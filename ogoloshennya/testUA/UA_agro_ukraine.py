# agro_ukraine_subcategories_from_r198.py
# -*- coding: utf-8 -*-

import re
import csv
import requests
from bs4 import BeautifulSoup

URL = "https://agro-ukraine.com/ua/trade/r-198/p-1/"
OUT = "vuvod/UA_agro_ukraine.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "uk-UA,uk;q=0.9",
}

RE_LAST_NUM = re.compile(r"(\d[\d\s\u202f\u00A0]*)$")

def norm_int(s: str) -> int:
    return int(
        str(s)
        .replace("\u202f", "")
        .replace("\u00A0", "")
        .replace("\xa0", "")
        .replace(" ", "")
    )

def extract_from_block(soup: BeautifulSoup):
    """
    Знаходить усі <a class="sfsp_l2"> у верхньому блоці 'всі підрубрики'
    """
    rows = []
    for a in soup.select("a.sfsp_l2[href]"):
        name = a.get_text(strip=True)
        href = a["href"]
        if not href.startswith("http"):
            href = "https://agro-ukraine.com" + href

        # після <a> часто стоїть число
        text = a.parent.get_text(" ", strip=True)
        tail = text.replace(name, "").strip()
        m = RE_LAST_NUM.search(tail)
        count = 0
        if m:
            try:
                count = norm_int(m.group(1))
            except Exception:
                pass

        rows.append((name, count, href))
    return rows


def main():
    print(f"[+] Завантажую сторінку: {URL}")
    resp = requests.get(URL, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = extract_from_block(soup)
    print(f"[+] Знайдено {len(rows)} підкатегорій.")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Name", "Count"])
        for name, cnt, href in rows:
            w.writerow([name, cnt])


    

    print(f"\n✅ Збережено у файл: {OUT}")


if __name__ == "__main__":
    main()
