#!/usr/bin/env python3
"""K/01 — сквозной прогон рецептов 12-recipes: блоки ```python рецепта (в напечатанном виде, по порядку) → один скрипт
examples/<slug>/build.py → Blender 5.2.2 без окна (blender_run.py) → для каждого <name>.glb в examples/<slug>/ (кроме *_raw,
*_ar): валидатор Khronos (gltf_check.py --json) и three r186 в Chromium (web_view.py, тонмаппинг Neutral).
Блок пропускается, если в его первой строке есть «[не проверено]» или «[не исполняется]».

    python3 99-raw/experiments/K/01-run-recipes/run_recipes.py 12-recipes/01-hero-product.md [ещё.md …] [--no-web]
Результат: 99-raw/experiments/K/01-run-recipes/result.json (по slug: код выхода, время, блоки, веб-проверки)."""
import glob, json, os, re, subprocess, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb("blender"))
HERE = os.path.dirname(os.path.abspath(__file__))
RES = str(kbpaths.out("blender", "run_recipes") / "result.json")


def blocks(md):
    src = open(md, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"```python\n(.*?)```", src, re.S):
        code = m.group(1)
        first = code.split("\n", 1)[0]
        line = src[:m.start()].count("\n") + 1
        skip = "[не проверено]" in first or "[не исполняется]" in first
        out.append({"line": line, "code": code, "skip": skip, "system": first.startswith("# run: system")})
    return out


def run(cmd, timeout=600):
    t = time.time()
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return r, round(time.time() - t, 1)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    web = "--no-web" not in sys.argv
    res = json.load(open(RES)) if os.path.exists(RES) else {}
    for md in args:
        md = os.path.abspath(md)
        slug = os.path.basename(md)[:-3]
        bl = blocks(md)
        ex = f"{ROOT}/12-recipes/examples/{slug}"
        os.makedirs(ex, exist_ok=True)
        run_bl = [b for b in bl if not b["skip"] and not b["system"]]
        sys_bl = [b for b in bl if not b["skip"] and b["system"]]
        rec = {"md": os.path.relpath(md, ROOT), "blocks_python": len(bl), "blocks_run": len(run_bl),
               "blocks_skipped_lines": [b["line"] for b in bl if b["skip"]]}
        if run_bl:
            script = f"{ex}/build.py"
            with open(script, "w", encoding="utf-8") as f:
                f.write(f"# Сгенерировано K/01 из {rec['md']} — блоки python в напечатанном виде, по порядку.\n")
                for b in run_bl:
                    f.write(f"\n# ---- блок со строки {b['line']}\n{b['code']}")
            r, sec = run(["python3", "99-raw/tools/blender_run.py", script, "--timeout", "600"])
            rec.update(exit=r.returncode, sec=sec, tail=(r.stdout + r.stderr)[-1500:])
            print(f"[{slug}] blender exit={r.returncode} {sec}s")
        if sys_bl and rec.get("exit", 0) == 0:          # блоки «# run: system» — системный Python 3 (Pillow, ffmpeg)
            script = f"{ex}/post.py"
            with open(script, "w", encoding="utf-8") as f:
                f.write(f"# Сгенерировано K/01 из {rec['md']} — блоки «run: system» в напечатанном виде.\n")
                for b in sys_bl:
                    f.write(f"\n# ---- блок со строки {b['line']}\n{b['code']}")
            r, sec = run(["python3", script])
            rec.update(system_exit=r.returncode, system_sec=sec, system_tail=(r.stdout + r.stderr)[-1200:])
            print(f"[{slug}] system exit={r.returncode} {sec}s")
            if r.returncode != 0:
                rec["exit"] = 100 + r.returncode
        if web and rec.get("exit", 0) == 0:
            rec["web"] = {}
            for glb in sorted(glob.glob(f"{ex}/*.glb")):
                name = os.path.basename(glb)[:-4]
                if name.endswith("_raw") or name.endswith("_ar"):
                    continue
                w = {}
                r, sec = run(["python3", "99-raw/tools/gltf_check.py", glb, "--json"], timeout=180)
                try:
                    j = json.loads(r.stdout)
                    v = j.get("validator", j)
                    w["validator"] = {k: v.get(k) for k in ("numErrors", "numWarnings")} if isinstance(v, dict) else None
                    if w["validator"] is None or w["validator"].get("numErrors") is None:
                        iss = (j.get("validator") or {}).get("issues") or j.get("issues") or {}
                        w["validator"] = {k: iss.get(k) for k in ("numErrors", "numWarnings")}
                except Exception as e:  # noqa
                    w["validator_raw"] = (r.stdout + r.stderr)[-400:]
                out = f"{ex}/web/{name}"
                r, sec = run(["python3", "99-raw/tools/web_view.py", glb, out, "--tone", "neutral", "--views", "4",
                              "--size", "800x600"], timeout=300)
                w["web_view_exit"], w["web_view_sec"] = r.returncode, sec
                st = f"{out}/stats.json" if os.path.exists(f"{out}/stats.json") else f"{out}/web_stats.json"
                if os.path.exists(st):
                    s = json.load(open(st))
                    info = s.get("info") or {}
                    w["three"] = {"rev": info.get("three"), "load_ms": info.get("load_ms"), "meshes": info.get("meshes"),
                                  "materials": info.get("materials"), "textures": info.get("textures"),
                                  "max_tex": info.get("max_texture_px"), "types": info.get("material_types"),
                                  "anims": len(info.get("animations") or []), "frame_time": s.get("frame_time"),
                                  "console": s.get("console")}
                rec["web"][name] = w
                print(f"[{slug}] web {name}: {w.get('validator')} exit={w['web_view_exit']}")
        res[slug] = rec
        json.dump(res, open(RES, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: {kk: v.get(kk) for kk in ("exit", "sec", "blocks_run")} for k, v in res.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
