#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""copy_lint.py — линтер маркетинговых текстов RU/EN по жанрам.

text-research · волна 1 · агент C · 2026-09-24. Спецификация: 06-anti-slop/02-linter-spec-and-profiles.md.

Что делает. Находит маркеры нейрослопа и ошибки жанра по правилам 06-anti-slop/lexicon/*.yaml (включая словари,
унаследованные из ../ux-research/07-ux-writing/06-banned-words-and-patterns.md через конвертер ux_dict_to_yaml.py),
профилю жанра 06-anti-slop/profiles.yaml и порогам 03-corpus-measured/thresholds.yaml (пока их нет — стартовые
значения профиля с provisional: true). Считает метрики на 100 слов: маркеры, тире, «не X, а Y», вопросы, тройки,
восклицания, конкретика; ритм предложений и абзацев; ищет следы сверхкоррекции («текст хуманайзера»).

Вход: .txt, .md, .html/.htm, copy deck .yaml/.yml (формат copy-deck v0 из PLAN.md или список {slot_type, text});
«-» — stdin. slot_type — из 99-raw/notes/temp-vocabulary-v0.yaml (временный словарь оркестратора).

Запуск:
  python3 99-raw/tools/copy_lint.py page.md --genre landing            # отчёт для человека
  python3 99-raw/tools/copy_lint.py page.md --genre article --json     # JSON: находки и метрики
  python3 99-raw/tools/copy_lint.py deck.yaml --md                     # Markdown-отчёт по copy deck
  python3 99-raw/tools/copy_lint.py text.txt --metrics-only --json     # только метрики (для замеров D)
  python3 99-raw/tools/copy_lint.py --selftest                         # самопроверка кода и всех словарей

Коды выхода: 0 — нет находок уровня error; 2 — есть error (ворота не пройдены); 1 — ошибка запуска или входа.
Зависимости: Python 3.10+, PyYAML. Морфология pymorphy3 — опционально (запуск интерпретатором 99-raw/tools/venv-C);
без неё работают регулярные приближения с уровнем не выше warning.

Как модуль (для copy_metrics.py агента D):
  from copy_lint import lint_text, text_metrics
  report = lint_text("Текст…", genre="landing", lang="auto")   # dict как в JSON-выводе (один результат)
  m = text_metrics("Текст…", lang="ru")                         # dict метрик без правил профиля
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import math
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

VERSION = "0.9.3"
DATE = "2026-09-24"

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("text")  # перенос: kb/text
LEXICON_DIR = ROOT / "06-anti-slop" / "lexicon"
PROFILES_PATH = ROOT / "06-anti-slop" / "profiles.yaml"
VOCAB_PATH = ROOT / "99-raw" / "notes" / "temp-vocabulary-v0.yaml"
THRESHOLDS_PATH = ROOT / "03-corpus-measured" / "thresholds.yaml"

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover
    sys.stderr.write("copy_lint: нужен PyYAML (python3 -c 'import yaml'); в venv-C он есть.\n")
    sys.exit(1)

LEVELS = ("error", "warning", "info", "off")
LEVEL_RANK = {"off": 0, "info": 1, "warning": 2, "error": 3}
GROUPS = ("ART", "CNT", "LEX", "SYN", "PUN", "STR", "TON", "MKT", "UX", "EXT")
GENRES = ("landing", "site-page", "article", "meta", "geo", "email-form")
STYLE_GROUPS = {"LEX", "SYN", "TON", "MKT", "STR", "PUN"}  # в цитатах и коде не срабатывают

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


def overlaps(a: tuple[int, int], spans: list[tuple[int, int]]) -> bool:
    return any(a[0] < e and s < a[1] for s, e in spans)


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
    origin: str = ""
    note: str = ""
    regex: re.Pattern | None = None
    unless_re: re.Pattern | None = None

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


RULE_FIELDS = set(Rule.__dataclass_fields__) - {"regex", "unless_re", "origin"}


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
    by_id = {r.id: r for r in rules}
    for ov in overrides:
        target = ov.get("target", "")
        hits = [r for rid, r in by_id.items() if fnmatch.fnmatch(rid, target)]
        for r in hits:
            for k, v in (ov.get("set") or {}).items():
                if k in RULE_FIELDS:
                    setattr(r, k, v)
            if ov.get("note"):
                r.note = (r.note + " " if r.note else "") + f"[{origin}] {ov['note']}"
            r.compile()


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
        # Правка оркестратора 2026-09-24 (0.9.3): ошибка во внешнем файле правил (G, H, …) пропускает только этот файл
        # и выводится заметкой; ошибка в собственных словарях 06-anti-slop/lexicon/ по-прежнему останавливает линтер.
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
def load_vocab(path: Path | None = None) -> dict:
    p = path or VOCAB_PATH
    if not p.exists():
        return {"slot_types": {}, "page_types": {}}
    data = load_yaml(p) or {}
    slots = {s["id"]: s for s in data.get("slot_types", []) or []}
    pages = {s["id"]: s for s in data.get("page_types", []) or []}
    return {"slot_types": slots, "page_types": pages, "path": str(p)}


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
    """Профиль = defaults ⊕ profiles[name] ⊕ thresholds.yaml (D) для этого жанра ⊕ analyzers_by_lang[lang] (D2, если
    язык известен). Возвращает (профиль, источник порогов)."""
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
            # 0.9.3 (оркестратор, 2026-09-24): пороги по языку D2 поверх общих — русское тире норма, английское примета
            # ИИ; объединённый порог давал warning тире 23 % лидеров RU против 8 % по своему (03-corpus-measured/03 §3).
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


@dataclass
class Document:
    path: str
    fmt: str
    units: list
    source_text: str = ""
    genre_hint: str = ""
    notes: list = field(default_factory=list)


def role_for(slot_type: str, vocab: dict, fallback: str = "marketing") -> str:
    st = vocab["slot_types"].get(slot_type)
    if st is not None:
        return st.get("ux_role") or ("meta" if slot_type.startswith(("meta-", "og-")) else fallback)
    return fallback


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


def parse_copy_deck(data, vocab: dict, path: str, chosen_only: bool) -> tuple[list[Unit], str]:
    units: list[Unit] = []
    genre_hint = ""

    def parse_allow(raw) -> list:
        out = []
        for a in (raw if isinstance(raw, list) else ([raw] if raw else [])):
            if isinstance(a, dict) and a.get("rule"):
                out.append((str(a["rule"]), str(a.get("reason", ""))))
            elif isinstance(a, str):
                out.append((a, ""))
        return out

    def add_slot(slot: dict, page_id="", section_id="", genre=""):
        st = slot.get("slot_type") or "body"
        facts = slot.get("fact_ids")
        facts = list(facts) if isinstance(facts, list) else (None if facts is None else [facts])
        allow = parse_allow(slot.get("lint_allow"))
        variants = slot.get("variants")
        if isinstance(variants, list) and variants:
            chosen = slot.get("chosen")
            for v in variants:
                if chosen_only and chosen and v.get("id") != chosen:
                    continue
                txt = v.get("text") or ""
                if not str(txt).strip():
                    continue
                units.append(Unit(str(txt), st, role_for(st, vocab), page_id, section_id, slot.get("slot_id", ""),
                                  str(v.get("id", "")), facts if facts is not None else [], path=path, genre=genre,
                                  allow=allow))
        elif slot.get("text"):
            units.append(Unit(str(slot["text"]), st, role_for(st, vocab), page_id, section_id, slot.get("slot_id", ""),
                              "", facts if facts is not None else [], path=path, genre=genre, allow=allow))

    root = data.get("copy_deck", data) if isinstance(data, dict) else data
    if isinstance(root, dict) and "pages" in root:
        for page in root.get("pages") or []:
            pt = page.get("page_type", "")
            genre = (vocab["page_types"].get(pt) or {}).get("genre", "") or page.get("genre", "")
            genre_hint = genre_hint or genre
            meta = page.get("meta") or {}
            for k, st in (("title", "meta-title"), ("description", "meta-description"), ("og_title", "og-title"),
                          ("og_description", "og-description")):
                if meta.get(k):
                    units.append(Unit(str(meta[k]), st, role_for(st, vocab, "meta"), page.get("page_id", ""), "meta",
                                      st, "", [], path=path, genre="meta"))
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


def read_document(path: str, genre: str, vocab: dict, chosen_only: bool = False, slot_type: str = "",
                  fmt: str = "") -> Document:
    if path == "-":
        text = sys.stdin.read()
        ext = fmt or "md"
    else:
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        ext = fmt or p.suffix.lower().lstrip(".")
    text = text.lstrip("\ufeff") if text.startswith("\ufeff") else text
    doc = Document(path, ext, [], text)
    if ext in ("yaml", "yml"):
        data = yaml.safe_load(text)
        units, ghint = parse_copy_deck(data, vocab, path, chosen_only)
        doc.units, doc.genre_hint = units, ghint
        doc.source_text = ""
    elif ext in ("html", "htm"):
        doc.units = parse_html(text, genre or "landing", vocab, path)
        doc.source_text = ""
    else:
        doc.units = parse_markdown(text, genre or "landing", vocab, path)
        doc.fmt = "md" if ext in ("md", "markdown") else "txt"
    if slot_type:
        for u in doc.units:
            u.slot_type = slot_type
            u.role = role_for(slot_type, vocab)
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

    def as_dict(self) -> dict:
        d = {"id": self.id, "marker_id": self.marker_id, "level": self.level, "group": self.group,
             "message": self.message, "fragment": self.fragment, "context": self.context,
             "position": {"unit": self.unit, "start": self.start, "end": self.end, "line": self.line,
                          "col": self.col},
             "replacement": self.replacement, "example": self.example, "source": self.source,
             "evidence": self.evidence, "slot": self.slot, "counts_as_marker": self.count_as_marker}
        if self.note:
            d["note"] = self.note
        return d


def effective_level(rule: Rule, genre: str, unit: Unit, profile: dict) -> str:
    lvl = rule.levels.get(genre, rule.level) if rule.levels else rule.level
    if rule.slot_levels and unit.slot_type in rule.slot_levels:
        lvl = rule.slot_levels[unit.slot_type]
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
    if rule.kind in ("analyzer", "manual"):
        return False
    if rule.lang not in ("any", lang):
        return False
    if rule.genres and genre not in rule.genres:
        return False
    if rule.appliesTo and unit.role not in rule.appliesTo:
        return False
    if rule.excludes and unit.role in rule.excludes:
        return False
    # отзыв и цитата клиента (роль user-content) стилистически не правятся: только артефакты (ART) и данные (CNT)
    if unit.role == "user-content" and rule.group in STYLE_GROUPS and "user-content" not in (rule.appliesTo or []):
        return False
    if rule.slot_types and not any(fnmatch.fnmatch(unit.slot_type, s) for s in rule.slot_types):
        return False
    if rule.exclude_slot_types and any(fnmatch.fnmatch(unit.slot_type, s) for s in rule.exclude_slot_types):
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
    for k in ("page_id", "section_id", "slot_id", "variant"):
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


def run_rules(doc: Document, rules: list[Rule], genre: str, lang: str, profile: dict,
              skip_ids: set | None = None) -> list[Finding]:
    out: list[Finding] = []
    doc_hits: dict = {}  # правила со scope: doc — копим находки по документу, решаем по min_count в конце
    for ui, u in enumerate(doc.units):
        ulang = u.lang or lang
        ugenre = u.genre or genre
        masks = masked_spans(u.text)
        for r in rules:
            if skip_ids and r.id in skip_ids:
                continue
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
                if r.mask_quotes and overlaps((m.start(), m.end()), masks):
                    continue
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
                f = Finding(r.id, r.marker_id, lvl, r.group, r.message, fragment=m.group(0)[:120],
                            context=context_of(u.text, m.start(), m.end()), unit=ui, start=m.start(), end=m.end(),
                            replacement=r.replacement, example=r.examples or {}, source=r.source,
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
                raise SystemExit("copy_lint: --morph on, но pymorphy3 не найден (запусти интерпретатором venv-C)")
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
                        if not overlaps((t[1], se), masks):
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
                    if run >= 3 and not overlaps((start, end), masks):
                        emit("ru-syn-genitive-chain", ui, u, start, end)
                    run, start = 0, None
            if run >= 3 and not overlaps((start, end), masks):
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
                    if not overlaps((t[1], t[2]), masks):
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


def run_analyzers(doc: Document, rules: list[Rule], genre: str, lang: str, profile: dict, morph,
                  marker_findings: list[Finding]) -> tuple[list[Finding], dict]:
    an = profile.get("analyzers") or {}
    rb = {r.id: r for r in rules}
    out: list[Finding] = []
    prose_types = set(profile.get("prose_slot_types") or ["body", "article-paragraph", "geo-answer", "email-body"])
    # подписи в 1–3 слова не проза, даже если слот размечен как body (опыт C/02: вкладки и статусы веб-приложения)
    prose_units = [(i, u) for i, u in enumerate(doc.units) if u.slot_type in prose_types and (u.genre or genre) == genre
                   and len(words_of(u.text)) >= 4]
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
            faq_q = sum(1 for u in doc.units if u.slot_type in ("faq-q", "email-subject")
                        and u.text.rstrip().endswith("?"))
            val = round(100.0 * max(0, m_all["questions"] - faq_q) / nw_all, 3)
        thr = cfg.get("warn_per_100w")
        cnt = {"not_x_but_y": m_all["not_x_but_y"], "questions": m_all["questions"], "triads": m_all["triads"],
               "exclamations": m_all["exclamations"]}[key]
        if thr is not None and val >= float(thr) and cnt >= int(cfg.get("min_count", 2)):
            out.append(mk_analyzer_finding(rb.get(rid), rid, an_level(cfg, "info"), f"Частота {name} выше порога жанра.",
                                           extra=f"{val} на 100 слов (порог {thr}, provisional)."))

    # надзаголовки: не чаще чем у каждой третьей секции
    cfg = an.get("eyebrow_rate") or {}
    if cfg.get("enabled", True):
        eyebrows = [u for u in doc.units if u.slot_type in EYEBROW_SLOTS]
        heads = [u for u in doc.units if u.slot_type in ("headline", "section-title")]
        if eyebrows and heads:
            limit = math.ceil(len(heads) / 3)
            if len(eyebrows) > limit:
                out.append(mk_analyzer_finding(rb.get("an-eyebrow-rate"), "an-eyebrow-rate", an_level(cfg),
                                               "Надзаголовков больше, чем у каждой третьей секции.",
                                               extra=f"{len(eyebrows)} надзаголовков на {len(heads)} заголовков (лимит {limit})."))
        metrics["eyebrows"] = {"count": len(eyebrows), "headings": len(heads)}

    # все списки по три пункта
    cfg = an.get("lists_of_three") or {}
    if cfg.get("enabled", True):
        sizes, run = [], 0
        for u in doc.units:
            if u.slot_type == "list-item":
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

    # числа без факта: сигнал для claims_check.py (B2)
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
                                        extra="Сверить с facts.yaml: 99-raw/tools/claims_check.py (B2).")
                f.start, f.end = mh.start(), mh.end()
                f.context = context_of(u.text, mh.start(), mh.end())
                if u.src_offset is not None and doc.source_text:
                    f.line, f.col = line_col(doc.source_text, u.src_offset + mh.start())
                out.append(f)
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
                  metrics_only: bool = False, include_units: bool = False, log: list | None = None) -> dict:
    g = genre or doc.genre_hint or "landing"
    if g not in GENRES:
        raise SystemExit(f"copy_lint: неизвестный жанр {g}; допустимо: {', '.join(GENRES)}")
    prof_name = profile_name or g
    if lang in ("", "auto"):
        lang = detect_lang(" ".join(u.text for u in doc.units))
    profile, th_src = resolve_profile(profiles, prof_name, thresholds_path, lang)
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
    an_findings = [f for f in an_findings if not allowed(f)]
    findings = rule_findings + an_findings
    # порядок отчёта = порядок проверок (спецификация §7): артефакты → выдуманные данные → словари ux и внешние →
    # лексика и синтаксис → структура → анализаторы → сверхкоррекция
    order = {"ART": 0, "CNT": 1, "UX": 2, "EXT": 2, "LEX": 3, "SYN": 3, "PUN": 3, "MKT": 3, "TON": 3, "STR": 4}

    def check_order(f: Finding) -> int:
        if f.id == "an-overcorrection":
            return 6
        if f.id.startswith("an-") and f.group != "CNT":
            return 5
        return order.get(f.group, 5)
    findings.sort(key=lambda f: (check_order(f), -LEVEL_RANK.get(f.level, 0), f.unit, f.start))
    counts = {lv: sum(1 for f in findings if f.level == lv) for lv in ("error", "warning", "info")}
    res = {"input": {"path": doc.path, "format": doc.fmt, "units": len(doc.units), "lang": lang, "genre": g,
                     "profile": prof_name, "morphology": bool(morph)},
           "thresholds": th_src,
           "summary": {**counts, "verdict": verdict_of(findings, metrics), "severity": severity_of(findings),
                       "gate": "fail" if counts["error"] else "pass", "suppressed": len(suppressed)},
           "metrics": metrics}
    if not metrics_only:
        res["findings"] = [f.as_dict() for f in findings]
    if include_units:
        res["units"] = [{"index": i, **slot_info(u), "words": len(words_of(u.text)), "text": u.text[:200]}
                        for i, u in enumerate(doc.units)]
    missing = [n.split(": ", 1)[1] for n in (log or []) if n.startswith("внешний файл правил не найден")]
    notes = list(doc.notes) + [n for n in (log or []) if not n.startswith("внешний файл правил не найден")]
    if missing:
        notes.append("внешние правила (G, H — волна 2) пока не подключены: " + ", ".join(missing))
    if not genre and not doc.genre_hint:
        notes.append("жанр не задан (--genre): применён landing")
    if suppressed:
        notes.append("подавлено lint_allow: " + "; ".join(suppressed))
    if notes:
        res["notes"] = notes
    return res


def lint_text(text: str, genre: str = "landing", lang: str = "auto", slot_type: str = "", profile: str = "",
              fmt: str = "md", metrics_only: bool = False) -> dict:
    """API для других утилит: текст → результат линтера (dict как один элемент results в JSON)."""
    vocab = load_vocab()
    profiles = load_profiles()
    log: list = []
    rules = load_rules(profiles=profiles, log=log)
    doc = Document("<text>", fmt, [], text)
    if fmt in ("html", "htm"):
        doc.units, doc.source_text = parse_html(text, genre, vocab, "<text>"), ""
    else:
        doc.units = parse_markdown(text, genre, vocab, "<text>")
    if slot_type:
        for u in doc.units:
            u.slot_type, u.role = slot_type, role_for(slot_type, vocab)
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


def selftest() -> int:
    ok = True
    profiles = load_profiles()
    log: list = []
    try:
        rules = load_rules(profiles=profiles, log=log)
    except Exception as exc:
        print(f"FAIL загрузка словарей: {exc}")
        return 1
    vocab = load_vocab()
    ids = {r.id for r in rules}
    print(f"словари: {len(rules)} правил из {len({r.origin for r in rules})} файлов; словарь слотов: "
          f"{len(vocab['slot_types'])} типов")
    # 1. каждое правило с примерами: «плохо» срабатывает, «хорошо» — нет
    bad_fail, good_fail, checked = [], [], 0
    for r in rules:
        if r.kind in ("analyzer", "manual") or not r.examples or r.level == "off":
            continue
        bad, good = r.examples.get("bad"), r.examples.get("good")

        def hits_in(txt: str) -> int:
            n = 0
            for m in r.regex.finditer(txt):
                if r.mask_quotes and overlaps((m.start(), m.end()), masked_spans(txt)):
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
    if bad_fail:
        print("  не ловят свой плохой пример:", ", ".join(bad_fail[:40]))
        ok = False
    if good_fail:
        print("  ловят свой хороший пример:", ", ".join(good_fail[:40]))
        ok = False
    # 2. сценарии
    for text, genre, rid, expect in SELFTEST_CASES:
        if rid not in ids:
            print(f"FAIL сценарий: правила {rid} нет в словарях")
            ok = False
            continue
        res = lint_text(text, genre=genre)
        got = any(f["id"] == rid for f in res["findings"])
        if got != expect:
            ok = False
            print(f"FAIL {rid}: ожидалось {'срабатывание' if expect else 'тишина'} на «{text[:60]}»")
    # 3. анализаторы
    mono = " ".join(["Это длинное предложение содержит ровно двенадцать слов, и следующее будет таким же."] * 12)
    if not any(f["id"] == "an-rhythm-monotone" for f in lint_text(mono, genre="article")["findings"]):
        print("FAIL an-rhythm-monotone не сработал на монотонном тексте")
        ok = False
    rag = ("Мы открылись весной. Честно. Без пафоса. Кофе варим сами, зерно берём у знакомых обжарщиков.\n\n"
           "Утро. Очередь. Кто-то спешит на работу, кто-то нет. Короче, всем хватает.\n\n"
           "Десерты? Печём ночью. Сами. Вот так.\n\n"
           "Цены обычные. Ну правда обычные. Капучино двести двадцать, раф двести шестьдесят.\n\n"
           "Заходите. Или не заходите. Решать вам.")
    r = lint_text(rag, genre="article")
    if not any(f["id"] == "an-overcorrection" for f in r["findings"]):
        print("FAIL an-overcorrection не сработал на нарочито рваном тексте; сигналы:",
              r["metrics"].get("overcorrection_signals"))
        ok = False
    m = text_metrics("Москва — столица. Сроки — 3–5 дней. Мы работаем — и это главное — без выходных.", "ru")
    if m["dash_count"] != 4:
        print(f"FAIL dash_count: ожидалось 4 (без диапазона 3–5), получено {m['dash_count']}")
        ok = False
    if (m["dash_obligatory"], m["dash_punct"]) != (2, 2):
        print(f"FAIL классификация тире: ожидалось 2 обязательных и 2 пунктуационных, получено "
              f"{m['dash_obligatory']} и {m['dash_punct']}")
        ok = False
    m3 = text_metrics("Мастер ответил:\n— Приедем завтра к девяти.", "ru")
    if (m3["dash_obligatory"], m3["dash_punct"]) != (1, 0):
        print(f"FAIL тире прямой речи в начале строки: {m3['dash_obligatory']} и {m3['dash_punct']}")
        ok = False
    m2 = text_metrics("Смета и выезд замерщика — бесплатно. Отправляем в день обжарки — без месяцев на складе.", "ru")
    if (m2["dash_obligatory"], m2["dash_punct"]) != (1, 1):
        print(f"FAIL тире «поле — значение» / «пояснение после глагола»: {m2['dash_obligatory']} и {m2['dash_punct']}")
        ok = False
    # 4. copy deck
    deck = {"copy_deck": {"version": 0, "pages": [{"page_id": "home", "page_type": "landing-saas", "sections": [
        {"section_id": "hero", "slots": [
            {"slot_id": "h1", "slot_type": "headline", "variants": [{"id": "a", "text": "Более 10 000 клиентов"}],
             "chosen": "a", "fact_ids": []},
            {"slot_id": "cta", "slot_type": "cta-label", "variants": [{"id": "a", "text": "Начать →"}], "chosen": "a"}]}]}]}}
    units, gh = parse_copy_deck(deck, vocab, "<deck>", False)
    doc = Document("<deck>", "yaml", units, "", gh)
    res = lint_document(doc, rules, profiles, "", "auto", "", None)
    fid = {f["id"] for f in res["findings"]}
    if "an-number-without-fact" not in fid:
        print("FAIL copy deck: число без факта не отмечено")
        ok = False
    if not any(i.startswith("ux-") and "arrow" in i or i == "ru-pun-arrow-cta" for i in fid):
        print("FAIL copy deck: стрелка в подписи кнопки не отмечена; нашлось:", sorted(fid))
        ok = False
    # отзыв клиента: стиль не проверяется, артефакты — проверяются
    deck3 = {"slots": [{"slot_type": "testimonial-quote",
                        "text": "Команда профессионалов, всё сделали качественно. Надеюсь, это поможет!"}]}
    units3, gh3 = parse_copy_deck(deck3, vocab, "<deck3>", False)
    res3 = lint_document(Document("<deck3>", "yaml", units3, "", gh3), rules, profiles, "landing", "auto", "", None)
    groups3 = {f["group"] for f in res3["findings"]}
    if groups3 & STYLE_GROUPS or "ART" not in groups3:
        print("FAIL отзыв (user-content): ожидались только артефакты, нашлось:", sorted((f["id"], f["group"])
                                                                                        for f in res3["findings"]))
        ok = False
    # lint_allow: стилистическое правило подавляется с причиной, данные (CNT) — нет
    deck2 = {"slots": [{"slot_type": "headline", "text": "Не только кофе, но и десерты: 4,9 из 5 на Картах",
                        "lint_allow": [{"rule": "ru-syn-not-only-but-also", "reason": "слоган бренда из брифа"},
                                       {"rule": "an-number-without-fact", "reason": "попытка подавить данные"}],
                        "fact_ids": []}]}
    units2, gh2 = parse_copy_deck(deck2, vocab, "<deck2>", False)
    res2 = lint_document(Document("<deck2>", "yaml", units2, "", gh2), rules, profiles, "landing", "auto", "", None)
    fid2 = {f["id"] for f in res2["findings"]}
    if "ru-syn-not-only-but-also" in fid2 or res2["summary"].get("suppressed") != 1 or "an-number-without-fact" not in fid2:
        print("FAIL lint_allow: ожидалось подавить ru-syn-not-only-but-also и оставить an-number-without-fact;",
              sorted(fid2), res2["summary"])
        ok = False
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
    ap = _ArgParser(description="Линтер маркетинговых текстов RU/EN по жанрам (text-research).")
    ap.add_argument("paths", nargs="*", help="файлы .txt .md .html .yaml; «-» — stdin")
    ap.add_argument("--genre", choices=GENRES, help="жанр: landing, site-page, article, meta, geo, email-form")
    ap.add_argument("--lang", default="auto", choices=("auto", "ru", "en"))
    ap.add_argument("--profile", default="", help="имя профиля из profiles.yaml (по умолчанию = жанр)")
    ap.add_argument("--slot-type", default="", help="slot_type для всего текста (из временного словаря)")
    ap.add_argument("--format", default="", help="формат входа, если расширение не подходит: md|txt|html|yaml")
    ap.add_argument("--json", action="store_true", help="вывод JSON")
    ap.add_argument("--md", action="store_true", help="вывод Markdown")
    ap.add_argument("--metrics-only", action="store_true", help="только метрики (для замеров корпуса)")
    ap.add_argument("--units", action="store_true", help="добавить в JSON разбор на блоки")
    ap.add_argument("--rules", action="append", default=[], help="доп. файл или папка YAML-правил (G, H и др.)")
    ap.add_argument("--profiles", default="", help="путь к profiles.yaml")
    ap.add_argument("--thresholds", default="", help="путь к thresholds.yaml (по умолчанию 03-corpus-measured/)")
    ap.add_argument("--vocab", default="", help="путь к словарю слотов")
    ap.add_argument("--final", action="store_true", help="финальная проверка: [PLACEHOLDER] — error")
    ap.add_argument("--chosen-only", action="store_true", help="в copy deck проверять только выбранный вариант")
    ap.add_argument("--morph", default="auto", choices=("auto", "on", "off"), help="морфология pymorphy3")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--version", action="store_true")
    a = ap.parse_args(argv)
    if a.version:
        print(f"copy_lint {VERSION} ({DATE})")
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
        results = []
        for p in a.paths:
            doc = read_document(p, a.genre or "", vocab, a.chosen_only, a.slot_type, a.format)
            res = lint_document(doc, rules, profiles, a.genre or "", a.lang, a.profile,
                                Path(a.thresholds) if a.thresholds else None, a.morph, a.final, a.metrics_only,
                                a.units, log)
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
