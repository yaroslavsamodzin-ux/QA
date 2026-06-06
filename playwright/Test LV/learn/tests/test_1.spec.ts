import {expect, test} from '@playwright/test';
import { SELECTOR, TIMEOUTS, } from './meta_data';

test ('Basic Navigation', async ({page}) => {
    await page.goto("https://www.google.com");
    await page.waitForTimeout(TIMEOUTS.long);
    await page.reload();
});

test ("Interacting with Web Elements", async ({ page })=>{
    await page.goto("https://automoto.com.lv/ru/");
    await page.click(SELECTOR.automoto.kinseva.submitButton);
    await page.waitForTimeout(TIMEOUTS.medium);
});

test ("for tests found elements", async ({ page })=>{
    await page.goto("https://automoto.com.lv/ru/");
    await page.locator('label:has-text("Новые")').click();
    const h2 = await page.locator('h2', {hasText: 'Популярные на AUTOMOTO.COM.LV'}).textContent();
    console.log(h2?.trim());
    const linkcart = (page.locator('a', {has: page.locator(SELECTOR.automoto.golovna.cart)}).first());
    const marka = (await linkcart.textContent())?.trim();
    console.log(`Found marka: ${marka}`);
    await expect(linkcart).toContainText('Volkswagen');
    await page.locator(SELECTOR.automoto.golovna.cart).first().click();
    await page.waitForTimeout(1000);
    await page.locator(SELECTOR.automoto.kinseva.submitButton).click();
    // await page.locator('button[type="button"]', {hasText: 'Контакты продавца'}).filter({visible:true}).click();
    await page.waitForTimeout(3000);
});

test.only ("Count photos", async ({ page })=>{
    const volks = "Volkswagen";
    await page.goto("https://automoto.com.lv/ru/bu-avto/estoniya/tallin/volkswagen/arteon/2020");
    const firstkarta = page.locator(SELECTOR.automoto.listing.cart).first();
    const marka = (await firstkarta.textContent())?.trim();
    expect(marka).toContain(volks);
    await firstkarta.click();

    //on the cart page
    expect(page.locator('h1')).toContainText(volks);
    const countPhotos = (await page.locator(SELECTOR.automoto.kinseva.countPhotos).textContent()) ?? ''.trim();
    const kpp = ((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(2).textContent()) ?? '').trim().toLowerCase();
    const page1Promise = page.waitForEvent('popup');
    await page.locator(SELECTOR.automoto.kinseva.submitButton).first().click();
    
    //next page
    const page1 = await page1Promise;
    await page1.getByRole('button', { name: 'Я принимаю' }).click();
    await page1.locator('a.vImages__item').first().click();
    const countPhotosInGalleryAutoPlius = await page1.locator('span.lg-counter-all').textContent() ?? '';
    expect(countPhotosInGalleryAutoPlius).toContain(countPhotos);
    await page1.getByRole('button', { name: 'Close gallery' }).click();
    await expect(page1.locator('h1')).toContainText(volks);
    const kppInAutoPlius = ((await page1.locator(SELECTOR.autoplius.kinseva.kpp).textContent()) ?? '').replace(/Коробка передач/, '').trim();
    expect(kppInAutoPlius).toContain(kpp);
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