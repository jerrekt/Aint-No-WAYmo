from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
p=root/'mini_waymo_micro_v8_demo.html'
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1380,'height':920},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(p.read_text(),wait_until='load');page.wait_for_timeout(350)
 assert page.locator('#surveyStatus').text_content()=='16 / 16'
 assert page.locator('#pauseRoute').is_disabled(), 'Pause should be unavailable before trip'
 page.locator('#roomSelect').select_option('230');page.locator('#goNow').click()
 page.wait_for_timeout(150)
 assert page.locator('#pauseRoute').is_enabled()
 assert page.locator('#destination').inner_text()=='IS 230'
 page.locator('#pauseRoute').click();page.wait_for_timeout(350)
 assert page.locator('#status').inner_text()=='PAUSED'
 assert 'Resume' in page.locator('#pauseRoute').inner_text()
 assert page.locator('#leftMotor').text_content()=='0.000 m/s'
 assert page.locator('#rightMotor').text_content()=='0.000 m/s'
 page.locator('#roomSelect').select_option('251');page.locator('#addStop').click()
 assert '251' in page.locator('#queueLive').inner_text()
 assert page.locator('#status').inner_text()=='PAUSED', 'Queue editing must not resume'
 page.locator('#pauseRoute').click();page.wait_for_timeout(200)
 assert page.locator('#status').inner_text()!='PAUSED'
 assert 'Pause' in page.locator('#pauseRoute').inner_text()
 page.locator('#pauseRoute').click();page.wait_for_timeout(150)
 assert page.locator('#status').inner_text()=='PAUSED'
 page.locator('#guestBtn').click()
 assert page.locator('#pauseRoute').is_disabled()
 page.locator('#adminBtn').click()
 page.locator('#holdRoute').click()
 assert page.locator('#status').inner_text()=='HELD — READY'
 assert page.locator('#pauseRoute').is_disabled()
 page.locator('#roomSelect').select_option('263');page.locator('#goNow').click();page.wait_for_timeout(110)
 assert page.locator('#destination').inner_text()=='IS 263'
 page.screenshot(path=str(root/'assets/preview_v8.png'),full_page=True)
 assert not errors,errors
 print('Browser V8 pause/resume, queue preservation, stop and guest tests passed')
 browser.close()
