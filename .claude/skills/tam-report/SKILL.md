---
name: tam-report
description: Produce a chart, dashboard, or written report from the EXL insurance corpus — "chart the top 10 EXL clients by revenue", "build a one-page brief on Travelers", "visualize competitor footprint across our accounts". Claude is the engine: it pulls grounded datasets via the query script, then builds the visual/report with its native abilities — every figure traced to a source and stamped with the data's as-of date.
---

# tam-report — charts & reports on proprietary data

Claude's native charting and writing, but grounded: **nothing is plotted or stated that
isn't a cited row from the corpus.** Built on the same query engine as `tam-ask`.

## Locating the package
Paths below are relative to the package root — the folder containing `.tam-root` (the working
directory in a repo). If not at the root, find it (`find . /mnt -maxdepth 4 -name .tam-root`)
and run from there, or set `TAM_ROOT`. Scripts resolve their own data paths regardless.

## Layout (repo-relative)
- Card index / cards: `produced_data/cards/index.json`, `produced_data/cards/<table_id>.json`
- Query engine:       `python3 code/tam/query.py --spec <spec.json>`
- Output artifacts:   write to `produced_data/reports/`

## Report workflow

1. **Decompose** the request into one or more data pulls — each a `tam-ask` QUERY SPEC.
   (For a Travelers brief: relationship row from `F1.top_insurers_and_brokers`, engagements
   from `F5.competitor_analysis`, priorities from `F1.buyer_priorities`, etc.)
2. **Pull grounded datasets** with `query.py`. Keep each result's `citation`,
   `provenance_rows`, and `as_of`.
3. **Determine the as-of date** for the whole artifact = the oldest `as_of` across the pulls.
   If any pull is stale, carry the refresh note into the artifact footer.
4. **Build the artifact** from those datasets ONLY:
   - Charts: follow the `dataviz` skill's conventions (accessible palette, clear axes,
     titles). Prefer a self-contained HTML/SVG or a matplotlib PNG.
   - Reports: structured doc (headline, findings, table, sources).
5. **Stamp provenance + time.** Every figure/number ties to a citation; put an
   **"As of <date>"** in the title/subtitle and a **Sources** section listing
   `file_alias / sheet / rows`. Add the staleness note when applicable.

## Rules
- No un-sourced numbers. If a requested cut isn't in the corpus, say so (use the card's
  `not_answerable`) rather than inventing it.
- Dates are mandatory: a chart with no as-of date is not acceptable — the reader must know
  the data is (e.g.) Aug 2020, not today.
- Use EXL vocabulary/outcome framing only where the data supports it.

## Example
"Chart the top 10 EXL clients by revenue" → query `F1.top_insurers_and_brokers`
(`EXL Client=Yes`, sort `2020-Rev Budget` desc, limit 10) → horizontal bar chart titled
*"Top 10 EXL Clients by 2020 Revenue Budget — as of Aug 2020"*, each bar labeled, a
Sources line citing `F1/Top Insurers and Brokers` rows, and a footer noting the data is
~6 years old.
