from playwright.sync_api import sync_playwright
import csv

URL = "https://www.ss.lv/ru/transport/cars/"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)

        rows = []
        for h4 in page.locator("h4.category").all():
            brand = h4.locator("a.a_category").inner_text().strip()
            count = h4.locator("span.category_cnt").inner_text().strip("()")
            rows.append([brand, count])

        print(f"Зібрано брендів: {len(rows)}")
        for b, c in rows[:10]:
            print(f"{b} {c}")

        with open("vuvod/sslv_avto.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Brand", "Count"])
            w.writerows(rows)

        browser.close()
        print("✅ Дані збережено у vuvod/sslv_avto.csv")

if __name__ == "__main__":
    main()
