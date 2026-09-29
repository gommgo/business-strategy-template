#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ux_dict_to_yaml.py — словарь запретов ux 07/06 и длины по ролям ux 07/01 §12 → производный YAML для copy_lint.py.

Канон словаря — ux/07-ux-writing/06-banned-words-and-patterns.md (таблицы §1–§6, формат правила §7.1, роли §7.2);
канон длин — таблица ux/07-ux-writing/01-principles-voice-and-tone.md §12. Выход —
kb/text/06-anti-slop/lexicon/ux-07-06.yaml: файл собирает этот конвертер, руками он не правится. Поправки для жанров
сайта — `overrides` с полем `genres` в 06-anti-slop/lexicon/marketing-role.yaml; в жанре `interface` правила ux
действуют с уровнями канона.

Что делает:
- находит в разделах §1–§6 таблицы с колонкой регулярного выражения («Regex», «Regex-приближение»); шаблон — первый
  `…` ячейки, роли — `…` после слов «роли», «ролей», исключения — «кроме `…`», «вне узлов роли `…`»; роли — закрытый
  список §7.2 источника и `body`;
- уровень: колонка «Уровень», слово в ячейке («уровень `предупреждение`») или строка раздела «Уровень — запрет»;
- делает шаблон переносимым между Python `re` и ECMAScript с флагом `u`: `\\w` и `\\W` — классом букв и цифр с
  кириллицей, `\\b` — просмотром по тому же классу, `\\d` — `[0-9]`; в классах кириллицы есть «Ё» и «ё»; флаг `i`
  снимается у шаблона с классом только из заглавных;
- ячейка с оговоркой в скобках, которую шаблон канона не выражает («о действии», «кроме аббревиатур», «в причинном
  значении»), получает шаблон с оговоркой (таблица QUALIFIED); оговорка места «как название», «как раздел» — роли
  названий (NAMING); правило несёт `note` с причиной;
- строки §6.5 о пробелах — правила набора H (08-russian-legal-typography/typography-rules.yaml): в словарь не идут, в
  файле — раздел `delegated`;
- ячейки без регулярного выражения («не regex», «сравнение стилей…») → `kind: manual`: линтер их не исполняет, они
  остаются в каталоге как ручные проверки;
- id: `ux-<раздел>-<nn>`; `marker_id`: `ux:07-06#<раздел>`; группа UX;
- таблицу §12 переводит в раздел `role_lengths`: у роли — варианты границ по элементам таблицы (слова, предложения,
  знаки; строки — проверка макета), у предложения — предел слов в интерфейсе и в пояснениях.

Запуск:
  ux_dict_to_yaml.py [--src PATH] [--lengths-src PATH] [--out PATH]   # собрать файл
  ux_dict_to_yaml.py --check      # сверка байт в байт без записи: код 3 — файл устарел
  ux_dict_to_yaml.py --selftest   # разбор, роли, длины и переносимость шаблонов: Python и Node на кириллице
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("text")
SRC = kbpaths.kb("ux", "07-ux-writing", "06-banned-words-and-patterns.md")
LENGTHS_SRC = kbpaths.kb("ux", "07-ux-writing", "01-principles-voice-and-tone.md")
OUT = ROOT / "06-anti-slop" / "lexicon" / "ux-07-06.yaml"
TOOL = "scripts/text/ux_dict_to_yaml.py"

INTERFACE_EXCLUDES = ["marketing", "help", "user-content"]
ROLES_SECTION = "7.2. Роли узлов"
LENGTHS_SECTION = "12. Длина текстов по компонентам"

# раздел → (язык, уровень по умолчанию или None, appliesTo по умолчанию, excludes по умолчанию)
SECTION_DEFAULTS = {
    "1": ("ru", None, ["label", "action", "error", "status", "hint", "empty", "confirm-title", "confirm-body"],
          INTERFACE_EXCLUDES),
    "2.1": ("ru", None, [], INTERFACE_EXCLUDES),
    "2.2": ("ru", None, [], INTERFACE_EXCLUDES),
    "2.3": ("ru", None, ["body", "hint", "empty"], INTERFACE_EXCLUDES),
    "2.4": ("ru", "warning", [], INTERFACE_EXCLUDES),
    "3.1": ("ru", None, [], INTERFACE_EXCLUDES),
    "3.2": ("ru", None, [], INTERFACE_EXCLUDES),
    "3.3": ("ru", None, [], INTERFACE_EXCLUDES),
    "3.4": ("ru", None, [], INTERFACE_EXCLUDES),
    "3.5": ("ru", "error", ["action", "link", "checkbox-label", "label", "confirm-title", "confirm-body"], ["user-content"]),
    "3.6": ("ru", "error", ["action", "link", "checkbox-label", "label", "confirm-title", "confirm-body"], ["user-content"]),
    "3.7": ("ru", None, [], INTERFACE_EXCLUDES),
    "4.1": ("en", None, [], INTERFACE_EXCLUDES),
    "4.2": ("en", "warning", [], INTERFACE_EXCLUDES),
    "5.1": ("any", "error", [], ["user-content"]),
    "5.2": ("any", "error", [], ["user-content"]),
    "5.3": ("any", None, [], ["user-content"]),
    "6.4": ("ru", "error", [], INTERFACE_EXCLUDES),
    "6.5": ("any", "error", [], []),
}
LEVEL_MAP = {"запрет": "error", "предупреждение": "warning"}
MARKER_HINTS = {"5.1": "COPY-M-ART-04", "5.2": "COPY-M-CNT-02", "6.5": "COPY-M-ART-05"}

# Ячейки, где текст канона сужает шаблон оговоркой, а шаблон её не выражает: (раздел, шаблон канона) → (шаблон с
# оговоркой, причина). Когда шаблон ячейки выражает оговорку сам, строка таблицы не нужна: --selftest называет
# неиспользованные.
QUALIFIED = {
    ("2.1", r"(?<![А-Яа-яЁё])производ[иия]\w*"): (
        r"(?<![А-Яа-яЁё])производ(?:ить|ит|ят|ится|ятся|ил|ила|или|ило|имый|имая|имое|имые)(?![А-Яа-яЁё])",
        "«о действии» — формы глагола «производить»: «производитель», «производительность» — не канцелярит"),
    ("6.4", r":\s+[А-ЯЁ]"): (
        r":\s+[А-ЯЁ](?![А-ЯЁ])",
        "«кроме аббревиатур»: «Оплата: СБП» — не заглавная буква после двоеточия"),
    ("4.2", r"\bsince\b"): (
        r"\bsince\b(?!\s+\d)",
        "«в причинном значении»: «since 2014» — время, а не причина"),
}
# Оговорка первой ячейки о месте строки («Список (как название)», «Услуги (как раздел)»): правило — для ролей
# названий, а не для любой строки, где слово стоит первым («Список заявок не загрузился» — сообщение).
NAMING = {"(как название)": ["title", "subtitle", "section-title", "nav", "tab"],
          "(как раздел)": ["title", "section-title", "nav", "tab"]}
# Строки §6.5 о пробелах — правила набора H: одно правило — одно место (typography-rules.yaml). Ячейка, которая
# называет id правила H (`typo-…`), делегируется по нему.
DELEGATED = {"  +": "typo-double-space", r"\s+[,.;:!?]": "typo-space-before-punct",
             r"[,.;:!?][А-Яа-яA-Za-z]": "typo-no-space-after-punct"}
H_TYPO_RE = re.compile(r"^typo-[a-z0-9-]+$")

# Таблица §12 называет элементы интерфейса, а не роли: элемент → роли 07/06 §7.2. Колонка «роль» таблицы, если она
# есть, сильнее этого соответствия.
ELEMENT_ROLES = {
    "кнопка": ["action"], "ссылка": ["link"], "подпись поля": ["label"], "подсказка под полем": ["hint"],
    "плейсхолдер": ["placeholder"], "заголовок экрана": ["title"], "заголовок секции": ["section-title"],
    "вкладка": ["tab"], "пункт меню": ["nav"], "заголовок колонки таблицы": ["column-header"],
    "статус, бейдж": ["status", "badge"], "заголовок подтверждения": ["confirm-title"],
    "тело подтверждения": ["confirm-body"], "сообщение об ошибке поля": ["error"], "тост": ["toast"],
    "баннер": ["banner"], "заголовок пустого состояния": ["empty"], "пояснение пустого состояния": ["empty"],
    "тултип": ["tooltip"], "описание настройки": ["setting-description"], "push": ["push"],
    "абзац развёрнутого текста": ["body", "help", "email"],
}
# «Тема письма» — часть роли `email` (у темы своей роли в §7.2 нет): предел знаков темы к телу письма не относится.
ELEMENT_SKIP = {"тема письма": "у темы письма нет своей роли в §7.2: предел относится к части роли email"}
SENTENCE_ELEMENT = "предложение"
# «≤ 20 в пояснениях» — роли развёрнутых и поясняющих текстов
EXPLANATORY_ROLES = ["body", "help", "email", "hint", "empty", "banner", "confirm-body", "tooltip",
                     "setting-description", "inline-message"]

WORD_CLASS = "A-Za-zА-Яа-яЁё0-9_"


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    cells, cur, i = [], [], 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("\\|")
            i += 2
            continue
        if ch == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def backticks(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def unescape_md(p: str) -> str:
    return p.replace("\\|", "|")


def section_text(text: str, title: str) -> str:
    """Текст раздела `## …`/`### …` с заголовком title (до следующего заголовка того же или старшего уровня)."""
    lines = text.split("\n")
    out, level = [], None
    for line in lines:
        m = re.match(r"^(#{2,4})\s+(.*?)\s*$", line)
        if m:
            if level is not None and len(m.group(1)) <= level:
                break
            if m.group(2).strip() == title:
                level = len(m.group(1))
                continue
        if level is not None:
            out.append(line)
    return "\n".join(out)


def ux_roles(text: str) -> list[str]:
    """Закрытый список ролей §7.2 источника и `body` — связный текст без своей роли."""
    roles = []
    for line in section_text(text, ROLES_SECTION).split("\n"):
        s = line.strip()
        if s.startswith("`") and "·" in s:
            roles += [r for r in re.findall(r"`([a-z-]+)`", s) if r not in roles]
    if "body" not in roles:
        roles.append("body")
    return roles


def portable(pat: str) -> str:
    """Шаблон, который одинаково работает в Python `re` и ECMAScript с флагом `u`."""
    w_cls, out, i = WORD_CLASS, [], 0
    boundary = f"(?:(?<=[{w_cls}])(?![{w_cls}])|(?<![{w_cls}])(?=[{w_cls}]))"
    while i < len(pat):
        ch = pat[i]
        if ch == "\\" and i + 1 < len(pat):
            nx = pat[i + 1]
            out.append({"w": f"[{w_cls}]", "W": f"[^{w_cls}]", "b": boundary, "d": "[0-9]"}.get(nx, pat[i:i + 2]))
            i += 2
            continue
        if ch == "[":
            j, body = i + 1, []
            if j < len(pat) and pat[j] == "^":
                body.append("^")
                j += 1
            if j < len(pat) and pat[j] == "]":
                body.append("]")
                j += 1
            while j < len(pat) and pat[j] != "]":
                if pat[j] == "\\" and j + 1 < len(pat):
                    body.append({"w": w_cls, "d": "0-9"}.get(pat[j + 1], pat[j:j + 2]))
                    j += 2
                    continue
                body.append(pat[j])
                j += 1
            cls = "".join(body)
            if "А-Я" in cls and "Ё" not in cls:
                cls = cls.replace("А-Я", "А-ЯЁ", 1)
            if "а-я" in cls and "ё" not in cls:
                cls = cls.replace("а-я", "а-яё", 1)
            out.append("[" + cls + "]")
            i = j + 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def case_sensitive(pat: str) -> bool:
    """Класс только с заглавными ([A-ZА-ЯЁ]): с флагом i он ловил бы и строчные («Мы — », «в Сормове: ремонт»)."""
    return any(("A-Z" in cls or "А-Я" in cls) and "a-z" not in cls and "а-я" not in cls
               for cls in re.findall(r"\[([^\]]+)\]", pat))


def roles_from(cell: str, known: list[str]) -> tuple[list[str], list[str]]:
    applies, excludes = [], []
    m = re.search(r"вне\s+узлов\s+рол\w*\s+(.*)$", cell)
    if m:
        excludes = [r for r in backticks(m.group(1)) if r in known]
        return applies, excludes
    m = re.search(r"кроме\s+(.*)$", cell)
    if m:
        excludes = [r for r in backticks(m.group(1)) if r in known]
    m = re.search(r"рол(?:и|ей)\s+(.*)$", cell)
    if m and "вне" not in cell:
        for r in backticks(m.group(1)):
            if r == "confirm":
                applies += ["confirm-title", "confirm-body"]
            elif r in known:
                applies.append(r)
    return applies, excludes


def convert(src_text: str) -> dict:
    known = ux_roles(src_text)
    lines = src_text.split("\n")
    rules, manual, delegated = [], [], []
    sec = ""
    sec_level_all = None
    header = None
    counters: dict = {}
    used_qualified = set()
    for idx, line in enumerate(lines, 1):
        m = re.match(r"^(#{2,3})\s+(\d+(?:\.\d+)?)\.\s+(.*)$", line)
        if m:
            sec = m.group(2)
            header = None
            sec_level_all = None
            continue
        if re.match(r"^##\s+[^\d]", line):
            sec = ""
            header = None
            continue
        if not sec or sec.split(".")[0] not in ("1", "2", "3", "4", "5", "6"):
            continue
        low = line.lower()
        if "уровень —" in low or "уровень -" in low:
            if "запрет" in low:
                sec_level_all = "error"
            elif "предупреждение" in low:
                sec_level_all = "warning"
        if sec == "2.4" and "regex-приближение" in low:
            continue
        if sec == "2.4" and line.strip().startswith("`(") and line.strip().endswith("`"):
            pat = unescape_md(backticks(line)[0])
            rules.append(("2.4", idx, "цепочка родительных падежей (3+ существительных)", pat, "warning",
                          "«Отчёт о движении средств» — разбить цепочку", [], [], None))
            continue
        if not line.strip().startswith("|"):
            header = None
            continue
        cells = split_row(line)
        if re.match(r"^\|?\s*-{3,}", line.strip()) or all(re.fullmatch(r":?-{3,}:?", c or "---") for c in cells):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        cols = header
        rx_i = next((i for i, h in enumerate(cols) if h.startswith("regex")), None)
        if rx_i is None or rx_i >= len(cells):
            continue
        lvl_i = next((i for i, h in enumerate(cols) if h.startswith("уровень")), None)
        rep_i = next((i for i, h in enumerate(cols) if h in ("чем заменить", "замена", "use this")), None)
        word = cells[0]
        rx_cell = cells[rx_i]
        bts = backticks(rx_cell)
        level = None
        if lvl_i is not None and lvl_i < len(cells):
            level = LEVEL_MAP.get(cells[lvl_i].strip().lower())
        lvl_txt = re.search(r"уровень\s+`?(предупреждение|запрет)`?", rx_cell)
        if lvl_txt:
            level = LEVEL_MAP[lvl_txt.group(1)]
        dflt = SECTION_DEFAULTS.get(sec, ("ru", None, [], INTERFACE_EXCLUDES))
        level = level or sec_level_all or dflt[1] or "warning"
        if sec == "2.2" and word.startswith("данный"):
            level = "warning"
        repl = cells[rep_i] if rep_i is not None and rep_i < len(cells) else ""
        typo = next((b for b in bts if H_TYPO_RE.match(b)), None)
        pat0 = unescape_md(bts[0]) if bts else ""
        if typo or (sec == "6.5" and pat0 in DELEGATED):
            delegated.append({"section": sec, "row": word.strip("*"), "to": typo or DELEGATED[pat0],
                              "source": f"ux 07/06 §{sec} (стр. {idx})"})
            continue
        lead = rx_cell.split("`", 1)[0].strip().lower()
        role_first = bool(bts) and bts[0] in known and lead and not lead.startswith("подсчёт")
        if not bts or role_first or "не regex" in rx_cell or "сравнение" in rx_cell.lower() \
                or rx_cell.startswith("текстовый"):
            manual.append((sec, idx, word, rx_cell, level, repl))
            continue
        pat = pat0
        note = ""
        fix = QUALIFIED.get((sec, pat))
        if fix:
            pat, note = fix
            used_qualified.add((sec, pat0))
        applies, excludes = roles_from(rx_cell, known)
        naming = next((q for q in NAMING if q in word), None)
        if naming and not applies:
            applies = list(NAMING[naming])
            note = (note + "; " if note else "") + f"«{naming.strip('()')}» — роли названий"
        count = None
        if rx_cell.strip().startswith("подсчёт"):
            count = 2
        rules.append((sec, idx, word, (pat, note), level, repl, applies, excludes, count))
    out_rules = []
    for sec, idx, word, pat_note, level, repl, applies, excludes, count in rules:
        pat, note = pat_note if isinstance(pat_note, tuple) else (pat_note, "")
        n = counters.get(sec, 0) + 1
        counters[sec] = n
        lang, _, d_app, d_exc = SECTION_DEFAULTS.get(sec, ("ru", None, [], INTERFACE_EXCLUDES))
        if lang == "any":
            lang = "en" if re.search(r"[A-Za-z]{3}", pat) and not re.search(r"[А-Яа-яЁё]", pat) else "any"
            if sec in ("5.1", "5.2", "5.3", "6.5"):
                lang = "any"
        rid = f"ux-{sec.replace('.', '-')}-{n:02d}"
        ppat = portable(pat)
        rule = {"id": rid, "marker_id": MARKER_HINTS.get(sec, f"ux:07-06#{sec}"), "level": level, "lang": lang,
                "group": "UX", "pattern": ppat, "flags": "" if case_sensitive(ppat) else "i",
                "message": f"ux 07/06 §{sec}: «{word.strip('*')}»" + (f" — {repl}" if repl else ""),
                "replacement": repl, "source": f"ux 07/06 §{sec} (стр. {idx})", "count_as_marker": False}
        app = list(applies or d_app)
        exc = sorted(set(excludes) | set(d_exc)) if excludes else list(d_exc)
        if app:
            rule["appliesTo"] = app
        if exc:
            ex = [e for e in exc if e not in app]
            if ex:
                rule["excludes"] = ex
        if count:
            rule["min_count"] = count
            if "экран" in word:
                rule["scope"] = "doc"
        if note:
            rule["note"] = f"оговорка ячейки канона: {note}"
        out_rules.append(rule)
    manual_rules = []
    for sec, idx, word, cell, level, repl in manual:
        n = counters.get(sec, 0) + 1
        counters[sec] = n
        manual_rules.append({"id": f"ux-{sec.replace('.', '-')}-{n:02d}", "marker_id": f"ux:07-06#{sec}",
                             "level": level, "lang": "any", "group": "UX", "kind": "manual",
                             "message": f"ux 07/06 §{sec}: «{word.strip('*')}» — ручная проверка ({cell})",
                             "replacement": repl, "source": f"ux 07/06 §{sec} (стр. {idx})", "count_as_marker": False})
    return {"roles": known, "rules": out_rules + manual_rules, "delegated": delegated,
            "_qualified_unused": sorted(k for k in QUALIFIED if k not in used_qualified)}


# ------------------------------------------------------------------------------------------------ длины по ролям §12
def parse_length(cell: str) -> dict:
    """Ячейка «Длина» → границы: words_max, sentences_max, chars_max, lines_max (строки — проверка макета)."""
    s = cell.replace("*", "").lower()
    out: dict = {}
    m = re.search(r"(\d+)\s*[–-]\s*(\d+)\s+слов", s)
    if m:
        out["words_max"] = int(m.group(2))
    m = re.search(r"≤\s*(\d+)\s+слов", s)
    if m and "words_max" not in out:
        out["words_max"] = int(m.group(1))
    m = re.search(r"≤\s*(\d+)\s+знак", s)
    if m:
        out["chars_max"] = int(m.group(1))
    m = re.search(r"(\d+)\s*[–-]\s*(\d+)\s+предложени", s)
    if m:
        out["sentences_max"] = int(m.group(2)) + (1 if "заголовок +" in s else 0)
    elif re.search(r"\b(одно|одна)\b[^,;]*предложени", s) or re.search(r"одно\s+(короткое\s+)?предложение", s):
        out["sentences_max"] = 1
    m = re.search(r"≤\s*(\d+)\s+строк", s)
    if m:
        out["lines_max"] = int(m.group(1))
    elif re.search(r"одна строка|одну строку|никогда не в две строки", s):
        out["lines_max"] = 1
    return out


def convert_lengths(text: str) -> dict:
    """Таблица §12 → {sentence, roles, skipped}."""
    body = section_text(text, LENGTHS_SECTION)
    start = text.split("\n").index(f"## {LENGTHS_SECTION}") + 1 if f"## {LENGTHS_SECTION}" in text.split("\n") else 0
    header, roles, skipped, sentence = None, {}, [], {}
    for k, line in enumerate(body.split("\n")):
        if not line.strip().startswith("|"):
            header = None if not line.strip() else header
            continue
        cells = split_row(line)
        if all(re.fullmatch(r":?-{3,}:?", c or "---") for c in cells):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        el_i = next((i for i, h in enumerate(header) if h.startswith("элемент")), 0)
        len_i = next((i for i, h in enumerate(header) if h.startswith("длина")), 1)
        role_i = next((i for i, h in enumerate(header) if h.startswith("роль")), None)
        element = re.sub(r"\s*\(.*?\)\s*", " ", cells[el_i]).strip()
        key = element.lower()
        where = f"ux 07/01 §12 (стр. {start + k + 1})"
        bounds = parse_length(cells[len_i] if len_i < len(cells) else "")
        if key == SENTENCE_ELEMENT:
            nums = [int(x) for x in re.findall(r"≤\s*(\d+)", cells[len_i])]
            if nums:
                sentence = {"words_max": nums[0], "explanatory_words_max": nums[-1],
                            "explanatory_roles": list(EXPLANATORY_ROLES), "source": where}
            continue
        if key in ELEMENT_SKIP:
            skipped.append({"element": element, "why": ELEMENT_SKIP[key], "source": where})
            continue
        rl = backticks(cells[role_i]) if role_i is not None and role_i < len(cells) else []
        rl = rl or ELEMENT_ROLES.get(key, [])
        if not rl:
            skipped.append({"element": element, "why": "роль элемента не названа", "source": where})
            continue
        if not bounds:
            skipped.append({"element": element, "why": "в ячейке нет числовой границы", "source": where})
            continue
        for r in rl:
            roles.setdefault(r, []).append({"element": element, **bounds, "source": where})
    return {"sentence": sentence, "roles": roles, "skipped": skipped}


def build(src_text: str, lengths_text: str) -> tuple[str, dict]:
    data = convert(src_text)
    lengths = convert_lengths(lengths_text)
    head = (f"# Собирает {TOOL} — руками не править.\n"
            f"# Источники: ../ux/07-ux-writing/06-banned-words-and-patterns.md (sha256 {sha16(src_text)}…) — правила;\n"
            f"#            ../ux/07-ux-writing/01-principles-voice-and-tone.md §12 (sha256 {sha16(lengths_text)}…) — длины.\n"
            f"# Правила ux по ролям §7.2 (appliesTo, excludes); в жанрах сайта — поправки marketing-role.yaml (overrides с\n"
            f"# полем genres). Группа UX: находка, перекрытая своим правилом того же места, скрывается.\n")
    meta = {"version": 1, "owner": "ux 07/06 (канон), конвертер " + TOOL, "inherits": "ux 07/06 §1–§6, ux 07/01 §12",
            "source_file": "../ux/07-ux-writing/06-banned-words-and-patterns.md", "source_sha256_16": sha16(src_text),
            "lengths_source_file": "../ux/07-ux-writing/01-principles-voice-and-tone.md",
            "lengths_source_sha256_16": sha16(lengths_text), "roles": data["roles"]}
    body = {**meta, "rules": data["rules"], "delegated": data["delegated"],
            "role_lengths": {"section": f"ux 07/01 §{LENGTHS_SECTION}", **lengths}}
    text = head + yaml.safe_dump(body, allow_unicode=True, sort_keys=False, width=120)
    return text, {"data": data, "lengths": lengths}


# ------------------------------------------------------------------------------------------------ самопроверка
JS_PROBE = r"""
const fs = require('fs');
const items = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = {};
for (const it of items) {
  try {
    const re = new RegExp(it.pattern, 'gu' + (it.flags.includes('i') ? 'i' : ''));
    out[it.id] = it.probes.map(p => Array.from(p.matchAll(re), m => m[0]).filter(s => s.length));
  } catch (e) { out[it.id] = 'ERR ' + e.message; }
}
process.stdout.write(JSON.stringify(out));
"""

PROBES = [  # (id правила, текст, должно найтись) — кириллица, оговорки ячеек, границы слова
    ("ux-1-01", "Мощный инструмент для команды", True),
    ("ux-2-1-04", "Кто производитель плитки?", False),
    ("ux-2-1-04", "Оплата производится после замера", True),
    ("ux-3-1-01", "Платёж успешно отправлен", True),
    ("ux-6-4-11", "Оплата: СБП или карта", False),
    ("ux-6-4-11", "Важно: Проверьте номер", True),
    ("ux-4-2-07", "since 2014 we have been open", False),
    ("ux-4-2-07", "since you asked, here it is", True),
    ("ux-3-2-02", "Список заявок не загрузился", True),
]


def probes_of(word: str) -> list[str]:
    """Слова первой колонки строки канона — образцы для сверки Python и JS."""
    s = re.sub(r"\(.*?\)", "", word.replace("*", ""))
    return [p.strip(" «»\"") for p in re.split(r",|/| или ", s) if p.strip(" «»\"")][:6]


def selftest(src: Path, lengths_src: Path) -> int:
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(("OK   " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
        ok = ok and bool(cond)

    text = src.read_text(encoding="utf-8")
    ltext = lengths_src.read_text(encoding="utf-8")
    out1, info = build(text, ltext)
    out2, _ = build(text, ltext)
    data, lengths = info["data"], info["lengths"]
    rules = [r for r in data["rules"] if r.get("kind") != "manual"]
    roles = set(data["roles"])
    check("сборка детерминирована", out1 == out2)
    check("роли §7.2 из источника и body", {"title", "action", "user-content", "body"} <= roles and len(roles) >= 32,
          f"{len(roles)} ролей")
    bad_roles = sorted({x for r in data["rules"] for x in (r.get("appliesTo") or []) + (r.get("excludes") or [])
                        if x not in roles})
    check("appliesTo и excludes — роли закрытого списка", not bad_roles, ", ".join(bad_roles))
    check("правил с регулярным выражением ≥ 140 и ручных ≥ 5", len(rules) >= 140 and
          len(data["rules"]) - len(rules) >= 5, f"{len(rules)} / {len(data['rules']) - len(rules)}")
    check("без заметки о роли body", not any("body" in (r.get("note") or "") and "отсутствует" in r.get("note", "")
                                             for r in data["rules"]))
    lst = next((r for r in data["rules"] if r["id"] == "ux-3-2-02"), {})
    check("«Список (как название)» — только роли названий", "title" in (lst.get("appliesTo") or []) and
          "inline-message" not in (lst.get("appliesTo") or []), json.dumps(lst.get("appliesTo"), ensure_ascii=False))
    check("строки пробелов §6.5 — правила H", {d["to"] for d in data["delegated"]} >= set(DELEGATED.values())
          and not any(r["pattern"] in DELEGATED for r in rules), json.dumps(data["delegated"], ensure_ascii=False))
    check("оговорки ячеек применены", not data["_qualified_unused"],
          f"шаблон ячейки уже с оговоркой — строку QUALIFIED снять: {data['_qualified_unused']}")
    py_bad = []
    for r in rules:
        try:
            re.compile(r["pattern"], re.I if "i" in r["flags"] else 0)
        except re.error as e:
            py_bad.append(f"{r['id']}: {e}")
        if re.search(r"\\[wbd]", r["pattern"]):
            py_bad.append(f"{r['id']}: \\w, \\b или \\d в шаблоне")
    check("шаблоны компилируются в Python, без \\w \\b \\d", not py_bad, "; ".join(py_bad[:5]))
    # сверка Python и JS на образцах строк канона и на пробах
    by_id = {r["id"]: r for r in rules}
    src_lines = text.split("\n")
    items = []
    for r in rules:
        m = re.search(r"стр\. (\d+)", r["source"])
        word = split_row(src_lines[int(m.group(1)) - 1])[0] if m else ""
        items.append({"id": r["id"], "pattern": r["pattern"], "flags": r["flags"], "probes": probes_of(word)})
    for rid, probe, _ in PROBES:
        it = next((x for x in items if x["id"] == rid), None)
        if it is not None:
            it["probes"] = it["probes"] + [probe]
    for rid, probe, want in PROBES:
        r = by_id.get(rid)
        got = bool(r and re.search(r["pattern"], probe, re.I if "i" in r["flags"] else 0))
        check(f"проба {rid}: «{probe}» — {'находка' if want else 'тишина'}", r is not None and got == want)
    node = kbpaths.find("node")
    if not node:
        print("SKIP сверка шаблонов в JS: node не найден (системный Node; путь — kbpaths.py --bins); без него — только Python")
    else:
        try:
            res = subprocess.run([node, "-e", JS_PROBE], input=json.dumps(items, ensure_ascii=False), text=True,
                                 capture_output=True, timeout=120, env=kbpaths.node_env())
            js = json.loads(res.stdout or "{}")
        except (OSError, ValueError, subprocess.SubprocessError) as e:
            js = {"__error__": str(e)}
        diff = []
        for it in items:
            r = by_id[it["id"]]
            fl = re.I if "i" in r["flags"] else 0
            py = [[m.group(0) for m in re.finditer(r["pattern"], p, fl) if m.group(0)] for p in it["probes"]]
            if js.get(it["id"]) != py:
                diff.append(f"{it['id']}: py {py} js {js.get(it['id'])}")
        cyr = sum(1 for it in items if re.search(r"[А-Яа-яЁё]", " ".join(it["probes"])))
        check(f"Python и JS (флаг u) дают одни совпадения на кириллице и латинице: {len(items)} правил, "
              f"{cyr} с кириллическими образцами", not diff and "__error__" not in js, "; ".join(diff[:4]))
    # длины по ролям §12
    rl = lengths["roles"]
    def first(role, key):
        return (rl.get(role) or [{}])[0].get(key)
    check("длины §12: кнопка ≤ 3 слов, тост ≤ 10, ссылка ≤ 3, заголовок экрана ≤ 4",
          (first("action", "words_max"), first("toast", "words_max"), first("link", "words_max"),
           first("title", "words_max")) == (3, 10, 3, 4), json.dumps(rl, ensure_ascii=False)[:300])
    check("длины §12: тело подтверждения и ошибка поля — одно предложение, баннер — заголовок и до двух",
          (first("confirm-body", "sentences_max"), first("error", "sentences_max"), first("banner", "sentences_max"))
          == (1, 1, 3))
    check("длины §12: у пустого состояния два варианта (заголовок и пояснение)", len(rl.get("empty") or []) == 2)
    check("длины §12: предложение ≤ 15 слов, в пояснениях ≤ 20",
          (lengths["sentence"].get("words_max"), lengths["sentence"].get("explanatory_words_max")) == (15, 20))
    check("длины §12: роли — из закрытого списка", set(rl) <= roles, ", ".join(sorted(set(rl) - roles)))
    print("self-test:", "OK" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ux 07/06 (словарь запретов) и ux 07/01 §12 (длины) → YAML для "
                                             "copy_lint.py; --check — сверка без записи, --selftest — самопроверка")
    ap.add_argument("--src", default=str(SRC), help="источник словаря (по умолчанию ux 07/06)")
    ap.add_argument("--lengths-src", default=str(LENGTHS_SRC), help="источник длин (по умолчанию ux 07/01)")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--check", action="store_true", help="сравнить с файлом без записи: код 3 — устарел")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    src, lsrc = Path(a.src), Path(a.lengths_src)
    if a.selftest:
        return selftest(src, lsrc)
    out_text, info = build(src.read_text(encoding="utf-8"), lsrc.read_text(encoding="utf-8"))
    outp = Path(a.out)
    if a.check:
        cur = outp.read_text(encoding="utf-8") if outp.exists() else ""
        if cur != out_text:
            print(f"устарел: {outp} (пересобрать без --check)")
            return 3
        print("актуален")
        return 0
    outp.write_text(out_text, encoding="utf-8")
    rules = info["data"]["rules"]
    n_auto = sum(1 for r in rules if r.get("kind") != "manual")
    print(f"{outp}: правил {n_auto} с регулярным выражением, {len(rules) - n_auto} ручных, "
          f"{len(info['data']['delegated'])} строк — правилам набора H; ролей с длинами {len(info['lengths']['roles'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
