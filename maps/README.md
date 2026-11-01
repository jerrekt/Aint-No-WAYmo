# IS Building second floor survey — UNVERIFIED door coordinates

These are **working references**, not a surveyed/approved floor plan and not navigation-ready robot coordinates.

- `reference/original-hand-drawn-survey.png` — user's initial survey sketch.
- `reference/user-annotated-survey-oct29.jpeg` — user markup correcting room locations, bathrooms, stairs, elevator. **Prefer this for change requests.**
- `reference/previous-estimated-map.png` — generated cleaned map before the last added aviation-club-room revision; still contains assumptions. Do not infer missing doors from it.
- `is_second_floor_provisional_map.json` — earlier rough geometry that may conflict with latest annotations; treat only as a starting point.

Measurements: **north hall about 168 ft, south hall about 168 ft, east hall about 300 ft**. Measurements were estimated from an iPhone Measure app; not precise architectural dimensions. The user confirmed the south room sequence 200–214 as a concept, but past generated images contained duplicate labels; final spatial coordinates remain unverified.

Most recent user corrections: elevator moves one room interval north, two IS 216 doors (one double, one single), no old bottom IS 216, **Aviation Club Room below those two doors**, upper east men's bathroom; unisex bathroom around the north inner corner from user annotation; women's bathroom below elevator; stairs near lower interior corner. More review required before physical navigation.

**Avoid replacing source map with image-generator redraws for minor edits; preserve user-confirmed corridor geometry and apply precise vector edits instead.**

## After changing the map
Run `python3 tools/build_map_svg.py && python3 tools/sync_room_list.py`, then re-embed the SVG as `SURVEY_IMAGE_URI` in `Mini_Waymo_V12_Demo.html` and run the node tests in `tests/`. `sync_room_list.py` refreshes the Where to? list and map hotspots from `maps/is_second_floor_rooms.json`; rooms snap to the nearest hallway stop, and only all-digit room numbers are listed.
