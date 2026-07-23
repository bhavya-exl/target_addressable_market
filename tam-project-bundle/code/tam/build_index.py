#!/usr/bin/env python3
"""
build_index.py — assemble produced_data/cards/index.json (the routing index).

Reads every card in produced_data/cards/*.json (skips the _profiles/ dir and index.json
itself) and emits a compact index: enough for Claude to ROUTE a question to the right
table(s) without loading full schemas. No columns/examples in the index — just id, title,
grain, summary, use_cases, entity_key_col, as_of, joins, duplicate_of, role.

Safe on a shared OneDrive/SharePoint folder — NO locks, nothing for anyone to manage:
  * index.json is 100% derived from the cards, so it is always regenerated from scratch.
  * It is written atomically (temp file + os.replace) so a reader never sees a half-written
    file, even if two people rebuild at nearly the same moment.
  * Before writing, any OneDrive "conflicted copy" of index.json left behind by a rare
    simultaneous rebuild is deleted — the freshly regenerated index supersedes it.
So if two people ingest close together, the next rebuild self-heals. Nobody coordinates.
"""
import json, os, sys, glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tam_root import resolve_root
REPO = resolve_root()
CARDS = REPO / "produced_data" / "cards"


def _heal_conflicts():
    """Remove OneDrive/SharePoint conflict copies of index.json (e.g.
    'index-Bhavya's conflicted copy 2026-07-22.json'). The index is regenerable, so
    these stray copies are never authoritative and are safe to delete."""
    removed = 0
    for pat in ("index*conflicted copy*.json", "index*_conflict*.json",
                "index* (conflict*).json"):
        for f in glob.glob(str(CARDS / pat)):
            if Path(f).name != "index.json":
                try:
                    os.remove(f); removed += 1
                except OSError:
                    pass
    if removed:
        print(f"  self-heal: removed {removed} stray index conflict copy(ies)")


def _write_atomic(path: Path, text: str):
    """Write to a temp file in the same dir, then atomically replace — a reader always
    sees either the old or the new index, never a partial one."""
    tmp = path.with_suffix(path.suffix + f".tmp-{os.getpid()}")
    tmp.write_text(text)
    os.replace(tmp, path)


def _is_real_card(name: str) -> bool:
    """A real card is F<n>.<slug>.json. Never the index, and never a OneDrive conflict
    copy of anything (which would otherwise be read as a bogus/duplicate table)."""
    low = name.lower()
    if name == "index.json" or name.startswith("index"):
        return False
    if "conflicted copy" in low or "_conflict" in low or "(conflict" in low:
        return False
    return name.endswith(".json")


def main():
    # Best-effort tidy of any stray index conflict copies up front (no-op if deletion is
    # unavailable — the _is_real_card filter below still keeps them out of the index).
    _heal_conflicts()
    entries = []
    for p in sorted(CARDS.glob("*.json")):
        if not _is_real_card(p.name):
            continue
        try:
            c = json.loads(p.read_text())
        except Exception as e:
            print(f"  ! skip {p.name}: {e}")
            continue
        joins = sorted({j for col in c.get("columns", []) for j in col.get("joins", []) or []})
        src = c.get("source", {}) or {}
        kind = c.get("kind", "table")       # "table" (spreadsheet) | "presentation" | "image"
        has_entities = kind in ("presentation", "image")
        entries.append({
            "table_id": c.get("table_id", p.stem),
            "title": c.get("title"),
            "kind": kind,
            "role": c.get("role", "data"),
            "grain": c.get("grain"),
            "file_alias": src.get("file_alias"),
            "source_file": Path(src.get("file", "")).name or None,
            "as_of": src.get("as_of"),
            "as_of_basis": src.get("as_of_basis"),      # stated | inferred | unknown (temporality)
            "summary": c.get("summary"),
            "use_cases": c.get("use_cases", []),
            "entity_key_col": c.get("entity_key_col"),
            "joins": joins,
            "duplicate_of": c.get("duplicate_of"),
            "row_count": c.get("row_count"),
            # presentations: how many slides; presentations & images: the entities mentioned (routing)
            "n_slides": src.get("n_slides") if kind == "presentation" else None,
            "entities": [e.get("name") for e in c.get("entities", [])] if has_entities else None,
        })
    # queryable content first (tables + decks + images), then non-data stubs; stable by id
    rank = {"data": 0, "presentation": 0, "image": 0}
    entries.sort(key=lambda e: (rank.get(e["role"], 2), e["table_id"]))
    out = {
        "corpus": "EXL insurance TAM",
        "n_tables": len(entries),
        "n_data_tables": sum(1 for e in entries if e["role"] == "data"),
        "n_presentations": sum(1 for e in entries if e["kind"] == "presentation"),
        "n_images": sum(1 for e in entries if e["kind"] == "image"),
        "note": "Routing index over spreadsheet TABLES, presentation DECKS, and IMAGES. Match a "
                "question to summary/use_cases; prefer canonical over duplicate_of; then load the "
                "full card from produced_data/cards/<table_id>.json. Tables are queried by row "
                "(table spec); decks by slide (deck_id) — every slide individually citable; images "
                "by transcript (image_id). Each entry carries as_of + as_of_basis (temporality).",
        "tables": entries,
    }
    _write_atomic(CARDS / "index.json", json.dumps(out, indent=2, default=str))
    print(f"Wrote {CARDS/'index.json'}  ({len(entries)} tables, "
          f"{out['n_data_tables']} data)")


if __name__ == "__main__":
    main()
