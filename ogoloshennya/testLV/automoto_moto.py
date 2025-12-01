# tests/automoto_moto_catalog_counts.py

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeoutError
from urllib.parse import urljoin, urlparse
import csv, re, os, time

START_URL = "https://automoto.com.lv/ru/bu-moto/aixam"
OUT_CSV   = "LV_automotomoto_moto.csv"

HEADLESS  = True
SLOWMO_MS = 0
NAV_TIMEOUT = 45_000

def safe_csv_path(path: str) -> str:
    base, ext = os.path.splitext(path)
    try:
        with open(path, "a", encoding="utf-8"):
            pass
        return path
    except PermissionError:
        ts = time.strftime("%Y%m%d-%H%M%S")
        new_path = f"{base}-{ts}{ext}"
        print(f"[WARN] {path} locked → writing to {new_path}")
        return new_path

def nice_brand_from_slug(slug: str) -> str:
    parts = slug.replace("_","-").split("-")
    uppers = {"bmw","ktm","cfmoto","kayo","atv","mg","uaz","vaz","gaz","swm","gac","bsa","kymco","sym"}
    return slug.upper() if slug in uppers else " ".join(p.capitalize() for p in parts)

def extract_count_from_page(page):
    try:
        el = page.get_by_text(re.compile(r"Всего\s+объявлений\s+\d", re.I)).first
        if el and el.is_visible():
            m = re.search(r"Всего\s+объявлений\s+([\d\s.,]+)", el.inner_text(), re.I)
            if m: return int(re.sub(r"\D", "", m.group(1)))
    except Exception:
        pass
    try:
        h1 = page.locator("h1").first
        if h1.count():
            t = h1.inner_text()
            m = re.search(r"все\s+([\d\s.,]+)\s+объявл", t, re.I) or re.search(r"\(([\d\s.,]+)\)", t)
            if m: return int(re.sub(r"\D", "", m.group(1)))
    except Exception:
        pass
    try:
        body = page.inner_text("body")
        m = re.search(r"Всего\s+объявлений\s+([\d\s.,]+)", body, re.I)
        if m: return int(re.sub(r"\D", "", m.group(1)))
    except Exception:
        pass
    return None

def collect_brand_links(page):
    page.wait_for_load_state("domcontentloaded")
    try:
        page.get_by_text(re.compile(r"Поиск\s+Мотоциклы\s+по\s+бренду", re.I)).first.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
    except Exception:
        pass

    container = page.locator(
        "xpath=//h2[contains(translate(normalize-space(.),'АВПЕКМНОРСТХ','авпекмнорстх'),'поиск мотоциклы по бренду')]/"
        "following::*[self::div or self::section][descendant::a[starts-with(@href,'/ru/bu-moto/') "
        "or starts-with(@href,'https://automoto.com.lv/ru/bu-moto/')]][1]"
    ).first
    if not container.count():
        return []

    anchors = container.locator("a[href^='/ru/bu-moto/'], a[href^='https://automoto.com.lv/ru/bu-moto/']").all()

    brand_links = []
    seen = set()
    for a in anchors:
        href = a.get_attribute("href") or ""
        if not href:
            continue
        href_rel = urlparse(href).path if href.startswith("http") else href
        m = re.fullmatch(r"/ru/bu-moto/([a-z0-9\-]+)", href_rel)
        if not m:
            continue
        slug = m.group(1)
        if slug in seen:
            continue
        seen.add(slug)
        brand_links.append((nice_brand_from_slug(slug), urljoin(START_URL, href_rel)))
    return brand_links

def main():
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOWMO_MS)
        context = browser.new_context(locale="ru-RU")
        page = context.new_page()

        page.goto(START_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)

        brand_links = []
        for _ in range(6):
            brand_links = collect_brand_links(page)
            if brand_links: break
            page.wait_for_timeout(350)

        print(f"Найдено брендов: {len(brand_links)}")

        for brand, href in brand_links:
            try:
                page.goto(href, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
                page.wait_for_timeout(300)
                count = extract_count_from_page(page)
                rows.append({"Brand": brand, "Count": count or 0, "URL": href})
                print(f"{brand} {count or 0}")   # ⬅️ тепер виводиться і марка, і кількість
            except PwTimeoutError:
                rows.append({"Brand": brand, "Count": 0, "URL": href})
                print(f"{brand} timeout")
            except Exception as e:
                rows.append({"Brand": brand, "Count": 0, "URL": href})
                print(f"{brand} error {e!r}")

        browser.close()

    out_path = safe_csv_path(OUT_CSV)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Brand", "Count", "URL"], delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ CSV → {out_path} (rows {len(rows)})")

if __name__ == "__main__":
    main()
