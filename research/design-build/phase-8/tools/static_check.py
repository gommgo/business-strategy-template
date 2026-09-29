#!/usr/bin/env python3
"""Статическая проверка Ф8 (phase-8/PLAN.md §6): всё, кроме полного смоука, соседнего чекаута и прогона по сценариям,
одним прогоном.

Что проверяет (от базового коммита Ф8 до рабочего дерева):
  1. refcheck --strict (scripts/maint) по md, правленым в Ф8, без фикстур и 99-raw: находки в новых файлах и в
     изменённых строках правленых — ошибка; в нетронутых строках — счётом (прежний текст, хвосты для уборки Ф10);
  2. следы в scripts/: прежний исполнитель макета (kimi, K3 как слово, `kimi -p`), модели других вендоров, Р- и
     Ф-номера — списком на разбор (снимки данных, id проверки K3 группы K ui_audit и модели генерации ai-media —
     законны); фразы «пока утилиты нет» в текстах шаблона — ошибка;
  3. YAML, JSON, JSONL и frontmatter md, новые и правленые в Ф8, парсятся;
  4. схемы kb вне 99-raw — метасхема Draft 2020-12; примеры баз — свои схемы (таблица SCHEMA_EXAMPLES);
  5. scripts/maint: mapcheck kb/INDEX.md — «НЕ НОРМА» 0; canon_check — 0 ошибок; sync_check — код 0 (генераторы,
     фикстуры, копия грамматики, описания скиллов);
  6. реестр и canon.tsv: пересборка registry.py merge и canon совпадает с файлами байт в байт;
  7. тесты scripts/*/tests/test_*.py — код 0 (тесты Blender — ключом --blender, через blender_run.py).

Запуск из корня: python3 research/design-build/phase-8/tools/static_check.py [--base a3836aa] [--blender] [-v]
Код выхода: 0 — всё чисто; 1 — есть находки. Схемы и тесты — Python окружения $DDD_HOME (jsonschema).
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
JOURNAL = ROOT / "research" / "design-build"
SK = ROOT / ".claude" / "skills" / "design-deep-dive"
MAINT = SK / "scripts" / "maint"
REGISTRY = JOURNAL / "phase-4" / "tools" / "registry.py"
CANON = SK / "kb" / "common" / "canon.tsv"
DDD_HOME = Path(os.environ.get("DDD_HOME", Path.home() / ".cache" / "design-deep-dive"))
VENV_PY = DDD_HOME / "venv" / "bin" / "python"
HIT = re.compile(r"^\s+([A-ZА-ЯЁ]+)\s*·\s*(\d+):")

# Схема (от kb/) → маски примеров (от kb/). Схемы v0 и v0.9 (код их не читает) — только метасхема. Overlay подачи
# (`*.treatment.yaml`: {overlay_version, plan, page, sections}) — не документ схемы treatment, а её контейнеры на плане:
# его проверяет spec_check.py plan <план> --overlay <overlay> (OVERLAYS ниже).
SCHEMA_EXAMPLES = {
    "site/10-playbooks-contracts/schemas/site-brief.schema.json": ["site/10-playbooks-contracts/examples/*/site-brief.yaml"],
    "site/10-playbooks-contracts/schemas/page-plan.schema.json": ["site/10-playbooks-contracts/examples/*/plans/*.yaml"],
    "site/10-playbooks-contracts/schemas/site-map.schema.json": ["site/10-playbooks-contracts/examples/*/site-map.yaml"],
    "site/10-playbooks-contracts/schemas/blocks.schema.json": ["site/04-blocks/blocks.yaml"],
    "common/brand.schema.yaml": ["site/10-playbooks-contracts/examples/*/brand.yaml"],
    "text/02-strategy-messaging/facts.schema.yaml": ["site/10-playbooks-contracts/examples/*/facts.yaml",
                                                     "text/02-strategy-messaging/examples/facts-*.yaml",
                                                     "text/10-templates-recipes/examples/facts/*.yaml"],
    "text/02-strategy-messaging/meaning.schema.yaml": ["text/02-strategy-messaging/examples/meaning-*.yaml"],
    "text/02-strategy-messaging/message-hierarchy.schema.yaml": ["text/02-strategy-messaging/examples/hierarchy-*.yaml"],
    "text/05-voice-editorial/voice.schema.yaml": ["text/05-voice-editorial/examples/voice-*.yaml"],
    "text/10-templates-recipes/copy-deck.schema.json": ["text/10-templates-recipes/examples/*.yaml"],
    "creative/09-ai-execution-evaluation/art-direction.v1.schema.json": [
        "creative/01-creative-direction/examples/art-direction-*.json",
        "creative/09-ai-execution-evaluation/examples/art-direction-*.v1.json"],
    "creative/09-ai-execution-evaluation/motion-spec.schema.json": [
        "creative/09-ai-execution-evaluation/examples/*.motion-spec.yaml", "creative/10-recipes/examples/*/motion-spec.yaml"],
    "creative/10-recipes/recipes/recipe.schema.json": ["creative/10-recipes/recipes/*.recipe.yaml"],
    "creative/06-effects-catalog/effects.schema.json": ["creative/06-effects-catalog/effects.yaml"],
    "creative/02-references-moodboards/refs-library.schema.json": ["creative/02-references-moodboards/library-example/library.jsonl"],
    "ai-media/05-prompting/asset-plan.schema.json": ["site/10-playbooks-contracts/examples/*/asset-plan.*.yaml"],
    "ai-media/05-prompting/asset-spec.schema.json": ["ai-media/14-recipes/examples/demo-landing/brand/specs/*.spec.json"],
    "ai-media/06-art-direction-consistency/visual-dna.schema.json": [
        "ai-media/06-art-direction-consistency/examples/dna-*.json", "ai-media/14-recipes/examples/demo-landing/brand/dna-*.json"],
    "ai-media/14-recipes/recipes/recipe.schema.json": ["ai-media/14-recipes/recipes/*.yaml"],
}

OVERLAYS = "creative/09-ai-execution-evaluation/examples/*.treatment.yaml"

TRACE_CODE = [
    ("прежний исполнитель", re.compile(r"kimi|(?<![\w-])K3(?![\w-])", re.I)),
    ("модель другого вендора", re.compile(r"gemini|qwen|\bgpt-|claude-3|llama|mistral", re.I)),
    ("Р-номер", re.compile(r"(?<![\w-])Р\d{1,3}(?![\w-])")),
    ("Ф-номер", re.compile(r"(?<![\w-])Ф\d{1,2}(?![\w-])")),
]
TRACE_TEXT = re.compile(r"пока (?:такой )?утилит\w* нет|утилит\w* пока нет|когда появится утилит|до появления утилит"
                        r"|утилиты ещё нет|утилита появится", re.I)

# Юникод-загрузчик YAML без преобразования дат: схемы ждут строки.
LOADER = r'''
import yaml
class L(yaml.SafeLoader): pass
L.yaml_implicit_resolvers = {k: [r for r in v if r[0] != "tag:yaml.org,2002:timestamp"]
                             for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()}
def load(p):
    t = open(p, encoding="utf-8").read()
    if p.endswith(".json"): import json; return json.loads(t)
    if p.endswith(".jsonl"): import json; return [json.loads(x) for x in t.splitlines() if x.strip()]
    return yaml.load(t, Loader=L)
'''

SCHEMA_CODE = LOADER + r'''
import json, sys, jsonschema
from pathlib import Path
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
kb = Path(sys.argv[1]); spec = json.loads(sys.argv[2]); bad = 0; n_ex = 0
schemas = sorted(p for p in kb.rglob("*.schema.*") if "99-raw" not in p.parts and p.suffix in (".json", ".yaml"))
res = []
for s in schemas:
    try:
        d = load(str(s)); jsonschema.Draft202012Validator.check_schema(d)
        r = Resource.from_contents(d, default_specification=DRAFT202012)
        res += [(s.resolve().as_uri(), r)] + ([(d["$id"], r)] if d.get("$id") else [])
    except Exception as e:
        bad += 1; print("  МЕТАСХЕМА:", s.relative_to(kb), str(e).splitlines()[0][:200])
reg = Registry().with_resources(res)
print(f"  схем {len(schemas)}, против метасхемы — ошибок {bad}")
for rel, masks in spec.items():
    sch = load(str(kb / rel)); v = jsonschema.Draft202012Validator(sch, registry=reg)
    files = sorted({f for m in masks for f in kb.glob(m)})
    if not files:
        bad += 1; print("  НЕТ ПРИМЕРОВ:", rel, masks); continue
    for f in files:
        doc = load(str(f)); docs = doc if f.suffix == ".jsonl" else [doc]
        for i, d in enumerate(docs):
            errs = sorted(v.iter_errors(d), key=lambda e: list(e.absolute_path))
            n_ex += 1
            for e in errs[:3]:
                bad += 1
                loc = "/".join(map(str, e.absolute_path)) or "(корень)"
                print(f"  ПРИМЕР: {f.relative_to(kb)}{'#' + str(i + 1) if f.suffix == '.jsonl' else ''}: {loc}: {e.message[:160]}")
            if len(errs) > 3:
                bad += len(errs) - 3; print(f"    … ещё {len(errs) - 3}")
print(f"  примеров (документов) {n_ex} по {len(spec)} схемам; ошибок всего {bad}")
sys.exit(1 if bad else 0)
'''


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def changed_files(base):
    out = git("diff", "--name-only", base, "--", ".claude", "docs", "CLAUDE.md", "README.md", "CONTRIBUTING.md")
    new = set(git("diff", "--name-only", "--diff-filter=A", base, "--", ".claude", "docs").split())
    files = [f for f in out.split() if (ROOT / f).exists()]
    return files, new


def changed_lines(base, f):
    diff = git("diff", "-U0", base, "--", f)
    lines = set()
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff, re.M):
        start, cnt = int(m.group(1)), int(m.group(2) or 1)
        lines.update(range(start, start + cnt))
    return lines


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=kw.pop("cwd", ROOT), capture_output=True, text=True, **kw)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="a3836aa", help="коммит закрытия Ф7 — начало Ф8")
    ap.add_argument("--blender", action="store_true", help="ещё тесты Blender (blender -b через blender_run.py)")
    ap.add_argument("-v", action="store_true", help="подробный вывод sync_check и canon_check")
    a = ap.parse_args()
    files, new = changed_files(a.base)
    bad = 0

    # 1. refcheck
    md = sorted(f for f in files if f.endswith(".md") and "/scripts/tests/fixtures/" not in f and "/99-raw/" not in f)
    in_changed, untouched = [], 0
    for f in md:
        out = run([sys.executable, str(MAINT / "refcheck.py"), "--strict", f]).stdout
        cl = None if f in new else changed_lines(a.base, f)
        for line in out.splitlines():
            m = HIT.match(line)
            if not m:
                continue
            if cl is None or int(m.group(2)) in cl:
                in_changed.append(f"{f}: {line.strip()}")
            else:
                untouched += 1
    print(f"1. refcheck --strict: {len(md)} md; находок в новых файлах и изменённых строках — {len(in_changed)}; "
          f"в нетронутых строках — {untouched}")
    for h in in_changed:
        print("   !!", h)
    bad |= bool(in_changed)

    # 2. следы
    code_hits = {}
    for p in sorted((SK / "scripts").rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or "fixtures" in p.parts:
            continue
        if p.suffix not in (".py", ".sh", ".js", ".mjs", ".yaml", ".yml", ".json", ".tsv", ".md", ".txt"):
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for name, rx in TRACE_CODE:
                if rx.search(line):
                    code_hits.setdefault(name, []).append(f"{p.relative_to(ROOT)}:{n}: {line.strip()[:150]}")
    print("2. следы в scripts/ (на разбор): " + ", ".join(f"{k} — {len(v)}" for k, v in code_hits.items()) or "0")
    for name, hits in code_hits.items():
        for h in hits:
            print(f"   ?? [{name}] {h}")
    text_hits = []
    for base in (ROOT / ".claude", ROOT / "docs"):
        for p in sorted(base.rglob("*.md")):
            if "99-raw" in p.parts or "fixtures" in p.parts:
                continue
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if TRACE_TEXT.search(line):
                    text_hits.append(f"{p.relative_to(ROOT)}:{n}: {line.strip()[:150]}")
    print(f"   фразы «пока утилиты нет» в текстах шаблона: {len(text_hits)}")
    for h in text_hits:
        print("   !!", h)
    bad |= bool(text_hits)

    # 3. YAML, JSON, JSONL, frontmatter
    try:
        import yaml
    except ImportError:
        yaml = None
    perr = []
    for f in files:
        p = ROOT / f
        try:
            if f.endswith((".yaml", ".yml")) and yaml:
                list(yaml.safe_load_all(p.read_text(encoding="utf-8")))
            elif f.endswith(".json"):
                json.loads(p.read_text(encoding="utf-8"))
            elif f.endswith(".jsonl"):
                for line in p.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        json.loads(line)
            elif f.endswith(".md") and yaml:
                t = p.read_text(encoding="utf-8")
                if t.startswith("---\n"):
                    yaml.safe_load(t.split("---", 2)[1])
        except Exception as e:  # noqa: BLE001
            perr.append(f"{f}: {str(e).splitlines()[0][:200]}")
    print(f"3. YAML, JSON, JSONL и frontmatter ({len(files)} файлов Ф8): ошибок {len(perr)}")
    for e in perr:
        print("   !!", e)
    bad |= bool(perr)

    # 4. схемы и примеры
    r = run([str(VENV_PY), "-c", SCHEMA_CODE, str(SK / "kb"), json.dumps(SCHEMA_EXAMPLES)])
    print("4. схемы kb и примеры баз:" + ("" if r.returncode == 0 else "  (есть ошибки)"))
    print(r.stdout.rstrip() or r.stderr[-800:])
    bad |= r.returncode != 0
    ov_bad = []
    ovs = sorted((SK / "kb").glob(OVERLAYS))
    for o in ovs:
        doc = yaml.safe_load(o.read_text(encoding="utf-8")) if yaml else {}
        plan = (o.parent / str((doc or {}).get("plan", ""))).resolve()
        rr = run([str(VENV_PY), str(SK / "scripts" / "creative" / "spec_check.py"), "plan", str(plan), "--overlay", str(o)],
                 cwd=SK)
        if rr.returncode != 0:
            ov_bad.append(f"{o.relative_to(SK)} (код {rr.returncode}): {(rr.stdout + rr.stderr).strip().splitlines()[-1][:160]}")
    print(f"  overlay подачи — spec_check.py plan --overlay: {len(ovs)}, с ошибками — {len(ov_bad)}")
    for x in ov_bad:
        print("   !!", x)
    bad |= bool(ov_bad)

    # 5. обслуживание
    mc = run([sys.executable, str(MAINT / "mapcheck.py"), str(SK / "kb" / "INDEX.md")])
    notnorm, chk = mc.stdout.count("НЕ НОРМА"), mc.stdout.count("ПРОВЕРИТЬ")
    print(f"5. mapcheck kb/INDEX.md: «НЕ НОРМА» {notnorm}, «ПРОВЕРИТЬ» {chk}")
    bad |= notnorm > 0
    cc = run([sys.executable, str(MAINT / "canon_check.py")])
    tail = [l for l in (cc.stdout + cc.stderr).splitlines() if l.strip()]
    print(f"   canon_check: код {cc.returncode}; {tail[-1] if tail else ''}")
    if a.v or cc.returncode:
        for l in tail[-15:]:
            print("     ", l)
    bad |= cc.returncode != 0
    sc = run([str(VENV_PY), str(MAINT / "sync_check.py")], cwd=SK)
    tail = [l for l in (sc.stdout + sc.stderr).splitlines() if l.strip()]
    print(f"   sync_check: код {sc.returncode}")
    for l in (tail if a.v or sc.returncode else tail[-6:]):
        print("     ", l)
    bad |= sc.returncode != 0

    # 6. реестр и canon.tsv
    with tempfile.TemporaryDirectory() as td:
        reg, can = Path(td) / "registry.tsv", Path(td) / "canon.tsv"
        run([sys.executable, str(REGISTRY), "merge", "--out", str(reg)], cwd=REGISTRY.parents[1])
        run([sys.executable, str(REGISTRY), "canon", "--registry", str(reg), "--out", str(can)], cwd=REGISTRY.parents[1])
        same_reg = reg.exists() and reg.read_bytes() == (JOURNAL / "phase-4" / "registry.tsv").read_bytes()
        same_can = can.exists() and can.read_bytes() == CANON.read_bytes()
    chk_reg = run([sys.executable, str(REGISTRY), "check", *sorted(glob.glob(str(REGISTRY.parents[1] / "nodes" / "*.tsv")))],
                  cwd=REGISTRY.parents[1])
    print(f"6. пересборка: registry.tsv {'байт в байт' if same_reg else 'РАСХОДИТСЯ'}, canon.tsv "
          f"{'байт в байт' if same_can else 'РАСХОДИТСЯ'}; registry.py check — код {chk_reg.returncode}")
    bad |= not (same_reg and same_can) or chk_reg.returncode != 0

    # 7. тесты
    tests = sorted(glob.glob(str(SK / "scripts" / "*" / "tests" / "test_*.py")))
    tres = []
    for t in tests:
        r = run([str(VENV_PY), t], cwd=SK)
        last = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
        tres.append((Path(t).relative_to(SK), r.returncode, last[-1][:140] if last else ""))
    if a.blender:
        for t in ("test_bpyx.py", "test_agent_helpers.py"):
            r = run([str(VENV_PY), "scripts/blender/blender_run.py", f"scripts/blender/{t}"], cwd=SK)
            last = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
            tres.append((f"scripts/blender/{t} (blender -b)", r.returncode, last[-1][:140] if last else ""))
    print(f"7. тесты: {len(tres)}; с кодом ≠ 0 — {sum(1 for _, c, _ in tres if c)}")
    for name, c, last in tres:
        print(f"   {'ok' if c == 0 else '!!'} {name} (код {c}): {last}")
    bad |= any(c for _, c, _ in tres)

    print("ИТОГ:", "чисто" if not bad else "есть находки")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
