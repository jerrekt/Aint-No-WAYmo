from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
roster=json.loads((root/'team_members.json').read_text())
assert len(roster)==6
for f in ['Mini_Waymo_V12_Demo.html','Mini_Waymo_V12_About.html']:
    s=(root/f).read_text()
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page()
        page.set_content(s)
        for name,link in [('Branden Adsuara','https://bja.adsuaracloud.com/'),('Branden Adsuara','https://www.linkedin.com/in/brandenjga/'),('Noah Zerarka','https://www.linkedin.com/in/noahzerarka/'),('Gage Watts','https://www.linkedin.com/in/gage-watts-30b30634a/')]:
            card=page.locator('.teamPerson',has=page.locator('h3',has_text=name))
            assert card.locator(f'a[href="{link}"]').count()==1,(f,name,link)
            assert 'SJSU SME' in card.locator('.teamAffiliation').inner_text()
        browser.close()
print('PASS standalone and dashboard fallback cards and SJSU SME affiliation')
