"""Conservative scan matching against operator-annotated, saved hallway survey.

12+ sampled azimuths can be adequate for a demonstration, but similar
corridors frequently match equally well. NEVER drive after ambiguous matching.
Signatures are 24 distances measured in a fixed survey map coordinate frame.
"""
from __future__ import annotations
import math
from typing import Any

BINS = 24
MAX_RANGE = 3.5


def validate_survey(survey: dict[str, Any]) -> dict[str, Any]:
    if survey.get("schema") != 1 or not isinstance(survey.get("signatures"), dict):
        raise ValueError("Wrong survey schema")
    if not all(k in survey for k in ("nodes", "edges", "rooms")):
        raise ValueError("Missing map topology")
    for node, signature in survey["signatures"].items():
        if node not in survey["nodes"] or len(signature) != BINS:
            raise ValueError("Invalid signature or node")
        if any(not isinstance(v, (int, float)) or not math.isfinite(v) or not .03 <= v <= 3.51 for v in signature):
            raise ValueError("Nonphysical sensor range")
    return survey


def match_scan(survey: dict[str, Any], readings: list[dict[str, float]]) -> dict[str, Any]:
    validate_survey(survey)
    if len(readings) < 10:
        return {"ok": False, "reason": "At least 10 scan headings required", "ranked": []}
    cleaned = []
    for r in readings:
        rel, dist = float(r["rel"]), float(r["range"])
        if not math.isfinite(rel) or not math.isfinite(dist) or dist < .03 or dist > MAX_RANGE + .01:
            raise ValueError("Invalid scan")
        cleaned.append((rel, dist))
    ranked = []
    for node, sig in survey["signatures"].items():
        best_score = float("inf")
        heading = 0.
        for shift in range(BINS):
            differences = []
            for angle, reading in cleaned:
                index = (round((angle / (2 * math.pi)) * BINS + shift)) % BINS
                differences.append((sig[index] - reading) ** 2)
            differences.sort()
            usable = max(5, int(len(differences) * .8))
            score = sum(differences[:usable]) / usable
            if score < best_score:
                best_score, heading = score, shift * 2 * math.pi / BINS
        ranked.append({"node": node, "score": best_score, "heading": heading})
    ranked.sort(key=lambda item: item["score"])
    if not ranked:
        return {"ok": False, "reason": "Empty survey", "ranked": []}
    best = ranked[0]
    next_best = ranked[1] if len(ranked) > 1 else None
    quality = best["score"] < .095
    distinct = not next_best or (next_best["score"] - best["score"] > .009 and next_best["score"] > best["score"] * 3)
    ok = bool(quality and distinct)
    return {"ok": ok, "node": best["node"] if ok else None,
            "heading_rad": best["heading"] if ok else None,
            "reason": "unique surveyed landmark" if ok else "ambiguous or unmatched geometry",
            "ranked": ranked[:4]}
