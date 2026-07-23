---
name: tam-ask
description: Answer any free-text question about EXL's insurance market corpus — carriers, competitors, EXL clients/revenue, engagements, captives, solutions, white-space — grounded in the source spreadsheets and always cited and dated. Use when someone asks about a specific company ("what's our involvement with Travelers?"), asks to rank/aggregate/compare ("top 10 EXL clients by revenue", "who competes with us at Allstate"), or asks anything the corpus data could answer. Claude is the engine: it routes over schema cards, pulls exact rows via a query script, and composes a source-cited, as-of-dated answer.
---

# tam-ask — grounded, cited Q&A over the TAM corpus

You (Claude) are the engine. The corpus is described by compact **schema cards** — over
spreadsheet **tables** and presentation **decks** — and a deterministic **query script** is
your hands for pulling exact, cited content. Never answer corpus questions from memory —
route, query, then compose.

## Locating the package
Paths below are relative to the package root — the folder containing `.tam-root`. In a repo
that's the working directory. If a command fails because you're not at the root, find it
(`find . /mnt -maxdepth 4 -name .tam-root 2>/dev/null`) and run from there, or set
`TAM_ROOT` to that folder. The scripts resolve their own data paths either way.

## Layout (repo-relative)
- Card index (scan first):  `produced_data/cards/index.json`
- Full cards (one per table): `produced_data/cards/<table_id>.json`
- Query engine:             `python3 code/tam/query.py --spec <spec.json>`  (or pipe spec on stdin)
- Name normalization:       `python3 code/tam/normalize.py --scan "<name>" ...`

## Answering workflow

1. **Read the index.** Load `produced_data/cards/index.json`. Each entry has `table_id`,
   `kind` (`table` | `presentation`), `summary`, `use_cases`, `entity_key_col`, `as_of`,
   `joins`, `duplicate_of`; deck entries also carry `n_slides` and `entities`.
2. **Classify** the question: `lookup` | `calc` (rank/aggregate) | `reason` (synthesize across
   sources) | `unanswerable-from-corpus`.
3. **Select the minimal set of sources** whose `summary`/`use_cases` match — tables and/or
   decks. Prefer the canonical table over any `duplicate_of`. Name 1–2 and why (citation trail).
4. **Load the full card(s)** — real columns/examples (tables), or slide points + entities (decks).
5. **Normalize any company/entity name** in the question:
   `python3 code/tam/normalize.py --scan "TRV"` → `Travelers Group`. Use the canonical form.
6. **Emit a QUERY SPEC** (JSON) against real columns and run it:
   ```
   echo '{"table_id":"F1.top_insurers_and_brokers",
          "select":["Company/ Group","2020-Rev Budget"],
          "filters":[{"col":"EXL Client","op":"==","value":"Yes"}],
          "sort":{"col":"2020-Rev Budget","dir":"desc"},"limit":10}' | python3 code/tam/query.py
   ```
   Spec ops: `== != > < >= <= in nin contains icontains notnull isnull`; plus
   `group_by`, `aggregate:[{col,fn,as}]`, `sort`, `limit`, `normalize:[cols]`,
   `join:{table_id,left_on,right_on,select}`. See a card's `use_cases` for hints.

   **For a deck** (`kind: presentation`), emit a DECK SPEC with `deck_id` instead — it
   re-reads the real slides and returns their text with slide-number provenance:
   ```
   echo '{"deck_id":"P1.deck","entity":"Travelers","fields":["title","text","notes"]}' \
        | python3 code/tam/query.py
   ```
   Deck keys: `slides:[N]` (specific slide numbers), `entity` (slides mentioning it, per the
   card — normalized), `contains` (case-insensitive text search), `fields`, `limit`. Use the
   card's `slides[].point` to pick which slide(s) to pull, and `entities[]` for who/why.
7. **Sanity-check** the result (row/slide count, plausibility). If empty/implausible, re-route
   (maybe the wrong source) or downgrade to `reason`.
8. **Compose the answer** under the output contract below.

## Output contract (non-negotiable)

- **Date every answer.** The query result carries `as_of` and `staleness`. Lead with it:
  *"As of **Aug 2020** (F1)…"*. When the result's `staleness.stale` is true, append the
  `staleness.note` (a nudge to refresh). If you combined tables of different vintages, state
  the range and name the oldest.
- **Cite every fact.** For a table, trace to `file_alias / sheet / row` using the result's
  `citation` and `provenance_rows` (e.g. `F5/Competitor Analysis/R8`). For a deck, trace to
  `file_alias / slide N` using `provenance_slides` (e.g. `P1/slide 4`). No citation → don't
  state it.
- **Normalize names** so "TRV"/"Travelers Companies Inc." read as one account.
- **Use the vocabulary the data itself uses** — the entity names, product/solution names,
  and terms found in the cards and cells. Don't import outside jargon; don't assume a domain.
- **When the corpus can't answer**, say so plainly, name the missing column/table (from the
  card's `not_answerable`), and **surface the closest available data** — never a bare
  "no data". Example: "EXL revenue from Allstate in 2024" → "No post-2020 figure exists; the
  closest is the 2020 revenue budget of ~$9.19M (F1, as of Aug 2020)."

## Knowing what skills exist (discovery + avoiding overlap)

This bundle can hold team-made skills for repeated jobs (see `docs/ADDING_SKILLS.md`). A
compact catalog of them lives at `produced_data/skills_catalog.json` (rebuilt by
`python3 code/tam/build_skill_index.py`).

- If someone asks **"what can I do here / what skills are available?"**, read the catalog and
  list each skill's `name` + `description`.
- If a request closely matches an existing skill, **use that skill** rather than answering
  from scratch, and say which one you used.
- If someone is about to **create a new skill**, first read the catalog and check for overlap.
  If an existing skill nearly covers it, suggest extending that one. Only spin up a new skill
  when the need is genuinely distinct — specificity is welcome, duplication is not.

## Worked examples

- *"What's our involvement with Travelers?"* → normalize → query `F5.competitor_analysis`
  (incumbents/friction) + `F1.top_insurers_and_brokers` (relationship, CxOs, wallet share);
  compose a dated, cited relationship summary.
- *"Top 10 EXL clients by revenue"* → `F1.top_insurers_and_brokers`, filter `EXL Client=Yes`,
  sort `2020-Rev Budget` desc, limit 10 → Hartford #1 (~$18.4M), cited, *as of Aug 2020*.
- *"Which competitor is at Allstate and how big?"* → `F5.competitor_analysis` filter customer.
- *"What data is stale / needs refreshing?"* → read every card's `as_of` from the index,
  sort oldest-first, report ages and which owners to ping.

For repeated, pre-built views, use whichever team skill covers them (see
`produced_data/skills_catalog.json`); use `tam-ask` for everything free-text.
