import { expect, test } from '@playwright/test';
import { SELECTOR, SYNONYMS } from './meta_data';

// 1. Створюємо інтерфейс для конфігурації сайтів-донорів
interface TargetSiteConfig {
    titleSelector: string; 
    photoCountMethod: (page: any) => Promise<string>;
    yearMethod?: (page: any, selector: string) => Promise<string>;
    colorSelector?: string;
    palivoSelector?: string;
    priceSelector: string;
    priceSelector_2?: string; //for auto24
    obyemDvigunaSelector?: string;
    tipDvigatelaSelector?: string; // for sslv
    kuzovSelector: string;
    kmSelector: string;
    kppSelector: string;
    privodSelector?: string;
    sellerSelector?: string;
    registrationSelector?: string;
    soldSelector?: string;
    onlyNumber?: (text: string) => string;
    bigPhotoSelector?: string
    yearSelector?: string
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
        // registrationSelector: SELECTOR.sslv.kinseva.registration,
        yearSelector: SELECTOR.sslv.kinseva.year,
        // sellerSelector: SELECTOR.sslv.kinseva.seller,
    },
    'auto24.lv': {
        titleSelector: SELECTOR.auto24.kinseva.title,
        photoCountMethod: async (p) => (await p.locator(SELECTOR.auto24.kinseva.counterSpan).textContent() ?? '').trim(),
        colorSelector: SELECTOR.auto24.kinseva.color,
        palivoSelector: SELECTOR.auto24.kinseva.palivo,
        priceSelector: SELECTOR.auto24.kinseva.price,
        priceSelector_2: SELECTOR.auto24.kinseva.price_2,
        obyemDvigunaSelector: SELECTOR.auto24.kinseva.obyemDviguna,
        kuzovSelector: SELECTOR.auto24.kinseva.kuzov,
        kmSelector: SELECTOR.auto24.kinseva.km,
        kppSelector: SELECTOR.auto24.kinseva.kpp,
        privodSelector: SELECTOR.auto24.kinseva.privod,
        sellerSelector: SELECTOR.auto24.kinseva.seller,
        registrationSelector: SELECTOR.auto24.kinseva.registration,
        soldSelector: SELECTOR.auto24.kinseva.sold,
    },
    'autogidas': {
        titleSelector: SELECTOR.autogidas.kinseva.title,

        photoCountMethod: async (p) => {
        const rawText = (await p.locator('#photoCount').first().textContent()) ?? ''; 
        const match = rawText.match(/\/(\d+)/); 
        
        if (match) {
            // Перетворюємо знайдену кількість у число
            const totalPhotos = parseInt(match[1], 10);
            
            // Віднімаємо 1 (якщо фото взагалі є) і повертаємо як рядок
            return totalPhotos > 0 ? (totalPhotos - 1).toString() : '0';
        }
        
        return '0'; 
        },

        yearMethod: async (p, selector) => {
        const rawText = await p.locator(selector).textContent() ?? ''; 
        const match = rawText.match(/\d{4}/); 
        return match ? match[0] : ''; 
        },

        colorSelector: SELECTOR.autogidas.kinseva.color,
        palivoSelector: SELECTOR.autogidas.kinseva.palivo,
        priceSelector: SELECTOR.autogidas.kinseva.price,
        // priceSelector_2: SELECTOR.autogidas.kinseva.price_2,
        obyemDvigunaSelector: SELECTOR.autogidas.kinseva.obyemDviguna,
        kuzovSelector: SELECTOR.autogidas.kinseva.kuzov,
        kmSelector: SELECTOR.autogidas.kinseva.km,
        kppSelector: SELECTOR.autogidas.kinseva.kpp,
        privodSelector: SELECTOR.autogidas.kinseva.privod,
        sellerSelector: SELECTOR.autogidas.kinseva.seller,
        registrationSelector: SELECTOR.autogidas.kinseva.registration,
        soldSelector: SELECTOR.autogidas.kinseva.sold,
        bigPhotoSelector: SELECTOR.autogidas.kinseva.bigPhoto,
        yearSelector: SELECTOR.autogidas.kinseva.year,
    },
    'autoplius': {
        titleSelector: SELECTOR.autoplius.kinseva.title,

        photoCountMethod: async (p) => {
        const counterLocator = p.locator('span.announcement-gallery-carousel__counter').first();
    
            // Чекаємо, поки лічильник фізично з'явиться на екрані після кліку
            await counterLocator.waitFor({ state: 'attached', timeout: 5000 });

            const rawText = await counterLocator.textContent() ?? ''; 
            const match = rawText.match(/(\d+)\s*$/); 
    
            return match ? match[1] : '0';
        },

        colorSelector: SELECTOR.autoplius.kinseva.color,
        palivoSelector: SELECTOR.autoplius.kinseva.palivo,
        priceSelector: SELECTOR.autoplius.kinseva.price,
        obyemDvigunaSelector: SELECTOR.autoplius.kinseva.obyemDviguna,
        kuzovSelector: SELECTOR.autoplius.kinseva.kuzov,
        kmSelector: SELECTOR.autoplius.kinseva.km,
        kppSelector: SELECTOR.autoplius.kinseva.kpp,
        privodSelector: SELECTOR.autoplius.kinseva.privod,
        sellerSelector: SELECTOR.autoplius.kinseva.seller,
        registrationSelector: SELECTOR.autoplius.kinseva.registration,
        soldSelector: SELECTOR.autoplius.kinseva.sold,
        yearSelector: SELECTOR.autoplius.kinseva.year,

    },
};

export function textToContainAnySynonym(actualText: string | null, synonymsArray: string[]) {
    const safeText = (actualText ?? '').toLowerCase();
    const isFound = synonymsArray.some(synonym => safeText.includes(synonym.toLowerCase()));
    const errorMessage = `Фактично: "${actualText}". Очікували: [${synonymsArray.join(', ')}].`;
    console.log(`GOOD: "${actualText}" є в [${synonymsArray}]`)
    expect(isFound, errorMessage).toBeTruthy();
}

export function textToNotContainAnySynonym(actualText: string | null, synonymsArray: string[]) {
    const safeText = (actualText ?? '').toLowerCase();
    const isFound = synonymsArray.some(synonym => safeText.includes(synonym.toLowerCase()));
    const errorMessage = `Фактично: "${actualText}". Очікували що не буде: [${synonymsArray.join(', ')}].`;
    console.log(`ERROR: SOLD Оголошення Продане`)
    expect(isFound, errorMessage).toBeFalsy();
}

const onlyNumber = (text: string | null | undefined): string => {
    if (!text) return '';
    return text.replace(/[^0-9.]/g, '').trim();
};

test("Universal test for parser", async ({ page }) => {

    // Збираємо з автомото, каталог, потім кінцева
    await page.goto("https://automoto.com.lv/ru/bu-avto/litva/vilnyus/audi/a4/2019");
    await page.waitForLoadState('domcontentloaded');

    let currentPage = 1;
    let maxPage = 3;
    
    while (currentPage <= maxPage) {

    const cardsLocator = page.locator(SELECTOR.automoto.listing.cart);
    const countKarta = await cardsLocator.count();

    //цикл
    for (let i = 0; i <= countKarta; i++) {
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
        const price = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.price).filter({hasText: '€'}).textContent() ?? '').trim());
        const kuzov = ((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(1).textContent()) ?? '').trim().toLowerCase();
        const palivo = (await page.locator(SELECTOR.automoto.kinseva.palivo).textContent() ?? '').replace(/топливо/g, "").trim().toLowerCase();
        const obyemDviguna = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.obyemDviguna).textContent() ?? '').replace(/Двигатель/g, "").trim());
        const seller = (await page.locator(SELECTOR.automoto.kinseva.seller).last().textContent() ?? '').trim().toLowerCase();
        const privod = (await page.locator(SELECTOR.automoto.kinseva.privod).textContent() ?? '').trim().toLowerCase();

        const km = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(0).textContent() ?? '').trim());
        const kmNumber = km.length;
        const kmNumber_2 = km.substring(0, 3);
        
        const registration = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).last().textContent() ?? '').trim());

        const yearRaw = (await page.locator(SELECTOR.automoto.kinseva.pole).last().textContent() ?? '').trim();
        const automotoYearMatch = yearRaw.match(/\d{4}/);
        const year = automotoYearMatch ? automotoYearMatch[0] : '';

        console.log(registration)
        // зберігаю урл для логів
        const automotoUrl = page.url();
        console.log(`URL: ${automotoUrl}`);


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
        // SOLD?
        if (currentConfig && currentConfig.soldSelector) {

            const soldSelector = page1.locator(currentConfig.soldSelector);

            if (await soldSelector.count() > 0) {

                const sold = (await soldSelector.first().textContent() ?? '').trim().toLowerCase();

                textToNotContainAnySynonym(sold, SYNONYMS.kinseva.sold);
                // expect(sold, `SOLD: ОГОЛОШЕННЯ ПРОДАНЕ`).not.toContain("продано");

            } else {
                console.log(`GOOD: Оголошення актуальне`);
            }
        };

        // 1. Перевірка Марки
        if (currentConfig && currentConfig.titleSelector) {

            const titleSelector = page1.locator(currentConfig.titleSelector);

            if (await titleSelector.count() > 0) {
                const siteMarka = (await titleSelector.first().textContent() ?? '').replace(/\s+/g, " ").trim().toLowerCase();

                if (marka.includes("mercedes-benz")) {

                    textToContainAnySynonym(marka, SYNONYMS.kinseva.marka.mercedes);
                    textToContainAnySynonym(siteMarka, SYNONYMS.kinseva.marka.mercedes);

                } else {
                    expect(siteMarka).toContain(markaModel);
                    expect(siteMarka).toContain(marka);
                    expect(siteMarka).toContain(model);
                    console.log(`GOOD: Marka, "${siteMarka}" include "${marka}"`)
                }
            } else {
                console.log(`FAIL: На ${siteUrl} немає марки: "${marka}"`);

            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано titleSelector в конфігу`);
        };
        // 2. Перевірка Моделі
        if (currentConfig && currentConfig.titleSelector) {

            const titleSelector = page1.locator(currentConfig.titleSelector);

            if (await titleSelector.count() > 0) {
                const siteMarka = (await titleSelector.first().textContent() ?? '').replace(/\s+/g, " ").trim().toLowerCase();

                if (model.includes("mercedes-benz")) {

                    textToContainAnySynonym(model, SYNONYMS.kinseva.marka.mercedes);
                    textToContainAnySynonym(siteMarka, SYNONYMS.kinseva.marka.mercedes);

                } else {
                    expect(siteMarka).toContain(model);
                    console.log(`GOOD: Model, "${siteMarka}" include "${model}"`)

                }
            } else {
                console.log(`FAIL: На ${siteUrl} немає марки: "${model}"`);
            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано titleSelector в конфігу`);
        };

        // 3. Рік
        if (currentConfig && currentConfig.yearSelector) {

            const yearSelector = page1.locator(currentConfig.yearSelector);

            if (await yearSelector.count() > 0) {
                const siteYear = (await yearSelector.first().textContent() ?? '').replace(/\s+/g, " ").trim().toLowerCase();
                expect(siteYear).toContain(year); 
                console.log(`GOOD: Year, "${siteYear}" include "${year}"`);
            } else {
                console.log(`FAIL: На ${siteUrl} немає року: "${year}"`);
            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано yearSelector в конфігу`);
        };

        // 4. Кількість фото
        if (currentConfig.bigPhotoSelector){
            const photoElement = page1.locator(currentConfig.bigPhotoSelector)

            await photoElement.click();
        }
        const sitePhotosCount = await currentConfig.photoCountMethod(page1);
        expect(sitePhotosCount).toBe(countPhotos); //закоментив бо часто падає
        console.log(`GOOD: CountPhoto, "${sitePhotosCount}" include "${countPhotos}"`);


        // 5. Тип кузова
        if (currentConfig && currentConfig.palivoSelector) {

            const kuzovLocator = page1.locator(currentConfig.kuzovSelector);

            if (await kuzovLocator.count() > 0) {
                const siteKuzov = (await kuzovLocator.first().textContent() ?? '').trim().toLowerCase();

                if (kuzov.includes("внедорожник")) {

                    textToContainAnySynonym(kuzov, SYNONYMS.kinseva.kuzov.vnedorojnik);
                    textToContainAnySynonym(siteKuzov, SYNONYMS.kinseva.kuzov.vnedorojnik);

                } else if (kuzov.includes("хэтчбек")) {

                    textToContainAnySynonym(kuzov, SYNONYMS.kinseva.kuzov.hetchbeck);
                    textToContainAnySynonym(siteKuzov, SYNONYMS.kinseva.kuzov.hetchbeck);

                } else {
                    expect(siteKuzov).toContain(kuzov)
                    console.log(`GOOD: Kuzov, "${siteKuzov}" include "${kuzov}"`)

                }
            } else {
                console.log(`FAIL: На ${siteUrl} немає кузова: "${kuzov}"`);
            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано kuzovSelector в конфігу`);
        };

        // 6. КПП
        if (currentConfig && currentConfig.kppSelector) {

            const kppLocator = page1.locator(currentConfig.kppSelector);

            if (await kppLocator.count() > 0) {
                const siteKpp = (await kppLocator.first().textContent() ?? '').trim().toLowerCase();

                if (kpp.includes("ручная")) {

                    textToContainAnySynonym(kpp, SYNONYMS.kinseva.kpp.manual);
                    textToContainAnySynonym(siteKpp, SYNONYMS.kinseva.kpp.manual);

                } else {
                    expect(siteKpp).toContain(kpp)
                    console.log(`GOOD: KPP, "${siteKpp}" include "${kpp}"`)

                }
            } else {
                console.log(`FAIL: На ${siteUrl} немає кпп: "${kpp}"`);
            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано kppLocator в конфігу`);
        };

        // 7. Колір
        if (currentConfig && currentConfig.colorSelector) {

            const colorLocator = page1.locator(currentConfig.colorSelector);

            if (await colorLocator.count() > 0) {
                const siteColor = (await colorLocator.first().textContent() ?? '').trim().toLowerCase();

                if (color.includes("черный")) {

                    textToContainAnySynonym(color, SYNONYMS.kinseva.color.black);
                    textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.black);

                } else if(color.includes("зеленый")) {

                    textToContainAnySynonym(color, SYNONYMS.kinseva.color.green);
                    textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.green);

                } else if(color.includes("серый")) {

                    textToContainAnySynonym(color, SYNONYMS.kinseva.color.gray);
                    textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.gray);

                } else {
                    expect(siteColor).toContain(color)
                    console.log(`GOOD: Color, "${siteColor}" include "${color}"`)

                }
            } else {
                console.log(`FAIL: На ${siteUrl} немає кольору: "${color}"`);
            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано colorLocator в конфігу`);
        };

        // 8. Об'єм двигуна
        if (currentConfig && currentConfig.obyemDvigunaSelector) {

            const colorLocator = page1.locator(currentConfig.obyemDvigunaSelector);
            
            if (await colorLocator.count() > 0) {
                const siteobyemDviguna = onlyNumber((await page1.locator(currentConfig.obyemDvigunaSelector).first().textContent() ?? '').toLowerCase().trim());
                expect(siteobyemDviguna).toContain(obyemDviguna);
                console.log(`GOOD: Obyem, "${siteobyemDviguna}" include "${obyemDviguna}"`)

            } else {
                console.log(`FAIL: На ${siteUrl} немає об'єму двигуна: ${obyemDviguna}`);
            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано obyemDvigunaLocator в конфігу`);
        };
    
        // 9. Продавець
        if (currentConfig.sellerSelector) {
            const siteseller = (await page1.locator(currentConfig.sellerSelector).first().textContent() ?? '').toLowerCase().trim();
            expect(siteseller).toContain(seller);
            console.log(`GOOD: Seller, "${siteseller}" include "${seller}"`)

        } else {
            console.log(`FAIL: На ${siteUrl} немає продавця: "${seller}"`)
        }

        // 10. Тип приводу
        if (currentConfig && currentConfig.privodSelector) {

            const privodLocator = page1.locator(currentConfig.privodSelector);

            if (await privodLocator.count() > 0) {
                const sitePrivod = (await privodLocator.first().textContent() ?? '').trim().toLowerCase();

                if (privod.includes("передний привод")) {

                    textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.FWD);
                    textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.FWD);

                } else if (privod.includes("полный привод")) {

                    textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.AWD);
                    textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.AWD);

                } else {
                    expect(sitePrivod).toContain(privod)
                    console.log(`GOOD: Privod, "${sitePrivod}" include "${privod}"`)

                }
            } else {
                console.log(`FAIL: На ${siteUrl} немає типу приводу: "${privod}"`);
            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано privodLocator в конфігу`);
        };

        // 11. Цена
        const priceSelector = page1.locator(currentConfig.priceSelector);
        if (await priceSelector.count() > 0) {
            const rawPriceText = await page1.locator(currentConfig.priceSelector).first().textContent() ?? '';
            const firstNumbersMatch = rawPriceText.trim().match(/^\d+[\s\u00A0]?\d+/); 
            const sitePrice = onlyNumber(firstNumbersMatch ? firstNumbersMatch[0] : '');
            // const sitePrice = onlyNumber(await page1.locator(currentConfig.priceSelector).first().innerText() ?? '');

            if (sitePrice == price) {

                expect(sitePrice).toContain(price);      
                console.log(`GOOD: First Price, "${sitePrice}" include "${price}"`)

            } else {

                expect(sitePrice).toContain(price);
                console.error(`FAIL: Біда з основною ціною`)
                console.log(sitePrice)
                console.log(price)
            };
            
        } else if (currentConfig && currentConfig.priceSelector_2) {
            
            const priceSelector_2 = page1.locator(currentConfig.priceSelector_2);
            
            if (await priceSelector_2.count() > 0){
                
                const sitePrice_2 = onlyNumber(await page1.locator(currentConfig.priceSelector_2).textContent() ?? '');
                expect(sitePrice_2).toContain(price)
                console.log(`GOOD: Action Price, "${sitePrice_2}" include "${price}"`)
                
            } else {
                
                console.error(`FAIL: Біда з ціною`)
                    
                }

            } else{

                console.error(`FAIL: На ${siteUrl} немає ціни: "${price}"`);

            };

        // 12. Паливо
        if (currentConfig && currentConfig.palivoSelector) {

            const palivoLocator = page1.locator(currentConfig.palivoSelector);

            if (await palivoLocator.count() > 0) {
                const sitePalivo = (await palivoLocator.first().textContent() ?? '').trim().toLowerCase();

                if (palivo.includes("дизель")) {

                    textToContainAnySynonym(palivo, SYNONYMS.kinseva.palivo.dizel);
                    textToContainAnySynonym(sitePalivo, SYNONYMS.kinseva.palivo.dizel);

                } else if (palivo.includes("электро")) {

                    textToContainAnySynonym(palivo, SYNONYMS.kinseva.palivo.electo);
                    textToContainAnySynonym(sitePalivo, SYNONYMS.kinseva.palivo.electo);

                }else if (palivo.includes("газ/бензин")) {

                    textToContainAnySynonym(palivo, SYNONYMS.kinseva.palivo.gaz_benz);
                    textToContainAnySynonym(sitePalivo, SYNONYMS.kinseva.palivo.gaz_benz);

                } else {
                    expect(sitePalivo).toContain(palivo)
                    console.log(`GOOD: Palivo, "${sitePalivo}" include "${palivo}"`)
                }
            } else {
                console.log(`FAIL: На ${siteUrl} немає палива: "${palivo}"`);
            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано palivoSelector в конфігу`);
        };

        // 13. Пробіг
        if (currentConfig && currentConfig.palivoSelector) {

            const kmSelector = page1.locator(currentConfig.kmSelector);

            if (await kmSelector.count() > 0) {
                const siteKm = onlyNumber((await page1.locator(currentConfig.kmSelector).first().textContent() ?? '').trim());

                if (kmNumber > 0) {

                    expect(siteKm.length).toBe(kmNumber);
                    console.log(`GOOD: KM, "${siteKm}" to have "${kmNumber}" numbers`)

                    // expect(siteKm).toContain(kmNumber_2); //закомєнтив, потім переробити перевірку, якщо пробіг буде 68 000 км 	68 300, зараз береться з третьої цифри

                }
            } else {
                console.log(`FAIL: На ${siteUrl} немає КМ: "${kmNumber}"`);
            }
        } else {
            console.log(`FAIL: На ${siteUrl} не налаштовано kmSelector в конфігу`);
        };

        // // 14. Перша реєстрація
        // if (currentConfig && currentConfig.palivoSelector) {

        //     const kmSelector = page1.locator(currentConfig.kmSelector);

        //     if (await kmSelector.count() > 0) {
        //         const siteKm = onlyNumber((await page1.locator(currentConfig.kmSelector).first().textContent() ?? '').trim());

        //         if (kmNumber > 0) {

        //             expect(siteKm.length).toBe(kmNumber);
        //             console.log(`GOOD: KM, "${siteKm}" to have "${kmNumber}" numbers`)

        //             // expect(siteKm).toContain(kmNumber_2); //закомєнтив, потім переробити перевірку, якщо пробіг буде 68 000 км 	68 300, зараз береться з третьої цифри

        //         }
        //     } else {
        //         console.log(`FAIL: На ${siteUrl} немає першої реєстрації: "${kmNumber}"`);
        //     }
        // } else {
        //     console.log(`FAIL: На ${siteUrl} не налаштовано kmSelector в конфігу`);
        // };





        // Закриваємо вкладку page1
        console.log("=====================Next Cart====================")
        await page1.close();

        // Повертаємося на сторінку лістингу
        await page.goBack();
        await page.waitForLoadState('domcontentloaded');

    }; // кінець циклу фор


    // Клікаєм на кнопку NextPage
    currentPage++;
    if (currentPage <= maxPage) {
        const nextPageButton = page.locator(SELECTOR.automoto.listing.nextPageButton);
        console.log(`Next page (${currentPage})`);
        await nextPageButton.click();
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2000);
    }
}; //кінець циклу вайл
});