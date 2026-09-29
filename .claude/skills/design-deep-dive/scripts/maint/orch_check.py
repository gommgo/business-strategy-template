#!/usr/bin/env python3
"""Приёмочная проверка файлов базы site (`kb/site/`) по формату базы: разделы, метки, штампы, машинные файлы, ссылки.

Использование:
    python3 .claude/skills/design-deep-dive/scripts/maint/orch_check.py [ПАПКА ...] [--selftest-tools]
    ПАПКА — путь от корня базы (например 03-page-structure) или all (все тематические папки 00–10, 90-sources,
    91-videos; без папок — тоже все).

Что проверяет:
- содержательные .md (кроме README): число строк; обязательные разделы формата базы: «Выжимка для агента», «Частые
  ошибки», «Чек-лист», «Открытые вопросы», «Источники»; строка метаданных под заголовком; остаток пометки
  `<!-- ЧЕРНОВИК`; метки доказательности (известные и неизвестные); штампы, которых база не допускает в своём тексте;
- .yaml/.yml — загрузка `yaml.safe_load` и наличие поля `date` на верхнем уровне (или в первом словаре);
- .json — загрузка `json.load`; для `*.schema.json` — наличие `$schema`;
- README в каждой папке с файлами;
- относительные ссылки на файлы в .md (`../…` и пути от корня базы в обратных кавычках) — существуют ли;
- с `--selftest-tools` — `--selftest` утилит базы в `scripts/site/` (vocab_lint.py, page_anatomy.py, site_validate.py и
  другие из списка TOOLS), если файл есть.
Коды выхода: 0 — замечаний уровня error нет; 1 — есть error.
"""
import argparse, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb("site"))
FOLDERS = ["00-glossary", "01-foundations", "02-site-types", "03-page-structure", "04-blocks", "05-conversion-funnels",
           "06-multipage-ia", "07-seo-geo-performance-analytics", "08-legal-trust-a11y", "09-ai-generation-evaluation",
           "10-playbooks-contracts", "90-sources", "91-videos"]
REQUIRED = [("выжимка", r"^##\s+Выжимка для агента"), ("ошибки", r"^##\s+(\d+\.\s*)?Частые ошибки"),
            ("чек-лист", r"^##\s+(\d+\.\s*)?Чек-лист"), ("открытые вопросы", r"^##\s+(\d+\.\s*)?Открытые вопросы"),
            ("источники", r"^##\s+(\d+\.\s*)?Источники")]
LABELS = ["исследование", "консенсус", "стандарт", "документация", "данные", "кейс", "практика", "мнение", "спорно",
          "проверено", "не проверено", "мнение вендора", "правоприменение", "награда", "гипотеза", "регулятор",
          "вендор-GEO"]
# Штампы, которых база не должна допускать в собственном тексте (_common.md, «Формат итоговых файлов»).
STAMPS = [r"в современном мире", r"важно отметить", r"играет ключевую роль", r"не только\s[^.]{0,60}?,\s*но и",
          r"(?<![А-Яа-яЁё])является(?![А-Яа-яЁё])", r"(?<![А-Яа-яЁё])данн(ый|ая|ое|ого|ой|ому|ую)(?![А-Яа-яЁё])"]  # «данные» (data) не штамп
TOOLS = ["vocab_lint.py", "page_anatomy.py", "ia_probe.py", "geo_probe.py", "page_gates.py", "ab_plan.py",
         "checklist_export.py", "site_validate.py", "plan_to_assets.py"]


def rel(p):
    return os.path.relpath(p, ROOT)


def check_md(path, out):
    text = open(path, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()
    n = len(lines)
    base = os.path.basename(path)
    issues = []
    if base.lower() == "readme.md" or "/91-videos/" in path:
        kind = "readme" if base.lower() == "readme.md" else "video"
    else:
        kind = "content"
    if lines and lines[0].startswith("<!-- ЧЕРНОВИК"):
        issues.append(("error", "первая строка — пометка ЧЕРНОВИК"))
    elif "<!-- ЧЕРНОВИК" in text:
        issues.append(("warning", "в тексте осталась пометка ЧЕРНОВИК"))
    if kind == "content":
        for name, rx in REQUIRED:
            if not re.search(rx, text, re.M | re.I):
                issues.append(("warning", f"нет раздела «{name}»"))
        head = "\n".join(lines[:6])
        if not re.search(r"(Волна|волна)\s*\d|·", head):
            issues.append(("info", "нет строки метаданных под заголовком"))
        if n < 150:
            issues.append(("info", f"короткий файл: {n} строк"))
        if n > 700:
            issues.append(("info", f"длинный файл: {n} строк"))
    found = re.findall(r"\[(" + "|".join(re.escape(l) for l in LABELS) + r")(?=[\]:;,\s])", text)
    unknown = set()
    text_nocode = re.sub(r"`[^`\n]*`", "``", text)  # скобки внутри кода (`Content-Usage: [путь] …`) — не метки
    for m in re.finditer(r"\[([а-яё][а-яё \-]{2,30})\]", text_nocode):
        lab = m.group(1).strip()
        if lab not in LABELS and not lab.startswith("V:") and len(lab.split()) <= 3 and len(lab) >= 4 \
                and not re.search(r"[а-яё]-[а-яё]", lab):
            unknown.add(lab)
    stamps = {}
    for rx in STAMPS:
        c = len(re.findall(rx, text, re.I))
        if c:
            stamps[rx] = c
    broken = []
    here = os.path.dirname(path)
    cands = set(re.findall(r"\]\((\.\./[^)\s#]+|[0-9]{2}-[^)\s#]+)\)", text))
    cands |= set(re.findall(r"`(\.\./[^`\s]+?)`", text))
    for c in sorted(cands):
        c2 = re.sub(r"[:#].*$", "", c).rstrip(".,;")
        if "*" in c2 or "<" in c2 or "…" in c2 or c2.endswith("-"):
            continue
        p1 = os.path.normpath(os.path.join(here, c2))
        p2 = os.path.normpath(os.path.join(ROOT, c2))
        if not (os.path.exists(p1) or os.path.exists(p2)):
            broken.append(c2)
    if broken:
        issues.append(("warning", f"ссылки не найдены ({len(broken)}): " + "; ".join(broken[:6])))
    out.append({"file": rel(path), "kind": kind, "lines": n, "issues": issues, "labels": len(found),
                "unknown_labels": sorted(unknown)[:12], "stamps": stamps})


def check_yaml(path, out):
    import yaml
    issues = []
    try:
        docs = list(yaml.safe_load_all(open(path, encoding="utf-8")))
        d = docs[0] if docs else None
        has_date = False
        if isinstance(d, dict):
            has_date = "date" in d or any(isinstance(v, dict) and "date" in v for v in d.values())
        elif isinstance(d, list) and d and isinstance(d[0], dict):
            has_date = "date" in d[0]
        if not has_date:
            issues.append(("info", "нет поля date на верхнем уровне"))
    except Exception as e:
        issues.append(("error", f"YAML не загружается: {str(e)[:160]}"))
    out.append({"file": rel(path), "kind": "yaml", "lines": sum(1 for _ in open(path, encoding="utf-8", errors="replace")),
                "issues": issues})


def check_json(path, out):
    issues = []
    try:
        d = json.load(open(path, encoding="utf-8"))
        if path.endswith(".schema.json") and "$schema" not in d:
            issues.append(("warning", "в схеме нет $schema"))
    except Exception as e:
        issues.append(("error", f"JSON не загружается: {str(e)[:160]}"))
    out.append({"file": rel(path), "kind": "json", "lines": sum(1 for _ in open(path, encoding="utf-8", errors="replace")),
                "issues": issues})


def walk(folder, out):
    full = os.path.join(ROOT, folder)
    if not os.path.isdir(full):
        return
    has_files = False
    for dp, dn, fn in os.walk(full):
        dn[:] = [d for d in dn if d not in ("transcripts",)]
        for f in sorted(fn):
            p = os.path.join(dp, f)
            has_files = True
            if f.endswith(".md"):
                check_md(p, out)
            elif f.endswith((".yaml", ".yml")):
                check_yaml(p, out)
            elif f.endswith(".json"):
                check_json(p, out)
    if has_files and folder not in ("91-videos", "90-sources", "00-glossary") and \
            not os.path.exists(os.path.join(full, "README.md")):
        out.append({"file": folder + "/README.md", "kind": "readme", "lines": 0,
                    "issues": [("warning", "нет README папки")]})


def selftest_tools(out):
    for t in TOOLS:
        p = str(kbpaths.scripts("site", t))
        if not os.path.exists(p):
            continue
        try:
            r = subprocess.run([sys.executable, p, "--selftest"], capture_output=True, text=True, timeout=600, cwd=ROOT)
            lvl = None if r.returncode == 0 else "error"
            tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
            out.append({"file": rel(p), "kind": "tool", "lines": sum(1 for _ in open(p, encoding="utf-8")),
                        "issues": ([(lvl, f"--selftest вернул {r.returncode}: {' | '.join(tail)[:300]}")] if lvl else
                                   [("info", f"--selftest ok: {' | '.join(tail)[:200]}")])})
        except subprocess.TimeoutExpired:
            out.append({"file": rel(p), "kind": "tool", "lines": 0, "issues": [("error", "--selftest завис (600 с)")]})


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], epilog=__doc__.split("\n", 2)[2],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="*", help="папки от корня базы или all")
    ap.add_argument("--selftest-tools", action="store_true", help="ещё --selftest утилит базы в scripts/site/")
    a = ap.parse_args()
    folders = FOLDERS if (not a.folders or "all" in a.folders) else a.folders
    out = []
    for f in folders:
        walk(f, out)
    if a.selftest_tools:
        selftest_tools(out)
    errors = 0
    for r in out:
        iss = r["issues"]
        errors += sum(1 for l, _ in iss if l == "error")
        flag = "ERROR" if any(l == "error" for l, _ in iss) else ("warn" if any(l == "warning" for l, _ in iss) else "ok")
        extra = ""
        if r["kind"] in ("content", "readme", "video"):
            extra = f" · меток {r.get('labels', 0)}"
            if r.get("stamps"):
                extra += " · штампы " + ", ".join(f"{k[:24]}×{v}" for k, v in r["stamps"].items())
            if r.get("unknown_labels"):
                extra += " · незнакомые метки: " + "; ".join(r["unknown_labels"])
        print(f"[{flag}] {r['file']} ({r['kind']}, {r['lines']} стр.){extra}")
        for l, m in iss:
            if l in ("error", "warning") or r["kind"] == "tool":
                print(f"    {l}: {m}")
    print(f"\nфайлов: {len(out)}; ошибок: {errors}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
