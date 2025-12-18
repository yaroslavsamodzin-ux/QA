import requests
import gzip
import csv
import xml.etree.ElementTree as ET

USER = "developer"
PASS = "gfhjkm2012"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
}

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

OUT_FILE = "automoto_links.csv"

# ✅ СЮДИ ВСТАВЛЯЄШ СВОЇ URL-и
INPUT_URLS = [
    "https://new2.automoto.com.lv/en/sitemaps/catalog-new.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-1.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-2.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-3.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-4.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-5.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-6.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-auto-news.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-new-latvia.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-new-estonia.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-latvia.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-estonia.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-new-lithuania.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-latvia-1.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-latvia-2.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-latvia-3.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-latvia-4.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-latvia-5.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-latvia-6.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-latvia-7.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-new-latvia.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-cars-overviews.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-estonia-1.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-estonia-2.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-estonia-3.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-estonia-4.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-estonia-5.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-estonia-6.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-new-estonia.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-latvia.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-estonia.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-1.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-2.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-3.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-4.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-5.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-6.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-7.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-8.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-9.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-new-lithuania.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-latvia-1.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-latvia-2.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-latvia-3.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-10.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/catalog-used-lithuania-11.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-estonia-1.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-estonia-2.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-lithuania.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-lithuania-1.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-lithuania-2.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-lithuania-3.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-lithuania-4.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-lithuania-5.xml.gz",
    "https://new2.automoto.com.lv/en/sitemaps/final-page-used-lithuania-6.xml.gz"
]


def fetch_bytes(url: str) -> bytes:
    r = requests.get(
        url,
        headers=HEADERS,
        auth=(USER, PASS),
        timeout=60,
        allow_redirects=True,
    )
    r.raise_for_status()
    data = r.content
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data)
    return data


def try_extract_sitemap_locs(content: bytes) -> list[str] | None:
    """Пробує розпарсити як sitemap XML і витягнути <loc>. Якщо не sitemap — повертає None."""
    try:
        root = ET.fromstring(content)
        locs = [x.text for x in root.findall(".//sm:loc", NS) if x.text]
        return locs if locs else []
    except ET.ParseError:
        return None


def main():
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["url"])

        total_written = 0

        for url in INPUT_URLS:
            try:
                content = fetch_bytes(url)
                locs = try_extract_sitemap_locs(content)

                # Якщо це sitemap — записуємо всі <loc>
                if locs is not None:
                    for loc in locs:
                        writer.writerow([loc])
                        total_written += 1
                    print(f"SITEMAP {url} -> {len(locs)} urls")
                else:
                    # Якщо це НЕ sitemap — записуємо як звичайний URL
                    writer.writerow([url])
                    total_written += 1
                    print(f"URL {url} -> saved as single link")

            except Exception as e:
                print(f"ERROR {url}: {e}")

    print(f"TOTAL WRITTEN: {total_written}")
    print(f"Saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
