import { test, expect, Page } from '@playwright/test';

type Case = {
  url: 'https://new.automoto.ua/renault-modus-2005-dnepr-dnepropetrovsk-68384908.html';
  lang: 'uk' | 'ru';
  hasVIN: boolean;
  isSold: boolean;
  // очікувані дані (можна підвантажувати з фікстур JSON)
  brandEN: string;
  modelEN: string;
  brandLoc: string; // Фольксваген / Мерседес тощо (для ru/uk)
  modelLoc: string; // Туарег / Віто тощо
  year: string;     // "2018"
  cityLoc: string;  // "Вінниці" / "Виннице"
  priceUSD?: number;
  vin?: string;
  colorLoc?: string;        // "Чорний" / "Черный"
  bodyTypeLoc?: string;     // "Позашляховик/кросовер" / "Внедорожник/кроссовер"
  mileageK?: number;        // 80 (тис. км)
  fuelLoc?: string;         // "Дизель" / "Дизель"
  engineLiters?: string;    // "3.0"
  transmissionLoc?: string; // "Автомат" / "Автомат"
  driveLoc?: string;        // "Передній" / "Передний"
};

const cases: Case[] = [
  // TODO: заповнити реальними URL
  // { url:'https://automoto....html', lang:'uk', hasVIN:true, isSold:false, brandEN:'Volkswagen', modelEN:'Touareg', brandLoc:'Фольксваген', modelLoc:'Туарег', year:'2018', cityLoc:'Вінниці', priceUSD:44900, vin:'WV1ZZZ9KZXR517722', colorLoc:'Чорний', bodyTypeLoc:'Позашляховик/кросовер', mileageK:80, fuelLoc:'Дизель', engineLiters:'3.0', transmissionLoc:'Автомат', driveLoc:'Передній' },
];

async function getMeta(page: Page, nameOrProp: string, by: 'name'|'property'='name') {
  const sel = `head meta[${by}="${nameOrProp}"]`;
  const el = page.locator(sel);
  return (await el.count()) ? (await el.first().getAttribute('content')) ?? '' : '';
}

async function getLink(page: Page, rel: string) {
  const sel = `head link[rel="${rel}"]`;
  const el = page.locator(sel);
  return (await el.count()) ? (await el.first().getAttribute('href')) ?? '' : '';
}

function normalizeSpaces(s: string) {
  return s.replace(/\s+/g, ' ').trim();
}

test.describe('SEO Final Page spec', () => {
  for (const c of cases) {
    test.describe(`${c.url}`, () => {
      test.beforeEach(async ({ page }) => {
        await page.goto(c.url, { waitUntil: 'domcontentloaded' });
      });

      test('Meta Title / Description / Keywords', async ({ page }) => {
        const title = await page.title();
        const desc = await getMeta(page, 'description');
        const keywords = await getMeta(page, 'keywords');

        // Title шаблон
        if (!c.hasVIN) {
          // "Купити {EN} {EN} {Рік} у {Місто} | {Марка Loc} {Модель Loc} за ціною {Ціна}$"
          if (c.lang === 'uk') {
            const rx = new RegExp(
              `^Купити ${c.brandEN} ${c.modelEN} ${c.year} у ${c.cityLoc} \\| ${c.brandLoc} ${c.modelLoc}( за ціною ${c.priceUSD}\\$)?$`
            );
            expect(normalizeSpaces(title)).toMatch(rx);
          } else {
            const rx = new RegExp(
              `^Купить ${c.brandEN} ${c.modelEN} ${c.year} в ${c.cityLoc} \\| ${c.brandLoc} ${c.modelLoc}( по цене ${c.priceUSD}\\$)?$`
            );
            expect(normalizeSpaces(title)).toMatch(rx);
          }
        } else {
          if (c.lang === 'uk') {
            const rx = new RegExp(
              `^Купити ${c.brandEN} ${c.modelEN} ${c.year} у ${c.cityLoc} \\| ${c.brandLoc} ${c.modelLoc}( за ціною ${c.priceUSD}\\$)? VIN:${c.vin}$`
            );
            expect(normalizeSpaces(title)).toMatch(rx);
          } else {
            const rx = new RegExp(
              `^Купить ${c.brandEN} ${c.modelEN} ${c.year} в ${c.cityLoc} \\| ${c.brandLoc} ${c.modelLoc}( по цене ${c.priceUSD}\\$)? VIN:${c.vin}$`
            );
            expect(normalizeSpaces(title)).toMatch(rx);
          }
        }

        // Description: перевірка ключових фрагментів і відсутності порожніх плейсхолдерів
        if (c.lang === 'uk') {
          expect(desc).toContain(`${c.brandEN} ${c.modelEN} ${c.year}`);
          if (c.colorLoc) expect(desc).toContain(c.colorLoc);
          if (c.bodyTypeLoc) expect(desc).toContain(c.bodyTypeLoc);
          if (c.mileageK != null) expect(desc).toMatch(new RegExp(`Пробіг\\s+${c.mileageK}\\s+тис\\. км`));
          if (c.fuelLoc) expect(desc).toContain(c.fuelLoc);
          if (c.engineLiters) expect(desc).toContain(`${c.engineLiters} л`);
          if (c.transmissionLoc) expect(desc).toContain(c.transmissionLoc);
          if (c.driveLoc) expect(desc).toContain(c.driveLoc);
          if (c.priceUSD) expect(desc).toContain(`${c.priceUSD}$`);
        } else {
          expect(desc).toContain(`${c.brandEN} ${c.modelEN} ${c.year}`);
          if (c.colorLoc) expect(desc).toContain(c.colorLoc);
          if (c.bodyTypeLoc) expect(desc).toContain(c.bodyTypeLoc);
          if (c.mileageK != null) expect(desc).toMatch(new RegExp(`Пробег\\s+${c.mileageK}\\s+тыс\\. км`));
          if (c.fuelLoc) expect(desc).toContain(c.fuelLoc);
          if (c.engineLiters) expect(desc).toContain(`${c.engineLiters} л`);
          if (c.transmissionLoc) expect(desc).toContain(c.transmissionLoc);
          if (c.driveLoc) expect(desc).toContain(c.driveLoc);
          if (c.priceUSD) expect(desc).toContain(`${c.priceUSD}$`);
        }

        // Keywords — базова наявність ключових слів (мінімальний асерт)
        expect(keywords.toLowerCase()).toContain(c.brandEN.toLowerCase());
        expect(keywords.toLowerCase()).toContain(c.modelEN.toLowerCase());
      });

      test('Meta Robots', async ({ page }) => {
        const robots = await getMeta(page, 'robots');
        const expected = c.isSold && !c.hasVIN ? 'noindex, follow' : 'index, follow';
        expect(robots).toBe(expected);
      });

      test('Canonical self-reference', async ({ page }) => {
        const canon = await getLink(page, 'canonical');
        const current = new URL(page.url());
        expect(canon.replace(/\/+$/, '')).toBe(current.href.replace(/\/+$/, ''));
      });

      test('Hreflang & x-default', async ({ page }) => {
        const need = [
          { hreflang: 'uk-ua' },
          { hreflang: 'ru-ua' },
          { hreflang: 'uk' },
          { hreflang: 'ru' },
          { hreflang: 'x-default' },
        ];
        for (const n of need) {
          const sel = `head link[rel="alternate"][hreflang="${n.hreflang}"]`;
          await expect(page.locator(sel)).toHaveCount(1);
          const href = await page.locator(sel).first().getAttribute('href');
          expect(href).toBeTruthy();
          if (n.hreflang === 'x-default') {
            expect(href!.includes('/uk/')).toBeTruthy(); // x-default → укр
          }
        }
      });

      test('Breadcrumbs HTML', async ({ page }) => {
        // підлаштуй під фактичний селектор крихт
        const crumbs = page.locator('nav[aria-label="breadcrumbs"] a, nav.breadcrumbs a, .breadcrumbs a');
        const count = await crumbs.count();
        expect(count).toBeGreaterThan(3);          // > 3
        // або якщо треба не менше 4:
        expect(count).toBeGreaterThanOrEqual(4);

        // остання крихта — VIN якщо є
        const last = await crumbs.last().innerText();
        if (c.hasVIN) {
          expect(last).toMatch(new RegExp(`VIN:\\s*${c.vin}`));
        } else {
          expect(last).toContain(`${c.brandLoc} ${c.modelLoc} ${c.year}`);
        }
      });

      test('Open Graph / Twitter Cards', async ({ page }) => {
        const ogType = await getMeta(page, 'og:type', 'property');
        expect(ogType).toBe('article');
        const title = await page.title();
        const ogTitle = await getMeta(page, 'og:title', 'property');
        const twTitle = await getMeta(page, 'twitter:title');
        expect(ogTitle).toBe(title);
        expect(twTitle).toBe(title);
        const ogDesc = await getMeta(page, 'og:description', 'property');
        const desc = await getMeta(page, 'description');
        expect(ogDesc).toBe(desc);

        // image або фолбек
        const ogImg = await getMeta(page, 'og:image', 'property');
        const twImg = await getMeta(page, 'twitter:image');
        expect(ogImg || '').not.toEqual('');
        expect(twImg || '').not.toEqual('');
      });

      test('JSON-LD BreadcrumbList', async ({ page }) => {
        const ld = await page.$$eval('script[type="application/ld+json"]', els =>
          els.map(e => e.textContent || '').join('\n')
        );
        const data = JSON.parse(ld.match(/\{[\s\S]*"@type"\s*:\s*"BreadcrumbList"[\s\S]*?\}\s*\}?/i)![0]);
        expect(data['@type']).toBe('BreadcrumbList');
        expect(Array.isArray(data.itemListElement)).toBeTruthy();
        // базові позиції 1..n і коректні назви пунктів — довільні детальні перевірки
      });

      test('JSON-LD Vehicle', async ({ page }) => {
        const ldAll = await page.$$eval('script[type="application/ld+json"]', els =>
          els.map(e => e.textContent || '').join('\n')
        );
        const match = ldAll.match(/\{[\s\S]*"@type"\s*:\s*"Vehicle"[\s\S]*?\}\s*\}?/i);
        expect(match).toBeTruthy();
        const veh = JSON.parse(match![0]);

        // Обов'язкові поля
        const must = [
          'bodyType','driveWheelConfiguration','mileageFromOdometer','productionDate','vehicleConfiguration',
          'logo','vehicleEngine','fuelType','vehicleTransmission','aggregateRating','brand','color',
          'itemCondition','keywords','manufacturer','model','offers','description','image','name','url'
        ];
        for (const k of must) expect(veh).toHaveProperty(k);

        // availability / price / currency
        expect(veh.offers).toHaveProperty('availability');
        expect(['InStock','OutOfStock','SoldOut']).toContain(veh.offers.availability);
        if (c.isSold) expect(['OutOfStock','SoldOut']).toContain(veh.offers.availability);

        // До 10 зображень
        expect(Array.isArray(veh.image)).toBeTruthy();
        expect(veh.image.length).toBeLessThanOrEqual(10);
      });

      test('Підказки (title-атрибути) та копіювання VIN/номеру', async ({ page }) => {
        // приклади селекторів: підлаштуй під верстку
        const fav = page.getByRole('button', { name: /обра(н|ні)|избран/i });
        await expect(fav).toHaveAttribute('title', c.lang === 'uk' ? 'Додати в обране' : 'Добавить в избранное');

        const copyVin = page.getByRole('button', { name: /vin/i });
        await expect(copyVin).toHaveAttribute('title', c.lang === 'uk' ? 'Скопіювати VIN код' : 'Скопировать VIN код');
      });

      test('Перелінковка з блоку "Основне"', async ({ page }) => {
        // приклад: клацаємо на значення "Тип кузову", звіряємо URL
        // Нехай у верстці є data-qa атрибути
        const bodyLink = page.locator('[data-qa="basic-bodyType"] a');
        if (await bodyLink.count()) {
          const href = await bodyLink.first().getAttribute('href');
          expect(href).toMatch(new RegExp(`^https://automoto\\.ua/${c.lang}/car/`));
        }
      });
    });
  }
});
