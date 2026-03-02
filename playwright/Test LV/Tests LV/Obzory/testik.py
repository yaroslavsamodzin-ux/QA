import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import csv

BASE_URL = "https://automoto.ua"
START_PAGE = 2
END_PAGE = 250
SLEEP = 0.2

HEADERS = {"User-Agent": "Mozilla/5.0 (QA SEO Test)"}

IGNORED_URLS = {
    "https://automoto.ua/uk/price-banners",
    "https://automoto.ua/uk/oplata-shtrafov",
    "https://automoto.ua/uk/book-new-auto",
    "https://automoto.ua/uk/feedback",
    "https://automoto.ua/uk/about",
}


def normalize_url(u: str) -> str:
    """ прибираємо #, фінальний / (щоб стабільно порівнювати) """
    u = (u or "").split("#")[0]
    if u.endswith("/") and u != BASE_URL + "/":
        u = u[:-1]
    return u


IGNORED_URLS = {normalize_url(u) for u in IGNORED_URLS}


def get_soup(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def normalize_robots(content: str) -> str:
    return (content or "").lower().replace(" ", "")


def robots_value(url: str) -> str:
    soup = get_soup(url)
    meta = soup.find("meta", attrs={"name": "robots"})
    if not meta:
        return ""  # meta robots нема
    return normalize_robots(meta.get("content", ""))


def extract_internal_links(listing_url: str) -> list[str]:
    soup = get_soup(listing_url)

    links = set()
    base_host = urlparse(BASE_URL).netloc

    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue

        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue

        full = normalize_url(urljoin(BASE_URL, href))
        parsed = urlparse(full)

        # тільки цей домен
        if parsed.netloc != base_host:
            continue

        # ігноримо задані сторінки (і не скануємо, і не виводимо)
        if full in IGNORED_URLS:
            continue

        links.add(full)

    return sorted(links)


def run():
    noindex_follow_urls = []
    scanned = 0

    for page in range(START_PAGE, END_PAGE + 1):
        listing_url = f"{BASE_URL}/uk/newauto?page={page}"
        print(f"\nPAGE {page}: {listing_url}")

        try:
            urls = extract_internal_links(listing_url)
        except Exception as e:
            print(f"❌ failed to parse listing: {e}")
            continue

        print(f"Found {len(urls)} internal links (after ignore)")

        for u in urls:
            # додатковий захист (на випадок, якщо десь підтягнеться)
            if u in IGNORED_URLS:
                continue

            scanned += 1
            try:
                rv = robots_value(u)  # наприклад "index,follow" або "noindex,follow"
                if rv == "noindex,follow":
                    noindex_follow_urls.append(u)
                    print(f"✅ NOINDEX,FOLLOW: {u}")
            except Exception as e:
                print(f"⚠️ error on {u}: {e}")

            time.sleep(SLEEP)

    print("\n========== RESULT ==========")
    print(f"Scanned URLs: {scanned}")
    print(f"noindex,follow found: {len(noindex_follow_urls)}")

    out_file = "noindex_follow_urls.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url"])
        for u in noindex_follow_urls:
            w.writerow([u])

    print(f"Saved: {out_file}")


if __name__ == "__main__":
    run()
