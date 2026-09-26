#!/usr/bin/env python3
"""Механические правки кода при переносе в шаблон (фаза 3, агент B) — детерминированно, к нетронутой копии источника.

Правка файла — `patches/<место от корня скилла>.yaml`, например `patches/scripts/site/site_validate.py.yaml` для
`.claude/skills/design-deep-dive/scripts/site/site_validate.py`. Формат (SPEC-code.md §3):

    source: site-research/99-raw/tools/site_validate.py        # от корня app-design
    source_sha256: 42c1…                                       # правка применяется только к этому содержимому
    dest: .claude/skills/design-deep-dive/scripts/site/site_validate.py
    result_sha256: 7f3a…                                       # sha256 результата (пишет --record)
    edits:                                                     # по порядку, каждая к результату предыдущих
      - code: root                                             # код правки (колонка patches в tools-map.tsv)
        find: ROOT = HERE.parents[1]                           # строка или список строк (склеиваются через \\n)
        replace: ROOT = kbpaths.kb("site")
        count: 1                                               # сколько раз find встречается — ровно столько (по умолчанию 1)
        note: …                                                # зачем (необязательно)

Правка, которая не нашла find ровно count раз, источник с другим sha256, результат с другим result_sha256 — ошибка
(PatchError, код выхода 1), а не молчание. Замена — str.replace всех непересекающихся вхождений.

  python3 apply_patches.py --check                # применить все правки в памяти, сверить счётчики и sha256
  python3 apply_patches.py --record               # то же + записать result_sha256 в файлы правок
  python3 apply_patches.py --apply-to DIR         # записать результаты в DIR/<dest> (временная раскладка)
  python3 apply_patches.py --diff DEST            # unified diff источник → результат для одного места
  python3 apply_patches.py --list                 # место, число правок, коды

Для migrate.py (импорт): load_patch, patch_file_for, apply_text, apply_patch, iter_patches, PatchError, CODES.
Только stdlib + PyYAML (как rules_eval.py).
"""
import argparse
import difflib
import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent                 # _skill-build/phase-3/migration
APP = HERE.parents[2]                                  # корень app-design (источник)
PATCHES = HERE / "patches"
SKILL = ".claude/skills/design-deep-dive"

CODES = {
    "boot": "подключение scripts/lib/kbpaths.py (sys.path + import kbpaths)",
    "root": "корень базы или утилиты от __file__ → kbpaths.kb() / kbpaths.scripts()",
    "kb": "пути в соседние базы (<APP>/<база>-research/…) → kbpaths.kb('<база>')",
    "imp": "импорты соседей и модулей опытов (sys.path на старые папки) → место в scripts/",
    "abs": "абсолютные пути /home/mm/… (прочие)",
    "lock": "блокировки браузера и очереди → kbpaths.lock_path() ($DDD_HOME/locks)",
    "out": "каталоги выходов → kbpaths.out() ($DDD_HOME/out)",
    "cache": "каталоги кэшей → kbpaths.cache() ($DDD_HOME/cache)",
    "venv": "Python окружения (venv-* в 99-raw/tools) → kbpaths.python()",
    "bin": "бинарники (blender, ffmpeg, brave, node, 99-raw/tools/bin) → kbpaths.which() и обёртки",
    "node": "npm-зависимости (99-raw/tools/node/node_modules) → kbpaths.node_modules() / node_env()",
    "data": "данные кода, уехавшие в scripts/<база>/data/ или kb/<база>/99-raw/ → kbpaths.data() / kbpaths.kb()",
    "model": "модели ONNX (99-raw/tools/models) → kbpaths.models()",
    "key": "ключи API — только из переменных окружения",
}


class PatchError(Exception):
    pass


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _text(v, where):
    if isinstance(v, str):
        return v
    if isinstance(v, list) and all(isinstance(x, str) for x in v):
        return "\n".join(v)
    raise PatchError(f"{where}: find/replace — строка или список строк")


def patch_file_for(dest):
    """Файл правки для места назначения (от корня шаблона или от корня скилла)."""
    d = str(dest)
    if d.startswith(SKILL + "/"):
        d = d[len(SKILL) + 1:]
    return PATCHES / (d + ".yaml")


def load_patch(path):
    import yaml
    path = Path(path)
    try:
        p = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        raise PatchError(f"{path}: не YAML ({e})")
    if not isinstance(p, dict):
        raise PatchError(f"{path}: ожидается словарь")
    for k in ("source", "source_sha256", "dest", "edits"):
        if k not in p:
            raise PatchError(f"{path}: нет поля {k}")
    if patch_file_for(p["dest"]) != path.resolve() and patch_file_for(p["dest"]) != path:
        raise PatchError(f"{path}: имя файла правки не соответствует dest {p['dest']}")
    if not isinstance(p["edits"], list) or not p["edits"]:
        raise PatchError(f"{path}: edits — непустой список")
    for i, e in enumerate(p["edits"], 1):
        where = f"{path.name} правка {i}"
        if not isinstance(e, dict) or "find" not in e or "replace" not in e:
            raise PatchError(f"{where}: нужны find и replace")
        if e.get("code") not in CODES:
            raise PatchError(f"{where}: неизвестный код {e.get('code')!r} (есть: {', '.join(CODES)})")
        e["find"] = _text(e["find"], where)
        e["replace"] = _text(e["replace"], where)
        if not e["find"]:
            raise PatchError(f"{where}: пустой find")
        e["count"] = int(e.get("count", 1))
        if e["count"] < 1:
            raise PatchError(f"{where}: count ≥ 1")
    p["_path"] = path
    return p


def apply_text(text, patch):
    """Применить правки к тексту. Возвращает (текст, [число замен по правкам]). Несовпадение счётчика — PatchError."""
    counts = []
    for i, e in enumerate(patch["edits"], 1):
        n = text.count(e["find"])
        if n != e["count"]:
            first = e["find"].split("\n", 1)[0][:90]
            raise PatchError(f"{patch['dest']}: правка {i} ({e['code']}) — найдено {n}, ожидалось {e['count']}: {first!r}")
        text = text.replace(e["find"], e["replace"])
        counts.append(n)
    return text, counts


def apply_patch(patch, source_root=APP, check_result=True):
    """Прочитать источник, сверить sha256, применить правки; вернуть байты результата."""
    src = Path(source_root) / patch["source"]
    raw = src.read_bytes()
    got = sha256_bytes(raw)
    if got != patch["source_sha256"]:
        raise PatchError(f"{patch['dest']}: sha256 источника {got[:12]}… ≠ {patch['source_sha256'][:12]}… ({patch['source']})")
    text, _ = apply_text(raw.decode("utf-8"), patch)
    res = text.encode("utf-8")
    if check_result and patch.get("result_sha256") and sha256_bytes(res) != patch["result_sha256"]:
        raise PatchError(f"{patch['dest']}: sha256 результата {sha256_bytes(res)[:12]}… ≠ записанного "
                         f"{patch['result_sha256'][:12]}…")
    return res


def iter_patches(root=PATCHES):
    return sorted(Path(root).rglob("*.yaml"))


def _record(path, sha):
    """Записать result_sha256 в файл правки (строка сразу после source_sha256; остальное — как есть)."""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    lines = [ln for ln in lines if not ln.startswith("result_sha256:")]
    for i, ln in enumerate(lines):
        if ln.startswith("source_sha256:"):
            lines.insert(i + 1, f"result_sha256: {sha}")
            break
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Механические правки кода при переносе (агент B)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="применить в памяти и сверить")
    g.add_argument("--record", action="store_true", help="сверить и записать result_sha256")
    g.add_argument("--apply-to", metavar="DIR", help="записать результаты в DIR/<dest>")
    g.add_argument("--diff", metavar="DEST", help="diff источник → результат")
    g.add_argument("--list", action="store_true", help="перечень правок")
    ap.add_argument("--source-root", default=str(APP), help="корень источника (по умолчанию app-design)")
    a = ap.parse_args()

    if a.diff:
        p = load_patch(patch_file_for(a.diff))
        src = (Path(a.source_root) / p["source"]).read_text(encoding="utf-8")
        res = apply_patch(p, a.source_root, check_result=False).decode("utf-8")
        sys.stdout.writelines(difflib.unified_diff(src.splitlines(True), res.splitlines(True),
                                                   "a/" + p["source"], "b/" + p["dest"]))
        return 0
    errors, total_files, total_edits, total_repl = [], 0, 0, 0
    for path in iter_patches():
        try:
            p = load_patch(path)
            if a.list:
                codes = sorted({e["code"] for e in p["edits"]})
                print(f"{p['dest']}\t{len(p['edits'])}\t{','.join(codes)}")
                continue
            res = apply_patch(p, a.source_root, check_result=not a.record)
            src_text = (Path(a.source_root) / p["source"]).read_text(encoding="utf-8")
            _, counts = apply_text(src_text, p)
            total_files += 1
            total_edits += len(p["edits"])
            total_repl += sum(counts)
            if a.record:
                _record(path, sha256_bytes(res))
            if a.apply_to:
                out = Path(a.apply_to) / p["dest"]
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(res)
        except PatchError as e:
            errors.append(str(e))
        except OSError as e:
            errors.append(f"{path}: {e}")
    if a.list:
        return 0
    for e in errors:
        print("ERROR", e)
    print(f"правок-файлов: {total_files}, правок: {total_edits}, замен: {total_repl}, ошибок: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
