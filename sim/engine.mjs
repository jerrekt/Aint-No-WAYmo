// Mini-Waymo Micro V4: simulated hallway telemetry, idealized depth scan, noisy odometry,
// gyroscope drift, landmark correction, MQTT watchdog, Kratos route planner.
// This is intentionally an illustrative / FICTIONAL hallway topology.
// Placeholder reverse-C hallway graph based on user-supplied IS building footprint.
// NO room number position is field verified. 200 starts bottom-right and 230
// runs up the right-hand leg, followed by the upper wing counter-clockwise.
export const NODES={
 A:[20,2], B:[20,4], C:[20,6], D:[20,8], E:[20,10], F:[20,12], G:[20,14],
 H:[16,14], I:[12,14], J:[9,14], K:[9,11], L:[9,9],
 M:[16,2], N:[12,2], O:[9,2], P:[9,4]
};
export const EDGES=[['A','B'],['B','C'],['C','D'],['D','E'],['E','F'],['F','G'],
 ['G','H'],['H','I'],['I','J'],['J','K'],['K','L'],
 ['A','M'],['M','N'],['N','O'],['O','P']];
export const ROOMS={'200':'A','205':'B','210':'C','215':'D','220':'E','225':'F','230':'G',
 '240':'H','251':'I','263':'J','265':'L','202':'M','204':'N','208':'O','212':'P'};
export const LABELS={0:'IDLE',1:'DRIVING',2:'WAITING FOR PEDESTRIAN',3:'OBSTACLE STOP',4:'SENSOR STOP',5:'MQTT LOST',6:'LOCALIZATION UNCERTAIN',7:'360° SCANNING',8:'ROOM CONFIRMED',9:'EMERGENCY STOP'};
export const hypot=(a,b)=>Math.hypot(a,b);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a));
const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const XY=([x,y])=>({x,y});
function segDist(p,a,b){const dx=b[0]-a[0],dy=b[1]-a[1],q=clamp(((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy),0,1);return Math.hypot(p[0]-a[0]-q*dx,p[1]-a[1]-q*dy)}
function walkDist(x,y){let d=1e9;for(const [a,b] of EDGES)d=Math.min(d,segDist([x,y],NODES[a],NODES[b]));return d}
const WIDTH=1.9;
export function inHall(x,y,margin=0){return walkDist(x,y)<WIDTH/2-margin}
export function route(start,end,blocked=[]){
 const distances={};const parent={};const open=new Set(Object.keys(NODES));for(const k of open) distances[k]=Infinity;distances[start]=0;
 while(open.size){let u=null;for(const v of open)if(u===null||distances[v]<distances[u])u=v;
 if(!Number.isFinite(distances[u]))break;open.delete(u);if(u===end)break;
 for(const [a,b] of EDGES){const v=u===a?b:u===b?a:null;if(!v||!open.has(v)||blocked.includes([u,v].sort().join('-')))continue;
 const alt=distances[u]+distance(NODES[u],NODES[v]);if(alt<distances[v]){distances[v]=alt;parent[v]=u;}}
 }
 if(!Number.isFinite(distances[end]))return [];
 let path=[end];let n=end;while(n!==start){n=parent[n];if(!n)return [];path.unshift(n);}return path;
}
export function ray(x,y,theta,max=3.5,objects=[]){
 for(let r=0.05;r<=max;r+=0.045){let px=x+Math.cos(theta)*r,py=y+Math.sin(theta)*r;
 if(!inHall(px,py))return r;
 for(const o of objects){if(Math.hypot(o.x-px,o.y-py)<o.r)return r;}
 }return max;
}
// The model casts eight horizontal ray directions; 8x8 optical depth zones are not
// faithfully modeled in 3D, and no real images or AprilTag detections are processed.
export function tofGrid(x,y,yaw,objects=[]){return Array.from({length:8},(_,i)=>ray(x,y,yaw+(i-3.5)*0.105,3.5,objects));}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296}}
function gaussian(rng){return Math.sqrt(-2*Math.log(Math.max(1e-8,rng())))*Math.cos(2*Math.PI*rng())}

// Saved survey: topology comes from an operator-drawn floor plan. Reference scans
// are recorded at operator-annotated landmarks. This is NOT automatic SLAM.
const SCAN_BINS=24;
export function newSurvey(){return {schema:1,building:'IS',floor:2,source:'synthetic operator-annotated training fixture',created:new Date().toISOString(),nodes:JSON.parse(JSON.stringify(NODES)),edges:EDGES.map(x=>[...x]),rooms:{...ROOMS},signatures:{}};}
export function validateSurvey(map){
 if(!map||map.schema!==1||!map.signatures||!map.nodes||!map.edges||!map.rooms)throw Error('Invalid survey schema');
 for(const [key,v] of Object.entries(map.signatures)){
  if(!(key in NODES)||!Array.isArray(v)||v.length!==SCAN_BINS||v.some(n=>!Number.isFinite(n)||n<0.03||n>3.51))throw Error('Invalid signature '+key);
 }
 return map;
}
export function recordSurveyAnchor(map,node,noiseSeed=1){
 validateSurvey(map);if(!(node in NODES))throw Error('Unknown survey anchor');
 const rng=mulberry32(noiseSeed+node.charCodeAt(0)*2917),[x,y]=NODES[node];
 map.signatures[node]=Array.from({length:SCAN_BINS},(_,i)=>clamp(ray(x,y,i*2*Math.PI/SCAN_BINS,3.5,[])+gaussian(rng)*.011,.05,3.5));
 return map;
}
function scoreSurvey(reference,readings,shift){
 // Robust matching: trim the most inconsistent 20% (e.g. moving students).
 const differences=readings.map(z=>{
  const j=Math.round((z.rel/(2*Math.PI))*SCAN_BINS+shift)%SCAN_BINS;
  return Math.pow(reference[(j+SCAN_BINS)%SCAN_BINS]-z.range,2);
 }).sort((a,b)=>a-b);
 return differences.slice(0,Math.max(5,Math.floor(differences.length*.80))).reduce((a,b)=>a+b,0)/Math.max(5,Math.floor(differences.length*.80));
}
export function matchSurvey(map,readings){
 validateSurvey(map);
 if(readings.length<10)return {ok:false,reason:'Too few valid scan headings',ranked:[]};
 let ranked=[];
 for(const [node,ref] of Object.entries(map.signatures)){
  let best={score:Infinity,heading:0};
  for(let shift=0;shift<SCAN_BINS;shift++){
   const score=scoreSurvey(ref,readings,shift);
   if(score<best.score)best={score,heading:shift*2*Math.PI/SCAN_BINS};
  }
  ranked.push({node,score:best.score,heading:best.heading});
 }
 ranked.sort((a,b)=>a.score-b.score);
 if(!ranked.length)return {ok:false,reason:'No survey anchors recorded',ranked};
 const first=ranked[0],second=ranked[1];
 // Exact repeated T-junctions are intentionally NOT accepted based on depth alone.
 const distinct=!second || (second.score-first.score>0.009 && second.score>first.score*3.0);
 const quality=first.score<0.095;
 return {ok:distinct&&quality,node:distinct&&quality?first.node:null,heading:first.heading,
  reason:!quality?'Scan does not match surveyed walls':!distinct?'Multiple hallway positions look alike':'Unique surveyed anchor matched',ranked:ranked.slice(0,4)};
}

export async function makeCore(wasmBytes){
 const {instance}=await WebAssembly.instantiate(wasmBytes,{env:{sin:Math.sin,cos:Math.cos,atan2:Math.atan2}});
 const exp=instance.exports, inputPtr=exp.core_input(),outPtr=exp.core_output();
 if(exp.core_input_count()!=15||exp.core_output_count()!=5)throw Error('Controller ABI mismatch');
 return {reset:()=>exp.core_reset(),run(values){const mem=new Float64Array(exp.memory.buffer);mem.set(values,inputPtr/8);exp.core_wasm_step();return Array.from(mem.slice(outPtr/8,outPtr/8+5));}};
}
export class MicroSimulation {
 constructor(core,{seed=1,mission=['200'],autoScan=false,noise=1,survey=null}={}){this.core=core;this.seed=seed;this.originalMission=[...mission];this.mission=[...mission];this.autoScan=autoScan;this.noise=noise;this.survey=survey;this.reset()}
 reset(){
  this.rng=mulberry32(this.seed);this.core.reset();this.time=0;const startNode=NODES[ROOMS[this.mission[0]]];this.robot={x:startNode[0],y:startNode[1],yaw:Math.PI/2,lv:0,rv:0};
  this.est={x:startNode[0]+0.02,y:startNode[1]+0.015,yaw:Math.PI/2+0.012,sigma:0.045};this.lastMarker=this.mission[0];this.sensor={front:3.5,side:1.0,grid:Array(8).fill(3.5),personConf:0,personRange:9};
  this.heartbeatAge=0;this.wifi=true;this.tofHealthy=true;this.markersEnabled=true;this.estop=false;this.estopSwitchPressed=false;this.estopLatched=false;this.autoRecover=true;this.people=false;this.chair=false;
  this.waitS=0;this.stops=0;this.arrivals=0;this.collisions=0;this.boundaryViolations=0;this.totalTravel=0;
  this.mode='IDLE';this.prevStatus=-1;this.out=[0,0,0,0,0];this.stepIndex=0;this.currentRoom=this.mission[0];this.plan=[];this.pathIndex=0;
  this.logged=[];this.scans=[];this.scanData=[];this.scanHeading=0;this.scannedNodes=new Set();this.scanRequested=false;this.scanning=false;this.scanStart=0;this.scanTurns=0;this.nextScanAngle=0;
  this.complete=false;this.failed=false;this.operatorPaused=false;this.lastMarkerTime=-100;this.dwell=0;this.goalConfirmed=false;this.dispatchCount=0;this.completedStops=[];this.tripHistory=[];this.activeLeg=null;this.batteryVoltage=4.12;this.lowBatteryStop=false;
  this.localized=true;this.relocalizeRequested=false;this.relocalizationResult=null;this.relocalizationNode=null;this.log('Booted at room '+this.currentRoom+'; map is fictional');
 }
 log(m){if(this.logged.at(-1)?.text===m)return;this.logged.push({t:this.time,text:m});if(this.logged.length>120)this.logged.shift()}
 start(){
  if(!this.localized){this.log('Kratos refused mission: position not confirmed');return false;}
  if(this.stepIndex>=this.mission.length-1){this.complete=true;this.running=false;this.log('Idle at IS '+this.currentRoom+'; ready for another room');return true}
  this.complete=false;this.running=true;this.nextLeg();if(!this.activeLeg)this.activeLeg={from:this.currentRoom,to:this.mission[this.stepIndex+1],start:this.time};return true;
 }

 // Dispatch APIs mirror the server model: a Go now replaces the outstanding
 // queue, while Add stop never interrupts the active leg. Neither operation
 // resets the map, odometry, history, or the virtual hardware.
 canDispatch(){
  if(!this.localized || this.est.sigma>0.65){this.log('Dispatch refused: position is not confirmed');return false;}
  if(this.batteryVoltage<3.55){this.log('Dispatch refused: low battery voltage');return false;}
  if(!this.wifi||!this.tofHealthy||this.estopLatched||this.estop){this.log('Dispatch refused: connection or E-stop safety not ready');return false;}
  return true;
 }
 plannedStops(){return this.mission.slice(this.stepIndex+1);}
 nextFromEstimatedPose(dest){
  // Candidate start points must be endpoints of the closest walkable edge.
  // The robot drives along an observed hallway; it never teleports to a node.
  let bestEdge=null, bestGap=1e8;
  for(const [a,b] of EDGES){const d=segDist([this.est.x,this.est.y],NODES[a],NODES[b]);if(d<bestGap){bestGap=d;bestEdge=[a,b];}}
  if(!bestEdge || bestGap>WIDTH/2+0.1)return [];
  let best=null;
  for(const n of bestEdge){const rest=route(n,dest);if(!rest.length)continue;
   let cost=distance([this.est.x,this.est.y],NODES[n]);
   for(let j=0;j<rest.length-1;j++)cost+=distance(NODES[rest[j]],NODES[rest[j+1]]);
   if(!best||cost<best.cost)best={cost,path:rest};
  }
  return best?.path||[];
 }
 goNow(room){
  if(!(room in ROOMS)){this.log('Unknown room '+room);return false;}
  if(!this.canDispatch())return false;
  // Current location remains the last *confirmed* room. Path from the
  // estimated physical pose, not from an older marker or a spawned start.
  if(!this.running && room===this.currentRoom){this.log('Already at IS '+room+'; ready for another destination');return true;}
  const newPlan=this.nextFromEstimatedPose(ROOMS[room]);
  if(!newPlan.length){this.log('Go now refused: no verified mapped route');return false;}
  this.mission=[this.currentRoom,room];this.stepIndex=0;this.plan=newPlan;this.pathIndex=0;
  this.goalConfirmed=false;this.dwell=0;this.complete=false;this.failed=false;
  if(this.activeLeg)this.finishLeg('rerouted');this.activeLeg={from:this.currentRoom,to:room,start:this.time};
  this.scanning=false;this.scanRequested=false;this.relocalizeRequested=false;
  this.scannedNodes=new Set();this.running=true;this.dispatchCount++;
  this.operatorPaused=false;this.log('GO NOW to IS '+room+'; replaced pending stops; replan '+newPlan.join('→'));
  return true;
 }
 addStop(room){
  if(!(room in ROOMS)){this.log('Unknown room '+room);return false;}
  if(!this.canDispatch())return false;
  if(!this.running || this.complete){
    this.mission=[this.currentRoom,room];this.stepIndex=0;
    this.plan=[];this.complete=false;this.failed=false;
    this.activeLeg={from:this.currentRoom,to:room,start:this.time};this.dispatchCount++;this.log('New trip from IS '+this.currentRoom+' to IS '+room);
    if(room===this.currentRoom){this.complete=true;this.log('Already at destination IS '+room);return true;}
    return this.start();
  }
  if(this.mission.length-this.stepIndex>15){this.log('Queue limit reached');return false;}
  this.mission.push(room);this.dispatchCount++;
  this.log('Queued IS '+room+' after '+this.mission[this.mission.length-2]);return true;
 }
 removeQueued(index){
  // index 0 is the ACTIVE destination, which cannot be removed this way.
  const i=this.stepIndex+1+index;
  if(index<1||i>=this.mission.length)return false;
  const [removed]=this.mission.splice(i,1);this.log('Removed queued IS '+removed);return true;
 }
 clearPending(){
  const keep=Math.min(this.mission.length,this.stepIndex+2);
  const removed=this.mission.length-keep;this.mission.length=keep;
  this.log('Cleared '+removed+' future stop(s); current leg unchanged');return removed;
 }
 holdAndClear(){
  if(this.estopLatched){this.log('Stop request received but E-stop remains latched');return;}
  if(this.activeLeg)this.finishLeg('operator stopped');
  this.operatorPaused=false;this.running=false;this.robot.lv=0;this.robot.rv=0;
  this.mission=[this.currentRoom];this.stepIndex=0;this.plan=[];this.pathIndex=0;
  this.complete=false;this.scanning=false;this.goalConfirmed=false;
  this.out=[0,0,0,0,0];this.mode='HELD — READY';this.log('Operator HOLD: route and queue canceled');
 }
 // Independent *simulated* hard E-stop. The physical design uses a dual-pole
 // normally-closed latching switch: one pole interrupts motor-driver VM and
 // one sends a normally-low signal to an ESP32 input. Simulation cannot
 // establish physical stopping distance or power isolation.
 pressEstop(){
  if(this.activeLeg)this.finishLeg('emergency stop');
  this.estopSwitchPressed=true;this.estopLatched=true;this.estop=true;
  this.running=false;this.scanning=false;this.relocalizeRequested=false;
  this.robot.lv=0;this.robot.rv=0;this.out=[0,0,9,2,0];this.mode='E-STOP LATCHED';
  this.log('HARD E-STOP (simulated): motor supply interrupted; manual reset required');
 }
 releaseEstopSwitch(){
  this.estopSwitchPressed=false;
  this.log('E-stop switch released; safety latch remains active');
 }
 localResetEstop(){
  if(this.estopSwitchPressed){this.log('Local reset refused: E-stop switch still pressed');return false;}
  if(!this.estopLatched)return true;
  this.estopLatched=false;this.estop=false;
  this.running=false;this.operatorPaused=false;this.plan=[];this.mission=[this.currentRoom];this.stepIndex=0;
  this.mode='DISARMED — SELECT NEW TRIP';this.out=[0,0,0,0,0];
  this.log('Local reset simulated: no automatic restart; select a new trip');return true;
 }
 // Unknown drop-off point: only the simulator knows the physical spawn location.
 // Kratos starts with NO position. It must match a scan or read a location marker.
 placeUnknown(node){
  if(!(node in NODES))throw Error('Unknown placement node');
  if(this.activeLeg)this.finishLeg('picked up - localization lost');
  this.core.reset();this.mission=[...this.originalMission];this.stepIndex=0;
  this.robot={x:NODES[node][0],y:NODES[node][1],yaw:0.38,lv:0,rv:0};
  this.est={x:0,y:0,yaw:0,sigma:1.2};this.currentRoom='unknown';this.currentNode=null;
  this.lastMarker='None';this.localized=false;this.relocalizationNode=null;
  this.relocalizationResult=null;this.relocalizeRequested=false;
  this.scanning=false;this.scanRequested=false;this.scanData=[];this.scans=[];
  this.complete=false;this.failed=false;this.running=false;this.plan=[];this.pathIndex=0;
  this.out=[0,0,6,2,0];this.mode='LOCALIZATION UNCERTAIN';this.prevStatus=-1;
  this.log('Robot placed in hallway; Kratos location is UNKNOWN');
  if(this.autoRecover && !this.estopLatched){
   // Prefer non-motion marker detection first; no 360 scan is required when a tag is visible.
   if(this.tryMarkerRecovery())this.log('AUTO RECOVERY: marker confirmed location without rotating');
   else this.log('AUTO RECOVERY: no unique visual marker; stop and request supervised 360 scan');
  }
 }
 finishLeg(result){
  if(!this.activeLeg)return;
  const v={from:this.activeLeg.from,to:this.activeLeg.to,start_s:+this.activeLeg.start.toFixed(1),end_s:+this.time.toFixed(1),result,arrival_verified:result==='marker confirmed',battery_end_v:+this.batteryVoltage.toFixed(2)};
  this.tripHistory.push(v);if(this.tripHistory.length>150)this.tripHistory.shift();this.activeLeg=null;
 }
 recoverNow(){
  if(this.estopLatched||!this.wifi||!this.tofHealthy||this.batteryVoltage<3.55){this.log('Recovery unavailable: safety or connection fault');return false;}
  if(this.localized&&this.est.sigma<0.40){this.log('Recovery unnecessary: position already verified');return true;}
  if(this.tryMarkerRecovery())return true;
  this.log('Marker not visible: stationary scan needs supervised clearance');
  return false;
 }
 beginRelocalize(){
  if(this.estopLatched){this.log('Recovery requires local E-stop reset');return false;}
  if(!this.survey||Object.keys(this.survey.signatures).length===0){this.log('No saved survey to match against');return false}
  if(!this.wifi||!this.tofHealthy||this.estop||this.estopLatched){this.log('Recovery scan refused: connection/sensor/estop');return false}
  this.running=true;this.relocalizeRequested=true;this.scanning=true;
  this.scanData=[];this.scanTurns=0;this.nextScanAngle=0;this.scanStart=this.robot.yaw;
  this.log('Relocalization: rotate 360° and compare saved scans');return true;
 }
 applyKnownNode(node,source){
  if(!(node in NODES))return false;
  const ref=NODES[node];this.est={x:ref[0],y:ref[1],yaw:this.relocalizationResult?.heading??this.robot.yaw,sigma:0.07};
  this.localized=true;this.relocalizationNode=node;this.lastMarker=source==='marker'?'Tag '+node:'Depth '+node;
  const named=Object.entries(ROOMS).find(([,n])=>n===node)?.[0]||node;
  this.currentRoom=named;this.currentNode=node;this.mission=[...this.originalMission];this.stepIndex=0;
  if(node!==ROOMS[this.mission[0]])this.mission=[named,...this.mission];
  this.scannedNodes=new Set();this.plan=[];this.running=false;this.robot.lv=0;this.robot.rv=0;this.out=[0,0,0,0,0];this.mode='READY';
  this.log(source==='marker'?'Unique location marker identified '+node:'Depth scan uniquely matched anchor '+node);
  return true;
 }
 tryMarkerRecovery(){
  if(this.localized)return true;
  if(!this.wifi||!this.tofHealthy||this.estopLatched)return false;
  if(!this.markersEnabled){this.log('No valid location markers available');return false;}
  // Simulated decoded marker near a surveyed junction. Real camera inference absent.
  const entries=Object.entries(NODES).map(([n,p])=>[n,distance([this.robot.x,this.robot.y],p)]).sort((a,b)=>a[1]-b[1]);
  if(entries[0][1]>.30||!this.survey?.signatures?.[entries[0][0]]){this.log('No recognizable surveyed marker nearby');return false;}
  this.relocalizationResult={ok:true,node:entries[0][0],heading:this.robot.yaw,reason:'Simulated unique marker'};
  return this.applyKnownNode(entries[0][0],'marker');
 }
 nextLeg(){const from=this.currentNode||ROOMS[this.currentRoom],to=this.mission[this.stepIndex+1], dest=ROOMS[to];this.plan=route(from,dest);this.pathIndex=1;this.goalConfirmed=false;this.dwell=0;if(!this.plan.length){this.failed=true;this.log('No mapped route');return;}this.log('Kratos planned: IS '+this.currentRoom+' → IS '+to+' ('+this.plan.join('→')+')')}
 currentTarget(){return this.plan[this.pathIndex]||null}
 person(){if(!this.people)return null; // periodic crossing near junction C: a moving student, not a real vision feed
  const phase=(this.time%22)/22;
  return {x:20+(phase-.5)*1.8,y:7.7,r:0.22,person:true};
 }
 objects(){let o=[];const p=this.person();if(p)o.push(p);if(this.chair)o.push({x:20.10,y:9.30,r:0.25,chair:true});return o;}
 landmarks(){ // Printed AprilTag / coded landmark assumptions. Not actually trained or captured.
  if(!this.markersEnabled)return null;
  let best=null,d=1e10;
  for(let n in NODES){let dd=distance([this.robot.x,this.robot.y],NODES[n]);if(dd<d&&dd<0.67){d=dd;best=n;}}
  if(!best||this.rng()>.94)return null;
  return {node:best,d};
 }
 sense(){
  const objects=this.objects();const forward=tofGrid(this.robot.x,this.robot.y,this.robot.yaw,objects);this.sensor.grid=forward.map(r=>clamp(r+gaussian(this.rng)*this.noise*0.012,.02,3.5));
  this.sensor.front=Math.min(...this.sensor.grid.slice(2,6));
  this.sensor.side=clamp(ray(this.robot.x,this.robot.y,this.robot.yaw+Math.PI/2,1.2,objects)+gaussian(this.rng)*0.02*this.noise,0,1.2);
  // One-dimensional side-wall scan matching: correct cross-track drift when a
  // stable mapped wall is in range. In a real building this needs gating for
  // glass walls / doorways and independent validation.
  const predictedSide=ray(this.est.x,this.est.y,this.est.yaw+Math.PI/2,1.2,[]);
  if(predictedSide<1.15&&this.sensor.side<1.15){
    const correction=clamp((predictedSide-this.sensor.side)*0.16,-0.025,0.025);
    this.est.x+=Math.cos(this.est.yaw+Math.PI/2)*correction;
    this.est.y+=Math.sin(this.est.yaw+Math.PI/2)*correction;
  }
  // Person detection is a synthetic camera classifier, not real image inference.
  const p=this.person();const pd=p?Math.hypot(this.robot.x-p.x,this.robot.y-p.y):9;
  const bearing=p?wrap(Math.atan2(p.y-this.robot.y,p.x-this.robot.x)-this.robot.yaw):0;
  this.sensor.personRange=pd;
  this.sensor.personConf=p&&pd<1.8&&Math.abs(bearing)<0.9?(.92-.09*this.rng()):0;
  if(this.markersEnabled&&this.localized){let mark=this.landmarks();if(mark){
    this.est.x=this.robot.x+gaussian(this.rng)*0.025*this.noise;
    this.est.y=this.robot.y+gaussian(this.rng)*0.025*this.noise;
    this.est.yaw=wrap(this.robot.yaw+gaussian(this.rng)*0.015*this.noise);
    this.est.sigma=0.040;this.lastMarker=mark.node;
    if(this.time-this.lastMarkerTime>2.0){this.log('Marker '+mark.node+' corrected pose');this.lastMarkerTime=this.time;}
    if(mark.node===ROOMS[this.mission[this.stepIndex+1]]&&mark.d<0.40)this.goalConfirmed=true;
   }}
 }
 scanMatch(){
  // Coarse scan matching over nearby candidate poses (a tiny educational model).
  const d=this.scanData.filter(z=>z.range<3.43);
  if(d.length<6){this.log('360 scan: insufficient stable walls');return;}
  let best=null;const e=this.est;
  for(let dx=-0.24;dx<=0.241;dx+=0.08)for(let dy=-0.24;dy<=0.241;dy+=0.08)for(let da=-0.13;da<=0.131;da+=0.065){
    let score=0;
    for(const m of d){const expected=ray(e.x+dx,e.y+dy,m.yaw+da,3.5,[]);let residual=Math.abs(expected-m.range);score+=Math.min(residual,0.5)**2;}
    if(!best||score<best.score)best={score,dx,dy,da};
  }
  if(best&&best.score/d.length<0.022){this.est.x+=best.dx*0.5;this.est.y+=best.dy*0.5;this.est.yaw=wrap(this.est.yaw+best.da*0.6);this.est.sigma=Math.max(0.075,Math.min(this.est.sigma,0.13));this.log('Kratos matched 360 scan to saved hallway map');}
  else this.log('Scan geometry ambiguous; kept odometry estimate');
 }
 pauseVehicle(){
  if(!this.running||this.complete||this.failed){this.log('Nothing to pause; select a room first');return false;}
  if(this.operatorPaused)return true;
  this.operatorPaused=true;this.out=[0,0,0,0,0];this.mode='PAUSED';
  this.log('PAUSED — route and upcoming stops preserved; wheel targets zero');
  return true;
 }
 resumeVehicle(){
  if(!this.operatorPaused)return false;
  if(!this.wifi||!this.tofHealthy||this.estop||this.estopLatched||!this.localized||this.est.sigma>0.65){
   this.log('Resume refused: link, sensors, E-stop or localization not ready');return false;
  }
  this.operatorPaused=false;this.log('RESUMED — continuing toward IS '+this.mission[this.stepIndex+1]);return true;
 }
 tick(dt=0.08){
  if(!this.running||this.complete||this.failed)return;
  this.time+=dt;
  // Synthetic 1S LiPo model; the physical firmware needs a calibrated ADC input.
  this.batteryVoltage=Math.max(3.05,this.batteryVoltage-dt*(0.000018+(this.running&&!this.operatorPaused?0.00010:0)));
  if(this.batteryVoltage<3.48&&!this.lowBatteryStop){this.lowBatteryStop=true;if(this.activeLeg)this.finishLeg('battery safety stop');this.log('Battery below conservative stop threshold; motors commanded to zero');}

  const active=this.wifi;this.heartbeatAge=active?0.07:this.heartbeatAge+dt;
  const old={...this.robot};this.sense();
  let target=this.currentTarget();
  if(!this.operatorPaused&&target&&!this.scanning&&Math.hypot(this.est.x-NODES[target][0],this.est.y-NODES[target][1])<0.18){
    if((this.autoScan||this.scanRequested)&&!this.scannedNodes.has(target)&&['C','E','G','H','J','M','N'].includes(target)){
      this.scanning=true;this.scanStart=this.robot.yaw;this.scanTurns=0;this.nextScanAngle=0;this.scanData=[];this.scannedNodes.add(target);this.scanRequested=false;this.log('Stopped at junction '+target+' for 360° scan');
    }else if(this.pathIndex<this.plan.length-1){this.pathIndex++;target=this.currentTarget();}
  }
  if(!this.operatorPaused&&this.scanRequested&&!this.scanning&&this.localized){this.scanning=true;this.scanStart=this.robot.yaw;this.scanTurns=0;this.nextScanAngle=0;this.scanData=[];this.scanRequested=false;this.log('Manual 360° scan requested');}
  let desiredHeading=target?Math.atan2(NODES[target][1]-this.est.y,NODES[target][0]-this.est.x):this.est.yaw;
  let dGoal=target?Math.hypot(NODES[target][0]-this.est.x,NODES[target][1]-this.est.y):0;
  let signal=0;
  if(target&&dGoal<1.5&&this.pathIndex<this.plan.length-1){const n2=this.plan[this.pathIndex+1],dh=Math.atan2(NODES[n2][1]-NODES[target][1],NODES[n2][0]-NODES[target][0]);let a=wrap(dh-desiredHeading);signal=Math.abs(a)>.3?Math.sign(a):0;}
  // Goal is only declared reached if an observed marker agrees with the route endpoint.
  const lastLeg=this.pathIndex>=this.plan.length-1;
  let atGoal=!!target&&lastLeg&&dGoal<0.25;
  let commandMode=this.operatorPaused?0:atGoal?3:this.scanning?2:!this.localized?0:1;
  const inArrive=!this.operatorPaused&&atGoal&&this.goalConfirmed;
  let input=[commandMode,wrap(desiredHeading-this.est.yaw),signal,this.sensor.front,this.tofHealthy?1:0,this.sensor.personConf,this.sensor.personRange,this.sensor.side,!this.localized?(this.scanning?.45:1.2):this.est.sigma,this.heartbeatAge,0.03,0.04,0.03,(this.estop||this.estopLatched)?1:0,inArrive?1:0];
  this.out=this.core.run(input);
  if(this.lowBatteryStop){this.out[0]=0;this.out[1]=0;this.out[2]=4;this.out[3]=2;this.running=false;}
this.mode=this.operatorPaused&&this.out[2]===0?'PAUSED':(LABELS[this.out[2]]||'UNKNOWN');if(this.relocalizeRequested&&[4,5,9].includes(this.out[2])){this.relocalizeRequested=false;this.scanning=false;this.running=false;this.log('Recovery scan aborted by safety controller');}
  if(this.out[2]!==this.prevStatus){
    if([2,3,4,5,6,9].includes(this.out[2]))this.log(this.mode+' — fail-safe motor command = 0');
    if(this.out[2]===7)this.log('Scanning: differential wheels counter-rotate');
    this.prevStatus=this.out[2];
  }
  if(this.out[4])this.log('Arrival chime triggered (original placeholder audio)');
  // Wheel inertia / drive train latency; measured wheel speeds are noisy.
  const tau=0.14;this.robot.lv+=(this.out[0]-this.robot.lv)*Math.min(1,dt/tau);this.robot.rv+=(this.out[1]-this.robot.rv)*Math.min(1,dt/tau);
  let actualL=this.robot.lv*(1+gaussian(this.rng)*0.018*this.noise),actualR=this.robot.rv*(1+gaussian(this.rng)*0.018*this.noise);
  let v=(actualL+actualR)/2,omega=(actualR-actualL)/0.060;
  let nyaw=wrap(this.robot.yaw+omega*dt);this.robot.yaw=nyaw;
  this.robot.x+=v*dt*Math.cos(nyaw);this.robot.y+=v*dt*Math.sin(nyaw);
  this.totalTravel+=Math.abs(v*dt);
  // Encoder + IMU dead reckoning. The error is independent from true vehicle pose.
  const l=actualL+gaussian(this.rng)*0.0035*this.noise;const r=actualR+gaussian(this.rng)*0.0035*this.noise;
  const gyro=omega+0.0006*this.noise+gaussian(this.rng)*0.015*this.noise;
  this.est.yaw=wrap(this.est.yaw+(0.35*gyro+0.65*(r-l)/.060)*dt);
  let odomV=(l+r)/2;this.est.x+=odomV*dt*Math.cos(this.est.yaw);this.est.y+=odomV*dt*Math.sin(this.est.yaw);
  this.est.sigma+=dt*(.00065+Math.abs(v)*.0025)*this.noise;
  if(!this.operatorPaused&&this.scanning){
    this.scanTurns+=Math.abs(omega*dt);
    if(this.scanTurns>=this.nextScanAngle){const rr=ray(this.robot.x,this.robot.y,this.robot.yaw,3.5,[])+gaussian(this.rng)*0.017*this.noise;
      this.scanData.push({yaw:this.robot.yaw,rel:this.scanTurns,range:clamp(rr,0,3.5),x:this.robot.x,y:this.robot.y});this.scans.push({x:this.robot.x+Math.cos(this.robot.yaw)*rr,y:this.robot.y+Math.sin(this.robot.yaw)*rr});this.nextScanAngle+=Math.PI/6;}
    if(this.scanTurns>=2*Math.PI-.12){this.scanning=false;if(this.relocalizeRequested){this.relocalizeRequested=false;this.relocalizationResult=matchSurvey(this.survey,this.scanData);if(this.relocalizationResult.ok){this.applyKnownNode(this.relocalizationResult.node,'scan')}else{this.localized=false;this.running=false;this.robot.lv=0;this.robot.rv=0;this.est.sigma=1.2;this.log('Location unresolved: '+this.relocalizationResult.reason)}}else this.scanMatch();if(this.currentTarget()&&Math.hypot(this.est.x-NODES[this.currentTarget()][0],this.est.y-NODES[this.currentTarget()][1])<0.25)this.pathIndex=Math.min(this.pathIndex+1,this.plan.length-1);this.log('Scan complete ('+this.scanData.length+' headings)');}
  }
  if(!inHall(this.robot.x,this.robot.y,0.07))this.boundaryViolations++;
  for(const o of this.objects())if(Math.hypot(o.x-this.robot.x,o.y-this.robot.y)<o.r+0.064)this.collisions++;
  if(this.out[2]===2)this.waitS+=dt;
  if(this.out[2]===3)this.stops++;
  if(!this.operatorPaused&&this.out[2]===8){this.dwell+=dt;if(this.dwell>1.1){
    const reached=this.mission[this.stepIndex+1];
    if(!this.goalConfirmed){this.log('Arrival denied: no confirmed room marker');return;}
    if(this.activeLeg)this.finishLeg('marker confirmed');
    this.arrivals++;this.completedStops.push(reached);this.currentRoom=reached;this.currentNode=ROOMS[reached];this.stepIndex++;this.log('Confirmed IS '+reached+'; '+(this.stepIndex===this.mission.length-1?'mission complete':'dwell and replan'));
    this.est.x=NODES[ROOMS[reached]][0];this.est.y=NODES[ROOMS[reached]][1];this.est.sigma=.04;
    if(this.stepIndex>=this.mission.length-1){this.complete=true;this.running=false;this.log('Ready at IS '+reached+'; dispatch another room without remapping');}
    else {this.nextLeg();this.activeLeg={from:this.currentRoom,to:this.mission[this.stepIndex+1],start:this.time};}
  }}
  if(this.time>680){this.failed=true;this.log('Simulation exceeded maximum time');}
 }
 snapshot(){return {time:this.time,robot:this.robot,est:this.est,sensor:this.sensor,mode:this.mode,status:this.out[2],signal:this.out[3],path:this.plan,stepIndex:this.stepIndex,mission:this.mission,goal:this.mission[this.stepIndex+1],current:this.currentRoom,complete:this.complete,failed:this.failed,arrivals:this.arrivals,collisions:this.collisions,boundaryViolations:this.boundaryViolations,waitS:this.waitS,lastMarker:this.lastMarker,heartbeatAge:this.heartbeatAge,scans:this.scans,objects:this.objects(),noise:this.noise,scanning:this.scanning,localized:this.localized,relocalizationNode:this.relocalizationNode,relocalizationResult:this.relocalizationResult,surveyAnchors:Object.keys(this.survey?.signatures||{}).length,pending:this.plannedStops(),operatorPaused:this.operatorPaused,estopLatched:this.estopLatched,estopSwitchPressed:this.estopSwitchPressed,dispatchCount:this.dispatchCount,completedStops:[...this.completedStops],running:!!this.running,batteryVoltage:this.batteryVoltage,batteryLow:this.lowBatteryStop,arrivalVerified:!!this.goalConfirmed,tripHistory:[...this.tripHistory]};}
}
