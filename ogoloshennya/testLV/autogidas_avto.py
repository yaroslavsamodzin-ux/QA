# -*- coding: utf-8 -*-
# autogidas_batch.py
# Збирає Brand + Count зі сторінок autogidas.lt і пише у autogidas_brands_counts.csv

import re
import csv
import time
from pathlib import Path
from typing import Tuple, Optional, List
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── НАЛАШТУВАННЯ ───────────────────────────────────────────────────────────────
URLS: List[str] = [
    # <<< СЮДИ ДОДАВАЙ СТОРІНКИ >>>
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_1%5B0%5D=Volkswagen&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=BMW&f_model_14%5B0%5D=", 
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Audi&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_1%5B0%5D=Opel&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_376=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_1%5B0%5D=Mercedes-Benz&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_376=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Toyota&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Ford&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Volvo&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Skoda&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Peugeot&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Nissan&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Renault&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Hyundai&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Seat&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Kia&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Citroen&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Mazda&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Subaru&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Honda&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Jeep&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Mitsubishi&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Chevrolet&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Land+Rover&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Porsche&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Lexus&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Dodge&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Fiat&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Suzuki&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Chrysler&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=MINI&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Tesla&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Jaguar&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Dacia&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Cupra&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Alfa+Romeo&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Saab&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Infiniti&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Lada&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Maserati&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Cadillac&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Ssangyong&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Iveco&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Buick&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Daihatsu&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Moskvich&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Lincoln&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=GAZ&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Acura&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Bentley&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=MG&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Pontiac&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=DS+Automobiles&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=GMC&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Isuzu&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Lancia&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_1%5B0%5D=Rolls-Royce&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Rover&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=ZAZ&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Aixam&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Alpina&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Ligier&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Mercury&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Polestar&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Aston+Martin&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Daewoo&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Ferrari&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Lamborghini&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Man&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Maybach&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=McLaren&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Microcar&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Tata&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Abarth&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Casalini&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Hongqi&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=JAC&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Lotus&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=LuAZ&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Piaggio&f_model_14%5B0%5D=",
    "https://autogidas.lt/ru/skelbimai/automobiliai/?f_215=&f_216=&f_41=&f_42=&f_376=&f_1%5B0%5D=Scion&f_model_14%5B0%5D=",
]
CSV_PATH = "vuvod/LV_autogidas_avto.csv"
HEADLESS = False           # якщо антибот заважає — постав False
REQUEST_DELAY = 1       # пауза між URL, щоб швидше (можеш 0.0..1.0)
MAX_TIMEOUT = 60_000      # мс
INCLUDE_URL = False       # True → додасть у CSV третю колонку URL
QUIET = False              # True → мінімальний вивід у консоль
# ───────────────────────────────────────────────────────────────────────────────

def accept_cookies(page) -> None:
    sels = [
        "#onetrust-accept-btn-handler",
        "button:has-text('Sutinku')", "button:has-text('Piekrītu')",
        "button:has-text('Соглас')",  "button:has-text('Accept')",
        "button:has-text('OK')",
    ]
    for s in sels:
        try:
            loc = page.locator(s).first
            if loc.is_visible():
                loc.click()
                break
        except Exception:
            pass

def digits_int(text: Optional[str]) -> int:
    m = re.search(r"\d[\d\s]*", text or "")
    return int(m.group(0).replace(" ", "")) if m else 0

def extract_brand_from_h1(page) -> str:
    # прибираємо (2973) у вкладеному <span class="ads-total"> з H1
    page.evaluate("""() => {
        document.querySelectorAll('h1.title span.ads-total').forEach(s=>s.remove());
    }""")
    t = (page.locator("h1.title").first.text_content() or "").strip()
    # відсікаємо службові слова
    return re.split(r"\s+(Автомобили|Automobiliai|Авто)\b", t)[0].strip()

def process_url(page, url: str) -> Tuple[str, int]:
    # швидше, ніж networkidle
    page.goto(url, wait_until="domcontentloaded", timeout=MAX_TIMEOUT)
    accept_cookies(page)

    # чекаємо не 60 сек, а максимум 5
    page.wait_for_selector("h1.title", timeout=5000)

    # ads-total може бути невидимий — чекаємо появу в DOM
    ads = page.locator("span.ads-total").first
    ads.wait_for(state="attached", timeout=5000)
    count = digits_int(ads.text_content())

    # бренд з чіпа активного фільтра; якщо нема — з H1
    brand = (page.locator("#active-filters-wrapper .filter-value")
             .first.text_content() or "").strip()
    if not brand:
        brand = extract_brand_from_h1(page)

    return brand, count

def main():
    rows: List[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(
            locale="ru-RU",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"),
            viewport={"width": 1366, "height": 900},
            ignore_https_errors=True,
        )
        page = ctx.new_page()

        for url in URLS:
            try:
                brand, count = process_url(page, url)
                row = {"Brand": brand, "Count": count}
                if INCLUDE_URL:
                    row["URL"] = url
                rows.append(row)
                if not QUIET:
                    # короткий вивід; або прибери цей print, якщо треба повна тиша
                    print(f"{brand} {count}" + (f";{url}" if INCLUDE_URL else ""))
            except PWTimeout:
                # збережемо артефакти для дебагу конкретного URL
                Path("debug.html").write_text(page.content(), encoding="utf-8")
                page.screenshot(path="debug.png", full_page=True)
                if not QUIET:
                    print("TIMEOUT → збережено debug.html / debug.png")
            except Exception as e:
                if not QUIET:
                    print(f"ERROR: {e}")

            time.sleep(REQUEST_DELAY)

        browser.close()

    # запис у CSV (крапка з комою)
    fieldnames = ["Brand", "Count"] + (["URL"] if INCLUDE_URL else [])
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    if not QUIET:
        print(f"\n✅ Дані збережено у {CSV_PATH}")

if __name__ == "__main__":
    main()
