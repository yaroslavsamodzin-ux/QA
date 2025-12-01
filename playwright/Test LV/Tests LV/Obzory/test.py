# tests/reviews_check.py
# pip install playwright
# python -m playwright install

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeoutError
from urllib.parse import urljoin, urlparse
import re, csv

LIST_URL   = "https://automoto.ua/uk/overview"
HOST       = "https://automoto.ua"
OUT_CSV    = "reviews_indexability_ua.csv"
HEADLESS   = True
NAV_TIMEOUT = 45_000

# детальні сторінки оглядів
DETAIL_RE = re.compile(r"^https?://automoto\.ua\/uk/overview/.+/\d+\.html$", re.I)

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
    # на випадок lazy-load
    smooth_scroll_to_bottom(page)
    found = set()
    for a in page.locator("a[href*='/uk/overview/']").all():
        href = a.get_attribute("href") or ""
        if not href:
            continue
        url = href if href.startswith("http") else urljoin(HOST, href)
        if DETAIL_RE.match(url):
            found.add(url)
    return found

def find_next_page_href(page):
    selectors = [
        "a[rel='next']",
        "a[aria-label*='след']",                 # Следующая
        "a[title*='следующ']",
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
            if val:
                if not val.startswith("/"): val = "/" + val
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

# ---------- ВІДЕО-ПЕРЕВІРКА ----------
def check_video_status(page):
    """
    has_embed:   чи є youtube-iframe на сторінці
    error_found: чи є .ytp-error / .ytp-error-content всередині будь-якого iframe
    error_text:  текст повідомлення (як вдасться прочитати)
    """
    # 1) кількість iframes визначаємо ЛИШЕ через Locator
    iframe_sel = "iframe[src*='youtube.com/embed'], iframe[src*='youtu.be/embed']"
    iframe_loc = page.locator(iframe_sel)
    iframe_count = iframe_loc.count()
    if iframe_count == 0:
        return False, False, ""

    # 2) перевіряємо кожен iframe окремо через frame_locator(...).nth(i)
    error_found, error_text = False, ""
    for i in range(iframe_count):
        fl = page.frame_locator(iframe_sel).nth(i)
        err_loc = fl.locator(".ytp-error, .ytp-error-content")
        if err_loc.count():
            error_found = True
            try:
                # пробуємо дістати текст помилки, якщо є
                txt = err_loc.first.inner_text(timeout=1500)
                if txt:
                    error_text = txt
            except Exception:
                pass

    return True, error_found, error_text

# -------------------------------------

def main():
    rows, fails = [], 0
    with sync_playwright() as p:
        http = p.request.new_context()
        rbt = http.get(f"{HOST}/robots.txt")
        disallows = parse_robots_text(rbt.text() if rbt.ok else "")

        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(locale="ru-RU")
        page = ctx.new_page()

        # 1) Збираємо всі огляди з усіх сторінок
        page.goto(LIST_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
        review_links = gather_all_review_links_with_pagination(page)
        print(f"Знайдено оглядів: {len(review_links)}")

        # 2) Перевірка кожного
        for i, url in enumerate(review_links, 1):
            status = "PASS"
            http_code = 0
            robots_blocked = False
            meta_noindex = False
            canonical = ""
            has_embed = False
            video_error = False
            video_error_text = ""

            try:
                r = http.get(url)
                http_code = r.status
                robots_blocked = is_blocked_by_robots(urlparse(url).path, disallows)

                resp = page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
                if resp:
                    http_code = resp.status

                meta_noindex = has_noindex(page)
                canonical = get_canonical(page) or ""

                # ---- перевірка відео ----
                has_embed, video_error, video_error_text = check_video_status(page)

                problems = []
                if http_code != 200:
                    problems.append(f"HTTP {http_code}")
                if robots_blocked:
                    problems.append("robots.txt Disallow")
                if meta_noindex:
                    problems.append("meta noindex")
                if not canonical:
                    problems.append("no canonical")
                # Відео — не блокуємо тест, але фіксуємо статус
                # Якщо хочеш падіння тесту при помилці відео — розкоментуй:
                # if has_embed and video_error:
                #     problems.append("video error (ytp-error)")

                if problems:
                    status = "FAIL: " + ", ".join(problems)
                    fails += 1

            except PwTimeoutError:
                status = "FAIL: timeout"
                fails += 1
            except Exception as e:
                status = f"FAIL: {e!r}"
                fails += 1

            print(f"[{i}/{len(review_links)}] {status} | video: "
                  f"{'no iframe' if not has_embed else ('ERROR' if video_error else 'ok')} → {url}")

            rows.append({
                "URL": url,
                "HTTP": http_code,
                "RobotsBlocked": robots_blocked,
                "MetaNoindex": meta_noindex,
                "Canonical": canonical,
                "HasVideoIframe": has_embed,
                "VideoHasError": video_error,
                "VideoErrorText": video_error_text,
                "Result": status
            })

        browser.close()

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "URL","HTTP","RobotsBlocked","MetaNoindex","Canonical",
                "HasVideoIframe","VideoHasError","VideoErrorText","Result"
            ],
            delimiter=";")
        w.writeheader()
        w.writerows(rows)

    print(f"\n✅ CSV → {OUT_CSV} (rows {len(rows)})")
    print(f"❗ Падінь: {fails}")

if __name__ == "__main__":
    main()
