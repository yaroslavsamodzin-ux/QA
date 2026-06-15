import { expect, test } from '@playwright/test';
import { SELECTOR, SYNONYMS } from './meta_data';

// 1. Створюємо інтерфейс для конфігурації сайтів-донорів
interface TargetSiteConfig {
    titleSelector: string; 
    photoCountMethod: (page: any) => Promise<string>;
    colorSelector: string;
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
        titleSelector: SELECTOR.auto24.kinseva.title, // приклад, підставте свої константи з SELECTOR
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
    expect(isFound, errorMessage).toBeTruthy();
}

const onlyNumber = (text: string | null | undefined): string => {
    if (!text) return '';
    return text.replace(/[^0-9.]/g, '').trim();
};

test("Universal test for parser", async ({ page }) => {
    
    await page.goto("https://automoto.com.lv/ru/bu-avto");
    
    // 1. Отримуємо локатор для ВСІХ карток на сторінці
    const allCardsLocator = page.locator(SELECTOR.automoto.listing.cart);
    const cardsCount = await allCardsLocator.count();
    
    console.log(`Знайдено ${cardsCount} оголошень для тестування.`);

    // 2. Запускаємо цикл по кожній картці
    for (let i = 0; i < cardsCount; i++) {
        console.log(`--- Старт тесту оголошення №${i + 1} з ${cardsCount} ---`);
        
        // Беремо конкретну картку за її індексом
        const currentCard = allCardsLocator.nth(i);
        
        // Збираємо дані з картки лістингу
        const cart = ((await currentCard.textContent()) ?? '').trim().toLowerCase();
        const marka = (cart.match(/^([^\s,]+)/) ?? [])[1] ?? '';
        const model = (cart.match(/^\S+\s+([^\s,]+)/) ?? [])[1] ?? '';
        const markaModel = `${marka} ${model}`;

        // Клікаємо на картку, щоб відкрилася кінцева сторінка automoto
        await currentCard.click();

        // Парсимо базові значення на сторінці автомобіля (automoto)
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

        // Перехід на сайт-джерело (відкриваємо поп-ап)
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

        // Якщо прилетів невідомий сайт, ми не валимо весь цикл, а просто логуємо або кидаємо помилку
        if (!currentConfig) {
            await page1.close(); // закриваємо вкладку перед виходом
            throw new Error(`Тест впав: Немає конфігурації для сайту донора! Поточний URL: ${siteUrl}`);
        }

        // --- ТУТ ІДУТЬ ВАШІ ПЕРЕВІРКИ (Блоки expect 1-11, які ви написали) ---
        // (Залиште ваші блоки перевірок без змін)
        
        // 1. Перевірка Марки Моделі
            if (currentConfig.titleSelector){
                const siteTitle = (await page1.locator(currentConfig.titleSelector).first().textContent() ?? '').toLowerCase();
                expect(siteTitle).toContain(markaModel);
            } else {
                console.log(`На  не знайшли марку: ${markaModel}`)
            };
            // 2. Кількість фото
            const sitePhotosCount = await currentConfig.photoCountMethod(page1);
            expect(sitePhotosCount).toBe(countPhotos);
        
            // 3. Тип кузова
            let siteKuzov = (await page1.locator(currentConfig.kuzovSelector).first().textContent() ?? '').toLowerCase().trim();
            if (siteKuzov.includes("хетчбэк") || siteKuzov.includes("хетчбек")) {
                siteKuzov = "хэтчбек";
            }
            expect(siteKuzov).toContain(kuzov);
        
            // 4. КПП
            const siteKpp = (await page1.locator(currentConfig.kppSelector).first().textContent() ?? '').toLowerCase().replace(/коробка передач/, '').trim();
            expect(siteKpp).toContain(kpp);
        
            // 5. Колір
            const siteColor = (await page1.locator(currentConfig.colorSelector).first().textContent() ?? '').toLowerCase().replace(/цвет/, '').trim();
            expect(siteColor).toContain(color);
        
            // 6. Об'єм двигуна
            if(currentConfig.obyemDvigunaSelector){
            const siteobyemDviguna = onlyNumber((await page1.locator(currentConfig.obyemDvigunaSelector).first().textContent() ?? '').toLowerCase().trim());
            expect(siteobyemDviguna).toContain(obyemDviguna);
            } else {
                console.log(`На ${siteUrl} немає об'єму двигуна: ${obyemDviguna}`)
            }
        
            // 7. Продавець
            if(currentConfig.sellerSelector){
            const siteseller = (await page1.locator(currentConfig.sellerSelector).first().textContent() ?? '').toLowerCase().replace(/цвет/, '').trim();
            expect(siteseller).toContain(seller);
            } else {
                console.log(`На ${siteUrl} немає продавця: ${seller}`)
            }
        
            // 8. Тип приводу
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
        
                    }
                } else {
                    console.log(`На ${siteUrl} немає палива: ${palivo}`);
                }
                } else {
                    console.log(`На ${siteUrl} не налаштовано palivoSelector в конфігу`);
            };
        
            // 11. Пробіг
            const siteKm = onlyNumber((await page1.locator(currentConfig.kmSelector).first().textContent() ?? '').trim());
            expect(siteKm.length).toBe(kmNumber);
            expect(siteKm).toContain(kmNumber_2);
        
        // === ВАЖЛИВИЙ КРОК НАПРИКІНЦІ ЦИКЛУ ===
        // Закриваємо вкладку сайту-джерела (page1)
        await page1.close();
        
        // Повертаємося назад на сторінку лістингу на головній вкладці (page), щоб взяти наступну картку
        await page.goBack(); 
        await page.waitForLoadState('domcontentloaded');
    }
});