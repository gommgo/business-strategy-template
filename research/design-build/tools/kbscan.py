#!/usr/bin/env python3
"""kbscan — счёт маркеров «внешнего» в базе знаний скилла design-deep-dive. Только стандартная библиотека.

Что считает. По каждому файлу `kb/`: вид (prose, data, code, bundle, bin), число строк, оценку токенов и число строк
с маркером каждого класса. Классы — то, от чего текстовая уборка абстрагирует базу: пути машины, ссылки на `99-raw`,
имя прежнего исполнителя макета, имена соседних баз с `-research`, процесс исследования (буквы агентов, волны, опыты),
номера «решений заказчика» исследований, следы журнала сборки, имена снятых утилит и подкоманд, ссылки на `PLAN.md`
баз и на витрину. Этим же скриптом приёмка зоны сверяет счёт «до» и «после».

Использование (из корня репозитория):
    python3 research/design-build/tools/kbscan.py                       # все файлы kb/, TSV в stdout
    python3 research/design-build/tools/kbscan.py --zone ЗОНА.tsv       # только файлы зоны (первая колонка — путь)
    python3 research/design-build/tools/kbscan.py --mask 'site/**'      # только файлы по маске (от kb/, можно повторять)
    python3 research/design-build/tools/kbscan.py --sum base            # свод по базам (или: dir — база/папка, kind)
    python3 research/design-build/tools/kbscan.py --list raw --mask 'ux/**/*.md'   # строки с маркером класса
    python3 research/design-build/tools/kbscan.py --classes            # классы, шаблоны и что с ними делает уборка
    python3 research/design-build/tools/kbscan.py --selftest           # самопроверка шаблонов на образцах

Ключи:
    --kb ПАПКА        папка базы (по умолчанию `.claude/skills/design-deep-dive/kb` от корня репозитория)
    --zone ФАЙЛ.tsv   список файлов зоны: первая колонка — путь от `kb/` (годится и `kb/…`, и путь от корня
                      репозитория); строки с «#» и строка заголовка пропускаются; файла нет на диске — строка `нет`
    --mask ГЛОБ       маска пути от `kb/` (fnmatch; `**` — любая глубина); --exclude ГЛОБ — исключение
    --only ВИД[,ВИД]  только виды файлов: prose, data, code, bundle, bin
    --extra ФАЙЛ.tsv  свои классы: «имя<TAB>регулярное выражение» (например, имя продукта заказчика — в скрипт не зашито)
    --matches         считать вхождения, а не строки
    --walk            обход диска вместо `git ls-files` (берёт и неотслеживаемые файлы)
    --out ФАЙЛ        писать TSV в файл

Колонки: file · kind · lines · tokens · <классы> · sum. `sum` — сумма целевых классов; справочные классы (`k3`,
`ns_dtcg`) в неё не входят: «K3» у ui — id проверки, `org.ui-research` — имя расширения DTCG, их правит не текстовая
зона. Последняя строка — `ИТОГО`.

Оценка токенов: tokens = a·кириллица + b·прочие знаки, коэффициенты по виду файла измерены на Opus 5.5
(`research/design-build/tools/calibration.json`, ошибка 6–8 %) и зашиты ниже; простое правило «знаков / 2,6» для md
базы занижает объём примерно на четверть — в md много таблиц, путей и латиницы. Чтение файла инструментом Read
добавляет номера строк: множитель ≈ 1,09 (`READ_FACTOR`), в колонку он не входит.

Код выхода: 0 — счёт напечатан; 1 — самопроверка не прошла; 2 — ошибка аргументов или входа.
"""
import argparse
import csv
import fnmatch
import os
import re
import subprocess
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]                                  # research/design-build/tools → корень репозитория
KB_DEFAULT = REPO / ".claude" / "skills" / "design-deep-dive" / "kb"
TRACES = REPO / ".claude" / "skills" / "design-deep-dive" / "scripts" / "maint" / "data" / "traces.tsv"

KINDS = {
    "prose": {".md", ".txt"},
    "data": {".json", ".jsonl", ".yaml", ".yml", ".tsv", ".csv", ".toml", ".xml", ".webmanifest", ".lock", ""},
    "code": {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".html", ".htm", ".css", ".py", ".sh", ".svg", ".glsl"},
}
# tokens = a * кириллица + b * прочие знаки (calibration.json, Opus 5.5)
COEF = {"prose": (0.3616, 0.6162), "data": (0.2045, 0.5230), "code": (0.5278, 0.4921), "bundle": (0.5104, 0.5076)}
READ_FACTOR = 1.09
BUNDLE_LINE = 5000                                      # строка длиннее — собранный или минифицированный код
CYR = re.compile(r"[\u0400-\u04FF]")

BASES = r"(?:ui|ux|site|text|creative|ai-media|blender|kimi|claude-design|cd|app)"
REMOVED = (
    r"\b(?:copy_extract|check_intake|make_skeleton|idle_probe|shot_v3|vm_sheet|validate_recipes|build_pairs|vote_server"
    r"|orch_check|count_tokens|upgrade_deck|ab_analyze|build_crosswalk)\b"
    r"|blender/(?:vote|regression)\b|\b(?:run_set|make_manifest|tally|calibrate|layers)\.py\b|\bcalibration\.json\b"
    r"|verify-page|digest-meaning|hierarchy-input|section-input|edit-input|apply-edits|canvas-texts"
)
# Следы журнала сборки — копия шаблонов forward-only из scripts/maint/data/traces.tsv (метки «Р-номер», «журнал»,
# «фаза сборки»); если файл на месте, шаблоны берутся из него.
JOURNAL_LABELS = ("Р-номер", "журнал", "фаза сборки")
JOURNAL_FALLBACK = (
    r"(?<![\w-])Р\d{1,3}(?!\d)"
    r"|research/design-build|design-build/|\bphase-\d\b|DECISIONS\.md|SYNTHESIS|CHAIN\.md"
    r"|(?<![\w-])Ф(?:[0-9]|10)(?![\w-])"
)

# имя · целевой (входит в sum) · шаблон · что это · что делает уборка · образцы «находит» · образцы «не находит»
CLASSES = OrderedDict([
    ("machine", (True,
        r"/home/[\w.-]+|/Users/[\w.-]+|(?<![\w/])Документы/|~/\.claude/plans|~/\.cache/[a-z-]+-research|\.nvm/versions",
        "путь машины исследования",
        "путь от корня скилла или от папки базы; окружение — `$DDD_HOME`",
        ['sys.path.insert(0, "/home/mm/Документы/app-design/blender-research/99-raw/tools")', "cd ~/.claude/plans/x.md"],
        ["`~/.cache/design-deep-dive/venv`", "`~/.claude.json` заказчика агент не меняет"])),
    ("raw", (True,
        r"99-raw|handoff-to-(?:neighbours|[a-z-]+-research)\.md|wave\d-[A-Z0-9]+-(?:audit|report)|triad-contract"
        r"|temp-vocabulary|prompts/_common\.md",
        "ссылка или упоминание `99-raw` и его файлов",
        "метка доказательности остаётся без пути; ссылка на отчёт, контракт, поправки — адрес нормы в базе или `kb/common/`",
        ["[проверено: 99-raw/experiments/H/14-camera-path]", "см. `handoff-to-neighbours.md` §3", "wave4-X-audit.md §2.1"],
        ["[проверено]", "raw-файл камеры"])),
    ("kimi", (True,
        r"(?i:kimi)|\bK2\.5\b",
        "имя прежнего исполнителя макета и его пакета",
        "вывод остаётся без имени («LLM-вёрстка», «исполнитель макета»); стык — вход холста Claude Design",
        ["пакет для kimi", "x-kimi-map", "Kimi K2.5 в бенчмарке"],
        ["Claude Design", "K2 summit"])),
    ("k3", (False,
        r"(?<![\w-])K3(?![\w-])",
        "«K3»: модель прежнего исполнителя или id проверки",
        "справочно: в `kb/ui/` это id проверки `ui_audit.py` — не трогать; в остальных базах — как `kimi`",
        ["генерация K3", "видео-референсы для K3"],
        ["K3-01", "LOOK-K3"])),
    ("research", (True,
        r"(?<![\w.])" + BASES + r"-research\b",
        "имя соседней базы с суффиксом `-research`",
        "имя базы без суффикса (`ux`, `site`) и короткий адрес «база NN/MM §N»",
        ["- [S3] ux-research, `05-flows-journeys/01-onboarding.md` §7", "клон `../../kimi-research/99-raw/cache/`"],
        ['"org.ui-research.llm": {', "user-research"])),
    ("ns_dtcg", (False,
        r"org\.ui-research",
        "имя расширения DTCG `org.ui-research.*`",
        "справочно: часть контракта токенов, правит зона кода вместе с `ds_build.py`",
        ['"org.ui-research.modes": {"dark": "x"}'],
        ["ui-research, файл 01"])),
    ("process", (True,
        r"[Аа]гент\w{0,3}\s+[A-Z][0-9A-Z]?\b"
        r"|(?i:волн\w{0,3})\s+\d|(?i:\bwave)[-_ ]?\d"
        r"|(?:[Оо]пыт\w{0,3}|[Ээ]ксперимент\w{0,3})\s+[A-Z][0-9A-Z]?(?:/\d+)?\b"
        r"|(?<![\w/.:-])[A-Z][0-9A-Z]?/\d{2}(?:-[a-z0-9-]+)?(?![\w/])"
        r"|phase5|(?i:фаз\w{0,3})\s+5\b|(?i:дорожк\w{0,3})\s+[A-Z]{1,2}\b|_ledger\.jsonl",
        "процесс исследования: буквы агентов, волны, опыты, дорожки, журналы прогонов",
        "снять; факт и его метка силы остаются; адрес опыта — адрес нормы в базе",
        ["- [S7] Агент E, волна 1.", "калибровка (опыт C/03)", "[проверено: D2/01]", "тема агента F", "не проверено в фазе 5"],
        ["ремонтного агента и конкретного судьи", "перламутровая волна", "раздел 03/02 §4", "WCAG 2.2/AA"])),
    ("decision", (True,
        r"(?i:решени\w{0,4})\s+заказчика[^.;\n]{0,14}?\d"
        r"|(?i:решени\w{0,4})\s+(?:№\s*|п\.\s*)?\d{1,2}\b(?![.,]\d)"
        r"|PLAN\s*№\s*\d+",
        "номер «решения заказчика» исследования как ссылка",
        "норма остаётся нормой, номер и слово «решение N» уходят",
        ["по умолчанию кампании — L2 (решение заказчика 15)", "сетка уровней решения 20", "поправка PLAN №7"],
        ["это решение заказчика", "решение принимает владелец продукта"])),
    ("journal", (True,
        JOURNAL_FALLBACK,
        "след журнала сборки шаблона: Р-номер, фаза, путь журнала",
        "снять: текст говорит о текущем состоянии",
        ["замер — после сборки (Р99)", "решено в Ф4", "research/design-build/phase-2/SYNTHESIS.md"],
        ["РФ", "WCAG 2.2", "Ф-образный паттерн"])),
    ("removed", (True,
        REMOVED,
        "имя снятой утилиты или подкоманды",
        "текст ведёт к живой утилите или этапу, либо абзац снимается",
        ["`copydeck.py verify-page`", "python3 orch_check.py", "scripts/blender/vote/build_pairs.py"],
        ["copydeck.py validate --final", "chain_inputs.py judge-input"])),
    ("plan", (True,
        r"PLAN\.md",
        "ссылка на `PLAN.md` базы (журнал исследования)",
        "норма — по адресу в README базы или `kb/common/`; ссылка на журнал снимается",
        ["значения и бюджеты — `../../creative/PLAN.md`"],
        ["page-plan.schema.json"])),
    ("showcase", (True,
        r"15-showcase",
        "ссылка на витрину испытания `kb/blender/15-showcase`",
        "по решению о витрине: ссылка на пример остаётся или снимается вместе с ней",
        ["метод — `15-showcase/KIT.md`"],
        ["showcase страницы"])),
])


def load_journal():
    """Шаблоны следов журнала из traces.tsv скилла (forward-only: Р-номер, журнал, фаза сборки)."""
    if not TRACES.is_file():
        return JOURNAL_FALLBACK, "встроенная копия"
    parts = []
    for line in TRACES.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) >= 3 and cols[0] == "forward-only" and cols[1] in JOURNAL_LABELS:
            parts.append(cols[2])
    if len(parts) != len(JOURNAL_LABELS):
        return JOURNAL_FALLBACK, "встроенная копия (в traces.tsv нет трёх меток)"
    return "|".join("(?:%s)" % p for p in parts), str(TRACES.relative_to(REPO))


def compile_classes(extra=None):
    out = OrderedDict()
    journal, _ = load_journal()
    for name, (target, pat, what, todo, pos, neg) in CLASSES.items():
        if name == "journal":
            pat = journal
        out[name] = (target, re.compile(pat))
    for name, pat in (extra or []):
        out[name] = (True, re.compile(pat))
    return out


def kind_of(path):
    ext = path.suffix.lower()
    for k, exts in KINDS.items():
        if ext in exts:
            return k
    return "bin"


def scan_file(path, classes, matches=False):
    """→ (kind, lines, tokens, {класс: счёт}); нечитаемый как UTF-8 файл — вид bin без счёта."""
    kind = kind_of(path)
    zero = {name: 0 for name in classes}
    if kind == "bin":
        return kind, 0, 0, zero
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return "bin", 0, 0, zero
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if kind == "code" and any(len(l) > BUNDLE_LINE for l in lines):
        kind = "bundle"
    cyr = len(CYR.findall(text))
    a, b = COEF[kind]
    tokens = int(round(a * cyr + b * (len(text) - cyr)))
    counts = dict(zero)
    for line in lines:
        for name, (_, rx) in classes.items():
            if matches:
                counts[name] += sum(1 for _ in rx.finditer(line))
            elif rx.search(line):
                counts[name] += 1
    return kind, len(lines), tokens, counts


def list_files(kb, walk=False):
    """Пути от kb/, отсортированы. По умолчанию — отслеживаемые git; иначе обход диска."""
    if not walk:
        try:
            r = subprocess.run(["git", "-C", str(kb), "ls-files", "-z", "."], capture_output=True, check=True)
            rel = [p for p in r.stdout.decode("utf-8").split("\0") if p]
            if rel:
                return sorted(rel)
        except (OSError, subprocess.CalledProcessError):
            pass
    out = []
    for root, dirs, files in os.walk(kb):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for f in files:
            out.append(os.path.relpath(os.path.join(root, f), kb))
    return sorted(out)


def norm_zone_path(raw, kb):
    p = raw.strip().strip("`").replace("\\", "/")
    marker = "design-deep-dive/kb/"
    if marker in p:
        p = p.split(marker, 1)[1]
    elif p.startswith("kb/"):
        p = p[3:]
    return p


def read_zone(path, kb):
    files = []
    with open(path, encoding="utf-8") as f:
        for i, row in enumerate(csv.reader(f, delimiter="\t")):
            if not row or not row[0].strip() or row[0].startswith("#"):
                continue
            first = row[0].strip()
            if i == 0 and first.lower() in ("file", "файл", "path", "путь"):
                continue
            if first.endswith("/"):                       # строка-папка списка зоны: счёт идёт по файлам
                continue
            files.append(norm_zone_path(first, kb))
    seen, out = set(), []
    for p in files:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def glob_match(rel, pattern):
    if fnmatch.fnmatchcase(rel, pattern):
        return True
    if "**/" in pattern:                                  # `a/**/b` покрывает и `a/b`
        return fnmatch.fnmatchcase(rel, pattern.replace("**/", ""))
    return False


def selftest():
    classes = compile_classes()
    bad = 0
    for name, (target, pat, what, todo, pos, neg) in CLASSES.items():
        rx = classes[name][1]
        for s in pos:
            if not rx.search(s):
                print("FAIL %s: не находит «%s»" % (name, s)); bad += 1
        for s in neg:
            if rx.search(s):
                print("FAIL %s: ложно находит «%s»" % (name, s)); bad += 1
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        kb = Path(d)
        (kb / "site").mkdir()
        (kb / "site" / "a.md").write_text("Норма [проверено: 99-raw/experiments/A/01-x].\nАгент B, волна 2.\nЧисто.\n",
                                           encoding="utf-8")
        (kb / "site" / "b.yaml").write_text("x: 1\n", encoding="utf-8")
        kind, lines, tokens, c = scan_file(kb / "site" / "a.md", classes)
        if (kind, lines, c["raw"], c["process"]) != ("prose", 3, 1, 1) or tokens <= 0:
            print("FAIL scan_file: %r" % ((kind, lines, tokens, c),)); bad += 1
        zone = kb / "z.tsv"
        zone.write_text("file\tactions\nkb/site/a.md\tx\n# комментарий\nsite/нет.md\t\n", encoding="utf-8")
        if read_zone(zone, kb) != ["site/a.md", "site/нет.md"]:
            print("FAIL read_zone: %r" % read_zone(zone, kb)); bad += 1
        if not glob_match("site/a.md", "site/**/*.md") or glob_match("ui/a.md", "site/**"):
            print("FAIL glob_match"); bad += 1
    print("selftest: %s" % ("OK" if not bad else "ошибок %d" % bad))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="Счёт маркеров «внешнего» в kb/ скилла design-deep-dive.",
                                 epilog="Подробности — докстринг файла.")
    ap.add_argument("--kb", default=str(KB_DEFAULT))
    ap.add_argument("--zone")
    ap.add_argument("--mask", action="append", default=[])
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--only")
    ap.add_argument("--extra")
    ap.add_argument("--matches", action="store_true")
    ap.add_argument("--walk", action="store_true")
    ap.add_argument("--sum", choices=("base", "dir", "kind"))
    ap.add_argument("--list", metavar="КЛАСС")
    ap.add_argument("--classes", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.classes:
        journal, src = load_journal()
        for name, (target, pat, what, todo, pos, neg) in CLASSES.items():
            if name == "journal":
                pat = journal
                what += " (шаблоны: %s)" % src
            print("%s\t%s\t%s\t%s\t%s" % (name, "целевой" if target else "справочный", what, todo, pat))
        return 0

    kb = Path(a.kb).resolve()
    if not kb.is_dir():
        print("нет папки базы: %s" % kb, file=sys.stderr)
        return 2
    extra = []
    if a.extra:
        for line in Path(a.extra).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                name, _, pat = line.partition("\t")
                extra.append((name.strip(), pat.strip()))
    try:
        classes = compile_classes(extra)
    except re.error as e:
        print("ошибка шаблона: %s" % e, file=sys.stderr)
        return 2
    if a.list and a.list not in classes:
        print("нет класса «%s»; есть: %s" % (a.list, ", ".join(classes)), file=sys.stderr)
        return 2

    if a.zone:
        rels = read_zone(a.zone, kb)
    else:
        rels = list_files(kb, a.walk)
    if a.mask:
        rels = [r for r in rels if any(glob_match(r, m) for m in a.mask)]
    if a.exclude:
        rels = [r for r in rels if not any(glob_match(r, m) for m in a.exclude)]
    only = set(a.only.split(",")) if a.only else None

    out = open(a.out, "w", encoding="utf-8", newline="") if a.out else sys.stdout
    names = list(classes)
    targets = [n for n in names if classes[n][0]]

    if a.list:
        rx = classes[a.list][1]
        for rel in rels:
            p = kb / rel
            if not p.is_file() or kind_of(p) == "bin":
                continue
            if only and kind_of(p) not in only:
                continue
            try:
                text = p.read_bytes().decode("utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in enumerate(text.split("\n"), 1):
                if rx.search(line):
                    out.write("%s:%d:\t%s\n" % (rel, i, line.strip()[:300]))
        return 0

    rows, missing = [], 0
    for rel in rels:
        p = kb / rel
        if not p.is_file():
            rows.append((rel, "нет", 0, 0, {n: 0 for n in names}))
            missing += 1
            continue
        kind, lines, tokens, counts = scan_file(p, classes, a.matches)
        if only and kind not in only:
            continue
        rows.append((rel, kind, lines, tokens, counts))

    def write(first, kind, lines, tokens, counts):
        s = sum(counts[n] for n in targets)
        out.write("\t".join([first, kind, str(lines), str(tokens)] + [str(counts[n]) for n in names] + [str(s)]) + "\n")

    out.write("\t".join(["file" if not a.sum else a.sum, "kind" if not a.sum else "files", "lines", "tokens"] + names + ["sum"]) + "\n")
    total = {n: 0 for n in names}
    tl = tt = 0
    if a.sum:
        agg = defaultdict(lambda: [0, 0, 0, {n: 0 for n in names}])
        for rel, kind, lines, tokens, counts in rows:
            parts = rel.split("/")
            key = {"base": parts[0], "dir": "/".join(parts[:2]) if len(parts) > 2 else parts[0], "kind": kind}[a.sum]
            g = agg[key]
            g[0] += 1; g[1] += lines; g[2] += tokens
            for n in names:
                g[3][n] += counts[n]
        for key in sorted(agg):
            n_files, lines, tokens, counts = agg[key]
            write(key, str(n_files), lines, tokens, counts)
    else:
        for rel, kind, lines, tokens, counts in rows:
            write(rel, kind, lines, tokens, counts)
    for rel, kind, lines, tokens, counts in rows:
        tl += lines; tt += tokens
        for n in names:
            total[n] += counts[n]
    write("ИТОГО", str(len(rows)), tl, tt, total)
    if missing:
        print("файлов зоны нет на диске: %d" % missing, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
