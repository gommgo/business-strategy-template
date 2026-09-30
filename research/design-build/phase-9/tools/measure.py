#!/usr/bin/env python3
"""Журнал замера пилотов Ф9 (research/design-build/phase-9/pilots/).

Что меряем и зачем — phase-9/PLAN.md § 4 «Журнал замера», правила ведения — phase-9/PILOT-PROMPT.md.
Файлы пилота: pilots/<P>/measure.tsv (события проверок и решений), sessions.tsv (сидения и блоки);
общий pilots/FINDINGS.tsv (находки о скилле). Скилл о замере не знает: журнал ведёт сессия пилота.

Подкоманды:
  init P2                              создать папку пилота и пустые TSV с шапками
  add P2 --tool T --stage S [поля]     строка события; --from-json F|-  — находки утилиты: строка на
                                       (правило, уровень), одинаковые срабатывания — счётом; прогон без
                                       находок — строка с count 0
  set P2 M-0007 useful=помогла customer=правка   поправить поля строки (ваше слово, польза, обход)
  set F9-001 check=… status=решено            поправить поля находки FINDINGS.tsv
  session P2 --part С1 [поля]          строка sessions.tsv; утилиты, сжатия и контекст — из журналов сессий
  finding --pilot P2 --what … [поля]   строка FINDINGS.tsv (F9-NNN)
  calls P2 [--session ID] [--since ISO]  вызовы утилит скилла, скиллов и агентов по журналам сессий
                                       Claude Code папки пилота; сверка с measure.tsv
  context P2 --session ID (--match RE | --at ISO)  контекст модели к событию (токены входа ответа)
  rub P2                               траты по журналу трат пилота
  summary [P2 …] [--out MEASURE.md]    сводка по утилитам и правилам
  check [P2 …]                         форма TSV: колонки, значения словарей, id

Код выхода: 0 — сделано; 1 — check нашёл ошибки формы; 2 — ошибка вызова.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

JOURNAL = Path(__file__).resolve().parents[1]          # research/design-build/phase-9
PILOTS = JOURNAL / "pilots"
FINDINGS = PILOTS / "FINDINGS.tsv"
DDD_HOME = Path(os.environ.get("DDD_HOME") or Path.home() / ".cache/design-deep-dive")
CLAUDE_PROJECTS = Path.home() / ".claude/projects"

# Папка проекта пилота — по ней ищутся журналы сессий Claude Code.
PILOT_DIRS = {"P2": Path("/home/mm/git/stit-core/pilot-greats")}
PILOT_LEDGER = {"P2": DDD_HOME / "out/ai-media/_ledger-P2.jsonl"}

MEASURE_COLS = ["id", "at", "pilot", "unit", "stage", "kind", "tool", "trigger", "rule", "level", "gate", "count",
                "finding", "useful", "customer", "bypass", "reason", "cost", "note"]
SESSION_COLS = ["date", "pilot", "part", "stages", "work_min", "customer_min", "decisions", "close_questions",
                "usage_before", "usage_after", "ctx_first_wireframe", "compactions", "utilities", "rub",
                "sessions", "note"]
FINDING_COLS = ["id", "pilot", "stage", "path", "what", "weight", "blocks", "proposal", "decision", "check", "status"]

VOCAB = {
    "kind": {"check", "stop", "bypass", "decision", "round", "rejected", "approval-lost"},
    "trigger": {"переход", "ход", "просьба", "аудит", "—"},
    "level": {"error", "warning", "hint", "info", "B", "S", "D", "—"},
    "gate": {"1", "2", "3", "4", "5", "—"},
    "useful": {"помогла", "шум", "спорно", ""},
    "customer": {"правка", "как есть", "ложная", "не спрашивали", ""},
}
FINDING_VOCAB = {
    "weight": {"высокий", "средний", "низкий"},
    "blocks": {"да", "нет"},
    "decision": {"сразу", "окно", "Ф10", ""},          # или «отклонено: причина»
    "status": {"открыто", "решено", "внесено", "проверено", "отклонено"},
}
SEVERITY_MAP = {"critical": "error", "major": "warning", "minor": "hint", "fail": "error", "warn": "warning",
                "review": "warning", "ok": "info", "pass": "info", "blocker": "error"}
UTIL_RE = re.compile(r"(?:scripts|design-deep-dive/scripts)/(?:[\w.-]+/)*([\w.-]+\.(?:py|sh|mjs|js))(?:\s+(?!-)([\w-]+))?")
SLASH_RE = re.compile(r"<command-name>/?([\w:-]+)</command-name>")


def die(msg: str) -> None:
    print(f"measure: {msg}", file=sys.stderr)
    sys.exit(2)


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


# ---------- TSV ----------

def pilot_dir(p: str) -> Path:
    if not re.fullmatch(r"P\d", p):
        die(f"пилот — P1, P2, P3 (дано {p!r})")
    return PILOTS / p


def read_tsv(path: Path, cols: list[str]) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        if rd.fieldnames != cols:
            die(f"{path}: колонки {rd.fieldnames} вместо {cols}")
        return [dict(r) for r in rd]


def clean(v) -> str:
    return re.sub(r"[\t\r\n]+", " ", str(v if v is not None else "")).strip()


def write_tsv(path: Path, cols: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(clean(r.get(c, "")) for c in cols) + "\n")
    tmp.replace(path)


def append_rows(path: Path, cols: list[str], rows: list[dict]) -> None:
    existing = read_tsv(path, cols)
    write_tsv(path, cols, existing + rows)


def next_id(rows: list[dict], prefix: str, width: int) -> int:
    n = 0
    for r in rows:
        m = re.fullmatch(re.escape(prefix) + r"(\d+)", r.get("id", ""))
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


# ---------- init / add / set ----------

def cmd_init(a) -> None:
    d = pilot_dir(a.pilot)
    (d / "votes").mkdir(parents=True, exist_ok=True)
    for name, cols in (("measure.tsv", MEASURE_COLS), ("sessions.tsv", SESSION_COLS)):
        if not (d / name).exists():
            write_tsv(d / name, cols, [])
    if not FINDINGS.exists():
        write_tsv(FINDINGS, FINDING_COLS, [])
    keep = d / "votes" / ".gitkeep"
    keep.touch()
    print(f"готово: {d.relative_to(JOURNAL.parent.parent)}")


def load_findings(src: str) -> list[dict]:
    text = sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")
    text = text.strip()
    if not text:
        return []
    items: list = []
    try:
        data = json.loads(text)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("findings", "items", "issues", "errors", "results"):
                if isinstance(data.get(key), list):
                    items = data[key]
                    break
            else:
                items = [data]
    except json.JSONDecodeError:
        for ln in text.splitlines():
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    items.append(json.loads(ln))
                except json.JSONDecodeError:
                    pass
    return [i for i in items if isinstance(i, dict)]


def finding_rule(f: dict) -> str:
    return clean(f.get("rule") or f.get("code") or f.get("id") or f.get("check") or "—")


def finding_level(f: dict) -> str:
    lv = clean(f.get("severity") or f.get("level") or f.get("verdict") or "—")
    lv = SEVERITY_MAP.get(lv.lower(), lv)
    return lv if lv in VOCAB["level"] else "—"


def base_row(a) -> dict:
    return {"at": now(), "pilot": a.pilot, "unit": a.unit or "—", "stage": a.stage, "kind": a.kind,
            "tool": a.tool, "trigger": a.trigger, "rule": a.rule or "—", "level": a.level or "—",
            "gate": a.gate or "—", "count": str(a.count if a.count is not None else 1), "finding": a.finding or "",
            "useful": a.useful or "", "customer": a.customer or "", "bypass": a.bypass or "—",
            "reason": a.reason or "", "cost": a.cost or "", "note": a.note or ""}


def cmd_add(a) -> None:
    path = pilot_dir(a.pilot) / "measure.tsv"
    rows = read_tsv(path, MEASURE_COLS)
    n = next_id(rows, "M-", 4)
    new: list[dict] = []
    if a.from_json:
        found = load_findings(a.from_json)
        groups: dict[tuple, list] = collections.OrderedDict()
        for f in found:
            groups.setdefault((finding_rule(f), finding_level(f)), []).append(f)
        if not groups:
            r = base_row(a)
            r.update(count="0", finding="без находок", rule="—", level="—")
            new.append(r)
        for (rule, level), fs in groups.items():
            r = base_row(a)
            first = fs[0]
            msg = clean(first.get("message") or first.get("msg") or first.get("text") or "")
            where = clean(first.get("path") or first.get("ref") or first.get("file") or "")
            r.update(rule=rule, level=level, count=str(len(fs)), finding=msg[:220],
                     note=(a.note + " · " if a.note else "") + (where[:160] if where else ""))
            if a.gate is None and level == "error" and rule.startswith("R-MAT-012"):
                r["gate"] = "2"
            new.append(r)
    else:
        new.append(base_row(a))
    for r in new:
        r["id"] = f"M-{n:04d}"
        n += 1
        bad = [f"{k}={r[k]!r}" for k in ("kind", "trigger", "level", "gate", "useful", "customer")
               if r[k] not in VOCAB[k]]
        if bad:
            die("значение вне словаря: " + ", ".join(bad))
    write_tsv(path, MEASURE_COLS, rows + new)
    for r in new:
        print(f"{r['id']}\t{r['rule']}\t{r['level']}\t×{r['count']}\t{r['finding'][:90]}")


def cmd_set_finding(ids: list[str], fields: list[str]) -> None:
    rows = read_tsv(FINDINGS, FINDING_COLS)
    pairs = []
    for kv in fields:
        k, v = kv.split("=", 1)
        if k not in FINDING_COLS or k == "id":
            die(f"нет поля {k!r}")
        if k in FINDING_VOCAB and v not in FINDING_VOCAB[k] and not (k == "decision" and v.startswith("отклонено:")):
            die(f"{k}={v!r} вне словаря {sorted(FINDING_VOCAB[k])}")
        pairs.append((k, v))
    hit = 0
    for r in rows:
        if r["id"] in ids:
            for k, v in pairs:
                r[k] = v
            hit += 1
    if hit != len(ids):
        die(f"найдено находок {hit} из {len(ids)}")
    write_tsv(FINDINGS, FINDING_COLS, rows)
    print(f"поправлено находок: {hit}")


def cmd_set(a) -> None:
    path = pilot_dir(a.pilot) / "measure.tsv"
    rows = read_tsv(path, MEASURE_COLS)
    ids = set(a.ids)
    pairs = []
    for kv in a.fields:
        if "=" not in kv:
            die(f"поле — ключ=значение (дано {kv!r})")
        k, v = kv.split("=", 1)
        if k not in MEASURE_COLS or k in ("id", "pilot"):
            die(f"нет поля {k!r}")
        if k in VOCAB and v not in VOCAB[k]:
            die(f"{k}={v!r} вне словаря {sorted(VOCAB[k])}")
        pairs.append((k, v))
    hit = 0
    for r in rows:
        if r["id"] in ids:
            for k, v in pairs:
                r[k] = v
            hit += 1
    if hit != len(ids):
        die(f"найдено строк {hit} из {len(ids)}")
    write_tsv(path, MEASURE_COLS, rows)
    print(f"поправлено строк: {hit}")


# ---------- журналы сессий ----------

def project_logdir(pilot: str) -> Path:
    d = PILOT_DIRS.get(pilot)
    if not d:
        die(f"для {pilot} не задана папка проекта (PILOT_DIRS)")
    return CLAUDE_PROJECTS / re.sub(r"[^A-Za-z0-9]", "-", str(d))


def session_files(pilot: str, session: str | None) -> list[Path]:
    base = project_logdir(pilot)
    if not base.exists():
        return []
    mains = sorted(base.glob("*.jsonl"))
    if session == "latest":
        mains = sorted(mains, key=lambda p: p.stat().st_mtime)[-1:]
    elif session:
        mains = [p for p in mains if p.stem.startswith(session)]
    out = []
    for m in mains:
        out.append(m)
        out.extend(sorted((base / m.stem / "subagents").glob("*.jsonl")))
    return out


def iter_entries(path: Path):
    with path.open(encoding="utf-8") as f:
        for ln in f:
            try:
                yield json.loads(ln)
            except json.JSONDecodeError:
                continue


def parse_ts(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def collect_calls(pilot: str, session: str | None, since: str | None) -> list[dict]:
    since_ts = parse_ts(since) if since else None
    calls = []
    for p in session_files(pilot, session):
        sub = "subagents" in p.parts
        for e in iter_entries(p):
            ts = parse_ts(e.get("timestamp"))
            if since_ts and ts and ts < since_ts:
                continue
            m = e.get("message") or {}
            c = m.get("content")
            if e.get("type") == "user":
                text = c if isinstance(c, str) else " ".join(
                    b.get("text", "") for b in (c or []) if isinstance(b, dict) and b.get("type") == "text")
                for name in SLASH_RE.findall(text or ""):
                    calls.append({"ts": e.get("timestamp"), "kind": "skill", "name": "/" + name, "sub": "",
                                  "file": p.name, "agent": sub})
            if e.get("type") != "assistant" or not isinstance(c, list):
                continue
            for b in c:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                inp = b.get("input") or {}
                if b.get("name") == "Bash":
                    for util, subc in UTIL_RE.findall(inp.get("command", "")):
                        calls.append({"ts": e.get("timestamp"), "kind": "util", "name": util, "sub": subc or "",
                                      "file": p.name, "agent": sub})
                elif b.get("name") == "Skill":
                    calls.append({"ts": e.get("timestamp"), "kind": "skill", "name": "/" + str(inp.get("skill")),
                                  "sub": clean(inp.get("args", ""))[:40], "file": p.name, "agent": sub})
                elif b.get("name") == "Agent":
                    calls.append({"ts": e.get("timestamp"), "kind": "agent",
                                  "name": str(inp.get("subagent_type") or "general-purpose"),
                                  "sub": clean(inp.get("description", ""))[:40], "file": p.name, "agent": sub})
    return calls


def cmd_calls(a) -> None:
    calls = collect_calls(a.pilot, a.session, a.since)
    files = session_files(a.pilot, a.session)
    print(f"журналы: {len(files)} файлов в {project_logdir(a.pilot)}")
    cnt = collections.Counter((c["kind"], c["name"], c["sub"]) for c in calls)
    for (kind, name, sub), k in sorted(cnt.items()):
        print(f"{kind:6} {name:28} {sub:28} ×{k}")
    rows = read_tsv(pilot_dir(a.pilot) / "measure.tsv", MEASURE_COLS)
    recorded = {Path(r["tool"].split()[0]).name for r in rows if r["tool"] and r["tool"] not in ("чтение", "глаза", "судья")}
    called = {c["name"] for c in calls if c["kind"] == "util"}
    miss = sorted(called - recorded)
    extra = sorted(recorded - called - {"—"})
    print(f"\nутилиты звались, строк замера нет: {', '.join(miss) or '—'}")
    print(f"строки замера без вызова в журналах: {', '.join(extra) or '—'}")


def context_at(pilot: str, session: str, match: str | None, at: str | None) -> tuple[int, str]:
    files = [p for p in session_files(pilot, session) if "subagents" not in p.parts]
    if not files:
        die(f"нет журнала сессии {session!r} в {project_logdir(pilot)}")
    rx = re.compile(match) if match else None
    at_ts = parse_ts(at) if at else None
    last_ctx, last_ts = 0, ""
    for e in iter_entries(files[0]):
        m = e.get("message") or {}
        if e.get("type") != "assistant":
            continue
        u = m.get("usage") or {}
        ctx = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens",
                                               "cache_creation_input_tokens"))
        ts = parse_ts(e.get("timestamp"))
        if at_ts and ts and ts > at_ts:
            return last_ctx, last_ts
        if rx:
            for b in m.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and rx.search(json.dumps(b.get("input"),
                                                                                                ensure_ascii=False)):
                    return ctx, e.get("timestamp", "")
        if ctx:
            last_ctx, last_ts = ctx, e.get("timestamp", "")
    if rx:
        die(f"событие по {match!r} в журнале не найдено")
    return last_ctx, last_ts


def compactions(pilot: str, session: str | None) -> int:
    n = 0
    for p in session_files(pilot, session):
        if "subagents" in p.parts:
            continue
        for e in iter_entries(p):
            if (e.get("type") == "system" and e.get("subtype") == "compact_boundary") or e.get("isCompactSummary"):
                n += 1
    return n


def cmd_context(a) -> None:
    ctx, ts = context_at(a.pilot, a.session, a.match, a.at)
    print(f"{ctx}\t{ts}")


# ---------- траты ----------

def ledger_spent(pilot: str) -> tuple[float, dict]:
    path = PILOT_LEDGER.get(pilot)
    by: dict[str, float] = collections.defaultdict(float)
    if not path or not path.exists():
        return 0.0, {}
    jobs: dict[str, dict] = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(ln)
        except json.JSONDecodeError:
            continue
        uid = e.get("uid")
        if not uid:
            continue
        j = jobs.setdefault(uid, {})
        for k in ("base_url", "estimate_rub", "cost_rub"):
            if e.get(k) is not None:
                j[k] = e[k]
        j["state"] = e.get("event")
    total = 0.0
    for j in jobs.values():
        st = j.get("state")
        if st == "completed":
            s = float(j.get("cost_rub") if j.get("cost_rub") is not None else j.get("estimate_rub") or 0)
        elif st in ("failed", "cancelled"):
            s = float(j.get("cost_rub") or 0)
        elif st in ("http_error", "cache_hit", "upload", "rejected"):
            s = 0.0
        else:
            s = float(j.get("estimate_rub") or 0)
        by[j.get("base_url", "?")] += s
        total += s
    return round(total, 2), {k: round(v, 2) for k, v in by.items()}


def cmd_rub(a) -> None:
    total, by = ledger_spent(a.pilot)
    print(f"журнал: {PILOT_LEDGER.get(a.pilot)}")
    for k, v in by.items():
        print(f"  {k}: {v} ₽")
    print(f"итого: {total} ₽")


# ---------- sessions / findings ----------

def cmd_session(a) -> None:
    path = pilot_dir(a.pilot) / "sessions.tsv"
    calls = collect_calls(a.pilot, a.session, a.since)
    utils = collections.Counter(c["name"] for c in calls if c["kind"] == "util")
    ctx_fw = a.ctx_first_wireframe or ""
    if not ctx_fw and a.session:
        try:
            ctx_fw = str(context_at(a.pilot, a.session, r"canvas_input\.py\s+build.*--stage\s+wireframe", None)[0])
        except SystemExit:
            ctx_fw = "—"
    row = {"date": a.date or dt.date.today().isoformat(), "pilot": a.pilot, "part": a.part,
           "stages": a.stages or "", "work_min": a.work_min or "", "customer_min": a.customer_min or "",
           "decisions": a.decisions or "", "close_questions": a.close_questions or "",
           "usage_before": a.usage_before or "", "usage_after": a.usage_after or "",
           "ctx_first_wireframe": ctx_fw, "compactions": str(compactions(a.pilot, a.session)),
           "utilities": ", ".join(f"{k}×{v}" for k, v in utils.most_common()) or "—",
           "rub": str(ledger_spent(a.pilot)[0]), "sessions": a.session or "", "note": a.note or ""}
    append_rows(path, SESSION_COLS, [row])
    print("\t".join(clean(row[c]) for c in SESSION_COLS))


def cmd_finding(a) -> None:
    rows = read_tsv(FINDINGS, FINDING_COLS)
    n = next_id(rows, "F9-", 3)
    row = {"id": f"F9-{n:03d}", "pilot": a.pilot, "stage": a.stage or "—", "path": a.path or "—", "what": a.what,
           "weight": a.weight, "blocks": a.blocks, "proposal": a.proposal or "", "decision": a.decision or "",
           "check": a.check or "", "status": a.status}
    for k, voc in FINDING_VOCAB.items():
        v = row[k]
        if k == "decision" and v.startswith("отклонено:"):
            continue
        if v not in voc:
            die(f"{k}={v!r} вне словаря {sorted(voc)}")
    append_rows(FINDINGS, FINDING_COLS, [row])
    print(row["id"])


# ---------- summary / check ----------

def cmd_summary(a) -> None:
    pilots = a.pilots or sorted(p.name for p in PILOTS.glob("P*") if p.is_dir())
    out = ["# Замер пилотов Ф9", "", f"Пилоты: {', '.join(pilots)}. Собрано `tools/measure.py summary`.", ""]
    all_rows = []
    for p in pilots:
        all_rows += read_tsv(pilot_dir(p) / "measure.tsv", MEASURE_COLS)
    checks = [r for r in all_rows if r["kind"] == "check"]
    out += ["## По утилите и правилу", "",
            "| утилита | правило | прогонов | срабатываний | помогла | шум | спорно | правка | как есть | ложная |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    agg: dict[tuple, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in checks:
        tool = r["tool"].split()[0] if r["tool"] else "—"
        c = agg[(tool, r["rule"])]
        c["runs"] += 1
        c["hits"] += int(r["count"] or 0)
        if r["useful"]:
            c[r["useful"]] += 1
        if r["customer"]:
            c[r["customer"]] += 1
    for (tool, rule), c in sorted(agg.items()):
        out.append(f"| {tool} | {rule} | {c['runs']} | {c['hits']} | {c['помогла']} | {c['шум']} | {c['спорно']} "
                   f"| {c['правка']} | {c['как есть']} | {c['ложная']} |")
    def section(title: str, rows: list[dict], fields: tuple) -> None:
        out.extend(["", f"## {title}", ""])
        if not rows:
            out.append("—")
            return
        for r in rows:
            out.append("- " + " · ".join(f"{r[f]}" for f in fields if r.get(f)))
    section("Стопы сверх пяти гейтов", [r for r in all_rows if r["kind"] == "stop" and r["gate"] == "—"],
            ("id", "pilot", "unit", "tool", "rule", "finding", "reason"))
    byp = [r for r in all_rows if r["kind"] == "bypass" or r["bypass"] not in ("—", "")]
    section("Обходы с причинами", byp, ("id", "pilot", "unit", "rule", "bypass", "reason"))
    section("Прошло проверки, но отклонено", [r for r in all_rows if r["kind"] == "rejected"],
            ("id", "pilot", "unit", "stage", "finding", "reason"))
    noisy = [r for r in checks if r["level"] in ("error", "warning", "B", "S")
             and r["customer"] in ("как есть", "ложная")]
    section("Завалило проверку, но принято", noisy, ("id", "pilot", "unit", "tool", "rule", "level", "customer"))
    section("Снятые одобрения", [r for r in all_rows if r["kind"] == "approval-lost"],
            ("id", "pilot", "unit", "reason", "cost"))
    out.extend(["", "## Сидения и блоки", "", "| пилот | часть | этапы | мин работы | ваши мин | решений | ₽ |",
                "|---|---|---|---|---|---|---|"])
    for p in pilots:
        for s in read_tsv(pilot_dir(p) / "sessions.tsv", SESSION_COLS):
            out.append(f"| {p} | {s['part']} | {s['stages']} | {s['work_min']} | {s['customer_min']} "
                       f"| {s['decisions']} | {s['rub']} |")
    text = "\n".join(out) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"записано: {a.out}")
    else:
        print(text)


def cmd_check(a) -> None:
    pilots = a.pilots or sorted(p.name for p in PILOTS.glob("P*") if p.is_dir())
    errs = []
    for p in pilots:
        rows = read_tsv(pilot_dir(p) / "measure.tsv", MEASURE_COLS)
        seen = set()
        for i, r in enumerate(rows, 2):
            if not re.fullmatch(r"M-\d{4}", r["id"]) or r["id"] in seen:
                errs.append(f"{p}/measure.tsv:{i}: id {r['id']!r}")
            seen.add(r["id"])
            if r["pilot"] != p:
                errs.append(f"{p}/measure.tsv:{i}: pilot {r['pilot']!r}")
            for k, voc in VOCAB.items():
                if r[k] not in voc:
                    errs.append(f"{p}/measure.tsv:{i}: {k}={r[k]!r}")
            if not r["count"].isdigit():
                errs.append(f"{p}/measure.tsv:{i}: count {r['count']!r}")
            if r["bypass"] not in ("—", "") and not r["reason"]:
                errs.append(f"{p}/measure.tsv:{i}: обход без причины")
        read_tsv(pilot_dir(p) / "sessions.tsv", SESSION_COLS)
    for i, r in enumerate(read_tsv(FINDINGS, FINDING_COLS), 2):
        if not re.fullmatch(r"F9-\d{3}", r["id"]):
            errs.append(f"FINDINGS.tsv:{i}: id {r['id']!r}")
    for e in errs:
        print(e)
    print(f"ошибок формы: {len(errs)}")
    sys.exit(1 if errs else 0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("init")
    s.add_argument("pilot")
    s.set_defaults(fn=cmd_init)

    s = sp.add_parser("add")
    s.add_argument("pilot")
    s.add_argument("--tool", required=True, help="утилита с командой; «чтение», «глаза», «судья»")
    s.add_argument("--stage", required=True, help="id этапа phases.md")
    s.add_argument("--from-json", help="файл находок утилиты (JSON, JSON lines) или «-»")
    s.add_argument("--unit")
    s.add_argument("--kind", default="check", choices=sorted(VOCAB["kind"]))
    s.add_argument("--trigger", default="переход", choices=sorted(VOCAB["trigger"]))
    s.add_argument("--rule")
    s.add_argument("--level")
    s.add_argument("--gate")
    s.add_argument("--count", type=int)
    s.add_argument("--finding")
    s.add_argument("--useful", default="")
    s.add_argument("--customer", default="")
    s.add_argument("--bypass")
    s.add_argument("--reason")
    s.add_argument("--cost")
    s.add_argument("--note")
    s.set_defaults(fn=cmd_add)

    s = sp.add_parser("set")
    s.add_argument("pilot")
    s.add_argument("ids", nargs="+", help="M-NNNN … затем поля ключ=значение")
    s.set_defaults(fn=None)

    s = sp.add_parser("session")
    s.add_argument("pilot")
    s.add_argument("--part", required=True, help="С1, Б1 …")
    for k in ("date", "stages", "work-min", "customer-min", "decisions", "close-questions", "usage-before",
              "usage-after", "ctx-first-wireframe", "session", "since", "note"):
        s.add_argument("--" + k)
    s.set_defaults(fn=cmd_session)

    s = sp.add_parser("finding")
    s.add_argument("--pilot", required=True)
    s.add_argument("--what", required=True)
    s.add_argument("--stage")
    s.add_argument("--path")
    s.add_argument("--weight", default="средний")
    s.add_argument("--blocks", default="нет")
    s.add_argument("--proposal")
    s.add_argument("--decision", default="")
    s.add_argument("--check")
    s.add_argument("--status", default="открыто")
    s.set_defaults(fn=cmd_finding)

    s = sp.add_parser("calls")
    s.add_argument("pilot")
    s.add_argument("--session")
    s.add_argument("--since")
    s.set_defaults(fn=cmd_calls)

    s = sp.add_parser("context")
    s.add_argument("pilot")
    s.add_argument("--session", required=True)
    s.add_argument("--match")
    s.add_argument("--at")
    s.set_defaults(fn=cmd_context)

    s = sp.add_parser("rub")
    s.add_argument("pilot")
    s.set_defaults(fn=cmd_rub)

    s = sp.add_parser("summary")
    s.add_argument("pilots", nargs="*")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_summary)

    s = sp.add_parser("check")
    s.add_argument("pilots", nargs="*")
    s.set_defaults(fn=cmd_check)

    argv = sys.argv[1:]
    if argv[:1] == ["set"] and len(argv) > 1 and re.fullmatch(r"F9-\d{3}", argv[1]):
        ids = [x for x in argv[1:] if re.fullmatch(r"F9-\d{3}", x)]
        fields = [x for x in argv[1:] if "=" in x]
        if not fields:
            die("set F9-001 [F9-002 …] поле=значение …")
        cmd_set_finding(ids, fields)
        return
    if argv[:1] == ["set"]:
        ids = [x for x in argv[2:] if re.fullmatch(r"M-\d{4}", x)]
        fields = [x for x in argv[2:] if "=" in x]
        if len(argv) < 3 or not ids or not fields:
            die("set P2 M-0007 [M-0008 …] поле=значение …")
        a = argparse.Namespace(pilot=argv[1], ids=ids, fields=fields)
        cmd_set(a)
        return
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
