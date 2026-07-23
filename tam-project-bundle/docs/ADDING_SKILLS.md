# Adding your own skills (the same way you add documents)

Skills live in `.claude/skills/` **inside this synced folder**. That means a new skill is
shared exactly like a new spreadsheet: once it's in the folder, OneDrive syncs it to everyone,
and anyone who opens the bundle in Claude can use it. No installs, no admin step.

## When to make a skill

Make one when you notice you keep asking for the **same shape of thing** — a report you
rebuild every month, a specific way you like accounts summarized, a data pull you repeat.
Turning it into a skill means you (and the team) get it in one phrase next time, done the same
way every time.

Examples worth saving:
- "Build the monthly top-25 EXL clients chart with revenue and competitor overlay."
- "Give me a one-page account brief in *this* layout for any carrier."
- "List every source that's more than 18 months old, grouped by owner."

## Check what already exists first

Before making a skill, see what's already there so you don't build a duplicate. Just ask:

> "What skills are available here?"

The main skill reads the catalog (`produced_data/skills_catalog.json`) and lists each skill
and what it does. If one nearly fits, extend it instead of adding a near-copy. Very specific
skills are fine — overlapping ones are what we avoid.

## How to make one (the easy way — just ask Claude)

You don't hand-write files. When you've just gotten an answer or report you'd want to repeat,
say:

> "Save this as a reusable skill called **monthly-top-clients**."

Claude will write a `SKILL.md` into `.claude/skills/monthly-top-clients/` in this folder,
following the template in `docs/skill_template.md`, and refresh the catalog
(`python3 code/tam/build_skill_index.py`) so the new skill shows up in discovery. On the next
OneDrive sync, everyone has it.
To use it later, anyone just asks in plain language (or types `/monthly-top-clients` if their
Claude supports slash commands).

To tweak a skill later: "update the **monthly-top-clients** skill so it also includes L&A
clients." To remove one: delete its folder under `.claude/skills/` (it stops being offered on
the next sync).

## Two homes for a skill (important)

A skill lives in two places, and it needs both:

1. **The file** in `.claude/skills/<name>/` — this is what syncs to the team via SharePoint.
   Claude writes/edits it for you and rebuilds the catalog.
2. **Registered in the Claude app** — dropping the file in the folder is NOT enough to run it
   in the desktop app. It also has to be under **Customize → Skills**. The clean way for a
   team: an owner uploads/shares or org-provisions the skill once, and everyone gets it (and
   auto-gets updates). Otherwise each person uploads the skill's `.skill`/ZIP themselves.

So the flow is: repeat a request → ask Claude to save it as a skill (it writes the file +
rebuilds the catalog) → upload/share it once via Customize → Skills → the team has it.

## The one rule that keeps skills trustworthy

Every data skill must **go through the cards and `query.py`** — the same grounded path
`tam-ask` uses (read `index.json` -> pick table(s) -> run a query spec -> cite + date the
result). A skill should never answer from memory or read a spreadsheet the cards don't
describe. This is what keeps answers cited, dated, and correct. The template reminds the
author to route through the engine.

## Two things to keep it tidy as skills grow

- **Give each skill a sharp one-line `description`.** Claude uses these descriptions to decide
  when to trigger a skill, so a vague one causes the wrong skill to fire. Be specific about
  *when* to use it.
- **One skill per repeated job, not per question.** If two skills do nearly the same thing,
  merge them. A handful of well-named skills beats dozens of near-duplicates.

## Note on where skills show up

In the shared-folder setup, skills in `.claude/skills/` are available wherever this bundle is
opened as the working folder. If your team also runs this as a claude.ai **Project**, add the
skill folders under Settings -> Capabilities as well (see `docs/PROJECT_SETUP.md`) — same
files, just registered in that interface.
