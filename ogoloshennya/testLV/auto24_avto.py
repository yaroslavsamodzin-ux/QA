# -*- coding: utf-8 -*-
"""
Збирає Brand + Count зі сторінок rus.auto24.lv і пише у results_auto24.csv
Працює через реальний браузер (Playwright), щоб обійти Cloudflare/anti-bot.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeoutError
import csv
import re
from time import sleep

URLS = [
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1655&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=9&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=372&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=149&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=2&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=247&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=4&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=38&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1148&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=44&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=31&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=28&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=20&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1434&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=254&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=55&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=418&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1714&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=24&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1259&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=70&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=14&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=713&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=7&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=45&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=54&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1671&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=193&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=34&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=255&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=26&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=443&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=36&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=32&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=25&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=18&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=376&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=37&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=42&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=35&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=76&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=29&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1397&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=60&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1657&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=378&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=6&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=751&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1470&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=12&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=379&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1154&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=144&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=3&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=181&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=11&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=5&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=16&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1483&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=71&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=140&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1162&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=19&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=168&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=30&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=17&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=22&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1361&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=40&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1574&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=102&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=39&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=23&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=41&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1282&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=642&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=13&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=225&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=105&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=52&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=8&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=10&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=232&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=101&aj=&b=1729&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA", 
]

SEL_COUNT = "div.current-range span.label strong"
SEL_BRAND_OPT = 'select[id*="searchParam-cmn-1-make"] option[selected]'
SEL_BRAND_CHIP = '#item-searchParam-cmn-1-make .search-filter'

def clean_brand(s: str) -> str:
    if not s: return ""
    s = " ".join(s.replace("\xa0"," ").split())
    s = re.sub(r"\s*легков(ой|ые)\s+автомобил(ь|и)\s*$", "", s, flags=re.I).strip()
    return s

def digits(s: str) -> str:
    m = re.search(r"\d+", s or "")
    return m.group(0) if m else "?"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36")
    )

    rows = []
    for url in URLS:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        if "Attention Required" in page.content():
            print("Марка: ? | Кількість: ? (Cloudflare)")
            continue

        # Count
        count = digits(page.locator(SEL_COUNT).first.inner_text()) if page.locator(SEL_COUNT).count() else "?"

        # Brand
        if page.locator(SEL_BRAND_OPT).count():
            brand = page.locator(SEL_BRAND_OPT).first.inner_text().strip()
        elif page.locator(SEL_BRAND_CHIP).count():
            brand = page.locator(SEL_BRAND_CHIP).first.inner_text().strip()
        else:
            brand = re.split(r"[-–|•()]", (page.title() or ""))[0].strip()
        brand = clean_brand(brand)
        if not brand:  # пропускаємо “Легковой автомобиль”
            continue

        print(f"{brand} {count}")
        rows.append([brand, count])

    browser.close()

with open("vuvod/LV_auto24_avto.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Brand", "Count"])
            w.writerows(rows)

print("\n✅ Дані збережено у vuvod/LV_auto24_avto.csv")