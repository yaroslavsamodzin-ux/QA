import requests
import json
import re
from bs4 import BeautifulSoup

URL = "https://motorfy.lv/ru/lietoti-auto"
OUT_FILE = "motorfy_brands.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# якщо треба щось ігнорувати — додай сюди
IGNORE_BRANDS = {
    # "автосалоны",
}

def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def parse_brands(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    result = []

    for a in soup.select("#main_make a"):
        # назва бренду = текст у <a> без <span>
        brand = a.get_text(" ", strip=True)
        # але brand зараз буде типу "Audi (181)", тож дістанемо цифру окремо
        span = a.select_one("span")

        if not span:
            continue

        count_text = span.get_text(strip=True)  # "(181)"
        m = re.search(r"(\d+)", count_text)
        if not m:
            continue

        count = int(m.group(1))

        # прибираємо "(число)" з назви бренду
        brand = re.sub(r"\(\s*\d+\s*\)", "", brand).strip()

        if not brand:
            continue

        if brand.lower() in IGNORE_BRANDS:
            continue

        result.append({"brand": brand, "count": count})

    return result


def save_json(items: list[dict], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def main():
    html = fetch_html(URL)
    items = parse_brands(html)
    save_json(items, OUT_FILE)
    print(f"OK: saved {len(items)} brands → {OUT_FILE}")


if __name__ == "__main__":
    main()
