#!/usr/bin/env python3
"""Ожидаемый состав переноса содержимого базы в шаблон (фаза 3, агент A).

Применяет упорядоченные правила manifest-rules.yaml (в каждом наборе первое совпадение решает) к замороженной базе —
манифест _skill-build/freeze/manifest.tsv.gz (пути, байты, sha256) + классы inventory.py — и к журналу _skill-build/ на
диске. Базу, шаблон и журнал только читает. Пишет только expected-content.tsv (--out); с --scan — ещё scan-*.tsv рядом
с --out (базовые числа проверок переноса).

  python3 rules_eval.py                           # expected-content.tsv + итоги по базам и purpose в stdout
  python3 rules_eval.py --scan                    # + scan-*.tsv: ссылки, идентификаторы, поля, передача B, открытые…
  python3 rules_eval.py --derive-blender-sources  # «финальные исходники» дорожек 13–17 (источник списка правила bl-tracks)

Для migrate.py (импорт): load_rules, evaluate, new_places, dir_new_place, resolve_old, rewrite_token, file_links,
link_scan. Ссылки считаются тем же кодом, что в inventory.py (регэкспы и порядок разрешения: папка файла → корень
базы → корень app-design), плюс голые пути в md (SKILL-MAP §3) и позиции токенов для замены.
"""
import argparse
import csv
import gzip
import hashlib
import json
import os
import posixpath
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True                        # не оставлять __pycache__ в _skill-build/tools при импорте
HERE = Path(__file__).resolve().parent               # _skill-build/phase-3/migration
BUILD = HERE.parents[1]                               # _skill-build
sys.path.insert(0, str(BUILD / "tools"))
import inventory as inv                               # noqa: E402  классы, токены, регэкспы ссылок, build_index
from count_tokens import is_bundle, read_text         # noqa: E402

ROOT = inv.ROOT                                       # /home/mm/Документы/app-design
MANIFEST = BUILD / "freeze" / "manifest.tsv.gz"
INVENTORY_FILES = BUILD / "freeze" / "inventory" / "files.tsv"
RULES = HERE / "manifest-rules.yaml"
OUT = HERE / "expected-content.tsv"
BUILD_REL = "_skill-build"
FIELDS = ["source", "dest", "purpose", "why", "bytes", "tokens_est", "sha256", "kind", "rule", "class"]
TEXT_EXT = inv.PROSE | inv.DATA | inv.CODE
MACHINE_EXT = {".yaml", ".yml", ".json", ".jsonl", ".tsv", ".csv"}


# ---------------------------------------------------------------- правила

def _glob(p):
    """Glob → регэксп: ** — любое число сегментов, * и ? — внутри сегмента, {a,b} — варианты."""
    out, i = [], 0
    while i < len(p):
        if p.startswith("**/", i):
            out.append("(?:[^/]+/)*")
            i += 3
            continue
        if p.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        c = p[i]
        if c == "*":
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == "{":
            j = p.index("}", i)
            out.append("(?:" + "|".join(_glob(a) for a in p[i + 1:j].split(",")) + ")")
            i = j + 1
            continue
        else:
            out.append(re.escape(c))
        i += 1
    return "".join(out)


def literal_prefix(p):
    """Часть шаблона до первого подстановочного знака, обрезанная по последний «/» — база для {rest}."""
    m = re.search(r"[*?{\[]", p)
    head = p[:m.start()] if m else p
    return head[:head.rfind("/") + 1]


@dataclass
class Rule:
    id: str
    scope: str
    patterns: list
    action: str
    dest: str = ""
    purpose: str = ""
    why: str = ""
    classes: frozenset = None
    when: str = ""
    alias_of: str = ""
    open: dict = None
    note: str = ""
    dedupe: bool = False

    def match(self, rec):
        if self.when == "symlink" and not rec.symlink:
            return None
        if self.when != "symlink" and rec.symlink:
            return None
        if self.classes is not None and rec.cls not in self.classes:
            return None
        for raw, rx, prefix in self.patterns:
            if rx.match(rec.source):
                return prefix
        return None


@dataclass
class Rules:
    meta: dict
    content: list
    journal: list

    @property
    def skill(self):
        return self.meta["roots"]["skill"]

    @property
    def journal_root(self):
        return self.meta["roots"]["journal"]

    @property
    def bases(self):
        return self.meta["bases"]


def load_rules(path=RULES):
    import yaml
    data = yaml.safe_load(Path(path).read_text())
    sets = {}
    seen = set()
    for scope in ("rules", "journal"):
        rules = []
        for item in data.get(scope) or []:
            rid = item["id"]
            if rid in seen:
                raise SystemExit(f"правило {rid}: id повторяется")
            seen.add(rid)
            pats = item["match"] if isinstance(item["match"], list) else [item["match"]]
            classes = item.get("class")
            rules.append(Rule(
                id=rid, scope="content" if scope == "rules" else "journal",
                patterns=[(p, re.compile("^" + _glob(p) + "$"), literal_prefix(p)) for p in pats],
                action=item["action"], dest=item.get("dest", ""), purpose=item.get("purpose", ""),
                why=str(item.get("why", "")), classes=frozenset(classes) if classes else None,
                when=item.get("when", ""), alias_of=item.get("alias_of", ""), open=item.get("open"),
                note=item.get("note", ""), dedupe=bool(item.get("dedupe"))))
            if item["action"] not in ("take", "skip", "handoff", "alias", "none"):
                raise SystemExit(f"правило {rid}: неизвестное действие {item['action']}")
            if (item.get("why") == "open") != bool(item.get("open")):
                raise SystemExit(f"правило {rid}: why: open и блок open идут вместе")
        sets[scope] = rules
    return Rules(meta=data, content=sets["rules"], journal=sets["journal"])


# ---------------------------------------------------------------- файлы

@dataclass
class Rec:
    source: str            # путь от корня app-design
    research: str          # папка базы (…-research) или ""
    path: str              # путь внутри базы (или внутри _skill-build)
    bytes: int
    sha256: str
    symlink: bool = False
    cls: str = ""

    @property
    def abs(self):
        return ROOT / self.source

    @property
    def ext(self):
        return os.path.splitext(self.path)[1].lower()


def classify(research, rel_path):
    """Класс файла базы — тем же кодом и с тем же чтением текста, что inventory.walk."""
    rel = Path(rel_path)
    ext = rel.suffix.lower()
    is_tool = rel.parts[0] == "99-raw" and len(rel.parts) > 2 and rel.parts[1] == "tools"
    text = None
    if (ext in TEXT_EXT or ext == "") and (rel.parts[0] not in inv.SERVICE or is_tool):
        text = read_text(ROOT / research / rel)
    return inv.classify(research, rel, text)


def kind_by_ext(ext, cls=""):
    if cls in inv.KIND:
        return inv.KIND[cls]
    if ext in inv.PROSE:
        return "prose"
    if ext in inv.DATA:
        return "data"
    if ext in inv.CODE:
        return "code"
    return None


def load_base(bases, manifest=MANIFEST):
    recs = []
    with gzip.open(manifest, "rt", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row["research"] not in bases:
                continue
            link = row["sha256"].startswith("symlink:")
            rec = Rec(source=f"{row['research']}/{row['path']}", research=row["research"], path=row["path"],
                      bytes=int(row["bytes"]), sha256=row["sha256"], symlink=link)
            rec.cls = "symlink" if link else classify(rec.research, rec.path)
            recs.append(rec)
    return recs


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_build(pruned):
    """Файлы _skill-build/ на диске (живой журнал). Временные папки сборки .staging* не обходим — только считаем."""
    recs = []
    top = ROOT / BUILD_REL
    for dirpath, dirnames, filenames in os.walk(top):
        keep = []
        for d in sorted(dirnames):
            full = Path(dirpath) / d
            rel = full.relative_to(top).as_posix()
            if re.fullmatch(r"phase-3/migration/\.staging[^/]*", rel) or full.is_symlink():
                pruned.append(rel + "/")
                continue
            keep.append(d)
        dirnames[:] = keep
        for f in sorted(filenames):
            full = Path(dirpath) / f
            rel = full.relative_to(top).as_posix()
            if full.is_symlink():
                recs.append(Rec(source=f"{BUILD_REL}/{rel}", research="", path=rel, bytes=0,
                                sha256="symlink:" + os.readlink(full), symlink=True, cls="symlink"))
                continue
            recs.append(Rec(source=f"{BUILD_REL}/{rel}", research="", path=rel, bytes=full.stat().st_size,
                            sha256="", cls=kind_by_ext(full.suffix.lower()) or "binary"))
    return recs


# ---------------------------------------------------------------- применение правил

@dataclass
class Entry:
    source: str
    dest: str
    purpose: str
    why: str
    bytes: int
    tokens: int
    sha256: str
    kind: str              # copy | alias | handoff | skip | none
    rule: str
    cls: str
    scope: str
    research: str = ""
    open: bool = False

    @property
    def base(self):
        return self.research[:-len("-research")] if self.research else ""


def expand(rule, rules, rec, prefix):
    tpl = rule.dest or ("{skill}/kb/{base}/{path}" if rule.scope == "content" else "{journal}/{rest}")
    rest = rec.source[len(prefix):] if prefix and rec.source.startswith(prefix) else rec.path
    return tpl.format(skill=rules.skill, journal=rules.journal_root, base=rules.bases.get(rec.research, ""),
                      path=rec.path, rest=rest, name=posixpath.basename(rec.path))


def est_tokens(rec, purpose):
    if purpose in ("asset-min", "calibration"):
        return 0
    kind = kind_by_ext(rec.ext, rec.cls)
    if kind is None:
        return 0
    text = read_text(rec.abs)
    return round(inv.tokens(text, kind)) if text is not None else 0


def decide(rules_list, rec):
    for rule in rules_list:
        prefix = rule.match(rec)
        if prefix is not None:
            return rule, prefix
    return None, None


def evaluate(rules, with_tokens=True, verbose=False):
    """Все решения: список Entry по базам и журналу. Ошибки правил (нет совпадения, коллизии, псевдонимы) — SystemExit."""
    bases = rules.bases
    base_recs = load_base(bases)
    pruned = []
    build_recs = load_build(pruned)
    entries, errors = [], []
    by_source = {}
    for rec in base_recs + build_recs:
        for scope, rlist in (("content", rules.content), ("journal", rules.journal)):
            if scope == "journal" and not rec.source.startswith(BUILD_REL + "/"):
                continue
            rule, prefix = decide(rlist, rec)
            if rule is None:
                if scope == "content":
                    errors.append(f"нет правила: {rec.source}")
                continue
            kind = {"take": "copy", "skip": "skip", "handoff": "handoff", "alias": "alias", "none": "none"}[rule.action]
            dest = expand(rule, rules, rec, prefix) if rule.action == "take" else ""
            purpose = rule.purpose or ("kb" if rule.action == "take" and scope == "content" else
                                       "journal" if rule.action == "take" else "")
            e = Entry(source=rec.source, dest=dest, purpose=purpose, why=rule.why, bytes=rec.bytes, tokens=0,
                      sha256=rec.sha256, kind=kind, rule=rule.id, cls=rec.cls, scope=scope, research=rec.research,
                      open=bool(rule.open))
            if kind == "alias":
                e.dest = rule.alias_of          # временно: источник-канон; ниже — его место
                e.purpose = "alias"
            entries.append(e)
            if kind in ("copy", "alias") and scope == "content":
                by_source[rec.source] = e
    # sha256 журнала и калибровки — с диска; токены — по тексту
    rec_by_source = {r.source: r for r in base_recs + build_recs}
    for e in entries:
        rec = rec_by_source[e.source]
        if e.kind in ("copy", "alias") and not e.sha256:
            e.sha256 = sha256_file(rec.abs)
        if with_tokens and (e.kind == "copy" or e.open):
            e.tokens = est_tokens(rec, e.purpose)
    # dedupe: копия из правила с dedupe, побайтно равная взятому файлу другого правила, → псевдоним канона
    dedupe_rules = {r.id for r in rules.content if r.dedupe}
    canon_by_sha = {}
    for e in sorted(entries, key=lambda x: x.source):
        if e.scope == "content" and e.kind == "copy" and e.rule not in dedupe_rules and e.sha256:
            canon_by_sha.setdefault(e.sha256, e.source)
    for e in entries:
        if e.scope == "content" and e.kind == "copy" and e.rule in dedupe_rules and e.sha256 in canon_by_sha:
            e.kind, e.dest, e.tokens, e.purpose = "alias", canon_by_sha[e.sha256], 0, "alias"
            e.why += "; дубль побайтно (dedupe)"
            by_source[e.source] = e
    # псевдонимы: канон взят и побайтно равен
    for e in entries:
        if e.kind != "alias":
            continue
        canon = by_source.get(e.dest)
        if canon is None or canon.kind != "copy":
            errors.append(f"псевдоним {e.source}: канон {e.dest} не взят")
            continue
        if canon.sha256 != e.sha256:
            errors.append(f"псевдоним {e.source}: sha256 не равен канону {e.dest}")
        e.dest = canon.dest
    # коллизии мест назначения
    dests = Counter(e.dest for e in entries if e.kind == "copy")
    for d, n in dests.items():
        if n > 1:
            errors.append(f"коллизия места: {d} ×{n}")
    if errors:
        raise SystemExit("ошибки правил:\n  " + "\n  ".join(errors[:50]))
    if verbose and pruned:
        print("не обходились (временные папки, симлинки):", ", ".join(pruned), file=sys.stderr)
    return entries


def new_places(entries):
    """Источник → новое место (от корня шаблона) для переписывания путей: содержимое главнее журнала."""
    places = {}
    for e in entries:
        if e.kind in ("copy", "alias") and e.scope == "journal":
            places.setdefault(e.source, e.dest)
    for e in entries:
        if e.kind in ("copy", "alias") and e.scope == "content":
            places[e.source] = e.dest
    return places


def dir_new_place(src_dir, places, prefix_index, skill, bases, journal_root):
    """Новое место каталога. Каталог базы → kb/<база>/<тот же путь>, если туда легла хоть одна его часть с тем же
    относительным путём; иначе — общий префикс, если все взятые файлы каталога уехали вместе с сохранением структуры
    и под тем же именем каталога (lucide-ref → scripts/ai-media/data/lucide-ref); _skill-build → журнал. Иначе None."""
    if src_dir == BUILD_REL:
        return journal_root
    items = prefix_index.get(src_dir)
    if not items:
        return None
    research, _, rel_dir = src_dir.partition("/")
    if research in bases:
        kb_dir = f"{skill}/kb/{bases[research]}" + (f"/{rel_dir}" if rel_dir else "")
        if any(dst == kb_dir + src[len(src_dir):] for src, dst in items):
            return kb_dir
    cands = {dst[:len(dst) - len(src) + len(src_dir)] if dst.endswith(src[len(src_dir):]) else None
             for src, dst in items}
    if len(cands) == 1:
        cand = cands.pop()
        if cand and posixpath.basename(cand) == posixpath.basename(src_dir):
            return cand
    return None


def new_layout_exists(places):
    """Проверка существования пути в новой раскладке по местам назначения (файлы и их каталоги)."""
    files = set(places.values())
    dirs = set()
    for d in files:
        while "/" in d:
            d = d.rsplit("/", 1)[0]
            if d in dirs:
                break
            dirs.add(d)
    return lambda p: p in files or p in dirs


def build_prefix_index(places):
    idx = defaultdict(list)
    for src, dst in places.items():
        parts = src.split("/")
        for i in range(1, len(parts)):
            idx["/".join(parts[:i])].append((src, dst))
    return idx


# ---------------------------------------------------------------- ссылки

def resolve_old(raw, research_dir, file_dir):
    """Как inventory.resolve_path, но ещё и какой корень разрешил: file | base | root | abs."""
    target = raw.split("#")[0].split("?")[0].rstrip(".,;:)")
    if not target:
        return None, None, target
    if target.startswith("/"):
        path = Path(target)
        return (path if _exists(path) else "missing"), "abs", target
    for kind, base in (("file", file_dir), ("base", research_dir), ("root", ROOT)):
        cand = Path(os.path.normpath(base / target))
        if _exists(cand):
            return cand, kind, target
    return "missing", None, target


def _exists(path):
    try:
        return path.exists()
    except OSError:                                   # слишком длинное имя и т. п. — не путь
        return False


def _mask(line, spans):
    chars = list(line)
    for a, b in spans:
        for i in range(a, b):
            chars[i] = " "
    return "".join(chars)


def file_links(rec_source, research, text, index):
    """Токены путей файла с позициями: (line, start, end, kind, raw). md — как inventory.extract_links + голые пути;
    остальное — как inventory.extract_paths (PATHLIKE по строке без URL)."""
    is_md = rec_source.endswith(".md")
    for line_no, line in enumerate(text.splitlines(), 1):
        if is_md:
            taken = []
            for m in inv.MD_LINK.finditer(line):
                taken.append(m.span())
                raw = m.group(1)
                if not raw.startswith(("http:", "https:", "mailto:", "#", "data:")):
                    yield line_no, m.start(1), m.end(1), "md", raw
            for m in inv.BACKTICK.finditer(line):
                taken.append(m.span())
                raw = m.group(1)
                if inv.looks_like_path(raw):
                    yield line_no, m.start(1), m.end(1), "backtick", raw
            spans = []
            for m in inv.SHORT_CROSS.finditer(line):
                spans.append(m.span())
                yield line_no, m.start(), m.end(), "short-cross", m.group(0)
            for m in inv.SHORT.finditer(line):
                if any(a <= m.start() < b for a, b in spans):
                    continue
                yield line_no, m.start(), m.end(), "short", m.group(0)
            masked = _mask(line, taken + [m.span() for m in inv.URL.finditer(line)])
            for m in inv.PATHLIKE.finditer(masked):
                if not inv.PLACEHOLDER.search(m.group(1)):
                    yield line_no, m.start(1), m.end(1), "bare", m.group(1)
        else:
            masked = _mask(line, [m.span() for m in inv.URL.finditer(line)])
            for m in inv.PATHLIKE.finditer(masked):
                if not inv.PLACEHOLDER.search(m.group(1)):
                    yield line_no, m.start(1), m.end(1), "path", m.group(1)


def short_target(index, research, kind, raw):
    if kind == "short-cross":
        m = inv.SHORT_CROSS.match(raw)
        other = inv.PREFIX[m.group(1)]
        return inv.short_target(index.get(other), m.group(2), m.group(3))
    m = inv.SHORT.search(raw)
    return inv.short_target(index.get(research), m.group(1), m.group(2))


BASE_SEG = re.compile(r"(?<![\w.-])(ux|ui|site|text|creative|ai-media|blender|claude-design)-research(?=/|$)")


def new_resolve(path_part, file_new, skill, base_short, exists):
    """Разрешение пути в новой раскладке (для check_links шаблона): папка файла → kb/<база> → kb → корень скилла →
    корень шаблона. Возвращает путь от корня шаблона или None."""
    if not path_part or path_part.startswith("/"):
        return None
    kb = f"{skill}/kb"
    roots = [posixpath.dirname(file_new)]
    if base_short and file_new.startswith(f"{kb}/{base_short}/"):
        roots.append(f"{kb}/{base_short}")
    roots += [kb, skill, ""]
    for root in roots:
        cand = posixpath.normpath(posixpath.join(root, path_part) if root else path_part)
        if not cand.startswith("..") and exists(cand):
            return cand
    return None


def rewrite_token(raw, base_kind, target_new, file_new, skill, base_short, exists):
    """Новый токен по правилу «разрешить → сопоставить» (SKILL-MAP §3) с минимальной правкой. Сначала — только смена
    сегментов x-research → x; если так токен в новой раскладке ведёт к новому месту цели, берём его. Иначе путь
    пересчитывается к новому месту цели от корня того же рода (папка файла → папка нового файла; корень базы →
    kb/<база>; корень app-design → kb, корень скилла или шаблона). Якорь, запрос и хвостовая пунктуация
    сохраняются. Возвращает (новый токен | None, если не меняется; ok — новый токен разрешается в цель)."""
    m = re.match(r"^([^#?]*?)([.,;:)]*)((?:[#?].*)?)$", raw)
    path_part, punct, suffix = m.group(1), m.group(2), m.group(3)
    if not path_part:
        return None, False
    target = target_new.rstrip("/")
    renamed = BASE_SEG.sub(r"\1", path_part)
    if new_resolve(renamed, file_new, skill, base_short, exists) == target:
        return (None if renamed == path_part else renamed + punct + suffix), True
    kb = f"{skill}/kb"
    if base_kind == "base" and base_short and file_new.startswith(f"{kb}/{base_short}/"):
        start = f"{kb}/{base_short}"
    elif base_kind == "root":
        start = kb if target.startswith(kb + "/") else skill if target.startswith(skill + "/") else ""
    else:
        start = posixpath.dirname(file_new)
    new = posixpath.relpath(target, start) if start else target
    if new_resolve(new, file_new, skill, base_short, exists) != target:
        new = posixpath.relpath(target, posixpath.dirname(file_new))   # затенение другим корнем — от папки файла
    if path_part.endswith("/") and not new.endswith("/"):
        new += "/"
    if path_part.startswith("./") and not new.startswith("."):
        new = "./" + new
    ok = new_resolve(new, file_new, skill, base_short, exists) == target
    return (None if new == path_part else new + punct + suffix), ok


def link_scan(entries, rules, collect_examples=40):
    """Базовые числа ссылок из переносимого (содержимое: md, машинные и прочие текстовые файлы, эталонный код kb)."""
    places = new_places(entries)
    pidx = build_prefix_index(places)
    exists = new_layout_exists(places)
    handoff = {e.source for e in entries if e.kind == "handoff"}
    content = [e for e in entries if e.scope == "content" and e.kind == "copy" and e.research]
    researches = sorted({e.research for e in content})
    index = {r: inv.build_index(ROOT / r) for r in researches}
    skill = rules.skill
    stats = defaultdict(Counter)
    examples = defaultdict(list)
    tokens_out = []
    for e in content:
        kind_src = kind_by_ext(os.path.splitext(e.source)[1].lower(), e.cls)
        if kind_src is None or e.purpose in ("asset-min",):
            continue
        text = read_text(ROOT / e.source)
        if text is None:
            continue
        src_kind = "md" if e.source.endswith(".md") else ("code" if kind_src == "code" else "data")
        file_dir = (ROOT / e.source).parent
        research_dir = ROOT / e.research
        base_short = rules.bases.get(e.research, "")
        for line_no, a, b, kind, raw in file_links(e.source, e.research, text, index):
            key = (e.base, src_kind)
            if kind in ("short", "short-cross"):
                tgt = short_target(index, e.research, kind, raw)
                if not isinstance(tgt, Path):
                    cat = "short-unresolved"
                else:
                    rel = tgt.relative_to(ROOT).as_posix()
                    cat = "short-ok" if rel in places and places[rel].endswith(rel.split("/", 1)[1]) else "short-to-untransferred"
                stats[key][cat] += 1
                continue
            resolved, base_kind, target = resolve_old(raw, research_dir, file_dir)
            if resolved is None:
                continue
            if resolved == "missing":
                cat, new_tok = "missing", None
            else:
                try:
                    rel = resolved.relative_to(ROOT).as_posix()
                except ValueError:
                    rel = None
                if rel is None:
                    cat, new_tok = "outside", None
                elif resolved.is_dir():
                    nd = dir_new_place(rel, places, pidx, skill, rules.bases, rules.journal_root)
                    if nd is None:
                        cat, new_tok = ("dir-to-handoff" if any(s.startswith(rel + "/") for s in handoff)
                                        else "dir-to-untransferred"), None
                    else:
                        cat = "dir-to-transferred"
                        new_tok, ok = rewrite_token(raw, base_kind, nd, e.dest, skill, base_short, exists)
                elif rel in places:
                    cat = "to-transferred"
                    new_tok, ok = rewrite_token(raw, base_kind, places[rel], e.dest, skill, base_short, exists)
                elif rel in handoff:
                    cat, new_tok = "to-handoff", None
                else:
                    cat, new_tok = "to-untransferred", None
            stats[key][cat] += 1
            if src_kind != "code" and cat in ("to-transferred", "dir-to-transferred"):
                stats[key]["rewrite" if new_tok else "unchanged"] += 1
                if not ok:
                    stats[key]["not-resolving-after"] += 1
                if new_tok:
                    tokens_out.append((e.source, line_no, a, b, kind, raw, new_tok))
            if src_kind == "code" and cat in ("to-transferred", "dir-to-transferred") and new_tok:
                stats[key]["code-would-break"] += 1
            ex_key = (e.base, cat)
            if len(examples[ex_key]) < collect_examples and cat not in ("to-transferred", "dir-to-transferred"):
                examples[ex_key].append((e.source, line_no, kind, raw))
    return stats, examples, tokens_out


# ---------------------------------------------------------------- «финальные исходники» дорожек blender (Р76 п. 16)

TRACK_CODE = {".py", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".sh", ".html", ".htm", ".css", ".glsl", ".frag", ".vert"}
TRACK_SKIP_SEG = {"out", "dist", "dbg", "logs", "chunks", "node_modules", "__pycache__", "renders", "shots", "blend", "tex"}
TRACK_DIR_VER = re.compile(r"-ref$|-v\d|_v\d")
TRACK_VER = re.compile(r"^(?P<stem>.*?)(?:[_-]v(?P<n>\d+)(?:[a-z]\d*)?(?:_final|_hero|i\d_hero)?|_orig|_j04_orig|_z2)$")
TRACK_DBG = re.compile(r"^(dbg|debug|diag|mem_|scan_|test_)|probe|debug")
TRACK_SH_KEEP = re.compile(r"^(build|pack|run_gates[^/]*)\.sh$")


def derive_blender_sources(recs):
    """Исходный код дорожек Z, CD, KB, SD, VD без выходов, бандлов, отладки и запускалок итераций; из семейства
    версий — файл без версии, иначе старшая версия. Детерминированно по манифесту."""
    fam = defaultdict(list)
    for rec in recs:
        m = re.match(r"blender-research/99-raw/experiments/(Z|CD|KB|SD|VD)/(.*)$", rec.source)
        if not m or rec.symlink:
            continue
        rest = m.group(2)
        parts = rest.split("/")
        name = parts[-1]
        stem, ext = os.path.splitext(name)
        if ext.lower() not in TRACK_CODE or set(parts[:-1]) & TRACK_SKIP_SEG:
            continue
        if any(TRACK_DIR_VER.search(p) for p in parts[:-1]) or name.endswith((".bundle.js", ".out.js", ".min.js")):
            continue
        if ext == ".sh" and not TRACK_SH_KEEP.match(name):
            continue
        text = read_text(rec.abs)
        if text is None or is_bundle(Path(rest), text) or TRACK_DBG.search(stem):
            continue
        mv = TRACK_VER.match(stem)
        fam_stem = mv.group("stem") if mv else stem
        rank = int(mv.group("n")) if mv and mv.group("n") else (-1 if mv else 10 ** 6)
        fam[(m.group(1), posixpath.dirname(rest), fam_stem, ext)].append((rank, rec.source))
    return sorted(max(v)[1] for v in fam.values())


# ---------------------------------------------------------------- сканы

IDENT = re.compile(r"(ux|ui|site|text|creative|ai-media|blender|claude-design|kimi)-research")
IDENT_TOKEN = re.compile(r"[\w.:/@$-]*(?:ux|ui|site|text|creative|ai-media|blender|claude-design|kimi)-research[\w.:/@$-]*")
SECRETS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("sk-key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("aws", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("google", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("bearer", re.compile(r"Bearer\s+[A-Za-z0-9_\-.=]{24,}")),
    ("assign", re.compile(r"(?i)\b(api[_-]?key|secret|token|password|authorization)\b[\"']?\s*[:=]\s*[\"']?"
                          r"(?=[A-Za-z0-9_\-]*\d)(?=[A-Za-z0-9_\-]*[A-Za-z])[A-Za-z0-9_\-]{24,}")),
]
INSTR = {"CLAUDE.md", "AGENTS.md", "SKILL.md", "CLAUDE.local.md", "GEMINI.md", ".mcp.json"}


def ident_class(line, a, b, path_spans):
    """Класс вхождения «<база>-research»: внутри токена пути (разрешимого или нет) или идентификатор/проза."""
    for s, t, resolvable in path_spans:
        if s <= a and b <= t:
            return "path-resolved" if resolvable else "path-unresolved"
    tok = next((m.group(0) for m in IDENT_TOKEN.finditer(line) if m.start() <= a < m.end()), line[a:b])
    if "urn:" in tok:
        return "urn"
    if "://" in tok:
        return "url"
    if re.search(r"[\w-]\.(?:ux|ui|site|text|creative|ai-media|blender|claude-design|kimi)-research\.", tok) or \
            re.match(r"(?:org|com|ru|app)\.", tok):
        return "namespace"
    if re.search(r"[\"']?\$(?:id|schema|ref)[\"']?\s*:", line):
        return "schema-id"
    if re.match(r"^\s*-?\s*[\"']?[\w.-]*" + re.escape(line[a:b]) + r"[\w.-]*[\"']?\s*:(\s|$)", line):
        return "key"
    if "/" in tok:
        return "path-like-other"
    return "prose"


def norm_ident(tok):
    tok = re.sub(r"\d+", "N", tok)
    return tok[:80]


def scan_identifiers(entries, rules):
    """Имена баз с -research в переносимом тексте: как путь (переписывается) или как идентификатор (не трогаем)."""
    content = [e for e in entries if e.scope == "content" and e.kind == "copy" and e.research]
    index = {r: inv.build_index(ROOT / r) for r in sorted({e.research for e in content})}
    counts = defaultdict(Counter)
    samples = defaultdict(Counter)
    conflicts = []
    for e in content:
        if kind_by_ext(os.path.splitext(e.source)[1].lower(), e.cls) is None or e.purpose == "asset-min":
            continue
        text = read_text(ROOT / e.source)
        if text is None or "-research" not in text:
            continue
        file_dir = (ROOT / e.source).parent
        per_line = defaultdict(list)
        for line_no, a, b, kind, raw in file_links(e.source, e.research, text, index):
            if kind in ("short", "short-cross"):
                continue
            resolved, _, _ = resolve_old(raw, ROOT / e.research, file_dir)
            per_line[line_no].append((a, b, isinstance(resolved, Path)))
        for line_no, line in enumerate(text.splitlines(), 1):
            for m in IDENT.finditer(line):
                cls = ident_class(line, m.start(), m.end(), per_line.get(line_no, []))
                counts[e.base][cls] += 1
                tok_m = next((t for t in IDENT_TOKEN.finditer(line) if t.start() <= m.start() < t.end()), None)
                tok = tok_m.group(0) if tok_m else m.group(0)
                if cls not in ("path-resolved", "path-unresolved", "prose", "path-like-other"):
                    samples[cls][norm_ident(tok)] += 1
                if cls == "path-resolved" and re.search(r"urn:|\borg\.|\$id|\$schema", tok):
                    conflicts.append((e.source, line_no, tok))
    return counts, samples, conflicts


def walk_values(obj, key="(root)"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_values(v, str(k))
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_values(v, key if key.endswith("[]") else key + "[]")
    elif isinstance(obj, str):
        yield key, obj


def machine_values(path, text):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".yaml", ".yml"):
        import yaml
        for doc in yaml.safe_load_all(text):
            yield from walk_values(doc)
    elif ext == ".json":
        yield from walk_values(json.loads(text))
    elif ext == ".jsonl":
        for line in text.splitlines():
            if line.strip():
                yield from walk_values(json.loads(line))
    elif ext in (".tsv", ".csv"):
        lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
        reader = csv.reader(lines, delimiter="\t" if ext == ".tsv" else ",")
        header = next(reader, [])
        for row in reader:
            for i, v in enumerate(row):
                yield (header[i] if i < len(header) else f"col{i}"), v


def scan_fields(entries):
    """Поля машинных файлов (YAML, JSON, TSV, CSV), значения которых разрешаются в файлы."""
    places = new_places(entries)
    stats = defaultdict(Counter)
    example = {}
    errors = []
    for e in entries:
        if e.scope != "content" or e.kind != "copy" or not e.research:
            continue
        ext = os.path.splitext(e.source)[1].lower()
        if ext not in MACHINE_EXT:
            continue
        text = read_text(ROOT / e.source)
        if text is None:
            continue
        file_dir = (ROOT / e.source).parent
        try:
            values = list(machine_values(e.source, text))
        except Exception as exc:  # noqa: BLE001 — разбор чужих файлов: ошибка — в отчёт, не падение
            errors.append((e.source, type(exc).__name__, str(exc).splitlines()[0][:120]))
            continue
        for fld, val in values:
            key = (e.base, ext.lstrip("."), fld)
            st = stats[key]
            st["values"] += 1
            v = val.strip()
            if not v or len(v) > 400 or "\n" in v:
                continue
            resolved, base_kind, _ = resolve_old(v, ROOT / e.research, file_dir) if not v.startswith(("http", "urn:")) \
                else (None, None, None)
            pathlike = bool(inv.PATHLIKE.search(inv.URL.sub(" ", v)))
            if isinstance(resolved, Path):
                rel = resolved.relative_to(ROOT).as_posix() if str(resolved).startswith(str(ROOT)) else None
                if resolved.is_dir():
                    st["whole-dir"] += 1
                else:
                    st["whole-file"] += 1
                    st["whole-file-transferred" if rel in places else "whole-file-untransferred"] += 1
                st["via-" + (base_kind or "?")] += 1
                if not pathlike:
                    st["whole-not-pathlike"] += 1
                example.setdefault(key, v)
            elif pathlike:
                st["pathlike-unresolved"] += 1
            for m in inv.PATHLIKE.finditer(inv.URL.sub(" ", v)):
                if m.group(1) != v:
                    r2, _, _ = resolve_old(m.group(1), ROOT / e.research, file_dir)
                    st["embedded-resolved" if isinstance(r2, Path) else "embedded-unresolved"] += 1
                    example.setdefault(key, v)
    return stats, example, errors


def check_inventory_classes(entries):
    """Сверка классов с files.tsv свежего инвентаря (построчные записи, без групп служебного): число расхождений."""
    mine = {e.source: e.cls for e in entries if e.scope == "content" and e.research}
    total = diff = 0
    examples = []
    with open(INVENTORY_FILES, newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row["path"].endswith("/…"):
                continue
            src = f"{row['research']}/{row['path']}"
            if src not in mine:
                continue
            total += 1
            if mine[src] != row["class"]:
                diff += 1
                if len(examples) < 5:
                    examples.append(f"{src}: {row['class']} → {mine[src]}")
    return total, diff, examples


def scan_secrets(entries):
    hits = []
    for e in entries:
        if e.kind != "copy":
            continue
        if kind_by_ext(os.path.splitext(e.source)[1].lower(), e.cls) is None or e.purpose == "asset-min":
            continue
        text = read_text(ROOT / e.source)
        if text is None:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for name, rx in SECRETS:
                for m in rx.finditer(line):
                    s = m.group(0)
                    hits.append((e.source, line_no, name, s[:6] + "…" + f"({len(s)})"))
    return hits


def check_calibration(entries, rules):
    """Пути rubric и file в assets/calibration/index.yaml → взятые файлы."""
    import yaml
    dests = {e.dest for e in entries if e.kind == "copy"}
    src = ROOT / BUILD_REL / "phase-3/calibration/index.yaml"
    data = yaml.safe_load(src.read_text())
    ok = miss = 0
    missing = []
    for fr in data.get("frames", []):
        for rub in fr.get("rubric") or []:
            path = rub.split()[0]
            if f"{rules.skill}/{path}" in dests:
                ok += 1
            else:
                miss += 1
                missing.append((fr.get("id"), path))
        f = fr.get("file")
        if f and f"{rules.skill}/assets/calibration/{f}" in dests:
            ok += 1
        elif f:
            miss += 1
            missing.append((fr.get("id"), f))
    return ok, miss, missing


GITIGNORE_NAME = [".env", ".env.local", "credentials*", "*.pem", "*.key", ".DS_Store", "Thumbs.db", "*.swp", "*~"]
GITIGNORE_DIR = [".idea", ".vscode", ".refs"]


def check_dests(entries, rules):
    import fnmatch
    out = defaultdict(list)
    skill = rules.skill + "/"
    for e in entries:
        if e.kind != "copy":
            continue
        name = posixpath.basename(e.dest)
        inner = e.dest[len(skill):] if e.dest.startswith(skill) else e.dest
        parts = inner.split("/")
        if any(fnmatch.fnmatch(name, p) for p in GITIGNORE_NAME) or set(parts[:-1]) & set(GITIGNORE_DIR) or \
                name == "settings.local.json":
            out["gitignore"].append(e.dest)
        if name in INSTR or ".claude" in parts[:-1] or ".git" in parts[:-1]:
            out["instruction"].append(e.dest)
        if re.search(r"(^|/)99-raw/cache/", e.source) or e.source.startswith("kimi-research/"):
            out["cache-or-kimi"].append(e.source)
        if e.cls == "junk" and e.purpose != "asset-min":
            out["junk"].append(e.source)
        if e.bytes > 5_000_000:
            out["large>5MB"].append(f"{e.source} ({e.bytes / 1e6:.1f} МБ)")
    return out


# ---------------------------------------------------------------- вывод

def write_tsv(path, header, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def write_expected(entries, path):
    rows = [[e.source, e.dest, e.purpose, e.why, e.bytes, e.tokens if e.kind == "copy" else 0, e.sha256, e.kind,
             e.rule, e.cls] for e in entries if e.kind in ("copy", "alias")]
    rows.sort(key=lambda r: (r[1], r[0]))
    write_tsv(path, FIELDS, rows)
    return len(rows)


def totals(entries):
    t = defaultdict(Counter)
    for e in entries:
        if e.kind != "copy":
            continue
        key = (e.base or ("journal" if e.purpose == "journal" else "_skill-build"), e.purpose)
        t[key]["files"] += 1
        t[key]["bytes"] += e.bytes
        t[key]["tokens"] += e.tokens
    return t


def print_totals(entries, rules):
    t = totals(entries)
    purposes = ["kb", "raw-norm", "build-input", "ref-code", "asset-min", "code-data", "calibration", "journal"]
    bases = list(rules.bases.values()) + ["_skill-build", "journal"]
    print("| часть | " + " | ".join(purposes) + " | итого |")
    print("|---|" + "---|" * (len(purposes) + 1))
    grand = Counter()
    col = defaultdict(Counter)
    for b in bases:
        row = Counter()
        cells = []
        for p in purposes:
            c = t.get((b, p))
            if c:
                row.update(c)
                col[p].update(c)
                cells.append(f"{c['files']} / {c['bytes'] / 1e6:.2f} / {c['tokens'] / 1e3:.0f}K")
            else:
                cells.append("")
        if row:
            grand.update(row)
            print(f"| {b} | " + " | ".join(cells) + f" | {row['files']} / {row['bytes'] / 1e6:.2f} / {row['tokens'] / 1e3:.0f}K |")
    print("| **итого** | " + " | ".join(
        f"{col[p]['files']} / {col[p]['bytes'] / 1e6:.2f} / {col[p]['tokens'] / 1e3:.0f}K" if col[p] else ""
        for p in purposes) + f" | {grand['files']} / {grand['bytes'] / 1e6:.2f} / {grand['tokens'] / 1e3:.0f}K |")
    kinds = Counter((e.scope, e.kind) for e in entries)
    print("решения:", ", ".join(f"{s}/{k} {n}" for (s, k), n in sorted(kinds.items())))


def rule_stats(entries, rules):
    st = defaultdict(Counter)
    for e in entries:
        c = st[e.rule]
        c["files"] += 1
        c["bytes"] += e.bytes
        c["tokens"] += e.tokens
    rows = []
    for r in rules.content + rules.journal:
        c = st.get(r.id, Counter())
        rows.append([r.id, r.scope, r.action, r.purpose, r.why, c["files"], c["bytes"], c["tokens"],
                     (r.open or {}).get("recommend", "")])
    return rows


def run_scan(entries, rules, outdir):
    outdir = Path(outdir)
    # правила: сколько файлов, байт, токенов попало под каждое
    write_tsv(outdir / "scan-rules.tsv", ["rule", "scope", "action", "purpose", "why", "files", "bytes",
                                          "tokens_est", "recommend"], rule_stats(entries, rules))
    # передача агенту B
    hand = sorted([e.source, e.rule, e.why, e.bytes, e.cls, e.sha256] for e in entries if e.kind == "handoff")
    write_tsv(outdir / "scan-handoff.tsv", ["source", "rule", "why", "bytes", "class", "sha256"], hand)
    # открытые пункты: цена
    op = sorted([e.rule, e.source, e.kind, e.bytes, e.tokens] for e in entries if e.open)
    write_tsv(outdir / "scan-open.tsv", ["rule", "source", "now", "bytes", "tokens_est"], op)
    # ссылки
    stats, examples, tokens_out = link_scan(entries, rules)
    cats = ["to-transferred", "dir-to-transferred", "to-handoff", "dir-to-handoff", "to-untransferred",
            "dir-to-untransferred", "missing", "outside", "short-ok", "short-to-untransferred", "short-unresolved",
            "rewrite", "unchanged", "not-resolving-after", "code-would-break"]
    rows = []
    for (base, src_kind), c in sorted(stats.items()):
        rows.append([base, src_kind] + [c[k] for k in cats])
    tot = Counter()
    for c in stats.values():
        tot.update(c)
    rows.append(["ВСЕГО", "*"] + [tot[k] for k in cats])
    write_tsv(outdir / "scan-links.tsv", ["base", "source_kind"] + cats, rows)
    ex_rows = []
    for (base, cat), items in sorted(examples.items()):
        for src, line, kind, raw in items[:15]:
            ex_rows.append([base, cat, f"{src}:{line}", kind, raw])
    write_tsv(outdir / "scan-links-examples.tsv", ["base", "category", "where", "kind", "raw"], ex_rows)
    rw = Counter()
    for src, line, a, b, kind, raw, new in tokens_out:
        rw[(src.split("/")[0][:-len("-research")], kind)] += 1
    write_tsv(outdir / "scan-rewrites.tsv", ["source", "line", "start", "end", "kind", "raw", "new"],
              sorted(tokens_out))
    # идентификаторы
    counts, samples, conflicts = scan_identifiers(entries, rules)
    icats = ["path-resolved", "path-unresolved", "path-like-other", "namespace", "urn", "url", "schema-id", "key",
             "prose"]
    irows = [[b] + [c[k] for k in icats] for b, c in sorted(counts.items())]
    itot = Counter()
    for c in counts.values():
        itot.update(c)
    irows.append(["ВСЕГО"] + [itot[k] for k in icats])
    irows.append([])
    irows.append(["шаблон", "класс", "вхождений"])
    for cls, cnt in sorted(samples.items()):
        for tok, n in cnt.most_common(25):
            irows.append([tok, cls, n])
    irows.append([])
    irows.append(["конфликты: идентификатор внутри разрешимого пути", len(conflicts)])
    irows += [[f"{s}:{ln}", t] for s, ln, t in conflicts[:30]]
    write_tsv(outdir / "scan-identifiers.tsv", ["base"] + icats, irows)
    # поля машинных файлов
    fstats, fex, ferr = scan_fields(entries)
    fcols = ["values", "whole-file", "whole-file-transferred", "whole-file-untransferred", "whole-dir", "via-file",
             "via-base", "via-root", "via-abs", "whole-not-pathlike", "pathlike-unresolved", "embedded-resolved",
             "embedded-unresolved"]
    frows = []
    for key, c in sorted(fstats.items(), key=lambda kv: (-(kv[1]["whole-file"] + kv[1]["whole-dir"]
                                                            + kv[1]["embedded-resolved"]), kv[0])):
        if c["whole-file"] + c["whole-dir"] + c["embedded-resolved"] + c["pathlike-unresolved"] == 0:
            continue
        frows.append(list(key) + [c[k] for k in fcols] + [fex.get(key, "")[:120]])
    frows += [["ошибка разбора", s, t, m] for s, t, m in ferr]
    write_tsv(outdir / "scan-fields.tsv", ["base", "type", "field"] + fcols + ["example"], frows)
    # секреты, калибровка, места назначения
    sec = scan_secrets(entries)
    write_tsv(outdir / "scan-secrets.tsv", ["source", "line", "pattern", "masked"], sec)
    cal_ok, cal_miss, cal_missing = check_calibration(entries, rules)
    inv_total, inv_diff, inv_ex = check_inventory_classes(entries)
    dchk = check_dests(entries, rules)
    return {"links": tot, "rewrite_by_kind": {f"{b}/{k}": n for (b, k), n in sorted(rw.items())}, "idents": itot, "conflicts": len(conflicts),
            "fields_files": len({(k[0], k[1]) for k in fstats}), "field_errors": len(ferr), "secrets": len(sec),
            "calibration": (cal_ok, cal_miss, cal_missing[:10]), "inventory_classes": (inv_total, inv_diff, inv_ex), "dests": {k: len(v) for k, v in dchk.items()},
            "dest_examples": {k: v[:5] for k, v in dchk.items()}, "handoff": len(hand), "open": len(op)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rules", type=Path, default=RULES)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--scan", action="store_true", help="ещё scan-*.tsv рядом с --out")
    ap.add_argument("--no-tokens", action="store_true", help="без оценки токенов (быстрее)")
    ap.add_argument("--derive-blender-sources", action="store_true",
                    help="напечатать список финальных исходников дорожек blender и выйти")
    args = ap.parse_args()
    if args.derive_blender_sources:
        recs = [r for r in load_base({"blender-research": "blender"})]
        for src in derive_blender_sources(recs):
            print(src)
        return
    rules = load_rules(args.rules)
    entries = evaluate(rules, with_tokens=not args.no_tokens, verbose=True)
    n = write_expected(entries, args.out)
    print(f"{args.out.name}: {n} строк (copy + alias)")
    print_totals(entries, rules)
    if args.scan:
        res = run_scan(entries, rules, args.out.parent)
        print(json.dumps(res, ensure_ascii=False, indent=1, default=lambda o: dict(o) if isinstance(o, Counter)
                         else str(o)))


if __name__ == "__main__":
    main()
