# -*- coding: utf-8 -*-
"""
Збір Brand;Count з <h1> для списку URL у links_autoria.txt.

Запуск:
    python UA_autoria.py --infile links_autoria.txt --outfile reports/brands_counts.csv --headless 1
"""

import re
import csv
import time
import argparse
import unicodedata
from pathlib import Path
from typing import List, Tuple, Optional
from urllib.parse import urlparse

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
HEADERS = {
    "User-Agent": UA,
    "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ---- патерни для кількості (підтримка знака "+") ----
COUNT_PATS = [
    re.compile(r"\(([\d\s\u00A0]+)\+?\)"),
    re.compile(r"знайдено\s+([\d\s\u00A0]+)\+?", re.I),
    re.compile(r"([\d\s\u00A0]+)\+?\s+(?:оголош|объявлен)", re.I),
    re.compile(r"[–—-]\s*([\d\s\u00A0]+)\+?\s+(?:пропоз|оголош|объявлен)", re.I),
]

# стоп-слова, які не повинні потрапляти в бренд
STOPWORDS_RE = re.compile(
    r"(?i)\b(авто|продаж|продажа|купити|купить|знайдено|оголошенн(?:я|і|ий)|оголошень|в україні|усі|всі|марка|всі марки|усі марки)\b"
)

# абревіатури, які тримаємо великими
ACRONYMS = {
    "BMW","BYD","GMC","MG","BRP","CFMOTO","JCB","MAN","MINI","VAZ","GAZ","ZAZ","UAZ",
    "ГАЗ","УАЗ","ЗАЗ","МАЗ","КРАЗ","ВАЗ","КАМАЗ"
}

# ---------- читання посилань ----------
def read_links(path: str) -> List[str]:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Не знайдено файл: {path}")
    urls: List[str] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "," in line:
            _, url = line.split(",", 1)
            urls.append(url.strip())
        else:
            urls.append(line)
    if not urls:
        raise SystemExit(f"Файл {path} порожній.")
    return urls

def _digits_to_int(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    d = re.sub(r"[^\d]", "", s)
    return int(d) if d.isdigit() else None

def _slug_to_brand(slug: str) -> str:
    s = unicodedata.normalize("NFKD", slug)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[-_]+", " ", s).strip()
    up = s.upper()
    if up in ACRONYMS:
        return up
    return " ".join(w.upper() if w.upper() in ACRONYMS else (w.capitalize() if w else "")
                    for w in s.split())

def _brand_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    parts = [p for p in path.split("/") if p]
    last = parts[-1] if parts else ""
    if last.lower() in {"cars", "avto", "auto"} and len(parts) >= 2:
        last = parts[-2]
    return _slug_to_brand(last)

# ---------- парсинг H1 (виправлено "продаж ...") ----------
def parse_h1(h1_text: str, url: str) -> Tuple[str, Optional[int]]:
    h1_raw = (h1_text or "").strip()
    # попереднє очищення від службових префіксів
    h1 = re.sub(r"^\s*(?:продаж|продажа|купити|купить)\s+", "", h1_raw, flags=re.I)
    h1 = re.sub(r"\s+", " ", h1)

    # COUNT
    count: Optional[int] = None
    for rx in COUNT_PATS:
        m = rx.search(h1)
        if m:
            count = _digits_to_int(m.group(1))
            if count is not None:
                break

    # BRAND
    brand = ""

    # 1) "... оголошень/объявлений про BRAND ..."
    m = re.search(
        r"(?:оголошенн(?:я|і|ий)|оголошень|объявлен[ийя])\s+про\s+([^\(\):–—-]+?)\s*(?:[:(]|[–—-]|$)",
        h1, re.I
    )
    if m:
        brand = m.group(1)

    # 2) "продаж BRAND ..." / "продажа BRAND ..." (беремо з сирого H1)
    if not brand:
        m = re.search(r"\b(?:продаж|продажа)\s+([^\(\):–—-]+?)\s*(?:[:(]|[–—-]|$)", h1_raw, re.I)
        if m:
            brand = m.group(1)

    # 3) "BRAND — 172 пропозиції"
    if not brand:
        m = re.search(
            r"^\s*([^\d–—-][^–—-]+?)\s*[–—-]\s*[\d\s\u00A0]+\+?\s+(?:пропоз|оголош|объявлен)",
            h1, re.I
        )
        if m:
            brand = m.group(1)

    # 4) фолбек: прибрати дужки/число і стоп-слова
    if not brand:
        tmp = re.sub(r"\(.*?\)", "", h1)
        tmp = re.sub(r"^[\d\s\u00A0]+\+?\s*", "", tmp)
        tmp = STOPWORDS_RE.sub("", tmp)
        tmp = re.sub(r"[:–—-].*$", "", tmp)
        brand = tmp.strip()

    # фінальна очистка
    brand = re.sub(r"^\s*(?:продаж|продажа|купити|купить)\s+", "", brand, flags=re.I)
    brand = re.sub(r"\s+", " ", brand).strip()
    brand = re.sub(r"^\W+|\W+$", "", brand)

    if not brand or brand.isdigit():
        brand = _brand_from_url(url)

    up = brand.upper()
    brand = up if up in ACRONYMS else brand
    return brand, count

# ---------- HTTP ----------
def fetch_h1_http(url: str, timeout: float = 25.0) -> str:
    import httpx
    from bs4 import BeautifulSoup
    r = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    h1 = soup.select_one("h1")
    return h1.get_text(" ", strip=True) if h1 else ""

# ---------- Playwright fallback (на випадок рендеру JS) ----------
async def fetch_h1_js(url: str, headless: bool = True, goto_timeout: int = 25000, h1_timeout: int = 8000) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        ctx = await browser.new_context(locale="uk-UA", user_agent=UA)
        page = await ctx.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=goto_timeout)
        try:
            await page.wait_for_selector("h1", timeout=h1_timeout)
        except Exception:
            pass
        try:
            h1 = await page.locator("h1").first.inner_text()
        except Exception:
            h1 = ""
        await ctx.close(); await browser.close()
        return (h1 or "").strip()

# ---------- Збереження ----------
def save_csv(rows: List[dict], outfile: str) -> Path:
    out = Path(outfile)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["Brand", "Count"], delimiter=";")
        w.writeheader()
        w.writerows(rows)
    return out

# ---------- обробка одного URL ----------
async def process_url(url: str, headless: bool) -> Tuple[str, int]:
    brand, count = "", None
    try:
        h1 = fetch_h1_http(url)
        brand, count = parse_h1(h1, url)
    except Exception:
        pass
    if not brand or count is None:
        try:
            h1 = await fetch_h1_js(url, headless=headless)
            b2, c2 = parse_h1(h1, url)
            if b2: brand = b2
            if c2 is not None: count = c2
        except Exception:
            pass
    brand = brand or _brand_from_url(url)
    count = count if isinstance(count, int) and count >= 0 else 0
    return brand, count

# ---------- CLI ----------
def build_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", default="links_autoria.txt")
    ap.add_argument("--outfile", default="vuvod/UA_autoria.csv")
    ap.add_argument("--headless", type=int, default=1, help="1=headless, 0=visible")
    return ap

def main():
    args = build_parser().parse_args()
    urls = read_links(args.infile)

    import asyncio
    rows: List[dict] = []
    for url in urls:
        brand, count = asyncio.run(process_url(url, bool(args.headless)))
        print(f"{brand} - {count}")           # тільки "Марка - Кількість"
        rows.append({"Brand": brand, "Count": count})

    out_path = save_csv(rows, args.outfile)
    print(f"\n[OK] Saved {len(rows)} rows → {out_path}")

if __name__ == "__main__":
    main()
