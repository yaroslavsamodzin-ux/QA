import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://automoto.com.lv/ru/avto');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#category').selectOption('1');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#fuelType').selectOption('7');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#bodyType2').check();
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#mark').selectOption('53');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#model').selectOption('1760');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#yearFrom').selectOption('1990');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#yearTo').selectOption('2025');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#priceFrom').selectOption('500');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#priceTo').selectOption('100000');
  await page.locator('div:nth-child(8) > .flex.flex-wrap > li:nth-child(12) > .flex > .size-5').click();
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#country').selectOption('25');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#region').selectOption('5');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#city').selectOption('5');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#gearbox').selectOption('1');
  await page.locator('form').filter({ hasText: 'Все Новые Б/У Тип транспорта Выбрать Легковые автомобили Мотоциклы Тип топлива В' }).locator('#drive').selectOption('2');
  await page.getByRole('button', { name: 'Показать', exact: true }).click();
  await expect(page).toHaveTitle(/Automoto/i);
  await page.getByRole('link', { name: 'Logo CARS FROM LATVIA AT ONE' }).click();
});