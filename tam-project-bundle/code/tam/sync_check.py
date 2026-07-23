#!/usr/bin/env python3
"""
sync_check.py — quick health check for a copy of the bundle.

Confirms the bundle resolves and is writable, and gives a hint about whether it's sitting
inside a OneDrive/SharePoint-synced folder (so ingests will reach the team). There is
NOTHING to manage here — no locks, no coordination. Concurrency on the shared index is
handled automatically by build_index.py (it regenerates index.json atomically and cleans
up any conflict copies), so teammates never run a "lock" step.

Usage:
  python3 code/tam/sync_check.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tam_root import resolve_root  # noqa: E402


def _looks_synced(root: Path) -> tuple[bool, str]:
    p = str(root).replace("\\", "/").lower()
    for h in ("onedrive", "sharepoint", "cloudstorage", "- documents", "exlservice"):
        if h in p:
            return True, f"path contains '{h}'"
    for var in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
        v = os.environ.get(var)
        if v and str(root).lower().startswith(v.lower()):
            return True, f"under ${var}"
    return False, "no sync marker found in path or environment"


def _writable(root: Path) -> bool:
    try:
        probe = root / "produced_data" / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except Exception:
        return False


def main() -> int:
    root = resolve_root()
    synced, why = _looks_synced(root)
    print(f"TAM root:      {root}")
    print(f"Writable:      {'yes' if _writable(root) else 'NO — cannot save ingests here'}")
    print(f"Synced share:  {'likely yes' if synced else 'UNKNOWN'} ({why})")
    if not synced:
        print("\nNote: this copy may not be in a synced folder. If you ingest here, "
              "teammates won't receive the new file until it lands in the synced "
              "SharePoint library. See docs/SHAREPOINT_SETUP.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
