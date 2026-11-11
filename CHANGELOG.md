## V1.049 — 2026-11-11
- Tap a map dimension to see its status and source, and report a new measurement to Discord
- Roof turret bench test for the XIAO ESP32-S3 (`bench/turret-s3`): sweeps the 2 g servo on D8 and reads the TF-Luna over I2C, JSON lines on USB serial. Compiles for seeed_xiao_esp32s3; logic tests in `bench/turret-s3/tests`. Not yet run on hardware.

## V1.048 — 2026-11-11
- Map dimensions show measured, estimated (~) or to measure from maps/is_second_floor_dimensions.json; VL53L7CX (Subir) as the V1 front sensor

## V1.047 — 2026-11-05
- Build page parts: costs now count only what the car uses; BJ keeps the rest. One S3 Sense ($17.56) and the OV5640 ($16.30), each with its share of the Seeed shipping and tax (the second board is for another project); one gyro of the 3-pack ($4.32); one servo of the 2-pack ($8.80); Kapton about $0.15 of the $10.99 pack; thin wire, piezo and floor tape estimated by the amount used. Multimeter is a tool on hand at $0. Small drill / pin vise removed

## V1.046 — 2026-11-05
- Build page parts: recorded BJ's orders. Waymo shell (Nov 1, $49.32, complete); TF-Luna lidar ($28.58) and MPU-6050 3-pack ($12.97) delivered Nov 5; 2-pack of 2 g roof servos ($17.59) and Kapton tape ($10.99) arriving Sat Nov 7; 2 XIAO ESP32-S3 Sense ($27.98) and a new OV5640 autofocus camera part ($12.99) ordered from Seeed Nov 5 ($51.42 total). 14 of 20 parts now bought. SUBIR_HANDOFF.md parts table matches

## V1.045 — 2026-11-05
- Controls page: Drive it yourself. Unlock with the team password, then hold the pad or W A S D to drive. Drives the simulator now, and the real car once the server switches it on (one driver at a time, the car stops itself if commands stop). The map shows on Controls while unlocked. Admin token check is now constant-time

## V1.044 — 2026-11-05
- Build page: wiring plan diagram (assets/wiring.svg) drawn from the team handoff pin map, with the decisions of 2026-11-05: steering is a servo on D2 (D3 free), and the V2 depth sensor is a TF-Luna lidar on the motor rail instead of the VL53L7CX. Parts list, tasks, About table and SUBIR_HANDOFF.md pin map updated to match

## V1.043 — 2026-11-05
- Simulator: car marker turns the short way again; its heading was never wrapped, so after enough trips the shortest-turn maths went the long way round (about 270 degrees) on the next dispatch

## V1.042 — 2026-11-05
- Map: clicking a room sends the car again. The 90 ms redraw was replacing the room hotspots between mouse-down and mouse-up, so clicks were lost; rooms now sit on their own layer above the route and are only redrawn when selection changes
- Arrival chime plays again: it read the arrival count as a list, so it never fired.
- `CLAUDE.md` rewritten as the full updater handoff (rules, infrastructure, repo map, map pipeline, vault workflow, current state); `handoff/handoffs/CLAUDE_PASTE_PROMPT.md` is the matching paste prompt for a new chat.

## V1.041 — 2026-11-04
- Task board: V1 and V2 are parallel paths, not phases. Tasks are shared, V1-only or V2-only; each car's bar counts shared work plus its own. Five new path-specific tasks (line sensor, tape following, room markers, roof turret, scan matching); checkpoint flag dropped

## V1.040 — 2026-11-04
- Simulator: car keeps to the right-hand lane, turns into the door on arrival (crossing the hall for left-side rooms), and plays Waymo-style ride chimes for departure, arrival and please-move; the Sound button toggles them

## V1.039 — 2026-11-04
- Board keeps sizes, phases and groups when tasks come from the live API; the task route now sends them too
- Kapton tape marked nice to have on the Build page: the printed tray, electrical tape or hot glue insulate the boards from the metal shell just as well.
- Gyro bought: HiLetgo GY-521 MPU-6050 3-pack, $11.79 (BJ).

## V1.038 — 2026-11-04
- Site polish: retire the old update form, server wording on public pages (q59), updated footer, no DRAFT tag, About describes the two versions, full-screen map on phones, decision and trip beside the map on desktop, trip chip hidden until a trip, Build jump links

## V1.037 — 2026-11-03
- Weighted task board (groups, S/M/L points, V1 and V2 phase bars with the Nov 13 checkpoint), progress card counted from tasks, priced buy list by group

## V1.036 — 2026-11-03
- Live map: the route line ends at the room's door and the car parks at the door on arrival
- Team page: roles as agreed 2026-11-03 (BJ lead and systems, Noah drivetrain, Subir parts and site, Isabel mechanical fit, Brandon survey; Gage open). Parts: donor car ordered (arrives 11/06), DRV8833 and V1 line sensors on hand, sensor and turret servo being ordered.
- Add a team handoff for Subir (handoff/handoffs/SUBIR_HANDOFF.md): build status, versions, hardware decisions, parts, pin map, repo workflow, next steps.

## V1.035 — 2026-11-03
- Build page: clearer V1/V2 summaries (what it does, can, can't, needs); V2 depth sensor on a sweeping roof turret, camera through the windshield; official shell size
- Simulator: 360-degree scans relabelled as roof-turret sweeps; wheel readouts marked as simulator-only, with a note that the real car steers and can't turn in place.
- Tasks: drop two-motor wording (diecast-fit-03, hardware-01, hardware-02); battery uses the donor's protected pack and the XIAO charger (hardware-03); chime is a must with our own tones, turn signals lowest priority (hardware-05); gyro only, no wheel counts (sensors-02); shell size, windshield camera and turret in the fit tasks.
- Parts: remove battery protection and charger; chime and turn lights reworded; donor steering may be a servo or a coil, check on teardown.

## V1.034 — 2026-11-03
- Build page parts: live bought flags and Mark bought through the claim bot; remove the retired CT 312 part route

## V1.033 — 2026-11-03
- Build page: V1 line follower and V2 room scanner, parts list with Mark bought (Discord + PR)

## V1.032 — 2026-11-01
- Add survey-05 (north wall doors) and survey-06 (unclear room labels)

## V1.031 — 2026-11-02
- Simpler task titles and details; kratos-04 (live task board database) done

## V1.030 — 2026-11-01
- Drop "(provisional)" from the Where to? options

## V1.029 — 2026-11-01
- kratos-02 in progress, owner Branden Adsuara

## V1.028 — 2026-11-01
- Simplify the opening page for visitors; move trip controls, vehicle status and diagnostics to a Controls tab (was My Car)

## V1.027 — 2026-11-01
- Add a short wordmark and route-line intro splash (once per visit, tap to skip)

## V1.026 — 2026-11-01
- Split the page into separate Live map, My Car, Build, About and Team views

## V1.025 — 2026-11-01
- Where to? room 245 is now 215 (map label and dropdown)
- Remove the white SJSU / SME affiliation banner from the Live map and About pages (the header already shows both logos).
- Handoff docs: room 245 is now 215.

## V1.024 — 2026-11-01
- Fix the map compass: true north is about 31 degrees clockwise of plan up (measured from the Google Maps footprint).
- Update the Where to? list and map hotspots to the rooms on the new map (29 rooms, 201-245). Rooms snap to the nearest hallway stop; old rooms not on the map (200, 215, 225, 251, 263, 265) are removed. Default room 227, start room 214. 218B and 219C are not listed (the backend only accepts numeric room ids). Added tools/sync_room_list.py and maps/is_second_floor_rooms.json.
- Replace the tab icon with a W in the app header colors.
- Add CLAUDE.md (Claude Code handoff) and tools/embed_map.py (one-command map refresh).

## V1.023 — 2026-11-01
- Task board claims and status changes go through the claim server in the bots container (waymo-api.adsuaracloud.com); falls back to this server's /api/tasks, then the built-in copy

## V1.022 — 2026-10-30
- Show the version number in the site header (all colorways, desktop and mobile)

## V1.021 — 2026-10-30
- Add a tab logo (favicon) to the site pages

## V1.020 — 2026-10-30
- Show the version in the page headers and stamp it on every bump

## V1.019 — 2026-10-30
- Desktop pages 20 percent larger

## V1.018 — 2026-10-30
- kratos-07 auto-pull confirmed done

## V1.017 — 2026-10-30
- Add design guidance to task detail lines

## V1.016 — 2026-10-29
- Refresh build list: tunnel, task board, auto-pull, main protection, Discord updates

## V1.015 — 2026-10-29
- Task update: kratos-01 done (Branden Adsuara); board serves team_tasks.json while live claims are off

## V1.014 — 2026-10-29
- Team updates: Send an update form posts to Discord; live claims are a separate opt-in

## V1.013 — 2026-10-29
- Auto-pull updater: root-owned install, fast-forward only, rollback and bad-commit skip

## V1.012 — 2026-10-29
- Map: south wall doors 201 to 214 to scale from the 100/65/108 inch pattern

## V1.011 — 2026-10-29
- Add build list to the About page

## V1.010 — 2026-10-29
- Hallway map redrawn as a vector drawing sheet (crisp, estimated, not to scale)

## V1.009 — 2026-10-29
- SME header logo uses the real swoosh colors

## V1.008 — 2026-10-30
- Replace tiny white-backed SJSU and SME header badges with readable transparent supplied logos on desktop and mobile

## V1.007 — 2026-10-30
- Implement approved three-column Waymo-app dashboard with diecast photo, dark survey map, live build stats, team rail and responsive navigation

## V1.006 — draft (unmerged)
- Replace generic concept-vehicle SVG in the app hero with a selected diecast-style car reference render (illustrative, not a build photo).
- Replace illustrated placeholder map with the uploaded October 29 IS Building map, retaining exact image labels, geometry and approximate dimensions.
- Add projected virtual route/vehicle overlay and clickable confirmed-on-image labels without modifying the synthetic navigation graph.
- Document image-source caveats and map calibration tasks for Claude/Mnemosyne.

## V1.005 — draft (unmerged)
- Adapt a dark-navy, app-like visual system with spacious vehicle presentation, rounded dispatch controls, and floating bottom navigation.
- Preserve SJSU/SME logos, six-person team roster, task board, simulator, safety controls, and prior colorways under Appearance.
- Vehicle art is an original schematic concept, not a Waymo asset or proof of physical assembly.
- No backend deployment changes.

## V1.004 — 2026-10-30
- Add Subir Khan, Isabel Burgos, and Brandon Wu to SJSU SME team roster and task-claim name suggestions

## V1.003 — draft (unmerged)
- Add Ride Blue, Midnight Navigation, and Mint Circuit colorway previews across Live Map, About, and the task board.
- Add keyboard-accessible switcher that keeps a preference between pages; original student-project identity retained.
- V1.002 team-board changes remain draft and are included unchanged.

## V1.002 - draft (unmerged)
- Expand build status into assignable task checklist backed by a dedicated authenticated SQLite API.
- Display SJSU wordmark, SME SJSU and Spartan project-affiliation graphics.
- Preserve verified milestone gauge separately from self-reported task status.

# Change log

This log tracks **team repository** revisions only. All merged changes increment exactly one unit:
`V1.000` → `V1.001` → `V1.002` → ... . A merged update is one pull request, even if it modifies several files.

## V1.001 — 2026-10-30
- Simplify About page copy and structure while preserving team, scope, comparison and build status
- Visual refresh: blue/green-on-white palette, minimal header, small Mini-Waymo subtitle, original placeholder icon; no changes to simulation logic

## V1.000 — 2026-10-29
- Created team-ready repository from the Mini-Waymo V12 prototype, ESP32-C3 receive-only MQTT bench suite, and provisional IS Building survey.
- Added version tracking, CI guard, contribution instructions, and Mnemosyne handoff.
- No hardware validation or live deployment implied.
