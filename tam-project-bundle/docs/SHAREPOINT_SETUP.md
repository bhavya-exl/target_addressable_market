# Sharing the TAM bundle over SharePoint (OneDrive-synced)

Goal: when **anyone** ingests a spreadsheet, the new file *and* its generated cards/index
become available to **everyone** using the folder — automatically.

## How the sharing actually works (read this first)

The Microsoft connector Claude uses is **read-only** for SharePoint — it can search and
read files, but it cannot upload. So the sharing is **not** done by Claude pushing files
up. Instead:

> The bundle lives inside a **SharePoint document library**, and each teammate **syncs that
> library to their computer with the OneDrive client**. To each person it looks like an
> ordinary local folder. When one person ingests a file, `tam-ingest` writes into that
> synced folder exactly as always — and **OneDrive propagates the changes to everyone**.

Nothing about the engine changes. The OneDrive sync client is the transport. The read-only
connector is a bonus (Claude can still *search* SharePoint), not the mechanism.

```
   Bhavya ingests a file
        │  writes new .xlsx + cards + index.json into the synced folder
        ▼
   SharePoint document library  ──OneDrive sync──►  every teammate's local copy
   (single source of truth)                          (auto-updated)
```

## One-time setup (owner)

1. **Create or pick a SharePoint site + document library.** Use a Team or private site so
   access stays inside EXL (this corpus is internal competitive intelligence). A dedicated
   library such as **"EXL TAM Intelligence"** keeps permissions clean.
2. **Set the library's members** to the people who should query/ingest. Give them
   **Edit** (not just Read) — they need to write cards back when they ingest.
3. **Upload the whole `tam-project-bundle/` folder into the library, structure intact.**
   The tree must stay together — the engine finds everything from the `.tam-root` marker at
   the top. Do not flatten or rename folders (see "load-bearing" in the root `README.md`).
4. **Sync the library to your machine:** in the library, click **Sync** → it opens in the
   OneDrive client and appears under something like
   `…/EXL Service - <Site> - <Library>/tam-project-bundle/`.
5. **Point work at the synced copy.** Run the engine from that synced path. If auto-detection
   ever fails, set `TAM_ROOT` to the synced bundle's top folder:
   - Windows: `setx TAM_ROOT "C:\Users\<you>\EXL Service\EXL TAM Intelligence\tam-project-bundle"`
   - macOS: add `export TAM_ROOT="/Users/<you>/Library/CloudStorage/OneDrive-EXL/.../tam-project-bundle"` to your shell profile.
6. **Smoke-test:** `python3 code/tam/sync_check.py` should print the synced root, `Writable: yes`,
   and a "likely yes" for the synced-share check. Then run the two golden queries from
   `docs/PROJECT_SETUP.md` (Hartford #1; Travelers competitors).

## Keep the data downloaded (one right-click)

On macOS/Windows, OneDrive keeps synced files as cloud-only placeholders by default, which can
make the engine stall when it reads a spreadsheet. Fix it once: right-click the synced
`tam-project-bundle` folder and choose **"Always keep on this device."** All data files (~2 MB
total) download and stay local, and new files added later download automatically. Each person
does this once on their machine after syncing.

## Onboarding each new teammate

1. Grant them **Edit** access to the library.
2. They open the library → **Sync** → wait for OneDrive to finish downloading.
3. `python3 code/tam/sync_check.py` to confirm their copy resolves and is writable.
4. They can now query (`tam-ask`), report (`tam-report`), and ingest (`tam-ingest`).

## Ingesting on a shared folder — nothing to manage

Just ingest normally. There is **no lock and no coordination step** — for anyone. The only
file everyone rewrites is `index.json`, and it is fully derived from the cards, so
`build_index.py` simply regenerates it every time: it writes atomically (readers never see a
half-written file) and auto-deletes any OneDrive "conflicted copy" before writing. If two
people happen to ingest close together, the next rebuild self-heals. No one thinks about this.

## Propagation & conflicts — what to expect

- **Speed:** OneDrive syncs within seconds to a few minutes depending on file size and
  network. Card/index files are small; the source spreadsheets are the slowest part.
- **Conflicts:** handled automatically. `index.json` is regenerated from the cards, and any
  stray `*conflicted copy*` of it is cleaned up on the next rebuild — nothing to do by hand.
  (Cards are one file per table, so they rarely collide in the first place.)
- **Offline:** ingests done offline sync when the machine reconnects.

## Confidentiality

Keep the library and its membership inside EXL (Team/private site, Edit limited to the corpus
team). Never move it to a public or externally-shared location. Same rule as the claude.ai
Project route in `PROJECT_SETUP.md`.

## Why not have Claude push to SharePoint directly?

The connector has no upload/write capability today (write actions are "gated"). If IT later
enables SharePoint write on the connector, a push-on-ingest step could be added — but the
OneDrive-sync approach above needs no such access and is the recommended setup.
