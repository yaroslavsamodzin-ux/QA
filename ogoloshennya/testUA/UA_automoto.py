# -*- coding: utf-8 -*-
"""
Збірка "Марка ; Кількість" зі сторінки https://automoto.ua/uk/
— приймає cookies
— розгортає (якщо є) блок "усі марки"
— збирає бренди як з верхнього гріда (.row.mark_auto-new), так і з розгорнутого блоку
— зберігає у reports/automoto_brands.csv (Brand;Count) і друкує у консоль
"""

import re
import csv
from pathlib import Path
from typing import Optional, List, Tuple
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

HOME_URL = "https://automoto.ua/uk/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# (16539) або (16 539) або (16 539+)
COUNT_RX = re.compile(r"\(([\d\s\u00A0]+)\+?\)")

def to_int(s: Optional[str]) -> int:
    if not s:
        return 0
    d = re.sub(r"[^\d]", "", s)
    return int(d) if d.isdigit() else 0


async def accept_cookies(page):
    # кілька варіантів підписів
    for txt in ("Прийняти", "Погоджуюсь", "Принять", "Согласен", "Accept", "Allow all"):
        try:
            btn = page.get_by_role("button", name=re.compile(txt, re.I)).first
            if await btn.is_visible():
                await btn.click()
                await page.wait_for_timeout(250)
                break
        except Exception:
            pass


async def try_expand_all(page):
    """Спроба натиснути 'Показати всі марки' (якщо є)."""
    selectors = [
        "a[data-target='#collapseMark']",
        "a[role='button'][data-toggle='collapse']",
        "span.more:has-text('Показати всі марки')",
        "text=Показати всі марки",
        "text=Показать все марки",
    ]
    clicked = False
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if await el.is_visible():
                await el.scroll_into_view_if_needed()
                await el.click()
                clicked = True
                break
        except Exception:
            pass

    if not clicked:
        # резерв: спробувати розгорнути через JS (на випадок, якщо бутстраповий collapse)
        try:
            await page.evaluate("""
              () => {
                const ids = ['collapseMark','collapseMarks','collapseBrand','collapseBrands'];
                for (const id of ids) {
                  const n = document.getElementById(id);
                  if (n) { n.classList.add('show'); }
                }
              }
            """)
        except Exception:
            pass

    # зачекати появи елементів у розгорнутому блоці (якщо він існує)
    try:
        await page.wait_for_selector("#collapseMark a, #collapseMarks a, #collapseBrand a, #collapseBrands a", timeout=3000)
    except PWTimeout:
        pass


async def collect_from_grid(page) -> List[Tuple[str, int]]:
    """
    Верхній грід 'Популярні марки'
    структура: div.row.mark_auto-new > div.col-4 ... всередині <a> з назвою,
    а число в дужках поруч/нижче. Беремо текст усієї плитки, щоб не втратити число.
    """
    tiles = page.locator("div.row.mark_auto-new > div.col-4")
    n = await tiles.count()
    out: List[Tuple[str,int]] = []
    for i in range(n):
        t = tiles.nth(i)
        try:
            text = (await t.inner_text()).strip()
        except Exception:
            continue
        # виділити (число) і назву без дужок
        m = COUNT_RX.search(text)
        count = to_int(m.group(1)) if m else 0
        brand = re.sub(r"\(\s*[\d\s\+]+\s*\)", "", text).strip()
        brand = re.sub(r"\s+", " ", brand)
        # інколи в плитці багато рядків — беремо перший "словесний" рядок як бренд
        if "\n" in brand:
            for part in (p.strip() for p in brand.splitlines()):
                if part and not COUNT_RX.search(part):
                    brand = part
                    break
        if brand:
            out.append((brand, count))
    return out


async def collect_from_collapse(page) -> List[Tuple[str, int]]:
    """
    Розгорнутий список брендів (якщо є).
    Беремо всі <a> всередині collapse* і парсимо 'Назва (число)'.
    """
    anchors = page.locator("#collapseMark a, #collapseMarks a, #collapseBrand a, #collapseBrands a")
    n = await anchors.count()
    out: List[Tuple[str,int]] = []
    for i in range(n):
        a = anchors.nth(i)
        try:
            txt = (await a.inner_text()).strip()
        except Exception:
            continue
        m = COUNT_RX.search(txt)
        count = to_int(m.group(1)) if m else 0
        brand = re.sub(r"\(\s*[\d\s\+]+\s*\)", "", txt).strip()
        brand = re.sub(r"\s+", " ", brand)
        if brand:
            out.append((brand, count))
    return out


async def run(headless: bool, outfile: str):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        ctx = await browser.new_context(locale="uk-UA", user_agent=UA, viewport={"width": 1366, "height": 900})

        # відрізаємо зайву аналітику, щоб пришвидшити
        noisy = ("googletagmanager", "google-analytics", "hotjar", "clarity", "doubleclick", "optimizely", "segment")
        await ctx.route("**/*", lambda r: r.abort() if any(x in r.request.url for x in noisy) else r.continue_())

        page = await ctx.new_page()
        await page.goto(HOME_URL, wait_until="domcontentloaded", timeout=30000)
        await accept_cookies(page)

        # прокрутимо до блоку з марками
        try:
            block = page.locator("div.row.mark_auto-new").first
            await block.scroll_into_view_if_needed()
        except Exception:
            pass

        # зберемо з верхнього гріда
        grid_items = await collect_from_grid(page)

        # спробуємо також розгорнути і зібрати з collapse (якщо є)
        await try_expand_all(page)
        collapse_items = await collect_from_collapse(page)

        await ctx.close(); await browser.close()

    # об'єднаємо, залишивши найбільшу кількість для дубльованих назв
    combined = {}
    for b, c in grid_items + collapse_items:
        if b not in combined or c > combined[b]:
            combined[b] = c
    items = sorted(combined.items(), key=lambda x: x[0].lower())

    # збереження
    out = Path(outfile)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Brand", "Count"])
        for b, c in items:
            w.writerow([b, c])

    # консоль
    for b, c in items:
        print(f"{b} ; {c}")
    print(f"\n[OK] Saved {len(items)} rows → {out}")


if __name__ == "__main__":
    import argparse, asyncio
    ap = argparse.ArgumentParser()
    ap.add_argument("--headless", type=int, default=1, help="1 — без UI, 0 — з вікном")
    ap.add_argument("--outfile", default="vuvod/UA_automoto.csv")
    args = ap.parse_args()
    asyncio.run(run(bool(args.headless), args.outfile))
