"""Team updates to Discord. Stores nothing; forwards a short update to a Discord webhook.

For teammates who do not code: pick a task, write what you did, enter the team password, send.
BJ gets it in Discord and copies it into team_tasks.json by pull request.

Server-only settings (never in HTML or Git):
  WAYMO_TASK_PASSWORD   shared team password (8+ characters), same check as the task board
  WAYMO_DISCORD_WEBHOOK https://discord.com/api/webhooks/... for the channel that receives updates
Without both, the route returns 503 and nothing is sent.
"""
from __future__ import annotations
import json
import os
import time
import urllib.error
import urllib.request
from collections import defaultdict, deque
from threading import Lock
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .team_tasks import TASKS_SEED, client_key, enforce_password, live_writes_enabled

router = APIRouter()
_lock = Lock()
_sent_by_client: dict[str, deque] = defaultdict(deque)
_sent_all: deque = deque()

PER_CLIENT = (4, 600)      # 4 sends per 10 minutes per visitor
GLOBAL = (30, 3600)        # 30 sends per hour in total
WEBHOOK_PREFIXES = ("https://discord.com/api/webhooks/", "https://discordapp.com/api/webhooks/")
STATUS_TEXT = {"claim": "Claiming", "in_progress": "In progress", "blocked": "Blocked / needs help", "done": "Done"}
REPO_STATUS = {"claim": "in_progress", "in_progress": "in_progress", "blocked": "blocked", "done": "done"}


class TeamUpdate(BaseModel):
    task_id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=2, max_length=70)
    status: str = Field(min_length=1, max_length=20)
    summary: str = Field(min_length=3, max_length=600)
    password: str = Field(min_length=1, max_length=256)


def _webhook() -> str | None:
    url = (os.environ.get("WAYMO_DISCORD_WEBHOOK") or "").strip()
    return url if url.startswith(WEBHOOK_PREFIXES) else None


def _tasks() -> dict:
    seed = json.loads(TASKS_SEED.read_text(encoding="utf-8"))
    return {t["id"]: t for t in seed.get("tasks", [])}


def _clean(text: str, limit: int) -> str:
    # One-line fields: no newlines; strip characters Discord would treat as formatting tricks.
    text = " ".join(text.replace("\r", " ").split())
    return text.replace("`", "'")[:limit]


def _take_slot(key: str) -> None:
    now = time.monotonic()
    with _lock:
        mine = _sent_by_client[key]
        while mine and now - mine[0] > PER_CLIENT[1]:
            mine.popleft()
        while _sent_all and now - _sent_all[0] > GLOBAL[1]:
            _sent_all.popleft()
        if len(mine) >= PER_CLIENT[0]:
            raise HTTPException(429, "Too many updates from you. Try again in a few minutes.")
        if len(_sent_all) >= GLOBAL[0]:
            raise HTTPException(429, "Too many updates this hour. Try again later or message BJ.")
        mine.append(now)
        _sent_all.append(now)


def _give_back(key: str) -> None:
    with _lock:
        if _sent_by_client[key]:
            _sent_by_client[key].pop()
        if _sent_all:
            _sent_all.pop()


def _message(task: dict, name: str, status: str, summary: str) -> str:
    line = json.dumps({"id": task["id"], "owner": name, "status": REPO_STATUS[status]}, ensure_ascii=False)
    body_lines = [f"> {part}" for part in summary.replace("\r", "").split("\n") if part.strip()][:12]
    msg = "\n".join([
        f"**Team update** · {STATUS_TEXT[status]}",
        f"**Task:** {_clean(task.get('title', task['id']), 140)} (`{task['id']}`)",
        f"**From:** {name}",
        *body_lines,
        "For team_tasks.json:",
        f"```json\n{line}\n```",
    ])
    return msg[:1900]


@router.get("/api/updates/status")
def updates_status():
    password_set = len(os.environ.get("WAYMO_TASK_PASSWORD") or "") >= 8
    return {"enabled": bool(_webhook()) and password_set, "live_claims": live_writes_enabled() and password_set}


@router.post("/api/updates")
def send_update(update: TeamUpdate, request: Request):
    url = _webhook()
    if not url:
        raise HTTPException(503, "Discord updates are not set up on the server yet. Use Copy update instead.")
    enforce_password(request, update.password)
    tasks = _tasks()
    task = tasks.get(update.task_id)
    if task is None:
        raise HTTPException(404, "Unknown task. Refresh the page.")
    if update.status not in STATUS_TEXT:
        raise HTTPException(422, "Pick a status from the list.")
    name = _clean(update.name, 70)
    summary = "\n".join(_clean(part, 600) for part in update.summary.split("\n"))
    if len(name) < 2 or len(summary.strip()) < 3:
        raise HTTPException(422, "Enter your name and a short summary.")
    key = client_key(request)
    _take_slot(key)
    payload = json.dumps({
        "content": _message(task, name, update.status, summary),
        "username": "Ain't No Waymo board",
        "allowed_mentions": {"parse": []},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "aint-no-waymo-updates"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status >= 300:
                raise HTTPException(502, "Discord did not accept the update. Use Copy update instead.")
    except HTTPException:
        _give_back(key)
        raise
    except (urllib.error.URLError, TimeoutError, OSError):
        _give_back(key)
        raise HTTPException(502, "Could not reach Discord. Use Copy update instead.")
    return {"sent": True}
