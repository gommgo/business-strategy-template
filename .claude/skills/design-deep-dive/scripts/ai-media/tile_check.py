#!/usr/bin/env python3
"""tile_check.py — бесшовность текстуры: метрика шва, тайл разрезом минимальной ошибки, превью (агент H2, волна 2, 23.09.2026).
Python 3.13 + numpy + Pillow (системные). Функции перенесены из опыта 99-raw/experiments/H/05-tiling-banding/tiling.py.

Команды:
  check   IMG                       seam_ratio (гор., верт.): средняя |разница| на стыке по кругу / медиана разницы соседних
                                    столбцов (строк). ≤ 1,3 — бесшовно (тайлы Poly Haven после ресайза 0,87–1,23), > 1,5 — чинить.
  cut     IMG OUT [--overlap 96]    тайл разрезом по пути минимальной ошибки в полосе перекрытия (Efros–Freeman 2001) по обеим
                                    осям; размер уменьшается на overlap; печатает шов до и после. Для органики (жаккард, камень,
                                    шум); регулярная сетка — заделка креста шва маской (генеративно) или SVG/CSS-паттерн.
  preview IMG OUT                   лист: сдвиг на 50 % (шов в центре крестом) | плитка 2×2 — смотреть глазами.
Выход — JSON в stdout. [проверено: H/05a — жаккард 1,64/1,58 → 1,11/1,11; мешковина 2,79/3,93 → 1,40/1,15]
"""
import argparse, json, sys
import numpy as np
from PIL import Image


def seam_ratio(a):
    a = np.asarray(a, np.float32)
    dcol = np.abs(a[:, 1:] - a[:, :-1]).mean(axis=(0, 2)); drow = np.abs(a[1:] - a[:-1]).mean(axis=(1, 2))
    rh = float(np.abs(a[:, -1] - a[:, 0]).mean() / max(float(np.median(dcol)), 1e-6))
    rv = float(np.abs(a[-1] - a[0]).mean() / max(float(np.median(drow)), 1e-6))
    return round(rh, 2), round(rv, 2)


def min_cut_path(err):
    """Вертикальный путь минимальной суммы ошибки через полосу err (h × o), шаг ±1 столбец за строку."""
    h, o = err.shape
    E = err.copy(); back = np.zeros((h, o), np.int8)
    for y in range(1, h):
        prev = E[y - 1]
        cand = np.stack([np.r_[np.inf, prev[:-1]], prev, np.r_[prev[1:], np.inf]])
        k = np.argmin(cand, 0); back[y] = k - 1
        E[y] += cand[k, np.arange(o)]
    path = np.zeros(h, int); path[-1] = int(np.argmin(E[-1]))
    for y in range(h - 1, 0, -1):
        path[y - 1] = np.clip(path[y] + back[y, path[y]], 0, o - 1)
    return path


def cut_tile_h(a, o):
    """Тайл по горизонтали: правые o столбцов перекрываются с левыми o; шов — по пути минимальной ошибки."""
    h, w = a.shape[:2]
    right, left = a[:, w - o:].astype(np.float32), a[:, :o].astype(np.float32)
    err = ((right - left) ** 2).sum(-1)
    err[:, 0] = 1e12          # столбец 0 всегда из продолжения правого края → стык по кругу непрерывен
    path = min_cut_path(err)
    out = a[:, :w - o].astype(np.float32).copy()
    take_right = np.arange(o)[None, :] < path[:, None]
    out[:, :o] = np.where(take_right[..., None], right, left)
    return out


def cut_tile(a, o=96):
    t = cut_tile_h(np.asarray(a, np.float32), o)
    return np.transpose(cut_tile_h(np.transpose(t, (1, 0, 2)), o), (1, 0, 2))


def to8(x):
    return np.clip(np.asarray(x, np.float32) + 0.5, 0, 255).astype(np.uint8)


def load(p):
    return np.asarray(Image.open(p).convert("RGB"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("check"); c.add_argument("img")
    k = sp.add_parser("cut"); k.add_argument("img"); k.add_argument("out"); k.add_argument("--overlap", type=int, default=96)
    p = sp.add_parser("preview"); p.add_argument("img"); p.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "check":
        rh, rv = seam_ratio(load(a.img))
        v = "SEAMLESS" if max(rh, rv) <= 1.3 else ("BORDERLINE" if max(rh, rv) <= 1.5 else "SEAM")
        print(json.dumps({"seam_ratio": [rh, rv], "verdict": v}, ensure_ascii=False)); return 0 if v == "SEAMLESS" else 1
    if a.cmd == "cut":
        src = load(a.img); before = seam_ratio(src)
        t = to8(cut_tile(src, a.overlap)); Image.fromarray(t).save(a.out); after = seam_ratio(t)
        print(json.dumps({"before": before, "after": after, "size": [t.shape[1], t.shape[0]],
                          "verdict": "SEAMLESS" if max(after) <= 1.3 else "CHECK"}, ensure_ascii=False)); return 0
    if a.cmd == "preview":
        x = load(a.img); h, w = x.shape[:2]
        rolled = np.roll(np.roll(x, w // 2, 1), h // 2, 0)
        tiled = np.tile(x, (2, 2, 1))
        side = 512
        r = Image.fromarray(rolled).resize((side, side), Image.LANCZOS)
        t = Image.fromarray(tiled).resize((side, side), Image.LANCZOS)
        sheet = Image.new("RGB", (2 * side, side)); sheet.paste(r, (0, 0)); sheet.paste(t, (side, 0)); sheet.save(a.out, quality=90)
        print(json.dumps({"preview": a.out}, ensure_ascii=False)); return 0


if __name__ == "__main__":
    sys.exit(main())
