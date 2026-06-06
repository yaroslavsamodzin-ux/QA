import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://automoto.com.lv/ru/bu-avto/estoniya/tallin/volkswagen/arteon/2020/69038150.html');
  const page1Promise = page.waitForEvent('popup');
  await page.getByRole('button', { name: 'Контакты продавца' }).click();
  const page1 = await page1Promise;
  
});