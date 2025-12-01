  import { test, expect } from '@playwright/test';

  test('Основні блоки сайту automoto.com.lv/ru відображаються', async ({ page }) => {
    await page.goto('https://automoto.com.lv/ru');

    // header / footer
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();

    // шукаємо саме той grid, у якому є картки авто (посилання ведуть у /ru/bu-avto/)
    const catalogGrid = page
      .locator('main div.grid')                            // усі гріди в main
      .filter({ has: page.locator('a[href*="/ru/bu-avto/"]') }) // залишаємо грід з картками
      .first();

    await expect(catalogGrid).toBeVisible();

    // у гріді є хоча б одна картка
    const firstCard = catalogGrid.locator('a[href*="/ru/bu-avto/"]').first();
    await expect(firstCard).toBeVisible();

    // (опц.) відкриваємо першу картку і переконуємось, що PDP завантажилась
    await Promise.all([
      page.waitForURL(/\/ru\/bu-avto\/.*/i),
      firstCard.click(),
    ]);
    await expect(page.locator('h1')).toBeVisible();
  });
