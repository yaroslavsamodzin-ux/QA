#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Robust matrix merger (handles encodings and Excel)"""
MATRIX_CSV_PATH   = "automoto_counts.csv"
BASE_PATH         = "base_brands.csv"
SYNONYMS_PATH     = "manual_synonyms.csv"
OUT_PATH          = "base_brands_merged.csv"
NEED_DIR          = "need_check"
ASSUME_PAIRS      = True
FUZZY_THRESHOLD   = 0
MATRIX_BASE_BRAND_COL = "Brand"

import os, re, sys
import pandas as pd

def _try_read_csv(path, enc, desc=""):
    try:
        df = pd.read_csv(path, encoding=enc, sep=None, engine="python")
        print(f"[info] read {desc or path} as CSV encoding={enc}, sep=auto -> shape={df.shape}")
        return df
    except Exception:
        return None

def _try_read_excel(path, desc=""):
    try:
        df = pd.read_excel(path, engine="openpyxl")
        print(f"[info] read {desc or path} as Excel -> shape={df.shape}")
        return df
    except Exception:
        return None

def read_tabular_any(path, desc=""):
    low = path.lower()
    if low.endswith(".xlsx") or low.endswith(".xls"):
        df = _try_read_excel(path, desc)
        if df is not None:
            return df
    encodings = ["utf-8", "utf-8-sig", "cp1251", "windows-1251", "latin1", "utf-16", "utf-16le", "utf-16be"]
    for enc in encodings:
        df = _try_read_csv(path, enc, desc)
        if df is not None:
            return df
    print(f"[error] failed to read {desc or path}", file=sys.stderr)
    return pd.DataFrame()

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

try:
    from unidecode import unidecode
except ImportError:
    def unidecode(x): return x

try:
    from rapidfuzz import process, fuzz
except Exception:
    process = fuzz = None

def normalize_name(s: str) -> str:
    if pd.isna(s): return ""
    s = str(s).strip()
    s = re.sub(r"[^\w\s\-&/\.]", " ", s, flags=re.UNICODE).lower()
    s = re.sub(r"\s+", " ", s).strip()
    s = unidecode(s)
    s = s.replace("alfa-romeo", "alfa romeo")
    s = s.replace("land-rover", "land rover")
    s = s.replace("mercedes benz", "mercedes-benz")
    s = s.replace("rolls royce", "rolls-royce")
    s = s.replace("lynk & co", "lynk & co")
    return s

def pair_columns(cols):
    pairs = []
    i = 1
    while i < len(cols):
        bcol = cols[i]
        ccol = cols[i+1] if (i+1) < len(cols) else None
        site = re.sub(r"\s+\(.*\)$", "", str(bcol)).strip()
        pairs.append((site, bcol, ccol))
        i += 2
    return pairs

def main():
    base = read_tabular_any(BASE_PATH, "base")
    if base.empty:
        sys.exit(f"ERROR: cannot read base: {BASE_PATH}")
    if "Brand" not in base.columns:
        sys.exit("ERROR: base must have column 'Brand'")
    base["__order"] = range(len(base))
    base["__norm"] = base["Brand"].apply(normalize_name)
    base_norm_map = dict(zip(base["__norm"], base["Brand"]))
    base_norm_keys = list(base_norm_map.keys())

    manual = {}
    syn = read_tabular_any(SYNONYMS_PATH, "synonyms")
    if not syn.empty and {"synonym","Brand"} <= set(syn.columns):
        syn["__norm"] = syn["synonym"].apply(normalize_name)
        manual = dict(zip(syn["__norm"], syn["Brand"]))
    else:
        print("[warn] synonyms missing/invalid — continuing without.")

    mat = read_tabular_any(MATRIX_CSV_PATH, "matrix")
    if mat.empty:
        sys.exit(f"ERROR: cannot read matrix: {MATRIX_CSV_PATH}")
    cols = list(mat.columns)
    sites = pair_columns(cols) if ASSUME_PAIRS else []
    if not sites:
        sys.exit("ERROR: couldn't infer site pairs.")

    ensure_dir(NEED_DIR)
    out = base.copy()
    use_fuzzy = FUZZY_THRESHOLD and FUZZY_THRESHOLD > 0 and process is not None

    for site, brand_col, count_col in sites:
        if brand_col == MATRIX_BASE_BRAND_COL:
            continue
        if brand_col not in mat.columns:
            continue
        site_name = re.sub(r"[^A-Za-z0-9_]+", "_", str(site).strip()).strip("_").lower() or "site"
        df = mat[[brand_col] + ([count_col] if count_col in mat.columns else [])].copy()
        df["__brand_raw"] = df[brand_col]
        df["__norm"] = df["__brand_raw"].apply(normalize_name)
        if count_col in df.columns:
            df["__count"] = pd.to_numeric(df[count_col], errors="coerce").fillna(0).astype(int)
        else:
            df["__count"] = 1

        mapped, need = [], []
        for _, r in df.iterrows():
            raw, norm, cnt = r["__brand_raw"], r["__norm"], int(r["__count"])
            if not norm: 
                continue
            mapped_brand = None
            if norm in manual:
                mapped_brand = manual[norm]
            elif norm in base_norm_map:
                mapped_brand = base_norm_map[norm]
            elif use_fuzzy:
                cand = process.extractOne(norm, base_norm_keys, scorer=fuzz.token_sort_ratio)
                if cand and cand[1] >= FUZZY_THRESHOLD:
                    mapped_brand = base_norm_map[cand[0]]
            if mapped_brand:
                mapped.append((mapped_brand, cnt))
            else:
                need.append({"site": site_name, "raw_brand": raw, "norm": norm, "count": cnt})

        if mapped:
            mdf = pd.DataFrame(mapped, columns=["Brand", site_name])
            agg = mdf.groupby("Brand")[site_name].sum().reset_index()
        else:
            agg = pd.DataFrame(columns=["Brand", site_name])

        out = out.merge(agg, on="Brand", how="left")
        out[site_name] = out[site_name].fillna(0).astype(int)

        if need:
            pd.DataFrame(need).to_csv(os.path.join(NEED_DIR, f"need_check_{site_name}.csv"),
                                      index=False, encoding="utf-8-sig")

    out = out.sort_values("__order").drop(columns=["__order","__norm"])
    out.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"✅ Saved -> {OUT_PATH}")
    print(f"📁 Need-check per site -> {NEED_DIR}/need_check_*.csv")

if __name__ == "__main__":
    main()
