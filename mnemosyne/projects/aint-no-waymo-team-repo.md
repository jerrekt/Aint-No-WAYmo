---
title: Ain't No Waymo — Team Repository and Versioning
type: project
tags: [mini-waymo, sjsu, sme, github, versioning, kratos]
public: false
updated: 2026-10-29
---
Project: Ain't No Waymo / Mini-Waymo Micro.
Team: SJSU SME; Branden Adsuara, Noah Zerarka, Gage Watts; additional members possible.
GitHub repository: NOT CREATED OR PUBLISHED BY CHATGPT; fill in remote URL after creation.
Current repo version: V1.002 (draft, not merged).
Version baseline: V1.000.
Rule: Each merged change/PR increments the repo version by exactly one, e.g. V1.001 then V1.002.
Version files: VERSION; version.json; CHANGELOG.md.
Command: python tools/version.py bump --message "Summary".
CI: GitHub Actions validates increment against PR base branch, simulator checks and C3 bench tests.
Older simulator V9–V12 titles: historical prototypes; NOT GitHub version sequence.
Progress gauge: project_progress.json milestone completion; independent of version.
Home project domain: aintnowaymo.adsuaracloud.com (planned; not verified deployed here).
Kratos: user's privately operated Proxmox homelab; hosts websites/game servers and SJSU student projects; not SJSU-owned.
Cloudflare: dedicated cloudflared inside an unprivileged project LXC with unique secret tunnel token (planned; no deployment verified here).
MQTT: private, C3 bench topics waymo/bench-c3; no motor output.
Physical build: standalone diecast shell is priority; optional FPV trailer only after core robot works.
Map: north/south halls approx 168 ft each; east approx 300 ft; provisional door locations; original annotated sketch in maps/reference/.
Hardware status: ESP32-C3 available for testing; main ESP32-S3 Sense planned; real motor/sensors not verified.
Claude handoff: inspect repository+Mnemosyne, audit LXC/Cloudflare setup, ensure production API auth, verify actual deployments and correct anything provisional.
Do not store credentials, tokens, or private IP configuration not independently verified.

V1.006 draft: user-provided estimated IS second floor image replaces placeholder live-map background; synthetic route overlay and click hitboxes remain provisional. See docs/MAP_V1.006_DRAFT.md.

V1.007 draft website layout implemented from team-approved mockup.
Desktop layout: left car/dispatch, center surveyed map/simulator, right progress/team.
Mobile layout: stacked panels and five-item floating dock.
Vehicle image: user's actual diecast product reference photo; not working robot proof.
Map: dark recoloring of user's October 29 second-floor drawing; retains original measurements/uncertainty.
Milestone progress: 25 percent from existing 2/8 verified milestones; individual tasks are separate.
Team: Branden Adsuara, Noah Zerarka, Gage Watts, Subir Khan, Isabel Burgos, Brandon Wu.
All hardware telemetry/route overlays in HTML are synthetic.
Server task claims still require Kratos backend deployment; standalone website does not persist shared claims.
See docs/APPROVED_UI_V1.007.md for full handoff.
