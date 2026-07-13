# Triggers Report

Generated: Wed May 27 02:55:41 EDT 2026
Evaluation date: 2026-05-27

## Trigger library

13 deterministic rules. Each fire is sourced to specific cells. No LLM in this stage.

| # | ID | Name | Weight |
|---:|---|---|---:|
| 1 | `renewal_le_6mo` | Incumbent renewal within 6 months | 1.00 |
| 2 | `renewal_le_12mo` | Incumbent renewal within 12 months | 0.70 |
| 3 | `mass_renewal` | Multiple incumbent scopes renewing together | 1.00 |
| 4 | `active_friction` | Active competitor friction (free-text signal) | 0.90 |
| 5 | `unaddressed_voc` | Mapped VOC priority not yet initiated | 0.60 |
| 6 | `cost_pressure` | Combined ratio > 100 (cost-pressure) | 0.50 |
| 7 | `strategic_low_wallet` | Strategic/Named with low EXL wallet share | 0.60 |
| 8 | `greenfield_outsourcer` | Greenfield prospect (Mutual/Private not outsourcing) | 0.40 |
| 9 | `high_competitor_ftes` | Single competitor with ≥200 FTEs at named account | 0.70 |
| 10 | `multi_competitor_friction` | Multiple competitors at one client all in friction | 1.00 |
| 11 | `competitor_concentration` | Large competitor footprint at one client (≥500 FTEs) | 0.60 |
| 12 | `named_backup` | Named-Backup status at top-25 account | 0.50 |
| 13 | `captive_rationalization` | Captive operations re-evaluating WFH/onshore | 0.50 |
| 14 | `function_headroom` | Competitor parked in function with high EXL retention headroom | 0.85 |


## Total firings: 60

## Firings by trigger type

| Trigger | Firings |
|---|---:|
| `strategic_low_wallet` (Strategic/Named with low EXL wallet share) | 19 |
| `high_competitor_ftes` (Single competitor with ≥200 FTEs at named account) | 12 |
| `cost_pressure` (Combined ratio > 100 (cost-pressure)) | 7 |
| `function_headroom` (Competitor parked in function with high EXL retention headroom) | 7 |
| `unaddressed_voc` (Mapped VOC priority not yet initiated) | 5 |
| `competitor_concentration` (Large competitor footprint at one client (≥500 FTEs)) | 4 |
| `active_friction` (Active competitor friction (free-text signal)) | 3 |
| `mass_renewal` (Multiple incumbent scopes renewing together) | 1 |
| `multi_competitor_friction` (Multiple competitors at one client all in friction) | 1 |
| `renewal_le_6mo` (Incumbent renewal within 6 months) | 1 |


## Top 25 clients by aggregate trigger strength

This is the proto-lead ranking. Stage 5 (scoring) will combine this with account-fit + solution-match weights.

| Rank | Client | Triggers Fired | Unique Trigger Types | Σ Strength |
|---:|---|---:|---:|---:|
| 1 | Travelers Group | 17 | 9 | 12.76 |
| 2 | Allstate | 5 | 2 | 3.40 |
| 3 | Nationwide | 3 | 3 | 2.03 |
| 4 | AON | 3 | 3 | 2.03 |
| 5 | Swiss Re | 3 | 3 | 1.93 |
| 6 | Liberty Mutual | 3 | 3 | 1.93 |
| 7 | Hanover Insurance Group | 2 | 2 | 1.30 |
| 8 | Hartford | 2 | 2 | 1.30 |
| 9 | Munich-Amer Hldg Corp Cos | 2 | 2 | 1.10 |
| 10 | American Family | 2 | 2 | 1.10 |
| 11 | Axis | 2 | 2 | 1.10 |
| 12 | Genworth | 1 | 1 | 0.73 |
| 13 | Great Amer P&C Ins Group | 1 | 1 | 0.60 |
| 14 | Aviva | 1 | 1 | 0.60 |
| 15 | Suncorp | 1 | 1 | 0.60 |
| 16 | State Farm | 1 | 1 | 0.60 |
| 17 | QBE | 1 | 1 | 0.60 |
| 18 | Munich Re | 1 | 1 | 0.60 |
| 19 | Marsh | 1 | 1 | 0.60 |
| 20 | MAPFRE | 1 | 1 | 0.60 |
| 21 | Esure Insurance Holdings | 1 | 1 | 0.60 |
| 22 | American Modern | 1 | 1 | 0.60 |
| 23 | Farmers | 1 | 1 | 0.60 |
| 24 | Great American | 1 | 1 | 0.60 |
| 25 | IAG | 1 | 1 | 0.60 |


## Sample: all triggers fired for **Travelers Group** (rank #1)

| Trigger | Strength | Evidence | Sources |
|---|---:|---|---|
| `renewal_le_6mo` | 1.00 | Cognizant contract renews in < 6 months (~1000 FTEs across 5 scope(s), functions: CLAIMS, UW, F&A) | F5/Competitor Analysis/R8; F5/Competitor Analysis/R9; F5/Competitor Analysis/R10 |
| `mass_renewal` | 1.00 | Single-vendor displacement window: Cognizant holds 5 concurrent scopes (~1000 FTEs) all renewing in < 6 Months | F5/Competitor Analysis/R8; F5/Competitor Analysis/R9; F5/Competitor Analysis/R10 |
| `multi_competitor_friction` | 1.00 | 3 concurrent incumbents in friction: Cognizant(champion challenger); Genpact(champion challenger,terminating); WNS(champion challenger,given notice,exploring champion) | F5/Competitor Analysis/R8; F5/Competitor Analysis/R9; F5/Competitor Analysis/R10 |
| `active_friction` | 0.90 | Cognizant: friction signals in account notes — champion challenger. Comments: Personal Insurance, Commercial Insurnace - From new business to claims settlement; Bill Review and Utilization Review; Pol... | F5/Competitor Analysis/R8; F5/Competitor Analysis/R9; F5/Competitor Analysis/R10 |
| `active_friction` | 0.90 | Genpact: friction signals in account notes — champion challenger,terminating. Comments: Policy Maintenance; Claims; Invoicing | F5/Competitor Analysis/R39; F5/Competitor Analysis/R40; F5/Competitor Analysis/R |
| `active_friction` | 0.90 | WNS: friction signals in account notes — champion challenger,given notice,exploring champion. Comments:  | F5/Competitor Analysis/R65 |
| `function_headroom` | 0.73 | Cognizant parked at 'Policy Servicing' (1000 FTEs documented). EXL typical retention for this function is only 35% (high headroom, implying ~2857 FTE TAM at this function). | F5/Competitor Analysis/R8; F5/Competitor Analysis/R9; F5/Competitor Analysis/R10 |
| `function_headroom` | 0.73 | Genpact parked at 'Policy Servicing' (210 FTEs documented). EXL typical retention for this function is only 35% (high headroom, implying ~600 FTE TAM at this function). | F5/Competitor Analysis/R39; F5/Competitor Analysis/R40; F5/Competitor Analysis/R |
| `high_competitor_ftes` | 0.70 | Cognizant has ~1000 FTEs at this Named account — large displacement target | F5/Competitor Analysis/R8; F5/Competitor Analysis/R9; F5/Competitor Analysis/R10 |
| `high_competitor_ftes` | 0.70 | Genpact has ~210 FTEs at this Named account — large displacement target | F5/Competitor Analysis/R39; F5/Competitor Analysis/R40; F5/Competitor Analysis/R |
| `unaddressed_voc` | 0.60 | VOC priority 'Optimizing Operating Leverage' has 2 mapped component(s) for EXL Int_Col solution — status 'Not Initiated' | F1/Buyer Priorities/R19; F1/Buyer Priorities/R20 |
| `unaddressed_voc` | 0.60 | VOC priority 'Strong Top Line Performance' has 3 mapped component(s) for EXL NB_PaaS solution — status 'Not Initiated' | F1/Buyer Priorities/R11; F1/Buyer Priorities/R12; F1/Buyer Priorities/R13 |
| `strategic_low_wallet` | 0.60 | Named account but EXL share-of-wallet = '(blank)' / EXL Client = '(blank)' | client_profile (F1/Top Insurers and Brokers) |
| `unaddressed_voc` | 0.60 | VOC priority 'Optimizing Operating Leverage' has 4 mapped component(s) for EXL FNOL solution — status 'Not Initiated' | F1/Buyer Priorities/R9; F1/Buyer Priorities/R15; F1/Buyer Priorities/R16; F1/Buy |
| `competitor_concentration` | 0.60 | Aggregate competitor footprint at this account ~1210 FTEs (3 competitors, 9 engagements) | client_engagements_summary (derived from F4 + F5) |
| `unaddressed_voc` | 0.60 | VOC priority 'Optimizing Operating Leverage' has 1 mapped component(s) for EXL E_E2E solution — status 'Not Initiated' | F1/Buyer Priorities/R14 |
| `unaddressed_voc` | 0.60 | VOC priority 'Strong Top Line Performance' has 1 mapped component(s) for EXL FNOL solution — status 'Not Initiated' | F1/Buyer Priorities/R17 |


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
