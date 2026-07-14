#!/usr/bin/env python3
"""
package.py — build a self-contained bundle for a claude.ai Project (option 2).

Assembles everything a teammate needs into dist/tam-project-bundle/ (and a .zip):
skills + engine + cards + alias map + the ONLY the source data files the cards
actually reference (derived from each card's source.file) + the .tam-root sentinel
+ the setup guide. Upload the zip to a Team/Enterprise Project; add the three
SKILL folders as org Skills. The engine's resolver then finds everything.

Usage:  python3 code/tam/package.py
"""
import json, shutil, sys, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tam_root import resolve_root

ROOT = resolve_root()
OUT = ROOT / "dist" / "tam-project-bundle"
CARDS = ROOT / "produced_data" / "cards"


def copy(rel):
    src = ROOT / rel
    dst = OUT / rel
    if not src.exists():
        print(f"  ! missing (skipped): {rel}")
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return sum(1 for _ in dst.rglob("*") if _.is_file())
    shutil.copy2(src, dst)
    return 1


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    n = 0

    # 1. sentinel + setup guide
    (OUT / ".tam-root").write_text((ROOT / ".tam-root").read_text() if (ROOT / ".tam-root").exists()
                                   else "TAM package root\n")
    n += 1
    n += copy("docs/PROJECT_SETUP.md")
    n += copy("docs/TAM_SKILLS.md")

    # 2. skills
    for s in ("tam-ingest", "tam-ask", "tam-report"):
        n += copy(f".claude/skills/{s}")

    # 3. engine (python + templates), excluding caches
    for p in (ROOT / "code" / "tam").rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            n += copy(p.relative_to(ROOT))

    # 4. cards + index (not _profiles)
    for p in sorted(CARDS.glob("*.json")):
        n += copy(p.relative_to(ROOT))

    # 5. alias map (normalize.py expects this exact path)
    n += copy("produced_data/pipeline/data/aliases.csv")

    # 6. ONLY the data files the cards reference (derived from the cards)
    data_files = set()
    for p in CARDS.glob("*.json"):
        if p.name == "index.json":
            continue
        try:
            c = json.loads(p.read_text())
        except Exception:
            continue
        f = (c.get("source") or {}).get("file")
        if f:
            data_files.add(f)
    print(f"  data files referenced by cards: {len(data_files)}")
    for f in sorted(data_files):
        n += copy(f)

    # 7. zip the Project bundle
    zip_path = ROOT / "dist" / "tam-project-bundle.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in OUT.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(OUT.parent))

    # 8. one upload-ready .zip per skill (claude.ai Skills wants a zip containing SKILL.md)
    skills_dir = ROOT / "dist" / "skills"
    if skills_dir.exists():
        shutil.rmtree(skills_dir)
    skills_dir.mkdir(parents=True)
    for s in ("tam-ingest", "tam-ask", "tam-report"):
        src = ROOT / ".claude" / "skills" / s
        if not src.exists():
            continue
        sz = skills_dir / f"{s}.zip"
        with zipfile.ZipFile(sz, "w", zipfile.ZIP_DEFLATED) as z:
            for p in src.rglob("*"):
                if p.is_file() and "__pycache__" not in p.parts:
                    z.write(p, Path(s) / p.relative_to(src))
    print(f"  skill upload zips: {skills_dir}/{{tam-ingest,tam-ask,tam-report}}.zip")

    size_mb = zip_path.stat().st_size / 1e6
    print(f"\nBundle: {OUT}  ({n} files)")
    print(f"Zip:    {zip_path}  ({size_mb:.1f} MB)")
    print("Upload the zip to a claude.ai Project; add the 3 skill folders as org Skills. "
          "See docs/PROJECT_SETUP.md.")


if __name__ == "__main__":
    main()
