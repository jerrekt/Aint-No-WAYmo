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
print('Repository metadata checks passed')
