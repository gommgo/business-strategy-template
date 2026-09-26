#!/usr/bin/env python3
"""K/03 — axe-core 4.13 с адресами узлов: какие элементы проваливают color-contrast и прочие правила SG-A11Y-01
(агент K3, 2026-09-24). Основа — `99-raw/experiments/I/02-axe/run_axe.py` (агент I; axe-core берётся из его node_modules,
только чтение). Отличия: для каждого узла — селектор, тег, текст, в H1 ли, действие ли (a, button), в форме ли, в подвале
ли, в первом экране ли, кегль — чтобы отличить «H1, лид, призыв, согласие» (профиль I: B) от прочего текста (S).
Без кликов и ввода; баннер cookie не трогается (состояние «первый визит»); десктоп 1440×900.
Запуск одной страницы (под двумя блокировками снаружи): python3 run_axe_targets.py ID URL MARKET OUTDIR
"""
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

pid, url, market, outdir = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
AXE_JS = str(kbpaths.node_modules('axe-core', 'axe.min.js'))
AXE = open(AXE_JS, encoding='utf-8').read()
RULES = ['color-contrast', 'link-name', 'button-name', 'label', 'meta-viewport', 'target-size', 'image-alt', 'frame-title',
         'html-has-lang', 'html-lang-valid']
res = {'id': pid, 'url': url, 'market': market, 'date': time.strftime('%Y-%m-%d %H:%M'), 'viewport': '1440x900'}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True)
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, locale='ru-RU' if market == 'ru' else 'en-US')
    page = ctx.new_page()
    try:
        r = page.goto(url, wait_until='domcontentloaded', timeout=45000)
        res['status'] = r.status if r else None
        try:
            page.wait_for_load_state('load', timeout=15000)
        except Exception:  # noqa: BLE001
            pass
        page.wait_for_timeout(6000)
        page.add_script_tag(content=AXE)
        res['axe'] = page.evaluate("""async (rules) => {
          const r = await axe.run(document, {runOnly:{type:'tag', values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}, resultTypes:['violations']});
          const out = [];
          for (const v of r.violations) {
            const nodes = [];
            for (const n of v.nodes.slice(0, 60)) {
              const sel = Array.isArray(n.target) ? n.target[n.target.length - 1] : n.target;
              let el = null; try { el = document.querySelector(typeof sel === 'string' ? sel : String(sel)); } catch (e) {}
              let info = {sel: String(sel).slice(0, 120)};
              if (el) {
                const rc = el.getBoundingClientRect(); const cs = getComputedStyle(el);
                info = Object.assign(info, {tag: el.tagName, text: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 60),
                  in_h1: !!el.closest('h1'), action: !!el.closest('a,button,[role=button]'), in_form: !!el.closest('form'),
                  in_footer: !!el.closest('footer,[class*=footer i],[id*=footer i]'), in_header: !!el.closest('header,[class*=header i]'),
                  cookie: !!el.closest('[id*=cookie i],[class*=cookie i],[id*=consent i],[class*=consent i],[id*=onetrust i],[class*=cky-]'),
                  top: Math.round(rc.top + scrollY), first_screen: (rc.top + scrollY) < innerHeight, fs: parseFloat(cs.fontSize) || null});
              }
              const d = (n.any && n.any[0] && n.any[0].data) || {};
              if (d.contrastRatio) info.ratio = d.contrastRatio;
              nodes.push(info);
            }
            out.push({id: v.id, impact: v.impact, nodes_n: v.nodes.length, nodes});
          }
          return {version: axe.version, violations: out};
        }""", RULES)
    except Exception as e:  # noqa: BLE001
        res['error'] = repr(e)[:300]
    finally:
        ctx.close()
        br.close()
os.makedirs(outdir, exist_ok=True)
json.dump(res, open(os.path.join(outdir, f'{pid}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(pid, res.get('status'), 'violations:', len((res.get('axe') or {}).get('violations', [])), 'err' if 'error' in res else '')
