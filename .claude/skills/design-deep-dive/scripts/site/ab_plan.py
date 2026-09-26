#!/usr/bin/env python3
"""ab_plan.py — план и проверка A/B-теста страницы сайта (агент P, волна 2 site-research, 2026-09-24).

Что считает (только стандартная библиотека; numpy — по желанию, для симуляций):
  size      выборка на вариант для двух долей (двусторонний α, мощность) — точная формула без объединения дисперсий
            (как опыт A/04) и правило Кохави n = 16σ²/δ²; поправка Бонферрони для A/B/n
  duration  дни и полные недели при заданном трафике; вердикт «реально / долго / нереально»
  mde       минимальный обнаружимый эффект при заданном трафике и числе недель
  srm       проверка соотношения выборок (sample ratio mismatch) хи-квадратом, порог ExP p < 0,0005
  fpr       риск ложной победы (false positive risk) по доле успешных идей, α и мощности (Kohavi, Deng, Vermeer 2022)
  analyze   итог теста: сначала SRM, затем z-тест двух долей, интервал разницы, относительный эффект, FPR,
            закон Твимана, правило «0,01 < p < 0,05 → повторить»
  peeking   инфляция ложных срабатываний при k просмотрах и номинальный порог Pocock для k анализов (симуляция)
  --selftest  сверка с первоисточниками (A/04, Intuition Busters 2022, Fabijan 2019, Evan Miller 2010) и Монте-Карло

Примеры:
  python3 99-raw/tools/ab_plan.py size --base 0.05 --mde-rel 0.20
  python3 99-raw/tools/ab_plan.py duration --base 0.03 --mde-rel 0.25 --visits-per-day 400 --share 1.0
  python3 99-raw/tools/ab_plan.py mde --base 0.03 --visits-per-day 400 --weeks 4
  python3 99-raw/tools/ab_plan.py srm 821588 815482
  python3 99-raw/tools/ab_plan.py fpr --success-rate 0.10
  python3 99-raw/tools/ab_plan.py analyze --visitors 5210 5187 --conversions 161 198 --success-rate 0.15
  python3 99-raw/tools/ab_plan.py peeking --looks 28
  python3 99-raw/tools/ab_plan.py --selftest
Вывод — человекочитаемый; `--json` — JSON. Код выхода: 0 — норма; 2 — SRM или вердикт «нереально»; 1 — ошибка ввода.
"""
import argparse
import json
import math
import random
import sys
from statistics import NormalDist

N01 = NormalDist()
Z = N01.inv_cdf
PHI = N01.cdf
SRM_P_THRESHOLD = 0.0005      # Microsoft ExP: «conservative… p-value < 0.0005» (MSR, Diagnosing SRM)
MAX_WEEKS_OK = 4              # дольше — растут новизна, cookie churn, внешние события (Kohavi & Longbotham 2015)
MAX_WEEKS_HARD = 8            # дольше — тест на сайте с таким трафиком не ставить (исследование вместо теста)
TWYMAN_REL = 0.30             # относительный эффект > 30 % от правки — «подозрительно, ищи ошибку» (порог P)


# ---------------------------------------------------------------- статистика
def gammaincc(a, x):
    """Регуляризованная верхняя неполная гамма Q(a, x) (ряд / цепная дробь, Numerical Recipes)."""
    if x < 0 or a <= 0:
        raise ValueError('gammaincc: a > 0, x >= 0')
    if x == 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1:  # ряд для P, затем Q = 1 − P
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(10000):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return max(0.0, 1.0 - s * math.exp(-x + a * math.log(x) - gln))
    b = x + 1 - a  # цепная дробь Ленца для Q
    c, d = 1 / 1e-300, 1 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def chi2_sf(x, df):
    return gammaincc(df / 2.0, x / 2.0)


def n_two_prop(p1, p2, alpha=0.05, power=0.80, two_sided=True):
    """Выборка на вариант (равные ветки), дисперсии без объединения — как A/04."""
    za = Z(1 - alpha / 2) if two_sided else Z(1 - alpha)
    zb = Z(power)
    return (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2


def n_rule16(p, delta_abs):
    """Правило Кохави / van Belle: n = 16σ²/δ² на вариант (α 0,05 двусторонний, мощность 80 %)."""
    return 16 * p * (1 - p) / delta_abs ** 2


def power_two_prop(p1, p2, n, alpha=0.05):
    """Мощность двустороннего z-теста при n на вариант (без хвоста «не той стороны»)."""
    se = math.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / n)
    return PHI(abs(p2 - p1) / se - Z(1 - alpha / 2))


def mde_abs(p, n, alpha=0.05, power=0.80):
    """Обнаружимый абсолютный эффект при n на вариант (приближение σ² = p(1−p) в обеих ветках)."""
    return (Z(1 - alpha / 2) + Z(power)) * math.sqrt(2 * p * (1 - p) / n)


def fpr(success_rate, alpha_one_side=0.025, power=0.80):
    """False positive risk = α·π / (α·π + (1−β)(1−π)), π = 1 − доля успешных идей (Kohavi, Deng, Vermeer 2022)."""
    pi = 1 - success_rate
    return alpha_one_side * pi / (alpha_one_side * pi + power * (1 - pi))


def alpha_for_fpr(success_rate, target=0.05, power=0.80):
    """Двусторонний α, при котором FPR = target: α/2 = target(1−β)(1−π)/((1−target)π)."""
    pi = 1 - success_rate
    return 2 * target * power * (1 - pi) / ((1 - target) * pi)


def posthoc_power(pvalue, alpha=0.05):
    """«Наблюдаемая мощность» — функция одного p-value; её не показывают как довод (Kohavi 2022, Hoenig 2001)."""
    return PHI(Z(1 - pvalue / 2) - Z(1 - alpha / 2))


def srm_test(counts, ratios=None):
    k = len(counts)
    ratios = ratios or [1.0 / k] * k
    s = sum(ratios)
    ratios = [r / s for r in ratios]
    total = sum(counts)
    exp = [total * r for r in ratios]
    chi2 = sum((o - e) ** 2 / e for o, e in zip(counts, exp))
    p = chi2_sf(chi2, k - 1)
    return {'counts': counts, 'expected': [round(e, 1) for e in exp], 'observed_share': [round(c / total, 5) for c in counts],
            'chi2': round(chi2, 4), 'df': k - 1, 'p_value': p, 'threshold': SRM_P_THRESHOLD, 'srm': p < SRM_P_THRESHOLD}


def two_prop_test(n1, x1, n2, x2, alpha=0.05):
    p1, p2 = x1 / n1, x2 / n2
    pp = (x1 + x2) / (n1 + n2)
    se0 = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se0 if se0 > 0 else 0.0
    p = 2 * (1 - PHI(abs(z)))
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    zc = Z(1 - alpha / 2)
    rel = (p2 - p1) / p1 if p1 > 0 else float('nan')
    # относительный эффект: дельта-метод для log(p2/p1)
    if x1 > 0 and x2 > 0:
        se_log = math.sqrt((1 - p1) / x1 + (1 - p2) / x2)
        lo, hi = math.exp(math.log(p2 / p1) - zc * se_log) - 1, math.exp(math.log(p2 / p1) + zc * se_log) - 1
    else:
        lo = hi = float('nan')
    return {'rate_a': p1, 'rate_b': p2, 'diff_abs': p2 - p1, 'diff_ci': (p2 - p1 - zc * se, p2 - p1 + zc * se),
            'lift_rel': rel, 'lift_rel_ci': (lo, hi), 'z': z, 'p_value': p}


def plan(base, mde_rel=None, mde_abs_=None, alpha=0.05, power=0.80, variants=2, visits_per_day=None, share=1.0):
    if mde_abs_ is None:
        mde_abs_ = base * mde_rel
    p2 = base + mde_abs_
    alpha_eff = alpha / (variants - 1) if variants > 2 else alpha      # Бонферрони: сравнения с контролем
    n = math.ceil(n_two_prop(base, p2, alpha_eff, power))
    out = {'base': base, 'mde_abs': mde_abs_, 'mde_rel': mde_abs_ / base, 'alpha': alpha, 'alpha_per_comparison': alpha_eff,
           'power': power, 'variants': variants, 'n_per_variant': n, 'n_total': n * variants,
           'n_rule16_per_variant': math.ceil(n_rule16(base, mde_abs_)), 'conversions_control': round(n * base)}
    if visits_per_day:
        days = out['n_total'] / (visits_per_day * share)
        weeks = max(1, math.ceil(days / 7))
        verdict = 'ok' if weeks <= MAX_WEEKS_OK else ('long' if weeks <= MAX_WEEKS_HARD else 'infeasible')
        out.update({'visits_per_day': visits_per_day, 'share_in_test': share, 'days_raw': round(days, 1),
                    'weeks_full': weeks, 'days_planned': weeks * 7, 'verdict': verdict})
        if verdict == 'infeasible':
            out['advice'] = ('трафика мало: тестировать только крупную развилку (эффект ≥ 30–50 %), либо не тестировать — '
                             'исследование, пятисекундный тест, тест с людьми, опрос на выходе; решение — по доказательствам')
        elif verdict == 'long':
            out['advice'] = 'дольше 4 недель: риск новизны, churn cookie и внешних событий; увеличить долю трафика или MDE'
    return out


def pocock_nominal(looks, sims=200000, seed=7, target=0.05):
    """Номинальный двусторонний α на каждом из `looks` равноотстоящих анализов, дающий общий α = target.
    Броуновское движение: Z_k = S_k / sqrt(k); ищем c: P(max_k |Z_k| > c) = target (бинарный поиск по симуляции)."""
    rng = random.Random(seed)
    maxabs = []
    for _ in range(sims):
        s = 0.0
        m = 0.0
        for k in range(1, looks + 1):
            s += rng.gauss(0, 1)
            v = abs(s) / math.sqrt(k)
            if v > m:
                m = v
        maxabs.append(m)
    maxabs.sort()
    c = maxabs[int((1 - target) * sims)]
    naive = sum(1 for v in maxabs if v > Z(1 - target / 2)) / sims
    return {'looks': looks, 'boundary_z': c, 'nominal_alpha': 2 * (1 - PHI(c)), 'type1_if_naive': naive}


# ---------------------------------------------------------------- вывод
def fmt(d):
    return json.dumps(d, ensure_ascii=False, indent=1, default=lambda o: round(o, 6) if isinstance(o, float) else str(o))


def cmd_size(a):
    r = plan(a.base, a.mde_rel, a.mde_abs, a.alpha, a.power, a.variants, a.visits_per_day, a.share)
    if a.json:
        print(fmt(r))
    else:
        print(f"база {r['base']:.2%}, MDE {r['mde_rel']:+.1%} отн. ({r['mde_abs']:.3%} абс.), α {r['alpha']} "
              f"(на сравнение {r['alpha_per_comparison']:.4f}), мощность {r['power']:.0%}, вариантов {r['variants']}")
        print(f"на вариант: {r['n_per_variant']:,} (правило 16σ²/δ²: {r['n_rule16_per_variant']:,}); всего {r['n_total']:,}; "
              f"конверсий в контроле ≈ {r['conversions_control']:,}".replace(',', ' '))
        if 'weeks_full' in r:
            print(f"трафик {r['visits_per_day']}/день × доля {r['share_in_test']:.0%}: {r['days_raw']} дн. → "
                  f"{r['weeks_full']} полн. нед. ({r['days_planned']} дн.) — вердикт: {r['verdict']}")
            if r.get('advice'):
                print('совет:', r['advice'])
    return 2 if r.get('verdict') == 'infeasible' else 0


def cmd_mde(a):
    n_per = a.visits_per_day * a.share * a.weeks * 7 / a.variants
    alpha_eff = a.alpha / (a.variants - 1) if a.variants > 2 else a.alpha
    d = mde_abs(a.base, n_per, alpha_eff, a.power)
    r = {'n_per_variant': int(n_per), 'mde_abs': d, 'mde_rel': d / a.base, 'weeks': a.weeks}
    print(fmt(r) if a.json else f"за {a.weeks} нед. по {int(n_per):,} на вариант обнаружим эффект ≥ {d / a.base:+.1%} отн. "
          f"({d:.3%} абс.) при базе {a.base:.2%}".replace(',', ' '))
    return 0


def cmd_srm(a):
    ratios = [float(x) for x in a.ratios.split(':')] if a.ratios else None
    r = srm_test([int(c) for c in a.counts], ratios)
    if a.json:
        print(fmt(r))
    else:
        print(f"доли {r['observed_share']}, ожидали {r['expected']}; χ² = {r['chi2']}, df = {r['df']}, p = {r['p_value']:.3g}")
        print('SRM: ДА — результат не показывать, искать причину (боты, редирект, триггер, старт, кэш)' if r['srm']
              else f"SRM нет (порог p < {SRM_P_THRESHOLD})")
    return 2 if r['srm'] else 0


def cmd_fpr(a):
    r = {'success_rate': a.success_rate, 'alpha_one_side': a.alpha / 2, 'power': a.power,
         'fpr': fpr(a.success_rate, a.alpha / 2, a.power), 'alpha_two_sided_for_fpr_5pct': alpha_for_fpr(a.success_rate, 0.05, a.power)}
    print(fmt(r) if a.json else f"доля успешных идей {a.success_rate:.0%}, α {a.alpha}, мощность {a.power:.0%}: FPR = {r['fpr']:.1%}; "
          f"для FPR 5 % нужен α ≈ {r['alpha_two_sided_for_fpr_5pct']:.4f}")
    return 0


def cmd_analyze(a):
    (n1, n2), (x1, x2) = a.visitors, a.conversions
    s = srm_test([n1, n2], [float(x) for x in a.ratios.split(':')] if a.ratios else None)
    t = two_prop_test(n1, x1, n2, x2, a.alpha)
    notes = []
    if s['srm']:
        notes.append('SRM: результат недействителен до разбора причины')
    if a.planned_n and min(n1, n2) < a.planned_n:
        notes.append(f'план не набран ({min(n1, n2)} < {a.planned_n} на вариант): решение не принимать (подглядывание)')
    if t['p_value'] < a.alpha and abs(t['lift_rel']) > TWYMAN_REL:
        notes.append(f"закон Твимана: эффект {t['lift_rel']:+.0%} слишком велик для правки — искать ошибку, повторить тест")
    if 0.01 < t['p_value'] < 0.05:
        notes.append('0,01 < p < 0,05: повторить тест и объединить p (Фишер/Стауффер) — правило Airbnb (Kohavi)')
    r = {'srm': s, 'test': t, 'notes': notes}
    if a.success_rate:
        r['fpr_at_threshold'] = fpr(a.success_rate, a.alpha / 2, a.power)
    if a.json:
        print(fmt(r))
    else:
        print(f"SRM: p = {s['p_value']:.3g} → {'ДА' if s['srm'] else 'нет'}")
        print(f"конверсия A {t['rate_a']:.3%}, B {t['rate_b']:.3%}; разница {t['diff_abs']:+.3%} "
              f"[{t['diff_ci'][0]:+.3%}; {t['diff_ci'][1]:+.3%}]; отн. {t['lift_rel']:+.1%} [{t['lift_rel_ci'][0]:+.1%}; {t['lift_rel_ci'][1]:+.1%}]; "
              f"z = {t['z']:.2f}, p = {t['p_value']:.4f}")
        if 'fpr_at_threshold' in r:
            print(f"риск ложной победы при доле успешных идей {a.success_rate:.0%}: {r['fpr_at_threshold']:.1%}")
        for n in notes:
            print('!', n)
    return 2 if s['srm'] else 0


def cmd_peeking(a):
    r = pocock_nominal(a.looks, a.sims)
    print(fmt(r) if a.json else f"{a.looks} равноотстоящих анализов: без поправки ложных ≈ {r['type1_if_naive']:.1%} вместо 5 %; "
          f"порог Pocock |z| > {r['boundary_z']:.3f} (номинальный α ≈ {r['nominal_alpha']:.4f} на каждом анализе)")
    return 0


# ---------------------------------------------------------------- самопроверка
def selftest():
    ok = True
    rows = []

    def check(name, got, want, tol):
        nonlocal ok
        good = abs(got - want) <= tol
        ok &= good
        rows.append(('PASS' if good else 'FAIL', name, got, want, tol))

    # 1) Опыт A/04 (та же формула, α 0,05, мощность 80 %) — `99-raw/experiments/A/04-sample-size/result.tsv`
    for base, lift, want in [(0.05, 0.20, 8155), (0.02, 0.10, 80679), (0.10, 0.50, 683), (0.066, 0.20, 6062)]:
        check(f'A/04 n на ветку, база {base}, +{lift:.0%}', round(n_two_prop(base, base * (1 + lift))), want, 1)
    # 2) Kohavi, Deng, Vermeer 2022 (Intuition Busters) §4: 16σ²/δ², база 3,7 %, +10 % → 41 642 на вариант
    check('16σ²/δ²: 3,7 %, +10 %', n_rule16(0.037, 0.0037), 41642, 5)
    # мощность при 80 на вариант — «about 3%»
    check('мощность при 80 на ветку (3,7 %, +10 %)', power_two_prop(0.037, 0.0407, 80), 0.03, 0.01)
    # 3) Таблицы 2–3 той же статьи: FPR при α = 0,025 (только улучшения)
    for sr, w80, w50, w20 in [(1 / 3, 0.059, 0.091, 0.200),  # «33 %» в статье = одна треть (Microsoft)
                              (0.20, 0.111, 0.167, 0.333), (0.15, 0.150, 0.221, 0.415),
                              (0.10, 0.220, 0.310, 0.529), (0.08, 0.264, 0.365, 0.590)]:
        check(f'FPR {sr:.0%} успехов, мощность 80 %', fpr(sr, 0.025, 0.8), w80, 0.0015)
        check(f'FPR {sr:.0%} успехов, мощность 50 %', fpr(sr, 0.025, 0.5), w50, 0.0015)
        check(f'FPR {sr:.0%} успехов, мощность 20 %', fpr(sr, 0.025, 0.2), w20, 0.0015)
    # α для FPR 5 % при мощности 3 % и 33 % успехов → «α = 0.0016»
    check('α для FPR 5 % (мощность 3 %, 33 %)', alpha_for_fpr(0.33, 0.05, 0.03), 0.0016, 0.0001)
    # пост-хок мощность при p = 0,009 → 74 %
    check('пост-хок мощность при p = 0,009', posthoc_power(0.009), 0.74, 0.01)
    # 4) Fabijan и др. 2019: 821 588 против 815 482 при 50/50 — «less than 1 in 500k»
    s = srm_test([821588, 815482])
    check('SRM Fabijan 2019: p (< 1/500 000)', s['p_value'], 1.8e-6, 0.2e-6)
    check('SRM Fabijan 2019: χ²', s['chi2'], 22.77, 0.05)
    # пересчёт W из дайджеста Кохави: ровно 1 000 000 при 50,2/49,8 → p ≈ 6·10⁻⁵
    check('SRM 502 000 / 498 000: p', srm_test([502000, 498000])['p_value'], 6.3e-5, 0.6e-5)
    # хи-квадрат с 2 степенями: SF(x) = exp(−x/2)
    check('χ² df=2, x=6: p = e^-3', chi2_sf(6.0, 2), math.exp(-3), 1e-12)
    # 5) Evan Miller 2010: номинальный порог для итоговых 5 % при N+1 анализах (≈ Pocock)
    for looks, want in [(2, 0.029), (3, 0.022), (4, 0.018), (6, 0.014), (11, 0.010)]:
        check(f'Pocock/Miller: {looks} анализов', pocock_nominal(looks, 120000)['nominal_alpha'], want, 0.0015)
    # 6) Монте-Карло: при n из формулы мощность ≈ 80 %, при нулевом эффекте ложных ≈ 5 %
    rng = random.Random(11)
    base, lift = 0.05, 0.20
    n = math.ceil(n_two_prop(base, base * (1 + lift)))
    sims = 3000
    hits = fa = 0
    for _ in range(sims):
        xa = _binom(rng, n, base)
        xb = _binom(rng, n, base * (1 + lift))
        xc = _binom(rng, n, base)
        hits += two_prop_test(n, xa, n, xb)['p_value'] < 0.05
        fa += two_prop_test(n, xa, n, xc)['p_value'] < 0.05
    check('Монте-Карло: мощность при n формулы', hits / sims, 0.80, 0.025)
    check('Монте-Карло: ложные при нулевом эффекте', fa / sims, 0.05, 0.012)
    # 7) Бонферрони для A/B/C: α на сравнение 0,025
    check('A/B/C: α на сравнение', plan(0.05, 0.2, variants=3)['alpha_per_comparison'], 0.025, 1e-12)
    for st, name, got, want, tol in rows:
        print(f'{st}  {name}: {got:.6g} (ожидали {want:.6g} ± {tol:g})')
    print(f"итог: {sum(r[0] == 'PASS' for r in rows)}/{len(rows)} PASS")
    return 0 if ok else 1


def _binom(rng, n, p):
    """Биномиальная выборка: нормальное приближение с поправкой (n·p ≥ 50) или прямой счёт."""
    if n * p >= 50 and n * (1 - p) >= 50:
        x = round(rng.gauss(n * p, math.sqrt(n * p * (1 - p))))
        return min(n, max(0, x))
    return sum(1 for _ in range(n) if rng.random() < p)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')

    def common(p, need_base=True):
        if need_base:
            p.add_argument('--base', type=float, required=True, help='базовая конверсия, доля (0.03 = 3 %%)')
        p.add_argument('--alpha', type=float, default=0.05)
        p.add_argument('--power', type=float, default=0.80)
        p.add_argument('--variants', type=int, default=2)
        p.add_argument('--json', action='store_true')

    p = sub.add_parser('size', help='выборка на вариант (и длительность, если задан трафик)')
    common(p)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--mde-rel', type=float, help='минимальный интересный эффект, относительный (0.2 = +20 %%)')
    g.add_argument('--mde-abs', type=float, help='минимальный интересный эффект, абсолютный (0.005 = +0,5 п.п.)')
    p.add_argument('--visits-per-day', type=float)
    p.add_argument('--share', type=float, default=1.0, help='доля трафика в тесте')
    p.set_defaults(fn=cmd_size)
    p = sub.add_parser('duration', help='то же, что size с обязательным трафиком')
    common(p)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--mde-rel', type=float)
    g.add_argument('--mde-abs', type=float)
    p.add_argument('--visits-per-day', type=float, required=True)
    p.add_argument('--share', type=float, default=1.0)
    p.set_defaults(fn=cmd_size)
    p = sub.add_parser('mde', help='обнаружимый эффект при трафике и длительности')
    common(p)
    p.add_argument('--visits-per-day', type=float, required=True)
    p.add_argument('--share', type=float, default=1.0)
    p.add_argument('--weeks', type=int, default=2)
    p.set_defaults(fn=cmd_mde)
    p = sub.add_parser('srm', help='проверка соотношения выборок')
    p.add_argument('counts', nargs='+')
    p.add_argument('--ratios', help='плановые доли, напр. 50:50 или 1:1:2')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_srm)
    p = sub.add_parser('fpr', help='риск ложной победы')
    p.add_argument('--success-rate', type=float, required=True, help='историческая доля успешных идей (0.1–0.33)')
    common(p, need_base=False)
    p.set_defaults(fn=cmd_fpr)
    p = sub.add_parser('analyze', help='итог теста двух вариантов')
    p.add_argument('--visitors', type=int, nargs=2, required=True, metavar=('A', 'B'))
    p.add_argument('--conversions', type=int, nargs=2, required=True, metavar=('A', 'B'))
    p.add_argument('--ratios')
    p.add_argument('--planned-n', type=int, help='плановая выборка на вариант (проверка подглядывания)')
    p.add_argument('--success-rate', type=float)
    common(p, need_base=False)
    p.set_defaults(fn=cmd_analyze)
    p = sub.add_parser('peeking', help='инфляция ложных при k просмотрах; порог Pocock')
    p.add_argument('--looks', type=int, required=True)
    p.add_argument('--sims', type=int, default=200000)
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_peeking)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.cmd:
        ap.print_help()
        return 1
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
