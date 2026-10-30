#!/usr/bin/env bash
# Pull-only updater for the Ain't No Waymo container.
#
# Installed copy: /usr/local/sbin/aint-no-waymo-sync (root:root 0755), copied by hand.
# This repo copy is the reviewed source only. systemd never runs a script from the repo,
# so a push to main cannot change what runs as root. See deploy/AUTO_PULL.md.
#
# What it does, once a minute from aint-no-waymo-sync.timer:
#   - fetches origin/main and fast-forwards only (never merges, never pushes)
#   - static pages go live on the next request (they are read from disk)
#   - if server code changed, syntax-checks it (no files written), restarts the app,
#     and rolls back to the previous commit if the app does not come back up
#   - remembers a commit that failed, so it is not retried every minute
# Holds no keys or tokens. The repo is public and fetched over HTTPS.
set -euo pipefail

REPO=${SYNC_REPO:-/opt/aint-no-waymo}
SERVICE=${SYNC_SERVICE:-aint-no-waymo.service}
STATE=${STATE_DIRECTORY:-/var/lib/aint-no-waymo-sync}
LOCK=${RUNTIME_DIRECTORY:-/run/aint-no-waymo-sync}/lock
BAD="$STATE/bad-commit"
export GIT_TERMINAL_PROMPT=0

log() { echo "$*"; }
err() { echo "$*" >&2; }

exec 9>"$LOCK"
flock -n 9 || exit 0

g() { git -C "$REPO" "$@"; }

old=$(g rev-parse HEAD)
if ! g fetch -q origin main; then
  err "warn: fetch failed, keeping $(g rev-parse --short HEAD)"
  exit 0
fi
new=$(g rev-parse origin/main)
[ "$old" = "$new" ] && exit 0

if [ -f "$BAD" ] && [ "$(cat "$BAD")" = "$new" ]; then
  exit 0  # already failed once; wait for a newer commit on main
fi

if [ -n "$(g status --porcelain --untracked-files=no)" ]; then
  err "error: tracked files were edited on the server; not updating. Run: git -C $REPO status"
  exit 1
fi

if ! g merge -q --ff-only origin/main; then
  err "error: $(g rev-parse --short "$new") is not a fast-forward of $(g rev-parse --short "$old"); leaving files alone"
  exit 1
fi

mark_bad() {
  echo "$new" > "$BAD"
  g reset -q --hard "$old"
  err "error: $1; rolled back to $(g rev-parse --short "$old") and will skip $(g rev-parse --short "$new")"
}

# Restart only when server code changed. Everything else is read from disk per request.
# (List first, then grep: with pipefail, `git diff | grep -q` can fail when grep exits early.)
changed=$(g diff --name-only "$old" "$new")
if grep -qE '^(kratos/|requirements[^/]*\.txt$)' <<<"$changed"; then
  # Parse every server .py file without importing or writing __pycache__.
  if ! python3 - "$REPO"/kratos <<'PY'
import ast, pathlib, sys
bad = 0
for f in sorted(pathlib.Path(sys.argv[1]).rglob("*.py")):
    try:
        ast.parse(f.read_text(encoding="utf-8"), str(f))
    except SyntaxError as e:
        print(f"syntax error: {e}", file=sys.stderr)
        bad = 1
sys.exit(bad)
PY
  then
    mark_bad "syntax check failed"
    exit 1
  fi
  systemctl restart "$SERVICE"
  sleep 5
  if ! systemctl is-active --quiet "$SERVICE"; then
    mark_bad "$SERVICE did not come back up"
    systemctl restart "$SERVICE" || true
    exit 1
  fi
  log "Deployed $(g rev-parse --short "$old")..$(g rev-parse --short HEAD) and restarted $SERVICE"
else
  log "Deployed $(g rev-parse --short "$old")..$(g rev-parse --short HEAD) (pages only, no restart)"
fi
rm -f "$BAD"
