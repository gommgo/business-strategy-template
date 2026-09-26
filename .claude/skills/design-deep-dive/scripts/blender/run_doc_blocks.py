#!/usr/bin/env python3
"""run_doc_blocks.py (агент J, волна 3) — исполнить блоки кода итоговых .md в напечатанном виде; обобщение раннеров
D2/99 (run_all.py), E/26 (md_blocks.py + run_md.py), H/30, F2/09.

    python3 99-raw/tools/run_doc_blocks.py FILE.md [FILE2.md …] [--json result.json] [--only python,bash] [--timeout 600]

python → один фоновый Blender 5.2.2 (blender_run.py); перед каждым блоком read_factory_settings(use_empty=True), своё
         пространство имён, stdout перехвачен; блок с первой строкой «# run: system» — системный python3.
bash   → `bash -e -c` в корне базы (переменная OUT_DIR — временная папка).
js     → не исполняется здесь (нужна страница с import map: образцы F2/09 run_blocks.py, H/30 run_js.py) — помечается skip.
Блок пропускается, если в первых двух строках есть «[не проверено]» или «# run: skip». Итог — строка RESULT ok/total.
"""
import json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb("blender"))
TOOLS = str(kbpaths.scripts("blender"))
RUNNER = r'''
import bpy, json, sys, traceback, io, contextlib
a = sys.argv[sys.argv.index("--") + 1:]
bl = json.load(open(a[0])); out = []
for b in bl:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ns = {"__name__": "__doc_block__"}; buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(b["code"], "%s:%d" % (b["doc"], b["line"]), "exec"), ns)
        out.append({"doc": b["doc"], "line": b["line"], "ok": True, "stdout": buf.getvalue()[-600:]})
    except Exception:
        out.append({"doc": b["doc"], "line": b["line"], "ok": False, "stdout": buf.getvalue()[-300:],
                    "error": traceback.format_exc()[-1500:]})
json.dump(out, open(a[1], "w"), ensure_ascii=False, indent=1)
print("BL_RUNNER_DONE", sum(o["ok"] for o in out), len(out))
'''


def blocks_of(path):
    src = open(path, encoding="utf-8").read()
    for m in re.finditer(r"^```(\w+)\n(.*?)^```", src, re.S | re.M):
        head = "\n".join(m.group(2).splitlines()[:2])
        yield {"doc": os.path.basename(path), "lang": m.group(1), "line": src[:m.start()].count("\n") + 1,
               "code": m.group(2), "skip": "[не проверено]" in head or "# run: skip" in head}


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); sys.exit(0)
    opt = lambda n, d=None: a[a.index(n) + 1] if n in a else d
    only = set((opt("--only") or "python,bash,js").split(","))
    docs = [x for x in a if x.endswith(".md")]
    blocks = [b for d in docs for b in blocks_of(d) if b["lang"] in only]
    tmp = tempfile.mkdtemp(prefix="docblocks_")
    env = dict(os.environ, OUT_DIR=tmp)
    res = []
    bl = [b for b in blocks if b["lang"] == "python" and not b["skip"] and not b["code"].lstrip().startswith("# run: system")]
    if bl:
        jp, op, rp = (os.path.join(tmp, n) for n in ("bl.json", "bl_out.json", "runner.py"))
        json.dump(bl, open(jp, "w"))
        open(rp, "w").write(RUNNER)
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "blender_run.py"), rp, "--timeout", opt("--timeout", "600"),
                            "--", jp, op], capture_output=True, text=True, env=env)
        if os.path.exists(op):
            res += [dict(o, lang="python/blender") for o in json.load(open(op))]
        else:
            res.append({"lang": "python/blender", "ok": False, "error": r.stdout[-2000:] + r.stderr[-1000:]})
    for b in blocks:
        if b["skip"]:
            res.append({"lang": b["lang"], "doc": b["doc"], "line": b["line"], "ok": None, "note": "skip"})
        elif b["lang"] == "python" and b["code"].lstrip().startswith("# run: system"):
            p = os.path.join(tmp, "sys_%d.py" % b["line"]); open(p, "w").write(b["code"])
            q = subprocess.run([sys.executable, p], capture_output=True, text=True, env=env, cwd=ROOT, timeout=600)
            res.append({"lang": "python/system", "doc": b["doc"], "line": b["line"], "ok": q.returncode == 0,
                        "stdout": q.stdout[-600:], "error": q.stderr[-1500:] if q.returncode else ""})
        elif b["lang"] == "bash":
            q = subprocess.run(["bash", "-e", "-c", b["code"]], capture_output=True, text=True, env=env, cwd=ROOT, timeout=900)
            res.append({"lang": "bash", "doc": b["doc"], "line": b["line"], "ok": q.returncode == 0,
                        "stdout": q.stdout[-800:], "error": q.stderr[-1500:] if q.returncode else ""})
        elif b["lang"] in ("js", "javascript"):
            res.append({"lang": "js", "doc": b["doc"], "line": b["line"], "ok": None, "note": "js — раннер страницы (F2/09, H/30)"})
    ran = [r for r in res if r.get("ok") is not None]
    ok = sum(1 for r in ran if r["ok"])
    for r in res:
        mark = "SKIP" if r.get("ok") is None else ("OK  " if r["ok"] else "FAIL")
        print(mark, r.get("lang"), "%s:%s" % (r.get("doc"), r.get("line")), (r.get("error") or "")[-300:].replace("\n", " | "))
    if opt("--json"):
        json.dump(res, open(opt("--json"), "w"), ensure_ascii=False, indent=1)
    print("RESULT %d/%d (пропущено %d)" % (ok, len(ran), len(res) - len(ran)))
    if "--keep" not in a:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if ok == len(ran) else 1)


if __name__ == "__main__":
    main()
