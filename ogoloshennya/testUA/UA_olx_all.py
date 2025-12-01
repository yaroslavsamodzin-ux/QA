#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO.RIA (uk/search) → для кожної марки підставляємо brand=<id> у публічний URL
і парсимо кількість оголошень з HTML (видимий текст «… пропозицій»).

Запуск:
    python ua_avtoria_html_counts.py

Вивід:
    vuvod/UA_ria_brands_counts.csv  ; колонки: brand_id;brand_name;count
"""

import csv
import json
import os
import re
import time
import unicodedata
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import requests

# ---- Константи / налаштування ----

# 1) Список марок (value = id, name = назва)
MARKS_URL = "https://auto.ria.com/api/categories/1/marks/"

# 2) База пошуку (саме публічна сторінка, як у тебе)
SEARCH_BASE = "https://auto.ria.com/uk/search/"

# 3) Базові параметри (окрім brand)
BASE_PARAMS: Dict[str, Any] = {
    "search_type": 1,
    "category": 1,
    "abroad": 0,
    "customs_cleared": 1,
    "page": 0,
    "limit": 20,
}

# Ключ параметра бренду
BRAND_PARAM_KEY = "all[0].any[0].brand"

# Вивід
OUT_CSV = "vuvod/UA_ria_brands_counts.csv"
DEBUG_DIR = "debug_ria_html"

# Обмеження запитів
RETRY_MAX = 5
RETRY_BACKOFF = 1.0   # секунди
SLEEP_BETWEEN_BRANDS = 0.05  # невелика пауза, щоб не «душити» сайт

# HTTP заголовки
HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "uk,ru;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

API_HEADERS = {
    "User-Agent": HTML_HEADERS["User-Agent"],
    "Accept": "application/json, text/plain, */*",
}

# ---- Утиліти ----

def http_get(session: requests.Session, url: str, headers: Dict[str, str]) -> requests.Response:
    """GET із ретраями."""
    backoff = RETRY_BACKOFF
    last_exc = None
    for attempt in range(1, RETRY_MAX + 1):
        try:
            r = session.get(url, headers=headers, timeout=40)
            if r.status_code in (429, 502, 503, 504):
                raise requests.HTTPError(f"Retryable {r.status_code}")
            r.raise_for_status()
            return r
        except Exception as e:
            last_exc = e
            if attempt >= RETRY_MAX:
                raise
            time.sleep(backoff); backoff *= 2
    raise last_exc  # type: ignore


def normalize_digits(s: str) -> str:
    """Заміна юнікодних пробілів/цифр → ASCII, залишаємо тільки цифри."""
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("\u00A0", " ").replace("&nbsp;", " ")
    return "".join(ch for ch in s if ch.isdigit())


def extract_total_from_html(html: str) -> int:
    """
    Витягуємо «… пропозицій» із DOM або тексту.
    Стратегії:
      1) #SortButtonContentCount → цифри
      2) Будь-який текст зі словом 'пропози'/'знайдено' поряд із числом
      3) Фолбек за JSON-скриптами поблизу 'search'/'SortButton'
    """
    # зробимо просту нормалізацію
    html_norm = html.replace("\u00A0", " ").replace("&nbsp;", " ")

    # 1) точні селектори (без bs4: regex по id)
    m = re.search(r'id=["\']SortButtonContentCount["\'][^>]*>\s*<[^>]*>\s*([^<]+?)\s*<', html_norm, flags=re.IGNORECASE)
    if m:
        digits = normalize_digits(m.group(1))
        if digits:
            try:
                return int(digits)
            except Exception:
                pass

    # 2) текстові маркери: «Знайдено 12 345», «… пропозицій»
    m2 = re.search(r'(?:Знайдено|Найдено|пропозицій|пропозиції)[^0-9]{0,40}([\d\s]{1,12})',
                   html_norm, flags=re.IGNORECASE)
    if m2:
        digits = normalize_digits(m2.group(1))
        if digits:
            try:
                return int(digits)
            except Exception:
                pass

    # 3) JSON-фолбек (count поряд із ключовими словами)
    m3 = re.search(
        r'(?:SortButtonContentCount|search[_\-]?result|additionalParams)[^{}]{0,800}?(?:"(?:count|total)"\s*:\s*(\d{1,9}))',
        html_norm, flags=re.IGNORECASE | re.DOTALL
    )
    if m3:
        try:
            return int(m3.group(1))
        except Exception:
            pass

    return 0


def build_search_url(brand_id: int) -> str:
    """
    Формуємо URL типу:
    https://auto.ria.com/uk/search/?search_type=1&category=1&...&all[0].any[0].brand=<brand_id>
    """
    pr = urlparse(SEARCH_BASE)
    q = dict(parse_qsl(pr.query, keep_blank_values=True))
    # базові
    for k, v in BASE_PARAMS.items():
        q[str(k)] = str(v)
    # brand
    q[BRAND_PARAM_KEY] = str(brand_id)
    query_encoded = urlencode(q, doseq=True)
    # зробимо дужки читабельними
    query_pretty = query_encoded.replace("%5B", "[").replace("%5D", "]")
    return urlunparse((pr.scheme or "https",
                       pr.netloc or "auto.ria.com",
                       pr.path or "/uk/search/",
                       pr.params,
                       query_pretty,
                       pr.fragment))


def fetch_marks(session: requests.Session) -> List[Tuple[int, str]]:
    """
    Тягнемо всі марки з MARKS_URL.
    Повертає список (id, name).
    """
    r = http_get(session, MARKS_URL, API_HEADERS)
    try:
        data = r.json()
    except Exception:
        open(os.path.join(DEBUG_DIR, "marks_raw.txt"), "w", encoding="utf-8").write(r.text)
        raise

    out: List[Tuple[int, str]] = []
    if isinstance(data, list):
        for it in data:
            try:
                out.append((int(it.get("value")), str(it.get("name", "")).strip()))
            except Exception:
                pass
    elif isinstance(data, dict) and "marks" in data:
        for it in data["marks"]:
            try:
                out.append((int(it.get("value")), str(it.get("name", "")).strip()))
            except Exception:
                pass

    if not out:
        open(os.path.join(DEBUG_DIR, "marks_debug.json"), "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2))
        raise RuntimeError("Не вдалося витягнути марки з MARKS_URL.")
    return out


# ---- Основна логіка ----

def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    os.makedirs(DEBUG_DIR, exist_ok=True)

    sess = requests.Session()

    print("→ Тягну марки з AUTO.RIA ...")
    marks = fetch_marks(sess)
    print(f"  ✓ Отримано марок: {len(marks)}")

    rows: List[Tuple[int, str, int]] = []
    miss = 0

    for bid, name in marks:
        url = build_search_url(bid)
        # важливо: реферер ставимо під поточний бренд (деякі блоки залежать від нього)
        headers = dict(HTML_HEADERS)
        headers["Referer"] = url

        try:
            r = http_get(sess, url, headers)
            cnt = extract_total_from_html(r.text)
            if cnt == 0:
                miss += 1
                # збережемо для діагностики
                safe_name = re.sub(r"[^0-9A-Za-zА-Яа-яЇїІіЄєҐґ]+", "_", name) or "brand"
                open(os.path.join(DEBUG_DIR, f"{bid}_{safe_name}.html"), "w", encoding="utf-8").write(r.text)
        except Exception as e:
            cnt = 0
            safe_name = re.sub(r"[^0-9A-Za-zА-Яа-яЇїІіЄєҐґ]+", "_", name) or "brand"
            open(os.path.join(DEBUG_DIR, f"{bid}_{safe_name}_ERR.txt"), "w", encoding="utf-8").write(str(e))

        rows.append((bid, name, cnt))
        if SLEEP_BETWEEN_BRANDS:
            time.sleep(SLEEP_BETWEEN_BRANDS)

    # Запис у CSV (закрий файл у Excel, якщо відкритий)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["brand_id", "brand_name", "count"])
        for bid, name, cnt in rows:
            w.writerow([bid, name, cnt])

    print(f"\nГотово → {OUT_CSV}")
    print(f"  Нульових/невизначених лічильників: {miss}. Якщо є — глянь {DEBUG_DIR}/* і скинь мені один HTML, піджену селектори.")

if __name__ == "__main__":
    main()
