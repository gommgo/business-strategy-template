#!/usr/bin/env python3
"""scroll_record.py — запись прокрутки страницы и движение в паузах (creative-research, волна 1, агент C, 2026-09-24).

Сценарий (Playwright + Chromium, запись record_video_dir):
  load → --wait мс → синхровспышка (полноэкранный пурпурный слой 400 мс — по нему видео сопоставляется со временем
  скрипта) → пауза на первом экране (--dwell) → --steps шагов колесом мыши; после каждого шага ждём, пока прокрутка
  успокоится (scrollY не меняется 250 мс, но не дольше 1,6 с — у плавной прокрутки Lenis хвост ≈ 1,2 с), затем пауза
  --dwell секунд → хвост 1 с → закрытие контекста (видео сохраняется).
Нарезка (ffmpeg, -threads 4): видео читается потоком 4 кадра/с в 320 px по ширине (rawvideo → numpy):
  * по каждой паузе (секции): доля меняющихся пикселей между соседними кадрами (порог 12/255, шум сжатия < 0,2 %
    отбрасывается), число одновременно движущихся областей (связные компоненты маски разницы на сетке 8×8 px,
    8-связность, ≥ 2 блоков), «непрерывность» (движение в ≥ 60 % пар кадров паузы);
  * кадры для просмотра — раз в 0,5 с и по смене сцены (разница > 35 % пикселей), почти одинаковые соседние кадры
    выбрасываются; контактные листы 4×4 (миниатюры 320×200, подпись «время · scrollY · шаг») ≤ ≈ 1 МБ на запись.
Видео удаляется после нарезки (--keep-video — только для отладки).

Использование:
  python3 scroll_record.py URL OUT_DIR [--mobile] [--reduced-motion] [--steps 12] [--dwell 1.5] [--wait 6000]
                           [--locale en-US] [--timeout 150] [--keep-video] [--tmpdir DIR]
Выход: OUT_DIR/record[_mobile][_rm].json, OUT_DIR/sheet[_mobile][_rm]_NN.jpg; одна строка JSON-сводки в stdout.
Браузер — только под двумя блокировками (см. effects_probe.py). UA не подделывается (как в effects_probe.py).
Проверено: 99-raw/experiments/C/05-scroll-record/ (статичная страница → 0 %, лабораторная — движение по секциям).
"""
import argparse, glob, io, json, math, os, shutil, subprocess, sys, tempfile, time

VERSION = "scroll_record.py 1.0 (2026-09-24)"
# как в effects_probe.py (с 17:10 24.09 — и WebGPU; до этого записи шли без WebGPU-флагов)
GPU_ARGS = ["--use-gl=angle", "--use-angle=gl", "--ignore-gpu-blocklist", "--enable-gpu", "--enable-unsafe-webgpu", "--enable-features=Vulkan"]
FPS = 4          # кадров в секунду для анализа
AW = 320         # ширина кадра анализа
THR = 12         # порог изменения канала
NOISE = 0.2      # %: ниже — шум сжатия


def ffprobe_size(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
                       capture_output=True, text=True, timeout=60)
    w, h = (int(x) for x in p.stdout.strip().split(",")[:2])
    return w, h


def read_frames(path, fps=FPS, width=AW):
    """Поток кадров rawvideo rgb24 → список numpy-массивов (H, W, 3) uint8."""
    import numpy as np
    w0, h0 = ffprobe_size(path)
    h = int(round(h0 * width / w0 / 2)) * 2
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-threads", "4", "-i", path, "-vf", f"fps={fps},scale={width}:{h}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.run(cmd, capture_output=True, timeout=900)
    buf = p.stdout; n = len(buf) // (width * h * 3)
    return [np.frombuffer(buf, dtype=np.uint8, count=width * h * 3, offset=i * width * h * 3).reshape(h, width, 3) for i in range(n)], (width, h)


def diff_regions(a, b, block=8):
    import numpy as np
    m = (np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2) > THR)
    pct = 100.0 * m.mean()
    H, W = m.shape; gh, gw = H // block, W // block
    g = m[:gh * block, :gw * block].reshape(gh, block, gw, block).mean(axis=(1, 3)) > 0.05
    seen = np.zeros_like(g, dtype=bool); regions = 0
    for y in range(gh):
        for x in range(gw):
            if g[y, x] and not seen[y, x]:
                st = [(y, x)]; seen[y, x] = True; n = 0
                while st:
                    cy, cx = st.pop(); n += 1
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < gh and 0 <= nx < gw and g[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True; st.append((ny, nx))
                if n >= 2:
                    regions += 1
    return pct, regions


def _is_flash(f):
    c = f.reshape(-1, 3).mean(axis=0)
    return c[0] > 200 and c[1] < 70 and c[2] > 200


def find_flash(frames, path=None, fps=FPS):
    """Время (с) первого пурпурного кадра: грубо по кадрам 4/с, затем уточнение 25 кадров/с в окне ±0,5 с."""
    import numpy as np
    coarse = next((i / fps for i, f in enumerate(frames[: fps * 90]) if _is_flash(f)), None)
    if coarse is None or not path:
        return coarse
    try:
        w0, h0 = ffprobe_size(path); w = 64; h = max(2, int(round(h0 * w / w0 / 2)) * 2)
        s = max(0.0, coarse - 0.5)
        p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{s:.3f}", "-i", path, "-t", "1.0", "-vf", f"fps=25,scale={w}:{h}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, timeout=120)
        n = len(p.stdout) // (w * h * 3)
        for i in range(n):
            f = np.frombuffer(p.stdout, dtype=np.uint8, count=w * h * 3, offset=i * w * h * 3).reshape(h, w, 3)
            if _is_flash(f):
                return round(s + i / 25, 3)
    except Exception:
        pass
    return coarse


def sheet(items, out, labels, cols=4, rows=4, tw=320, th=200, quality=70):
    from PIL import Image, ImageDraw
    lab = 16
    s = Image.new("RGB", (cols * tw, rows * (th + lab)), (18, 18, 18)); d = ImageDraw.Draw(s)
    for k, (im, lb) in enumerate(zip(items, labels)):
        x, y = (k % cols) * tw, (k // cols) * (th + lab)
        t = Image.fromarray(im); t.thumbnail((tw, th)); s.paste(t, (x + (tw - t.width) // 2, y + lab))
        d.text((x + 4, y + 2), lb, fill=(235, 220, 120))
    s.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
    return out


def main():
    ap = argparse.ArgumentParser(description="запись прокрутки и движение в паузах")
    ap.add_argument("url"); ap.add_argument("out")
    ap.add_argument("--mobile", action="store_true"); ap.add_argument("--reduced-motion", action="store_true")
    ap.add_argument("--steps", type=int, default=12); ap.add_argument("--dwell", type=float, default=1.5)
    ap.add_argument("--wait", type=int, default=6000); ap.add_argument("--locale", default="en-US")
    ap.add_argument("--timeout", type=int, default=150); ap.add_argument("--keep-video", action="store_true")
    ap.add_argument("--slug"); ap.add_argument("--tmpdir", default=None, help="куда писать временное видео (по умолчанию системный tmp)")
    a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    suffix = ("_mobile" if a.mobile else "") + ("_rm" if a.reduced_motion else "")
    vdir = tempfile.mkdtemp(prefix="scroll_record_", dir=a.tmpdir)
    st = {"tool": VERSION, "url": a.url, "mode": suffix.strip("_") or "desktop", "date": time.strftime("%Y-%m-%d %H:%M"), "steps": a.steps,
          "dwell_s": a.dwell, "wait_ms": a.wait, "locale": a.locale, "log": []}
    ev = []  # (t_отн, событие, данные)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=GPU_ARGS)
        st["browser"] = b.version
        rm = "reduce" if a.reduced_motion else "no-preference"
        if a.mobile:
            dev = dict(pw.devices["Pixel 7"]); dev["user_agent"] = dev["user_agent"].replace("Chrome/", "HeadlessChrome/")
            vsize = {"width": 412, "height": 839}
            ctx = b.new_context(**dev, reduced_motion=rm, locale=a.locale, record_video_dir=vdir, record_video_size=vsize)
        else:
            vsize = {"width": 960, "height": 600}
            ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1, reduced_motion=rm, locale=a.locale,
                                record_video_dir=vdir, record_video_size=vsize)
        p = ctx.new_page(); T0 = time.time()
        W, H = p.viewport_size["width"], p.viewport_size["height"]
        st["viewport"] = [W, H]; st["video_size"] = [vsize["width"], vsize["height"]]
        rel = lambda: round(time.time() - T0, 3)
        try:
            resp = p.goto(a.url, wait_until="load", timeout=a.timeout * 1000); st["status"] = resp.status if resp else None
        except Exception as e:
            st["log"].append(f"goto: {str(e)[:160]}")
        ev.append((rel(), "loaded", None))
        p.wait_for_timeout(a.wait)
        # синхровспышка
        try:
            p.evaluate("""(() => { const d = document.createElement('div'); d.id = '__rec_flash';
              d.style.cssText = 'position:fixed;inset:0;background:#ff00ff;z-index:2147483647;pointer-events:none';
              document.documentElement.appendChild(d); })()""")
            tf = rel(); p.wait_for_timeout(400)
            p.evaluate("(() => { const d = document.getElementById('__rec_flash'); if (d) d.remove(); })()")
            ev.append((tf, "flash", None))
        except Exception as e:
            st["log"].append(f"flash: {str(e)[:120]}")
        p.wait_for_timeout(300)
        try:
            total = p.evaluate("Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0) - innerHeight")
        except Exception:
            total = 0
        native = total > H * 0.5
        delta = max(200, int(total / a.steps)) if native else 450
        st["doc_scrollable_px"] = total; st["scroll_mode"] = "native" if native else "virtual/none"; st["wheel_delta"] = delta
        p.mouse.move(W / 2, H / 2)
        windows = []

        def dwell(step):
            y = p.evaluate("Math.round(scrollY)")
            t0 = rel(); p.wait_for_timeout(int(a.dwell * 1000)); t1 = rel()
            windows.append({"step": step, "y": y, "t0": t0, "t1": t1})
        dwell(0)
        for s in range(1, a.steps + 1):
            tw = rel(); p.mouse.wheel(0, delta)
            last, stable_since, settle = None, None, None
            for k in range(16):
                p.wait_for_timeout(100)
                y = p.evaluate("Math.round(scrollY)")
                if y == last:
                    if stable_since is None:
                        stable_since = rel()
                    elif rel() - stable_since >= 0.25:
                        settle = round(stable_since - tw, 2); break
                else:
                    stable_since = None
                last = y
            ev.append((tw, "wheel", {"step": s, "settle_s": settle}))
            dwell(s)
            if time.time() - T0 > a.timeout + 60:
                st["log"].append("deadline"); break
        p.wait_for_timeout(1000)
        try:
            st["title"] = p.title()
        except Exception:
            pass
        video = p.video
        ctx.close()
        vpath = video.path() if video else None
        b.close()
    st["events"] = ev; st["windows"] = windows
    if not vpath or not os.path.exists(vpath):
        st["error"] = "нет видео"
    else:
        st["video_mb"] = round(os.path.getsize(vpath) / 1e6, 2)
        frames, (fw, fh) = read_frames(vpath)
        st["frames_analyzed"] = len(frames)
        vf = find_flash(frames, vpath)
        tf = next((t for t, e, _ in ev if e == "flash"), None)
        off = round(vf - tf, 3) if (vf is not None and tf is not None) else 0.0
        st["sync"] = {"flash_video_s": vf, "flash_script_s": tf, "offset_s": off}
        # движение по паузам
        for w in windows:
            # окно паузы без краёв: +0,25 с после успокоения, −0,35 с до следующего шага (точность синхронизации ≈ 40 мс,
            # запаздывание кадров скринкаста до ≈ 250 мс)
            i0 = int(math.ceil((w["t0"] + off + 0.25) * FPS)); i1 = int(math.floor((w["t1"] + off - 0.35) * FPS))
            pcts, regs = [], []
            for i in range(max(1, i0 + 1), min(len(frames), i1 + 1)):
                pc, rg = diff_regions(frames[i - 1], frames[i])
                pcts.append(pc); regs.append(rg if pc >= NOISE else 0)
            moving = [pc for pc in pcts if pc >= NOISE]
            w.update({"pairs": len(pcts), "pct_mean": round(sum(pcts) / len(pcts), 2) if pcts else None, "pct_max": round(max(pcts), 2) if pcts else None,
                      "regions_max": max(regs) if regs else 0, "continuous": bool(pcts) and len(moving) >= 0.6 * len(pcts)})
        ws = [w for w in windows if w.get("pairs")]
        st["summary"] = {
            "windows": len(ws),
            "motion_idle_max": max((w["pct_mean"] for w in ws), default=None),
            "motion_idle_median": sorted(w["pct_mean"] for w in ws)[len(ws) // 2] if ws else None,
            "regions_max": max((w["regions_max"] for w in ws), default=0),
            "regions_median": sorted(w["regions_max"] for w in ws)[len(ws) // 2] if ws else None,
            "windows_moving": sum(1 for w in ws if w["continuous"]),
            "windows_moving_pct": round(100 * sum(1 for w in ws if w["continuous"]) / len(ws), 1) if ws else None,
            "hero_moving": bool(ws and ws[0]["continuous"]), "hero_pct": ws[0]["pct_mean"] if ws else None, "hero_regions": ws[0]["regions_max"] if ws else None,
            "settle_s_median": (lambda xs: sorted(xs)[len(xs) // 2] if xs else None)([d["settle_s"] for t, e, d in ev if e == "wheel" and d and d.get("settle_s") is not None]),
        }
        # кадры для листов: раз в 0,5 с + смена сцены, без почти одинаковых соседей
        import numpy as np
        keep, labels, prev = [], [], None
        wins = sorted(windows, key=lambda w: w["t0"])

        def label(t):
            ts = t - off; y = None; stp = None
            for w in wins:
                if w["t0"] - 0.05 <= ts:
                    y, stp = w["y"], w["step"]
            return f"{t:5.1f}s load" if stp is None else f"{t:5.1f}s y={y} s{stp}"
        t_first = (wins[0]["t0"] + off) if wins else 0.0
        for i, f in enumerate(frames):
            t = i / FPS
            scene = i > 0 and diff_regions(frames[i - 1], f)[0] > 35
            if t < t_first - 0.5 and i % (FPS * 2):
                continue  # загрузка до первой паузы — кадр раз в 2 с
            if i % (FPS // 2) and not scene:
                continue
            c = f.reshape(-1, 3).mean(axis=0)
            if c[0] > 200 and c[1] < 70 and c[2] > 200:
                continue  # кадр синхровспышки
            sig = f[::8, ::8].astype(np.int16)
            if prev is not None and np.abs(sig - prev).mean() < 1.5 and not scene:
                continue
            prev = sig; keep.append(f); labels.append(label(t) + (" scene" if scene else ""))
        import re as _re
        for old in glob.glob(os.path.join(out, f"sheet{suffix}_*.jpg")):
            if _re.fullmatch(rf"sheet{suffix}_\d+\.jpg", os.path.basename(old)):
                os.remove(old)
        per = 16; sheets = []
        q = 70
        for k in range(0, len(keep), per):
            sheets.append(os.path.basename(sheet(keep[k:k + per], os.path.join(out, f"sheet{suffix}_{k // per + 1:02d}.jpg"), labels[k:k + per], quality=q)))
        tot = sum(os.path.getsize(os.path.join(out, s)) for s in sheets)
        while tot > 1_000_000 and q > 40:
            q -= 10
            for k in range(0, len(keep), per):
                sheet(keep[k:k + per], os.path.join(out, f"sheet{suffix}_{k // per + 1:02d}.jpg"), labels[k:k + per], quality=q)
            tot = sum(os.path.getsize(os.path.join(out, s)) for s in sheets)
        st["sheets"] = sheets; st["sheets_kb"] = round(tot / 1024, 1); st["frames_kept"] = len(keep)
        if a.keep_video:
            shutil.copy(vpath, os.path.join(out, f"video{suffix}.webm"))
    shutil.rmtree(vdir, ignore_errors=True)
    json.dump(st, open(os.path.join(out, f"record{suffix}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    sm = st.get("summary") or {}
    print(json.dumps({"slug": a.slug or os.path.basename(out.rstrip("/")), "mode": st["mode"], "status": st.get("status"), "frames": st.get("frames_analyzed"),
                      "sheets": len(st.get("sheets") or []), "sheets_kb": st.get("sheets_kb"), "motion_idle_max": sm.get("motion_idle_max"),
                      "regions_max": sm.get("regions_max"), "windows_moving_pct": sm.get("windows_moving_pct"), "hero_moving": sm.get("hero_moving"),
                      "sync_offset_s": (st.get("sync") or {}).get("offset_s"), "video_mb": st.get("video_mb")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
