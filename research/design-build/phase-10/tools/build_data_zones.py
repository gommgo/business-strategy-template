#!/usr/bin/env python3
"""build_data_zones — списки зон данных `Д-<база>` (волна 4 кода Ф10): машинные файлы базы со следами процесса.

Берёт счёт `tools/kbscan.py` по файлам видов data и code под `kb/<база>/` (вне `99-raw`), оставляет файлы с
маркерами целевых классов и классов `--extra` и пишет `phase-10/code-zones/Д-<база>.tsv` (файл · вид · строк ·
токенов · маркеры по классам · сумма) и маски `Д-<база>.masks` для `scripts/maint/accept.py`.

    python3 research/design-build/phase-10/tools/build_data_zones.py [--extra ФАЙЛ] [--dry]
"""
import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
JOURNAL = HERE.parents[1]
spec = importlib.util.spec_from_file_location("kbscan", JOURNAL / "tools" / "kbscan.py")
kbscan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kbscan)

BASES = ["site", "creative", "ai-media", "text", "ux", "ui", "blender", "claude-design", "common"]
EXTS = ["yaml", "yml", "json", "jsonl", "tsv", "csv", "toml", "xml", "js", "mjs", "cjs", "html", "css", "py", "sh", "svg", "glsl"]
SKIP_CLASSES = {"ns_dtcg"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    extra = []
    if a.extra:
        for line in Path(a.extra).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#") and "\t" in line:
                name, pat = line.split("\t", 1)
                extra.append((name.strip(), pat.strip()))
    classes = kbscan.compile_classes(extra=extra)
    kb = kbscan.KB_DEFAULT
    out_dir = HERE.parent / "code-zones"
    names = [n for n in classes if n not in SKIP_CLASSES]
    total = 0
    for base in BASES:
        rows = []
        for p in sorted((kb / base).rglob("*")):
            rel = p.relative_to(kb).as_posix()
            if not p.is_file() or "/99-raw/" in "/" + rel:
                continue
            kind = kbscan.kind_of(p)
            if kind not in ("data", "code"):
                continue
            kind, lines, tokens, counts = kbscan.scan_file(p, classes)
            if kind not in ("data", "code"):
                continue
            if base == "ui":
                counts["k3"] = 0                      # в ui «K3» — id проверки
            s = sum(counts[n] for n in names)
            if s == 0:
                continue
            marks = "; ".join(f"{n} {counts[n]}" for n in names if counts[n])
            rows.append((rel, kind, lines, tokens, marks, s))
        if not rows:
            continue
        total += sum(r[5] for r in rows)
        print("Д-%-14s файлов %3d  строк с маркерами %5d  токенов %8d" % (base, len(rows), sum(r[5] for r in rows), sum(r[3] for r in rows)))
        if a.dry:
            continue
        with open(out_dir / f"Д-{base}.tsv", "w", encoding="utf-8") as fh:
            fh.write("file\tkind\tlines\ttokens\tmarkers\tsum\n")
            for r in rows:
                fh.write("\t".join(str(x) for x in r) + "\n")
        with open(out_dir / f"Д-{base}.masks", "w", encoding="utf-8") as fh:
            fh.write(f"# Д-{base} — машинные файлы базы {base} (волна 4); маски — glob от корня репозитория, для scripts/maint/accept.py --masks-file\n")
            for e in EXTS:
                fh.write(f".claude/skills/design-deep-dive/kb/{base}/**/*.{e}\n")
    print("всего строк с маркерами:", total)


if __name__ == "__main__":
    sys.exit(main())
