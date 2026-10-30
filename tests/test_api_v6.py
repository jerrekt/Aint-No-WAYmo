"""Test mission queue API's contract against an injected fake broker.
This does not exercise live MQTT, ESP32 firmware or real authentication UI.
"""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from kratos import app as backend

class FakeMQTT:
    def __init__(self):self.commands=[]
    def is_connected(self):return True
    def publish(self,topic,payload,qos,retain):
        self.commands.append((topic,json.loads(payload)))
        class Info:rc=0
        return Info()

with TemporaryDirectory() as temp:
    p=Path(temp)/'survey.json'
    p.write_text((Path(__file__).resolve().parents[1]/'kratos/example-fictional-survey-v6.json').read_text())
    backend.SURVEY_PATH=p;backend.ADMIN_TOKEN='test-key';broker=FakeMQTT();backend.broker=broker
    backend.state.update({'localization':'marker-confirmed','position':'A','online':True,'mission':[],'active_destination':None,'pending_rooms':[],'estop_latched':False})
    client=TestClient(backend.app)
    assert client.get('/api/rooms').json()['rooms']
    assert client.post('/api/go-now',json={'room':'230'}).status_code==401
    headers={'Authorization':'Bearer test-key'}
    assert client.post('/api/go-now',json={'room':'230'},headers=headers).status_code==200
    assert client.post('/api/queue',json={'room':'251'},headers=headers).status_code==200
    assert client.post('/api/queue',json={'room':'202'},headers=headers).status_code==200
    assert backend.state['mission']==['230','251','202']
    assert client.post('/api/go-now',json={'room':'215'},headers=headers).status_code==200
    assert backend.state['mission']==['215']
    assert client.post('/api/queue',json={'room':'201'},headers=headers).status_code==422
    assert client.post('/api/queue',json={'room':'225'},headers=headers).status_code==200
    assert client.post('/api/queue/clear',headers=headers).json()['pending_rooms']==[]
    assert client.post('/api/hold',headers=headers).status_code==200
    assert backend.state['mission']==[]
    assert [e[1]['type'] for e in broker.commands]==['go_now','queue_stop','queue_stop','go_now','queue_stop','clear_pending','hold']
    print('Kratos API: 9 role/queue/dispatch checks passed (fake broker, example map)')
