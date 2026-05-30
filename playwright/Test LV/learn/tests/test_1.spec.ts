import {expect, test} from '@playwright/test';

test ('Basic Navigation', async ({page}) => {
    await page.goto("https://www.google.com");
    await page.waitForTimeout(3000);
    await page.reload();
});

test ("Interacting with Web Elements", async ({ page })=>{
    await page.goto("https://automoto.com.lv/ru/");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);
});

test ("test", async ({ page })=>{
    await page.goto("https://automoto.com.lv/ru/");
    await page.locator('span', {hasText: 'Войти / Регистрация'}).filter({visible : true}).click();
    await page.fill('input[name="email_or_phone"]', '+380682302622');
    await page.fill('input[name="password"]', '123123123');
    await page.getByRole('button', {name: 'Войти'}).click();
    // await page.click('button[type="submit"]').filter({name: 'Войти'}).click();
    await page.waitForTimeout(3000);
});

test ("Go to registration", async ({ page })=>{
    await page.goto("https://automoto.com.lv/ru/");
    await page.getByRole ('button', {name: 'Показать'}).click();
    await page.waitForTimeout(3000);
});

test ("status code is 200", async ({page})=>{
    const resp = await page.request.get("https://www.google.com");
    expect(resp.status()).toBe(200);
});