# Target Addressable Market (TAM)

EXL competitive-intelligence and sales-lead engine for the insurance Total
Addressable Market. A deterministic, rule-based pipeline reads a corpus of
internal EXL spreadsheets and produces ranked, source-cited sales leads,
account briefs, and a strategic white-space map. It is surfaced to EXL teams
through the `exl-sales-intelligence` Claude Code skill.

## Repository layout

Files are organized by **role** — code, the data going in, the data coming
out, project demos, docs, and the Claude skill.

```
├── code/                    # all executable code
│   ├── pipeline/            # 7-stage lead engine + exl_taxonomy.py (shared vocabulary)
│   │                        #   ingest → audit → profiles → triggers → score → synthesize → whitespace
│   └── scripts/             # standalone builders (inventory, Travelers brief, project deck)
│
├── input_data/              # raw source material fed INTO the code (never generated)
│   ├── corpus/              # the 5 canonical EXL spreadsheets (F1–F5) the pipeline ingests
│   ├── L&A Playbook 2025.xlsx
│   ├── PC Insurance Directory - Sep 2025_Final (2).xlsx
│   └── travelers/           # Travelers-specific source data
│
├── produced_data/           # everything the code GENERATES (regenerable)
│   ├── pipeline/            # data/ (CSVs), leads/ (per-account briefs), *_REPORT.md,
│   │                        #   COVERAGE_AUDIT.md, LEADS_DIGEST.md, WHITESPACE_MAP.xlsx
│   ├── excel_data_inventory.xlsx
│   └── travelers/           # Travelers deliverables (lead brief, detailed report, presentation)
│
├── demo/                    # decks that showcase THIS project (V1_Presy)
│
├── docs/                    # specs, frameworks, and planning material
│   ├── SCHEMA_RAG_SPEC.md   # engineering spec for the schema-RAG data layer
│   ├── Addressable Market Tracker.docx   # TAM/SAM/SOM assessment framework
│   ├── plan/                # project plan, approach, TODO
│   └── project_plan/        # source decks/gantt (incl. the taxonomy source deck)
│
└── .claude/                 # the exl-sales-intelligence skill (SKILL.md + run.py)
```

## Using the skill

The skill has a single entrypoint that wraps the pipeline outputs:

```bash
python3 .claude/skills/exl-sales-intelligence/run.py <command> [args]
```

| Command | What it does |
|---|---|
| `list_accounts` | Ranked list of all client accounts |
| `account <name>` | Full source-cited sales brief for one account (fuzzy name match) |
| `top [N]` | Top N leads (default 10) with recommended EXL products |
| `triggers <name>` | Every signal that fired for an account, with evidence |
| `whitespace` | Partnering-Matrix benchmarks + top white-space accounts |
| `refresh` | Re-run all 7 pipeline stages (use after source spreadsheets change) |

## Re-running the pipeline directly

All scripts resolve their paths relative to the repo root, so they run from
anywhere:

```bash
python3 code/pipeline/ingest.py && python3 code/pipeline/audit.py && \
python3 code/pipeline/profiles.py && python3 code/pipeline/triggers.py && \
python3 code/pipeline/score.py && python3 code/pipeline/synthesize.py && \
python3 code/pipeline/whitespace.py
```

Inputs are read from `input_data/corpus/`; all outputs are written to
`produced_data/pipeline/`.

### Dependencies

```bash
pip install pandas openpyxl python-docx python-pptx
```
