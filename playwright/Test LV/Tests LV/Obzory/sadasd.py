import requests

urls = [
    "https://new.automoto.ua/uk/car",
    "https://new.automoto.ua/uk/car/audi",
    "https://new.automoto.ua/uk/car/audi/a3",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://new.automoto.ua/",
}

s = requests.Session()
for url in urls:
    r = s.get(url, headers=headers, allow_redirects=True, timeout=15)
    chain = [h.status_code for h in r.history] + [r.status_code]
    print(url, "->", chain)
