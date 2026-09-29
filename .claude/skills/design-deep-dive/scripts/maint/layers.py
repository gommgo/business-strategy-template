#!/usr/bin/env python3
"""Сколько весят «сжатые слои» баз знаний скилла (`kb/<база>/`) — в токенах по коэффициентам `calibration.json`.

Слои: README тематических папок; разделы «Выжимка для агента», «Чек-лист», «Частые ошибки» внутри md-файлов; плюс
наличие `99-raw/skills-map.md`. Раздел — от заголовка до следующего заголовка того же или более высокого уровня.
Файлы базы — те же, что у `count_tokens.py` (тематические папки без служебных).

  python3 .claude/skills/design-deep-dive/scripts/maint/layers.py
"""
import argparse
import json
import re
from collections import defaultdict

from count_tokens import CYR, HERE, research_dirs, thematic_files

SECTIONS = {"digest": re.compile(r"выжимка для агента", re.I),
            "checklist": re.compile(r"чек-?лист", re.I),
            "mistakes": re.compile(r"частые ошибки", re.I)}
HEADING = re.compile(r"^(#{1,6})\s+(.*)")


def sections(text, pattern):
    out, level = [], None
    for line in text.splitlines(keepends=True):
        match = HEADING.match(line)
        if match and level is not None and len(match.group(1)) <= level:
            level = None
        if match and level is None and pattern.search(match.group(2)):
            level = len(match.group(1))
        if level is not None:
            out.append(line)
    return "".join(out)


def main():
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    cal = json.loads((HERE / "calibration.json").read_text())["kinds"]["prose"]

    def tokens(text):
        cyr = len(CYR.findall(text))
        return cal["a"] * cyr + cal["b"] * (len(text) - cyr)

    def cells(row):
        return (f"{row['md']:>5.0f}{row['md_tok'] / 1000:>8.0f}K"
                f"{row['readme']:>6.0f} /{row['readme_tok'] / 1000:>5.0f}K"
                f"{row['digest']:>6.0f} /{row['digest_tok'] / 1000:>6.0f}K"
                f"{row['checklist']:>6.0f} /{row['checklist_tok'] / 1000:>6.0f}K"
                f"{row['mistakes']:>5.0f} /{row['mistakes_tok'] / 1000:>6.0f}K")

    print(f"{'база':<19}{'md':>5}{'md tok':>9}{'README папок':>14}{'Выжимки':>15}{'Чек-листы':>15}"
          f"{'Ошибки':>14}  skills-map")
    totals = defaultdict(float)
    for research in research_dirs():
        row = defaultdict(float)
        for section, path in thematic_files(research):
            if path.suffix != ".md" or section == "(root)":
                continue
            text = path.read_text(errors="replace")
            row["md"] += 1
            row["md_tok"] += tokens(text)
            if path.name == "README.md" and path.parent.parent == research:
                row["readme"] += 1
                row["readme_tok"] += tokens(text)
            for key, pattern in SECTIONS.items():
                part = sections(text, pattern)
                if part:
                    row[key] += 1
                    row[key + "_tok"] += tokens(part)
        skills_map = research / "99-raw" / "skills-map.md"
        sm = f"{tokens(skills_map.read_text(errors='replace')) / 1000:.0f}K tok" if skills_map.exists() else "нет"
        print(f"{research.name:<19}{cells(row)}  {sm}")
        for key, value in row.items():
            totals[key] += value
    print(f"{'ИТОГО':<19}{cells(totals)}")
    print("(формат: число файлов / ~токенов по calibration.json; md tok — все тематические .md целиком)")


if __name__ == "__main__":
    main()
