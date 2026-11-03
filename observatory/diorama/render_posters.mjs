// Pre-render one poster frame per embedded snapshot and file it under the snapshot's canonical
// hash, so the page shows a frame only for the exact data it was rendered from (E-013).
// Needs Node and Playwright (Chromium). Run after `python3 -m seventh_seat.observatory.snapshot`,
// and again after any change to the scene's look (the hash covers the data, not the drawing).
//
//   node render_posters.mjs [--three-dir DIR]     (default: ./node_modules/three when present)
import { chromium } from "playwright";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import fs from "node:fs";

const here = path.dirname(fileURLToPath(import.meta.url));
const file = path.join(here, "index.html");
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const html0 = fs.readFileSync(file, "utf8");
const pinned = html0.match(/https:\/\/cdn\.jsdelivr\.net\/npm\/three@([\d.]+)\//)?.[1];
const localThree = path.join(here, "node_modules", "three");
const threeDir = arg("--three-dir") ?? (fs.existsSync(localThree) ? localThree : null);
if (threeDir) {
  const v = JSON.parse(fs.readFileSync(path.join(threeDir, "package.json"), "utf8")).version;
  if (v !== pinned) throw new Error(`local three.js is ${v}, the page pins ${pinned}; run npm ci`);
}

const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
const page = await (await browser.newContext({ viewport: { width: 1600, height: 760 }, deviceScaleFactor: 1, reducedMotion: "reduce" })).newPage();
if (threeDir) await page.route(`https://cdn.jsdelivr.net/npm/three@${pinned}/**`, (r) => {
  const rel = new URL(r.request().url()).pathname.replace(`/npm/three@${pinned}/`, "");
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
  if (!frame.startsWith("data:image/webp;base64,")) throw new Error("browser did not produce a WebP frame");
  posters[hash] = frame;
  console.log(`${label}: ${hash.slice(0, 12)}… ${(frame.length / 1024).toFixed(0)} KB`);
}
await browser.close();

const html = fs.readFileSync(file, "utf8");
const block = /(<script id="posters" type="application\/json">)([\s\S]*?)(<\/script>)/;
if (!block.test(html)) throw new Error("no posters block in index.html");
fs.writeFileSync(file, html.replace(block, (_, a, __, c) => `${a}\n${JSON.stringify(posters)}\n${c}`));
console.log(`embedded ${Object.keys(posters).length} poster frame(s) in index.html`);
