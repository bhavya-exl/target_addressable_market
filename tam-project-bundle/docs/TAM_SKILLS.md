# TAM Skill Suite — a schema-card data layer for Claude

A portable set of **Agent Skills** that let **Claude (the model) answer questions over a
corpus of spreadsheets** — grounded, cited, and dated. Claude is the engine; the skills give
it a map of the data (schema cards) and deterministic scripts to pull exact rows. Ship the
skills together with the data files and any Claude with code execution can use them.

## The idea (pseudo-RAG over schemas, not rows)

We don't embed cell contents. Each table (spreadsheet sheet) is described by a compact
**schema card**: a summary, the questions it can answer, typed columns, real example rows,
what it *can't* answer, and its **vintage** (as-of date). To answer a question, Claude reads
the small **card index**, picks the relevant table(s), pulls exact rows with a query script,
and composes a cited, dated answer. New files are added by the *same* procedure — no per-file
coding.

## Components

```
.claude/skills/
  tam-ingest/   Add a new spreadsheet: profile it, author a card per table, normalize
                names, register + link it. Knows only "this is a spreadsheet."
  tam-ask/      Answer a free-text question: route over cards -> query -> cited, dated answer.
  tam-report/   Build a chart/report from the corpus; every figure cited and dated.
  tam-catalog/  Orientation (read-only): what documents, tables, and skills exist.

code/tam/       Deterministic engine (no domain knowledge, repo-relative paths):
  dump.py         profile any .xlsx/.csv (header detection, types, samples, anomalies)
  query.py        header-aware cited query: filter/join/group/aggregate/sort + provenance + as_of
  normalize.py    entity-name normalization over the alias map
  link.py         detect joins between tables by value overlap
  build_index.py  build the compact routing index
  templates/card.template.json

produced_data/cards/    the card store
  index.json            routing index (id, summary, use_cases, as_of, joins) — scanned first
  <F#>.<slug>.json      one card per table
  _profiles/            regenerable dump.py output (gitignored)

produced_data/reports/  generated artifacts (charts, reports, staleness)
input_data/corpus/      the source spreadsheets the cards point at
```

## Using it

**Ask a question** (tam-ask):
```
1. read produced_data/cards/index.json
2. pick the table(s) whose summary/use_cases match; normalize any company name
3. echo '<query spec>' | python3 code/tam/query.py     # returns rows + provenance + as_of
4. answer, leading with "As of <date>…", citing file/sheet/row, flagging staleness
```
Example spec:
```json
{"table_id":"F1.top_insurers_and_brokers","select":["Company/ Group","2020-Rev Budget"],
 "filters":[{"col":"EXL Client","op":"==","value":"Yes"}],
 "sort":{"col":"2020-Rev Budget","dir":"desc"},"limit":10}
```

**Ingest a new file** (tam-ingest): point it at any spreadsheet; it profiles, authors cards
(inferring vintage from the file), normalizes names, then `link.py` + `build_index.py`. The
file is immediately queryable. See `.claude/skills/tam-ingest/SKILL.md`.

**Make a report** (tam-report): decompose the request into query specs, pull grounded data,
build a chart/report with every figure cited and an as-of date. See `produced_data/reports/`.

## Principles

- **Temporal grounding.** Every card carries `as_of`; every answer is dated; stale sources get
  a refresh nudge (`produced_data/reports/STALENESS.md` lists what to update, oldest first).
- **Cited, not remembered.** Facts trace to `file / sheet / row`. If the corpus can't answer,
  the system says so and offers the closest available data — it does not invent.
- **Domain-agnostic ingest.** `tam-ingest` assumes nothing about the subject matter; it derives
  everything from the file. The same procedure handles a file it has never seen.
- **Normalized entities.** "TRV" / "Travelers Companies Inc." resolve to one account
  (`produced_data/pipeline/data/aliases.csv`), so filters and joins work across sources.

## Dependencies
`pip install pandas openpyxl` (charts/reports may use the host's rendering).
