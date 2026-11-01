import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeCore,MicroSimulation,newSurvey,recordSurveyAnchor,NODES} from '../sim/engine.mjs';
const c=await makeCore(fs.readFileSync(new URL('../sim/controller.wasm',import.meta.url)));
const survey=newSurvey();for(const n of Object.keys(NODES))recordSurveyAnchor(survey,n,17);
{
 let s=new MicroSimulation(c,{mission:['214'],survey});
 assert(s.goNow('227'));assert.deepEqual(s.plannedStops(),['227']);
 assert(s.addStop('224'));assert(s.goNow('222'));assert.deepEqual(s.plannedStops(),['222']);
 assert(s.activeLeg?.to==='222');assert(s.tripHistory.some(t=>t.result==='rerouted'));
}
{
 let s=new MicroSimulation(c,{mission:['214'],survey});
 s.batteryVoltage=3.54;assert.equal(s.goNow('227'),false);
 s.batteryVoltage=4.12;assert(s.goNow('227'));s.batteryVoltage=3.47;s.tick(.08);
 assert(s.lowBatteryStop);assert.equal(s.running,false);assert(s.tripHistory.some(t=>t.result==='battery safety stop'));
 assert.equal(s.out[0],0);assert.equal(s.out[1],0);
}
{
 let s=new MicroSimulation(c,{mission:['214'],survey});s.markersEnabled=false;s.placeUnknown('I');
 assert.equal(s.localized,false);assert.equal(s.recoverNow(),false);
 s.markersEnabled=true;assert.equal(s.recoverNow(),true);assert.equal(s.currentRoom,'224');
 assert.equal(s.scanning,false);
}
{
 let s=new MicroSimulation(c,{mission:['214','210'],survey});assert(s.start());
 let count=0;while(!s.complete&&!s.failed&&count++<20000)s.tick(.08);
 assert(s.complete);assert(s.tripHistory.some(t=>t.to==='210'&&t.result==='marker confirmed'));
 assert(s.snapshot().batteryVoltage>3.55);
}
console.log('V10 controller/simulator: override history, low-battery lockout, stop, marker recovery and verified arrival history pass');
