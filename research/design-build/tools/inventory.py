#!/usr/bin/env python3
"""Инвентарь ресерчей для фазы 2: классы файлов, политика переноса по умолчанию, ссылки, упоминания Kimi.

Только читает базу. Пишет в _skill-build/phase-2/inventory/:
  files.tsv    — файлы (служебные папки — группами, кроме утилит 99-raw/tools): класс, решение, размер, токены, Kimi;
  links.tsv    — ссылки из переносимых md: куда ведут и что с ними будет при переносе;
  <ресерч>.md  — срез для агента фазы 2;
  SUMMARY.md   — сводка по всем ресерчам.

Политика по умолчанию (решения заказчика 26.09): содержимое и код переносим; ассеты, мусор и служебные папки — нет
(кроме утилит 99-raw/tools); kimi-research — донор, не переносится; закрытые тексты claude-design — никогда.

  python3 inventory.py
"""
import ast
import csv
import hashlib
import json
import os
import re
import warnings
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from count_tokens import CYR, HERE, ROOT, is_bundle, read_text, research_dirs

OUT = HERE.parent / "phase-2" / "inventory"
SERVICE = {"90-sources", "91-videos", "99-raw"}
ROOT_DOCS = {"README.md", "PLAN.md", "CONTRADICTIONS.md"}
SOURCE_INDEX = {"sources.tsv", "sources.md", "sources.yaml", "README.md"}
PROSE = {".md", ".txt"}
DATA = {".json", ".jsonl", ".yaml", ".yml", ".tsv", ".csv", ".toml", ".xml", ".webmanifest", ".vtt", ".srt"}
CODE = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".css", ".scss", ".html", ".htm", ".sh",
        ".glsl", ".frag", ".vert", ".go"}
ASSET = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".svg", ".ico", ".bmp", ".tif", ".tiff", ".mp4", ".webm",
         ".mov", ".m4v", ".mp3", ".wav", ".ogg", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".glb", ".gltf", ".usdz",
         ".blend", ".blend1", ".fbx", ".obj", ".hdr", ".exr", ".ktx2", ".bin", ".pdf", ".psd", ".fig", ".zip", ".gz",
         ".tar", ".wasm", ".npy", ".pt", ".onnx"}
JUNK_DIRS = {"__pycache__", "node_modules", ".venv", "venv", ".cache", ".pytest_cache", ".mypy_cache", "dist", ".git",
             ".next", ".astro"}
JUNK_EXT = {".pyc", ".pyo", ".log", ".map", ".tmp", ".swp", ".lock"}
JUNK_NAMES = {".DS_Store", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Thumbs.db"}
FORBIDDEN = {("claude-design-research", "99-raw/cache")}
DONOR = {"kimi-research"}
MOVE = {"prose", "data", "code", "root-doc", "tool"}
CLASS_ORDER = ["prose", "data", "code", "tool", "root-doc", "asset", "bundle", "junk", "service", "forbidden", "other"]
KIND = {"prose": "prose", "root-doc": "prose", "data": "data", "code": "code", "tool": "code", "bundle": "code"}
PREFIX = {"ux": "ux-research", "ui": "ui-research", "site": "site-research", "text": "text-research",
          "creative": "creative-research", "ai-media": "ai-media-research", "blender": "blender-research",
          "kimi": "kimi-research", "claude-design": "claude-design-research"}
KIMI = re.compile(r"kimi|\bK3\b", re.I)
MD_LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)")
BACKTICK = re.compile(r"`([^`\s]{3,200})`")
SHORT_CROSS = re.compile(r"\b(ux|ui|site|text|creative|ai-media|blender|kimi|claude-design)\s+(\d{2})/(\d{2})(?![\w/])")
SHORT = re.compile(r"(?<![\w/.#-])(\d{2})/(\d{2})(?![\w/])")
VENV = re.compile(r"^\.?venv")
ARROW = re.compile(r"→[^→\n]{0,80}?§")
URL = re.compile(r"[a-z][a-z0-9+.-]*://\S+", re.I)
PATHLIKE = re.compile(r"(?<![\w@./-])((?:\.\.?/|[\w-]+/)[\w./@-]*\.(?:md|ya?ml|json|tsv|csv|txt|py|m?js|cjs|ts|html?|css|png"
                      r"|jpe?g|webp|avif|gif|svg|ico|mp4|webm|mov|mp3|glb|gltf|usdz|hdr|ktx2|bin|woff2?|ttf|otf|pdf|zip))(?![\w/])",
                      re.I)
PLACEHOLDER = re.compile(r"[<>{}*…$|]|\bNN\b|-NN\b|\bXX\b")
ABS = re.compile(r"/home/mm[^\s'\"`)\],;]*")
ASSET_REF = re.compile(r"""(?:src|href|poster)\s*=\s*["']([^"']+\.(?:png|jpe?g|webp|avif|gif|svg|mp4|webm|woff2?|ttf|otf|glb|gltf|hdr|ktx2|bin))["']"""
                       r"""|url\(\s*["']?([^)"']+\.(?:png|jpe?g|webp|avif|gif|svg|woff2?|ttf|otf|mp4|webm))""", re.I)
NETWORK = {"requests", "urllib", "httpx", "aiohttp", "http", "socket", "playwright", "selenium", "yt_dlp", "openai",
           "anthropic", "websocket", "websockets"}
CAL = json.loads((HERE / "calibration.json").read_text())["kinds"]


def tokens(text, kind):
    coef = CAL[kind]
    cyr = len(CYR.findall(text))
    return coef["a"] * cyr + coef["b"] * (len(text) - cyr)


def classify(research, rel, text):
    parts, ext = rel.parts, rel.suffix.lower()
    if any(research == r and rel.as_posix().startswith(p + "/") for r, p in FORBIDDEN):
        return "forbidden"
    if (set(parts[:-1]) & JUNK_DIRS or any(VENV.match(p) or p == "site-packages" for p in parts[:-1])
            or ext in JUNK_EXT or rel.name in JUNK_NAMES):
        return "junk"
    if ext in ASSET:
        return "asset"
    if parts[0] in SERVICE:
        if parts[0] == "99-raw" and len(parts) > 2 and parts[1] == "tools" and ext in CODE:
            return "tool"
        return "service"
    if len(parts) == 1 and rel.name in ROOT_DOCS:
        return "root-doc"
    if ext in PROSE:
        return "prose"
    if ext in DATA:
        return "data"
    if ext in CODE:
        return "bundle" if text is not None and is_bundle(rel, text) else "code"
    return "data" if text is not None else "other"


def decision(research, cls):
    if research in DONOR:
        return "донор"
    return "да" if cls in MOVE else "нет"


def walk(research):
    for path in sorted(research.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(research)
        ext = rel.suffix.lower()
        is_tool = rel.parts[0] == "99-raw" and len(rel.parts) > 2 and rel.parts[1] == "tools"
        text = None
        if (ext in PROSE | DATA | CODE or ext == "") and (rel.parts[0] not in SERVICE or is_tool):
            text = read_text(path)
        yield rel, classify(research.name, rel, text), path.stat().st_size, text


def build_index(research):
    dirs, files = {}, {}
    for child in research.iterdir():
        match = re.match(r"(\d{2})-", child.name)
        if not match:
            continue
        dirs[match.group(1)] = child
        if child.is_dir():
            for sub in child.iterdir():
                sub_match = re.match(r"(\d{2})-", sub.name)
                if sub_match and sub.suffix == ".md":
                    files.setdefault((match.group(1), sub_match.group(1)), sub)
    return {"dirs": dirs, "files": files}


def target_status(target, source_research):
    """(статус, цель от корня базы, межресерчевая ли) для существующего пути."""
    try:
        rel_root = target.relative_to(ROOT)
    except ValueError:
        return "outside", str(target), False
    if not rel_root.parts:
        return "outside", "(корень базы)", False
    research = rel_root.parts[0]
    cross = research != source_research
    if research in DONOR:
        return "to-kimi", rel_root.as_posix(), cross
    if len(rel_root.parts) == 1:
        return "ok", rel_root.as_posix(), cross
    rel = Path(*rel_root.parts[1:])
    if target.is_dir():
        excluded = rel.parts[0] in SERVICE or set(rel.parts) & JUNK_DIRS
        forbidden = any(research == r and rel.as_posix().startswith(p) for r, p in FORBIDDEN)
        return ("to-excluded" if excluded or forbidden else "ok"), rel_root.as_posix(), cross
    cls = classify(research, rel, None if rel.suffix.lower() in CODE else "")
    return ("ok" if cls in MOVE else "to-excluded"), rel_root.as_posix(), cross


def resolve_path(raw, research, file_dir):
    target = raw.split("#")[0].split("?")[0].rstrip(".,;:)")
    if not target:
        return None
    if target.startswith("/"):
        path = Path(target)
        return path if path.exists() else "missing"
    for base in (file_dir, research, ROOT):
        candidate = Path(os.path.normpath(base / target))
        if candidate.exists():
            return candidate
    return "missing"


def looks_like_path(s):
    if "://" in s or PLACEHOLDER.search(s) or s.startswith(("-", "--")):
        return False
    first = s.split("/")[0]
    last = s.rstrip("/").split("/")[-1]
    return (first in ("..", ".") or first in SERVICE or first.endswith("-research") or re.match(r"\d{2}-", first)
            or ("/" in s and "." in last and not last.startswith(".")))


def extract_links(rel, text, research, index):
    file_dir = research / rel.parent
    for line_no, line in enumerate(text.splitlines(), 1):
        spans = []
        for match in MD_LINK.finditer(line):
            raw = match.group(1)
            if not raw.startswith(("http:", "https:", "mailto:", "#", "data:")):
                yield line_no, "md", raw, resolve_path(raw, research, file_dir)
        for match in BACKTICK.finditer(line):
            raw = match.group(1)
            if looks_like_path(raw):
                yield line_no, "backtick", raw, resolve_path(raw, research, file_dir)
        for match in SHORT_CROSS.finditer(line):
            spans.append(match.span())
            other = ROOT / PREFIX[match.group(1)]
            yield line_no, "short-cross", match.group(0), short_target(index.get(other.name), match.group(2), match.group(3))
        for match in SHORT.finditer(line):
            if any(a <= match.start() < b for a, b in spans):
                continue
            yield line_no, "short", match.group(0), short_target(index.get(research.name), match.group(1), match.group(2))


def extract_paths(rel, text, kind, research):
    """Пути в данных и коде: src/href/url(), строки с путями и расширением; адреса URL отбрасываются."""
    file_dir = research / rel.parent
    for line_no, line in enumerate(text.splitlines(), 1):
        for match in PATHLIKE.finditer(URL.sub(" ", line)):
            raw = match.group(1)
            if not PLACEHOLDER.search(raw):
                yield line_no, kind, raw, resolve_path(raw, research, file_dir)


def target_kind(target):
    """Тип цели ссылки, которая сломается: ассет, служебное или прочее (мусор, forbidden)."""
    rel = Path(*target.split("/")[1:]) if "/" in target else Path(target)
    if rel.suffix.lower() in ASSET:
        return "ассет"
    if rel.parts and rel.parts[0] in SERVICE:
        return "служебное"
    return "прочее"


def short_target(idx, folder, file):
    if idx is None:
        return "short-unresolved"
    return idx["files"].get((folder, file)) or "short-unresolved"


def code_info(rel, text):
    info = {"path": rel.as_posix(), "lines": text.count("\n") + 1, "abs": ABS.findall(text),
            "service": sum(text.count(s) for s in SERVICE), "assets": len(ASSET_REF.findall(text)),
            "doc": "", "imports": [], "network": False, "cli": False}
    if rel.suffix == ".py":
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(text)
        except SyntaxError:
            info["doc"] = "(не парсится)"
            return info
        doc = (ast.get_docstring(tree) or "").strip()
        info["doc"] = doc.splitlines()[0][:110] if doc else ""
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                modules.add(node.module.split(".")[0])
        info["imports"] = sorted(modules)
        info["network"] = bool(modules & NETWORK) or "curl " in text or "wget " in text
        info["cli"] = "argparse" in modules or "sys.argv" in text
    return info


def analyze(research, index, file_rows, link_rows):
    name = research.name
    rep = {"classes": defaultdict(Counter), "tops": defaultdict(Counter), "service": defaultdict(Counter),
           "gray": defaultdict(list), "code": [], "kimi": Counter(), "links": Counter(), "examples": defaultdict(list),
           "noise": Counter(), "broken_by": Counter(), "kinds": Counter()}
    ref_files = []
    for rel, cls, size, text in walk(research):
        tok = tokens(text, KIND[cls]) if text is not None and cls in KIND else 0.0
        for counter in (rep["classes"][cls], ):
            counter["files"] += 1
            counter["bytes"] += size
            counter["tokens"] += tok
        top = rel.parts[0] if len(rel.parts) > 1 else "(корень)"
        rep["tops"][top]["files"] += 1
        rep["tops"][top]["bytes"] += size
        rep["tops"][top]["tokens"] += tok
        rep["tops"][top][cls] += 1
        kimi_lines = 0
        if cls == "service" or cls == "forbidden":
            group = "/".join(rel.parts[:2]) if len(rel.parts) > 2 else rel.as_posix()
            rep["service"][group]["files"] += 1
            rep["service"][group]["bytes"] += size
            if rel.parts[0] == "90-sources" and len(rel.parts) == 2 and rel.name in SOURCE_INDEX:
                rep["gray"]["sources"].append(rel.as_posix())
        if text is not None and cls in MOVE:
            kimi_lines = sum(1 for line in text.splitlines() if KIMI.search(line))
            if kimi_lines:
                rep["kimi"][rel.as_posix()] = kimi_lines
            if size > 1_000_000:
                rep["gray"]["large"].append(f"{rel.as_posix()} ({size / 1e6:.1f} МБ)")
            if name not in DONOR:
                source_kind = "md" if rel.suffix == ".md" else ("код" if cls in ("code", "tool") else "данные")
                ref_files.append((rel, text, source_kind))
            if cls in ("code", "tool"):
                rep["code"].append(code_info(rel, text))
        if cls == "root-doc" and rel.name == "PLAN.md":
            rep["gray"]["plan"].append(f"{rel.as_posix()} ({size / 1e3:.0f} КБ)")
        if cls not in ("service", "forbidden"):
            file_rows.append([name, rel.as_posix(), cls, decision(name, cls), size, round(tok), kimi_lines])
    for group, counter in sorted(rep["service"].items()):
        cls = "forbidden" if any(name == r and group.startswith(p) for r, p in FORBIDDEN) else "service"
        file_rows.append([name, group + ("/…" if counter["files"] > 1 else ""), cls, decision(name, cls),
                          counter["bytes"], 0, 0])
    referenced_service = Counter()
    for rel, text, source_kind in ref_files:
        if source_kind == "md":
            for line in text.splitlines():
                if any(s in line for s in SERVICE):
                    rep["noise"]["service_mentions"] += 1
                rep["noise"]["video_marks"] += line.count("[V:")
                rep["noise"]["arrow_refs"] += len(ARROW.findall(line))
            refs = extract_links(rel, text, research, index)
        else:
            refs = extract_paths(rel, text, source_kind, research)
        for line_no, kind, raw, resolved in refs:
            if isinstance(resolved, Path):
                status, target, cross = target_status(resolved, name)
            else:
                status, target, cross = resolved, "", False
            rep["links"][status] += 1
            rep["kinds"][kind] += 1
            if cross:
                rep["noise"]["cross_links"] += 1
            if status == "to-excluded":
                rep["broken_by"][(source_kind, target_kind(target))] += 1
                if target.split("/")[1:2] and target.split("/")[1] in SERVICE:
                    referenced_service[target] += 1
            if status in ("to-excluded", "missing", "to-kimi", "outside") and len(rep["examples"][status]) < 12:
                rep["examples"][status].append(f"{rel.as_posix()}:{line_no} → {raw}")
            link_rows.append([name, rel.as_posix(), line_no, kind, raw, target, status, int(cross)])
    rep["gray"]["referenced_service"] = [f"{t} ({n})" for t, n in referenced_service.most_common()]
    rep["gray"]["asset_refs"] = [f"{c['path']} ({c['assets']})" for c in rep["code"] if c["assets"]]
    return rep


def mb(value):
    return f"{value / 1e6:.1f}"


def ktok(value):
    return f"{value / 1000:.0f}K"


def research_report(name, rep):
    lines = [f"# {name} — инвентарь для фазы 2", "",
             f"Скрипт `_skill-build/tools/inventory.py`, {datetime.now():%d.%m.%Y %H:%M}. Токены — Opus 5.5 по калибровке.",
             "Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, "
             "service, forbidden — нет." + (" **Этот ресерч — донор: в шаблон не переносится.**" if name in DONOR else ""),
             "", "## Классы файлов", "", "| класс | файлов | МБ | ~токенов | переносим? |", "|---|---|---|---|---|"]
    move = Counter()
    stay = Counter()
    for cls in CLASS_ORDER:
        counter = rep["classes"].get(cls)
        if not counter:
            continue
        dec = decision(name, cls)
        lines.append(f"| {cls} | {counter['files']} | {mb(counter['bytes'])} | {ktok(counter['tokens'])} | {dec} |")
        (move if dec == "да" else stay).update(counter)
    lines += [f"| **итого переносим** | {move['files']} | {mb(move['bytes'])} | {ktok(move['tokens'])} | |",
              f"| **итого не переносим** | {stay['files']} | {mb(stay['bytes'])} | — | |", "",
              "## Папки верхнего уровня", "", "| папка | файлов | МБ | ~токенов текста | состав |", "|---|---|---|---|---|"]
    for top, counter in sorted(rep["tops"].items()):
        mix = ", ".join(f"{cls} {counter[cls]}" for cls in CLASS_ORDER if counter.get(cls))
        lines.append(f"| {top} | {counter['files']} | {mb(counter['bytes'])} | {ktok(counter['tokens'])} | {mix} |")
    if rep["service"]:
        lines += ["", "## Служебные папки (группами, топ по размеру)", "", "| группа | файлов | МБ |", "|---|---|---|"]
        for group, counter in sorted(rep["service"].items(), key=lambda kv: -kv[1]["bytes"])[:15]:
            lines.append(f"| {group} | {counter['files']} | {mb(counter['bytes'])} |")
    gray = rep["gray"]
    lines += ["", "## Серые зоны (решить при переносе)", ""]
    for key, title in (("large", "Крупные текстовые файлы > 1 МБ"), ("plan", "PLAN.md (план ресерча)"),
                       ("sources", "Индекс источников в 90-sources"),
                       ("referenced_service", "Служебные файлы, на которые ссылается переносимое (ссылок)"),
                       ("asset_refs", "Код, который ссылается на ассеты (без них сломается; число ссылок)")):
        items = gray.get(key) or []
        shown = "; ".join(items[:12]) + (f"; … ещё {len(items) - 12}" if len(items) > 12 else "")
        lines.append(f"- **{title}**: {len(items)}" + (f" — {shown}" if items else ""))
    code = rep["code"]
    lines += ["", f"## Код и утилиты ({len(code)} файлов)", ""]
    if code:
        lines += ["| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |",
                  "|---|---|---|---|---|---|---|---|"]
        tools = [c for c in code if c["path"].startswith("99-raw/tools/")]
        others = [c for c in code if not c["path"].startswith("99-raw/tools/")]
        for c in tools[:60] + (others if len(others) <= 40 else []):
            imports = ", ".join(i for i in c["imports"] if i not in {"sys", "os", "re", "json", "pathlib", "argparse",
                                                                       "typing", "__future__", "collections", "datetime"})
            lines.append(f"| `{c['path']}` | {c['lines']} | {c['doc'].replace('|', '/')} | {imports[:80]} | "
                         f"{'да' if c['network'] else ''} | {'да' if c['cli'] else ''} | {len(c['abs']) or ''} | "
                         f"{c['service'] or ''} |")
        if len(tools) > 60:
            folders = Counter("/".join(c["path"].split("/")[:3]) for c in tools[60:])
            lines += ["", f"Ещё утилит ({len(tools) - 60}) по папкам: "
                      + ", ".join(f"`{f}` {n}" for f, n in folders.most_common(20))]
        if len(others) > 40:
            folders = Counter("/".join(c["path"].split("/")[:2]) for c in others)
            lines += ["", f"Прочий код ({len(others)} файлов) по папкам: "
                      + ", ".join(f"`{f}` {n}" for f, n in folders.most_common(20))]
        abs_examples = sorted({a for c in code for a in c["abs"]})
        if abs_examples:
            lines += ["", f"Зашитые абсолютные пути ({len(abs_examples)} разных): "
                      + "; ".join(f"`{a}`" for a in abs_examples[:10])]
    links = rep["links"]
    lines += ["", "## Ссылки из переносимых файлов (md, данные, код)", "",
              "| статус | число | смысл |", "|---|---|---|",
              f"| ok | {links['ok']} | цель переносится |",
              f"| to-excluded | {links['to-excluded']} | цель есть, но не переносится (служебное, ассет, мусор) — сломается |",
              f"| to-kimi | {links['to-kimi']} | ведёт в kimi-research (донор) — заменить при уборке |",
              f"| missing | {links['missing']} | цели нет уже сейчас (или путь условный) |",
              f"| outside | {links['outside']} | абсолютный путь вне базы |",
              f"| short-unresolved | {links['short-unresolved']} | адрес «NN/MM» не нашёл файла (часто — номер раздела) |"]
    broken = rep["broken_by"]
    if broken:
        lines += ["", "Сломаются — по источнику ссылки и типу цели:", "",
                  "| тип цели | из md | из данных | из кода | всего |", "|---|---|---|---|---|"]
        for target in ("ассет", "служебное", "прочее"):
            row = [broken[(source, target)] for source in ("md", "данные", "код")]
            if sum(row):
                lines.append(f"| {target} | " + " | ".join(map(str, row)) + f" | {sum(row)} |")
    for status in ("to-excluded", "missing", "to-kimi", "outside"):
        if rep["examples"][status]:
            lines += ["", f"Примеры {status}:"] + [f"- `{e}`" for e in rep["examples"][status]]
    incoming = rep.get("incoming") or Counter()
    lines += ["", "## Входящие ссылки из соседних ресерчей", "",
              (f"Всего {sum(incoming.values())}: " + "; ".join(f"{r} {n}" for r, n in incoming.most_common())
               + ". Самые цитируемые файлы: "
               + "; ".join(f"`{t}` {n}" for t, n in rep["incoming_targets"].most_common(10))) if incoming else "Нет."]
    kinds = rep["kinds"]
    lines += ["", "## Короткие адреса и указатели", "",
              f"- адресов «NN/MM» (свои и «<база> NN/MM»): {kinds['short'] + kinds['short-cross']}, из них файл не найден: "
              f"{links['short-unresolved']} — зависят от нумерации папок и файлов",
              f"- указателей «→ … §» в тексте: {rep['noise']['arrow_refs']} — зависят от нумерации разделов внутри файлов"]
    dups = rep.get("dups") or []
    lines += ["", "## Дубли утилит (md5) в других ресерчах", ""]
    lines += [f"- `{path}` = " + ", ".join(f"`{other}`" for other in group if other != path) for path, group in dups] or ["Нет."]
    kimi = rep["kimi"]
    lines += ["", "## Kimi / K3", "",
              f"{sum(kimi.values())} строк в {len(kimi)} переносимых файлах."
              + (" Топ: " + "; ".join(f"`{f}` {n}" for f, n in kimi.most_common(10)) if kimi else "")]
    noise = rep["noise"]
    lines += ["", "## «Внешнее» — оценка объёма финальной уборки", "",
              f"- ссылок в исключаемое (служебное и т. п.): {links['to-excluded']}; строк с упоминанием служебных папок: "
              f"{noise['service_mentions']}",
              f"- ссылок в соседние ресерчи: {noise['cross_links']} (из них в kimi: {links['to-kimi']})",
              f"- меток роликов `[V:…]`: {noise['video_marks']}",
              f"- строк про Kimi/K3: {sum(kimi.values())}"]
    return "\n".join(lines) + "\n"


def main():
    global OUT
    import argparse
    ap = argparse.ArgumentParser(description="Инвентарь ресерчей")
    ap.add_argument("--out", type=Path, default=OUT, help="куда писать срезы (по умолчанию phase-2/inventory)")
    OUT = ap.parse_args().out.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    researches = research_dirs()
    index = {r.name: build_index(r) for r in researches}
    file_rows, link_rows, reports = [], [], {}
    for research in researches:
        reports[research.name] = analyze(research, index, file_rows, link_rows)
    incoming, incoming_targets = defaultdict(Counter), defaultdict(Counter)
    for name, _source, _line, _kind, _raw, target, status, cross in link_rows:
        if cross and target and status in ("ok", "to-excluded"):
            incoming[target.split("/")[0]][name] += 1
            incoming_targets[target.split("/")[0]][target] += 1
    by_md5 = defaultdict(list)
    for research in researches:
        for c in reports[research.name]["code"]:
            if c["path"].startswith("99-raw/tools/"):
                by_md5[hashlib.md5((research / c["path"]).read_bytes()).hexdigest()].append(f"{research.name}/{c['path']}")
    for research in researches:
        rep = reports[research.name]
        rep["incoming"], rep["incoming_targets"] = incoming[research.name], incoming_targets[research.name]
        rep["dups"] = [(p, g) for g in by_md5.values() if len({x.split("/")[0] for x in g}) > 1
                       for p in g if p.startswith(research.name + "/")]
        (OUT / f"{research.name}.md").write_text(research_report(research.name, rep))
    with (OUT / "files.tsv").open("w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["research", "path", "class", "move", "bytes", "tokens_est", "kimi_lines"])
        writer.writerows(file_rows)
    with (OUT / "links.tsv").open("w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["research", "source", "line", "kind", "raw", "target", "status", "cross"])
        writer.writerows(link_rows)
    head = ["| ресерч | переносим: файлов / МБ / ~ток | не переносим: ассеты / мусор+бандлы / служебное, МБ | код, файлов | "
            "ссылки: ok / сломаются (ассеты · служебное · прочее) / в kimi / нет цели | Kimi, строк | серых зон |",
            "|---|---|---|---|---|---|---|"]
    rows = []
    for name, rep in reports.items():
        cls = rep["classes"]
        move = Counter()
        for c in MOVE:
            move.update(cls.get(c, Counter()))
        junk = cls.get("junk", Counter())["bytes"] + cls.get("bundle", Counter())["bytes"]
        service = cls.get("service", Counter())["bytes"] + cls.get("forbidden", Counter())["bytes"]
        links, gray = rep["links"], rep["gray"]
        gray_count = sum(len(gray.get(k) or []) for k in ("large", "plan", "sources", "referenced_service", "asset_refs"))
        tag = " (донор)" if name in DONOR else ""
        rows.append(f"| {name}{tag} | {move['files']} / {mb(move['bytes'])} / {ktok(move['tokens'])} | "
                    f"{mb(cls.get('asset', Counter())['bytes'])} / {mb(junk)} / {mb(service)} | {len(rep['code'])} | "
                    f"{links['ok']} / {links['to-excluded']} ("
                    + " · ".join(str(sum(v for (s, t), v in rep['broken_by'].items() if t == kind))
                                 for kind in ("ассет", "служебное", "прочее"))
                    + f") / {links['to-kimi']} / {links['missing']} | "
                    f"{sum(rep['kimi'].values())} | {gray_count} |")
    summary = "\n".join([f"# Инвентарь фазы 2 — сводка ({datetime.now():%d.%m.%Y %H:%M})", "",
                         "Срезы по ресерчам — `<ресерч>.md`; построчно — `files.tsv`, `links.tsv`.", ""] + head + rows) + "\n"
    (OUT / "SUMMARY.md").write_text(summary)
    print(summary)


if __name__ == "__main__":
    main()
