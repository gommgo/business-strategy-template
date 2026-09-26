#!/usr/bin/env python3
"""alpha_check.py — проверка прозрачности (вырез, нативная альфа модели, матирование). Агент H, волна 2, 23.09.2026.
Python 3.13 + numpy + scipy + Pillow (системные).

Команды:
  metrics PRED GT_ALPHA [--rgb GT_RGBA]   альфа против эталона (свой рендер Blender): IoU@0.5, MAE, MSE, SAD, ошибка
                                          в полосе края, ошибка композита на чёрном и белом (ореол, ΔE00 в полосе)
  halo    RGBA [--bg #RRGGBB]             без эталона: доли прозрачного/полупрозрачного, ширина «загрязнённой» каймы
                                          (цвет каймы ближе к исходному фону, чем к объекту) → halo_px; критерий ≤ 2 px
  fake    IMG                             «нарисованная шахматка вместо прозрачности» (OpenAI: «checkerboard is not
                                          transparency»): альфа непрозрачна + периодические квадраты двух серых
Выход — JSON в stdout. [проверено: 99-raw/experiments/H/01-background-removal]
"""
import argparse, json, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from edit_check import srgb_to_lab, de2000  # noqa: E402


def load_alpha(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
        return np.asarray(im.convert("RGBA"), np.float32)[..., 3] / 255.0
    return np.asarray(im.convert("L"), np.float32) / 255.0   # маска в оттенках серого


def load_rgba(path):
    return np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255.0


def edge_band(gt, r=5):
    partial = (gt > 0.02) & (gt < 0.98)
    hard = ndi.binary_dilation(gt > 0.5, iterations=1) ^ ndi.binary_erosion(gt > 0.5, iterations=1)
    return ndi.binary_dilation(partial | hard, iterations=r)


def cmd_metrics(a):
    P = load_alpha(a.pred)
    G = load_alpha(a.gt)
    if P.shape != G.shape:
        P = np.asarray(Image.fromarray((P * 255).astype(np.uint8)).resize(G.shape[::-1], Image.BILINEAR), np.float32) / 255
    band = edge_band(G)
    inter = ((P > 0.5) & (G > 0.5)).sum(); uni = ((P > 0.5) | (G > 0.5)).sum()
    r = {"iou": round(float(inter / max(uni, 1)), 4),
         "mae_x1000": round(float(np.abs(P - G).mean() * 1000), 2),
         "mse_x1000": round(float(((P - G) ** 2).mean() * 1000), 3),
         "sad_k": round(float(np.abs(P - G).sum() / 1000), 2),
         "band_mae_x1000": round(float(np.abs(P - G)[band].mean() * 1000), 1),
         "band_frac": round(float(band.mean()), 4),
         "gt_partial_frac": round(float(((G > 0.02) & (G < 0.98)).mean()), 4),
         "pred_partial_frac": round(float(((P > 0.02) & (P < 0.98)).mean()), 4)}
    if a.rgb:   # композит предсказания (цвет исходника a.src) против эталонного композита на чёрном и белом
        GT = load_rgba(a.rgb)
        src = load_rgba(a.src)[..., :3] if a.src else GT[..., :3]
        for name, bg in (("black", 0.0), ("white", 1.0)):
            cg = GT[..., :3] * G[..., None] + bg * (1 - G[..., None])
            cp = src * P[..., None] + bg * (1 - P[..., None])
            de = de2000(srgb_to_lab(np.clip(cg, 0, 1)), srgb_to_lab(np.clip(cp, 0, 1)))
            r[f"comp_{name}_band_de_mean"] = round(float(de[band].mean()), 2)
            r[f"comp_{name}_band_de_p95"] = round(float(np.percentile(de[band], 95)), 2)
    print(json.dumps(r, ensure_ascii=False))
    return 0


def hex2rgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def cmd_halo(a):
    X = load_rgba(a.rgba)
    al = X[..., 3]
    r = {"transparent_frac": round(float((al < 0.02).mean()), 4), "opaque_frac": round(float((al > 0.98).mean()), 4),
         "partial_frac": round(float(((al >= 0.02) & (al <= 0.98)).mean()), 4)}
    if r["transparent_frac"] < 0.001:
        r["verdict"] = "NO_ALPHA"; print(json.dumps(r, ensure_ascii=False)); return 1
    core = al > 0.98
    dist = ndi.distance_transform_edt(~core)
    fringe = (al > 0.02) & ~core & (dist <= 12)
    # цвет исходного фона: задан или оценён по полупрозрачной кайме (если объект на светлом — кайма светлая)
    bg = hex2rgb(a.bg) if a.bg else None
    # цвет объекта рядом: размытие ядра
    w = ndi.gaussian_filter(core.astype(np.float32), 4) + 1e-6
    obj = np.stack([ndi.gaussian_filter(X[..., c] * core, 4) / w for c in range(3)], -1)
    rgb = X[..., :3]
    if bg is None:   # «загрязнение» = кайма заметно светлее/темнее объекта (ореол на контрастном фоне)
        lum = rgb @ [0.2126, 0.7152, 0.0722]; lo = obj @ [0.2126, 0.7152, 0.0722]
        cont = fringe & (np.abs(lum - lo) > 0.25)
    else:
        d_bg = np.linalg.norm(rgb - bg, axis=-1); d_obj = np.linalg.norm(rgb - obj, axis=-1)
        cont = fringe & (d_bg < d_obj)
    r["fringe_px"] = int(fringe.sum()); r["contaminated_px"] = int(cont.sum())
    r["halo_px"] = round(float(np.percentile(dist[cont], 95)), 2) if cont.sum() > 20 else 0.0
    r["verdict"] = "PASS" if r["halo_px"] <= 2.0 else "HALO"
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["verdict"] == "PASS" else 1


def cmd_fake(a):
    im = Image.open(a.img)
    X = np.asarray(im.convert("RGBA"), np.float32) / 255
    opaque = float((X[..., 3] > 0.98).mean())
    g = X[..., :3] @ [0.2126, 0.7152, 0.0722]
    sat = X[..., :3].max(-1) - X[..., :3].min(-1)
    best = (0.0, 0)
    for s in range(6, 65):
        if 2 * s >= min(g.shape):
            break
        same = np.abs(g[:, 2 * s:] - g[:, :-2 * s]) < 0.02
        diff = np.abs(g[:, s:-s] - g[:, :-2 * s]) > 0.04
        m = (sat[:, :-2 * s] < 0.05) & (g[:, :-2 * s] > 0.5)
        score = float((same[:, :diff.shape[1]] & diff & m[:, :diff.shape[1]]).mean())
        if score > best[0]:
            best = (score, s)
    r = {"opaque_frac": round(opaque, 4), "checker_score": round(best[0], 4), "checker_period_px": best[1] * 2}
    r["verdict"] = "FAKE_CHECKERBOARD" if opaque > 0.99 and best[0] > 0.05 else ("REAL_ALPHA" if opaque < 0.99 else "OPAQUE")
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["verdict"] == "REAL_ALPHA" else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("metrics"); m.add_argument("pred"); m.add_argument("gt"); m.add_argument("--rgb"); m.add_argument("--src")
    h = sp.add_parser("halo"); h.add_argument("rgba"); h.add_argument("--bg")
    f = sp.add_parser("fake"); f.add_argument("img")
    a = ap.parse_args()
    sys.exit({"metrics": cmd_metrics, "halo": cmd_halo, "fake": cmd_fake}[a.cmd](a))


if __name__ == "__main__":
    main()
