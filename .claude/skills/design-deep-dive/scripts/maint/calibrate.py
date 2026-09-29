#!/usr/bin/env python3
"""Калибровка оценки токенов баз знаний (`kb/<база>/`) под Claude Opus 5.5 через `claude -p` Claude Code (API-ключ не
нужен, сессия Claude Code — да).

Точные входные токены образца = usage(прогон с текстом на stdin) − usage(пустой прогон). По выборке тематических файлов
каждого вида (prose, data, code; выборка — по доле кириллицы) подгоняется tokens = a · кириллица + b · прочие символы
(МНК без свободного члена); результат — `calibration.json` рядом со скриптом, его читают `count_tokens.py` и
`layers.py`. Каждый образец — один вызов модели: ≈ 1 тыс. токенов обвязки + сам текст, поэтому калибровку запускают
осознанно (после крупной правки базы), а не в проверках.

  python3 .claude/skills/design-deep-dive/scripts/maint/calibrate.py                  # 12 prose + 6 data + 6 code
  python3 .claude/skills/design-deep-dive/scripts/maint/calibrate.py --prose 20 --seed 3
"""
import argparse
import json
import random
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from count_tokens import CYR, ROOT, is_bundle, kind_of, read_text, research_dirs, thematic_files  # noqa: E402

MODEL = "claude-opus-5-5"
CLAUDE = ["claude", "-p", "Reply with exactly: OK", "--model", MODEL, "--output-format", "json",
          "--tools", "", "--system-prompt", "You are a token counter. Reply with exactly: OK",
          "--no-session-persistence", "--strict-mcp-config", "--disable-slash-commands", "--effort", "low"]
FIT_KINDS = ("prose", "data", "code")


def input_tokens(text):
    """Все входные токены одного прогона (input + cache_creation + cache_read)."""
    proc = subprocess.run(CLAUDE, input=text, capture_output=True, text=True, timeout=900, cwd=HERE)
    data = json.loads(proc.stdout)
    models = set(data.get("modelUsage", {}))
    if data.get("is_error") or models != {MODEL}:
        raise RuntimeError(f"прогон не удался: is_error={data.get('is_error')}, models={models}, "
                           f"stderr={proc.stderr[:300]}")
    usage = data["usage"]
    return usage["input_tokens"] + usage["cache_creation_input_tokens"] + usage["cache_read_input_tokens"]


def candidates(min_chars, max_chars):
    pool = {kind: [] for kind in FIT_KINDS}
    for research in research_dirs():
        for section, path in thematic_files(research):
            kind = kind_of(path)
            if kind not in pool or section == "(root)":
                continue
            text = read_text(path)
            if text is None or not min_chars <= len(text) <= max_chars or is_bundle(path, text):
                continue
            pool[kind].append((path, text))
    return pool


def stratified(items, n, rng):
    """n файлов с разной долей кириллицы: сортируем по доле, режем на n корзин, из каждой — случайный."""
    items = sorted(items, key=lambda item: len(CYR.findall(item[1])) / len(item[1]))
    bins = [items[i * len(items) // n:(i + 1) * len(items) // n] for i in range(n)]
    return [rng.choice(bucket) for bucket in bins if bucket]


def fit(samples, fallback_a=None):
    """МНК для tokens = a·cyr + b·other. Если кириллицы почти нет — a берётся из fallback_a."""
    cyr = sum(s["cyr"] for s in samples)
    chars = sum(s["cyr"] + s["other"] for s in samples)
    if fallback_a is not None and cyr < 0.02 * chars:
        b = sum((s["tokens"] - fallback_a * s["cyr"]) * s["other"] for s in samples) / sum(s["other"] ** 2 for s in samples)
        return fallback_a, b
    sxx = sum(s["cyr"] ** 2 for s in samples)
    syy = sum(s["other"] ** 2 for s in samples)
    sxy = sum(s["cyr"] * s["other"] for s in samples)
    sxt = sum(s["cyr"] * s["tokens"] for s in samples)
    syt = sum(s["other"] * s["tokens"] for s in samples)
    det = sxx * syy - sxy ** 2
    return (sxt * syy - syt * sxy) / det, (syt * sxx - sxt * sxy) / det


def errors(samples, a, b):
    return [abs(a * s["cyr"] + b * s["other"] - s["tokens"]) / s["tokens"] for s in samples]


def loo(samples, fallback_a=None):
    errs = []
    for i, sample in enumerate(samples):
        a, b = fit(samples[:i] + samples[i + 1:], fallback_a)
        errs += errors([sample], a, b)
    return errs


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prose", type=int, default=12, help="образцов прозы (.md, .txt)")
    parser.add_argument("--data", type=int, default=6, help="образцов данных (.json, .yaml, .tsv …)")
    parser.add_argument("--code", type=int, default=6, help="образцов кода")
    parser.add_argument("--min-chars", type=int, default=3000, help="файл-образец не короче, знаков")
    parser.add_argument("--max-chars", type=int, default=30000, help="файл-образец не длиннее, знаков")
    parser.add_argument("--seed", type=int, default=7, help="зерно выборки")
    parser.add_argument("--workers", type=int, default=4, help="параллельных вызовов модели")
    parser.add_argument("--out", type=Path, default=HERE / "calibration.json", help="куда писать коэффициенты")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    pool = candidates(args.min_chars, args.max_chars)
    samples = []
    for kind in FIT_KINDS:
        for path, text in stratified(pool[kind], getattr(args, kind), rng):
            samples.append({"kind": kind, "path": str(path.relative_to(ROOT)), "text": text})
    # Так файл видит агент через Read (cat -n: номер строки + таб) — меряем надбавку на трёх prose.
    numbered = [{"kind": "read", "path": s["path"],
                 "text": "".join(f"{i:>6}\t{line}\n" for i, line in enumerate(s["text"].splitlines(), 1))}
                for s in samples if s["kind"] == "prose"][:3]

    texts = ["", "я"] + [s["text"] for s in samples + numbered] + [""]
    with ThreadPoolExecutor(args.workers) as executor:
        base_start, one_char, *measured, base_end = executor.map(input_tokens, texts)
    overhead = one_char - base_start - 1  # «я» считаем за 1 токен; остальное — обвязка stdin
    for sample, total in zip(samples + numbered, measured):
        sample["tokens"] = total - base_start - overhead
        sample["cyr"] = len(CYR.findall(sample["text"]))
        sample["other"] = len(sample["text"]) - sample["cyr"]

    prose = [s for s in samples if s["kind"] == "prose"]
    a_prose, _ = fit(prose)
    kinds = {}
    for kind in FIT_KINDS:
        group = [s for s in samples if s["kind"] == kind]
        fallback = None if kind == "prose" else a_prose
        a, b = fit(group, fallback)
        kinds[kind] = {"a": a, "b": b, "n": len(group),
                       "mape": sum(errors(group, a, b)) / len(group),
                       "loo_mape": sum(loo(group, fallback)) / len(group)}
    a_all, b_all = fit(samples)
    read_factor = [n["tokens"] / next(s["tokens"] for s in prose if s["path"] == n["path"]) for n in numbered]

    print(f"Модель {MODEL}; пустой прогон {base_start} (в конце {base_end}); обвязка stdin {overhead} ток.")
    print(f"{'вид':<6}{'симв':>8}{'кир%':>6}{'токенов':>9}{'симв/ток':>10}  файл")
    for s in samples + numbered:
        chars = s["cyr"] + s["other"]
        print(f"{s['kind']:<6}{chars:>8}{100 * s['cyr'] / chars:>5.0f}%{s['tokens']:>9}{chars / s['tokens']:>10.2f}"
              f"  {s['path'][:80]}")
    for kind, c in kinds.items():
        print(f"{kind:<6} a(кир)={c['a']:.4f}  b(проч)={c['b']:.4f}  n={c['n']}  "
              f"ошибка {100 * c['mape']:.1f}% (LOO {100 * c['loo_mape']:.1f}%)")
    print(f"общая  a={a_all:.4f}  b={b_all:.4f};  надбавка формата Read: "
          + ", ".join(f"×{f:.3f}" for f in read_factor))

    args.out.write_text(json.dumps({
        "model": MODEL, "measured_at": datetime.now().isoformat(timespec="seconds"),
        "baseline": [base_start, base_end], "overhead": overhead,
        "kinds": kinds, "global": {"a": a_all, "b": b_all},
        "read_tool_factor": sum(read_factor) / len(read_factor) if read_factor else None,
        "samples": [{k: v for k, v in s.items() if k != "text"} for s in samples + numbered],
    }, ensure_ascii=False, indent=2))
    print(f"→ {args.out}")


if __name__ == "__main__":
    main()
