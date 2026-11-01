#!/usr/bin/env python3
"""Refresh the "Where to?" room list from the current map drawing.

Reads maps/is_second_floor_rooms.json (written by tools/build_map_svg.py), snaps each room to the nearest
stop on the simulator's hallway graph (DISPLAY_NODES / EDGES in Mini_Waymo_V12_Demo.html), then rewrites
ROOMS in sim/engine.mjs and in the demo page, plus the clickable map hotspots (ROOM_IMAGE_HITS).

Rooms near each other share a stop; the graph itself is not changed. Only all-digit room numbers are listed:
kratos/app.py rejects anything else for missions (r.isdigit()), and letter-suffixed doors (218B, 219C) are the
unconfirmed ones. Run after every map change:
    python3 tools/build_map_svg.py && python3 tools/sync_room_list.py
Then re-embed the SVG (see VERSIONING.md notes) and run the node tests.
"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "Mini_Waymo_V12_Demo.html"
ENGINE = ROOT / "sim" / "engine.mjs"
ROOMS_JSON = ROOT / "maps" / "is_second_floor_rooms.json"


def natural(room):
    m = re.match(r"(\d+)(.*)", room)
    return (int(m.group(1)), m.group(2)) if m else (10**9, room)


def load_graph(demo_text):
    nodes = json.loads(re.search(r"const DISPLAY_NODES=(\{.*?\});", demo_text).group(1))
    edges_src = re.search(r"const EDGES=(\[.*?\]);", demo_text, re.S).group(1)
    edges = [tuple(e) for e in json.loads(edges_src.replace("'", '"'))]
    return nodes, edges


def snap(point, nodes, edges):
    """Nearest hallway stop: closest point on any hallway segment, then that segment's nearer end."""
    best = None
    for a, b in edges:
        (ax, ay), (bx, by) = nodes[a], nodes[b]
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((point[0] - ax) * dx + (point[1] - ay) * dy) / (dx * dx + dy * dy)))
        d = math.hypot(point[0] - (ax + t * dx), point[1] - (ay + t * dy))
        if best is None or d < best[0]:
            best = (d, a if t < 0.5 else b)
    node = best[1]
    return node, math.hypot(point[0] - nodes[node][0], point[1] - nodes[node][1])


def build():
    demo = DEMO.read_text(encoding="utf-8")
    nodes, edges = load_graph(demo)
    labels = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))["rooms"]
    first, skipped = {}, []
    for r in labels:  # a room drawn twice (repeated label, two doors) keeps its first, non-repeated position
        if not re.fullmatch(r"\d{1,4}", r["room"]):
            if r["room"] not in skipped:
                skipped.append(r["room"])
            continue
        if r["room"] not in first and not r["repeated_label"]:
            first[r["room"]] = (r["x"], r["y"])
    snapped = {room: snap(pos, nodes, edges) for room, pos in first.items()}
    # Insertion order matters: when the sim names the room for a stop it takes the first room mapped to it,
    # so list each stop's nearest room first. The dropdown sorts numerically on its own.
    rooms = {}
    for node in nodes:
        for room, (n, _) in sorted(snapped.items(), key=lambda kv: kv[1][1]):
            if n == node:
                rooms[room] = node
    hits = {room: [round(first[room][0]), round(first[room][1] - 1)] for room in sorted(first, key=natural)}
    return rooms, hits, snapped, skipped


def js_rooms(rooms):
    items = [f"'{r}':'{n}'" for r, n in rooms.items()]
    lines, cur = [], ""
    for it in items:
        if len(cur) + len(it) > 100:
            lines.append(cur.rstrip())
            cur = ""
        cur += it + ","
    lines.append(cur.rstrip(","))
    return "{" + ("\n ".join(lines)) + "}"


def rewrite(path, rooms, hits=None):
    text = path.read_text(encoding="utf-8")
    pat = re.compile(r"((?:export )?const ROOMS=)\{[^}]*\};")
    assert len(pat.findall(text)) == 1, f"ROOMS not found exactly once in {path.name}"
    text = pat.sub(lambda m: m.group(1) + js_rooms(rooms) + ";", text)
    if hits is not None:
        hp = re.compile(r"const ROOM_IMAGE_HITS=\{[^}]*\};")
        assert len(hp.findall(text)) == 1, "ROOM_IMAGE_HITS not found exactly once"
        text = hp.sub(lambda m: "const ROOM_IMAGE_HITS=" + json.dumps(hits, separators=(",", ":")) + ";", text)
    path.write_text(text, encoding="utf-8")


def main():
    rooms, hits, snapped, skipped = build()
    rewrite(DEMO, rooms, hits)
    rewrite(ENGINE, rooms)
    print(f"{len(rooms)} rooms -> stops" + (f" (not listed, non-numeric: {', '.join(skipped)})" if skipped else ""))
    by_node = {}
    for room, node in rooms.items():
        by_node.setdefault(node, []).append(room)
    for node, rs in by_node.items():
        print(f"  stop {node}: {', '.join(sorted(rs, key=natural))}")


if __name__ == "__main__":
    main()
