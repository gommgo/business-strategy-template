#!/usr/bin/env python3
"""series_metrics.py — согласованность серии картинок без платных судей.
Python 3.13, numpy, Pillow; палитра и OKLab — palette.py рядом.
Для набора: σ средней светлоты L, σ медианы хромы C, круговой разброс оттенка хроматических пикселей (°),
b* нейтралей (σ), попарный ΔE палитр (симметричная adherence, OKLab), pHash (Хэмминг из 64) — дубли и разнообразие.
CLI: python3 series_metrics.py IMG1 IMG2 … [--ref REF1 REF2 …] → JSON (с --ref — ещё ΔE каждой картинки к палитре эталона)."""
import sys, os, json, itertools, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # palette.py — рядом
from palette import load, to_oklab, palette, adherence
def phash(p):
    g = np.asarray(Image.open(p).convert("L").resize((32, 32), Image.LANCZOS)).astype(np.float64)
    n = 32; k = np.arange(n); D = np.cos(np.pi * (2 * k[None] + 1) * k[:, None] / (2 * n))   # DCT-II
    c = (D @ g @ D.T)[:8, :8]; return (c > np.median(c[1:].ravel())).ravel()
def per_image(p):
    im = load(p, 600); X = to_oklab(im.reshape(-1, 3)); C = np.hypot(X[:, 1], X[:, 2]); h = np.arctan2(X[:, 2], X[:, 1])
    ch = C > 0.04; n = C < 0.03
    return {"L": float(X[:, 0].mean()), "C": float(np.median(C)), "hue": float(np.angle(np.exp(1j * h[ch]).mean())) if ch.any() else 0.0,
            "b_neutral": float(X[n, 2].mean()) if n.any() else 0.0, "pal": palette(im, 5), "ph": phash(p)}
def series(paths, ref=None):
    I = [per_image(p) for p in paths]
    hue = np.array([i["hue"] for i in I]); R = abs(np.exp(1j * hue).mean())
    pal_de = [0.5 * (adherence(a["pal"], b["pal"]) + adherence(b["pal"], a["pal"])) for a, b in itertools.combinations(I, 2)]
    ham = [int((a["ph"] != b["ph"]).sum()) for a, b in itertools.combinations(I, 2)]
    out = {"n": len(I), "sd_L": round(float(np.std([i["L"] for i in I])), 4), "sd_C": round(float(np.std([i["C"] for i in I])), 4),
           "hue_spread_deg": round(float(np.degrees(np.sqrt(-2 * np.log(max(R, 1e-9))))), 1),
           "sd_b_neutral": round(float(np.std([i["b_neutral"] for i in I])), 4),
           "pal_dE_mean": round(float(np.mean(pal_de)), 4), "pal_dE_max": round(float(np.max(pal_de)), 4),
           "phash_min": min(ham), "phash_mean": round(float(np.mean(ham)), 1)}
    if ref:
        rp = palette(np.concatenate([load(r, 600).reshape(-1, 3) for r in ref])[None], 6)
        out["dE_to_ref"] = [round(adherence(i["pal"], rp), 4) for i in I]
    return out
if __name__ == "__main__":
    a = sys.argv[1:]; ref = None
    if "--ref" in a: k = a.index("--ref"); ref = a[k + 1:]; a = a[:k]
    print(json.dumps(series(a, ref), ensure_ascii=False))
