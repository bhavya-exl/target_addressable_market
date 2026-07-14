#!/usr/bin/env python3
"""
dump.py — universal table profiler (Claude's "eyes" during tam-ingest).

Deterministic, no LLM. Given any .xlsx/.xlsm/.csv (best-effort .docx/.pptx tables),
emit a JSON profile per sheet that Claude reads to AUTHOR a schema card:
  - detected header row (not assumed to be row 1)
  - per column: inferred type, null %, distinct count, sample values, role hint
  - N sample data rows WITH their real source row numbers (for provenance)
  - anomaly flags: two-row header band, empty/scaffold sheet, near-duplicate sheet

Usage:
  python3 code/tam/dump.py "<file>" [--sheet NAME] [--rows N] [--json OUT]
"""
import sys, os, json, re, argparse, hashlib
from pathlib import Path
from datetime import datetime, date

SAMPLE_ROWS = 6
HEADER_SCAN = 15          # how many top rows to consider as a possible header


# ---------- type inference ----------
def _is_int(v):
    try:
        int(str(v).replace(",", "").strip()); return True
    except Exception:
        return False

def _is_float(v):
    try:
        float(str(v).replace(",", "").replace("$", "").replace("%", "").strip()); return True
    except Exception:
        return False

def infer_type(values, colname=""):
    vals = [v for v in values if v not in (None, "", " ")]
    if not vals:
        return "string"
    cn = colname.lower()
    if isinstance(vals[0], (datetime, date)) or any(isinstance(v, (datetime, date)) for v in vals):
        return "date"
    str_vals = [str(v).strip() for v in vals]
    if all(v.lower() in ("yes", "no", "y", "n", "true", "false") for v in str_vals):
        return "bool"
    if all("%" in v or (_is_float(v) and 0 <= (float(re.sub(r"[^0-9.\-]", "", v) or 0)) <= 1) for v in str_vals) and "%" in "".join(str_vals):
        return "percent"
    if all(_is_int(v) for v in str_vals):
        nums = [int(v.replace(",", "")) for v in str_vals]
        if all(1900 <= n <= 2100 for n in nums) and ("year" in cn or "yr" in cn):
            return "year"
        return "int"
    if all(_is_float(v) for v in str_vals):
        if any(s in cn for s in ("rev", "premium", "nwp", "gwp", "tcv", "budget", "$", "revenue", "spend")):
            return "currency_usd"
        return "float"
    if any(s in cn for s in ("company", "group", "insurer", "carrier", "client", "account", "broker")):
        return "name_company"
    if any(s in cn for s in ("ceo", "cfo", "coo", "cxo", "contact", "leader", "owner", "exec", "name")):
        return "name_person"
    if any(v.startswith(("http://", "https://", "www.", "file://")) for v in str_vals):
        return "url"
    distinct = len(set(str_vals))
    if distinct <= 15 and distinct < max(2, len(str_vals) * 0.6):
        return "enum"
    if max((len(v) for v in str_vals), default=0) > 60:
        return "freetext"
    return "string"


def role_hint(t, null_pct):
    if t in ("name_company",):
        return "entity_key"
    if t in ("int", "float", "currency_usd", "percent"):
        return "measure"
    if t in ("enum", "bool", "year", "date"):
        return "dimension"
    if t in ("freetext", "url", "name_person"):
        return "attribute"
    return "attribute"


# ---------- header detection ----------
def score_row(cells):
    non_empty = [c for c in cells if c not in (None, "", " ")]
    if not non_empty:
        return -1
    strings = [c for c in non_empty if isinstance(c, str) and not _is_float(c)]
    uniq = len(set(str(c).strip() for c in non_empty))
    return len(non_empty) * 1.0 + len(strings) * 0.5 + uniq * 0.5


def detect_header(grid):
    best_i, best_s = 0, -1
    for i in range(min(HEADER_SCAN, len(grid))):
        s = score_row(grid[i])
        # a header should be followed by a data row (not empty)
        nxt = score_row(grid[i + 1]) if i + 1 < len(grid) else -1
        if nxt <= 0:
            continue
        if s > best_s:
            best_s, best_i = s, i
    # two-row header band: next row also mostly string labels with high overlap of emptiness
    two_row = False
    if best_i + 1 < len(grid):
        nxt = grid[best_i + 1]
        nxt_strings = [c for c in nxt if isinstance(c, str) and not _is_float(c) and c not in (None, "", " ")]
        nxt_non_empty = [c for c in nxt if c not in (None, "", " ")]
        if nxt_non_empty and len(nxt_strings) >= 0.7 * len(nxt_non_empty) and len(nxt_non_empty) < 0.6 * len(grid[best_i]):
            two_row = True
    return best_i, two_row


# ---------- readers ----------
def read_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    sheets = {}
    for ws in wb.worksheets:
        grid = []
        for row in ws.iter_rows(values_only=True):
            grid.append(list(row))
        sheets[ws.title] = grid
    wb.close()
    return sheets

def read_csv(path):
    import csv
    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        grid = [row for row in csv.reader(f)]
    return {Path(path).stem: grid}


# ---------- profiling ----------
def profile_sheet(name, grid, max_rows=SAMPLE_ROWS):
    # trim fully-empty trailing rows
    while grid and all(c in (None, "", " ") for c in grid[-1]):
        grid.pop()
    non_empty_rows = sum(1 for r in grid if any(c not in (None, "", " ") for c in r))
    if non_empty_rows <= 1:
        return {"sheet": name, "role": "non_data", "warnings": ["empty or scaffold sheet"],
                "n_rows": non_empty_rows, "columns": []}

    header_i, two_row = detect_header(grid)
    headers = grid[header_i]
    # de-dup + fill blank headers
    cols, seen = [], {}
    for j, h in enumerate(headers):
        h = (str(h).strip() if h not in (None, "") else f"col{j}")
        if h in seen:
            seen[h] += 1; h = f"{h}.{seen[h]}"
        else:
            seen[h] = 0
        cols.append(h)

    data = grid[header_i + (2 if two_row else 1):]
    ncols = len(cols)
    col_profiles = []
    for j in range(ncols):
        column = [r[j] if j < len(r) else None for r in data]
        non_null = [v for v in column if v not in (None, "", " ")]
        t = infer_type(non_null, cols[j])
        distinct = len(set(str(v).strip() for v in non_null))
        null_pct = round(100 * (len(column) - len(non_null)) / max(1, len(column)))
        samples = []
        for v in non_null:
            sv = str(v).strip()
            if sv not in samples:
                samples.append(sv)
            if len(samples) >= 5:
                break
        col_profiles.append({
            "name": cols[j], "type": t, "role_hint": role_hint(t, null_pct),
            "null_pct": null_pct, "distinct": distinct, "samples": samples,
        })

    # sample rows with real (1-based) source row numbers
    sample_rows = []
    first_data_excel_row = header_i + (2 if two_row else 1) + 1  # 1-based
    for k, r in enumerate(data):
        if any(c not in (None, "", " ") for c in r):
            obj = {cols[j]: (str(r[j]).strip() if j < len(r) and r[j] not in (None, "") else None)
                   for j in range(ncols)}
            sample_rows.append({"_source_row": first_data_excel_row + k, **obj})
        if len(sample_rows) >= max_rows:
            break

    colset_hash = hashlib.md5("|".join(sorted(cols)).encode()).hexdigest()[:10]
    return {
        "sheet": name, "role": "data",
        "header_row": header_i + 1,            # 1-based, for the card
        "two_row_header": two_row,
        "n_data_rows": sum(1 for r in data if any(c not in (None, "", " ") for c in r)),
        "n_cols": ncols,
        "colset_hash": colset_hash,
        "columns": col_profiles,
        "sample_rows": sample_rows,
        "warnings": (["two-row header band"] if two_row else []) +
                    ([f"trailing space in sheet name '{name}'"] if name != name.strip() else []),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--sheet")
    ap.add_argument("--rows", type=int, default=SAMPLE_ROWS)
    ap.add_argument("--json")
    args = ap.parse_args()
    path = args.file
    ext = Path(path).suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        sheets = read_xlsx(path)
    elif ext in (".csv", ".tsv"):
        sheets = read_csv(path)
    else:
        print(f"Unsupported for now: {ext} (xlsx/csv supported; docx/pptx = best-effort TODO)", file=sys.stderr)
        sys.exit(2)

    profiles = []
    for name, grid in sheets.items():
        if args.sheet and name.strip() != args.sheet.strip():
            continue
        profiles.append(profile_sheet(name, grid, max_rows=args.rows))

    # near-duplicate detection across sheets (same column set)
    by_hash = {}
    for p in profiles:
        h = p.get("colset_hash")
        if h:
            by_hash.setdefault(h, []).append(p["sheet"])
    for p in profiles:
        dupes = [s for s in by_hash.get(p.get("colset_hash"), []) if s != p["sheet"]]
        if dupes:
            p.setdefault("warnings", []).append(f"near-duplicate column set with: {dupes}")

    out = {"file": path, "n_sheets": len(profiles), "sheets": profiles}
    text = json.dumps(out, indent=2, default=str)
    if args.json:
        Path(args.json).write_text(text)
        print(f"Wrote {args.json}  ({len(profiles)} sheets)")
    else:
        print(text)


if __name__ == "__main__":
    main()
