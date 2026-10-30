#pragma once
// Shared safety / differential-drive controller. Used unchanged in native tests,
// browser WebAssembly, and ESP32-S3 firmware.
// Units: seconds, meters, radians, meters per second.
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
  double command_mode;          // 0=HOLD 1=DRIVE 2=SCAN 3=ARRIVED
  double heading_error_rad;     // requested heading minus estimated yaw
  double near_turn;             // 0 none, -1 right, 1 left
  double front_distance_m;      // nearest valid obstruction, not merely a person
  double front_valid;
  double person_confidence;     // camera classifier confidence (not in real firmware yet)
  double person_distance_m;
  double side_distance_m;       // wall distance; informational initially
  double pose_sigma_m;
  double mqtt_age_s;
  double imu_age_s;
  double encoder_age_s;
  double tof_age_s;
  double estop;
  double marker_confirmed;
} CoreInput;
typedef struct {
  double left_mps;
  double right_mps;
  double status;                // 0 hold 1 moving 2 person 3 obstacle 4 sensor 5 link 6 pose 7 scan 8 arrived 9 estop
  double turn_signal;          // -1 right, 0 none, 1 left, 2 hazards
  double chime_event;          // 1 once when arrival first confirmed
} CoreOutput;
void core_reset(void);
void core_step(const CoreInput* input, CoreOutput* output);
CoreInput* core_input(void);
CoreOutput* core_output(void);
void core_wasm_step(void);
int core_input_count(void);
int core_output_count(void);
#ifdef __cplusplus
}
#endif
