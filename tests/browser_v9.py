from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1390,'height':960},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
 page.set_content((root/'mini_waymo_micro_v9_demo.html').read_text(),wait_until='load');page.wait_for_timeout(450)
 assert page.locator('#roomSelect').input_value()=='227'
 assert 'Go to IS 227' in page.locator('#goNow').inner_text()
 page.locator('#goNow').click();page.wait_for_timeout(200)
 assert page.locator('#destination').inner_text()=='IS 227'
 page.locator('#roomSelect').select_option('224');page.locator('#addStop').click()
 assert '224' in page.locator('#queueLive').inner_text()
 page.locator('#pauseRoute').click();page.wait_for_timeout(180)
 assert page.locator('#status').inner_text()=='PAUSED'
 page.locator('#pauseRoute').click();page.wait_for_timeout(150)
 page.locator('#hardEstop').click();page.wait_for_timeout(100)
 assert page.locator('#status').inner_text()=='E-STOP LATCHED'
 assert page.locator('#goNow').is_disabled()
 page.locator('#advancedPanel > summary').click()
 page.locator('#resetEstop').click();page.wait_for_timeout(70)
 assert page.locator('#goNow').is_disabled(), 'reset requires releasing switch'
 page.locator('#releaseEstop').click();page.locator('#resetEstop').click();page.wait_for_timeout(100)
 assert page.locator('#goNow').is_enabled()
 assert page.locator('#status').inner_text()!='DRIVING','reset must not auto-resume'
 page.locator('#roomSelect').select_option('227');page.locator('#goNow').click();page.wait_for_timeout(120)
 assert page.locator('#destination').inner_text()=='IS 227'
 page.locator('#dropNode').select_option('I');page.locator('#drop').click();page.wait_for_timeout(100)
 assert page.locator('#location').inner_text()=='IS 224','automatic unique marker recovery should recognize IS224'
 assert 'AUTO RECOVERY' in page.locator('#events').text_content()
 page.locator('#noMarkers').check();page.locator('#drop').click();page.wait_for_timeout(100)
 assert page.locator('#location').inner_text()=='UNKNOWN'
 page.locator('#goNow').click();page.wait_for_timeout(70)
 assert page.locator('#location').inner_text()=='UNKNOWN','must not dispatch before localization'
 page.locator('#guestBtn').click()
 assert page.locator('#hardEstop').is_disabled() and page.locator('#goNow').is_disabled()
 page.locator('#adminBtn').click()
 page.screenshot(path=str(root/'assets/preview_v9.png'),full_page=True)
 assert not errors,errors
 print('Browser V9: Go IS227, queue, Pause, latched simulated E-stop, manual reset, auto marker and guest tests passed')
 browser.close()
