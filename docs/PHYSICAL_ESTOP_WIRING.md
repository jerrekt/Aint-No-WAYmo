# Mini-Waymo Micro V9 — physical emergency stop (proposed bench wiring)

**Not yet built, wired, validated, or approved for public hallway use.** The browser `Emergency stop (simulation)` button is only a simulation. Software, a website, an MQTT `stop` message, or a PWM=0 command do not replace a genuine hardware stop.

## Mandatory hardware

- A **latching, dual-pole, normally-closed (NC)** emergency-stop switch (two independent sets of NC contacts) rated by its manufacturer for the battery's DC voltage and the propulsion system's maximum interruption current. A suitable bench tether is acceptable if the model is too small.
- Proper inline fuse, insulated connectors, strain relief, and motor-driver power isolation.
- A tested, separate power-off/kill means accessible to a nearby human supervisor.
- All actuators that can drive the robot must be isolated. If adding any powered steering actuator, validate its safe stop path as well.

## Suggested circuit logic (not a final pinout)

```
Battery positive -- fuse -- NC contact A -- motor driver VM (drive-power only)
Battery negative -------------------------- motor driver GND

ESP32-S3 3.3V logic remains powered by separate regulated supply
ESP32 GPIO configured INPUT_PULLUP -- NC contact B -- GND

NC closed (released) : GPIO LOW, but software still boots disarmed
NC open (pressed or broken sense wire): GPIO HIGH -> latch stop

ESP32 logic ground and motor-driver ground share reference as required
by the selected driver. No direct battery voltage reaches a GPIO.
```

**Use `WAYMO_ESTOP_SENSE_GPIO=-1` until physical pin assignments are validated**; this forces bench-stop state. After wiring, configure the GPIO via PlatformIO build flags and confirm the board's pin capabilities against the installed camera, motor, and sensor peripherals. This is deliberately not a recommended fixed GPIO.

## Reset behavior

1. Pressing the switch must interrupt the drive power mechanically, irrespective of firmware/Wi-Fi/server failures. A firmware latch is secondary defense.
2. Releasing the mushroom switch does **not** automatically restart the robot.
3. Inspect for an obstruction/unsafe condition and intentionally rearm locally after confirming all sensors and location are valid. The current bench scaffold does **not implement arming** and will not drive even after switch release.
4. Test failure modes with the wheels off the ground: cut Wi-Fi, disconnect the E-stop sense wire, reset the MCU, and unplug the driver supply. Verify actuation isolation with a meter and test loads before attaching wheels.

## Known gaps

- Physical stop hardware has not been selected or tested for motor stall current.
- A mechanical switch may be unsuitable for interrupting a motor's DC inductive load without a suitably rated switching circuit. Confirm DC rating and wiring with a qualified supervisor.
- The current ESP32 firmware does not drive motor pins and accepts only a literal `STOP` bench command. Kratos's example JSON-based commands are not integrated with it.
- The simulator's immediate zero wheel velocity is not evidence of real-world stopping distance.
