import json,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from kratos import app as b
class MQTT:
 def __init__(self):self.out=[]
 def is_connected(self):return True
 def publish(self,t,p,qos,retain):self.out.append(json.loads(p));return type('X',(),{'rc':0})()
with TemporaryDirectory() as td:
 b.SURVEY_PATH=Path(td)/'survey.json';b.SURVEY_PATH.write_text((Path(__file__).resolve().parents[1]/'kratos/example-fictional-survey-v6.json').read_text())
 b.HISTORY_DB=Path(td)/'history.sqlite3';b.ADMIN_TOKEN='test';b.broker=MQTT()
 b.state.update({'online':False,'localization':'unknown','position':None,'estop_latched':False,'emergency_stop_requested':False,'active_destination':None,'pending_rooms':[],'battery_v':None,'battery_pct':None,'mission':[],'arrival_confirmed':False,'pause_requested':False})
 c=TestClient(b.app);h={'Authorization':'Bearer test'}
 assert c.post('/api/recovery/request').status_code==401
 assert c.post('/api/recovery/request',headers=h).status_code==200
 assert b.broker.out[-1]['type']=='request_marker_observation'
 b.update_telemetry({'marker_node':'A','battery_v':4.03,'estop_latched':False})
 assert c.post('/api/go-now',json={'room':'263'},headers=h).status_code==200
 # wrong marker is not an arrival
 b.update_telemetry({'marker_node':'I','arrival_confirmed':True,'speed_mps':0.0})
 assert b.state['active_destination']=='263' and len(b.recent_history())==0
 # matching marker with movement is not an arrival
 b.update_telemetry({'marker_node':'J','arrival_confirmed':True,'speed_mps':0.25})
 assert len(b.recent_history())==0
 b.update_telemetry({'marker_node':'J','arrival_confirmed':True,'speed_mps':0.0})
 assert len(b.recent_history())==1 and b.recent_history()[0]['room']=='263'
 assert b.state['last_confirmed_room']=='263'
 assert c.get('/api/history').json()['trips'][0]['room']=='263'
 # low battery blocks next dispatch and resume
 b.update_telemetry({'battery_v':3.40})
 assert c.post('/api/go-now',json={'room':'251'},headers=h).status_code==409
 assert c.post('/api/recovery/request',headers=h).status_code==200
 print('V10 Kratos: history SQLite, marker+stationary arrival, recovery auth, low battery checks pass')
