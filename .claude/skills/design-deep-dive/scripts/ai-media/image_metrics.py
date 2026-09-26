#!/usr/bin/env python3
"""Опыт A/04: простые метрики маркеров «сгенерированности» (IMG-M01, M03, M04, M05, M17) на картинках живых сайтов.

python3 image_metrics.py images.tsv out.json [--keep]
images.tsv: group<TAB>slug<TAB>url<TAB>заметка. Картинка скачивается во временную папку tmp/ (публичный файл, только для замера,
не публикуется), приводится к sRGB и к 1024 px по длинной стороне (LANCZOS), считаются метрики, файл удаляется.

Метрики (все на кадре ≤ 1024 px):
  colorfulness  — Hasler & Süsstrunk 2003: sqrt(σ_rg²+σ_yb²) + 0.3·sqrt(μ_rg²+μ_yb²), rg=R−G, yb=0.5(R+G)−B (0–255);
  sat_share     — доля пикселей с HSV S > 0.7 и V > 0.35;
  clip_hi/lo    — доля пикселей с max(R,G,B) ≥ 250 / с яркостью ≤ 5 (пересвет и провал);
  warm_b        — средний b* (CIELAB, D65) почти нейтральных светлых пикселей (C*ab < 10, L* > 60); neutral_share — их доля;
  purple_share  — доля хроматических пикселей (OKLCH C > 0.06) с оттенком 270–320°;
  chroma_med    — медиана хромы OKLCH по кадру;
  hdr_index     — средний |L − blur16(L)| / σ(L) (L — яркость CIELAB): растёт у «HDR»/локально-контрастной обработки;
  lap_var       — дисперсия лапласиана яркости (0–1) ×1000: резкость/микрофактура (зависит от сюжета!);
  lum_range     — разница перцентилей 99 и 1 яркости L*.
Это описательные метрики для калибровки порогов; классификатором «ИИ / не ИИ» они не являются.
"""
import io, json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageCms

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"


def load(path):
    im = Image.open(path)
    try:
        icc = im.info.get("icc_profile")
        if icc:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc)); dst = ImageCms.createProfile("sRGB")
            im = ImageCms.profileToProfile(im, src, dst, outputMode="RGB")
    except Exception:
        pass
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
    im = im.convert("RGB")
    s = 1024 / max(im.size)
    if s < 1:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def srgb_to_linear(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lab(rgb):
    lin = srgb_to_linear(rgb)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ M.T
    xyz /= np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    L = 116 * f[..., 1] - 16; a = 500 * (f[..., 0] - f[..., 1]); b = 200 * (f[..., 1] - f[..., 2])
    return L, a, b


def oklab(rgb):
    lin = srgb_to_linear(rgb)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    lms = np.cbrt(np.clip(lin @ M1.T, 0, None))
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    o = lms @ M2.T
    return o[..., 0], o[..., 1], o[..., 2]


def metrics(rgb):
    from scipy.ndimage import gaussian_filter, laplace
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    rg = R - G; yb = 0.5 * (R + G) - B
    colorful = float(np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2))
    mx = rgb.max(axis=2); mn = rgb.min(axis=2)
    S = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0); V = mx / 255
    L, a, b = lab(rgb)
    C = np.sqrt(a * a + b * b)
    neut = (C < 10) & (L > 60)
    ol, oa, ob = oklab(rgb)
    oc = np.sqrt(oa * oa + ob * ob); oh = (np.degrees(np.arctan2(ob, oa)) + 360) % 360
    chrom = oc > 0.06
    Ln = L / 100.0
    hdr = float(np.abs(Ln - gaussian_filter(Ln, 16)).mean() / max(Ln.std(), 1e-6))
    gray = (0.2126 * R + 0.7152 * G + 0.0722 * B) / 255
    return {"w": int(rgb.shape[1]), "h": int(rgb.shape[0]), "colorfulness": round(colorful, 1), "sat_share": round(float(((S > 0.7) & (V > 0.35)).mean()), 4),
            "clip_hi": round(float((mx >= 250).mean()), 4), "clip_lo": round(float((L <= 5).mean()), 4),
            "warm_b": round(float(b[neut].mean()), 2) if neut.mean() > 0.02 else None, "neutral_share": round(float(neut.mean()), 3),
            "purple_share": round(float(((oh >= 270) & (oh <= 320) & chrom).sum() / max(1, chrom.sum())), 3), "chroma_med": round(float(np.median(oc)), 4),
            "hdr_index": round(hdr, 3), "lap_var": round(float(laplace(gray).var() * 1000), 3), "lum_range": round(float(np.percentile(L, 99) - np.percentile(L, 1)), 1)}


def main():
    a = sys.argv[1:]
    lst, out = a[0], a[1]
    tmp = os.path.join(HERE, "tmp"); os.makedirs(tmp, exist_ok=True)
    res = []
    for i, line in enumerate(open(lst)):
        if not line.strip() or line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        grp, slug, url, note = p[0], p[1], p[2], (p[3] if len(p) > 3 else "")
        fn = os.path.join(tmp, f"{i:03d}")
        subprocess.run(["curl", "-sL", "-A", UA, "-H", "Accept: image/avif,image/webp,image/*;q=0.8", "--max-time", "60", "-o", fn, url], capture_output=True, timeout=90)
        item = {"group": grp, "slug": slug, "url": url[:300], "note": note}
        try:
            item.update(metrics(load(fn)))
            item["bytes"] = os.path.getsize(fn)
        except Exception as e:
            item["error"] = str(e)[:160]
        res.append(item)
        print(json.dumps(item, ensure_ascii=False)[:400], flush=True)
        if "--keep" not in a and os.path.exists(fn):
            os.remove(fn)
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
