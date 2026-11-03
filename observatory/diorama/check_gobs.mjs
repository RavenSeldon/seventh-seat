// Gate G-OBS, browser half (E-011, E-013). Needs Node and Playwright (Chromium).
//
//   node observatory/diorama/check_gobs.mjs [--three-dir node_modules/three] [--shots out/]
//
// Checks: the scripted label is visible; the page renders without WebGL; the HUD, the panel, the
// flat plan and the 3D meshes all agree with the snapshot (widths are measured from the drawn SVG
// and mesh geometry, not read back from the data); decoration is off in the calibrated plan; an
// idle view renders nothing; the reveal is labelled as a staging, not a replay; pre-rendered frames
// are shown only for the snapshot they were made from; invalid snapshots are refused.
// --three-dir serves three.js from a local copy instead of the CDN (offline runs).
import { chromium } from "playwright";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import fs from "node:fs";

const here = path.dirname(fileURLToPath(import.meta.url));
const pageUrl = pathToFileURL(path.join(here, "index.html")).href;
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const threeDir = arg("--three-dir");
const shots = arg("--shots");
if (shots) fs.mkdirSync(shots, { recursive: true });

let failures = 0;
const check = (ok, msg) => { console.log((ok ? "  ok   " : "  FAIL ") + msg); if (!ok) failures++; };
const close = (a, b, tol = 1e-3) => Math.abs(a - b) <= tol;
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

async function open(browser, { webgl = true, viewport = { width: 1440, height: 900 } } = {}) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  page.on("pageerror", (e) => { console.log("  page error: " + e.message); failures++; });
  await page.route("https://fonts.googleapis.com/**", (r) => r.abort());
  await page.route("https://fonts.gstatic.com/**", (r) => r.abort());
  if (threeDir) await page.route("https://cdn.jsdelivr.net/npm/three@0.160.0/**", (r) => {
    const rel = new URL(r.request().url()).pathname.replace("/npm/three@0.160.0/", "");
    r.fulfill({ path: path.resolve(threeDir, rel), contentType: "text/javascript" });
  });
  if (!webgl) await page.addInitScript(() => {
    const orig = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (t, ...a) { return /webgl/.test(t) ? null : orig.call(this, t, ...a); };
  });
  await page.goto(pageUrl);
  await page.waitForFunction(() => window.__diorama);
  return { ctx, page };
}

async function checkSnapshot(page, i, withScene) {
  await page.evaluate((i) => window.__diorama.show(i), i);
  const { s, panel, hud, plan, scene } = await page.evaluate(() => {
    const d = window.__diorama;
    return { s: d.current(), panel: d.panel(), hud: d.hud(), plan: d.plan(), scene: d.scene() };
  });
  const total = Object.values(s.withdrawals_by_actor).reduce((a, b) => a + b, 0);
  const short = Math.max(0, s.minimum_required_flow - s.downstream_flow);
  console.log(`snapshot ${i}: ${s.label} (${s.data_status})`);
  check(panel.total_inflow === s.total_inflow && panel.downstream_flow === s.downstream_flow &&
        panel.minimum_required_flow === s.minimum_required_flow && panel.total_withdrawal === total &&
        panel.shortfall === short, "panel figures equal the snapshot");
  check(s.actors.every((a) => panel["w:" + a] === s.withdrawals_by_actor[a]), "panel bars equal withdrawals_by_actor");
  check(hud.downstream_flow === s.downstream_flow && hud.minimum_required_flow === s.minimum_required_flow &&
        (short > 0 ? hud.shortfall === short : !("shortfall" in hud)), "HUD figures equal the snapshot");
  const pm = (m, a) => plan.find((p) => p.mark === m && (a === undefined || p.actor === a));
  check(close(pm("inflow").strokeValue, s.total_inflow), "plan: inflow width = total_inflow");
  check(close(pm("outflow").strokeValue, s.downstream_flow), "plan: outlet width = downstream_flow");
  check(close(pm("minimum").strokeValue, s.minimum_required_flow), "plan: gilt band width = minimum_required_flow");
  check(s.actors.every((a) => s.withdrawals_by_actor[a] === 0 ? !pm("offtake", a) : close(pm("offtake", a).strokeValue, s.withdrawals_by_actor[a])),
        "plan: each district channel width = its withdrawal");
  check(!plan.some((p) => p.mark === "ring"), "plan: no sequential river course (E-013)");
  check(close(pm("seventh-arc").fraction, Math.min(1, s.downstream_flow / s.minimum_required_flow)), "plan: seventh-seat arc = share of minimum delivered");
  if (withScene) {
    const sm = (k, a) => scene.find((m) => m.kind === k && (a === undefined || m.actor === a));
    check(close(sm("inflow").measuredValue, s.total_inflow), "3D: inflow mesh width = total_inflow");
    check(close(sm("outflow").measuredValue, s.downstream_flow), "3D: outlet mesh width = downstream_flow");
    check(close(sm("minimum").measuredValue, s.minimum_required_flow), "3D: gilt band mesh width = minimum_required_flow");
    check(s.actors.every((a) => s.withdrawals_by_actor[a] === 0 ? !sm("offtake", a) : close(sm("offtake", a).measuredValue, s.withdrawals_by_actor[a])),
          "3D: each district channel mesh width = its withdrawal");
    check(scene.every((m) => !m.decorative), "3D: decorative glow is not among the measured marks");
  }
}

const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });

console.log("First view, before WebGL");
{
  const { ctx, page } = await open(browser);
  check(/scripted fixture/i.test(await page.locator("#status").innerText()) && await page.locator("#status").isVisible(), "scripted-fixture label visible");
  check(await page.locator("canvas").count() === 0, "no WebGL context before the viewer asks for it");
  for (let i = 0; i < 2; i++) {
    await page.evaluate((i) => window.__diorama.show(i), i);
    await wait(150);
    const { has, src, expected } = await page.evaluate(async () => {
      const d = window.__diorama, h = await d.snapHash(d.current());
      return { has: h in d.posters, src: document.getElementById("frame").getAttribute("src"), expected: d.posters[h] ?? null };
    });
    if (has) check(src === expected && await page.locator("#frame").isVisible(), `snapshot ${i}: its own pre-rendered frame is shown`);
    else check(await page.locator("#theatre-plan").isVisible(), `snapshot ${i}: no frame filed for it, flat plan shown instead`);
  }
  const refused = await page.evaluate(() => {
    const d = window.__diorama, base = structuredClone(d.snapshots[1]), out = {};
    const tryIt = (s) => { try { d.validate(s); return "accepted"; } catch (e) { return e.message; } };
    const a = structuredClone(base); delete a.withdrawals_by_actor.D3; out.missing = tryIt(a);
    const b = structuredClone(base); b.downstream_flow = 30; out.unbalanced = tryIt(b);
    const c = structuredClone(base); c.data_status = "illustrative"; out.status = tryIt(c);
    const e = structuredClone(base); e.data_status = "experimental"; out.experimental = tryIt(e);
    return out;
  });
  check(/missing is not zero/.test(refused.missing), "missing withdrawal is an error, never a zero");
  check(/does not balance/.test(refused.unbalanced), "unbalanced accounting is refused");
  check(/data_status/.test(refused.status), "unknown data status is refused");
  check(/export manifest/.test(refused.experimental), "experimental data without a verified manifest is refused");
  for (let i = 0; i < 2; i++) await checkSnapshot(page, i, false);
  if (shots) { await page.evaluate(() => window.__diorama.show(1)); await wait(150); await page.screenshot({ path: path.join(shots, "first-view.png") }); }

  console.log("Entering the diorama (WebGL)");
  await page.click("#enter");
  await page.waitForFunction(() => window.__diorama.scene() !== null, null, { timeout: 30000 });
  check(await page.locator("canvas").count() === 1, "WebGL canvas created on request");
  for (const i of [0, 1]) await checkSnapshot(page, i, true);
  const d3 = () => page.evaluate(() => { const s = window.__diorama.scene3d(); return { mode: s.mode(), halo: s.haloVisible(), frames: s.frames() }; });
  check((await d3()).halo === true, "cinematic view shows the decorative glow");
  check(/not a reading/.test(await page.locator("#view-chip").innerText()), "cinematic view says its widths are not a reading");
  await wait(500);
  if (shots) await page.locator("#theatre").screenshot({ path: path.join(shots, "cinematic.png") });
  await page.click("#view-plan");
  await wait(1000);   // let the last camera damping settle
  // settle: the view must reach a state where consecutive samples render no frames
  let a = await d3(), b = a;
  for (let k = 0; k < 8; k++) { await wait(600); b = await d3(); if (b.frames === a.frames) break; a = b; }
  check(a.mode === "plan" && a.halo === false, "calibrated plan switches the glow off");
  check(b.frames === a.frames, `calibrated plan settles to idle: no frames rendered while nothing changes (${a.frames} → ${b.frames})`);
  if (shots) await page.locator("#theatre").screenshot({ path: path.join(shots, "plan-3d.png") });

  console.log("Guided reveal");
  await page.click("#view-cinematic");
  await page.click("#reveal-start");
  check(/not a replay/i.test(await page.locator("#reveal-card").innerText()), "reveal is labelled a staging of a final state, not a replay");
  await page.click("#reveal-next");
  const s = await page.evaluate(() => window.__diorama.current());
  const t1 = await page.locator("#reveal-text").innerText();
  check(s.actors.every((x) => t1.includes(`${x} ${s.withdrawals_by_actor[x]}`)) && /same pool at once/.test(t1), "step 2 states every withdrawal and that all draw at once");
  await page.click("#reveal-next");
  const camDist = () => page.evaluate(() => { const s = window.__diorama.scene3d(), a = s.camera(), w = s.pose("seventh").pos; return Math.hypot(a[0] - w[0], a[1] - w[1], a[2] - w[2]); });
  for (let k = 0; k < 40 && (await camDist()) >= 0.05; k++) await wait(250);   // up to 10 s on software rendering
  check((await page.locator("#reveal-text").innerText()).includes(`${s.downstream_flow} arrive`), "step 3 states the recorded downstream flow");
  const cam = await page.evaluate(() => { const s = window.__diorama.scene3d(); return { at: s.camera(), want: s.pose("seventh").pos }; });
  check(Math.hypot(...cam.at.map((v, k) => v - cam.want[k])) < 0.05, `step 3 camera arrives at the seventh seat, even after quick steps (at ${cam.at.map((v) => v.toFixed(2))})`);
  if (shots) await page.locator("#theatre").screenshot({ path: path.join(shots, "reveal-seventh.png") });
  await page.click("#reveal-exit");
  check(await page.locator("#reveal-card").isHidden(), "reveal can be ended at any step");
  await ctx.close();
}

console.log("Phone width");
{
  const { ctx, page } = await open(browser, { viewport: { width: 390, height: 844 } });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  check(!overflow, "no horizontal page scroll at 390 px");
  if (shots) await page.screenshot({ path: path.join(shots, "phone.png"), fullPage: false });
  await ctx.close();
}

console.log("WebGL unavailable");
{
  const { ctx, page } = await open(browser, { webgl: false });
  await page.click("#enter");
  await page.waitForSelector("#stage-error:not([hidden])");
  check(/could not start/.test(await page.locator("#stage-error").innerText()), "fallback explains what happened");
  check(await page.locator("#plan").isVisible(), "the calibrated plan stays available");
  check((await page.evaluate(() => window.__diorama.panel())).downstream_flow === 16, "the panel still shows the snapshot");
  await ctx.close();
}

await browser.close();
console.log(failures ? `G-OBS: ${failures} check(s) failed` : "G-OBS: all checks passed");
process.exit(failures ? 1 : 0);
