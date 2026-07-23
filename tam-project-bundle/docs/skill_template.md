# SKILL.md template

Copy this structure when creating a new skill under `.claude/skills/<skill-name>/SKILL.md`.
The frontmatter (between the `---` lines) is required; the body is instructions to Claude.
Keep data skills grounded: route through the cards and `query.py`, cite and date everything.

```markdown
---
name: <skill-name>            # kebab-case, unique; matches the folder name
description: <one sharp line naming WHAT it does and WHEN to use it — this is how Claude
  decides to trigger the skill, so be specific. e.g. "Build the monthly top-N EXL clients
  chart (revenue + competitor overlay). Use when someone asks for the monthly client report.">
---

# <skill-name> — <short title>

## What this produces
<one or two sentences: the exact output and its format>

## Inputs / parameters
<what the user can vary, e.g. N (default 25), business line (P&C / L&A / both), month>

## Procedure (stay grounded)
1. Read `produced_data/cards/index.json` and pick the table(s) needed.
2. Load the full card(s) for real column names.
3. Normalize any company names via `python3 code/tam/normalize.py --scan "<name>"`.
4. Pull data with a query spec through `python3 code/tam/query.py` — never read a
   spreadsheet the cards don't describe, and never answer from memory.
5. Build the output (chart/table/brief). Every figure carries its citation and as-of date.

## Output contract
- Lead with the as-of date; append the staleness note when the result is stale.
- Cite each fact to file_alias / sheet / row.
- If the corpus can't answer, say so and surface the closest available data.
```

Tips:
- Test the skill once end-to-end before relying on it.
- If it overlaps an existing skill, update that one instead of adding a near-duplicate.
