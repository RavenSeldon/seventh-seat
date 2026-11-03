// Gate G-OBS, browser half (E-011, E-013). Needs Node 18+ and Playwright with Chromium.
//
//   npm ci && npx playwright install chromium        # once, in observatory/diorama/
//   node check_gobs.mjs [--page FILE] [--three-dir DIR] [--offline] [--shots DIR]
//
// What it checks, and why each matters:
//   Data honesty  HUD, panel, flat plan and 3D meshes agree with the snapshot. Widths are measured
//                 from the drawn SVG strokes and mesh vertices, never read back from the data. Invalid
//                 snapshots are refused. A pre-rendered frame appears only over its own snapshot.
//   Labelling     The scripted-fixture label is visible; the cinematic view says it is not a reading;
//                 the reveal says it is not a replay; full screen keeps the disclaimer.
//   Calibration   Decoration (glow, moving light, ripples, 道, ∞) is off in the calibrated plan.
//   Legibility    No label overlaps another or leaves the theatre (desktop, plan, phone, reveal).
//   Cost          An idle view stops rendering (plan, paused, reduced motion, offscreen). A settle
//                 helper waits for the loop to stop, so these checks do not depend on machine speed.
//                 The page makes no third-party requests beyond the pinned three.js (none at all for
//                 a release build).
//   Access        No WebGL before it is asked for; a working fallback without WebGL; 44 px touch
//                 targets and no sideways scroll on a phone; reduced-motion settings respected.
//
// --page       page to check (default: index.html beside this script; use the release build's page
//              to check what will be deployed)
// --three-dir  local three.js for the source page's CDN imports (default: ./node_modules/three when
//              present). Its version must equal the version pinned in the page's importmap.
// --offline    block every request that does not come from the page's own directory
// A RELEASE.json beside the page (written by scripts/build_release.py) supplies the release's
// Content-Security-Policy; the page is then served with it, and any violation fails the run.
// --shots      write screenshots there
import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import http from "node:http";
import path from "node:path";
import fs from "node:fs";

const here = path.dirname(fileURLToPath(import.meta.url));
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const flag = (k) => process.argv.includes(k);
const pageFile = path.resolve(arg("--page") ?? path.join(here, "index.html"));
const root = path.dirname(pageFile);
const offline = flag("--offline");
const shots = arg("--shots");
if (shots) fs.mkdirSync(shots, { recursive: true });

const html = fs.readFileSync(pageFile, "utf8");
const pinned = html.match(/https:\/\/cdn\.jsdelivr\.net\/npm\/three@([\d.]+)\//)?.[1] ?? null;   // null: vendored build
const localThree = path.join(here, "node_modules", "three");
const threeDir = arg("--three-dir") ?? (pinned && fs.existsSync(localThree) ? localThree : null);
if (pinned && threeDir) {
  const v = JSON.parse(fs.readFileSync(path.join(threeDir, "package.json"), "utf8")).version;
  if (v !== pinned) { console.log(`  FAIL local three.js is ${v}, the page pins ${pinned}; run npm ci`); process.exit(1); }
}
if (pinned && offline && !threeDir) { console.log("  FAIL --offline on the source page needs a local three.js (npm ci)"); process.exit(1); }
const releaseFile = path.join(root, "RELEASE.json");
const csp = fs.existsSync(releaseFile) ? JSON.parse(fs.readFileSync(releaseFile, "utf8")).content_security_policy ?? null : null;
const allowedHosts = pinned ? new Set(["cdn.jsdelivr.net"]) : new Set();
console.log(`page: ${path.relative(process.cwd(), pageFile) || pageFile}  three.js: ${pinned ? `CDN ${pinned}${threeDir ? " (served from local copy)" : ""}` : "vendored"}${offline ? "  offline" : ""}${csp ? "  with the release CSP" : ""}`);

/* Serve the page's directory over HTTP, as production does (relative module paths, real MIME types). */
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json",
  ".webp": "image/webp", ".svg": "image/svg+xml", ".css": "text/css", ".txt": "text/plain; charset=utf-8" };
const server = http.createServer((req, res) => {
  const rel = decodeURIComponent(new URL(req.url, "http://local").pathname);
  const f = path.normalize(path.join(root, rel.endsWith("/") ? rel + "index.html" : rel));
  if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end(); return; }
  const headers = { "content-type": TYPES[path.extname(f)] ?? "application/octet-stream", "x-content-type-options": "nosniff" };
  if (csp && f.endsWith(".html")) headers["content-security-policy"] = csp;
  res.writeHead(200, headers);
  fs.createReadStream(f).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const origin = `http://127.0.0.1:${server.address().port}`;
const pageUrl = `${origin}/${path.basename(pageFile) === "index.html" ? "" : path.basename(pageFile)}`;

let failures = 0, passed = 0;
const check = (ok, msg) => { console.log((ok ? "  ok   " : "  FAIL ") + msg); if (ok) passed++; else failures++; };
const close = (a, b, tol = 1e-3) => Math.abs(a - b) <= tol;
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const externalHosts = new Set();

async function open(browser, { webgl = true, viewport = { width: 1440, height: 900 }, reducedMotion = "no-preference" } = {}) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion });
  const page = await ctx.newPage();
  page.on("pageerror", (e) => { console.log("  FAIL page error: " + e.message); failures++; });
  page.on("console", (m) => { if (/Content Security Policy/i.test(m.text())) { console.log("  FAIL CSP: " + m.text().slice(0, 200)); failures++; } });
  await page.route("**/*", (r) => {
    const u = new URL(r.request().url());
    if (u.origin === origin) return r.continue();
    externalHosts.add(u.host);
    if (pinned && threeDir && u.href.startsWith(`https://cdn.jsdelivr.net/npm/three@${pinned}/`))
      return r.fulfill({ path: path.resolve(threeDir, u.pathname.replace(`/npm/three@${pinned}/`, "")), contentType: "text/javascript" });
    return offline ? r.abort() : r.continue();
  });
  if (!webgl) await page.addInitScript(() => {
    const orig = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (t, ...a) { return /webgl/.test(t) ? null : orig.call(this, t, ...a); };
  });
  await page.goto(pageUrl);
  await page.waitForFunction(() => window.__diorama);
  return { ctx, page };
}

async function enter(page) {
  await page.click("#enter");
  await page.waitForFunction(() => window.__diorama.scene() !== null, null, { timeout: 30000 });
}

/* The live scene's render state. */
const state = (page) => page.evaluate(() => {
  const s = window.__diorama.scene3d();
  return { mode: s.mode(), halo: s.haloVisible(), decor: s.decorVisible(), frames: s.frames(), looping: s.looping(), water: s.waterTime() };
});

/* Wait until the render loop has stopped and stays stopped: no frames for half a second. Returns
   idle: false if that never happens before the deadline (a view that keeps rendering). */
async function settle(page, deadline = 15000) {
  const end = Date.now() + deadline;
  while (Date.now() < end) {
    const a = await state(page);
    if (a.looping) { await wait(200); continue; }
    await wait(500);
    const b = await state(page);
    if (!b.looping && b.frames === a.frames) return { idle: true, ...b };
  }
  return { idle: false, ...(await state(page)) };
}

/* Wait for the camera to reach a named pose (the reveal flies there; software rendering is slow). */
const camDist = (page, pose) => page.evaluate((pose) => {
  const s = window.__diorama.scene3d(), a = s.camera(), w = s.pose(pose).pos;
  return Math.hypot(a[0] - w[0], a[1] - w[1], a[2] - w[2]);
}, pose);
async function arrive(page, pose, deadline = 12000) {
  const end = Date.now() + deadline;
  let d = await camDist(page, pose);
  while (d >= 0.05 && Date.now() < end) { await wait(200); d = await camDist(page, pose); }
  return d;
}

/* Labels: every visible label inside the theatre and none on top of another. */
async function labelsClear(page, where, { only } = {}) {
  const r = await page.evaluate(() => window.__diorama.scene3d().labels());
  if (only) {
    const mine = r.overlaps.filter((o) => o.includes(only));
    check(!r.hidden && !r.outside.includes(only) && mine.length === 0,
      `${where}: the "${only}" label is inside the theatre and covers no other label${mine.length ? ` (${mine.join("; ")})` : ""}`);
  } else {
    check(!r.hidden && r.count === 7 && r.overlaps.length === 0 && r.outside.length === 0,
      `${where}: all ${r.count} labels are visible, inside the theatre and clear of each other` +
      (r.hidden ? " (hidden)" : "") + (r.overlaps.length ? ` (overlap: ${r.overlaps.join("; ")})` : "") + (r.outside.length ? ` (outside: ${r.outside.join(", ")})` : ""));
  }
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
    check(scene.every((m) => !m.decorative), "3D: decoration is not among the measured marks");
  }
}

const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
const started = Date.now();

console.log("First view, before WebGL");
{
  const { ctx, page } = await open(browser);
  check(await page.evaluate(() => document.characterSet === "UTF-8" && document.compatMode === "CSS1Compat" && document.documentElement.lang === "en"), "UTF-8, standards mode and page language are explicit");
  check((await page.locator('meta[name="viewport"]').getAttribute("content")).includes("width=device-width"), "mobile viewport uses the device width");
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
    const f = structuredClone(base); f.data_status = "experimental"; f.provenance = { manifest_sha256: "0".repeat(64) }; out.withManifest = tryIt(f);
    return out;
  });
  check(/missing is not zero/.test(refused.missing), "missing withdrawal is an error, never a zero");
  check(/does not balance/.test(refused.unbalanced), "unbalanced accounting is refused");
  check(/data_status/.test(refused.status), "unknown data status is refused");
  check(/export-manifest reference/.test(refused.experimental), "experimental data without an export-manifest reference is refused");
  check(refused.withManifest === "accepted", "experimental data with a manifest reference passes the structural check (the exporter verifies it)");
  for (let i = 0; i < 2; i++) await checkSnapshot(page, i, false);
  const zero = await page.evaluate(() => {
    const d = window.__diorama, s = structuredClone(d.current());
    s.total_inflow = s.downstream_flow = 0;
    for (const actor of s.actors) s.withdrawals_by_actor[actor] = 0;
    d.snapshots.push(s); d.show(d.snapshots.length - 1);
    const result = { finite: [...document.querySelectorAll(".fill")].every(e => e.style.width === "0%"),
      scale: document.querySelector("#bars").getAttribute("aria-label"), source: JSON.parse(document.querySelector("#snapshot-source").textContent).downstream_flow };
    d.snapshots.pop(); d.show(1); return result;
  });
  check(zero.finite && zero.scale.includes("0 to 30") && zero.source === 0, "valid zero-inflow snapshot uses a finite bar scale and inspectable source");
  if (shots) { await page.evaluate(() => window.__diorama.show(1)); await wait(150); await page.screenshot({ path: path.join(shots, "first-view.png") }); }

  console.log("Entering the diorama (WebGL)");
  await enter(page);
  check(await page.locator("canvas").count() === 1, "WebGL canvas created on request");
  for (const i of [0, 1]) await checkSnapshot(page, i, true);

  console.log("Cinematic view");
  let st = await state(page);
  check(st.halo && st.decor, "cinematic view shows its decoration (glow, moving light, ripples, 道, ∞)");
  check(/not a reading/.test(await page.locator("#view-chip").innerText()), "cinematic view says its widths are not a reading");
  await wait(700);
  const moving = await state(page);
  check(moving.looping && moving.water > st.water && moving.frames > st.frames, "with motion on, the water moves (this is what the idle checks below must stop)");
  await labelsClear(page, "desktop cinematic");
  if (shots) await page.locator("#theatre").screenshot({ path: path.join(shots, "cinematic.png") });

  console.log("Calibrated plan");
  await page.click("#view-plan");
  st = await settle(page);
  check(st.mode === "plan" && !st.halo && !st.decor, "calibrated plan switches all decoration off");
  check(st.idle, `calibrated plan settles to idle: no frames rendered while nothing changes (frames ${st.frames})`);
  const w0 = st.water; await wait(500);
  check((await state(page)).water === w0, "calibrated plan: the water light stands still");
  await labelsClear(page, "calibrated plan");
  if (shots) await page.locator("#theatre").screenshot({ path: path.join(shots, "plan-3d.png") });

  console.log("Guided reveal");
  await page.click("#view-cinematic");
  await page.click("#reveal-start");
  check(/not a replay/i.test(await page.locator("#reveal-card").innerText()), "reveal is labelled a staging of a final state, not a replay");
  await page.click("#reveal-next");
  const s = await page.evaluate(() => window.__diorama.current());
  const t1 = await page.locator("#reveal-text").innerText();
  check(s.actors.every((x) => t1.includes(`${x} ${s.withdrawals_by_actor[x]}`)) && /same pool at once/.test(t1), "step 2 states every withdrawal and that all draw at once");
  await page.click("#reveal-next");   // clicked before step 2's camera move ends
  check((await page.locator("#reveal-text").innerText()).includes(`${s.downstream_flow} arrive`), "step 3 states the recorded downstream flow");
  const d = await arrive(page, "seventh");
  check(d < 0.05, `step 3 camera arrives at the seventh seat, even after quick steps (${d.toFixed(3)} away)`);
  await labelsClear(page, "reveal at the seventh seat", { only: "Downstream users" });
  if (shots) await page.locator("#theatre").screenshot({ path: path.join(shots, "reveal-seventh.png") });
  await page.click("#reveal-exit");
  check(await page.locator("#reveal-card").isHidden(), "reveal can be ended at any step");

  console.log("Pause, reset, fixture change");
  await page.click("#motion-toggle");
  await page.click("#reset-view");
  st = await settle(page);
  check(st.idle, `paused cinematic scene settles to idle (frames ${st.frames})`);
  const w1 = st.water; await wait(500);
  check((await state(page)).water === w1, "paused: the water light stands still");
  check(await page.locator("#motion-toggle").getAttribute("aria-pressed") === "true", "motion toggle exposes its paused state");
  check(await camDist(page, "hero") < 0.05, "Reset view restores the overview camera");
  await page.click("#reveal-start");
  await page.click("#reveal-next"); await page.click("#reveal-next");
  await page.click("#fixture-0");
  check(await page.locator("#reveal-card").isHidden() && (await page.locator("#hud-flow").innerText()).includes("30"), "changing fixture ends the old narration and updates the reading");
  await page.click("#reveal-start");
  await page.click("#reveal-next"); await page.click("#reveal-next");
  check((await page.locator("#reveal-text").innerText()).includes("30 arrive"), "a new reveal narrates the newly selected fixture");
  await page.click("#reset-view");
  check(await page.locator("#reveal-card").isHidden(), "Reset view exits a reveal");
  await page.click("#motion-toggle");
  if (await page.locator("#fullscreen").isVisible()) {
    await page.click("#fullscreen");
    await page.waitForFunction(() => document.fullscreenElement !== null);
    check(await page.locator("#fullscreen-status").isVisible() && /not an experimental result/.test(await page.locator("#fullscreen-status").innerText()), "full screen retains the fixture disclaimer");
    await page.click("#read-instrument");
    await page.waitForFunction(() => !document.fullscreenElement);
    check(await page.evaluate(() => document.activeElement.id === "instrument-title"), "Read the numbers exits full screen and moves keyboard focus to the instrument");
  }

  console.log("Offscreen");
  await page.locator("#source-title").scrollIntoViewIfNeeded();
  st = await settle(page);
  check(st.idle, `offscreen theatre stops rendering, even with motion on (frames ${st.frames})`);
  check(externalHosts.size === 0 || [...externalHosts].every((h) => allowedHosts.has(h)),
    pinned ? `requests leave this site only for the pinned three.js (${[...externalHosts].join(", ") || "none"})`
           : `no third-party requests: everything is served from this site${externalHosts.size ? ` (asked: ${[...externalHosts].join(", ")})` : ""}`);
  await ctx.close();
}

console.log("Phone width");
{
  const { ctx, page } = await open(browser, { viewport: { width: 390, height: 844 } });
  check(!(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)), "no horizontal page scroll at 390 px");
  if (shots) await page.screenshot({ path: path.join(shots, "phone.png"), fullPage: false });
  await enter(page);
  const fits = await page.evaluate(() => {
    const canvas = document.querySelector("canvas").getBoundingClientRect();
    const top = document.querySelector(".hud-top").getBoundingClientRect();
    const bottom = document.querySelector(".hud-bottom").getBoundingClientRect();
    return canvas.top >= top.bottom && canvas.bottom <= bottom.top && canvas.width <= innerWidth;
  });
  check(fits, "phone canvas has its own space between title and controls");
  check(await page.evaluate(() => [...document.querySelectorAll('.stage-tools button:not([hidden])')].every(e => e.getBoundingClientRect().height >= 44)), "phone controls have at least 44px touch targets");
  await wait(300);
  await labelsClear(page, "phone");
  if (shots) await page.locator("#theatre").screenshot({ path: path.join(shots, "phone-live.png") });
  await page.click("#reveal-start"); await page.click("#reveal-next"); await page.click("#reveal-next");
  check(await page.locator("#reveal-exit").isVisible(), "guided reveal remains operable on a phone");
  await arrive(page, "seventh");
  await labelsClear(page, "phone reveal at the seventh seat", { only: "Downstream users" });
  if (shots) await page.locator("#theatre").screenshot({ path: path.join(shots, "phone-reveal.png") });
  await ctx.close();
}

console.log("Reduced motion");
{
  const { ctx, page } = await open(browser, { reducedMotion: "reduce" });
  await enter(page);
  check(await page.locator("#motion-toggle").isDisabled() && await page.locator("#motion-toggle").getAttribute("aria-pressed") === "true", "device reduced-motion preference is respected");
  await page.click("#reveal-start"); await page.click("#reveal-next"); await page.click("#reveal-next");
  check(await camDist(page, "seventh") < 0.05, "reduced-motion camera cuts directly to the seventh seat");
  const st = await settle(page);
  check(st.idle, `reduced-motion reveal settles without decorative animation (frames ${st.frames})`);
  check(st.water === 0, "reduced motion: the water light never moves");
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
server.close();
const secs = ((Date.now() - started) / 1000).toFixed(0);
console.log(failures ? `G-OBS: ${failures} check(s) failed, ${passed} passed (${secs} s)` : `G-OBS: all ${passed} checks passed (${secs} s)`);
process.exit(failures ? 1 : 0);
