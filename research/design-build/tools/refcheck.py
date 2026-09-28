#!/usr/bin/env python3
"""Проверка ссылок и forward-only в текстах скилла design-deep-dive (kb/common, kb/INDEX.md, SKILL.md и др.).

Что ищет в каждом файле:
  • ссылки markdown `[..](путь)` — от папки файла;
  • пути в обратных кавычках (`kb/…`, `common/…`, `ux/03-…/01-….md`, `scripts/…`, `assets/…`, `docs/…`) — от папки файла,
    от `kb/`, от корня скилла, от корня репозитория; `*` — шаблон (нужно ≥ 1 совпадение); `…`, `<…>`, `{…}` — образец, не ссылка;
  • короткие адреса «<база> NN/MM § X.Y» (база: ux, ui, site, text, creative, ai-media, blender, claude-design, cd) —
    файл `kb/<база>/NN-*/MM-*` и раздел по заголовкам (§ X.Y — заголовок, начинающийся с «X.Y»; § имя — заголовок или
    строка с этим именем);
  • следы журнала (forward-only): Р-номера, пути в журнал сборки, имена фаз сборки (Ф4…Ф10), даты, слова сравнения с прошлым,
    имя снятого генератора.

Запуск (Python ≥ 3.11, только стандартная библиотека):
    python3 research/design-build/tools/refcheck.py <файл> [...]        # ссылки + forward-only
    python3 research/design-build/tools/refcheck.py --strict <файл> ...  # код 1 и при следах журнала
Код выхода: 0 — битых ссылок нет; 1 — есть битые (или следы журнала при --strict).
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / ".claude" / "skills" / "design-deep-dive"
KB = SKILL / "kb"
BASES = ["ux", "ui", "site", "text", "creative", "ai-media", "blender", "claude-design"]
ALIAS = {"cd": "claude-design"}
EXT = (".md", ".yaml", ".yml", ".json", ".tsv", ".csv", ".py", ".js", ".mjs", ".ts", ".html", ".css", ".txt", ".sh",
       ".webp", ".avif", ".png", ".jpg", ".svg", ".glb", ".blend", ".toml")

MD_LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")
TICK = re.compile(r"`([^`\n]+)`")
BASE_RE = "|".join(sorted([re.escape(b) for b in BASES] + ["cd"], key=len, reverse=True))
SHORT = re.compile(
    rf"(?<![\w/.-])({BASE_RE})\s+(\d{{2}})/(\d{{2}}|README)(?![\w/])"
    r"(?:\s*§\s*([0-9]+(?:\.[0-9]+)*|[^\s,;:)`«»\"]+))?")

FWD = [
    ("Р-номер", re.compile(r"(?<![\w-])Р\d{1,3}(?!\d)")),
    ("журнал", re.compile(r"research/design-build|design-build/|\bphase-\d\b|DECISIONS\.md|SYNTHESIS|CHAIN\.md")),
    ("фаза сборки", re.compile(r"(?<![\w-])Ф(?:[0-9]|10)(?![\w-])")),
    ("дата", re.compile(r"\b\d{1,2}\.\d{2}\.20\d{2}\b|\b\d{1,2} (?:января|февраля|марта|апреля|мая|июня|июля|августа|"
                        r"сентября|октября|ноября|декабря)(?: 20\d{2})?\b")),
    ("сравнение с прошлым", re.compile(r"(?i)(?<![\w-])(теперь|больше не|по-прежнему|как и раньше|прежн\w+|"
                                       r"раньше было|было\s*/\s*стало|устаревш\w+ верси\w+)(?![\w-])")),
    ("снятый генератор", re.compile(r"(?i)\bkimi\b|\bK2\.5\b")),
]


def headings(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    out, fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence and re.match(r"^#{1,6}\s", line):
            out.append(re.sub(r"^#{1,6}\s+", "", line).strip())
    return out


def section_ok(path: Path, sec: str) -> bool:
    if not path.is_file() or path.suffix != ".md":
        return True  # раздел проверяем только у md
    heads = headings(path)
    sec = sec.strip().rstrip(".")
    if re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", sec):
        pat = re.compile(rf"^(?:§\s*)?(?:[A-Za-zА-Яа-я]+\s+)?{re.escape(sec)}(?:[.\s)]|$)")
        return any(pat.match(h) for h in heads)
    low = sec.lower()
    if any(low in h.lower() for h in heads):
        return True
    return low in path.read_text(encoding="utf-8").lower()


def resolve_short(base: str, nn: str, mm: str) -> Path | None:
    base = ALIAS.get(base, base)
    dirs = sorted((KB / base).glob(f"{nn}-*"))
    dirs = [d for d in dirs if d.is_dir()]
    if not dirs:
        return None
    if mm == "README":
        p = dirs[0] / "README.md"
        return p if p.exists() else None
    files = sorted(dirs[0].glob(f"{mm}-*"))
    md = [f for f in files if f.suffix == ".md"]
    return (md or files or [None])[0]


def looks_like_path(tok: str) -> bool:
    if any(c in tok for c in "…<>{}=()|\"'") or "..." in tok:
        return False
    if tok.startswith(("-", "http", "$", "~", "#", "/")) or ":" in tok:
        return False
    if re.match(r"\d{2}/", tok):
        return False  # адрес папки без базы («04/*», «11/») — база названа в тексте рядом
    return "/" in tok or tok.lower().endswith(EXT)


_NAMES: dict[str, bool] = {}


def name_exists(name: str) -> bool:
    """Голое имя файла (без «/») — имя, место даёт контекст: достаточно, чтобы такой файл был в скилле или в docs/."""
    if name not in _NAMES:
        found = (ROOT / name).is_file()  # файлы корня репозитория: `CLAUDE.md`, `CONTRIBUTING.md`
        for base in () if found else (SKILL, ROOT / "docs", ROOT / ".claude"):
            if any(base.rglob(name)):
                found = True
                break
        _NAMES[name] = found
    return _NAMES[name]


def resolve_path(tok: str, here: Path) -> bool:
    tok = tok.rstrip(".,;")
    if "/" not in tok.rstrip("/"):
        return name_exists(tok.rstrip("/"))
    cands = [here.parent, KB, SKILL, ROOT, ROOT / "docs" / "projects" / "_template", ROOT / "docs" / "projects",
             ROOT / "docs"]
    for base in cands:
        target = base / tok
        if "*" in tok or "?" in tok:
            if glob.glob(str(target)):
                return True
        elif target.exists():
            return True
    return False


def check_file(path: Path) -> tuple[list[str], list[str], int]:
    broken, fwd, n = [], [], 0
    text = path.read_text(encoding="utf-8")
    fence = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        # ссылки markdown
        for m in MD_LINK.finditer(line):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            n += 1
            file_part = target.split("#", 1)[0]
            if file_part and not (path.parent / file_part).exists():
                broken.append(f"{i}: ссылка ({target})")
        # пути в обратных кавычках
        for m in TICK.finditer(line):
            tok = m.group(1).strip()
            first = tok.split(" §")[0].split("#")[0].strip()
            if " " in first:
                first = first.split()[0]
            if not looks_like_path(first):
                continue
            n += 1
            if not resolve_path(first, path):
                broken.append(f"{i}: путь `{tok}`")
                continue
            msec = re.search(r"§\s*([0-9]+(?:\.[0-9]+)*|[^\s,;:)`]+)", tok)
            if msec:
                for base in (path.parent, KB, SKILL, ROOT):
                    t = base / first
                    if t.exists():
                        if not section_ok(t, msec.group(1)):
                            broken.append(f"{i}: раздел `{tok}`")
                        break
        # короткие адреса
        for m in SHORT.finditer(line):
            base, nn, mm, sec = m.group(1), m.group(2), m.group(3), m.group(4)
            n += 1
            p = resolve_short(base, nn, mm)
            if p is None:
                broken.append(f"{i}: адрес «{m.group(0).strip()}» — нет файла")
                continue
            if sec:
                secs = [sec]
                tail = line[m.end():m.end() + 12]
                mt = re.match(r"\s*[–-]\s*§?\s*([0-9]+(?:\.[0-9]+)*)", tail)
                if mt:
                    secs.append(mt.group(1))
                for s in secs:
                    if not section_ok(p, s):
                        broken.append(f"{i}: адрес «{base} {nn}/{mm} § {s}» — нет раздела в {p.relative_to(KB)}")
        for label, rx in FWD:
            for m in rx.finditer(line):
                fwd.append(f"{i}: {label}: «{m.group(0)}»")
    return broken, fwd, n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--strict", action="store_true", help="код 1 и при следах журнала")
    ap.add_argument("--quiet", action="store_true", help="только итоги по файлам")
    args = ap.parse_args()
    total_broken = total_fwd = 0
    for f in args.files:
        p = Path(f).resolve()
        if not p.exists():
            print(f"{f}: нет файла")
            total_broken += 1
            continue
        broken, fwd, n = check_file(p)
        total_broken += len(broken)
        total_fwd += len(fwd)
        rel = p.relative_to(ROOT) if p.is_relative_to(ROOT) else p
        print(f"{rel}: ссылок {n}, битых {len(broken)}, следов журнала {len(fwd)}")
        if not args.quiet:
            for b in broken:
                print(f"  БИТАЯ · {b}")
            for w in fwd:
                print(f"  СЛЕД · {w}")
    print(f"итого: битых {total_broken}, следов журнала {total_fwd}")
    return 1 if total_broken or (args.strict and total_fwd) else 0


if __name__ == "__main__":
    sys.exit(main())
