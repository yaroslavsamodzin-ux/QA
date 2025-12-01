import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://automoto.com.lv/lv/auto');
  await page.getByRole('button', { name: 'Kārtošana' }).click();
  await page.getByText('Pēc pievienošanas datuma (vispirms jaunākie)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Kārtošana' }).click();
  await page.getByText('Pēc pievienošanas datuma (vispirms vecākie)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Kārtošana' }).click();
  await page.getByText('Pēc cenas (augošā secībā)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Kārtošana' }).click();
  await page.getByText('Pēc cenas (dilstošā secībā)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Kārtošana' }).click();
  await page.getByText('Pēc nobraukuma (augošā secībā)').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Kārtošana' }).click();
  await page.getByText('Pēc nobraukuma (dilstošā secī').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Kārtošana' }).click();
  await page.getByText('Pēc izgatavošanas gada (augo').click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Kārtošana' }).click();
  await page.getByText('Pēc izgatavošanas gada (dilstošā secībā)').click();
  await page.getByRole('link', { name: 'Logo CARS FROM LATVIA AT ONE' }).click();
});