#!/usr/bin/env python3
"""Проверки собранного дерева (агент C): SPEC §8, SPEC-code §10 п. 4, SKILL-MAP §5. Модуль migrate.py.

Жёсткие проверки (провал → код выхода 1): источник не менялся, правки кода, дерево = план, состав (A, B, overlay, журнал,
path-map в обе стороны), запретное и мусор, файлы-инструкции (и в журнале — Р110), секреты, ссылки на перенесённое (0 битых),
короткие адреса, идентификаторы, калибровка, места назначения (.gitignore, симлинки), /home/mm в scripts/, forward-only.md,
смоук утилит (0 FAIL) и неизменность дерева после смоука. Базовые числа (ссылки на непереносимое, неразрешимые, совпадение
с scan-rewrites.tsv, размер) — предупреждения с цифрами. Не выполнилось обязательное (смоук, .gitignore) — код 2.
"""
import csv
import json
import os
import posixpath
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import mig_plan as MP                                  # noqa: E402
from mig_plan import APP, RE, inv, sha256_bytes        # noqa: E402

SMOKE_DIR = HERE / ".staging-smoke"                   # окружение и сырые результаты смоука (временная папка, в журнал не идёт)
SMOKE_TAG = "staging"
MIN_MEM_GB = 3.0
ACCEPTED_MB = (66.0, 68.0)                             # Р111: ≈ 66–68 МБ, ≈ 1,7 тыс. файлов
ACCEPTED_FILES = 1700
MD_LINK_ANY = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")


class Result:
    def __init__(self):
        self.checks = []

    def add(self, cid, level, ok, summary, **details):
        """level: hard | warn | info; ok: True | False | None (не выполнено)."""
        self.checks.append({"id": cid, "level": level, "ok": ok, "summary": summary, **details})
        mark = {True: "ok ", False: "FAIL" if level == "hard" else "warn", None: "n/a "}[ok]
        print(f"  [{mark}] {cid}: {summary}", flush=True)

    @property
    def hard_failed(self):
        return [c for c in self.checks if c["level"] == "hard" and c["ok"] is False]

    @property
    def not_run(self):
        return [c for c in self.checks if c["level"] == "hard" and c["ok"] is None]

    @property
    def warnings(self):
        return [c for c in self.checks if c["level"] == "warn" and c["ok"] is False]


# ---------------------------------------------------------------- дерево на диске

def scan_disk(root):
    files, links = {}, []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for d in list(dirnames):
            if (Path(dirpath) / d).is_symlink():
                links.append((Path(dirpath) / d).relative_to(root).as_posix())
        for f in sorted(filenames):
            p = Path(dirpath) / f
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                links.append(rel)
                continue
            data = p.read_bytes()
            files[rel] = {"sha": sha256_bytes(data), "x": bool(p.stat().st_mode & 0o111), "size": len(data)}
    dirs = set()
    for f in files:
        d = f
        while "/" in d:
            d = d.rsplit("/", 1)[0]
            if d in dirs:
                break
            dirs.add(d)
    return files, dirs, links


def mem_available_gb():
    try:
        for ln in open("/proc/meminfo"):
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1]) / 1024 / 1024
    except OSError:
        pass
    return None


def text_of(root, rel):
    return RE.read_text(Path(root) / rel)


# ---------------------------------------------------------------- проверки

def check_freeze(res):
    r = subprocess.run([sys.executable, "-B", str(APP / MP.BUILD_REL / "tools" / "freeze.py"), "--verify"],
                       capture_output=True, text=True)
    counts = dict(re.findall(r"^(добавлено|удалено|изменено): (\d+)", r.stdout, re.M))
    ok = r.returncode == 0 and all(v == "0" for v in counts.values()) and len(counts) == 3
    res.add("freeze", "hard", ok, "источник не менялся с заморозки: " + ", ".join(f"{k} {v}" for k, v in counts.items()),
            output=r.stdout.strip().splitlines()[:30])


def check_patches(res):
    r = subprocess.run([sys.executable, "-B", str(HERE / "apply_patches.py"), "--check"], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    res.add("patches", "hard", r.returncode == 0, f"apply_patches.py --check: {last}",
            errors=[ln for ln in r.stdout.splitlines() if ln.startswith("ERROR")][:30])


def check_fidelity(res, plan, disk):
    planned = {it.dest: it for it in plan.items.values()}
    missing = sorted(d for d in planned if d not in disk)
    extra = sorted(d for d in disk if d not in planned)
    changed = sorted(d for d, it in planned.items() if d in disk and
                     (disk[d]["sha"] != sha256_bytes(it.data) or disk[d]["x"] != bool(it.mode & 0o111)))
    ok = not (missing or extra or changed)
    res.add("fidelity", "hard", ok, f"дерево = план из текущих входов: нет {len(missing)}, лишних {len(extra)}, "
            f"других {len(changed)} (из {len(planned)})", missing=missing[:30], extra=extra[:30], changed=changed[:30])


def read_path_map(root, plan):
    p = Path(root) / plan.path_map_dest
    if not p.exists():
        return None
    return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))


def check_composition(res, plan, disk, root):
    problems = []
    info = {}
    skill, jr = plan.skill, plan.journal_root
    pm = read_path_map(root, plan)
    if pm is None:
        res.add("composition", "hard", False, "нет path-map.tsv")
        return
    by_src = defaultdict(list)
    for r in pm:
        by_src[r["source"]].append(r)
    # 1) path-map ↔ дерево в обе стороны
    kinds_ok = {"copy", "rewritten", "patched", "generated", "alias"}
    dest_rows = Counter(r["dest"] for r in pm if r["kind"] != "alias")
    for r in pm:
        if r["kind"] not in kinds_ok:
            problems.append(f"path-map: вид {r['kind']!r} ({r['dest']})")
        if r["dest"] not in disk:
            problems.append(f"path-map: строка на несуществующий файл {r['dest']} ({r['kind']})")
        elif r["kind"] == "copy" and r["sha256"] != disk[r["dest"]]["sha"]:
            problems.append(f"path-map: copy, но sha256 файла ≠ источника: {r['dest']}")
    for d in disk:
        if dest_rows[d] != 1:
            problems.append(f"path-map: у файла {d} строк {dest_rows[d]} (нужна одна)")
    info["path_map_rows"] = len(pm)
    info["path_map_kinds"] = dict(Counter(r["kind"] for r in pm))
    # sha256 источника у переписанных и правленых — как в заморозке / на диске
    for r in pm:
        if r["kind"] in ("rewritten", "patched") or (r["kind"] == "alias"):
            want = plan.frozen_sha(r["source"])
            if want is None and r["source"].startswith(MP.BUILD_REL + "/"):
                want = sha256_bytes((APP / r["source"]).read_bytes())
            if want and r["sha256"] != want:
                problems.append(f"path-map: sha256 источника {r['source']} ≠ заморозки")
    # 2) содержимое — expected-content.tsv агента A (без журнала)
    exp = [r for r in csv.DictReader(open(MP.EXPECTED, encoding="utf-8"), delimiter="\t")]
    exp_content = [r for r in exp if r["purpose"] != "journal"]
    fresh = {(e.source, e.dest, e.kind, e.sha256) for e in plan.content}
    listed = {(r["source"], r["dest"], r["kind"], r["sha256"]) for r in exp_content}
    if fresh != listed:
        problems.append(f"expected-content.tsv расходится с правилами: только в правилах {len(fresh - listed)}, "
                        f"только в списке {len(listed - fresh)} — перезапустить rules_eval.py")
    n_copy = n_alias = 0
    for r in exp_content:
        rows = [x for x in by_src.get(r["source"], []) if not x["dest"].startswith(jr + "/")]
        if r["kind"] == "alias":
            n_alias += 1
            if not any(x["kind"] == "alias" and x["dest"] == r["dest"] for x in rows):
                problems.append(f"псевдоним {r['source']} → {r['dest']}: нет строки alias в path-map")
            continue
        n_copy += 1
        tm = plan.tm.get(r["source"])
        dest = tm["dest"] if tm and tm["verdict"] in ("take", "adapt") else r["dest"]
        row = next((x for x in rows if x["dest"] == dest), None)
        if dest not in disk or row is None:
            problems.append(f"содержимое не на месте: {r['source']} → {dest}")
            continue
        if row["sha256"] != r["sha256"]:
            problems.append(f"sha256 источника {r['source']} в path-map ≠ expected-content")
        if row["kind"] == "copy" and disk[dest]["sha"] != r["sha256"]:
            problems.append(f"копия {dest} не равна источнику")
    info["content"] = {"copies": n_copy, "aliases": n_alias}
    # 3) код — tools-map.tsv агента B
    n_take = n_adapt = n_dup = 0
    for tr in plan.tm_rows:
        src, dest, v = tr["source"], tr["dest"], tr["verdict"]
        rows = [x for x in by_src.get(src, []) if not x["dest"].startswith(jr + "/")]
        if v == "take":
            n_take += 1
            want = plan.frozen_sha(src) or sha256_bytes((APP / src).read_bytes())
            if dest not in disk or disk[dest]["sha"] != want:
                problems.append(f"код take: {dest} нет или не равен источнику")
        elif v == "adapt":
            n_adapt += 1
            patch = MP.AP.load_patch(MP.AP.patch_file_for(dest))
            it = plan.items.get(dest)
            if dest not in disk:
                problems.append(f"код adapt: {dest} нет")
            elif it is not None and it.zone and it.zone["reps"]:
                pass                                           # README утилит: правка + переписывание путей (сверено fidelity)
            elif disk[dest]["sha"] != patch.get("result_sha256"):
                problems.append(f"код adapt: {dest} ≠ result_sha256 правки")
            if not any(x["kind"] == "patched" and x["dest"] == dest for x in rows):
                problems.append(f"код adapt: нет строки patched для {dest}")
        elif tr["canonical"].startswith("dup-of:") and dest:
            n_dup += 1
            if not any(x["kind"] == "alias" and x["dest"] == dest for x in rows):
                problems.append(f"дубль кода {src}: нет строки alias → {dest}")
        elif rows:
            problems.append(f"код skip без места, но в дереве: {src}")
    handoff = [r["source"] for r in csv.DictReader(open(MP.SCAN_HANDOFF, encoding="utf-8"), delimiter="\t")]
    lost = [s for s in handoff if s not in plan.tm]
    if lost:
        problems.append(f"передача A → B: {len(lost)} файлов без строки tools-map")
    info["code"] = {"take": n_take, "adapt": n_adapt, "aliases": n_dup, "handoff": f"{len(handoff) - len(lost)}/{len(handoff)}"}
    # 4) overlay
    n_ov = 0
    for p in plan.overlay_files:
        dest = p.relative_to(MP.OVERLAY).as_posix()
        n_ov += 1
        if dest not in disk or disk[dest]["sha"] != sha256_bytes(p.read_bytes()):
            problems.append(f"overlay: {dest} нет или отличается")
    info["overlay"] = n_ov
    # 5) журнал: зеркало живого _skill-build/ (без исключений §6 SPEC, Р110 и reports/)
    jdisk = {d for d in disk if d.startswith(jr + "/")} - {f"{jr}/README.md", plan.path_map_dest}
    jplan = {e.dest for e in plan.journal_entries}
    if jdisk != jplan:
        problems.append(f"журнал: лишних {len(jdisk - jplan)}, нет {len(jplan - jdisk)}")
    for e in plan.journal_entries:
        if e.dest in disk and disk[e.dest]["sha"] != sha256_bytes((APP / e.source).read_bytes()):
            problems.append(f"журнал: {e.dest} не равен источнику")
    exp_j = {r["source"] for r in exp if r["purpose"] == "journal"}
    now_j = {e.source for e in plan.journal_entries}
    info["journal"] = {"files": len(jplan), "new_since_expected": len(now_j - exp_j), "gone_since_expected": len(exp_j - now_j),
                       "excluded": plan.info.get("journal_excluded", [])}
    # 6) ничего сверх плана (fidelity) — и сводка
    ok = not problems
    res.add("composition", "hard", ok,
            f"содержимое {n_copy} копий + {n_alias} псевдонима (A); код take {n_take}, adapt {n_adapt}, дублей-псевдонимов "
            f"{n_dup}, передача {info['code']['handoff']} (B); overlay {n_ov}; журнал {len(jplan)}; path-map {len(pm)} строк ↔ "
            f"{len(disk)} файлов" + (f"; проблем {len(problems)}" if problems else ""), problems=problems[:40], **info)


def check_forbidden(res, plan, disk, root):
    pm = read_path_map(root, plan) or []
    bad = [r["source"] for r in pm if re.search(r"(^|/)99-raw/cache/", r["source"]) or r["source"].startswith("kimi-research/")]
    junk_items = [it.dest for it in plan.items.values() if it.cls == "junk" and it.part != "asset-min"]
    asset_junk = [it.dest for it in plan.items.values() if it.cls == "junk" and it.part == "asset-min"]
    skill = plan.skill + "/"
    allowed = {it.dest for it in plan.items.values() if it.part == "asset-min"}
    junk_names = []
    for d in disk:
        if not d.startswith(skill) or d in allowed:
            continue
        rel = Path(d[len(skill):])
        if (set(rel.parts[:-1]) & inv.JUNK_DIRS or any(inv.VENV.match(p) for p in rel.parts[:-1])
                or rel.suffix.lower() in inv.JUNK_EXT or rel.name in inv.JUNK_NAMES):
            junk_names.append(d)
    ok = not (bad or junk_items or junk_names)
    res.add("forbidden", "hard", ok, f"99-raw/cache, kimi, запретное — {len(bad)}; мусор вне asset-min — "
            f"{len(junk_items) + len(junk_names)}; мусор-класс в asset-min — {len(asset_junk)} (допустимо, Р57)",
            forbidden=bad[:20], junk=(junk_items + junk_names)[:20], asset_min_junk=asset_junk)


def check_instructions(res, plan, disk, links):
    hits = []
    for top in (plan.skill, plan.journal_root):
        for d in list(disk) + links:
            if not d.startswith(top + "/"):
                continue
            rel = d[len(top) + 1:]
            if top == plan.skill and rel == "SKILL.md":
                continue                                       # навигатор скилла — наш
            parts = rel.split("/")
            if parts[-1] in RE.INSTR or ".claude" in parts[:-1] or ".git" in parts[:-1] or parts[-1] in (".claude", ".git"):
                hits.append(d)
    res.add("instructions", "hard", not hits, f"файлов-инструкций в kb/, scripts/, assets/ и журнале — {len(hits)} "
            "(кроме навигатора SKILL.md)", hits=hits[:30])


def check_secrets(res, disk, root):
    hits = []
    n = 0
    for d in sorted(disk):
        text = text_of(root, d)
        if text is None:
            continue
        n += 1
        for ln_no, line in enumerate(text.splitlines(), 1):
            for name, rx in RE.SECRETS:
                for m in rx.finditer(line):
                    s = m.group(0)
                    hits.append(f"{d}:{ln_no} {name} {s[:6]}…({len(s)})")
    res.add("secrets", "hard", not hits, f"секретов по шаблонам scan-secrets в {n} текстовых файлах — {len(hits)}",
            hits=hits[:30])


def staged_span(a, b, reps):
    da = sum(len(r.new) - (r.end - r.start) for r in reps if r.end <= a and r.start < r.end)
    db = sum(len(r.new) - (r.end - r.start) for r in reps if r.end <= b and r.start < b)
    return a + da, b + db


def ident_counts(lines, spans_by_line):
    c = Counter()
    for ln, line in enumerate(lines, 1):
        if "-research" not in line:
            continue
        spans = spans_by_line.get(ln, [])
        for m in RE.IDENT.finditer(line):
            cls = RE.ident_class(line, m.start(), m.end(), spans)
            c["path" if cls.startswith("path-") and cls != "path-like-other" else cls] += 1
    return c


def check_links(res, plan, disk, dirs, root):
    """Ссылки из зоны переписывания в дереве на диске: цель перенесена → новый токен разрешается в неё (0 битых);
    короткие адреса; идентификаторы; базовые числа."""
    exists_disk = lambda p: p in disk or p in dirs                      # noqa: E731
    skill = plan.skill
    old_index = {r: inv.build_index(APP / r) for r in plan.bases}
    cats = Counter()
    groups = defaultdict(Counter)                                     # kb — сравнимо с базой A; readme — README утилит (Р112)
    broken, short_broken, ident_bad, retok = [], [], [], []
    after_unresolved = defaultdict(Counter)
    rewritten = 0
    per_base = defaultdict(Counter)
    zone_items = [it for it in plan.files() if it.zone]
    # файлы правил, которых не было в скане A (scan-rules.tsv), — отдельной группой: базовые числа A их не знают
    scanned_rules = {r["rule"] for r in csv.DictReader(open(MP.HERE / "scan-rules.tsv", encoding="utf-8"), delimiter="\t")}
    new_rule_dests = {e.dest for e in plan.content if e.rule not in scanned_rules}
    held_list = []
    for it in zone_items:
        z = it.zone
        staged = text_of(root, it.dest)
        if staged is None:
            broken.append(f"{it.dest}: не читается")
            continue
        staged_lines = staged.splitlines()
        src_lines = z["text"].splitlines()
        reps_by_line = defaultdict(list)
        for r in z["reps"]:
            reps_by_line[r.line].append(r)
        rep_at = {(r.line, r.start, r.end): r for r in z["reps"]}
        grp = ("readme" if not it.dest.startswith(skill + "/kb/") else "new-rule" if it.dest in new_rule_dests else "kb")
        held = {(h["line"], h["start"], h["end"]): h for h in z.get("held", [])}
        toks = plan.scan_tokens(z["text"], z["old_source"], z["research"], it.dest, z["base_short"], exists=exists_disk)
        spans_src, spans_new = defaultdict(list), defaultdict(list)
        for ln, a, b, kind, raw, cat, target, new_raw, ok in toks:
            if cat == "short":
                tgt = RE.short_target(old_index, z["research"], kind, raw) if z["research"] else "short-unresolved"
                if not isinstance(tgt, Path):
                    cats["short-unresolved"] += 1
                    groups[grp]["short-unresolved"] += 1
                    continue
                rel = tgt.relative_to(APP).as_posix()
                within = rel.split("/", 1)[1] if "/" in rel else ""
                place = plan.places.get(rel)
                sc = "short-ok" if place and place.endswith("/" + within) else "short-to-untransferred"
                cats[sc] += 1
                groups[grp][sc] += 1
                if sc == "short-ok" and place not in disk:
                    short_broken.append(f"{it.dest}:{ln} {raw} → {place}")
                continue
            line_reps = reps_by_line.get(ln, [])
            spans_src[ln].append((a, b, True))
            if any(r.start <= a and b <= r.end and (r.start, r.end) != (a, b) for r in line_reps):
                cats["inside-rewritten"] += 1              # токен внутри переписанного токена — его текст часть той замены
                continue
            sa, sb = staged_span(a, b, line_reps)
            spans_new[ln].append((sa, sb, True))
            staged_tok = staged_lines[ln - 1][sa:sb] if ln - 1 < len(staged_lines) else ""
            if (ln, a, b) in held:                          # исключение: форма генератора (см. mig_plan.generator_outputs)
                h = held[(ln, a, b)]
                cats["held-for-generator"] += 1
                groups[grp]["held-for-generator"] += 1
                held_list.append(f"{it.dest}:{ln} {raw!r} → цель {h['target']} (генератор {h['generator']})")
                if staged_tok != raw:
                    retok.append(f"{it.dest}:{ln} ждали {raw!r}, в файле {staged_tok!r}")
                continue
            cats[cat] += 1
            groups[grp][cat] += 1
            per_base[it.base or "-"][cat] += 1
            rep = rep_at.get((ln, a, b))
            if rep:
                expect_tok = rep.new
            else:                                          # внутри токена могли переписать вложенный (ссылка в `…`)
                expect_tok = raw
                for r in sorted((r for r in line_reps if a <= r.start and r.end <= b), key=lambda r: -r.start):
                    expect_tok = expect_tok[:r.start - a] + r.new + expect_tok[r.end - a:]
            if staged_tok != expect_tok:
                retok.append(f"{it.dest}:{ln} ждали {expect_tok!r}, в файле {staged_tok!r}")
                continue
            if rep:
                rewritten += 1
            path_part = MP.split_token(staged_tok)[0]
            got = RE.new_resolve(path_part, it.dest, skill, z["base_short"], exists_disk) if path_part else None
            if target is not None:
                if got != target.rstrip("/"):
                    broken.append(f"{it.dest}:{ln} {staged_tok!r} → ждали {target}, разрешается в {got}")
            elif got is None:
                after_unresolved[grp][cat] += 1
        src_ids = ident_counts(src_lines, spans_src)
        new_ids = ident_counts(staged_lines, spans_new)
        for cls in set(src_ids) | set(new_ids):
            if cls != "path" and src_ids[cls] != new_ids[cls]:
                ident_bad.append(f"{it.dest}: {cls} {src_ids[cls]} → {new_ids[cls]}")
    # kb/INDEX.md — сгенерированные ссылки
    index_bad = []
    idx_text = text_of(root, plan.index_dest) or ""
    for m in MD_LINK_ANY.finditer(idx_text):
        tgt = posixpath.normpath(posixpath.join(posixpath.dirname(plan.index_dest), m.group(1)))
        if not exists_disk(tgt):
            index_bad.append(m.group(1))
    to_tr = cats["to-transferred"] + cats["dir-to-transferred"]
    ok = not (broken or short_broken or retok or index_bad)
    res.add("links", "hard", ok,
            f"ссылок на перенесённое {to_tr} (файл {cats['to-transferred']}, каталог {cats['dir-to-transferred']}) — битых "
            f"{len(broken)}; переписано {rewritten} токенов в {sum(1 for it in zone_items if it.zone['reps'])} файлах зоны "
            f"({len(zone_items)}); короткие адреса: верны {cats['short-ok'] - len(short_broken)} из {cats['short-ok']}; "
            f"ссылки kb/INDEX.md — битых {len(index_bad)}"
            + (f"; исключения — {len(held_list)} ссылок на код в производных файлах генераторов с --check (форма "
               f"генератора после правки B; перевести вместе с генераторами при адаптации)" if held_list else ""),
            categories=dict(cats), broken=broken[:30], short_broken=short_broken[:20], token_mismatch=retok[:20],
            held_for_generators=held_list,
            index_broken=index_bad[:20], by_base={b: dict(c) for b, c in sorted(per_base.items())},
            by_group={g: dict(c) for g, c in sorted(groups.items())})
    res.add("identifiers", "hard", not ident_bad,
            f"идентификаторы (неймспейсы, URN, URL $id, ключи, проза) по файлам зоны — изменений {len(ident_bad)}",
            changed=ident_bad[:30])
    return groups, after_unresolved, rewritten


def check_baselines(res, plan, groups, after_by_group):
    """Базовые числа A (scan-links.tsv, scan-rewrites.tsv) — предупреждения с цифрами. Сравнение — по зоне kb (как у A);
    README утилит (Р112) — отдельной строкой."""
    cats = groups.get("kb", Counter())
    after_unresolved = after_by_group.get("kb", Counter())
    rd, rd_after = groups.get("readme", Counter()), after_by_group.get("readme", Counter())
    nr, nr_after = groups.get("new-rule", Counter()), after_by_group.get("new-rule", Counter())
    base = {}
    for r in csv.DictReader(open(MP.SCAN_LINKS, encoding="utf-8"), delimiter="\t"):
        if r["source_kind"] in ("md", "data"):
            for k, v in r.items():
                if k not in ("base", "source_kind"):
                    base[k] = base.get(k, 0) + int(v)
    before_bad = sum(cats[k] for k in ("to-untransferred", "dir-to-untransferred", "to-handoff", "dir-to-handoff",
                                        "missing", "outside"))
    after_bad = sum(after_unresolved.values())
    a_untr = base.get("to-untransferred", 0) + base.get("dir-to-untransferred", 0)
    a_code = base.get("to-handoff", 0) + base.get("dir-to-handoff", 0)
    a_missing = base.get("missing", 0) + base.get("outside", 0)
    now_untr = cats["to-untransferred"] + cats["dir-to-untransferred"]
    now_code = cats["to-handoff"] + cats["dir-to-handoff"]
    now_missing = cats["missing"] + cats["outside"]
    over = []
    if now_untr > a_untr + a_code:
        over.append("на непереносимое")
    if now_missing > a_missing:
        over.append("неразрешимые")
    if after_bad > before_bad:
        over.append("битых после > до")
    if cats["short-unresolved"] > base.get("short-unresolved", 0):
        over.append("короткие не найдены")
    res.add("links-baseline", "warn", not over,
            f"на непереносимое {now_untr} (база A {a_untr} + код B {a_code}; из кода не взято {now_code}); неразрешимые "
            f"сейчас {now_missing} (база {a_missing}); короткие не найдены {cats['short-unresolved']} (база "
            f"{base.get('short-unresolved', 0)}); неразрешённых после переноса {after_bad} ≤ до {before_bad}"
            + (f"; выше базы: {', '.join(over)}" if over else "")
            + f"; вне базы A — README утилит (Р112): на перенесённое {rd['to-transferred'] + rd['dir-to-transferred']}, "
              f"прочих {sum(v for k, v in rd.items() if k not in ('to-transferred', 'dir-to-transferred'))}, неразрешённых "
              f"после {sum(rd_after.values())}; файлы правил после скана A: на перенесённое "
              f"{nr['to-transferred'] + nr['dir-to-transferred']}, прочих "
              f"{sum(v for k, v in nr.items() if k not in ('to-transferred', 'dir-to-transferred'))}",
            baseline_A=base, now=dict(cats), after_unresolved=dict(after_unresolved), readme=dict(rd),
            readme_after_unresolved=dict(rd_after), new_rule=dict(nr), new_rule_after_unresolved=dict(nr_after))
    # совпадение с scan-rewrites.tsv (2 026 токенов — без целей в коде, до Р112)
    mine = {(r[0], r[1], r[2], r[3]): r for r in plan.rewrites()}
    a = {(r["source"], int(r["line"]), int(r["start"]), int(r["end"])): r
         for r in csv.DictReader(open(MP.SCAN_REWRITES, encoding="utf-8"), delimiter="\t")}
    same = sum(1 for k, r in a.items() if k in mine and mine[k][6] == r["new"])
    differ = [f"{k[0]}:{k[1]} {a[k]['raw']!r}: A {a[k]['new']!r}, здесь {mine[k][6]!r}" for k in a if k in mine
              and mine[k][6] != a[k]["new"]]
    only_a = [f"{k[0]}:{k[1]} {a[k]['raw']!r}" for k in a if k not in mine]
    extra = Counter()
    for k, r in mine.items():
        if k in a:
            continue
        if "/scripts/" in r[8]:
            extra["README утилит (Р112)"] += 1
        elif "/scripts/" in r[7]:
            extra["цель — код B (tools-map)"] += 1
        elif "facts-demo" in r[7]:
            extra["факты голоса (Р112)"] += 1
        else:
            extra["прочее"] += 1
    ok = not differ and not only_a
    res.add("rewrites-baseline", "warn", ok,
            f"scan-rewrites.tsv A: {len(a)} токенов — те же {same}, иначе {len(differ)}, не переписаны {len(only_a)}; сверх "
            f"базы {sum(extra.values())}: " + ", ".join(f"{k} {v}" for k, v in sorted(extra.items())),
            differ=differ[:20], only_a=only_a[:20], extra=dict(extra))


def check_calibration(res, plan, disk, root):
    import yaml
    dest = f"{plan.skill}/assets/calibration/index.yaml"
    text = text_of(root, dest)
    if text is None:
        res.add("calibration", "hard", False, "нет assets/calibration/index.yaml")
        return
    data = yaml.safe_load(text)
    ok_n, miss = 0, []
    frames = data.get("frames", [])
    for fr in frames:
        wanted = [(r.split()[0], f"{plan.skill}/{r.split()[0]}") for r in fr.get("rubric") or []]
        if fr.get("file"):
            wanted.append((fr["file"], f"{plan.skill}/assets/calibration/{fr['file']}"))
        for shown, p in wanted:
            if p in disk:
                ok_n += 1
            else:
                miss.append(f"{fr.get('id')}: {shown}")
    src = APP / MP.BUILD_REL / "phase-3/calibration/index.yaml"
    same = disk[dest]["sha"] == sha256_bytes(src.read_bytes())
    frames_disk = sum(1 for d in disk if d.startswith(f"{plan.skill}/assets/calibration/frames/"))
    res.add("calibration", "hard", not miss and same,
            f"index.yaml: rubric и file → файлы дерева {ok_n}/{ok_n + len(miss)}; кадров {frames_disk}, записей {len(frames)}; "
            f"index.yaml байт в байт как утверждён — {'да' if same else 'нет'}", missing=miss[:20])


def gitignore_specs(plan):
    """Правила .gitignore шаблона (ветка main) по пути к управляемым папкам + .gitignore скилла из дерева."""
    import pathspec
    specs = []
    names = MP.git(plan.template, "ls-tree", "-r", "--name-only", plan.template_ref).stdout.decode().splitlines()
    for n in names:
        if posixpath.basename(n) != ".gitignore":
            continue
        d = posixpath.dirname(n)
        if d and not any((m + "/").startswith(d + "/") for m in (plan.skill, plan.journal_root, MP.FORWARD_ONLY)):
            continue
        lines = plan.template_file(n).decode("utf-8", "replace").splitlines()
        specs.append((d, pathspec.GitIgnoreSpec.from_lines(lines), f"{plan.template_ref}:{n}"))
    return specs


def check_dests(res, plan, disk, links, root):
    try:
        specs = gitignore_specs(plan)
        import pathspec
        skill_gi = text_of(root, f"{plan.skill}/.gitignore")
        if skill_gi is not None:
            specs.append((plan.skill, pathspec.GitIgnoreSpec.from_lines(skill_gi.splitlines()), f"{plan.skill}/.gitignore"))
    except ImportError:
        specs = None
    ignored = []
    if specs is not None:
        for d in sorted(disk):
            for base, spec, name in specs:
                if base and not d.startswith(base + "/"):
                    continue
                rel = d[len(base) + 1:] if base else d
                if spec.match_file(rel):
                    ignored.append(f"{d} ({name})")
                    break
    big = [f"{d} ({v['size'] / 1e6:.1f} МБ)" for d, v in sorted(disk.items()) if v["size"] > 5_000_000]
    non_ascii = sorted(d for d in disk if not d.isascii())
    lower = Counter(d.lower() for d in disk)
    case = sorted(d for d in disk if lower[d.lower()] > 1)
    if specs is None:
        res.add("gitignore", "hard", None, "нет модуля pathspec — совпадение с .gitignore не проверено")
    else:
        res.add("gitignore", "hard", not ignored, f"файлов дерева, которые спрятал бы .gitignore (шаблон {plan.template_ref} + "
                f"скилл), — {len(ignored)}; правил-файлов {len(specs)}", ignored=ignored[:30])
    res.add("symlinks", "hard", not links, f"симлинков в дереве — {len(links)}", links=links[:20])
    res.add("dest-names", "warn", not big and not case,
            f"файлов > 5 МБ — {len(big)}; совпадений имён без учёта регистра — {len(case)}; не-ASCII имён — {len(non_ascii)}",
            big=big, case=case[:20], non_ascii=non_ascii)


def check_home(res, plan, disk, root):
    skill = plan.skill
    in_scripts = sorted(d for d in disk if d.startswith(f"{skill}/scripts/") and b"/home/mm" in (Path(root) / d).read_bytes())
    refs = [r["dest"] for r in plan.tm_rows if r["kind"] == "ref"]
    in_refs = sorted(d for d in refs if d in disk and b"/home/mm" in (Path(root) / d).read_bytes())
    in_kb = sum(1 for d in disk if d.startswith(f"{skill}/kb/") and b"/home/mm" in (Path(root) / d).read_bytes())
    res.add("home-paths", "hard", not in_scripts and not in_refs,
            f"/home/mm: в scripts/ — {len(in_scripts)} файлов, в эталонном коде kb с правкой — {len(in_refs)}; "
            f"в kb всего — {in_kb} (тексты и журналы замеров, уборка)", scripts=in_scripts[:20], refs=in_refs)


def check_forward_only(res, plan, root):
    main = plan.template_file(MP.FORWARD_ONLY).decode("utf-8")
    snippet = MP.SNIPPET.read_text(encoding="utf-8")
    want, _ = MP.merge_forward_only(main, snippet)
    got = (Path(root) / MP.FORWARD_ONLY).read_text(encoding="utf-8") if (Path(root) / MP.FORWARD_ONLY).exists() else None
    n = got.count(snippet.strip("\n")) if got else 0
    ok = got == want and n == 1
    res.add("forward-only", "hard", ok, f".claude/rules/forward-only.md = {plan.template_ref} + абзац-исключение "
            f"(абзац {n} раз)")


def tokens_of(text, kind):
    return round(inv.tokens(text, kind)) if text is not None and kind else 0


def check_sizes(res, plan, disk, root):
    skill, jr = plan.skill + "/", plan.journal_root + "/"
    parts = defaultdict(Counter)
    for d, v in disk.items():
        it = plan.items.get(d)
        if d.startswith(skill + "kb/"):
            rest = d[len(skill) + 3:]
            key = "kb/" + (rest.split("/")[0] if "/" in rest else rest)
        elif d.startswith(skill + "scripts/"):
            key = "scripts/"
        elif d.startswith(skill + "assets/"):
            key = "assets/"
        elif d.startswith(skill):
            key = "skill: SKILL.md, .gitignore"
        elif d.startswith(jr):
            key = "журнал research/design-build/"
        else:
            key = d
        kind = None
        if it is not None and it.part not in ("asset-min", "calibration"):
            kind = (inv.KIND.get(it.cls) if it.cls in inv.KIND else None) or RE.kind_by_ext(Path(d).suffix.lower())
        text = text_of(root, d) if kind else None
        parts[key]["files"] += 1
        parts[key]["bytes"] += v["size"]
        parts[key]["tokens"] += tokens_of(text, kind)
    total = Counter()
    for c in parts.values():
        total.update(c)
    rows = {k: {"files": c["files"], "mb": round(c["bytes"] / 1e6, 2), "tokens_k": round(c["tokens"] / 1e3)}
            for k, c in sorted(parts.items())}
    mb = total["bytes"] / 1e6
    over = mb > ACCEPTED_MB[1] * 1.05 or total["files"] > ACCEPTED_FILES * 1.1
    res.add("size", "warn", not over, f"{total['files']} файлов, {mb:.1f} МБ, ≈ {total['tokens'] / 1e6:.2f} млн токенов "
            f"(принято Р111: ≈ {ACCEPTED_MB[0]:.0f}–{ACCEPTED_MB[1]:.0f} МБ, ≈ 1,7 тыс. файлов)", parts=rows,
            total={"files": total["files"], "mb": round(mb, 2), "tokens": total["tokens"]})
    return rows


def run_smoke(res, root):
    mem = mem_available_gb()
    if mem is not None and mem < MIN_MEM_GB:
        res.add("smoke", "hard", None, f"смоук не запускался: доступно {mem:.1f} ГБ < {MIN_MEM_GB:.0f} ГБ")
        return None
    SMOKE_DIR.mkdir(exist_ok=True)
    log = SMOKE_DIR / f"smoke-{SMOKE_TAG}.log"
    code = ("import sys; sys.dont_write_bytecode = True; sys.path.insert(0, sys.argv[1]); import code_stage as C; "
            "from pathlib import Path; C.RESULTS = Path(sys.argv[2]); "
            "sys.exit(C.smoke(False, '', (), sys.argv[3], False, sys.argv[4]))")
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as fh:
        r = subprocess.run([sys.executable, "-B", "-c", code, str(HERE), str(SMOKE_DIR), SMOKE_TAG, str(Path(root).resolve())],
                           stdout=fh, stderr=subprocess.STDOUT, cwd=str(HERE), env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    raw = SMOKE_DIR / f"code-smoke-{SMOKE_TAG}.raw.tsv"
    if not raw.exists():
        res.add("smoke", "hard", False, f"смоук не дал результатов (код {r.returncode}), лог — {log.relative_to(HERE)}")
        return None
    rows = list(csv.DictReader(open(raw, encoding="utf-8"), delimiter="\t"))
    st = Counter(x["status"] for x in rows)
    fails = [f"{x['path']} {x['check']}: {x['note']}" for x in rows if x["status"] == "FAIL"]
    xfail = [f"{x['path']} {x['check']}" for x in rows if x["status"] == "XFAIL"]
    xpass = [f"{x['path']} {x['check']}" for x in rows if x["status"] == "XPASS"]
    res.add("smoke", "hard", st["FAIL"] == 0 and r.returncode == 0,
            f"scripts/tests/smoke.py на дереве (песочница bwrap, без сети, браузеров и Blender): PASS {st['PASS']}, FAIL "
            f"{st['FAIL']}, XFAIL {st['XFAIL']}, XPASS {st['XPASS']} за {time.time() - t0:.0f} с",
            fails=fails, xfail=xfail, xpass=xpass, log=str(log.relative_to(HERE)), raw=str(raw.relative_to(HERE)))
    return st


def smoke_side_effects(res, plan, root, before, before_dirs, fp0):
    """Что утилиты записали внутрь дерева во время смоука. Правка или удаление файла дерева — жёсткий провал. Новые
    файлы — выходы утилит: убираются из .staging (своя временная папка), а в отчёт — покрывает ли их .gitignore скилла и
    шаблона (иначе в шаблоне они повиснут неотслеживаемыми после первого запуска утилиты)."""
    root = Path(root)
    after, _, links = scan_disk(root)
    changed = sorted(d for d in before if d in after and after[d] != before[d])
    removed = sorted(d for d in before if d not in after)
    new = sorted(d for d in after if d not in before) + sorted(links)
    specs = None
    try:
        import pathspec
        specs = gitignore_specs(plan)
        gi = text_of(root, f"{plan.skill}/.gitignore")
        if gi is not None:
            specs.append((plan.skill, pathspec.GitIgnoreSpec.from_lines(gi.splitlines()), f"{plan.skill}/.gitignore"))
    except ImportError:
        pass
    covered, uncovered = [], []
    for d in new:
        hit = specs is not None and any((not b or d.startswith(b + "/")) and sp.match_file(d[len(b) + 1:] if b else d)
                                        for b, sp, _ in specs)
        (covered if hit else uncovered).append(d)
        p = root / d
        if p.is_symlink() or p.is_file():
            p.unlink()
    for dp, _, _ in sorted(os.walk(root), key=lambda x: -len(x[0])):
        rel = Path(dp).relative_to(root).as_posix()
        if rel not in before_dirs and not any(Path(dp).iterdir()):
            Path(dp).rmdir()
    fp1 = MP.tree_fingerprint(root)[0]
    res.add("tree-after-smoke", "hard", not changed and not removed and fp1 == fp0,
            f"смоук не менял файлы дерева (правок {len(changed)}, удалений {len(removed)}); после уборки выходов "
            f"утилит отпечаток {'тот же' if fp1 == fp0 else 'ДРУГОЙ'}", changed=changed[:20], removed=removed[:20])
    res.add("smoke-outputs", "warn", not uncovered,
            f"утилиты во время смоука записали внутрь скилла {len(new)} файлов (убраны из .staging): под .gitignore — "
            f"{len(covered)}, вне .gitignore — {len(uncovered)}" + (f" ({', '.join(uncovered[:5])})" if uncovered else ""),
            covered=covered[:20], uncovered=uncovered[:20])


# ---------------------------------------------------------------- сводка

def human(report):
    out = [f"check: {'ЗЕЛЁНЫЙ' if report['ok'] else ('НЕ ЗАВЕРШЁН' if not report['hard_failed'] else 'ПРОВАЛ')}"
           f" — {report['generated_at']}",
           f"дерево: {report['root']}", f"отпечаток: {report['fingerprint']} ({report['files']} файлов, "
           f"{report['bytes'] / 1e6:.1f} МБ)", ""]
    for c in report["checks"]:
        mark = {True: "ok  ", False: "FAIL" if c["level"] == "hard" else "warn", None: "n/a "}[c["ok"]]
        out.append(f"[{mark}] {c['id']} ({c['level']}): {c['summary']}")
        for key in ("problems", "broken", "fails", "hits", "missing", "changed", "extra", "ignored", "errors"):
            vals = c.get(key)
            if c["ok"] is False and vals:
                out += [f"         {v}" for v in vals[:8]]
        for key in ("held_for_generators", "uncovered"):          # исключения и находки — с причиной, даже при ok
            out += [f"         {v}" for v in (c.get(key) or [])[:8]]
    size = next((c for c in report["checks"] if c["id"] == "size"), None)
    if size:
        out += ["", "размер и токены по частям:", "| часть | файлов | МБ | тыс. токенов |", "|---|---|---|---|"]
        for k, v in size["parts"].items():
            out.append(f"| {k} | {v['files']} | {v['mb']} | {v['tokens_k']} |")
    smoke = next((c for c in report["checks"] if c["id"] == "smoke"), None)
    if smoke and smoke.get("xfail"):
        out += ["", "смоук XFAIL (известные ограничения без окружения, code-xfail.tsv):"] + [f"  {x}" for x in smoke["xfail"]]
        if smoke.get("xpass"):
            out += ["смоук XPASS:"] + [f"  {x}" for x in smoke["xpass"]]
    return "\n".join(out) + "\n"


def run(root, smoke=True, template=None):
    root = Path(root)
    res = Result()
    t0 = time.time()
    if not root.is_dir():
        raise MP.BuildError(f"нет дерева {root} — сначала build")
    print("check: план из текущих входов…", flush=True)
    plan = MP.Plan(template=template or MP.built_template())
    disk, dirs, links = scan_disk(root)
    fp0 = MP.tree_fingerprint(root)
    print(f"check: дерево {fp0[0]} ({fp0[1]} файлов)", flush=True)
    check_freeze(res)
    check_patches(res)
    check_fidelity(res, plan, disk)
    check_composition(res, plan, disk, root)
    check_forbidden(res, plan, disk, root)
    check_instructions(res, plan, disk, links)
    check_secrets(res, disk, root)
    groups, after_unresolved, _ = check_links(res, plan, disk, dirs, root)
    check_calibration(res, plan, disk, root)
    check_dests(res, plan, disk, links, root)
    check_home(res, plan, disk, root)
    check_forward_only(res, plan, root)
    check_baselines(res, plan, groups, after_unresolved)
    check_sizes(res, plan, disk, root)
    if smoke:
        before_dirs = {Path(dp).relative_to(root).as_posix() for dp, _, _ in os.walk(root)}
        run_smoke(res, root)
        smoke_side_effects(res, plan, root, disk, before_dirs, fp0[0])
    else:
        res.add("smoke", "hard", None, "смоук пропущен (--no-smoke)")
    last_build = None
    bj = MP.REPORTS / "build.json"
    if bj.exists():
        last_build = json.loads(bj.read_text(encoding="utf-8")).get("fingerprint")
    res.add("determinism", "hard", plan.fingerprint() == fp0[0],
            f"план из текущих входов даёт тот же отпечаток ({plan.fingerprint()[:16]}…); последний build — "
            f"{(last_build or '—')[:16]}…")
    report = {
        "ok": not res.hard_failed and not res.not_run, "complete": not res.not_run,
        "hard_failed": [c["id"] for c in res.hard_failed], "not_run": [c["id"] for c in res.not_run],
        "warnings": [c["id"] for c in res.warnings], "fingerprint": fp0[0], "files": fp0[1], "bytes": fp0[2],
        "root": str(root.relative_to(HERE)) if root.resolve().is_relative_to(HERE) else str(root),
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "seconds": round(time.time() - t0, 1),
        "checks": res.checks,
    }
    MP.dump_json(MP.REPORTS / "check.json", report)
    (MP.REPORTS / "check.txt").write_text(human(report), encoding="utf-8")
    return report
