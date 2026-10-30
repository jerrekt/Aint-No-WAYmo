# Mini-Waymo Micro V12 — project progress and Kratos explanation

- Open `Mini_Waymo_V12_Demo.html` and click **About project** (or append `#about`).
- Open `Mini_Waymo_V12_About.html` as a separate About page.
- `project_progress.json` is the source of truth for the displayed build gauge on HTTP(S) hosting. After changing milestone statuses, refresh the hosted page.
- Progress is **only** verified finished milestones divided by all milestones. The initial 25% means 2 of 8 tasks completed—not 25% physical autonomous driving readiness.
- When opening HTML offline as `file://`, an embedded JSON snapshot displays progress, which will not automatically refresh from the external JSON file. Rebuild the offline snapshot using `tools/rebuild_offline_progress.py` after edits.
- Run `python tools/sync_mnemosyne.py` after updating JSON to refresh `mnemosyne/projects/mini-waymo-micro-progress.md`.
- The separate `mnemosyne/infra/kratos.md` describes the privately operated Proxmox homelab and its student-project use.
- Kratos's website, game-server, and SJSU-project use is independent of SJSU's official infrastructure. Do not call it a university-hosted server.
- Existing V11 simulator and software/bench limitations are unchanged. Physical chassis fit, real sensors, and live Kratos deployment remain unverified.

## Updating build status
Statuses: `complete`, `in_progress`, `not_started`. Only `complete` contributes to the gauge. Keep each item's evidence accurate. If the hosted site loads the JSON but the downloaded standalone HTML has the older percentage, run the snapshot script (see below).

## Keeping the standalone file updated
```sh
python tools/rebuild_offline_progress.py
python tools/sync_mnemosyne.py
```

Use only the simulator as an educational model until hardware safety functions and motor cutout are validated on the actual device.
