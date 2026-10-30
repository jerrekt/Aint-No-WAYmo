/* Mini-Waymo ESP32-S3 Sense BENCH SCAFFOLD
 * This is not a fully wired car. Motors are intentionally DISABLED.
 * Core motor/safety math is identical to the native and browser simulation.
 * Connect actual VL53L7CX, IMU, wheel encoders and validated motor driver
 * before setting WAYMO_MOTORS_ENABLED=1 or connecting a powered motor.
 */
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "controller.h"

#ifndef WAYMO_MOTORS_ENABLED
#define WAYMO_MOTORS_ENABLED 0
#endif
static constexpr const char *WIFI_SSID = "REPLACE_WIFI_SSID";
static constexpr const char *WIFI_PASS = "REPLACE_WIFI_PASSWORD";
static constexpr const char *MQTT_SERVER = "REPLACE_KRATOS_HOST";
static constexpr const char *MQTT_USER = "REPLACE_MQTT_USERNAME";
static constexpr const char *MQTT_PASS = "REPLACE_MQTT_PASSWORD";
WiFiClient client;
PubSubClient mqtt(client);
uint32_t lastFrame=0,lastPing=0,lastTelemetry=0;
uint32_t lastValidToF=0,lastValidIMU=0,lastValidEncoder=0;
// Optional: connect a measured 1:1 resistor voltage divider to a FREE ADC pin.
// Negative default disables sensing. Choose GPIO after final pin-budget review;
// do NOT connect raw battery voltage directly to an ESP32 ADC.
#ifndef WAYMO_BATTERY_ADC_GPIO
#define WAYMO_BATTERY_ADC_GPIO -1
#endif
float measuredBatteryV = -1.0f;
void readBatteryVoltage(){
#if WAYMO_BATTERY_ADC_GPIO >= 0
  // This is an uncalibrated bench reading of 1S LiPo via 2:1 divider.
  measuredBatteryV=analogReadMilliVolts(WAYMO_BATTERY_ADC_GPIO)*2.0f/1000.0f;
#else
  measuredBatteryV=-1.0f;
#endif
}

// Connect ONLY to the sense pole of a *dual-pole normally-closed* physical
// E-stop; the OTHER pole must interrupt battery-to-motor-driver VM directly.
// Leave -1 for unconfigured/unsafe: firmware refuses to arm.
#ifndef WAYMO_ESTOP_SENSE_GPIO
#define WAYMO_ESTOP_SENSE_GPIO -1
#endif
bool estop = true; // latched on boot; motor outputs remain permanently disabled
bool estopSwitchOpen = true;
void readHardwareEstop() {
#if WAYMO_ESTOP_SENSE_GPIO >= 0
  // NC switch to GND: LOW=closed/safe, HIGH=open/pressed or broken wire.
  estopSwitchOpen = digitalRead(WAYMO_ESTOP_SENSE_GPIO) != LOW;
#else
  estopSwitchOpen = true;
#endif
  if (estopSwitchOpen) estop = true; // latch; NEVER remotely clear
}

void callback(char *topic, byte *payload, unsigned int len) {
  // Only STOP is accepted until verified sensor drivers and route control
  // are implemented. Never trust a remote command to bypass safety.
  if (len==4 && memcmp(payload,"STOP",4)==0) estop=true;
}
void publishTelemetry(const CoreOutput &out){
  if(!mqtt.connected())return;
  char msg[224];
  char batteryField[40];
  if(measuredBatteryV>=2.5f && measuredBatteryV<=4.3f)
    snprintf(batteryField,sizeof(batteryField),"%.3f",measuredBatteryV);
  else
    snprintf(batteryField,sizeof(batteryField),"null");
  snprintf(msg,sizeof(msg),"{\"status\":\"BENCH_ONLY\",\"controller_state\":%d,\"motor_enabled\":false,\"estop_latched\":%s,\"estop_switch_open\":%s,\"localization\":\"unknown\",\"battery_v\":%s}",out.status,estop?"true":"false",estopSwitchOpen?"true":"false",batteryField);
  mqtt.publish("waymo/micro-01/telemetry",msg,false);
}
void setup(){
  Serial.begin(115200);
  core_reset();
#if WAYMO_ESTOP_SENSE_GPIO >= 0
  pinMode(WAYMO_ESTOP_SENSE_GPIO, INPUT_PULLUP);
#endif
  readHardwareEstop();
#if WAYMO_BATTERY_ADC_GPIO >= 0
  pinMode(WAYMO_BATTERY_ADC_GPIO,INPUT);
  analogReadResolution(12);
#endif
  WiFi.mode(WIFI_STA);WiFi.begin(WIFI_SSID,WIFI_PASS);
  mqtt.setServer(MQTT_SERVER,1883);
  mqtt.setCallback(callback);
  Serial.println("BENCH MODE: motors disabled; not autonomous navigation firmware");
}
void loop(){
  const uint32_t now=millis();
  readHardwareEstop(); // sensor update independent of MQTT callback
  if(now%500 < 30)readBatteryVoltage();
  if(WiFi.status()==WL_CONNECTED){
    if(!mqtt.connected() && now-lastPing>5000){lastPing=now;String id="waymo-s3-"+String((uint32_t)ESP.getEfuseMac(),HEX);
      if(mqtt.connect(id.c_str(),MQTT_USER,MQTT_PASS))mqtt.subscribe("waymo/micro-01/cmd");}
    mqtt.loop();
  }
  if(now-lastFrame>=50){
    lastFrame=now;
    CoreInput in{};
    in.command_mode=0;
    in.estop=estop?1:0;
    in.mqtt_age_s=mqtt.connected()?0:10;
    in.pose_sigma_m=2.0; // no proven localization
    in.front_valid=0;     // no real ToF driver is connected
    in.front_distance_m=0;
    in.person_distance_m=9;
    in.tof_age_s=10;in.imu_age_s=10;in.encoder_age_s=10;
    CoreOutput out{};
    core_step(&in,&out);
    // Deliberately no motor pins: do not arm unvalidated motor control.
    if(now-lastTelemetry>=500){lastTelemetry=now;publishTelemetry(out);}
  }
}
