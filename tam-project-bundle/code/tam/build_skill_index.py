#!/usr/bin/env python3
"""
build_skill_index.py — assemble a compact catalog of the skills in this bundle.

Scans .claude/skills/<name>/SKILL.md, reads the frontmatter (name + description), and writes
produced_data/skills_catalog.json — one small entry per skill. This lets the main skill
(tam-ask) tell people what's already available and steer them away from building overlapping
skills, without hardcoding a list that would go stale or bloat any prompt.

Run it after adding, editing, or removing a skill (the same way build_index.py is run after
ingesting data). It's cheap and idempotent.

Usage:
  python3 code/tam/build_skill_index.py          # rebuild the catalog
  python3 code/tam/build_skill_index.py --print  # rebuild and print a human-readable list
"""
import json, os, re, sys, glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tam_root import resolve_root

REPO = resolve_root()
SKILLS_DIR = REPO / ".claude" / "skills"
OUT = REPO / "produced_data" / "skills_catalog.json"

# top-level frontmatter keys that end a multi-line value
_KEY = re.compile(r"^(name|description|allowed-tools|tools|model|license|version):\s?(.*)$")


def _parse_frontmatter(text: str) -> dict:
    """Minimal frontmatter parser: grabs the block between the first two '---' lines and
    reads key: value pairs, joining wrapped/indented continuation lines into one value."""
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.S | re.M)
    if not m:
        return {}
    fm, cur, out = m.group(1).splitlines(), None, {}
    for line in fm:
        km = _KEY.match(line)
        if km:
            cur = km.group(1)
            out[cur] = km.group(2).strip()
        elif cur and line.strip():
            out[cur] = (out[cur] + " " + line.strip()).strip()
    return out


def build():
    entries = []
    for skill_md in sorted(glob.glob(str(SKILLS_DIR / "*" / "SKILL.md"))):
        folder = Path(skill_md).parent.name
        if folder.startswith(("_", ".")):
            continue  # templates / hidden helpers are not live skills
        fm = _parse_frontmatter(Path(skill_md).read_text(encoding="utf-8"))
        entries.append({
            "name": fm.get("name", folder),
            "description": fm.get("description", "").strip(),
            "path": f".claude/skills/{folder}/SKILL.md",
        })
    entries.sort(key=lambda e: e["name"])
    catalog = {
        "corpus": "EXL insurance TAM",
        "n_skills": len(entries),
        "note": "Available skills in this bundle. Before creating a new skill, check here for "
                "one that already covers the need; extend it instead of duplicating. Rebuild "
                "with: python3 code/tam/build_skill_index.py",
        "skills": entries,
    }
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))
    os.replace(tmp, OUT)
    return catalog


def main():
    catalog = build()
    print(f"Wrote {OUT}  ({catalog['n_skills']} skills)")
    if "--print" in sys.argv:
        print()
        for s in catalog["skills"]:
            print(f"- {s['name']}: {s['description']}")


if __name__ == "__main__":
    main()
