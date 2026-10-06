#!/usr/bin/env python3
"""edit_check.py — проверка правки картинки нейросетью и композит оригинала обратно.

Правка моделью никогда не пиксельно точна (Google, документация OpenAI: маска «may not follow its exact shape»), поэтому
после ЛЮБОЙ правки: совместить → карта разницы → доля изменённых пикселей вне цели → решение → при утечке композит
исходника по маске. Python 3.13 + numpy + scipy + Pillow (системные, venv не нужен).

Команды:
  check    ORIG EDITED [--mask M] [--mask-mode white|black|alpha] [--protect P] [--band PX] [--thr DE] [--out DIR]
           [--composite] [--feather PX] [--match-color] [--align shift|none] [--leak-max 0.02]
           Правка «на месте» (тот же кадр). M — где правка РАЗРЕШЕНА (white: белое = цель; black: чёрное = цель;
           alpha: прозрачное = цель, как у OpenAI). Без маски — вся картинка считается «вне цели» (проверка дрейфа).
           P — «защищённая» зона (товар, логотип): SSIM ≥ 0.9 и ΔE00 медиана ≤ 5 (критерий A-3).
  polarity ORIG EDITED MASK
           Где на самом деле менялось: доля изменённых пикселей в белой и в чёрной части маски → полярность модели.
  outpaint ORIG EXTENDED [--out DIR] [--composite] [--feather PX]
           Найти исходник внутри расширенного кадра (масштаб + сдвиг), SSIM центра (критерий ≥ 0.9),
           вставить исходник обратно («product must be pixel perfect, never regenerated»). Совмещение: грубый поиск
           на 256 px → уточнение масштаба (шаг 0,05 %) и субпиксельного сдвига на полном разрешении (v0.2). PASS: SSIM
           центра ≥ 0.9, ΔE00 медиана области исходника ≤ 3, резкость сильных краёв (Собель, верхние 2 %) ≥ 0.85 от
           исходника — иначе REGENERATED.
  selftest Синтетические правки с известным ответом.
  Всегда: edges_iou — IoU карт краёв (Собель, допуск 1 px): геометрия при правке света/цвета (≥ 0.9).

Выход: JSON в stdout и OUT/report.json; OUT/diff_heat.png (ΔE00: чёрный < 2, жёлтый 5, красный ≥ 10);
OUT/composite.png; OUT/sheet.jpg (оригинал | правка | карта разницы | композит) — смотреть глазами.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

VERSION = "0.2 (2026-09-23)"


# ---------- цвет ----------
def load_rgb(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        a = np.asarray(im, np.float32) / 255.0
        rgb = a[..., :3] * a[..., 3:] + 1.0 * (1 - a[..., 3:])   # прозрачное — на белом (для сравнения цвета)
        return rgb
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def srgb_to_lab(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def de2000(lab1, lab2):
    L1, a1, b1 = lab1[..., 0], lab1[..., 1], lab1[..., 2]
    L2, a2, b2 = lab2[..., 0], lab2[..., 1], lab2[..., 2]
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dh = h2p - h1p
    dh = np.where(C1p * C2p == 0, 0, np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh)))
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hs = h1p + h2p
    hbp = np.where(C1p * C2p == 0, hs, np.where(np.abs(h1p - h2p) > 180, np.where(hs < 360, (hs + 360) / 2, (hs - 360) / 2), hs / 2))
    T = (1 - 0.17 * np.cos(np.radians(hbp - 30)) + 0.24 * np.cos(np.radians(2 * hbp)) + 0.32 * np.cos(np.radians(3 * hbp + 6))
         - 0.20 * np.cos(np.radians(4 * hbp - 63)))
    dth = 30 * np.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / np.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -np.sin(np.radians(2 * dth)) * Rc
    return np.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))


def gray(rgb):
    return rgb @ np.array([0.2126, 0.7152, 0.0722])


def edges(g, q=0.85):
    """Карта краёв: модуль Собеля выше квантиля q (порог по каждой картинке — устойчив к общему сдвигу яркости)."""
    m = np.hypot(ndi.sobel(g, 0), ndi.sobel(g, 1))
    return m > np.quantile(m, q)


def edges_iou(g1, g2, tol=1):
    """IoU карт краёв с допуском tol px (≥ 0.9 — геометрия сохранена при правке света)."""
    e1, e2 = edges(g1), edges(g2)
    d1, d2 = ndi.binary_dilation(e1, iterations=tol), ndi.binary_dilation(e2, iterations=tol)
    inter = (e1 & d2).sum() + (e2 & d1).sum()
    return float(inter / max(e1.sum() + e2.sum(), 1))


def ssim_map(x, y, sigma=1.5):
    C1, C2 = 0.01 ** 2, 0.03 ** 2
    mx, my = ndi.gaussian_filter(x, sigma), ndi.gaussian_filter(y, sigma)
    sxx = ndi.gaussian_filter(x * x, sigma) - mx * mx
    syy = ndi.gaussian_filter(y * y, sigma) - my * my
    sxy = ndi.gaussian_filter(x * y, sigma) - mx * my
    return ((2 * mx * my + C1) * (2 * sxy + C2)) / ((mx * mx + my * my + C1) * (sxx + syy + C2))


# ---------- совмещение ----------
def phase_shift(a, b, weight=None):
    """Сдвиг b относительно a (dy, dx) фазовой корреляцией с субпиксельной параболой; weight — где сравнивать."""
    h, w = a.shape
    win = np.outer(np.hanning(h), np.hanning(w))
    if weight is not None:
        win = win * weight
    A = np.fft.fft2((a - a.mean()) * win)
    B = np.fft.fft2((b - b.mean()) * win)
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-9
    r = np.fft.ifft2(R).real
    py, px = np.unravel_index(np.argmax(r), r.shape)

    # парабола по соседям
    def par(vm, v0, vp):
        d = vm - 2 * v0 + vp
        return 0.0 if d == 0 else 0.5 * (vm - vp) / d
    dy = py + par(r[(py - 1) % h, px], r[py, px], r[(py + 1) % h, px])
    dx = px + par(r[py, (px - 1) % w], r[py, px], r[py, (px + 1) % w])
    if dy > h / 2: dy -= h
    if dx > w / 2: dx -= w
    return float(dy), float(dx)


def resize_to(img, w, h):
    arr = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
    return np.asarray(Image.fromarray(arr).resize((w, h), Image.LANCZOS), np.float32) / 255.0


# ---------- маски ----------
def load_mask(path, mode, shape):
    im = Image.open(path)
    h, w = shape
    if mode == "alpha":
        a = np.asarray(im.convert("RGBA").resize((w, h), Image.NEAREST))[..., 3] < 128   # прозрачное = цель
    else:
        g = np.asarray(im.convert("L").resize((w, h), Image.NEAREST)) >= 128
        a = g if mode == "white" else ~g
    return a


def verdict_block(de, ssim, target, band, thr, leak_max):
    outside = ~ndi.binary_dilation(target, iterations=band) if target.any() else np.ones_like(target)
    changed = de > thr
    leak = ndi.binary_opening(changed & outside, structure=np.ones((3, 3)))
    res = {
        "outside_px": int(outside.sum()),
        "outside_changed_frac_de2": round(float((de[outside] > 2).mean()), 4) if outside.any() else None,
        "outside_changed_frac_thr": round(float(changed[outside].mean()), 4) if outside.any() else None,
        "outside_leak_frac": round(float(leak[outside].mean()), 4) if outside.any() else None,
        "outside_de_median": round(float(np.median(de[outside])), 2) if outside.any() else None,
        "outside_de_p95": round(float(np.percentile(de[outside], 95)), 2) if outside.any() else None,
        "outside_ssim": round(float(ssim[outside].mean()), 4) if outside.any() else None,
    }
    if target.any():
        res.update({"target_px": int(target.sum()),
                    "target_changed_frac": round(float(changed[target].mean()), 4),
                    "target_de_median": round(float(np.median(de[target])), 2),
                    "target_ssim": round(float(ssim[target].mean()), 4)})
    ok_leak = res["outside_leak_frac"] is not None and res["outside_leak_frac"] <= leak_max
    ok_edit = (not target.any()) or res["target_changed_frac"] >= 0.2
    res["verdict"] = "PASS" if ok_leak and ok_edit else ("LEAK" if not ok_leak else "NO_EDIT")
    return res, leak


def heat(de):
    t = np.clip(de / 10.0, 0, 1)
    r = np.clip(t * 2, 0, 1); g = np.clip(1.6 * t - 0.2, 0, 1) * (t < 0.75) + (t >= 0.75) * np.clip(3 - 4 * t, 0, 1)
    b = np.zeros_like(t)
    out = np.stack([r, g, b], -1)
    out[de < 2] = 0
    return out


def save(img, path):
    Image.fromarray(np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)).save(path)


def sheet(parts, path, h=320):
    tiles = []
    for p in parts:
        H, W = p.shape[:2]
        tiles.append(resize_to(p, max(1, int(W * h / H)), h))
    Image.fromarray(np.clip(np.concatenate(tiles, 1) * 255 + 0.5, 0, 255).astype(np.uint8)).save(path, quality=88)


def composite(orig, edited, target, feather, band):
    """Правка только внутри цели: C = E·m + O·(1−m); m — цель, расширенная на feather и размытая, но не дальше
    полосы допуска band (вне полосы результат ровно равен оригиналу)."""
    m = ndi.binary_dilation(target, iterations=max(1, feather)).astype(np.float32)
    m = ndi.gaussian_filter(m, sigma=max(0.5, feather / 2))
    m = np.maximum(m, target.astype(np.float32)) * ndi.binary_dilation(target, iterations=max(band, feather + 1))
    return edited * m[..., None] + orig * (1 - m[..., None])


# ---------- команды ----------
def cmd_check(a):
    O = load_rgb(a.orig); E = load_rgb(a.edited)
    info = {"tool": "edit_check.py " + VERSION, "orig": a.orig, "edited": a.edited,
            "orig_size": [O.shape[1], O.shape[0]], "edited_size": [E.shape[1], E.shape[0]]}
    h, w = O.shape[:2]
    ar_o, ar_e = w / h, E.shape[1] / E.shape[0]
    if abs(ar_o / ar_e - 1) > 0.01:
        info["error"] = "соотношение сторон изменилось — это не правка на месте; используй команду outpaint"
        print(json.dumps(info, ensure_ascii=False, indent=1)); return 2
    if E.shape[:2] != O.shape[:2]:
        E = resize_to(E, w, h); info["resized_edited"] = True
    target = load_mask(a.mask, a.mask_mode, (h, w)) if a.mask else np.zeros((h, w), bool)
    far = ~ndi.binary_dilation(target, iterations=a.band) if target.any() else np.ones((h, w), bool)
    if a.align == "shift":
        dy, dx = phase_shift(gray(O), gray(E), far.astype(np.float32))
        info["shift_px"] = [round(dy, 2), round(dx, 2)]
        if (abs(dy) > 0.25 or abs(dx) > 0.25) and abs(dy) < h / 8 and abs(dx) < w / 8:
            Es = np.stack([ndi.shift(E[..., c], (dy, dx), order=3, mode="nearest") for c in range(3)], -1)
            mse0 = float(((O - E)[far] ** 2).mean()); mse1 = float(((O - Es)[far] ** 2).mean())
            if mse1 < 0.9 * mse0:          # сдвиг принимается, только если заметно уменьшает ошибку вне цели
                E = Es; info["shift_applied"] = True
            else:
                info["shift_applied"] = False
    # глобальный дрейф цвета вне цели: E ≈ gain·O + offset по каналам (медианы, устойчиво)
    drift = {}
    Lo, Le = srgb_to_lab(O), srgb_to_lab(E)
    drift["mean_lab_orig"] = [round(float(v), 2) for v in Lo[far].mean(0)]
    drift["mean_lab_edit"] = [round(float(v), 2) for v in Le[far].mean(0)]
    drift["global_de00"] = round(float(de2000(Lo[far].mean(0)[None], Le[far].mean(0)[None])[0]), 2)
    info["global_drift"] = drift
    if a.match_color and far.any():
        gains = []
        for c in range(3):
            o, e = O[..., c][far], E[..., c][far]
            A = np.vstack([e, np.ones_like(e)]).T
            g, off = np.linalg.lstsq(A, o, rcond=None)[0]
            E[..., c] = np.clip(E[..., c] * g + off, 0, 1); gains.append([round(float(g), 4), round(float(off), 4)])
        info["color_match_gain_offset"] = gains
        Le = srgb_to_lab(E)
    de = de2000(Lo, Le)
    ss = ssim_map(gray(O), gray(E))
    res, leak = verdict_block(de, ss, target, a.band, a.thr, a.leak_max)
    info.update(res)
    info["edges_iou"] = round(edges_iou(gray(O), gray(E)), 4)
    if far.any() and not far.all():
        info["edges_iou_outside"] = round(edges_iou(gray(O) * far, gray(E) * far), 4)
    info["psnr_outside"] = round(float(10 * np.log10(1 / max(1e-12, ((O - E)[far] ** 2).mean()))), 2) if far.any() else None
    if a.protect:
        P = load_mask(a.protect, "white", (h, w))
        info["protect"] = {"ssim": round(float(ss[P].mean()), 4), "de_median": round(float(np.median(de[P])), 2),
                           "de_p95": round(float(np.percentile(de[P], 95)), 2)}
        info["protect"]["ok"] = info["protect"]["ssim"] >= 0.9 and info["protect"]["de_median"] <= 5
    out = a.out or os.path.splitext(a.edited)[0] + "_check"
    os.makedirs(out, exist_ok=True)
    save(heat(de), os.path.join(out, "diff_heat.png"))
    parts = [O, E, heat(de)]
    if a.composite and target.any():
        C = composite(O, E, target, a.feather, a.band)
        save(C, os.path.join(out, "composite.png"))
        dec = de2000(Lo, srgb_to_lab(C))
        info["composite_outside_de_max"] = round(float(dec[far].max()), 3)
        parts.append(C)
    sheet(parts, os.path.join(out, "sheet.jpg"))
    json.dump(info, open(os.path.join(out, "report.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0 if info["verdict"] == "PASS" else 1


def cmd_polarity(a):
    O = load_rgb(a.orig); E = load_rgb(a.edited)
    h, w = O.shape[:2]
    if E.shape[:2] != O.shape[:2]:
        E = resize_to(E, w, h)
    white = load_mask(a.mask, "white", (h, w))
    de = de2000(srgb_to_lab(O), srgb_to_lab(E))
    ch = de > a.thr
    fw, fb = float(ch[white].mean()) if white.any() else 0.0, float(ch[~white].mean()) if (~white).any() else 0.0
    guess = "white=edit" if fw > 3 * fb and fw > 0.1 else ("black=edit" if fb > 3 * fw and fb > 0.1 else "неясно (менялось всё или ничего)")
    info = {"changed_frac_in_white": round(fw, 4), "changed_frac_in_black": round(fb, 4), "polarity_guess": guess}
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0


def locate(O, X):
    """Найти O внутри X: масштаб по высоте или ширине ± 4 %, сдвиг — нормированная корреляция на уменьшенных."""
    ho, wo = O.shape[:2]; hx, wx = X.shape[:2]
    k = 256 / max(hx, wx)
    Xs = gray(resize_to(X, max(8, int(wx * k)), max(8, int(hx * k))))
    best = None
    for base in sorted({hx / ho, wx / wo}):
        for f in np.linspace(0.96, 1.04, 9):
            s = base * f
            tw, th = int(round(wo * s * k)), int(round(ho * s * k))
            if tw > Xs.shape[1] or th > Xs.shape[0] or tw < 8 or th < 8:
                continue
            T = gray(resize_to(O, tw, th))
            T = (T - T.mean()) / (T.std() + 1e-6)
            # корреляция скользящим окном через FFT
            F = np.fft.rfft2(Xs); G = np.fft.rfft2(T[::-1, ::-1], Xs.shape)
            cc = np.fft.irfft2(F * G, Xs.shape)[th - 1:, tw - 1:]
            S1 = ndi.uniform_filter(Xs, (th, tw), mode="constant")
            S2 = ndi.uniform_filter(Xs * Xs, (th, tw), mode="constant")
            # окно с центром → левый верхний угол
            cy0, cx0 = th // 2, tw // 2
            mu = S1[cy0:cy0 + cc.shape[0], cx0:cx0 + cc.shape[1]]
            var = S2[cy0:cy0 + cc.shape[0], cx0:cx0 + cc.shape[1]] - mu ** 2
            ncc = cc / (np.sqrt(np.maximum(var, 1e-9)) * th * tw)
            ncc = ncc[:mu.shape[0], :mu.shape[1]]
            iy, ix = np.unravel_index(np.argmax(ncc), ncc.shape)
            v = float(ncc[iy, ix])
            if best is None or v > best[0]:
                best = (v, s, iy / k, ix / k)
    return best


def edge_sharpness(Os, reg, q=0.98):
    """Отношение среднего модуля Собеля правки к исходнику на сильных краях исходника (верхние 2 %). Требует совмещения
    ≤ 0,5 px. Эталон: без размытия 0,96–0,99; размытие 1 px ≈ 0,9; 1,5 px ≈ 0,82; 2 px ≈ 0,75."""
    go, gr = gray(Os), gray(reg)
    mo = np.hypot(ndi.sobel(go, 0), ndi.sobel(go, 1)); mr = np.hypot(ndi.sobel(gr, 0), ndi.sobel(gr, 1))
    strong = mo > np.quantile(mo, q)
    return float(mr[strong].mean() / max(float(mo[strong].mean()), 1e-6))


def refine_place(O, X, s, y0, x0, span=0.015, step=0.0025, fine=0.0005, max_t=24):
    """Уточнить масштаб s и положение (y0, x0) исходника O в X: перебор масштаба, для каждого — фазовая корреляция
    (целый сдвиг + субпиксельный остаток), критерий — MSE центральной области. Возвращает (s, y0, x0, sdy, sdx, mse),
    где ndi.shift(область X, (sdy, sdx)) ≈ исходник, уменьшенный до масштаба s."""
    ho, wo = O.shape[:2]; H, W = X.shape[:2]

    def trial(sc):
        tw, th = int(round(wo * sc)), int(round(ho * sc))
        if tw > W or th > H or tw < 16 or th < 16:
            return None
        yy = min(max(0, y0), H - th); xx = min(max(0, x0), W - tw)
        go = gray(resize_to(O, tw, th))
        dy, dx = phase_shift(go, gray(X[yy:yy + th, xx:xx + tw]))
        if abs(dy) > max_t or abs(dx) > max_t:
            dy = dx = 0.0
        yy = min(max(0, yy - int(round(dy))), H - th); xx = min(max(0, xx - int(round(dx))), W - tw)
        gr = gray(X[yy:yy + th, xx:xx + tw])
        sdy, sdx = phase_shift(go, gr)
        if abs(sdy) > 1.5 or abs(sdx) > 1.5:
            sdy = sdx = 0.0
        ga = ndi.shift(gr, (sdy, sdx), order=1, mode="nearest")
        b = max(2, int(0.1 * min(th, tw)))
        return float(((go - ga)[b:-b, b:-b] ** 2).mean()), sc, yy, xx, sdy, sdx

    cand = [r for r in (trial(sc) for sc in s * (1 + np.arange(-span, span + 1e-9, step))) if r]
    if not cand:
        return s, y0, x0, 0.0, 0.0, None
    best = min(cand)
    cand = [r for r in (trial(sc) for sc in best[1] * (1 + np.arange(-step, step + 1e-9, fine))) if r] + [best]
    mse, sc, yy, xx, sdy, sdx = min(cand)
    return sc, yy, xx, sdy, sdx, mse


def cmd_outpaint(a):
    O = load_rgb(a.orig); X = load_rgb(a.extended)
    v, s0, y0, x0 = locate(O, X)
    ho, wo = O.shape[:2]
    s, y0, x0, sdy, sdx, _ = refine_place(O, X, s0, int(round(y0)), int(round(x0)))
    tw, th = int(round(wo * s)), int(round(ho * s))
    Os = resize_to(O, tw, th)
    reg = X[y0:y0 + th, x0:x0 + tw]
    reg = np.stack([ndi.shift(reg[..., c], (sdy, sdx), order=1, mode="nearest") for c in range(3)], -1)
    ss = ssim_map(gray(Os), gray(reg))
    de = de2000(srgb_to_lab(Os), srgb_to_lab(reg))
    b = max(2, int(0.1 * min(th, tw)))
    center = np.zeros((th, tw), bool); center[b:-b, b:-b] = True
    info = {"tool": "edit_check.py " + VERSION, "orig_size": [wo, ho], "extended_size": [X.shape[1], X.shape[0]],
            "ncc": round(v, 3), "scale_coarse": round(s0, 4), "scale": round(s, 5), "place_xywh": [x0, y0, tw, th],
            "subpixel_shift": [round(sdy, 2), round(sdx, 2)],
            "ssim_orig_region": round(float(ss.mean()), 4), "ssim_center": round(float(ss[center].mean()), 4),
            "de_median_orig_region": round(float(np.median(de)), 2), "de_p95_orig_region": round(float(np.percentile(de, 95)), 2)}
    def hfstd(g):
        return float((g - ndi.uniform_filter(g, 3)).std())
    info["detail_ratio"] = round(hfstd(gray(reg)) / max(hfstd(gray(Os)), 1e-6), 3)   # справочно: раздувается шумом/JPEG
    info["edge_sharpness"] = round(edge_sharpness(Os, reg), 3)
    # перерисовка = упал SSIM, ИЛИ сдвинулся цвет (ΔE00 медиана > 3), ИЛИ размылись сильные края (< 0.85 от исходника)
    info["verdict"] = ("PASS" if info["ssim_center"] >= 0.9 and info["de_median_orig_region"] <= 3 and info["edge_sharpness"] >= 0.85
                       else "REGENERATED")
    out = a.out or os.path.splitext(a.extended)[0] + "_check"
    os.makedirs(out, exist_ok=True)
    parts = [X]
    if a.composite:
        C = X.copy()
        m = np.zeros(X.shape[:2], np.float32); f = max(1, a.feather)
        m[y0 + f:y0 + th - f, x0 + f:x0 + tw - f] = 1
        m = ndi.gaussian_filter(m, f / 2)[..., None]
        Osx = np.stack([ndi.shift(Os[..., c], (-sdy, -sdx), order=3, mode="nearest") for c in range(3)], -1)
        full = np.zeros_like(X); full[y0:y0 + th, x0:x0 + tw] = np.clip(Osx, 0, 1)
        C = full * m + X * (1 - m)
        save(C, os.path.join(out, "composite.png")); parts.append(C)
    hm = np.zeros_like(X); hm[y0:y0 + th, x0:x0 + tw] = heat(de); parts.insert(1, hm)
    sheet(parts, os.path.join(out, "sheet.jpg"))
    json.dump(info, open(os.path.join(out, "report.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0 if info["verdict"] == "PASS" else 1


def cmd_selftest(a):
    import tempfile, io
    rng = np.random.default_rng(1)
    h, w = 240, 320
    y, x = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    O = np.stack([0.2 + 0.6 * x, 0.3 + 0.4 * y, 0.5 + 0.3 * np.sin(6 * x)], -1)
    O += 0.05 * rng.standard_normal((h, w, 1)); O[60:120, 200:260] = [0.9, 0.2, 0.2]   # «объект»
    O = np.clip(O, 0, 1)
    d = tempfile.mkdtemp(prefix="editcheck_")
    save(O, os.path.join(d, "o.png"))
    mask = np.zeros((h, w), bool); mask[50:130, 190:270] = True
    save(np.repeat(mask[..., None], 3, -1).astype(np.float32), os.path.join(d, "m.png"))
    # правка 1: объект перекрашен внутри маски + сдвиг 2 px + JPEG q90 + яркость +2 % (как у моделей) — PASS после совмещения
    E = O.copy(); E[60:120, 200:260] = [0.2, 0.3, 0.9]
    E = np.clip(np.stack([ndi.shift(E[..., c], (2, -1), order=1, mode="nearest") for c in range(3)], -1) * 1.02, 0, 1)
    buf = io.BytesIO(); Image.fromarray((E * 255).astype(np.uint8)).save(buf, "JPEG", quality=90)
    open(os.path.join(d, "e1.jpg"), "wb").write(buf.getvalue())
    # правка 2: то же + «утечка» — пятно вне маски
    E2 = E.copy(); E2[150:220, 20:120] *= 0.6
    save(E2, os.path.join(d, "e2.png"))
    rc = []
    for e, exp in (("e1.jpg", 0), ("e2.png", 1)):
        ns = argparse.Namespace(orig=os.path.join(d, "o.png"), edited=os.path.join(d, e), mask=os.path.join(d, "m.png"),
                                mask_mode="white", protect=None, band=6, thr=5.0, out=os.path.join(d, e + "_chk"),
                                composite=True, feather=4, match_color=False, align="shift", leak_max=0.02)
        r = cmd_check(ns)
        rc.append(r == exp)
    rep = json.load(open(os.path.join(d, "e1.jpg_chk", "report.json")))
    ok_shift = abs(rep["shift_px"][0] + 2) < 0.6 and abs(rep["shift_px"][1] - 1) < 0.6
    print("SELFTEST", "OK" if all(rc) and ok_shift else "FAIL", {"verdicts_as_expected": rc, "shift_detected": rep["shift_px"], "dir": d})
    return 0 if all(rc) and ok_shift else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("check"); c.add_argument("orig"); c.add_argument("edited")
    c.add_argument("--mask"); c.add_argument("--mask-mode", default="white", choices=["white", "black", "alpha"])
    c.add_argument("--protect"); c.add_argument("--band", type=int, default=6)
    c.add_argument("--thr", type=float, default=5.0); c.add_argument("--out")
    c.add_argument("--composite", action="store_true"); c.add_argument("--feather", type=int, default=4)
    c.add_argument("--match-color", action="store_true"); c.add_argument("--align", default="shift", choices=["shift", "none"])
    c.add_argument("--leak-max", type=float, default=0.02)
    p = sp.add_parser("polarity"); p.add_argument("orig"); p.add_argument("edited"); p.add_argument("mask")
    p.add_argument("--thr", type=float, default=5.0)
    o = sp.add_parser("outpaint"); o.add_argument("orig"); o.add_argument("extended"); o.add_argument("--out")
    o.add_argument("--composite", action="store_true"); o.add_argument("--feather", type=int, default=6)
    sp.add_parser("selftest")
    a = ap.parse_args()
    sys.exit({"check": cmd_check, "polarity": cmd_polarity, "outpaint": cmd_outpaint, "selftest": cmd_selftest}[a.cmd](a))


if __name__ == "__main__":
    main()
