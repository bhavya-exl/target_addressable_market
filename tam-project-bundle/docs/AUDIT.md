# TAM bundle audit — 22 Jul 2026

Findings from a full pass over the bundle. Nothing here blocks the system from
running; these are data-hygiene items for the corpus owner to review.

## What was cleaned up in this pass

- Removed 7 stray `.DS_Store` files and the `code/tam/__pycache__/` bytecode cache.
- Added a root `.gitignore` (covers `.DS_Store`, `__pycache__`, the regenerable
  `_profiles/`, generated `reports/`, and `dist/`).
- Moved the one loose source spreadsheet into the corpus so all 7 sources live in
  one place: `input_data/PC Insurance Directory - Sep 2025_Final (2).xlsx` →
  `input_data/corpus/…`. The 8 `F6.*` card `source.file` paths were updated to match,
  the index was rebuilt, and an F6 query was confirmed to still work.
- Created `produced_data/reports/` (the skills write artifacts here and the docs
  reference it, but it did not exist) and moved the loose root artifact
  `EXL_Top10_Clients_Brief.pdf` into it.

## Open items (not changed — owner's call)

**1. Orphan profile: `produced_data/cards/_profiles/F7.profile.json`.**
An `F7` file was profiled by `dump.py` but no `F7` cards were ever authored, and no
card references an `F7` source. This is an incomplete ingest — either finish carding
that file with `tam-ingest`, or delete the stray profile. (`_profiles/` is regenerable
and now gitignored, so it's low-stakes.)

**2. Three "Capability Gap Assessment" cards are near-identical but not linked.**
`F1.capability_gap_assessment`, `…_2`, and `…_ver2` are each 52 rows and map to three
separate sheets in the F1 workbook ("Capability Gap Assessment", "… 2", "… -Ver2") —
so they are genuine versions in the source, not duplicate cards. But unlike
`F1.p_c_solutions_list` (correctly flagged `duplicate_of` `F1.consolidated_solutions`),
none of the three carries a `duplicate_of` or a "use the latest version" note. A
question routed here could land on a stale version. Recommend marking the canonical
one and setting `duplicate_of` (or a warning) on the others.

**3. Two source files have no `as_of` date.**
`F3` (Competitor Analysis PL and CL) and `F4` (EXL Insurance Competitors) carry no
vintage, so answers drawn from them can't be dated — which breaks the system's
"every answer is dated" principle. Recommend adding an `as_of` to those cards' `source`
blocks (infer from the file, or ask the data owner).

## Source-file registry (as of this audit)

| Alias | Cards | As-of    | File |
|-------|-------|----------|------|
| F1    | 23    | Aug 2020 | 20200803 PC-Strategy-Solution Development and GoToMarket PlanVer1.5.xlsx |
| F2    | 2     | Jun 2021 | Captive Operations Details Jun 2021 v3 - Copy.xlsx |
| F3    | 2     | *(none)* | Competitor Analysis PL and CL.xlsx |
| F4    | 3     | *(none)* | EXL Insurance Competitors.xlsx |
| F5    | 1     | Feb 2021 | P&C Competitor Analysis.xlsx |
| F6    | 8     | Sep 2025 | PC Insurance Directory - Sep 2025_Final (2).xlsx |
| F8    | 13    | 2025     | L&A Playbook 2025.xlsx |

52 tables total (44 data tables) across the index. F1 (Aug 2020) is the oldest source
and is flagged stale (~71 months old) by the query engine.
