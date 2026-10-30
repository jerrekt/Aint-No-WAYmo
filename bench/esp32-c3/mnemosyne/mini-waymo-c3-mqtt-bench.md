---
title: Mini-Waymo ESP32-C3 MQTT Bench Test
type: project
tags: [mini-waymo, esp32-c3, mqtt, kratos, testing]
public: false
updated: 2026-10-29
---
Goal: Validate MQTT command/ack round-trip latency before integrating Mini-Waymo Micro motors.
Device: Existing ESP32-C3, receive-only and no GPIO outputs.
Broker: Private Mosquitto on Kratos or reachable local test host.
Topics: waymo/bench-c3/cmd, waymo/bench-c3/ack, waymo/bench-c3/status.
Commands: ping, go_now, queue_stop, pause, resume, stop, recovery.
Measurement: Python monotonic end-to-end command-to-ack RTT; summarize median, p95, maximum and no-ack count.
Status: Firmware and probe code authored; physical ESP32 connection and measured latency not yet validated.
Safety: Dedicated bench topics. No motor control. Later physical robot must stop locally on hazards or communication loss.
Next: Flash ESP32-C3, connect to broker, run 50+ sample RTT probe, record Wi-Fi environment and results.
