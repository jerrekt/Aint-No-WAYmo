#!/usr/bin/env python3
"""Generate maps/is_second_floor_drawing.svg: a vector, drawing-sheet style plan of the IS second floor.
Schematic only. Geometry follows the 1500x1049 px space used by the page overlay (hotspots and route nodes).
Door positions are estimates from the user survey sketch. Not to scale, except the south wall doors 201 to 214,
which follow BJ's stated pattern (2026-10-29): 100" wall, then 65" door and 108" wall repeating. Not navigation-ready."""
import sys, math
OUT = sys.argv[1] if len(sys.argv) > 1 else "maps/is_second_floor_drawing.svg"
P = dict(sheet="#ffffff", line="#111418", floor="#f3f1ea", dim="#1a3f8f", note="#555b66", warn="#b4540a")
F = "font-family=\"Arial, Helvetica, sans-serif\""
o = []
a = o.append

def text(x, y, s, size=14, anchor="middle", color=None, weight="normal", extra=""):
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color or P["line"]}" font-weight="{weight}" {F} {extra}>{s}</text>')

def line(x1, y1, x2, y2, w=1, color=None, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or P["line"]}" stroke-width="{w}"{d}/>')

def label(x, y, s, w=None, dup=False):
    w = w or (14 + 10 * len(s))
    dash = ' stroke-dasharray="4 3"' if dup else ""
    a(f'<rect x="{x-w/2}" y="{y-14}" width="{w}" height="26" rx="2" fill="{P["sheet"]}" stroke="{P["warn"] if dup else P["line"]}" stroke-width="1.2"{dash}/>')
    text(x, y+5, s, 15, weight="bold", color=P["warn"] if dup else None)

def door(x, y, side, kind, gap=None):
    """Door gap in a wall at (x,y). side = direction the door swings toward (N,S,E,W)."""
    gap = gap or (26 if kind == "single" else 34)
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

def arrowline(x1, y1, x2, y2):
    line(x1, y1, x2, y2, 1, P["dim"])
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    for (px, py, s) in ((x1, y1, 1), (x2, y2, -1)):
        bx, by = px + ux * 10 * s, py + uy * 10 * s
        a(f'<polygon points="{px},{py} {bx-uy*3.2:.1f},{by+ux*3.2:.1f} {bx+uy*3.2:.1f},{by-ux*3.2:.1f}" fill="{P["dim"]}"/>')

def chain(y, ticks, texts, ext_to=None, ext_from=None, size=12):
    line(ticks[0], y, ticks[-1], y, 1, P["dim"])
    for t in ticks:
        line(t, y - 7, t, y + 7, 1.2, P["dim"])
        line(t - 4, y + 4, t + 4, y - 4, 1.4, P["dim"])
        if ext_from is not None:
            line(t, ext_from, t, y - 8, 0.5, P["dim"], "2 3")
    for i, s in enumerate(texts):
        text((ticks[i] + ticks[i + 1]) / 2, y - 8, s, size, color=P["dim"])

W, H = 1500, 1049
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
a(f'<rect width="{W}" height="{H}" fill="{P["sheet"]}"/>')
a(f'<rect x="5" y="5" width="{W-10}" height="{H-10}" fill="none" stroke="{P["line"]}" stroke-width="2"/>')
a(f'<rect x="11" y="11" width="{W-22}" height="{H-22}" fill="none" stroke="{P["line"]}" stroke-width="0.8"/>')

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
D_N = [(434, 182, "N", "double"), (624, 182, "N", "single"), (811, 182, "N", "double"),
       (979, 182, "N", "double"), (1133, 182, "N", "double"), (1288, 182, "N", "double")]
D_NS = [(516, 262, "S", "single"), (718, 262, "S", "single"), (909, 262, "S", "single")]
D_E = [(1232, 354, "E", "double"), (1232, 412, "E", "single"), (1232, 470, "E", "double"),
       (1232, 528, "E", "double"), (1232, 630, "E", "double"), (1232, 695, "E", "single"),
       (1232, 766, "E", "single")]
D_W = [(1160, 335, "W", "single"), (1160, 660, "W", "single")]
D_S = [(519, 828, "N", "single"), (745, 828, "N", "single"), (977, 828, "N", "single")]
# South wall, rooms 201 to 214: to scale from BJ's pattern (2026-10-29), one door each (205 has one door).
# West end of the hall is x=328; 214's door centre stays at x=1168 so the east end lines up with the east hall.
S_WEST, S_LEAD, S_DOOR, S_WALL = 328, 100, 65, 108          # inches
SOUTH_ROOMS = ["201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", "212", "213", "214"]
S_PX = (1168 - S_WEST) / (S_LEAD + (len(SOUTH_ROOMS) - 1) * (S_DOOR + S_WALL) + S_DOOR / 2)   # px per inch
def s_x(inches): return round(S_WEST + inches * S_PX, 1)
xs_south = [s_x(S_LEAD + k * (S_DOOR + S_WALL) + S_DOOR / 2) for k in range(len(SOUTH_ROOMS))]
S_END_IN = S_LEAD + len(SOUTH_ROOMS) * S_DOOR + (len(SOUTH_ROOMS) - 1) * S_WALL          # east jamb of 214
D_SB = [(x, 908, "S", "single", round(S_DOOR * S_PX, 1)) for x in xs_south]
D_END = [(1262, 898, "E", "single")]
for d in D_N + D_NS + D_E + D_W + D_S + D_SB + D_END:
    door(*d)

# ---- elevator ----
a(f'<rect x="1136" y="570" width="30" height="56" fill="{P["sheet"]}" stroke="{P["line"]}" stroke-width="2"/>')
line(1136, 570, 1166, 626, 1.2); line(1166, 570, 1136, 626, 1.2)

# ---- unconfirmed rooms taken from the user's markup (dashed) ----
for (x, y, w, h, s) in ((1058, 262, 54, 46, "UNISEX"), (1088, 772, 72, 56, "STAIRS")):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{P["warn"]}" stroke-width="1.4" stroke-dasharray="6 4"/>')
    text(x + w / 2, y + h / 2 + 4, s, 11, color=P["warn"], weight="bold")
text(1085, 322, "BATH (UNCONFIRMED)", 10, color=P["warn"])

# ---- room labels ----
dups = {(680, 934), (1133, 166)}
for x, s in ((434, "227"), (624, "226"), (811, "224"), (979, "223"), (1133, "223"), (1288, "222")):
    label(x, 166, s, 50, dup=(x, 166) in {(1133, 166)})
for x, s in ((516, "229"), (909, "230")):
    label(x, 294, s, 50)
for y, s in ((354, "220"), (412, "221"), (470, "219C"), (528, "218B"), (630, "217"), (695, "216"), (766, "216")):
    label(1284, y, s, 60 if len(s) > 3 else 50)
for x, s in ((519, "241"), (745, "240"), (977, "239")):
    label(x, 803, s, 50)
for x, s in zip(xs_south, SOUTH_ROOMS):
    label(x, 934, s, 42)
label(1310, 901, "245", 50)
# hall / feature callouts
def callout(tx, ty, s1, s2, px, py):
    text(tx, ty, s1, 13, "start"); text(tx, ty + 16, s2, 13, "start")
    line(tx + 78, ty + 4, px, py, 0.8)
callout(1030, 352, "Men's", "Bathroom", 1160, 335)
callout(1030, 678, "Women's", "Bathroom", 1160, 660)
text(1130, 600, "Elevator", 13, "end")
text(802, 224, "NORTH HALL", 13, color=P["note"])
text(1196, 560, "EAST HALL", 12, color=P["note"], extra='transform="rotate(-90 1196 560)"')
text(800, 876, "SOUTH HALL", 13, color=P["note"])

# ---- dimensions ----
top_ticks = [268, 402, 466, 596, 650, 792, 830, 972, 1006, 1148, 1336]
# top chain is schematic: tick positions interpolated from the label positions in the survey sketch
top_texts = ['100"', '65"', '108"', '65"', '108"', '65"', '108"', '65"', '108"', '65"']
# overall 168' string
arrowline(262, 92, 1342, 92)
line(262, 84, 262, 168, 0.5, P["dim"], "3 3"); line(1342, 84, 1342, 168, 0.5, P["dim"], "3 3")
a(f'<rect x="690" y="78" width="200" height="26" fill="{P["sheet"]}"/>')
text(790, 98, "168' (2016&quot;)", 20, color=P["dim"], weight="bold")
chain(134, top_ticks, top_texts)
chain(290, [546, 633, 709, 810, 880], ['100"', '65"', '108"', '65"'])
south_in = [0, S_LEAD]
for k in range(len(SOUTH_ROOMS)):
    south_in.append(south_in[-1] + S_DOOR)
    if k < len(SOUTH_ROOMS) - 1:
        south_in.append(south_in[-1] + S_WALL)
south_ticks = [s_x(v) for v in south_in]
south_texts = ['100"'] + ['65"' if i % 2 == 0 else '108"' for i in range(len(south_ticks) - 2)]
chain(966, south_ticks, south_texts, ext_from=950, size=10)
# past 214 to the east end: not measured
line(south_ticks[-1], 966, 1262, 966, 1, P["dim"], "4 3"); line(1262, 960, 1262, 972, 1.4, P["dim"])
text((south_ticks[-1] + 1262) / 2, 958, "not measured", 9, color=P["warn"])
s_end = s_x(S_END_IN)
arrowline(S_WEST, 997, s_end, 997)
line(S_WEST, 960, S_WEST, 1004, 0.5, P["dim"], "3 3"); line(s_end, 960, s_end, 1004, 0.5, P["dim"], "3 3")
ft, inch = divmod(S_END_IN, 12)
a(f'<rect x="{(S_WEST + s_end) / 2 - 170}" y="984" width="340" height="26" fill="{P["sheet"]}"/>')
text((S_WEST + s_end) / 2, 1004, f"{ft}' {inch}&quot; ({S_END_IN}&quot;) WEST END TO 214", 18, color=P["dim"], weight="bold")
# 300' on the east side
arrowline(1447, 177, 1447, 913)
line(1352, 177, 1460, 177, 0.5, P["dim"], "3 3"); line(1270, 913, 1460, 913, 0.5, P["dim"], "3 3")
a(f'<rect x="1400" y="510" width="94" height="76" fill="{P["sheet"]}"/>')
text(1447, 548, "300'", 20, color=P["dim"], weight="bold"); text(1447, 574, "(3600&quot;)", 20, color=P["dim"], weight="bold")

# ---- compass ----
# Plan "up" is the building's own north. Measured from the Google Maps footprint (2026-10-30, north-up screenshot),
# the building's long axis tilts 31 deg west of true north, so true north points 31 deg clockwise of plan-up.
TRUE_NORTH_CW = 31
cx, cy = 125, 860
def rot(dx, dy, deg=TRUE_NORTH_CW):
    r = math.radians(deg)
    return dx * math.cos(r) - dy * math.sin(r), dx * math.sin(r) + dy * math.cos(r)
a(f'<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{P["line"]}" stroke-width="1"/>')
a(f'<g transform="rotate({TRUE_NORTH_CW} {cx} {cy})">')
a(f'<polygon points="{cx},{cy-42} {cx+8},{cy} {cx},{cy+42} {cx-8},{cy}" fill="{P["line"]}"/>')
a(f'<polygon points="{cx-42},{cy} {cx},{cy-8} {cx+42},{cy} {cx},{cy+8}" fill="none" stroke="{P["line"]}" stroke-width="1.2"/>')
a('</g>')
for s, (dx, dy), size, wt in (("N", (0, -57), 16, "bold"), ("S", (0, 61), 14, "normal"), ("W", (-56, 0), 14, "normal"), ("E", (56, 0), 14, "normal")):
    rx, ry = rot(dx, dy)
    text(round(cx + rx, 1), round(cy + ry + 5, 1), s, size, weight=wt)   # letters stay upright; positions follow the rose
text(cx, cy + 90, "N = TRUE NORTH", 12, color=P["note"], weight="bold")
text(cx, cy + 106, f"{TRUE_NORTH_CW}&#176; RIGHT OF PLAN UP", 11, color=P["note"])

# ---- sheet title (top-left) and title block (bottom-right) ----
bx, by, bw, bh = 1290, 936, 196, 100
a(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{P["sheet"]}" stroke="{P["line"]}" stroke-width="1.6"/>')
for yy in (by + 34, by + 62): line(bx, yy, bx + bw, yy, 0.8)
line(bx + 98, by + 62, bx + 98, by + bh, 0.8)
text(bx + 10, by + 15, "TITLE", 8, "start", P["note"]); text(bx + 10, by + 28, "IS 2ND FLOOR PLAN", 13, "start", weight="bold")
text(bx + 10, by + 46, "STATUS", 8, "start", P["note"]); text(bx + 10, by + 57, "ESTIMATED, NOT SURVEYED", 11, "start", P["warn"], "bold")
text(bx + 10, by + 74, "SCALE", 8, "start", P["note"]); text(bx + 10, by + 92, "NTS", 16, "start", weight="bold")
text(bx + 108, by + 74, "UNITS", 8, "start", P["note"]); text(bx + 108, by + 92, "IN / FT", 14, "start", weight="bold")
text(30, 1030, "Door positions estimated from a hand sketch. Dashed orange = unconfirmed. South doors 201 to 214 follow the stated 100/65/108 inch pattern; label 223 repeats in the source.", 12, "start", color=P["note"])
a('</svg>')
open(OUT, "w", encoding="utf-8").write("\n".join(o))
print("wrote", OUT, len("\n".join(o)), "bytes")
