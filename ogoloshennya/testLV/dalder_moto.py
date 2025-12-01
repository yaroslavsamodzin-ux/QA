# -*- coding: utf-8 -*-
# dalder_batch.py
# Збирає всі Brand + Count зі сторінок dalder.lv → dalder_brands_counts.csv

import re
import csv
import time
from pathlib import Path
from typing import List, Dict
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── НАЛАШТУВАННЯ ───────────────────────────────────────────────────────────────
URLS: List[str] = [
    "https://www.dalder.lv/motocikly",      # RU список марок
    # Можеш додати інші розділи/мови, наприклад:
    # "https://www.dalder.lv/en/cars",
]
CSV_PATH = "LV_dalder_moto.csv"
HEADLESS = True
REQUEST_DELAY = 0.4
MAX_TIMEOUT = 40_000  # мс
PRINT_TO_CONSOLE = True   # False → повна тиша
# ───────────────────────────────────────────────────────────────────────────────

# На сторінці кожна марка — це <a class="category-link">Alfa Romeo (8)</a>
SEL_BRAND_LINKS = "a.category-link"

COOKIE_BTNS = [
    "#onetrust-accept-btn-handler",
    "button:has-text('Соглас')", "button:has-text('Accept')",
    "button:has-text('Piekrītu')", "button:has-text('Nõustun')",
    "button:has-text('OK')",
]

def valid_url(u: str) -> bool:
    u = (u or "").strip()
    p = urlparse(u)
    return p.scheme in ("http", "https") and bool(p.netloc)

def digits(text: str) -> str:
    m = re.search(r"\d[\d\s]*", text or "")
    return m.group(0).replace(" ", "") if m else "?"

def extract_brand_and_count(text: str) -> Dict[str, str]:
    # очікуємо "Brand (123)" або "Brand(123)"
    text = " ".join((text or "").split())
    m = re.match(r"^(.*?)(?:\s*\(([\d\s]+)\))?$", text)
    brand = (m.group(1) or "").strip()
    count = digits(m.group(2) or "") if m else "?"
    return {"Brand": brand, "Count": count}

def click_cookies(page):
    for sel in COOKIE_BTNS:
        try:
            loc = page.locator(sel).first
            if loc.is_visible():
                loc.click()
                break
        except Exception:
            pass

def process_page(page, url: str) -> List[Dict[str, str]]:
    try:
        page.goto(url, wait_until="networkidle", timeout=MAX_TIMEOUT)
    except PWTimeout:
        page.goto(url, wait_until="domcontentloaded", timeout=MAX_TIMEOUT)
    click_cookies(page)

    page.wait_for_selector(SEL_BRAND_LINKS, state="attached", timeout=10_000)

    rows: List[Dict[str, str]] = []
    links = page.locator(SEL_BRAND_LINKS)
    n = links.count()
    for i in range(n):
        txt = (links.nth(i).text_content() or "").strip()
        if not txt:
            continue
        rows.append(extract_brand_and_count(txt))
    return rows

def main():
    urls = [u for u in URLS if valid_url(u)]
    all_rows: List[Dict[str, str]] = []

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
                rows = process_page(page, url)
                all_rows.extend(rows)
                if PRINT_TO_CONSOLE:
                    for r in rows:
                        print(f"{r['Brand']} {r['Count']}")
            except Exception as e:
                Path(f"dalder_debug_{i}.html").write_text(page.content(), encoding="utf-8")
                page.screenshot(path=f"dalder_debug_{i}.png", full_page=True)
                print(f"ERROR on #{i}: {e} → saved dalder_debug_{i}.*")
            time.sleep(REQUEST_DELAY)

        browser.close()

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Brand", "Count"], delimiter=";")
        w.writeheader()
        w.writerows(all_rows)

    print(f"\n✅ Дані збережено у {CSV_PATH} (всього {len(all_rows)} рядків)")

if __name__ == "__main__":
    main()
