import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  // Recording...
  await page.goto('https://automoto.com.lv/ru/bu-avto/litva/kaunas/volkswagen/cc-passat-cc/2011/68560069.html');
  await page.getByRole('button', { name: 'Atteikt visus cookies' }).click();
  await page.getByRole('button', { name: 'Пожаловаться' }).click();
  await page.locator('label').filter({ hasText: 'Транспорт продан' }).locator('div').first().click();
  await page.locator('label').filter({ hasText: 'Объявление дублируется' }).locator('div').first().click();
  await page.locator('label').filter({ hasText: 'Фото/описание не совпадают' }).locator('div').first().click();
  await page.locator('label').filter({ hasText: 'Продажа других товаров' }).locator('div').first().click();
  await page.locator('label').filter({ hasText: 'Продавец мошенник' }).locator('div').first().click();
  await page.locator('label').filter({ hasText: 'Другая причина' }).locator('div').first().click();
  await page.getByRole('textbox', { name: 'Введите причину' }).click();
  await page.getByRole('textbox', { name: 'Введите причину' }).fill('Test');
  await page.getByRole('button', { name: 'Продолжить' }).click();
  await page.getByRole('dialog', { name: 'Жалоба' }).getByRole('button').click();
});