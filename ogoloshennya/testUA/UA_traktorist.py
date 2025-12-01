# traktorist_brand_counts_fix.py
# -*- coding: utf-8 -*-

import csv
import requests

URL = "https://traktorist.ua/api/filters/catalog/counters?page=1"
OUT = "vuvod/UA_traktorist.csv"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://traktorist.ua/",
}

# якщо хочеш «олюднити» ключі типу "metal-fach" -> "Metal Fach"
PRETTY_NAMES = True
def pretty(name: str) -> str:
    return name.replace("-", " ").strip().title()

def main():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    brand = data.get("brand")
    if not isinstance(brand, dict):
        raise SystemExit("⚠️ У відповіді немає об'єкта 'brand' (очікував dict).")

    rows = []
    for k, v in brand.items():
        name = pretty(k) if PRETTY_NAMES else k
        try:
            cnt = int(v)
        except Exception:
            cnt = 0
        rows.append((name, cnt))

    # відсортуємо за назвою
    rows.sort(key=lambda x: x[0].lower())

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Brand", "Count"])
        w.writerows(rows)

    # консольний вивід
    for name, cnt in rows:
        print(f"{name}: {cnt}")

    print(f"\n✅ Збережено у файл: {OUT}")

if __name__ == "__main__":
    main()
