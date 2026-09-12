/**
 * Візуальна регресія: знімає сторінки й порівнює з еталоном.
 *
 * 1) Зняти еталон (до змін / на проді):
 *      set QA_URLS=https://site.com,https://site.com/cart
 *      npx playwright test --config qa-toolkit/visual/playwright.config.js --update-snapshots
 *
 * 2) Порівняти після деплою:
 *      npx playwright test --config qa-toolkit/visual/playwright.config.js
 *
 * Різниця відкривається як HTML-звіт:
 *      npx playwright show-report qa-toolkit/visual/report
 *
 * Змінні оточення:
 *   QA_URLS      список URL через кому (обовʼязково)
 *   QA_WIDTHS    ширини через кому, типово 390,1280
 *   QA_STORAGE   storageState.json для авторизованих сторінок
 *   QA_MASK      CSS-селектори через кому — замалювати (банери, лічильники, дати)
 *   QA_WAIT      пауза після завантаження, мс (типово 1000)
 */
const { test, expect } = require('@playwright/test');

const urls = (process.env.QA_URLS || '')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

const widths = (process.env.QA_WIDTHS || '390,1280')
  .split(',')
  .map((s) => Number(s.trim()))
  .filter(Boolean);

const masks = (process.env.QA_MASK || '')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

const wait = Number(process.env.QA_WAIT || 1000);

const slug = (u) =>
  u.replace(/^https?:\/\//, '').replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').slice(0, 60);

test.describe('Візуальна регресія', () => {
  test.skip(urls.length === 0, 'Не задано QA_URLS — нічого порівнювати.');

  for (const url of urls) {
    for (const width of widths) {
      test(`${slug(url)} @ ${width}px`, async ({ browser }) => {
        const ctx = await browser.newContext({
          viewport: { width, height: width < 640 ? 844 : 900 },
          isMobile: width <= 640,
          hasTouch: width <= 640,
          deviceScaleFactor: 1,
          storageState: process.env.QA_STORAGE || undefined,
          ignoreHTTPSErrors: true,
        });
        const page = await ctx.newPage();
        await page.goto(url, { waitUntil: 'load' });

        // приглушуємо те, що змінюється саме собою і дає хибні дифи
        await page.addStyleTag({
          content: `*,*::before,*::after{animation:none!important;transition:none!important;
                    caret-color:transparent!important}`,
        });
        await page.waitForTimeout(wait);
        await page.evaluate(() => window.scrollTo(0, 0));

        await expect(page).toHaveScreenshot(`${slug(url)}-${width}.png`, {
          fullPage: true,
          mask: masks.map((m) => page.locator(m)),
        });

        await ctx.close();
      });
    }
  }
});
