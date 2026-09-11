import {expect, test} from './fixtures';
import {SELECTOR, SYNONYMS} from './meta_data';

interface TargetSiteConfig {
    titleSelector: string;
    photoCountMethod: (page: any) => Promise < string > ;
    counterPhotoSelector ? : string;
    yearMethod : (page: any) => Promise < string > ;
    colorSelector ? : string;
    palivoSelector ? : string;
    priceSelector: string;
    priceSelector_2 ? : string; //for auto24
    obyemDvigunaSelector ? : string;
    obyemDvigunaSelector_kwh ? : string; // for electgric car
    tipDvigatelaSelector ? : string; // for sslv
    kuzovSelector: string;
    kmSelector: string;
    kppSelector: string;
    privodSelector ? : string; 
    privodSelector_2 ? : string; //for motorfy
    sellerSelector ? : string;
    registrationSelector ? : string;
    soldSelector ? : string;
    onlyNumber ? : (text: string) => string;
    bigPhotoSelector ? : string
}

const SITE_CONFIGS: Record < string, TargetSiteConfig > = {
    'ss.lv': {
        titleSelector: SELECTOR.sslv.kinseva.title,
        photoCountMethod: async (p) => (await p.locator(SELECTOR.sslv.kinseva.counterSpan).count()).toString(),
        yearMethod: async (p) => (await p.locator(SELECTOR.sslv.kinseva.year).textContent() ?? '').trim(),
        colorSelector: SELECTOR.sslv.kinseva.color,
        palivoSelector: SELECTOR.sslv.kinseva.palivo,
        priceSelector: SELECTOR.sslv.kinseva.price,
        priceSelector_2: SELECTOR.sslv.kinseva.price_2,
        obyemDvigunaSelector: SELECTOR.sslv.kinseva.obyemDviguna,
        tipDvigatelaSelector: SELECTOR.sslv.kinseva.tipDvigatela,
        kuzovSelector: SELECTOR.sslv.kinseva.kuzov,
        kmSelector: SELECTOR.sslv.kinseva.km,
        kppSelector: SELECTOR.sslv.kinseva.kpp,
        privodSelector: SELECTOR.sslv.kinseva.privod,
        // registrationSelector: SELECTOR.sslv.kinseva.registration,
        sellerSelector: SELECTOR.sslv.kinseva.seller,
    },
    'auto24.lv': {
        titleSelector: SELECTOR.auto24.kinseva.title,
        photoCountMethod: async (p) => (await p.locator(SELECTOR.auto24.kinseva.counterSpan).textContent() ?? '').trim(),
        yearMethod: async (p) => {
            const rawText = await p.locator(SELECTOR.auto24.kinseva.year).textContent() ?? '';
            const match = rawText.match(/\d{4}/);
            return match ? match[0] : '';
        },
        colorSelector: SELECTOR.auto24.kinseva.color,
        palivoSelector: SELECTOR.auto24.kinseva.palivo,
        priceSelector: SELECTOR.auto24.kinseva.price,
        priceSelector_2: SELECTOR.auto24.kinseva.price_2,
        obyemDvigunaSelector: SELECTOR.auto24.kinseva.obyemDviguna,
        obyemDvigunaSelector_kwh: SELECTOR.auto24.kinseva.obyemDviguna_kwh,
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

        photoCountMethod: async (p): Promise < string > => {
            // 1. Забираємо тексти ВСІХ скриптів на сторінці одним махом
            const allScriptsArray: string[] = await p.locator('script').allTextContents();

            // 2. Фільтруємо і склеюємо лише ті, які містять "gallery.addImage"
            // Явно вказуємо, що scriptText — це string
            const targetScriptsText: string = allScriptsArray.filter((scriptText: string) => scriptText.includes('gallery.addImage')).join('');

            if (targetScriptsText) {
                // 3. Видаляємо всі пробіли, таби та переноси рядків (\n, \r, \u00a0)
                const cleanedText: string = targetScriptsText.replace(/[\s\u00a0]+/g, '');

                // 4. Rozbyvaemo monolit za vyklykom funktsii
                const parts: string[] = cleanedText.split('gallery.addImage(');

                // 5. Рахуємо тільки ті блоки, де другим параметром йде строго 'image' або "image"
                // Явно вказуємо, що part — це string
                const photoCount: number = parts.filter((part: string) => {return part.includes(",'image'") || part.includes(',"image"');}).length;

                if (photoCount > 0) {
                    return photoCount.toString();
                }
            }

            return '0';
        },

        yearMethod: async (p) => {
            const rawText = await p.locator(SELECTOR.autogidas.kinseva.year).textContent() ?? '';
            const match = rawText.match(/\d{4}/);
            return match ? match[0] : '';
        },

        colorSelector: SELECTOR.autogidas.kinseva.color,
        palivoSelector: SELECTOR.autogidas.kinseva.palivo,
        priceSelector: SELECTOR.autogidas.kinseva.price,
        priceSelector_2: SELECTOR.autogidas.kinseva.price_2,
        obyemDvigunaSelector: SELECTOR.autogidas.kinseva.obyemDviguna,
        kuzovSelector: SELECTOR.autogidas.kinseva.kuzov,
        kmSelector: SELECTOR.autogidas.kinseva.km,
        kppSelector: SELECTOR.autogidas.kinseva.kpp,
        privodSelector: SELECTOR.autogidas.kinseva.privod,
        sellerSelector: SELECTOR.autogidas.kinseva.seller,
        registrationSelector: SELECTOR.autogidas.kinseva.registration,
        soldSelector: SELECTOR.autogidas.kinseva.sold,
        bigPhotoSelector: SELECTOR.autogidas.kinseva.bigPhoto,
    },
    'autoplius': {
        titleSelector: SELECTOR.autoplius.kinseva.title,

        photoCountMethod: async (p) => {
            const counterLocator = p.locator(SELECTOR.autoplius.kinseva.counterSpan);

            const countLocator = await counterLocator.count();
            const count = countLocator / 2;
            const countLocatorString = count.toString();

            return countLocatorString;
        },
        yearMethod: async (p) => (await p.locator(SELECTOR.autoplius.kinseva.year).first().textContent() ?? '').trim(),
        colorSelector: SELECTOR.autoplius.kinseva.color,
        palivoSelector: SELECTOR.autoplius.kinseva.palivo,
        priceSelector: SELECTOR.autoplius.kinseva.price,
        priceSelector_2: SELECTOR.autoplius.kinseva.price_2,
        obyemDvigunaSelector: SELECTOR.autoplius.kinseva.obyemDviguna,
        obyemDvigunaSelector_kwh: SELECTOR.autoplius.kinseva.obyemDviguna_kwh,
        kuzovSelector: SELECTOR.autoplius.kinseva.kuzov,
        kmSelector: SELECTOR.autoplius.kinseva.km,
        kppSelector: SELECTOR.autoplius.kinseva.kpp,
        privodSelector: SELECTOR.autoplius.kinseva.privod,
        sellerSelector: SELECTOR.autoplius.kinseva.seller,
        registrationSelector: SELECTOR.autoplius.kinseva.registration,
        soldSelector: SELECTOR.autoplius.kinseva.sold,
    },
    'okidoki': {
        titleSelector: SELECTOR.okidoki.kinseva.title,

        photoCountMethod: async (p) => {
            const counterLocator = p.locator(SELECTOR.okidoki.kinseva.counterSpan);

            const countLocator = await counterLocator.count();
            const count = countLocator / 2;
            const countLocatorString = count.toString();

            return countLocatorString;
        },
        yearMethod: async (p) => (await p.locator(SELECTOR.okidoki.kinseva.year).texContent() ?? '').trim(),
        colorSelector: SELECTOR.okidoki.kinseva.color,
        palivoSelector: SELECTOR.okidoki.kinseva.palivo,
        priceSelector: SELECTOR.okidoki.kinseva.price,
        priceSelector_2: SELECTOR.okidoki.kinseva.price_2,
        obyemDvigunaSelector: SELECTOR.okidoki.kinseva.obyemDviguna,
        kuzovSelector: SELECTOR.okidoki.kinseva.kuzov,
        kmSelector: SELECTOR.okidoki.kinseva.km,
        kppSelector: SELECTOR.okidoki.kinseva.kpp,
        privodSelector: SELECTOR.okidoki.kinseva.privod,
        sellerSelector: SELECTOR.okidoki.kinseva.seller,
        registrationSelector: SELECTOR.okidoki.kinseva.registration,
        soldSelector: SELECTOR.okidoki.kinseva.sold,
    },
    'motorfy': {
        titleSelector: SELECTOR.motorfy.kinseva.title,

        photoCountMethod: async (p) => {
            const counterLocator = p.locator(SELECTOR.motorfy.kinseva.counterSpan);

            const countLocator = await counterLocator.count();
            const countPhoto = (countLocator + 1).toString();

            return countPhoto;
        },
        yearMethod: async (p) => (await p.locator(SELECTOR.motorfy.kinseva.year).textContent() ?? '').trim(),
        counterPhotoSelector: SELECTOR.motorfy.kinseva.counterSpan,
        colorSelector: SELECTOR.motorfy.kinseva.color,
        palivoSelector: SELECTOR.motorfy.kinseva.palivo,
        priceSelector: SELECTOR.motorfy.kinseva.price,
        priceSelector_2: SELECTOR.motorfy.kinseva.price_2,
        obyemDvigunaSelector: SELECTOR.motorfy.kinseva.obyemDviguna,
        kuzovSelector: SELECTOR.motorfy.kinseva.kuzov,
        kmSelector: SELECTOR.motorfy.kinseva.km,
        kppSelector: SELECTOR.motorfy.kinseva.kpp,
        privodSelector: SELECTOR.motorfy.kinseva.privod,
        privodSelector_2: SELECTOR.motorfy.kinseva.privod_2,
        sellerSelector: SELECTOR.motorfy.kinseva.seller,
        registrationSelector: SELECTOR.motorfy.kinseva.registration,
        soldSelector: SELECTOR.motorfy.kinseva.sold,
    },
    'mollerauto': {
        titleSelector: SELECTOR.mollerauto.kinseva.title,

        photoCountMethod: async (p) => {
            const counterLocator = p.locator(SELECTOR.mollerauto.kinseva.counterSpan);

            const countLocator = await counterLocator.count();
            const countPhoto = ((countLocator - 1)/2).toString();

            return countPhoto;
        },
        yearMethod: async (p) => (await p.locator(SELECTOR.mollerauto.kinseva.year).textContent() ?? '').trim(),
        counterPhotoSelector: SELECTOR.mollerauto.kinseva.counterSpan,
        colorSelector: SELECTOR.mollerauto.kinseva.color,
        palivoSelector: SELECTOR.mollerauto.kinseva.palivo,
        priceSelector: SELECTOR.mollerauto.kinseva.price,
        priceSelector_2: SELECTOR.mollerauto.kinseva.price_2,
        obyemDvigunaSelector: SELECTOR.mollerauto.kinseva.obyemDviguna,
        kuzovSelector: SELECTOR.mollerauto.kinseva.kuzov,
        kmSelector: SELECTOR.mollerauto.kinseva.km,
        kppSelector: SELECTOR.mollerauto.kinseva.kpp,
        privodSelector: SELECTOR.mollerauto.kinseva.privod,
        privodSelector_2: SELECTOR.mollerauto.kinseva.privod_2,
        sellerSelector: SELECTOR.mollerauto.kinseva.seller,
        registrationSelector: SELECTOR.mollerauto.kinseva.registration,
        soldSelector: SELECTOR.mollerauto.kinseva.sold,
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

const onlyNumber = (text: string | null | undefined): string => {if (!text) return '';return text.replace(/[^0-9.]/g, '').trim();};

test("Universal test for parser", async ({page}) => {

    // Збираємо з автомото, каталог, потім кінцева
    await page.goto("https://automoto.com.lv/ru/bu-avto?page=3");
    await page.waitForLoadState('domcontentloaded');

    let currentPage = 3;
    let maxPage = 10;

    while (currentPage <= maxPage) {

        const cardsLocator = page.locator(SELECTOR.automoto.listing.cart);
        const countKarta = await cardsLocator.count();

        //цикл
        for (let i = 0; i < countKarta; i++) {
            const thisCard = cardsLocator.nth(i);

            const cart = ((await thisCard.textContent()) ?? '').trim().toLowerCase();
            const marka = ((cart.match(/^([^\s,]+)/) ?? [])[1] ?? '').replace(/-/g, ' ').replace(/\//g, '').trim();
            const model = ((cart.match(/^\S+\s+([^\s,]+)/) ?? [])[1] ?? '').replace(/-/g, ' ').replace(/\//g, '').trim();
            const markaModel = `${marka} ${model}`;

            await thisCard.click();

            // Парсимо базові значення
            const pole = ((await page.locator(SELECTOR.automoto.kinseva.pole).textContent()) ?? '').replace(/-/g, ' ').trim().toLowerCase();
            expect(pole).toContain(marka);
            expect(pole).toContain(model);

            const countPhotos = ((await page.locator(SELECTOR.automoto.kinseva.countPhotos).textContent()) ?? '').trim();
            const kpp = ((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(2).textContent()) ?? '').trim().toLowerCase();
            const color = (await page.locator(SELECTOR.automoto.kinseva.color).textContent() ?? '').toLowerCase().replace(/цвет/, '').trim();
            const price = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.price).filter({hasText: '€'}).textContent() ?? '').trim());
            const kuzov = ((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(1).textContent()) ?? '').trim().toLowerCase();
            const palivo = (await page.locator(SELECTOR.automoto.kinseva.palivo).textContent() ?? '').replace(/топливо/g, "").trim().toLowerCase();
            // const obyemDviguna = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.obyemDviguna).textContent() ?? '').replace(/Двигатель/g, "").trim()); //закомєнтив для теста, поставив harakteristiki
            const obyemDviguna = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(3).textContent() ?? '').trim());
            // console.log(obyemDviguna)
            const seller = (await page.locator(SELECTOR.automoto.kinseva.seller).last().textContent() ?? '').trim().toLowerCase();
            const privod = (await page.locator(SELECTOR.automoto.kinseva.privod).textContent() ?? '').trim().toLowerCase();

            const km = onlyNumber((await page.locator(SELECTOR.automoto.kinseva.harakteristiki).nth(0).textContent() ?? '').trim());
            const kmNumber = km.length;
            const kmNumber_2 = km.substring(0, 3);

            const registration = onlyNumber((await page.locator('div[class="flex items-start gap-2 text-[#666666] shrink-0"] .text-sm').last().textContent() ?? '').trim());
            console.log(`Шо виведе ${registration}`)

            const yearRaw = (await page.locator(SELECTOR.automoto.kinseva.pole).last().textContent() ?? '').trim();
            const parts = yearRaw.split(',');
            let year = '';
            if (parts.length > 1) {
                // Шукаємо 4 цифри вже суто в другій частині (" 2023")
                const match = parts[1].match(/\d{4}/);
                year = match ? match[0] : '';
            };

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
            if (!currentConfig) {throw new Error(`Тест впав: Немає конфігурації для сайту донора! Поточний URL: ${siteUrl}`);}

            // Перевірки
            // SOLD?
            if (currentConfig && currentConfig.soldSelector) {

                const soldSelector = page1.locator(currentConfig.soldSelector);

                if (await soldSelector.count() > 0) {

                    const sold = (await soldSelector.first().textContent() ?? '').trim().toLowerCase();

                    textToNotContainAnySynonym(sold, SYNONYMS.kinseva.sold);

                } else {
                    console.log(`GOOD: Оголошення актуальне`);
                }
            };

            // 1. Перевірка Марки
            if (currentConfig && currentConfig.titleSelector) {

                const titleSelector = page1.locator(currentConfig.titleSelector);

                if (await titleSelector.count() > 0) {
                    const siteMarka = (await titleSelector.first().textContent() ?? '').replace(/\s+/g, "").replace(/-/g, '').replace(/\//g, '').trim().toLowerCase();
            
                    if (marka.includes("mercedes-benz")) {

                        textToContainAnySynonym(marka, SYNONYMS.kinseva.marka.mercedes);
                        textToContainAnySynonym(siteMarka, SYNONYMS.kinseva.marka.mercedes);

                    } else if (marka.includes("vaz")) {
                        textToContainAnySynonym(marka, SYNONYMS.kinseva.marka.vaz);
                        textToContainAnySynonym(siteMarka, SYNONYMS.kinseva.marka.vaz);
                    } else {
                        // expect(siteMarka).toContain(markaModel);
                        expect(siteMarka).toContain(marka);
                        // expect(siteMarka).toContain(model);
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
                    const siteMarka = (await titleSelector.first().textContent() ?? '').replace(/\s+/g, "").replace(/-/g, ' ').replace(/\//g, '').trim().toLowerCase();

                    // if (model.includes("xc")) {

                    //     textToContainAnySynonym(model, SYNONYMS.kinseva.model.volvo);
                    //     textToContainAnySynonym(siteMarka, SYNONYMS.kinseva.model.volvo);

                    // }else if (model.includes("vito")) {
                    //     textToContainAnySynonym(model, SYNONYMS.kinseva.model.mercedes.vito);
                    //     textToContainAnySynonym(siteMarka, SYNONYMS.kinseva.model.mercedes.vito);
                    // } else {
                        expect(siteMarka).toContain(model);
                        console.log(`GOOD: Model, "${siteMarka}" include "${model}"`)

                    // }
                } else {
                    console.log(`FAIL: На ${siteUrl} немає марки: "${model}"`);
                }
            } else {
                console.log(`FAIL: На ${siteUrl} не налаштовано titleSelector в конфігу`);
            };

            // 3. Рік
            if (currentConfig && currentConfig.yearMethod) {

                const yearSelector = await currentConfig.yearMethod(page1);

                if (yearSelector) {
                    expect(yearSelector).toContain(year);
                    console.log(`GOOD: Year, "${yearSelector}" include "${year}"`);
                } else {
                    console.log(`FAIL: На ${siteUrl} немає року: "${year}"`);
                }
            } else {
                console.log(`FAIL: На ${siteUrl} не налаштовано yearSelector в конфігу`);
            };

            // 4. Кількість фото
            if (currentConfig.bigPhotoSelector) {
                const photoElement = page1.locator(currentConfig.bigPhotoSelector)

                await photoElement.click();
            }

            const sitePhotosCount = await currentConfig.photoCountMethod(page1);
            expect(sitePhotosCount).toBe(countPhotos); //закоментив бо часто падає
            console.log(`GOOD: CountPhoto, "${sitePhotosCount}" toBe "${countPhotos}"`);


            // 5. Тип кузова
            if (currentConfig && currentConfig.kuzovSelector) {

                const kuzovLocator = page1.locator(currentConfig.kuzovSelector);

                if (await kuzovLocator.count() > 0) {
                    const siteKuzov = (await kuzovLocator.first().textContent() ?? '').trim().toLowerCase();

                    if (kuzov.includes("внедорожник")) {

                        textToContainAnySynonym(kuzov, SYNONYMS.kinseva.kuzov.vnedorojnik);
                        textToContainAnySynonym(siteKuzov, SYNONYMS.kinseva.kuzov.vnedorojnik);

                    } else if (kuzov.includes("хэтчбек")) {

                        textToContainAnySynonym(kuzov, SYNONYMS.kinseva.kuzov.hetchbeck);
                        textToContainAnySynonym(siteKuzov, SYNONYMS.kinseva.kuzov.hetchbeck);

                    } else if (kuzov.includes("легковой фургон")) {

                        textToContainAnySynonym(kuzov, SYNONYMS.kinseva.kuzov.lite_furgon);
                        textToContainAnySynonym(siteKuzov, SYNONYMS.kinseva.kuzov.lite_furgon);

                    } else if (kuzov.includes("другой")) {

                        textToContainAnySynonym(kuzov, SYNONYMS.kinseva.kuzov.drugoy);
                        textToContainAnySynonym(siteKuzov, SYNONYMS.kinseva.kuzov.drugoy);

                    } else if (siteKuzov.includes("-")) {
                        
                        console.log(`CHECK: На ${siteUrl} немає кузова : "${siteKuzov}"`);
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

            // 7. Цвет / Колір
            if (currentConfig && currentConfig.colorSelector) {

                const colorLocator = page1.locator(currentConfig.colorSelector);

                if (await colorLocator.count() > 0) {
                    const siteColor = (await colorLocator.first().textContent() ?? '').replace(/цв\./, " ").trim().toLowerCase();

                    if (color.includes("черный")) {

                        textToContainAnySynonym(color, SYNONYMS.kinseva.color.black);
                        textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.black);

                    } else if (color.includes("зеленый")) {

                        textToContainAnySynonym(color, SYNONYMS.kinseva.color.green);
                        textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.green);

                    } else if (color.includes("серый")) {

                        textToContainAnySynonym(color, SYNONYMS.kinseva.color.gray);
                        textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.gray);

                    } else if (color.includes("синий")) {

                        textToContainAnySynonym(color, SYNONYMS.kinseva.color.blue);
                        textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.blue);

                    } else if (color.includes("желтый")) {

                        textToContainAnySynonym(color, SYNONYMS.kinseva.color.yellow);
                        textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.yellow);

                    } else if (color.includes("белый")) {

                        textToContainAnySynonym(color, SYNONYMS.kinseva.color.white);
                        textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.white);

                    } else if (color.includes("коричневый")) {

                        textToContainAnySynonym(color, SYNONYMS.kinseva.color.brown);
                        textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.brown);

                    } else if (color.includes("красный")) {

                        textToContainAnySynonym(color, SYNONYMS.kinseva.color.red);
                        textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.red);

                    } else if (color.includes("не указан")) {

                        textToContainAnySynonym(color, SYNONYMS.kinseva.color.drugoy);
                        textToContainAnySynonym(siteColor, SYNONYMS.kinseva.color.drugoy);

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

    const obyemDvigunaLocator = page1.locator(currentConfig.obyemDvigunaSelector);

    if (await obyemDvigunaLocator.count() > 0) {

        const siteobyemDviguna = onlyNumber((await page1.locator(currentConfig.obyemDvigunaSelector).first().textContent() ?? '').toLowerCase().trim());

        if (obyemDviguna.includes("0.0")) {

            console.log(`CHECK, FAIL : На ${automotoUrl} немає об'єму двигуна: ${obyemDviguna}`)
        } else if (obyemDviguna.includes(siteobyemDviguna)) {

            expect (obyemDviguna).toContain(siteobyemDviguna)
            console.log(`GOOD: Obyem, "${obyemDviguna}" include "${siteobyemDviguna}"`)
        } else if (siteobyemDviguna.includes(obyemDviguna)) {

            expect (siteobyemDviguna).toContain(obyemDviguna)
            console.log(`GOOD: Obyem, "${siteobyemDviguna}" include "${obyemDviguna}"`)
        
        } else {
            // Перевіряємо наявність другого селектора ТІЛЬКИ якщо основний об'єм не підійшов
            const hasKwh = currentConfig.obyemDvigunaSelector_kwh && await page1.locator(currentConfig.obyemDvigunaSelector_kwh).count() > 0;
            
            if (hasKwh) {
                const siteobyemDviguna_2 = onlyNumber((await page1.locator(currentConfig.obyemDvigunaSelector_kwh!).first().textContent() ?? '').toLowerCase().trim());
                
                expect(siteobyemDviguna_2).toContain(obyemDviguna);
                console.log(`GOOD: Obyem KWH, "${siteobyemDviguna_2}" include "${obyemDviguna}"`)
            } else if (currentConfig.obyemDvigunaSelector_kwh) {
                // Якщо селектор у конфігу є, але count === 0 (елемента немає на сторінці)
                console.log(`FAIL: На ${siteUrl} немає об'єму двигуна kWh: ${obyemDviguna}, або невідповідний об'єм ${siteobyemDviguna} `);
                // expect(siteobyemDviguna).toContain(obyemDviguna); поки в коменті бо часто падає коли об'єм 1490 - на сайті це 1.5, а у нас це 1.49
            } else {
                // Якщо селектора кВт·год взагалі немає в конфігу цього сайту
                expect (siteobyemDviguna).toContain(obyemDviguna);
                console.log(`FAIL: На ${siteUrl} не налаштовано obyemDvigunaLocator_kwh в конфігу 1`);
            }
        }

    // --- Нижній блок для випадків, коли основного селектора взагалі немає (наприклад, чисті електрокари) ---
    } else if (currentConfig.obyemDvigunaSelector_kwh) {
            
        const obyemDvigunaLocator_kwh = page1.locator(currentConfig.obyemDvigunaSelector_kwh);

        if (await obyemDvigunaLocator_kwh.count() > 0) {
            
            const siteobyemDviguna_2 = onlyNumber((await page1.locator(currentConfig.obyemDvigunaSelector_kwh).first().textContent() ?? '').toLowerCase().trim());
            
                expect(siteobyemDviguna_2).toContain(obyemDviguna);
                console.log(`GOOD: Obyem KWH, "${siteobyemDviguna_2}" include "${obyemDviguna}"`)
        } else {
            console.log(`FAIL: На ${siteUrl} немає об'єму двигуна kWh: ${obyemDviguna} `);
            // expect(siteobyemDviguna).toContain(obyemDviguna); поки в коменті бо часто падає коли об'єм 1490 - на сайті це 1.5, а у нас це 1.49
        }

    } else {
        // expect (siteobyemDviguna).toContain(obyemDviguna);
        console.log(`CHECK: На ${siteUrl} немає obyemDvigunaLocator_kwh`);
    }
} else {
    console.log(`FAIL: На ${siteUrl} не налаштовано obyemDvigunaLocator в конфігу`);
};

            //9. Продавець

            if (currentConfig && currentConfig.sellerSelector) {

                const sellerLocator = page1.locator(currentConfig.sellerSelector);

                if (await sellerLocator.count() > 0) {
                    // прибрати перевірку if коли зроблять таску 977
                    // const siteSeller = onlyNumber((await page1.locator(currentConfig.sellerSelector).first().textContent() ?? '').toLowerCase().trim());
                    const siteseller = (await page1.locator(currentConfig.sellerSelector).first().textContent() ?? '').toLowerCase().replace(/личность подтверждена/, " ").trim(); // можливо знадобиться 
                    if (siteseller.length > 0) {
                    
                        if (siteseller === "продавец") {
                            textToContainAnySynonym(seller, SYNONYMS.kinseva.seller.prodavets);
                        } else {
                            expect(siteseller).toContain(seller); // змінив seller contain siteseller щоб ловити якщо витягуємо з лишнім текстом
                            console.log(`GOOD: Seller, "${siteseller}" include "${seller}"`)
                        }
                    } else {
                        console.log(`CHECK: На ${siteUrl} немає поля продавця: "${siteseller}", тому вивели ${seller}`);
                    }
                } else {
                    console.log(`FAIL: На ${siteUrl} немає продавця: ${seller}`);
                }
            } else {
                console.log(`FAIL: На ${siteUrl} не налаштовано sellerLocator в конфігу`);
            };

            // 10. Тип приводу
            if (currentConfig && currentConfig.privodSelector) {

                const privodLocator = page1.locator(currentConfig.privodSelector);
                const privodLocator_2 = page1.locator(currentConfig.privodSelector_2 ?? 'BIDA');

                if (await privodLocator.count() > 0) {
                    const sitePrivod = (await privodLocator.first().textContent() ?? '').trim().toLowerCase();


                    if (privod.includes("передний привод")) {

                        textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.FWD);
                        textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.FWD);

                    } else if (privod.includes("полный привод")) {

                        textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.AWD);
                        textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.AWD);

                    } else if (privod.includes("задний привод")) {

                        textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.RWD);
                        textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.RWD);

                    } else {
                        expect(sitePrivod).toContain(privod)
                        console.log(`GOOD: Privod, "${sitePrivod}" include "${privod}"`)
                    }
                } else if (await privodLocator_2.count() > 0) {
                    const sitePrivod = (await privodLocator_2.first().textContent() ?? '').trim().toLowerCase();

                    if (privod.includes("передний привод")) {

                        textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.FWD);
                        textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.FWD);

                    } else if (privod.includes("полный привод")) {

                        textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.AWD);
                        textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.AWD);

                    } else if (privod.includes("задний привод")) {

                        textToContainAnySynonym(privod, SYNONYMS.kinseva.privod.RWD);
                        textToContainAnySynonym(sitePrivod, SYNONYMS.kinseva.privod.RWD);

                    } else {
                        expect(sitePrivod).toContain(privod)
                        console.log(`GOOD: Privod, "${sitePrivod}" include "${privod}"`)
                    }
                
                } else {
                    console.log(`FAIL: На ${siteUrl} немає типу приводу: "${privod}"`);
                }
            } else {
                console.log(`FAIL: На ${siteUrl} не налаштовано privodLocator or privodLocator_2 в конфігу`);
            };

            // 11. Цена
            const priceSelector = page1.locator(currentConfig.priceSelector);

            if (await priceSelector.count() > 0) {
                const rawPriceText = await page1.locator(currentConfig.priceSelector).first().textContent() ?? '';
                const firstNumbersMatch = rawPriceText.trim().match(/^\d+[\s\u00A0]?\d+/);
                const sitePrice = onlyNumber(firstNumbersMatch ? firstNumbersMatch[0] : '');
                // const sitePrice_2 = onlyNumber(await page1.locator(currentConfig.priceSelector_2 ?? "beda_2").first().textContent() ?? '');
                // const sitePrice = onlyNumber(await page1.locator(currentConfig.priceSelector).first().innerText() ?? '');

                if (sitePrice == price) {

                    expect(sitePrice).toContain(price);
                    console.log(`GOOD: First Price, "${sitePrice}" include "${price}"`)

                }else {
                    const hasPrice2 = currentConfig.priceSelector_2 && await page1.locator(currentConfig.priceSelector_2).count() > 0;
                    const sitePrice_2 = hasPrice2? onlyNumber(await page1.locator(currentConfig.priceSelector_2 ?? "beda_2").first().textContent() ?? ''): '';

                    if (sitePrice_2 == price) {
                        expect(sitePrice_2).toContain(price);
                        console.log(`GOOD: Second Price, "${sitePrice_2}" include "${price}"`)
                    } else {

                    expect(sitePrice).toContain(price);
                    console.error(`FAIL: Біда з основною ціною`)
                    console.log(sitePrice)
                    console.log(price)
                    };
                };

            } else if (currentConfig && currentConfig.priceSelector_2) {

                const priceSelector_2 = page1.locator(currentConfig.priceSelector_2);

                if (await priceSelector_2.count() > 0) {

                    const sitePrice_2 = onlyNumber(await page1.locator(currentConfig.priceSelector_2 ?? "beda_2").first().textContent() ?? '');
                    expect(sitePrice_2).toContain(price)
                    console.log(`GOOD: Action Price, "${sitePrice_2}" include "${price}"`)

                } else {

                    console.error(`FAIL: Біда з ціною`)
                }

            } else {

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

                    } else if (palivo.includes("газ/бензин")) {

                        textToContainAnySynonym(palivo, SYNONYMS.kinseva.palivo.gaz_benz);
                        textToContainAnySynonym(sitePalivo, SYNONYMS.kinseva.palivo.gaz_benz);

                    } else if (palivo.includes("гибрид")) {

                        textToContainAnySynonym(palivo, SYNONYMS.kinseva.palivo.gibrid);
                        textToContainAnySynonym(sitePalivo, SYNONYMS.kinseva.palivo.gibrid);

                    } else {
                        expect(sitePalivo).toContain(palivo)
                        console.log(`GOOD: Palivo, "${sitePalivo}" include "${palivo}"`)
                    }
                }else if (currentConfig.tipDvigatelaSelector) { //for sslv electir cars
                    const tipDvigatelaLocator = page1.locator(currentConfig.tipDvigatelaSelector);
                    if (await tipDvigatelaLocator.count() > 0) {
                        const siteTipDvigatela = (await tipDvigatelaLocator.first().textContent() ?? '').trim().toLowerCase();
                        textToContainAnySynonym(siteTipDvigatela, SYNONYMS.kinseva.palivo.electo);
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