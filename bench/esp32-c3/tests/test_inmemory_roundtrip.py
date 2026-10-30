"""Tests benchmark plumbing without claiming a real network/device measurement."""
import sys
import json
import types
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from probe import Probe, CMD_TOPIC, ACK_TOPIC

class FakeReason:
    is_failure = False

class FakeClient:
    def __init__(self, *args, **kwargs):
        self.on_connect = self.on_subscribe = self.on_message = self.on_disconnect = None
        self.suppress_ack = False
    def username_pw_set(self, user, password):
        self.user = user
    def connect(self, host, port, keepalive):
        self.host = host
    def loop_start(self):
        self.on_connect(self,None,None,FakeReason(),None)
    def subscribe(self, topics):
        self.on_subscribe(self,None,1,[FakeReason(),FakeReason()],None)
    def publish(self, topic, body, qos=0, retain=False):
        assert topic == CMD_TOPIC and qos == 1 and retain is False
        if not self.suppress_ack:
            payload=json.loads(body)
            ack={"id":payload['id'],"accepted":True,"reason":"simulated_only", "type":payload['type'],
                 "state":"IDLE","rssi_dbm":-62,"esp_processing_ms":1}
            self.on_message(self,None,types.SimpleNamespace(topic=ACK_TOPIC,payload=json.dumps(ack).encode()))
        return types.SimpleNamespace(rc=0)
    def disconnect(self): pass
    def loop_stop(self): pass

class MqttFake:
    CallbackAPIVersion=types.SimpleNamespace(VERSION2=2)
    Client=FakeClient

class RoundTripTests(unittest.TestCase):
    def test_echo_and_timeout(self):
        runner=Probe(MqttFake, 'localhost',1883,'test','test',0.02)
        runner.start()
        try:
            sample=runner.send({'id':'run-1','type':'go_now','room':'263'})
            self.assertEqual(sample['room'],'263')
            self.assertIsNotNone(sample['rtt_ms'])
            self.assertTrue(sample['accepted'])
            self.assertEqual(sample['reason'],'simulated_only')
            runner.client.suppress_ack=True
            timedout=runner.send({'id':'run-2','type':'ping'})
            self.assertIsNone(timedout['rtt_ms'])
            self.assertEqual(timedout['reason'],'timeout')
        finally:
            runner.close()

if __name__=='__main__': unittest.main()
