/* Capture the actual local app. The bottom strip is an editorial video label.
 * All live analysis requests use_ai=false. Recorded Bedrock data is labelled
 * before it is displayed and never sent to AWS during this capture.
 */
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const { performance } = require("node:perf_hooks");
const { chromium } = require("../runtime/browser-check/node_modules/playwright");

(async () => {
  const manifest = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const archive = JSON.parse(fs.readFileSync(manifest.archive, "utf8"));
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 810 },
    recordVideo: { dir: path.join(manifest.work, "capture"), size: { width: 1440, height: 810 } },
    acceptDownloads: true,
  });
  const captureStart = performance.now();
  const page = await context.newPage();
  const errors = [];
  const result = { scenes: [], javascript_errors: errors, new_aws_requests: 0, replayed_requests: 0 };
  page.on("pageerror", e => errors.push(e.message));
  let labelledReplay = false;
  let latest;
  page.on("response", async response => {
    if (response.url().endsWith("/api/analyze") && response.status() === 200) latest = await response.json();
  });
  await page.route("**/api/analyze", async route => {
    const body = route.request().postDataJSON();
    if (body.use_ai) {
      assert(labelledReplay, "Recorded analysis must be labelled before playback");
      assert.equal(body.persona, "mateo");
      result.replayed_requests++;
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(archive) });
    } else {
      await route.continue();
    }
  });
  await page.route(`**/api/report/${archive.id}`, async route => {
    assert(labelledReplay, "Recorded export must be explicitly labelled");
    await route.fulfill({
      status: 200, contentType: "application/json",
      headers: { "content-disposition": `attachment; filename="AlphaForge_${archive.id}.json"` },
      body: JSON.stringify(archive, null, 2),
    });
  });
  const wait = ms => page.waitForTimeout(Math.max(0, ms));
  const clock = () => (performance.now() - captureStart) / 1000;
  const ready = async () => {
    await page.locator("#result-card[aria-busy=false]").waitFor();
    await page.locator("#chart-container svg").waitFor();
    await wait(550);
  };
  const calc = async perform => {
    const response = page.waitForResponse(r => r.url().endsWith("/api/analyze") && r.status() === 200);
    await perform();
    const report = await (await response).json();
    await ready();
    latest = report;
    return report;
  };
  const scroll = async (selector, offset = 38) => {
    await page.locator(selector).evaluate((element, offset) => {
      window.scrollTo({ top: Math.max(0, element.getBoundingClientRect().top + scrollY - offset), behavior: "smooth" });
    }, offset);
    await wait(650);
  };
  const top = async () => { await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" })); await wait(650); };
  const view = async name => {
    await page.locator(`.nav-item[data-view="${name}"]`).click();
    await page.locator(`#view-${name}`).waitFor({ state: "visible" });
    await wait(550);
  };
  const persona = async name => {
    await view("atelier");
    await top();
    return calc(() => page.locator(`[data-persona="${name}"]`).click());
  };
  const label = async scene => {
    labelledReplay = scene.kind.startsWith("PREUVE BEDROCK");
    await page.evaluate(scene => {
      const bar = document.getElementById("demo-editorial-strip");
      bar.querySelector("[data-title]").textContent = scene.title;
      bar.querySelector("[data-kind]").textContent = scene.kind;
      bar.querySelector("[data-index]").textContent = String(scene.number).padStart(2, "0") + " / 13";
    }, scene);
  };
  await page.goto(manifest.url);
  await ready();
  assert.equal(latest.settings.focus_weight, 5);
  assert(Math.abs(latest.comparison.baseline.metrics.max_drawdown_pct + 23.4) < .1);
  assert(Math.abs(latest.comparison.alternative.metrics.max_drawdown_pct + 11.3) < .1);
  // A video-only strip, visually separated from the unmodified application.
  await page.evaluate(() => {
    const style = document.createElement("style");
    style.textContent = `
      body{padding-bottom:64px!important}
      #demo-editorial-strip{position:fixed;z-index:99999;bottom:0;left:0;right:0;height:54px;
        display:flex;align-items:center;justify-content:space-between;gap:20px;padding:0 24px;
        background:#132a24;color:#f2f5ea;border-top:2px solid #cee7a1;pointer-events:none;
        font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
      #demo-editorial-strip [data-title]{font-size:15px;font-weight:550;letter-spacing:.1px}
      #demo-editorial-strip [data-kind]{font-size:12px;color:#d8e7c5;letter-spacing:.1px}
      #demo-editorial-strip [data-index]{font-size:12px;color:#adc797;font-variant-numeric:tabular-nums;margin-right:15px}
    `;
    document.head.appendChild(style);
    const strip = document.createElement("div");
    strip.id = "demo-editorial-strip";
    strip.setAttribute("aria-hidden", "true");
    strip.innerHTML = '<div><span data-index></span><span data-title></span></div><span data-kind></span>';
    document.body.appendChild(strip);
  });

  const prepare = {
    intro: () => top(),
    contexte: () => scroll("#prompt", 150),
    robert: async () => {
      await page.locator('[data-chart="value"]').click();
      await scroll("#result-card", 40);
    },
    recalcul: () => scroll(".hypothesis-card", 80),
    fenetres: () => scroll("#scenario-card", 65),
    mateo: async () => {
      const data = await persona("mateo");
      assert(Math.abs(data.comparison.baseline.metrics.max_drawdown_pct + 12.7) < .1);
      assert(Math.abs(data.comparison.alternative.metrics.max_drawdown_pct + 18.6) < .1);
      await scroll("#result-card", 45);
    },
    agent: () => scroll("#prompt", 125),
    preuves: async () => { await view("preuves"); await top(); },
    questions: async () => { await view("atelier"); await scroll("#insight-card", 45); },
    amira: async () => {
      const data = await persona("amira");
      assert.equal(data.settings.focus_ticker, "NVDA");
      await scroll("#result-card", 45);
    },
    methode: async () => { await view("methode"); await top(); },
    export: async () => {
      await persona("mateo");
      await calc(() => page.locator("#analyze-btn").click());
      await view("preuves");
      await top();
    },
    fin: async () => { await persona("robert"); await top(); },
  };
  const actions = {
    contexte: [
      [7, async () => {
        const details = page.locator(".portfolio-editor");
        if (!(await details.evaluate(element => element.open))) await details.locator("summary").click();
        await scroll(".profile-card", 90);
      }],
    ],
    robert: [[11, async () => {
      const chart = await page.locator("#chart-container").boundingBox();
      await page.mouse.move(chart.x + chart.width * .69, chart.y + chart.height * .35, { steps: 18 });
      await wait(1800);
      await page.mouse.move(190, 110, { steps: 12 });
    }]],
    recalcul: [
      [2.5, async () => { await page.locator("#focus-weight").fill("25"); await wait(450); }],
      [5.3, async () => {
        const data = await calc(() => page.locator("#recalculate-btn").click());
        assert.deepEqual(data.comparison.baseline.series, data.comparison.alternative.series);
        result.same_weights_identical = true;
        await scroll("#result-card", 45);
      }],
      [17, async () => {
        await page.locator("#undo-btn").click();
        assert.equal(await page.locator("#focus-weight").inputValue(), "5");
        await page.locator('[data-chart="drawdown"]').click();
        await scroll("#result-card", 45);
      }],
    ],
    mateo: [[11, async () => { await page.locator('[data-chart="drawdown"]').click(); await scroll("#result-card", 45); }]],
    agent: [[5, async () => {
      const replay = await calc(() => page.locator("#analyze-btn").click());
      assert.deepEqual(replay, archive);
      await scroll("#insight-card", 45);
    }]],
    preuves: [[10, () => scroll("#trace-list", 40)]],
    questions: [[8, () => scroll("#revision-conditions", 145)]],
    amira: [
      [6, async () => { await page.locator('[data-chart="drawdown"]').click(); }],
      [13, async () => {
        const details = page.locator(".portfolio-editor");
        if (!(await details.evaluate(element => element.open))) await details.locator("summary").click();
        await scroll(".profile-card", 80);
      }],
    ],
    methode: [[11, () => scroll(".method-footer", 440)]],
    export: [[5, async () => {
      const downloadEvent = page.waitForEvent("download");
      await page.locator("#export-btn").click();
      const download = await downloadEvent;
      const saved = path.join(manifest.work, "reexported-archive.json");
      await download.saveAs(saved);
      assert.deepEqual(JSON.parse(fs.readFileSync(saved, "utf8")), archive);
      result.export_identical = true;
      await scroll("#agent-detail", 440);
    }]],
  };

  for (const scene of manifest.scenes) {
    // Retain the recorded-evidence label during transitions away from it.
    // Conversely, introduce that label before any archive is displayed.
    if (scene.kind.startsWith("PREUVE BEDROCK")) await label(scene);
    await prepare[scene.id]();
    await label(scene);
    await wait(300);
    const start = clock();
    result.scenes.push({ id: scene.id, start, audio_duration: scene.audio_duration });
    console.log(`Scene ${scene.number}/13: ${scene.id} at ${start.toFixed(2)}s`, { title: scene.title });
    for (const [at, perform] of actions[scene.id] || []) {
      await wait((start + at - clock()) * 1000);
      await perform();
    }
    await wait((start + scene.audio_duration + .65 - clock()) * 1000);
    await page.screenshot({ path: path.join(manifest.work, `scene-${String(scene.number).padStart(2, "0")}.png`) });
  }
  result.end = clock();
  const video = page.video();
  result.wall_duration = clock();
  await context.close();
  result.video = path.join(manifest.work, "application.webm");
  await video.saveAs(result.video);
  await browser.close();
  assert.deepEqual(errors, []);
  fs.writeFileSync(path.join(manifest.work, "capture.json"), JSON.stringify(result, null, 2));
  console.log(JSON.stringify({ duration: result.end, errors, newAws: 0, replayed: result.replayed_requests }));
})().catch(error => { console.error(error); process.exit(1); });
