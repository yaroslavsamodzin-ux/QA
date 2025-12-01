# -*- coding: utf-8 -*-
# motorfy_batch.py
# Збирає всі Brand + Count зі сторінок motorfy.lv/ru/lietoti-auto → motorfy_brands_counts.csv

import re
import csv
import time
from pathlib import Path
from typing import List, Dict
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── НАЛАШТУВАННЯ ───────────────────────────────────────────────────────────────
URLS: List[str] = [
    "https://motorfy.lv/ru/lietoti-auto",
    # можеш додати ще розділів, якщо є
]
CSV_PATH = "vuvod/LV_motorfy_avto.csv"
HEADLESS = True          # якщо вередує — постав False
REQUEST_DELAY = 0.4
MAX_TIMEOUT = 40_000     # мс
PRINT_TO_CONSOLE = True  # False → повна тиша
# ───────────────────────────────────────────────────────────────────────────────

SEL_BRAND_LINKS = "#main_make a"   # кожен <a> містить текст марки + <span>(N)
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

def click_cookies(page) -> None:
    for sel in COOKIE_BTNS:
        try:
            loc = page.locator(sel).first
            if loc.is_visible():
                loc.click()
                break
        except Exception:
            pass

def extract_brand_and_count_from_links(page) -> List[Dict[str, str]]:
    rows = []
    links = page.locator(SEL_BRAND_LINKS)
    n = links.count()
    for i in range(n):
        a = links.nth(i)
        # бренд = текст <a> без <span>(N)
        brand = a.evaluate("""el => {
            // беремо текст без вмісту всіх span
            const clone = el.cloneNode(true);
            clone.querySelectorAll('span').forEach(s => s.remove());
            return (clone.textContent || '').trim();
        }""")
        # кількість беремо зі span усередині <a>
        cnt_txt = (a.locator("span").first.text_content() or "") if a.locator("span").count() else ""
        count = digits(cnt_txt)

        if brand:
            rows.append({"Brand": " ".join(brand.split()), "Count": count})
    return rows

def process_page(page, url: str) -> List[Dict[str, str]]:
    # на сторінці є трохи JS, іноді зручніший networkidle
    try:
        page.goto(url, wait_until="networkidle", timeout=MAX_TIMEOUT)
    except PWTimeout:
        page.goto(url, wait_until="domcontentloaded", timeout=MAX_TIMEOUT)
    click_cookies(page)
    page.wait_for_selector(SEL_BRAND_LINKS, state="attached", timeout=10_000)
    return extract_brand_and_count_from_links(page)

def main():
    urls = [u.strip() for u in URLS if valid_url(u)]
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
                Path(f"motorfy_debug_{i}.html").write_text(page.content(), encoding="utf-8")
                page.screenshot(path=f"motorfy_debug_{i}.png", full_page=True)
                print(f"ERROR on #{i}: {e} → saved motorfy_debug_{i}.*")
            time.sleep(REQUEST_DELAY)

        browser.close()

    # запис у CSV (крапка з комою)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Brand", "Count"], delimiter=";")
        w.writeheader()
        w.writerows(all_rows)

    print(f"\n✅ Дані збережено у {CSV_PATH} (всього {len(all_rows)} рядків)")

if __name__ == "__main__":
    main()
