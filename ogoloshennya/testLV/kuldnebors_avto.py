# -*- coding: utf-8 -*-
# kuldnebors_batch.py
# Збирає Brand + Count зі сторінок kuldnebors.ee → kuldnebors_brands_counts.csv

import re
import csv
import time
from pathlib import Path
from typing import List, Tuple, Optional
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── НАЛАШТУВАННЯ ───────────────────────────────────────────────────────────────
URLS: List[str] = [
    "https://www.kuldnebors.ee/search/vehicles/cars/alfa-romeo/search.mec?pob_cat_id=11061&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/audi/search.mec?pob_cat_id=11049&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/bmw/search.mec?pob_cat_id=11050&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/buick/search.mec?pob_cat_id=11062&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/cadillac/search.mec?pob_cat_id=11063&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/chevrolet/search.mec?pob_cat_id=11064&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/chrysler/search.mec?pob_cat_id=11066&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/citroen/search.mec?pob_cat_id=11065&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/daihatsu/search.mec?pob_cat_id=11068&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/dodge/search.mec?pob_cat_id=11069&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/fiat/search.mec?pob_cat_id=11060&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/ford/search.mec?pob_cat_id=11053&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/honda/search.mec?pob_cat_id=11054&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/hyundai/search.mec?pob_cat_id=11070&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/jaguar/search.mec?pob_cat_id=11071&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/jeep/search.mec?pob_cat_id=11120&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/kia/search.mec?pob_cat_id=11121&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/lada/search.mec?pob_cat_id=11122&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/lancia/search.mec?pob_cat_id=11073&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/land-rover/search.mec?pob_cat_id=11123&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/lexus/search.mec?pob_cat_id=11124&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/mazda/search.mec?pob_cat_id=11056&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/mb/search.mec?pob_cat_id=11057&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/mitsubishi/search.mec?pob_cat_id=11074&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/nissan/search.mec?pob_cat_id=11075&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/opel/search.mec?pob_cat_id=11055&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/peugeot/search.mec?pob_cat_id=11077&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/pontiac/search.mec?pob_cat_id=11078&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/porsche/search.mec?pob_cat_id=11079&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/renault/search.mec?pob_cat_id=11080&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/rover/search.mec?pob_cat_id=11081&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/saab/search.mec?pob_cat_id=11082&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/seat/search.mec?pob_cat_id=11083&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/skoda/search.mec?pob_cat_id=11084&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/smart/search.mec?pob_cat_id=11413&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/subaru/search.mec?pob_cat_id=11085&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/suzuki/search.mec?pob_cat_id=11086&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/toyota/search.mec?pob_cat_id=11059&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/vw/search.mec?pob_cat_id=11052&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/volvo/search.mec?pob_cat_id=11058&pob_action=search",
    "https://www.kuldnebors.ee/search/vehicles/cars/other-makes/search.mec?pob_cat_id=11045&pob_action=search",
]
CSV_PATH = "vuvod/LV_kuldnebors_avto.csv"
HEADLESS = True          # якщо щось блокує — постав False
REQUEST_DELAY = 0.0      # пауза між URL
MAX_TIMEOUT = 40_000     # мс
INCLUDE_URL = False      # True -> третя колонка URL
# ───────────────────────────────────────────────────────────────────────────────

SEL_H1 = "h1"  # на сторінці brand у звичайному <h1>
SEL_SEARCH_BTN = "#search_do_search, a.kb-search-form__search-button"

def is_valid_url(u: str) -> bool:
    if not u:
        return False
    p = urlparse(u.strip())
    return p.scheme in ("http", "https") and bool(p.netloc)

def digits(text: Optional[str]) -> str:
    if not text:
        return "?"
    m = re.search(r"\d[\d\s]*", text)
    return m.group(0).replace(" ", "") if m else "?"

def get_brand(page) -> str:
    # беремо перший видимий h1
    page.wait_for_selector(SEL_H1, timeout=8000, state="attached")
    for i in range(page.locator(SEL_H1).count()):
        t = (page.locator(SEL_H1).nth(i).text_content() or "").strip()
        if t:
            return " ".join(t.split())
    return ""

def get_count(page) -> str:
    # з кнопки пошуку: "ПОИСК (32)" / "OTSING (32)"
    if page.locator(SEL_SEARCH_BTN).count():
        txt = page.locator(SEL_SEARCH_BTN).first.text_content() or ""
        c = digits(txt)
        if c != "?":
            return c
    # запасний варіант — пошук у всьому документі
    c2 = digits(page.content())
    return c2

def process_url(page, url: str) -> Tuple[str, str]:
    page.goto(url, wait_until="domcontentloaded", timeout=MAX_TIMEOUT)
    # інколи кнопка формується скриптом — невелика пауза
    page.wait_for_timeout(300)
    brand = get_brand(page)
    cnt = get_count(page)
    return brand, cnt

def main():
    urls = [u.strip() for u in URLS if is_valid_url(u)]
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"),
            viewport={"width": 1366, "height": 900},
            locale="ru-RU",
            ignore_https_errors=True,
        )
        page = ctx.new_page()

        for i, url in enumerate(urls, 1):
            try:
                brand, cnt = process_url(page, url)
                row = {"Brand": brand, "Count": cnt}
                if INCLUDE_URL:
                    row["URL"] = url
                rows.append(row)
                print(f"{brand} {cnt}")  # хочеш — прибереш цей рядок
            except PWTimeout:
                Path(f"kb_debug_{i}.html").write_text(page.content(), encoding="utf-8")
                page.screenshot(path=f"kb_debug_{i}.png", full_page=True)
                print(f"TIMEOUT → kb_debug_{i}.* збережено")
            except Exception as e:
                print(f"ERROR: {e}")
            time.sleep(REQUEST_DELAY)

        browser.close()

    fields = ["Brand", "Count"] + (["URL"] if INCLUDE_URL else [])
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        w.writerows(rows)

    print(f"\n✅ Дані збережено у {CSV_PATH}")

if __name__ == "__main__":
    main()
