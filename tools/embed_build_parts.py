"""Copy build_parts.json into the Build page so it works offline. Run after editing build_parts.json."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "Mini_Waymo_V12_Demo.html"
PATTERN = re.compile(r'(<script id="buildPartsData" type="application/json">)(.*?)(</script>)', re.S)


def payload() -> str:
    data = json.loads((ROOT / "build_parts.json").read_text(encoding="utf-8"))
    data.pop("_note", None)
    # "</" is escaped so a part name can never close the script tag.
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def embedded(html: str) -> str | None:
    m = PATTERN.search(html)
    return m.group(2) if m else None


def main() -> int:
    html = PAGE.read_text(encoding="utf-8")
    if embedded(html) is None:
        print("buildPartsData block not found in", PAGE.name)
        return 1
    PAGE.write_text(PATTERN.sub(lambda m: m.group(1) + payload() + m.group(3), html, count=1), encoding="utf-8")
    print("Embedded build_parts.json into", PAGE.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
