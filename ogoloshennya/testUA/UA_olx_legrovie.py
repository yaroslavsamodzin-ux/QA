#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OLX brands counts → CSV тільки для заданого списку брендів з їх ID.

Як користуватися:
1) Устав свій "Copy as cURL (bash)" у COUNTS_CURL (той, де у Response видно [{id,count}, ...]).
2) Поклади список брендів з ID у BRANDS_IDS_FILE (див. формати нижче).
3) Запусти: python olx_brands_with_ids.py
4) Результат: vuvod/UA_olx_all.csv (brand_name;count) — або з brand_id, якщо INCLUDE_ID_IN_CSV=True.

Формати для BRANDS_IDS_FILE:
- JSON:       [{"name":"Acura","id":963}, {"name":"Alfa Romeo","id":"965"}, ...]
- CSV:        name;id   або name,id  (з або без заголовку)
- "Сирий" текст у стилі консолі:
              0: {name: 'Acura', id: '963'}
              1: {name: 'Alfa Romeo', id: '965'}
              ...
"""

import csv
import json
import os
import re
import shlex
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import requests

# ===================== ВСТАВ СВІЙ cURL НИЖЧЕ =====================

COUNTS_CURL = r"""
curl 'https://www.olx.ua/api/v1/offers/metadata/search-categories/?offset=0&limit=40&category_id=1558&currency=UAH&filter_refiners=spell_checker&facets=%5B%7B%22field%22%3A%22region%22%2C%22fetchLabel%22%3Atrue%2C%22fetchUrl%22%3Atrue%2C%22limit%22%3A30%7D%5D' \
  -H 'accept: */*' \
  -H 'accept-language: uk' \
  -H 'cache-control: no-cache' \
  -b 'deviceGUID=421ee75f-985e-4054-b77b-538e6fed7389; _cc_id=db09b3c2a7f31626f8c0aff1cfa93171; cookieBarSeenV2=true; cookieBarSeen=true; _ga=GA1.1.547247245.1749836613; _hjSessionUser_2218922=eyJpZCI6IjEzMTI2YzVhLTg3NjQtNTM3Yi05ZWU5LTQ0MDUwMjQ2MzdjMiIsImNyZWF0ZWQiOjE3NDk4MzY2MDgyMjEsImV4aXN0aW5nIjp0cnVlfQ==; _hjSessionUser_1617300=eyJpZCI6IjM4ZGYwZmE2LWI2YzgtNTBkMS04NjM5LTExNDljODU3ZDc4YSIsImNyZWF0ZWQiOjE3NTQzOTMxMDIwNzgsImV4aXN0aW5nIjpmYWxzZX0=; user_id=1068124716; user_uuid=2305208b-3b18-4ce7-888d-3d842624459a; __user_id_P&S=1068124716; user_id_recs=1068124716; user_business_status=private; _sharedid=6b9468d3-a21f-4761-a5c2-2b9ed5861834; _sharedid_cst=zix7LPQsHA%3D%3D; _gcl_au=1.1.1221995718.1757677044; lang=uk; test=1; laquesisff=aut-1425#aut-388#buy-2279#carparts-312#de-2724#decision-657#deluareb-3016#deluareb-3155#deluareb-4067#deluareb-4197#ema-54#euonb-114#eus-1773#grw-124#jobs-7611#kuna-307#mart-1341#oec-1238#oesx-2798#oesx-3343#pos-2021#posting-1419#posting-1638#rm-28#rm-707#rm-780#rm-824#rm-852#srt-1289#srt-1346#srt-1434#srt-1593#srt-1758#srt-682#uacc-529#up-991; __gsas=ID=f5a14f72cce30e38:T=1759846597:RT=1759846597:S=ALNI_Mad0_5T9W1Ba2b9p-XbwEORDs70zQ; laquesis=buy-10188@b#eupp-3544@a#eupp-3582@a#eupp-3590@a#oec-706@a#oesx-5296@b#olxeu-42683@b#platf-21180@b#pos-2233@a#pos-2251@b#ream-432@a#rnk-2072@b#search-2109@b; mobile_default=desktop; __gads=ID=d087d81b6312096c:T=1749836610:RT=1761068835:S=ALNI_MbVn2wGXj0LjCSWztdBM9EvLw456A; __gpi=UID=000010ddcf8b1825:T=1749836610:RT=1761068835:S=ALNI_MZuxR-bjloWQICZnr89tBnWVsoPig; __eoi=ID=24f7514997d02312:T=1749836610:RT=1761068835:S=AA-AfjbCUW_pJhAMBVj6yZeS2Gfc; lqstatus=1761121325|199c295a5f6xabd9e39|rnk-2072#search-2109|||0|1761120005|0; _hjSession_2218922=eyJpZCI6ImI2NDRiNWFmLWFmMTMtNDYyMS05YWRkLWE2Y2M3YjI1NjRkMiIsImMiOjE3NjExMjA5Mzc0MDcsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; session_start_date=1761122738350; cto_bidid=qFt1t19Qa3lEeTJMOUNTTEJyTmh3eldmWDlEV0lReVBldFhseEU5Qjl3QWYzZnFBcFR5ZFc0N1ZtRjMwZTglMkZ0QzhJYXVXWGYlMkZDS0tobW95NlYzdDFEYjdnYjdKaXNNUGlpQkNsUzVOUiUyRlNSOFRiNCUzRA; cto_bundle=lkre6l9oUkRyNm9vNHpsNUF2empQd1g4d1h4RTdTOGg5M1Bqc2c0QmVWNjY5UDRBdXNQNXpLeDludEV1TGdDQzlMVmdkVTZLM2RPNnF5SSUyRlBFanFMcGlzU21BblNuS2Z3RkxvV2ZhRUxaSE9HJTJGbTU3WW1wTnhIV3czdEtGVHFNZHJDQXJTM3JXQ3RWY3FJenR6OE5kQXRqdTQ2V1VRSmFwTDhsekxxV3JVVk1jM2x5V05GVlhJeVRyT1dkQW1jTU1qazg0b0U0aFI0djJKYU1DYyUyQm1FJTJGRSUyQjBiNElOUGZHb09yJTJCUGVuN2I1ZUFvJTJGQnZJdENmUTNkNnBxaXgzZ21qYjZ5c1Q; ab.storage.sessionId.d6bbf693-a714-4ff9-a598-baa9bd848490=g%3A792da3fa-937d-b2f3-697b-3306a7cf90bb%7Ce%3A1761122745944%7Cc%3A1761120945944%7Cl%3A1761120945944; ab.storage.deviceId.d6bbf693-a714-4ff9-a598-baa9bd848490=g%3A829b6e03-4c81-6a4e-6380-b95b4af142cb%7Ce%3Aundefined%7Cc%3A1749836612611%7Cl%3A1761120945945; ab.storage.userId.d6bbf693-a714-4ff9-a598-baa9bd848490=g%3A2305208b-3b18-4ce7-888d-3d842624459a%7Ce%3Aundefined%7Cc%3A1754393109342%7Cl%3A1761120945946; onap=1976a63c229x72e7b73a-62-19a0afd04f1x335acc1d-11-1761122852; _ga_TVZPR1MEG9=GS2.1.s1761120924$o63$g1$t1761121051$j40$l0$h0; PHPSESSID=6vibbqj0t4sc6d3uq4na51r3pk' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.olx.ua/uk/transport/legkovye-avtomobili/byd/?currency=UAH' \
  -H 'sec-ch-ua: "Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' \
  -H 'x-client: DESKTOP' \
  -H 'x-device-id: 421ee75f-985e-4054-b77b-538e6fed7389' \
  -H 'x-fingerprint: fbdc4f53959cdb4af9c2a8983d0ffab85c6324e638a283d8d11dae88fc3236ac3fef60c9cf99daeee8380ebb100f22a6faed307981c3a6ca4e1f7a2acddfea3321f2c817b2cc220c3fef60c9cf99daee3fef60c9cf99daee4e1f7a2acddfea33b497a357830277b800d2d70001a8f455308e012c59cf7bdd93ba89d2bc096e295c6324e638a283d85a1778be62509b00e8380ebb100f22a6986102e8dd8cde950310d17283129330f6e9813aa2a88b6b2aa98c6b03d84b2aaa6925b0558d723aa2dab357225d0511272ec8e83d084c3e29b755643a58ca1b6255da105753936400ab77cc9433c49756b16d11aecc8186428983c35d9b74ca131d7dd9eb490fb0fb7dd9ca7e63276c9fc7316f43582ce9171a6acf45418985964f5950205a4320525fa71314aa02ef8ac63dd7ad0259d2bd311f3bba661284854360a07fd48fdb854360a07fd48fdb854360a07fd48fdb854360a07fd48fdb854360a07fd48fdb854360a07fd48fdb854360a07fd48fdb854360a07fd48fdb854360a07fd48fdb854360a07fd48fdb99424db0dded4c09' \
  -H 'x-platform-type: mobile-html5'
  """.strip()
# ===================== НАЛАШТУВАННЯ =====================

# Файл з твоїми брендами та ID
BRANDS_IDS_FILE = "olx.txt"

# Чи додавати стовпчик brand_id у CSV
INCLUDE_ID_IN_CSV = False

OUT_CSV = "vuvod/UA_olx_legkovie.csv"

# пагінація (якщо всі бренди приходять за 1 раз — постав False)
MODE_PAGINATION = True
PAGE_SIZE = 40
PAGE_SIZE_PARAM = None     # None = авто; або "limit" / "count"
OFFSET_PARAM = "offset"
MAX_PAGES = 200
SLEEP_BETWEEN_PAGES_SEC = 0.0

# ===================== УТИЛІТИ =====================

def parse_curl(curl_str: str) -> Tuple[str, str, Dict[str, str], Optional[str]]:
    if not curl_str or "curl" not in curl_str.lower():
        raise ValueError("COUNTS_CURL має містити 'Copy as cURL (bash)' із DevTools.")
    line = " ".join(curl_str.strip().splitlines())
    if line.lower().startswith("curl "):
        line = line[5:]
    tokens = shlex.split(line)

    method = "GET"
    url = ""
    headers: Dict[str, str] = {}
    data: Optional[str] = None

    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("-X", "--request") and i + 1 < len(tokens):
            method = tokens[i + 1].upper(); i += 2; continue
        if t in ("-H", "--header") and i + 1 < len(tokens):
            hv = tokens[i + 1]
            if ":" in hv:
                k, v = hv.split(":", 1)
                headers[k.strip()] = v.strip()
            i += 2; continue
        if t in ("--data", "--data-raw", "--data-binary", "-d") and i + 1 < len(tokens):
            data = tokens[i + 1]; i += 2
            if method == "GET":
                method = "POST"
            continue
        if t.startswith("http://") or t.startswith("https://"):
            url = t; i += 1; continue
        i += 1

    if not url:
        for t in tokens:
            if t.startswith("http://") or t.startswith("https://"):
                url = t; break
    if not url:
        raise ValueError("Не знайшов URL у COUNTS_CURL.")

    headers.setdefault("Accept", "application/json, text/plain, */*")
    headers.setdefault("User-Agent", "Mozilla/5.0")
    return method, url, headers, data

def http_call(session: requests.Session, method: str, url: str, headers: Dict[str, str], data: Optional[str]) -> Any:
    max_tries = 5; backoff = 1.0
    for attempt in range(1, max_tries + 1):
        try:
            if method == "GET":
                r = session.get(url, headers=headers, timeout=40)
            else:
                if data:
                    if data.strip().startswith("{"):
                        r = session.post(url, headers={**headers, "Content-Type": headers.get("Content-Type", "application/json")},
                                         data=data.encode("utf-8"), timeout=60)
                    else:
                        r = session.post(url, headers={**headers, "Content-Type": headers.get("Content-Type", "application/x-www-form-urlencoded")},
                                         data=data.encode("utf-8"), timeout=60)
                else:
                    r = session.post(url, headers=headers, timeout=40)
            if r.status_code in (429, 502, 503, 504):
                raise requests.HTTPError(f"Retryable {r.status_code}")
            r.raise_for_status()
            if not r.text.strip():
                return {}
            try:
                return r.json()
            except Exception:
                open("debug_raw.txt", "w", encoding="utf-8").write(r.text)
                raise
        except Exception:
            if attempt >= max_tries:
                raise
            time.sleep(backoff); backoff *= 2

def extract_id_count(obj: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    def walk(x):
        if isinstance(x, dict):
            if "id" in x and "count" in x:
                out.append({"id": x["id"], "count": x["count"]})
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for it in x: walk(it)
    walk(obj); return out

def get_query_param(url: str, key: str, default: Optional[str] = None) -> Optional[str]:
    pr = urlparse(url); q = dict(parse_qsl(pr.query, keep_blank_values=True)); return q.get(key, default)

def set_query_param(url: str, key: str, value: Any) -> str:
    pr = urlparse(url); q = dict(parse_qsl(pr.query, keep_blank_values=True))
    q[key] = str(value); new_query = urlencode(q, doseq=True)
    return urlunparse((pr.scheme, pr.netloc, pr.path, pr.params, new_query, pr.fragment))

def detect_page_size_param(url: str) -> str:
    if PAGE_SIZE_PARAM: return PAGE_SIZE_PARAM
    if get_query_param(url, "limit") is not None: return "limit"
    if get_query_param(url, "count") is not None: return "count"
    return "limit"

# ---------- ЛОАДЕР СПИСКУ БРЕНДІВ З ID ----------

_BRAND_LINE_RE = re.compile(
    r"""\{\s*name\s*:\s*['"](?P<name>[^'"]+)['"]\s*,\s*id\s*:\s*['"]?(?P<id>\d+)['"]?\s*\}""",
    re.IGNORECASE
)

def load_brands_with_ids(path: str) -> List[Tuple[str, int]]:
    """
    Повертає список (name, id) у порядку з файлу.
    Підтримує JSON / CSV / "сирий" текст з рядками {name:'...', id:'...'}.
    """
    if not os.path.exists(path):
        raise SystemExit(f"❌ Не знайдено файл зі списком брендів: {path}")

    txt = open(path, "r", encoding="utf-8").read().strip()

    # 1) JSON масив об'єктів
    try:
        data = json.loads(txt)
        if isinstance(data, dict):
            # може бути словник name->id
            items = []
            for k, v in data.items():
                try:
                    items.append((str(k).strip(), int(v)))
                except Exception:
                    continue
            if items:
                return items
        elif isinstance(data, list):
            items = []
            for obj in data:
                if isinstance(obj, dict) and "name" in obj and "id" in obj:
                    try:
                        items.append((str(obj["name"]).strip(), int(obj["id"])))
                    except Exception:
                        pass
            if items:
                return items
    except Exception:
        pass

    # 2) CSV (name;id або name,id)
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    sep = None
    if any(";" in ln for ln in lines):
        sep = ";"
    elif any("," in ln for ln in lines):
        sep = ","
    if sep:
        items = []
        # пропустимо заголовок, якщо є
        start_i = 0
        header = [p.strip().lower() for p in lines[0].split(sep)]
        if "name" in header and "id" in header:
            start_i = 1
        for ln in lines[start_i:]:
            parts = [p.strip() for p in ln.split(sep)]
            if len(parts) >= 2:
                try:
                    items.append((parts[0], int(parts[1])))
                except Exception:
                    pass
        if items:
            return items

    # 3) "сирий" консольний формат: 0: {name: 'Acura', id: '963'}
    items = []
    for ln in lines:
        m = _BRAND_LINE_RE.search(ln)
        if m:
            try:
                items.append((m.group("name").strip(), int(m.group("id"))))
            except Exception:
                pass
    if items:
        return items

    raise SystemExit("❌ Не вдалося розпізнати формат BRANDS_IDS_FILE. Зроби JSON/CSV або залиш як у прикладі з консолі.")

# ===================== ГОЛОВНА ЛОГІКА =====================

def fetch_counts_all(session: requests.Session, method: str, url: str, headers: Dict[str, str], data: Optional[str]) -> List[Dict[str, Any]]:
    if not MODE_PAGINATION:
        j = http_call(session, method, url, headers, data)
        items = extract_id_count(j)
        if not items:
            open("debug_counts.json", "w", encoding="utf-8").write(json.dumps(j, ensure_ascii=False, indent=2))
            raise RuntimeError("Не знайшов {id,count}. Дивись debug_counts.json.")
        return items

    page_param = detect_page_size_param(url)
    if get_query_param(url, page_param) is None:
        url = set_query_param(url, page_param, PAGE_SIZE)

    items_all: List[Dict[str, Any]] = []
    seen_ids = set()

    try: offset = int(get_query_param(url, OFFSET_PARAM, "0"))
    except Exception: offset = 0

    for _ in range(MAX_PAGES):
        url_page = set_query_param(url, OFFSET_PARAM, offset)
        j = http_call(session, method, url_page, headers, data)
        items = extract_id_count(j)
        if not items: break

        added = 0
        for it in items:
            try:
                bid = int(it["id"]); cnt = int(it["count"])
            except Exception:
                continue
            if bid in seen_ids: continue
            seen_ids.add(bid); items_all.append({"id": bid, "count": cnt}); added += 1

        if added == 0: break

        try: page_size_val = int(get_query_param(url, page_param, str(PAGE_SIZE)))
        except Exception: page_size_val = PAGE_SIZE
        offset += page_size_val

        if SLEEP_BETWEEN_PAGES_SEC: time.sleep(SLEEP_BETWEEN_PAGES_SEC)

    if not items_all:
        open("debug_counts.json", "w", encoding="utf-8").write(json.dumps(j, ensure_ascii=False, indent=2))
        raise RuntimeError("Пагінація не дала результатів. Дивись debug_counts.json.")
    return items_all

def main():
    # --- завантажуємо твої (name, id) ---
    brand_pairs: List[Tuple[str, int]] = load_brands_with_ids(BRANDS_IDS_FILE)
    print(f"→ Завантажено брендів із ID: {len(brand_pairs)}")

    # --- COUNTS із OLX ---
    counts_method, counts_url, counts_headers, counts_data = parse_curl(COUNTS_CURL)
    host = urlparse(counts_url).netloc.lower()
    if "example.com" in host or not host:
        raise SystemExit("❌ Встав реальний COUNTS_CURL із DevTools (не example.com).")

    session = requests.Session()
    base_headers: Dict[str, str] = {}
    for k in ("User-Agent", "Accept", "Cookie", "Referer", "x-csrf-token", "Authorization", "Content-Type"):
        if k in counts_headers:
            base_headers[k] = counts_headers[k]

    print("→ Тягну {id,count} ...")
    counts = fetch_counts_all(session, counts_method, counts_url, base_headers, counts_data)
    print(f"  ✓ Отримано пар: {len(counts)}")

    # робимо мапу id -> count
    id_to_count: Dict[int, int] = {}
    for it in counts:
        try:
            id_to_count[int(it["id"])] = int(it["count"])
        except Exception:
            continue

    # --- CSV вихід ---
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    written = 0
    missing: List[Tuple[str, int]] = []

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        if INCLUDE_ID_IN_CSV:
            w = csv.writer(f, delimiter=";")
            w.writerow(["brand_id", "brand_name", "count"])
        else:
            w = csv.writer(f, delimiter=";")
            w.writerow(["brand_name", "count"])

        for name, bid in brand_pairs:
            cnt = id_to_count.get(bid, 0)
            if INCLUDE_ID_IN_CSV:
                w.writerow([bid, name, cnt])
            else:
                w.writerow([name, cnt])
            written += 1
            if bid not in id_to_count:
                missing.append((name, bid))

    # --- діагностика ---
    print(f"\n✓ Записано рядків: {written}")
    if missing:
        print("⚠️ Для цих брендів ID не знайдено у відповіді OLX — виставлено count=0:")
        for name, bid in missing[:50]:
            print(f"  - {name} (id={bid})")
        if len(missing) > 50:
            print(f"  ... і ще {len(missing)-50} шт.")

    print(f"\nГотово → {OUT_CSV}")
    print("Якщо щось впаде — прикріпи debug_counts.json / debug_raw.txt, я піджену парсер.")

if __name__ == "__main__":
    main()
