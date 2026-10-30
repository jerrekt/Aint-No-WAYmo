# Paste into Claude — Ain't No Waymo handoff

I am handing you my SJSU SME **Ain't No Waymo / Mini-Waymo Micro** project as a continuation, not a new build. Read the attached V1.008 repository and especially `README.md`, `docs/CLAUDE_HANDOFF_CURRENT.md`, `docs/INFRA_KRATOS_HANDOFF_CURRENT.md`, `docs/TEAM_BOARD_DEPLOYMENT.md`, `docs/HARDWARE_FIRMWARE_MAP_HANDOFF.md`, `docs/DEPLOY_CHECKLIST.md`, and `mnemosyne/projects/aint-no-waymo-current-state.md`. Also inspect my **Mnemosyne vault** and the actual GitHub/Kratos state before changing anything; my homelab and site may already have newer work than this local ZIP.

The **approved visual direction is the dark navy V1.008 three-column website**. Keep the real diecast image, SJSU and SME header logos, uploaded IS Building map, six-member SJSU SME team, 34-task board and simulation safety controls. Do not revert to the older colorway experiments. The existing HTML filename contains V12 even though the release candidate is V1.008.

Priorities: (1) reconcile GitHub version/repo, (2) inspect user-reported CT 312 and its cloudflared tunnel, (3) deploy the guest website without exposing MQTT/SSH/admin services, (4) make team task claims persistent and secure under real user authorization, (5) integrate real telemetry when available and preserve local motor failsafes, (6) update Mnemosyne with only verified status. **Never commit secrets, invent team roles, or treat simulator states as physical robot telemetry.** Each merged PR increments the V1.xxx version exactly once.

First give me a short system audit and a safe, non-destructive next-step plan; then proceed incrementally using the existing repository and vault.
