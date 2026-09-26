#!/usr/bin/env python3
"""Код скилла на временной раскладке (фаза 3, агент B): генерация overlay по tools-map, сборка, смоук.

  python3 code_stage.py --gen                 # overlay: scripts/tests/smoke-list.tsv и scripts/README.md из tools-map.tsv
  python3 code_stage.py --build               # .staging-code/: scripts/ по tools-map с правками + overlay + kb/<база> → симлинки на базы
  python3 code_stage.py --build --faithful    # .staging-code-faithful/: kb и data — по файлам expected-content.tsv (только переносимое)
  python3 code_stage.py --smoke [--faithful]  # смоук внутри bwrap: источник только для чтения, без сети, без браузеров и Blender
  python3 code_stage.py --report             # code-smoke.tsv из результатов обоих режимов
  python3 code_stage.py --smoke --root .staging --tag staging   # смоук чужой раскладки (migrate.py: .staging агента C)

Источник (базы, _skill-build вне этой папки) только читается. Пишет: overlay/…/scripts/{tests/smoke-list.tsv,README.md},
.staging-code*/ (сырые результаты — .staging-code-results/), code-smoke.tsv. Смоук — Python из ~/.cache/design-deep-dive/venv (через DDD_HOME временной раскладки).
Сборка раскладки — та же, что должна сделать migrate.py для кода (SPEC-code.md «Передача агенту C»): строки tools-map с
verdict take/adapt копируются в dest; у adapt — результат apply_patches; dup-of — не копируются (псевдонимы).
"""
import argparse
import ast
import csv
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
APP = HERE.parents[2]
sys.path.insert(0, str(HERE))
import apply_patches as AP  # noqa: E402

TOOLS_MAP = HERE / "tools-map.tsv"
EXPECTED = HERE / "expected-content.tsv"
OVERLAY = HERE / "overlay"
SKILL = ".claude/skills/design-deep-dive"
OV_SCRIPTS = OVERLAY / SKILL / "scripts"
STAGE = {False: HERE / ".staging-code", True: HERE / ".staging-code-faithful"}
RESULTS = HERE / ".staging-code-results"      # сырые результаты смоука (временная папка; в журнал не идёт)
VENV = Path.home() / ".cache" / "design-deep-dive" / "venv"
BASES = {"ux": "ux-research", "ui": "ui-research", "site": "site-research", "text": "text-research",
         "creative": "creative-research", "ai-media": "ai-media-research", "blender": "blender-research",
         "claude-design": "claude-design-research"}
KIND_ORDER = ["utility", "step", "module", "kit", "maint", "test", "ref", "data"]
DOMAIN_TITLE = {"ux": "ux — логика продукта", "ui": "ui — визуальный язык", "site": "site — сайты и лендинги",
                "text": "text — тексты", "creative": "creative — подача и движение", "ai-media": "ai-media — картинки и видео",
                "blender": "blender — 3D", "claude-design": "claude-design — макеты", "maint": "maint — обслуживание базы",
                "lib": "lib — общие модули"}


def read_map():
    return list(csv.DictReader(open(TOOLS_MAP, encoding="utf-8"), delimiter="\t"))


def taken(rows):
    return [r for r in rows if r["verdict"] in ("take", "adapt")]


# ------------------------------------------------------------------ генерация overlay

def docline(src):
    """Первая фраза докстринга (или первого комментария) — назначение."""
    p = APP / src
    if p.suffix != ".py":
        return ""
    text = p.read_text(encoding="utf-8", errors="replace")
    try:
        d = ast.get_docstring(ast.parse(text)) or ""
    except SyntaxError:
        d = ""
    if not d:
        for ln in text.splitlines()[:6]:
            if ln.startswith("#") and not ln.startswith("#!"):
                d = ln.lstrip("# ").strip()
                break
    d = d.strip().split("\n\n")[0].replace("\n", " ")
    d = re.sub(r"^[\w./-]+\.py\s*(?:[\d.]+\s*)?(?:\([^)]*\))?\s*[—-]\s*", "", d)
    m = re.match(r"(.+?[.!?])(\s|$)", d)
    d = (m.group(1) if m else d).strip()
    d = re.sub(r"\s*\((?=[^()]*(?:агент|волна|оркестратор|сессия|20\d\d-\d\d-\d\d|\d\d\.\d\d\.20\d\d))[^()]*\)", "", d).strip()
    return (d[:170] + "…") if len(d) > 170 else d


KB_OUT = {  # генераторы и утилиты, которые пишут в kb или рядом с собой (их функция), — для указателя
    "ux/checklist_export.py": "`kb/ux/12-evaluation-checklists/master-checklist.yaml`",
    "site/checklist_export.py": "`kb/site/09-ai-generation-evaluation/site-checklist.yaml`",
    "site/build_profile.py": "`kb/site/09-ai-generation-evaluation/ux-marketing-profile.tsv`, `kb/site/99-raw/experiments/K/02-ux-profile/ac-profile.tsv`",
    "text/ux_dict_to_yaml.py": "`kb/text/06-anti-slop/lexicon/ux-07-06.yaml`",
    "blender/rk.py": "`kb/blender/12-recipes/examples/<рецепт>/` (постер, GLB, numbers.json)",
    "blender/vote/tally.py": "блок итогов в `kb/blender/15-showcase/VERDICT.md`; results.* рядом со страницей",
    "blender/vote/build_pairs.py": "`blender/vote/{img/,pairs.json}` — папка страницы голосования",
    "blender/vote/vote_server.py": "`blender/vote/votes/` (или `--dir`)",
    "ui/build_reference_tokens.py": "`--out`: tokens.json, tokens.css, theme.css, report.txt",
}


def outputs(dest):
    rel = dest.split("/scripts/", 1)[-1]
    if rel in KB_OUT:
        return KB_OUT[rel]
    p = AP.patch_file_for(dest)
    if not p.exists():
        return ""
    txt = p.read_text(encoding="utf-8")
    outs = []
    for fn, dom, rest in re.findall(r'kbpaths\.(out|cache)\(["\']([\w-]+)["\']((?:,\s*["\'][^"\']+["\'])*)\)', txt):
        parts = [dom] + re.findall(r'["\']([^"\']+)["\']', rest)
        s = f"$DDD_HOME/{fn}/" + "/".join(parts)
        if s not in outs:
            outs.append(s)
    return ", ".join(f"`{o}`" for o in outs[:3])


def gen():
    rows = read_map()
    tk = taken(rows)
    # smoke-list.tsv
    xfail = parse_xfail()
    lines = ["path\tkind\tsmoke\txfail"]
    for r in sorted(tk, key=lambda r: r["dest"]):
        if not r["dest"].startswith((SKILL + "/scripts/", SKILL + "/kb/")) or r["smoke"] in ("", "-"):
            continue
        rel = r["dest"][len(SKILL) + 1:]
        lines.append(f"{rel}\t{r['kind']}\t{r['smoke']}\t{xfail.get(rel, '')}")
    lines += ["scripts/lib/kbpaths.py\tmodule\thelp; run: --selftest\t", "scripts/tests/smoke.py\ttest\thelp\t",
              "scripts/install.sh\tmaint\tcompile; run: --dry-run\t", "scripts/package.json\tdata\tdata\t",
              "scripts/requirements.txt\tdata\tdata\t", "scripts/README.md\tdata\tdata\t"]
    (OV_SCRIPTS / "tests").mkdir(parents=True, exist_ok=True)
    (OV_SCRIPTS / "tests" / "smoke-list.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # README.md
    by_dom = defaultdict(list)
    for r in tk:
        if not r["dest"].startswith(SKILL + "/scripts/"):
            continue
        rel = r["dest"][len(SKILL) + len("/scripts/"):]
        dom = rel.split("/")[0]
        by_dom[dom].append((rel, r))
    out = ["# Утилиты скилла design-deep-dive", "",
           "Указатель собран при переносе из списка утилит сборки (`tools-map.tsv`).",
           "Пути — от `scripts/`. Запуск — Python окружения: `~/.cache/design-deep-dive/venv/bin/python scripts/<домен>/<утилита>.py --help`;",
           "пути к базе, выходы, кэши, блокировки, бинарники — `lib/kbpaths.py` (`python3 lib/kbpaths.py` показывает, что где).",
           "Окружение ставит `install.sh` (`--dry-run` — только показать план); проверка — `tests/smoke.py`.", "",
           "Колонки: назначение — первая фраза описания утилиты; вход — как её запускать (подробно — `--help` и README домена);",
           "выход — куда пишет по умолчанию (`$DDD_HOME` = `~/.cache/design-deep-dive`); зависимости — Python, npm, бинарники.", ""]
    doms = [d for d in ("lib", "ux", "ui", "site", "text", "creative", "ai-media", "blender", "claude-design", "maint") if d in by_dom]
    for dom in doms:
        out += [f"## {DOMAIN_TITLE.get(dom, dom)}", ""]
        if (APP / BASES.get(dom, "-") / "99-raw/tools/README.md").exists():
            out += [f"Подробный README домена — `{dom}/README.md` (из базы).", ""]
        out += ["| утилита | вид | назначение | вход | выход | зависимости |", "|---|---|---|---|---|---|"]
        items = sorted(by_dom[dom], key=lambda x: (KIND_ORDER.index(x[1]["kind"]) if x[1]["kind"] in KIND_ORDER else 99, x[0]))
        for rel, r in items:
            if r["kind"] == "data":
                continue
            purpose = docline(r["source"]).replace("|", "/")
            smoke = r["smoke"]
            if "import-only" in smoke or "compile" in smoke:
                entry = "модуль / без `--help`" if r["kind"] in ("module", "test") else "см. докстринг"
            else:
                entry = "`--help`"
            deps = "; ".join(x for x in (r["deps_py"].replace(",", ", "), r["deps_node"], r["deps_bin"]) if x)
            note = f" {r['notes']}" if r["kind"] in ("step",) and r["notes"] else ""
            out.append(f"| `{rel}` | {r['kind']} | {purpose}{note.replace('|', '/')} | {entry} | {outputs(r['dest']) or 'stdout / `--out`'} | "
                       f"{deps.replace('|', '/') or 'stdlib'} |")
        data = [rel for rel, r in items if r["kind"] == "data"]
        if data:
            out += ["", "Данные кода: " + ", ".join(f"`{d}`" for d in data) + "."]
        out.append("")
    out += ["## Данные, которые читает только код", "",
            "Кроме файлов выше (из tools-map): `ai-media/data/lucide-ref/` (эталонные иконки Lucide, ISC — для `check_icons`),",
            "`ai-media/data/genapi_prices_2026-09-23.json` (прайс Gen-API — `mp_client`), `blender/data/studio_small_09_1k.hdr`",
            "(HDRI по умолчанию `gltf_diff`, CC0) — их кладут правила содержимого.", ""]
    (OV_SCRIPTS / "README.md").write_text("\n".join(out), encoding="utf-8")
    print("smoke-list:", len(lines) - 1, "строк; README:", sum(len(v) for v in by_dom.values()), "файлов")


def parse_xfail():
    """Известные ограничения смоука без окружения — из xfail.tsv рядом (path → причина)."""
    p = HERE / "code-xfail.tsv"
    if not p.exists():
        return {}
    return {r["path"]: r["reason"] for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t")}


# ------------------------------------------------------------------ сборка временной раскладки

def build(faithful):
    root = STAGE[faithful]
    if root.exists():
        shutil.rmtree(root)
    skill = root / SKILL
    rows = read_map()
    n = Counter()
    for r in taken(rows):
        dest = r["dest"]
        if dest.startswith(SKILL + "/kb/") and not faithful:
            n["ref-skip"] += 1          # в режиме «базы симлинками» kb — источник, правленый эталонный код не кладём
            continue
        out = root / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        if r["verdict"] == "adapt":
            out.write_bytes(AP.apply_patch(AP.load_patch(AP.patch_file_for(dest))))
            n["adapt"] += 1
        else:
            shutil.copyfile(APP / r["source"], out)
            n["take"] += 1
        shutil.copymode(APP / r["source"], out)
    for p in (OVERLAY / SKILL / "scripts").rglob("*"):
        if p.is_file():
            t = skill / "scripts" / p.relative_to(OVERLAY / SKILL / "scripts")
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, t)
            n["overlay"] += 1
    exp = list(csv.DictReader(open(EXPECTED, encoding="utf-8"), delimiter="\t"))
    for r in exp:                       # данные кода, размещённые агентом A (scripts/<база>/data/…)
        if r["kind"] == "copy" and r["purpose"] == "code-data":
            t = root / r["dest"]
            t.parent.mkdir(parents=True, exist_ok=True)
            t.symlink_to(APP / r["source"])
            n["code-data"] += 1
    kb = skill / "kb"
    kb.mkdir(parents=True, exist_ok=True)
    if not faithful:
        for b, src in BASES.items():
            (kb / b).symlink_to(APP / src)
            n["kb-link"] += 1
    else:
        rw = defaultdict(list)          # переписывание путей агента A (scan-rewrites.tsv) — как после migrate.py
        for r in csv.DictReader(open(HERE / "scan-rewrites.tsv", encoding="utf-8"), delimiter="\t"):
            rw[r["source"]].append((int(r["line"]), int(r["start"]), int(r["end"]), r["raw"], r["new"]))
        for r in exp:
            if r["kind"] == "copy" and r["dest"].startswith(SKILL + "/kb/"):
                t = root / r["dest"]
                if t.exists():          # эталонный код с правкой уже лежит файлом
                    continue
                t.parent.mkdir(parents=True, exist_ok=True)
                if r["source"] in rw:
                    lines = (APP / r["source"]).read_text(encoding="utf-8").split("\n")
                    for ln, a, b, raw, new in sorted(rw[r["source"]], key=lambda x: (x[0], -x[1])):
                        cur = lines[ln - 1]
                        if cur[a:b] != raw:
                            raise SystemExit(f"scan-rewrites: {r['source']}:{ln} не совпал токен {raw!r}")
                        lines[ln - 1] = cur[:a] + new + cur[b:]
                    t.write_text("\n".join(lines), encoding="utf-8")
                    n["kb-rewritten"] += 1
                else:
                    t.symlink_to(APP / r["source"])
                    n["kb-file"] += 1
    home = root / ".ddd-home"
    home.mkdir()
    (home / "venv").symlink_to(VENV)
    print(f"{root.name}: " + ", ".join(f"{k} {v}" for k, v in n.items()))


# ------------------------------------------------------------------ смоук в песочнице

SOURCE_CACHE = {"polza": "ai-media-research/99-raw/cache/polza", "routerai": "ai-media-research/99-raw/cache/routerai",
                "genapi": "ai-media-research/99-raw/cache/genapi",
                "c2pa-trust-2026-09-23": "ai-media-research/99-raw/cache/c2pa-trust-2026-09-23"}


def smoke(faithful, only="", extra_env=(), tag="", source_cache=False, root=None):
    """Смоук scripts/tests/smoke.py раскладки root (корень шаблона) в песочнице bwrap: источник app-design — только чтение,
    без сети, браузеры Playwright, Brave и Blender спрятаны; DDD_HOME — временный (своя раскладка — внутри неё, чужая —
    в .staging-code-results/, чтобы не менять её дерево); venv — ссылка на общий ~/.cache/design-deep-dive/venv."""
    foreign = bool(root)
    root = Path(root).resolve() if root else STAGE[faithful]
    skill = root / SKILL
    RESULTS.mkdir(exist_ok=True)
    # своя раскладка — окружение внутри неё; чужая (.staging агента C) — снаружи, чтобы не менять её дерево и отпечаток
    home = (RESULTS / f"ddd-home-{tag or 'root'}") if foreign else (root / ".ddd-home")
    if not home.exists():
        home.mkdir(parents=True)
        (home / "venv").symlink_to(VENV)
    if source_cache:                    # проверка с кэшами источника (снимки каталогов, список доверия C2PA) — только чтение
        home = (RESULTS if foreign else root) / ".ddd-home-srccache"
        if home.exists():
            shutil.rmtree(home)         # своя временная папка этой проверки
        (home / "cache" / "ai-media").mkdir(parents=True)
        (home / "venv").symlink_to(VENV)
        for name, rel in SOURCE_CACHE.items():
            if (APP / rel).exists():
                (home / "cache" / "ai-media" / name).symlink_to(APP / rel)
    RESULTS.mkdir(exist_ok=True)
    tsv = RESULTS / (f"code-smoke-{tag or ('faithful' if faithful else 'full')}.raw.tsv")
    hm = Path.home()
    bw = ["bwrap", "--dev-bind", "/", "/", "--ro-bind", str(APP), str(APP), "--bind", str(root), str(root),
          "--bind", str(RESULTS), str(RESULTS), "--unshare-net", "--die-with-parent"]
    masks = [hm / ".cache" / "ms-playwright", Path("/opt/brave.com")]
    for m in masks:
        if m.exists():
            bw += ["--tmpfs", str(m)]
    for f in (hm / ".local" / "bin" / "blender", Path("/usr/bin/brave-browser")):
        if f.exists():                  # симлинк: прячем каталог, куда он ведёт (bwrap не монтирует поверх симлинка)
            d = f.resolve().parent
            if str(d) not in bw:
                bw += ["--tmpfs", str(d)]
    env = dict(os.environ, DDD_HOME=str(home), PLAYWRIGHT_BROWSERS_PATH=str(root / ".no-browsers"),
               DDD_BLENDER=str(root / ".no-blender"), DDD_BRAVE=str(root / ".no-brave"), PYTHONDONTWRITEBYTECODE="1")
    env.pop("XDG_CACHE_HOME", None)
    for kv in extra_env:
        k, v = kv.split("=", 1)
        env[k] = v
    out_tmp = tsv
    cmd = bw + [str(VENV / "bin" / "python"), str(skill / "scripts" / "tests" / "smoke.py"), "--tsv", str(out_tmp)]
    if only:
        cmd += ["--only", only]
    r = subprocess.run(cmd, env=env)
    return r.returncode


def report():
    """code-smoke.tsv: строки tools-map (взятые) × результаты смоука двух раскладок."""
    rows = read_map()
    res = {}
    for mode, name in (("full", "code-smoke-full.raw.tsv"), ("faithful", "code-smoke-faithful.raw.tsv"),
                       ("srccache", "code-smoke-srccache.raw.tsv")):
        p = RESULTS / name
        if not p.exists():
            continue
        for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"):
            res.setdefault((r["path"], mode), []).append(r)
    xf = parse_xfail()
    out = ["path\tsource\tkind\tverdict\tsmoke\tfull\tfaithful\tsrccache\tseconds\tnote"]
    extra = [("scripts/lib/kbpaths.py", "overlay", "module", "overlay"), ("scripts/tests/smoke.py", "overlay", "test", "overlay"),
             ("scripts/install.sh", "overlay", "maint", "overlay"), ("scripts/package.json", "overlay", "data", "overlay"),
             ("scripts/requirements.txt", "overlay", "data", "overlay"), ("scripts/README.md", "overlay", "data", "overlay")]
    items = [(r["dest"][len(SKILL) + 1:], r["source"], r["kind"], r["verdict"], r["smoke"]) for r in taken(rows)]
    items += [(p, s, k, v, "") for p, s, k, v in extra]
    cnt = Counter()
    for path, src, kind, verdict, sm in sorted(items):
        cells, secs, notes = {}, 0.0, []
        for mode in ("full", "faithful", "srccache"):
            rr = res.get((path, mode))
            if not rr:
                cells[mode] = "n/a" if (mode == "full" and path.startswith("kb/")) or not path.startswith(("scripts/", "kb/")) else "-"
                continue
            st = [x["status"] for x in rr]
            cells[mode] = "FAIL" if "FAIL" in st else ("XFAIL" if "XFAIL" in st else ("XPASS" if "XPASS" in st else "PASS"))
            secs = max(secs, sum(float(x["seconds"]) for x in rr))
            for x in rr:
                if x["note"] and x["note"] not in notes:
                    notes.append(f"{mode}: {x['check']}: {x['note']}")
        if not sm:
            sm = {"scripts/lib/kbpaths.py": "help; run: --selftest", "scripts/tests/smoke.py": "help",
                  "scripts/install.sh": "compile; run: --dry-run"}.get(path, "data")
        if not path.startswith("scripts/") and not path.startswith("kb/"):
            continue
        cnt[(cells["full"], cells["faithful"])] += 1
        note = "; ".join(notes)[:400] or xf.get(path, "")
        out.append("\t".join([path, src, kind, verdict, sm, cells["full"], cells["faithful"], cells["srccache"], f"{secs:.1f}",
                               note.replace("\t", " ")]))
    (HERE / "code-smoke.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("code-smoke.tsv:", len(out) - 1, "строк;", dict(cnt))


def main():
    ap = argparse.ArgumentParser(description="Код скилла на временной раскладке (агент B)")
    ap.add_argument("--gen", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--faithful", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--env", action="append", default=[], help="K=V для смоука (проверка с внешним окружением)")
    ap.add_argument("--tag", default="", help="имя результата code-smoke-<tag>.raw.tsv")
    ap.add_argument("--source-cache", action="store_true", help="смоук с кэшами источника ai-media (снимки каталогов, C2PA)")
    ap.add_argument("--root", default="", help="смоук другой раскладки (корень шаблона, например .staging агента C)")
    a = ap.parse_args()
    rc = 0
    if a.gen:
        gen()
    if a.build:
        build(a.faithful)
    if a.smoke:
        rc = smoke(a.faithful, a.only, a.env, a.tag, a.source_cache, a.root or None)
    if a.report:
        report()
    return rc


if __name__ == "__main__":
    sys.exit(main())
