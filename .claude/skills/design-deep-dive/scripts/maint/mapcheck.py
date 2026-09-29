#!/usr/bin/env python3
"""Проверка карты знаний по `kb/common/canon.tsv`: адрес карты не должен вести в копию нормы вместо её канона.

Для каждого адреса с разделом или ключом (короткий «ux 06/01 §2», путь в обратных кавычках с `§…` или `#ключ`):
  • ПРОВЕРИТЬ — адрес совпадает с местом из колонки `copies` какой-то нормы и не совпадает ни с одним `place`:
    печатается канон этой нормы и её id. Один раздел бывает каноном одной нормы и копией другой, поэтому это вопрос,
    а не ошибка: если строка карты говорит именно об этой норме — адрес меняют на канон;
  • НЕ НОРМА — адрес (любой, и без раздела) ведёт в материал к разбору (`99-raw/`), в `PLAN.md` базы или в журнал
    сборки — ошибка; шаблоны — `not-norm` в `scripts/maint/data/traces.tsv`.
Адрес файла целиком — вход, а не место нормы: он не сверяется с копиями.
Совпадение: тот же файл и тот же раздел; раздел «§4» совпадает с «§4.2» копии только точно.

Запуск (Python ≥ 3.11, только стандартная библиотека):
    python3 .claude/skills/design-deep-dive/scripts/maint/mapcheck.py <файл карты> [...] [--canon ФАЙЛ]
    python3 .claude/skills/design-deep-dive/scripts/maint/mapcheck.py --selftest
Код выхода: 0 — ссылок «не на норму» нет (строки ПРОВЕРИТЬ допустимы); 1 — есть.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import kbpaths  # noqa: E402

kbpaths.use("maint")
import refcheck  # noqa: E402

KB = refcheck.KB
CANON = KB / "common" / "canon.tsv"
NOT_NORM = refcheck.load_traces("not-norm")


def norm_path(p: str) -> str:
    p = p.strip().rstrip(".,;")
    if p.startswith("kb/"):
        p = p[3:]
    return p


def split_place(s: str) -> tuple[str, str]:
    s = s.strip()
    m = re.match(r"^(.*?)(?:\s*§\s*(.+)|#(.+))?$", s)
    path = norm_path(m.group(1))
    sec = (m.group(2) or m.group(3) or "").strip()
    sec = sec.split(",")[0].split("–")[0].strip().rstrip(".")
    return path, sec


def load_canon(canon: Path = CANON):
    places, copies = set(), {}
    with canon.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            places.add(split_place(r["place"]))
            for c in (r.get("copies") or "").split(";"):
                c = c.strip()
                if not c or c == "—":
                    continue
                copies.setdefault(split_place(c), []).append((r["id"], r["place"], r["norm"]))
    return places, copies


def not_norm(path: str) -> bool:
    return any(rx.search(path) for _, rx in NOT_NORM)


def addresses(line: str):
    for m in refcheck.SHORT.finditer(line):
        base, nn, mm, sec = m.group(1), m.group(2), m.group(3), m.group(4) or ""
        p = refcheck.resolve_short(base, nn, mm)
        if p is not None:
            yield m.group(0).strip(), str(p.relative_to(KB)), sec.strip().rstrip(".")
    for m in refcheck.TICK.finditer(line):
        tok = m.group(1).strip()
        path, sec = split_place(tok)
        if not refcheck.looks_like_path(path.split()[0] if path else ""):
            continue
        yield tok, path.split()[0], sec


def check(files, canon: Path = CANON) -> int:
    places, copies = load_canon(canon)
    bad = 0
    for f in files:
        p = Path(f).resolve()
        fence = False
        hits = []
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            for shown, path, sec in addresses(line):
                if not_norm(path):
                    hits.append(f"{i}: НЕ НОРМА `{shown}`")
                    continue
                if not sec:
                    continue
                key = (path, sec)
                if key in copies and key not in places:
                    ids = "; ".join(f"{i_} «{nm[:50]}» → {pl}" for i_, pl, nm in copies[key][:3])
                    hits.append(f"{i}: ПРОВЕРИТЬ `{shown}` — копия нормы: {ids}")
        errs = sum(1 for h in hits if "НЕ НОРМА" in h)
        bad += errs
        print(f"{p.name}: не на норму {errs}, проверить {len(hits) - errs}")
        for h in hits:
            print("  " + h)
    return 1 if bad else 0


def selftest() -> int:
    """Временные таблица и карта: канон, копия, адрес в материале к разбору, в журнале ресерча и в журнале сборки."""
    import contextlib
    import io
    import tempfile
    ok = fail = 0

    def ok_if(name, cond):
        nonlocal ok, fail
        print(("OK   " if cond else "FAIL ") + name)
        ok, fail = ok + bool(cond), fail + (not cond)

    with tempfile.TemporaryDirectory(prefix="mapcheck-") as td:
        d = Path(td)
        canon = d / "canon.tsv"
        canon.write_text("norm\tplace\tstatus\tid\tcopies\n"
                         "Норма А\tux/01-a/01-a.md §2\tзакрыто\tGL-01\tui/02-b/03-c.md §4; site/README.md §Карта\n"
                         "Норма Б\tui/02-b/03-c.md §4\tзакрыто\tGL-02\t—\n", encoding="utf-8")
        not_norm_examples = {row["label"]: row["example"] for row in refcheck.trace_rows("not-norm")}
        cases = {
            "канон": "Смотри `ux/01-a/01-a.md §2`.",
            "копия": "Смотри `site/README.md §Карта`.",
            "копия и канон": "Смотри `ui/02-b/03-c.md §4`.",
            "файл целиком": "Вход — `site/README.md`.",
        }
        cases.update({label: f"Адрес — `{ex}`." for label, ex in not_norm_examples.items()})
        res = {}
        for name, line in cases.items():
            f = d / "map.md"
            f.write_text("# Карта\n\n" + line + "\n```\n`site/99-raw/в-блоке.md`\n```\n", encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = check([f], canon)
            res[name] = (rc, buf.getvalue())
        ok_if("канон — без находок", res["канон"][0] == 0 and "проверить 0" in res["канон"][1])
        ok_if("копия — ПРОВЕРИТЬ с id и каноном", res["копия"][0] == 0 and "ПРОВЕРИТЬ" in res["копия"][1]
              and "GL-01" in res["копия"][1] and "ux/01-a/01-a.md §2" in res["копия"][1])
        ok_if("место, которое и канон другой нормы, — без находки", "ПРОВЕРИТЬ" not in res["копия и канон"][1])
        ok_if("адрес файла целиком не сверяется с копиями", "ПРОВЕРИТЬ" not in res["файл целиком"][1])
        for name in not_norm_examples:
            ok_if(f"{name} — НЕ НОРМА, код 1", res[name][0] == 1 and "НЕ НОРМА" in res[name][1])
        ok_if("блок кода не проверяется", all("в-блоке" not in out for _, out in res.values()))
    print(f"selftest: {ok} OK, {fail} FAIL")
    return 0 if not fail else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="файлы карты (обычно kb/INDEX.md)")
    ap.add_argument("--canon", type=Path, default=CANON, help="таблица «норма → место» (по умолчанию kb/common/canon.tsv)")
    ap.add_argument("--selftest", action="store_true", help="самопроверка во временной папке, без сети")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.files:
        ap.error("назовите файл карты или --selftest")
    return check(args.files, args.canon)


if __name__ == "__main__":
    sys.exit(main())
