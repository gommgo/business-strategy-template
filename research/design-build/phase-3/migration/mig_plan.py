#!/usr/bin/env python3
"""План переноса (агент C): какое дерево ложится в шаблон и откуда каждый его файл. Модуль migrate.py.

Входы — только чтение: замороженная база (манифест `_skill-build/freeze/manifest.tsv.gz`), правила содержимого агента A
(`manifest-rules.yaml` через `rules_eval.py`), код агента B (`tools-map.tsv`, `patches/` через `apply_patches.py`), overlay
(`overlay/`), живой журнал `_skill-build/` и `.claude/rules/forward-only.md` шаблона из ветки main (`git show`).

Дерево — от корня шаблона: `.claude/skills/design-deep-dive/…` (kb, scripts, assets, навигатор), `research/design-build/…`
(журнал) и новая версия `.claude/rules/forward-only.md`. Порядок сборки:
  код по tools-map (строка tools-map главнее правила содержимого) → содержимое по правилам A (зона переписывания путей —
  SPEC §7.1) → overlay → журнал (без overlay, Р110, и без reports/ — выходов check и apply) → forward-only.md →
  kb/INDEX.md → path-map.tsv.
Каждый взятый файл базы сверяется с манифестом заморозки по sha256; расхождение — ошибка сборки.
"""
import csv
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent                 # _skill-build/phase-3/migration
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import rules_eval as RE                                # noqa: E402  агент A: правила, ссылки, разрешение путей
import apply_patches as AP                             # noqa: E402  агент B: механические правки кода

inv = RE.inv                                           # _skill-build/tools/inventory.py
APP = RE.ROOT                                          # корень app-design
BUILD_REL = RE.BUILD_REL                               # "_skill-build"
MIG_REL = f"{BUILD_REL}/phase-3/migration"
STAGING = HERE / ".staging"
REPORTS = HERE / "reports"
TOOLS_MAP = HERE / "tools-map.tsv"
EXPECTED = HERE / "expected-content.tsv"
SCAN_HANDOFF = HERE / "scan-handoff.tsv"
SCAN_REWRITES = HERE / "scan-rewrites.tsv"
SCAN_LINKS = HERE / "scan-links.tsv"
OVERLAY = HERE / "overlay"
SNIPPET = OVERLAY / "snippets" / "forward-only-exception.md"
FORWARD_ONLY = ".claude/rules/forward-only.md"
TEMPLATE_REF = "main"
# Выходы migrate.py внутри _skill-build/ — не вход сборки: иначе каждый check менял бы дерево, которое он проверяет.
JOURNAL_EXCLUDE = (f"{MIG_REL}/reports/",)
ZONE_KINDS = ("prose", "data")                         # SPEC §7.1 п. 1: md, txt и машинные файлы kb
TOKEN_RX = re.compile(r"^([^#?]*?)([.,;:)]*)((?:[#?].*)?)$")   # путь | хвостовая пунктуация | якорь — как в rewrite_token


class BuildError(Exception):
    pass


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def exec_mode(path):
    return 0o755 if os.stat(path).st_mode & 0o111 else 0o644


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if check and r.returncode != 0:
        raise BuildError(f"git {' '.join(args)} ({repo}): {r.stderr.decode('utf-8', 'replace').strip()}")
    return r


# ---------------------------------------------------------------- модель

@dataclass
class Item:
    dest: str                    # от корня шаблона
    source: str                  # от корня app-design; «-» — у сгенерированного
    kind: str                    # copy | rewritten | patched | generated | alias
    part: str                    # purpose содержимого | code | overlay | journal | generated | alias
    src_sha: str = ""            # sha256 источника (для alias — самого файла-дубля)
    data: bytes = None           # байты результата (у alias — нет)
    mode: int = 0o644
    replacements: int = 0        # замен: правки кода + переписанные токены путей
    origin: str = ""             # правило A, «tools-map», «overlay», «migrate.py»
    base: str = ""               # имя базы без -research
    cls: str = ""                # класс inventory.py (для содержимого)
    zone: dict = None            # зона переписывания: old_source, research, base_short, text, reps


@dataclass
class Rep:
    line: int
    start: int
    end: int
    kind: str
    raw: str
    new: str
    target: str                  # новое место цели (от корня шаблона)


def split_token(raw):
    """(путь, пунктуация, якорь) — та же разбивка, что в rules_eval.rewrite_token."""
    m = TOKEN_RX.match(raw)
    return m.group(1), m.group(2), m.group(3)


def apply_reps(text, reps):
    """Замены справа налево по строкам; окончания строк (\\n, \\r\\n и др.) — как в источнике. Пересечение — ошибка."""
    if not reps:
        return text
    keep = text.splitlines(keepends=True)
    bare = text.splitlines()
    by_line = defaultdict(list)
    for r in reps:
        by_line[r.line].append(r)
    for ln, rs in by_line.items():
        body, end = bare[ln - 1], keep[ln - 1][len(bare[ln - 1]):]
        rs = sorted(rs, key=lambda r: r.start)
        for x, y in zip(rs, rs[1:]):
            if x.end > y.start:
                raise BuildError(f"пересекающиеся токены в строке {ln}: {x.raw!r} и {y.raw!r}")
        for r in reversed(rs):
            if body[r.start:r.end] != r.raw:
                raise BuildError(f"строка {ln}: на месте {r.start}–{r.end} не {r.raw!r}")
            body = body[:r.start] + r.new + body[r.end:]
        keep[ln - 1] = body + end
    return "".join(keep)


def merge_forward_only(cur, snippet):
    """Текст forward-only.md с абзацем-исключением. → (текст, 'present' | 'append'); чужая правка абзаца — BuildError."""
    body = snippet.strip("\n")
    if body in cur:
        return cur, "present"
    heading = next((ln for ln in body.splitlines() if ln.startswith("## ")), None)
    if heading and heading in cur:
        raise BuildError(f"в forward-only.md уже есть «{heading}», но абзац отличается от overlay/snippets — правили руками")
    return cur.rstrip("\n") + "\n\n" + body + "\n", "append"


def tree_fingerprint(root):
    """Отпечаток дерева: sha256 отсортированных строк «путь \\t x|- \\t sha256». → (hex, файлов, байт)."""
    root = Path(root)
    lines, total = [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for f in filenames:
            p = Path(dirpath) / f
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                lines.append(f"{rel}\tL\t{os.readlink(p)}")
                continue
            data = p.read_bytes()
            total += len(data)
            lines.append(f"{rel}\t{'x' if p.stat().st_mode & 0o111 else '-'}\t{sha256_bytes(data)}")
    lines.sort(key=lambda s: s.encode("utf-8"))
    return sha256_bytes("\n".join(lines).encode("utf-8")), len(lines), total


def items_fingerprint(items):
    lines = [f"{it.dest}\t{'x' if it.mode & 0o111 else '-'}\t{sha256_bytes(it.data)}" for it in items if it.data is not None]
    lines.sort(key=lambda s: s.encode("utf-8"))
    return sha256_bytes("\n".join(lines).encode("utf-8"))


# ---------------------------------------------------------------- план

class Plan:
    """Полный план дерева в памяти. Plan().items — файлы и псевдонимы; .write(dir) — записать; .path_map_rows — строки."""

    def __init__(self, template=None, template_ref=TEMPLATE_REF):
        self.rules = RE.load_rules()
        self.skill = self.rules.skill
        self.journal_root = self.rules.journal_root
        self.bases = self.rules.bases                       # папка базы → имя
        self.template = Path(template or self.rules.meta["roots"]["template"])
        self.template_ref = template_ref
        self.warnings = []
        self.info = {}
        try:
            self.entries = RE.evaluate(self.rules, with_tokens=False)
        except SystemExit as e:                             # rules_eval падает SystemExit при ошибке правил
            raise BuildError(f"rules_eval: {e}")
        self._index_entries()
        self._load_tools_map()
        self._places()
        self._plan_dests()
        self.generator_outputs = generator_outputs(self.skill)
        self.items = {}
        self.aliases = []
        self._build_code()
        self._build_content()
        self._build_overlay()
        self._build_journal()
        self._build_forward_only()
        self._build_index()
        self._build_path_map()

    # ------------------------------------------------ входы

    def _index_entries(self):
        e_all = self.entries
        self.content = [e for e in e_all if e.scope == "content" and e.kind in ("copy", "alias")]
        self.handoff = {e.source: e for e in e_all if e.scope == "content" and e.kind == "handoff"}
        self.base_rec = {e.source: e for e in e_all if e.scope == "content" and e.research}   # sha256 — из манифеста
        excluded = [e for e in e_all if e.scope == "journal" and e.kind == "copy" and e.source.startswith(JOURNAL_EXCLUDE)]
        self.journal_entries = [e for e in e_all if e.scope == "journal" and e.kind == "copy"
                                and not e.source.startswith(JOURNAL_EXCLUDE)]
        self.info["journal_excluded"] = sorted(e.source for e in excluded)
        self.content_by_source = {e.source: e for e in self.content}

    def _load_tools_map(self):
        rows = list(csv.DictReader(open(TOOLS_MAP, encoding="utf-8"), delimiter="\t"))
        errors = []
        self.tm = {}
        for r in rows:
            if r["source"] in self.tm:
                errors.append(f"tools-map: источник дважды — {r['source']}")
            self.tm[r["source"]] = r
        for r in rows:
            v, dest = r["verdict"], r["dest"]
            if v not in ("take", "adapt", "skip"):
                errors.append(f"tools-map: неизвестный verdict {v!r} у {r['source']}")
            if v in ("take", "adapt") and not dest.startswith(self.skill + "/"):
                errors.append(f"tools-map: {r['source']} — место вне скилла или пусто: {dest!r}")
            if r["canonical"].startswith("dup-of:") and dest:
                canon = self.tm.get(r["canonical"][len("dup-of:"):])
                if canon is None or canon["verdict"] not in ("take", "adapt") or canon["dest"] != dest:
                    errors.append(f"tools-map: псевдоним {r['source']} → {dest}, но канон не взят в это место")
        for src in sorted(self.handoff):
            if src not in self.tm:
                errors.append(f"код не учтён: {src} (правило handoff без строки tools-map)")
        patch_files = {p.resolve() for p in AP.iter_patches()}
        need = {AP.patch_file_for(r["dest"]).resolve() for r in rows if r["verdict"] == "adapt"}
        for p in sorted(patch_files - need):
            errors.append(f"правка без строки adapt: {p.relative_to(HERE)}")
        for p in sorted(need - patch_files):
            errors.append(f"строка adapt без файла правки: {p.relative_to(HERE)}")
        # строка tools-map на файл, который правила A берут в kb: место то же или пометка в notes (SPEC §2)
        self.tm_conflicts = []
        for src, r in sorted(self.tm.items()):
            e = self.content_by_source.get(src)
            if e is None or e.kind != "copy":
                continue
            if r["verdict"] in ("take", "adapt") and r["dest"] != e.dest:
                self.tm_conflicts.append(f"{src}: правило {e.rule} → {e.dest}, tools-map → {r['dest']}")
            elif r["verdict"] == "skip":
                self.tm_conflicts.append(f"{src}: правило {e.rule} берёт, tools-map — skip")
        if self.tm_conflicts:
            self.warnings += [f"tools-map главнее правила: {c}" for c in self.tm_conflicts]
        if errors:
            raise BuildError("tools-map / правки:\n  " + "\n  ".join(errors[:40]))
        self.tm_rows = rows

    def _places(self):
        """Источник → новое место: содержимое главнее журнала (new_places A), код — по dest tools-map (главнее всего)."""
        places = RE.new_places(self.entries)
        for src in list(places):
            if src.startswith(JOURNAL_EXCLUDE):
                del places[src]
        for r in self.tm_rows:
            if r["dest"] and (r["verdict"] in ("take", "adapt") or r["canonical"].startswith("dup-of:")):
                places[r["source"]] = r["dest"]
        for src, r in self.tm.items():                     # tools-map skip на файл, который A брал, — места нет
            if r["verdict"] == "skip" and not r["dest"] and src in self.content_by_source:
                places.pop(src, None)
        self.code_dests = {r["dest"] for r in self.tm_rows if r["dest"] and self.content_by_source.get(r["source"]) is None}
        self.places = places
        self.pidx = RE.build_prefix_index(places)
        self.handoff_dirs = set()
        for src in self.handoff:
            parts = src.split("/")
            for i in range(1, len(parts)):
                self.handoff_dirs.add("/".join(parts[:i]))

    def _plan_dests(self):
        """Все места файлов дерева заранее — для разрешения путей в новой раскладке при переписывании."""
        dests = {}
        clash = []

        def claim(dest, who):
            if dest in dests and dests[dest] != who:
                clash.append(f"{dest}: {dests[dest]} и {who}")
            dests.setdefault(dest, who)

        for r in self.tm_rows:
            if r["verdict"] in ("take", "adapt"):
                claim(r["dest"], r["source"])
        for e in self.content:
            if e.kind == "copy":
                r = self.tm.get(e.source)
                if r is not None:                          # строка tools-map главнее: её место (или skip — ничего)
                    continue
                claim(e.dest, e.source)
        self.overlay_files = []
        for p in sorted(OVERLAY.rglob("*")):
            rel = p.relative_to(OVERLAY)
            if not p.is_file() or rel.parts[0] == "snippets":
                continue
            if "__pycache__" in rel.parts or p.suffix in (".pyc", ".pyo"):
                self.warnings.append(f"overlay: пропущен мусор {rel.as_posix()}")
                continue
            if p.is_symlink():
                raise BuildError(f"overlay: симлинк {rel.as_posix()}")
            self.overlay_files.append(p)
        for p in self.overlay_files:
            dest = p.relative_to(OVERLAY).as_posix()
            if dest in dests:
                self.warnings.append(f"overlay поверх: {dest} (было {dests[dest]})")
                dests[dest] = f"overlay:{dest}"
            else:
                claim(dest, f"overlay:{dest}")
        for e in self.journal_entries:
            claim(e.dest, e.source)
        self.path_map_dest = f"{self.journal_root}/phase-3/migration/path-map.tsv"
        self.index_dest = f"{self.skill}/kb/INDEX.md"
        for d, who in ((self.path_map_dest, "path-map"), (self.index_dest, "INDEX"), (FORWARD_ONLY, "forward-only")):
            claim(d, who)
        if clash:
            raise BuildError("коллизии мест назначения:\n  " + "\n  ".join(clash[:40]))
        self.planned = set(dests)
        dirs = set()
        for d in self.planned:
            while "/" in d:
                d = d.rsplit("/", 1)[0]
                if d in dirs:
                    break
                dirs.add(d)
        self.planned_dirs = dirs
        self.exists = lambda p: p in self.planned or p in self.planned_dirs

    # ------------------------------------------------ чтение источника со сверкой

    def read_source(self, source, expect_sha=None, what=""):
        data = (APP / source).read_bytes()
        sha = sha256_bytes(data)
        if expect_sha and sha != expect_sha:
            raise BuildError(f"источник изменился с заморозки ({what}): {source} — sha256 {sha[:12]}… ≠ {expect_sha[:12]}…")
        return data, sha

    def frozen_sha(self, source):
        e = self.base_rec.get(source)
        if e is None:
            return None
        if e.sha256.startswith("symlink:"):
            raise BuildError(f"источник — симлинк: {source}")
        return e.sha256

    def add(self, item):
        if item.dest in self.items:
            raise BuildError(f"место занято дважды: {item.dest} ({self.items[item.dest].source} и {item.source})")
        self.items[item.dest] = item

    # ------------------------------------------------ код (tools-map, агент B)

    def _build_code(self):
        self.code_stats = Counter()
        for r in self.tm_rows:
            src, dest, v = r["source"], r["dest"], r["verdict"]
            if v == "skip":
                if r["canonical"].startswith("dup-of:") and dest:
                    sha = self.frozen_sha(src) or sha256_bytes((APP / src).read_bytes())
                    self.aliases.append(Item(dest=dest, source=src, kind="alias", part="alias", src_sha=sha,
                                             origin="tools-map", base=self._base_of(src)))
                    self.code_stats["alias"] += 1
                continue
            frozen = self.frozen_sha(src)
            data, sha = self.read_source(src, frozen, "код")
            if hashlib.md5(data).hexdigest() != r["md5"]:
                raise BuildError(f"tools-map устарел: md5 {src} не совпадает с колонкой md5")
            mode = exec_mode(APP / src)
            reps_n = 0
            if v == "adapt":
                patch = AP.load_patch(AP.patch_file_for(dest))
                if patch["source"] != src or patch["dest"] != dest:
                    raise BuildError(f"правка {AP.patch_file_for(dest).name}: source/dest не совпадают со строкой tools-map")
                if frozen and patch["source_sha256"] != frozen:
                    raise BuildError(f"правка {dest}: source_sha256 не равен sha256 заморозки")
                try:
                    out = AP.apply_patch(patch)
                    _, counts = AP.apply_text(data.decode("utf-8"), patch)
                except AP.PatchError as e:
                    raise BuildError(f"apply_patches: {e}")
                reps_n = sum(counts)
                kind = "patched"
            else:
                out, kind = data, "copy"
            item = Item(dest=dest, source=src, kind=kind, part="code", src_sha=sha, data=out, mode=mode,
                        replacements=reps_n, origin="tools-map", base=self._base_of(src), cls=r["kind"])
            ce = self.content_by_source.get(src)
            if ce is not None and ce.kind == "copy":
                item.part = ce.purpose                     # эталонный код kb (kind=ref) — часть содержимого
                item.cls = ce.cls
            if r["kind"] == "data" and dest.endswith(".md") and src.endswith("/99-raw/tools/README.md"):
                # README утилит базы: после правки — переписывание путей тем же правилом, что md kb (Р112), от старого места
                research = src.split("/", 1)[0]
                self._zone(item, out.decode("utf-8", "surrogateescape"), src, research, self.bases.get(research, ""))
            self.add(item)
            self.code_stats[kind] += 1

    def _base_of(self, source):
        research = source.split("/", 1)[0]
        return self.bases.get(research, "")

    # ------------------------------------------------ содержимое (правила A)

    def _in_zone(self, e):
        # assets/calibration/index.yaml SPEC §7.1 п. 1 относит к зоне, но §5 и заметка правила cal-index — «файл не меняется»:
        # утверждённый заказчиком файл (Р109) объявляет source.path путями от корня app-design (провенанс в паре с sha256
        # заморозки). Частное правило главнее общего: копия байт в байт; rubric и file проверяет check (калибровка).
        if not e.dest.startswith(self.skill + "/kb/") or e.purpose == "asset-min":
            return False
        return RE.kind_by_ext(os.path.splitext(e.source)[1].lower(), e.cls) in ZONE_KINDS

    def _build_content(self):
        self.content_stats = Counter()
        for e in sorted(self.content, key=lambda x: x.dest):
            if e.kind == "alias":
                self.aliases.append(Item(dest=e.dest, source=e.source, kind="alias", part="alias", src_sha=e.sha256,
                                         origin=e.rule, base=e.base))
                self.content_stats["alias"] += 1
                continue
            if e.source in self.tm:                         # строка tools-map главнее (эталонный код kb и т. п.)
                self.content_stats["by-tools-map"] += 1
                continue
            data, sha = self.read_source(e.source, e.sha256, "содержимое")
            item = Item(dest=e.dest, source=e.source, kind="copy", part=e.purpose, src_sha=sha, data=data,
                        mode=exec_mode(APP / e.source), origin=e.rule, base=e.base, cls=e.cls)
            if self._in_zone(e) and b"\x00" not in data[:8192]:
                self._zone(item, data.decode("utf-8", "surrogateescape"), e.source, e.research,
                           self.bases.get(e.research, ""))
            self.add(item)
            self.content_stats[item.kind] += 1

    # ------------------------------------------------ переписывание путей (SPEC §7.1)

    def classify(self, raw, research_dir, file_dir):
        """Токен в старой раскладке → (категория, base_kind, новое место цели | None)."""
        resolved, base_kind, _ = RE.resolve_old(raw, research_dir, file_dir)
        if resolved is None:
            return "empty", None, None
        if resolved == "missing":
            return "missing", None, None
        try:
            rel = resolved.relative_to(APP).as_posix()
        except ValueError:
            return "outside", None, None
        if resolved.is_dir():
            nd = RE.dir_new_place(rel, self.places, self.pidx, self.skill, self.bases, self.journal_root)
            if nd is not None:
                return "dir-to-transferred", base_kind, nd
            return ("dir-to-handoff" if rel in self.handoff_dirs else "dir-to-untransferred"), base_kind, None
        if rel in self.places:
            return "to-transferred", base_kind, self.places[rel]
        if rel in self.handoff:
            return "to-handoff", base_kind, None
        return "to-untransferred", base_kind, None

    def scan_tokens(self, text, old_source, research, file_new, base_short, exists=None):
        """Все токены путей файла: (line, start, end, kind, raw, cat, target_new, new_raw | None, ok)."""
        exists = exists or self.exists
        file_dir = APP / posixpath.dirname(old_source)
        research_dir = (APP / research) if research else file_dir
        out = []
        for line_no, a, b, kind, raw in RE.file_links(old_source, research, text, None):
            if kind in ("short", "short-cross"):
                out.append((line_no, a, b, kind, raw, "short", None, None, True))
                continue
            cat, base_kind, target_new = self.classify(raw, research_dir, file_dir)
            new_raw, ok = None, True
            if target_new is not None:
                new_raw, ok = RE.rewrite_token(raw, base_kind, target_new, file_new, self.skill, base_short, exists)
            out.append((line_no, a, b, kind, raw, cat, target_new, new_raw, ok))
        return out

    def _zone(self, item, text, old_source, research, base_short):
        toks = self.scan_tokens(text, old_source, research, item.dest, base_short)
        generator = self.generator_outputs.get(item.dest)
        reps, held = [], []
        for ln, a, b, kind, raw, cat, tgt, new, ok in toks:
            if new is None:
                continue
            if generator and tgt in self.code_dests:
                # производный файл генератора с --check: путь к коду генератор пишет в старой форме — держим её
                held.append({"line": ln, "start": a, "end": b, "raw": raw, "target": tgt, "generator": generator})
                continue
            reps.append(Rep(ln, a, b, kind, raw, new, tgt))
        broken = [(ln, raw) for ln, a, b, kind, raw, cat, tgt, new, ok in toks
                  if tgt is not None and not ok and not any(h["line"] == ln and h["start"] == a for h in held)]
        try:
            new_text = apply_reps(text, reps)
        except BuildError as e:
            raise BuildError(f"{old_source}: {e}")
        item.zone = {"old_source": old_source, "research": research, "base_short": base_short, "text": text,
                     "reps": reps, "broken": broken, "held": held, "tokens": len(toks)}
        if reps:
            item.data = new_text.encode("utf-8", "surrogateescape")
            item.replacements += len(reps)
            if item.kind == "copy":
                item.kind = "rewritten"

    # ------------------------------------------------ overlay, журнал, forward-only

    def _build_overlay(self):
        for p in self.overlay_files:
            dest = p.relative_to(OVERLAY).as_posix()
            data = p.read_bytes()
            src = f"{MIG_REL}/overlay/{dest}"
            if dest in self.items:                          # overlay поверх строки tools-map (предупреждение — в плане мест)
                del self.items[dest]
            self.add(Item(dest=dest, source=src, kind="copy", part="overlay", src_sha=sha256_bytes(data), data=data,
                          mode=exec_mode(p), origin="overlay"))

    def _build_journal(self):
        for e in self.journal_entries:
            data, sha = self.read_source(e.source, e.sha256, "журнал менялся во время сборки")
            self.add(Item(dest=e.dest, source=e.source, kind="copy", part="journal", src_sha=sha, data=data,
                          mode=exec_mode(APP / e.source), origin=e.rule))

    def template_file(self, path):
        return git(self.template, "show", f"{self.template_ref}:{path}").stdout

    def _build_forward_only(self):
        cur_b = self.template_file(FORWARD_ONLY)
        snippet = SNIPPET.read_text(encoding="utf-8")
        text, state = merge_forward_only(cur_b.decode("utf-8"), snippet)
        self.info["forward_only"] = state
        self.forward_only_source_sha = sha256_bytes(cur_b)
        self.add(Item(dest=FORWARD_ONLY, source=f"{self.template.name}@{self.template_ref}:{FORWARD_ONLY}",
                      kind="generated", part="generated", src_sha=sha256_bytes(cur_b), data=text.encode("utf-8"),
                      replacements=1 if state == "append" else 0, origin="migrate.py"))

    # ------------------------------------------------ kb/INDEX.md — заготовка карты знаний

    @staticmethod
    def readme_head(text):
        lines = text.splitlines()
        title, first = "", ""
        at = next((i for i, ln in enumerate(lines) if ln.startswith("# ")), None)
        if at is not None:
            title = lines[at][2:].strip()
        rest = lines[at + 1:] if at is not None else lines
        for j, ln in enumerate(rest):
            s = ln.strip()
            if s and not s.startswith("#"):
                first = s
                if j + 1 < len(rest) and rest[j + 1].strip():
                    first += " …"
                break
        first = re.sub(r"\[([^\]\n]*)\]\([^)\s]+\)", r"\1", first).replace("**", "")
        return title, first

    def _build_index(self):
        kb = f"{self.skill}/kb/"
        out = ["# Карта знаний — заготовка", "",
               "Заготовка, собранная при переносе базы: для каждой базы — заголовок и первая строка её `README.md` и "
               "тематические папки с числом файлов. Её заменит карта знаний, которая строится после сверки баз.", ""]
        dests = [d for d in self.items if d.startswith(kb)] + [self.index_dest]
        for research, base in self.bases.items():
            prefix = f"{kb}{base}/"
            mine = sorted(d[len(prefix):] for d in dests if d.startswith(prefix))
            readme = self.items.get(prefix + "README.md")
            title, first = self.readme_head(readme.data.decode("utf-8", "replace")) if readme else (base, "")
            out += [f"## {base} — {title}", ""]
            if first:
                out += [first, ""]
            roots = [d for d in mine if "/" not in d]
            out.append("Корень: " + ", ".join(f"[`{d}`]({base}/{d})" for d in roots) + ".")
            out += ["", "| папка | файлов |", "|---|---|"]
            folders = Counter(d.split("/", 1)[0] for d in mine if "/" in d)
            for folder in sorted(folders):
                note = " — к разбору" if folder == "99-raw" else ""
                out.append(f"| [`{folder}/`]({base}/{folder}/){note} | {folders[folder]} |")
            out.append("")
        data = "\n".join(out).rstrip("\n") + "\n"
        self.add(Item(dest=self.index_dest, source="-", kind="generated", part="generated", src_sha="-",
                      data=data.encode("utf-8"), origin="migrate.py"))

    # ------------------------------------------------ path-map.tsv

    def _build_path_map(self):
        rows = []
        for it in list(self.items.values()) + self.aliases:
            rows.append([it.source, it.dest, it.src_sha or "-", it.kind, str(it.replacements)])
        rows.append(["-", self.path_map_dest, "-", "generated", "0"])
        rows.sort(key=lambda r: (r[0].encode("utf-8"), r[1].encode("utf-8")))
        self.path_map_rows = rows
        text = "source\tdest\tsha256\tkind\treplacements\n" + "".join("\t".join(r) + "\n" for r in rows)
        self.add(Item(dest=self.path_map_dest, source="-", kind="generated", part="generated", src_sha="-",
                      data=text.encode("utf-8"), origin="migrate.py"))

    # ------------------------------------------------ вывод

    def files(self):
        return [self.items[d] for d in sorted(self.items, key=lambda s: s.encode("utf-8"))]

    def fingerprint(self):
        return items_fingerprint(self.items.values())

    def rewrites(self):
        """Все замены токенов: (источник, строка, начало, конец, вид, было, стало, место цели, файл цели)."""
        out = []
        for it in self.files():
            if it.zone:
                for r in it.zone["reps"]:
                    out.append((it.zone["old_source"], r.line, r.start, r.end, r.kind, r.raw, r.new, r.target, it.dest))
        return sorted(out, key=lambda x: (x[0], x[1], x[2]))

    def write(self, root):
        root = Path(root)
        for it in self.files():
            p = root / it.dest
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(it.data)
            os.chmod(p, it.mode)

    def summary(self):
        by_part = defaultdict(Counter)
        for it in self.items.values():
            by_part[it.part]["files"] += 1
            by_part[it.part]["bytes"] += len(it.data)
        kinds = Counter(it.kind for it in self.items.values())
        kinds["alias"] = len(self.aliases)
        zone = [it for it in self.items.values() if it.zone]
        rw = Counter()
        for it in zone:
            for r in it.zone["reps"]:
                rw[r.kind] += 1
        return {
            "files": len(self.items), "bytes": sum(len(it.data) for it in self.items.values()),
            "kinds": dict(sorted(kinds.items())), "parts": {k: dict(v) for k, v in sorted(by_part.items())},
            "rewrite": {"zone_files": len(zone), "files_changed": sum(1 for it in zone if it.zone["reps"]),
                        "tokens": sum(rw.values()), "by_kind": dict(sorted(rw.items())),
                        "not_resolving": sum(len(it.zone["broken"]) for it in zone),
                        "held_for_generators": [dict(h, file=it.dest) for it in zone for h in it.zone["held"]]},
            "aliases": len(self.aliases), "journal_excluded": self.info.get("journal_excluded", []),
            "forward_only": self.info.get("forward_only"), "code": dict(self.code_stats),
            "content": dict(self.content_stats), "warnings": self.warnings,
        }


def generator_outputs(skill):
    """Производные файлы kb, чьи генераторы проверяются в смоуке через --check: место файла → утилита. Из данных B:
    code_stage.KB_OUT (что куда пишет генератор) и smoke-list.tsv overlay (у кого в смоуке run: --check). Правка B
    переводит в таких генераторах пути к содержимому в новую форму, а пути к коду (99-raw/tools/…) оставляет — здесь их
    не переписываем, иначе --check видит расхождение (Р112: перегенерация производных — при адаптации, Ф8)."""
    try:
        import code_stage as CS
    except Exception:                                      # noqa: BLE001 — без данных B исключений нет, смоук покажет
        return {}
    smoke_list = OVERLAY / skill / "scripts" / "tests" / "smoke-list.tsv"
    checked = {r["path"] for r in csv.DictReader(open(smoke_list, encoding="utf-8"), delimiter="\t")
               if "--check" in (r.get("smoke") or "")}
    out = {}
    for tool, outs in sorted(CS.KB_OUT.items()):
        if f"scripts/{tool}" in checked:
            for kbp in re.findall(r"`(kb/[^`]+)`", outs):
                out[f"{skill}/{kbp}"] = f"scripts/{tool}"
    return out


def inputs_digest(plan):
    """sha256 входов сборки — для отчёта (что именно собрано)."""
    def fsha(p):
        return sha256_bytes(Path(p).read_bytes())
    patches = hashlib.sha256()
    for p in AP.iter_patches():
        patches.update(p.relative_to(HERE).as_posix().encode() + b"\0" + Path(p).read_bytes())
    overlay = hashlib.sha256()
    for p in sorted(q for q in OVERLAY.rglob("*") if q.is_file()):
        overlay.update(p.relative_to(OVERLAY).as_posix().encode() + b"\0" + p.read_bytes())
    return {"manifest-rules.yaml": fsha(RE.RULES), "tools-map.tsv": fsha(TOOLS_MAP), "patches/": patches.hexdigest(),
            "overlay/": overlay.hexdigest(), "freeze/manifest.tsv.gz": fsha(RE.MANIFEST),
            f"{plan.template.name}@{plan.template_ref}:{FORWARD_ONLY}": plan.forward_only_source_sha,
            "journal": sha256_bytes("\n".join(f"{e.source}\t{e.sha256}" for e in plan.journal_entries).encode())}


def built_template():
    """Шаблон, из которого собран .staging (reports/build.json), — чтобы check и apply пересобирали план так же."""
    try:
        return json.loads((REPORTS / "build.json").read_text(encoding="utf-8")).get("template")
    except (OSError, ValueError):
        return None


def dump_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + "\n", encoding="utf-8")
