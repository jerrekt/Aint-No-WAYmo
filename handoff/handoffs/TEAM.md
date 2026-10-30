# Team handoff — Ain't No Waymo (V1.008 development candidate)

**Current source is a local draft, not a proven GitHub merge or hosted deployment.** Each team member should use this repository as the handoff baseline only after reconciling it with the actual GitHub `main` branch.

## People and links

- Branden Adsuara — provisional systems integration, electronics, website; portfolio https://bja.adsuaracloud.com/; LinkedIn https://www.linkedin.com/in/brandenjga/
- Noah Zerarka — SJSU SME; role TBD; https://www.linkedin.com/in/noahzerarka/
- Gage Watts — SJSU SME; role TBD; https://www.linkedin.com/in/gage-watts-30b30634a/
- Subir Khan — SJSU SME; role TBD.
- Isabel Burgos — SJSU SME; role TBD.
- Brandon Wu — SJSU SME; role TBD.

Do not assign named responsibilities to anyone until they accept them. Public About roster: `team_members.json`.

## What is done vs remaining

**Implemented in software:** 34 seeded tasks (5 done, 2 in progress, 27 to do), 8 milestone progress gauge (2 done = 25%), diecast photo in website, SJSU/SME logos, responsive three-column dashboard, illustrative floor map, room menu, simulated Go/Pause/Stop/recovery, task board UI and API prototype, notes, C3 bench code.

**Not proven:** mini car internal fit, rolling drivetrain, battery and safety cutoff, real ranging/camera/encoders, S3 motor firmware, real C3 MQTT latency, mapped corridor coordinates, live websocket telemetry, production role authorization, team-synced tasks on Kratos, or successful hallway mission.

## How to collaborate

1. First identify the actual GitHub remote and whether the repo has already been published; don't force-push over teammates' work.
2. One feature per `feature/<area>-<change>` branch. Keep PRs focused, with a testing note and screenshot for any UI change.
3. At PR creation, bump version **exactly once** relative to current `main` (`python tools/version.py bump --message "..."`). Rebase or update before merge if another PR advanced the version.
4. Require at least one reviewer. Never place secrets or private server configuration in commits, issues, or Mnemosyne.
5. Seed task statuses in `team_tasks.json` are not the deployed database. A claim is only shared when the FastAPI+SQLite backend has been deployed and tested.
6. Do not alter `core/`, `firmware/` or the real robot's motor connections without the safety owner's review. Physical stop and watchdog have priority over any remote command.
7. After merge, record changed interfaces, evidence and owner in Mnemosyne.

## Immediate opportunities for teammates

- **Mechanical:** disassemble/measure the real diecast safely, CAD clearance/cutouts, choose tiny drivetrain and battery.
- **Electrical:** verify regulator/1S LiPo charging, motor driver, local E-stop, LED/sound packaging; bench first.
- **Firmware/communications:** ESP32-C3 receive-only MQTT RTT test and logging; later S3 camera/sensor APIs.
- **Navigation:** survey door locations, marker plans and route confidence; avoid fake coordinates.
- **Kratos/backend:** inspect current CT and tunnel, secure/admin-auth backend, MQTT ACL, acknowledgements, task persistence.
- **Website:** keep approved V1.008 visual direction; integrate real task/telemetry data and remove simulator-only claims.

## Files to read

`README.md`, `docs/CLAUDE_HANDOFF_CURRENT.md`, `docs/INFRA_KRATOS_HANDOFF_CURRENT.md`, `docs/HARDWARE_FIRMWARE_MAP_HANDOFF.md`, `VERSIONING.md`, `project_progress.json`, `team_tasks.json`, `maps/README.md`.
