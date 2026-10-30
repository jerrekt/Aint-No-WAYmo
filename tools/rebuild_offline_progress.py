#!/usr/bin/env python3
"""Update inline fallback snapshot in the two offline HTML files."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
raw=json.dumps(json.loads((root/'project_progress.json').read_text(encoding='utf-8')),ensure_ascii=False,separators=(',',':')).replace('</','<\/')
for name in ['Mini_Waymo_V12_Demo.html','Mini_Waymo_V12_About.html']:
 path=root/name;s=path.read_text(encoding='utf-8')
 s,n=re.subn(r'(<script id="projectProgressFallback" type="application/json">).*?(</script>)',lambda m:m.group(1)+raw+m.group(2),s,flags=re.S)
 assert n==1,(name,n)
 path.write_text(s,encoding='utf-8')
 print('Updated',name)
tasks_raw=json.dumps(json.loads((root/'team_tasks.json').read_text(encoding='utf-8')),ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
for name in ['Mini_Waymo_V12_Demo.html','Mini_Waymo_V12_About.html']:
 path=root/name;s=path.read_text(encoding='utf-8')
 s,n=re.subn(r'(<script id="boardTasksFallback" type="application/json">).*?(</script>)',lambda m:m.group(1)+tasks_raw+m.group(2),s,flags=re.S)
 assert n==1,(name,n)
 path.write_text(s,encoding='utf-8')
 print('Updated task list in',name)
