// Pre-render one poster frame per embedded snapshot and file it under the snapshot's canonical
// hash, so the page shows a frame only for the exact data it was rendered from (E-013).
// Needs Node and Playwright (Chromium). Run after `python3 -m seventh_seat.observatory.snapshot`.
//
//   node observatory/diorama/render_posters.mjs [--three-dir node_modules/three]
import { chromium } from "playwright";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import fs from "node:fs";

const here = path.dirname(fileURLToPath(import.meta.url));
const file = path.join(here, "index.html");
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const threeDir = arg("--three-dir");

const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
const page = await (await browser.newContext({ viewport: { width: 1600, height: 760 }, deviceScaleFactor: 1, reducedMotion: "reduce" })).newPage();
await page.route("https://fonts.googleapis.com/**", (r) => r.abort());
await page.route("https://fonts.gstatic.com/**", (r) => r.abort());
if (threeDir) await page.route("https://cdn.jsdelivr.net/npm/three@0.160.0/**", (r) => {
  const rel = new URL(r.request().url()).pathname.replace("/npm/three@0.160.0/", "");
  r.fulfill({ path: path.resolve(threeDir, rel), contentType: "text/javascript" });
});
await page.goto(pathToFileURL(file).href);
await page.waitForFunction(() => window.__diorama);
await page.evaluate(() => window.__diorama.enter());
await page.waitForFunction(() => window.__diorama.scene() !== null, null, { timeout: 30000 });

const posters = {};
const n = await page.evaluate(() => window.__diorama.snapshots.length);
for (let i = 0; i < n; i++) {
  const { hash, label, frame } = await page.evaluate(async (i) => {
    const d = window.__diorama;
    d.show(i);
    d.scene3d().setMode("cinematic");
    d.scene3d().hero();
    await new Promise((r) => setTimeout(r, 250));
    return { hash: await d.snapHash(d.snapshots[i]), label: d.snapshots[i].label, frame: d.scene3d().snapshotFrame(0.8) };
  }, i);
  posters[hash] = frame;
  console.log(`${label}: ${hash.slice(0, 12)}… ${(frame.length / 1024).toFixed(0)} KB`);
}
await browser.close();

const html = fs.readFileSync(file, "utf8");
const block = /(<script id="posters" type="application\/json">)([\s\S]*?)(<\/script>)/;
if (!block.test(html)) throw new Error("no posters block in index.html");
fs.writeFileSync(file, html.replace(block, (_, a, __, c) => `${a}\n${JSON.stringify(posters)}\n${c}`));
console.log(`embedded ${Object.keys(posters).length} poster frame(s) in index.html`);
