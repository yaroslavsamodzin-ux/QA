# mmlvavto.py
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import re, csv

START_URL  = "https://mm.lv/transport"
OUT_CSV    = "vuvod/mmlv_avto.csv"
HEADLESS   = False
NAV_TIMEOUT = 45_000

BRAND_URL_RE = re.compile(r"^https?://mm\.lv/[a-z0-9\-]+-ru$", re.I)  # лише бренди

def clean_brand(s: str) -> str:
    return re.sub(r"[›»«→]", "", (s or "")).strip()

def main():
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()
        page.goto(START_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)

        # кукі-банер (якщо є)
        for txt in ("Согласен", "Piekrītu", "Accept"):
            try:
                page.get_by_text(txt, exact=False).first.click(timeout=12000)
                break
            except Exception:
                pass

        # Знаходимо заголовок категорії "Легковые авто"
        header = page.locator("a.category", has_text="Легковые авто").first
        if not header.count():
            print("[ERR] Не знайдено заголовок 'Легковые авто'")
            browser.close()
            return

        # Обмежимо пошук тільки брендами в межах блоку після заголовка
        # Беремо всі посилання під цим блоком і відфільтровуємо по шаблону бренду
        # (це простіше і надійніше, ніж намагатися жорстко вгадувати контейнер)
        anchors = page.locator("a.subcat").all()

        for a in anchors:
            href = a.get_attribute("href") or ""
            if not href:
                continue

            abs_url = urljoin(page.url, href)

            # Фільтр: тільки lінки виду https://mm.lv/<brand>-ru
            if not BRAND_URL_RE.match(abs_url):
                continue

            brand = clean_brand(a.inner_text())
            # кількість із data-c
            data_c = a.get_attribute("data-c") or "0"
            try:
                count = int(re.sub(r"\D", "", data_c))
            except Exception:
                count = 0

            rows.append({"Brand": brand, "Count": count})
            print(f"{brand} {count}")

        browser.close()

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Brand", "Count"], delimiter=";")
        w.writeheader()
        w.writerows(rows)

    print(f"✅ CSV → {OUT_CSV} (rows {len(rows)})")

if __name__ == "__main__":
    main()
