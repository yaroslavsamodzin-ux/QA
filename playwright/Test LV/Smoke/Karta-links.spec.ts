import { test, expect, Page } from '@playwright/test';

async function acceptCookiesIfPresent(page: Page) {
  const consentBtn = page.getByRole('button', {
    name: /прийня|погодж|згод|ок|добре|accept|agree|принять|piekrītu/i,
  });
  try {
    await consentBtn.waitFor({ state: 'visible', timeout: 2000 });
    await consentBtn.click();
  } catch {}
}

test('Каталог → PDP (UA): клікаємо характеристики в секції інформації', async ({ page, context }) => {
  const START_URL = 'https://automoto.ua/uk/';
  const MAX_CARDS = 3;

  await page.goto(START_URL, { waitUntil: 'domcontentloaded' });
  await acceptCookiesIfPresent(page);

  // 1) Візьмемо саме картки оголошень (звузили селектор до типових карток PDP)
  const cardLinks = page
    .locator('main a[href^="/uk/"]')
    .filter({
      has: page.locator('img'),
      // часто PDP мають у шляху маркер "ogoloshennya" або інший стабільний фрагмент
      // якщо знаєш точний фрагмент PDP — залиш його; якщо ні, фільтруй по дод. умовах:
    });

  const total = await cardLinks.count();
  expect(total, 'Не знайдено жодної картки з головної').toBeGreaterThan(0);

  const cardsToTest = Math.min(total, MAX_CARDS);
  for (let i = 0; i < cardsToTest; i++) {
    const link = cardLinks.nth(i);

    // 2) Прокрутимо до елемента та переконаємось, що можна клікнути
    await link.scrollIntoViewIfNeeded();
    await expect(link).toBeVisible();

    const prevUrl = page.url();

    // 3) Клік і коректне очікування: або справжня навігація, або хоча б зміна URL
    await Promise.all([
      page.waitForLoadState('domcontentloaded'),
      link.click({ trial: false }),
    ]);

    // якщо soft-навігація, перевіримо факт зміни URL
    await expect.poll(async () => page.url(), {
      message: 'URL не змінився після кліку по картці',
      timeout: 5000,
    }).not.toBe(prevUrl);

    // 4) PDP: h1 може прогружатися — чекаємо видимість/непорожній текст
    const h1 = page.locator('h1');
    await h1.waitFor({ state: 'visible', timeout: 10000 });
    await expect(h1).not.toHaveText(/^$/);

    // 5) Секція інформації: інколи це h2 або текст без рівня — зробимо кілька варіантів
    const infoSection = page
      .locator('section, div')
      .filter({
        has: page.locator('h1,h2,h3,h4', {
          hasText: /Основна інформація|Key information|Основная информация|Galvenā informācija/i,
        }),
      })
      .first();

    // fallback: якщо заголовок не знайдено, шукаємо за ключовими мітками всередині
    const infoSectionAlt = page.locator('section:has(ul li), div:has(ul li)').filter({
      hasText: /(Кузов|Двигун|Пробіг|Коробка|Привід|Дверей|Паливо|Ціна|Цена|Cena)/i,
    }).first();

    const hasInfo = await infoSection.isVisible().catch(() => false);
    const section = hasInfo ? infoSection : infoSectionAlt;
    await expect(section, 'Секцію з характеристиками не знайдено').toBeVisible();

// 6) Збираємо клікабельні посилання
let clickableLinks = section.locator('a[href]:not([href="#"]):not([href^="javascript:"])');
await expect(clickableLinks.first()).toBeAttached(); // стабілізуємо DOM

const infoCount = await clickableLinks.count();
expect(infoCount).toBeGreaterThan(0);

// важливо: щоразу беремо .nth(j) наново і перевіряємо attached перед дією
for (let j = 0; j < infoCount; j++) {
  const ilink = clickableLinks.nth(j);

  await ilink.waitFor({ state: 'attached' });   // <-- ключ
  await ilink.scrollIntoViewIfNeeded().catch(() => {}); // якщо встиг від’єднатись — не падаємо

  const target = (await ilink.getAttribute('target')) || '';
  if (target === '_blank') {
    const [newPage] = await Promise.all([
      context.waitForEvent('page'),
      ilink.click()
    ]);
    await newPage.waitForLoadState('domcontentloaded');
    await expect(newPage).toHaveURL(/https?:\/\/[^/]+\/.*/);
    await newPage.close();
  } else {
    const before = page.url();
    await Promise.all([
      page.waitForLoadState('domcontentloaded'),
      ilink.click()
    ]);
   // збережи URL PDP відразу після відкриття картки (перед роботою із секцією):
// const pdpUrl = page.url();
// const h1 = page.locator('h1'); await h1.waitFor({ state: 'visible', timeout: 10000 });

/** ... усередині циклу по info-лінках ... */

// --- Повернення на PDP після переходу по внутрішньому лінку ---
let tries = 3;

// 1) Повертаємось поки не відновиться ТОЧНИЙ PDP URL (а не просто /uk/...)
while (tries-- > 0 && page.url() !== pdpUrl) {
  await page.goBack();
  await page.waitForLoadState('domcontentloaded');
}

// 2) Переконайся, що ми дійсно на PDP (h1 видимий, не порожній)
await h1.waitFor({ state: 'visible', timeout: 10000 });
await expect(h1).not.toHaveText(/^$/);

// 3) Перестворюємо локатор секції і СКРОЛИМО до неї, інакше вона може бути поза в’юпортом/в акордеоні
const sectionAgain = page
  .locator('section, div')
  .filter({
    has: page.locator('h1,h2,h3,h4', {
      hasText: /Основна інформація|Key information|Основная информация|Galvenā informācija/i,
    }),
  })
  .first();

// fallback: якщо заголовка не знайдено — шукаємо за ключовими мітками
const sectionFallback = page
  .locator('section:has(ul li), div:has(ul li)')
  .filter({ hasText: /(Кузов|Двигун|Пробіг|Коробка|Привід|Паливо|Ціна|Цена|Cena)/i })
  .first();

const section = (await sectionAgain.count()) ? sectionAgain : sectionFallback;

await section.waitFor({ state: 'visible', timeout: 10000 });
await section.scrollIntoViewIfNeeded(); // <-- важливо

// оновлюємо список посилань у секції для наступної ітерації
clickableLinks = section.locator('a[href]:not([href="#"]):not([href^="javascript:"])');


    // 7) Повертаємось на головну /uk/
    let tries = 2;
    while (tries-- > 0 && !/\/uk\/?$/.test(page.url())) {
      await page.goBack();
      await page.waitForLoadState('domcontentloaded');
    }
    await expect(page).toHaveURL(/\/uk\/?$/i);
  }
});
