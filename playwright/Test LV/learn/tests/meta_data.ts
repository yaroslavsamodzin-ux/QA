export const TEST_DATA = {
    volks: 'Volkswagen',
    audi: 'Audi',
    bmw: 'BMW',
    mainUrl: 'https://automoto.com.lv/ru/',
    cookieButtonAutoPlius: '#onetrust-reject-all-handler',
};

export const SYNONYMS = {
    kinseva:{
        palivo:{
            electo:["электро", "электрический"],
            dizel:["дизель"],
        },

        privod:{
            AWD:["полный привод", "четырехприводный", "4wd", "4x4"],
            FWD:["передний привод", "переднеприводный", "fwd"],
        },

        color:{
            black:["черный", "чёрный"],
        },

        kuzov:{
            vnedorojnik:["джип", "внедорожник"],
        },

        marka:{
            mercedes:["mercedes-benz", "mercedes"],
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
        },
    },
    auto24:{
        golovna:{

        },

        listing:{

        },

        kinseva:{
            title: 'h1.commonSubtitle',
            seller: 'address[class="section seller"] h2.commonSubtitle',
            kuzov: 'tr.field-keretyyp span.value',
            km: 'tr.field-labisoit span.value',
            kpp: 'tr.field-kaigukast_kaikudega',
            privod: 'tr.field-vedavsild span.value',
            color: 'tr.field-varvus',
            price: 'tr.field-hind span.value',
            palivo: 'table.group.full tr:has-text("Топливо:") td.value',
            obyemDviguna: 'table.group.full tr:has-text("Объем:") td.value',
            counterSpan: 'span.lg-counter-all',

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