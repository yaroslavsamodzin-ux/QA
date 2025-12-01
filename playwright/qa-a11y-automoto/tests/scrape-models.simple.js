// tests/scrape-models.simple.js
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BASE_HOST  = process.env.BASE_HOST  || 'https://automoto.com.lv';
const START_PATH = process.env.START_PATH || '/ru/avto';

let START = Number.parseInt(process.env.START ?? '1', 10);
let END   = Number.parseInt(process.env.END   ?? '250', 10);
if (!Number.isFinite(START) || START < 1) START = 1;
if (!Number.isFinite(END)   || END   < START) END = START;

const TIMEOUT_MS = 25000;

function ensureDir(p){ if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true }); }

function hyphenModels(text){
  const rx = /\b([a-z0-9]+(?:-[a-z0-9]+)+)\b/gi;
  const out = []; let m;
  while ((m = rx.exec(text))) out.push(m[1].toLowerCase());
  return out;
}

async function getTitles(page) {
  const pdpTexts = await page.$$eval(
    'a[href*="/ru/bu-avto/"]',
    els => els.map(e => (e.textContent || '').trim()).filter(Boolean)
  );
  if (pdpTexts.length) return pdpTexts;

  const candidates = [
    'auto-item .card-title a',
    '.card .card-title a',
    '.card .card-title',
    'article .card-title a',
    'article h2 a, article h3 a',
    '.card h2 a, .card h3 a',
    'a[href*="/ru/auto/"], a[href*="/lv/auto/"], a[href*="/ru/bu-avto/"], a[href*="/lv/bu-avto/"]',
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

  const cards = await page.$$('.card, auto-item, article');
  const texts = [];
  for (const c of cards) {
    const t = (await c.textContent().catch(() => '')).trim();
    if (t) texts.push(t);
  }
  return texts;
}

(async () => {
  console.log(`[CFG ] BASE=${BASE_HOST}${START_PATH}  RANGE=${START}..${END}`);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const outDir = path.join('reports', 'models');
  ensureDir(outDir);
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonPath = path.join(outDir, `models-with-dash__${stamp}.json`);
  const csvPath  = path.join(outDir, `models-with-dash__${stamp}.csv`);

  const counts  = new Map(); 
  const example = new Map(); 
  let scanned = 0;
  let cardsTotal = 0;

  for (let p = START; p <= END; p++) {
    const url = (p === 1) ? `${BASE_HOST}${START_PATH}` : `${BASE_HOST}${START_PATH}?page=${p}`;

    try {
      const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: TIMEOUT_MS });
      if (!resp || !resp.ok()) {
        console.warn(`[WARN] p=${p} status=${resp ? resp.status() : 'no response'} — skip`);
        continue;
      }

      await page.waitForTimeout(300);
      await page.evaluate(async () => {
        await new Promise(r => {
          let y = 0;
          const max = document.body.scrollHeight;
          const id = setInterval(() => {
            y = Math.min(y + 900, max);
            window.scrollTo(0, y);
            if (y >= max) { clearInterval(id); r(); }
          }, 120);
        });
      });

      const titles = await getTitles(page);
      const uniq = [...new Set(titles.map(t => t.replace(/\s+/g, ' ').trim()))];
      cardsTotal += uniq.length;

      for (const t of uniq) {
        const normalized = t.toLowerCase();
        const words = normalized.split(/\s+/);
        const brand = words[0]; // Перше слово - марка
        const modelPart = words.slice(1).join(' ');

        for (const m of hyphenModels(modelPart)) {
          const key = `${brand} ${m}`;  // ключ включає бренд
          counts.set(key, (counts.get(key) || 0) + 1);
          if (!example.has(key)) example.set(key, url);
        }
      }

      scanned++;
      console.log(`[PAGE] ${p}/${END} | cards≈${uniq.length} | models(total)=${counts.size}`);
    } catch (e) {
      console.warn(`[ERR ] p=${p} ${e.message}`);
    }
  }

  const rows = [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([model, count]) => {
      const [brand, ...rest] = model.split(' ');
      return { brand, model: rest.join(' '), count, example: example.get(model) };
    });

  fs.writeFileSync(jsonPath, JSON.stringify({
    base: `${BASE_HOST}${START_PATH}`,
    range: { start: START, end: END },
    scannedPages: scanned,
    cardsApprox: cardsTotal,
    uniqueModelsWithDash: rows.length,
    models: rows
  }, null, 2), 'utf8');

  fs.writeFileSync(
    csvPath,
    'brand,model,count,example\n' + rows.map(r => `${r.brand},${r.model},${r.count},${r.example}`).join('\n') + '\n',
    'utf8'
  );

  console.log(`\nSaved JSON: ${jsonPath}`);
  console.log(`Saved CSV : ${csvPath}`);
  await browser.close();
})();
