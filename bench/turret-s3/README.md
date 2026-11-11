# Roof turret bench test (XIAO ESP32-S3 Sense)

Sweeps the 2 g turret servo and reads the TF-Luna lidar over I2C, printing one JSON line per reading on USB serial. **Bench only:** no drive motor, no steering, no Wi-Fi. Compiled for `seeed_xiao_esp32s3`; not yet run on the real board.

## Wiring (from `handoff/handoffs/SUBIR_HANDOFF.md`)

| From | To | Note |
| --- | --- | --- |
| Servo signal (orange/yellow) | **D8** (GPIO7) | No SD card in the Sense board: D8 is shared with it |
| Servo V+ (red) | Motor rail (after the E-stop) | On the bench, 3.7 to 5 V from the battery or a bench supply |
| TF-Luna pin 1 VCC | Motor rail | **3.7 to 5.2 V, not the 3V3 pin** |
| TF-Luna pin 2 SDA | **D4** (GPIO5) | Shared I2C bus with the gyro and VL53L7CX |
| TF-Luna pin 3 SCL | **D5** (GPIO6) | |
| TF-Luna pin 4 GND | GND | |
| **TF-Luna pin 5 (CFG)** | **GND** | **Required.** Left open, the Luna talks serial (UART) and never answers on I2C |
| TF-Luna pin 6 | Not connected | |
| All grounds | Joined | XIAO, servo, Luna, battery |

## Flash and run

```
pio run -d bench/turret-s3 -t upload
pio device monitor -d bench/turret-s3
```

At boot it lists the I2C addresses it finds (expect `0x10` TF-Luna, `0x68` gyro, `0x29` VL53L7CX if connected), checks the Luna, centers the servo and waits for a command:

| Command | What it does |
| --- | --- |
| `wag` | Wags ±25° around center, as while driving; prints a pass summary at each end |
| `sweep` | One full sweep (10° to 170°), as at a stop; then back to center |
| `center` / `angle N` | Move and hold |
| `read` | One reading where it points now |
| `quiet` | Hide the per-reading lines (summaries still print) |
| `i2c` | List I2C addresses again |
| `off` | Stop and let the servo go limp |

Reading line: `{"t":1234,"mode":"wag","deg":95,"cm":134,"amp":812,"temp_c":31.2,"q":"good"}`. `q` is `good`, `weak` (signal under 100: nothing in range), `saturated`, `too_close` (under 20 cm), `far` (over 8 m) or `no_data` (no answer).

Pass summary: `{"pass":"wag",...,"nearest_cm":134,"nearest_deg":95,"clear":true}`. `clear` is false for anything under 32 cm, a saturated or too-close reading, or a pass with no usable readings. It is a bench check, not the car's safety stop.

## Calibrate after the turret is built

At the top of `src/main.cpp`: `SERVO_CENTER_DEG` (straight ahead), `SERVO_MIN_DEG`/`SERVO_MAX_DEG` (keep off the end stops and the wires), and `SERVO_MIN_US`/`SERVO_MAX_US` if the servo buzzes at the ends.

## Tests

The pure logic (`src/turret_logic.h`) has laptop tests:

```
g++ -std=c++17 -I bench/turret-s3/src bench/turret-s3/tests/test_turret_logic.cpp -o /tmp/turret_test && /tmp/turret_test
```
