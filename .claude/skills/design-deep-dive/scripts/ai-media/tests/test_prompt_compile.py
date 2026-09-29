#!/usr/bin/env python3
"""Офлайн-тесты prompt_compile.py: CLI и API, ценовые параметры, видео, правки, референсы, каналы, соотношения,
задания polza.py и чтение снимка каталога. Без сети и генераций; нужен снимок каталога polza (scripts/install.sh
--catalogs) — без него тесты завершаются строкой о снимке и кодом 2.
Запуск: $DDD_HOME/venv/bin/python scripts/ai-media/tests/test_prompt_compile.py [-v]"""
import json, os, pathlib, re, subprocess, sys, tempfile
HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parent
sys.path.insert(0, str(TOOLS.parent / "lib"))  # scripts/lib: kbpaths
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("ai-media")
sys.path.insert(0, str(TOOLS))
import prompt_compile as pc  # noqa: E402

D, C = pc.load_dialects(), pc.load_catalog()
FX = HERE / "fixtures"
F = lambda n: pc.load_json(FX / f"{n}.spec.json")
E = lambda n: pc.load_json(FX / "D02" / f"{n}.spec.json")
B = lambda n: pc.load_json(FX / "D03" / f"{n}.spec.json")
comp = lambda spec, m, d=None, **kw: pc.compile_prompt(spec, m, d, D, C, **kw)
R = []


def check(name, cond, info=""):
    R.append((name, bool(cond), info))


def fx(n, m, d=None, **kw):
    return comp(F(n), m, d, spec_path=FX / f"{n}.spec.json", **kw)


# --- 1. совместимость CLI и API
py = sys.executable
cli = lambda *a: subprocess.run([py, str(TOOLS / "prompt_compile.py"), *a], capture_output=True, text=True)
r = cli("validate", str(FX / "D02/E1.spec.json"))
check("CLI validate E1 → OK, код 0", r.returncode == 0 and "OK" in r.stdout, r.stdout[-200:])
r = cli("compile", str(FX / "D02/E1.spec.json"), "--model", "black-forest-labs/flux.2-pro")
check("CLI compile: строка «// модель · семейство · диалект» и params", r.stdout.startswith("// black-forest-labs/flux.2-pro · flux2 · prose") and "params:" in r.stdout, r.stdout[:200])
with tempfile.TemporaryDirectory() as td:
    out = pathlib.Path(td) / "j.jsonl"
    r = cli("jobs", str(FX / "D03/B2.spec.json"), "--models", "qwen/image-2.1",
            "--dialects", "prose,json", "--repeats", "2", "--seeds", "101,202", "--out", str(out))
    lines = out.read_text().splitlines() if out.exists() else []
    j0 = json.loads(lines[0]) if lines else {}
    check("CLI jobs: 4 задания, seed 101/202, meta.compile, provider mie без запасных", len(lines) == 4 and j0["input"].get("seed") == 101
          and j0["meta"]["compile"]["schema"] == "prompt-compile-passport/1" and j0["provider"] == {"only": ["mie"], "allow_fallbacks": False}, r.stderr[-300:])
r = comp(E("E1"), "black-forest-labs/flux.2-pro")
check("API v1: ключи результата сохранены", all(k in r for k in ("model", "family", "dialect", "prompt", "chars", "limit", "params", "errors", "warnings")))

# --- 2. ценовые параметры явно (B §4) и каталог той же библиотекой
r = comp(E("E1"), "google/gemini-3.1-flash-image-preview")
check("NB2: image_resolution из спецификации (2K)", r["params"].get("image_resolution") == "2K", r["params"])
r = comp(B("B1"), "google/gemini-3.1-flash-image-preview")
check("NB2: без resolution в спецификации — явно самая дешёвая 1K", r["params"].get("image_resolution") == "1K", r["params"])
r = comp(E("E2"), "bytedance/seedream-4.5")
check("Seedream 4.5: quality явно (basic = 2K)", r["params"].get("quality") == "basic", r["params"])
e4 = E("E4")
r = comp(e4, "kling/v3")
check("Kling 3: mode std, sound false, aspect 16:9 явно", r["params"].get("mode") == "std" and r["params"].get("sound") == "false" and r["params"].get("aspect_ratio") == "16:9", r["params"])
r = comp(e4, "google/veo3_fast")
check("Veo: FIRST_AND_LAST_FRAMES_2_VIDEO и enableTranslation false для английского", r["params"].get("generationType") == "FIRST_AND_LAST_FRAMES_2_VIDEO" and r["params"].get("enableTranslation") == "false", r["params"])
check("цена по каталогу (polza_catalog.estimate): Veo Fast 45 ₽", r["price_rub"] == 45.0, r["price_rub"])
r = fx("v2-loop", "bytedance/seedance-1.5-pro")
check("Seedance 1.5 Pro: 480p, 4 с, звук и fixed_lens явно; 5,25 ₽", r["params"].get("resolution") == "480p" and r["params"].get("generate_audio") == "false" and r["params"].get("fixed_lens") == "true" and r["price_rub"] == 5.25, (r["params"], r["price_rub"]))
check("Seedance 1.5 Pro: images = [первый, последний] кадр", len(r["images"]) == 2 and r["images"][0].endswith("frame-A.png"), r["images"])
check("каталог без ошибок (validate polza_catalog)", not [i for i in r["catalog_issues"] if i["level"] == "error"], r["catalog_issues"])

# --- 3. видео-промт: фон, неподвижное, запреты, темп
p = r["prompt"]
check("i2v: только движение — сцены нет", "ceramic cup of tea on a sunlit" not in p and "warm white" not in p, p)
check("фоновое движение по элементам", "Thin steam from the cup rises slowly" in p and "The sheer curtain sways gently" in p, p)
check("неподвижное перечислено", "the cup, the windowsill and the window frame stay perfectly still" in p.lower(), p)
check("запреты предложениями у Seedance (sentence)", "No zoom. No spin. Do not reposition the subject." in p, p)
check("темп словами", "All movement is slow and gentle." in p, p)
r = fx("v2-loop", "grok-imagine-video-1-5")
check("Grok: FLF не документирован → i2v, одна картинка", len(r["images"]) == 1 and r["mode"] == "i2v", r["images"])
check("запреты утвердительно у Grok (positive)", "The focal length stays fixed." in r["prompt"] and "No zoom" not in r["prompt"], r["prompt"])
s = F("v2-loop"); s["motion"]["duration_s"] = 5
r = comp(s, "wan/2.5", spec_path=FX / "v2-loop.spec.json")
check("Wan 2.5 (images ≤ 1): FLF → i2v, одна картинка, предупреждение", len(r["images"]) == 1 and any("последний кадр" in w and "i2v" in w for w in r["warnings"]) and not r["errors"], (r["images"], r["errors"]))
r = fx("v2-loop", "minimax/hailuo-3-max", "ir")
check("H3 IR: длительность 4 с отвергнута (5–15)", any("длительность 4" in e for e in r["errors"]), r["errors"])
s = F("v2-loop"); s["motion"]["duration_s"] = 5; s["motion"]["end_frame"] = None; s["motion"].pop("end_frame"); s["motion"]["loop"] = "none"
r = comp(s, "minimax/hailuo-3-max", "ir", spec_path=FX / "v2-loop.spec.json")
check("H3 IR: I2VA-строка для одного кадра, позитивные запреты", r["prompt"].startswith("For the target video, at 0.00 seconds") and "The subject keeps its orientation." in r["prompt"], r["prompt"][:300])
s = F("v2-loop"); s["motion"]["camera"] = {"move": "dolly-in", "amplitude": "small", "speed": "slow"}; s["motion"]["forbid"] = ["spin"]
s["motion"]["start_frame"] = None; s["motion"].pop("start_frame"); s["motion"].pop("end_frame"); s["motion"]["loop"] = "none"; s["motion"]["duration_s"] = 5
r = comp(s, "minimax/hailuo-3-max", "ir")
check("H3: камера «тип + амплитуда + скорость»", "The camera pushes in with small amplitude at slow speed." in r["prompt"], r["prompt"][:400])
s = F("v2-loop"); s["motion"]["forbid"] = ["zoom"]; s["motion"]["camera"] = {"move": "zoom-in"}
check("противоречие: запрет zoom + zoom-in", any("запрет zoom" in e for e in pc.validate_spec(s, None, D, C)[0]))
s = F("v2-loop"); s["motion"]["subject_motion"] = "cinematic 4K slow steam"
check("линт: слова качества в движении", any("слова качества" in w for w in pc.validate_spec(s, None, D, C)[1]))
r = fx("v2-loop", "bytedance/seedance-1.5-pro", options={"quality_words": True})
check("плечо A/B: стопка слов качества добавляется опцией", "Cinematic, 4K, masterpiece" in r["prompt"], r["prompt"])

# --- 4. мульти-шот
r = fx("v2-shots", "kling/v3")
check("Kling: «shot 1, 4, …; shot 2, 6, …;»", "shot 1, 4, wide shot, the potter centers" in r["prompt"] and "shot 2, 6, close-up" in r["prompt"], r["prompt"])
r = fx("v2-shots", "wan/2.6")
check("Wan 2.6: «Shot 1 [0–4 s]» и multi_shots=true", "Shot 1 [0–4 s]" in r["prompt"] and r["params"].get("multi_shots") == "true", (r["prompt"], r["params"]))
s = F("v2-shots"); s["motion"]["shots"][1]["t1"] = 9
check("мульти-шот: сумма планов ≠ длительности → ошибка", any("сумма планов" in e for e in pc.validate_spec(s, None, D, C)[0]))

# --- 5. правка
r = fx("v2-edit", "qwen/image-2.1")
p = r["prompt"]
check("правка: перечень «что → на что» + целевое значение + положение и размер", "Change only these elements: the armchair upholstery in the right third to deep green velvet (#1F5E3B); the throw pillow to a darker pillow." in p and "Keep their positions and sizes exactly the same." in p, p)
check("правка: что видно, что сохранить, суффикс", "After the change, the frame shows" in p and "Keep the camera angle, window light and floor shadows unchanged." in p and "Maintain the original composition and subject." in p, p)
check("линт: сравнительная правка без value", any("сравнительная" in w for w in r["warnings"]), r["warnings"])
check("маска Qwen: файл белое=менять → без инверсии; images = [исходник]", r["mask"] and r["mask"]["invert"] is False and len(r["images"]) == 1, r["mask"])
r = fx("v2-edit", "openai/gpt-5-image")
check("маска GPT-5 Image (polza): чёрное=менять → инверсия", r["mask"] and r["mask"]["invert"] is True and r["mask"]["model_polarity"] == "black=change", r["mask"])
with tempfile.TemporaryDirectory() as td:
    dst = pc.derive_mask(r["mask"], td)
    from PIL import Image
    a = Image.open(FX / "mask-white-change.png").convert("L").getpixel((50, 10)); b = Image.open(dst).convert("L").getpixel((50, 10))
    check("derive_mask: пиксели инвертированы", a == 255 and b == 0, (a, b))
r = fx("v2-edit", "google/gemini-3.1-flash-image-preview")
check("Nano Banana: закрывающая фраза Google + суффикс", "Maintain the original composition and subject." in r["prompt"] and "Keep everything else in the image exactly the same" in r["prompt"], r["prompt"])
check("Nano Banana: маска не поддерживается → ошибка", any("маска не поддерживается" in e for e in r["errors"]), r["errors"])
s = F("v2-edit"); s["edit"]["changes"] = [{"target": f"object {i}", "to": f"thing {i}"} for i in range(7)]; s["edit"].pop("mask")
r = comp(s, "openai/gpt-image-2.5-sunburst", spec_path=FX / "v2-edit.spec.json")
check("правка: 7 изменений > 5 → ошибка", any("7 изменений > 5" in e for e in r["errors"]), r["errors"])
check("chain: 7 изменений → 2 шага (5 + 2)", [len(x["edit"]["changes"]) for x in pc.edit_chain(s, D)] == [5, 2])

# --- 6. референсы, продукт, серия
r = fx("v2-series", "gpt-image-2-5-flare", "prose")
check("GPT Image: «Image 1 is the style reference: match its line weight and palette only»", "Image 1 is the style reference: match its line weight and palette only" in r["prompt"], r["prompt"][:300])
check("серия: блок первым, против «среднего» — позитивом", r["prompt"].startswith("Flat vector illustration") and "Off-center subject" in r["prompt"], r["prompt"][:200])
r = fx("v2-series", "black-forest-labs/flux.2-pro")
check("FLUX.2: ссылка на референс по номеру (image 1)", "image 1 is the style reference" in r["prompt"].lower(), r["prompt"][:300])
s = F("v2-series"); s["references"][0]["role"] = "identity"
r = comp(s, "bytedance/seedance-2-mini", spec_path=FX / "v2-series.spec.json") if False else None
r = fx("v2-product", "openai/gpt-image-2.5-sunburst", "prose", options={"order": "product7"})
p = r["prompt"]
check("7 блоков: композиция → идентичность → типографика → цвета → свет → оптика", p.find("Close-up") < p.find("The product is") < p.find("The label reads") < p.lower().find("the cap is black") < p.find("Soft window daylight") < p.find("85mm"), p)
check("типографика: «no misspellings…» (sentence)", "No misspellings, no extra letters, and no warped glyphs." in p, p)
r = fx("v2-product", "black-forest-labs/flux.2-pro")
check("FLUX.2: строгая орфография позитивом", "Every letter is spelled exactly as written" in r["prompt"] and "No misspellings" not in r["prompt"], r["prompt"])

s1 = F("v2-edit"); s1["edit"]["changes"] = s1["edit"]["changes"][:1]
r1 = comp(s1, "qwen/image-2.1", spec_path=FX / "v2-edit.spec.json")
check("правка из одного изменения: «Change only the …» + «Keep its position and size…»", "Change only the armchair upholstery in the right third to deep green velvet (#1F5E3B)." in r1["prompt"] and "Keep its position and size exactly the same." in r1["prompt"], r1["prompt"])

# --- 7. рычаги A/B формы при неизменном содержании
b1 = B("B1")
full = comp(b1, "google/gemini-3.1-flash-lite-image", "prose")["prompt"]
shuf = comp(b1, "google/gemini-3.1-flash-lite-image", "prose", options={"order": "shuffled", "shuffle_seed": 7})["prompt"]
short = comp(b1, "google/gemini-3.1-flash-lite-image", "prose", options={"length": "short"})["prompt"]
check("перемешанный порядок: те же предложения, другой порядок", sorted(full.split(". ")) == sorted(shuf.split(". ")) and full != shuf)
check("короткий профиль короче в ≥ 1,8 раза", len(full) / len(short) >= 1.8, (len(full), len(short)))
check("зона текста: шаблон Google «vast, empty»", "vast, empty" in comp(b1, "google/gemini-3.1-flash-lite-image", "prose", options={"text_zone_style": "google"})["prompt"])
check("зона текста: «copy space»", "Copy space on the left." in comp(b1, "google/gemini-3.1-flash-lite-image", "prose", options={"text_zone_style": "copyspace"})["prompt"])
r = comp(b1, "black-forest-labs/flux.2-pro", "prose", options={"negation": "sentence"})
check("плечо «no X»: FLUX.2 получает «No people.»", "No people." in r["prompt"] and "No people." not in comp(b1, "black-forest-labs/flux.2-pro")["prompt"])
check("палитра names: у FLUX.2 без hex", "#" not in comp(b1, "black-forest-labs/flux.2-pro", "prose", options={"palette_form": "names"})["prompt"])
check("палитра hex: у Nano Banana с hex", "#D9D4CC" in comp(b1, "google/gemini-3.1-flash-lite-image", "prose", options={"palette_form": "hex"})["prompt"])
r = comp(b1, "tongyi-mai/z-image", "prose", options={"fit": "drop"})
check("бюджет длины: Z-Image B1 ужат до 1000 выбросом блоков", r["chars"] <= 1000 and not r["errors"] and r["dropped_blocks"], (r["chars"], r["dropped_blocks"], r["errors"]))
check("по умолчанию fit=fail: ошибка без обрезки (как v1)", any("> 1000" in e for e in comp(b1, "tongyi-mai/z-image")["errors"]))
r = comp(b1, "qwen/image-2.1", "prose", options={"enhancer": "on"})
check("плечо enhance_prompt=true (D-9)", r["params"].get("enhance_prompt") is True, r["params"])

# --- 8. язык
s = B("B1"); s["subject"]["summary"] = "уютный уголок для чтения"
check("кириллица в описании → ошибка", any("кириллица в описательных" in e for e in pc.validate_spec(s, None, D, C)[0]))
check("compile.language=ru → без ошибки (плечо RU)", not any("кириллица в описательных" in e for e in pc.validate_spec(s, None, D, C, options={"language": "ru"})[0]))
s = E("E4"); s["motion"]["subject_motion"] = "Пар поднимается"
r = comp(s, "google/veo3_fast", options={"language": "ru"})
check("Veo: кириллица → enableTranslation true + предупреждение", r["params"].get("enableTranslation") == "true" and any("Veo: кириллица" in w for w in r["warnings"]), r["params"])

# --- 9. каналы RouterAI / Gen-API
r = comp(B("B1"), "black-forest-labs/flux.2-pro", "json", channel="routerai", options={"seed": 101})
check("RouterAI FLUX.2 Pro: seed есть, disable_pup нет", r["body"].get("seed") == 101 and "disable_pup" not in r["body"] and not r["errors"], r["body"].keys())
r = comp(B("B1"), "black-forest-labs/flux.2-pro", "prose", channel="routerai", options={"seed": 101, "extra_body": {"disable_pup": True}})
check("RouterAI: passthrough disable_pup помечен гипотезой", r["body"].get("disable_pup") is True and any("passthrough" in w for w in r["warnings"]) and not r["errors"])
r = comp(B("B1"), "flux-2", "prose", channel="genapi", options={"seed": 202})
bd = r["body"]
check("Gen-API FLUX.2 [dev]: expansion off, translate off, ≤ 1 Мп, seed", bd.get("enable_prompt_expansion") is False and bd.get("translate_input") is False and bd["width"] * bd["height"] <= 1_000_000 and bd.get("seed") == 202, bd)
r = comp(B("B1"), "bria-fibo", "fibo_json", channel="genapi", options={"seed": 101})
sp = r["body"].get("structured_prompt") or {}
check("Gen-API Bria FIBO: structured_prompt с ключами схемы", list(sp)[:3] == ["short_description", "objects", "background_setting"] and "lighting" in sp and r["body"].get("model") == "generate", list(sp))

# --- 10. соотношения и серия
s = E("E1")
s["output"]["aspect_ratios"] = ["16:9", "4:5", "9:16", "21:9"]
v = {x["ratio"]: x for x in pc.ratio_variants(s)}
check("кадр 4:5 из 16:9 содержит безопасную зону и фокус", v["4:5"]["strategy"] == "crop" and v["4:5"]["crop_box"][0] <= 0.5 and v["4:5"]["crop_box"][2] >= 0.95, v["4:5"])
check("9:16 из 16:9: кадр 0,316 уже зоны E1 (0,35) → аутпейнт", v["9:16"]["strategy"] == "outpaint" and v["9:16"]["crop_box"] is None, v["9:16"])
s2 = E("E1"); s2["output"]["aspect_ratios"] = ["9:16"]; s2["composition"]["safe_zones"] = [{"ratio": "9:16", "keep_rect": [0.6, 0.15, 0.9, 0.95]}]
bx = pc.ratio_variants(s2)[0]["crop_box"]
check("9:16 из 16:9 при зоне 0,30: ширина 0,316, зона внутри", bx and abs(bx[2] - bx[0] - 0.3164) < 0.001 and bx[0] <= 0.6 and bx[2] >= 0.9, bx)
s["composition"]["safe_zones"].append({"ratio": "21:9", "keep_rect": [0.1, 0.0, 0.9, 1.0]})
check("21:9 не вмещает зону по высоте → аутпейнт", {x["ratio"]: x for x in pc.ratio_variants(s)}["21:9"]["strategy"] == "outpaint")
with tempfile.TemporaryDirectory() as td:
    a = F("v2-series"); b_ = F("v2-series"); b_["id"] = "t-series-3"; b_["series"]["block"] += " Extra."
    pa, pb = pathlib.Path(td) / "a.spec.json", pathlib.Path(td) / "b.spec.json"
    pa.write_text(json.dumps(a)); pb.write_text(json.dumps(b_))
    jobs, skipped = pc.make_jobs([pa, pb], ["qwen/image-2.1"], ["prose"], 1, (101,), "t", allow_missing_inputs=True)
    check("серия: перефразированный блок → задание пропущено", len(jobs) == 1 and any("блок стиля отличается" in e for s_ in skipped for e in s_["errors"]), skipped)

# --- 11. устойчивость
r = comp(E("E4"), "black-forest-labs/flux.2-pro", "json")
check("JSON + motion на модели картинок: ошибка, а не исключение (v1 падал)", r["errors"] and isinstance(r["prompt"], str))
s = E("E4"); s["motion"]["timeline"] = [{"t0": 0, "t1": 2, "beat": "steam starts to rise"}]
check("Veo: таймкод «[00:00-00:02]»", "[00:00-00:02] steam starts to rise" in comp(s, "google/veo3_fast")["prompt"])
check("Omni: теги петли сохранены", comp(E("E4"), "gemini-omni-video")["prompt"].startswith("[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]"))

# --- 12. снимок каталога, GA Omni, референсы одной роли, смешанные правки, проверки видео
check("снимок каталога — последний (find_snapshot), путь в паспорте", pc.snapshot_dir().name >= "2026-09-23_1745"
      and comp(E("E1"), "black-forest-labs/flux.2-pro")["passport"]["catalog_snapshot"].endswith(f"{pc.snapshot_dir().name}/api-v1-models.json"), pc.snapshot_dir())
r = fx("v2-loop", "google/gemini-omni-1.1-flash")
check("GA Omni: петля — first_frame_url = last_frame_url, images пусты, 48 ₽", r["frame_fields"].get("first_frame_url", "").endswith("frame-A.png")
      and r["frame_fields"].get("last_frame_url") == r["frame_fields"].get("first_frame_url") and not r["images"] and r["price_rub"] == 48.0
      and not r["errors"], (r["frame_fields"], r["images"], r["price_rub"], r["errors"]))
check("GA Omni: без тегов preview, с фразой одного плана", not r["prompt"].startswith("[# Sources") and "Use this image as the first frame" not in r["prompt"]
      and "In a single continuous shot. No scene cuts." in r["prompt"], r["prompt"][:200])
check("preview Omni: теги петли по-прежнему", fx("v2-loop", "gemini-omni-video")["prompt"].startswith("[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]"))
s = F("v2-loop"); s["references"] = [{"src": "style-ref.png", "role": "video_motion", "kind": "video"}]
check("GA Omni: кадры + видео-референс → ошибка (поля не сочетаются)", any("не сочетается" in e for e in comp(s, "google/gemini-omni-1.1-flash", spec_path=FX / "v2-loop.spec.json")["errors"]))
with tempfile.TemporaryDirectory() as td:
    jobs, skipped = pc.make_jobs([FX / "v2-loop.spec.json"], ["google/gemini-omni-1.1-flash"], ["prose"], 1, (101,), "t", out_path=pathlib.Path(td) / "j.jsonl")
    j0 = jobs[0]["input"] if jobs else {}
    check("GA Omni: в задании поля *_url и meta.url_fields/prepare", "first_frame_url" in j0 and "images" not in j0 and j0.get("seed") == 101
          and jobs[0]["meta"].get("url_fields") and "upload" in jobs[0]["meta"].get("prepare", ""), (j0.keys(), skipped))
s = F("v2-series"); s["references"] = [dict(s["references"][0], id=f"s{i}") for i in (1, 2, 3)]
r = comp(s, "black-forest-labs/flux.2-pro", spec_path=FX / "v2-series.spec.json")
check("F2 (1): три стилевых референса — одна фраза «Images 1-3 are style references»", "Images 1-3 are style references from one shoot" in r["prompt"]
      and r["prompt"].lower().count("style reference") == 1, r["prompt"][:400])
s2 = F("v2-series"); s2["references"] = [dict(s2["references"][0], id="a"), dict(s2["references"][0], id="b", role="palette", note="colors only")]
r = comp(s2, "openai/gpt-image-2.5-sunburst", "prose", spec_path=FX / "v2-series.spec.json")
check("разные роли — по фразе на референс (Image 1 стиль, Image 2 палитра)", "Image 1 is the style reference" in r["prompt"] and "Take only the color palette from Image 2" in r["prompt"], r["prompt"][:400])
b1 = B("B1"); b1["exclusions"] = b1.get("exclusions", []) + [{"what": "signs", "kind": "artifact", "replace_with": "clean unmarked surfaces"}]
check("F2 (2): «clean unmarked surfaces» не повторяется", comp(b1, "black-forest-labs/flux.2-pro")["prompt"].count("clean unmarked surfaces") == 1)
b1 = B("B1"); b1["composition"]["text_zone"]["surface"] = "a long, evenly lit lawn"
p = comp(b1, "black-forest-labs/flux.2-pro")["prompt"]
check("F2 (3): поверхность зоны без артикля", "uncluttered long, evenly lit lawn" in p and "uncluttered a long" not in p, p[:600])
s = F("v2-series"); s["series"]["block"] = "Series style: flat vector illustration, two colors, thin even lines."
p = comp(s, "openai/gpt-image-2.5-sunburst", "sections", spec_path=FX / "v2-series.spec.json")["prompt"]
check("F2 (4): блок «Series style: …» без второй метки", p.startswith("Series style: flat vector") and "Series style (keep identical): Series style" not in p, p[:120])
s = F("v2-edit"); s["edit"].pop("mask"); s["edit"]["changes"] = [{"target": "armchair upholstery", "to": "deep green velvet", "value": "#1F5E3B"},
                                                               {"op": "add", "target": "fern", "to": "a small potted fern", "where": "on the window sill"},
                                                               {"op": "remove", "target": "floor lamp", "to": "the bare wall"}]
p = comp(s, "google/gemini-3.1-flash-image-preview", spec_path=FX / "v2-edit.spec.json")["prompt"]
check("смешанная правка: свои глаголы (change / add / remove)", "make only these changes: change the armchair upholstery to deep green velvet (#1F5E3B); add a small potted fern on the window sill; remove the floor lamp, showing the bare wall in its place." in p
      and "change the window sill" not in p, p[:400])
s = F("v2-shots"); s["motion"]["shots"][1]["action"] = "x" * 520
check("Kling: план > 512 символов → ошибка", any("> 512" in e for e in comp(s, "kling/v3", spec_path=FX / "v2-shots.spec.json")["errors"]))
s = F("v2-shots"); s["motion"]["start_frame"] = "frame-A.png"; s["motion"]["end_frame"] = "frame-A.png"
check("Kling: мульти-шот + последний кадр → ошибка", any("только стартовый кадр" in e for e in comp(s, "kling/v3", spec_path=FX / "v2-shots.spec.json")["errors"]))
s = F("v2-loop"); s["motion"]["camera"]["target"] = "the steaming cup"
check("Kling: цель неподвижной камеры", "The camera remains fixed on the steaming cup." in fx("v2-loop", "kling/v3")["prompt"].replace("the subject", "the steaming cup") and
      "The camera remains fixed on the steaming cup." in comp(s, "kling/v3", spec_path=FX / "v2-loop.spec.json")["prompt"])
s = E("E4"); s["motion"].pop("end_frame"); s["motion"]["loop"] = "none"; s["references"] = s["references"][:1]; s["motion"]["duration_s"] = 5
s["motion"]["timeline"] = [{"t0": 0, "t1": 2, "beat": "steam rises"}, {"t0": 3, "t1": 5, "beat": "the curtain sways"}]
r = comp(s, "bytedance/seedance-2-5")
check("Seedance 2.5: разрыв в таймлайне → предупреждение", any("разрывы" in w for w in r["warnings"]), r["warnings"])
s["motion"].pop("timeline")
check("Wan 2.5: звук не выключается параметром → предупреждение -an", any("-an" in w for w in comp(s, "wan/2.5")["warnings"]))
check("Seedance 1.5 Pro: звук параметром — без предупреждения -an", not any("-an" in w for w in fx("v2-loop", "bytedance/seedance-1.5-pro")["warnings"]))
check("GA Omni: запрос 480p → 720p (цена та же, 48 ₽), а не 360p", fx("v2-loop", "google/gemini-omni-1.1-flash")["params"].get("resolution") == "720p")
check("Seedance 1.5 Pro: точная ступень 480p не меняется", fx("v2-loop", "bytedance/seedance-1.5-pro")["params"].get("resolution") == "480p")
s = F("v2-shots")
p_ = comp(s, "wan/2.6", spec_path=FX / "v2-shots.spec.json")["prompt"]
check("планы и отрезки — законченными предложениями (точка перед следующим планом)", "on the wheel. Shot 2 [4–10 s]" in p_ and "bowl wall. " in p_, p_)
p_ = comp(s, "gemini-omni-video", spec_path=FX / "v2-shots.spec.json")["prompt"]
check("видео: запреты последними (Omni: «No text.» в конце)", p_.rstrip().endswith("No text."), p_)
s = F("v2-series")
p_ = fx("v2-series", "gpt-image-2-5-flare", "prose")["prompt"]
check("«против среднего» у иллюстрации предмета: без «gaze» и «natural imperfections»", "Off-center subject placed on a rule-of-thirds line, asymmetric composition." in p_
      and "gaze" not in p_ and "imperfections" not in p_, p_[:400])
s["composition"]["subject_region"] = "center"
check("«против среднего» + субъект по центру → ошибка", any("против среднего" in e for e in pc.validate_spec(s, None, D, C)[0]))
s = F("v2-series"); s["subject"]["summary"] = "a woman reading on a bench"; s["series"]["block"] = "Documentary photograph of a city park."
check("«против среднего» у фото с человеком: взгляд и несовершенства", "gaze turned away from the camera, natural imperfections." in comp(s, "gpt-image-2-5-flare", "prose", spec_path=FX / "v2-series.spec.json")["prompt"])
r = comp(B("B1"), "grok-imagine-image-2-0/text-to-image")
check("Grok Image 2.0 (снимок 17:45) компилируется: 16:9, 3 ₽", r["params"].get("aspect_ratio") == "16:9" and r["price_rub"] == 3.0 and not r["errors"], (r["params"], r["price_rub"], r["errors"]))

# --- 13. задания по умолчанию и команды без снимка каталога
jobs, skipped = pc.make_jobs([FX / "D03/B2.spec.json"], ["openai/gpt-image-2.5-sunburst"])
j0 = jobs[0] if jobs else {}
check("jobs по умолчанию: одно задание — диалект семейства, вариант 1, без seed, тега и агента",
      len(jobs) == 1 and not skipped and j0["meta"]["dialect"] == pc.family_of("openai/gpt-image-2.5-sunburst", D)[1]["format"]
      and j0["variant"] == 1 and "seed" not in j0["input"] and "agent" not in j0 and j0["tag"].startswith("ab-b2-illustr-"),
      (len(jobs), skipped, j0.get("tag")))
with tempfile.TemporaryDirectory() as td:
    out = pathlib.Path(td) / "one.jsonl"
    r = cli("jobs", str(FX / "D03/B2.spec.json"), "--models", "openai/gpt-image-2.5-sunburst", "--out", str(out))
    lines = out.read_text().splitlines() if out.exists() else []
    check("CLI jobs без ключей формы: 1 задание", len(lines) == 1 and "заданий: 1" in r.stderr, r.stderr[-200:])
    env = {k: v for k, v in os.environ.items() if k != "POLZA_CATALOG"}
    env["DDD_HOME"] = td
    run = lambda *a: subprocess.run([py, str(TOOLS / "prompt_compile.py"), *a], capture_output=True, text=True, env=env)
    e1 = str(FX / "D02/E1.spec.json")
    rs = [run("--help"), run("ratios", e1), run("validate", e1)]
    check("без снимка каталога: --help, ratios и validate без --model — код 0", all(x.returncode == 0 for x in rs),
          [(x.returncode, x.stderr[-160:]) for x in rs])
    rs = [run("validate", e1, "--model", "openai/gpt-image-2.5-sunburst"), run("compile", e1, "--model", "openai/gpt-image-2.5-sunburst")]
    check("без снимка каталога: validate --model и compile — код 2 и строка с командой установки",
          all(x.returncode == 2 and "нет снимков" in x.stderr and "install.sh --catalogs" in x.stderr for x in rs),
          [(x.returncode, x.stderr[-200:]) for x in rs])

ok = sum(x[1] for x in R)
verbose = "-v" in sys.argv
for n, c, i in R:
    if verbose or not c:
        print(f"[{'OK' if c else 'FAIL'}] {n}" + ("" if c else f" — {str(i)[:300]}"))
print(f"ИТОГ: {ok}/{len(R)} пройдено")
sys.exit(0 if ok == len(R) else 1)
