# TAM Intelligence — how to work in this folder

This folder is the EXL TAM Intelligence corpus: data + engine + skills. Whenever you (Claude)
start a session here, do the ORIENTATION below first, then handle the user's request.

## Start every session by surfacing skills + data (do this first)

Before answering the first request, show a short "what's here" panel — this is how everyone
sees the available skills and how to add/update them:

1. **Available skills.** Read `produced_data/skills_catalog.json` and list each skill as
   `name — one-line description`. Then, in one line, how to change them:
   > "To add or update a skill: tell me a workflow you repeat and I'll write/edit it in
   > `.claude/skills/` and rebuild the catalog. To make it usable in the Claude app it must
   > also be uploaded or org-provisioned under Customize → Skills — see docs/ADDING_SKILLS.md."
2. **What data is here.** Read `produced_data/cards/index.json`; give a one-liner
   (N tables + N presentation decks across N documents; newest & oldest vintage). Offer the
   full breakdown via the `tam-catalog` skill.
3. **Offer next steps:** ask a question (`tam-ask`), build a report (`tam-report`), add data or
   a deck (`tam-ingest`), or add/update a skill.

Keep the panel tight (a few lines). Show it once at the start of a session, not on every turn.
If the user opened with a specific request, show the panel briefly, then do the request.

## Rules when working here

- **Stay grounded.** Answer corpus questions only through the cards + `code/tam/query.py`
  (route → query → cite → date). Never from memory; never read a spreadsheet the cards don't
  describe.
- **After adding, editing, or removing a skill:** run `python3 code/tam/build_skill_index.py`.
- **After ingesting data:** run `python3 code/tam/build_index.py`.
- **Skills live in two places.** The file lives in `.claude/skills/` (shared via the synced
  folder); to actually run in the desktop app it must be registered under Customize → Skills
  (upload or org-provision). Remind the user whenever they create one.
- **No manual locks.** The index rebuild is self-healing; never reintroduce a lock step.

## Layout
`.tam-root` marks the package root. `code/tam/` = engine, `produced_data/cards/` = schema
cards + `index.json`, `produced_data/skills_catalog.json` = skill catalog,
`.claude/skills/` = the skills, `input_data/corpus/` = source spreadsheets, `docs/` = guides
(START: README.md, ADDING_SKILLS.md, SHAREPOINT_SETUP.md).
