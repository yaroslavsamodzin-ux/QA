// tests/models.hyphen.spec.js
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// --- НАЛАШТУВАННЯ ---
const BASE_HOST  = 'https://automoto.com.lv';
const START_PATH = '/ru/avto';
const TOTAL_PAGES = 6131;           // <- твоя відома кількість сторінок
const CONCURRENCY = 1;              // 1 = послідовно (бережемо сайт). Можна 2-3, якщо треба швидше.
const PAGE_LOAD_TIMEOUT = 20000;    // мс
const SAVE_EVERY = 250;             // зберігати чекпоінт кожні N сторінок
// ---------------------

function ensureDir(p) { if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true }); }

function extractHyphenModelsFromText(text) {
  // слова з дефісом: corolla-verso, a6-allroad, e-200, тощо
  const rx = /\b([a-z0-9]+(?:-[a-z0-9]+)+)\b/gi;
  const out = [];
  let m;
  while ((m = rx.exec(text))) out.push(m[1].toLowerCase());
  return out;
}

async function getCardTitleTexts(page) {
  // Набір потенційних локаторів заголовка картки/посилання на оголошення.
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

  // Якщо жоден з селекторів не спрацював — пробуємо витягнути текст із контейнерів
  const cards = await page.$$('.card, auto-item, article');
  const texts = [];
  for (const c of cards) {
    const t = (await c.textContent().catch(() => '')).trim();
    if (t) texts.push(t);
  }
  return texts;
}

test('Зібрати моделі з дефісом з усіх 6131 сторінок пагінації', async ({ browser }) => {
  const context = await browser.newContext();
  const pagePool = []; // для "паралелі" 1..CONCURRENCY
  for (let i = 0; i < CONCURRENCY; i++) pagePool.push(await context.newPage());

  const resultsDir = path.join('reports', 'models');
  ensureDir(resultsDir);
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonPath = path.join(resultsDir, `models-with-dash__${stamp}.json`);
  const csvPath  = path.join(resultsDir, `models-with-dash__${stamp}.csv`);
  const checkpointPath = path.join(resultsDir, `models-with-dash__checkpoint.json`);

  const modelCounts = new Map();        // model -> count
  const modelExampleUrl = new Map();    // model -> перший URL, де знайшли (для зручності розробників)
  let totalCards = 0;
  let scannedPages = 0;

  async function processPage(p, page) {
    const url = p === 1 ? `${BASE_HOST}${START_PATH}` : `${BASE_HOST}${START_PATH}?page=${p}`;
    try {
      const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: PAGE_LOAD_TIMEOUT });
      if (!resp || !resp.ok()) {
        console.warn(`[WARN] p=${p} status=${resp ? resp.status() : 'no response'} — пропускаю`);
        return;
      }
      const titles = await getCardTitleTexts(page);
      const uniq = [...new Set(titles.map(t => t.replace(/\s+/g, ' ').trim()))];
      totalCards += uniq.length;
      for (const t of uniq) {
        const models = extractHyphenModelsFromText(t);
        for (const m of models) {
          modelCounts.set(m, (modelCounts.get(m) || 0) + 1);
          if (!modelExampleUrl.has(m)) modelExampleUrl.set(m, url);
        }
      }
      scannedPages++;
      if (p % 50 === 0 || p === 1) {
        console.log(`[INFO] p=${p}/${TOTAL_PAGES} | cards≈${uniq.length} | models(total)=${modelCounts.size}`);
      }
    } catch (e) {
      console.warn(`[ERR ] p=${p} failed: ${e.message}`);
    }
  }

  // Послідовно (CONCURRENCY=1) або невеликими "пачками"
  for (let p = 1; p <= TOTAL_PAGES; p += CONCURRENCY) {
    const tasks = [];
    for (let i = 0; i < CONCURRENCY && (p + i) <= TOTAL_PAGES; i++) {
      tasks.push(processPage(p + i, pagePool[i]));
    }
    await Promise.all(tasks);

    // чекпоінт, щоб не втратити прогрес на довгому прогоні
    if ((p % SAVE_EVERY) === 0 || p >= TOTAL_PAGES) {
      const asArray = [...modelCounts.entries()]
        .sort((a, b) => b[1] - a[1])
        .map(([model, count]) => ({
          model, count, example: modelExampleUrl.get(model)
        }));
      fs.writeFileSync(checkpointPath, JSON.stringify({
        startUrl: `${BASE_HOST}${START_PATH}`,
        upToPage: Math.min(p + CONCURRENCY - 1, TOTAL_PAGES),
        scannedPages, totalCards,
        uniqueModelsWithDash: asArray.length,
        models: asArray
      }, null, 2));
      console.log(`[SAVE] checkpoint @ page ${Math.min(p + CONCURRENCY - 1, TOTAL_PAGES)} (${checkpointPath})`);
    }
  }

  // Фінальний звіт
  const final = [...modelCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([model, count]) => ({ model, count, example: modelExampleUrl.get(model) }));

  fs.writeFileSync(jsonPath, JSON.stringify({
    startUrl: `${BASE_HOST}${START_PATH}`,
    scannedPages, totalCards,
    uniqueModelsWithDash: final.length,
    models: final
  }, null, 2), 'utf8');

  const header = 'model,count,example\n';
  const rows = final.map(r => `${r.model},${r.count},${r.example}`).join('\n');
  fs.writeFileSync(csvPath, header + rows + '\n', 'utf8');

  console.log('\n=== Models with hyphen (summary) ===');
  console.log('Start URL      :', `${BASE_HOST}${START_PATH}`);
  console.log('Pages scanned  :', scannedPages, '/', TOTAL_PAGES);
  console.log('Cards seen (~) :', totalCards);
  console.log('Unique models  :', final.length);
  console.table(final.slice(0, 20));
  console.log(`Saved JSON: ${jsonPath}`);
  console.log(`Saved CSV : ${csvPath}`);

  // Мінімальна валідація
  expect(scannedPages).toBeGreaterThan(0);
});
