# -*- coding: utf-8 -*-
# kuldnebors_batch.py
# Збирає Brand + Count зі сторінок kuldnebors.ee → kuldnebors_moto.csv

import re
import csv
import time
from pathlib import Path
from typing import List, Tuple, Optional
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── НАЛАШТУВАННЯ ───────────────────────────────────────────────────────────────
URLS: List[str] = [
    # приклад мото з виставленою маркою
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1048",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&pob_cat_id=11050&search_C_make_id=1002",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1173",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1154",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1061",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1062",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1163",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1070",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&pob_cat_id=11054&search_C_make_id=1014",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1155",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1065",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1077",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1078",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1079",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1081",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1086",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1093",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1099",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1101",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1167",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1152",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&pob_cat_id=11086&search_C_make_id=1036",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1170",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1123",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1156",
    "https://www.kuldnebors.ee/search/search.mec?search_evt=onsearch&search_X_cat_ids=10705&pob_action=search&search_C_make_id=1127",
]
CSV_PATH = "LV_kuldnebors_moto.csv"
HEADLESS = True
REQUEST_DELAY = 0.0
MAX_TIMEOUT = 40_000
INCLUDE_URL = False
# ───────────────────────────────────────────────────────────────────────────────

SEL_H1_VISIBLE = "h1:visible"
SEL_SEARCH_BTN = "#search_do_search, a.kb-search-form__search-button"
SEL_MAKE_SELECT = 'select[name*="make_id"]'
SEL_FILTER_CHIP = ".kb-filter-tag, .kb-selected-filter, .kb-chip"

CATEGORY_WORDS = {
    # службові заголовки/категорії різними мовами
    "Mootorrattad", "Sõiduautod", "Autod", "Авто", "Легковые автомобили",
    "Transport", "Транспорт", "Vehicles", "Transporto priemonės",
}

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

def normalize_brand(title: str) -> str:
    t = (title or "").strip()
    # зрізаємо хвіст типу " (32)"
    t = re.sub(r"\s*\(\d[\d\s]*\)\s*$", "", t)
    # згортаємо пробіли
    t = " ".join(t.split())
    return t

def get_brand_from_select(page) -> str:
    if not page.locator(SEL_MAKE_SELECT).count():
        return ""
    try:
        txt = page.eval_on_selector(
            SEL_MAKE_SELECT,
            "el => (el.options && el.selectedIndex >= 0) ? el.options[el.selectedIndex].text : ''"
        ) or ""
        return normalize_brand(txt)
    except Exception:
        return ""

def get_brand_from_chips(page) -> str:
    chips = page.locator(SEL_FILTER_CHIP)
    if chips.count():
        txt = chips.first.inner_text() or ""
        # у чіпі може бути "Марка: Yamaha"
        txt = re.sub(r"^[^:]+:\s*", "", txt).strip()
        return normalize_brand(txt)
    return ""

def get_brand(page) -> str:
    # 1) спроба з видимого h1
    h1 = ""
    try:
        page.wait_for_selector(SEL_H1_VISIBLE, timeout=8000, state="visible")
        h1 = page.locator(SEL_H1_VISIBLE).first.inner_text() or ""
    except Exception:
        h1 = ""
    h1 = normalize_brand(h1)

    if h1 and h1 not in CATEGORY_WORDS and not re.match(r"^(Search|Poisk|Otsing)\b", h1, re.I):
        return h1

    # 2) вибрана опція бренду у select
    brand = get_brand_from_select(page)
    if brand:
        return brand

    # 3) чіпи/теги вибраних фільтрів
    brand = get_brand_from_chips(page)
    if brand:
        return brand

    # 4) запасний — meta og:title
    try:
        og = page.locator('meta[property="og:title"]').first.get_attribute("content") or ""
        og = normalize_brand(re.sub(r"\s*\(\d.*$", "", og))
        if og:
            return og
    except Exception:
        pass

    return h1 or ""

def get_count(page) -> str:
    # з кнопки "ПОИСК (32)" / "OTSING (32)"
    try:
        if page.locator(SEL_SEARCH_BTN).count():
            txt = page.locator(SEL_SEARCH_BTN).first.text_content() or ""
            c = digits(txt)
            if c != "?":
                return c
    except Exception:
        pass
    # запасний варіант — перше число в DOM
    return digits(page.content())

def process_url(page, url: str) -> Tuple[str, str]:
    page.goto(url, wait_until="domcontentloaded", timeout=MAX_TIMEOUT)
    page.wait_for_timeout(350)  # даємо JS домалюватись
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
                print(f"{brand} {cnt}")
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
