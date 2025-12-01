#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automoto.com.lv (RU): збір кількості оголошень по марках.
- Вхід: id_automoto.txt з рядками "Марка;ID"
- Перехід: https://automoto.com.lv/ru/avto?filter%5Bused%5D=&filter%5Bmark%5D=260
           (структуру URL НЕ змінюємо, міняємо лише ID)
- Вивід у консоль: "Марка - Кількість"
- Збереження у CSV UTF-8 з delimiter ';' -> automoto_counts.csv
"""

import csv
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

INPUT_FILE  = "automoto_brands_v2.txt"
OUTPUT_FILE = "vuvod/LV_automoto.csv"

# ВАЖЛИВО: структура посилання незмінна. Міняється лише ID.
BASE_URL = "https://automoto.com.lv/ru/avto?filter%5Bused%5D=&filter%5Bmark%5D={id}"

# витягуємо число з різних варіацій написання, з урахуванням пробілів/nbsp
NUM_RE = re.compile(r"(\d[\d\u00a0\u202f ]*)")

def read_brands(path: str):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(";")]
            if len(parts) < 2:
                continue
            brand = parts[0]
            id_ = "".join(ch for ch in parts[1] if ch.isdigit())
            if id_:
                rows.append((brand, id_))
    return rows

def parse_int(s: str) -> int:
    m = NUM_RE.search(s or "")
    if not m:
        return 0
    return int(m.group(1).replace(" ", "").replace("\u00a0", "").replace("\u202f", ""))

def get_total_count(page) -> int:
    """
    Прагматичний витяг лічильника:
    1) поширені селектори лічильника
    2) текстові фрази ("Найдено", "Объявлений" тощо)
    Повертає 0, якщо нічого не знайшли.
    """
    selectors = [
        # типові місця для "знайдено N" / "объявлений (N)"
        ".results-count",
        ".search-count",
        ".search__count",
        ".list-search__count",
        ".search-results-count",
        "span.count",
        "span.result-count",
        "h1 .count",
        "h1 .result-count",
        "h1 span",
    ]
    for sel in selectors:
        try:
            if page.locator(sel).count() > 0:
                txt = page.locator(sel).first.text_content(timeout=2000)
                if txt:
                    n = parse_int(txt)
                    if n > 0:
                        return n
        except Exception:
            pass

    # спроба знайти по ключових словах у всьому документі
    try:
        body_text = page.locator("body").inner_text(timeout=2000)
        # часті формулювання: "Найдено", "объявлений", "объявления", "результатов"
        for kw in ["Найдено", "объявлен", "результат", "Показано", "найдено"]:
            if kw.lower() in body_text.lower():
                n = parse_int(body_text)
                if n > 0:
                    return n
    except Exception:
        pass

    return 0

def main():
    brands = read_brands(INPUT_FILE)
    if not brands:
        print("❌ Файл порожній або має неправильний формат (очікується 'Марка;ID').")
        return

    out_path = Path(OUTPUT_FILE)
    with out_path.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout, delimiter=';')

        with sync_playwright() as p:
            # headful, як ти любиш (можеш змінити на headless=True за потреби)
            browser = p.chromium.launch(headless=True, args=["--start-maximized", "--disable-dev-shm-usage"])
            context = browser.new_context(
                locale="ru-RU",
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/141.0.0.0 Safari/537.36"),
            )
            page = context.new_page()

            print(f"Загалом: {len(brands)} брендів\n")

            for i, (brand, id_) in enumerate(brands, 1):
                url = BASE_URL.format(id=id_)
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    # невеличка пауза на ініціалізацію сторінки
                    page.wait_for_timeout(300)

                    # Додаткові спроби дочекатися потенційного елемента-лічильника
                    for sel in ["h1", ".results-count", ".search-count", "span.count", "span.result-count"]:
                        try:
                            page.wait_for_selector(sel, timeout=1)
                        except Exception:
                            pass

                    count = get_total_count(page)

                    print(f"{brand} - {count}")
                    writer.writerow([brand, count])

                except PWTimeout:
                    print(f"{brand} - 0 (timeout)")
                    writer.writerow([brand, 0])
                except Exception as e:
                    print(f"{brand} - 0 (error)")
                    writer.writerow([brand, 0])

                time.sleep(0.25)

            browser.close()

    print(f"\n✅ Готово! Результат збережено у: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
