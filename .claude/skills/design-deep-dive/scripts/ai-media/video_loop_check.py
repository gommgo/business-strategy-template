#!/usr/bin/env python3
"""video_loop_check.py — приёмка ИИ-видео для сайта: шов петли, «живость», мёртвые концы, склейки, дрейф неподвижных
зон и камеры, однородность хромакея, стык клипов цепочки, контактный лист (агент I, волна 2, 23.09.2026).

Python 3.13 + numpy + scipy + Pillow (системные) + ffmpeg/ffprobe 7.1.5; ΔE00, SSIM и фазовая корреляция — из
edit_check.py агента H (та же папка). OpenCV не нужен. Вход VIDEO — видеофайл или папка кадров (PNG/JPG по имени).

Команды:
  loop   VIDEO [--control VIDEO] [--width 320] [--dead 0.25]
         seam_ratio = MAD(последний, первый) / motion_med; motion_med («живость») = медиана MAD соседних кадров (0–255,
         серый, 320 px); cut_ratio = max MAD / motion_med (склейка > 10); static_frac = доля пар с MAD < 0,5;
         head/tail_motion = медиана MAD первой/последней четверти к motion_med (угасание < 0,5); dead_start/dead_end —
         подряд идущие «мёртвые» пары на концах (MAD < dead × motion_med); dup_last — последний кадр дублирует первый
         (seam_ratio < dead); trim — сколько кадров срезать и seam_ratio после среза; best_cut — лучшая точка реза в
         последних 40 % (для i2v без второго кадра); cam_shift_max_px — глобальный сдвиг к кадру 0 (фазовая
         корреляция, пиксели исходника); seam_dE00 — ΔE00 среднего цвета последнего и первого кадра; color_drift_dE00 —
         максимум ΔE00 среднего цвета к кадру 0. С --control: motion_vs_control и curve_corr (хореография).
  trim   VIDEO OUT [--start K] [--end K] [--auto]   срез кадров на концах (auto — по loop), без звука, мезонин БЕЗ ПОТЕРЬ
         x264 -qp 0 в пиксельном формате исходника (не из списка x264 — 4:4:4), +faststart — на нём меряют шов и с него
         кодируют финал (X2, 24.09.2026: CRF 10 давал ложный шов чистой петли 0,96 → 2,12, K/03); ffmpeg
         trim=start_frame:end_frame (end — исключительно) и -r <fps>: без него MP4 после setpts теряет последний кадр
         (edit list); ok — число кадров сошлось. Размер: ≈ 10–40 МБ на 5 с 1080p — промежуточный файл, в поставку не идёт.
  drift  VIDEO --mask MASK.png [--width 320]   неподвижные зоны (белое в маске): MAD к кадру 0 по времени, максимум и
         медиана; сдвиг камеры по маске; dE00_max/dE00_last — ΔE00 среднего цвета зоны к кадру 0 (дрейф цвета, I-18).
         Для синемаграфа: цель — drift_max < 1,0 (шум кодека), cam_shift < 1 px, dE00_max < 2.
  chroma VIDEO [--key '#00B140'|auto] [--de 5]   фон = пиксели, близкие к ключу (ΔE00 < 25) и связанные с краем кадра;
         доля фона с ΔE00 ≤ de к ключу (bg_ok_min по кадрам), σ фона, дрейф центра объекта (% ширины), масштаб (площадь).
  join   A B   стык клипов цепочки: MAD и seam_ratio стыка к живости обоих, SSIM, ΔE00 среднего цвета, отношение темпа.
  sheet  VIDEO OUT.jpg [--n 12] [--cols 4]   контактный лист: N кадров равномерно + полоса «последний | первый | |Δ|×4».
  colormatch SRC REF OUT [--mask M]   перенос среднего и σ в OKLab (Рейнхард) от REF к SRC по белой зоне маски
         (неизменные зоны) — подгонка правленого конечного кадра FLF к начальному (W3-7, тест I-18).
  selftest   синтетика с известным ответом (идеальная петля, дубль, разрыв, угасание, склейка, сдвиг камеры).
Выход — JSON в stdout. [проверено: 99-raw/experiments/I/02-loop-seam, 03-chroma-key]
"""
import argparse, glob, json, os, subprocess, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_check import srgb_to_lab, de2000, ssim_map, phase_shift  # noqa: E402  (агент H)

VERSION = "0.2.1 (2026-09-24, X2: trim — мезонин без потерь)"
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")


# ---------- чтение кадров ----------
def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
                       capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    a = [s.get("codec_name") for s in j.get("streams", []) if s.get("codec_type") == "audio"]
    fmt = j.get("format", {})

    def fr(x):
        try:
            n, d = x.split("/"); return round(float(n) / float(d), 3) if float(d) else None
        except Exception:
            return None
    return {"codec": v.get("codec_name"), "profile": v.get("profile"), "pix_fmt": v.get("pix_fmt"), "w": v.get("width"),
            "r_frame_rate": v.get("r_frame_rate"),
            "h": v.get("height"), "fps": fr(v.get("avg_frame_rate", "0/1")), "duration_s": float(fmt.get("duration", 0) or 0),
            "size_kb": round(int(fmt.get("size", 0) or 0) / 1024, 1), "kbps": round(int(fmt.get("bit_rate", 0) or 0) / 1000),
            "audio": a, "container": fmt.get("format_name")}


def frame_files(src):
    return sorted(f for f in glob.glob(os.path.join(src, "*")) if f.lower().endswith(IMG_EXT))


def load(src, width=320, mode="gray"):
    """Кадры (n, h, w[, 3]) float32 0–255, уменьшенные до width по ширине (area). mode: gray | rgb."""
    if os.path.isdir(src):
        out = []
        for f in frame_files(src):
            im = Image.open(f).convert("RGB")
            h = int(round(im.height * width / im.width / 2) * 2)
            im = im.resize((width, h), Image.BOX)
            a = np.asarray(im, dtype=np.float32)
            out.append(a @ np.array([0.2126, 0.7152, 0.0722], np.float32) if mode == "gray" else a)
        return np.stack(out)
    p = probe(src)
    h = int(round(p["h"] * width / p["w"] / 2) * 2)
    pf, ch = ("gray", 1) if mode == "gray" else ("rgb24", 3)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-threads", "4", "-i", src, "-vf", f"scale={width}:{h}:flags=area,format={pf}",
                          "-f", "rawvideo", "-pix_fmt", pf, "-"], capture_output=True).stdout
    n = len(raw) // (width * h * ch)
    a = np.frombuffer(raw[: n * width * h * ch], np.uint8).astype(np.float32)
    return a.reshape((n, h, width) if ch == 1 else (n, h, width, 3))


def src_width(src):
    if os.path.isdir(src):
        return Image.open(frame_files(src)[0]).width
    return probe(src)["w"]


def mad(a, b):
    return float(np.abs(a - b).mean())


def ssim(a, b):
    return float(ssim_map(a / 255.0, b / 255.0).mean())


def mean_lab(rgb):
    return srgb_to_lab((rgb.reshape(-1, 3).mean(0) / 255.0)[None, :])[0]


def dE(lab1, lab2):
    return float(de2000(np.asarray(lab1)[None, :], np.asarray(lab2)[None, :])[0])


# ---------- метрики петли ----------
def loop_metrics(fr, dead=0.25, rgb=None, scale=1.0, max_trim=3, k=3, win=6):
    n = len(fr)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    med = float(np.median(d)) if len(d) else 0.0
    eps = max(med, 1e-6)
    seam = mad(fr[-1], fr[0])
    q = max(2, len(d) // 4)
    ds = 0
    while ds < len(d) and d[ds] < dead * eps:
        ds += 1
    de_ = 0
    while de_ < len(d) and d[len(d) - 1 - de_] < dead * eps:
        de_ += 1
    dup = seam < dead * eps
    # срез: мёртвые пары на концах + дубль последнего кадра (FLF [A,A]); длинный мёртвый конец — не дубль, а угасание
    collapse = ds > max_trim or de_ > max_trim
    cut_s = ds if ds <= max_trim else 0
    cut_e = (de_ if de_ <= max_trim else 0) + (1 if dup else 0)
    f2 = fr[cut_s: n - cut_e] if n - cut_e - cut_s >= 3 else fr
    d2 = np.abs(np.diff(f2, axis=0)).mean(axis=(1, 2))
    med2 = max(float(np.median(d2)), 1e-6)

    def local(seam_mad, dd):
        """Шов к k парам у каждого конца: движение бывает неравномерным (оборот: этикетка видна часть цикла)."""
        nb = np.concatenate([dd[:k], dd[-k:]]) if len(dd) >= 2 * k else dd
        return seam_mad / max(float(np.median(nb)) if len(nb) else 0.0, 1e-6)
    # склейка — локальный пик: пара к медиане соседей в окне ±win (пол знаменателя — 0,25·медианы и 0,05 уровня)
    loc = []
    for i in range(len(d)):
        nb = np.concatenate([d[max(0, i - win):i], d[i + 1:i + 1 + win]])
        loc.append(d[i] / max(float(np.median(nb)) if len(nb) else 0.0, 0.25 * eps, 0.05))
    # пинг-понг (бумеранг): кадры симметричны во времени вокруг какого-то центра c — MAD(f[c+i], f[c−i]) ≈ 0
    th = fr[:, ::4, ::4]
    mir, mc = None, None
    if n >= 8 and med > 0.02:
        span = range(1, max(2, n // 4))
        eth = max(float(np.median(np.abs(np.diff(th, axis=0)).mean(axis=(1, 2)))), 1e-6)
        for c in range(n):
            sp = float(np.median([np.abs(th[(c + i) % n] - th[c]).mean() for i in span]))   # размах движения вокруг c
            if sp < 2 * eth:                                                             # неподвижный участок — не судим
                continue
            v = float(np.median([np.abs(th[(c + i) % n] - th[(c - i) % n]).mean() for i in span])) / sp
            if mir is None or v < mir:
                mir, mc = v, c
    # лучшая точка реза (для i2v без второго кадра): кадр в последних 40 %, ближайший к кадру 0
    t0 = int(n * 0.6)
    tail = [mad(fr[i], fr[0]) for i in range(t0, n)]
    bi = int(np.argmin(tail)) + t0 if tail else n - 1
    # сдвиг камеры к кадру 0 (фазовая корреляция по всему кадру; для синемаграфа — drift с маской)
    step = max(1, n // 24)
    shifts = [phase_shift(fr[0], fr[i]) for i in range(step, n, step)]
    cam = max((float(np.hypot(*s)) for s in shifts), default=0.0) * scale
    res = {"n": n, "motion_med": round(med, 3), "seam_mad": round(seam, 3), "seam_ratio": round(seam / eps, 2),
           "seam_ratio_local": round(local(seam, d), 2),
           "cut_ratio": round(float(max(loc)), 2) if len(d) else None, "cut_at": int(np.argmax(loc)) + 1 if len(d) else None,
           "cut_ratio_global": round(float(d.max()) / eps, 2) if len(d) else None,
           "static_frac": round(float((d < dead * eps).mean()), 3) if len(d) else None,
           "static_abs_frac": round(float((d < 0.5).mean()), 3) if len(d) else None,
           "head_motion": round(float(np.median(d[:q])) / eps, 2), "tail_motion": round(float(np.median(d[-q:])) / eps, 2),
           "ssim_seam": round(ssim(fr[-1], fr[0]), 4), "ssim_typ": round(float(np.median([ssim(fr[i], fr[i + 1]) for i in range(0, n - 1, step)])), 4),
           "dead_start": ds, "dead_end": de_, "dup_last": bool(dup), "collapse_suspect": bool(collapse),
           "trim": {"start": cut_s, "end": cut_e, "seam_ratio_after": round(mad(f2[-1], f2[0]) / med2, 2),
                    "seam_ratio_local_after": round(local(mad(f2[-1], f2[0]), d2), 2), "n_after": len(f2)},
           "best_cut": {"frame": bi, "seam_ratio": round(mad(fr[bi - 1], fr[0]) / eps, 2) if bi > 0 else None},
           "mirror_ratio": round(mir, 3) if mir is not None else None, "mirror_center": mc,
           "pingpong_suspect": bool(mir is not None and mir < dead),
           "cam_shift_max_px": round(cam, 2)}
    if rgb is not None:
        labs = [mean_lab(x) for x in rgb]
        res["seam_dE00"] = round(dE(labs[-1], labs[0]), 2)
        res["color_drift_dE00"] = round(max(dE(l, labs[0]) for l in labs), 2)
    res["_curve"] = d
    return res


def verdict(m):
    """Шов — по локальному отношению после среза (при равномерном движении оно ≈ глобальному seam_ratio A/02 и C2)."""
    v = {"seam": m["trim"]["seam_ratio_local_after"] <= 1.5, "no_cut": (m["cut_ratio"] or 0) < 10,
         "alive_head": m["head_motion"] >= 0.5, "alive_tail": m["tail_motion"] >= 0.5,
         "not_static": (m["static_frac"] or 0) <= 0.3 and not m["collapse_suspect"]}
    if "motion_vs_control" in m:
        v["alive_vs_control"] = m["motion_vs_control"] >= 0.5
    return v


def cmd_loop(a):
    fr = load(a.video, a.width)
    rgb = load(a.video, 96, "rgb")
    m = loop_metrics(fr, a.dead, rgb, src_width(a.video) / a.width)
    if a.control:
        c = load(a.control, a.width)
        cm = loop_metrics(c, a.dead)
        m["control_motion_med"] = cm["motion_med"]
        m["motion_vs_control"] = round(m["motion_med"] / max(cm["motion_med"], 1e-6), 2)
        x, y = m["_curve"], cm["_curve"]
        k = min(len(x), len(y))
        xi = np.interp(np.linspace(0, 1, k), np.linspace(0, 1, len(x)), x)
        yi = np.interp(np.linspace(0, 1, k), np.linspace(0, 1, len(y)), y)
        m["curve_corr"] = round(float(np.corrcoef(xi, yi)[0, 1]), 3) if xi.std() > 0 and yi.std() > 0 else None
    m.pop("_curve")
    m["verdict"] = verdict(m)
    if not os.path.isdir(a.video):
        m["probe"] = probe(a.video)
    print(json.dumps(m, ensure_ascii=False))
    return m


X264_LOSSLESS_PIX = {"yuv420p", "yuvj420p", "yuv422p", "yuvj422p", "yuv444p", "yuvj444p", "yuv420p10le", "yuv422p10le",
                     "yuv444p10le", "gray", "gray10le"}


def cmd_trim(a):
    s, e = a.start, a.end
    if a.auto:
        m = loop_metrics(load(a.video, 320))
        s, e = m["trim"]["start"], m["trim"]["end"]
    n = len(load(a.video, 64))
    vf = f"trim=start_frame={s}:end_frame={n - e},setpts=PTS-STARTPTS"
    # -r обязателен: после setpts у последнего кадра нет длительности и MP4-мультиплексор отрезает его списком
    # правки (edit list) — 145 кадров → 144 (ffmpeg 7.1.5, проверено в I/02); для петли это лишний шаг на стыке
    pr = probe(a.video) if not os.path.isdir(a.video) else {}
    fr = pr.get("r_frame_rate") or "24/1"
    # X2 24.09.2026: мезонин без потерь (x264 -qp 0, как K/03). CRF 10 давал пульс ключевого кадра: чистая петля K/03 c08
    # после trim — шов 2,12 вместо 0,96 и вердикт «шов провален»; формат исходника сохраняется (4:2:0 → 4:2:0 без пересчёта
    # цветности, 10 бит → 10 бит), кадры вне списка x264 (RGB и т. п.) — 4:4:4.
    pix = pr.get("pix_fmt") if pr.get("pix_fmt") in X264_LOSSLESS_PIX else "yuv444p"
    cmd = ["ffmpeg", "-v", "error", "-y", "-threads", "4", "-i", a.video, "-vf", vf, "-an", "-c:v", "libx264", "-qp", "0",
           "-preset", "medium", "-pix_fmt", pix, "-r", fr, "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    n_out = len(load(a.out, 64))
    out = {"n_in": n, "cut_start": s, "cut_end": e, "n_out": n_out, "n_expected": n - s - e, "ok": n_out == n - s - e, "vf": vf,
           "mezzanine": f"x264 -qp 0 {pix}"}
    print(json.dumps(out, ensure_ascii=False))


def cmd_drift(a):
    fr = load(a.video, a.width)
    m = Image.open(a.mask).convert("L").resize((fr.shape[2], fr.shape[1]), Image.BILINEAR)
    mask = np.asarray(m, np.float32) / 255.0 > 0.5
    mask = ndi.binary_erosion(mask, iterations=2)  # без края маски
    dd = [float(np.abs(f - fr[0])[mask].mean()) for f in fr]
    step = max(1, len(fr) // 24)
    sh = [phase_shift(fr[0], fr[i], weight=mask.astype(np.float32)) for i in range(step, len(fr), step)]
    sc = src_width(a.video) / a.width
    # цвет неподвижных зон: ΔE00 среднего цвета маски к кадру 0 (правленый конечный кадр FLF «плывёт» цветом — I-18)
    rgb = load(a.video, 160, "rgb")
    mc = np.asarray(m.resize((rgb.shape[2], rgb.shape[1]), Image.BILINEAR), np.float32) / 255.0 > 0.5
    mc = ndi.binary_erosion(mc, iterations=1)
    labs = [srgb_to_lab((f[mc].mean(0) / 255.0)[None, :])[0] for f in rgb]
    dcol = [dE(l, labs[0]) for l in labs]
    print(json.dumps({"n": len(fr), "static_area": round(float(mask.mean()), 3), "drift_max": round(max(dd), 3),
                      "drift_med": round(float(np.median(dd)), 3), "drift_last": round(dd[-1], 3),
                      "cam_shift_max_px": round(max((float(np.hypot(*s)) for s in sh), default=0.0) * sc, 2),
                      "dE00_max": round(max(dcol), 2), "dE00_last": round(dcol[-1], 2)}, ensure_ascii=False))


def parse_hex(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def cmd_chroma(a):
    fr = load(a.video, a.width, "rgb")
    n, h, w, _ = fr.shape
    if a.key == "auto":
        ring = np.concatenate([fr[0, :4].reshape(-1, 3), fr[0, -4:].reshape(-1, 3), fr[0, :, :4].reshape(-1, 3), fr[0, :, -4:].reshape(-1, 3)])
        key = np.median(ring, 0)
    else:
        key = parse_hex(a.key)
    klab = srgb_to_lab(key / 255.0)
    rows, c0, area0 = [], None, None
    for f in fr:
        de = de2000(srgb_to_lab(f / 255.0), klab[None, None, :])
        near = de < 25
        lab_, _ = ndi.label(near)
        border = np.unique(np.concatenate([lab_[0], lab_[-1], lab_[:, 0], lab_[:, -1]]))
        bg = np.isin(lab_, border[border > 0])
        obj = ~bg
        ok = float((de[bg] <= a.de).mean()) if bg.any() else 0.0
        yx = np.argwhere(obj)
        c = yx.mean(0) if len(yx) else np.array([h / 2, w / 2])
        area = float(obj.mean())
        if c0 is None:
            c0, area0 = c, max(area, 1e-6)
        rows.append({"bg_ok": ok, "bg_de_mean": float(de[bg].mean()) if bg.any() else None,
                     "bg_sigma": float(f[bg].std(0).mean()) if bg.any() else None,
                     "drift_pct_w": float(np.hypot(*(c - c0)) / w * 100), "area_ratio": area / area0})
    out = {"n": n, "key": "#%02X%02X%02X" % tuple(int(x) for x in key), "de_thr": a.de,
           "bg_ok_min": round(min(r["bg_ok"] for r in rows), 4), "bg_ok_med": round(float(np.median([r["bg_ok"] for r in rows])), 4),
           "bg_de_mean_max": round(max(r["bg_de_mean"] or 0 for r in rows), 2), "bg_sigma_max": round(max(r["bg_sigma"] or 0 for r in rows), 2),
           "obj_drift_max_pct_w": round(max(r["drift_pct_w"] for r in rows), 2),
           "obj_area_ratio_range": [round(min(r["area_ratio"] for r in rows), 3), round(max(r["area_ratio"] for r in rows), 3)]}
    out["verdict"] = {"bg_uniform": out["bg_ok_min"] >= 0.95, "obj_still": out["obj_drift_max_pct_w"] <= 2.0}
    print(json.dumps(out, ensure_ascii=False))


def cmd_join(a):
    A, B = load(a.a, 320), load(a.b, 320)
    Ar, Br = load(a.a, 96, "rgb"), load(a.b, 96, "rgb")
    ma, mb = [float(np.median(np.abs(np.diff(x, axis=0)).mean(axis=(1, 2)))) for x in (A, B)]
    j = mad(A[-1], B[0])
    print(json.dumps({"join_mad": round(j, 3), "join_ratio": round(j / max((ma + mb) / 2, 1e-6), 2), "ssim_join": round(ssim(A[-1], B[0]), 4),
                      "dE00_join": round(dE(mean_lab(Ar[-1]), mean_lab(Br[0])), 2), "tempo_B_to_A": round(mb / max(ma, 1e-6), 2),
                      "motion_med": [round(ma, 3), round(mb, 3)]}, ensure_ascii=False))


def cmd_sheet(a):
    fr = load(a.video, 320, "rgb")
    n = len(fr)
    idx = np.linspace(0, n - 1, min(a.n, n)).round().astype(int)
    h, w = fr.shape[1:3]
    rows = int(np.ceil(len(idx) / a.cols))
    W = w * a.cols
    seam_h = h
    canvas = Image.new("RGB", (W, rows * h + seam_h + 4), (20, 20, 20))
    for k, i in enumerate(idx):
        canvas.paste(Image.fromarray(fr[i].astype(np.uint8)), ((k % a.cols) * w, (k // a.cols) * h))
    diff = np.clip(np.abs(fr[-1] - fr[0]) * 4, 0, 255).astype(np.uint8)
    y = rows * h + 4
    for k, im in enumerate((fr[-1], fr[0], diff)):
        canvas.paste(Image.fromarray(im.astype(np.uint8)), (k * w, y))
    canvas.save(a.out, quality=88)
    print(json.dumps({"sheet": a.out, "frames": idx.tolist(), "seam_strip": "последний | первый | |Δ|×4"}, ensure_ascii=False))


# ---------- OKLab (перенос цвета) ----------
M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])


def to_oklab(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return np.cbrt(c @ M1.T) @ M2.T


def from_oklab(lab):
    lin = (lab @ np.linalg.inv(M2).T) ** 3 @ np.linalg.inv(M1).T
    lin = np.clip(lin, 0, 1)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)


def cmd_colormatch(a):
    S = np.asarray(Image.open(a.src).convert("RGB"), np.float64) / 255.0
    R = np.asarray(Image.open(a.ref).convert("RGB").resize((S.shape[1], S.shape[0]), Image.LANCZOS), np.float64) / 255.0
    m = np.ones(S.shape[:2], bool)
    if a.mask:
        m = np.asarray(Image.open(a.mask).convert("L").resize((S.shape[1], S.shape[0])), np.float32) > 127
    Ls, Lr = to_oklab(S), to_oklab(R)
    mu_s, sd_s = Ls[m].mean(0), Ls[m].std(0) + 1e-6
    mu_r, sd_r = Lr[m].mean(0), Lr[m].std(0)
    out = from_oklab((Ls - mu_s) / sd_s * sd_r + mu_r)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(a.out)
    before = de2000(srgb_to_lab(S), srgb_to_lab(R))[m]
    after = de2000(srgb_to_lab(out), srgb_to_lab(R))[m]
    print(json.dumps({"out": a.out, "dE00_med_before": round(float(np.median(before)), 2), "dE00_med_after": round(float(np.median(after)), 2),
                      "mask_area": round(float(m.mean()), 3)}, ensure_ascii=False))


# ---------- самопроверка ----------
def synth(n=96, h=90, w=160, seed=1, period=48, warp=None):
    """Петля по построению: периодический шум (плитка period px), сдвиг period/n = 0,5 px за кадр (кадр n = кадр 0).
    warp(u) — неравномерная скорость: смещение period·warp(i/n), warp(0) = 0, warp(1) = 1."""
    rng = np.random.default_rng(seed)
    tile = ndi.gaussian_filter(rng.random((h, period)) * 255, 2, mode="wrap")
    tile = (tile - tile.mean()) * 3 + 128
    base = np.tile(tile, (1, w // period + 2))
    pos = [(warp(i / n) if warp else i / n) * period for i in range(n)]
    return np.stack([ndi.shift(base, (0, -p), mode="wrap", order=1)[:, :w] for p in pos]).astype(np.float32)


def cmd_selftest(a):
    s = synth()
    n = len(s)
    fast_at_seam = synth(warp=lambda u: u + 0.9 * np.sin(2 * np.pi * u) / (2 * np.pi))    # быстро у стыка, медленно в середине
    subtle = synth(period=48) * 0.04 + 128 * 0.96                                           # еле заметное движение (MAD ≈ 0,1)
    cases = {
        "perfect": s,
        "dup_last": np.concatenate([s, s[:1]]),                       # FLF [A,A]: последний кадр = первый
        "gap_8": s[: n - 8],                                           # петля не замкнулась: не хватает 8 кадров
        "collapse": np.concatenate([s[: n // 2], np.repeat(s[n // 2: n // 2 + 1], n // 2, 0)]),  # движение угасло
        "cut": np.concatenate([s[: n // 2], np.clip(synth(seed=7)[n // 2:] * 0.5 + 150, 0, 255)]),  # склейка: другой план
        "dead_both": np.concatenate([s[:1], s, s[:1]]),                # круговой стык цепочки: мёртвый старт и конец
        "dup_x2": np.concatenate([s, s[:1], s[:1]]),                   # два дубля A в конце: срезать 2
        "nonuniform": fast_at_seam,                                    # как оборот: движение неравномерно по циклу
        "subtle": subtle,                                              # тихая петля уровня Notion/Seasats (A/02)
        "pingpong": np.concatenate([s[: n // 2], s[n // 2 - 2:0:-1]]),  # вперёд-назад
    }
    res = {}
    for k, fr in cases.items():
        m = loop_metrics(fr)
        m.pop("_curve")
        res[k] = {x: m[x] for x in ("motion_med", "seam_ratio", "seam_ratio_local", "cut_ratio", "cut_ratio_global", "tail_motion",
                                    "static_frac", "static_abs_frac", "dup_last", "dead_start", "dead_end", "collapse_suspect",
                                    "pingpong_suspect", "mirror_ratio", "trim")}
        res[k]["verdict"] = verdict(m)
    cam = np.stack([ndi.shift(s[0], (0, 0.7 * i), mode="nearest", order=1) for i in range(8)])
    res["cam_drift_0.7px_per_frame"] = round(loop_metrics(cam)["cam_shift_max_px"], 2)
    ok = (0.8 <= res["perfect"]["seam_ratio"] <= 1.2 and res["dup_last"]["dup_last"] and res["dup_last"]["trim"]["end"] == 1
          and 0.8 <= res["dup_last"]["trim"]["seam_ratio_after"] <= 1.2 and res["gap_8"]["seam_ratio"] > 1.5
          and res["gap_8"]["seam_ratio_local"] > 1.5 and not res["gap_8"]["verdict"]["seam"]
          and res["collapse"]["tail_motion"] < 0.5 and res["collapse"]["collapse_suspect"] and res["cut"]["cut_ratio"] > 10
          and not res["cut"]["verdict"]["no_cut"]
          and res["dead_both"]["trim"]["start"] == 1 and res["dead_both"]["trim"]["end"] == 1 and res["dead_both"]["trim"]["n_after"] == n
          and res["dup_x2"]["trim"]["end"] == 2 and abs(res["cam_drift_0.7px_per_frame"] - 4.9) < 0.3
          and res["nonuniform"]["seam_ratio_local"] <= 1.5 and res["nonuniform"]["verdict"]["seam"]
          and res["subtle"]["static_frac"] <= 0.3 and res["subtle"]["verdict"]["not_static"] and res["subtle"]["static_abs_frac"] > 0.9
          and res["pingpong"]["pingpong_suspect"] and not res["perfect"]["pingpong_suspect"]
          and all(res[k]["verdict"]["no_cut"] for k in ("perfect", "nonuniform", "subtle", "collapse")))
    res["PASS"] = bool(ok)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return ok


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("loop"); x.add_argument("video"); x.add_argument("--control"); x.add_argument("--width", type=int, default=320)
    x.add_argument("--dead", type=float, default=0.25)
    x = sp.add_parser("trim"); x.add_argument("video"); x.add_argument("out"); x.add_argument("--start", type=int, default=0)
    x.add_argument("--end", type=int, default=0); x.add_argument("--auto", action="store_true")
    x = sp.add_parser("drift"); x.add_argument("video"); x.add_argument("--mask", required=True); x.add_argument("--width", type=int, default=320)
    x = sp.add_parser("chroma"); x.add_argument("video"); x.add_argument("--key", default="#00B140"); x.add_argument("--de", type=float, default=5)
    x.add_argument("--width", type=int, default=320)
    x = sp.add_parser("join"); x.add_argument("a"); x.add_argument("b")
    x = sp.add_parser("sheet"); x.add_argument("video"); x.add_argument("out"); x.add_argument("--n", type=int, default=12)
    x.add_argument("--cols", type=int, default=4)
    x = sp.add_parser("colormatch"); x.add_argument("src"); x.add_argument("ref"); x.add_argument("out"); x.add_argument("--mask")
    sp.add_parser("selftest")
    a = p.parse_args()
    r = {"loop": cmd_loop, "trim": cmd_trim, "drift": cmd_drift, "chroma": cmd_chroma, "join": cmd_join, "sheet": cmd_sheet,
         "colormatch": cmd_colormatch, "selftest": cmd_selftest}[a.cmd](a)
    if a.cmd == "selftest" and not r:
        sys.exit(1)


if __name__ == "__main__":
    main()
