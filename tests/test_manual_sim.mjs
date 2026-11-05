import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeCore,MicroSimulation,newSurvey,recordSurveyAnchor,NODES} from '../sim/engine.mjs';
const core=await makeCore(fs.readFileSync(new URL('../sim/controller.wasm',import.meta.url)));
const survey=newSurvey();for(const n of Object.keys(NODES))recordSurveyAnchor(survey,n,17);
const sim=new MicroSimulation(core,{mission:['214'],survey,seed:7});
const start={...sim.robot};
// Forward with no steer moves the car and marks it off route.
for(let i=0;i<40;i++)sim.manualStep(.08,1,0);
const moved=Math.hypot(sim.robot.x-start.x,sim.robot.y-start.y);
assert.ok(moved>0.3,'manual forward should move the car, moved '+moved);
assert.ok(sim.snapshot().offRoute&&sim.snapshot().manual);
// Steering turns it; it never turns in place (no motion when throttle is zero).
const y0=sim.robot.yaw;for(let i=0;i<30;i++)sim.manualStep(.08,0,1);
for(let i=0;i<10;i++)sim.manualStep(.08,0,1);
const p0={...sim.robot};for(let i=0;i<10;i++)sim.manualStep(.08,0,1);
assert.equal(sim.robot.x,p0.x);assert.equal(sim.robot.yaw,p0.yaw);
for(let i=0;i<20;i++)sim.manualStep(.08,.6,1);
assert.ok(Math.abs(sim.robot.yaw-y0)>0.2,'steer should turn while moving');
// Holding full throttle for a long time never leaves the hallway.
for(let i=0;i<2000;i++)sim.manualStep(.08,1,i%400<200?0:.3);
assert.equal(sim.boundaryViolations,0);
// E-stop: no motion.
sim.pressEstop();const p1={...sim.robot};for(let i=0;i<20;i++)sim.manualStep(.08,1,0);
assert.equal(sim.robot.x,p1.x);assert.equal(sim.robot.y,p1.y);assert.match(sim.mode,/E-stop/);
sim.releaseEstopSwitch();sim.localResetEstop();
// Lost link: no motion.
sim.wifi=false;const p2={...sim.robot};for(let i=0;i<20;i++)sim.manualStep(.08,1,0);
assert.equal(sim.robot.x,p2.x);sim.wifi=true;
// After manual, a trip plans from where the car is, even back to the last room.
// (A car left nose-to-wall would sit in OBSTACLE STOP until driven back out, like the real one.)
const sim2=new MicroSimulation(core,{mission:['214'],survey,seed:7});
for(let i=0;i<40;i++)sim2.manualStep(.08,1,0);
sim2.manualEnd();
assert.ok(sim2.goNow('214'),'go to the last room after manual drive');
for(let i=0;i<4000&&!sim2.complete;i++)sim2.tick(.08);
assert.ok(sim2.complete,'trip after manual drive completes: '+sim2.mode);assert.equal(sim2.currentRoom,'214');
assert.equal(sim2.snapshot().offRoute,false);
// Manual drive refused while a trip runs.
sim2.goNow('222');assert.equal(sim2.manualStep(.08,1,0),false);
console.log('Manual sim: forward, steer, no turn in place, stays in hall, E-stop, link loss, trip after manual, refused mid-trip all pass');
