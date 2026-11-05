# Ain't No Waymo: handoff for the site updater

Written 2026-11-05 by the previous Claude chat. You are the new updater for this project. Claude Code loads this file on its own; a new chat gets it pasted. Read it fully before changing anything, then read `CHANGELOG.md` for what shipped after V1.042.

## 1. Who and what

- **BJ** (Branden Adsuara, GitHub `jerrekt`, email ends adsuaracloud) leads the SJSU SME "Ain't No Waymo" (Mini-Waymo Micro) project: make the World's Littlest Waymo I-PACE diecast drive itself between rooms on the second floor of the Industrial Studies (IS) building, plus a map-first website. Three-week challenge from guest speaker Dan Berte. Independent student project, not affiliated with Waymo.
- Team of six: BJ (project lead, systems integration: electronics, web, server), Noah Zerarka (drivetrain, donor car teardown), Subir Khan (parts and sensing, website help), Isabel Burgos (mechanical fit, shell measurement and chassis), Brandon Wu (hallway survey: doors, labels, lengths), Gage Watts (role open). Owners on the task board come from each person claiming; never assign a named person a task they didn't accept.
- Site: **aintnowaymo.adsuaracloud.com**. Repo: `jerrekt/Aint-No-WAYmo` (GitHub reports it moved to that casing; the clone works either way).
- Second repo: **Mnemosyne**, BJ's private second-brain vault (`jerrekt/mnemosyne`), where project notes and a change log live. Section 7.
- A separate chat is being opened for the **schematic and wiring diagram**. Don't redo that work; keep the pin map in `handoff/handoffs/SUBIR_HANDOFF.md` as the shared reference and update it only when a hardware decision changes.

## 2. How BJ works with you (rules)

- **Short, direct replies.** No preambles, no recaps. He self-corrects mid-conversation and expects you to recalibrate without hedging.
- **Branch, preview, wait for "push".** Work on a branch, screenshot at desktop and **400 px** width, describe the result. Open the PR only when he says **push**. He merges himself (merging from a Claude session is blocked). Say "push" once per PR; he says it a lot.
- **One version bump per PR**: `python3 tools/version.py bump --message "..."` then `python3 tools/check_repo.py`. More changes in the same PR do not bump again: add lines under that version in `CHANGELOG.md`. If two PRs pick the same next version, whichever merges second updates from main and rebumps.
- **Batch small things into one PR** to save his usage; don't open a PR per tweak unless he asks.
- **Ask before building anything expensive to redo**; otherwise start and show the result.
- **Never claim a deploy or command worked.** Claude can't reach his servers or the live site (the cloud session can't even fetch aintnowaymo.adsuaracloud.com). Give commands, ask for pasted output, diagnose from it.
- **Secrets:** never write the team password, the Discord webhook URL, tokens, Wi-Fi passwords, real LAN IPs or internal hostnames into files, PRs, public vault notes or chat. The word "password" must not appear in `team_tasks.json`. Real addresses go only in the vault's `private/` folder. Public pages must not name Kratos, CT 312 or the tunnel (q59, done in V1.038: pages say "a private home server"). Never expose ports 22, 8006 or 1883.
- **Security work** (auth, firewall, tokens, server writes, auto-deploy): flag it in the vault's `runbooks/security-review.md` **before** building, and tell BJ to switch the model to **Opus high** for it. Sonnet medium is fine for site, map, wording, notes.
- Hardware advice: concise trade-offs, cost-effective picks, and he'll paste Amazon search text for you to pick from. He owns: Waymo shell, DRV8833, bulk cap, LEDs/resistors, slide switch, XIAO ESP32-C3, Bambu P2S printer, calipers; ordered GY-521 MPU-6050 3-pack (arrives Nov 6, $11.79).

## 3. Where things run

- **Site:** FastAPI app in `kratos/` on CT 312 (Proxmox LXC on his homelab host "Kratos"), uvicorn on `127.0.0.1:8090` behind a Cloudflare tunnel, system user `waymo`, repo at `/opt/aint-no-waymo`.
- **Auto-pull:** `aint-no-waymo-sync.timer` runs every minute, pull-only fast-forward of main; a change under `kratos/` restarts the app (and rolls back if it fails to start). Page-only changes go live without restart. Merged PRs are live in about a minute. Diagnose with (BJ runs on Kratos):
  `pct exec 312 -- bash -c 'git -C /opt/aint-no-waymo log --oneline -1; cat /opt/aint-no-waymo/VERSION; systemctl is-active aint-no-waymo-sync.timer aint-no-waymo.service; journalctl -u aint-no-waymo-sync.service --no-pager -n 25'`
- **Task claims and parts:** go through the claim bot (`waymo-api.adsuaracloud.com`, in the "bots" container, code shared with the Bricked Sorting project). Site buttons and Discord `/claim`, `/start`, `/done`, `/release`, `/tasks` write there; this server's own `/api/tasks` is read-only (`WAYMO_TASK_WRITES` off on purpose) and serves `team_tasks.json`. The bot keeps owner/status/bought by **task or part id**; new ids in the seed file show without owners until the bot reloads. Bot should be at or after Bricked commit `c3aed02` (unchecked: `git -C /opt/waymo-claim log -1 --oneline`). Team updates post to Discord via `/api/updates`.
- **MQTT bench:** CT 313 `waymo-mqtt` (Mosquitto, LAN-only 1883, accounts `waymo_bench_c3` and `waymo_bench_controller`, per-account topic ACL, firewall before first start). Controller login tested. **Not done:** flashing the ESP32-C3 bench sketch (`bench/esp32-c3`, PlatformIO, secrets in a git-ignored `secrets.h`) and measuring round-trip delay (goal under 150 ms for 95%). Stage 2 (campus access via phone hotspot + Cloudflare tunnel + Access service token) is flagged in the security runbook, not built.
- **SME club site** (`jerrekt/sme-sjsu`, `data/site.json` → `.aint_no_waymo.status`) carries a one-line status of this project; keep it in step after big merges (PR #4 there may still be open).

## 4. Repo map

| Path | What |
| --- | --- |
| `Mini_Waymo_V12_Demo.html` | The app: Live map + simulator, Car, Build, About, Team views (`body[data-view]`, hash routing, dock ids `dockMap dockCar dockBuild dockAbout dockTeam`). The V9/V10/V12 file names are old snapshots, not the version. |
| `Mini_Waymo_V12_About.html` | Standalone About page (same board code duplicated; patch both). |
| `VERSION`, `version.json`, `CHANGELOG.md` | Stamped by `tools/version.py`; header pill and tab title are regex-stamped, never hand-edit. |
| `team_tasks.json` | Task board seed: 44 tasks, `size` S/M/L (1/2/4 pts), `phase` `both`/`v1`/`v2`, `groups` (car, brains, map, demo), `milestone_labels`. `tests/test_team_board.py` line 20 asserts the count. |
| `team_members.json` | Roles and links for the Team page. |
| `build_parts.json` | Parts with `group`, `cost`, `approx`, `qty`, `where`, `link`, `bought`, `bought_by`, `note`. After editing: `python3 tools/embed_build_parts.py` (check_repo fails if the embedded copy is stale). |
| `tools/build_map_svg.py` → `maps/*.svg,*.json`; `tools/sync_room_list.py`; `tools/embed_map.py` | Map pipeline (section 5). |
| `tools/rebuild_offline_progress.py` | Re-embeds `team_tasks.json` and `project_progress.json` into both pages. Run after editing tasks. |
| `sim/engine.mjs`, `sim/template.html`, `core/` | Simulator engine (node tests) and the C++ safety core compiled to wasm (inline base64 in the page). Engine still models differential drive; the page says so. Don't touch for display changes. |
| `kratos/` | FastAPI: `app.py` (static pages, mission API, rejects non-numeric room ids), `team_tasks.py` (`/api/tasks`), `team_updates.py` (Discord). |
| `bench/esp32-c3/` | MQTT bench sketch, `probe.py` timing tool, README. |
| `deploy/` | Auto-pull unit files and `AUTO_PULL.md`. |
| `handoff/handoffs/SUBIR_HANDOFF.md` | Team handoff: versions table, hardware decisions, parts, **pin map**, wiring rules, next steps. Linked from `handoff/START_HERE.md`. Keep current. |
| `docs/` | Older design docs from the V1.00x bundle; historical, mostly superseded. |

## 5. Map and the "Where to?" list

The map is a generated SVG embedded as base64 (`SURVEY_IMAGE_URI`). Never hand-edit the SVG or base64.
1. Edit `tools/build_map_svg.py` (geometry, doors, labels, compass). South wall rooms 201 to 214 are to scale: 100" wall, 65" door, 108" wall, repeating. Compass: true north about 31° clockwise of plan-up (from a Google Maps screenshot, unsurveyed).
2. `python3 tools/build_map_svg.py && python3 tools/sync_room_list.py && python3 tools/embed_map.py`. `sync_room_list.py` snaps each numeric room to the nearest of 16 hallway stops (NODES A to P) and rewrites `ROOMS` in `sim/engine.mjs` and the page plus the clickable hotspots. Rooms must be all digits.
3. Run the CI checks. The graph was not rebuilt per door; a true per-door graph rewrites the node tests (bigger job).

Display geometry in `draw()` (page): hall centre lines are drawn at north y=222, east x=1196, south y=868 in the 1500×1049 image; the lane is 18 px right of centre (`laneShift`). The car marker (`carPose`) eases toward a lane point while driving and toward the door hit (`ROOM_IMAGE_HITS`) on arrival. The map is two SVG layers: `#mapDyn` (route, car, scans; pointer-events off; redrawn every 90 ms) and `#mapHot` (room hotspots; only re-rendered when selection changes). **Don't merge them back**: a redraw between mouse-down and mouse-up swallows clicks (V1.042 lesson).

Chimes: `chime` object in the page (Web Audio, synthesized; start / arrive / move sequences), watched in `chimeWatch(s)` from the engine snapshot (`running` edge, `arrivals` count, status 2 or 3). The "♪ Chimes on" button under the room picker toggles; preference in `localStorage` `waymoChimeV1`. BJ explicitly allowed mimicking the Waymo chime sound.

## 6. CI checks (run before every PR)

```
python3 tools/version.py check --base-ref origin/main
python3 tools/check_repo.py
node tests/test_v6.mjs && node tests/test_v9.mjs && node tests/test_v10.mjs && node tests/test_pause.mjs
```
`pytest tests` fails at collection (needs fastapi and a system Chromium); CI doesn't run it. Required check on main: `version-and-simulator`.

Previewing: serve the repo locally and drive with Playwright. Useful: `document.getElementById('surveyAll').click()` then `chooseRoom('227'); sendRoom('now')` dispatches a trip; `sim.snapshot()` reads state; `document.getElementById('dockBuild').click()` switches views; `teamBuildDetails.open=true` expands the About checklist. The task API isn't reachable from the cloud, so pages fall back to the embedded data; to test the live shape, serve a fake `/api/tasks` that returns only `tasks` and `milestone_labels` (the real one adds `size_points`, `phases`, `groups` since V1.039).

## 7. Mnemosyne (vault) workflow

- Clone `jerrekt/mnemosyne` (private). Notes push straight to main anytime; no PRs.
- Gates before pushing: `python3 site/build.py --strict` and `python3 tests/check_vault.py`. `INDEX.md` is generated by `tools/make_index.py`, never hand-edited.
- **Log every significant Waymo change** in `inbox/changes.yaml`: read the `# next id` line first (c276 as of 2026-11-05), use that id, bump the line. Single-quoted values, double any apostrophe. Keep ids unique even after deletions (c255 was once duplicated and renumbered).
- Waymo notes: `projects/mini-waymo.md` (public card), `projects/mini-waymo-notes.md` (private detail; version section needs updating after each merge), `projects/mini-waymo-handoff.md` (this file's twin), `projects/mini-waymo-role-handoff.md`, `projects/mini-waymo-task-guidance.md` (superseded callout at top), `projects/waymo-board-and-buy-list-handoff.md`, `infra/mini-waymo-kratos-deployment.md`, `runbooks/security-review.md` (flags), `private/homelab-addresses.md` (CT 312/313 lines; the only place real addresses go).
- Labels used in notes: verified (BJ pasted output), reported, planned, unknown. "Details only" means no editorializing.
- Not logged yet: V1.039 to V1.042 (changes.yaml entries), and the V1.041 task-path redo in `mini-waymo-notes.md`.

## 8. Current state (2026-11-05 morning)

- main = **V1.041**; **PR #34 (V1.042)** open: room clicks on the map work again (two-layer map) and the arrival chime fires. Shipped this week: V1.038 site polish and public wording; V1.039 board keeps sizes/phases/groups with live API data; V1.040 keep-right lane, turn into the door, Waymo-style chimes; V1.041 V1/V2 as parallel task paths.
- **Task model (V1.041):** V1 (line follower on floor tape) and V2 (room scanner) are two *paths* to the demo, not phases. Tasks are `both`, `v1` or `v2`; each car's bar = shared + its own; no checkpoint flag (Nov 13 was a Claude suggestion, dropped). Demo date unknown.
- **Hardware decisions:** donor 1/43 RC drift car (Noah, arrives Nov 6) supplies motor, steering, wheels, 1S pack; XIAO ESP32-S3 Sense (camera through the windshield reads printed room markers); DRV8833; GY-521 MPU-6050 gyro (bought); piezo chime (a must); 2 amber LEDs (lowest priority); E-stop slide switch on the motor rail only; no separate battery protection board; no SD card (D8 to D10). Kapton marked nice-to-have.
- **Sensor decision in flight (last night):** BJ asked about a "real lidar". Recommendation given: **TF-Luna** (8 m single-point, 5 g, $26 Amazon same-day) on the roof turret instead of the VL53L7CX, with the servo wagging ±25° while driving for obstacle stop and a full sweep at stops; drop the 7CX unless Subir already ordered it. BJ had not confirmed the purchase when the chat ended. If he bought it: update `build_parts.json` (replace `vl53l7cx` with the Luna, power from the battery rail not 3V3, I2C 0x10), the pin map in `SUBIR_HANDOFF.md`, and the V2 copy on the Build page.
- **Feasibility review flagged:** the donor's tiny 1S pack will brown out the S3 (suggest a 300 to 500 mAh 1S if it fits); the zinc body is heavy for the donor motor; wheelbase mismatch likely (I-PACE at 1:42 is about 71 mm, donors 62 to 65 mm); V1 needs a 2 to 3 element line sensor not one; buy the S3 Sense from Amazon (Seeed direct is slow). Build page still says "DRV8835 class" and "steering servo runs straight from the ESP32": fix when the teardown settles steering.
- **Open survey work (Brandon, at school):** north wall doors 227 to 222 (`survey-05`), hall lengths (168 ft north / 300 ft east are estimates), labels 218B, 219C, two 216s, repeated 223 (`survey-06`); compass check with a phone.
- **BJ's own next tasks:** measure the diecast with calipers, post roles in Discord, flash the C3 bench test and measure delay, breadboard E-stop + DRV8833 + cap on the C3, chime and LEDs on the C3, lock down robot controls (Opus high).
- **Opus-high backlog:** constant-time admin token compare (`hmac.compare_digest`), Cloudflare Access on write routes (q62), reserve CT 312's address (q56), q54, backups, MQTT and ESP32 tests, letter-suffixed room ids in the backend, decision on held-back infra docs, MQTT stage 2.
- **Housekeeping:** merged branches stay until BJ asks; branch `claude/affectionate-wright-9j5evw` is a teammate's, leave it. `project_progress.json` is stale (2 of 8) and no longer shown. Seapot "20% to 99% load rate" claim elsewhere is unconfirmed.

## 9. Gotchas

- Cloud sessions reach GitHub by REST only: `gh api repos/jerrekt/Aint-No-WAYmo/pulls -f title=... -f head=... -f base=main -F body=@file`. `gh pr create` fails (GraphQL blocked). Sometimes the first PR-create call is refused by the session's permission classifier; retry once with the body in a file.
- Shallow clone: `git remote set-branches --add origin <branch>` before pushing a new branch; `git fetch origin main` first.
- Don't pipe checks into `tail` before a `&&` push.
- `pkill -f` matching your own shell kills the session; use `nohup` for a local server and check it with curl.
- Tab icon is `assets/favicon.svg` plus inline copies in both pages; browsers cache it hard.
- The About page and the Demo page duplicate the board JS; patch both with the same script and assert each replacement matches exactly once.
- Mosquitto `pct enter` paste swallows password prompts: run `mosquitto_passwd` one line at a time.
