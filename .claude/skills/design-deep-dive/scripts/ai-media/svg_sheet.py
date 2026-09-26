#!/usr/bin/env python3
"""svg_sheet.py — разбор SVG (Recraft, LLM → SVG): метрики, гигиена с сохранением подписи, листы на светлом и тёмном фоне.

Агент A, сессия 4, 25.09.2026 (этап 2: CM-01, CM-03, CM-11, G-01…G-18). Запуск — `99-raw/tools/venv-G/bin/python`
(cairosvg, numpy, Pillow); svgo 4.1.0 — `99-raw/tools/node/node_modules/.bin/svgo` с конфигом G/02 `keep-signature`.

  venv-G/bin/python svg_sheet.py sheet SVG… --out DIR [--palette "#0E1417,#F1E5DB,…"] [--mode icons|illustration]
        [--light "#F1E5DB"] [--dark "#0E1417"] [--sizes 16,24,48] [--cells 4] [--blind]
  venv-G/bin/python svg_sheet.py render SVG --png 1024 --out FILE.png      # растр для референса (CM-03)

Метрики (на файл): байты исходника; `<path>`; узлы (команды в `d`); уникальные заливки; ΔE00 каждой заливки к ближайшему цвету
палитры (медиана, максимум) и доля **площади** (растр 512 px, без фона) с ΔE00 ≤ 3; подпись `<recraft-signature>` до и после;
гигиена G/02: корень (без `preserveAspectRatio="none"`, пиксельных размеров), фон-прямоугольник первым путём → svgo
`multipass` + `floatPrecision: 1` с сохранением подписи → байты после. Листы: `--mode icons` — весь набор в ширинах, при которых
одна иконка ≈ 16/24/48 px (`--cells` — иконок в ряду), на светлом и тёмном; `--mode illustration` — 1440 px на светлом и тёмном.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))  # перенос: edit_check.py — рядом
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
from edit_check import de2000, srgb_to_lab  # noqa: E402

SVGO = kbpaths.node_modules(".bin", "svgo")
SVGO_CFG = kbpaths.data("ai-media", "svgo.keep-signature.config.mjs")
NODE_BIN = os.path.dirname(kbpaths.node())


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def to_lab(rgb) -> np.ndarray:
    a = np.asarray(rgb, np.float64).reshape(-1, 3) / 255.0
    return srgb_to_lab(a)


def fills(txt: str) -> list[tuple[int, int, int]]:
    out = set()
    for m in re.finditer(r'fill="rgb\((\d+),\s*(\d+),\s*(\d+)\)"', txt):
        out.add(tuple(int(x) for x in m.groups()))
    for m in re.finditer(r'fill="(#[0-9a-fA-F]{3,6})"', txt):
        out.add(hex_rgb(m.group(1)))
    for m in re.finditer(r'fill:\s*(#[0-9a-fA-F]{3,6})', txt):
        out.add(hex_rgb(m.group(1)))
    return sorted(out)


def fix_root(txt: str) -> str:
    m = re.search(r"<svg\b[^>]*>", txt)
    if not m:
        return txt
    root = m.group(0)
    return txt.replace(root, re.sub(r'\s(preserveAspectRatio|width|height|style)="[^"]*"', "", root), 1)


def drop_bg(txt: str) -> tuple[str, bool]:
    vbm = re.search(r'viewBox="([^"]+)"', txt)
    if not vbm:
        return txt, False
    vb = [float(v) for v in vbm.group(1).replace(",", " ").split()]
    for m in re.finditer(r"<path\b[^>]*?(?:/>|>\s*</path>)", txt):
        el = m.group(0)
        dm = re.search(r'\sd="([^"]+)"', el)
        if not dm:
            break
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", dm.group(1))]
        xs, ys = nums[0::2], nums[1::2]
        if not xs or not ys:
            break
        full = min(xs) <= vb[0] + 1 and min(ys) <= vb[1] + 1 and max(xs) >= vb[0] + vb[2] - 1 and max(ys) >= vb[1] + vb[3] - 1
        col = re.search(r'fill="rgb\((\d+),\s*(\d+),\s*(\d+)\)"', el) or re.search(r'fill="(#[0-9a-fA-F]{3,6})"', el)
        rgb = tuple(int(c) for c in col.groups()) if col and len(col.groups()) == 3 else (hex_rgb(col.group(1)) if col else None)
        if full and rgb:
            return txt.replace(el, "", 1), True       # фон — первый путь на весь холст (любого цвета: у «Перламутра» фон тёплый)
        break
    return txt, False


def raster(txt: str, w: int, bg=None) -> Image.Image:
    png = cairosvg.svg2png(bytestring=txt.encode(), output_width=w)
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    if bg is None:
        return im
    base = Image.new("RGBA", im.size, (*hex_rgb(bg), 255))
    return Image.alpha_composite(base, im).convert("RGB")


def svgo(src: Path, dst: Path) -> int:
    env = dict(os.environ, PATH=NODE_BIN + ":" + os.environ.get("PATH", ""))
    subprocess.run([str(SVGO), str(src), "-o", str(dst), "--config", str(SVGO_CFG), "--quiet"], check=True, env=env)
    return dst.stat().st_size


def analyze(path: Path, palette: list[str], clean_dir: Path) -> dict:
    txt = path.read_text(encoding="utf-8", errors="replace")
    r = {"file": path.name, "bytes_raw": len(txt.encode()), "signature_raw": "recraft-signature" in txt,
         "paths": len(re.findall(r"<path\b", txt)), "shapes": len(re.findall(r"<(path|circle|rect|ellipse|polygon|polyline|line)\b", txt)),
         "nodes": sum(len(re.findall(r"[MLHVCSQTAZmlhvcsqtaz]", d)) for d in re.findall(r'\sd="([^"]+)"', txt)),
         "strokes": len(re.findall(r'stroke="(?!none)', txt)), "gradients": len(re.findall(r"<(linear|radial)Gradient", txt))}
    fl = fills(txt)
    r["fills_unique"] = len(fl)
    if palette and fl:
        pl = to_lab([hex_rgb(p) for p in palette])
        fd = []
        for c in fl:
            d = de2000(np.repeat(to_lab([c]), len(pl), 0), pl)
            fd.append(float(np.min(d)))
        r["fill_dE00_median"] = round(float(np.median(fd)), 2)
        r["fill_dE00_max"] = round(float(np.max(fd)), 2)
        # доля площади (без фона-прямоугольника) с ΔE00 ≤ 3 к палитре
        t_nobg, _ = drop_bg(fix_root(txt))
        im = np.asarray(raster(t_nobg, 256))
        a = im[:, :, 3] > 200
        px = im[:, :, :3][a].reshape(-1, 3)
        if len(px):
            if len(px) > 20000:
                px = px[np.random.default_rng(1).choice(len(px), 20000, replace=False)]
            lab = to_lab(px)
            dmin = np.min(np.stack([de2000(lab, np.repeat(pl[i:i + 1], len(lab), 0)) for i in range(len(pl))]), 0)
            r["area_share_dE00_le3"] = round(float((dmin <= 3).mean()), 3)
    t2, had_bg = drop_bg(fix_root(txt))
    r["bg_rect_removed"] = had_bg
    clean_dir.mkdir(parents=True, exist_ok=True)
    pre = clean_dir / (path.stem + ".pre.svg")
    pre.write_text(t2, encoding="utf-8")
    out = clean_dir / (path.stem + ".clean.svg")
    try:
        r["bytes_clean_svgo"] = svgo(pre, out)
        r["signature_kept"] = "recraft-signature" in out.read_text(encoding="utf-8", errors="replace")
        r["svgo_saving_pct"] = round(100 * (1 - r["bytes_clean_svgo"] / r["bytes_raw"]), 1)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        r["svgo_error"] = str(e)[:160]
    finally:
        pre.unlink(missing_ok=True)
    return r


def font(sz):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def cmd_sheet(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    palette = [p.strip() for p in a.palette.split(",")] if a.palette else []
    files = [Path(f) for f in a.svgs]
    codes = list(range(1, len(files) + 1))
    if a.blind:
        random.Random(20260925).shuffle(codes)
    rows, key = [], {}
    for code, f in sorted(zip(codes, files)):
        m = analyze(f, palette, out / "clean")
        m["code"] = code
        rows.append((m, f))
        key[str(code)] = str(f)
    tiles = []
    for m, f in rows:
        clean = out / "clean" / (f.stem + ".clean.svg")
        txt = (clean if clean.exists() else f).read_text(encoding="utf-8", errors="replace")
        if a.mode == "icons":
            ws = [int(s * a.cells * 1.5) for s in a.sizes]          # ширина рендера, при которой иконка ≈ s px
            parts = [raster(txt, w, bg) for bg in (a.light, a.dark) for w in ws]
            big = [raster(txt, 960, a.light), raster(txt, 960, a.dark)]
            parts = parts + big
        else:
            parts = [raster(txt, 1440, a.light), raster(txt, 1440, a.dark)]
        tiles.append((m, parts))
    pad, lab_h = 16, 40
    W = max(sum(p.width for p in parts) + pad * (len(parts) + 1) if a.mode == "icons" else max(p.width for p in parts) + 2 * pad
            for _, parts in tiles)
    if a.mode == "icons":
        H = sum(lab_h + max(p.height for p in parts) + pad for _, parts in tiles)
    else:
        H = sum(lab_h + sum(p.height for p in parts) + pad * 3 for _, parts in tiles)
    sheet = Image.new("RGB", (W, H), (128, 128, 128))
    d = ImageDraw.Draw(sheet)
    y = 0
    for m, parts in tiles:
        lab = f"#{m['code']}" if a.blind else (f"#{m['code']} {m['file']} · пути {m['paths']} · узлы {m['nodes']} · заливок "
                                               f"{m['fills_unique']} · ΔE00 мед. {m.get('fill_dE00_median')} · площадь ≤3: "
                                               f"{m.get('area_share_dE00_le3')} · {m['bytes_raw']//1024} → "
                                               f"{(m.get('bytes_clean_svgo') or 0)//1024} КБ · подпись {m.get('signature_kept')}")
        d.text((pad, y + 10), lab, fill=(255, 255, 255), font=font(18))
        y += lab_h
        if a.mode == "icons":
            x = pad
            for p in parts:
                sheet.paste(p, (x, y))
                x += p.width + pad
            y += max(p.height for p in parts) + pad
        else:
            for p in parts:
                sheet.paste(p, (pad, y))
                y += p.height + pad
            y += pad
    sheet.save(out / "sheet.png", optimize=True)
    js = [m for m, _ in rows]
    (out / "metrics.json").write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.blind:
        (out / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
    cols = ["code", "file", "bytes_raw", "bytes_clean_svgo", "svgo_saving_pct", "signature_kept", "paths", "nodes",
            "fills_unique", "strokes", "gradients", "fill_dE00_median", "fill_dE00_max", "area_share_dE00_le3", "bg_rect_removed"]
    md = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    md += ["| " + " | ".join("" if m.get(c) is None else str(m.get(c)) for c in cols) + " |" for m in js]
    (out / "metrics.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(out / "sheet.png")
    print("\n".join(md))


def cmd_recolor(a):
    """Каждая заливка → ближайший цвет палитры (ΔE00); `--swap "#0E1417=#F1E5DB,…"` — вариант тёмной темы после приведения."""
    txt = Path(a.svg).read_text(encoding="utf-8", errors="replace")
    pal = [p.strip() for p in a.palette.split(",")]
    pl = to_lab([hex_rgb(p) for p in pal])
    swap = dict(kv.split("=") for kv in a.swap.split(",")) if a.swap else {}
    report = []

    def nearest(rgb):
        d = de2000(np.repeat(to_lab([rgb]), len(pl), 0), pl)
        i = int(np.argmin(d))
        return pal[i], float(d[i])

    def sub(m):                                          # один проход: rgb() и hex вместе (иначе swap применился бы дважды)
        rgb = tuple(int(x) for x in m.group(1, 2, 3)) if m.group(1) else hex_rgb(m.group(4))
        h, d = nearest(rgb)
        h = swap.get(h, h)
        report.append({"from": "#%02X%02X%02X" % rgb, "to": h, "dE00": round(d, 2)})
        return f'fill="{h}"'

    out = re.sub(r'fill="(?:rgb\((\d+),\s*(\d+),\s*(\d+)\)|(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}))"', sub, txt)
    Path(a.out).write_text(out, encoding="utf-8")
    uniq = {(r["from"], r["to"]): r["dE00"] for r in report}
    print(json.dumps({"out": a.out, "fills": len(report), "map": [{"from": f, "to": t, "dE00": d} for (f, t), d in sorted(uniq.items())],
                      "max_shift_dE00": max(uniq.values()) if uniq else None}, ensure_ascii=False, indent=1))


def cmd_render(a):
    txt = Path(a.svg).read_text(encoding="utf-8", errors="replace")
    im = raster(fix_root(txt), a.png, a.bg) if a.bg else raster(fix_root(txt), a.png)
    im.save(a.out)
    print(a.out, im.size)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("sheet")
    s.add_argument("svgs", nargs="+")
    s.add_argument("--out", required=True)
    s.add_argument("--palette")
    s.add_argument("--mode", choices=["icons", "illustration"], default="illustration")
    s.add_argument("--light", default="#F1E5DB")
    s.add_argument("--dark", default="#0E1417")
    s.add_argument("--sizes", type=lambda v: [int(x) for x in v.split(",")], default=[16, 24, 48])
    s.add_argument("--cells", type=int, default=4, help="иконок в ряду набора")
    s.add_argument("--blind", action="store_true")
    s.set_defaults(fn=cmd_sheet)
    s = sp.add_parser("recolor")
    s.add_argument("svg")
    s.add_argument("--palette", required=True)
    s.add_argument("--swap", help='тёмная тема: "#0E1417=#F1E5DB,#F1E5DB=#0E1417"')
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_recolor)
    s = sp.add_parser("render")
    s.add_argument("svg")
    s.add_argument("--png", type=int, default=1024)
    s.add_argument("--bg")
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_render)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
