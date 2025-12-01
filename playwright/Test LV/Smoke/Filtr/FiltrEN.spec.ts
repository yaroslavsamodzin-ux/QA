import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://automoto.com.lv/en/cars');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#category').selectOption('1');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#fuelType').selectOption('7');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#bodyType2').check();
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#mark').selectOption('53');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#model').selectOption('1760');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#yearFrom').selectOption('1990');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#yearTo').selectOption('2025');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#priceFrom').selectOption('500');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#priceTo').selectOption('100000');
  await page.locator('div:nth-child(8) > .flex.flex-wrap > li:nth-child(12) > .flex > .size-5').click();
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#country').selectOption('25');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#region').selectOption('5');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#city').selectOption('5');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#gearbox').selectOption('1');
  await page.locator('form').filter({ hasText: 'All New Used Vehicle type Select Passenger cars Motorcycles Fuel type Select' }).locator('#drive').selectOption('2');
  await page.getByRole('button', { name: 'Show', exact: true }).click();
  await expect(page.locator('main h1, h1').first()).toBeVisible();
  await expect(page).toHaveTitle(/Automoto/i);
  await page.getByRole('link', { name: 'Logo CARS FROM LATVIA AT ONE' }).click();
});
