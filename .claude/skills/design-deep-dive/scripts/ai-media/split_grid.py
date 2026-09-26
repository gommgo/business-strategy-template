#!/usr/bin/env python3
"""F/06 split_grid.py — разрезать сетку R×C одной генерации на ячейки: поиск светлых/ровных «желобов», иначе — равное деление.
Python 3.13, numpy, Pillow. CLI: python3 split_grid.py GRID.png OUTDIR [rows cols]"""
import sys, os, numpy as np
from PIL import Image
def gutters(profile, n_cells, min_run=3):
    """Ищет n_cells−1 полос с низкой дисперсией вдоль оси; возвращает центры или None."""
    L = len(profile); cand = []
    for k in range(1, n_cells):
        c = int(L * k / n_cells); w = int(L * 0.06); seg = profile[c - w:c + w]
        i = int(np.argmin(seg)); lo = hi = i; thr = seg[i] + 1.0
        while lo > 0 and seg[lo - 1] <= thr: lo -= 1
        while hi < len(seg) - 1 and seg[hi + 1] <= thr: hi += 1
        cand.append((c - w + lo, c - w + hi + 1) if seg[i] < 4.0 else None)   # желоб — почти ровная полоса (σ < 4 из 255)
    return None if any(x is None for x in cand) else cand
def split(path, out, rows=2, cols=2):
    im = Image.open(path).convert("RGB"); a = np.asarray(im).astype(np.float32).mean(2)
    col_prof = a.std(0); row_prof = a.std(1)
    gx = gutters(col_prof, cols) or [(int(im.width * k / cols),) * 2 for k in range(1, cols)]
    gy = gutters(row_prof, rows) or [(int(im.height * k / rows),) * 2 for k in range(1, rows)]
    xs = [(0, 0)] + gx + [(im.width, im.width)]; ys = [(0, 0)] + gy + [(im.height, im.height)]; os.makedirs(out, exist_ok=True); cells = []
    for r in range(rows):
        for c in range(cols):
            box = (xs[c][1], ys[r][1], xs[c + 1][0], ys[r + 1][0])      # между желобами, без белых полос
            cell = im.crop(box); fn = os.path.join(out, f"cell_{r}{c}.png"); cell.save(fn); cells.append((fn, cell.size))
    return cells, gx, gy
if __name__ == "__main__":
    a = sys.argv[1:]; r, c = (int(a[2]), int(a[3])) if len(a) > 3 else (2, 2); print(split(a[0], a[1], r, c))
