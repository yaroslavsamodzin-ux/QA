import gzip
import csv
import requests
import xml.etree.ElementTree as ET

urls = [
    "https://automoto.com.lv/en/sitemaps/catalog-new.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-1.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-2.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-3.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-4.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-5.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-6.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-7.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-auto-news.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-new-latvia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-new-estonia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-latvia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-estonia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-new-lithuania.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-latvia-1.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-latvia-2.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-latvia-3.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-latvia-4.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-latvia-5.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-latvia-6.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-latvia-7.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-new-latvia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-cars-overviews.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-estonia-1.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-estonia-2.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-estonia-3.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-estonia-4.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-estonia-5.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-estonia-6.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-new-estonia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-latvia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-estonia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-1.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-2.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-3.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-4.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-5.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-6.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-7.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-8.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-9.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-new-lithuania.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-latvia-1.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-latvia-2.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-latvia-3.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-10.xml.gz",
    "https://automoto.com.lv/en/sitemaps/catalog-used-lithuania-11.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-estonia-1.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-estonia-2.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-lithuania.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-lithuania-1.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-lithuania-2.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-lithuania-3.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-lithuania-4.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-lithuania-5.xml.gz",
    "https://automoto.com.lv/en/sitemaps/final-page-used-lithuania-6.xml.gz",
    "https://automoto.com.lv/en/sitemaps/end-page-сar-dealerships-latvia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/end-page-сar-dealerships-estonia.xml.gz",
    "https://automoto.com.lv/en/sitemaps/end-page-сar-dealerships-lithuania.xml.gz"
]

csv_filename = "sitemap_links.csv"

with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["sitemap", "link"])

    for url in urls:
        try:
            xml_gz = requests.get(url).content
            xml = gzip.decompress(xml_gz)

            root = ET.fromstring(xml)

            # Namespace fix
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            for loc in root.findall(".//sm:loc", ns):
                writer.writerow([url, loc.text])
                print("OK:", loc.text)

        except Exception as e:
            print(f"Помилка в {url}: {e}")

print(f"\nГотово! Збережено у {csv_filename}")
