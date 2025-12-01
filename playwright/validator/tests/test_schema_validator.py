# tests/test_schema_validator.py
# -*- coding: utf-8 -*-
import os, re, csv, time
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeoutError

# --- шляхова логіка ---
SCRIPT_DIR = Path(__file__).resolve().parent          # ...\validator\tests
ROOT_DIR = SCRIPT_DIR.parent                          # ...\validator
ART_DIR = ROOT_DIR / "artifacts"
ART_DIR.mkdir(exist_ok=True)

def find_urls_file():
    # шукаємо urls.txt у: корінь проєкту → поточна робоча тека → тека tests
    for p in [ROOT_DIR / "urls.txt", Path.cwd() / "urls.txt", SCRIPT_DIR / "urls.txt"]:
        if p.exists():
            return p
    return None

def load_urls():
    p = find_urls_file()
    if not p:
        print("[WARN] urls.txt not found. Using fallback list.")
        return []
    urls = []
    with p.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln and not ln.lstrip().startswith("#"):
                urls.append(ln)
    print(f"[INFO] Loaded {len(urls)} URL(s) from {p}")
    return urls

def safe_name(url: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", url)

def run_validator(page, site_url: str):
    vurl = f"https://validator.schema.org/#url={quote(site_url, safe=':/')}"
    page.goto(vurl, wait_until="domcontentloaded", timeout=90_000)
    try:
        btn = page.get_by_role("button", name=re.compile(r"Запустить новый тест|Run new test", re.I))
        if btn.is_visible():
            btn.click()
    except Exception:
        pass
    start = time.time()
    while time.time() - start < 60:
        try:
            txt = page.inner_text("body").lower()
        except TimeoutError:
            txt = ""
        if any(k in txt for k in ("предупрежден", "warnings", "ошиб", "errors")):
            break
        time.sleep(1)
    else:
        return (False, False, "validator did not render keywords in 60s")
    body = page.inner_text("body").lower()
    warnings_ok = ("нет предупреждений" in body) or ("no warnings" in body)
    errors_ok   = ("нет ошибок" in body) or ("no errors" in body)
    return (warnings_ok, errors_ok, "")

def main():
    urls = load_urls() or ["https://automoto.com.lv/ru"]  # fallback
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="ru-RU")
        page = context.new_page()
        fail_count = 0

        for url in urls:
            print(f"\n[VALIDATE] {url}")
            warnings_ok, errors_ok, reason = run_validator(page, url)
            if not warnings_ok or not errors_ok:
                fname = safe_name(url)
                page.screenshot(path=ART_DIR / f"{fname}.png", full_page=True)
                with open(ART_DIR / f"{fname}.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                fail_count += 1
                print(f"  X WARNINGS_OK={warnings_ok}  ERRORS_OK={errors_ok}  {reason}")
            else:
                print("  OK No warnings / No errors")
            rows.append({"url": url, "warnings_ok": warnings_ok, "errors_ok": errors_ok, "reason": reason})

        browser.close()

    out_csv = ROOT_DIR / "results_schema_validator.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["url","warnings_ok","errors_ok","reason"])
        w.writeheader(); w.writerows(rows)
    print(f"\nDone. Failures: {fail_count}. CSV -> {out_csv}. Artifacts -> {ART_DIR}")

if __name__ == "__main__":
    main()
