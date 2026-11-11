# Ain't No Waymo: Handoff for Subir

As of 2026-11-03 · Branden Adsuara (BJ)

## Where things stand

The website and simulator are live at [aintnowaymo.adsuaracloud.com](https://aintnowaymo.adsuaracloud.com); the real car is not built yet. The project is a three-week SJSU SME challenge from guest speaker Dan Berte: make the World's Littlest Waymo I-PACE diecast drive itself between rooms on the IS building's second floor. Parts are being ordered now: Noah ordered the donor RC car, the depth sensor is being ordered, and BJ has the motor driver. The exact demo date is not written down yet.

## The two versions

V1 is the low-effort fallback; V2 is the version we're building toward. Both use the same donor car, shell and ESP32-S3 Sense, and take trips sent from the website.

|  | V1: line follower | V2: room scanner |
| --- | --- | --- |
| What it does | Follows a tape line, counts junction and door marks, stops at the chosen room | Drives the hallway like a real car; at stops the roof turret sweeps the depth sensor to match the saved map, and the windshield camera reads room markers |
| Can | Room-to-room trips; stops for anything in front (single depth sensor); physical E-stop | Trips with no tape; gyro heading; stops for obstacles without Wi-Fi; stops instead of guessing when unsure; physical E-stop |
| Can't | Leave the tape, or recover if it loses count | See into rooms (2 to 3 m range), recognize people specifically, turn in place |
| Needs | Permission to tape the floor | Permission to place room markers; the parts fit confirmed |

## Hardware decisions

The car is a 1/43 drift car's guts inside the Waymo shell, with the sensor on a roof turret and the camera behind the windshield.

| Part | Decision | Why |
| --- | --- | --- |
| Shell | World's Littlest Waymo I-PACE, 112 x 45.6 x 51.2 mm outside, about 1:42 | Official size from the Waymo shop; inside still to measure with calipers |
| Drivetrain | Donor 1/43 4WD mini RC drift car (motor, steering, wheels, battery) | Fits the shell's size class; it steers like a car, so no turning in place |
| Brain and camera | XIAO ESP32-S3 Sense | Camera pokes through the windshield, facing forward, and reads room markers |
| Motor driver | DRV8833 dual H-bridge (BJ has one) | Runs on 1S, 3.3 V logic; channel A drives, channel B steers if the steering is a coil |
| Depth sensor (V2) | TF-Luna single-point lidar, 8 m, 5 g, I2C 0x10 | Decided 2026-11-05, replaces the VL53L7CX: real range down the hall; the turret wags it ±25° while driving for obstacle stop and sweeps a full arc at stops |
| Turret servo (V2) | 2 g 180-degree micro servo (2-pack bought, JR connector) | Sweeps the sensor back and forth from a printed roof dome; no slip ring |
| Gyro (V2) | GY-521 MPU-6050 board | Heading between scans; the donor has no wheel encoders |
| Sound | Piezo chime, a must | Our own tones: trip start, arrival, and please-move when blocked. No copied Waymo audio |
| Turn lights | 2 amber LEDs | Lowest priority |
| Battery | Donor's 1S pack + the XIAO's built-in charger | No separate protection board; check the pack has its own at teardown |
| E-stop | Slide switch on the motor power | Cuts motors without Wi-Fi; the ESP32 stays on |

Steering: the donor uses a servo (BJ, 2026-11-05).

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

Steering is a servo (BJ, 2026-11-05), so D2 is its signal and D3 is free. The wiring diagram on the Build page (`assets/wiring.svg`) is this table drawn out. All grounds are joined.

| XIAO pin | GPIO | V1 | V2 | Note |
| --- | --- | --- | --- | --- |
| D0 | 1 | DRV8833 AIN1 (drive) | DRV8833 AIN1 (drive) | PWM |
| D1 | 2 | DRV8833 AIN2 (drive) | DRV8833 AIN2 (drive) | PWM |
| D2 | 3 | Steering servo signal | Steering servo signal | Donor steers with a servo (BJ, 2026-11-05) |
| D3 | 4 | Free | Free | Was BIN2 for a steering coil |
| D4 | 5 | I2C SDA: VL53L7CX (0x29) | I2C SDA: TF-Luna (0x10) + gyro (0x68) | One shared bus |
| D5 | 6 | I2C SCL: VL53L7CX | I2C SCL: TF-Luna + gyro | One shared bus |
| D6 | 43 | Left turn LED (330 Ω) | Left turn LED (330 Ω) | Flickers at boot; harmless |
| D7 | 44 | Right turn LED (330 Ω) | Right turn LED (330 Ω) | |
| D8 | 7 | Line sensor (analog in) | Turret servo signal | Shared with the SD slot: no SD card |
| D9 | 8 | Piezo chime (100 Ω) | Piezo chime (100 Ω) | PWM tone |
| D10 | 9 | Rail sense (analog in) | Rail sense (analog in) | Motor rail → 100k → D10 → 100k → GND (D10 on the middle) |
| BAT+ | pad | 1S battery after the main switch | 1S battery after the main switch | Back of the XIAO; charges over USB-C |
| 3V3 | out | VL53L7CX VIN, line sensor VCC, nSLEEP | Gyro VIN, nSLEEP | The TF-Luna is NOT on 3V3 |

Power path: battery → main switch → XIAO BAT+, and main switch → E-stop → motor rail (DRV8833 VM, steering and turret servo V+, TF-Luna VCC, 470 µF bulk cap to GND).

- Gyro from the XIAO's 3V3 pin. The TF-Luna takes 3.7 to 5.2 V and about 70 mA, so it goes on the motor rail (after the E-stop; it stops with the motors, which is fine). Its I2C lines are 3.3 V logic, so no level shifter. Below about 3.7 V on the pack the Luna may misread: the D10 rail sense should flag low battery before that.
- TF-Luna pin 5 (configuration) must be tied to GND. Left open, the Luna stays in serial (UART) mode and never answers on I2C. Pin 6 stays unconnected.
- The E-stop cuts only the motor rail (driver and servos); the ESP32 stays on. D10 reads the rail, so the firmware sees both the battery level and the E-stop state.
- DRV8833: tie nSLEEP high, and put the 470 µF bulk cap across VM and GND at the board.
- Steering servo: signal on D2, V+ from the motor rail, GND common. BOUT1/BOUT2 on the DRV8833 are spare. (If the teardown shows a 5-wire servo with a position pot instead, its motor goes on BOUT1/BOUT2 and the pot wiper to D10 in place of the rail sense.)
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

The next big unlock is the donor car's teardown: it settles the steering wiring and whether everything fits.

- [ ] Tear down the donor car when it arrives: is the steering a servo or a coil, does the battery have a protection board, what are its dimensions
- [ ] Measure the shell's inside with calipers: size, wheelbase, roof height, ground clearance
- [ ] Order the rest: S3 Sense, turret servo, piezo, thin wire
- [ ] Flash the ESP32-C3 bench test and measure the delay (BJ)
- [ ] Measure the north wall doors, rooms 227 to 222 (someone at school)
- [ ] Confirm the unclear room labels: 218B, 219C, the two 216s, the repeated 223

Open questions:

- What is the exact demo date?
- Who asks permission to run the car in the IS hallways, place room markers, and (for V1) tape the floor?
- Do we build V1 at all? If tape isn't allowed, V1 could follow the wall with a side-facing distance sensor and count door gaps instead.
- Person detection: keep or drop? The please-move chime works without it, since it triggers on anything blocking the car.
