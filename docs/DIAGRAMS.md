# TAM Intelligence — process diagrams

Rendered version: `produced_data/reports/tam_flows.html` (also published as an Artifact).

## Pipeline A — Ingestion (`tam-ingest`)

Same procedure for every file; assumes nothing about the subject, only that it is a spreadsheet.

```mermaid
flowchart TB
  A["New spreadsheet dropped<br/>any .xlsx / .csv"] --> B["dump.py · profile each sheet<br/>header-row detection · type & role inference<br/>null% · samples w/ real source rows · anomaly flags"]
  B --> C["Claude authors a schema card per table<br/>grain · summary · use-cases · typed columns<br/>entity key · structural examples · not-answerable"]
  C --> D["Infer vintage (as-of) from the file<br/>filename / header / cell dates<br/>— else unknown → ask data owner"]
  D --> E["normalize.py · canonicalize entity names<br/>append new variants to the alias map"]
  E --> F["link.py · detect joins across tables<br/>by value overlap — no assumptions"]
  F --> G["build_index.py · refresh routing index"]
  G --> H{"self-test every use-case<br/>via query.py"}
  H -- "a fair question fails" --> C
  H -- "all pass" --> I["Card store ready<br/>cards/*.json + index.json"]
```

## Pipeline B — Querying (`tam-ask` / `tam-report`)

```mermaid
flowchart TB
  Q["User question — free text"] --> R["Read index.json · classify<br/>lookup · calc · reason · unanswerable"]
  R --> S["Select the minimal table(s)<br/>match summary + use-cases<br/>prefer canonical over duplicate"]
  S --> T["Load full card(s)<br/>normalize any entity name in the question"]
  T --> U["Emit query spec → query.py (header-aware)<br/>filter · join · group · aggregate · sort"]
  U --> V["Rows + provenance (file/sheet/row)<br/>+ as-of + staleness"]
  V --> W{"plausible result?"}
  W -- "empty / off" --> S
  W -- "yes" --> X["Compose answer<br/>dated 'as of…' · cited · honest fallback"]
  X --> Y["Optional · tam-report<br/>chart/report from the same cited rows"]
```

## Packaging & sharing

A skill file alone is not enough — the cards, alias map, engine scripts, and the actual
**data files** must travel together, because `query.py` reads the source sheets live.

**Ships as one package:** `.claude/skills/tam-{ingest,ask,report}` · `code/tam/*.py` ·
`produced_data/cards/` (+ `index.json`) · `produced_data/pipeline/data/aliases.csv` ·
`input_data/` (source spreadsheets).

| Option | For whom | Notes |
|---|---|---|
| **Shared internal repo + Claude Code** _(recommended)_ | Anyone who can open a repo in Claude Code | The repo *is* the package — skills auto-discovered, paths resolve, access = repo permissions, versioned/updatable. |
| **Shared Project on claude.ai** | Sales reps who live in claude.ai | Data + cards + scripts in a Team/Enterprise Project; skills added as org Skills. Needs a one-time bundle + a configurable data-root. |

**Confidentiality:** internal EXL competitive intelligence — distribute only within the org
(private repo / Enterprise workspace); never publish publicly.
