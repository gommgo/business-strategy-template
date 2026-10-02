#!/usr/bin/env python3
"""Проверка ссылок и forward-only в текстах скилла design-deep-dive (kb/common, kb/INDEX.md, SKILL.md и др.).

Что ищет в каждом файле:
  • ссылки markdown `[..](путь)` — от папки файла;
  • пути в обратных кавычках (`kb/…`, `common/…`, `ux/03-…/01-….md`, `scripts/…`, `assets/…`, `docs/…`) — от папки файла,
    от `kb/`, от корня скилла, от корня репозитория; `*` — шаблон (нужно ≥ 1 совпадение); `…`, `<…>`, `{…}` — образец, не ссылка;
    не ссылка и расширение файла (`.glb`), а когда файла по такому пути нет — домен с путём (`cdn.example.net/npm/`)
    и тип содержимого (`text/plain`, `model/gltf-binary`);
  • короткие адреса «<база> NN/MM § X.Y» (база: ux, ui, site, text, creative, ai-media, blender, claude-design, cd) —
    файл `kb/<база>/NN-*/MM-*` и раздел по заголовкам (§ X.Y — заголовок, начинающийся с «X.Y»; § имя — заголовок или
    строка с этим именем);
  • следы журнала (forward-only): Р-номера, пути в журнал сборки, имена фаз сборки, даты, слова сравнения с прошлым,
    имя снятого генератора, пути машины — шаблоны `forward-only` в `scripts/maint/data/traces.tsv`. Дата в строке,
    которая начинается со слова «Снимок:», — не след: статья со скоропортящимся знанием называет день своего снимка.

Корень скилла и репозитория — через `scripts/lib/kbpaths.py`: утилита работает в любом клоне и из соседнего чекаута.
Находки выводятся с путём от корня репозитория.

Запуск (Python ≥ 3.11, только стандартная библиотека):
    python3 .claude/skills/design-deep-dive/scripts/maint/refcheck.py <файл> [...]        # ссылки + forward-only
    python3 .claude/skills/design-deep-dive/scripts/maint/refcheck.py --strict <файл> ...  # код 1 и при следах журнала
    python3 .claude/skills/design-deep-dive/scripts/maint/refcheck.py --selftest           # самопроверка во временной папке
Код выхода: 0 — битых ссылок нет; 1 — есть битые (или следы журнала при --strict).
"""
from __future__ import annotations

import argparse
import csv
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import kbpaths  # noqa: E402

ROOT = kbpaths.repo()
SKILL = kbpaths.skill()
KB = kbpaths.kb()
TRACES = kbpaths.data("maint", "traces.tsv")
BASES = list(kbpaths.BASES)
ALIAS = {"cd": "claude-design"}
EXT = (".md", ".yaml", ".yml", ".json", ".tsv", ".csv", ".py", ".js", ".mjs", ".ts", ".html", ".css", ".txt", ".sh",
       ".webp", ".avif", ".png", ".jpg", ".svg", ".glb", ".blend", ".toml")

MD_LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")
TICK = re.compile(r"`([^`\n]+)`")
BASE_RE = "|".join(sorted([re.escape(b) for b in BASES] + ["cd"], key=len, reverse=True))
SHORT = re.compile(
    rf"(?<![\w/.-])({BASE_RE})\s+(\d{{2}})/(\d{{2}}|README)(?![\w/])"
    r"(?:\s*§\s*([0-9]+(?:\.[0-9]+)*|[^\s,;:)`«»\"]+))?")


def trace_rows(kind: str) -> list[dict]:
    """Строки одного вида из `data/traces.tsv` в порядке файла: {kind, label, pattern, example}."""
    lines = [x for x in TRACES.read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    return [row for row in csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE) if row["kind"] == kind]


def load_traces(kind: str) -> list[tuple[str, re.Pattern]]:
    """Шаблоны одного вида: [(метка, регулярка)] в порядке файла."""
    return [(row["label"], re.compile(row["pattern"])) for row in trace_rows(kind)]


FWD = load_traces("forward-only")
DATE = "дата"            # имя следа в данных: в строке снимка статьи он не ищется
SNAPSHOT = "Снимок:"     # начало строки, которой статья называет день своего снимка


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
    if tok.startswith(".") and "/" not in tok:
        return False  # расширение файла («.glb», «.glb.json»), а не имя файла
    return "/" in tok or tok.lower().endswith(EXT)


HOST = re.compile(r"(?:[a-z0-9-]+\.)+[a-z]{2,}", re.I)
MEDIA_TYPES = ("application", "audio", "font", "image", "message", "model", "multipart", "text", "video")
MEDIA_SUBTYPE = re.compile(r"(?!\d{2}-)[a-z0-9][a-z0-9.+-]*", re.I)   # «NN-имя» — папка базы, а не подтип


def not_a_file(tok: str) -> bool:
    """Спан с «/», который называет не файл скилла: домен с путём без схемы (`cdn.example.net/npm/`) или тип
    содержимого из двух слов без расширения файла (`text/plain`, `model/gltf-binary`). Спрашивается, когда файла по
    такому пути нет: существующий путь остаётся ссылкой."""
    tok = tok.rstrip(".,;")
    head, sep, rest = tok.partition("/")
    if not sep:
        return False
    if HOST.fullmatch(head) and not head.lower().endswith(EXT):   # «notes.md/json» — имя файла, а не домен
        return True
    return (head.lower() in MEDIA_TYPES and "/" not in rest and bool(MEDIA_SUBTYPE.fullmatch(rest))
            and not rest.lower().endswith(EXT))


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
            found = resolve_path(first, path)
            if not found and not_a_file(first):
                continue
            n += 1
            if not found:
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
        snapshot = line.lstrip().startswith(SNAPSHOT)
        for label, rx in FWD:
            if snapshot and label == DATE:
                continue
            for m in rx.finditer(line):
                fwd.append(f"{i}: {label}: «{m.group(0)}»")
    return broken, fwd, n


def selftest() -> int:
    """Временная папка с файлом-пробой: по хорошему и битому случаю на каждый вид ссылки и по строке на каждый след."""
    import tempfile
    ok = fail = 0

    def check(name, cond):
        nonlocal ok, fail
        print(("OK   " if cond else "FAIL ") + name)
        ok, fail = ok + bool(cond), fail + (not cond)

    samples = [row["example"] for row in trace_rows("forward-only")]
    check("данные: пример каждого следа находится своим шаблоном",
          all(rx.search(s) for (_, rx), s in zip(FWD, samples)) and len(samples) == len(FWD))
    with tempfile.TemporaryDirectory(prefix="refcheck-") as td:
        d = Path(td)
        (d / "sub").mkdir()
        (d / "sub" / "doc.md").write_text("# Док\n\n## 2. Раздел\n\nтекст\n", encoding="utf-8")
        (d / "other.md").write_text("# Другой\n", encoding="utf-8")
        probe = d / "probe.md"
        probe.write_text("\n".join([
            "# Проба",
            "[есть](other.md) и [нет](missing.md); [снаружи](https://example.org) не считается.",
            "`kb/common/canon.tsv`, `kb/common/nope.tsv`, `kb/common/*.md`, `kb/nope/*.md`.",
            "`sub/doc.md §2` есть, `sub/doc.md §7` нет; `canon.tsv` — имя, `nosuchfile-xyz.md` — нет.",
            "Образцы не ссылки: `kb/<база>/…`, `scripts/{домен}/`.",
            "Адрес ux 06/01 есть, адрес ux 06/99 — нет, ux 06/01 §99.9 — нет раздела.",
            "```",
            f"`kb/в/блоке/кода.md` {samples[0]} — не проверяется",
            "```",
            "Следы: " + "; ".join(samples) + ".",
            "Не файлы: `.glb`, `.glb.json`, `cdn.example.net/npm/`, `text/plain`, `model/gltf-binary`.",
            "Битые пути: `sub/nope`, `text/09-nope`, `sub/nope.glb`, `nope.md/json`.",
            "Снимок: 01.02.2030 · среда и версия.",
            "- Проба: прогон 01.02.2030.",
        ]) + "\n", encoding="utf-8")
        broken, fwd, n = check_file(probe)
        text = "\n".join(broken)
        check("ссылка markdown: битая найдена, живая — нет", "(missing.md)" in text and "(other.md)" not in text)
        check("путь в кавычках: битый найден, живой — нет", "`kb/common/nope.tsv`" in text
              and "`kb/common/canon.tsv`" not in text)
        check("шаблон пути: без совпадений — битый", "`kb/nope/*.md`" in text and "`kb/common/*.md`" not in text)
        check("раздел: нет — битый, есть — нет находки", "`sub/doc.md §7`" in text and "`sub/doc.md §2`" not in text)
        check("голое имя: нет файла — битое, есть — нет", "nosuchfile-xyz.md" in text and "`canon.tsv`" not in text)
        check("образец `<…>`, `{…}` — не ссылка", "<база>" not in text and "{домен}" not in text)
        check("короткий адрес: нет файла и нет раздела — битые", "ux 06/99" in text and "§ 99.9" in text)
        check("блок кода не проверяется", "в/блоке" not in text and not any(f.startswith("8:") for f in fwd))
        labels = [f.split(": ")[1] for f in fwd if f.startswith("10:")]
        check("следы: каждый вид на строке следов — по одному", sorted(labels) == sorted(lbl for lbl, _ in FWD))
        check("расширение, домен с путём и тип содержимого — не ссылки",
              not any(f.startswith("11:") for f in broken) and n == 17)
        check("битый путь без расширения, папка базы под именем типа, файл с расширением и имя файла перед «/» — "
              "находки как прежде",
              all(s in text for s in ("`sub/nope`", "`text/09-nope`", "`sub/nope.glb`", "`nope.md/json`")))
        check("дата в строке «Снимок:» — не след, в обычной строке — след",
              not any(f.startswith("13:") for f in fwd) and [f for f in fwd if f.startswith("14:")] == [
                  f"14: {DATE}: «01.02.2030»"])
        check("битых ссылок — 11", len(broken) == 11)
        rc_plain = main([str(probe), "--quiet"])
        (d / "clean.md").write_text(f"# Чисто\n\nтекст и `kb/common/canon.tsv`; {samples[0]}\n", encoding="utf-8")
        rc_soft = main([str(d / "clean.md"), "--quiet"])
        rc_strict = main([str(d / "clean.md"), "--strict", "--quiet"])
        check("код выхода: битые — 1, следы без --strict — 0, с --strict — 1",
              rc_plain == 1 and rc_soft == 0 and rc_strict == 1)
    print(f"selftest: {ok} OK, {fail} FAIL")
    return 0 if not fail else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--strict", action="store_true", help="код 1 и при следах журнала")
    ap.add_argument("--quiet", action="store_true", help="только итоги по файлам")
    ap.add_argument("--selftest", action="store_true", help="самопроверка во временной папке, без сети")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.files:
        ap.error("назовите файлы или --selftest")
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
