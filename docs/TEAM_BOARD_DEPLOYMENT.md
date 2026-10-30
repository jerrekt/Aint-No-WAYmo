# Team build checklist and claiming (V1.002 draft)

## What works

- Clicking the build-status panel expands all 34 project tasks, grouped under eight major milestones.
- The publicly readable board shows one of four statuses per task (To do, In progress, Blocked, Done), and the teammate name for claimed tasks.
- A teammate claims a task by entering their name and the team password. Claims and status changes are saved to server-side SQLite and become visible to other browsers after refresh (automatic polling every 15 seconds while the board is open).
- Only the teammate name on a claimed task can update or release it (self-reported identity). The shared password is **not** a strong authentication method: anyone knowing it can impersonate a name. For real role-based access, migrate to Cloudflare Access identities or per-user login.
- Already completed tasks are shown as historical done items and cannot be newly claimed. The old milestone progress bar remains tied to verified milestone status in `project_progress.json`, not self-reported task claims.

## Important limitations

- These files are **not deployed**; the downloadable standalone HTML previews are read-only and do not synchronize.
- A team password must be configured privately **on the server**, never in the HTML, browser JavaScript, GitHub, Mnemosyne, or screenshot. A short temporary team password was discussed in chat; treat it as publicly exposed and rotate it to a strong private value before enabling any write endpoints.
- Server-side IP rate limiting (8 failed attempts / 10 min) is a minimal guard, not a replacement for Cloudflare WAF/Access rate limiting. Avoid a publicly accessible password-only mutation API for sustained use.
- The current website and mission API are prototypes; deploying the task board does not mean hardware control is safe or enabled.
- SQLite database files in `data/` are deliberately excluded by `.gitignore`. Back them up separately on Kratos.
- Photos and SJSU/SME logos provided by the user are project-affiliation graphics, not an endorsement or official Waymo collaboration.

## Deploy inside the existing Waymo LXC (not the Proxmox host)

1. Put this repository in a private writable deployment location, for example `/opt/aint-no-waymo`, and use a dedicated service user with access to its `data/` directory.
2. Create a local environment file readable only by the service user (for example `/etc/aint-no-waymo/team.env`, chmod 0600), setting `WAYMO_TASK_PASSWORD` to a **new, strong** private team password, `WAYMO_TASKS_DB` to an absolute persistent SQLite path and (if needed) the existing `WAYMO_ADMIN_TOKEN` and MQTT variables. Do not commit this file.
3. Run `python -m pip install -r kratos/requirements.txt` in a virtual environment.
4. Start from the repo root with env loaded: `uvicorn kratos.app:app --host 127.0.0.1 --port 8090`. The app serves both the website and task API at the same origin.
5. Configure the existing dedicated Cloudflare Tunnel's HTTP service to point at `http://localhost:8090` in that LXC; do **not** expose MQTT, Proxmox, SSH or any new public TCP port. Preserve the user's current working tunnel and security policy; review before changing.
6. Verify `GET /api/tasks` returns the task list but no secret, and a successful authenticated claim is saved. Test wrong-password (401), duplicate claim (409), foreign owner (403), and a fresh browser after update.
7. Back up the SQLite database, configure Cloudflare WAF rules / Access restrictions for write endpoints, and maintain audit logs. Keep ordinary About-page viewing public.

## Mnemosyne and versioning

Source seed: `team_tasks.json`, database source of truth after first deploy: `WAYMO_TASKS_DB`. Existing eight milestone gauge: `project_progress.json`. The seed file does not automatically overwrite live SQLite state on restart. `V1.002` here is an **unmerged draft**; merge from the current main branch following `VERSIONING.md` and bump exactly once. Claude should inspect the actual deployed server and reconcile version before merging.

## Team task board API

- `GET /api/tasks` - public task list, status and current owner.
- `POST /api/tasks/{id}/claim` - JSON `{ "name": "Branden Adsuara", "password": "<private value>" }`
- `POST /api/tasks/{id}/status` - JSON `{ "name": "Branden Adsuara", "password": "<private value>", "status": "done" }` where status is `todo|in_progress|blocked|done`.
- `POST /api/tasks/{id}/release` - same name/password JSON as claim.

No browser stores or transmits a team password except in the explicitly submitted HTTPS POST request. Do not reuse the team board password as the real vehicle's admin token.
