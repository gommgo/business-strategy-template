#!/usr/bin/env python3
"""Сводный реестр Ф4 (сверка баз): проверка строк узла, сборка реестра, покрытие карты входов, выпуск
`kb/common/canon.tsv` («норма → место»).

Строки узла — `nodes/<NN>-<код>.tsv`, схема — `PLAN.md` «Строки узла»: 13 колонок, первая строка — заголовок.

Команды (Python 3.13, только стандартная библиотека):
    python tools/registry.py check nodes/01-GL.tsv [...] [--rows F]
                                                           # схема, id, статусы, пути в sides / canon / copies, source
    python tools/registry.py merge [--nodes DIR] [--out F] # nodes/*.tsv → registry.tsv
    python tools/registry.py coverage [--nodes DIR] [--node TR] [--all] [--rows F]
                                                           # строки inputs/rows.tsv с узлом, не упомянутые ни в одном source
    python tools/registry.py canon [--registry F] [--out F]
                                                           # registry.tsv (закрыто, позиция) → kb/common/canon.tsv

Пути в `sides`, `canon`, `copies`: элементы через `;`; путь — часть до ` §` или `#`; в `sides` префикс `база:` отбрасывается;
путь разрешается от `kb/` (префикс `kb/` допустим), а если начинается с `docs/`, `.claude/` или `research/` — от корня
репозитория; элементы без `/` (например, `Р28`) не проверяются; `*` в пути — шаблон, нужен хотя бы один файл; номер строки
после пути (`путь:120`) отбрасывается с предупреждением — строки сдвигаются, место называют разделом ` §…`.
В `source`: `IN-0001`, диапазоны `IN-0010…IN-0015` (также `–`, `..`), `§9 п. N`, `§6.12 п. N`.
`canon` пишет файл, только если в реестре нет ошибок: у нормы ровно одно место, путь существует, одна тема — одно место.
Код выхода: 0 — без ошибок (предупреждения допустимы), 1 — есть ошибки, непокрытые или неназначенные строки.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
REPO = PHASE.parent.parent.parent
KB = REPO / ".claude/skills/design-deep-dive/kb"
NODES_DIR = PHASE / "nodes"
REGISTRY = PHASE / "registry.tsv"
ROWS = PHASE / "inputs/rows.tsv"
CANON = KB / "common/canon.tsv"

COLUMNS = ["id", "node", "kind", "topic", "sides", "positions", "resolution", "basis", "canon", "copies", "action",
           "status", "source"]
NODE_CODES = ["GL", "TR", "GT", "CM", "ST", "NU", "TX", "VI", "JU", "CN"]
KINDS = {"conflict", "duplicate", "gap", "id-sync", "term", "new-norm"}
STATUSES = {"закрыто", "позиция", "открыто", "заказчику"}
NEED_CANON = {"закрыто", "позиция"}
BASES = {"ux", "ui", "site", "text", "creative", "ai-media", "blender", "claude-design", "common"}
REPO_ROOTS = ("docs/", ".claude/", "research/")
LIMITS = {"topic": 80, "resolution": 300}
IN_ID = re.compile(r"IN-(\d{4})")
IN_RANGE = re.compile(r"IN-(\d{4})\s*(?:…|\.\.|–|—|-)\s*IN-(\d{4})")
S9_REF = re.compile(r"§\s*9\s*п\.\s*(\d+)")
DOC_REF = re.compile(r"§\s*6\.12\s*п\.\s*(\d+)")
LINE_SUFFIX = re.compile(r":\d+(?:\s*[–-]\s*\d+)?$")


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, where: str, msg: str):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str):
        self.warnings.append(f"{where}: {msg}")

    def print(self, title: str) -> int:
        for w in self.warnings:
            print(f"  предупреждение · {w}")
        for e in self.errors:
            print(f"  ОШИБКА · {e}")
        print(f"{title}: ошибок {len(self.errors)}, предупреждений {len(self.warnings)}")
        return 1 if self.errors else 0


# ─────────────────────────────── чтение ───────────────────────────────

def read_tsv(path: Path, rep: Report) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = [x for x in lines if x.strip()]
    if not lines:
        rep.err(path.name, "пустой файл: нужен заголовок из 13 колонок")
        return []
    header = lines[0].split("\t")
    if header != COLUMNS:
        rep.err(path.name, f"заголовок {header} ≠ {COLUMNS}")
        return []
    out = []
    for n, line in enumerate(lines[1:], 2):
        cells = line.split("\t")
        if len(cells) != len(COLUMNS):
            rep.err(f"{path.name}:{n}", f"{len(cells)} колонок вместо {len(COLUMNS)} (табуляция внутри поля?)")
            continue
        row = dict(zip(COLUMNS, (c.strip() for c in cells)))
        row["_where"] = f"{path.name}:{n}"
        out.append(row)
    return out


def load_input_rows() -> "OrderedDict[str, dict]":
    out: "OrderedDict[str, dict]" = OrderedDict()
    if not ROWS.exists():
        return out
    lines = ROWS.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    for line in lines[1:]:
        if line.strip():
            d = dict(zip(header, line.split("\t")))
            out[d["row"]] = d
    return out


def node_files() -> list[Path]:
    return sorted(p for p in NODES_DIR.glob("*.tsv") if re.match(r"^\d{2}-[A-Z]{2}\.tsv$", p.name))


def relname(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(REPO))
    except ValueError:
        return str(p)


# ─────────────────────────────── пути ───────────────────────────────

def split_items(value: str) -> list[str]:
    return [x.strip() for x in value.split(";") if x.strip() and x.strip() != "—"]


def path_of(item: str, strip_base: bool) -> str:
    s = item.strip().strip("`").strip()
    if strip_base:
        m = re.match(r"^([a-z][a-z-]*)\s*:\s*(.+)$", s)
        if m and m.group(1) in BASES:
            s = m.group(2).strip().strip("`").strip()
    for sep in (" §", "#"):
        if sep in s:
            s = s.split(sep, 1)[0]
    return s.strip().strip("`").rstrip(",.").strip()


def resolve(p: str) -> Path:
    if p.startswith(REPO_ROOTS):
        return REPO / p
    if p.startswith("kb/"):
        p = p[3:]
    return KB / p


def exists(p: str) -> tuple[bool, str]:
    """(найден ли путь, замечание)."""
    root = REPO if p.startswith(REPO_ROOTS) else KB
    rel = p[3:] if p.startswith("kb/") else p
    if "*" in rel:
        return any(root.glob(rel)), ""
    if (root / rel).exists():
        return True, ""
    head = rel.split()[0] if rel.split() else rel
    if head != rel and (root / head).exists():
        return True, f"после пути лишний текст: «{p}» (путь — до « §» или «#»)"
    return False, ""


def check_paths(row: dict, field: str, rep: Report, strip_base: bool):
    for item in split_items(row[field]):
        p = path_of(item, strip_base)
        if "/" not in p:
            continue
        if LINE_SUFFIX.search(p):
            rep.warn(row["_where"], f"{field}: номер строки после пути «{p}» — строки сдвигаются, место называют разделом « §…»")
            p = LINE_SUFFIX.sub("", p)
        ok, note = exists(p)
        if not ok:
            rep.err(row["_where"], f"{field}: нет пути `{p}` (от {'корня' if p.startswith(REPO_ROOTS) else 'kb/'})")
        elif note:
            rep.warn(row["_where"], f"{field}: {note}")


# ─────────────────────────────── source ───────────────────────────────

def source_refs(value: str, s9_rows: dict) -> set[str]:
    """Строки карты входов, на которые ссылается `source`. `s9_rows` — {("s9", N) | ("doc", N): IN-…} из `s9_map`."""
    refs: set[str] = set()
    for a, b in IN_RANGE.findall(value):
        lo, hi = sorted((int(a), int(b)))
        refs.update(f"IN-{n:04d}" for n in range(lo, hi + 1))
    refs.update(f"IN-{m}" for m in IN_ID.findall(value))
    for kind, rx in (("s9", S9_REF), ("doc", DOC_REF)):
        for n in rx.findall(value):
            if (kind, int(n)) in s9_rows:
                refs.add(s9_rows[(kind, int(n))])
    return refs


def s9_map(inputs: "OrderedDict[str, dict]") -> dict:
    """Пункты SYNTHESIS в карте входов: («s9», N) — §9 п. N, («doc», N) — §6.12 п. N."""
    out = {}
    for rid, d in inputs.items():
        kind = {"s9": "s9", "doc-conflict": "doc"}.get(d.get("src_kind", ""))
        m = re.search(r"п\.\s*(\d+)", d.get("item_id", ""))
        if kind and m:
            out[(kind, int(m.group(1)))] = rid
    return out


# ─────────────────────────────── check ───────────────────────────────

def check_rows(rows: list[dict], rep: Report, file_code: str | None, inputs: "OrderedDict[str, dict]"):
    s9 = s9_map(inputs)
    ids = Counter(r["id"] for r in rows)
    for r in rows:
        w = r["_where"]
        for f in ("id", "node", "kind", "topic", "status", "source"):
            if not r[f]:
                rep.err(w, f"пустое поле {f}")
        if r["node"] and r["node"] not in NODE_CODES:
            rep.err(w, f"node `{r['node']}` не из {NODE_CODES}")
        if file_code and r["node"] and r["node"] != file_code:
            rep.err(w, f"node `{r['node']}` ≠ код файла `{file_code}`")
        if r["id"] and not re.fullmatch(rf"{re.escape(r['node'] or '??')}-\d{{2,3}}", r["id"]):
            if re.fullmatch(r"[A-Z]{2}-\d{2,3}", r["id"]):
                rep.err(w, f"id `{r['id']}`: префикс не совпадает с node `{r['node']}`")
            else:
                rep.err(w, f"id `{r['id']}` не в форме `<код>-NN`")
        if ids[r["id"]] > 1:
            rep.err(w, f"id `{r['id']}` повторяется")
        if r["kind"] and r["kind"] not in KINDS:
            rep.err(w, f"kind `{r['kind']}` не из {sorted(KINDS)}")
        if r["status"] and r["status"] not in STATUSES:
            rep.err(w, f"status `{r['status']}` не из {sorted(STATUSES)}")
        if r["status"] in NEED_CANON:
            for f in ("resolution", "canon"):
                if not r[f] or r[f] == "—":
                    rep.err(w, f"у статуса «{r['status']}» пустое поле {f}")
        if r["status"] == "открыто" and not r["action"]:
            rep.warn(w, "открытая строка без action (что её закроет)")
        if len(split_items(r["canon"])) > 1:
            rep.err(w, "canon: больше одного места (одна норма — одно место)")
        for f, limit in LIMITS.items():
            if len(r[f]) > limit:
                rep.warn(w, f"{f}: {len(r[f])} символов при норме до {limit}")
        check_paths(r, "sides", rep, strip_base=True)
        check_paths(r, "canon", rep, strip_base=False)
        check_paths(r, "copies", rep, strip_base=False)
        refs = source_refs(r["source"], s9)
        if r["source"] and not refs:
            rep.warn(w, "source без IN-…, «§9 п. N» и «§6.12 п. N» — строка не покрывает карту входов")
        unknown = sorted(x for x in refs if x not in inputs)
        if unknown:
            rep.err(w, f"source: нет в inputs/rows.tsv: {', '.join(unknown[:8])}{' …' if len(unknown) > 8 else ''}")
    # Строки карты, назначенные другим узлам: не ошибка (узел может закрыть и чужую строку), но оркестратору видно
    if file_code and file_code != "CN":
        foreign: dict[str, list[str]] = defaultdict(list)
        for r in rows:
            for ref in sorted(source_refs(r["source"], s9)):
                node = inputs.get(ref, {}).get("node", "")
                if ref in inputs and node not in (file_code, "—"):
                    foreign[node or "(пусто)"].append(ref)
        if foreign:
            rep.warn(file_code, "source называет строки других узлов: " + "; ".join(
                f"{n} — {', '.join(sorted(set(ids))[:6])}{' …' if len(set(ids)) > 6 else ''}" for n, ids in sorted(foreign.items())))


def cmd_check(paths: list[str]) -> int:
    inputs = load_input_rows()
    status = 0
    for p in paths:
        path = Path(p)
        if not path.is_absolute():
            path = (Path.cwd() / path) if (Path.cwd() / path).exists() else PHASE / p
        rep = Report()
        m = re.match(r"^\d{2}-([A-Z]{2})\.tsv$", path.name)
        if not m:
            rep.warn(path.name, "имя файла не в форме `NN-КОД.tsv` — код узла не сверяется")
        rows = read_tsv(path, rep)
        check_rows(rows, rep, m.group(1) if m else None, inputs)
        status |= rep.print(f"{path.name}: строк {len(rows)}")
    return status


# ─────────────────────────────── merge ───────────────────────────────

def collect(rep: Report) -> list[dict]:
    out = []
    for p in node_files():
        out.extend(read_tsv(p, rep))
    ids = Counter(r["id"] for r in out)
    for r in out:
        if ids[r["id"]] > 1:
            rep.err(r["_where"], f"id `{r['id']}` повторяется в реестре")
    topics = defaultdict(list)
    for r in out:
        topics[r["topic"].lower()].append(r)
    for t, rs in topics.items():
        canons = {x["canon"] for x in rs if x["canon"]}
        if len(rs) > 1 and len(canons) > 1:
            rep.warn(", ".join(x["id"] for x in rs), f"одна тема «{rs[0]['topic']}» — разные canon: {'; '.join(sorted(canons))}")
    return out


def cmd_merge() -> int:
    rep = Report()
    files = node_files()
    rows = collect(rep)
    with REGISTRY.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join(r[c] for c in COLUMNS) + "\n")
    print(f"{relname(REGISTRY)}: файлов узлов {len(files)}, строк {len(rows)}")
    by = Counter(r["node"] for r in rows)
    if by:
        print("по узлам: " + ", ".join(f"{k} {by[k]}" for k in NODE_CODES if by[k]))
    return rep.print("merge")


# ─────────────────────────────── coverage ───────────────────────────────

def compact(ids: list[str]) -> str:
    nums = sorted(int(x[3:]) for x in ids)
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        parts.append(f"IN-{nums[i]:04d}" + (f"…IN-{nums[j]:04d}" if j > i else ""))
        i = j + 1
    return ", ".join(parts)


def cmd_coverage(only: str | None, show_all: bool) -> int:
    inputs = load_input_rows()
    if not inputs:
        print(f"нет {relname(ROWS)} — сначала tools/extract_rows.py")
        return 1
    rep = Report()
    reg = collect(rep)
    if REGISTRY.exists() and node_files():
        newest = max(p.stat().st_mtime for p in node_files())
        if REGISTRY.stat().st_mtime < newest:
            print("примечание: registry.tsv старше nodes/*.tsv — покрытие считается по nodes/*.tsv; обновите merge")
    s9 = s9_map(inputs)
    covered_by: dict[str, set[str]] = defaultdict(set)
    for r in reg:
        for ref in source_refs(r["source"], s9):
            covered_by[ref].add(r["node"])
    # Строка без узла или с узлом не из списка — не «—»: её никто не покроет, значит, потеря; такие строки — ошибка
    unassigned = [rid for rid, d in inputs.items() if (d.get("node") or "") not in NODE_CODES + ["—"]]
    need = [(rid, d["node"]) for rid, d in inputs.items() if d.get("node") in NODE_CODES]
    total_by = Counter(n for _, n in need)
    miss_by: dict[str, list[str]] = defaultdict(list)
    foreign = Counter()
    for rid, node in need:
        if rid not in covered_by:
            miss_by[node].append(rid)
        elif node not in covered_by[rid]:
            foreign[node] += 1
    print(f"карта входов: строк {len(inputs)}, с узлом {len(need)}, «—» {len(inputs) - len(need) - len(unassigned)}, "
          f"без узла {len(unassigned)}; реестр: файлов {len(node_files())}, строк {len(reg)}")
    if unassigned:
        print(f"  ОШИБКА · строки карты без узла или с узлом не из списка (назначить в inputs/assign.tsv): "
              f"{', '.join(unassigned[:12])}{' …' if len(unassigned) > 12 else ''}")
    print("| узел | строк карты | покрыто | не покрыто | покрыто чужим узлом |")
    print("|---|---:|---:|---:|---:|")
    for n in NODE_CODES:
        if only and n != only:
            continue
        t = total_by[n]
        m = len(miss_by[n])
        print(f"| {n} | {t} | {t - m} | {m} | {foreign[n]} |")
    uncovered = sum(len(v) for k, v in miss_by.items() if not only or k == only)
    for n in NODE_CODES:
        if (only and n != only) or not miss_by[n]:
            continue
        ids = miss_by[n]
        text = compact(ids)
        if not show_all and len(text) > 600:
            text = text[:600].rsplit(",", 1)[0] + " … (--all — полностью)"
        print(f"не покрыто {n}: {text}")
    for e in rep.errors:
        print(f"  ОШИБКА · {e}")
    print(f"итого не покрыто: {uncovered}" + (f"; без узла: {len(unassigned)}" if unassigned else ""))
    return 1 if uncovered or rep.errors or unassigned else 0


# ─────────────────────────────── canon ───────────────────────────────

def cmd_canon(registry: Path, out: Path) -> int:
    rep = Report()
    if not registry.exists():
        print(f"нет {relname(registry)} — сначала merge")
        return 1
    rows = read_tsv(registry, rep)
    chosen = [r for r in rows if r["status"] in NEED_CANON]
    ids = Counter(r["id"] for r in chosen)
    by_topic: dict[str, set[str]] = defaultdict(set)
    for r in chosen:
        places = split_items(r["canon"])
        if len(places) != 1:
            rep.err(r["_where"], f"{r['id']}: canon — {'пусто' if not places else 'больше одного места'} (одна норма — одно место)")
        if ids[r["id"]] > 1:
            rep.err(r["_where"], f"id `{r['id']}` повторяется")
        check_paths(r, "canon", rep, strip_base=False)
        by_topic[r["topic"].strip().lower()].add(r["canon"].strip())
    for topic, places in by_topic.items():
        if len(places) > 1:
            rep.err(topic, f"одна тема — разные места: {'; '.join(sorted(places))}")
    if rep.errors:
        print(f"{relname(out)} не записан: в реестре ошибки")
        return rep.print("canon")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write("norm\tplace\tstatus\tid\tcopies\n")
        for r in sorted(chosen, key=lambda x: (NODE_CODES.index(x["node"]) if x["node"] in NODE_CODES else 99, x["id"])):
            f.write("\t".join([r["topic"], r["canon"], r["status"], r["id"], r["copies"]]) + "\n")
    print(f"{relname(out)}: норм {len(chosen)}")
    return rep.print("canon")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="проверить строки узла")
    c.add_argument("files", nargs="+")
    c.add_argument("--rows", help="карта входов (по умолчанию phase-4/inputs/rows.tsv)")
    m = sub.add_parser("merge", help="nodes/*.tsv → registry.tsv")
    m.add_argument("--nodes", help="папка строк узлов (по умолчанию phase-4/nodes)")
    m.add_argument("--out", help="куда писать реестр (по умолчанию phase-4/registry.tsv)")
    cv = sub.add_parser("coverage", help="покрытие inputs/rows.tsv")
    cv.add_argument("--nodes", help="папка строк узлов (по умолчанию phase-4/nodes)")
    cv.add_argument("--node", choices=NODE_CODES)
    cv.add_argument("--all", action="store_true", help="полный список непокрытых")
    cv.add_argument("--rows", help="карта входов (по умолчанию phase-4/inputs/rows.tsv)")
    cn = sub.add_parser("canon", help="registry.tsv → kb/common/canon.tsv")
    cn.add_argument("--registry", help="сводный реестр (по умолчанию phase-4/registry.tsv)")
    cn.add_argument("--out", help="куда писать таблицу «норма → место» (по умолчанию kb/common/canon.tsv; для проб — "
                                  "путь во временной папке)")
    args = ap.parse_args()
    global NODES_DIR, REGISTRY, ROWS
    if getattr(args, "rows", None):
        ROWS = Path(args.rows).resolve()
    if getattr(args, "nodes", None):
        NODES_DIR = Path(args.nodes).resolve()
    if args.cmd == "merge" and args.out:
        REGISTRY = Path(args.out).resolve()
    if args.cmd == "check":
        return cmd_check(args.files)
    if args.cmd == "merge":
        return cmd_merge()
    if args.cmd == "coverage":
        return cmd_coverage(args.node, args.all)
    registry = Path(args.registry).resolve() if args.registry else REGISTRY
    out = Path(args.out).resolve() if args.out else CANON
    return cmd_canon(registry, out)


if __name__ == "__main__":
    sys.exit(main())
