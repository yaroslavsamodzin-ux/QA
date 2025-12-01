import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://automoto.ua/uk/');
  await page.getByRole('link', { name: 'RU' }).click();
  await page.getByRole('link', { name: 'UA', exact: true }).click();
  await page.getByText('МаркаRemove item').click();
  await page.getByRole('option', { name: 'Audi' }).click();
  await page.getByText('МодельRemove item').click();
  await page.getByRole('option', { name: 'A6', exact: true }).click();
  await page.locator('select[name="state"]').selectOption('1');
  await page.getByPlaceholder('Ціна від $').click();
  await page.getByPlaceholder('Ціна від $').fill('100');
  await page.getByPlaceholder('Ціна до $').click();
  await page.getByPlaceholder('Ціна до $').fill('100000');
  await page.locator('select[name="year[from]"]').selectOption('1930');
  await page.locator('select[name="year[to]"]').selectOption('2026');
  await page.getByRole('button', { name: 'Пошук' }).click();
  await page.getByRole('link', { name: 'automoto.ua ВСІ АВТО ЗІ 100' }).click();
});