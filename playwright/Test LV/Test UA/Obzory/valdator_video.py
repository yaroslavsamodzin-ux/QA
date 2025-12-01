# ua_reviews_video_check.py
# pip install playwright
# python -m playwright install

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeoutError
from urllib.parse import urljoin
import re, csv, os

HOST        = "https://automoto.ua"
LIST_URL    = f"{HOST}/uk/overview"
OUT_CSV     = "ua_reviews_video.csv"
HEADLESS    = True
NAV_TIMEOUT = 45_000

# /uk/overview/.../<id> або <id>.html
DETAIL_RE = re.compile(r"^https?://automoto\.ua/uk/overview/.+/\d+(?:\.html)?$", re.I)

CARD_LINK_SELECTOR = (
    # найбільш типові варіанти
    "div.card a.stretched-link,"
    "article.card a.stretched-link,"
    ".card a.stretched-link,"
    # запасні варіанти, якщо картка без stretched-link
    "div.card a[href*='/uk/overview/'],"
    "article.card a[href*='/uk/overview/']"
)

def ensure_cards_loaded(page):
    """
    Чекаємо, поки з’являться хоч якісь картки.
    Якщо за 5с не з’явились — зробимо прокрутку і ще раз почекаємо.
    """
    try:
        page.wait_for_selector(CARD_LINK_SELECTOR, state="visible", timeout=5000)
    except Exception:
        # інколи контент ледачий — прокрутимо і ще раз почекаємо
        page.mouse.wheel(0, 40000)
        page.wait_for_timeout(500)
        page.wait_for_selector(CARD_LINK_SELECTOR, state="visible", timeout=5000)

def smooth_scroll_to_bottom(page, max_rounds=20, pause_ms=300):
    last_h = -1
    for _ in range(max_rounds):
        h = page.evaluate("document.body.scrollHeight")
        if h == last_h:
            break
        page.mouse.wheel(0, 40000)
        page.wait_for_timeout(pause_ms)
        last_h = h

def collect_review_links(page, page_no: int) -> set[str]:
    ensure_cards_loaded(page)
    smooth_scroll_to_bottom(page)

    found = set()
    # збір через JS — швидше й надійніше
    hrefs = page.eval_on_selector_all(
        CARD_LINK_SELECTOR,
        "els => els.map(a => a.getAttribute('href') || '')"
    )
    for href in hrefs:
        if not href:
            continue
        url = href if href.startswith("http") else urljoin(HOST, href)
        if DETAIL_RE.match(url):
            found.add(url)

    # якщо все ще 0 — збережемо дебаг
    if not found:
        os.makedirs("debug", exist_ok=True)
        with open(f"debug/overview_page{page_no}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        with open(f"debug/overview_links{page_no}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(hrefs))
        print(f"DEBUG: на сторінці {page_no} посилань не знайдено. "
              f"Збережено debug/overview_page{page_no}.html та overview_links{page_no}.txt")
    return found

def extract_max_page(page) -> int:
    max_page = 1
    # дочекаймося пагінації, якщо вона є
    try:
        page.wait_for_selector("ul.pagination a.page-link", timeout=3000)
    except Exception:
        pass
    for a in page.locator("ul.pagination a.page-link").all():
        txt = (a.inner_text() or "").strip()
        if txt.isdigit():
            max_page = max(max_page, int(txt))
    return max_page

def gather_all_review_links_with_pagination(page) -> list[str]:
    all_links = set()
    page.goto(LIST_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
    last_page = extract_max_page(page)

    for num in range(1, last_page + 1):
        url = LIST_URL if num == 1 else f"{LIST_URL}?page={num}"
        page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
        links = collect_review_links(page, num)
        print(f"Сторінка {num}/{last_page}: знайдено {len(links)} лінків")
        all_links |= links

    return sorted(all_links)

def click_third_party_media_consent(page) -> bool:
    candidates = [
        "button:has-text('Only this media')",
        "button:has-text('Always for YouTube')",
        "button.kb.kbs",
        "button[aria-label*='Only this media']",
        "button[aria-label*='Always for YouTube']",
    ]
    for sel in candidates:
        try:
            btn = page.locator(sel).first
            if btn and btn.count() and btn.is_visible():
                btn.click(timeout=1500)
                page.wait_for_timeout(400)
                return True
        except Exception:
            pass
    return False

def check_video_status(page) -> tuple[bool, bool]:
    click_third_party_media_consent(page)
    iframe_sel = "iframe[src*='youtube.com/embed'], iframe[src*='youtu.be/embed']"
    iframe_loc = page.locator(iframe_sel)
    count = iframe_loc.count()
    if count == 0:
        return False, False

    has_error = False
    for i in range(count):
        fl = page.frame_locator(iframe_sel).nth(i)
        if fl.locator(".ytp-error, .ytp-error-content").count():
            has_error = True
    return True, has_error

def main():
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(locale="uk-UA")
        page = ctx.new_page()

        links = gather_all_review_links_with_pagination(page)
        print(f"Знайдено оглядів ВСЬОГО: {len(links)}")

        for i, url in enumerate(links, 1):
            status = "PASS"
            has_iframe, has_error = False, False
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
                has_iframe, has_error = check_video_status(page)
                if not has_iframe:
                    status = "FAIL: немає iframe"
                elif has_error:
                    status = "FAIL: відео помилка (ytp-error)"
            except PwTimeoutError:
                status = "FAIL: timeout"
            except Exception as e:
                status = f"FAIL: {e!r}"

            print(f"[{i}/{len(links)}] {status} → {url}")
            rows.append({
                "URL": url,
                "HasVideoIframe": has_iframe,
                "VideoHasError": has_error,
                "Result": status
            })

        browser.close()

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["URL","HasVideoIframe","VideoHasError","Result"], delimiter=";")
        w.writeheader()
        w.writerows(rows)

    print(f"\n✅ CSV → {OUT_CSV} (rows {len(rows)})")

if __name__ == "__main__":
    main()
