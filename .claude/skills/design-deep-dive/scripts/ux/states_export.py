#!/usr/bin/env python3
"""Экспорт словаря состояний экрана и матрицы «экран или компонент × состояние» в YAML.

Читает `06-feedback-states-motion/01-state-matrix.md` базы ux — таблицы групп §2.1–§2.4 (строка `| **S01** | `slug` |
когда | обязательность | что показать | что предложить | как проверить |`), таблицу приоритета §2.5 и сводную матрицу §3.1
с заголовками разборов §3.2 и дальше — и пишет `06-feedback-states-motion/screen-states.yaml`. Канон — Markdown; YAML
производный, руками не правится: правка — в Markdown, затем перегенерация.

Форма YAML:
  states: <id> → key (slug — ключ `states` экрана), group (название группы §2), section, obligation (base | by-type),
          scope (условие обязательности словами источника), when, show, offer, check;
  groups: название, раздел, состояния в порядке таблицы;
  priority: какое состояние показывать, когда их несколько (по убыванию); overlays — те, что накладываются поверх
          содержимого, а не заменяют его;
  matrix: <ключ строки> → title (как в §3.1), required, by_type, notes (пояснение к id в скобках), specific,
          detail (раздел развёрнутого разбора строки, если он есть).
Ключ строки матрицы — постоянное имя, на него ссылаются `kb/common/components.yaml` (`screen_states`) и утилиты экранов;
новая строка §3.1 требует ключа в ROW_KEYS, иначе экспорт останавливается с ошибкой.

Запуск (из любой папки):
  python3 states_export.py            # записать YAML и напечатать сводку
  python3 states_export.py --check    # YAML совпадает с Markdown байт в байт? Ничего не пишет; код 1 — нет
  python3 states_export.py --selftest # самопроверка разбора на встроенном примере
  python3 states_export.py --md FILE --out FILE   # другой источник и выход
Коды выхода: 0 — готово или совпадает; 1 — YAML устарел или в источнике ошибки; 2 — нет файла источника.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import kbpaths  # noqa: E402

BASE = kbpaths.kb("ux")
MD_REL = "06-feedback-states-motion/01-state-matrix.md"
OUT_REL = "06-feedback-states-motion/screen-states.yaml"
SCRIPT_REL = "../../scripts/ux/states_export.py"   # путь генератора от корня базы — для шапки YAML

# Ключи строк матрицы §3.1: название строки → постоянное имя.
ROW_KEYS = {
    "Список и таблица": "list-table",
    "Карточка объекта": "object",
    "Дашборд и плитка показателя": "dashboard-tile",
    "Форма": "form",
    "Поиск": "search",
    "Уведомления (лента, центр)": "notifications",
    "Файл и вложение": "file",
    "Настройки": "settings",
    "Экран или маршрут целиком": "route",
    "Мастер и многошаговый процесс": "wizard",
    "Экспорт и импорт": "export-import",
}

ID_RE = re.compile(r"^S\d{2}$")
H2 = re.compile(r"^## (\d+)\. ")
H3 = re.compile(r"^### (\d+)\.(\d+)\. (.+?)\s*$")
GROUP_HEAD = re.compile(r"^Группа «(.+)»$")
STATE_ROW = re.compile(r"^\|\s*\*\*(S\d{2})\*\*\s*\|\s*`([a-z0-9-]+)`\s*\|(.*)\|\s*$")
PRIO_ITEM = re.compile(r"^\d+\.\s+\*\*(S\d{2})\b[^*]*\*\*\s*\.?\s*(?:—\s*(.*))?$")
MATRIX_ROW = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|(.*)\|\s*$")


def q(s):
    return json.dumps(s, ensure_ascii=False)


def clean(cell):
    """Текст ячейки без выделения полужирным и лишних пробелов; код в бэктиках остаётся."""
    return re.sub(r"\s+", " ", cell.replace("**", "")).strip()


def split_cells(body):
    return [c.strip() for c in body.split("|")]


def split_top(s):
    """Разбить список «S07 (загрузка справочников), S11» по запятым вне скобок."""
    out, depth, cur = [], 0, ""
    for ch in s:
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [x.strip() for x in out if x.strip()]


def parse_obligation(cell):
    """«база», «база для форм…», «по типу (очереди…)», «по типу» → (base | by-type, условие)."""
    c = clean(cell)
    if c.startswith("база"):
        rest = c[len("база"):].strip()
        return "base", re.sub(r"^для\s+", "", rest)
    if c.startswith("по типу"):
        m = re.search(r"\((.*)\)\s*$", c)
        return "by-type", (m.group(1).strip() if m else "")
    raise ValueError(f"обязательность «{c}»: ждём «база…» или «по типу…»")


def parse_ids(cell, errors, where):
    ids, notes = [], {}
    for item in split_top(clean(cell)):
        m = re.match(r"^(S\d{2})\s*(?:\((.+)\))?$", item)
        if not m:
            errors.append(f"{where}: не id состояния «{item}»")
            continue
        ids.append(m.group(1))
        if m.group(2):
            notes[m.group(1)] = m.group(2).strip()
    return ids, notes


def parse(text):
    """Markdown → {'states', 'groups', 'priority', 'overlays', 'matrix', 'errors'}."""
    states, groups, priority, overlays = {}, [], [], []
    rows, details, errors = [], [], []
    sec2 = sec3 = None
    group = None
    for ln in text.split("\n"):
        m = H2.match(ln)
        if m:
            sec2, sec3, group = int(m.group(1)), None, None
            continue
        m = H3.match(ln)
        if m:
            sec3 = (int(m.group(1)), int(m.group(2)))
            group = None
            if sec2 == 2:
                g = GROUP_HEAD.match(m.group(3))
                if g:
                    group = {"title": g.group(1), "section": f"{sec3[0]}.{sec3[1]}", "states": []}
                    groups.append(group)
            elif sec2 == 3 and sec3[1] >= 2:
                details.append((f"{sec3[0]}.{sec3[1]}", m.group(3).split(":", 1)[0]))
            continue
        if sec2 == 2 and group is not None:
            m = STATE_ROW.match(ln)
            if m:
                sid, key, rest = m.group(1), m.group(2), split_cells(m.group(3))
                if len(rest) != 5:
                    errors.append(f"{sid}: {len(rest) + 2} колонок вместо 7")
                    continue
                try:
                    obligation, scope = parse_obligation(rest[1])
                except ValueError as e:
                    errors.append(f"{sid}: {e}")
                    continue
                if sid in states:
                    errors.append(f"{sid}: повтор id")
                states[sid] = {"key": key, "group": group["title"], "section": group["section"],
                               "obligation": obligation, "scope": scope, "when": clean(rest[0]),
                               "show": clean(rest[2]), "offer": clean(rest[3]), "check": clean(rest[4])}
                group["states"].append(sid)
            continue
        if sec2 == 2 and sec3 == (2, 5):
            m = PRIO_ITEM.match(ln.strip())
            if m:
                (overlays if "накладывается" in (m.group(2) or "") else priority).append(m.group(1))
            continue
        if sec2 == 3 and sec3 == (3, 1):
            m = MATRIX_ROW.match(ln)
            if m:
                title, cells = clean(m.group(1)), split_cells(m.group(2))
                if len(cells) != 3:
                    errors.append(f"строка матрицы «{title}»: {len(cells) + 1} колонок вместо 4")
                    continue
                req, n1 = parse_ids(cells[0], errors, title)
                opt, n2 = parse_ids(cells[1], errors, title)
                rows.append({"title": title, "required": req, "by_type": opt, "notes": {**n1, **n2},
                             "specific": clean(cells[2]), "detail": ""})
    matrix = {}
    for r in rows:
        key = ROW_KEYS.get(r["title"])
        if not key:
            errors.append(f"строка матрицы «{r['title']}» без ключа: добавь её в ROW_KEYS генератора")
            continue
        matrix[key] = r
    for section, names in details:
        for name in [n.strip() for n in names.split(",") if n.strip()]:
            hits = [r for r in rows if r["title"].lower().startswith(name.lower())]
            if len(hits) != 1:
                errors.append(f"разбор §{section}: «{name}» не находит одну строку матрицы")
                continue
            hits[0]["detail"] = section
    return {"states": states, "groups": groups, "priority": priority, "overlays": overlays, "matrix": matrix,
            "errors": errors}


def validate(d):
    errors = list(d["errors"])
    ids = set(d["states"])
    keys = [s["key"] for s in d["states"].values()]
    for sid in ids:
        if not ID_RE.match(sid):
            errors.append(f"{sid}: id не по форме S<NN>")
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        errors.append(f"повтор ключей: {', '.join(dup)}")
    if not d["states"]:
        errors.append("в §2 не найдено ни одного состояния")
    for g in d["groups"]:
        if not g["states"]:
            errors.append(f"группа «{g['title']}» без состояний")
    if not d["priority"]:
        errors.append("§2.5: приоритет не найден")
    for sid in d["priority"] + d["overlays"]:
        if sid not in ids:
            errors.append(f"§2.5: {sid} нет в словаре")
    for key, r in d["matrix"].items():
        for sid in r["required"] + r["by_type"]:
            if sid not in ids:
                errors.append(f"§3.1 «{r['title']}»: {sid} нет в словаре")
        both = sorted(set(r["required"]) & set(r["by_type"]))
        if both:
            errors.append(f"§3.1 «{r['title']}»: {', '.join(both)} и в обязательных, и по типу")
    return errors


def render(d, sha16):
    out = [f"# Машиночитаемая версия {MD_REL} §2–§3: словарь состояний экрана и матрица «экран или компонент × состояние».",
           f"# Сгенерировано скриптом {SCRIPT_REL} — правки вносить в Markdown и перегенерировать.",
           f"source_md: {q(MD_REL)}",
           f"source_sha256_16: {q(sha16)}",
           f"states_count: {len(d['states'])}",
           "obligation: {base: " + q("база — обязательно у экрана с данными; scope, если есть, сужает круг экранов")
           + ", by-type: " + q("по типу — обязательно, если экран подходит под scope и условие when") + "}",
           "groups:"]
    for g in d["groups"]:
        out.append(f"  - {{title: {q(g['title'])}, section: {q(g['section'])}, states: [{', '.join(g['states'])}]}}")
    out.append("states:")
    for sid, s in d["states"].items():
        out.append(f"  {sid}:")
        out.append(f"    key: {s['key']}")
        out.append(f"    group: {q(s['group'])}")
        out.append(f"    section: {q(s['section'])}")
        out.append(f"    obligation: {s['obligation']}")
        out.append(f"    scope: {q(s['scope'])}")
        for k in ("when", "show", "offer", "check"):
            out.append(f"    {k}: {q(s[k])}")
    out.append(f"priority: [{', '.join(d['priority'])}]")
    out.append(f"overlays: [{', '.join(d['overlays'])}]")
    out.append("matrix:")
    for key, r in d["matrix"].items():
        out.append(f"  {key}:")
        out.append(f"    title: {q(r['title'])}")
        out.append(f"    required: [{', '.join(r['required'])}]")
        out.append(f"    by_type: [{', '.join(r['by_type'])}]")
        if r["notes"]:
            out.append("    notes: {" + ", ".join(f"{k}: {q(v)}" for k, v in r["notes"].items()) + "}")
        out.append(f"    specific: {q(r['specific'])}")
        if r["detail"]:
            out.append(f"    detail: {q(r['detail'])}")
    return "\n".join(out) + "\n"


def build(md_path):
    text = io.open(md_path, encoding="utf-8").read()
    d = parse(text)
    return d, validate(d), render(d, hashlib.sha256(text.encode("utf-8")).hexdigest()[:16])


def check_yaml(text):
    try:
        import yaml
    except ImportError:
        return "PyYAML не установлен — разбор YAML не проверен"
    try:
        y = yaml.safe_load(text)
        return f"YAML разбирается: состояний {len(y['states'])}, строк матрицы {len(y['matrix'])}"
    except Exception as e:  # noqa: BLE001
        return f"ОШИБКА YAML: {e}"


SAMPLE = """# Пример

## 2. Закрытый список состояний

### 2.1. Группа «данные»

| ID | Слаг | Когда возникает | Обяз. | Что показать | Что предложить | Как проверить |
|---|---|---|---|---|---|---|
| **S01** | `empty-first-run` | Объектов ещё нет | база | Что здесь будет | Главное действие | Пустой массив |
| **S02** | `empty-filtered` | Фильтр пуст | база для списков и поиска | Что искали | Сбросить | Пустой фильтр |

### 2.2. Группа «процесс»

| ID | Слаг | Когда возникает | Обяз. | Что показать | Что предложить | Как проверить |
|---|---|---|---|---|---|---|
| **S07** | `loading-initial` | Первый показ | база | Скелетон | **Ничего** | Задержка 3 с |
| **S24** | `generating` | Поток ИИ | по типу (блок с ответом ИИ) | Признак | Остановку | Задержать поток |

### 2.4. Группа «доступ и правила»

| ID | Слаг | Когда возникает | Обяз. | Что показать | Что предложить | Как проверить |
|---|---|---|---|---|---|---|
| **S23** | `not-found` | Объекта нет | по типу (маршрут объекта: параметр) | Что искали | Выход | Несуществующий ключ |

### 2.5. Таблица приоритета

1. **S23 объекта нет** — объясняет.
2. **S07 загрузка** — пока идёт.
3. **S02 пусто после фильтра**.
4. **S01 пусто с самого начала**.
5. **S24 поток** — накладывается поверх ответа.

## 3. Матрица

### 3.1. Сводная таблица

| Экран / компонент | Обязательные | По типу | Что специфично |
|---|---|---|---|
| **Список и таблица** | S01, S02, S07 | S24 | Пустое **заменяет** таблицу |
| **Форма** | S07 (загрузка справочников) | S23 | Поля — §7.2 |

### 3.2. Список и таблица: развёрнуто

### 3.4. Форма: что специфично

## 4. Дальше
"""


def selftest():
    res = []

    def check(name, cond):
        res.append((bool(cond), name))
        print(f"{'PASS' if cond else 'FAIL'} {name}")

    d = parse(SAMPLE)
    errs = validate(d)
    check("пять состояний в порядке групп", list(d["states"]) == ["S01", "S02", "S07", "S24", "S23"])
    check("группа и раздел", d["states"]["S23"]["group"] == "доступ и правила" and d["states"]["S23"]["section"] == "2.4")
    check("обязательность «база для…»", (d["states"]["S02"]["obligation"], d["states"]["S02"]["scope"])
          == ("base", "списков и поиска"))
    check("обязательность «по типу (…)»", (d["states"]["S23"]["obligation"], d["states"]["S23"]["scope"])
          == ("by-type", "маршрут объекта: параметр"))
    check("полужирный снят", d["states"]["S07"]["offer"] == "Ничего")
    check("приоритет и наложение", d["priority"] == ["S23", "S07", "S02", "S01"] and d["overlays"] == ["S24"])
    check("строки матрицы по ключам", list(d["matrix"]) == ["list-table", "form"])
    check("пояснение к id в скобках", d["matrix"]["form"]["notes"] == {"S07": "загрузка справочников"}
          and d["matrix"]["form"]["required"] == ["S07"])
    check("разборы §3.2 и §3.4", d["matrix"]["list-table"]["detail"] == "3.2" and d["matrix"]["form"]["detail"] == "3.4")
    check("ошибок в примере нет", not errs)
    bad = parse(SAMPLE.replace("| **Форма** | S07 (загрузка справочников) | S23 |", "| **Форма** | S07 | S99 |"))
    check("неизвестный id в матрице — ошибка", any("S99" in e for e in validate(bad)))
    bad = parse(SAMPLE.replace("**Форма**", "**Отчёт**"))
    check("строка без ключа — ошибка", any("ROW_KEYS" in e for e in validate(bad)))
    bad = parse(SAMPLE.replace("| база для списков и поиска |", "| иногда |"))
    check("непонятная обязательность — ошибка", any("S02" in e for e in validate(bad)))
    y = render(d, "0" * 16)
    check("YAML разбирается", check_yaml(y).startswith("YAML разбирается") or "не установлен" in check_yaml(y))
    try:
        import yaml
        data = yaml.safe_load(y)
        check("YAML: ключ, группа, приоритет, матрица", data["states"]["S24"]["key"] == "generating"
              and data["priority"][0] == "S23" and data["matrix"]["form"]["by_type"] == ["S23"])
    except ImportError:
        pass
    with tempfile.TemporaryDirectory(prefix="states-export-") as tmp:
        md, out = os.path.join(tmp, "m.md"), os.path.join(tmp, "s.yaml")
        io.open(md, "w", encoding="utf-8").write(SAMPLE)
        check("запись и --check совпадают", main(["--md", md, "--out", out, "--quiet"]) == 0
              and main(["--md", md, "--out", out, "--check", "--quiet"]) == 0)
        io.open(out, "a", encoding="utf-8").write("# правка руками\n")
        check("--check ловит расхождение", main(["--md", md, "--out", out, "--check", "--quiet"]) == 1)
    print(f"итог: {sum(ok for ok, _ in res)}/{len(res)} PASS")
    return 0 if all(ok for ok, _ in res) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--md", default=str(BASE / MD_REL), help="источник Markdown")
    ap.add_argument("--out", default=str(BASE / OUT_REL), help="производный YAML")
    ap.add_argument("--check", action="store_true", help="сравнить YAML с Markdown байт в байт, ничего не писать")
    ap.add_argument("--selftest", action="store_true", help="самопроверка на встроенном примере")
    ap.add_argument("--quiet", action="store_true", help="без сводки")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not os.path.isfile(a.md):
        print(f"нет файла источника: {a.md}", file=sys.stderr)
        return 2
    d, errors, text = build(a.md)
    for e in errors:
        print("ОШИБКА", e)
    if a.check:
        if not os.path.isfile(a.out):
            print(f"нет файла {a.out}: перегенерировать (states_export.py)")
            return 1
        same = io.open(a.out, encoding="utf-8").read() == text
        if not a.quiet:
            print("YAML совпадает с Markdown" if same else "YAML УСТАРЕЛ: перегенерировать (states_export.py)")
        return 0 if same and not errors else 1
    if errors:
        print("YAML не записан: в источнике ошибки")
        return 1
    io.open(a.out, "w", encoding="utf-8").write(text)
    if not a.quiet:
        print(f"{a.out}: состояний {len(d['states'])}, групп {len(d['groups'])}, строк матрицы {len(d['matrix'])}; "
              f"приоритет {' > '.join(d['priority'])}, поверх — {', '.join(d['overlays'])}; {check_yaml(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
