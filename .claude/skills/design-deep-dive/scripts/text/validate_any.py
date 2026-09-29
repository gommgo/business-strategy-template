#!/usr/bin/env python3
"""validate_any.py — проверки смысла (схема + смысл) для meaning и иерархий сообщений проекта, вне примеров базы.

validate_meaning.py без аргументов проверяет примеры базы; эта обёртка вызывает его функции (schema_errors,
semantic_meaning, semantic_hierarchy) на любом файле — для выхода промтов P2 (смысл) и P3 (иерархия), включая
предупреждения «обещание из допущения».

Запуск (Python окружения скилла, нужен jsonschema):
    python3 scripts/text/validate_any.py FILE.yaml [FILE2.yaml …]
Тип файла — по ключу meaning_version или hierarchy_version. Код выхода: 0 — ошибок нет, 1 — есть.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate_meaning as v  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        print(__doc__)
        sys.exit(1)
    vm = Draft202012Validator(v.load(os.path.join(v.SM, "meaning.schema.yaml")))
    vh = Draft202012Validator(v.load(os.path.join(v.SM, "message-hierarchy.schema.yaml")))
    total = 0
    for p in files:
        d = v.load(p)
        if "meaning_version" in d:
            se = v.schema_errors(vm, d)
            e, w, info = v.semantic_meaning(p, d)
            kind = "meaning"
        elif "hierarchy_version" in d:
            se = v.schema_errors(vh, d)
            e, w, info = v.semantic_hierarchy(p, d)
            kind = "hierarchy"
        else:
            print(f"{p}: не meaning и не hierarchy")
            total += 1
            continue
        total += len(se) + len(e)
        print(f"[{kind}] {os.path.basename(p)}: схема — {len(se)} ошибок; смысл — {len(e)} ошибок, {len(w)} предупр.; {info}")
        for x in se + e:
            print("  ОШИБКА:", x)
        for x in w:
            print("  предупреждение:", x)
    print(f"ИТОГ: ошибок {total}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
