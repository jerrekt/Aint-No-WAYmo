# IS Building second floor survey — UNVERIFIED door coordinates

**2026-11-12:** rooms, doors and their order now follow the posted emergency evacuation plan (`reference/evacuation-plan-2026-11-12.pdf`). Doors are 36" single, 72" double (BJ). True north is 47° clockwise of plan-up (phone compass on the east hall, 313°); the drawing is turned so north is up. Hall lengths are still estimates.

These are **working references**, not a surveyed/approved floor plan and not navigation-ready robot coordinates.

- `reference/original-hand-drawn-survey.png` — user's initial survey sketch.
- `reference/user-annotated-survey-oct29.jpeg` — user markup correcting room locations, bathrooms, stairs, elevator. **Prefer this for change requests.**
- `reference/previous-estimated-map.png` — generated cleaned map before the last added aviation-club-room revision; still contains assumptions. Do not infer missing doors from it.
- `is_second_floor_provisional_map.json` — earlier rough geometry that may conflict with latest annotations; treat only as a starting point.

Measurements: **north hall about 168 ft, south hall about 168 ft, east hall about 300 ft**. Measurements were estimated from an iPhone Measure app; not precise architectural dimensions. The user confirmed the south room sequence 200–214 as a concept, but past generated images contained duplicate labels; final spatial coordinates remain unverified.

Most recent user corrections: elevator moves one room interval north, two IS 216 doors (one double, one single), no old bottom IS 216, **Aviation Club Room below those two doors**, upper east men's bathroom; unisex bathroom around the north inner corner from user annotation; women's bathroom below elevator; stairs near lower interior corner. More review required before physical navigation.

**Avoid replacing source map with image-generator redraws for minor edits; preserve user-confirmed corridor geometry and apply precise vector edits instead.**

## Updating a measurement
Every dimension on the map comes from `is_second_floor_dimensions.json`. Each entry has a `status`:

- `measured`: taken on site with a tape or laser. Drawn solid blue.
- `estimated`: from a sketch, Google Maps or a copied pattern. Drawn dashed with `~` before the number.
- `to_measure`: no number yet. Drawn amber with "to measure".

To record a new measurement, change the entry's number (`inches`, `segments`, or the south wall's `lead`/`door`/`wall`), set `status` to `measured`, and fill in `source`, `measured_by` and `date`. Keep everything in inches. A chain's `segments` must keep the same count as the drawing has gaps; the script stops with a message if it doesn't. Then run the refresh below.

Not a coder? Tap the dimension on the Live map. Its card shows the status and source; enter the new number there and press **Send to Discord** (team password) or **Copy for Discord**. Someone then copies it into this file by pull request. The tap areas come from `DIM_HITS` in `tools/build_map_svg.py`, written to `is_second_floor_dimension_hits.json` and embedded by `tools/embed_map.py`; a new dimension needs a tap area there too.

## After changing the map
Run `python3 tools/build_map_svg.py && python3 tools/sync_room_list.py`, then re-embed the SVG as `SURVEY_IMAGE_URI` in `Mini_Waymo_V12_Demo.html` and run the node tests in `tests/`. `sync_room_list.py` refreshes the Where to? list and map hotspots from `maps/is_second_floor_rooms.json`; rooms snap to the nearest hallway stop, and only all-digit room numbers are listed.
