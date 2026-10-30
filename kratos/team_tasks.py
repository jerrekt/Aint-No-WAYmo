"""Persistent task board. Public reads, password-gated changes, no password in HTML/Git.

Password is specified through WAYMO_TASK_PASSWORD on the server only.
Use HTTPS and a reverse-proxy rate limit for real public deployments.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import re
import sqlite3
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
TASKS_SEED = ROOT / 'team_tasks.json'
DB_PATH = Path(os.environ.get('WAYMO_TASKS_DB',str(ROOT / 'data' / 'team_tasks.sqlite3')))
router = APIRouter()
lock = Lock()
failed_attempts = defaultdict(deque)
REQUIRED_STATUSES = ('todo','in_progress','blocked','done')

class MemberAction(BaseModel):
    name: str = Field(min_length=2,max_length=70)
    password: str = Field(min_length=1,max_length=256)

class StatusAction(MemberAction):
    status: str

def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def db_connect():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(DB_PATH,timeout=10.0)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA busy_timeout=10000')
    return conn

def setup():
    seed=json.loads(TASKS_SEED.read_text(encoding='utf-8'))
    with db_connect() as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('''CREATE TABLE IF NOT EXISTS team_tasks (
          id TEXT PRIMARY KEY, milestone TEXT NOT NULL, title TEXT NOT NULL,
          detail TEXT NOT NULL, status TEXT NOT NULL,
          owner TEXT, changed_utc TEXT NOT NULL
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS team_task_audit (
          id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
          actor TEXT NOT NULL, action TEXT NOT NULL,
          prior_status TEXT NOT NULL, new_status TEXT NOT NULL,
          at_utc TEXT NOT NULL
        )''')
        for t in seed['tasks']:
            db.execute('''INSERT OR IGNORE INTO team_tasks(id,milestone,title,detail,status,owner,changed_utc)
                    VALUES(?,?,?,?,?,?,?)''',(t['id'],t['milestone'],t['title'],t['detail'],t['status'],t['owner'],utcnow()))
    return seed

def normalize(name):
    normalized=' '.join(name.split())
    if not re.fullmatch(r"[\w .'-]{2,70}",normalized,flags=re.UNICODE):
        raise HTTPException(422,'Enter a valid full name (2-70 characters).')
    return normalized

def client_key(request: Request) -> str:
    """Who is asking, for rate limits. The app listens on 127.0.0.1 only, so every request comes
    through cloudflared, which sets CF-Connecting-IP to the visitor's address."""
    cf = (request.headers.get('cf-connecting-ip') or '').strip()
    if cf and len(cf) <= 64:
        return cf
    return request.client.host if request.client else 'unknown'

def live_writes_enabled() -> bool:
    """Live SQLite claims are a separate opt-in. Setting the team password alone (for Discord
    updates) must not switch them on."""
    return os.environ.get('WAYMO_TASK_WRITES') == '1'

def require_live_writes():
    if not live_writes_enabled():
        raise HTTPException(503,'Live claims are off. Use "Send an update" below the checklist instead.')

def enforce_password(request: Request, secret):
    value=os.environ.get('WAYMO_TASK_PASSWORD')
    if not value or len(value)<8:
        raise HTTPException(503,'Task assignment is not configured on Kratos.')
    key=client_key(request)
    now=time.monotonic()
    with lock:
        attempts=failed_attempts[key]
        while attempts and now-attempts[0]>600:attempts.popleft()
        if len(attempts)>=8:raise HTTPException(429,'Too many failed attempts. Try again later.')
    # Hash before compare so comparison length cannot reveal the secret length.
    expected=hashlib.sha256(value.encode()).digest()
    provided=hashlib.sha256(secret.encode()).digest()
    if not hmac.compare_digest(expected,provided):
        with lock:failed_attempts[key].append(now)
        raise HTTPException(401,'Incorrect team password.')
    with lock:failed_attempts.pop(key,None)

def update_task(task_id, name, command, status=None):
    actor=normalize(name)
    with lock:
      with db_connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT * FROM team_tasks WHERE id=?',(task_id,)).fetchone()
        if row is None:raise HTTPException(404,'Unknown task.')
        before=row['status']; owner=row['owner']
        if command=='claim':
            if owner:raise HTTPException(409,f'Task already claimed by {owner}. Refresh the list.')
            if before=='done':raise HTTPException(409,'This task is already complete.')
            new_owner=actor;new_status='in_progress'
        else:
            if not owner:raise HTTPException(409,'Claim this task first.')
            if owner.casefold()!=actor.casefold():raise HTTPException(403,'Only the assigned teammate can update or release this task.')
            new_owner=None if command=='release' else owner
            if command=='release':new_status='todo'
            else:
                if status not in ('todo','in_progress','blocked','done'):
                    raise HTTPException(422,'Invalid status.')
                new_status=status
        db.execute('UPDATE team_tasks SET status=?,owner=?,changed_utc=? WHERE id=?',(new_status,new_owner,utcnow(),task_id))
        db.execute('INSERT INTO team_task_audit(task_id,actor,action,prior_status,new_status,at_utc) VALUES(?,?,?,?,?,?)',(task_id,actor,command,before,new_status,utcnow()))
        return {'id':task_id,'title':row['title'],'owner':new_owner,'status':new_status}

@router.get('/api/tasks')
def list_tasks():
    if not live_writes_enabled():
        # Live claims are off: BJ updates team_tasks.json by PR, so serve the file as is.
        seed=json.loads(TASKS_SEED.read_text(encoding='utf-8'))
        response=JSONResponse({'schema':1,'milestone_labels':seed['milestone_labels'],'tasks':seed['tasks'],'synchronized':True,'updated':utcnow()})
        response.headers['Cache-Control']='no-store'
        return response
    seed=setup()
    with db_connect() as db:
        rows=[dict(r) for r in db.execute('SELECT * FROM team_tasks ORDER BY rowid')]
    response=JSONResponse({'schema':1,'milestone_labels':seed['milestone_labels'],'tasks':rows,'synchronized':True,'updated':utcnow()})
    response.headers['Cache-Control']='no-store'
    return response

@router.post('/api/tasks/{task_id}/claim')
def claim_task(task_id:str,action:MemberAction,request:Request):
    require_live_writes()
    enforce_password(request,action.password)
    setup()
    return update_task(task_id,action.name,'claim')

@router.post('/api/tasks/{task_id}/status')
def change_status(task_id:str,action:StatusAction,request:Request):
    require_live_writes()
    enforce_password(request,action.password)
    setup()
    return update_task(task_id,action.name,'status',action.status)

@router.post('/api/tasks/{task_id}/release')
def release_task(task_id:str,action:MemberAction,request:Request):
    require_live_writes()
    enforce_password(request,action.password)
    setup()
    return update_task(task_id,action.name,'release')
