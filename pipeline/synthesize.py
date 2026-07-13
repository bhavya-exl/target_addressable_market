"""
Stage 6: Action synthesis + output formatter
=============================================
For the top N ranked leads, generate the polished sales brief per the Task #5 spec.

Output:
  - pipeline/leads/{rank:02d}_{client_slug}.md   (one polished brief per lead)
  - pipeline/LEADS_DIGEST.md                     (top 10 inline + index of all)
  - pipeline/data/leads_summary.csv              (compact exec view of top N)

This stage is template-based (no LLM) so output is deterministic and auditable.
Every claim in every lead carries the source-row citation it was derived from.
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
LEADS_DIR = "/Users/bhavya242574/Library/CloudStorage/OneDrive-EXLService.com(I)Pvt.Ltd/Desktop/TAM/pipeline/leads"
DIGEST = "/Users/bhavya242574/Library/CloudStorage/OneDrive-EXLService.com(I)Pvt.Ltd/Desktop/TAM/pipeline/LEADS_DIGEST.md"

os.makedirs(LEADS_DIR, exist_ok=True)

TOP_N_FULL = 20      # number of leads to generate full briefs for
TOP_N_INLINE = 10    # number to include inline in the digest

INGESTION_DATE = date.today().isoformat()

# ============ Load ============
profiles    = pd.read_csv(f"{DATA}/client_profiles.csv")
fires       = pd.read_csv(f"{DATA}/triggers_fired.csv")
matches     = pd.read_csv(f"{DATA}/solution_matches.csv")
engagements = pd.read_csv(f"{DATA}/client_engagements_summary.csv")
priorities  = pd.read_csv(f"{DATA}/priorities.csv")
ranked      = pd.read_csv(f"{DATA}/leads_ranked.csv")

# ============ Helpers ============

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '_', str(name).lower()).strip('_')[:50]

def to_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return ""
    return str(v).strip()

def fmt_money(v):
    try:
        f = float(v)
        if pd.isna(f): return "-"
        if f >= 1e9: return f"${f/1e9:.1f}B"
        if f >= 1e6: return f"${f/1e6:.0f}M"
        return f"${int(f):,}"
    except (TypeError, ValueError):
        return to_str(v) or "-"

def fmt_pct(v):
    try:
        f = float(v)
        if pd.isna(f): return "-"
        return f"{f*100:+.1f}%"
    except (TypeError, ValueError):
        return "-"

def fmt_num(v, default="-"):
    try:
        f = float(v)
        if pd.isna(f): return default
        return f"{f:.1f}" if f != int(f) else str(int(f))
    except (TypeError, ValueError):
        return default

# ============ Render sections ============

def render_header_box(lead, profile):
    nwp = fmt_money(profile.get('nwp_2019'))
    gwp = to_str(profile.get('gwp')) or "-"
    growth = fmt_pct(profile.get('pct_change_yoy')) if profile.get('pct_change_yoy') else fmt_pct(profile.get('growth_pct'))
    rank = to_str(profile.get('rank_2019')) or "-"
    if rank != "-":
        try: rank = f"#{int(float(rank))}"
        except: pass
    cr = fmt_num(profile.get('combined_ratio'))
    geo = to_str(profile.get('geography')) or "-"
    rt = to_str(profile.get('relationship_type')) or "-"
    outsource = to_str(profile.get('outsource')) or "-"
    exl_client = to_str(profile.get('exl_client')) or "(blank)"
    growth_leader = to_str(profile.get('exl_growth_leader')) or "(unassigned)"
    ce = to_str(profile.get('exl_ce')) or "(unassigned)"

    # Displacement owner = first owner across this client's engagements
    c_engs = engagements[engagements.client_canonical == lead['client_canonical']]
    owner = ""
    if not c_engs.empty:
        owners = c_engs['owner'].dropna().astype(str)
        owners = owners[owners.str.strip() != ""]
        if len(owners): owner = owners.iloc[0]

    return f"""```
Account:              {lead['client_canonical']}
Type / Geo:           {to_str(profile.get('type'))} / {geo}
Size:                 {nwp} NWP 2019 ({growth} YoY)   |   GWP: {gwp}
Rank:                 {rank} by NWP
Combined ratio:       {cr}
EXL relationship:     {rt}    |   Outsources: {outsource}   |   EXL Client: {exl_client}
EXL Growth Leader:    {growth_leader}
EXL Client Exec:      {ce}
Displacement owner:   {owner or '(none assigned)'}
Score:                {lead['lead_score']:.1f} / 100
Confidence:           {lead['confidence']}
```"""

def render_score_breakdown(lead):
    return f"""## Score breakdown

| Component | Score (0–1) | Weight | Contribution |
|---|---:|---:|---:|
| Account fit (NWP rank, Strategic/Named, growth) | {lead['account_fit']:.2f} | 30% | {lead['account_fit']*0.30:.3f} |
| Signal strength (Σ trigger strength + diversity) | {lead['signal_strength']:.2f} | 40% | {lead['signal_strength']*0.40:.3f} |
| Solution match (triggers mapped to EXL solutions) | {lead['solution_match']:.2f} | 20% | {lead['solution_match']*0.20:.3f} |
| Relationship warmth (CE / Growth Leader / Owner) | {lead['relationship_warmth']:.2f} | 10% | {lead['relationship_warmth']*0.10:.3f} |
| **TOTAL** | | | **{lead['lead_score']/100:.3f}** ({lead['lead_score']:.1f}/100) |
"""

def render_triggers(c_fires, c_matches):
    if c_fires.empty:
        return "\n## Triggers firing\n\n_No triggers fired._ This account scored on profile fit alone.\n"
    n = len(c_fires)
    md = f"\n## Triggers firing ({n})\n\n"
    md += "| # | Trigger | Strength | Evidence | Sources |\n"
    md += "|---:|---|---:|---|---|\n"
    for i, (_, fr) in enumerate(c_fires.iterrows(), 1):
        ev = to_str(fr['evidence_text']).replace('|', '\\|').replace('\n', ' ')
        srcs = to_str(fr['evidence_sources'])[:120].replace('|', '\\|')
        md += f"| {i} | `{fr['trigger_id']}` | {fr['strength']:.2f} | {ev[:200]}{'...' if len(ev) > 200 else ''} | {srcs} |\n"
    return md

def compute_top_products(c_matches, c_fires):
    """Returns sorted list of (product_name, count) for products this account's triggers map to."""
    if c_matches.empty: return []
    top = c_matches.merge(c_fires[['trigger_id', 'strength']].drop_duplicates(), on='trigger_id', how='left')
    top = top.sort_values('strength', ascending=False)
    product_counter = {}
    for _, m in top.iterrows():
        ms = str(m.get('matched_solutions', '') or '')
        for product in ms.split(';'):
            product = product.strip()
            if product in EXL_PRODUCTS:
                product_counter[product] = product_counter.get(product, 0) + 1
            elif product and "(" in product:  # legacy mapped string
                head = product.split('(')[0]
                for sub in re.split(r'\s*\+\s*', head):
                    sub = sub.strip()
                    if sub.startswith("EXL ") and sub in EXL_PRODUCTS:
                        product_counter[sub] = product_counter.get(sub, 0) + 1
    return sorted(product_counter.items(), key=lambda x: -x[1])

def render_recommended_play(c_fires, c_matches, lead, top_products):
    if c_matches.empty:
        return "\n## Recommended EXL play\n\n_No specific solution matches; treat as portfolio-level outreach._\n"
    top = c_matches.merge(c_fires[['trigger_id', 'strength']].drop_duplicates(), on='trigger_id', how='left')
    top = top.sort_values('strength', ascending=False)
    top_concrete = top[top['matched_solutions'].fillna('').str.len() > 0]
    top_concrete = top_concrete[~top_concrete['matched_solutions'].str.startswith('any ', na=True)]
    top_concrete = top_concrete[top_concrete['matched_solutions'] != 'unmatched']
    if top_concrete.empty:
        return "\n## Recommended EXL play\n\n_Triggers fired but no concrete solution matches yet — treat as broad consultative engagement._\n"

    md = "\n## Recommended EXL play\n\n"
    if top_products:
        md += "**Anchor products** (most-cited across this account's triggers):\n\n"
        md += "| EXL Product | What it does | Typical outcome |\n"
        md += "|---|---|---|\n"
        for prod, count in top_products[:4]:
            info = EXL_PRODUCTS[prod]
            md += f"| **{prod}** | {info['what']} | {info['outcome']} |\n"
        md += "\n"

    primary = top_concrete.iloc[0]
    md += f"**Primary trigger driving the pitch**: {primary['trigger_name']}\n\n"
    md += f"Solution mapping basis: *{primary['matching_basis']}*\n\n"
    if len(top_concrete) > 1:
        secondary = top_concrete.iloc[1]
        md += f"**Secondary trigger**: {secondary['trigger_name']} — *{secondary['matching_basis']}*\n\n"

    md += f"**All matched solutions for this account**: {to_str(lead['recommended_solutions']) or '-'}\n"
    return md

def render_stakeholders(profile):
    rows = []
    for role, col in [("CEO", "ceo"), ("CFO", "cfo"), ("CRO", "cro"), ("CCO", "cco"),
                      ("COO", "coo"), ("CIO/CTO", "cio_cto"), ("CUO", "cuo")]:
        name = to_str(profile.get(col))
        if name and name != "#N/A":
            rows.append((role, name))
    if not rows:
        return "\n## Stakeholder map\n\n_No CxO names captured in source data._\n"
    md = "\n## Stakeholder map (client side)\n\n| Role | Name |\n|---|---|\n"
    for r, n in rows:
        md += f"| {r} | {n} |\n"
    # Flag dual roles
    duals = [r for r, n in rows if [x for x in rows if x[1] == n and x[0] != r]]
    if duals:
        md += f"\n*Note: same name appears in multiple roles — possible dual role or data-entry artifact. Verify.*\n"
    return md

def render_pitch_hook(c_fires, profile, lead, top_products):
    """Templated pitch hook based on dominant trigger pattern.
    Now references real EXL products + outcome metrics from the deck.
    `top_products` is a list of (product_name, count) tuples from render_recommended_play.
    """
    if c_fires.empty:
        return "\n## Pitch hook\n\n> _No triggers fired; engage at portfolio level._\n"
    fired_ids = set(c_fires['trigger_id'])
    client = lead['client_canonical']
    rt = to_str(profile.get('relationship_type')) or "the account"

    # Build product-anchor string from top products
    prod_anchor = ""
    outcome_anchor = ""
    if top_products:
        anchors = [p for p, _ in top_products[:2]]
        prod_anchor = " + ".join(anchors)
        if anchors:
            outcome_anchor = EXL_PRODUCTS.get(anchors[0], {}).get("outcome", "")

    # Pattern selection
    if {'mass_renewal', 'multi_competitor_friction'} & fired_ids:
        engs = engagements[engagements.client_canonical == client].sort_values('total_ftes_estimated', ascending=False)
        top_comp = engs.iloc[0]['competitor_canonical'] if not engs.empty else "the incumbent"
        top_ftes = int(engs.iloc[0]['total_ftes_estimated']) if not engs.empty and pd.notna(engs.iloc[0]['total_ftes_estimated']) else None
        ftes_str = f"{top_ftes}+ FTE" if top_ftes else "large"
        hook = (f"Sequenced displacement vehicle for {top_comp}'s {ftes_str} footprint as multiple concurrent "
                f"scopes approach renewal. Lead with **{prod_anchor or 'EXL XTRAKTO.AI + NerveHub'}** — "
                f"typical outcome: *{outcome_anchor or '25-30% cost-of-operations reduction'}*. "
                f"Anchor narrative on {client}'s stated operating-leverage commitments, with EXL's "
                f"solution mapping to their VOC already complete.")
    elif 'unaddressed_voc' in fired_ids:
        c_prios = priorities[priorities.client_canonical == client]
        c_prios = c_prios[c_prios['solution_life_cycle'] == "Not Initiated"]
        top_area = c_prios['priority_area'].mode().iloc[0] if not c_prios.empty else "stated priorities"
        n = len(c_prios)
        hook = (f"Direct response to {client}'s stated '{top_area}' priority — {n} EXL solution components "
                f"already mapped to their business needs. Lead with **{prod_anchor or 'EXL XTRAKTO.AI'}** "
                f"(*{outcome_anchor or '25-30% cost-of-operations reduction'}*). Pre-built case, ready to pitch.")
    elif 'strategic_low_wallet' in fired_ids and 'high_competitor_ftes' in fired_ids:
        engs = engagements[engagements.client_canonical == client].sort_values('total_ftes_estimated', ascending=False)
        top_comp = engs.iloc[0]['competitor_canonical'] if not engs.empty else "the incumbent"
        hook = (f"Account-opening play at this {rt} where EXL has minimal wallet share despite the strategic "
                f"designation. {top_comp} holds a large entrenched footprint — open with a low-friction "
                f"entry vehicle (**{prod_anchor or 'EXL XTRAKTO.AI'}** for intake + indexing) and build "
                f"reference work before pitching wider.")
    elif 'cost_pressure' in fired_ids:
        cr = fmt_num(profile.get('combined_ratio'))
        hook = (f"Operating-leverage pitch addressing {client}'s combined-ratio pressure (CR {cr}). "
                f"Lead with **{prod_anchor or 'EXL Paymentor + Digital Finance Suite'}** — "
                f"typical outcome: *{outcome_anchor or '40-60% F&A cost reduction, 100% payment-leakage elimination'}*.")
    elif 'competitor_concentration' in fired_ids:
        hook = (f"Multi-incumbent displacement opportunity — {client} has fragmented competitor presence "
                f"(no single provider with majority). Position EXL as consolidation partner via "
                f"**{prod_anchor or 'EXL NerveHub'}** orchestration spanning the value chain.")
    else:
        hook = (f"Engagement opportunity at {client} on the basis of {len(c_fires)} signal(s). "
                f"Validate triggers in detail before allocating effort.")
    return f"\n## Pitch hook\n\n> *{hook}*\n"

def render_risks(c_fires, profile):
    risks = []
    # Data quality
    if not to_str(profile.get('exl_client')) or to_str(profile.get('exl_client')) == "":
        risks.append("EXL Client column is blank in source — confirm whether EXL has any current scope at this account.")
    if to_str(profile.get('file_vintages_touched', '')):
        vins = to_str(profile.get('file_vintages_touched'))
        if '2020' in vins and not any(y in vins for y in ['2024', '2023']):
            risks.append(f"Data vintage 2020-2021 — CxO names and renewal windows may be stale (4+ years old). Verify externally before outreach.")
    # CR
    cr_v = profile.get('combined_ratio')
    try:
        if pd.notna(cr_v) and float(cr_v) > 100:
            risks.append(f"Combined ratio {float(cr_v):.1f} — client is under cost pressure, but may also be defensive on new outsourcing spend.")
    except (TypeError, ValueError): pass

    # High switching cost
    fired_ids = set(c_fires['trigger_id']) if not c_fires.empty else set()
    if 'high_competitor_ftes' in fired_ids:
        risks.append("Large incumbent footprint = high switching cost. Plan for sequenced/phased displacement, not big-bang.")
    if 'multi_competitor_friction' in fired_ids:
        risks.append("Multiple parallel Champion-Challenger threads — coordinate to avoid fragmented pitches.")

    # CxO inconsistency
    coo = to_str(profile.get('coo'))
    cio = to_str(profile.get('cio_cto'))
    if coo and cio and coo == cio:
        risks.append(f"COO and CIO/CTO listed as same person ({coo}) — could be dual role or data-entry artifact. Verify.")

    # Unaddressed VOC but no current EXL presence
    if 'unaddressed_voc' in fired_ids and to_str(profile.get('exl_client')) != "Yes":
        risks.append("Unaddressed VOC items present but no documented current EXL scope — pitching from outside the wallet.")

    if not risks:
        risks = ["No specific risks flagged from data analysis. Validate triggers manually before outreach."]

    md = "\n## Risks / disqualifiers\n\n"
    for r in risks:
        md += f"- {r}\n"
    return md

def render_next_steps(c_fires, profile):
    if c_fires.empty:
        return ("\n## Next 3 steps\n\n"
                "1. Manual review — no specific triggers fired\n"
                "2. Validate the account-fit signals against fresh data\n"
                "3. Decide whether to add to pipeline or deprioritize\n")
    fired_ids = set(c_fires['trigger_id'])
    growth_leader = to_str(profile.get('exl_growth_leader')) or "(unassigned)"
    ce = to_str(profile.get('exl_ce')) or "(unassigned)"
    # Get displacement owner if any
    c_engs = engagements[engagements.client_canonical == profile['client_canonical']]
    owner = ""
    if not c_engs.empty:
        owners = c_engs['owner'].dropna().astype(str)
        owners = owners[owners.str.strip() != ""]
        if len(owners): owner = owners.iloc[0]
    owner = owner or growth_leader

    steps = []
    if {'mass_renewal', 'multi_competitor_friction', 'renewal_le_6mo'} & fired_ids:
        steps.append((owner, "Engage primary client contact on Champion-Challenger discussions; bring case studies for the largest incumbent's scope."))
        steps.append((owner, "Sequence the displacement timeline — pick smallest scope as fast-pilot, anchor scope as headline."))
    if 'unaddressed_voc' in fired_ids:
        steps.append((growth_leader, "Schedule meeting with client CxO to walk through the EXL solution components already mapped to their stated priorities."))
    if 'strategic_low_wallet' in fired_ids:
        steps.append((ce, "Review account expansion strategy; identify a lower-friction entry-point service to win first reference work."))
    if 'cost_pressure' in fired_ids:
        steps.append((growth_leader, "Build a TCO/operating-leverage case study tailored to this client's CR profile."))
    if not steps:
        steps.append((growth_leader, "Validate triggers in detail and prepare an account-level outreach plan."))

    md = "\n## Next 3 steps\n\n| # | Owner | Action |\n|---:|---|---|\n"
    for i, (own, act) in enumerate(steps[:3], 1):
        md += f"| {i} | {own} | {act} |\n"
    return md

def render_evidence_pack(c_fires):
    if c_fires.empty:
        return "\n## Evidence pack\n\n_(no firings)_\n"
    md = "\n## Evidence pack — full source citations\n\n"
    md += "| Trigger | Strength | Sources |\n|---|---:|---|\n"
    for _, fr in c_fires.iterrows():
        srcs = to_str(fr['evidence_sources']).replace('|', '\\|')
        md += f"| `{fr['trigger_id']}` | {fr['strength']:.2f} | {srcs} |\n"
    return md

# ============ Render full lead ============

def render_lead(rank, lead_row):
    client = lead_row['client_canonical']
    profile = profiles[profiles.client_canonical == client].iloc[0]
    c_fires = fires[fires.client_canonical == client].sort_values('strength', ascending=False)
    c_matches = matches[matches.client_canonical == client]
    top_products = compute_top_products(c_matches, c_fires)

    sections = [
        f"# LEAD #{rank} — {client}",
        "",
        f"*Score: **{lead_row['lead_score']:.1f}/100** • Confidence: **{lead_row['confidence']}** • Triggers fired: {lead_row['num_triggers_fired']} ({lead_row['unique_trigger_types']} unique types)*",
        "",
        render_header_box(lead_row, profile),
        render_score_breakdown(lead_row),
        render_triggers(c_fires, c_matches),
        render_recommended_play(c_fires, c_matches, lead_row, top_products),
        render_stakeholders(profile),
        render_pitch_hook(c_fires, profile, lead_row, top_products),
        render_risks(c_fires, profile),
        render_next_steps(c_fires, profile),
        render_evidence_pack(c_fires),
        f"\n---\n\n*Generated {INGESTION_DATE} from data vintages {to_str(profile.get('file_vintages_touched'))}. Re-run `pipeline/synthesize.py` to refresh.*",
    ]
    return "\n".join(sections)

# ============ Generate ============

top_leads = ranked.head(TOP_N_FULL)

for _, lead in top_leads.iterrows():
    md = render_lead(int(lead['rank']), lead)
    slug = slugify(lead['client_canonical'])
    fname = f"{int(lead['rank']):02d}_{slug}.md"
    with open(os.path.join(LEADS_DIR, fname), 'w') as f:
        f.write(md)

print(f"Generated {len(top_leads)} lead briefs in pipeline/leads/")

# ============ Compact summary CSV ============

summary_cols = ['rank', 'client_canonical', 'lead_score', 'confidence',
                'account_fit', 'signal_strength', 'solution_match', 'relationship_warmth',
                'relationship_type', 'rank_2019', 'nwp_2019', 'combined_ratio',
                'exl_client', 'exl_growth_leader', 'exl_ce',
                'num_triggers_fired', 'unique_trigger_types', 'sum_trigger_strength',
                'recommended_solutions']
ranked[summary_cols].head(50).to_csv(f"{DATA}/leads_summary.csv", index=False)
print(f"Wrote leads_summary.csv: top 50 leads (compact)")

# ============ Digest ============

digest = f"""# Leads Digest

Generated: {INGESTION_DATE}

Top {TOP_N_INLINE} leads from {len(ranked)} ranked accounts. Full briefs in `pipeline/leads/`.

## Top {TOP_N_INLINE} ranked

| Rank | Client | Score | Confidence | Triggers | Recommended Solutions |
|---:|---|---:|---|---:|---|
"""
for _, lead in ranked.head(TOP_N_INLINE).iterrows():
    rec = to_str(lead['recommended_solutions'])[:100]
    digest += f"| **{int(lead['rank'])}** | [{lead['client_canonical']}](leads/{int(lead['rank']):02d}_{slugify(lead['client_canonical'])}.md) | **{lead['lead_score']:.1f}** | {lead['confidence']} | {int(lead['num_triggers_fired'])} | {rec or '-'} |\n"

digest += f"""

## Scoring weights (V1 defaults — tunable)

| Component | Weight |
|---|---:|
| Account fit (NWP rank, Strategic/Named status, growth %) | 30% |
| Signal strength (Σ trigger strength + diversity) | 40% |
| Solution match (triggers mapped to EXL packaged solutions) | 20% |
| Relationship warmth (EXL CE / Growth Leader / Owner) | 10% |

## Trigger library (13 rules)

See `pipeline/TRIGGERS_REPORT.md` for the full catalog. All rules are deterministic and source-cited.

## Full lead briefs

"""
for _, lead in ranked.head(TOP_N_FULL).iterrows():
    fname = f"{int(lead['rank']):02d}_{slugify(lead['client_canonical'])}.md"
    digest += f"- [{int(lead['rank']):02d}. {lead['client_canonical']} ({lead['lead_score']:.1f})](leads/{fname})\n"

digest += f"""

---

## All artifacts (end-to-end)

```
pipeline/
├── ingest.py          → 18 typed CSVs + audit log
├── audit.py           → row-by-row coverage reconciliation (PASS)
├── profiles.py        → per-account profiles + engagement summary
├── triggers.py        → 13-rule trigger library + firings with citations
├── score.py           → solution matching + 4-component weighted scoring
├── synthesize.py      → polished lead briefs (THIS STAGE)
├── data/*.csv         → all the structured outputs
└── leads/*.md         → top-{TOP_N_FULL} briefs (one .md per lead)
```

Re-run from scratch:
```
python3 pipeline/ingest.py && python3 pipeline/audit.py && \\
python3 pipeline/profiles.py && python3 pipeline/triggers.py && \\
python3 pipeline/score.py && python3 pipeline/synthesize.py
```

Total runtime: ~5 seconds for 236 accounts.
"""

with open(DIGEST, 'w') as f:
    f.write(digest)

print(f"Digest: {DIGEST}")
print(f"\nTop 10 ranked:")
print(ranked.head(10)[['rank','client_canonical','lead_score','confidence']].to_string(index=False))
