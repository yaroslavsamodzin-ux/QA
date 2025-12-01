# -*- coding: utf-8 -*-
import asyncio, re, csv, argparse
from pathlib import Path
from typing import List, Tuple
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

URL = "https://traktorist.ua/catalog?page=1&country=ukraina&"

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def parse_label_text(txt: str) -> Tuple[str, int] | None:
    """
    Очікуємо щось на кшталт:
    'John Deere (1 763)' або з переносами
    """
    t = norm(txt)
    # забираємо перенос/пробіли між назвою і дужками
    m = re.search(r"^(.*?)\s*\(([\d\s]+)\)\s*$", t)
    if not m:
        return None
    brand = norm(m.group(1))
    count = int(re.sub(r"[^\d]", "", m.group(2)))
    if not brand or count < 0:
        return None
    return brand, count

async def expand_brands_block(page) -> None:
    """
    Розкриваємо список брендів. Уникаємо пагінації:
    клікаємо лише div/span з точним текстом 'Показати більше'
    поруч із заголовком 'Бренди'.
    """
    # кілька стратегій пошуку заголовка
    hdr = page.locator("//h3[contains(normalize-space(.), 'Брен')]").first
    try:
        await hdr.wait_for(state="attached", timeout=8000)
    except PWTimeout:
        # інколи блок рендериться пізніше — прокрутимо сторінку
        await page.mouse.wheel(0, 700)
        await page.wait_for_timeout(600)

    # клікаємо лише div/span в межах секції з брендами
    # 1) пробуємо відносно заголовка
    more = page.locator(
        "(//h3[contains(normalize-space(.),'Брен')])[1]"
        "/following::div[1]//div[normalize-space()='Показати більше']"
    )
    # 2) запасний: будь-який div/span 'Показати більше', але не <a> (щоб не чіпати пагінацію)
    if await more.count() == 0:
        more = page.locator(
            "//div[normalize-space()='Показати більше'] | //span[normalize-space()='Показати більше']"
        )

    # кілька кліків, поки є що розкривати
    for _ in range(6):
        try:
            if await more.first.is_visible():
                await more.first.scroll_into_view_if_needed()
                await more.first.click()
                await page.wait_for_timeout(700)
            else:
                break
        except PWTimeout:
            break
        except Exception:
            break

async def collect_brands(page) -> List[Tuple[str, int]]:
    """
    Збираємо всі <label> з чекбоксами брендів і парсимо назву/кількість.
    Працює і без точного заголовка.
    """
    labels = page.locator("//label[.//input[@type='checkbox']]")
    n = await labels.count()
    items: List[Tuple[str, int]] = []

    for i in range(n):
        txt = await labels.nth(i).inner_text()
        p = parse_label_text(txt)
        if p:
            items.append(p)

    # прибираємо дублікати, зберігаючи першу появу (початкова послідовність)
    seen = set()
    ordered: List[Tuple[str, int]] = []
    for b, c in items:
        if b not in seen:
            seen.add(b)
            ordered.append((b, c))
    return ordered

async def scrape_traktorist(url: str, headless: bool, timeout: int) -> List[Tuple[str, int]]:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        ctx = await browser.new_context(locale="uk-UA", viewport={"width": 1280, "height": 900})
        page = await ctx.new_page()

        print(f"[INFO] Відкриваю {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout)

        # cookie/банер (якщо з’явиться)
        for sel in ("button:has-text('Приймаю')", "button:has-text('Погоджуюсь')", "button:has-text('Добре')"):
            try:
                el = page.locator(sel).first
                if await el.is_visible():
                    await el.click()
                    await page.wait_for_timeout(300)
                    break
            except Exception:
                pass

        # пробуємо розкрити бренди
        await expand_brands_block(page)
        # на всяк випадок — невеликий скрол, щоб підвантажились ліниві елементи
        await page.mouse.wheel(0, 600)
        await page.wait_for_timeout(400)

        rows = await collect_brands(page)

        await ctx.close()
        await browser.close()
        return rows

def save_csv(rows: List[Tuple[str, int]], outfile: str) -> None:
    Path(outfile).parent.mkdir(parents=True, exist_ok=True)
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Brand", "Count"])
        for b, c in rows:
            w.writerow([b, c])
    print(f"[OK] Збережено {len(rows)} рядків ➜ {outfile}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=URL)
    ap.add_argument("--headless", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=60000)
    ap.add_argument("--outfile", default="reports/traktorist_brands.csv")
    args = ap.parse_args()

    try:
        rows = asyncio.run(scrape_traktorist(args.url, bool(args.headless), args.timeout))
    except PWTimeout:
        rows = []
    save_csv(rows, args.outfile)

if __name__ == "__main__":
    main()
