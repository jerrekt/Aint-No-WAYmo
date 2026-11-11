// Checks the turret's pure logic on a laptop: g++ -std=c++17 -I bench/turret-s3/src bench/turret-s3/tests/test_turret_logic.cpp -o /tmp/t && /tmp/t
#include <cstdio>
#include <cstdlib>
#include "turret_logic.h"

using namespace turret;
static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { std::printf("FAIL line %d: %s\n", __LINE__, #cond); failures++; } } while (0)

static LunaReading R(uint16_t cm, uint16_t amp) { return LunaReading{cm, amp, 2500}; }

int main() {
  // decode: little-endian distance, amp, temperature
  const uint8_t frame[6] = {0x2C, 0x01, 0x20, 0x03, 0xC4, 0x09};   // 300 cm, amp 800, 25.00 C
  LunaReading d = decode(frame);
  CHECK(d.cm == 300 && d.amp == 800 && d.temp_centi == 2500);

  // classify
  CHECK(classify(R(150, 800)) == Quality::Good);
  CHECK(classify(R(150, 99)) == Quality::Weak);
  CHECK(classify(R(150, 0xFFFF)) == Quality::Saturated);
  CHECK(classify(R(12, 900)) == Quality::TooClose);
  CHECK(classify(R(900, 300)) == Quality::Far);

  // stepper wags between the ends and turns back without overshooting
  Stepper s; s.start(90, 65, 115, 5);
  bool turned = false; int a = 0, ends = 0, lo = 999, hi = -1;
  for (int i = 0; i < 60; i++) { a = s.next(&turned); if (turned) ends++; if (a < lo) lo = a; if (a > hi) hi = a; }
  CHECK(lo == 65 && hi == 115);
  CHECK(ends >= 5);
  Stepper big; big.start(0, 10, 170, 3); CHECK(big.angle == 10);   // start is clamped into range

  // pass decisions
  PassSummary p; p.reset();
  CHECK(!passIsClear(p, 32));                                     // no readings: not clear
  p.add(90, R(250, 500), Quality::Good); p.add(95, R(400, 50), Quality::Weak);
  CHECK(passIsClear(p, 32) && p.nearestCm == 250 && p.nearestDeg == 90);
  p.add(100, R(25, 900), Quality::Good);
  CHECK(!passIsClear(p, 32) && p.nearestDeg == 100);              // something at 25 cm: stop
  p.reset(); for (int i = 0; i < 5; i++) p.addMissing();
  CHECK(!passIsClear(p, 32));                                     // sensor not answering: stop
  p.reset(); p.add(90, R(300, 0xFFFF), Quality::Saturated); p.add(95, R(300, 500), Quality::Good);
  CHECK(!passIsClear(p, 32));                                     // overexposed reading: stop
  p.reset(); p.add(90, R(10, 900), Quality::TooClose); p.add(95, R(300, 500), Quality::Good);
  CHECK(!passIsClear(p, 32));                                     // inside the 20 cm blind zone: stop
  p.reset(); p.add(90, R(950, 200), Quality::Far); p.add(95, R(0, 20), Quality::Weak);
  CHECK(passIsClear(p, 32));                                      // empty hallway: clear

  if (failures) { std::printf("%d check(s) failed\n", failures); return 1; }
  std::printf("turret logic: all checks passed\n");
  return 0;
}
