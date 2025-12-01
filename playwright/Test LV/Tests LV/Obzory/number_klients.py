# easyweek_export.py
import csv
import sys
from time import sleep
import requests
from requests.adapters import HTTPAdapter, Retry

API_BASE = "https://my.easyweek.io/api/clients"
LIMIT = 100
TOTAL_PAGES = 17  # ти підтвердив, що їх 17

# ВСТАВ СВІЙ ТОКЕН НИЖЧЕ (разом зі словом 'Bearer ')
TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbXkuZWFzeXdlZWsuaW8vYXBpL3JlZnJlc2giLCJpYXQiOjE3NjIxNzA5NzAsImV4cCI6MTc2MjE3NDU3MCwibmJmIjoxNzYyMTcwOTcwLCJqdGkiOiJWam5tN1VhYmhMYmd2RnBKIiwic3ViIjozODUzOCwicHJ2IjoiODdlMGFmMWVmOWZkMTU4MTJmZGVjOTcxNTNhMTRlMGIwNDc1NDZhYSIsInR3b19mYWN0b3IiOm51bGx9.oj8qy-EOJtLmYm-p7AqJMjYPoXpJEGhu7WKl4svDG9c"

HEADERS = {
    "Authorization": TOKEN,
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0"
}

def none_to_empty(x):
    return "" if x is None else x

def make_session():
    sess = requests.Session()
    retries = Retry(
        total=5, backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"])
    )
    sess.mount("https://", HTTPAdapter(max_retries=retries))
    return sess

def fetch_page(session, page: int):
    params = {"page": page, "limit": LIMIT}
    resp = session.get(API_BASE, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    out_rows = []
    with make_session() as s:
        for page in range(1, TOTAL_PAGES + 1):
            try:
                payload = fetch_page(s, page)
            except requests.HTTPError as e:
                print(f"[page {page}] HTTP error: {e}", file=sys.stderr)
                break
            except requests.RequestException as e:
                print(f"[page {page}] Network error: {e}", file=sys.stderr)
                break

            data = payload.get("data") or []
            if not data:
                # На випадок, якщо сторінок менше ніж очікується
                print(f"[page {page}] empty data, stopping early.")
                break

            for item in data:
                first_name  = none_to_empty(item.get("first_name"))
                middle_name = none_to_empty(item.get("middle_name"))
                last_name   = none_to_empty(item.get("last_name"))
                phone       = none_to_empty((item.get("customer_phone_formatted") or {}).get("rfc3966"))

                out_rows.append({
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "phone_rfc3966": phone
                })

            # невелика пауза — бути ввічливими до API
            sleep(0.1)

    # запис у CSV (UTF-8-SIG для Excel)
    fieldnames = ["first_name", "middle_name", "last_name", "phone_rfc3966"]

    with open("easyweek_clients.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"✅ Done: {len(out_rows)} rows → easyweek_clients.csv")


if __name__ == "__main__":
    main()
