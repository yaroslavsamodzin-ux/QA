import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('https://playwright.dev/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Playwright/);
});

test('First request', async ({ request }) => {

  const response = await request.get('https://automoto.com.lv/ru/catalog/get/models?parent=98')
  const responseObject = await response.json()
  console.log(responseObject)
  expect(responseObject[20]).toEqual('1 Series')
  expect(response.status()).toBe(200)
});

test('First POST request', async ({ request }) => {

  const response = await request.post('https://automoto.com.lv/ru/catalog/get/models?parent=98')
  const responseObject = await response.json()
  console.log(responseObject)
  expect(responseObject[20]).toEqual('1 Series')
  expect(response.status()).toBe(200)
});