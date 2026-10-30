---
title: Mini-Waymo Micro Progress
type: project
tags: [mini-waymo, sjsu, sme, robotics, kratos, progress]
public: true
updated: 2026-10-29
---
Project: Mini-Waymo Micro / World’s Littlest Waymo diecast
Organization: SJSU SME student team
Setting: Industrial Studies Building, second floor
Infrastructure: Kratos / Proxmox homelab
Team repo version: V1.000
Progress: 2/8 milestones complete (25%)
Progress method: Eight equally weighted build milestones. Only verified completed milestones contribute to the displayed percentage; software simulation is not proof of a working physical robot.
Current phase: Mechanical fit and component validation
Milestones:
- 1. Challenge scope and architecture — Complete
  Evidence: Three-week scope, ESP32-S3 / Kratos split and indoor building goal defined.
- 2. Interactive website and virtual missions — Complete
  Evidence: Room queue, Go now, Pause/Resume, route preview and safety simulation built and tested in a browser.
- 3. Measure diecast and verify component fit — In progress
  Evidence: Adjustable fit planner exists; actual shell interior has not been measured or validated.
- 4. Assemble drivetrain, power and electronics — Not started
  Evidence: Motors, battery, wiring and physical E-stop are not verified on a built vehicle.
- 5. Integrate real sensing and local safety — Not started
  Evidence: Depth sensor, encoders, IMU, markers and motor control need physical calibration.
- 6. Deploy Kratos website, MQTT and telemetry — Not started
  Evidence: FastAPI/MQTT examples exist but are not deployed to the live server or vehicle.
- 7. Survey IS second-floor route and relocalize — Not started
  Evidence: Current C-shaped hallway map is schematic; actual room locations and localization remain unverified.
- 8. Demonstrate supervised room-to-room mission — Not started
  Evidence: Physical routes (e.g., 251 → 263 → 251 → 202), arrival chime and turn signals need tests.
Physical hardware remains unvalidated until measured, built, and tested.
Live Kratos deployment: not complete as of this update.
Mission target: IS 251 -> 263 -> 251 -> 202.
Data source: project_progress.json
