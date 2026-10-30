import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
HTML=(Path(__file__).resolve().parents[1]/'Mini_Waymo_V12_Demo.html').read_text()
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  page=await browser.new_page(viewport={'width':1536,'height':900})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content(HTML,wait_until='domcontentloaded',timeout=60000)
  await page.wait_for_timeout(350)
  assert await page.locator('#vehicleRail .dispatchCard #goNow').count()==1
  assert await page.locator('#centerRail #map').count()==1
  assert await page.locator('#taskRail .teamMini').count()==6
  assert await page.locator('#railBuildPercent').inner_text()=='25%'
  await page.locator('#roomSelect').select_option('263')
  await page.locator('#goNow').click()
  await page.wait_for_timeout(350)
  print('AFTER GO',await page.locator('#status').inner_text(),await page.locator('#destination').inner_text())
  await page.locator('#pauseRoute').click()
  await page.wait_for_timeout(150)
  print('AFTER PAUSE',await page.locator('#status').inner_text(),await page.locator('#pauseRoute').inner_text())
  await page.locator('#holdRoute').click()
  await page.wait_for_timeout(150)
  print('AFTER STOP',await page.locator('#status').inner_text())
  await page.locator('#openBuildBoard').click()
  assert await page.locator('#teamBuildDetails').evaluate('(el)=>el.open')
  print('BUILD',await page.locator('#taskBoardGroups').count(), await page.locator('#aboutPage').is_visible())
  await page.locator('#dockMap').click()
  assert await page.locator('#dashboardPage').is_visible()
  await page.locator('#dockTeam').click()
  assert await page.locator('#aboutPage').is_visible()
  await page.locator('.appearanceMenu>summary').click()
  print('SETTINGS',await page.locator('.appearanceMenu').evaluate('(e)=>e.open'),await page.locator('#guestBtn').count())
  assert not errors,errors
  await browser.close()
asyncio.run(main())
