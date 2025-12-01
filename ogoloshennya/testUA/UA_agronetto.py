#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agriline (UA) — Трактори: "Марка -> Кількість" за готовими brand→id.

Вхід:
  - текстовий файл зі стовпцями brand  id  (таб-розділені; перший рядок — хедер).
    Приклад: "ЮМЗ\t2863"

Логіка:
  - для кожного запису формує URL фільтра бренду:
        https://agriline.ua/-/traktori/<slug>--c228tm<ID>
    де <slug> — транслітерована назва бренду (ASCII). Якщо такий URL дає 404/порожньо,
    робимо фолбек на варіант БЕЗ слугу:
        https://agriline.ua/-/traktori/--c228tm<ID>
  - витягає кількість із ".current-ads-num-title span.num" (як на твоєму скріні),
    з підстраховкою через regex.
  - пише CSV: Brand,Count,URL

Запуск:
    python agriline_traktori_by_ids.py
    або
    python agriline_traktori_by_ids.py input.tsv output.csv
"""

import csv
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional

import requests
from bs4 import BeautifulSoup

BASE = "https://agriline.ua"
CATEGORY_PREFIX = "/-/traktori/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA}

# Фолбек-патерни
COUNT_RE_LIST = [
    re.compile(r'Знайдено:\s*(\d+)\s+оголошен', re.I | re.U),
    re.compile(r'(\d+)\s+оголошен', re.I | re.U),
]

def fetch(url: str, *, retry: int = 3, timeout: int = 25) -> Optional[requests.Response]:
    for i in range(retry):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200 and r.text:
                return r
        except requests.RequestException:
            pass
        time.sleep(1.0 + 0.6 * i)
    return None

# --- простий трансліт (uk/ru -> латиниця) + слаг ---
_CYR_MAP = {
    "а":"a","б":"b","в":"v","г":"h","ґ":"g","д":"d","е":"e","є":"ie","ж":"zh","з":"z","и":"y","і":"i","ї":"i","й":"i",
    "к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f","х":"kh","ц":"ts","ч":"ch",
    "ш":"sh","щ":"shch","ь":"","ю":"iu","я":"ia","ы":"y","э":"e","ъ":"",
    "ё":"e","йо":"io","ё":"e",
}
def _translit(s: str) -> str:
    t = []
    i = 0
    s_low = s.lower()
    while i < len(s_low):
        # дволітерні комбінації
        if i+1 < len(s_low) and s_low[i:i+2] in ("йо",):
            t.append({"йо":"io"}[s_low[i:i+2]])
            i += 2
            continue
        ch = s_low[i]
        t.append(_CYR_MAP.get(ch, ch))
        i += 1
    return "".join(t)

def slugify_brand(name: str) -> str:
    import unicodedata, re as _re
    # трансліт для кирилиці
    s = _translit(name)
    # нормалізація + ASCII
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    # до слага
    s = _re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    s = _re.sub(r"-{2,}", "-", s)
    return s or "brand"

def build_urls(brand: str, tm_id: str) -> List[str]:
    slug = slugify_brand(brand)
    return [
        f"{BASE}{CATEGORY_PREFIX}{slug}--c228tm{tm_id}",
        f"{BASE}{CATEGORY_PREFIX}--c228tm{tm_id}",   # фолбек без слугу (часто працює)
    ]

def extract_count_from_html(html: str) -> Optional[int]:
    soup = BeautifulSoup(html, "html.parser")
    node = soup.select_one(".current-ads-num-title span.num")
    if node:
        m = re.search(r"(\d+)", node.get_text(" ", strip=True))
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return None
    # фолбек regex-ами по всій сторінці
    for rx in COUNT_RE_LIST:
        m = rx.search(html)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                continue
    return None

def parse_count_for_tm(brand: str, tm_id: str) -> Tuple[int, str]:
    """
    Повертає (count, used_url). Якщо не вдалося — (0 або -1, останній url з проб).
    """
    last_url = ""
    for url in build_urls(brand, tm_id):
        last_url = url
        resp = fetch(url)
        if not resp:
            # мережевий збій — спробуємо інший варіант
            continue
        cnt = extract_count_from_html(resp.text)
        if isinstance(cnt, int):
            return cnt, url
    # якщо зовсім не вдалося — 0 (або -1 якщо хочеш помічати мережеві)
    return 0, last_url

def read_brand_ids(path: Path) -> List[Tuple[str, str]]:
    """
    Зчитує файл з хедером 'brand<tab>id'. Допускає і коми.
    """
    rows: List[Tuple[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        sample = f.read(2048)
        f.seek(0)
        # визначимо роздільник
        dialect = csv.Sniffer().sniff(sample, delimiters="\t,;")
        reader = csv.DictReader(f, dialect=dialect)
        # нормалізуємо імена полів
        field_map = {k.strip().lower(): k for k in reader.fieldnames or []}
        bcol = field_map.get("brand")
        icol = field_map.get("id")
        if not bcol or not icol:
            raise RuntimeError("Очікував стовпці 'brand' та 'id' у першому рядку.")
        for row in reader:
            brand = (row.get(bcol) or "").strip()
            tm_id = (row.get(icol) or "").strip()
            if brand and tm_id:
                rows.append((brand, tm_id))
    return rows

def main(in_file: str, out_csv: str):
    in_path = Path(in_file)
    if not in_path.exists():
        print(f"⚠️  Файл не знайдено: {in_path}")
        sys.exit(2)

    pairs = read_brand_ids(in_path)
    if not pairs:
        print("⚠️  У вхідному файлі немає валідних пар brand→id.")
        sys.exit(3)

    print(f"⚙️  Обробка: {in_file} → {out_csv}")
    total = len(pairs)
    rows = []

    for i, (brand, tm_id) in enumerate(pairs, 1):
        cnt, used_url = parse_count_for_tm(brand, tm_id)
        rows.append({"Brand": brand, "Count": cnt})
        print(f"[{i}/{total}] {brand} → {cnt}")
        time.sleep(0.25)

    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Brand", "Count"], delimiter=';')
        w.writeheader()
        w.writerows(rows)

    print(f"\n✅ Готово! Збережено: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main("agriline_brands_ids.txt", "vuvod/UA_agriline.csv")
    elif len(sys.argv) == 2:
        main(sys.argv[1], "vuvod/UA_agriline.csv")
    else:
        main(sys.argv[1], sys.argv[2])
