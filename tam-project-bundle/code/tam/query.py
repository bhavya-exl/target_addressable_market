#!/usr/bin/env python3
"""
query.py — deterministic, header-aware, CITED table query (Claude's "hands").

Given a QUERY SPEC (JSON) that Claude emits after routing via the card index,
resolve the table's real source (file/sheet/header_row from its card), run
filter -> join -> group/aggregate -> sort -> limit, and return rows WITH:
  - provenance: the real source row number behind each returned row
  - as_of: the table vintage, so every answer can be dated
  - staleness: months old vs. today, + a refresh nudge when stale

TABLE QUERY SPEC (spreadsheets):
{
  "table_id": "F1.top_insurers_and_brokers",
  "select":   ["Company/ Group", "2020-Rev Budget"],        // omit = all columns
  "filters":  [{"col": "EXL Client", "op": "==", "value": "Yes"}],
  "normalize": ["Company/ Group"],                            // canonicalize these name cols
  "group_by": ["Type"],
  "aggregate":[{"col": "2020-Rev Budget", "fn": "sum", "as": "total_rev"}],
  "sort":     {"col": "2020-Rev Budget", "dir": "desc"},
  "limit":    10,
  "join":     {"table_id": "...", "left_on": "...", "right_on": "...", "select": [...]}
}
ops: == != > < >= <= in nin contains icontains notnull isnull

DECK QUERY SPEC (presentations) — grounded slide retrieval, provenance = slide number:
{
  "deck_id":  "P1.deck",
  "slides":   [3, 5],                 // specific slide numbers (optional)
  "entity":   "Travelers",            // slides where this entity appears, per the card (optional)
  "contains": "premium audit",        // case-insensitive text search over slide text+notes (optional)
  "fields":   ["title", "text", "notes", "tables"],   // default: title + text
  "limit":    10
}
(no filter given -> returns every slide; a slide's real text is re-read from the file.)

Usage:
  python3 code/tam/query.py --spec spec.json          # or pipe spec JSON on stdin
  python3 code/tam/query.py --today 2026-07           # override "now" for staleness
"""
import sys, os, json, argparse, re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
import normalize as N
import dump

from tam_root import resolve_root
REPO = resolve_root()
CARDS = REPO / "produced_data" / "cards"

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def load_card(table_id):
    p = CARDS / f"{table_id}.json"
    if not p.exists():
        raise FileNotFoundError(f"No card for '{table_id}' at {p}")
    return json.loads(p.read_text())


def parse_as_of(as_of):
    """'Aug 2020' / '2024+' / '~Feb 2021' -> (year, month) best-effort."""
    if not as_of:
        return None
    s = str(as_of).lower()
    yr = re.search(r"(19|20)\d{2}", s)
    year = int(yr.group()) if yr else None
    mon = None
    for name, num in MONTHS.items():
        if name in s:
            mon = num
            break
    if year is None:
        return None
    return (year, mon or 1)


def staleness(as_of, today):
    ym = parse_as_of(as_of)
    if not ym:
        return None
    ty, tm = today
    months = (ty - ym[0]) * 12 + (tm - ym[1])
    return {
        "as_of": as_of,
        "months_old": months,
        "stale": months > 18,
        "note": (f"Data reflects {as_of} (~{months//12}y {months%12}m old). "
                 f"Consider asking the data owner to refresh.") if months > 18 else None,
    }


def read_table(card):
    import pandas as pd
    src = card["source"]
    path = REPO / src["file"] if not os.path.isabs(src["file"]) else Path(src["file"])
    hdr = int(src.get("header_row", 1)) - 1                 # 0-based
    ext = path.suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        df = pd.read_excel(path, sheet_name=src["sheet"], header=hdr, engine="openpyxl")
    else:
        df = pd.read_csv(path, header=hdr)
    two_row = bool(card.get("source", {}).get("two_row_header") or card.get("two_row_header"))
    first_data_excel_row = int(src.get("header_row", 1)) + (2 if two_row else 1)
    if two_row and len(df):
        df = df.iloc[1:].reset_index(drop=True)
        first_data_excel_row += 0
    df.columns = [str(c).strip() for c in df.columns]
    # provenance: real excel row per dataframe row
    df["_source_row"] = [first_data_excel_row + i for i in range(len(df))]
    return df


def apply_filters(df, filters):
    import pandas as pd
    for f in filters or []:
        col, op, val = f["col"], f["op"], f.get("value")
        if col not in df.columns:
            raise KeyError(f"filter column '{col}' not in table columns {list(df.columns)[:12]}...")
        s = df[col]
        if op == "==":
            df = df[s.astype(str).str.strip().str.lower() == str(val).strip().lower()]
        elif op == "!=":
            df = df[s.astype(str).str.strip().str.lower() != str(val).strip().lower()]
        elif op in (">", "<", ">=", "<="):
            num = pd.to_numeric(s.astype(str).str.replace(r"[,$%]", "", regex=True), errors="coerce")
            v = float(val)
            df = df[{">": num > v, "<": num < v, ">=": num >= v, "<=": num <= v}[op]]
        elif op == "in":
            vals = [str(x).strip().lower() for x in val]
            df = df[s.astype(str).str.strip().str.lower().isin(vals)]
        elif op == "nin":
            vals = [str(x).strip().lower() for x in val]
            df = df[~s.astype(str).str.strip().str.lower().isin(vals)]
        elif op == "contains":
            df = df[s.astype(str).str.contains(str(val), case=True, na=False)]
        elif op == "icontains":
            df = df[s.astype(str).str.contains(str(val), case=False, na=False)]
        elif op == "notnull":
            df = df[s.notna() & (s.astype(str).str.strip() != "")]
        elif op == "isnull":
            df = df[s.isna() | (s.astype(str).str.strip() == "")]
        else:
            raise ValueError(f"unknown op '{op}'")
    return df


def run(spec, today):
    import pandas as pd
    card = load_card(spec["table_id"])
    df = read_table(card)
    as_of_list = [card["source"].get("as_of")]

    for col in spec.get("normalize", []):
        if col in df.columns:
            df[col] = N.normalize_series(df[col])

    df = apply_filters(df, spec.get("filters"))

    if spec.get("join"):
        j = spec["join"]
        jcard = load_card(j["table_id"])
        jdf = read_table(jcard)
        as_of_list.append(jcard["source"].get("as_of"))
        for col in j.get("normalize", []):
            if col in df.columns:
                df[col] = N.normalize_series(df[col])
            if col in jdf.columns:
                jdf[col] = N.normalize_series(jdf[col])
        jsel = j.get("select")
        if jsel:
            jdf = jdf[list(set(jsel + [j["right_on"], "_source_row"]))]
        df = df.merge(jdf, how=j.get("how", "left"),
                      left_on=j["left_on"], right_on=j["right_on"], suffixes=("", "_j"))

    agg = spec.get("aggregate")
    if agg:
        for a in agg:
            df[a["col"]] = pd.to_numeric(
                df[a["col"]].astype(str).str.replace(r"[,$%]", "", regex=True), errors="coerce")
        gb = spec.get("group_by")
        if gb:
            aggmap = {a["col"]: a["fn"] for a in agg}
            g = df.groupby(gb, dropna=False).agg(aggmap).reset_index()
            g = g.rename(columns={a["col"]: a.get("as", a["col"]) for a in agg})
            df = g
        else:
            row = {a.get("as", a["col"]): getattr(df[a["col"]], a["fn"])() for a in agg}
            df = pd.DataFrame([row])

    if spec.get("sort"):
        s = spec["sort"]
        col = s["col"]
        tmp = pd.to_numeric(df[col].astype(str).str.replace(r"[,$%]", "", regex=True), errors="coerce")
        if tmp.notna().mean() > 0.5:
            df = df.assign(_sortkey=tmp).sort_values("_sortkey", ascending=(s.get("dir") != "desc")).drop(columns="_sortkey")
        else:
            df = df.sort_values(col, ascending=(s.get("dir") != "desc"))

    if spec.get("limit"):
        df = df.head(int(spec["limit"]))

    sel = spec.get("select")
    prov = df["_source_row"].tolist() if "_source_row" in df.columns else []
    if sel:
        keep = [c for c in sel if c in df.columns]
        out_df = df[keep]
    else:
        out_df = df[[c for c in df.columns if c != "_source_row"]]

    rows = json.loads(out_df.to_json(orient="records"))
    as_of_list = [a for a in as_of_list if a]
    stale = staleness(as_of_list[0], today) if as_of_list else None

    return {
        "table_id": spec["table_id"],
        "source": {"file": card["source"]["file"], "sheet": card["source"]["sheet"]},
        "as_of": as_of_list,
        "staleness": stale,
        "row_count": len(rows),
        "citation": f'{card["source"]["file_alias"]}/{card["source"]["sheet"]}',
        "provenance_rows": prov,
        "rows": rows,
    }


def run_deck(spec, today):
    """Grounded slide retrieval for a presentation card. Re-reads the real .pptx (so
    returned text is faithful to the file, not the card's paraphrase), filters slides by
    number / entity / text, and returns them with slide-number provenance + as_of."""
    card = load_card(spec["deck_id"])
    src = card["source"]
    path = REPO / src["file"] if not os.path.isabs(src["file"]) else Path(src["file"])
    slides = dump.read_pptx(str(path))
    by_num = {s["slide"]: s for s in slides}

    # entity -> the slides the card says it appears on (authored, normalizable)
    entity_slides = None
    if spec.get("entity"):
        want, _, _ = N.canonical(spec["entity"])
        want_l = str(want).strip().lower()
        entity_slides = set()
        for e in card.get("entities", []):
            nm, _, _ = N.canonical(e.get("name", ""))
            if str(nm).strip().lower() == want_l or want_l in str(e.get("name", "")).strip().lower():
                entity_slides.update(e.get("slides", []))

    contains = (spec.get("contains") or "").strip().lower()
    wanted_nums = spec.get("slides")

    picked = []
    for s in slides:
        if wanted_nums and s["slide"] not in wanted_nums:
            continue
        if entity_slides is not None and s["slide"] not in entity_slides:
            continue
        if contains:
            hay = "\n".join([s.get("title") or "", s.get("text") or "", s.get("notes") or ""]).lower()
            if contains not in hay:
                continue
        picked.append(s)

    fields = spec.get("fields") or ["title", "text"]
    alias = src.get("file_alias")
    out_slides = []
    for s in picked:
        row = {"slide": s["slide"], "_provenance": f'{alias}/slide {s["slide"]}'}
        for f in fields:
            if f == "tables":
                row["tables"] = s["tables"]
            elif f in s:
                row[f] = s[f]
        out_slides.append(row)

    if spec.get("limit"):
        out_slides = out_slides[: int(spec["limit"])]

    as_of = src.get("as_of")
    return {
        "deck_id": spec["deck_id"],
        "kind": "presentation",
        "source": {"file": src["file"], "n_slides": src.get("n_slides", len(slides))},
        "as_of": [as_of] if as_of else [],
        "staleness": staleness(as_of, today),
        "n_slides_returned": len(out_slides),
        "citation": f'{alias}/deck',
        "provenance_slides": [s["slide"] for s in picked][: int(spec["limit"])] if spec.get("limit")
                             else [s["slide"] for s in picked],
        "slides": out_slides,
    }


def dispatch(spec, today):
    """Route by spec shape: a presentation card is queried by slide, a table by rows."""
    if "deck_id" in spec:
        return run_deck(spec, today)
    return run(spec, today)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", help="path to spec JSON (default: read stdin)")
    ap.add_argument("--today", default="2026-07", help="YYYY-MM, for staleness")
    args = ap.parse_args()
    spec_text = Path(args.spec).read_text() if args.spec else sys.stdin.read()
    spec = json.loads(spec_text)
    ty, tm = args.today.split("-")
    today = (int(ty), int(tm))
    print(json.dumps(dispatch(spec, today), indent=2, default=str))


if __name__ == "__main__":
    main()
