#!/usr/bin/env python3
"""stand_run.py — стенд моделей ai-media: задания по рецептам стенда, сбор результатов, автометрики, контактные листы,
страница слепого попарного выбора (варианты картинок, кадры 3D, текстовые варианты), подсчёт голосов, мини-стенд новой
модели.

Python окружения скилла: PyYAML, numpy, scipy, Pillow. Сеть не нужна; платные вызовы делает только polza.py и только с
--live (ключ — переменная окружения владельца). Описание стенда — kb/ai-media/13-routing-matrix/; метод голосования —
13/01 §4.3.

Папка заданий стенда — $DDD_HOME/out/ai-media/stand или общий ключ --jobs-dir DIR (до подкоманды, как --tasks): в неё
пишут build и ministand, из неё читает estimate. Входные картинки и маска рецепта уходят в задание как записаны: URL,
абсолютный путь или путь от папки файла заданий — так их читает polza.py; от той же папки metrics читает source и target
задач. Вход, файла по которому нет, — строка отчёта «входа нет в скилле»: задание собирается, файл подставляют перед
прогоном.

Подкоманды:
  build     [--only E-02,E-08] [--agent ИМЯ]   рецепты tasks.yaml (ключ recipes) → задания polza.py в папке заданий
                                       (E-*.jsonl, + .routerai.json); промт — компилятор prompt_compile.py (диалект
                                       семейства по умолчанию) или буквальная строка; --agent — имя в поле agent заданий
                                       (по нему polza.py раскладывает выходы и ведёт журнал затрат), без ключа поля нет;
                                       модель рецепта вне снимка каталога — строка «ОШИБКА» с тестом и моделью, остальные
                                       группы собираются, код 1
  estimate  [--only …]                 polza.py estimate по заданиям E-* папки заданий → таблица «тест · заданий ·
                                       ошибок · ₽»; код 1 — есть задания с ошибками, 2 — polza.py вернул ошибку вызова
                                       или окружения (нет снимка каталога)
  run       JOBS.jsonl [--live] [--parallel 2]   прогон через polza.py batch (без --live — сухой прогон); код выхода —
                                       код polza.py batch (особые исходы от 3 — в справке polza.py)
  collect   [--root DIR] [--agent A] [--out results.jsonl]   паспорта polza.py под DIR → таблица результатов (строка на
                                       файл); DIR по умолчанию — выходы polza.py (POLZA_OUT_ROOT, иначе
                                       $DDD_HOME/out/ai-media/_polza); путь паспорта — от DIR; --agent — только его задания
  metrics   RESULTS.jsonl [--transcripts T.json] [--out metrics.jsonl]   автометрики по задачам (см. METRICS)
  sheet     RESULTS.jsonl --out DIR [--blind]      контактные листы по тестам (подписи моделей или буквы)
  page      ВХОД --out DIR [--tests E-08,E-10] [--repeat 0.1] [--seed 7] [--maxside 1600] [--lossless]
            страница слепых пар картинок (DIR/index.html + DIR/img/; ключ «картинка → вариант» — рядом, в
            DIR.key.json, в папку страницы не кладётся). ВХОД — папка выходов polza.py (паспорта), таблица collect
            или папка картинок без паспортов. Задания стенда — пары между моделями группы голосования; задания
            плана (prompt_compile.py jobs) — группа на спецификацию, пары между всеми её вариантами (вариант —
            «модель#номер»); папка картинок (кадры 3D, снимки сборок) — группа на подпапку, вариант — имя файла;
            --tests — только эти группы. Картинки страницы: сторона не больше --maxside (0 — без уменьшения),
            JPEG q90, с прозрачностью — PNG; --lossless — всегда PNG, пиксели без потерь. Пары на чёткость и
            мелкую деталь — `--maxside 0 --lossless`. Файл перекодируется, а не копируется: метаданные исходника
            (модель, промт) на слепую страницу не попадают; кодирование записано в ключ страницы (поле encoding)
  page      --text SHEET.md [--text-key KEY.yaml] --out DIR [--repeat 0.1] [--seed 7]
                                       те же слепые пары для текстовых вариантов: карточки текста из листа
                                       copydeck.py export-variants, пары — между вариантами одного слота
  tally     VOTES.json [VOTES2.json …] --key DIR.key.json [--out tally.md] [--selection VOTES.yaml]
                                       доли побед с интервалом Уилсона, Брэдли–Терри, согласованность повторов,
                                       позиционный сдвиг, контрольные пары; у текстовой страницы --selection — победы
                                       меток по слоту для copydeck.py apply-selection --votes (--method human-pairwise)
  ministand --model ID [--params '{"image_resolution":"1K"}'] [--vs PRESET] [--agent ИМЯ] [--out FILE]
                                       регрессионный набор для новой модели → E-MS-<модель>.jsonl в папке заданий или
                                       --out; --agent — как у build; задачи с полем pipeline (проверяет постобработка или
                                       видео) в набор не входят; модели нет в снимке каталога — код 2
  selftest                             офлайн-проверки (нормализация кириллицы, Уилсон, Брэдли–Терри, страницы картинок и
                                       текстов, сбор паспортов вне базы, кодирование картинок страницы, папка заданий
                                       и имя агента, модель вне снимка, путь входа от папки заданий в build и metrics)
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import html
import importlib.util
import io
import json
import math
import os
import random
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))  # scripts/lib: kbpaths
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("ai-media")
TOOLS = kbpaths.scripts("ai-media")
STAND = ROOT / "13-routing-matrix/stand"
TASKS = STAND / "tasks.yaml"
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif")   # что страница пар показывает картинкой
sys.path.insert(0, str(TOOLS))


def load_yaml(p):
    import yaml
    return yaml.safe_load(Path(p).read_text(encoding="utf-8"))


def jl_write(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def jl_read(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]


def slug(s):
    return re.sub(r"[^A-Za-z0-9.-]+", "-", str(s)).strip("-")


def jobs_dir(a):
    """Папка заданий стенда — выход, не kb: ключ --jobs-dir, иначе $DDD_HOME/out/ai-media/stand; создаётся."""
    d = Path(a.jobs_dir) if getattr(a, "jobs_dir", None) else kbpaths.out("ai-media", "stand", create=False)
    d.mkdir(parents=True, exist_ok=True)
    return d


def agent_field(a):
    """Поле agent задания — только с ключа --agent: без ключа поля нет, и polza.py берёт своё умолчание."""
    return {"agent": a.agent} if getattr(a, "agent", None) else {}


# ================================================================ build: рецепты → задания polza.py

def input_missing(path, base):
    """Локальный вход рецепта (абсолютный путь или путь от папки файла заданий — так его читает polza.py), файла по
    которому нет; URL и data:URI не проверяются."""
    s = str(path)
    if re.match(r"(https?|data):", s):
        return False
    p = Path(s)
    return not (p if p.is_absolute() else Path(base) / p).is_file()


def cmd_build(a):
    cfg = load_yaml(a.tasks)
    import polza_catalog as pcat
    import prompt_compile as pc
    snap, dialects, catalog = pcat.Snapshot(), pc.load_dialects(), pc.load_catalog()
    only = set(a.only.split(",")) if a.only else None
    jobs, agent = jobs_dir(a), agent_field(a)
    report, errors, absent = [], [], []
    snap_name = getattr(getattr(snap, "dir", None), "name", "")
    for grp in cfg["recipes"]:
        if only and grp["test"] not in only:
            continue
        rows, skipped = [], []
        for jd in grp["jobs"]:
            tid, task = jd["task"], cfg["tasks"][jd["task"]]
            arm = jd.get("arm", "a")
            ins = list(jd.get("images") or []) + ([jd["mask"]] if jd.get("mask") else []) \
                + [task[k] for k in ("source", "target") if task.get(k)]
            for pth in ins:
                line = f"{grp['test']}/{tid}: входа нет в скилле — {pth}"
                if input_missing(pth, jobs) and line not in absent:
                    absent.append(line)
            for preset in jd["use"]:
                mp = cfg["models"][preset]
                mid = mp["model"]
                if mid not in snap.by_id:          # модель выбыла из каталога: задания пресета не собираются
                    line = f"ОШИБКА: {grp['test']}: модели {mid} (пресет {preset}) нет в снимке каталога {snap_name}".rstrip()
                    if line not in errors:
                        errors.append(line)
                    continue
                params = dict(mp.get("params") or {})
                if jd.get("prompt"):
                    prompt = cfg["literals"][jd["prompt"]].replace("{subject}", jd.get("subject", ""))
                    dialect, cparams = "literal", {}
                else:
                    spec = json.loads((STAND / task["brief"]).read_text(encoding="utf-8"))
                    r = pc.compile_prompt(spec, mid, None, dialects, catalog)
                    if r["errors"]:
                        skipped.append({"task": tid, "model": mid, "errors": r["errors"]})
                        continue
                    prompt, dialect, cparams = r["prompt"], r["dialect"], dict(r["params"])
                    if jd.get("prefix"):
                        pre = cfg["literals"][jd["prefix"]].strip()
                        prompt = pre + prompt if pre.endswith(":") or pre.endswith(": ") else pre + "\n" + prompt
                    if jd.get("suffix"):
                        prompt += cfg["literals"][jd["suffix"]]
                inp = {"prompt": prompt, **cparams, **params, **(jd.get("params") or {})}
                if jd.get("images"):
                    inp["images"] = list(jd["images"])          # путь — как в рецепте: его разбирает polza.py
                if jd.get("mask"):
                    inp["mask_url"] = jd["mask"]
                model = snap.by_id[mid]
                mpar = model.get("parameters") or {}
                for k in [k for k in inp if k not in mpar and k != "prompt"]:
                    skipped.append({"task": tid, "model": mid, "dropped_param": k})
                    inp.pop(k)
                for i in range(jd.get("samples", 1)):
                    x = dict(inp)
                    if "seed" in mpar:
                        x["seed"] = cfg["seeds"][i % len(cfg["seeds"])]
                    variant = jd.get("variant_base", 1) + i
                    est = pcat.estimate(model, x, provider="mie", providers=snap.providers.get(mid))
                    rub = est.get("rub") or 0
                    meta = {"test": grp["test"], "task": tid, "code": task["code"], "arm": arm, "preset": preset,
                            "dialect": dialect, "compiler": cfg["compiler"], "compiled_prompt": dialect != "literal",
                            "judge": grp["judge"], "success": grp["success"], "value": jd.get("value", grp["value"]),
                            "expect": task.get("expect"), "brief": task.get("brief"), "catalog": cfg["catalog_snapshot"]}
                    purpose = ""
                    if task.get("brief") and task["brief"] != "literal":
                        purpose = json.loads((STAND / task["brief"]).read_text(encoding="utf-8"))["role"]["purpose"]
                    meta["brief_text"] = task["title"] + (f" — {purpose}" if purpose else "")
                    if jd.get("images"):
                        meta["ref"] = jd["images"][0]
                    vg = jd.get("vote_groups", [f"{grp['test']}/{tid}/{arm}"]) + ([jd["vote_extra"]] if jd.get("vote_extra") else [])
                    meta["vote_groups"] = [g.replace("{model}", mid) for g in vg]
                    if jd.get("vote_by_arm"):          # одна модель, разные плечи (черновик → финал): голосуем за плечо
                        meta["vote_id"] = f"{preset}:{arm}"
                    for k in ("source", "target", "target_rect", "target_hex"):
                        if task.get(k):
                            meta[k] = task[k]
                    if jd.get("inputs_from"):
                        meta["inputs_from"] = jd["inputs_from"]
                    if grp.get("depends"):
                        meta["depends"] = grp["depends"]
                    rows.append({"model": mid, "input": x, "provider": cfg["provider_default"],
                                 "tag": f"{grp['test']}-{tid}-{arm}-{preset}-{variant}", **agent, "variant": variant,
                                 "max_rub": math.ceil(rub * 1.25 * 10) / 10 if rub else None,
                                 "notes": grp["hypothesis"][:240], "meta": meta})
        out = jobs / grp["file"]
        jl_write(out, rows)
        report.append((grp["test"], out.name, len(rows), skipped))
    for ext in cfg.get("external", []):
        if only and ext["test"] not in only:
            continue
        body = {"model": ext["model"], "prompt": cfg["literals"][ext["prompt"]], "aspect_ratio": "16:9", "n": 1}
        job = {"channel": ext["channel"], "method": "POST", "path": "/api/v1/images", "body": body, "tag": f"{ext['test']}-recraft",
               **agent, "variant": 1, "max_rub": round(ext["price_rub"] * 1.5, 1), "price_rub": ext["price_rub"],
               "price_source": ext["price_source"], "docs": ext["docs"], "notes": ext["note"],
               "meta": {"test": ext["test"], "task": "S08", "code": "IMG-TEXT-CYR", "judge": "metric", "value": ext["value"],
                        "expect": cfg["tasks"]["S08"]["expect"], "success": "3 строки дословны по кодовым точкам (как E-02)"}}
        (jobs / ext["file"]).write_text(json.dumps(job, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        report.append((ext["test"], ext["file"], 1, []))
    for t, f, n, sk in report:
        print(f"{t}: {f} — заданий {n}" + (f"; пропуски/снятые параметры: {sk}" if sk else ""))
    for line in absent + errors:
        print(line)
    return 1 if errors else 0


# ================================================================ estimate / run: обёртки над polza.py

def e_files(jobs, only=None):
    fs = sorted(Path(jobs).glob("E-*.jsonl"))
    return [f for f in fs if not only or f.name[:4] in only]


def cmd_estimate(a):
    only = set(a.only.split(",")) if a.only else None
    total, rows, env_err = 0.0, [], False
    for f in e_files(jobs_dir(a), only):
        r = subprocess.run([sys.executable, str(TOOLS / "polza.py"), "estimate", str(f)], capture_output=True, text=True,
                           env={**__import__("os").environ, "POLZA_BASE_URL": "http://127.0.0.1:9"})
        m = re.search(r"ИТОГО: заданий (\d+), с ошибками (\d+), оценка суммы ([\d  ,]+) ₽", r.stdout)
        n, err, rub = (int(m.group(1)), int(m.group(2)), float(m.group(3).replace(" ", "").replace(" ", "").replace(",", "."))) if m else (0, -1, 0.0)
        total += rub
        rows.append((f.name, n, err, rub))
        env_err |= r.returncode == 2               # polza.py: ошибка вызова или окружения
        if err or not m:
            print(r.stdout[-1500:], r.stderr[-800:], file=sys.stderr)
    print("| Файл | Заданий | Ошибок | ₽ (estimate) |\n|---|---|---|---|")
    for name, n, err, rub in rows:
        print(f"| `{name}` | {n} | {err} | {rub:.2f} |")
    print(f"| **Итого** | {sum(r[1] for r in rows)} | {sum(max(r[2], 0) for r in rows)} | **{total:.2f}** |")
    return 2 if env_err else 0 if all(r[2] == 0 for r in rows) else 1


def cmd_run(a):
    cmd = [sys.executable, str(TOOLS / "polza.py"), "batch", a.jobs, "--parallel", str(a.parallel)]
    if a.live:
        cmd.append("--live")          # трата — только с ключом владельца и после сухого прогона
    return subprocess.call(cmd)


# ================================================================ collect: паспорта → результаты

def collect_rows(root, agent=None):
    """Паспорта polza.py под root → строки результатов (файл результата — строка); путь паспорта — от root."""
    root, rows = Path(root), []
    for pp in sorted(root.rglob("*.passport.json")):
        p = json.loads(pp.read_text(encoding="utf-8"))
        job = p.get("job") or {}
        meta = job.get("meta") or {}
        if agent and job.get("agent") != agent:
            continue
        for i, f in enumerate(p.get("files") or []):
            if not f.get("path"):
                continue
            media = f.get("media") or {}
            rows.append({"test": meta.get("test"), "task": meta.get("task"), "code": meta.get("code"), "arm": meta.get("arm"),
                         "preset": meta.get("preset"), "model": job.get("model"), "variant": job.get("variant"),
                         "file": f.get("path"), "file_index": i, "w": media.get("width"), "h": media.get("height"),
                         "bytes": f.get("bytes"), "cost_rub": (p.get("cost") or {}).get("usage_cost_rub"),
                         "wall_s": (p.get("timing") or {}).get("wall_s"), "provider_actual": p.get("provider_actual"),
                         "dialect": meta.get("dialect"), "meta": meta, "passport": str(pp.relative_to(root))})
    return rows


def cmd_collect(a):
    rows = collect_rows(a.root, a.agent)
    jl_write(a.out, rows)
    print(f"результатов: {len(rows)} → {a.out} (паспорта — от {a.root})")
    return 0


# ================================================================ метрики

def _img(path, mode="RGB", maxside=None, base=ROOT):
    """Картинка: относительный путь — от base (входы source и target задач — от папки файла заданий)."""
    from PIL import Image
    im = Image.open(Path(base) / path if not Path(path).is_absolute() else path)
    im = im.convert(mode)
    if maxside and max(im.size) > maxside:
        s = maxside / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return im


def srgb_lab(rgb):
    import numpy as np
    c = rgb / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def de2000(l1, l2):
    """CIEDE2000 для массивов Lab (…×3)."""
    import numpy as np
    L1, a1, b1 = l1[..., 0], l1[..., 1], l1[..., 2]
    L2, a2, b2 = l2[..., 0], l2[..., 1], l2[..., 2]
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p, h2p = np.degrees(np.arctan2(b1, a1p)) % 360, np.degrees(np.arctan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dh = h2p - h1p
    dh = np.where(C1p * C2p == 0, 0, np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh)))
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hs = h1p + h2p
    hbp = np.where(C1p * C2p == 0, hs, np.where(np.abs(h1p - h2p) <= 180, hs / 2, np.where(hs < 360, (hs + 360) / 2, (hs - 360) / 2)))
    T = 1 - 0.17 * np.cos(np.radians(hbp - 30)) + 0.24 * np.cos(np.radians(2 * hbp)) + 0.32 * np.cos(np.radians(3 * hbp + 6)) \
        - 0.20 * np.cos(np.radians(4 * hbp - 63))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / np.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) * np.sin(np.radians(60 * np.exp(-((hbp - 275) / 25) ** 2)))
    return np.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))


def hex_lab(h):
    import numpy as np
    h = h.lstrip("#")
    return srgb_lab(np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)]], float))[0]


def dominant(rgb, k=6, iters=12, seed=0):
    """k-средних в Lab по подвыборке: [(lab, доля)] по убыванию доли."""
    import numpy as np
    px = srgb_lab(rgb.reshape(-1, 3).astype(float))
    rng = np.random.default_rng(seed)
    px = px[rng.choice(len(px), min(len(px), 20000), replace=False)]
    cen = px[rng.choice(len(px), k, replace=False)]
    for _ in range(iters):
        lab = ((px[:, None, :] - cen[None]) ** 2).sum(-1).argmin(1)
        cen = np.array([px[lab == j].mean(0) if (lab == j).any() else cen[j] for j in range(k)])
    share = np.bincount(lab, minlength=k) / len(px)
    order = share.argsort()[::-1]
    return [(cen[j], float(share[j])) for j in order]


def ssim_gray(x, y, mask=None):
    import numpy as np
    from scipy.ndimage import gaussian_filter
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mx, my = gaussian_filter(x, 1.5), gaussian_filter(y, 1.5)
    sxx = gaussian_filter(x * x, 1.5) - mx * mx
    syy = gaussian_filter(y * y, 1.5) - my * my
    sxy = gaussian_filter(x * y, 1.5) - mx * my
    m = ((2 * mx * my + C1) * (2 * sxy + C2)) / ((mx * mx + my * my + C1) * (sxx + syy + C2))
    return float(m[mask].mean() if mask is not None else m.mean())


def phash(im):
    import numpy as np
    from scipy.fft import dctn
    g = np.asarray(im.convert("L").resize((32, 32))).astype(float)
    d = dctn(g, norm="ortho")[:8, :8].flatten()[1:]
    bits = d > np.median(d)
    return "".join("1" if b else "0" for b in bits)


# --- кириллица: сверка транскрипта (OCR / VLM / человек) с эталоном по кодовым точкам
HOMO_TO_CYR = str.maketrans({"A": "А", "B": "В", "E": "Е", "K": "К", "M": "М", "H": "Н", "O": "О", "P": "Р", "C": "С",
                             "T": "Т", "X": "Х", "Y": "У", "a": "а", "e": "е", "o": "о", "p": "р", "c": "с", "x": "х",
                             "y": "у", "3": "З"})
CYR = re.compile(r"[А-Яа-яЁё]")
LAT = re.compile(r"[A-Za-z]")
DASHES = str.maketrans({"−": "-", "–": "-", "—": "-", "‑": "-", "«": '"', "»": '"', "„": '"', "“": '"', "”": '"',
                        " ": " ", " ": " ", " ": " ", "·": "·", "•": "·"})


def norm_line(s, homoglyphs=True):
    s = unicodedata.normalize("NFC", s).translate(DASHES)
    s = re.sub(r"\s+", " ", s).strip()
    if homoglyphs:          # визуально одинаковые латинские буквы внутри русских слов → кириллица (OCR их не различает)
        s = " ".join(w.translate(HOMO_TO_CYR) if CYR.search(w) else w for w in s.split(" "))
    return s


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def text_check(expect, transcript):
    """Эталонные строки против транскрипта картинки. Возвращает долю дословных строк (строго и без учёта регистра),
    CER лучшего окна, «латинские недвойники» в русских словах (N вместо И, R вместо Я …) и лишние слова."""
    raw_words = unicodedata.normalize("NFC", transcript).split()
    fake = [w for w in raw_words if CYR.search(w) and any(LAT.match(ch) and ch not in "ABEKMHOPCTXYaeopcxy" for ch in w)]
    T = norm_line(transcript)
    res, exp_words = [], set()
    for e in expect:
        E = norm_line(e)
        exp_words |= {w.lower().strip('.,:;!?"') for w in E.split()}
        best = min((lev(E.lower(), T.lower()[i:i + len(E)]) for i in range(max(1, len(T) - len(E) + 1))), default=len(E))
        res.append({"expect": e, "exact": E in T, "exact_ci": E.lower() in T.lower(), "cer": round(best / max(1, len(E)), 3),
                    "yo_lost": ("ё" in E.lower()) and (E.lower().replace("ё", "е") in T.lower()) and (E.lower() not in T.lower())})
    extra = [w for w in T.split() if w.lower().strip('.,:;!?"') not in exp_words and re.search(r"\w", w)]
    return {"lines": res, "exact_share": round(sum(r["exact"] for r in res) / len(res), 3),
            "exact_ci_share": round(sum(r["exact_ci"] for r in res) / len(res), 3),
            "fake_latin": fake, "extra_words": extra, "pass": all(r["exact_ci"] for r in res) and not fake and not extra}


def load_a04():
    p = TOOLS / "image_metrics.py"
    spec = importlib.util.spec_from_file_location("image_metrics_a04", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A04_Q3 = {"colorfulness": 54.5, "sat_share": 0.0748, "hdr_index": 0.349, "clip_hi": 0.14}   # Q3 фото лидеров


def metrics_for(row, transcripts, a04, inputs=ROOT):
    import numpy as np
    meta, out = row.get("meta") or {}, {}
    im = _img(row["file"], "RGBA")
    rgba = np.asarray(im)
    rgb = rgba[..., :3].astype(float)
    out["dims"] = {"w": im.width, "h": im.height, "ratio": round(im.width / im.height, 3), "bytes": row.get("bytes")}
    alpha = rgba[..., 3]
    out["alpha"] = {"has_alpha": bool((alpha < 250).any()), "transparent": round(float((alpha < 10).mean()), 4),
                    "semi": round(float(((alpha >= 10) & (alpha < 245)).mean()), 4)}
    small = np.asarray(_img(row["file"], "RGB", 1024)).astype(float)
    out["slop_color"] = {k: v for k, v in a04.metrics(small).items() if k in ("colorfulness", "sat_share", "hdr_index", "clip_hi", "warm_b", "purple_share")}
    out["slop_color"]["over_q3"] = [k for k, q in A04_Q3.items() if (out["slop_color"].get(k) or 0) > q]
    out["phash"] = phash(im)
    brief = meta.get("brief")
    spec = json.loads((STAND / brief).read_text(encoding="utf-8")) if brief and brief != "literal" else {}
    pal = [p["hex"] for p in spec.get("palette", [])] + ([meta["target_hex"]] if meta.get("target_hex") else [])
    if pal:
        dom = dominant(small)
        out["palette_de"] = {h: round(float(min(de2000(hex_lab(h), c) for c, s in dom if s > 0.02)), 2) for h in pal}
    tz = (spec.get("composition") or {}).get("text_zone")
    if tz:
        from scipy.ndimage import sobel
        L = srgb_lab(small)[..., 0] / 100
        g = np.hypot(sobel(L, 0), sobel(L, 1))
        H, W = L.shape
        x0, y0, x1, y1 = tz["rect"]
        zone = np.zeros_like(L, bool)
        zone[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)] = True
        out["text_zone"] = {"edge_zone": round(float(g[zone].mean()), 4), "edge_rest": round(float(g[~zone].mean()), 4),
                            "ratio": round(float(g[zone].mean() / max(g[~zone].mean(), 1e-6)), 3),
                            "lum_std_zone": round(float(L[zone].std()), 4)}
    if meta.get("source"):
        src = _img(meta["source"], "RGB", base=inputs)
        out_im = _img(row["file"], "RGB").resize(src.size)
        A, B = np.asarray(src).astype(float), np.asarray(out_im).astype(float)
        if meta.get("target"):
            tgt = np.asarray(_img(meta["target"], "L", base=inputs).resize(src.size)) > 127
        else:
            tgt = np.zeros(A.shape[:2], bool)
            x0, y0, x1, y1 = meta.get("target_rect", [0, 0, 0, 0])
            tgt[y0:y1, x0:x1] = True
        dE = de2000(srgb_lab(A), srgb_lab(B))
        ga, gb = A.mean(2), B.mean(2)
        out["edit_diff"] = {"de_out_mean": round(float(dE[~tgt].mean()), 2), "de_out_p95": round(float(np.percentile(dE[~tgt], 95)), 2),
                            "changed_out_share": round(float((dE[~tgt] > 10).mean()), 4),
                            "ssim_out": round(ssim_gray(ga, gb, __import__("scipy.ndimage", fromlist=["x"]).binary_erosion(~tgt, iterations=8)), 4),
                            "de_in_mean": round(float(dE[tgt].mean()), 2)}
        if meta.get("target_hex"):
            med = np.median(srgb_lab(B)[tgt], 0)
            out["edit_diff"]["target_de"] = round(float(de2000(hex_lab(meta["target_hex"]), med)), 2)
    if meta.get("expect"):
        t = transcripts.get(row["file"])
        out["text"] = text_check(meta["expect"], t) if t is not None else {"pending": "нужен транскрипт (OCR ru/VLM/человек)"}
    return out


def cmd_metrics(a):
    rows = jl_read(a.results)
    transcripts = json.loads(Path(a.transcripts).read_text(encoding="utf-8")) if a.transcripts else {}
    a04 = load_a04()
    inputs = jobs_dir(a)                    # входы задач — от папки файла заданий, как их читает polza.py
    outs = []
    for r in rows:
        try:
            m = metrics_for(r, transcripts, a04, inputs)
        except Exception as e:          # noqa: BLE001
            m = {"error": str(e)[:200]}
        outs.append({**{k: r.get(k) for k in ("test", "task", "arm", "preset", "model", "variant", "file")}, "m": m})
        print(json.dumps(outs[-1], ensure_ascii=False)[:300])
    jl_write(a.out, outs)
    return 0


# ================================================================ контактные листы

def cmd_sheet(a):
    from PIL import Image, ImageDraw, ImageFont
    rows = jl_read(a.results)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    by = {}
    for r in rows:
        by.setdefault(r["test"], []).append(r)
    for test, rs in by.items():
        rs.sort(key=lambda r: (r.get("task") or "", r.get("arm") or "", r.get("preset") or "", r.get("variant") or 0))
        cols, cw = 4, 400
        tiles = []
        for i, r in enumerate(rs):
            im = _img(r["file"], "RGB")
            im.thumbnail((cw, cw))
            label = chr(65 + i % 26) if a.blind else f"{r.get('task')}/{r.get('arm')} {r.get('preset')} #{r.get('variant')}"
            tiles.append((im, label))
        rows_n = math.ceil(len(tiles) / cols)
        sh = Image.new("RGB", (cols * cw, rows_n * (cw + 28)), (40, 40, 40))
        d = ImageDraw.Draw(sh)
        for i, (im, lab) in enumerate(tiles):
            x, y = (i % cols) * cw, (i // cols) * (cw + 28)
            sh.paste(im, (x + (cw - im.width) // 2, y))
            d.text((x + 6, y + cw + 4), lab, fill=(230, 230, 230), font=font)
        sh.save(out / f"{test}{'-blind' if a.blind else ''}.jpg", quality=88)
        print(out / f"{test}{'-blind' if a.blind else ''}.jpg")
    return 0


# ================================================================ страница слепого голосования

QUESTIONS = [
    {"id": "slot", "text": "Что лучше для слота на сайте (как будет стоять на странице)?", "options": ["A", "B", "=", "0"]},
    {"id": "natural", "text": "Что естественнее и ближе к брифу (меньше «сделано нейросетью»)?", "options": ["A", "B", "="]},
]
TEXT_QUESTIONS = [
    {"id": "slot", "text": "Какой текст лучше для этого места на странице?", "options": ["A", "B", "=", "0"]},
]
HINTS = {"image": "Клавиши: ← A, → B, ↓ равно, X — оба не годятся (вопрос 1); затем те же для вопроса 2. Пробел — увеличить "
                  "(A/B переключает Tab), M — макет с текстом, Backspace — назад.",
         "text": "Клавиши: ← A, → B, ↓ равно, X — оба не годятся; Backspace — назад. Тексты — дословно, как на странице."}


def parse_variants_sheet(text):
    """Лист слепого выбора copydeck.py export-variants → [{path, stype, context, variants: [(метка, текст)]}]: секция
    «## <путь> · <тип слота>», строка «Контекст: …», варианты «- **A**: текст»."""
    slots, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^##\s+(\S+)\s+·\s*(.*)$", line.strip())
        if m:
            cur = {"path": m.group(1), "stype": m.group(2).strip(), "context": "", "variants": []}
            slots.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"^Контекст:\s*(.*)$", line.strip())
        if m:
            cur["context"] = m.group(1).strip()
            continue
        m = re.match(r"^-\s+\*\*([A-Z])\*\*:\s?(.*)$", line.strip())
        if m:
            cur["variants"].append((m.group(1), m.group(2)))
    return [x for x in slots if len(x["variants"]) >= 2]


def _encode(im, maxside=1600, lossless=False):
    """Картинка → байты и расширение: JPEG (без альфы) или PNG (с альфой), сторона ≤ maxside (0 или None — без
    уменьшения). lossless — всегда PNG: пиксели без потерь, альфа остаётся, если она есть хоть в одной точке."""
    im = im.copy()
    if maxside:
        im.thumbnail((maxside, maxside))
    buf = io.BytesIO()
    alpha = im.mode == "RGBA" and min(im.getchannel("A").getextrema()) < (255 if lossless else 250)
    if alpha or lossless:
        (im if alpha else im.convert("RGB")).save(buf, "PNG", optimize=True)
        return buf.getvalue(), "png"
    im.convert("RGB").save(buf, "JPEG", quality=90, optimize=True)
    return buf.getvalue(), "jpg"


def build_page(items, out, title="Стенд моделей — слепое сравнение", repeat=0.1, seed=7, gold=True, kind="image",
               maxside=1600, lossless=False):
    """items: [{"group": ключ сравнения, "brief": текст, "text_zone": [x0,y0,x1,y1] | None, "copy": [...],
    "ref": путь эталона | None, "model": …, "files": [пути] , "test": …}] — пары строятся внутри group между разными моделями.
    kind="text": у элемента вместо files — "text" (карточка текста), model — метка варианта листа; контрольных пар с
    размытием нет, одинаковая пара — та же карточка с обеих сторон. maxside и lossless — кодирование картинок страницы
    (см. _encode); оно записано в ключ страницы, поле encoding."""
    from PIL import Image, ImageFilter
    rnd = random.Random(seed)
    out = Path(out)
    (out / "img").mkdir(parents=True, exist_ok=True)
    key = {"page": out.name, "built": dt.datetime.now().isoformat(timespec="seconds"), "images": {}, "pairs": {}}
    img_ids = {}

    def put(path, degrade=False):
        k = (str(path), degrade)
        if k in img_ids:
            return img_ids[k]
        im = Image.open(ROOT / path if not Path(path).is_absolute() else path)
        im = im.convert("RGBA")
        if degrade:
            im = im.filter(ImageFilter.GaussianBlur(6)).convert("RGB")
        data, ext = _encode(im, maxside, lossless)
        iid = f"{rnd.getrandbits(40):010x}"
        (out / "img" / f"{iid}.{ext}").write_bytes(data)
        img_ids[k] = f"img/{iid}.{ext}"
        return img_ids[k]

    groups = {}
    for it in items:
        groups.setdefault(it["group"], []).append(it)
    pairs = []
    for g, its in groups.items():
        for i in range(len(its)):
            for j in range(i + 1, len(its)):
                x, y = its[i], its[j]
                if x["model"] == y["model"]:
                    continue
                if rnd.random() < 0.5:
                    x, y = y, x
                pairs.append({"g": g, "A": x, "B": y})
    rnd.shuffle(pairs)
    half = len(pairs) // 2
    first, second = pairs[:half], pairs[half:]
    rep = rnd.sample(first, min(len(first), max(1, round(len(pairs) * repeat)))) if first and repeat > 0 else []
    extra = [{"g": p["g"], "A": p["B"], "B": p["A"], "repeat_of": id(p)} for p in rep]
    golds = []
    if gold and pairs and kind == "image":
        for p in rnd.sample(pairs, max(1, len(pairs) // 20)):
            good = p["A"]
            golds.append({"g": p["g"], "A": good, "B": dict(good, _degrade=True), "gold": "A"} if rnd.random() < 0.5 else
                         {"g": p["g"], "A": dict(good, _degrade=True), "B": good, "gold": "B"})
    same = []                                   # одна и та же картинка с обеих сторон: ожидается «равно» или «оба не годятся»
    if gold and pairs:
        it = rnd.choice(pairs)["A"]
        same.append({"g": it["group"], "A": it, "B": it, "identical": True})
    tail = second + extra + golds + same
    rnd.shuffle(tail)
    seq = first + tail
    pid_of = {id(p): f"p{n + 1:03d}" for n, p in enumerate(seq)}
    questions = TEXT_QUESTIONS if kind == "text" else QUESTIONS
    data = {"title": title, "kind": kind, "questions": questions, "hint": HINTS[kind], "pairs": []}
    key["kind"] = kind
    if kind == "image":
        key["encoding"] = {"maxside": maxside or None, "lossless": bool(lossless)}
    key["questions"] = [q["id"] for q in questions]
    for p in seq:
        pid = pid_of[id(p)]
        side = {}
        for s in ("A", "B"):
            it = p[s]
            side[s] = [it["text"]] if kind == "text" else [put(f, it.get("_degrade", False)) for f in it["files"]]
        first = p["A"]
        rec = {"id": pid, "brief": first.get("brief", ""), "tz": first.get("text_zone"), "copy": first.get("copy") or [],
               "ref": put(first["ref"]) if first.get("ref") else None, "A": side["A"], "B": side["B"]}
        data["pairs"].append(rec)
        key["pairs"][pid] = {"group": p["g"], "A": {"model": p["A"]["model"], "files": p["A"].get("files") or [], "degraded": p["A"].get("_degrade", False)},
                             "B": {"model": p["B"]["model"], "files": p["B"].get("files") or [], "degraded": p["B"].get("_degrade", False)},
                             "test": first.get("test"), "gold": p.get("gold"), "identical": p.get("identical", False),
                             "repeat_of": pid_of.get(p.get("repeat_of")) if p.get("repeat_of") else None}
        if kind == "text":
            for s in ("A", "B"):
                key["pairs"][pid][s].update({"text": p[s]["text"], **({"variant": p[s]["variant"]} if p[s].get("variant") else {})})
    for (path, deg), iid in img_ids.items():
        key["images"][iid] = {"file": path, "degraded": deg}
    page = PAGE_HTML.replace("__TITLE__", html.escape(title)).replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (out / "index.html").write_text(page, encoding="utf-8")
    Path(str(out) + ".key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"pairs": len(seq), "main": len(pairs), "repeats": len(extra), "gold": len(golds), "identical": len(same), "images": len(img_ids)}


def cmd_page(a):
    if a.text:
        slots = parse_variants_sheet(Path(a.text).read_text(encoding="utf-8"))
        labels = load_yaml(a.text_key) if a.text_key else {}
        items = [{"group": sl["path"], "model": lab, "text": txt, "brief": sl["context"] or sl["path"], "test": sl["path"],
                  **({"variant": str(labels[sl["path"]][lab])} if isinstance(labels.get(sl["path"]), dict) and lab in labels[sl["path"]] else {})}
                 for sl in slots for lab, txt in sl["variants"]]
        if not items:
            print(f"в листе {a.text} нет слотов с двумя вариантами и больше", file=sys.stderr)
            return 2
        st = build_page(items, a.out, title="Тексты — слепое сравнение", repeat=a.repeat, seed=a.seed, kind="text")
        print(json.dumps(st, ensure_ascii=False))
        return 0
    if not a.results or not Path(a.results).exists():
        print(f"нет входа страницы {a.results or ''}: нужна папка выходов polza.py, таблица collect, папка картинок "
              f"или --text SHEET.md", file=sys.stderr)
        return 2
    maxside, lossless = getattr(a, "maxside", 1600), getattr(a, "lossless", False)
    if maxside is not None and maxside < 0:
        print(f"--maxside {maxside}: нужна сторона в пикселях или 0 (без уменьшения)", file=sys.stderr)
        return 2
    src = Path(a.results)
    rows = page_rows(src)
    tests = set(a.tests.split(",")) if a.tests else None
    by, seen, other = {}, {}, 0
    for r in rows:
        meta = r.get("meta") or {}
        if Path(str(r.get("file") or "")).suffix.lower() not in IMAGE_EXT:
            other += 1
            continue
        if meta.get("vote_groups") or meta.get("task"):       # задания стенда: пары между моделями группы голосования
            for grp in meta.get("vote_groups") or [f"{r['test']}/{r.get('task')}/{r.get('arm')}"]:
                if tests and grp.split("/")[0] not in tests:
                    continue
                key = (grp, meta.get("vote_id") or r.get("preset") or r.get("model"), r.get("variant"), r.get("file_index"))
                by.setdefault(key, []).append(r)
            continue
        # задания плана и папка картинок: группа — спецификация (подпапка), пары между всеми вариантами группы
        grp = meta.get("group") or meta.get("spec") or r.get("test") or src.resolve().name
        if tests and grp.split("/")[0] not in tests:
            continue
        label = meta.get("label") or (f"{r.get('model')}#{r.get('variant') or 1}"
                                      + (f".{r['file_index'] + 1}" if r.get("file_index") else ""))
        base, n = label, 1
        while label in seen.setdefault(grp, set()):
            n += 1
            label = f"{base}·{n}"
        seen[grp].add(label)
        by[(grp, label, None, None)] = [r]
    if other:
        print(f"не картинки — на страницу не попали файлов: {other}", file=sys.stderr)
    items = []
    for (grp, model, _, _), rs in by.items():
        meta = rs[0].get("meta") or {}
        brief = meta.get("brief")
        spec = json.loads((STAND / brief).read_text(encoding="utf-8")) if brief and brief != "literal" else {}
        tz = ((spec.get("composition") or {}).get("text_zone") or {}).get("rect")
        items.append({"group": grp, "model": model, "files": [r["file"] for r in rs], "test": grp.split("/")[0],
                      "brief": meta.get("brief_text") or meta.get("success") or meta.get("spec") or meta.get("group") or "",
                      "text_zone": tz, "copy": (spec.get("text") or {}).get("copy"), "ref": meta.get("ref")})
    if not items:
        print(f"в {src} нет картинок для пар", file=sys.stderr)
        return 2
    st = build_page(items, a.out, repeat=a.repeat, seed=a.seed, maxside=maxside, lossless=lossless)
    print(json.dumps(st, ensure_ascii=False))
    return 0


def page_rows(src):
    """Вход страницы картинок → строки результатов: таблица collect (файл); паспорта polza.py в папке; если паспортов
    нет — картинки папки (строка на файл: группа — подпапка, вариант — имя файла)."""
    src = Path(src)
    if src.is_file():
        return jl_read(src)
    rows = collect_rows(src)
    if rows:
        return rows
    for f in sorted(x for x in src.rglob("*") if x.is_file() and x.suffix.lower() in IMAGE_EXT):
        grp = f.parent.relative_to(src).as_posix() if f.parent != src else src.resolve().name
        rows.append({"model": None, "variant": None, "file": str(f.resolve()), "file_index": 0,
                     "meta": {"group": grp, "label": f.stem}})
    return rows


PAGE_HTML = r"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#2b2b2b;--panel:#353535;--ink:#ececec;--mut:#a9a9a9;--acc:#7fb3ff;--ok:#6fcf97;--line:#4a4a4a}
:root[data-bg="mid"]{--bg:#7a7a7a;--panel:#6c6c6c;--ink:#111;--mut:#262626;--line:#8a8a8a}
:root[data-bg="light"]{--bg:#f3f2ef;--panel:#e6e4df;--ink:#161616;--mut:#555;--line:#cfccc5;--acc:#1f5eff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:10px 16px;background:var(--panel);border-bottom:1px solid var(--line)}
header h1{font-size:16px;margin:0 12px 0 0;font-weight:600}.grow{flex:1}
button,select,input{font:inherit;color:inherit;background:transparent;border:1px solid var(--line);border-radius:8px;padding:6px 10px;cursor:pointer}
button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.bar{height:6px;background:var(--line);border-radius:3px;min-width:120px;flex:0 0 180px}.bar>i{display:block;height:100%;background:var(--acc);border-radius:3px}
main{padding:12px 16px 90px;max-width:1800px;margin:0 auto}
.brief{color:var(--mut);margin:4px 0 10px}.ref{display:flex;gap:10px;align-items:center;margin-bottom:8px;color:var(--mut)}.ref img{max-height:120px;border-radius:6px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.side{position:relative;background:var(--panel);border-radius:10px;padding:8px}
.side h2{margin:0 0 6px;font-size:14px;color:var(--mut);font-weight:600}
.shots{display:grid;gap:6px}.shots.n2{grid-template-columns:1fr 1fr}
.shot{position:relative}.shot img{display:block;width:100%;height:auto;border-radius:6px;cursor:zoom-in;background:repeating-conic-gradient(#999 0 25%,#ccc 0 50%) 0 0/16px 16px}
.tz{position:absolute;display:none;flex-direction:column;justify-content:center;padding:4%;pointer-events:none;font-weight:700;text-shadow:0 1px 2px rgba(0,0,0,.25)}
.mock .tz{display:flex}.tz b{font-size:clamp(14px,2.2vw,34px);line-height:1.1}.tz span{font-weight:400;font-size:clamp(10px,1.1vw,18px);margin-top:.4em}
.q{margin-top:12px;background:var(--panel);border-radius:10px;padding:10px 12px}.q p{margin:0 0 8px;font-weight:600}
.q .opts{display:flex;gap:8px;flex-wrap:wrap}.q button[aria-pressed="true"]{background:var(--acc);color:#111;border-color:var(--acc)}
#mockbtn[aria-pressed="true"]{background:var(--acc);color:#111}.q.dim{opacity:.55}.hint{color:var(--mut);font-size:13px;margin-top:10px}
textarea{width:100%;min-height:38px;margin-top:8px;font:inherit;color:inherit;background:transparent;border:1px solid var(--line);border-radius:8px;padding:6px}
#zoom{position:fixed;inset:0;background:#000d;display:none;align-items:center;justify-content:center;z-index:9}#zoom.on{display:flex}
#zoom img{max-width:100vw;max-height:100vh;image-rendering:auto}#zoom .lab{position:fixed;top:10px;left:14px;color:#fff;font-weight:700}
footer{position:fixed;left:0;right:0;bottom:0;display:flex;gap:8px;align-items:center;padding:10px 16px;background:var(--panel);border-top:1px solid var(--line)}
.done{padding:40px 16px;text-align:center}.warn{color:#ffb547}
.card{background:var(--bg);border-radius:6px;padding:14px 16px;font-size:17px;line-height:1.5;white-space:pre-wrap;min-height:64px}
@media (max-width:760px){.pair{grid-template-columns:1fr}.shots.n2{grid-template-columns:1fr}}
</style></head><body>
<header><h1>__TITLE__</h1><span id="prog"></span><div class="bar"><i id="barfill" style="width:0"></i></div><div class="grow"></div>
<label>Фон <select id="bgsel"><option value="dark">тёмный</option><option value="mid">серый</option><option value="light">светлый</option></select></label>
<button id="mockbtn" aria-pressed="false" title="клавиша M">Макет с текстом (M)</button>
<input id="voter" placeholder="Кто голосует (Enter)" size="16"></header>
<main id="main"></main>
<div id="zoom" role="dialog" aria-label="Увеличение"><span class="lab" id="zlab"></span><img id="zimg" alt=""></div>
<footer><button id="prev">← Назад</button><button id="skip">Пропустить</button><div class="grow"></div>
<span id="saved" class="hint"></span><button id="export">Скачать голоса (JSON)</button><button id="copy">Скопировать</button>
<label class="hint" style="cursor:pointer">Загрузить <input id="imp" type="file" accept="application/json" hidden></label></footer>
<script type="application/json" id="data">__DATA__</script>
<script>
(()=>{const D=JSON.parse(document.getElementById('data').textContent);const KEY='stand-votes:'+D.title+':'+D.pairs.length;
let S={voter:'',i:0,votes:{},started:new Date().toISOString(),mock:false,bg:'dark'};
try{const s=JSON.parse(localStorage.getItem(KEY)||'null');if(s&&s.votes)S=Object.assign(S,s)}catch(e){}
const $=id=>document.getElementById(id);let shown=0,zoomSide='A';
function save(){S.updated=new Date().toISOString();try{localStorage.setItem(KEY,JSON.stringify(S));$('saved').textContent='сохранено в браузере'}catch(e){$('saved').textContent='браузер не сохраняет — скачайте JSON'}}
function applyUI(){document.documentElement.dataset.bg=S.bg;$('bgsel').value=S.bg;$('mockbtn').setAttribute('aria-pressed',S.mock);$('voter').value=S.voter||''}
function answered(){return Object.values(S.votes).filter(v=>D.questions.every(q=>v[q.id])).length}
function prog(){const n=D.pairs.length,a=answered();$('prog').textContent=`${Math.min(S.i+1,n)} / ${n} · готово ${a}`;$('barfill').style.width=(100*a/n)+'%'}
function esc(s){return String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function shots(p,s){if(D.kind==='text')return `<div class="card">${esc(p[s][0])}</div>`;const f=p[s];return `<div class="shots ${f.length>1?'n2':''}">`+f.map(src=>`<div class="shot">${tz(p)}<img src="${src}" alt="Вариант ${s}" loading="eager" data-side="${s}"></div>`).join('')+'</div>'}
function tz(p){if(!p.tz)return'';const[x0,y0,x1,y1]=p.tz;const c=p.copy||[];const col='#1E1E1E';
 return `<div class="tz" style="left:${x0*100}%;top:${y0*100}%;width:${(x1-x0)*100}%;height:${(y1-y0)*100}%;color:${col}"><b>${esc(c[0]||'Заголовок страницы')}</b><span>${esc(c[1]||'')}</span></div>`}
function render(){prog();const m=$('main');if(S.i>=D.pairs.length){m.innerHTML=`<div class="done"><h2>Готово: ${answered()} из ${D.pairs.length}</h2><p>Нажмите «Скачать голоса (JSON)» и отправьте файл. Можно вернуться кнопкой «Назад».</p>${answered()<D.pairs.length?'<p class="warn">Есть неотвеченные пары — они будут пропущены при подсчёте.</p>':''}</div>`;return}
 const p=D.pairs[S.i],v=S.votes[p.id]||{};shown=performance.now();
 m.innerHTML=`<p class="brief">${esc(p.brief)}</p>${p.ref?`<div class="ref"><img src="${p.ref}" alt="Эталон"><span>Эталон: результат должен совпадать с ним (товар, стиль)</span></div>`:''}
 <div class="pair ${S.mock?'mock':''}"><section class="side"><h2>A</h2>${shots(p,'A')}</section><section class="side"><h2>B</h2>${shots(p,'B')}</section></div>`+
 D.questions.map((q,k)=>`<div class="q ${k>0&&!v[D.questions[k-1].id]?'dim':''}" data-q="${q.id}"><p>${k+1}. ${esc(q.text)}</p><div class="opts">`+
  q.options.map(o=>`<button data-o="${o}" aria-pressed="${v[q.id]===o}">${o==='A'?'A лучше':o==='B'?'B лучше':o==='='?'Равно':'Оба не годятся'}</button>`).join('')+'</div></div>').join('')+
 `<textarea id="cm" placeholder="Почему (необязательно): дефект, «пластик», лишний текст…">${esc(v.comment||'')}</textarea>
 <p class="hint">${esc(D.hint||'')}</p>`;
 m.querySelectorAll('.q button').forEach(b=>b.onclick=()=>answer(b.closest('.q').dataset.q,b.dataset.o));
 m.querySelectorAll('.shot img').forEach(im=>im.onclick=()=>openZoom(im.dataset.side,im.src));
 $('cm').oninput=e=>{(S.votes[p.id]=S.votes[p.id]||{}).comment=e.target.value;save()}}
function answer(qid,o){const p=D.pairs[S.i];const v=S.votes[p.id]=S.votes[p.id]||{};v[qid]=o;v.ms=(v.ms||0)+Math.round(performance.now()-shown);v.at=new Date().toISOString();
 v.left=p.A;v.right=p.B;save();if(D.questions.every(q=>v[q.id])){setTimeout(()=>{S.i++;save();render()},220)}else render()}
function cur(){const p=D.pairs[S.i];if(!p)return null;const v=S.votes[p.id]||{};return D.questions.find(q=>!v[q.id])||D.questions[D.questions.length-1]}
function openZoom(side,src){zoomSide=side;$('zimg').src=src||D.pairs[S.i][side][0];$('zlab').textContent=side+' (Tab — другой вариант, Esc — закрыть)';$('zoom').classList.add('on')}
$('zoom').onclick=()=>$('zoom').classList.remove('on');
document.addEventListener('keydown',e=>{if(e.target.tagName==='TEXTAREA'||e.target.tagName==='INPUT')return;const z=$('zoom').classList.contains('on');
 if(z){if(e.key==='Escape'||e.key===' '){$('zoom').classList.remove('on');e.preventDefault()}if(e.key==='Tab'){e.preventDefault();openZoom(zoomSide==='A'?'B':'A')}return}
 const q=cur();if(!q)return;const map={ArrowLeft:'A',ArrowRight:'B',ArrowDown:'=',x:'0',X:'0',ч:'0',Ч:'0'};
 if(map[e.key]&&q.options.includes(map[e.key])){e.preventDefault();answer(q.id,map[e.key])}
 else if(e.key===' '&&D.kind!=='text'){e.preventDefault();openZoom('A')}else if((e.key==='m'||e.key==='M'||e.key==='ь')&&D.kind!=='text'){toggleMock()}
 else if(e.key==='Backspace'){e.preventDefault();S.i=Math.max(0,S.i-1);save();render()}});
function toggleMock(){S.mock=!S.mock;save();applyUI();render()}
$('mockbtn').onclick=toggleMock;$('bgsel').onchange=e=>{S.bg=e.target.value;save();applyUI()};$('voter').oninput=e=>{S.voter=e.target.value;save()};$('voter').onkeydown=e=>{if(e.key==='Enter'||e.key==='Escape')e.target.blur()};
$('prev').onclick=()=>{S.i=Math.max(0,S.i-1);save();render()};$('skip').onclick=()=>{S.i=Math.min(D.pairs.length,S.i+1);save();render()};
function payload(){return JSON.stringify({page:D.title,pairs_total:D.pairs.length,voter:S.voter,started:S.started,exported:new Date().toISOString(),ua:navigator.userAgent,votes:S.votes},null,1)}
$('export').onclick=()=>{const b=new Blob([payload()],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);
 a.download=`votes-${(S.voter||'anon').replace(/\W+/g,'_')}-${new Date().toISOString().slice(0,16).replace(/[:T]/g,'-')}.json`;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},500)};
$('copy').onclick=async()=>{try{await navigator.clipboard.writeText(payload());$('saved').textContent='скопировано'}catch(e){$('saved').textContent='копирование недоступно — скачайте JSON'}};
$('imp').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{const j=JSON.parse(await f.text());S.votes=Object.assign(S.votes,j.votes||{});save();render()}catch(err){alert('Не JSON голосов')}};
if(D.kind==='text')$('mockbtn').hidden=true;applyUI();render()})();
</script></body></html>
"""


# ================================================================ подсчёт голосов

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, max(0.0, c - h), min(1.0, c + h))


def bradley_terry(games, iters=200):
    """games: [(i, j, score_i)] score 1 / 0 / 0.5. MM-алгоритм Hunter (2004) + слабый априор (0,5 победы против
    виртуального среднего). Возвращает {модель: рейтинг в шкале Эло (среднее геометрическое = 1000)}."""
    items = sorted({g[0] for g in games} | {g[1] for g in games})
    w = {i: 0.5 for i in items}
    n = {i: {} for i in items}
    for i, j, s in games:
        w[i] += s
        w[j] += 1 - s
        n[i][j] = n[i].get(j, 0) + 1
        n[j][i] = n[j].get(i, 0) + 1
    p = {i: 1.0 for i in items}
    for _ in range(iters):
        newp = {}
        for i in items:
            den = sum(c / (p[i] + p[j]) for j, c in n[i].items()) + 1 / (p[i] + 1.0)
            newp[i] = w[i] / den
        g = math.exp(sum(math.log(v) for v in newp.values()) / len(newp))
        p = {i: v / g for i, v in newp.items()}
    return {i: round(1000 + 400 * math.log10(p[i]), 1) for i in items}


def tally(votes_files, key):
    K = json.loads(Path(key).read_text(encoding="utf-8"))
    res = {"voters": [], "questions": {}, "consistency": None, "position_A_share": {}, "gold": None, "both_bad": {}}
    allv = []
    for f in votes_files:
        V = json.loads(Path(f).read_text(encoding="utf-8"))
        res["voters"].append(V.get("voter") or Path(f).stem)
        for pid, v in (V.get("votes") or {}).items():
            if pid in K["pairs"]:
                allv.append((V.get("voter"), pid, v))
    for q in K.get("questions") or ("slot", "natural"):
        games, per_test, posA, nonTie = [], {}, 0, 0
        for voter, pid, v in allv:
            kp = K["pairs"][pid]
            if kp.get("gold") or kp.get("repeat_of") or kp.get("identical") or q not in v:
                continue
            o = v[q]
            a, b = kp["A"]["model"], kp["B"]["model"]
            t = kp.get("test") or kp["group"]
            if o == "0":
                for m in (a, b):
                    res["both_bad"][m] = res["both_bad"].get(m, 0) + 1
                continue
            s = 1.0 if o == "A" else 0.0 if o == "B" else 0.5
            games.append((a, b, s))
            per_test.setdefault(t, []).append((a, b, s))
            if o in ("A", "B"):
                nonTie += 1
                posA += o == "A"
        out = {"overall_bt": bradley_terry(games) if games else {}, "tests": {}}
        for t, gs in per_test.items():
            wins = {}
            for a, b, s in gs:
                for m, sc in ((a, s), (b, 1 - s)):
                    k, n = wins.get(m, (0.0, 0))
                    wins[m] = (k + sc, n + 1)
            out["tests"][t] = {"bt": bradley_terry(gs),
                               "win_rate": {m: [round(x, 3) for x in wilson(k, n)] + [n] for m, (k, n) in wins.items()}}
        res["questions"][q] = out
        res["position_A_share"][q] = round(posA / nonTie, 3) if nonTie else None
    same, tot = 0, 0
    byp = {(vo, pid): v for vo, pid, v in allv}
    for vo, pid, v in allv:
        r = K["pairs"][pid].get("repeat_of")
        if r and (vo, r) in byp:
            o1, o2 = byp[(vo, r)].get("slot"), v.get("slot")
            flip = {"A": "B", "B": "A"}.get(o2, o2)
            tot += 1
            same += o1 == flip
    res["consistency"] = {"same": same, "total": tot, "share": round(same / tot, 3) if tot else None}
    g_ok, g_n = 0, 0
    for vo, pid, v in allv:
        gd = K["pairs"][pid].get("gold")
        if gd and v.get("slot"):
            g_n += 1
            g_ok += v["slot"] == gd
    res["gold"] = {"correct": g_ok, "total": g_n}
    idn = [v.get("slot") for vo, pid, v in allv if K["pairs"][pid].get("identical") and v.get("slot")]
    res["identical"] = {"tie_or_both_bad": sum(o in ("=", "0") for o in idn), "total": len(idn)}
    if K.get("kind") == "text":
        sel: dict = {}
        for vo, pid, v in allv:
            kp = K["pairs"][pid]
            if kp.get("gold") or kp.get("repeat_of") or kp.get("identical"):
                continue
            wins = sel.setdefault(kp["group"], {kp["A"]["model"]: 0, kp["B"]["model"]: 0})
            wins.setdefault(kp["A"]["model"], 0)
            wins.setdefault(kp["B"]["model"], 0)
            if v.get("slot") in ("A", "B"):
                wins[kp[v["slot"]]["model"]] += 1
        res["selection"] = {g: dict(sorted(w.items())) for g, w in sorted(sel.items())}
    return res


def tally_md(r):
    L = [f"# Итоги голосования стенда · голосующие: {', '.join(map(str, r['voters']))}", ""]
    for q, out in r["questions"].items():
        L += [f"## Вопрос `{q}`", "", "| Тест | Модель | Доля побед | 95 % ДИ (Уилсон) | Пар | Брэдли–Терри |", "|---|---|---|---|---|---|"]
        for t, d in sorted(out["tests"].items()):
            for m, (p, lo, hi, n) in sorted(d["win_rate"].items(), key=lambda x: -x[1][0]):
                L.append(f"| {t} | `{m}` | {p:.2f} | {lo:.2f}–{hi:.2f} | {n} | {d['bt'].get(m)} |")
        L += ["", f"Сквозной рейтинг Брэдли–Терри: " + ", ".join(f"`{m}` {v}" for m, v in sorted(out["overall_bt"].items(), key=lambda x: -x[1])), ""]
    L += [f"- Доля выборов левой картинки (A) без ничьих: {r['position_A_share']} (норма ≈ 0,5).",
          f"- Согласованность повторов (та же пара, стороны переставлены): {r['consistency']}.",
          f"- Контрольные пары (размытая копия должна проиграть): {r['gold']}.",
          f"- Одинаковая картинка с обеих сторон (ожидается «равно»/«оба не годятся»): {r.get('identical')}.",
          f"- «Оба не годятся» по моделям: {r['both_bad']}."]
    if r.get("selection"):
        L += ["", "## Победы вариантов по слотам (для copydeck.py apply-selection)", ""]
        L += [f"- `{g}`: " + ", ".join(f"{lab} — {n}" for lab, n in w.items()) for g, w in r["selection"].items()]
    return "\n".join(L) + "\n"


def cmd_tally(a):
    r = tally(a.votes, a.key)
    md = tally_md(r)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
        Path(a.out).with_suffix(".json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.selection:
        if "selection" not in r:
            print("--selection — только для текстовой страницы (page --text)", file=sys.stderr)
            return 2
        import yaml
        Path(a.selection).write_text("# победы меток по слоту — copydeck.py apply-selection --votes (method human-pairwise)\n"
                                     + yaml.safe_dump(r["selection"], allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(md)
    return 0


# ================================================================ мини-стенд новой модели

def cmd_ministand(a):
    cfg = load_yaml(a.tasks)
    import polza_catalog as pcat
    import prompt_compile as pc
    snap, dialects, catalog = pcat.Snapshot(), pc.load_dialects(), pc.load_catalog()
    if a.model not in snap.by_id:
        print(f"{a.model} нет в снимке каталога — сначала polza_catalog.py snapshot", file=sys.stderr)
        return 2
    params = json.loads(a.params) if a.params else {}
    out = Path(a.out) if a.out else jobs_dir(a) / f"E-MS-{slug(a.model)}.jsonl"
    rows, total = [], 0.0
    for tid, t in cfg["tasks"].items():
        if not t.get("reg") or t.get("pipeline"):     # задачу проверяет постобработка или видео, не генерация
            continue
        prompts = []                                   # (диалект, промт, входные картинки)
        lit = {"S08": "cyr_a_en", "S13": "lat_a_en", "S14": "edit_wall"}.get(tid)
        if lit:
            prompts.append(("literal", cfg["literals"][lit], [t["source"]] if t.get("source") else []))
        elif t.get("prompts"):
            prompts += [("literal", x, []) for x in t["prompts"]]
        elif t.get("brief") and t["brief"] != "literal":
            spec = json.loads((STAND / t["brief"]).read_text(encoding="utf-8"))
            r = pc.compile_prompt(spec, a.model, None, dialects, catalog)
            if r["errors"]:
                print(f"{tid}: пропуск ({r['errors'][0]})", file=sys.stderr)
                continue
            refs = [x["src"] for x in spec.get("references", []) if x.get("role") in ("product", "style", "subject")]
            pre = cfg["literals"]["product_prefix"].strip() + "\n" if tid == "S03" else ""
            prompts.append((r["dialect"], pre + r["prompt"], refs))
        else:
            print(f"{tid}: пропуск (нет брифа или нужен вход из другого теста)", file=sys.stderr)
            continue
        m = snap.by_id[a.model]
        mpar = m.get("parameters") or {}
        for k, (dialect, prompt, imgs) in enumerate(prompts, 1):
            inp = {"prompt": prompt, **{kk: v for kk, v in params.items() if kk in mpar}}
            if "aspect_ratio" in mpar and "aspect_ratio" not in inp:
                inp["aspect_ratio"] = "16:9" if "16:9" in (mpar["aspect_ratio"].get("values") or []) else (mpar["aspect_ratio"].get("values") or ["1:1"])[0]
            if imgs:
                if "images" not in mpar:
                    print(f"{tid}: пропуск (модель без images)", file=sys.stderr)
                    continue
                inp["images"] = list(imgs)                      # путь — как в рецепте: его разбирает polza.py
                for pth in imgs:
                    if input_missing(pth, out.parent):
                        print(f"ministand/{tid}: входа нет в скилле — {pth}")
            est = pcat.estimate(m, inp, providers=snap.providers.get(a.model))
            total += est.get("rub") or 0
            rows.append({"model": a.model, "input": inp, "tag": f"MS-{slug(a.model)}-{tid}-{k}", **agent_field(a), "variant": 1,
                         "max_rub": math.ceil((est.get("rub") or 0) * 1.25 * 10) / 10 or None,
                         "meta": {"test": "ministand", "task": tid, "code": t["code"], "dialect": dialect, "expect": t.get("expect"),
                                  "brief": t.get("brief"), "source": t.get("source"), "target": t.get("target"),
                                  "target_hex": t.get("target_hex"),
                                  "compare_with": f"результаты стенда по {tid} (тот же бриф, те же метрики и голоса)"}})
    jl_write(out, rows)
    print(f"мини-стенд: {len(rows)} заданий, ≈ {total:.2f} ₽ → {out}")
    return 0


# ================================================================ selftest

def cmd_selftest(a):
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(("OK   " if cond else "FAIL ") + name)
    exp = ["Весенняя распродажа", "Скидки до −30 % на всю мебель", "Подробнее"]
    check("дословно (с латинскими двойниками — нормализуются)", text_check(exp, "Becенняя pаспродажа\nСкидки до -30 % на всю мебель\nПодробнее")["pass"])
    r = text_check(exp, "ВЕСЕNNЯЯ РАСПРОДАЖА Скидки до 30% на мебель Подробнее Sale")
    check("латинский недвойник N пойман", r["fake_latin"] == ["ВЕСЕNNЯЯ"])
    check("лишнее слово Sale поймано", "Sale" in r["extra_words"])
    check("строка 2 не дословна", not r["lines"][1]["exact_ci"])
    r = text_check(["Съешь же ещё этих мягких французских булок"], "Съешь же еще этих мягких французских булок")
    check("потеря ё отмечена", r["lines"][0]["yo_lost"] and not r["lines"][0]["exact"])
    p, lo, hi = wilson(14, 20)
    check(f"Уилсон 14/20 = {p:.2f} [{lo:.3f}; {hi:.3f}] ≈ [0,481; 0,855]", abs(lo - 0.481) < 0.002 and abs(hi - 0.855) < 0.002)
    g = [("x", "y", 1)] * 8 + [("x", "y", 0)] * 2 + [("y", "z", 1)] * 8 + [("y", "z", 0)] * 2
    bt = bradley_terry(g)
    check(f"Брэдли–Терри порядок x > y > z: {bt}", bt["x"] > bt["y"] > bt["z"])
    import numpy as np
    check("ΔE2000 эталон Шармы (пара 1) = 2,0425", abs(float(de2000(np.array([50.0, 2.6772, -79.7751]), np.array([50.0, 0.0, -82.7485]))) - 2.0425) < 1e-3)
    # текстовые карточки: лист export-variants → страница слепых пар → голоса → победы меток для apply-selection
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="stand_text_"))
    try:
        sheet = ("# Слепой выбор вариантов\n\n## home/hero/h1 · headline\nКонтекст: что предлагаем\n\n"
                 "- **A**: Ремонт квартир под ключ за 45 дней\n- **B**: Отремонтируем квартиру под ключ\n"
                 "- **C**: Квартира под ключ — с гарантией 3 года\n\nВыбор: ___\n\n## home/hero/cta · cta-label\n\n"
                 "- **A**: Позвать замерщика\n\nВыбор: ___\n")
        (tmp / "sheet.md").write_text(sheet, encoding="utf-8")
        (tmp / "key.yaml").write_text("home/hero/h1: {A: v2, B: v1, C: v3}\n", encoding="utf-8")
        slots = parse_variants_sheet(sheet)
        check("текст: лист export-variants разобран (слот с одним вариантом — не на странице)",
              len(slots) == 1 and [lab for lab, _ in slots[0]["variants"]] == ["A", "B", "C"])
        a = argparse.Namespace(text=str(tmp / "sheet.md"), text_key=str(tmp / "key.yaml"), out=str(tmp / "page"), repeat=0.5,
                               seed=3, results=None)
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_page(a)
        html_ = (tmp / "page" / "index.html").read_text(encoding="utf-8")
        K = json.loads((tmp / "page.key.json").read_text(encoding="utf-8"))
        main_pairs = [kp for kp in K["pairs"].values() if not (kp.get("repeat_of") or kp.get("identical") or kp.get("gold"))]
        check("текст: 3 варианта → 3 пары, повторы со сменой сторон, одинаковая пара; ключ — вне папки страницы",
              len(main_pairs) == 3 and any(kp.get("repeat_of") for kp in K["pairs"].values())
              and any(kp.get("identical") for kp in K["pairs"].values()) and not (tmp / "page" / "page.key.json").exists())
        check("текст: карточки текста на странице, id вариантов и метки — только в ключе",
              '"kind": "text"' in html_ and "Отремонтируем квартиру" in html_ and '"v2"' not in html_
              and {kp["A"].get("variant") for kp in main_pairs} <= {"v1", "v2", "v3"})
        votes = {}
        for pid, kp in K["pairs"].items():
            if kp.get("identical"):
                votes[pid] = {"slot": "="}
                continue
            pref = sorted((kp["A"]["model"], kp["B"]["model"]), key=lambda m: {"C": 0, "A": 1, "B": 2}[m])[0]
            votes[pid] = {"slot": "A" if kp["A"]["model"] == pref else "B"}
        (tmp / "votes.json").write_text(json.dumps({"voter": "заказчик", "votes": votes}), encoding="utf-8")
        a = argparse.Namespace(votes=[str(tmp / "votes.json")], key=str(tmp / "page.key.json"), out=None,
                               selection=str(tmp / "selection.yaml"))
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_tally(a)
        import yaml
        sel = yaml.safe_load((tmp / "selection.yaml").read_text(encoding="utf-8"))
        check(f"текст: победы меток по слоту для apply-selection — {sel}", sel == {"home/hero/h1": {"A": 1, "B": 0, "C": 2}})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # картинки: паспорта polza.py вне базы → collect → страница пар между вариантами спецификации; папка кадров без паспортов
    from PIL import Image
    tmp = Path(tempfile.mkdtemp(prefix="stand_img_"))
    try:
        day = tmp / "out" / "pilot" / "day"
        day.mkdir(parents=True)
        for n, (model, variant) in enumerate([("m/a", 1), ("m/a", 2), ("m/b", 1)]):
            f = day / f"hero__{slug(model)}__g{n}.png"
            Image.new("RGB", (64, 36), (60 + 60 * n, 90, 140)).save(f)
            pas = {"schema": "polza-passport/1", "job": {"tag": "hero", "agent": "pilot", "variant": variant, "model": model,
                                                         "meta": {"spec": "hero-16x9", "dialect": "sections"}},
                   "files": [{"path": str(f), "bytes": f.stat().st_size, "media": {"width": 64, "height": 36}}]}
            (day / f"{f.stem}.passport.json").write_text(json.dumps(pas), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = cmd_collect(argparse.Namespace(root=str(tmp / "out"), agent=None, out=str(tmp / "results.jsonl")))
            cmd_collect(argparse.Namespace(root=str(tmp / "out"), agent="другой", out=str(tmp / "none.jsonl")))
        rows = jl_read(tmp / "results.jsonl")
        check("картинки: collect по паспортам вне базы — путь паспорта от корня выходов; --agent — только его задания",
              rc == 0 and len(rows) == 3 and all(r["passport"].startswith("pilot/day/") for r in rows)
              and jl_read(tmp / "none.jsonl") == [])
        page_args = dict(text=None, text_key=None, tests=None, repeat=0.1, seed=3)
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_page(argparse.Namespace(results=str(tmp / "out"), out=str(tmp / "vote"), **page_args))
        K = json.loads((tmp / "vote.key.json").read_text(encoding="utf-8"))
        main_pairs = [kp for kp in K["pairs"].values() if not (kp.get("repeat_of") or kp.get("identical") or kp.get("gold"))]
        check("картинки: страница из выхода polza.py — 3 варианта спецификации → 3 пары, варианты одной модели — тоже в паре",
              len(main_pairs) == 3 and {kp["group"] for kp in main_pairs} == {"hero-16x9"}
              and {kp[s]["model"] for kp in main_pairs for s in "AB"} == {"m/a#1", "m/a#2", "m/b#1"}
              and (tmp / "vote" / "index.html").exists())
        frames = tmp / "frames" / "hero-3d"
        frames.mkdir(parents=True)
        for n in range(3):
            Image.new("RGB", (48, 48), (40 + 70 * n, 120, 90)).save(frames / f"kadr-{n + 1}.png")
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_page(argparse.Namespace(results=str(tmp / "frames"), out=str(tmp / "vote3d"), **page_args))
        K = json.loads((tmp / "vote3d.key.json").read_text(encoding="utf-8"))
        main_pairs = [kp for kp in K["pairs"].values() if not (kp.get("repeat_of") or kp.get("identical") or kp.get("gold"))]
        check("картинки: папка кадров без паспортов — группа по подпапке, вариант — имя файла",
              len(main_pairs) == 3 and {kp["group"] for kp in main_pairs} == {"hero-3d"}
              and {kp[s]["model"] for kp in main_pairs for s in "AB"} == {"kadr-1", "kadr-2", "kadr-3"})
        # кодирование картинок страницы: без ключей — JPEG с уменьшением; --maxside 0 --lossless — пиксели исходника
        detail = tmp / "detail" / "kadr"
        detail.mkdir(parents=True)
        cells = (np.indices((64, 96)).sum(0) % 2 * 255).astype("uint8")            # шахматка в 1 px — мелкая деталь
        for n in range(2):
            Image.fromarray(np.stack([cells, np.roll(cells, n, 1), 255 - cells], -1)).save(detail / f"kadr-{n + 1}.png")

        def page_files(out, *keys):
            with contextlib.redirect_stdout(io.StringIO()):
                rc = main(["page", str(tmp / "detail"), "--out", str(out), "--seed", "3", *keys])
            K = json.loads(Path(str(out) + ".key.json").read_text(encoding="utf-8"))
            return rc, K, [(out / iid, v["file"]) for iid, v in K["images"].items() if not v["degraded"]]

        def same(f, src):
            return np.array_equal(np.asarray(Image.open(f).convert("RGB")), np.asarray(Image.open(src).convert("RGB")))
        rc, K, fs = page_files(tmp / "p-default")
        check("страница: без ключей — JPEG, шахматка в 1 px пережата с потерями",
              rc == 0 and len(fs) == 2 and all(f.suffix == ".jpg" and not same(f, s) for f, s in fs)
              and K["encoding"] == {"maxside": 1600, "lossless": False})
        rc, K, fs = page_files(tmp / "p-small", "--maxside", "48")
        check("страница: --maxside 48 — наибольшая сторона картинок 48",
              rc == 0 and len(fs) == 2 and all(max(Image.open(f).size) == 48 for f, _ in fs))
        rc, K, fs = page_files(tmp / "p-lossless", "--maxside", "0", "--lossless")
        check("страница: --maxside 0 --lossless — PNG с размером и пикселями исходника, кодирование — в ключе страницы",
              rc == 0 and len(fs) == 2 and all(f.suffix == ".png" and same(f, s) for f, s in fs)
              and K["encoding"] == {"maxside": None, "lossless": True})
        soft = Image.new("RGBA", (8, 8), (10, 20, 30, 252))
        check("кодирование: почти непрозрачная картинка — JPEG, без потерь — PNG с той же альфой",
              _encode(soft)[1] == "jpg" and _encode(soft, 0, True)[1] == "png"
              and Image.open(io.BytesIO(_encode(soft, 0, True)[0])).getpixel((0, 0)) == (10, 20, 30, 252))
        with contextlib.redirect_stderr(io.StringIO()):
            rc = main(["page", str(tmp / "detail"), "--out", str(tmp / "p-bad"), "--maxside", "-5"])
        check("страница: отрицательный --maxside — ошибка вызова (код 2), страницы нет",
              rc == 2 and not (tmp / "p-bad").exists())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # задания: папка — ключом или $DDD_HOME/out/ai-media/stand, поле agent — только с ключа, пути входов — как в рецепте
    import types
    tmp = Path(tempfile.mkdtemp(prefix="stand_jobs_"))
    mods = {k: sys.modules.get(k) for k in ("polza_catalog", "prompt_compile")}
    home = os.environ.get(kbpaths.ENV_HOME)
    try:
        model = {"id": "m/a", "parameters": {"images": {}, "mask_url": {}, "aspect_ratio": {"values": ["16:9"]}}}
        snap = types.SimpleNamespace(by_id={"m/a": model}, providers={})     # каталог и компилятор — заглушки без сети
        sys.modules["polza_catalog"] = types.SimpleNamespace(Snapshot=lambda: snap, estimate=lambda *x, **k: {"rub": 2.0})
        sys.modules["prompt_compile"] = types.SimpleNamespace(load_dialects=dict, load_catalog=dict)
        recipe = {"compiler": "prompt_compile.py", "catalog_snapshot": "снимок", "provider_default": {"only": ["x"]},
                  "seeds": [1], "models": {"a-1k": {"model": "m/a"}}, "literals": {"edit_wall": "Перекрась стену в зелёный"},
                  "tasks": {"S08": {"code": "IMG-TEXT-CYR", "title": "надпись", "expect": ["Привет"]},
                            "S14": {"code": "IMG-EDIT", "title": "правка стены", "reg": True, "source": "inputs/scene.png"}},
                  "recipes": [{"test": "E-01", "file": "E-01-edit.jsonl", "judge": ["metric"], "success": "стена перекрашена",
                               "value": 1, "hypothesis": "правка по маске",
                               "jobs": [{"task": "S14", "prompt": "edit_wall", "use": ["a-1k"], "images": ["inputs/scene.png"],
                                         "mask": "/stand/inputs/mask.png"}]}],
                  "external": [{"test": "E-09", "file": "E-09.routerai.json", "model": "v/x", "prompt": "edit_wall",
                                "channel": "канал", "price_rub": 2.0, "price_source": "прайс", "docs": "документация",
                                "note": "заметка", "value": 1}]}
        (tmp / "tasks.yaml").write_text(yaml.safe_dump(recipe, allow_unicode=True), encoding="utf-8")
        base = ["--tasks", str(tmp / "tasks.yaml"), "--jobs-dir", str(tmp / "jobs")]

        def built():
            return [jl_read(tmp / "jobs" / "E-01-edit.jsonl")[0], jl_read(tmp / "jobs" / "E-MS-m-a.jsonl")[0],
                    json.loads((tmp / "jobs" / "E-09.routerai.json").read_text(encoding="utf-8"))]
        with contextlib.redirect_stdout(io.StringIO()):
            rc = main(base + ["build"]), main(base + ["ministand", "--model", "m/a"])
        job, ms, ext = built()
        check("задания: --jobs-dir — папка заданий build и ministand; без --agent поля agent нет",
              rc == (0, 0) and not any("agent" in j for j in (job, ms, ext)))
        check("задания: входные картинки и маска — как в рецепте, без пересчёта пути",
              job["input"]["images"] == ["inputs/scene.png"] and job["input"]["mask_url"] == "/stand/inputs/mask.png"
              and ms["input"]["images"] == ["inputs/scene.png"])
        with contextlib.redirect_stdout(io.StringIO()):
            main(base + ["build", "--agent", "стенд"]), main(base + ["ministand", "--model", "m/a", "--agent", "стенд"])
        check("задания: --agent — имя в поле agent заданий build, ministand и внешнего канала",
              all(j.get("agent") == "стенд" for j in built()))
        # модель рецепта вне снимка: строка отчёта с тестом и моделью, остальные группы собраны, код 1
        recipe["models"]["gone-1k"] = {"model": "m/gone"}
        recipe["recipes"].append({"test": "E-02", "file": "E-02-gone.jsonl", "judge": ["metric"], "success": "—", "value": 1,
                                  "hypothesis": "модель выбыла", "jobs": [{"task": "S08", "prompt": "edit_wall",
                                                                           "use": ["gone-1k", "a-1k"]}]})
        recipe["recipes"].append({"test": "E-03", "file": "E-03-text.jsonl", "judge": ["metric"], "success": "—", "value": 1,
                                  "hypothesis": "надпись", "jobs": [{"task": "S08", "prompt": "edit_wall", "use": ["a-1k"]}]})
        (tmp / "tasks.yaml").write_text(yaml.safe_dump(recipe, allow_unicode=True), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as said:
            rc = main(base + ["build"])
        said = said.getvalue()
        check("build: модель вне снимка — строка «ОШИБКА» с тестом и моделью, остальные группы собраны, код 1",
              rc == 1 and "ОШИБКА: E-02: модели m/gone" in said and len(jl_read(tmp / "jobs" / "E-02-gone.jsonl")) == 1
              and len(jl_read(tmp / "jobs" / "E-03-text.jsonl")) == 1 and len(jl_read(tmp / "jobs" / "E-01-edit.jsonl")) == 1)
        check("build: вход без файла от папки заданий — строка «входа нет в скилле», задание собрано",
              "E-01/S14: входа нет в скилле — inputs/scene.png" in said
              and "E-01/S14: входа нет в скилле — /stand/inputs/mask.png" in said)
        (tmp / "jobs" / "inputs").mkdir()
        Image.new("RGB", (64, 36), (200, 200, 200)).save(tmp / "jobs" / "inputs" / "scene.png")
        Image.new("RGB", (64, 36), (40, 120, 60)).save(tmp / "res.png")
        with contextlib.redirect_stdout(io.StringIO()) as said:
            main(base + ["build", "--only", "E-01"])
        jl_write(tmp / "results.jsonl", [{"test": "E-01", "task": "S14", "file": str(tmp / "res.png"),
                                          "meta": {"source": "inputs/scene.png", "target_rect": [0, 0, 32, 18]}}])
        with contextlib.redirect_stdout(io.StringIO()):
            main(base + ["metrics", str(tmp / "results.jsonl"), "--out", str(tmp / "metrics.jsonl")])
        m = jl_read(tmp / "metrics.jsonl")[0]["m"]
        check("путь входа от папки заданий: build находит inputs/scene.png, metrics читает тот же файл (edit_diff)",
              "входа нет в скилле — inputs/scene.png" not in said.getvalue() and "edit_diff" in m and "error" not in m)
        os.environ[kbpaths.ENV_HOME] = str(tmp / "home")
        check("задания: без --jobs-dir — $DDD_HOME/out/ai-media/stand, папка создаётся",
              jobs_dir(argparse.Namespace(jobs_dir=None)) == tmp / "home" / "out" / "ai-media" / "stand"
              and (tmp / "home" / "out" / "ai-media" / "stand").is_dir())
    finally:
        for k, v in mods.items():
            sys.modules.pop(k, None) if v is None else sys.modules.__setitem__(k, v)
        os.environ.pop(kbpaths.ENV_HOME, None) if home is None else os.environ.__setitem__(kbpaths.ENV_HOME, home)
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if ok else 1


# ================================================================ main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", default=str(TASKS))
    ap.add_argument("--jobs-dir", help="папка заданий стенда (по умолчанию $DDD_HOME/out/ai-media/stand)")
    agent_help = "имя в поле agent заданий (выходы и журнал затрат polza.py); без ключа поля нет"
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("--only"); b.add_argument("--agent", help=agent_help)
    e = sub.add_parser("estimate"); e.add_argument("--only")
    r = sub.add_parser("run"); r.add_argument("jobs"); r.add_argument("--live", action="store_true"); r.add_argument("--parallel", type=int, default=2)
    c = sub.add_parser("collect"); c.add_argument("--out", default="results.jsonl")
    c.add_argument("--root", default=os.environ.get("POLZA_OUT_ROOT") or str(kbpaths.out("ai-media", "_polza")),
                   help="корень выходов polza.py с паспортами (по умолчанию POLZA_OUT_ROOT или $DDD_HOME/out/ai-media/_polza)")
    c.add_argument("--agent", help="только задания этого агента (поле agent задания)")
    m = sub.add_parser("metrics"); m.add_argument("results"); m.add_argument("--transcripts"); m.add_argument("--out", default="metrics.jsonl")
    s = sub.add_parser("sheet"); s.add_argument("results"); s.add_argument("--out", required=True); s.add_argument("--blind", action="store_true")
    p = sub.add_parser("page"); p.add_argument("--out", required=True)
    p.add_argument("results", nargs="?", help="папка выходов polza.py, таблица collect (.jsonl) или папка картинок")
    p.add_argument("--tests", help="только эти группы: тесты стенда, спецификации или подпапки через запятую")
    p.add_argument("--text", help="лист copydeck.py export-variants: страница текстовых карточек")
    p.add_argument("--text-key", help="ключ меток export-variants (id вариантов — в ключ страницы)")
    p.add_argument("--repeat", type=float, default=0.1); p.add_argument("--seed", type=int, default=7)
    p.add_argument("--maxside", type=int, default=1600, help="наибольшая сторона картинок страницы; 0 — без уменьшения")
    p.add_argument("--lossless", action="store_true", help="картинки страницы — PNG, пиксели без потерь")
    t = sub.add_parser("tally"); t.add_argument("votes", nargs="+"); t.add_argument("--key", required=True); t.add_argument("--out")
    t.add_argument("--selection", help="текстовая страница: YAML побед меток по слоту для copydeck.py apply-selection --votes")
    ms = sub.add_parser("ministand"); ms.add_argument("--model", required=True); ms.add_argument("--params"); ms.add_argument("--vs"); ms.add_argument("--out")
    ms.add_argument("--agent", help=agent_help)
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    return {"build": cmd_build, "estimate": cmd_estimate, "run": cmd_run, "collect": cmd_collect, "metrics": cmd_metrics,
            "sheet": cmd_sheet, "page": cmd_page, "tally": cmd_tally, "ministand": cmd_ministand, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
