import sys, pathlib
from playwright.sync_api import sync_playwright
SRC = pathlib.Path('/home/mm/Документы/app-design/ui-research/14-recipes/examples')
OUT = pathlib.Path(sys.argv[1])
pages = ['01-table-with-filters','02-form','03-dashboard','04-empty-state','05-modal','06-settings','07-object-page']
with sync_playwright() as p:
    b = p.chromium.launch(args=['--disable-gpu'])
    for scheme in ('light','dark'):
        ctx = b.new_context(viewport={'width':1440,'height':900}, device_scale_factor=1, color_scheme=scheme, reduced_motion='reduce')
        pg = ctx.new_page()
        for name in pages:
            pg.goto((SRC/f'{name}.html').as_uri(), wait_until='load')
            pg.wait_for_timeout(600)
            pg.screenshot(path=str(OUT/f'{name}_{scheme}_1440x900.png'))
            print('ok', name, scheme, flush=True)
        ctx.close()
    b.close()
