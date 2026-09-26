#!/usr/bin/env python3
"""run_set.py — прогон регрессионного набора (manifest.json) через qa_pipeline.py и сравнение с базовой линией.

    python3 11-evaluation-qa/regression/run_set.py --label baseline [--tiers core,negative,k] [--pages] [--diff]
    python3 11-evaluation-qa/regression/run_set.py --label new --compare baseline      # что стало хуже

Сцены (.blend) — одним вызовом `qa_pipeline.py scene` с паспортами из манифеста; GLB — `qa_pipeline.py glb` по одному;
анимация — `three_probe.py` + check.js (углы в четвертях); страницы — `qa_pipeline.py page` (только с --pages, 12–16 с каждая).
Регрессия: вердикт хуже; новый код WARN/ERROR; вес GLB или треугольники +20 %; отрицательный контроль перестал ловиться.
Результат: results_<label>.json рядом с манифестом; код выхода 1, если есть регрессии.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
M = json.load(open(str(kbpaths.kb("blender", "11-evaluation-qa", "regression", "manifest.json"))))  # перенос: набор — в kb (Р58: данные пересоздаются)
ROOT = M["root"]
QA = str(kbpaths.scripts("blender", "qa_pipeline.py"))
PROBE = str(kbpaths.scripts("blender", "three_probe.py"))
RANK = {"pass": 0, "review": 1, "fail": 2}


def opt(a, n, d=None):
    return a[a.index(n) + 1] if n in a else d


def qa(args):
    out = tempfile.mktemp(suffix=".json")
    subprocess.run([sys.executable, QA] + args + ["--out", out], capture_output=True, text=True, timeout=900, cwd=ROOT)
    return json.load(open(out)) if os.path.exists(out) else {"verdict": "fail", "codes": ["runner_failed"]}


def main():
    a = sys.argv[1:]
    label = opt(a, "--label", "run")
    tiers = set((opt(a, "--tiers") or "core,negative,page,k").split(","))
    ents = [e for e in M["entries"] if e["tier"].split(" ")[0].replace("k-recipes", "k") in tiers]
    res = {}
    # 1. сцены одним процессом Blender
    blends = [e for e in ents if e.get("blend")]
    if blends:
        pmap = {os.path.splitext(os.path.basename(e["blend"]))[0]: e["passport"] for e in blends if e.get("passport")}
        pj = tempfile.mktemp(suffix=".json")
        json.dump(pmap, open(pj, "w"))
        r = qa(["scene"] + [os.path.join(ROOT, e["blend"]) for e in blends] + ["--passports", pj])
        for e in blends:
            f = r.get("files", {}).get(os.path.basename(e["blend"]), {})
            m = f.get("metrics", {})
            res.setdefault(e["id"], {})["scene"] = {"verdict": f.get("verdict", "fail"), "codes": f.get("codes", ["missing"]),
                                                    "tris": (m.get("totals") or {}).get("tris"), "dims_m": m.get("dims_m")}
    # 2. GLB по одному
    for e in ents:
        if e.get("glb"):
            args = ["glb", os.path.join(ROOT, e["glb"])]
            if "--diff" in a and e.get("blend"):
                args += ["--blend", os.path.join(ROOT, e["blend"]), "--diff"]
            r = qa(args)
            lint = (r.get("report") or {}).get("glb_lint") or {}
            res.setdefault(e["id"], {})["glb"] = {"verdict": r.get("verdict"), "codes": r.get("codes", []),
                                                  "file_kb": (r.get("report") or {}).get("file_kb"),
                                                  "tris": lint.get("triangles") or lint.get("tris"), "calls": lint.get("draw_calls_estimate"), "gpu_tex_mb": lint.get("gpu_textures_mb")}
    # 3. анимация: углы в четвертях
    for e in ents:
        if e.get("anim_check"):
            q = subprocess.run([sys.executable, PROBE, os.path.join(ROOT, e["glb"]), os.path.join(ROOT, e["anim_check"])],
                               capture_output=True, text=True, timeout=300)
            try:
                d = json.loads(q.stdout)
                ang = dict((t, v) for t, v in d["angles"])
                got = [ang.get(t) for t in (0.5, 1.5, 2.5, 3.5)]
                ok = all(g is not None and abs(g - x) <= 1 for g, x in zip(got, e["anim_expect"]["quarters"]))
            except (ValueError, KeyError):
                got, ok = None, False
            res.setdefault(e["id"], {})["anim"] = {"verdict": "pass" if ok else "fail", "quarters": got}
    # 4. страницы (долго)
    if "--pages" in a:
        for e in ents:
            if e.get("page") and e["tier"] == "page":
                r = qa(["page", os.path.join(ROOT, e["page"])])
                res.setdefault(e["id"], {})["page"] = {"verdict": r.get("verdict"), "codes": r.get("codes", []),
                                                       "gates_failed": [g["check"] for g in r.get("gates", []) if not g["ok"]]}
    out = os.path.join(HERE, f"results_{label}.json")
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    # сравнение и отрицательные контроли
    probs = []
    for e in ents:
        r = res.get(e["id"], {})
        if e["tier"] == "negative":
            codes = set((r.get("scene") or {}).get("codes", []))
            if e.get("expect_codes") and not set(e["expect_codes"]) <= codes:
                probs.append(f'{e["id"]}: контроль не пойман, нет {sorted(set(e["expect_codes"]) - codes)}')
            if e.get("expect_fail") and (r.get("anim") or {}).get("verdict") != "fail":
                probs.append(f'{e["id"]}: анимационный контроль не пойман')
    base = opt(a, "--compare")
    if base:
        b = json.load(open(os.path.join(HERE, f"results_{base}.json")))
        for eid, stages in res.items():
            for st, v in stages.items():
                bv = (b.get(eid) or {}).get(st)
                if not bv or eid.startswith("neg-"):
                    continue
                if RANK.get(v.get("verdict"), 2) > RANK.get(bv.get("verdict"), 2):
                    probs.append(f"{eid}/{st}: вердикт {bv.get('verdict')} → {v.get('verdict')}")
                new = sorted(set(v.get("codes") or []) - set(bv.get("codes") or []))
                if new:
                    probs.append(f"{eid}/{st}: новые коды {new}")
                for k in ("file_kb", "tris"):
                    if v.get(k) and bv.get(k) and v[k] > 1.2 * bv[k]:
                        probs.append(f"{eid}/{st}: {k} {bv[k]} → {v[k]} (+{round(100 * (v[k] / bv[k] - 1))} %)")
    summary = {k: {st: v.get("verdict") for st, v in s.items()} for k, s in res.items()}
    print(json.dumps(summary, ensure_ascii=False))
    print("PROBLEMS:", len(probs))
    for p in probs:
        print("  -", p)
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
