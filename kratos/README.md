# Kratos backend example — Mini-Waymo Micro V8

This is separate from the standalone browser simulator, and has **not been deployed to Kratos**. It publishes commands to a private MQTT broker. Real firmware does NOT yet consume them; do not connect motors for first tests.

```
pip install -r kratos/requirements.txt
export WAYMO_ADMIN_TOKEN='use-a-long-random-secret'
export WAYMO_MQTT_HOST='127.0.0.1'
export WAYMO_MQTT_USERNAME='your-user'
export WAYMO_MQTT_PASSWORD='your-password'
uvicorn kratos.app:app --host 127.0.0.1 --port 8765
```

- Guest read only: `GET /api/state`, `GET /api/rooms`, `GET /api/survey/meta`, `WS /ws/state`.
- Admin bearer token: `POST /api/survey`, `POST /api/relocalize`, `POST /api/go-now` `{ "room": "230" }`, `POST /api/queue` `{ "room": "251" }`, `POST /api/queue/clear`, `POST /api/hold`, `POST /api/stop`.
- Admin-only endpoints validate room IDs against currently uploaded survey and require localized state before dispatch.
- Go-now publishes `{ "type":"go_now", "room":"230" }`, queues send `queue_stop`, hold sends `hold`.
- Example status is **optimistic**: MQTT publish acceptance does NOT prove the vehicle executed a command; production needs command IDs, acknowledgement, independent watchdog and consistent state after reconnect.
- Device permissions and auth must be secured; don't expose MQTT publicly. A real login UI is not implemented in this sample.
- `example-fictional-survey-v6.json` is a fictional map fixture for testing, not a real floor plan. Do not use it for a physical robot.

V8 exposes `POST /api/pause` and `POST /api/resume` under admin bearer authentication. These publish `{ "type": "pause" }` and `{ "type": "resume" }` respectively; pending stops are preserved. The firmware bench scaffold does **not** act on them, and the server does not yet get ACKs. These are prototype API contracts only.

## V9: automatic marker relocalization / safety

The server's example telemetry handler now accepts a device-published `marker_node` and only confirms a location if the node exists in the uploaded survey and has a recorded signature. With no unique marker, it stays in an unresolved state. A matching depth scan through `/api/relocalize` returns an **estimated candidate** requiring validation; it does not authorize dispatch.

Admin `POST /api/go-now` (`{"room":"263"}`) replaces active/pending stops, while `POST /api/queue` retains the active destination. Both now require a marker-confirmed position and explicit `estop_latched:false` telemetry. `POST /api/emergency-stop` requests remote STOP (mockable through MQTT) and clears the server-side mission, but it is **not a physical stop or proof of acknowledgement**. It also prevents further dispatch until a locally verified reset workflow is implemented; no remote latch-clear endpoint is provided. The firmware bench scaffold currently accepts only a literal STOP payload; the JSON protocol is not yet wired to the board.

The broker should grant the ESP32 telemetry publishing rights and the Kratos backend command-publishing rights; no public guest should receive MQTT credentials. Production work still needs freshness timeouts, authenticated marker origins, command IDs, ACKs, and a verified manual local E-stop reset procedure.
