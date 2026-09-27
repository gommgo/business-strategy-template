#!/usr/bin/env python3
"""Карта входов Ф4 (сверка баз): строки реестров, таблиц канонов, поправок к соседям, контракта
тройки, владения темами, решений заказчика баз, легенд меток, противоречий между документами и
пунктов SYNTHESIS §9 → `inputs/rows.tsv`.

Разделы находятся по заголовкам, строки — по таблицам и нумерованным спискам (номера строк файлов
не зашиты). Места без табличной структуры — `inputs/manual-rows.tsv` (вливаются в свою группу).
Узлы и примечания — `inputs/assign.tsv` (ключ строки → узел, примечание); у видов строк без
назначения действует правило по умолчанию (`DEFAULT_NODE`). Повторный запуск даёт тот же файл.

Запуск (Python 3.13, только стандартная библиотека):
    python tools/extract_rows.py            # пишет inputs/rows.tsv и печатает сводку
    python tools/extract_rows.py --dump     # строки без назначения узла: ключ, вид, статус, заголовок
    python tools/extract_rows.py --report   # счётчики по источникам и сверка с заявленными
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
BUILD = PHASE.parent
REPO = BUILD.parent.parent
KB = REPO / ".claude/skills/design-deep-dive/kb"
INPUTS = PHASE / "inputs"
ROWS = INPUTS / "rows.tsv"
MANUAL = INPUTS / "manual-rows.tsv"
ASSIGN = INPUTS / "assign.tsv"
SYNTH = BUILD / "phase-2/SYNTHESIS.md"

COLUMNS = ["row", "src_base", "src_kind", "src_file", "line", "item_id", "title", "src_status",
           "mentions", "node", "note"]
KINDS = ["registry", "canon", "handoff", "triad-owner", "triad-format", "triad-label",
         "triad-conclusion", "owners", "customer-decision", "legend", "doc-conflict", "s9"]
NODES = ["GL", "TR", "GT", "CM", "ST", "NU", "TX", "VI", "JU", "CN"]
NODE_OK = set(NODES) | {"—"}
BASES = ["ux", "ui", "site", "text", "creative", "ai-media", "blender", "claude-design"]
MENTION_ORDER = BASES + ["kimi"]

# Узел по умолчанию для видов строк, у которых смысл задан видом; registry и handoff назначаются
# построчно в assign.tsv. Пункты SYNTHESIS §9 — по таблице узлов PLAN.md.
DEFAULT_NODE = {
    "canon": "CN", "owners": "CN", "customer-decision": "CN",
    "triad-owner": "TR", "triad-format": "TR", "triad-conclusion": "TR",
    "triad-label": "JU", "legend": "JU",
}
S9_NODE = {1: "TR", 2: "GT", 3: "GT", 4: "TR", 5: "GL", 6: "CM", 7: "ST", 8: "ST", 9: "NU", 10: "NU",
           11: "NU", 12: "NU", 13: "JU", 14: "VI", 15: "VI", 16: "TX", 17: "VI", 18: "VI", 19: "CM",
           20: "CN", 21: "JU", 22: "GT"}

# ─────────────────────────────── Markdown ───────────────────────────────

HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
NUM = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
BULLET = re.compile(r"^(\s*)[-*]\s+(.*)$")
_CACHE: dict[Path, list[str]] = {}


def load(path: Path) -> list[str]:
    if path not in _CACHE:
        _CACHE[path] = path.read_text(encoding="utf-8").splitlines()
    return _CACHE[path]


def headings(lines: list[str]):
    """(индекс, уровень, текст) заголовков вне блоков кода."""
    code = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            code = not code
            continue
        if code:
            continue
        m = HEADING.match(line)
        if m:
            yield i, len(m.group(1)), m.group(2)


def section(lines: list[str], pattern: str, *, level: int | None = None, stop_any: bool = False,
            occurrence: int = 1) -> tuple[int, int]:
    """Индексы [начало, конец) раздела: заголовок совпал с `pattern` (re.search); конец — следующий
    заголовок того же или более высокого уровня (`stop_any` — любого)."""
    rx = re.compile(pattern)
    hs = list(headings(lines))
    seen = 0
    for n, (i, lvl, text) in enumerate(hs):
        if rx.search(text) and (level is None or lvl == level):
            seen += 1
            if seen < occurrence:
                continue
            end = len(lines)
            for j, lvl2, _ in hs[n + 1:]:
                if stop_any or lvl2 <= lvl:
                    end = j
                    break
            return i, end
    raise LookupError(f"раздел не найден: {pattern!r}")


def split_row(line: str, want: int | None = None) -> list[str]:
    """Ячейки строки таблицы: `|` внутри `кода` и `\\|` не делят ячейку."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]

    def cut(aware: bool) -> list[str]:
        cells, buf, tick, i = [], [], False, 0
        while i < len(s):
            c = s[i]
            if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
                buf.append("|")
                i += 2
                continue
            if aware and c == "`":
                tick = not tick
            if c == "|" and not tick:
                cells.append("".join(buf).strip())
                buf = []
            else:
                buf.append(c)
            i += 1
        cells.append("".join(buf).strip())
        return cells

    cells = cut(True)
    if want and len(cells) != want:
        plain = cut(False)
        if len(plain) == want:
            return plain
    return cells


def tables(lines: list[str], start: int, end: int):
    """Таблицы раздела: [(номер строки заголовка, ячейки заголовка, [(номер строки, ячейки), …])]."""
    out, i, code = [], start, False
    while i < end:
        line = lines[i]
        if line.lstrip().startswith("```"):
            code = not code
            i += 1
            continue
        if not code and line.lstrip().startswith("|") and i + 1 < end and SEP.match(lines[i + 1]):
            header = split_row(line)
            rows, j = [], i + 2
            while j < end and lines[j].lstrip().startswith("|"):
                rows.append((j + 1, split_row(lines[j], len(header))))
                j += 1
            out.append((i + 1, header, rows))
            i = j
            continue
        i += 1
    return out


def numbered(lines: list[str], start: int, end: int, indent: int = 0):
    """Пункты нумерованного списка с отступом `indent`: [(номер, строка файла, текст одной строкой)].
    Продолжение пункта — строки с отступом (и пустые между ними); пункт кончается на строке без
    отступа, заголовке или новом пункте."""
    items, cur = [], None
    for i in range(start, end):
        line = lines[i]
        m = NUM.match(line)
        if m and len(m.group(1)) == indent:
            if cur:
                items.append(cur)
            cur = [int(m.group(2)), i + 1, m.group(3).strip()]
            continue
        if cur is None:
            continue
        if not line.strip():
            continue
        if HEADING.match(line) or not line[:1].isspace():
            items.append(cur)
            cur = None
            continue
        cur[2] += " " + line.strip()
    if cur:
        items.append(cur)
    return [tuple(x) for x in items]


def bullets(lines: list[str], start: int, end: int, indent: int = 0):
    """Пункты маркированного списка с отступом `indent` (продолжение — как у `numbered`)."""
    items, cur = [], None
    for i in range(start, end):
        line = lines[i]
        m = BULLET.match(line)
        if m and len(m.group(1)) == indent:
            if cur:
                items.append(cur)
            cur = [i + 1, m.group(2).strip()]
            continue
        if cur is None:
            continue
        if not line.strip():
            continue
        if HEADING.match(line) or not line[:1].isspace():
            items.append(cur)
            cur = None
            continue
        cur[1] += " " + line.strip()
    if cur:
        items.append(cur)
    return [tuple(x) for x in items]


# ─────────────────────────────── Поля строк ───────────────────────────────

def clean(text: str) -> str:
    text = text.replace("\t", " ").replace("\r", " ").replace("\n", " ")
    text = text.replace("**", "").replace("<br>", " ")
    return re.sub(r"\s+", " ", text).strip()


def short(text: str, limit: int = 120) -> str:
    text = clean(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def first_part(text: str, sep: str = "·") -> str:
    return clean(text).split(sep)[0].strip()


def bold_head(text: str) -> str:
    """Текст первого **…** или начало строки до точки."""
    m = re.search(r"\*\*(.+?)\*\*", text)
    return m.group(1).strip() if m else text


PATH_MENTION = re.compile(r"\.\./(?:\.\./)*(ux|ui|site|text|creative|ai-media|blender|claude-design|kimi)"
                          r"(?:-research)?/")
WORD_MENTION = re.compile(r"(?<![\w./@#:\[-])(ux|ui|site|text|creative|ai-media|blender|claude-design)"
                          r"(?:-research)?(?![\w-])")
KIMI = re.compile(r"(?<![\w./-])[Kk]imi(?:-research)?(?![\w-])")
CD_PRODUCT = re.compile(r"Claude Design")
TICKS = re.compile(r"`[^`]*`")


def mentions(text: str, own: str, extra: tuple[str, ...] = ()) -> str:
    """Другие базы, названные в тексте: пути `../<база>/`, слова-имена баз вне `кода`, Kimi, Claude Design."""
    found = set(extra)
    found.update(PATH_MENTION.findall(text))
    bare = TICKS.sub(" ", text)
    found.update(WORD_MENTION.findall(bare))
    if KIMI.search(text):
        found.add("kimi")
    if CD_PRODUCT.search(bare):
        found.add("claude-design")
    found.discard(own)
    return ",".join(b for b in MENTION_ORDER if b in found)


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO).as_posix()


def short_src(src_file: str) -> str:
    """Ключ файла для assign.tsv: путь от kb/ или от research/design-build/."""
    for prefix in (".claude/skills/design-deep-dive/kb/", "research/design-build/"):
        if src_file.startswith(prefix):
            return src_file[len(prefix):]
    return src_file


class Rows:
    def __init__(self):
        self.groups: "OrderedDict[str, list[dict]]" = OrderedDict()
        self.report: list[tuple[str, int, str]] = []   # (источник, найдено, заявлено/замечание)

    def add(self, group: str, *, base: str, kind: str, path: Path, line: int, item: str, title: str,
            status: str = "", text: str = "", extra: tuple[str, ...] = (), note: str = "") -> dict:
        row = {
            "src_base": base, "src_kind": kind, "src_file": rel(path), "line": str(line),
            "item_id": clean(item), "title": short(title), "src_status": short(status, 90),
            "mentions": mentions(text or title, base, extra), "node": "", "note": clean(note),
        }
        self.groups.setdefault(group, []).append(row)
        return row

    def count(self, source: str, found: int, claim: str = ""):
        self.report.append((source, found, claim))


# ─────────────────────────────── (a) Реестры противоречий ───────────────────────────────

def ui_registry(R: Rows):
    path = KB / "ui/CONTRADICTIONS.md"
    L = load(path)
    s, e = section(L, r"^Сводная таблица$")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        R.add("a:ui", base="ui", kind="registry", path=path, line=ln, item=c[0], title=c[1],
              status=f"решено · {c[3]}", text=" | ".join(c))
    R.count("ui CONTRADICTIONS C1–C49", len(rows), "заявлено 49")


def text_registry(R: Rows):
    path = KB / "text/CONTRADICTIONS.md"
    L = load(path)
    s, e = section(L, r"^Сводная таблица$")
    (_, hdr, rows), = tables(L, s, e)
    st = Counter()
    for ln, c in rows:
        status = first_part(c[3])
        st[status.split()[0] if status else "?"] += 1
        R.add("a:text", base="text", kind="registry", path=path, line=ln, item=c[0], title=c[1],
              status=c[3], text=" | ".join(c))
    R.count("text CONTRADICTIONS X1–X45", len(rows),
            "заявлено 45: решено 15, позиция 22, открыто 8; найдено " + ", ".join(f"{k} {v}" for k, v in st.most_common()))
    s, e = section(L, r"^Числовые расхождения внутри базы")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        m = re.search(r"\*\*((?:сверено|исправлено)[^*]*)\*\*", c[3])
        R.add("a:text", base="text", kind="registry", path=path, line=ln, item=c[0],
              title=f"{c[1]} ↔ {c[2]}", status=m.group(1) if m else "проверить", text=" | ".join(c))
    R.count("text CONTRADICTIONS N1–N10", len(rows), "заявлено 10")
    # README «Поправки к соседям (свод)» — позиции text для сайта (таблица PLAN.md «Поправки…» — её источник)
    rpath = KB / "text/README.md"
    RL = load(rpath)
    s, e = section(RL, r"^Поправки к соседям \(свод\)$", level=2)
    (_, hdr, rows), = tables(RL, s, e)
    for k, (ln, c) in enumerate(rows, 1):
        R.add("a:text", base="text", kind="registry", path=rpath, line=ln, item=f"свод-{k:02d}",
              title=f"{c[0]}: {c[1]}", status="поправка к соседу (свод README)", text=" | ".join(c))
    R.count("text README «Поправки к соседям (свод)»", len(rows), "полная передача — handoff (S1b: 80 строк)")


def creative_registry(R: Rows):
    path = KB / "creative/CONTRADICTIONS.md"
    L = load(path)
    s, e = section(L, r"^Сводная таблица$")
    (_, hdr, rows), = tables(L, s, e)
    st = Counter()
    for ln, c in rows:
        st[clean(c[2]).split()[0].strip("(),") if c[2] else "?"] += 1
        R.add("a:creative", base="creative", kind="registry", path=path, line=ln, item=c[0], title=c[1],
              status=c[2], text=" | ".join(c))
    R.count("creative CONTRADICTIONS X-01…X-67", len(rows),
            "README и шапка handoff — «66»; SYNTHESIS: решено 31, позиция 22, открыто 9, X-59 заказчику; найдено "
            + ", ".join(f"{k} {v}" for k, v in st.most_common()))
    # §Ж — поправки к правилам соседей для сайтов (копия таблицы PLAN.md со статусами)
    s, e = section(L, r"^Ж\. Таблица поправок")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        R.add("a:creative", base="creative", kind="registry", path=path, line=ln, item=f"Ж №{clean(c[0])}",
              title=c[1], status=c[-1], text=" | ".join(c),
              note="поправка к соседу для сайта (§Ж; таблица PLAN.md «Поправки к правилам соседей» — копия)")
    R.count("creative CONTRADICTIONS §Ж (поправки к соседям)", len(rows), "заявлено 26")


def aimedia_registry(R: Rows):
    path = KB / "ai-media/CONTRADICTIONS.md"
    L = load(path)
    s, e = section(L, r"^Сводная таблица$")
    (_, hdr, rows), = tables(L, s, e)
    st = Counter()
    for ln, c in rows:
        status = first_part(c[3])
        st[status.split()[0] if status else "?"] += 1
        R.add("a:ai-media", base="ai-media", kind="registry", path=path, line=ln, item=c[0], title=c[1],
              status=c[3], text=" | ".join(c))
    R.count("ai-media CONTRADICTIONS X1–X50", len(rows),
            "заявлено 50: решено 38, позиция 10, открыто 2; найдено " + ", ".join(f"{k} {v}" for k, v in st.most_common()))


UX_DIRECT = {2, 5, 12, 22, 32, 42, 43, 46, 47}


def ux_registry(R: Rows):
    path = KB / "ux/README.md"
    L = load(path)
    s, e = section(L, r"^Реестр разрешённых противоречий$", level=2)
    tbs = tables(L, s, e)
    _, hdr, rows = tbs[0]
    for ln, c in rows:
        n = int(re.sub(r"\D", "", c[0]))
        status = "закрыто правкой (прямое)" if n in UX_DIRECT else "позиция с условием"
        R.add("a:ux", base="ux", kind="registry", path=path, line=ln, item=f"№ {n}", title=c[1],
              status=status, text=" | ".join(c))
    R.count("ux README реестр № 1–61", len(rows), "шапка реестра — «Шестьдесят расхождений»; строк 61 (№ 61 — дополнение claude-design)")
    s2, e2 = section(L, r"^Позиции, ограниченные контекстом$", level=3)
    (_, hdr, rows2), = tables(L, s2, e2)
    for k, (ln, c) in enumerate(rows2, 1):
        R.add("a:ux", base="ux", kind="registry", path=path, line=ln, item=f"поз-{k:02d}",
              title=f"{c[0]} ({c[1]})", status="не правило (развилка с условием)", text=" | ".join(c))
    R.count("ux README позиции с условием", len(rows2), "заявлено 16")


def site_registry(R: Rows):
    path = KB / "site/README.md"
    L = load(path)
    s, e = section(L, r"^Реестр разрешённых противоречий$", level=2)
    (_, hdr, rows), = tables(L, s, e)
    ids = 0
    for ln, c in rows:
        ids += len(re.findall(r"В-\d+", c[0]))
        R.add("a:site", base="site", kind="registry", path=path, line=ln, item=c[0], title=c[1],
              status=c[4], text=" | ".join(c))
    R.count("site README В-01…В-36", len(rows), f"id в строках: {ids} (В-13 и В-14 — одной строкой)")
    s, e = section(L, r"^Свод поправок к соседям$", level=2)
    (_, hdr, rows), = tables(L, s, e)
    v = Counter(clean(c[4]).split()[0] for _, c in rows)
    for ln, c in rows:
        R.add("a:site-svod", base="site", kind="registry", path=path, line=ln, item=f"PLAN №{c[0]}",
              title=c[1], status=c[4], text=" | ".join(c))
    R.count("site README «Свод поправок» (таблица)", len(rows),
            "заявлено 26: ✔ 19, ◐ 7; найдено " + ", ".join(f"{k} {n}" for k, n in v.most_common()))
    # «Вне таблицы PLAN» (17): в README — абзацем, в отчёте X §1.2 — таблицей «Поправки, которых нет в таблице PLAN»
    xpath = xreport("site")
    X = load(xpath)
    s, e = section(X, r"^1\.2\. С соседями")
    readme_line = next(i for i, x in enumerate(L) if x.startswith("**Вне таблицы PLAN**")) + 1
    extra = [t for t in tables(X, s, e) if t[1][:2] == ["Файл:строка", "Поправка к"]]
    (_, hdr, rows), = extra
    for k, (ln, c) in enumerate(rows, 1):
        R.add("a:site-svod", base="site", kind="registry", path=xpath, line=ln, item=f"вне-{k:02d}",
              title=f"{c[1]}: {c[2]}", status="оформлено (вне таблицы PLAN)", text=" | ".join(c),
              note=f"в README «Свод поправок» — абзац «Вне таблицы PLAN» (стр. {readme_line})")
    R.count("site «Вне таблицы PLAN» (отчёт X §1.2)", len(rows), "заявлено 17")


def r_ids(text: str) -> list[int]:
    out = []
    for a, b in re.findall(r"R(\d+)(?:\s*[–-]\s*R(\d+))?", text):
        out.extend(range(int(a), int(b) + 1) if b else [int(a)])
    return out


def blender_x_registry() -> dict[int, dict]:
    path = KB / "blender/99-raw/reports/wave4-X-audit.md"
    L = load(path)
    s, e = section(L, r"^1\. Реестр противоречий$", level=2)
    (_, hdr, rows), = tables(L, s, e)
    out = {}
    for ln, c in rows:
        n = int(c[0][1:])
        dec = re.findall(r"\*\*([^*]+?)\*\*", c[5])
        out[n] = {"line": ln, "theme": c[1], "decision": "; ".join(d.rstrip(":").strip() for d in dec) or clean(c[5])[:40],
                  "text": " | ".join(c)}
    return out


def blender_registry(R: Rows):
    path = KB / "blender/README.md"
    L = load(path)
    xr = blender_x_registry()
    s, e = section(L, r"^Реестр противоречий$", level=2)
    tbs = tables(L, s, e)
    covered: set[int] = set()
    _, hdr, rows = tbs[0]
    for ln, c in rows:
        m = re.match(r"\*\*(.+?)\*\*\s*\((.+?)\)", c[0])
        theme, rs = (m.group(1), m.group(2)) if m else (c[0], "")
        nums = r_ids(rs)
        covered.update(nums)
        dec = "; ".join(f"R{n}: {xr[n]['decision']}" for n in nums if n in xr)
        R.add("a:blender", base="blender", kind="registry", path=path, line=ln, item=clean(rs), title=theme,
              status=dec, text=" | ".join(c))
    missing = [n for n in range(1, 53) if n not in covered]
    xpath = KB / "blender/99-raw/reports/wave4-X-audit.md"
    for n in missing:
        x = xr[n]
        R.add("a:blender", base="blender", kind="registry", path=xpath, line=x["line"], item=f"R{n}",
              title=x["theme"], status=x["decision"], text=x["text"],
              note="нет в реестре README — строка из отчёта X §1")
    R.count("blender README реестр R (строк-тем)", len(rows),
            f"R в строках: {len(covered)} из 52; вне README: {', '.join(f'R{n}' for n in missing) or 'нет'}; в отчёте X §1 строк: {len(xr)}")
    s2, e2 = section(L, r"^Добавлено испытанием 15-showcase", level=3)
    (_, hdr, rows2), = tables(L, s2, e2)
    for ln, c in rows2:
        m = re.match(r"\*\*(T\d+)\.\s*(.+?)\*\*", c[0])
        item, theme = (m.group(1), m.group(2)) if m else (c[0], c[0])
        if item in {"T15", "T18"}:
            status = "открыто (пробел)" if item == "T15" else "открыто (не откалибровано, [спорно])"
        elif "исправлено" in c[2]:
            status = "исправлено FX"
        else:
            status = "позиция базы"
        R.add("a:blender", base="blender", kind="registry", path=path, line=ln, item=item, title=theme,
              status=status, text=" | ".join(c))
    R.count("blender README T1–T26", len(rows2), "заявлено 26; открыты T15, T18 (SYNTHESIS §5.1)")


# ─────────────────────────────── (b) Таблицы канонов ───────────────────────────────

def xreport(base: str) -> Path:
    return KB / base / "99-raw/reports/wave4-X-audit.md"


def canon_tables(R: Rows):
    # ux §2.1
    path = xreport("ux")
    L = load(path)
    s, e = section(L, r"^2\.1\. Одно правило в нескольких файлах")
    (_, hdr, rows), = tables(L, s, e)
    for k, (ln, c) in enumerate(rows, 1):
        R.add("b:ux", base="ux", kind="canon", path=path, line=ln, item=f"§2.1-{k:02d}", title=c[0],
              status=f"канон: {c[3]}", text=" | ".join(c))
    R.count("ux X §2.1 (таблица канонов)", len(rows), "SYNTHESIS §5.2 и Р50 — «54 строки»")

    # site §1.3, §2
    path = xreport("site")
    L = load(path)
    s, e = section(L, r"^1\.3\. С сёстрами")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        R.add("b:site13", base="site", kind="canon", path=path, line=ln, item=c[0], title=c[1],
              status=re.split(r"(?<=[.;])\s", clean(c[4]))[0], text=" | ".join(c))
    R.count("site X §1.3 С-01…С-32", len(rows), "заявлено 32")
    s, e = section(L, r"^2\. Дубли и каноническое место")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        R.add("b:site2", base="site", kind="canon", path=path, line=ln, item=c[0], title=c[1],
              status=f"канон: {c[3]}", text=" | ".join(c))
    R.count("site X §2 Д-01…Д-19", len(rows), "заявлено 19")
    s, e = section(L, r"^9\.3\. Что не править")
    items = numbered(L, s, e)
    for n, ln, text in items:
        R.add("b:site93", base="site", kind="legend", path=path, line=ln, item=f"§9.3 пометки п. {n}",
              title=text, status="правило пометок", text=text)
    R.count("site X §9.3 правило пометок", len(items), "8 пунктов; абзац «Не править» — manual-rows")

    # text §3, §6, §7
    path = xreport("text")
    L = load(path)
    s, e = section(L, r"^3\. Пятнадцать вопросов базы")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        R.add("b:text3", base="text", kind="canon", path=path, line=ln, item=f"вопрос {c[0]}", title=c[1],
              status=c[2], text=" | ".join(c))
    R.count("text X §3 (15 вопросов)", len(rows), "заявлено 15: закрыты 12, с частичным стыком 3")
    s, e = section(L, r"^6\. Дубли и каноническое место")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        R.add("b:text6", base="text", kind="canon", path=path, line=ln, item=c[0], title=c[1],
              status=f"канон: {c[4]}", text=" | ".join(c))
    R.count("text X §6 Д1–Д15", len(rows), "заявлено 15")
    s, e = section(L, r"^7\. Калибровка утилит")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        R.add("b:text7", base="text", kind="canon", path=path, line=ln, item=c[0], title=f"{c[1]}: {c[2]}",
              status=f"калибровка, приоритет {clean(c[5])}", text=" | ".join(c))
    R.count("text X §7 К1–К31", len(rows), "заявлено 31")

    # creative §2, §9
    path = xreport("creative")
    L = load(path)
    s, e = section(L, r"^2\. Дубли и каноническое место")
    (_, hdr, rows), = tables(L, s, e)
    for k, (ln, c) in enumerate(rows, 1):
        R.add("b:creative2", base="creative", kind="canon", path=path, line=ln, item=f"§2-{k:02d}", title=c[0],
              status=f"канон: {c[2]}", text=" | ".join(c))
    R.count("creative X §2 (нормы)", len(rows), "SYNTHESIS — «≈ 20 норм»")
    s, e = section(L, r"^9\. Калибровка утилит")
    (_, hdr, rows), = tables(L, s, e)
    for k, (ln, c) in enumerate(rows, 1):
        R.add("b:creative9", base="creative", kind="canon", path=path, line=ln, item=f"§9-{k:02d}", title=c[0],
              status=f"порог: {first_part(c[2], ';')}", text=" | ".join(c))
    R.count("creative X §9 (пороги)", len(rows), "заявлено 14")

    # blender §4
    path = xreport("blender")
    L = load(path)
    s, e = section(L, r"^4\. Дубли и рассинхрон чисел")
    (_, hdr, rows), = tables(L, s, e)
    for k, (ln, c) in enumerate(rows, 1):
        R.add("b:blender4", base="blender", kind="canon", path=path, line=ln, item=f"§4-{k:02d}", title=c[0],
              status=f"канон: {c[3]}", text=" | ".join(c))
    R.count("blender X §4 (темы)", len(rows), "заявлено 22")

    # ai-media §3 и «Продолжение X2» — только счёт: история поправок, не нормы
    path = xreport("ai-media")
    L = load(path)
    s, e = section(L, r"^3\. Противоречия и слабые места$")
    n3 = sum(len(r) for _, _, r in tables(L, s, e))
    s, e = section(L, r"^Продолжение X2")
    nx2 = sum(len(r) for _, _, r in tables(L, s, e))
    R.count("ai-media X §3 (таблица правок) — не нормы, только счёт", n3, "история поправок")
    R.count("ai-media X «Продолжение X2» (таблицы) — не нормы, только счёт", nx2, "история поправок и тестов")


# ─────────────────────────────── (c) Поправки к соседям ───────────────────────────────

# Статусы site C1–C9 устарели: ответ site на итоговый пакет creative (W4, 25.09 08:49) в kb не
# перенесён; его итог записан в site PLAN.md «Статус» (25.09 08:49), creative PLAN.md «Статус»
# (25.09 08:50) и phase-2/light/site-research.md Д.1 п. 3.
W4 = {
    "C1": "W4 25.09: уровни 5 proposed типов подтверждены (по логике решения 20), типы — proposed до S2",
    "C9": "W4 25.09: решено — steps.mobile (линия 2 px) и счёт акцентов — зона creative, вариант подачи в block-treatments.yaml",
    **{f"C{n}": "W4 25.09: закрыто ответом site на итоговый пакет creative" for n in range(2, 9)},
}
SECTION_BASE = [("kimi", "kimi"), ("ai-media", "ai-media"), ("blender", "blender"), ("ux", "ux"),
                ("ui", "ui"), ("text", "text"), ("creative", "creative"), ("site", "site")]


def base_of_heading(text: str) -> str:
    for key, base in SECTION_BASE:
        if re.search(rf"(?<![\w-]){re.escape(key)}(?:-research)?(?![\w-])", text):
            return base
    return ""


def answers(path: Path, pattern: str) -> dict[str, str]:
    L = load(path)
    s, e = section(L, pattern)
    (_, hdr, rows), = tables(L, s, e)
    return {clean(c[0]): clean(c[-1]) for _, c in rows}


def site_handoff(R: Rows):
    path = KB / "site/99-raw/handoff-to-neighbours.md"
    L = load(path)
    crv_ans = answers(KB / "creative/99-raw/handoff-to-neighbours.md", r"^Ответ на ваши C1–C10")
    per = Counter()
    for i, lvl, text in headings(L):
        if lvl < 2 or not re.search(r"research", text):
            continue
        addressee = base_of_heading(text)
        s, e = section(L, re.escape(text), level=lvl)
        for _, hdr, rows in tables(L, s, e):
            for ln, c in rows:
                item = clean(c[0])
                note = []
                if item in W4:
                    note.append(W4[item])
                if addressee == "creative" and item in crv_ans:
                    note.append(f"ответ creative: {crv_ans[item]}")
                R.add("c:site", base="site", kind="handoff", path=path, line=ln, item=item, title=c[2],
                      status=c[-1], text=" | ".join(c), extra=(addressee,), note="; ".join(note))
                per[addressee] += 1
    total = sum(per.values())
    R.count("site handoff (строки передачи)", total,
            "README site — «62 строки: K 18, M 9, B 4, U 7, UI 1, T 13, C 10»; найдено "
            + ", ".join(f"{k} {v}" for k, v in per.items()))


def text_handoff(R: Rows):
    path = KB / "text/99-raw/handoff-to-neighbours.md"
    L = load(path)
    crv_ans = answers(KB / "creative/99-raw/handoff-to-neighbours.md", r"^Ответ на ваши crv-01")
    per = Counter()
    for i, lvl, text in headings(L):
        if lvl != 2 or " — `../../" not in text:
            continue
        addressee = base_of_heading(text)
        s, e = section(L, re.escape(text), level=2)
        for _, hdr, rows in tables(L, s, e):
            for ln, c in rows:
                item = clean(c[0])
                note = f"ответ creative: {crv_ans[item]}" if item in crv_ans else ""
                R.add("c:text", base="text", kind="handoff", path=path, line=ln, item=item, title=c[1],
                      status=f"П{clean(c[-1])}", text=" | ".join(c), extra=(addressee,), note=note)
                per[addressee] += 1
        if addressee == "site":
            s2 = next(k for k in range(s, e) if L[k].startswith("**Встречные запросы site к text**"))
            for n, ln, t in numbered(L, s2 + 1, e):
                R.add("c:text", base="text", kind="handoff", path=path, line=ln, item=f"встр-{n}", title=t,
                      status="запрос site к text", text=t, extra=("site",))
                per["site→text"] += 1
    s, e = section(L, r"^Словарь: предложения text")
    (_, hdr, rows), = tables(L, s, e)
    for k, (ln, c) in enumerate(rows, 1):
        R.add("c:text", base="text", kind="handoff", path=path, line=ln, item=f"слов-{k:02d}",
              title=f"{c[0]} ({c[1]})", status=c[3], text=" | ".join(c), extra=("site",))
        per["словарь"] += 1
    R.count("text handoff", sum(per.values()),
            "«Кому сколько строк»: ux 21, kimi 17, ai-media 9, ui 4, site 18, creative 11; найдено "
            + ", ".join(f"{k} {v}" for k, v in per.items()))


CREATIVE_PREFIX = {"cs": "site", "ct": "text", "cu": "ui", "cx": "ux", "ca": "ai-media", "cb": "blender",
                   "ck": "kimi", "ce": "", "cz": "", "ci": ""}


def creative_handoff(R: Rows):
    path = KB / "creative/99-raw/handoff-to-neighbours.md"
    L = load(path)
    per = Counter()
    s, e = section(L, r"^Что site приняла по пакетам creative")
    (_, hdr, rows), = tables(L, s, e)
    for k, (ln, c) in enumerate(rows, 1):
        R.add("c:creative", base="creative", kind="handoff", path=path, line=ln, item=f"принято-{k:02d}",
              title=f"{c[0]}: {c[1]}", status=c[2], text=" | ".join(c), extra=("site",))
        per["site (принято)"] += 1
    for _, hdr, rows in tables(L, 0, len(L)):
        for ln, c in rows:
            m = re.match(r"^(c[a-z])-\d+$", clean(c[0]))
            if not m:
                continue
            pre = m.group(1)
            addressee = CREATIVE_PREFIX[pre]
            title = c[2] if len(c) >= 5 else c[1]
            R.add("c:creative", base="creative", kind="handoff", path=path, line=ln, item=clean(c[0]),
                  title=title, status=c[-1], text=" | ".join(c), extra=(addressee,) if addressee else ())
            per[pre] += 1
    R.count("creative handoff (без ответов на C1–C10 и crv — они вписаны в note строк site и text)",
            sum(per.values()), "«Кому сколько строк»: site 13 принято + 12 cs, text 4 ct, ui 16, ux 3, ai-media 14, "
            "blender 13, kimi 14, внешние 1, заказчик 3, внутри базы 9; найдено "
            + ", ".join(f"{k} {v}" for k, v in per.items()))


def blender_handoff(R: Rows):
    path = KB / "blender/99-raw/handoff-to-neighbours.md"
    L = load(path)
    status = "не вносить (решение владельца 23.09) — справка"
    s, e = section(L, r"^1\.1\. Что заменить и чем")
    (_, hdr, rows), = tables(L, s, e)
    for k, (ln, c) in enumerate(rows, 1):
        R.add("c:blender", base="blender", kind="handoff", path=path, line=ln, item=f"1.1-{k:02d}",
              title=f"ui 12/01 {c[0]}: {c[1]}", status=status, text=" | ".join(c), extra=("ui",))
    n1 = len(rows)
    s, e = section(L, r"^1\.2\. Паспорт серии")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        R.add("c:blender", base="blender", kind="handoff", path=path, line=ln, item=f"паспорт: {clean(c[0])}",
              title=f"паспорт 3D-серии, {c[0]}: ui «{c[1]}» ↔ blender «{c[2]}»", status=status,
              text=" | ".join(c), extra=("ui",))
    n2 = len(rows)
    s, e = section(L, r"^3\. Что предложить соседям добавить")
    items = numbered(L, s, e)
    for n, ln, t in items:
        R.add("c:blender", base="blender", kind="handoff", path=path, line=ln, item=f"3.{n}", title=t,
              status=status, text=t)
    R.count("blender handoff", n1 + n2 + len(items),
            f"§1.1 {n1}, §1.2 паспорт {n2}, §3 {len(items)}; §2 (8 строк ссылок на соседей) — не поправки, не извлекается")


def ux_handoff(R: Rows):
    path = KB / "ux/99-raw/handoff-to-ui-research.md"
    L = load(path)
    s, e = section(L, r"^2\. Дайджесты и транскрипты для передачи")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        R.add("c:ux", base="ux", kind="handoff", path=path, line=ln, item=f"видео {clean(c[0]).strip('`')}",
              title=f"{c[1]} → ui {c[4]}", status="передать дайджест", text=" | ".join(c), extra=("ui",))
    n2 = len(rows)
    s, e = section(L, r"^4\. Какие значения ждём")
    n4 = 0
    for i, lvl, text in headings(L):
        if lvl == 3 and s < i < e:
            s3, e3 = section(L, re.escape(text), level=3)
            body = " ".join(x.strip() for x in L[s3 + 1:e3] if x.strip())
            m = re.search(r"\*\*Ждём:\*\*\s*(.+)", body)
            R.add("c:ux", base="ux", kind="handoff", path=path, line=s3 + 1, item=f"ждём {clean(text)}",
                  title=f"ui {clean(text)}: ждём {m.group(1) if m else body}", status="ждём от ui", text=body,
                  extra=("ui",))
            n4 += 1
    s, e = section(L, r"^5\. Что вернуть в `ux`")
    items = numbered(L, s, e)
    for n, ln, t in items:
        R.add("c:ux", base="ux", kind="handoff", path=path, line=ln, item=f"вернуть {n}", title=t,
              status="ждём от ui", text=t, extra=("ui",))
    R.count("ux handoff-to-ui", n2 + n4 + len(items),
            f"§2 видео {n2}, §4 папки {n4}, §5 {len(items)}; §3 (таблица целей) — одной строкой в manual-rows")


def triad_handoff(R: Rows):
    path = KB / "site/99-raw/notes/triad-contract-2026-09-24.md"
    L = load(path)
    s, e = section(L, r"^8\. Предложения соседям от тройки")
    items = bullets(L, s, e)
    for ln, t in items:
        who = base_of_heading(bold_head(t))
        R.add("c:triad", base="site", kind="handoff", path=path, line=ln, item=f"тройка §8 {who}", title=t,
              status="предложение тройки", text=t, extra=(who,) if who else (),
              note="контракт тройки §8 (сводка предложений трёх баз)")
    R.count("контракт тройки §8 (предложения соседям)", len(items), "5 соседей")


# ─────────────────────────────── (d) Контракт тройки ───────────────────────────────

def triad(R: Rows):
    path = KB / "site/99-raw/notes/triad-contract-2026-09-24.md"
    L = load(path)
    s, e = section(L, r"^2\. Владельцы пересекающихся тем")
    (_, hdr, rows), = tables(L, s, e)
    for k, (ln, c) in enumerate(rows, 1):
        owners = [hdr[j] for j in (1, 2, 3) if re.search(r"\*\*владелец", c[j])]
        status = ("владелец: " + ", ".join(owners)) if owners else "владельцы по частям"
        R.add("d:triad", base="site", kind="triad-owner", path=path, line=ln, item=f"§2-{k:02d}", title=c[0],
              status=status, text=" | ".join(c), extra=("creative", "text"))
    R.count("контракт тройки §2 (темы)", len(rows), "заявлено 32")
    s, e = section(L, r"^3\. Общие форматы обмена")
    items = numbered(L, s, e)
    for n, ln, t in items:
        m = re.search(r"\(владелец ([^,)]+)", t)
        R.add("d:triad", base="site", kind="triad-format", path=path, line=ln, item=f"§3-{n}",
              title=bold_head(t) + (f" (владелец {m.group(1)})" if m else ""),
              status=f"владелец: {m.group(1)}" if m else "", text=t)
    R.count("контракт тройки §3 (форматы)", len(items), "заявлено 16")
    s, e = section(L, r"^4\. Размер и метод")
    labels = []
    for ln, t in bullets(L, s, e):
        if not re.match(r"\*\*Метки", t):
            continue
        for m in re.finditer(r"`(\[[^\]`]+\])`(\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\))?", t):
            labels.append((ln, m.group(1), m.group(3) or "", bold_head(t)))
    seen = set()
    for ln, lab, expl, grp in labels:
        if lab in seen:
            continue
        seen.add(lab)
        R.add("d:triad", base="site", kind="triad-label", path=path, line=ln, item=lab,
              title=f"{lab} {expl}".strip(), status=grp.rstrip(":"), text=expl, extra=("creative", "text"))
    R.count("контракт тройки §4 (метки)", len(seen), "общий набор 12 + метки тройки 4 + синонимы")
    s, e = section(L, r"^6\. Сквозные выводы аудита")
    items = numbered(L, s, e)
    for n, ln, t in items:
        R.add("d:triad", base="site", kind="triad-conclusion", path=path, line=ln, item=f"§6-{n}",
              title=bold_head(t), status="обязателен для тройки", text=t)
    R.count("контракт тройки §6 (выводы)", len(items), "заявлено 15")


# ─────────────────────────────── (e) Кто чем владеет ───────────────────────────────

def owners(R: Rows):
    for base in ("site", "creative"):
        path = KB / base / "99-raw/prompts/_common.md"
        L = load(path)
        s, e = section(L, r"^Кто чем владеет")
        (_, hdr, rows), = tables(L, s, e)
        for k, (ln, c) in enumerate(rows, 1):
            R.add(f"e:{base}", base=base, kind="owners", path=path, line=ln, item=f"владение-{k:02d}", title=c[0],
                  status=f"владелец: {clean(c[1])}", text=" | ".join(c))
        R.count(f"{base} _common.md «Кто чем владеет»", len(rows), "site — заявлено 15" if base == "site" else "сверх задания (для полноты)")
    path = KB / "creative/99-raw/prompts/_common.md"
    L = load(path)
    s, e = section(L, r"^Решения заказчика \(обязательны\)")
    items = numbered(L, s, e)
    for n, ln, t in items:
        R.add("f:creative", base="creative", kind="customer-decision", path=path, line=ln, item=f"_common реш. {n}",
              title=t, status="решение заказчика (_common.md)", text=t)
    R.count("creative _common.md решения 1–6", len(items), "заявлено 6")


# ─────────────────────────────── (f) Решения заказчика баз ───────────────────────────────

def split_semicolons(text: str) -> list[str]:
    head, _, rest = text.partition("):")
    parts = [p.strip().rstrip(".") for p in rest.split(";") if p.strip()]
    return parts


def split_subbullets(text: str) -> list[str]:
    parts = re.split(r"\s-\s(?=\*\*)", text)
    return [p.strip() for p in parts[1:]] if len(parts) > 1 else []


DECISIONS = [
    # (база, файл от kb, заголовок раздела, номера, как делить, узкий конец)
    ("site", "site/PLAN.md", r"^Решения заказчика \(24\.09\.2026\)$", {7, 8, 10, 11, 15, 20}, {15: "semi", 20: "sub"}),
    ("text", "text/PLAN.md", r"^Решения заказчика \(24\.09\.2026\)$", {8, 16, 17}, {}),
    ("creative", "creative/PLAN.md", r"^Решения заказчика \(24\.09\.2026\)$", set(range(1, 25)), {}),
    ("ai-media", "ai-media/PLAN.md", r"^Решения заказчика \(23\.09\.2026\)$", {12, 14, 15, 16}, {}),
    ("blender", "blender/README.md", r"^Решения заказчика \(23\.09\.2026\)", set(range(1, 7)), {}),
    # SYNTHESIS §5.5 claude-design не называет; решения 1–5 — процесс ресерча, 6 и 7 — о границах базы и соседях
    ("claude-design", "claude-design/PLAN.md", r"^Решения заказчика \(25\.09\.2026\)$", {6, 7}, {}),
]


def customer_decisions(R: Rows):
    for base, f, pat, wanted, how in DECISIONS:
        path = KB / f
        L = load(path)
        s, e = section(L, pat, stop_any=True)
        found = 0
        for n, ln, t in numbered(L, s, e):
            if n not in wanted:
                continue
            found += 1
            mode = how.get(n)
            parts = split_semicolons(t) if mode == "semi" else split_subbullets(t) if mode == "sub" else []
            if parts:
                for k, p in enumerate(parts, 1):
                    R.add(f"f:{base}", base=base, kind="customer-decision", path=path, line=ln, item=f"реш. {n}.{k}",
                          title=p, status=f"решение заказчика п. {n}", text=p)
            else:
                R.add(f"f:{base}", base=base, kind="customer-decision", path=path, line=ln, item=f"реш. {n}",
                      title=t, status=f"решение заказчика п. {n}", text=t)
        R.count(f"{base} решения заказчика", found, f"взято {len(wanted)} номеров")


# ─────────────────────────────── (g) Легенды меток ───────────────────────────────

LABEL = re.compile(r"`(\[[^\]`]+\])`")
LEGENDS = [
    # (база, файл от kb, заголовок, id, заметка)
    ("site", "site/PLAN.md", r"^Метки доказательности$", "легенда PLAN", "15 меток: общий набор тройки + 3 своих"),
    ("site", "site/99-raw/prompts/_common.md", r"^Метки доказательности$", "легенда _common", "копия легенды PLAN для агентов"),
    ("text", "text/PLAN.md", r"^Метки доказательности$", "легенда PLAN",
     "SYNTHESIS §5.5 — 16; в таблице 18: общий набор тройки 12, две свои, три узаконены аудитом X, [награда] тройки; "
     "синонимы волн 1–3 — абзац ниже таблицы"),
    ("creative", "creative/PLAN.md", r"^Метки доказательности$", "легенда PLAN", "общий набор + 3 своих"),
    ("ux", "ux/README.md", r"^Легенда меток уровня доказательности$", "легенда README", "9 меток; «Оговорки к числам» — отдельной строкой"),
    ("ux", "ux/99-raw/reports/wave4-X-audit.md", r"^2\.2\. Метки уровня доказательности", "X §2.2", "рассинхрон легенды и предложение девяти меток"),
    ("ui", "ui/README.md", r"^Уровни доказательности и как читать метки$", "легенда README", "метки PLAN + добавленные агентами"),
    ("ai-media", "ai-media/PLAN.md", r"^Метки доказательности$", "легенда PLAN", "`[стенд]` — правило 13/04 §3"),
    ("ai-media", "ai-media/README.md", r"^Уровни доказательности и как читать метки$", "легенда README", "`[стенд]` ни разу не выполнен"),
    ("ai-media", "ai-media/13-routing-matrix/04-update-procedure.md", r"^3\. Правило замены меток$", "13/04 §3", "условия `[стенд]`: ≥ 70 % пар, ≥ 2 задачи"),
    ("blender", "blender/README.md", r"^Легенда меток$", "легенда README", "в выжимку — не ниже `[консенсус]`"),
    ("blender", "blender/PLAN.md", r"^Метки доказательности$", "легенда PLAN", ""),
    ("claude-design", "claude-design/PLAN.md", r"^Метки доказательности$", "легенда PLAN", ""),
    ("claude-design", "claude-design/06-design-process/README.md", r"^Выжимка$", "06/README п. 9", "метки сверх базовых"),
]


def plural(n: int, one: str, few: str, many: str) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} {one}"
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return f"{n} {few}"
    return f"{n} {many}"


REF_TAG = re.compile(r"^\[(?:[SC]\d+|V\d+(?:\s[^\]]*)?)\]$")   # [S7], [C12], [V08 B 03:03] — ссылки, не метки


def legend_labels(L: list[str], s: int, e: int) -> tuple[list[str], list[str], bool]:
    """(метки легенды, прочие метки и ссылки раздела, есть ли таблица легенды). Легенда — первая колонка таблицы
    «Метка | …»; без такой таблицы легендой считаются все метки раздела, кроме образцов ссылок (`[S7]`, `[C12]`)."""
    everything = list(OrderedDict.fromkeys(LABEL.findall("\n".join(L[s + 1:e]))))
    legend = []
    for _, hdr, rows in tables(L, s, e):
        if hdr and clean(hdr[0]).lower().startswith("метка"):
            for _, c in rows:
                found = LABEL.findall(c[0])
                if found:
                    legend.append(found[0])
    legend = list(OrderedDict.fromkeys(legend))
    if not legend:
        return [x for x in everything if not REF_TAG.match(x)], [x for x in everything if REF_TAG.match(x)], False
    return legend, [x for x in everything if x not in legend], True


def legends(R: Rows):
    for base, f, pat, item, note in LEGENDS:
        path = KB / f
        if not path.exists():
            matches = sorted(path.parent.glob(path.name.split("-")[0] + "*.md"))
            path = matches[0]
        L = load(path)
        s, e = section(L, pat)
        line = s + 1
        if item == "06/README п. 9":
            n, line, text = next(x for x in numbered(L, s + 1, e) if x[0] == 9)
            labs, extra, table = list(OrderedDict.fromkeys(LABEL.findall(text))), [], False
        else:
            labs, extra, table = legend_labels(L, s, e)
        where = "в легенде" if table else "в разделе"
        tail = f"; ещё в разделе (синонимы, примеры): {' '.join(extra)}" if extra else ""
        R.add("g:legend", base=base, kind="legend", path=path, line=line, item=item,
              title=f"{clean(L[s].lstrip('#'))}: {plural(len(labs), 'метка', 'метки', 'меток')}",
              status=f"меток {where}: {len(labs)}", text="",
              note=(note + "; " if note else "") + "метки: " + " ".join(labs) + tail)
    # легенды внутри абзацев PLAN ux и ui (строка «Уровни доказательности: …»)
    for base in ("ux", "ui"):
        path = KB / base / "PLAN.md"
        L = load(path)
        k = next(i for i, x in enumerate(L) if x.startswith("Уровни доказательности:"))
        par = []
        for x in L[k:]:
            if not x.strip():
                break
            par.append(x)
        labs = list(OrderedDict.fromkeys(LABEL.findall(" ".join(par))))
        R.add("g:legend", base=base, kind="legend", path=path, line=k + 1, item="легенда PLAN",
              title=f"Уровни доказательности (PLAN): {plural(len(labs), 'метка', 'метки', 'меток')}",
              status=f"меток в абзаце: {len(labs)}", note="метки: " + " ".join(labs))
    R.count("легенды меток", len(LEGENDS) + 2, "SYNTHESIS §5.5: site, text, creative, ux, ai-media, blender, ui, cd 06; "
            "счёт — по таблице «Метка | …», прочие метки раздела — в note")
    caveats(R)


# Оговорки к числам и «что ненадёжно» — вторая половина легенды: где метке нельзя верить без условия.
CAVEATS = [
    # (база, файл от kb, раздел: ("heading", regex) или ("bold", начало строки), id, заметка)
    ("ux", "ux/README.md", ("bold", "**Оговорки к числам**"), "оговорки README", "SYNTHESIS §5.5: «11 оговорок к числам»; абзац внутри легенды"),
    ("ui", "ui/README.md", ("heading", r"^Что ненадёжно$"), "что ненадёжно README", "SYNTHESIS §5.5: ui README «Что ненадёжно»"),
    ("ai-media", "ai-media/README.md", ("heading", r"^Что ненадёжно$"), "что ненадёжно README",
     "копия — CONTRADICTIONS «Что ненадёжно (для корневого README)»"),
    ("blender", "blender/README.md", ("heading", r"^Оговорки к числам$"), "оговорки README", ""),
    ("claude-design", "claude-design/README.md", ("heading", r"^Метки и доверие$"), "метки и доверие README",
     "метки — легенда PLAN (строка PLAN); здесь — оговорки о доверии к источникам"),
]


def caveats(R: Rows):
    for base, f, (how, pat), item, note in CAVEATS:
        path = KB / f
        L = load(path)
        if how == "heading":
            s, e = section(L, pat)
            head = clean(L[s].lstrip("#"))
        else:
            s = next(i for i, x in enumerate(L) if x.startswith(pat))
            e = next((i for i, _, _ in headings(L) if i > s), len(L))
            head = clean(pat)
        items = bullets(L, s + 1, e)
        heads = "; ".join(short(bold_head(t) if t.startswith("**") else t, 60) for _, t in items)
        R.add("g:legend", base=base, kind="legend", path=path, line=s + 1, item=item,
              title=f"{head}: {plural(len(items), 'пункт', 'пункта', 'пунктов')}",
              status=f"оговорок: {len(items)}", text=" ".join(t for _, t in items),
              note=(note + "; " if note else "") + "пункты: " + heads)
    R.count("оговорки к числам и «что ненадёжно»", len(CAVEATS), "SYNTHESIS §5.5 называет ux (11 оговорок) и ui «Что ненадёжно»; "
            "ai-media, blender, claude-design — те же разделы у других баз")


# ─────────────────────────────── (h), (i) SYNTHESIS ───────────────────────────────

# Пункты §6.12 о нормах баз и о решениях, которые узлы принимают; прочие — о счётчиках, журнале и коде, уже
# закрытом Р-решениями (п. 4 — Р69, пп. 5–7 — Р66, п. 21 — Р39, п. 26 — Р77, п. 27 — Р73) — список в INPUTS.md.
DOC_CONFLICTS = {3, 9, 11, 12, 13, 14, 15, 17, 18, 20, 22, 23, 24, 25}


def synthesis(R: Rows):
    L = load(SYNTH)
    s, e = section(L, r"^6\.12\. Противоречия между документами")
    items = numbered(L, s, e)
    for n, ln, t in items:
        if n in DOC_CONFLICTS:
            R.add("h:doc", base="—", kind="doc-conflict", path=SYNTH, line=ln, item=f"§6.12 п. {n}", title=t,
                  status="показано, не сглажено", text=t)
    R.count("SYNTHESIS §6.12 (о нормах баз)", len([x for x in items if x[0] in DOC_CONFLICTS]),
            f"из {len(items)} пунктов; прочие — о журнале, счётчиках и коде (в INPUTS.md)")
    s, e = section(L, r"^9\. Сверка баз")
    (_, hdr, rows), = tables(L, s, e)
    for ln, c in rows:
        n = int(c[0])
        R.add("i:s9", base="—", kind="s9", path=SYNTH, line=ln, item=f"п. {n}", title=c[1], status="что сверять",
              text=" | ".join(c[:3]))
    R.count("SYNTHESIS §9", len(rows), "заявлено 22")


# ─────────────────────────────── Сборка ───────────────────────────────

GROUP_ORDER = ["a:ux", "a:ui", "a:site", "a:site-svod", "a:text", "a:creative", "a:ai-media", "a:blender",
               "a:claude-design", "b:ux", "b:site13", "b:site2", "b:site93", "b:text3", "b:text6", "b:text7",
               "b:creative2", "b:creative9", "b:blender4", "c:site", "c:text", "c:creative", "c:blender", "c:ux",
               "c:triad", "c:claude-design", "d:triad", "e:site", "e:creative", "f:site", "f:text", "f:creative",
               "f:ai-media", "f:blender", "f:claude-design", "g:legend", "h:doc", "i:s9"]
MANUAL_COLUMNS = ["group"] + COLUMNS[1:]


def read_tsv(path: Path) -> tuple[list[str], list[list[str]]]:
    lines = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    header = lines[0].split("\t")
    rows = [x.split("\t") for x in lines[1:]]
    for r in rows:
        if len(r) != len(header):
            raise SystemExit(f"{path.name}: {len(r)} колонок вместо {len(header)}: {r[:3]}")
    return header, rows


def manual_rows(R: Rows):
    if not MANUAL.exists():
        return
    header, rows = read_tsv(MANUAL)
    if header != MANUAL_COLUMNS:
        raise SystemExit(f"{MANUAL.name}: заголовок {header} ≠ {MANUAL_COLUMNS}")
    for r in rows:
        d = dict(zip(header, r))
        path = REPO / d["src_file"]
        if not path.exists():
            raise SystemExit(f"{MANUAL.name}: нет файла {d['src_file']}")
        row = {k: clean(d[k]) for k in COLUMNS[1:]}
        row["title"] = short(row["title"])
        R.groups.setdefault(d["group"], []).append(row)


def key(row: dict) -> str:
    return f"{short_src(row['src_file'])}#{row['item_id']}"


def assign(R: Rows) -> tuple[int, list[str]]:
    table: dict[str, tuple[str, str]] = {}
    if ASSIGN.exists():
        header, rows = read_tsv(ASSIGN)
        if header != ["key", "node", "note"]:
            raise SystemExit(f"{ASSIGN.name}: заголовок {header}")
        for k, node, note in rows:
            if k in table:
                raise SystemExit(f"{ASSIGN.name}: ключ дважды: {k}")
            table[k] = (node.strip(), note.strip())
    used, problems = set(), []
    for rows in R.groups.values():
        for row in rows:
            k = key(row)
            if row["src_kind"] == "s9" and not row["node"]:
                row["node"] = S9_NODE[int(row["item_id"].split()[-1])]
            if k in table:
                used.add(k)
                node, note = table[k]
                if node:
                    row["node"] = node
                if note:
                    row["note"] = f"{row['note']}; {note}" if row["note"] else note
            if not row["node"]:
                row["node"] = DEFAULT_NODE.get(row["src_kind"], "")
            if row["node"] not in NODE_OK:
                problems.append(f"узел {row['node'] or '(пусто)'}: {k}")
    for k in sorted(set(table) - used):
        problems.append(f"ключ assign.tsv не найден среди строк: {k}")
    return len(used), problems


def collect() -> Rows:
    R = Rows()
    for fn in (ux_registry, ui_registry, site_registry, text_registry, creative_registry, aimedia_registry,
               blender_registry, canon_tables, site_handoff, text_handoff, creative_handoff, blender_handoff,
               ux_handoff, triad_handoff, triad, owners, customer_decisions, legends, synthesis):
        fn(R)
    manual_rows(R)
    return R


def ordered(R: Rows) -> list[dict]:
    unknown = [g for g in R.groups if g not in GROUP_ORDER]
    if unknown:
        raise SystemExit(f"группы вне GROUP_ORDER: {unknown}")
    out = []
    for g in GROUP_ORDER:
        out.extend(R.groups.get(g, []))
    for n, row in enumerate(out, 1):
        row["row"] = f"IN-{n:04d}"
    seen = Counter(key(r) for r in out)
    dups = [k for k, v in seen.items() if v > 1]
    if dups:
        raise SystemExit("ключи строк не уникальны: " + "; ".join(dups[:10]))
    return out


def write(rows: list[dict]):
    INPUTS.mkdir(parents=True, exist_ok=True)
    with ROWS.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join(clean(str(r[c])) for c in COLUMNS) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dump", action="store_true", help="строки без узла: ключ · вид · статус · упоминания · заголовок")
    ap.add_argument("--report", action="store_true", help="счётчики по источникам")
    ap.add_argument("--no-write", action="store_true", help="не писать rows.tsv")
    args = ap.parse_args()

    R = collect()
    rows = ordered(R)
    used, problems = assign(R)
    if args.dump:
        for r in rows:
            if not r["node"] or r["node"] not in NODE_OK:
                print("\t".join([key(r), r["src_kind"], r["src_status"][:40], r["mentions"], r["title"]]))
        return 0
    if args.report:
        for src, n, claim in R.report:
            print(f"{n:5d}  {src} — {claim}")
    if not args.no_write:
        write(rows)
    by_node = Counter(r["node"] or "?" for r in rows)
    by_kind = Counter(r["src_kind"] for r in rows)
    print(f"строк: {len(rows)} → {rel(ROWS) if not args.no_write else '(не записано)'}")
    print("по видам: " + ", ".join(f"{k} {by_kind[k]}" for k in KINDS if by_kind[k]))
    print("по узлам: " + ", ".join(f"{k} {by_node[k]}" for k in NODES + ['—', '?'] if by_node[k]))
    print(f"назначений из assign.tsv: {used}")
    if problems:
        print(f"замечаний: {len(problems)}", file=sys.stderr)
        for p in problems[:40]:
            print("  " + p, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
