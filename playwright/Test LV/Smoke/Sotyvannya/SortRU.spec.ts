import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://automoto.com.lv/ru/avto');
  await page.getByRole('button', { name: 'Сортировка' }).click();
  await page.getByText('По дате добавления (сначала старые)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Сортировка' }).click();
  await page.getByText('По дате добавления (сначала новые)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Сортировка' }).click();
  await page.getByText('По цене (по возрастанию)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Сортировка' }).click();
  await page.getByText('По цене (по убыванию)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Сортировка' }).click();
  await page.getByText('По пробегу (по возрастанию)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Сортировка' }).click();
  await page.getByText('По пробегу (по убыванию)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Сортировка' }).click();
  await page.getByText('По году выпуска (по возрастанию)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Сортировка' }).click();
  await page.getByText('По году выпуска (по убыванию)').click();
  await page.getByRole('link', { name: 'Logo CARS FROM LATVIA AT ONE' }).click();
});