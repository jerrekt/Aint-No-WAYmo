# ESP32-S3 Sense motor-disabled bench scaffold (V10)

This is NOT ready-to-drive firmware. It has the same C++ safety-controller core as the native/WebAssembly demo, but missing real sensor drivers and vehicle actuation. No motor output pins are configured; WAYMO_MOTORS_ENABLED defaults to 0 and must remain disabled until integrated and tested.

- When `WAYMO_ESTOP_SENSE_GPIO=-1`, the normally-closed physical stop sense is treated as open; the latch remains asserted. Only choose a GPIO after actual wiring and pin-budget validation. A physical power-cut switch must interrupt the **motor supply independently**.
- When `WAYMO_BATTERY_ADC_GPIO=-1`, battery voltage is reported as `null`. If a free ADC GPIO is selected with a separately measured equal-value resistor divider (2:1), the skeleton reports nominal 1S LiPo voltage via `analogReadMilliVolts * 2`. Calibrate against a multimeter, under load. Do not connect battery voltage directly to an ADC input. A protected LiPo and correct charger are required.
- MQTT data and the C++ core scaffold are not proof of reliable navigation or authentication. Literal `STOP` is the only accepted inbound command so far.
- ESP32 Wi-Fi credentials and MQTT credentials are placeholders. Never push real secrets to Git.

When PlatformIO is available, build with `pio run -d firmware`. PlatformIO was not installed in the execution environment, so an actual board build could not be verified.
