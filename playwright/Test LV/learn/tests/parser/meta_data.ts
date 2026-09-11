export const TEST_DATA = {
    volks: 'Volkswagen',
    audi: 'Audi',
    bmw: 'BMW',
    mainUrl: 'https://automoto.com.lv/ru/',
    cookieButtonAutoPlius: '#onetrust-reject-all-handler',
};

export const SYNONYMS = {
    kinseva:{
        sold: ["продано", "не существует", "не актульное", "продал", "это транспортное средство уже продано!", "объявление не существует."],
        palivo:{
            electo:["электро", "электрический", "электричество", "электроическая"],
            dizel:["дизель"],
            gaz_benz:["газ/бензин", "бензин/газ", "бензин / газ", "газ / бензин", "газ/бензин"],
            gaz:["газ", "газовый", "газовое", "газовая", "газ (CNG/сжатый)", "газ (LPG/сжиженный)", "газ (LPG/сжиженный)"],
            gibrid:["бензин / электричество", "гибрид", "подключаемый гибрид (дизель / электричество)", "Гибрид (дизель/электричество)", "подключаемый гибрид (бензин / электричество)", "подключаемый гибрид (бензин / электричество)", "подключаемый гибрид (бензин / электричество)"],
        },

        privod:{
            AWD:["полный привод", "четырехприводный", "все ведущие", "4wd", "4x4"],
            FWD:["передний привод", "переднеприводный", "передние ведущие", "fwd"],
            RWD:["задний привод", "заднеприводный", "задние ведущие", "rwd"],
        },

        color:{
            black:["черный", "чёрный", "черного"],
            white:["белый", "белого"],
            green:["зеленый", "зелёный"],
            gray:["серый", "серого", "серебряный", "серебристый", "серебряного", "серебристого", "grey"],
            blue:["синий", "синего", "голубой", "голубого"], //потом убрать голубой когда в админке включат
            red:["красный", "красного", "бордовый", "бордового"], //потом убрать бордовый когда в админке включат
            yellow:["желтый", "желтого", "жёлтый", "жёлтого"],
            brown:["коричневый", "коричневого", "коричн"],
            drugoy:["другой", "другое", "не указан"],
        },

        kuzov:{
            vnedorojnik:["джип", "внедорожник"],
            hetchbeck:["хэтчбек", "хетчбэк"],
            lite_furgon:["легковой фургон", "пассажирский микроавтобус", "грузовые микроавтобусы", "коммерческий"],
            microBus:["минивэн/микроавтобус", "микроавтобус"],
            drugoy:["другой", "другое"],
        },

        marka:{
            mercedes:["mercedes-benz", "mercedes"],
            vaz:["vaz", "lada", "lada (vaz)", "ваз"],
        },

        model:{
            volvo:["xc40", "xc60", "xc90", "s60", "s90", "v60", "v90"],
            mercedes:{
                vito:["vito", "v200", "v220", "v250", "v300"],
            },
        },

        kpp:{
            manual:["ручная", "механическая"],
        },

        seller:{
            prodavets:["продавец"],
        },
        

    },
};

//kinseva
export const SELECTOR = {
    automoto:{
        golovna:{
            newLabel: 'label:has-text("Новые")',
            cart: 'span[class="absolute inset-0"]',
            
        },
        listing:{
            cart: 'a[class="block text-[#252525] text-xl font-medium"]',
            nextPageButton: 'a[data-click-arg="pagination_next"]'
        },
        kinseva:{
            pole: 'h1[class="text-[#252525] text-[28px] font-medium leading-none"]', //title
            countPhotos: 'span.swiper-pagination-total',
            harakteristiki: 'div[class="text-[#252525] text-sm font-medium"]',
            color: 'a[data-click-arg=link_key_information_color]',
            palivo: 'a[data-click-arg=link_key_information_fuel]',
            price: 'div[class="text-[#252525] text-2xl font-medium"]',
            obyemDviguna: 'a[data-click-arg=link_key_information_engine_volume]',
            privod: 'a[data-click-arg=link_key_information_drive]',
            seller: 'div.bg-gray-50.border.rounded-lg span.font-medium',
            submitButton: 'button[data-click-arg="button_contact_partner"]',
        },
    },

    sslv:{
        //haven't seller
        kinseva:{
            title: '#tdo_31 b',
            seller: 'td.ads_contacts_name:has-text("Компания:") + td.ads_contacts',
            kuzov: '#tdo_32',
            km: '#tdo_16',
            kpp: '#tdo_35',
            privod: '#msg_div_spec b:has-text("привод")',
            color: '#tdo_17',
            price: '#tdo_8',
            price_2: '#tdo_8',
            tipDvigatela: '#tdo_34',// for electric
            palivo: '#tdo_15',
            obyemDviguna: '#tdo_15',//skip for electric
            counterSpan: 'div.pic_dv_thumbnail',
            registration: 'div.pic_dv_thumbnail',
            year: '#tdo_18',
        },
    },
    auto24:{
        kinseva:{
            sold: 'div[class="e-message -error t-fs-xl t-mb-m"]',
            title: 'div.tpl-content h1.commonSubtitle',
            seller: 'address[class="section seller"] h2.commonSubtitle',
            kuzov: 'tr.field-keretyyp span.value',
            km: 'tr.field-labisoit span.value',
            kpp: 'tr.field-kaigukast_kaikudega span.value',
            privod: 'tr.field-vedavsild span.value',
            color: 'tr.field-varvus span.value',
            price: 'tr.field-hind span.value',
            price_2: 'tr.field-soodushind span.value',
            palivo: 'table.group.full tr:has-text("Топливо:") td.value',
            obyemDviguna: 'table.group.full tr:has-text("Объем:") td.value',
            obyemDviguna_kwh: 'table.group.full tr:has-text("мощность:") td.value',
            counterSpan: 'span.lg-counter-all',
            registration: 'span.lg-counter-all',
            year: 'tr.field-month_and_year',
        },
    },
    autogidas:{
        kinseva:{
            sold: 'div[class="e-message -error t-fs-xl t-mb-m"]',
            title: 'h1.sticky-title',
            seller: 'div.seller-name',
            kuzov: 'div.list-striped-item:has-text("Тип кузова") div.list-striped-item-value',
            km: 'div.icon.param-mileage b',
            kpp: 'div.icon.param-gearbox b',
            privod: 'div.list-striped-item:has-text("Ведущие колёса") div.list-striped-item-value',
            color: 'div.list-striped-item:has-text("Цвет") div.list-striped-item-value',
            price: 'div.sticky-price strong',
            price_2: 'div.sticky-price strong',
            palivo: 'div.icon.param-fuel-type b',
            obyemDviguna: 'div.icon.param-engine b',
            counterSpan: '#photoCount',
            registration: 'div.icon.param-year b',
            year: 'div.icon.param-year b',
            bigPhoto: '#big-photo-container',
        },
    },
    autoplius:{
        kinseva:{
            sold: '.notification-message-title',
            title: 'div.title-text',
            seller: 'div.seller-contact-name',
            kuzov: 'div.parameter-row:has-text("Тип кузова") div.parameter-value',
            km: 'div.parameter-row:has-text("Пробег") div.parameter-value',
            kpp: 'div.parameter-row:has-text("Коробка передач") div.parameter-value',
            privod: 'div.parameter-row:has-text("Тип трансмиссии") div.parameter-value',
            color: 'div.parameter-row:has-text("Цвет") div.parameter-value',
            price: 'div.price',
            price_2: 'div.price',
            palivo: 'div.parameter-row:has-text("Тип топлива") div.parameter-value',
            obyemDviguna: '.title-parameters-container .title-parameter:nth-child(2)',
            obyemDviguna_kwh: '.parameter-value.green-vehicle',
            counterSpan: 'div[class="announcement-gallery-carousel__slide js-announcement-gallery-thumbnail-carousel"]',
            registration: 'div.parameter-row:has-text("Первая регистрация") div.parameter-value',
            year: 'div.title-year',
        },
    },
    okidoki:{
        kinseva:{
            sold: '.notification-message-title',
            title: 'div[class="item-title"] h1[itemprop="name"]',
            seller: 'div.seller-contact-name',
            kuzov: 'li:has-text("Тип кузова") span.item-specific__data',
            km: 'ul.item-params li:nth-child(2) span:nth-child(2)',
            kpp: 'li:has-text("Коробка передач") span.item-specific__data',
            privod: 'li:has-text("Привод") span.item-specific__data',
            color: 'li:has-text("Цвет") span.item-specific__data',
            price: '.item-price-content',
            price_2: '.item-price-content',
            palivo: 'ul.item-params li:nth-child(4) span:nth-child(2)',
            obyemDviguna: 'ul.item-params li:nth-child(3) span:nth-child(2)',
            counterSpan: 'span[class="item-photos__counter item-photos__counter--total"]',
            registration: 'ul.item-params li:nth-child(1) span:nth-child(2)',
            year: 'ul.item-params li:nth-child(1) span:nth-child(2)',
        },
    },
    motorfy:{
        kinseva:{
            sold: 'img.h-full:has-text("thumb_drīzumā")', // thumb_drīzumā = thumb_скоро. мб таке добавить в словник
            title: 'h2[class="text-center text-xl min-[901px]:text-2xl font-bold text-gray-900"]',
            seller: 'div.seller-contact-name',
            kuzov: 'div.flex.items-end:has-text("Virsbūve") div.min-w-0 span',
            km: 'div.flex.items-end:has-text("Пробег") div.min-w-0 span',
            kpp: 'li:has-text("Коробка передач") span.item-specific__data',
            privod: 'li:has-text("Привод") span.item-specific__data',
            privod_2: 'span[data-slot="base"]:has-text("привод")',
            color: 'div.flex.items-end:has-text("Цвет") div.min-w-0 span',
            price: 'span[class="ml-2 text-xl min-[901px]:text-2xl font-bold text-primary"]',
            price_2: 'span[class="ml-2 text-xl min-[901px]:text-2xl font-bold text-primary"]',
            palivo: 'div.flex.items-end:has-text("Двигатель") div.min-w-0 span',
            obyemDviguna: 'div.flex.items-end:has-text("Двигатель") div.min-w-0 span',
            counterSpan: 'button[class="rounded-md font-medium inline-flex items-center disabled:cursor-not-allowed aria-disabled:cursor-not-allowed disabled:opacity-75 aria-disabled:opacity-75 transition-colors text-sm gap-1.5 text-default hover:bg-elevated active:bg-elevated focus:outline-none focus-visible:bg-elevated hover:disabled:bg-transparent dark:hover:disabled:bg-transparent hover:aria-disabled:bg-transparent dark:hover:aria-disabled:bg-transparent h-16 w-20 min-[901px]:h-24 min-[901px]:w-28 shrink-0 overflow-hidden p-0"]',
            registration: 'ul.item-params li:nth-child(1) span:nth-child(2)',
            year: 'div.flex.items-end:has-text("Год выпуска") div.min-w-0 span',
        },
    },
    mollerauto:{
        kinseva:{
            sold: 'img.h-full:has-text("thumb_drīzumā")',
            title: 'h1.ProductActions-Title',
            seller: 'div.ProductAdditionalInfo-Details:has-text("Дилер") p',
            kuzov: 'dt:has-text("Тип кузова") + dd',
            km: 'dt:has-text("Пробег") + dd',
            kpp: 'h3:has-text("Коробка передач") + div',
            privod: 'dt:has-text("Трансмиссия") + dd',
            privod_2: 'span[data-slot="base"]:has-text("привод")',
            color: 'dt:has-text("Цвет") + dd',
            price: 'span[itemprop="price"]',
            price_2: 'span[itemprop="price"]',
            palivo: 'dt:has-text("Топливо") + dd',
            obyemDviguna: 'dt:has-text("Рабочий объем") + dd',
            counterSpan: '.Image-Image',
            registration: 'ul.item-params li:nth-child(1) span:nth-child(2)',
            year: 'dt:has-text("Первая регистрация") + dd',
        },
    },
};

//listing
export const SELECTOR_L = {
};

//golovna
export const SELECTOR_G = {
};

export const TIMEOUTS = {
    short: 1000,
    medium: 3000,
    long: 5000,
};
