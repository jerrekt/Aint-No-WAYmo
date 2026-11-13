#!/usr/bin/env python3
"""Generate maps/is_second_floor_drawing.svg: a vector, drawing-sheet style plan of the IS second floor.
Schematic only. The plan is drawn in the 1500x1049 px space used by the page overlay (hotspots and route nodes),
then turned as a whole so true north points up; the turn is written to maps/is_second_floor_frame.json and the page
applies the same transform to its overlay. Rooms, doors and their order come from the posted IS 2nd floor emergency
evacuation plan (photo, 2026-11-12), placed along each hall in proportion. Not to scale, except the south wall doors
201 to 214, which follow BJ's measured pattern (2026-10-29): 100" wall, then 65" door and 108" wall repeating.
Not navigation-ready."""
import sys, math, json, os
OUT = sys.argv[1] if len(sys.argv) > 1 else "maps/is_second_floor_drawing.svg"
P = dict(sheet="#ffffff", line="#111418", floor="#f3f1ea", dim="#1a3f8f", note="#555b66", warn="#b4540a")

# Dimension values and their status come from maps/is_second_floor_dimensions.json; positions stay in this script.
DIMS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "maps", "is_second_floor_dimensions.json")
STATUSES = ("measured", "estimated", "to_measure")
DIMS = {d["id"]: d for d in json.load(open(DIMS_PATH, encoding="utf-8"))["dimensions"]}
for _d in DIMS.values():
    if _d.get("status") not in STATUSES:
        sys.exit(f'{DIMS_PATH}: "{_d.get("id")}" has status {_d.get("status")!r}; use one of {", ".join(STATUSES)}')

def dim(did):
    if did not in DIMS:
        sys.exit(f'{DIMS_PATH}: missing dimension "{did}"')
    return DIMS[did]

def dim_style(status):
    """(colour, dash, prefix): measured is solid, estimated dashed with ~, to_measure amber dashed."""
    return {"measured": (P["dim"], None, ""), "estimated": (P["dim"], "6 4", "~"), "to_measure": (P["warn"], "6 4", "")}[status]

def ft_in(inches):
    ft, inch = divmod(inches, 12)
    return f"{ft}'" if inch == 0 else f"{ft}' {inch}&quot;"
F = "font-family=\"Arial, Helvetica, sans-serif\""
o = []          # plan content, in the 1500x1049 plan space (turned as a group at the end)
deco = []       # sheet furniture drawn upright on the turned canvas: key, compass, title block, note
_to = [o]
def a(s): _to[0].append(s)

def text(x, y, s, size=14, anchor="middle", color=None, weight="normal", extra=""):
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color or P["line"]}" font-weight="{weight}" {F} {extra}>{s}</text>')

def line(x1, y1, x2, y2, w=1, color=None, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or P["line"]}" stroke-width="{w}"{d}/>')

ROOM_LABELS = []   # (room id, x, y, repeated-in-source flag) in SVG px; written to is_second_floor_rooms.json
def label(x, y, s, w=None, dup=False):
    ROOM_LABELS.append((s, x, y, bool(dup)))
    w = w or (14 + 10 * len(s))
    dash = ' stroke-dasharray="4 3"' if dup else ""
    a(f'<g transform="rotate({TRUE_NORTH_CW} {x} {y})">')   # undo the sheet turn so room numbers read upright
    a(f'<rect x="{x-w/2}" y="{y-14}" width="{w}" height="26" rx="2" fill="{P["sheet"]}" stroke="{P["warn"] if dup else P["line"]}" stroke-width="1.2"{dash}/>')
    text(x, y+5, s, 15, weight="bold", color=P["warn"] if dup else None)
    a('</g>')

def door(x, y, side, kind, gap=None):
    """Door gap in a wall at (x,y). side = direction the door swings toward (N,S,E,W)."""
    gap = gap or DOOR_GAP[kind]   # to the south wall scale: single 36", double 72" (BJ, 2026-11-12)
    hx = {"N": (1, 0), "S": (1, 0), "E": (0, 1), "W": (0, 1)}[side]
    nx, ny = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}[side]
    ux, uy = hx
    # erase wall in the gap
    if ux:
        a(f'<rect x="{x-gap/2}" y="{y-5}" width="{gap}" height="10" fill="{P["floor"]}"/>')
    else:
        a(f'<rect x="{x-5}" y="{y-gap/2}" width="10" height="{gap}" fill="{P["floor"]}"/>')
    for s in (-1, 1):  # jambs
        jx, jy = x + ux * s * gap / 2, y + uy * s * gap / 2
        line(jx - nx * 5, jy - ny * 5, jx + nx * 5, jy + ny * 5, 2.2)
    leaves = [(-1, gap)] if kind == "single" else [(-1, gap / 2), (1, gap / 2)]
    for s, L in leaves:
        hxp, hyp = x + ux * s * gap / 2, y + uy * s * gap / 2      # hinge at jamb
        ex, ey = hxp + nx * L, hyp + ny * L                         # open leaf end
        line(hxp, hyp, ex, ey, 1.4)
        cx, cy = hxp - ux * s * L, hyp - uy * s * L                 # closed leaf end
        sweep = 1 if (ux * ny - uy * nx) * (-s) > 0 else 0
        a(f'<path d="M {ex:.1f} {ey:.1f} A {L} {L} 0 0 {sweep} {cx:.1f} {cy:.1f}" fill="none" stroke="{P["line"]}" stroke-width="0.9" stroke-dasharray="3 2"/>')

def arrowline(x1, y1, x2, y2, status="measured"):
    color, dash, _ = dim_style(status)
    line(x1, y1, x2, y2, 1, color, dash)
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    for (px, py, s) in ((x1, y1, 1), (x2, y2, -1)):
        bx, by = px + ux * 10 * s, py + uy * 10 * s
        a(f'<polygon points="{px},{py} {bx-uy*3.2:.1f},{by+ux*3.2:.1f} {bx+uy*3.2:.1f},{by-ux*3.2:.1f}" fill="{color}"/>')

def chain(y, ticks, texts, ext_to=None, ext_from=None, size=12, status="measured"):
    color, dash, prefix = dim_style(status)
    line(ticks[0], y, ticks[-1], y, 1, color, dash)
    for t in ticks:
        line(t, y - 7, t, y + 7, 1.2, color)
        line(t - 4, y + 4, t + 4, y - 4, 1.4, color)
        if ext_from is not None:
            line(t, ext_from, t, y - 8, 0.5, color, "2 3")
    for i, s in enumerate(texts):
        text((ticks[i] + ticks[i + 1]) / 2, y - 8, prefix + s, size, color=color)

def chain_dim(did, y, ticks, size=12):
    """A chain of door and wall widths. to_measure draws the ticks with one 'to measure' label."""
    d = dim(did)
    if d["status"] == "to_measure":
        chain(y, ticks, [], size=size, status="to_measure")
        text((ticks[0] + ticks[-1]) / 2, y - 8, "to measure", size, color=P["warn"])
        return
    segs = d.get("segments") or []
    if len(segs) != len(ticks) - 1:
        sys.exit(f'{DIMS_PATH}: "{did}" needs {len(ticks) - 1} segments to match the drawing, has {len(segs)}')
    chain(y, ticks, [f"{v}&quot;" for v in segs], size=size, status=d["status"])

def span_dim(did, x1, y1, x2, y2, label_xy, rotate=False):
    """One overall span: drawn in its status style, labelled with its value or 'to measure'."""
    d = dim(did)
    color, dash, prefix = dim_style(d["status"])
    line(x1, y1, x2, y2, 1, color, dash)
    for (px, py) in ((x1, y1), (x2, y2)):
        if rotate: line(px - 7, py, px + 7, py, 1.2, color)
        else: line(px, py - 7, px, py + 7, 1.2, color)
    lx, ly = label_xy
    extra = f'transform="rotate(-90 {lx} {ly})"' if rotate else ""
    total = d.get("inches") if d.get("inches") is not None else (sum(d["segments"]) if d.get("segments") else None)
    label = "to measure" if d["status"] == "to_measure" or total is None else prefix + f"{total}&quot;"   # a chain shows its total
    a(f'<rect x="{lx - 40}" y="{ly - 12}" width="80" height="16" fill="{P["sheet"]}" {extra}/>')
    text(lx, ly, label, 11, color=color, extra=extra)

W, H = 1500, 1049   # plan space; the sheet itself is sized after the turn (see the end of this script)

# ---- true north ----
# Brandon Wu, 2026-11-12: phone compass held along the east hall, facing the 222 end (plan up), read 313 deg.
# So plan up points 313 deg and true north is 47 deg clockwise of plan up. The whole plan is turned 47 deg
# counterclockwise so north is straight up. (Earlier estimate from a Google Maps screenshot: 31 deg.)
TRUE_NORTH_CW = 47

# ---- corridor floor (north hall, east hall, south hall) ----
north = (262, 182, 1342, 262)
east = (1160, 262, 1232, 830)
south = (328, 828, 1262, 908)
for (x1, y1, x2, y2) in (north, east, south):
    a(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" fill="{P["floor"]}"/>')
# walls: outline of the C-shaped corridor
walls = [
    ((262, 182), (1342, 182)),            # north outer (top)
    ((262, 262), (1160, 262)),            # north inner (bottom)
    ((1232, 262), (1342, 262)),           # north inner right of east hall
    ((1160, 262), (1160, 828)),           # east hall west wall
    ((1232, 262), (1232, 828)),           # east hall east wall
    ((328, 828), (1160, 828)),            # south inner
    ((1232, 828), (1262, 828)),
    ((328, 908), (1262, 908)),            # south outer
]
for (p, q) in walls:
    line(*p, *q, 5)
# hall end caps with windows
for (x, y1, y2) in ((262, 182, 262), (1342, 182, 262), (328, 828, 908), (1262, 828, 908)):
    line(x, y1, x, y2, 5)
    wy1, wy2 = y1 + 22, y2 - 22
    a(f'<rect x="{x-5}" y="{wy1}" width="10" height="{wy2-wy1}" fill="{P["sheet"]}" stroke="{P["line"]}" stroke-width="1"/>')
    line(x, wy1, x, wy2, 0.8)

# ---- doors: (x, y, swing side, kind) ----
# Order and spacing from the evacuation plan (2026-11-12), scaled along each hall. Single/double is a guess.
NORTH_OUT = [("227", 434, "double"), ("226", 607, "single"), ("225", 794, "double"),
             ("224", 947, "double"), ("223", 1094, "double"), ("222", 1269, "double")]
NORTH_IN = [("228", 483), ("229", 664), ("230", 777), ("UNISEX", 879), ("231B", 986), ("MEN", 1117)]
EAST_OUT = [("221", 320, "single"), ("220A", 373, "single"), ("220", 415, "double"), ("219C", 459, "double"),
            ("219", 545, "double"), ("218", 633, "single"), ("217", 678, "double"), ("216", 764, "single")]
EAST_IN = [("233", 368), ("234", 468), ("235", 620), ("236", 672), ("237", 748)]
SOUTH_IN = [("241", 535), ("240", 855), ("239", 1010)]
D_N = [(x, 182, "N", k) for _, x, k in NORTH_OUT]
D_NS = [(x, 262, "S", "single") for _, x in NORTH_IN]
D_E = [(1232, y, "E", k) for _, y, k in EAST_OUT]
D_W = [(1160, y, "W", "single") for _, y in EAST_IN]
D_S = [(x, 828, "N", "single") for _, x in SOUTH_IN]
# South wall, rooms 201 to 214: to scale from BJ's pattern (2026-10-29), one door each (205 has one door).
# West end of the hall is x=328; 214's door centre stays at x=1168 so the east end lines up with the east hall.
S_PAT = dim("south-wall-pattern")
S_WEST = 328
S_LEAD, S_DOOR, S_WALL = S_PAT["lead"], S_PAT["door"], S_PAT["wall"]   # inches
SOUTH_ROOMS = ["201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", "212", "213", "214"]
S_PX = (1168 - S_WEST) / (S_LEAD + (len(SOUTH_ROOMS) - 1) * (S_DOOR + S_WALL) + S_DOOR / 2)   # px per inch
def s_x(inches): return round(S_WEST + inches * S_PX, 1)
xs_south = [s_x(S_LEAD + k * (S_DOOR + S_WALL) + S_DOOR / 2) for k in range(len(SOUTH_ROOMS))]
S_END_IN = S_LEAD + len(SOUTH_ROOMS) * S_DOOR + (len(SOUTH_ROOMS) - 1) * S_WALL          # east jamb of 214
D_SB = [(x, 908, "S", "single", round(S_DOOR * S_PX, 1)) for x in xs_south]
DOOR_GAP = {"single": round(36 * S_PX, 1), "double": round(72 * S_PX, 1)}
D_END = [(1262, 898, "E", "single")]
for d in D_N + D_NS + D_E + D_W + D_S + D_SB + D_END:
    door(*d)

# ---- elevator, between 236 and 237 on the inner side of the east hall ----
a(f'<rect x="1126" y="690" width="32" height="36" fill="{P["sheet"]}" stroke="{P["line"]}" stroke-width="2"/>')
line(1126, 690, 1158, 726, 1.2); line(1158, 690, 1126, 726, 1.2)
text(1100, 712, "ELEV", 10, color=P["note"], weight="bold")

# ---- restrooms and stairs (from the evacuation plan) ----
for (x, y, w, h, s) in ((852, 262, 54, 40, "UNISEX"), (1090, 262, 54, 40, "MEN"), (1088, 772, 72, 56, "STAIRS")):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{P["line"]}" stroke-width="1.2"/>')
    text(x + w / 2, y + h / 2 + 4, s, 11, color=P["note"], weight="bold")

# ---- room labels ----
for s, x, _ in NORTH_OUT:
    label(x, 166, s, 50)
for s, x in NORTH_IN:
    if s[0].isdigit():
        label(x, 294, s, 60 if len(s) > 3 else 50)
for s, y, _ in EAST_OUT:
    label(1284, y, s, 60 if len(s) > 3 else 50)
for s, y in EAST_IN:
    label(1108, y, s, 50)
for s, x in SOUTH_IN:
    label(x, 803, s, 50)
for x, s in zip(xs_south, SOUTH_ROOMS):
    label(x, 934, s, 42)
label(1310, 901, "215", 50)
# hall / feature callouts
def callout(tx, ty, s1, s2, px, py):
    text(tx, ty, s1, 13, "start"); text(tx, ty + 16, s2, 13, "start")
    line(tx + 78, ty + 4, px, py, 0.8)
text(802, 224, "NORTH HALL", 13, color=P["note"])
text(1196, 560, "EAST HALL", 12, color=P["note"], extra='transform="rotate(-90 1196 560)"')
text(800, 876, "SOUTH HALL", 13, color=P["note"])

# ---- dimensions ----
# Values and status come from the dimensions file. Tick positions are schematic, interpolated from the survey sketch.
def overall(did):
    """(colour, prefix, value text) for an overall length; to_measure has no number."""
    d = dim(did)
    color, _, prefix = dim_style(d["status"])
    if d["status"] == "to_measure" or d.get("inches") is None:
        return P["warn"], "", "to measure"
    return color, prefix, ft_in(d["inches"])
# north hall overall
n = dim("north-hall-length"); color, prefix, val = overall("north-hall-length")
arrowline(262, 92, 1342, 92, n["status"])
line(262, 84, 262, 168, 0.5, color, "3 3"); line(1342, 84, 1342, 168, 0.5, color, "3 3")
a(f'<rect x="680" y="78" width="220" height="26" fill="{P["sheet"]}"/>')
text(790, 98, prefix + val + (f" ({n['inches']}&quot;)" if n.get("inches") else ""), 20, color=color, weight="bold")
GAP = DOOR_GAP
chain_dim("north-wall-doors", 134, [268] + [v for _, x, k in NORTH_OUT[:5] for v in (x - GAP[k] / 2, x + GAP[k] / 2)])
chain_dim("north-inner-doors", 352, [496, 651, 677, 764, 790])
# east hall doors and south hall inner wall
span_dim("east-wall-doors", 1340, 300, 1340, 800, (1352, 560), rotate=True)
span_dim("south-inner-doors", 340, 764, 1060, 764, (700, 768))
# south wall, 201 to 214 (positions and labels follow the measured pattern)
south_in = [0, S_LEAD]
for k in range(len(SOUTH_ROOMS)):
    south_in.append(south_in[-1] + S_DOOR)
    if k < len(SOUTH_ROOMS) - 1:
        south_in.append(south_in[-1] + S_WALL)
south_ticks = [s_x(v) for v in south_in]
south_texts = [f"{S_LEAD}&quot;"] + [f"{S_DOOR}&quot;" if i % 2 == 0 else f"{S_WALL}&quot;" for i in range(len(south_ticks) - 2)]
chain(966, south_ticks, south_texts, ext_from=950, size=10, status=S_PAT["status"])
# past 214 to the east end
e = dim("south-east-end")
ecolor, edash, eprefix = dim_style(e["status"])
line(south_ticks[-1], 966, 1262, 966, 1, ecolor, edash or None); line(1262, 960, 1262, 972, 1.4, ecolor)
etext = "to measure" if e["status"] == "to_measure" or e.get("inches") is None else eprefix + f"{e['inches']}&quot;"
text((south_ticks[-1] + 1262) / 2, 958, etext, 9, color=ecolor)
s_end = s_x(S_END_IN)
scolor, _, sprefix = dim_style(S_PAT["status"])
arrowline(S_WEST, 997, s_end, 997, S_PAT["status"])
line(S_WEST, 960, S_WEST, 1004, 0.5, scolor, "3 3"); line(s_end, 960, s_end, 1004, 0.5, scolor, "3 3")
a(f'<rect x="{(S_WEST + s_end) / 2 - 170}" y="984" width="340" height="26" fill="{P["sheet"]}"/>')
text((S_WEST + s_end) / 2, 1004, f"{sprefix}{ft_in(S_END_IN)} ({S_END_IN}&quot;) WEST END TO 214", 18, color=scolor, weight="bold")
# east side overall
ea = dim("east-hall-length"); color, prefix, val = overall("east-hall-length")
arrowline(1447, 177, 1447, 913, ea["status"])
line(1352, 177, 1460, 177, 0.5, color, "3 3"); line(1270, 913, 1460, 913, 0.5, color, "3 3")
a(f'<rect x="1400" y="510" width="94" height="76" fill="{P["sheet"]}"/>')
text(1447, 548, prefix + val, 20, color=color, weight="bold")
if ea.get("inches"):
    text(1447, 574, f"({ea['inches']}&quot;)", 20, color=color, weight="bold")

# ---- sheet size after the turn ----
# Everything above is plan content (x 250..1495, y 70..1012 in plan px). Turn it about its centre so true north
# points up, then size the sheet to the turned outline plus a margin.
PCX, PCY = 872, 541
def turned(x, y):
    r = math.radians(-TRUE_NORTH_CW)
    dx, dy = x - PCX, y - PCY
    return PCX + dx * math.cos(r) - dy * math.sin(r), PCY + dx * math.sin(r) + dy * math.cos(r)
corners = [turned(x, y) for x, y in ((250, 70), (1495, 70), (1495, 1012), (250, 1012))]
MARGIN = 40
min_x, min_y = min(c[0] for c in corners), min(c[1] for c in corners)
CW = round(max(c[0] for c in corners) - min_x + 2 * MARGIN)
CH = round(max(c[1] for c in corners) - min_y + 2 * MARGIN)
TX, TY = round(MARGIN - min_x, 1), round(MARGIN - min_y, 1)
TRANSFORM = f"translate({TX} {TY}) rotate({-TRUE_NORTH_CW} {PCX} {PCY})"
_to[0] = deco

# ---- dimension legend (top-left) ----
lx, ly = 24, 62   # below the page's "survey map" badge, which sits over the sheet's top-left corner
a(f'<rect x="{lx}" y="{ly}" width="214" height="86" fill="{P["sheet"]}" stroke="{P["line"]}" stroke-width="1.2"/>')
text(lx + 10, ly + 16, "DIMENSIONS", 9, "start", P["note"], "bold")
for i, (status, word) in enumerate((("measured", "Measured on site"), ("estimated", "~ Estimated, not measured"), ("to_measure", "Still to measure"))):
    color, dash, _ = dim_style(status)
    yy = ly + 34 + i * 20
    line(lx + 10, yy, lx + 46, yy, 1.6, color, dash)
    text(lx + 56, yy + 4, word, 12, "start", color)

# ---- compass: the plan is turned, so north is straight up ----
cx, cy = 110, CH - 150
a(f'<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{P["line"]}" stroke-width="1"/>')
a(f'<polygon points="{cx},{cy-42} {cx+8},{cy} {cx},{cy+42} {cx-8},{cy}" fill="{P["line"]}"/>')
a(f'<polygon points="{cx-42},{cy} {cx},{cy-8} {cx+42},{cy} {cx},{cy+8}" fill="none" stroke="{P["line"]}" stroke-width="1.2"/>')
for s, dx, dy, size, wt in (("N", 0, -52, 16, "bold"), ("S", 0, 66, 14, "normal"), ("W", -56, 5, 14, "normal"), ("E", 56, 5, 14, "normal")):
    text(cx + dx, cy + dy, s, size, weight=wt)
text(cx, cy + 92, "N = TRUE NORTH", 12, color=P["note"], weight="bold")
text(cx, cy + 108, f"PLAN TURNED {TRUE_NORTH_CW}&#176; SO NORTH IS UP", 11, color=P["note"])

# ---- sheet title (top-left) and title block (bottom-right) ----
bx, by, bw, bh = CW - 216, CH - 120, 196, 100
a(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{P["sheet"]}" stroke="{P["line"]}" stroke-width="1.6"/>')
for yy in (by + 34, by + 62): line(bx, yy, bx + bw, yy, 0.8)
line(bx + 98, by + 62, bx + 98, by + bh, 0.8)
text(bx + 10, by + 15, "TITLE", 8, "start", P["note"]); text(bx + 10, by + 28, "IS 2ND FLOOR PLAN", 13, "start", weight="bold")
text(bx + 10, by + 46, "STATUS", 8, "start", P["note"]); text(bx + 10, by + 57, "ROOMS FROM EVAC PLAN", 11, "start", P["warn"], "bold")
text(bx + 10, by + 74, "SCALE", 8, "start", P["note"]); text(bx + 10, by + 92, "NTS", 16, "start", weight="bold")
text(bx + 108, by + 74, "UNITS", 8, "start", P["note"]); text(bx + 108, by + 92, "IN / FT", 14, "start", weight="bold")
text(30, CH - 14, "Rooms and doors from the posted evacuation plan, spaced in proportion along each hall. Hall lengths not to scale. Dimension status: see the key.", 12, "start", color=P["note"])
sheet = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CW} {CH}" width="{CW}" height="{CH}">',
         f'<rect width="{CW}" height="{CH}" fill="{P["sheet"]}"/>',
         f'<rect x="5" y="5" width="{CW-10}" height="{CH-10}" fill="none" stroke="{P["line"]}" stroke-width="2"/>',
         f'<rect x="11" y="11" width="{CW-22}" height="{CH-22}" fill="none" stroke="{P["line"]}" stroke-width="0.8"/>',
         f'<g transform="{TRANSFORM}">'] + o + ['</g>'] + deco + ['</svg>']
open(OUT, "w", encoding="utf-8").write("\n".join(sheet))
print("wrote", OUT, len("\n".join(sheet)), "bytes")
frame_path = os.path.join(os.path.dirname(OUT) or ".", "is_second_floor_frame.json")
with open(frame_path, "w", encoding="utf-8") as fh:
    json.dump({"note": "Sheet size and the plan-to-sheet transform, generated by tools/build_map_svg.py. The page draws its overlay "
                       "(route, car, room and dimension tap areas) in plan px inside this transform. Read by tools/embed_map.py.",
               "w": CW, "h": CH, "transform": TRANSFORM, "true_north_cw": TRUE_NORTH_CW}, fh, indent=1)
print("wrote", frame_path, CW, "x", CH)
# Tap areas for each dimension on the page, [x, y, w, h] in the same 1500x1049 space. tools/embed_map.py
# puts them in the page with the values from the dimensions file.
DIM_HITS = {
    "north-hall-length": [262, 76, 1080, 30],
    "north-wall-doors": [268, 116, 1068, 26],
    "north-inner-doors": [490, 340, 310, 26],
    "east-wall-doors": [1326, 300, 30, 500],
    "south-inner-doors": [340, 748, 720, 26],
    "south-wall-pattern": [S_WEST, 952, round(s_end - S_WEST, 1), 58],   # below the room tap areas (y up to 950)
    "south-east-end": [south_ticks[-1], 952, round(1262 - south_ticks[-1], 1), 24],
    "east-hall-length": [1400, 177, 94, 736],
}
missing = sorted(set(DIMS) - set(DIM_HITS))
if missing:
    sys.exit(f'{DIMS_PATH}: no tap area for {", ".join(missing)}; add it to DIM_HITS in tools/build_map_svg.py')
hits_path = os.path.join(os.path.dirname(OUT) or ".", "is_second_floor_dimension_hits.json")
with open(hits_path, "w", encoding="utf-8") as fh:
    json.dump({"note": "Dimension tap areas [x, y, w, h] in the 1500x1049 SVG space, generated by tools/build_map_svg.py. Read by tools/embed_map.py.",
               "hits": DIM_HITS}, fh, indent=1)
print("wrote", hits_path, len(DIM_HITS), "tap areas")
rooms_path = os.path.join(os.path.dirname(OUT) or ".", "is_second_floor_rooms.json")
with open(rooms_path, "w", encoding="utf-8") as fh:
    json.dump({"note": "Room label centres in the 1500x1049 SVG space, generated by tools/build_map_svg.py. Feed tools/sync_room_list.py.",
               "rooms": [{"room": s, "x": x, "y": y, "repeated_label": d} for s, x, y, d in ROOM_LABELS]}, fh, indent=1)
print("wrote", rooms_path, len(ROOM_LABELS), "labels")
