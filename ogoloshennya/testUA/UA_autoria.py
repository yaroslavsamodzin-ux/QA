import re
import time
import json
import argparse
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === Файли ===
INPUT_FILE  = "autoria_marks.txt"      # формат: 5166 ; Abarth
OUTPUT_FILE = "vuvod/UA_autoria.csv"     # результат: лише 2 колонки brand_name;count
LOG_FILE    = "errors.log"

# === Базовий URL (структуру не міняємо) ===
BASE_URL = (
    "https://auto.ria.com/uk/demo/bu/searchPage/search/indexes/auto,order_auto,newauto_search"
    "?abroad=0&marka_id[0]={brand_id}&model_id[0]=0&indexName=auto,order_auto,newauto_search"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "uk,ru;q=0.9,en;q=0.8",
    "Referer": "https://auto.ria.com/uk/advanced-search/",
    "Connection": "keep-alive",
}


# === Допоміжні функції ===
def log(msg: str):
    """Записує помилки в errors.log"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg.rstrip() + "\n")


def parse_marks(path: str):
    """Зчитує марки з файла (формат: ID ; Name)."""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if ";" in line:
                left, right = line.split(";", 1)
                brand_id = re.sub(r"\D", "", left)
                brand_name = right.strip(" \t-–—")
            else:
                brand_id = re.sub(r"\D", "", line)
                brand_name = ""
            if brand_id:
                rows.append({"id": brand_id, "name": brand_name})
    return rows


def build_session() -> requests.Session:
    """HTTP сесія з повторними спробами"""
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"]),
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


def pick(d: dict, path: str, default=None):
    """Дістає значення з вкладеного JSON за шляхом типу 'a.b.c'."""
    cur = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


# === Основна логіка ===
def main():
    ap = argparse.ArgumentParser(description="Отримуємо кількість оголошень по марках з AUTO.RIA JSON API")
    ap.add_argument("--delay", type=float, default=0.25, help="затримка між запитами, сек")
    args = ap.parse_args()

    marks = parse_marks(INPUT_FILE)
    sess = build_session()
    out_rows = []

    for i, m in enumerate(marks, 1):
        brand_id, brand_name = m["id"], m["name"]
        url = BASE_URL.format(brand_id=brand_id)

        try:
            r = sess.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            data = r.json()

            # Основний лічильник
            main_count = pick(data, "result.search_result.count", default=0)

            print(f"[{i}/{len(marks)}] {brand_name or '(no name)'} (ID={brand_id}) → {main_count}")

            out_rows.append({
                "brand_name": brand_name,
                "count": main_count,
            })

        except Exception as e:
            print(f"[{i}/{len(marks)}] {brand_name or '(no name)'} (ID={brand_id}) → 0 [error]")
            log(f"ID={brand_id} error: {e}")
            out_rows.append({
                "brand_name": brand_name,
                "count": 0,
            })

        time.sleep(args.delay)

    # === Зберігаємо тільки 2 колонки, роздільник ';' ===
    df = pd.DataFrame(out_rows)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig", header=False)

    print(f"\n✅ Збережено у файл: {OUTPUT_FILE} (brand_name;count)")


if __name__ == "__main__":
    main()
