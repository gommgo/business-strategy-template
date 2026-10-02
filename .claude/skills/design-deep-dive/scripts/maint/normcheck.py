#!/usr/bin/env python3
"""normcheck — сверка правки текста нормы: числа, id, пути, метки доказательности и заголовки md остались на месте.

Для того, кто принимает правку текстов базы `kb/`: формулировку можно чистить и сокращать, норму — нет. Утилита
сравнивает два состояния md-файла — базовый коммит (`--base`, по умолчанию `HEAD`) и рабочее дерево — по изменённым
кускам (`difflib` по строкам). В каждом куске слева и справа считаются мультимножества элементов:
  • число — целое или дробное (запятая или точка), диапазон (`6–12`, `1920×1080`), с единицей (`%`, `px`, `мс`, `с`,
    `КБ`, `МБ`, `×`, `rem`, `em` и другие); номер пункта нумерованного списка и номер заголовка числом не считаются;
  • id — `UX-A11-14`, `SG-PERF-03`, id реестров (`X12`, `X-12`, `C3`, `R7`, `В-4`), приметы `m12`, состояния `S07`,
    любое слово из букв с цифрой (`L2`, `p75`, `H1`) и цвет `#0A0A0A`;
  • код — содержимое код-спана в обратных кавычках (ключ, токен, имя файла);
  • путь — относительный путь, имя файла с расширением и URL вне код-спана;
  • адрес — короткий адрес «[база] NN/MM §N» и отсылка «§N»;
  • метка — метка доказательности по слову до двоеточия (`[проверено: …]` считается как `проверено`), `[V:…]` и
    `[S7]`; хвост метки после двоеточия разбирается как обычный текст.
Элемент, которого слева больше, — «потеряно» (строка — по базовой версии); которого справа больше — «появилось»
(строка — по рабочему дереву). Текст читается логическими строками — абзац, пункт списка, строка таблицы вместе с
переносами: метка, код-спан или адрес с переносом — один элемент. Заголовки сверяются по файлу целиком: уровень,
номер и текст каждого, порядок тот же. Файл, которого нет в рабочем дереве, — потеря; файл, которого нет в базовом
коммите, не сравнивается (списком в итоге).

Что считается чистой правкой:
  • `--strip ФАЙЛ` — регулярные выражения Python, по одному в строке (строка с «#» в начале — комментарий). Совпадение
    вырезается из обеих сторон до сравнения и расширяется до границ слова или пути; внутри код-спана — до всего спана;
    внутри хвоста метки — только в пределах хвоста, слово метки остаётся; в заголовке — ещё и до круглых скобок.
    Элемент из вырезанного может уйти или остаться — это не находка. Потеря рядом с вырезанным — на той же логической
    строке — идёт не в находки, а в список «потеряно на строке с вырезанным». Адрес нормы, появившийся на такой
    строке (вырезанное заменили адресом: короткий адрес, отсылка «§N» или путь в `kb/` — файл базы существует), —
    в список «появилось на строке с вырезанным». Списки читают выборкой: `--list-lost` печатает оба, без ключа —
    счёт. Появление числа, id, метки и прочего кода на такой строке остаётся находкой с пометкой;
  • `--allow ФАЙЛ` — TSV «файл · что · причина»: названное разрешено потерять или добавить. Файл — путь от корня
    репозитория или от `kb/`, допустим glob и `*`; что — элемент, как его печатает находка (`2,5 с`, `UX-A11-14`,
    `budgets.yaml`, `проверено`), `заголовок: текст` или `файл` (файл снят целиком); причина обязательна.
Всё прочее — находка `НОРМА` с файлом, строкой, элементом и строками «до» и «после»; элемент, который ушёл из одного
куска и пришёл в другой, — две находки с отсылкой друг на друга.

    python3 .claude/skills/design-deep-dive/scripts/maint/normcheck.py [--base REF] [ФАЙЛ.md | ПАПКА …]
                                [--files-from СПИСОК] [--strip ФАЙЛ] [--allow ФАЙЛ] [--json] [--list-lost]
    python3 .claude/skills/design-deep-dive/scripts/maint/normcheck.py --pair СТАРЫЙ НОВЫЙ [--strip ФАЙЛ] [--allow ФАЙЛ]
    python3 .claude/skills/design-deep-dive/scripts/maint/normcheck.py --selftest

Файлы — аргументами (файл или папка: все md папки), списком `--files-from` (путь на строку; в TSV путь — первая
колонка, строка-заголовок и строки с «#» пропускаются; не md — пропускаются) или без них — md базы `kb/`, изменённые
против базового коммита. Путь — от корня репозитория, от `kb/` (`kb` — вся база) или от рабочей папки. `--pair`
сравнивает два файла на диске без git. Репозиторий — тот, в котором лежит скилл (`scripts/lib/kbpaths.py`). Нужны git
и стандартная библиотека. Код выхода: 0 — находок нет; 1 — есть находки `НОРМА`; 2 — ошибка вызова (нет коммита,
файла, пути, ошибка регулярного выражения или строки разрешений).
"""
from __future__ import annotations

import argparse
import bisect
import contextlib
import difflib
import fnmatch
import glob
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import kbpaths  # noqa: E402

ROOT = kbpaths.repo()
KB_REL = kbpaths.kb().relative_to(ROOT).as_posix()       # .claude/skills/design-deep-dive/kb
RULE = "НОРМА"
WIDTH = 170                                              # длина строк «до» и «после» в выводе
PAIR_LIMIT = 900                                         # кусок крупнее (строк слева × справа) — без подбора пар строк
# Переменные, которыми вызывающий процесс направляет git в другой репозиторий: сверка их не наследует.
GIT_ENV_DROP = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
                "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE")
GIT_ENV: dict[str, str] = {}                             # добавка к окружению git: самопроверка снимает общие настройки
LIST_HEADER = ("file", "файл", "path", "путь")

# ─────────────────────────────── образцы элементов ───────────────────────────────

BASE_ALT = "|".join(sorted(map(re.escape, kbpaths.BASES + ("cd", "common")), key=len, reverse=True))
GAP = " \u00a0\u202f"                                  # пробел, неразрывный и узкий неразрывный
NUM = rf"(?:\d{{1,3}}(?:[{GAP}]\d{{3}})+(?!\d)|\d+)(?:[.,]\d+)*"
UNIT = "%|‰|°|px|rem|em|мс|с|КБ|МБ|ГБ|ms|s|KB|MB|GB|dvh|vh|vw|fps|мин|ч|×"
FILE_EXT = ("md|ya?ml|jsonl?|tsv|csv|py|js|mjs|cjs|tsx?|html|css|sh|txt|svg|png|webp|avif|jpe?g|gif|glb|blend|toml"
            "|mp4|webm|woff2?")

FENCE = re.compile(r"^\s*(?:```|~~~)")
HEAD = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
HEAD_NUM = re.compile(r"^(?:§\s*)?(\d+(?:\.\d+)*)\.?(?=\s|$)")
LIST_NUM = re.compile(r"^(\s*(?:>\s*)*)\d{1,3}[.)](?=\s)")   # номер пункта — до трёх цифр: «2025. » — число
BLOCK_START = re.compile(r"^\s*(?:[-*+]\s|\d{1,3}[.)]\s|#{1,6}\s|\||>)")
BLOCK_SOLO = re.compile(r"^\s*(?:#{1,6}\s|\|)")
CODE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
LABEL = re.compile(r"\[([а-яё]+(?:[ \n-][а-яё]+){0,4})\s*(?::\s*([^\[\]]*))?\](?!\()")
LABEL_V = re.compile(r"\[V:[^\]]*\]")
LABEL_S = re.compile(r"\[S\d+[A-Za-z0-9-]*\]")
ANY_LABEL = re.compile(f"{LABEL.pattern}|{LABEL_V.pattern}|{LABEL_S.pattern}")
URL = re.compile(r"https?://[^\s<>\"'`)\]]+")
ADDR = re.compile(rf"(?<![\w/.-])(?:({BASE_ALT})\s+)?(\d{{2}})/(\d{{2}}|README)(?![\w/])(?:\s*§\s*(\d+(?:\.\d+)*))?")
SECTION = re.compile(r"§\s*(\d+(?:\.\d+)*)")
PATH = re.compile(r"(?<![\w/.\-~$])(?:(?:\.{1,2}/)+|~/|\$[A-Z_]+/|/)?[A-Za-z0-9_][A-Za-z0-9_.\-*]*"
                  r"(?:/[A-Za-z0-9_.\-*<>{}]+)+/?")
FILE = re.compile(rf"(?<![\w/.\-])[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*\.(?:{FILE_EXT})(?!\w)")
TOKEN = re.compile(
    r"(?P<hex>(?<![\w&#])#[0-9A-Fa-f]{3,8}(?![\w-]))"
    r"|(?P<uid>(?<![\w-])[A-Z]{2,}(?:-[A-Z0-9]+)+(?![\w-]))"
    r"|(?P<rid>(?<![\w-])[XВ]-\d+(?![\w-]))"
    r"|(?P<tok>(?<!\w)[^\W\d_][^\W_]*\d\w*(?:\.\d+)*)"
    rf"|(?P<num>(?<!\w)[+±−]?{NUM}(?:[–—…×-][+±−]?{NUM})*)(?:[{GAP}\n]?(?P<unit>{UNIT})(?!\w))?"
    rf"|(?P<mul>×[{GAP}]?{NUM})"
)


class CallError(Exception):
    """Ошибка вызова или окружения (код выхода 2)."""


# ─────────────────────────────── элементы строки ───────────────────────────────

def extract(text: str, heading: bool = False) -> list[tuple[str, str, int, int]]:
    """Элементы норм логической строки: [(вид, значение, начало, конец)]. Взятое маскируется пробелами, чтобы число
    внутри id, пути или код-спана не считалось второй раз."""
    out: list[tuple[str, str, int, int]] = []
    s = text

    def take(rx: re.Pattern, fn):
        """fn(совпадение) → None (взято, замаскировать целиком) или (a, b) — какую часть совпадения оставить."""
        nonlocal s

        def rep(m):
            g = m.group(0)
            keep = fn(m)
            if keep is None:
                return " " * len(g)
            return " " * keep[0] + g[keep[0]:keep[1]] + " " * (len(g) - keep[1])
        s = rx.sub(rep, s)

    def item(kind: str, value: str, m: re.Match):
        out.append((kind, " ".join(value.split()), m.start(), m.end()))

    if heading:                                           # номер заголовка сверяется вместе с заголовками
        m = HEAD.match(s)
        n = HEAD_NUM.match(m.group(2)) if m else None
        if n:
            a = m.start(2)
            s = s[:a] + " " * n.end() + s[a + n.end():]
    else:
        s = LIST_NUM.sub(lambda m: " " * len(m.group(0)), s, count=1)

    def code(m):
        ticks, body = len(m.group(1)), m.group(2)
        if not body.strip():
            return None
        if ANY_LABEL.search(body):                        # метка в кавычках — метка: дальше читается как текст
            return ticks, len(m.group(0)) - ticks
        item("код", body, m)
        return None

    def label(m):
        item("метка", m.group(1), m)
        if m.group(2) is None:
            return None
        return m.start(2) - m.start(), m.end(2) - m.start()   # хвост метки остаётся текстом

    def path(m):
        g = m.group(0)
        if not re.search(r"[A-Za-z]", g):                 # «16/9» — числа, не путь
            return 0, len(g)
        item("путь", g.rstrip(".,;:"), m)
        return None

    take(CODE, code)
    take(LABEL_V, lambda m: item("метка", m.group(0), m))
    take(LABEL_S, lambda m: item("метка", m.group(0), m))
    take(LABEL, label)
    take(URL, lambda m: item("путь", m.group(0).rstrip(".,;:"), m))
    take(ADDR, lambda m: item("адрес", f"{m.group(1) + ' ' if m.group(1) else ''}{m.group(2)}/{m.group(3)}"
                                        f"{' §' + m.group(4) if m.group(4) else ''}", m))
    take(SECTION, lambda m: item("адрес", "§" + m.group(1), m))
    take(PATH, path)
    take(FILE, lambda m: item("путь", m.group(0), m))
    for m in TOKEN.finditer(s):
        if m.group("num"):
            body, unit = re.sub(f"[{GAP}]", "", m.group("num")), m.group("unit")
            item("число", body + ("×" if unit == "×" else f" {unit}" if unit else ""), m)
        elif m.group("mul"):
            item("число", re.sub(f"[{GAP}]", "", m.group("mul")), m)
        else:
            item("id", m.group(0), m)
    return out


def items(text: str, heading: bool = False) -> list[tuple[str, str]]:
    """Элементы без позиций: [(вид, значение)]."""
    return [(kind, value) for kind, value, _, _ in extract(text, heading)]


# ─────────────────────────────── вырезание ───────────────────────────────

def read_strip(path: str | None) -> list[re.Pattern]:
    """Регулярные выражения файла `--strip`: по одному в строке, пустые строки и строки с «#» в начале пропускаются."""
    if not path:
        return []
    p = Path(path)
    if not p.is_file():
        raise CallError(f"--strip: нет файла {path}")
    out = []
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            out.append(re.compile(line, re.M))       # «^» и «$» — границы строки файла
        except re.error as e:
            raise CallError(f"--strip: {path}:{n}: {e}") from e
    return out


def _token_char(ch: str) -> bool:
    return ch.isalnum() or ch in "_/.-~$*"


def cut_text(line: str, strips: list[re.Pattern]) -> tuple[str, str, list[tuple[int, int]]]:
    """Логическая строка без вырезанного: (узко, широко, вырезанные спаны). Узко — совпадение до границ слова или
    пути, внутри код-спана — весь спан, внутри хвоста метки — только в хвосте. Широко — ещё и до ближайших круглых
    скобок вокруг. Вырезанное заменяется пробелами той же длины."""
    hits = [m.span() for rx in strips for m in rx.finditer(line) if m.end() > m.start()]
    if not hits:
        return line, line, []
    tails = [(m.start(2), m.end(2)) for m in LABEL.finditer(line) if m.group(2) is not None]
    codes = [(m.start(), m.end()) for m in CODE.finditer(line) if not ANY_LABEL.search(m.group(2))]
    parens, stack = [], []
    for i, ch in enumerate(line):
        if ch == "(":
            stack.append(i)
        elif ch == ")" and stack:
            parens.append((stack.pop(), i + 1))
    core, wide, spans = list(line), list(line), []
    for a, b in hits:
        while a > 0 and _token_char(line[a - 1]):
            a -= 1
        while b < len(line) and _token_char(line[b]):
            b += 1
        in_tail = any(s <= a and b <= e for s, e in tails)
        if not in_tail:
            for s, e in codes:
                if s <= a and b <= e:
                    a, b = s, e
                    break
        core[a:b] = [ch if ch == "\n" else " " for ch in line[a:b]]
        spans.append((a, b))
        around = [] if in_tail else [(s, e) for s, e in parens if s <= a and b <= e]
        wa, wb = min(around, key=lambda x: x[1] - x[0]) if around else (a, b)
        wide[wa:wb] = [ch if ch == "\n" else " " for ch in line[wa:wb]]
    return "".join(core), "".join(wide), spans


def tidy(text: str) -> str:
    """Текст после вырезания: пробелы и осиротевшие знаки убраны — для сравнения заголовков."""
    s = " ".join(text.split())
    s = re.sub(r"([(\[«])\s+", r"\1", s)
    s = re.sub(r"\s+([)\]».,;:])", r"\1", s)
    s = re.sub(r"\(\s*[,;·—–-]*\s*\)|\[\s*\]|«\s*»|`\s*`", "", s)
    return " ".join(s.split()).strip(" ·—–-,;:").rstrip(".")


# ─────────────────────────────── строки файла ───────────────────────────────

def block_ids(lines: list[str]) -> list[int]:
    """Номер логической строки для каждой строки файла: абзац, пункт списка, строка таблицы — вместе с переносами."""
    ids, cur, fence, solo = [], 0, False, True
    for line in lines:
        is_fence = bool(FENCE.match(line))
        blank = not line.strip()
        if is_fence or fence or blank or solo or BLOCK_START.match(line):
            cur += 1
        ids.append(cur)
        if is_fence:
            fence = not fence
        solo = is_fence or fence or blank or bool(BLOCK_SOLO.match(line))
    return ids


def headings(lines: list[str], strips: list[re.Pattern]) -> list[dict]:
    """Заголовки файла вне блоков кода: {line, level, num, core, wide, raw} — текст после вырезания, узко и широко."""
    out, fence = [], False
    for n, line in enumerate(lines, 1):
        if FENCE.match(line):
            fence = not fence
            continue
        m = None if fence else HEAD.match(line)
        if not m:
            continue
        title = m.group(2)
        num = HEAD_NUM.match(title)
        core, wide = (LABEL.sub(lambda x: f"[{x.group(1)}]", t)          # хвост метки сверяется элементами строки
                      for t in cut_text(title[num.end():] if num else title, strips)[:2])
        out.append({"line": n, "level": len(m.group(1)), "num": num.group(1) if num else "", "core": tidy(core),
                    "wide": tidy(wide), "raw": " ".join(title.split())})
    return out


def scan(lines: list[str], strips: list[re.Pattern], wanted: set[int]) -> dict[int, tuple[list, Counter, bool, list]]:
    """Строки файла из набора wanted → {строка: (элементы вне вырезанного, элементы внутри вырезанного, было ли
    вырезание, элементы с переносом, начатые выше)}. Разбор идёт по логическим строкам: метка, код-спан и адрес с
    переносом читаются целиком и относятся к строке файла, на которой начинаются; последний список называет их
    и на строках продолжения — [(вид, значение, строка начала)]."""
    ids = block_ids(lines)
    heads = {h["line"] - 1 for h in headings(lines, [])}
    out: dict[int, tuple[list, Counter, bool, list]] = {}
    for i in sorted(wanted):
        if i in out:
            continue
        lo = hi = i
        while lo > 0 and ids[lo - 1] == ids[i]:
            lo -= 1
        while hi + 1 < len(lines) and ids[hi + 1] == ids[i]:
            hi += 1
        parts = [lines[lo]] + [x.lstrip() for x in lines[lo + 1:hi + 1]]
        starts = [0]
        for part in parts[:-1]:
            starts.append(starts[-1] + len(part) + 1)
        text = "\n".join(parts)
        core, _, spans = cut_text(text, strips)

        def line_of(pos: int) -> int:
            return lo + bisect.bisect_right(starts, pos) - 1

        kept: dict[int, list] = {k: [] for k in range(lo, hi + 1)}
        inside: dict[int, Counter] = {k: Counter() for k in range(lo, hi + 1)}
        above: dict[int, list] = {k: [] for k in range(lo, hi + 1)}
        for kind, value, start, end in extract(core, lo in heads):
            first = line_of(start)
            kept[first].append((kind, value))
            for k in range(first + 1, line_of(end - 1) + 1):
                above[k].append((kind, value, first))
        if spans:
            for kind, value, start, _ in extract(text, lo in heads):
                inside[line_of(start)][(kind, value)] += 1
        hit = {k for a, b in spans for k in range(line_of(a), line_of(b - 1) + 1)}
        for k in range(lo, hi + 1):
            out[k] = kept[k], (inside[k] - Counter(kept[k])) if spans else inside[k], k in hit, above[k]
    return out


def clip(line: str, start: int = 0) -> str:
    """Строка для вывода: пробелы сжаты, окно WIDTH знаков с позиции start."""
    s = " ".join(line.split())
    start = min(start, max(0, len(s) - WIDTH))
    return ("…" if start else "") + s[start:start + WIDTH] + ("…" if len(s) > start + WIDTH else "")


def window(line: str, value: str) -> int:
    """Начало окна вывода, в которое попадает элемент длинной строки."""
    at = " ".join(line.split()).find(value)
    return 0 if at + len(value) <= WIDTH - 10 else max(0, at - WIDTH // 2)


def pair_lines(old: list[str], new: list[str]) -> dict[int, int]:
    """Пары «строка слева → строка справа» внутри куска: поровну строк — по порядку, иначе — по сходству текста."""
    if len(old) == len(new):
        return {i: i for i in range(len(old))}
    if not old or not new or len(old) * len(new) > PAIR_LIMIT:
        return {}
    pairs, used = {}, set()
    sm = difflib.SequenceMatcher(None, autojunk=False)
    for i, a in enumerate(old):
        sm.set_seq2(a)
        best, at = 0.6, None
        for j, b in enumerate(new):
            if j in used:
                continue
            sm.set_seq1(b)
            if sm.real_quick_ratio() > best and sm.quick_ratio() > best:
                r = sm.ratio()
                if r > best:
                    best, at = r, j
        if at is not None:
            pairs[i] = at
            used.add(at)
    return pairs


# ─────────────────────────────── разрешения ───────────────────────────────

class Allow:
    """Строки `--allow`: {file, what, reason}; `permits` отмечает сработавшие строки."""

    def __init__(self, path: str | None = None):
        self.rows: list[dict] = []
        if not path:
            return
        p = Path(path)
        if not p.is_file():
            raise CallError(f"--allow: нет файла {path}")
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            cols = [c.strip() for c in line.split("\t")]
            if not self.rows and cols[0].lower() in LIST_HEADER:
                continue
            if len(cols) < 3 or not all(cols[:3]):
                raise CallError(f"--allow: {path}:{n}: нужны три колонки через табуляцию — файл, что, причина")
            f = cols[0].strip("`").replace("\\", "/")
            self.rows.append({"file": f[2:] if f.startswith("./") else f, "what": " ".join(cols[1].split()),
                              "reason": cols[2], "line": n, "used": 0})

    @staticmethod
    def _file(rel: str, mask: str) -> bool:
        names = {rel, rel[len(KB_REL) + 1:] if rel.startswith(KB_REL + "/") else rel}
        names |= {"kb/" + x for x in names}
        return mask == "*" or any(x == mask or fnmatch.fnmatchcase(x, mask) for x in names)

    def permits(self, rel: str, forms: set[str]) -> bool:
        hit = False
        for r in self.rows:
            if r["what"] in forms and self._file(rel, r["file"]):
                r["used"] += 1
                hit = True
        return hit

    def unused(self) -> list[dict]:
        return [{k: r[k] for k in ("file", "what", "line")} for r in self.rows if not r["used"]]


def item_forms(kind: str, value: str) -> set[str]:
    """Как элемент может быть назван в строке разрешений."""
    forms = {value}
    if kind == "код":
        forms.add(f"`{value}`")
    elif kind == "метка":
        forms |= {f"[{value}]", value.strip("[]")}
    return forms


def heading_forms(h: dict) -> set[str]:
    texts = {h["raw"], h["core"], h["wide"], f"{h['num']}. {h['core']}" if h["num"] else h["core"]}
    return {f"заголовок: {t}" for t in texts if t} | {f"заголовок:{t}" for t in texts if t}


# ─────────────────────────────── сравнение файла ───────────────────────────────

def finding(path: str, line: int, kind: str, category: str, value: str, before: str, after: str, note: str = "",
            stripped: bool = False) -> dict:
    start = window(after if kind == "появилось" else before, value)
    return {"rule": RULE, "path": path, "line": line, "kind": kind, "category": category, "item": value,
            "before": clip(before, start), "after": clip(after, start), "note": note, "stripped": stripped}


_KB_NAMES: dict[Path, set[str]] = {}


def norm_address(kind: str, value: str, root: Path | None, rel: str) -> bool:
    """Элемент — адрес нормы: короткий адрес или отсылка «§N» либо путь (и в код-спане), который ведёт в `kb/`:
    от папки файла, от папки его базы, от `kb/`, от корня скилла или репозитория; имя без папки — файл базы."""
    if kind == "адрес":
        return True
    if kind not in ("путь", "код") or root is None:
        return False
    tok = (value.split() or [""])[0].split("#")[0].rstrip(".,;:")
    if not tok or tok.startswith(("-", "http", "$", "~", "/")) or re.search(r"[<>{}…=()|\"']", tok):
        return False
    kb = root / KB_REL
    inside = rel[len(KB_REL) + 1:] if rel.startswith(KB_REL + "/") else ""
    bases = [(root / rel).parent] + ([kb / inside.split("/")[0]] if "/" in inside else []) + [kb, kb.parent, root]
    for base in bases:
        target = os.path.normpath(base / (tok[3:] if base == kb and tok.startswith("kb/") else tok))
        found = glob.glob(target) if re.search(r"[*?]", tok) else [target] if os.path.exists(target) else []
        if any(x == str(kb) or x.startswith(str(kb) + os.sep) for x in found):
            return True
    if "/" in tok.rstrip("/") or not FILE.fullmatch(tok):
        return False
    if kb not in _KB_NAMES:
        _KB_NAMES[kb] = {f for _, _, files in os.walk(kb) for f in files}
    return tok in _KB_NAMES[kb]


def compare_headings(rel: str, a: list[str], b: list[str], strips, allow: Allow) -> tuple[list[dict], int]:
    """Заголовки файла целиком: уровень, номер, текст и порядок. → (находки, разрешено)."""
    old, new = headings(a, strips), headings(b, strips)

    def same(o, n):
        return (o["level"], o["num"]) == (n["level"], n["num"]) and (o["core"] == n["core"] or o["wide"] == n["wide"]
                                                                        or o["wide"] == n["core"])

    def key(h):
        return h["level"], h["num"], h["wide"]

    out, allowed = [], 0

    def add(kind, h_old, h_new, note=""):
        nonlocal allowed
        forms = set().union(*(heading_forms(h) for h in (h_old, h_new) if h))
        if allow.permits(rel, forms):
            allowed += 1
            return
        h = h_old or h_new
        out.append(finding(rel, h["line"], kind, "заголовок", h["raw"],
                           "#" * h_old["level"] + " " + h_old["raw"] if h_old else "",
                           "#" * h_new["level"] + " " + h_new["raw"] if h_new else "", note))

    if len(old) == len(new) and all(same(o, n) for o, n in zip(old, new)):
        return out, allowed
    sm = difflib.SequenceMatcher(None, [key(h) for h in old], [key(h) for h in new], autojunk=False)
    gone, come = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        n = min(i2 - i1, j2 - j1)
        for o, h in zip(old[i1:i1 + n], new[j1:j1 + n]):
            if same(o, h):
                continue
            text = o["core"] == h["core"] or o["wide"] == h["wide"]
            if text and o["level"] == h["level"]:
                add("изменено", o, h, f"номер раздела: «{o['num'] or '—'}» → «{h['num'] or '—'}»")
            elif text and o["num"] == h["num"]:
                add("изменено", o, h, f"уровень заголовка: {o['level']} → {h['level']}")
            elif (o["level"], o["num"]) == (h["level"], h["num"]):
                add("изменено", o, h, "текст заголовка")
            else:
                gone.append(o)
                come.append(h)
        gone += old[i1 + n:i2]
        come += new[j1 + n:j2]
    moved = {key(h) for h in gone} & {key(h) for h in come}
    for h in gone:
        add("потеряно", h, None, "заголовок переставлен" if key(h) in moved else "заголовок снят")
    for h in come:
        add("появилось", None, h, "заголовок переставлен" if key(h) in moved else "заголовка не было")
    return out, allowed


def compare(rel: str, old: str, new: str, strips: list[re.Pattern], allow: Allow, root: Path | None = None) -> dict:
    """Два состояния текста → {findings, soft, fresh, allowed}: находки, потери и появившиеся адреса норм на строках
    с вырезанным, число разрешённых. root — репозиторий: по нему путь сверяется с файлами `kb/`."""
    a, b = old.split("\n"), new.split("\n")
    findings, allowed = compare_headings(rel, a, b, strips, allow)
    soft: list[dict] = []
    fresh: list[dict] = []
    blocks, blocks_new = block_ids(a), block_ids(b)
    chunks = [op[1:] for op in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if op[0] != "equal"]
    was = scan(a, strips, {i for i1, i2, _, _ in chunks for i in range(i1, min(i2 + 1, len(a)))})
    now = scan(b, strips, {j for _, _, j1, j2 in chunks for j in range(j1, min(j2 + 1, len(b)))})

    for i1, i2, j1, j2 in chunks:
        soft_blocks = {blocks[i] for i in range(i1, i2) if was[i][2]}
        occ = [[k, i, blocks[i] in soft_blocks, False] for i in range(i1, i2) for k in was[i][0]]
        if i1 < len(a):                                   # элемент с переносом начат выше куска и задет им
            occ += [[(kind, value), i, blocks[i] in soft_blocks, False] for kind, value, i in was[i1][3]]
        optional = sum((was[i][1] for i in range(i1, i2)), Counter())
        right = {j: Counter(now[j][0]) for j in range(j1, j2)}
        if j1 < len(b) and now[j1][3]:
            right.setdefault(j1, Counter()).update((kind, value) for kind, value, _ in now[j1][3])
        pairs = pair_lines(a[i1:i2], b[j1:j2])
        back = {j: i for i, j in pairs.items()}
        # логические строки справа, которым слева отвечает строка с вырезанным (или вырезание сработало в них самих)
        marked = {blocks_new[j1 + j] for i, j in pairs.items() if blocks[i1 + i] in soft_blocks}
        marked |= {blocks_new[j] for j in range(j1, j2) if now[j][2]}
        if soft_blocks and all(blocks[i] in soft_blocks for i in range(i1, i2) if a[i].strip()):
            marked |= {blocks_new[j] for j in right}      # слева в куске — только строки с вырезанным
        for o in occ:                                     # сначала — в паре строк
            j = pairs.get(o[1] - i1)
            if j is not None and right[j1 + j][o[0]] > 0:
                right[j1 + j][o[0]] -= 1
                o[3] = True
        rest = sum(right.values(), Counter())
        for o in sorted((o for o in occ if not o[3]), key=lambda o: (not o[2], o[1])):   # затем — по куску целиком
            if rest[o[0]] > 0:
                rest[o[0]] -= 1
                o[3] = True
        for k in list(rest):                              # оставшееся из вырезанного — не новое
            rest[k] -= min(rest[k], optional[k])

        def old_line(j):
            i = back.get(j - j1)
            return a[i1 + i] if i is not None else (a[i1] if i2 > i1 else "")

        def new_line(i):
            j = pairs.get(i - i1)
            return b[j1 + j] if j is not None else (b[j1] if j2 > j1 else "")

        for (kind, value), i, is_soft, matched in occ:
            if matched:
                continue
            if is_soft:
                soft.append({"path": rel, "line": i + 1, "category": kind, "item": value, "before": clip(a[i])})
            elif allow.permits(rel, item_forms(kind, value)):
                allowed += 1
            else:
                findings.append(finding(rel, i + 1, "потеряно", kind, value, a[i], new_line(i)))
        for j in sorted(right):
            mark = blocks_new[j] in marked
            for (kind, value), c in right[j].items():
                for _ in range(min(c, rest[(kind, value)])):
                    rest[(kind, value)] -= 1
                    if mark and norm_address(kind, value, root, rel):   # маркер заменили адресом нормы
                        fresh.append({"path": rel, "line": j + 1, "category": kind, "item": value,
                                      "after": clip(b[j])})
                    elif allow.permits(rel, item_forms(kind, value)):
                        allowed += 1
                    else:
                        findings.append(finding(rel, j + 1, "появилось", kind, value, old_line(j), b[j],
                                                "на строке с вырезанным" if mark else "", mark))

    where = {}
    for f in findings:                                    # тот же элемент ушёл в одном куске и пришёл в другом
        if f["category"] != "заголовок":
            where.setdefault((f["category"], f["item"], f["kind"]), f["line"])
    for f in findings:
        other = where.get((f["category"], f["item"], "появилось" if f["kind"] == "потеряно" else "потеряно"))
        if other and f["category"] != "заголовок" and f["kind"] in ("потеряно", "появилось"):
            word = "появился" if f["kind"] == "потеряно" else "потерян"
            f["note"] = "; ".join(x for x in (f["note"], f"такой же элемент {word} на строке {other}") if x)
    findings.sort(key=lambda f: (f["line"], f["kind"]))
    return {"findings": findings, "soft": soft, "fresh": fresh, "allowed": allowed}


# ─────────────────────────────── git и список файлов ───────────────────────────────

def git(root: Path, *args: str, ok: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
    """git в репозитории root без попутной записи индекса; вывод — байтами; код не из ok — ошибка вызова."""
    env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}
    env.update(GIT_ENV, GIT_LITERAL_PATHSPECS="1", GIT_OPTIONAL_LOCKS="0")
    try:
        r = subprocess.run(["git", "-C", str(root), "-c", "core.quotepath=off", *args], env=env, capture_output=True)
    except OSError as e:
        raise CallError(f"git не запускается: {e}") from e
    if r.returncode not in ok:
        tail = (r.stderr.decode("utf-8", "replace").strip().splitlines() or [f"код {r.returncode}"])[-1]
        raise CallError(f"git {args[0]}: {tail}")
    return r


def base_files(root: Path, base: str) -> set[str]:
    """Пути файлов базового коммита от корня репозитория."""
    if not base or base.startswith("-"):
        raise CallError(f"--base: «{base}» — не имя коммита")
    r = git(root, "rev-parse", "--is-inside-work-tree", ok=(0, 128))
    if r.returncode or r.stdout.strip() != b"true":
        raise CallError(f"{root}: не рабочее дерево репозитория git")
    if git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", ok=(0, 1, 128)).returncode:
        raise CallError(f"--base: нет коммита «{base}»")
    out = git(root, "ls-tree", "-r", "--name-only", "-z", "--full-tree", base).stdout.decode("utf-8", "replace")
    return {p for p in out.split("\0") if p}


def read_list(path: str) -> list[str]:
    """Пути списка `--files-from`: первая колонка строки; строка-заголовок, пустые строки и строки с «#» — мимо."""
    p = Path(path)
    if not p.is_file():
        raise CallError(f"--files-from: нет файла {path}")
    out, first = [], True
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cell = line.split("\t")[0].strip().strip("`")
        if first and cell.lower() in LIST_HEADER:
            first = False
            continue
        first = False
        if cell:
            out.append(cell)
    return out


def md_under(root: Path, folder: str, tracked: set[str]) -> list[str]:
    """md папки: из базового коммита и с диска."""
    found = {p for p in tracked if p.startswith(folder + "/") and p.endswith(".md")}
    for cur, dirs, files in os.walk(root / folder):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        found |= {(Path(cur) / f).relative_to(root).as_posix() for f in files if f.endswith(".md")}
    return sorted(found)


def resolve(root: Path, raw: str, tracked: set[str]) -> tuple[list[str], int]:
    """Путь вызова или списка → (md от корня репозитория, сколько не md пропущено). Путь — от корня репозитория,
    от `kb/` или от рабочей папки; файл может быть только в базовом коммите."""
    p = raw.strip().strip("`").replace("\\", "/")
    if Path(p).is_absolute():
        try:
            cands = [Path(p).resolve().relative_to(root).as_posix()]
        except ValueError as e:
            raise CallError(f"{raw}: путь вне репозитория {root}") from e
    else:
        p = (p[2:] if p.startswith("./") else p).rstrip("/")
        if not p:
            raise CallError(f"«{raw}»: назовите файл или папку")
        cands = [p, f"{KB_REL}/{p[3:]}" if p.startswith("kb/") else KB_REL if p == "kb" else f"{KB_REL}/{p}"]
        with contextlib.suppress(ValueError):
            cands.append((Path.cwd() / p).resolve().relative_to(root).as_posix())
    for c in cands:
        if (root / c).is_file() or c in tracked:
            return ([c], 0) if c.endswith(".md") else ([], 1)
        if (root / c).is_dir() or any(t.startswith(c + "/") for t in tracked):
            return md_under(root, c, tracked), 0
    raise CallError(f"{raw}: нет такого файла или папки ни в рабочем дереве, ни в базовом коммите")


def changed_md(root: Path, base: str) -> list[str]:
    """md базы `kb/`, изменённые против базового коммита (вместе с удалёнными)."""
    out = git(root, "diff", "--name-only", "-z", "--no-renames", base, "--", KB_REL).stdout.decode("utf-8", "replace")
    return sorted(p for p in out.split("\0") if p.endswith(".md"))


def old_text(root: Path, base: str, rel: str, tracked: set[str]) -> str | None:
    if rel not in tracked:
        return None
    return git(root, "cat-file", "blob", f"{base}:{rel}").stdout.decode("utf-8", "replace")


# ─────────────────────────────── сверка ───────────────────────────────

def report(base: str, repo: str) -> dict:
    return {"base": base, "repo": repo, "files": 0, "changed": 0, "new_files": [], "skipped": 0, "findings": [],
            "lost_on_stripped": [], "new_on_stripped": [], "allowed": 0, "allow_unused": [], "clean": True}


def add_file(rep: dict, rel: str, old: str | None, new: str | None, strips, allow: Allow, root: Path | None = None):
    rep["files"] += 1
    if old is None:
        rep["new_files"].append(rel)
        return
    if new is None:
        rep["changed"] += 1
        if allow.permits(rel, {"файл"}):
            rep["allowed"] += 1
        else:
            rep["findings"].append(finding(rel, 0, "потеряно", "файл", rel, "", "", "файла нет в рабочем дереве"))
        return
    if old == new:
        return
    rep["changed"] += 1
    res = compare(rel, old, new, strips, allow, root)
    rep["findings"] += res["findings"]
    rep["lost_on_stripped"] += res["soft"]
    rep["new_on_stripped"] += res["fresh"]
    rep["allowed"] += res["allowed"]


def check(root: Path, base: str, paths: list[str], lists: list[str], strips, allow: Allow) -> dict:
    """Сверка файлов рабочего дерева с базовым коммитом → отчёт."""
    tracked = base_files(root, base)
    rep = report(base, str(root))
    if paths or lists:
        files: list[str] = []
        for p in list(paths) + [x for f in lists for x in read_list(f)]:
            got, skipped = resolve(root, p, tracked)
            rep["skipped"] += skipped
            files += [f for f in got if f not in files]
    else:
        files = changed_md(root, base)
    for rel in files:
        disk = root / rel
        new = disk.read_bytes().decode("utf-8", "replace") if disk.is_file() else None
        add_file(rep, rel, old_text(root, base, rel, tracked), new, strips, allow, root)
    return finish(rep, allow)


def check_pair(old: str, new: str, strips, allow: Allow, root: Path = ROOT) -> dict:
    """Сверка двух файлов на диске без git; root — репозиторий, по которому путь сверяется с файлами `kb/`."""
    for p in (old, new):
        if not Path(p).is_file():
            raise CallError(f"--pair: нет файла {p}")
    rep = report(f"файл {old}", "")
    add_file(rep, str(new), Path(old).read_bytes().decode("utf-8", "replace"),
             Path(new).read_bytes().decode("utf-8", "replace"), strips, allow, root)
    return finish(rep, allow)


def finish(rep: dict, allow: Allow) -> dict:
    rep["allow_unused"] = allow.unused()
    rep["clean"] = not rep["findings"]
    return rep


def render(rep: dict, list_lost: bool) -> str:
    out = [f"== сверка правки текста нормы: база {rep['base']}; файлов {rep['files']}, с правкой {rep['changed']}"]
    for f in rep["findings"]:
        where = f"{f['path']}:{f['line']}" if f["line"] else f["path"]
        note = f" ({f['note']})" if f["note"] else ""
        out.append(f"{RULE}  {where}  {f['kind']}: {f['category']} «{f['item']}»{note}")
        if f["category"] != "файл":
            out.append(f"    до:    {f['before'] or '—'}")
            out.append(f"    после: {f['after'] or '—'}")
    soft = rep["lost_on_stripped"]
    fresh = rep["new_on_stripped"]
    if list_lost and soft:
        out.append(f"== потеряно на строке с вырезанным ({len(soft)})")
        out += [f"  {s['path']}:{s['line']}  {s['category']} «{s['item']}»  | {s['before']}" for s in soft]
    if list_lost and fresh:
        out.append(f"== появилось на строке с вырезанным ({len(fresh)})")
        out += [f"  {s['path']}:{s['line']}  {s['category']} «{s['item']}»  | {s['after']}" for s in fresh]
    if rep["new_files"]:
        out.append(f"== нет в базовом коммите, не сравнивались ({len(rep['new_files'])})")
        out += [f"  {p}" for p in rep["new_files"]]
    if rep["allow_unused"]:
        out.append(f"== строки разрешений без совпадений ({len(rep['allow_unused'])})")
        out += [f"  строка {r['line']}: {r['file']} · {r['what']}" for r in rep["allow_unused"]]
    kinds = Counter(f["kind"] for f in rep["findings"])
    hint = "" if list_lost or not (soft or fresh) else " (списки — --list-lost)"
    tail = [f"на строках с вырезанным: потеряно — {len(soft)}, адресов появилось — {len(fresh)}{hint}",
            f"разрешено — {rep['allowed']}"]
    if rep["skipped"]:
        tail.append(f"не md, пропущено — {rep['skipped']}")
    if rep["clean"]:
        head = "ИТОГ: находок нет"
    else:
        head = (f"ИТОГ: находок {RULE} — {len(rep['findings'])} (потеряно {kinds['потеряно']}, "
                f"появилось {kinds['появилось']}, изменено {kinds['изменено']})")
    out.append("; ".join([head] + tail))
    return "\n".join(out)


# ─────────────────────────────── самопроверка ───────────────────────────────

def selftest() -> int:
    """Разбор строк на образцах и временный репозиторий git: чистая правка проходит, каждую посеянную потерю и
    каждое появление ловит сверка, разрешение снимает находку."""
    ok = fail = 0

    def ok_if(name, cond):
        nonlocal ok, fail
        print(("OK   " if cond else "FAIL ") + name)
        ok, fail = ok + bool(cond), fail + (not cond)

    def quiet(argv, root):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = main(argv, root)
        return rc, out.getvalue(), err.getvalue()

    def has(line, *want):
        got = items(line)
        return all(w in got for w in want)

    ok_if("число: дробное с единицей, разряды, диапазон, множитель, процент",
          has("LCP ≤ 2,5 с, вес 1 916 КБ, 6–12 месяцев, CPU×4, 77 %, 1920×1080, 0.3s",
              ("число", "2,5 с"), ("число", "1916 КБ"), ("число", "6–12"), ("число", "×4"), ("число", "77 %"),
              ("число", "1920×1080"), ("число", "0.3 s")))
    ok_if("число: номер пункта списка и номер заголовка не считаются",
          items("12. Текст 3 раза") == [("число", "3")] and items("## 2.1. Порог 4 с", True) == [("число", "4 с")]
          and items("2025. Затем") == [("число", "2025")])
    ok_if("id: реестры, приметы, состояния, уровни, цвет",
          has("UX-A11-14, SG-PERF-03, X12, X-7, В-4, m12, S07, L2 и p75, цвет #0A0A0A",
              ("id", "UX-A11-14"), ("id", "SG-PERF-03"), ("id", "X12"), ("id", "X-7"), ("id", "В-4"), ("id", "m12"),
              ("id", "S07"), ("id", "L2"), ("id", "p75"), ("id", "#0A0A0A")))
    ok_if("код, путь, адрес: число внутри них отдельно не считается",
          sorted(items("см. `budgets.yaml`, kb/site/07-x/03-y.md, site 07/03 §4 и → §1.1"))
          == [("адрес", "site 07/03 §4"), ("адрес", "§1.1"), ("код", "budgets.yaml"), ("путь", "kb/site/07-x/03-y.md")])
    ok_if("метка: слово до двоеточия, хвост — текстом; метка в кавычках, [S7] и [V:…]",
          sorted(items("`[проверено: стенд 153]` [не проверено] [S7] [V:abc 05:20] [ссылка](x.md)"))
          == [("метка", "[S7]"), ("метка", "[V:abc 05:20]"), ("метка", "не проверено"), ("метка", "проверено"),
              ("путь", "x.md"), ("число", "153")])
    rx = [re.compile(r"old-lab"), re.compile(r"(?<![\w/.:-])[A-Z]/\d{2}(?![\w/])")]
    ok_if("вырезание: путь целиком, код-спан целиком, хвост метки — только хвост, заголовок — до скобок",
          cut_text("см. ../old-lab/run/07 и 5 мс", rx)[0].split() == ["см.", "и", "5", "мс"]
          and cut_text("файл `old-lab/a.md` (3 шт.)", rx)[0].split() == ["файл", "(3", "шт.)"]
          and items(cut_text("норма `[проверено: P/02]`", rx)[0]) == [("метка", "проверено")]
          and tidy(cut_text("Сверка (стенд P/03, 4 прогона)", rx)[1]) == "Сверка"
          and cut_text("чисто", rx) == ("чисто", "чисто", []))
    wrapped = scan(["- порог 200", "  мс `[проверено: P/02,", "  P/03]` и site", "  07/03 §4", "", "хвост 5"], rx, {1})
    ok_if("перенос: метка, единица и адрес читаются через перенос и относятся к строке начала",
          wrapped[0][0] == [("число", "200 мс")] and wrapped[1][0] == [("метка", "проверено")]
          and wrapped[2][0] == [("адрес", "site 07/03 §4")] and wrapped[1][2] and wrapped[2][2] and not wrapped[0][2]
          and wrapped[3][3] == [("адрес", "site 07/03 §4", 2)] and sorted(wrapped) == [0, 1, 2, 3])
    res = compare("x.md", "вызов `tool --a\n--b 5` и текст\n", "вызов `tool --a\n--b 6` и текст\n", [], Allow())
    ok_if("перенос: правка второй строки код-спана — потеря и появление спана целиком",
          sorted((f["kind"], f["item"]) for f in res["findings"])
          == [("потеряно", "tool --a --b 5"), ("появилось", "tool --a --b 6")])
    ok_if("логическая строка: абзац и пункт списка с переносами — одна, строка таблицы и заголовок — свои",
          block_ids(["# З", "абзац", "перенос", "", "- пункт", "  перенос", "- пункт", "| a |", "| b |"])
          == [1, 2, 2, 3, 4, 4, 5, 6, 7])

    doc = "\n".join([
        "# Скорость и бюджет страницы",
        "",
        "Черновик 2 · агент P · прочитано 24 источника (обзоры ×14) ·",
        "артефакты: `budgets.yaml`.",
        "",
        "## 1. Метрики",
        "",
        "1. Цель поля: LCP ≤ 2,5 с, INP ≤ 200 мс → §1.1 `[проверено: P/02]` `[документация]`.",
        "2. Профиль SG-PERF-03 держит 300 КБ скрипта; правило UX-A11-14 — без изменений [S7].",
        "3. Уровень L2: первый экран ≤ 2,0 МБ, сессия 5 МБ → site 07/03 §4 [практика].",
        "",
        "## 2. Ворота",
        "",
        "Порог блокировки — 4 с; медиана 3 прогонов.",
        "",
        "Сверка порогов — агент P §4.",
        "",
        "### 2.1. Порядок (стенд P/03)",
        "",
        "Текст раздела со ссылкой на `page-gates.yaml`.",
        "",
        "## 3. Источники",
        "",
        "- [S7] Обзор весов страниц.",
        "",
    ])
    clean = (doc.replace("Черновик 2 · агент P · прочитано 24 источника (обзоры ×14) ·\n", "")
             .replace("артефакты: `budgets.yaml`.\n\n", "")
             .replace("`[проверено: P/02]`", "`[проверено]`")
             .replace("Профиль SG-PERF-03 держит 300 КБ скрипта; правило UX-A11-14 — без изменений [S7].",
                      "Правило UX-A11-14 — без изменений, профиль SG-PERF-03 держит 300 КБ скрипта [S7].")
             .replace("Сверка порогов — агент P §4.", "Сверка порогов — site 07/04 §4.")
             .replace("### 2.1. Порядок (стенд P/03)", "### 2.1. Порядок"))
    git_env = dict(GIT_ENV)
    GIT_ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="selftest",
                   GIT_AUTHOR_EMAIL="selftest@example.invalid", GIT_COMMITTER_NAME="selftest",
                   GIT_COMMITTER_EMAIL="selftest@example.invalid")
    try:
        with tempfile.TemporaryDirectory(prefix="normcheck-") as td:
            repo = Path(td).resolve() / "repo"
            name = f"{KB_REL}/site/07-speed/03-gates.md"
            other = f"{KB_REL}/site/07-speed/04-other.md"
            for rel, text in ((name, doc), (other, "# Другой\n\nПорог 7 с.\n"), (f"{KB_REL}/site/data.yaml", "a: 1\n")):
                (repo / rel).parent.mkdir(parents=True, exist_ok=True)
                (repo / rel).write_text(text, encoding="utf-8")
            GIT_ENV["GIT_CEILING_DIRECTORIES"] = str(repo.parent.parent)   # выше временной папки git не ищет
            git(repo, "init", "-q")
            git(repo, "add", "-A")
            git(repo, "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + os.devnull, "commit", "-q", "-m", "base")
            strip = Path(td) / "strip.txt"
            strip.write_text("# буква исполнителя и адрес стенда\nагент\\w{0,3}\\s+[A-Z]\\b\n\n"
                             "(?<![\\w/.:-])[A-Z]/\\d{2}(?![\\w/])\n", encoding="utf-8")
            strips = read_strip(str(strip))

            def run(text, allow=None, use_strip=True):
                (repo / name).write_text(text, encoding="utf-8")
                return check(repo, "HEAD", [name], [], strips if use_strip else [], Allow(allow))

            def seen(rep):
                return sorted((f["kind"], f["category"], f["item"]) for f in rep["findings"])

            rep = run(doc)
            ok_if("без правок: находок нет", rep["clean"] and rep["changed"] == 0 and rep["files"] == 1)
            rep = run(clean)
            ok_if("чистая правка с --strip: буква исполнителя, хвост метки и скобка заголовка убраны, слова "
                  "переставлены — находок нет", rep["clean"] and rep["changed"] == 1)
            ok_if("чистая правка: потери шапки — в списке «на строке с вырезанным», вырезанное — молча",
                  sorted((s["category"], s["item"]) for s in rep["lost_on_stripped"])
                  == [("адрес", "§4"), ("код", "budgets.yaml"), ("число", "2"), ("число", "24"), ("число", "×14")])
            ok_if("адрес нормы на месте вырезанного — в списке «появилось на строке с вырезанным», не находкой",
                  [(s["category"], s["item"], s["line"]) for s in rep["new_on_stripped"]]
                  == [("адрес", "site 07/04 §4", 13)])
            rep = run(clean.replace("— site 07/04 §4.", "— `04-other.md` §4, см. `tool.py`."))
            ok_if("путь в kb/ на месте вырезанного — в списке; код-спан не из kb/ там же — находка с пометкой",
                  [(s["category"], s["item"]) for s in rep["new_on_stripped"]] == [("код", "04-other.md")]
                  and seen(rep) == [("появилось", "код", "tool.py")] and rep["findings"][0]["stripped"])
            rep = run(clean.replace("медиана 3 прогонов.", "медиана 3 прогонов → site 07/04 §2."))
            ok_if("адрес нормы появился на строке без вырезанного — находка",
                  seen(rep) == [("появилось", "адрес", "site 07/04 §2")] and not rep["findings"][0]["stripped"]
                  and len(rep["new_on_stripped"]) == 1)
            rep = run(clean, use_strip=False)
            ok_if("та же правка без --strip: потери и появившийся адрес — находки",
                  ("потеряно", "число", "24") in seen(rep) and ("потеряно", "путь", "P/02") in seen(rep)
                  and ("появилось", "адрес", "site 07/04 §4") in seen(rep) and not rep["new_on_stripped"]
                  and any(f["category"] == "заголовок" for f in rep["findings"]))
            lossy = clean.replace("держит 300 КБ скрипта", "держит скрипт")
            rep = run(lossy)
            ok_if("потерянное число — находка со строкой и текстом «до» и «после»",
                  seen(rep) == [("потеряно", "число", "300 КБ")] and rep["findings"][0]["line"] == 9
                  and "300 КБ" in rep["findings"][0]["before"] and "держит скрипт" in rep["findings"][0]["after"])
            rep = run(clean.replace(", INP ≤ 200 мс", ""))
            ok_if("число потеряно на строке с вырезанным — в списке, не находкой",
                  rep["clean"] and ("число", "200 мс") in [(s["category"], s["item"]) for s in rep["lost_on_stripped"]])
            rep = run(clean.replace("UX-A11-14", "UX-A11-15"))
            ok_if("изменённый id — потеря старого и появление нового",
                  seen(rep) == [("потеряно", "id", "UX-A11-14"), ("появилось", "id", "UX-A11-15")])
            rep = run(clean.replace("### 2.1. Порядок\n\nТекст раздела со ссылкой на `page-gates.yaml`.\n\n", ""))
            ok_if("снятый заголовок и код-спан раздела — находки",
                  seen(rep) == [("потеряно", "заголовок", "2.1. Порядок (стенд P/03)"),
                                ("потеряно", "код", "page-gates.yaml")])
            rep = run(clean.replace("## 3. Источники", "## 4. Источники"))
            ok_if("сдвинутый номер раздела — находка заголовка",
                  [(f["kind"], f["category"]) for f in rep["findings"]] == [("изменено", "заголовок")]
                  and "«3» → «4»" in rep["findings"][0]["note"])
            rep = run(clean.replace("## 2. Ворота", "### 2. Ворота").replace("## 1. Метрики", "## 1. Числа"))
            ok_if("изменённые уровень и текст заголовка — находки",
                  sorted(f["note"] for f in rep["findings"]) == ["текст заголовка", "уровень заголовка: 2 → 3"])
            rep = run(clean.replace(" [практика]", ""))
            ok_if("потерянная метка — находка", seen(rep) == [("потеряно", "метка", "практика")])
            rep = run(clean.replace("медиана 3 прогонов", "медиана 3 прогонов из 5"))
            ok_if("новое число — находка", seen(rep) == [("появилось", "число", "5")])
            rep = run(clean.replace("`[проверено]` ", ""))
            ok_if("слово метки с вырезанным хвостом потеряно — в списке, не молча",
                  rep["clean"]
                  and ("метка", "проверено") in [(s["category"], s["item"]) for s in rep["lost_on_stripped"]])
            moved = (clean.replace("сессия 5 МБ ", "")
                     .replace("Порог блокировки — 4 с;", "Порог блокировки — 4 с, сессия 5 МБ;"))
            rep = run(moved)
            ok_if("элемент ушёл из одного куска в другой — обе находки с отсылкой друг на друга",
                  seen(rep) == [("потеряно", "число", "5 МБ"), ("появилось", "число", "5 МБ")]
                  and all("такой же элемент" in f["note"] for f in rep["findings"]))

            allow = Path(td) / "allow.tsv"
            allow.write_text("файл\tчто\tпричина\n# разрешения\n"
                             "site/07-speed/03-gates.md\t300 КБ\tпорог снят владельцем\n"
                             f"{name}\tзаголовок: Порядок\tраздел снят\n*\t`page-gates.yaml`\tфайл снят\n"
                             "site/*\tфайл\tфайл снят\nsite/07-speed/04-other.md\t9 с\tлишняя строка\n",
                             encoding="utf-8")
            rep = run(lossy.replace("### 2.1. Порядок\n\nТекст раздела со ссылкой на `page-gates.yaml`.\n\n", ""),
                      str(allow))
            ok_if("--allow: названные число, код-спан и заголовок разрешены; лишняя строка — в списке без совпадений",
                  rep["clean"] and rep["allowed"] == 3 and [r["what"] for r in rep["allow_unused"]] == ["файл", "9 с"])

            (repo / name).write_text(lossy, encoding="utf-8")
            lst = Path(td) / "list.tsv"
            lst.write_text("file\tkind\n# md и данные\nsite/07-speed/03-gates.md\tprose\nkb/site/data.yaml\tdata\n"
                           f"{other}\tprose\n", encoding="utf-8")
            rc, out, _ = quiet(["--files-from", str(lst), "--strip", str(strip), "--json"], repo)
            rep = json.loads(out) if out.startswith("{") else {}
            ok_if("вызов: список TSV с заголовком, пути от kb/ и от корня, не md пропущен; --json; код 1",
                  rc == 1 and rep.get("files") == 2 and rep.get("skipped") == 1 and len(rep.get("findings", [])) == 1)
            rc, out, _ = quiet(["kb", "--strip", str(strip), "--list-lost"], repo)
            ok_if("вызов: папка (`kb` — вся база) — все её md; таблица с находкой, списком потерь и итогом",
                  rc == 1 and f"{RULE}  {name}:9  потеряно: число «300 КБ»" in out and "    до:    " in out
                  and "== потеряно на строке с вырезанным (5)" in out
                  and "== появилось на строке с вырезанным (1)" in out and "ИТОГ: находок НОРМА — 1" in out)
            rc, out, _ = quiet(["--strip", str(strip)], repo)
            ok_if("вызов без путей: изменённые md базы", rc == 1 and "файлов 1, с правкой 1" in out)
            (repo / name).write_text(clean, encoding="utf-8")
            rc, out, _ = quiet(["--strip", str(strip)], repo)
            ok_if("вызов: чистая правка — код 0", rc == 0 and "ИТОГ: находок нет" in out)
            (repo / other).unlink()
            (repo / KB_REL / "site/07-speed/05-new.md").write_text("# Новый\n", encoding="utf-8")
            rc, out, _ = quiet(["site/07-speed", "--strip", str(strip)], repo)
            ok_if("файла нет в рабочем дереве — находка; файла нет в базовом коммите — не сравнивается",
                  rc == 1 and "потеряно: файл" in out and "05-new.md" in out and "файлов 3, с правкой 2" in out)
            rc, out, _ = quiet(["site/07-speed", "--strip", str(strip), "--allow", str(allow)], repo)
            ok_if("--allow: снятый файл разрешён строкой «файл»", rc == 0)
            before, after = Path(td) / "a.md", Path(td) / "b.md"
            before.write_text(doc, encoding="utf-8")
            after.write_text(clean.replace("300 КБ", "350 КБ"), encoding="utf-8")
            rc, out, _ = quiet(["--pair", str(before), str(after), "--strip", str(strip)], repo.parent)
            ok_if("--pair: два файла без git — потеря и появление", rc == 1 and "потеряно: число «300 КБ»" in out
                  and "появилось: число «350 КБ»" in out)
            bad = Path(td) / "bad.txt"
            bad.write_text("(незакрытая\n", encoding="utf-8")
            short = Path(td) / "short.tsv"
            short.write_text("a.md\t5\n", encoding="utf-8")
            codes = [quiet(argv, repo)[0] for argv in (["--base", "нет-такого-коммита"], ["--strip", str(bad)],
                                                       ["--strip", str(bad) + ".нет"], ["--allow", str(short)],
                                                       ["нет/такого.md"], ["--files-from", str(lst) + ".нет"],
                                                       ["--pair", str(before), str(after) + ".нет"])]
            ok_if("вызов: нет коммита, битое выражение, нет файла выражений, строка разрешений без причины, нет пути, "
                  "нет списка, нет файла пары — код 2", codes == [2] * 7)
            rc, _, err = quiet([name], repo.parent)
            ok_if("вызов: папка вне репозитория git — код 2", rc == 2 and "репозитория git" in err)
    finally:
        GIT_ENV.clear()
        GIT_ENV.update(git_env)
    print(f"selftest: {ok} OK, {fail} FAIL")
    return 0 if not fail else 1


# ─────────────────────────────── запуск ───────────────────────────────

def main(argv=None, root: Path = ROOT) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], epilog=__doc__.split("\n", 2)[2],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", metavar="ФАЙЛ.md | ПАПКА",
                    help="что сверять; без путей и без списка — изменённые md базы kb/")
    ap.add_argument("--base", default="HEAD", metavar="REF",
                    help="базовый коммит: сверяется его версия файла с рабочим деревом (по умолчанию HEAD)")
    ap.add_argument("--files-from", action="append", default=[], metavar="СПИСОК",
                    help="список путей: путь на строку или первая колонка TSV (ключ — повтором)")
    ap.add_argument("--strip", metavar="ФАЙЛ", help="регулярные выражения: совпадения вырезаются до сравнения")
    ap.add_argument("--allow", metavar="ФАЙЛ", help="TSV «файл · что · причина»: что разрешено потерять или добавить")
    ap.add_argument("--pair", nargs=2, metavar=("СТАРЫЙ", "НОВЫЙ"), help="сравнить два файла на диске без git")
    ap.add_argument("--json", action="store_true", help="отчёт одним документом JSON вместо таблицы")
    ap.add_argument("--list-lost", action="store_true", help="печатать список «потеряно на строке с вырезанным»")
    ap.add_argument("--selftest", action="store_true", help="самопроверка во временном репозитории git, без сети")
    a = ap.parse_args(argv)
    try:
        if a.selftest:
            return selftest()
        strips, allow = read_strip(a.strip), Allow(a.allow)
        if a.pair:
            if a.paths or a.files_from:
                raise CallError("--pair сравнивает два названных файла: пути и --files-from с ним не сочетаются")
            rep = check_pair(a.pair[0], a.pair[1], strips, allow, root)
        else:
            rep = check(root, a.base, a.paths, a.files_from, strips, allow)
    except CallError as e:
        print(f"normcheck: {e}", file=sys.stderr)
        return 2
    print(json.dumps(rep, ensure_ascii=False, indent=1) if a.json else render(rep, a.list_lost))
    return 0 if rep["clean"] else 1


if __name__ == "__main__":
    sys.exit(main())
