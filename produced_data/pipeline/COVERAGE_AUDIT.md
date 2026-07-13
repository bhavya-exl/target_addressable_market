# Coverage Audit

Reconciles every row of every sheet of every Excel file against ingestion log.

## Verdict

**PASS ✓**

| Check | Result |
|---|---|
| Sheets with mismatched row counts | 0 |
| Output CSV rows missing from ingestion log | 0 |
| Ingested-flagged rows missing from any output CSV | 0 |

## Totals

| Metric | Count |
|---|---:|
| Total rows across all sheets (sum of max_row) | 1862 |
| Total rows logged in rows_log.csv | 1862 |
| Total rows ingested into output tables | 1076 |
| Header rows (intentionally skipped) | 89 |
| Empty rows | 362 |
| Explicitly-skipped rows (sheet-level skip with reason) | 321 |
| Skipped non-data rows (content present but not data shape) | 14 |
| Sum (ingested + header + empty + explicit_skip + non_data) | 1862 |

Reconciliation: `max_row` total should equal `logged` total AND the sum of all categories.

## Per-sheet breakdown

| File | Sheet | max_row | logged | ingested | header | empty | explicit_skip | non_data | Reconciled? |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| F1 | Build-Buy-Partner Analysis | 138 | 138 | 121 | 13 | 3 | 0 | 1 | ✓ |
| F1 | Buyer Priorities | 109 | 109 | 39 | 6 | 64 | 0 | 0 | ✓ |
| F1 | Capability Gap Assessment  | 72 | 72 | 0 | 0 | 13 | 59 | 0 | ✓ |
| F1 | Capability Gap Assessment -Ver2 | 67 | 67 | 52 | 2 | 11 | 0 | 2 | ✓ |
| F1 | Capability Gap Assessment 2 | 67 | 67 | 0 | 0 | 11 | 56 | 0 | ✓ |
| F1 | Client Prioritization Framework | 22 | 22 | 10 | 1 | 2 | 0 | 9 | ✓ |
| F1 | Collated Collaterals List | 47 | 47 | 0 | 0 | 2 | 45 | 0 | ✓ |
| F1 | Competitor Analysis | 76 | 76 | 72 | 4 | 0 | 0 | 0 | ✓ |
| F1 | Consolidated Solutions | 58 | 58 | 0 | 0 | 13 | 45 | 0 | ✓ |
| F1 | Dashboard | 140 | 140 | 0 | 0 | 136 | 4 | 0 | ✓ |
| F1 | Go-To-Market Plan | 75 | 75 | 0 | 0 | 23 | 52 | 0 | ✓ |
| F1 | Home | 24 | 24 | 0 | 0 | 22 | 2 | 0 | ✓ |
| F1 | InsureTech Landscape | 88 | 88 | 81 | 7 | 0 | 0 | 0 | ✓ |
| F1 | Insuretch Anlaysis - Roopak | 14 | 14 | 9 | 5 | 0 | 0 | 0 | ✓ |
| F1 | P&C Solutions List | 65 | 65 | 43 | 9 | 13 | 0 | 0 | ✓ |
| F1 | Partnership Landscape | 70 | 70 | 63 | 7 | 0 | 0 | 0 | ✓ |
| F1 | Partnerships and Alliances | 87 | 87 | 63 | 6 | 17 | 0 | 1 | ✓ |
| F1 | Reference Tab - Do not Delete | 42 | 42 | 0 | 0 | 8 | 34 | 0 | ✓ |
| F1 | Sheet3 | 15 | 15 | 14 | 1 | 0 | 0 | 0 | ✓ |
| F1 | Solution Evaluation Criteria | 1 | 1 | 0 | 0 | 0 | 1 | 0 | ✓ |
| F1 | Top Clients Shortlist | 33 | 33 | 28 | 5 | 0 | 0 | 0 | ✓ |
| F1 | Top Insurers and Brokers | 231 | 231 | 225 | 6 | 0 | 0 | 0 | ✓ |
| F1 | White Spaces - Experience | 23 | 23 | 0 | 0 | 0 | 23 | 0 | ✓ |
| F2 | Captives in India | 9 | 9 | 7 | 2 | 0 | 0 | 0 | ✓ |
| F2 | Captives in the Philippines | 9 | 9 | 7 | 2 | 0 | 0 | 0 | ✓ |
| F3 | Commercial | 21 | 21 | 6 | 2 | 12 | 0 | 1 | ✓ |
| F3 | Personal Lines | 21 | 21 | 7 | 2 | 12 | 0 | 0 | ✓ |
| F4 | Competitor wise | 47 | 47 | 46 | 1 | 0 | 0 | 0 | ✓ |
| F4 | L&A Clientwise | 61 | 61 | 59 | 2 | 0 | 0 | 0 | ✓ |
| F4 | P&C Clientwise | 54 | 54 | 52 | 2 | 0 | 0 | 0 | ✓ |
| F5 | Competitor Analysis | 76 | 76 | 72 | 4 | 0 | 0 | 0 | ✓ |

## `skipped_non_data` rows — worth scrutinising

These rows have content but didn't match the expected data shape. Could be footer notes, sub-tables, or schema mismatches.

- **F1 / Build-Buy-Partner Analysis** (1 rows): [55]
- **F1 / Capability Gap Assessment -Ver2** (2 rows): [47, 64]
- **F1 / Client Prioritization Framework** (9 rows): [3, 4, 11, 12, 18, 19, 20, 21, 22]
- **F1 / Partnerships and Alliances** (1 rows): [70]
- **F3 / Commercial** (1 rows): [7]

## Datetime coverage on output rows

| Table | Rows | with file_vintage | with captured_date | with ingestion_date | Complete? |
|---|---:|---:|---:|---:|:---:|
| competitor_caps.csv | 46 | 46 | 46 | 46 | ✓ |
| priorities.csv | 23 | 23 | 23 | 23 | ✓ |
| build_buy_partner.csv | 121 | 121 | 121 | 121 | ✓ |
| build_buy_partner_table_b.csv | 80 | 80 | 80 | 80 | ✓ |
| solutions.csv | 43 | 43 | 43 | 43 | ✓ |
| client_engagements_summary.csv | 73 | 0 | 0 | 73 | ✗ |
| engagements_competitor_analysis.csv | 144 | 144 | 144 | 144 | ✓ |
| partners_alliances.csv | 63 | 63 | 63 | 63 | ✓ |
| leads_ranked.csv | 236 | 0 | 236 | 236 | ✗ |
| solution_matches.csv | 60 | 0 | 0 | 0 | ✗ |
| clients_top_insurers.csv | 225 | 225 | 225 | 225 | ✓ |
| solution_codes.csv | 16 | 16 | 16 | 16 | ✓ |
| capability_gaps.csv | 52 | 52 | 52 | 52 | ✓ |
| clients_top_clients_shortlist.csv | 28 | 28 | 28 | 28 | ✓ |
| leads_summary.csv | 50 | 0 | 0 | 0 | ✗ |
| insuretech_landscape.csv | 81 | 81 | 81 | 81 | ✓ |
| competitor_profiles.csv | 13 | 13 | 13 | 13 | ✓ |
| engagements_f4_clientwise.csv | 111 | 111 | 111 | 111 | ✓ |
| triggers_fired.csv | 60 | 0 | 60 | 60 | ✗ |
| prioritization_framework.csv | 10 | 10 | 10 | 10 | ✓ |
| partnership_landscape.csv | 63 | 63 | 63 | 63 | ✓ |
| client_profiles.csv | 236 | 0 | 0 | 236 | ✗ |
| insuretech_gap_analysis.csv | 9 | 9 | 9 | 9 | ✓ |
| clients_sheet3.csv | 14 | 14 | 14 | 14 | ✓ |
| captives.csv | 14 | 14 | 14 | 14 | ✓ |
