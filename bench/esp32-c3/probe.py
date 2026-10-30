#!/usr/bin/env python3
"""Kratos-side MQTT command/ack round-trip benchmark.

Requires paho-mqtt>=2,<3. Sends only to an isolated bench topic.
No GPIO or real-car commands are issued.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import statistics
import threading
import time
import uuid
from pathlib import Path

CMD_TOPIC = "waymo/bench-c3/cmd"
ACK_TOPIC = "waymo/bench-c3/ack"
STATUS_TOPIC = "waymo/bench-c3/status"


def percentile(values: list[float], p: float) -> float | None:
    """Percentile via linear interpolation, result in milliseconds."""
    if not values:
        return None
    ordered = sorted(values)
    ix = (len(ordered)-1) * (p/100)
    lo = int(ix)
    hi = min(lo+1, len(ordered)-1)
    return round(ordered[lo] + (ix-lo)*(ordered[hi]-ordered[lo]), 2)


def summary(rows: list[dict]) -> dict:
    rtt = [row["rtt_ms"] for row in rows if row["rtt_ms"] is not None]
    n = len(rows)
    return {
        "sent": n,
        "acknowledged": len(rtt),
        "no_ack": n - len(rtt),
        "ack_rate_pct": round(len(rtt) / n * 100, 1) if n else None,
        "rtt_avg_ms": round(statistics.mean(rtt), 2) if rtt else None,
        "rtt_median_ms": percentile(rtt, 50),
        "rtt_p95_ms": percentile(rtt, 95),
        "rtt_p99_ms": percentile(rtt, 99),
        "rtt_max_ms": round(max(rtt), 2) if rtt else None,
        "rtt_stddev_ms": round(statistics.pstdev(rtt), 2) if len(rtt) > 1 else None,
    }


class Probe:
    def __init__(self, mqtt, host, port, username, password, timeout_s):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                  client_id=f"kratos-bench-{uuid.uuid4().hex[:8]}")
        if username:
            self.client.username_pw_set(username, password)
        self.host, self.port = host, port
        self.timeout_s = timeout_s
        self.connected = threading.Event()
        self.subscribed = threading.Event()
        self.waiting = threading.Event()
        self.lock = threading.Lock()
        self.acks = {}
        self.status = None
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if not reason_code.is_failure:
            self.connected.set()
            client.subscribe([(ACK_TOPIC, 1), (STATUS_TOPIC, 0)])
        else:
            print(f"MQTT rejected connection: {reason_code}")

    def on_subscribe(self, client, userdata, mid, reason_codes, properties):
        if reason_codes and all(not code.is_failure for code in reason_codes):
            self.subscribed.set()
        else:
            print("Subscription rejected; check MQTT ACLs")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected.clear()
        self.subscribed.clear()

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
            if not isinstance(data, dict):
                return
        except (ValueError, UnicodeError):
            return
        if msg.topic == STATUS_TOPIC:
            self.status = data
            return
        if msg.topic == ACK_TOPIC:
            with self.lock:
                self.acks[str(data.get('id',''))] = (time.perf_counter(), data)
            self.waiting.set()

    def start(self):
        self.client.connect(self.host, self.port, keepalive=30)
        self.client.loop_start()
        if not self.subscribed.wait(timeout=10):
            self.close()
            raise RuntimeError("No MQTT subscription; check host, credentials, network and ACL")

    def send(self, packet: dict) -> dict:
        msg_id = str(packet['id'])
        row = {"id": msg_id, "type": packet['type'], "room": packet.get('room', ''),
               "rtt_ms": None, "esp_processing_ms": None, "rssi_dbm": None,
               "accepted": False, "state": None, "reason": "timeout"}
        self.waiting.clear()
        with self.lock:
            self.acks.pop(msg_id, None)
        sent_at = time.perf_counter()
        result = self.client.publish(CMD_TOPIC, json.dumps(packet, separators=(',',':')), qos=1, retain=False)
        if result.rc != 0:
            row['reason'] = f'publish_rc_{result.rc}'
            return row
        deadline = sent_at + self.timeout_s
        while time.perf_counter() < deadline:
            self.waiting.wait(min(0.1, max(0.0, deadline - time.perf_counter())))
            self.waiting.clear()
            with self.lock:
                response = self.acks.pop(msg_id, None)
            if response:
                arrived_at, ack = response
                row.update(rtt_ms=round((arrived_at - sent_at)*1000, 2),
                           esp_processing_ms=ack.get('esp_processing_ms'),
                           rssi_dbm=ack.get('rssi_dbm'),
                           accepted=ack.get('accepted',False),
                           state=ack.get('state'),
                           reason=ack.get('reason'))
                return row
        return row

    def close(self):
        self.client.disconnect()
        self.client.loop_stop()


def main():
    parser = argparse.ArgumentParser(description="Mini-Waymo receive-only C3 MQTT RTT test")
    parser.add_argument('--host', default=os.getenv('WAYMO_MQTT_HOST','127.0.0.1'))
    parser.add_argument('--port', type=int, default=int(os.getenv('WAYMO_MQTT_PORT','1883')))
    parser.add_argument('--count', type=int, default=50, help='Number of pings (default: 50)')
    parser.add_argument('--interval-ms', type=float, default=100.0)
    parser.add_argument('--timeout-ms', type=float, default=1500.0)
    parser.add_argument('--demo', action='store_true', help='Also send Go 263, queue, pause, resume, stop and recovery')
    parser.add_argument('--output', default='bench_results.csv')
    args = parser.parse_args()
    if args.count < 1 or args.count > 10000:
        parser.error('count must be from 1 to 10000')

    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise SystemExit('Install dependencies: python -m pip install -r requirements.txt') from exc

    runner = Probe(mqtt, args.host, args.port,
                   os.getenv('WAYMO_MQTT_USER',''), os.getenv('WAYMO_MQTT_PASS',''),
                   args.timeout_ms / 1000)
    run_id = uuid.uuid4().hex[:8]
    rows=[]
    try:
        runner.start()
        print('Subscribed for C3 acks; waiting for the device to be online...')
        time.sleep(0.3)
        if runner.status is not None:
            print(f'Device status: {runner.status}')
        for i in range(args.count):
            row=runner.send({'id': f'{run_id}-p{i:04d}', 'type':'ping'})
            rows.append(row)
            print(f'{i+1:>3}/{args.count}: {row["rtt_ms"] if row["rtt_ms"] is not None else "TIMEOUT"} ms')
            if i < args.count-1: time.sleep(args.interval_ms/1000)
        if args.demo:
            commands=[{'type':'go_now','room':'263'}, {'type':'queue_stop','room':'251'},
                      {'type':'pause'}, {'type':'resume'}, {'type':'stop'},
                      {'type':'request_marker_observation'}]
            for i,cmd in enumerate(commands):
                cmd['id']=f'{run_id}-d{i:04d}'
                row=runner.send(cmd)
                rows.append(row)
                print(f'{cmd["type"]:<27} rtt={row["rtt_ms"]}ms state={row["state"]} result={row["reason"]}')
                time.sleep(0.15)
    finally:
        runner.close()

    totals=summary(rows)
    print('\nEND-TO-END RTT = Kratos probe -> MQTT broker -> C3 -> broker -> Kratos probe')
    print(json.dumps(totals, indent=2))
    output=Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', newline='', encoding='utf-8') as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    output.with_suffix('.summary.json').write_text(json.dumps(totals, indent=2) + '\n')
    print('CSV:', output.resolve())
    print('Summary:', output.with_suffix('.summary.json').resolve())

if __name__ == '__main__':
    main()
