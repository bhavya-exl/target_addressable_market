"""
Stage 5: Solution-match + scoring engine
=========================================
For each client, compute:
  - solution_matches:   which EXL packaged solutions each trigger maps to
  - lead_score:         weighted aggregate of (account_fit, signal_strength,
                                               solution_match, relationship_warmth)

Output:
  - leads_ranked.csv          One row per client with score components + total
  - solution_matches.csv      One row per (client, trigger) -> matched solutions
"""

import pandas as pd
import os, re, sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from exl_taxonomy import (
    EXL_PRODUCTS, FUNCTION_TO_PRODUCTS, LEGACY_CODE_TO_PRODUCT,
    product_outcome, products_for_function, map_legacy_code,
)

DATA = "/Users/bhavya242574/Library/CloudStorage/OneDrive-EXLService.com(I)Pvt.Ltd/Desktop/TAM/pipeline/data"
INGESTION_DATE = date.today().isoformat()

profiles = pd.read_csv(f"{DATA}/client_profiles.csv")
fires = pd.read_csv(f"{DATA}/triggers_fired.csv")
eng_summary = pd.read_csv(f"{DATA}/client_engagements_summary.csv")
priorities = pd.read_csv(f"{DATA}/priorities.csv")

# ============ Scoring weights ============
W_ACCOUNT_FIT       = 0.30
W_SIGNAL_STRENGTH   = 0.40
W_SOLUTION_MATCH    = 0.20
W_RELATIONSHIP      = 0.10

# ============ EXL Solution catalog (now sourced from exl_taxonomy.py) ============
# Functional area -> list of relevant EXL products (real names from the Addressable
# Market Tracker deck). The old generic names ("FNOL-aaS", "NB-PaaS") are kept only
# as legacy keys mapped through LEGACY_CODE_TO_PRODUCT for backward-compat.
FUNCTION_TO_SOLUTIONS = {
    "CLAIMS":         FUNCTION_TO_PRODUCTS["Claims / FNOL"],
    "UW":             FUNCTION_TO_PRODUCTS["Underwriting"],
    "PREMIUM_AUDIT":  FUNCTION_TO_PRODUCTS["Premium Audit"],
    "F&A":            FUNCTION_TO_PRODUCTS["F&A / Finance"],
    "PLATFORM":       FUNCTION_TO_PRODUCTS["Platform / Tech"],
}

# Solution code map — legacy codes -> EXL product strings
SOL_CODE_MAP = dict(LEGACY_CODE_TO_PRODUCT)

# ============ Helpers ============

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

def parse_raw_data(s):
    """Parse raw_data column 'competitor=Cognizant;ftes=1000;engagements=5' into dict."""
    if pd.isna(s) or not s: return {}
    out = {}
    for part in str(s).split(';'):
        if '=' in part:
            k, v = part.split('=', 1)
            out[k.strip()] = v.strip()
    return out

# ============ Solution matching per fire ============

solution_matches = []  # list of dicts: client, trigger_id, matched_solutions, basis

def match_solutions(fire_row):
    """Returns (list of matched solutions, basis for matching)."""
    tid = fire_row['trigger_id']
    rd = parse_raw_data(fire_row.get('raw_data', ''))
    evidence = to_str(fire_row.get('evidence_text'))

    # 1. unaddressed_voc fires already carry the mapped solution
    if tid == 'unaddressed_voc':
        sol_code = rd.get('solution', '').strip()
        if sol_code:
            full = SOL_CODE_MAP.get(sol_code, sol_code)
            return [full], f"VOC mapping (priority -> {sol_code})"
        return [], "VOC fire but no solution code"

    # 2. function-based mapping from evidence/raw_data
    matched = set()
    basis = []
    # Look for function keywords in evidence
    upper_ev = evidence.upper()
    for func, sols in FUNCTION_TO_SOLUTIONS.items():
        if func == "F&A" and "F&A" in upper_ev:
            matched.update(sols)
            basis.append("function:F&A in evidence")
        elif func != "F&A" and func in upper_ev:
            matched.update(sols)
            basis.append(f"function:{func} in evidence")

    # Also check raw_data for competitor + function info via comments
    if matched:
        return list(matched), "; ".join(basis)

    # 3. cost_pressure -> broad operational solutions (F&A + intake stack)
    if tid == 'cost_pressure':
        return ["EXL Paymentor", "EXL Digital Finance Suite", "EXL XTRAKTO.AI", "EXL NerveHub"], \
               "cost_pressure -> F&A + intake stack"

    # 4. strategic_low_wallet -> account-opening (broad)
    if tid == 'strategic_low_wallet':
        return ["EXL XTRAKTO.AI", "EXL NerveHub"], "strategic-low-wallet -> low-friction entry stack"

    # 5. competitor_concentration -> multi-solution orchestration
    if tid == 'competitor_concentration':
        return ["EXL NerveHub", "EXL XTRAKTO.AI", "EXL EXELIA.AI", "EXL Paymentor"], \
               "concentration -> sequenced multi-solution via NerveHub"

    # 6. captive_rationalization -> captive replacement / co-source
    if tid == 'captive_rationalization':
        return ["any (captive co-source / replace)"], "captive context"

    # 7. greenfield_outsourcer -> first-engagement play
    if tid == 'greenfield_outsourcer':
        return ["any (first-engagement consultative)"], "greenfield"

    # 8. named_backup -> displacement
    if tid == 'named_backup':
        return ["any (named-backup activation)"], "named-backup posture"

    # Generic / unmatched
    return [], "unmatched"

for _, fr in fires.iterrows():
    sols, basis = match_solutions(fr)
    solution_matches.append({
        "client_canonical": fr['client_canonical'],
        "trigger_id": fr['trigger_id'],
        "trigger_name": fr['trigger_name'],
        "matched_solutions": "; ".join(sols) if sols else "",
        "matching_basis": basis,
        "evidence_sources": fr.get('evidence_sources', ''),
    })

sm_df = pd.DataFrame(solution_matches)
sm_df.to_csv(f"{DATA}/solution_matches.csv", index=False)
print(f"Wrote solution_matches.csv: {len(sm_df)} rows")

# ============ Score components per client ============

def calc_account_fit(profile):
    """0-1: weighted by NWP rank, relationship type, growth"""
    score = 0.0
    rank = parse_num(profile.get('rank_2019'))
    if rank:
        if rank <= 10:   score += 0.4
        elif rank <= 25: score += 0.3
        elif rank <= 50: score += 0.2
        elif rank <= 100: score += 0.1

    rt = to_str(profile.get('relationship_type'))
    if rt == "Strategic":           score += 0.4
    elif rt == "Named":             score += 0.3
    elif rt == "Named Backup":      score += 0.2

    growth = parse_num(profile.get('pct_change_yoy'))
    if growth is not None:
        if growth >= 0.10:   score += 0.2
        elif growth >= 0.05: score += 0.15
        elif growth >= 0:    score += 0.05

    return min(round(score, 3), 1.0)

def calc_signal_strength(client_fires):
    """0-1: based on Σ trigger strength + diversity"""
    if client_fires.empty: return 0
    sum_strength = client_fires['strength'].sum()
    unique_types = client_fires['trigger_id'].nunique()
    # Cap sum at 5.0 -> contributes 0-0.8
    base = min(sum_strength / 5.0, 1.0) * 0.8
    # Diversity bonus: +0.04 per unique trigger type up to 0.2
    diversity = min(unique_types * 0.04, 0.2)
    return round(base + diversity, 3)

def calc_solution_match(client_fires, client_matches):
    """0-1: fraction of triggers that map to a clean EXL solution."""
    if client_fires.empty: return 0
    n_total = len(client_fires)
    n_matched = sum(1 for _, r in client_matches.iterrows()
                    if r['matched_solutions'] and r['matched_solutions'] != "unmatched"
                    and not r['matched_solutions'].startswith("any "))
    n_specific_voc = sum(1 for _, r in client_matches.iterrows()
                         if r['matching_basis'].startswith("VOC mapping"))
    # Base = fraction matched
    base = n_matched / n_total
    # Bonus for VOC-mapped triggers (already-mapped solutions = higher confidence)
    bonus = min(n_specific_voc * 0.05, 0.2)
    return round(min(base + bonus, 1.0), 3)

def calc_relationship_warmth(profile, client_engagements):
    """0-1: based on EXL ownership signals in the corpus"""
    score = 0.0
    if to_str(profile.get('exl_growth_leader')): score += 0.3
    if to_str(profile.get('exl_ce')):            score += 0.2
    if to_str(profile.get('exl_client')) == "Yes": score += 0.2
    if not client_engagements.empty:
        if client_engagements['owner'].notna().any() and (client_engagements['owner'] != "").any():
            score += 0.3
    return min(round(score, 3), 1.0)

def confidence_label(score):
    if score >= 70: return "Very High"
    elif score >= 55: return "High"
    elif score >= 40: return "Medium"
    elif score >= 25: return "Low"
    else: return "Very Low"

leads = []
for _, prof in profiles.iterrows():
    client = prof['client_canonical']
    c_fires = fires[fires['client_canonical'] == client]
    c_matches = sm_df[sm_df['client_canonical'] == client]
    c_engs = eng_summary[eng_summary['client_canonical'] == client]
    c_prios = priorities[priorities['client_canonical'] == client]

    af = calc_account_fit(prof)
    ss = calc_signal_strength(c_fires)
    sm = calc_solution_match(c_fires, c_matches)
    rw = calc_relationship_warmth(prof, c_engs)
    total = round((W_ACCOUNT_FIT * af + W_SIGNAL_STRENGTH * ss
                 + W_SOLUTION_MATCH * sm + W_RELATIONSHIP * rw) * 100, 1)

    # Top recommended solutions (most-cited across this client's triggers)
    sol_counter = {}
    for _, m in c_matches.iterrows():
        sols = to_str(m.get('matched_solutions', ''))
        if not sols or sols.startswith('any ') or sols == 'unmatched': continue
        for s in sols.split(';'):
            s = s.strip()
            if s: sol_counter[s] = sol_counter.get(s, 0) + 1
    top_sols = sorted(sol_counter.items(), key=lambda x: -x[1])
    top_sols_str = "; ".join(f"{s} ({c})" for s, c in top_sols[:5])

    leads.append({
        "client_canonical": client,
        "lead_score": total,
        "confidence": confidence_label(total),
        "account_fit": af,
        "signal_strength": ss,
        "solution_match": sm,
        "relationship_warmth": rw,
        # Profile snapshot
        "relationship_type": prof.get('relationship_type'),
        "rank_2019": prof.get('rank_2019'),
        "nwp_2019": prof.get('nwp_2019'),
        "combined_ratio": prof.get('combined_ratio'),
        "exl_client": prof.get('exl_client'),
        "exl_growth_leader": prof.get('exl_growth_leader'),
        "exl_ce": prof.get('exl_ce'),
        # Trigger snapshot
        "num_triggers_fired": len(c_fires),
        "unique_trigger_types": c_fires['trigger_id'].nunique() if not c_fires.empty else 0,
        "sum_trigger_strength": round(c_fires['strength'].sum(), 2) if not c_fires.empty else 0,
        # Solution snapshot
        "recommended_solutions": top_sols_str,
        # Provenance
        "captured_date": INGESTION_DATE,
        "ingestion_date": INGESTION_DATE,
    })

leads_df = pd.DataFrame(leads).sort_values('lead_score', ascending=False).reset_index(drop=True)
leads_df.insert(0, 'rank', leads_df.index + 1)
leads_df.to_csv(f"{DATA}/leads_ranked.csv", index=False)
print(f"Wrote leads_ranked.csv: {len(leads_df)} rows")

# Brief summary
print(f"\nTop 15 leads:")
print(leads_df.head(15)[['rank','client_canonical','lead_score','confidence',
                          'account_fit','signal_strength','solution_match',
                          'relationship_warmth','num_triggers_fired']].to_string(index=False))
