from pathlib import Path
import json, re
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
page_source=(root/'Mini_Waymo_V12_Demo.html').read_text()
loader=page_source.split('// V11: read team_members.json when hosted;',1)[1].split('// V11: public About page.',1)[0]
loader='// V11: read team_members.json when hosted;'+loader
# Browser network traffic to localhost is restricted in this execution environment.
# Emulate a successful same-origin JSON request to exercise DOM rendering safely.
loader=loader.replace('if (!/^https?:$/.test(location.protocol)) return;','// simulated hosted origin for unit test')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page()
 page.set_content((root/'Mini_Waymo_V12_About.html').read_text())
 members=json.loads((root/'team_members.json').read_text())
 members.append({'name':'Future Teammate','role':'Testing & documentation','url':''})
 page.evaluate('(members)=>{window.fetch=async()=>({ok:true,json:async()=>members})}',members)
 page.evaluate(loader)
 page.wait_for_timeout(70)
 assert page.locator('#aboutTeamRoster .teamPerson').count()==7
 assert 'Future Teammate' in page.locator('#aboutTeamRoster').inner_text()
 print('PASS mocked hosted roster loader updates team cards from JSON')
 b.close()
