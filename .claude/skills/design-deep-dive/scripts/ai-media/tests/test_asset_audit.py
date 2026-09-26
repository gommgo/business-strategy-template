#!/usr/bin/env python3
"""Тесты asset_audit.py (агент K, волна 3, 23.09.2026). Без сети и платных вызовов.
Запуск: python3 99-raw/tools/tests/test_asset_audit.py [--ocr] [--keep] [-v]
  --ocr  — ещё и OCR кириллицы (venv-K, под heavy.lock; ≈ 10 с);  --keep — не удалять временную папку.
Материал: синтетика (numpy/Pillow), файлы базы — H/03 (правки), F/01 (CC0-фото), K/03 (13 роликов), G/01 (иконки)."""
import argparse, io, json, shutil, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
sys.path.insert(0, str(TOOLS.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("ai-media")
sys.path.insert(0, str(TOOLS))
import asset_audit as aa  # noqa: E402

R = []


def check(name, cond, info=""):
    R.append((name, bool(cond), info))


def audit(paths, out, **kw):
    ap = aa.build_parser()
    argv = ["audit", *map(str, paths), "--out", str(out), "--no-provenance"]
    for k, v in kw.items():
        flag = "--" + k.replace("_", "-")
        if v is True:
            argv.append(flag)
        elif isinstance(v, list):
            for x in v:
                argv += [flag, str(x)]
        elif v is not None:
            argv += [flag, str(v)]
    a = ap.parse_args(argv)
    return aa.audit_paths(a)


def codes(asset, levels=("warn", "needs_human", "fail")):
    return {d["code"] for d in asset["defects"] if d["level"] in levels}


def t_thresholds():
    doc = aa.load_thresholds()
    th = aa.Th(doc)
    missing = [k for k in aa.TH_KEYS_USED if k not in th.flat]
    nosrc = [k for k in aa.TH_KEYS_USED if k in th.flat and not th.src(k)]
    check("thresholds: все ключи кода есть в YAML", not missing, missing)
    check("thresholds: у каждого порога есть источник", not nosrc, nosrc)


def t_text():
    tv = aa.text_verdict
    check("текст: дословно → pass", tv(["Весенняя распродажа"], "Весенняя распродажа")["verdict"] == "pass")
    check("текст: латинские двойники нормализуются → pass", tv(["Весенняя распродажа"], "Bесенняя pаспродажа")["verdict"] == "pass")
    check("текст: однобуквенный двойник «K» в русской строке → pass", tv(["Подарки к Новому году"], "Подарки K Новому году")["verdict"] == "pass")
    r = tv(["Весенняя распродажа"], "Весення распродажа")
    check("текст: пропуск буквы → omission", "omission" in r["fail_classes"], r["fail_classes"])
    r = tv(["Весенняя распродажа"], "Весенняя распроодажа")
    check("текст: удвоение → doubling", "doubling" in r["fail_classes"], r["fail_classes"])
    r = tv(["ВЕСЕННЯЯ РАСПРОДАЖА"], "ВЕСЕNNЯЯ РАСПРОДАЖА")
    check("текст: латинский недвойник N → latin_substitute", "latin_substitute" in r["fail_classes"], r["fail_classes"])
    r = tv(["Жёлтый чайник"], "Желтый чайник")
    check("текст: ё → е → needs_human (не брак без человека)", r["verdict"] == "needs_human" and "yo_lost" in r["fail_classes"], r["verdict"])
    r = tv(["Подробнее"], "Подробнее Sale")
    check("текст: лишнее слово → extra_text", "extra_text" in r["fail_classes"], r["fail_classes"])
    r = tv(["Подробнее"], "Подробнее ARABICA", allowed=["ARABICA 100%"])
    check("текст: разрешённый текст (этикетка) не «лишний»", r["verdict"] == "pass", r["extra_text"])
    check("текст: висящая точка не «лишнее слово»", tv(["Хлеб и сыр"], "Хлеб и сыр.")["verdict"] == "pass")
    check("текст: GNED = 0 для дословного", tv(["Цена 2 490 ₽"], "Цена 2 490 ₽")["gned"] == 0.0)
    meta = [{"text": "Скидки до −30 %", "score_min": 0.97, "h_px": 40, "text_en": "CKngKn go -30 %"}]
    r = tv(["Скидки до −30 %"], "Скидки до −30 %", lines_meta=meta)
    check("текст: «латинский нюх» (g в английском чтении «до») → needs_human", r["verdict"] == "needs_human" and r["latin_suspect"], r["latin_suspect"])
    meta = [{"text": "Весення", "score_min": 0.95, "h_px": 40}]
    check("текст: уверенный пропуск в крупной строке → fail", tv(["Весенняя"], "Весення", lines_meta=meta)["verdict"] == "fail")
    meta = [{"text": "Весення", "score_min": 0.95, "h_px": 10}]
    check("текст: пропуск в мелкой строке (10 px) → needs_human", tv(["Весенняя"], "Весення", lines_meta=meta)["verdict"] == "needs_human")


def t_image_cutout_texture(tmp):
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    src = ROOT / "99-raw/experiments/F/01-materials/cc0/fish_hoek_beach__IMG_0019.jpg"
    base = Image.open(src).convert("RGB")
    base.thumbnail((1024, 1024))
    p0 = tmp / "calm.png"
    base.save(p0)
    im = ImageEnhance.Color(base).enhance(1.8)
    a = np.asarray(im).astype(np.float32)
    b = np.asarray(im.filter(ImageFilter.GaussianBlur(12))).astype(np.float32)
    ImageEnhance.Contrast(Image.fromarray(np.clip(a + 0.9 * (a - b), 0, 255).astype(np.uint8))).enhance(1.2).save(tmp / "loud.png")
    s = audit([p0, tmp / "loud.png"], tmp / "o_img", ocr="off")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    check("image: спокойное CC0-фото без fail", A["calm.png"]["verdict"] != "fail", codes(A["calm.png"]))
    check("image: «фильтр» → маркер IMG-M03 (цвет или HDR выше Q3 лидеров)", "IMG-M03" in A["loud.png"]["markers"], A["loud.png"]["markers"])
    check("image: панель для человека записана", bool(A["calm.png"].get("panel")))
    # вырез
    H = W = 400
    yy, xx = np.mgrid[0:H, 0:W]
    circ = ((yy - 200) ** 2 + (xx - 200) ** 2) < 120 ** 2
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = (200, 60, 40)
    rgba[..., 3] = (circ * 255).astype(np.uint8)
    Image.fromarray(rgba).save(tmp / "cut_ok.png")
    edge = ((yy - 200) ** 2 + (xx - 60) ** 2) < 120 ** 2
    rgba2 = rgba.copy()
    rgba2[..., 3] = (edge * 255).astype(np.uint8)
    Image.fromarray(rgba2).save(tmp / "cut_edge.png")
    chk = ((xx // 16 + yy // 16) % 2).astype(np.float32)
    fake = np.stack([200 + 40 * chk] * 3, -1).astype(np.uint8)
    fake[circ] = (200, 60, 40)
    Image.fromarray(fake).save(tmp / "cut_fake.png")
    Image.fromarray(fake).convert("RGB").save(tmp / "cut_opaque.png")
    s = audit([tmp / "cut_ok.png", tmp / "cut_edge.png"], tmp / "o_cut", ocr="off")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    check("cutout: чистая альфа — режим cutout, без fail", A["cut_ok.png"]["mode"] == "cutout" and A["cut_ok.png"]["verdict"] != "fail",
          (A["cut_ok.png"]["mode"], codes(A["cut_ok.png"])))
    check("cutout: объект у края → QA-ALPHA-MARGIN", "QA-ALPHA-MARGIN" in codes(A["cut_edge.png"]), codes(A["cut_edge.png"]))
    s = audit([tmp / "cut_fake.png"], tmp / "o_fake", ocr="off", mode="cutout")
    check("cutout: нарисованная шахматка → QA-ALPHA-FAKE (fail)", "QA-ALPHA-FAKE" in codes(s["assets"][0], ("fail",)), codes(s["assets"][0]))
    # текстура
    rng = np.random.default_rng(1)
    from scipy import ndimage as ndi
    tile = ndi.gaussian_filter(rng.random((256, 256)), 3, mode="wrap")
    tile = ((tile - tile.min()) / (tile.max() - tile.min()) * 200 + 20).astype(np.uint8)
    Image.fromarray(np.stack([tile] * 3, -1)).save(tmp / "tile_ok.png")
    grad = (tile.astype(np.float32) * 0.6 + np.linspace(0, 90, 256)[None, :]).clip(0, 255).astype(np.uint8)
    Image.fromarray(np.stack([grad] * 3, -1)).save(tmp / "tile_bad.png")
    s = audit([tmp / "tile_ok.png", tmp / "tile_bad.png"], tmp / "o_tile", ocr="off", mode="texture")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    check("texture: периодический тайл → бесшовно", "QA-TILE-SEAM" not in codes(A["tile_ok.png"]), A["tile_ok.png"]["checks"].get("tile"))
    check("texture: градиент поперёк → QA-TILE-SEAM fail", "QA-TILE-SEAM" in codes(A["tile_bad.png"], ("fail",)), A["tile_bad.png"]["checks"].get("tile"))


def t_edit(tmp):
    I = ROOT / "99-raw/phase5/inputs/H"
    C = ROOT / "99-raw/experiments/H/03-edit-check/cases"
    if not (C / "e_leak.png").exists():
        check("edit: нет кейсов H/03 — пропуск", True)
        return
    s = audit([C / "e_leak.png", C / "e_ideal.png"], tmp / "o_edit", ocr="off", orig=I / "product_1024.png", mask=I / "mask_product_white.png")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    check("edit: утечка-угол H/03 видна (QA-EDIT-LOCAL-SHIFT при --match-color)", "QA-EDIT-LOCAL-SHIFT" in codes(A["e_leak.png"]), codes(A["e_leak.png"]))
    check("edit: идеальное удаление без warn/fail", not codes(A["e_ideal.png"]), codes(A["e_ideal.png"]))
    check("edit: композит записан", (tmp / "o_edit" / "e_leak_edit" / "composite.png").exists())
    s = audit([C / "e_outpaint_regen.png", C / "e_outpaint_9x16.png"], tmp / "o_out", ocr="off", orig=I / "hero_16x9.png")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    check("outpaint: перерисованный исходник → QA-OUTPAINT-REGEN fail", "QA-OUTPAINT-REGEN" in codes(A["e_outpaint_regen.png"], ("fail",)))
    check("outpaint: честное расширение → pass", A["e_outpaint_9x16.png"]["verdict"] == "pass", codes(A["e_outpaint_9x16.png"]))
    s = audit([C / "e_modellike.png"], tmp / "o_nomask", ocr="off", orig=I / "product_1024.png")
    dm = s["assets"][0]["checks"].get("diff_mask") or {}
    check("edit без маски: маска из разницы построена, изменено 10–60 % кадра", 0.1 < dm.get("changed_frac", 0) < 0.6, dm.get("changed_frac"))


def t_video(tmp):
    K = ROOT / "99-raw/experiments/K/03-video-negatives/clips"
    if not (K / "c00_clean.mp4").exists():
        check("video: нет роликов K/03 — пропуск", True)
        return
    s = audit([K / "c00_clean.mp4", K / "c01_gap8.mp4", K / "c09_weak.mp4", K / "c10_h264_crf23.mp4", K / "c11_audio.mp4"], tmp / "o_vid",
              control=K / "c00_clean.mp4")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    check("video: чистая петля → pass", A["c00_clean.mp4"]["verdict"] == "pass", codes(A["c00_clean.mp4"]))
    check("video: петля не замкнулась → QA-LOOP-SEAM fail", "QA-LOOP-SEAM" in codes(A["c01_gap8.mp4"], ("fail",)))
    check("video: слабое движение к контролю → QA-LOOP-WEAK-MOTION", "QA-LOOP-WEAK-MOTION" in codes(A["c09_weak.mp4"], ("fail",)))
    check("video: H.264 тихой петли → шов needs_human (пульс ключевого кадра)", "QA-LOOP-SEAM" in codes(A["c10_h264_crf23.mp4"], ("needs_human",)),
          codes(A["c10_h264_crf23.mp4"]))
    check("video: звуковая дорожка → QA-VIDEO-AUDIO", "QA-VIDEO-AUDIO" in codes(A["c11_audio.mp4"]))
    # motion_keep (J): финал к мастеру-мезонину; H.264 CRF 23 движение сохраняет, CRF 38 «замораживает» рябь
    import subprocess
    low = tmp / "c00_h264_crf38.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(K / "c00_clean.mp4"), "-an", "-threads", "4", "-c:v", "libx264", "-crf", "38",
                    "-pix_fmt", "yuv420p", str(low)], check=True)
    s = audit([K / "c10_h264_crf23.mp4", low], tmp / "o_keep", master=K / "c00_clean.mp4", control=K / "c00_clean.mp4")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    k23 = A["c10_h264_crf23.mp4"]["checks"]["loop"].get("motion_keep")
    k38 = A["c00_h264_crf38.mp4"]["checks"]["loop"].get("motion_keep")
    check("video: motion_keep — CRF 23 без QA-ENCODE-MOTION, CRF 38 → warn", k23 is not None and k23 >= 0.75
          and "QA-ENCODE-MOTION" not in codes(A["c10_h264_crf23.mp4"]) and "QA-ENCODE-MOTION" in codes(A["c00_h264_crf38.mp4"], ("warn",)),
          (k23, k38))


def t_svg_series(tmp):
    ref = kbpaths.data("ai-media", "lucide-ref", "search.svg")
    naive = ROOT / "99-raw/experiments/G/01-llm-svg-icons/icons-naive/heart.svg"
    if aa.VENV_G.exists() and ref.exists():
        s = audit([ref, naive], tmp / "o_svg")
        A = {Path(x["file"]).name: x for x in s["assets"]}
        check("svg: иконка Lucide без fail", A["search.svg"]["verdict"] != "fail", codes(A["search.svg"]))
        check("svg: «наивная» иконка LLM → fail (цвет/шапка)", A["heart.svg"]["verdict"] == "fail", codes(A["heart.svg"]))
    cc0 = ROOT / "99-raw/experiments/F/01-materials/cc0"
    same = sorted(cc0.glob("autumn_park__*.jpg"))
    diff = [cc0 / "autumn_park__DSC_0088.jpg", cc0 / "comfy_cafe__DSC_6776.jpg", cc0 / "fish_hoek_beach__IMG_0016.jpg",
            cc0 / "piazza_san_marco__DSC07156.jpg"]
    if len(same) >= 3:
        s = audit(same, tmp / "o_ser1", ocr="off", mode="series")
        check("series: одна съёмка → не fail", s["series"]["verdict"] != "fail", s["series"]["metrics"])
        s = audit(diff, tmp / "o_ser2", ocr="off", mode="series")
        check("series: четыре локации → QA-SERIES-BREAK", any(d["code"] == "QA-SERIES-BREAK" for d in s["series"]["defects"]), s["series"]["metrics"])


def t_judge(tmp):
    rub = aa.load_rubric("hero-photo")
    b = aa.judge_body(rub, "pairwise", rub["vlm"]["pairwise_questions"], ["a.png", "b.png"], "google/gemini-3.1-flash-lite", "brief")
    check("judge: Gemini — structured output и reasoning", "response_format" in b and "reasoning" in b)
    b = aa.judge_body(rub, "defects", rub["vlm"]["defect_questions"], ["a.png"], "qwen/qwen3.5-9b", None)
    check("judge: qwen3.5-9b — без response_format/temperature, формат словами", "response_format" not in b and "temperature" not in b
          and "Reply with JSON only" in b["messages"][1]["content"][0]["text"])
    norm, probs = aa.normalize_answer({"defects": [{"code": "IMG-M03", "present": "yes", "where": "", "severity": "major"}]}, "defects")
    check("judge: «есть» без «где» → unsure", norm["defects"][0]["present"] == "unsure" and probs)
    sch = json.loads(aa.JUDGE_SCHEMA.read_text(encoding="utf-8"))
    errs = aa.mini_validate({"answers": [{"id": "q1"}]}, sch["$defs"]["checklist_answer"])
    check("judge: схема ловит пропущенное поле", any("answer" in e for e in errs), errs)
    # попарные задания: повтор со сменой сторон
    items = tmp / "pairs.jsonl"
    items.write_text("".join(json.dumps({"pair": f"p{i}", "a": "x.png", "b": "y.png", "brief_text": "b"}) + "\n" for i in range(10)), encoding="utf-8")
    ap = aa.build_parser()
    a = ap.parse_args(["judge-jobs", "--rubric", "hero-photo", "--items", str(items), "--mode", "pairwise", "--repeat", "1", "--out",
                       str(tmp / "J.polza-chat.json")])
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        aa.cmd_judge_jobs(a)
    keys = json.loads((tmp / "J.keys.json").read_text(encoding="utf-8"))
    by = {}
    for v in keys.values():
        by.setdefault(v["pair"], []).append(v["swapped"])
    check("judge: повтор пары — всегда с переставленными сторонами", all(len(x) == 2 and x[0] != x[1] for x in by.values()), by)
    # согласие: судья = заказчик на 20 из 25 пар
    K = {"pairs": {f"p{i:03d}": {"A": {"files": [f"a{i}.png"]}, "B": {"files": [f"b{i}.png"]}} for i in range(25)}}
    (tmp / "page.key.json").write_text(json.dumps(K), encoding="utf-8")
    votes = {"votes": {f"p{i:03d}": {"slot": "A"} for i in range(25)}}
    (tmp / "votes.json").write_text(json.dumps(votes), encoding="utf-8")
    ans = [{"mode": "pairwise", "pair": f"p{i:03d}", "run": 1, "A": f"a{i}.png", "B": f"b{i}.png", "orig_a": f"a{i}.png", "orig_b": f"b{i}.png",
            "answers": {"slot": "A" if i < 20 else "B"}} for i in range(25)]
    (tmp / "ans.jsonl").write_text("".join(json.dumps(x) + "\n" for x in ans), encoding="utf-8")
    a = ap.parse_args(["agree", "--answers", str(tmp / "ans.jsonl"), "--votes", str(tmp / "votes.json"), "--key", str(tmp / "page.key.json"),
                       "--out", str(tmp / "agree.json")])
    with contextlib.redirect_stdout(io.StringIO()):
        aa.cmd_agree(a)
    rep = json.loads((tmp / "agree.json").read_text(encoding="utf-8"))
    ag = rep.get("pairwise", {}).get("slot", {})
    check("agree: 20/25 = 0,8, Уилсон и решение посчитаны", ag.get("agree") == 0.8 and ag.get("n") == 25 and ag.get("decision"), ag)


def t_stand_page(tmp):
    """K-01 из страницы голосования: судья видит те же перекодированные файлы, что заказчик; согласие — по исходникам."""
    import contextlib
    from PIL import Image
    sr = aa.mod("stand_run")
    rank = {"m1": 0, "m2": 1, "m3": 2}                  # «заказчик» и «судья» предпочитают m1 > m2 > m3
    items = []
    for m, col in (("m1", (200, 80, 60)), ("m2", (60, 120, 200)), ("m3", (90, 160, 90))):
        p = tmp / f"{m}.png"
        Image.new("RGB", (900, 600), col).save(p)
        items.append({"group": "T/1/a", "model": m, "files": [str(p)], "test": "T", "brief": "b"})
    page = tmp / "page"
    with contextlib.redirect_stdout(io.StringIO()):
        sr.build_page(items, page, repeat=0.1, seed=3)
    K = json.loads((tmp / "page.key.json").read_text(encoding="utf-8"))
    ap = aa.build_parser()
    out = tmp / "jobs" / "S.polza-chat.json"
    out.parent.mkdir()
    a = ap.parse_args(["judge-jobs", "--rubric", "hero-photo", "--from-stand-page", str(page), "--mode", "pairwise", "--repeat", "0",
                       "--out", str(out)])
    with contextlib.redirect_stdout(io.StringIO()):
        aa.cmd_judge_jobs(a)
    jobs = json.loads(out.read_text(encoding="utf-8"))
    urls = [c["image_url"]["url"] for t in jobs for c in t["body"]["messages"][1]["content"] if c.get("type") == "image_url"]
    inside = all((out.parent / u).resolve().parent == (page / "img").resolve() for u in urls)
    check("stand page: судья видит файлы страницы (то же кодирование, что у заказчика)", urls and inside, urls[:2])
    keys = json.loads((tmp / "jobs" / "S.keys.json").read_text(encoding="utf-8"))
    check("stand page: только основные пары (без gold, повторов, «одинаковых»)", len(keys) == 3, len(keys))
    model_of = {str(f): m for m in rank for f in [tmp / f"{m}.png"]}
    votes = {}
    for pid, kp in K["pairs"].items():
        if kp.get("gold") or kp.get("identical") or kp.get("repeat_of"):
            continue
        votes[pid] = {"slot": "A" if rank[kp["A"]["model"]] < rank[kp["B"]["model"]] else "B"}
    (tmp / "votes_s.json").write_text(json.dumps({"votes": votes}), encoding="utf-8")
    ans = []
    for tag, k in keys.items():
        w = "A" if rank[model_of[k["A_orig"]]] < rank[model_of[k["B_orig"]]] else "B"
        ans.append({"mode": "pairwise", **k, "answers": {"slot": w}})
    (tmp / "ans_s.jsonl").write_text("".join(json.dumps(x) + "\n" for x in ans), encoding="utf-8")
    a = ap.parse_args(["agree", "--answers", str(tmp / "ans_s.jsonl"), "--votes", str(tmp / "votes_s.json"), "--key",
                       str(tmp / "page.key.json"), "--out", str(tmp / "agree_s.json")])
    with contextlib.redirect_stdout(io.StringIO()):
        aa.cmd_agree(a)
    ag = json.loads((tmp / "agree_s.json").read_text(encoding="utf-8")).get("pairwise", {}).get("slot", {})
    check("stand page: согласие считается по исходникам сторон (3/3)", ag.get("agree") == 1.0 and ag.get("n") == 3, ag)
    # пары вне страницы: --same-encoding кодирует обе стороны одинаково
    big = tmp / "big.png"
    Image.new("RGB", (2400, 1600), (120, 110, 100)).save(big)
    items = tmp / "pairs_enc.jsonl"
    items.write_text(json.dumps({"pair": "q1", "a": str(big), "b": str(tmp / "m2.png")}) + "\n", encoding="utf-8")
    a = ap.parse_args(["judge-jobs", "--rubric", "hero-photo", "--items", str(items), "--mode", "pairwise", "--repeat", "0",
                       "--same-encoding", str(tmp / "enc"), "--out", str(tmp / "jobs" / "E.polza-chat.json")])
    with contextlib.redirect_stdout(io.StringIO()):
        aa.cmd_judge_jobs(a)
    k = next(iter(json.loads((tmp / "jobs" / "E.keys.json").read_text(encoding="utf-8")).values()))
    shown = [Path(k["A"]), Path(k["B"])]
    ok = all(p.parent == tmp / "enc" and p.suffix == ".jpg" and max(Image.open(p).size) <= 1600 for p in shown)
    check("same-encoding: обе стороны → JPEG ≤ 1600 px, исходники в ключе", ok and {k["A_orig"], k["B_orig"]} == {str(big), str(tmp / "m2.png")},
          (k["A"], k["B"]))


def t_provenance(tmp):
    """Провенанс через provenance_check.py агента L (+ --corners): надпись в углу → QA-PROV-VISIBLE-MARK (needs_human)."""
    if not (aa.TOOLS / "provenance_check.py").exists():
        check("provenance: нет provenance_check.py (L) — пропуск", True)
        return
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    H, W = 720, 1280
    yy, xx = np.mgrid[0:H, 0:W]
    g = np.stack([40 + 60 * xx / W, 50 + 40 * yy / H, 90 + 50 * (xx + yy) / (W + H)], -1).astype(np.uint8)
    Image.fromarray(g).save(tmp / "p_clean.png")
    im = Image.fromarray(g.copy())
    ImageDraw.Draw(im).text((W - 250, H - 40), "Generated with AI", fill=(235, 235, 235),
                            font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22))
    im.save(tmp / "p_marked.png")
    ap = aa.build_parser()
    a = ap.parse_args(["audit", str(tmp / "p_clean.png"), str(tmp / "p_marked.png"), "--out", str(tmp / "o_prov"), "--ocr", "off"])
    s = aa.audit_paths(a)
    A = {Path(x["file"]).name: x for x in s["assets"]}
    pm = A["p_marked.png"]["checks"].get("provenance") or {}
    check("provenance: надпись в углу → QA-PROV-VISIBLE-MARK + лист углов",
          "QA-PROV-VISIBLE-MARK" in codes(A["p_marked.png"], ("needs_human",)) and (tmp / "o_prov" / "p_marked_corners.jpg").exists(), pm)
    check("provenance: чистый кадр без подозрения на метку", "QA-PROV-VISIBLE-MARK" not in codes(A["p_clean.png"]),
          (A["p_clean.png"]["checks"].get("provenance") or {}).get("visible_suspect"))
    # ворота L 04 §5 п. 8: файл ИИ-ассета (есть паспорт) для страницы без машиночитаемой метки → QA-PROV-NO-MARK; после stamp — нет
    import subprocess
    shutil.copy(tmp / "p_clean.png", tmp / "p_web.png")
    subprocess.run([sys.executable, str(aa.TOOLS / "provenance_check.py"), "stamp", str(tmp / "p_web.png"), str(tmp / "p_web_st.png"),
                    "--dst", "trained"], capture_output=True, text=True, timeout=120)
    for n in ("p_web", "p_web_st"):
        (tmp / f"{n}.passport.json").write_text(json.dumps({"schema": "mp-passport/1", "model": "test/model",
                                                             "job": {"tag": "t", "meta": {"code": "IMG-BG-ABSTRACT"}},
                                                             "files": [{"path": f"{n}.png"}]}), encoding="utf-8")
    a = ap.parse_args(["audit", str(tmp / "p_web.png"), str(tmp / "p_web_st.png"), "--out", str(tmp / "o_prov2"), "--ocr", "off",
                       "--stage", "web"])
    A = {Path(x["file"]).name: x for x in aa.audit_paths(a)["assets"]}
    marks_st = ((A["p_web_st.png"]["checks"].get("provenance") or {}).get("summary") or {}).get("marks")
    check("provenance: ИИ-файл для страницы без метки → QA-PROV-NO-MARK; после stamp — нет",
          "QA-PROV-NO-MARK" in codes(A["p_web.png"], ("warn",)) and "QA-PROV-NO-MARK" not in codes(A["p_web_st.png"]), marks_st)


def t_ocr(tmp):
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    for name, text in (("ok.png", "Весенняя распродажа"), ("miss.png", "Весення распродажа")):
        im = Image.new("RGB", (760, 140), (245, 242, 236))
        ImageDraw.Draw(im).text((24, 40), text, font=f, fill=(20, 20, 20))
        im.save(tmp / name)
    s = audit([tmp / "ok.png", tmp / "miss.png"], tmp / "o_ocr", expect=["Весенняя распродажа"])
    A = {Path(x["file"]).name: x for x in s["assets"]}
    t_ok = (A["ok.png"]["checks"].get("text") or {}).get("verdict")
    t_miss = (A["miss.png"]["checks"].get("text") or {}).get("verdict")
    check("ocr: верная строка → pass", t_ok == "pass", A["ok.png"]["checks"].get("ocr"))
    tm = A["miss.png"]["checks"].get("text") or {}
    # OCR менее уверен на «не-словах» (0,87 < 0,9) → чаще needs_human, чем fail (K/01: пропуск 60 fail / 12 needs_human из 72);
    # главное — ошибка не проходит как pass и названа классом
    check("ocr: пропуск буквы → не pass, класс omission", t_miss in ("fail", "needs_human") and "omission" in tm.get("fail_classes", []), tm)


def run(keep=False, ocr=False, verbose=False):
    R.clear()
    tmp = Path(tempfile.mkdtemp(prefix="asset_audit_test_"))
    try:
        for t in (t_thresholds, t_text, lambda: t_image_cutout_texture(tmp), lambda: t_edit(tmp), lambda: t_video(tmp),
                  lambda: t_svg_series(tmp), lambda: t_judge(tmp), lambda: t_stand_page(tmp), lambda: t_provenance(tmp)) + \
                ((lambda: t_ocr(tmp),) if ocr else ()):
            try:
                t()
            except Exception as e:  # noqa: BLE001
                import traceback
                check(f"исключение в {getattr(t, '__name__', 'тесте')}", False, f"{type(e).__name__}: {e}")
                if verbose:
                    traceback.print_exc()
    finally:
        if not keep:
            shutil.rmtree(tmp, ignore_errors=True)
    ok = sum(1 for _, c, _ in R if c)
    for name, c, info in R:
        if verbose or not c:
            print(("OK   " if c else "FAIL ") + name + (f"  → {info}" if (not c and info) else ""))
    print(f"asset_audit tests: {ok}/{len(R)} OK" + (f" (папка {tmp})" if keep else ""))
    return 0 if ok == len(R) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ocr", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    sys.exit(run(a.keep, a.ocr, a.v))
