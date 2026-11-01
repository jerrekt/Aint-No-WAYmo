import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeCore,MicroSimulation,newSurvey,recordSurveyAnchor,NODES,ROOMS,route} from '../sim/engine.mjs';
const core=await makeCore(fs.readFileSync(new URL('../sim/controller.wasm',import.meta.url)));
const survey=newSurvey();for(const n of Object.keys(NODES))recordSurveyAnchor(survey,n,17);
const missions=[['214','222'],['214','210'],['224','227','224','210'],['214','222','224','227','210'],['227','214'],['210','222']];
const outcomes=[];
function execute(sim,max=18000){let n=0;while(n++<max&&!sim.complete&&!sim.failed&&sim.running)sim.tick(.08);return {done:sim.complete,failed:sim.failed,t:Math.round(sim.time),collision:sim.collisions,edge:sim.boundaryViolations,arrivals:sim.completedStops,last:sim.logged.at(-1)?.text};}
for(const mission of missions){const sim=new MicroSimulation(core,{mission,survey,autoScan:false});sim.start();outcomes.push({mission:mission.join('→'),...execute(sim)});}
{
 const sim=new MicroSimulation(core,{mission:['214'],survey,autoScan:false});
 assert(sim.addStop('222'));assert(sim.addStop('224'));assert(sim.addStop('210'));
 const r=execute(sim);outcomes.push({mission:'queued 200→230→251→202',...r});
 assert.deepEqual(sim.completedStops,['222','224','210']);assert(sim.complete);
 assert(sim.addStop('214'),'New trip from last stop should work');const next=execute(sim);
 outcomes.push({mission:'later 202→200',...next});assert(next.done);
}
{
 const sim=new MicroSimulation(core,{mission:['214'],survey,autoScan:false});assert(sim.addStop('222'));
 for(let i=0;i<70;i++)sim.tick(.08);
 assert(sim.goNow('217'),'Override should work while moving');
 const r=execute(sim);outcomes.push({mission:'Go now 200→210 mid trip',...r});
}
{
 const sim=new MicroSimulation(core,{mission:['214'],survey,autoScan:false});
 sim.addStop('222');sim.wifi=false;for(let i=0;i<20;i++)sim.tick(.08);
 assert(sim.out[0]===0&&sim.out[1]===0);
 assert(!sim.goNow('224'));outcomes.push({mission:'MQTT lost - no dispatch',status:sim.mode});
}
console.table(outcomes);
fs.writeFileSync(new URL('v6_results.json',import.meta.url),JSON.stringify(outcomes,null,2));
assert(outcomes.slice(0,6).some(x=>x.done));
console.log('Room labels:',Object.keys(ROOMS));
