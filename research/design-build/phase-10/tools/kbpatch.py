#!/usr/bin/env python3
"""kbpatch — точные замены в md-файлах базы для текстовой зоны Ф10: файл пишется, только если совпали все замены.

Файл замен — модуль Python с словарём `P`: путь файла от `kb/` → список замен. Замена — кортеж:
    ("старое", "новое")            старое должно встретиться в файле ровно один раз
    ("старое", "новое", N)         ровно N раз
    ("re", r"шаблон", "новое")     регулярное выражение (флаги S и M), хотя бы одно совпадение
    ("re", r"шаблон", "новое", N)  ровно N совпадений
Замены одного файла применяются по порядку к уже изменённому тексту. Любая замена не совпала — файл не тронут,
ошибки напечатаны, код выхода 1.

    python3 research/design-build/phase-10/tools/kbpatch.py ФАЙЛ_ЗАМЕН.py [ФАЙЛ_ЗАМЕН.py …] [--dry]
    python3 research/design-build/phase-10/tools/kbpatch.py --selftest
"""
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
KB = HERE.parents[3] / ".claude" / "skills" / "design-deep-dive" / "kb"


def apply(text, edits):
    """→ (новый текст, [ошибки])."""
    errs = []
    for i, e in enumerate(edits):
        if e and e[0] == "re":
            pat, rep = e[1], e[2]
            want = e[3] if len(e) > 3 else None
            new, n = re.subn(pat, rep, text, flags=re.S | re.M)
            if n == 0 or (want is not None and n != want):
                errs.append((i, n, "re:" + pat[:100]))
                continue
            text = new
            continue
        old, new = e[0], e[1]
        want = e[2] if len(e) > 2 else 1
        n = text.count(old)
        if n != want:
            errs.append((i, n, old[:100]))
            continue
        text = text.replace(old, new)
    return text, errs


def run(specfile, root, dry):
    spec = importlib.util.spec_from_file_location("p", specfile)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ok = True
    for rel, edits in mod.P.items():
        f = root / rel
        if not f.is_file():
            print("FAIL", rel, "— файла нет")
            ok = False
            continue
        text, errs = apply(f.read_text(encoding="utf-8"), edits)
        if errs:
            ok = False
            print("FAIL", rel)
            for i, n, o in errs:
                print("   #%d совпадений %d: %r" % (i, n, o))
        else:
            if not dry:
                f.write_text(text, encoding="utf-8")
            print("ok  ", rel, len(edits), "(сухой прогон)" if dry else "")
    return ok


def selftest():
    t, e = apply("a b a", [("b", "c"), ("a", "x", 2)])
    assert (t, e) == ("x c x", []), (t, e)
    t, e = apply("a b a", [("a", "x")])
    assert e and e[0][1] == 2
    t, e = apply("p1 p2", [("re", r"p\d", "q", 2)])
    assert (t, e) == ("q q", [])
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "x.md").write_text("один два\n", encoding="utf-8")
        sp = root / "s.py"
        sp.write_text('P = {"x.md": [("два", "три"), ("нет", "да")]}\n', encoding="utf-8")
        assert run(sp, root, False) is False
        assert (root / "x.md").read_text(encoding="utf-8") == "один два\n"
        sp.write_text('P = {"x.md": [("два", "три")]}\n', encoding="utf-8")
        assert run(sp, root, False) is True
        assert (root / "x.md").read_text(encoding="utf-8") == "один три\n"
    print("selftest: OK")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    if not args:
        print(__doc__)
        sys.exit(2)
    good = True
    for a in args:
        good = run(a, KB, "--dry" in sys.argv) and good
    sys.exit(0 if good else 1)
