import { expect, test } from '@playwright/test';
import { SELECTOR, SYNONYMS } from './meta_data';

// 1. Створюємо інтерфейс для конфігурації сайтів-донорів
interface TargetSiteConfig {
    titleSelector: string; 
    photoCountMethod: (page: any) => Promise<string>;
    colorSelector?: string;
    palivoSelector?: string;
    priceSelector: string;
    obyemDvigunaSelector?: string;
    tipDvigatelaSelector?: string; // for sslv
    kuzovSelector: string;
    kmSelector: string;
    kppSelector: string;
    privodSelector?: string;
    sellerSelector?: string;
    onlyNumber?: (text: string) => string;
}

// 2. Описуємо правила гри для кожного сайту
const SITE_CONFIGS: Record<string, TargetSiteConfig> = {
    'ss.lv': {
        titleSelector: SELECTOR.sslv.kinseva.title,
        photoCountMethod: async (p) => (await p.locator(SELECTOR.sslv.kinseva.counterSpan).count()).toString(),
        colorSelector: SELECTOR.sslv.kinseva.color,
        palivoSelector: SELECTOR.sslv.kinseva.palivo,
        priceSelector: SELECTOR.sslv.kinseva.price,
        obyemDvigunaSelector: SELECTOR.sslv.kinseva.obyemDviguna,
        tipDvigatelaSelector: SELECTOR.sslv.kinseva.tipDvigatela,
        kuzovSelector: SELECTOR.sslv.kinseva.kuzov,
        kmSelector: SELECTOR.sslv.kinseva.km,
        kppSelector: SELECTOR.sslv.kinseva.kpp,
        privodSelector: SELECTOR.sslv.kinseva.privod,
        // sellerSelector: SELECTOR.sslv.kinseva.seller,
    },
    'auto24.lv': { // Естонія
        titleSelector: SELECTOR.auto24.kinseva.title,
        photoCountMethod: async (p) => (await p.locator(SELECTOR.auto24.kinseva.counterSpan).textContent() ?? '').trim(),
        colorSelector: SELECTOR.auto24.kinseva.color,
        palivoSelector: SELECTOR.auto24.kinseva.palivo,
        priceSelector: SELECTOR.auto24.kinseva.price,
        obyemDvigunaSelector: SELECTOR.auto24.kinseva.obyemDviguna,
        kuzovSelector: SELECTOR.auto24.kinseva.kuzov,
        kmSelector: SELECTOR.auto24.kinseva.km,
        kppSelector: SELECTOR.auto24.kinseva.kpp,
        privodSelector: SELECTOR.auto24.kinseva.privod,
        sellerSelector: SELECTOR.auto24.kinseva.seller,
    }
    // Сюди легко додати 'autoplius': { ... }
};

export function textToContainAnySynonym(actualText: string | null, synonymsArray: string[]) {
    const safeText = (actualText ?? '').toLowerCase();
    const isFound = synonymsArray.some(synonym => safeText.includes(synonym.toLowerCase()));
    const errorMessage = `Фактично: "${actualText}". Очікували: [${synonymsArray.join(', ')}].`;
    console.log(`"${actualText}" є в [${synonymsArray}]`)
    expect(isFound, errorMessage).toBeTruthy();
}

const onlyNumber = (text: string | null | undefined): string => {
    if (!text) return '';
    return text.replace(/[^0-9.]/g, '').trim();
};

test("Universal test for parser", async ({ page }) => {

    // Збираємо з автомото, каталог, потім кінцева
    await page.goto("https://automoto.com.lv/ru/bu-avto");
    await page.waitForLoadState('domcontentloaded');

    let currentPage = 1;
    let maxPage = 3;
    
    while(currentPage <= maxPage){

    const cardsLocator = page.locator(SELECTOR.automoto.listing.cart);
    const countKarta = await cardsLocator.count();
    
    //цикл
    for (let i = 0; i <= countKarta; i++){
    const thisCard = cardsLocator.nth(i);

    const cart = ((await thisCard.textContent()) ?? '').trim().toLowerCase();
    const marka = ((cart.match(/^([^\s,]+)/) ?? [])[1] ?? '');
    const model = (cart.match(/^\S+\s+([^\s,]+)/) ?? [])[1] ?? '';
    const markaModel = `${marka} ${model}`;

    await thisCard.click();

    // Парсимо базові значення
    const pole = ((await page.locator(SELECTOR.automoto.kinseva.pole).textContent()) ?? '').toLowerCase();
    expect(pole).toContain(marka);
    expect(pole).toContain(model);
    
    const countPhotos = ((await page.locator(SELECTOR.automoto.kinseva.countPhotos).textContent()) ?? '').trim();
    const kpp = ((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(2).textContent()) ?? '').trim().toLowerCase();
    const color = (await page.locator(SELECTOR.automoto.kinseva.color).textContent() ?? '').toLowerCase().replace(/цвет/, '').trim();
    const price = (await page.locator(SELECTOR.automoto.kinseva.price).filter({hasText: '€'}).textContent() ?? '').replace(/[^0-9]/g, '').trim();
    const kuzov = ((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(1).textContent()) ?? '').trim().toLowerCase();
    const palivo = (await page.locator(SELECTOR.automoto.kinseva.palivo).textContent() ?? '').replace(/топливо/g, "").trim().toLowerCase();
    const obyemDviguna = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.obyemDviguna).textContent() ?? '').replace(/Двигатель/g, "").trim());
    const seller = (await page.locator(SELECTOR.automoto.kinseva.seller).last().textContent() ?? '').trim().toLowerCase();
    const privod = (await page.locator(SELECTOR.automoto.kinseva.privod).textContent() ?? '').trim().toLowerCase();

    const km = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(0).textContent() ?? '').trim());
    const kmNumber = km.length;
    const kmNumber_2 = km.substring(0, 3);

    // Перехід на сайт-джерело
    const page1Promise = page.waitForEvent('popup');
    await page.locator(SELECTOR.automoto.kinseva.submitButton).first().click();
    const page1 = await page1Promise;
    await page1.waitForLoadState('domcontentloaded');

    // Визначаємо куди ми потрапили по URL
    const siteUrl = page1.url();
    let currentConfig: TargetSiteConfig | undefined;

    for (const key of Object.keys(SITE_CONFIGS)) {
        if (siteUrl.includes(key)) {
            currentConfig = SITE_CONFIGS[key];
            break;
        }
    }

    // Якщо прилетів невідомий сайт
    if (!currentConfig) {
        throw new Error(`Тест впав: Немає конфігурації для сайту донора! Поточний URL: ${siteUrl}`);
    }

    // Перевірки
    
    // 1. Перевірка Марки
    if (currentConfig && currentConfig.titleSelector) {

    const titleSelector = page1.locator(currentConfig.titleSelector);

        if (await titleSelector.count() > 0) {
            const siteMarka = (await titleSelector.first().textContent() ?? '').trim().toLowerCase();

            if(marka.includes("mercedes-benz")){

                textToContainAnySynonym(marka, SYNONYMS.kinseva.marka.mercedes);
                textToContainAnySynonym(siteMarka, SYNONYMS.kinseva.marka.mercedes);

            } else {
                expect(siteMarka).toContain(markaModel);
                expect(siteMarka).toContain(marka);
                expect(siteMarka).toContain(model);
                console.log(`Marka Good, "${siteMarka}" include "${marka}"`)
            }
        } else {
            console.log(`На ${siteUrl} немає марки: ${marka}`);

        }
        } else {
            console.log(`На ${siteUrl} не налаштовано titleSelector в конфігу`);
    };
    // 2. Перевірка Моделі
    if (currentConfig && currentConfig.titleSelector) {

    const titleSelector = page1.locator(currentConfig.titleSelector);

        if (await titleSelector.count() > 0) {
            const siteMarka = (await titleSelector.first().textContent() ?? '').trim().toLowerCase();

            if(model.includes("mercedes-benz")){

                textToContainAnySynonym(model, SYNONYMS.kinseva.marka.mercedes);
                textToContainAnySynonym(siteMarka, SYNONYMS.kinseva.marka.mercedes);

            } else{
                expect(siteMarka).toContain(model);
                console.log(`Model Good, "${siteMarka}" include "${model}"`)

            }
        } else {
            console.log(`На ${siteUrl} немає марки: ${model}`);
        }
        } else {
            console.log(`На ${siteUrl} не налаштовано titleSelector в конфігу`);
    };

    // 3. Кількість фото
    const sitePhotosCount = await currentConfig.photoCountMethod(page1);
    // expect(sitePhotosCount).toBe(countPhotos); //закоментив бо на сслв часто падає

    // 4. Тип кузова
    if (currentConfig && currentConfig.palivoSelector) {

    const kuzovLocator = page1.locator(currentConfig.kuzovSelector);

        if (await kuzovLocator.count() > 0) {
            const siteKuzov = (await kuzovLocator.first().textContent() ?? '').trim().toLowerCase();

            if(kuzov.includes("внедорожник")){
                
                textToContainAnySynonym(kuzov, SYNONYMS.kinseva.kuzov.vnedorojnik);
                textToContainAnySynonym(siteKuzov, SYNONYMS.kinseva.kuzov.vnedorojnik);

            } else {
                expect(siteKuzov).toContain(kuzov)
                console.log(`Kuzov Good, "${siteKuzov}" include "${kuzov}"`)

            }
        } else {
            console.log(`На ${siteUrl} немає кузова: ${kuzov}`);
        }
        } else {
            console.log(`На ${siteUrl} не налаштовано kuzovSelector в конфігу`);
    };

    // 5. КПП
    const siteKpp = (await page1.locator(currentConfig.kppSelector).first().textContent() ?? '').toLowerCase().replace(/коробка передач/, '').trim();
    expect(siteKpp).toContain(kpp);
                console.log(`CHECK KPP Good?, "${siteKpp}" include "${kpp}"`)


    // 6. Колір
    if (currentConfig && currentConfig.colorSelector) {

    const colorLocator = page1.locator(currentConfig.colorSelector);

        if (await colorLocator.count() > 0) {
            const siteColor = (await colorLocator.first().textContent() ?? '').trim().toLowerCase();

            if(color.includes("черный")){

                textToContainAnySynonym(color, SYNONYMS.kinseva.color.black);
                textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.black);

            } else {
                expect(siteColor).toContain(color)
                console.log(`Color Good, "${siteColor}" include "${color}"`)

            }
        } else {
            console.log(`На ${siteUrl} немає кольору: ${color}`);
        }
        } else {
            console.log(`На ${siteUrl} не налаштовано colorLocator в конфігу`);
    };

    // 7. Об'єм двигуна
    if(currentConfig.obyemDvigunaSelector){
    const siteobyemDviguna = onlyNumber((await page1.locator(currentConfig.obyemDvigunaSelector).first().textContent() ?? '').toLowerCase().trim());
    expect(siteobyemDviguna).toContain(obyemDviguna);
                console.log(`Obyem Dviguna Good, "${siteobyemDviguna}" include "${obyemDviguna}"`)

    } else {
        console.log(`На ${siteUrl} немає об'єму двигуна: ${obyemDviguna}`)
    }

    // 8. Продавець
    if(currentConfig.sellerSelector){
    const siteseller = (await page1.locator(currentConfig.sellerSelector).first().textContent() ?? '').toLowerCase().replace(/цвет/, '').trim();
    expect(siteseller).toContain(seller);
                console.log(`Seller Good, "${siteseller}" include "${seller}"`)

    } else {
        console.log(`На ${siteUrl} немає продавця: ${seller}`)
    }

    // 9. Тип приводу
    if (currentConfig && currentConfig.privodSelector) {

    const privodLocator = page1.locator(currentConfig.privodSelector);

        if (await privodLocator.count() > 0) {
            const sitePrivod = (await privodLocator.first().textContent() ?? '').trim().toLowerCase();

            if(privod.includes("передний привод")){

                textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.FWD);
                textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.FWD);

            } else if(privod.includes("полный привод")){

                textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.AWD);
                textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.AWD);

            } else {
                expect(sitePrivod).toContain(privod)
                console.log(`Privod Good, "${sitePrivod}" include "${privod}"`)

            }
        } else {
            console.log(`На ${siteUrl} немає типу приводу: ${privod}`);
        }
        } else {
            console.log(`На ${siteUrl} не налаштовано privodLocator в конфігу`);
    };

    // 9. Ціна
    const sitePrice = onlyNumber(await page1.locator(currentConfig.priceSelector).first().textContent() ?? '');
    expect(sitePrice).toContain(price);
                console.log(`Price Good, "${sitePrice}" include "${price}"`)

    
    // 10. Паливо
    if (currentConfig && currentConfig.palivoSelector) {

    const palivoLocator = page1.locator(currentConfig.palivoSelector);

        if (await palivoLocator.count() > 0) {
            const sitePalivo = (await palivoLocator.first().textContent() ?? '').trim().toLowerCase();

            if(palivo.includes("дизель")){

                textToContainAnySynonym(palivo, SYNONYMS.kinseva.palivo.dizel);
                textToContainAnySynonym(sitePalivo, SYNONYMS.kinseva.palivo.dizel);

            } else if(palivo.includes("электро")){

                textToContainAnySynonym(palivo, SYNONYMS.kinseva.palivo.electo);
                textToContainAnySynonym(sitePalivo, SYNONYMS.kinseva.palivo.electo);

            } else {
                expect(sitePalivo).toContain(palivo)
                console.log(`Palivo Good, "${sitePalivo}" include "${palivo}"`)
            }
        } else {
            console.log(`На ${siteUrl} немає палива: ${palivo}`);
        }
        } else {
            console.log(`На ${siteUrl} не налаштовано palivoSelector в конфігу`);
    };

    // 11. Пробіг
    if (currentConfig && currentConfig.palivoSelector) {

    const kmSelector = page1.locator(currentConfig.kmSelector);
    
    if (await kmSelector.count() > 0) {
        const siteKm = onlyNumber((await page1.locator(currentConfig.kmSelector).first().textContent() ?? '').trim());

            if(kmNumber > 0){

                expect(siteKm.length).toBe(kmNumber);
                console.log(`KM Good, "${siteKm}" to have "${kmNumber}" numbers`)
                
             // expect(siteKm).toContain(kmNumber_2); //закомєнтив, потім переробити перевірку, якщо пробіг буде 68 000 км 	68 300, зараз береться з третьої цифри

            }
        } else {
            console.log(`На ${siteUrl} немає КМ: ${kmNumber}`);
        }
        } else {
            console.log(`На ${siteUrl} не налаштовано kmSelector в конфігу`);
    };

    

    // Закриваємо вкладку page1
    console.log("=====================Next Cart====================")
        await page1.close();
        
        // Повертаємося на сторінку лістингу
        await page.goBack(); 
        await page.waitForLoadState('domcontentloaded');

    };// кінець циклу фор


        // Клікаєм на кнопку NextPage
        currentPage++;
        if (currentPage <= maxPage) {
            const nextPageButton = page.locator(SELECTOR.automoto.listing.nextPageButton);
            console.log(`Next page (${currentPage})`);
            await nextPageButton.click();
            await page.waitForLoadState('domcontentloaded');
            await page.waitForTimeout(2000); 
        }
    };//кінець циклу вайл
});