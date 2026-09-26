#!/usr/bin/env python3
"""provenance_check.py — бесплатная проверка провенанса ИИ-ассетов (0 ₽, без сети).

Агент L, волна 3, 23.09.2026. Что ищет в каждом файле (картинка, SVG, видео):
  * C2PA — через c2patool (validation_state, генератор, подписант, действия, digitalSourceType, ингредиенты, sidecar .c2pa);
  * IPTC/XMP — DigitalSourceType, AISystemUsed, AIPromptInformation, dcterms:provenance, Credit, Software… (exiftool -G1);
  * китайскую неявную метку AIGC (GB 45438-2025: Label/ContentProducer/ProduceID, подпись TC260PG) в тегах MP4/WebM;
  * подпись Recraft `<recraft-signature>` в SVG (signed_by, алгоритм, время, identifier);
  * строки-маркеры в байтах (c2pa, jumb, caBX, AIGC, SynthID, TC260, trainedAlgorithmicMedia…) — страховка на случай,
    если exiftool/c2patool не разобрали контейнер;
  * видимую метку в углах кадра — эвристика («строка символов» top-hat + плотность краёв; на фото ловит ≈ половину
    надписей, 1 ложное из 10) + контактный лист углов corners.jpg — главное средство, смотреть глазами или VLM (K).
SynthID и другие невидимые водяные знаки локально НЕ детектируются: для них — Gemini app / Google Search «Is this AI
generated?» (SynthID Google и OpenAI) и openai.com/verify (картинки OpenAI); утилита лишь подсказывает, где проверять.

Команды:
  python3 provenance_check.py scan PATH... [--out DIR] [--corners] [--trust] [--json F] [--md F]
      --trust — сверка подписи со списком доверия C2PA (кэш C2PA-TRUST-LIST.pem): «Trusted» только у подписантов из списка.
      PATH — файлы и/или каталоги (рекурсивно). Паспорт polza (*.passport.json рядом) подтягивается автоматически.
  python3 provenance_check.py stamp IN OUT --dst trained|composite [--system NAME] [--system-version V] [--credit TEXT]
      [--force]  — записать IPTC DigitalSourceType (≈1 КБ) в ПРОИЗВОДНУЮ (AVIF/WebP/JPEG/PNG/JXL/MP4/MOV — exiftool;
      WebM/MKV — ремукс ffmpeg с тегом). Файл с валидным C2PA не штампует без --force (правка ломает подпись).
  python3 provenance_check.py selftest [--keep DIR]

Выход scan: JSON (полные записи) и Markdown-таблица; при --corners — corners.jpg (углы TL TR / BL BR каждого файла).
Коды выхода: 0 — ок; 1 — ошибка аргументов/инструментов; 2 — selftest FAIL.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
EXIFTOOL = os.environ.get("EXIFTOOL", kbpaths.which("exiftool"))
C2PATOOL = os.environ.get("C2PATOOL", kbpaths.which("c2patool"))
# Официальный список доверия C2PA (снимок 23.09.2026, 30 корней: Google, DigiCert, SSL.com, Adobe, TrustAsia…) — даёт «Trusted»
TRUST_PEM = os.environ.get("C2PA_TRUST_PEM", str(kbpaths.cache("ai-media", "c2pa-trust-2026-09-23") / "C2PA-TRUST-LIST.pem"))
USE_TRUST = False
VERSION = "0.1.1 (L, 2026-09-23; C2PA в SVG — оркестратор, 2026-09-25)"

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".jxl", ".gif", ".tif", ".tiff", ".heic", ".heif", ".bmp"}
VID_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
SVG_EXT = {".svg"}
DST = {
    "trained": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
    "composite": "http://cv.iptc.org/newscodes/digitalsourcetype/compositeWithTrainedAlgorithmicMedia",
}
BYTE_TOKENS = [b"c2pa", b"jumb", b"caBX", b"AIGC", b"SynthID", b"TC260", b"trainedAlgorithmicMedia",
               b"compositeWithTrainedAlgorithmicMedia", b"recraft-signature", b"digitalsourcetype"]
META_KEYS = ("DigitalSourceType", "AISystemUsed", "AISystemVersionUsed", "AIPromptInformation", "AIPromptWriterName",
             "Provenance", "Credit", "Copyright", "Rights", "Software", "Artist", "Creator", "ImageDescription",
             "Description", "UserComment", "Comment", "Parameters", "Prompt", "Workflow", "AIGC", "Encoder",
             "Make", "Model", "CreatorTool", "Title")
CORNER_W, CORNER_H = 0.22, 0.12   # доля ширины и высоты кадра на угол (видимые метки вендоров — в углах)


# ------------------------------------------------------------------ утилиты
def run(cmd: list[str], timeout: int = 120) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    except FileNotFoundError as e:
        return 127, "", str(e)
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout {timeout}s"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def kind_of(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in SVG_EXT:
        return "svg"
    if ext in VID_EXT:
        return "video"
    if ext in IMG_EXT:
        return "image"
    return "other"


def byte_scan(path: Path, limit: int = 256 << 20) -> dict:
    counts = {t.decode(): 0 for t in BYTE_TOKENS}
    tail = b""
    read = 0
    with open(path, "rb") as f:
        while read < limit:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            buf = tail + chunk
            for t in BYTE_TOKENS:
                counts[t.decode()] += buf.count(t) - tail.count(t)
            tail = chunk[-64:]
            read += len(chunk)
    return {k: v for k, v in counts.items() if v}


def short(v, n=240):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…"


# ------------------------------------------------------------------ C2PA
def c2pa_read(path: Path) -> dict:
    out = {"present": False}
    if not Path(C2PATOOL).exists():
        return {"present": None, "error": "c2patool не найден"}
    sidecar = path.with_suffix(".c2pa")
    if sidecar.exists():
        out["sidecar"] = sidecar.name
    cmd = [C2PATOOL, str(path)]
    if USE_TRUST and Path(TRUST_PEM).exists():
        cmd += ["trust", "--trust_anchors", TRUST_PEM]
        out["trust_list"] = Path(TRUST_PEM).name
    rc, so, se = run(cmd)
    if rc != 0 or not so.strip().startswith("{"):
        msg = (se or so).strip().splitlines()
        msg = msg[-1] if msg else f"rc={rc}"
        if "No claim found" in msg or "no JUMBF" in msg.lower() or "not found" in msg.lower():
            out["note"] = "манифеста нет"
        else:
            out["error"] = short(msg, 200)
        return out
    try:
        d = json.loads(so)
    except json.JSONDecodeError as e:
        return {"present": None, "error": f"JSON c2patool: {e}"}
    out["present"] = True
    out["state"] = d.get("validation_state")
    codes = [s.get("code") for s in d.get("validation_status", []) or []]
    out["issues"] = codes
    mans = d.get("manifests") or {}
    out["manifests"] = len(mans)
    act = mans.get(d.get("active_manifest"), {}) if mans else {}
    gen = act.get("claim_generator")
    if not gen and act.get("claim_generator_info"):
        g = act["claim_generator_info"][0]
        gen = " ".join(str(x) for x in (g.get("name"), g.get("version")) if x)
    out["generator"] = gen
    si = act.get("signature_info") or {}
    out["signer"] = si.get("issuer") or si.get("common_name")
    out["signed_at"] = si.get("time")
    actions, dsts = [], set()
    for a in act.get("assertions", []) or []:
        if str(a.get("label", "")).startswith("c2pa.actions"):
            for x in (a.get("data") or {}).get("actions", []) or []:
                actions.append(x.get("action"))
                if x.get("digitalSourceType"):
                    dsts.add(x["digitalSourceType"].rsplit("/", 1)[-1])
    out["actions"] = actions
    out["digital_source_types"] = sorted(dsts)
    out["ingredients"] = len(act.get("ingredients", []) or [])
    rc2, so2, _ = run([C2PATOOL, str(path), "--info"])
    m = re.search(r"Manifest store size = (\d+) \(([\d.]+)% of file size", so2)
    if m:
        out["store_bytes"], out["store_pct"] = int(m.group(1)), float(m.group(2))
    return out


# ------------------------------------------------------------------ exiftool / ffprobe
def exif_read(path: Path) -> dict:
    if not Path(EXIFTOOL).exists():
        return {"error": "exiftool не найден"}
    rc, so, se = run([EXIFTOOL, "-j", "-a", "-G1", "-s", "-struct", "-api", "largefilesupport=1", str(path)])
    if rc not in (0, 1) or not so.strip().startswith("["):
        return {"error": short(se or so, 200)}
    try:
        d = json.loads(so)[0]
    except Exception as e:  # noqa: BLE001
        return {"error": f"JSON exiftool: {e}"}
    hits, groups = {}, set()
    for k, v in d.items():
        grp, _, tag = k.partition(":")
        groups.add(grp)
        if any(tag.endswith(x) or tag == x for x in META_KEYS):
            hits[k] = short(v)
    dst = [v for k, v in d.items() if k.endswith(":DigitalSourceType")]
    return {"hits": hits, "groups": sorted(g for g in groups if g not in ("SourceFile", "ExifTool", "System", "File")),
            "digital_source_type": [str(x).rsplit("/", 1)[-1] for x in dst],
            "jumbf": any(g.upper().startswith("JUMBF") or g.upper().startswith("C2PA") for g in groups)}


def ffprobe_read(path: Path) -> dict:
    rc, so, _ = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    if rc != 0:
        return {"error": "ffprobe"}
    d = json.loads(so)
    fmt = d.get("format", {})
    tags = dict(fmt.get("tags", {}) or {})
    streams = d.get("streams", [])
    for s in streams:
        for k, v in (s.get("tags") or {}).items():
            if k.lower() in ("aigc", "comment", "description", "title", "digitalsourcetype"):
                tags[f"stream{s.get('index')}:{k}"] = v
    aigc = None
    for k, v in tags.items():
        if k.split(":")[-1].lower() == "aigc" or "AIGC" in k:
            try:
                aigc = json.loads(v)
            except Exception:  # noqa: BLE001
                aigc = {"raw": short(v)}
    v = next((s for s in streams if s.get("codec_type") == "video"), {})
    return {"format": fmt.get("format_name"), "duration": float(fmt.get("duration", 0) or 0),
            "vcodec": v.get("codec_name"), "size": f"{v.get('width')}x{v.get('height')}",
            "audio": any(s.get("codec_type") == "audio" for s in streams),
            "tags": {k: short(val, 160) for k, val in tags.items()}, "aigc": aigc}


def svg_read(path: Path) -> dict:
    txt = path.read_text("utf-8", "replace")
    out = {"metadata_blocks": len(re.findall(r"<metadata\b", txt)), "recraft": None,
           "c2pa_manifest_blocks": len(re.findall(r"<c2pa:manifest\b", txt))}
    m = re.search(r"<recraft-signature>(.*?)</recraft-signature>", txt, re.S)
    if m:
        try:
            j = json.loads(m.group(1))
            ts = j.get("generation_timestamp")
            out["recraft"] = {"signed_by": j.get("signed_by"), "algo": j.get("signing_algo"),
                              "generated": dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat() if ts else None,
                              "identifier": j.get("identifier")}
        except Exception:  # noqa: BLE001
            out["recraft"] = {"raw": short(m.group(1), 120)}
    return out


# ------------------------------------------------------------------ видимая метка в углах
def load_frames(path: Path, kind: str, tmp: Path):
    from PIL import Image
    frames = []
    if kind == "image":
        try:
            im = Image.open(path)
            im.seek(0)
            frames.append(("f0", im.convert("RGB")))
        except Exception:  # noqa: BLE001
            pass
    elif kind == "video":
        info = ffprobe_read(path)
        dur = info.get("duration") or 0
        for name, t in (("start", 0.0), ("mid", dur / 2), ("end", max(dur - 0.1, 0))):
            fp = tmp / f"{path.stem}_{name}.png"
            rc, _, _ = run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
                            str(fp)], timeout=60)
            if rc == 0 and fp.exists():
                frames.append((name, Image.open(fp).convert("RGB")))
    return frames


def text_chain(g, H: int) -> int:
    """Длина самой длинной «строки символов» в области: white/black top-hat → компоненты размера буквы → цепочка
    соседей по x с одним уровнем по y. ≥ 6 — похоже на надпись («AI-generated»). Эвристика: на 8 CC0-фото
    находит надпись 2,2–3,5 % высоты кадра в ≈ 50 % случаев, ложные срабатывания — 1 из 10 (L/01 README)."""
    import numpy as np
    from scipy import ndimage as nd
    best = 0
    k = max(5, int(round(H * 0.012)) | 1)
    for pol in ("white", "dark"):
        th = nd.white_tophat(g, size=(k, k)) if pol == "white" else nd.black_tophat(g, size=(k, k))
        lab, n = nd.label(th > 35, structure=np.ones((3, 3)))
        if n == 0:
            continue
        comps = []
        for i, sl in enumerate(nd.find_objects(lab), 1):
            hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if hh < max(4, 0.006 * H) or hh > 0.06 * H or ww > 0.09 * H:
                continue
            area = int((lab[sl] == i).sum())
            if area < 6 or not (0.08 <= area / (hh * ww) <= 0.9):
                continue
            comps.append(((sl[0].start + sl[0].stop) / 2, sl[1].start, sl[1].stop, hh))
        comps.sort(key=lambda c: c[1])
        for i in range(len(comps)):
            chain, last = 1, comps[i]
            for c in comps[i + 1:]:
                mh = max(last[3], c[3])
                if abs(c[0] - last[0]) <= 0.35 * mh and 0 <= c[1] - last[2] <= 1.2 * mh and 0.5 <= c[3] / last[3] <= 2.0:
                    chain, last = chain + 1, c
            best = max(best, chain)
    return best


def corner_stats(img) -> dict:
    """По каждому углу: плотность сильных краёв против всего кадра (density, ratio) и длина «строки символов»
    (text_chain, углы 30 % × 14 % кадра). Флаг — text_chain ≥ 6 или (density ≥ 0,03 и ratio ≥ 2,5). Это подсказка,
    а не детектор: решение — глазами по corners.jpg (или VLM-вопросом K)."""
    import numpy as np
    g = np.asarray(img.convert("L"), dtype=np.float32)
    h, w = g.shape
    gx = np.abs(np.diff(g, axis=1))[:-1, :]
    gy = np.abs(np.diff(g, axis=0))[:, :-1]
    strong = np.maximum(gx, gy) > 40.0
    glob = float(strong.mean()) + 1e-6
    cw, ch = max(8, int(w * CORNER_W)), max(8, int(h * CORNER_H))
    tw, tch = max(8, int(w * 0.30)), max(8, int(h * 0.14))
    boxes = {"TL": (0, 0), "TR": (w - cw - 1, 0), "BL": (0, h - ch - 1), "BR": (w - cw - 1, h - ch - 1)}
    tboxes = {"TL": (0, 0), "TR": (w - tw, 0), "BL": (0, h - tch), "BR": (w - tw, h - tch)}
    out = {}
    for k, (x, y) in boxes.items():
        dens = float(strong[y:y + ch, x:x + cw].mean())
        tx, ty = tboxes[k]
        chain = text_chain(g[ty:ty + tch, tx:tx + tw], h)
        out[k] = {"density": round(dens, 4), "ratio": round(dens / glob, 2), "text_chain": chain,
                  "flag": bool(chain >= 6 or (dens >= 0.03 and dens / glob >= 2.5))}
    return out


def corners_sheet(entries: list[tuple[str, object]], out_png: Path, cell_h: int = 110):
    from PIL import Image, ImageDraw
    rows = []
    for label, img in entries:
        w, h = img.size
        cw, ch = max(8, int(w * CORNER_W)), max(8, int(h * CORNER_H))
        crops = [img.crop((0, 0, cw, ch)), img.crop((w - cw, 0, w, ch)),
                 img.crop((0, h - ch, cw, h)), img.crop((w - cw, h - ch, w, h))]
        scale = cell_h / ch
        crops = [c.resize((max(1, int(c.width * scale)), cell_h)) for c in crops]
        cwid = crops[0].width
        row = Image.new("RGB", (260 + 2 * cwid + 12, 2 * cell_h + 8), "white")
        d = ImageDraw.Draw(row)
        d.text((6, 6), label[:40], fill="black")
        d.text((6, 22), "TL TR / BL BR", fill="gray")
        row.paste(crops[0], (260, 0)); row.paste(crops[1], (260 + cwid + 6, 0))
        row.paste(crops[2], (260, cell_h + 6)); row.paste(crops[3], (260 + cwid + 6, cell_h + 6))
        rows.append(row)
    if not rows:
        return None
    W = max(r.width for r in rows)
    sheet = Image.new("RGB", (W, sum(r.height + 6 for r in rows)), (230, 230, 230))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height + 6
    if str(out_png).lower().endswith((".jpg", ".jpeg")):
        sheet.save(out_png, quality=85)
    else:
        sheet.save(out_png)
    return out_png


# ------------------------------------------------------------------ паспорт polza рядом
def find_passport(path: Path) -> dict | None:
    for pp in path.parent.glob("*.passport.json"):
        try:
            d = json.loads(pp.read_text("utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for f in d.get("files", []) or []:
            if Path(str(f.get("path", ""))).name == path.name:
                job = d.get("job") or {}
                return {"passport": pp.name, "model": job.get("model"), "tag": job.get("tag"),
                        "provider_actual": d.get("provider_actual"), "sha256_match": f.get("sha256") == sha256(path)}
    return None


# ------------------------------------------------------------------ сводка и советы
def summarize(rec: dict) -> dict:
    marks, ai = [], False
    c2 = rec.get("c2pa") or {}
    if c2.get("present"):
        marks.append(f"C2PA:{c2.get('state')}")
        if any(x in ("trainedAlgorithmicMedia", "compositeWithTrainedAlgorithmicMedia", "algorithmicMedia")
               for x in c2.get("digital_source_types", [])):
            ai = True
    ex = rec.get("exif") or {}
    for dstv in ex.get("digital_source_type", []) or []:
        marks.append(f"XMP-DST:{dstv}")
        if "Algorithmic" in dstv:
            ai = True
    vid = rec.get("video") or {}
    if vid.get("aigc"):
        a = vid["aigc"]
        marks.append(f"AIGC:{a.get('ContentProducer', '?') if isinstance(a, dict) else '?'}")
        if isinstance(a, dict) and str(a.get("Label")) == "1":
            ai = True
    sv = rec.get("svg") or {}
    if sv.get("recraft"):
        marks.append("recraft-signature")
        ai = True
    bs = rec.get("bytes_markers") or {}
    if bs.get("SynthID"):
        marks.append("string:SynthID")
    if bs.get("TC260"):
        marks.append("string:TC260")
    vis = [f"{fr}:{k}" for fr, st in (rec.get("corners") or {}).items() for k, v in st.items() if v.get("flag")]
    advice = []
    gen = (c2.get("generator") or "") + " " + json.dumps(ex.get("hits", {}), ensure_ascii=False)
    if c2.get("present") and c2.get("state") in ("Valid", "Trusted"):
        advice.append("мастер с подписью: хранить побайтно; производные — без встроенного манифеста + XMP-DST или sidecar")
    if c2.get("present") and c2.get("state") not in ("Valid", "Trusted"):
        advice.append("C2PA есть, но подпись не сходится: файл правили после подписи — не публиковать как «оригинал»")
    if rec["kind"] in ("image", "video") and not marks:
        advice.append("машиночитаемых меток нет: если это финальный ИИ-ассет — stamp --dst trained|composite")
    if re.search(r"google|gemini|imagen|veo|openai|gpt", gen, re.I) or bs.get("SynthID"):
        advice.append("SynthID локально не видно: проверить в Gemini app / Google Lens («Is this AI-generated?»), "
                      "картинки OpenAI — openai.com/verify")
    if vis:
        advice.append("подозрение на видимую метку в углу: смотреть corners.jpg; метки вендора не вырезать кропом "
                      "без решения по 04-agent-policy")
    if sv.get("recraft"):
        advice.append("подпись Recraft: не удалять (Developer Terms 6.4); svgo — конфиг keep-signature (G/02)")
    if rec["kind"] == "svg" and (c2.get("present") or sv.get("c2pa_manifest_blocks")):
        advice.append("C2PA в <metadata> SVG: svgo preset-default (removeMetadata) удаляет его вместе с <metadata>; "
                      "мастер хранить побайтно, в чистке — отключить removeMetadata или вести паспорт/sidecar; "
                      "любая правка путей ломает dataHash (подпись станет недействительной)")
    return {"marks": marks, "ai_declared": ai, "visible_suspect": vis, "advice": advice}


def scan_file(path: Path, tmp: Path, corners: bool) -> tuple[dict, list]:
    k = kind_of(path)
    rec = {"file": str(path), "kind": k, "bytes": path.stat().st_size, "sha256": sha256(path)}
    rec["c2pa"] = c2pa_read(path) if k in ("image", "video", "svg") else {"present": None, "note": "не проверялся"}
    rec["exif"] = exif_read(path) if k in ("image", "video") else {}
    if k == "video":
        rec["video"] = ffprobe_read(path)
    if k == "svg":
        rec["svg"] = svg_read(path)
    rec["bytes_markers"] = byte_scan(path)
    frames = load_frames(path, k, tmp) if corners and k in ("image", "video") else []
    if frames:
        rec["corners"] = {name: corner_stats(img) for name, img in frames}
    pp = find_passport(path)
    if pp:
        rec["passport"] = pp
    rec["summary"] = summarize(rec)
    return rec, [(f"{path.name}:{n}", im) for n, im in frames]


def iter_paths(paths: list[str]):
    for p in paths:
        pp = Path(p)
        if pp.is_dir():
            for q in sorted(pp.rglob("*")):
                if q.is_file() and kind_of(q) != "other":
                    yield q
        elif pp.is_file():
            yield pp


def md_table(recs: list[dict]) -> str:
    lines = ["| Файл | Вид | КБ | C2PA | Метки | ИИ заявлен | Видимая метка? | Совет |", "|---|---|---|---|---|---|---|---|"]
    for r in recs:
        c2 = r.get("c2pa") or {}
        c2s = "—" if not c2.get("present") else f"{c2.get('state')} · {short(c2.get('generator') or '?', 40)}" + (
            f" · {c2.get('store_bytes', 0) // 1024} КБ" if c2.get("store_bytes") else "")
        s = r["summary"]
        lines.append(f"| {Path(r['file']).name} | {r['kind']} | {r['bytes'] / 1024:.1f} | {c2s} | "
                     f"{', '.join(s['marks']) or '—'} | {'да' if s['ai_declared'] else 'нет'} | "
                     f"{', '.join(s['visible_suspect']) or '—'} | {'; '.join(s['advice']) or '—'} |")
    return "\n".join(lines) + "\n"


def cmd_scan(a) -> int:
    global USE_TRUST
    USE_TRUST = bool(a.trust)
    out = Path(a.out) if a.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    recs, frames_all = [], []
    with tempfile.TemporaryDirectory(prefix="provcheck_") as td:
        for p in iter_paths(a.paths):
            rec, fr = scan_file(p, Path(td), a.corners)
            recs.append(rec)
            frames_all.extend(fr)
            s = rec["summary"]
            print(f"{p.name}: {', '.join(s['marks']) or 'меток нет'}; ИИ заявлен: {'да' if s['ai_declared'] else 'нет'}"
                  + (f"; углы: {', '.join(s['visible_suspect'])}" if s["visible_suspect"] else ""))
        if a.corners and frames_all and out:
            corners_sheet(frames_all, out / "corners.jpg")
    meta = {"tool": "provenance_check.py", "version": VERSION, "checked_at": dt.datetime.now().isoformat(timespec="seconds"),
            "exiftool": run([EXIFTOOL, "-ver"])[1].strip(), "c2patool": run([C2PATOOL, "--version"])[1].strip(),
            "files": recs}
    jpath = Path(a.json) if a.json else (out / "provenance.json" if out else None)
    mpath = Path(a.md) if a.md else (out / "provenance.md" if out else None)
    if jpath:
        jpath.write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    if mpath:
        mpath.write_text(f"# Провенанс ({meta['checked_at']}, {VERSION})\n\n" + md_table(recs))
    if not (jpath or mpath):
        print(md_table(recs))
    return 0


# ------------------------------------------------------------------ stamp
def cmd_stamp(a) -> int:
    src, dst = Path(a.inp), Path(a.out)
    c2 = c2pa_read(src) if kind_of(src) in ("image", "video") else {}
    if c2.get("present") and c2.get("state") in ("Valid", "Trusted") and not a.force:
        print("ОТКАЗ: у файла валидный C2PA — правка метаданных сломает подпись. Штампуйте производную "
              "(перекодированный файл) или --force.", file=sys.stderr)
        return 1
    uri = DST[a.dst]
    if src.resolve() != dst.resolve():
        shutil.copyfile(src, dst)
    ext = dst.suffix.lower()
    if ext in (".webm", ".mkv"):
        tmp = dst.with_name(dst.stem + ".stamp" + dst.suffix)
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(dst), "-map", "0", "-c", "copy",
               "-metadata", f"DIGITAL_SOURCE_TYPE={uri}", "-metadata", f"COMMENT=AI-generated ({a.dst})"]
        if a.system:
            cmd += ["-metadata", f"AI_SYSTEM={a.system}"]
        rc, _, se = run(cmd + [str(tmp)], timeout=300)
        if rc != 0:
            print(se, file=sys.stderr); return 1
        tmp.replace(dst)
    else:
        cmd = [EXIFTOOL, "-overwrite_original", "-q", f"-XMP-iptcExt:DigitalSourceType={uri}"]
        if a.system:
            cmd.append(f"-XMP-iptcExt:AISystemUsed={a.system}")
        if a.system_version:
            cmd.append(f"-XMP-iptcExt:AISystemVersionUsed={a.system_version}")
        if a.credit:
            cmd.append(f"-XMP-photoshop:Credit={a.credit}")
        rc, so, se = run(cmd + [str(dst)])
        if rc != 0:
            print(se or so, file=sys.stderr); return 1
    print(f"{dst}: DigitalSourceType={a.dst} (+{dst.stat().st_size - src.stat().st_size} байт)")
    return 0


# ------------------------------------------------------------------ selftest
def cmd_selftest(a) -> int:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    base = Path(a.keep) if a.keep else Path(tempfile.mkdtemp(prefix="provself_"))
    base.mkdir(parents=True, exist_ok=True)
    ok, results = True, []

    def check(name, cond, info=""):
        nonlocal ok
        ok &= bool(cond)
        results.append((name, bool(cond), info))
        print(f"{'PASS' if cond else 'FAIL'}  {name}  {info}")

    rng = np.random.default_rng(7)
    yy, xx = np.mgrid[0:512, 0:768]
    arr = np.stack([60 + 120 * xx / 768, 90 + 80 * yy / 512, 150 + 60 * np.sin(xx / 90)], -1)
    arr = np.clip(arr + rng.normal(0, 3, arr.shape), 0, 255).astype("uint8")
    clean = base / "clean.png"; Image.fromarray(arr).save(clean)
    marked = base / "marked.png"
    im = Image.fromarray(arr); d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:  # noqa: BLE001
        font = ImageFont.load_default()
    d.text((768 - 150, 512 - 34), "AI-generated", fill=(255, 255, 255), font=font)
    im.save(marked)
    # подпись C2PA тестовым сертификатом c2patool
    man = base / "manifest.json"
    man.write_text(json.dumps({"claim_generator_info": [{"name": "provenance_check selftest", "version": "0.1"}],
                               "title": "selftest", "assertions": [{"label": "c2pa.actions", "data": {"actions": [
                                   {"action": "c2pa.created", "digitalSourceType": DST["trained"]}]}}]}))
    signed = base / "signed.png"
    rc, so, se = run([C2PATOOL, str(clean), "-m", str(man), "-o", str(signed), "-f"])
    check("c2patool подписал мастер", rc == 0 and signed.exists(), (se or "").strip()[-120:])
    avif = base / "derived.avif"
    Image.open(signed).save(avif, quality=55)
    stamped = base / "derived_dst.avif"
    rc_stamp = cmd_stamp(argparse.Namespace(inp=str(avif), out=str(stamped), dst="trained", system="selftest",
                                            system_version="0.1", credit=None, force=False))
    refused = cmd_stamp(argparse.Namespace(inp=str(signed), out=str(base / "signed_stamped.png"), dst="trained",
                                           system=None, system_version=None, credit=None, force=False))
    # видео с китайской меткой и её судьба при ремуксе
    mp4 = base / "aigc.mp4"
    aigc = json.dumps({"Label": "1", "ContentProducer": "selftest", "ProduceID": "42"})
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=2", "-f", "lavfi",
         "-i", "sine=frequency=440:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
         "-metadata", f"AIGC={aigc}", "-movflags", "use_metadata_tags", str(mp4)], timeout=120)
    plain = base / "remux_plain.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-c", "copy", str(plain)])
    keep = base / "remux_keep_an.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-map_metadata", "0", "-c:v", "copy", "-an", "-movflags",
         "use_metadata_tags+faststart", str(keep)])
    webm = base / "keep.webm"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-map_metadata", "0", "-c:v", "libvpx-vp9", "-b:v", "200k",
         "-an", "-deadline", "realtime", "-cpu-used", "8", str(webm)], timeout=180)
    svg = base / "recraft.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/>'
                   '<metadata><recraft-signature>{"signed_by": "recraft", "signature_b64": "AAAA", "signing_algo": '
                   '"Ed25519", "generation_timestamp": 1771419804, "identifier": "x"}</recraft-signature></metadata></svg>')
    recs = {}
    with tempfile.TemporaryDirectory(prefix="provself_fr_") as td:
        for p in (clean, marked, signed, avif, stamped, mp4, plain, keep, webm, svg):
            if p.exists():
                recs[p.name] = scan_file(p, Path(td), corners=True)[0]
    g = lambda n: recs.get(n, {})  # noqa: E731
    check("подписанный мастер: C2PA Valid + ИИ заявлен", g("signed.png").get("c2pa", {}).get("state") == "Valid"
          and g("signed.png")["summary"]["ai_declared"], str(g("signed.png").get("c2pa", {}).get("store_bytes")))
    check("производная AVIF: манифест потерян", not g("derived.avif").get("c2pa", {}).get("present"))
    check("stamp: XMP DigitalSourceType в AVIF", rc_stamp == 0 and "trainedAlgorithmicMedia" in
          g("derived_dst.avif").get("exif", {}).get("digital_source_type", []))
    check("stamp отказывается править подписанный мастер", refused == 1)
    fl_m = g("marked.png").get("summary", {}).get("visible_suspect", [])
    fl_c = g("clean.png").get("summary", {}).get("visible_suspect", [])
    check("видимая метка в углу BR найдена", any(x.endswith("BR") for x in fl_m), str(fl_m))
    check("на чистом кадре ложных углов нет", not fl_c, str(fl_c))
    check("MP4: метка AIGC читается", bool(g("aigc.mp4").get("video", {}).get("aigc")))
    check("remux -c copy: AIGC теряется", not g("remux_plain.mp4").get("video", {}).get("aigc"))
    check("-map_metadata 0 + use_metadata_tags + -an: AIGC живёт", bool(g("remux_keep_an.mp4").get("video", {}).get("aigc")))
    check("WebM (VP9, -an): AIGC живёт в тегах Matroska", bool(g("keep.webm").get("video", {}).get("aigc")))
    check("SVG: подпись Recraft распознана", bool(g("recraft.svg").get("svg", {}).get("recraft")))
    (base / "selftest.json").write_text(json.dumps({"results": results, "records": recs}, ensure_ascii=False, indent=1))
    print(("SELFTEST PASS" if ok else "SELFTEST FAIL") + f"  ({base})")
    if not a.keep:
        shutil.rmtree(base, ignore_errors=True)
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan"); s.add_argument("paths", nargs="+"); s.add_argument("--out")
    s.add_argument("--corners", action="store_true"); s.add_argument("--json"); s.add_argument("--md")
    s.add_argument("--trust", action="store_true", help="сверять подпись со списком доверия C2PA (C2PA_TRUST_PEM)")
    t = sub.add_parser("stamp"); t.add_argument("inp"); t.add_argument("out")
    t.add_argument("--dst", choices=sorted(DST), required=True); t.add_argument("--system")
    t.add_argument("--system-version"); t.add_argument("--credit"); t.add_argument("--force", action="store_true")
    st = sub.add_parser("selftest"); st.add_argument("--keep")
    a = ap.parse_args()
    return {"scan": cmd_scan, "stamp": cmd_stamp, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
