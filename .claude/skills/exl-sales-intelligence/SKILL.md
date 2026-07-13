---
name: exl-sales-intelligence
description: EXL competitive intelligence and sales lead engine for the insurance Total Addressable Market (TAM) corpus. Use when the user asks about EXL accounts, sales leads, competitor footprints at insurers, white-space or market opportunities, an account brief, what triggers fired for an account, or wants to refresh the pipeline. Commands (one entrypoint): list_accounts (ranked list of all 236 client accounts), account NAME (full sales brief for one client with EXL product recommendations, outcome metrics, and source citations), top N (top N leads), triggers NAME (signals firing for an account), whitespace (strategic heatmap and Partnering Matrix benchmarks), refresh (re-run the full pipeline). Output is source-cited to the 5 internal EXL spreadsheets in input_data/corpus/, uses EXL product vocabulary (XTRAKTO.AI, EXELIA.AI, NerveHub, Subrosource, Paymentor, Digital Finance Suite, Customer 360, LifePRO, MedConnection, Engage, Assist, DIVA), and references the Addressable Market Tracker deck taxonomy.
---

# exl-sales-intelligence — EXL Sales Lead Engine

One-stop skill for querying the consolidated competitive-intelligence pipeline built from EXL's internal TAM corpus (5 spreadsheets in `input_data/corpus/`).

## When to invoke this skill

Use this skill whenever the user asks anything related to:
- EXL accounts (Travelers, Allstate, Liberty Mutual, etc.) or insurance carriers in general
- Sales leads or lead generation
- Competitive intelligence (what competitors are doing at which clients)
- Market white space / TAM / segment opportunities
- A specific account's profile, triggers, or pitch
- The lead-engine pipeline itself (refreshing, scoring, etc.)

Examples of user requests that match:
- "Show me the top 10 leads"
- "Give me a brief for Travelers"
- "What's happening at Allstate?"
- "List all the accounts we have"
- "Where's the biggest white space?"
- "Why is Travelers ranked first?"
- "Refresh the pipeline"

## How to use

The skill has a single entrypoint script that handles all commands:

```
python3 .claude/skills/exl-sales-intelligence/run.py <command> [args...]
```

Available commands:

| Command | What it does |
|---|---|
| `list_accounts` (or `list`) | Print the full ranked list of all 236 accounts with score, confidence, relationship type, trigger count |
| `account <name>` | Print the full sales brief for one account. Fuzzy match on name (e.g. `account travelers` matches "Travelers Group"). If multiple matches, lists candidates |
| `top [N]` | Print top N leads (default 10) — rank, score, confidence, trigger count, top recommended EXL products |
| `triggers <name>` | List every trigger that fired for an account, with evidence text and source-row citations |
| `whitespace` | Print the Partnering Matrix retention benchmarks + top-20 white-space accounts. The richer view is in `produced_data/pipeline/WHITESPACE_MAP.xlsx` |
| `refresh` | Re-run the full 7-stage pipeline (ingest → audit → profiles → triggers → score → synthesize → whitespace). Use after source spreadsheets are updated |

## Invocation pattern

When user asks something matching the patterns above:
1. Pick the right command (e.g. "show me top 5" → `top 5`)
2. Run the Python script via Bash tool
3. Format the output for the user — keep the source citations and lead-score breakdowns visible
4. If a name is ambiguous, let the script's fuzzy-match output guide the next question

## Output contract

Every output the skill produces is:
- **Source-cited** — every claim traces back to a specific row in a specific source sheet (e.g. `F5/Competitor Analysis/R8`)
- **Vocabulary-correct** — uses EXL's actual product names (XTRAKTO.AI, EXELIA.AI, etc.) and the Addressable Market Tracker's 5-area P&C taxonomy
- **Outcome-anchored** — every product recommendation pairs with the typical outcome metric from the deck (e.g. "25-30% cost-of-operations reduction")
- **Deterministic** — re-running on the same data produces the same output. The pipeline is rule-based; no LLM in the synthesis loop

## What's NOT in this skill (V1 scope)

- External data (SEC EDGAR, earnings calls, AM Best, news) — V2 work
- Interactive Q&A on the lead briefs (the script outputs static text)
- Visualizations beyond the Excel heatmap (no embedded charts)
- Score-weight tuning UI — weights are in `code/pipeline/score.py` constants

## Related files

- Pipeline scripts: `code/pipeline/{ingest,audit,profiles,triggers,score,synthesize,whitespace}.py`
- Single-source taxonomy: `code/pipeline/exl_taxonomy.py`
- Lead briefs (one per top-20 account): `produced_data/pipeline/leads/*.md`
- Source-row reconciliation: `produced_data/pipeline/COVERAGE_AUDIT.md`
- Strategic heatmap: `produced_data/pipeline/WHITESPACE_MAP.xlsx` (7 sheets)
- Project memory: `~/.claude/projects/.../memory/` (auto-loaded)
