#!/usr/bin/env python3
"""ad_check.py — опыты A/01 и A/02: проверка примеров art-direction (2026-09-24).

1. Схема: examples/*.json против art-direction.schema.json (JSON Schema 2020-12).
2. Паспорт визуала: handoff.visual_dna.* против подсхем ../ai-media-research/06-art-direction-consistency/visual-dna.schema.json
   (character, palette.forbidden_hues, exclusions, abstract, video, composition, subject_matter, materials).
3. Правила, которые схема выразить не может: различие направлений (≥ 2 осей из 4), не больше одного тёплого или
   антиквенного направления, семейства территорий (≥ 3) и буквальные (≤ 1), ссылки (territory, chosen, merged_from),
   id макроструктур по словарю site, уровень ↔ эффекты ↔ движение ↔ плавная прокрутка, boldness ↔ уровень, профиль
   бюджета ↔ тип страницы и уровень, контраст палитр (WCAG 2), акцент в запретной полосе, id эффектов.
4. Сравнение «Лесная обжарка» L0 ↔ L2 (таблица), отрицательные случаи.
Запуск: 99-raw/tools/venv-A/bin/python 99-raw/experiments/A/01-art-direction-examples/ad_check.py → out/report.json.
"""
import copy, glob, json, os, sys
import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
APP = str(kbpaths.kb())  # перенос: kb/ (базы без -research)
CR = f"{APP}/creative"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = str(kbpaths.out("creative", "ad_check")); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: color.py — scripts/lib
from color import hex2oklch, wcag  # noqa: E402

AD = json.load(open(f"{CR}/01-creative-direction/art-direction.schema.json"))
VD = json.load(open(f"{APP}/ai-media/06-art-direction-consistency/visual-dna.schema.json"))
TR = json.load(open(f"{CR}/01-creative-direction/drafts-for-site/treatment.v0.schema.json"))
LV = yaml.safe_load(open(f"{CR}/01-creative-direction/ambition-levels.yaml"))
VOC = yaml.safe_load(open(f"{APP}/site/02-site-types/vocabulary.yaml"))["namespaces"]
MACRO = {x["id"]: x.get("layout_family") for x in VOC["macrostructure"]["values"]}
EFFECT_IDS = set(TR["x-effect-ids-v0"])
# списки запретов по уровню — из той же подсхемы treatment (одно место правды)
L0_FORBID = set(TR["allOf"][0]["then"]["properties"]["effects"]["items"]["properties"]["ref"]["not"]["enum"])
L1_FORBID = set(TR["allOf"][1]["then"]["properties"]["effects"]["items"]["properties"]["ref"]["not"]["enum"])
ORDER = {"L0": 0, "L1": 1, "L2": 2}
MOTION_MAX = {"L0": {"none", "subtle"}, "L1": {"none", "subtle", "expressive"}, "L2": {"none", "subtle", "expressive", "cinematic"}}
BOLD = {"L0": "restrained", "L1": "balanced", "L2": "bold"}

reg = Registry().with_resources([
    (AD["$id"], Resource.from_contents(AD, default_specification=DRAFT202012)),
    (VD["$id"], Resource.from_contents(VD, default_specification=DRAFT202012)),
])
V_AD = Draft202012Validator(AD, registry=reg)
VD_SUB = {
    "character": "#/properties/character", "palette_forbidden_hues": "#/properties/palette/properties/forbidden_hues",
    "exclusions": "#/properties/exclusions", "abstract": "#/properties/abstract", "video": "#/properties/video",
    "composition": "#/properties/composition", "subject_matter": "#/properties/subject_matter", "materials": "#/properties/materials",
}
V_VD = {k: Draft202012Validator({"$ref": VD["$id"] + p}, registry=reg) for k, p in VD_SUB.items()}

def errs(v, doc):
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:150]}" for e in v.iter_errors(doc)]

CORE = ["paper", "display_style", "accent_hue", "macrostructure"]

def cross(ad):
    E, W = [], []
    lvl = ad["ambition"]["level"]
    dirs = {d["id"]: d for d in ad["directions"]}
    # различие направлений
    ids = list(dirs)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = dirs[ids[i]]["axes"], dirs[ids[j]]["axes"]
            diff = [k for k in CORE if a.get(k) != b.get(k)]
            if len(diff) < 2:
                E.append(f"направления {ids[i]} и {ids[j]} различаются только по {diff or 'ни одной оси'} (нужно ≥ 2 из {CORE})")
    brand_words = " ".join(ad["inputs"].get("must_keep", [])).lower()
    warm_serif = [d["id"] for d in ad["directions"] if d["axes"].get("paper_temperature") == "warm" or d["axes"]["display_style"] == "serif"]
    if len(warm_serif) > 1 and not any(w in brand_words for w in ("антиква", "serif", "тёпл", "крем")):
        E.append(f"тёплая бумага или антиква у {len(warm_serif)} направлений {warm_serif} (≤ 1, kimi 03/04 T2a)")
    # территории
    terr = {t["id"]: t for t in ad["territories"]}
    fams = {t["family"] for t in ad["territories"] if not t.get("rejected_because")} or {t["family"] for t in ad["territories"]}
    if len({t["family"] for t in ad["territories"]}) < 3:
        E.append("территории из < 3 материальных семейств (impeccable new-work §3)")
    if sum(1 for t in ad["territories"] if t.get("literal")) > 1:
        E.append("буквальных прочтений > 1")
    for d in ad["directions"]:
        if d["territory"] not in terr:
            E.append(f"направление {d['id']}: территории {d['territory']} нет")
        m = d["axes"]["macrostructure"]
        if m not in MACRO:
            E.append(f"направление {d['id']}: макроструктуры {m} нет в словаре site")
        for pal_name, pal in (("palette", d["palette"]),):
            if wcag(pal["text"], pal["background"]) < 4.5:
                E.append(f"{d['id']}: текст/фон {wcag(pal['text'], pal['background']):.2f} < 4,5")
            if pal.get("on_accent") and wcag(pal["on_accent"], pal["accent"]) < 4.5:
                E.append(f"{d['id']}: текст на акценте {wcag(pal['on_accent'], pal['accent']):.2f} < 4,5")
        for e in d["signature_move"].get("effects", []):
            if e not in EFFECT_IDS:
                W.append(f"{d['id']}: эффект {e} вне временного списка x-effect-ids-v0")
    ch = ad.get("choice")
    if ch:
        if ch["chosen"] not in dirs:
            E.append(f"choice.chosen {ch['chosen']} нет среди направлений")
        for m in ch.get("merged_from", []):
            if m not in dirs:
                E.append(f"merged_from {m} нет среди направлений")
        chosen = dirs.get(ch["chosen"])
        if chosen:
            if lvl not in chosen["level_fit"]:
                E.append(f"выбранное направление {chosen['id']} не работает на уровне {lvl} (level_fit {chosen['level_fit']})")
            if ORDER[chosen["signature_move"].get("min_level", "L0")] > ORDER[lvl]:
                E.append(f"главный приём выбранного направления требует {chosen['signature_move']['min_level']} > {lvl}")
    # уровень ↔ эффекты ↔ движение
    for s in ad.get("effects_by_section", []):
        sl = s.get("level", lvl)
        if ORDER[sl] > ORDER[lvl]:
            E.append(f"эффекты секции {s['section']}: уровень {sl} выше страницы {lvl}")
        for e in s["effects"]:
            if sl == "L0" and e in L0_FORBID or sl == "L1" and e in L1_FORBID:
                E.append(f"эффект {e} запрещён на уровне {sl} (секция {s['section']})")
            if e not in EFFECT_IDS:
                W.append(f"эффект {e} вне временного списка x-effect-ids-v0")
    ms = ad.get("motion_system")
    if ms:
        if ms["level"] not in MOTION_MAX[lvl]:
            E.append(f"motion_system.level {ms['level']} выше допустимого для {lvl}")
        cap = ad["ambition"].get("motion_cap")
        order_m = ["none", "subtle", "expressive", "cinematic"]
        if cap and order_m.index(ms["level"]) > order_m.index(cap):
            E.append(f"motion_system.level {ms['level']} выше motion_cap {cap}")
        if ms.get("smooth_scroll") and lvl != "L2":
            E.append("плавная прокрутка вне L2")
        for b in ms.get("by_section", []):
            if b["motion_level"] not in MOTION_MAX[lvl]:
                E.append(f"движение секции {b['section']} {b['motion_level']} выше уровня {lvl}")
    # профиль бюджета
    bp = ad["ambition"]["budget_profile"]
    if bp != f"{ad['inputs']['page_type']}@{lvl}":
        E.append(f"budget_profile {bp} ≠ {ad['inputs']['page_type']}@{lvl}")
    # паспорт визуала
    vd = (ad.get("handoff") or {}).get("visual_dna") or {}
    if vd.get("character", {}).get("boldness") and vd["character"]["boldness"] != BOLD[lvl]:
        E.append(f"visual_dna boldness {vd['character']['boldness']} ≠ {BOLD[lvl]} для {lvl}")
    # акцент в запретной полосе
    vl = ad.get("visual_language", {}).get("palette")
    if vl:
        H = hex2oklch(vl["accent"])[2]
        for band in ad.get("exclusions", {}).get("forbidden_hues", []):
            if band["from"] <= H <= band["to"]:
                W.append(f"акцент {vl['accent']} (H {H:.0f}°) внутри запретной полосы {band['from']}–{band['to']}°")
    # приметы K3: каждая разрешённая — с обоснованием
    allowed = set(ad.get("exclusions", {}).get("k3_allow", []))
    justified = {d.get("k3_allow") for d in ad.get("decisions", []) if d.get("k3_allow")}
    for k in allowed - justified:
        W.append(f"--allow {k} без решения (decisions[].k3_allow)")
    return E, W

report = {"examples": {}, "negative": [], "compare": None}
fails = []
examples = sorted(glob.glob(f"{CR}/01-creative-direction/examples/art-direction-*.json"))
docs = {}
for p in examples:
    ad = json.load(open(p)); name = os.path.basename(p); docs[name] = ad
    se = errs(V_AD, ad)
    ve = []
    for k, v in ((ad.get("handoff") or {}).get("visual_dna") or {}).items():
        ve += [f"visual_dna.{k}: {m}" for m in errs(V_VD[k], v)]
    ce, cw = cross(ad)
    ok = not se and not ve and not ce
    report["examples"][name] = {"schema": se, "visual_dna": ve, "cross": ce, "warnings": cw, "ok": ok}
    if not ok: fails.append(name)
    print(("ok  " if ok else "XX  ") + name + f" — схема {len(se)}, паспорт {len(ve)}, правила {len(ce)}, предупреждений {len(cw)}")
    for m in se + ve + ce: print("     ·", m)
    for m in cw: print("     ~", m)

# отрицательные случаи (на «Кварце»)
base = docs["art-direction-kvarts.json"]
def neg(name, mut, kind):
    d = copy.deepcopy(base); mut(d)
    e = errs(V_AD, d) if kind == "schema" else cross(d)[0]
    good = bool(e)
    report["negative"].append({"case": name, "kind": kind, "caught": good, "first": e[0] if e else None})
    if not good: fails.append(name)
    print(("ok  " if good else "XX  ") + f"[neg] {name}: " + (e[0] if e else "НЕ ПОЙМАНО"))
def set_axes_like_a(d):
    d["directions"][1]["axes"].update({k: d["directions"][0]["axes"][k] for k in ("paper", "display_style", "macrostructure")})
neg("n1-directions-too-similar", set_axes_like_a, "cross")
neg("n2-two-serif-directions", lambda d: d["directions"][3]["axes"].update({"display_style": "serif"}), "cross")
neg("n3-use-with-failed-criterion", lambda d: d["decisions"][1]["criteria"]["epoch"].update({"result": "fail"}), "schema")
neg("n4-approved-without-signer", lambda d: d.update({"approved_by": None}), "schema")
neg("n5-smooth-scroll-on-L1", lambda d: d["motion_system"].update({"smooth_scroll": True}), "cross")
neg("n6-boldness-mismatch", lambda d: d["handoff"]["visual_dna"]["character"].update({"boldness": "bold"}), "cross")
neg("n7-low-contrast-palette", lambda d: d["directions"][0]["palette"].update({"text": "#9AA0A6"}), "cross")
neg("n8-unknown-macrostructure", lambda d: d["directions"][0]["axes"].update({"macrostructure": "hero-bento-magic"}), "cross")
neg("n9-two-literal-territories", lambda d: d["territories"][0].update({"literal": True}), "cross")
neg("n10-chosen-missing", lambda d: d["choice"].update({"chosen": "z"}), "cross")
neg("n11-3d-scene-on-L1", lambda d: d["effects_by_section"].append({"section": "hero", "level": "L1", "effects": ["effect:3d-scene"]}), "cross")
neg("n12-two-directions-only", lambda d: d.update({"directions": d["directions"][:2]}), "schema")
neg("n13-budget-profile-mismatch", lambda d: d["ambition"].update({"budget_profile": "landing-saas@L1"}), "cross")
neg("n14-thesis-too-long", lambda d: d["concept"].update({"thesis": "очень " * 60}), "schema")

# сравнение L0 ↔ L2 для «Лесной обжарки»
l0, l2 = docs.get("art-direction-forest-roast-l0.json"), docs.get("art-direction-forest-roast-l2.json")
if l0 and l2:
    def pick(ad):
        ch = next(d for d in ad["directions"] if d["id"] == (ad.get("choice") or {"chosen": next(x["id"] for x in ad["directions"] if x.get("recommended"))})["chosen"])
        eff = sorted({e for s in ad.get("effects_by_section", []) for e in s["effects"]})
        return {
            "уровень": ad["ambition"]["level"], "профиль": ad["ambition"]["budget_profile"],
            "boldness": ad["handoff"]["visual_dna"]["character"]["boldness"], "направление": ch["name"],
            "макроструктура": ch["axes"]["macrostructure"], "стратегия цвета": ad["visual_language"]["color_strategy"],
            "движение": ad["motion_system"]["level"], "плавная прокрутка": ad["motion_system"].get("smooth_scroll"),
            "эффекты": ", ".join(eff), "главный приём": ch["signature_move"]["what"],
            "бюджет эффектов, КБ": sum(s["kb"] for s in ad.get("budget", {}).get("spend", []) if s.get("device") in ("desktop", "both")),
        }
    a, b = pick(l0), pick(l2)
    report["compare"] = {"L0": a, "L2": b}
    print("\n| Поле | L0 | L2 |\n|---|---|---|")
    for k in a: print(f"| {k} | {a[k]} | {b[k]} |")

json.dump(report, open(os.path.join(OUT, "report.json"), "w"), ensure_ascii=False, indent=1)
print("\nИТОГ:", "все ожидания выполнены" if not fails else f"расхождения: {fails}")
sys.exit(1 if fails else 0)
