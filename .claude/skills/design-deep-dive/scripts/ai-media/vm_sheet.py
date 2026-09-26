#!/usr/bin/env python3
"""vm_sheet.py — лист видео-моделей: кадры 0/25/50/75/100 %, метрики `video_loop_check.py`, цена и время из паспорта.

Агент A, сессия 4, 25.09.2026 (этап 2: разбор VM-*, D2-07/D2-08/D2-11, MS-03). Лёгкий: кадры для метрик — 320 px в градациях
серого (как `video_loop_check.py loop`), кадры листа — ffmpeg по времени; память < 300 МБ на ролик 720p.

  python3 vm_sheet.py ВИДЕО… --out DIR [--start КАДР.png] [--blind] [--frame-w 640] [--x3] [--title "…"]

Выход в DIR: `sheet.jpg` (строка на ролик: 5 кадров по `--frame-w` px + подпись; при `--blind` — только номер, ключ —
`key.json`), `frames/<код>_<процент>.png` (кадры в полном размере), `metrics.md` и `metrics.json` (модель, ₽ факт и оценка,
время генерации, размер, к/с, длительность, звук, motion_med, cut_ratio, seam_ratio_local, static_frac, SSIM кадра 0 к
стартовому), при `--x3` — `x3/<код>_x3.mp4` (ролик трижды подряд, без звука — смотреть петлю/стык).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))  # перенос: video_loop_check.py — рядом
import video_loop_check as vlc  # noqa: E402

PCTS = (0, 25, 50, 75, 100)


def passport_for(video: Path) -> dict:
    for cand in (video.with_suffix(".passport.json"), video.with_name(video.stem.rsplit("_", 1)[0] + ".passport.json")):
        if cand.exists():
            try:
                return json.loads(cand.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
    return {}


def font(sz):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def grab(video: Path, t: float, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", "-ss", f"{max(t, 0):.3f}", "-i", str(video),
                    "-frames:v", "1", "-update", "1", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", help="стартовый кадр (SSIM кадра 0)")
    ap.add_argument("--blind", action="store_true")
    ap.add_argument("--frame-w", type=int, default=640)
    ap.add_argument("--x3", action="store_true")
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    out = Path(a.out)
    (out / "frames").mkdir(parents=True, exist_ok=True)
    vids = [Path(v) for v in a.videos]
    codes = list(range(1, len(vids) + 1))
    if a.blind:
        random.Random(20260925).shuffle(codes)
    start_g = None
    if a.start:
        im = Image.open(a.start).convert("RGB")
        h = int(round(im.height * 320 / im.width / 2) * 2)
        start_g = np.asarray(im.resize((320, h), Image.BOX), np.float32) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    rows, key = [], {}
    for code, v in sorted(zip(codes, vids)):
        p = vlc.probe(str(v))
        dur = float(p.get("duration_s") or p.get("duration") or 0) or 4.0
        fps = p.get("fps") or 24
        ps = passport_for(v)
        job = ps.get("job") or {}
        m = {}
        try:
            fr = vlc.load(str(v), 320)
            rgb = vlc.load(str(v), 96, "rgb")
            m = vlc.loop_metrics(fr, 0.25, rgb, vlc.src_width(str(v)) / 320)
            m.pop("_curve", None)
            if hasattr(vlc, "verdict"):
                m["verdict"] = vlc.verdict(m)
            if start_g is not None:
                sg = start_g
                if fr.shape[1:] != sg.shape:          # другое соотношение/округление (480p 864×496) — приводим размер
                    sg = np.asarray(Image.fromarray(start_g.astype(np.uint8)).resize((fr.shape[2], fr.shape[1]), Image.BOX),
                                    np.float32)
                m["ssim_frame0_to_start"] = round(vlc.ssim(fr[0], sg), 3)
        except Exception as e:  # noqa: BLE001 — лист строим и без метрик
            m = {"error": str(e)[:200]}
        frames = []
        for pct in PCTS:
            t = (dur - 1.0 / float(fps if isinstance(fps, (int, float)) else 24)) * pct / 100
            fp = out / "frames" / f"{code:02d}_{pct:03d}.png"
            grab(v, t, fp)
            frames.append(fp)
        cost = (ps.get("cost") or {}).get("usage_cost_rub")
        est = (ps.get("cost") or {}).get("estimate_rub")
        wall = (ps.get("timing") or {}).get("wall_s")
        audio = ",".join(p.get("audio") or []) or "нет"
        row = {"code": code, "file": str(v), "tag": job.get("tag"), "model": ps.get("model") or job.get("model")
               or (ps.get("request") or {}).get("body", {}).get("model"), "cost_rub": cost, "estimate_rub": est,
               "wall_s": wall, "w": p.get("w"), "h": p.get("h"), "fps": fps, "dur": round(dur, 2), "audio": audio,
               **{k: m.get(k) for k in ("motion_med", "cut_ratio", "seam_ratio_local", "seam_ratio", "static_frac",
                                        "pingpong_suspect", "collapse_suspect", "ssim_frame0_to_start", "verdict", "error")}}
        rows.append((row, frames))
        key[str(code)] = {"tag": row["tag"], "model": row["model"], "file": row["file"]}
        if a.x3:
            (out / "x3").mkdir(exist_ok=True)
            lst = out / "x3" / f"{code:02d}.txt"
            lst.write_text("".join(f"file '{v.resolve()}'\n" for _ in range(3)), encoding="utf-8")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", "-f", "concat", "-safe", "0", "-i", str(lst), "-an",
                            "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                            str(out / "x3" / f"{code:02d}_x3.mp4")], check=True)
            lst.unlink()
    # лист
    fw = a.frame_w
    heads = []
    for row, frames in rows:
        ims = [Image.open(f).convert("RGB") for f in frames]
        hh = int(round(ims[0].height * fw / ims[0].width))
        heads.append((row, [im.resize((fw, hh), Image.LANCZOS) for im in ims], hh))
    label_h = 44
    W = fw * len(PCTS)
    H = sum(hh + label_h for _, _, hh in heads) + (60 if a.title else 0)
    sheet = Image.new("RGB", (W, H), (22, 22, 22))
    d = ImageDraw.Draw(sheet)
    y = 0
    if a.title:
        d.text((16, 16), a.title, fill=(235, 235, 235), font=font(26))
        y = 60
    f18 = font(20)
    for row, ims, hh in heads:
        if a.blind:
            lab = f"#{row['code']}"
        else:
            c = row["cost_rub"] if row["cost_rub"] is not None else row["estimate_rub"]
            lab = (f"#{row['code']}  {row['model']}  ·  {c} ₽  ·  {row['wall_s']} с  ·  {row['w']}×{row['h']} {row['fps']} к/с "
                   f"{row['dur']} с  ·  движение {row['motion_med']}  шов {row['seam_ratio_local']}  SSIM0 {row['ssim_frame0_to_start']}")
        d.text((12, y + 10), lab, fill=(235, 235, 235), font=f18)
        y += label_h
        for i, im in enumerate(ims):
            sheet.paste(im, (i * fw, y))
        y += hh
    sheet.save(out / "sheet.jpg", quality=90)
    js = [r for r, _ in rows]
    (out / "metrics.json").write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.blind:
        (out / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
    cols = ["code", "model", "cost_rub", "wall_s", "w", "h", "fps", "dur", "audio", "motion_med", "cut_ratio",
            "seam_ratio_local", "static_frac", "ssim_frame0_to_start", "verdict"]
    md = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in js:
        md.append("| " + " | ".join("" if r.get(c) is None else str(r.get(c)) for c in cols) + " |")
    (out / "metrics.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(out / "sheet.jpg")
    print("\n".join(md))


if __name__ == "__main__":
    main()
