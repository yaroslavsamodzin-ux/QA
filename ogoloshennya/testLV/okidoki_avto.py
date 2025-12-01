# okidoki_brand_page.py
# pip install playwright
# python -m playwright install

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import csv, re

URLS = [
    "https://www.okidoki.ee/ru/buy/1601/?c13=1221",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1233",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1288",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1329",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1343",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1444",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1459",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1506",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1529",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1575",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1617",
    "https://www.okidoki.ee/ru/buy/1601/?c13=4553",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1670",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1717",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1786",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1808",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1812",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1849",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1866",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1868",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1886",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1898",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1935",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1981",
    "https://www.okidoki.ee/ru/buy/1601/?c13=1996",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2027",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2032",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2078",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2113",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2353",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2359",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2403",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2442",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2506",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2546",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2595",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2614",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2638",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2696",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2729",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2740",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2754",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2771",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2782",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2790",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2806",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2837",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2838",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2896",
    "https://www.okidoki.ee/ru/buy/1601/?c13=2946",
    "https://www.okidoki.ee/ru/buy/1601/?c13=3018",
    "https://www.okidoki.ee/ru/buy/1601/?c13=3019",
    "https://www.okidoki.ee/ru/buy/1601/?c13=4455",
    "https://www.okidoki.ee/ru/buy/1601/?c13=4368",
]

OUT_CSV   = "vuvod/LV_okidoki_avto.csv"
HEADLESS  = False
TIMEOUT   = 45_000

BRAND_SEL = "#current-category b"   # ліва колонка → <a id="current-category"><b>Acura</b></a>
COUNT_SEL = "p.found b"             # зверху → "<b>297</b> найдено ..."

def digits(text: str) -> str:
    m = re.search(r"\d[\d\s]*", text or "")
    return m.group(0).replace(" ", "") if m else "0"

def accept_cookies(page):
    for s in ("#onetrust-accept-btn-handler",
              "button:has-text('Соглас')", "button:has-text('Accept')", "button:has-text('OK')"):
        try:
            btn = page.locator(s).first
            if btn.is_visible(): btn.click(); break
        except Exception:
            pass

with sync_playwright() as p:
    br = p.chromium.launch(headless=HEADLESS)
    page = br.new_page(
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"),
        viewport={"width": 1366, "height": 900},
        locale="ru-RU",
        ignore_https_errors=True,
    )

    rows = []
    for url in URLS:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT)
        except PWTimeout:
            page.goto(url, timeout=TIMEOUT)

        accept_cookies(page)

        # чекаємо, поки з'являться ключові елементи
        page.wait_for_selector(BRAND_SEL, timeout=TIMEOUT)
        page.wait_for_selector(COUNT_SEL, timeout=TIMEOUT)

        brand = (page.locator(BRAND_SEL).first.text_content() or "").strip()
        count = digits(page.locator(COUNT_SEL).first.text_content())

        rows.append({"Brand": brand, "Count": count})
        print(f"{brand} {count}")

    br.close()

with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["Brand", "Count"], delimiter=";")
    w.writeheader(); w.writerows(rows)

print(f"✅ Дані збережено у {OUT_CSV} (всього {len(rows)} рядків)")
