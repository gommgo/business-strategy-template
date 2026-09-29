#!/usr/bin/env python3
"""Объём тематического контента баз знаний скилла (`kb/<база>/`): файлы, символы, оценка токенов.

Тематическое — всё внутри папки базы, кроме служебных `90-sources`, `91-videos`, `99-raw`; корневые `README.md`,
`PLAN.md`, `CONTRADICTIONS.md` идут отдельной колонкой «root tok». Собранный или минифицированный код (строка длиннее
5000 знаков, `dist/`, `node_modules/`, `.min.`) считается отдельно — «бандлы».

Токены оцениваются моделью  tokens = a · кириллица + b · прочие символы; коэффициенты по видам файлов (prose, data,
code) измеряет `calibrate.py` и пишет в `calibration.json` рядом. Без калибровки печатаются только символы.

  python3 .claude/skills/design-deep-dive/scripts/maint/count_tokens.py                  # сводка по базам
  python3 .claude/skills/design-deep-dive/scripts/maint/count_tokens.py --by-folder      # плюс разбивка по папкам
  python3 .claude/skills/design-deep-dive/scripts/maint/count_tokens.py --csv out.csv    # все строки в CSV
"""
import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import sys; sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib")); import kbpaths
ROOT = kbpaths.kb()
HERE = Path(__file__).resolve().parent
SERVICE = {"90-sources", "91-videos", "99-raw"}
ROOT_DOCS = {"README.md", "PLAN.md", "CONTRADICTIONS.md"}
KINDS = {
    "prose": {".md", ".txt"},
    "data": {".json", ".yaml", ".yml", ".tsv", ".csv", ".log", ".toml", ".xml", ".webmanifest", ".lock"},
    "code": {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".html", ".htm", ".css", ".py", ".sh", ".svg", ".go", ".glsl"},
}
TEXT_KINDS = ("prose", "data", "code", "bundle")
CYR = re.compile(r"[Ѐ-ӿ]")
BUNDLE_LINE = 5000  # строка длиннее — минифицированный/собранный код, а не контент


def read_text(path):
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw[:8192]:
        return None
    return raw.decode("utf-8", errors="replace")


def kind_of(path):
    ext = path.suffix.lower()
    for kind, exts in KINDS.items():
        if ext in exts:
            return kind
    return "binary"


def is_bundle(path, text):
    parts = set(path.parts)
    return ("dist" in parts or "node_modules" in parts or ".min." in path.name
            or max((len(line) for line in text.splitlines()), default=0) > BUNDLE_LINE)


def research_dirs(root=ROOT):
    return sorted(p for p in root.iterdir() if p.is_dir() and p.name in kbpaths.BASES)  # папки баз kb/<база>


def thematic_files(research):
    """(section, path) для всех не-служебных файлов базы."""
    for child in sorted(research.iterdir()):
        if child.name in SERVICE:
            continue
        if child.is_file():
            yield ("(root)" if child.name in ROOT_DOCS else child.name), child
        else:
            for path in sorted(child.rglob("*")):
                if path.is_file():
                    yield child.name, path


def text_stats(text):
    return {"chars": len(text), "cyr": len(CYR.findall(text)), "lines": text.count("\n") + 1}


def scan(root=ROOT):
    rows = defaultdict(lambda: {"files": 0, "bytes": 0, "chars": 0, "cyr": 0, "lines": 0})
    service_bytes = defaultdict(int)
    for research in research_dirs(root):
        for section, path in thematic_files(research):
            kind = kind_of(path)
            text = None
            if kind != "binary" or path.suffix == "":
                text = read_text(path)
                if text is not None and kind == "binary":
                    kind = "data"
                if text is not None and kind == "code" and is_bundle(path, text):
                    kind = "bundle"
            row = rows[(research.name, section, kind)]
            row["files"] += 1
            row["bytes"] += path.stat().st_size
            if text is not None:
                for key, value in text_stats(text).items():
                    row[key] += value
        for name in SERVICE:
            service = research / name
            if service.is_dir():
                service_bytes[research.name] += sum(p.stat().st_size for p in service.rglob("*") if p.is_file())
    return rows, service_bytes


def load_calibration(path):
    return json.loads(path.read_text()) if path.exists() else None


def estimate(row, kind, cal):
    if cal is None or kind not in TEXT_KINDS:
        return None
    coef = cal["kinds"].get("code" if kind == "bundle" else kind) or cal["global"]
    return coef["a"] * row["cyr"] + coef["b"] * (row["chars"] - row["cyr"])


def fmt_k(value):
    return "—" if value is None else f"{value / 1000:,.0f}K".replace(",", " ")


def summarize(rows, keys):
    total = {"files": 0, "bytes": 0, "chars": 0, "cyr": 0, "tokens": 0.0, "bin_files": 0, "bin_bytes": 0,
             "bundle_chars": 0}
    by_kind = defaultdict(float)
    for key in keys:
        row, kind = rows[key], key[2]
        if kind == "binary":
            total["bin_files"] += row["files"]
            total["bin_bytes"] += row["bytes"]
            continue
        if kind == "bundle":
            total["bundle_chars"] += row["chars"]
            continue
        total["files"] += row["files"]
        total["chars"] += row["chars"]
        total["cyr"] += row["cyr"]
        tokens = row.get("tokens")
        if tokens is not None:
            total["tokens"] += tokens
            by_kind[kind] += tokens
    return total, by_kind


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT, help="папка баз (по умолчанию kb/ скилла)")
    parser.add_argument("--calibration", type=Path, default=HERE / "calibration.json",
                        help="коэффициенты калибровки (по умолчанию calibration.json рядом)")
    parser.add_argument("--by-folder", action="store_true", help="разбивка по тематическим папкам")
    parser.add_argument("--csv", type=Path, help="все строки в CSV")
    args = parser.parse_args()

    cal = load_calibration(args.calibration)
    rows, service_bytes = scan(args.root)
    for (research, section, kind), row in rows.items():
        row["tokens"] = estimate(row, kind, cal)

    has_tokens = cal is not None
    tok = lambda value: fmt_k(value if has_tokens else None)
    print(f"Калибровка: {args.calibration if has_tokens else 'нет — только символы'}")
    if has_tokens:
        print(f"Модель: {cal['model']}; коэффициенты (токенов на символ):",
              ", ".join(f"{k}: кир {v['a']:.3f} / проч {v['b']:.3f}" for k, v in cal["kinds"].items()))
    header = (f"{'база':<20}{'тем.файлов':>11}{'символов':>11}{'кирил%':>8}"
              f"{'tok prose':>11}{'tok data':>10}{'tok code':>10}{'tok итого':>11}"
              f"{'root tok':>10}{'бандлы симв':>12}{'бинарн.':>9}{'бин МБ':>8}{'служ. МБ':>10}")
    print(header)
    print("-" * len(header))
    grand = defaultdict(float)
    researches = sorted({key[0] for key in rows})
    for research in researches:
        theme_keys = [k for k in rows if k[0] == research and k[1] != "(root)"]
        root_keys = [k for k in rows if k[0] == research and k[1] == "(root)"]
        theme, by_kind = summarize(rows, theme_keys)
        root, _ = summarize(rows, root_keys)
        cyr_share = 100 * theme["cyr"] / theme["chars"] if theme["chars"] else 0
        print(f"{research:<20}{theme['files']:>11}{fmt_k(theme['chars']):>11}{cyr_share:>7.0f}%"
              f"{tok(by_kind['prose']):>11}{tok(by_kind['data']):>10}{tok(by_kind['code']):>10}{tok(theme['tokens']):>11}"
              f"{tok(root['tokens']):>10}{fmt_k(theme['bundle_chars']):>12}"
              f"{theme['bin_files']:>9}{theme['bin_bytes'] / 1e6:>8.0f}{service_bytes[research] / 1e6:>10.0f}")
        for key, value in (("files", theme["files"]), ("chars", theme["chars"]), ("cyr", theme["cyr"]),
                           ("bundle", theme["bundle_chars"]),
                           ("prose", by_kind["prose"]), ("data", by_kind["data"]), ("code", by_kind["code"]),
                           ("tokens", theme["tokens"]), ("root", root["tokens"]), ("root_chars", root["chars"]),
                           ("bin_files", theme["bin_files"]), ("bin_bytes", theme["bin_bytes"]),
                           ("service", service_bytes[research])):
            grand[key] += value
    print("-" * len(header))
    cyr_share = 100 * grand["cyr"] / grand["chars"] if grand["chars"] else 0
    print(f"{'ИТОГО':<20}{grand['files']:>11.0f}{fmt_k(grand['chars']):>11}{cyr_share:>7.0f}%"
          f"{tok(grand['prose']):>11}{tok(grand['data']):>10}{tok(grand['code']):>10}{tok(grand['tokens']):>11}"
          f"{tok(grand['root']):>10}{fmt_k(grand['bundle']):>12}"
          f"{grand['bin_files']:>9.0f}{grand['bin_bytes'] / 1e6:>8.0f}{grand['service'] / 1e6:>10.0f}")
    print(f"root-доки (README/PLAN/CONTRADICTIONS) всего: {fmt_k(grand['root_chars'])} символов")

    if args.by_folder:
        for research in researches:
            print(f"\n== {research}")
            sections = sorted({k[1] for k in rows if k[0] == research})
            for section in sections:
                keys = [k for k in rows if k[0] == research and k[1] == section]
                total, by_kind = summarize(rows, keys)
                cyr_share = 100 * total["cyr"] / total["chars"] if total["chars"] else 0
                binaries = f"  +{total['bin_files']} бин." if total["bin_files"] else ""
                print(f"  {section:<42}{total['files']:>5} ф{fmt_k(total['chars']):>9} симв{cyr_share:>5.0f}% кир"
                      f"{tok(total['tokens']):>9} tok (prose {tok(by_kind['prose'])}){binaries}")

    if args.csv:
        with args.csv.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["base", "section", "kind", "files", "bytes", "chars", "cyr", "lines", "tokens_est"])
            for (research, section, kind), row in sorted(rows.items()):
                tokens = row["tokens"]
                writer.writerow([research, section, kind, row["files"], row["bytes"], row["chars"], row["cyr"],
                                 row["lines"], "" if tokens is None else round(tokens)])
        print(f"\nCSV: {args.csv}")


if __name__ == "__main__":
    main()
