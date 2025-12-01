# mollerauto_brands.py
import csv
import sys
import time
from pathlib import Path
from typing import List, Dict

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OUTPUT_FILE = "mollerauto_brands.csv"

# Селектори/тексти, щоб знайти секцію "Марка" і кнопку "Показать ещё"
BRAND_SECTION_TITLES = ["Марка", "Marka", "Brand"]  # RU/LV/EN
SHOW_MORE_TEXTS = ["Показать ещё", "Parādīt vairāk", "Show more"]

def ensure_brand_section_open(page) -> None:
    """
    Знаходить секцію з заголовком "Марка" і розкриває її, якщо згорнута.
    """
    for title in BRAND_SECTION_TITLES:
        # шукаємо елемент, що схожий на заголовок фільтра
        loc = page.locator(
            f"xpath=//*[self::legend or self::button or self::div or self::span]"
            f"[normalize-space()='{title}']"
        )
        if loc.count() > 0:
            el = loc.first
            try:
                el.scroll_into_view_if_needed()
            except Exception:
                pass
            # клікнемо — багато UI робить toggle саме кліком по заголовку
            try:
                el.click(timeout=1000)
            except Exception:
                pass
            return
    # якщо не знайшли — нічого страшного, далі спробуємо читати весь aside

def click_show_more_if_present(page) -> None:
    """
    Клікає на "Показать ещё / Parādīt vairāk / Show more" у межах сайдбара,
    поки кнопка з’являється (деякі сайти підвантажують список марок частинами).
    """
    side = page.locator("aside, .sidebar, .filters, #narrow-by-list")
    if side.count() == 0:
        side = page  # fallback: шукаємо по всій сторінці

    while True:
        found = False
        for text in SHOW_MORE_TEXTS:
            btn = side.get_by_text(text, exact=True)
            if btn.count():
                try:
                    btn.first.scroll_into_view_if_needed()
                    btn.first.click(timeout=1000)
                    found = True
                    time.sleep(0.3)
                    break
                except Exception:
                    pass
        if not found:
            break

def extract_brand_counts(page) -> List[Dict]:
    """
    Повертає список словників: {"brand": str, "count": int}
    Витягує тільки ті label, які прив'язані до input з name/id ~ make|brand|mark
    """
    script = """
    () => {
      const container = document.querySelector('aside, .sidebar, .filters, #narrow-by-list') || document;
      const labels = Array.from(container.querySelectorAll('label'));
      const out = [];
      for (const lab of labels) {
        // зв'язаний input
        const inp = lab.control || lab.querySelector('input');
        const ident = (inp?.name || '') + ' ' + (inp?.id || '');
        if (!/(make|brand|mark)/i.test(ident)) continue;

        const t = (lab.innerText || '').trim().replace(/\\s+/g, ' ');
        // Очікуємо формат "Назва (123)"
        const m = t.match(/^(.+?)\\s*\\((\\d+)\\)\\s*$/);
        if (m) {
          out.push({ brand: m[1].trim(), count: Number(m[2]) });
        }
      }
      // дедуп за назвою, максимум count
      const seen = new Map();
      for (const r of out) {
        const k = r.brand.toLowerCase();
        if (!seen.has(k) || r.count > seen.get(k).count) {
          seen.set(k, r);
        }
      }
      return Array.from(seen.values()).sort((a,b)=> b.count - a.count);
    }
    """
    return page.evaluate(script)

def scrape(url: str, headless: bool = True) -> List[Dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU",
        )
        page = ctx.new_page()
        page.set_default_timeout(10000)

        # Перехід
        page.goto(url, wait_until="domcontentloaded")
        # Трохи дочекаємось мережі/рендера
        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except PWTimeout:
            pass

        ensure_brand_section_open(page)
        click_show_more_if_present(page)
        data = extract_brand_counts(page)

        browser.close()
        return data

def save_csv(rows: List[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(["brand", "count"])
        for r in rows:
            w.writerow([r["brand"], r["count"]])

def main():
    url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://mollerauto.lv/lv_ru/used-cars.html"
    )
    headless = "--headed" not in sys.argv  # за замовчуванням headless=True
    rows = scrape(url, headless=headless)
    if not rows:
        print("Нічого не знайшов у секції 'Марка'. Спробуй запустити з --headed.")
    save_csv(rows, Path(OUTPUT_FILE))
    print(f"Збережено {len(rows)} рядків у {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
