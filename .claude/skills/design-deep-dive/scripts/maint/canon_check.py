#!/usr/bin/env python3
"""Проверка таблицы «норма → место» `kb/common/canon.tsv` и её сверка с записями `kb/common/CONTRADICTIONS.md`.

`canon.tsv` — источник правды о месте каждой нормы: норма и её место правятся в таблице и в записи `CONTRADICTIONS.md`
вместе (`kb/common/README.md § Как пользоваться canon.tsv`). Утилита проверяет результат правки; адреса карты
`kb/INDEX.md` сверяет `mapcheck.py`, ссылки и следы в правленых md — `refcheck.py`.

Таблица:
  • форма — колонки `norm place status id copies`, пять ячеек в строке, пустых `norm`, `place`, `status`, `id` нет,
    `status` — `закрыто` или `позиция`, id — `<КОД>-<номер>`; тема `norm` — коротко, до 80 знаков (иначе
    предупреждение);
  • одно место на норму — id уникальны, в `place` одно место (без «;»), у одной темы (`norm`) одно место;
  • место — путь существует (от `kb/`, префикс `kb/` допустим; `docs/…`, `.claude/…` и путь, которого нет в `kb/`, — от
    корня репозитория), раздел `§ …` md-файла есть (номер — заголовок, имя — заголовок или строка файла, «№ N» — пункт
    или строка таблицы раздела, «п. N» не сверяется), ключ `#…` есть (md — заголовок; YAML, JSON — путь через точку:
    ключ словаря, элемент списка по `id`, `key`, `name`, `slug`, `code`, уровень, пропущенный в пути, семейство ключей
    `<имя>_*`, диапазон `A…N`); место не в материале к разбору, не в `PLAN.md` базы и не в журнале сборки (шаблоны
    `not-norm` — `scripts/maint/data/traces.tsv`);
  • копии (`copies`, через «;») — путь существует; раздела или ключа нет — предупреждение (копию выровняли или
    сдвинули); номер строки после пути (`путь:120`) — предупреждение: строки сдвигаются, место называют разделом.
Записи `CONTRADICTIONS.md` (запись — пункт списка в разделе темы; хвост «— `канон` · ID[, ID]»):
  • id записи темы есть в таблице; id раздела «Открытое» — без строки таблицы или позицией с тем же условием
    (решённое уходит в раздел своей темы);
  • у каждой строки со статусом `позиция` есть запись; канон записи — тот же файл, что `place` таблицы (или место
    таблицы — сам раздел записи: `common/CONTRADICTIONS.md §N`);
  • id таблицы соседей «Сайт и соседи» — записи этого файла;
  • предупреждения: у строки `закрыто` запись ещё называет «Закроет»; у строки `позиция` запись не говорит, что её
    закроет; пункт раздела темы без хвоста «— канон · id».

    python3 .claude/skills/design-deep-dive/scripts/maint/canon_check.py [--canon ФАЙЛ] [--contradictions ФАЙЛ] [--json]
    python3 .claude/skills/design-deep-dive/scripts/maint/canon_check.py --selftest
Нужен PyYAML (окружение скилла или системный python3 с pyyaml): ключи YAML-файлов разбираются. Код выхода: 0 — ошибок
нет (предупреждения допустимы); 1 — есть ошибки; 2 — нет файла таблицы или записей.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import kbpaths  # noqa: E402

kbpaths.use("maint")
import refcheck  # noqa: E402

ROOT = kbpaths.repo()
KB = kbpaths.kb()
SKILL_PREFIX = kbpaths.skill().relative_to(ROOT).as_posix() + "/"   # .claude/skills/design-deep-dive/
CANON = KB / "common" / "canon.tsv"
CONTRADICTIONS = KB / "common" / "CONTRADICTIONS.md"
COLUMNS = ["norm", "place", "status", "id", "copies"]
STATUSES = ("закрыто", "позиция")
REPO_ROOTS = ("docs/", ".claude/")
ID = r"[A-Z]{2,4}-\d{2,3}"
ID_RE = re.compile(rf"^{ID}$")
LINE_SUFFIX = re.compile(r":\d+(?:\s*[–-]\s*\d+)?$")
NORM_MAX = 80                                            # тема нормы — коротко: подробности в записи и в каноне
ITEM_KEYS = ("id", "key", "name", "slug", "code")
TAIL = re.compile(rf"\s—\s((?:(?!\s—\s).)*?)\s·\s({ID}(?:\s*,\s*{ID})*)\s*$")
OPEN = "Открытое"
SKIP_SECTIONS = ("Как читать запись",)
NEIGHBOURS = "Сайт и соседи"
NOT_NORM = refcheck.load_traces("not-norm")


class Report:
    def __init__(self):
        self.items: list[dict] = []

    def add(self, severity: str, check: str, where: str, message: str):
        self.items.append({"severity": severity, "check": check, "where": where, "message": message})

    def err(self, check, where, message):
        self.add("error", check, where, message)

    def warn(self, check, where, message):
        self.add("warning", check, where, message)

    @property
    def errors(self):
        return [x for x in self.items if x["severity"] == "error"]

    @property
    def warnings(self):
        return [x for x in self.items if x["severity"] == "warning"]


# ─────────────────────────────── адреса ───────────────────────────────

def split_item(item: str) -> tuple[str, str, str]:
    """«путь §раздел» | «путь#ключ» | «путь» → (путь, раздел, ключ)."""
    s = item.strip().strip("`").strip()
    m = re.match(r"^(.*?)(?:\s*§\s*(.+)|#(.+))?$", s)
    return m.group(1).strip(), (m.group(2) or "").strip(), (m.group(3) or "").strip()


def resolve(path: str) -> Path:
    """Путь от `kb/` (префикс `kb/` допустим), `docs/…` и `.claude/…` — от корня репозитория; путь, которого нет в
    `kb/`, ищется и от корня репозитория."""
    if path.startswith(REPO_ROOTS):
        return ROOT / path
    p = KB / (path[3:] if path.startswith("kb/") else path)
    if not p.exists() and not path.startswith("kb/") and (ROOT / path).exists():
        return ROOT / path
    return p


def short_path(path: str) -> str:
    """Путь для сравнения мест: от `kb/`, у текстов скилла — от его папки."""
    p = path.strip()
    if p.startswith(SKILL_PREFIX):
        p = p[len(SKILL_PREFIX):]
    if p.startswith("kb/"):
        p = p[3:]
    return p


_DOCS: dict[Path, object] = {}


def load_doc(path: Path):
    if path not in _DOCS:
        import yaml
        text = path.read_text(encoding="utf-8")
        try:
            _DOCS[path] = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
        except Exception as e:  # noqa: BLE001 — разбор файла: любая ошибка — находка, а не падение
            _DOCS[path] = e
    return _DOCS[path]


def _item_hit(x, seg: str) -> bool:
    return isinstance(x, dict) and any(str(x.get(k)) == seg for k in ITEM_KEYS)


def walk(node, segs: list[str]) -> bool:
    """Путь ключа через точку: ключ словаря, элемент списка по id, пропущенный уровень, семейство `<имя>_*`."""
    if not segs:
        return True
    seg, rest = segs[0], segs[1:]
    if isinstance(node, dict):
        if seg in node:
            return walk(node[seg], rest)
        if not rest and any(isinstance(k, str) and k.startswith(seg + "_") for k in node):
            return True  # семейство ключей: `effects.video` — `video_autoplay_kb`, `video_first_screen_kb`
        kids = [v for v in node.values() if isinstance(v, dict)]
        # пропущенный уровень: `levels.outcome` — `outcome` каждого уровня словаря {L0: …, L1: …}
        return bool(kids) and len(kids) == len(node) and any(walk(v, segs) for v in kids)
    if isinstance(node, list):
        hits = [x for x in node if _item_hit(x, seg)]
        if hits:
            return any(walk(h, rest) for h in hits)
        return any(walk(x, segs) for x in node if isinstance(x, (dict, list)))
    return False


def anywhere(node, seg: str) -> bool:
    """Одиночный ключ — ключ словаря или id элемента где угодно в документе."""
    if isinstance(node, dict):
        return seg in node or _item_hit(node, seg) or any(anywhere(v, seg) for v in node.values())
    if isinstance(node, list):
        return any(anywhere(x, seg) for x in node)
    return False


def key_ok(path: Path, key: str) -> bool:
    if path.suffix == ".md":
        return refcheck.section_ok(path, key) or refcheck.section_ok(path, key.replace("-", " "))
    if path.suffix not in (".yaml", ".yml", ".json"):
        return key in path.read_text(encoding="utf-8")
    doc = load_doc(path)
    if isinstance(doc, Exception):
        return False
    keys = [key]
    if "…" in key:  # диапазон «EG-A11Y-05…10» — оба конца
        a, b = key.split("…", 1)
        keys = [a, a[:len(a) - len(b)] + b]
    for k in keys:
        segs = k.split(".")
        if not (walk(doc, segs) or (len(segs) == 1 and anywhere(doc, segs[0]))):
            return False
    return True


def section_range(lines: list[str], name: str) -> tuple[int, int] | None:
    """Строки раздела с заголовком, содержащим имя: от заголовка до следующего того же или более высокого уровня."""
    low = name.lower()
    for i, ln in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)", ln)
        if m and low in m.group(2).lower():
            level = len(m.group(1))
            for j in range(i + 1, len(lines)):
                mj = re.match(r"^(#{1,6})\s", lines[j])
                if mj and len(mj.group(1)) <= level:
                    return i, j
            return i, len(lines)
    return None


def section_ok(path: Path, sec: str) -> bool:
    sec = re.sub(r"\s+п\.\s*[\d–-]+\s*$", "", sec).strip()  # «§4 п. 1» — пункт внутри раздела не сверяется
    item = None
    m = re.match(r"^(.*?)\s*№\s*(\d+)$", sec)
    if m:
        sec, item = m.group(1).strip(), m.group(2)
    sec = sec.split(",")[0].split("–")[0].strip()
    if not sec:
        return True
    if not refcheck.section_ok(path, sec):
        return False
    if item and path.suffix == ".md":
        lines = path.read_text(encoding="utf-8").splitlines()
        rng = section_range(lines, sec) or (0, len(lines))
        pat = re.compile(rf"^\s*(?:\|\s*{item}\s*\||{item}\.\s)")
        return any(pat.match(x) for x in lines[rng[0]:rng[1]])
    return True


def check_address(item: str, field: str, where: str, rep: Report):
    path, sec, key = split_item(item)
    if "/" not in path:
        return  # не путь (метка, имя без папки) — не сверяется
    if LINE_SUFFIX.search(path):
        rep.warn("path", where, f"{field}: номер строки после пути «{path}» — строки сдвигаются, место называют "
                                f"разделом « §…»")
        path = LINE_SUFFIX.sub("", path)
    target = resolve(path)
    if "*" in path:
        if not list(target.parent.glob(target.name)):
            rep.err("path", where, f"{field}: по шаблону `{path}` нет файлов")
        return
    if not target.exists():
        head = path.split()[0] if path.split() else path
        if head != path and resolve(head).exists():
            rep.warn("path", where, f"{field}: после пути лишний текст: «{item.strip()}» (путь — до « §» или «#»)")
        else:
            rep.err("path", where, f"{field}: нет пути `{path}` (от {'корня' if path.startswith(REPO_ROOTS) else 'kb/'})")
        return
    # у места нормы раздел и ключ обязаны быть; у копии ушедший раздел — знак выравнивания: копию снимают из copies
    add = rep.err if field == "place" else rep.warn
    tail = "" if field == "place" else " — копию выровняли или сдвинули: поправить или снять из copies"
    if sec and target.is_file() and not section_ok(target, sec):
        add("section", where, f"{field}: в `{path}` нет раздела «{sec}»{tail}")
    if key and target.is_file() and not key_ok(target, key):
        add("section", where, f"{field}: в `{path}` нет ключа «{key}»{tail}")


# ─────────────────────────────── таблица ───────────────────────────────

def read_canon(path: Path, rep: Report) -> list[dict]:
    lines = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    name = path.name
    if not lines:
        rep.err("form", name, f"пустой файл: нужен заголовок {COLUMNS}")
        return []
    header = lines[0].split("\t")
    if header != COLUMNS:
        rep.err("form", name, f"заголовок {header} ≠ {COLUMNS}")
        return []
    rows = []
    for n, line in enumerate(lines[1:], 2):
        cells = line.split("\t")
        if len(cells) != len(COLUMNS):
            rep.err("form", f"{name}:{n}", f"{len(cells)} ячеек вместо {len(COLUMNS)} (табуляция внутри поля?)")
            continue
        row = dict(zip(COLUMNS, (c.strip() for c in cells)))
        row["_where"] = f"{name}:{n}"
        rows.append(row)
    return rows


def check_rows(rows: list[dict], rep: Report):
    ids = Counter(r["id"] for r in rows)
    topics: dict[str, set] = defaultdict(set)
    for r in rows:
        w = f"{r['_where']} {r['id']}".strip()
        for f in ("norm", "place", "status", "id"):
            if not r[f] or r[f] == "—":
                rep.err("form", w, f"пустое поле {f}")
        if r["status"] and r["status"] not in STATUSES:
            rep.err("form", w, f"status «{r['status']}» — не {' и не '.join(STATUSES)}")
        if r["id"] and not ID_RE.match(r["id"]):
            rep.err("form", w, f"id «{r['id']}» не в форме <КОД>-<номер>")
        if len(r["norm"]) > NORM_MAX:
            rep.warn("form", w, f"norm: {len(r['norm'])} знаков при норме до {NORM_MAX} — тема коротко")
        if r["id"] and ids[r["id"]] > 1:
            rep.err("id", w, f"id `{r['id']}` повторяется ({ids[r['id']]} строки)")
        places = [x.strip() for x in r["place"].split(";") if x.strip()]
        if len(places) > 1:
            rep.err("one-place", w, "place: больше одного места (одна норма — одно место)")
        if r["norm"] and r["place"]:
            topics[r["norm"].lower()].add(r["place"])
        for p in places[:1]:
            path = split_item(p)[0]
            bad = [label for label, rx in NOT_NORM if rx.search(short_path(path))]
            if bad:
                rep.err("not-norm", w, f"place `{path}` — {bad[0]}: место нормы не бывает там")
            check_address(p, "place", w, rep)
        for c in [x.strip() for x in r["copies"].split(";") if x.strip() and x.strip() != "—"]:
            check_address(c, "copies", w, rep)
    for topic, places in topics.items():
        if len(places) > 1:
            rep.err("one-place", topic[:60], f"одна тема — разные места: {'; '.join(sorted(places))}")


# ─────────────────────────────── записи ───────────────────────────────

def records(text: str) -> list[dict]:
    """Пункты списка по разделам `## …`: {sec, line, text}; продолжение пункта — строки с отступом."""
    out, sec, cur = [], None, None
    for i, ln in enumerate(text.split("\n"), 1):
        if ln.startswith("## "):
            sec, cur = ln[3:].strip(), None
            continue
        if ln.startswith("- "):
            cur = {"sec": sec, "line": i, "text": ln[2:].strip()}
            out.append(cur)
            continue
        if cur is not None and ln.startswith("  ") and ln.strip():
            cur["text"] += " " + ln.strip()
            continue
        cur = None
    return out


def neighbour_ids(text: str) -> list[tuple[int, str]]:
    """id из последней колонки таблицы раздела «Сайт и соседи»: [(строка, id)]."""
    out, inside = [], False
    for i, ln in enumerate(text.split("\n"), 1):
        if ln.startswith("## "):
            inside = ln[3:].strip() == NEIGHBOURS
            continue
        if inside and ln.startswith("|") and not re.match(r"^\|\s*-", ln):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            out += [(i, x) for x in re.findall(ID, cells[-1])]
    return out


def section_number(sec: str | None) -> str:
    m = re.match(r"^(\d+)\.", sec or "")
    return m.group(1) if m else ""


def check_records(rows: list[dict], path: Path, rep: Report):
    by_id = {r["id"]: r for r in rows}
    text = path.read_text(encoding="utf-8")
    name = path.name
    seen: dict[str, list[dict]] = defaultdict(list)
    open_ids = set()
    for rec in records(text):
        if rec["sec"] in SKIP_SECTIONS or rec["sec"] == NEIGHBOURS or rec["sec"] is None:
            continue
        where = f"{name}:{rec['line']}"
        m = TAIL.search(rec["text"])
        if not m:
            rep.warn("record", where, "пункт без хвоста «— `канон` · id»: запись не связана со строкой canon.tsv")
            continue
        canon_part, ids = m.group(1), re.findall(ID, m.group(2))
        paths = [short_path(split_item(p)[0]) for p in re.findall(r"`([^`]+)`", canon_part)]
        for i in ids:
            row = by_id.get(i)
            if rec["sec"] == OPEN:
                open_ids.add(i)
                if row is not None and row["status"] != "позиция":
                    rep.err("record", where, f"{i}: запись в «{OPEN}», а в canon.tsv строка «{row['status']}» — "
                                             f"решённое переносится в раздел своей темы")
                if row is None:
                    continue
            seen[i].append(rec)
            if row is None:
                rep.err("record", where, f"{i}: записи нет строки в canon.tsv")
                continue
            place = short_path(split_item(row["place"])[0])
            own = f"common/{name}"
            if place not in paths and not (place == own and split_item(row["place"])[1].split(".")[0].strip()
                                           == section_number(rec["sec"])):
                rep.err("record", where, f"{i}: канон записи {', '.join(f'`{p}`' for p in paths) or '—'} ≠ место "
                                         f"canon.tsv `{row['place']}`")
            if row["status"] == "закрыто" and "Закроет" in rec["text"]:
                rep.warn("record", where, f"{i}: в canon.tsv «закрыто», а запись называет «Закроет» — снять условие "
                                          f"из записи или вернуть строке статус «позиция»")
    for r in rows:
        if r["status"] == "позиция":
            recs = seen.get(r["id"], [])
            if not recs:
                rep.err("record", f"{r['_where']} {r['id']}", f"у позиции нет записи в {name}: что её подтвердит — "
                                                              f"пишется в запись")
            elif not any("Закроет" in x["text"] or "позиция" in x["text"].lower() for x in recs):
                rep.warn("record", f"{name}:{recs[0]['line']}", f"{r['id']}: позиция, а запись не говорит, что её "
                                                               f"закроет")
    known = set(by_id) | open_ids
    for line, i in neighbour_ids(text):
        if i not in known:
            rep.err("record", f"{name}:{line}", f"{i}: в таблице «{NEIGHBOURS}» — id без записи и без строки canon.tsv")


# ─────────────────────────────── запуск ───────────────────────────────

def run(canon: Path = CANON, contradictions: Path = CONTRADICTIONS) -> tuple[Report, list[dict]]:
    rep = Report()
    rows = read_canon(canon, rep)
    check_rows(rows, rep)
    check_records(rows, contradictions, rep)
    return rep, rows


def render(rep: Report, rows: list[dict], canon: Path) -> str:
    out = []
    for x in rep.warnings:
        out.append(f"  предупреждение · {x['where']}: {x['message']}")
    for x in rep.errors:
        out.append(f"  ОШИБКА · {x['where']}: {x['message']}")
    places = {r["place"] for r in rows}
    out.append(f"{canon.name}: норм {len(rows)}, мест {len(places)}; ошибок {len(rep.errors)}, "
               f"предупреждений {len(rep.warnings)}")
    return "\n".join(out)


def selftest() -> int:
    """Маленькие таблица и записи во временной папке: чистый случай и по одному посеву на каждую проверку."""
    import tempfile
    ok = fail = 0

    def ok_if(name, cond):
        nonlocal ok, fail
        print(("OK   " if cond else "FAIL ") + name)
        ok, fail = ok + bool(cond), fail + (not cond)

    head = "\t".join(COLUMNS) + "\n"
    clean_rows = [
        ("Словарь компонентов", "common/components.yaml#types", "закрыто", "GL-01", "common/glossary.md#компонент"),
        ("Старшинство источников", "common/README.md §Старшинство", "позиция", "GL-02", "—"),
        ("Слово «зона»", "common/glossary.md#зона", "закрыто", "GL-03", "—"),
        ("Таблица норм", "common/canon.tsv", "закрыто", "GL-04", "common/README.md §Как пользоваться"),
    ]
    clean_md = ("# Противоречия\n\n## Как читать запись\n\n- **Тема.** Норма. — канон · id.\n\n## Открытое\n\n"
                "- **Открытый вопрос.** Что действует до решения. Закроет: пилот. — `common/owners.md` · GL-09\n\n"
                "## 1. Общее\n\n- **Компоненты.** Словарь закрытый. — `common/components.yaml#types` · GL-01\n"
                "- **Старшинство.** Верхний источник действует. Закроет: заказчик.\n"
                "  — `common/README.md §Старшинство` · GL-02\n\n## Сайт и соседи\n\n| соседи | о чём | запись |\n"
                "|---|---|---|\n| site ↔ ux | компоненты | GL-01, GL-09 |\n")

    def case(rows, md=clean_md):
        with tempfile.TemporaryDirectory(prefix="canon_check-") as td:
            c, k = Path(td) / "canon.tsv", Path(td) / "CONTRADICTIONS.md"
            c.write_text(head + "".join("\t".join(r) + "\n" for r in rows), encoding="utf-8")
            k.write_text(md, encoding="utf-8")
            rep, _ = run(c, k)
            return rep

    def has(rep, severity, check, needle):
        return any(x["severity"] == severity and x["check"] == check and needle in x["message"] for x in rep.items)

    rep = case(clean_rows)
    ok_if("чистый случай — 0 ошибок, 0 предупреждений", not rep.items)
    r = case(clean_rows + [("Другая норма", "common/owners.md", "закрыто", "GL-01", "—")])
    ok_if("дубль id — ошибка", has(r, "error", "id", "GL-01"))
    r = case(clean_rows + [("Путь в пустоту", "common/нет-такого.md §2", "закрыто", "GL-05", "—")])
    ok_if("путь в пустоту — ошибка", has(r, "error", "path", "нет-такого.md"))
    r = case(clean_rows + [("Нет раздела", "common/README.md §Нет такого раздела", "закрыто", "GL-05", "—")])
    ok_if("нет раздела — ошибка", has(r, "error", "section", "Нет такого раздела"))
    r = case(clean_rows + [("Нет ключа", "common/components.yaml#no_such_key", "закрыто", "GL-05", "—")])
    ok_if("нет ключа — ошибка", has(r, "error", "section", "no_such_key"))
    r = case(clean_rows + [("Два места", "common/owners.md; common/judge.md", "закрыто", "GL-05", "—")])
    ok_if("два места в place — ошибка", has(r, "error", "one-place", "больше одного"))
    r = case(clean_rows + [("Словарь компонентов", "common/owners.md", "закрыто", "GL-05", "—")])
    ok_if("одна тема — два места — ошибка", has(r, "error", "one-place", "разные места"))
    r = case(clean_rows + [("Черновик", "text/99-raw/reports", "закрыто", "GL-05", "—")])
    ok_if("место в материале к разбору — ошибка", has(r, "error", "not-norm", "99-raw"))
    r = case(clean_rows + [("Статус", "common/owners.md", "открыто", "GL-05", "—")])
    ok_if("статус не из двух — ошибка", has(r, "error", "form", "открыто"))
    r = case(clean_rows + [("Тема " + "длинная " * 12, "common/owners.md", "закрыто", "GL-05", "—")])
    ok_if("тема длиннее 80 знаков — предупреждение", has(r, "warning", "form", "до 80") and not r.errors)
    r = case(clean_rows + [("Копия", "common/owners.md", "закрыто", "GL-05", "common/judge.md:12")])
    ok_if("номер строки у копии — предупреждение", has(r, "warning", "path", "номер строки"))
    r = case(clean_rows + [("Позиция без записи", "common/owners.md", "позиция", "GL-05", "—")])
    ok_if("позиция без записи — ошибка", has(r, "error", "record", "нет записи"))
    r = case(clean_rows + [("Открытое решено", "common/owners.md", "закрыто", "GL-09", "—")])
    ok_if("id «Открытого» в таблице со статусом «закрыто» — ошибка", has(r, "error", "record", "GL-09"))
    r = case(clean_rows + [("Позиция открытого вопроса", "common/owners.md", "позиция", "GL-09", "—")])
    ok_if("id «Открытого» — позиция с тем же условием — без находки", not r.items)
    r = case(clean_rows + [("Копия", "common/owners.md", "закрыто", "GL-05", "common/judge.md §Нет раздела")])
    ok_if("у копии нет раздела — предупреждение", has(r, "warning", "section", "Нет раздела") and not r.errors)
    r = case(clean_rows, clean_md.replace("`common/components.yaml#types` · GL-01", "`common/judge.md` · GL-01"))
    ok_if("канон записи ≠ place — ошибка", has(r, "error", "record", "≠ место"))
    r = case(clean_rows, clean_md.replace("· GL-01\n", "· GL-01, GL-07\n", 1))
    ok_if("id записи без строки таблицы — ошибка", has(r, "error", "record", "GL-07"))
    r = case(clean_rows, clean_md.replace("Словарь закрытый.", "Словарь закрытый. Закроет: утилита."))
    ok_if("«закрыто», а запись называет «Закроет» — предупреждение", has(r, "warning", "record", "Закроет"))
    r = case(clean_rows, clean_md.replace("GL-01, GL-09 |", "GL-01, GL-08 |"))
    ok_if("таблица соседей: id без записи — ошибка", has(r, "error", "record", "GL-08"))
    r = case([("Бюджет", "site/07-seo-geo-performance-analytics/budgets.yaml#levels.outcome.lcp_ms_lab", "закрыто",
               "GL-05", "—")], "# П\n")
    ok_if("ключ с пропущенным уровнем (levels.<уровень>.outcome) — есть", not r.errors)
    print(f"selftest: {ok} OK, {fail} FAIL")
    return 0 if not fail else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--canon", type=Path, default=CANON, help="таблица «норма → место» (по умолчанию kb/common/canon.tsv)")
    ap.add_argument("--contradictions", type=Path, default=CONTRADICTIONS,
                    help="записи противоречий (по умолчанию kb/common/CONTRADICTIONS.md)")
    ap.add_argument("--json", action="store_true", help="находки JSON в stdout")
    ap.add_argument("--selftest", action="store_true", help="самопроверка во временной папке, без сети")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    for p in (a.canon, a.contradictions):
        if not p.is_file():
            print(f"нет файла {p}", file=sys.stderr)
            return 2
    rep, rows = run(a.canon, a.contradictions)
    if a.json:
        print(json.dumps({"norms": len(rows), "errors": len(rep.errors), "warnings": len(rep.warnings),
                          "findings": rep.items}, ensure_ascii=False, indent=1))
    else:
        print(render(rep, rows, a.canon))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
