#!/usr/bin/env python3
"""checklist_export.py — сводный чек-лист сайта из Markdown в YAML (агент K, волна 3 site-research, 2026-09-24).

Читает строки таблиц `09-ai-generation-evaluation/02-site-checklist.md`:
  | SITE-<БЛОК>-<NN> | проверка | B|S|D | DOM, SCR, … | источник |      — пункты чек-листа
  | DEF-<NN> | дефект | step:… | ловят | маркер |                         — каталог дефектов для процедуры J
и пишет `09-ai-generation-evaluation/site-checklist.yaml`. Правки — только в Markdown; YAML — производный артефакт
(PLAN.md: «YAML, выводимый из Markdown, генерируется скриптом и руками не правится»). Образец —
`../ux-research/99-raw/tools/checklist_export.py` (формат ux `12-evaluation-checklists/master-checklist.yaml`).

Запуск из любого места (пути считаются от расположения файла):
  python3 99-raw/tools/checklist_export.py            # записать YAML и напечатать сводку
  python3 99-raw/tools/checklist_export.py --check    # YAML совпадает с Markdown? (код 1 — нет)
  python3 99-raw/tools/checklist_export.py --selftest # самопроверка разбора на встроенном примере
  python3 99-raw/tools/checklist_export.py --md FILE --out FILE   # другой файл (опыты)
Только стандартная библиотека; PyYAML — если установлен — для проверки валидности результата.
"""
import argparse
import collections
import datetime
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('site'))
MD_DEFAULT = os.path.join(ROOT, '09-ai-generation-evaluation', '02-site-checklist.md')
OUT_DEFAULT = os.path.join(ROOT, '09-ai-generation-evaluation', 'site-checklist.yaml')
MARKERS = os.path.join(ROOT, '09-ai-generation-evaluation', 'ai-landing-markers.yaml')

SEV = {'B': 'блокер', 'S': 'серьёзно', 'D': 'желательно'}
WAY = {'DOM': 'dom', 'LNT': 'script', 'AXE': 'script', 'SCR': 'scenario', 'IMG': 'visual', 'JDG': 'judge', 'HUM': 'human'}
NO_GATE = {'JDG', 'HUM'}
BLOCKS = ('PRE', 'STR', 'BLK', 'CTA', 'FRM', 'PRF', 'NAV', 'SEO', 'GEO', 'PERF', 'A11Y', 'LEGAL', 'TRK', 'MOB', 'OUT')
STEPS = ('step:intake', 'step:proof', 'step:site-type', 'step:site-map', 'step:page-plan', 'step:sister-sync',
         'step:plan-check', 'step:package', 'step:build-loop', 'step:gates', 'step:fix', 'step:acceptance', 'step:measure')
LEVELS = (r'\[(исследование|консенсус|стандарт|документация|данные|кейс|практика|мнение вендора|мнение|спорно|проверено|'
          r'не проверено|вендор-GEO|регулятор|правоприменение|награда|гипотеза)(?:[:\] ])')
RELATED = re.compile(r'\b(?:UX|AC)-[A-Z0-9]{3}-\d{2}\b|\bCOPY-[A-Z]+(?:-[A-Z]+)?-\d{2}\b|\bCOPY-[A-Z]-[A-Z]+\b|'
                     r'\bCRV-[A-Z]+-\d{2}\b|\bSG-[A-Z0-9]+-\d{2}\b|\bLR-(?:RU|EU)-\d{2}\b|\bAIL-\d{2}\b|\bDEF-\d{2}\b|'
                     r'\bSITE-[A-Z0-9]{2,5}-\d{2}\b')
ROW_ITEM = re.compile(r'^\|\s*(SITE-([A-Z0-9]{2,5})-(\d{2}))\s*\|\s*(.+?)\s*\|\s*([BSD])\s*\|\s*([A-Z0-9, ]+?)\s*\|\s*(.*?)\s*\|\s*$')
ROW_DEF = re.compile(r'^\|\s*(DEF-(\d{2}))\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$')
HEAD_BLOCK = re.compile(r'^#{2,3}\s+(?:\d+(?:\.\d+)*\.?\s+)?(?:Блок\s+)?([A-Z0-9]{2,5})\s+—\s+(.+?)\s*$')
FILE_EXT = ('.md', '.yaml', '.yml', '.json', '.py', '.tsv', '.csv')


def q(s):
    return json.dumps(s, ensure_ascii=False)


def base_files():
    """Имя файла → путь от корня базы (для ссылок вида `lead-forms.yaml` без папки)."""
    out = {}
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p) and re.match(r'^\d\d-', d):
            for f in sorted(os.listdir(p)):
                out.setdefault(f, f'{d}/{f}')
    tools = str(kbpaths.scripts('site'))  # перенос: утилиты site — scripts/site
    if os.path.isdir(tools):
        for f in sorted(os.listdir(tools)):
            out.setdefault(f, os.path.relpath(os.path.join(tools, f), ROOT))
    return out


def resolve_token(tok, md_dir, names):
    """Токен в бэктиках → путь от корня базы (для чужих баз — `../<база>/…`); None, если это не путь."""
    t = tok.strip('`').strip()
    if not t or ' ' in t or not (t.endswith(FILE_EXT) or t.endswith('/')):
        return None
    if t.startswith('../') or t.startswith('./') or '/' in t:
        absp = os.path.normpath(os.path.join(md_dir, t))
        rel = os.path.relpath(absp, ROOT)
        return rel + ('' if os.path.exists(absp) else '?')
    if t in names:
        return names[t]
    here = os.path.join(md_dir, t)
    rel = os.path.relpath(here, ROOT)
    return rel + ('' if os.path.exists(here) else '?')


def parse(md_path):
    md_dir = os.path.dirname(os.path.abspath(md_path))
    names = base_files()
    lines = io.open(md_path, encoding='utf-8').read().split('\n')
    meta = next((l.strip() for l in lines[:15] if 'пункт' in l and '**' in l), '')
    items, defects, blocks, problems = [], [], collections.OrderedDict(), []
    cur_block, cur_title = None, None
    for ln, line in enumerate(lines, 1):
        m = HEAD_BLOCK.match(line)
        if m and m.group(1) in BLOCKS:
            cur_block, cur_title = m.group(1), m.group(2).strip()
            blocks[cur_block] = cur_title
            continue
        m = ROW_ITEM.match(line)
        if m:
            sid, blk, num, text, sev, way, src = m.groups()
            ways = [w.strip() for w in way.split(',') if w.strip()]
            bad = [w for w in ways if w not in WAY]
            if bad:
                problems.append(f'{sid} (стр. {ln}): неизвестный способ {bad}')
            if blk not in BLOCKS:
                problems.append(f'{sid} (стр. {ln}): неизвестный блок {blk}')
            if cur_block and blk != cur_block:
                problems.append(f'{sid} (стр. {ln}): стоит в разделе блока {cur_block}')
            files = []
            for tok in re.findall(r'`[^`]+`', src):
                f = resolve_token(tok, md_dir, names)
                if f and f not in files:
                    files.append(f)
            section = re.sub(r'`[^`]+`', '', src)
            section = re.sub(r'\s+', ' ', section).strip(' ;,—-')
            related = sorted(set(RELATED.findall(src + ' ' + text)) - {sid})
            items.append({
                'id': sid, 'block': blk, 'block_title': blocks.get(blk, cur_title or ''), 'num': int(num),
                'text': text.strip(), 'severity': sev, 'severity_label': SEV[sev],
                'check_method': ways, 'check_method_class': [WAY.get(w, '?') for w in ways],
                'check_method_main': WAY.get(ways[0], '?') if ways else '',
                'auto_gate': bool(ways) and ways[0] not in NO_GATE,
                'source_file': files, 'source_section': section, 'source_raw': src.strip(),
                'evidence_level': sorted(set(re.findall(LEVELS, src))),
                'videos': sorted(set(re.findall(r'\[V:([A-Za-z0-9_-]{11})', src))),
                'related_ids': related, 'line': ln,
            })
            continue
        m = ROW_DEF.match(line)
        if m:
            did, num, text, steps, caught, marker = m.groups()
            st = re.findall(r'step:[a-z-]+', steps)
            bad = [x for x in st if x not in STEPS]
            if bad:
                problems.append(f'{did} (стр. {ln}): неизвестный шаг {bad}')
            caught_ids = []
            for mm in re.finditer(r'SITE-([A-Z0-9]{2,5})-(\d{2})(?:…(\d{2}))?', caught):
                blk, a, b = mm.group(1), int(mm.group(2)), mm.group(3)
                for n in range(a, (int(b) if b else a) + 1):
                    caught_ids.append(f'SITE-{blk}-{n:02d}')
            defects.append({
                'id': did, 'num': int(num), 'text': text.strip(), 'steps': st,
                'caught_by': caught_ids, 'caught_by_other': sorted(set(re.findall(r'\b(?:SG-[A-Z0-9]+-\d{2}|COPY-C-\d{2})\b', caught))),
                'markers': sorted(set(re.findall(r'AIL-\d{2}', marker))), 'line': ln,
            })
    return {'meta': meta, 'items': items, 'defects': defects, 'blocks': blocks, 'problems': problems}


def validate(d, markers_path=MARKERS):
    """Ошибки (errors) и предупреждения (warnings) целостности чек-листа."""
    errors, warnings = list(d['problems']), []
    ids = [i['id'] for i in d['items']]
    dup = [k for k, v in collections.Counter(ids).items() if v > 1]
    if dup:
        errors.append(f'повтор id: {dup}')
    by_block = collections.defaultdict(list)
    for i in d['items']:
        by_block[i['block']].append(i['num'])
    for b, nums in by_block.items():
        if sorted(nums) != list(range(1, len(nums) + 1)):
            warnings.append(f'{b}: номера не подряд {sorted(nums)[:5]}…')
    known = set(ids)
    for df in d['defects']:
        for c in df['caught_by']:
            if c not in known:
                errors.append(f'{df["id"]}: ссылка на несуществующий {c}')
        if not df['steps']:
            errors.append(f'{df["id"]}: нет шага процедуры')
    for i in d['items']:
        for r in i['related_ids']:
            if r.startswith('SITE-') and r not in known:
                errors.append(f'{i["id"]}: ссылка на несуществующий {r}')
        miss = [f for f in i['source_file'] if f.endswith('?')]
        if miss:
            warnings.append(f'{i["id"]}: файл не найден {miss}')
        if not i['source_file'] and not i['related_ids']:
            warnings.append(f'{i["id"]}: нет источника-файла и связанных id')
    mk = set()
    if os.path.exists(markers_path):
        try:
            import yaml
            y = yaml.safe_load(io.open(markers_path, encoding='utf-8'))
            mk = {m['id'] for m in (y.get('markers') or [])}
        except Exception as e:  # noqa: BLE001
            warnings.append(f'ai-landing-markers.yaml не прочитан: {e}')
    refs = {r for i in d['items'] for r in i['related_ids'] if r.startswith('AIL-')} | \
           {m for df in d['defects'] for m in df['markers']}
    if mk:
        for r in sorted(refs - mk):
            errors.append(f'маркер {r} упомянут, но нет в ai-landing-markers.yaml')
    else:
        warnings.append('ai-landing-markers.yaml нет — ссылки AIL не сверены')
    return errors, warnings


def render(d, md_path, now=None):
    now = now or datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    rel_md = os.path.relpath(md_path, ROOT)
    out = [f'# Машиночитаемая версия {rel_md} (сводный чек-лист сайта, агент K).',
           '# Сгенерировано 99-raw/tools/checklist_export.py — правки вносить в Markdown и перегенерировать.',
           f'version: {q("1.0")}', f'generated_at: {q(now)}', f'checked: {q(now[:10])}',
           f'source_md: {q(rel_md)}', f'source_md_meta: {q(d["meta"])}',
           f'items_count: {len(d["items"])}', f'defects_count: {len(d["defects"])}',
           'severity_scale: {B: блокер, S: серьёзно, D: желательно}',
           'severity_note: ' + q('серьёзность на маршруте «визит → действие» (поправка PLAN №10), назначена агентом K, не измерена; [спорно] — не выше S'),
           'check_method_codes: {DOM: dom, LNT: script, AXE: script, SCR: scenario, IMG: visual, JDG: judge, HUM: human}',
           'check_method_note: ' + q('первый способ — основной; JDG и HUM не ставят автоматических ворот (auto_gate: false)'),
           'steps: [' + ', '.join(STEPS) + ']',
           'blocks:']
    for b, t in d['blocks'].items():
        n = sum(1 for i in d['items'] if i['block'] == b)
        sev = collections.Counter(i['severity'] for i in d['items'] if i['block'] == b)
        out.append(f'  - {{code: {b}, title: {q(t)}, items: {n}, B: {sev.get("B", 0)}, S: {sev.get("S", 0)}, D: {sev.get("D", 0)}}}')
    out.append('items:')
    for i in d['items']:
        out.append(f'  - id: {i["id"]}')
        out.append(f'    block: {i["block"]}')
        out.append(f'    block_title: {q(i["block_title"])}')
        out.append(f'    text: {q(i["text"])}')
        out.append(f'    severity: {i["severity"]}')
        out.append(f'    severity_label: {q(i["severity_label"])}')
        out.append(f'    check_method: [{", ".join(i["check_method"])}]')
        out.append(f'    check_method_class: [{", ".join(i["check_method_class"])}]')
        out.append(f'    check_method_main: {i["check_method_main"]}')
        out.append(f'    auto_gate: {"true" if i["auto_gate"] else "false"}')
        out.append(f'    source_file: [{", ".join(q(f) for f in i["source_file"])}]')
        out.append(f'    source_section: {q(i["source_section"])}')
        out.append(f'    source_raw: {q(i["source_raw"])}')
        out.append(f'    evidence_level: [{", ".join(q(x) for x in i["evidence_level"])}]')
        if i['videos']:
            out.append(f'    videos: [{", ".join(q(v) for v in i["videos"])}]')
        if i['related_ids']:
            out.append(f'    related_ids: [{", ".join(i["related_ids"])}]')
    out.append('defects:')
    for df in d['defects']:
        out.append(f'  - id: {df["id"]}')
        out.append(f'    text: {q(df["text"])}')
        out.append(f'    steps: [{", ".join(df["steps"])}]')
        out.append(f'    caught_by: [{", ".join(df["caught_by"])}]')
        if df['caught_by_other']:
            out.append(f'    caught_by_other: [{", ".join(df["caught_by_other"])}]')
        out.append(f'    markers: [{", ".join(df["markers"])}]')
    return '\n'.join(out) + '\n'


def strip_volatile(text):
    return '\n'.join(l for l in text.split('\n') if not l.startswith(('generated_at:', 'checked:')))


def check_yaml(text):
    try:
        import yaml
    except ImportError:
        return 'PyYAML не установлен — валидность не проверена'
    try:
        y = yaml.safe_load(text)
        return f'YAML валиден: items={len(y["items"])}, defects={len(y["defects"])}'
    except Exception as e:  # noqa: BLE001
        return f'ОШИБКА YAML: {e}'


SELFTEST_MD = """# Тест
Свод: **3 пункта в 2 блоках**.
### 3.1. STR — структура, сюжет
| ID | Проверка | Сер. | Способ | Источник |
|---|---|---|---|---|
| SITE-STR-01 | Порядок из вопросов посетителя | S | JDG, HUM | `../03-page-structure/01-narratives-and-section-order.md` §3.1 `[проверено: C/01]`; AIL-01; UX-LAY-02 |
| SITE-STR-02 | Хвост из возражений | D | DOM | `lead-forms.yaml`; [V:w87hTii1Dao 36:07]; SITE-STR-01 |
### 3.2. FRM — формы
| SITE-FRM-01 | Форма — `<form>` с `type=submit` | B | SCR, DOM | `../05-conversion-funnels/01-cta-and-lead-capture.md` §9; SG-CONTENT-02; COPY-C-01; LR-RU-01 |
## 4. Каталог
| ID | Дефект | Шаг | Ловят | Маркер |
|---|---|---|---|---|
| DEF-01 | Шаблон порядка | step:page-plan | SITE-STR-01…02 | AIL-01 |
| DEF-02 | Форма не работает | step:build-loop, step:gates | SITE-FRM-01, SG-CONTENT-02 | — |
"""


def selftest():
    ok, res = True, []

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        res.append(('PASS' if cond else 'FAIL', name))

    with tempfile.TemporaryDirectory() as td:
        sub = os.path.join(td, '09-x')
        os.makedirs(sub)
        md = os.path.join(sub, 'c.md')
        io.open(md, 'w', encoding='utf-8').write(SELFTEST_MD)
        d = parse(md)
    ids = [i['id'] for i in d['items']]
    check('3 пункта разобраны', ids == ['SITE-STR-01', 'SITE-STR-02', 'SITE-FRM-01'])
    check('блоки из заголовков', list(d['blocks'].keys()) == ['STR', 'FRM'])
    i1, i2, i3 = d['items']
    check('способы и класс', i1['check_method'] == ['JDG', 'HUM'] and i1['check_method_main'] == 'judge')
    check('JDG — без автоворот', i1['auto_gate'] is False and i3['auto_gate'] is True)
    check('метка доказательности', i1['evidence_level'] == ['проверено'])
    check('связанные id', 'AIL-01' in i1['related_ids'] and 'UX-LAY-02' in i1['related_ids'])
    check('связанные id FRM', {'SG-CONTENT-02', 'COPY-C-01', 'LR-RU-01'} <= set(i3['related_ids']))
    check('ролик', i2['videos'] == ['w87hTii1Dao'])
    check('код в бэктиках — не путь', all('<form>' not in f for f in i3['source_file']))
    check('2 дефекта', [x['id'] for x in d['defects']] == ['DEF-01', 'DEF-02'])
    check('диапазон …', d['defects'][0]['caught_by'] == ['SITE-STR-01', 'SITE-STR-02'])
    check('шаги дефекта', d['defects'][1]['steps'] == ['step:build-loop', 'step:gates'])
    check('прочие ловцы', d['defects'][1]['caught_by_other'] == ['SG-CONTENT-02'])
    errs, warns = validate(d, markers_path='/nonexistent')
    check('нет ошибок целостности', not errs)
    y = render(d, md, now='2026-09-24 00:00')
    check('YAML валиден', check_yaml(y).startswith('YAML валиден') or 'не установлен' in check_yaml(y))
    bad = SELFTEST_MD.replace('| S | JDG, HUM |', '| X | JDG, HUM |').replace('SITE-FRM-01 | Форма', 'SITE-FRM-01 | Форма')
    with tempfile.TemporaryDirectory() as td:
        md2 = os.path.join(td, 'c.md')
        io.open(md2, 'w', encoding='utf-8').write(bad)
        d2 = parse(md2)
    check('строка с неверной серьёзностью не принимается', 'SITE-STR-01' not in [i['id'] for i in d2['items']])
    for st, n in res:
        print(st, n)
    print(f"итог: {sum(r[0] == 'PASS' for r in res)}/{len(res)} PASS")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--md', default=MD_DEFAULT)
    ap.add_argument('--out', default=OUT_DEFAULT)
    ap.add_argument('--check', action='store_true', help='сравнить существующий YAML с Markdown (без записи)')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    d = parse(a.md)
    errs, warns = validate(d)
    y = render(d, a.md)
    if a.check:
        if not os.path.exists(a.out):
            print(f'нет файла {a.out}')
            return 1
        same = strip_volatile(io.open(a.out, encoding='utf-8').read()) == strip_volatile(y)
        print('YAML совпадает с Markdown' if same else 'YAML УСТАРЕЛ: перегенерировать (checklist_export.py)')
        return 0 if same and not errs else 1
    io.open(a.out, 'w', encoding='utf-8').write(y)
    sev = collections.Counter(i['severity'] for i in d['items'])
    way = collections.Counter(i['check_method_main'] for i in d['items'])
    print(f'пунктов {len(d["items"])} (B {sev["B"]}, S {sev["S"]}, D {sev["D"]}); блоков {len(d["blocks"])}; '
          f'дефектов {len(d["defects"])}; автоворота {sum(i["auto_gate"] for i in d["items"])}; {check_yaml(y)}')
    print('по блокам:', {b: sum(1 for i in d['items'] if i['block'] == b) for b in d['blocks']})
    print('основной способ:', dict(way))
    for e in errs:
        print('ОШИБКА', e)
    for w in warns[:30]:
        print('предупреждение', w)
    if len(warns) > 30:
        print(f'… ещё предупреждений: {len(warns) - 30}')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
