#!/usr/bin/env python3
"""Экспорт сводного чек-листа в YAML.

Читает 12-evaluation-checklists/02-master-checklist.md (строки таблиц `| UX-XXX-NN | … |`) и пишет
12-evaluation-checklists/master-checklist.yaml. Правки делаются в Markdown; YAML — производный артефакт.
Поля: id, block, block_title, sub_block, text, severity, severity_label, severity_note, check_method (коды файла),
check_method_class (visual/dom/script/scenario/human), source_file (полные пути от корня базы; сокращённые пути
`../09-mobile/04-...` и диапазоны `../04-components-patterns/01–04` раскрыты), source_section, source_raw,
evidence_level, failure_modes, related_ids.
Запуск из корня базы: python3 99-raw/tools/checklist_export.py
"""
import io, os, re, glob, json, datetime, collections

import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib")); import kbpaths  # перенос: scripts/lib
ROOT = str(kbpaths.kb("ux"))
os.chdir(ROOT)
MD = "12-evaluation-checklists/02-master-checklist.md"
OUT = "12-evaluation-checklists/master-checklist.yaml"

SEV = {"B": "блокер", "S": "серьёзно", "D": "желательно"}
WAY = {"DOM": "dom", "LNT": "script", "AXE": "script", "SCR": "scenario", "IMG": "visual", "JDG": "visual", "HUM": "human"}
LEVELS = r"\[(исследование|консенсус|система|практика|мнение|спорно|стандарт|данные|не проверено)\]"

FOLDERS = {os.path.basename(d): d for d in glob.glob("[0-9][0-9]-*") if os.path.isdir(d)}
def files_in(folder):
    return sorted(os.path.basename(f) for f in glob.glob(os.path.join(folder, "[0-9][0-9]-*.md")))

def resolve_token(tok, cur_folder):
    """Возвращает список путей от корня базы для одного токена в бэктиках; [] если это не путь."""
    t = tok.strip("`").strip()
    if t.startswith("../../ui/"):  # перенос: базы — kb/<база> без -research
        return [t.replace("../../", "")]
    if t.startswith("[") or t.startswith("UX-"):
        return []
    m = re.match(r"^\.\./(\d\d-[a-z0-9-]+)/(.*)$", t)
    if m:
        folder, rest = m.group(1), m.group(2)
        if folder not in FOLDERS: return []
        names = files_in(folder)
        if rest == "" : return [folder + "/"]
        r = re.match(r"^(\d\d)[–-](\d\d)$", rest)                      # диапазон 01–04
        if r:
            a, b = int(r.group(1)), int(r.group(2))
            return [f"{folder}/{n}" for n in names if a <= int(n[:2]) <= b]
        r = re.match(r"^(\d\d)(?:-?(?:\.\.\.|…|\*))?$", rest)              # 04-... / 04-* / 04
        if r:
            return [f"{folder}/{n}" for n in names if n.startswith(r.group(1) + "-")][:1]
        r = re.match(r"^(\d\d)-([a-z0-9-]*?)(?:\.\.\.|…|\*)$", rest)       # 03-mobile-...
        if r:
            return [f"{folder}/{n}" for n in names if n.startswith(r.group(1) + "-")][:1]
        if rest.endswith(".md"):
            return [f"{folder}/{rest}"] if rest in names else [f"{folder}/{rest}?"]
        return []
    m = re.match(r"^(\d\d)-[a-z0-9-]+\.md$", t)                            # соседний файл той же папки
    if m:
        if t in files_in(cur_folder): return [f"{cur_folder}/{t}"]
        for folder in FOLDERS:
            if t in files_in(folder): return [f"{folder}/{t}"]
        return [f"?/{t}"]
    return []

def q(s):
    return json.dumps(s, ensure_ascii=False)

def main():
    lines = io.open(MD, encoding="utf-8").read().split("\n")
    meta_line = next((l for l in lines[:12] if "пунктов" in l), "")
    items, blocks = [], collections.OrderedDict()
    block = title = sub = None
    prev_files = []
    for l in lines:
        m = re.match(r"^##+ (?:\d+\.\d+ |\d+\. Блок )?([A-Z0-9]{3}) — (.+)$", l)
        if m:
            block, title, sub = m.group(1), m.group(2).strip(), None
            blocks[block] = title; prev_files = []; continue
        m = re.match(r"^\*\*([A-Z]{3}) — (.+)\*\*$", l)
        if m and block == "APP":
            sub = m.group(1); continue
        m = re.match(r"^\| (UX-([A-Z0-9]{3})-(\d{2})) \| (.+?) \| ([BSD]) \| ([A-Z, ]+) \| (.*) \|\s*$", l)
        if not m: continue
        uid, code, num, text, sev, way, src = m.groups()
        ways = [w.strip() for w in way.split(",") if w.strip()]
        toks = re.findall(r"`[^`]+`", src)
        files = []
        for t in toks:
            for f in resolve_token(t, "12-evaluation-checklists"):
                if f not in files: files.append(f)
        if not files and re.search(r"там же", src) and prev_files:
            files = list(prev_files)
        if not files:  # запасные сопоставления для ячеек без пути
            if re.search(r"дефект F\d|\bF\d{1,2}\.\d", src): files.append("11-ai-generated-ui/01-failure-modes-catalog.md")
            if re.search(r"FullFront|UI2App|WebGen|Design2Code|A11yn", src): files.append("11-ai-generated-ui/02-research-and-benchmarks.md")
            if re.search(r"\[S\d+\]", src): files.append("12-evaluation-checklists/02-master-checklist.md")
            if re.search(r"\b[1-4]\.\d{1,2}\.\d{1,2}\b", src): files.append("08-accessibility/01-wcag22-as-build-rules.md")
            if re.search(r"\baxe\b|автоматикой|grayscale", src): files.append("12-evaluation-checklists/03-automated-checks.md")
        if files: prev_files = files
        section = re.sub(r"`[^`]+`", "", src)
        section = re.sub(r"\s+", " ", section).strip(" ;,—-")
        levels = re.findall(LEVELS, src)
        fms = sorted(set(re.findall(r"\bF\d{1,2}\.\d{1,2}\b", src)))
        related = sorted(set(re.findall(r"\bUX-[A-Z0-9]{3}-\d{2}\b", src)))
        wave4 = (code in ("ADM", "CLI", "AIF", "PRC")) or (code == "CNS" and int(num) >= 7)
        items.append({
            "id": uid, "block": "APP" if code in ("ADM", "CLI", "AIF", "PRC") else code,
            "block_title": blocks.get("APP" if code in ("ADM", "CLI", "AIF", "PRC") else code, title or ""),
            "sub_block": sub if code in ("ADM", "CLI", "AIF", "PRC") else "",
            "text": text.strip(), "severity": sev, "severity_label": SEV[sev],
            "severity_note": "назначено агентом S1 (волна 4), не измерено" if wave4 else "назначено агентом I, не измерено",
            "check_method": ways, "check_method_class": [WAY.get(w, "?") for w in ways],
            "check_method_main": WAY.get(ways[0], "?") if ways else "",
            "source_file": files, "source_section": section, "source_raw": src.strip(),
            "evidence_level": levels, "failure_modes": fms, "related_ids": related,
        })
    unresolved = [(i["id"], f) for i in items for f in i["source_file"] if "?" in f]
    no_src = [i["id"] for i in items if not i["source_file"]]
    out = ["# Машиночитаемая версия 12-evaluation-checklists/02-master-checklist.md.",
           "# Сгенерировано скриптом 99-raw/tools/checklist_export.py — правки вносить в Markdown и перегенерировать.",
           f"generated_at: {q(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))}",
           f"source_md: {q(MD)}", f"source_md_meta: {q(meta_line.strip())}", f"items_count: {len(items)}",
           "severity_scale: {B: блокер, S: серьёзно, D: желательно}",
           "severity_note_default: " + q("серьёзность назначена агентом I (волна 3) по свёртке шкалы Нильсена 0–4; для блоков CNS-07…29 и APP — агентом S1 (волна 4); не измерена (см. 02-master-checklist.md, «Открытые вопросы» п.2)"),
           "check_method_codes: {DOM: dom, LNT: script, AXE: script, SCR: scenario, IMG: visual, JDG: visual, HUM: human}",
           "check_method_note: " + q("коды файла: DOM — разбор DOM/кода страницы; LNT — линтер по исходникам; AXE — axe-core/Lighthouse; SCR — сценарий в headless-браузере; IMG — анализ скриншота; JDG — мультимодальный судья по рубрике; HUM — только человек. JDG и HUM не ставят автоматических ворот"),
           "blocks:"]
    for b, t in blocks.items():
        out.append(f"  - {{code: {b}, title: {q(t)}, items: {sum(1 for i in items if i['block'] == b)}}}")
    out.append("items:")
    for i in items:
        out.append(f"  - id: {i['id']}")
        out.append(f"    block: {i['block']}")
        out.append(f"    block_title: {q(i['block_title'])}")
        if i["sub_block"]: out.append(f"    sub_block: {i['sub_block']}")
        out.append(f"    text: {q(i['text'])}")
        out.append(f"    severity: {i['severity']}")
        out.append(f"    severity_label: {q(i['severity_label'])}")
        out.append(f"    severity_note: {q(i['severity_note'])}")
        out.append(f"    check_method: [{', '.join(i['check_method'])}]")
        out.append(f"    check_method_class: [{', '.join(i['check_method_class'])}]")
        out.append(f"    check_method_main: {i['check_method_main']}")
        out.append(f"    source_file: [{', '.join(q(f) for f in i['source_file'])}]")
        out.append(f"    source_section: {q(i['source_section'])}")
        out.append(f"    source_raw: {q(i['source_raw'])}")
        out.append(f"    evidence_level: [{', '.join(q(x) for x in i['evidence_level'])}]")
        if i["failure_modes"]: out.append(f"    failure_modes: [{', '.join(i['failure_modes'])}]")
        if i["related_ids"]: out.append(f"    related_ids: [{', '.join(i['related_ids'])}]")
    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    ok = ""
    try:
        import yaml
        data = yaml.safe_load(io.open(OUT, encoding="utf-8").read())
        ok = f"; YAML валиден, items={len(data['items'])}"
    except ImportError:
        ok = "; модуль yaml не установлен — валидность не проверена"
    except Exception as e:
        ok = f"; ОШИБКА YAML: {e}"
    by_block = collections.Counter(i["block"] for i in items)
    n_full = sum(1 for i in items if i["source_file"])
    n_range = sum(1 for i in items if len([f for f in i["source_file"] if not f.startswith("ui/")]) > 1)
    print(f"пунктов {len(items)}; блоков {len(blocks)}; с source_file {n_full}; без источника-файла {len(no_src)}; многофайловых (диапазоны/списки) {n_range}; нераскрытых путей {len(unresolved)}{ok}")
    print("по блокам:", dict(by_block))
    if unresolved: print("нераскрытые:", unresolved[:12])
    if no_src: print("без файла-источника:", no_src[:40], "…" if len(no_src) > 40 else "")

if __name__ == "__main__":
    main()
