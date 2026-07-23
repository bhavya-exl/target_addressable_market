---
name: tam-ingest
description: Ingest a new spreadsheet into the corpus so it becomes queryable. Use when someone adds an .xlsx/.xlsm/.csv file and wants it usable for questions — "ingest this file", "add this data", "profile this workbook". Claude runs a profiler over the file and authors a schema card per table (summary, use-cases, typed columns, real examples, what it can't answer, vintage), then registers it in the card index. The procedure is identical for every file.
---

# tam-ingest — turn any spreadsheet into queryable, cited, dated data

**You know nothing about this file except that it is a spreadsheet.** Do not assume any
industry, company, product, or subject matter. Everything you write in a card MUST be
derivable from the file itself — its structure and its cell values. Never import outside
knowledge about "what this file probably is." The whole point is that this same procedure
works on a file no one has seen before.

The point is NOT "read every row" (any tool can dump rows). The point is that when a
relevant question comes later, `tam-ask` can tell *which* table holds the answer and pull
*exactly* the right rows — cited and dated. The card is what makes that possible.

## Locating the package
Paths below are relative to the package root — the folder containing `.tam-root` (the working
directory in a repo). If not at the root, find it (`find . /mnt -maxdepth 4 -name .tam-root`)
and run from there, or set `TAM_ROOT`. Scripts resolve their own data paths regardless.

## Shared (OneDrive-synced) folders — nothing to coordinate
If this bundle is hosted in a SharePoint library synced to multiple people (see
`docs/SHAREPOINT_SETUP.md`), just ingest normally. New files land for everyone automatically
once OneDrive syncs — you don't push anything, and there is no lock to manage. `build_index.py`
regenerates `index.json` atomically and auto-cleans any OneDrive conflict copy, so even if two
people ingest close together the next rebuild self-heals. (`python3 code/tam/sync_check.py`
is an optional health check that just confirms the copy resolves and is writable.)

## Tools (repo-relative)
- Profiler:      `python3 code/tam/dump.py "<file>" --json produced_data/cards/_profiles/<alias>.profile.json`
- Card template: `code/tam/templates/card.template.json`  (structure to fill; content comes from the file)
- Normalizer:    `python3 code/tam/normalize.py --scan ... | --append ...`
- Index builder: `python3 code/tam/build_index.py`
- Link detector: `python3 code/tam/link.py`   (finds joins across tables by value overlap — no domain knowledge)
- Query (self-test): `python3 code/tam/query.py --spec <spec.json>`

## Procedure (same for every file)

1. **Profile** the file with `dump.py`. You get, per sheet: detected `header_row` (not
   assumed to be row 1), `two_row_header`, columns (inferred type, role hint, null %,
   distinct, sample values), and `sample_rows` with **real source row numbers**, plus
   anomaly flags (empty scaffold, near-duplicate column set).

2. **Assign a file alias** (a short handle like `F6`) — just an identifier, carries no meaning.

3. **Infer the vintage (`as_of`)** strictly from evidence in the file:
   - dates in the **filename** (e.g. `...Jun 2021...`, `20200803`, `Sep 2025`),
   - dates in **sheet names / column headers** (e.g. a column literally named `... - 2/21`),
   - date **values** in the data.
   Use the most specific reliable one. **If you find no date, set `as_of: null`**, add
   `"vintage_unknown"` to `warnings`, and note that the data owner should confirm the
   as-of date. Never invent a date. (This is what lets every answer be dated and lets the
   system flag stale data for refresh.)

4. **Author one card per data table** → `produced_data/cards/<alias>.<slug>.json`
   (`slug` = sheet name lowercased, non-alphanumeric runs → single underscore).
   Fill the template using ONLY the file:
   - `grain`: one clause describing what one row represents (infer from the entity-like column + row shape).
   - `summary`: 2–3 plain sentences on what the columns collectively represent and what they let you answer. Describe the data as it is; do not editorialize about things not in this table.
   - `use_cases`: 3–6 questions the columns can answer, phrased naturally (lookup, ranking/aggregation, filter/segment). These are what the router matches on.
   - `entity_key_col`: the column that best identifies each row (a high-cardinality name/id column at the grain), or null.
   - `columns`: every meaningful column, with corrected `type` (use the samples: large plain numbers under a money-suggesting header → `currency_usd`; a `%`-bearing column → `percent`; etc.) and `role` (`entity_key|dimension|measure|attribute|meta`). Terse `note` only when non-obvious. Leave `joins` empty — the link detector fills them.
   - `examples`: pick **2–3 rows structurally** — one fully-populated row and one sparse/edge row — copied from the profile `sample_rows` (keep `_source_row`). Never pick rows by their topic or content.
   - `not_answerable`: 1–3 questions the table cannot answer, each with the reason (a missing column, no time series, an all-empty field). Derive these from the columns that are absent or empty.
   - carry `header_row`, `two_row_header`, `duplicate_of`, and `warnings` from the profile.

5. **Non-data sheets** (nav/home/reference/empty scaffold; profile `role != "data"` or near-zero
   rows): write a minimal stub card with `"role": "non_data"` and a one-line reason. Still set `as_of`.

6. **Duplicates:** if the profiler flags two sheets with the same column set, keep the one with
   more populated rows/columns as canonical and set `duplicate_of` on the other (generic rule —
   based on completeness, not on what the sheet is about).

7. **Normalize entities:** scan the `entity_key_col` values with `normalize.py --scan`. For new
   entities not yet mapped, `--append` a variant→canonical row so future joins/filters resolve.

8. **Link & register:** run `link.py` (adds `joins` between tables whose entity columns share
   values — pure overlap, no assumptions), then `build_index.py` (folds cards + joins into `index.json`).

9. **Self-verify** each data card: for every `use_case`, confirm `query.py` returns non-empty,
   plausible rows against real columns. If a fair question fails, enrich the card's summary/
   use_cases (add the missing concept) and retry — do not fix it by dumping rows.

## Determinism expectation
Re-ingesting the same file must produce a stable card — same grain, columns, `entity_key_col`,
and use-case intent. The profiler is fully deterministic; keep authored text faithful to the
columns so two runs agree.
