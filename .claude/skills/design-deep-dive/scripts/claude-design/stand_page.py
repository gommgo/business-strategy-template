#!/usr/bin/env python3
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# stand_page.py — копия БЕЗ ПРАВОК КОДА (26.09.2026) страницы слепого попарного выбора для стенда тестов от 24.09.2026,
# md5 оригинала 7cae69382f00cdc712b416741e0c7d6d. Как пользоваться — claude-design-research/06-design-process/06-test-stand.md (§5, §6).
# Брать: build (страница + ключи рядом), tally (Уилсон, Брэдли — Терри, повторы, контрольные пары, вердикт по паре условий),
#   power (мощность правила решения), fake и simulate (проверка конвейера без модели), selftest.
# Зависимость: читает модуль ai-media-research/99-raw/tools/stand_run.py по АБСОЛЮТНОМУ пути (константа STAND) — канон слепых пар
#   (ai-media 13-routing-matrix/01-stand-method.md); при переносе в шаблон — путь относительный или модуль рядом.
# Что убрать при адаптации:
#   1. Имена условий другого исполнителя в докстринге, умолчаниях `fake` (--test T-501 --conditions …) и в selftest — заменить на
#      условия этой базы (например types, kit, ui); ссылка на правило решения 09-test-plan/… → 06-design-process/06-test-stand.md §6.
#   2. Кадры ждёт как <shots_dir>/<вид>.jpg (виды по умолчанию desktop-1440x900-00, mobile-390x844-00, desktop-1440x900-map):
#      первые экраны даёт mockup_checks.py page --shots, карту — JPEG из полного кадра kit/shot.py (или --views без карты).
#   3. selftest создаёт временную папку рядом со скриптом; запускать с PYTHONDONTWRITEBYTECODE=1, чтобы не писать кэш в ai-media.
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
"""stand_page.py — страница слепого попарного выбора для СТЕНДА тестов (T, волна 2, 2026-09-24).

Поверх `stand_run.py page/tally` из ai-media (модуль только читается; страница и ключи пишутся рядом с --out).
Отличие от G/05 `variants_page.py` (варианты одного проекта): здесь сравниваются УСЛОВИЯ теста (K3 high / K3 max / Claude
Opus 5.5 / Claude Fable 5.1 / …) на нескольких брифах и прогонах; пары строятся внутри группы «тест | бриф | вид» между
разными условиями, прогоны одного условия между собой не сравниваются; итог — вердикт по паре условий с интервалом Уилсона
и кластерной проверкой по парам прогонов (виды одного прогона не независимы). Модель не вызывается, сеть не нужна.

  stand_page.py build --manifest runs.tsv --out PAGE_DIR [--views desktop-1440x900-00,mobile-390x844-00,desktop-1440x900-map]
                      [--title T] [--repeat 0.1] [--seed 7]
      runs.tsv: test, brief, brief_text, condition, run, shots_dir (TAB; строка на прогон; базовые прогоны повторить под
      каждым тестом, где они — база). Пишет PAGE_DIR/index.html + img/, ключ PAGE_DIR.key.json и PAGE_DIR.runs.json РЯДОМ.
  stand_page.py simulate --key PAGE_DIR.key.json --runs PAGE_DIR.runs.json --truth 'T-501:k3=0,opus=0.4,fable=0.8'
                      [--truth …] [--run-sd 0.3] [--tau 0.35] [--tie 0.12] [--seed 1] --out votes.json
      сценарный голосующий: скрытое качество прогона = качество условия + шум прогона; голос по виду — логистика разницы.
  stand_page.py tally VOTES.json [VOTES2.json …] --key PAGE_DIR.key.json --runs PAGE_DIR.runs.json [--out tally.md]
      таблицы stand_run (Уилсон, Брэдли — Терри, повторы, контрольные) + ВЕРДИКТ по каждой паре условий каждого теста.
  stand_page.py power [--designs 1x2,1x3,2x2,3x2] [--diffs 0,0.2,0.4,0.6,0.9] [--sims 2000] [--out power.md]
      доля верно найденных перевесов и ложных срабатываний правила решения для размеров стенда (брифов × прогонов).
  stand_page.py fake --out DIR --manifest-out runs.tsv [--test T-501 --conditions k3,opus,fable --briefs S1 --runs 2]
      фиктивные кадры (PIL) и манифест — для проверки конвейера без модели.
  stand_page.py selftest    fake → build → проверка слепоты страницы → simulate → tally (вердикт = заданный порядок)

Правило решения (09-test-plan/03-protocol-logging.md §5.4): условие X лучше Y, если (1) нижняя граница 95 % Уилсона доли
побед X (ничья = ½) > 0,5 и (2) X выиграл большинство видов в ≥ 75 % пар прогонов; симметрично для Y; иначе «неразличимы» —
остаётся умолчание (дешевле / проще). Контрольная пара провалена или повторы перевёрнуты больше чем в половине — голосование
не засчитывать.
"""
import argparse, csv, importlib.util, json, math, os, random, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lib'))  # перенос: scripts/lib
import kbpaths  # noqa: E402
STAND = kbpaths.scripts('ai-media', 'stand_run.py')
DEF_VIEWS = 'desktop-1440x900-00,mobile-390x844-00,desktop-1440x900-map'
VIEW_HUMAN = {'desktop-1440x900-00': 'первый экран · десктоп 1440', 'mobile-390x844-00': 'первый экран · телефон 390',
              'desktop-1440x900-map': 'вся страница · карта 1440', 'tablet-768x1024-00': 'первый экран · планшет 768'}
QUESTIONS_STAND = [  # id 'slot'/'natural' — их ждёт tally() в stand_run.py
    {"id": "slot", "text": "Какую страницу вы бы отдали клиенту по этому брифу?", "options": ["A", "B", "=", "0"]},
    {"id": "natural", "text": "Какая выглядит спроектированной под этот продукт, а не собранной из шаблона?", "options": ["A", "B", "="]},
]
COLS = ['test', 'brief', 'brief_text', 'condition', 'run', 'shots_dir']
FIT_CSS = ('<style>/* stand_page.py: кадр целиком по высоте окна; кнопка макета текста не нужна для сайтов */'
           '.shot{text-align:center}.shot img{max-height:calc(100vh - 330px);width:auto;max-width:100%;margin:0 auto}'
           '#mockbtn{display:none}</style>')


def load_stand():
    spec = importlib.util.spec_from_file_location('stand_run', STAND)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # только чтение модуля соседней базы
    mod.QUESTIONS[:] = QUESTIONS_STAND    # build_page берёт вопросы из модульной константы
    return mod


def read_manifest(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader((ln for ln in f if ln.strip() and not ln.startswith('#')), delimiter='\t'):
            miss = [c for c in COLS if not (r.get(c) or '').strip()]
            if miss:
                raise SystemExit(f'манифест: нет полей {miss} в строке {r}')
            rows.append({c: r[c].strip() for c in COLS})
    return rows


# ───────────────────────────── build ─────────────────────────────
def cmd_build(a):
    st = load_stand()
    rows = read_manifest(a.manifest)
    views = [v.strip() for v in a.views.split(',') if v.strip()]
    items, runs = [], {}
    for r in rows:
        for v in views:
            p = Path(r['shots_dir']) / f'{v}.jpg'
            if not p.is_file():
                raise SystemExit(f'нет кадра {p}')
            ap = str(p.resolve())
            items.append({'group': f"{r['test']}|{r['brief']}|{v}", 'model': r['condition'], 'files': [ap],
                          'brief': f"{r['brief_text']} · {VIEW_HUMAN.get(v, v)}", 'test': f"{r['test']}|{v}"})
            rec = {'brief': r['brief'], 'condition': r['condition'], 'run': r['run'], 'view': v}
            if ap in runs and runs[ap] != rec:   # один кадр — одно условие и прогон во всех тестах (база общая)
                raise SystemExit(f'кадр {ap} подписан по-разному: {runs[ap]} и {rec}')
            runs[ap] = rec
    out = Path(a.out)
    stats = st.build_page(items, out, title=a.title, repeat=a.repeat, seed=a.seed, gold=True)
    html_path = out / 'index.html'                 # кадры — целиком в высоту окна (карта страницы высокая), вопросы видны
    html = html_path.read_text(encoding='utf-8').replace('</head>', FIT_CSS + '</head>', 1)
    html_path.write_text(html, encoding='utf-8')
    Path(str(out) + '.runs.json').write_text(json.dumps(runs, ensure_ascii=False, indent=1), encoding='utf-8')
    blind = blind_check(out, rows)
    print(json.dumps({'page': str(out / 'index.html'), 'key': str(out) + '.key.json', 'runs': str(out) + '.runs.json',
                      **stats, 'blind_ok': not blind, 'leaks': blind,
                      'minutes_at_20s_per_pair': round(stats['pairs'] * 20 / 60, 1)}, ensure_ascii=False))
    return 0 if not blind else 1


def blind_check(out, rows):
    """На странице не должно быть имён условий, номеров прогонов и путей к кадрам (слепота)."""
    html = (Path(out) / 'index.html').read_text(encoding='utf-8')
    leaks = []
    for r in rows:
        for needle in (r['shots_dir'], os.path.basename(r['shots_dir'].rstrip('/'))):
            if needle and needle in html:
                leaks.append(needle)
        cond = r['condition']
        if re.search(r'(?<![\w-])' + re.escape(cond) + r'(?![\w-])', html.split('<script type="application/json"', 1)[-1]):
            leaks.append(cond)
    for f in Path(out).joinpath('img').iterdir():
        if not re.fullmatch(r'[0-9a-f]{10}\.(jpg|png)', f.name):
            leaks.append(f.name)
    return sorted(set(leaks))


# ───────────────────────────── simulate ─────────────────────────────
def parse_truth(specs):
    truth = {}
    for s in specs or []:
        test, rest = s.split(':', 1)
        truth[test] = {k: float(v) for k, v in (x.split('=') for x in rest.split(','))}
    return truth


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def cmd_simulate(a):
    key = json.loads(Path(a.key).read_text(encoding='utf-8'))
    runs = json.loads(Path(a.runs).read_text(encoding='utf-8'))
    truth = parse_truth(a.truth)
    rnd = random.Random(a.seed)
    noise, seen = {}, {}

    def q(path, test):
        r = runs[path]
        k = (r['condition'], r['brief'], r['run'])          # шум прогона общий для всех тестов (одна и та же страница)
        if k not in noise:
            noise[k] = rnd.gauss(0, a.run_sd)
        return truth.get(test, {}).get(r['condition'], 0.0) + noise[k]

    votes = {}
    for pid, kp in key['pairs'].items():
        if kp.get('identical'):
            votes[pid] = {'slot': '=', 'natural': '='}
            continue
        if kp.get('gold'):
            votes[pid] = {'slot': kp['gold'], 'natural': kp['gold']}
            continue
        test = kp['group'].split('|')[0]
        fa, fb = kp['A']['files'][0], kp['B']['files'][0]
        pk = (test, frozenset((fa, fb)))
        if pk not in seen:                                   # повтор пары с переставленными сторонами — то же впечатление
            d0 = q(fa, test) - q(fb, test)
            seen[pk] = {'ref': fa, 'u': {qid: (rnd.random(), rnd.random()) for qid in ('slot', 'natural')}, 'd': d0}
        m = seen[pk]
        d = m['d'] if m['ref'] == fa else -m['d']
        v = {}
        for qid in ('slot', 'natural'):
            u_tie, u = m['u'][qid]
            if u_tie < a.tie:
                v[qid] = '='
            else:
                pa = sigmoid(d / a.tau)
                win_ref = u < (pa if m['ref'] == fa else 1 - pa)
                v[qid] = ('A' if m['ref'] == fa else 'B') if win_ref else ('B' if m['ref'] == fa else 'A')
        votes[pid] = v
    Path(a.out).write_text(json.dumps({'page': key['page'], 'voter': a.voter, 'votes': votes}, ensure_ascii=False, indent=1),
                           encoding='utf-8')
    print(json.dumps({'votes': len(votes), 'out': a.out, 'runs_with_noise': len(noise)}, ensure_ascii=False))
    return 0


# ───────────────────────────── verdict ─────────────────────────────
def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, max(0.0, c - h), min(1.0, c + h))


def verdicts(votes_files, key_path, runs_path, question='slot', cluster_share=0.75):
    K = json.loads(Path(key_path).read_text(encoding='utf-8'))
    R = json.loads(Path(runs_path).read_text(encoding='utf-8'))
    games = {}          # (test, x, y) → список (runA, runB, view, score_x)
    both_bad = {}
    for f in votes_files:
        V = json.loads(Path(f).read_text(encoding='utf-8'))
        for pid, v in (V.get('votes') or {}).items():
            kp = K['pairs'].get(pid)
            if not kp or kp.get('gold') or kp.get('repeat_of') or kp.get('identical') or question not in v:
                continue
            ra, rb = R[kp['A']['files'][0]], R[kp['B']['files'][0]]
            test = kp['group'].split('|')[0]
            x, y = sorted([ra['condition'], rb['condition']])
            o = v[question]
            if o == '0':
                both_bad[(test, x, y)] = both_bad.get((test, x, y), 0) + 1
                continue
            s_a = 1.0 if o == 'A' else 0.0 if o == 'B' else 0.5
            s_x = s_a if ra['condition'] == x else 1 - s_a
            run_x = ra['run'] if ra['condition'] == x else rb['run']
            run_y = rb['run'] if ra['condition'] == x else ra['run']
            games.setdefault((test, x, y), []).append((f"{ra['brief']}/{run_x}", f"{ra['brief']}/{run_y}", ra['view'], s_x))
    out = []
    for (test, x, y), gs in sorted(games.items()):
        n = len(gs)
        k = sum(g[3] for g in gs)
        p, lo, hi = wilson(k, n)
        clusters = {}
        for rx, ry, view, s in gs:
            clusters.setdefault((rx, ry), []).append(s)
        won_x = sum(1 for ss in clusters.values() if sum(ss) > len(ss) / 2)
        won_y = sum(1 for ss in clusters.values() if sum(ss) < len(ss) / 2)
        nc = len(clusters)
        need = math.ceil(cluster_share * nc)
        if lo > 0.5 and won_x >= need:
            verdict = f'{x} лучше'
        elif hi < 0.5 and won_y >= need:
            verdict = f'{y} лучше'
        else:
            verdict = 'неразличимы → умолчание'
        per_view = {}
        for rx, ry, view, s in gs:
            a_, b_ = per_view.get(view, (0.0, 0))
            per_view[view] = (a_ + s, b_ + 1)
        out.append({'test': test, 'x': x, 'y': y, 'pairs': n, 'share_x': round(p, 3), 'wilson_x': [round(lo, 3), round(hi, 3)],
                    'run_pairs': nc, 'run_pairs_won_x': won_x, 'run_pairs_won_y': won_y, 'need': need, 'verdict': verdict,
                    'per_view_share_x': {v: round(a_ / b_, 2) for v, (a_, b_) in per_view.items()},
                    'both_bad': both_bad.get((test, x, y), 0)})
    return out


def verdicts_md(vs, question):
    L = [f'## Вердикты по парам условий (вопрос `{question}`)', '',
         '| Тест | X | Y | Пар | Доля X | 95 % Уилсон | Пар прогонов (X / Y / нужно) | По видам (доля X) | «Обе не годятся» | Вердикт |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for v in vs:
        pv = ', '.join(f"{VIEW_HUMAN.get(k, k).split(' · ')[-1]} {s}" for k, s in sorted(v['per_view_share_x'].items()))
        L.append(f"| {v['test']} | `{v['x']}` | `{v['y']}` | {v['pairs']} | {v['share_x']:.2f} | {v['wilson_x'][0]:.2f}–{v['wilson_x'][1]:.2f} | "
                 f"{v['run_pairs_won_x']} / {v['run_pairs_won_y']} / {v['need']} из {v['run_pairs']} | {pv} | {v['both_bad']} | **{v['verdict']}** |")
    return '\n'.join(L) + '\n'


def cmd_tally(a):
    st = load_stand()
    r = st.tally(a.votes, a.key)
    md = st.tally_md(r)
    g = r.get('gold') or {}
    c = r.get('consistency') or {}
    valid = (g.get('total', 0) == 0 or g.get('correct') == g.get('total')) and (not c.get('total') or (c.get('share') or 0) >= 0.5)
    parts = [md]
    for q in ('slot', 'natural'):
        parts.append(verdicts_md(verdicts(a.votes, a.key, a.runs, q), q))
    parts.append(f"- Голосование {'засчитано' if valid else 'НЕ засчитано (контрольная пара или повторы) — переголосовать позже'}.\n")
    text = '\n'.join(parts)
    if a.out:
        Path(a.out).write_text(text, encoding='utf-8')
        Path(a.out).with_suffix('.json').write_text(json.dumps({'stand_run': r, 'valid': valid,
                                                               'verdicts': {q: verdicts(a.votes, a.key, a.runs, q) for q in ('slot', 'natural')}},
                                                              ensure_ascii=False, indent=1), encoding='utf-8')
    print(text)
    return 0


# ───────────────────────────── power ─────────────────────────────
def sim_campaign(rnd, briefs, runs, views, diff, run_sd, tau, tie, cluster_share=0.75):
    """Одна кампания «X против Y»: скрытое качество прогона ~ N(μ, run_sd), μ_X − μ_Y = diff; голос по виду — логистика."""
    gs = []
    for b in range(briefs):
        qx = [diff + rnd.gauss(0, run_sd) for _ in range(runs)]
        qy = [rnd.gauss(0, run_sd) for _ in range(runs)]
        for i in range(runs):
            for j in range(runs):
                for v in range(views):
                    if rnd.random() < tie:
                        s = 0.5
                    else:
                        s = 1.0 if rnd.random() < sigmoid((qx[i] - qy[j]) / tau) else 0.0
                    gs.append(((b, i), (b, j), s))
    n = len(gs)
    k = sum(g[2] for g in gs)
    p, lo, hi = wilson(k, n)
    cl = {}
    for rx, ry, s in gs:
        cl.setdefault((rx, ry), []).append(s)
    nc = len(cl)
    need = math.ceil(cluster_share * nc)
    won_x = sum(1 for ss in cl.values() if sum(ss) > len(ss) / 2)
    won_y = sum(1 for ss in cl.values() if sum(ss) < len(ss) / 2)
    if lo > 0.5 and won_x >= need:
        return 'X', p
    if hi < 0.5 and won_y >= need:
        return 'Y', p
    return '=', p


def cmd_power(a):
    rnd = random.Random(a.seed)
    designs = [tuple(int(x) for x in d.split('x')) for d in a.designs.split(',')]
    diffs = [float(x) for x in a.diffs.split(',')]
    L = ['# Мощность правила решения стенда — симуляция stand_page.py power', '',
         f'Модель: скрытое качество прогона ~ N(μ условия, {a.run_sd}); голос по виду: P(X) = σ((q_X − q_Y)/{a.tau}); ничья {a.tie}; '
         f'{a.views} вида на пару прогонов; правило — Уилсон > 0,5 и ≥ 75 % пар прогонов; {a.sims} кампаний на клетку. '
         'Ячейка: доля кампаний с вердиктом «X лучше» (при разнице 0 — ложные срабатывания в любую сторону); в скобках — средняя доля голосов за X.', '',
         '| Разница μ | ' + ' | '.join(f'{b} бриф. × {r} прог. ({r * r * a.views * b} пар)' for b, r in designs) + ' |',
         '|---|' + '---|' * len(designs)]
    res = {}
    for d in diffs:
        cells = []
        for b, r in designs:
            wins, false_any, shares = 0, 0, []
            for _ in range(a.sims):
                v, p = sim_campaign(rnd, b, r, a.views, d, a.run_sd, a.tau, a.tie)
                shares.append(p)
                wins += v == 'X'
                false_any += v != '='
            rate = (false_any if d == 0 else wins) / a.sims
            res[(d, b, r)] = rate
            cells.append(f'{rate:.2f} ({sum(shares) / len(shares):.2f})')
        L.append(f'| {d} | ' + ' | '.join(cells) + ' |')
    text = '\n'.join(L) + '\n'
    if a.out:
        Path(a.out).write_text(text, encoding='utf-8')
    print(text)
    return 0


# ───────────────────────────── fake + selftest ─────────────────────────────
def cmd_fake(a):
    from PIL import Image, ImageDraw
    rnd = random.Random(a.seed)
    out = Path(a.out)
    rows = []
    n = 0
    for brief in a.briefs.split(','):
        for cond in a.conditions.split(','):
            for run in range(1, a.runs + 1):
                n += 1
                d = out / f'shots-{n:03d}'          # имя папки не выдаёт условие
                d.mkdir(parents=True, exist_ok=True)
                hue = rnd.random()
                for view, (w, h) in {'desktop-1440x900-00': (1440, 900), 'mobile-390x844-00': (390, 844),
                                     'desktop-1440x900-map': (360, 1100)}.items():
                    im = Image.new('RGB', (w, h), tuple(int(200 + 40 * rnd.random()) for _ in range(3)))
                    dr = ImageDraw.Draw(im)
                    for _ in range(8):
                        x0, y0 = rnd.randrange(0, w - 40), rnd.randrange(0, h - 40)
                        x1, y1 = min(w, x0 + rnd.randrange(40, max(41, w // 2))), min(h, y0 + rnd.randrange(20, max(21, h // 4)))
                        col = tuple(int(255 * c) for c in __import__('colorsys').hsv_to_rgb((hue + rnd.random() * 0.1) % 1, 0.5, 0.6))
                        dr.rectangle([x0, y0, x1, y1], fill=col)
                    dr.text((16, 16), f'FAKE screen {n:03d}', fill=(20, 20, 20))
                    im.save(d / f'{view}.jpg', quality=80)
                rows.append({'test': a.test, 'brief': brief, 'brief_text': f'Бриф {brief}: вымышленный продукт для проверки страницы',
                             'condition': cond, 'run': str(run), 'shots_dir': str(d.resolve())})
    with open(a.manifest_out, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter='\t')
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({'runs': len(rows), 'manifest': a.manifest_out, 'dir': str(out)}, ensure_ascii=False))
    return 0


def cmd_selftest(a):
    import tempfile
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(('OK   ' if cond else 'FAIL ') + name)
    p, lo, hi = wilson(10, 12)
    check(f'Уилсон 10/12 = {p:.2f} [{lo:.3f}; {hi:.3f}] — нижняя > 0,5', lo > 0.5)
    p, lo, hi = wilson(9, 12)
    check(f'Уилсон 9/12 = {p:.2f} [{lo:.3f}; {hi:.3f}] — нижняя ≤ 0,5', lo <= 0.5)
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(__file__))) as td:
        ns = argparse.Namespace
        cmd_fake(ns(out=f'{td}/shots', manifest_out=f'{td}/runs.tsv', test='T-501', conditions='k3,opus,fable', briefs='S1',
                    runs=2, seed=3))
        rc = cmd_build(ns(manifest=f'{td}/runs.tsv', out=f'{td}/page', views=DEF_VIEWS, title='Стенд · selftest', repeat=0.1, seed=7))
        check('страница собрана и слепа (нет имён условий и путей)', rc == 0)
        key = json.loads(Path(f'{td}/page.key.json').read_text(encoding='utf-8'))
        check(f"пар: {len(key['pairs'])} (36 основных + повторы и контрольные)", len(key['pairs']) >= 36)
        check('ключ лежит рядом со страницей, не внутри', not Path(f'{td}/page/page.key.json').exists())
        cmd_simulate(ns(key=f'{td}/page.key.json', runs=f'{td}/page.runs.json', truth=['T-501:k3=0,opus=-1.5,fable=1.5'],
                        run_sd=0.1, tau=0.35, tie=0.05, seed=1, voter='scripted', out=f'{td}/votes.json'))
        vs = verdicts([f'{td}/votes.json'], f'{td}/page.key.json', f'{td}/page.runs.json')
        vd = {(v['x'], v['y']): v['verdict'] for v in vs}
        check(f'вердикт fable > k3: {vd.get(("fable", "k3"))}', vd.get(('fable', 'k3')) == 'fable лучше')
        check(f'вердикт k3 > opus: {vd.get(("k3", "opus"))}', vd.get(('k3', 'opus')) == 'k3 лучше')
        rnd = random.Random(13)
        fp = sum(sim_campaign(rnd, 1, 2, 3, 0.0, 0.15, 0.35, 0.12)[0] != '=' for _ in range(400)) / 400
        check(f'ложные «лучше» при равных условиях (1 бриф × 2 прогона, шум прогона 0,15): {fp:.2f} ≤ 0,15', fp <= 0.15)
        pw = sum(sim_campaign(rnd, 1, 3, 3, 0.9, 0.15, 0.35, 0.12)[0] == 'X' for _ in range(400)) / 400
        check(f'мощность при сильном перевесе (1 бриф × 3 прогона, разница 0,9): {pw:.2f} ≥ 0,8', pw >= 0.8)
    print('selftest', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('--manifest', required=True); b.add_argument('--out', required=True)
    b.add_argument('--views', default=DEF_VIEWS); b.add_argument('--title', default='Стенд тестов — слепой выбор')
    b.add_argument('--repeat', type=float, default=0.1); b.add_argument('--seed', type=int, default=7)
    s = sub.add_parser('simulate'); s.add_argument('--key', required=True); s.add_argument('--runs', required=True)
    s.add_argument('--truth', action='append', required=True); s.add_argument('--run-sd', type=float, default=0.3)
    s.add_argument('--tau', type=float, default=0.35); s.add_argument('--tie', type=float, default=0.12)
    s.add_argument('--seed', type=int, default=1); s.add_argument('--voter', default='scripted'); s.add_argument('--out', required=True)
    t = sub.add_parser('tally'); t.add_argument('votes', nargs='+'); t.add_argument('--key', required=True)
    t.add_argument('--runs', required=True); t.add_argument('--out')
    p = sub.add_parser('power'); p.add_argument('--designs', default='1x2,1x3,2x2,3x2'); p.add_argument('--diffs', default='0,0.2,0.4,0.6,0.9')
    p.add_argument('--sims', type=int, default=2000); p.add_argument('--views', type=int, default=3)
    p.add_argument('--run-sd', type=float, default=0.3); p.add_argument('--tau', type=float, default=0.35)
    p.add_argument('--tie', type=float, default=0.12); p.add_argument('--seed', type=int, default=11); p.add_argument('--out')
    f = sub.add_parser('fake'); f.add_argument('--out', required=True); f.add_argument('--manifest-out', required=True)
    f.add_argument('--test', default='T-501'); f.add_argument('--conditions', default='k3,opus,fable')
    f.add_argument('--briefs', default='S1'); f.add_argument('--runs', type=int, default=2); f.add_argument('--seed', type=int, default=3)
    sub.add_parser('selftest')
    a = ap.parse_args()
    return {'build': cmd_build, 'simulate': cmd_simulate, 'tally': cmd_tally, 'power': cmd_power, 'fake': cmd_fake,
            'selftest': cmd_selftest}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
