"""Minimal Kratos web/API skeleton. Run under an HTTPS reverse proxy.

This server is NOT the self-contained browser simulator. It is a separate starting
point for integrating real ESP32 telemetry with a private Mosquitto broker.
Motion output remains disabled by firmware until hardware passes bench testing.
"""
from __future__ import annotations
import asyncio
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from .localization import validate_survey, match_scan

HERE = Path(__file__).parent
SURVEY_PATH = Path(os.environ.get("WAYMO_SURVEY_PATH", str(HERE / "floor2-survey.json")))
HISTORY_DB = Path(os.environ.get("WAYMO_HISTORY_DB", str(HERE / "mission_history.sqlite3")))
ADMIN_TOKEN = os.environ.get("WAYMO_ADMIN_TOKEN", "")
MQTT_HOST = os.environ.get("WAYMO_MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.environ.get("WAYMO_MQTT_PORT", "1883"))
MQTT_USERNAME = os.environ.get("WAYMO_MQTT_USERNAME", "")
MQTT_PASSWORD = os.environ.get("WAYMO_MQTT_PASSWORD", "")
app = FastAPI(title="Mini-Waymo Micro / Kratos", version="0.1")
state = {"online": False, "status": "NO DEVICE TELEMETRY", "floor": 2,
         "mission": [], "active_destination": None, "pending_rooms": [], "pause_requested": False, "estop_latched": None, "emergency_stop_requested": False, "recovery_state": "awaiting initial marker", "position": None, "localization": "unknown", "robot": "waymo-micro-01", "battery_v": None, "battery_pct": None, "arrival_confirmed": False, "last_confirmed_room": None}
listeners: set[asyncio.Queue] = set()
broker = None

def init_history():
    HISTORY_DB.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(HISTORY_DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY, arrived_utc TEXT NOT NULL, room TEXT NOT NULL, marker_node TEXT NOT NULL, battery_v REAL, verified INTEGER NOT NULL)")

def record_arrival(room: str, marker: str, battery_v):
    init_history()
    with sqlite3.connect(HISTORY_DB) as db:
        db.execute("INSERT INTO trips(arrived_utc,room,marker_node,battery_v,verified) VALUES(?,?,?,?,1)", (datetime.now(timezone.utc).isoformat(), room, marker, battery_v))

def recent_history(limit: int = 40):
    init_history()
    with sqlite3.connect(HISTORY_DB) as db:
        db.row_factory=sqlite3.Row
        return [dict(r) for r in db.execute("SELECT * FROM trips ORDER BY id DESC LIMIT ?", (max(1,min(limit,100)),))]


def admin(authorization: str | None):
    if not ADMIN_TOKEN:
        raise HTTPException(503, "Admin token not configured")
    if authorization != "Bearer " + ADMIN_TOKEN:
        raise HTTPException(401, "Admin authentication required")


def notify():
    for q in tuple(listeners):
        try: q.put_nowait(state.copy())
        except asyncio.QueueFull: pass


def publish(topic: str, data: dict):
    if not broker or not broker.is_connected():
        raise HTTPException(503, "Private MQTT broker not connected")
    info = broker.publish(topic, json.dumps(data), qos=1, retain=False)
    if info.rc:
        raise HTTPException(503, "MQTT publish failed")


@app.on_event("startup")
async def on_startup():
    global broker
    init_history()
    try:
        import paho.mqtt.client as mqtt
        loop = asyncio.get_running_loop()
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="waymo-kratos")
        if MQTT_USERNAME: client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        def connected(_client, _userdata, _flags, reason_code, _properties):
            if reason_code == 0: _client.subscribe("waymo/micro-01/telemetry", qos=0)
        def message(_client, _userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                if not isinstance(payload, dict): return
                # Whitelist fields shown to guests; never publish secrets or a camera stream.
                valid = {k: payload[k] for k in ('status','battery_pct','battery_v','room','speed_mps','estop_latched','estop_switch_open','marker_node','arrival_confirmed') if k in payload}
                loop.call_soon_threadsafe(update_telemetry, valid)
            except (ValueError, UnicodeError, TypeError): pass
        client.on_connect,client.on_message=connected,message
        client.connect_async(MQTT_HOST, MQTT_PORT)
        client.loop_start();broker = client
    except (ImportError, OSError):
        # Public dashboard still works and explicitly reports no robot connection.
        broker = None

def init_history():
    HISTORY_DB.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(HISTORY_DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY, arrived_utc TEXT NOT NULL, room TEXT NOT NULL, marker_node TEXT NOT NULL, battery_v REAL, verified INTEGER NOT NULL)")

def record_arrival(room: str, marker: str, battery_v):
    init_history()
    with sqlite3.connect(HISTORY_DB) as db:
        db.execute("INSERT INTO trips(arrived_utc,room,marker_node,battery_v,verified) VALUES(?,?,?,?,1)", (datetime.now(timezone.utc).isoformat(), room, marker, battery_v))

def recent_history(limit: int = 40):
    init_history()
    with sqlite3.connect(HISTORY_DB) as db:
        db.row_factory=sqlite3.Row
        return [dict(r) for r in db.execute("SELECT * FROM trips ORDER BY id DESC LIMIT ?", (max(1,min(limit,100)),))]


def update_telemetry(telemetry):
    # Device-originated observations only. Replace this mock device source with
    # authenticated per-device MQTT identity before allowing unattended motion.
    safe = {k:v for k,v in telemetry.items() if k not in ('marker_node','arrival_confirmed','battery_v','battery_pct')}
    state.update(safe)
    state['online']=True
    if type(telemetry.get('battery_v')) in (int,float):
        val=float(telemetry['battery_v'])
        if 2.5<=val<=4.3: state['battery_v']=round(val,3)
    if type(telemetry.get('battery_pct')) in (int,float):
        val=float(telemetry['battery_pct'])
        if 0<=val<=100: state['battery_pct']=round(val,1) # reported, uncalibrated
    marker=telemetry.get('marker_node')
    surveyed=None
    if isinstance(marker,str) and SURVEY_PATH.exists():
        try:
            surveyed=validate_survey(json.loads(SURVEY_PATH.read_text()))
        except (ValueError,OSError,KeyError,json.JSONDecodeError): pass
    if surveyed and marker in surveyed['nodes'] and marker in surveyed['signatures']:
        state['position']=marker
        state['localization']='marker-confirmed'
        state['recovery_state']='localized without rotation'
    elif state.get('localization') in ('unknown','ambiguous - stopped',None):
        state['position']=None
        state['recovery_state']='waiting for unique marker; scan requires supervised clearance'
    # Arrival requires a matching marker, a separate on-device arrival indication,
    # and a STOPPED measured speed. Status on the dashboard is not motion authority.
    goal=state.get('active_destination')
    expected=surveyed['rooms'].get(goal) if (surveyed and goal) else None
    speed=telemetry.get('speed_mps')
    can_verify=(goal is not None and expected==marker and
      telemetry.get('arrival_confirmed') is True and
      isinstance(speed,(int,float)) and not isinstance(speed,bool) and abs(speed)<0.025 and
      state.get('localization')=='marker-confirmed')
    if can_verify:
        record_arrival(goal, marker, state.get('battery_v'))
        state['last_confirmed_room']=goal
        state['arrival_confirmed']=True
        state['status']='ARRIVED - VERIFIED MARKER'
        following=state['pending_rooms'].pop(0) if state['pending_rooms'] else None
        state['active_destination']=following
        state['mission']=[following,*state['pending_rooms']] if following else []
        # New mission leg must be separately acknowledged before motion.
        state['pause_requested']=bool(following)
    elif goal:
        state['arrival_confirmed']=False
    notify()


@app.on_event("shutdown")
async def on_shutdown():
    if broker:
        broker.loop_stop()
        broker.disconnect()


class Mission(BaseModel):
    rooms: list[str] = Field(min_length=1, max_length=12)


class RoomTarget(BaseModel):
    room: str = Field(min_length=1, max_length=8)


class RelocalizeRequest(BaseModel):
    scan: list[dict[str,float]] = Field(min_length=10,max_length=120)


@app.get('/api/history')
async def history():
    # Read-only summary suitable for guests; no photos or precise personal data.
    return {'trips': recent_history()}

@app.get('/api/state')
async def get_state():
    return state


@app.get('/api/survey/meta')
async def survey_meta():
    if not SURVEY_PATH.exists():
        return {'available': False, 'recorded_anchors': 0}
    data = validate_survey(json.loads(SURVEY_PATH.read_text()))
    return {'available': True, 'recorded_anchors': len(data['signatures']), 'building': data.get('building'), 'floor': data.get('floor')}


@app.post('/api/survey')
async def upload_survey(payload: dict, authorization: str | None = Header(None)):
    admin(authorization)
    data = validate_survey(payload)
    SURVEY_PATH.parent.mkdir(parents=True,exist_ok=True)
    SURVEY_PATH.write_text(json.dumps(data,indent=2))
    return {'recorded_anchors':len(data['signatures'])}


@app.post('/api/relocalize')
async def relocalize(payload: RelocalizeRequest, authorization: str | None = Header(None)):
    admin(authorization)
    if not SURVEY_PATH.exists():
        raise HTTPException(404, 'No trained hallway survey')
    match = match_scan(json.loads(SURVEY_PATH.read_text()), payload.scan)
    if match['ok']:
        state['localization'] = 'estimated anchor (requires verification)'; state['recovery_state'] = 'depth candidate needs validation'
        state['position'] = match['node']
        notify()
    else:
        state['localization'] = 'ambiguous - stopped'; state['recovery_state'] = 'ambiguous scan; wait for marker'
        state['position'] = None
        notify()
    return match


@app.post('/api/mission')
async def mission(payload: Mission, authorization: str | None = Header(None)):
    admin(authorization)
    if any(not r.isdigit() or len(r)>4 for r in payload.rooms):
        raise HTTPException(422, 'Room names must be numeric')
    if state['localization'] != 'marker-confirmed' or state.get('estop_latched') is not False or state.get('emergency_stop_requested'):
        raise HTTPException(409, 'Localization, physical E-stop or remote STOP lockout unverified')
    publish('waymo/micro-01/cmd', {'type': 'mission', 'rooms': payload.rooms})
    state['mission'] = payload.rooms
    notify()
    return {'queued':payload.rooms}


# These routes expose explicit immediate and queued dispatch APIs to an admin.
# Commands are PUBLISHED but not considered EXECUTED until a device ACK is added.
def checked_room(room: str) -> str:
    if not room.isdigit() or len(room)>4:
        raise HTTPException(422,'Room must be numeric')
    if not SURVEY_PATH.exists():
        raise HTTPException(409,'Upload a verified building survey first')
    surveyed = validate_survey(json.loads(SURVEY_PATH.read_text()))
    if room not in surveyed['rooms']:
        raise HTTPException(422,'Room is not present in surveyed map')
    if state['localization'] != 'marker-confirmed' or state['position'] is None:
        raise HTTPException(409,'Robot needs a confirmed location marker before dispatch')
    if state.get('battery_v') is not None and state['battery_v'] < 3.55:
        raise HTTPException(409,'Battery voltage too low for new trip')
    if state.get('estop_latched') is not False or state.get('emergency_stop_requested'):
        raise HTTPException(409,'E-stop status unknown or STOP lockout active; local verification required')
    return room


@app.get('/api/rooms')
async def list_rooms():
    if not SURVEY_PATH.exists():
        return {'rooms': [], 'surveyed': False}
    data=validate_survey(json.loads(SURVEY_PATH.read_text()))
    return {'rooms': sorted(data['rooms'].keys()), 'surveyed': True}


@app.post('/api/go-now')
async def go_now(payload: RoomTarget, authorization: str | None=Header(None)):
    admin(authorization)
    room=checked_room(payload.room)
    publish('waymo/micro-01/cmd', {'type':'go_now', 'room': room})
    state['mission']=[room]
    state['pause_requested']=False
    state['active_destination']=room
    state['arrival_confirmed']=False
    state['pending_rooms']=[]
    notify()
    return {'published':True, 'active_destination':room, 'pending_rooms':[]}


@app.post('/api/queue')
async def queue_room(payload: RoomTarget, authorization: str | None=Header(None)):
    admin(authorization)
    room=checked_room(payload.room)
    if len(state['pending_rooms'])>=12:
        raise HTTPException(409, 'Queue is full')
    publish('waymo/micro-01/cmd', {'type':'queue_stop','room': room})
    if state['active_destination'] is None:
        state['active_destination']=room
        state['arrival_confirmed']=False
    else:
        state['pending_rooms'].append(room)
    state['mission']=[state['active_destination'],*state['pending_rooms']]
    notify()
    return {'published':True,'active_destination':state['active_destination'], 'pending_rooms':state['pending_rooms']}


@app.post('/api/queue/clear')
async def clear_queue(authorization: str | None=Header(None)):
    admin(authorization)
    publish('waymo/micro-01/cmd', {'type':'clear_pending'})
    state['pending_rooms']=[]
    state['mission']=[state['active_destination']] if state['active_destination'] else []
    notify()
    return {'published': True,'active_destination':state['active_destination'],'pending_rooms':[]}


@app.post('/api/pause')
async def pause(authorization: str | None=Header(None)):
    admin(authorization)
    if state['active_destination'] is None:
        raise HTTPException(409, 'There is no active route to pause')
    publish('waymo/micro-01/cmd', {'type':'pause'})
    state['pause_requested']=True
    notify()
    return {'published':True,'pause_requested':True,'active_destination':state['active_destination'],'pending_rooms':state['pending_rooms']}

@app.post('/api/resume')
async def resume(authorization: str | None=Header(None)):
    admin(authorization)
    if not state['pause_requested'] or state['active_destination'] is None:
        raise HTTPException(409, 'There is no paused trip')
    if (state.get('battery_v') is not None and state['battery_v']<3.55):
        raise HTTPException(409, 'Battery voltage below resume threshold')
    if not state['online'] or state['localization'] != 'marker-confirmed' or state['position'] is None or state.get('estop_latched') is not False or state.get('emergency_stop_requested'):
        raise HTTPException(409, 'Cannot resume without device telemetry and a verified position')
    publish('waymo/micro-01/cmd', {'type':'resume'})
    state['pause_requested']=False
    notify()
    return {'published':True,'pause_requested':False,'active_destination':state['active_destination'],'pending_rooms':state['pending_rooms']}

@app.post('/api/hold')
async def hold(authorization: str | None=Header(None)):
    admin(authorization)
    publish('waymo/micro-01/cmd', {'type':'hold'})
    state['pending_rooms']=[]
    state['active_destination']=None
    state['pause_requested']=False
    state['mission']=[]
    notify()
    return {'published':True}


@app.post('/api/emergency-stop')
async def emergency_stop(authorization: str | None=Header(None)):
    admin(authorization)
    # Remote command, not equivalent to cutting hardware motor power.
    publish('waymo/micro-01/cmd', {'type':'stop'})
    state['emergency_stop_requested'] = True
    state['pause_requested'] = False
    state['pending_rooms'] = []
    state['active_destination'] = None
    state['mission'] = []
    notify()
    return {'published': True, 'note': 'Remote STOP requested; hardware E-stop must be actuated locally'}

@app.post('/api/stop')
async def stop(authorization: str | None = Header(None)):
    admin(authorization)
    publish('waymo/micro-01/cmd', {'type':'stop'})
    state['pending_rooms']=[]
    state['active_destination']=None
    state['pause_requested']=False
    state['mission']=[]
    notify()
    return {'sent':True}


@app.websocket('/ws/state')
async def ws_state(ws: WebSocket):
    # Guest telemetry only. The socket CANNOT send commands.
    await ws.accept()
    q = asyncio.Queue(maxsize=5)
    listeners.add(q)
    try:
        await ws.send_json(state)
        while True: await ws.send_json(await q.get())
    except (WebSocketDisconnect,RuntimeError): pass
    finally: listeners.discard(q)

@app.post('/api/recovery/request')
async def request_recovery(authorization: str | None=Header(None)):
    admin(authorization)
    if state.get('estop_latched') is not False or state.get('emergency_stop_requested'):
        raise HTTPException(409, 'Cannot request recovery while stop circuit is active or unknown')
    if state.get('active_destination'):
        raise HTTPException(409, 'Pause or stop mission before recovery')
    publish('waymo/micro-01/cmd', {'type':'request_marker_observation'})
    state['recovery_state']='awaiting sensor-confirmed unique marker'
    notify()
    return {'published':True,'note':'No automatic spin; observation only; not confirmation'}

# Shared project task assignment. Site visitors can see the board without login;
# only a server-verified team password can change task ownership/status.
from .team_tasks import router as team_tasks_router
app.include_router(team_tasks_router)

# Single-origin deployment convenience. FastAPI serves the static site and
# /api/tasks from the same hostname, avoiding browser CORS and hidden API hosts.
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
SITE_ROOT = Path(__file__).resolve().parent.parent
app.mount('/assets', StaticFiles(directory=str(SITE_ROOT / 'assets')),name='assets')

@app.get('/',include_in_schema=False)
@app.get('/index.html',include_in_schema=False)
def team_site_index():
    return FileResponse(str(SITE_ROOT / 'Mini_Waymo_V12_Demo.html'))

@app.get('/Mini_Waymo_V12_Demo.html',include_in_schema=False)
def team_site_demo():
    return FileResponse(str(SITE_ROOT / 'Mini_Waymo_V12_Demo.html'))

@app.get('/Mini_Waymo_V12_About.html',include_in_schema=False)
def team_site_about():
    return FileResponse(str(SITE_ROOT / 'Mini_Waymo_V12_About.html'))

@app.get('/team_members.json',include_in_schema=False)
def team_site_roster():
    return FileResponse(str(SITE_ROOT / 'team_members.json'),media_type='application/json')

@app.get('/project_progress.json',include_in_schema=False)
def team_site_progress():
    return FileResponse(str(SITE_ROOT / 'project_progress.json'),media_type='application/json')
