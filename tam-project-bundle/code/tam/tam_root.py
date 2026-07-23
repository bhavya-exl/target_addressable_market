#!/usr/bin/env python3
"""
tam_root.py — locate the TAM package root, wherever the package has been dropped.

In the repo, the root is the repo top. In a claude.ai Project (or a zip a teammate
unpacked), the files land somewhere else entirely. Every engine script resolves its
data paths through resolve_root() so it works in both cases with no code changes.

Resolution order:
  1. $TAM_ROOT env var, if it points at a valid package.
  2. A directory containing the '.tam-root' sentinel AND 'produced_data/cards',
     searched upward from this file and from the cwd, plus common hosted mount points.
  3. Fallback: the nearest ancestor that simply contains 'produced_data/cards'.
Set TAM_ROOT explicitly to skip the search.
"""
import os
from pathlib import Path

SENTINEL = ".tam-root"
MARKER = Path("produced_data") / "cards"


def _valid(p: Path) -> bool:
    return (p / MARKER).is_dir()


def _candidates():
    seen = set()
    def add(p):
        try:
            p = Path(p).resolve()
        except Exception:
            return
        if p not in seen:
            seen.add(p)
            yield p
    # upward from this file and from cwd
    for base in (Path(__file__).resolve(), Path.cwd().resolve()):
        for anc in [base, *base.parents]:
            yield from add(anc)
    # common hosted upload/mount roots and their immediate children
    for root in ("/mnt/user-data", "/mnt/user-data/uploads", "/mnt/data",
                 "/mnt/project", "/mnt/skills", "/workspace", "/home/user"):
        rp = Path(root)
        if rp.exists():
            yield from add(rp)
            try:
                for child in rp.iterdir():
                    if child.is_dir():
                        yield from add(child)
            except Exception:
                pass


def resolve_root() -> Path:
    env = os.environ.get("TAM_ROOT")
    if env:
        p = Path(env).expanduser()
        if _valid(p):
            return p.resolve()
    # prefer a dir with BOTH the sentinel and the marker
    fallback = None
    for c in _candidates():
        if _valid(c):
            if (c / SENTINEL).exists():
                return c
            if fallback is None:
                fallback = c
    if fallback is not None:
        return fallback
    raise RuntimeError(
        "TAM package root not found. Set the TAM_ROOT environment variable to the "
        "folder that contains 'produced_data/cards' (and ideally a '.tam-root' file)."
    )


if __name__ == "__main__":
    print(resolve_root())
