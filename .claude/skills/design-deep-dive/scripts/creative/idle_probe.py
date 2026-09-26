#!/usr/bin/env python3
"""J/02 · зонд «рисует ли холст в покое» — два снимка счётчика вызовов WebGL внутри одной паузы (агент J · 2026-09-25).

Доказательство к исключению EG-A11Y-16/17 (motion_check 0.1 считает прирост вызовов от прошлой паузы, т.е. и кадры прокрутки).
Под двумя блокировками: flock … flock … timeout 280 python3 99-raw/experiments/J/02-l2-zveno/idle_probe.py OUT.json [--mobile]
Сценарий: загрузка → 5 с (пробуждение закончилось) → для долей страницы 0; 0,2; 0,3; 0,55; 0,6: прокрутка колесом к точке →
пауза 0,7 с → счётчик A → пауза 1,2 с → счётчик B; «рисует в покое» = B − A > 0. Вызовы — перехват drawElements/drawArrays(+Instanced).
"""
import functools, http.server, json, os, socketserver, sys, threading
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('creative', '10-recipes', 'examples'))
HOOK = """(() => { window.__draws = 0; for (const C of [WebGL2RenderingContext, WebGLRenderingContext]) { if (!C) continue;
  for (const m of ['drawElements', 'drawArrays', 'drawElementsInstanced', 'drawArraysInstanced']) { const f = C.prototype[m]; if (!f) continue;
    C.prototype[m] = function (...a) { window.__draws++; return f.apply(this, a); }; } } })();"""


def main():
    out = sys.argv[1]
    mobile = '--mobile' in sys.argv
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    h.log_message = lambda *a, **k: None
    httpd = socketserver.TCPServer(('127.0.0.1', 0), h)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{httpd.server_address[1]}/l2-zveno/index.html"
    res = {'url': url, 'mobile': mobile, 'points': []}
    with sync_playwright() as p:
        br = p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        ctx = br.new_context(**(p.devices['Pixel 7'] if mobile else {'viewport': {'width': 1440, 'height': 900}}))
        pg = ctx.new_page()
        pg.add_init_script(HOOK)
        pg.goto(url, wait_until='load')
        pg.wait_for_timeout(5000)
        H = pg.evaluate('document.documentElement.scrollHeight - innerHeight')
        for f in (0, 0.2, 0.3, 0.55, 0.6):
            target = int(H * f)
            for _ in range(40):
                y = pg.evaluate('scrollY')
                if abs(y - target) < 60:
                    break
                if mobile:
                    pg.evaluate(f'window.scrollBy(0, {max(-500, min(500, target - y))})')
                else:
                    pg.mouse.wheel(0, max(-500, min(500, target - y)))
                pg.wait_for_timeout(60)
            pg.wait_for_timeout(700)
            a = pg.evaluate('window.__draws')
            pg.wait_for_timeout(1200)
            b = pg.evaluate('window.__draws')
            res['points'].append({'frac': f, 'y': pg.evaluate('scrollY'), 'draws_a': a, 'draws_b': b, 'idle_draws': b - a,
                                  'gl_on': pg.evaluate("document.documentElement.classList.contains('gl-on')")})
        br.close()
    httpd.shutdown()
    json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(res['points'], ensure_ascii=False))


if __name__ == '__main__':
    main()
