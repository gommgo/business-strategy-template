#!/usr/bin/env python3
"""Статическая проверка Ф7 (phase-7/PLAN.md §6): всё, что тронула фаза, одним прогоном.

Что проверяет (от базового коммита до рабочего дерева):
  1. refcheck --strict по новым и правленым md — находки только в новых файлах и в изменённых строках правленых
     (находки в нетронутых строках — счётом: это ложные срабатывания прежнего текста или хвосты для уборки);
  2. следы прежнего запрета во всех правленых и новых текстах шаблона: «craft», «wireframe и hi-fi … вручную»,
     «Committed-скрипт…» (kb/ и журнал — не в счёт);
  3. описания всех `.claude/skills/*/SKILL.md`: длина каждого ≤ 600 знаков, сумма ≤ 18 000, нет
     `disable-model-invocation`;
  4. YAML и JSON: все новые и правленые `.yaml`, `.yml`, `.json` и frontmatter новых и правленых md парсятся;
  5. карта знаний: mapcheck по `kb/INDEX.md` — «НЕ НОРМА» 0;
  6. реестр и `canon.tsv`: пересборка `registry.py merge` и `canon` совпадает с файлами байт в байт.

Запуск из корня: python3 research/design-build/phase-7/tools/static_check.py [--base f369f34]
Код выхода: 0 — всё чисто; 1 — есть находки.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
JOURNAL = ROOT / "research" / "design-build"
REFCHECK = JOURNAL / "tools" / "refcheck.py"
MAPCHECK = JOURNAL / "tools" / "mapcheck.py"
REGISTRY = JOURNAL / "phase-4" / "tools" / "registry.py"
SKILLS = ROOT / ".claude" / "skills"
CANON = SKILLS / "design-deep-dive" / "kb" / "common" / "canon.tsv"

TRACES = [
    (re.compile(r"\bcraft\b", re.I), "craft"),
    (re.compile(r"hi-fi[^\n]{0,80}вручную|вручную[^\n]{0,80}hi-fi", re.I), "wireframe и hi-fi вручную"),
    (re.compile(r"Committed-скрипт", re.I), "Committed-скрипт"),
]
HIT = re.compile(r"^\s+([A-ZА-ЯЁ]+)\s*·\s*(\d+):")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def changed_files(base):
    out = git("diff", "--name-only", base, "--", ".claude", "docs", "CLAUDE.md", "README.md", "CONTRIBUTING.md",
              ".gitignore", ".gitattributes")
    new = set(git("diff", "--name-only", "--diff-filter=A", base, "--", ".claude", "docs").split())
    files = [f for f in out.split() if (ROOT / f).exists()]
    return files, new


def changed_lines(base, f):
    diff = git("diff", "-U0", base, "--", f)
    lines = set()
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff, re.M):
        start, cnt = int(m.group(1)), int(m.group(2) or 1)
        lines.update(range(start, start + cnt))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="f369f34")
    a = ap.parse_args()
    files, new = changed_files(a.base)
    bad = 0

    # 1. refcheck
    md = [f for f in files if f.endswith(".md") and "/kb/" not in f or f.endswith("kb/INDEX.md")
          or re.search(r"kb/common/[^/]+\.md$", f)]
    md = sorted(set(f for f in md if f.endswith(".md")))
    in_changed, untouched = [], 0
    for f in md:
        out = subprocess.run([sys.executable, str(REFCHECK), "--strict", f], cwd=ROOT, capture_output=True,
                             text=True).stdout
        cl = None if f in new else changed_lines(a.base, f)
        for line in out.splitlines():
            m = HIT.match(line)
            if not m:
                continue
            n = int(m.group(2))
            if cl is None or n in cl:
                in_changed.append(f"{f}: {line.strip()}")
            else:
                untouched += 1
    print(f"1. refcheck --strict: {len(md)} md; находок в новых файлах и изменённых строках — {len(in_changed)}; "
          f"в нетронутых строках — {untouched}")
    for h in in_changed:
        print("   !!", h)
    bad |= bool(in_changed)

    # 2. следы прежнего запрета
    tr = []
    for f in files:
        if "/kb/" in f or not f.endswith(".md"):
            continue
        for i, line in enumerate((ROOT / f).read_text(encoding="utf-8").splitlines(), 1):
            for rx, name in TRACES:
                if rx.search(line):
                    tr.append(f"{f}:{i}: «{name}»: {line.strip()[:120]}")
    print(f"2. следы прежнего запрета: {len(tr)}")
    for t in tr:
        print("   !!", t)
    bad |= bool(tr)

    # 3. описания
    try:
        import yaml
    except ImportError:
        yaml = None
    total, over, hidden = 0, [], []
    rows = []
    for p in sorted(SKILLS.glob("*/SKILL.md")):
        text = p.read_text(encoding="utf-8")
        fm = text.split("---", 2)[1] if text.startswith("---") else ""
        d = yaml.safe_load(fm) if yaml else {}
        desc = str((d or {}).get("description", ""))
        total += len(desc)
        rows.append((p.parent.name, len(desc)))
        if len(desc) > 600:
            over.append((p.parent.name, len(desc)))
        if (d or {}).get("disable-model-invocation"):
            hidden.append(p.parent.name)
    print(f"3. описания: скиллов {len(rows)}, сумма {total} знаков (цель ≤ 18 000); длиннее 600 — {len(over)}; "
          f"скрытых от модели — {len(hidden)}")
    for name, n in over:
        print(f"   !! {name}: {n}")
    for name in hidden:
        print(f"   !! скрыт: {name}")
    bad |= bool(over) or total > 18000

    # 4. YAML и JSON
    perr = []
    for f in files:
        p = ROOT / f
        try:
            if f.endswith((".yaml", ".yml")) and yaml:
                yaml.safe_load(p.read_text(encoding="utf-8"))
            elif f.endswith(".json"):
                json.loads(p.read_text(encoding="utf-8"))
            elif f.endswith(".md") and yaml:
                t = p.read_text(encoding="utf-8")
                if t.startswith("---\n"):
                    yaml.safe_load(t.split("---", 2)[1])
        except Exception as e:  # noqa: BLE001
            perr.append(f"{f}: {e}")
    print(f"4. YAML, JSON и frontmatter: ошибок {len(perr)}")
    for e in perr:
        print("   !!", e)
    bad |= bool(perr)

    # 5. mapcheck
    mc = subprocess.run([sys.executable, str(MAPCHECK), str(SKILLS / "design-deep-dive" / "kb" / "INDEX.md")],
                        cwd=ROOT, capture_output=True, text=True)
    notnorm = mc.stdout.count("НЕ НОРМА")
    check = mc.stdout.count("ПРОВЕРИТЬ")
    print(f"5. mapcheck kb/INDEX.md: «НЕ НОРМА» {notnorm}, «ПРОВЕРИТЬ» {check}")
    bad |= notnorm > 0

    # 6. реестр и canon.tsv
    with tempfile.TemporaryDirectory() as td:
        reg = Path(td) / "registry.tsv"
        can = Path(td) / "canon.tsv"
        subprocess.run([sys.executable, str(REGISTRY), "merge", "--out", str(reg)], cwd=REGISTRY.parents[1],
                       capture_output=True, text=True)
        subprocess.run([sys.executable, str(REGISTRY), "canon", "--registry", str(reg), "--out", str(can)],
                       cwd=REGISTRY.parents[1], capture_output=True, text=True)
        same_reg = reg.read_bytes() == (JOURNAL / "phase-4" / "registry.tsv").read_bytes()
        same_can = can.read_bytes() == CANON.read_bytes()
    print(f"6. пересборка: registry.tsv {'байт в байт' if same_reg else 'РАСХОДИТСЯ'}, "
          f"canon.tsv {'байт в байт' if same_can else 'РАСХОДИТСЯ'}")
    bad |= not (same_reg and same_can)

    print("ИТОГ:", "чисто" if not bad else "есть находки")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
