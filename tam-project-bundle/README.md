# EXL TAM Intelligence bundle

A portable "ask-the-corpus" system for EXL insurance competitive intelligence. It lets
Claude answer free-text questions over a set of internal insurance spreadsheets —
**grounded, cited to file/sheet/row, and dated** — without embedding cell contents.

Instead of RAG over rows, each spreadsheet sheet gets a compact **schema card** (a summary,
the questions it can answer, typed columns, example rows, and an as-of date). To answer a
question, Claude scans the small card index, picks the relevant table(s), pulls exact rows
with a deterministic query script, and composes a cited, dated answer. New files are added by
the same procedure — no per-file coding.

## Folder map

```
tam-project-bundle/
├─ .tam-root                 Sentinel marking the package root. DO NOT MOVE — the engine
│                            finds everything relative to this file.
├─ .gitignore
├─ README.md                 This file.
├─ CLAUDE.md                 Session-start orientation Claude follows in this folder.
│
├─ code/tam/                 The engine (deterministic Python, no domain knowledge).
│   ├─ tam_root.py           Locates the bundle root via the .tam-root sentinel.
│   ├─ dump.py               Profiles any .xlsx/.csv (headers, types, samples, anomalies).
│   ├─ query.py              Header-aware cited query: filter/join/group/sort + provenance.
│   ├─ normalize.py          Entity-name normalization over the alias map.
│   ├─ link.py               Detects joins between tables by value overlap.
│   ├─ build_index.py        Rebuilds produced_data/cards/index.json.
│   ├─ build_skill_index.py  Rebuilds produced_data/skills_catalog.json.
│   ├─ package.py            Builds dist/tam-project-bundle.zip for sharing.
│   └─ templates/            card.template.json (card structure to fill).
│
├─ produced_data/
│   ├─ cards/                The card store — one JSON card per spreadsheet sheet.
│   │   ├─ index.json        Routing index (scanned first to pick tables). 52 tables.
│   │   ├─ F<n>.<slug>.json  53 cards. F1–F6, F8 map to the 7 source files below.
│   │   └─ _profiles/        Regenerable dump.py output (gitignored).
│   ├─ pipeline/data/
│   │   └─ aliases.csv       Entity alias map ("TRV" → "Travelers Group") for filters/joins.
│   ├─ reports/              Generated artifacts (charts, briefs). Written by tam-report.
│   └─ skills_catalog.json   Catalog of available skills (rebuilt by build_skill_index.py).
│       └─ EXL_Top10_Clients_Brief.pdf
│
├─ input_data/corpus/        The 7 source spreadsheets the cards point at.
│
├─ .claude/skills/           The three Agent Skills:
│   ├─ tam-ask/              Answer a question → route, query, cited/dated answer.
│   ├─ tam-catalog/          Orientation: what documents/tables/skills exist.
│   ├─ tam-ingest/           Add a new spreadsheet → profile, card, normalize, index.
│   └─ tam-report/           Build a chart/report; every figure cited and dated.
│
└─ docs/
    ├─ TAM_SKILLS.md         How the skill suite / schema-card approach works.
    ├─ PROJECT_SETUP.md      How to share this as a claude.ai Project.
    ├─ ORG_OWNER_SETUP.md    One-time owner setup: enable + provision skills, grant access.
    ├─ TEAMMATE_QUICKSTART.md One-page start for anyone joining.
    ├─ SHAREPOINT_SETUP.md   How to share via a OneDrive-synced SharePoint library.
    ├─ ADDING_SKILLS.md      How the team can add their own reusable skills.
    ├─ skill_template.md     Structure to follow when creating a new skill.
    └─ AUDIT.md              Data-hygiene findings from the 22 Jul 2026 cleanup.
```

## What's load-bearing (do not move or rename)

The engine, cards, and skills use hardcoded paths **relative to the `.tam-root` marker**.
These must keep their exact locations or the system breaks:

- `.tam-root`, `code/tam/`, `produced_data/cards/`,
  `produced_data/pipeline/data/aliases.csv`, `.claude/skills/`, and every file under
  `input_data/corpus/` (each card's `source.file` points at its exact path).

Only `produced_data/reports/` (generated output) and `docs/` are free to reorganize.

## Using it

- **Ask a question** (tam-ask): read `produced_data/cards/index.json`, pick the table(s),
  then
  `echo '<spec>' | python3 code/tam/query.py` returns rows + provenance + as-of.
- **Add a file** (tam-ingest): point it at a spreadsheet; it profiles, authors cards,
  normalizes names, then runs `link.py` + `build_index.py`.
- **Make a report** (tam-report): pull grounded data via `query.py`, build the visual with
  every figure cited and dated; output lands in `produced_data/reports/`.

Dependencies: `pip install pandas openpyxl`.

## Source files (registry)

| Alias | As-of    | File |
|-------|----------|------|
| F1    | Aug 2020 | 20200803 PC-Strategy-Solution Development and GoToMarket PlanVer1.5.xlsx |
| F2    | Jun 2021 | Captive Operations Details Jun 2021 v3 - Copy.xlsx |
| F3    | —        | Competitor Analysis PL and CL.xlsx |
| F4    | —        | EXL Insurance Competitors.xlsx |
| F5    | Feb 2021 | P&C Competitor Analysis.xlsx |
| F6    | Sep 2025 | PC Insurance Directory - Sep 2025_Final (2).xlsx |
| F8    | 2025     | L&A Playbook 2025.xlsx |

See `docs/AUDIT.md` for open data-hygiene items (undated F3/F4, an orphan F7 profile, and
an unlinked "Capability Gap Assessment" version trio).
