#!/usr/bin/env python3
"""video_loop_check.py — приёмка видео для сайта: шов петли, «живость», мёртвые концы, склейки и монтаж, повторы кадров,
вспышки (WCAG 2.3.1), дрейф неподвижных зон и камеры, однородность хромакея, стык клипов цепочки, контактный лист.

Python окружения скилла (numpy, scipy, Pillow, PyYAML) + ffmpeg и ffprobe; ΔE00, SSIM и фазовая корреляция — из
edit_check.py (та же папка). Вход VIDEO — видеофайл или папка кадров (PNG/JPG по имени). Числа приёмки (шов по стадии
файла, склейка, «мёртвая» пара, угасание, вспышки, хромакей) — группы video и video_alpha файла
kb/ai-media/11-evaluation-qa/thresholds.yaml (--thresholds — другой файл): в коде порогов нет, нет ключа — код 2.

Команды:
  loop   VIDEO [--control VIDEO] [--width 320] [--dead D] [--encoded] [--montage] [--once] [--fade-event]
         seam_ratio = MAD(последний, первый) / motion_med; motion_med («живость») = медиана MAD соседних кадров (0–255,
         серый, 320 px); seam_ratio_local — шов к движению у концов (ends_motion — медиана трёх пар у каждого конца);
         cut_ratio = пара к медиане соседей в окне ±6 пар, cuts — кадры, с которых начинается новый план;
         static_frac = доля «мёртвых» пар (MAD < video.dead_pair_frac × motion_med); head/tail_motion = медиана первой
         и последней четверти к motion_med; dead_start/dead_end — подряд идущие «мёртвые» пары на концах; dup_last —
         последний кадр дублирует первый; dup_frames — «мёртвые» пары внутри ролика между живыми соседями (повтор
         кадра — рывок; плавная остановка у точки разворота не считается), timing — таймкоды: при переменной частоте
         кадр, который держится дольше шага, считается повтором; trim — сколько
         кадров срезать и шов после среза; best_cut — лучшая точка реза в последних 40 %; cam_shift_max_px —
         глобальный сдвиг к кадру 0 (фазовая корреляция, пиксели исходника); seam_dE00 и color_drift_dE00 — ΔE00
         среднего цвета; flash — вспышки. С --control: motion_vs_control и curve_corr (хореография).
         Вердикт шва — по файлу как есть (seam_check): порог отношения — video.seam_local_max у мезонина и выхода
         модели, video.seam_encoded_max у файла после кодирования (--encoded); у почти неподвижных концов (движение
         ниже video.quiet_motion_med) шов сверяется по абсолютной разнице кадров с тем же уровнем.
         --montage — ролик из нескольких планов: склейки не находка, «мёртвые» пары и угасание считаются к движению
         своего плана, стык петли принимается и как гладкий шов, и как ещё одна склейка. --once — разовый ролик
         (вступление): шов, угасание и концы не судятся. --fade-event — в петле объявлено событие-затемнение: длинный
         «мёртвый» конец вердикт не роняет.
  flash  VIDEO [--css-width W] [--fps F]   вспышки по WCAG 2.3.1 на родных кадрах: переход — изменение относительной
         яркости не меньше video.flash_luma_delta_min при тёмном состоянии ниже video.flash_dark_max, вспышка — пара
         противоположных переходов; провал — больше video.flash_per_s_max вспышек за секунду на доле
         video.flash_area_frac_min поля video.flash_field_css_px. --css-width — ширина ролика на странице в CSS px (по
         умолчанию — ширина файла); у папки кадров частота — --fps. Красные вспышки отдельно не считаются.
  trim   VIDEO OUT [--start K] [--end K] [--auto]   срез кадров на концах, без звука, мезонин без потерь x264 -qp 0 в
         пиксельном формате исходника (не из списка x264 — 4:4:4), +faststart: на нём меряют шов и с него кодируют
         финал. --auto — все «мёртвые» пары у концов по порогу движения и дубль последнего кадра (поле trim команды
         loop). ffmpeg trim=start_frame:end_frame (end — исключительно) и -r <fps>: без него MP4 после setpts теряет
         последний кадр (edit list); ok — число кадров сошлось. Размер ≈ 10–40 МБ на 5 с 1080p — файл промежуточный.
  drift  VIDEO --mask MASK.png [--width 320]   неподвижные зоны (белое в маске): MAD к кадру 0 по времени, максимум и
         медиана; сдвиг камеры по маске; dE00_max/dE00_last — ΔE00 среднего цвета зоны к кадру 0. Нормы синемаграфа —
         video.cinemagraph_drift_max, video.cam_shift_max_px, video.color_de_max.
  chroma VIDEO [--key '#00B140'|auto] [--de D]   фон = пиксели, близкие к ключу (ΔE00 < 25) и связанные с краем кадра;
         доля фона с ΔE00 ≤ de к ключу (bg_ok_min по кадрам; de по умолчанию — video_alpha.key_de), σ фона, дрейф
         центра объекта (% ширины), масштаб (площадь).
  join   A B   стык клипов цепочки: MAD и seam_ratio стыка к живости обоих, SSIM, ΔE00 среднего цвета, отношение темпа.
  sheet  VIDEO OUT.jpg [--n 12] [--cols 4]   контактный лист: N кадров равномерно + полоса «последний | первый | |Δ|×4».
  colormatch SRC REF OUT [--mask M]   перенос среднего и σ в OKLab (Рейнхард) от REF к SRC по белой зоне маски
         (неизменные зоны) — подгонка правленого конечного кадра к начальному.
  selftest   синтетика с известным ответом: идеальная петля, дубль, разрыв, угасание, склейка, сдвиг камеры, монтаж
         трёх планов, петля с равными концами, почти неподвижные концы, повторы кадров и точка разворота, срез по
         движению, вспышки.
Выход — JSON в stdout. Код выхода: 0 — команда выполнена; 1 — самопроверка не прошла; 2 — ошибка вызова или нет порога.
"""
import argparse, glob, json, os, subprocess, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # scripts/lib: kbpaths
import kbpaths  # noqa: E402
from edit_check import srgb_to_lab, de2000, ssim_map, phase_shift  # noqa: E402

VERSION = "0.3"
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
THRESHOLDS = kbpaths.kb("ai-media", "11-evaluation-qa", "thresholds.yaml")
TH_GROUPS = ("video", "video_alpha")
TH_KEYS = ("video.seam_local_max", "video.seam_encoded_max", "video.cut_ratio_max", "video.head_tail_min",
           "video.static_frac_max", "video.motion_vs_control_min", "video.dead_pair_frac", "video.dead_trim_max",
           "video.quiet_motion_med", "video.pingpong_mirror_max", "video.flash_luma_delta_min", "video.flash_dark_max",
           "video.flash_per_s_max", "video.flash_area_frac_min", "video.flash_field_css_px", "video_alpha.bg_ok_min",
           "video_alpha.key_de", "video_alpha.obj_drift_max_pct_w")


# ---------- пороги ----------
class ThresholdError(Exception):
    """Нет файла порогов или ключа в нём — код выхода 2."""


def limits(path=None):
    """Числа приёмки групп video и video_alpha: {'video.seam_local_max': …}. Источник один — thresholds.yaml."""
    import yaml
    p = path or THRESHOLDS
    try:
        with open(p, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
    except OSError as e:
        raise ThresholdError(f"нет файла порогов {p}: {e.strerror}")
    out = {}
    for g in TH_GROUPS:
        for k, node in ((doc.get("thresholds") or {}).get(g) or {}).items():
            if isinstance(node, dict) and "value" in node:
                out[f"{g}.{k}"] = node["value"]
    return out


def lim(th, key):
    if th.get(key) is None:
        raise ThresholdError(f"нет порога {key} в thresholds.yaml (группы video и video_alpha)")
    return th[key]


# ---------- чтение кадров ----------
def probe(path):
    r = subprocess.run([kbpaths.ffprobe(), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
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


def frames(src, width=320, mode="gray"):
    """Кадры по одному (h, w[, 3]) uint8, уменьшенные до width (area). У файла — каждый декодированный кадр один раз
    (-fps_mode passthrough): при переменной частоте ffmpeg иначе сам размножает кадры до постоянной."""
    if os.path.isdir(src):
        for f in frame_files(src):
            im = Image.open(f).convert("RGB")
            h = int(round(im.height * width / im.width / 2) * 2)
            im = im.resize((width, h), Image.BOX)
            yield np.asarray(im.convert("L") if mode == "gray" else im)
        return
    p = probe(src)
    h = int(round(p["h"] * width / p["w"] / 2) * 2)
    pf, ch = ("gray", 1) if mode == "gray" else ("rgb24", 3)
    proc = subprocess.Popen([kbpaths.ffmpeg(), "-v", "error", "-threads", "4", "-i", src, "-fps_mode", "passthrough", "-vf",
                             f"scale={width}:{h}:flags=area,format={pf}", "-f", "rawvideo", "-pix_fmt", pf, "-"],
                            stdout=subprocess.PIPE)
    size = width * h * ch
    try:
        while True:
            buf = proc.stdout.read(size)
            if len(buf) < size:
                break
            yield np.frombuffer(buf, np.uint8).reshape((h, width) if ch == 1 else (h, width, 3))
    finally:
        proc.stdout.close()
        proc.wait()


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
    raw = subprocess.run([kbpaths.ffmpeg(), "-v", "error", "-threads", "4", "-i", src, "-fps_mode", "passthrough", "-vf",
                          f"scale={width}:{h}:flags=area,format={pf}", "-f", "rawvideo", "-pix_fmt", pf, "-"],
                         capture_output=True).stdout
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


def frame_timing(path):
    """Таймкоды кадров файла. Шаг — медиана интервалов; кадр, который держится два шага и дольше, — повтор по времени
    (так выглядит переменная частота после приведения к постоянной). У папки кадров таймкодов нет — None."""
    if os.path.isdir(path):
        return None
    r = subprocess.run([kbpaths.ffprobe(), "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time", "-of",
                        "csv=p=0", path], capture_output=True, text=True)
    ts = []
    for x in r.stdout.replace(",", " ").split():
        try:
            ts.append(float(x))
        except ValueError:
            continue
    if len(ts) < 3:
        return None
    dt = np.diff(np.sort(np.asarray(ts)))
    step = float(np.median(dt))
    if step <= 0:
        return None
    mult = np.rint(dt / step)
    held = np.flatnonzero(mult >= 2)
    return {"frames": len(ts), "step_s": round(step, 5), "vfr": bool((mult != 1).any()),
            "held_frames": int((mult[held] - 1).sum()), "held_at": [int(i) for i in held[:8]]}


# ---------- метрики петли ----------
def loop_metrics(fr, dead=None, rgb=None, scale=1.0, max_trim=None, k=3, win=6, th=None, montage=False):
    """Метрики ролика по кадрам fr. «Мёртвая» пара — движение ниже dead × медианы (video.dead_pair_frac); при montage
    медиана — своя у каждого плана, а пары склеек из счёта концов и заморозок исключены."""
    th = limits() if th is None else th
    dead = lim(th, "video.dead_pair_frac") if dead is None else dead
    max_trim = int(lim(th, "video.dead_trim_max")) if max_trim is None else max_trim
    cut_lim = lim(th, "video.cut_ratio_max")
    n = len(fr)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    med = float(np.median(d)) if len(d) else 0.0
    eps = max(med, 1e-6)
    seam = mad(fr[-1], fr[0])
    # склейка — локальный пик: пара к медиане соседей в окне ±win (пол знаменателя — 0,25·медианы и 0,05 уровня)
    loc = []
    for i in range(len(d)):
        nb = np.concatenate([d[max(0, i - win):i], d[i + 1:i + 1 + win]])
        loc.append(d[i] / max(float(np.median(nb)) if len(nb) else 0.0, 0.25 * eps, 0.05))
    cut_pairs = [i for i, v in enumerate(loc) if v >= cut_lim]         # пара i — между кадрами i и i + 1
    # движение пары к опорному: общая медиана, в монтаже — медиана своего плана; пары склеек в счёт не идут
    keep = np.ones(len(d), bool)
    ref = np.full(len(d), eps)
    if montage and cut_pairs:
        keep[cut_pairs] = False
        a0 = 0
        for c in cut_pairs + [len(d)]:
            if c > a0:
                ref[a0:c] = max(float(np.median(d[a0:c])), 1e-6)
            a0 = c + 1
    rel, dk, pair_at = (d / ref)[keep], d[keep], np.flatnonzero(keep)
    q = max(2, len(rel) // 4)
    ds = 0
    while ds < len(rel) and rel[ds] < dead:
        ds += 1
    de_ = 0
    while de_ < len(rel) and rel[len(rel) - 1 - de_] < dead:
        de_ += 1
    eps_ends = float(np.median([ref[0], ref[-1]])) if len(ref) else eps
    dup = seam < dead * eps_ends
    # длинный мёртвый конец — подозрение на угасание; срез — все мёртвые пары у концов и дубль последнего кадра
    collapse = ds > max_trim or de_ > max_trim
    cut_s = ds
    cut_e = de_ + (1 if dup else 0)
    f2 = fr[cut_s: n - cut_e] if n - cut_e - cut_s >= 3 else fr
    d2 = np.abs(np.diff(f2, axis=0)).mean(axis=(1, 2))
    med2 = max(float(np.median(d2)), 1e-6)

    def ends(dd):
        """Движение у концов: медиана k пар у каждого конца (движение бывает неравномерным — оборот, всплески)."""
        nb = np.concatenate([dd[:k], dd[-k:]]) if len(dd) >= 2 * k else dd
        return float(np.median(nb)) if len(nb) else 0.0

    def local(seam_mad, dd):
        return seam_mad / max(ends(dd), 1e-6)
    # повторы кадров внутри ролика: «мёртвые» пары вне концов, по обе стороны от которых движение живое (не ниже
    # video.head_tail_min) — резкая остановка; плавное замедление у точки разворота движения повтором не считается
    alive = lim(th, "video.head_tail_min")
    inner, dup_runs, i = [], 0, ds
    while i < len(rel) - de_:
        if rel[i] >= dead:
            i += 1
            continue
        j = i
        while j + 1 < len(rel) - de_ and rel[j + 1] < dead:
            j += 1
        if i > 0 and j + 1 < len(rel) and rel[i - 1] >= alive and rel[j + 1] >= alive:
            inner += list(range(i, j + 1))
            dup_runs += 1
        i = j + 1
    # пинг-понг (бумеранг): кадры симметричны во времени вокруг какого-то центра c — MAD(f[c+i], f[c−i]) ≈ 0
    th_ = fr[:, ::4, ::4]
    mir, mc = None, None
    if n >= 8 and med > 0.02:
        span = range(1, max(2, n // 4))
        eth = max(float(np.median(np.abs(np.diff(th_, axis=0)).mean(axis=(1, 2)))), 1e-6)
        for c in range(n):
            sp = float(np.median([np.abs(th_[(c + i) % n] - th_[c]).mean() for i in span]))   # размах движения вокруг c
            if sp < 2 * eth:                                                             # неподвижный участок — не судим
                continue
            v = float(np.median([np.abs(th_[(c + i) % n] - th_[(c - i) % n]).mean() for i in span])) / sp
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
           "seam_ratio_local": round(local(seam, dk), 2), "ends_motion": round(ends(dk), 3),
           "cut_ratio": round(float(max(loc)), 2) if len(d) else None, "cut_at": int(np.argmax(loc)) + 1 if len(d) else None,
           "cuts": [c + 1 for c in cut_pairs], "montage": bool(montage),
           "cut_ratio_global": round(float(d.max()) / eps, 2) if len(d) else None,
           "static_frac": round(float((rel < dead).mean()), 3) if len(rel) else None,
           "static_abs_frac": round(float((d < 0.5).mean()), 3) if len(d) else None,
           "head_motion": round(float(np.median(rel[:q])), 2), "tail_motion": round(float(np.median(rel[-q:])), 2),
           "ssim_seam": round(ssim(fr[-1], fr[0]), 4), "ssim_typ": round(float(np.median([ssim(fr[i], fr[i + 1]) for i in range(0, n - 1, step)])), 4),
           "dead_start": ds, "dead_end": de_, "dup_last": bool(dup), "collapse_suspect": bool(collapse),
           "dup_frames": int(len(inner)), "dup_runs": dup_runs, "dup_at": [int(pair_at[i]) + 1 for i in inner[:8]],
           "trim": {"start": cut_s, "end": cut_e, "seam_ratio_after": round(mad(f2[-1], f2[0]) / med2, 2),
                    "seam_ratio_local_after": round(local(mad(f2[-1], f2[0]), d2), 2), "n_after": len(f2)},
           "best_cut": {"frame": bi, "seam_ratio": round(mad(fr[bi - 1], fr[0]) / eps, 2) if bi > 0 else None},
           "mirror_ratio": round(mir, 3) if mir is not None else None, "mirror_center": mc,
           "pingpong_suspect": bool(mir is not None and mir < lim(th, "video.pingpong_mirror_max")),
           "cam_shift_max_px": round(cam, 2)}
    if rgb is not None:
        labs = [mean_lab(x) for x in rgb]
        res["seam_dE00"] = round(dE(labs[-1], labs[0]), 2)
        res["color_drift_dE00"] = round(max(dE(l, labs[0]) for l in labs), 2)
    res["_curve"] = d
    return res


def seam_check(m, th, encoded=False, montage=False):
    """Вердикт шва по файлу как есть. Порог отношения — по стадии файла: мезонин и выход модели — video.seam_local_max,
    файл после кодирования — video.seam_encoded_max (пульс ключевого кадра). У почти неподвижных концов отношение
    неустойчиво: шов на уровне соседних кадров принимается по абсолютной разнице — не выше video.quiet_motion_med. В
    монтаже стык петли — ещё одна склейка: шов, который сам проходит порог склейки, в норме."""
    limit = lim(th, "video.seam_encoded_max" if encoded else "video.seam_local_max")
    quiet = lim(th, "video.quiet_motion_med")
    out = {"stage": "encoded" if encoded else "mezzanine", "value": m["seam_ratio_local"], "limit": limit, "basis": "ratio",
           "ok": m["seam_ratio_local"] <= limit}
    if not out["ok"] and m["ends_motion"] < quiet and m["seam_mad"] <= quiet:
        out.update(ok=True, basis="abs", value=m["seam_mad"], limit=quiet)
    elif not out["ok"] and montage and m["seam_ratio_local"] >= lim(th, "video.cut_ratio_max"):
        out.update(ok=True, basis="cut", limit=lim(th, "video.cut_ratio_max"))
    return out


def verdict(m, th=None, encoded=False, montage=False, once=False, fade_event=False):
    """Вердикт по порогам thresholds.yaml. Разовый ролик (once) — без шва, концов и угасания; монтаж — склейки объявлены;
    событие-затемнение (fade_event) — длинный мёртвый конец вердикт не роняет."""
    th = limits() if th is None else th
    v = {"no_cut": montage or (m["cut_ratio"] or 0) < lim(th, "video.cut_ratio_max"), "no_dup_frames": not m["dup_frames"]}
    if not once:
        alive = lim(th, "video.head_tail_min")
        v.update({"seam": seam_check(m, th, encoded, montage)["ok"], "alive_head": m["head_motion"] >= alive,
                  "alive_tail": m["tail_motion"] >= alive,
                  "not_static": (m["static_frac"] or 0) <= lim(th, "video.static_frac_max")
                  and (fade_event or not m["collapse_suspect"])})
    if "motion_vs_control" in m:
        v["alive_vs_control"] = m["motion_vs_control"] >= lim(th, "video.motion_vs_control_min")
    if isinstance(m.get("flash"), dict):
        v["no_flash"] = not m["flash"].get("fail")
    if isinstance(m.get("timing"), dict):
        v["no_dup_frames"] = v["no_dup_frames"] and not m["timing"]["held_frames"]
    return v


# ---------- вспышки (WCAG 2.3.1) ----------
def flash_scan(src, th=None, css_width=None, width=256, fps=None, frames_iter=None):
    """Вспышки на родных кадрах. Переход — изменение относительной яркости пикселя от последнего экстремума не меньше
    video.flash_luma_delta_min при тёмном состоянии ниже video.flash_dark_max; вспышка — пара противоположных переходов.
    Провал — больше video.flash_per_s_max вспышек в любую секунду на доле video.flash_area_frac_min поля
    video.flash_field_css_px. css_width — ширина ролика на странице, CSS px (по умолчанию — ширина файла)."""
    th = limits() if th is None else th
    delta, dark = lim(th, "video.flash_luma_delta_min"), lim(th, "video.flash_dark_max")
    per_s, area_min = lim(th, "video.flash_per_s_max"), lim(th, "video.flash_area_frac_min")
    fw, fh = lim(th, "video.flash_field_css_px")
    if frames_iter is None:
        if fps is None and not os.path.isdir(src):
            pr = probe(src)
            try:
                num, den = str(pr.get("r_frame_rate") or "").split("/")
                fps = pr.get("fps") or float(num) / float(den)
            except (ValueError, ZeroDivisionError):
                fps = pr.get("fps")
        css_width = css_width or src_width(src)
        frames_iter = frames(src, width, "rgb")
    if not fps:
        raise ThresholdError("частота кадров неизвестна: у папки кадров задайте --fps")
    css_per_px = (css_width or width) / width
    win = max(1, int(round(fps)))
    need = 2 * int(per_s) + 1                              # больше per_s вспышек = не меньше 2·per_s + 1 переходов
    lut = np.arange(256, dtype=np.float32) / 255.0
    lut = np.where(lut <= 0.04045, lut / 12.92, ((lut + 0.055) / 1.055) ** 2.4).astype(np.float32)
    coef = np.array([0.2126, 0.7152, 0.0722], np.float32)
    ring, last, dirn, count = [], None, None, None
    n, worst, worst_t, tr_max = 0, 0.0, None, 0
    for f in frames_iter:
        L = lut[f] @ coef if f.ndim == 3 else lut[f]
        if last is None:
            last, dirn = L.copy(), np.zeros(L.shape, np.int8)
            tr = np.zeros(L.shape, bool)
            count = np.zeros(L.shape, np.int16)
            ww, hh = min(L.shape[1], max(2, int(round(fw / css_per_px)))), min(L.shape[0], max(2, int(round(fh / css_per_px))))
        else:
            low = np.minimum(L, last) < dark
            up = (L - last >= delta) & low & (dirn <= 0)
            down = (last - L >= delta) & low & (dirn >= 0)
            tr = up | down
            ext = ((dirn >= 0) & (L > last)) | ((dirn <= 0) & (L < last))
            last = np.where(tr | ext, L, last)
            dirn = np.where(up, 1, np.where(down, -1, dirn)).astype(np.int8)
        ring.append(tr)
        count += tr
        if len(ring) > win:
            count -= ring.pop(0)
        n += 1
        tr_max = max(tr_max, int(count.max()))
        hot = count >= need
        if hot.any():
            ii = np.pad(hot.astype(np.float32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
            area = ii[hh:, ww:] - ii[:-hh, ww:] - ii[hh:, :-ww] + ii[:-hh, :-ww]
            frac = float(area.max()) / (ww * hh)
            if frac > worst:
                worst, worst_t = frac, round((n - 1) / fps, 2)
    return {"frames": n, "fps": fps, "css_width": css_width, "field_px": [ww, hh] if n else None,
            "transitions_per_s_max": tr_max, "flashes_per_s_max": tr_max // 2, "max_area_frac": round(worst, 3),
            "fail": worst >= area_min, "worst_t_s": worst_t}


def cmd_flash(a):
    out = flash_scan(a.video, limits(a.thresholds), css_width=a.css_width, fps=a.fps)
    print(json.dumps(out, ensure_ascii=False))
    return out


def cmd_loop(a):
    th = limits(getattr(a, "thresholds", None))
    fr = load(a.video, a.width)
    rgb = load(a.video, 96, "rgb")
    m = loop_metrics(fr, a.dead, rgb, src_width(a.video) / a.width, th=th, montage=a.montage)
    if a.control:
        c = load(a.control, a.width)
        cm = loop_metrics(c, a.dead, th=th)
        m["control_motion_med"] = cm["motion_med"]
        m["motion_vs_control"] = round(m["motion_med"] / max(cm["motion_med"], 1e-6), 2)
        x, y = m["_curve"], cm["_curve"]
        k = min(len(x), len(y))
        xi = np.interp(np.linspace(0, 1, k), np.linspace(0, 1, len(x)), x)
        yi = np.interp(np.linspace(0, 1, k), np.linspace(0, 1, len(y)), y)
        m["curve_corr"] = round(float(np.corrcoef(xi, yi)[0, 1]), 3) if xi.std() > 0 and yi.std() > 0 else None
    m.pop("_curve")
    m["timing"] = frame_timing(a.video)
    if not os.path.isdir(a.video):
        m["probe"] = probe(a.video)
        try:
            m["flash"] = flash_scan(a.video, th)
        except ThresholdError as e:
            m["flash"] = {"error": str(e)}
    if not a.once:
        m["seam_check"] = seam_check(m, th, a.encoded, a.montage)
    m["verdict"] = verdict(m, th, a.encoded, a.montage, a.once, a.fade_event)
    print(json.dumps(m, ensure_ascii=False))
    return m


X264_LOSSLESS_PIX = {"yuv420p", "yuvj420p", "yuv422p", "yuvj422p", "yuv444p", "yuvj444p", "yuv420p10le", "yuv422p10le",
                     "yuv444p10le", "gray", "gray10le"}


def cmd_trim(a):
    s, e = a.start, a.end
    if a.auto:
        m = loop_metrics(load(a.video, 320), th=limits(a.thresholds))
        s, e = m["trim"]["start"], m["trim"]["end"]
    n = len(load(a.video, 64))
    vf = f"trim=start_frame={s}:end_frame={n - e},setpts=PTS-STARTPTS"
    # -r обязателен: после setpts у последнего кадра нет длительности и MP4-мультиплексор отрезает его списком
    # правки (edit list) — 145 кадров → 144 (ffmpeg 7.1.5); для петли это лишний шаг на стыке
    pr = probe(a.video) if not os.path.isdir(a.video) else {}
    fr = pr.get("r_frame_rate") or "24/1"
    # мезонин без потерь (x264 -qp 0): сжатие с потерями даёт пульс ключевого кадра и ложный шов у чистой петли; формат
    # исходника сохраняется (4:2:0 → 4:2:0 без пересчёта цветности, 10 бит → 10 бит), кадры вне списка x264 (RGB и т. п.)
    # — 4:4:4.
    pix = pr.get("pix_fmt") if pr.get("pix_fmt") in X264_LOSSLESS_PIX else "yuv444p"
    cmd = [kbpaths.ffmpeg(), "-v", "error", "-y", "-threads", "4", "-i", a.video, "-vf", vf, "-an", "-c:v", "libx264", "-qp", "0",
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
    th = limits(getattr(a, "thresholds", None))
    de_thr = lim(th, "video_alpha.key_de") if a.de is None else a.de
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
        ok = float((de[bg] <= de_thr).mean()) if bg.any() else 0.0
        yx = np.argwhere(obj)
        c = yx.mean(0) if len(yx) else np.array([h / 2, w / 2])
        area = float(obj.mean())
        if c0 is None:
            c0, area0 = c, max(area, 1e-6)
        rows.append({"bg_ok": ok, "bg_de_mean": float(de[bg].mean()) if bg.any() else None,
                     "bg_sigma": float(f[bg].std(0).mean()) if bg.any() else None,
                     "drift_pct_w": float(np.hypot(*(c - c0)) / w * 100), "area_ratio": area / area0})
    out = {"n": n, "key": "#%02X%02X%02X" % tuple(int(x) for x in key), "de_thr": de_thr,
           "bg_ok_min": round(min(r["bg_ok"] for r in rows), 4), "bg_ok_med": round(float(np.median([r["bg_ok"] for r in rows])), 4),
           "bg_de_mean_max": round(max(r["bg_de_mean"] or 0 for r in rows), 2), "bg_sigma_max": round(max(r["bg_sigma"] or 0 for r in rows), 2),
           "obj_drift_max_pct_w": round(max(r["drift_pct_w"] for r in rows), 2),
           "obj_area_ratio_range": [round(min(r["area_ratio"] for r in rows), 3), round(max(r["area_ratio"] for r in rows), 3)]}
    out["verdict"] = {"bg_uniform": out["bg_ok_min"] >= lim(th, "video_alpha.bg_ok_min"),
                      "obj_still": out["obj_drift_max_pct_w"] <= lim(th, "video_alpha.obj_drift_max_pct_w")}
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
    th = limits()
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
        "subtle": subtle,                                              # тихая петля
        "pingpong": np.concatenate([s[: n // 2], s[n // 2 - 2:0:-1]]),  # вперёд-назад
        "dead_start_5": np.concatenate([np.repeat(s[:1], 5, 0), s]),   # кадр A держится пять кадров, потом движение
        "dup_inner": np.concatenate([np.repeat(s[i:i + 1], 2 if i % 5 == 4 else 1, 0) for i in range(n)]),  # каждый пятый кадр дважды
    }
    res = {}
    for k, fr in cases.items():
        m = loop_metrics(fr, th=th)
        m.pop("_curve")
        res[k] = {x: m[x] for x in ("motion_med", "seam_ratio", "seam_ratio_local", "cut_ratio", "cut_ratio_global", "tail_motion",
                                    "static_frac", "static_abs_frac", "dup_last", "dead_start", "dead_end", "collapse_suspect",
                                    "pingpong_suspect", "mirror_ratio", "dup_frames", "trim")}
        res[k]["verdict"] = verdict(m, th)
    cam = np.stack([ndi.shift(s[0], (0, 0.7 * i), mode="nearest", order=1) for i in range(8)])
    res["cam_drift_0.7px_per_frame"] = round(loop_metrics(cam, th=th)["cam_shift_max_px"], 2)
    seam_max = lim(th, "video.seam_local_max")
    cut_max = lim(th, "video.cut_ratio_max")
    alive = lim(th, "video.head_tail_min")
    ok = (0.8 <= res["perfect"]["seam_ratio"] <= 1.2 and res["dup_last"]["dup_last"] and res["dup_last"]["trim"]["end"] == 1
          and 0.8 <= res["dup_last"]["trim"]["seam_ratio_after"] <= 1.2 and res["gap_8"]["seam_ratio"] > seam_max
          and res["gap_8"]["seam_ratio_local"] > seam_max and not res["gap_8"]["verdict"]["seam"]
          and res["collapse"]["tail_motion"] < alive and res["collapse"]["collapse_suspect"] and res["cut"]["cut_ratio"] > cut_max
          and not res["cut"]["verdict"]["no_cut"]
          and res["dead_both"]["trim"]["start"] == 1 and res["dead_both"]["trim"]["end"] == 1 and res["dead_both"]["trim"]["n_after"] == n
          and res["dup_x2"]["trim"]["end"] == 2 and abs(res["cam_drift_0.7px_per_frame"] - 4.9) < 0.3
          and res["nonuniform"]["seam_ratio_local"] <= seam_max and res["nonuniform"]["verdict"]["seam"]
          and res["subtle"]["static_frac"] <= lim(th, "video.static_frac_max") and res["subtle"]["verdict"]["not_static"]
          and res["subtle"]["static_abs_frac"] > 0.9
          and res["pingpong"]["pingpong_suspect"] and not res["perfect"]["pingpong_suspect"]
          and all(res[k]["verdict"]["no_cut"] for k in ("perfect", "nonuniform", "subtle", "collapse")))
    extra = {}

    def check(name, cond):
        extra[name] = bool(cond)
    check("пороги: все ключи утилиты есть в thresholds.yaml", all(th.get(k) is not None for k in TH_KEYS))
    check("петля с равными концами: шов по файлу как есть — 0, вердикт шва в норме",
          res["dup_last"]["seam_ratio_local"] == 0 and res["dup_last"]["verdict"]["seam"])
    check("срез по движению: мёртвое начало из пяти кадров срезается целиком",
          res["dead_start_5"]["trim"]["start"] == 5 and res["dead_start_5"]["trim"]["n_after"] == n)
    check("повторы кадров внутри ролика — счёт и провал no_dup_frames",
          res["dup_inner"]["dup_frames"] >= 15 and not res["dup_inner"]["verdict"]["no_dup_frames"]
          and res["perfect"]["dup_frames"] == 0 and res["perfect"]["verdict"]["no_dup_frames"])
    pend = np.stack([ndi.shift(s[0], (0, 6 * np.sin(2 * np.pi * i / n)), mode="wrap", order=1) for i in range(n)])
    mp = loop_metrics(pend, th=th)
    res["pendulum"] = {"dup_frames": mp["dup_frames"], "static_frac": mp["static_frac"]}
    check("точка разворота движения (маятник): плавная остановка — не повтор кадра", mp["dup_frames"] == 0 and mp["static_frac"] > 0)
    # монтаж трёх планов: два живых и тихий (движение впятеро слабее); стык петли — тоже склейка
    b = np.clip(synth(seed=5) * 0.5 + 150, 0, 255)
    quiet = np.clip(synth(seed=3, n=480)[:32] * 0.8 - 20, 0, 255)       # 0,1 px за кадр — движение в пять раз слабее
    mont = np.concatenate([s[:32], b[:32], quiet])
    m1, m2 = loop_metrics(mont, th=th), loop_metrics(mont, th=th, montage=True)
    v1, v2 = verdict(m1, th), verdict(m2, th, montage=True)
    res["montage"] = {"cuts": m2["cuts"], "plain": v1, "montage": v2, "seam_check": seam_check(m2, th, montage=True),
                      "dead_end_plain": m1["dead_end"], "dead_end_montage": m2["dead_end"]}
    check("монтаж без ключа: склейки — находка", not v1["no_cut"] and m1["cuts"] == [32, 64])
    check("монтаж с ключом: две склейки, без находки склейки, шов-склейка в норме, тихий план не «мёртвый»",
          v2["no_cut"] and m2["cuts"] == [32, 64] and v2["seam"] and res["montage"]["seam_check"]["basis"] == "cut"
          and v2["not_static"] and v2["alive_tail"] and m2["dead_end"] == 0 and not m2["collapse_suspect"])
    check("монтаж: без ключа тихий план после живых считается угасанием", m1["collapse_suspect"] or not v1["alive_tail"])
    # событие-затемнение: длинный мёртвый конец — провал not_static, с ключом события — нет
    fade = np.concatenate([s[:80], s[80:88] * np.linspace(1, 0, 8, dtype=np.float32)[:, None, None], np.zeros_like(s[:8])])
    mf = loop_metrics(fade, th=th)
    res["fade_event"] = {"collapse_suspect": mf["collapse_suspect"], "plain": verdict(mf, th)["not_static"],
                         "fade_event": verdict(mf, th, fade_event=True)["not_static"]}
    check("событие-затемнение: провал not_static без ключа, норма с ключом",
          mf["collapse_suspect"] and not res["fade_event"]["plain"] and res["fade_event"]["fade_event"])
    # почти неподвижные концы: шов на уровне соседних кадров — отношение велико, абсолютная разница мала
    slow = synth(warp=lambda u: u - 0.98 * np.sin(2 * np.pi * u) / (2 * np.pi)) * 0.1 + 115    # у стыка движение почти нулевое
    slow = np.concatenate([slow, slow[:1] + 0.08])
    ms = loop_metrics(slow, th=th)
    res["static_ends"] = {"seam_mad": ms["seam_mad"], "ends_motion": ms["ends_motion"], "seam_ratio_local": ms["seam_ratio_local"],
                          "seam_check": seam_check(ms, th)}
    check("почти неподвижные концы: отношение выше порога, шов принят по абсолютной разнице",
          ms["seam_ratio_local"] > seam_max and res["static_ends"]["seam_check"]["ok"]
          and res["static_ends"]["seam_check"]["basis"] == "abs")
    check("шов по стадии файла: отношение между порогами мезонина и файла после кодирования — провал только у мезонина",
          not seam_check({"seam_ratio_local": 2.0, "ends_motion": 1.0, "seam_mad": 2.0}, th)["ok"]
          and seam_check({"seam_ratio_local": 2.0, "ends_motion": 1.0, "seam_mad": 2.0}, th, encoded=True)["ok"]
          and seam_max < 2.0 <= lim(th, "video.seam_encoded_max"))
    check("разовый ролик: вердикт без шва, концов и угасания",
          set(verdict(loop_metrics(cases["gap_8"], th=th), th, once=True)) == {"no_cut", "no_dup_frames"})

    # вспышки: 25 кадров/с, мигание на весь кадр 10 Гц — провал, 1 Гц — норма; мигание на малом пятне — норма
    def blink(hz, spot=False, fps=25, sec=2):
        for i in range(fps * sec):
            f = np.full((36, 64, 3), 20, np.uint8)
            if int(i * 2 * hz / fps) % 2:
                (f[:2, :3] if spot else f)[...] = 235
            yield f
    fl = {hz: flash_scan(None, th, css_width=1280, width=64, fps=25, frames_iter=blink(hz)) for hz in (10, 1)}
    spot = flash_scan(None, th, css_width=64 * 40, width=64, fps=25, frames_iter=blink(10, spot=True))
    res["flash"] = {"10hz": fl[10], "1hz": fl[1], "spot_10hz": spot}
    check("вспышки: 10 Гц на весь кадр — провал, 1 Гц — норма", fl[10]["fail"] and not fl[1]["fail"]
          and fl[10]["flashes_per_s_max"] > lim(th, "video.flash_per_s_max") >= fl[1]["flashes_per_s_max"])
    check("вспышки: мигание на пятне меньше доли поля — норма", not spot["fail"] and 0 < spot["max_area_frac"] < lim(th, "video.flash_area_frac_min"))
    try:
        lim({}, "video.seam_local_max")
        raised = False
    except ThresholdError:
        raised = True
    check("нет порога в данных — ошибка, чисел в коде нет", raised)
    res["checks"] = extra
    res["PASS"] = bool(ok and all(extra.values()))
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return res["PASS"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("loop"); x.add_argument("video"); x.add_argument("--control"); x.add_argument("--width", type=int, default=320)
    x.add_argument("--dead", type=float, help="доля медианы движения, ниже которой пара «мёртвая» (по умолчанию — video.dead_pair_frac)")
    x.add_argument("--encoded", action="store_true", help="файл после кодирования: порог шва — video.seam_encoded_max")
    x.add_argument("--montage", action="store_true", help="ролик из нескольких планов: склейки объявлены")
    x.add_argument("--once", action="store_true", help="разовый ролик: шов, концы и угасание не судятся")
    x.add_argument("--fade-event", action="store_true", help="в петле объявлено событие-затемнение")
    x.add_argument("--thresholds", help="другой файл порогов")
    x = sp.add_parser("flash"); x.add_argument("video")
    x.add_argument("--css-width", type=float, help="ширина ролика на странице, CSS px (по умолчанию — ширина файла)")
    x.add_argument("--fps", type=float, help="частота кадров папки кадров"); x.add_argument("--thresholds")
    x = sp.add_parser("trim"); x.add_argument("video"); x.add_argument("out"); x.add_argument("--start", type=int, default=0)
    x.add_argument("--end", type=int, default=0); x.add_argument("--auto", action="store_true"); x.add_argument("--thresholds")
    x = sp.add_parser("drift"); x.add_argument("video"); x.add_argument("--mask", required=True); x.add_argument("--width", type=int, default=320)
    x = sp.add_parser("chroma"); x.add_argument("video"); x.add_argument("--key", default="#00B140"); x.add_argument("--de", type=float)
    x.add_argument("--width", type=int, default=320); x.add_argument("--thresholds")
    x = sp.add_parser("join"); x.add_argument("a"); x.add_argument("b")
    x = sp.add_parser("sheet"); x.add_argument("video"); x.add_argument("out"); x.add_argument("--n", type=int, default=12)
    x.add_argument("--cols", type=int, default=4)
    x = sp.add_parser("colormatch"); x.add_argument("src"); x.add_argument("ref"); x.add_argument("out"); x.add_argument("--mask")
    sp.add_parser("selftest")
    a = p.parse_args()
    try:
        r = {"loop": cmd_loop, "flash": cmd_flash, "trim": cmd_trim, "drift": cmd_drift, "chroma": cmd_chroma, "join": cmd_join,
             "sheet": cmd_sheet, "colormatch": cmd_colormatch, "selftest": cmd_selftest}[a.cmd](a)
    except ThresholdError as e:
        print(f"video_loop_check.py {a.cmd}: {e}", file=sys.stderr)
        sys.exit(2)
    if a.cmd == "selftest" and not r:
        sys.exit(1)


if __name__ == "__main__":
    main()
