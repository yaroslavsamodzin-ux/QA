# tests/mm_lv_moto_brand_counts.py
# pip install playwright
# python -m playwright install

from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import re, csv

START_URL  = "https://mm.lv/mototsikly-agusta"
OUT_CSV    = "mmlv_moto.csv"
HEADLESS   = True
NAV_TIMEOUT = 45_000

def clean_brand(text: str) -> str:
    # прибрати декоративні символи типу «›», «»» тощо
    return re.sub(r"[›»«→]", "", (text or "")).strip()

def main():
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(locale="ru-RU")
        page = ctx.new_page()

        page.goto(START_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)

        # Прибрати кукі-банер, якщо заважає
        for txt in ("Согласен", "Piekrītu", "Accept"):
            try:
                page.get_by_text(txt, exact=False).first.click(timeout=1200)
                break
            except Exception:
                pass

        # Усі пункти лівих колонок-брендів: <a class="subcat" ... data-c="N">
        # (фільтруємо тільки посилання на мотокатегорії, щоб не брати «аренда/запчасти/аксессуары»)
        page.wait_for_selector("div.search-cat-list a.subcat", timeout=NAV_TIMEOUT)
        anchors = page.locator("div.search-cat-list a.subcat").all()

        for a in anchors:
            href  = a.get_attribute("href") or ""
            if not href:
                continue
            abs_url = urljoin(page.url, href)

            # беремо тільки підкатегорії мотоциклів (у них шлях вигляду /mototsikly-xxx)
            path = urlparse(abs_url).path or ""
            if "/mototsikly-" not in path:
                continue

            brand = clean_brand(a.inner_text())
            # якщо текст пустий — зробимо бренд зі слага в URL
            if not brand:
                slug = path.rsplit("/", 1)[-1].replace("mototsikly-", "").replace("-", " ")
                brand = slug.title()

            # кількість беремо з data-c
            data_c = a.get_attribute("data-c") or "0"
            try:
                count = int(re.sub(r"\D", "", data_c))
            except Exception:
                count = 0

            rows.append({"Brand": brand, "Count": count, "URL": abs_url})
            print(f"{brand} {count}")

        browser.close()

    # CSV
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Brand", "Count", "URL"], delimiter=";")
        w.writeheader()
        w.writerows(rows)

    print(f"✅ CSV → {OUT_CSV} (rows {len(rows)})")

if __name__ == "__main__":
    main()
