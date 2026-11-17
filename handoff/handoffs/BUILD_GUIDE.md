# Ain't No Waymo: car build guide

As of 2026-11-16 · Branden Adsuara (BJ). For the team, and for a Claude chat helping with the build (paste this file, or point Claude Code at it).

This takes the car from "ESP32 mostly wired" to driving trips in the IS hallway. The pin map and power rules live in [`SUBIR_HANDOFF.md`](SUBIR_HANDOFF.md#wiring) and the diagram on the Build page (`assets/wiring.svg`); this guide is the order to do things in and how to know each step worked.

## The rule: one part at a time

Don't wire everything and then load the full code. If the car doesn't move, you can't tell if it's a wire, a part, power or the code. Instead:

1. Connect **one** component.
2. Flash **its** bench test.
3. Check the pass line below. Paste the serial output in the chat if anything looks off.
4. Only then connect the next one.

Order: power and rail sense → I2C bus → turret (TF-Luna + servo) → gyro → chime and lights → steering servo → drive motor and E-stop → Wi-Fi and MQTT → camera. Motors come late on purpose: everything before them can't run the car off the table.

## Before any power

- [ ] Board is the **XIAO ESP32-S3 Sense** (the pin map is for it; the C3 has different GPIOs). No SD card in the Sense slot (D8 to D10 are shared with it).
- [ ] Every ground joined: XIAO, DRV8833, both servos, TF-Luna, gyro, battery.
- [ ] Nothing from the battery or motor rail touches 3V3 or a GPIO. The gyro is on **3V3**; the TF-Luna and servos are on the **motor rail**.
- [ ] TF-Luna **pin 5 tied to GND** (otherwise it talks serial and never shows up on I2C). Pin 6 open.
- [ ] DRV8833 nSLEEP tied high (3V3). 470 µF cap across VM and GND at the driver, **stripe to GND**.
- [ ] D10 divider: motor rail → 100k → D10 → 100k → GND.
- [ ] E-stop switch is in the motor rail only (battery → main switch → E-stop → rail). The XIAO stays powered when it's off.
- [ ] Multimeter continuity: no short between BAT+ and GND, or 3V3 and GND.
- [ ] Wheels off the table for everything until step 7 passes.

## Bench steps

Each step names its sketch. If the folder doesn't exist yet, ask Claude to write it in `bench/<name>/` (PlatformIO, `seeed_xiao_esp32s3`, one JSON line per reading on USB serial, no Wi-Fi), the same way `bench/turret-s3` is built.

| # | Connect | Sketch | Pass |
| --- | --- | --- | --- |
| 1 | Battery, main switch, E-stop, D10 divider (no loads) | `bench/power-s3` (to write) | Multimeter: 3V3 pin 3.25 to 3.35 V. Serial: rail volts within 0.1 V of the multimeter; drops to about 0 with the E-stop off |
| 2 | Gyro (3V3, SDA D4, SCL D5) and the TF-Luna (rail, D4, D5, pin 5 to GND) | `bench/turret-s3`, command `i2c` | Lists `0x10` (Luna) and `0x68` (gyro). Missing 0x10: pin 5 not grounded or Luna not on the rail |
| 3 | Turret servo signal on **D8**, V+ on the rail | `bench/turret-s3`: `center`, `wag`, `sweep` | Servo moves smoothly, no buzzing at rest. `wag` pass lines say `"clear":true` with nothing near; a hand at 20 cm gives `"clear":false`. Readings `q:"good"` at a wall 1 to 3 m away, within 5 cm of a tape measure |
| 4 | (gyro already on) | `bench/gyro-s3` (to write) | Sits still 60 s: heading drift under 2°. Turned 90° by hand on the table: reads 85 to 95° |
| 5 | Piezo on D9 (100 Ω), LEDs on D6/D7 (330 Ω) | `bench/chime-s3` (to write) | Start, arrival and please-move chimes play the same tunes as the site. LEDs blink (D6 flickers at boot, that's normal) |
| 6 | Steering servo signal on **D2**, V+ on the rail | `bench/steer-s3` (to write) | Finds center, left and right stops. Write the three numbers down. The servo must **not** buzz or get warm at the ends (back off 2 to 3° from each stop) |
| 7 | DRV8833 AIN1 **D0**, AIN2 **D1**, motor on AOUT1/AOUT2 | `bench/drive-s3` (to write) | Wheels up: forward and reverse at 20, 40, 60% PWM. Note the lowest PWM that still turns the wheels. E-stop off mid-run: wheels stop, rail reads about 0, board keeps printing. Board must not reset when the motor starts (if it does: battery, see Risks) |
| 8 | Wi-Fi (phone hotspot or the 2.4 GHz home network), broker login | `bench/esp32-c3` adapted for the S3 | Joins Wi-Fi, connects to the MQTT broker, `probe.py` round trip under 150 ms for 95% of messages. Secrets only in `secrets.h` (git-ignored) |
| 9 | Camera (already on the Sense) | `bench/camera-s3` (to write) | Saves a frame over USB or Wi-Fi with a printed marker readable at 30 to 50 cm. V2 only; can wait |

After each step, tick the matching task on the site's Team board (or `/done` in Discord) and mark parts bought on the Build page.

## Mechanical

Runs in parallel with the bench steps. Noah and Isabel lead.

1. **Teardown of the donor car**: record wheelbase, track width, motor size, steering servo type and travel, battery size, mAh and whether it has a protection board. Weigh the chassis.
2. **Measure the shell** with calipers: inside length, width, roof height, wheel arch centers (the I-PACE at 1:42 is about 71 mm wheelbase; most 1/43 donors are 62 to 65 mm, so check before cutting).
3. **Weigh the shell** and test the donor carrying it (tape it on): does it still move at low PWM?
4. **Print the tray** that holds the XIAO, DRV8833 and gyro off the metal shell (Kapton only where a board must touch metal). Camera lens at the windshield, facing forward. Wi-Fi antenna outside the metal or at a window.
5. **Print the roof dome** for the turret: servo inside, TF-Luna on the horn, wires down through the roof. Keep it low.
6. Cable everything with the thin wire; strain-relief at the servo and battery leads.

## Putting it together (code)

Once steps 1 to 7 pass on the bench, the drivers go into the real firmware (`firmware/`, the S3 scaffold with the C++ safety core; motors are off by default, `WAYMO_MOTORS_ENABLED=0`). Ask Claude to:

1. Move each passing bench driver into `firmware/` (power, Luna, turret, gyro, chime, steering, drive).
2. Wire the **safety stop first**: Luna reading under the stop distance, E-stop off, low battery, lost link or a stale command each stop the motor. Test each one wheels-up before enabling motors.
3. Add manual drive over MQTT (the site already has it, V1.045: `{type:manual, seq, throttle, steer, ttl_ms:400}` on `waymo/micro-01/cmd`) with the firmware dead man: no fresh command within 400 ms means stop.
4. Then trips: heading hold on the gyro, count doors with the Luna, confirm the room with the camera marker (V2) or the tape count (V1).

Security note: anything that lets the site drive the real car is flagged work. Switch Claude to Opus high for it and log it in Mnemosyne `runbooks/security-review.md` first.

## Drive tests, in order

Each one passes before the next. Someone holds the E-stop every time.

1. Wheels up, manual drive from the site: forward, reverse, steer, dead man (close the tab: wheels stop within half a second).
2. On the floor, manual: straight line at walking pace or slower; steering trim so it tracks straight.
3. Gyro heading hold: 5 m straight with no steering input, under 20 cm drift.
4. Obstacle stop: walk a shoe into its path at crawl speed; it stops before touching and plays please-move.
5. Door turn-in: from the hall, turn into a doorway and stop.
6. One hallway run with manual drive, recording the Luna and gyro logs (Brandon's door positions to compare against).
7. First trip from the site: 214 to 210 (short, straight, same wall).
8. Longer trips; then the demo route.

## Risks to watch

- **Battery brown-out**: the donor's tiny 1S pack may not run the S3, Wi-Fi, the Luna and the motor together. If the board resets when the motor starts, try a 300 to 500 mAh 1S pack that fits.
- **Weight**: the zinc shell is heavy for a donor motor made for a plastic body. Check at mechanical step 3.
- **Crawl speed**: drift-car motors are geared fast and stall at low PWM. Find the lowest working PWM at bench step 7.
- **Metal shell**: shorts, and it blocks Wi-Fi. Tray, Kapton, antenna placement.
- **Indoor compass**: the map's north (47°) came from a phone inside a steel building; it doesn't affect driving.

## What's done (2026-11-16)

- On hand: Waymo shell, ESP32-C3 (bench only), XIAO ESP32-S3 Sense (ordered Nov 5; confirm it arrived), DRV8833, TF-Luna, MPU-6050 gyro (3), turret servos (2), Kapton, caps, LEDs, resistors, printer.
- Still to buy: piezo, thin wire (about 30 AWG), multimeter or USB power meter if nobody has one.
- Code: `bench/turret-s3` (Luna + turret) written, not yet run on the board. `bench/esp32-c3` MQTT test written for the C3. `firmware/` scaffold with motors disabled. Manual drive on the site (V1.045).
- Map: the Facilities floor plan with the simulator's stops and 35 rooms (V1.052).
