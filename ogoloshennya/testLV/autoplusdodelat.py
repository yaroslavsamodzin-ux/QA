# autoplius_one_brand.py
# pip install playwright
# python -m playwright install chromium

from playwright.sync_api import sync_playwright
import csv, re, time

URL = "https://ru.autoplius.lt/objavlenija/b-u-avtomobili?make_id=104"
OUT = "autoplius.csv"

def brand_from_title(t: str) -> str:
    # приклади: "Б/У автомобили (6) — Acura | Autoplius"
    m = re.search(r"автомобили.*?\)\s*[—\-]\s*([^|]+)", t, flags=re.I)
    return m.group(1).strip() if m else "?"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36")
        )

        # достатньо domcontentloaded
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)

        # чекаємо саме на футпринт заголовка зі лічильником
        page.wait_for_selector("div.search-list-title span.result-count", timeout=15000)

        # COUNT
        count = page.locator("div.search-list-title span.result-count").first.inner_text().strip("()")

        # BRAND: пробуємо точний селектор, потім кілька разів ще перевіряємо, потім fallback з title
        brand = "?"
        deadline = time.time() + 5  # до 5 сек на появу h3
        while brand == "?" and time.time() < deadline:
            loc = page.locator("div.search-list-title h3")
            if loc.count():
                txt = loc.first.inner_text().strip()
                if txt:
                    brand = txt
                    break
            page.wait_for_timeout(200)

        if brand == "?":           # запасний варіант
            brand = brand_from_title(page.title())

        print(f"{brand} | {count}")

        with open(OUT, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Brand", "Count"])
            w.writerow([brand, count])

        browser.close()
        print(f"✅ Дані збережено у {OUT}")

if __name__ == "__main__":
    main()
