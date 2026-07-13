#!/usr/bin/env python3
"""
exl-sales-intelligence — entrypoint for the EXL competitive-intelligence pipeline.

Usage:
  python3 run.py list_accounts                # all 236 accounts, ranked
  python3 run.py account <name>               # full sales brief
  python3 run.py top [N]                      # top N (default 10)
  python3 run.py triggers <name>              # what fired at this account
  python3 run.py whitespace                   # heatmap + Partnering Matrix highlights
  python3 run.py refresh                      # re-run all 7 pipeline stages
"""
import sys, os, subprocess, time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent              # .claude/skills/exl-sales-intelligence/
TAM_ROOT   = SCRIPT_DIR.parent.parent.parent              # TAM/
PIPELINE   = TAM_ROOT / "pipeline"
DATA       = PIPELINE / "data"
LEADS      = PIPELINE / "leads"

# Defer heavy imports
def _pandas():
    import pandas as pd
    return pd


def _check_pipeline_built():
    """Verify the pipeline outputs exist; nudge user to refresh if not."""
    needed = [DATA / "leads_ranked.csv", DATA / "triggers_fired.csv"]
    missing = [p for p in needed if not p.exists()]
    if missing:
        print("Pipeline outputs not found — run `refresh` first.")
        print("Missing:")
        for p in missing:
            print(f"  - {p}")
        sys.exit(1)


def cmd_list_accounts(args):
    """All 236 accounts, full ranked list."""
    _check_pipeline_built()
    pd = _pandas()
    df = pd.read_csv(DATA / "leads_ranked.csv")
    print(f"All {len(df)} accounts in the TAM corpus, ranked by lead score:")
    print()
    print(f"{'Rank':>4}  {'Score':>5}  {'Conf':<10}  {'Rel':<14}  {'Triggers':>8}  Account")
    print("-" * 100)
    for _, r in df.iterrows():
        rel = str(r.get('relationship_type') or '-')[:14]
        conf = r['confidence']
        trig = int(r.get('num_triggers_fired') or 0)
        score = r['lead_score']
        marker = ""
        if score >= 70: marker = " ★"
        elif score >= 55: marker = " ●"
        print(f"{int(r['rank']):>4}  {score:>5.1f}  {conf:<10}  {rel:<14}  {trig:>8}  {r['client_canonical']}{marker}")
    print()
    print(f"  ★ = Very High confidence (score ≥ 70)")
    print(f"  ● = High confidence (score 55–69)")
    print()
    print(f"Tip: `account <name>` for full brief on any account.")


def cmd_account(args):
    """Print the sales brief for a specific account."""
    _check_pipeline_built()
    pd = _pandas()
    if not args:
        print("Usage: account <name>   (e.g. account travelers)")
        return
    query = " ".join(args).lower().strip()

    # 1) Try the lead .md files first (top 20 have generated briefs)
    files = sorted(LEADS.glob("*.md"))
    # match against slugified filename body
    file_matches = []
    for f in files:
        stem_normalised = f.stem.split('_', 1)[-1].replace('_', ' ').lower()  # drop the rank prefix
        if query in stem_normalised:
            file_matches.append(f)

    if len(file_matches) == 1:
        print(file_matches[0].read_text())
        return
    if len(file_matches) > 1:
        print(f"Multiple lead briefs match '{query}':\n")
        for f in file_matches:
            print(f"  {f.stem}")
        print("\nNarrow the query (e.g. `account travelers group`).")
        return

    # 2) No brief — see if the account exists at all
    df = pd.read_csv(DATA / "leads_ranked.csv")
    candidates = df[df.client_canonical.str.lower().str.contains(query, regex=False, na=False)]

    if candidates.empty:
        print(f"No account matches '{query}'.")
        print("\nTop 15 accounts in the corpus (for reference):")
        for _, r in df.head(15).iterrows():
            print(f"  #{int(r['rank']):>3}  {r['lead_score']:>5.1f}  {r['client_canonical']}")
        print("\nUse `list_accounts` to see all 236.")
        return

    print(f"Found {len(candidates)} account(s) matching '{query}':\n")
    for _, r in candidates.iterrows():
        in_top20 = int(r['rank']) <= 20
        marker = "  (brief available)" if in_top20 else "  (no brief — outside top 20)"
        print(f"  #{int(r['rank']):>3}  {r['lead_score']:>5.1f}  {r['confidence']:<10}  {r['client_canonical']}{marker}")
    print()
    print("Briefs are pre-generated only for the top 20. For lower-ranked accounts, "
          "use `triggers <name>` to see what signals fired.")


def cmd_top(args):
    """Top N leads."""
    _check_pipeline_built()
    pd = _pandas()
    n = int(args[0]) if args and args[0].isdigit() else 10
    df = pd.read_csv(DATA / "leads_ranked.csv").head(n)
    print(f"Top {n} leads by lead score:")
    print()
    print(f"{'Rank':>4}  {'Score':>5}  {'Conf':<10}  {'Triggers':>8}  {'Account':<32}  Top recommended EXL products")
    print("-" * 130)
    for _, r in df.iterrows():
        sols = str(r.get('recommended_solutions') or '')[:60]
        client = str(r['client_canonical'])[:32]
        print(f"{int(r['rank']):>4}  {r['lead_score']:>5.1f}  {r['confidence']:<10}  {int(r['num_triggers_fired']):>8}  {client:<32}  {sols}")
    print()
    print("Tip: `account <name>` for the full source-cited brief on any account.")


def cmd_triggers(args):
    """Show trigger firings for one account, with full evidence."""
    _check_pipeline_built()
    pd = _pandas()
    if not args:
        print("Usage: triggers <name>")
        return
    query = " ".join(args).lower().strip()
    df = pd.read_csv(DATA / "triggers_fired.csv")
    matches = df[df.client_canonical.str.lower().str.contains(query, regex=False, na=False)]
    if matches.empty:
        print(f"No triggers fired for accounts matching '{query}'.")
        print("Either the account has no signal in the corpus, or the name doesn't match.")
        print("Try `list_accounts` to see canonical names.")
        return
    clients = sorted(matches.client_canonical.unique())
    for client in clients:
        client_fires = matches[matches.client_canonical == client].sort_values('strength', ascending=False)
        print()
        print("=" * 80)
        print(f"  {client} — {len(client_fires)} triggers fired")
        print("=" * 80)
        for i, (_, t) in enumerate(client_fires.iterrows(), 1):
            print(f"\n  T{i}. [{t['trigger_id']}]  strength={t['strength']:.2f}")
            print(f"      {t['evidence_text']}")
            srcs = str(t['evidence_sources'])[:200]
            print(f"      Sources: {srcs}")


def cmd_whitespace(args):
    """Summary view of the strategic heatmap + Partnering Matrix."""
    _check_pipeline_built()
    pd = _pandas()
    xlsx = PIPELINE / "WHITESPACE_MAP.xlsx"
    if not xlsx.exists():
        print(f"Whitespace map not found at {xlsx}. Run `refresh` first.")
        return
    print("=" * 90)
    print("  PARTNERING MATRIX — EXL retention benchmarks, sorted by displacement headroom")
    print("=" * 90)
    df_pm = pd.read_excel(xlsx, sheet_name="Partnering Matrix", header=3)
    # Filter to only real data rows (those with a non-NaN retention range)
    df_pm = df_pm.dropna(subset=['Function', 'EXL Retention Range'])
    for _, r in df_pm.iterrows():
        fn = str(r.get('Function', ''))[:36]
        ret = str(r.get('EXL Retention Range', ''))
        hp = str(r.get('Headroom %', ''))
        label = str(r.get('Headroom Label', ''))
        print(f"  {fn:<36}  retention {ret:<10}  headroom {hp:<6}  ({label})")

    print()
    print("=" * 90)
    print("  TOP 20 WHITE-SPACE ACCOUNTS — high lead score × many open functions")
    print("=" * 90)
    df_ws = pd.read_excel(xlsx, sheet_name="White Space Ranking", header=3)
    for _, r in df_ws.head(20).iterrows():
        client = str(r.get('Client', ''))[:32]
        score = r.get('Lead Score', 0)
        rel   = str(r.get('Rel', ''))[:14]
        opens = r.get('# Open Functions', 0)
        cov   = r.get('# Covered Functions', 0)
        dom   = str(r.get('Dominant Competitor', '') or '')[:24]
        print(f"  {client:<32}  score={score:>5}  {rel:<14}  open={opens:>2}  covered={cov:>2}  dominant={dom}")
    print()
    print(f"Full workbook (7 sheets): {xlsx}")


def cmd_refresh(args):
    """Re-run all 7 pipeline stages end-to-end."""
    stages = ["ingest.py", "audit.py", "profiles.py", "triggers.py",
              "score.py", "synthesize.py", "whitespace.py"]
    print(f"Refreshing pipeline ({len(stages)} stages)…")
    t0 = time.time()
    for s in stages:
        script_path = PIPELINE / s
        print(f"\n  ▶ {s}")
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"    FAILED (exit {result.returncode})")
            print(result.stderr[-1000:])
            sys.exit(1)
        # show last 2 lines of stdout
        tail = [l for l in result.stdout.strip().split("\n") if l.strip()][-2:]
        for line in tail:
            print(f"    {line}")
    dt = time.time() - t0
    print(f"\nDone in {dt:.1f}s. Run `top 10` to see latest leads.")


COMMANDS = {
    "list_accounts": cmd_list_accounts,
    "list":          cmd_list_accounts,
    "ls":            cmd_list_accounts,
    "account":       cmd_account,
    "acct":          cmd_account,
    "top":           cmd_top,
    "triggers":      cmd_triggers,
    "whitespace":    cmd_whitespace,
    "ws":            cmd_whitespace,
    "refresh":       cmd_refresh,
}


def main():
    if len(sys.argv) < 2:
        print("Usage: run.py <command> [args...]")
        print()
        print("Commands:")
        seen = set()
        for c, fn in COMMANDS.items():
            if fn in seen: continue
            seen.add(fn)
            doc = (fn.__doc__ or "").strip().split('\n')[0]
            print(f"  {c:<14} {doc}")
        return
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]
    fn = COMMANDS.get(cmd)
    if not fn:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(sorted(set(COMMANDS.keys())))}")
        sys.exit(1)
    fn(args)


if __name__ == "__main__":
    main()
