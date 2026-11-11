// Roof turret bench test for the XIAO ESP32-S3 Sense: sweeps the 2 g turret servo and reads the TF-Luna
// over I2C. Bench only: no drive motor, no steering, no Wi-Fi. Output is one JSON object per line on USB
// serial (115200), ready for a live viewer page later.
//
// Pins (from handoff/handoffs/SUBIR_HANDOFF.md):
//   D8  (GPIO7) turret servo signal       V+ from the motor rail, GND common
//   D4  (GPIO5) I2C SDA                   TF-Luna 0x10, gyro 0x68, VL53L7CX 0x29 share the bus
//   D5  (GPIO6) I2C SCL
// TF-Luna pin 5 (CFG) must be tied to GND or it stays in serial (UART) mode and never answers on I2C.
//
// Serial commands (type a word, press Enter):
//   wag        wag +-25 degrees around center, as while driving; prints a pass summary at each end
//   sweep      one full sweep from end to end, as at a stop; then back to center
//   center     move to center and hold
//   angle N    move to N degrees and hold (limited to SERVO_MIN_DEG..SERVO_MAX_DEG)
//   read       one TF-Luna reading where the turret points now
//   quiet      toggle the per-reading lines (pass summaries still print)
//   i2c        list the I2C addresses that answer
//   off        stop and let the servo go limp
//   help       this list
#include <Arduino.h>
#include <Wire.h>
#include <ESP32Servo.h>
#include "turret_logic.h"

using namespace turret;

// ---- wiring and calibration: change these after the turret is built ----
const int PIN_SERVO = 7;        // D8
const int PIN_SDA = 5;          // D4
const int PIN_SCL = 6;          // D5
const uint8_t LUNA_ADDR = 0x10;
const uint32_t I2C_HZ = 400000;

const int SERVO_MIN_US = 500;   // FFTY 2 g 180-degree servo; adjust if it buzzes at the ends
const int SERVO_MAX_US = 2500;
const int SERVO_CENTER_DEG = 90;   // straight ahead once the horn is fitted; trim this after assembly
const int SERVO_MIN_DEG = 10;      // keep off the end stops and away from the wires
const int SERVO_MAX_DEG = 170;

const int WAG_HALF_DEG = 25;    // +-25 degrees while driving (handoff)
const int WAG_STEP_DEG = 5;
const int SWEEP_STEP_DEG = 3;
const int SETTLE_MS_BASE = 15;  // the servo moves about 60 degrees in 0.07 s; wait a little longer per degree
const int SETTLE_MS_PER_DEG = 3;
const uint16_t STOP_CM = 32;    // same stop distance as the simulator's safety core

// ---- state ----
enum class Mode { Off, Hold, Wag, Sweep };
Servo servo;
Mode mode = Mode::Off;
Stepper stepper;
PassSummary pass;
int angleNow = SERVO_CENTER_DEG;
uint32_t nextAt = 0;
bool quiet = false;
bool sweepStarted = false;
String line;

const char* modeName(Mode m) {
  switch (m) {
    case Mode::Hold: return "hold";
    case Mode::Wag: return "wag";
    case Mode::Sweep: return "sweep";
    default: return "off";
  }
}

int clampDeg(int d) { return d < SERVO_MIN_DEG ? SERVO_MIN_DEG : (d > SERVO_MAX_DEG ? SERVO_MAX_DEG : d); }

int settleMs(int fromDeg, int toDeg) { return SETTLE_MS_BASE + SETTLE_MS_PER_DEG * abs(toDeg - fromDeg); }

void moveTo(int deg) {
  deg = clampDeg(deg);
  if (!servo.attached()) servo.attach(PIN_SERVO, SERVO_MIN_US, SERVO_MAX_US);
  nextAt = millis() + settleMs(angleNow, deg);
  servo.write(deg);
  angleNow = deg;
}

// Reads registers 0x00..0x05. Returns false if the TF-Luna does not answer.
bool readLuna(LunaReading* out) {
  Wire.beginTransmission(LUNA_ADDR);
  Wire.write((uint8_t)0x00);
  if (Wire.endTransmission() != 0) return false;
  if (Wire.requestFrom((int)LUNA_ADDR, 6) != 6) return false;
  uint8_t b[6];
  for (int i = 0; i < 6; i++) b[i] = Wire.read();
  *out = decode(b);
  return true;
}

void printReading(int deg, bool ok, const LunaReading& r, Quality q) {
  if (quiet) return;
  if (!ok) {
    Serial.printf("{\"t\":%lu,\"mode\":\"%s\",\"deg\":%d,\"q\":\"no_data\"}\n", (unsigned long)millis(), modeName(mode), deg);
    return;
  }
  Serial.printf("{\"t\":%lu,\"mode\":\"%s\",\"deg\":%d,\"cm\":%u,\"amp\":%u,\"temp_c\":%.1f,\"q\":\"%s\"}\n",
                (unsigned long)millis(), modeName(mode), deg, r.cm, r.amp, r.temp_centi / 100.0, qualityName(q));
}

void printPass(const char* kind) {
  Serial.printf("{\"t\":%lu,\"pass\":\"%s\",\"readings\":%d,\"good\":%d,\"weak\":%d,\"saturated\":%d,\"too_close\":%d,"
                "\"far\":%d,\"no_data\":%d,\"nearest_cm\":%d,\"nearest_deg\":%d,\"clear\":%s}\n",
                (unsigned long)millis(), kind, pass.readings, pass.good, pass.weak, pass.saturated, pass.tooClose,
                pass.far, pass.noData, pass.good ? (int)pass.nearestCm : -1, pass.nearestDeg,
                passIsClear(pass, STOP_CM) ? "true" : "false");
  pass.reset();
}

// One reading at the current angle, counted into the pass.
void sample() {
  LunaReading r = {0, 0, 0};
  bool ok = readLuna(&r);
  Quality q = ok ? classify(r) : Quality::NoData;
  if (ok) pass.add(angleNow, r, q); else pass.addMissing();
  printReading(angleNow, ok, r, q);
}

void scanI2C() {
  Serial.print("{\"i2c\":[");
  bool first = true;
  for (uint8_t a = 1; a < 127; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      Serial.printf("%s\"0x%02X\"", first ? "" : ",", a);
      first = false;
    }
  }
  Serial.println("],\"expect\":{\"tf_luna\":\"0x10\",\"gyro\":\"0x68\",\"vl53l7cx\":\"0x29\"}}");
}

void help() {
  Serial.println("{\"help\":\"wag | sweep | center | angle N | read | quiet | i2c | off | help\"}");
}

void startWag() {
  int lo = clampDeg(SERVO_CENTER_DEG - WAG_HALF_DEG), hi = clampDeg(SERVO_CENTER_DEG + WAG_HALF_DEG);
  stepper.start(angleNow, lo, hi, WAG_STEP_DEG);
  pass.reset();
  mode = Mode::Wag;
  moveTo(stepper.angle);
}

void startSweep() {
  stepper.start(SERVO_MIN_DEG, SERVO_MIN_DEG, SERVO_MAX_DEG, SWEEP_STEP_DEG);
  pass.reset();
  sweepStarted = false;
  mode = Mode::Sweep;
  moveTo(SERVO_MIN_DEG);
}

void handle(String cmd) {
  cmd.trim();
  cmd.toLowerCase();
  if (cmd == "wag") startWag();
  else if (cmd == "sweep") startSweep();
  else if (cmd == "center") { mode = Mode::Hold; moveTo(SERVO_CENTER_DEG); }
  else if (cmd.startsWith("angle ")) { mode = Mode::Hold; moveTo(cmd.substring(6).toInt()); }
  else if (cmd == "read") { pass.reset(); sample(); }
  else if (cmd == "quiet") { quiet = !quiet; Serial.printf("{\"quiet\":%s}\n", quiet ? "true" : "false"); }
  else if (cmd == "i2c") scanI2C();
  else if (cmd == "off") { mode = Mode::Off; servo.detach(); }
  else if (cmd == "help" || cmd.length() == 0) help();
  else Serial.printf("{\"error\":\"unknown command: %s\"}\n", cmd.c_str());
  if (cmd != "quiet" && cmd != "i2c" && cmd != "help" && cmd != "read")
    Serial.printf("{\"mode\":\"%s\",\"deg\":%d}\n", modeName(mode), angleNow);
}

void setup() {
  Serial.begin(115200);
  uint32_t waitUntil = millis() + 3000;
  while (!Serial && millis() < waitUntil) delay(10);   // USB serial: give the monitor a moment to attach
  Wire.begin(PIN_SDA, PIN_SCL, I2C_HZ);
  ESP32PWM::allocateTimer(0);
  servo.setPeriodHertz(50);
  Serial.println("{\"boot\":\"turret bench\",\"servo_pin\":\"D8\",\"i2c\":\"D4 SDA, D5 SCL\"}");
  scanI2C();
  LunaReading r;
  if (!readLuna(&r))
    Serial.println("{\"warn\":\"TF-Luna not answering at 0x10. Check VCC (3.7 to 5.2 V), GND, SDA/SCL, and that pin 5 is tied to GND.\"}");
  help();
  moveTo(SERVO_CENTER_DEG);
  mode = Mode::Hold;
}

void loop() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') { if (line.length()) handle(line); line = ""; }
    else if (line.length() < 40) line += c;
  }
  if ((int32_t)(millis() - nextAt) < 0) return;   // servo still moving

  if (mode == Mode::Wag) {
    sample();
    bool turned = false;
    int to = stepper.next(&turned);
    if (turned) printPass("wag");
    moveTo(to);
  } else if (mode == Mode::Sweep) {
    sample();
    if (sweepStarted && angleNow >= SERVO_MAX_DEG) {   // reached the far end: report and come back to center
      printPass("sweep");
      mode = Mode::Hold;
      moveTo(SERVO_CENTER_DEG);
      return;
    }
    sweepStarted = true;
    moveTo(stepper.next(nullptr));
  }
}
