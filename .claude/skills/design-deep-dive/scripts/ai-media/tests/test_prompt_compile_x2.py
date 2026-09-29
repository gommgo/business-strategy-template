#!/usr/bin/env python3
"""Офлайн-тесты prompt_compile.py на спецификациях демо `kb/ai-media/14-recipes/examples/demo-landing`: поверхность
зоны текста, `edit.keep`, заглавная в движении, «Keep its position…» только после замены объекта, `ratios` без
safe_zone, `focal_point` не объектом. Основные тесты — test_prompt_compile.py; нужен снимок каталога polza.
Запуск: $DDD_HOME/venv/bin/python scripts/ai-media/tests/test_prompt_compile_x2.py [-v]"""
import copy, pathlib, sys
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
M = lambda n: pc.load_json(ROOT / "14-recipes/examples/demo-landing/brand/specs" / f"{n}.spec.json")
comp = lambda spec, m, d=None, **kw: pc.compile_prompt(spec, m, d, D, C, **kw)
R = []


def check(name, cond, info=""):
    R.append((name, bool(cond), info))


# 1. поверхность зоны с «empty…» — без повтора (M: «an empty, uncluttered empty cream plaster wall»)
s = M("M-01-hero-16x9-2k")
s["composition"]["text_zone"]["surface"] = "empty, uncluttered evenly lit cream plaster wall"
p = comp(s, "openai/gpt-image-2.5-sunburst")["prompt"]
check("зона: «empty, uncluttered» в поверхности не повторяется (GPT, позитивные замены)",
      "empty, uncluttered evenly lit cream plaster wall" in p and "uncluttered empty" not in p and "empty, uncluttered empty" not in p, p[:400])
s["composition"]["text_zone"]["surface"] = "an empty cream wall"
ok = True
for mid in ("google/gemini-3.1-flash-image-preview", "black-forest-labs/flux.2-pro", "bytedance/seedream-4"):
    p = comp(s, mid)["prompt"]
    ok &= "empty empty" not in p and "uncluttered empty" not in p and "empty, uncluttered cream wall" in p
check("зона: артикль и «empty» в поверхности срезаются (NB2, FLUX.2, Seedream)", ok, p[:400])
s["composition"]["text_zone"]["surface"] = "empty"
p = comp(s, "openai/gpt-image-2.5-sunburst")["prompt"]
check("зона: поверхность из одного «empty» не превращается в пустую строку", " , " not in p and "empty" in p, p[:400])

# 2. edit.keep с артиклем — без «the the»
s = M("M-06-hero-evening-edit")
s["edit"]["keep"] = ["the cup", "the napkin", "camera angle"]
p = comp(s, "openai/gpt-image-2.5-sunburst")["prompt"]
check("keep: «Keep the the cup» → «Keep the cup, the napkin and camera angle unchanged»",
      "the the" not in p and "Keep the cup, the napkin and camera angle unchanged." in p, p[-400:])
s["edit"]["keep"] = ["all other objects"]
p = comp(s, "openai/gpt-image-2.5-sunburst")["prompt"]
check("keep: местоимение/квантор без «the» («Keep all other objects unchanged»)", "Keep all other objects unchanged." in p, p[-300:])

# 3. subject_motion со строчной — с заглавной после точки
s = M("M-07b-floating-beans-loop")
s["motion"]["subject_motion"] = "the beans turn slowly around their long axes"
p = comp(s, "bytedance/seedance-1.5-pro")["prompt"]
check("движение: «… still. the beans» → «The beans turn slowly …»", "The beans turn slowly around their long axes." in p and ". the beans" not in p, p[:300])

# 4. «Keep its position…» — только после замены объекта
p = comp(M("M-06-hero-evening-edit"), "openai/gpt-image-2.5-sunburst")["prompt"]
check("relight с change.op=replace: без «Keep its position and size exactly the same»", "Keep its position" not in p and p.startswith("Relight the scene"), p[:300])
s = F("v2-edit"); s["edit"]["changes"] = s["edit"]["changes"][:1]; s["edit"]["operation"] = "replace"
p = comp(s, "openai/gpt-image-2.5-sunburst", spec_path=FX / "v2-edit.spec.json")["prompt"]
check("replace одного объекта: «Keep its position…» остаётся", "Keep its position and size exactly the same." in p, p[:400])

# 5. ratios: без safe_zone — кроп по фокусу/зоне текста, варианты выводятся
v = {x["ratio"]: x for x in pc.ratio_variants(M("M-01-hero-16x9-2k"))}
check("ratios M-01: 40:21 из 16:9 — кроп (−6,67 % высоты), не аутпейнт", v["40:21"]["strategy"] == "crop" and abs(v["40:21"]["crop_box"][1] - 0.0667) < 1e-3, v["40:21"])
check("ratios M-01: вариант 4:5 generate из output.variants выводится", v.get("4:5", {}).get("strategy") == "generate", list(v))
v = {x["ratio"]: x for x in pc.ratio_variants(M("M-02-hero-phone-3x4-2k"))}
check("ratios M-02: 4:5 из 3:4 режет низ, зона текста сверху цела", v["4:5"]["crop_box"] == [0.0, 0.0, 1.0, 0.9375] and "зоне текста" in v["4:5"]["note"], v["4:5"])
v = {x["ratio"]: x for x in pc.ratio_variants(E("E1"))}
check("ratios E1: safe_zone по-прежнему главнее (4:5 — [0,5; 0,95], 9:16 — аутпейнт)",
      v["4:5"]["crop_box"] == [0.5, 0.0, 0.95, 1.0] and v["9:16"]["strategy"] == "outpaint", v)

# 6. focal_point списком — ошибка схемы, не TypeError
s = M("M-01-hero-16x9-2k"); s["composition"]["focal_point"] = [0.74, 0.62]
try:
    errs, _ = pc.validate_spec(s, "openai/gpt-image-2.5-sunburst", D, C)
    ok = any("focal_point" in e for e in errs)
except TypeError as e:
    ok, errs = False, [repr(e)]
check("focal_point [x, y]: validate_spec — ошибка схемы, без TypeError", ok, errs[:2])
try:
    r = comp(s, "openai/gpt-image-2.5-sunburst")
    ok = bool(r["errors"]) and any("focal_point" in e for e in r["errors"])
except TypeError as e:
    ok, r = False, {"errors": [repr(e)]}
check("focal_point [x, y]: compile_prompt возвращает ошибку, не падает", ok, r["errors"][:2])
try:
    v = pc.ratio_variants(s); ok = all("crop_box" in x for x in v)
except (TypeError, AttributeError) as e:
    ok, v = False, repr(e)
check("focal_point [x, y]: ratios не падает (кадр по центру, пометка)", ok and "не объект" in v[1]["note"], v)

bad = [x for x in R if not x[1]]
for n, c, i in R:
    if not c or "-v" in sys.argv:
        print(f"[{'OK' if c else 'FAIL'}] {n}" + ("" if c else f" — {i}"))
print(f"ИТОГ: {len(R) - len(bad)}/{len(R)} пройдено")
sys.exit(1 if bad else 0)
