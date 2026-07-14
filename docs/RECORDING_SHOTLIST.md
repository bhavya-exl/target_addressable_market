# TAM Intelligence — Screen-Recording Shot List

Capture these as **separate clips** (not one long take). Separate clips let you redo one
without redoing all of them, and let me time narration to each. **Name each file by its clip
number** (e.g. `clip2_ingest.mov`) when you send them back.

There are **7 required clips + 1 optional**. Total raw footage ~3–4 min; the final cut lands
at ~2:30. Record a little extra head/tail on each (start recording ~1s before you act, stop
~1s after) so I have room to trim.

## Global setup (once, before any clip)
- Open the shared **claude.ai Project**, signed in, Skills on.
- Full-screen browser, bookmarks bar hidden, page zoom ~110–125%.
- Start a **fresh chat** for the Q&A clips so the transcript is clean.
- Recorder: macOS Cmd-Shift-5 → record the browser window. Mic optional (I'm scripting the VO
  separately, so you don't need to talk while recording).

---

## Clip 1 — The problem (B-roll, ~12s)
**Goal:** show the sprawl the tool replaces.
**Steps:**
1. Open the Project's **file list** (or a Finder window of the raw spreadsheets folder).
2. Slowly scroll through the workbooks / tabs. Hover over a couple to show the variety.
**Make sure the recording shows:** the sheer number of files/sheets. No typing.

---

## Clip 2 — Ingest a file from scratch (HERO, ~40s)
**Goal:** prove it turns a raw spreadsheet into queryable data with zero hardcoding.
**Prep (optional but nice):** have a copy of the **P&C Insurance Directory** `.xlsx` ready on
your desktop (it's inside your downloaded bundle under `input_data/`).
**Steps:**
1. In the chat, either **drag that `.xlsx` into the message** (cleanest — you see it drop in),
   or skip the drag and just reference it by name.
2. Type this prompt **verbatim**:
   ```
   Ingest this spreadsheet from scratch, and show me each step as you profile it, build the schema cards, and learn the company-name variants.
   ```
3. Let it run to completion. **Don't rush** — let the on-screen work (profiling, writing cards,
   the name variants it learns) stay visible for a beat.
**Make sure the recording shows:** the commands running, cards being created, and especially any
**name-normalization** it surfaces (e.g. AMIG → American Modern, IAG → Insurance Australia
Group). That's the "it's really reading the data" moment.

---

## Clip 3 — Direct question (~20s)
**Goal:** grounded, cited, dated answer.
**Steps:**
1. New line in the chat. Type **verbatim**:
   ```
   Top 10 EXL clients by revenue.
   ```
2. Let the full answer render — the table **and** the "Source: … as of Aug 2020" line at the bottom.
**Make sure the recording shows:** the ranked table AND the citation/date line (don't cut before
the source line appears).

---

## Clip 4 — Reasoning question (~25s)
**Goal:** it reasons across sheets, not just one lookup.
**Steps:**
1. Type **verbatim**:
   ```
   Where is Cognizant competing against us, and at which accounts?
   ```
2. Let the full answer render, including its sources.
**Make sure the recording shows:** the synthesized answer and the citations.

---

## Clip 5 — Name normalization (OPTIONAL, ~10s)  *(first to cut if short on time)*
**Goal:** it understands how reps actually type.
**Steps:**
1. Type **verbatim**:
   ```
   What's our position at TRV?
   ```
2. Show that it resolves "TRV" to Travelers and answers normally.
**Make sure the recording shows:** that "TRV" was understood as Travelers.

---

## Clip 6 — Turn an answer into a deliverable (~25s)
**Goal:** question → client-ready artifact in one step.
**Steps:**
1. Type **verbatim**:
   ```
   Turn the top-10 clients into a one-page brief I can bring to the account team.
   ```
2. Let `tam-report` build the brief/chart. Scroll so the finished artifact is fully visible.
**Make sure the recording shows:** the finished brief/chart, ideally with a visible date/source.

---

## Clip 7 — Trust spotlight (~10s)
**Goal:** the "honest by design" close — cited + dated + refresh nudge.
**Steps:**
1. Scroll back to the **Top-10 answer** (or the Cognizant one).
2. Slowly move the cursor to / select the **"as of Aug 2020 — worth refreshing"** line and the
   **Source:** citation. Linger on it.
**Make sure the recording shows:** the date, the source citation, and the refresh nudge, held
still long enough to read.

---

## Clip 8 — How a rep gets it (~12s)
**Goal:** no install — open and ask.
**Steps:**
1. Go to the **Project home** (or open a brand-new chat inside the Project).
2. Show the empty prompt box, ready for a question. Optionally type the first few words of a
   question and stop.
**Make sure the recording shows:** that this is a shared workspace a rep just opens and types into.

---

## When you're done
Send me the clips (or, if the files are large, just tell me the **final duration of each clip**
and confirm which optional ones you kept). I'll return:
- word-for-word **narration timed to each clip**,
- **on-screen captions/titles**,
- an **edit/assembly sheet** (order, trims, pacing) for CapCut / Descript / Premiere.
