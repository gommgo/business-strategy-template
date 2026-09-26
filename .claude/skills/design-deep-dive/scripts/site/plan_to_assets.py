#!/usr/bin/env python3
"""plan_to_assets.py — каркас плана ассетов ai-media из медиа- и 3D-слотов page-plan (site-research, агент J, волна 3, 2026-09-24).

Формат выхода — существующий YAML-шаблон ai-media (../ai-media-research/01-web-assets-landscape/01-asset-slots-by-page-type.md §8;
второй формат не изобретается). Проекция полей — E 04-blocks/03-slots-and-page-plan.md §1.4: <секция>-<id> → slots[].id,
id секции → section, media_role → role, source (customer-tbd → real + ожидание материалов), task → task_codes, ratio → variants[],
text_zone, lcp_candidate/loading → delivery, alt → id текстового слота (текст пишет text), authenticity → ai_fit и policy,
motion → motion.type (параметры — treatment creative). page_type → page.page_type плана ассетов по строкам §8 crosswalk.tsv
(запасное правило по классу страницы для id v1 без строки). Бюджеты — профиль P (budgets.yaml), не нормы ai-media.

  python3 99-raw/tools/plan_to_assets.py PLAN.yaml [--out asset-plan.yaml] [--check]
--check: сверка каждого слота с полями и перечислениями шаблона §8 (код 1 при ошибке). Поля subject, must_include, must_avoid,
size, formats, max_kb, focal заполняют Claude и ai-media — в каркасе они пустые с пометкой TODO.
"""
import argparse
import csv
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("site")
CROSSWALK = ROOT / '02-site-types' / 'crosswalk.tsv'
VOCAB = ROOT / '02-site-types' / 'vocabulary.yaml'
BUDGETS = ROOT / '07-seo-geo-performance-analytics' / 'budgets.yaml'
LADDER = {'text', 'svg', 'css', 'shader', 'image', 'video', '3d'}
SOURCE = {'generate', 'edit-real', 'real', 'code', 'template'}
REQUIRED = ('id', 'section', 'role', 'goal', 'ladder', 'source', 'task_codes', 'variants', 'motion', 'delivery', 'ai_fit')
SVG_SLOTS = {'diagram', 'qr-code', 'logo', 'brand-logo', 'favicon', 'icon'}
NO_AI = {'real-only': 'forbidden', 'real-or-generated': 'conditional', 'generated-ok': 'allowed', 'code': 'allowed'}


def load(p):
    with open(p, encoding='utf-8') as f:
        return yaml.safe_load(f)


def asset_page_type(pt):
    if CROSSWALK.exists():
        for r in csv.DictReader(open(CROSSWALK, encoding='utf-8'), delimiter='\t'):
            if r['source_base'] == 'ai-media-research' and r['source_section'].startswith('§8') and r['our_id'] == pt and r['namespace'] == 'page_type':
                return r['source_term'], f"crosswalk §8 ({r['relation']})"
    cls = ((({x['id']: x for x in load(VOCAB)['namespaces']['page_type']['values']}).get(pt)) or {}).get('class')
    return ({'content': 'blog'}.get(cls, 'corporate'), f'запасное правило по классу {cls} (строки §8 нет — предложение X)')


def budgets(profile, level):
    if not BUDGETS.exists():
        return {}
    b = load(BUDGETS)
    w = ((b.get('levels') or {}).get(level) or {}).get('weight') or {}
    out = {}
    for k in ('first_screen_kb', 'session_kb'):
        v = w.get(k)
        if v is None:
            continue
        out[k] = v if isinstance(v, dict) else {'mobile': v, 'desktop': None}
    ov = (((b.get('overrides') or {}).get(profile) or {}).get('weight') or {}).get('first_screen_kb')
    if isinstance(ov, dict):
        out['first_screen_kb'] = ov
    return out


def ladder(sl, kind):
    if kind == '3d':
        return '3d'
    if sl.get('motion') == 'shader':
        return 'shader'
    if sl.get('slot') == 'video' or sl.get('motion') in ('loop', 'video-controls'):
        return 'video'
    if sl.get('slot') in SVG_SLOTS or sl.get('authenticity') == 'code':
        return 'svg'
    return 'image'


def slot_entry(sec, sl, kind, texts):
    sid = f"{sec['id']}-{sl['id']}"
    src = sl.get('source') or ('code' if kind == '3d' else 'real')
    note = []
    if src == 'customer-tbd':
        src = 'real'
        note.append('ждём материалы заказчика (source: customer-tbd в плане)')
    auth = sl.get('authenticity') or ('code' if kind == '3d' else 'real-or-generated')
    variants = []
    ratio = sl.get('ratio') or {}
    tz = sl.get('text_zone')
    for dev in ('desktop', 'mobile'):
        if ratio.get(dev):
            v = {'id': dev, 'ratio': str(ratio[dev]), 'size': 'TODO ai-media', 'formats': 'TODO ai-media', 'max_kb': 'TODO ai-media'}
            if tz and dev == 'desktop':
                v['text_zone'] = tz
            variants.append(v)
    if not variants:
        variants.append({'id': 'default', 'ratio': 'TODO', 'size': 'TODO ai-media', 'formats': 'TODO ai-media', 'max_kb': 'TODO ai-media'})
    alt = sl.get('alt')
    e = {'id': sid, 'section': sec['id'], 'role': sl.get('media_role', 'informational'),
         'goal': sl.get('goal') or 'TODO Claude: что показать за 3 секунды',
         'ladder': ladder(sl, kind), 'source': src, 'task_codes': [t.replace('task:', '') for t in sl.get('task') or []],
         'subject': 'TODO Claude и ai-media (паспорт визуала, art-direction)', 'must_include': [], 'must_avoid': [],
         'variants': variants, 'motion': {'type': sl.get('motion') or 'none'},
         'delivery': {'lcp_candidate': bool(sl.get('lcp_candidate')), 'loading': sl.get('loading') or ('eager' if sl.get('lcp_candidate') else 'lazy')},
         'alt': ('decorative (alt="")' if alt == 'decorative' else f"текст — copy-deck text, слот {sec['id']}.{alt}" if alt else 'TODO: id текстового слота image-alt'),
         'ai_fit': NO_AI.get(auth, 'conditional')}
    if e['delivery']['lcp_candidate']:
        e['delivery']['fetchpriority'] = 'high'
    if sl.get('load') in ('on-visible', 'on-interaction'):
        e['delivery']['load'] = sl['load']
    if kind == '3d':
        note.append(f"3D — blender {sl.get('recipe', 'recipe: TODO')}; постер — {sec['id']}-{sl.get('poster')}; загрузка {sl.get('load', 'after-lcp')}")
    if sl.get('poster_for'):
        note.append(f"постер для {sec['id']}-{sl['poster_for']} (кандидат LCP вместо 3D или видео)")
    if auth == 'real-only':
        note.append('подлинность real-only: люди, работы, товар, скриншоты — только настоящие (I 08/02 §1.2)')
    if note:
        e['note'] = '; '.join(note)
    return e


def build(plan):
    pg = plan['page']
    apt, why = asset_page_type(pg['page_type'])
    slots, no_ai = [], set()
    for sec in plan.get('sections') or []:
        texts = {t['id'] for t in (sec.get('slots') or {}).get('text') or []}
        for kind in ('media', '3d'):
            for sl in (sec.get('slots') or {}).get(kind) or []:
                e = slot_entry(sec, sl, kind, texts)
                slots.append(e)
                if e['ai_fit'] == 'forbidden':
                    no_ai.add({'avatar': 'testimonials', 'logo': 'logos', 'photo': 'real_people_or_work'}.get(sl.get('slot'), sl.get('slot')))
    for sl in (plan.get('page_slots') or {}).get('media') or []:
        slots.append({'id': sl['id'], 'section': 'meta', 'role': 'informational', 'goal': sl.get('goal') or sl['slot'],
                      'ladder': 'svg' if sl.get('slot') == 'favicon' else 'image', 'source': 'code' if sl.get('slot') == 'favicon' else 'template',
                      'task_codes': [], 'variants': [{'id': sl['slot'], 'ratio': '1.91:1' if sl.get('slot') == 'og-image' else '1:1'}],
                      'motion': {'type': 'none'}, 'delivery': {'lcp_candidate': False, 'loading': 'lazy'},
                      'ai_fit': 'forbidden' if sl.get('slot') == 'favicon' else 'allowed'})
    return {'plan_version': 1, 'checked': str(plan.get('checked')),
            'page': {'id': pg['id'], 'page_type': apt, 'locale': pg.get('locale', 'ru-RU'), 'audience': pg.get('goal', ''),
                     'x_site': {'page_plan': f"{plan.get('site')}/{pg['id']}", 'page_type': pg['page_type'], 'mapping': why}},
            'brand': {'palette_tokens': 'TODO art-direction creative', 'style_passport': 'TODO', 'photo_language': 'TODO', 'forbidden_markers': []},
            'budgets': budgets(pg.get('budget_profile'), pg.get('ambition_level', 'L1')),
            'policy': {'no_ai_subjects': sorted(x for x in no_ai if x), 'disclosure': 'per-slot'},
            'slots': slots}


def check(ap):
    errs = []
    for s in ap['slots']:
        for k in REQUIRED:
            if k not in s:
                errs.append(f"{s.get('id')}: нет поля {k}")
        if s.get('role') not in ('informational', 'decorative'):
            errs.append(f"{s['id']}: role {s.get('role')}")
        if s.get('ladder') not in LADDER:
            errs.append(f"{s['id']}: ladder {s.get('ladder')}")
        if s.get('source') not in SOURCE:
            errs.append(f"{s['id']}: source {s.get('source')}")
        if s.get('ai_fit') not in ('allowed', 'conditional', 'forbidden'):
            errs.append(f"{s['id']}: ai_fit {s.get('ai_fit')}")
    ids = [s['id'] for s in ap['slots']]
    if len(ids) != len(set(ids)):
        errs.append('id слотов повторяются')
    if ap['page']['page_type'] not in ('saas-landing', 'product', 'ecom-home', 'ecom-pdp', 'campaign', 'studio', 'corporate', 'blog', 'web-app-inserts'):
        errs.append(f"page.page_type {ap['page']['page_type']} вне перечня §8")
    return errs


def main():
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    a.add_argument('plan')
    a.add_argument('--out')
    a.add_argument('--check', action='store_true')
    x = a.parse_args()
    plan = load(x.plan)
    ap = build(plan)
    head = (f"# asset-plan.yaml — КАРКАС из {Path(x.plan).name} (plan_to_assets.py, site-research J). Формат — ai-media 01/01 §8.\n"
            "# TODO-поля заполняют Claude (subject, goal) и ai-media (size, formats, max_kb, маршрут задачи); бюджеты — профиль P.\n")
    text = head + yaml.safe_dump(ap, allow_unicode=True, sort_keys=False, width=120)
    if x.out:
        Path(x.out).write_text(text, encoding='utf-8')
    else:
        print(text)
    errs = check(ap) if x.check else []
    print(f"слотов {len(ap['slots'])}; page_type {ap['page']['page_type']} ({ap['page']['x_site']['mapping']}); ошибок полей §8: {len(errs)}", file=sys.stderr)
    for e in errs:
        print('  ', e, file=sys.stderr)
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
