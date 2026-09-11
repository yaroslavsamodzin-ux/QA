import {expect, test} from '@playwright/test';
import { SELECTOR, SYNONYMS, } from './meta_data';

export function textToContainAnySynonym(actualText: string | null, synonymsArray: string[]) {

    const safeText = (actualText ?? '').toLowerCase();

    const isFound = synonymsArray.some(synonym => safeText.includes(synonym.toLowerCase())
    );

    const errorMessage = `
  Фактично прийшло з сайту: "${actualText}". 
  Очікували хоча б одне зі слів: [${synonymsArray.join(', ')}].`;

    expect(isFound, errorMessage).toBeTruthy();
}

test.only ("Count photos, kpp, color, price, kuzov, seller, palivo, obyemDviguna, km, marka, model", async ({ page })=>{
    const volks = "Volkswagen";
    await page.goto("https://automoto.com.lv/ru/bu-avto/latviya/riga/nissan/leaf/2020");
    const firstkarta = page.locator(SELECTOR.automoto.listing.cart).first();
    const cart = ((await firstkarta.textContent()) ?? '').trim();
    //found marka (first slovo)
    const match = cart.match(/^([^\s,]+)/);
    const marka = match ? match[1] : '';
    //found model (second slovo)
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

    const km = (await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(0).textContent() ?? '').replace(/км/g, "").replace(/\s+/g, "").trim();
    const kmNumber = km.toString().length;
    const kmNumber_2 = km.replace(/000/, "").trim();

    const page1Promise = page.waitForEvent('popup');
    await page.locator(SELECTOR.automoto.kinseva.submitButton).first().click();
    
    //next page
    const page1 = await page1Promise;

    const markaModelInSsLv = await page1.locator(SELECTOR.sslv.kinseva.title).textContent() ?? '';
    expect(markaModelInSsLv).toContain(markaModel);

    const countPhotosInGallerySsLv = (await page1.locator(SELECTOR.sslv.kinseva.counterSpan).count()).toString();
    expect(countPhotosInGallerySsLv).toBe(countPhotos);

    let kuzovSsLv = ((await page1.locator(SELECTOR.sslv.kinseva.kuzov).textContent()) ?? '').toLowerCase().trim();
    if (kuzovSsLv.includes("хетчбэк") || kuzovSsLv.includes("хетчбек")) {
        kuzovSsLv = "хэтчбек";
    };
    expect(kuzovSsLv).toContain(kuzov);

    const kppInSsLv = ((await page1.locator(SELECTOR.sslv.kinseva.kpp).textContent()) ?? '').toLowerCase().replace(/коробка передач/, '').trim();
    expect(kppInSsLv).toContain(kpp);

    const colorInSsLv = ((await page1.locator(SELECTOR.sslv.kinseva.color).textContent()) ?? '').toLowerCase().replace(/цвет/, '').trim();
    expect(colorInSsLv).toContain(color);

    const priceInSsLv = ((await page1.locator(SELECTOR.sslv.kinseva.price).textContent()) ?? '').toLowerCase().replace(/\s+/g, '').trim();
    expect(priceInSsLv).toContain(price);
    
    const palivoInSsLv = ((await page1.locator(SELECTOR.sslv.kinseva.palivo).textContent()) ?? '').trim().toLowerCase();
    textToContainAnySynonym(palivo, SYNONYMS.kinseva.palivo.electo)
    textToContainAnySynonym(palivoInSsLv, SYNONYMS.kinseva.palivo.electo)

    // const obyemDvigunaInSsLv = ((await page1.locator(SELECTOR.sslv.kinseva.obyemDviguna).nth(0).textContent()) ?? '').trim();
    // expect(obyemDvigunaInSsLv).toContain(obyemDviguna);

    // const privodInSsLv = ((await page1.locator(SELECTOR.sslv.kinseva.privod).nth(0).textContent()) ?? '').trim();
    // textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.AWD)
    // textToContainAnySynonym(privodInSsLv, SYNONYMS.kinseva.privod.AWD)

    const kmInSsLv = ((await page1.locator(SELECTOR.sslv.kinseva.km).nth(0).textContent()) ?? '').replace(/km/g, "").replace(/\s+/g, "").trim();
    const kmNumberInSsLv = kmInSsLv.toString();
    expect(kmNumberInSsLv.length).toBe(kmNumber);
    expect(kmNumberInSsLv).toContain(kmNumber_2);
});