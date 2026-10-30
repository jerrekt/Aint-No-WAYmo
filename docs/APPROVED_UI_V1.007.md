# Ain't No Waymo — Approved dashboard implementation V1.007 (draft)

## Design baseline
- Approved visual reference: user-approved three-column dark navy mockup (October 29, 2026).
- Actual implementation: `Mini_Waymo_V12_Demo.html` (legacy filename; live site source), which contains V1.007 CSS and script blocks.
- Standalone preview: `Aint_No_Waymo_V1.007_Interactive_Draft.html` in the delivery package.
- Desktop layout: left vehicle/dispatch rail, center uploaded IS Building map and simulator, right verified progress and team.
- Mobile: stacked panels with five-item floating dock.
- Header uses SJSU and SJSU SME logos from project assets.
- Selected vehicle picture is a derivative of the **user-provided white Waymo I-PACE diecast reference photo** (`assets/diecast-car-transparent.webp`), not evidence of a completed robot.
- `assets/mockup-layout-v1.007.css` and `assets/mockup-layout-v1.007.js` are the authored style and layout source. They are also inlined in the standalone HTML.

## What changed in behavior
- No core navigation, command payload, firmware or safety logic modified.
- Existing live DOM nodes moved into visual rails; listener identity is preserved.
- Go to 263, Add Stop, Pause, Resume, Stop, simulated E-stop and sensor tools retain their original event handlers.
- Floating dock: Live map, Build (opens task board), My Car (vehicle card), About, Team (roster).
- Gear opens Admin/Guest **preview** selection. It does not grant backend access; role permission is enforced by the server separately.
- Status on vehicle is deliberately **SIM ONLY**; the site must not claim real hardware is online.
- Right panel reads the current major milestone percentage from `#projectProgressPercent`; seeded task counts are from `boardTasksFallback` and explicitly marked as a preview. For live server counts, wire to authenticated team task API.
- The old three colorways have been retired from the site navigation to keep the approved visual identity consistent.

## Map
- The visual background is a palette-transformed copy of `maps/reference/is_building_user_map_2026-10-29.png` preserving its exact room positions and screenshot geometry. Derived image: `maps/reference/is_building_dark_presentation.png`.
- Map is ~168 ft north, ~168 ft south, ~300 ft east **approximate iPhone hallway estimates**. Individual door coordinates are provisional.
- Current SVG vehicle/route overlay uses synthetic graph coordinates; it is not physical localization.
- Original source image is retained for audit/correction; some room labels (e.g. 205 and 223) are duplicated in the supplied drawing.

## Deployment and team notes
- Do not deploy yet without reviewing live Kratos service settings, authentication, and MQTT access rules.
- Task claims require the Kratos FastAPI+SQLite endpoint and backend-provided secret; standalone file is a **read-only/offline preview**.
- Do not put the shared task-board password or Cloudflare tunnel token in Git or Mnemosyne.
- University and Waymo/Opera are contextual affiliations only; this is an independently operated SJSU SME student project.
- Tag/version format must advance one increment per merged change, e.g. `V1.006 -> V1.007`; draft files are not proof of merged release.

## Validation
- Browser loaded with `page.set_content` due environment restrictions on `file://` navigation.
- Desktop 1536px, tablet 1000px, mobile 390px: no page JavaScript errors and no horizontal overflow.
- Go to IS263, Pause, Stop, task-board expansion, map/team navigation, view settings verified.
- Node controller/navigation tests pass; Python backend/team tests have no failures, with expected deprecated FastAPI startup-hook warnings.
- Physical ESP32 and Kratos deployment remain unverified.
