import { test, expect, Page, chromium } from '@playwright/test';

async function acceptCookiesIfPresent(page: Page) {
  // пробуємо знайти кнопку прийняття кукі українською/російською/англійською/латиською
  const consentBtn = page.getByRole('button', {
    name: /прийня|погодж|згод|ок|добре|accept|agree|принять|piekrītu/i,
  });
  try {
    if (await consentBtn.isVisible()) {
      await consentBtn.click({ timeout: 2000 });
    }
  } catch {
    /* ігноруємо, якщо банер зник сам */
  }
}

test('Каталог → PDP (UA): клікаємо всі характеристики у блоці "Основна/Key/Galvenā інформація"', async ({ page, context }) => {
  const START_URL = 'https://automoto.ua/uk/';
  const MAX_CARDS = 3;

  await page.goto(START_URL, { waitUntil: 'domcontentloaded' });
  await acceptCookiesIfPresent(page);

  // З головної збираємо посилання-картки оголошень:
  // — посилання в <main>, що ведуть на /uk/... і містять зображення (типова картка)
  const cardLinks = page
    .locator('main a[href^="/uk/"]')
    .filter({ has: page.locator('img') });

  // Щоб не підхопити навігаційні банери, візьмемо лише ті, де в href не порожній останній сегмент
  const total = await cardLinks.count();
  expect(total, 'Не знайдено жодної картки з головної').toBeGreaterThan(0);

  // Пробіжимося по перших MAX_CARDS
  for (let i = 0; i < Math.min(total, MAX_CARDS); i++) {
    const link = cardLinks.nth(i);

    await Promise.all([
      page.waitForURL(/\/uk\/.+/i),
      link.click(),
    ]);

    // Перевіряємо, що це PDP: є H1 і основний блок контенту
    await expect(page.locator('h1')).toBeVisible();

    // 1) Знаходимо секцію характеристик за H3 будь-якою з мов
    const infoSection = page
      .locator('section, div')
      .filter({
        has: page.getByRole('heading', {
          level: 3,
          name: /Основна інформація|Key information|Основная информация|Galvenā informācija/i,
        }),
      })
      .first();

    await expect(infoSection, 'Секцію з характеристиками не знайдено').toBeVisible();

    // 2) Усі посилання всередині секції (перевага ul a, інакше всі a)
    let infoLinks = infoSection.locator('a');
    const listLinks = infoSection.locator('ul a');
    if (await listLinks.count()) infoLinks = listLinks;

    const infoCount = await infoLinks.count();
    expect(infoCount, 'У секції характеристик немає посилань').toBeGreaterThan(0);

    for (let j = 0; j < infoCount; j++) {
      const ilink = infoLinks.nth(j);
      const href = await ilink.getAttribute('href');
      if (!href || href.startsWith('#')) continue; // пропускаємо якірні

      // Якщо посилання відкривається у новій вкладці — ловимо її й закриваємо.
      // Інакше — відкриється в цій самій вкладці: чекаємо навігацію та повертаємось Back.
      const target = (await ilink.getAttribute('target')) || '';
      if (target === '_blank') {
        const [newPage] = await Promise.all([
          context.waitForEvent('page'),
          ilink.click({ button: 'middle' }),
        ]);
        await newPage.waitForLoadState('domcontentloaded');
        await expect(newPage).toHaveURL(/https?:\/\/[^/]+\/.*/i);
        await newPage.close();
      } else {
        await Promise.all([
          page.waitForLoadState('domcontentloaded'),
          ilink.click(),
        ]);
        await expect(page).toHaveURL(/https?:\/\/[^/]+\/.*/i);
        await page.goBack(); // повертаємось на PDP
        await expect(infoSection).toBeVisible(); // секція знову видима
      }
    }

    // Повертаємось на головну /uk/ (де брали картки)
    await Promise.all([
      page.waitForURL(/\/uk\/?$/i),
      page.goBack(),
    ]);
  }
});
