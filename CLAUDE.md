# Ain't No Waymo: Claude Code handoff

BJ (Branden Adsuara, GitHub `jerrekt`) runs this SJSU SME project: a Mini-Waymo diecast car plus a map-first website. BJ mostly updates the **site** from here. Keep replies short and direct. Ask before building anything expensive to redo.

## Rules
- Work on a branch. Preview with screenshots at **desktop and 400px width**. BJ merges himself; open the PR when he says "push".
- `main` is protected: PR + passing `version-and-simulator` check. **One version bump per PR**: `python3 tools/version.py bump --message "..."`, then `python3 tools/check_repo.py`. Extra changes in the same PR do not bump again; add them as lines under that version in `CHANGELOG.md`.
- Never write the team password, Discord webhook URL or tokens into files, PRs or the vault. The word "password" must not appear in `team_tasks.json`.
- Claude can't reach BJ's servers. Give commands, ask for pasted output, never claim a deploy worked first.
- Log significant changes in Mnemosyne `inbox/changes.yaml` (repo `jerrekt/mnemosyne`; read `# next id` first; single-quoted values, double any apostrophe). Flag security work in `runbooks/security-review.md` **before** building it.
- Model: Sonnet medium for site, map, wording, notes. **Opus high** for security, auto-deploy, secrets, server writes (see backlog).

## Where things run
- Site: `aintnowaymo.adsuaracloud.com`. FastAPI app in `kratos/` on CT 312 (Proxmox LXC on Kratos), uvicorn `127.0.0.1:8090` behind a Cloudflare tunnel, user `waymo`.
- Auto-pull: merged PRs go live in about a minute. Changes under `kratos/` restart the app (rollback if it fails). Page-only changes don't restart.
- Main pages: `Mini_Waymo_V12_Demo.html` (Live map + simulator) and `Mini_Waymo_V12_About.html`. The `V9`/`V10`/`V12` file names are historical snapshots, not the version number. Repo version is in `VERSION`.
- The header version pill and tab title are stamped by `tools/version.py bump`. Don't hand-edit them.

## Updating the map and the "Where to?" list
The map is a generated SVG, embedded in the demo page as base64. Don't hand-edit the SVG or the base64.
1. Edit `tools/build_map_svg.py` (geometry, doors, labels, compass). South wall (201 to 214) is to scale: 100" wall, 65" door, 108" wall, repeating.
2. Run the full refresh: `python3 tools/build_map_svg.py && python3 tools/sync_room_list.py && python3 tools/embed_map.py`
   - `build_map_svg.py` writes `maps/is_second_floor_drawing.svg` and `maps/is_second_floor_rooms.json` (every room label position).
   - `sync_room_list.py` snaps each room to the nearest hallway stop and rewrites `ROOMS` (in `sim/engine.mjs` and the demo page) and the clickable map hotspots.
   - `embed_map.py` writes the SVG into `SURVEY_IMAGE_URI`.
3. Run the CI checks (below). Rooms listed must be all digits: `kratos/app.py` rejects any other mission room id.
- Rooms near each other share a hallway stop. The graph (`NODES`/`EDGES`) is only 16 stops (A to P) and was **not** rebuilt per door. A real per-door graph is a bigger change that rewrites the node tests.
- The dropdown comes from hardcoded `ROOMS`, not the backend. If the live site still shows old rooms (263, 251, 200...), the PR with the new list isn't merged yet.
- The test rooms were swapped to rooms on the same stop (200 to 214, 230 to 222, 251 to 224, 263 to 227, 202 to 210). Default room is 227, start room 214.

## CI checks (run locally before a PR)
```
python3 tools/version.py check --base-ref origin/main
python3 tools/check_repo.py
node tests/test_v6.mjs && node tests/test_v9.mjs && node tests/test_v10.mjs && node tests/test_pause.mjs
```
Plain `pytest tests` fails at collection (needs fastapi and a system Chromium); CI doesn't run it. The browser tests in `tests/browser_v*.py` were updated to the new rooms but never run.

## Current state
- V1.022 merged (version in header). **PR #14 (V1.023)** is open and green: compass fix (true north is about 31 degrees clockwise of plan up, measured from a north-up Google Maps screenshot, not surveyed), new Where to? list (29 rooms, 201 to 245), W tab icon.
- PR #6 (V1.017) is still open but redundant: kratos-07 is already done on main and the version is far past V1.017. Close it.
- Live task claims are off on purpose (`WAYMO_TASK_WRITES`). Team updates go to Discord via `/api/updates`.

## Open work
1. **North wall (rooms 227 to 222), needs BJ at school:** wall length before the first door, each door and wall width, which doors are doubles. Then add to `build_map_svg.py` and run the full refresh.
2. **Hall lengths:** 168 ft north / 300 ft east and the 205 ft south / 330 ft east split of 536.93 ft are estimates from a Google Maps screenshot. Measure before treating as fact.
3. **Labels:** 218B and 219C are unconfirmed and not in the dropdown. Is "Aviation Club Room" right? East wall labels (q65). White map sheet (q66). Label 223 repeats in the source (two 223s on the north wall, one dashed). Two doors are both labelled 216.
4. **Compass:** check the 31 degrees against a phone compass in the hallway.
5. **Task list additions:** BJ has a list of 11 suggested new tasks to approve yes/no (survey measurements, Kratos hardening, hardware decisions). `tests/test_team_board.py` line 20 asserts the task count (37); update it when tasks change. Progress bars come from `team_tasks.json` via `tools/rebuild_offline_progress.py`; keep SME (`jerrekt/sme-sjsu`, `data/site.json`) and Mnemosyne (`projects/mini-waymo-notes.md`, `projects/sme.md`) in step. Find the exact bar values with `grep -n -i progress`.
6. **Mnemosyne:** `changes.yaml` entries for V1.022 and V1.023 are not logged yet.
7. **Seapot 20% to 99% load rate:** documented as unconfirmed only. Before public use: Cloudflare view, date range, request count, survey details.
8. **Opus-high backlog:** constant-time admin token compare (`hmac.compare_digest`); Cloudflare Access on write routes (q62); reserve CT 312's address (q56); q54; q59 (remove Kratos / CT 312 / tunnel wording from public pages); backups; MQTT and ESP32 tests; accept letter-suffixed room ids in the backend; decision on held-back infra docs.
9. **Hardware (BJ to confirm what's done):** diecast measurements, ESP32-S3 vs C3 choice, 1/43 RC drift car fit. Mark finished items in `team_tasks.json` by PR.
10. **Housekeeping:** merged branches left in place until BJ asks to delete. Unknown branch `claude/affectionate-wright-9j5evw` is likely a teammate's; leave it alone.

## Gotchas
- Cloud sessions reach GitHub by REST only (`gh api`); GraphQL and settings writes are blocked. Merging from a Claude session may be blocked too; BJ merges.
- Don't pipe checks into `tail` before a `&&` push.
- Mnemosyne `INDEX.md` is generated (`tools/make_index.py`), never hand-edited. Vault gates: `python3 site/build.py --strict` and `python3 tests/check_vault.py`.
- Shallow clones: `git remote set-branches --add origin <branch>` before pushing a new branch, and `git fetch origin main` first so the push is a thin pack.
- Tab icon is `assets/favicon.svg` plus an inline copy in both pages. Browsers cache icons hard; hard-refresh to see changes.
