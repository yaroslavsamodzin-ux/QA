# autoplius_one_brand.py
# pip install playwright
# python -m playwright install chromium

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeoutError
import csv, re, os

URLS_FILE = "urlsautoplus_moto.txt"
OUT = "LV_autoplus_moto.csv"
ART_DIR = "artifacts"

HEADLESS = False          # для “повної” верстки краще False
SLOW_MO = 0.5               # уповільнення дій для більш "людської" поведінки

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0.0.0 Safari/537.36"
)
ACCEPT_LANG = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"

# слова категорій, які треба прибирати з бренду
CATEGORY_WORDS = {
    "мотоциклы", "мотоцикл", "мото",
    "motociklai", "motociklas", "motocikli", "motocykle", "motocykli",
    "motociklu", "motociklių"
}

def load_urls():
    if not os.path.exists(URLS_FILE):
        print(f"[WARN] {URLS_FILE} not found")
        return []
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]

def clean_brand(s: str) -> str:
    if not s:
        return "?"
    s = s.strip()
    # прибрати лічильник типу " (785)"
    s = re.sub(r"\s*\(\s*[\d\s.,]+\s*\)\s*$", "", s)
    # якщо є кома — беремо до коми ("Honda, Мотоциклы" -> "Honda")
    s = s.split(",", 1)[0].strip()
    # прибрати службові слова
    for w in CATEGORY_WORDS:
        s = re.sub(rf"\b{re.escape(w)}\b", "", s, flags=re.I)
    return " ".join(s.split()) or "?"

def brand_from_title_like(t: str) -> str:
    if not t:
        return "?"
    # шукаємо частину між "—" та "|" або після ") — "
    m = re.search(r"\)\s*[-—–]\s*([^|]+)", t)
    if not m:
        m = re.search(r"[-—–]\s*([^|]+)\|", t)
    return clean_brand(m.group(1)) if m else "?"

def count_from_title_or_body(title: str, body: str) -> str:
    m = re.search(r"\(([\d\s.,]+)\)", title or "")
    if not m:
        m = re.search(r"\(([\d\s.,]+)\)", body or "")
    if m:
        return re.sub(r"\D+", "", m.group(1))
    for pat in [
        r"найдено\s*([\d\s.,]+)", r"([\d\s.,]+)\s*объявл",
        r"([\d\s.,]+)\s*skelb", r"([\d\s.,]+)\s*result"
    ]:
        m = re.search(pat, (body or "").lower())
        if m:
            return re.sub(r"\D+", "", m.group(1))
    return "0"

def brand_from_h3(page) -> str:
    sels = [
        "div.search-list-title h3 a",
        "div.search-list-title h3 span",
        "div.search-list-title h3",
        "h3.search-list-title",
    ]
    for sel in sels:
        loc = page.locator(sel).first
        if loc.count():
            try:
                txt = (loc.inner_text() or "").strip()
                if txt:
                    return clean_brand(txt)
            except Exception:
                pass
    return "?"

def brand_from_first_card(page) -> str:
    sels = [
        ".announcement-title a",
        "a.announcement-title",
        ".search-item .title a",
        ".items-list .title a",
        ".list .title a",
    ]
    for sel in sels:
        loc = page.locator(sel).first
        if loc.count():
            try:
                t = (loc.inner_text() or "").strip()
                if t and len(t) > 2:
                    tokens = re.findall(r"[A-Za-zÀ-ÿĀ-žЁёА-Яа-я0-9\-]+", t)
                    clean = [w for w in tokens if not re.search(r"\d", w)]
                    if clean:
                        if len(clean) >= 2 and clean[1][0].isupper():
                            return clean_brand(f"{clean[0]} {clean[1]}")
                        return clean_brand(clean[0])
            except Exception:
                pass
    return "?"

def scrape_one(page, url: str):
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)

    # лічильник у шапці (коли є)
    count = None
    try:
        page.wait_for_selector("div.search-list-title span.result-count", timeout=15_000)
        raw = page.locator("div.search-list-title span.result-count").first.inner_text()
        count = re.sub(r"\D+", "", raw)
    except PwTimeoutError:
        pass

    # бренд з h3 (пріоритет)
    brand = brand_from_h3(page)
    if brand == "?":
        # og:title → title → перша карточка
        try:
            og = page.locator("meta[property='og:title']").first.get_attribute("content") or ""
        except Exception:
            og = ""
        brand = brand_from_title_like(og) if og else "?"
        if brand == "?":
            brand = brand_from_title_like(page.title())
        if brand == "?":
            brand = brand_from_first_card(page)

    if count is None:
        body = page.inner_text("body")
        count = count_from_title_or_body(page.title(), body)

    return brand, count

def main():
    os.makedirs(ART_DIR, exist_ok=True)
    urls = load_urls()
    if not urls:
        print("[INFO] add links to urlsautoplus_moto.txt")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--lang=ru-RU",
            ],
        )
        context = browser.new_context(
            user_agent=UA,
            viewport={"width": 1536, "height": 960},
            device_scale_factor=1.0,
            locale="ru-RU",
            timezone_id="Europe/Vilnius",
            extra_http_headers={"Accept-Language": ACCEPT_LANG},
        )
        # мінімізуємо детект автомата
        context.add_init_script("""
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
Object.defineProperty(navigator, 'language', { get: () => 'ru-RU' });
Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU','ru','en-US','en'] });
        """)
        page = context.new_page()

        rows = []
        for i, url in enumerate(urls, 1):
            try:
                brand, count = scrape_one(page, url)
                if brand == "?":  # збережемо артефакти для дебагу
                    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", url)
                    page.screenshot(path=os.path.join(ART_DIR, f"{safe}.png"), full_page=True)
                    with open(os.path.join(ART_DIR, f"{safe}.html"), "w", encoding="utf-8") as f:
                        f.write(page.content())
                rows.append([brand, count, url])
                print(f"[{i}/{len(urls)}] {brand} | {count}")
            except Exception as e:
                print(f"[ERR] {url}: {e}")
                rows.append(["?", "0", url])

        browser.close()

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Brand", "Count", "URL"])
        w.writerows(rows)
    print(f"✅ Saved {OUT}")

if __name__ == "__main__":
    main()
