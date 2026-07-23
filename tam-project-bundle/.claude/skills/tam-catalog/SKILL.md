---
name: tam-catalog
description: Show what is IN this corpus — which source documents and data tables exist, what each one covers, how current it is, and what skills are available — so people know what they can ask before diving in. Use when someone asks "what data do we have", "what's in here", "what can I ask about", "what documents/files/tables exist", "what's in the L&A playbook", "what covers competitors", or wants an overview/orientation. This skill only DESCRIBES what's present; it does not answer business questions or pull data rows (hand those to tam-ask / tam-report).
---

# tam-catalog — what's in the corpus (orientation, read-only)

Your job is to tell someone **what exists** so they know what they can ask. You describe
coverage; you do **not** analyze, rank, recommend, or pull row-level data — for that, point
them to `tam-ask` (questions), `tam-report` (charts/briefs), or `tam-ingest` (add a file).
Everything you report comes from the generated catalogs below — never from memory, and never
by opening the spreadsheets themselves.

## Sources to read
- Data catalog: `produced_data/cards/index.json` — one entry per source with `table_id`,
  `title`, `kind` (`table` | `presentation` | `image`), `summary`, `file_alias`, `source_file`,
  `as_of`, `as_of_basis` (stated/inferred/unknown), `row_count`, `grain`, `role`; deck entries
  also carry `n_slides`. The header has `n_data_tables`, `n_presentations`, `n_images`.
- Skills catalog: `produced_data/skills_catalog.json` — `name` + `description` per skill.
  (Rebuild these with `python3 code/tam/build_index.py` and
  `python3 code/tam/build_skill_index.py` if they look out of date.)

## What to show

**Default ("what's in here?" / "what can I ask about?")** — a grouped inventory:
1. Read `index.json`. Group entries by `source_file` / `file_alias` (each file is one document).
2. For each document, give: the file name, its `as_of` (vintage) — noting when `as_of_basis`
   is `inferred`/`unknown` so people know the date is soft — what it holds (how many tables,
   a deck's `n_slides`, or an image), and a one-line sense of what it covers (from
   titles/summaries).
3. Under each document, list its entries as `table_id — title` (one line each). A deck shows as
   a single `<alias>.deck` entry; an image as `<alias>.image`. Keep it scannable.
4. End with: the total (files, tables, decks, images), the newest and oldest `as_of`, and a
   pointer — "ask tam-ask a question, or tam-report for a chart."

**Focused asks** — answer from the same catalog, no data access:
- "What's in the L&A playbook / F8?" → list only that file's tables + summaries.
- "What covers competitors?" → scan summaries/titles for the theme and list the matching
  tables and which document they live in.
- "What's the newest / oldest data?" → sort by `as_of`.
- "What skills can I use?" → read `skills_catalog.json` and list name + description.

## Rules
- **Describe, don't do.** If the ask is actually a question about the data ("who are the top
  clients?"), say the catalog shows that lives in table X and hand off to `tam-ask`.
- **Be honest about coverage and age.** Note stale documents (e.g. F1 is Aug 2020) so people
  know how current an area is. If something isn't in the catalog, say it's not in the corpus
  and suggest `tam-ingest`.
- **Group by document** by default — people think in terms of "which file / which report."
