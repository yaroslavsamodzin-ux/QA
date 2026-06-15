import {expect, test} from '@playwright/test';
import { SELECTOR, TIMEOUTS, SYNONYMS } from './meta_data';

export function textToContainAnySynonym(actualText: string | null, synonymsArray: string[]) {

    const safeText = (actualText ?? '').toLowerCase();

    const isFound = synonymsArray.some(synonym => safeText.includes(synonym.toLowerCase())
    );

    const errorMessage = `
  Фактично прийшло з сайту: "${actualText}". 
  Очікували хоча б одне зі слів: [${synonymsArray.join(', ')}].`;

    expect(isFound, errorMessage).toBeTruthy();
}

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

test.only ("Count photos, kpp, color, price, kuzov, seller, palivo, obyemDviguna, km, marka, model", async ({ page })=>{
    const volks = "Volkswagen";
    await page.goto("https://automoto.com.lv/ru/bu-avto/estoniya/tallin/volkswagen/arteon/2020");
    const firstkarta = page.locator(SELECTOR.automoto.listing.cart).first();
    const cart = ((await firstkarta.textContent()) ?? '').trim();
    expect(cart).toContain(volks);
    //found marka
    const match = cart.match(/^([^\s,]+)/);
    const marka = match ? match[1] : '';
    //found model
    const match_2 = cart.match(/^\S+\s+([^\s,]+)/);
    const model = match_2 ? match_2[1] : '';
    //combinate marka and model
    const markaModel = `${marka} ${model}`;


    await firstkarta.click();

    //on the cart page
    const pole = (await page.locator(SELECTOR.automoto.kinseva.pole).textContent()) ?? '';
    expect(pole).toContain(marka);
    expect(pole).toContain(model);
    
    const countPhotos = ((await page.locator(SELECTOR.automoto.kinseva.countPhotos).textContent()) ?? '').trim();

    const kpp = ((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(2).textContent()) ?? '').trim().toLowerCase();
    
    const color = (await page.locator(SELECTOR.automoto.kinseva.color).textContent() ?? '').toLowerCase().replace(/цвет/, '').trim();
    
    const price = (await page.locator(SELECTOR.automoto.kinseva.price).filter({hasText: '€'}).textContent() ?? '').toLowerCase().replace(/€/, '').replace(/\s+/g, '').trim();
    
    const kuzov = ((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(1).textContent()) ?? '').trim().toLowerCase();
    
    const seller = (await page.locator(SELECTOR.automoto.kinseva.seller).last().textContent() ?? '').trim();
    
    const palivo = (await page.locator(SELECTOR.automoto.kinseva.palivo).textContent() ?? '').replace(/топливо/g, "").trim().toLowerCase();
    
    const obyemDviguna = (await page.locator(SELECTOR.automoto.kinseva.obyemDviguna).textContent() ?? '').replace(/Двигатель/g, "").trim();
    
    const privod = (await page.locator(SELECTOR.automoto.kinseva.privod).textContent() ?? '').trim().toLocaleLowerCase();
    console.log(privod);

    const km = (await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(0).textContent() ?? '').replace(/км/g, "").replace(/\s+/g, "").trim();
    const kmNumber = km.toString().length;
    const kmNumber_2 = km.replace(/000/, "").trim();

    const page1Promise = page.waitForEvent('popup');
    await page.locator(SELECTOR.automoto.kinseva.submitButton).first().click();
    
    //next page
    const page1 = await page1Promise;
    await page1.getByRole('button', { name: 'Я принимаю' }).click();
    // await page1.locator('a.vImages__item').first().click();

    const markaModelInGalleryAutoPlius = await page1.locator(SELECTOR.auto24.kinseva.title).textContent() ?? '';
    expect(markaModelInGalleryAutoPlius).toContain(markaModel);

    const countPhotosInGalleryAutoPlius = await page1.locator(SELECTOR.auto24.kinseva.counterSpan).textContent() ?? '';
    console.log(countPhotos)
    console.log(countPhotosInGalleryAutoPlius)
    expect(countPhotosInGalleryAutoPlius).toContain(countPhotos);
    // await page1.getByRole('button', { name: 'Close gallery' }).click();

    await expect(page1.locator('h1')).toContainText(volks);

    let kuzovAutoPlius = ((await page1.locator(SELECTOR.auto24.kinseva.kuzov).textContent()) ?? '').toLowerCase().trim();
    if (kuzovAutoPlius.includes("хетчбэк") || kuzovAutoPlius.includes("хетчбек")) {
        kuzovAutoPlius = "хэтчбек";
    };
    expect(kuzovAutoPlius).toContain(kuzov);

    const kppInAutoPlius = ((await page1.locator(SELECTOR.auto24.kinseva.kpp).textContent()) ?? '').toLowerCase().replace(/коробка передач/, '').trim();
    expect(kppInAutoPlius).toContain(kpp);

    const colorInAutoPlius = ((await page1.locator(SELECTOR.auto24.kinseva.color).textContent()) ?? '').toLowerCase().replace(/цвет/, '').trim();
    expect(colorInAutoPlius).toContain(color);

    const priceInAutoPlius = ((await page1.locator(SELECTOR.auto24.kinseva.price).textContent()) ?? '').toLowerCase().replace(/eur/, '').replace(/\s+/g, '').trim();
    expect(priceInAutoPlius).toContain(price);

    const sellerInAutoPlius = ((await page1.locator(SELECTOR.auto24.kinseva.seller).textContent()) ?? '').trim();
    expect(sellerInAutoPlius).toContain(seller);
    
    const palivoInAutoPlius = ((await page1.locator(SELECTOR.auto24.kinseva.palivo).textContent()) ?? '').trim().toLowerCase();
    expect(palivoInAutoPlius).toContain(palivo);

    const obyemDvigunaInAutoPlius = ((await page1.locator(SELECTOR.auto24.kinseva.obyemDviguna).nth(0).textContent()) ?? '').trim();
    expect(obyemDvigunaInAutoPlius).toContain(obyemDviguna);

    const privodInAutoPlius = ((await page1.locator(SELECTOR.auto24.kinseva.privod).nth(0).textContent()) ?? '').trim();
    textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.AWD)
    textToContainAnySynonym(privodInAutoPlius, SYNONYMS.kinseva.privod.AWD)

    const kmInAutoPlius = ((await page1.locator(SELECTOR.auto24.kinseva.km).nth(0).textContent()) ?? '').replace(/km/g, "").replace(/\s+/g, "").trim();
    const kmNumberInAutoPlius = kmInAutoPlius.toString();
    expect(kmNumberInAutoPlius.length).toBe(kmNumber);
    expect(kmNumberInAutoPlius).toContain(kmNumber_2);
    

});

test ("check saller", async ({ page })=>{
    await page.goto("https://automoto.com.lv/ru/bu-avto/estoniya/tallin/volkswagen/arteon/2020/68993497.html");
    
    const seller = (await page.locator(SELECTOR.automoto.kinseva.seller).last().textContent() ?? '').trim();
    console.log(seller);
    
    const page1Promise = page.waitForEvent('popup');
    await page.locator(SELECTOR.automoto.kinseva.submitButton).first().click();
    
    //next page
    const page1 = await page1Promise;
    await page1.getByRole('button', { name: 'Я принимаю' }).click();
    
    const sellerInAutoPlius = ((await page.locator(SELECTOR.auto24.kinseva.seller).textContent()) ?? '').trim();
    console.log(sellerInAutoPlius);
    expect(sellerInAutoPlius).toContain(seller);
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