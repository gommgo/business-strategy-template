#!/usr/bin/env python3
"""F/04 composition_metrics.py — маркеры «среднего вида» и пригодности кадра под веб, кодом.
Python 3.13, numpy, scipy, Pillow. Цвет (colorfulness, hdr_index, warm_b, purple_share) — из A/04 image_metrics.metrics.
Метрики:
  centroid_x/y   — центр масс карты значимости (spectral residual, Hou & Zhang 2007) в долях кадра;
  center_offset  — |centroid − 0,5| по x (маркер IMG-M09 «строго в центре»: < 0,08);
  mirror_sym     — корреляция левой и зеркальной правой половины яркости (симметрия, 1 = зеркально);
  empty_share    — доля клеток сетки 16×9 с плотностью краёв ≤ 0,06 (спокойные зоны; «40 % negative space» W2-12);
  zone_edge      — плотность краёв в заданной зоне текста (по умолчанию левые 45 %);
  blobs          — число связных «пятен» значимости > 0,5·max (прокси числа объектов, «≤ 3 элемента»).
CLI: python3 composition_metrics.py IMG [IMG…]  → JSON-строки. [проверено: 99-raw/experiments/F/04-slop-metrics]"""
import sys, os, json, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # перенос: image_metrics.py — рядом
from image_metrics import metrics as color_metrics
def gray(im, w=512):
    im = im.convert("L"); h = round(im.height * w / im.width); return np.asarray(im.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
def saliency(g):
    """Spectral residual: лог-амплитуда минус её сглаживание → обратное FFT → квадрат → размытие."""
    small = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((64, 64), Image.BILINEAR)).astype(np.float32)
    F = np.fft.fft2(small); A = np.log(np.abs(F) + 1e-6); P = np.angle(F)
    R = A - ndimage.uniform_filter(A, 3)
    S = np.abs(np.fft.ifft2(np.exp(R + 1j * P))) ** 2; S = ndimage.gaussian_filter(S, 2.5)
    S = np.asarray(Image.fromarray(S.astype(np.float32)).resize((g.shape[1], g.shape[0]), Image.BILINEAR))
    return S / (S.max() + 1e-9)
def edges(g, thr=0.10):
    gx = np.abs(np.diff(g, axis=1))[:-1, :]; gy = np.abs(np.diff(g, axis=0))[:, :-1]; return np.hypot(gx, gy) > thr
def analyse(path, text_zone=(0, 0, .45, 1)):
    im = Image.open(path).convert("RGB"); g = gray(im); S = saliency(g); H, W = S.shape
    ys, xs = np.mgrid[0:H, 0:W]; m = S ** 2; cx = float((m * xs).sum() / m.sum() / W); cy = float((m * ys).sum() / m.sum() / H)
    half = W // 2; left = g[:, :half]; right = np.fliplr(g[:, W - half:])
    sym = float(np.corrcoef(left.ravel(), right.ravel())[0, 1]) if left.std() > 1e-4 and right.std() > 1e-4 else 0.0
    E = edges(g); gh, gw = 9, 16; eh, ew = E.shape
    cells = [E[i * eh // gh:(i + 1) * eh // gh, j * ew // gw:(j + 1) * ew // gw].mean() for i in range(gh) for j in range(gw)]
    x0, y0, x1, y1 = text_zone; z = E[int(y0 * eh):int(y1 * eh), int(x0 * ew):int(x1 * ew)]
    lab, n = ndimage.label(S > 0.5); sizes = ndimage.sum(np.ones_like(S), lab, range(1, n + 1)) if n else []
    blobs = int(sum(1 for s in sizes if s > 0.002 * S.size))
    out = {"file": os.path.basename(path), "centroid_x": round(cx, 3), "centroid_y": round(cy, 3), "center_offset": round(abs(cx - .5), 3),
           "mirror_sym": round(sym, 3), "empty_share": round(float(np.mean(np.array(cells) <= 0.06)), 3),
           "zone_edge": round(float(z.mean()), 4), "blobs": blobs}
    arr = np.asarray(im.resize((1024, round(im.height * 1024 / im.width)))).astype(np.float32)
    cm = color_metrics(arr); out.update({k: cm[k] for k in ("colorfulness", "hdr_index", "warm_b", "purple_share", "lap_var") if k in cm})
    return out
if __name__ == "__main__":
    for p in sys.argv[1:]: print(json.dumps(analyse(p), ensure_ascii=False))
