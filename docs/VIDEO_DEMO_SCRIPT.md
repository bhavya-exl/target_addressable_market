# TAM Intelligence — Live Demo Script (leadership, ~2:30, screen recording)

**Audience:** EXL leadership / decision-makers (buy-in).
**Format:** live screen recording of the real claude.ai Project — no edited effects required.
**Runtime target:** 2:00–2:45.
**Core message for this audience:** *This turns EXL's scattered insurance market data into a
single thing a rep can ask — grounded, cited, and dated — and it keeps working on every new
file the business produces, with no engineering.*

The narration lines are a **guide, not a teleprompter** — speak them naturally in your own
words. What must stay exact are the **prompts you type** (copy them verbatim so the answers
land the way we tested).

---

## Pre-flight checklist (do this before you hit record)

- [ ] Open the shared **claude.ai Project** ("EXL TAM Intelligence"), signed in.
- [ ] Confirm the three Skills are on (Customize → Skills shows `tam-ingest`, `tam-ask`, `tam-report`).
- [ ] Have the **"new" spreadsheet for the ingestion beat** on your desktop, ready to drag in.
      (Ask me to generate a clean demo file for this — see "The ingestion beat" note below.)
- [ ] Start a **fresh chat** in the Project so the transcript is clean.
- [ ] Browser: full-screen, hide the bookmarks bar, close noisy tabs. Zoom the page to ~110–125%
      so text is readable in the recording.
- [ ] Do **one silent rehearsal run** end-to-end, especially the ingestion beat, so timing/latency
      hold no surprises on the real take.
- [ ] Screen recorder ready (macOS: Cmd-Shift-5 → record selected window). Mic checked.

---

## Run of show

### Beat 1 — The problem (~15s)
**On screen:** Show the Project's file list (the stack of workbooks), or a Finder window of the
raw spreadsheets. Slow scroll.
**Say:** *"This is how EXL's insurance market intelligence lives today — a dozen workbooks,
scattered tabs, and a lot of it in people's heads. Here's what happens when a rep can just ask
it a question instead."*

### Beat 2 — Extensibility: it understands any new file (~30s)  ⭐ hero moment
**On screen:** Drag the new spreadsheet into the chat. Type:
```
Ingest this file into the corpus.
```
Let `tam-ingest` run — it profiles the workbook, writes schema cards, dates it, learns the name
variants.
**Say:** *"I'm dropping in a file the system has never seen. It doesn't know anything about it —
only that it's a spreadsheet. It figures out the structure on its own, works out how recent the
data is, learns how the company names are written, and makes it queryable. That means every new
dataset the business produces becomes searchable the day it's created — no engineering ticket,
no schema project."*

### Beat 3 — A direct question, grounded and dated (~20s)
**On screen:** Type:
```
Top 10 EXL clients by revenue.
```
**Say:** *"Now a straight question. Notice it doesn't answer from memory — it pulls the actual
rows, and every number is cited back to the source file, and stamped 'as of August 2020.' You
always know exactly where a figure came from and how old it is."*

### Beat 4 — A reasoning question across the data (~25s)
**On screen:** Type:
```
Where is Cognizant competing against us, and at which accounts?
```
**Say:** *"This one isn't a lookup — it has to reason across several sheets to pull our
competitive picture together. This is the difference between a search box and an analyst: it
connects the client data to the competitive data and gives a rep something they can actually walk
into a meeting with."*

### Beat 5 — It speaks the way reps do (~10s, optional — cut first if short on time)
**On screen:** Type:
```
What's our position at TRV?
```
**Say:** *"A rep types 'TRV' — it knows that's Travelers. It normalizes the messy ways people
write company names, so nobody has to know the 'official' spelling to get an answer."*

### Beat 6 — Turn an answer into a deliverable (~20s)
**On screen:** Type:
```
Turn the top-10 clients into a one-page brief I can bring to the account team.
```
Let `tam-report` build the chart/brief.
**Say:** *"And it doesn't stop at an answer. Ask for a brief or a chart and it builds one — every
figure still traced to the source and dated. A rep goes from question to a client-ready page in
one step."*

### Beat 7 — The trust close: never stale, never made up (~15s)  ⭐ leadership hook
**On screen:** Scroll to / point at the *"as of Aug 2020 — worth refreshing"* line in any answer.
**Say:** *"Two things make this safe to put in front of clients. It never invents a number — if
the data can't answer, it says so. And it never lets old data pass as current: it always tells
you the date, and when data gets stale it flags the owner to refresh it. It's honest by design."*

### Beat 8 — How a rep gets it (~15s)
**On screen:** Show the shared Project home / the "open and start a chat" view.
**Say:** *"For the rep, there's nothing to install. They open this shared workspace and ask. The
whole thing is packaged so it travels with the data — as we add files, or roll this out to more
teams, it just comes along. This is EXL's market intelligence, on tap."*

---

## The ingestion beat (Beat 2) — make it safe on camera

Beat 2 is the strongest moment for a leadership audience (it's the "this keeps paying off"
argument), but it's the one live step with the most moving parts. To de-risk:

1. **Use a small, clean, genuinely-new file** so ingestion runs fast and produces a tidy card on
   screen. Ask me to generate one — a compact, realistic carrier/market spreadsheet the corpus
   has never seen — and I'll send it to you to drop in.
2. **Rehearse it once** before the real take so you know the latency.
3. **Fallback if it runs long live:** record Beat 2 separately, or open with beats 3–8 (the Q&A)
   and show ingestion at the end. The script works in either order.

## After you record
- Keep it raw for an internal leadership share — authenticity ("it actually works, live") is the
  point for this audience.
- If you later want a polished cut with captions/titles for a wider roll-out, tell me and I'll
  write the edit script and on-screen text.
