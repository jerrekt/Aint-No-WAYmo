#!/usr/bin/env python3
"""Regenerate Mnemosyne project progress note from project_progress.json."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
p=json.loads((root/'project_progress.json').read_text(encoding='utf-8'))
ms=p['milestones'];done=sum(m['status']=='complete' for m in ms);percent=round(100*done/len(ms))
status={'complete':'Complete','in_progress':'In progress','not_started':'Not started'}
lines=[
'---','title: Mini-Waymo Micro Progress','type: project',
 'tags: [mini-waymo, sjsu, sme, robotics, kratos, progress]','public: true',
 'updated: '+p['updated'],'---',
 'Project: Mini-Waymo Micro / World’s Littlest Waymo diecast',
 'Organization: SJSU SME student team',
 'Setting: Industrial Studies Building, second floor',
 'Infrastructure: Kratos / Proxmox homelab',
 'Team repo version: '+(root/'VERSION').read_text(encoding='utf-8').strip(),
 f'Progress: {done}/{len(ms)} milestones complete ({percent}%)',
 'Progress method: '+p['basis'],
 'Current phase: '+p['phase'],
 'Milestones:']
for i,m in enumerate(ms,1):
 lines.extend([f'- {i}. {m["title"]} — {status.get(m["status"],m["status"])}',
               '  Evidence: '+m.get('evidence','')])
lines.extend(['Physical hardware remains unvalidated until measured, built, and tested.',
 'Live Kratos deployment: not complete as of this update.',
 'Mission target: IS 251 -> 263 -> 251 -> 202.',
 'Data source: project_progress.json'])
path=root/'mnemosyne'/'projects'/'mini-waymo-micro-progress.md'
path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Wrote',path,'—',percent,'%')
