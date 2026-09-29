#!/usr/bin/env python3
"""Приёмка зоны Ф8 (оркестратор, phase-8/PLAN.md §5): механические пункты одним прогоном.

  python3 research/design-build/phase-8/tools/accept.py C1 [C2 …] [--smoke scripts/lib,scripts/tests] [--base REF]

Что делает для изменённых файлов (git: изменённые и новые относительно --base, по умолчанию HEAD, плюс неотслеживаемые):
  1. файлы зоны — сверка с масками зоны (ZONE_GLOBS ниже); чужие пути — отдельным списком;
  2. .md — refcheck.py --strict журнала (битые ссылки, следы журнала);
  3. .json / .yaml / .yml — разбор; *.schema.json — метасхема Draft 2020-12 (jsonschema из venv $DDD_HOME);
  4. .py — компиляция; поиск следов: прежний исполнитель макета, модели других вендоров, Р- и Ф-номера, даты;
  5. --smoke — smoke.py --only по каждой папке списка.
Итог — таблица в stdout; код выхода 1, если есть чужие пути, ошибки разбора или FAIL смоука.
Журнальный инструмент: стандартная библиотека и pyyaml (системный python3).
"""
import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SK = ".claude/skills/design-deep-dive"
DDD_HOME = Path(os.environ.get("DDD_HOME", Path.home() / ".cache" / "design-deep-dive"))
VENV_PY = DDD_HOME / "venv" / "bin" / "python"

# Маски файлов зон (PLAN.md §2); журнал зоны (отчёт) — всегда разрешён.
ZONE_GLOBS = {
    "C1": [f"{SK}/scripts/lib/kbpaths.py", f"{SK}/scripts/lib/docpaths.py", f"{SK}/scripts/install.sh",
           f"{SK}/scripts/requirements.txt", f"{SK}/scripts/package.json", f"{SK}/scripts/tests/smoke.py",
           f"{SK}/scripts/tests/smoke/*", f"{SK}/scripts/tests/smoke-list.tsv", f"{SK}/scripts/tests/fixture_project.py",
           f"{SK}/scripts/tests/fixtures/*", f"{SK}/.gitignore"],
    "C2": [f"{SK}/scripts/ui/*", f"{SK}/scripts/ux/*", f"{SK}/kb/ux/06-feedback-states-motion/*",
           f"{SK}/kb/ux/12-evaluation-checklists/master-checklist.yaml", f"{SK}/kb/ui/11-styles-trends/04-anti-slop-ui.md",
           f"{SK}/kb/ui/14-recipes/examples/03-dashboard.html", f"{SK}/kb/ui/14-recipes/examples/app.css",
           f"{SK}/kb/common/components.yaml"],
    "C3": [f"{SK}/scripts/project/*", f"{SK}/scripts/tests/fixtures/*", f"{SK}/scripts/tests/smoke/project-screens.tsv"],
    "C4": [f"{SK}/scripts/creative/spec_check.py", f"{SK}/scripts/creative/ad_check.py",
           f"{SK}/scripts/creative/validate_stack.py", f"{SK}/scripts/creative/registry_check.py",
           f"{SK}/scripts/creative/marketing_audit.py", f"{SK}/scripts/creative/README.md",
           f"{SK}/kb/creative/01-creative-direction/ambition-levels.yaml", f"{SK}/kb/creative/01-creative-direction/examples/*",
           f"{SK}/kb/creative/09-ai-execution-evaluation/art-direction.v1.schema.json",
           f"{SK}/kb/creative/09-ai-execution-evaluation/treatment.schema.json",
           f"{SK}/kb/creative/09-ai-execution-evaluation/motion-spec.schema.json",
           f"{SK}/kb/creative/09-ai-execution-evaluation/block-treatments.yaml",
           f"{SK}/kb/creative/09-ai-execution-evaluation/effectiveness.rubric.json",
           f"{SK}/kb/creative/09-ai-execution-evaluation/examples/*", f"{SK}/kb/creative/06-effects-catalog/effects.yaml",
           f"{SK}/kb/creative/07-stack-implementation/stack.yaml", f"{SK}/kb/creative/04-visual-language/marketing-tokens.json",
           f"{SK}/scripts/tests/smoke/creative.tsv"],
    "C5": [f"{SK}/scripts/project/ds_coverage.py", f"{SK}/scripts/project/ds_build.py", f"{SK}/scripts/project/ds_sync.py",
           f"{SK}/kb/common/*.schema.json", f"{SK}/kb/common/*.schema.yaml", f"{SK}/kb/common/README.md",
           f"{SK}/kb/common/components.yaml", f"{SK}/scripts/tests/fixtures/*", f"{SK}/scripts/tests/smoke/project-ds.tsv"],
    "C6": [f"{SK}/scripts/project/demo_data.py", f"{SK}/scripts/project/contract.py", f"{SK}/scripts/tests/fixtures/*",
           f"{SK}/scripts/tests/smoke/project-demo.tsv"],
    "C7": [f"{SK}/scripts/site/site_validate.py", f"{SK}/scripts/site/vocab_lint.py", f"{SK}/scripts/site/build_profile.py",
           f"{SK}/scripts/site/README.md", f"{SK}/kb/site/10-playbooks-contracts/schemas/*",
           f"{SK}/kb/site/02-site-types/vocabulary.yaml", f"{SK}/kb/site/02-site-types/crosswalk.tsv",
           f"{SK}/kb/site/08-legal-trust-a11y/legal-requirements.yaml",
           f"{SK}/kb/site/09-ai-generation-evaluation/ux-marketing-profile.tsv",
           f"{SK}/kb/site/10-playbooks-contracts/examples/*", f"{SK}/scripts/tests/smoke/site.tsv"],
    "C8": [f"{SK}/scripts/text/*", f"{SK}/kb/text/10-templates-recipes/*", f"{SK}/kb/text/02-strategy-messaging/*",
           f"{SK}/kb/text/05-voice-editorial/*", f"{SK}/kb/text/08-russian-legal-typography/claims-rules.yaml",
           f"{SK}/kb/text/*/examples/*", f"{SK}/kb/site/10-playbooks-contracts/examples/*/facts.yaml",
           f"{SK}/scripts/tests/smoke/text.tsv"],
    "C9": [f"{SK}/scripts/site/plan_to_assets.py", f"{SK}/scripts/ai-media/asset_inventory.py",
           f"{SK}/scripts/creative/refs_client.py", f"{SK}/kb/ai-media/05-prompting/*", f"{SK}/kb/ai-media/01-*/*",
           f"{SK}/kb/site/10-playbooks-contracts/examples/*/asset-plan.home.yaml", f"{SK}/scripts/site/README.md",
           f"{SK}/scripts/ai-media/README.md", f"{SK}/scripts/creative/README.md", f"{SK}/scripts/tests/smoke/site.tsv",
           f"{SK}/scripts/tests/smoke/ai-media.tsv", f"{SK}/scripts/tests/smoke/creative.tsv"],
    "C10": [f"{SK}/scripts/claude-design/*", f"{SK}/scripts/tests/smoke/claude-design.tsv"],
    "C11": [f"{SK}/scripts/project/canvas_input.py", "docs/projects/_template/design/_template/REVIEW.md",
            f"{SK}/scripts/tests/fixtures/*", f"{SK}/scripts/tests/smoke/project-canvas.tsv"],
    "C12": [f"{SK}/scripts/ai-media/asset_audit.py", f"{SK}/scripts/ai-media/tests/test_asset_audit.py",
            f"{SK}/scripts/ai-media/stand_run.py", f"{SK}/scripts/ai-media/mp_client.py", f"{SK}/scripts/ai-media/vlm_to_dna.py",
            f"{SK}/scripts/ai-media/README.md", f"{SK}/kb/ai-media/11-evaluation-qa/thresholds.yaml",
            f"{SK}/kb/ai-media/11-evaluation-qa/rubrics/*", f"{SK}/kb/ai-media/06-art-direction-consistency/*",
            f"{SK}/kb/common/judge.md", f"{SK}/scripts/tests/smoke/ai-media.tsv"],
    "C13": [f"{SK}/scripts/project/ready.py", f"{SK}/scripts/project/design_audit.py", f"{SK}/scripts/tests/fixtures/*",
            f"{SK}/scripts/tests/smoke/project-package.tsv"],
    "C14": [f"{SK}/scripts/site/page_gates.py", f"{SK}/scripts/site/page_anatomy.py", f"{SK}/scripts/ai-media/page_accept.py",
            f"{SK}/scripts/creative/motion_check.py", f"{SK}/scripts/creative/scroll_record.py",
            f"{SK}/scripts/blender/gate_check.py", f"{SK}/scripts/blender/site_probe.py", f"{SK}/scripts/blender/web_view.py",
            f"{SK}/scripts/site/geo_probe.py", f"{SK}/scripts/site/ia_probe.py", f"{SK}/scripts/site/run_axe_targets.py",
            f"{SK}/kb/site/07-seo-geo-performance-analytics/budgets.yaml",
            f"{SK}/kb/site/07-seo-geo-performance-analytics/page-gates.yaml",
            f"{SK}/kb/creative/09-ai-execution-evaluation/effect-gates.yaml", f"{SK}/kb/blender/09-web-runtime/*.yaml",
            f"{SK}/kb/blender/09-web-runtime/README.md", f"{SK}/kb/creative/01-creative-direction/ambition-levels.yaml",
            f"{SK}/scripts/site/plan_to_assets.py",
            f"{SK}/scripts/site/README.md", f"{SK}/scripts/ai-media/README.md", f"{SK}/scripts/creative/README.md",
            f"{SK}/scripts/blender/README.md", f"{SK}/scripts/tests/smoke/site.tsv", f"{SK}/scripts/tests/smoke/ai-media.tsv",
            f"{SK}/scripts/tests/smoke/creative.tsv", f"{SK}/scripts/tests/smoke/blender.tsv"],
    "C15": [f"{SK}/scripts/text/copy_lint.py", f"{SK}/scripts/text/ux_dict_to_yaml.py", f"{SK}/scripts/text/copy_extract.py",
            f"{SK}/scripts/text/README.md", f"{SK}/kb/text/06-anti-slop/*", f"{SK}/kb/text/04-copy-by-block/copy-slots.yaml",
            f"{SK}/kb/text/07-seo-geo-copy/*", f"{SK}/kb/text/08-russian-legal-typography/typography-rules.yaml",
            f"{SK}/kb/text/09-ai-generation-evaluation/*", f"{SK}/kb/common/tells.yaml", f"{SK}/scripts/tests/smoke/text.tsv"],
    "C16": [f"{SK}/scripts/maint/*", f"{SK}/kb/common/README.md", f"{SK}/scripts/tests/smoke/maint.tsv"],
}
ALWAYS = ["research/design-build/phase-8/reports/*"]
IGNORE = ["research/design-build/phase-4/inputs/in-drafts/*", "research/design-build/phase-8/briefs/*",
          "research/design-build/phase-8/tools/*", "research/design-build/phase-8/check/*",
          "research/design-build/phase-8/CHAIN.md", "research/design-build/STATE.md", "research/design-build/DECISIONS.md",
          "*/__pycache__/*", "*.pyc"]

TRACE_PATTERNS = [
    ("прежний исполнитель", re.compile(r"kimi|\bK3\b(?!-)", re.I)),
    ("модель другого вендора", re.compile(r"gemini|qwen|\bgpt-|claude-3|llama|mistral", re.I)),
    ("Р-номер", re.compile(r"(?<![\w-])Р\d{1,3}(?![\w-])")),
    ("Ф-номер", re.compile(r"(?<![\w-])Ф\d{1,2}(?![\w-])")),
    ("дата", re.compile(r"\b20\d\d-\d\d-\d\d\b|\b\d\d\.\d\d\.20\d\d\b")),
]


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True).stdout


def changed(base):
    files = set()
    for line in git("diff", "--name-only", base).splitlines():
        files.add(line.strip())
    for line in git("ls-files", "--others", "--exclude-standard").splitlines():
        files.add(line.strip())
    return sorted(f for f in files if f and not any(fnmatch.fnmatch(f, g) for g in IGNORE))


def match(path, globs):
    return any(fnmatch.fnmatch(path, g) or fnmatch.fnmatch(path, g.rstrip("*") + "**") or
               (g.endswith("/*") and path.startswith(g[:-1])) for g in globs)


def check_md(paths):
    if not paths:
        return "md: нет"
    r = subprocess.run([sys.executable, str(ROOT / "research/design-build/tools/refcheck.py"), "--strict", *paths],
                       capture_output=True, text=True, cwd=ROOT)
    tail = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()][-40:]
    return "refcheck --strict (код %d):\n  " % r.returncode + "\n  ".join(tail)


def check_data(paths):
    import yaml
    out, bad = [], 0
    schemas = []
    for p in paths:
        fp = ROOT / p
        if not fp.exists():
            continue
        try:
            if p.endswith(".json"):
                json.loads(fp.read_text(encoding="utf-8"))
                if p.endswith(".schema.json"):
                    schemas.append(p)
            elif p.endswith((".yaml", ".yml")):
                list(yaml.safe_load_all(fp.read_text(encoding="utf-8")))
        except Exception as e:  # noqa: BLE001
            bad += 1
            out.append(f"  РАЗБОР: {p}: {str(e)[:200]}")
    if schemas and VENV_PY.exists():
        code = ("import json,sys,jsonschema\nbad=0\nfor f in sys.argv[1:]:\n  try: jsonschema.Draft202012Validator.check_schema("
                "json.load(open(f,encoding='utf-8')))\n  except Exception as e: bad+=1; print('  МЕТАСХЕМА:',f,str(e)[:200])\n"
                "sys.exit(1 if bad else 0)")
        r = subprocess.run([str(VENV_PY), "-c", code, *[str(ROOT / s) for s in schemas]], capture_output=True, text=True)
        if r.stdout.strip():
            out.append(r.stdout.rstrip())
        bad += r.returncode
    out.insert(0, f"данные: {len(paths)} файлов, схем {len(schemas)}, ошибок {bad}")
    return "\n".join(out), bad


def check_py(paths):
    out, bad = [], 0
    for p in paths:
        fp = ROOT / p
        if not fp.exists():
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        try:
            compile(text, p, "exec")
        except SyntaxError as e:
            bad += 1
            out.append(f"  СИНТАКСИС: {p}: {e}")
        for n, line in enumerate(text.splitlines(), 1):
            for name, rx in TRACE_PATTERNS:
                if rx.search(line):
                    out.append(f"  след «{name}»: {p}:{n}: {line.strip()[:140]}")
    out.insert(0, f"код: {len(paths)} файлов .py, синтаксис — ошибок {bad}")
    return "\n".join(out), bad


def smoke(folders):
    res = []
    fail = 0
    for f in folders:
        r = subprocess.run([sys.executable, "scripts/tests/smoke.py", "--only", f], capture_output=True, text=True,
                           cwd=ROOT / SK)
        last = [l for l in r.stdout.splitlines() if l.startswith("итого")]
        fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
        fail += len(fails) + (1 if r.returncode not in (0, 1) else 0)
        res.append(f"смоук {f}: {last[-1] if last else r.stdout[-300:]}" + "".join("\n  " + x for x in fails))
    return "\n".join(res), fail


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zones", nargs="+")
    ap.add_argument("--base", default="HEAD")
    ap.add_argument("--smoke", default="")
    ap.add_argument("--no-trace", action="store_true", help="не искать следы в коде")
    a = ap.parse_args()
    globs = ALWAYS[:]
    for z in a.zones:
        if z not in ZONE_GLOBS:
            sys.exit(f"нет масок зоны {z}")
        globs += ZONE_GLOBS[z]
    files = changed(a.base)
    own = [f for f in files if match(f, globs)]
    foreign = [f for f in files if f not in own]
    rc = 0
    print(f"== изменено файлов: {len(files)}; зоны {' '.join(a.zones)}: {len(own)}; вне масок: {len(foreign)}")
    for f in foreign:
        print("  ВНЕ МАСОК:", f)
    rc |= bool(foreign)
    stat = git("diff", "--numstat", a.base, "--", *own) if own else ""
    for line in stat.splitlines():
        print("  ", line)
    for f in own:
        if not (ROOT / f).exists():
            print("  УДАЛЁН:", f)
        elif not git("ls-files", "--", f).strip():
            n = sum(1 for _ in (ROOT / f).open(encoding="utf-8", errors="replace")) if (ROOT / f).is_file() else 0
            print(f"   новый\t{n} строк\t{f}")
    md = [f for f in own if f.endswith(".md") and (ROOT / f).exists() and not f.startswith("research/")]
    print("\n== " + check_md(md))
    data = [f for f in own if f.endswith((".json", ".yaml", ".yml"))]
    txt, bad = check_data(data)
    print("\n== " + txt)
    rc |= bool(bad)
    py = [f for f in own if f.endswith(".py")]
    if not a.no_trace:
        txt, bad = check_py(py)
        print("\n== " + txt)
        rc |= bool(bad)
    if a.smoke:
        txt, bad = smoke([s for s in a.smoke.split(",") if s])
        print("\n== " + txt)
        rc |= bool(bad)
    sys.exit(1 if rc else 0)


if __name__ == "__main__":
    main()
