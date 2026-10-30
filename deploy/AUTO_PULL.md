# Auto-pull for the Ain't No Waymo container

Once installed, a merge to `main` goes live within about a minute. No more manual `git pull`.

## How it works
- A timer runs `/usr/local/sbin/aint-no-waymo-sync` once a minute as root.
- It fetches `origin/main` and **fast-forwards only**. It never merges, never pushes, and holds no keys or tokens.
- HTML pages go live on the next request; they are read from disk.
- If anything under `kratos/` or a `requirements*.txt` changed, it parses the server Python (nothing is imported or written), restarts `aint-no-waymo.service`, and checks it came back.
- If the syntax check fails or the app does not come back up, it **rolls back** to the previous commit and **skips that commit** until a newer one lands on `main`.
- If someone edited tracked files directly on the server, it stops and leaves everything alone.

## Why the script is copied out of the repo
systemd runs the copy in `/usr/local/sbin`, not the file in this repo. If it ran the repo copy, anyone who could push to `main` could make the container run any command as root within a minute. Changing the installed script is a deliberate, by-hand step: review the diff, then re-run the install commands below.

The repo stays `root:root`, so the app user (`waymo`) can read the code but not change it.

## Before installing
- Protect `main` on GitHub so a push to `main` is never an accident (see the security review note in Mnemosyne).
- Merge this branch and do **one last manual pull** in the container, so the files below exist in `/opt/aint-no-waymo/deploy/`.

## Install (inside the container, as root)
```bash
cd /opt/aint-no-waymo/deploy
install -o root -g root -m 0755 aint-no-waymo-sync.sh      /usr/local/sbin/aint-no-waymo-sync
install -o root -g root -m 0644 aint-no-waymo-sync.service /etc/systemd/system/
install -o root -g root -m 0644 aint-no-waymo-sync.timer   /etc/systemd/system/
systemctl daemon-reload
```

## Test, one step at a time (paste each output before the next)
1. One manual run. Expect no output if already up to date, and `status=0/SUCCESS`:
   ```bash
   systemctl start aint-no-waymo-sync.service
   systemctl status aint-no-waymo-sync.service --no-pager | head -8
   journalctl -u aint-no-waymo-sync -n 20 --no-pager
   ```
   If it fails with `226/NAMESPACE`, the container does not allow one of the sandbox lines; tell the AI before removing any.
2. Turn on the timer and confirm it is scheduled:
   ```bash
   systemctl enable --now aint-no-waymo-sync.timer
   systemctl list-timers --all | grep -i waymo
   ```
3. After the next merge to `main`, wait a minute and check:
   ```bash
   journalctl -u aint-no-waymo-sync -n 20 --no-pager
   git -C /opt/aint-no-waymo log --oneline -1
   ```

## Useful checks
- Skipped bad commit: `cat /var/lib/aint-no-waymo-sync/bad-commit` (empty or missing means none).
- Pause updates: `systemctl stop aint-no-waymo-sync.timer` (start it again to resume).

## Turn it off
```bash
systemctl disable --now aint-no-waymo-sync.timer
```
Manual `git -C /opt/aint-no-waymo pull` keeps working either way.

## Updating the updater
Changes to `deploy/aint-no-waymo-sync.sh` in the repo do **nothing** until someone re-runs the install commands. That is on purpose.
