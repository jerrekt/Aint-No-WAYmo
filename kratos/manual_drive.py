"""Manual drive from the Controls page, behind the team password.

Flagged in the vault's runbooks/security-review.md (2026-11-05) before building.

Flow:
  POST /api/manual/unlock  {password}            -> {token, ...} or {token: None, sim_only: True}
  POST /api/manual/drive   {token, seq, throttle, steer}
  POST /api/manual/release {token}               -> zero command, lease freed
  GET  /api/manual/status                        -> {enabled, driver_active, robot_connected}

Rules:
  - Driving the car is off unless WAYMO_MANUAL_DRIVE=1 (kill switch: set 0 and restart). The
    password is still checked when it is off, so the page can drive the simulator behind it.
  - The password is the team password (WAYMO_TASK_PASSWORD), checked by team_tasks.enforce_password:
    hashed, constant-time compare, 8 failures per 10 minutes per visitor (shared lockout).
  - One driver at a time. A lease is a random token held only in memory; it expires after
    LEASE_IDLE_S without commands or LEASE_MAX_S in total. Another visitor gets 409 meanwhile.
  - Every drive command is clamped, rate-limited per lease, and carries ttl_ms: the car must
    stop its motors if no newer command arrives within ttl_ms (dead man). A dropped tab or
    connection therefore stops the car on its own.
  - Refused while a trip is active or a remote stop is requested. The physical E-stop on the
    car always wins; nothing here can override it.
"""
from __future__ import annotations

import hmac
import logging
import os
import secrets
import threading
import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .team_tasks import enforce_password

log = logging.getLogger('waymo.manual')
router = APIRouter()

TOPIC = 'waymo/micro-01/cmd'
TTL_MS = 400            # firmware dead man: stop if no newer command within this
LEASE_IDLE_S = 20.0     # lease lapses after this long without a command
LEASE_MAX_S = 15 * 60.0 # hard cap on one unlock
RATE_PER_S = 20         # drive commands per second per lease (page sends about 10)

_lock = threading.Lock()
_lease: dict | None = None   # {'token', 'started', 'last', 'seq', 'window', 'count'}


def _no_publish(topic: str, data: dict):
    raise HTTPException(503, 'Car not connected')

# app.py wires these in; tests replace them.
publish = _no_publish
busy = lambda: None  # returns a reason string when manual drive must be refused
robot_connected = lambda: False


def configure(*, publish_fn, busy_fn, connected_fn):
    global publish, busy, robot_connected
    publish, busy, robot_connected = publish_fn, busy_fn, connected_fn


def enabled() -> bool:
    return os.environ.get('WAYMO_MANUAL_DRIVE') == '1'


def _require_enabled():
    if not enabled():
        raise HTTPException(503, 'Manual drive is off on the server.')


def _live(lease: dict | None, now: float) -> bool:
    return bool(lease) and now - lease['last'] < LEASE_IDLE_S and now - lease['started'] < LEASE_MAX_S


def _check_token(token: str, now: float) -> dict:
    lease = _lease
    if not _live(lease, now) or not hmac.compare_digest(lease['token'].encode(), token.encode()):
        raise HTTPException(401, 'Unlock again: your drive session ended.')
    return lease


class Unlock(BaseModel):
    password: str = Field(min_length=1, max_length=256)


class Drive(BaseModel):
    token: str = Field(min_length=32, max_length=128)
    seq: int = Field(ge=0, le=2**31)
    throttle: float = Field(ge=-1.0, le=1.0)
    steer: float = Field(ge=-1.0, le=1.0)


class Release(BaseModel):
    token: str = Field(min_length=32, max_length=128)


@router.get('/api/manual/status')
def status():
    with _lock:
        active = _live(_lease, time.monotonic())
    return {'enabled': enabled(), 'driver_active': active, 'robot_connected': bool(robot_connected())}


@router.post('/api/manual/unlock')
def unlock(body: Unlock, request: Request):
    """Always checks the password. The car lease is only taken when the car route is on and the
    car is connected; otherwise the page drives the simulator (sim_only)."""
    global _lease
    try:
        enforce_password(request, body.password)
    except HTTPException as e:
        if e.status_code == 503:
            raise HTTPException(503, 'The team password is not set on the server.')
        raise
    if not enabled() or not robot_connected():
        return {'token': None, 'sim_only': True,
                'reason': 'Manual drive of the car is off on the server.' if not enabled() else 'Car not connected.'}
    now = time.monotonic()
    with _lock:
        if _live(_lease, now):
            raise HTTPException(409, 'Someone else is driving. Try again in a few seconds.')
        token = secrets.token_hex(32)
        _lease = {'token': token, 'started': now, 'last': now, 'seq': -1, 'window': now, 'count': 0}
    log.info('manual drive unlocked')
    return {'token': token, 'sim_only': False, 'ttl_s': LEASE_IDLE_S, 'max_s': LEASE_MAX_S, 'ttl_ms': TTL_MS}


@router.post('/api/manual/drive')
def drive(body: Drive):
    _require_enabled()
    now = time.monotonic()
    with _lock:
        lease = _check_token(body.token, now)
        if now - lease['window'] >= 1.0:
            lease['window'], lease['count'] = now, 0
        lease['count'] += 1
        if lease['count'] > RATE_PER_S:
            raise HTTPException(429, 'Too many commands.')
        if body.seq <= lease['seq']:
            return {'sent': False, 'stale': True}
        lease['seq'] = body.seq
        lease['last'] = now
    reason = busy()
    if reason:
        raise HTTPException(409, reason)
    publish(TOPIC, {'type': 'manual', 'seq': body.seq, 'throttle': round(body.throttle, 3),
                    'steer': round(body.steer, 3), 'ttl_ms': TTL_MS})
    return {'sent': True}


@router.post('/api/manual/release')
def release(body: Release):
    global _lease
    _require_enabled()
    now = time.monotonic()
    with _lock:
        lease = _check_token(body.token, now)
        seq = lease['seq'] + 1
        _lease = None
    try:
        publish(TOPIC, {'type': 'manual', 'seq': seq, 'throttle': 0.0, 'steer': 0.0, 'ttl_ms': 0})
    except HTTPException:
        pass  # no car connected: nothing to stop
    log.info('manual drive released')
    return {'released': True}


def _reset_for_tests():
    global _lease
    with _lock:
        _lease = None
