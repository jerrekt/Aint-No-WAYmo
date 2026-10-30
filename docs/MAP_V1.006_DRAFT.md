# V1.006 draft — Use the user-provided IS second floor map

The Live Map now uses the uploaded `/maps/reference/is_building_user_map_2026-10-29.png` exactly as received, without image-generator redraws. The source is inlined in the offline single-file HTML so the demo opens from disk. A source copy is retained under `maps/reference`.

**Important limitations:** The existing C-shaped graph, distances, room-to-node mappings, synthetic motion, scans and route planner are **unchanged**. Their positions are projected onto the reference image for demonstration only. This does not convert the simulation into a calibrated map or guarantee that the displayed blue route stays within surveyed corridors. Only a subset of drawn rooms (e.g. 202, 204, 205, 208, 210, 212, 220, 230, 240) has an overlaid clickable hitbox; unlabeled simulator destinations, including IS 263, must be chosen through the dropdown. Correcting other rooms requires real survey data, not a guess.

Known source-image limitations: approximate measurements, repeated labels (205 and 223), missing room 200, and room locations yet to be verified. Do not silently interpret duplicate or uncertain labels as distinct destinations. North and south travel length estimates are 168 ft, east 300 ft, measured approximately with the iPhone Measure app.

`maps/is_second_floor_user_map_overlay.json` stores editable image hotspots and provisional graph projections. The back-end provisional map remains separate and must not be represented as physically accurate.

All other V1.005 app styling, About, build board, tasks, safety controls and software simulation logic are preserved. No actual server deployment is implied.
