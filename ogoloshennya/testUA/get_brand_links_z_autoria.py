# -*- coding: utf-8 -*-
"""
Зчитує посилання з links_autoria.txt,
відкриває кожну сторінку, бере <h1> → витягує Brand і Count.
Результат: CSV з 2 колонками (Brand;Count)
"""

import re
import csv
import httpx
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse

# ===== Налаштування =====
IN_FILE = "links_autoria.txt"
OUT_CSV = "reports/UA_autoria.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36",
    "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8"
}


# ----- Допоміжні функції -----
def get_slug(url: str) -> str:
    """Витягує slug марки з URL."""
    p = urlparse(url)
    parts = [x for x in p.path.split("/") if x]
    return parts[-1] if parts else ""


def parse_count_and_brand(h1_text: str):
    """Витягує кількість і назву марки з тексту <h1>."""
    h1_clean = re.sub(r"\s+", " ", h1_text.strip())

    # шукаємо кількість
    count = None
    for pat in [
        r"\(([\d\s\u00A0]+)\)",                # (12 345)
        r"знайдено\s+([\d\s\u00A0]+)",         # знайдено 12 345
        r"([\d\s\u00A0]+)\s+оголош",           # 12 345 оголошень
    ]:
        m = re.search(pat, h1_clean, re.I)
        if m:
            count = int(re.sub(r"[^\d]", "", m.group(1)))
            break

    # прибираємо все після дужок
    brand = re.sub(r"\(.*?\)", "", h1_clean).strip()
    # прибираємо службові слова
    brand = re.sub(r"(?i)\b(авто|продаж|купити|знайдено|оголошення|в україні)\b", "", brand).strip()

    return brand, count


# ----- Основна логіка -----
def main():
    Path("reports").mkdir(exist_ok=True)

    links = []
    with open(IN_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "," in line:
                brand, url = line.split(",", 1)
                links.append(url.strip())
            else:
                links.append(line)

    rows = []

    for url in links:
        try:
            r = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=30.0)
            soup = BeautifulSoup(r.text, "html.parser")
            h1 = soup.select_one("h1")
            if not h1:
                print(f"[WARN] no <h1> for {url}")
                continue

            brand, count = parse_count_and_brand(h1.get_text(" ", strip=True))
            rows.append({"Brand": brand, "Count": count or 0})
            print(f"[OK] {brand}: {count}")
        except Exception as e:
            print(f"[ERROR] {url}: {e}")

    # ----- Збереження -----
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Brand", "Count"], delimiter=";")
        w.writeheader()
        w.writerows(rows)

    print(f"\n✅ Done! Saved {len(rows)} rows → {OUT_CSV}")


if __name__ == "__main__":
    main()
