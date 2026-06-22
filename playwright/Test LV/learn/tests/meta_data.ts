export const TEST_DATA = {
    volks: 'Volkswagen',
    audi: 'Audi',
    bmw: 'BMW',
    mainUrl: 'https://automoto.com.lv/ru/',
    cookieButtonAutoPlius: '#onetrust-reject-all-handler',
};

export const SYNONYMS = {
    kinseva:{
        sold: ["продано", "не существует", "не актульное", "продал"],
        palivo:{
            electo:["электро", "электрический"],
            dizel:["дизель"],
            gaz_benz:["газ/бензин", "бензин/газ"],
        },

        privod:{
            AWD:["полный привод", "четырехприводный", "все ведущие", "4wd", "4x4"],
            FWD:["передний привод", "переднеприводный", "передние ведущие", "fwd"],
        },

        color:{
            black:["черный", "чёрный"],
            green:["зеленый", "зелёный"],
            gray:["серый", "серого цв."],
        },

        kuzov:{
            vnedorojnik:["джип", "внедорожник"],
            hetchbeck:["хэтчбек", "хетчбэк"],
        },

        marka:{
            mercedes:["mercedes-benz", "mercedes"],
        },

        kpp:{
            manual:["ручная", "механическая"],
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
            kuzov: '#tdo_32',
            km: '#tdo_16',
            kpp: '#tdo_35',
            privod: '#msg_div_spec b:has-text("привод")',
            color: '#tdo_17',
            price: '#tdo_8',
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
            counterSpan: 'span.lg-counter-all',
            registration: 'span.lg-counter-all',
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
            // price_2: 'tr.field-soodushind span.value',
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
            sold: 'div[class="e-message -error t-fs-xl t-mb-m"]',
            title: 'div.title-text',
            seller: 'div.seller-contact-name',
            kuzov: 'div.parameter-row:has-text("Тип кузова") div.parameter-value',
            km: 'div.parameter-row:has-text("Пробег") div.parameter-value',
            kpp: 'div.parameter-row:has-text("Коробка передач") div.parameter-value',
            privod: 'div.parameter-row:has-text("Тип трансмиссии") div.parameter-value',
            color: 'div.parameter-row:has-text("Цвет") div.parameter-value',
            price: 'div.price',
            palivo: 'div.parameter-row:has-text("Тип топлива") div.parameter-value',
            obyemDviguna: '.title-parameters-container .title-parameter:nth-child(2)',
            counterSpan: 'span.announcement-gallery-carousel__counter',
            registration: 'div.parameter-row:has-text("Первая регистрация") div.parameter-value',
            year: 'div.title-year',
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