# infocar_brand_counts_from_list.py
# -*- coding: utf-8 -*-

import re
import csv
import time
from pathlib import Path
from typing import List, Tuple
import httpx
from bs4 import BeautifulSoup

# === Константи ===
SEARCH_URL = ("https://avtobazar.infocar.ua/search-car/"
              "?m%5B%5D={brand_id}&n%5B%5D=0&x%5B%5D=0&y1=&y2=&p1=&p2=&"
              "o%5B%5D=0&c%5B%5D=0&ru=&m1=&m2=&k%5B%5D=&co%5B%5D=&d=&p=&pr=&da=0")

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/123.0.0.0 Safari/537.36"),
    "Accept-Language": "uk-UA,uk;q=0.9,ru;q=0.8,en;q=0.7",
}

RX_COUNT = re.compile(r"(?:Знайдено|Найдено)\s*:\s*<strong>(\d+)</strong>", re.I | re.S)


# === Функції ===
def parse_brand_list(path: Path) -> List[Tuple[int, str]]:
    pairs: List[Tuple[int, str]] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        if ";" in line:
            left, right = line.split(";", 1)
        else:
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            left, right = parts
        left, right = left.strip(), right.strip()
        if left.isdigit():
            pairs.append((int(left), right))
    return pairs


def fetch(url: str, timeout: float = 30.0) -> str:
    r = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=timeout)
    r.raise_for_status()
    return r.text


def extract_count(html: str) -> int:
    m = RX_COUNT.search(html)
    if m:
        return int(m.group(1))
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one("#sort") or soup
    for strong in root.select("strong"):
        txt = strong.parent.get_text(" ").lower() if strong.parent else ""
        if "знайдено" in txt or "найдено" in txt:
            num = re.sub(r"[^\d]", "", strong.get_text(""))
            if num.isdigit():
                return int(num)
    return 0


def main():
    infile = Path("testUA/brands.txt")
    outfile = Path("vuvod/UA_infocar_counts.csv")
    pause = 0.6

    if not infile.exists():
        raise SystemExit(f"[ERR] Файл не знайдено: {infile}")

    outfile.parent.mkdir(parents=True, exist_ok=True)
    brands = parse_brand_list(infile)
    if not brands:
        raise SystemExit("[ERR] Список брендів порожній!")

    rows = []
    for bid, name in brands:
        url = SEARCH_URL.format(brand_id=bid)
        try:
            html = fetch(url)
            count = extract_count(html)
        except Exception as e:
            print(f"[ERR] {bid} {name}: {e}")
            time.sleep(pause)
            continue

        print(f"{name} ; {count}")
        rows.append((name, count))
        time.sleep(pause)

    with outfile.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Brand", "Count"])
        w.writerows(rows)

    print(f"\n[OK] Saved {len(rows)} rows -> {outfile}")


if __name__ == "__main__":
    main()
