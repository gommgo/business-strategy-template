#!/usr/bin/env python3
"""Заморозка базы перед переносом: манифест sha256 всех файлов ресерчей.

Только читает базу. Пишет в _skill-build/freeze/:
  manifest.tsv.gz — ресерч, путь, байты, mtime, sha256 (симлинки — с целью вместо хеша);
  SUMMARY.md      — сводка по ресерчам, отпечаток манифеста, самое позднее изменение.

Мусорные папки (venv, node_modules, __pycache__, .git и др.) не хешируются — только считаются.
Проверка, что база не менялась после заморозки: `python3 freeze.py --verify` (сверяет размер, mtime и, при
расхождении mtime, sha256).

  python3 freeze.py [--verify] [--workers 8]
"""
import argparse
import csv
import gzip
import hashlib
import io
import os
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from count_tokens import HERE, ROOT, research_dirs

OUT = HERE.parent / "freeze"
MANIFEST = OUT / "manifest.tsv.gz"
JUNK_DIRS = {"node_modules", "__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".venv", "venv"}
FIELDS = ["research", "path", "bytes", "mtime", "sha256"]


def is_junk_dir(name):
    return name in JUNK_DIRS or name.startswith("venv-") or name.startswith(".venv")


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(research):
    """(path, stat) файлов ресерча и счётчик мусора."""
    files, junk = [], Counter()
    for dirpath, dirnames, filenames in os.walk(research):
        keep = []
        for d in dirnames:
            full = Path(dirpath) / d
            if is_junk_dir(d) and not full.is_symlink():
                for jp, _jd, jf in os.walk(full):
                    for f in jf:
                        try:
                            junk["bytes"] += (Path(jp) / f).lstat().st_size
                        except OSError:
                            pass
                        junk["files"] += 1
            elif full.is_symlink():
                files.append(full)
            else:
                keep.append(d)
        dirnames[:] = sorted(keep)
        files.extend(Path(dirpath) / f for f in sorted(filenames))
    return files, junk


def row(research, path):
    st = path.lstat()
    rel = path.relative_to(research).as_posix()
    mtime = datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
    if path.is_symlink():
        return [research.name, rel, st.st_size, mtime, "symlink:" + os.readlink(path)]
    return [research.name, rel, st.st_size, mtime, sha256(path)]


def build(workers):
    rows, junk_by, latest = [], {}, {}
    for research in research_dirs(ROOT):
        files, junk = walk(research)
        junk_by[research.name] = junk
        with ThreadPoolExecutor(workers) as pool:
            part = list(pool.map(lambda p, r=research: row(r, p), files))
        rows.extend(part)
        latest[research.name] = max((r[3], r[1]) for r in part) if part else ("", "")
        print(f"{research.name}: {len(part)} файлов", file=sys.stderr)
    return rows, junk_by, latest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true", help="сверить базу с сохранённым манифестом")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    if args.verify:
        with gzip.open(MANIFEST, "rt", newline="") as fh:
            saved = {(r["research"], r["path"]): r for r in csv.DictReader(fh, delimiter="\t")}
        now = {}
        for research in research_dirs(ROOT):
            files, _ = walk(research)
            for p in files:
                now[(research.name, p.relative_to(research).as_posix())] = p
        added = sorted(set(now) - set(saved))
        removed = sorted(set(saved) - set(now))
        changed = []
        for key in sorted(set(now) & set(saved)):
            r, p = saved[key], now[key]
            st = p.lstat()
            mtime = datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
            if int(r["bytes"]) != st.st_size or (mtime != r["mtime"] and not p.is_symlink() and sha256(p) != r["sha256"]):
                changed.append(key)
        for title, items in (("добавлено", added), ("удалено", removed), ("изменено", changed)):
            print(f"{title}: {len(items)}")
            for research, path in items[:20]:
                print(f"  {research}/{path}")
        sys.exit(1 if added or removed or changed else 0)

    OUT.mkdir(parents=True, exist_ok=True)
    rows, junk_by, latest = build(args.workers)
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter="\t", lineterminator="\n")
    writer.writerow(FIELDS)
    writer.writerows(rows)
    text = buf.getvalue()
    fingerprint = hashlib.sha256(text.encode()).hexdigest()
    with gzip.open(MANIFEST, "wt", newline="") as fh:
        fh.write(text)

    per = defaultdict(Counter)
    for r in rows:
        per[r[0]]["files"] += 1
        per[r[0]]["bytes"] += int(r[2])
    lines = [f"# Заморозка базы — {datetime.now():%d.%m.%Y %H:%M}", "",
             f"Манифест: `manifest.tsv.gz` ({len(rows)} файлов), отпечаток sha256 содержимого: `{fingerprint}`.",
             "Проверка неизменности: `python3 ../tools/freeze.py --verify`.", "",
             "| ресерч | файлов | МБ | мусор (не хешируется): файлов / МБ | самое позднее изменение |", "|---|---|---|---|---|"]
    for name in sorted(per):
        j = junk_by.get(name, Counter())
        when, path = latest[name]
        lines.append(f"| {name} | {per[name]['files']} | {per[name]['bytes'] / 1e6:.1f} | {j['files']} / {j['bytes'] / 1e6:.1f} | "
                     f"{when} `{path}` |")
    total = sum(c["bytes"] for c in per.values())
    lines += ["", f"Итого: {len(rows)} файлов, {total / 1e9:.2f} ГБ."]
    (OUT / "SUMMARY.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
