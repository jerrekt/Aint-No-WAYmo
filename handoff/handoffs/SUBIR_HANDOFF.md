# Ain't No Waymo: Handoff for Subir

As of 2026-11-03 · Branden Adsuara (BJ)

## Where things stand

The website and simulator are live at [aintnowaymo.adsuaracloud.com](https://aintnowaymo.adsuaracloud.com); the real car is not built yet. The project is a three-week SJSU SME challenge from guest speaker Dan Berte: make the World's Littlest Waymo I-PACE diecast drive itself between rooms on the IS building's second floor. Parts are being ordered now: Noah ordered the donor RC car, the depth sensor is being ordered, and BJ has the motor driver. The exact demo date is not written down yet.

## The two versions

V1 is the low-effort fallback; V2 is the version we're building toward. Both use the same donor car, shell and ESP32-S3 Sense, and take trips sent from the website.

|  | V1: line follower | V2: room scanner |
| --- | --- | --- |
| What it does | Follows a tape line, counts junction and door marks, stops at the chosen room | Drives the hallway like a real car; at stops the roof turret sweeps the lidar to match the saved map, and the hood camera reads room markers |
| Can | Room-to-room trips; stops for anything in front (single depth sensor); physical E-stop | Trips with no tape; gyro heading; stops for obstacles without Wi-Fi; stops instead of guessing when unsure; physical E-stop |
| Can't | Leave the tape, or recover if it loses count | See into rooms (2 to 3 m range), recognize people specifically, turn in place |
| Needs | Permission to tape the floor | Permission to place room markers; the parts fit confirmed |

## Hardware decisions

The car is a 1/43 drift car's guts inside the Waymo shell, with the lidar on a roof turret and the camera on the hood.

| Part | Decision | Why |
| --- | --- | --- |
| Shell | World's Littlest Waymo I-PACE, 112 x 45.6 x 51.2 mm outside, about 1:42 | Official size from the Waymo shop; inside still to measure with calipers |
| Drivetrain | Donor 1/43 4WD mini RC drift car (motor, steering, wheels, battery) | Fits the shell's size class; it steers like a car, so no turning in place. Teardown (Nov 9): drive motor in the rear gearbox; steering is a small DC motor with a position pot (the stock board's RV pads), not a 3-wire servo |
| Brain and camera | XIAO ESP32-S3 Sense with the OV5640 autofocus camera | The camera sits on the hood, facing forward, on a small printed stand; its flat cable snakes through the hood vent to the board. Its job: read the printed room marker by each door so the car knows which room it's at, and stop instead of guessing if it can't read one |
| Motor driver | DRV8833 dual H-bridge (BJ has one) | Runs on 1S, 3.3 V logic; channel A drives, channel B runs the steering motor |
| Depth sensor (V2) | TF-Luna single-point lidar, 8 m, 5 g, I2C 0x10 | Decided 2026-11-05, replaces the VL53L7CX: real range down the hall; the turret wags it ±25° while driving for obstacle stop and sweeps a full arc at stops |
| Turret servo (V2) | 2 g 180-degree micro servo (2-pack bought, JR connector) | Sweeps the TF-Luna back and forth from a printed roof dome; no slip ring. Needs a printed adapter (servo horn to Luna) and a hole drilled in the roof for the servo and its wires |
| Gyro (V2) | GY-521 MPU-6050 board | Heading between scans; the donor has no wheel encoders |
| Sound | Piezo chime, a must | Waymo-style tones: trip start, arrival, and please-move when blocked |
| Hazard lights | 2 amber LEDs on one pin (D6) | No turn signals: both blink together as hazards when the car stops for a person or is parked (decided 2026-11-10) |
| Battery | Donor's 1S pack + the XIAO's built-in charger | Teardown: 701530 pouch, 1S 3.7 V 220 mAh (7 x 15 x 30 mm), protection board likely under the yellow tape. Too small for the S3 with Wi-Fi and camera: a 1S 400 to 500 mAh that fits is the upgrade |
| E-stop | Slide switch on the motor power | Cuts motors without Wi-Fi; the ESP32 stays on |

Steering: a small DC motor with a position pot (teardown 2026-11-09). The ESP32 runs the motor through the DRV8833 and reads the pot, closing the loop itself like a servo does.

## Parts

The Build page on the site is the live list. When you buy something, mark it there (or in Discord) so everyone sees it. Status as of 2026-11-03:

| Part | Status | Who | For |
| --- | --- | --- | --- |
| Waymo shell | On hand | BJ | Both |
| DRV8833 motor driver | On hand | BJ | Both |
| Bulk capacitor, LEDs, resistors | On hand | BJ | Both |
| 3D printer and filament (chassis, turret dome, markers) | On hand | BJ | Both |
| ESP32-C3 | On hand, bench tests only (no camera) | BJ | Testing |
| Donor 1/43 RC drift car | Ordered | Noah | Both |
| TF-Luna lidar (replaces the VL53L7CX; don't order the 7CX) | Delivered Nov 5 | BJ | V2 |
| XIAO ESP32-S3 Sense + OV5640 autofocus camera (second board is for another project) | Ordered Nov 5 from Seeed (US warehouse) | BJ | Both |
| 2 g micro servo (turret), 2-pack, JR connector | Ordered Nov 5, arrives Sat Nov 7 | BJ | V2 |
| Gyro (GY-521 MPU-6050, 3-pack) | Delivered Nov 5 | BJ | V2 |
| Piezo sounder (chime) | To buy | Not set | Both |
| Thin wire (about 30 AWG) | To buy | Not set | Both |
| Kapton tape (4-pack) | Ordered Nov 5, arrives Sat Nov 7 | BJ | Both |
| Multimeter or USB power meter | To check if someone has one | Not set | Both |
| Line sensor, floor tape | Only if we build V1 | Not set | V1 |
| VL53L7CX depth sensor (V1 front, Pololu #3418; in place of the VL53L1X) | Arrived | Subir | V1 |
| Phone hotspot | Use a phone; no purchase | Not set | Both |

Pololu ships from Las Vegas, so UPS Ground usually arrives in 1 to 2 days. Add the gyro to the same Pololu order to share shipping.

## Wiring

Updated 2026-11-10 after the teardown: steering is a DC motor plus a pot, so D2/D3 drive it through the DRV8833 and D10 reads the pot; battery sense moves to D9, the piezo to D7, and both amber LEDs share D6 (hazards only). The car's S3 is wired with leads soldered straight to the pins. The wiring diagram on the Build page (`assets/wiring.svg`) is this table drawn out. All grounds are joined.

| XIAO pin | GPIO | V1 | V2 | Note |
| --- | --- | --- | --- | --- |
| D0 | 1 | DRV8833 AIN1 (drive) | DRV8833 AIN1 (drive) | PWM |
| D1 | 2 | DRV8833 AIN2 (drive) | DRV8833 AIN2 (drive) | PWM |
| D2 | 3 | DRV8833 BIN1 (steering motor) | DRV8833 BIN1 (steering motor) | PWM |
| D3 | 4 | DRV8833 BIN2 (steering motor) | DRV8833 BIN2 (steering motor) | PWM |
| D4 | 5 | I2C SDA: VL53L7CX (0x29) | I2C SDA: TF-Luna (0x10) + gyro (0x68) | One shared bus |
| D5 | 6 | I2C SCL: VL53L7CX | I2C SCL: TF-Luna + gyro | One shared bus |
| D6 | 43 | Both amber LEDs (330 Ω each) | Both amber LEDs (330 Ω each) | Hazards only; flickers at boot, harmless |
| D7 | 44 | Piezo chime (100 Ω) | Piezo chime (100 Ω) | PWM tone |
| D8 | 7 | Line sensor (analog in) | Turret servo signal | Shared with the SD slot: no SD card |
| D9 | 8 | Battery sense (analog in) | Battery sense (analog in) | Motor rail → 100k → D9 → 100k → GND (D9 on the middle) |
| D10 | 9 | Steering pot wiper (analog in) | Steering pot wiper (analog in) | Pot fed from 3V3, so the wiper stays in the ADC range |
| BAT+ | pad | 1S battery after the main switch | 1S battery after the main switch | Back of the XIAO; charges over USB-C |
| 3V3 | out | VL53L7CX VIN, line sensor VCC, steering pot, nSLEEP | Gyro VIN, steering pot, nSLEEP | The TF-Luna is NOT on 3V3 |

Power path: battery → main switch → XIAO BAT+, and main switch → E-stop → motor rail (DRV8833 VM, turret servo V+, TF-Luna VCC, 470 µF bulk cap to GND).

- Gyro from the XIAO's 3V3 pin. The TF-Luna takes 3.7 to 5.2 V and about 70 mA, so it goes on the motor rail (after the E-stop; it stops with the motors, which is fine). Its I2C lines are 3.3 V logic, so no level shifter. Below about 3.7 V on the pack the Luna may misread: the D9 battery sense should flag low battery before that.
- TF-Luna pin 5 (configuration) must be tied to GND. Left open, the Luna stays in serial (UART) mode and never answers on I2C. Pin 6 stays unconnected.
- The E-stop cuts only the motor rail (driver and servos); the ESP32 stays on. D9 reads the rail, so the firmware sees both the battery level and the E-stop state.
- DRV8833: tie nSLEEP high, and put the 470 µF bulk cap across VM and GND at the board.
- Steering: the motor on DRV8833 BOUT1/BOUT2 (D2/D3), the pot on 3V3 and GND with its wiper on D10. Find the wiper with a meter first (the pad whose resistance sweeps as you turn the wheels).
- Resistors go right at the pin, under heat-shrink: 330 Ω per LED on D6, 100 Ω on D7, and the 100k/100k divider on D9. Never feed the battery or motor rail straight into any pin.
- Wire colors: black GND, red battery + (before the E-stop), orange motor rail (after the E-stop), white 3V3, blue SDA, green SCL, yellow signals with pin-number tags. Keep the stock pink/blue motor leads; the stock pot lead's red is 3.3 V, so tag it white.
- If the Luna is noisy on the shared rail, add a 100 µF cap at its connector.
- No SD card in the Sense board, because pins D8 to D10 are shared with it.
- The shell is metal: nothing conductive may touch it. Keep boards in the printed tray (or under tape or hot glue), and the Wi-Fi antenna out of the metal.

## Website and repo

Everything lives in this repo; merged changes go live on the site within about a minute. Read `CLAUDE.md` at the repo root first. It has the full rules, and Claude Code loads it automatically.

1. Make a branch; never commit to `main` (it's protected).
2. Make your change. Preview it at desktop width and at 400 px (phone).
3. Bump the version once per pull request: `python3 tools/version.py bump --message "what changed"`.
4. Run the checks: `python3 tools/check_repo.py`, then the four node tests in `tests/` (listed in `CLAUDE.md`).
5. Open a pull request. BJ reviews and merges.

If two pull requests pick the same next version, whichever merges second has to update from `main` and bump again.

Where things are:

- **Main pages:** `Mini_Waymo_V12_Demo.html` (live map, simulator, Build, Team) and `Mini_Waymo_V12_About.html`. The V9/V10/V12 names are old snapshots, not the version.
- **Tasks:** `team_tasks.json`. Claim and update tasks on the site or in Discord (`/claim`, `/done`, `/tasks`).
- **Parts:** `build_parts.json`. Run `python3 tools/embed_build_parts.py` after editing it.
- **Map:** generated, never hand-edited. Edit `tools/build_map_svg.py`, then run `python3 tools/build_map_svg.py && python3 tools/sync_room_list.py && python3 tools/embed_map.py`. That refreshes the map, the Where to? room list and the clickable rooms.

Never put the team password, the Discord webhook or any token in a file, a pull request or a chat.

## Server and the ESP32 link

A private MQTT broker (the message server the car will talk to) is set up, with logins and per-account topic limits. BJ runs the server side, so ask him for anything there; no one else needs server access.

- **Done:** broker built and locked down; the controller login and its topics tested.
- **Next:** flash the ESP32-C3 bench test (`bench/esp32-c3`, no motor output) and measure the round-trip delay. The goal is under 150 ms for 95% of messages; nothing has been measured yet.
- **Later:** reaching the broker from campus with the car on a phone hotspot. That needs a firmware change and a security review first.

**Manual drive (V1.045).** The Controls page has a "Drive it yourself" pad behind the team password. When BJ turns it on for the car, the server sends on `waymo/micro-01/cmd`:

`{"type":"manual","seq":12,"throttle":0.5,"steer":-0.2,"ttl_ms":400}`

throttle and steer run from -1 to 1 (steer +1 = left). The firmware must: drop any command whose `seq` is not newer than the last one; scale throttle to a safe walking speed; and **stop the motors if no newer command arrives within `ttl_ms`** (a dead man, so a closed tab or lost Wi-Fi stops the car). `ttl_ms: 0` means stop now. The depth-sensor stop and the physical E-stop still win over manual commands.

Wi-Fi and broker passwords go only in the board's `secrets.h`, which Git ignores. Never commit or screenshot that file.

## Next steps

The teardown is done (Nov 9). Next: fit everything in the shell and power up the wired car S3.

- [x] Tear down the donor car: steering is a DC motor with a position pot; battery is a 1S 220 mAh 701530 pouch
- [ ] Find the steering pot's wiper with a meter; note which motor plug is drive and which is steering
- [ ] Measure the shell's inside with calipers: size, wheelbase, roof height, ground clearance; compare the donor's wheelbase
- [ ] Print the turret adapter (servo horn to TF-Luna) and drill the roof hole for the servo
- [ ] Print the hood camera stand; route the camera's flat cable through the hood vent
- [ ] Order the rest: piezo, a 1S 400 to 500 mAh battery that fits
- [ ] First power on the car S3: continuity check for shorts, then USB only
- [ ] Flash the ESP32-C3 bench test and measure the delay (BJ)
- [ ] Measure the north wall doors, rooms 227 to 222 (someone at school)
- [ ] Confirm the unclear room labels: 218B, 219C, the two 216s, the repeated 223

Open questions:

- What is the exact demo date?
- Who asks permission to run the car in the IS hallways, place room markers, and (for V1) tape the floor?
- Do we build V1 at all? If tape isn't allowed, V1 could follow the wall with a side-facing distance sensor and count door gaps instead.
- Person detection: keep or drop? The please-move chime works without it, since it triggers on anything blocking the car.
