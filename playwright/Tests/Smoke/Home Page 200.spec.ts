import { test, expect } from '@playwright/test';

test('Home page loads without errors (RU, only site-origin errors)', async ({ page }) => {
  const consoleErrors: string[] = [];

  // фільтруємо тільки помилки з твого сайту, ігноруємо гугл-рекламу тощо
  page.on('console', msg => {
    if (msg.type() !== 'error') return;
    const text = msg.text() || '';
    const loc = msg.location()?.url || '';
    const host = (() => { try { return new URL(loc).host; } catch { return ''; } })();

    const is3pDomain =
      /google|gdoubleclick|doubleclick|googlesyndication|googletag/i.test(host) ||
      /gstatic|analytics|tagmanager/i.test(host);

    const isKnownNoise =
      /Attestation check.*(Shared Storage|Protected Audience)/i.test(text);

    const isOurOrigin =
      host === '' || /(^|\.)automoto\.com\.lv$/i.test(host);

    if (isOurOrigin && !is3pDomain && !isKnownNoise) {
      consoleErrors.push(`${loc} :: ${text}`);
    }
  });

  // відкриваємо
  const resp = await page.goto('https://automoto.com.lv/ru', { waitUntil: 'networkidle' });
  expect(resp?.status(), 'Статус відповіді має бути 200').toBe(200);

  // основні блоки (у тебе є <header>, <footer>, <main>)
  await expect(page.locator('header')).toBeVisible();
  await expect(page.locator('footer')).toBeVisible();
  await expect(page.locator('main')).toBeVisible();

  // перевіряємо лише "свої" помилки
  expect(consoleErrors, `Очікувалось 0 site-origin помилок, але були:\n${consoleErrors.join('\n')}`)
    .toHaveLength(0);
});
