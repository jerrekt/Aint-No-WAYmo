# Ain't No Waymo: wiring handoff for Noah

As of 2026-11-16 · Branden Adsuara (BJ). Noah finishes the car's wiring from here. Paste [`NOAH_PASTE_PROMPT.md`](NOAH_PASTE_PROMPT.md) into a Claude chat to get help with each step.

The rules, pass checks and risks are in [`BUILD_GUIDE.md`](BUILD_GUIDE.md). The pin map and power rules are in [`SUBIR_HANDOFF.md`](SUBIR_HANDOFF.md#wiring), drawn on the Build page (`assets/wiring.svg`). This file covers only what is done, what is left and what to report back.

## Done (BJ, 2026-11-16)

- **Gyro** (GY-521 MPU-6050): wired on 3V3, SDA D4, SCL D5, I2C 0x68.
- **Lidar** (TF-Luna): wired on the motor rail, SDA D4, SCL D5, pin 5 to GND, I2C 0x10.
- Not written down: whether the turret servo (D8) is wired, and whether the power path below is the final one or a bench supply. Ask BJ when he hands over the board.

### TF-Luna cable colors (our cable, BJ 2026-11-16)

Go by pin number, not color. **Black is +5V and red is GND** on this cable, the opposite of normal. The colors in the TF-Luna datasheet picture are different again, so ignore them.

| Pin | Wire | Function | Goes to |
| --- | --- | --- | --- |
| 1 | **Black** | +5V | Motor rail (3.7 to 5.2 V), never 3V3 |
| 2 | White | SDA | D4 |
| 3 | Green | SCL | D5 |
| 4 | **Red** | GND | GND |
| 5 | Yellow | Config | GND (I2C mode) |
| 6 | Blue | Data ready | Not connected |

**Check this first, before adding anything:** flash `bench/turret-s3` and send `i2c`. It must list `0x10` and `0x68`. Run it again after every step below. If one disappears, the last thing you added broke the bus or the power.

## What's left, in this order

One part at a time, wheels off the table, pass check before the next one. Every ground is joined. Nothing from the battery or motor rail goes to 3V3 or to a GPIO.

| # | Wire | Pins | Bench sketch | Pass |
| --- | --- | --- | --- | --- |
| 1 | Power path, if not final yet: battery → main switch → XIAO BAT+; main switch → E-stop → motor rail. 470 µF cap across VM and GND at the DRV8833, **stripe to GND**. Rail sense: motor rail → 100k → **D10** → 100k → GND | BAT+, D10 | `bench/power-s3` (to write) | 3V3 pin reads 3.25 to 3.35 V. Serial rail volts within 0.1 V of the multimeter; about 0 with the E-stop off. Then `i2c` still shows 0x10 and 0x68 |
| 2 | Piezo (100 Ω in series) and two amber LEDs (330 Ω each) | Piezo **D9**, LEDs **D6** (left), **D7** (right) | `bench/chime-s3` (to write) | Start, arrival and please-move chimes play. LEDs blink. D6 flickering at boot is normal |
| 3 | Steering servo: signal, V+ from the motor rail, GND | Signal **D2** | `bench/steer-s3` (to write) | Finds center, left stop and right stop. Write the three angles down. No buzzing or heat at the ends: back off 2 to 3° from each stop |
| 4 | DRV8833: AIN1, AIN2, drive motor on AOUT1/AOUT2, VM on the motor rail, **nSLEEP to 3V3** | AIN1 **D0**, AIN2 **D1** | `bench/drive-s3` (to write) | Wheels up: forward and reverse at 20, 40, 60% PWM. Note the lowest PWM that still turns. E-stop off mid-run: wheels stop, rail reads about 0, board keeps printing. The board must not reset when the motor starts |

Step 2 needs a piezo and step 5 below needs thin wire; both are still to buy on the Build page. Do steps 3 and 4 first if the piezo isn't here yet.

**If the steering is not a plain 3-wire servo:** a 5-wire servo (motor plus position pot) puts its motor on DRV8833 BOUT1/BOUT2 and its pot wiper on D10 in place of the rail sense. Stop and tell BJ before wiring it that way, since it changes the pin map.

**Don't use:** D3 (spare), BOUT1/BOUT2 (spare, unless the case above), D8 (turret servo, or line sensor on V1), the SD slot (no card: it shares D8 to D10).

## After the bench steps

5. Move everything into the printed tray: no board, pad or wire end touching the metal shell. Use Kapton or hot glue where something must touch. Use thin wire and strain-relieve the servo and battery leads.
6. Run `i2c` and the drive test once more in the tray. Moving the wiring is when shorts happen.

Out of scope for this handoff (BJ): Wi-Fi and MQTT, the camera, and anything that lets the website drive the real car.

## What to send back

Post in **#waymo-build** after each step:
- The step number, a photo of the wiring, and the pass line from serial (paste the text, not a screenshot of it).
- From the teardown, if not posted yet: wheelbase, track width, steering type (3-wire servo, 5-wire or coil), battery mAh and whether it has a protection board, chassis weight.
- Step 3: the center, left and right angles. Step 4: the lowest PWM that turns the wheels, and whether the board reset.

Then mark the task done on the site's Team board, or with `/done` in Discord:
- Step 1: `hardware-03` (battery and charging)
- Step 2: `hardware-05` (chime and turn signals)
- Step 3 and step 4: `hardware-02` (drivetrain)
- E-stop check in step 4: `hardware-04`

## Code

Bench sketches go in `bench/<name>/` and copy how `bench/turret-s3` is built: PlatformIO, board `seeed_xiao_esp32s3`, one JSON line per reading on USB serial, no Wi-Fi, laptop tests for any pure logic. Push them on a branch and open a pull request, or send the folder to BJ. BJ merges. Never commit Wi-Fi details, passwords or tokens.

Motors stay off in `firmware/` (`WAYMO_MOTORS_ENABLED=0`). The drive test runs only from `bench/drive-s3`, with wheels up and someone on the E-stop.
