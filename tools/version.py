#!/usr/bin/env python3
"""Synchronize repo VERSION + version.json + CHANGELOG; enforce one bump per PR."""
import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMAT = re.compile(r"^V1\.(\d{3})$")

def parse(raw):
    text = raw.strip()
    match = FORMAT.fullmatch(text)
    if not match:
        raise SystemExit(f"Invalid version {text!r}; expected V1.000 through V1.999")
    return int(match.group(1))

def current():
    return (ROOT / 'VERSION').read_text(encoding='utf-8').strip()

def check(base_ref=None):
    version = current()
    number = parse(version)
    manifest = json.loads((ROOT / 'version.json').read_text(encoding='utf-8'))
    if manifest.get('version') != version:
        raise SystemExit('VERSION does not match version.json')
    changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    if not re.search(r'^## ' + re.escape(version) + r'\b', changelog, re.MULTILINE):
        raise SystemExit('CHANGELOG.md missing entry for ' + version)
    if base_ref:
        try:
            raw = subprocess.check_output(['git','show',base_ref+':VERSION'],cwd=ROOT,text=True).strip()
        except subprocess.CalledProcessError as exc:
            raise SystemExit('Cannot read base VERSION (ensure checkout fetch-depth: 0)') from exc
        base_number = parse(raw)
        if number != base_number + 1:
            raise SystemExit(f'PR must increment version exactly once: base={raw}; expected=V1.{base_number+1:03d}; found={version}')
    print('Version check OK:',version,'(baseline check)' if base_ref is None else f'(increment from {raw})')

def stamp_pages(new):
    """Write the current version into the visible header text of the site pages."""
    subs = {
        'Mini_Waymo_V12_Demo.html': [
            (r'(<span class="version">)V1\.\d{3}( · DRAFT)', r'\g<1>%s\2'),
            (r"(ver\.textContent=')V1\.\d{3}( · DRAFT')", r'\g<1>%s\2'),
            (r'(<title>[^<]*?)V1\.\d{3}( Draft)', r'\g<1>%s\2'),
            (r'(document\.title="Ain\'t No Waymo \| )V1\.\d{3}( Draft")', r'\g<1>%s\2'),
        ],
        'Mini_Waymo_V12_About.html': [
            (r'(<span class="pill">)V1\.\d{3}( draft · Student prototype)', r'\g<1>%s\2'),
        ],
    }
    for name, rules in subs.items():
        path = ROOT/name
        if not path.exists(): continue
        text = path.read_text(encoding='utf-8')
        for pattern, repl in rules:
            text = re.sub(pattern, lambda m, r=repl: m.expand(r % new), text)
        path.write_text(text, encoding='utf-8')

def bump(message):
    prev = current()
    n = parse(prev)
    if n >= 999:
        raise SystemExit('V1.999 reached; plan a V2.000 migration first')
    new = f'V1.{n+1:03d}'
    if not message.strip():
        raise SystemExit('Describe the update with --message')
    (ROOT/'VERSION').write_text(new+'\n',encoding='utf-8')
    data = json.loads((ROOT/'version.json').read_text(encoding='utf-8'))
    data.update(version=new,date=dt.date.today().isoformat(),status='development-update',note=message.strip())
    (ROOT/'version.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    log = (ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
    position = log.find('## '+prev)
    if position == -1: raise SystemExit('Missing previous version in CHANGELOG.md')
    block = f'## {new} — {dt.date.today().isoformat()}\n- {message.strip()}\n\n'
    (ROOT/'CHANGELOG.md').write_text(log[:position]+block+log[position:],encoding='utf-8')
    note_path = ROOT/'mnemosyne/projects/aint-no-waymo-team-repo.md'
    if note_path.exists():
        note = note_path.read_text(encoding='utf-8')
        note = re.sub(r'^Current repo version: V1\.\d{3}\.$',f'Current repo version: {new}.',note,flags=re.MULTILINE)
        note_path.write_text(note,encoding='utf-8')
    stamp_pages(new)
    print(f'Updated: {prev} -> {new}')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='cmd',required=True)
    b=sub.add_parser('bump'); b.add_argument('--message',required=True)
    c=sub.add_parser('check'); c.add_argument('--base-ref')
    args=parser.parse_args()
    if args.cmd=='bump': bump(args.message)
    else: check(args.base_ref)
if __name__=='__main__':main()
