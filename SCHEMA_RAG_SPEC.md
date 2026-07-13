# Schema-RAG Data Layer — Engineering Spec

**Status:** Draft for implementation
**Owner:** Bhavya
**Target implementer:** Claude Code
**Context:** Core data-grounding layer beneath the `exl-sales-intelligence` skill (TAM corpus).

---

## 1. Motivation

The current skill exposes fixed commands (`top N`, `account NAME`, `whitespace`) built on a hand-cleaned set of derived CSVs in `pipeline/data/`. This is brittle in two ways:

1. **Lossy derivation.** The cleaning step silently drops columns. Concrete failure: a user asked for "top 10 EXL clients by revenue." The answer exists in the raw file `excel_data/20200803 PC-Strategy...xlsx` → sheet `Top Insurers and Brokers` → column **`2020-Rev Budget`** (populated for all 225 carriers, e.g. Hartford $18.4M, Zurich $16.4M). But that column never made it into `client_profiles.csv`, so the query returned "data not available." The system was wrong, not the data.
2. **Fixed surface.** Anything outside the pre-built commands can't be answered, even when the data supports it.

We want a layer that can ingest **any** file, understand its schema well enough to answer a **broad** range of questions — direct/calculative ("top 10 by revenue"), nuanced ("which clients look underpenetrated relative to their premium?"), and broad ("how is EXL positioned vs Genpact in commercial lines?") — and stay **grounded and cited** in the corpus, falling back to reasoning or web search only when the data genuinely can't answer.

The mechanism is **RAG over schemas, not over rows.** We do not embed cell contents. Instead, each table is represented by a compact, self-describing **Schema Card**. At query time the model scans the cards (cheap), selects the relevant tables, then issues real queries against just those tables.

---

## 2. Goals / Non-goals

### Goals
- **Universal intake.** Profile any `.xlsx/.xlsm/.csv/.tsv` (and best-effort `.docx/.pptx` tables) dropped into the corpus, without per-file hand-coding.
- **Schema Cards.** Produce one compact card per table: `schema + examples + reasoning description`.
- **Self-verifying cards.** Each card ships with a generated question set; a card is only "good" if those questions can be routed and answered using the card alone. Cards that fail get their description enriched.
- **Minimality.** Keep each card (schema + examples + description) as small as possible while passing verification. The full card set must be small enough to fit in a routing prompt.
- **Query router.** Given a free-text question, select the minimal set of relevant tables from the card index, generate and run a query plan, and return a **cited** answer.
- **Graceful fallback.** Classify each query as `calc` (computable from data), `reason` (synthesize across tables), `hybrid` (corpus + web/reasoning), or `unanswerable-from-corpus` (and say so, with what's missing).
- **No lossy middle layer.** Cards point at *raw source* tables. Derived CSVs may exist as a cache but are never the source of truth.

### Non-goals
- Not a vector DB / embeddings system. Retrieval is over card text, not cell embeddings.
- Not a NL-to-SQL product. Query execution can be pandas/duckdb; SQL is an implementation detail.
- Not a UI. CLI + library API only (the skill wraps it).
- No write-back to source spreadsheets.

---

## 3. Core concept: the Schema Card

A Schema Card describes one table at three increasing levels of abstraction, exactly as the design intends:

1. **Schema** (most concrete structure) — column names, types, roles, join keys.
2. **Examples** (concrete content) — a few representative rows.
3. **Description** (the middle layer, written as reasoning) — what the table *is for*, what questions it answers, what it deliberately does **not** contain. This is the layer the router reads first; it sits between raw schema and raw examples in abstraction.

### 3.1 Card data model (JSON)

```jsonc
{
  "table_id": "F1.top_insurers_and_brokers",      // stable id: <file_alias>.<slug>
  "title": "Top Insurers and Brokers",
  "source": {
    "file": "excel_data/20200803 PC-Strategy-Solution Development and GoToMarket PlanVer1.5.xlsx",
    "file_alias": "F1",
    "sheet": "Top Insurers and Brokers",
    "header_row": 6,                                // detected, not assumed
    "vintage": "2020-08"
  },
  "grain": "one row per insurer/broker group",
  "row_count": 225,
  "description": "Master carrier ranking. Each row is a US insurer or broker group. Pairs hard financials (2019 net written premium, YoY %, rank, combined ratio) with EXL relationship data (is-client flag, 2020 revenue budget per account, EXL share-of-wallet band, renewal timing, future TCV) and the buying committee (named CxOs). Use to size accounts, rank by premium OR by EXL revenue, find decision-makers, segment clients vs prospects, or spot under-penetrated accounts (high premium, low wallet share). The `2020-Rev Budget` column is the only per-account EXL revenue figure in the entire corpus. Does NOT contain: post-2020 revenue, actuals vs budget, contract/TCV dollar values (Future TCV is blank), or line-of-business splits.",
  "columns": [
    {"name": "Company/ Group", "type": "string", "role": "entity_key", "joins": ["F1.buyer_priorities.Company", "client_profiles.client_canonical"]},
    {"name": "NWP - 2019", "type": "currency_usd", "role": "measure", "note": "carrier net written premium, account size"},
    {"name": "2020-Rev Budget", "type": "currency_usd", "role": "measure", "note": "EXL planned revenue from this account; 0 for non-clients"},
    {"name": "EXL Client", "type": "enum", "role": "dimension", "values": ["Yes", null]},
    {"name": "EXL's Share of Wallet", "type": "enum", "role": "dimension", "values": ["Low","Medium","High", null], "note": "sparse: 7/225 populated"}
    // ... all remaining columns, terse
  ],
  "examples": [
    {"Company/ Group": "Hartford Ins Group", "NWP - 2019": 11871251000, "2020-Rev Budget": 18364859, "EXL Client": "Yes", "EXL's Share of Wallet": "Medium"},
    {"Company/ Group": "State Farm Group", "NWP - 2019": 65100455000, "2020-Rev Budget": 0, "EXL Client": null}
  ],
  "answerable": [
    {"q": "top 10 EXL clients by revenue", "route": "filter EXL Client=Yes, sort 2020-Rev Budget desc, head 10", "verified": true},
    {"q": "who is the CFO at Travelers", "route": "lookup row Company~Travelers, col CFO", "verified": true},
    {"q": "which clients are under-penetrated", "route": "EXL Client=Yes, high NWP-2019 + low/blank share-of-wallet", "verified": true}
  ],
  "not_answerable": [
    {"q": "EXL revenue from Allstate in 2023", "reason": "only 2020 budget present; no time series"},
    {"q": "contract TCV per client", "reason": "Future TCV Potential column is empty"}
  ],
  "quality": {"warnings": ["Future TCV 100% empty", "Share-of-Wallet 97% empty", "trailing whitespace in company names"]},
  "card_tokens": 480                                // measured size, for the minimality budget
}
```

### 3.2 Type vocabulary
`string, enum, int, float, currency_usd, percent, date, year, bool, id, freetext, url, name_person, name_company`. The profiler infers these; the authoring step can correct them.

### 3.3 Roles
`entity_key` (the grain / join key), `dimension` (filter/group-by), `measure` (sum/sort/avg), `attribute` (descriptive lookup), `meta` (source/audit, ignore for queries).

---

## 4. Pipeline A — Ingestion & card building

Run when a new/changed file appears. Idempotent; re-runnable.

**Stage 1 — Discover & split into tables.**
- Walk the corpus root. For each `.xlsx/.xlsm`, enumerate sheets; for each `.csv/.tsv`, one table. For `.docx/.pptx`, extract embedded tables (best-effort, flag low confidence).
- One sheet may contain multiple logical tables or a banner + table. **Detect the real header row** (don't assume row 1) by scanning for the row with the most non-empty, mostly-unique, string-typed cells followed by data rows. Record `header_row`.
- Skip non-data sheets (nav/home/reference) but still emit a stub card marked `role: "non_data"` so the router knows they exist and why they're skipped.

**Stage 2 — Profile each table.**
- Column names (de-duplicated, original preserved), inferred type, % null, distinct count, min/max/sample for measures, top-k values for enums/dimensions.
- Row count (excluding blanks).
- Detect join keys: columns whose values overlap heavily with entity keys in other tables (esp. company/client names). Use the existing `aliases.csv` to canonicalize company names when matching.
- Emit data-quality warnings (all-empty columns, broken VLOOKUP `#N/A`, Excel-epoch date artifacts, duplicated tables across files — see `INGEST_REPORT.md` for known cases).

**Stage 3 — Author the description + examples (LLM step).**
- Input: the profile + a sample of rows.
- Output: the **reasoning description** at middle abstraction. Rules:
  - State the grain in one clause.
  - Say what kinds of questions it answers, naming the key columns.
  - **Explicitly enumerate what it does NOT contain** (this is what prevents false "no data" answers AND false positives).
  - No marketing language; this is for a router, not a human reader.
- Select **2–3 example rows** that maximize coverage of the important columns (e.g. one populated EXL client + one non-client), not just the first rows.

**Stage 4 — Generate the question set.**
- LLM generates 8–15 candidate questions the table *should* be able to support, spanning: direct lookups, aggregations/rankings, filters/segments, and 1–2 deliberately out-of-scope questions (to populate `not_answerable`).

**Stage 5 — Verify & minimize (the heart of the system).**
For each candidate question:
  1. **Routing test:** given ONLY the card (schema + examples + description), can a model decide this table is relevant and produce a valid query plan against real columns? (binary)
  2. **Retrieval test:** execute the plan; does it return non-empty, plausible data?
- If a fair question fails routing → **enrich the description** (add the missing concept/synonym) and re-test. Do not enrich by dumping rows; add reasoning.
- If it fails retrieval because the data truly isn't there → move it to `not_answerable` with a reason.
- **Minimization:** after the card passes, attempt to *shrink* it — drop description sentences, trim examples, collapse column notes — and re-run verification. Keep the smallest card that still passes. Record `card_tokens`.
- Acceptance: a card is "verified" when ≥90% of in-scope questions pass routing+retrieval and all out-of-scope ones are correctly refused.

**Output:** `cards/<table_id>.json` per table, plus a consolidated `cards/index.json` (the routing index — id, title, grain, description, join keys, card_tokens only; NOT full schema) sized to fit one prompt.

---

## 5. Pipeline B — Query routing & answering

**Stage 1 — Classify.** Label the question: `calc | reason | hybrid | unanswerable`. (LLM, using `index.json`.)

**Stage 2 — Select tables.** Using `index.json` (descriptions + join keys), pick the minimal set of cards likely to contain the answer. Return ranked candidates with a one-line reason each (for transparency/citation).

**Stage 3 — Load full cards** for the selected tables only, and build a **query plan**: filters, joins (via detected keys + alias canonicalization), aggregations, sort/limit. Plan is data-engine-agnostic; reference implementation uses pandas or duckdb over the raw files (read live, header_row-aware).

**Stage 4 — Execute & verify.** Run the plan. Sanity-check the result (row counts, nulls, units). If empty/implausible, re-route (maybe wrong table) or downgrade to `reason`/`hybrid`.

**Stage 5 — Compose answer.**
- Grounded answer with **source citations** down to `file → sheet → column` (and row ids where relevant), matching the skill's existing citation contract.
- For `hybrid`: clearly separate corpus-grounded facts from web/reasoned additions; cite web sources separately.
- For `unanswerable`: say so plainly and name the missing column/table (e.g. "no post-2020 revenue in corpus"), and — critically — surface the *closest available* data (this is the behavior that would have caught the dropped-column bug: the router would see `2020-Rev Budget` in the card and never have said "no data").

---

## 6. CLI / API

```bash
# Pipeline A
schema-rag build [--root excel_data/] [--changed-only] [--file F1]
schema-rag verify [--table F1.top_insurers_and_brokers]   # re-run verification loop
schema-rag index                                          # rebuild cards/index.json

# Pipeline B
schema-rag ask "top 10 EXL clients by revenue" [--json] [--explain]
schema-rag route "..."        # show selected tables + reasons, no execution (debugging)
schema-rag plan "..."         # show the query plan, no execution
```

Library API mirrors the CLI: `build_cards()`, `verify_card()`, `route(question)`, `answer(question)`.

`--explain` emits: classification, tables selected + why, query plan, execution result, citations. This is the audit trail.

---

## 7. Repo layout

```
schema_rag/
  __init__.py
  intake.py        # Stage 1-2: discover, header detection, profile
  author.py        # Stage 3-4: description, examples, question gen (LLM)
  verify.py        # Stage 5: routing+retrieval test, minimize
  route.py         # Pipeline B Stage 1-2
  plan.py          # Stage 3: query plan builder
  execute.py       # Stage 4: pandas/duckdb runner (header_row-aware, live read)
  answer.py        # Stage 5: compose + cite
  types.py         # Card dataclasses / JSON schema
  cli.py
cards/
  index.json
  F1.top_insurers_and_brokers.json
  ...
tests/
  test_intake.py
  test_verify.py
  test_route.py
  regression/      # see §8
```

Cards are committed to the repo (reviewable diffs). Source files are read live; no derived CSV is treated as source of truth.

---

## 8. Acceptance criteria & tests

**Regression (must pass — these encode the bugs we found):**
- `ask "top 10 EXL clients by revenue"` returns the ranking from `2020-Rev Budget` with Hartford #1 (~$18.4M) and a $92.7M total across 22 clients — NOT "data not available."
- `ask "EXL revenue from <client> in 2024"` returns `unanswerable-from-corpus`, names the gap (no time series), and offers the 2020 budget figure as the closest available.
- Header detection picks row 6 (not row 1) for `Top Insurers and Brokers`.
- Duplicate tables (F1 `Competitor Analysis` == F5) are detected and the router prefers the canonical (F5) per `COVERAGE_AUDIT.md`.

**Unit:**
- Type inference, null/distinct profiling, join-key detection, alias canonicalization.
- Card minimization actually reduces `card_tokens` without dropping verified questions.

**System:**
- Every emitted card passes its own verification gate (≥90% in-scope routing+retrieval; 100% correct refusal of out-of-scope).
- `index.json` fits within a configurable token budget (default: routing index ≤ ~6k tokens for the full corpus).
- Determinism: same inputs → same cards (LLM steps seeded/cached; profiling fully deterministic).

---

## 9. Integration with `exl-sales-intelligence`

- The existing fixed commands (`top N`, `account NAME`, `whitespace`, `list_accounts`) stay as curated fast-paths.
- Add a new generic entrypoint: `ask "<free text>"` → Pipeline B.
- Migrate the fixed commands to *consume* cards rather than hardcoded CSVs, so they inherit any newly-surfaced columns automatically.
- The skill's output contract (source-cited, EXL product vocabulary, outcome-anchored) is preserved by the `answer.py` composer.

---

## 10. Phasing

1. **M1 — Intake + profiling** (`intake.py`, header detection, profiles) on the 5 `excel_data` files. Deliverable: profiles for all ~30 sheets.
2. **M2 — Cards + verification loop** (`author.py`, `verify.py`, minimization). Deliverable: verified card set + `index.json`.
3. **M3 — Router + executor + answer** (`route/plan/execute/answer`). Deliverable: `ask` passes all §8 regression tests.
4. **M4 — Hybrid + web fallback**, and migrate the legacy skill commands onto cards.
5. **M5 — Generalize intake** to docx/pptx tables and arbitrary dropped files.

---

## 11. Open questions

- LLM for the authoring/verification steps: which model, and do we cache by content hash to keep `build` cheap and deterministic?
- Query engine choice: pandas (simple, in-proc) vs duckdb (SQL, faster joins). Recommend duckdb reading xlsx/csv directly.
- Token budget for `index.json` as the corpus grows beyond the current 5 files — may need a two-stage coarse→fine route.
- How aggressive should minimization be? Define the stopping rule (e.g. stop when removing any item drops a verified question).
