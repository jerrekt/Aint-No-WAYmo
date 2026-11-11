#!/usr/bin/env python3
"""Draw assets/wiring.svg, the wiring plan on the Build page.

Keep this in step with the pin map in handoff/handoffs/SUBIR_HANDOFF.md.
Wire colours in the drawing are the team's real wire colour code, so the picture
matches the harness: black GND, red battery +, orange motor rail, white 3V3,
blue SDA, green SCL, yellow signals.

Run: python3 tools/build_wiring_svg.py
"""
from pathlib import Path

W, H = 1300, 960
BOX = '#1e52a4'; INK = '#1b2a3a'; MUT = '#5a6b7c'; BG = '#f7fafc'
C = {  # wire colour code
    'gnd': '#1b1b1b', 'bat': '#d32f2f', 'rail': '#ef7d00', 'v33': '#aab4bf',
    'sda': '#1e6fd9', 'scl': '#2e9d4f', 'sig': '#d9a400', 'motor': '#c2185b',
}
out = []


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def txt(x, y, s, size=13, col=INK, anchor='start', bold=False):
    b = ' font-weight="700"' if bold else ''
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(s)}</text>')


def box(x, y, w, h, title, sub='', col=BOX, ts=15, sub2=''):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#ffffff" stroke="{col}" stroke-width="2.4"/>')
    lines = [s for s in (sub, sub2) if s]
    ty = y + h / 2 + 5 - 9 * len(lines)
    if title:
        txt(x + w / 2, ty, title, ts, INK, 'middle', True)
    for i, s in enumerate(lines):
        txt(x + w / 2, ty + 18 * (i + 1), s, 12, MUT, 'middle')


def wire(pts, col, w=3, dash=''):
    d = ' '.join(f'{x},{y}' for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ''
    # white 3V3 gets a thin dark outline so it reads on a light background
    if col == C['v33']:
        out.append(f'<polyline points="{d}" fill="none" stroke="#6b7783" stroke-width="{w + 2}" stroke-linejoin="round"{da}/>')
    out.append(f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round"{da}/>')


def dot(x, y, col=INK):
    out.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{col}"/>')


def res(x, y, label, col=INK):
    out.append(f'<rect x="{x - 21}" y="{y - 10}" width="42" height="20" fill="#fff" stroke="{col}" stroke-width="2"/>')
    txt(x, y + 4, label, 10, col, 'middle')


def ground(x, y):
    out.append(f'<line x1="{x - 10}" y1="{y}" x2="{x + 10}" y2="{y}" stroke="{C["gnd"]}" stroke-width="2.5"/>')
    out.append(f'<line x1="{x - 6}" y1="{y + 5}" x2="{x + 6}" y2="{y + 5}" stroke="{C["gnd"]}" stroke-width="2.5"/>')
    out.append(f'<line x1="{x - 2}" y1="{y + 10}" x2="{x + 2}" y2="{y + 10}" stroke="{C["gnd"]}" stroke-width="2.5"/>')


# ---- XIAO ESP32-S3 Sense
XX, XY, XW, XH = 520, 130, 250, 560
out.append(f'<rect x="{XX}" y="{XY}" width="{XW}" height="{XH}" rx="12" fill="#ffffff" stroke="{BOX}" stroke-width="3"/>')
txt(XX + XW / 2, XY + 28, 'XIAO ESP32-S3 Sense', 18, INK, 'middle', True)
txt(XX + XW / 2, XY + 48, 'the car board, leads soldered to the pins', 12, MUT, 'middle')
P = 46
LP = [('D0', 'GPIO1'), ('D1', 'GPIO2'), ('D2', 'GPIO3'), ('D3', 'GPIO4'), ('D4', 'GPIO5'), ('D5', 'GPIO6')]
RP = [('D6', 'GPIO43'), ('D7', 'GPIO44'), ('D8', 'GPIO7'), ('D9', 'GPIO8'), ('D10', 'GPIO9'), ('3V3', 'out'), ('BAT+', 'pad'), ('GND', '')]
LY, RY = {}, {}
for i, (p, g) in enumerate(LP):
    y = XY + 90 + i * P; LY[p] = y; dot(XX, y); txt(XX + 12, y + 5, p, 14, bold=True); txt(XX + 48, y + 5, g, 11, MUT)
for i, (p, g) in enumerate(RP):
    y = XY + 90 + i * P; RY[p] = y; dot(XX + XW, y); txt(XX + XW - 12, y + 5, p, 14, anchor='end', bold=True); txt(XX + XW - 60, y + 5, g, 11, MUT, anchor='end')
# camera note inside the board box
txt(XX + XW / 2, XY + XH - 46, 'Camera: OV5640 on the hood, facing forward;', 11.5, MUT, 'middle')
txt(XX + XW / 2, XY + XH - 30, 'flat cable through the hood vent.', 11.5, MUT, 'middle')
txt(XX + XW / 2, XY + XH - 14, 'Reads the room marker by each door.', 11.5, MUT, 'middle')

# ---- DRV8833
DX, DY, DW, DH = 150, 130, 230, 230
box(DX, DY, DW, DH, '')
txt(DX + DW / 2, DY + 26, 'DRV8833', 17, INK, 'middle', True); txt(DX + DW / 2, DY + 45, 'A drives, B steers', 12, MUT, 'middle')
pins = ['AIN1', 'AIN2', 'BIN1', 'BIN2', 'EEP']
for i, p in enumerate(pins):
    y = DY + 78 + i * 26; dot(DX + DW, y); txt(DX + DW - 10, y + 4, p, 12, anchor='end')
for i, d in enumerate(['D0', 'D1', 'D2', 'D3']):
    ay = DY + 78 + i * 26; mx = 492 - i * 14
    wire([(XX, LY[d]), (mx, LY[d]), (mx, ay), (DX + DW, ay)], C['sig'])
txt(455, LY['D0'] - 24, 'PWM', 11, MUT, 'middle')
wire([(DX + DW, DY + 78 + 4 * 26), (DX + DW + 22, DY + 78 + 4 * 26)], C['v33'], 2.5)
txt(DX + DW + 26, DY + 78 + 4 * 26 + 4, '3V3', 11, MUT)
VMx, GNDx = DX + 40, DX + 95
dot(VMx, DY + DH); txt(VMx, DY + DH - 10, 'VCC', 12, C['rail'], 'middle', True)
dot(GNDx, DY + DH); txt(GNDx, DY + DH - 10, 'GND', 12, MUT, 'middle')
txt(DX + 10, DY + 82, 'AOUT', 11, MUT); txt(DX + 10, DY + 82 + 2 * 26, 'BOUT', 11, MUT)
box(20, DY + 52, 112, 52, 'Drive', 'rear gearbox', INK, 14)
wire([(132, DY + 72), (DX, DY + 72)], C['motor']); wire([(132, DY + 84), (DX, DY + 84)], '#1e3fbf')
box(20, DY + 114, 112, 52, 'Steering', 'small motor', INK, 14)
wire([(132, DY + 134), (DX, DY + 134)], C['motor']); wire([(132, DY + 146), (DX, DY + 146)], '#1e3fbf')
txt(20, DY + 186, 'stock pink/blue leads', 11, MUT)

# ---- I2C devices
IX, IY = 150, 450
txt(IX, IY - 12, 'I2C · SDA D4 · SCL D5 · one shared bus', 12, INK, bold=True)
devs = [('TF-Luna lidar (0x10)', 'VCC: motor rail · pin 5 to GND', 'roof turret'),
        ('MPU-6050 gyro (0x68)', 'VCC: 3V3', ''),
        ('VL53L7CX front (0x29)', 'VCC: 3V3', '')]
sx, cx = 430, 446
ys = []
for i, (t, s1, s2) in enumerate(devs):
    by = IY + i * 76
    box(IX, by, 230, 64, t, s1, BOX, 13.5, s2)
    ys.append(by)
wire([(XX, LY['D4']), (sx, LY['D4']), (sx, ys[-1] + 22)], C['sda'])
wire([(XX, LY['D5']), (cx, LY['D5']), (cx, ys[-1] + 42)], C['scl'])
for by in ys:
    wire([(sx, by + 22), (IX + 230, by + 22)], C['sda']); wire([(cx, by + 42), (IX + 230, by + 42)], C['scl'])

# ---- right side
RX, RW = 900, 280
# D6 hazard LEDs
wire([(XX + XW, RY['D6']), (RX, RY['D6'])], C['sig']); res(840, RY['D6'], '330 ×2')
box(RX, RY['D6'] - 20, RW, 40, 'Hazard lights: 2 amber LEDs', '', BOX, 13.5)
# D7 piezo
wire([(XX + XW, RY['D7']), (RX, RY['D7'])], C['sig']); res(840, RY['D7'], '100')
box(RX, RY['D7'] - 20, RW, 40, 'Piezo chime (PWM tone)', '', BOX, 13.5)
# D8
wire([(XX + XW, RY['D8']), (RX, RY['D8'])], C['sig'])
box(RX, RY['D8'] - 20, RW, 40, 'V2 turret servo / V1 line sensor', '', BOX, 13)
# D9 battery sense divider (both resistors at the pin end)
wire([(XX + XW, RY['D9']), (RX, RY['D9'])], C['sig']); res(840, RY['D9'], '÷2')
box(RX, RY['D9'] - 20, RW, 40, 'Battery sense, motor rail ÷ 2', 'rail → 100k → D9 → 100k → GND', BOX, 13)
# D10 steering pot
wire([(XX + XW, RY['D10']), (RX, RY['D10'])], C['sig'])
box(RX, RY['D10'] - 20, RW, 40, 'Steering pot wiper', 'pot ends: 3V3 and GND', BOX, 13)
# 3V3
wire([(XX + XW, RY['3V3']), (RX, RY['3V3'])], C['v33'])
box(RX, RY['3V3'] - 20, RW, 40, '3V3 → gyro, VL53L7CX, pot, EEP', '', BOX, 12.5)
# BAT+ and GND
wire([(XX + XW, RY['BAT+']), (830, RY['BAT+']), (830, 750), (460, 750), (460, 780)], C['bat'], 3.5)
txt(842, RY['BAT+'] + 4, 'BAT+ pad on the back · charges over USB-C', 11, C['bat'])
wire([(XX + XW, RY['GND']), (800, RY['GND'])], C['gnd']); ground(800, RY['GND'])
txt(832, RY['GND'] + 4, 'all grounds joined', 11, MUT)
txt(RX - 10, RY['D6'] - 30, 'resistors sit right at the pin', 11, MUT)

# ---- power path
PY = 780
box(60, PY, 180, 60, '1S battery', '220 mAh stock; bigger planned', INK, 14)
box(390, PY, 140, 60, 'Main switch', '', INK, 14)
box(600, PY, 140, 60, 'E-stop', 'cuts motors only', '#c62828', 14)
box(810, PY, 220, 60, 'Motor rail', 'DRV8833 VCC · Luna · servo', INK, 14)
box(1080, PY, 120, 60, '470 µF', 'rail to GND', INK, 14)
wire([(240, PY + 30), (390, PY + 30)], C['bat'], 4); wire([(530, PY + 30), (600, PY + 30)], C['bat'], 4)
wire([(740, PY + 30), (810, PY + 30)], C['rail'], 4); wire([(1030, PY + 30), (1080, PY + 30)], C['rail'], 4)
dot(460, PY, C['bat'])
wire([(VMx, DY + DH), (VMx, DY + DH + 30), (135, DY + DH + 30), (135, 730), (870, 730), (870, PY)], C['rail'], 3)
dot(870, PY, C['rail'])
txt(150, 724, 'motor rail → DRV8833 VCC · TF-Luna VCC · turret servo V+ · battery sense', 11, C['rail'])
wire([(GNDx, DY + DH), (GNDx, DY + DH + 18), (120, DY + DH + 18), (120, 710)], C['gnd'], 2.5)
ground(120, 710)
txt(745, PY - 8, 'tag the red/orange split here', 11, '#c62828', 'end')

# ---- title and key
txt(20, 36, 'Ain’t No Waymo · wiring plan', 22, INK, bold=True)
txt(20, 60, 'Updated Nov 10 after the teardown: steering is a small motor with a position pot. Same pins as the team handoff.', 13, MUT)
txt(20, 80, 'Metal shell: nothing conductive may touch it. Never feed the battery or motor rail straight into a pin.', 13, MUT)
key = [('gnd', 'black GND'), ('bat', 'red battery +'), ('rail', 'orange motor rail'), ('v33', 'white 3V3'),
       ('sda', 'blue SDA'), ('scl', 'green SCL'), ('sig', 'yellow signals (tag pin numbers)')]
ky = H - 30
x = 20
for k, label in key:
    if k == 'v33':
        out.append(f'<rect x="{x - 1}" y="{ky - 13}" width="30" height="8" fill="#6b7783"/>')
    out.append(f'<rect x="{x}" y="{ky - 12}" width="28" height="6" fill="{C[k]}"/>')
    txt(x + 36, ky - 5, label, 12, MUT)
    x += 36 + 8 * len(label) + 22

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif" '
       f'role="img" aria-label="Wiring plan for the Mini-Waymo car">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
       + '\n'.join(out) + '\n</svg>\n')
Path(__file__).resolve().parents[1].joinpath('assets', 'wiring.svg').write_text(svg, encoding='utf-8')
print('wrote assets/wiring.svg')
