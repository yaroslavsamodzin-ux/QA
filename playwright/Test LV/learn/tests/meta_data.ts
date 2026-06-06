export const TEST_DATA = {
    volks: 'Volkswagen',
    audi: 'Audi',
    bmw: 'BMW',
    mainUrl: 'https://automoto.com.lv/ru/',
    cookieButtonAutoPlius: '#onetrust-reject-all-handler',
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

        },
        kinseva:{
            submitButton: 'button[data-click-arg="button_contact_partner"]',
            countPhotos: 'span.swiper-pagination-total',
            harakteristiki: 'div[class="text-[#252525] text-sm font-medium"]',
        },
    },

    autoplius:{
        golovna:{

        },

        listing:{

        },

        kinseva:{
            kpp: 'tr.field-kaigukast_kaikudega',
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
// autoplius
// counterSpan: 'span.lg-counter-all',