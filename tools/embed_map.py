#!/usr/bin/env python3
"""Embed maps/is_second_floor_drawing.svg into the demo page as SURVEY_IMAGE_URI (base64), and the
dimension list (values, status, tap areas) as MAP_DIMENSIONS so each dimension on the map can be tapped.

Full map refresh, in order:
    python3 tools/build_map_svg.py && python3 tools/sync_room_list.py && python3 tools/embed_map.py
Safe to run twice: a second run changes nothing.
"""
import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "maps" / "is_second_floor_drawing.svg"
DIMS = ROOT / "maps" / "is_second_floor_dimensions.json"
HITS = ROOT / "maps" / "is_second_floor_dimension_hits.json"
FRAME = ROOT / "maps" / "is_second_floor_frame.json"
PAGE = ROOT / "Mini_Waymo_V12_Demo.html"
PATTERN = re.compile(r'(const SURVEY_IMAGE_URI="data:image/svg\+xml;base64,)[A-Za-z0-9+/=]+(")')
DIM_PATTERN = re.compile(r'const MAP_DIMENSIONS=\[.*?\];')
FRAME_PATTERN = re.compile(r'const MAP_FRAME=\{.*?\};')
# The sheet size appears in the map markup and in the full-screen overlay CSS; keep them in step with the SVG.
SIZE_PATTERNS = [re.compile(r'(id="map" style="aspect-ratio:)\d+/\d+(" viewbox="0 0 )\d+ \d+(")'),
                 re.compile(r'(--map-w:)\d+(;--map-h:)\d+(;)')]
# Which survey task a reported measurement belongs to (task ids from team_tasks.json).
DEFAULT_TASK = "survey-02"


def ft_in(inches):
    ft, inch = divmod(inches, 12)
    return f"{ft}'" if inch == 0 else f"{ft}' {inch}\""


def shown(d):
    """The value as the map shows it."""
    if d["status"] == "to_measure":
        return "Not measured yet"
    prefix = "~" if d["status"] == "estimated" else ""
    if "segments" in d:
        return " · ".join(f'{prefix}{v}"' for v in d["segments"])
    if "lead" in d:
        return f'{prefix}{d["lead"]}" to the first door, then {d["door"]}" doors and {d["wall"]}" walls'
    if d.get("inches") is None:
        return "Not measured yet"
    return f'{prefix}{ft_in(d["inches"])} ({d["inches"]}")' if d["inches"] >= 120 else f'{prefix}{d["inches"]}"'


def dimensions():
    dims = json.loads(DIMS.read_text(encoding="utf-8"))["dimensions"]
    hits = json.loads(HITS.read_text(encoding="utf-8"))["hits"]
    out = []
    for d in dims:
        if d["id"] not in hits:
            raise SystemExit(f'No tap area for "{d["id"]}": run tools/build_map_svg.py first')
        kind = "chain" if "segments" in d else "pattern" if "lead" in d else "span"
        out.append({"id": d["id"], "label": d["label"], "kind": kind, "status": d["status"], "shown": shown(d),
                    "source": d.get("source"), "measured_by": d.get("measured_by"), "date": d.get("date"),
                    "task": d.get("task") or DEFAULT_TASK, "box": hits[d["id"]]})
    return out


def main():
    text = PAGE.read_text(encoding="utf-8")
    if len(PATTERN.findall(text)) != 1:
        raise SystemExit("SURVEY_IMAGE_URI not found exactly once in " + PAGE.name)
    if len(DIM_PATTERN.findall(text)) != 1:
        raise SystemExit("MAP_DIMENSIONS not found exactly once in " + PAGE.name)
    data = base64.b64encode(SVG.read_bytes()).decode("ascii")
    new = PATTERN.sub(lambda m: m.group(1) + data + m.group(2), text)
    dims = json.dumps(dimensions(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    new = DIM_PATTERN.sub(lambda m: "const MAP_DIMENSIONS=" + dims + ";", new)
    frame = json.loads(FRAME.read_text(encoding="utf-8"))
    if len(FRAME_PATTERN.findall(new)) != 1:
        raise SystemExit("MAP_FRAME not found exactly once in " + PAGE.name)
    fjs = json.dumps({k: frame[k] for k in ("w", "h", "transform", "true_north_cw")}, separators=(",", ":"))
    new = FRAME_PATTERN.sub(lambda m: "const MAP_FRAME=" + fjs + ";", new)
    w, h = frame["w"], frame["h"]
    m0 = SIZE_PATTERNS[0]
    if len(m0.findall(new)) != 1:
        raise SystemExit("map svg size not found exactly once in " + PAGE.name)
    new = m0.sub(lambda m: f"{m.group(1)}{w}/{h}{m.group(2)}{w} {h}{m.group(3)}", new)
    if len(SIZE_PATTERNS[1].findall(new)) != 1:
        raise SystemExit("--map-w/--map-h not found exactly once in " + PAGE.name)
    new = SIZE_PATTERNS[1].sub(lambda m: f"{m.group(1)}{w}{m.group(2)}{h}{m.group(3)}", new)
    if new == text:
        print("Already up to date:", PAGE.name)
        return
    PAGE.write_text(new, encoding="utf-8")
    print(f"Embedded {SVG.name} ({SVG.stat().st_size} bytes) and {len(dimensions())} dimensions into {PAGE.name}")


if __name__ == "__main__":
    main()
