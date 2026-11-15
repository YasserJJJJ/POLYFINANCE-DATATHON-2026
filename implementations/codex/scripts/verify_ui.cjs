/* Isolated browser test; never attaches to the user's browser or profile. */
const { chromium } = require("../runtime/browser-check/node_modules/playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

(async () => {
  const root = path.resolve(__dirname, "..");
  const output = path.join(root, "artifacts");
  fs.mkdirSync(path.join(output, "screens"), { recursive: true });
  const record = process.argv.includes("--record");
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    ...(record ? { recordVideo: { dir: path.join(output, "video"), size: { width: 1440, height: 1000 } } } : {}),
  });
  const page = await context.newPage();
  const errors = [];
  const responses = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("response", async (response) => {
    if (response.url().endsWith("/api/analyze")) responses.push(await response.json());
  });
  const pause = async (ms = 3500) => { if (record) await page.waitForTimeout(ms); };
  const ready = async () => {
    await page.locator("#result-card[aria-busy=false]").waitFor();
    await page.locator("#chart-container svg").waitFor();
  };
  const action = async (perform) => {
    const received = page.waitForResponse((r) => r.url().endsWith("/api/analyze") && r.status() === 200);
    await perform();
    const response = await received;
    const data = await response.json();
    await ready();
    return data;
  };
  await page.goto("http://127.0.0.1:8766");
  await ready();
  assert.match(await page.locator("#analysis-status").innerText(), /Comparaison calculée/);
  assert.equal(await page.locator("#focus-weight").inputValue(), "5");
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  await page.screenshot({ path: path.join(output, "screens/desktop.png"), fullPage: true });
  await page.screenshot({ path: path.join(output, "screens/desktop-viewport.png") });
  await pause(5000);
  await page.locator("#result-card").scrollIntoViewIfNeeded();
  await pause(5000);
  await page.locator("#focus-weight").fill("25");
  assert.equal(await page.locator("#dirty-note").isVisible(), true);
  const same = await action(() => page.locator("#recalculate-btn").click());
  assert.deepEqual(same.comparison.baseline.series, same.comparison.alternative.series);
  await pause();
  await page.locator("#undo-btn").click();
  assert.equal(await page.locator("#focus-weight").inputValue(), "5");
  await pause();
  await page.locator('[data-chart="drawdown"]').click();
  await page.screenshot({ path: path.join(output, "screens/drawdown.png") });
  await pause();
  const amira = await action(() => page.locator('[data-persona="amira"]').click());
  assert.equal(amira.settings.focus_ticker, "NVDA");
  assert.equal(await page.locator("#horizon").inputValue(), "15");
  await pause();
  const mateo = await action(() => page.locator('[data-persona="mateo"]').click());
  assert.equal(mateo.settings.focus_ticker, "XOM");
  assert.equal(mateo.settings.focus_weight, 0);
  assert(mateo.comparison.alternative.metrics.max_drawdown_pct < mateo.comparison.baseline.metrics.max_drawdown_pct);
  await pause(5000);
  const agent = await action(() => page.locator("#analyze-btn").click());
  assert.equal(agent.mode, "bedrock");
  assert.equal(agent.agent.status, "success");
  assert(agent.agent.calls.every((call) => call.request_id));
  await page.locator("#insight-card").scrollIntoViewIfNeeded();
  await pause(7000);
  await page.screenshot({ path: path.join(output, "screens/agent-mateo.png"), fullPage: true });
  await page.locator('.nav-item[data-view="preuves"]').click();
  await page.locator("#view-preuves").waitFor({ state: "visible" });
  await page.waitForTimeout(450); // Let the view transition settle before its visual record.
  await page.screenshot({ path: path.join(output, "screens/evidence.png"), fullPage: true });
  assert.match(await page.locator("#trace-list").innerText(), /Requête/);
  await pause(6000);
  const downloadEvent = page.waitForEvent("download");
  await page.locator("#export-btn").click();
  const download = await downloadEvent;
  const report = path.join(output, "ui-export.json");
  await download.saveAs(report);
  const saved = JSON.parse(fs.readFileSync(report, "utf8"));
  assert.equal(saved.id, agent.id);
  assert.deepEqual(saved.comparison, agent.comparison);
  const methodResponse = await page.request.get("http://127.0.0.1:8766/api/source/method");
  assert.equal(methodResponse.status(), 200);
  await page.locator('.nav-item[data-view="methode"]').click();
  await page.locator("#view-methode").waitFor({ state: "visible" });
  await pause(5000);
  await page.locator('.nav-item[data-view="atelier"]').click();
  await pause();
  const video = page.video();
  await context.close();
  if (video) await video.saveAs(path.join(output, "AlphaForge_demo_locale.webm"));

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, deviceScaleFactor: 1 });
  await mobile.goto("http://127.0.0.1:8766");
  await mobile.locator("#result-card[aria-busy=false]").waitFor();
  await mobile.locator("#chart-container svg").waitFor();
  assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  await mobile.screenshot({ path: path.join(output, "screens/mobile.png"), fullPage: true });
  await mobile.screenshot({ path: path.join(output, "screens/mobile-viewport.png") });
  await mobile.locator('.nav-item[data-view="preuves"]').click();
  assert.equal(await mobile.locator("#view-preuves").isVisible(), true);
  await mobile.waitForTimeout(450);
  await mobile.screenshot({ path: path.join(output, "screens/mobile-evidence.png") });
  assert.deepEqual(errors, []);
  const result = { checked_at: new Date().toISOString(), desktop: "1440×1000", mobile: "390×844",
    checks: ["rendering", "no horizontal overflow", "same-weight identity", "undo", "drawdown view",
      "persona parameters", "real Bedrock through UI", "evidence", "exact exported report", "mobile navigation"],
    javascript_errors: errors, agent_report_id: agent.id, aws_requests: agent.agent.calls.map((call) => call.request_id) };
  fs.writeFileSync(path.join(output, "ui-verification.json"), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result));
  await browser.close();
})().catch((error) => { console.error(error); process.exit(1); });
