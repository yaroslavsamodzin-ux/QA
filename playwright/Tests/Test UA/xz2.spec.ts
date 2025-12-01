import { test, expect, Page } from '@playwright/test';

/* ===================== COMMON HELPERS ===================== */
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

/* ===================== COOKIE HANDLER (виправлено strict mode) ===================== */
async function acceptCookiesIfPresent(page: Page) {
  // 1) шукати тільки в контейнерах cookie/consent
  const roots = page.locator([
    '[id*="cookie"]',
    '[class*="cookie"]',
    '[id*="consent"]',
    '[class*="consent"]',
    'div:has-text("cookie")',
    'div:has-text("Cookie")',
    'div:has-text("файли cookie")',
    'div:has-text("файлы cookie")',
  ].join(','));

  const textRe =
    /(accept|agree|allow|ok|окей|ок|принять|соглас|я згоден|погоджуюсь|добре|закрити|закрыть)/i;

  // 2) кнопка всередині банера (беремо першу — без strict)
  const inBanner = roots.locator('button, [role="button"]').filter({ hasText: textRe }).first();
  if (await inBanner.count()) {
    if (await inBanner.isVisible().catch(() => false)) {
      await inBanner.click({ timeout: 1500 }).catch(() => {});
      return;
    }
  }

  // 3) відомі селектори (OneTrust, ін.)
  const known = page.locator('#onetrust-accept-btn-handler, button#onetrust-accept-btn-handler').first();
  if (await known.count()) {
    await known.click({ timeout: 1000 }).catch(() => {});
    return;
  }

  // 4) глобальний фолбек: перша видима кнопка з потрібним текстом
  const anyBtn = page.locator('button, [role="button"]').filter({ hasText: textRe }).first();
  if (await anyBtn.count()) {
    if (await anyBtn.isVisible().catch(() => false)) {
      await anyBtn.click({ timeout: 1500 }).catch(() => {});
      return;
    }
  }

  // 5) останній шанс: закрити хрестиком
  const close = roots.locator('button:has-text("×"), [role="button"]:has-text("×"), .close, .ot-close-icon').first();
  if (await close.count()) {
    await close.click({ timeout: 800 }).catch(() => {});
  }
}

/* ===================== TEMPLATE HELPERS (ТЗ) ===================== */
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
  const y = title.match(/\b(19|20)\d{2}\b/);
  if (!y) return { brandEN: '', modelEN: '' };
  const pre = title.slice(0, y.index!);
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

function buildDescriptionRegex(
  lang: 'uk'|'ru',
  p: {
    brandEN: string; modelEN: string; year: string;
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

/* ===================== PDP CHECK ===================== */
async function checkMetaDescriptionOnPDP(page: Page, url: string) {
  // завжди на .ua (якщо раптом com.lv)
  const u = new URL(url, 'https://automoto.ua/');
  if (/automoto\.com\.lv$/i.test(u.hostname)) u.hostname = 'automoto.ua';

  await page.goto(u.href, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await acceptCookiesIfPresent(page);

  const host = new URL(page.url()).hostname;
  if (!/(^|\.)automoto\.ua$/i.test(host) && !/(^|\.)new\.automoto\.ua$/i.test(host)) {
    test.info().annotations.push({ type: 'skip', description: `Non-UA domain: ${page.url()}` });
    return;
  }

  const title = await page.title();
  expect.soft(title.trim(), `Title empty at ${page.url()}`).not.toBe('');

  const veh = await readJSONLDVehicle(page);
  const lang = detectLang(title);
  const year = extractYear(title, veh);
  const { brandEN, modelEN } = extractBrandModel(title);

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
  const drive = veh?.driveWheelConfiguration || veh?.drive || '';

  const isElectric = /(^|\s)(electro|electric|електро|электро)/i.test(fuel || '');
  if (isElectric) engineLiters = '';

  const priceUSD =
    (veh?.offers?.priceCurrency === 'USD' ? veh?.offers?.price : undefined) ??
    (veh?.offers?.priceCurrency === '$' ? veh?.offers?.price : undefined);

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
  expect.soft(descReal, `Meta description mismatch at ${page.url()}\nRegex: ${rx}`).toMatch(rx);

  if (mileageK != null) expect.soft(descReal).toMatch(/(тис\. км|тыс\. км)/);
  if (priceUSD) expect.soft(descReal).toMatch(/\$/);
}

/* ===================== CATALOG (.ua only) ===================== */
function isUaHost(host: string) {
  return /(^|\.)automoto\.ua$/i.test(host) || /(^|\.)new\.automoto\.ua$/i.test(host);
}
function looksLikeUaPDP(href: string) {
  const host = new URL(href, 'https://automoto.ua/').hostname;
  if (!isUaHost(host)) return false;
  return (/\/(uk|ru)\/obyavlen/i.test(href) || /-\d{5,}\.html(\?.*)?$/i.test(href));
}
async function collectUaAdUrlsOnPage(page: Page): Promise<string[]> {
  const urls = await page.evaluate(() => {
    const anchors = Array.from(document.querySelectorAll('a[href]')) as HTMLAnchorElement[];
    return anchors.map(a => a.href);
  });
  const filtered = urls
    .filter(looksLikeUaPDP)
    .map(u => {
      const url = new URL(u, page.url());
      if (/automoto\.com\.lv$/i.test(url.hostname)) url.hostname = 'automoto.ua';
      return url.href;
    });
  return Array.from(new Set(filtered));
}
// надійний пошук "наступної" сторінки — весь DOM у браузері
async function findNextPageHrefUA(page: Page): Promise<string | null> {
  return await page.evaluate(() => {
    const absolutize = (href: string) => new URL(href, location.href).href;

    // 1) rel="next"
    const rel = document.querySelector('a[rel="next"]') as HTMLAnchorElement | null;
    if (rel?.getAttribute('href')) return absolutize(rel.getAttribute('href')!);

    // 2) текст/aria-label (Next/След/Наступ/Далі)
    const candidates = Array.from(document.querySelectorAll('a[href]')) as HTMLAnchorElement[];
    const nextByLabel = candidates.find(a => {
      const t = (a.textContent || '').toLowerCase();
      const ar = (a.getAttribute('aria-label') || '').toLowerCase();
      return /(next|след|следующая|наступ|далі)/i.test(t) || /(next|след|следующая|наступ|далі)/i.test(ar);
    });
    if (nextByLabel?.getAttribute('href')) return absolutize(nextByLabel.getAttribute('href')!);

    // 3) класична пагінація: активна сторінка + сусідній <a>
    const active = document.querySelector('.pagination .active, li.active, .page-item.active');
    const sib = active?.nextElementSibling?.querySelector('a[href]') as HTMLAnchorElement | null;
    if (sib?.getAttribute('href')) return absolutize(sib.getAttribute('href')!);

    // 4) fallback: інкремент ?page=, тільки якщо у DOM є посилання на наступну
    const url = new URL(location.href);
    const current = Number(url.searchParams.get('page') || '1');
    const probe = `page=${current + 1}`;
    if (document.querySelector(`a[href*="${probe}"]`)) {
      url.searchParams.set('page', String(current + 1));
      return url.href;
    }
    return null;
  });
}
// нескінченна підвантажка
async function lazyLoadMore(page: Page, maxScrolls = 8) {
  let lastCount = 0;
  for (let i = 0; i < maxScrolls; i++) {
    const before = await page.$$eval('a[href]', els => els.length);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(800);
    const after = await page.$$eval('a[href]', els => els.length);
    if (after <= before && after === lastCount) break;
    lastCount = after;
  }
}

/* ===================== MAIN TEST ===================== */
test.describe('Catalog crawl (UA): automoto.ua/car → PDP (.ua) → meta description (ТЗ)', () => {
  const START = 'https://automoto.ua/car';
  const MAX_PAGES = Number(process.env.MAX_PAGES || 5);
  const MAX_ADS_PER_PAGE = Number(process.env.MAX_ADS || 30);

  test.setTimeout(1000 * 60 * 20);

  test('crawl & check', async ({ page, context }) => {
    const visited = new Set<string>();
    let listUrl = START;

    for (let i = 1; i <= MAX_PAGES; i++) {
      await page.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await acceptCookiesIfPresent(page);

      // якщо немає явної пагінації — підвантажимо ще
      if (!(await page.$('.pagination, a[rel="next"], li.next'))) {
        await lazyLoadMore(page, 6);
      }

      const adUrls = (await collectUaAdUrlsOnPage(page))
        .filter(u => !visited.has(u))
        .slice(0, MAX_ADS_PER_PAGE);

      console.log(`List page ${i}: ${adUrls.length} UA ads`);

      for (const url of adUrls) {
        visited.add(url);
        const p2 = await context.newPage();
        try {
          await checkMetaDescriptionOnPDP(p2, url);
        } catch (e) {
          console.error('Error at', url, e);
        } finally {
          await p2.close();
        }
      }

      const nextHref = await findNextPageHrefUA(page);
      if (!nextHref) {
        console.log('No next page — stop.');
        break;
      }
      const nh = new URL(nextHref, page.url());
      if (/automoto\.com\.lv$/i.test(nh.hostname)) nh.hostname = 'automoto.ua';
      listUrl = nh.href;
    }

    console.log(`Checked ${visited.size} UA PDP pages total.`);
  });
});
