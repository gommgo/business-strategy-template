#!/usr/bin/env python3
"""Перенос базы design-deep-dive в шаблон business-strategy-template (фаза 3, агент C).

  python3 migrate.py build                        # дерево → .staging/ (+ reports/build.json, rewrites.tsv), отпечаток
  python3 migrate.py check [--no-smoke]           # проверки SPEC §8 и SPEC-code → reports/check.json, check.txt
  python3 migrate.py apply --repo PATH [--dry-run]  # .staging → шаблон; только после зелёного check, с защитой
  python3 migrate.py fingerprint [DIR]            # отпечаток дерева (по умолчанию .staging)

Входы только читаются: замороженная база, правила A (manifest-rules.yaml, rules_eval.py), код B (tools-map.tsv, patches/,
apply_patches.py, code_stage.py), overlay/, живой журнал _skill-build/, forward-only.md шаблона из ветки main. Пишет:
.staging/ (пересоздаётся целиком), .staging-smoke/ (окружение смоука), reports/; apply — только управляемые пути
репозитория. Коды выхода: 0 — готово; 1 — ошибка или жёсткий провал check; 2 — отказ apply или check не завершён.
Подробно — MIGRATE.md рядом.
"""
import argparse
import csv
import shutil
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mig_plan as MP                                  # noqa: E402


def _safe_rmtree(path):
    """Пересоздание своей временной папки: только .staging / .staging-apply внутри phase-3/migration."""
    path = Path(path)
    if path.is_symlink() or path.parent.resolve() != HERE or path.name not in (".staging", ".staging-apply"):
        raise MP.BuildError(f"отказ удалять {path}: не своя временная папка")
    if path.exists():
        shutil.rmtree(path)


def cmd_build(a):
    t0 = time.time()
    plan = MP.Plan(template=a.template)
    fp = plan.fingerprint()
    _safe_rmtree(MP.STAGING)
    MP.STAGING.mkdir()
    plan.write(MP.STAGING)
    fp_disk, n, size = MP.tree_fingerprint(MP.STAGING)
    if fp_disk != fp:
        raise MP.BuildError(f"записанное дерево {fp_disk[:16]}… ≠ плану {fp[:16]}…")
    s = plan.summary()
    MP.REPORTS.mkdir(exist_ok=True)
    MP.dump_json(MP.REPORTS / "build.json", {
        "fingerprint": fp, "files": n, "bytes": size, "template": str(plan.template), "template_ref": plan.template_ref,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "seconds": round(time.time() - t0, 1), "inputs": MP.inputs_digest(plan), **s})
    with open(MP.REPORTS / "rewrites.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["source", "line", "start", "end", "kind", "raw", "new", "target", "dest"])
        w.writerows(plan.rewrites())
    k = s["kinds"]
    rw = s["rewrite"]
    print(f"build: {n} файлов, {size / 1e6:.1f} МБ → {MP.STAGING.relative_to(HERE)}/ за {time.time() - t0:.0f} с")
    print(f"  виды: copy {k.get('copy', 0)}, rewritten {k.get('rewritten', 0)}, patched {k.get('patched', 0)}, "
          f"generated {k.get('generated', 0)}; псевдонимов (без файла) {k.get('alias', 0)}")
    print(f"  части: " + ", ".join(f"{p} {v['files']}" for p, v in s["parts"].items()))
    print(f"  пути: переписано {rw['tokens']} токенов в {rw['files_changed']} файлах из {rw['zone_files']} зоны; "
          f"не разрешаются после — {rw['not_resolving']}")
    for wmsg in s["warnings"]:
        print(f"  предупреждение: {wmsg}")
    print(f"отпечаток дерева: {fp}")
    return 0


def cmd_check(a):
    import mig_check
    root = Path(a.root) if a.root else MP.STAGING
    rep = mig_check.run(root, smoke=not a.no_smoke, template=a.template)
    print()
    print((MP.REPORTS / "check.txt").read_text(encoding="utf-8").split("\n\n", 1)[0])
    print(f"итог: {'ЗЕЛЁНЫЙ' if rep['ok'] else 'не зелёный'}; жёстких провалов {len(rep['hard_failed'])}"
          f"{' (' + ', '.join(rep['hard_failed']) + ')' if rep['hard_failed'] else ''}; не выполнено "
          f"{len(rep['not_run'])}; предупреждений {len(rep['warnings'])}"
          f"{' (' + ', '.join(rep['warnings']) + ')' if rep['warnings'] else ''} — reports/check.txt")
    if rep["hard_failed"]:
        return 1
    return 0 if rep["ok"] else 2


def cmd_apply(a):
    import mig_apply
    return mig_apply.run(a.repo, dry_run=a.dry_run)


def cmd_fingerprint(a):
    root = Path(a.dir) if a.dir else MP.STAGING
    fp, n, size = MP.tree_fingerprint(root)
    print(f"{fp}  {n} файлов, {size / 1e6:.1f} МБ  {root}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="собрать дерево в .staging/")
    b.add_argument("--template", default=None, help="шаблон (по умолчанию roots.template из manifest-rules.yaml)")
    c = sub.add_parser("check", help="проверки дерева")
    c.add_argument("--root", default="", help="дерево (по умолчанию .staging)")
    c.add_argument("--no-smoke", action="store_true", help="без смоука утилит (check тогда не зелёный: не завершён)")
    c.add_argument("--template", default=None)
    p = sub.add_parser("apply", help="перенести .staging в шаблон")
    p.add_argument("--repo", required=True, help="корень репозитория шаблона (ветка feat/design-deep-dive)")
    p.add_argument("--dry-run", action="store_true", help="только проверить защиту и показать план записи")
    f = sub.add_parser("fingerprint", help="отпечаток дерева")
    f.add_argument("dir", nargs="?", default="")
    a = ap.parse_args()
    try:
        return {"build": cmd_build, "check": cmd_check, "apply": cmd_apply, "fingerprint": cmd_fingerprint}[a.cmd](a)
    except MP.BuildError as e:
        print(f"{a.cmd}: ОШИБКА — {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
