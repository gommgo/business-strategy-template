#!/usr/bin/env python3
"""ad_check.py — проверка арт-дирекции сайта: файл проекта `docs/projects/<slug>/design/<surface>/art-direction.json`
или пример базы (без аргументов — все примеры kb/creative).

1. Схема — kb/creative/09-ai-execution-evaluation/art-direction.v1.schema.json (JSON Schema 2020-12).
2. Паспорт визуала — handoff.visual_dna.* против подсхем ai-media 06-art-direction-consistency/visual-dna.schema.json.
3. Правила, которые схема выразить не может: тёплая бумага или антиква — не больше чем у одного направления без
   требования бренда; буквальное прочтение территории ≤ 1;
   ссылки на направления, территории и решения (choice.chosen, merged_from, rejected, lifted_markers[].decision_ref)
   существуют; макроструктура — id словаря site; контраст палитр (WCAG 2); уровень ↔ эффекты (level_min каталога
   эффектов) ↔ движение (потолок уровня — ambition-levels.yaml#levels.maps_to.claude_design) ↔ плавная прокрутка
   (forbidden уровня); boldness ↔ уровень (maps_to.visual_dna); профиль бюджета = <page_type>@<уровень>; акцент в
   запретной полосе оттенков; ключи --allow — из kb/common/tells.yaml#checks и у каждого есть решение.
4. Ссылки с префиксом разрешаются: effect:<id> — каталог эффектов, cliche:<id> — реестр клише, префиксы словаря site
   (section-role:, block:, macrostructure: …) — vocabulary.yaml, fact:<id> — факты по refs.facts, если файл на месте.

  python3 ad_check.py [ФАЙЛ …] [--json]    код выхода: 0 — ошибок нет; 1 — есть; 2 — файла нет или он не JSON
  python3 ad_check.py --selftest           примеры базы без ошибок, посеянные ошибки ловятся
Предупреждения, а не ошибки (законно при строгом бренде или референсе заказчика; основание — поля inputs
brand_expression_mode и references_given, решает заказчик): направлений меньше трёх (схема — от 1 до 5), пара
направлений различается меньше чем по двум осям из 4, территории — меньше трёх материальных семейств.
Ключ k3_allow без решения и lifted_markers на несуществующее решение — предупреждение, у документа approved — ошибка.
Предупреждения о согласованности документа: у эффекта из effects_by_section нет записи decisions[] (technique называет
effect:<id>); снятую примету (lifted_markers) держит решение не вида use или twist; до выбора направления уровень требует
больше пиков, чем один главный приём направления (section_distribution.peaks_min файла уровней); варианты подачи
(treatment_variants) записаны без выбора направления; расширение x-direction-bans — не {id направления: [запрет]}, зовёт
несуществующее направление или расходится с полем bans направления; трекинг заголовков, названный в type.note числом в
em, ниже нормы гарнитуры из kb/creative/04-visual-language/cyrillic-display-fonts.yaml (tracking_touch и запас файла).
"""
import argparse
import copy
import glob
import json
import os
import re
import sys
import tempfile

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import kbpaths  # noqa: E402
from color import hex2oklch, wcag  # noqa: E402

AD_SCHEMA = kbpaths.kb('creative', '09-ai-execution-evaluation', 'art-direction.v1.schema.json')
VD_SCHEMA = kbpaths.kb('ai-media', '06-art-direction-consistency', 'visual-dna.schema.json')
LEVELS = kbpaths.kb('creative', '01-creative-direction', 'ambition-levels.yaml')
EFFECTS = kbpaths.kb('creative', '06-effects-catalog', 'effects.yaml')
CLICHES = kbpaths.kb('creative', '08-uniqueness-anti-slop', 'cliche-registry.yaml')
VOCAB = kbpaths.kb('site', '02-site-types', 'vocabulary.yaml')
TELLS = kbpaths.kb(None, 'common', 'tells.yaml')
FONTS = kbpaths.kb('creative', '04-visual-language', 'cyrillic-display-fonts.yaml')
EXAMPLES = sorted(glob.glob(str(kbpaths.kb('creative', '01-creative-direction', 'examples', 'art-direction-*.json')))
                  + glob.glob(str(kbpaths.kb('creative', '09-ai-execution-evaluation', 'examples', 'art-direction-*.json'))))
ORDER = {'L0': 0, 'L1': 1, 'L2': 2}
CORE = ['paper', 'display_style', 'accent_hue', 'macrostructure']
TRACKING = re.compile(r'трекинг\w*\s*([+−–-]?\s*\d+(?:[.,]\d+)?)\s*em', re.I)      # «трекинг +0,015 em» в заметке шрифтов
VD_SUB = {'character': '#/properties/character', 'palette_forbidden_hues': '#/properties/palette/properties/forbidden_hues',
          'exclusions': '#/properties/exclusions', 'abstract': '#/properties/abstract', 'video': '#/properties/video',
          'composition': '#/properties/composition', 'subject_matter': '#/properties/subject_matter', 'materials': '#/properties/materials'}


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f) if str(p).endswith('.json') else yaml.safe_load(f)


class Ctx:
    """Схемы и справочники соседних баз."""
    def __init__(self):
        self.ad = load(AD_SCHEMA)
        vd = load(VD_SCHEMA)
        reg = Registry().with_resources([(self.ad['$id'], Resource.from_contents(self.ad, default_specification=DRAFT202012)),
                                         (vd['$id'], Resource.from_contents(vd, default_specification=DRAFT202012))])
        self.v_ad = Draft202012Validator(self.ad, registry=reg)
        self.v_vd = {k: Draft202012Validator({'$ref': vd['$id'] + p}, registry=reg) for k, p in VD_SUB.items()}
        lv = load(LEVELS)
        self.levels = {L['id']: L for L in lv['levels']}
        self.motion_order = lv.get('motion_caps') or ['none', 'subtle', 'expressive', 'cinematic']
        self.effects = {e['id']: e for e in load(EFFECTS)['effects']}
        reg_c = load(CLICHES)
        self.cliches = {e['id'] for e in reg_c['entries']} | set(reg_c.get('id_aliases') or {})
        voc = load(VOCAB)
        self.vocab = {p: {x['id'] for x in voc['namespaces'][ns]['values']} for p, ns in voc['ref_prefixes'].items()}
        self.allow_keys = {v['allow'] for v in (load(TELLS).get('checks') or {}).values() if isinstance(v, dict) and v.get('allow')}
        with open(FONTS, encoding='utf-8') as f:
            fonts_text = f.read()
        self.touch = {}       # гарнитура (нижний регистр) → tracking_touch каталога, em
        for ft in (yaml.safe_load(fonts_text) or {}).get('fonts') or []:
            t = (ft.get('metrics') or {}).get('tracking_touch')
            if isinstance(t, (int, float)):
                for name in re.sub(r'\s*\(.*?\)', '', str(ft.get('family') or '')).split('/'):
                    if name.strip():
                        self.touch[name.strip().lower()] = float(t)
        # запас над tracking_touch — число из шапки каталога («трекинг display не ниже tracking_touch + …»)
        m = re.search(r'tracking_touch \+ (\d+[.,]\d+)', fonts_text)
        self.touch_margin = float(m.group(1).replace(',', '.')) if m else 0.0
        pref = '|'.join(sorted(set(self.vocab) | {'effect', 'cliche', 'fact'}, key=len, reverse=True))
        self.prefix_re = re.compile(rf'(?<![A-Za-z0-9_-])({pref}):([a-z0-9]+(?:-[a-z0-9]+)*)')

    def motion_max(self, lvl):
        """Потолок уровня движения: проекция уровня (maps_to.claude_design.motion_level) в порядке motion_caps."""
        top = ((self.levels[lvl].get('maps_to') or {}).get('claude_design') or {}).get('motion_level', self.motion_order[-1])
        return self.motion_order[:self.motion_order.index(top) + 1]

    def forbids(self, lvl, item):
        return any(f.get('id') == item for f in self.levels[lvl].get('forbidden') or [])

    def boldness(self, lvl):
        return ((self.levels[lvl].get('maps_to') or {}).get('visual_dna') or {}).get('character.boldness')

    def peaks_min(self, lvl):
        return (self.levels[lvl].get('section_distribution') or {}).get('peaks_min') or 0

    def tracking_floor(self, family):
        """Нижняя граница трекинга заголовков гарнитуры, em: tracking_touch каталога + запас; гарнитуры нет — None."""
        t = self.touch.get(str(family or '').strip().lower())
        return None if t is None else t + self.touch_margin


def errs(v, doc):
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:160]}" for e in v.iter_errors(doc)]


def strings(x, path=''):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from strings(v, f'{path}/{k}')
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from strings(v, f'{path}/{i}')
    elif isinstance(x, str):
        yield path, x


def facts_ids(ad, path):
    ref = (ad.get('refs') or {}).get('facts')
    if not ref or not path:
        return None
    p = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(path)), ref.split('#', 1)[0]))
    if not os.path.isfile(p):
        return None
    d = load(p) or {}
    ids = {f.get('id') for f in d.get('facts') or [] if isinstance(f, dict)}
    for f in d.get('facts') or []:
        ids |= set(f.get('aliases') or []) if isinstance(f, dict) else set()
    return ids


def prefixed(ctx, ad, path=None):
    """Ссылки с префиксом пространства разрешаются в своих справочниках."""
    facts = facts_ids(ad, path)
    out = []
    for where, s in strings(ad):
        for m in ctx.prefix_re.finditer(s):
            p, i = m.group(1), m.group(2)
            if p == 'effect':
                ok = i in ctx.effects
            elif p == 'cliche':
                ok = i in ctx.cliches
            elif p == 'fact':
                ok = facts is None or i in facts
            else:
                ok = i in ctx.vocab.get(p, set())
            if not ok:
                out.append(f'{where}: {p}:{i} не разрешается ({"каталог эффектов" if p == "effect" else "реестр клише" if p == "cliche" else "факты refs.facts" if p == "fact" else "словарь site"})')
    return out


def cross(ctx, ad):
    E, W = [], []
    lvl = ad['ambition']['level']
    approved = ad.get('status') == 'approved'
    dirs = {d['id']: d for d in ad['directions']}
    ids = list(dirs)
    # число направлений, различие пар и семейства территорий — нормы creative 01/01 §4.1, §6: при строгом бренде или
    # референсе заказчика меньший набор законен, поэтому это предупреждение с основанием, а решает заказчик
    inp = ad.get('inputs') or {}
    basis = ('строгий бренд' if inp.get('brand_expression_mode') == 'strict' else
             'референс заказчика' if inp.get('references_given') else None)
    soft = (f'основание — {basis}, решает заказчик' if basis else
            'законно при строгом бренде (inputs.brand_expression_mode: strict) или референсе заказчика (inputs.references_given)')
    if len(ids) < 3:
        W.append(f'направлений {len(ids)} — меньше трёх (creative 01/01 §6.3): {soft}')
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = dirs[ids[i]]['axes'], dirs[ids[j]]['axes']
            diff = [k for k in CORE if a.get(k) != b.get(k)]
            if len(diff) < 2:
                W.append(f'направления {ids[i]} и {ids[j]} различаются только по {diff or "ни одной оси"} '
                         f'(норма — ≥ 2 из {CORE}, creative 01/01 §6.2): {soft}')
    brand_words = ' '.join(ad['inputs'].get('must_keep', [])).lower()
    warm_serif = [d['id'] for d in ad['directions'] if d['axes'].get('paper_temperature') == 'warm' or d['axes']['display_style'] == 'serif']
    if len(warm_serif) > 1 and not any(w in brand_words for w in ('антиква', 'serif', 'тёпл', 'крем')):
        E.append(f'тёплая бумага или антиква у {len(warm_serif)} направлений {warm_serif} (≤ 1 без требования бренда, creative 01/01 §6)')
    terr = {t['id']: t for t in ad['territories']}
    fams = {t['family'] for t in ad['territories']}
    if len(fams) < 3:
        W.append(f'материальных семейств у территорий {len(fams)} — меньше трёх (creative 01/01 §4.1): {soft}')
    if sum(1 for t in ad['territories'] if t.get('literal')) > 1:
        E.append('буквальных прочтений > 1')
    macro = ctx.vocab.get('macrostructure', set())
    for d in ad['directions']:
        if d['territory'] not in terr:
            E.append(f'направление {d["id"]}: территории {d["territory"]} нет')
        if d['axes']['macrostructure'] not in macro:
            E.append(f'направление {d["id"]}: макроструктуры {d["axes"]["macrostructure"]} нет в словаре site')
        pal = d['palette']
        if wcag(pal['text'], pal['background']) < 4.5:
            E.append(f'{d["id"]}: текст/фон {wcag(pal["text"], pal["background"]):.2f} < 4,5')
        if pal.get('on_accent') and wcag(pal['on_accent'], pal['accent']) < 4.5:
            E.append(f'{d["id"]}: текст на акценте {wcag(pal["on_accent"], pal["accent"]):.2f} < 4,5')
        for e in d['signature_move'].get('effects', []):
            if e.split(':', 1)[-1] in ctx.effects and ORDER[ctx.effects[e.split(':', 1)[-1]]['level_min']] > ORDER[max(d['level_fit'], key=ORDER.get)]:
                W.append(f'{d["id"]}: главный приём {e} требует уровня выше level_fit {d["level_fit"]}')
    ch = ad.get('choice')
    if not ch:
        # до выбора: один главный приём направления — один пик; уровню с большим числом пиков его мало
        need = ctx.peaks_min(lvl)
        if need > 1:
            for d in ad['directions']:
                W.append(f'направление {d["id"]} не держит ритм уровня {lvl}: главный приём один, уровню нужно пиков от {need} '
                         f'(ambition-levels.yaml section_distribution.peaks_min) — назовите остальные пики до выбора')
        if ad.get('treatment_variants'):
            W.append('treatment_variants записаны без выбора направления (choice): варианты подачи — у выбранного направления')
    xb = ad.get('x-direction-bans')
    if xb is not None:
        if not isinstance(xb, dict) or not all(isinstance(v, list) and all(isinstance(x, str) and x.strip() for x in v)
                                               for v in xb.values()):
            W.append('x-direction-bans — не {id направления: [запрет строкой]}')
        else:
            for k in sorted(set(xb) - set(dirs)):
                W.append(f'x-direction-bans: направления {k} нет среди directions')
            for k in sorted(k for k in xb if k in dirs and dirs[k].get('bans') and list(dirs[k]['bans']) != list(xb[k])):
                W.append(f'направление {k}: запреты записаны полем bans и расширением x-direction-bans, списки расходятся')
    for where, tp in [(f'направление {d["id"]}', d.get('type') or {}) for d in ad['directions']] + \
                     [('visual_language', (ad.get('visual_language') or {}).get('type') or {})]:
        floor = ctx.tracking_floor(tp.get('display'))
        if floor is None:
            continue
        for raw in TRACKING.findall(str(tp.get('note') or '')):
            val = float(re.sub(r'\s', '', raw).replace(',', '.').replace('−', '-').replace('–', '-'))
            if val < floor - 1e-9:
                W.append(f'{where}: трекинг {val:+g} em у {tp["display"]} ниже нормы каталога гарнитур {floor:+g} em '
                         f'(cyrillic-display-fonts.yaml: tracking_touch + {ctx.touch_margin:g})')
    if ch:
        if ch['chosen'] not in dirs:
            E.append(f'choice.chosen {ch["chosen"]} нет среди направлений')
        for m in ch.get('merged_from', []):
            if m not in dirs:
                E.append(f'choice.merged_from {m} нет среди направлений')
        for r in ch.get('rejected', []):
            if r['id'] not in dirs:
                E.append(f'choice.rejected {r["id"]} нет среди направлений')
        chosen = dirs.get(ch['chosen'])
        if chosen:
            if lvl not in chosen['level_fit']:
                E.append(f'выбранное направление {chosen["id"]} не работает на уровне {lvl} (level_fit {chosen["level_fit"]})')
            if ORDER[chosen['signature_move'].get('min_level', 'L0')] > ORDER[lvl]:
                E.append(f'главный приём выбранного направления требует {chosen["signature_move"]["min_level"]} > {lvl}')
    for s in ad.get('effects_by_section', []):
        sl = s.get('level', lvl)
        if ORDER[sl] > ORDER[lvl]:
            E.append(f'эффекты секции {s["section"]}: уровень {sl} выше страницы {lvl}')
        for e in s['effects']:
            ce = ctx.effects.get(e.split(':', 1)[-1])
            if ce and ORDER[ce['level_min']] > ORDER[sl]:
                E.append(f'эффект {e} запрещён на уровне {sl} (level_min {ce["level_min"]}, секция {s["section"]})')
    ms = ad.get('motion_system')
    if ms:
        allowed = ctx.motion_max(lvl)
        if ms['level'] not in allowed:
            E.append(f'motion_system.level {ms["level"]} выше допустимого для {lvl} ({allowed[-1]})')
        cap = ad['ambition'].get('motion_cap')
        order_m = ctx.motion_order
        if cap and order_m.index(ms['level']) > order_m.index(cap):
            E.append(f'motion_system.level {ms["level"]} выше motion_cap {cap}')
        if ms.get('smooth_scroll') and ctx.forbids(lvl, 'smooth-scroll'):
            E.append(f'плавная прокрутка запрещена уровнем {lvl}')
        for b in ms.get('by_section', []):
            if b['motion_level'] not in allowed:
                E.append(f'движение секции {b["section"]} {b["motion_level"]} выше уровня {lvl}')
    bp = ad['ambition']['budget_profile']
    if bp != f"{ad['inputs']['page_type']}@{lvl}":
        E.append(f"budget_profile {bp} ≠ {ad['inputs']['page_type']}@{lvl}")
    vd = (ad.get('handoff') or {}).get('visual_dna') or {}
    want = ctx.boldness(lvl)
    if vd.get('character', {}).get('boldness') and want and vd['character']['boldness'] != want:
        E.append(f"visual_dna boldness {vd['character']['boldness']} ≠ {want} для {lvl}")
    vl = ad.get('visual_language', {}).get('palette')
    if vl:
        H = hex2oklch(vl['accent'])[2]
        for band in ad.get('exclusions', {}).get('forbidden_hues', []):
            if band['from'] <= H <= band['to']:
                W.append(f"акцент {vl['accent']} (H {H:.0f}°) внутри запретной полосы {band['from']}–{band['to']}°")
    decisions = {d['id']: d for d in ad.get('decisions', [])}
    techniques = ' '.join(str(d.get('technique') or '') for d in decisions.values())
    for s in ad.get('effects_by_section', []):
        for e in s['effects']:
            if not re.search(rf'(?<![A-Za-z0-9_-]){re.escape(e)}(?![a-z0-9-])', techniques):
                W.append(f'эффект {e} секции {s["section"]} без решения: в decisions[] нет записи с technique {e}')
    keys = set(ad.get('exclusions', {}).get('k3_allow', [])) | {d['k3_allow'] for d in decisions.values() if d.get('k3_allow')}
    for k in sorted(keys - ctx.allow_keys):
        E.append(f'ключа --allow {k} нет у проверок утилиты макета (kb/common/tells.yaml#checks)')
    justified = {d.get('k3_allow') for d in decisions.values() if d.get('k3_allow') and d.get('decision') in ('use', 'twist')}
    for k in sorted(set(ad.get('exclusions', {}).get('k3_allow', [])) - justified):
        (E if approved else W).append(f'--allow {k} без решения (decisions[].k3_allow с use или twist)')
    for lm in ad.get('exclusions', {}).get('lifted_markers', []):
        if lm['decision_ref'] not in decisions:
            (E if approved else W).append(f"lifted_markers {lm['marker']}: решения {lm['decision_ref']} нет в decisions")
        elif decisions[lm['decision_ref']].get('decision') not in ('use', 'twist'):
            W.append(f"lifted_markers {lm['marker']}: решение {lm['decision_ref']} — {decisions[lm['decision_ref']].get('decision')}; "
                     f"примету снимает решение вида use или twist")
    return E, W


def check(ctx, ad, path=None):
    se = errs(ctx.v_ad, ad)
    ve = []
    for k, v in ((ad.get('handoff') or {}).get('visual_dna') or {}).items():
        if k in ctx.v_vd:
            ve += [f'visual_dna.{k}: {m}' for m in errs(ctx.v_vd[k], v)]
    pe = prefixed(ctx, ad, path)
    try:
        ce, cw = cross(ctx, ad)
    except (KeyError, TypeError, IndexError, AttributeError, ValueError) as e:
        # правила вне схемы опираются на обязательные поля: без них — предупреждение к ошибке схемы
        ce, cw = ([], [f'правила вне схемы не проверены: нет поля {e}']) if se else ([f'правила вне схемы: {e!r}'], [])
    return {'schema': se, 'visual_dna': ve, 'refs': pe, 'rules': ce, 'warnings': cw, 'ok': not (se or ve or pe or ce)}


def report(path, r):
    name = os.path.relpath(path) if path else '—'
    print(('ok  ' if r['ok'] else 'XX  ') + name + f" — схема {len(r['schema'])}, паспорт {len(r['visual_dna'])}, ссылки {len(r['refs'])}, "
          f"правила {len(r['rules'])}, предупреждений {len(r['warnings'])}")
    for m in r['schema'] + r['visual_dna'] + r['refs'] + r['rules']:
        print('     ·', m)
    for m in r['warnings']:
        print('     ~', m)


def run_files(ctx, files, as_json=False):
    res, code = {}, 0
    for p in files:
        try:
            ad = load(p)
        except (OSError, ValueError) as e:
            print(f'ad_check: {p}: {e}', file=sys.stderr)
            return 2
        r = check(ctx, ad, p)
        res[p] = r
        code = max(code, 0 if r['ok'] else 1)
        if not as_json:
            report(p, r)
    if as_json:
        print(json.dumps({'files': res}, ensure_ascii=False, indent=1))
    return code


def selftest(ctx):
    ok = True

    def expect(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f'{"OK  " if cond else "FAIL"} {name}')
    Draft202012Validator.check_schema(ctx.ad)
    expect('примеров арт-дирекции в базе ≥ 6', len(EXAMPLES) >= 6)
    for p in EXAMPLES:
        r = check(ctx, load(p), p)
        expect(f'пример {os.path.basename(p)}: 0 ошибок', r['ok'])
    base = load(kbpaths.kb('creative', '01-creative-direction', 'examples', 'art-direction-kvarts.json'))

    def neg(name, mut, part):
        d = copy.deepcopy(base)
        mut(d)
        r = check(ctx, d)
        if part == 'warnings':       # доклад, а не стоп: предупреждение и ни одной ошибки
            expect(f'предупреждает: {name}', r['warnings'] and r['ok'])
        else:
            expect(f'ловит: {name}', r[part])

    def one_direction(d, mode):
        d['directions'] = d['directions'][:1]
        d['choice'].update({'merged_from': [], 'rejected': []})
        d['inputs']['brand_expression_mode'] = mode
        d['inputs'].pop('references_given', None)
    neg('направления различаются меньше чем по двум осям',
        lambda d: d['directions'][1]['axes'].update({k: d['directions'][0]['axes'][k] for k in ('paper', 'display_style', 'macrostructure')}), 'warnings')
    neg('два направления с антиквой', lambda d: d['directions'][3]['axes'].update({'display_style': 'serif'}), 'rules')
    neg('use при проваленной проверке', lambda d: d['decisions'][1]['criteria']['epoch'].update({'result': 'fail'}), 'schema')
    neg('approved без подписи', lambda d: d.update({'approved_by': None}), 'schema')
    neg('нет обязательного поля (concept.rut)', lambda d: d['concept'].pop('rut'), 'schema')
    neg('плавная прокрутка на L1', lambda d: d['motion_system'].update({'smooth_scroll': True}), 'rules')
    neg('boldness не по уровню', lambda d: d['handoff']['visual_dna']['character'].update({'boldness': 'bold'}), 'rules')
    neg('контраст палитры', lambda d: d['directions'][0]['palette'].update({'text': '#9AA0A6'}), 'rules')
    neg('макроструктуры нет в словаре', lambda d: d['directions'][0]['axes'].update({'macrostructure': 'hero-bento-magic'}), 'rules')
    neg('две буквальные территории', lambda d: d['territories'][0].update({'literal': True}), 'rules')
    neg('choice.chosen — несуществующее направление', lambda d: d['choice'].update({'chosen': 'z'}), 'rules')
    neg('merged_from — несуществующее направление', lambda d: d['choice'].update({'merged_from': ['q']}), 'rules')
    neg('3D-сцена на L1', lambda d: d['effects_by_section'].append({'section': 'hero', 'level': 'L1', 'effects': ['effect:3d-scene']}), 'rules')
    neg('два направления вместо 3–5', lambda d: (d.update({'directions': d['directions'][:2]}),
                                                 d['choice'].update({'rejected': []})), 'warnings')
    neg('шесть направлений — больше пяти', lambda d: d['directions'].extend(
        dict(copy.deepcopy(d['directions'][1]), id=f'x{i}') for i in range(2)), 'schema')
    neg('территории из одного материального семейства',
        lambda d: [t.update({'family': 'document-print'}) for t in d['territories']], 'warnings')
    neg('профиль бюджета не по типу и уровню', lambda d: d['ambition'].update({'budget_profile': 'landing-saas@L1'}), 'rules')
    neg('тезис длиннее 240', lambda d: d['concept'].update({'thesis': 'очень ' * 60}), 'schema')
    neg('движение выше потолка уровня', lambda d: d['motion_system'].update({'level': 'cinematic'}), 'rules')
    neg('id с префиксом: эффекта нет в каталоге', lambda d: d['directions'][0]['signature_move'].update({'effects': ['effect:no-such-effect']}), 'refs')
    neg('id с префиксом: роли секции нет в словаре', lambda d: d['moodboard'][0].update({'applies_to': 'section-role:no-such-role'}), 'refs')
    neg('id с префиксом: записи клише нет в реестре', lambda d: d['decisions'][0].update({'technique': 'cliche:no-such-cliche'}), 'refs')
    neg('lifted_markers на несуществующее решение (approved — ошибка)',
        lambda d: d['exclusions'].update({'lifted_markers': [{'marker': 'IMG-M05', 'decision_ref': 'no-such-decision'}]}), 'rules')
    neg('референс со значениями без measured и estimated', lambda d: d['moodboard'][0].update({'values': {}}), 'schema')
    expect('пример-основа посеянных случаев — без предупреждений', not check(ctx, base)['warnings'])

    def warns(mut, text):
        """Копия основы после mut даёт предупреждение с text; ошибок правка не добавляет."""
        d = copy.deepcopy(base)
        mut(d)
        r = check(ctx, d)
        return any(text in m for m in r['warnings']) and not (r['schema'] or r['refs'])
    use_id = next(x['id'] for x in base['decisions'] if x['decision'] in ('use', 'twist'))
    avoid_id = next(x['id'] for x in base['decisions'] if x['decision'] == 'avoid')
    ebs_eff = base['effects_by_section'][0]['effects'][0]
    expect('эффект из effects_by_section без записи decisions[] — предупреждение',
           warns(lambda d: d.update(decisions=[x for x in d['decisions'] if ebs_eff not in x['technique']]), f'эффект {ebs_eff}'))
    expect('снятая примета с решением вида avoid — предупреждение',
           warns(lambda d: d['exclusions'].update({'lifted_markers': [{'marker': 'IMG-M05', 'decision_ref': avoid_id}]}), 'use или twist'))
    d = copy.deepcopy(base)
    d['exclusions']['lifted_markers'] = [{'marker': 'MS-10', 'decision_ref': use_id, 'page': 'home', 'section': 'hero'}]
    d['directions'][0].update(bans=['без градиента в заголовках'], notes='смотреть на первый экран и на ритм секций')
    d['treatment_variants'] = [{'id': 'v-calm', 'name': 'Спокойный', 'shows': 'первый экран без сцены, секции появляются по очереди',
                                'effects': [ebs_eff], 'chosen': True, 'chosen_by': 'customer'},
                               {'id': 'v-scene', 'shows': 'первый экран сценой по прокрутке, остальное спокойно'}]
    r = check(ctx, d)
    expect('запись снятой нормы с page и section, запреты и заметка направления, варианты подачи: схема проходит, 0 предупреждений',
           r['ok'] and not r['warnings'])
    neg('запрет направления не строкой', lambda d: d['directions'][0].update(bans=[{'what': 'градиент'}]), 'schema')
    neg('выбранный вариант подачи без chosen_by', lambda d: d.update(
        treatment_variants=[{'id': 'v-calm', 'shows': 'первый экран без сцены', 'chosen': True}]), 'schema')
    expect('варианты подачи без выбора направления — предупреждение',
           warns(lambda d: (d.pop('choice'), d.pop('approved_by', None), d.pop('approved_at', None),
                            d.update(status='proposed', treatment_variants=[{'id': 'v-calm', 'shows': 'первый экран без сцены'}])),
                 'treatment_variants записаны без выбора'))
    known = base['directions'][0]['id']
    expect('x-direction-bans: список своему направлению — без предупреждений; чужой id и не список — предупреждение',
           not check(ctx, dict(copy.deepcopy(base), **{'x-direction-bans': {known: ['без градиента в заголовках']}}))['warnings']
           and warns(lambda d: d.update({'x-direction-bans': {'no-such-direction': ['без градиента']}}), 'no-such-direction нет среди directions')
           and warns(lambda d: d.update({'x-direction-bans': {known: 'без градиента'}}), 'x-direction-bans — не'))
    expect('x-direction-bans расходится с полем bans направления — предупреждение',
           warns(lambda d: (d['directions'][0].update(bans=['без градиента в заголовках']),
                            d.update({'x-direction-bans': {known: ['без капса в заголовках']}})), 'списки расходятся'))
    # ритм уровня до выбора: уровень с peaks_min больше одного — предупреждение у каждого направления
    many = next((k for k in ctx.levels if ctx.peaks_min(k) > 1), None)
    d = copy.deepcopy(base)
    for k in ('choice', 'approved_by', 'approved_at'):
        d.pop(k, None)
    d['status'] = 'proposed'
    lvl0 = d['ambition']['level']
    r = check(ctx, d)
    expect('ритм уровня до выбора: уровню хватает одного пика — предупреждения нет',
           ctx.peaks_min(lvl0) <= 1 and not any('не держит ритм уровня' in m for m in r['warnings']))
    d['ambition']['level'] = many
    r = check(ctx, d)
    expect('ритм уровня до выбора: уровню нужно больше пиков — «направление не держит ритм уровня» у каждого направления',
           many and sum('не держит ритм уровня' in m for m in r['warnings']) == len(d['directions']))
    d = copy.deepcopy(base)
    d['ambition']['level'] = many
    expect('ритм уровня после выбора: предупреждения нет (норму пиков сверяет план)',
           not any('не держит ритм уровня' in m for m in check(ctx, d)['warnings']))
    # трекинг заголовков против каталога гарнитур
    fam = base['visual_language']['type']['display']
    floor = ctx.tracking_floor(fam)
    expect('гарнитура заголовков примера есть в каталоге гарнитур с tracking_touch', floor is not None)
    if floor is not None:
        expect('трекинг заголовков ниже нормы каталога гарнитур — предупреждение',
               warns(lambda d: d['visual_language']['type'].update(note=f'заголовки — трекинг {floor - 0.01:+.3f} em'.replace('.', ',').replace('-', '−')),
                     'ниже нормы каталога гарнитур'))
        d = copy.deepcopy(base)
        d['visual_language']['type']['note'] = f'заголовки — трекинг {floor + 0.01:+.3f} em'.replace('.', ',')
        expect('трекинг заголовков не ниже нормы каталога — предупреждения нет', not check(ctx, d)['warnings'])
    d = copy.deepcopy(base)
    one_direction(d, 'strict')
    r = check(ctx, d)
    expect('одно направление при строгом бренде: схема проходит, предупреждение называет основание, 0 ошибок',
           r['ok'] and any('меньше трёх' in m and 'строгий бренд' in m for m in r['warnings']))
    d = copy.deepcopy(base)
    one_direction(d, 'open')
    r = check(ctx, d)
    expect('одно направление без основания: предупреждение с условием, 0 ошибок',
           r['ok'] and any('меньше трёх' in m and 'законно при строгом бренде' in m for m in r['warnings']))
    d = copy.deepcopy(base)
    d['moodboard'][0].update({'values': {'measured': ['H1 — 72 px на 1440, трекинг −2 %']}, 'source': 'customer', 'captured': '2026-09-24 1440x900'})
    expect('референс со значениями, источником и датой снятия проходит схему', check(ctx, d)['ok'])
    d = copy.deepcopy(base)
    d['lifecycle'].pop('history')
    expect('lifecycle без history проходит схему', check(ctx, d)['ok'])
    d = copy.deepcopy(base)
    d['handoff']['executor'] = {}
    expect('handoff: проекции только соседям из схемы (visual_dna, blender), чужой ключ — ошибка схемы', check(ctx, d)['schema'])
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, 'design', 'promo', 'art-direction.json')
        os.makedirs(os.path.dirname(p))
        seeded = copy.deepcopy(base)
        seeded.pop('concept')
        seeded['choice']['chosen'] = 'no-such-direction'
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(seeded, f, ensure_ascii=False)
        r = check(ctx, load(p), p)
        expect('файл проекта с посеянными ошибками: нет обязательного поля — находка схемы', any('concept' in m for m in r['schema']))
        seeded['concept'] = base['concept']
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(seeded, f, ensure_ascii=False)
        r = check(ctx, load(p), p)
        expect('файл проекта: ссылка на несуществующее направление — находка', any('no-such-direction' in m for m in r['rules']))
    print('selftest:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='*', help='файлы арт-дирекции; без них — примеры базы')
    ap.add_argument('--json', action='store_true', help='находки одним JSON в stdout')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    ctx = Ctx()
    if a.selftest:
        return selftest(ctx)
    return run_files(ctx, a.files or EXAMPLES, a.json)


if __name__ == '__main__':
    sys.exit(main())
