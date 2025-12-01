import { test, expect, Page } from '@playwright/test';

/* ============ helpers ============ */
async function acceptCookiesIfPresent(page: Page) {
  const btn = page.getByRole('button', {
    name: /прийня|погодж|згод|ок|добре|accept|agree|принять|piekrītu/i,
  });
  try {
    if (await btn.isVisible()) await btn.click({ timeout: 2000 });
  } catch {
    /* ignore */
  }
}

function wireSiteOriginErrorCapture(page: Page) {
  const consoleErrors: string[] = [];
  const pageErrors: string[] = [];

  page.on('console', (msg) => {
    if (msg.type() !== 'error') return;
    const text = msg.text() || '';
    const loc = msg.location()?.url || '';
    const host = (() => { try { return new URL(loc).host; } catch { return ''; } })();

    const isKnownNoise =
      /Attestation check.*(Shared Storage|Protected Audience)/i.test(text) ||
      /chrome-extension:\/\//i.test(loc) ||
      /The resource .* was preloaded using link preload/i.test(text);

    const isOurOrigin = host === '' || /(^|\.)automoto\.ua$/i.test(host);
    if (isOurOrigin && !isKnownNoise) {
      consoleErrors.push(`${loc || '(inline)'} :: ${text}`);
    }
  });

  page.on('pageerror', (err) => pageErrors.push(err?.message || String(err)));

  return { consoleErrors, pageErrors };
}

async function findInfoSection(page: Page) {
  // 1) шукаємо заголовок секції (h2/h3/h4) з очікуваними назвами
  const heading = page
    .locator(':is(h2,h3,h4)')
    .filter({
      hasText: /Основна інформація|Основні характеристики|Основні параметри|Характеристики|Технічні характеристики|Key information|Specifications|Specs|Galvenā informācija|Основная информация/i,
    })
    .first();

  if ((await heading.count()) > 0) {
    // контейнер секції відносно заголовка
    return heading.locator('xpath=ancestor::*[self::section or self::div][1]');
  }

  // 2) фолбек: перший блок, який виглядає як список характеристик
  return page
    .locator(':is(section,div):has(dl), :is(section,div):has(ul li)')
    .first();
}

/* ============ constants ============ */
const START = 'https://automoto.ua/uk/';

test.describe('Automoto.ua (UA) — Smoke', () => {
  test('01. Home loads, UA locale, key sections visible, no site-origin errors', async ({ page }) => {
    const { consoleErrors, pageErrors } = wireSiteOriginErrorCapture(page);

    const resp = await page.goto(START, { waitUntil: 'domcontentloaded' });
    expect(resp?.status(), 'HTTP статус має бути 200').toBe(200);

    await acceptCookiesIfPresent(page);

    await expect(page).toHaveURL(/\/uk\/?$/);
    await expect(page.locator('html')).toHaveAttribute('lang', /^(uk|uk-UA)$/i);

    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();

    await expect(page).toHaveTitle(/.{10,}/);
    const desc = await page.locator('head meta[name="description"]').getAttribute('content');
    expect(desc ?? '', 'meta description має бути непорожнім').toMatch(/.{20,}/);

    expect(consoleErrors, `Очікувалось 0 console errors (site-origin):\n${consoleErrors.join('\n')}`).toHaveLength(0);
    expect(pageErrors, `Очікувалось 0 pageerror:\n${pageErrors.join('\n')}`).toHaveLength(0);
  });

  test('02. From home open first visible car card → PDP shows H1 and info section', async ({ page }) => {
    await page.goto(START, { waitUntil: 'domcontentloaded' });
    await acceptCookiesIfPresent(page);

    // картка оголошення: посилання в main із картинкою та шляхом /uk/
    const cards = page.locator('main a[href^="/uk/"]').filter({ has: page.locator('img') });
    const count = await cards.count();
    expect(count, 'Не знайдено карток на головній').toBeGreaterThan(0);

    await Promise.all([page.waitForURL(/\/uk\/.+/i), cards.first().click()]);
    await expect(page.locator('h1')).toBeVisible();

    const infoSection = await findInfoSection(page);
    await expect(infoSection, 'Не знайшов секцію характеристик (заголовок або список)').toBeVisible();
  });

  test('03. Header/Footer critical links respond with 200 (sample up to 6)', async ({ page, request }) => {
    await page.goto(START, { waitUntil: 'domcontentloaded' });
    await acceptCookiesIfPresent(page);

    // збираємо href з header/footer (внутрішні /uk/)
    const hLinks = await page
      .locator('header a[href^="/uk/"]')
      .evaluateAll((as) => as.map((a) => a.getAttribute('href')).filter(Boolean) as string[]);

    const fLinks = await page
      .locator('footer a[href^="/uk/"]')
      .evaluateAll((as) => as.map((a) => a.getAttribute('href')).filter(Boolean) as string[]);

    const sample = [...new Set([...hLinks, ...fLinks])]
      .filter((href) => typeof href === 'string' && href.startsWith('/uk/') && href.length > 4)
      .slice(0, 6);

    expect(sample.length, 'Немає внутрішніх лінків у header/footer').toBeGreaterThan(0);

    for (const href of sample) {
      const url = new URL(href, START).toString();
      const res = await request.get(url);
      expect(res.status(), `Лінк ${url} має відповідати 200`).toBe(200);
    }
  });

  test('04. Search UI visible (input + submit) and goes to listing', async ({ page }) => {
    await page.goto(START, { waitUntil: 'domcontentloaded' });
    await acceptCookiesIfPresent(page);

    const searchForm = page.locator('main form').first();
    await expect(searchForm).toBeVisible();

    const textInputs = searchForm.locator('input[type="text"], input[role="combobox"]').first();
    if (await textInputs.count()) {
      await textInputs.fill('BMW');
    }

    const searchBtnByName = searchForm.getByRole('button', { name: /Пошук|Знайти|Search/i }).first();
    const btn = (await searchBtnByName.count()) ? searchBtnByName : searchForm.locator('button').first();

    await Promise.all([page.waitForLoadState('domcontentloaded'), btn.click()]);

    await expect(page.locator('main')).toBeVisible();
    const listingCards = page.locator('main a[href^="/uk/"]').filter({ has: page.locator('img') });
    expect(await listingCards.count(), 'Лістинг порожній або не відобразився').toBeGreaterThan(0);
  });
});
