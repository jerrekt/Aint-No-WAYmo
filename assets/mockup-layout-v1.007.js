/* Ain't No Waymo V1.008 DRAFT — presentation-only DOM rearrangement.
 * Move existing elements rather than cloning so original simulator event listeners persist.
 */
(function(){
  const dashboard=document.getElementById('dashboardPage');
  const about=document.getElementById('aboutPage');
  if(!dashboard||!about||dashboard.dataset.mockLayout==='ready')return;
  const hero=dashboard.querySelector('.appScene');
  const columns=dashboard.querySelectorAll(':scope > .column');
  if(columns.length!==2||!hero)return;
  const [leftOld,controlsOld]=columns;
  const mapCard=leftOld.querySelector(':scope > section.card');
  const dispatch=controlsOld.querySelector('.dispatchCard');
  if(!mapCard||!dispatch)return;

  const make=(tag,cls,id)=>{const n=document.createElement(tag);n.className=cls;if(id)n.id=id;return n};
  const vehicle=make('aside','mockRail','vehicleRail');
  const center=make('div','mockRail','centerRail');
  const rail=make('aside','mockRail','taskRail');
  vehicle.setAttribute('aria-label','Vehicle and dispatch controls');
  center.setAttribute('aria-label','Navigation map and telemetry');
  rail.setAttribute('aria-label','Project progress and team');

  const title=document.createElement('div'); title.className='mapHeadTitle';
  title.innerHTML='<div><h2>IS Building — Second Floor</h2><p>Mini-Waymo navigation map · estimated survey</p></div><span class="simFlag">SIMULATED ROUTE</span>';
  mapCard.insertBefore(title,mapCard.firstChild);

  // Selected car comes from the real user-supplied diecast reference photograph.
  const reference=hero.querySelector('.sceneArt');
  if(reference){
    const preferred=document.getElementById('waymoActualDiecastAsset');
    if(preferred)reference.src=preferred.textContent.trim();
    reference.alt='User-provided reference image of the white Waymo Jaguar I-PACE miniature on its display base; not the finished autonomous robot';
  }
  const words=hero.querySelector('.sceneWords');
  if(words){words.innerHTML='<div class="vehicleMeta"><div><h2>Mini-Waymo · Diecast</h2><p>SJSU SME engineering prototype</p></div><span class="simFlag">SIM ONLY</span></div>'}
  const sceneLabel=hero.querySelector('.sceneLabel');if(sceneLabel)sceneLabel.textContent='SELECTED DIECAST · REFERENCE';

  // Keep original action buttons with their original handlers.
  vehicle.appendChild(hero); vehicle.appendChild(dispatch);
  const metrics=leftOld.querySelector(':scope > .metrics');if(metrics)vehicle.appendChild(metrics);
  for(const child of Array.from(leftOld.children))center.appendChild(child);
  for(const child of Array.from(controlsOld.children))center.appendChild(child);
  leftOld.remove();controlsOld.remove();

  const p=document.getElementById('projectProgressPercent');
  const raw=p?p.textContent.trim():'25%';
  const totalData=document.getElementById('boardTasksFallback');
  let tasks=[];try{tasks=JSON.parse(totalData.textContent).tasks||[]}catch(e){}
  const statusCount={done:0,in_progress:0,blocked:0,todo:0};
  tasks.forEach(t=>{if(Object.prototype.hasOwnProperty.call(statusCount,t.status))statusCount[t.status]++});
  const rows=[['done','Completed'],['in_progress','In progress'],['todo','Not started'],['blocked','Blocked']];
  const build=make('section','mockPanel','quickBuild');
  build.innerHTML='<div class="railHead"><h2 class="railHeading">Build Status</h2><button type="button" id="quickBuildArrow" aria-label="Open full build checklist">›</button></div><div class="buildRing" id="railBuildRing"><div class="buildRingInner"><strong id="railBuildPercent"></strong><span>Verified milestones</span></div></div><div class="statusRows" id="railTaskCounts"></div><p class="railFoot" id="railStatusSource">Task counts use the local preview until the Kratos API is connected.</p><button class="railButton" type="button" id="openBuildBoard"><span>☷ &nbsp; View All Tasks</span><span aria-hidden="true">›</span></button>';
  rail.appendChild(build);
  const rowsElm=build.querySelector('#railTaskCounts');
  rowsElm.innerHTML=rows.map(([status,label])=>'<div class="statusRow"><i class="countDot '+(status==='in_progress'?'progress':status)+'"></i><span>'+label+'</span><strong>'+statusCount[status]+'</strong></div>').join('');
  const updateGauge=()=>{const v=(p?p.textContent:raw).trim()||'25%';const m=v.match(/\d+(?:\.\d+)?/);const pct=m?Math.min(100,Math.max(0,Number(m[0]))):25;build.querySelector('#railBuildPercent').textContent=Math.round(pct)+'%';build.querySelector('#railBuildRing').style.background='conic-gradient(#65e7c9 0 '+pct+'%,#334b64 '+pct+'% 100%)'};
  updateGauge();if(p&&window.MutationObserver)new MutationObserver(updateGauge).observe(p,{childList:true,subtree:true,characterData:true});

  const team=make('section','mockPanel','quickTeam');
  team.innerHTML='<div class="railHead"><h2 class="railHeading">The Team</h2><span style="color:#86c1fa;font-size:11px;font-weight:750">SJSU SME</span></div><div class="teamMiniList" id="teamMiniList"></div><button type="button" class="railButton" id="openTeamInfo"><span>Meet the full team</span><span aria-hidden="true">›</span></button>';
  rail.appendChild(team);
  const sourcePeople=Array.from(document.querySelectorAll('#aboutTeamRoster .teamPerson'));
  const destTeam=team.querySelector('#teamMiniList');
  sourcePeople.forEach((card,i)=>{
    const name=(card.querySelector('h3')?.textContent||'Team member').trim();
    const role=(card.querySelector('.role')?.textContent||'Role to be confirmed').trim();
    const initials=(card.querySelector('.teamAvatar')?.textContent||'TM').trim();
    const b=document.createElement('button');b.type='button';b.className='teamMini';b.dataset.index=i;
    const init=document.createElement('span');init.className='initials'+(i===0?' me':'');init.textContent=initials;
    const meta=document.createElement('span');meta.style.flex='1';
    const nm=document.createElement('div');nm.className='personName';nm.textContent=name;
    const rl=document.createElement('div');rl.className='personRole';rl.textContent=role;
    const arrow=document.createElement('span');arrow.className='chevron';arrow.textContent='›';
    meta.append(nm,rl);b.append(init,meta,arrow);destTeam.appendChild(b);
    b.addEventListener('click',()=>openAboutElement(card));
  });
  dashboard.replaceChildren(vehicle,center,rail);
  dashboard.dataset.mockLayout='ready';

  const mapBtn=document.getElementById('navDashboard');
  const aboutBtn=document.getElementById('navAbout');
  function openAboutElement(element){aboutBtn?.click();setTimeout(()=>element?.scrollIntoView({behavior:'smooth',block:'start'}),80)}
  function openBoard(){aboutBtn?.click();const d=document.getElementById('teamBuildDetails');if(d)d.open=true;setTimeout(()=>d?.scrollIntoView({behavior:'smooth',block:'start'}),80)}
  document.getElementById('quickBuildArrow')?.addEventListener('click',openBoard);
  document.getElementById('openBuildBoard')?.addEventListener('click',openBoard);
  document.getElementById('openTeamInfo')?.addEventListener('click',()=>openAboutElement(document.getElementById('aboutTeamRoster')));

  const oldDock=document.querySelector('.appDock');
  if(oldDock){
    const theme=document.getElementById('dockTheme');const aboutDock=document.getElementById('dockAbout');
    const car=make('button','dockButton dockCar','dockCar');car.type='button';car.innerHTML='<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 14 6 9c.3-1 1.2-1.5 2.3-1.5h7.4c1.1 0 2 .5 2.3 1.5l2 5"></path><path d="M3 14h18v5H3z"></path><circle cx="7" cy="19" r="1.5"></circle><circle cx="17" cy="19" r="1.5"></circle></svg><span>My Car</span>';
    car.addEventListener('click',()=>{mapBtn?.click();setTimeout(()=>hero.scrollIntoView({behavior:'smooth',block:'center'}),70)});
    const teamButton=make('button','dockButton','dockTeam');teamButton.type='button';teamButton.innerHTML='<svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="8" cy="8" r="3"></circle><circle cx="17" cy="9" r="2.5"></circle><path d="M2 21v-3a6 6 0 0 1 12 0v3M14 16a5 5 0 0 1 8 4v1"></path></svg><span>Team</span>';
    teamButton.addEventListener('click',()=>openAboutElement(document.getElementById('aboutTeamRoster')));
    oldDock.insertBefore(car,aboutDock);
    oldDock.appendChild(teamButton);
    if(theme)theme.remove();
  }

  // Always use the user's original SJSU and SME marks; the header uses dedicated
  // transparent dark-background variants, not white logo badges or text impostors.
  const head=document.querySelector('header .headerRight');
  if(head){
    const logos=make('div','headerLogos');
    logos.setAttribute('aria-label','San Jose State University and SJSU SME');
    for(const [identifier,cssClass,alt] of [
      ['headerSJSUAsset','sjsuHeader','San José State University'],
      ['headerSMEAsset','smeHeader','SJSU Society of Manufacturing Engineers']
    ]){
      const asset=document.getElementById(identifier);
      if(!asset)continue;
      const img=document.createElement('img');
      img.src=asset.textContent.trim();
      img.className=cssClass;
      img.alt=alt;
      img.decoding='async';
      logos.appendChild(img);
    }
    head.prepend(logos);
  }
  // The user locked the app-style design: repurpose the gear into useful
  // demo view-mode controls rather than keeping unused colorways.
  try{document.body.dataset.colorway='app';localStorage.setItem('waymoColorwayV1005','app')}catch(e){document.body.dataset.colorway='app'}
  const settings=document.querySelector('header .appearanceMenu');
  const roles=document.querySelector('header .headerRight .roles');
  if(settings){
    const summary=settings.querySelector('summary');
    if(summary){summary.textContent='Settings';summary.setAttribute('aria-label','Demo view settings');summary.title='Demo view settings'}
    const chooser=settings.querySelector('.colorwayChooser');
    if(chooser){
      chooser.replaceChildren();
      const heading=document.createElement('div');heading.className='settingsLabel';heading.textContent='Simulator display mode';
      chooser.appendChild(heading);
      if(roles){chooser.appendChild(roles);roles.style.display='flex'}
      const note=document.createElement('p');note.className='settingsNote';note.textContent='Admin / Guest affects this offline preview only. Real vehicle controls require backend authorization.';chooser.appendChild(note);
    }
  }
  const titleText=document.querySelector('header .brandWordmark .brandSubtitle');if(titleText)titleText.textContent='Mini-Waymo · SJSU SME';
  const ver=document.querySelector('header .version');if(ver)ver.textContent='V1.008 · DRAFT';
  document.title="Ain't No Waymo | V1.008 Draft";
})();
