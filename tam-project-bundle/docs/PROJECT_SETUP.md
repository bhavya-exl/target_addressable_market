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
This writes `dist/tam-project-bundle.zip` — skills + engine + cards + alias map + the
`.tam-root` marker + **only the source spreadsheets the cards actually reference**
(derived from the cards, so nothing extra ships).

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

**3 — Add the Skills.** In Settings → Capabilities → **Skills**, add the three skill folders
from the bundle (`.claude/skills/tam-ingest`, `tam-ask`, `tam-report`) as org Skills, per the
current claude.ai Skills upload flow. (If your workspace supports Project-scoped skills, add
them to the Project instead.)

**4 — Enable code execution** for the Project (the skills run Python).

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
