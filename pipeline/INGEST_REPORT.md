# Ingestion Report

Generated: Wed May 27 02:55:36 EDT 2026
Ingestion date: 2026-05-27

## File vintages (used as captured_date for every row)

| Alias | File | Inferred vintage | Source of date |
|---|---|---|---|
| F1 | 20200803 PC-Strategy-Solution Development and GoToMarket PlanVer1.5.xlsx | 2020-08-03 | Filename + Home sheet "Last Updated" |
| F2 | Captive Operations Details Jun 2021 v3 - Copy.xlsx | 2021-06-30 | Filename "Jun 2021" |
| F3 | Competitor Analysis PL and CL.xlsx | 2023-01-01 | **Estimated** - content references post-2022 tools (Skense, Mosaic) |
| F4 | EXL Insurance Competitors.xlsx | 2024-06-01 | **Estimated** - references "CoPilot Research" (post-2023) |
| F5 | P&C Competitor Analysis.xlsx | 2021-02-21 | "2/21" date marker in column R |

**Estimated vintages are best guesses** - flagged in `file_vintage` column on every row. Recommend confirming with file owners.

## Row accounting (every cell of every sheet)

| Status | Rows | Meaning |
|---|---:|---|
| ingested | 1076 | Produced an output row in one of the typed CSVs |
| header | 89 | First N rows of a sheet, intentionally skipped |
| empty | 362 | All cells in the row are None/blank |
| explicitly_skipped | 321 | Sheet flagged as not-ingested with documented reason |
| skipped_non_data | 14 | Row has content but didn't fit the table's data shape (e.g. footer notes) |
| **TOTAL** | **1862** | Should equal sum of max_row across all sheets (1862) |

Reconciliation: see `audit.py` for full per-sheet breakdown.

## Output tables

| Table | Rows | Source |
|---|---:|---|
| clients_top_insurers.csv | 225 | F1 / Top Insurers and Brokers |
| clients_sheet3.csv | 14 | F1 / Sheet3 |
| clients_top_clients_shortlist.csv | 28 | F1 / Top Clients Shortlist |
| engagements_competitor_analysis.csv | 144 | F1 + F5 Competitor Analysis |
| engagements_f4_clientwise.csv | 111 | F4 P&C + L&A Clientwise |
| priorities.csv | 23 | F1 / Buyer Priorities |
| competitor_caps.csv | 46 | F4 / Competitor wise |
| partners_alliances.csv | 63 | F1 / Partnerships and Alliances |
| capability_gaps.csv | 52 | F1 / Capability Gap Assessment -Ver2 |
| insuretech_landscape.csv | 81 | F1 / InsureTech Landscape |
| partnership_landscape.csv | 63 | F1 / Partnership Landscape |
| solutions.csv | 43 | F1 / P&C Solutions List |
| prioritization_framework.csv | 10 | F1 / Client Prioritization Framework |
| insuretech_gap_analysis.csv | 9 | F1 / Insuretch Anlaysis - Roopak |
| build_buy_partner.csv | 121 | F1 / Build-Buy-Partner Analysis |
| captives.csv | 14 | F2 India + PH |
| competitor_profiles.csv | 13 | F3 PL + CL (WNS profile) |

## Sheets ingested

- F1 / Build-Buy-Partner Analysis
- F1 / Buyer Priorities
- F1 / Capability Gap Assessment -Ver2
- F1 / Client Prioritization Framework
- F1 / Competitor Analysis
- F1 / InsureTech Landscape
- F1 / Insuretch Anlaysis - Roopak
- F1 / P&C Solutions List
- F1 / Partnership Landscape
- F1 / Partnerships and Alliances
- F1 / Sheet3
- F1 / Top Clients Shortlist
- F1 / Top Insurers and Brokers
- F2 / Captives in India
- F2 / Captives in the Philippines
- F3 / Commercial
- F3 / Personal Lines
- F4 / Competitor wise
- F4 / L&A Clientwise
- F4 / P&C Clientwise
- F5 / Competitor Analysis

## Sheets explicitly skipped (with reason)

- F1 / Home — Navigation / landing page
- F1 / Go-To-Market Plan — Narrative strategy text in col B; no row-level structured data
- F1 / Dashboard — Multi-table summary view derived from other tables; no source data
- F1 / Capability Gap Assessment  — Superseded by 'Capability Gap Assessment -Ver2' (canonical)
- F1 / Capability Gap Assessment 2 — Superseded by 'Capability Gap Assessment -Ver2' (canonical)
- F1 / Collated Collaterals List — Marketing-collateral URL list; not lead-relevant data
- F1 / Reference Tab - Do not Delete — Lookup ranges; reference data only
- F1 / Consolidated Solutions — Near-duplicate of 'P&C Solutions List' (canonical)
- F1 / White Spaces - Experience — Empty scaffold grid (no data filled in)
- F1 / Solution Evaluation Criteria — Empty stub (only Home link, 1x1)

## Entity normalization

- Unique canonical clients: 236
- Unique canonical competitors: 91
- Client aliases: 142 variants -> 70 canonicals
- Competitor aliases: 62 variants -> 53 canonicals
- Unresolved client names: 207 (mostly small carriers/brokers - see `unresolved.csv`)
- Unresolved competitor names: 1

## Signal-relevant aggregates (for trigger-library design in Task #7)

| Signal | Count |
|---|---:|
| F5 engagements with renewal `< 6 Months` (canonical) | 5 |
| Clients flagged Strategic / Named / Named Backup | 21 |
| Clients with Outsource = Yes | 22 |
| Clients with Combined Ratio > 100 | 5 |
| Priorities with status "Not Initiated" | 13 |

## Data quality flags

- **F5 is canonical for Competitor Analysis**: F1's Competitor Analysis tab duplicates F5's data with sparser Comments/Owner fields. Downstream consumers should use F5.
- **F1 Buyer Priorities is sparse**: only 3 clients (Travelers, Allstate, CNA) have VOC captured despite the sheet having 109 rows.
- **CxO names broken in Buyer Priorities**: rows beyond the first per client show `#N/A` (broken VLOOKUP).
- **Top Insurers col V header/content mismatch**: header reads "InsureTech Partner 1" but content is a year flag like `2021` for many top accounts.
- **Top Clients Shortlist row 26 has date "1905-07-13"**: Excel epoch artifact.
- **Strategic-status inconsistency**: e.g., Travelers is "Named" in Top Insurers and "Named Backup" in Competitor Analysis.
- **F3 + F4 vintages estimated**: no explicit date in those files; verify with file owners.

## Output files in pipeline/data/

CSVs above + `rows_log.csv` (audit log) + `aliases.csv` + `unresolved.csv`.
Run `audit.py` for the row-by-row reconciliation report.
