from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path('/mnt/data/mini_waymo_micro_v11')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1440,'height':1000})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((root/'Mini_Waymo_V11_Demo.html').read_text(),wait_until='load');page.wait_for_timeout(500)
 assert page.locator('#dashboardPage').is_visible()
 assert page.locator('#roomSelect').input_value()=='263'
 page.locator('#navAbout').click()
 assert page.locator('#aboutPage').is_visible()
 assert not page.locator('#dashboardPage').is_visible()
 assert page.locator('.aboutTable tbody tr').count()==7
 assert page.locator('#aboutTeamRoster .teamPerson').count()==3
 for name in ['Branden Adsuara','Noah Zerarka','Gage Watts']:
  assert name in page.locator('#aboutTeamRoster').inner_text()
 page.screenshot(path=str(root/'v11_about_preview.png'),full_page=True)
 page.locator('#navDashboard').click()
 assert page.locator('#dashboardPage').is_visible()
 page.locator('#goNow').click();page.wait_for_timeout(120)
 assert '263' in page.locator('#destination').inner_text()
 page.locator('#guestBtn').click();page.locator('#navAbout').click();assert page.locator('#aboutPage').is_visible()
 page.locator('#navDashboard').click();assert page.locator('#goNow').is_disabled()
 assert not errors,errors
 print('PASS desktop about, team, table, guest, immediate dispatch, back navigation')
 mobile=b.new_page(viewport={'width':390,'height':844})
 mobile.set_content((root/'Mini_Waymo_V11_Demo.html').read_text(),wait_until='load');mobile.wait_for_timeout(450)
 mobile.locator('#navAbout').click()
 assert mobile.locator('#aboutPage').is_visible()
 overflow=mobile.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
 assert overflow<12,f'overflow {overflow}'
 mobile.screenshot(path=str(root/'v11_about_mobile.png'),full_page=True)
 print('PASS mobile about, no document overflow')
 standalone=b.new_page();standalone.set_content((root/'Mini_Waymo_About.html').read_text(),wait_until='load');assert standalone.locator('#aboutPage').is_visible()
 print('PASS standalone about page')
 b.close()
