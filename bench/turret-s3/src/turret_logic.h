// Pure logic for the roof turret bench test: TF-Luna frame decoding, reading quality, the servo's
// back-and-forth stepping, and the per-pass summary. No Arduino calls, so tests/test_turret_logic.cpp
// builds it with plain g++.
#pragma once
#include <stdint.h>

namespace turret {

// TF-Luna I2C registers 0x00..0x05, little-endian: distance (cm), signal strength (amp), chip temp (0.01 C).
struct LunaReading {
  uint16_t cm;
  uint16_t amp;
  int16_t temp_centi;
};

inline LunaReading decode(const uint8_t b[6]) {
  LunaReading r;
  r.cm = (uint16_t)(b[0] | (b[1] << 8));
  r.amp = (uint16_t)(b[2] | (b[3] << 8));
  r.temp_centi = (int16_t)(b[4] | (b[5] << 8));
  return r;
}

enum class Quality { Good, Weak, Saturated, TooClose, Far, NoData };

inline const char* qualityName(Quality q) {
  switch (q) {
    case Quality::Good: return "good";
    case Quality::Weak: return "weak";
    case Quality::Saturated: return "saturated";
    case Quality::TooClose: return "too_close";
    case Quality::Far: return "far";
    default: return "no_data";
  }
}

// TF-Luna manual: a signal strength under 100 is unreliable, 0xFFFF means overexposed, and the range
// is 0.2 to 8 m. Weak usually means nothing in range (an open hallway); saturated usually means very close.
const uint16_t AMP_MIN = 100;
const uint16_t AMP_SATURATED = 0xFFFF;
const uint16_t CM_MIN = 20;
const uint16_t CM_MAX = 800;

inline Quality classify(const LunaReading& r) {
  if (r.amp == AMP_SATURATED) return Quality::Saturated;
  if (r.amp < AMP_MIN) return Quality::Weak;
  if (r.cm < CM_MIN) return Quality::TooClose;
  if (r.cm > CM_MAX) return Quality::Far;
  return Quality::Good;
}

// Moves between lo and hi in fixed steps, turning back at each end (no slip ring, so it never spins).
struct Stepper {
  int lo, hi, step, angle, dir;
  void start(int from, int low, int high, int stepDeg) {
    lo = low; hi = high; step = stepDeg > 0 ? stepDeg : 1;
    angle = from < lo ? lo : (from > hi ? hi : from);
    dir = 1;
  }
  // Returns the next angle; flips direction at an end. *turned is set when this step reached an end.
  int next(bool* turned) {
    int a = angle + dir * step;
    bool end = false;
    if (a >= hi) { a = hi; end = true; }
    if (a <= lo) { a = lo; end = true; }
    if (end) dir = -dir;
    angle = a;
    if (turned) *turned = end;
    return a;
  }
};

// One pass of readings (one wag from end to end, or one full sweep).
struct PassSummary {
  int readings, good, weak, saturated, tooClose, far, noData;
  uint16_t nearestCm;
  int nearestDeg;
  void reset() {
    readings = good = weak = saturated = tooClose = far = noData = 0;
    nearestCm = 0xFFFF; nearestDeg = -1;
  }
  void add(int deg, const LunaReading& r, Quality q) {
    readings++;
    switch (q) {
      case Quality::Good:
        good++;
        if (r.cm < nearestCm) { nearestCm = r.cm; nearestDeg = deg; }
        break;
      case Quality::Weak: weak++; break;
      case Quality::Saturated: saturated++; break;
      case Quality::TooClose: tooClose++; break;
      case Quality::Far: far++; break;
      default: noData++; break;
    }
  }
  void addMissing() { readings++; noData++; }
};

// Bench-only obstacle call for one pass. It fails closed: something nearer than stopCm, an overexposed
// or too-close (blind zone, under 20 cm) reading, or a pass with no usable readings at all (sensor unplugged, wrong mode, blocked
// lens) all count as "not clear". Weak or far readings alone are fine: the hallway ahead is just empty.
inline bool passIsClear(const PassSummary& s, uint16_t stopCm) {
  if (s.readings == 0) return false;
  if (s.noData == s.readings) return false;
  if (s.good == 0 && s.weak == 0 && s.far == 0) return false;
  if (s.saturated > 0 || s.tooClose > 0) return false;
  if (s.good > 0 && s.nearestCm < stopCm) return false;
  return true;
}

}  // namespace turret
