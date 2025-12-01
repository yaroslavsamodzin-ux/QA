# okidoki_counts_playwright.py
import csv
import re
import time
from typing import List, Tuple, Optional

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

INPUT_FILE  = "id_okidoki.txt"      # рядок: Audi;1343
OUTPUT_FILE = "vuvod/okidoki.csv"  # результат: brand;count
BASE_URL    = "https://www.okidoki.ee/ru/buy/1601/?c13={brand_id}"

INT_RE = re.compile(r"(\d[\d\u00A0\s]*)")

def read_input(path: str) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().lstrip("\ufeff")
            if not line or ";" not in line or line.startswith("#"):
                continue
            b, i = line.split(";", 1)
            b, i = b.strip(), i.strip()
            if b and i:
                pairs.append((b, i))
    return pairs

def _to_int(text: str) -> Optional[int]:
    m = INT_RE.search(text or "")
    if not m:
        return None
    num = m.group(1).replace(" ", "").replace("\u00A0", "")
    try:
        return int(num)
    except ValueError:
        return None

def extract_count(page) -> Optional[int]:
    # 1) meta description / og:description
    for sel in [
        'meta[name="description"]',
        'meta[property="og:description"]',
        'meta[name="og:description"]',
    ]:
        content = page.evaluate("""sel => {
            const el = document.querySelector(sel);
            return el ? el.getAttribute('content') : null;
        }""", sel)
        if content:
            v = _to_int(content)
            if v is not None:
                return v

    # 2) .found span
    try:
        span_text = page.locator(".found span").first.inner_text(timeout=500)
        v = _to_int(span_text)
        if v is not None:
            return v
    except PWTimeout:
        pass

    # 3) .adsCounter
    try:
        cnt_text = page.locator(".adsCounter").first.inner_text(timeout=500)
        v = _to_int(cnt_text)
        if v is not None:
            return v
    except PWTimeout:
        pass

    return None

def main():
    pairs = read_input(INPUT_FILE)
    if not pairs:
        print("У вхідному файлі немає пар brand;id")
        return

    out_rows: List[Tuple[str, int]] = []
    errors: List[Tuple[str, str, str]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            locale="ru-RU",
        )
        page = context.new_page()

        for brand, bid in pairs:
            url = BASE_URL.format(brand_id=bid)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                # Дочекаймося, поки Cloudflare/JS відпрацює
                page.wait_for_timeout(600)  # легкий grace-period
                cnt = extract_count(page)
                if cnt is None:
                    # спробуємо ще раз після трохи довшого очікування
                    page.wait_for_timeout(1000)
                    cnt = extract_count(page)
                if cnt is None:
                    errors.append((brand, bid, "count_not_found"))
                    cnt = 0
            except Exception as e:
                errors.append((brand, bid, str(e)))
                cnt = 0

            out_rows.append((brand, cnt))
            time.sleep(0.3)  # чемно до сайту

        browser.close()

    # CSV UTF-8 із ; як розділювачем
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["brand", "count"])
        w.writerows(out_rows)

    print(f"✅ Збережено {len(out_rows)} рядків → {OUTPUT_FILE}")
    if errors:
        print(f"⚠️ Помилки/порожні значення: {len(errors)}")
        # Розкоментуй для діагностики:
        # for b, i, msg in errors:
        #     print(b, i, msg)

if __name__ == "__main__":
    main()
