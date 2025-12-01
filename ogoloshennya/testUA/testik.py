#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio, csv, os, re, unicodedata
from pathlib import Path
from typing import List, Tuple
from urllib.parse import quote

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

HEADLESS = os.getenv("HEADLESS", "1") == "1"
CONCURRENCY = int(os.getenv("CONCURRENCY", "5"))
PAGE_TIMEOUT = int(os.getenv("PAGE_TIMEOUT", "30000"))
RETRIES = int(os.getenv("RETRIES", "2"))

OUT_CSV = "models_count.csv"
SITE = "automoto.com.lv"

BRANDS_RAW = r"""
2ППС
ABG Titan
AION
ALPINA
ATS Corsa
Abarth
Ackermann Fruehauf
Acura
Adler
Aero
Aiways
Alfa
Alfa Romeo
Alpine
Anaig
Aprilia
Aro
Asia
Aston Martin
Atlas
Audi
Avatr
Azimut
BAIC
BMW
BMW-Alpina
BOVA
BRP
BYD
Baojun
Barkas
Bayliner
Benelli
Bentley
BlueCar
Bobcat
Bomag
Brilliance
Bristol
Buick
CFMOTO
CUPRA
Cadillac
Capello
Caterpillar
Cenntro
ChAZ
Chana
Changan
Changfeng
Changhe
Chanje
Chery
Chevrolet
Chrysler
Citroёn
Cobra
Crownline
Cupra
DAF (VDL)
DKW
DS
Dacia
Dadi
Daewoo
Daf
Daihatsu
Defiant
Denza
Derways
Dodge
Dongfeng
Ducati
Eagle
Elwinn
Enovate
FAW
FCB
FSO
FUQI
Ferrari
Fiat
Fisker
Ford
Foton
GAZ
GMC
Gac
Geely
Genesis
Geo
Geon
Gilera
Gonow
Great Wall
Groz
HTZ
Hafei
Harley-Davidson
Haval
Honda
Hongqi
Huabei
Huanghai
Humbaur
Hummer
Husqvarna
Hyosung
Hyundai
IM
Ineos
Infiniti
Isuzu
Iveco
Izh
JAC
JCB
Jaguar
Jawa
Jeep
Jetour
Jinbei
KAMAZ
KTM
Kanuni
Kawasaki
Kaya
Kia
Kogel
Krone
Kubota
LADA
LAG
LDV
Lamborghini
Lancia
Land Rover
Landwind
Leapmotor
Leopard
Letin
Lexus
Li Auto
Lifan
Like.Bike
Lincoln
Link Tour
Lotus
Lovol
LuAZ
Lucid
Lucid Motors
MAG Trailer
MAN
MG
MINI
MPM Motors
MTD
Mahindra
Malaguti
Maserati
Maxus
Maxxter
Maybach
Mazda
McLaren
Mercedes-Benz
Mercury
Mitsubishi
Moto Guzzi
Mv agusta
Neoplan
Neta
New Holland
Nissan
Nysa
ORA
Oldsmobile
Opel
Pacton
Panav
Peugeot
Piaggio
Plymouth
Polaris
Polestar
Pontiac
Porsche
Powerboat
Pragmatec
Princess
Proton
Ram
Ravon
Raysince
Renault
Retro
Rivian
Roewe
Rolls-Royce
Rover
SAIPA
SCHMIDT
SEAT
SMA
Saab
Sabur
Samand
Samsung
Saturn
Scania
Schmitz
Schmitz Cargobull
Schwarzmuller
Scion
Segway
Senke
Shark
Shelby
Shuanghuan
Sinomach
Skoda
Skywell
Smart
SouEast
Soul
Sparta
Speed Gear
SsangYong
Subaru
Suzuki
TATA
TCM
Talbot
Temared
Tesla
Tianma
Toyota
Trabant
Tracker
Triumph
UAZ
VEGA
VIS
Venturi
VinFast
Viper
Voge
Volkswagen
Volvo
Voyah
Wanfeng
Wartburg
Weltmeister
Willys
Wuling
Xiaomi
Xinkai
Xpeng
YCF
Yamaha
Yema
YiBen
Yokomoto
ZAZ
ZIL
ZIM
ZX
Zastava
Zeekr
Zongshen
Zotye
Zubr
Zuk
moskvich-azlk
ІФА
Ікарус
Індокс
Індіан
Інтер Карс
А Ті Ві
АІМА
АБМ
АЛЕКО
Адвенчур
Адріа
Акербі
Ал-ко
Альфа
Аман
Амкодор
Арктік кет
Атаман
БАЗ
БСЄ
Баварія Яхтс
Баджадж
Балканкар
Башан
Беналу
Бергер
Бета
Блюмхардт
Бобер
Бобкет
Богдан
Бодекс
Болган
Бріг
Булат
Бург
ВДЛ
ВанХул
Вартбург
Вейліфтер
Вельтмейстер
Віелтон
Вікенд
Вікторі
Вілкокс
Вілліг
Віртген
ГРАС
Галеон
Гластрон
Голдхофер
Гофа
Гроне веген
Гєніє
Гідромек
ДС
Дельта
Деннісон
Десот
Детлефс
Дженерал Трейлерс
Дженміл
Джетур
Джіанше
Днепр
Дніпро
Дніпро-КМЗ
Доган
Дромеч
Дусан
ЕОС
Еверласт
Ексдрайв
Елєктро Скутєр
Енерко
Ес Ді Сі
Жук
ЗАЗ ЛуАЗ
ЗХ
Заслав
Зонтес
Зремб
Казанка
Кайо
Карді
Карнехл
Кассбохрер
Келберг
Кемпф
Кес Конструкшн
Кнапен
Кобелко
Кобо
Кові
Кодер
Коматсу
Комман
КрАЗ
Ківей
Кімко
Кінлон
ЛАЗ
ЛДС
Ламберет
Лангендорф
Лацінена
Лев
ЛесіТрейлер
Лида
Лонкін
Львівський навантажувач
Люсід
Лінде
Лінхай
ЛіуГонг
МАЗ
ММЗ
МОЛ
Магіар
Майрлінг
Максус
Маніту
Маісонью
Мейлер
Менчі
Мерцерон
Метако
Монтракон
Мото-Лідер
Мустанг
Мікілон
Мінськ
НПП Палич
Новатрейл
Нутебум
Нієвіадов
ОМТ
Ова
ПАВАМ
ПАЗ
ПВА
ПГМФ
ПП
ПРТ
Панав
Плімут
Полестар
Причіп
Прогрес
РАФ
РУТА
Райдер
Рам
Рейш
Рендерс
Робуст
Рохр
Рівіан
СВІФТ
СМЗ
СМТ
СТАС
Самро
СауІст
Сегвей
Сетра
СкайБайк
СкайМото
Соммер
Спайер
Спарк
Стокота
Стілл
Стім
Сумітомо
Сцион
Сім
ТАД
Табберт
Тадано
Татра
Теккен
Терекс
Трейлер
Трейлор
Троуілет
Тріумф
Тула мотоцикл
Українська мрія
Урал
Фада
Файмонвіль
Фелдбіндер
Флур
Флуід
Флігл
Фор Вінс
Форте
Фотон
Фрухауф
Фібер
Фінвал
ХАЗ
ХЦМГ
Хамер
Хамм
Хантер
Хаулот
Хафей
Хендрікс
Хоббі
Хово
Хонгда
Хорнет
Хістер
Цітококо
Чана
Чанган
Чезет
Чендж
Череау
Чінчі
ШМІДТ
Шанрай
Шпітцер
Южанка
Юнгхайнріх
Ютонг
Ява ЦЗ
Ядеа
Яле
Янмар
бус РАФ
катер Крим
катер СіРей
мото ВОСХОД
причіп ВАРЗ
причіп ГКБ
причіп Кремінь
причіп МЕГА
причіп Муравей
причіп ОДАЗ
причіп СЗАП
причіп Сантей
причіп ЧМЗАП
трактор ЧТЗ
човен Бустер
човен Колібрі
човен Обь
човен Скіф
човен ЮМС
ВАЗ
""".strip()

def dedupe_preserve_order(lines: List[str]) -> List[str]:
    seen, out = set(), []
    for x in lines:
        k = x.strip()
        if not k or k in seen: 
            continue
        seen.add(k); out.append(k)
    return out

BRANDS = dedupe_preserve_order(BRANDS_RAW.splitlines())

# --- slugify для URL бренду: максимально лояльний ---
def slugify(name: str) -> str:
    s = name.strip().lower()
    # нормалізація/транслітерація basic (прибираємо діакритику)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # кирилиця -> груба латинка (мінімальний маппінг для найтиповіших брендів)
    translit = {
        "мерседес": "mercedes", "бмв": "bmw", "тойота": "toyota", "хонда": "honda",
        "ниссан": "nissan", "форд": "ford", "мазда": "mazda", "ваз": "vaz", "лада": "lada",
        "вольво": "volvo", "ауди": "audi", "фольксваген": "volkswagen", "шкода": "skoda",
        "ренольт": "renault", "рено": "renault", "ситроен": "citroen", "дачия": "dacia",
        "хендай": "hyundai", "хаммер": "hummer"
    }
    for ru, lat in translit.items():
        if s.startswith(ru): s = s.replace(ru, lat, 1)
    # прибираємо все зайве
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    # деякі нормалізації (mercedes-benz, land-rover тощо лишаємо як є)
    return s

# шаблон лінків на моделі: /ru/bu-avto/<region>/{brandSlug}/{modelSlug}
MODEL_HREF_RE = re.compile(r"^/ru/bu-avto/[^/]+/([^/]+)/([^/]+)/?$", re.I)

async def count_models_for_brand(page, brand: str) -> Tuple[int, str]:
    slug = slugify(brand)
    # пробуємо латвійський каталог (найчастіший)
    url_candidates = [
        f"https://{SITE}/ru/bu-avto/latviya/{quote(slug)}",
        f"https://{SITE}/ru/bu-avto/{quote(slug)}",  # запасний
    ]
    last_err = None
    for url in url_candidates:
        try:
            await page.goto(url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
            await page.wait_for_timeout(800)

            # дістаємо всі href і фільтруємо regex-ом
            hrefs = await page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
            model_hrefs = set()
            for h in hrefs:
                if not h: 
                    continue
                m = MODEL_HREF_RE.match(h)
                if not m: 
                    continue
                brand_in_href = m.group(1).lower()
                if brand_in_href == slug:
                    model_hrefs.add(h)
            return len(model_hrefs), "ok"
        except PWTimeout as e:
            last_err = f"timeout:{type(e).__name__}"
        except Exception as e:
            last_err = f"error:{type(e).__name__}"
    return 0, (last_err or "not-found")

async def worker(brand: str, writer, sem, browser):
    async with sem:
        page = await browser.new_page()
        for attempt in range(1, RETRIES+1):
            try:
                cnt, status = await count_models_for_brand(page, brand)
                writer.writerow([brand, SITE, cnt, status])
                break
            except Exception as e:
                status = f"error:{type(e).__name__}"
                if attempt >= RETRIES:
                    writer.writerow([brand, SITE, 0, status])
        await page.close()

async def main():
    sem = asyncio.Semaphore(CONCURRENCY)
    write_header = not Path(OUT_CSV).exists()
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["brand", "site", "models_count", "status"])
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=HEADLESS)
            await asyncio.gather(*(worker(b, writer, sem, browser) for b in BRANDS))
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
