import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
await page.goto('https://automoto.com.lv/ru/bu-avto/latviya/riga/bmw/320/2007/68452802.html');
await page.locator('button').filter({ hasText: 'В избранное' }).click();
await page.getByRole('button', { name: 'В избранном' }).click();
await page.getByRole('button', { name: 'В избранное' }).nth(2).click();
await page.getByRole('button', { name: 'В избранное' }).nth(1).click();
});