import csv
import requests
from bs4 import BeautifulSoup

INPUT_CSV = "sitemap_links.csv"
OUTPUT_CSV = "bad_titles.csv"
CSV_DELIMITER = ";"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

TIMEOUT = 0.1

# ❗ Сюди додаєш заборонені placeholder-и
BAD_KEYWORDS = [
    ":region",
    ":gearbox",
    ":make",
    ":model",
    ":body",
    ":bodytype",
    ":engine",
    ":year",
    ":fuel",
]


def title_has_placeholders(title: str) -> bool:
    title_lower = title.lower().replace(" ", "")  # видаляємо пробіли для безпечного пошуку
    return any(bad in title_lower for bad in BAD_KEYWORDS)


def analyze_url(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code != 200:
            return None, [f"HTTP_{resp.status_code}"]

        soup = BeautifulSoup(resp.text, "html.parser")
        title_tag = soup.find("title")

        if not title_tag:
            return None, ["MISSING_TITLE"]

        title_text = title_tag.get_text(strip=True)

        issues = []
        if title_has_placeholders(title_text):
            issues.append("TITLE_PLACEHOLDERS")

        return title_text, issues

    except Exception as e:
        return None, [f"ERROR_{type(e).__name__}"]


def main():
    with open(INPUT_CSV, newline="", encoding="utf-8") as infile, \
         open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile, delimiter=CSV_DELIMITER)
        writer = csv.writer(outfile, delimiter=CSV_DELIMITER)

        writer.writerow(["url", "title", "issues"])

        for row in reader:
            url = row.get("link") or row.get("url")
            if not url:
                continue

            title, issues = analyze_url(url)

            if issues:
                writer.writerow([url, title or "", "|".join(issues)])
                print(f"[BAD] {url} -> {issues}")
            else:
                print(f"[OK] {url}")


if __name__ == "__main__":
    main()
