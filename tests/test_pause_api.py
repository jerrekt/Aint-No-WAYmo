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
 p=Path(temp)/'survey.json';p.write_text((Path(__file__).resolve().parents[1]/'kratos/example-fictional-survey-v6.json').read_text())
 backend.SURVEY_PATH=p;backend.ADMIN_TOKEN='test-key';backend.broker=FakeMQTT()
 backend.state.update({'online':True,'localization':'marker-confirmed','position':'A','active_destination':None,'pending_rooms':[],'mission':[],'pause_requested':False,'estop_latched':False})
 client=TestClient(backend.app);h={'Authorization':'Bearer test-key'}
 assert client.post('/api/pause',headers=h).status_code==409
 assert client.post('/api/go-now',json={'room':'230'},headers=h).status_code==200
 assert client.post('/api/queue',json={'room':'251'},headers=h).status_code==200
 assert client.post('/api/pause').status_code==401
 assert client.post('/api/pause',headers=h).status_code==200
 assert backend.state['pause_requested']
 assert backend.state['active_destination']=='230' and backend.state['pending_rooms']==['251']
 assert client.post('/api/resume',headers=h).status_code==200
 assert backend.state['active_destination']=='230' and backend.state['pending_rooms']==['251']
 assert backend.broker.commands[-2:]==[{'type':'pause'},{'type':'resume'}]
 assert client.post('/api/resume',headers=h).status_code==409
 assert client.post('/api/pause',headers=h).status_code==200
 assert client.post('/api/stop',headers=h).status_code==200
 assert backend.state['pause_requested']==False and backend.state['mission']==[]
 print('Kratos pause/resume auth/queue/stop tests passed (mock broker)')
