# START HERE — Ain't No Waymo V1.008 handoff bundle

**Package created October 29, 2026 (Pacific).** Contains the latest available **V1.008 draft**, not a confirmed GitHub merge or deployed service. It corrects outdated documentation but deliberately does not advance the application version; any future merged change advances exactly one V1.xxx revision.

## Which file should I open?

- **Website:** `website/Aint_No_Waymo_V1.008_Website.html` (offline interactive simulation).
- **About page:** `website/Aint_No_Waymo_V1.008_About.html`.
- **Visual check:** `previews/V1.008_Desktop.png` and `previews/V1.008_Mobile.png`.
- **All sources:** `aint-no-waymo/` (GitHub-ready working tree, including MCU, backend, assets, tasks, maps, and version tools).
- **Claude handoff:** `handoffs/CLAUDE.md`, `handoffs/KRATOS.md`, `handoffs/CLAUDE_PASTE_PROMPT.md`.
- **Team handoff:** `handoffs/TEAM.md`, `handoffs/TEAM_PASTE_PROMPT.md`.
- **Hardware/map:** `handoffs/HARDWARE_MAP.md`.
- **Mnemosyne note:** `handoffs/MNEMOSYNE_CURRENT_STATE.md`.
- **Deployment review:** `handoffs/RELEASE_CHECKLIST.md`.

The matching website source is also in `aint-no-waymo/Mini_Waymo_V12_Demo.html` despite its older prototype filename.

## Release truth

No direct GitHub/Proxmox/Cloudflare access was used to build this package. Do not state that V1.008 is merged or deployed, that a mini robot physically drives, or that all hallway room placements are verified. The SJSU and SME transparent header-logo correction was browser-checked at the prior V1.008 generation stage; this handoff refresh is documentation-only.

## What to do now

Send the **complete ZIP** to Claude (which already uses your Mnemosyne vault) or unzip it into your local Git repository after comparing with `main`. Use the teammate guide to divide work; verify the server environment before deployment. After a real merged update, advance exactly one release revision, and update the vault with verified facts.
