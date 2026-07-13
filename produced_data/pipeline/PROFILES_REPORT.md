# Profiles Report

Generated: Wed May 27 02:55:40 EDT 2026
Ingestion date: 2026-05-27

## Outputs

| File | Rows | Description |
|---|---:|---|
| `client_profiles.csv` | 236 | One row per canonical client with identity + EXL relationship + CxOs + competitor & priority aggregates |
| `client_engagements_summary.csv` | 73 | One row per (client, competitor) pair with aggregated FTEs / functions / renewals / comments / friction signals |

## Coverage

- **Unique canonical clients in profiles**: 236
- **Strategic/Named/Named Backup clients**: 33
- **Clients with mapped VOC priorities**: 3
- **Unique (client, competitor) engagement pairs**: 73

## Top 20 accounts by estimated competitor FTE footprint

| Client | Type | NWP 2019 | Rank | CR | Rel | EXL Client | Total Competitor FTEs (est) | # Competitors |
|---|---|---:|---:|---:|---|---|---:|---:|
| Allstate | Carrier | $34,038,467,000 | 4 | 85.0 | Strategic | Yes | 5900 | 8 |
| Travelers Group | Carrier | $27,214,083,000 | 6 | 96.5 | Named | nan | 1210 | 3 |
| Hanover Insurance Group | Carrier | $4,580,867,000 | 25 | 95.6 | Strategic | Yes | 924 | 12 |
| Hartford | Carrier | $11,871,251,000 | 12 | 94.0 | Strategic | Yes | 840 | 2 |
| AON |  | - | - | - | Named |  | 490 | 1 |
| Liberty Mutual | Carrier | $32,268,379,000 | 5 | 101.7 | Named | Yes | 455 | 4 |
| Swiss Re | Carrier | $2,023,929,000 | 15 | 107.0 | Named | Yes | 350 | 1 |
| Genworth | Carrier | $818,540,000 | 97 | - |  | nan | 300 | 1 |
| Nationwide | Carrier | $17,992,806,000 | 9 | 94.0 | Named | nan | 200 | 4 |
| Zurich | Carrier | $3,657,532,000 | 29 | 96.4 | Strategic | Yes | 170 | 4 |
| MAPFRE | Carrier | $1,863,845,000 | 51 | 97.6 | Named | nan | 150 | 5 |
| Kemper | Carrier | $4,042,228,000 | 30 | 93.0 | Named | Yes | 80 | 2 |


## Dedup proof

- Raw engagements (F1 + F5 Competitor Analysis combined): 144
- After dedup (F5 canonical only): 72
- Dropped (F1 duplicates): 72

## Notes

- FTE counts are best-effort extracted from messy free-text ('~1000 - 1300', '$10M-$15M (~500 FTEs)', etc.) - take with confidence-band caution.
- Where the same competitor has multiple engagements at one client (e.g., Cognizant at Travelers = 5 separate scopes), totals are summed.
- `friction_signals` column flags free-text mentions of 'Champion Challenger', 'given notice', etc. - used by Trigger #8 in the next stage.
- Clients with VOC priorities (3) = the only ones with `num_priorities_not_initiated > 0` will fire Trigger #4 (unaddressed VOC).
