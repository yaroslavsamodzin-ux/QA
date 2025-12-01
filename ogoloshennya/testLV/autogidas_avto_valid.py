# autogidas_brand_totals_ok.py
import asyncio, csv, re, unicodedata, random
from typing import List, Tuple
from urllib.parse import quote

from playwright.async_api import async_playwright, TimeoutError as PwTimeout

BASE = "https://autogidas.lt"
XHR_PATH = "/ajax/category/models"
CATEGORY_ID = "01"
INSERTION = "false"

BRANDS = [
    "Volkswagen",
"BMW",
"Audi",
"Opel",
"Mercedes-Benz",
"Ford",
"Toyota",
"Volvo",
"Skoda",
"Nissan",
"Peugeot",
"Renault",
"Hyundai",
"Seat",
"Citroen",
"Kia",
"Mazda",
"Honda",
"Jeep",
"Subaru",
"Mitsubishi",
"Fiat",
"Chevrolet",
"Porsche",
"Lexus",
"Land Rover",
"Dodge",
"Suzuki",
"Chrysler",
"MINI",
"Cupra",
"Dacia",
"Tesla",
"Jaguar",
"Alfa Romeo",
"Saab",
"Lada",
"Infiniti",
"Iveco",
"Ssangyong",
"Cadillac",
"Maserati",
"Buick",
"GAZ",
"Lincoln",
"Moskvich",
"Smart",
"Daihatsu",
"Acura",
"Hummer",
"Lancia",
"UAZ",
"Isuzu",
"GMC",
"Pontiac",
"ZAZ",
"Aixam",
"Bentley",
"MG",
"DS Automobiles",
"Rover",
"Ligier",
"Microcar",
"Rolls-Royce",
"Maybach",
"Mercury",
"Polestar",
"Kita",
"Alpina",
"Aston Martin",
"Daewoo",
"McLaren",
"Oldsmobile",
"Tata",
"Abarth",
"Casalini",
"Ferrari",
"Geely",
"Hongqi",
"Lamborghini",
"Lotus",
"LuAZ",
"MPM",
"Man",
"Piaggio",
"Shuanghuan",
"Wartburg",
"AC",
"Aro",
"Asia",
"Austin",
"Autobianchi",
"BYD",
"Baic",
"Bellier",
"Brilliance",
"Bugatti",
"Caterham",
"Chatenet",
"CityEL",
"Comarth",
"DAF",
"DFSK",
"DKW",
"De Lorean",
"EMoto",
"Eagle",
"Excalibur",
"FAW",
"Fisker",
"GWM",
"Galloper",
"Genesis",
"Gonow",
"Goupil",
"Grecav",
"Holden",
"JAC",
"Kaipan",
"Koenigsegg",
"LDV",
"LTI",
"Landwind",
"Lynk & Co",
"Mahindra",
"Maruti",
"Morgan",
"NSU",
"Nysa",
"Oltcit",
"Ora",
"Pinzgauer",
"Plymouth",
"Polonez",
"Proton",
"Samsung",
"Santana",
"Saturn",
"Scion",
"Syrena",
"TVR",
"Talbot",
"Tarpan",
"Tatra",
"Tavria",
"Tazzari",
"Think",
"Trabant",
"Triumph",
"Vauxhall",
"Warszawa",
"Weismann",
"Xpeng",
"Yugo",
"Yunlong Motors",
"Zastava",
"Zuk",
]

OUT_CSV = "vuvod/LV_autogidas_avto.csv"

# ---------- helpers ----------
def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").strip().casefold()
    return " ".join(s.split())

def slugify_brand(brand: str) -> str:
    # slug для /automobiliai/<slug>/
    s = unicodedata.normalize("NFKD", brand)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))  # без діакритики
    s = s.replace("&", "and").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def extract_total(payload: dict, brand: str) -> Tuple[str, int]:
    want = norm(brand)
    for item in payload.get("data", []):
        title = (item.get("title") or "").strip()
        if not title.lower().startswith("visi "):
            continue
        after = title[5:].strip()
        if norm(after) == want:
            try:
                return after, int(item.get("count", 0))
            except Exception:
                return after, 0
    return brand, 0

async def try_accept_cookies(page):
    sels = [
        'button:has-text("Sutinku")',
        'button:has-text("Sutikti")',
        'button:has-text("Accept")',
        'button[aria-label*="Accept"]',
        'button:has-text("Priimti")',
    ]
    for sel in sels:
        try:
            btn = await page.wait_for_selector(sel, timeout=1500)
            await btn.click()
            await page.wait_for_timeout(300)
            break
        except PwTimeout:
            continue

async def fetch_models_json_in_page(page, brand: str) -> dict:
    url = (
        f"{BASE}{XHR_PATH}?category_id={CATEGORY_ID}"
        f"&make={quote(brand, safe='')}"
        f"&insertion={INSERTION}"
    )
    js = f"""
        async () => {{
            const resp = await fetch("{url}", {{
                headers: {{
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "application/json, text/plain, */*",
                }},
                credentials: "include"
            }});
            const ct = resp.headers.get("content-type") || "";
            const text = await resp.text();
            return {{ status: resp.status, ct, text }};
        }}
    """
    result = await page.evaluate(js)
    text = result.get("text") or ""
    if "json" in (result.get("ct") or "").lower() or text.strip().startswith(("{", "[")):
        import json
        return json.loads(text)
    raise RuntimeError(f"NON-JSON (status={result.get('status')}, ct={result.get('ct')})")

# ---------- main ----------
async def main(brands: List[str]):
    rows: List[Tuple[str, int]] = []

    async with async_playwright() as p:
        # Використаємо звичайний Chrome-канал і видимий режим
        browser = await p.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context(
            locale="lt-LT",
            timezone_id="Europe/Vilnius",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"),
        )
        # Приберемо navigator.webdriver
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        page = await context.new_page()

        # 1) Зайдемо на головну, приймемо кукі
        await page.goto(BASE + "/", wait_until="domcontentloaded")
        await try_accept_cookies(page)
        await page.wait_for_timeout(800)

        for i, brand in enumerate(brands, 1):
            slug = slugify_brand(brand)
            try:
                # 2) Сторінка бренду — тут стаються токени/куки
                await page.goto(f"{BASE}/automobiliai/{slug}/", wait_until="networkidle")
                await page.wait_for_timeout(700 + int(random.random()*400))

                # 3) У цій сторінці робимо fetch -> JSON
                payload = await fetch_models_json_in_page(page, brand)
                bclean, total = extract_total(payload, brand)
                rows.append((bclean, total))
                print(f"[{i}/{len(brands)}] {bclean}: {total}")
            except Exception as e:
                print(f"[{i}] {brand}: ERROR {e}")
                rows.append((brand, 0))

        await browser.close()

    # --- Запис у CSV з роздільником ; ---
    from csv import DictWriter
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = DictWriter(f, fieldnames=["Brand", "Count"], delimiter=";")
        writer.writeheader()
        for brand, count in rows:
            writer.writerow({"Brand": brand, "Count": count})

    print(f"\nSaved: {OUT_CSV} ({len(rows)} brands)")

if __name__ == "__main__":
    asyncio.run(main(BRANDS))
