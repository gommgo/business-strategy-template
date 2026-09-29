"""Вывод plan_to_assets.py check --json на фикстурах проекта — для сверки до и после правки (аргумент — файл вывода)."""
import subprocess, sys
S = "/home/mm/git/stit-core/business-strategy-template/.claude/skills/design-deep-dive/scripts"
sys.path.insert(0, S + "/lib"); sys.path.insert(0, S + "/tests")
import fixture_project
out = []
for name in ("asset-plan", "input-landing", "input-site"):
    with fixture_project.built(name) as fx:
        r = subprocess.run([sys.executable, S + "/site/plan_to_assets.py", "check", fx.slug, "--repo", str(fx.root), "--json"],
                           capture_output=True, text=True)
        out.append(f"== {name} rc={r.returncode}\n" + r.stdout.replace(str(fx.root), "<ROOT>") + r.stderr.replace(str(fx.root), "<ROOT>"))
open(sys.argv[1], "w").write("\n".join(out))
print("\n".join(x.splitlines()[0] + f" ({len(x.splitlines()) - 1} строк)" for x in out))
