#!/usr/bin/env python3
"""Перенос собранного дерева в шаблон (агент C): только после зелёного check и с защитой от ручных правок. Модуль migrate.py.

Управляемые пути: `.claude/skills/design-deep-dive/`, `research/design-build/` и абзац-исключение в
`.claude/rules/forward-only.md`. Отметка прошлого переноса — `research/design-build/phase-3/migration/applied.json`
(sha256 и бит исполнения каждого записанного файла). Git — только чтение: rev-parse, symbolic-ref, status, ls-files,
check-ignore; коммитит оркестратор.

Отказ (код 2, в репозитории ничего не меняется), если:
  - check не зелёный или дерево .staging не то, что проверено (отпечаток);
  - путь — не корень git-репозитория; текущая ветка — не feat/design-deep-dive;
  - в рабочем дереве есть незакоммиченные изменения, кроме записанного прошлым переносом (совпадает с отметкой);
  - управляемые пути не пусты, а отметки нет; или они расходятся с отметкой (правили руками) — кроме расхождений, которые
    совпадают с новой сборкой (удалённый файл, которого нет и в .staging; файл, равный новой версии);
  - в управляемых путях есть файл, которого нет в .staging (перенос ничего не удаляет);
  - в forward-only.md заголовок абзаца-исключения есть, а текст абзаца другой.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import mig_plan as MP                                  # noqa: E402
from mig_plan import RE, sha256_bytes                  # noqa: E402

BRANCH = "feat/design-deep-dive"


class Refusal(Exception):
    def __init__(self, title, items=()):
        super().__init__(title)
        self.title = title
        self.items = list(items)


def git(repo, *args, stdin=None, ok=(0,)):
    r = subprocess.run(["git", "-C", str(repo), *args], input=stdin, capture_output=True)
    if r.returncode not in ok:
        raise MP.BuildError(f"git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r


def file_state(p):
    data = Path(p).read_bytes()
    return {"sha256": sha256_bytes(data), "x": bool(os.stat(p).st_mode & 0o111)}


def staged_tree(staging):
    out = {}
    for dirpath, dirnames, filenames in os.walk(staging):
        dirnames.sort()
        for f in sorted(filenames):
            p = Path(dirpath) / f
            if p.is_symlink():
                raise MP.BuildError(f".staging: симлинк {p}")
            out[p.relative_to(staging).as_posix()] = p
    return out


def repo_managed(repo, dirs, mark_rel):
    """Файлы управляемых папок в репозитории: отслеживаемые и неотслеживаемые, кроме спрятанных .gitignore."""
    r = git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *dirs)
    names = sorted({n for n in r.stdout.decode("utf-8").split("\0") if n})
    return {n: repo / n for n in names if n != mark_rel and (repo / n).is_file() and not (repo / n).is_symlink()}


def dirty_paths(repo):
    r = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    parts = r.stdout.decode("utf-8").split("\0")
    out, i = [], 0
    while i < len(parts):
        e = parts[i]
        i += 1
        if not e:
            continue
        status, path = e[:2], e[3:]
        out.append((status, path))
        if "R" in status or "C" in status:            # у переименования следом идёт старый путь
            if i < len(parts) and parts[i]:
                out.append((status, parts[i]))
            i += 1
    return out


def run(repo, dry_run=False, staging=MP.STAGING):
    repo = Path(repo).resolve()
    staging = Path(staging)
    rules = RE.load_rules()
    skill, journal = rules.skill, rules.journal_root
    mark_rel = f"{journal}/phase-3/migration/applied.json"
    managed_dirs = [skill, journal]
    report = {"repo": str(repo), "dry_run": dry_run, "branch": BRANCH}
    try:
        # 1) только после зелёного check этого самого дерева
        cj = MP.REPORTS / "check.json"
        if not cj.exists():
            raise Refusal("нет reports/check.json — сначала check")
        chk = json.loads(cj.read_text(encoding="utf-8"))
        if not (chk.get("ok") and chk.get("complete")):
            raise Refusal("check не зелёный: " + ", ".join(chk.get("hard_failed", []) + chk.get("not_run", [])))
        fp, n_files, _ = MP.tree_fingerprint(staging)
        if fp != chk.get("fingerprint"):
            raise Refusal(f"дерево .staging изменилось после check: {fp[:16]}… ≠ {str(chk.get('fingerprint'))[:16]}… — "
                          "повторить check")
        report["fingerprint"] = fp
        # входы с тех пор не менялись: иначе в шаблон ушёл бы устаревший журнал (или база разошлась с заморозкой)
        plan = MP.Plan(template=MP.built_template())
        if plan.fingerprint() != fp:
            now = {it.dest: sha256_bytes(it.data) for it in plan.items.values()}
            was = {p: sha256_bytes(q.read_bytes()) for p, q in staged_tree(staging).items()}
            diff = sorted(p for p in set(now) | set(was) if now.get(p) != was.get(p))
            raise Refusal("входы сборки изменились после build и check (журнал _skill-build/, правила, код, overlay) — "
                          "повторить build и check", diff)
        # 2) репозиторий и ветка
        top = git(repo, "rev-parse", "--show-toplevel", ok=(0, 128))
        if top.returncode != 0 or Path(top.stdout.decode().strip()).resolve() != repo:
            raise Refusal(f"{repo} — не корень git-репозитория")
        br = git(repo, "symbolic-ref", "--short", "-q", "HEAD", ok=(0, 1)).stdout.decode().strip()
        if br != BRANCH:
            raise Refusal(f"текущая ветка {br or '(detached HEAD)'}, нужна {BRANCH}")
        # 3) состояние управляемых путей против отметки
        staged = staged_tree(staging)
        staged_managed = {p: q for p, q in staged.items() if any(p.startswith(d + "/") for d in managed_dirs)}
        other = sorted(p for p in staged if p not in staged_managed and p != MP.FORWARD_ONLY)
        if other:
            raise MP.BuildError(f".staging: файлы вне управляемых путей: {other[:5]}")
        if mark_rel in staged_managed:
            raise MP.BuildError(".staging содержит applied.json — отметку пишет только apply")
        cur = repo_managed(repo, managed_dirs, mark_rel)
        mark_path = repo / mark_rel
        mark = None
        if mark_path.exists():
            try:
                mark = json.loads(mark_path.read_text(encoding="utf-8"))
            except ValueError as e:
                raise Refusal(f"отметка {mark_rel} не читается: {e}")
        state = {p: file_state(q) for p, q in cur.items()}
        new = {p: file_state(q) for p, q in staged_managed.items()}
        diverged, agreed = [], []
        if mark is None:
            if cur:
                raise Refusal(f"управляемые пути не пусты, а отметки {mark_rel} нет — переноса сюда не было или отметку "
                              f"удалили; файлов: {len(cur)}", sorted(cur)[:40])
        else:
            mfiles = mark.get("files", {})
            for p in sorted(set(mfiles) | set(state)):
                was, now, want = mfiles.get(p), state.get(p), new.get(p)
                if was == now:
                    continue
                if now is None:                             # удалён после прошлого переноса
                    (agreed if want is None else diverged).append(f"удалён: {p}")
                elif now == want:                           # добавлен или изменён — ровно как в новой сборке
                    agreed.append(f"{'изменён' if was else 'добавлен'} как в новой сборке: {p}")
                else:
                    diverged.append(f"{'изменён' if was else 'добавлен'} вручную: {p}")
        if diverged:
            raise Refusal("управляемые пути расходятся с отметкой прошлого переноса (правили руками)", diverged)
        extra = sorted(set(cur) - set(staged_managed))
        if extra:
            raise Refusal("в управляемых путях есть файлы, которых нет в .staging (перенос ничего не удаляет) — "
                          "убрать их отдельным осознанным шагом или вернуть в сборку", extra)
        # 4) forward-only.md
        fo_path = repo / MP.FORWARD_ONLY
        if not fo_path.exists():
            raise Refusal(f"нет {MP.FORWARD_ONLY}")
        fo_cur = fo_path.read_text(encoding="utf-8")
        snippet = MP.SNIPPET.read_text(encoding="utf-8")
        try:
            fo_new, fo_action = MP.merge_forward_only(fo_cur, snippet)
        except MP.BuildError as e:
            raise Refusal(str(e))
        fo_staged = (staging / MP.FORWARD_ONLY).read_text(encoding="utf-8")
        report["forward_only"] = {"action": fo_action, "equals_staging": fo_new == fo_staged}
        # 5) рабочее дерево чистое, кроме записанного прошлым переносом
        ours = set()
        if mark is not None:
            ours = {p for p, s in state.items() if mark.get("files", {}).get(p) == s} | {mark_rel}
            if sha256_bytes(fo_cur.encode("utf-8")) == (mark.get("forward_only") or {}).get("sha256_after"):
                ours.add(MP.FORWARD_ONLY)
        dirty = [f"{s} {p}" for s, p in dirty_paths(repo) if p not in ours]
        if dirty:
            raise Refusal("рабочее дерево не чистое (незакоммиченное вне записанного прошлым переносом)", dirty)
    except Refusal as r:
        report.update({"result": "refused", "reason": r.title, "items": r.items[:200]})
        _report(report)
        print(f"apply: ОТКАЗ — {r.title}")
        for x in r.items[:40]:
            print(f"  {x}")
        if len(r.items) > 40:
            print(f"  … ещё {len(r.items) - 40}")
        return 2
    # 6) план записи
    add = sorted(p for p in new if p not in state)
    upd = sorted(p for p in new if p in state and state[p] != new[p])
    same = len(new) - len(add) - len(upd)
    mark_new = {
        "tool": f"{journal}/phase-3/migration/migrate.py",
        "fingerprint": fp,
        "branch": BRANCH,
        "managed": managed_dirs + [MP.FORWARD_ONLY],
        "forward_only": {"path": MP.FORWARD_ONLY, "paragraph_sha256": sha256_bytes(snippet.strip("\n").encode("utf-8")),
                         "sha256_after": sha256_bytes(fo_new.encode("utf-8"))},
        "files": {p: new[p] for p in sorted(new)},
    }
    mark_text = json.dumps(mark_new, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    mark_changes = not mark_path.exists() or mark_path.read_text(encoding="utf-8") != mark_text
    report.update({"result": "dry-run" if dry_run else "applied", "add": len(add), "update": len(upd), "same": same,
                   "forward_only_action": fo_action, "mark": "write" if mark_changes else "same",
                   "agreed_divergences": agreed, "update_list": upd[:100]})
    print(f"apply{' --dry-run' if dry_run else ''}: {repo} ({BRANCH}), дерево {fp[:16]}…")
    print(f"  добавить {len(add)}, обновить {len(upd)}, без изменений {same}; forward-only.md: "
          f"{'дописать абзац' if fo_action == 'append' else 'абзац уже есть'}"
          f"{'' if report['forward_only']['equals_staging'] else ' (итог отличается от .staging: файл в ветке не как в main)'}; "
          f"отметка: {'записать' if mark_changes else 'та же'}")
    for x in agreed:
        print(f"  расхождение с отметкой совпадает с новой сборкой — {x}")
    if dry_run:
        _report(report)
        return 0
    # 7) запись
    for p in add + upd:
        dst = repo / p
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(staged_managed[p].read_bytes())
        os.chmod(dst, 0o755 if new[p]["x"] else 0o644)
    if fo_action == "append":
        fo_path.write_text(fo_new, encoding="utf-8")
    if mark_changes:
        mark_path.parent.mkdir(parents=True, exist_ok=True)
        mark_path.write_text(mark_text, encoding="utf-8")
    # 8) сверка после записи: управляемые пути = .staging; .gitignore ничего не прячет
    after = {p: file_state(q) for p, q in repo_managed(repo, managed_dirs, mark_rel).items()}
    bad = sorted(p for p in set(after) | set(new) if after.get(p) != new.get(p))
    ign = git(repo, "check-ignore", "-z", "--stdin", stdin="\0".join(sorted(new)).encode("utf-8"), ok=(0, 1))
    hidden = [x for x in ign.stdout.decode("utf-8").split("\0") if x]
    report.update({"verify_mismatch": bad[:50], "gitignored": hidden[:50]})
    _report(report)
    if bad or hidden:
        print(f"apply: записано, но сверка не сошлась — расхождений {len(bad)}, спрятано .gitignore {len(hidden)}")
        for x in (bad + hidden)[:20]:
            print(f"  {x}")
        return 1
    print(f"apply: готово — управляемые пути совпадают с .staging ({len(new)} файлов); коммит — за оркестратором")
    return 0


def _report(report):
    MP.dump_json(MP.REPORTS / "apply-last.json", report)
