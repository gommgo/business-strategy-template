#!/usr/bin/env python3
"""spec_check.py — проверки и проекции подачи для исполнителя (creative-research · агент I · волна 3 · 2026-09-24).

Нужен Python с jsonschema ≥ 4.18 и pyyaml: 99-raw/tools/venv-I/bin/python (uv venv; только чтение чужих файлов).

Команды:
  blocks [--yaml F]                              block-treatments.yaml ↔ blocks.yaml site, effects.yaml, cliche-registry.yaml
  plan PLAN.yaml [--overlay T.yaml] [--out M.yaml] treatment v1 секций и страницы: схема page-plan v1 с treatment v1 + правила
  spec SPEC.yaml [--plan PLAN.yaml] [--overlay T.yaml]  motion-spec: схема + id, эффекты, токены, классы, пределы, LCP
  moments SPEC.yaml [--section ID]               строки «Moments» шаблона T7 kimi (brief.yaml decisions.motion.moments)
  motion-md SPEC.yaml [--out MOTION.md]          MOTION.md пакета kimi: таймлайн по секциям, раскадровка, reduce, телефон, пауза
  values SPEC.yaml --out DIR                     JSON чисел на секцию для модуля эффекта (правит Claude, код эффекта K3 не трогает)
  levels                                         списки effect:<id> по level_min из effects.yaml (для x-effect-levels схемы)
  --selftest                                     самопроверка на файлах базы и подброшенных ошибках
Коды выхода: 0 — нет error; 1 — есть error; 2 — сбой запуска. Overlay treatment (формат примеров базы):
  {overlay_version: "1.0", plan: <путь к page-plan site>, page: {treatment страницы}, sections: {<id секции>: {treatment}}}
"""
import argparse, copy, json, os, re, sys

try:
    import yaml
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except ImportError as e:  # pragma: no cover
    sys.stderr.write(f'нужны pyyaml и jsonschema ≥ 4.18 ({e}); запуск: 99-raw/tools/venv-I/bin/python\n')
    sys.exit(2)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('creative'))
APP = str(kbpaths.kb())
SITE = str(kbpaths.kb('site'))
P = {
    'blocks': os.path.join(SITE, '04-blocks', 'blocks.yaml'),
    'pp_schema': os.path.join(SITE, '10-playbooks-contracts', 'schemas', 'page-plan.schema.json'),
    'sm_schema': os.path.join(SITE, '10-playbooks-contracts', 'schemas', 'site-map.schema.json'),
    'levels': os.path.join(ROOT, '01-creative-direction', 'ambition-levels.yaml'),
    'effects': os.path.join(ROOT, '06-effects-catalog', 'effects.yaml'),
    'cliche': os.path.join(ROOT, '08-uniqueness-anti-slop', 'cliche-registry.yaml'),
    'tokens': os.path.join(ROOT, '04-visual-language', 'marketing-tokens.json'),
    't_schema': os.path.join(ROOT, '09-ai-execution-evaluation', 'treatment.schema.json'),
    'm_schema': os.path.join(ROOT, '09-ai-execution-evaluation', 'motion-spec.schema.json'),
    'bt': os.path.join(ROOT, '09-ai-execution-evaluation', 'block-treatments.yaml'),
    'gates': os.path.join(ROOT, '09-ai-execution-evaluation', 'effect-gates.yaml'),
}
LV = {'L0': 0, 'L1': 1, 'L2': 2}
PEAKS = {'L0': (0, 0), 'L1': (0, 2), 'L2': (2, 4)}          # E 05-motion/01 §5.5; A section_distribution
ACCENTS_MAX = {'L0': 1, 'L1': 3, 'L2': 4}                  # E §5.5 [гипотеза]
SIGNATURE_MAX = {'L0': 1, 'L1': 2, 'L2': 4}                # A signature_moves_max / «секции с фирменным приёмом»
LOOPS_MAX = {'L0': 1, 'L1': 2, 'L2': 3}                    # E §5.2
PROPS_L0 = {'transform', 'translate', 'scale', 'rotate', 'opacity', 'color', 'background-color'}
CHROME_ROLES = {'header', 'footer', 'utility', 'legal'}
ROLES = ['peak', 'accent', 'support', 'calm', 'pause', 'chrome']


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f) if p.endswith('.json') else yaml.safe_load(f)


class Report:
    def __init__(self):
        self.items = []

    def add(self, sev, code, where, msg):
        self.items.append((sev, code, where, msg))

    def dump(self, title):
        e = sum(1 for i in self.items if i[0] == 'error')
        w = sum(1 for i in self.items if i[0] == 'warning')
        print(f'== {title}: error {e}, warning {w}, info {len(self.items) - e - w}')
        for sev, code, where, msg in self.items:
            print(f'  {sev:7} {code:6} {where}: {msg}')
        return 1 if e else 0


# ── справочники ────────────────────────────────────────────────────────────────────────────────────────────
class Ctx:
    def __init__(self):
        self.effects = {e['id']: e for e in load(P['effects'])['effects']}
        self.blocks = load(P['blocks'])['blocks']
        reg = load(P['cliche'])
        self.cliches = {e['id'] for e in reg['entries']} | set((reg.get('id_aliases') or {}).keys())
        lv = load(P['levels'])
        caps = lv.get('section_caps') or {}
        self.conv_roles = set(caps.get('conversion_roles_max_L0') or [])
        self.conv_blocks = set(caps.get('conversion_blocks_max_L0') or [])
        self.tokens = {}
        tok = load(P['tokens'])
        self._flat(tok.get('motion', {}), 'motion')
        self.motion_tokens = dict(self.tokens)
        for k, v in tok.items():
            if not k.startswith('$') and k != 'motion':
                self._flat(v, k)
        self.all_tokens = set(self.tokens)
        self.tokens = self.motion_tokens
        self.bt = load(P['bt'])

    def _flat(self, node, path):
        if isinstance(node, dict):
            if '$value' in node:
                self.tokens[path] = node['$value']
                return
            for k, v in node.items():
                if not k.startswith('$'):
                    self._flat(v, f'{path}.{k}')

    def token_ms(self, ref):
        v = self.tokens.get(ref)
        if isinstance(v, dict) and 'value' in v:
            return float(v['value'])
        if isinstance(v, (int, float)):
            return float(v)
        return None

    def scale_ms(self):
        out = set()
        for k, v in self.tokens.items():
            if k.startswith('motion.marketing.duration.') or k.startswith('motion.marketing.stagger.'):
                if isinstance(v, dict) and v.get('unit') == 'ms':
                    out.add(float(v['value']))
        return out

    def css_var(self, name):
        m = {'dur': 'duration', 'ease': 'easing', 'stagger': 'stagger', 'shift': 'distance', 'lift': 'distance', 'magnet': 'distance',
             'scale': 'scale', 'breathe': 'duration'}
        mm = re.match(r'--mm-([a-z]+)-(.+)$', name)
        if not mm:
            return None
        grp, rest = mm.groups()
        if grp in ('shift', 'lift', 'magnet'):
            rest = f'{grp}-{rest}'
        return self.token_ms(f'motion.marketing.{m.get(grp, grp)}.{rest}')

    def block_eff(self, bid):
        """Эффекты блока по уровням (накопительно) и поля блока с наследованием семейства."""
        b = self.bt['blocks'].get(bid)
        if b is None:
            return None
        fam = self.bt['families'].get(b.get('family'), {})
        res = {k: v for k, v in fam.items()}
        res.update(b)
        eff = res.get('effects') or {}
        acc, out = [], {}
        for L in ('L0', 'L1', 'L2'):
            acc = acc + list(eff.get(L) or [])
            out[L] = set(acc)
        res['_eff'] = out
        return res


def registry(t_schema):
    res = []
    for key in ('pp_schema', 'sm_schema'):
        d = load(P[key])
        res.append((d['$id'], Resource.from_contents(d, default_specification=DRAFT202012)))
    res.append((t_schema['$id'], Resource.from_contents(t_schema, default_specification=DRAFT202012)))
    alias = copy.deepcopy(t_schema)
    alias['$id'] = 'urn:app-design:creative-research:treatment:0'       # как будто site переключил $ref на v1
    res.append((alias['$id'], Resource.from_contents(alias, default_specification=DRAFT202012)))
    return Registry().with_resources(res)


# ── blocks ─────────────────────────────────────────────────────────────────────────────────────────────────
def cmd_blocks(ctx, R, path=None):
    bt = load(path) if path else ctx.bt
    site_ids, our_ids = set(ctx.blocks), set(bt['blocks'])
    for b in sorted(site_ids - our_ids):
        R.add('error', 'BT-01', b, 'блок есть в blocks.yaml site, но нет в block-treatments.yaml')
    for b in sorted(our_ids - site_ids):
        R.add('error', 'BT-01', b, 'блока нет в blocks.yaml site')
    fams = bt.get('families') or {}
    for name, fam in list(fams.items()) + [(k, v) for k, v in bt['blocks'].items()]:
        where = f'{"family " if name in fams and name not in bt["blocks"] else ""}{name}'
        for L, lst in (fam.get('effects') or {}).items():
            if L not in LV:
                R.add('error', 'BT-02', where, f'ключ уровня {L}')
                continue
            for ref in lst or []:
                eid = ref.split(':', 1)[1] if ref.startswith('effect:') else None
                e = ctx.effects.get(eid)
                if e is None:
                    R.add('error', 'BT-02', where, f'{ref} нет в effects.yaml')
                elif LV[e['level_min']] > LV[L]:
                    R.add('error', 'BT-03', where, f'{ref} level_min {e["level_min"]} > {L}')
        for c in fam.get('avoid') or []:
            if not c.startswith('cliche:') or c[7:] not in ctx.cliches:
                R.add('error', 'BT-04', where, f'{c} нет в cliche-registry.yaml')
        for r in fam.get('roles') or []:
            if r not in ROLES:
                R.add('error', 'BT-08', where, f'роль {r}')
        if fam.get('level_max') and fam['level_max'] not in LV:
            R.add('error', 'BT-09', where, f'level_max {fam["level_max"]}')
    for bid, b in bt['blocks'].items():
        if b.get('family') not in fams:
            R.add('error', 'BT-07', bid, f'семейство {b.get("family")} не описано')
        site = ctx.blocks.get(bid) or {}
        svars = {v.get('id') for v in site.get('variants') or []}
        seen = set()
        full = ctx.block_eff(bid)
        for vv in b.get('visual_variants') or []:
            if vv['id'] in seen:
                R.add('error', 'BT-06', bid, f'повтор visual_variant {vv["id"]}')
            seen.add(vv['id'])
            for s in vv.get('structural') or []:
                if svars and s not in svars:
                    R.add('error', 'BT-05', f'{bid}.{vv["id"]}', f'структурного варианта {s} нет у блока site ({sorted(svars)})')
            for L in vv.get('levels') or []:
                if full and LV.get(L, 9) > LV.get(full.get('level_max', 'L2'), 2):
                    R.add('error', 'BT-09', f'{bid}.{vv["id"]}', f'уровень {L} выше level_max {full.get("level_max")}')
    return R


# ── plan ───────────────────────────────────────────────────────────────────────────────────────────────────
def merge_overlay(plan, ov, R):
    plan = copy.deepcopy(plan)
    pg = plan.setdefault('page', {})
    if ov.get('page') is not None:
        pg['treatment'] = ov['page']
    ids = {s['id']: s for s in plan.get('sections') or []}
    for sid, t in (ov.get('sections') or {}).items():
        if sid not in ids:
            R.add('error', 'TR-09', f'overlay.{sid}', 'секции нет в плане (id v1: роль или блок)')
            continue
        ids[sid]['treatment'] = t
    for sid in ids:
        if sid not in (ov.get('sections') or {}):
            R.add('info', 'TR-00', sid, 'treatment взят из плана site (v0), overlay его не задаёт')
    return plan


def section_targets(s):
    sid = s['id']
    out = {sid}
    for kind, lst in (s.get('slots') or {}).items():
        for x in lst or []:
            out.add(f'{sid}.{x["id"]}')
            g = x.get('group')
            an = x.get('anatomy')
            if g:
                base = re.sub(r'-\d+$', '', g)
                out |= {f'{sid}.{g}', f'{sid}.{base}'}
                if an and '.' in an:
                    el = an.split('.', 1)[1]
                    out |= {f'{sid}.{g}.{el}', f'{sid}.{base}.{el}'}
            if an:
                out.add(f'{sid}.{an}')
                if '.' in an:
                    out.add(f'{sid}.{an.split(".")[0]}')
    return out


def target_ok(t, targets, sid=None):
    if t in ('section', 'page') or t in targets:
        return True
    parts = t.split('.')
    return len(parts) >= 2 and parts[1].startswith('fx-') and (sid is None or parts[0] == sid)


def is_conv(ctx, s):
    role, bid = s.get('role'), s.get('block')
    acts = (s.get('slots') or {}).get('action') or []
    return role in ctx.conv_roles or bid in ctx.conv_blocks or any(a.get('form') or a.get('slot') == 'form' for a in acts)


def cmd_plan(ctx, R, plan_path, overlay_path=None, out=None, spec=None):
    plan = load(plan_path)
    if overlay_path:
        ov = load(overlay_path)
        plan = merge_overlay(plan, ov, R)
    t_schema = load(P['t_schema'])
    reg = registry(t_schema)
    v = Draft202012Validator(load(P['pp_schema']), registry=reg)
    for e in sorted(v.iter_errors(plan), key=lambda x: list(x.path)):
        R.add('error', 'TR-S', '/'.join(str(p) for p in e.path), e.message[:220])
    pg = plan.get('page') or {}
    lvl = pg.get('ambition_level')
    pt = pg.get('treatment') or {}
    ms = pt.get('motion_system') or {}
    flow = [s for s in plan.get('sections') or [] if s.get('role') not in CHROME_ROLES]
    peaks, accents, sigs, used_refs, roles_seq = [], [], [], {}, []
    spec_ids = set()
    if spec is not None:
        spec_ids = {s['id'] for s in spec.get('sections') or []}
    for s in plan.get('sections') or []:
        sid, t = s['id'], s.get('treatment') or {}
        if not t:
            continue
        w = f'{sid}'
        tl = t.get('level') or lvl
        bl = ctx.block_eff(s.get('block'))
        if tl and lvl and LV[tl] > LV[lvl]:
            R.add('error', 'TR-01', w, f'уровень секции {tl} выше уровня страницы {lvl}')
        conv = is_conv(ctx, s)
        if conv and tl and tl != 'L0':
            R.add('error', 'TR-02', w, f'секция конверсии ({s.get("role")}, {s.get("block")}) — только L0')
        effs = t.get('effects') or []
        if conv and any(e.get('purpose') == 'signature' for e in effs):
            R.add('error', 'TR-03', w, 'фирменный эффект в секции конверсии')
        if bl is not None and tl and LV[tl] > LV[bl.get('level_max', 'L2')]:
            R.add('error', 'TR-23', w, f'уровень {tl} выше level_max блока {s.get("block")} ({bl.get("level_max")})')
        vr = t.get('visual_role')
        if s.get('role') in CHROME_ROLES and vr not in (None, 'chrome'):
            R.add('warning', 'TR-22', w, f'служебная роль {s.get("role")} с visual_role {vr}')
        if bl is not None and vr and vr not in (bl.get('roles') or ROLES):
            R.add('warning', 'TR-24', w, f'visual_role {vr} не из ролей блока {bl.get("roles")}')
        if vr == 'peak':
            peaks.append(sid)
        if vr == 'accent':
            accents.append(sid)
        if any(e.get('purpose') == 'signature' for e in effs):
            sigs.append(sid)
        if s in flow:
            roles_seq.append((sid, vr))
        targets = section_targets(s)
        for i, e in enumerate(effs):
            we = f'{w}.effects[{i}]'
            eid = e['ref'].split(':', 1)[1]
            ce = ctx.effects.get(eid)
            if ce is None:
                R.add('error', 'TR-10', we, f'{e["ref"]} нет в effects.yaml')
                continue
            if tl and LV[ce['level_min']] > LV[tl]:
                R.add('error', 'TR-11', we, f'{e["ref"]} level_min {ce["level_min"]} > уровня секции {tl}')
            if bl is not None and tl and e['ref'] not in bl['_eff'].get(tl, set()):
                R.add('warning', 'TR-12', we, f'{e["ref"]} не в списке блока {s.get("block")} для {tl} (block-treatments.yaml)')
            if e.get('target') and not target_ok(e['target'], targets, sid):
                R.add('error', 'TR-09', we, f'target {e["target"]} не найден в секции (слоты, группы, anatomy, fx-*)')
            kind = (ce.get('motion') or {}).get('kind')
            if e.get('class') and kind and e['class'] != kind:
                R.add('warning', 'TR-18', we, f'class {e["class"]} ≠ motion.kind каталога {kind}')
            lim = ce.get('limits') or {}
            for k, val in (e.get('params') or {}).items():
                for lk, lv in lim.items():
                    if lv is None or not isinstance(val, (int, float)):
                        continue
                    if lk == f'{k}_max' and val > lv or lk == f'{k}_min' and val < lv:
                        R.add('error', 'TR-27', we, f'params.{k}={val} вне limits {lk}={lv}')
        tok = (t.get('background') or {}).get('token')
        if tok and tok not in ctx.all_tokens:
            R.add('warning', 'TR-28', w, f'background.token {tok} нет в marketing-tokens.json')
        vv = t.get('visual_variant')
        if vv and bl is not None:
            vmap = {x['id']: x for x in bl.get('visual_variants') or []}
            if vv not in vmap:
                R.add('error', 'TR-13', w, f'visual_variant {vv} нет у блока {s.get("block")} ({sorted(vmap)})')
            elif s.get('variant') and vmap[vv].get('structural') and s['variant'] not in vmap[vv]['structural']:
                R.add('warning', 'TR-13', w, f'visual_variant {vv} задуман для {vmap[vv]["structural"]}, а вариант плана {s["variant"]}')
            elif vmap.get(vv, {}).get('levels') and tl not in vmap[vv]['levels']:
                R.add('warning', 'TR-13', w, f'visual_variant {vv} задуман для уровней {vmap[vv]["levels"]}, секция {tl}')
        for r in t.get('refs') or []:
            used_refs.setdefault(r, []).append(sid)
        if t.get('loop_control') == 'page-toggle' and not ms.get('reduce_toggle'):
            R.add('error', 'TR-16', w, 'loop_control page-toggle без page.treatment.motion_system.reduce_toggle: true')
        if (t.get('mobile') or {}).get('strategy') in ('simplified', 'separate-asset') and not (t.get('mobile') or {}).get('note'):
            R.add('warning', 'TR-17', w, 'mobile simplified/separate-asset без note: объявите, что меняется')
        if (t.get('reduce') or {}).get('strategy') == 'custom' and not (t.get('reduce') or {}).get('note'):
            R.add('warning', 'TR-26', w, 'reduce custom без note')
        if tl and (t.get('loops') or 0) > LOOPS_MAX[tl]:
            R.add('error', 'TR-21', w, f'петель {t["loops"]} > {LOOPS_MAX[tl]} для {tl}')
        msr = t.get('motion_spec_ref')
        if msr and spec is not None and '#/sections/' in msr and msr.split('#/sections/')[1] not in spec_ids:
            R.add('error', 'TR-15', w, f'motion_spec_ref → секции {msr.split("#/sections/")[1]} нет в motion-spec')
        if spec is not None and vr in ('peak', 'accent') and sid not in spec_ids:
            R.add('warning', 'TR-15', w, f'{vr} без раздела в motion-spec')
    if lvl:
        lo, hi = PEAKS[lvl]
        if not lo <= len(peaks) <= hi:
            R.add('error', 'TR-04', 'page', f'пиков {len(peaks)} {peaks}, норма {lo}–{hi} для {lvl}')
        if len(accents) > ACCENTS_MAX[lvl]:
            R.add('error', 'TR-05', 'page', f'акцентов {len(accents)} {accents} > {ACCENTS_MAX[lvl]} для {lvl}')
        if len(sigs) > SIGNATURE_MAX[lvl]:
            R.add('error', 'TR-06', 'page', f'секций с signature {len(sigs)} {sigs} > {SIGNATURE_MAX[lvl]} для {lvl}')
        if lvl == 'L0' and accents and any(a != 'hero' for a in accents):
            R.add('error', 'TR-05', 'page', f'на L0 акцент — только hero: {accents}')
    if pt.get('peaks') is not None and set(pt['peaks']) != set(peaks):
        R.add('error', 'TR-07', 'page', f'page.treatment.peaks {pt["peaks"]} ≠ секции-пики {peaks}')
    if pt.get('accents') is not None and set(pt['accents']) != set(accents):
        R.add('error', 'TR-08', 'page', f'page.treatment.accents {pt["accents"]} ≠ секции-акценты {accents}')
    if pt.get('signature_sections') is not None and set(pt['signature_sections']) != set(sigs):
        R.add('error', 'TR-08', 'page', f'signature_sections {pt["signature_sections"]} ≠ {sigs}')
    if ms.get('smooth_scroll') and lvl != 'L2':
        R.add('error', 'TR-25', 'page', f'плавная прокрутка на {lvl} (только L2)')
    for i in range(1, len(roles_seq)):
        if roles_seq[i][1] == 'peak' and roles_seq[i - 1][1] == 'peak':
            sev = 'error' if lvl != 'L2' else 'warning'
            R.add(sev, 'TR-19', f'{roles_seq[i - 1][0]}+{roles_seq[i][0]}', 'два пика подряд (L2 — только одна сквозная сцена)')
    if lvl == 'L2':
        idx = [i for i, (_, r) in enumerate(roles_seq) if r == 'peak']
        for a, b in zip(idx, idx[1:]):
            if not any(r in ('calm', 'pause') for _, r in roles_seq[a + 1:b]):
                R.add('error', 'TR-20', f'{roles_seq[a][0]}…{roles_seq[b][0]}', 'между пиками нет calm или pause')
    for r, where in used_refs.items():
        if len(where) > 1:
            R.add('error', 'TR-14', 'page', f'референс {r} в {len(where)} секциях {where}')
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            yaml.safe_dump(plan, f, allow_unicode=True, sort_keys=False, width=140)
    return plan


# ── spec ───────────────────────────────────────────────────────────────────────────────────────────────────
def dur_ms(ctx, d, base):
    if not d:
        return None
    if 'ms' in d:
        return float(d['ms'])
    if 'token' in d:
        return ctx.token_ms(d['token'])
    if 'share' in d and base:
        return float(d['share']) * base
    return None


def px_of(ctx, s):
    """Максимальное смещение в px из строки transform; var(--mm-*) — по токенам."""
    if isinstance(s, (int, float)):
        return None
    vals = [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)px', s or '')]
    for name in re.findall(r'var\((--mm-[a-z0-9-]+)\)', s or ''):
        v = ctx.css_var(name)
        if v is not None:
            vals.append(v)
    return max((abs(x) for x in vals), default=None)


def cmd_spec(ctx, R, spec_path, plan_path=None, overlay_path=None):
    spec = load(spec_path)
    v = Draft202012Validator(load(P['m_schema']))
    for e in sorted(v.iter_errors(spec), key=lambda x: list(x.path)):
        R.add('error', 'MS-S', '/'.join(str(p) for p in e.path), e.message[:220])
    if any(i[1] == 'MS-S' for i in R.items):
        return spec
    lvl = spec['level']
    page = spec['page']
    base = (page.get('base') or {}).get('duration_ms')
    plan = None
    if plan_path:
        plan = load(plan_path)
        if overlay_path:
            plan = merge_overlay(plan, load(overlay_path), Report())
        if (plan.get('page') or {}).get('ambition_level') not in (None, lvl):
            R.add('error', 'MS-01', 'level', f'уровень спецификации {lvl} ≠ уровню плана {plan["page"]["ambition_level"]}')
    psec = {s['id']: s for s in (plan or {}).get('sections') or []}
    scale = ctx.scale_ms()
    for key in ('lcp',):
        t = page[key]['target']
        if plan and not any(target_ok(t, section_targets(s)) for s in psec.values()):
            R.add('error', 'MS-03', f'page.{key}', f'target {t} не найден в плане')
    first_flow = next((s['id'] for s in (plan or {}).get('sections') or [] if s.get('role') not in CHROME_ROLES), None)
    for si, sec in enumerate(spec['sections']):
        sid = sec['id']
        w = sid
        ps = psec.get(sid)
        if plan and ps is None:
            R.add('error', 'MS-01', w, 'секции нет в плане (id v1)')
        tr = (ps or {}).get('treatment') or {}
        if tr.get('visual_role') and tr['visual_role'] != sec['role']:
            R.add('error', 'MS-02', w, f'role {sec["role"]} ≠ treatment.visual_role {tr["visual_role"]}')
        slvl = sec.get('level') or tr.get('level') or lvl
        targets = section_targets(ps) if ps else None
        scene = sec.get('scene') or {}
        st_ids = {x['id'] for x in scene.get('stations') or []}
        L = scene.get('length_vh')
        if L is not None:
            cap = ctx.token_ms('motion.marketing.scroll.pin-l1-max-vh') if slvl == 'L1' else ctx.token_ms('motion.marketing.scroll.pin-l2-max-vh')
            if slvl == 'L0' and scene.get('pin') not in (None, 'none', 'sticky'):
                R.add('error', 'MS-13', w, 'закрепление со скрабом на L0 (только sticky)')
            elif cap and scene.get('pin') not in (None, 'none') and L > cap:
                R.add('error', 'MS-13', w, f'длина сцены {L}vh > {cap:g}vh для {slvl}')
            nst = len(scene.get('stations') or [])
            if nst >= 2 and L / (nst - 1) > 150:
                R.add('warning', 'MS-13', w, f'шаг между станциями {L / (nst - 1):.0f}vh > 150vh')
        if sec['reduce']['strategy'] == 'stations' and not st_ids:
            R.add('error', 'MS-18', w, 'reduce stations без scene.stations')
        if (tr.get('reduce') or {}).get('stations') and st_ids and tr['reduce']['stations'] != len(st_ids):
            R.add('warning', 'MS-17', w, f'treatment.reduce.stations {tr["reduce"]["stations"]} ≠ станций сцены {len(st_ids)}')
        loops = 0
        t_end = 0.0
        tr_effs = {e['ref'] for e in tr.get('effects') or []}
        used_effs = set()
        for m in sec['moments']:
            wm = f'{sid}.{m["id"]}'
            for tg in [m['target']] + list(m.get('stagger_targets') or []):
                if targets is not None and not target_ok(tg, targets, sid):
                    R.add('error', 'MS-03', wm, f'target {tg} не найден (слоты, группы, anatomy, fx-*)')
            if m.get('effect'):
                used_effs.add(m['effect'])
                ce = ctx.effects.get(m['effect'].split(':', 1)[1])
                if ce is None:
                    R.add('error', 'MS-04', wm, f'{m["effect"]} нет в effects.yaml')
                else:
                    kind = (ce.get('motion') or {}).get('kind')
                    kinds = kind if isinstance(kind, list) else [kind]   # S1b 2026-09-25 (X-64): motion.kind — строка или список классов
                    if kind and m['class'] not in kinds and 'static' not in kinds:
                        R.add('warning', 'MS-05', wm, f'class {m["class"]} ≠ motion.kind {kind}')
                    if LV[ce['level_min']] > LV[slvl]:
                        R.add('error', 'MS-04', wm, f'{m["effect"]} level_min {ce["level_min"]} > {slvl}')
                    lim = ce.get('limits') or {}
                    sp = (m.get('loop') or {}).get('speed_px_s')
                    if sp is not None and lim.get('speed_px_s_max') and not lim.get('speed_px_s_min', 0) <= sp <= lim['speed_px_s_max']:
                        R.add('error', 'MS-12', wm, f'скорость {sp} px/с вне {lim.get("speed_px_s_min")}–{lim["speed_px_s_max"]}')
            for fld in ('duration', 'easing'):
                d = m.get(fld) or {}
                if 'token' in d and d['token'] not in ctx.tokens:
                    R.add('error', 'MS-06', wm, f'токена {d["token"]} нет в marketing-tokens.json')
            d_ms = dur_ms(ctx, m.get('duration'), base)
            if 'ms' in (m.get('duration') or {}) and d_ms not in scale:
                R.add('warning', 'MS-07', wm, f'{d_ms:g} мс вне шкалы motion.marketing (CRV-MO-14): возьмите токен или долю базы')
            for tk in m['tracks']:
                prop = tk['property']
                if slvl == 'L0' and prop not in PROPS_L0:
                    R.add('error', 'MS-08', wm, f'свойство {prop} на L0 (только transform, opacity, цвет — E П12)')
                if prop == 'filter':
                    for b in re.findall(r'blur\((\d+(?:\.\d+)?)px\)', f'{tk.get("from", "")} {tk.get("to", "")}'):
                        if float(b) > 8:
                            R.add('error', 'MS-08', wm, f'blur {b}px > 8 px (E П12)')
                if prop == 'opacity' and str(tk.get('from')) in ('0', '0.0') and m['class'] == 'one-shot' and sid == first_flow:
                    R.add('warning', 'MS-19', wm, 'появление из opacity 0 в первом экране: возьмите .01 (кандидат LCP сохраняется — E 02 §10)')
            is_lcp = m.get('lcp') == 'is-lcp' or m['target'] == page['lcp']['target']
            if is_lcp:
                if page['lcp']['entrance'] == 'none':
                    R.add('error', 'MS-09', wm, f'элемент LCP {page["lcp"]["target"]} анимируется, а page.lcp.entrance = none')
                for tk in m['tracks']:
                    if tk['property'] not in ('transform', 'translate'):
                        R.add('error', 'MS-09', wm, f'LCP-элемент: свойство {tk["property"]} (только transform ≤ 24 px)')
                    px = px_of(ctx, tk.get('from'))
                    if px is not None and px > 24:
                        R.add('error', 'MS-09', wm, f'LCP-элемент: сдвиг {px:g} px > 24')
            if m['class'] == 'one-shot' and m['trigger']['type'] == 'load' and sid == first_flow:
                st = m.get('stagger') or {}
                each = dur_ms(ctx, st.get('each'), base) or 0
                n = 1 + len(m.get('stagger_targets') or [])
                end = (m['trigger'].get('delay_ms') or 0) + (d_ms or 0) + each * (n - 1)
                t_end = max(t_end, end)
            st = m.get('stagger') or {}
            if st.get('each'):
                each = dur_ms(ctx, st['each'], base) or 0
                if not 40 <= each <= 80:
                    R.add('warning', 'MS-11', wm, f'стаггер {each:g} мс вне 40–80 (E 01 §7.4)')
                if st.get('max_items') and each * (st['max_items'] - 1) > 600:
                    R.add('error', 'MS-11', wm, f'сумма стаггера {each * (st["max_items"] - 1):g} мс > 600')
            if m['class'] == 'loop':
                loops += 1
                per = (m.get('loop') or {}).get('period_ms')
                if per and 2500 <= per <= 6000:
                    fam = (ctx.effects.get((m.get('effect') or ':').split(':', 1)[1]) or {}).get('family')
                    sev = 'error' if fam in ('background', '3d', 'video') else 'warning'
                    R.add(sev, 'MS-15', wm, f'период петли {per:g} мс в полосе 2,5–6 с (вестибулярный риск, E 01 §6.3)')
                if (m.get('pause') or {}).get('control') == 'page-toggle' and not page['toggle'].get('required'):
                    R.add('error', 'MS-14', wm, 'пауза page-toggle, а page.toggle.required = false')
            if m.get('scrub', {}).get('snap') == 'stations' and slvl != 'L2':
                R.add('error', 'MS-13', wm, 'привязка к станциям (snap) — только L2')
        if sid == first_flow and t_end > 1200:
            R.add('error', 'MS-10', w, f'сцена первого экрана {t_end:g} мс > 1 200')
        if loops > LOOPS_MAX.get(slvl, 3):
            R.add('error', 'MS-14', w, f'петель {loops} > {LOOPS_MAX[slvl]} для {slvl}')
        gids = set()
        if os.path.exists(P['gates']):
            gids = {g.get('id') for g in (load(P['gates']).get('gates') or [])}
        for ac in sec.get('acceptance') or []:
            if ac.get('gate') and gids and ac['gate'] not in gids:
                R.add('warning', 'MS-22', f'{sid}.{ac["id"]}', f'ворот {ac["gate"]} нет в effect-gates.yaml (K)')
        for ef in sorted(tr_effs - used_effs):
            R.add('warning', 'MS-21', w, f'эффект treatment {ef} не описан ни одним моментом')
    if plan:
        for sid, s in psec.items():
            vr = ((s.get('treatment') or {}).get('visual_role'))
            if vr in ('peak', 'accent') and sid not in {x['id'] for x in spec['sections']}:
                R.add('warning', 'MS-16', sid, f'{vr} плана без раздела motion-spec')
    return spec


# ── проекции ───────────────────────────────────────────────────────────────────────────────────────────────
def fmt_dur(ctx, d, base):
    ms = dur_ms(ctx, d, base)
    return f'{ms:g} ms' if ms is not None else '?'


def fmt_ease(ctx, e):
    if not e:
        return 'no easing'
    if e.get('none'):
        return 'no easing (scrub)'
    if 'css' in e:
        return e['css']
    v = ctx.tokens.get(e.get('token'))
    return f'cubic-bezier({", ".join(f"{x:g}" for x in v)})' if isinstance(v, list) else e.get('token', '?')


def fmt_trigger(m, sec):
    t = m['trigger']
    ty = t['type']
    if ty in ('scroll-scrub', 'pin-scrub'):
        if t.get('range_vh'):
            r = t['range_vh']
            s = f'scroll {r.get("start", 0):g}–{r.get("start", 0) + r["length"]:g}vh of #{sec["id"]}'
        elif t.get('progress'):
            s = f'scroll progress {t["progress"]["start"]:g}–{t["progress"]["end"]:g} of #{sec["id"]}'
        else:
            s = f'scroll {t["range"]["start"]} → {t["range"]["end"]} of ' + (f'`{t["subject"]}`' if t.get('subject') else f'#{sec["id"]}')
        return s + (' (pinned)' if ty == 'pin-scrub' else '')
    extra = []
    if t.get('delay_ms'):
        extra.append(f'+{t["delay_ms"]:g} ms')
    if t.get('after'):
        extra.append(f'after {t["after"]}')
    if ty == 'in-view' and t.get('threshold') is not None:
        extra.append(f'{int(t["threshold"] * 100)} % visible, once' if t.get('once', True) else f'{int(t["threshold"] * 100)} % visible')
    return ty + (f' ({", ".join(extra)})' if extra else '')


def moment_line(ctx, m, sec, base):
    el = ', '.join([m['target']] + list(m.get('stagger_targets') or [])) + f' [data-moment={m["id"]}]' + (f' `{m["selector_hint"]}`' if m.get('selector_hint') else '')
    props = ', '.join(f'{tk["property"]} {tk["from"]} -> {tk["to"]}' if 'from' in tk else
                      f'{tk["property"]} ' + ' / '.join(f'{k["at"]:g}:{k["value"]}' for k in tk['keyframes']) for tk in m['tracks'])
    if m['class'] in ('scroll-linked',):
        timing = 'progress = scroll' + (f', smoothing {m["scrub"]["smoothing_s"]:g} s' if m.get('scrub', {}).get('smoothing_s') else '')
    elif m['class'] == 'loop':
        lp = m.get('loop') or {}
        timing = (f'{lp["speed_px_s"]:g} px/s' if lp.get('speed_px_s') else f'period {lp.get("period_ms", 0):g} ms') + ', infinite'
    else:
        timing = fmt_dur(ctx, m.get('duration'), base)
    parts = [f'{fmt_trigger(m, sec)} -> {el} -> {props}', timing, fmt_ease(ctx, m.get('easing'))]
    st = m.get('stagger') or {}
    if st.get('each'):
        parts.append(f'stagger {fmt_dur(ctx, st["each"], base)} ({st.get("order", "dom")})')
    red = m['reduce']
    parts.append(f'reduced motion: {red["strategy"]}' + (f' — {red["describe"]}' if red.get('describe') else ''))
    if m.get('mobile'):
        parts.append(f'phone: {m["mobile"]["strategy"]}' + (f' — {m["mobile"]["describe"]}' if m['mobile'].get('describe') else ''))
    if m.get('pause', {}).get('control') not in (None, 'not-needed'):
        parts.append(f'pause: {m["pause"]["control"]}')
    if m.get('lcp') == 'is-lcp':
        parts.append('LCP element: transform only')
    return '; '.join(parts)


def cmd_moments(ctx, spec, section=None):
    base = (spec['page'].get('base') or {}).get('duration_ms')
    lines = []
    for sec in spec['sections']:
        if section and sec['id'] != section:
            continue
        for m in sec['moments']:
            lines.append(moment_line(ctx, m, sec, base))
    for i, l in enumerate(lines, 1):
        print(f'{i}. {l}')
    return lines


def cmd_motion_md(ctx, spec, out=None):
    pg = spec['page']
    base = (pg.get('base') or {}).get('duration_ms')
    L = [f'# MOTION — {spec["id"]}', '',
         f'<!-- motion-spec {spec["motion_spec_version"]} · {spec["checked_at"]} · сгенерировано spec_check.py motion-md; правится спецификация, не этот файл -->', '',
         f'Motion thesis: {pg["thesis"]}']
    if pg.get('character'):
        L.append(f'Character: {", ".join(pg["character"])}.')
    if base:
        L.append(f'Base duration: {base:g} ms; parts use shares of it.')
    if pg.get('primitives'):
        L.append(f'Entrance system (only these primitives): {", ".join(pg["primitives"])}; sections without moments do not animate.')
    lc = pg['lcp']
    L.append(f'LCP element: `{lc["target"]}` — ' + ('no animation at all.' if lc['entrance'] == 'none' else 'transform only (≤ 24 px), never from opacity 0 or a line mask.'))
    tg = pg['toggle']
    L.append('Motion toggle: ' + (f'required — attribute `data-motion` on <html> with states {", ".join(tg.get("states", []))}; '
                                  f'placement {tg.get("placement", "sticky-header")}; it also pauses every loop.' if tg['required'] else 'not required.'))
    sc = pg.get('scroll') or {}
    L.append('Scrolling: native' + (' + smooth scroll' if sc.get('smooth') else '') + '; never change scroll speed or direction.')
    L.append('Markup contract: data-section="<section id>" on each section, data-slot="<slot id>", data-group="<group-N>", data-fx="<name>" on '
             'decorative elements (targets <section>.fx-<name>), data-moment="<moment id>" on the element a moment moves, data-effect="<effect id>" '
             'for effect modules. Checks find elements by these attributes.')
    allowed = pg.get('properties_allowed')
    if allowed:
        L.append(f'Animate only: {", ".join(allowed)}. Never width, height, top, left, margin, padding; never `transition: all`.')
    for n in pg.get('never') or []:
        L.append(f'- Never: {n}')
    L.append('')
    for sec in spec['sections']:
        L.append(f'## #{sec["id"]} — {sec["role"]}' + (f' · {sec["intent"]}' if sec.get('intent') else ''))
        scn = sec.get('scene') or {}
        if scn:
            L.append(f'Scene: pin {scn.get("pin", "none")}, length {scn.get("length_vh", "—")}vh (phone {scn.get("length_vh_mobile", "—")}vh).')
            for stt in scn.get('stations') or []:
                pos = f'at {stt["at"]:g}' if 'at' in stt else f'when `{stt["anchor"]}` is at {stt.get("anchor_line", "viewport-center")}'
                L.append(f'- station {stt["id"]} {pos}: {stt["describe"]}')
        if sec['moments']:
            L += ['', '| # | moment | class | trigger → element → property | time / range | easing | reduced motion | phone |', '|---|---|---|---|---|---|---|---|']
            for i, m in enumerate(sec['moments'], 1):
                props = '; '.join(f'{tk["property"]} {tk.get("from", "")} → {tk.get("to", "")}' for tk in m['tracks'])
                timing = moment_line(ctx, m, sec, base).split('; ')[1]
                L.append(f'| {i} | {m["id"]} | {m["class"]} | {fmt_trigger(m, sec)} → `{m["target"]}` → {props} | {timing} | {fmt_ease(ctx, m.get("easing"))} | '
                         f'{m["reduce"]["strategy"]} | {(m.get("mobile") or {}).get("strategy", "same")} |')
        L.append('')
        L.append(f'Reduced motion for the section: {sec["reduce"]["strategy"]} — {sec["reduce"]["describe"]}')
        L.append(f'Phone: {sec["mobile"]["strategy"]} — {sec["mobile"]["describe"]}')
        for fr in (sec.get('storyboard') or {}).get('frames') or []:
            at = ', '.join(f'{k} {v}' for k, v in fr['at'].items())
            L.append(f'- frame {fr["id"]} ({fr["viewport"]}, {at}): {fr["describe"]}' + (f' Check: {fr["check"]}' if fr.get('check') else ''))
        for rf in sec.get('references') or []:
            L.append(f'- reference {rf["id"]} ({rf["kind"]}{", " + rf["file"] if rf.get("file") else ""}):')
            for tk in rf['take']:
                span = f'{tk.get("from", "")}–{tk.get("to", "")} ' if tk.get('from') else ''
                L.append(f'  - Take {span}{tk["what"]}')
            for d in rf['do_not_take']:
                L.append(f'  - Do not take: {d}')
        L.append('')
    txt = '\n'.join(L)
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(txt)
    else:
        print(txt)
    return txt


def cmd_values(ctx, spec, out):
    os.makedirs(out, exist_ok=True)
    base = (spec['page'].get('base') or {}).get('duration_ms')
    files = []
    for sec in spec['sections']:
        d = {'spec': spec['id'], 'checked_at': spec['checked_at'], 'section': sec['id'], 'scene': sec.get('scene') or {}, 'moments': {}}
        for m in sec['moments']:
            e = m.get('easing') or {}
            ez = ctx.tokens.get(e.get('token')) if e.get('token') else e.get('css')
            mv = {'class': m['class'], 'duration_ms': dur_ms(ctx, m.get('duration'), base), 'easing': ez,
                  'stagger_ms': dur_ms(ctx, (m.get('stagger') or {}).get('each'), base), 'trigger': m['trigger'],
                  'tracks': m['tracks'], 'reduce': m['reduce']['strategy']}
            for k in ('loop', 'scrub', 'spring', 'params'):
                if m.get(k):
                    mv[k] = m[k]
            if m.get('tunable'):
                mv['tunable'] = m['tunable']
            d['moments'][m['id']] = mv
        p = os.path.join(out, f'{sec["id"]}.motion.json')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        files.append(p)
    print('\n'.join(files))
    return files


def cmd_levels(ctx):
    out = {'L1': [], 'L2': []}
    for eid, e in ctx.effects.items():
        if e['level_min'] in out:
            out[e['level_min']].append(f'effect:{eid}')
    print(json.dumps(out, ensure_ascii=False))


# ── самопроверка ───────────────────────────────────────────────────────────────────────────────────────────
def selftest(ctx):
    ok = True
    for key in ('t_schema', 'm_schema'):
        Draft202012Validator.check_schema(load(P[key]))
    R = cmd_blocks(ctx, Report())
    e = [i for i in R.items if i[0] == 'error']
    print(f'blocks: error {len(e)}')
    ok &= not e
    tv = Draft202012Validator(load(P['t_schema']))
    bad = [({'level': 'L0', 'effects': [{'ref': 'effect:pin-scrub-story'}], 'reduce': {'strategy': 'final-state'}, 'mobile': {'strategy': 'static'}}, 'L0 + pin'),
           ({'visual_role': 'peak', 'effects': [{'ref': 'effect:sticky-stack', 'purpose': 'support'}], 'reduce': {'strategy': 'final-state'}, 'mobile': {'strategy': 'same'}}, 'peak без signature'),
           ({'composition': {'text_media': 'text-over'}}, 'text-over без text_contrast'),
           ({'background': {'kind': 'video-loop'}, 'mobile': {'strategy': 'poster'}}, 'видео без flash_check'),
           ({'motion_level': 'cinematic', 'reduce': {'strategy': 'final-state'}}, 'cinematic без ролика')]
    for doc, name in bad:
        caught = bool(list(tv.iter_errors(doc)))
        print(f'treatment «{name}»: {"поймано" if caught else "ПРОПУЩЕНО"}')
        ok &= caught
    mom = Draft202012Validator({'$ref': '#/$defs/moment', '$defs': load(P['m_schema'])['$defs']})
    m_bad = {'id': 'x', 'class': 'one-shot', 'purpose': 'guide', 'target': 'hero.headline', 'lcp': 'is-lcp', 'trigger': {'type': 'load'},
             'tracks': [{'property': 'opacity', 'from': 0, 'to': 1}], 'duration': {'ms': 600}, 'reduce': {'strategy': 'final-state'}}
    caught = bool(list(mom.iter_errors(m_bad)))
    print(f'motion-spec «LCP из opacity»: {"поймано" if caught else "ПРОПУЩЕНО"}')
    ok &= caught
    print('selftest:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    b = sub.add_parser('blocks'); b.add_argument('--yaml')
    p = sub.add_parser('plan'); p.add_argument('plan'); p.add_argument('--overlay'); p.add_argument('--out'); p.add_argument('--spec')
    s = sub.add_parser('spec'); s.add_argument('spec'); s.add_argument('--plan'); s.add_argument('--overlay')
    m = sub.add_parser('moments'); m.add_argument('spec'); m.add_argument('--section')
    md = sub.add_parser('motion-md'); md.add_argument('spec'); md.add_argument('--out')
    v = sub.add_parser('values'); v.add_argument('spec'); v.add_argument('--out', required=True)
    sub.add_parser('levels')
    a = ap.parse_args()
    ctx = Ctx()
    if a.selftest:
        return selftest(ctx)
    if a.cmd == 'blocks':
        return cmd_blocks(ctx, Report(), a.yaml).dump('block-treatments')
    if a.cmd == 'plan':
        R = Report()
        spec = load(a.spec) if a.spec else None
        cmd_plan(ctx, R, a.plan, a.overlay, a.out, spec)
        return R.dump(f'plan {os.path.basename(a.plan)}')
    if a.cmd == 'spec':
        R = Report()
        cmd_spec(ctx, R, a.spec, a.plan, a.overlay)
        return R.dump(f'motion-spec {os.path.basename(a.spec)}')
    if a.cmd == 'moments':
        cmd_moments(ctx, load(a.spec), a.section)
        return 0
    if a.cmd == 'motion-md':
        cmd_motion_md(ctx, load(a.spec), a.out)
        return 0
    if a.cmd == 'values':
        cmd_values(ctx, load(a.spec), a.out)
        return 0
    if a.cmd == 'levels':
        cmd_levels(ctx)
        return 0
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
