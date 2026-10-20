from playwright.sync_api import sync_playwright
import os
src=os.environ.get('KP_OUT','/mnt/user-data/outputs/KP.html')
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file://'+src); pg.wait_for_timeout(600)
    pg.pdf(path=src[:-5]+'.pdf', format='A4', landscape=True, print_background=True, margin={'top':'0','right':'0','bottom':'0','left':'0'})
    b.close()
