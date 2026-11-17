# Paste into Noah's Claude chat: finish the car wiring

```
I'm Noah, on the SJSU SME "Ain't No Waymo" team: a tiny self-driving Waymo I-PACE diecast built on a 1/43 RC drift car's drivetrain. I own the drivetrain and I'm finishing the car's wiring. BJ (project lead) already wired the gyro and the TF-Luna lidar.

Repo (public): https://github.com/jerrekt/Aint-No-WAYmo. Read these first, in this order, from the latest main:
1. handoff/handoffs/NOAH_HANDOFF.md: what's done, what's left, what to report
2. handoff/handoffs/BUILD_GUIDE.md: one-part-at-a-time rule, pass checks, risks
3. handoff/handoffs/SUBIR_HANDOFF.md, section Wiring: the pin map and power rules
4. bench/turret-s3/: the pattern every new bench sketch copies
If you can't open GitHub, tell me and I'll paste the files.

Board: Seeed XIAO ESP32-S3 Sense (not the C3). No SD card in it.
Already on the board: MPU-6050 gyro (3V3, D4/D5, 0x68) and TF-Luna (motor rail, D4/D5, pin 5 to GND, 0x10).
TF-Luna cable colors on our cable, pin 1 to 6: black +5V, white SDA, green SCL, red GND, yellow config, blue data ready. Black is power and red is ground. Never trust color alone: go by pin number.

What I'm doing, in order: (1) power path, E-stop and D10 rail sense if not final, (2) piezo on D9 and LEDs on D6/D7, (3) steering servo on D2, (4) DRV8833 on D0/D1 with the drive motor. Then I move everything into the printed tray, away from the metal shell.

How to help me:
- One step at a time. Before I connect anything, give me the exact wire-by-wire list for that step (from pin, to pin, any resistor or cap), then the bench sketch, then the pass check from the build guide. Wait for my serial output before the next step.
- Write each missing bench sketch (bench/power-s3, chime-s3, steer-s3, drive-s3) like bench/turret-s3: PlatformIO, board seeed_xiao_esp32s3, Arduino framework, USB serial JSON lines, no Wi-Fi, commands over serial, safe defaults (motor off at boot, PWM ramps, stop on any unknown command).
- After every step, have me run `i2c` on bench/turret-s3 and confirm 0x10 and 0x68 still show.
- Safety: wheels off the table for all motor tests, someone on the E-stop, nothing from the battery or motor rail to 3V3 or a GPIO, all grounds joined. If the board resets when the motor starts, stop and say so (battery brown-out).
- If the steering turns out to be a 5-wire servo or a coil, stop: it changes the pin map, and BJ decides.
- Don't touch firmware/ (motors stay disabled there), Wi-Fi, MQTT or the website. Never put Wi-Fi details, passwords or tokens in any file.
- Short, direct answers. If you're not sure of a pin, voltage or part spec, say so and ask me to check the board or the part. Don't guess.

At the end of each step, write me a short post for #waymo-build: step number, what's wired, the pass line from serial, and any numbers (servo center/left/right angles, lowest working PWM, teardown measurements).
```
