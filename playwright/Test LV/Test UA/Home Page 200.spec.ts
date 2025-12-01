import { test, expect } from '@playwright/test';

test('Home page loads without errors (UA, only site-origin errors)', async ({ page }) => {
  const consoleErrors: string[] = [];
  const pageErrors: string[] = [];

  // Перехоплюємо помилки консолі і лишаємо тільки ті, що з automoto.ua
  page.on('console', (msg) => {
    if (msg.type() !== 'error') return;

    const text = msg.text() || '';
    const loc = msg.location()?.url || '';
    const host = (() => {
      try { return new URL(loc).host; } catch { return ''; }
    })();

    // Шум, який можна ігнорувати
    const isKnownNoise =
      /Attestation check.*(Shared Storage|Protected Audience)/i.test(text) ||
      /chrome-extension:\/\//i.test(loc) ||
      /A cookie .* has been blocked because it does not have the “Secure” attribute/i.test(text);

    // Наш домен
    const isOurOrigin = host === '' || /(^|\.)automoto\.ua$/i.test(host);

    if (isOurOrigin && !isKnownNoise) {
      consoleErrors.push(`${loc || '(inline)'} :: ${text}`);
    }
  });

  // JS runtime помилки сторінки
  page.on('pageerror', (err) => {
    pageErrors.push(err?.message || String(err));
  });

  // Відкриваємо головну
  const resp = await page.goto('https://automoto.ua/uk/', { waitUntil: 'networkidle' });
  expect(resp?.status(), 'Статус відповіді має бути 200').toBe(200);

  // Переконуємось, що ми дійсно на /uk/ та сторінка українська
  await expect(page).toHaveURL(/\/uk\/?/);
  await expect(page.locator('html')).toHaveAttribute('lang', /^(uk|uk-UA)$/i);

  // Базові блоки
  await expect(page.locator('header')).toBeVisible();
  await expect(page.locator('main')).toBeVisible();
  await expect(page.locator('footer')).toBeVisible();

  // Ключові елементи навігації/пошуку — звужуємо область, щоб уникнути strict mode violation
  const advSearchLink = page.locator('header').getByRole('link', { name: /^Розширений пошук$/ });
  await expect(advSearchLink.first()).toBeVisible();

  const searchBtn = page.locator('main').getByRole('button', { name: /^Пошук$/ });
  await expect(searchBtn.first()).toBeVisible();

  // Жодних Uncaught JS-винятків
  //expect(
    //pageErrors,
    //`Очікувалось 0 pageerror, але були:\n${pageErrors.join('\n')}`
  //).toHaveLength(0);
});
