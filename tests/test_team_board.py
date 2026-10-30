"""Simulated API tests only; no Kratos deployment or public authentication test."""
import json
import os
import tempfile
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi import FastAPI
from fastapi.testclient import TestClient

with tempfile.TemporaryDirectory() as tmp:
    os.environ['WAYMO_TASKS_DB'] = str(Path(tmp)/'board.sqlite3')
    os.environ['WAYMO_TASK_PASSWORD'] = 'local-test-not-a-real-password'
    os.environ.pop('WAYMO_TASK_WRITES', None)
    from kratos.team_tasks import router, TASKS_SEED
    app=FastAPI()
    app.include_router(router)
    cli=TestClient(app)
    tasks=cli.get('/api/tasks').json()
    assert len(tasks['tasks'])==34
    assert 'password' not in json.dumps(tasks).lower()
    target=next(t for t in tasks['tasks'] if t['status']=='todo')
    tid=target['id']
    endpoint=f'/api/tasks/{tid}'
    k1=next(t for t in tasks['tasks'] if t['id']=='kratos-01')
    assert k1['status']=='done' and k1['owner'], 'with live claims off, /api/tasks serves team_tasks.json'
    off=cli.post(endpoint+'/claim',json={'name':'Branden Adsuara','password':os.environ['WAYMO_TASK_PASSWORD']})
    assert off.status_code==503,off.text  # password alone must not turn on live claims
    os.environ['WAYMO_TASK_WRITES'] = '1'
    wrong=cli.post(endpoint+'/claim',json={'name':'Branden Adsuara','password':'wrong'})
    assert wrong.status_code==401,wrong.text
    payload={'name':'Branden Adsuara','password':os.environ['WAYMO_TASK_PASSWORD']}
    accepted=cli.post(endpoint+'/claim',json=payload)
    assert accepted.status_code==200,accepted.text
    assert accepted.json()['owner']=='Branden Adsuara'
    duplicate=cli.post(endpoint+'/claim',json=payload)
    assert duplicate.status_code==409
    foreign=cli.post(endpoint+'/status',json={'name':'Noah Zerarka','password':payload['password'],'status':'done'})
    assert foreign.status_code==403
    blocked=cli.post(endpoint+'/status',json={**payload,'status':'blocked'})
    assert blocked.status_code==200 and blocked.json()['status']=='blocked'
    done=cli.post(endpoint+'/status',json={**payload,'status':'done'})
    assert done.status_code==200 and done.json()['status']=='done'
    after=cli.get('/api/tasks').json()
    assert next(t for t in after['tasks'] if t['id']==tid)['owner']=='Branden Adsuara'
    release=cli.post(endpoint+'/release',json=payload)
    assert release.status_code==200 and release.json()['owner'] is None
    assert cli.get('/api/tasks').status_code==200
    with __import__('sqlite3').connect(os.environ['WAYMO_TASKS_DB']) as db:
        assert db.execute('SELECT COUNT(*) FROM team_task_audit').fetchone()[0]==4
    print('Team task API PASS: 34 seeds, no password leak, wrong password, claim, conflict, owner checks, blocked/done, release, audit')
