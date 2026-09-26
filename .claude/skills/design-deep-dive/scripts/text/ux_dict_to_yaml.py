#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ux_dict_to_yaml.py — конвертер словарей ux 07/06 (Markdown-таблицы) в YAML-правила copy_lint.py.

text-research · волна 1 · агент C · 2026-09-24.

Источник: ../ux-research/07-ux-writing/06-banned-words-and-patterns.md (§1–§6, формат правила §7.1, роли §7.2).
Выход:    06-anti-slop/lexicon/ux-07-06.yaml — файл генерируется, руками не правится (правки для роли marketing и
          поправки PLAN.md «для сайта» — в 06-anti-slop/lexicon/marketing-role.yaml через overrides).

Что делает:
- находит в разделах §1–§6 таблицы с колонкой регулярного выражения («Regex», «Regex-приближение»);
- берёт шаблон из первого `…` в ячейке, роли — из следующих `…` после слов «роли/ролей» («в узлах роли `link`»),
  исключения — «кроме `email`», «вне узлов роли `placeholder`»;
- уровень: «запрет» → error, «предупреждение» → warning (или уровень раздела: «Уровень — запрет во всех строках»);
- ECMAScript → Python: снимает экранирование «\\|» из Markdown, флаги giu → i; `\\w` в Python юникодный (в JS — нет;
  см. 06-anti-slop/02-linter-spec-and-profiles.md, раздел о наследовании);
- ячейки без регулярного выражения («не regex», «сравнение стилей…») → kind: manual (в линтере не исполняются, остаются
  в каталоге как ручные проверки);
- id: ux-<раздел>-<nn>; marker_id: ux:07-06#<раздел> (короткая ссылка по контракту тройки §3 п.15); group: UX.

Запуск:  python3 99-raw/tools/ux_dict_to_yaml.py [--src PATH] [--out PATH] [--check]
         --check — не писать файл, а сравнить с существующим (код 3, если устарел).
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("text")
SRC = kbpaths.kb("ux", "07-ux-writing", "06-banned-words-and-patterns.md")
OUT = ROOT / "06-anti-slop" / "lexicon" / "ux-07-06.yaml"

UX_ROLES = ["title", "subtitle", "section-title", "label", "checkbox-label", "placeholder", "hint", "caption", "action",
            "link", "nav", "tab", "column-header", "status", "badge", "toast", "banner", "inline-message", "error",
            "empty", "confirm-title", "confirm-body", "tooltip", "setting-description", "email", "push", "aria", "alt",
            "marketing", "help", "user-content"]
INTERFACE_EXCLUDES = ["marketing", "help", "user-content"]

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


def md5_short(text: str) -> str:
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


def roles_from(cell: str) -> tuple[list[str], list[str]]:
    applies, excludes = [], []
    m = re.search(r"вне\s+узлов\s+рол\w*\s+(.*)$", cell)
    if m:
        excludes = [r for r in backticks(m.group(1)) if r in UX_ROLES]
        return applies, excludes
    m = re.search(r"кроме\s+(.*)$", cell)
    if m:
        excludes = [r for r in backticks(m.group(1)) if r in UX_ROLES]
    m = re.search(r"рол(?:и|ей)\s+(.*)$", cell)
    if m and "вне" not in cell:
        for r in backticks(m.group(1)):
            if r == "confirm":
                applies += ["confirm-title", "confirm-body"]
            elif r in UX_ROLES or r == "body":
                applies.append(r)
    return applies, excludes


def convert(src_text: str) -> dict:
    lines = src_text.split("\n")
    rules = []
    manual = []
    sec = ""
    sec_level_all = None
    header = None
    counters: dict = {}
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
        lead = rx_cell.split("`", 1)[0].strip().lower()
        role_first = bool(bts) and bts[0] in UX_ROLES and lead and not lead.startswith("подсчёт")
        if not bts or role_first or "не regex" in rx_cell or "сравнение" in rx_cell.lower() \
                or rx_cell.startswith("текстовый"):
            manual.append((sec, idx, word, rx_cell, level, repl))
            continue
        pat = unescape_md(bts[0])
        applies, excludes = roles_from(rx_cell)
        count = None
        if rx_cell.strip().startswith("подсчёт"):
            count = 2
        rules.append((sec, idx, word, pat, level, repl, applies, excludes, count))
    out_rules = []
    for sec, idx, word, pat, level, repl, applies, excludes, count in rules:
        n = counters.get(sec, 0) + 1
        counters[sec] = n
        lang, _, d_app, d_exc = SECTION_DEFAULTS.get(sec, ("ru", None, [], INTERFACE_EXCLUDES))
        if lang == "any":
            lang = "en" if re.search(r"[A-Za-z]{3}", pat) and not re.search(r"[А-Яа-яЁё]", pat) else "any"
            if sec in ("5.1", "5.2", "5.3", "6.5"):
                lang = "any"
        rid = f"ux-{sec.replace('.', '-')}-{n:02d}"
        # регистрозависимый шаблон: класс только с заглавными ([A-ZА-Я]), без строчных; с флагом i он ловит «Мы — »
        case_sensitive = any(("A-Z" in cls or "А-Я" in cls) and "a-z" not in cls and "а-я" not in cls
                             for cls in re.findall(r"\[([^\]]+)\]", pat))
        rule = {"id": rid, "marker_id": MARKER_HINTS.get(sec, f"ux:07-06#{sec}"), "level": level, "lang": lang,
                "group": "UX", "pattern": pat, "flags": "" if case_sensitive else "i",
                "message": f"ux 07/06 §{sec}: «{word.strip('*')}»" + (f" — {repl}" if repl else ""),
                "replacement": repl, "source": f"ux 07/06 §{sec} (стр. {idx})",
                "evidence": "[практика] ux-research (волна 3, агент G, 2026-09-22)", "count_as_marker": False,
                "date": "2026-09-22"}
        app = applies or d_app
        exc = sorted(set(excludes) | set(d_exc)) if excludes else list(d_exc)
        if app:
            rule["appliesTo"] = app
        if exc:
            rule["excludes"] = [e for e in exc if e not in app]
        if count:
            rule["min_count"] = count
            if "экран" in word:
                rule["scope"] = "doc"
        if sec == "6.5" and pat in ("  +", r"\s+[,.;:!?]", r"[,.;:!?][А-Яа-яA-Za-z]"):
            rule["level"] = "warning"
            rule["note"] = "типографика — H; в прозе сайта ложные срабатывания на URL и сокращениях"
        if "body" in (rule.get("appliesTo") or []):
            rule["note"] = (rule.get("note", "") + " роль «body» отсутствует в закрытом списке §7.2 ux 07/06 — "
                            "в copy_lint не срабатывает, пока роль не уточнит ux").strip()
        out_rules.append(rule)
    manual_rules = []
    for sec, idx, word, cell, level, repl in manual:
        n = counters.get(sec, 0) + 1
        counters[sec] = n
        manual_rules.append({"id": f"ux-{sec.replace('.', '-')}-{n:02d}", "marker_id": f"ux:07-06#{sec}",
                             "level": level, "lang": "any", "group": "UX", "kind": "manual",
                             "message": f"ux 07/06 §{sec}: «{word.strip('*')}» — ручная проверка ({cell})",
                             "replacement": repl, "source": f"ux 07/06 §{sec} (стр. {idx})", "count_as_marker": False,
                             "date": "2026-09-22"})
    return {"rules": out_rules + manual_rules}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ux 07/06 → YAML для copy_lint.py")
    ap.add_argument("--src", default=str(SRC))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    src = Path(a.src)
    text = src.read_text(encoding="utf-8")
    data = convert(text)
    head = (f"# СГЕНЕРИРОВАНО 99-raw/tools/ux_dict_to_yaml.py — руками не править.\n"
            f"# Источник: ../ux/07-ux-writing/06-banned-words-and-patterns.md (sha256 {md5_short(text)}…).\n"
            f"# Правила ux для интерфейсных ролей (appliesTo/excludes по §7.2); для роли marketing и «для сайта» —\n"
            f"# поправки в marketing-role.yaml (overrides). Группа UX: находка, перекрытая своим правилом, скрывается.\n")
    meta = {"date": "2026-09-24", "version": 1, "owner": "C (волна 1), конвертер", "inherits": "ux 07/06 §1–§6",
            "source_file": "../ux/07-ux-writing/06-banned-words-and-patterns.md",
            "source_sha256_16": md5_short(text), "source_date": "2026-09-22"}
    body = yaml.safe_dump({**meta, **data}, allow_unicode=True, sort_keys=False, width=120)
    out_text = head + body
    outp = Path(a.out)
    if a.check:
        cur = outp.read_text(encoding="utf-8") if outp.exists() else ""
        if cur != out_text:
            print(f"устарел: {outp} (перегенерировать без --check)")
            return 3
        print("актуален")
        return 0
    outp.write_text(out_text, encoding="utf-8")
    n_auto = sum(1 for r in data["rules"] if r.get("kind") != "manual")
    n_man = sum(1 for r in data["rules"] if r.get("kind") == "manual")
    print(f"{outp}: правил {n_auto} с регулярным выражением, {n_man} ручных")
    return 0


if __name__ == "__main__":
    sys.exit(main())
