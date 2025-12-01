import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://automoto.com.lv/lv/auto');
  await page.locator('#category').nth(1).selectOption('1');
  await page.locator('#fuelType').nth(1).selectOption('7');
  await page.locator('#bodyType2').nth(1).check();
  await page.locator('#mark').nth(1).selectOption('53');
  await page.locator('#model').nth(1).selectOption('1760');
  await page.locator('#yearFrom').nth(1).selectOption('1990');
  await page.locator('#yearTo').nth(1).selectOption('2025');
  await page.locator('#priceFrom').nth(1).selectOption('500');
  await page.locator('#priceTo').nth(1).selectOption('100000');
  await page.locator('div:nth-child(8) > .flex.flex-wrap > li:nth-child(12) > .flex > .size-5').click();
  await page.locator('#country').nth(1).selectOption('25');
  await page.locator('#region').nth(1).selectOption('5');
  await page.locator('#city').nth(1).selectOption('5');
  await page.locator('#gearbox').nth(1).selectOption('1');
  await page.locator('#drive').nth(1).selectOption('2');
  await page.getByRole('button', { name: 'Rodyti' }).click();
  await expect(page.locator('main h1, h1').first()).toBeVisible();
  await expect(page).toHaveTitle(/Automoto/i);
  await page.getByRole('link', { name: 'Logo CARS FROM LATVIA AT ONE' }).click();
});