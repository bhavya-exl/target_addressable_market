"""
Stage 4: Trigger library + signal detection
============================================
Evaluates 13 trigger rules against per-client profiles and emits a fired-trigger
log that the scoring engine (Stage 5) will consume.

Output: pipeline/data/triggers_fired.csv
        One row per (client, trigger, evidence) tuple, with:
          client_canonical, trigger_id, trigger_name, evidence_text,
          evidence_sources, strength, captured_date, ingestion_date

The trigger library IS the lead engine's IP. Each rule:
  - is deterministic (rules-based, not LLM)
  - is auditable (every firing carries source-row citations)
  - has a strength weight tunable independent of the rule logic
"""

import pandas as pd
import os, re, sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from exl_taxonomy import RETENTION_BENCHMARKS, retention_headroom

DATA = "/Users/bhavya242574/Library/CloudStorage/OneDrive-EXLService.com(I)Pvt.Ltd/Desktop/TAM/pipeline/data"
REPORT = "/Users/bhavya242574/Library/CloudStorage/OneDrive-EXLService.com(I)Pvt.Ltd/Desktop/TAM/pipeline/TRIGGERS_REPORT.md"

INGESTION_DATE = date.today().isoformat()

# ============ Load ============
profiles = pd.read_csv(f"{DATA}/client_profiles.csv")
engagements = pd.read_csv(f"{DATA}/client_engagements_summary.csv")
ca = pd.read_csv(f"{DATA}/engagements_competitor_analysis.csv")
priorities = pd.read_csv(f"{DATA}/priorities.csv")
captives = pd.read_csv(f"{DATA}/captives.csv")

# Use F5 canonical only
ca = ca[ca['source_file'] == 'F5']

# ============ Trigger definitions ============
# Each entry: id, name, weight (1.0 = max strength contribution), description

TRIGGER_DEFS = {
    "renewal_le_6mo":           {"name": "Incumbent renewal within 6 months",          "weight": 1.0},
    "renewal_le_12mo":          {"name": "Incumbent renewal within 12 months",         "weight": 0.7},
    "mass_renewal":             {"name": "Multiple incumbent scopes renewing together","weight": 1.0},
    "active_friction":          {"name": "Active competitor friction (free-text signal)","weight": 0.9},
    "unaddressed_voc":          {"name": "Mapped VOC priority not yet initiated",      "weight": 0.6},
    "cost_pressure":            {"name": "Combined ratio > 100 (cost-pressure)",       "weight": 0.5},
    "strategic_low_wallet":     {"name": "Strategic/Named with low EXL wallet share",  "weight": 0.6},
    "greenfield_outsourcer":    {"name": "Greenfield prospect (Mutual/Private not outsourcing)","weight": 0.4},
    "high_competitor_ftes":     {"name": "Single competitor with ≥200 FTEs at named account","weight": 0.7},
    "multi_competitor_friction":{"name": "Multiple competitors at one client all in friction","weight": 1.0},
    "competitor_concentration": {"name": "Large competitor footprint at one client (≥500 FTEs)","weight": 0.6},
    "named_backup":             {"name": "Named-Backup status at top-25 account",       "weight": 0.5},
    "captive_rationalization":  {"name": "Captive operations re-evaluating WFH/onshore","weight": 0.5},
    "function_headroom":        {"name": "Competitor parked in function with high EXL retention headroom","weight": 0.85},
}

# Keyword patterns mapping free-text engagement comments to granular function buckets
# from the Partnering Matrix (slides 10-11). Order matters; first match wins per category.
GRANULAR_FUNCTION_PATTERNS = [
    (["fnol", "first notification of loss", "claim intake", "claim setup", "claim set up"], "Claims Set up (FNOL)"),
    (["underwriting risk assessment", "risk assessment"], "Underwriting Risk Assessment"),
    (["underwriting rating", "rating "], "Underwriting Rating"),
    (["account set up", "account setup", "clearance", "submission "], "Account Set Up & Clearance"),
    (["policy issuance"], "Policy Issuance"),
    (["policy servicing", "endorsement", "policy maintenance", "policy admin"], "Policy Servicing"),
    (["subrogation"], "Subrogation"),
    (["coverage verification"], "Coverage verification"),
    (["compliance"], "Compliance"),
    (["investigation"], "Investigation"),
    (["bill review", "utilization review", "resolution", "settlement", "adjudication"], "Resolution"),
    (["information gathering", "info gathering"], "Underwriting Info Gathering"),
]

def classify_to_granular_function(text):
    """Maps free-text comments to the first matching granular function bucket.
    Returns list of (function_label, matched_keyword) tuples."""
    t = str(text).lower() if text else ""
    if not t: return []
    matches = []
    seen = set()
    for keywords, label in GRANULAR_FUNCTION_PATTERNS:
        if label in seen: continue
        for k in keywords:
            if k in t:
                matches.append((label, k))
                seen.add(label)
                break
    return matches

# ============ Helpers ============

def src(*refs):
    """Format source refs as 'F1/Sheet/R12; F5/Sheet/R8'."""
    return "; ".join(str(r) for r in refs if r)

def fire(rule_id, client, evidence_text, evidence_sources, strength, raw_data=""):
    return {
        "client_canonical": client,
        "trigger_id": rule_id,
        "trigger_name": TRIGGER_DEFS[rule_id]["name"],
        "evidence_text": evidence_text,
        "evidence_sources": evidence_sources,
        "strength": round(strength, 2),
        "raw_data": raw_data,
        "captured_date": INGESTION_DATE,  # trigger evaluation date
        "ingestion_date": INGESTION_DATE,
    }

def parse_num(v):
    if v is None: return None
    try:
        f = float(v)
        if pd.isna(f): return None
        return f
    except (TypeError, ValueError): return None

def to_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return ""
    return str(v).strip()


# ============ Trigger rules ============

def t_renewal_le_6mo(profile, c_engs, c_prios):
    out = []
    for _, e in c_engs.iterrows():
        rw = to_str(e.get('renewal_windows'))
        if "< 6 Months" in rw:
            ftes = parse_num(e.get('total_ftes_estimated')) or 0
            out.append(fire(
                "renewal_le_6mo", profile['client_canonical'],
                f"{e['competitor_canonical']} contract renews in < 6 months "
                f"(~{int(ftes) if ftes else '?'} FTEs across {e['num_engagements']} scope(s), functions: {e['functions_covered'] or 'unspecified'})",
                e['source_refs'],
                strength=TRIGGER_DEFS["renewal_le_6mo"]["weight"],
                raw_data=f"competitor={e['competitor_canonical']};ftes={ftes};engagements={e['num_engagements']}"
            ))
    return out

def t_renewal_le_12mo(profile, c_engs, c_prios):
    out = []
    for _, e in c_engs.iterrows():
        rw = to_str(e.get('renewal_windows'))
        if "1 Year" in rw and "< 6 Months" not in rw:  # exclude already-counted-by-T1
            ftes = parse_num(e.get('total_ftes_estimated')) or 0
            out.append(fire(
                "renewal_le_12mo", profile['client_canonical'],
                f"{e['competitor_canonical']} contract renews within 1 year (~{int(ftes) if ftes else '?'} FTEs)",
                e['source_refs'],
                strength=TRIGGER_DEFS["renewal_le_12mo"]["weight"],
                raw_data=f"competitor={e['competitor_canonical']};ftes={ftes}"
            ))
    return out

def t_mass_renewal(profile, c_engs, c_prios):
    """3+ competitor engagements at one client all in a near-term renewal window."""
    near_renewals = c_engs[c_engs['renewal_windows'].fillna('').str.contains("< 6 Months", na=False)]
    if len(near_renewals) >= 2:  # at least 2 separate competitors with <6mo renewal -> aggregate signal
        return []  # individual triggers already fired via T1; mass_renewal fires when ALL near-term scopes converge
    # Actually re-interpret: mass_renewal = ONE competitor with 3+ engagements ALL in same renewal window
    out = []
    for _, e in c_engs.iterrows():
        rw = to_str(e.get('renewal_windows'))
        if e['num_engagements'] >= 3 and ("< 6 Months" in rw or "1 Year" in rw):
            ftes = parse_num(e.get('total_ftes_estimated')) or 0
            out.append(fire(
                "mass_renewal", profile['client_canonical'],
                f"Single-vendor displacement window: {e['competitor_canonical']} holds {e['num_engagements']} concurrent scopes "
                f"(~{int(ftes) if ftes else '?'} FTEs) all renewing in {rw}",
                e['source_refs'],
                strength=TRIGGER_DEFS["mass_renewal"]["weight"],
                raw_data=f"competitor={e['competitor_canonical']};num_scopes={e['num_engagements']};ftes={ftes}"
            ))
    return out

def t_active_friction(profile, c_engs, c_prios):
    out = []
    for _, e in c_engs.iterrows():
        fs = to_str(e.get('friction_signals'))
        if fs:
            out.append(fire(
                "active_friction", profile['client_canonical'],
                f"{e['competitor_canonical']}: friction signals in account notes — {fs}. "
                f"Comments: {to_str(e['comments_concat'])[:150]}{'...' if len(to_str(e['comments_concat'])) > 150 else ''}",
                e['source_refs'],
                strength=TRIGGER_DEFS["active_friction"]["weight"],
                raw_data=f"competitor={e['competitor_canonical']};signals={fs}"
            ))
    return out

def t_unaddressed_voc(profile, c_engs, c_prios):
    pending = c_prios[(c_prios['solution_life_cycle'] == "Not Initiated") &
                      c_prios['exl_solution'].notna() & (c_prios['exl_solution'] != "")]
    if pending.empty: return []
    # Aggregate: one fire per (priority area, solution) tuple
    out = []
    grouped = pending.groupby(['priority_area', 'exl_solution'])
    for (area, sol), grp in grouped:
        refs = "; ".join(f"{r.source_file}/{r.source_sheet}/R{r.source_row}" for _, r in grp.iterrows())
        out.append(fire(
            "unaddressed_voc", profile['client_canonical'],
            f"VOC priority '{area}' has {len(grp)} mapped component(s) for EXL {sol} solution — status 'Not Initiated'",
            refs,
            strength=TRIGGER_DEFS["unaddressed_voc"]["weight"],
            raw_data=f"priority_area={area};solution={sol};components={len(grp)}"
        ))
    return out

def t_cost_pressure(profile, c_engs, c_prios):
    cr = parse_num(profile.get('combined_ratio'))
    if cr is None or cr <= 100: return []
    return [fire(
        "cost_pressure", profile['client_canonical'],
        f"Combined ratio {cr:.1f} (>100) indicates underwriting/operating pressure — cost optimization receptivity high",
        f"client_profile (derived from F1/Top Insurers and Brokers + sheet3)",
        strength=TRIGGER_DEFS["cost_pressure"]["weight"],
        raw_data=f"combined_ratio={cr}"
    )]

def t_strategic_low_wallet(profile, c_engs, c_prios):
    rt = to_str(profile.get('relationship_type'))
    if rt not in ("Strategic", "Named", "Named Backup"): return []
    share = to_str(profile.get('exl_share_of_wallet')).lower()
    exl_client = to_str(profile.get('exl_client'))
    if share == "low" or (exl_client.lower() != "yes" and rt in ("Strategic", "Named")):
        return [fire(
            "strategic_low_wallet", profile['client_canonical'],
            f"{rt} account but EXL share-of-wallet = '{share or '(blank)'}' / EXL Client = '{exl_client or '(blank)'}'",
            "client_profile (F1/Top Insurers and Brokers)",
            strength=TRIGGER_DEFS["strategic_low_wallet"]["weight"],
            raw_data=f"relationship={rt};share={share};exl_client={exl_client}"
        )]
    return []

def t_greenfield_outsourcer(profile, c_engs, c_prios):
    typ = to_str(profile.get('type'))
    outsource = to_str(profile.get('outsource')).lower()
    if "mutual" in typ.lower() or "private" in typ.lower():
        if not outsource or outsource == "no":
            return [fire(
                "greenfield_outsourcer", profile['client_canonical'],
                f"{typ} carrier with Outsource={outsource or '(blank)'} — no incumbent outsourcer footprint in the corpus",
                "client_profile (F1/Top Insurers and Brokers)",
                strength=TRIGGER_DEFS["greenfield_outsourcer"]["weight"],
                raw_data=f"type={typ};outsource={outsource}"
            )]
    return []

def t_high_competitor_ftes(profile, c_engs, c_prios):
    rt = to_str(profile.get('relationship_type'))
    if rt not in ("Strategic", "Named", "Named Backup"): return []
    out = []
    for _, e in c_engs.iterrows():
        ftes = parse_num(e.get('total_ftes_estimated')) or 0
        if ftes >= 200:
            out.append(fire(
                "high_competitor_ftes", profile['client_canonical'],
                f"{e['competitor_canonical']} has ~{int(ftes)} FTEs at this {rt} account — large displacement target",
                e['source_refs'],
                strength=TRIGGER_DEFS["high_competitor_ftes"]["weight"],
                raw_data=f"competitor={e['competitor_canonical']};ftes={ftes};relationship={rt}"
            ))
    return out

def t_multi_competitor_friction(profile, c_engs, c_prios):
    in_friction = c_engs[c_engs['friction_signals'].fillna('') != '']
    if len(in_friction) >= 2:
        comps = "; ".join(f"{r['competitor_canonical']}({r['friction_signals']})" for _, r in in_friction.iterrows())
        refs = "; ".join(in_friction['source_refs'].dropna())
        return [fire(
            "multi_competitor_friction", profile['client_canonical'],
            f"{len(in_friction)} concurrent incumbents in friction: {comps}",
            refs,
            strength=TRIGGER_DEFS["multi_competitor_friction"]["weight"],
            raw_data=f"competitors_in_friction={len(in_friction)}"
        )]
    return []

def t_competitor_concentration(profile, c_engs, c_prios):
    total = parse_num(profile.get('total_competitor_ftes_estimated')) or 0
    if total >= 500:
        return [fire(
            "competitor_concentration", profile['client_canonical'],
            f"Aggregate competitor footprint at this account ~{int(total)} FTEs ({profile['num_competitors_at_account']} competitors, {profile['num_engagements_total']} engagements)",
            "client_engagements_summary (derived from F4 + F5)",
            strength=TRIGGER_DEFS["competitor_concentration"]["weight"],
            raw_data=f"total_ftes={total};num_competitors={profile['num_competitors_at_account']}"
        )]
    return []

def t_named_backup(profile, c_engs, c_prios):
    rt = to_str(profile.get('relationship_type'))
    rank = parse_num(profile.get('rank_2019'))
    if rt == "Named Backup" and rank and rank <= 25:
        return [fire(
            "named_backup", profile['client_canonical'],
            f"Named Backup at rank #{int(rank)} carrier — EXL on bench, primed for displacement window",
            "client_profile (F1/Top Insurers and Brokers)",
            strength=TRIGGER_DEFS["named_backup"]["weight"],
            raw_data=f"rank={int(rank)}"
        )]
    return []

def t_function_headroom(profile, c_engs, c_prios):
    """For each engagement, classify the competitor's scope into a granular function,
    look up EXL's typical retention for that function, and fire if headroom is high.
    The trigger surfaces the *expanded TAM* — if a competitor has N FTEs at function X
    where EXL typically retains R%, the total function size at that client is ~N/R FTEs.
    """
    out = []
    for _, e in c_engs.iterrows():
        comments = to_str(e.get('comments_concat', ''))
        functions_covered = to_str(e.get('functions_covered', ''))
        text = comments + " " + functions_covered
        matches = classify_to_granular_function(text)
        if not matches: continue

        ftes = parse_num(e.get('total_ftes_estimated')) or 0

        for fn_label, kw in matches:
            headroom_pct, hr_label = retention_headroom(fn_label)
            if headroom_pct is None or headroom_pct < 50:
                continue  # only fire on functions with substantial headroom

            # Estimate expanded TAM
            retention_frac = (100 - headroom_pct) / 100
            expanded_tam_str = ""
            if retention_frac > 0 and ftes > 0:
                expanded_tam = int(ftes / retention_frac)
                expanded_tam_str = f", implying ~{expanded_tam} FTE TAM at this function"

            strength = 0.4 + (headroom_pct / 100) * 0.5  # 0.4 baseline + up to 0.5 from headroom
            strength = min(round(strength, 2), 1.0)

            ev = (f"{e['competitor_canonical']} parked at '{fn_label}' "
                  f"({int(ftes) if ftes else '?'} FTEs documented). "
                  f"EXL typical retention for this function is only {100 - headroom_pct:.0f}% "
                  f"({hr_label}{expanded_tam_str}).")

            out.append(fire(
                "function_headroom", profile['client_canonical'], ev,
                e['source_refs'],
                strength=strength,
                raw_data=f"competitor={e['competitor_canonical']};function={fn_label};kw={kw};"
                         f"ftes={ftes};headroom_pct={headroom_pct}"
            ))
    return out


def t_captive_rationalization(profile, c_engs, c_prios):
    cap = captives[captives['client_canonical'] == profile['client_canonical']]
    if cap.empty: return []
    out = []
    for _, c in cap.iterrows():
        covid = to_str(c.get('covid_impact')).lower()
        commentary = to_str(c.get('leader_subjective_commentary')).lower()
        if any(t in covid + commentary for t in ["rethink", "rethinking", "wfh", "70% wfh", "90% wfh",
                                                  "moving back", "repatriat", "continuity", "moving to"]):
            out.append(fire(
                "captive_rationalization", profile['client_canonical'],
                f"Captive operations ({c['country']}, ~{c['ftes'] or '?'} FTEs) showing WFH/onshore re-evaluation: "
                f"\"{to_str(c['covid_impact'])[:120]}\"",
                f"{c['source_file']}/{c['source_sheet']}/R{c['source_row']}",
                strength=TRIGGER_DEFS["captive_rationalization"]["weight"],
                raw_data=f"country={c['country']};ftes={c['ftes']}"
            ))
    return out


ALL_TRIGGERS = [
    t_renewal_le_6mo, t_renewal_le_12mo, t_mass_renewal, t_active_friction,
    t_unaddressed_voc, t_cost_pressure, t_strategic_low_wallet,
    t_greenfield_outsourcer, t_high_competitor_ftes, t_multi_competitor_friction,
    t_competitor_concentration, t_named_backup, t_captive_rationalization,
    t_function_headroom,
]

# ============ Evaluate ============

fires = []
for _, prof in profiles.iterrows():
    client = prof['client_canonical']
    c_engs = engagements[engagements['client_canonical'] == client]
    c_prios = priorities[priorities['client_canonical'] == client]
    for rule in ALL_TRIGGERS:
        fires.extend(rule(prof, c_engs, c_prios))

fires_df = pd.DataFrame(fires)
fires_df.to_csv(f"{DATA}/triggers_fired.csv", index=False)
print(f"Wrote triggers_fired.csv: {len(fires_df)} firings")


# ============ Report ============

# Firings per trigger
per_trigger = fires_df.groupby(['trigger_id', 'trigger_name']).size().reset_index(name='firings').sort_values('firings', ascending=False)

# Firings per client (clients with most triggers fired)
per_client = fires_df.groupby('client_canonical').agg(
    triggers_fired=('trigger_id', 'count'),
    unique_trigger_types=('trigger_id', 'nunique'),
    sum_strength=('strength', 'sum'),
).reset_index().sort_values('sum_strength', ascending=False)

# Top 25 clients with highest aggregate trigger strength (leading indicator of lead quality)
top25 = per_client.head(25)

report = f"""# Triggers Report

Generated: {os.popen('date').read().strip()}
Evaluation date: {INGESTION_DATE}

## Trigger library

13 deterministic rules. Each fire is sourced to specific cells. No LLM in this stage.

| # | ID | Name | Weight |
|---:|---|---|---:|
"""
for i, (tid, td) in enumerate(TRIGGER_DEFS.items(), 1):
    report += f"| {i} | `{tid}` | {td['name']} | {td['weight']:.2f} |\n"

report += f"""

## Total firings: {len(fires_df)}

## Firings by trigger type

| Trigger | Firings |
|---|---:|
"""
for _, r in per_trigger.iterrows():
    report += f"| `{r['trigger_id']}` ({r['trigger_name']}) | {r['firings']} |\n"

report += f"""

## Top 25 clients by aggregate trigger strength

This is the proto-lead ranking. Stage 5 (scoring) will combine this with account-fit + solution-match weights.

| Rank | Client | Triggers Fired | Unique Trigger Types | Σ Strength |
|---:|---|---:|---:|---:|
"""
for i, (_, r) in enumerate(top25.iterrows(), 1):
    report += f"| {i} | {r['client_canonical']} | {r['triggers_fired']} | {r['unique_trigger_types']} | {r['sum_strength']:.2f} |\n"

# Sample full lead detail for the top client
if len(top25) > 0:
    top_client = top25.iloc[0]['client_canonical']
    top_fires = fires_df[fires_df['client_canonical'] == top_client].sort_values('strength', ascending=False)
    report += f"""

## Sample: all triggers fired for **{top_client}** (rank #1)

| Trigger | Strength | Evidence | Sources |
|---|---:|---|---|
"""
    for _, r in top_fires.iterrows():
        ev = r['evidence_text'][:200].replace('|', '\\|') + ('...' if len(r['evidence_text']) > 200 else '')
        srcs = r['evidence_sources'][:80].replace('|', '\\|') if isinstance(r['evidence_sources'], str) else ''
        report += f"| `{r['trigger_id']}` | {r['strength']:.2f} | {ev} | {srcs} |\n"

report += f"""

## Output

- `pipeline/data/triggers_fired.csv` — every firing with full evidence + sources

## Next stage (Task #8)

Score & rank leads:
```
lead_score = w1·account_fit          (NWP rank, Strategic/Named status, growth %)
           + w2·signal_strength      (Σ trigger strength + recency)
           + w3·solution_match       (does the trigger map cleanly to a packaged solution?)
           + w4·relationship_warmth  (EXL CE in place? Growth Leader assigned? prior wins?)
```
Default weights 0.30 / 0.40 / 0.20 / 0.10 (calibrate after seeing top-N leads).
"""

with open(REPORT, 'w') as f:
    f.write(report)

print(f"Report: {REPORT}")
print(f"\nTop 10 by aggregate strength:")
print(top25.head(10).to_string(index=False))
