"""
Stage 3: Assemble per-account profiles
=======================================
Joins the ingested CSVs into:
  - client_profiles.csv               (1 row per canonical client, all summary fields)
  - client_engagements_summary.csv    (1 row per client x competitor pair, aggregated)

These two views are what the trigger library queries.

Dedupe rule: F1 + F5 Competitor Analysis are identical; we keep F5 only (canonical).
"""

import pandas as pd
import os, re
from datetime import date

from pathlib import Path
REPO = Path(__file__).resolve().parents[2]                      # repo root (code/pipeline/<script>.py)
DATA = str(REPO / "produced_data" / "pipeline" / "data")
REPORT = str(REPO / "produced_data" / "pipeline" / "PROFILES_REPORT.md")

INGESTION_DATE = date.today().isoformat()

# ============ Load ============

ti = pd.read_csv(f"{DATA}/clients_top_insurers.csv")
s3 = pd.read_csv(f"{DATA}/clients_sheet3.csv")
sl = pd.read_csv(f"{DATA}/clients_top_clients_shortlist.csv")
ca = pd.read_csv(f"{DATA}/engagements_competitor_analysis.csv")
f4 = pd.read_csv(f"{DATA}/engagements_f4_clientwise.csv")
pr = pd.read_csv(f"{DATA}/priorities.csv")

# Dedupe: keep F5 only for competitor_analysis
ca_canonical = ca[ca['source_file'] == 'F5'].copy()
print(f"Loaded: {len(ti)} top_insurers, {len(s3)} sheet3, {len(sl)} shortlist, "
      f"{len(ca)} engagements (raw), {len(ca_canonical)} engagements (F5 only), "
      f"{len(f4)} F4 engagements, {len(pr)} priorities")

# ============ Helpers ============

def parse_ftes(s):
    """Extract a numeric FTE estimate from messy free-text like '~1000 - 1300', '$10M-$15M (~500 FTEs)', '300-500 FTEs', '450', 'Unknown'."""
    if pd.isna(s) or s is None:
        return None
    s = str(s).strip()
    if not s or s.lower() in ("unknown", "tbd", "na", "n/a"):
        return None
    # Pull the first integer-looking number
    m = re.search(r'(\d{2,5})', s)
    if m:
        return int(m.group(1))
    return None

def parse_revenue_usd_m(s):
    """Pull a $-million estimate from free-text like '$10M-$15M (~500 FTEs)', '$2.5M', '$6.5M'."""
    if pd.isna(s) or s is None: return None
    s = str(s)
    m = re.search(r'\$(\d+(?:\.\d+)?)\s*M', s, re.IGNORECASE)
    if m: return float(m.group(1))
    return None

def first_non_null(*vals):
    for v in vals:
        if v is not None and not (isinstance(v, float) and pd.isna(v)) and str(v).strip() not in ("", "nan"):
            return v
    return None

def to_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return ""
    return str(v).strip()


# ============ Build client_profiles ============

# Get the union of all canonical client names across sources
all_clients = set()
for df in (ti, s3, sl):
    all_clients.update(df['client_canonical'].dropna().astype(str))

all_clients.discard("")
all_clients.discard("nan")

# Build a lookup: canonical -> top_insurers row (first match), sheet3 row, shortlist row
ti_by_canon = {}
for _, row in ti.iterrows():
    c = row['client_canonical']
    if isinstance(c, str) and c not in ti_by_canon:
        ti_by_canon[c] = row

s3_by_canon = {}
for _, row in s3.iterrows():
    c = row['client_canonical']
    if isinstance(c, str) and c not in s3_by_canon:
        s3_by_canon[c] = row

sl_by_canon = {}
for _, row in sl.iterrows():
    c = row['client_canonical']
    if isinstance(c, str) and c not in sl_by_canon:
        sl_by_canon[c] = row

# Build profiles
profiles = []
for client in sorted(all_clients):
    t = ti_by_canon.get(client, pd.Series(dtype=object))
    s = s3_by_canon.get(client, pd.Series(dtype=object))
    l = sl_by_canon.get(client, pd.Series(dtype=object))

    # Engagements at this client (F5 + F4)
    ca_eng = ca_canonical[ca_canonical['client_canonical'] == client]
    f4_eng = f4[f4['client_canonical'] == client]
    num_competitors = len(set(list(ca_eng['competitor_canonical'].dropna()) + list(f4_eng['competitor_canonical'].dropna())))
    total_ftes_at_account = 0
    for f in ca_eng['ftes'].dropna():
        v = parse_ftes(f)
        if v: total_ftes_at_account += v
    for f in f4_eng['ftes_or_revenue_freetext'].dropna():
        v = parse_ftes(f)
        if v: total_ftes_at_account += v
    # Aggregate competitor presence summary
    comp_summary = {}
    for _, r in ca_eng.iterrows():
        cc = r['competitor_canonical']
        if pd.isna(cc): continue
        comp_summary.setdefault(cc, {"engagements": 0, "ftes": 0, "renewals": []})
        comp_summary[cc]["engagements"] += 1
        f = parse_ftes(r['ftes'])
        if f: comp_summary[cc]["ftes"] += f
        rw = to_str(r['contract_renewal_window'])
        if rw: comp_summary[cc]["renewals"].append(rw)
    competitor_summary_str = "; ".join(
        f"{c} ({d['engagements']} eng, {d['ftes'] or '?'} FTEs"
        + (f", renewal {min(d['renewals'])}" if d['renewals'] else "")
        + ")"
        for c, d in sorted(comp_summary.items(), key=lambda x: -x[1]['ftes'])
    )

    # Priorities at this client
    client_priorities = pr[pr['client_canonical'] == client]
    num_priorities = len(client_priorities)
    num_priorities_not_initiated = len(client_priorities[client_priorities['solution_life_cycle'] == "Not Initiated"])
    num_priorities_with_solution = len(client_priorities[client_priorities['exl_solution'].notna() & (client_priorities['exl_solution'] != "")])

    # File vintages we touched
    vintages = set()
    for src in (t, s, l):
        if hasattr(src, 'get'):
            v = src.get('file_vintage')
            if v and not pd.isna(v): vintages.add(str(v))
    for df_chunk in (ca_eng, f4_eng, client_priorities):
        for v in df_chunk.get('file_vintage', pd.Series()).dropna():
            vintages.add(str(v))

    profiles.append({
        "client_canonical": client,

        # Identity
        "type": first_non_null(t.get('type'), s.get('strategic_named')),  # weak fallback
        "geography": first_non_null(t.get('geography'), s.get('geography'), l.get('geography')),
        "nwp_2019": t.get('nwp_2019'),
        "pct_change_yoy": t.get('pct_change'),
        "rank_2019": t.get('rank_2019'),
        "combined_ratio": first_non_null(t.get('combined_ratio'), s.get('combined_ratio'), l.get('combined_ratio')),
        "gwp": first_non_null(s.get('gwp'), l.get('gwp')),
        "growth_pct": first_non_null(s.get('growth_pct'), l.get('growth_pct')),

        # EXL relationship
        "relationship_type": first_non_null(t.get('relationship_type'), s.get('strategic_named'), l.get('strategic_named')),
        "bucket_strategy": l.get('bucket_strategy'),
        "priority_position": l.get('priority_position'),
        "exl_growth_leader": first_non_null(t.get('growth_leader'), l.get('growth_leader')),
        "exl_ce": first_non_null(t.get('ce'), s.get('client_exec'), l.get('client_exec')),
        "outsource": first_non_null(t.get('outsource'), s.get('outsource')),
        "exl_client": t.get('exl_client'),
        "exl_share_of_wallet": t.get('exl_share_of_wallet'),
        "renewal_timeframe_account_level": t.get('renewal_timeframe'),
        "future_tcv": t.get('future_tcv'),
        "client_priority_rating": t.get('client_priority_rating'),
        "exl_competitors_listed": first_non_null(t.get('exl_competitors_freetext'), s.get('exl_competitors')),
        "year_flag": first_non_null(t.get('year_flag'), s.get('year_flag')),

        # Stakeholders (prefer top_insurers; fill from sheet3)
        "ceo": first_non_null(t.get('ceo'), s.get('ceo')),
        "cfo": first_non_null(t.get('cfo'), s.get('cfo')),
        "cro": first_non_null(t.get('cro'), s.get('cro')),
        "cco": first_non_null(t.get('cco'), s.get('cco')),
        "coo": first_non_null(t.get('coo'), s.get('coo')),
        "cio_cto": first_non_null(t.get('cio_cto'), s.get('cio_cto')),
        "cuo": first_non_null(t.get('cuo'), s.get('cuo')),

        # Competitor footprint summary
        "num_competitors_at_account": num_competitors,
        "total_competitor_ftes_estimated": total_ftes_at_account if total_ftes_at_account > 0 else None,
        "competitors_at_account_summary": competitor_summary_str,
        "num_engagements_total": len(ca_eng) + len(f4_eng),

        # Priorities summary
        "num_priorities": num_priorities,
        "num_priorities_not_initiated": num_priorities_not_initiated,
        "num_priorities_with_mapped_solution": num_priorities_with_solution,

        # Provenance
        "source_files_touched": ",".join(sorted({sf for sf in [t.get('source_file'), s.get('source_file'), l.get('source_file')] if sf and not pd.isna(sf)})),
        "file_vintages_touched": ",".join(sorted(vintages)),
        "ingestion_date": INGESTION_DATE,
    })

profiles_df = pd.DataFrame(profiles)
profiles_df.to_csv(f"{DATA}/client_profiles.csv", index=False)
print(f"Wrote client_profiles.csv: {len(profiles_df)} rows")


# ============ Build client_engagements_summary ============

eng_summary = []
# F5 engagements
for client in sorted(all_clients):
    ca_eng = ca_canonical[ca_canonical['client_canonical'] == client]
    f4_eng = f4[f4['client_canonical'] == client]

    competitors_seen = set()
    competitors_seen.update(ca_eng['competitor_canonical'].dropna())
    competitors_seen.update(f4_eng['competitor_canonical'].dropna())

    for competitor in sorted(competitors_seen):
        ca_c = ca_eng[ca_eng['competitor_canonical'] == competitor]
        f4_c = f4_eng[f4_eng['competitor_canonical'] == competitor]

        # Aggregate FTEs from both sources
        ftes_total = 0
        for f in ca_c['ftes'].dropna():
            v = parse_ftes(f)
            if v: ftes_total += v
        for f in f4_c['ftes_or_revenue_freetext'].dropna():
            v = parse_ftes(f)
            if v: ftes_total += v

        revenue_usd_m_total = 0
        for f in f4_c['ftes_or_revenue_freetext'].dropna():
            v = parse_revenue_usd_m(f)
            if v: revenue_usd_m_total += v

        # Functions covered (from CA flags)
        functions = []
        for col in ('claims_y', 'uw_y', 'premium_audit_y', 'fna_y', 'platform_y'):
            if (ca_c[col] == 'Y').any():
                functions.append(col.replace('_y', '').upper().replace('FNA', 'F&A'))
        functions_str = ", ".join(functions) if functions else ""

        # Renewal windows
        renewals = sorted({to_str(rw) for rw in ca_c['contract_renewal_window'].dropna() if to_str(rw)})
        renewals_str = "; ".join(renewals)

        # Comments
        comments = "; ".join(to_str(c) for c in ca_c['comments'].dropna() if to_str(c))[:400]

        # Statuses (the "Current Status" col in F5)
        statuses = "; ".join(to_str(c) for c in ca_c['current_status'].dropna() if to_str(c))[:400]

        # F4 segment notes
        f4_segments = "; ".join(to_str(c) for c in f4_c['competitor_segment_supported'].dropna() if to_str(c))[:400]
        f4_research = "; ".join(to_str(c) for c in f4_c['research_notes'].dropna() if to_str(c))[:400]

        # Owner (from CA)
        owner = first_non_null(*ca_c['owner'].dropna()[:1])

        # Sources
        source_refs = []
        for _, r in ca_c.iterrows():
            source_refs.append(f"{r['source_file']}/{r['source_sheet']}/R{r['source_row']}")
        for _, r in f4_c.iterrows():
            source_refs.append(f"{r['source_file']}/{r['source_sheet']}/R{r['source_row']}")
        source_refs_str = "; ".join(source_refs)

        # File vintages
        vintages = set()
        for v in list(ca_c['file_vintage'].dropna()) + list(f4_c['file_vintage'].dropna()):
            vintages.add(str(v))
        vintages_str = ",".join(sorted(vintages))

        # Friction signals in comments + statuses
        text_all = (comments + " " + statuses).lower()
        friction_terms = ["champion challenger", "given notice", "terminating", "exploring champion",
                          "given formal notice", "bad experience", "moved away"]
        friction_hits = [t for t in friction_terms if t in text_all]

        eng_summary.append({
            "client_canonical": client,
            "competitor_canonical": competitor,
            "num_engagements": len(ca_c) + len(f4_c),
            "total_ftes_estimated": ftes_total if ftes_total > 0 else None,
            "revenue_usd_m_estimated": revenue_usd_m_total if revenue_usd_m_total > 0 else None,
            "functions_covered": functions_str,
            "renewal_windows": renewals_str,
            "comments_concat": comments,
            "current_status_concat": statuses,
            "f4_segments_supported": f4_segments,
            "f4_research_notes": f4_research,
            "owner": owner,
            "friction_signals": ",".join(friction_hits),
            "source_refs": source_refs_str,
            "file_vintages_touched": vintages_str,
            "ingestion_date": INGESTION_DATE,
        })

eng_df = pd.DataFrame(eng_summary)
eng_df.to_csv(f"{DATA}/client_engagements_summary.csv", index=False)
print(f"Wrote client_engagements_summary.csv: {len(eng_df)} rows")


# ============ Report ============

# Top 20 accounts by total competitor FTE estimate
top20_by_ftes = profiles_df.dropna(subset=['total_competitor_ftes_estimated']).sort_values(
    'total_competitor_ftes_estimated', ascending=False).head(20)

# Strategic/Named accounts
strategic = profiles_df[profiles_df['relationship_type'].isin(['Strategic', 'Named', 'Named Backup'])]

# Clients with priorities mapped
clients_with_priorities = profiles_df[profiles_df['num_priorities'] > 0]

report = f"""# Profiles Report

Generated: {os.popen('date').read().strip()}
Ingestion date: {INGESTION_DATE}

## Outputs

| File | Rows | Description |
|---|---:|---|
| `client_profiles.csv` | {len(profiles_df)} | One row per canonical client with identity + EXL relationship + CxOs + competitor & priority aggregates |
| `client_engagements_summary.csv` | {len(eng_df)} | One row per (client, competitor) pair with aggregated FTEs / functions / renewals / comments / friction signals |

## Coverage

- **Unique canonical clients in profiles**: {len(profiles_df)}
- **Strategic/Named/Named Backup clients**: {len(strategic)}
- **Clients with mapped VOC priorities**: {len(clients_with_priorities)}
- **Unique (client, competitor) engagement pairs**: {len(eng_df)}

## Top 20 accounts by estimated competitor FTE footprint

| Client | Type | NWP 2019 | Rank | CR | Rel | EXL Client | Total Competitor FTEs (est) | # Competitors |
|---|---|---:|---:|---:|---|---|---:|---:|
"""
for _, r in top20_by_ftes.iterrows():
    nwp = f"${int(r['nwp_2019']):,}" if pd.notna(r['nwp_2019']) else "-"
    cr = f"{float(r['combined_ratio']):.1f}" if pd.notna(r['combined_ratio']) and str(r['combined_ratio']) not in ('', 'nan') else "-"
    rank = int(r['rank_2019']) if pd.notna(r['rank_2019']) else "-"
    report += f"| {r['client_canonical']} | {r['type'] or ''} | {nwp} | {rank} | {cr} | {r['relationship_type'] or ''} | {r['exl_client'] or ''} | {int(r['total_competitor_ftes_estimated'])} | {r['num_competitors_at_account']} |\n"

# Dedup proof (F1 vs F5)
report += f"""

## Dedup proof

- Raw engagements (F1 + F5 Competitor Analysis combined): {len(ca)}
- After dedup (F5 canonical only): {len(ca_canonical)}
- Dropped (F1 duplicates): {len(ca) - len(ca_canonical)}

## Notes

- FTE counts are best-effort extracted from messy free-text ('~1000 - 1300', '$10M-$15M (~500 FTEs)', etc.) - take with confidence-band caution.
- Where the same competitor has multiple engagements at one client (e.g., Cognizant at Travelers = 5 separate scopes), totals are summed.
- `friction_signals` column flags free-text mentions of 'Champion Challenger', 'given notice', etc. - used by Trigger #8 in the next stage.
- Clients with VOC priorities ({len(clients_with_priorities)}) = the only ones with `num_priorities_not_initiated > 0` will fire Trigger #4 (unaddressed VOC).
"""

with open(REPORT, 'w') as f:
    f.write(report)

print(f"Report: {REPORT}")
