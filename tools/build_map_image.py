#!/usr/bin/env python3
"""Build the Live map from the Facilities floor plan image (replaces the hand-drawn tools/build_map_svg.py sheet).

Inputs (maps/):
  is_second_floor_base.jpg          the SJSU Facilities "Corporation Yard Map #29" sheet of the IS 2nd floor, cropped
  is_second_floor_image_points.json hallway stops (nodes) and room-number positions measured on that image, in plan px

Outputs (maps/):
  is_second_floor_drawing.svg       the image turned so true north is up, plus an upright compass and a note
  is_second_floor_frame.json        sheet size and the plan-to-sheet transform the page applies to its overlay
  is_second_floor_rooms.json        room positions for tools/sync_room_list.py
  is_second_floor_dimension_hits.json  empty: the image has no dimension tap areas
and DISPLAY_NODES in Mini_Waymo_V12_Demo.html (where each simulator stop is drawn).

Full refresh:
    python3 tools/build_map_image.py && python3 tools/sync_room_list.py && python3 tools/embed_map.py

North: on the sheet, plan-up of the old drawing (the 222 end of the base hall) is image-left. Brandon's phone on that
hall read 313 deg (2026-11-12), so true north is 47 deg clockwise of image-left; turning the image 90 - 47 = 43 deg
clockwise puts north straight up.
"""
import base64
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "maps"
PAGE = ROOT / "Mini_Waymo_V12_Demo.html"
pts = json.loads((MAPS / "is_second_floor_image_points.json").read_text(encoding="utf-8"))
img = pts["image"]
W, H = img["width"], img["height"]
TURN = 90 - pts["true_north_cw_of_left"]          # degrees clockwise applied to the plan

# ---- sheet size: the turned image plus a margin
CX, CY = W / 2, H / 2
def turned(x, y):
    r = math.radians(TURN)
    dx, dy = x - CX, y - CY
    return CX + dx * math.cos(r) - dy * math.sin(r), CY + dx * math.sin(r) + dy * math.cos(r)
corners = [turned(x, y) for x, y in ((0, 0), (W, 0), (W, H), (0, H))]
MARGIN = 30
min_x, min_y = min(c[0] for c in corners), min(c[1] for c in corners)
SW = round(max(c[0] for c in corners) - min_x + 2 * MARGIN)
SH = round(max(c[1] for c in corners) - min_y + 2 * MARGIN)
TX, TY = round(MARGIN - min_x, 1), round(MARGIN - min_y, 1)
TRANSFORM = f"translate({TX} {TY}) rotate({TURN} {CX:g} {CY:g})"

# ---- SVG
b64 = base64.b64encode((MAPS / img["file"]).read_bytes()).decode("ascii")
mime = "image/jpeg" if img["file"].lower().endswith((".jpg", ".jpeg")) else "image/png"
ink, note = "#14171a", "#55606b"
def text(x, y, s, size, anchor="middle", color=ink, weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{color}" font-weight="{weight}">{s}</text>')
cx, cy = 90, SH - 150
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SW} {SH}" width="{SW}" height="{SH}">',
       f'<rect width="{SW}" height="{SH}" fill="#ffffff"/>',
       f'<g transform="{TRANSFORM}"><image href="data:{mime};base64,{b64}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="none"/></g>',
       # compass: the sheet is turned, so north is straight up
       f'<circle cx="{cx}" cy="{cy}" r="34" fill="#ffffff" stroke="{ink}" stroke-width="1"/>',
       f'<polygon points="{cx},{cy-42} {cx+8},{cy} {cx},{cy+42} {cx-8},{cy}" fill="{ink}"/>',
       f'<polygon points="{cx-42},{cy} {cx},{cy-8} {cx+42},{cy} {cx},{cy+8}" fill="none" stroke="{ink}" stroke-width="1.2"/>',
       text(cx, cy - 52, "N", 16, weight="bold"), text(cx, cy + 66, "S", 14),
       text(cx - 56, cy + 5, "W", 14), text(cx + 56, cy + 5, "E", 14),
       text(cx, cy + 92, "N = TRUE NORTH", 12, color=note, weight="bold"),
       text(SW - 24, SH - 18, "Base plan: SJSU Facilities, IS Bldg 181 second floor (Corporation Yard Map #29). "
            f"Turned {TURN}&#176; so north is up. Not to scale.", 12, "end", note),
       '</svg>']
(MAPS / "is_second_floor_drawing.svg").write_text("\n".join(svg), encoding="utf-8")

# ---- frame, rooms, empty dimension hits
(MAPS / "is_second_floor_frame.json").write_text(json.dumps({
    "note": "Sheet size and the plan-to-sheet transform, written by tools/build_map_image.py. The page draws its overlay "
            "(route, car, room tap areas) in plan px inside this transform. Read by tools/embed_map.py.",
    "w": SW, "h": SH, "transform": TRANSFORM, "turn": TURN,
    "true_north_cw": pts["true_north_cw_of_left"], "lane_px": pts["lane_px"]}, indent=1) + "\n", encoding="utf-8")
(MAPS / "is_second_floor_rooms.json").write_text(json.dumps({
    "note": "Room-number positions on the base image (plan px), from maps/is_second_floor_image_points.json.",
    "rooms": [{"room": r, "x": x, "y": y, "repeated_label": False} for r, (x, y) in pts["rooms"].items()]},
    indent=1) + "\n", encoding="utf-8")
(MAPS / "is_second_floor_dimension_hits.json").write_text(json.dumps({
    "note": "The Facilities image has no dimension tap areas; dimensions stay in is_second_floor_dimensions.json.",
    "hits": {}}, indent=1) + "\n", encoding="utf-8")

# ---- DISPLAY_NODES in the page
page = PAGE.read_text(encoding="utf-8")
pat = re.compile(r"const DISPLAY_NODES=\{.*?\};")
if len(pat.findall(page)) != 1:
    raise SystemExit("DISPLAY_NODES not found exactly once in " + PAGE.name)
nodes = json.dumps(pts["nodes"], separators=(",", ":"))
new = pat.sub(lambda m: "const DISPLAY_NODES=" + nodes + ";", page)
if new != page:
    PAGE.write_text(new, encoding="utf-8")
print(f"wrote drawing {SW}x{SH}, turn {TURN} deg, {len(pts['rooms'])} rooms, {len(pts['nodes'])} stops")
