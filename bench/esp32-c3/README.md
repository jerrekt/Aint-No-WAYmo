# Mini-Waymo Micro: ESP32-C3 MQTT receive-only bench test

This is a no-output communication test for the three-week SJSU Mini-Waymo project.
It intentionally does **not** drive motors, GPIO pins, LEDs, the chime, or any sensors.
It does log messages to USB Serial and publish MQTT acknowledgments.

The ESP32-C3 is only the test receiver; you can later swap in the ESP32-S3 Sense.
The `type` names match the existing V12 Kratos API, but all topics are isolated under
`waymo/bench-c3/` to prevent accidental control of future hardware.

## Data flow

```
Kratos / laptop: probe.py  --QoS 1-->  Mosquitto  -->  ESP32-C3
          ^                                         |
          +-- ack topic (QoS 0)  <--- Mosquitto  <--+
```

Commands: `ping`, `go_now`, `queue_stop`, `mission`, `pause`, `resume`, `stop`,
`hold`, `clear_pending`, `request_marker_observation`.

MQTT topics:
- `waymo/bench-c3/cmd`: command JSON, sent non-retained.
- `waymo/bench-c3/ack`: command ID, accepted/rejected, simulated state and timing.
- `waymo/bench-c3/status`: heartbeat roughly every 2 seconds, no real telemetry.

Example outbound command:

```json
{"id":"abcd1234-0001","type":"go_now","room":"263"}
```

Example acknowledgment **format, not a measured result**:

```json
{"id":"abcd1234-0001","type":"go_now","accepted":true,"reason":"simulated_only","state":"MOVING_SIM","room":"263","motor_output_enabled":false,"rx_count":2,"rssi_dbm":-51,"esp_processing_ms":1,"uptime_ms":3300}
```

## Fastest option: Arduino IDE

Open `Mini_Waymo_C3_Bench.ino`, enter the Wi-Fi and MQTT credentials at the top,
install `PubSubClient` and `ArduinoJson` via Library Manager, select your ESP32-C3
board, and upload. For a Seeed XIAO C3, Seeed documents the Arduino board
choice as `XIAO_ESP32C3`. Open Serial Monitor at 115200 baud.

This is an alternative to the PlatformIO project below; do not copy both into
the same sketch folder.

## 1. Flash ESP32-C3 with PlatformIO

Connect the C3 to your laptop using a USB data cable.
Use VS Code + PlatformIO and open this folder.

Board selection:
- Seeed XIAO ESP32-C3: default `xiao_esp32c3` environment.
- Typical Espressif ESP32-C3 DevKitM: `pio run -e esp32c3_devkitm -t upload`.
- If you have another ESP32-C3 variant, change the `board` entry accordingly.

First copy `src/secrets.example.h` to `src/secrets.h` (the latter is Git-ignored), then edit `src/secrets.h` with:
- A **2.4 GHz** Wi-Fi SSID and password that the C3 can join.
- The private, reachable IP/DNS of the Mosquitto broker, not a public website URL.
- The dedicated MQTT bench account username/password.

Upload and open Serial Monitor at 115200 baud. You should see
`Mini-Waymo C3 MQTT BENCH TEST: NO GPIO OUTPUTS`, then MQTT connected.
If the board isn't recognized, check the USB cable and actual board variant.

**Keep passwords out of Git.** `src/secrets.h` is a local configuration file;
never commit or share it in source archives.

## 2. Set up a PRIVATE MQTT broker on Kratos

If Kratos already has Mosquitto, reuse it and add **separate bench user accounts**.
You do not need a second broker, and you should not disturb live projects.

On a Debian/Ubuntu LXC, if Mosquitto is not installed:

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
```

For authentication, create two users using `mosquitto_passwd` and adapt
`broker_acl.example` to the broker's existing ACL configuration. Use a private
listener accessible to the C3 and the test script. If the broker is in an LXC,
use the IP that actually reaches that LXC. Ports can be blocked by Proxmox,
UniFi firewall rules, or broker listener settings.

**Do not forward unencrypted port 1883 to the public internet.** The example
firmware uses plain MQTT intended only for a trusted LAN/test network. For testing
from SJSU, arrange a secured broker endpoint or an authenticated local bridge
back to Kratos. Do not assume an ESP32-C3 can directly join a Tailscale network.

## 3. Run the latency test from Kratos

Install the dependency in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Export broker login information in your shell (never paste it into chat):

```bash
export WAYMO_MQTT_HOST='YOUR_PRIVATE_BROKER_IP'
export WAYMO_MQTT_USER='waymo_bench_controller'
export WAYMO_MQTT_PASS='YOUR_BROKER_PASSWORD'
```

Then run 50 round-trip probes followed by a sample mission command sequence:

```bash
python probe.py --count 50 --interval-ms 100 --demo --output results/first_run.csv
```

The report includes sent/acknowledged/no-ack totals, average, median, 95th
percentile, 99th percentile, and maximum **round-trip** latency, plus
Wi-Fi RSSI and ESP processing time on each acknowledgment.

The resulting files are `results/first_run.csv` and
`results/first_run.summary.json`. Re-run from your laptop to compare LAN,
Kratos LXC, and eventually campus-to-Kratos network paths.

## 4. How to interpret the results

**RTT (round-trip time)** is measured entirely using `probe.py`'s monotonic
clock: Kratos -> Mosquitto -> ESP32 -> Mosquitto -> Kratos. No clock
synchronization is required. It is *not* one-way control latency or motor
reaction time; it includes the device sending an acknowledgment back.

Initial prototype targets (not guaranteed performance):
- Acknowledgments on >= 99% of probes on a stable local network.
- LAN p95 RTT below roughly 150 ms is a useful early goal.
- Noticeable spikes / timeouts need investigation regardless of the average.

The ESP's `esp_processing_ms` only measures software callback time prior to
attempting to publish its ack; it excludes broker and Wi-Fi transit.

Test at least twice: once with both on the same trusted LAN, then on the
actual network arrangement you'll use in the IS building. Wi-Fi strength,
firewalls, and home-to-campus routing can change the results dramatically.

**Safety:** Network response time must never determine obstacle stopping or
motor braking. The ESP32-S3 physical vehicle will need local stop logic and
independent hardware E-stop regardless of these measurements.

## 5. Run offline tests

```bash
python -m unittest discover -s tests -v
```

These unit tests validate report calculations; they cannot verify your physical
ESP32, live Mosquitto, or the V12 website. The C3 firmware has not been flashed
or compiled by the author in this environment without PlatformIO/hardware.

## 6. Relationship to the current V12 website

Existing V12 Kratos live topics are `waymo/micro-01/cmd` and
`waymo/micro-01/telemetry`. This bench test deliberately **does not subscribe**
to those topics. Its message types are compatible with the V12 API at a
schema-concept level. A real backend integration would assign unique command
IDs, collect device acknowledgments, and expose RTT to an admin-only panel.
Never reuse this receive-only state machine to control real motors.
