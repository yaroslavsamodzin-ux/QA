import { test, expect, Page } from '@playwright/test';

/* ========== UTILS ========== */
const normalize = (s: string) =>
  (s || '').replace(/\s+/g, ' ').replace(/, +/g, ', ').trim();

async function getMeta(page: Page, nameOrProp: string, by: 'name'|'property'='name') {
  const el = page.locator(`head meta[${by}="${nameOrProp}"]`);
  return (await el.count()) ? (await el.first().getAttribute('content')) ?? '' : '';
}

async function readJSONLDVehicle(page: Page) {
  const joined = await page.$$eval('script[type="application/ld+json"]', els =>
    els.map(e => e.textContent || '').join('\n')
  );
  const m = joined.match(/\{[\s\S]*"@type"\s*:\s*"Vehicle"[\s\S]*?\}\s*\}?/i);
  if (!m) return null;
  try { return JSON.parse(m[0]); } catch { return null; }
}

function detectLang(title: string): 'uk'|'ru' {
  if (/(купити|купуйте)/iu.test(title)) return 'uk';
  if (/(купить|покупайте)/iu.test(title)) return 'ru';
  if (/(року|у )/iu.test(title)) return 'uk';
  return 'ru';
}

function extractYear(title: string, veh?: any) {
  const m = title.match(/\b(19|20)\d{2}\b/);
  const yFromTitle = m?.[0];
  const yFromJSON = typeof veh?.productionDate === 'string'
    ? (veh.productionDate.match(/\b(19|20)\d{2}\b/)?.[0] || '')
    : '';
  return yFromTitle || yFromJSON || '';
}

function extractBrandModel(title: string) {
  // два останні слова (латиниця/цифри) перед роком
  const y = title.match(/\b(19|20)\d{2}\b/);
  if (!y) return { brandEN: '', modelEN: '' };
  const pre = title.slice(0, y.index);
  const words = pre.match(/[A-Za-z0-9]+/g) || [];
  const modelEN = words.pop() || '';
  const brandEN = words.pop() || '';
  return { brandEN, modelEN };
}

function sanitizeEngineLiters(v?: string) {
  if (!v) return '';
  const n = Number(String(v).replace(',', '.'));
  if (!isFinite(n) || n <= 0) return '';
  return n > 10 ? (n / 1000).toFixed(1) : n.toString();
}

function kmToThousandsLabel(value: any, lang: 'uk'|'ru') {
  const n = typeof value === 'number' ? value : Number(value?.value ?? value);
  if (!isFinite(n)) return '';
  const k = Math.round(n / 1000);
  return lang === 'uk' ? `${k} тис. км` : `${k} тыс. км`;
}

function buildDescriptionRegex(
  lang: 'uk'|'ru',
  p: {
    brandEN: string; modelEN: string; year: string;
    // місто не фіксуємо жорстко — дозволяємо будь-який фрагмент між "року/года" і "⚡"
    color?: string; bodyType?: string; mileageK?: number;
    fuel?: string; engineLiters?: string; transmission?: string; drive?: string;
    priceUSD?: number | string;
  }
) {
  const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const sp = String.raw`\s+`;
  const sep = String.raw`${sp}`;
  const commaSep = String.raw`${sp},${sp}`;

  const head =
    lang === 'uk'
      ? String.raw`^Купу(?:йте|ти)${sep}${esc(p.brandEN)}${sep}${esc(p.modelEN)}${sep}${esc(p.year)}${sp}року(?:.|(?!$))*?`
      : String.raw`^(?:Покупайте|Купить)${sep}${esc(p.brandEN)}${sep}${esc(p.modelEN)}${sep}${esc(p.year)}${sp}года(?:.|(?!$))*?`;

  const attrs: string[] = [];
  if (p.color || p.bodyType) {
    const combo = [p.color && esc(p.color), p.bodyType && esc(p.bodyType)].filter(Boolean).join(sep);
    if (combo) attrs.push(combo);
  }
  if (p.mileageK != null) {
    attrs.push(
      lang === 'uk'
        ? String.raw`Пробіг${sep}${esc(String(p.mileageK))}${sep}тис\.${sep}км`
        : String.raw`Пробег${sep}${esc(String(p.mileageK))}${sep}тыс\.${sep}км`
    );
  }
  if (p.fuel) {
    const fuelPart = p.engineLiters ? `${esc(p.fuel)}${sep}${esc(p.engineLiters)}${sep}л` : esc(p.fuel);
    attrs.push(fuelPart);
  }
  if (p.transmission) attrs.push(esc(p.transmission));
  if (p.drive) attrs.push(lang === 'uk' ? `${esc(p.drive)}${sep}привід` : `${esc(p.drive)}${sep}привод`);

  const attrsBlock = attrs.length ? String.raw`${sep}⚡${sep}${attrs.join(commaSep)}` : '';

  const priceBlock = p.priceUSD
    ? (lang === 'uk'
        ? String.raw`${sep}за${sep}ціною${sep}${esc(String(p.priceUSD))}\$`
        : String.raw`${sep}по${sep}цене${sep}${esc(String(p.priceUSD))}\$`)
    : '';

  const tail = String.raw`${sep}на${sep}AUTOMOTO\.UA$`;

  return new RegExp(head + attrsBlock + priceBlock + tail, 'iu');
}

/* ========== TEST ========== */
test.describe('SEO Meta Description (adaptive by template)', () => {
  const URLS = [
    // можна додати більше PDP
    'https://new.automoto.ua/renault-modus-2005-dnepr-dnepropetrovsk-68384908.html',
  ];

  for (const URL of URLS) {
    test(`Meta Description matches template: ${URL}`, async ({ page }) => {
      await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 45000 });

      const title = await page.title();
      expect(title.trim()).not.toBe('');

      const veh = await readJSONLDVehicle(page);
      const lang = detectLang(title);
      const year = extractYear(title, veh);
      const { brandEN, modelEN } = extractBrandModel(title);

      // JSON-LD поля (максимально універсально)
      const mileageKm: number | undefined =
        (veh?.mileageFromOdometer?.value as number) ??
        (typeof veh?.mileageFromOdometer === 'number' ? veh.mileageFromOdometer : undefined);

      const color = veh?.color || '';
      const bodyType = veh?.bodyType || veh?.vehicleConfiguration || '';
      const fuel = veh?.vehicleEngine?.fuelType || veh?.fuelType || '';

      let engineLiters = '';
      const eng = veh?.vehicleEngine;
      if (eng?.engineDisplacement) {
        const raw = String(eng.engineDisplacement);
        const lit =
          raw.match(/([\d.,]+)\s*l/i)?.[1] ||
          raw.match(/([\d.,]+)\s*см?3/i)?.[1] ||
          raw.match(/([\d.,]+)/)?.[1];
        if (lit) {
          const n = Number(lit.replace(',', '.'));
          engineLiters = n > 10 ? (n / 1000).toFixed(1) : n.toString();
        }
      }
      engineLiters = sanitizeEngineLiters(engineLiters);

      const transmission = veh?.vehicleTransmission || '';
      const drive =
        veh?.driveWheelConfiguration ||
        veh?.drive ||
        '';

      const isElectric = /(^|\s)(electro|electric|електро|электро)/i.test(fuel || '');
      if (isElectric) engineLiters = ''; // згідно ТЗ — без об’єму для EV

      const priceUSD =
        (veh?.offers?.priceCurrency === 'USD' ? veh?.offers?.price : undefined) ??
        (veh?.offers?.priceCurrency === '$' ? veh?.offers?.price : undefined);

      // будуємо гнучкий RegExp за ТЗ
      const mileageK = mileageKm != null ? Math.round(Number(mileageKm) / 1000) : undefined;
      const rx = buildDescriptionRegex(lang, {
        brandEN, modelEN, year,
        color, bodyType,
        mileageK,
        fuel,
        engineLiters,
        transmission,
        drive,
        priceUSD,
      });

      const descReal = normalize(await getMeta(page, 'description'));
      expect(descReal).toMatch(rx);

      // додатково: базова цілісність
      if (mileageK != null) {
        expect(descReal).toMatch(/(тис\. км|тыс\. км)/);
      }
      if (priceUSD) {
        expect(descReal).toMatch(/\$\b/);
      }

      // лог для дебагу
      console.log({ lang, year, brandEN, modelEN, mileageKm, engineLiters, fuel, transmission, drive, priceUSD });
      console.log('Description:', descReal);
    });
  }
});
