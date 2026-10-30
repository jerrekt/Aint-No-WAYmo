---
title: Ain't No Waymo — Current State and Handoff
type: project
tags: [mini-waymo, sjsu-sme, esp32, proxmox, kratos]
public: false
updated: 2026-10-29
---
Project: Ain't No Waymo / Mini-Waymo Micro.
SJSU SME three-week challenge initiated by visiting speaker Dan Berte after Opera classroom presentation.
Independent student project; not Waymo or Opera affiliated.
Team: Branden Adsuara; Noah Zerarka; Gage Watts; Subir Khan; Isabel Burgos; Brandon Wu.
Only Branden provisional systems/electronics/web role specified; other roles TBD.
Website target: aintnowaymo.adsuaracloud.com.
Latest available local candidate: V1.008; GitHub merge and deployment unverified.
Design: approved dark navy three-column layout with user diecast photo, dark hallway map, build/team right rail, SJSU and SME transparent header logos.
Site: Mini_Waymo_V12_Demo.html (legacy filename), About: Mini_Waymo_V12_About.html.
Status: local simulation only; S3 motor outputs disabled; physical autonomy unverified.
Milestones: 2/8 done = 25% display; task seed 34 (5 done, 2 in progress, 27 todo).
Task API prototype: FastAPI+SQLite; public GET; writes require server-only secret; no deployment verified; shared password insufficient for real user identity.
Kratos: independently operated Proxmox homelab for websites, game servers and SJSU student/senior projects; not university-owned.
User-reported Kratos CT 312: 1 GB RAM, 2 CPU cores; not independently verified.
Cloudflare preference: unique cloudflared connector inside each LXC, private origin; actual tunnel state unverified.
ESP32-C3 receive-only MQTT bench available; device flash and RTT measurements not verified.
Planned final control: XIAO ESP32-S3 Sense, local obstacle/link-loss stop, dual small motors, compact motor driver, forward VL53L7CX, battery, lights/chime.
Physical diecast fit unmeasured; standalone vehicle Plan A.
Hallway iPhone estimates: north 168 ft, south 168 ft, east 300 ft; no navigation-grade door coordinates.
Optional post-MVP trailer with battery and DJI O4 FPV; Goggles 3 -> iPhone DJI Fly -> Discord -> presentation PC for spectator video only.
Repository version policy: every merged PR increments exactly once from V1.000 baseline; V1.008 package is a draft, not an assumed remote release.
Review before deployment: GitHub main, CT/tunnel, API authorization, task password rotation, MQTT ACL, real telemetry ACK, physical E-stop.
See docs/CLAUDE_HANDOFF_CURRENT.md and docs/TEAM_HANDOFF_CURRENT.md.
