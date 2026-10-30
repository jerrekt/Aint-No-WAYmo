#!/usr/bin/env bash
# Pull-only updater for CT 312. Runs every minute from aint-no-waymo-sync.timer.
# Nothing pushes into this container. It only fetches the public repo's main branch.
# Safe by design: fast-forward only, one run at a time, syntax-checked before a restart,
# and it rolls back if the check fails. Holds no keys or tokens.
set -uo pipefail
REPO=/opt/aint-no-waymo
SERVICE=aint-no-waymo.service
export GIT_TERMINAL_PROMPT=0
exec 9>/run/aint-no-waymo-sync.lock; flock -n 9 || exit 0

old=$(git -C "$REPO" rev-parse HEAD) || exit 1
git -C "$REPO" fetch -q origin main || { echo "warn: fetch failed, keeping current copy" >&2; exit 0; }
new=$(git -C "$REPO" rev-parse origin/main)
[ "$old" = "$new" ] && exit 0

git -C "$REPO" merge -q --ff-only origin/main || { echo "error: not a fast-forward, leaving files alone" >&2; exit 1; }

# Static pages are read from disk per request. Restart only when server code changed.
if git -C "$REPO" diff --name-only "$old" "$new" | grep -qE '^kratos/'; then
  if python3 -m py_compile "$REPO"/kratos/*.py; then
    systemctl restart "$SERVICE"
    sleep 3
    systemctl is-active --quiet "$SERVICE" || { echo "error: service down, rolling back" >&2
      git -C "$REPO" reset -q --hard "$old"; systemctl restart "$SERVICE"; exit 1; }
  else
    echo "error: syntax check failed, rolling back" >&2
    git -C "$REPO" reset -q --hard "$old"; exit 1
  fi
fi
echo "Deployed $(git -C "$REPO" rev-parse --short HEAD)"
