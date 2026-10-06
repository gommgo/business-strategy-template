#!/usr/bin/env python3
"""text_zone.py — контраст HTML-текста поверх картинки по зоне и минимальный скрим.
Python 3.13, numpy, Pillow 11.3.
Библиотека: zone_stats(img, rect), zone_contrast(img, rect, text_hex), scrim_alpha(img, rect, text_hex, target, q),
glyph_true(img, rect, text_hex, text) — «истинный» контраст под буквами (фон под маской глифов).
CLI: python3 text_zone.py IMG x0 y0 x1 y1 [#fff|#111] — rect в долях кадра."""
import sys, json, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def load(p, w=1280):
    im = Image.open(p).convert("RGB")
    if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def relL(rgb): l = lin(rgb); return 0.2126 * l[..., 0] + 0.7152 * l[..., 1] + 0.0722 * l[..., 2]
def hexrgb(h): h = h.lstrip('#'); h = ''.join(c * 2 for c in h) if len(h) == 3 else h; return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], np.float32) / 255
def ratio(a, b): hi, lo = np.maximum(a, b), np.minimum(a, b); return (hi + 0.05) / (lo + 0.05)
def crop(a, rect):
    H, W = a.shape[:2]; x0, y0, x1, y1 = rect
    return a[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
def edge_density(rgb, thr=0.10):
    L = relL(rgb) ** (1 / 2.2)                     # перцептивная яркость ~ гамма
    gx = np.abs(np.diff(L, axis=1))[:-1, :]; gy = np.abs(np.diff(L, axis=0))[:, :-1]
    g = np.hypot(gx, gy); return float((g > thr).mean())
def zone_stats(img, rect):
    z = crop(img, rect); L = relL(z).ravel()
    q = np.percentile(L, [0, 5, 50, 95, 100])
    return {"L_min": q[0], "L_p5": q[1], "L_p50": q[2], "L_p95": q[3], "L_max": q[4], "L_mean": float(L.mean()),
            "edge_density": edge_density(z), "L_std": float(L.std())}
def zone_contrast(img, rect, text_hex):
    s = zone_stats(img, rect); Lt = relL(hexrgb(text_hex)[None, None, :])[0, 0]
    light = Lt > 0.18                                 # светлый текст — худший фон самый светлый
    worst = s["L_max"] if light else s["L_min"]; p = s["L_p95"] if light else s["L_p5"]
    return {"mean": float(ratio(Lt, s["L_mean"])), "p95": float(ratio(Lt, p)), "worst": float(ratio(Lt, worst)), **s}
def composite(z, color_rgb, a): return z * (1 - a) + color_rgb * a     # как браузер: смешение в sRGB (гамма)
def scrim_alpha(img, rect, text_hex, target=4.5, q=95, scrim_hex=None):
    """Минимальная альфа равномерного скрима, при которой контраст по q-перцентилю ≥ target."""
    z = crop(img, rect); Lt = relL(hexrgb(text_hex)[None, None, :])[0, 0]; light = Lt > 0.18
    sc = hexrgb(scrim_hex or ("#000000" if light else "#ffffff"))
    def ok(a):
        L = relL(composite(z, sc, a)).ravel(); p = np.percentile(L, q if light else 100 - q); return ratio(Lt, p) >= target
    if ok(0.0): return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(9):
        m = (lo + hi) / 2; lo, hi = (lo, m) if ok(m) else (m, hi)
    return round(hi, 3)
def glyph_true(img, rect, text_hex, text="Заголовок сайта", px=None):
    """Рендер строки в зоне → фон под глифами (маска, раздутая на 2 px) → контраст: минимум и 5-й перцентиль."""
    H, W = img.shape[:2]; x0, y0, x1, y1 = rect
    px = px or max(18, int((y1 - y0) * H * 0.12))
    f = ImageFont.truetype(FONT, px); zw = (x1 - x0) * W * 0.88
    while f.getlength(text) > zw and px > 12: px -= 2; f = ImageFont.truetype(FONT, px)   # строка целиком внутри зоны
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.text((int(x0 * W + 0.06 * (x1 - x0) * W), int(y0 * H + (y1 - y0) * H * 0.35)), text, font=f, fill=255)
    m = m.filter(ImageFilter.MaxFilter(5)); mask = np.asarray(m) > 0
    Lt = relL(hexrgb(text_hex)[None, None, :])[0, 0]; L = relL(img)[mask]
    r = ratio(Lt, L); return {"glyph_min": float(r.min()), "glyph_p5": float(np.percentile(r, 5)), "px": px, "n": int(mask.sum())}
if __name__ == "__main__":
    a = sys.argv[1:]; img = load(a[0]); rect = tuple(map(float, a[1:5])); t = a[5] if len(a) > 5 else "#ffffff"
    out = zone_contrast(img, rect, t); out["scrim_alpha_4.5_p95"] = scrim_alpha(img, rect, t)
    print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}, ensure_ascii=False))
