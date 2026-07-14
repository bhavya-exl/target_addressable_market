#!/usr/bin/env python3
"""
normalize.py — entity-name normalization (part of ingest AND query).

Wraps the corpus alias map (produced_data/pipeline/data/aliases.csv:
entity_kind,variant,canonical) so that "TRV" / "Travelers Companies Inc." /
"travelers group" all resolve to the one canonical account name. Deterministic.

CLI:
  python3 code/tam/normalize.py --scan "TRV" "Allstate Corp" "Nowhere Inc"
      -> JSON {value: {canonical, matched: exact|fuzzy|UNMATCHED, score}}
  python3 code/tam/normalize.py --append --kind client --variant "trv corp" --canonical "Travelers Group"

Library:
  from normalize import canonical, normalize_series, load_aliases
"""
import sys, csv, json, argparse, difflib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tam_root import resolve_root
REPO = resolve_root()
ALIASES = REPO / "produced_data" / "pipeline" / "data" / "aliases.csv"

_CACHE = None


def load_aliases():
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    m = {}          # variant(lower) -> (canonical, kind)
    canon = set()
    if ALIASES.exists():
        with open(ALIASES, newline="", encoding="utf-8", errors="ignore") as f:
            for row in csv.DictReader(f):
                v = (row.get("variant") or "").strip().lower()
                c = (row.get("canonical") or "").strip()
                k = (row.get("entity_kind") or "").strip()
                if v and c:
                    m[v] = (c, k)
                    canon.add(c)
    # every canonical is also a variant of itself
    for c in canon:
        m.setdefault(c.lower(), (c, ""))
    _CACHE = (m, sorted(canon))
    return _CACHE


def canonical(name, kind=None, fuzzy=True):
    """Return (canonical_name, match_kind, score)."""
    if name is None:
        return (None, "UNMATCHED", 0.0)
    key = str(name).strip().lower()
    if not key:
        return (str(name), "UNMATCHED", 0.0)
    m, canon = load_aliases()
    if key in m:
        return (m[key][0], "exact", 1.0)
    if fuzzy:
        # fuzzy against known variants
        hit = difflib.get_close_matches(key, list(m.keys()), n=1, cutoff=0.88)
        if hit:
            return (m[hit[0]][0], "fuzzy", round(difflib.SequenceMatcher(None, key, hit[0]).ratio(), 3))
    return (str(name).strip(), "UNMATCHED", 0.0)


def normalize_series(series):
    """Map a pandas Series of names to canonical form (for query-time joins/filters)."""
    return series.map(lambda v: canonical(v)[0] if v is not None else v)


def scan(values):
    out = {}
    for v in values:
        c, kind, score = canonical(v)
        out[str(v)] = {"canonical": c, "matched": kind, "score": score}
    return out


def append(kind, variant, canon):
    exists = ALIASES.exists()
    with open(ALIASES, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["entity_kind", "variant", "canonical"])
        w.writerow([kind, variant.strip().lower(), canon.strip()])
    global _CACHE
    _CACHE = None
    return {"appended": {"entity_kind": kind, "variant": variant.strip().lower(), "canonical": canon.strip()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", nargs="*")
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--kind", default="client")
    ap.add_argument("--variant")
    ap.add_argument("--canonical")
    args = ap.parse_args()
    if args.append:
        print(json.dumps(append(args.kind, args.variant, args.canonical), indent=2))
    elif args.scan is not None:
        print(json.dumps(scan(args.scan), indent=2))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
