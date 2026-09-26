#!/usr/bin/env python3
"""asset_audit.py — единая автоматическая приёмка ИИ-ассетов сайта (агент K, волна 3, 23.09.2026).

Объединяет готовые проверки волн 1–2 вызовом и импортом, ничего в них не переписывая:
  A/04 image_metrics.py (цвет, «HDR»), F/04 composition_metrics.py («средний вид»), F/02 text_zone.py (зона текста,
  скрим, WCAG F83), F/06 series_metrics.py и split_grid.py (серия), stand_run.py (E: text_check, pHash, Уилсон, BT),
  edit_check.py 0.2 и alpha_check.py (H), tile_check.py (H2), video_loop_check.py 0.2 (I), G/check_icons.py (venv-G),
  mp_client.py (svg_info), vlm_to_dna.py (паспорт визуала: палитра, приёмка, запреты), polza/mp_client-паспорта,
  exiftool / c2patool (или provenance_check.py агента L, если есть), OCR кириллицы RapidOCR + PP-OCRv5 eslav (venv-K).
Пороги — 11-evaluation-qa/thresholds.yaml (у каждого — источник). Вход — файл, список или папка с паспортами.
Выход — JSON-вердикт с кодами дефектов (asset-audit/1), Markdown-сводка и контактный лист для человека.

Режимы (--mode; auto — по паспорту, коду задачи, альфе и расширению):
  image       фото, иллюстрация, фон, 3D-объект: размеры, цвет-слоп, композиция, зона текста, палитра, текст (OCR), провенанс
  cutout      вырез/нативная альфа: альфа есть и настоящая, ореол, поле, полупрозрачность, эталон (--ref-alpha)
  edit        правка на месте (--orig [--mask] [--protect]) или аутпейнт (другая пропорция) — edit_check.py; без маски —
              маска из разницы (ΔE00 > 5 после подгонки цвета + морфология) и композит с растушёвкой
  series      папка или список кадров: оттенок, ΔE палитр, светлота, pHash-дубли (+ --ref, --grid RxC)
  texture     бесшовность (tile_check)
  video-loop  шов на мезонине, живость (+ --control), склейки, угасание, пинг-понг, камера, звук, мерцание яркости,
              синемаграф (--mask → drift)
  video-alpha хромакей-исходник (chroma) или файл с альфой (pix_fmt)
  svg-icon    линейная иконка (check_icons, пороги Lucide) или цветной SVG (фон, корень, <image>, <text>, подпись Recraft)
  og          OG-картинка 1200×630: размер, вес, текст (OCR), поля, + всё из image

Команды:
  audit PATH… [--mode M] [--out DIR] [--dna DNA.json] [--spec SPEC.json] [--expect "строка"]… [--orig O] [--mask M]
        [--control C] [--ref-alpha GT] [--text-zone x0,y0,x1,y1] [--slot hero|section|product|icon|og] [--strict]
  ocr IMG… [--lang ru|en] [--expect …]      OCR (venv-K под heavy.lock) + сверка со строками
  thresholds [--check]                       пороги с источниками; --check — у каждого есть source
  judge-jobs / judge-parse / agree / calibrate — VLM-критик и калибровка по голосам заказчика (см. 11-evaluation-qa/02)
  selftest                                   офлайн-проверки на синтетике (без OCR-модели — отдельный тест)
Платных вызовов нет: judge-jobs только пишет задания .polza-chat.json (исполняет mp_client.py в фазе 5).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

VERSION = "0.1 (2026-09-23)"
SCHEMA = "asset-audit/1"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("ai-media")
TOOLS = kbpaths.scripts("ai-media")
EXP = ROOT / "99-raw" / "experiments"
LOCKS = Path(kbpaths.lock_path("heavy", "ai-media")).parent  # перенос: $DDD_HOME/locks/ai-media/{heavy,browser,blender}.lock
THRESHOLDS = ROOT / "11-evaluation-qa" / "thresholds.yaml"
RUBRICS = ROOT / "11-evaluation-qa" / "rubrics"
VENV_K = Path(kbpaths.python())  # перенос: venv-K (rapidocr) → Python окружения скилла
VENV_G = Path(kbpaths.python())  # перенос: venv-G (cairosvg, svgelements)
OCR_MODELS = kbpaths.models("ocr")
A04 = F02 = F04 = F05 = F06 = G_EXP = TOOLS  # перенос: модули опытов (Р54) — scripts/ai-media
LUCIDE_REF = kbpaths.data("ai-media", "lucide-ref")
EXIFTOOL = Path(kbpaths.which("exiftool"))
C2PATOOL = Path(kbpaths.which("c2patool"))
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".bmp", ".tif", ".tiff")
VID_EXT = (".mp4", ".webm", ".mov", ".m4v", ".mkv")
SVG_EXT = (".svg",)

sys.path.insert(0, str(TOOLS))

# ================================================================ общие помощники


def _load(name: str, path: Path):
    """Импорт модуля по пути (утилиты соседей и скрипты опытов, которые можно импортировать без побочных эффектов)."""
    key = f"_aa_{name}"
    if key in sys.modules:
        return sys.modules[key]
    for extra in (str(path.parent),):
        if extra not in sys.path:
            sys.path.insert(0, extra)
    spec = importlib.util.spec_from_file_location(key, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


def mod(name: str):
    """Модули соседей: импорт по требованию (numpy/scipy нужны только им)."""
    paths = {"edit_check": TOOLS / "edit_check.py", "alpha_check": TOOLS / "alpha_check.py",
             "tile_check": TOOLS / "tile_check.py", "video_loop_check": TOOLS / "video_loop_check.py",
             "stand_run": TOOLS / "stand_run.py", "vlm_to_dna": TOOLS / "vlm_to_dna.py", "mp_client": TOOLS / "mp_client.py",
             "ab_analyze": TOOLS / "ab_analyze.py", "image_metrics": A04 / "image_metrics.py",
             "composition_metrics": F04 / "composition_metrics.py", "text_zone": F02 / "text_zone.py",
             "series_metrics": F06 / "series_metrics.py", "split_grid": F06 / "split_grid.py"}
    return _load(name, paths[name])


def rel(p) -> str:
    p = Path(p)
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def jdump(o, indent=1) -> str:
    return json.dumps(o, ensure_ascii=False, indent=indent, default=_json_default)


def _json_default(o):
    try:
        import numpy as np
        if isinstance(o, np.generic):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:
        pass
    if isinstance(o, Path):
        return str(o)
    return str(o)


def rnd(x, k=4):
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return x
    return round(v, k) if math.isfinite(v) else None


def free_gb() -> float | None:
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024 / 1024
    except OSError:
        return None
    return None


def _ancestor_holds_lock(lock_name: str) -> bool:
    """Держит ли уже этот замок процесс-предок через flock(1) (`flock … heavy.lock python3 asset_audit.py …`).

    Повторный `flock` на тот же файл из дочернего процесса ждал бы родителя до таймаута — самоблокировка
    (найдено агентом M, исправлено агентом X 24.09.2026). Только Linux (/proc); при любой ошибке — False.
    """
    try:
        pid = os.getppid()
        for _ in range(16):
            if pid <= 1:
                break
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                args = [a.decode("utf-8", "replace") for a in fh.read().split(b"\0") if a]
            if args and os.path.basename(args[0]) == "flock" and any(a.endswith(lock_name) for a in args[1:]):
                return True
            with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as fh:
                pid = int(fh.read().rsplit(")", 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        return False
    return False


def locked(cmd: list[str], lock: str = "heavy", wait: int = 1800) -> list[str]:
    """Команда под flock из 99-raw/tools/.locks (heavy — модели, browser — Chromium, blender — Blender).

    Если замок уже держит процесс-предок (утилиту обернули во внешний `flock`), повторно не берём — иначе самоблокировка.
    """
    if shutil.which("flock") is None:
        return cmd
    if _ancestor_holds_lock(f"{lock}.lock"):
        return cmd
    LOCKS.mkdir(parents=True, exist_ok=True)
    return ["flock", "-w", str(wait), str(LOCKS / f"{lock}.lock")] + cmd


# ================================================================ пороги


_TH_CACHE: dict = {}


def load_thresholds(path: Path | None = None) -> dict:
    """Пороги из YAML; у каждого узла {value, source, …}. Возвращает dict и плоский индекс 'a.b.c' → value."""
    p = Path(path or THRESHOLDS)
    if str(p) in _TH_CACHE:
        return _TH_CACHE[str(p)]
    import yaml
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    flat: dict = {}

    def walk(node, prefix):
        if isinstance(node, dict) and "value" in node and ("source" in node or "sources" in node):
            flat[prefix] = node["value"]
            return
        if isinstance(node, dict):
            for k, v in node.items():
                if k.startswith("_"):
                    continue
                walk(v, f"{prefix}.{k}" if prefix else k)
    walk(doc.get("thresholds", {}), "")
    doc["_flat"] = flat
    doc["_path"] = rel(p)
    doc["_sha"] = sha256_file(p)[:12] if p.exists() else None
    _TH_CACHE[str(p)] = doc
    return doc


class Th:
    """Доступ к порогам: th('image.colorfulness_max') → значение; переопределения из паспорта визуала (--dna)."""

    def __init__(self, doc: dict, overrides: dict | None = None):
        self.doc = doc
        self.flat = dict(doc.get("_flat", {}))
        self.over = overrides or {}

    def __call__(self, key: str, default=None):
        if key in self.over:
            return self.over[key]
        return self.flat.get(key, default)

    def src(self, key: str) -> str | None:
        node = self.doc.get("thresholds", {})
        for part in key.split("."):
            if not isinstance(node, dict):
                return None
            node = node.get(part)
        if isinstance(node, dict):
            s = node.get("source") or node.get("sources")
            if key in self.over:
                return f"паспорт визуала (переопределено); база: {s}"
            return s if isinstance(s, str) else "; ".join(s) if isinstance(s, list) else None
        return None


# ================================================================ дефекты и вердикт


class Report:
    """Отчёт по одному ассету: checks (числа), defects (коды), human (что смотреть человеку)."""

    LEVELS = {"info": 0, "warn": 1, "needs_human": 2, "fail": 3}

    def __init__(self, path: Path, mode: str, th: Th):
        self.path = Path(path)
        self.mode = mode
        self.th = th
        self.checks: dict = {}
        self.defects: list[dict] = []
        self.human: list[dict] = []
        self.errors: list[str] = []
        self.meta: dict = {}
        self.markers: set[str] = set()

    def defect(self, code: str, level: str, msg: str, metric: str | None = None, value=None, th_key: str | None = None,
               threshold=None, marker: str | None = None, evidence=None):
        d = {"code": code, "level": level, "msg": msg}
        if metric:
            d["metric"] = metric
        if value is not None:
            d["value"] = rnd(value) if isinstance(value, (int, float)) else value
        if th_key:
            d["threshold_key"] = th_key
            d["threshold"] = threshold if threshold is not None else self.th(th_key)
            s = self.th.src(th_key)
            if s:
                d["source"] = s
        elif threshold is not None:
            d["threshold"] = threshold
        if marker:
            d["marker"] = marker
            if level in ("warn", "fail", "needs_human"):
                self.markers.add(marker)
        if evidence is not None:
            d["evidence"] = evidence
        self.defects.append(d)
        return d

    def ask_human(self, item: str, why: str, codes: list[str] | None = None):
        self.human.append({"item": item, "why": why, **({"codes": codes} if codes else {})})

    def verdict(self) -> str:
        lv = max([self.LEVELS[d["level"]] for d in self.defects] + [0])
        if self.errors and lv < 2:
            lv = 2
        return {0: "pass", 1: "warn", 2: "needs_human", 3: "fail"}[lv]

    def to_dict(self) -> dict:
        v = self.verdict()
        return {"schema": SCHEMA, "tool": f"asset_audit.py {VERSION}", "checked_at": now_iso(), "file": rel(self.path),
                "mode": self.mode, **self.meta, "verdict": v,
                "summary": {k: sum(1 for d in self.defects if d["level"] == k) for k in ("fail", "needs_human", "warn", "info")},
                "markers": sorted(self.markers), "defects": self.defects, "human": self.human, "checks": self.checks,
                "errors": self.errors, "thresholds": {"file": self.th.doc.get("_path"), "sha": self.th.doc.get("_sha")}}


# ================================================================ OCR (RapidOCR + PP-OCRv5, venv-K)

OCR_SETS = {
    # det — детектор строк, rec — распознаватель; модели: 99-raw/tools/models/ocr (sha256 — thresholds.yaml → ocr.models);
    # «@» — модель из колеса rapidocr 3.9.2 (venv-K). Кириллица — только eslav/cyrillic PP-OCRv5 (у PP-OCRv6 её нет).
    # K/01 (714 синтетических баннеров): ru = det PP-OCRv6 small + rec eslav — меньше всего ложного брака (3/72 чистых).
    "ru": ("@PP-OCRv6_det_small.onnx", "eslav_PP-OCRv5_rec_mobile.onnx"),
    "ru-v5det": ("ch_PP-OCRv5_det_mobile.onnx", "eslav_PP-OCRv5_rec_mobile.onnx"),
    "ru-cyrillic": ("@PP-OCRv6_det_small.onnx", "cyrillic_PP-OCRv5_rec_mobile.onnx"),
    "en": ("@PP-OCRv6_det_small.onnx", "en_PP-OCRv5_rec_mobile.onnx"),
    "multi-v6": ("@PP-OCRv6_det_small.onnx", "@PP-OCRv6_rec_small.onnx"),
}
OCR_SNIFF_REC = "en_PP-OCRv5_rec_mobile.onnx"   # второй распознаватель по тем же рамкам строк — «латинский нюх»
OCR_DET_LIMIT = (1600, "max")


def _ocr_model_path(name: str) -> str:
    if name.startswith("@"):      # модель из колеса rapidocr (venv-K)
        import rapidocr
        return str(Path(rapidocr.__file__).parent / "models" / name[1:])
    return str(OCR_MODELS / name)


def ocr_lines(boxes, txts, scores, y_overlap=0.5):
    """Слова/фрагменты RapidOCR → строки в порядке чтения: группировка по перекрытию по вертикали, внутри — по x."""
    items = []
    for b, t, s in zip(boxes, txts, scores):
        xs, ys = [p[0] for p in b], [p[1] for p in b]
        items.append({"text": t, "score": round(float(s), 4), "x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys),
                      "h": max(ys) - min(ys)})
    items.sort(key=lambda it: (it["y0"] + it["y1"]) / 2)
    lines: list[list[dict]] = []
    for it in items:
        placed = False
        for ln in lines:
            ly0, ly1 = min(x["y0"] for x in ln), max(x["y1"] for x in ln)
            ov = min(ly1, it["y1"]) - max(ly0, it["y0"])
            if ov >= y_overlap * min(it["h"], ly1 - ly0):
                ln.append(it)
                placed = True
                break
        if not placed:
            lines.append([it])
    out = []
    for ln in lines:
        ln.sort(key=lambda x: x["x0"])
        out.append({"text": " ".join(x["text"] for x in ln), "score_min": min(x["score"] for x in ln),
                    "score_mean": round(sum(x["score"] for x in ln) / len(ln), 4),
                    "h_px": round(sorted(x["h"] for x in ln)[len(ln) // 2], 1),
                    "box": [round(min(x["x0"] for x in ln)), round(min(x["y0"] for x in ln)),
                            round(max(x["x1"] for x in ln)), round(max(x["y1"] for x in ln))],
                    "words": [{"text": x["text"], "score": x["score"], "box": [round(x["x0"]), round(x["y0"]),
                                                                              round(x["x1"]), round(x["y1"])]} for x in ln]})
    out.sort(key=lambda L: (L["box"][1], L["box"][0]))
    return out


def _load_rgb_pil(p):
    from PIL import Image
    im = Image.open(p)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (128, 128, 128, 255))   # прозрачное — на средне-сером: виден и светлый, и тёмный текст
        bg.alpha_composite(im)
        im = bg
    return im.convert("RGB")


def ocr_worker(paths: list[str], lang: str = "ru", text_score: float = 0.3, relines: bool = True,
               det_limit: tuple = OCR_DET_LIMIT, sniff: bool = True) -> list[dict]:
    """Выполняется в venv-K (rapidocr 3.9.2 + onnxruntime). Возвращает на каждую картинку строки, слова, время.
    relines: слова одной строки склеиваются по рамке и строка распознаётся заново целиком (K/01: детектор PP-OCRv5 режет
    строку на перекрывающиеся слова, и буква на стыке читается дважды — «Весенняяр распродажа»)."""
    import time
    from rapidocr import RapidOCR
    det, rec = OCR_SETS[lang]
    eng = RapidOCR(params={"Global.log_level": "error", "Global.use_cls": False, "Global.text_score": text_score,
                           "Det.model_path": _ocr_model_path(det), "Rec.model_path": _ocr_model_path(rec),
                           "Det.limit_side_len": int(det_limit[0]), "Det.limit_type": str(det_limit[1]),
                           "EngineConfig.onnxruntime.intra_op_num_threads": 4})
    sn = None
    if sniff and lang.startswith("ru"):
        # K/01: русская модель «исправляет» латиницу в кириллицу (DОСТАВКА → ДОСТАВКА: 5 из 5); английская по той же
        # рамке читает «D» (5 из 5, ложных 1 из 144) — сверка в text_verdict (класс latin_suspect)
        sn = RapidOCR(params={"Global.log_level": "error", "Global.use_cls": False, "Global.text_score": 0.0,
                              "Det.model_path": _ocr_model_path(det), "Rec.model_path": _ocr_model_path(OCR_SNIFF_REC),
                              "EngineConfig.onnxruntime.intra_op_num_threads": 4})
    res = []
    for p in paths:
        t0 = time.time()
        try:
            img = _load_rgb_pil(p)
            r = eng(img, use_det=True, use_cls=False, use_rec=True)   # параметры RapidOCR «залипают» между вызовами
            boxes = [] if r.boxes is None else [[[float(x), float(y)] for x, y in b] for b in r.boxes]
            txts = list(r.txts or [])
            scores = list(r.scores or [])
            lines = ocr_lines(boxes, txts, scores)
            W, H = img.size
            for L in lines:
                L["text_words"] = L["text"]
                x0, y0, x1, y1 = L["box"]
                pad = max(2, int(0.25 * (y1 - y0)))
                crop = img.crop((max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)))
                if relines and len(L["words"]) >= 2:
                    rr = eng(crop, use_det=False, use_cls=False, use_rec=True)
                    if rr.txts:
                        t, sc = str(rr.txts[0]), float(rr.scores[0])
                        L["text_line"], L["score_line"] = t, round(sc, 4)
                        if sc >= L["score_min"] - 0.05:
                            L["text"] = t
                if sn is not None:
                    rs = sn(crop, use_det=False, use_cls=False, use_rec=True)
                    L["text_en"] = str(rs.txts[0]) if rs.txts else ""
            res.append({"file": str(p), "lang": lang, "det": det, "rec": rec, "relines": relines, "sniff": sn is not None,
                        "det_limit": list(det_limit),
                        "size": list(img.size),
                        "lines": lines, "elapsed_s": round(time.time() - t0, 3)})
        except Exception as e:  # noqa: BLE001
            res.append({"file": str(p), "lang": lang, "error": f"{type(e).__name__}: {e}"[:300]})
    return res


def run_ocr(paths: list, lang: str = "ru", text_score: float = 0.3, timeout: int = 900) -> list[dict]:
    """Из системного Python: OCR в venv-K под heavy.lock (одна загрузка моделей на пачку картинок)."""
    if not VENV_K.exists():
        return [{"file": str(p), "error": "нет venv-K (rapidocr) — см. 99-raw/tools/README.md, раздел asset_audit"} for p in paths]
    fg = free_gb()
    if fg is not None and fg < 1.0:
        return [{"file": str(p), "error": f"мало памяти ({fg:.1f} ГБ available) — OCR не запущен"} for p in paths]
    cmd = locked([str(VENV_K), str(Path(__file__).resolve()), "_ocr-worker", "--lang", lang, "--text-score", str(text_score)]
                 + [str(Path(p).resolve()) for p in paths])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return [{"file": str(p), "error": f"OCR упал: {(r.stderr or r.stdout)[-400:]}"} for p in paths]


# ================================================================ сверка текста (кириллица): классы ошибок, GNED

LAT = re.compile(r"[A-Za-z]")
CYR = re.compile(r"[А-Яа-яЁё]")
HOMO_LAT = set("ABEKMHOPCTXYaeopcxy")                      # латинские двойники кириллических букв
DIGIT_PAIRS = {("о", "0"), ("о", "o"), ("з", "3"), ("б", "6"), ("ч", "4"), ("в", "8"), ("l", "1"), ("i", "1"), ("s", "5")}
SIMILAR_CYR = {frozenset(p) for p in (("и", "й"), ("ш", "щ"), ("б", "в"), ("п", "н"), ("ц", "щ"), ("ь", "ъ"), ("е", "ё"),
                                        ("ы", "ь"), ("л", "п"), ("к", "н"), ("г", "т"), ("з", "э"))}


def norm_text(s: str, homoglyphs: bool = True, all_homoglyphs: bool = False) -> str:
    """Нормализация E (stand_run.norm_line): NFC, тире и кавычки, пробелы; латинские двойники в русских словах → кириллица.
    all_homoglyphs — двойники → кириллица и в словах без кириллицы (однобуквенное «K» вместо «к»): только если в ожидаемой
    строке нет латиницы (K/01: «Щедрые подарки K Новому году» — ложный брак без этого правила)."""
    sr = mod("stand_run")
    s = sr.norm_line(s, homoglyphs)
    if homoglyphs and all_homoglyphs:
        s = s.translate(sr.HOMO_TO_CYR)
    return s


def lev(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def fit_align(a: str, t: str):
    """Нечёткий поиск строки a внутри транскрипта t (начало и конец в t бесплатны). Возвращает (дистанция, j0, j1, ops),
    ops — ('eq'|'sub'|'del'|'ins', символ a, символ t, позиция в a)."""
    n, m = len(a), len(t)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        D[i][0] = i
    for i in range(1, n + 1):
        ai = a[i - 1]
        Di, Dp = D[i], D[i - 1]
        for j in range(1, m + 1):
            Di[j] = min(Dp[j] + 1, Di[j - 1] + 1, Dp[j - 1] + (ai != t[j - 1]))
    j1 = min(range(m + 1), key=lambda j: (D[n][j], -j)) if m else 0
    dist = D[n][j1]
    ops, i, j = [], n, j1
    while i > 0:
        if j > 0 and D[i][j] == D[i - 1][j - 1] + (a[i - 1] != t[j - 1]):
            ops.append(("eq" if a[i - 1] == t[j - 1] else "sub", a[i - 1], t[j - 1], i - 1))
            i, j = i - 1, j - 1
        elif D[i][j] == D[i - 1][j] + 1:
            ops.append(("del", a[i - 1], "", i - 1))
            i -= 1
        elif j > 0 and D[i][j] == D[i][j - 1] + 1:
            ops.append(("ins", "", t[j - 1], i))
            j -= 1
        else:          # j == 0 — остаток a не найден
            ops.append(("del", a[i - 1], "", i - 1))
            i -= 1
    ops.reverse()
    return dist, j, j1, ops


def classify_ops(ops: list, exp: str) -> list[dict]:
    """Операции выравнивания → классы ошибок кириллицы (C1, W6, E): пропуск, удвоение, латинский недвойник, ё → е,
    похожая буква, цифра вместо буквы, регистр, пробел/пунктуация, прочая замена или вставка."""
    out = []
    for k, (op, ca, ct, pos) in enumerate(ops):
        if op == "eq":
            continue
        if op == "del":
            if ca == " ":
                cls = "spacing"
            elif not ca.isalnum():
                cls = "punct"
            else:
                cls = "omission"
        elif op == "ins":
            prev_t = next((o[2] for o in reversed(ops[:k]) if o[0] in ("eq", "sub", "ins") and o[2]), "")
            next_t = next((o[2] for o in ops[k + 1:] if o[0] in ("eq", "sub", "ins") and o[2]), "")
            if ct == " ":
                cls = "spacing"
            elif not ct.isalnum():
                cls = "punct"
            elif ct.lower() in (prev_t.lower(), next_t.lower()):
                cls = "doubling"
            else:
                cls = "insertion"
        else:  # sub
            la, lt = ca.lower(), ct.lower()
            if la == "ё" and lt == "е":
                cls = "yo_lost"
            elif la == lt:
                cls = "case"
            elif (la, lt) in DIGIT_PAIRS or (lt, la) in DIGIT_PAIRS or (ca.isalpha() and ct.isdigit()) or (ca.isdigit() and ct.isalpha()):
                cls = "digit_confusion"
            elif CYR.match(ca) and LAT.match(ct) and ct not in HOMO_LAT:
                cls = "latin_substitute"
            elif frozenset((la, lt)) in SIMILAR_CYR:
                cls = "similar_cyr"
            elif not ca.isalnum() or not ct.isalnum():
                cls = "punct"
            else:
                cls = "substitution"
        out.append({"class": cls, "op": op, "expected": ca, "got": ct, "pos": pos,
                    "context": exp[max(0, pos - 6):pos + 7]})
    return out


FAIL_CLASSES = {"omission", "doubling", "insertion", "substitution", "latin_substitute", "similar_cyr", "digit_confusion"}
# Классы, которые OCR ловит почти без ложных тревог (K/01): при уверенном OCR и строке ≥ min_line_h — сразу брак;
# остальные расхождения — «покажи человеку» (кроп строки и дифф).
ROBUST_CLASSES = {"omission", "doubling", "extra_text", "missing_line", "latin_substitute"}
# «Латинский нюх»: пары, где английская модель надёжно видит латиницу, которую русская исправила (K/01: D 5/5 при 1/144
# ложных, R 5/7 при 0/144, g 9/16 при 2/144); n, u, r — шумно (34, 8, 6 ложных из 144) — не используются.
SNIFF_PAIRS = {"Д": "D", "д": "g", "Я": "R", "я": "R"}


def latin_sniff(expected: list[str], lines_meta: list[dict] | None) -> list[dict]:
    en = " ".join(L.get("text_en", "") for L in (lines_meta or []) if L.get("text_en"))
    if not en or not expected:
        return []
    exp_all = " ".join(expected)
    xw, ew = exp_all.split(), en.split()
    hits = []
    for i, w in enumerate(xw):
        cand = ew[i] if len(ew) == len(xw) else en
        for c, L in SNIFF_PAIRS.items():
            if c in w and L in cand and L not in exp_all:
                hits.append({"word": w, "cyr": c, "latin": L, "en_reading": cand if len(ew) == len(xw) else en[:80]})
    return hits


def gned(expected_words: list[str], got_words: list[str]) -> float | None:
    """GNED (TIIF-Bench): венгерское сопоставление слов по нормированной дистанции + штраф |m − n|; 0 — идеально."""
    m, n = len(expected_words), len(got_words)
    if m == 0 and n == 0:
        return 0.0
    if m == 0 or n == 0:
        return 1.0
    try:
        import numpy as np
        from scipy.optimize import linear_sum_assignment
    except ImportError:
        return None
    C = np.ones((max(m, n), max(m, n)))
    for i, a in enumerate(expected_words):
        for j, b in enumerate(got_words):
            C[i, j] = lev(a, b) / max(len(a), len(b), 1)
    r, c = linear_sum_assignment(C)
    matched = sum(C[i, j] for i, j in zip(r, c) if i < m and j < n)
    return round(float((matched + abs(m - n)) / max(m, n)), 4)


def text_verdict(expected: list[str], transcript: str, case_sensitive: bool = False, yo_required: bool = True,
                 extra_allowed: bool = False, lines_meta: list[dict] | None = None, th: Th | None = None,
                 allowed: list[str] | None = None) -> dict:
    """Сверка ожидаемых строк брифа с транскриптом картинки (OCR, VLM или человек).
    Основа — stand_run.text_check агента E (двойники, латинские недвойники, лишние слова, ё); сверху — классы ошибок
    по выравниванию (пропуск, удвоение, похожая буква, цифра), точность и полнота слов, GNED, минимальная высота строки."""
    sr = mod("stand_run")
    base = sr.text_check(expected, transcript) if expected else {"lines": [], "fake_latin": [], "extra_words": []}
    pure_cyr = bool(expected) and not any(LAT.search(e) for e in expected)
    T = norm_text(transcript, all_homoglyphs=pure_cyr)
    Tc = T if case_sensitive else T.lower()
    lines, covered = [], [False] * len(Tc)
    for e in expected:
        E = norm_text(e, all_homoglyphs=pure_cyr)
        Ec = E if case_sensitive else E.lower()
        dist, j0, j1, ops = fit_align(Ec, Tc)
        cls = classify_ops(ops, Ec)
        for j in range(j0, j1):
            covered[j] = True
        found = dist <= max(1, len(Ec)) * 0.5
        lines.append({"expected": e, "found": found, "distance": dist, "cer": round(dist / max(1, len(Ec)), 4),
                      "match": Tc[j0:j1], "errors": cls if found else [],
                      "classes": sorted({c["class"] for c in cls}) if found else ["missing_line"]})
    # лишний текст: слова транскрипта вне найденных окон (WeGenBench: точность — «нет лишнего»); считаются только буквы
    # и цифры вне окон — висящая точка или кавычка от JPEG-шума не «лишнее слово» (K/01: «булок.» — ложный брак)
    extra, cur, start = [], "", 0
    for j, ch in enumerate(Tc + " "):
        if ch == " ":
            if cur and any(ch2.isalnum() and not covered[start + k] for k, ch2 in enumerate(cur)):
                extra.append(T[start:j])
            cur, start = "", j + 1
        else:
            cur += ch
    if allowed:   # разрешённый текст (этикетка товара и т. п.) — не «лишний»
        allow_words = {w.strip('.,:;!?"«»()') for x in allowed for w in norm_text(x, all_homoglyphs=pure_cyr).lower().split()}
        extra = [w for w in extra if w.lower().strip('.,:;!?"«»()') not in allow_words]
    exp_words = [w for e in expected for w in norm_text(e, all_homoglyphs=pure_cyr).lower().split()]
    got_words = Tc.split()
    counts: dict[str, int] = {}
    for L in lines:
        for c in L["classes"]:
            counts[c] = counts.get(c, 0) + 1
    fails = sorted({c for c in counts if c in FAIL_CLASSES or c == "missing_line"})
    if base.get("fake_latin") and not all(LAT.search(e) for e in expected):
        fails = sorted(set(fails) | {"latin_substitute"})
    if yo_required and counts.get("yo_lost"):
        fails = sorted(set(fails) | {"yo_lost"})
    if extra and not extra_allowed:
        fails = sorted(set(fails) | {"extra_text"})
    min_h = None
    if lines_meta:
        hs = [L.get("h_px") for L in lines_meta if L.get("h_px")]
        min_h = min(hs) if hs else None
    sniff = latin_sniff(expected, lines_meta)
    scores = [L.get("score_line", L.get("score_min")) for L in (lines_meta or []) if L.get("score_min") is not None]
    score_min = min(scores) if scores else None
    th = th or Th({"_flat": {}})
    h_fail = th("text.fail_min_line_h_px", 16)
    s_fail = th("text.fail_min_ocr_score", 0.9)
    if not fails and not sniff:
        verdict = "pass"
    elif fails and set(fails) <= ROBUST_CLASSES and (score_min is None or score_min >= s_fail) and \
            (min_h is None or min_h >= h_fail):
        verdict = "fail"
    else:
        verdict = "needs_human"
    res = {"expected": expected, "transcript": transcript, "normalized": T, "lines": lines, "classes": counts,
           "fake_latin": base.get("fake_latin", []), "latin_suspect": sniff, "extra_text": extra, "ocr_score_min": score_min,
           "verdict": verdict,
           "precision_words": round(1 - len(extra) / max(1, len(got_words)), 4) if got_words else (1.0 if not expected else 0.0),
           "recall_lines": round(sum(L["found"] and not (set(L["classes"]) & FAIL_CLASSES) for L in lines) / max(1, len(lines)), 4),
           "gned": gned(exp_words, got_words), "fail_classes": fails, "pass": verdict == "pass", "min_line_h_px": min_h}
    return res




# ================================================================ вызов утилит соседей: JSON из stdout


def call_json(fn, **kw):
    """Вызвать cmd_* соседа (печатает JSON в stdout) с Namespace и вернуть (код, JSON)."""
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(argparse.Namespace(**kw))
    txt = buf.getvalue().strip()
    try:
        return rc, json.loads(txt)
    except json.JSONDecodeError:
        # некоторые cmd_* печатают несколько строк: берём последний JSON-объект
        for chunk in reversed(re.split(r"\n(?=\{)", txt)):
            try:
                return rc, json.loads(chunk)
            except json.JSONDecodeError:
                continue
        return rc, {"_raw": txt[-500:]}


# ================================================================ паспорта polza.py / mp_client.py


def find_passport(path: Path) -> tuple[dict | None, Path | None]:
    """Паспорт рядом с файлом: <стем>.passport.json (для нескольких файлов генерации — без суффикса _N)."""
    stems = [path.stem, re.sub(r"_\d+$", "", path.stem)]
    for st in dict.fromkeys(stems):
        pp = path.with_name(st + ".passport.json")
        if pp.exists():
            try:
                return json.loads(pp.read_text(encoding="utf-8")), pp
            except json.JSONDecodeError:
                return None, pp
    return None, None


def passport_facts(pp: dict, pp_path: Path, path: Path) -> dict:
    job = pp.get("job") or {}
    meta = job.get("meta") or {}
    fentry = {}
    for f in pp.get("files") or []:
        fp = f.get("path") if isinstance(f, dict) else f
        if fp and Path(fp).name == path.name:
            fentry = f if isinstance(f, dict) else {"path": f}
            break
    cost = pp.get("cost") or {}
    body = ((pp.get("request") or {}).get("body") or {})
    inp = body.get("input") if isinstance(body.get("input"), dict) else body
    out = {"passport": rel(pp_path), "passport_schema": pp.get("schema"), "channel": pp.get("channel") or "polza-media",
           "model": pp.get("model") or job.get("model"), "provider_actual": pp.get("provider_actual"), "tag": job.get("tag"),
           "agent": job.get("agent"), "variant": job.get("variant"), "test": meta.get("test"),
           "task_code": meta.get("code") or meta.get("task_code") or meta.get("task"),
           "cost_rub": cost.get("usage_cost_rub"), "estimate_rub": cost.get("estimate_rub"),
           "requested": {k: inp.get(k) for k in ("aspect_ratio", "image_resolution", "resolution", "duration", "background",
                                               "output_format", "size", "generate_audio") if isinstance(inp, dict) and k in inp},
           "media": fentry.get("media"), "sha256_passport": fentry.get("sha256"),
           "prompt": (pp.get("prompt") or "")[:300] if isinstance(pp.get("prompt"), str) else None}
    for k in ("expect", "slot", "series", "brief", "spec", "text_zone", "palette", "control", "source", "target", "mask",
              "orig", "judge", "success"):
        if k in meta:
            out.setdefault("meta", {})[k] = meta[k]
    return out


def ratio_of(s) -> float | None:
    if not s or not isinstance(s, str) or ":" not in s:
        return None
    try:
        a, b = s.split(":")
        return float(a) / float(b)
    except (ValueError, ZeroDivisionError):
        return None


# ================================================================ режим по файлу

TASK_MODE = {"IMG-CUTOUT": "cutout", "IMG-EDIT": "edit", "IMG-OUTPAINT": "edit", "IMG-TEXTURE": "texture",
             "VID-ALPHA": "video-alpha", "VEC-ICON-LINE": "svg-icon", "VEC-ICON-FILLED": "svg-icon", "VEC-ILLUSTR": "svg-icon",
             "VEC-PATTERN": "svg-icon", "VEC-TRACE": "svg-icon"}
SLOT_OF_TASK = {"IMG-HERO-PHOTO": "hero", "IMG-BG-ABSTRACT": "hero", "IMG-PRODUCT": "product", "IMG-ICON3D": "section",
                "IMG-ILLUSTR": "section", "IMG-SERIES": "section", "IMG-TEXT-LATIN": "og", "IMG-TEXT-CYR": "og",
                "IMG-MOCKUP": "section", "IMG-TEXTURE": "texture", "VID-HERO-LOOP": "hero", "VID-CINEMAGRAPH": "hero"}


def image_alpha_info(path: Path) -> dict:
    from PIL import Image
    with Image.open(path) as im:
        has = im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info)
        if not has:
            return {"has_alpha": False}
        a = im.convert("RGBA").getchannel("A")
        hist = a.histogram()
        n = sum(hist)
        return {"has_alpha": True, "alpha_min": min(i for i, v in enumerate(hist) if v),
                "transparent_frac": round(sum(hist[:5]) / n, 4), "partial_frac": round(sum(hist[5:250]) / n, 4)}


def infer_mode(path: Path, facts: dict | None, a) -> str:
    ext = path.suffix.lower()
    if ext in SVG_EXT:
        return "svg-icon"
    code = (facts or {}).get("task_code") or getattr(a, "task", None)
    if ext in VID_EXT:
        if code == "VID-ALPHA" or getattr(a, "key", None):
            return "video-alpha"
        return "video-loop"
    if code in TASK_MODE:
        m = TASK_MODE[code]
        if m == "edit" and not getattr(a, "orig", None) and not ((facts or {}).get("meta") or {}).get("source"):
            return "image"
        return m
    if getattr(a, "orig", None):
        return "edit"
    if getattr(a, "slot", None) == "og":
        return "og"
    ai = image_alpha_info(path)
    if ai.get("has_alpha") and ai.get("transparent_frac", 0) > 0.01:
        return "cutout"
    return "image"


# ================================================================ картинка: загрузка и общие проверки


def load_rgb_np(path: Path, maxside: int | None = None, bg=(255, 255, 255)):
    import numpy as np
    from PIL import Image
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P", "PA"):
        im = im.convert("RGBA")
        base = Image.new("RGBA", im.size, bg + (255,))
        base.alpha_composite(im)
        im = base
    im = im.convert("RGB")
    if maxside and max(im.size) > maxside:
        s = maxside / max(im.size)
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def check_file_basics(R: Report, path: Path, facts: dict | None, a):
    from PIL import Image
    th = R.th
    st = path.stat()
    info = {"bytes": st.st_size, "sha256": sha256_file(path)}
    if facts and facts.get("sha256_passport") and facts["sha256_passport"] != info["sha256"]:
        R.defect("QA-FILE-CHANGED", "info", "файл отличается от скачанного (паспорт): производная — провенанс вендора мог "
                 "потеряться (C2PA не переживает перекодирование, H/04b)", value=facts["sha256_passport"][:12])
    if path.suffix.lower() in IMG_EXT:
        with Image.open(path) as im:
            info.update({"w": im.width, "h": im.height, "ratio": round(im.width / im.height, 4), "format": im.format,
                         "mode": im.mode, "icc": bool(im.info.get("icc_profile")), "exif": bool(im.info.get("exif"))})
        want = ratio_of((facts or {}).get("requested", {}).get("aspect_ratio")) or ratio_of(getattr(a, "ratio", None))
        if want:
            dev = abs(info["ratio"] / want - 1)
            info["ratio_requested"] = round(want, 4)
            if dev > th("image.ratio_tolerance", 0.02):
                R.defect("QA-DIMS-RATIO", "fail", f"пропорция {info['ratio']:.3f} вместо заказанной {want:.3f}",
                         metric="dims.ratio", value=info["ratio"], th_key="image.ratio_tolerance")
    R.checks["file"] = info
    return info


def check_budget(R: Report, info: dict, slot: str | None, a, kind="image"):
    """Бюджет веса — только для файлов на страницу (--stage web): A 01/01 §2–§4."""
    if getattr(a, "stage", "master") != "web" or not slot:
        return
    key = f"budget.{kind}.{slot}_kb"
    lim = R.th(key)
    if lim is None:
        return
    kb = info["bytes"] / 1024
    R.checks.setdefault("budget", {})[slot] = {"kb": round(kb, 1), "limit_kb": lim}
    if kb > lim:
        R.defect("QA-BUDGET", "warn", f"{kb:.0f} КБ > бюджета слота {slot} {lim} КБ", metric="file.bytes", value=round(kb, 1),
                 th_key=key)


def slop_color_metrics(path: Path) -> dict:
    im = mod("image_metrics")
    return im.metrics(im.load(str(path)))


def dna_reference_metrics(dna: dict | None, dna_path: Path | None) -> dict | None:
    """Средние цветовые метрики эталонов паспорта визуала (references) — основа порогов «к эталону бренда» (A/04, F/04)."""
    if not dna or not dna_path:
        return None
    refs = [r.get("src") for r in dna.get("references", []) if r.get("src")]
    vals = []
    for s in refs:
        p = (dna_path.parent / s)
        if p.exists():
            try:
                vals.append(slop_color_metrics(p))
            except Exception:  # noqa: BLE001
                pass
    if not vals:
        return None
    keys = ("colorfulness", "hdr_index", "sat_share", "warm_b")
    return {k: round(sum(v[k] for v in vals if v.get(k) is not None) / max(1, sum(1 for v in vals if v.get(k) is not None)), 4)
            for k in keys} | {"n": len(vals)}


def check_slop_color(R: Report, path: Path, ref: dict | None, dna: dict | None):
    th = R.th
    m = slop_color_metrics(path)
    R.checks["slop_color"] = m
    renderish = (m.get("chroma_med") or 0) < 0.005 and (m.get("clip_hi") or 0) > 0.1   # рендер на белом: пороги фото не применимы
    if ref:
        R.checks["slop_color"]["ref"] = ref
        rel_c = m["colorfulness"] / max(ref["colorfulness"], 1e-6)
        dh = m["hdr_index"] - ref["hdr_index"]
        if rel_c > th("image.colorfulness_max_rel", 1.2):
            R.defect("QA-COLOR-OVERSAT", "warn", f"colorfulness ×{rel_c:.2f} к эталонам бренда", metric="slop_color.colorfulness",
                     value=rel_c, th_key="image.colorfulness_max_rel", marker="IMG-M03")
        if dh > th("image.hdr_index_max_delta", 0.1):
            R.defect("QA-COLOR-HDR", "warn", f"hdr_index +{dh:.2f} к эталонам", metric="slop_color.hdr_index", value=dh,
                     th_key="image.hdr_index_max_delta", marker="IMG-M03")
        if rel_c > th("image.filter_colorfulness_rel", 1.5) and dh > th("image.hdr_index_max_delta", 0.1):
            R.defect("QA-FILTER-INSTAGRAM", "warn", "«Instagram-фильтр»: насыщенность +50 % и локальный контраст +0,1 к эталону",
                     metric="slop_color", value=round(rel_c, 2), th_key="image.filter_colorfulness_rel", marker="IMG-M03")
    elif not renderish:
        for k, key, code in (("colorfulness", "image.colorfulness_q3", "QA-COLOR-OVERSAT"), ("sat_share", "image.sat_share_q3", "QA-COLOR-OVERSAT"),
                             ("hdr_index", "image.hdr_index_q3", "QA-COLOR-HDR"), ("clip_hi", "image.clip_hi_q3", "QA-COLOR-CLIP")):
            v, lim = m.get(k), th(key)
            if v is not None and lim is not None and v > lim:
                R.defect(code, "warn", f"{k} {v} выше Q3 фото лидеров ({lim}) — посмотреть глазом, не брак сам по себе",
                         metric=f"slop_color.{k}", value=v, th_key=key, marker="IMG-M03")
    wb_neutral = bool(dna and ((dna.get("palette") or {}).get("neutral_wb") or {}).get("target_b", 1) <= 0.004)
    if m.get("warm_b") is not None and m["warm_b"] > th("image.warm_b_max", 4.0):
        R.defect("QA-COLOR-WARM", "warn" if wb_neutral or not dna else "info",
                 f"b* нейтралей +{m['warm_b']} — жёлтый сдвиг белого (у 9 из 51 фото лидеров это стиль, A/04)",
                 metric="slop_color.warm_b", value=m["warm_b"], th_key="image.warm_b_max", marker="IMG-M04")
    purple_ok = False
    if dna:
        for e in (dna.get("palette") or {}).get("image_palette", []) + (dna.get("palette") or {}).get("illustration_palette", []):
            try:
                _, C, H = mod("vlm_to_dna").hex_oklch(e["hex"])
                purple_ok |= C > 0.04 and 270 <= H <= 320
            except Exception:  # noqa: BLE001
                pass
    if (m.get("purple_share") or 0) > th("image.purple_share_max", 0.5) and not purple_ok:
        R.defect("QA-COLOR-PURPLE", "warn", f"пурпур 270–320° — {m['purple_share']:.2f} хроматических пикселей без пурпура в бренде",
                 metric="slop_color.purple_share", value=m["purple_share"], th_key="image.purple_share_max", marker="IMG-M05")
    return m


def text_zone_rect(a, facts: dict | None, spec: dict | None, dna: dict | None):
    """Зона текста: --text-zone x0,y0,x1,y1 → спецификация (composition.text_zone.rect) → паспорт визуала (сторона + доля)."""
    if getattr(a, "text_zone", None):
        v = [float(x) for x in a.text_zone.split(",")]
        return v, "--text-zone"
    tz = ((spec or {}).get("composition") or {}).get("text_zone") or ((facts or {}).get("meta") or {}).get("text_zone")
    if isinstance(tz, dict) and tz.get("rect"):
        return list(map(float, tz["rect"])), "spec"
    d = ((dna or {}).get("composition") or {}).get("text_zone_default")
    if d and d.get("side") in ("left", "right", "top", "bottom"):
        s = float(d.get("share", 0.4))
        rect = {"left": [0, 0, s, 1], "right": [1 - s, 0, 1, 1], "top": [0, 0, 1, s], "bottom": [0, 1 - s, 1, 1]}[d["side"]]
        return rect, "dna"
    return None, None


def check_composition(R: Report, path: Path, rect, slot: str | None, dna: dict | None, spec: dict | None):
    th = R.th
    cm = mod("composition_metrics")
    c = cm.analyse(str(path), tuple(rect) if rect else (0, 0, .45, 1))
    R.checks["composition"] = {k: c[k] for k in ("centroid_x", "centroid_y", "center_offset", "mirror_sym", "empty_share",
                                                 "zone_edge", "blobs")}
    comp = (dna or {}).get("composition") or {}
    region = comp.get("subject_region") or ((spec or {}).get("composition") or {}).get("subject_region")
    if rect and slot in ("hero", "og", None) and c["center_offset"] < th("composition.center_offset_min", 0.08):
        R.defect("QA-COMP-CENTER", "warn", "главное — строго по центру при заказанной зоне текста («средний вид»)",
                 metric="composition.center_offset", value=c["center_offset"], th_key="composition.center_offset_min",
                 marker="IMG-M09")
    if region == "right-third" and c["centroid_x"] < th("composition.centroid_x_min", 0.62):
        R.defect("QA-COMP-SIDE", "warn", f"центр значимости x = {c['centroid_x']} — не в правой трети", metric="composition.centroid_x",
                 value=c["centroid_x"], th_key="composition.centroid_x_min")
    if region == "left-third" and c["centroid_x"] > 1 - th("composition.centroid_x_min", 0.62):
        R.defect("QA-COMP-SIDE", "warn", f"центр значимости x = {c['centroid_x']} — не в левой трети", metric="composition.centroid_x",
                 value=c["centroid_x"], th_key="composition.centroid_x_min")
    maxel = comp.get("max_elements") or ((spec or {}).get("composition") or {}).get("max_elements")
    if maxel is None and slot == "hero":
        maxel = th("composition.blobs_max", 3)
    if maxel is not None and c["blobs"] > maxel:
        R.defect("QA-COMP-CLUTTER", "warn", f"пятен значимости {c['blobs']} > {maxel} — перегруженность", metric="composition.blobs",
                 value=c["blobs"], threshold=maxel, th_key="composition.blobs_max" if not comp.get("max_elements") else None)
    neg = comp.get("negative_space_min")
    if neg is not None and c["empty_share"] < neg:
        R.defect("QA-COMP-NO-AIR", "warn", f"спокойных клеток {c['empty_share']} < {neg}", metric="composition.empty_share",
                 value=c["empty_share"], threshold=neg)
    return c


def check_text_zone(R: Report, path: Path, rect, dna: dict | None, text_color: str | None):
    """F/02: плотность краёв зоны и скрим под текст (p99,9 → проверка F83 по худшему пикселю)."""
    th = R.th
    tz = mod("text_zone")
    img = tz.load(str(path), 1280)
    stats = tz.zone_stats(img, tuple(rect))
    out = {"rect": [round(x, 3) for x in rect], "edge_density": round(stats["edge_density"], 4), "L_std": round(stats["L_std"], 4),
           "colors": {}}
    q = th("text_zone.scrim_percentile", 99.9)
    target = th("text_zone.contrast_min", 4.5)
    colors = [text_color] if text_color else ["#ffffff", "#111111"]
    for col in colors:
        zc = tz.zone_contrast(img, tuple(rect), col)
        a_q = tz.scrim_alpha(img, tuple(rect), col, target, q)
        a_w = tz.scrim_alpha(img, tuple(rect), col, target, 100)
        out["colors"][col] = {"contrast_worst": round(zc["worst"], 2), "contrast_p95": round(zc["p95"], 2),
                              "f83_quick_no_scrim": zc["worst"] >= target, f"scrim_alpha_p{q}": a_q, "scrim_alpha_f83": a_w}
    best = min(out["colors"].items(), key=lambda kv: kv[1]["scrim_alpha_f83"])
    out["best_text_color"], out["best_scrim_alpha_f83"] = best[0], best[1]["scrim_alpha_f83"]
    R.checks["text_zone"] = out
    lim = th("text_zone.edge_density_max", 0.06)
    if stats["edge_density"] > lim:
        R.defect("QA-ZONE-BUSY", "warn", f"зона текста неспокойная: плотность краёв {stats['edge_density']:.3f} > {lim}",
                 metric="text_zone.edge_density", value=stats["edge_density"], th_key="text_zone.edge_density_max")
    if out["best_scrim_alpha_f83"] > th("text_zone.scrim_alpha_warn", 0.55):
        R.defect("QA-ZONE-SCRIM", "warn", f"для WCAG F83 нужна плашка α {out['best_scrim_alpha_f83']} даже для лучшего цвета текста "
                 f"({out['best_text_color']}) — «серая коробка»; сначала композиция", metric="text_zone.best_scrim_alpha_f83",
                 value=out["best_scrim_alpha_f83"], th_key="text_zone.scrim_alpha_warn")
    return out


def check_palette(R: Report, path: Path, dna: dict | None, spec: dict | None):
    """Палитра к паспорту визуала или спецификации: ΔE OKLab до палитры, снятой с картинки, и покрытие (F-05, vlm_to_dna)."""
    pal = []
    if dna:
        pal = [dict(e) for e in (dna.get("palette") or {}).get("image_palette", [])]
    if not pal and spec:
        pal = [dict(e) for e in spec.get("palette", [])]
    if not pal:
        return None
    vd = mod("vlm_to_dna")
    measured = vd.measure_image(str(path))
    rows = vd.palette_check([{"hex": e["hex"], "name": e.get("name") or e.get("role"),
                              "share": e.get("share", e.get("share_max", 0))} for e in pal], measured,
                            thr=R.th("palette.de_ok", 0.05))
    ok = sum(r["ok"] for r in rows)
    need = min(len(rows), R.th("palette.min_matched", 3))
    R.checks["palette"] = {"rows": rows, "matched": ok, "of": len(rows), "measured": measured["palette"]}
    if ok < need:
        R.defect("QA-PALETTE-OFF", "warn", f"цвета паспорта найдены {ok} из {len(rows)} (нужно ≥ {need} в ΔE OKLab ≤ "
                 f"{R.th('palette.de_ok', 0.05)})", metric="palette.matched", value=ok, th_key="palette.min_matched")
    return rows


# ================================================================ провенанс (информационно; решения — агент L)


def provenance(path: Path, out_dir: Path | None = None) -> dict:
    lp = TOOLS / "provenance_check.py"
    alt = sorted((EXP / "L").glob("*/provenance_check.py")) if (EXP / "L").exists() else []
    tool = lp if lp.exists() else (alt[0] if alt else None)
    if tool:   # утилита агента L: `provenance_check.py scan PATH --json F` (C2PA, IPTC/XMP, AIGC, подпись Recraft, маркеры)
        try:   # + `--corners` (ворота L 04 §5 п. 7): эвристика видимой метки в углах и лист углов для глаза / VLM
            sheet = None
            with tempfile.TemporaryDirectory() as td:
                jf = Path(td) / "p.json"
                cmd = [sys.executable, str(tool), "scan", str(path), "--json", str(jf)]
                if out_dir is not None:
                    cmd += ["--corners", "--out", str(Path(td) / "o")]
                subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                d = json.loads(jf.read_text(encoding="utf-8"))
                cs = Path(td) / "o" / "corners.jpg"
                if out_dir is not None and cs.exists():
                    sheet = Path(out_dir) / (path.stem + "_corners.jpg")
                    shutil.copyfile(cs, sheet)
            f = (d.get("files") or [{}])[0]
            s = f.get("summary") or {}
            return {"tool": f"{rel(tool)} {d.get('version', '')}".strip(), "c2pa_present": (f.get("c2pa") or {}).get("present"),
                    "c2pa": f.get("c2pa"), "digital_source_type": (f.get("exif") or {}).get("digital_source_type"),
                    "markers": f.get("bytes_markers"), "summary": s, "visible_suspect": s.get("visible_suspect") or [],
                    "corners_sheet": rel(sheet) if sheet else None}
        except Exception as e:  # noqa: BLE001
            return {"tool": rel(tool), "error": str(e)[:200]}
    out: dict = {"tool": "exiftool + c2patool (сырые факты; юридическая оценка — L)"}
    if EXIFTOOL.exists():
        try:
            r = subprocess.run(["perl", str(EXIFTOOL), "-j", "-a", "-G1", str(path)], capture_output=True, text=True, timeout=60)
            d = (json.loads(r.stdout) or [{}])[0]
            keep = {}
            for k, v in d.items():
                kl = k.lower()
                if any(s in kl for s in ("digitalsourcetype", "software", "creatortool", "c2pa", "jumbf", "credit", "aigc",
                                          "claim_generator", "make", "model", "description", "comment", "provenance")):
                    keep[k] = str(v)[:160]
            out["exif"] = keep
            out["xmp_digital_source_type"] = next((v for k, v in keep.items() if "digitalsourcetype" in k.lower()), None)
        except Exception as e:  # noqa: BLE001
            out["exif_error"] = str(e)[:200]
    if C2PATOOL.exists():
        try:
            r = subprocess.run([str(C2PATOOL), str(path)], capture_output=True, text=True, timeout=60)
            txt = (r.stdout or "") + (r.stderr or "")
            out["c2pa_present"] = r.returncode == 0 and '"manifests"' in txt
            if out["c2pa_present"]:
                j = json.loads(r.stdout)
                act = j.get("active_manifest")
                man = (j.get("manifests") or {}).get(act, {})
                out["c2pa"] = {"claim_generator": str(man.get("claim_generator"))[:120], "title": man.get("title"),
                               "issuer": ((man.get("signature_info") or {}).get("issuer")),
                               "validation_status": [s.get("code") for s in (j.get("validation_status") or [])][:8]}
        except Exception as e:  # noqa: BLE001
            out["c2pa_error"] = str(e)[:200]
    return out


# ================================================================ режимы


def audit_image(R: Report, path: Path, facts, a, ctx):
    info = check_file_basics(R, path, facts, a)
    slot = ctx["slot"]
    if slot in ("hero",) and max(info["w"], info["h"]) < R.th("image.hero_master_min_px", 2560):
        R.defect("QA-DIMS-SMALL", "info" if getattr(a, "stage", "master") == "master" else "warn",
                 f"длинная сторона {max(info['w'], info['h'])} px < мастера hero {R.th('image.hero_master_min_px', 2560)} px "
                 "(ступень 2K/4K модели или апскейл Lanczos, H 08/02 §1)", metric="file.w", value=max(info["w"], info["h"]),
                 th_key="image.hero_master_min_px")
    check_budget(R, info, slot, a)
    check_slop_color(R, path, ctx.get("ref_metrics"), ctx.get("dna"))
    rect, rect_src = text_zone_rect(a, facts, ctx.get("spec"), ctx.get("dna"))
    check_composition(R, path, rect, slot, ctx.get("dna"), ctx.get("spec"))
    if rect:
        tz = check_text_zone(R, path, rect, ctx.get("dna"), getattr(a, "text_color", None))
        tz["source"] = rect_src
    check_palette(R, path, ctx.get("dna"), ctx.get("spec"))
    if getattr(a, "master", None):
        check_ssimulacra(R, path, Path(a.master), slot)
    return R


def check_ssimulacra(R: Report, path: Path, master: Path, slot: str | None):
    """Производная для страницы против мастера: SSIMULACRA2 (H 08/04 §1.2: ≥ 80 hero, ≥ 70 прочее)."""
    s2 = kbpaths.bin_dir("libjxl", "tools", "ssimulacra2")
    if not s2.exists() or not master.exists():
        return
    with tempfile.TemporaryDirectory() as td:
        dec = Path(td) / "dec.png"
        ext = path.suffix.lower()
        if ext == ".avif":
            subprocess.run([str(kbpaths.bin_dir() / "libavif/avifdec"), str(path), str(dec)], capture_output=True)
        elif ext == ".webp":
            subprocess.run([str(kbpaths.bin_dir() / "libwebp/dwebp"), "-quiet", str(path), "-o", str(dec)], capture_output=True)
        elif ext == ".jxl":
            subprocess.run([str(kbpaths.bin_dir() / "libjxl/tools/djxl"), str(path), str(dec)], capture_output=True)
        else:
            from PIL import Image
            Image.open(path).convert("RGB").save(dec)
        ref = Path(td) / "ref.png"
        from PIL import Image
        m = Image.open(master).convert("RGB")
        d = Image.open(dec).convert("RGB")
        if d.size != m.size:
            m = m.resize(d.size, Image.LANCZOS)
        m.save(ref)
        r = subprocess.run([str(s2), str(ref), str(dec)], capture_output=True, text=True)
    try:
        score = float(r.stdout.strip().split()[-1])
    except (ValueError, IndexError):
        return
    key = "encoding.ssimulacra2_hero_min" if slot in ("hero", "product") else "encoding.ssimulacra2_min"
    lim = R.th(key, 80 if slot in ("hero", "product") else 70)
    R.checks["encoding"] = {"master": rel(master), "ssimulacra2": round(score, 2), "min": lim}
    if score < lim:
        R.defect("QA-ENCODE-QUALITY", "fail", f"SSIMULACRA2 {score:.1f} < {lim}: сжато заметно (avif_pick.sh подберёт q)",
                 metric="encoding.ssimulacra2", value=score, th_key=key)


def audit_cutout(R: Report, path: Path, facts, a, ctx):
    import numpy as np
    from PIL import Image
    info = check_file_basics(R, path, facts, a)
    check_budget(R, info, ctx["slot"], a)
    ac = mod("alpha_check")
    _, fake = call_json(ac.cmd_fake, img=str(path))
    R.checks["alpha_fake"] = fake
    if fake.get("verdict") == "FAKE_CHECKERBOARD":
        R.defect("QA-ALPHA-FAKE", "fail", "нарисованная шахматка вместо прозрачности (OpenAI: «checkerboard is not transparency»)",
                 metric="alpha_fake.checker_score", value=fake.get("checker_score"), marker="IMG-M23")
        return R
    if fake.get("verdict") == "OPAQUE":
        R.defect("QA-ALPHA-MISSING", "fail", "альфы нет: картинка непрозрачна — вырез не сделан", metric="alpha_fake.opaque_frac",
                 value=fake.get("opaque_frac"))
        return R
    _, halo = call_json(ac.cmd_halo, rgba=str(path), bg=getattr(a, "bg", None))
    R.checks["alpha_halo"] = halo
    if halo.get("transparent_frac", 0) < R.th("cutout.transparent_frac_min", 0.2):
        R.defect("QA-ALPHA-LITTLE", "warn", f"прозрачно лишь {halo.get('transparent_frac')} кадра — объект во весь кадр или "
                 "альфа почти не используется", metric="alpha_halo.transparent_frac", value=halo.get("transparent_frac"),
                 th_key="cutout.transparent_frac_min")
    im = Image.open(path).convert("RGBA")
    al_ = np.asarray(im)[..., 3]
    translucent = float(((al_ > 25) & (al_ < 230)).sum() / max(1, (al_ > 25).sum()))
    if (halo.get("halo_px") or 0) > R.th("cutout.halo_px_max", 2.0):
        # на полупрозрачном (стекло, дым, ткань) «ядро» alpha_check мало, и кайма законно отличается от него — ореол по этой
        # эвристике ложный (K: эталонный рендер матового флакона H/00 → 12 px); смотреть на контрастном фоне глазами
        glassy = getattr(a, "object", None) == "glass" or translucent > 0.25
        R.defect("QA-ALPHA-HALO", "info" if glassy else "warn",
                 f"ореол {halo.get('halo_px')} px (кайма цвета фона) — " + ("полупрозрачный объект: эвристика ненадёжна, смотреть на "
                 "чёрном и белом" if glassy else "деконтаминация или сужение края"), metric="alpha_halo.halo_px",
                 value=halo.get("halo_px"), th_key="cutout.halo_px_max")
    al = np.asarray(im)[..., 3]
    ys, xs = np.nonzero(al > 127)
    if len(xs):
        H, W = al.shape
        margin = min(xs.min() / W, ys.min() / H, (W - 1 - xs.max()) / W, (H - 1 - ys.max()) / H)
        obj = al > 127
        partial_in = float(((al > 25) & (al < 230)).sum() / max(1, (al > 25).sum()))
        R.checks["alpha_geometry"] = {"margin_frac": round(float(margin), 4), "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                                      "object_frac": round(float(obj.mean()), 4), "partial_in_object": round(partial_in, 4)}
        if margin < R.th("cutout.margin_min_frac", 0.02):
            R.defect("QA-ALPHA-MARGIN", "warn", f"поле {margin:.3f} стороны < 2 % — объект упирается в край, обрезаны кайма и тень",
                     metric="alpha_geometry.margin_frac", value=margin, th_key="cutout.margin_min_frac")
        kind = getattr(a, "object", None)
        if kind == "glass" and partial_in < R.th("cutout.glass_partial_min", 0.3):
            R.defect("QA-ALPHA-GLASS", "warn", f"стекло почти непрозрачно: полупрозрачных {partial_in:.2f} тела (< 0,3)",
                     metric="alpha_geometry.partial_in_object", value=partial_in, th_key="cutout.glass_partial_min")
        if kind in ("hair", "fur") and partial_in < R.th("cutout.fiber_partial_min", 0.03):
            R.defect("QA-ALPHA-FIBERS", "warn", f"волокна «подстрижены»: полупрозрачных {partial_in:.3f} (< 0,03)",
                     metric="alpha_geometry.partial_in_object", value=partial_in, th_key="cutout.fiber_partial_min")
    if getattr(a, "ref_alpha", None):
        _, m = call_json(ac.cmd_metrics, pred=str(path), gt=a.ref_alpha, rgb=None, src=None)
        R.checks["alpha_vs_ref"] = m
        kind = getattr(a, "object", None)
        key = "cutout.iou_min_fibers" if kind in ("hair", "fur") else "cutout.iou_min_solid"
        if m.get("iou") is not None and m["iou"] < R.th(key, 0.95):
            R.defect("QA-ALPHA-IOU", "fail", f"IoU с эталонной альфой {m['iou']} < {R.th(key)}", metric="alpha_vs_ref.iou",
                     value=m["iou"], th_key=key)
        if (m.get("band_mae_x1000") or 0) > R.th("cutout.band_mae_x1000_max", 150):
            R.defect("QA-ALPHA-EDGE", "warn", f"ошибка края {m['band_mae_x1000']} ×10⁻³ > 150", metric="alpha_vs_ref.band_mae_x1000",
                     value=m["band_mae_x1000"], th_key="cutout.band_mae_x1000_max")
    return R


def diff_mask(orig: Path, edited: Path, thr: float = 5.0, min_frac: float = 0.0005):
    """Маска изменений для безмасочной правки (D2: edit_check её не строит): подгонка цвета по «устойчивым» пикселям,
    ΔE00 > thr, открытие 3×3 и закрытие 5×5, компоненты ≥ min_frac кадра. Возвращает (маска bool, отчёт)."""
    import numpy as np
    from scipy import ndimage as ndi
    ec = mod("edit_check")
    O, E = ec.load_rgb(str(orig)), ec.load_rgb(str(edited))
    h, w = O.shape[:2]
    if E.shape[:2] != O.shape[:2]:
        E = ec.resize_to(E, w, h)
    de0 = ec.de2000(ec.srgb_to_lab(O), ec.srgb_to_lab(E))
    calm = de0 < np.percentile(de0, 60)
    gains = []
    for c in range(3):
        o, e = O[..., c][calm], E[..., c][calm]
        A = np.vstack([e, np.ones_like(e)]).T
        g, off = np.linalg.lstsq(A, o, rcond=None)[0]
        E[..., c] = np.clip(E[..., c] * g + off, 0, 1)
        gains.append([round(float(g), 4), round(float(off), 4)])
    de = ec.de2000(ec.srgb_to_lab(O), ec.srgb_to_lab(E))
    m = de > thr
    m = ndi.binary_opening(m, structure=np.ones((3, 3)))
    m = ndi.binary_closing(m, structure=np.ones((5, 5)))
    lab, n = ndi.label(m)
    comps = []
    if n:
        sizes = ndi.sum(np.ones_like(de), lab, range(1, n + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if s >= min_frac * h * w]
        m = np.isin(lab, keep)
        for i in keep:
            ys, xs = np.nonzero(lab == i)
            comps.append({"area_frac": round(float(len(xs) / (h * w)), 4),
                          "bbox_frac": [round(xs.min() / w, 3), round(ys.min() / h, 3), round(xs.max() / w, 3), round(ys.max() / h, 3)]})
        comps.sort(key=lambda c: -c["area_frac"])
    return m, {"color_match_gain_offset": gains, "changed_frac": round(float(m.mean()), 4), "regions": len(comps),
               "largest": comps[:6], "de_median_after_match": round(float(np.median(de)), 3)}


def local_shift(orig: Path, edited: Path, target_mask: str | None, mask_mode: str, band: int, de_thr: float, min_frac: float):
    """Локальный сдвиг вне цели после робастной подгонки цвета (своя проверка K поверх edit_check.py): подгонка по
    пикселям «вне цели» в 2 прохода (второй — без пикселей с остатком ΔE00 > 3), затем связные области ΔE00 > de_thr
    площадью ≥ min_frac «вне цели». Зачем: глобальная --match-color убирает общий сдвиг модели, и локальная утечка слабее
    ΔE00 5 перестаёт быть видна порогом edit_check (H/03 leak: 0,131 без подгонки → 0,0001 с подгонкой)."""
    import numpy as np
    from scipy import ndimage as ndi
    ec = mod("edit_check")
    O, E0 = ec.load_rgb(str(orig)), ec.load_rgb(str(edited))
    h, w = O.shape[:2]
    if E0.shape[:2] != O.shape[:2]:
        E0 = ec.resize_to(E0, w, h)
    tgt = ec.load_mask(target_mask, mask_mode, (h, w)) if target_mask else np.zeros((h, w), bool)
    far = ~ndi.binary_dilation(tgt, iterations=band) if tgt.any() else np.ones((h, w), bool)
    Lo = ec.srgb_to_lab(O)
    fit = far.copy()
    for it in range(2):
        E = E0.copy()
        for c in range(3):
            o, e = O[..., c][fit], E0[..., c][fit]
            g, off = np.linalg.lstsq(np.vstack([e, np.ones_like(e)]).T, o, rcond=None)[0]
            E[..., c] = np.clip(E0[..., c] * g + off, 0, 1)
        de = ec.de2000(Lo, ec.srgb_to_lab(E))
        if it == 0:
            keep = far & (de <= 3.0)
            if keep.sum() < 0.5 * far.sum():
                break
            fit = keep
    m = ndi.binary_opening((de > de_thr) & far, structure=np.ones((5, 5)))
    lab, n = ndi.label(m)
    dist = ndi.distance_transform_edt(~tgt) if tgt.any() else None
    regs = []
    if n:
        sizes = ndi.sum(np.ones_like(de), lab, range(1, n + 1))
        for i, sz in enumerate(sizes, 1):
            if sz >= min_frac * far.sum():
                reg = lab == i
                ys, xs = np.nonzero(reg)
                dmin = float(dist[reg].min()) / max(h, w) if dist is not None else None
                regs.append({"area_frac_outside": round(float(sz / far.sum()), 4), "de_median": round(float(np.median(de[reg])), 2),
                             "bbox_frac": [round(xs.min() / w, 3), round(ys.min() / h, 3), round(xs.max() / w, 3), round(ys.max() / h, 3)],
                             "dist_to_target_frac": round(dmin, 3) if dmin is not None else None,
                             "near_target": bool(dmin is not None and dmin <= 0.12)})
    regs.sort(key=lambda r: -r["area_frac_outside"])
    return {"fit_frac": round(float(fit.sum() / max(1, far.sum())), 4), "de_median_outside": round(float(np.median(de[far])), 3),
            "regions": regs[:6], "n_regions": len(regs)}


def audit_edit(R: Report, path: Path, facts, a, ctx):
    from PIL import Image
    info = check_file_basics(R, path, facts, a)
    orig = Path(a.orig) if getattr(a, "orig", None) else None
    if orig is None and facts and (facts.get("meta") or {}).get("source"):
        orig = ROOT / facts["meta"]["source"]
    if orig is None or not orig.exists():
        R.errors.append("режим edit: нужен --orig (исходник правки)")
        return R
    ec = mod("edit_check")
    outd = Path(ctx["out"]) / (path.stem + "_edit")
    outd.mkdir(parents=True, exist_ok=True)
    with Image.open(orig) as io_:
        ro = io_.width / io_.height
    re_ = info["w"] / info["h"]
    if abs(ro / re_ - 1) > 0.01:
        rc, rep = call_json(ec.cmd_outpaint, orig=str(orig), extended=str(path), out=str(outd), composite=True,
                            feather=max(4, int(0.005 * max(info["w"], info["h"]))))
        R.checks["outpaint"] = rep
        R.meta["edit_kind"] = "outpaint"
        if rep.get("verdict") == "REGENERATED":
            R.defect("QA-OUTPAINT-REGEN", "fail", "исходник в расширенном кадре перерисован (SSIM центра, ΔE00, резкость краёв) — "
                     "взять composite.png (исходник вставлен обратно)", metric="outpaint.edge_sharpness",
                     value=rep.get("edge_sharpness"), th_key="edit.outpaint_edge_sharpness_min",
                     evidence={"composite": rel(outd / "composite.png"), "sheet": rel(outd / "sheet.jpg")})
        return R
    mask = getattr(a, "mask", None)
    derived = None
    if not mask:
        m, drep = diff_mask(orig, path, R.th("edit.leak_de", 5.0))
        R.checks["diff_mask"] = drep
        if drep["changed_frac"] < R.th("edit.noedit_changed_min", 0.002):
            R.defect("QA-EDIT-NOEDIT", "fail", "правка почти ничего не изменила (< 0,2 % кадра)", metric="diff_mask.changed_frac",
                     value=drep["changed_frac"], th_key="edit.noedit_changed_min")
            return R
        if drep["changed_frac"] > R.th("edit.maskless_changed_max", 0.5):
            R.defect("QA-EDIT-REDRAW", "warn", f"изменено {drep['changed_frac']:.0%} кадра — перерисовка, а не правка",
                     metric="diff_mask.changed_frac", value=drep["changed_frac"], th_key="edit.maskless_changed_max")
        exp_n = getattr(a, "changes", None)
        if exp_n is not None and drep["regions"] > exp_n + R.th("edit.extra_regions_tolerance", 2):
            R.defect("QA-EDIT-EXTRA-REGIONS", "warn", f"изменённых областей {drep['regions']} при заказанных {exp_n} — утечка?",
                     metric="diff_mask.regions", value=drep["regions"], threshold=exp_n)
        from scipy import ndimage as ndi
        import numpy as np
        side = max(m.shape)
        mm = ndi.binary_dilation(m, iterations=max(2, int(R.th("edit.derived_mask_dilate_frac", 0.02) * side)))
        derived = outd / "diff_mask.png"
        Image.fromarray((mm * 255).astype(np.uint8)).save(derived)
        mask = str(derived)
        R.ask_human("Сравнить карту изменений с заказанными правками (безмасочная правка: цель неизвестна коду)",
                    "маска выведена из разницы — что изменено по заказу, а что утечка, решает глаз", ["QA-EDIT-DIFF"])
    feather = getattr(a, "feather", None)
    if not feather:
        feather = max(4, int(R.th("edit.feather_frac", 0.03) * max(info["w"], info["h"]))) if getattr(a, "removal", False) else 4
    rc, rep = call_json(ec.cmd_check, orig=str(orig), edited=str(path), mask=mask, mask_mode=getattr(a, "mask_mode", "white") if not derived else "white",
                        protect=getattr(a, "protect", None), band=6, thr=R.th("edit.leak_de", 5.0), out=str(outd),
                        composite=True, feather=feather, match_color=True, align="shift", leak_max=R.th("edit.leak_frac_max", 0.02))
    R.checks["edit"] = {k: rep.get(k) for k in ("verdict", "outside_leak_frac", "outside_de_median", "outside_ssim", "target_changed_frac",
                                               "global_drift", "edges_iou", "edges_iou_outside", "protect", "shift_px", "composite_outside_de_max")}
    R.checks["edit"]["mask"] = rel(mask) if derived else mask
    R.checks["edit"]["files"] = {"sheet": rel(outd / "sheet.jpg"), "composite": rel(outd / "composite.png"), "diff_heat": rel(outd / "diff_heat.png")}
    R.meta["edit_kind"] = "maskless" if derived else "mask"
    gd = (rep.get("global_drift") or {}).get("global_de00")
    if gd is not None and gd > R.th("edit.global_drift_max", 2.0):
        R.defect("QA-EDIT-DRIFT", "warn", f"общий сдвиг цвета ΔE00 {gd} > 2 — подогнан (--match-color); отдавать композит",
                 metric="edit.global_drift.global_de00", value=gd, th_key="edit.global_drift_max")
    if not derived:
        ls = local_shift(orig, path, mask, getattr(a, "mask_mode", "white"), 6, R.th("edit.local_shift_de", 3.0),
                         R.th("edit.local_shift_min_frac", 0.005))
        R.checks["edit"]["local_shift"] = ls
        if ls["n_regions"] and rep.get("verdict") != "LEAK":
            r0 = ls["regions"][0]
            R.defect("QA-EDIT-LOCAL-SHIFT", "warn", f"вне цели {ls['n_regions']} обл. сдвинуты на ΔE00 > {R.th('edit.local_shift_de', 3.0)} "
                     f"после робастной подгонки цвета (крупнейшая {r0['area_frac_outside']:.1%} «вне цели», ΔE {r0['de_median']}, "
                     f"{'рядом с целью' if r0['near_target'] else 'вдали от цели'}): утечка слабее порога edit_check или «призрак» "
                     "света и тени изменённого объекта (H 08/02 §2.4 — маска шире); смотреть лист, отдавать композит",
                     metric="edit.local_shift.n_regions",
                     value=ls["n_regions"], th_key="edit.local_shift_de", evidence=ls["regions"][:3])
        if rep.get("verdict") == "LEAK":
            R.defect("QA-EDIT-LEAK", "warn", f"утечка вне цели {rep.get('outside_leak_frac')} > 0,02 — композит исходника по маске "
                     "(composite.png), не перегенерация", metric="edit.outside_leak_frac", value=rep.get("outside_leak_frac"),
                     th_key="edit.leak_frac_max", evidence={"composite": rel(outd / "composite.png")})
        if rep.get("verdict") == "NO_EDIT":
            R.defect("QA-EDIT-NOEDIT", "fail", f"в цели изменено {rep.get('target_changed_frac')} (< 0,2) — правка не выполнена",
                     metric="edit.target_changed_frac", value=rep.get("target_changed_frac"), th_key="edit.target_changed_min")
    if getattr(a, "edit_kind", None) in ("light", "color") and rep.get("edges_iou") is not None and rep["edges_iou"] < R.th("edit.edges_iou_min", 0.9):
        R.defect("QA-EDIT-GEOMETRY", "warn", f"правка света/цвета изменила формы: edges_iou {rep['edges_iou']} < 0,9",
                 metric="edit.edges_iou", value=rep["edges_iou"], th_key="edit.edges_iou_min")
    pr = rep.get("protect")
    if pr and not pr.get("ok"):
        R.defect("QA-PROTECT-CHANGED", "fail", f"защищённый объект изменён: SSIM {pr.get('ssim')}, ΔE00 медиана {pr.get('de_median')} — "
                 "вставить оригинал товара по альфе", metric="edit.protect", value=pr.get("ssim"), th_key="edit.protect_ssim_min",
                 marker="IMG-M24")
    return R


def audit_texture(R: Report, path: Path, facts, a, ctx):
    info = check_file_basics(R, path, facts, a)
    check_budget(R, info, "texture", a)
    tc = mod("tile_check")
    rh, rv = tc.seam_ratio(tc.load(str(path)))
    mx = max(rh, rv)
    R.checks["tile"] = {"seam_ratio": [rh, rv], "max": mx}
    if mx > R.th("texture.seam_ratio_fail", 1.5):
        R.defect("QA-TILE-SEAM", "fail", f"шов тайла {mx} > 1,5 — tile_check.py cut (органика) или заделка креста маской",
                 metric="tile.max", value=mx, th_key="texture.seam_ratio_fail")
    elif mx > R.th("texture.seam_ratio_max", 1.3):
        R.defect("QA-TILE-SEAM", "warn", f"шов тайла {mx}: пограничный (1,3–1,5) — смотреть превью 2×2", metric="tile.max", value=mx,
                 th_key="texture.seam_ratio_max")
    R.ask_human("Превью тайла 2×2 и сдвиг 50 %: узнаваемое пятно повторяется?", "периодичность повторов метрика шва не ловит (H 08/03 §2.2)")
    return R


def luma_flicker(frames) -> dict:
    """Мерцание яркости (VID-M14): отклонение средней яркости кадра от медианного сглаживания по 11 кадрам, 0–255."""
    import numpy as np
    from scipy.ndimage import median_filter
    L = frames.reshape(len(frames), -1).mean(1)
    if len(L) < 7:
        return {"n": int(len(L))}
    sm = median_filter(L, size=11, mode="nearest")   # окно 11: вспышка на 3–4 кадра не «съедается» медианой (K/03)
    dev = np.abs(L - sm)
    return {"luma_mean": round(float(L.mean()), 2), "luma_range": round(float(L.max() - L.min()), 3),
            "flicker_max": round(float(dev.max()), 3), "flicker_p95": round(float(np.percentile(dev, 95)), 3)}


def audit_video(R: Report, path: Path, facts, a, ctx, alpha=False):
    vl = mod("video_loop_check")
    pr = vl.probe(str(path)) if path.is_file() else {}
    R.checks["probe"] = pr
    R.checks["file"] = {"bytes": path.stat().st_size if path.is_file() else None,
                        "sha256": sha256_file(path) if path.is_file() else None}
    if pr.get("audio"):
        R.defect("QA-VIDEO-AUDIO", "warn", f"звуковая дорожка {pr['audio']} — снять `-an` при кодировании (фон-видео без звука)",
                 metric="probe.audio", value=",".join(pr["audio"]))
    if alpha and pr.get("pix_fmt") and "yuva" in str(pr.get("pix_fmt")):
        R.checks["alpha_video"] = {"pix_fmt": pr["pix_fmt"], "note": "альфа в потоке (VP9-alpha читает libvpx, не встроенный декодер)"}
    if alpha and not ("yuva" in str(pr.get("pix_fmt") or "")):
        _, ch = call_json(vl.cmd_chroma, video=str(path), key=getattr(a, "key", None) or "auto", de=R.th("video_alpha.key_de", 5),
                          width=320)
        R.checks["chroma"] = ch
        if ch.get("bg_ok_min", 1) < R.th("video_alpha.bg_ok_min", 0.95):
            R.defect("QA-CHROMA-BG", "fail", f"фон-ключ неоднороден: доля фона в ΔE00 ≤ 5 — {ch.get('bg_ok_min')} (< 0,95)",
                     metric="chroma.bg_ok_min", value=ch.get("bg_ok_min"), th_key="video_alpha.bg_ok_min")
        if ch.get("obj_drift_max_pct_w", 0) > R.th("video_alpha.obj_drift_max_pct_w", 2.0):
            R.defect("QA-CHROMA-DRIFT", "warn", f"объект уплывает на {ch.get('obj_drift_max_pct_w')} % ширины (> 2)",
                     metric="chroma.obj_drift_max_pct_w", value=ch.get("obj_drift_max_pct_w"),
                     th_key="video_alpha.obj_drift_max_pct_w")
    fr = vl.load(str(path), 320)
    rgb = vl.load(str(path), 96, "rgb")
    m = vl.loop_metrics(fr, 0.25, rgb, vl.src_width(str(path)) / 320)
    ctrl = getattr(a, "control", None)
    if ctrl:
        c = vl.loop_metrics(vl.load(ctrl, 320), 0.25)
        m["control_motion_med"] = c["motion_med"]
        m["motion_vs_control"] = round(m["motion_med"] / max(c["motion_med"], 1e-6), 2)
    master = getattr(a, "master", None)
    if master and Path(master).suffix.lower() in VID_EXT and Path(master).resolve() != path.resolve():
        # сжатие «замораживает» тихую петлю: motion_keep = motion_med финала / мезонина (J 10-web-integration/02 §6.1)
        mm = vl.loop_metrics(vl.load(str(master), 320), 0.25)
        m["master_motion_med"] = mm["motion_med"]
        m["motion_keep"] = round(m["motion_med"] / max(mm["motion_med"], 1e-6), 2)
    m.pop("_curve", None)
    m["verdict"] = vl.verdict(m)
    m["flicker"] = luma_flicker(fr)
    R.checks["loop"] = m
    th = R.th
    lossless = "4:4:4" in str(pr.get("profile") or "") or str(pr.get("pix_fmt") or "").startswith(("yuv444", "rgb", "gbr"))
    lossy_final = (pr.get("codec") in ("h264", "hevc", "vp9", "av1") and not getattr(a, "mezzanine", False) and not lossless
                   and (pr.get("kbps") or 0) < th("video.mezzanine_kbps_min", 15000))
    quiet = m["motion_med"] < th("video.quiet_motion_med", 0.3)
    seam = m["trim"]["seam_ratio_local_after"]
    if not alpha:
        if seam > th("video.seam_local_max", 1.5):
            if lossy_final and quiet:
                R.defect("QA-LOOP-SEAM", "needs_human", f"шов {seam} на сжатом файле тихой петли: пульс ключевого кадра даёт ложный шов "
                         "(I/02: 0,98 → 3,4) — мерить мезонин или выход модели до перекодирования", metric="loop.trim.seam_ratio_local_after",
                         value=seam, th_key="video.seam_local_max", marker="VID-M12")
            else:
                R.defect("QA-LOOP-SEAM", "fail", f"шов петли {seam} > 1,5 после среза — кроссфейд хвоста 12 кадров или мост (I 09/01 §3)",
                         metric="loop.trim.seam_ratio_local_after", value=seam, th_key="video.seam_local_max", marker="VID-M12")
        if m["trim"]["start"] or m["trim"]["end"]:
            R.defect("QA-LOOP-TRIM", "info", f"срезать кадры: начало {m['trim']['start']}, конец {m['trim']['end']} "
                     f"(дубль последнего — {m['dup_last']}) → video_loop_check.py trim --auto", metric="loop.trim",
                     value=m["trim"]["end"] + m["trim"]["start"])
        if m["pingpong_suspect"]:
            R.defect("QA-LOOP-PINGPONG", "warn", "похоже на пинг-понг (кадры зеркальны во времени): движение разворачивается",
                     metric="loop.mirror_ratio", value=m["mirror_ratio"], marker="VID-M12")
    if (m.get("cut_ratio") or 0) >= th("video.cut_ratio_max", 10):
        R.defect("QA-LOOP-CUT", "fail", f"склейка (локальный пик {m['cut_ratio']} ≥ 10 на кадре {m['cut_at']}) — мульти-шот выключить",
                 metric="loop.cut_ratio", value=m["cut_ratio"], th_key="video.cut_ratio_max", marker="VID-M15")
    elif (m.get("cut_ratio") or 0) >= th("video.event_ratio_warn", 4):
        R.defect("QA-LOOP-EVENT", "info", f"всплеск движения ×{m['cut_ratio']} на кадре {m['cut_at']}: событие в фоновой петле?",
                 metric="loop.cut_ratio", value=m["cut_ratio"], th_key="video.event_ratio_warn", marker="VID-M18")
    if m["collapse_suspect"]:
        R.defect("QA-LOOP-COLLAPSE", "fail", "движение угасает (длинный мёртвый конец) — браковать, перегенерировать",
                 metric="loop.dead_end", value=m["dead_end"])
    elif min(m["head_motion"], m["tail_motion"]) < th("video.head_tail_min", 0.5):
        R.defect("QA-LOOP-FADE", "warn", f"движение слабеет к краю: голова {m['head_motion']}, хвост {m['tail_motion']} (< 0,5)",
                 metric="loop.tail_motion", value=min(m["head_motion"], m["tail_motion"]), th_key="video.head_tail_min")
    if (m.get("static_frac") or 0) > th("video.static_frac_max", 0.3):
        R.defect("QA-LOOP-STATIC", "warn", f"«замёрзших» пар кадров {m['static_frac']} > 0,3 (заморозки, дубли кадров)",
                 metric="loop.static_frac", value=m["static_frac"], th_key="video.static_frac_max")
    if "motion_vs_control" in m:
        if m["motion_vs_control"] < th("video.motion_vs_control_min", 0.5):
            R.defect("QA-LOOP-WEAK-MOTION", "fail", f"движения {m['motion_vs_control']} от i2v-контроля (< 0,5) — статичный коллапс",
                     metric="loop.motion_vs_control", value=m["motion_vs_control"], th_key="video.motion_vs_control_min")
    elif not alpha:
        R.defect("QA-LOOP-NO-CONTROL", "info", "нет i2v-контроля (--control): равномерно слабое движение метрикой не видно (I/02)")
    if "motion_keep" in m and m["motion_keep"] < th("video.motion_keep_min", 0.75):
        R.defect("QA-ENCODE-MOTION", "warn", f"сжатие съело движение: motion_keep {m['motion_keep']} к мастеру (< 0,75) — CRF ниже "
                 "(J/05: AV1 CRF 36 тихих петель 0,24–0,77; AV1 24–28, H.264 18–20)", metric="loop.motion_keep", value=m["motion_keep"],
                 th_key="video.motion_keep_min")
    if not alpha and m["cam_shift_max_px"] >= th("video.cam_shift_max_px", 1.0) and not getattr(a, "camera_move", False):
        R.defect("QA-VIDEO-CAM-CREEP", "warn", f"кадр ползёт на {m['cam_shift_max_px']} px — «ползущая камера» ломает шов",
                 metric="loop.cam_shift_max_px", value=m["cam_shift_max_px"], th_key="video.cam_shift_max_px", marker="VID-M07")
    for k in ("seam_dE00", "color_drift_dE00"):
        if m.get(k) is not None and m[k] >= th("video.color_de_max", 2.0):
            R.defect("QA-LOOP-COLOR", "warn", f"{k} {m[k]} ≥ 2 — цвет плывёт", metric=f"loop.{k}", value=m[k],
                     th_key="video.color_de_max", marker="VID-M14")
    fl = m["flicker"]
    if fl.get("flicker_max") is not None and fl["flicker_max"] > th("video.flicker_max", 2.0):
        R.defect("QA-VIDEO-FLICKER", "info", f"яркость кадра «дышит»: отклонение до {fl['flicker_max']} из 255 [не откалибровано]",
                 metric="loop.flicker.flicker_max", value=fl["flicker_max"], th_key="video.flicker_max", marker="VID-M14")
    if getattr(a, "mask", None):
        _, dr = call_json(vl.cmd_drift, video=str(path), mask=a.mask, width=320)
        R.checks["cinemagraph_drift"] = dr
        if dr.get("drift_max", 0) >= th("video.cinemagraph_drift_max", 1.0) or dr.get("dE00_max", 0) >= th("video.color_de_max", 2.0) \
                or dr.get("cam_shift_max_px", 0) >= th("video.cam_shift_max_px", 1.0):
            R.defect("QA-CINEMAGRAPH-DRIFT", "warn", f"неподвижные зоны плывут: drift {dr.get('drift_max')}, ΔE00 {dr.get('dE00_max')}, "
                     f"камера {dr.get('cam_shift_max_px')} px", metric="cinemagraph_drift.drift_max", value=dr.get("drift_max"),
                     th_key="video.cinemagraph_drift_max")
    dur = pr.get("duration_s") or 0
    if dur and not (th("video.loop_len_min_s", 4) <= dur <= th("video.loop_len_max_s", 10)) and not alpha:
        R.defect("QA-LOOP-LENGTH", "info", f"длительность {dur:.1f} с вне 4–10 с для фоновой петли", metric="probe.duration_s", value=dur)
    if getattr(a, "stage", "master") == "web" and path.is_file():
        kb = path.stat().st_size / 1024
        key = "budget.video.hero_1080_kb" if (pr.get("h") or 0) >= 1000 else "budget.video.hero_720_kb"
        lim = th(key)
        if lim and kb > lim:
            R.defect("QA-BUDGET", "warn", f"{kb:.0f} КБ > бюджета {lim} КБ", metric="file.bytes", value=round(kb), th_key=key)
    sheet = Path(ctx["out"]) / (path.stem + "_sheet.jpg")
    call_json(vl.cmd_sheet, video=str(path), out=str(sheet), n=12, cols=4)
    R.checks["sheet"] = rel(sheet)
    return R


def svg_colors(txt: str) -> list[str]:
    cols = re.findall(r"(?:fill|stroke|stop-color)\s*[:=]\s*[\"']?\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|white|black)", txt)
    return sorted(set(c.lower() for c in cols))


def audit_svg(R: Report, path: Path, facts, a, ctx):
    info = check_file_basics(R, path, facts, a)
    raw = path.read_bytes()
    si = mod("mp_client").svg_info(raw)
    txt = raw.decode("utf-8", "replace")
    root = re.search(r"<svg\b[^>]*>", txt)
    tag = root.group(0) if root else ""
    si["preserveAspectRatio_none"] = 'preserveAspectRatio="none"' in tag
    si["colors_all"] = svg_colors(txt)
    line_like = bool(re.search(r'stroke-width="', txt)) and ('fill="none"' in tag or "fill=\"none\"" in txt[:400])
    si["style"] = "line" if line_like else "filled"
    R.checks["svg"] = si
    if not si["root_svg"]:
        R.defect("QA-SVG-INVALID", "fail", "нет корня <svg>")
        return R
    if si["has_image"]:
        R.defect("QA-SVG-RASTER", "fail", "внутри SVG растр <image> — это не вектор (перекраска и масштаб не работают)")
    if si["has_text"]:
        R.defect("QA-SVG-TEXT", "warn", "в SVG есть <text> — зависит от шрифтов; перевести в кривые или HTML")
    if si["preserveAspectRatio_none"]:
        R.defect("QA-SVG-ROOT", "warn", 'корень с preserveAspectRatio="none" — искажение при другой пропорции (G/02)')
    if not si.get("viewBox"):
        R.defect("QA-SVG-ROOT", "warn", "нет viewBox — не масштабируется")
    first = re.search(r"<svg\b[^>]*>\s*(?:<[^>]+>\s*)?<(rect|path)\b([^>]*)>", txt)
    if first and first.group(1) == "rect" and re.search(r'width="100%"|width="' + re.escape(str(si.get("width") or "")) + '"', first.group(2) or ""):
        R.defect("QA-SVG-BG", "warn", "первым идёт прямоугольник во весь холст — фон: удалить до svgo (G/02)")
    if si.get("recraft_signature"):
        R.defect("QA-SVG-SIGNATURE", "info", "подпись провенанса Recraft — не удалять при svgo (конфиг keep-signature, G/02; L)")
    light = any(c in ("#fff", "#ffffff", "white", "#fefefe") for c in si["colors_all"])
    dark = any(c in ("#000", "#000000", "black") or (c.startswith("#") and len(c) in (4, 7) and int(c[1:2], 16) < 4)
               for c in si["colors_all"])
    if si["style"] == "filled" and light and dark:
        R.defect("QA-SVG-PAINTED-HOLES", "warn", "светлые фигуры поверх тёмных — «дырки» нарисованы цветом фона: в тёмной теме "
                 "и с currentColor будет пятно (G/02: 3 из 5 иконок Recraft) — проверить рендер на тёмном фоне")
    kb = info["bytes"] / 1024
    lim = R.th("svg.icon_kb_max", 10) if ctx["slot"] in ("icon", None) else R.th("svg.illustration_kb_max", 100)
    if kb > lim:
        R.defect("QA-SVG-HEAVY", "warn", f"{kb:.1f} КБ > {lim} КБ — svgo (−57…−65 % у Recraft) или растр AVIF", metric="file.bytes",
                 value=round(kb, 1), threshold=lim)
    if si["style"] == "line":
        check_icons(R, path)
    R.ask_human("Узнаётся ли метафора иконки за 5 секунд без подписи?", "новые метафоры узнаются 2 из 5 (G/01); геометрию код "
                "проверяет, смысл — человек или VLM с контролем (G-06)")
    return R


def check_icons(R: Report, path: Path):
    """G/check_icons.py (пороги по Lucide 1.47) — в venv-G; иконка копируется во временную папку."""
    if not VENV_G.exists():
        R.errors.append("нет venv-G — check_icons не запущен")
        return
    with tempfile.TemporaryDirectory() as td:
        shutil.copy(path, Path(td) / path.name)
        out = Path(td) / "r.json"
        r = subprocess.run([str(VENV_G), str(G_EXP / "check_icons.py"), td, "--ref", str(LUCIDE_REF), "--json", str(out)],
                           capture_output=True, text=True, timeout=300)
        if not out.exists():
            R.errors.append(f"check_icons: {(r.stderr or r.stdout)[-300:]}")
            return
        res = json.loads(out.read_text(encoding="utf-8")).get(path.stem, {})
    R.checks["icon"] = res
    for f in res.get("flags", []):
        code, lvl = {"шапка": ("QA-SVG-HEADER", "fail"), "цвет": ("QA-SVG-COLOR", "fail")}.get(f.split()[0], (None, None))
        if code is None:
            code = {"поле<1": "QA-SVG-MARGIN", "зазор": "QA-SVG-GAP", "узко": "QA-SVG-NARROW", "вес": "QA-SVG-WEIGHT",
                    "центр": "QA-SVG-CENTER", "сетка": "QA-SVG-GRID"}.get(f.split()[0], "QA-SVG-FLAG")
            lvl = "warn"
        R.defect(code, lvl, f"check_icons: {f} (пороги по Lucide 1.47, G/01)", metric="icon.flags", value=f,
                 th_key="svg.check_icons_flags")


def audit_og(R: Report, path: Path, facts, a, ctx):
    audit_image(R, path, facts, a, ctx)
    info = R.checks["file"]
    W, H = info["w"], info["h"]
    ok = (W, H) in ((1200, 630), (2400, 1260))
    if not ok:
        R.defect("QA-OG-SIZE", "warn" if abs(W / H - 1.905) < 0.02 else "fail", f"{W}×{H} вместо 1200×630 (1,91:1)",
                 metric="file.w", value=f"{W}x{H}", th_key="og.size")
    if info.get("format") not in ("PNG", "JPEG"):
        R.defect("QA-OG-FORMAT", "warn", f"формат {info.get('format')} — для OG PNG или JPEG (не AVIF)", th_key="og.formats")
    kb = info["bytes"] / 1024
    if kb > R.th("og.kb_max", 300):
        R.defect("QA-OG-WEIGHT", "warn", f"{kb:.0f} КБ > 300 КБ", metric="file.bytes", value=round(kb), th_key="og.kb_max")
    return R


MODES = {"image": audit_image, "cutout": audit_cutout, "edit": audit_edit, "texture": audit_texture,
         "video-loop": lambda R, p, f, a, c: audit_video(R, p, f, a, c, alpha=False),
         "video-alpha": lambda R, p, f, a, c: audit_video(R, p, f, a, c, alpha=True),
         "svg-icon": audit_svg, "og": audit_og}


# ================================================================ текст (OCR) пачкой и «незаказанный текст»


def apply_text(reports: list[Report], ocr_res: dict, a):
    for R in reports:
        o = ocr_res.get(str(R.path.resolve()))
        exp = R.meta.get("_expect")
        if o is None:
            continue
        if "error" in o:
            R.errors.append(f"OCR: {o['error']}")
            continue
        lines = o.get("lines", [])
        R.checks["ocr"] = {"lines": [{k: L.get(k) for k in ("text", "score_min", "score_line", "h_px", "box", "text_en")} for L in lines],
                           "lang": o.get("lang"), "elapsed_s": o.get("elapsed_s")}
        if exp:
            tv = text_verdict(exp, "\n".join(L["text"] for L in lines), lines_meta=lines, th=R.th,
                              yo_required=not getattr(a, "yo_optional", False), allowed=getattr(a, "allow_text", None))
            R.checks["text"] = {k: tv[k] for k in ("verdict", "fail_classes", "classes", "extra_text", "latin_suspect", "fake_latin",
                                                   "precision_words", "recall_lines", "gned", "ocr_score_min", "min_line_h_px")}
            R.checks["text"]["lines"] = [{k: L[k] for k in ("expected", "found", "cer", "match", "classes")} for L in tv["lines"]]
            if tv["verdict"] == "fail":
                R.defect("QA-TEXT-MISMATCH", "fail", f"текст не совпал с брифом: {', '.join(tv['fail_classes'])}", metric="text.fail_classes",
                         value=",".join(tv["fail_classes"]), th_key="text.fail_min_ocr_score", marker="IMG-M12")
            elif tv["verdict"] == "needs_human":
                why = ", ".join(tv["fail_classes"] + (["latin_suspect"] if tv["latin_suspect"] else [])) or "неуверенный OCR"
                R.defect("QA-TEXT-CHECK", "needs_human", f"текст прочитать глазами по буквам на 200 %: {why}", metric="text.fail_classes",
                         value=why, marker="IMG-M12")
        else:
            words = [L for L in lines if sum(ch.isalnum() for ch in L["text"]) >= R.th("text.unrequested_min_chars", 2)
                     and L.get("score_min", 0) >= R.th("text.unrequested_min_score", 0.6)]
            if words:
                R.defect("QA-TEXT-UNREQUESTED", "warn", f"на картинке найден незаказанный текст ({len(words)} строк: "
                         f"{'; '.join(L['text'][:30] for L in words[:3])}) — псевдотекст или вывеска", metric="ocr.lines",
                         value=len(words), th_key="text.unrequested_min_score", marker="IMG-M12")


# ================================================================ маркеры-кластер и человек


HUMAN_DEFAULT = {
    "image": ["5-секундный взгляд в слоте на странице: что заметно сразу (кинематографизация, фильтр, пурпур, клише, центр)",
              "Зум 200 % по сетке 3×3: руки, лица, надписи, мелкие предметы, фон-«каша» (IMG-M01, M11, M12, M15, M17)",
              "Перечислить предметы: каждый работает как в жизни? (функциональные ошибки — 58,7 % трудных ИИ-картинок, Kamali 2025)",
              "Эстетика и «годится как финальный ассет» — решает человек (у Google нет автооценщика эстетики)"],
    "cutout": ["Объект на чёрном, белом и фото-фоне, край на 200 %: ореол, «стриженые» волосы, дыры, мутное стекло"],
    "edit": ["Лист «оригинал | правка | карта | композит»: правка выполнена? остальное не испорчено? (раздельно, GEditBench v2)"],
    "texture": [],
    "video-loop": ["Три повтора подряд на полном размере и на телефоне: пауза, «вспышка» кадра 0, разворот, застывший фон",
                   "Покадрово 0 / 25 / 50 / 75 / 100 %: морфинг, «кипение» фактур, плывущий текст (VID-M01…M03, M11)"],
    "video-alpha": ["Альфа на двух контрастных фонах, край объекта во движении: «кипение», зелёный отсвет на металле"],
    "svg-icon": ["Иконки набора рядом в 24 px и на тёмном фоне: вес линий, узнаваемость, «дырки» цветом фона"],
    "og": ["Превью карточки 600×315 и обрезка 1:1: заголовок читается, ключевое внутри 1100×530"],
}


def finish(R: Report, slot: str | None):
    th = R.th
    n = len(R.markers)
    key_slot = slot in ("hero", "product", "og")
    lim = th("slop.key_slot_markers", 2) if key_slot else th("slop.cluster_markers", 3)
    R.meta["markers_suspected"] = n
    if n >= lim:
        R.defect("QA-SLOP-CLUSTER", "needs_human", f"метрики подозревают {n} маркеров ({', '.join(sorted(R.markers))}) — порог "
                 f"кластера {lim} ({'ключевой слот' if key_slot else 'обычный'}): подтвердить глазом или VLM-рубрикой",
                 value=n, th_key="slop.key_slot_markers" if key_slot else "slop.cluster_markers")
    for item in HUMAN_DEFAULT.get(R.mode, []):
        R.ask_human(item, "ручная приёмка ≈ 2 мин (11-evaluation-qa/03)")


# ================================================================ контактный лист


def contact_panel(R: Report, out_dir: Path) -> str | None:
    """Панель для человека: картинка с зоной текста, центром значимости и рамками OCR + полоса вердикта."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    if R.mode.startswith("video"):
        return R.checks.get("sheet")
    if R.path.suffix.lower() in SVG_EXT:
        return None
    try:
        im = Image.open(R.path)
        if im.mode in ("RGBA", "LA", "P", "PA"):
            im = im.convert("RGBA")
            chk = Image.new("RGBA", im.size, (0, 0, 0, 0))
            d0 = ImageDraw.Draw(chk)
            s = 16
            for y in range(0, im.height, s):
                for x in range(0, im.width, s):
                    d0.rectangle([x, y, x + s - 1, y + s - 1], fill=(200, 200, 200, 255) if (x // s + y // s) % 2 else (240, 240, 240, 255))
            chk.alpha_composite(im)
            im = chk
        im = im.convert("RGB")
        W = 960
        sc = W / im.width
        im = im.resize((W, max(1, round(im.height * sc))), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        tz = R.checks.get("text_zone")
        if tz:
            x0, y0, x1, y1 = tz["rect"]
            d.rectangle([x0 * im.width, y0 * im.height, x1 * im.width - 1, y1 * im.height - 1], outline=(0, 200, 255), width=3)
        comp = R.checks.get("composition")
        if comp:
            cx, cy = comp["centroid_x"] * im.width, comp["centroid_y"] * im.height
            d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=(255, 60, 60), width=3)
        for L in (R.checks.get("ocr") or {}).get("lines", []):
            b = L.get("box")
            if b:
                d.rectangle([b[0] * sc, b[1] * sc, b[2] * sc, b[3] * sc], outline=(255, 210, 0), width=2)
        v = R.verdict()
        col = {"pass": (40, 160, 70), "warn": (220, 160, 0), "needs_human": (40, 110, 220), "fail": (210, 40, 40)}[v]
        bar = Image.new("RGB", (W, 64), col)
        db = ImageDraw.Draw(bar)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
            font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except OSError:
            font = font2 = ImageFont.load_default()
        db.text((10, 6), f"{v.upper()} · {R.mode} · {R.path.name[:60]}", fill=(255, 255, 255), font=font)
        codes = [d_["code"] for d_ in R.defects if d_["level"] != "info"][:8]
        db.text((10, 36), ", ".join(codes) or "дефектов нет", fill=(255, 255, 255), font=font2)
        sheet = Image.new("RGB", (W, im.height + 64), (20, 20, 20))
        sheet.paste(bar, (0, 0))
        sheet.paste(im, (0, 64))
        out = out_dir / (R.path.stem + "_panel.jpg")
        sheet.save(out, quality=85)
        return rel(out)
    except Exception as e:  # noqa: BLE001
        R.errors.append(f"контактный лист: {e}"[:200])
        return None


def index_sheet(reports: list[Report], out: Path, cols: int = 4, cell: int = 320):
    from PIL import Image, ImageDraw, ImageFont
    items = [(R, R.meta.get("panel")) for R in reports if R.meta.get("panel")]
    if not items:
        return None
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 4)), (24, 24, 24))
    for i, (R, p) in enumerate(items):
        try:
            im = Image.open(ROOT / p if not Path(p).is_absolute() else p).convert("RGB")
            im.thumbnail((cell - 8, cell - 8))
            sheet.paste(im, ((i % cols) * cell + 4, (i // cols) * (cell + 4) + 4))
        except Exception:  # noqa: BLE001
            continue
    sheet.save(out, quality=85)
    return rel(out)


# ================================================================ серия


def audit_series(paths: list[Path], th: Th, a, out_dir: Path, dna: dict | None) -> dict:
    sm = mod("series_metrics")
    cells = list(paths)
    grid_note = None
    if getattr(a, "grid", None) and len(paths) == 1:
        r_, c_ = (int(x) for x in a.grid.lower().split("x"))
        sg = mod("split_grid")
        res, gx, gy = sg.split(str(paths[0]), str(out_dir / (paths[0].stem + "_cells")), r_, c_)
        cells = [Path(f) for f, _ in res]
        grid_note = {"grid": a.grid, "cells": [rel(c) for c in cells]}
    refs = [str(Path(x)) for x in (getattr(a, "ref", None) or [])]
    s = sm.series([str(p) for p in cells], refs or None)
    acc = (dna or {}).get("acceptance") or {}
    lim_h = acc.get("series_hue_spread_max_deg", th("series.hue_spread_max_deg", 10))
    lim_p = acc.get("series_pal_dE_mean_max", th("series.pal_de_mean_max", 0.045))
    brk_p = acc.get("series_pal_dE_break", th("series.pal_de_break", 0.06))
    lim_l = acc.get("series_sd_L_max", th("series.sd_L_max", 0.04))
    lim_ph = acc.get("phash_min", th("series.phash_dup_max", 10))
    defects = []

    def d(code, level, msg, metric, value, thr):
        defects.append({"code": code, "level": level, "msg": msg, "metric": metric, "value": value, "threshold": thr})
    if s["hue_spread_deg"] > th("series.hue_break_deg", 25):
        d("QA-SERIES-BREAK", "fail", f"серия распалась по оттенку: {s['hue_spread_deg']}° > 25°", "hue_spread_deg", s["hue_spread_deg"], 25)
    elif s["hue_spread_deg"] > lim_h:
        d("QA-SERIES-HUE", "warn", f"разброс оттенка {s['hue_spread_deg']}° > {lim_h}°", "hue_spread_deg", s["hue_spread_deg"], lim_h)
    if s["pal_dE_mean"] > brk_p:
        d("QA-SERIES-BREAK", "fail", f"ΔE палитр {s['pal_dE_mean']} > {brk_p}", "pal_dE_mean", s["pal_dE_mean"], brk_p)
    elif s["pal_dE_mean"] > lim_p:
        d("QA-SERIES-PALETTE", "warn", f"ΔE палитр {s['pal_dE_mean']} > {lim_p}", "pal_dE_mean", s["pal_dE_mean"], lim_p)
    if s["sd_L"] > lim_l:
        d("QA-SERIES-LIGHTNESS", "warn", f"разброс светлоты {s['sd_L']} > {lim_l}", "sd_L", s["sd_L"], lim_l)
    if s["phash_min"] < lim_ph:
        d("QA-SERIES-DUP", "warn", f"два кадра почти одинаковы (pHash {s['phash_min']} < {lim_ph}) — дубль сюжета", "phash_min",
          s["phash_min"], lim_ph)
    lvl = max([Report.LEVELS[x["level"]] for x in defects] + [0])
    return {"schema": SCHEMA, "kind": "series", "files": [rel(p) for p in cells], "grid": grid_note, "metrics": s,
            "verdict": {0: "pass", 1: "warn", 2: "needs_human", 3: "fail"}[lvl], "defects": defects,
            "human": ["Серия рядом в одном размере, размыть: одинаковы ли пятна по весу; стиль, свет и линия одни? (цвет метрики "
                      "видят, стиль — нет: CSD ρ 0,565 с людьми, F-src-series)"],
            "thresholds_note": "F/06: одна съёмка 5,7° / 0,038; четыре локации 104° / 0,091; пороги — фото, для иллюстраций пересчитать"}


# ================================================================ главный проход


def load_json_opt(p):
    if not p:
        return None, None
    pth = Path(p)
    return json.loads(pth.read_text(encoding="utf-8")), pth


def collect_inputs(paths: list[str]) -> list[tuple[Path, dict | None, Path | None]]:
    """Файлы и папки → (файл, паспорт, путь паспорта). Папка: все *.passport.json (их files[]) + медиа без паспорта."""
    out, seen = [], set()
    for p in paths:
        P = Path(p)
        if P.is_dir():
            for pp in sorted(P.rglob("*.passport.json")):
                try:
                    j = json.loads(pp.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                for f in j.get("files") or []:
                    fp = f.get("path") if isinstance(f, dict) else f
                    if not fp:
                        continue
                    cand = [ROOT / fp, pp.parent / Path(fp).name]
                    fpath = next((c for c in cand if c.exists()), None)
                    if fpath and fpath.suffix.lower() in IMG_EXT + VID_EXT + SVG_EXT and fpath.resolve() not in seen:
                        seen.add(fpath.resolve())
                        out.append((fpath, j, pp))
            for f in sorted(P.rglob("*")):
                if f.is_file() and f.suffix.lower() in IMG_EXT + VID_EXT + SVG_EXT and f.resolve() not in seen \
                        and not re.search(r"_(panel|sheet|check)|diff_heat|composite", f.name):
                    seen.add(f.resolve())
                    pj, ppath = find_passport(f)
                    out.append((f, pj, ppath))
        elif P.exists():
            if P.resolve() in seen:
                continue
            seen.add(P.resolve())
            pj, ppath = find_passport(P)
            out.append((P, pj, ppath))
    return out


def audit_paths(a) -> dict:
    th_doc = load_thresholds(Path(a.thresholds) if getattr(a, "thresholds", None) else None)
    dna, dna_path = load_json_opt(getattr(a, "dna", None))
    spec, _ = load_json_opt(getattr(a, "spec", None))
    over = {}
    if dna:
        acc = dna.get("acceptance") or {}
        mapping = {"colorfulness_max_rel": "image.colorfulness_max_rel", "hdr_index_max_delta": "image.hdr_index_max_delta",
                   "zone_edge_max": "text_zone.edge_density_max", "text_contrast_min": "text_zone.contrast_min",
                   "text_zone_percentile": "text_zone.scrim_percentile", "centroid_x_min": "composition.centroid_x_min",
                   "markers_max": "slop.key_slot_markers"}
        for k, v in acc.items():
            if k in mapping:
                over[mapping[k]] = v + 1 if k == "markers_max" else v
    th = Th(th_doc, over)
    out_dir = Path(a.out or (kbpaths.out("ai-media", "audit") / dt.date.today().isoformat()))
    out_dir.mkdir(parents=True, exist_ok=True)
    items = collect_inputs(a.paths)
    ref_metrics = dna_reference_metrics(dna, dna_path)
    reports: list[Report] = []
    need_ocr: list[Report] = []
    for path, pj, ppath in items:
        facts = passport_facts(pj, ppath, path) if pj else None
        mode = a.mode if a.mode != "auto" else infer_mode(path, facts, a)
        R = Report(path, mode, th)
        slot = getattr(a, "slot", None) or SLOT_OF_TASK.get((facts or {}).get("task_code") or getattr(a, "task", None) or "")
        if mode == "og":
            slot = "og"
        R.meta.update({"slot": slot, "stage": getattr(a, "stage", "master")})
        if facts:
            R.meta["generation"] = {k: facts.get(k) for k in ("passport", "passport_schema", "channel", "model", "provider_actual",
                                                              "tag", "test", "task_code", "cost_rub", "requested")}
        ctx = {"slot": slot, "dna": dna, "spec": spec, "out": str(out_dir), "ref_metrics": ref_metrics}
        try:
            MODES[mode](R, path, facts, a, ctx)
        except Exception as e:  # noqa: BLE001
            import traceback
            R.errors.append(f"{type(e).__name__}: {e}"[:300])
            if getattr(a, "debug", False):
                traceback.print_exc()
        exp = list(getattr(a, "expect", None) or [])
        if not exp and facts and (facts.get("meta") or {}).get("expect"):
            exp = list(facts["meta"]["expect"])
        if not exp and spec:
            exp = [t for t in ((spec.get("text") or {}).get("lines") or [])] if isinstance(spec.get("text"), dict) else []
        R.meta["_expect"] = exp
        ocr_mode = getattr(a, "ocr", "auto")
        if path.suffix.lower() in IMG_EXT and mode in ("image", "og", "cutout", "edit") and ocr_mode != "off" and \
                (exp or ocr_mode == "on" or mode in ("image", "og")):
            need_ocr.append(R)
        reports.append(R)
    if need_ocr and getattr(a, "ocr", "auto") != "off":
        lang = getattr(a, "lang", None) or "ru"
        res = run_ocr([R.path for R in need_ocr], lang=lang)
        apply_text(need_ocr, {str(Path(o["file"]).resolve()): o for o in res}, a)
    results = []
    for R in reports:
        if getattr(a, "provenance", True) and R.path.suffix.lower() in IMG_EXT + VID_EXT:
            try:
                P = provenance(R.path, out_dir)
                R.checks["provenance"] = P
                if P.get("visible_suspect"):   # эвристика L: ≈ половина надписей в углах, ≈ 1 ложное из 10 фото → только человек
                    R.defect("QA-PROV-VISIBLE-MARK", "needs_human",
                             f"подозрение на видимую метку в углу ({', '.join(P['visible_suspect'][:4])}) — смотреть "
                             f"{P.get('corners_sheet') or 'лист углов'}; метку вендора не вырезать кропом без решения заказчика "
                             "(12-legal-provenance/04 §5 п. 7)", evidence=P.get("corners_sheet"))
                marks = (P.get("summary") or {}).get("marks")
                if R.meta.get("stage") == "web" and R.meta.get("generation") and marks is not None and not marks:
                    # ворота L 04 §5 п. 8: у производной ИИ-ассета для страницы — машиночитаемая метка (C2PA теряется при любом кодировании)
                    R.defect("QA-PROV-NO-MARK", "warn", "в файле для страницы нет машиночитаемой метки ИИ (C2PA / XMP DigitalSourceType / "
                             "AIGC) — `provenance_check.py stamp IN OUT --dst trained|composite` (12-legal-provenance/02 §5, 04 §5 п. 8)")
            except Exception as e:  # noqa: BLE001
                R.checks["provenance"] = {"error": str(e)[:200]}
        finish(R, R.meta.get("slot"))
        R.meta["panel"] = contact_panel(R, out_dir)
        R.meta.pop("_expect", None)
        results.append(R.to_dict())
    series = None
    if getattr(a, "series", False) or a.mode == "series":
        imgs = [R.path for R in reports if R.path.suffix.lower() in IMG_EXT]
        if imgs:
            series = audit_series(imgs, th, a, out_dir, dna)
    summary = {"schema": SCHEMA, "tool": f"asset_audit.py {VERSION}", "checked_at": now_iso(), "out": rel(out_dir),
               "thresholds": {"file": th_doc.get("_path"), "sha": th_doc.get("_sha")}, "n": len(results),
               "verdicts": {v: sum(1 for r in results if r["verdict"] == v) for v in ("pass", "warn", "needs_human", "fail")},
               "assets": results, "series": series, "index_sheet": index_sheet(reports, out_dir / "index_sheet.jpg")}
    (out_dir / "audit.json").write_text(jdump(summary), encoding="utf-8")
    (out_dir / "audit.md").write_text(audit_md(summary), encoding="utf-8")
    return summary


def audit_md(s: dict) -> str:
    L = [f"# Приёмка ассетов — {s['checked_at']}", "", f"Пороги: `{s['thresholds']['file']}` ({s['thresholds']['sha']}); итог: "
         + ", ".join(f"{k} {v}" for k, v in s["verdicts"].items()), "",
         "| Файл | Режим | Вердикт | Дефекты (не info) | Человеку |", "|---|---|---|---|---|"]
    for r in s["assets"]:
        codes = ", ".join(sorted({d["code"] for d in r["defects"] if d["level"] != "info"})) or "—"
        L.append(f"| `{Path(r['file']).name}` | {r['mode']} | **{r['verdict']}** | {codes} | {len(r['human'])} |")
    if s.get("series"):
        ss = s["series"]
        L += ["", f"Серия ({len(ss['files'])} кадров): **{ss['verdict']}** — оттенок {ss['metrics']['hue_spread_deg']}°, ΔE палитр "
              f"{ss['metrics']['pal_dE_mean']}, pHash min {ss['metrics']['phash_min']}"]
    L += ["", "Коды и пороги — `11-evaluation-qa/01-metrics-and-asset-audit.md`; ручная приёмка — `03-checklists-by-asset.md`."]
    return "\n".join(L) + "\n"


# ================================================================ пороги: печать и проверка

TH_KEYS_USED = [
    "image.ratio_tolerance", "image.hero_master_min_px", "image.colorfulness_q3", "image.sat_share_q3", "image.hdr_index_q3",
    "image.clip_hi_q3", "image.colorfulness_max_rel", "image.hdr_index_max_delta", "image.filter_colorfulness_rel",
    "image.warm_b_max", "image.purple_share_max", "composition.center_offset_min", "composition.centroid_x_min",
    "composition.blobs_max", "text_zone.edge_density_max", "text_zone.scrim_percentile", "text_zone.contrast_min",
    "text_zone.scrim_alpha_warn", "palette.de_ok", "palette.min_matched", "cutout.transparent_frac_min", "cutout.halo_px_max",
    "cutout.margin_min_frac", "cutout.glass_partial_min", "cutout.fiber_partial_min", "cutout.iou_min_solid",
    "cutout.iou_min_fibers", "cutout.band_mae_x1000_max", "edit.leak_frac_max", "edit.leak_de", "edit.global_drift_max",
    "edit.target_changed_min", "edit.edges_iou_min", "edit.protect_ssim_min", "edit.outpaint_edge_sharpness_min",
    "edit.noedit_changed_min", "edit.maskless_changed_max", "edit.extra_regions_tolerance", "edit.derived_mask_dilate_frac",
    "edit.feather_frac", "edit.local_shift_de", "edit.local_shift_min_frac", "texture.seam_ratio_max", "texture.seam_ratio_fail", "video.seam_local_max", "video.cut_ratio_max",
    "video.event_ratio_warn", "video.head_tail_min", "video.static_frac_max", "video.motion_vs_control_min",
    "video.cam_shift_max_px", "video.color_de_max", "video.flicker_max", "video.cinemagraph_drift_max", "video.quiet_motion_med",
    "video.mezzanine_kbps_min", "video.loop_len_min_s", "video.loop_len_max_s", "video.motion_keep_min", "video_alpha.bg_ok_min", "video_alpha.key_de",
    "video_alpha.obj_drift_max_pct_w", "series.hue_spread_max_deg", "series.hue_break_deg", "series.pal_de_mean_max",
    "series.pal_de_break", "series.sd_L_max", "series.phash_dup_max", "text.fail_min_ocr_score", "text.fail_min_line_h_px",
    "text.unrequested_min_chars", "text.unrequested_min_score", "slop.cluster_markers", "slop.key_slot_markers",
    "svg.icon_kb_max", "svg.illustration_kb_max", "svg.check_icons_flags", "og.size", "og.formats", "og.kb_max",
    "encoding.ssimulacra2_hero_min", "encoding.ssimulacra2_min", "budget.image.hero_kb", "budget.image.section_kb",
    "budget.image.og_kb", "budget.image.texture_kb", "budget.image.product_kb", "budget.video.hero_1080_kb", "budget.video.hero_720_kb",
    "judge.trust_agreement_min", "judge.prefilter_agreement_min", "judge.min_pairs", "judge.swap_consistency_min",
    "judge.position_bias_max"]


def cmd_thresholds(a):
    doc = load_thresholds(Path(a.thresholds) if a.thresholds else None)
    th = Th(doc)
    rows, missing, nosrc = [], [], []
    for k in TH_KEYS_USED:
        if k not in th.flat:
            missing.append(k)
            continue
        s = th.src(k)
        if not s:
            nosrc.append(k)
        rows.append((k, th.flat[k], s))
    if a.check:
        ok = not missing and not nosrc
        print(jdump({"ok": ok, "keys_used": len(TH_KEYS_USED), "in_yaml": len(th.flat), "missing": missing, "no_source": nosrc,
                     "file": doc.get("_path"), "sha": doc.get("_sha")}))
        return 0 if ok else 1
    for k, v, s in rows:
        print(f"{k:42s} {str(v):>14s}  ← {s}")
    return 0


# ================================================================ VLM-критик: задания, разбор ответов, согласие с голосами

JUDGE_MODEL = "google/gemini-3.1-flash-lite"      # polza 2026-09-23_1745: 14,78 / 88,69 ₽ за 1 млн токенов вход/выход
JUDGE_SCHEMA = RUBRICS / "judge-response.schema.json"


def load_rubric(name: str) -> dict:
    p = RUBRICS / f"{name}.rubric.json"
    if not p.exists():
        raise SystemExit(f"нет рубрики {rel(p)}")
    return json.loads(p.read_text(encoding="utf-8"))


def image_key(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16] if Path(path).exists() else hashlib.sha256(str(path).encode()).hexdigest()[:16]


def model_params(model: str) -> set | None:
    """supported_parameters модели в последнем снимке каталога polza (99-raw/cache/polza/<дата[_ЧЧММ]>/api-v1-models.json)."""
    snaps = sorted(kbpaths.cache("ai-media", "polza").glob("20*/api-v1-models.json"))
    if not snaps:
        return None
    d = json.loads(snaps[-1].read_text(encoding="utf-8"))
    for m in (d.get("data") if isinstance(d, dict) else d) or []:
        if m.get("id") == model:
            return set(((m.get("top_provider") or {}).get("supported_parameters")) or [])
    return None


def judge_body(rubric: dict, mode: str, questions: list[dict], images: list[str], model: str, brief: str | None) -> dict:
    j = rubric["judge"]
    sys_prompt = j["system"]
    if mode == "checklist":
        text = j["checklist_intro"] + "\n" + "\n".join(f'{q["id"]}: {q["q"]}' for q in questions)
    elif mode == "defects":
        text = j["defects_intro"] + "\n" + "\n".join(f'{q["code"]}: {q["q"]}' for q in questions)
    elif mode == "transcribe":
        text = j.get("transcribe_intro") or ("Transcribe all text visible in the image exactly as written, letter by letter, preserving "
                                             "case, punctuation and line breaks. Do not correct spelling and do not translate. "
                                             "If there is no text, return an empty list.")
    else:
        text = j["pairwise_intro"].replace("{brief}", brief or "—") + "\n" + "\n".join(f'{q["id"]}: {q["q"]}' for q in questions)
    content = [{"type": "text", "text": text}]
    for lab, im in zip(("A", "B") if mode == "pairwise" else ("",), images):
        if lab:
            content.append({"type": "text", "text": f"Image {lab}:"})
        content.append({"type": "image_url", "image_url": {"url": im}})
    schema = json.loads(JUDGE_SCHEMA.read_text(encoding="utf-8")) if JUDGE_SCHEMA.exists() else None
    body = {"model": model, "temperature": 0, "seed": 7, "max_tokens": j.get("max_tokens", 700),
            "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": content}]}
    sup = model_params(model)
    if schema and j.get("structured", True) and (sup is None or "response_format" in sup):
        sub = schema["$defs"][{"checklist": "checklist_answer", "defects": "defects_answer", "pairwise": "pairwise_answer",
                               "transcribe": "transcribe_answer"}[mode]]
        body["response_format"] = {"type": "json_schema", "json_schema": {"name": f"judge_{mode}", "strict": True, "schema": sub}}
    elif schema:   # модель без structured output (qwen3.5-9b: только max_tokens) — формат словами + образец
        example = {"checklist": '{"answers": [{"id": "q1", "answer": "yes"}]}',
                   "defects": '{"defects": [{"code": "IMG-M03", "present": "no", "where": "", "severity": "none"}]}',
                   "pairwise": '{"answers": [{"id": "slot", "winner": "A"}], "defect_codes": []}',
                   "transcribe": '{"lines": ["first line of text", "second line"]}'}[mode]
        content[0]["text"] += f"\nReply with JSON only, exactly in this shape: {example}"
    if j.get("reasoning_effort") and (sup is None or "reasoning" in sup):
        body["reasoning"] = {"effort": j["reasoning_effort"]}
    if sup is not None:   # убрать то, чего модель не принимает (каталог polza)
        for k in ("temperature", "seed"):
            if k not in sup:
                body.pop(k, None)
    return body


def cmd_judge_jobs(a):
    """Задания VLM-судьи (.polza-chat.json, исполняет mp_client.py в фазе 5). Вход — пары или картинки (JSONL):
    checklist/defects: {"image": путь, "brief": id|текст, "questions": [...]?}; pairwise: {"a": путь, "b": путь, "brief": …,
    "pair": id}. Слепо: имя модели и плечо в задание не попадают; ключ → *.keys.json рядом."""
    import random
    rubric = load_rubric(a.rubric)
    if getattr(a, "from_stand_page", None):
        rows = stand_page_items(Path(a.from_stand_page))
    else:
        rows = [json.loads(x) for x in Path(a.items).read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    qfile = json.loads(Path(a.questions).read_text(encoding="utf-8")) if a.questions else {}
    jobs_dir = Path(a.out).resolve().parent
    rnd_ = random.Random(20260923)
    tasks, keys = [], {}
    price = a.price_rub
    base_q = rubric.get("vlm", {}).get("pairwise_questions" if a.mode == "pairwise" else "defect_questions" if a.mode == "defects"
                                          else "checklist_generic", [])

    def relp(p):
        P = Path(p)
        P = P if P.is_absolute() else (ROOT / P)
        return os.path.relpath(P, jobs_dir)
    work = list(rows)
    enc_dir = Path(a.same_encoding) if getattr(a, "same_encoding", None) else None
    enc_cache: dict = {}

    def shown(p):
        """Одинаковое кодирование сторон (как на странице голосования stand_run: JPEG q90 ≤ 1600 px, PNG при альфе) —
        судья и люди выбирают по артефактам сжатия [V:b_PmGocP4rc 11:17]; K-04 меряет это смещение и идёт без флага."""
        if enc_dir is None:
            return p
        if p not in enc_cache:
            from PIL import Image
            P = Path(p) if Path(p).is_absolute() else ROOT / p
            data, ext = mod("stand_run")._encode(Image.open(P).convert("RGBA"))
            enc_dir.mkdir(parents=True, exist_ok=True)
            q = enc_dir / f"{hashlib.sha256(data).hexdigest()[:16]}.{ext}"
            q.write_bytes(data)
            enc_cache[p] = str(q)
        return enc_cache[p]
    if a.mode == "pairwise":
        extra = rnd_.sample(work, max(1, round(len(work) * a.repeat))) if work and a.repeat > 0 else []
        first_swap: dict = {}
        for run, group in ((1, work), (2, extra)):
            for r in group:
                rid = id(r)
                # повтор — всегда с переставленными сторонами относительно первого показа (позиционный сдвиг, Arena Bench)
                swap = first_swap.setdefault(rid, rnd_.random() < 0.5) if run == 1 else not first_swap.get(rid, False)
                oa, ob = str(r.get("orig_a") or r["a"]), str(r.get("orig_b") or r["b"])   # исходники сторон (для сверки с голосами)
                sa, sb = shown(r["a"]), shown(r["b"])                                       # что увидит судья
                A, B, A_orig, B_orig = (sb, sa, ob, oa) if swap else (sa, sb, oa, ob)
                pid = r.get("pair") or hashlib.sha256((oa + ob).encode()).hexdigest()[:12]
                qs = r.get("questions") or base_q
                body = judge_body(rubric, "pairwise", qs, [relp(A), relp(B)], a.model, r.get("brief_text") or r.get("brief"))
                tag = f"K-judge-{a.rubric}-pw-{pid}-r{run}"
                keys[tag] = {"pair": pid, "A": str(A), "B": str(B), "A_orig": A_orig, "B_orig": B_orig, "swapped": swap, "run": run,
                             "orig_a": oa, "orig_b": ob,
                             "meta": {k: v for k, v in r.items() if k not in ("a", "b", "orig_a", "orig_b")}}
                tasks.append(chat_job(body, tag, a, price, {"test": a.test, "mode": "pairwise", "rubric": a.rubric, "pair": pid, "run": run}))
    else:
        extra = rnd_.sample(work, max(1, round(len(work) * a.repeat))) if work and a.repeat > 0 else []
        for run, group in ((1, work), (2, extra)):
            for r in group:
                img = r["image"]
                key = image_key(ROOT / img if not Path(img).is_absolute() else Path(img))
                if a.mode == "checklist":
                    qs = r.get("questions") or qfile.get(r.get("brief") or "", []) or base_q
                    qs = [q for q in qs if "q" in q]
                elif a.mode == "transcribe":
                    qs = []
                else:
                    qs = r.get("questions") or base_q
                body = judge_body(rubric, a.mode, qs, [relp(img)], a.model, None)
                tag = f"K-judge-{a.rubric}-{a.mode[:2]}-{key}-r{run}"
                keys[tag] = {"key": key, "image": str(img), "run": run, "meta": {k: v for k, v in r.items() if k != "image"}}
                tasks.append(chat_job(body, tag, a, price, {"test": a.test, "mode": a.mode, "rubric": a.rubric, "key": key, "run": run,
                                                            "n_questions": len(qs)}))
    Path(a.out).write_text(jdump(tasks) + "\n", encoding="utf-8")
    kp = Path(a.out).with_name(Path(a.out).name.replace(".polza-chat.json", "") + ".keys.json")
    kp.write_text(jdump(keys) + "\n", encoding="utf-8")
    print(jdump({"jobs": len(tasks), "file": rel(a.out), "keys": rel(kp), "price_rub_expected": round(price * len(tasks), 2)}))
    return 0


def stand_page_items(page_dir: Path) -> list[dict]:
    """Пары страницы слепого голосования stand_run.py (DIR/index.html + DIR.key.json) → пары для судьи с теми же id и теми же
    файлами, что видел заказчик (DIR/img/*: одинаковое кодирование JPEG q90 ≤ 1600 px); исходники — orig_a/orig_b для сверки
    с голосами. Без контрольных, повторов и «одинаковых»; серия (несколько файлов на сторону) — судье только первый."""
    page_dir = Path(page_dir).resolve()
    html_ = (page_dir / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="data">(.*?)</script>', html_, re.S)
    data = json.loads(m.group(1).replace("<\\/", "</")) if m else {"pairs": []}
    K = json.loads(Path(str(page_dir) + ".key.json").read_text(encoding="utf-8"))
    out = []
    for p in data.get("pairs", []):
        kp = K["pairs"].get(p["id"])
        if not kp or kp.get("gold") or kp.get("identical") or kp.get("repeat_of"):
            continue
        out.append({"pair": p["id"], "a": str(page_dir / p["A"][0]), "b": str(page_dir / p["B"][0]),
                    "orig_a": str(kp["A"]["files"][0]), "orig_b": str(kp["B"]["files"][0]), "brief_text": p.get("brief") or "",
                    "test": kp.get("test"), "group": kp.get("group")})
    return out


def chat_job(body, tag, a, price, meta):
    return {"channel": "polza-chat", "method": "POST", "path": "/api/v1/chat/completions", "body": body, "tag": tag, "agent": "K",
            "variant": meta.get("run", 1), "max_rub": a.max_rub, "price_rub": price,
            "price_source": "каталог polza 2026-09-23_1745: google/gemini-3.1-flash-lite 14,78225 / 88,6935 ₽ за 1 млн токенов "
                            "вход/выход; оценка — mp_client.py estimate",
            "docs": "99-raw/cache/polza/2026-09-23/docs-repo/gaidy/structured-output.mdx; gaidy/media-input.mdx",
            "notes": "VLM-судья вслепую (рубрика 11-evaluation-qa/rubrics): имя модели и плечо скрыты, ключ — *.keys.json",
            "meta": {**meta, "judge": "vlm"}}


def extract_json_text(t: str):
    t = t.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, re.S)
    if m:
        t = m.group(1)
    s, e = t.find("{"), t.rfind("}")
    if s < 0 or e < s:
        raise ValueError("нет JSON")
    return json.loads(t[s:e + 1])


def normalize_answer(ans: dict, mode: str) -> tuple[dict, list[str]]:
    """Ответ судьи → нормализованный вид; дефект «есть» без «где» понижается до unsure (защита от галлюцинаций)."""
    probs = []
    if mode == "checklist":
        out = {}
        for q in ans.get("answers", []):
            v = str(q.get("answer", "")).lower()
            out[q.get("id")] = v if v in ("yes", "no", "unsure") else "unsure"
        return {"answers": out}, probs
    if mode == "defects":
        out = []
        for d in ans.get("defects", []):
            present = d.get("present")
            present = {True: "yes", False: "no"}.get(present, str(present).lower() if present is not None else "unsure")
            present = present if present in ("yes", "no", "unsure") else "unsure"
            where = (d.get("where") or "").strip()
            if present == "yes" and len(where) < 3:
                present = "unsure"
                probs.append(f"{d.get('code')}: «есть» без «где» → unsure")
            out.append({"code": d.get("code"), "present": present, "where": where, "severity": d.get("severity")})
        return {"defects": out}, probs
    if mode == "transcribe":
        return {"lines": [str(x) for x in ans.get("lines", [])]}, probs
    out = {}
    for q in ans.get("answers", []):
        v = str(q.get("winner", "")).upper()
        out[q.get("id")] = v if v in ("A", "B", "TIE", "BOTH_BAD") else "TIE"
    return {"answers": out, "codes": ans.get("defect_codes", [])}, probs


def cmd_judge_parse(a):
    """Ответы mp_client.py (паспорта mp-passport/1 + файлы ответа .json/.md) → answers.jsonl (разметка по ключу)."""
    keys = json.loads(Path(a.keys).read_text(encoding="utf-8"))
    rows, bad = [], 0
    schema_ok = JUDGE_SCHEMA.exists()
    for pp in sorted(Path(a.passports).rglob("*.passport.json")):
        j = json.loads(pp.read_text(encoding="utf-8"))
        tag = (j.get("job") or {}).get("tag")
        if tag not in keys:
            continue
        mode = ((j.get("job") or {}).get("meta") or {}).get("mode")
        f = (j.get("files") or [{}])[0]
        fp = ROOT / f.get("path", "")
        row = {"tag": tag, "mode": mode, **keys[tag], "usage": j.get("usage"), "cost_rub": (j.get("cost") or {}).get("usage_cost_rub")}
        try:
            raw = json.loads(fp.read_text(encoding="utf-8")) if fp.suffix == ".json" else extract_json_text(fp.read_text(encoding="utf-8"))
            if schema_ok:
                sch = json.loads(JUDGE_SCHEMA.read_text(encoding="utf-8"))
                sub = sch["$defs"][{"checklist": "checklist_answer", "defects": "defects_answer", "pairwise": "pairwise_answer",
                                    "transcribe": "transcribe_answer"}[mode]]
                errs = mini_validate(raw, sub)
                row["schema_errors"] = errs[:5]
            norm, probs = normalize_answer(raw, mode)
            row.update(norm)
            row["problems"] = probs
            row["valid"] = not row.get("schema_errors")
        except Exception as e:  # noqa: BLE001
            row.update({"valid": False, "error": str(e)[:200]})
            bad += 1
        rows.append(row)
    Path(a.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(jdump({"answers": len(rows), "invalid": bad, "out": rel(a.out)}))
    return 0


def mini_validate(inst, sch, path="") -> list[str]:
    """Проверка подмножества JSON Schema (type, required, enum, properties, items, additionalProperties) — для ответа судьи."""
    errs = []
    t = sch.get("type")
    types = {"object": dict, "array": list, "string": str, "boolean": bool, "number": (int, float), "integer": int}
    if t:
        tl = t if isinstance(t, list) else [t]
        if not any(isinstance(inst, types[x]) and not (x in ("number", "integer") and isinstance(inst, bool)) for x in tl if x in types):
            return [f"{path or '/'}: тип {type(inst).__name__}, нужен {t}"]
    if "enum" in sch and inst not in sch["enum"]:
        errs.append(f"{path}: {inst!r} не из {sch['enum']}")
    if isinstance(inst, dict):
        for k in sch.get("required", []):
            if k not in inst:
                errs.append(f"{path}/{k}: нет обязательного поля")
        props = sch.get("properties", {})
        for k, v in inst.items():
            if k in props:
                errs += mini_validate(v, props[k], f"{path}/{k}")
            elif sch.get("additionalProperties") is False:
                errs.append(f"{path}/{k}: лишнее поле")
    if isinstance(inst, list) and "items" in sch:
        for i, v in enumerate(inst):
            errs += mini_validate(v, sch["items"], f"{path}[{i}]")
    return errs


def wilson(k, n):
    return mod("stand_run").wilson(k, n)


def cohen_kappa(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    labels = sorted({x for p in pairs for x in p})
    n = len(pairs)
    po = sum(1 for x, y in pairs if x == y) / n
    pe = sum((sum(1 for x, _ in pairs if x == L) / n) * (sum(1 for _, y in pairs if y == L) / n) for L in labels)
    return round((po - pe) / (1 - pe), 4) if pe < 1 else None


def trust_level(agree: float | None, lo: float | None, n: int, th: Th) -> str:
    if agree is None or n < th("judge.min_pairs", 20):
        return "мало данных"
    if agree >= th("judge.trust_agreement_min", 0.8) and (lo or 0) >= 0.65:
        return "доверять (фильтр и сортировка best-of-N)"
    if agree >= th("judge.prefilter_agreement_min", 0.7):
        return "только предфильтр грубого брака, решение — человек"
    return "не использовать"


def cmd_agree(a):
    """Согласие VLM-судьи с заказчиком. Попарно: голоса страницы stand_run.py (--votes, --key) против ответов судьи
    (--answers pairwise). Бинарно: ответы заказчика на те же вопросы (--labels) против ответов судьи (checklist)."""
    th = Th(load_thresholds(Path(a.thresholds) if a.thresholds else None))
    ans = [json.loads(x) for x in Path(a.answers).read_text(encoding="utf-8").splitlines() if x.strip()]
    rep: dict = {"answers": rel(a.answers)}
    if a.votes and a.key:
        K = json.loads(Path(a.key).read_text(encoding="utf-8"))
        human, human_pid = {}, {}
        for vf in a.votes:
            V = json.loads(Path(vf).read_text(encoding="utf-8"))
            for pid, v in (V.get("votes") or {}).items():
                kp = K["pairs"].get(pid)
                if not kp or kp.get("gold") or kp.get("identical") or kp.get("repeat_of"):
                    continue
                pa, pb = str(kp["A"]["files"][0]), str(kp["B"]["files"][0])
                for q, o in v.items():
                    if o in ("A", "B"):
                        w = pa if o == "A" else pb
                        human[(frozenset((pa, pb)), q)] = w
                        human_pid[(pid, q)] = w
        per_q, pos, swaps = {}, [], {}
        for r in ans:
            if r.get("mode") != "pairwise" or not r.get("answers"):
                continue
            for q, w in r["answers"].items():
                if w in ("A", "B"):
                    pos.append(w == "A")
                    # исходник выбранной стороны (судья мог видеть перекодированную копию страницы или --same-encoding)
                    winner = (r.get("A_orig") or r["A"]) if w == "A" else (r.get("B_orig") or r["B"])
                    swaps.setdefault((r["pair"], q), []).append(winner)
                    h = human_pid.get((r.get("pair"), q)) or human.get((frozenset((str(r["orig_a"]), str(r["orig_b"]))), q))
                    if h is not None and r.get("run") == 1:
                        per_q.setdefault(q, []).append((winner == h))
        rep["pairwise"] = {}
        for q, v in per_q.items():
            k, n = sum(v), len(v)
            p, lo, hi = wilson(k, n)
            rep["pairwise"][q] = {"agree": round(p, 3), "wilson95": [round(lo, 3), round(hi, 3)], "n": n,
                                  "decision": trust_level(p, lo, n, th)}
        cons = [len(set(w)) == 1 for w in swaps.values() if len(w) >= 2]
        rep["swap_consistency"] = {"same": sum(cons), "n": len(cons), "share": round(sum(cons) / len(cons), 3) if cons else None}
        rep["position_A_share"] = round(sum(pos) / len(pos), 3) if pos else None
        if rep["position_A_share"] is not None and abs(rep["position_A_share"] - 0.5) > th("judge.position_bias_max", 0.15):
            rep["warning"] = "судья предпочитает одну сторону — ответы на перестановках обязательны"
    if a.labels:
        lab = {json.loads(x)["key"]: json.loads(x) for x in Path(a.labels).read_text(encoding="utf-8").splitlines() if x.strip()}
        pairs, by_type = [], {}
        yes_j, yes_h = 0, 0
        for r in ans:
            if r.get("mode") != "checklist" or r.get("run") != 1 or r.get("key") not in lab:
                continue
            hl = lab[r["key"]]["answers"]
            types = lab[r["key"]].get("types", {})
            for q, v in r.get("answers", {}).items():
                if q in hl and v in ("yes", "no") and hl[q] in ("yes", "no"):
                    pairs.append((v, hl[q]))
                    by_type.setdefault(types.get(q, "?"), []).append(v == hl[q])
                    yes_j += v == "yes"
                    yes_h += hl[q] == "yes"
        k = sum(1 for x, y in pairs if x == y)
        p, lo, hi = wilson(k, len(pairs)) if pairs else (None, None, None)
        rep["checklist"] = {"agree": round(p, 3) if p is not None else None, "wilson95": [round(lo, 3), round(hi, 3)] if pairs else None,
                            "n": len(pairs), "kappa": cohen_kappa(pairs),
                            "yes_rate_judge": round(yes_j / len(pairs), 3) if pairs else None,
                            "yes_rate_human": round(yes_h / len(pairs), 3) if pairs else None,
                            "by_type": {t: {"agree": round(sum(v) / len(v), 3), "n": len(v)} for t, v in by_type.items()},
                            "decision": trust_level(p, lo, len(pairs), th)}
    Path(a.out).write_text(jdump(rep), encoding="utf-8") if a.out else None
    print(jdump(rep))
    return 0


def cmd_calibrate(a):
    """Порог метрики по меткам человека (ok/bad): лучший порог по Юдену, AUC (Манн–Уитни), n. Пример: калибровка
    text_zone.edge_density и palette на первых 10 картинках фазы 5 (E)."""
    audit = json.loads(Path(a.audit).read_text(encoding="utf-8"))
    lab = {json.loads(x)["file"]: json.loads(x)["label"] for x in Path(a.labels).read_text(encoding="utf-8").splitlines() if x.strip()}
    vals = []
    for r in audit.get("assets", []):
        v = r
        for part in a.metric.split("."):
            v = v.get(part) if isinstance(v, dict) else None
        name = Path(r["file"]).name
        L = lab.get(r["file"]) or lab.get(name)
        if isinstance(v, (int, float)) and L in ("ok", "bad"):
            vals.append((float(v), L == "bad"))
    if len(vals) < 4:
        print(jdump({"n": len(vals), "error": "мало размеченных"}))
        return 1
    pos = [v for v, b in vals if b]
    neg = [v for v, b in vals if not b]
    auc = sum((x > y) + 0.5 * (x == y) for x in pos for y in neg) / max(1, len(pos) * len(neg))
    direction = "above" if auc >= 0.5 else "below"
    best = None
    for t in sorted({v for v, _ in vals}):
        pred = [(v > t) if direction == "above" else (v < t) for v, _ in vals]
        tp = sum(p and b for p, (_, b) in zip(pred, vals))
        fp = sum(p and not b for p, (_, b) in zip(pred, vals))
        tpr, fpr = tp / max(1, len(pos)), fp / max(1, len(neg))
        j = tpr - fpr
        if best is None or j > best[0]:
            best = (j, t, tpr, fpr)
    print(jdump({"metric": a.metric, "n": len(vals), "bad": len(pos), "auc": round(auc, 3), "direction": direction,
                 "threshold": best[1], "tpr": round(best[2], 3), "fpr": round(best[3], 3), "youden": round(best[0], 3),
                 "note": "n < 20 — ориентир, не порог; сверить с порогом thresholds.yaml" if len(vals) < 20 else ""}))
    return 0


# ================================================================ CLI


def cmd_ocr_worker(a):
    lim = a.det_limit.split(":")
    print(json.dumps(ocr_worker(a.paths, a.lang, a.text_score, not a.no_relines, (int(lim[0]), lim[1])), ensure_ascii=False))
    return 0


def cmd_ocr(a):
    paths = []
    for p in a.paths:
        P = Path(p)
        paths += sorted(x for x in P.rglob("*") if x.suffix.lower() in IMG_EXT) if P.is_dir() else [P]
    res = run_ocr(paths, a.lang, a.text_score)
    th = Th(load_thresholds())
    for r in res:
        if a.expect and "lines" in r:
            tr = "\n".join(L["text"] for L in r["lines"])
            r["text_check"] = text_verdict(a.expect, tr, lines_meta=r["lines"], th=th)
    if a.transcripts_out:   # формат stand_run.py metrics --transcripts: {путь от корня: транскрипт}
        tr = {rel(r["file"]): "\n".join(L["text"] for L in r.get("lines", [])) for r in res if "lines" in r}
        Path(a.transcripts_out).write_text(jdump(tr), encoding="utf-8")
    print(jdump(res))
    return 0 if all("error" not in r for r in res) else 2


def cmd_audit(a):
    s = audit_paths(a)
    if a.json:
        print(jdump(s))
    else:
        print(Path(ROOT / s["out"] / "audit.md").read_text(encoding="utf-8") if (ROOT / s["out"] / "audit.md").exists()
              else audit_md(s))
        print(f"JSON: {s['out']}/audit.json · лист: {s.get('index_sheet')}")
    worst = "fail" if s["verdicts"]["fail"] else ("needs_human" if s["verdicts"]["needs_human"] else "ok")
    if s.get("series") and s["series"]["verdict"] == "fail":
        worst = "fail"
    return 1 if (a.strict and worst == "fail") else 0


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    w = sp.add_parser("_ocr-worker")
    w.add_argument("paths", nargs="+")
    w.add_argument("--lang", default="ru", choices=sorted(OCR_SETS))
    w.add_argument("--text-score", type=float, default=0.3)
    w.add_argument("--det-limit", default=f"{OCR_DET_LIMIT[0]}:{OCR_DET_LIMIT[1]}")
    w.add_argument("--no-relines", action="store_true")
    o = sp.add_parser("ocr", help="OCR (venv-K под heavy.lock) + сверка со строками")
    o.add_argument("paths", nargs="+")
    o.add_argument("--lang", default="ru", choices=sorted(OCR_SETS))
    o.add_argument("--text-score", type=float, default=0.3)
    o.add_argument("--expect", action="append", default=[])
    o.add_argument("--transcripts-out", help="JSON {файл: транскрипт} для stand_run.py metrics --transcripts (E)")
    u = sp.add_parser("audit", help="приёмка файлов или папки с паспортами")
    u.add_argument("paths", nargs="+")
    u.add_argument("--mode", default="auto", choices=["auto", "series"] + sorted(MODES))
    u.add_argument("--out")
    u.add_argument("--thresholds")
    u.add_argument("--dna", help="паспорт визуала (06-art-direction-consistency): палитра, приёмка, эталоны, зона текста")
    u.add_argument("--spec", help="спецификация ассета (05-prompting/asset-spec.schema.json): зона текста, палитра, строки")
    u.add_argument("--task", help="код задачи (IMG-HERO-PHOTO …), если нет паспорта")
    u.add_argument("--slot", choices=["hero", "section", "product", "icon", "og", "texture"])
    u.add_argument("--stage", default="master", choices=["master", "web"], help="web — файл на страницу: бюджеты веса")
    u.add_argument("--ratio", help="заказанная пропорция 16:9, если нет паспорта")
    u.add_argument("--expect", action="append", help="строка, которая должна быть на картинке дословно (повторять)")
    u.add_argument("--allow-text", action="append", help="текст, который может быть на картинке (этикетка товара)")
    u.add_argument("--yo-optional", action="store_true", help="ё → е не считать ошибкой")
    u.add_argument("--ocr", default="auto", choices=["auto", "on", "off"])
    u.add_argument("--lang", default="ru", choices=sorted(OCR_SETS))
    u.add_argument("--text-zone", help="x0,y0,x1,y1 в долях кадра")
    u.add_argument("--text-color", help="#hex цвета текста поверх зоны")
    u.add_argument("--master", help="мастер для проверки производной: картинка — SSIMULACRA2, видео — motion_keep к мезонину (J)")
    u.add_argument("--orig", help="исходник правки или аутпейнта")
    u.add_argument("--mask")
    u.add_argument("--mask-mode", default="white", choices=["white", "black", "alpha"])
    u.add_argument("--protect", help="маска защищённого объекта (товар, логотип)")
    u.add_argument("--changes", type=int, help="сколько изменений заказано (безмасочная правка)")
    u.add_argument("--removal", action="store_true", help="удаление объекта: растушёвка ≈ 3 %% стороны (H 08/02 §2.4)")
    u.add_argument("--edit-kind", choices=["light", "color", "object", "other"])
    u.add_argument("--feather", type=int)
    u.add_argument("--bg", help="#hex фона под вырезом (ореол)")
    u.add_argument("--object", choices=["solid", "glass", "hair", "fur"])
    u.add_argument("--ref-alpha", help="эталонная альфа (рендер Blender)")
    u.add_argument("--control", help="i2v-контроль того же кадра (живость петли)")
    u.add_argument("--key", help="#hex ключа хромакея или auto")
    u.add_argument("--mezzanine", action="store_true", help="файл — мезонин или выход модели до перекодирования")
    u.add_argument("--camera-move", action="store_true", help="движение камеры заказано (не считать «ползущей»)")
    u.add_argument("--series", action="store_true", help="считать ещё и серию по всем картинкам")
    u.add_argument("--grid", help="RxC: разрезать сетку одной генерации и считать серию по ячейкам")
    u.add_argument("--ref", action="append", help="эталоны серии (ΔE палитры к эталону)")
    u.add_argument("--no-provenance", dest="provenance", action="store_false")
    u.add_argument("--strict", action="store_true", help="код выхода 1 при fail")
    u.add_argument("--json", action="store_true")
    u.add_argument("--debug", action="store_true")
    t = sp.add_parser("thresholds", help="пороги с источниками")
    t.add_argument("--check", action="store_true")
    t.add_argument("--thresholds")
    j = sp.add_parser("judge-jobs", help="задания VLM-судьи .polza-chat.json (платно только в фазе 5 через mp_client.py --live)")
    j.add_argument("--rubric", required=True)
    j.add_argument("--items", help="JSONL: {image,…} или {a,b,pair,brief,…}")
    j.add_argument("--from-stand-page", help="папка страницы голосования stand_run.py page (пары те же, что у заказчика)")
    j.add_argument("--mode", default="checklist", choices=["checklist", "defects", "pairwise", "transcribe"])
    j.add_argument("--questions", help="вопросы по id брифа (формат questions_v2.json D2)")
    j.add_argument("--model", default=JUDGE_MODEL)
    j.add_argument("--repeat", type=float, default=0.1)
    j.add_argument("--same-encoding", metavar="DIR",
                   help="pairwise: перекодировать обе стороны одинаково (как страница stand_run: JPEG q90 ≤ 1600 px) в DIR "
                        "(например 99-raw/phase5/inputs/K/<тест>); не для K-04 — он меряет смещение к сжатию")
    j.add_argument("--price-rub", type=float, default=0.05)
    j.add_argument("--max-rub", type=float, default=0.3)
    j.add_argument("--test", default="K")
    j.add_argument("--out", required=True)
    pj = sp.add_parser("judge-parse", help="ответы судьи (паспорта mp_client) → answers.jsonl")
    pj.add_argument("--passports", required=True)
    pj.add_argument("--keys", required=True)
    pj.add_argument("--out", required=True)
    g = sp.add_parser("agree", help="согласие судьи с заказчиком")
    g.add_argument("--answers", required=True)
    g.add_argument("--votes", action="append")
    g.add_argument("--key")
    g.add_argument("--labels")
    g.add_argument("--thresholds")
    g.add_argument("--out")
    c = sp.add_parser("calibrate", help="порог метрики по меткам человека")
    c.add_argument("--audit", required=True)
    c.add_argument("--labels", required=True)
    c.add_argument("--metric", required=True, help="путь в JSON ассета: checks.text_zone.edge_density")
    s = sp.add_parser("selftest")
    s.add_argument("--keep", action="store_true")
    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    fn = {"_ocr-worker": cmd_ocr_worker, "ocr": cmd_ocr, "audit": cmd_audit, "thresholds": cmd_thresholds,
          "judge-jobs": cmd_judge_jobs, "judge-parse": cmd_judge_parse, "agree": cmd_agree, "calibrate": cmd_calibrate,
          "selftest": cmd_selftest}[a.cmd]
    return fn(a)


def cmd_selftest(a):
    """Самопроверка без сети и без OCR-модели (OCR — tests/test_asset_audit.py, если есть venv-K)."""
    sys.path.insert(0, str(TOOLS / "tests"))
    import test_asset_audit as T
    return T.run(keep=getattr(a, "keep", False), ocr=False)


if __name__ == "__main__":
    sys.exit(main())
