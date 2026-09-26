#!/usr/bin/env python3
"""qa_pipeline.py (агент J, волна 3) — сводный конвейер проверок: сцена → GLB → страница; JSON с порогами и вердиктом.
Тонкая обёртка над готовыми утилитами (ничего не считает сам):
  scene: scene_check.py (J = C1/10 + C1/16 + D1) и preflight() агента E (08-export-gltf/04 §5) — в одном фоновом Blender;
  glb:   gltf_check.py (валидатор Khronos) → glb_lint() агента E (§6) → gltf_web_inspect.py → [gltf_diff.py] → [gltf_load_bench.py];
  page:  site_probe.py (A) → gate_check() из 99-raw/tools/gate_check.py (F1 09-web-runtime/05 §7.2, модуль — U) + статическая проверка import map (F1, F2).

  python3 qa_pipeline.py scene A.blend [B.blend …] [--passport P.json | --passports MAP.json] [--out r.json]
  python3 qa_pipeline.py glb M.glb [--blend S.blend --diff [--tone neutral] [--engine cycles]] [--bench] [--max-tris N] [--max-kb N] [--out r.json]
  python3 qa_pipeline.py page URL|DIR [--mobile] [--reduced] [--wait 16000] [--out r.json]

MAP.json для пакета: {"<имя файла без .blend>": {паспорт}, …}. Вердикт каждой стадии и общий: fail (есть ERROR) → review
(есть WARN) → pass. Код выхода: 0 pass, 1 review, 2 fail, 3 ошибка запуска. Пороги gltf_diff — E/02; ворота страницы — F1.
"""
import json, os, re, shutil, struct, subprocess, sys, tempfile, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb("blender"))
TOOLS = str(kbpaths.scripts("blender"))
E26 = TOOLS  # перенос: preflight_block, glb_lint_block — scripts/blender
SERVE_BR = TOOLS  # перенос: serve_br — scripts/blender
RANK = {"pass": 0, "review": 1, "fail": 2}

sys.path.insert(0, TOOLS)
from gate_check import gate_check  # агент U, волна 4: общий модуль вместо своей копии (X §12) — .bin в 3D-ассетах, TBT/KTX2 R20

RUNNER = r'''
import bpy, io, json, sys, traceback
from contextlib import redirect_stdout
a = sys.argv[sys.argv.index("--") + 1:]
cfg = json.load(open(a[0]))
sc_code = open(cfg["scene_check"], encoding="utf-8").read()
pf_code = open(cfg["preflight"], encoding="utf-8").read()
res = {}
for f in cfg["files"]:
    r = {}
    try:
        bpy.ops.wm.open_mainfile(filepath=f)
    except Exception as e:
        res[f] = {"open_error": str(e)}
        continue
    P = cfg["passports"].get(f)
    code = sc_code.replace("\nPASSPORT = None\n", "\nPASSPORT = " + repr(P) + "\n", 1) if P else sc_code
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(code, {"bpy": bpy})
        line = [l for l in buf.getvalue().splitlines() if l.startswith("SCENE_CHECK ")][-1]
        r["scene_check"] = json.loads(line[len("SCENE_CHECK "):])
    except Exception:
        r["scene_check_error"] = traceback.format_exc()[-1500:]
    try:
        ns = {"__name__": "preflight"}
        exec(pf_code, ns)
        r["preflight"] = [list(x) for x in ns["preflight"]()]
    except Exception:
        r["preflight_error"] = traceback.format_exc()[-1500:]
    res[f] = r
json.dump(res, open(a[1], "w"), ensure_ascii=False)
print("QA_SCENE_DONE", len(res))
'''


def opt(a, name, default=None):
    return a[a.index(name) + 1] if name in a else default


def worst(*verdicts):
    v = [x for x in verdicts if x in RANK]
    return max(v, key=RANK.get) if v else "pass"


def issue(level, code, msg, stage):
    return {"level": level, "code": code, "msg": msg, "stage": stage}


def verdict_of(issues):
    lv = {i["level"] for i in issues}
    return "fail" if "ERROR" in lv else ("review" if "WARN" in lv else "pass")


# ------------------------------------------------------------------------------------------------ scene
def run_scene(files, passports, timeout=600):
    files = [os.path.abspath(f) for f in files]
    tmp = tempfile.mkdtemp(prefix="qa_scene_")
    cfg = {"files": files, "passports": {}, "scene_check": os.path.join(TOOLS, "scene_check.py"),
           "preflight": os.path.join(E26, "preflight_block.py")}
    for f in files:
        key = os.path.splitext(os.path.basename(f))[0]
        if key in passports:
            cfg["passports"][f] = passports[key]
        elif "*" in passports:
            cfg["passports"][f] = passports["*"]
    cp, outp, runner = (os.path.join(tmp, n) for n in ("cfg.json", "out.json", "runner.py"))
    json.dump(cfg, open(cp, "w"))
    open(runner, "w").write(RUNNER)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "blender_run.py"), runner, "--timeout", str(timeout), "--",
                        cp, outp], capture_output=True, text=True)
    if not os.path.exists(outp):
        return {"verdict": "fail", "error": (r.stdout[-2000:] + r.stderr[-1000:]), "tmp": tmp}
    raw = json.load(open(outp))
    out = {}
    for f, r in raw.items():
        iss = []
        sc = r.get("scene_check") or {}
        for i in sc.get("issues", []):
            iss.append(issue(i["level"], i["code"], f'{i["obj"]}: {i["msg"]} [{i["m"]}]', "scene_check"))
        asset = set((sc.get("metrics") or {}).get("objects", {}).keys())
        for lvl, code, ob, msg in r.get("preflight", []):
            if asset and ob not in asset and ob != "scene" and not ob.startswith("action:"):
                lvl, msg = "INFO", msg + " (вне ассета)"
            iss.append(issue(lvl, "PF_" + code, f"{ob}: {msg}", "preflight"))
        for k in ("open_error", "scene_check_error", "preflight_error"):
            if k in r:
                iss.append(issue("ERROR", k, r[k][-400:], "runner"))
        out[os.path.basename(f)] = {"verdict": verdict_of(iss), "scene_verdict": sc.get("verdict"),
                                    "codes": sorted({i["code"] for i in iss if i["level"] != "INFO"}),
                                    "issues": iss, "metrics": sc.get("metrics", {})}
    return {"verdict": worst(*[v["verdict"] for v in out.values()]), "files": out, "tmp": tmp}


# ------------------------------------------------------------------------------------------------ glb
ASSET_ONLY = r'''
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=a[0])
keep = set()
for c in bpy.data.collections:
    if c.name.startswith("ASSET_"):
        keep |= {o.name for o in c.all_objects}
n = 0
if keep:
    for o in list(bpy.data.objects):
        if o.type in ("MESH", "CURVE", "FONT", "SURFACE", "META") and o.name not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
            n += 1
bpy.ops.wm.save_as_mainfile(filepath=a[1], copy=True)
print("ASSET_ONLY removed", n, "kept", len(keep))
'''


def asset_only_blend(blend, tmp):
    """Копия .blend без подложки (циклорама, пол, фон вне ASSET_*): gltf_diff рендерит ВСЮ видимую геометрию источника,
    а в GLB — только ассет; без копии IoU 0,002 на кружке C1/12 (J/03)."""
    runner, out = os.path.join(tmp, "asset_only.py"), os.path.join(tmp, "asset_only.blend")
    open(runner, "w").write(ASSET_ONLY)
    subprocess.run([sys.executable, os.path.join(TOOLS, "blender_run.py"), runner, "--", os.path.abspath(blend), out],
                   capture_output=True, text=True, timeout=300)
    return out if os.path.exists(out) else os.path.abspath(blend)


GLB_SANITIZE = re.compile(r"[\[\].:/]")           # агент U, волна 4: NAME_COLLISION (X §12)


def glb_three_name(name):
    """Как PropertyBinding.sanitizeNodeName three r186 (02-blender-workflow/01 §8.2): пробел → '_', удалить [ ] . : /"""
    return GLB_SANITIZE.sub("", re.sub(r"\s", "_", name))


def glb_json(path):
    """JSON-чанк .glb без парсера/трёх.js: 12 байт заголовка + 4 байта длины 1-го чанка + 4 байта типа → JSON."""
    data = open(path, "rb").read()
    n = struct.unpack_from("<I", data, 12)[0]
    return json.loads(data[20:20 + n])


def glb_name_collisions(glb):
    """Узлы .glb, чьи имена после санитизации three (01 §8.2, I/03) совпадают — ERROR, критично для интерактива
    (getObjectByName найдёт не тот узел). Возвращает [(имя1, имя2, санитизированное), …]."""
    seen, dups = {}, []
    for node in glb_json(glb).get("nodes", []):
        name = node.get("name")
        if not name:
            continue
        t = glb_three_name(name)
        if t in seen:
            dups.append((seen[t], name, t))
        else:
            seen[t] = name
    return dups


def run_glb(glb, a):
    glb = os.path.abspath(glb)
    tmp = tempfile.mkdtemp(prefix="qa_glb_")
    iss, rep = [], {"file_kb": round(os.path.getsize(glb) / 1024, 1)}
    # 0. коллизии имён узлов после санитизации three (02-blender-workflow/01 §8.2, I/03) — критично для интерактива
    dups = glb_name_collisions(glb)
    if dups:
        rep["name_collisions"] = dups
        for a_name, b_name, t in dups:
            iss.append(issue("ERROR", "NAME_COLLISION", f"{a_name!r} и {b_name!r} → оба {t!r} (getObjectByName найдёт не тот)", "names"))
    # 1. валидатор Khronos + inspect
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "gltf_check.py"), glb, "--json"], capture_output=True, text=True, timeout=300)
    try:
        chk = json.loads(r.stdout[r.stdout.index("{"):])
        rep["validator"] = chk.get("issues")
        rep["hints"] = chk.get("hints", [])
        if chk["issues"].get("numErrors"):
            iss.append(issue("ERROR", "validator_errors", f'{chk["issues"]["numErrors"]} ошибок валидатора', "gltf_check"))
        if chk["issues"].get("numWarnings"):
            iss.append(issue("WARN", "validator_warnings", f'{chk["issues"]["numWarnings"]} предупреждений', "gltf_check"))
        for h in chk.get("hints", []):
            iss.append(issue("WARN" if "сжат" in h or "> 5 МБ" in h else "INFO", "hint", h, "gltf_check"))
    except (ValueError, KeyError):
        iss.append(issue("ERROR", "gltf_check_failed", (r.stdout + r.stderr)[-400:], "gltf_check"))
    # 2. glb_lint (E, 08/04 §6)
    sys.path.insert(0, E26)
    from glb_lint_block import glb_lint
    lint = glb_lint(glb)
    rep["glb_lint"] = lint
    for w in lint.get("warnings", []):
        iss.append(issue("WARN", "glb_lint", w, "glb_lint"))
    # бюджет из паспорта / таблицы F1 09/05 §1.1 (hero: телефон 50 тыс. треуг. и 820 КБ, десктоп 100 тыс. и 1536 КБ)
    if opt(a, "--max-tris") and (lint.get("triangles") or 0) > int(opt(a, "--max-tris")):
        iss.append(issue("ERROR", "over_budget_tris", f'{lint.get("triangles")} > {opt(a, "--max-tris")} треугольников', "budget"))
    if opt(a, "--max-kb") and rep["file_kb"] > float(opt(a, "--max-kb")):
        iss.append(issue("ERROR", "over_budget_kb", f'{rep["file_kb"]} > {opt(a, "--max-kb")} КБ', "budget"))
    # 3. что создал three r186
    wi = os.path.join(tmp, "three.json")
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "gltf_web_inspect.py"), glb, "--out", wi], capture_output=True,
                       text=True, timeout=300)
    if os.path.exists(wi):
        w = json.load(open(wi))
        errs = [c for c in w.get("console", []) if c.startswith("error") or c.startswith("pageerror")]
        rep["three"] = {k: w.get(k) for k in ("draw_calls", "calls", "triangles", "render", "clips") if k in w}
        rep["three_console"] = w.get("console", [])[:10]
        if errs:
            iss.append(issue("ERROR", "three_console_errors", "; ".join(errs[:3]), "gltf_web_inspect"))
        if any("Multiple instances of Three.js" in c for c in w.get("console", [])):
            iss.append(issue("WARN", "three_multiple_instances", "две копии three", "gltf_web_inspect"))
    else:
        iss.append(issue("ERROR", "web_inspect_failed", (r.stdout + r.stderr)[-400:], "gltf_web_inspect"))
    # 4. Blender против three (по запросу)
    if "--diff" in a and opt(a, "--blend"):
        dd = os.path.join(tmp, "diff")
        src = asset_only_blend(opt(a, "--blend"), tmp)
        cmd = [sys.executable, os.path.join(TOOLS, "gltf_diff.py"), src, dd, "--glb", glb]
        for k in ("--tone", "--engine", "--views", "--hdri"):
            if opt(a, k):
                cmd += [k, opt(a, k)]
        subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        mp = os.path.join(dd, "diff_metrics.json")
        if os.path.exists(mp):
            m = json.load(open(mp))["mean"]
            rep["diff"] = dict(m, sheet=os.path.join(dd, "diff_sheet.png"))
            de, iou = m["de2000_mean"], m["iou"]
            if de > 6 or iou < 0.95:
                iss.append(issue("ERROR", "diff_broken", f"ΔE {de}, IoU {iou} (поломка: ΔE > 6 или IoU < 0,95, E/02)", "gltf_diff"))
            elif de > 3.5 or iou < 0.99:
                iss.append(issue("WARN", "diff_drift", f"ΔE {de}, IoU {iou} (норма ΔE ≤ 3,5 и IoU ≥ 0,99)", "gltf_diff"))
        else:
            iss.append(issue("ERROR", "diff_failed", "gltf_diff не дал diff_metrics.json", "gltf_diff"))
    # 5. цена загрузки (по запросу)
    if "--bench" in a:
        bj = os.path.join(tmp, "bench.json")
        subprocess.run([sys.executable, os.path.join(TOOLS, "gltf_load_bench.py"), glb, "--runs", "3", "--json", bj],
                       capture_output=True, text=True, timeout=600)
        if os.path.exists(bj):
            rep["bench"] = json.load(open(bj))
    return {"verdict": verdict_of(iss), "codes": sorted({i["code"] for i in iss if i["level"] != "INFO"}),
            "issues": iss, "report": rep, "tmp": tmp}


# ------------------------------------------------------------------------------------------------ page
def importmap_check(html_path):
    """Статика (F1 09/01, F2): import map — одна версия three для ядра и addons, без *.min.js ядра с jsDelivr."""
    iss = []
    src = open(html_path, encoding="utf-8").read()
    m = re.search(r'<script type="importmap">(.*?)</script>', src, re.S)
    if not m:
        return iss
    try:
        imports = json.loads(m.group(1)).get("imports", {})
    except ValueError:
        return [issue("ERROR", "importmap_invalid", "import map не JSON", "static")]
    vers = {re.search(r"three@([\d.]+)", u).group(1) for u in imports.values() if re.search(r"three@([\d.]+)", u)}
    if len(vers) > 1:
        iss.append(issue("ERROR", "importmap_versions", f"разные версии three: {sorted(vers)}", "static"))
    core = imports.get("three", "")
    remap = any(k.endswith("three.core.js") and v.endswith("three.core.min.js") for k, v in imports.items())
    if core.endswith(".min.js") and "jsdelivr" in core and not remap:
        iss.append(issue("WARN", "importmap_min_core", "three.module.min.js с jsDelivr без переназначения three.core.js → "
                         "three.core.min.js тянет неминифицированное ядро 204 КБ br (F1 09/01 §1.2)", "static"))
    return iss


def run_page(target, a):
    tmp = tempfile.mkdtemp(prefix="qa_page_")
    iss, httpd, url = [], None, target
    if os.path.isdir(target) or target.endswith(".html"):
        src_root = target if os.path.isdir(target) else os.path.dirname(os.path.abspath(target))
        page = "index.html" if os.path.isdir(target) else os.path.basename(target)
        if os.path.exists(os.path.join(src_root, page)):
            iss += importmap_check(os.path.join(src_root, page))
        # агент U, волна 4 (по замечанию S1): раздаём из временной копии — serve_br.precompress() иначе пишет
        # file.br рядом с демо прямо в базе (09-web-runtime/examples/…), качество проверки от этого не зависит
        root = os.path.join(tmp, "site")
        shutil.copytree(os.path.abspath(src_root), root)
        sys.path.insert(0, SERVE_BR)
        from serve_br import start
        httpd = start(root, int(opt(a, "--port", "0")))     # 0 — свободный порт
        url = f"http://127.0.0.1:{httpd.server_address[1]}/{page}"
    mobile, reduced = "--mobile" in a, "--reduced" in a
    cmd = [sys.executable, os.path.join(TOOLS, "site_probe.py"), url, tmp, "--quick"]
    if mobile:
        cmd += ["--mobile", "--throttle", "--wait", opt(a, "--wait", "16000")]
    elif opt(a, "--wait"):
        cmd += ["--wait", opt(a, "--wait")]
    if reduced:
        cmd += ["--reduced-motion"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    finally:
        if httpd:
            httpd.shutdown()
            httpd.server_close()
    suffix = ("_mobile" if mobile else "") + ("_thr" if mobile else "") + ("_rm" if reduced else "") + ("_quick" if not reduced else "")
    pp = os.path.join(tmp, f"probe{suffix}.json")
    if not os.path.exists(pp):
        iss.append(issue("ERROR", "probe_failed", (r.stdout + r.stderr)[-500:], "site_probe"))
        return {"verdict": "fail", "issues": iss, "url": url, "tmp": tmp}
    rows = gate_check(pp, "mobile" if mobile else "desktop", reduced)
    for name, val, lim, ok in rows:
        if not ok:
            iss.append(issue("ERROR", "gate:" + name, f"{val} при пороге {lim}", "gate_check"))
    txt = open(pp, encoding="utf-8").read()
    if "Multiple instances of Three.js" in txt:
        iss.append(issue("WARN", "three_multiple_instances", "в консоли «Multiple instances of Three.js»", "site_probe"))
    st = json.load(open(pp))
    timing = st.get("page_timing") or st.get("timing") or {}
    return {"verdict": verdict_of(iss), "url": url, "mode": ("mobile" if mobile else "desktop") + ("+reduce" if reduced else ""),
            "gates": [{"check": n, "value": v, "limit": l, "ok": o} for n, v, l, o in rows],
            "codes": sorted({i["code"] for i in iss}), "issues": iss, "probe": pp, "timing": timing, "tmp": tmp}


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help") or a[0] not in ("scene", "glb", "page"):
        print(__doc__); sys.exit(3)
    t0 = time.time()
    mode = a[0]
    if mode == "scene":
        files = [x for x in a[1:] if x.endswith(".blend")]
        passports = {}
        if opt(a, "--passports"):
            passports = json.load(open(opt(a, "--passports")))
        elif opt(a, "--passport"):
            passports = {"*": json.load(open(opt(a, "--passport")))}
        res = run_scene(files, passports)
    elif mode == "glb":
        res = run_glb(a[1], a)
    else:
        res = run_page(a[1], a)
    res["sec"] = round(time.time() - t0, 1)
    if "--keep" not in a:                      # временные папки (кадры diff, отчёты зонда) — удалить; --keep оставляет
        d = res.get("tmp", "")
        if d and os.path.isdir(d) and os.path.basename(d).startswith("qa_"):
            shutil.rmtree(d, ignore_errors=True)
        if isinstance(res.get("probe"), str) and "--out" in a:
            res["probe_note"] = "папка зонда удалена; --keep, чтобы оставить"
    txt = json.dumps(res, ensure_ascii=False, indent=1)
    if opt(a, "--out"):
        open(opt(a, "--out"), "w").write(txt)
    short = {k: res[k] for k in ("verdict", "codes", "sec") if k in res}
    if mode == "scene":
        short["files"] = {k: [v["verdict"], v["codes"]] for k, v in res.get("files", {}).items()}
    print(json.dumps(short, ensure_ascii=False))
    sys.exit(RANK.get(res.get("verdict"), 3))


if __name__ == "__main__":
    main()
