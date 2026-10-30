#include "controller.h"
#if defined(__wasm__)
extern "C" double sin(double);
extern "C" double cos(double);
extern "C" double atan2(double,double);
extern "C" double fabs(double);
#else
#include <math.h>
#endif
static CoreInput wi;
static CoreOutput wo;
static int arrival_notified = 0;
static double clamp(double v,double lo,double hi){return v<lo?lo:(v>hi?hi:v);}
static void stop(CoreOutput*o,int status,int signals=0){o->left_mps=0;o->right_mps=0;o->status=status;o->turn_signal=signals;}
void core_reset(void){arrival_notified=0;}
void core_step(const CoreInput*i,CoreOutput*o){
  *o=CoreOutput{0,0,4,0,0};
  // Invalid readings, missing sensor updates, or stale control fail closed.
  if (!__builtin_isfinite(i->mqtt_age_s)||!__builtin_isfinite(i->front_distance_m)||!__builtin_isfinite(i->heading_error_rad)||
      !__builtin_isfinite(i->pose_sigma_m)||!__builtin_isfinite(i->person_distance_m)) {stop(o,4,2);return;}
  if(i->estop>0.5){stop(o,9,2);return;}
  if(i->mqtt_age_s>0.80){stop(o,5,2);return;}
  if(i->pose_sigma_m>0.65){stop(o,6,2);return;}
  if(i->front_valid<0.5||i->tof_age_s>0.4||i->imu_age_s>0.35||i->encoder_age_s>0.50||
     i->front_distance_m<0){stop(o,4,2);return;}
  if(i->command_mode==3){
    if(i->marker_confirmed>0.5){stop(o,8);if(!arrival_notified){o->chime_event=1;arrival_notified=1;}}
    else stop(o,6,2);
    return;
  }
  arrival_notified=0;
  if(i->command_mode==0){stop(o,0);return;}
  // Detecting a person is only modeled until real camera inference is implemented.
  if(i->person_confidence>0.62&&i->person_distance_m<1.0){stop(o,2,2);return;}
  if(i->front_distance_m<0.32){stop(o,3,2);return;}
  if(i->command_mode==2){
    // Scanning is possible only on a two-motor differential chassis.
    // 0.052 m/s per wheel implies about 1.73rad/s for a 0.06m wheel track.
    o->left_mps=-0.045;o->right_mps=0.045;o->status=7;return;
  }
  if(i->command_mode!=1){stop(o,0);return;}
  // Differential-drive heading feedback. Bound angular velocity and speed.
  double error=atan2(sin(i->heading_error_rad),cos(i->heading_error_rad));
  double angular=clamp(error*2.2,-1.8,1.8);
  double v=0.16;
  if(fabs(error)>1.05)v=0.0; // rotate on spot when reversing direction
  else if(fabs(error)>0.45)v=0.075;
  if(i->front_distance_m<0.85 || (i->person_confidence>0.62&&i->person_distance_m<1.5))v=0.06;
  // track width 60mm, speed cap +/-0.22m/s
  o->left_mps=clamp(v-angular*0.030,-0.22,0.22);
  o->right_mps=clamp(v+angular*0.030,-0.22,0.22);
  o->status=1;
  o->turn_signal=i->near_turn>0.5?1:(i->near_turn<-0.5?-1:0);
}
CoreInput*core_input(){return &wi;}
CoreOutput*core_output(){return &wo;}
void core_wasm_step(){core_step(&wi,&wo);}
int core_input_count(){return (int)(sizeof(CoreInput)/sizeof(double));}
int core_output_count(){return (int)(sizeof(CoreOutput)/sizeof(double));}
