#!/usr/bin/env python3
"""Embed maps/is_second_floor_drawing.svg into the demo page as SURVEY_IMAGE_URI (base64).

Full map refresh, in order:
    python3 tools/build_map_svg.py && python3 tools/sync_room_list.py && python3 tools/embed_map.py
Safe to run twice: a second run changes nothing.
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "maps" / "is_second_floor_drawing.svg"
PAGE = ROOT / "Mini_Waymo_V12_Demo.html"
PATTERN = re.compile(r'(const SURVEY_IMAGE_URI="data:image/svg\+xml;base64,)[A-Za-z0-9+/=]+(")')


def main():
    text = PAGE.read_text(encoding="utf-8")
    if len(PATTERN.findall(text)) != 1:
        raise SystemExit("SURVEY_IMAGE_URI not found exactly once in " + PAGE.name)
    data = base64.b64encode(SVG.read_bytes()).decode("ascii")
    new = PATTERN.sub(lambda m: m.group(1) + data + m.group(2), text)
    if new == text:
        print("Already up to date:", PAGE.name)
        return
    PAGE.write_text(new, encoding="utf-8")
    print(f"Embedded {SVG.name} ({SVG.stat().st_size} bytes) into {PAGE.name}")


if __name__ == "__main__":
    main()
