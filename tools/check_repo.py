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
assert all((x.get('cost') is None or isinstance(x['cost'],(int,float))) and isinstance(x.get('approx',False),bool) and x.get('group') in parts.get('group_labels',{}) for x in parts['parts']), 'build_parts.json: cost must be a number or null, approx a bool, group one of group_labels'
tasks=json.loads((root/'team_tasks.json').read_text(encoding='utf-8'))
assert all(t.get('size') in {'S','M','L'} and t.get('phase') in tasks.get('phases',{}) for t in tasks['tasks']), 'team_tasks.json: every task needs size S/M/L and a phase listed in phases'
import sys; sys.path.insert(0,str(root/'tools'))
import embed_build_parts as ebp
assert ebp.embedded((root/'Mini_Waymo_V12_Demo.html').read_text(encoding='utf-8'))==ebp.payload(), 'Build page parts are out of date: run python3 tools/embed_build_parts.py'
print('Repository metadata checks passed')
