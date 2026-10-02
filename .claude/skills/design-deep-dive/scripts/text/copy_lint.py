#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""copy_lint.py — линтер текстов RU/EN по жанру и роли строки: маркетинговые тексты сайта и тексты интерфейса.

Спецификация — kb/text/06-anti-slop/02-linter-spec-and-profiles.md; словарь запретов интерфейса — ux 07/06 (производный
06-anti-slop/lexicon/ux-07-06.yaml собирает ux_dict_to_yaml.py).

Что делает. Находит маркеры нейрослопа и ошибки жанра по правилам 06-anti-slop/lexicon/*.yaml и внешним файлам
(мета, GEO и набор; profiles.yaml → external_rules), профилю жанра 06-anti-slop/profiles.yaml и порогам
03-corpus-measured/thresholds.yaml. Право формулировок (правила COPY-L-…) линтер не проверяет — это делает
claims_check.py: одно нарушение права даёт одну находку. Считает метрики на 100 слов: маркеры, тире, «не X, а Y», вопросы, тройки,
восклицания, конкретика; ритм предложений и абзацев; ищет следы сверхкоррекции («текст хуманайзера»).

Жанры: landing, site-page, article, meta, geo, email-form — тексты сайта; interface — тексты продукта за входом
(кабинет, приложение, бот, письма, СМС, push). В interface правила ux действуют с уровнями канона 07/06, из text —
артефакты, данные и набор; поправки сайта (overrides с полем genres) к нему не относятся; межстрочные проверки ux
07/06 §7.3 — анализаторы над реестром текстов: имя действия по потоку (action.md), синонимы объекта (object.md,
aliases), формы меню и статусов, дубли на экране, maxlen и длина по роли (ux 07/01 §12), форматы чисел и диапазонов,
ICU, «ты» и «вы», «ё» и «е», US и UK, уровень чтения ролей body, help, email.

Вход: .txt, .md, .html/.htm; copy deck .yaml/.yml (copy_deck.pages[].sections[].slots[] или короткая форма
slots: [{slot_type | role | component, text}]); реестр текстов интерфейса texts.md (таблица key, role, text, maxlen,
action, object, group, context, status; жанр — interface); «-» — stdin. Тип слота — id слота вида text словаря site
(kb/site/02-site-types/vocabulary.yaml); роль ux, жанры и lint_as типа — 04-copy-by-block/copy-slots.yaml; жанр
страницы copy deck — page_type.genre словаря. Роль строки — ключ --role, поле role (реестр, короткая форма copy deck) или
роль части компонента (--component, поле component; kb/common/components.yaml#text_roles); закрытый список — ux 07/06
§7.2 и body (раздел roles производного словаря ux) и внутренняя meta. Неизвестная роль, тип слота или часть
компонента, роль строки не из ролей части — ошибка вызова.

Запуск (из папки скилла):
  scripts/text/copy_lint.py page.md --genre landing              # отчёт для человека (аудит страницы — сигнал)
  scripts/text/copy_lint.py deck.yaml --json                     # copy deck: выбранные варианты; --all-variants — все
  scripts/text/copy_lint.py docs/projects/<slug>/screens/<surface>/texts.md     # реестр текстов, жанр interface
  scripts/text/copy_lint.py - --genre interface --role action    # одна строка интерфейса со stdin
  scripts/text/copy_lint.py page.md --facts facts.yaml           # адреса и названия мест из фактов — не деепричастия
  scripts/text/copy_lint.py --selftest                           # словари, сводка уровней по жанрам, калибровки
Обслуживание базы (в маршруте этапов проекта не участвует):
  scripts/text/copy_lint.py text.txt --metrics-only --json       # только метрики — замеры корпуса для порогов жанров

Места из фактов. Имена сущностей вида place файла фактов (entities[]: адрес, улица, название места) правило о слове на
«-ая,» (ux-6-4-10) не трогает: «улица Лесная, дом 3» — адрес, а не деепричастный оборот. Файл фактов — ключ --facts,
у copy deck — его facts_ref.

Коды выхода: 0 — нет находок уровня error; 2 — есть error (ворота не пройдены); 1 — ошибка вызова, входа или словаря.
Интерпретатор — $DDD_HOME/venv/bin/python (PyYAML, морфология pymorphy3); без pymorphy3 работают регулярные
приближения с уровнем не выше warning, а проверка форм групп строк интерфейса пропускается с заметкой.

Как модуль:
  from copy_lint import lint_text, text_metrics
  report = lint_text("Текст…", genre="landing", lang="auto")   # dict как в JSON-выводе (один результат)
  report = lint_text("Сохранить", genre="interface", role="action")
  m = text_metrics("Текст…", lang="ru")                         # dict метрик без правил профиля
"""
from __future__ import annotations

import argparse
import copy
import fnmatch
import json
import math
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

VERSION = "1.0.0"
DATE = "2026-09-29"

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("text")
LEXICON_DIR = ROOT / "06-anti-slop" / "lexicon"
PROFILES_PATH = ROOT / "06-anti-slop" / "profiles.yaml"
VOCAB_PATH = kbpaths.kb("site", "02-site-types", "vocabulary.yaml")
COPY_SLOTS_PATH = ROOT / "04-copy-by-block" / "copy-slots.yaml"
UX_DICT_PATH = LEXICON_DIR / "ux-07-06.yaml"
TELLS_PATH = kbpaths.kb(None, "common", "tells.yaml")
TELL_KEY = "copy_lint:"             # ключ проверки в tells.yaml#checks: copy_lint:<id правила или анализатора>
THRESHOLDS_PATH = ROOT / "03-corpus-measured" / "thresholds.yaml"

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover
    sys.stderr.write("copy_lint: нужен PyYAML — запускайте интерпретатором $DDD_HOME/venv/bin/python.\n")
    sys.exit(1)

LEVELS = ("error", "warning", "info", "off")
LEVEL_RANK = {"off": 0, "info": 1, "warning": 2, "error": 3}
GROUPS = ("ART", "CNT", "LEX", "SYN", "PUN", "STR", "TON", "MKT", "UX", "EXT")
SITE_GENRES = ("landing", "site-page", "article", "meta", "geo", "email-form")
GENRES = SITE_GENRES + ("interface",)
STYLE_GROUPS = {"LEX", "SYN", "TON", "MKT", "STR", "PUN"}  # в цитатах и коде не срабатывают
INTERNAL_ROLES = ("meta",)          # роль парсера: мета и OG страницы
INTERNAL_SLOTS = ("hr",)            # псевдослот парсера: разделитель «---» в Markdown


class UsageError(ValueError):
    """Ошибка вызова: неизвестная роль, тип слота или часть компонента; роль строки не из ролей части — код 1."""

# --- токенизация -------------------------------------------------------------------------------------------------
LETTER = "A-Za-zА-Яа-яЁё"
WORDCH = LETTER + "0-9"
B_MACRO = r"(?<![" + WORDCH + r"_])"          # левая граница слова, работает для кириллицы
E_MACRO = r"(?![" + WORDCH + r"_])"           # правая граница слова
W_MACRO = r"[" + WORDCH + r"_]*"              # продолжение основы
WORD_RE = re.compile(r"[" + WORDCH + r"]+(?:[-’'][" + WORDCH + r"]+)*")
CYR_RE = re.compile(r"[А-Яа-яЁё]")
LAT_RE = re.compile(r"[A-Za-z]")
NBSP = "\u00a0\u202f\u2009\u2007"

ABBREV_RU = {"т", "е", "д", "п", "к", "др", "г", "гг", "руб", "коп", "тыс", "млн", "млрд", "ул", "стр", "им", "см",
             "рис", "табл", "пп", "ст", "ч", "мин", "сек", "кв", "пр", "проф", "акад", "доц", "напр", "ср", "англ",
             "рус", "лат", "обл", "пер", "просп", "тел", "эт", "оф", "корп", "вкл", "искл", "шт", "ок", "прим"}
ABBREV_EN = {"e.g", "i.e", "etc", "vs", "mr", "mrs", "ms", "dr", "prof", "inc", "ltd", "co", "st", "no", "jr", "sr",
             "approx", "dept", "est", "fig", "min", "max", "mt", "u.s", "u.k"}
SENT_END_RE = re.compile(r"([.!?…]+)([\"»”’)\]]*)(\s+)(?=[«\"“(\[A-ZА-ЯЁ0-9—–-])")


def norm_spaces(s: str) -> str:
    for ch in NBSP:
        s = s.replace(ch, " ")
    return s


def words_of(text: str) -> list[str]:
    return WORD_RE.findall(norm_spaces(text))


def split_sentences(text: str) -> list[tuple[int, int]]:
    """Границы предложений (start, end) внутри текста. Учитывает сокращения, инициалы и десятичные дроби."""
    t = norm_spaces(text)
    spans, start = [], 0
    for m in SENT_END_RE.finditer(t):
        punct = m.group(1)
        cut = m.end(2)
        if punct.endswith("."):
            before = t[start:m.start(1)]
            last = re.findall(r"[" + WORDCH + r".]+$", before)
            tok = last[0].lower() if last else ""
            tok_clean = tok.strip(".")
            if tok_clean in ABBREV_RU or tok_clean in ABBREV_EN or tok in ABBREV_EN:
                continue
            if len(tok_clean) == 1 and tok_clean.isalpha():  # инициал «А. С. Пушкин»
                continue
        seg = t[start:cut].strip()
        if seg:
            s0 = start + (len(t[start:cut]) - len(t[start:cut].lstrip()))
            spans.append((s0, cut))
        start = m.end()
    if t[start:].strip():
        s0 = start + (len(t[start:]) - len(t[start:].lstrip()))
        spans.append((s0, len(t.rstrip())))
    return spans


def split_paragraphs(text: str) -> list[tuple[int, int]]:
    spans, pos = [], 0
    for m in re.finditer(r"\n\s*\n", text):
        if text[pos:m.start()].strip():
            spans.append((pos, m.start()))
        pos = m.end()
    if text[pos:].strip():
        spans.append((pos, len(text)))
    return spans


QUOTE_RE = re.compile(r"«[^«»\n]{1,400}»|“[^“”\n]{1,400}”|„[^„“”\n]{1,400}[“”]|\"[^\"\n]{1,400}\"|`[^`\n]+`")


def masked_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in QUOTE_RE.finditer(text)]


def inside(a: tuple[int, int], spans: list[tuple[int, int]]) -> bool:
    """Совпадение целиком внутри цитаты: чужие слова в кавычках не правятся, а длинное совпадение, задевшее кавычки
    («не только «экономит», но и…»), остаётся находкой."""
    return any(s <= a[0] and a[1] <= e for s, e in spans)


def detect_lang(text: str) -> str:
    c, l = len(CYR_RE.findall(text)), len(LAT_RE.findall(text))
    if c == 0 and l == 0:
        return "ru"
    return "ru" if c >= l else "en"


# --- правила -------------------------------------------------------------------------------------------------------
def expand_macros(p: str) -> str:
    return p.replace("%B%", B_MACRO).replace("%E%", E_MACRO).replace("%W%", W_MACRO)


def words_to_pattern(words: list[str]) -> str:
    alts = []
    for w in words:
        w = w.strip()
        if not w:
            continue
        parts = re.split(r"\s+", w)
        out = []
        for part in parts:
            esc = re.escape(part).replace(r"\*", "%W%").replace(r"\?", "?")
            esc = esc.replace("ё", "[её]").replace("Ё", "[ЕЁ]")
            out.append(esc)
        alts.append(r"\s+".join(out))
    alts.sort(key=len, reverse=True)
    return "%B%(?:" + "|".join(alts) + ")%E%"


def py_flags(flags: str) -> int:
    f = 0
    for ch in (flags or ""):
        if ch == "i":
            f |= re.IGNORECASE
        elif ch == "m":
            f |= re.MULTILINE
        elif ch == "s":
            f |= re.DOTALL
        elif ch == "x":
            f |= re.VERBOSE
    return f


@dataclass
class Rule:
    id: str
    level: str
    message: str
    source: str
    group: str = "LEX"
    marker_id: str = ""
    lang: str = "any"
    kind: str = "regex"            # regex | words | analyzer | manual
    pattern: str = ""
    words: list = field(default_factory=list)
    flags: str = "i"
    levels: dict = field(default_factory=dict)        # уровень по жанру
    slot_levels: dict = field(default_factory=dict)   # уровень по slot_type
    appliesTo: list = field(default_factory=list)     # роли ux 07/06 §7.2
    excludes: list = field(default_factory=list)
    genres: list = field(default_factory=list)
    slot_types: list = field(default_factory=list)
    exclude_slot_types: list = field(default_factory=list)
    count_as_marker: bool = True
    min_count: int = 1
    replacement: str = ""
    examples: dict = field(default_factory=dict)
    evidence: str = ""
    threshold_ref: str = ""
    date: str = ""
    mask_quotes: bool | None = None
    unless: str = ""               # регулярное выражение: если есть в том же предложении — не срабатывать
    requires_no_fact: bool = False  # срабатывает, только если у слота нет fact_ids
    scope: str = "unit"            # unit — min_count в пределах блока; doc — по всему документу
    priority: int = 50             # при совпадении места у двух правил остаётся более приоритетное
    per_sections: int = 0          # анализатор надзаголовков: не чаще одного на N секций с заголовком
    origin: str = ""
    note: str = ""
    regex: re.Pattern | None = None
    unless_re: re.Pattern | None = None
    genre_variants: dict = field(default_factory=dict)   # жанр → правило с поправками overrides этого жанра

    def for_genre(self, genre: str) -> "Rule":
        return self.genre_variants.get(genre, self)

    def compile(self) -> None:
        if self.kind in ("analyzer", "manual"):
            return
        pat = self.pattern
        if self.kind == "words" or (not pat and self.words):
            pat = words_to_pattern(self.words)
        if not pat:
            raise ValueError(f"{self.id}: пустой pattern/words")
        self.regex = re.compile(expand_macros(pat), py_flags(self.flags))
        if self.unless:
            self.unless_re = re.compile(expand_macros(self.unless), py_flags(self.flags))
        if self.mask_quotes is None:
            self.mask_quotes = self.group in STYLE_GROUPS


RULE_FIELDS = set(Rule.__dataclass_fields__) - {"regex", "unless_re", "origin", "genre_variants"}


def load_yaml(path: Path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_rule_file(path: Path) -> tuple[list[Rule], list[dict], dict]:
    data = load_yaml(path) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: корень YAML должен быть словарём")
    defaults = data.get("defaults", {}) or {}
    rules = []
    for raw in data.get("rules", []) or []:
        item = dict(defaults)
        item.update(raw)
        unknown = set(item) - RULE_FIELDS
        for k in unknown:
            item.pop(k)
        missing = [k for k in ("id", "level", "message", "source") if not item.get(k)]
        if missing:
            raise ValueError(f"{path}: правило {raw.get('id', '?')} без полей {missing}")
        if item["level"] not in LEVELS:
            raise ValueError(f"{path}: {item['id']}: уровень {item['level']} не из {LEVELS}")
        r = Rule(**item)
        r.origin = path.name
        r.compile()
        rules.append(r)
    return rules, data.get("overrides", []) or [], data


def apply_overrides(rules: list[Rule], overrides: list[dict], origin: str) -> None:
    """Поправка к чужому правилу действует в жанрах своего поля genres (без поля — в жанрах сайта): у правила появляется
    вариант для каждого такого жанра, в остальных жанрах — правило как есть. Поле requires_no_fact видно и у самого
    правила: его читает copydeck.py, чтобы снять находку при fact_ids слота; у строки без фактов оно ничего не меняет."""
    by_id = {r.id: r for r in rules}
    for ov in overrides:
        target = ov.get("target", "")
        genres = [g for g in (ov.get("genres") or SITE_GENRES) if g in GENRES]
        hits = [r for rid, r in by_id.items() if fnmatch.fnmatch(rid, target)]
        for r in hits:
            for g in genres:
                v = r.genre_variants.get(g)
                if v is None:
                    v = copy.copy(r)
                    v.genre_variants = {}
                    r.genre_variants[g] = v
                for k, val in (ov.get("set") or {}).items():
                    if k in RULE_FIELDS:
                        setattr(v, k, val)
                if ov.get("note"):
                    v.note = (v.note + " " if v.note else "") + f"[{origin}] {ov['note']}"
                v.compile()
            if (ov.get("set") or {}).get("requires_no_fact"):
                r.requires_no_fact = True


def load_rules(extra: list[str] | None = None, profiles: dict | None = None, log: list | None = None) -> list[Rule]:
    files = sorted(LEXICON_DIR.glob("*.yaml"))
    ext_paths = []
    for item in (profiles or {}).get("external_rules", []) or []:
        p = ROOT / item["path"] if not str(item["path"]).startswith("/") else Path(item["path"])
        ext_paths.append(p)
    for e in extra or []:
        p = Path(e)
        ext_paths.extend(sorted(p.glob("*.yaml")) if p.is_dir() else [p])
    rules, overrides = [], []
    seen = set()
    for f in files + ext_paths:
        if not f.exists():
            if log is not None:
                log.append(f"внешний файл правил не найден, пропущен: {f.relative_to(ROOT) if f.is_relative_to(ROOT) else f}")
            continue
        is_ext = f not in files
        # Ошибка во внешнем файле правил (G, H, …) пропускает только этот файл и выводится заметкой; ошибка в
        # собственных словарях 06-anti-slop/lexicon/ останавливает линтер.
        try:
            rs, ovs, data = load_rule_file(f)
            dup = [r.id for r in rs if r.id in seen]
            if dup:
                raise ValueError(f"повтор id правила: {', '.join(dup[:5])} ({f.name})")
        except Exception as e:
            if not is_ext:
                raise
            where = f.relative_to(ROOT) if f.is_relative_to(ROOT) else f
            msg = f"ошибка во внешнем файле правил, файл пропущен: {where}: {str(e)[:300]}"
            if log is not None:
                log.append(msg)
            print(f"copy_lint: {msg}", file=sys.stderr)
            continue
        for r in rs:
            if is_ext and r.group not in GROUPS:
                r.group = "EXT"
            seen.add(r.id)
        rules.extend(rs)
        overrides.extend((o, f.name) for o in ovs)
    for o, origin in overrides:
        apply_overrides(rules, [o], origin)
    return rules


# --- словарь слотов и профили ---------------------------------------------------------------------------------------
_VOCAB: dict = {}


def _mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def load_vocab(path: Path | None = None) -> dict:
    """Словарь site v1: слоты вида text — типы слотов; типы страниц — жанр text (page_type.genre). Роль ux, жанры и
    lint_as типа слота — 04-copy-by-block/copy-slots.yaml: у слота без своих правил роль и жанры — у типа lint_as.
    Результат запоминается по времени изменения обоих файлов (API линтера зовут на каждый слот)."""
    p = path or VOCAB_PATH
    key = (str(p), _mtime(p), _mtime(COPY_SLOTS_PATH))
    if key in _VOCAB:
        return _VOCAB[key]
    out: dict = {"slot_types": {}, "page_types": {}, "path": str(p)}
    if not p.exists():
        out["missing"] = True
        return out
    ns = (load_yaml(p) or {}).get("namespaces") or {}
    for x in (ns.get("slot") or {}).get("values") or []:
        if isinstance(x, dict) and x.get("kind") == "text" and x.get("id"):
            out["slot_types"][x["id"]] = {"id": x["id"]}
    for x in (ns.get("page_type") or {}).get("values") or []:
        if isinstance(x, dict) and x.get("id"):
            out["page_types"][x["id"]] = {"id": x["id"], "genre": x.get("genre") or ""}
    specs = {}
    if COPY_SLOTS_PATH.exists():
        specs = {s["id"]: s for s in (load_yaml(COPY_SLOTS_PATH) or {}).get("slot_types") or []
                 if isinstance(s, dict) and s.get("id")}
    for sid, st in out["slot_types"].items():
        sp = specs.get(sid) or {}
        st["lint_as"] = sp.get("lint_as") or ""
        base = (specs.get(st["lint_as"]) or {}) if st["lint_as"] else {}
        st["ux_role"] = sp.get("ux_role") or base.get("ux_role") or ""
        st["genres"] = list(sp.get("genres") or base.get("genres") or [])
    _VOCAB[key] = out
    return out


_ROLES: dict = {}


def closed_roles() -> list[str]:
    """Закрытый список ролей текста: ux 07/06 §7.2 и body — раздел roles производного ux-07-06.yaml — и внутренняя meta."""
    key = _mtime(UX_DICT_PATH)
    if key not in _ROLES:
        roles = list((load_yaml(UX_DICT_PATH) or {}).get("roles") or []) if UX_DICT_PATH.exists() else []
        if not roles:
            raise UsageError(f"в {UX_DICT_PATH.name} нет раздела roles: пересоберите словарь — "
                             "scripts/text/ux_dict_to_yaml.py")
        _ROLES.clear()
        _ROLES[key] = roles + [r for r in INTERNAL_ROLES if r not in roles]
    return _ROLES[key]


def check_role(role: str, where: str = "") -> str:
    if role not in closed_roles():
        raise UsageError(f"роль «{role}»{' (' + where + ')' if where else ''} не из закрытого списка ux 07/06 §7.2 и "
                         f"body; допустимо: {', '.join(r for r in closed_roles() if r not in INTERNAL_ROLES)}")
    return role


_LAYER = None


def _layer():
    """Модуль разбора файлов проекта scripts/project/layer.py: реестр texts.md, таблицы продукта, словарь компонентов."""
    global _LAYER
    if _LAYER is None:
        kbpaths.use("project")
        import layer  # noqa: WPS433
        _LAYER = layer
    return _LAYER


def component_roles(name: str) -> list[str]:
    """Роли текста части компонента — kb/common/components.yaml#text_roles: «Field.Error» → [error], «Button» → [action]."""
    key = name[3:] if name.startswith("ui:") else name
    t, _, part = key.partition(".")
    roles = _layer().components().roles(t, part or None)
    if not roles:
        raise UsageError(f"компонент «{name}»: у части нет роли текста в kb/common/components.yaml#text_roles")
    return roles


def resolve_role(role: str = "", component: str = "", where: str = "") -> str:
    """Роль строки: явная (ключ --role, поле role) или роль части компонента; явная роль — из ролей части."""
    if component:
        croles = component_roles(component)
        if role:
            check_role(role, where)
            if role not in croles:
                raise UsageError(f"роль «{role}»{' (' + where + ')' if where else ''} ≠ роль части «{component}»: "
                                 f"{', '.join(croles)}")
            return role
        if len(croles) > 1:
            raise UsageError(f"у части «{component}» роли {', '.join(croles)}: задайте роль строки (--role, поле role)")
        return croles[0]
    return check_role(role, where) if role else ""


def load_profiles(path: Path | None = None) -> dict:
    p = path or PROFILES_PATH
    if not p.exists():
        return {"profiles": {g: {"genre": g} for g in GENRES}, "provisional": True}
    return load_yaml(p) or {}


def merge_dict(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge_dict(out[k], v)
        else:
            out[k] = v
    return out


def resolve_profile(profiles: dict, name: str, thresholds_path: Path | None, lang: str = "") -> tuple[dict, dict]:
    """Профиль = defaults ⊕ profiles[name] ⊕ thresholds.yaml (замер корпуса) для этого жанра ⊕ analyzers_by_lang[lang]
    (если язык известен). Возвращает (профиль, источник порогов)."""
    base = profiles.get("defaults", {}) or {}
    prof = merge_dict(base, (profiles.get("profiles", {}) or {}).get(name, {}) or {})
    prof.setdefault("genre", name)
    src = {"thresholds": "profiles.yaml (стартовые, provisional: true)", "provisional": True}
    tp = thresholds_path or THRESHOLDS_PATH
    if tp and tp.exists():
        try:
            th = load_yaml(tp) or {}
            g = (th.get("genres", {}) or {}).get(prof["genre"], {}) or {}
            an = g.get("analyzers") or g.get("linter") or {}
            # пороги по языку поверх общих: русское тире — норма, английское — примета ИИ; объединённый порог давал
            # warning тире 23 % лидеров RU против 8 % по своему (03-corpus-measured/03 §3)
            by_lang = ((g.get("analyzers_by_lang") or {}).get(lang) or {}) if lang else {}
            if an or by_lang:
                prof["analyzers"] = merge_dict(prof.get("analyzers", {}), an)
                if by_lang:
                    prof["analyzers"] = merge_dict(prof["analyzers"], by_lang)
                src = {"thresholds": str(tp.relative_to(ROOT) if tp.is_relative_to(ROOT) else tp),
                       "provisional": bool(th.get("provisional", False))}
                if by_lang:
                    src["by_lang"] = lang
        except Exception as exc:  # pragma: no cover
            src["error"] = f"thresholds.yaml не прочитан: {exc}"
    return prof, src


# --- вход -----------------------------------------------------------------------------------------------------------
@dataclass
class Unit:
    text: str
    slot_type: str = "body"
    role: str = "marketing"
    page_id: str = ""
    section_id: str = ""
    slot_id: str = ""
    variant: str = ""
    fact_ids: list | None = None
    src_offset: int | None = None
    path: str = ""
    genre: str = ""
    lang: str = ""
    allow: list = field(default_factory=list)   # [(шаблон id правила, причина)] — lint_allow слота copy deck
    lint_type: str = ""            # тип слота для правил: lint_as слота без своих правил (copy-slots.yaml)
    key: str = ""                  # строка реестра texts.md: ключ, предел, действие, объект, группа, статус
    maxlen: str = ""
    action: str = ""
    object: str = ""
    group: str = ""
    status: str = ""


@dataclass
class Document:
    path: str
    fmt: str
    units: list
    source_text: str = ""
    genre_hint: str = ""
    notes: list = field(default_factory=list)
    registry: dict | None = None   # реестр текстов: объекты и действия продукта для межстрочных проверок
    places: list = field(default_factory=list)   # регулярки имён мест из фактов (entities[] вида place)


def ltype(u: Unit) -> str:
    """Тип слота, по которому строку выбирают правила и анализаторы."""
    return u.lint_type or u.slot_type


def role_for(slot_type: str, vocab: dict, fallback: str = "marketing") -> str:
    """Роль ux типа слота; тип не из словаря site — ошибка вызова (псевдослот парсера hr — роль fallback)."""
    if slot_type in INTERNAL_SLOTS:
        return fallback
    st = vocab["slot_types"].get(slot_type)
    if st is None:
        if vocab.get("missing"):
            raise UsageError(f"словарь site не найден: {vocab.get('path')}")
        raise UsageError(f"тип слота «{slot_type}» не из словаря site (слоты вида text: {vocab.get('path')})")
    return st.get("ux_role") or ("meta" if slot_type.startswith(("meta-", "og-")) else fallback)


def lint_type_of(slot_type: str, vocab: dict) -> str:
    return ((vocab["slot_types"].get(slot_type) or {}).get("lint_as") or "") if slot_type else ""


def md_slot(level: int, genre: str) -> str:
    if genre == "article":
        return "article-title" if level == 1 else "article-heading"
    if genre == "geo":
        return "section-title"
    return {1: "headline", 2: "section-title"}.get(level, "card-title")


def prose_slot(genre: str) -> str:
    return {"article": "article-paragraph", "geo": "geo-answer", "email-form": "email-body",
            "meta": "meta-description"}.get(genre, "body")


CAPS_LINE_RE = re.compile(r"^[^a-zа-яё]*[A-ZА-ЯЁ][^a-zа-яё]*$")


def parse_markdown(text: str, genre: str, vocab: dict, path: str) -> list[Unit]:
    units: list[Unit] = []
    lines = text.split("\n")
    offs, pos = [], 0
    for ln in lines:
        offs.append(pos)
        pos += len(ln) + 1
    i, n = 0, len(lines)
    in_code = False
    fm = False
    if lines and lines[0].strip() == "---":
        for j in range(1, min(n, 60)):
            if lines[j].strip() == "---":
                i = j + 1
                fm = True
                break
    para, para_off = [], None

    def flush():
        nonlocal para, para_off
        if para:
            t = "\n".join(para)
            st = prose_slot(genre)
            units.append(Unit(t, st, role_for(st, vocab), src_offset=para_off, path=path))
        para, para_off = [], None

    while i < n:
        ln = lines[i]
        s = ln.strip()
        if s.startswith("```"):
            flush()
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue
        if not s:
            flush()
            i += 1
            continue
        m = re.match(r"^(\s*)(#{1,6})\s+(.*)$", ln)
        if m:
            flush()
            lvl = len(m.group(2))
            st = md_slot(lvl, genre)
            if genre in ("landing", "site-page", "geo", "article") and m.group(3).rstrip().endswith("?") and lvl >= 2:
                st = "faq-q"
            off = offs[i] + ln.index(m.group(3)) if m.group(3) else offs[i]
            units.append(Unit(m.group(3), st, role_for(st, vocab), src_offset=off, path=path))
            i += 1
            continue
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", ln)
        if m:
            flush()
            off = offs[i] + len(m.group(1)) + len(m.group(2)) + 1
            units.append(Unit(m.group(3), "list-item", role_for("list-item", vocab), src_offset=off, path=path))
            i += 1
            continue
        if s.startswith(">"):
            flush()
            t = re.sub(r"^\s*>\s?", "", ln)
            units.append(Unit(t, "testimonial-quote", "user-content", src_offset=offs[i] + ln.index(t) if t else offs[i],
                              path=path))
            i += 1
            continue
        if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", ln):
            flush()
            units.append(Unit(s, "hr", "marketing", src_offset=offs[i], path=path))
            i += 1
            continue
        # короткая строка капсом перед заголовком — надзаголовок (eyebrow)
        nxt = lines[i + 1].strip() if i + 1 < n else ""
        if genre in ("landing", "site-page") and not para and len(s) <= 60 and len(words_of(s)) <= 9 \
                and CAPS_LINE_RE.match(s) and len(re.findall(r"[A-ZА-ЯЁ]", s)) >= 3 and nxt.startswith("#"):
            units.append(Unit(s, "eyebrow", role_for("eyebrow", vocab), src_offset=offs[i], path=path))
            i += 1
            continue
        if para_off is None:
            para_off = offs[i] + (len(ln) - len(ln.lstrip()))
            para.append(ln.strip())
        else:
            para.append(ln.strip())
        i += 1
    flush()
    return units


class _HTMLText(HTMLParser):
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "button", "blockquote", "figcaption", "td", "th", "label",
             "dt", "dd", "summary", "caption", "title", "small", "div", "section", "article", "header", "footer",
             "aside", "main", "nav", "form", "ul", "ol", "table", "tr", "br"}
    SKIP = {"script", "style", "noscript", "svg", "template", "iframe", "canvas"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, str, str]] = []  # (tag, text, classes)
        self.stack: list[tuple[str, str]] = []
        self.buf: list[str] = []
        self.skip = 0
        self.meta: dict = {}

    def _flush(self):
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if t:
            tag, cls = self.stack[-1] if self.stack else ("div", "")
            self.blocks.append((tag, t, cls))
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self.skip += 1
            return
        if tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key in ("description", "og:title", "og:description", "og:image:alt", "twitter:title",
                       "twitter:description") and a.get("content"):
                self.meta[key] = a["content"]
            return
        if tag == "img" and a.get("alt"):
            self.blocks.append(("img-alt", a["alt"], ""))
            return
        if tag == "input" and (a.get("type") or "").lower() in ("submit", "button") and a.get("value"):
            self.blocks.append(("button", a["value"], a.get("class", "")))
            return
        if tag in self.BLOCK or tag == "a":
            if tag == "a" and not re.search(r"btn|button|cta", a.get("class", "") or "", re.I):
                return
            self._flush()
            self.stack.append((tag if tag != "a" else "button", a.get("class", "") or ""))

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if tag in self.BLOCK or tag == "a":
            if tag == "a" and (not self.stack or self.stack[-1][0] != "button"):
                return
            self._flush()
            if self.stack:
                self.stack.pop()

    def handle_data(self, data):
        if self.skip:
            return
        self.buf.append(data)


def parse_html(text: str, genre: str, vocab: dict, path: str) -> list[Unit]:
    p = _HTMLText()
    p.feed(text)
    p._flush()
    units: list[Unit] = []
    title_seen = False
    blocks = p.blocks
    for idx, (tag, t, cls) in enumerate(blocks):
        if tag == "title":
            if not title_seen:
                units.append(Unit(t, "meta-title", "meta", path=path))
                title_seen = True
            continue
        if tag == "img-alt":
            units.append(Unit(t, "image-alt", "alt", path=path))
            continue
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            lvl = int(tag[1])
            st = md_slot(lvl, genre)
            if t.endswith("?") and lvl >= 2:
                st = "faq-q"
        elif tag == "button":
            st = "cta-label"
        elif tag == "li":
            st = "list-item"
        elif tag == "blockquote":
            st = "testimonial-quote"
        elif tag in ("figcaption", "small", "caption"):
            st = "stat-label" if len(t) < 40 else "body"
        elif tag == "label":
            st = "form-consent" if re.search(r"персональн|согласи|consent|privacy", t, re.I) else "body"
        else:
            st = prose_slot(genre)
        nxt = blocks[idx + 1][0] if idx + 1 < len(blocks) else ""
        if st in ("body", "stat-label") and nxt in ("h1", "h2") and len(t) <= 60 and len(words_of(t)) <= 9 and (
                CAPS_LINE_RE.match(t) or re.search(r"eyebrow|kicker|overline|tagline|label|subtitle-top", cls, re.I)):
            st = "eyebrow"
        units.append(Unit(t, st, role_for(st, vocab), path=path))
    meta_map = {"description": "meta-description", "og:title": "og-title", "og:description": "og-description",
                "og:image:alt": "og-image-alt"}
    for k, st in meta_map.items():
        if k in p.meta:
            units.insert(0, Unit(p.meta[k], st, role_for(st, vocab, "meta"), path=path))
    return units


def parse_allow(raw) -> list:
    out = []
    for a in (raw if isinstance(raw, list) else ([raw] if raw else [])):
        if isinstance(a, dict) and a.get("rule"):
            out.append((str(a["rule"]), str(a.get("reason", ""))))
        elif isinstance(a, str):
            out.append((a, ""))
    return out


def parse_copy_deck(data, vocab: dict, path: str, all_variants: bool = False) -> tuple[list[Unit], str]:
    """Copy deck → блоки. По умолчанию — выбранный вариант слота (без выбора — все живые); --all-variants — все живые
    варианты; отклонённые (status: rejected) не проверяются. Мета страницы несёт meta.fact_ids и lint_allow страницы.
    Короткая форма slots: [{slot_type | role | component, text}] — строки интерфейса мобильного приложения и бота."""
    units: list[Unit] = []
    genre_hint = ""

    def add_slot(slot: dict, page_id="", section_id="", genre=""):
        where = slot.get("slot_id") or slot.get("key") or slot.get("slot_type") or ""
        role = resolve_role(str(slot.get("role") or ""), str(slot.get("component") or ""), where)
        st = str(slot.get("slot_type") or ("" if role else "body"))
        role = role or role_for(st, vocab)
        lt = lint_type_of(st, vocab)
        facts = slot.get("fact_ids")
        facts = list(facts) if isinstance(facts, list) else (None if facts is None else [facts])
        allow = parse_allow(slot.get("lint_allow"))
        variants = slot.get("variants")
        if isinstance(variants, list) and variants:
            chosen = slot.get("chosen")
            for v in variants:
                if not isinstance(v, dict) or v.get("status") == "rejected":
                    continue
                if not all_variants and chosen and v.get("id") != chosen:
                    continue
                txt = v.get("text") or ""
                if not str(txt).strip():
                    continue
                vf = v.get("fact_ids")
                vf = list(vf) if isinstance(vf, list) else None
                units.append(Unit(str(txt), st, role, page_id, section_id, slot.get("slot_id", ""),
                                  str(v.get("id", "")), vf if vf is not None else (facts if facts is not None else []),
                                  path=path, genre=genre, allow=allow, lint_type=lt, key=str(slot.get("key") or "")))
        elif slot.get("text"):
            units.append(Unit(str(slot["text"]), st, role, page_id, section_id, slot.get("slot_id", ""),
                              "", facts if facts is not None else [], path=path, genre=genre, allow=allow, lint_type=lt,
                              key=str(slot.get("key") or "")))

    root = data.get("copy_deck", data) if isinstance(data, dict) else data
    if isinstance(root, dict) and "pages" in root:
        for page in root.get("pages") or []:
            if page.get("status") == "rejected":
                continue
            pt = page.get("page_type", "")
            genre = (vocab["page_types"].get(pt) or {}).get("genre", "") or page.get("genre", "")
            genre_hint = genre_hint or genre
            meta = page.get("meta") or {}
            mfacts = [str(x) for x in meta.get("fact_ids") or []] if isinstance(meta.get("fact_ids"), list) else []
            pallow = parse_allow(page.get("lint_allow"))
            for k, st in (("title", "meta-title"), ("description", "meta-description"), ("og_title", "og-title"),
                          ("og_description", "og-description")):
                if meta.get(k):
                    units.append(Unit(str(meta[k]), st, role_for(st, vocab, "meta"), page.get("page_id", ""), "meta",
                                      st, "", list(mfacts), path=path, genre="meta", allow=pallow))
            for sec in page.get("sections") or []:
                for slot in sec.get("slots") or []:
                    add_slot(slot, page.get("page_id", ""), sec.get("section_id", ""), genre)
    else:
        items = root.get("slots", []) if isinstance(root, dict) else root
        if isinstance(root, dict) and root.get("genre"):
            genre_hint = root["genre"]
        for slot in items or []:
            if isinstance(slot, dict):
                add_slot(slot, slot.get("page_id", ""), slot.get("section_id", ""), slot.get("genre", ""))
    return units, genre_hint


PLACE_RULES = {"ux-6-4-10"}     # слово на «-ая,» в адресе и названии места — не деепричастный оборот
_PLACES: dict = {}


def place_patterns(facts_path: str | Path) -> list:
    """Имена сущностей вида place файла фактов (entities[]) → регулярки: без регистра, целым словом, пробел имени —
    любой пробел, дефис — любое тире. Нет файла или сущностей — пустой список."""
    p = Path(facts_path)
    key = (str(p), _mtime(p))
    if key not in _PLACES:
        out = []
        data = (load_yaml(p) or {}) if p.is_file() else {}
        for e in (data.get("entities") or []) if isinstance(data, dict) else []:
            if not isinstance(e, dict) or e.get("type") != "place":
                continue
            for name in e.get("names") or []:
                parts = [r"\s+" if x.isspace() else r"[-‐‑–—−]" if x in "-‐‑–—−" else re.escape(x)
                         for x in re.split(r"(\s+|[-‐‑–—−])", str(name).strip()) if x]
                if parts:
                    out.append(re.compile(r"(?<!\w)" + "".join(parts) + r"(?!\w)", re.I))
        _PLACES[key] = out
    return _PLACES[key]


def is_registry(path: str, text: str, fmt: str = "") -> bool:
    """Реестр текстов интерфейса: формат texts или файл texts.md с таблицей key · role · text."""
    if fmt == "texts":
        return True
    return (not fmt or fmt in ("md", "markdown")) and Path(path).name == "texts.md" and \
        bool(re.search(r"^\|\s*key\s*\|\s*role\s*\|\s*text\s*\|", text, re.M))


def product_tables(registry_path: str, objects_path: str = "", actions_path: str = "") -> dict:
    """Глоссарий объектов (object.md: name, aliases, statuses) и словарь действий (action.md: verb, past, banned,
    objects) проекта. Без явных путей — файлы продукта рядом с реестром: docs/projects/<slug>/screens/<surface>/texts.md
    → docs/projects/<slug>/object.md, action.md."""
    L = _layer()
    rp = Path(registry_path)
    project = rp.resolve().parents[2] if len(rp.resolve().parents) > 2 and rp.resolve().parents[1].name == "screens" else None
    op = Path(objects_path) if objects_path else (project / "object.md" if project else None)
    ap = Path(actions_path) if actions_path else (project / "action.md" if project else None)
    out = {"objects": {}, "actions": {}, "objects_path": str(op) if op and op.is_file() else "",
           "actions_path": str(ap) if ap and ap.is_file() else ""}

    def words(cell):
        v = L.cell(cell) or ""
        return [x.strip().strip("«»\"") for x in re.split(r"[,;/]", v) if x.strip().strip("«»\"")]
    if op and op.is_file():
        tb = L.Md(op).table(("slug", "name"))
        for r in tb.rows if tb else []:
            slug = L.cell(r.get("slug"))
            if slug and not L.is_empty(slug):
                out["objects"][slug] = {"name": L.cell(r.get("name")) or "", "aliases": words(r.get("aliases")),
                                        "line": r.line}
    if ap and ap.is_file():
        tb = L.Md(ap).table(("slug", "verb"))
        for r in tb.rows if tb else []:
            slug = L.cell(r.get("slug"))
            if slug and not L.is_empty(slug):
                out["actions"][slug] = {"verb": L.cell(r.get("verb")) or "", "past": L.cell(r.get("past")) or "",
                                        "banned": words(r.get("banned")), "objects": L.refs(r.get("objects")),
                                        "line": r.line}
    return out


def parse_registry(path: str, text: str) -> tuple[list[Unit], list[str]]:
    """Реестр texts.md → блоки со строками интерфейса: текст, роль (закрытый список), ключ, maxlen, действие, объект,
    группа, статус; место находки — строка файла. Роль вне списка — ошибка вызова."""
    L = _layer()
    reg = L.Texts(path)
    if reg.table is None:
        raise UsageError(f"{path}: нет таблицы реестра с колонками key, role, text")
    lines = text.split("\n")
    offs, pos = [], 0
    for ln in lines:
        offs.append(pos)
        pos += len(ln) + 1
    bad, units, notes = [], [], []
    for key, row in reg.rows.items():
        if not row.role or row.role not in closed_roles():
            bad.append(f"{key} (строка {row.line}): «{row.role or '—'}»")
            continue
        body = row.text.strip()
        if body.startswith(("«", "\"")) and body.endswith(("»", "\"")) and len(body) > 1:
            body = body[1:-1]
        if not body or L.is_empty(body):
            continue
        raw = lines[row.line - 1] if 0 < row.line <= len(lines) else ""
        at = raw.find(body)
        u = Unit(body, "", row.role, slot_id=key, path=path, genre="interface",
                 src_offset=(offs[row.line - 1] + at) if at >= 0 else None, key=key, maxlen=row.maxlen or "",
                 action=row.action or "", object=row.object or "", group=row.group or "", status=row.status or "")
        units.append(u)
    if bad:
        raise UsageError(f"{path}: роль строки не из закрытого списка ux 07/06 §7.2 и body — " + "; ".join(bad[:6]))
    for d in reg.duplicates:
        notes.append(f"ключ {d.key} повторён (строка {d.line}) — проверена первая строка")
    return units, notes


def read_document(path: str, genre: str, vocab: dict, all_variants: bool = False, slot_type: str = "",
                  fmt: str = "", role: str = "", component: str = "", objects: str = "", actions: str = "") -> Document:
    if path == "-":
        text = sys.stdin.read()
        ext = fmt or "md"
    else:
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        ext = fmt or p.suffix.lower().lstrip(".")
    text = text.lstrip("\ufeff") if text.startswith("\ufeff") else text
    doc = Document(path, ext, [], text)
    if path != "-" and is_registry(path, text, fmt):
        if role or component or slot_type:
            raise UsageError("у реестра texts.md роль — колонка role: ключи --role, --component и --slot-type к нему не "
                             "применяются")
        doc.units, doc.notes = parse_registry(path, text)
        doc.fmt, doc.genre_hint = "texts", "interface"
        doc.registry = product_tables(path, objects, actions)
        for k, what in (("objects_path", "глоссарий объектов object.md"), ("actions_path", "словарь действий action.md")):
            if not doc.registry[k]:
                doc.notes.append(f"{what} не найден — проверки, которые его читают, пропущены")
        return doc
    if ext in ("yaml", "yml"):
        data = yaml.safe_load(text)
        units, ghint = parse_copy_deck(data, vocab, path, all_variants)
        doc.units, doc.genre_hint = units, ghint
        doc.source_text = ""
        root = data.get("copy_deck", data) if isinstance(data, dict) else {}
        if path != "-" and isinstance(root, dict) and root.get("facts_ref"):
            doc.places = place_patterns(Path(path).parent / str(root["facts_ref"]))
    elif ext in ("html", "htm"):
        doc.units = parse_html(text, genre or "landing", vocab, path)
        doc.source_text = ""
    else:
        doc.units = parse_markdown(text, genre or "landing", vocab, path)
        doc.fmt = "md" if ext in ("md", "markdown") else "txt"
    urole = resolve_role(role, component, "--role" if role else "")
    if genre == "interface" and not urole and not slot_type and ext not in ("yaml", "yml"):
        urole = "body"
        doc.notes.append("жанр interface без роли (--role, --component): строки проверены как body")
    if slot_type:
        srole = role_for(slot_type, vocab)
        for u in doc.units:
            u.slot_type, u.role, u.lint_type = slot_type, srole, lint_type_of(slot_type, vocab)
    if urole:
        for u in doc.units:
            u.role = urole
            if not slot_type:
                u.slot_type, u.lint_type = "", ""
    else:
        for u in doc.units:
            u.lint_type = u.lint_type or lint_type_of(u.slot_type, vocab)
    return doc


# --- находки --------------------------------------------------------------------------------------------------------
@dataclass
class Finding:
    id: str
    marker_id: str
    level: str
    group: str
    message: str
    fragment: str = ""
    context: str = ""
    unit: int = -1
    start: int = -1
    end: int = -1
    line: int | None = None
    col: int | None = None
    replacement: str = ""
    example: dict = field(default_factory=dict)
    source: str = ""
    evidence: str = ""
    slot: dict = field(default_factory=dict)
    count_as_marker: bool = False
    note: str = ""
    tell: str = ""                 # id приметы реестра kb/common/tells.yaml (раздел checks)

    def as_dict(self) -> dict:
        d = {"id": self.id, "marker_id": self.marker_id, "level": self.level, "group": self.group,
             "message": self.message, "fragment": self.fragment, "context": self.context,
             "position": {"unit": self.unit, "start": self.start, "end": self.end, "line": self.line,
                          "col": self.col},
             "replacement": self.replacement, "example": self.example, "source": self.source,
             "evidence": self.evidence, "slot": self.slot, "counts_as_marker": self.count_as_marker}
        if self.note:
            d["note"] = self.note
        if self.tell:
            d["tell"] = self.tell
        return d


_TELLS: dict = {}


def tells_of_checks() -> dict:
    """id приметы по id правила или анализатора: ключи copy_lint:<id> раздела checks реестра примет."""
    key = _mtime(TELLS_PATH)
    if key not in _TELLS:
        d = (load_yaml(TELLS_PATH) or {}) if TELLS_PATH.exists() else {}
        _TELLS.clear()
        _TELLS[key] = {k[len(TELL_KEY):]: v.get("tell") for k, v in (d.get("checks") or {}).items()
                       if isinstance(k, str) and k.startswith(TELL_KEY) and isinstance(v, dict) and v.get("tell")}
    return _TELLS[key]


def effective_level(rule: Rule, genre: str, unit: Unit, profile: dict) -> str:
    lvl = rule.levels.get(genre, rule.level) if rule.levels else rule.level
    if rule.slot_levels and ltype(unit) in rule.slot_levels:
        lvl = rule.slot_levels[ltype(unit)]
    ov = (profile.get("level_overrides") or {})
    for pat, v in ov.items():
        if fnmatch.fnmatch(rule.id, pat):
            lvl = v
    grp = (profile.get("groups") or {}).get(rule.group, {}) or {}
    if grp.get("enabled") is False:
        return "off"
    cap = grp.get("max_level")
    if cap and LEVEL_RANK.get(lvl, 0) > LEVEL_RANK.get(cap, 3):
        lvl = cap
    floor_ = grp.get("min_level")
    if floor_ and lvl != "off" and LEVEL_RANK.get(lvl, 0) < LEVEL_RANK.get(floor_, 0):
        lvl = floor_
    return lvl


def rule_applies(rule: Rule, unit: Unit, genre: str, lang: str) -> bool:
    """Место правила: у слота сайта — тип слота (slot_types), у строки без типа (реестр интерфейса, --role) — роль
    (appliesTo); правило только с типами слотов строку без типа не проверяет."""
    if rule.kind in ("analyzer", "manual"):
        return False
    if rule.lang not in ("any", lang):
        return False
    if rule.genres and genre not in rule.genres:
        return False
    st = ltype(unit)
    if rule.slot_types and st:
        if not any(fnmatch.fnmatch(st, s) for s in rule.slot_types):
            return False
    elif rule.slot_types and not rule.appliesTo:
        return False
    elif rule.appliesTo and unit.role not in rule.appliesTo:
        return False
    if rule.excludes and unit.role in rule.excludes:
        return False
    # отзыв и цитата клиента (роль user-content) стилистически не правятся: только артефакты (ART) и данные (CNT)
    if unit.role == "user-content" and rule.group in STYLE_GROUPS and "user-content" not in (rule.appliesTo or []):
        return False
    if rule.exclude_slot_types and st and any(fnmatch.fnmatch(st, s) for s in rule.exclude_slot_types):
        return False
    return True


def line_col(src: str, offset: int) -> tuple[int, int]:
    line = src.count("\n", 0, offset) + 1
    col = offset - (src.rfind("\n", 0, offset) + 1) + 1
    return line, col


def context_of(text: str, s: int, e: int, width: int = 40) -> str:
    a, b = max(0, s - width), min(len(text), e + width)
    return ("…" if a > 0 else "") + norm_spaces(text[a:b]).replace("\n", " ") + ("…" if b < len(text) else "")


def slot_info(u: Unit) -> dict:
    d = {"slot_type": u.slot_type, "role": u.role}
    if u.lint_type and u.lint_type != u.slot_type:
        d["lint_as"] = u.lint_type
    for k in ("page_id", "section_id", "slot_id", "variant", "key"):
        v = getattr(u, k)
        if v:
            d[k] = v
    return d


def sentence_of(text: str, pos: int) -> tuple[int, int]:
    for s, e in split_sentences(text):
        if s <= pos < e:
            return s, e
    return 0, len(text)


MORPH_REPLACES = {"ru-syn-gerund-tail", "ru-syn-genitive-chain", "ru-syn-passive", "ru-syn-passive-agent"}
NBSP_AFTER_RULES = {"typo-hanging-preposition"}   # правка — неразрывный пробел после найденного слова


def fix_from_text(r: Rule, text: str, m: re.Match) -> tuple[str, dict]:
    """Правка и пример находки. У правил о неразрывном пробеле после короткого слова — из текста находки: найденное
    слово связано со следующим («в городе» → «в⍽городе», ⍽ — U+00A0); у остальных — правка и примеры правила."""
    if r.id in NBSP_AFTER_RULES:
        nxt = re.match(r"[«\"]?[" + WORDCH + r"]+(?:-[" + WORDCH + r"]+)*", text[m.end():])
        if nxt:
            word = m.group(0).strip()
            good = f"{word}\u00a0{nxt.group(0)}"
            return f"«{good}» — неразрывный пробел после «{word}»", {"bad": f"{word} {nxt.group(0)}", "good": good}
    return r.replacement, r.examples or {}


def run_rules(doc: Document, rules: list[Rule], genre: str, lang: str, profile: dict,
              skip_ids: set | None = None) -> list[Finding]:
    out: list[Finding] = []
    doc_hits: dict = {}  # правила со scope: doc — копим находки по документу, решаем по min_count в конце
    for ui, u in enumerate(doc.units):
        ulang = u.lang or lang
        ugenre = u.genre or genre
        masks = masked_spans(u.text)
        icu = icu_spans(u.text) if ugenre == "interface" else []
        places = [m.span() for rx in doc.places for m in rx.finditer(u.text)] if doc.places else []
        for r0 in rules:
            if skip_ids and r0.id in skip_ids:
                continue
            r = r0.for_genre(ugenre)
            if not rule_applies(r, u, ugenre, ulang):
                continue
            lvl = effective_level(r, ugenre, u, profile)
            if lvl == "off":
                continue
            if r.requires_no_fact and u.fact_ids:
                continue
            hits = []
            for m in r.regex.finditer(u.text):
                if m.end() == m.start():
                    continue
                if r.mask_quotes and inside((m.start(), m.end()), masks):
                    continue
                if icu and r.group == "ART" and inside((m.start(), m.end()), icu):
                    continue          # подстановка ICU {name} в строке интерфейса — синтаксис, а не шаблон-заглушка
                if places and r.id in PLACE_RULES and any(a <= m.start() < b for a, b in places):
                    continue          # слово внутри адреса или названия места из фактов
                if r.unless_re is not None:
                    ss, se = sentence_of(u.text, m.start())
                    if r.unless_re.search(u.text[ss:se]):
                        continue
                hits.append(m)
            if r.scope == "doc":
                doc_hits.setdefault(r.id, (r, lvl, []))[2].extend((ui, u, m) for m in hits)
                continue
            if len(hits) < max(1, r.min_count):
                continue
            for m in hits:
                fix, example = fix_from_text(r, u.text, m)
                f = Finding(r.id, r.marker_id, lvl, r.group, r.message, fragment=m.group(0)[:120],
                            context=context_of(u.text, m.start(), m.end()), unit=ui, start=m.start(), end=m.end(),
                            replacement=fix, example=example, source=r.source,
                            evidence=r.evidence, slot=slot_info(u), count_as_marker=bool(r.count_as_marker),
                            note=r.note)
                if u.src_offset is not None and doc.source_text:
                    f.line, f.col = line_col(doc.source_text, u.src_offset + m.start())
                out.append(f)
    for rid, (r, lvl, lst) in doc_hits.items():
        if len(lst) < max(1, r.min_count):
            continue
        for ui, u, m in lst:
            f = Finding(r.id, r.marker_id, lvl, r.group, r.message, fragment=m.group(0)[:120],
                        context=context_of(u.text, m.start(), m.end()), unit=ui, start=m.start(), end=m.end(),
                        replacement=r.replacement, example=r.examples or {}, source=r.source, evidence=r.evidence,
                        slot=slot_info(u), count_as_marker=bool(r.count_as_marker), note=r.note)
            if u.src_offset is not None and doc.source_text:
                f.line, f.col = line_col(doc.source_text, u.src_offset + m.start())
            out.append(f)
    prio = {r.id: r.priority for r in rules}
    # одно и то же место одним правилом — одна находка; у двух правил — остаётся приоритетное, затем более строгое
    best: dict = {}
    for f in out:
        k = (f.unit, f.start, f.end, f.group == "ART")
        cur = best.get(k)
        key = (prio.get(f.id, 50), LEVEL_RANK.get(f.level, 0), f.group != "UX")
        if cur is None or key > cur[0]:
            if cur is not None and cur[1].id != f.id:
                f.note = (f.note + " " if f.note else "") + f"(то же место: {cur[1].id})"
            best[k] = (key, f)
        elif cur[1].id != f.id:
            cur[1].note = (cur[1].note + " " if cur[1].note else "") + f"(то же место: {f.id})"
    uniq = [v[1] for v in best.values()]
    # унаследованное правило ux, перекрытое своим правилом того же места, — только отметкой
    ours = [f for f in uniq if f.group != "UX"]
    final = []
    for f in uniq:
        if f.group == "UX" and any(o.unit == f.unit and o.start < f.end and f.start < o.end for o in ours):
            continue
        final.append(f)
    return final


def merged_marker_spans(findings: list[Finding]) -> int:
    """Число «кластеров» маркеров: перекрывающиеся находки в одном блоке считаются одной."""
    by_unit: dict = {}
    for f in findings:
        if f.start < 0:
            by_unit.setdefault((f.unit, id(f)), []).append((0, 0))
            continue
        by_unit.setdefault(f.unit, []).append((f.start, f.end))
    total = 0
    for spans in by_unit.values():
        spans.sort()
        cur_end = -1
        for s0, e0 in spans:
            if s0 >= cur_end or (s0 == 0 and e0 == 0):
                total += 1
                cur_end = e0
            else:
                cur_end = max(cur_end, e0)
    return total


# --- анализаторы и метрики ----------------------------------------------------------------------------------------
CONNECTIVES_RU = ["но", "однако", "поэтому", "потому что", "так что", "зато", "при этом", "а", "и", "если", "когда",
                  "чтобы", "хотя", "ведь", "то есть", "значит", "вот почему", "в итоге", "сначала", "потом", "затем",
                  "тогда", "иначе", "впрочем", "например", "кстати", "даже", "только", "ещё", "уже", "всё же",
                  "из-за", "благодаря", "вместо", "после", "до", "пока", "раз", "так как", "поскольку", "который",
                  "которая", "которые", "которое", "где", "куда", "что", "как"]
CONNECTIVES_EN = ["but", "so", "because", "however", "and", "if", "when", "although", "though", "which", "that",
                  "then", "yet", "while", "since", "unless", "instead", "for example", "for instance", "even", "only",
                  "still", "after", "before", "until", "whereas", "who", "where", "what", "how"]
INFORMAL_RU = ["короче", "ну", "вот", "кстати", "честно", "блин", "типа", "как бы", "в общем", "такие дела", "окей",
               "ага", "ладно", "прикиньте", "фигня", "вообще-то", "по фану", "чё", "щас"]
INFORMAL_EN = ["honestly", "look", "kinda", "gonna", "wanna", "tbh", "lol", "okay so", "anyway", "basically",
               "literally", "y'know", "stuff", "folks"]
UNITS_RE = re.compile(r"%B%(?:\d[\d\s.,]*\s?(?:%|‰|₽|руб\w*|р\.|\$|€|£|млн|млрд|тыс\w*|км|кг|г|мг|мл|л|м²|м2|м|см|мм|"
                      r"ч|час\w*|мин\w*|сек\w*|дн\w*|дня|недел\w*|мес\w*|лет|год\w*|шт|кВт|Вт|ГБ|МБ|ТБ|Гб|Мб|px|ms|"
                      r"kg|km|min|hrs?|hours?|days?|weeks?|months?|years?|users?|customers?|%)?)".replace("%B%", B_MACRO))
YEAR_RE = re.compile(B_MACRO + r"(?:19|20)\d\d" + E_MACRO)
MONTHS_RE = re.compile(B_MACRO + r"(?:январ|феврал|март|апрел|ма[йя]|июн|июл|август|сентябр|октябр|ноябр|декабр|"
                       r"january|february|march|april|may|june|july|august|september|october|november|december)\w*",
                       re.I)
PROPER_RE = re.compile(r"(?<![" + WORDCH + r"])[A-ZА-ЯЁ][a-zа-яё][" + WORDCH + r"-]*")
ACRONYM_RE = re.compile(r"(?<![" + WORDCH + r"])[A-ZА-ЯЁ]{2,6}(?![" + WORDCH + r"])")


def count_proper_names(t: str) -> int:
    """Слова с заглавной не в начале предложения (имена, бренды, города) — приближение без NER."""
    n = 0
    for m in PROPER_RE.finditer(t):
        j = m.start() - 1
        while j >= 0 and t[j] in " \t«\"“„(—–-":
            j -= 1
        if j < 0 or t[j] in ".!?…\n:;":
            continue
        n += 1
    return n
DASH_RE = re.compile(r"(?:(?<=\S)\s+[—–]\s+(?=\S))|(?:(?<=[" + LETTER + r"])—(?=[" + LETTER + r"]))")
RANGE_DASH_RE = re.compile(r"\d\s*[—–]\s*\d")
HYPHEN_AS_DASH_RE = re.compile(r"(?<=[" + LETTER + r"»\"”)])\s-\s(?=[" + LETTER + r"«\"“(])")
NOT_X_BUT_Y_RU = re.compile(B_MACRO + r"не\s+(?!только|просто|раз|менее|более|то|так|без|лишн)[^.,;:!?\n]{1,40},\s+а" + E_MACRO,
                            re.I)
NOT_X_BUT_Y_EN = re.compile(r"\b(?:not|isn['’]t|aren['’]t|wasn['’]t|don['’]t|doesn['’]t)\s+(?:just\s+|only\s+|about\s+)?"
                            r"[^.,;:!?\n]{1,40},\s+(?:but|it['’]s|they['’]re|we['’]re)\b", re.I)
TRIAD_RU = re.compile(B_MACRO + r"([А-Яа-яЁё]{3,}(?:\s[А-Яа-яЁё]{3,})?),\s([А-Яа-яЁё]{3,}(?:\s[А-Яа-яЁё]{3,})?)\s+"
                      r"(?:и|или|а\sтакже)\s+([А-Яа-яЁё]{3,}(?:\s[А-Яа-яЁё]{3,})?)" + E_MACRO)
TRIAD_EN = re.compile(r"\b([A-Za-z]{3,}(?:\s[A-Za-z]{3,})?),\s([A-Za-z]{3,}(?:\s[A-Za-z]{3,})?),?\s+(?:and|or)\s+"
                      r"([A-Za-z]{3,}(?:\s[A-Za-z]{3,})?)\b")
VERB_SUFFIX_RU = re.compile(r"(ует|яет|ает|еет|ит|ат|ят|ют|ет|ут|ал|ял|ил|ел|ла|ли|ся|сь|ть|ешь|ишь|ем|им)$")
VERB_EN = re.compile(r"\b(?:is|are|was|were|has|have|had|do|does|did|can|will|would|should|could|may|might|must)\b|"
                     r"\b\w+(?:ed|es|s)\b", re.I)
FACT_CLAIM_RE = re.compile(
    r"(?:" + B_MACRO + r"(?:№|#)\s?1" + E_MACRO +
    r"|" + B_MACRO + r"\d[\d  ]*(?:[.,]\d+)?\s?(?:%|процент\w*)" +
    r"|" + B_MACRO + r"\d[\d  ]*(?:[.,]\d+)?\s?(?:\+|x|×|k\+|K\+|M\+|тыс\.?\+?)(?![" + WORDCH + r"])" +
    r"|" + B_MACRO + r"(?:x|×)\s?\d+" + E_MACRO +
    r"|" + B_MACRO + r"\d[.,]\d\s?(?:из|/|out\sof)\s?(?:5|10)" + E_MACRO +
    r"|" + B_MACRO + r"(?:в\s)?\d[\d  ]*\s(?:раз\w*|times)" + E_MACRO +
    r"|" + B_MACRO + r"\d[\d  ]*\s(?:клиент\w*|покупател\w*|пользовател\w*|компани\w*|проект\w*|заказ\w*|отзыв\w*|"
    r"сотрудник\w*|специалист\w*|партн[её]р\w*|брендов|магазин\w*|город\w*|стран\w*|лет|года?|customers|clients|users|"
    r"companies|projects|teams|years|reviews|brands|countries)" + E_MACRO +
    r"|" + B_MACRO + r"(?:более|свыше|больше|около|почти|over|more\sthan|nearly|almost)\s\d[\d  ]*" +
    r"|" + B_MACRO + r"(?:в\s)?(?:два|две|три|четыре|пять|шесть|семь|восемь|девять|десять|полтора)\s+раз[а]?" + E_MACRO +
    r"|" + B_MACRO + r"(?:вдвое|втрое|вчетверо|впятеро|вдесятеро|двукратн\w*|тр[её]хкратн\w*|многократн\w*)" + E_MACRO +
    r"|" + B_MACRO + r"(?:десятк\w*|сотн\w*|тысяч\w*|миллион\w*)\s+(?:довольн\w*\s+)?(?:клиент\w*|покупател\w*|"
    r"пользовател\w*|компани\w*|проект\w*|заказ\w*|отзыв\w*)" + E_MACRO +
    r"|\b(?:twice|three\s+times|(?:two|three|ten)fold|thousands\s+of\s+(?:customers|users|clients|companies))\b" +
    r")", re.I)
EYEBROW_SLOTS = {"eyebrow"}
HEADING_SLOTS = {"headline", "section-title", "article-title", "article-heading", "case-title", "form-title"}


def sentence_lengths(texts: list[str]) -> list[int]:
    out = []
    for t in texts:
        for s, e in split_sentences(t):
            n = len(words_of(t[s:e]))
            if n:
                out.append(n)
    return out


def stats_rhythm(lengths: list[int]) -> dict:
    if not lengths:
        return {"sentences": 0}
    n = len(lengths)
    mean = sum(lengths) / n
    sd = (sum((x - mean) ** 2 for x in lengths) / n) ** 0.5
    diffs = [abs(a - b) for a, b in zip(lengths, lengths[1:])]
    return {"sentences": n, "mean_len": round(mean, 2), "sd_len": round(sd, 2),
            "mean_abs_diff": round(sum(diffs) / len(diffs), 2) if diffs else None,
            "share_short_le8": round(sum(1 for x in lengths if x <= 8) / n, 3),
            "share_long_ge25": round(sum(1 for x in lengths if x >= 25) / n, 3),
            "max_len": max(lengths), "min_len": min(lengths)}


# без морфологии повтор ищется только среди глаголов, которые модели чаще всего дублируют (humanizer-ru п.33);
# полный поиск по основам давал шум на человеческих текстах (опыт C/02)
REPEAT_VERBS_RU = re.compile(r"(?<![а-яё])(позволя|помога|предлага|обеспечива|поддержива|да[её]т|дают|дела[ею]т|"
                             r"показыва|использу|осуществля|созда[ёе]т|создают|демонстриру|способству|формиру|реализу|"
                             r"улучша|повыша|сокраща|оптимизиру|автоматизиру|гарантиру|отвеча)", re.I)


def listed_verb_stems_ru(sentence: str) -> set:
    return {m.group(1).lower().replace("ё", "е").replace("дают", "дает") for m in REPEAT_VERBS_RU.finditer(sentence)}


def verb_stems_ru(sentence: str) -> set:
    stems = set()
    for w in re.findall(r"[а-яё]{5,}", sentence.lower()):
        if VERB_SUFFIX_RU.search(w):
            st = VERB_SUFFIX_RU.sub("", w)[:6]
            if len(st) >= 4:
                stems.add(st)
    return stems


_MORPH = None


def get_morph(mode: str):
    global _MORPH
    if mode == "off":
        return None
    if _MORPH is None:
        try:
            import pymorphy3  # type: ignore
            _MORPH = pymorphy3.MorphAnalyzer()
        except Exception:
            _MORPH = False
            if mode == "on":
                raise SystemExit("copy_lint: --morph on, но pymorphy3 не найден (запустите интерпретатором "
                                 "$DDD_HOME/venv/bin/python)")
    return _MORPH or None


TOKEN_RU = re.compile(r"[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)?|[A-Za-z0-9]+|[,.!?;:—–]")
REFLEXIVE_CANC = {"осуществляться", "производиться", "проводиться", "реализовываться", "обеспечиваться",
                  "предоставляться", "оказываться", "формироваться", "выполняться", "обрабатываться"}


def morph_findings(doc: Document, rules: list[Rule], genre: str, profile: dict, morph) -> list[Finding]:
    """Деепричастные хвосты, цепочки родительных и пассив по pymorphy3 (опыт C/03: полнота 1,0 против 0,57–0,75 у
    регулярок на размеченном наборе). Заменяет одноимённые регулярные правила, когда морфология доступна."""
    rb = {r.id: r for r in rules}
    out: list[Finding] = []

    def emit(rid, ui, u, s0, e0):
        r = rb.get(rid)
        if r is None:
            return
        r = r.for_genre(u.genre or genre)
        lvl = effective_level(r, u.genre or genre, u, profile)
        if lvl == "off" or not rule_applies(r, u, u.genre or genre, "ru"):
            return
        f = Finding(r.id, r.marker_id, lvl, r.group, r.message, fragment=u.text[s0:e0][:120],
                    context=context_of(u.text, s0, e0), unit=ui, start=s0, end=e0, replacement=r.replacement,
                    example=r.examples or {}, source=r.source, evidence=r.evidence, slot=slot_info(u),
                    count_as_marker=bool(r.count_as_marker), note="морфология pymorphy3")
        if u.src_offset is not None and doc.source_text:
            f.line, f.col = line_col(doc.source_text, u.src_offset + s0)
        out.append(f)

    for ui, u in enumerate(doc.units):
        if u.role in ("user-content",) or (u.lang and u.lang != "ru"):
            continue
        masks = masked_spans(u.text)
        for ss, se in split_sentences(u.text):
            sent = u.text[ss:se]
            toks = [(m.group(0), ss + m.start(), ss + m.end()) for m in TOKEN_RU.finditer(sent)]
            words = [t for t in toks if t[0] not in ",.!?;:—–"]
            if not words:
                continue
            parsed = {id(t): morph.parse(t[0]) for t in toks}
            best = lambda t: parsed[id(t)][0]
            # деепричастный хвост: «, <деепричастие> … .» без личного глагола до конца предложения
            for i, t in enumerate(toks):
                if t[0] == "," and i + 1 < len(toks) and best(toks[i + 1]).tag.POS == "GRND":
                    rest = toks[i + 2:]
                    if not any(best(x).tag.POS == "VERB" for x in rest if x[0] not in ",.!?;:—–"):
                        if not inside((t[1], se), masks):
                            emit("ru-syn-gerund-tail", ui, u, t[1], se)
                        break
            # цепочка: ≥ 3 существительных в родительном подряд после вершины
            run, start = 0, None
            for i, t in enumerate(words):
                ps = parsed[id(t)][:3]
                b0 = ps[0]
                gent = (b0.tag.POS == "NOUN" and "gent" in b0.tag) or (
                    b0.tag.POS == "NOUN" and any(p.tag.POS == "NOUN" and "gent" in p.tag and p.score >= 0.2
                                                 for p in ps[1:]))
                if i > 0 and gent:
                    run += 1
                    start = t[1] if run == 1 else start
                    end = t[2]
                else:
                    if run >= 3 and not inside((start, end), masks):
                        emit("ru-syn-genitive-chain", ui, u, start, end)
                    run, start = 0, None
            if run >= 3 and not inside((start, end), masks):
                emit("ru-syn-genitive-chain", ui, u, start, end)
            # пассив: краткое страдательное причастие (кроме коротких статусов), возвратный глагол канцелярита,
            # «нами»
            low = [w[0].lower() for w in words]
            if "нами" in low:
                j = low.index("нами")
                emit("ru-syn-passive-agent", ui, u, words[j][1], words[min(len(words) - 1, j + 3)][2])
                continue
            for i, t in enumerate(words):
                p = best(t)
                if (p.tag.POS == "PRTS" and "pssv" in p.tag and len(words) > 2) or \
                        (p.tag.POS == "VERB" and p.normal_form in REFLEXIVE_CANC):
                    if not inside((t[1], t[2]), masks):
                        emit("ru-syn-passive", ui, u, t[1], t[2])
                    break
    return out


def verb_lemmas_ru(sentence: str, morph) -> set:
    out = set()
    for w in re.findall(r"[а-яё]+", sentence.lower()):
        p = morph.parse(w)[0]
        if p.tag.POS in ("VERB", "INFN"):
            out.add(p.normal_form)
    return out


def count_connective_sentences(sents: list[str], lang: str) -> int:
    lst = CONNECTIVES_RU if lang == "ru" else CONNECTIVES_EN
    pat = re.compile(B_MACRO + r"(?:" + "|".join(re.escape(c) for c in sorted(lst, key=len, reverse=True)) + r")" +
                     E_MACRO, re.I)
    return sum(1 for s in sents if pat.search(s))


# Личная форма глагола по окончанию (без морфологии). «-ем» — только после гласной (делаем, проверяем: «систем»,
# «совсем», «всем» не глаголы), «-им» — только после в т д с з б п л м р (доставим, говорим: «многолетним», «лучшим»,
# «таким», «режим» не глаголы); повелительное -ите/-ьте/-йте. Опыт C/05 — где это ошибается.
FINITE_VERB_RU = re.compile(r"(?:ет|ют|ут|ит|ат|ят|ешь|ишь|ете|ите|(?<=[аяуюе])ем|(?<=[втдсзбплмр])им|ал|ял|ил|ел|ла|ли|"
                            r"ло|лся|лась|лись|лось|ется|ются|ится|ятся|ешься|ишься|ьте|йте|итесь|ьтесь|йтесь)$")
FINITE_YO_RU = re.compile(r"(?:ёт|ёшь|ёте|ётся|[бвгджзклмнпрстфхцшщ]ём)$")   # идёт, даёт, начнём, пришлём
# существительные, наречия и союзы с «глагольными» окончаниями — частые в текстах сайтов (ё записано как е)
NOT_VERB_RU = {
    # -ет, -ете, -ёт
    "бюджет", "объект", "пакет", "предмет", "совет", "ответ", "билет", "кабинет", "портрет", "сюжет", "интернет",
    "секрет", "букет", "цвет", "свет", "рассвет", "привет", "запрет", "паркет", "макет", "планшет", "приоритет",
    "авторитет", "паритет", "комитет", "факультет", "университет", "иммунитет", "менталитет", "балет", "туалет",
    "скелет", "жилет", "омлет", "брикет", "квартет", "берет", "сорбет", "обет", "отчет", "счет", "расчет", "учет",
    "полет", "самолет", "вертолет", "зачет", "почет", "взлет", "перелет", "налет", "пулемет", "смет", "анкет",
    "конфет", "монет", "планет", "газет", "диет", "ракет", "примет", "кассет", "интернете", "бюджете", "кабинете",
    "пакете", "ответе", "совете", "билете", "портрете", "сюжете", "секрете", "предмете", "приоритете", "планшете",
    "паркете", "макете", "цвете", "свете", "отчете", "счете", "расчете", "учете", "полете", "самолете",
    # -ут, -ют, -ит, -ите, -йте
    "минут", "маршрут", "институт", "атрибут", "валют", "приют", "салют", "кают", "парашют", "абсолют", "кредит",
    "лимит", "визит", "депозит", "аппетит", "транзит", "реквизит", "магнит", "гранит", "элит", "орбит", "плит",
    "кредите", "лимите", "визите", "депозите", "защите", "элите", "орбите", "плите", "граните", "магните",
    "транзите", "сайте",
    # -ат, -ят
    "результат", "формат", "адресат", "кандидат", "аппарат", "салат", "агрегат", "сертификат", "депутат", "квадрат",
    "штат", "плакат", "шпагат", "концентрат", "зарплат", "оплат", "доплат", "выплат", "предоплат", "затрат", "цитат",
    "брат", "карат", "гранат", "мандат", "адвокат", "автомат", "комбинат", "препарат", "экспонат", "аромат", "томат",
    "халат", "ребят", "котят",
    # -ал, -ел
    "материал", "канал", "персонал", "финал", "журнал", "портал", "капитал", "интервал", "сериал", "потенциал",
    "минерал", "идеал", "сигнал", "терминал", "оригинал", "арсенал", "карнавал", "вокзал", "подвал", "причал",
    "генерал", "штурвал", "ритуал", "мануал", "квартал", "филиал", "зал", "бокал", "перевал", "отдел", "раздел",
    "предел", "удел", "пробел", "прицел", "графит", "антрацит", "малахит",
    # -ла, -ло, -ли
    "школа", "сила", "правила", "зеркала", "начала", "дела", "тела", "села", "стрела", "пила", "игла", "скала",
    "метла", "смола", "мгла", "число", "стекло", "масло", "кресло", "крыло", "село", "дело", "тело", "весло",
    "сверло", "начало", "зеркало", "правило", "одеяло", "мыло", "сало", "шило", "русло", "тепло", "светло", "мало",
    "смело", "умело", "цели", "модели", "роли", "стили", "соли", "недели", "детали", "панели", "отели", "мысли",
    "мебели", "рубли", "угли", "капли", "туфли", "петли", "земли", "корабли", "вдали", "если", "причем", "почем",
    # имена с «глагольными» окончаниями (в начале части предложения; имена в середине пропускаются по заглавной)
    "павел", "михаил", "даниил", "гавриил", "самуил", "людмила", "мила", "алла", "стелла", "камилла", "марат", "ренат",
    "булат", "талгат", "рифат", "максим", "вадим", "ефим", "серафим", "герасим", "ахмет", "натали",
    # прежний список (формы на -ы, -и, -кт и др. — для совместимости)
    "эффект", "проект", "аспект", "продукт", "факт", "контракт", "дни", "сроки", "итоги", "услуги", "товары", "работы",
    "расходы", "материалы"}


def _expand_not_verb(base: set) -> set:
    """Добавляет формы, совпадающие с глагольными окончаниями: «канала», «филиала» (-ла), «бюджете», «кредите» (-те),
    «числа», «кресла» (-ла)."""
    out = set(base)
    for w in base:
        if w.endswith(("ал", "ел", "ил")):
            out.add(w + "а")
        if w.endswith(("ет", "ит")):
            out.add(w + "е")
        if w.endswith("ло"):
            out.add(w[:-1] + "а")
    return out


NOT_VERB_RU = _expand_not_verb(NOT_VERB_RU)
NOUN_ET_RU = NOT_VERB_RU   # имя v0.9.1 оставлено для совместимости
OBLIG_RIGHT_RE = re.compile(r"^\s*(?:это|вот|значит|всё|все|всего|никто|ничто|каждый)(?![А-Яа-яЁё])", re.I)
# тире перед союзом — интонационное («Доверьте ремонт нам — и наслаждайтесь результатом»)
CONJ_RIGHT_RE = re.compile(r"^\s*(?:и|а|но|или|да|зато|однако|причём|причем|притом|поэтому|потому|так\s+что|чтобы|"
                           r"если|когда|пока|хотя|ведь|то\s+есть)(?![А-Яа-яЁё])", re.I)
PREDICATE_POS = ("VERB", "ADJS", "PRTS")   # с морфологией сказуемым считаются и краткие прилагательные и причастия


def _is_finite_verb_ru(word: str, morph=None) -> bool:
    lw = word.lower()
    if "-" in lw:                          # «демо-бренд», «по-русски»: решает последняя часть
        return _is_finite_verb_ru(lw.rsplit("-", 1)[-1], morph)
    if morph is not None and not morph.word_is_known(lw):
        morph = None                       # незнакомое слово (бренд, жарг.): догадка pymorphy хуже окончаний
    if morph is not None:
        ps = morph.parse(lw)
        p0 = ps[0]
        if p0.tag.POS in PREDICATE_POS:
            # «свежей»: повелительное «свежеть» и прилагательное с равным весом — не сказуемое
            alt = max((p.score for p in ps[1:] if p.tag.POS not in PREDICATE_POS), default=0.0)
            return p0.score > alt
        return False
    if len(lw) < 4:
        return False
    le = lw.replace("ё", "е")
    if le in NOT_VERB_RU:
        return False
    if FINITE_YO_RU.search(lw):
        return True
    return bool(FINITE_VERB_RU.search(le))


def _has_finite_verb_ru(chunk: str, morph=None) -> bool:
    for k, w in enumerate(re.findall(r"[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*", chunk)):
        if k > 0 and w[:1].isupper():     # слово с заглавной в середине части — имя собственное («Яндекс Маркет»)
            continue
        if _is_finite_verb_ru(w, morph):
            return True
    return False


def dash_classes(t: str, dashes: list, lang: str, morph=None) -> list[str]:
    """Класс каждого тире: «O» — обязательное, «P» — пунктуационное.

    Обязательное — пропуск связки или сказуемого: «Смета и выезд замерщика — бесплатно», «Гарантия — 3 года»,
    «электрик — материалы», «Наша задача — вернуть…»; тире перед «это», «вот», «значит» и перед обобщающим «всё»,
    «никто», если слева нет сказуемого. Пунктуационное — пара тире в одной части предложения (вставка), тире перед
    союзом, пояснение или следствие после сказуемого («Отправляем в день обжарки — без месяцев на складе»), всё в
    английском тексте. Часть предложения — отрезок между , ; : . ! ? и переводом строки; без синтаксиса.
    Спорные случаи уходят в «обязательное»: лучше не оштрафовать живой текст (спецификация §5.1, опыт C/05)."""
    out = ["P"] * len(dashes)
    by_clause: dict = {}
    for i, m in enumerate(dashes):
        g = m.group(0)
        if "\n" in g[:max(g.find("—"), g.find("–"))]:   # тире в начале строки — прямая речь, диалог: обязательное
            out[i] = "O"
            continue
        # границы части предложения; скобки отсекают вставку: «Текст — HTML-шаблон (кириллица набрана…)»
        a = max(t.rfind(ch, 0, m.start()) for ch in ",;:.!?\n)")
        b_candidates = [j for j in (t.find(ch, m.end()) for ch in ",;:.!?\n(") if j >= 0]
        b = min(b_candidates) if b_candidates else len(t)
        by_clause.setdefault((a + 1, b), []).append(i)
    for (c0, c1), idxs in by_clause.items():
        if len(idxs) >= 2 or lang != "ru":   # пара тире в одной части — вставная конструкция
            continue
        i = idxs[0]
        m = dashes[i]
        left, right = t[c0:m.start()], t[m.end():c1]
        if CONJ_RIGHT_RE.search(right):
            continue
        left_verb = _has_finite_verb_ru(left, morph)
        if not left_verb and OBLIG_RIGHT_RE.search(right):
            out[i] = "O"
            continue
        lw, rw = words_of(left), words_of(right)
        if 0 < len(lw) <= 7 and 0 < len(rw) <= 9 and not left_verb and not _has_finite_verb_ru(right, morph):
            out[i] = "O"                     # «подлежащее — сказуемое», «поле — значение», неполное предложение
    return out


def classify_dashes(t: str, dashes: list, lang: str, morph=None) -> tuple[int, int]:
    """Возвращает (обязательных, пунктуационных) — см. dash_classes."""
    cls = dash_classes(t, dashes, lang, morph)
    return cls.count("O"), cls.count("P")


def text_metrics(text: str, lang: str = "auto", paragraphs: list[str] | None = None, morph=None) -> dict:
    """Метрики одного текста без правил (для замеров корпуса). paragraphs — если абзацы уже выделены."""
    if lang == "auto":
        lang = detect_lang(text)
    paras = paragraphs if paragraphs is not None else [text[s:e] for s, e in split_paragraphs(text)]
    words = words_of(text)
    nw = len(words) or 1
    lens = sentence_lengths(paras)
    t = norm_spaces(text)
    dashes = []
    for m in DASH_RE.finditer(t):
        before = t[:m.start()].rstrip()[-1:]
        after = t[m.end():].lstrip()[:1]
        if before.isdigit() and after.isdigit():  # диапазон «3 — 5» набран тире: это не пунктуационное тире
            continue
        dashes.append(m)
    dash_line_start = len(re.findall(r"(?m)^\s*[—–]\s", t))
    d_oblig, d_punct = classify_dashes(t, dashes, lang, morph)
    nxy = len((NOT_X_BUT_Y_RU if lang == "ru" else NOT_X_BUT_Y_EN).findall(t))
    triads = len((TRIAD_RU if lang == "ru" else TRIAD_EN).findall(t))
    sent_spans = [(p, s, e) for p in paras for (s, e) in split_sentences(p)]
    questions = sum(1 for p, s, e in sent_spans if p[s:e].rstrip().endswith("?"))
    excl = t.count("!")
    numbers = len(re.findall(B_MACRO + r"\d+(?:[.,]\d+)?", t))
    units_hits = len([m for m in UNITS_RE.finditer(t) if re.search(r"\d", m.group(0))])
    years = len(YEAR_RE.findall(t))
    months = len(MONTHS_RE.findall(t))
    propers = count_proper_names(t)
    acronyms = len(ACRONYM_RE.findall(t))
    claims = len(FACT_CLAIM_RE.findall(t))
    plens = [len(words_of(p)) for p in paras if len(words_of(p)) >= 5]
    pcv = None
    if len(plens) >= 2:
        pm = sum(plens) / len(plens)
        pcv = round(((sum((x - pm) ** 2 for x in plens) / len(plens)) ** 0.5) / pm, 3) if pm else None
    sents_text = [p[s:e] for p, s, e in sent_spans]
    conn = count_connective_sentences(sents_text, lang) if sents_text else 0
    frag = sum(1 for s in sents_text if len(words_of(s)) <= 3)
    inf_list = INFORMAL_RU if lang == "ru" else INFORMAL_EN
    inf_re = re.compile(B_MACRO + r"(?:" + "|".join(re.escape(x) for x in inf_list) + r")" + E_MACRO, re.I)
    informal = len(inf_re.findall(t))
    per100 = lambda x: round(100.0 * x / nw, 3)
    m = {"lang": lang, "words": len(words), "chars": len(text), "paragraphs": len(paras),
         "dash_count": len(dashes), "dash_per_100w": per100(len(dashes)), "dash_line_start": dash_line_start,
         "dash_obligatory": d_oblig, "dash_punct": d_punct, "dash_punct_per_100w": per100(d_punct),
         "hyphen_as_dash": len(HYPHEN_AS_DASH_RE.findall(t)) if lang == "ru" else 0,
         "not_x_but_y": nxy, "not_x_but_y_per_100w": per100(nxy),
         "triads": triads, "triads_per_100w": per100(triads),
         "questions": questions, "questions_per_100w": per100(questions),
         "exclamations": excl, "exclamations_per_100w": per100(excl),
         "numbers": numbers, "numbers_per_100w": per100(numbers),
         "concrete_units": units_hits, "years": years, "months": months, "proper_names": propers,
         "acronyms": acronyms,
         "concreteness_per_100w": per100(numbers + months + propers),
         "claims_needing_fact": claims,
         "middots": t.count("·"), "arrows": len(re.findall(r"[→←↗↘⇒➔➜]", t)),
         "emoji": len(re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", t)),
         "bold_md": len(re.findall(r"\*\*[^*\n]+\*\*", text)),
         "paragraph_len_cv": pcv,
         "connective_share": round(conn / len(sents_text), 3) if sents_text else None,
         "fragment_share_le3": round(frag / len(sents_text), 3) if sents_text else None,
         "informal_per_100w": per100(informal)}
    m["rhythm"] = stats_rhythm(lens)
    return m


def analyzer_rule(rules_by_id: dict, rid: str) -> Rule | None:
    return rules_by_id.get(rid)


def mk_analyzer_finding(r: Rule | None, rid: str, level: str, message: str, doc_unit: int = -1, fragment: str = "",
                        slot: dict | None = None, extra: str = "") -> Finding:
    if r is None:
        return Finding(rid, "", level, "STR", message + (f" {extra}" if extra else ""), fragment=fragment,
                       unit=doc_unit, slot=slot or {})
    return Finding(r.id, r.marker_id, level, r.group, (r.message + (f" {extra}" if extra else "")), fragment=fragment,
                   unit=doc_unit, replacement=r.replacement, example=r.examples or {}, source=r.source,
                   evidence=r.evidence, slot=slot or {}, count_as_marker=bool(r.count_as_marker), note=r.note)


def an_level(cfg: dict, default: str = "warning") -> str:
    lv = (cfg or {}).get("level", default)
    return lv if lv in LEVELS else default


# --- межстрочные проверки интерфейса (ux 07/06 §7.3) и общие для жанров ---------------------------------------------
LETTERS_RE = re.compile(r"[А-Яа-яЁёA-Za-z]+")
VERB_SUFFIXES = ("ировать", "овывать", "ывать", "ивать", "евать", "овать", "ать", "ять", "еть", "ить", "уть", "ыть",
                 "оть", "ти", "ть", "чь")
NOUN_ENDINGS = "(?:а|я|у|ю|о|е|и|ы|ь|й|ом|ем|ой|ей|ов|ев|ам|ям|ах|ях|ами|ями)?"
# роли строк с содержанием: одинаковый текст двух таких строк на экране — дубль (F8.1, F8.2); кнопки, ссылки, подписи
# полей и колонок законно повторяются
CONTENT_ROLES = {"title", "subtitle", "section-title", "body", "help", "empty", "banner", "inline-message", "hint",
                 "caption", "tooltip", "setting-description", "confirm-body", "toast", "error"}
YO_AMBIGUOUS = {"все", "узнаем", "совершенный", "совершенная", "совершенное", "совершенные", "осел", "небо"}
US_UK = [("color", "colour"), ("behavior", "behaviour"), ("favorite", "favourite"), ("center", "centre"),
         ("organiz", "organis"), ("customiz", "customis"), ("optimiz", "optimis"), ("authoriz", "authoris"),
         ("analyz", "analys"), ("canceled", "cancelled"), ("canceling", "cancelling"), ("catalog", "catalogue"),
         ("gray", "grey"), ("license", "licence"), ("dialog", "dialogue"), ("fulfill", "fulfil")]


def yo(s: str) -> str:
    return s.lower().replace("ё", "е")


def match_brace(text: str, i: int) -> int:
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    return -1


ICU_KEY_RE = re.compile(r"\s*(?:offset:\s*\d+\s*)?(=\d+|zero|one|two|few|many|other)\s*\{")


def icu_branches(rest: str) -> dict | None:
    out, i = {}, 0
    while i < len(rest):
        if not rest[i:].strip():
            break
        m = ICU_KEY_RE.match(rest, i)
        if not m:
            return None
        j = match_brace(rest, m.end() - 1)
        if j < 0:
            return None
        out[m.group(1)] = rest[m.end():j]
        i = j + 1
    return out


def icu_scan(text: str, lang: str = "ru") -> tuple[str, list, list]:
    """Строка ICU (ux 07/05 §4.4) → (текст без подстановок: у plural и select — самая длинная ветка, «#» снят;
    проблемы [(уровень, что)]; границы аргументов верхнего уровня)."""
    plain, issues, spans, i = [], [], [], 0
    while i < len(text):
        ch = text[i]
        if ch == "{":
            j = match_brace(text, i)
            if j < 0:
                issues.append(("error", "скобка «{» не закрыта"))
                plain.append(text[i:])
                break
            spans.append((i, j + 1))
            parts = [x.strip() for x in text[i + 1:j].split(",", 2)]
            name, typ = parts[0], (parts[1] if len(parts) > 1 else "")
            if typ in ("plural", "select", "selectordinal"):
                br = icu_branches(parts[2] if len(parts) > 2 else "")
                if br is None:
                    issues.append(("error", f"{{{name}, {typ}}}: ветки не разбираются"))
                    br = {}
                elif "other" not in br:
                    issues.append(("error", f"{{{name}, {typ}}}: нет ветки other"))
                if typ == "plural":
                    if "=1" in br and "one" not in br:
                        issues.append(("warning", f"{{{name}, plural}}: «=1» вместо one — one в русском значит 1, 21, 31…"))
                    miss = [k for k in ("one", "few", "many") if k not in br] if lang == "ru" else []
                    if miss and br:
                        issues.append(("warning", f"{{{name}, plural}}: у русского нет веток {', '.join(miss)}"))
                subs = [icu_scan(m, lang) for m in br.values()]
                for s in subs:
                    issues.extend(s[1])
                plain.append(max((s[0] for s in subs), key=len, default="").replace("#", ""))
            elif not re.fullmatch(r"[A-Za-z_][\w.]*", name or ""):
                issues.append(("error", f"«{{{text[i + 1:j]}}}» — не аргумент ICU"))
            i = j + 1
        elif ch == "}":
            issues.append(("error", "лишняя «}»"))
            i += 1
        else:
            plain.append(ch)
            i += 1
    return "".join(plain), issues, spans


def icu_spans(text: str) -> list[tuple[int, int]]:
    return icu_scan(text)[2] if "{" in text else []


def root_of(word: str) -> str:
    """Основа глагола без окончания инфинитива и частицы -ся: «создать» → «созд», «записаться» → «запис»."""
    w = yo(word)
    if w.endswith(("ся", "сь")) and len(w) > 6:
        w = w[:-2]
    for suf in VERB_SUFFIXES:
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w[:max(4, len(w) - 2)]


def action_roots(verb: str, past: str) -> set:
    """Корни имени действия: основа глагола кнопки (verb) и общее начало verb и past («отметить» — «отмечен»)."""
    vw = LETTERS_RE.findall(verb or "")
    if not vw:
        return set()
    v0 = yo(vw[0])
    roots = {root_of(v0)}
    best = ""
    for pw in LETTERS_RE.findall(past or ""):
        cp = ""
        for a, b in zip(v0, yo(pw)):
            if a != b:
                break
            cp += a
        best = cp if len(cp) > len(best) else best
    if len(best) >= 4:
        roots.add(best)
    return {r for r in roots if len(r) >= 3}


def word_with_root(text: str, roots, longer: bool = False) -> str:
    """Слово текста с одним из корней; longer — слово длиннее корня («перед» ≠ «передать»)."""
    for w in LETTERS_RE.findall(text):
        lw = yo(w)
        for r in roots:
            if lw.startswith(r) and (len(lw) > len(r) if longer else True):
                return w
    return ""


def alias_re(alias: str):
    """Синоним объекта с падежными окончаниями: «лид» — «лида», «лидов», но не «лидер»."""
    parts = []
    for w in LETTERS_RE.findall(alias):
        lw = yo(w)
        stem = lw[:-1] if len(lw) >= 5 and lw[-1] in "аяоеиыьйую" else lw
        parts.append(re.escape(stem) + NOUN_ENDINGS)
    if not parts:
        return None
    return re.compile(r"(?<![а-яa-z])" + r"\s+".join(parts) + r"(?![а-яa-z])")


def phrase_form(text: str, morph) -> str:
    """Какой вопрос строка группы закрывает: «действие» (инфинитив, повелительное), «признак» (краткое причастие или
    прилагательное, строка из одних прилагательных — «какая?»), «предмет» (именная группа — «что?»)."""
    ws = [w for w in LETTERS_RE.findall(icu_scan(text)[0]) if CYR_RE.search(w)]
    if not ws or morph is None:
        return ""
    ps = [morph.parse(w)[0] for w in ws]
    p0 = ps[0]
    if p0.tag.POS == "INFN" or (p0.tag.POS == "VERB" and "impr" in p0.tag):
        return "действие"
    if any(p.tag.POS in ("PRTS", "ADJS") for p in ps):
        return "признак"
    content = [p for p in ps if p.tag.POS in ("NOUN", "ADJF", "PRTF")]
    if content and all(p.tag.POS in ("ADJF", "PRTF") for p in content):
        return "признак"
    return "предмет" if p0.tag.POS in ("NOUN", "ADJF", "PRTF", "NPRO", "NUMR") else ""


TY_RE = re.compile(r"(?<![А-Яа-яЁё])(?:ты|тебя|тебе|тобой|тобою|тво[йяеёи]|твоего|твоей|твоему|твоим|твоих|твою|"
                   r"твоими)(?![А-Яа-яЁё])", re.I)
VY_RE = re.compile(r"(?<![А-Яа-яЁё])(?:вы|вас|вам|вами|ваш|ваша|ваше|ваши|вашего|вашей|вашему|вашим|ваших|вашу|"
                   r"вашими)(?![А-Яа-яЁё])", re.I)
TY_VERB_RE = re.compile(r"(?<![А-Яа-яЁё])[А-Яа-яЁё]{2,}(?:ешь|ишь|ёшь|ешься|ишься|ёшься)(?![А-Яа-яЁё])", re.I)
VY_VERB_RE = re.compile(r"(?<![А-Яа-яЁё])[А-Яа-яЁё]{2,}(?:ете|ите|ёте|етесь|итесь|ётесь|йте|ьте|йтесь|ьтесь)"
                        r"(?![А-Яа-яЁё])", re.I)


def address_hits(text: str, morph) -> tuple[list, list]:
    """Приметы обращения на «ты» и на «вы»: местоимения, личные формы и повелительное наклонение."""
    t = norm_spaces(text)
    ty = [m.group(0) for m in TY_RE.finditer(t)] + [m.group(0) for m in TY_VERB_RE.finditer(t)
                                                   if yo(m.group(0)) not in NOT_VERB_RU]
    vy = [m.group(0) for m in VY_RE.finditer(t)] + [m.group(0) for m in VY_VERB_RE.finditer(t)
                                                   if yo(m.group(0)) not in NOT_VERB_RU]
    if morph is not None:
        for w in re.findall(r"[А-Яа-яЁё]{3,}", t):
            p = morph.parse(w.lower())[0]
            if p.tag.POS == "VERB" and "impr" in p.tag and p.score >= 0.5:
                (ty if "sing" in p.tag else vy).append(w)
    return ty, vy


def address_mix(doc: Document, rb: dict, cfg: dict, morph, form: str = "") -> list:
    """«Ты» и «вы» в одном тексте: находка — на строках меньшинства (или не той формы, что у голоса продукта)."""
    per = []
    for ui, u in enumerate(doc.units):
        if u.role == "user-content" or (u.lang and u.lang != "ru"):
            continue
        ty, vy = address_hits(u.text, morph)
        if ty or vy:
            per.append((ui, u, ty, vy))
    n_ty = sum(1 for x in per if x[2])
    n_vy = sum(1 for x in per if x[3])
    want = {"ty": "ty", "vy": "vy"}.get(form, "")
    if not want:
        if not (n_ty and n_vy):
            return []
        want = "vy" if n_vy >= n_ty else "ty"
    out = []
    for ui, u, ty, vy in per:
        bad = ty if want == "vy" else vy
        if bad:
            f = mk_analyzer_finding(rb.get("an-address-mix"), "an-address-mix", an_level(cfg), "«Ты» и «вы» в одном тексте.",
                                    doc_unit=ui, fragment=bad[0], slot=slot_info(u),
                                    extra=f"Форма текста — «{'вы' if want == 'vy' else 'ты'}»: здесь «{bad[0]}».")
            out.append(f)
    return out


def role_lengths() -> dict:
    return ((load_yaml(UX_DICT_PATH) or {}).get("role_lengths") or {}) if UX_DICT_PATH.exists() else {}


def syllables(word: str) -> int:
    if CYR_RE.search(word):
        return len(re.findall(r"[аеёиоуыэюяАЕЁИОУЫЭЮЯ]", word))
    return max(1, len(re.findall(r"[aeiouy]+", word.lower())))


def _ui_finding(rb, rid, level, message, ui, u, doc, fragment="", extra="", start=-1, end=-1) -> Finding:
    f = mk_analyzer_finding(rb.get(rid), rid, level, message, doc_unit=ui, fragment=fragment, slot=slot_info(u),
                            extra=extra)
    f.start, f.end = start, end
    if u.src_offset is not None and doc.source_text:
        f.line, f.col = line_col(doc.source_text, u.src_offset + max(0, start))
    return f


def run_ui_analyzers(doc: Document, rules: list[Rule], profile: dict, morph, lang: str) -> tuple[list, dict]:
    """Межстрочные проверки ux 07/06 §7.3 для строк интерфейса: имя действия по потоку и синонимы действия (action.md),
    синонимы объекта (object.md, aliases), формы групп, дубли на экране, maxlen, длина по роли (ux 07/01 §12),
    форматы чисел и диапазонов, ICU, «ё» и «е», US и UK, уровень чтения. Заголовок против содержимого и стили пары
    «согласие / отказ» — судья и проверка макета."""
    an = profile.get("analyzers") or {}
    rb = {r.id: r for r in rules}
    out: list = []
    metrics: dict = {}
    reg = doc.registry or {}
    units = [(ui, u) for ui, u in enumerate(doc.units) if u.role != "user-content" and not ltype(u)]
    notes = []

    # имя действия по потоку и запрещённые синонимы действия
    cfg = an.get("ui_action_name") or {}
    acts = reg.get("actions") or {}
    if cfg.get("enabled") and acts:
        roots = {slug: action_roots(a["verb"], a["past"]) for slug, a in acts.items()}
        banned = {slug: [(b, {root_of(LETTERS_RE.findall(b)[0])}) for b in a["banned"] if LETTERS_RE.findall(b)]
                  for slug, a in acts.items()}
        for ui, u in units:
            plain = icu_scan(u.text, lang)[0]
            if u.action and u.action in acts:
                hit = next(((b, w) for b, rs in banned[u.action] for w in [word_with_root(plain, rs, True)] if w), None)
                if hit:
                    out.append(_ui_finding(rb, "an-ui-action-synonym", cfg.get("level_banned", "error"),
                                           "Запрещённый синоним действия.", ui, u, doc, hit[1],
                                           f"Действие `{u.action}` — «{acts[u.action]['verb']}» / «{acts[u.action]['past']}»; "
                                           f"«{hit[1]}» — в списке запрещённых («{hit[0]}»)."))
                elif roots[u.action] and not word_with_root(plain, roots[u.action]):
                    out.append(_ui_finding(rb, "an-ui-action-name", an_level(cfg), "Имя действия по потоку.", ui, u, doc,
                                           "", f"Строка действия `{u.action}` не называет его глаголом словаря: "
                                               f"«{acts[u.action]['verb']}» / «{acts[u.action]['past']}» — у потока "
                                               f"второе имя («{plain[:60]}»)."))
            elif u.object:
                for slug, a in acts.items():
                    if u.object not in a["objects"]:
                        continue
                    hit = next(((b, w) for b, rs in banned[slug] for w in [word_with_root(plain, rs, True)] if w), None)
                    if hit:
                        out.append(_ui_finding(rb, "an-ui-action-synonym", cfg.get("level_banned", "error"),
                                               "Запрещённый синоним действия.", ui, u, doc, hit[1],
                                               f"Объект `{u.object}`: действие `{slug}` — «{a['verb']}»; «{hit[1]}» — "
                                               f"в списке запрещённых («{hit[0]}»)."))
                        break
    elif cfg.get("enabled"):
        notes.append("имя действия по потоку: словаря действий action.md нет — проверка пропущена")

    # синонимы объекта
    cfg = an.get("ui_object_alias") or {}
    objs = reg.get("objects") or {}
    if cfg.get("enabled") and objs:
        pats = []
        for slug, o in objs.items():
            for al in o["aliases"]:
                if yo(al) != yo(o["name"]):
                    rx = alias_re(al)
                    if rx is not None:
                        pats.append((slug, o["name"], al, rx))
        for ui, u in units:
            low = yo(u.text)
            for slug, name, al, rx in pats:
                m = rx.search(low)
                if m:
                    out.append(_ui_finding(rb, "an-ui-object-alias", an_level(cfg, "error"), "Синоним объекта.", ui, u,
                                           doc, u.text[m.start():m.end()],
                                           f"«{u.text[m.start():m.end()]}» — синоним объекта `{slug}` («{name}», "
                                           f"aliases: {al}).", m.start(), m.end()))
    elif cfg.get("enabled"):
        notes.append("синонимы объекта: глоссария object.md нет — проверка пропущена")

    # формы строк одной группы (меню, статусы объекта)
    cfg = an.get("ui_group_form") or {}
    if cfg.get("enabled"):
        groups: dict = {}
        for ui, u in units:
            if u.group:
                groups.setdefault(u.group, []).append((ui, u))
        if groups and morph is None:
            notes.append("формы групп строк — с морфологией pymorphy3: без неё проверка пропущена")
        for g, items in groups.items() if morph is not None else []:
            forms = [(ui, u, phrase_form(u.text, morph)) for ui, u in items]
            kinds = [k for _, _, k in forms if k]
            if len(set(kinds)) < 2:
                continue
            major = max(set(kinds), key=kinds.count)
            for ui, u, k in forms:
                if k and k != major:
                    out.append(_ui_finding(rb, "an-ui-group-form", an_level(cfg), "Строки группы в разных формах.", ui,
                                           u, doc, u.text[:40], f"Группа «{g}»: у большинства строк — {major}, здесь — {k}."))

    # дубли на экране
    cfg = an.get("ui_duplicate") or {}
    if cfg.get("enabled"):
        seen: dict = {}
        for ui, u in units:
            if not u.key or u.role not in CONTENT_ROLES:
                continue
            screen = ".".join(u.key.split(".")[:2])
            k = (screen, re.sub(r"\s+", " ", yo(u.text)).strip())
            if k in seen:
                out.append(_ui_finding(rb, "an-ui-duplicate", an_level(cfg), "Один текст дважды на экране.", ui, u, doc,
                                       u.text[:40], f"Экран `{screen}`: «{u.text[:50]}» — и в `{seen[k]}`."))
            else:
                seen[k] = u.key

    # maxlen строки (ворота) и длина по роли ux 07/01 §12 (сигнал)
    cfg_m, cfg_r = an.get("ui_maxlen") or {}, an.get("ui_role_length") or {}
    rl = role_lengths()
    sent = rl.get("sentence") or {}
    for ui, u in units:
        plain = icu_scan(u.text, lang)[0].strip()
        if cfg_m.get("enabled") and re.fullmatch(r"\d+", (u.maxlen or "").strip()):
            mx = int(u.maxlen)
            if len(plain) > mx:
                out.append(_ui_finding(rb, "an-ui-maxlen", an_level(cfg_m, "error"), "Строка длиннее maxlen.", ui, u, doc,
                                       plain[:40], f"{len(plain)} знаков > maxlen {mx} (без подстановок ICU)."))
        if not cfg_r.get("enabled") or not rl:
            continue
        paras = [p for p in re.split(r"\n\s*\n|\n", plain) if p.strip()] or [plain]
        n_words = max((len(words_of(p)) for p in paras), default=0)
        n_sent = len(split_sentences(plain))
        alts = (rl.get("roles") or {}).get(u.role) or []
        problems = []
        for alt in alts:
            bad = []
            if alt.get("words_max") and n_words > alt["words_max"]:
                bad.append(f"{n_words} слов > {alt['words_max']}")
            if alt.get("sentences_max") and n_sent > alt["sentences_max"]:
                bad.append(f"{n_sent} предложений > {alt['sentences_max']}")
            if alt.get("chars_max") and len(plain) > alt["chars_max"]:
                bad.append(f"{len(plain)} знаков > {alt['chars_max']}")
            if not bad:
                problems = []
                break
            problems.append(f"{alt.get('element')}: " + ", ".join(bad))
        if alts and problems:
            out.append(_ui_finding(rb, "an-ui-role-length", an_level(cfg_r), "Строка длиннее ориентира роли.", ui, u,
                                   doc, plain[:40], f"Роль `{u.role}` — {'; '.join(problems)} (ux 07/01 §12)."))
        if sent:
            lim = sent.get("explanatory_words_max") if u.role in (sent.get("explanatory_roles") or []) else \
                sent.get("words_max")
            longest = max((len(words_of(plain[s:e])) for s, e in split_sentences(plain)), default=0)
            if lim and longest > lim:
                out.append(_ui_finding(rb, "an-ui-role-length", an_level(cfg_r), "Предложение длиннее ориентира.", ui, u,
                                       doc, plain[:40], f"{longest} слов в предложении > {lim} (ux 07/01 §12)."))

    # форматы: число литералом, знак диапазона, пробел разрядов
    cfg = an.get("ui_formats") or {}
    if cfg.get("enabled"):
        signs: dict = {}
        seps: dict = {}
        for ui, u in units:
            spans = icu_spans(u.text)
            outside = "".join(ch if not any(s <= k < e for s, e in spans) else " " for k, ch in enumerate(u.text))
            m = re.search(r"\d", outside)
            if m:
                out.append(_ui_finding(rb, "an-ui-formats", an_level(cfg), "Число литералом.", ui, u, doc,
                                       outside[max(0, m.start() - 8):m.start() + 8].strip(),
                                       "Число, дата, сумма — из данных продукта: подстановка ICU и формат Intl "
                                       "(ux 07/05 §4.4, §5).", m.start(), m.end()))
            for rm in re.finditer(r"(?:(?<=\d)|(?<=\}))(\s*)([-‐‑–—])(\s*)(?=\d|\{)", u.text):
                sign, spaced = rm.group(2), bool(rm.group(1) or rm.group(3))
                if sign in "-‐‑" or spaced:
                    out.append(_ui_finding(rb, "an-ui-formats", an_level(cfg), "Знак диапазона.", ui, u, doc,
                                           u.text[max(0, rm.start() - 6):rm.end() + 6],
                                           "Диапазон — тире без пробелов: «–» (U+2013) или знак дизайн-системы "
                                           "продукта (text 08/02 §1.3).", rm.start(), rm.end()))
                else:
                    signs.setdefault(sign, []).append((ui, u, rm))
            for nm in re.finditer(r"\d{1,3}(?:([    ])\d{3})+(?!\d)", u.text):
                seps.setdefault(nm.group(1), []).append((ui, u, nm))
        if len(signs) > 1:
            major = max(signs, key=lambda s: len(signs[s]))
            for s, items in signs.items():
                if s == major:
                    continue
                for ui, u, rm in items:
                    out.append(_ui_finding(rb, "an-ui-formats", an_level(cfg), "Смешение знака диапазона.", ui, u, doc,
                                           u.text[max(0, rm.start() - 6):rm.end() + 6],
                                           f"В продукте знак диапазона «{major}» ({len(signs[major])} строк), здесь "
                                           f"«{s}»: знак один на продукт.", rm.start(), rm.end()))
        for sp, items in seps.items():
            if sp == " " or len(seps) > 1 and sp != max(seps, key=lambda x: len(seps[x])):
                for ui, u, nm in items:
                    out.append(_ui_finding(rb, "an-ui-formats", an_level(cfg), "Пробел в разрядах.", ui, u, doc,
                                           nm.group(0), "Пробел разряда — неразрывный U+00A0 (U+202F — решение ДС), "
                                                        "один на продукт.", nm.start(), nm.end()))

    # ICU
    cfg = an.get("ui_icu") or {}
    if cfg.get("enabled"):
        for ui, u in units:
            if "{" not in u.text and "}" not in u.text:
                continue
            for lvl, what in icu_scan(u.text, u.lang or lang)[1]:
                level = an_level(cfg, "error") if lvl == "error" else "warning"
                out.append(_ui_finding(rb, "an-ui-icu", level, "Строка ICU не по форме.", ui, u, doc, u.text[:40],
                                       what + " (ux 07/05 §4.4)."))

    # «ё» и «е» в одном слове
    cfg = an.get("yo_mix") or {}
    if cfg.get("enabled"):
        with_yo = {}
        for ui, u in units:
            for w in LETTERS_RE.findall(u.text):
                if "ё" in w.lower():
                    with_yo.setdefault(yo(w), w)
        for ui, u in units:
            for w in LETTERS_RE.findall(u.text):
                lw = w.lower()
                if "ё" not in lw and lw in with_yo and lw not in YO_AMBIGUOUS:
                    out.append(_ui_finding(rb, "an-ui-yo-mix", an_level(cfg), "«Ё» и «е» в одном слове.", ui, u, doc, w,
                                           f"«{w}» — в других строках «{with_yo[lw]}»."))
                    break

    # US и UK
    cfg = an.get("us_uk") or {}
    if cfg.get("enabled"):
        found = {"us": [], "uk": []}
        for ui, u in units:
            low = u.text.lower()
            for us, uk in US_UK:
                if re.search(r"\b" + uk, low):
                    found["uk"].append((ui, u, uk))
                elif re.search(r"\b" + us, low):
                    found["us"].append((ui, u, us))
        if found["us"] and found["uk"]:
            minor = "uk" if len(found["us"]) >= len(found["uk"]) else "us"
            for ui, u, w in found[minor]:
                out.append(_ui_finding(rb, "an-ui-us-uk", an_level(cfg), "US и UK орфография вместе.", ui, u, doc, w,
                                       f"Орфография продукта — {'US' if minor == 'uk' else 'UK'}: здесь «{w}…»."))

    # уровень чтения развёрнутых текстов: роли прозы (body, help, email)
    cfg = an.get("reading_level") or {}
    if cfg.get("enabled"):
        prose_roles = set(profile.get("prose_roles") or [])
        rows = []
        for ui, u in units:
            if u.role not in prose_roles:
                continue
            plain = icu_scan(u.text, lang)[0]
            ws = words_of(plain)
            if len(ws) < int(cfg.get("min_words", 30)):
                continue
            sents = max(1, len(split_sentences(plain)))
            w_syl = sum(syllables(w) for w in ws) / len(ws)
            k_obo = round(206.835 - 60.1 * w_syl - 1.3 * (len(ws) / sents), 1)
            rows.append({"key": u.key or u.slot_id, "words": len(ws), "syllables_per_word": round(w_syl, 2),
                         "words_per_sentence": round(len(ws) / sents, 1), "oborneva": k_obo})
            if w_syl > float(cfg.get("syllables_max", 2.5)):
                out.append(_ui_finding(rb, "an-reading-level", an_level(cfg, "info"), "Длинные слова.", ui, u, doc,
                                       plain[:40], f"{w_syl:.2f} слога на слово > {cfg.get('syllables_max', 2.5)}; "
                                                   f"индекс Оборневой {k_obo} — сигнал, не ворота."))
        if rows:
            metrics["reading"] = rows
    if notes:
        metrics["ui_notes"] = notes
    return out, metrics


def run_analyzers(doc: Document, rules: list[Rule], genre: str, lang: str, profile: dict, morph,
                  marker_findings: list[Finding]) -> tuple[list[Finding], dict]:
    an = profile.get("analyzers") or {}
    rb = {r.id: r for r in rules}
    out: list[Finding] = []
    prose_types = set(profile.get("prose_slot_types") or ["body", "article-paragraph", "geo-answer", "email-body"])
    prose_roles = set(profile.get("prose_roles") or [])
    # подписи в 1–3 слова не проза, даже если слот размечен как body (опыт C/02: вкладки и статусы веб-приложения);
    # у строки без типа слота (жанр interface) проза — по роли (body, help, email)
    prose_units = [(i, u) for i, u in enumerate(doc.units) if (ltype(u) in prose_types if ltype(u) else
                                                              u.role in prose_roles)
                   and (u.genre or genre) == genre and len(words_of(u.text)) >= 4]
    all_text = "\n\n".join(u.text for u in doc.units)
    prose_paras: list[str] = []
    for _, u in prose_units:
        prose_paras.extend(u.text[s:e] for s, e in split_paragraphs(u.text))
    prose_text = "\n\n".join(prose_paras)
    m_all = text_metrics(all_text, lang, None, morph)
    m_prose = text_metrics(prose_text, lang, prose_paras, morph) if prose_paras else None
    metrics = {"all": m_all, "prose": m_prose, "prose_slot_types": sorted(prose_types)}
    nw_all = max(1, m_all["words"])

    # плотность маркеров
    counted = [f for f in marker_findings if f.count_as_marker and f.level != "off"]
    n_clusters = merged_marker_spans(counted)
    dens = round(100.0 * n_clusters / nw_all, 3)
    fam = sorted({f.group for f in counted})
    metrics["markers"] = {"count": n_clusters, "hits": len(counted), "per_100w": dens,
                          "distinct_rules": len({f.id for f in counted}),
                          "families": fam,
                          "by_group": {g: sum(1 for f in counted if f.group == g) for g in fam}}
    cfg = an.get("marker_density") or {}
    if cfg.get("enabled", True) and m_all["words"] >= int(cfg.get("min_words", 40)) \
            and n_clusters >= int(cfg.get("min_count", 2)):
        warn, err = cfg.get("warn_per_100w"), cfg.get("error_per_100w")
        lvl = None
        if err is not None and dens >= float(err):
            lvl = "error" if cfg.get("allow_error", True) else "warning"
        elif warn is not None and dens >= float(warn):
            lvl = an_level(cfg)
        if lvl:
            out.append(mk_analyzer_finding(rb.get("an-marker-density"), "an-marker-density", lvl,
                                           "Плотность маркеров слопа выше порога жанра.",
                                           extra=f"{dens} на 100 слов (порог {warn}/{err}{', provisional' if cfg.get('provisional', True) else ''}); "
                                                 f"семей: {', '.join(fam)}."))

    # ритм и абзацы — только проза
    if m_prose and m_prose["words"] >= 30:
        rh = m_prose["rhythm"]
        cfg = an.get("rhythm") or {}
        if cfg.get("enabled", True) and rh.get("sentences", 0) >= int(cfg.get("min_sentences", 8)):
            md = rh.get("mean_abs_diff")
            # ровные короткие фразы (серия вопросов, живая колонка) — другой стиль; машинная монотонность — это ровные
            # средние и длинные предложения (опыт C/04: колонка bureau.ru 2012 со средним 7 слов давала ложное)
            if md is not None and md < float(cfg.get("mean_diff_min", 4)) \
                    and rh.get("mean_len", 0) >= float(cfg.get("min_mean_len", 9)):
                out.append(mk_analyzer_finding(rb.get("an-rhythm-monotone"), "an-rhythm-monotone", an_level(cfg),
                                               "Монотонный ритм прозы.",
                                               extra=f"Средняя разница длин соседних предложений {md} слова (порог {cfg.get('mean_diff_min', 4)}, цель ≥ {cfg.get('target', 6)})."))
            if rh.get("sentences", 0) >= int(cfg.get("min_sentences_short", 10)) and rh.get("share_short_le8", 1) == 0:
                out.append(mk_analyzer_finding(rb.get("an-rhythm-no-short"), "an-rhythm-no-short", an_level(cfg),
                                               "В прозе нет ни одного короткого предложения (до 8 слов)."))
        cfg = an.get("paragraph_uniformity") or {}
        plens = [len(words_of(p)) for p in prose_paras if len(words_of(p)) >= 5]
        if cfg.get("enabled", True) and len(plens) >= int(cfg.get("min_paragraphs", 5)):
            pm = sum(plens) / len(plens)
            cv = ((sum((x - pm) ** 2 for x in plens) / len(plens)) ** 0.5) / pm if pm else 1
            if cv < float(cfg.get("cv_min", 0.25)):
                out.append(mk_analyzer_finding(rb.get("an-paragraphs-uniform"), "an-paragraphs-uniform",
                                               an_level(cfg, "info"), "Абзацы прозы одинаковой длины.",
                                               extra=f"Разброс {cv:.0%} от средней (порог {float(cfg.get('cv_min', 0.25)):.0%})."))
        # тире в прозе
        cfg = an.get("dash_density") or {}
        # считаются только пунктуационные тире; обязательные («Смета — бесплатно», «Гарантия — 3 года») не штрафуются
        if cfg.get("enabled", True) and m_prose["dash_punct"] >= int(cfg.get("min_count", 3)):
            thr = float(cfg.get("warn_per_100w", 1.5))
            if m_prose["dash_punct_per_100w"] >= thr:
                out.append(mk_analyzer_finding(rb.get("an-dash-density"), "an-dash-density", an_level(cfg),
                                               "Плотность пунктуационных тире в прозе выше порога жанра.",
                                               extra=f"{m_prose['dash_punct']} пунктуационных из {m_prose['dash_count']} тире, "
                                                     f"{m_prose['dash_punct_per_100w']} на 100 слов (порог {thr}, provisional); "
                                                     f"обязательных {m_prose['dash_obligatory']} — не считаются."))
        # конкретика
        cfg = an.get("concreteness") or {}
        if cfg.get("enabled", True) and m_prose["words"] >= int(cfg.get("min_words", 60)):
            mn = float(cfg.get("min_per_100w", 1.5))
            if m_prose["concreteness_per_100w"] < mn:
                out.append(mk_analyzer_finding(rb.get("an-low-concreteness"), "an-low-concreteness",
                                               an_level(cfg, "info"), "Мало конкретики в прозе.",
                                               extra=f"{m_prose['concreteness_per_100w']} конкретных единиц на 100 слов (порог {mn}, provisional)."))
        # повтор глагола в соседних предложениях
        cfg = an.get("verb_repeat") or {}
        cwords = [yo(c) for c in profile.get("customer_words") or [] if str(c).strip()]
        if cfg.get("enabled", True) and lang == "ru":
            for ui, u in prose_units:
                sents = [u.text[s:e] for s, e in split_sentences(u.text)]
                for a, b in zip(sents, sents[1:]):
                    if len(words_of(b)) <= 4:  # эхо-повтор для ритма («Платил молча.») — приём, не слоп (humanizer-ru п.33)
                        continue
                    if lang == "ru":
                        common = (verb_lemmas_ru(a, morph) & verb_lemmas_ru(b, morph)) if morph else \
                            (listed_verb_stems_ru(a) & listed_verb_stems_ru(b))
                        common = {c for c in common if c not in ("быть", "есть", "мочь", "стать")}
                    else:
                        wa = {w.lower() for w in re.findall(r"\b[a-z]{4,}(?:s|ed|es)\b", a, re.I)}
                        wb = {w.lower() for w in re.findall(r"\b[a-z]{4,}(?:s|ed|es)\b", b, re.I)}
                        common = {w for w in wa & wb if w not in ("this", "these", "those", "does", "goes", "uses")}
                    if common and cwords:
                        # повтор слова клиента — приём, а не тик: глагол из фразы клиента (voc, customer_words)
                        pair = yo(a + " " + b)
                        common = {c for c in common if not any(p in pair and yo(c)[:4] in p for p in cwords)}
                    if common:
                        out.append(mk_analyzer_finding(rb.get("an-verb-repeat"), "an-verb-repeat",
                                                       an_level(cfg, "info"), "Повтор глагола в соседних предложениях.",
                                                       doc_unit=ui, fragment=sorted(common)[0], slot=slot_info(u),
                                                       extra=f"«{sorted(common)[0]}…»: {norm_spaces(b)[:60]}"))
    # сверхкоррекция: своё условие — короткие рваные тексты (письма, пуши) тоже проверяются
    cfg = an.get("overcorrection") or {}
    if m_prose and cfg.get("enabled", True) and m_prose["words"] >= int(cfg.get("min_words", 15)) \
            and m_prose["rhythm"].get("sentences", 0) >= int(cfg.get("min_sentences", 8)):
        fs = m_prose["fragment_share_le3"] or 0
        cs = m_prose["connective_share"] if m_prose["connective_share"] is not None else 1
        inf = m_prose["informal_per_100w"]
        para_frag = 0
        if prose_paras:
            para_frag = sum(1 for p in prose_paras
                            if any(len(words_of(p[s:e])) <= 3 for s, e in split_sentences(p))) / len(prose_paras)
        md = m_prose["rhythm"].get("mean_abs_diff") or 0
        signals = []
        if fs >= float(cfg.get("fragment_share_min", 0.3)):
            signals.append(f"фрагментов ≤ 3 слов {fs:.0%}")
        if cs <= float(cfg.get("connective_share_max", 0.25)):
            signals.append(f"предложений со связками {cs:.0%}")
        if len(prose_paras) >= 3 and para_frag >= float(cfg.get("para_fragment_share_min", 0.8)):
            signals.append(f"абзацев с рублеными фразами {para_frag:.0%}")
        if inf >= float(cfg.get("informal_per_100w_min", 1.5)):
            signals.append(f"разговорных вставок {inf} на 100 слов")
        if md >= float(cfg.get("mean_diff_max", 12)):
            signals.append(f"скачки длины {md} слова")
        need = int(cfg.get("min_signals", 3))
        metrics["overcorrection_signals"] = signals
        if len(signals) >= need:
            out.append(mk_analyzer_finding(rb.get("an-overcorrection"), "an-overcorrection", an_level(cfg),
                                           "Похоже на сверхкоррекцию («текст хуманайзера»).",
                                           extra="Сигналы: " + "; ".join(signals) + "."))

    # частоты «не X, а Y», вопросы, тройки, восклицания — по всему тексту
    for key, rid, name, mkey in (("not_x_but_y", "an-not-x-but-y-density", "«не X, а Y»", "not_x_but_y_per_100w"),
                                 ("questions", "an-question-density", "вопросов", "questions_per_100w"),
                                 ("triads", "an-triad-density", "троек однородных членов", "triads_per_100w"),
                                 ("exclamations", "an-exclamation-density", "восклицаний", "exclamations_per_100w")):
        cfg = an.get(key) or {}
        if not cfg.get("enabled", True) or m_all["words"] < int(cfg.get("min_words", 60)):
            continue
        val = m_all[mkey]
        if key == "questions":
            faq_q = sum(1 for u in doc.units if ltype(u) in ("faq-q", "email-subject")
                        and u.text.rstrip().endswith("?"))
            val = round(100.0 * max(0, m_all["questions"] - faq_q) / nw_all, 3)
        thr = cfg.get("warn_per_100w")
        cnt = {"not_x_but_y": m_all["not_x_but_y"], "questions": m_all["questions"], "triads": m_all["triads"],
               "exclamations": m_all["exclamations"]}[key]
        if thr is not None and val >= float(thr) and cnt >= int(cfg.get("min_count", 2)):
            out.append(mk_analyzer_finding(rb.get(rid), rid, an_level(cfg, "info"), f"Частота {name} выше порога жанра.",
                                           extra=f"{val} на 100 слов (порог {thr}, provisional)."))

    # надзаголовки: не чаще одного на N секций с заголовком (H1, H2); N — поле per_sections записи an-eyebrow-rate
    cfg = an.get("eyebrow_rate") or {}
    per = (rb.get("an-eyebrow-rate").per_sections if rb.get("an-eyebrow-rate") else 0) or 0
    if cfg.get("enabled", True) and per:
        eyebrows = [u for u in doc.units if ltype(u) in EYEBROW_SLOTS]
        heads = [u for u in doc.units if ltype(u) in ("headline", "section-title")]
        if eyebrows and heads:
            limit = math.ceil(len(heads) / per)
            if len(eyebrows) > limit:
                out.append(mk_analyzer_finding(rb.get("an-eyebrow-rate"), "an-eyebrow-rate", an_level(cfg),
                                               f"Надзаголовков больше, чем один на {per} секции с заголовком.",
                                               extra=f"{len(eyebrows)} надзаголовков на {len(heads)} заголовков (лимит {limit})."))
        metrics["eyebrows"] = {"count": len(eyebrows), "headings": len(heads), "per_sections": per}

    # все списки по три пункта
    cfg = an.get("lists_of_three") or {}
    if cfg.get("enabled", True):
        sizes, run = [], 0
        for u in doc.units:
            if ltype(u) == "list-item":
                run += 1
            else:
                if run:
                    sizes.append(run)
                run = 0
        if run:
            sizes.append(run)
        metrics["list_sizes"] = sizes
        if len(sizes) >= int(cfg.get("min_lists", 2)) and all(s == 3 for s in sizes):
            out.append(mk_analyzer_finding(rb.get("an-lists-of-three"), "an-lists-of-three", an_level(cfg, "info"),
                                           "Все списки ровно по три пункта.", extra=f"Списков: {len(sizes)}."))

    # числа без факта: сигнал для claims_check.py
    cfg = an.get("numbers_without_fact") or {}
    if cfg.get("enabled", True):
        for ui, u in enumerate(doc.units):
            if u.role == "user-content" and not cfg.get("check_quotes", False):
                continue
            hits = list(FACT_CLAIM_RE.finditer(u.text))
            if not hits:
                continue
            if u.fact_ids:
                continue
            lvl = cfg.get("level_known_empty", "warning") if u.fact_ids is not None else cfg.get("level_unknown", "info")
            if lvl == "off":
                continue
            for mh in hits:
                f = mk_analyzer_finding(rb.get("an-number-without-fact"), "an-number-without-fact", lvl,
                                        "Число или соцдоказательство без ссылки на факт.", doc_unit=ui,
                                        fragment=mh.group(0), slot=slot_info(u),
                                        extra="Сверить с facts.yaml: scripts/text/claims_check.py.")
                f.start, f.end = mh.start(), mh.end()
                f.context = context_of(u.text, mh.start(), mh.end())
                if u.src_offset is not None and doc.source_text:
                    f.line, f.col = line_col(doc.source_text, u.src_offset + mh.start())
                out.append(f)

    # карточки секции одной длины (COPY-C-18): разброс длин тел карточек секции ниже порога
    cfg = an.get("cards_uniform") or {}
    if cfg.get("enabled", True):
        by_sec: dict = {}
        for ui, u in enumerate(doc.units):
            if ltype(u) == "card-body" and (u.genre or genre) == genre:
                by_sec.setdefault((u.page_id, u.section_id), []).append((ui, u))
        for (pid, sid), items in by_sec.items():
            if not sid or len(items) < int(cfg.get("min_cards", 3)):
                continue
            lens = [len(words_of(u.text)) for _, u in items]
            mean = sum(lens) / len(lens)
            cv = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5 / mean if mean else 1.0
            if cv < float(cfg.get("cv_min", 0.25)):
                out.append(mk_analyzer_finding(rb.get("an-cards-uniform"), "an-cards-uniform", an_level(cfg, "info"),
                                               "Карточки секции одной длины.", doc_unit=items[0][0],
                                               slot=slot_info(items[0][1]),
                                               extra=f"Секция {sid}: {len(lens)} карточек по {', '.join(map(str, lens))} "
                                                     f"слов, разброс {cv:.0%} (порог {float(cfg.get('cv_min', 0.25)):.0%})."))

    # «ты» и «вы» в одном тексте: обращение одно на продукт
    cfg = an.get("address_mix") or {}
    if cfg.get("enabled", True):
        out.extend(address_mix(doc, rb, cfg, morph, profile.get("address_form") or ""))
    return out, metrics


# --- сборка отчёта ----------------------------------------------------------------------------------------------------
def severity_of(findings: list[Finding]) -> int:
    w = {"error": 3, "warning": 1, "info": 0, "off": 0}
    per_rule: dict = {}
    for f in findings:
        per_rule[f.id] = per_rule.get(f.id, 0) + w.get(f.level, 0)
    return sum(min(4, v) for v in per_rule.values())


def verdict_of(findings: list[Finding], metrics: dict) -> str:
    errs = sum(1 for f in findings if f.level == "error")
    warns = sum(1 for f in findings if f.level == "warning")
    if any(f.id == "an-overcorrection" for f in findings):
        return "overcorrected"
    if errs:
        return "fail"
    fam = len(metrics.get("markers", {}).get("families", []))
    if warns >= 6 and fam >= 2:
        return "rewrite"
    if warns:
        return "review"
    return "clean"


def lint_document(doc: Document, rules: list[Rule], profiles: dict, genre: str, lang: str, profile_name: str,
                  thresholds_path: Path | None, morph_mode: str = "auto", final: bool = False,
                  metrics_only: bool = False, include_units: bool = False, log: list | None = None,
                  page_audit: bool = False, voice: dict | None = None) -> dict:
    """Проверка документа. page_audit — текст целой страницы без copy deck: пороги замера сняты по слотам, поэтому
    находки анализаторов — не выше warning, а вердикт «переписать» — сигнал «проверить» (ворота — copy deck).
    voice — профиль голоса: словарь «не говорим» и написания (правила), обращение («ты» или «вы»)."""
    g = genre or doc.genre_hint or "landing"
    if g not in GENRES:
        raise UsageError(f"неизвестный жанр {g}; допустимо: {', '.join(GENRES)}")
    prof_name = profile_name or g
    if lang in ("", "auto"):
        lang = detect_lang(" ".join(u.text for u in doc.units))
    profile, th_src = resolve_profile(profiles, prof_name, thresholds_path, lang)
    if voice:
        rules = rules + voice.get("rules", [])
        if voice.get("address_form"):
            profile = merge_dict(profile, {"address_form": voice["address_form"]})
        if voice.get("customer_words"):
            profile = merge_dict(profile, {"customer_words": voice["customer_words"]})
    for u in doc.units:
        if len(words_of(u.text)) >= 3:
            ul = detect_lang(u.text)
            c, l = len(CYR_RE.findall(u.text)), len(LAT_RE.findall(u.text))
            if ul != lang and (c + l) and max(c, l) / (c + l) >= 0.9:
                u.lang = ul
    morph = get_morph(morph_mode) if lang == "ru" else None
    if final:
        profile = merge_dict(profile, {"level_overrides": {"art-placeholder-marker": "error"}})
    rule_findings = run_rules(doc, rules, g, lang, profile, MORPH_REPLACES if morph else None)
    if morph:
        rule_findings = rule_findings + morph_findings(doc, rules, g, profile, morph)
    suppressed: list = []

    def allowed(f: Finding) -> bool:
        """lint_allow слота copy deck: видимое исключение с причиной. Артефакты (ART) и данные (CNT) не подавляются."""
        if f.unit < 0 or f.group in ("ART", "CNT") or f.unit >= len(doc.units):
            return False
        for pat, reason in doc.units[f.unit].allow:
            if fnmatch.fnmatch(f.id, pat):
                s = doc.units[f.unit]
                suppressed.append(f"{f.id} @ {s.slot_id or s.slot_type}{'/' + s.variant if s.variant else ''}"
                                  f"{': ' + reason if reason else ''}")
                return True
        return False
    rule_findings = [f for f in rule_findings if not allowed(f)]
    an_findings, metrics = run_analyzers(doc, rules, g, lang, profile, morph, rule_findings)
    if g == "interface":
        ui_findings, ui_metrics = run_ui_analyzers(doc, rules, profile, morph, lang)
        an_findings += ui_findings
        metrics.update(ui_metrics)
    an_findings = [f for f in an_findings if not allowed(f)]
    if page_audit:
        for f in an_findings:
            if f.level == "error":
                f.level = "warning"
                f.note = (f.note + " " if f.note else "") + "(аудит страницы: сигнал)"
    findings = rule_findings + an_findings
    # порядок отчёта = порядок проверок (спецификация §7): артефакты → выдуманные данные → словари ux и внешние →
    # лексика и синтаксис → структура → анализаторы → сверхкоррекция
    order = {"ART": 0, "CNT": 1, "UX": 2, "EXT": 2, "LEX": 3, "SYN": 3, "PUN": 3, "MKT": 3, "TON": 3, "STR": 4}

    def check_order(f: Finding) -> int:
        if f.id in ("an-overcorrection", "an-reading-level"):
            return 6
        if f.id.startswith("an-") and f.group != "CNT":
            return 5
        return order.get(f.group, 5)
    findings.sort(key=lambda f: (check_order(f), -LEVEL_RANK.get(f.level, 0), f.unit, f.start))
    tells = tells_of_checks()
    for f in findings:
        f.tell = tells.get(f.id, "")
    counts = {lv: sum(1 for f in findings if f.level == lv) for lv in ("error", "warning", "info")}
    verdict = verdict_of(findings, metrics)
    if page_audit and verdict == "rewrite":
        verdict = "review"
    res = {"input": {"path": doc.path, "format": doc.fmt, "units": len(doc.units), "lang": lang, "genre": g,
                     "profile": prof_name, "morphology": bool(morph)},
           "thresholds": th_src,
           "summary": {**counts, "verdict": verdict, "severity": severity_of(findings),
                       "gate": "fail" if counts["error"] else "pass", "suppressed": len(suppressed),
                       "mode": "page-audit" if page_audit else ("registry" if doc.registry is not None else "slots")},
           "metrics": metrics}
    if not metrics_only:
        res["findings"] = [f.as_dict() for f in findings]
    if include_units:
        res["units"] = [{"index": i, **slot_info(u), "words": len(words_of(u.text)), "text": u.text[:200]}
                        for i, u in enumerate(doc.units)]
    missing = [n.split(": ", 1)[1] for n in (log or []) if n.startswith("внешний файл правил не найден")]
    notes = list(doc.notes) + [n for n in (log or []) if not n.startswith("внешний файл правил не найден")]
    if missing:
        notes.append("внешние файлы правил не найдены: " + ", ".join(missing))
    if not genre and not doc.genre_hint:
        notes.append("жанр не задан (--genre): применён landing")
    if page_audit:
        notes.append("аудит страницы без copy deck — сигнал, а не приговор: пороги замера сняты по слотам, находки "
                     "анализаторов не выше warning; ворота — copy deck (copydeck.py check)")
    notes.extend(metrics.pop("ui_notes", []))
    if suppressed:
        notes.append("подавлено lint_allow: " + "; ".join(suppressed))
    if notes:
        res["notes"] = notes
    return res


def load_voice(path: str = "", customer_words_path: str = "") -> dict:
    """Профиль голоса (voice.yaml): vocabulary.avoid — словарь бренда «не говорим» (правила words, входят в плотность
    маркеров), vocabulary.spellings — единое написание, address.ru_form — обращение для проверки «ты» и «вы». Слова
    клиента — customer_words из voc.yaml или meaning.yaml: повтор такого слова в соседних предложениях — приём, а не тик."""
    out: dict = {"rules": [], "address_form": "", "customer_words": []}
    if path:
        d = load_yaml(Path(path)) or {}
        name = Path(path).name
        voc = d.get("vocabulary") or {}
        for n, a in enumerate(voc.get("avoid") or [], 1):
            term = str((a or {}).get("term") or "").strip()
            if len(term) < 2:
                continue
            r = Rule(id=f"voice-avoid-{n:02d}", level=a.get("level") if a.get("level") in LEVELS else "warning",
                     message=f"Словарь бренда «не говорим»: «{term}»" + (f" — {a['reason']}" if a.get("reason") else ""),
                     source=f"{name}#vocabulary.avoid", group="EXT", lang=a.get("lang") or "ru", kind="words",
                     words=[term], replacement=str(a.get("use_instead") or ""), mask_quotes=True, priority=55,
                     slot_types=list(a.get("slot_types") or []), count_as_marker=True,
                     note=f"можно: {a['unless']}" if a.get("unless") else "")
            r.origin = name
            r.compile()
            out["rules"].append(r)
        for n, s in enumerate(voc.get("spellings") or [], 1):
            variants = sorted({str(v) for v in (s or {}).get("variants") or [] if str(v).strip()}, key=len, reverse=True)
            if not variants or not (s or {}).get("preferred"):
                continue
            pat = "(?<![" + WORDCH + "])(?:" + "|".join(re.escape(v) for v in variants) + ")(?![" + WORDCH + "])"
            r = Rule(id=f"voice-spelling-{n:02d}", level="warning", message=f"Единое написание: «{s['preferred']}»",
                     source=f"{name}#vocabulary.spellings", group="EXT", lang=s.get("lang") or "any", pattern=pat,
                     flags="", replacement=str(s["preferred"]), mask_quotes=True, count_as_marker=False, priority=55,
                     note=str(s.get("note") or ""))
            r.origin = name
            r.compile()
            out["rules"].append(r)
        out["address_form"] = {"vy": "vy", "ty": "ty"}.get(str((d.get("address") or {}).get("ru_form") or ""), "")
    if customer_words_path:
        found: list = []

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == "customer_words" and isinstance(v, list):
                        found.extend(str(x) for x in v if str(x).strip())
                    else:
                        walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(load_yaml(Path(customer_words_path)) or {})
        out["customer_words"] = found
    return out


def text_document(text: str, genre: str, vocab: dict, slot_type: str = "", role: str = "", component: str = "",
                  fmt: str = "md", path: str = "<text>") -> Document:
    """Текст → документ: блоки Markdown или HTML; slot_type — тип слота для всех блоков, role и component — роль
    строки интерфейса (в жанре interface без роли — body)."""
    doc = Document(path, fmt, [], text)
    if fmt in ("html", "htm"):
        doc.units, doc.source_text = parse_html(text, genre, vocab, path), ""
    else:
        doc.units = parse_markdown(text, genre, vocab, path)
    urole = resolve_role(role, component, "role") or ("body" if genre == "interface" and not slot_type else "")
    if slot_type:
        srole = role_for(slot_type, vocab)
        for u in doc.units:
            u.slot_type, u.role, u.lint_type = slot_type, srole, lint_type_of(slot_type, vocab)
    for u in doc.units:
        if urole:
            u.role = urole
            if not slot_type:
                u.slot_type, u.lint_type = "", ""
        else:
            u.lint_type = u.lint_type or lint_type_of(u.slot_type, vocab)
    return doc


def lint_text(text: str, genre: str = "landing", lang: str = "auto", slot_type: str = "", profile: str = "",
              fmt: str = "md", metrics_only: bool = False, role: str = "", component: str = "", facts: str = "") -> dict:
    """API для других утилит: текст → результат линтера (dict как один элемент results в JSON). slot_type — id слота
    вида text словаря site; role, component — роль строки интерфейса (жанр interface); facts — путь файла фактов: имена
    мест из него (entities[] вида place) правило о слове на «-ая,» не трогает. Неизвестные — UsageError."""
    vocab = load_vocab()
    profiles = load_profiles()
    log: list = []
    rules = load_rules(profiles=profiles, log=log)
    doc = text_document(text, genre, vocab, slot_type, role, component, fmt)
    doc.places = place_patterns(facts) if facts else []
    return lint_document(doc, rules, profiles, genre, lang, profile, None, metrics_only=metrics_only, log=log)


# --- вывод ---------------------------------------------------------------------------------------------------------
LEVEL_RU = {"error": "ОШИБКА", "warning": "ВНИМАНИЕ", "info": "сигнал"}


def fmt_pos(f: dict) -> str:
    p = f["position"]
    if p.get("line"):
        return f"стр. {p['line']}:{p['col']}"
    s = f.get("slot") or {}
    bits = [s.get("page_id"), s.get("section_id"), s.get("slot_id") or s.get("slot_type")]
    bits = [b for b in bits if b]
    if s.get("variant"):
        bits.append("вар. " + s["variant"])
    return "/".join(bits) if bits else (f"блок {p['unit']}" if p.get("unit", -1) >= 0 else "текст")


def render_text(results: list[dict]) -> str:
    out = []
    for r in results:
        i, sm, mt = r["input"], r["summary"], r["metrics"]
        out.append(f"== {i['path']} · жанр {i['genre']} · язык {i['lang']} · блоков {i['units']}")
        for f in r.get("findings", []):
            out.append(f"{LEVEL_RU.get(f['level'], f['level'])} [{f['id']}{'/' + f['marker_id'] if f['marker_id'] else ''}]"
                       f" {fmt_pos(f)}: {f['message']}" + (f" «{f['fragment']}»" if f['fragment'] else ""))
            if f.get("replacement"):
                out.append(f"    правка: {f['replacement']}")
        mk = mt.get("markers", {})
        a = mt.get("all", {})
        out.append(f"-- слов {a.get('words')}; маркеров {mk.get('count')} ({mk.get('per_100w')} на 100 слов); "
                   f"тире {a.get('dash_per_100w')} (пунктуационных {a.get('dash_punct_per_100w')}); "
                   f"«не X, а Y» {a.get('not_x_but_y_per_100w')}; "
                   f"вопросов {a.get('questions_per_100w')}; троек {a.get('triads_per_100w')}; "
                   f"восклицаний {a.get('exclamations_per_100w')}; конкретика {a.get('concreteness_per_100w')} на 100 слов")
        pr = mt.get("prose") or {}
        if pr:
            rh = pr.get("rhythm", {})
            out.append(f"-- проза: слов {pr.get('words')}, предложений {rh.get('sentences')}, средняя разница длин "
                       f"{rh.get('mean_abs_diff')}, коротких ≤ 8 слов {rh.get('share_short_le8')}, разброс абзацев "
                       f"{pr.get('paragraph_len_cv')}")
        out.append(f"-- итог: {sm['error']} error, {sm['warning']} warning, {sm['info']} info; вердикт {sm['verdict']}; "
                   f"severity {sm['severity']}; ворота {sm['gate']}; пороги: {r['thresholds'].get('thresholds')}")
        for n in r.get("notes", []):
            out.append(f"-- заметка: {n}")
    return "\n".join(out)


def render_md(results: list[dict]) -> str:
    out = []
    for r in results:
        i, sm, mt = r["input"], r["summary"], r["metrics"]
        out.append(f"## copy_lint: `{i['path']}`\n")
        out.append(f"Жанр `{i['genre']}` · язык `{i['lang']}` · блоков {i['units']} · вердикт **{sm['verdict']}** · "
                   f"ворота **{sm['gate']}** · error {sm['error']}, warning {sm['warning']}, info {sm['info']} · "
                   f"пороги: {r['thresholds'].get('thresholds')}\n")
        fs = r.get("findings", [])
        if fs:
            out.append("| Уровень | Правило | Маркер | Где | Фрагмент | Что не так | Правка |")
            out.append("|---|---|---|---|---|---|---|")
            for f in fs:
                frag = (f["fragment"] or "").replace("|", "\\|").replace("\n", " ")
                msg = f["message"].replace("|", "\\|")
                rep = (f.get("replacement") or "").replace("|", "\\|")
                out.append(f"| {f['level']} | `{f['id']}` | {f['marker_id']} | {fmt_pos(f)} | {frag} | {msg} | {rep} |")
        a, mk = mt.get("all", {}), mt.get("markers", {})
        out.append("")
        out.append(f"Метрики: слов {a.get('words')}; маркеров {mk.get('count')} ({mk.get('per_100w')} на 100 слов, "
                   f"семьи {', '.join(mk.get('families', []))}); тире {a.get('dash_per_100w')} (пунктуационных "
                   f"{a.get('dash_punct_per_100w')}); «не X, а Y» "
                   f"{a.get('not_x_but_y_per_100w')}; вопросы {a.get('questions_per_100w')}; тройки "
                   f"{a.get('triads_per_100w')}; восклицания {a.get('exclamations_per_100w')}; конкретика "
                   f"{a.get('concreteness_per_100w')} на 100 слов.\n")
    return "\n".join(out)


# --- самопроверка -----------------------------------------------------------------------------------------------------
SELFTEST_CASES = [
    # (текст, жанр, ожидаемый id или префикс, должно сработать)
    ("Наша компания является лидером и представляет собой команду профессионалов.", "landing", "ru-lex-copula", True),
    ("Мы — команда из 12 инженеров.", "landing", "ru-lex-copula", False),
    ("Сервис не только экономит время, но и снижает затраты.", "landing", "ru-syn-not-only-but-also", True),
    ("Отчёт включает не только штатных сотрудников.", "landing", "ru-syn-not-only-but-also", False),
    ("Это не просто курс, а целая философия.", "landing", "ru-syn-not-just", True),
    ("Он пришёл сюда не просто так.", "landing", "ru-syn-not-just", False),
    ("Рынок вырос :contentReference[oaicite:0]{index=0}.", "landing", "art-chatbot-citation", True),
    ("Подробнее в отчёте: https://example.com/?utm_source=chatgpt.com", "article", "art-ai-utm", True),
    ("В современном мире каждый бизнес ищет рост.", "landing", "ru-lex-intro-cliche", True),
    ("Built for the modern team. Unleash your potential.", "landing", "en-mkt-banned-openers", True),
    ("Linear is a purpose-built tool for planning software.", "landing", "en-mkt-banned-openers", False),
    ("Надеюсь, это поможет! Если есть вопросы — пишите.", "article", "art-assistant-reply-ru", True),
]


def levels_summary(rules: list[Rule], profiles: dict, genre: str) -> dict:
    """Сколько правил жанра на каком уровне — с поправками жанра, уровнями профиля и группами (правила с шаблоном)."""
    prof, _ = resolve_profile(profiles, genre, None)
    counts = {lv: 0 for lv in LEVELS}
    probe = Unit("", "", "")
    for r0 in rules:
        if r0.kind in ("analyzer", "manual"):
            continue
        r = r0.for_genre(genre)
        if r.genres and genre not in r.genres:
            continue
        counts[effective_level(r, genre, probe, prof)] += 1
    return counts


def selftest() -> int:
    ok = True
    fails: list = []
    n_checks = 0

    def check(name: str, cond, detail="") -> None:
        nonlocal ok, n_checks
        n_checks += 1
        if not cond:
            ok = False
            fails.append(f"FAIL {name}" + (f" — {detail}" if detail else ""))

    profiles = load_profiles()
    log: list = []
    try:
        rules = load_rules(profiles=profiles, log=log)
    except Exception as exc:
        print(f"FAIL загрузка словарей: {exc}")
        return 1
    vocab = load_vocab()
    ids = {r.id for r in rules}
    rb = {r.id: r for r in rules}
    print(f"словари: {len(rules)} правил из {len({r.origin for r in rules})} файлов; словарь site: "
          f"{len(vocab['slot_types'])} слотов вида text, {len(vocab['page_types'])} типов страниц; ролей текста: "
          f"{len(closed_roles())}")
    # 0. сводка правил по уровням для жанра: уровни в файлах — у правил, счёт для жанра — здесь
    print("сводка правил с шаблоном по уровням для жанра (error · warning · info · off):")
    summ = {}
    for g in GENRES:
        summ[g] = levels_summary(rules, profiles, g)
        print(f"  {g:10s} " + " · ".join(f"{summ[g][lv]}" for lv in LEVELS))
    check("сводка: в interface правила ux с уровнями канона — error больше, чем на landing",
          summ["interface"]["error"] > 0 and rb["ux-5-2-02"].for_genre("interface").level == "error" and
          rb["ux-5-2-02"].for_genre("landing").level == "info")
    # 1. каждое правило с примерами: «плохо» срабатывает, «хорошо» — нет
    bad_fail, good_fail, checked = [], [], 0
    for r in rules:
        if r.kind in ("analyzer", "manual") or not r.examples or r.level == "off":
            continue
        bad, good = r.examples.get("bad"), r.examples.get("good")

        def hits_in(txt: str) -> int:
            n = 0
            for m in r.regex.finditer(txt):
                if r.mask_quotes and inside((m.start(), m.end()), masked_spans(txt)):
                    continue
                if r.unless_re is not None:
                    ss, se = sentence_of(txt, m.start())
                    if r.unless_re.search(txt[ss:se]):
                        continue
                n += 1
            return n
        need = max(1, r.min_count)
        if bad and not r.examples.get("skip_bad"):
            checked += 1
            if hits_in(bad) < need:
                bad_fail.append(r.id)
        if good and not r.examples.get("skip_good"):
            if hits_in(good) >= need:
                good_fail.append(r.id)
    print(f"примеры правил: проверено {checked}; «плохо» не пойман: {len(bad_fail)}; «хорошо» пойман: {len(good_fail)}")
    check("примеры правил: «плохо» ловится", not bad_fail, ", ".join(bad_fail[:40]))
    check("примеры правил: «хорошо» не ловится", not good_fail, ", ".join(good_fail[:40]))

    def lt(text, genre="landing", role="", slot_type="", component="", fmt="md", page_audit=False, voice=None,
           morph="auto"):
        doc = text_document(text, genre, vocab, slot_type, role, component, fmt)
        return lint_document(doc, rules, profiles, genre, "auto", "", None, morph, page_audit=page_audit, voice=voice)

    def deck(data, genre="", all_variants=False, voice=None):
        units, gh = parse_copy_deck(data, vocab, "<deck>", all_variants)
        return lint_document(Document("<deck>", "yaml", units, "", gh), rules, profiles, genre, "auto", "", None,
                             voice=voice)

    def found(res, rid, level=None):
        return [f for f in res.get("findings", []) if fnmatch.fnmatch(f["id"], rid) and (level is None or
                                                                                          f["level"] == level)]

    def raises(fn) -> bool:
        try:
            fn()
        except UsageError:
            return True
        return False
    # 2. сценарии
    for text, genre, rid, expect in SELFTEST_CASES:
        if rid not in ids:
            check(f"сценарий {rid}: правило есть в словарях", False)
            continue
        check(f"сценарий {rid}: {'срабатывание' if expect else 'тишина'} на «{text[:50]}»",
              bool(found(lt(text, genre), rid)) == expect)
    # 3. анализаторы
    mono = " ".join(["Это длинное предложение содержит ровно двенадцать слов, и следующее будет таким же."] * 12)
    check("an-rhythm-monotone на монотонном тексте", found(lt(mono, "article"), "an-rhythm-monotone"))
    rag = ("Мы открылись весной. Честно. Без пафоса. Кофе варим сами, зерно берём у знакомых обжарщиков.\n\n"
           "Утро. Очередь. Кто-то спешит на работу, кто-то нет. Короче, всем хватает.\n\n"
           "Десерты? Печём ночью. Сами. Вот так.\n\n"
           "Цены обычные. Ну правда обычные. Капучино двести двадцать, раф двести шестьдесят.\n\n"
           "Заходите. Или не заходите. Решать вам.")
    r = lt(rag, "article")
    check("an-overcorrection на нарочито рваном тексте", found(r, "an-overcorrection"),
          str(r["metrics"].get("overcorrection_signals")))
    m = text_metrics("Москва — столица. Сроки — 3–5 дней. Мы работаем — и это главное — без выходных.", "ru")
    check("тире: 4 без диапазона 3–5", m["dash_count"] == 4, str(m["dash_count"]))
    check("тире: 2 обязательных и 2 пунктуационных", (m["dash_obligatory"], m["dash_punct"]) == (2, 2))
    m3 = text_metrics("Мастер ответил:\n— Приедем завтра к девяти.", "ru")
    check("тире прямой речи в начале строки — обязательное", (m3["dash_obligatory"], m3["dash_punct"]) == (1, 0))
    m2 = text_metrics("Смета и выезд замерщика — бесплатно. Отправляем в день обжарки — без месяцев на складе.", "ru")
    check("тире «поле — значение» и «пояснение после глагола»", (m2["dash_obligatory"], m2["dash_punct"]) == (1, 1))
    # 4. copy deck: число без факта, стрелка, отзыв, lint_allow
    d1 = {"copy_deck": {"version": 0, "pages": [{"page_id": "home", "page_type": "landing-saas", "sections": [
        {"section_id": "hero", "slots": [
            {"slot_id": "h1", "slot_type": "headline", "variants": [{"id": "a", "text": "Более 10 000 клиентов"}],
             "chosen": "a", "fact_ids": []},
            {"slot_id": "cta", "slot_type": "cta-label", "variants": [{"id": "a", "text": "Начать →"}], "chosen": "a"}]}]}]}}
    r = deck(d1)
    check("copy deck: число без факта отмечено", found(r, "an-number-without-fact"))
    check("copy deck: стрелка в подписи кнопки — error", found(r, "ru-pun-arrow-cta", "error"))
    r3 = deck({"slots": [{"slot_type": "testimonial-quote",
                          "text": "Команда профессионалов, всё сделали качественно. Надеюсь, это поможет!"}]}, "landing")
    groups3 = {f["group"] for f in r3["findings"]}
    check("отзыв (user-content): только артефакты", not (groups3 & STYLE_GROUPS) and "ART" in groups3, str(groups3))
    r2 = deck({"slots": [{"slot_type": "headline", "text": "Не только кофе, но и десерты: 4,9 из 5 на Картах",
                          "lint_allow": [{"rule": "ru-syn-not-only-but-also", "reason": "слоган бренда из брифа"},
                                         {"rule": "an-number-without-fact", "reason": "попытка подавить данные"}],
                          "fact_ids": []}]}, "landing")
    check("lint_allow: стиль подавлен, данные — нет", not found(r2, "ru-syn-not-only-but-also") and
          r2["summary"].get("suppressed") == 1 and found(r2, "an-number-without-fact"))
    # 5. роль — вход: неизвестная роль, тип слота, часть компонента — ошибка вызова
    check("неизвестная роль — ошибка вызова", raises(lambda: lt("x", "interface", role="button")))
    check("неизвестный тип слота — ошибка вызова", raises(lambda: lt("x", slot_type="hero-title")))
    check("неизвестная часть компонента — ошибка вызова", raises(lambda: lt("x", "interface", component="Field.Caption")))
    check("роль строки не из ролей части — ошибка вызова", raises(lambda: lt("x", "interface", "title", component="Button")))
    check("часть с двумя ролями без --role — ошибка вызова", raises(lambda: lt("x", "interface", component="IconButton")))
    check("роль в короткой форме copy deck вне списка — ошибка вызова",
          raises(lambda: deck({"slots": [{"role": "cta", "text": "Сохранить"}]}, "interface")))
    r = lt("Неверный формат телефона", "interface", component="Field.Error")
    check("роль части компонента: Field.Error → error; «Неверный» — запрет ux 07/06 §3.3",
          found(r, "ux-3-3-05", "error") and found(r, "ux-3-3-05")[0]["slot"]["role"] == "error")
    # 6. жанр interface: уровни ux 07/06 без поправок сайта
    check("«Нам доверяют»: interface — error", found(lt("Нам доверяют", "interface", "title"), "ux-5-2-02", "error"))
    rl = deck({"slots": [{"slot_type": "logos-caption", "text": "Нам доверяют"}]}, "landing")
    check("«Нам доверяют»: landing — не выше info", rl["findings"] and all(f["level"] == "info" for f in rl["findings"]),
          str([(f["id"], f["level"]) for f in rl["findings"]]))
    check("«10 000+ пользователей»: interface — error", found(lt("10 000+ пользователей", "interface", "title"),
                                                             "ux-5-2-01", "error"))
    rs = deck({"slots": [{"slot_type": "hero-proof", "text": "10 000+ пользователей", "fact_ids": ["users-count"]}]},
              "landing")
    check("«10 000+ пользователей» на сайте с fact_ids — без находки ux-5-2", not found(rs, "ux-5-2-*"))
    check("«Подробнее» в ссылке интерфейса — error", found(lt("Подробнее", "interface", "link"), "ux-3-2-07", "error"))
    rp = deck({"slots": [{"slot_type": "cta-label", "text": "Подробнее"},
                         {"slot_type": "cta-secondary-label", "text": "Подробнее"}]}, "landing")
    lv = sorted((f["id"], f["level"]) for f in rp["findings"])
    check("«Подробнее» на лендинге — warning (слабая кнопка), не error правила ux",
          lv == [("ru-mkt-weak-cta", "warning")] * 2 and rb["ux-3-2-07"].for_genre("landing").level == "warning",
          str(lv))
    check("«Каталог» в навигации многостраничника — конвенция, в интерфейсе — warning",
          not found(deck({"slots": [{"slot_type": "nav-label", "text": "Каталог"}]}, "site-page"), "ux-3-2-01") and
          found(lt("Каталог", "interface", "nav"), "ux-3-2-01", "warning"))
    check("правил ux-6-5-07…09 нет — пробелы ведут правила набора H", not ({"ux-6-5-07", "ux-6-5-08", "ux-6-5-09"} & ids))
    check("двойной пробел: interface — error (typo-double-space)",
          found(lt("Нет  связи", "interface", "banner"), "typo-double-space", "error"))
    check("Title Case в заголовке интерфейса — error", found(lt("Мои Заявки И Замеры", "interface", "title"),
                                                            "ru-pun-title-case", "error"))
    check("эмодзи в кнопке интерфейса — error", found(lt("Создать 🚀", "interface", "action"), "ru-pun-emoji-heading",
                                                     "error"))
    check("прямые кавычки в интерфейсе — error", found(lt('Проект "Альфа" создан', "interface", "toast"),
                                                      "ru-pun-straight-quotes", "error"))
    check("подстановка ICU {name} в строке интерфейса — не шаблон-заглушка",
          not found(lt("{name} пригласил вас в проект", "interface", "body"), "art-template-slot"))
    # 7. реестр texts.md на фикстурах: чистый — 0 находок, с посеянными дефектами — ровно четыре
    kbpaths.use("tests")
    import fixture_project  # noqa: WPS433
    for name, want in (("cabinet-texts", []),
                       ("cabinet-texts-defects", [("an-ui-action-name", "warning"), ("an-ui-action-synonym", "error"),
                                                  ("an-ui-formats", "warning"), ("an-ui-object-alias", "error")])):
        with fixture_project.built(name) as fx:
            reg = fx.project / "screens" / "office" / "texts.md"
            doc = read_document(str(reg), "", vocab)
            res = lint_document(doc, rules, profiles, "", "auto", "", None)
        got = sorted((f["id"], f["level"]) for f in res["findings"])
        check(f"реестр {name}: жанр interface, находки {want or 'нет'}", res["input"]["genre"] == "interface" and
              got == sorted(want), str(got))
        if name == "cabinet-texts-defects":
            f0 = found(res, "an-ui-object-alias")
            check("находка реестра: строка файла и ключ строки", f0 and f0[0]["position"]["line"] == 22 and
                  f0[0]["slot"].get("key") == "requests.list.empty-first-run.empty", str(f0[:1]))
    # 8. межстрочные анализаторы на строках интерфейса
    items = [
        {"key": "requests.list.status-new.badge", "role": "badge", "text": "Новая", "group": "статусы"},
        {"key": "requests.list.status-set.badge", "role": "badge", "text": "Замер назначен", "group": "статусы"},
        {"key": "requests.list.status-no.badge", "role": "badge", "text": "Отказ", "group": "статусы"},
        {"key": "requests.list.title.title", "role": "title", "text": "Заявки на замер"},
        {"key": "requests.list.heading.section-title", "role": "section-title", "text": "Заявки на замер"},
        {"key": "requests.list.long.action", "role": "action", "text": "Сохранить все изменения заявки", "maxlen": "12"},
        {"key": "requests.list.count.status", "role": "status", "text": "{n, plural, =1 {# заявка} other {# заявок}}"},
        {"key": "requests.list.open.status", "role": "status", "text": "{n, select, one {Открыта}}"},
        {"key": "requests.list.saved.toast", "role": "toast", "text": "Введённое сохранено"},
        {"key": "requests.card.saved.toast", "role": "toast", "text": "Введенное сохранено"},
        {"key": "requests.card.en1.label", "role": "label", "text": "Color"},
        {"key": "requests.card.en2.label", "role": "label", "text": "Favourite"},
        {"key": "requests.card.en3.label", "role": "label", "text": "Organize"},
        {"key": "requests.card.price.hint", "role": "hint", "text": "Смета от 9800 рублей"},
        {"key": "requests.card.window.hint", "role": "hint", "text": "Окно {from} - {to}"},
    ]
    units = []
    for it in items:
        u = Unit(it["text"], "", it["role"], slot_id=it["key"], genre="interface", key=it["key"],
                 maxlen=it.get("maxlen", ""), group=it.get("group", ""))
        units.append(u)
    rdoc = Document("<registry>", "texts", units, "", "interface", registry={"objects": {}, "actions": {}})
    rr = lint_document(rdoc, rules, profiles, "", "ru", "", None)
    morph_ok = rr["input"]["morphology"]
    if morph_ok:
        fg = found(rr, "an-ui-group-form")
        check("формы группы статусов: «Отказ» — не «какая?»", len(fg) == 1 and fg[0]["slot"]["key"].endswith("status-no.badge"),
              str([f["slot"].get("key") for f in fg]))
    fd = found(rr, "an-ui-duplicate")
    check("дубль на экране: одинаковые заголовок и заголовок секции", len(fd) == 1, str(len(fd)))
    check("maxlen: строка длиннее предела — error", found(rr, "an-ui-maxlen", "error"))
    check("длина по роли: кнопка длиннее 3 слов — warning", any(f["slot"].get("key", "").endswith("long.action")
                                                               for f in found(rr, "an-ui-role-length", "warning")))
    icu = [f["message"] for f in found(rr, "an-ui-icu")]
    check("ICU: «=1» вместо one, нет веток few и many — warning; нет other — error",
          any("=1" in x for x in icu) and any("few" in x for x in icu) and found(rr, "an-ui-icu", "error"), str(icu))
    check("«ё» и «е» в одном слове — warning", found(rr, "an-ui-yo-mix", "warning"))
    check("US и UK орфография вместе — warning", found(rr, "an-ui-us-uk", "warning"))
    fmt_ = [f["message"] for f in found(rr, "an-ui-formats")]
    check("форматы: число литералом и диапазон с дефисом", any("Число, дата, сумма" in x for x in fmt_) and
          any("Диапазон — тире без пробелов" in x for x in fmt_), str(fmt_))
    long_body = ("Документы подтверждения принадлежности объекта недвижимости предоставляются собственником "
                 "исключительно одновременно с доверенностями представителей, уполномоченных распоряжаться "
                 "принадлежащим имуществом, включая дополнительные согласования управляющей организации, "
                 "администрации муниципального образования, регистрационной палаты, нотариальной конторы. "
                 "Дополнительные экземпляры предоставляются заявителем самостоятельно.")
    rb_ = lt(long_body, "interface", "body")
    check("уровень чтения: роль body — метрика и сигнал о длинных словах", rb_["metrics"].get("reading") and
          found(rb_, "an-reading-level", "info"))
    check("уровень чтения: подпись поля не проверяется", not lt(long_body, "interface", "label")["metrics"].get("reading"))
    # 9. «ты» и «вы»
    check("«ты» и «вы» в одном тексте — an-address-mix",
          found(lt("Оставьте заявку.\n\nТы получишь смету завтра.", "landing"), "an-address-mix"))
    check("голос на «ты»: строка на «вы» — находка", found(lt("Оставьте заявку.", "landing",
                                                              voice={"address_form": "ty"}), "an-address-mix"))
    # 10. калибровки линтера (text X §7: К1–К16, К28)
    check("К1: «10 - 15 дней» — диапазон (typo-range-hyphen), не дефис вместо тире",
          not found(lt("Сдача через 10 - 15 дней.", "landing", slot_type="body"), "ru-pun-hyphen-as-dash") and
          found(lt("Сдача через 10 - 15 дней.", "landing", slot_type="body"), "typo-range-hyphen") and
          found(lt("Анамнез - это разговор с пациентом.", "landing", slot_type="body"), "ru-pun-hyphen-as-dash"))
    check("К3: сообщение ru-mkt-superlatives ссылается на COPY-L-SUP-01", "COPY-L-SUP-01" in rb["ru-mkt-superlatives"].message
          and "38-ФЗ" not in rb["ru-mkt-superlatives"].message)
    sup = lt("Лучшая мастерская в городе — по мнению наших гостей.", "landing", slot_type="headline")
    check("право — только в claims_check.py: правил COPY-L-… в словарях линтера нет, превосходная степень — одна "
          "находка стиля", not [i for i in ids if i.startswith("COPY-L-")] and not found(sup, "COPY-L-*") and
          [f["id"] for f in sup["findings"] if f["fragment"] == "Лучшая"] == ["ru-mkt-superlatives"],
          str([(f["id"], f["fragment"]) for f in sup["findings"]]))
    check("К4: «По статистике, 78 %» — размытая атрибуция, в geo — error",
          found(lt("По статистике, 78 % клиентов возвращаются.", "geo", slot_type="geo-answer"),
                "ru-lex-vague-attribution", "error"))
    dense = ("В современном мире уникальный комплексный подход обеспечивает эффективное решение ключевых задач. "
             "Наша команда профессионалов предлагает инновационные решения и индивидуальный подход. "
             "Мы гарантируем высокое качество и надёжность, открываем новые горизонты и выводим бизнес на новый "
             "уровень. Уникальный опыт и мощные инструменты позволяют достигать впечатляющих результатов. "
             "Комплексное решение для вашего бизнеса — это наш приоритет и наша миссия.")
    full, page = lt(dense, "landing"), lt(dense, "landing", page_audit=True)
    check("К5: аудит страницы без copy deck — анализаторы не выше warning, вердикт — сигнал",
          found(full, "an-marker-density") and not found(page, "an-*", "error") and
          page["summary"]["mode"] == "page-audit" and page["summary"]["verdict"] != "rewrite",
          f"{full['summary']} / {page['summary']}")
    check("плотность маркеров выше верхнего порога жанра — warning, не error (allow_error: false)",
          found(full, "an-marker-density", "warning") and not found(full, "an-marker-density", "error") and
          all(resolve_profile(profiles, g, None)[0]["analyzers"]["marker_density"].get("allow_error") is False
              for g in SITE_GENRES), str(found(full, "an-marker-density")))
    check("правила микрокопи интерфейса на тексте страницы — один набор уровней у всех жанров сайта",
          all((resolve_profile(profiles, g, None)[0].get("level_overrides") or {}).get("ux-6-4-10") == "info" and
              (resolve_profile(profiles, g, None)[0].get("level_overrides") or {}).get("ux-6-4-*") == "warning"
              for g in SITE_GENRES) and "ux-6-4-10" not in
          (resolve_profile(profiles, "interface", None)[0].get("level_overrides") or {}))
    check("К6: «Подробнее» на лендинге — не error", not found(rp, "ux-3-2-07", "error"))
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        fpath = Path(td) / "facts.yaml"
        fpath.write_text(yaml.safe_dump({"facts": [], "entities": [
            {"id": "office", "type": "place", "names": ["улица Лесная", "Лесная улица, 3"]},
            {"id": "brand", "type": "brand", "names": ["Ясная"]}]}, allow_unicode=True), encoding="utf-8")
        addr = "Приезжайте: улица Лесная, дом 3, вход со двора."
        check("слово на «-ая,» внутри имени места из фактов (entities вида place) — вне правила; без фактов — находка",
              found(lt(addr, "landing", slot_type="subheadline"), "ux-6-4-10") and
              not found(lint_text(addr, "landing", slot_type="subheadline", facts=str(fpath)), "ux-6-4-10") and
              found(lint_text("Заходите: площадь Ясная, дом 3.", "landing", slot_type="subheadline", facts=str(fpath)),
                    "ux-6-4-10"))
        dpath = Path(td) / "deck.yaml"
        dpath.write_text(yaml.safe_dump({"copy_deck": {"facts_ref": "facts.yaml", "pages": [
            {"page_id": "p", "page_type": "contacts-page", "sections": [{"section_id": "s", "slots": [
                {"slot_id": "a", "slot_type": "subheadline", "text": addr}]}]}]}}, allow_unicode=True), encoding="utf-8")
        ddoc = read_document(str(dpath), "", vocab)
        check("copy deck: места берутся из его facts_ref", ddoc.places and not found(
            lint_document(ddoc, rules, profiles, "", "auto", "", None), "ux-6-4-10"))
    hp = found(lt("Ремонт квартир в Нижнем Новгороде и области", "landing", slot_type="headline"), "typo-hanging-preposition")
    check("висячий предлог: пример правки — из текста находки, у каждой находки свой",
          [f["example"].get("good") for f in hp] == ["в\u00a0Нижнем", "и\u00a0области"] and
          all("неразрывный пробел после" in f["replacement"] for f in hp), str([(f["fragment"], f["example"]) for f in hp]))
    tag = deck({"slots": [{"slot_type": "footer-tagline", "text": "Быстро. Просто. Надёжно."}]}, "landing")
    check("К7: рубленый драматизм в слогане (footer-tagline) — сигнал", found(tag, "ru-syn-chopped", "info") and
          not found(tag, "ru-syn-chopped", "warning"))
    rep_text = ("Прораб каждый вечер присылал фото с объекта, чтобы хозяин видел работу. Мастер тоже присылал фото "
                "плитки, когда заканчивал стену в ванной.")
    vr = lt(rep_text, "landing", slot_type="body", voice={"customer_words": ["каждый вечер присылал фото"]})
    check("К7: повтор слова клиента (customer_words) — не находка", not found(vr, "an-verb-repeat"))
    check("К8: длинное совпадение с кавычками внутри — находка; фраза целиком в кавычках — нет",
          found(lt("Сервис не только «экономит» время, но и снижает затраты.", "landing", slot_type="body"),
                "ru-syn-not-only-but-also") and
          not found(lt("Клиент написал: «Сервис не только экономит время, но и снижает затраты».", "landing",
                       slot_type="body"), "ru-syn-not-only-but-also"))
    check("К8: кликбейт в заголовке статьи и теме письма",
          found(deck({"slots": [{"slot_type": "article-heading", "text": "Вы не поверите, сколько стоит ремонт"}]},
                     "article"), "meta-clickbait", "warning") and
          found(deck({"slots": [{"slot_type": "email-subject", "text": "Вы не поверите, что внутри"}]}, "email-form"),
                "meta-clickbait", "error"))
    dm = {"copy_deck": {"pages": [{"page_id": "home", "page_type": "landing-lead-services",
                                   "meta": {"title": "Ремонт квартир от 9 800 ₽/м² — гарантия 3 года",
                                            "fact_ids": ["price-from-per-m2", "guarantee-3-years"]},
                                   "sections": []}]}}
    check("К9: meta.fact_ids снимают число без факта в мета", not found(deck(dm), "an-number-without-fact"))
    dv = {"slots": [{"slot_type": "headline", "chosen": "a", "variants": [
        {"id": "a", "text": "Ремонт квартир с 2014 года"},
        {"id": "b", "text": "В современном мире ремонт — это стресс"},
        {"id": "c", "status": "rejected", "text": "Откройте для себя ремонт нового поколения"}]}]}
    check("К10: по умолчанию — выбранный вариант; --all-variants — живые, без rejected",
          not found(deck(dv, "landing"), "ru-lex-intro-cliche") and
          found(deck(dv, "landing", all_variants=True), "ru-lex-intro-cliche") and
          not found(deck(dv, "landing", all_variants=True), "ru-mkt-banned-openers"))
    check("К11: «X, который Y» с fact_ids — без находки",
          not found(deck({"slots": [{"slot_type": "headline", "text": "Лампа, которая сама подбирает свет",
                                     "fact_ids": ["auto-light"]}]}, "landing"), "ru-mkt-headline-which") and
          found(deck({"slots": [{"slot_type": "headline", "text": "Сервис, который понимает ваш бизнес"}]}, "landing"),
                "ru-mkt-headline-which"))
    stuffing = ("Ремонт квартир в Нижнем Новгороде — наша работа. Мы делаем ремонт квартир любой сложности, "
                "ремонт квартир под ключ и косметический ремонт квартир.")
    check("К12: набивка ключа на лендинге — сигнал, в статье — warning",
          found(lt(stuffing, "landing", slot_type="body"), "geo-keyword-stuffing", "info") and
          found(lt(stuffing, "article", slot_type="article-paragraph"), "geo-keyword-stuffing", "warning"))
    labels = deck({"slots": [{"slot_type": "section-title", "text": x} for x in
                             ("Наши преимущества", "Частые вопросы", "Вопросы и ответы", "Контакты")]}, "landing")
    got_l = [f["fragment"] for f in found(labels, "ru-mkt-label-headings", "warning")]
    check("К13: ярлык секции — warning; «Частые вопросы», «Вопросы и ответы», «Контакты» — конвенции",
          got_l == ["Наши преимущества"], str(got_l))
    vf = kbpaths.kb("text", "05-voice-editorial", "examples", "voice-otves-warm.yaml")
    voice = load_voice(str(vf))
    rv = lt("Команда профессионалов делает ремонт в кратчайшие сроки.", "landing", slot_type="body", voice=voice)
    check("К14: словарь бренда «не говорим» (--voice) — находки, в плотности маркеров",
          len(found(rv, "voice-avoid-*")) >= 2 and all(f["counts_as_marker"] for f in found(rv, "voice-avoid-*")))
    check("К14: EN-приметы истории", found(lt("They got the kitchen of their dreams and couldn't be happier.", "landing",
                                             slot_type="body"), "en-mkt-story-cliches"))
    check("К14: аббревиатура после двоеточия и «since 2014» — без находок ux",
          not found(lt("Оплата: СБП", "interface", "label"), "ux-6-4-11") and
          not found(lt("Open since 2014", "interface", "label"), "ux-4-2-07"))
    dc = {"copy_deck": {"pages": [{"page_id": "home", "page_type": "landing-saas", "sections": [
        {"section_id": "features", "slots": [{"slot_id": f"c{i}", "slot_type": "card-body", "text": txt} for i, txt in
                                             enumerate(["Счёт уходит клиенту сразу после визита мастера.",
                                                        "Мастер видит запись и адрес клиента в телефоне.",
                                                        "Отчёт по выручке собирается каждый вечер сам."])]}]}]}}
    fc = found(deck(dc), "an-cards-uniform", "info")
    check("К15: карточки секции одной длины — сигнал an-cards-uniform с приметой реестра (tells.yaml#checks)",
          fc and fc[0].get("tell") == "uniform-card-copy", str(fc[:1]))
    check("К15: утверждение со счётом словами — число без факта",
          found(lt("Мы работаем в два раза быстрее конкурентов.", "landing"), "an-number-without-fact"))
    check("К16: строчная после двоеточия и грамматическое тире в прозе — без находок ux",
          not found(lt("Ремонт в Сормове: ремонт под ключ", "landing", slot_type="headline"), "ux-6-4-11") and
          not found(deck({"slots": [{"slot_type": "guarantee-text", "text": "Смета — бесплатно."}]}, "landing"),
                    "ux-5-3-03"))
    ma = {"copy_deck": {"pages": [{"page_id": "home", "page_type": "home-multipage", "meta": {"title": "Сбер"},
                                   "lint_allow": [{"rule": "meta-title-too-short", "reason": "известный бренд"}],
                                   "sections": []}]}}
    rma = deck(ma)
    check("К28: короткий title известного бренда — lint_allow страницы", not found(rma, "meta-title-too-short") and
          rma["summary"]["suppressed"] == 1)
    tpl = ((load_yaml(ROOT / "07-seo-geo-copy" / "meta-rules.yaml") or {}).get("templates") or {}) \
        .get("landing-lead-services", {}).get("example_ru") or {}
    check("К28: description шаблона landing-lead-services не начинается с тех же 42 знаков, что title",
          tpl.get("title") and tpl.get("description") and tpl["title"][:42] != tpl["description"][:42])
    # 11. надзаголовки, стрелка, разряды
    per = rb["an-eyebrow-rate"].per_sections
    eb = {"copy_deck": {"pages": [{"page_id": "p", "page_type": "landing-saas", "sections": [
        {"section_id": f"s{i}", "slots": [{"slot_type": "eyebrow", "text": f"Этап {i}"},
                                          {"slot_type": "section-title", "text": f"Раздел {i}"}]} for i in range(3)]}]}}
    feb = found(deck(eb), "an-eyebrow-rate")
    check("TR-14: число надзаголовков — per_sections записи an-eyebrow-rate (3)", per == 3 and feb and
          "лимит 1" in feb[0]["message"], str(feb[:1]))
    check("VI-29: «↗» у ссылки на внешний сайт — не ошибка; «→» в кнопке — error",
          not found(deck({"slots": [{"slot_type": "cta-secondary-label", "text": "Документация ↗"}]}, "landing"),
                    "ru-pun-arrow-cta") and found(deck({"slots": [{"slot_type": "cta-label", "text": "Начать →"}]},
                                                       "landing"), "ru-pun-arrow-cta", "error"))
    check("TX-27: разряды с U+00A0 и U+202F — без находок набора",
          not found(lt("Цена 25 000 ₽ и 30 000 ₽", "landing", slot_type="body"), "typo-thousands"))
    check("TX-12, TX-15: поправки ux-5-2-*, ux-3-2-0[14] — только в жанрах сайта",
          all(set(rb[i].genre_variants) <= set(SITE_GENRES) and rb[i].genre_variants for i in
              ("ux-5-2-01", "ux-5-2-02", "ux-3-2-01", "ux-3-2-04")) and not rb["ux-5-2-01"].for_genre("interface")
          is not rb["ux-5-2-01"])
    for line in fails:
        print(line)
    print(f"проверок: {n_checks}, провалов: {len(fails)}")
    print("self-test:", "OK" if ok else "FAIL")
    return 0 if ok else 1


# --- CLI -------------------------------------------------------------------------------------------------------------
class _ArgParser(argparse.ArgumentParser):
    """Ошибка ключей — код 1 (у argparse по умолчанию 2, а 2 у линтера значит «есть error в тексте»)."""

    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"copy_lint: {message}\n")
        raise SystemExit(1)


def main(argv=None) -> int:
    ap = _ArgParser(description="Линтер текстов RU/EN по жанру и роли строки: маркетинговые тексты сайта (жанры сайта) и "
                                "тексты интерфейса (жанр interface, реестр texts.md). Коды: 0 — нет error, 2 — есть error, "
                                "1 — ошибка вызова (неизвестная роль, тип слота, часть компонента, жанр).")
    ap.add_argument("paths", nargs="*", help="файлы .txt .md .html .yaml, реестр texts.md; «-» — stdin")
    ap.add_argument("--genre", choices=GENRES, help="жанр: " + ", ".join(GENRES) + "; у copy deck — page_type.genre словаря "
                                                    "site, у реестра texts.md — interface")
    ap.add_argument("--lang", default="auto", choices=("auto", "ru", "en"))
    ap.add_argument("--profile", default="", help="имя профиля из profiles.yaml (по умолчанию = жанр)")
    ap.add_argument("--slot-type", default="", help="тип слота для всего текста: id слота вида text словаря site")
    ap.add_argument("--role", default="", help="роль строки интерфейса: ux 07/06 §7.2 или body (жанр interface)")
    ap.add_argument("--component", default="", help="часть компонента: роль — из kb/common/components.yaml#text_roles "
                                                     "(Field.Error → error)")
    ap.add_argument("--format", default="", help="формат входа, если расширение не подходит: md|txt|html|yaml|texts")
    ap.add_argument("--objects", default="", help="глоссарий объектов object.md (по умолчанию — рядом с реестром)")
    ap.add_argument("--actions", default="", help="словарь действий action.md (по умолчанию — рядом с реестром)")
    ap.add_argument("--voice", default="", help="профиль голоса voice.yaml: словарь «не говорим», написания, обращение")
    ap.add_argument("--customer-words", default="", help="voc.yaml или meaning.yaml: слова клиента (customer_words)")
    ap.add_argument("--json", action="store_true", help="вывод JSON")
    ap.add_argument("--md", action="store_true", help="вывод Markdown")
    ap.add_argument("--facts", default="", help="файл фактов facts.yaml: имена мест (entities вида place) — вне правила о "
                                                "слове на «-ая,»; у copy deck — его facts_ref")
    maint = ap.add_argument_group("обслуживание базы (в маршруте этапов проекта не участвует)")
    maint.add_argument("--metrics-only", action="store_true", help="только метрики — замеры корпуса для порогов жанров")
    ap.add_argument("--units", action="store_true", help="добавить в JSON разбор на блоки")
    ap.add_argument("--rules", action="append", default=[], help="доп. файл или папка YAML-правил")
    ap.add_argument("--profiles", default="", help="путь к profiles.yaml")
    ap.add_argument("--thresholds", default="", help="путь к thresholds.yaml (по умолчанию 03-corpus-measured/)")
    ap.add_argument("--vocab", default="", help="путь к словарю site (по умолчанию kb/site/02-site-types/vocabulary.yaml)")
    ap.add_argument("--final", action="store_true", help="финальная проверка: [PLACEHOLDER] — error")
    ap.add_argument("--all-variants", action="store_true", help="в copy deck — все живые варианты слота (без rejected)")
    ap.add_argument("--chosen-only", action="store_true", help="в copy deck — только выбранный вариант (так по умолчанию)")
    ap.add_argument("--morph", default="auto", choices=("auto", "on", "off"), help="морфология pymorphy3")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--version", action="store_true")
    a = ap.parse_args(argv)
    if a.version:
        print(f"copy_lint {VERSION}")
        return 0
    if a.selftest:
        return selftest()
    if not a.paths:
        ap.print_usage()
        return 1
    try:
        vocab = load_vocab(Path(a.vocab) if a.vocab else None)
        profiles = load_profiles(Path(a.profiles) if a.profiles else None)
        log: list = []
        rules = load_rules(a.rules, profiles, log)
        voice = load_voice(a.voice, a.customer_words) if (a.voice or a.customer_words) else None
        results = []
        for p in a.paths:
            doc = read_document(p, a.genre or "", vocab, a.all_variants, a.slot_type, a.format, a.role, a.component,
                                a.objects, a.actions)
            if a.facts:
                doc.places = place_patterns(a.facts)
            page_audit = doc.fmt in ("md", "txt", "html", "htm") and not (a.slot_type or a.role or a.component) \
                and (a.genre or "landing") not in ("interface", "meta")
            res = lint_document(doc, rules, profiles, a.genre or "", a.lang, a.profile,
                                Path(a.thresholds) if a.thresholds else None, a.morph, a.final, a.metrics_only,
                                a.units, log, page_audit=page_audit, voice=voice)
            results.append(res)
    except (OSError, ValueError, yaml.YAMLError, re.error) as exc:
        sys.stderr.write(f"copy_lint: {exc}\n")
        return 1
    payload = {"tool": "copy_lint", "version": VERSION, "date": DATE, "results": results}
    if a.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    elif a.md:
        print(render_md(results))
    else:
        print(render_text(results))
    return 2 if any(r["summary"]["error"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
