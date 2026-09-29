#!/usr/bin/env python3
"""palette.py — палитра картинки (k-means в OKLab с долями), ΔE к эталону, перенос цвета (Reinhard, MKL) и экспорт 3D LUT
(.cube). Python окружения скилла: numpy, Pillow.

Командная строка — замер палитры ассетов (этап design-system: палитра ключевых ассетов кодом, не со слов модели):
  palette.py IMG… [--k 6] [--json]
    на картинку — доминирующие цвета по площади: hex, доля, OKLCH (L, C, h°) и нейтрали — средние a, b OKLab пикселей с
    хромой < 0,03 (b > 0 — тёплые, b < 0 — холодные) и медиана хромы; у двух картинок и больше — ещё общая палитра всех
    (all); без --json — таблица. Картинка не читается — одна строка ошибки и код 2.

Модуль (импорт из соседних утилит):
  load(path, w=800) -> float RGB 0…1             — картинка, уменьшенная до стороны w
  palette(img, k=6) -> [(hex, share, oklab)]      — доминирующие цвета по площади; цветов меньше k — палитра короче
  adherence(pal, ref_pal) -> ΔE OKLab             — средняя по площади дистанция цветов картинки до ближайшего цвета эталона
  transfer_reinhard(src, ref, strength) / transfer_mkl(src, ref, strength) — глобальный перенос в OKLab
  grade_params, grade_match, parametric_grade     — грейд без содержания и параметрический грейд паспорта
  write_cube(fn, func, n=33)                      — LUT: func применяется к решётке sRGB, порядок R быстрее всего (Adobe .cube 1.0)"""
import numpy as np
from PIL import Image
M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def gam(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
def to_oklab(rgb): return np.cbrt(lin(rgb) @ M1.T) @ M2.T
def from_oklab(lab): return gam((np.linalg.inv(M2) @ lab.reshape(-1, 3).T).T.__pow__(3) @ np.linalg.inv(M1).T).reshape(lab.shape)
def load(p, w=800):
    im = Image.open(p).convert("RGB"); im.thumbnail((w, w)); return np.asarray(im).astype(np.float64) / 255
def hexs(rgb): return "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in np.clip(rgb, 0, 1))
def palette(img, k=6, iters=20, seed=0):
    X = to_oklab(img.reshape(-1, 3)); rng = np.random.default_rng(seed); X = X[rng.choice(len(X), min(20000, len(X)), replace=False)]
    C = X[[rng.integers(len(X))]]
    for _ in range(k - 1):                                          # k-means++
        d = ((X[:, None] - C[None]) ** 2).sum(-1).min(1)
        if not d.sum() > 0:                                         # цветов меньше k: центров столько, сколько цветов
            break
        C = np.vstack([C, X[rng.choice(len(X), p=d / d.sum())]])
    k = len(C)
    for _ in range(iters):
        lab_ = ((X[:, None] - C[None]) ** 2).sum(-1).argmin(1)
        C = np.array([X[lab_ == j].mean(0) if (lab_ == j).any() else C[j] for j in range(k)])
    share = np.bincount(lab_, minlength=k) / len(X); o = np.argsort(-share)
    return [(hexs(from_oklab(C[j][None])[0]), float(share[j]), C[j]) for j in o]
def adherence(pal, ref_pal):
    R = np.array([c[2] for c in ref_pal]); return float(sum(s * np.sqrt(((c - R) ** 2).sum(1)).min() for _, s, c in pal))
def stats(img): X = to_oklab(img.reshape(-1, 3)); return X.mean(0), X.std(0), np.cov(X.T)
def transfer_reinhard(src, ref, strength=1.0):
    X = to_oklab(src.reshape(-1, 3)); ms, ss, _ = stats(src); mr, sr, _ = stats(ref)
    Y = (X - ms) * (sr / (ss + 1e-9)) + mr; Y = X + strength * (Y - X); return from_oklab(Y).reshape(src.shape)
def _sqrtm(A): w, V = np.linalg.eigh(A); return V @ np.diag(np.sqrt(np.clip(w, 1e-12, None))) @ V.T
def mkl_params(src, ref):
    ms, _, Cs = stats(src); mr, _, Cr = stats(ref); Cs12 = _sqrtm(Cs); iCs12 = np.linalg.inv(Cs12)
    return ms, mr, iCs12 @ _sqrtm(Cs12 @ Cr @ Cs12) @ iCs12        # Pitié & Kokaram 2007 (линейное MKL)
def apply_mkl(img, params, strength=1.0):
    ms, mr, T = params; X = to_oklab(img.reshape(-1, 3)); Y = (X - ms) @ T.T + mr; Y = X + strength * (Y - X)
    return from_oklab(Y).reshape(img.shape)
def write_cube(fn, func, n=33, title="F/05"):
    g = np.linspace(0, 1, n); b, gg, r = np.meshgrid(g, g, g, indexing="ij")    # R меняется быстрее всего
    lattice = np.stack([r, gg, b], -1).reshape(-1, 3); out = np.clip(func(lattice.reshape(1, -1, 3)).reshape(-1, 3), 0, 1)
    with open(fn, "w") as f:
        f.write(f'TITLE "{title}"\nLUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        for v in out: f.write("%.6f %.6f %.6f\n" % tuple(v))

def grade_params(img, neutral_c=0.03):
    """Параметры грейда без содержания: перцентили светлоты, медиана хромы, средний a/b нейтральных пикселей."""
    X = to_oklab(img.reshape(-1, 3)); C = np.hypot(X[:, 1], X[:, 2]); n = C < neutral_c
    return {"Lq": np.percentile(X[:, 0], [1, 25, 50, 75, 99]), "Cmed": float(np.median(C)),
            "ab_neutral": X[n, 1:].mean(0) if n.any() else np.zeros(2)}
def grade_match(src, ref_params, strength=1.0, c_clip=(0.7, 1.3)):
    """Перенос только грейда: кусочно-линейная кривая L по перцентилям, масштаб хромы (с ограничением), сдвиг баланса
    белого по нейтралям с весом, падающим с хромой. Оттенки объектов сцены сохраняются."""
    X = to_oklab(src.reshape(-1, 3)); sp = grade_params(src); rp = ref_params
    L = np.interp(X[:, 0], sp["Lq"], rp["Lq"]); k = np.clip(rp["Cmed"] / max(sp["Cmed"], 1e-6), *c_clip)
    C = np.hypot(X[:, 1], X[:, 2]); w = np.clip(1 - C / 0.08, 0, 1)[:, None]
    ab = X[:, 1:] * k + w * (rp["ab_neutral"] - sp["ab_neutral"])
    Y = np.column_stack([L, ab]); Y = X + strength * (Y - X); return from_oklab(Y).reshape(src.shape)

def parametric_grade(img, wb_ab=(0.0, 0.008), chroma=0.9, black=0.03, white=0.98, contrast=0.12, neutral_c=0.08):
    """Грейд бренда числами паспорта (не из чужой сцены): L' = black + (white−black)·((1−k)·L + k·smoothstep(L)),
    ab' = ab·chroma + wb_ab·вес нейтральности. Оттенки объектов сохраняются, меняется «плёнка»."""
    X = to_oklab(img.reshape(-1, 3)); L = np.clip(X[:, 0], 0, 1); s = L * L * (3 - 2 * L)
    L2 = black + (white - black) * ((1 - contrast) * L + contrast * s)
    C = np.hypot(X[:, 1], X[:, 2]); w = np.clip(1 - C / neutral_c, 0, 1)[:, None]
    ab = X[:, 1:] * chroma + w * np.array(wb_ab)
    return from_oklab(np.column_stack([L2, ab])).reshape(img.shape)

def oklch(lab):
    """OKLab → [L, C, h°]."""
    L, a, b = (float(v) for v in lab)
    return [round(L, 4), round(float(np.hypot(a, b)), 4), round(float(np.degrees(np.arctan2(b, a)) % 360), 1)]

def measure(img, k=6, neutral_c=0.03):
    """Замер командной строки: палитра (hex, доля, OKLCH) и нейтрали (средние a, b OKLab пикселей с хромой < neutral_c)."""
    X = to_oklab(img.reshape(-1, 3)); C = np.hypot(X[:, 1], X[:, 2]); n = C < neutral_c
    return {"palette": [{"hex": h, "share": round(s, 4), "oklch": oklch(c)} for h, s, c in palette(img, k)],
            "neutral": {"share": round(float(n.mean()), 4), "a": round(float(X[n, 1].mean()), 4) if n.any() else None,
                        "b": round(float(X[n, 2].mean()), 4) if n.any() else None, "chroma_median": round(float(np.median(C)), 4)}}

def to_text(rec, title):
    lines = [f"{title}", "  hex       доля    L       C       h°"]
    lines += [f"  {c['hex']}  {c['share']:.3f}  {c['oklch'][0]:.3f}  {c['oklch'][1]:.4f}  {c['oklch'][2]:.1f}" for c in rec["palette"]]
    nt = rec["neutral"]
    ab = f"a {nt['a']:+.4f}, b {nt['b']:+.4f}" if nt["a"] is not None else "нейтралей нет"
    lines.append(f"  нейтрали (хрома < 0,03): доля {nt['share']:.3f}, {ab}; медиана хромы {nt['chroma_median']:.4f}")
    return "\n".join(lines)

def main(argv=None):
    import argparse, json, sys
    ap = argparse.ArgumentParser(prog="palette.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+", metavar="IMG", help="картинки (ключевые ассеты)")
    ap.add_argument("--k", type=int, default=6, help="число цветов палитры (по умолчанию 6)")
    ap.add_argument("--json", action="store_true", help="JSON в stdout: {k, images: [{file, palette, neutral}], all}")
    a = ap.parse_args(argv)
    if a.k < 1:
        ap.error("--k — не меньше 1")
    out, imgs = {"k": a.k, "images": []}, []
    for p in a.images:
        try:
            img = load(p)
        except (OSError, ValueError) as e:
            print(f"palette.py: картинка не читается: {p} ({type(e).__name__}: {e})", file=sys.stderr)
            return 2
        imgs.append(img)
        out["images"].append({"file": p, **measure(img, a.k)})
    if len(imgs) > 1:   # общая палитра: пиксели всех картинок вместе (каждая уменьшена до стороны 800)
        out["all"] = measure(np.concatenate([i.reshape(-1, 3) for i in imgs])[None], a.k)
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print("\n\n".join([to_text(r, r["file"]) for r in out["images"]] + ([to_text(out["all"], "все картинки")] if "all" in out else [])))
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
