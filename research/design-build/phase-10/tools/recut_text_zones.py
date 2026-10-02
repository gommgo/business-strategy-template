#!/usr/bin/env python3
"""recut_text_zones — вторая нарезка текстовых зон Ф10 по урокам пробы: зона ограничена объёмом окон маркеров.

Берёт прежние списки `phase-10/text-zones/T-<база>-<n>.tsv` (порядок файлов, действия сверки, прочие пункты), считает у
каждого md-файла токены окон маркеров (`kbctx.py`, окно ±1 строка, классы `kbscan.py` плюс файл `--extra`) и режет базу
на зоны `T2-<база>-NN`: не больше `--cap` токенов окон и `--files` файлов. Машинные файлы в списки не идут — они у зон
кода. Пишет `phase-10/text-zones-v2/<зона>.tsv`, свод `_zones.tsv` и по базе — пункты разделов «Для текстов» отчётов
зон кода (`_code-<база>.md`), которые называют md-файлы этой базы.

    python3 research/design-build/phase-10/tools/recut_text_zones.py [--cap 110000] [--files 16] [--extra ФАЙЛ] [--dry]
"""
import argparse
import csv
import importlib.util
import re
import sys
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
spec = importlib.util.spec_from_file_location("kbctx", HERE / "kbctx.py")
kbctx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kbctx)

BASES = ["ai-media", "blender", "creative", "site", "text", "ui", "ux", "common"]
SKIP = re.compile(r"(^|/)99-raw/|(^|/)PLAN\.md$")


def old_rows():
    by_base = OrderedDict((b, []) for b in BASES)
    for f in sorted((PHASE / "text-zones").glob("T-*.tsv"), key=lambda p: (p.stem.rsplit("-", 1)[0], int(p.stem.rsplit("-", 1)[1]))):
        base = f.stem[2:].rsplit("-", 1)[0]
        if base == "cd":
            continue
        for r in csv.DictReader(open(f, encoding="utf-8"), delimiter="\t"):
            if r.get("kind") != "prose" or SKIP.search(r["file"]):
                continue
            by_base.setdefault(base, []).append(r)
    return by_base


def code_items(base):
    """Пункты «Для текстов» отчётов зон кода, называющие md-файлы базы."""
    out = []
    key = "kb/" + base + "/"
    for rep in sorted((PHASE / "reports").glob("К*.md")):
        text = rep.read_text(encoding="utf-8")
        m = re.search(r"^## «?Для текстов»?\s*$(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
        if not m:
            continue
        items, cur = [], []
        for line in m.group(1).split("\n"):
            if line.startswith("| ") or line.startswith("- "):
                if cur:
                    items.append("\n".join(cur))
                cur = [line]
            elif cur and line.strip():
                cur.append(line)
            elif cur:
                items.append("\n".join(cur))
                cur = []
        if cur:
            items.append("\n".join(cur))
        last_dir = None
        for it in items:
            if it.startswith("| файл") or it.startswith("|---"):
                continue
            if key in it or (it.lstrip("| ").startswith("то же") or it.lstrip("| ").startswith("там же") or it.lstrip("| ").startswith("тот же")) and last_dir == base:
                out.append((rep.stem, it))
                last_dir = base
            else:
                last_dir = None if "kb/" in it or "references/" in it or "scripts/" in it or "docs/" in it else last_dir
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=110000)
    ap.add_argument("--files", type=int, default=16)
    ap.add_argument("--extra")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    classes = kbctx.load_classes(a.extra)
    out_dir = PHASE / "text-zones-v2"
    summary = []
    for base, rows in old_rows().items():
        zones, cur, cur_ctx = [], [], 0
        for r in rows:
            p = kbctx.KB / r["file"]
            if not p.is_file():
                continue
            lines = p.read_text(encoding="utf-8").split("\n")
            if lines and lines[-1] == "":
                lines.pop()
            found = kbctx.marks(lines, classes, r["file"].split("/", 1)[0])
            ctx = kbctx.tokens(kbctx.render(r["file"], lines, found, 1))
            full = kbctx.tokens("\n".join(lines))
            has_work = bool(found) or bool(r["actions"].strip()) or bool(r["other"].strip())
            if not has_work:
                continue
            # README базы и файл с действиями читаются шире окон: считаем его целиком
            whole = r["file"].count("/") == 1 and r["file"].endswith("README.md")
            cost = full if whole else ctx + (full // 6 if r["actions"].strip() else 0)
            if cur and (cur_ctx + cost > a.cap or len(cur) >= a.files):
                zones.append((cur, cur_ctx))
                cur, cur_ctx = [], 0
            cur.append((r, len(found), ctx, full, whole))
            cur_ctx += cost
        if cur:
            zones.append((cur, cur_ctx))
        for i, (items, cost) in enumerate(zones, 1):
            name = f"T2-{base}-{i:02d}"
            acts = sum(1 for it in items if it[0]["actions"].strip())
            summary.append((name, base, len(items), sum(it[1] for it in items), cost, sum(it[3] for it in items), acts))
            if a.dry:
                continue
            with open(out_dir / f"{name}.tsv", "w", encoding="utf-8", newline="") as fh:
                w = csv.writer(fh, delimiter="\t", lineterminator="\n")
                w.writerow(["file", "read", "lines", "tokens", "ctx_tokens", "marker_lines", "actions", "other"])
                for r, n, ctx, full, whole in items:
                    w.writerow([r["file"], "целиком" if whole else "окна", r["lines"], full, ctx, n, r["actions"], r["other"]])
        if not a.dry:
            items = code_items(base)
            if items:
                body = [f"# Пункты зон кода для текстов базы `{base}`", "",
                        "Готовые строки из разделов «Для текстов» отчётов зон кода: вносит та зона, в чьём списке стоит файл пункта.",
                        "Пункт о файле вне списка зоны — не твой.", ""]
                for rep, it in items:
                    body.append(f"**{rep}**")
                    body.append(it)
                    body.append("")
                (out_dir / f"_code-{base}.md").write_text("\n".join(body), encoding="utf-8")
    if not a.dry:
        with open(out_dir / "_zones.tsv", "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t", lineterminator="\n")
            w.writerow(["zone", "base", "files", "marker_lines", "read_tokens", "full_tokens", "files_with_actions"])
            w.writerows(summary)
    for s in summary:
        print("%-18s файлов %3d  строк с маркерами %5d  читать ≈ %7d  полный объём %8d  с действиями %2d" % (s[0], s[2], s[3], s[4], s[5], s[6]))
    print("зон:", len(summary), " читать всего ≈", sum(s[4] for s in summary), " полный объём", sum(s[5] for s in summary))


if __name__ == "__main__":
    sys.exit(main())
