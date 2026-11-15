/* Record real prototype interactions. No generated animation or model call.
 * Usage: node docs/experience/proofs/demo.cjs
 * Requires the prototype server on 127.0.0.1:8770 and existing Playwright.
 */
const path = require('path');
const fs = require('fs');
const root = path.resolve(__dirname, '../../..');
const { chromium } = require(path.join(root, 'runtime/browser-check/node_modules/playwright'));
const output = path.join(root, 'prototype/prompt6/demo');
fs.mkdirSync(output, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    recordVideo: { dir: output, size: { width: 1440, height: 1000 } },
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  const video = page.video();
  const actions = [], errors = [], calculations = [];
  const start = Date.now();
  const mark = (action) => actions.push({ seconds: Number(((Date.now() - start) / 1000).toFixed(2)), action });
  const hold = async (seconds) => new Promise(resolve => setTimeout(resolve, seconds * 1000));
  const click = async (selector, label, pause = 2) => {
    const element = page.locator(selector).first();
    await element.scrollIntoViewIfNeeded();
    const box = await element.boundingBox();
    if (box) await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 12 });
    mark(label);
    await element.click();
    await hold(pause);
  };
  page.on('pageerror', error => errors.push(error.message));
  page.on('response', async response => {
    if (response.url().endsWith('/api/prototype/explore')) {
      try {
        const body = await response.json();
        calculations.push({
          status: response.status(), mode: body.mode,
          receipt: body.receipt, simulated_error: body.detail?.simulated || false,
        });
      } catch (error) { errors.push(`Receipt read: ${error.message}`); }
    }
  });
  try {
    mark('Ouvrir la promesse et les dossiers de référence');
    await page.goto('http://127.0.0.1:8770/#accueil');
    await page.waitForSelector('.home-hero');
    await hold(4);
    await click('.home-hero a[href="#dossier/robert/r5/decision"]', 'Ouvrir Robert r5', 3);
    await click('[data-action=proof]', 'Examiner la preuve du minimum conditionnel', 5);
    await click('#close-panel', 'Revenir à la conclusion', 1);
    await click('[data-action=level][data-id=explore]', 'Approfondir la même conclusion, résultats invariants', 2);
    await page.locator('.chart-panel').scrollIntoViewIfNeeded();
    mark('Comparer les allocations et la règle simple');
    await hold(4);
    await page.locator('.data-table').first().scrollIntoViewIfNeeded();
    await hold(3);
    await click('[data-action=tab][data-id=variants]', 'Explorer une variante sans changer le dossier', 2);
    await page.locator('#field-withdrawal_cad').fill('40000');
    mark('Corriger le retrait dans une copie : 30 000 → 40 000 CAD');
    await hold(2);
    await click('#explore-form button[type=submit]', 'Lancer le moteur Python sur les paramètres copiés', 2);
    await page.waitForSelector('[data-action=adopt]');
    await page.locator('.scenario-result').scrollIntoViewIfNeeded();
    await hold(4);
    await click('[data-action=adopt]', 'Adopter dans la copie locale seulement', 2);
    await click('[data-action=restore]', 'Annuler la copie et retrouver l’archive', 2);
    await click('[data-action=tab][data-id=variants]', 'Examiner une erreur récupérable', 1);
    await page.locator('#field-withdrawal_cad').fill('40000');
    await page.locator('summary').filter({ hasText: 'Examiner la récupération après erreur' }).click();
    await page.locator('input[name=simulate_error]').check();
    await click('#explore-form button[type=submit]', 'Déclencher l’erreur explicitement simulée', 2);
    await page.waitForSelector('[data-action=retry]');
    await page.locator('.form-error').scrollIntoViewIfNeeded();
    await hold(3);
    await click('[data-action=retry]', 'Reprendre le calcul réel avec les mêmes paramètres', 2);
    await page.waitForSelector('[data-action=adopt]');
    await hold(2);
    await click('[data-action=tab][data-id=history]', 'Voir les trois révisions AWS réellement archivées', 3);
    await page.locator('.history-card').nth(1).scrollIntoViewIfNeeded();
    await hold(4);
    await page.locator('.history-card').nth(2).scrollIntoViewIfNeeded();
    await hold(3);
    await click('a[href="#accueil"]', 'Revenir aux dossiers', 1);
    await click('a.case-card[href="#dossier/amira/r5/decision"]', 'Ouvrir Amira : autre profil et autre méthode', 3);
    await page.locator('.line-chart').scrollIntoViewIfNeeded();
    mark('Examiner deux trajectoires historiques réelles, sans projection');
    await hold(5);
    await click('[data-action=series]', 'Accéder aux observations exactes derrière les courbes', 3);
    await click('#close-panel', 'Revenir au contexte et aux limites', 2);
    mark('Fin de démonstration');
  } finally {
    await context.close();
    const original = await video.path();
    const destination = path.join(output, 'AlphaForge-prototype-reference.webm');
    fs.renameSync(original, destination);
    await browser.close();
    const report = {
      generated_at: new Date().toISOString(), duration_seconds: Number(((Date.now() - start) / 1000).toFixed(2)),
      video: path.relative(root, destination), viewport: '1440×1000',
      mode: 'Real browser clicks, archived dossiers, isolated deterministic calculations',
      model_calls: 0, product_mutations: 0, actions, calculations, browser_errors: errors,
    };
    fs.writeFileSync(path.join(output, 'actions.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ video: report.video, seconds: report.duration_seconds, errors, actions: actions.length }));
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
