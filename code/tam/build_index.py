#!/usr/bin/env python3
"""
build_index.py — assemble produced_data/cards/index.json (the routing index).

Reads every card in produced_data/cards/*.json (skips the _profiles/ dir and index.json
itself) and emits a compact index: enough for Claude to ROUTE a question to the right
table(s) without loading full schemas. No columns/examples in the index — just id, title,
grain, summary, use_cases, entity_key_col, as_of, joins, duplicate_of, role.
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tam_root import resolve_root
REPO = resolve_root()
CARDS = REPO / "produced_data" / "cards"


def main():
    entries = []
    for p in sorted(CARDS.glob("*.json")):
        if p.name == "index.json":
            continue
        try:
            c = json.loads(p.read_text())
        except Exception as e:
            print(f"  ! skip {p.name}: {e}")
            continue
        joins = sorted({j for col in c.get("columns", []) for j in col.get("joins", []) or []})
        entries.append({
            "table_id": c.get("table_id", p.stem),
            "title": c.get("title"),
            "role": c.get("role", "data"),
            "grain": c.get("grain"),
            "as_of": (c.get("source", {}) or {}).get("as_of"),
            "summary": c.get("summary"),
            "use_cases": c.get("use_cases", []),
            "entity_key_col": c.get("entity_key_col"),
            "joins": joins,
            "duplicate_of": c.get("duplicate_of"),
            "row_count": c.get("row_count"),
        })
    # data tables first, then stubs; stable by id
    entries.sort(key=lambda e: (e["role"] != "data", e["table_id"]))
    out = {
        "corpus": "EXL insurance TAM",
        "n_tables": len(entries),
        "n_data_tables": sum(1 for e in entries if e["role"] == "data"),
        "note": "Routing index. Pick the minimal set of tables by matching a question to "
                "summary/use_cases; prefer canonical over duplicate_of; then load the full "
                "card(s) from produced_data/cards/<table_id>.json.",
        "tables": entries,
    }
    (CARDS / "index.json").write_text(json.dumps(out, indent=2, default=str))
    print(f"Wrote {CARDS/'index.json'}  ({len(entries)} tables, "
          f"{out['n_data_tables']} data)")


if __name__ == "__main__":
    main()
