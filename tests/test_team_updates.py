"""Team updates to Discord: simulated, no network. Discord is replaced by a fake urlopen."""
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi import FastAPI
from fastapi.testclient import TestClient
import kratos.team_updates as tu

PW = 'local-test-not-a-real-password'
sent = []

class FakeResp:
    status = 204
    def __enter__(self): return self
    def __exit__(self, *a): return False

def fake_urlopen(req, timeout):
    sent.append(json.loads(req.data.decode()))
    assert req.full_url.startswith('https://discord.com/api/webhooks/')
    assert timeout <= 10
    return FakeResp()

tu.urllib.request.urlopen = fake_urlopen
app = FastAPI(); app.include_router(tu.router)
cli = TestClient(app)
task = next(iter(tu._tasks().values()))
good = {'task_id': task['id'], 'name': 'Isabel Burgos', 'status': 'done', 'summary': 'Measured the shell.\nInside is 38 mm wide. @everyone `x`', 'password': PW}
def ip(n): return {'CF-Connecting-IP': f'203.0.113.{n}'}

# Not configured: 503 and nothing sent.
os.environ.pop('WAYMO_DISCORD_WEBHOOK', None); os.environ['WAYMO_TASK_PASSWORD'] = PW
assert cli.get('/api/updates/status').json() == {'enabled': False, 'live_claims': False}
r = cli.post('/api/updates', json=good, headers=ip(1)); assert r.status_code == 503, r.text
os.environ['WAYMO_DISCORD_WEBHOOK'] = 'https://example.com/hook'
r = cli.post('/api/updates', json=good, headers=ip(1)); assert r.status_code == 503, 'non-Discord webhook must be refused'
os.environ['WAYMO_DISCORD_WEBHOOK'] = 'https://discord.com/api/webhooks/123/test'
assert cli.get('/api/updates/status').json() == {'enabled': True, 'live_claims': False}
assert not sent

# Wrong password, unknown task, bad status, short summary.
assert cli.post('/api/updates', json={**good, 'password': 'nope'}, headers=ip(2)).status_code == 401
assert cli.post('/api/updates', json={**good, 'task_id': 'not-a-task'}, headers=ip(2)).status_code == 404
assert cli.post('/api/updates', json={**good, 'status': 'hacked'}, headers=ip(2)).status_code == 422
assert cli.post('/api/updates', json={**good, 'summary': 'x'}, headers=ip(2)).status_code == 422
assert not sent

# Good send: no mentions allowed, repo line present, no password in the message.
r = cli.post('/api/updates', json=good, headers=ip(3)); assert r.status_code == 200, r.text
msg = sent[-1]
assert msg['allowed_mentions'] == {'parse': []}
assert PW not in json.dumps(msg)
assert f'"id": "{task["id"]}"' in msg['content'] and '"status": "done"' in msg['content']
assert '`x`' not in msg['content'], 'backticks from users are neutralised'
assert len(msg['content']) <= 1900

# Per-visitor limit: 4 per 10 minutes; another visitor still gets through.
for _ in range(3):
    assert cli.post('/api/updates', json=good, headers=ip(3)).status_code == 200
assert cli.post('/api/updates', json=good, headers=ip(3)).status_code == 429
assert cli.post('/api/updates', json=good, headers=ip(4)).status_code == 200

# Discord down: 502 and the slot is given back.
def broken(req, timeout): raise tu.urllib.error.URLError('down')
tu.urllib.request.urlopen = broken
before = len(tu._sent_all)
assert cli.post('/api/updates', json=good, headers=ip(5)).status_code == 502
assert len(tu._sent_all) == before
print('team updates tests passed:', len(sent), 'fake sends')
