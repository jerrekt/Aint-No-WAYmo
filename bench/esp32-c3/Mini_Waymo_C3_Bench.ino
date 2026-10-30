/* Mini-Waymo Micro / ESP32-C3 BENCH-ONLY MQTT receiver.
 * No motor pins, GPIO outputs, sensor inputs, camera or sound are used.
 * Commands are simulated in RAM and acknowledged back to Kratos.
 * Names/types mirror the Kratos V12 mission API, but use separate bench topics.
 */
#define WAYMO_BENCH_ONLY 1
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
// Replace values below with your LOCAL TEST network and broker credentials.
// Do not share the resulting sketch once configured.
#define WIFI_SSID "YOUR_2_4_GHZ_WIFI"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define MQTT_HOST "YOUR_PRIVATE_MQTT_HOST"
#define MQTT_PORT 1883
#define MQTT_USER "waymo_bench_c3"
#define MQTT_PASSWORD "YOUR_MQTT_PASSWORD"

#ifndef WAYMO_BENCH_ONLY
#error "This firmware must only compile as a no-output bench receiver"
#endif

static constexpr char CMD_TOPIC[] = "waymo/bench-c3/cmd";
static constexpr char ACK_TOPIC[] = "waymo/bench-c3/ack";
static constexpr char STATUS_TOPIC[] = "waymo/bench-c3/status";
static constexpr uint32_t WIFI_RETRY_MS = 5000;
static constexpr uint32_t MQTT_RETRY_MS = 3000;
static constexpr uint32_t TELEMETRY_MS = 2000;
static constexpr size_t MAX_PACKET_BYTES = 768;

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
uint32_t lastWifiAttempt = 0, lastMqttAttempt = 0, lastStatus = 0;
uint32_t bootMs = 0;
uint32_t rxCount = 0;
char simState[20] = "IDLE";
char activeRoom[12] = "";
char pendingRoom[12] = ""; // One-stop preview only; not a real mission planner

void statusPublish() {
  if (!mqtt.connected()) return;
  StaticJsonDocument<288> doc;
  doc["mode"] = "BENCH_ONLY";
  doc["state"] = simState;
  doc["room"] = activeRoom;
  doc["pending_room"] = pendingRoom;
  doc["received_count"] = rxCount;
  doc["uptime_ms"] = millis() - bootMs;
  doc["rssi_dbm"] = WiFi.RSSI();
  doc["motor_output_enabled"] = false;
  char out[288];
  const size_t n = serializeJson(doc, out, sizeof(out));
  mqtt.publish(STATUS_TOPIC, (const uint8_t*)out, n, false);
}

void onCommand(char* topic, byte* payload, unsigned int length) {
  if (strcmp(topic, CMD_TOPIC) != 0) return;
  const uint32_t receivedAt = millis();
  rxCount++;
  // Reject oversized packets without attempting partial JSON parsing.
  if (length > 440) { Serial.println("Rejected oversized command"); return; }

  StaticJsonDocument<512> cmd;
  const auto error = deserializeJson(cmd, payload, length);
  if (error || !cmd.is<JsonObject>()) {
    Serial.println("Rejected malformed command JSON");
    return;
  }
  const char* id = cmd["id"] | "";
  const char* type = cmd["type"] | "";
  const char* room = cmd["room"] | "";
  bool accepted = false;
  const char* reason = "unsupported_command";

  if (strcmp(type, "ping") == 0) {
    accepted = true; reason = "ok";
  } else if (strcmp(type, "go_now") == 0 && room[0]) {
    strlcpy(activeRoom, room, sizeof(activeRoom));
    pendingRoom[0] = 0;
    strlcpy(simState, "MOVING_SIM", sizeof(simState));
    accepted = true; reason = "simulated_only";
  } else if (strcmp(type, "queue_stop") == 0 && room[0]) {
    strlcpy(pendingRoom, room, sizeof(pendingRoom));
    accepted = true; reason = "simulated_only";
  } else if (strcmp(type, "mission") == 0 && cmd["rooms"].is<JsonArray>() && cmd["rooms"].size() > 0) {
    strlcpy(activeRoom, cmd["rooms"][0] | "", sizeof(activeRoom));
    strlcpy(pendingRoom, cmd["rooms"][1] | "", sizeof(pendingRoom));
    strlcpy(simState, "MOVING_SIM", sizeof(simState));
    accepted = true; reason = "simulated_only";
  } else if (strcmp(type, "pause") == 0) {
    strlcpy(simState, "PAUSED", sizeof(simState));
    accepted = true; reason = "simulated_only";
  } else if (strcmp(type, "resume") == 0) {
    if (strcmp(simState, "PAUSED") == 0) {
      strlcpy(simState, activeRoom[0] ? "MOVING_SIM" : "IDLE", sizeof(simState));
      accepted = true; reason = "simulated_only";
    } else reason = "not_paused";
  } else if (strcmp(type, "stop") == 0 || strcmp(type, "hold") == 0) {
    strlcpy(simState, "STOPPED", sizeof(simState));
    accepted = true; reason = "simulated_only";
  } else if (strcmp(type, "clear_pending") == 0) {
    pendingRoom[0] = 0;
    accepted = true; reason = "simulated_only";
  } else if (strcmp(type, "request_marker_observation") == 0) {
    strlcpy(simState, "RECOVER_SIM", sizeof(simState));
    accepted = true; reason = "no_camera_or_marker_attached";
  } else if (strcmp(type, "go_now") == 0 || strcmp(type, "queue_stop") == 0) {
    reason = "room_required";
  }

  StaticJsonDocument<384> ack;
  ack["id"] = id;
  ack["type"] = type;
  ack["accepted"] = accepted;
  ack["reason"] = reason;
  ack["state"] = simState;
  ack["room"] = activeRoom;
  ack["motor_output_enabled"] = false;
  ack["rx_count"] = rxCount;
  ack["rssi_dbm"] = WiFi.RSSI();
  ack["esp_processing_ms"] = millis() - receivedAt;
  ack["uptime_ms"] = millis() - bootMs;
  char out[400];
  const size_t n = serializeJson(ack, out, sizeof(out));
  const bool queued = mqtt.publish(ACK_TOPIC, (const uint8_t*)out, n, false);
  Serial.printf("RX id=%s type=%s room=%s => %s state=%s (ack queued=%s)\n",
                id, type, room, reason, simState, queued ? "yes" : "no");
}

void connectMqtt() {
  if (WiFi.status() != WL_CONNECTED || mqtt.connected()) return;
  const uint32_t now = millis();
  if (now - lastMqttAttempt < MQTT_RETRY_MS) return;
  lastMqttAttempt = now;
  String clientId = "waymo-c3-bench-" + String((uint32_t)ESP.getEfuseMac(), HEX);
  const bool ok = mqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD);
  if (ok) {
    const bool sub = mqtt.subscribe(CMD_TOPIC, 1);
    Serial.printf("MQTT connected; subscribed=%s; topic=%s\n",sub?"yes":"no",CMD_TOPIC);
    statusPublish();
  } else {
    Serial.printf("MQTT connect failed rc=%d\n", mqtt.state());
  }
}

void setup() {
  Serial.begin(115200);
  delay(400);
  bootMs = millis();
  Serial.println("Mini-Waymo C3 MQTT BENCH TEST: NO GPIO OUTPUTS");
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false); // minimize latency while USB-powered
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  lastWifiAttempt = millis();
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onCommand);
  mqtt.setBufferSize(MAX_PACKET_BYTES);
  mqtt.setKeepAlive(20);
}

void loop() {
  const uint32_t now = millis();
  if (WiFi.status() != WL_CONNECTED) {
    if (now - lastWifiAttempt > WIFI_RETRY_MS) {
      lastWifiAttempt = now;
      WiFi.disconnect();
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
      Serial.println("Wi-Fi reconnecting...");
    }
    delay(5);
    return;
  }
  connectMqtt();
  if (mqtt.connected()) {
    mqtt.loop();
    if (now - lastStatus >= TELEMETRY_MS) {
      lastStatus = now;
      statusPublish();
    }
  }
  delay(2);
}
