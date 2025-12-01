import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://automoto.com.lv/ru');
  await page.getByRole('button', { name: 'Atteikt visus cookies' }).click();
  await page.getByRole('link', { name: 'LV', exact: true }).click();
  await page.getByRole('link', { name: 'RU', exact: true }).click();
  await page.getByRole('link', { name: 'EN', exact: true }).click();
  await page.getByRole('link', { name: 'LV', exact: true }).click();
  await page.getByRole('link', { name: 'EN', exact: true }).click();
  await page.getByRole('link', { name: 'RU', exact: true }).click();
});