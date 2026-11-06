"""Manual drive route: no network, MQTT replaced by a list."""
import os
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import kratos.manual_drive as md
import kratos.team_tasks as tt

PW = 'local-test-not-a-real-password'
sent = []
reason = [None]
connected = [True]
def pub(topic, data):
    if not connected[0]: raise HTTPException(503, 'Car not connected')
    sent.append((topic, data))
md.configure(publish_fn=pub, busy_fn=lambda: reason[0], connected_fn=lambda: connected[0])
app = FastAPI(); app.include_router(md.router); cli = TestClient(app)
def ip(n): return {'CF-Connecting-IP': f'203.0.113.{n}'}
def fresh():
    md._reset_for_tests(); tt.failed_attempts.clear(); sent.clear(); reason[0] = None; connected[0] = True

os.environ['WAYMO_TASK_PASSWORD'] = PW

# Off by default: every route refuses, nothing published.
os.environ.pop('WAYMO_MANUAL_DRIVE', None); fresh()
assert cli.get('/api/manual/status').json()['enabled'] is False
assert cli.post('/api/manual/unlock', json={'password': 'nope'}, headers=ip(1)).status_code == 401
r = cli.post('/api/manual/unlock', json={'password': PW}, headers=ip(1))
assert r.status_code == 200 and r.json()['sim_only'] is True and r.json()['token'] is None, r.text
assert cli.post('/api/manual/drive', json={'token': 'f' * 64, 'seq': 0, 'throttle': 0.5, 'steer': 0}).status_code == 503
assert not sent
os.environ['WAYMO_MANUAL_DRIVE'] = '1'

# Wrong password: 401, and the shared lockout kicks in after 8 failures.
fresh()
for _ in range(8):
    assert cli.post('/api/manual/unlock', json={'password': 'nope'}, headers=ip(2)).status_code == 401
assert cli.post('/api/manual/unlock', json={'password': PW}, headers=ip(2)).status_code == 429
assert not sent

# Unlock, drive, clamp by validation, stale seq ignored.
fresh()
r = cli.post('/api/manual/unlock', json={'password': PW}, headers=ip(3)); assert r.status_code == 200, r.text
tok = r.json()['token']; assert len(tok) == 64 and r.json()['ttl_ms'] == md.TTL_MS and r.json()['sim_only'] is False
assert cli.post('/api/manual/drive', json={'token': tok, 'seq': 0, 'throttle': 0.5, 'steer': -0.2}).json() == {'sent': True}
assert sent[-1] == ('waymo/micro-01/cmd', {'type': 'manual', 'seq': 0, 'throttle': 0.5, 'steer': -0.2, 'ttl_ms': md.TTL_MS})
assert cli.post('/api/manual/drive', json={'token': tok, 'seq': 1, 'throttle': 1.5, 'steer': 0}).status_code == 422
assert cli.post('/api/manual/drive', json={'token': tok, 'seq': 0, 'throttle': 0.1, 'steer': 0}).json()['stale'] is True
assert len(sent) == 1

# A second visitor cannot take over a live lease; a bad token is refused.
assert cli.post('/api/manual/unlock', json={'password': PW}, headers=ip(4)).status_code == 409
assert cli.post('/api/manual/drive', json={'token': 'f' * 64, 'seq': 5, 'throttle': 0, 'steer': 0}).status_code == 401

# Busy (trip running or remote stop): 409 and nothing sent.
reason[0] = 'A trip is running. Stop it first.'
assert cli.post('/api/manual/drive', json={'token': tok, 'seq': 2, 'throttle': 0.2, 'steer': 0}).status_code == 409
reason[0] = None; n = len(sent)

# Rate limit per lease.
codes = [cli.post('/api/manual/drive', json={'token': tok, 'seq': 10 + i, 'throttle': 0.1, 'steer': 0}).status_code for i in range(md.RATE_PER_S + 5)]
assert 429 in codes

# Release sends a zero command and frees the lease; the old token is dead.
r = cli.post('/api/manual/release', json={'token': tok}); assert r.status_code == 200
assert sent[-1][1]['throttle'] == 0.0 and sent[-1][1]['ttl_ms'] == 0
assert cli.post('/api/manual/drive', json={'token': tok, 'seq': 99, 'throttle': 0.1, 'steer': 0}).status_code == 401
assert cli.post('/api/manual/unlock', json={'password': PW}, headers=ip(4)).status_code == 200

# Idle lease lapses so the next person can drive.
fresh()
tok = cli.post('/api/manual/unlock', json={'password': PW}, headers=ip(5)).json()['token']
md._lease['last'] -= md.LEASE_IDLE_S + 1
assert cli.post('/api/manual/unlock', json={'password': PW}, headers=ip(6)).status_code == 200
assert cli.post('/api/manual/drive', json={'token': tok, 'seq': 1, 'throttle': 0, 'steer': 0}).status_code == 401

# No car connected: unlock still works but takes no lease (page drives the simulator).
fresh(); connected[0] = False
r = cli.post('/api/manual/unlock', json={'password': PW}, headers=ip(7)); assert r.json()['sim_only'] is True
assert md._lease is None
# Car drops after unlock: drive answers 503, release still frees the lease.
connected[0] = True
tok = cli.post('/api/manual/unlock', json={'password': PW}, headers=ip(8)).json()['token']
connected[0] = False
assert cli.post('/api/manual/drive', json={'token': tok, 'seq': 0, 'throttle': 0.3, 'steer': 0}).status_code == 503
assert cli.post('/api/manual/release', json={'token': tok}).status_code == 200 and md._lease is None

print('manual drive route: off by default, password + lockout, one driver, clamp, stale seq, busy, rate limit, release, lapse, no-car all pass')
