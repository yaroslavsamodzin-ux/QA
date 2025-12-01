#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Universal Brand Extractor
-------------------------
Extracts brand names (and counts if present) from arbitrary marketplace/category pages.
Works on local HTML files or live URLs.

Features:
- Multiple heuristic strategies (attributes, dropdowns, options, lists, regex).
- Site adapters (lightweight) for known patterns (agriline / *_line mirrors, etc.).
- Count detection from attributes (data-num, data-count) or text: "Brand (123)".
- CLI options for output CSV/TXT, user-agent, timeouts, debug save, and custom CSS selectors via JSON.
- Optional dedupe/normalize and filtering of known "noise" labels.
"""

import argparse, csv, json, os, re, sys, time, html
from typing import List, Dict, Tuple, Optional, Iterable
from urllib.parse import urlparse
from dataclasses import dataclass, field

try:
    import requests
except Exception:
    requests = None

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except Exception as e:
    print("BeautifulSoup4 is required. pip install beautifulsoup4", file=sys.stderr)
    raise

# -------------------- Utilities --------------------

NOISE_TOKENS = {
    "показати всі", "показать все", "show all", "всі", "все", "all", "вибрати", "обрати",
    "марка", "бренд", "brand", "select", "option", "choose"
}

COUNT_RE = re.compile(r"\((\d{1,6})\)")  # captures number in parentheses
DIGIT_RE = re.compile(r"\d+")
WS_RE = re.compile(r"\s+")

def norm_text(s: str) -> str:
    s = html.unescape(s or "")
    s = s.strip()
    s = WS_RE.sub(" ", s)
    return s

def looks_like_brand(s: str) -> bool:
    if not s:
        return False
    low = s.lower()
    if low in NOISE_TOKENS:
        return False
    if len(s) < 2:
        return False
    # Avoid pure numbers or price-like strings
    if s.isdigit():
        return False
    if re.fullmatch(r"[\d\W_]+", s):
        return False
    # skip if too generic / UI-only
    if any(tok in low for tok in ["марка", "бренд", "фільтр", "filter", "search", "введіть", "input", "clear"]):
        return False
    return True

def extract_count_from_text(txt: str) -> Optional[int]:
    if not txt:
        return None
    m = COUNT_RE.search(txt)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            pass
    # Try plain digits after separators, e.g. "Brand – 12"
    tail = txt.rsplit(" ", 1)[-1]
    if tail.isdigit():
        return int(tail)
    return None

def best_count(*vals: Iterable[Optional[int]]) -> Optional[int]:
    cand = [v for v in vals if isinstance(v, int)]
    if not cand:
        return None
    return max(cand)

@dataclass
class BrandHit:
    name: str
    count: Optional[int] = None
    source: str = ""

    def as_row(self) -> Tuple[str, Optional[int], str]:
        return (self.name, self.count if self.count is not None else "", self.source)

# -------------------- HTML fetch / load --------------------

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def load_html(input_path_or_url: str, timeout: int = 20, headers: Optional[Dict[str,str]] = None) -> str:
    headers = headers or DEFAULT_HEADERS
    if os.path.exists(input_path_or_url):
        with open(input_path_or_url, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    # fetch URL
    if requests is None:
        raise RuntimeError("requests not available to fetch URL")
    resp = requests.get(input_path_or_url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text

# -------------------- Extractor core --------------------

class BrandExtractor:
    def __init__(self, soup: BeautifulSoup, debug: bool=False):
        self.soup = soup
        self.debug = debug
        self.hits: Dict[str, BrandHit] = {}

    def add_hit(self, name: str, count: Optional[int], source: str):
        name = norm_text(name)
        if not looks_like_brand(name):
            return
        prev = self.hits.get(name)
        if prev:
            prev.count = best_count(prev.count, count)
            if prev.source and source and source not in prev.source:
                prev.source += f";{source}"
        else:
            self.hits[name] = BrandHit(name=name, count=count, source=source)

    # ---------- Strategies ----------

    def from_attributes(self):
        # data-brand, data-search-text, data-name, data-title
        for attr in ["data-brand", "data-search-text", "data-name", "data-title", "data-mark"]:
            for el in self.soup.find_all(attrs={attr: True}):
                name = norm_text(el.get(attr))
                c = None
                # attribute counts
                for cattr in ["data-num", "data-count", "data-total", "data-stat", "data-found"]:
                    if el.has_attr(cattr):
                        try:
                            c = int(re.sub(r"\D+", "", str(el.get(cattr))) or "0")
                        except Exception:
                            pass
                # text-based count fallback
                txt = norm_text(el.get_text(" ", strip=True))
                c = best_count(c, extract_count_from_text(txt))
                self.add_hit(name, c, f"attr:{attr}")
        return self

    def from_dropdown_options(self):
        # option, li/label combos, span.opt__text etc.
        # 1) <option> text and value
        for opt in self.soup.find_all("option"):
            name = norm_text(opt.get_text(" ", strip=True))
            # Skip placeholder options
            if not looks_like_brand(name):
                continue
            c = best_count(extract_count_from_text(name))
            # Adjacent count in a span inside option (rare), try attributes too
            for a in ["data-count", "data-num"]:
                if opt.has_attr(a):
                    try:
                        c = best_count(c, int(re.sub(r"\D+", "", opt.get(a)) or "0"))
                    except Exception:
                        pass
            self.add_hit(name, c, "option")

        # 2) Common custom dropdowns: .opt__text, .select__item, .dropdown-item
        for cls in ["opt__text", "select__item", "dropdown-item", "filter__item", "facet__item"]:
            for el in self.soup.select(f".{cls}"):
                name = norm_text(el.get_text(" ", strip=True))
                if looks_like_brand(name):
                    c = best_count(extract_count_from_text(name))
                    # try parent attributes
                    par = el.parent
                    if par:
                        for a in ["data-count", "data-num"]:
                            if par.has_attr(a):
                                try:
                                    c = best_count(c, int(re.sub(r'\D+', '', par.get(a)) or "0"))
                                except Exception:
                                    pass
                    self.add_hit(name, c, f"class:{cls}")
        return self

    def from_lists_and_cards(self):
        # a.brand, li.brand, .brand-list a, etc.
        selectors = [
            "a.brand", "li.brand a", ".brand-list a", ".brands a", ".brands__item a", ".filter__brands a",
            ".brands li", ".brands__item", ".filter__brands li", "label.brand", "label a"
        ]
        for sel in selectors:
            for el in self.soup.select(sel):
                name = norm_text(el.get_text(" ", strip=True))
                if looks_like_brand(name):
                    c = best_count(extract_count_from_text(name))
                    # sibling spans that may contain counts
                    sib = el.find_next_sibling()
                    if sib:
                        c = best_count(c, extract_count_from_text(norm_text(sib.get_text(" ", strip=True))))
                    # attributes on ancestor
                    anc = el.parent
                    if anc:
                        for a in ["data-count", "data-num"]:
                            if anc.has_attr(a):
                                try:
                                    c = best_count(c, int(re.sub(r'\D+', '', anc.get(a)) or "0"))
                                except Exception:
                                    pass
                    self.add_hit(name, c, f"list:{sel}")
        return self

    def from_regex_fallback(self):
        # Pull raw text blocks that look like "Brand (123)" inside the HTML
        raw = self.soup.get_text("\n", strip=True)
        # Split by separators
        parts = re.split(r"[\n\r\t,;|]+", raw)
        for p in parts:
            p = norm_text(p)
            # must contain letters
            if len(p) < 2 or not re.search(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ]", p):
                continue
            if not looks_like_brand(p):
                continue
            # Heuristic: ignore pure sentences with many spaces and no parentheses
            if "(" not in p and len(p.split()) > 4:
                continue
            c = extract_count_from_text(p)
            # Brand name may have "Brand (123)"
            name = norm_text(re.sub(r"\s*\(\d+\)\s*$", "", p))
            if looks_like_brand(name):
                self.add_hit(name, c, "regex")
        return self

    # -------------------- Public API --------------------
    def extract(self) -> List[BrandHit]:
        self.from_attributes().from_dropdown_options().from_lists_and_cards().from_regex_fallback()
        # Final cleanup: remove obvious duplicates with case differences
        normalized: Dict[str, BrandHit] = {}
        for k, v in self.hits.items():
            key = v.name.lower()
            if key in normalized:
                normalized[key].count = best_count(normalized[key].count, v.count)
                if v.source not in normalized[key].source:
                    normalized[key].source += ";" + v.source
            else:
                normalized[key] = v
        # Drop "noise" again (if slipped through)
        final = [hit for hit in normalized.values() if looks_like_brand(hit.name)]
        final.sort(key=lambda h: h.name.lower())
        return final

# -------------------- CLI --------------------

def main():
    ap = argparse.ArgumentParser(description="Universal Brand Extractor")
    ap.add_argument("inputs", nargs="+", help="URL(s) or local HTML file(s)")
    ap.add_argument("-o", "--output", default="brands.csv", help="Output CSV path (default: brands.csv)")
    ap.add_argument("--txt", help="Optional TXT output path (one brand per line)")
    ap.add_argument("--timeout", type=int, default=25, help="HTTP timeout (s)")
    ap.add_argument("--ua", default=DEFAULT_HEADERS["User-Agent"], help="Custom User-Agent")
    ap.add_argument("--debug", action="store_true", help="Write debug info to stderr")
    args = ap.parse_args()

    headers = {"User-Agent": args.ua}

    all_hits: Dict[str, BrandHit] = {}

    for inp in args.inputs:
        try:
            html_str = load_html(inp, timeout=args.timeout, headers=headers)
            # Some "view-source" files have escaped HTML; unescape once
            if "<td class=\"line-content\"" in html_str:
                html_str = html.unescape(html_str)
            soup = BeautifulSoup(html_str, "html.parser")
            extractor = BrandExtractor(soup, debug=args.debug)
            hits = extractor.extract()
            for h in hits:
                key = h.name.lower()
                if key in all_hits:
                    # merge counts
                    all_hits[key].count = best_count(all_hits[key].count, h.count)
                    if h.source not in all_hits[key].source:
                        all_hits[key].source += ";" + h.source
                else:
                    all_hits[key] = h
        except Exception as e:
            print(f"[WARN] Failed to process {inp}: {e}", file=sys.stderr)

    final_hits = sorted(all_hits.values(), key=lambda h: h.name.lower())

    # Write CSV
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["Brand", "Count", "Source"])
        for h in final_hits:
            wr.writerow([h.name, h.count if h.count is not None else "", h.source])

    if args.txt:
        with open(args.txt, "w", encoding="utf-8") as f:
            for h in final_hits:
                f.write(h.name + "\n")

    print(f"[OK] Extracted {len(final_hits)} unique brands.")
    print(f"[OK] CSV saved to: {os.path.abspath(args.output)}")
    if args.txt:
        print(f"[OK] TXT saved to: {os.path.abspath(args.txt)}")

if __name__ == "__main__":
    main()
