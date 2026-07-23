---
name: tam-ingest
description: Ingest a new file into the corpus so it becomes queryable. Use when someone adds a spreadsheet (.xlsx/.xlsm/.csv), a presentation (.pptx/.pptm), or an image (.png/.jpg/…) and wants it usable for questions — "ingest this file", "add this data", "profile this workbook", "add this deck", "OCR this screenshot". Claude detects the file type, runs the profiler, and authors schema cards — one card per table for a spreadsheet (typed columns, examples), one deck card for a presentation (collective summary, a per-slide point, entities with why), or one image card (OCR transcript, summary, entities). Every card carries temporality: an as_of date plus whether it is stated in the source or inferred — down to each slide/datapoint. Then registers it in the card index.
---

# tam-ingest — turn any file into queryable, cited, dated corpus

**You know almost nothing about the file except its type.** Do not assume any
industry, company, product, or subject matter. Everything you write in a card MUST be
derivable from the file itself — its structure and its content. Never import outside
knowledge about "what this file probably is." The whole point is that this same procedure
works on a file no one has seen before.

The point is NOT "read everything" (any tool can dump content). The point is that when a
relevant question comes later, `tam-ask` can tell *which* source holds the answer and pull
*exactly* the right slice — cited and dated. The card is what makes that possible.

## Detect the file type first
- Spreadsheet — `.xlsx`, `.xlsm`, `.csv`, `.tsv` → **Track A** (one card per table).
- Presentation — `.pptx`, `.pptm` → **Track B** (one deck card; slides are the grain).
- Image — `.png`, `.jpg/.jpeg`, `.webp`, `.tif/.tiff`, `.bmp`, `.gif` → **Track C** (one image card; the file is the unit).

The profiler (`dump.py`) auto-detects the type and emits the right profile shape; you
choose which authoring track to follow from the extension. Everything else — aliasing,
vintage + temporality, normalizing entities, indexing, self-verify — is shared.

## Locating the package
Paths below are relative to the package root — the folder containing `.tam-root` (the working
directory in a repo). If not at the root, find it (`find . /mnt -maxdepth 4 -name .tam-root`)
and run from there, or set `TAM_ROOT`. Scripts resolve their own data paths regardless.

## Shared (OneDrive-synced) folders — nothing to coordinate
If this bundle is hosted in a SharePoint library synced to multiple people (see
`docs/SHAREPOINT_SETUP.md`), just ingest normally. New files land for everyone automatically
once OneDrive syncs — you don't push anything, and there is no lock to manage. `build_index.py`
regenerates `index.json` atomically and auto-cleans any OneDrive conflict copy, so even if two
people ingest close together the next rebuild self-heals. (`python3 code/tam/sync_check.py`
is an optional health check that just confirms the copy resolves and is writable.)

## Tools (repo-relative)
- Profiler:       `python3 code/tam/dump.py "<file>" --json produced_data/cards/_profiles/<alias>.profile.json`
- Card templates: `card.template.json` (table) · `deck.template.json` (deck) · `image.template.json` (image), under `code/tam/templates/`
- Normalizer:     `python3 code/tam/normalize.py --scan ... | --append ...`
- Index builder:  `python3 code/tam/build_index.py`
- Link detector:  `python3 code/tam/link.py`   (finds joins across TABLES by value overlap — no domain knowledge)
- Query (self-test): `python3 code/tam/query.py --spec <spec.json>`
- Dependencies: spreadsheets need `openpyxl`/`pandas`; presentations need `python-pptx`;
  images need `Pillow` and (for OCR) `pytesseract` + the `tesseract-ocr` binary
  (`pip install python-pptx pillow pytesseract`; `apt-get install -y tesseract-ocr`).
  Install on demand if a profile/query import fails. Images degrade gracefully: with no OCR
  engine you author the transcript from a direct visual read of the image.

## Shared steps (both tracks)

1. **Assign a file alias** — a short handle carrying no meaning. Use the `F` series for
   spreadsheets (`F9`, `F10`, …) and the `P` series for presentations (`P1`, `P2`, …), so the
   source type is obvious at a glance. Check existing aliases in `produced_data/cards/` first.

2. **Profile** the file with `dump.py --json produced_data/cards/_profiles/<alias>.profile.json`.
   The profile surfaces date candidates (`date_candidates` per slide, `meta_dates`/
   `content_date_candidates`/`filename_date_candidates` for images) — your raw material for
   temporality.

3. **Set the vintage (`as_of`) AND its basis — temporality is mandatory.** We always want to
   know the date of each datapoint and *how* we know it. From evidence in the file:
   - dates in the **filename** (e.g. `...Jun 2021...`, `20200803`, `Sep 2025`),
   - dates in **sheet/slide titles, headers, footers, or image metadata (EXIF/PNG chunks)**,
   - date **values** in the content (a column, a chart axis, OCR'd text).
   Set `source.as_of` to the most specific reliable one, and `source.as_of_basis` to:
   - `"stated"` — a date literally present in the file/filename/metadata,
   - `"inferred"` — deduced from context (say why in a warning),
   - `"unknown"` — no date found: set `as_of: null` and `as_of_basis: "unknown"`, add
     `"vintage_unknown"` to `warnings`, and note the owner should confirm.
   Never invent a date. Then date **each datapoint**, not just the document: Track B records a
   per-slide `as_of` + `as_of_basis`; Track C records `content_dates[]` (each with `basis`).
   (This is what lets every answer be dated, marked stated-vs-inferred, and flagged when stale.)

4. **Normalize entities:** run new entity names through `normalize.py --scan`. For names not
   yet mapped, `--append` a variant→canonical row so future joins/filters/mentions resolve to
   one account. (Track A: the `entity_key_col` values. Track B: the entity names you author.)

5. **Register:** run `build_index.py` (folds every card into `index.json`). For spreadsheets
   also run `link.py` first (adds `joins` between tables whose entity columns share values),
   then rebuild. Decks and images have no columns to join, so `link.py` skips them.

---

## Track A — spreadsheets (one card per table)

The profile gives you, per sheet: detected `header_row` (not assumed row 1), `two_row_header`,
columns (inferred type, role hint, null %, distinct, sample values), and `sample_rows` with
**real source row numbers**, plus anomaly flags (empty scaffold, near-duplicate column set).

A1. **Author one card per data table** → `produced_data/cards/<alias>.<slug>.json`
    (`slug` = sheet name lowercased, non-alphanumeric runs → single underscore).
    Use `card.template.json`, filled using ONLY the file:
    - `grain`: one clause describing what one row represents.
    - `summary`: 2–3 plain sentences on what the columns collectively represent and answer.
    - `use_cases`: 3–6 questions the columns can answer, phrased naturally (lookup,
      ranking/aggregation, filter/segment). These are what the router matches on.
    - `entity_key_col`: the column that best identifies each row, or null.
    - `columns`: every meaningful column with corrected `type` (use the samples: large plain
      numbers under a money header → `currency_usd`; a `%` column → `percent`; etc.) and `role`
      (`entity_key|dimension|measure|attribute|meta`). Terse `note` only when non-obvious.
      Leave `joins` empty — the link detector fills them.
    - `examples`: pick **2–3 rows structurally** — one fully-populated, one sparse/edge — copied
      from the profile `sample_rows` (keep `_source_row`). Never pick rows by their content.
    - `not_answerable`: 1–3 questions the table cannot answer, each with the reason (a missing
      column, no time series, an all-empty field).
    - carry `header_row`, `two_row_header`, `duplicate_of`, and `warnings` from the profile.

A2. **Non-data sheets** (nav/home/reference/empty scaffold; profile `role != "data"` or
    near-zero rows): write a minimal stub card with `"role": "non_data"` and a one-line reason.
    Still set `as_of`.

A3. **Duplicates:** if the profiler flags two sheets with the same column set, keep the one
    with more populated rows/columns as canonical and set `duplicate_of` on the other.

A4. **Self-verify** each data card: for every `use_case`, confirm `query.py` returns non-empty,
    plausible rows against real columns. If a fair question fails, enrich the card's summary/
    use_cases (add the missing concept) and retry — do not fix it by dumping rows.

---

## Track B — presentations (one deck card; slides are the grain)

A deck can't be sliced with SQL, so it gets a different card. The profile gives you, per
**slide** (1-based `slide` number = the provenance unit): `title`, `bullets` (every text line,
including table cells), `n_tables`/`tables`, `notes` (speaker notes), `n_images`, `char_count`
— plus `entity_hints`: a deterministic, frequency-ranked list of capitalized phrases and the
slides they appear on. **Hints are raw material, not answers** — you decide which are real
entities, normalize them, and write the reason each matters.

Author **one deck card** → `produced_data/cards/<alias>.deck.json` using
`deck.template.json`, filled using ONLY the slides:

B1. **`summary` — the collective read.** 3–6 plain sentences: what the whole deck is, its
    purpose / narrative arc, and what it collectively covers. This is the file-level summary a
    reader gets "after a read." Describe the deck as it is; don't editorialize beyond the slides.

B2. **`slides[]` — one point per slide, each dated.** For every slide, one sentence in `point`
    capturing what that slide contains or asserts (`title` = its heading or null). Keep it
    faithful and specific enough that "which slide covers X?" resolves to the right `slide`
    number — this is what makes a single slide individually retrievable. Set `has_table`/
    `has_notes` from the profile. Also set the slide's **temporality**: `as_of` = the date that
    slide's datapoints refer to (use its `date_candidates` from the profile), and `as_of_basis`
    = `stated` (a date on the slide) / `inferred` (from context) / `inherited` (no slide-level
    date — falls back to the deck vintage) / `unknown`. Cover **every** slide, in order.

B3. **`entities[]` — who/what and why.** Curate the real entities mentioned (companies,
    people, products/solutions, places, metrics). Skip section labels and generic words the
    hints will surface. For each: `name` (normalized via `normalize.py`), `type`, `slides` (the
    slide numbers it appears on), and `why` — a short line on why it appears in THIS deck / its
    role in the narrative. This is the deck's mention-index.

B4. **`use_cases`:** 3–6 questions this deck is the right source for — e.g. "what does the deck
    say about <topic>?", "which slide covers <topic>?", "who/what is mentioned and why?". These
    are what the router matches on.

B5. **`not_answerable`:** 1–3 things the deck can't answer (no numbers behind a claim, a topic
    absent, an image-only slide with no extractable text), each with the reason.

B6. **Self-verify** the deck card with the query.py deck spec:
    - by slide: `{"deck_id":"<alias>.deck","slides":[N],"fields":["title","text"]}` returns that
      slide's real text and its `as_of`/`as_of_basis`.
    - by entity: `{"deck_id":"<alias>.deck","entity":"<a name you authored>"}` returns the
      slides you listed for it (non-empty).
    - by text: `{"deck_id":"<alias>.deck","contains":"<a term on a slide>"}` finds it.
    If a fair retrieval misses, fix the slide `point` / entity `slides` so it resolves — the
    card must agree with the file.

---

## Track C — images (one image card; the file is the unit)

An image (chart, screenshot, scanned page, diagram) has no rows or slides, so it gets one
card and the whole file is the provenance unit. The profile gives you: `width`/`height`/
`format`, `ocr_text` (if a tesseract engine is available, else null), `meta_dates` (EXIF /
PNG-chunk dates — stated), and date candidates from OCR / filename / metadata. **OCR is a
starting point, not the authority** — you are multimodal, so **open the image with the Read
tool and look at it** to author an accurate summary, transcript, and entities. OCR is a
cross-check, especially for charts and low-quality scans.

Author **one image card** → `produced_data/cards/<alias>.image.json` (I-series alias) using
`image.template.json`, filled using ONLY the image:

C1. **`summary`:** 3–6 plain sentences on what the image shows and what it is for — written
    after a direct visual read, not just from OCR.

C2. **`transcript`:** the text visible in the image, verbatim-ish (OCR cross-checked by your
    read). For a chart, transcribe axis labels, series names, and any printed values. This is
    the grounded artifact `query.py` returns, so it must be faithful.

C3. **`entities[]`:** the real entities depicted (companies, people, products, metrics), each
    with a normalized `name` (via `normalize.py`), `type`, and `why` it appears.

C4. **`content_dates[]` — temporality of the datapoints.** For every date the image asserts
    about its data (a time axis, a footer "as of", a labeled year), record `{value, basis,
    note}` where `basis` is `stated` (printed on the image or in metadata) or `inferred`. Set
    `source.as_of`/`as_of_basis` from the most representative of these (prefer stated).

C5. **`use_cases`** (3–6 questions this image answers) and **`not_answerable`** (things absent
    or illegible), as usual.

C6. **Self-verify** with the query.py image spec:
    `{"image_id":"<alias>.image","fields":["summary","transcript","content_dates"]}` returns
    the grounded transcript + temporality; `{"image_id":"<alias>.image","contains":"<a term you
    transcribed>"}` reports `matched: true`. If a term you can see isn't in the transcript, the
    transcript is incomplete — fix it.

---

## Determinism expectation
Re-ingesting the same file must produce a stable card. The profiler is fully deterministic
(same sheets/columns/samples for a spreadsheet; same slides/text/entity_hints for a deck;
same dimensions/OCR/metadata for an image — OCR text is stable for a given engine version);
keep authored text faithful to the source so two runs agree — same grain/columns/entity_key
for a table, same per-slide points and entity set for a deck, same transcript/entities for an
image. Temporality is part of that: the same dates, with the same stated-vs-inferred basis.
