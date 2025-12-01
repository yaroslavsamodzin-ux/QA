#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Playwright (headless=False)
Формат збереження: CSV (UTF-8, delimiter=';')
Формат рядка: Марка;Кількість
"""

import csv
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

INPUT_FILE  = "urlsautoplus_avto.txt"
OUTPUT_FILE = "vuvod/LV_autoplius.csv"

BASE_URL = "https://ru.autoplius.lt/objavlenija/b-u-avtomobili?make_id={id}"
NUM_RE = re.compile(r"(\d[\d\s\u00a0\u202f]*)")

def read_brands(path):
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

def parse_count(text):
    m = NUM_RE.search(text or "")
    if not m:
        return 0
    return int(m.group(1).replace(" ", "").replace("\u00a0", "").replace("\u202f", ""))

def main():
    brands = read_brands(INPUT_FILE)
    if not brands:
        print("❌ Файл порожній або у неправильному форматі")
        return

    out_path = Path(OUTPUT_FILE)
    # Створюємо CSV з роздільником ';' і кодуванням UTF-8
    with out_path.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout, delimiter=';')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--start-maximized"])
            context = browser.new_context(locale="ru-RU")
            page = context.new_page()

            print(f"Загалом: {len(brands)} брендів\n")

            for i, (brand, id_) in enumerate(brands, 1):
                url = BASE_URL.format(id=id_)
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_selector("span.result-count", timeout=10000)
                    text = page.locator("span.result-count").first.text_content()
                    count = parse_count(text)

                    # консоль і файл — один і той самий формат
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

    print(f"\n✅ Завершено! Результат збережено у: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
