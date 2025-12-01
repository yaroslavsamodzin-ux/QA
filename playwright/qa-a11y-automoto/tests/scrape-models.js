// scripts/scrape-models.js
// Node script (CommonJS) — запускається: node scripts/scrape-models.js
// Налаштування через константи нижче або через ENV/CLI (див. інструкції внизу)

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

// ======== НАЛАШТУВАННЯ ЗА ЗАМОВЧУВАННЯМ ========
const BASE_HOST        = process.env.BASE_HOST  || 'https://automoto.com.lv';
const START_PATH       = process.env.START_PATH || '/ru/avto';
const TOTAL_PAGES_CONF = parseInt(process.env.TOTAL_PAGES ?? '5587', 10); // усі сторінки
const START_PAGE       = parseInt(process.env.START       ?? '1',    10); // можна змінювати
const END_PAGE         = parseInt(process.env.END         ?? String(TOTAL_PAGES_CONF), 10);
const CONCURRENCY      = parseInt(process.env.CONCURRENCY ?? '1',    10); // 1 — максимально безпечно
const PAGE_LOAD_TIMEOUT= parseInt(process.env.PAGE_TIMEOUT?? '25000',10); // мс
const SAVE_EVERY       = parseInt(process.env.SAVE_EVERY  ?? '250',  10); // чекпоінт
const HEADLESS         = (process.env.HEADED ?? '1') !== '0'; // 1=headless, 0 = показувати браузер
// ================================================

function ensureDir(p) { if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true }); }

function extractHyphenModelsFromText(text) {
  // ловимо "слова" з одним або більше дефісів: corolla-verso, e-200, a6-allroad-quadro
  const rx = /\b([a-z0-9]+(?:-[a-z0-9]+)+)\b/gi;
  const out = [];
  let m;
  while ((m = rx.exec(text))) out.push(m[1].toLowerCase());
  return out;
}

async function getCardTitleTexts(page) {
  // На різних сторінках верстка може різнитись — перебираємо кілька селекторів
  const candidates = [
    'auto-item .card-title a',
    '.card .card-title a',
    '.card .card-title',
    'article .card-title a',
    'article h2 a, article h3 a',
    '.card h2 a, .card h3 a',
    // fallback: будь-яке посилання на PDP
    'auto-item a[href*="/ru/auto/"], .card a[href*="/ru/auto/"], a[href*="/ru/auto/"]',
  ];

  for (const sel of candidates) {
    const nodes = await page.$$(sel);
    if (nodes.length) {
      const texts = [];
      for (const n of nodes) {
        const t = (await n.innerText().catch(() => '')).trim();
        if (t) texts.push(t);
      }
      if (texts.length) return texts;
    }
  }

  // Якщо зовсім нічого — спробуємо витягти текст з карток в цілому
  const cards = await page.$$('.card, auto-item, article');
  const texts = [];
  for (const c of cards) {
    const t = (await c.textContent().catch(() => '')).trim();
    if (t) texts.push(t);
  }
  return texts;
}

(async () => {
  const browser = await chromium.launch({ headless: HEADLESS });
  const context = await browser.newContext();
  const pagePool = [];
  for (let i = 0; i < CONCURRENCY; i++) pagePool.push(await context.newPage());

  const resultsDir = path.join('reports', 'models');
  ensureDir(resultsDir);
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonPath = path.join(resultsDir, `models-with-dash__${stamp}.json`);
  const csvPath  = path.join(resultsDir, `models-with-dash__${stamp}.csv`);
  const checkpointPath = path.join(resultsDir, `models-with-dash__checkpoint.json`);

  const modelCounts = new Map();     // model -> count
  const modelExample = new Map();    // model -> перший URL (для dev’ів)
  let totalCards = 0;
  let scannedPages = 0;

  async function processPage(p, page) {
    const url = p === 1
      ? `${BASE_HOST}${START_PATH}`
      : `${BASE_HOST}${START_PATH}?page=${p}`;

    try {
      const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: PAGE_LOAD_TIMEOUT });
      if (!resp || !resp.ok()) {
        console.warn(`[WARN] p=${p} status=${resp ? resp.status() : 'no response'} — пропускаю`);
        return;
      }

      // інколи контент догружається пізніше — додатково трошки чекаємо
      await page.waitForTimeout(150);

      const titles = await getCardTitleTexts(page);
      const uniq = [...new Set(titles.map(t => t.replace(/\s+/g, ' ').trim()))];

      totalCards += uniq.length;
      for (const t of uniq) {
        const models = extractHyphenModelsFromText(t);
        for (const m of models) {
          modelCounts.set(m, (modelCounts.get(m) || 0) + 1);
          if (!modelExample.has(m)) modelExample.set(m, url);
        }
      }
      scannedPages++;
      if (p === START_PAGE || p % 50 === 0) {
        console.log(`[INFO] p=${p}/${END_PAGE} | cards≈${uniq.length} | models(total)=${modelCounts.size}`);
      }
    } catch (e) {
      console.warn(`[ERR ] p=${p} failed: ${e.message}`);
    }
  }

  // основний цикл: послідовно або малими пачками
  for (let p = START_PAGE; p <= END_PAGE; p += CONCURRENCY) {
    const tasks = [];
    for (let i = 0; i < CONCURRENCY && (p + i) <= END_PAGE; i++) {
      tasks.push(processPage(p + i, pagePool[i]));
    }
    await Promise.all(tasks);

    // чекпоінт періодично
    if ((p - START_PAGE) % SAVE_EVERY === 0 || p >= END_PAGE) {
      const arr = [...modelCounts.entries()]
        .sort((a, b) => b[1] - a[1])
        .map(([model, count]) => ({ model, count, example: modelExample.get(model) }));

      fs.writeFileSync(checkpointPath, JSON.stringify({
        startUrl: `${BASE_HOST}${START_PATH}`,
        processedRange: { from: START_PAGE, to: Math.min(p + CONCURRENCY - 1, END_PAGE) },
        scannedPages, totalCards,
        uniqueModelsWithDash: arr.length,
        models: arr,
      }, null, 2));
      console.log(`[SAVE] checkpoint @ page ${Math.min(p + CONCURRENCY - 1, END_PAGE)} → ${checkpointPath}`);
    }
  }

  // фінальний звіт
  const final = [...modelCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([model, count]) => ({ model, count, example: modelExample.get(model) }));

  fs.writeFileSync(jsonPath, JSON.stringify({
    startUrl: `${BASE_HOST}${START_PATH}`,
    pages: { start: START_PAGE, end: END_PAGE, totalExpected: TOTAL_PAGES_CONF },
    scannedPages, totalCards,
    uniqueModelsWithDash: final.length,
    models: final,
  }, null, 2), 'utf8');

  const header = 'model,count,example\n';
  fs.writeFileSync(
    csvPath,
    header + final.map(r => `${r.model},${r.count},${r.example}`).join('\n') + '\n',
    'utf8'
  );

  console.log('\n=== Models with hyphen — SUMMARY ===');
  console.log('Start URL     :', `${BASE_HOST}${START_PATH}`);
  console.log('Pages scanned :', scannedPages, `(range ${START_PAGE}..${END_PAGE} / expected ${TOTAL_PAGES_CONF})`);
  console.log('Cards seen (~):', totalCards);
  console.log('Unique models :', final.length);
  console.log('Saved JSON    :', jsonPath);
  console.log('Saved CSV     :', csvPath);

  await browser.close();
})().catch(err => {
  console.error(err);
  process.exit(1);
});
