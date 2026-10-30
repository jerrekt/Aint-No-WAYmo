"""Prototype Kratos API tests; no hardware connected."""
import json,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from kratos import app as backend
class FakeMQTT:
 def __init__(self):self.commands=[]
 def is_connected(self):return True
 def publish(self,t,p,qos,retain):
  self.commands.append(json.loads(p));return type('Out',(),{'rc':0})()
with TemporaryDirectory() as temp:
 path=Path(temp)/'survey.json'
 path.write_text((Path(__file__).resolve().parents[1]/'kratos/example-fictional-survey-v6.json').read_text())
 backend.SURVEY_PATH=path;backend.ADMIN_TOKEN='test-key';backend.broker=FakeMQTT()
 backend.state.update({'online':True,'localization':'unknown','position':None,'estop_latched':None,'active_destination':None,'pending_rooms':[],'mission':[],'pause_requested':False})
 client=TestClient(backend.app);headers={'Authorization':'Bearer test-key'}
 assert client.post('/api/go-now',json={'room':'263'},headers=headers).status_code==409
 backend.update_telemetry({'estop_latched':False,'marker_node':'I'})
 assert backend.state['localization']=='marker-confirmed'
 assert backend.state['position']=='I'
 assert backend.state['recovery_state']=='localized without rotation'
 assert client.post('/api/go-now',json={'room':'263'},headers=headers).status_code==200
 assert backend.state['active_destination']=='263'
 assert client.post('/api/queue',json={'room':'251'},headers=headers).status_code==200
 backend.update_telemetry({'estop_latched':True})
 assert client.post('/api/go-now',json={'room':'202'},headers=headers).status_code==409
 assert client.post('/api/resume',headers=headers).status_code==409
 assert client.post('/api/emergency-stop').status_code==401
 resp=client.post('/api/emergency-stop',headers=headers)
 assert resp.status_code==200 and resp.json()['published'] is True
 assert backend.broker.commands[-1]=={'type':'stop'}
 assert backend.state['estop_latched'] is True, 'remote command must not clear physical latch'
 assert backend.state['active_destination'] is None and backend.state['mission']==[]
 assert client.post('/api/go-now',json={'room':'263'},headers=headers).status_code==409, 'remote STOP requires local verified clearance'
 print('Kratos V9 auto-marker, E-stop dispatch block and remote STOP publishing checks passed')
