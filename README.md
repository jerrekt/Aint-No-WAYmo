# Ain't No Waymo — Mini-Waymo Micro

**SJSU Society of Manufacturing Engineers student project** · independent three-week miniature autonomous vehicle challenge.

**Local development package: V1.008 draft**, dated 2026-10-29 (Pacific). This is **not a verified merged GitHub release** or a live Kratos deployment. The source uses historical file names containing V9–V12; current website entry points are `Mini_Waymo_V12_Demo.html` and `Mini_Waymo_V12_About.html`.

## Start here

- **Web preview:** open `Mini_Waymo_V12_Demo.html` locally. This is a standalone simulated demo; no real ESP32 is connected.
- **About-only preview:** `Mini_Waymo_V12_About.html`.
- **Team handoff:** `docs/TEAM_HANDOFF_CURRENT.md`.
- **Claude implementation handoff:** `docs/CLAUDE_HANDOFF_CURRENT.md`.
- **Kratos and Cloudflare:** `docs/INFRA_KRATOS_HANDOFF_CURRENT.md`.
- **Hardware and map:** `docs/HARDWARE_FIRMWARE_MAP_HANDOFF.md`.
- **Deployment acceptance:** `docs/DEPLOY_CHECKLIST.md`.
- **Mnemosyne update note:** `mnemosyne/projects/aint-no-waymo-current-state.md`.
- **Status facts:** `docs/PROJECT_STATUS_MACHINE.json`.

## Mission and scope

In a three-week challenge issued by visiting Opera guest speaker Dan Berte, the SJSU SME team aims to make the World's Littlest Waymo I-PACE diecast model act like a miniature autonomous car in the second floor of the IS Building. Intended capabilities include selected room-to-room missions, sensing/obstacle stop, turn signals, chimes, local failsafes, and remote mission dispatch and telemetry via Kratos. The finished car should be self-contained if physically feasible; a detachable battery/FPV trailer is only an optional later upgrade. Independent student effort; not affiliated with or endorsed by Waymo or Opera.

## Team (roles not invented)

Branden Adsuara (provisional systems/electronics/website), Noah Zerarka, Gage Watts, Subir Khan, Isabel Burgos, Brandon Wu. The latter five members' detailed responsibilities have **not been confirmed**. Actual roster and links: `team_members.json`.

## Layout and APIs

| Area | Location | Evidence status |
|---|---|---|
| Website and About | `Mini_Waymo_V12_Demo.html`, `Mini_Waymo_V12_About.html`; `assets/mockup-layout-v1.007.*` | Dark three-column V1.008 draft; desktop/mobile previously visually verified |
| Roadmap and task board | `project_progress.json`, `team_tasks.json`, `kratos/team_tasks.py` | 25% (2/8 milestones); 34 seeded tasks, no deployed shared DB verified |
| Simulation | `core/`, `sim/`, `tests/` | Virtual tests only; no verified physical driving |
| S3 firmware | `firmware/` | BENCH scaffold, **motors disabled** |
| C3 receive-only MQTT benchmark | `bench/esp32-c3/` | Firmware + probe code; not verified on user's physical board |
| Server prototype | `kratos/` | FastAPI+MQTT example, **not production audited** |
| Building map | `maps/` | Approximate visual hallway survey, not navigation-ready |
| Diecast sizing | `Mini_Waymo_Fit_Planner.html`, `diecast_fit_test_tray.scad` | Not measured to real collectible yet |

## Versioning

Official team baseline started **V1.000**; every merged update advances exactly one suffix (`V1.001`, `V1.002`...). Run `python tools/version.py bump --message "..."` once per PR, and `python tools/version.py check` before review. Because these V1.001–V1.008 development files have **not been verified as merged**, do not assume GitHub `main` or the deployed website is currently V1.008. **This repackaging updates handoff documentation only; application version remains V1.008 draft.** See `VERSIONING.md`.

## Security and deployment

Keep Cloudflare tokens, Wi-Fi/MQTT credentials, team-board password and admin tokens **out of source control, website files and Mnemosyne**. Configure secrets via protected server settings. Protect mutating `/api/tasks/` endpoints and robot-control endpoints with meaningful server-side authorization; the shared task password prototype does not prove user identity. Keep raw MQTT/SSH/Proxmox private. Inspect the user's existing Kratos container before making any changes.

## Engineering honesty

- Progress bar reflects two completed software/planning milestones, **not** a driving robot.
- The display's room labels and corridor lengths are from an approximate iPhone survey; overlays are synthetic and cannot yet guide a physical robot.
- The demonstration site is **not evidence** of deployed cloud service, live telemetry, or motor electronics.
- Do **not** run `python build.py` expecting it to rebuild the complete V1.008 website: it is an older simulator generation script and can omit later website features.
- University logos are used to identify the student team; the website requires any appropriate branding approvals and a non-endorsement notice.

## GitHub onboarding

Create the repository named `aint-no-waymo` if it does not yet exist, then import this directory and invite the six members. Use feature branches, PR review and the existing CI/version checks. **Do not overwrite an existing remote** without inspecting it first. See `docs/TEAM_HANDOFF_CURRENT.md`.
