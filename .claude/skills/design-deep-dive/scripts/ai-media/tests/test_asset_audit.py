#!/usr/bin/env python3
"""Тесты asset_audit.py без сети и платных вызовов: пороги, сверка строк, проверки картинок, правок, видео, иконок и
серий на синтетике (Pillow, numpy, ffmpeg — входы строятся во временной папке), пакет судьи на заглушках ответов (пары,
рубрика, калибровочный набор, страница голосования), доверие по порогам группы judge; набор и эталон иконок, кодирование
без усечения глубины и резкость источника, подбор качества под бюджет веса, строки окружения вместо трассировки,
командная строка palette.py.
Запуск: python3 scripts/ai-media/tests/test_asset_audit.py [--ocr] [--keep] [-v]
  --ocr  — ещё и OCR кириллицы (под блокировкой heavy; ≈ 10 с);  --keep — не удалять временную папку.
Программы окружения, которых нет на машине (exiftool, avifenc, ssimulacra2), — пропуск с пометкой, не провал."""
import argparse, hashlib, io, json, re, shutil, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
sys.path.insert(0, str(TOOLS.parent / "lib"))  # scripts/lib: kbpaths
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
    r = tv(["Весенняя"], "Весення", lines_meta=meta)
    check("текст: пропуск в мелкой строке (10 px) → warn, не брак и не «покажи человеку»",
          r["verdict"] == "warn" and r["small_text"] == ["omission"] and not r["fail_classes"], (r["verdict"], r["small_text"]))
    meta = [{"text": "Весенняя распродажа", "score_min": 0.97, "h_px": 60}, {"text": "товары до конца месяца", "score_min": 0.93, "h_px": 36}]
    exp = ["Весенняя распродажа", "товаров до конца месяца"]
    r1 = tv(exp, "Весенняя распродажа\nтовары до конца месяца", lines_meta=meta)
    r2 = tv(exp, "Весенняя распродажа\nтовары до конца месяца", lines_meta=meta, h_scale=0.4)
    check("текст: высота букв — в масштабе распознавания: строка 36 px при уменьшении кадра до 0,4 — мелкая (warn), без него — нет",
          r1["verdict"] != "warn" and r2["verdict"] == "warn" and r2["min_line_h_px"] == 14.4, (r1["verdict"], r2["verdict"], r2["min_line_h_px"]))
    two = "Скидка 20 %\nСкидка 20 %"
    check("текст: две одинаковые ожидаемые надписи (повтор строки и суффикс {×2}) — чисто",
          tv(["Скидка 20 %", "Скидка 20 %"], two)["verdict"] == "pass" and tv(["Скидка 20 %{×2}"], two)["verdict"] == "pass"
          and not tv(["Скидка 20 %{×2}"], two)["extra_text"])
    r = tv(["Скидка 20 %"], two)
    check("текст: вторая надпись без заказа числа вхождений — extra_text", "extra_text" in r["fail_classes"], r["fail_classes"])
    r = tv(["Скидка 20 %{×2}"], "Скидка 20 %")
    check("текст: заказано два вхождения, на картинке одно — missing_line", "missing_line" in r["fail_classes"]
          and [L["found"] for L in r["lines"]] == [True, False], r["fail_classes"])


def calm_photo(size=(1024, 640), seed=3):
    """Спокойный синтетический «пейзаж»: небо, земля, пятно дерева, мягкий шум (цветность ниже Q3 лидеров)."""
    import numpy as np
    from PIL import Image
    from scipy import ndimage as ndi
    W, H = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = np.stack([150 + 30 * yy / H, 175 + 20 * yy / H, 200 + 10 * yy / H], -1)
    ground = np.stack([95 + 20 * xx / W, 105 + 10 * xx / W, 70 + 5 * xx / W], -1)
    img = np.where((yy > H * 0.55)[..., None], ground, sky)
    img = img + (ndi.gaussian_filter(np.random.default_rng(seed).normal(0, 1, (H, W)), 2) * 18)[..., None]
    tree = ((yy - H * 0.45) ** 2 / 90 ** 2 + (xx - W * 0.72) ** 2 / 70 ** 2) < 1
    img[tree] = img[tree] * 0.55 + np.array([60, 80, 40]) * 0.45
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def t_image_cutout_texture(tmp):
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    base = calm_photo()
    p0 = tmp / "calm.png"
    base.save(p0)
    im = ImageEnhance.Color(base).enhance(1.8)
    a = np.asarray(im).astype(np.float32)
    b = np.asarray(im.filter(ImageFilter.GaussianBlur(12))).astype(np.float32)
    ImageEnhance.Contrast(Image.fromarray(np.clip(a + 0.9 * (a - b), 0, 255).astype(np.uint8))).enhance(1.2).save(tmp / "loud.png")
    s = audit([p0, tmp / "loud.png"], tmp / "o_img", ocr="off")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    check("image: спокойный кадр без fail", A["calm.png"]["verdict"] != "fail", codes(A["calm.png"]))
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


def edit_scene(size=(512, 512), obj=True, seed=5):
    """Сцена для правки: небо, земля, мягкий шум и крупный предмет (эллипс ≈ 20 % кадра); obj=False — та же сцена без
    предмета: «идеальное удаление». Возвращает (кадр float32, маска предмета с запасом)."""
    import numpy as np
    from scipy import ndimage as ndi
    W, H = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = np.stack([150 + 30 * yy / H, 175 + 20 * yy / H, 200 + 10 * yy / H], -1)
    ground = np.stack([95 + 20 * xx / W, 105 + 10 * xx / W, 70 + 5 * xx / W], -1)
    img = np.where((yy > H * 0.6)[..., None], ground, sky)
    img = img + (ndi.gaussian_filter(np.random.default_rng(seed).normal(0, 1, (H, W)), 2) * 18)[..., None]
    r = ((yy - H * 0.5) / (H * 0.24)) ** 2 + ((xx - W * 0.55) / (W * 0.27)) ** 2
    if obj:
        img[r < 1] = img[r < 1] * 0.35 + np.array([170, 60, 40]) * 0.65
    return np.clip(img, 0, 255).astype(np.float32), r < 1.25


def t_edit(tmp):
    """Правка на месте и аутпейнт на синтетической сцене: утечка вне маски, идеальное удаление, перерисованный и честный
    аутпейнт, маска из разницы у безмасочной правки."""
    import numpy as np
    from PIL import Image
    from scipy import ndimage as ndi
    d = tmp / "edit"
    d.mkdir()
    src, mask = edit_scene()
    clean, _ = edit_scene(obj=False)

    def save(arr, name):
        Image.fromarray(np.clip(arr, 0, 255).round().astype(np.uint8)).save(d / name)
        return d / name
    orig = save(src, "scene.png")
    Image.fromarray((mask * 255).astype(np.uint8)).save(d / "mask_object_white.png")
    ideal = np.where(mask[..., None], clean, src)
    save(ideal, "e_ideal.png")
    leak = ideal.copy()
    leak[:200, :200] += np.array([7.0, 5.0, -7.0])             # угол вне маски сдвинут по цвету слабее порога утечки
    save(leak, "e_leak.png")
    s = audit([d / "e_leak.png", d / "e_ideal.png"], tmp / "o_edit", ocr="off", orig=orig, mask=d / "mask_object_white.png")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    check("edit: сдвиг цвета в углу вне маски виден (QA-EDIT-LOCAL-SHIFT или QA-EDIT-LEAK)",
          {"QA-EDIT-LOCAL-SHIFT", "QA-EDIT-LEAK"} & codes(A["e_leak.png"]), (codes(A["e_leak.png"]), A["e_leak.png"]["checks"].get("edit")))
    check("edit: идеальное удаление без warn/fail", not codes(A["e_ideal.png"]), codes(A["e_ideal.png"]))
    check("edit: композит записан", (tmp / "o_edit" / "e_leak_edit" / "composite.png").exists())
    # аутпейнт 16:9 → выше кадра: исходник в середине, сверху небо, снизу земля
    wide, _ = edit_scene((640, 360))
    yy = np.linspace(0, 1, 200, dtype=np.float32)[:, None, None]
    rng = np.random.default_rng(11)
    top = np.array([150.0, 175.0, 200.0]) * np.ones((200, 640, 1), np.float32) - 25 * (1 - yy) + rng.normal(0, 3, (200, 640, 1))
    bottom = np.array([100.0, 108.0, 72.0]) * np.ones((200, 640, 1), np.float32) - 20 * yy + rng.normal(0, 3, (200, 640, 1))
    save(wide, "wide.png")
    save(np.concatenate([top, wide, bottom]), "e_outpaint_tall.png")
    regen = np.stack([ndi.gaussian_filter(wide[..., c], 2.5) for c in range(3)], -1) + np.array([10.0, 0.0, -10.0])
    save(np.concatenate([top, regen, bottom]), "e_outpaint_regen.png")
    s = audit([d / "e_outpaint_regen.png", d / "e_outpaint_tall.png"], tmp / "o_out", ocr="off", orig=d / "wide.png")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    check("outpaint: перерисованный исходник → QA-OUTPAINT-REGEN fail", "QA-OUTPAINT-REGEN" in codes(A["e_outpaint_regen.png"], ("fail",)),
          A["e_outpaint_regen.png"]["checks"].get("outpaint"))
    check("outpaint: честное расширение → pass", A["e_outpaint_tall.png"]["verdict"] == "pass",
          (codes(A["e_outpaint_tall.png"]), A["e_outpaint_tall.png"]["checks"].get("outpaint")))
    # безмасочная правка «как у модели»: предмет убран, весь кадр слегка сдвинут и зашумлён
    save(ideal + np.random.default_rng(12).normal(0, 1.2, ideal.shape) + np.array([2.0, 1.0, 0.0]), "e_modellike.png")
    s = audit([d / "e_modellike.png"], tmp / "o_nomask", ocr="off", orig=orig)
    dm = s["assets"][0]["checks"].get("diff_mask") or {}
    check("edit без маски: маска из разницы построена, изменено 10–60 % кадра", 0.1 < dm.get("changed_frac", 0) < 0.6, dm.get("changed_frac"))


def loop_frames(n=48, h=180, w=320, amp=60.0, seed=1, gap=0.0, warp=None, level=120.0, blobs=60, sigma=9.0):
    """Синтетическая петля без движения кадра: пятна на своих местах «дышат» по синусу, пары пятен — в противофазе
    (средняя яркость кадра постоянна). gap — на сколько шагов стык длиннее обычного шага (0 — петля замкнута);
    warp(u) — неравномерная скорость по циклу."""
    import numpy as np
    from scipy import ndimage as ndi
    rng = np.random.default_rng(seed)
    base = ndi.gaussian_filter(rng.random((h, w)), 1.5)        # мелкая неподвижная фактура держит кадр на месте
    base = (base - base.mean()) / base.std() * 50 + level
    yy, xx = np.mgrid[0:h, 0:w]
    cy, cx = rng.random(blobs) * h, rng.random(blobs) * w
    ph = rng.random(blobs // 2) * 2 * np.pi
    ph = np.concatenate([ph, ph + np.pi])
    g = np.stack([np.exp(-((yy - y) ** 2 + (xx - x) ** 2) / (2 * sigma ** 2)) for y, x in zip(cy, cx)])
    u = [(warp(i / (n + gap)) if warp else i / (n + gap)) for i in range(n)]
    return np.clip(np.stack([base + amp * np.tensordot(np.sin(2 * np.pi * x + ph), g, axes=1) for x in u]), 0, 255).round().astype(np.uint8)


LOSSLESS = ("-c:v", "libx264", "-qp", "0", "-pix_fmt", "yuv444p")


def h264(crf):
    return ("-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p")


def write_clip(frames, path, fps=24, args=LOSSLESS, audio=False):
    """Кадры (n, h, w) uint8 → видеофайл через ffmpeg; по умолчанию — мезонин без потерь."""
    import subprocess
    h, w = frames.shape[1:3]
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-"]
    if audio:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=440", "-shortest", "-c:a", "aac"]
    subprocess.run(cmd + ["-threads", "2", *args, str(path)], input=frames.tobytes(), check=True)
    return path


def t_video(tmp):
    """Видео на синтетических клипах (кадры numpy → ffmpeg): шов по стадии файла, бюджет строки плана, разовый ролик,
    монтаж, событие-затемнение, почти неподвижные концы, повторы кадров и переменная частота, вспышки."""
    import subprocess
    import numpy as np
    if kbpaths.find("ffmpeg") is None:
        check("video: нет ffmpeg (install.sh --ffmpeg) — проверки видео не выполнены", False)
        return
    d = tmp / "clips"
    d.mkdir()
    s = loop_frames()
    clean = write_clip(s, d / "clean.mp4")
    write_clip(loop_frames(gap=8), d / "gap.mp4")
    write_clip(loop_frames(amp=12.0), d / "weak.mp4")
    write_clip(s, d / "audio.mp4", audio=True)
    A = {Path(x["file"]).name: x for x in audit([clean, d / "gap.mp4", d / "weak.mp4", d / "audio.mp4"], tmp / "o_vid",
                                                 control=clean)["assets"]}
    check("video: чистая петля → pass", A["clean.mp4"]["verdict"] == "pass", codes(A["clean.mp4"]))
    check("video: петля не замкнулась → QA-LOOP-SEAM fail", "QA-LOOP-SEAM" in codes(A["gap.mp4"], ("fail",)))
    check("video: слабое движение к контролю → QA-LOOP-WEAK-MOTION", "QA-LOOP-WEAK-MOTION" in codes(A["weak.mp4"], ("fail",)))
    check("video: звуковая дорожка → QA-VIDEO-AUDIO", "QA-VIDEO-AUDIO" in codes(A["audio.mp4"]))
    # шов по стадии файла: стык длиннее шага в 1,7 раза — брак у мезонина, норма у файла после кодирования
    th = aa.Th(aa.load_thresholds())
    between = loop_frames(gap=0.7)
    write_clip(between, d / "between.mp4")
    write_clip(between, d / "between_web.mp4", args=h264(14))
    A = {Path(x["file"]).name: x for x in audit([d / "between.mp4", d / "between_web.mp4"], tmp / "o_stage")["assets"]}
    sc = A["between_web.mp4"]["checks"]["loop"]["seam_check"]
    check("video: шов между порогами у мезонина → QA-LOOP-SEAM fail (порог мезонина)",
          "QA-LOOP-SEAM" in codes(A["between.mp4"], ("fail",)) and A["between.mp4"]["checks"]["loop"]["seam_check"]["stage"] == "mezzanine",
          A["between.mp4"]["checks"]["loop"]["seam_check"])
    check("video: тот же шов у сжатого файла — между порогами и не fail (порог после кодирования)",
          sc["stage"] == "encoded" and th("video.seam_local_max") < sc["value"] <= th("video.seam_encoded_max")
          and "QA-LOOP-SEAM" not in codes(A["between_web.mp4"]), sc)
    # тихая петля после H.264: пульс ключевого кадра → шов needs_human; motion_keep к мезонину
    q = loop_frames(amp=4.0)
    quiet = write_clip(q, d / "quiet.mp4")
    write_clip(q, d / "quiet_crf12.mp4", args=h264(12))
    write_clip(q, d / "quiet_crf30.mp4", args=h264(30))
    A = {Path(x["file"]).name: x for x in audit([d / "quiet_crf12.mp4", d / "quiet_crf30.mp4"], tmp / "o_keep", master=quiet)["assets"]}
    check("video: H.264 тихой петли → шов needs_human (пульс ключевого кадра)", "QA-LOOP-SEAM" in codes(A["quiet_crf12.mp4"], ("needs_human",)),
          codes(A["quiet_crf12.mp4"]))
    k12 = A["quiet_crf12.mp4"]["checks"]["loop"].get("motion_keep")
    k30 = A["quiet_crf30.mp4"]["checks"]["loop"].get("motion_keep")
    check("video: motion_keep — CRF 12 без QA-ENCODE-MOTION, CRF 30 → warn", k12 is not None and k12 >= th("video.motion_keep_min")
          and "QA-ENCODE-MOTION" not in codes(A["quiet_crf12.mp4"]) and "QA-ENCODE-MOTION" in codes(A["quiet_crf30.mp4"], ("warn",)),
          (k12, k30))
    # бюджет веса: строка плана ассетов раньше умолчания
    plan = tmp / "plan-home.yaml"
    plan.write_text("plan_version: 1\nstatus: draft\npage: {id: home}\nslots:\n"
                    "  - id: hero-loop\n    slot: hero-visual\n    variants:\n"
                    "      - {id: desktop, max_kb: 4}\n      - {id: mobile, max_kb: 100000}\n"
                    "  - id: about-photo\n    slot: photo\n    variants: [{id: default, max_kb: TODO}]\n", encoding="utf-8")
    kb = (d / "between_web.mp4").stat().st_size / 1024
    a1 = audit([d / "between_web.mp4"], tmp / "o_plan1", stage="web", plan=plan, slot="hero-loop")["assets"][0]
    a2 = audit([d / "between_web.mp4"], tmp / "o_plan2", stage="web", plan=plan, slot="hero-loop", variant="mobile")["assets"][0]
    a3 = audit([d / "between_web.mp4"], tmp / "o_plan3", stage="web")["assets"][0]
    bd = [x for x in a1["defects"] if x["code"] == "QA-BUDGET"]
    check("video: бюджет — max_kb слота плана (desktop 4 КБ) → QA-BUDGET со ссылкой на слот; вариант mobile — в норме",
          kb > 4 and bd and "hero-loop" in bd[0]["msg"] and bd[0]["threshold"] == 4 and a1["slot"] == "hero"
          and "QA-BUDGET" not in codes(a2) and a2["checks"]["budget"]["key"] == "plan:hero-loop/mobile", (kb, bd, a2["checks"].get("budget")))
    check("video: без плана — бюджет по умолчанию (ключ budget.video.*)",
          a3["checks"]["budget"]["key"].startswith("budget.video.") and "QA-BUDGET" not in codes(a3), a3["checks"].get("budget"))
    rc, _ = _run(["audit", str(d / "between_web.mp4"), "--out", str(tmp / "o_plan4"), "--no-provenance", "--plan", str(plan),
                  "--slot", "нет-такого"])
    rc2, _ = _run(["audit", str(d / "between_web.mp4"), "--out", str(tmp / "o_plan5"), "--no-provenance", "--slot", "hero-loop"])
    check("video: слота нет в плане или id слота без --plan — ошибка вызова (код 2)", rc == 2 and rc2 == 2, (rc, rc2))
    # разовый ролик: пятно едет и останавливается
    yy, xx = np.mgrid[0:180, 0:320]
    once = np.stack([(40 + 180 * np.exp(-((yy - 90) ** 2 + (xx - 40 - 6.5 * min(i, 36)) ** 2) / (2 * 14.0 ** 2))) for i in range(48)])
    write_clip(once.round().astype(np.uint8), d / "intro.mp4")
    o1 = audit([d / "intro.mp4"], tmp / "o_once", mode="video-once")["assets"][0]
    o2 = audit([d / "intro.mp4"], tmp / "o_once_loop")["assets"][0]
    check("video-once: разовый ролик — без находок петли (ни одного QA-LOOP-*)",
          o1["mode"] == "video-once" and not [x["code"] for x in o1["defects"] if x["code"].startswith("QA-LOOP-")]
          and "QA-VIDEO-CAM-CREEP" not in codes(o1), [x["code"] for x in o1["defects"]])
    check("video-once: тот же ролик как петля — QA-LOOP-SEAM fail", "QA-LOOP-SEAM" in codes(o2, ("fail",)), codes(o2))
    # петля с равными концами: шов по файлу как есть — 0
    write_clip(np.concatenate([s, s[:1]]), d / "equal_ends.mp4")
    e = audit([d / "equal_ends.mp4"], tmp / "o_equal")["assets"][0]
    check("video: петля с равными концами — шов 0, QA-LOOP-SEAM нет, срез дубля — info",
          e["checks"]["loop"]["seam_ratio_local"] == 0 and "QA-LOOP-SEAM" not in codes(e)
          and "QA-LOOP-TRIM" in codes(e, ("info",)), (e["checks"]["loop"]["seam_ratio_local"], codes(e)))
    # вспышки: 10 Гц на весь кадр, 25 кадров/с
    fl = np.stack([np.full((180, 320), 235 if int(i * 20 / 25) % 2 else 20, np.uint8) for i in range(50)])
    write_clip(fl, d / "flash.mp4", fps=25)
    f = audit([d / "flash.mp4"], tmp / "o_flash", mode="video-once")["assets"][0]
    check("video: клип со вспышками → QA-VIDEO-FLASH; чистая петля — без неё",
          "QA-VIDEO-FLASH" in codes(f) and f["checks"]["loop"]["flash"]["fail"] and not A["quiet_crf12.mp4"]["checks"]["loop"]["flash"]["fail"],
          f["checks"]["loop"].get("flash"))
    # монтаж трёх планов: два живых и тихий
    mont = np.concatenate([loop_frames(n=24, seed=1), loop_frames(n=24, seed=2, level=190.0), loop_frames(n=24, seed=3, amp=12.0, level=60.0)])
    write_clip(mont, d / "montage.mp4")
    m1 = audit([d / "montage.mp4"], tmp / "o_mont1")["assets"][0]
    m2 = audit([d / "montage.mp4"], tmp / "o_mont2", montage=True)["assets"][0]
    L2 = m2["checks"]["loop"]
    check("montage: без ключа склейка планов — QA-LOOP-CUT fail", "QA-LOOP-CUT" in codes(m1, ("fail",)), codes(m1))
    check("montage: с ключом --montage — три плана, без QA-LOOP-CUT, QA-LOOP-SEAM и QA-LOOP-COLLAPSE; стык петли — склейка",
          L2.get("shots") == 3 and L2["cuts"] == [24, 48] and not ({"QA-LOOP-CUT", "QA-LOOP-SEAM", "QA-LOOP-COLLAPSE"} & codes(m2))
          and L2["seam_check"]["basis"] == "cut", (L2.get("cuts"), codes(m2), L2.get("seam_check")))
    # событие-затемнение: петля уходит в чёрное и выходит из него
    ramp = np.linspace(0, 1, 7)[:6]
    fade = np.concatenate([s[:6] * ramp[:, None, None], s[6:34], s[34:40] * ramp[::-1][:, None, None], np.zeros_like(s[:8])])
    write_clip(fade.round().astype(np.uint8), d / "fade.mp4")
    f1 = audit([d / "fade.mp4"], tmp / "o_fade1")["assets"][0]
    f2 = audit([d / "fade.mp4"], tmp / "o_fade2", fade_event=True)["assets"][0]
    check("fade-event: без ключа — QA-LOOP-COLLAPSE fail; с ключом события-затемнения — warn",
          "QA-LOOP-COLLAPSE" in codes(f1, ("fail",)) and "QA-LOOP-COLLAPSE" in codes(f2, ("warn",))
          and "QA-LOOP-COLLAPSE" not in codes(f2, ("fail",)), (codes(f1), codes(f2)))
    # почти неподвижные концы: шов на уровне соседних кадров
    slow = loop_frames(amp=4.0, gap=1.0, warp=lambda u: u - 0.5 * np.sin(2 * np.pi * u) / (2 * np.pi))
    write_clip(slow, d / "static_ends.mp4")
    se = audit([d / "static_ends.mp4"], tmp / "o_static")["assets"][0]
    sc = se["checks"]["loop"]["seam_check"]
    check("video: почти неподвижные концы — отношение выше порога, шов в норме по абсолютной разнице",
          se["checks"]["loop"]["seam_ratio_local"] > th("video.seam_local_max") and sc["ok"] and sc["basis"] == "abs"
          and "QA-LOOP-SEAM" not in codes(se), (se["checks"]["loop"]["seam_ratio_local"], sc))
    # повторы кадров: каждый пятый кадр дважды; переменная частота — пропуски по таймкодам
    dup = np.concatenate([np.repeat(s[i:i + 1], 2 if i % 5 == 4 else 1, 0) for i in range(len(s))])
    write_clip(dup, d / "dups.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clean), "-vf", "select='not(eq(mod(n\\,5)\\,4))'", "-fps_mode", "vfr",
                    "-threads", "2", *LOSSLESS, str(d / "vfr.mkv")], check=True)
    D = {Path(x["file"]).name: x for x in audit([d / "dups.mp4", d / "vfr.mkv"], tmp / "o_dups")["assets"]}
    tm = D["vfr.mkv"]["checks"]["loop"].get("timing") or {}
    check("video: клип с повторёнными кадрами → QA-VIDEO-DUP-FRAMES; чистая петля — без неё",
          "QA-VIDEO-DUP-FRAMES" in codes(D["dups.mp4"]) and D["dups.mp4"]["checks"]["loop"]["dup_frames"] >= 8
          and "QA-VIDEO-DUP-FRAMES" not in codes(e), D["dups.mp4"]["checks"]["loop"].get("dup_frames"))
    check("video: переменная частота — кадры, которые держатся дольше шага, считаются по таймкодам",
          tm.get("vfr") and tm.get("held_frames", 0) >= 8 and "QA-VIDEO-DUP-FRAMES" in codes(D["vfr.mkv"]), tm)


# вымышленная «наивная» иконка: свой viewBox, жёсткий цвет, толстый штрих
NAIVE_HEART = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="none" stroke="#e11d48" stroke-width="6" '
               'd="M50 82 L18 46 A19 19 0 0 1 50 28 A19 19 0 0 1 82 46 Z"/></svg>')


def t_svg_series(tmp):
    """Иконка набора против «наивной» и серия: одна сцена в четырёх дублях против четырёх сцен разного цвета."""
    import numpy as np
    from PIL import Image
    ref = kbpaths.data("ai-media", "lucide-ref", "search.svg")
    if svg_ready() and ref.exists():
        (tmp / "heart.svg").write_text(NAIVE_HEART, encoding="utf-8")
        s = audit([ref, tmp / "heart.svg"], tmp / "o_svg")
        A = {Path(x["file"]).name: x for x in s["assets"]}
        check("svg: иконка Lucide без fail", A["search.svg"]["verdict"] != "fail", codes(A["search.svg"]))
        check("svg: «наивная» иконка → fail (цвет и шапка)", A["heart.svg"]["verdict"] == "fail"
              and {"QA-SVG-COLOR", "QA-SVG-HEADER"} <= codes(A["heart.svg"], ("fail",)), codes(A["heart.svg"]))
    else:
        check("svg: нет пакетов группы svg (install.sh --groups svg) — пропуск", True)
    d = tmp / "series"
    d.mkdir()
    same, diff = [], []
    for i in range(4):
        p = d / f"shoot_{i}.png"
        calm_photo((640, 400), seed=20 + i).save(p)
        same.append(p)
    base = np.asarray(calm_photo((640, 400), seed=31))
    for i, perm in enumerate(((0, 1, 2), (2, 1, 0), (1, 0, 2), (0, 2, 1))):      # те же формы, другая гамма: четыре «локации»
        p = d / f"place_{i}.png"
        Image.fromarray(np.ascontiguousarray(base[..., perm])).save(p)
        diff.append(p)
    s = audit(same, tmp / "o_ser1", ocr="off", mode="series")
    check("series: одна съёмка → не fail", s["series"]["verdict"] != "fail", s["series"]["metrics"])
    s = audit(diff, tmp / "o_ser2", ocr="off", mode="series")
    check("series: четыре сцены разной гаммы → QA-SERIES-BREAK", any(x["code"] == "QA-SERIES-BREAK" for x in s["series"]["defects"]),
          s["series"]["metrics"])


def t_encoding(tmp):
    """Сжатие к мастеру без усечения глубины, резкость источника отдельно от оценки сжатия, подбор качества под бюджет."""
    import subprocess
    import numpy as np
    from PIL import Image
    from scipy import ndimage as ndi
    avifenc, s2 = kbpaths.bin_dir("libavif", "avifenc"), kbpaths.bin_dir("libjxl", "tools", "ssimulacra2")
    if not (avifenc.exists() and s2.exists() and kbpaths.find("ffmpeg")):
        check("encoding: нет avifenc, ssimulacra2 или ffmpeg (install.sh --bin, --ffmpeg) — пропуск", True)
        return
    d = tmp / "enc"
    d.mkdir()
    # мастер 16 бит: плавный градиент — ступени 8 бит на нём видны, 10 бит ближе к мастеру
    W, H = 640, 400
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    g = np.stack([0.20 + 0.10 * xx / W, 0.22 + 0.08 * yy / H, 0.30 + 0.06 * (xx + yy) / (W + H)], -1)
    raw = np.clip(g * 65535, 0, 65535).astype("<u2").tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le", "-s", f"{W}x{H}", "-i", "-",
                    "-frames:v", "1", "-pix_fmt", "rgb48be", str(d / "master16.png")], input=raw, check=True)
    for depth in (8, 10):
        subprocess.run([str(avifenc), "-q", "70", "-s", "8", "-y", "444", "-d", str(depth), str(d / "master16.png"),
                        str(d / f"grad_{depth}bit.avif")], capture_output=True, check=True)
    A = {Path(x["file"]).name: x for x in audit([d / "grad_8bit.avif", d / "grad_10bit.avif"], tmp / "o_enc", ocr="off",
                                                 master=d / "master16.png", stage="web")["assets"]}
    e8 = (A["grad_8bit.avif"]["checks"].get("encoding") or {}).get("ssimulacra2")
    e10 = (A["grad_10bit.avif"]["checks"].get("encoding") or {}).get("ssimulacra2")
    check("encoding: оценка 10-битного файла не ниже 8-битного того же кадра (декод и мастер без усечения до 8 бит)",
          e8 is not None and e10 is not None and e10 >= e8, (e8, e10))
    # резкость источника: мягкий мастер (увеличен втрое) — сжатие к нему оценивается высоко, резкость — находка
    rng = np.random.default_rng(4)
    tex = ndi.gaussian_filter(rng.random((500, 800, 3)), (0.7, 0.7, 0))
    tex = np.clip((tex - tex.mean()) / tex.std() * 55 + 128, 0, 255).astype(np.uint8)
    sharp = Image.fromarray(tex)
    sharp.save(d / "sharp.png")
    sharp.resize((267, 167), Image.LANCZOS).resize((800, 500), Image.LANCZOS).save(d / "soft.png")
    subprocess.run([str(avifenc), "-q", "85", "-s", "8", "-y", "444", str(d / "soft.png"), str(d / "soft_web.avif")],
                   capture_output=True, check=True)
    w = audit([d / "soft_web.avif"], tmp / "o_soft", ocr="off", master=d / "soft.png", stage="web", slot="section")["assets"][0]
    k = audit([d / "sharp.png"], tmp / "o_sharp", ocr="off")["assets"][0]
    enc = w["checks"].get("encoding") or {}
    check("резкость: мягкий источник — находка QA-SOURCE-SOFT при высокой оценке сжатия к нему",
          enc.get("ssimulacra2", 0) >= enc.get("min", 100) and "QA-ENCODE-QUALITY" not in codes(w)
          and "QA-SOURCE-SOFT" in codes(w, ("info",)) and w["checks"]["sharpness"]["source"].endswith("soft.png"),
          (enc, w["checks"].get("sharpness")))
    check("резкость: детальный кадр — без QA-SOURCE-SOFT", "QA-SOURCE-SOFT" not in codes(k, ("info", "warn")),
          k["checks"].get("sharpness"))
    # подбор качества под бюджет веса: файл не тяжелее бюджета
    pick = str(aa.TOOLS / "avif_pick.sh")
    calm_photo((480, 300)).save(d / "frame.png")
    r0 = subprocess.run(["bash", pick, "-s", "8", str(d / "frame.png"), str(d / "free.avif"), "80"], capture_output=True, text=True)
    size0 = (d / "free.avif").stat().st_size if (d / "free.avif").exists() else 0
    budget_kb = max(1, size0 // 1024 - 1)                      # бюджет ниже файла, прошедшего порог
    r1 = subprocess.run(["bash", pick, "-s", "8", "-b", str(budget_kb), str(d / "frame.png"), str(d / "fit.avif"), "80"],
                        capture_output=True, text=True)
    size1 = (d / "fit.avif").stat().st_size if (d / "fit.avif").exists() else None
    check("avif_pick: без бюджета — код 0 и строка PICK; двоичный поиск — не больше 8 проб на границы 35–85",
          r0.returncode == 0 and "PICK q=" in r0.stdout and len([x for x in r0.stdout.splitlines() if x.startswith("q=")]) <= 8,
          (r0.returncode, r0.stdout[-200:], r0.stderr[-200:]))
    check("avif_pick: бюджет ниже файла порога — вес не выше бюджета, код 3 (порог в бюджете не достигнут)",
          size1 is not None and size1 <= budget_kb * 1024 < size0 and r1.returncode == 3, (size0, budget_kb, size1, r1.returncode))
    r2 = subprocess.run(["bash", pick, "-s", "8", "-b", "0.2", str(d / "frame.png"), str(d / "none.avif"), "80"],
                        capture_output=True, text=True)
    check("avif_pick: в бюджет не укладывается и наименьшее качество — файла нет, код 1",
          r2.returncode == 1 and not (d / "none.avif").exists(), (r2.returncode, r2.stderr[-200:]))


def _run(argv):
    """Команда asset_audit без печати в консоль: (код выхода, вывод stdout)."""
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        rc = aa.main(argv)
    return rc, buf.getvalue()


def _schema_ok(ans: dict, mode: str) -> bool:
    import jsonschema
    sch = json.loads(aa.JUDGE_SCHEMA.read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator({"$defs": sch["$defs"], "$ref": f"#/$defs/{aa.ANSWER_DEF[mode]}"})
    return not list(v.iter_errors(ans))


def _write_answer(pkg: Path, jid: str, kind: str, ans: dict, bad: list):
    """Ответ-заглушка сессии судьи: первая строка вида вызова и блок JSON по схеме ответа."""
    if not _schema_ok(ans, {"попарно": "pairwise"}.get(kind, kind)):
        bad.append(jid)
    first = "попарно" if kind == "попарно" else "рубрика"
    (pkg / "answers" / f"{jid}.md").write_text(f"{first} · заглушка теста · входов хватило\n\n```json\n"
                                               + json.dumps(ans, ensure_ascii=False) + "\n```\n", encoding="utf-8")


def _pair_answers(K: dict, pkg: Path, choose, bad: list):
    """choose(job) → (вариант | tie | both_bad, причина) для каждого вопроса задания; вариант переводится в сторону A/B."""
    for jid, j in K["jobs"].items():
        out = []
        for q in j["questions"]:
            v, why = choose(j, q)
            w = "A" if v == j["A"] else "B" if v == j["B"] else v
            out.append({"id": q, "winner": w, **({"why": why, "where": "левая половина"} if why else {})})
        _write_answer(pkg, jid, "попарно", {"answers": out, "defect_codes": []}, bad)


def t_judge_package(tmp):
    """Пакет судьи из пар: оба порядка и повторы — отдельными заданиями, кадры вслепую, ключ вне пакета; разбор ответов —
    пара совпадением порядков и большинством прогонов (judge.md §5)."""
    from PIL import Image
    d = tmp / "judge_items"
    d.mkdir()
    Image.new("RGB", (800, 500), (200, 90, 60)).save(d / "variant_new_model.png")
    Image.new("RGB", (800, 500), (60, 90, 200)).save(d / "variant_old_model.png")
    Image.new("RGB", (1600, 1000), (90, 160, 90)).save(d / "bigger_same_ratio.png")
    Image.new("RGB", (800, 500), (160, 160, 60)).save(d / "smaller.png")
    Image.new("RGB", (800, 800), (40, 40, 40)).save(d / "square_other.png")
    items = d / "pairs.jsonl"
    items.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in (
        {"pair": "p1", "a": "variant_new_model.png", "b": "variant_old_model.png", "brief": "кресло у окна"},
        {"pair": "p2", "a": "bigger_same_ratio.png", "b": "smaller.png", "brief": "кресло у окна"},
        {"pair": "p3", "a": "variant_new_model.png", "b": "square_other.png", "brief": "кресло у окна"})), encoding="utf-8")
    out = tmp / "judge_out"
    rc, _ = _run(["judge-jobs", "--rubric", "hero-photo", "--items", str(items), "--mode", "pairwise", "--runs", "3",
                  "--out", str(out), "--name", "pkg-pairs"])
    pkg, key_path = out / "pkg-pairs", out / "pkg-pairs.key.json"
    check("judge-jobs: пакет собран (код 0)", rc == 0 and pkg.is_dir(), rc)
    K = json.loads(key_path.read_text(encoding="utf-8"))
    jobs = sorted((pkg / "jobs").glob("*.md"))
    check("judge-jobs: 3 пары × 2 порядка × 3 прогона = 18 заданий", len(jobs) == 18 and len(K["jobs"]) == 18, len(jobs))
    check("judge-jobs: ключ слепоты вне папки пакета", key_path.parent == pkg.parent and not list(pkg.rglob("*.key.json")))
    names = [f.name for f in (pkg / "frames").iterdir()]
    check("judge-jobs: кадры под нейтральными именами (sha256), PNG без потерь",
          names and all(re.fullmatch(r"[0-9a-f]{16}\.png", n) for n in names), names)
    text = "".join(f.read_text(encoding="utf-8") for f in pkg.rglob("*") if f.is_file() and f.suffix in (".md", ".json"))
    leaks = [w for w in ("variant_new_model", "variant_old_model", "bigger_same_ratio", "square_other", "key.json", '"orig_')
             if w in text]
    check("judge-jobs: в пакете нет имён исходников и ключа", not leaks, leaks)
    by: dict = {}
    for j in K["jobs"].values():
        by.setdefault((j["pair"], j["run"]), {})[j["order"]] = (j["A"], j["B"])
    check("judge-jobs: у каждой пары в каждом прогоне — оба порядка, стороны переставлены",
          len(by) == 9 and all(set(v) == {"AB", "BA"} and v["AB"] == v["BA"][::-1] for v in by.values()), by)
    fr = K["pairs"]["p2"]["frames"]
    sizes = {Image.open(pkg / fr[v]).size for v in ("a", "b")}
    check("judge-jobs: кадры пары одной пропорции — к меньшему размеру", sizes == {(800, 500)} and K["pairs"]["p2"].get("resized") == "a",
          (sizes, K["pairs"]["p2"].get("resized")))
    man = json.loads((pkg / "manifest.json").read_text(encoding="utf-8"))
    check("judge-jobs: пара разной пропорции — предупреждение в манифесте", any("пропорции" in w for w in man["warnings"]),
          man["warnings"])
    check("judge-jobs: манифест — рубрика с версией и хэшем, модель судьи из описания агента",
          man["rubric"]["id"] == "hero-photo" and man["rubric"]["version"] and man["rubric"]["sha256"]
          and man["session"]["agent"] == "design-judge", man["rubric"], )
    prompt = jobs[0].read_text(encoding="utf-8")
    check("judge-jobs: задание — кадры пакета, вопросы рубрики, формат ответа по схеме",
          str(pkg / "frames") in prompt and "slot:" in prompt and "pairwise_answer" in prompt and "```json" in prompt)
    rc, _ = _run(["judge-jobs", "--rubric", "hero-photo", "--items", str(items), "--mode", "pairwise", "--out", str(out),
                  "--name", "pkg-pairs"])
    check("judge-jobs: пересборка пакета без ответов — можно", rc == 0)

    bad: list = []

    def choose(j, q):
        if j["pair"] == "p1":
            return "a", "тёплее и спокойнее"
        if j["pair"] == "p2":
            return ("a" if j["order"] == "AB" else "b", "по-разному") if j["run"] == 3 else ("b", "ровнее зона")
        return {1: ("a", "чище"), 2: ("b", "чище"), 3: ("a", "")}[j["run"]]
    _pair_answers(K, pkg, choose, bad)
    check("заглушки: ответы проходят схему ответа", not bad, bad)
    rc, _ = _run(["judge-jobs", "--rubric", "hero-photo", "--items", str(items), "--mode", "pairwise", "--out", str(out),
                  "--name", "pkg-pairs"])
    check("judge-jobs: пакет с ответами не перезаписывается без --force (код 2)", rc == 2, rc)
    rc, _ = _run(["judge-parse", str(pkg)])
    V = json.loads((out / "pkg-pairs.verdict.json").read_text(encoding="utf-8"))
    pv = {p: {q: r["verdict"] for q, r in qs.items()} for p, qs in V["pairs"].items()}
    check("judge-parse: код 0, все ответы разобраны", rc == 0 and V["answers"] == 18 and not V["missing"] and not V["invalid"],
          (rc, V["missing"], V["invalid"]))
    check("judge-parse: пара — вариант, выбранный в обоих порядках всеми прогонами", pv["p1"] == {"slot": "a", "natural": "a"}, pv["p1"])
    check("judge-parse: разные ответы порядков — ничья прогона; вердикт — большинство (2 из 3)",
          pv["p2"]["slot"] == "b" and V["pairs"]["p2"]["slot"]["runs"]["3"] == "tie", V["pairs"]["p2"]["slot"])
    check("judge-parse: выбор без причины — ничья; нет большинства — «неразличимы»", pv["p3"]["slot"] == "indistinct",
          V["pairs"]["p3"]["slot"])
    b = V["batch"]
    check("judge-parse: партия — доля позиции A и согласованность перестановки посчитаны",
          b["position_A_share"] is not None and b["swap_consistency"] is not None and b["swap_runs"] == 18, b)
    rows = (out / "pkg-pairs.answers.jsonl").read_text(encoding="utf-8").splitlines()
    check("judge-parse: строки ответов лежат рядом с ключом, вне пакета", len(rows) == 18 and not list(pkg.rglob("*.jsonl")))
    (pkg / "answers" / "j001.md").unlink()
    rc, _ = _run(["judge-parse", str(pkg), "--out", str(tmp / "v_missing.verdict.json")])
    check("judge-parse: нет ответа — код 1 и задание в missing", rc == 1 and "j001" in json.loads(
        (tmp / "v_missing.verdict.json").read_text(encoding="utf-8"))["missing"], rc)


def t_judge_rubric(tmp):
    """Рубрика по кадру: маркер и находка засчитываются, если есть не меньше чем в двух прогонах; «да» без места и «нет»
    без доказательства — «не уверен»; F1 против разметки человека."""
    from PIL import Image
    d = tmp / "judge_rubric"
    d.mkdir()
    Image.new("RGB", (900, 600), (180, 170, 150)).save(d / "hero.png")
    (d / "items.jsonl").write_text(json.dumps({"id": "hero", "image": "hero.png", "brief": "кресло у окна"}) + "\n", encoding="utf-8")
    out = tmp / "judge_rub"
    rc, _ = _run(["judge-jobs", "--rubric", "hero-photo", "--items", str(d / "items.jsonl"), "--mode", "defects", "--runs", "3",
                  "--out", str(out), "--name", "def"])
    K = json.loads((out / "def.key.json").read_text(encoding="utf-8"))
    check("judge-jobs defects: кадр × 3 прогона = 3 задания", rc == 0 and len(K["jobs"]) == 3, len(K["jobs"]))
    bad: list = []
    for jid, j in K["jobs"].items():
        r = j["run"]
        defects = [{"code": c, "present": "no", "where": ""} for c in j["questions"]]
        for dd in defects:
            if dd["code"] == "IMG-M03" and r in (1, 2):
                dd.update(present="yes", where="небо сверху", evidence="ореол у кромки крыши")
            if dd["code"] == "IMG-M05" and r == 1:
                dd.update(present="yes", where="правый угол", evidence="фиолетовый отсвет")
            if dd["code"] == "IMG-M06":
                dd.update(present="yes", where="")
        fnd = [{"what": "глянец", "where": "кресло", "rule": "RUB-GLOSS", "evidence": "блик как на обложке"}] if r in (2, 3) else []
        _write_answer(out / "def", jid, "defects", {"defects": defects, "findings": fnd}, bad)
    check("заглушки defects: ответы проходят схему ответа", not bad, bad)
    rc, _ = _run(["judge-parse", str(out / "def")])
    V = json.loads((out / "def.verdict.json").read_text(encoding="utf-8"))
    it = V["items"]["hero"]
    conf = {x["code"]: x["confirmed"] for x in it["defects"]}
    check("judge-parse: маркер в 2 из 3 прогонов засчитан, в 1 из 3 — нет", conf.get("IMG-M03") is True and conf.get("IMG-M05") is False,
          conf)
    check("judge-parse: «есть» без «где» — не уверен, не маркер", "IMG-M06" not in conf and V["batch"]["unsure_share"] > 0,
          (conf, V["batch"]["unsure_share"]))
    check("judge-parse: находка вне перечня в 2 из 3 прогонов засчитана", any(f["rule"] == "RUB-GLOSS" and f["confirmed"] for f in it["findings"]),
          it["findings"])
    rows = out / "def.answers.jsonl"
    labels = tmp / "labels.jsonl"
    labels.write_text(json.dumps({"key": it["key"], "defects": {"IMG-M03": "yes", "IMG-M05": "yes", "RUB-GLOSS": "no",
                                                                 "IMG-M07": "no"}}) + "\n", encoding="utf-8")
    rc, txt = _run(["agree", "--answers", str(rows), "--labels", str(labels)])
    rep = json.loads(txt)
    dd = rep.get("defects") or {}
    check("agree: F1 находок против разметки человека (tp 1, fp 1, fn 1 → 0,5), мало данных",
          dd.get("tp") == 1 and dd.get("fp") == 1 and dd.get("fn") == 1 and dd.get("f1") == 0.5 and dd.get("decision") == "мало данных", dd)
    ck = tmp / "judge_chk"
    rc, _ = _run(["judge-jobs", "--rubric", "hero-photo", "--items", str(d / "items.jsonl"), "--mode", "checklist", "--runs", "3",
                  "--out", str(ck), "--name", "chk"])
    K = json.loads((ck / "chk.key.json").read_text(encoding="utf-8"))
    bad = []
    for jid, j in K["jobs"].items():
        ans = [{"id": q, "answer": "yes"} for q in j["questions"]]
        ans[0] = {"id": ans[0]["id"], "answer": "no", **({"evidence": "зона под заголовок пёстрая"} if j["run"] < 3 else {})}
        ans[1] = {"id": ans[1]["id"], "answer": "not_applicable"}
        _write_answer(ck / "chk", jid, "checklist", {"answers": ans, "findings": []}, bad)
    rc, _ = _run(["judge-parse", str(ck / "chk")])
    V = json.loads((ck / "chk.verdict.json").read_text(encoding="utf-8"))
    chk = V["items"]["hero"]["checklist"]
    check("judge-parse checklist: «нет» с доказательством большинством, «не применимо» — отдельный ответ",
          not bad and chk.get("g1") == "no" and chk.get("g2") == "not_applicable", chk)
    # без рубрики ai-media — вопросы рубрики владельца в строке входа (макет, страница: ui 13/02, site-rubric)
    mock = d / "mock.jsonl"
    mock.write_text(json.dumps({"id": "home-1440", "image": "hero.png", "brief": "главная, первый экран",
                                "questions": [{"id": "hierarchy", "q": "Главный заголовок читается первым на кадре?"},
                                              {"id": "alignment", "q": "У блоков одна главная левая вертикаль?"}],
                                "report": "mockup_checks: 0 FAIL, 1 WARN (LOOK-HEADER 72 > 64)"}, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    rc, _ = _run(["judge-jobs", "--items", str(mock), "--mode", "checklist", "--out", str(tmp / "judge_mock"), "--name", "mock"])
    jobs = sorted((tmp / "judge_mock" / "mock" / "jobs").glob("*.md"))
    txt = jobs[0].read_text(encoding="utf-8") if jobs else ""
    check("judge-jobs без --rubric: вопросы строки, машинный отчёт первым, 3 прогона",
          rc == 0 and len(jobs) == 3 and "hierarchy: Главный заголовок" in txt and "Машинный отчёт" in txt
          and txt.index("Машинный отчёт") < txt.index("## Рубрика"), (rc, len(jobs)))
    rc, _ = _run(["judge-jobs", "--items", str(d / "items.jsonl"), "--mode", "checklist", "--out", str(tmp / "judge_mock")])
    check("judge-jobs без --rubric и без вопросов в строке — ошибка входа (код 2)", rc == 2, rc)


def t_judge_trust(tmp):
    """Уровень доверия — пороги группы judge thresholds.yaml: смена порога в копии меняет уровень; сессии подряд."""
    import yaml
    th = aa.Th(aa.load_thresholds())
    p, lo, hi = aa.wilson(20, 25)
    check("trust_level: 20/25 (Уилсон ≈ 0,61 < 0,65) — только предфильтр", aa.trust_level(p, lo, 25, th) == "только предфильтр",
          (round(lo, 3), aa.trust_level(p, lo, 25, th)))
    doc = yaml.safe_load(aa.THRESHOLDS.read_text(encoding="utf-8"))
    doc["thresholds"]["judge"]["wilson_low_min"]["value"] = 0.6
    t2 = tmp / "thresholds-wilson.yaml"
    t2.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    check("trust_level: копия с wilson_low_min 0,6 — сортировать", aa.trust_level(p, lo, 25, aa.Th(aa.load_thresholds(t2))) == "сортировать")
    doc["thresholds"]["judge"]["min_pairs"]["value"] = 30
    t3 = tmp / "thresholds-pairs.yaml"
    t3.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    check("trust_level: копия с min_pairs 30 — мало данных", aa.trust_level(p, lo, 25, aa.Th(aa.load_thresholds(t3))) == "мало данных")
    del doc["thresholds"]["judge"]["wilson_low_min"]
    t4 = tmp / "thresholds-broken.yaml"
    t4.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    try:
        aa.trust_level(0.9, 0.8, 40, aa.Th(aa.load_thresholds(t4)))
        raised = False
    except aa.JudgeError:
        raised = True
    check("trust_level: нет порога в группе judge — ошибка входа, чисел в коде нет", raised)
    # согласие по сессиям: 25 пар, судья всегда за вариант a; сессия 1 — человек за A, сессии 2–4 — за B
    K = {"pairs": {f"p{i:03d}": {"A": {"files": [f"/src/a{i}.png"]}, "B": {"files": [f"/src/b{i}.png"]}} for i in range(25)}}
    (tmp / "page.key.json").write_text(json.dumps(K), encoding="utf-8")
    rows = []
    for i in range(25):
        for run in (1, 2, 3):
            for order, (A, B) in (("AB", ("a", "b")), ("BA", ("b", "a"))):
                rows.append({"mode": "pairwise", "pair": f"p{i:03d}", "run": run, "order": order, "A": A, "B": B,
                             "A_orig": f"/src/{A}{i}.png", "B_orig": f"/src/{B}{i}.png",
                             "answers": {"slot": "A" if A == "a" else "B"}, "valid": True})
    (tmp / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    votes = []
    for s_, side in enumerate(("A", "B", "B", "B"), 1):
        f = tmp / f"votes-{s_}.json"
        f.write_text(json.dumps({"voter": "заказчик", "votes": {f"p{i:03d}": {"slot": side} for i in range(25)}}), encoding="utf-8")
        votes += ["--votes", str(f)]
    rc, txt = _run(["agree", "--answers", str(tmp / "rows.jsonl"), "--key", str(tmp / "page.key.json"), *votes])
    rep = json.loads(txt)
    ag = rep["pairwise"]["slot"]
    check("agree: вердикт пары по протоколу против решающих голосов, 25 из 100", ag["n"] == 100 and ag["agree"] == 0.25
          and ag["decision"] == "не использовать", ag)
    check("agree: расхождение с заказчиком 3 сессии подряд — пересчитать калибровку",
          rep["sessions_disagree_tail"] == 3 and any("сессий подряд" in x for x in rep["recalibrate"]), rep.get("recalibrate"))


def t_judge_calibration(tmp):
    """Задания калибровки из assets/calibration/index.yaml: пары, вопросы из поля rubric, разметка — только в ключе."""
    out = tmp / "judge_cal"
    rc, txt = _run(["judge-jobs", "--calibration", "--pairs", "am-f04,cr-zveno-light,bl-c1-mug", "--runs", "3", "--out", str(out),
                    "--name", "cal"])
    pkg = out / "cal"
    K = json.loads((out / "cal.key.json").read_text(encoding="utf-8"))
    check("calibration: 3 пары × 2 порядка × 3 прогона = 18 заданий", rc == 0 and len(K["jobs"]) == 18, len(K.get("jobs", {})))
    text = "".join(f.read_text(encoding="utf-8") for f in pkg.rglob("*") if f.is_file() and f.suffix in (".md", ".json"))
    import yaml
    idx = yaml.safe_load(aa.CALIBRATION.read_text(encoding="utf-8"))
    ours = [f for f in idx["frames"] if f.get("pair") in ("am-f04", "cr-zveno-light", "bl-c1-mug")]
    leaks = [w for f in ours for w in (Path(f["file"]).stem, *(str(f.get(k) or "")[:40] for k in ("illustrates", "assessment", "look_at")))
             if w and w in text]
    leaks += [w for w in ("index.yaml", "calibration/frames", "illustrates", "look_at", "zveno", "Звено") if w in text]
    check("calibration: в пакете нет имён кадров, разметки и адреса набора", not leaks, leaks)
    check("calibration: ожидание, сила и адрес рубрики — в ключе", K["pairs"]["am-f04"]["expect"] == "17"
          and K["pairs"]["cr-zveno-light"]["expect"] == "02" and "hero-photo.rubric.json" in K["pairs"]["am-f04"]["rubric_address"])
    qs = {j["pair"]: j["questions"] for j in K["jobs"].values()}
    check("calibration: вопросы из поля rubric — g1, g3 рубрики hero-photo; craft и craft.media рубрики эффектности",
          qs["am-f04"] == ["g1", "g3"] and qs["cr-zveno-light"] == ["craft", "craft.media"], qs)
    bad: list = []

    def choose(j, q):
        exp = K["pairs"][j["pair"]]["expect"]
        other = next(v for v in K["pairs"][j["pair"]]["variants"] if v != exp)
        return (other if j["order"] == "AB" else exp, "сравнение") if j["run"] == 3 else (exp, "ровнее и честнее")
    _pair_answers(K, pkg, choose, bad)
    rc, _ = _run(["judge-parse", str(pkg)])
    V = json.loads((out / "cal.verdict.json").read_text(encoding="utf-8"))
    check("calibration: judge-parse — попадания в уровень по ожиданию ключа (2 из 3 прогонов)",
          not bad and V["calibration"]["hit"] == 5 and V["calibration"]["miss"] == 0, V.get("calibration"))
    rc, _ = _run(["judge-jobs", "--calibration", "--pairs", "нет-такой-пары", "--out", str(out)])
    check("calibration: неизвестная пара — ошибка входа (код 2)", rc == 2, rc)


def t_stand_page(tmp):
    """Пакет из страницы голосования: судья видит те же файлы, что заказчик (байт в байт); согласие — по исходникам."""
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
    out = tmp / "judge_page"
    rc, _ = _run(["judge-jobs", "--rubric", "hero-photo", "--from-stand-page", str(page), "--runs", "1", "--out", str(out),
                  "--name", "page"])
    J = json.loads((out / "page.key.json").read_text(encoding="utf-8"))
    page_img = {hashlib.sha256(f.read_bytes()).hexdigest() for f in (page / "img").iterdir()}
    pkg_img = {hashlib.sha256(f.read_bytes()).hexdigest() for f in (out / "page" / "frames").iterdir()}
    check("stand page: кадры пакета — файлы страницы байт в байт", rc == 0 and pkg_img and pkg_img <= page_img, (rc, len(pkg_img)))
    check("stand page: только основные пары (без контрольных, повторов, «одинаковых»), оба порядка",
          len(J["pairs"]) == 3 and len(J["jobs"]) == 6, (len(J["pairs"]), len(J["jobs"])))
    model_of = {str(tmp / f"{m}.png"): m for m in rank}
    bad: list = []

    def choose(j, q):
        return ("a" if rank[model_of[j["orig_a"]]] < rank[model_of[j["orig_b"]]] else "b", "насыщеннее цвет")
    _pair_answers(J, out / "page", choose, bad)
    _run(["judge-parse", str(out / "page")])
    votes = {pid: {"slot": "A" if rank[kp["A"]["model"]] < rank[kp["B"]["model"]] else "B"} for pid, kp in K["pairs"].items()
             if not (kp.get("gold") or kp.get("identical") or kp.get("repeat_of"))}
    (tmp / "votes_s.json").write_text(json.dumps({"votes": votes}), encoding="utf-8")
    rc, txt = _run(["agree", "--answers", str(out / "page.answers.jsonl"), "--votes", str(tmp / "votes_s.json"), "--key",
                    str(tmp / "page.key.json")])
    ag = json.loads(txt).get("pairwise", {}).get("slot", {})
    check("stand page: согласие по исходникам сторон 3/3, пар меньше min_pairs — мало данных",
          not bad and ag.get("agree") == 1.0 and ag.get("n") == 3 and ag.get("decision") == "мало данных", ag)
    big = tmp / "big.png"
    Image.new("RGB", (2400, 1600), (120, 110, 100)).save(big)
    enc_items = tmp / "pairs_enc.jsonl"
    enc_items.write_text(json.dumps({"pair": "q1", "a": str(big), "b": str(tmp / "m2.png")}) + "\n", encoding="utf-8")
    rc, _ = _run(["judge-jobs", "--rubric", "hero-photo", "--items", str(enc_items), "--mode", "pairwise", "--runs", "1",
                  "--same-encoding", "--out", str(out), "--name", "enc"])
    fr = list((out / "enc" / "frames").iterdir())
    check("same-encoding: обе стороны — JPEG ≤ 1600 px, как на странице голосования",
          rc == 0 and len(fr) == 2 and all(f.suffix == ".jpg" and max(Image.open(f).size) <= 1600 for f in fr), [f.name for f in fr])


def t_provenance(tmp):
    """Провенанс через provenance_check.py (+ --corners): надпись в углу → QA-PROV-VISIBLE-MARK (info) и лист углов для глаза."""
    if not (aa.TOOLS / "provenance_check.py").exists():
        check("provenance: нет provenance_check.py — пропуск", True)
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
          "QA-PROV-VISIBLE-MARK" in codes(A["p_marked.png"], ("info",)) and (tmp / "o_prov" / "p_marked_corners.jpg").exists(), pm)
    vm = [d for d in A["p_marked.png"]["defects"] if d["code"] == "QA-PROV-VISIBLE-MARK"]
    check("provenance: метка в углу — info с листом углов, вердикт не роняет; лист — в списке «человеку»",
          vm and all(d["level"] == "info" and "corners" in str(d.get("evidence")) for d in vm)
          and "QA-PROV-VISIBLE-MARK" not in codes(A["p_marked.png"])
          and any("QA-PROV-VISIBLE-MARK" in (h.get("codes") or []) for h in A["p_marked.png"]["human"]), vm)
    check("provenance: чистый кадр без подозрения на метку", "QA-PROV-VISIBLE-MARK" not in codes(A["p_clean.png"], ("info", "warn")),
          (A["p_clean.png"]["checks"].get("provenance") or {}).get("visible_suspect"))
    # ворота 12-legal-provenance/04 §5 п. 8: файл ИИ-ассета (есть паспорт) для страницы без машиночитаемой метки →
    # QA-PROV-NO-MARK; после stamp — нет. Штамп пишет exiftool окружения скилла.
    if kbpaths.find("exiftool") is None:
        check("provenance: нет exiftool (install.sh) — пропуск проверки штампа", True)
        return
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


# Heroicons v2, outline «home» (MIT): набор со штрихом 1,5, без width и height в шапке, round — у контура, не у корня
HEROICONS_HOME = ('<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">'
                  '<path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 '
                  '9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 '
                  '1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/></svg>')


def svg_ready() -> bool:
    """Пакеты группы svg в Python окружения скилла (им check_icons рисует иконку)."""
    import subprocess
    r = subprocess.run([kbpaths.python(), "-c", "import cairosvg, svgelements, skimage, scipy"], capture_output=True, text=True)
    return r.returncode == 0


def t_icon_set(tmp):
    """Шапка и штрих Lucide — брак только у набора Lucide; у другого набора — предупреждение с советом; цвет — брак всегда."""
    if not svg_ready():
        check("icon-set: нет пакетов группы svg (install.sh --groups svg) — пропуск", True)
        return
    d = tmp / "icon_set"
    d.mkdir()
    (d / "home.svg").write_text(HEROICONS_HOME, encoding="utf-8")
    (d / "home_red.svg").write_text(HEROICONS_HOME.replace('stroke="currentColor"', 'stroke="#e11d48"'), encoding="utf-8")
    s = audit([d / "home.svg"], tmp / "o_set_lucide")
    A = s["assets"][0]
    check("icon-set: Heroicons «home» при наборе Lucide (по умолчанию) — QA-SVG-HEADER fail, как было",
          A["verdict"] == "fail" and "QA-SVG-HEADER" in codes(A, ("fail",)), codes(A, ("fail",)))
    s = audit([d / "home.svg", d / "home_red.svg"], tmp / "o_set_hero", icon_set="heroicons")
    A = {Path(x["file"]).name: x for x in s["assets"]}
    h = A["home.svg"]
    hd = [x for x in h["defects"] if x["code"] == "QA-SVG-HEADER"]
    check("icon-set: Heroicons «home» при наборе heroicons — warn, не fail; уровень — из levels check_icons",
          h["verdict"] == "warn" and "QA-SVG-HEADER" in codes(h, ("warn",)) and not codes(h, ("fail",))
          and (h["checks"].get("icon") or {}).get("levels", {}).get("шапка") == "warn", (h["verdict"], codes(h)))
    check("icon-set: находка шапки у другого набора — с правилом Lucide и советом сверить со спецификацией набора",
          hd and "stroke-width 2" in hd[0]["msg"] and "сверить" in hd[0]["msg"] and "heroicons" in hd[0]["msg"],
          [x["msg"] for x in hd])
    check("icon-set: жёсткий цвет — брак у любого набора (QA-SVG-COLOR fail при heroicons)",
          "QA-SVG-COLOR" in codes(A["home_red.svg"], ("fail",)), codes(A["home_red.svg"]))
    ref = kbpaths.data("ai-media", "lucide-ref", "search.svg")
    if ref.exists():
        s = audit([ref], tmp / "o_set_ref")
        check("icon-set: иконка Lucide при наборе Lucide — без флагов шапки", "QA-SVG-HEADER" not in codes(s["assets"][0]),
              codes(s["assets"][0]))
    # эталон шапки параметрами: иконка набора Lucide со штрихом 1,5 из норм дизайн-системы
    thin = d / "thin"
    thin.mkdir()
    (thin / "mark.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
                                   'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
                                   '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>', encoding="utf-8")
    (d / "system.yaml").write_text("conventions:\n  icons: {set: lucide, sizes: [16, 20], stroke: 1.5}\n", encoding="utf-8")
    a0 = audit([thin / "mark.svg"], tmp / "o_thin0")["assets"][0]
    a1 = audit([thin / "mark.svg"], tmp / "o_thin1", icon_stroke=1.5)["assets"][0]
    a2 = audit([thin / "mark.svg"], tmp / "o_thin2", conventions=d / "system.yaml")["assets"][0]
    check("icon-stroke: штрих 1,5 при эталоне Lucide (2) — QA-SVG-HEADER fail; при --icon-stroke 1.5 и при --conventions — чисто",
          "QA-SVG-HEADER" in codes(a0, ("fail",)) and not codes(a1) and not codes(a2)
          and (a2["checks"].get("icon") or {}).get("header_rules", {}).get("stroke-width") == "1.5", (codes(a0), codes(a1), codes(a2)))


def t_env(tmp):
    """Нет моделей, пакета или бинарника — одна строка с командой установки вместо трассировки."""
    import os
    import subprocess
    calm_photo((320, 200)).save(tmp / "env.png")
    saved = aa.OCR_MODELS
    aa.OCR_MODELS = tmp / "no-models"
    try:
        res = aa.run_ocr([tmp / "env.png"], "ru")
        s = audit([tmp / "env.png"], tmp / "o_env_ocr", ocr="on")
    finally:
        aa.OCR_MODELS = saved
    err = res[0].get("error", "")
    check("env: нет моделей OCR — одна строка «поставьте scripts/install.sh --groups ocr --models», без запуска OCR",
          res[0].get("env") and "\n" not in err and "eslav_PP-OCRv5_rec_mobile.onnx" in err
          and "`scripts/install.sh --groups ocr --models`" in err, err)
    A = s["assets"][0]
    check("env: OCR не запущен — строка в errors (needs_human) и в «Окружение» сводки и audit.md",
          A["verdict"] == "needs_human" and len(A["errors"]) == 1 and A["errors"][0].startswith("OCR не запущен: нет моделей OCR")
          and s.get("env") == A.get("env") and "--groups ocr --models" in (tmp / "o_env_ocr" / "audit.md").read_text(encoding="utf-8"),
          (A["errors"], s.get("env")))
    # нет пакета группы svg: заглушка cairosvg в PYTHONPATH обработчика check_icons → код 2 и одна строка
    stub = tmp / "stub_nocairo"
    stub.mkdir()
    (stub / "cairosvg.py").write_text("raise ImportError('заглушка теста', name='cairosvg')\n", encoding="utf-8")
    (tmp / "env_icon").mkdir()
    (tmp / "env_icon" / "home.svg").write_text(HEROICONS_HOME, encoding="utf-8")
    old = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = str(stub) + (os.pathsep + old if old else "")
    try:
        r = subprocess.run([kbpaths.python(), str(aa.TOOLS / "check_icons.py"), str(tmp / "env_icon")], capture_output=True, text=True)
        s = audit([tmp / "env_icon" / "home.svg"], tmp / "o_env_svg")
    finally:
        if old is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = old
    lines = [x for x in r.stderr.splitlines() if x.strip()]
    check("env: check_icons без cairosvg — код 2, одна строка «поставьте scripts/install.sh --groups svg»",
          r.returncode == 2 and len(lines) == 1 and "`scripts/install.sh --groups svg`" in lines[0], (r.returncode, lines))
    A = s["assets"][0]
    check("env: asset_audit — check_icons не запущен, одна строка с командой установки",
          any(e.startswith("check_icons не запущен: нет пакета cairosvg") and "--groups svg" in e for e in A["errors"])
          and any("--groups svg" in h for h in s.get("env", [])), (A["errors"], s.get("env")))
    # нет c2patool: провенанс неполон — строка в «Окружение», вердикт не меняется
    old = os.environ.get("C2PATOOL")
    os.environ["C2PATOOL"] = str(tmp / "no-c2patool")
    try:
        a = aa.build_parser().parse_args(["audit", str(tmp / "env.png"), "--out", str(tmp / "o_env_prov"), "--ocr", "off"])
        s = aa.audit_paths(a)
    finally:
        if old is None:
            os.environ.pop("C2PATOOL", None)
        else:
            os.environ["C2PATOOL"] = old
    A = s["assets"][0]
    check("env: нет c2patool — «c2patool не найден — поставьте scripts/install.sh --bin» в «Окружение», errors и вердикт без неё",
          any(h.startswith("c2patool не найден") and h.endswith("`scripts/install.sh --bin`") for h in s.get("env", []))
          and not any("c2patool" in e for e in A["errors"]), (s.get("env"), A["errors"], A["verdict"]))


def t_palette_cli(tmp):
    """palette.py из командной строки: картинки → палитра JSON (--k, --json), справка, ошибка входа — код 2."""
    import subprocess
    import numpy as np
    from PIL import Image
    img = np.zeros((100, 200, 3), np.uint8)
    img[:, :140] = (200, 60, 40)
    img[:, 140:] = (30, 90, 160)
    Image.fromarray(img).save(tmp / "two.png")
    tool = str(aa.TOOLS / "palette.py")
    r = subprocess.run([sys.executable, tool, str(tmp / "two.png"), "--k", "2", "--json"], capture_output=True, text=True)
    try:
        pal = json.loads(r.stdout)["images"][0]["palette"]
    except (json.JSONDecodeError, KeyError, IndexError):
        pal = []

    def near(hx, rgb):
        return all(abs(int(hx[1 + 2 * i:3 + 2 * i], 16) - v) <= 1 for i, v in enumerate(rgb))
    check("palette.py --k 2 --json: два цвета с долями 0,7 и 0,3, hex и OKLCH",
          r.returncode == 0 and len(pal) == 2 and near(pal[0]["hex"], (200, 60, 40)) and abs(pal[0]["share"] - 0.7) < 0.02
          and near(pal[1]["hex"], (30, 90, 160)) and len(pal[0]["oklch"]) == 3, (r.returncode, pal, r.stderr[-200:]))
    r = subprocess.run([sys.executable, tool, str(tmp / "two.png"), str(tmp / "two.png"), "--json"], capture_output=True, text=True)
    try:
        P = json.loads(r.stdout)
    except json.JSONDecodeError:
        P = {}
    check("palette.py: цветов меньше k — палитра короче, без падения; у двух картинок — общая палитра all",
          r.returncode == 0 and len(P.get("images", [{}])[0].get("palette", [])) == 2 and "all" in P, (r.returncode, r.stderr[-200:]))
    r = subprocess.run([sys.executable, tool, "--help"], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, tool, str(tmp / "нет.png")], capture_output=True, text=True)
    check("palette.py --help — справка; нет картинки — код 2 и одна строка",
          r.returncode == 0 and "--k" in r.stdout and r2.returncode == 2 and len(r2.stderr.strip().splitlines()) == 1,
          (r.returncode, r2.returncode, r2.stderr))


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
    # OCR менее уверен на «не-словах» (0,87 < 0,9) → чаще needs_human, чем fail (на 72 синтетических баннерах с пропуском
    # буквы — 60 fail и 12 needs_human);
    # главное — ошибка не проходит как pass и названа классом
    check("ocr: пропуск буквы → не pass, класс omission", t_miss in ("fail", "needs_human") and "omission" in tm.get("fail_classes", []), tm)
    # две одинаковые надписи и мелкая строка с расхождением
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 9)     # рамка строки OCR ≈ 12 px
    im = Image.new("RGB", (760, 240), (245, 242, 236))
    dr = ImageDraw.Draw(im)
    dr.text((24, 30), "Скидка 20 %", font=f, fill=(20, 20, 20))
    dr.text((24, 130), "Скидка 20 %", font=f, fill=(20, 20, 20))
    im.save(tmp / "twice.png")
    im = Image.new("RGB", (760, 200), (245, 242, 236))
    dr = ImageDraw.Draw(im)
    dr.text((24, 30), "Весенняя распродажа", font=f, fill=(20, 20, 20))
    dr.text((24, 140), "товары до конца месяца", font=small, fill=(20, 20, 20))
    im.save(tmp / "small.png")
    s2 = audit([tmp / "twice.png"], tmp / "o_ocr2", expect=["Скидка 20 %{×2}"])["assets"][0]
    s3 = audit([tmp / "small.png"], tmp / "o_ocr3", expect=["Весенняя распродажа", "товаров до конца месяца"])["assets"][0]
    check("ocr: две одинаковые надписи при --expect «…{×2}» — чисто", (s2["checks"].get("text") or {}).get("verdict") == "pass"
          and "QA-TEXT-MISMATCH" not in codes(s2), s2["checks"].get("text"))
    check("ocr: расхождение в мелкой строке → QA-TEXT-SMALL warn, не fail", "QA-TEXT-SMALL" in codes(s3, ("warn",))
          and not ({"QA-TEXT-MISMATCH", "QA-TEXT-CHECK"} & codes(s3)), (s3["checks"].get("text"), s3["checks"].get("ocr")))


def run(keep=False, ocr=False, verbose=False):
    R.clear()
    tmp = Path(tempfile.mkdtemp(prefix="asset_audit_test_"))
    try:
        for t in (t_thresholds, t_text, lambda: t_image_cutout_texture(tmp), lambda: t_edit(tmp), lambda: t_video(tmp),
                  lambda: t_svg_series(tmp), lambda: t_encoding(tmp), lambda: t_judge_package(tmp), lambda: t_judge_rubric(tmp),
                  lambda: t_judge_trust(tmp), lambda: t_judge_calibration(tmp), lambda: t_stand_page(tmp),
                  lambda: t_provenance(tmp), lambda: t_icon_set(tmp), lambda: t_env(tmp),
                  lambda: t_palette_cli(tmp)) + ((lambda: t_ocr(tmp),) if ocr else ()):
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
