# tests/reviews_check.py
# pip install playwright
# python -m playwright install
# перевяємо статус код 200. відсутність блокувань robots.txt, meta noindex, наявність канонікалу
# збираємо лінки з усіх сторінок пагінації
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeoutError
from urllib.parse import urljoin, urlparse
import re, csv

LIST_URL   = "https://automoto.com.lv/ru/obzory-avto"
HOST       = "https://automoto.com.lv"
OUT_CSV    = "index_obzoriv.csv"
HEADLESS   = True
NAV_TIMEOUT = 45_000

# детальні сторінки оглядів
DETAIL_RE = re.compile(r"^https?://automoto\.com\.lv/ru/obzory-avto/.+/\d+\.html$", re.I)

def smooth_scroll_to_bottom(page, max_rounds=20, pause_ms=400):
    same, last_h = 0, -1
    for _ in range(max_rounds):
        h = page.evaluate("document.body.scrollHeight")
        if h == last_h:
            same += 1
            if same >= 2:
                break
        else:
            same = 0
        page.mouse.wheel(0, 40000)
        page.wait_for_timeout(pause_ms)
        last_h = h

def collect_review_links(page):
    smooth_scroll_to_bottom(page)
    found = set()
    for a in page.locator("a[href*='/ru/obzory-avto/']").all():
        href = a.get_attribute("href") or ""
        if not href:
            continue
        url = href if href.startswith("http") else urljoin(HOST, href)
        if DETAIL_RE.match(url):
            found.add(url)
    return found

def find_next_page_href(page):
    """Повертає href на наступну сторінку або None."""
    selectors = [
        "a[rel='next']",
        "a[aria-label*='след']",                 # 'Следующая'
        "a[title*='следующ']",                   # title="Перейти на следующую страницу"
        "nav[aria-label='Page navigation'] a[title*='следующ']",
        "nav[aria-label='Page navigation'] a[rel='next']",
    ]
    for sel in selectors:
        loc = page.locator(sel).first
        if loc.count():
            href = loc.get_attribute("href")
            if href:
                return href if href.startswith("http") else urljoin(HOST, href)
    return None

def gather_all_review_links_with_pagination(page):
    """Обійти всі сторінки пагінації та зібрати унікальні лінки оглядів."""
    all_links, visited_pages = set(), set()
    current_url = LIST_URL

    while current_url and current_url not in visited_pages:
        visited_pages.add(current_url)
        page.goto(current_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
        all_links |= collect_review_links(page)
        next_url = find_next_page_href(page)
        if not next_url or next_url in visited_pages:
            break
        current_url = next_url

    return sorted(all_links)

def parse_robots_text(text: str):
    rules, ua_all = [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.lower().startswith("user-agent:"):
            ua_all = line.split(":", 1)[1].strip() == "*"
        elif ua_all and line.lower().startswith("disallow:"):
            val = line.split(":", 1)[1].strip()
            if val and not val.startswith("#"):
                if not val.startswith("/"):
                    val = "/" + val
                rules.append(val)
        elif line.lower().startswith("user-agent:") and ua_all:
            ua_all = False
    return rules

def is_blocked_by_robots(path: str, disallows: list[str]) -> bool:
    return any(path.startswith(rule) for rule in disallows)

def has_noindex(page) -> bool:
    metas = page.locator("meta[name='robots'], meta[name='googlebot']").all()
    for m in metas:
        content = (m.get_attribute("content") or "").lower()
        if "noindex" in content or content.strip() == "none":
            return True
    return False

def get_canonical(page) -> str | None:
    loc = page.locator("link[rel='canonical']").first
    return loc.get_attribute("href") if loc.count() else None

def main():
    rows, fails = [], 0
    with sync_playwright() as p:
        http = p.request.new_context()
        # robots.txt
        rbt = http.get(f"{HOST}/robots.txt")
        disallows = parse_robots_text(rbt.text() if rbt.ok else "")

        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(locale="ru-RU")
        page = ctx.new_page()

        # 1) збір лінків з усіх сторінок пагінації
        page.goto(LIST_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
        review_links = gather_all_review_links_with_pagination(page)
        print(f"Знайдено оглядів (усі сторінки): {len(review_links)}")

        # 2) перевірка кожного огляду
        for i, url in enumerate(review_links, 1):
            status = "PASS"
            http_code = 0
            robots_blocked = False
            meta_noindex = False
            canonical = ""

            try:
                r = http.get(url)
                http_code = r.status

                robots_blocked = is_blocked_by_robots(urlparse(url).path, disallows)

                resp = page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
                if resp:
                    http_code = resp.status

                meta_noindex = has_noindex(page)
                canonical = get_canonical(page) or ""

                problems = []
                if http_code != 200:
                    problems.append(f"HTTP {http_code}")
                if robots_blocked:
                    problems.append("robots.txt Disallow")
                if meta_noindex:
                    problems.append("meta noindex")
                if not canonical:
                    problems.append("no canonical")

                if problems:
                    status = "FAIL: " + ", ".join(problems)
                    fails += 1

            except PwTimeoutError:
                status = "FAIL: timeout"
                fails += 1
            except Exception as e:
                status = f"FAIL: {e!r}"
                fails += 1

            print(f"[{i}/{len(review_links)}] {status} → {url}")
            rows.append({
                "URL": url,
                "HTTP": http_code,
                "RobotsBlocked": robots_blocked,
                "MetaNoindex": meta_noindex,
                "Canonical": canonical,
                "Result": status
            })

        browser.close()

    # 3) CSV
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["URL","HTTP","RobotsBlocked","MetaNoindex","Canonical","Result"], delimiter=";")
        w.writeheader()
        w.writerows(rows)

    print(f"\n✅ CSV → {OUT_CSV} (rows {len(rows)})")
    print(f"❗ Падінь: {fails}")

if __name__ == "__main__":
    main()

