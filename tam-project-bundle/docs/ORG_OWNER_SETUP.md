# One-time setup for the org owner

Do this once so the whole team can use the TAM corpus. ~15 minutes. You need to be a
Team/Enterprise **owner** for the skill steps.

## A. Turn on the foundations (Organization settings → Skills)

1. Go to **Organization settings → Skills** (claude.ai/admin-settings/skills).
2. Enable **Code execution and file creation**.
3. Enable **Skills**.
4. Enable **Skill sharing** (and/or **Share with organization**) so skills can be provisioned
   to everyone.

## B. Provision the four skills to everyone

You have the four `.skill` files (tam-catalog, tam-ask, tam-report, tam-ingest). Provision
them once and they appear in every member's Skills list automatically — and when a skill is
updated later, members get the new version automatically.

1. In **Organization settings → Skills**, upload each `.skill` file to provision it org-wide.
   (Or, from **Customize → Skills → "+" → Create skill → Upload a skill**, upload each, then
   use **Share → Entire organization**.)
2. Confirm all four show up as organization/provisioned skills.

Keep the skill files as the source of truth in this bundle's `.claude/skills/`; re-upload only
when you change one.

## C. Give the team the data (SharePoint)

1. In the **TargetAddressableMarket** site, grant your teammates **Edit** on the
   **Shared Documents** library (or specifically the `tam-project-bundle` folder).
2. Send them the site link and `docs/TEAMMATE_QUICKSTART.md`.

## Done

Members now: get the four skills automatically (section B), sync the folder for the data
(their quickstart), and start asking. Nothing else to configure.

> Note: this corpus is internal EXL competitive intelligence — keep the site and skills inside
> the org; don't share externally.
