# avtobazar_counts_api.py
# -*- coding: utf-8 -*-
"""
Brand;Count для avtobazar.ua через API (без парсингу HTML).

1) Марки:  https://avtobazar.ua/api/transports/makes/?transport=1
2) К-сть:  https://avtobazar.ua/api/makes/_posts/_count/?transport=1

Вивід: avtobazar_counts.csv з колонками Brand;Count
"""

import csv
import json
import requests
from collections import defaultdict

API_MAKES = "https://avtobazar.ua/api/transports/makes/?transport=1"
API_COUNTS = "https://avtobazar.ua/api/makes/_posts/_count/?transport=1"
OUT_CSV    = "vuvod/UA_avtobazar_counts.csv"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "uk-UA,uk;q=0.9",
    "Origin": "https://avtobazar.ua",
    "Referer": "https://avtobazar.ua/",
}

def load_makes():
    """Повертає словник id->назва та список (назва, id)."""
    r = requests.get(API_MAKES, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    id_to_name = {}
    ordered = []
    for item in data:
        # у відповіді бувають поля id/title або makeId/name тощо — страхуємось
        mid = item.get("id") or item.get("makeId") or item.get("value") or item.get("Id")
        name = item.get("title") or item.get("name") or item.get("value") or item.get("Title")
        if mid is None or name is None:
            continue
        id_to_name[int(mid)] = str(name).strip()
        ordered.append((str(name).strip(), int(mid)))
    return id_to_name, ordered

def load_counts():
    """
    Завантажує масив лічильників по марках.
    Деякі бекенди вимагають POST; пробуємо GET, потім POST з порожнім тілом.
    Повертає список словників з ключами типу {makeId|id, count|postsCount}.
    """
    try:
        r = requests.get(API_COUNTS, headers=HEADERS, timeout=30)
        if r.status_code in (200, 304):
            return r.json()
    except Exception:
        pass

    # fallback на POST (деякі роутери позначені як _count очікують POST)
    r = requests.post(API_COUNTS, headers=HEADERS, json={}, timeout=30)
    r.raise_for_status()
    return r.json()

def normalize_count_item(obj):
    """
    Повертає (make_id, count) з елемента відповіді, незалежно від назв полів.
    Шукаємо ідентифікатор марки та поле з кількістю.
    """
    # можливі назви полів для ID
    for id_key in ("makeId", "make_id", "id", "MakeId", "MakeID", "value"):
        if id_key in obj:
            make_id = obj[id_key]
            break
    else:
        return None

    # можливі назви полів для лічильника
    for c_key in ("count", "postsCount", "total", "qty", "Count"):
        if c_key in obj:
            count = obj[c_key]
            break
    else:
        return None

    try:
        return int(make_id), int(count)
    except Exception:
        return None

def main():
    id_to_name, ordered = load_makes()
    print(f"[+] Отримано {len(ordered)} марок з API")

    raw_counts = load_counts()

    # Підтримка випадку, коли сервер повертає dict зі списком всередині
    if isinstance(raw_counts, dict):
        # спробуємо знайти перший список у значеннях
        for v in raw_counts.values():
            if isinstance(v, list):
                raw_counts = v
                break

    counts_map = defaultdict(int)
    if isinstance(raw_counts, list):
        for item in raw_counts:
            if not isinstance(item, dict):
                continue
            pair = normalize_count_item(item)
            if pair:
                mid, cnt = pair
                counts_map[int(mid)] = int(cnt)

    # Вивід у CSV у порядку марок з першого API
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Brand", "Count"])

        for name, mid in ordered:
            cnt = counts_map.get(mid, 0)
            print(f"{name}: {cnt}")
            w.writerow([name, cnt])

    print(f"\n✅ Збережено у файл: {OUT_CSV}")

if __name__ == "__main__":
    main()
