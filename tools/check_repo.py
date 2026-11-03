#!/usr/bin/env python3
"""Simple no-dependency repository sanity check (not a substitute for secret scanning)."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
team=json.loads((root/'team_members.json').read_text(encoding='utf-8'))
assert {'Branden Adsuara','Noah Zerarka','Gage Watts'} <= {x['name'] for x in team}
progress=json.loads((root/'project_progress.json').read_text(encoding='utf-8'))
assert len(progress['milestones']) >= 1
assert all(x['status'] in {'complete','in_progress','not_started'} for x in progress['milestones'])
assert (root/'maps/reference/user-annotated-survey-oct29.jpeg').exists()
assert not (root/'bench/esp32-c3/src/secrets.h').exists(), 'Local secrets.h must not be committed'
assert (root/'bench/esp32-c3/src/secrets.example.h').exists()
parts=json.loads((root/'build_parts.json').read_text(encoding='utf-8'))
ids=[x['id'] for x in parts['parts']]
assert len(ids)==len(set(ids)), 'build_parts.json has duplicate part ids'
assert all(x['versions'] in {'both','v1','v2'} and isinstance(x['bought'],bool) for x in parts['parts']), 'build_parts.json: versions must be both/v1/v2 and bought true/false'
import sys; sys.path.insert(0,str(root/'tools'))
import embed_build_parts as ebp
assert ebp.embedded((root/'Mini_Waymo_V12_Demo.html').read_text(encoding='utf-8'))==ebp.payload(), 'Build page parts are out of date: run python3 tools/embed_build_parts.py'
print('Repository metadata checks passed')
