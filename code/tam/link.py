#!/usr/bin/env python3
"""
link.py — detect joins BETWEEN tables by value overlap. Domain-blind.

For every pair of data cards that declare an entity_key_col, read those columns,
canonicalize the values (via normalize), and if two columns share enough values,
record a join on each card's entity column. No knowledge of what the entities are —
purely "these two columns contain the same names."

Run after cards exist; then rebuild the index. Idempotent (recomputes joins each run).
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import normalize as N
from query import read_table

from tam_root import resolve_root
REPO = resolve_root()
CARDS = REPO / "produced_data" / "cards"

MIN_SHARED = 5        # need at least this many shared canonical values
MIN_FRAC = 0.30       # OR this fraction of the smaller column's distinct values


def entity_values(card):
    col = card.get("entity_key_col")
    if not col:
        return None
    try:
        df = read_table(card)
    except Exception:
        return None
    if col not in df.columns:
        return None
    vals = {N.canonical(v)[0] for v in df[col].dropna().tolist() if str(v).strip()}
    vals = {v for v in vals if v and str(v).strip()}
    return vals or None


def main():
    cards = {}
    for p in sorted(CARDS.glob("*.json")):
        if p.name == "index.json":
            continue
        c = json.loads(p.read_text())
        if c.get("role", "data") == "data" and c.get("entity_key_col"):
            cards[c["table_id"]] = (p, c)

    values = {tid: entity_values(c) for tid, (p, c) in cards.items()}
    values = {tid: v for tid, v in values.items() if v}

    # reset joins on entity columns, then recompute
    links = {tid: set() for tid in cards}
    ids = list(values.keys())
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            shared = values[a] & values[b]
            smaller = min(len(values[a]), len(values[b]))
            if len(shared) >= MIN_SHARED or (smaller and len(shared) / smaller >= MIN_FRAC):
                ca = cards[a][1]["entity_key_col"]
                cb = cards[b][1]["entity_key_col"]
                links[a].add(f"{b}.{cb}")
                links[b].add(f"{a}.{ca}")

    n_written = 0
    for tid, (p, c) in cards.items():
        ekey = c["entity_key_col"]
        found = sorted(links.get(tid, []))
        for col in c.get("columns", []):
            if col.get("name") == ekey:
                col["joins"] = found
                break
        p.write_text(json.dumps(c, indent=2, default=str))
        if found:
            n_written += 1
    print(f"link.py: annotated joins on {n_written}/{len(cards)} entity-keyed tables. "
          f"Re-run build_index.py to capture them in the index.")


if __name__ == "__main__":
    main()
