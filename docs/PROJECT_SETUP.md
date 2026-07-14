# Sharing the TAM system as a claude.ai Project (option 2)

Goal: let sales reps who live in **claude.ai** (not a repo) ask the corpus questions.
They get a shared **Project** that holds the data + engine + cards, plus the three
**Skills**. Claude runs the bundled scripts via code execution and answers — grounded,
cited, dated — exactly as in the repo.

## Prerequisites
- A **Team or Enterprise** claude.ai workspace (org Skills + code execution + Projects).
- Admin access to add Skills and create a shared Project.

## One-time setup

**1 — Build the bundle** (from the repo):
```
python3 code/tam/package.py
```
This writes:
- `dist/tam-project-bundle.zip` — the Project files (engine + cards + alias map + `.tam-root`
  marker + **only the source spreadsheets the cards reference**), and
- `dist/skills/{tam-ingest,tam-ask,tam-report}.zip` — three upload-ready Skill files (each is
  a zip containing its `SKILL.md`, which is the format claude.ai wants).

**2 — Create the Project.** In claude.ai → Projects → new Project (e.g. "EXL TAM Intelligence").
Upload the **unzipped** bundle into the Project's files, keeping the folder structure intact.
The tree must stay together — the `.tam-root` marker at the top is how the engine finds
everything:
```
tam-project-bundle/
  .tam-root
  code/tam/…            produced_data/cards/…        produced_data/pipeline/data/aliases.csv
  input_data/…          .claude/skills/…             docs/…
```

**3 — Turn on Skills for the org.** In **Organization settings → Skills**, toggle on both
**"Code execution and file creation"** and **"Skills."** Then **upload** the three files
`dist/skills/tam-ingest.zip`, `tam-ask.zip`, `tam-report.zip` (one at a time). Uploaded via
org settings, they become available to everyone under **Customize → Skills** — reps never
upload anything themselves.
(Single user on Pro/Max instead: Settings → Capabilities → enable code execution, then
Settings → Capabilities → Skills → upload the same three zips.)

**4 — Confirm code execution is on** for the workspace/Project (the skills run Python).
Requires a Pro, Max, Team, or Enterprise plan.

**5 — Smoke-test.** In the Project, ask:
- *"Top 10 EXL clients by revenue"* → Hartford #1 (~$18.4M), **as of Aug 2020**, cited to `F1`.
- *"What's our competitive situation at Travelers?"* → Cognizant/Genpact/WNS footprint, **as of Feb 2021**, cited to `F5`.
If those return dated, cited answers, the Project is live.

## How paths resolve (why it "just works")
Every engine script calls `resolve_root()` (in `code/tam/tam_root.py`), which finds the
package by locating the `.tam-root` marker — from the working directory, from the script
location, or from common upload mounts. If auto-detection ever fails, set an environment
variable **`TAM_ROOT`** to the bundle's top folder and it's used directly.

## Updating the data
Re-ingest changed/new files in the repo with `tam-ingest`, re-run `python3 code/tam/package.py`,
and re-upload the new zip to the Project. (The staleness report,
`produced_data/reports/STALENESS.md`, tells you which sources are overdue.)

## Confidentiality
The corpus is internal EXL competitive intelligence. Keep the Project and Skills inside the
org (Team/Enterprise workspace); never publish them publicly.
