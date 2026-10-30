## V1.017 — 2026-10-29
- kratos-07 auto-pull confirmed done

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
