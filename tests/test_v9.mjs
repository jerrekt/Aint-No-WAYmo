import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeCore,MicroSimulation,newSurvey,recordSurveyAnchor,NODES} from '../sim/engine.mjs';
const core=await makeCore(fs.readFileSync(new URL('../sim/controller.wasm',import.meta.url)));
const survey=newSurvey();for(const n of Object.keys(NODES))recordSurveyAnchor(survey,n,17);
// Primary go-now dispatch from initial position; queue is replaced only by override
{
 const sim=new MicroSimulation(core,{mission:['200'],survey});
 assert(sim.goNow('263')); assert.deepEqual(sim.plannedStops(),['263']);
 assert(sim.addStop('251')); assert.deepEqual(sim.plannedStops(),['263','251']);
 assert(sim.goNow('263')); assert.deepEqual(sim.plannedStops(),['263']);
}
// On relocation, a unique visible landmark restores position automatically
{
 const sim=new MicroSimulation(core,{mission:['200'],survey});
 sim.placeUnknown('I');
 assert.equal(sim.localized,true); assert.equal(sim.currentRoom,'251');
 assert.equal(sim.scanning,false);assert.equal(sim.running,false);
 assert(sim.goNow('263'));
}
// No markers means robot refuses dispatch; recovery scan can be offered only via explicit operator input
{
 const sim=new MicroSimulation(core,{mission:['200'],survey});
 sim.markersEnabled=false;sim.placeUnknown('I');
 assert.equal(sim.localized,false);assert.equal(sim.running,false);
 assert.equal(sim.goNow('263'),false);
 assert(sim.beginRelocalize());
}
// E-stop must latch even after releasing switch, block go/resume, require local explicit reset
{
 const sim=new MicroSimulation(core,{mission:['200'],survey});
 assert(sim.goNow('263'));assert(sim.addStop('251'));
 sim.pressEstop(); assert.equal(sim.mode,'E-STOP LATCHED');
 assert.deepEqual([sim.robot.lv,sim.robot.rv],[0,0]);
 assert.equal(sim.goNow('202'),false);
 assert.equal(sim.localResetEstop(),false);
 sim.releaseEstopSwitch();assert.equal(sim.estopLatched,true);
 assert.equal(sim.goNow('202'),false);
 assert.equal(sim.localResetEstop(),true);
 assert.equal(sim.running,false); assert.deepEqual(sim.plannedStops(),[]);
 assert(sim.goNow('263'));
}
console.log('V9: immediate IS263, queue override, automatic marker recovery, uncertain-location stop, physical E-stop latch/reset passed');
