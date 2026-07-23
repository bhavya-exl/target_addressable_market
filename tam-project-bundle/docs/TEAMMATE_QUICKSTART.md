# Quickstart (for anyone joining the TAM corpus)

Two things: get the data (SharePoint), and make sure the skills are on. ~5 minutes.

## 1. Get the data — sync the folder

1. Open the site link you were sent (TargetAddressableMarket → Shared Documents).
2. Click **Sync**. Approve the OneDrive prompt.
3. The `tam-project-bundle` folder now appears on your computer (Finder/Explorer).
4. <b>Important — do this once:</b> right-click the <b>tam-project-bundle</b> folder in Finder and choose <b>“Always keep on this device.”</b> This downloads the data files so they’re always ready (it’s only ~2&nbsp;MB). Skip this and Claude may stall on a “cloud-only” file.

## 2. Open it in Claude

1. Open the **Claude desktop app**.
2. Open/connect that synced `tam-project-bundle` folder as your working folder.
3. Claude greets you with what's available (skills + a data summary). That's your home base.

## 3. Turn the skills on

- Go to **Customize → Skills**. You should see **tam-catalog, tam-ask, tam-report,
  tam-ingest** (your org owner provisioned them). Toggle them on if they aren't already.
- If you don't see them, ask your owner to provision them, or upload the `.skill` files
  yourself via **Customize → Skills → "+" → Create skill → Upload a skill**.
- (Skills need **code execution** enabled — on by default for the org.)

## 4. Try it

Ask, in plain language:
- "What data do we have here?"  → an overview of every document (tam-catalog)
- "Top 10 EXL clients by revenue" → a cited, dated answer (tam-ask)
- "Chart competitor footprint across our accounts" → a visual (tam-report)

## Adding your own

Found yourself asking the same thing a lot? Say: "save this as a reusable skill called X."
Claude writes it and rebuilds the catalog; then upload/share it (or ask your owner to
provision it) so the team gets it. See `docs/ADDING_SKILLS.md`.

To add new data: drop a spreadsheet in `input_data/corpus/` and say "ingest this file."
