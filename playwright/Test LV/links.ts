import { test, expect } from '@playwright/test';

test('Перехід по кожному оголошенню в гріді', async ({ page }) => {
  await page.goto('https://automoto.com.lv/ru');

  // шукаємо грід з оголошеннями
  const grid = page
    .locator('main div.grid')
    .filter({ has: page.locator('a[href*="/ru/bu-avto/"]') })
    .first();

  // всі посилання на оголошення в гріді
  const ads = grid.locator('a[href*="/ru/bu-avto/"]');
  const count = await ads.count();
  console.log(`Знайдено ${count} оголошень`);

  // щоб тест не був надто довгим, можна обмежити кількість
  const MAX = Math.min(count, 5);

  for (let i = 0; i < MAX; i++) {
    const ad = ads.nth(i);

    // відкриваємо оголошення
    await Promise.all([
      page.waitForURL(/\/ru\/bu-avto\/.*/i),
      ad.click(),
    ]);

    // перевіряємо, що завантажилась сторінка оголошення (є h1)
    await expect(page.locator('h1')).toBeVisible();

    // повертаємось назад у каталог
    await Promise.all([
      page.waitForURL(/\/ru$/i),
      page.goBack(),
    ]);
  }
});
