
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { createObjectCsvWriter } from 'csv-writer';

export async function makeBrowser(headless = true) {
  const browser = await chromium.launch({ headless });
  const context = await browser.newContext({
    viewport: { width: 1366, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118 Safari/537.36'
  });
  const page = await context.newPage();
  return { browser, context, page };
}

export async function saveSiteCsv(siteKey, rows) {
  const outDir = path.join(process.cwd(), 'out');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);
  const filePath = path.join(outDir, `${siteKey}_counts.csv`);
  const writer = createObjectCsvWriter({
    path: filePath,
    header: [
      {id: 'brand', title: 'brand'},
      {id: 'count', title: 'count'}
    ],
    fieldDelimiter: ','
  });
  await writer.writeRecords(rows);
  console.log(`[SAVE] ${filePath}`);
  return filePath;
}

export function loadBrands(filePath = './brands.json') {
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  if (!data.brands || !Array.isArray(data.brands)) {
    throw new Error('brands.json must have a "brands" array');
  }
  return data.brands;
}

export async function acceptCookiesIfPresent(page) {
  const btns = [
    'button:has-text("Accept")',
    'button:has-text("I agree")',
    'button:has-text("Sutinku")',
    'button:has-text("Piekrītu")',
    'button:has-text("Принять")',
    'button:has-text("Akceptēt")',
  ];
  for (const sel of btns) {
    const el = page.locator(sel).first();
    if (await el.count()) {
      try { await el.click({ timeout: 1500 }); break; } catch {}
    }
  }
}
