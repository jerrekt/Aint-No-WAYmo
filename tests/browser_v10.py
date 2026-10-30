from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1400,'height':1000},device_scale_factor=1,accept_downloads=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((root/'Mini_Waymo_V10_Demo.html').read_text(),wait_until='load')
 page.wait_for_timeout(550)
 assert page.locator('#roomSelect').input_value()=='263'
 assert page.locator('#batteryLevel').inner_text().endswith('V')
 assert 'Not yet confirmed' in page.locator('#arrivalState').inner_text()
 page.locator('#goNow').click();page.wait_for_timeout(160)
 assert '263' in page.locator('#destination').inner_text()
 page.locator('#roomSelect').select_option('251');page.locator('#addStop').click();assert '251' in page.locator('#queueLive').inner_text()
 page.locator('#pauseRoute').click();page.wait_for_timeout(110);assert 'PAUSED' in page.locator('#status').inner_text()
 page.locator('#pauseRoute').click();page.wait_for_timeout(100)
 page.locator('#recoverQuick').click();page.wait_for_timeout(100)
 page.locator('#advancedPanel > summary').click()
 page.locator('#noMarkers').check();page.locator('#dropNode').select_option('I');page.locator('#drop').click();page.wait_for_timeout(100)
 assert page.locator('#location').inner_text()=='UNKNOWN'
 page.locator('#recoverQuick').click();page.wait_for_timeout(100)
 assert page.locator('#location').inner_text()=='UNKNOWN'
 page.locator('#noMarkers').uncheck();page.locator('#recoverQuick').click();page.wait_for_timeout(100)
 assert page.locator('#location').inner_text()=='IS 251'
 page.locator('#guestBtn').click();assert page.locator('#recoverQuick').is_disabled()
 page.locator('#adminBtn').click();assert page.locator('#recoverQuick').is_enabled()
 page.screenshot(path=str(root/'v10_dashboard_preview.png'),full_page=True)
 assert not errors,errors
 print('Browser V10 dashboard: Go IS263, queue, pause, front recovery, guest, battery and arrival UI passed')
 fit=browser.new_page(viewport={'width':1250,'height':900},accept_downloads=True)
 fiterr=[];fit.on('pageerror',lambda e:fiterr.append(str(e)))
 fit.set_content((root/'Mini_Waymo_Fit_Planner.html').read_text(),wait_until='load')
 fit.wait_for_timeout(300)
 assert 'Footprints' in fit.locator('#fits').inner_text() or 'Fit is not established' in fit.locator('#fits').inner_text()
 fit.locator('#innerW').fill('15');fit.locator('#innerW').dispatch_event('input');fit.wait_for_timeout(75)
 assert 'exceeds' in fit.locator('#fits').inner_text() or 'overlaps' in fit.locator('#fits').inner_text()
 fit.screenshot(path=str(root/'v10_fit_planner_preview.png'),full_page=True)
 assert not fiterr,fiterr
 print('Browser fit planner: dimensions change, conflicts and scale render passed')
 browser.close()
