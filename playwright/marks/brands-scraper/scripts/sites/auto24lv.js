import { acceptCookiesIfPresent } from '../common.js';
import fs from 'fs';
import path from 'path';

function normalizeBrand(s) {
  return (s || '')
    .replace(/\s+/g, ' ')
    .replace(/[‐-–—−]+/g, '-')        // різні дефіси в один
    .trim()
    .toLowerCase();
}

const SITE = {
  key: 'auto24lv',
  url: 'https://www.auto24.lv/',
  async scrape(page, brands) {
    const listUrls = [
      'https://www.auto24.lv/',
      'https://www.auto24.lv/lv/',
      'https://www.auto24.lv/lv/auto',
      'https://www.auto24.lv/en/',
      'https://www.auto24.lv/en/auto',
    ];

    // 1) відкриваємо будь-яку робочу лістинг-сторінку
    let opened = false;
    for (const u of listUrls) {
      try {
        await page.goto(u, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await acceptCookiesIfPresent(page);
        const bodyText = (await page.content()) || '';
        if (bodyText.toLowerCase().includes('auto')) { opened = true; break; }
      } catch {}
    }
    if (!opened) throw new Error('Cannot open listing page — update listUrls');

    // 2) спробуємо розгорнути можливі секції фільтрів (Марка/Make/Zīmols)
    const sectionTriggers = [
      'text=/\\bМарка\\b/i',
      'text=/\\bMake\\b/i',
      'text=/\\bZīmols\\b/i',
      'text=/\\bMarka\\b/i'
    ];
    for (const sel of sectionTriggers) {
      try { await page.locator(sel).first().click({ timeout: 800 }); } catch {}
    }

    // 3) зібрати всі пари "назва (число)" з сайдбарів/фільтрів
    const containers = [
      'aside', '.sidebar', '#sidebar', '.filters', '.facets',
      '.filter-block', '.search-filter', '.left', '.refine', '.refinements'
    ];
    const itemSelectors = containers.map(c => `${c} li, ${c} a, ${c} label, ${c} span, ${c} div`);

    // прочитати тексти
    const texts = [];
    for (const sel of itemSelectors) {
      const items = page.locator(sel);
      const n = await items.count();
      for (let i = 0; i < Math.min(n, 4000); i++) {
        const it = items.nth(i);
        const t = (await it.textContent() || '').replace(/\s+/g, ' ').trim();
        if (t && t.length <= 80) texts.push(t);
      }
    }

    // 4) побудувати мапу brand->count із знайдених рядків
    // Патерни: "Audi (123)" або "Audi 123" або "Audi — 123"
    const map = new Map();
    const reList = [
      /^(.+?)\s*\((\d{1,7})\)\s*$/,         // Audi (123)
      /^(.+?)\s*[–—\-]?\s*(\d{1,7})\s*$/,   // Audi — 123  / Audi-123 / Audi 123
    ];

    for (const t of texts) {
      for (const re of reList) {
        const m = t.match(re);
        if (m) {
          let b = m[1].replace(/\s+/g, ' ').trim();
          const c = parseInt(m[2], 10);
          if (!b || isNaN(c)) continue;
          const key = normalizeBrand(b);
          // інколи один бренд дублюється в різних блоках — беремо максимум
          map.set(key, Math.max(map.get(key) || 0, c));
          break;
        }
      }
    }

    // дебаг: вивести перші 30 пар
    const preview = Array.from(map.entries()).slice(0, 30);
    console.log(`[${SITE.key}] found facet pairs:`, preview);

    // якщо нічого не знайшли — збережемо HTML для діагностики
    if (map.size === 0) {
      const html = await page.content();
      const outDir = path.join(process.cwd(), 'out');
      if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);
      fs.writeFileSync(path.join(outDir, 'auto24lv_debug.html'), html, 'utf-8');
      console.warn(`[${SITE.key}] facet map is empty — saved out/auto24lv_debug.html for inspection`);
    }

    // 5) зіставляємо з нашим списком брендів
    const rows = [];
    for (const brand of brands) {
      const key = normalizeBrand(brand);
      const count = map.get(key) || 0;
      rows.push({ brand, count });
      if (rows.length % 25 === 0) console.log(`[${SITE.key}] ${rows.length}/${brands.length} done`);
    }
    return rows;
  }
};

export default SITE;
