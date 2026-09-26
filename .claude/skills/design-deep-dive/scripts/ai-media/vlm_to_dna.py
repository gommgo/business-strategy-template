#!/usr/bin/env python3
"""vlm_to_dna.py — паспорт визуала бренда (visual DNA): VLM-бриф сетки бренд-картинок → черновик паспорта,
проверка по схеме и смыслу, сверка прогонов, грейд .cube, вывод из токенов UI, спецификация ассета.

Агент F (продолжатель F2), волна 2, 23.09.2026. Python 3.13 + numpy + Pillow (системные); jsonschema — если есть
(`99-raw/tools/venv-D2/bin/python`), иначе встроенный валидатор подмножества JSON Schema 2020-12.
Платных вызовов нет: `build` только пишет задание `.polza-chat.json` (исполняет клиент каналов в фазе 5),
`parse` работает с сохранённым ответом. [проверено: 99-raw/experiments/F/07-dna, selftest]

Схема паспорта — 06-art-direction-consistency/visual-dna.schema.json; описание полей и правил вывода —
06-art-direction-consistency/01-visual-dna-from-ui.md. Цвет и грейд — 99-raw/experiments/F/05-color/palette.py.

Команды:
  grid IMG... --out GRID.jpg [--cell 640 --cols 3]      сетка бренд-картинок для VLM (белые желоба 10 px)
  build GRID --out JOB.polza-chat.json [--model M] [--variant N] [--tag T]
                                                        задание F-05: VLM описывает сетку → JSON брифа
  parse RESPONSE.json --out DNA.json [--grid GRID] [--id ID] [--brand B]
                                                        ответ VLM (chat completion или голый JSON) → черновик
                                                        паспорта; с --grid — палитра, баланс белого и хрома,
                                                        снятые локально, и критерий F-05 «≥ 3 из 5 hex в ΔE ≤ 0,05»
  validate DNA.json...                                  схема + смысловой линт (запрещённые оттенки, слова, роли)
  compare A.json B.json                                 два прогона VLM: совпадение grade и light, ΔE палитр
  lut DNA.json --out FILE.cube [--size 33]              параметрический грейд паспорта → 3D LUT (.cube)
  from-tokens TOKENS.json --out DNA.json [--adjectives a,b,c] [--id ID]
                                                        скелет паспорта из токенов DTCG (ui-research 09/04)
  to-spec DNA.json --kind photo|illustration|icon3d --task CODE --subject TEXT [--slot hero]
          [--ratio 16:9] [--no-text-zone] [--ref-class CLASS] [--out SPEC.json]
                                                        спецификация ассета v0.2 (05-prompting) из паспорта
  selftest                                              самопроверка на заглушках ответа VLM
"""
import argparse, copy, datetime as dt, json, math, os, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))  # перенос: scripts/lib (kbpaths, color)
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("ai-media")
TOOLS = kbpaths.scripts("ai-media")
SCHEMA_PATH = ROOT / "06-art-direction-consistency" / "visual-dna.schema.json"
SPEC_SCHEMA_PATH = ROOT / "05-prompting" / "asset-spec.schema.json"
EXAMPLES = ROOT / "06-art-direction-consistency" / "examples"
F05 = TOOLS  # перенос: palette.py — scripts/ai-media
F05_JOB = kbpaths.out("ai-media", "phase5", "jobs") / "F-05-vlm-brand-brief.polza-chat.json"
sys.path.insert(0, str(F05))
sys.path.insert(0, str(TOOLS))

# ---------------------------------------------------------------- запрос VLM (как задание F-05, дословно)
VLM_MODEL = "google/gemini-3-flash-preview"
VLM_SYSTEM = ("You are an expert brand visual analyst and image generation brief writer. You receive one image containing "
              "a grid of brand photographs. Describe only what is visible; use numbers where asked; do not flatter; do not "
              "invent brand names.")
VLM_USER = ("Return ONLY a JSON object (no prose) with these keys: character: {adjectives: [3 words]}; palette: [5 items {hex, "
            "name, role: background|dominant|secondary|accent|shadow, share: 0-1 of image area}] (shares sum <= 1); grade: "
            "{white_balance: warm|neutral|cool, contrast: low|medium|high, saturation: muted|natural|vivid, black_point: "
            "crushed|neutral|lifted, grain: none|fine|visible}; light: {direction, quality: soft|hard|mixed, time_of_day, "
            "color_temp_K: integer}; camera: {lens_mm: integer, height: ground|eye-level|high, depth_of_field: "
            "shallow|medium|deep}; composition: {subject_region, horizon_position: top-third|middle|bottom-third, "
            "negative_space: low|medium|high, crop_style}; subject_matter: {domain_props: [up to 8 concrete objects], motifs: "
            "[up to 4], people_policy: none|background|primary}; style_block_photo: one paragraph of at most 60 words in English "
            "that would make a text-to-image model reproduce this photographic style for NEW subjects (visible features only, "
            "no adjectives like stunning/cinematic/vibrant); exclusions: [up to 6 visible features that would break this "
            "style]; canaries: [5 short test subjects of different classes (object, interior, nature, abstract, product) to "
            "check the style on a new model].")
# цены polza 2026-09-23 (api-v1-models.json): вход и картинка 29,498 ₽/M токенов, выход 176,988 ₽/M
PRICE_NOTE = ("polza 2026-09-23 api-v1-models.json: google/gemini-3-flash-preview prompt 29,498 ₽/M, image_input 29,498 ₽/M, "
              "completion 176,988 ₽/M; оценка: вход ≈ 1,7 тыс. токенов (картинка ≈ 3 плитки × 258) + выход ≈ 4 тыс. с "
              "размышлением ≈ 0,05 + 0,71 ≈ 0,8 ₽")

# ---------------------------------------------------------------- VLM-категории → числа паспорта [мнение F2; калибровать в F-05]
WB = {"warm": (0.002, 0.010), "neutral": (0.0, 0.0), "cool": (-0.001, -0.006)}
WB_TARGET_B = {"warm": (0.010, 0.006), "neutral": (0.0, 0.004), "cool": (-0.004, 0.004)}
SAT = {"muted": 0.80, "natural": 0.92, "vivid": 1.0}
CON = {"low": 0.05, "medium": 0.12, "high": 0.20}
BLACK = {"crushed": 0.0, "neutral": 0.03, "lifted": 0.05}
GRAIN = {"none": 0.0, "fine": 1.5, "visible": 3.0}
NEG = {"low": 0.15, "medium": 0.30, "high": 0.45}
DEFAULT_BANNED = ["stunning", "vibrant", "luminous", "radiant", "breathtaking", "gorgeous", "mesmerizing", "cinematic", "epic",
                  "dramatic", "masterpiece", "8k", "hyper-detailed", "hyperrealistic", "award-winning", "golden hour", "hdr"]
DEFAULT_MARKERS = ["IMG-M02", "IMG-M03", "IMG-M05", "IMG-M07", "IMG-M09", "IMG-M10", "IMG-M13", "IMG-M14", "IMG-M21", "IMG-M22"]
ACCEPTANCE_DEFAULT = {  # F/02, F/03, F/04, F/06 — фото одной съёмки
    "palette_dE_max": 0.02, "series_hue_spread_max_deg": 10, "series_pal_dE_mean_max": 0.045, "series_pal_dE_break": 0.06,
    "series_sd_L_max": 0.04, "phash_min": 10, "text_contrast_min": 4.5, "text_zone_percentile": 99.9, "zone_edge_max": 0.06,
    "centroid_x_min": 0.62, "colorfulness_max_rel": 1.2, "hdr_index_max_delta": 0.1, "markers_max": 1}


def today():
    return dt.date.today().isoformat()


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump_json(obj, p):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ---------------------------------------------------------------- цвет (без numpy: color.py)
def hex_rgb(h):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hex_oklab(h):
    from color import rgb2oklab
    return rgb2oklab(*hex_rgb(h))


def hex_oklch(h):
    L, a, b = hex_oklab(h)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def dE(a, b):
    return math.dist(hex_oklab(a) if isinstance(a, str) else a, hex_oklab(b) if isinstance(b, str) else b)


def hue_in(h, lo, hi):
    return lo <= h <= hi if lo <= hi else (h >= lo or h <= hi)


# ---------------------------------------------------------------- валидатор (jsonschema или встроенный)
def _type_ok(v, t):
    return {"object": isinstance(v, dict), "array": isinstance(v, list), "string": isinstance(v, str),
            "integer": isinstance(v, int) and not isinstance(v, bool),
            "number": isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": isinstance(v, bool), "null": v is None}.get(t, True)


def mini_validate(inst, sch, root, path="", errs=None):
    """Подмножество JSON Schema 2020-12, которого хватает схемам паспорта и спецификации ассета."""
    errs = [] if errs is None else errs
    where = path or "(root)"
    if sch is True or not isinstance(sch, dict):
        return errs
    if "$ref" in sch:
        node = root
        for part in sch["$ref"].lstrip("#/").split("/"):
            node = node[part]
        mini_validate(inst, node, root, path, errs)
    t = sch.get("type")
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        if not any(_type_ok(inst, x) for x in ts):
            errs.append(f"{where}: тип {type(inst).__name__}, ожидался {t}")
            return errs
    if "const" in sch and inst != sch["const"]:
        errs.append(f"{where}: должно быть {sch['const']!r}")
    if "enum" in sch and inst not in sch["enum"]:
        errs.append(f"{where}: {inst!r} не из {sch['enum']}")
    if isinstance(inst, str):
        if "pattern" in sch and not re.search(sch["pattern"], inst):
            errs.append(f"{where}: {inst!r} не соответствует {sch['pattern']}")
        if "minLength" in sch and len(inst) < sch["minLength"]:
            errs.append(f"{where}: короче {sch['minLength']}")
        if "maxLength" in sch and len(inst) > sch["maxLength"]:
            errs.append(f"{where}: длиннее {sch['maxLength']}")
    if _type_ok(inst, "number"):
        if "minimum" in sch and inst < sch["minimum"]:
            errs.append(f"{where}: {inst} < {sch['minimum']}")
        if "maximum" in sch and inst > sch["maximum"]:
            errs.append(f"{where}: {inst} > {sch['maximum']}")
        if "exclusiveMinimum" in sch and inst <= sch["exclusiveMinimum"]:
            errs.append(f"{where}: {inst} ≤ {sch['exclusiveMinimum']}")
        if "exclusiveMaximum" in sch and inst >= sch["exclusiveMaximum"]:
            errs.append(f"{where}: {inst} ≥ {sch['exclusiveMaximum']}")
    if isinstance(inst, list):
        if "minItems" in sch and len(inst) < sch["minItems"]:
            errs.append(f"{where}: элементов {len(inst)} < {sch['minItems']}")
        if "maxItems" in sch and len(inst) > sch["maxItems"]:
            errs.append(f"{where}: элементов {len(inst)} > {sch['maxItems']}")
        pre = sch.get("prefixItems", [])
        for i, (x, s) in enumerate(zip(inst, pre)):
            mini_validate(x, s, root, f"{path}/{i}", errs)
        if "items" in sch:
            for i, x in enumerate(inst[len(pre):], start=len(pre)):
                mini_validate(x, sch["items"], root, f"{path}/{i}", errs)
    if isinstance(inst, dict):
        for k in sch.get("required", []):
            if k not in inst:
                errs.append(f"{where}: нет обязательного поля {k!r}")
        props = sch.get("properties", {})
        for k, v in inst.items():
            if k in props:
                mini_validate(v, props[k], root, f"{path}/{k}", errs)
            elif sch.get("additionalProperties") is False:
                errs.append(f"{where}: лишнее поле {k!r}")
            elif isinstance(sch.get("additionalProperties"), dict):
                mini_validate(v, sch["additionalProperties"], root, f"{path}/{k}", errs)
        if "minProperties" in sch and len(inst) < sch["minProperties"]:
            errs.append(f"{where}: полей {len(inst)} < {sch['minProperties']}")
    for key in ("oneOf", "anyOf"):
        if key in sch:
            ok = sum(1 for s in sch[key] if not mini_validate(inst, s, root, path, []))
            if (key == "oneOf" and ok != 1) or (key == "anyOf" and ok < 1):
                errs.append(f"{where}: {key} — подходит {ok} вариантов")
    for s in sch.get("allOf", []):
        mini_validate(inst, s, root, path, errs)
    return errs


def schema_errors(inst, schema_path=SCHEMA_PATH, force_builtin=False):
    schema = load_json(schema_path)
    if not force_builtin:
        try:
            import jsonschema
            v = jsonschema.Draft202012Validator(schema)
            return ["/" + "/".join(map(str, e.absolute_path)) + ": " + e.message
                    for e in sorted(v.iter_errors(inst), key=lambda e: list(map(str, e.absolute_path)))], "jsonschema"
        except ImportError:
            pass
    return mini_validate(inst, schema, schema), "builtin"


# ---------------------------------------------------------------- смысловой линт паспорта
def words(s):
    return len(re.findall(r"[A-Za-zА-Яа-яЁё0-9#'-]+", s))


def lint(dna, dna_path=None):
    errs, warns = [], []
    if dna.get("status") == "approved" and not dna.get("approved_by"):
        errs.append("status approved без approved_by: паспорт утверждает человек")
    pal = dna.get("palette", {})
    bands = pal.get("forbidden_hues", [])
    for key in ("image_palette", "illustration_palette"):
        for e in pal.get(key, []):
            L, C, H = hex_oklch(e["hex"])
            brand_token = e.get("strict") and e.get("source") == "token"
            for b in bands:
                if key == "illustration_palette" and brand_token:
                    continue  # бренд-акцент из токенов в иллюстрации разрешён; потолок доли полосы — для фото
                if C > 0.04 and hue_in(H, b["from"], b["to"]) and e.get("share_max", 1) > b.get("except_share_max", 0):
                    errs.append(f"{key} {e['hex']} ({e['name']}): оттенок {H:.0f}° в запрещённой полосе {b['from']}–{b['to']}°, "
                                f"доля {e.get('share_max')} > {b.get('except_share_max', 0)}")
            caps = pal.get("chroma_caps")
            if key == "illustration_palette" and caps:
                s = e.get("share_max", 0)
                cap = caps.get("large_area_C_max") if s > 0.3 else caps.get("mid_area_C_max") if s > 0.05 else caps.get("small_area_C_max")
                if cap is not None and C > cap + 0.005 and e.get("role") != "accent":
                    warns.append(f"illustration_palette {e['hex']}: хрома {C:.3f} выше потолка {cap} для доли {s}")
        roles = [e["role"] for e in pal.get(key, [])]
        if key == "image_palette" and not ({"dominant", "background"} & set(roles)):
            errs.append("image_palette: нет роли dominant или background")
        if roles.count("accent") > 3:
            warns.append(f"{key}: акцентов {roles.count('accent')} > 3 (ui 07/02 §2.1: 2–3)")
    banned = [w.lower() for w in dna.get("exclusions", {}).get("banned_words", [])] or DEFAULT_BANNED
    for k, block in dna.get("style_blocks", {}).items():
        n = words(block)
        if n > 80:
            warns.append(f"style_blocks.{k}: {n} слов > 80 (FLUX: 30–80 оптимально; блок идёт первым в каждом промте)")
        negs = re.findall(r"\bno [a-z-]+", block.lower())
        if negs:
            warns.append(f"style_blocks.{k}: «{', '.join(negs[:3])}» — у FLUX, Gemini и Recraft V4 негативов нет, «no X» может "
                         "вызвать X; писать позитивом (словарь замен 01-visual-dna-from-ui.md §4)")
        if re.search(r"\btransparent background\b|\bon transparent\b|\bno background\b", block, re.I):
            warns.append(f"style_blocks.{k}: «transparent background» в промте — модели без альфы рисуют шахматку (H `08/01` §3, "
                         "`alpha_check.py fake`); в блоке — ровный фон цвета секции, альфа — вырезом или векторизацией (поле "
                         "`illustration.background` паспорта — про поставку, не про промт)")
        if re.match(r"^\s*series style", block, re.I):
            warns.append(f"style_blocks.{k}: начинается с ярлыка «Series style» — компилятор D2 добавит свой, будет дубль")
        low = block.lower()
        hits = [w for w in banned if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low)]
        if hits:
            errs.append(f"style_blocks.{k}: запрещённые слова {hits}")
    for e in dna.get("exclusions", {}).get("replace_with", []):
        if e.get("kind") == "object" and e.get("replace_with") and words(e["replace_with"]) > 6:
            warns.append(f"exclusions: замена «{e['replace_with']}» длинная — не вписывает ли она новые предметы в каждый кадр серии?")
    refs = dna.get("references", [])
    style_refs = [r for r in refs if r.get("role") == "style"]
    if len({r.get("class") for r in style_refs}) > 1:
        warns.append("references: стилевые референсы разных классов сюжетов — делите по классам (референс работает на классе, "
                     "на котором собран) и подавайте 1–3 одного класса на вызов")
    if dna.get("icon3d") and not pal.get("env_color"):
        warns.append("icon3d без palette.env_color: фон и рефлексы 3D не привязаны к цвету секции страницы (ореол при вырезе)")
    if dna_path:
        for r in refs:
            if not re.match(r"^[a-z]+://", r["src"]) and not (Path(dna_path).parent / r["src"]).exists():
                warns.append(f"references: файл не найден {r['src']}")
        lut = dna.get("grade", {}).get("lut", {}).get("file")
        if lut and not (Path(dna_path).parent / lut).exists():
            warns.append(f"grade.lut.file не найден: {lut}")
    can = dna.get("canaries", [])
    classes = {c.split(":")[0].strip() for c in can if ":" in c}
    if can and len(classes) < 3:
        warns.append("canaries: меньше 3 разных классов («object: …», «interior: …», «nature: …»)")
    comp = dna.get("composition", {})
    tz = comp.get("text_zone_default")
    if tz and tz.get("side") in ("left", "right") and comp.get("subject_region") in ("left-third", "right-third"):
        if (tz["side"] == "left") == (comp["subject_region"] == "left-third"):
            errs.append(f"composition: объект ({comp['subject_region']}) и зона текста ({tz['side']}) на одной стороне")
    acc = dna.get("acceptance", {})
    if acc.get("text_zone_percentile", 99.9) < 99:
        warns.append("acceptance.text_zone_percentile < 99: скрим по p95 оставил нечитаемыми 14 из 64 комбинаций (F/02)")
    nw = pal.get("neutral_wb")
    if nw and nw["target_b"] > 0.008 and "IMG-M04" in dna.get("exclusions", {}).get("forbidden_markers", []):
        warns.append("IMG-M04 (тёплый сдвиг) в запретах, а баланс белого бренда тёплый: сдвиг — стиль, проверять к neutral_wb")
    return errs, warns


# ---------------------------------------------------------------- сетка и замеры с картинки
def make_grid(paths, out, cell=640, cols=3, gutter=10):
    from PIL import Image
    ims = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        h = round(im.height * cell / im.width)
        ims.append(im.resize((cell, h), Image.LANCZOS))
    rows = math.ceil(len(ims) / cols)
    ch = min(i.height for i in ims)
    W = cols * cell + (cols - 1) * gutter
    H = rows * ch + (rows - 1) * gutter
    g = Image.new("RGB", (W, H), "white")
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        g.paste(im.crop((0, (im.height - ch) // 2, cell, (im.height - ch) // 2 + ch)), (c * (cell + gutter), r * (ch + gutter)))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    g.save(out, quality=90)
    return g.size


def strip_gutters(img, thr=0.94, frac=0.95):
    """Убрать белые желоба сетки (строки и столбцы, где ≥ 95 % пикселей почти белые)."""
    import numpy as np
    white = (img > thr).all(axis=2)
    keep_r = white.mean(axis=1) < frac
    keep_c = white.mean(axis=0) < frac
    return img[keep_r][:, keep_c]


def measure_image(path, k=6):
    import numpy as np
    from palette import load, palette, to_oklab, hexs
    img = strip_gutters(load(path, 1200))
    pal = palette(img, k)
    X = to_oklab(img.reshape(-1, 3))
    C = np.hypot(X[:, 1], X[:, 2])
    n = C < 0.03
    return {"palette": [[h.upper(), round(s, 3)] for h, s, _ in pal],
            "neutral_ab": [round(float(X[n, 1].mean()), 4), round(float(X[n, 2].mean()), 4)] if n.any() else None,
            "neutral_share": round(float(n.mean()), 3),
            "median_chroma": round(float(np.median(C)), 4),
            "L_percentiles_1_25_50_75_99": [round(float(v), 3) for v in np.percentile(X[:, 0], [1, 25, 50, 75, 99])],
            "_lab": [c for _, _, c in pal],
            "_pix": X[np.random.default_rng(0).choice(len(X), min(40000, len(X)), replace=False)]}


# ---------------------------------------------------------------- разбор ответа VLM
def extract_json(obj):
    """Ответ chat completion, текст с ```json или голый JSON → dict ответа VLM."""
    if isinstance(obj, dict) and "choices" in obj:
        content = obj["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        return extract_json(content)
    if isinstance(obj, dict):
        return obj
    s = str(obj).strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", s, re.S)
    if m:
        s = m.group(1).strip()
    start = s.find("{")
    if start < 0:
        raise ValueError("в ответе нет JSON-объекта")
    depth, instr, esc = 0, False, False
    for i, ch in enumerate(s[start:], start):
        if instr:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                instr = False
        elif ch == '"':
            instr = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(s[start:i + 1])
    raise ValueError("JSON-объект в ответе не закрыт")


VLM_KEYS = ["character", "palette", "grade", "light", "camera", "composition", "subject_matter", "style_block_photo",
            "exclusions", "canaries"]


def vlm_problems(v):
    p = [f"нет ключа {k}" for k in VLM_KEYS if k not in v]
    pal = v.get("palette", [])
    if not isinstance(pal, list) or not pal:
        p.append("palette пуст")
    else:
        for i, e in enumerate(pal):
            if not re.match(r"^#[0-9A-Fa-f]{6}$", str(e.get("hex", ""))):
                p.append(f"palette[{i}].hex {e.get('hex')!r}")
        s = sum(float(e.get("share", 0) or 0) for e in pal)
        if s > 1.05:
            p.append(f"palette: сумма долей {s:.2f} > 1")
    for k, allowed in (("white_balance", WB), ("contrast", CON), ("saturation", SAT), ("black_point", BLACK), ("grain", GRAIN)):
        val = v.get("grade", {}).get(k)
        if val not in allowed:
            p.append(f"grade.{k} = {val!r} не из {list(allowed)}")
    return p


def map_direction(txt):
    t = (txt or "").lower()
    for key, words_ in (("back", ("back", "behind", "contre", "rim")), ("top", ("overhead", "top", "above", "zenith")),
                        ("left", ("left",)), ("right", ("right",)), ("front", ("front",)), ("side", ("side",))):
        if any(w in t for w in words_):
            return key
    return "ambient"


def map_region(txt):
    t = (txt or "").lower()
    if "left" in t:
        return "left-third"
    if "right" in t:
        return "right-third"
    if "cent" in t or "middle" in t:
        return "center"
    if "top" in t or "upper" in t:
        return "top"
    if "bottom" in t or "lower" in t or "foreground" in t:
        return "bottom"
    return "full-frame"


def vlm_to_dna(v, dna_id, brand=None, measured=None, model=VLM_MODEL):
    g, li, cam, comp, sm = v["grade"], v.get("light", {}), v.get("camera", {}), v.get("composition", {}), v.get("subject_matter", {})
    sat, con = g.get("saturation"), g.get("contrast")
    boldness = "bold" if sat == "vivid" or con == "high" else "restrained" if sat == "muted" or con == "low" else "balanced"
    image_palette = []
    for e in v["palette"][:6]:
        role = e.get("role") if e.get("role") in ("background", "dominant", "secondary", "accent", "shadow") else "secondary"
        share = float(e.get("share", 0) or 0)
        image_palette.append({"role": role, "hex": e["hex"].upper(), "name": str(e.get("name", "colour"))[:40],
                              "share_max": round(min(1.0, share * 1.3 + 0.02), 2), "applies_to": "", "source": "vlm"})
    for e in image_palette:
        if not e["applies_to"]:
            e.pop("applies_to")
    height = cam.get("height") if cam.get("height") in ("ground", "eye-level", "high") else "eye-level"
    tb, tol = WB_TARGET_B[g["white_balance"]]
    if measured and measured.get("neutral_ab") and measured.get("neutral_share", 0) > 0.01:
        tb, tol = measured["neutral_ab"][1], 0.006
    region = map_region(comp.get("subject_region"))
    dna = {
        "dna_version": "0.1", "id": dna_id, "brand": brand or "черновик VLM", "checked_at": today(), "status": "draft",
        "approved_by": None,
        "character": {"adjectives": (list(v.get("character", {}).get("adjectives", [])) + ["?", "?", "?"])[:3], "boldness": boldness},
        "palette": {"image_palette": image_palette,
                    "forbidden_hues": [{"from": 270, "to": 320, "reason": "пурпур и неон (IMG-M05), если их нет в бренде"}],
                    "neutral_wb": {"target_b": round(tb, 4), "tol": tol}},
        "grade": {"wb_ab": list(WB[g["white_balance"]]), "chroma": SAT[sat], "black": BLACK[g["black_point"]], "white": 0.975,
                  "contrast": CON[con], "grain_pct": GRAIN[g["grain"]], "lut": {"size": 33, "file": None},
                  "applies_to": ["photo", "video"], "note": "числа — из категорий VLM по таблице vlm_to_dna.py; утвердить глазом"},
        "light": {"direction": map_direction(li.get("direction")), "detail": str(li.get("direction", "")),
                  "quality": li.get("quality") if li.get("quality") in ("soft", "hard", "mixed") else "soft",
                  "time_of_day": str(li.get("time_of_day", ""))},
        "camera": {"lens_mm": int(cam.get("lens_mm") or 35), "height": height,
                   "angle": {"ground": "low-angle", "eye-level": "eye-level", "high": "high-angle"}[height],
                   "depth_of_field": cam.get("depth_of_field") if cam.get("depth_of_field") in ("shallow", "medium", "deep") else "medium"},
        "composition": {"subject_region": region, "negative_space_min": NEG.get(comp.get("negative_space"), 0.3),
                        "max_elements": 3, "asymmetry": region != "center",
                        "horizon": comp.get("horizon_position") if comp.get("horizon_position") in ("top-third", "middle", "bottom-third") else "none",
                        "note": str(comp.get("crop_style", ""))},
        "subject_matter": {"domain_props": (list(sm.get("domain_props", [])) + ["?", "?", "?"])[:max(3, len(sm.get("domain_props", [])))][:16],
                           "motifs": list(sm.get("motifs", []))[:6],
                           "people_policy": "none" if sm.get("people_policy") == "none" else "real-only",
                           "product_policy": "reference-locked"},
        "canaries": [str(c) for c in v.get("canaries", [])][:8] or ["object: ?", "interior: ?", "nature: ?"],
        "style_blocks": {"photo": str(v.get("style_block_photo", "")).strip()},
        "exclusions": {"forbidden_markers": list(DEFAULT_MARKERS), "banned_words": list(DEFAULT_BANNED),
                       "replace_with": [{"what": str(x), "kind": "style"} for x in v.get("exclusions", [])][:6]},
        "post": {"grain_pct": GRAIN[g["grain"]], "scrim": {"max_alpha": 0.55, "shape": "gradient", "percentile": 99.9},
                 "focal_required": True},
        "acceptance": dict(ACCEPTANCE_DEFAULT),
        "provenance": {"created_by": "vlm", "vlm_model": model, "runs": 1, "vlm_raw": v},
    }
    ct = li.get("color_temp_K")
    if isinstance(ct, (int, float)) and 2000 <= ct <= 12000:
        dna["light"]["cct_K"] = int(ct)
    if len(dna["canaries"]) < 3:
        dna["canaries"] += ["object: ?", "interior: ?", "nature: ?"][:3 - len(dna["canaries"])]
    if dna["composition"]["subject_region"] in ("left-third", "right-third"):
        dna["composition"]["text_zone_default"] = {"side": "right" if region == "left-third" else "left", "share": 0.4}
    if measured:
        dna["palette"]["median_chroma_max"] = round(measured["median_chroma"] * 1.2, 3)
        dna["provenance"]["measured"] = {k: v_ for k, v_ in measured.items() if not k.startswith("_")}
    return dna


def palette_check(dna_or_vlm_palette, measured, thr=0.05):
    """Критерий F-05: сколько hex VLM лежат в ΔE OKLab ≤ thr от ближайшего цвета палитры, снятой локально."""
    import numpy as np
    labs = [tuple(float(x) for x in c) for c in measured["_lab"]]
    pix = measured.get("_pix")
    rows = []
    for e in dna_or_vlm_palette:
        lab = hex_oklab(e["hex"])
        d = min(math.dist(lab, c) for c in labs)
        row = {"hex": e["hex"], "name": e.get("name"), "dE_to_local": round(d, 4), "ok": d <= thr}
        if pix is not None:
            cov = float((np.sqrt(((pix - np.array(lab)) ** 2).sum(1)) <= thr).mean())
            share = float(e.get("share", e.get("share_max", 0)) or 0)
            row.update({"coverage": round(cov, 3), "declared_share": share,
                        "invented": cov < 0.005 or (share >= 0.1 and cov < share / 3)})
        rows.append(row)
    return rows


# ---------------------------------------------------------------- сравнение прогонов
def compare(a, b):
    out = {}
    ra, rb = a.get("provenance", {}).get("vlm_raw"), b.get("provenance", {}).get("vlm_raw")
    if ra and rb:
        out["grade_categories_equal"] = {k: ra["grade"].get(k) == rb["grade"].get(k) for k in ("white_balance", "contrast", "saturation", "black_point", "grain")}
        out["light_equal"] = {"direction": a["light"]["direction"] == b["light"]["direction"], "quality": a["light"]["quality"] == b["light"]["quality"]}
    else:
        out["grade_numbers_equal"] = {k: a["grade"].get(k) == b["grade"].get(k) for k in ("wb_ab", "chroma", "black", "contrast", "grain_pct")}
        out["light_equal"] = {"direction": a["light"]["direction"] == b["light"]["direction"], "quality": a["light"]["quality"] == b["light"]["quality"]}
    pa, pb = a["palette"]["image_palette"], b["palette"]["image_palette"]
    d1 = [min(dE(x["hex"], y["hex"]) for y in pb) for x in pa]
    d2 = [min(dE(y["hex"], x["hex"]) for x in pa) for y in pb]
    out["palette_dE_sym_mean"] = round((sum(d1) / len(d1) + sum(d2) / len(d2)) / 2, 4)
    gk = out.get("grade_categories_equal") or out.get("grade_numbers_equal")
    out["same_grade_and_light"] = all(gk.values()) and all(out["light_equal"].values())
    return out


# ---------------------------------------------------------------- LUT
def write_lut(dna, out, size=33):
    from palette import parametric_grade, write_cube
    g = dna["grade"]
    f = lambda x: parametric_grade(x, wb_ab=tuple(g["wb_ab"]), chroma=g["chroma"], black=g["black"], white=g["white"],
                                   contrast=g["contrast"])
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    write_cube(str(out), f, n=size, title=f"{dna['id']} grade (vlm_to_dna.py lut)")
    return out


def cube_numbers(p):
    rows = []
    for line in open(p):
        parts = line.split()
        if len(parts) == 3:
            try:
                rows.append(tuple(float(x) for x in parts))
            except ValueError:
                pass
    return rows


# ---------------------------------------------------------------- вывод из токенов DTCG
def tok(tokens, path):
    node = tokens
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    val = node.get("$value") if isinstance(node, dict) and "$value" in node else node
    if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
        return tok(tokens, val[1:-1])
    return val


def tok_hex(tokens, path):
    v = tok(tokens, path)
    if isinstance(v, dict):
        v = v.get("hex")
    return v.upper() if isinstance(v, str) and re.match(r"^#[0-9A-Fa-f]{6}$", v) else None


def tok_px(tokens, path):
    v = tok(tokens, path)
    if isinstance(v, dict) and "value" in v:
        return float(v["value"])
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str) and v.endswith("px"):
        return float(v[:-2])
    return None


def name_for(hexv):
    """Английское название цвета для промта по OKLCH (hex без названия не отправлять — BFL)."""
    L, C, H = hex_oklch(hexv)
    warm, cool = 20 <= H <= 110, 180 <= H <= 290
    light = "light " if L > 0.8 else "dark " if L < 0.45 else ""
    if C < 0.02:
        tone = "white" if L > 0.96 else "light grey" if L > 0.8 else "mid grey" if L > 0.55 else "dark grey" if L > 0.3 else "near black"
        tint = "" if C < 0.006 or tone == "white" else ("warm " if warm else "cool " if cool else "")
        return (tint + tone).strip()
    if C < 0.06:
        if L < 0.32:
            return "deep navy" if cool else "dark brown" if warm else "near black"
        return light + ("blue-grey" if cool else "warm grey" if warm else "grey")
    hues = [(40, "red"), (70, "orange"), (95, "amber"), (115, "yellow"), (135, "yellow-green"), (165, "green"), (200, "teal"),
            (240, "sky blue"), (270, "blue"), (295, "indigo"), (330, "violet"), (360, "magenta")]
    hn = next(n for lim, n in hues if H <= lim)
    return ("deep " if L < 0.45 else "light " if L > 0.8 else "") + hn


def from_tokens(tokens, dna_id="from-tokens", adjectives=None, tokens_path=None):
    """Правила R1–R8 файла 01-visual-dna-from-ui.md §3: токены UI → скелет паспорта (без брендовых фото)."""
    canvas = tok_hex(tokens, "color.bg.canvas") or "#FFFFFF"
    surface = tok_hex(tokens, "color.bg.surface") or "#FFFFFF"
    text = tok_hex(tokens, "color.text.primary") or "#111111"
    text2 = tok_hex(tokens, "color.text.secondary") or text
    border = tok_hex(tokens, "color.border.subtle") or tok_hex(tokens, "color.border.default") or "#E5E7EB"
    accent = tok_hex(tokens, "color.accent.solid") or "#2563EB"
    neutral_mid = tok_hex(tokens, "primitive.color.neutral.500") or text2
    n200 = tok_hex(tokens, "primitive.color.neutral.200") or border
    n400 = tok_hex(tokens, "primitive.color.neutral.400") or text2
    a200 = tok_hex(tokens, "primitive.color.accent.200")
    radius = tok_px(tokens, "radius.md") or 6.0
    fam = tok(tokens, "primitive.font.family.serif") and "serif" or ""
    sans = tok(tokens, "primitive.font.family.sans")
    fam_name = (sans[0] if isinstance(sans, list) and sans else str(sans or "")).lower()
    AL, AC, AH = hex_oklch(accent)
    NL, NC, NH = hex_oklch(neutral_mid)
    temp = "neutral" if NC < 0.006 else ("warm" if 20 <= NH <= 110 else "cool" if 180 <= NH <= 290 else "neutral")
    has_raised = tok(tokens, "elevation.raised") is not None
    dark = False
    try:
        dark = "dark" in json.dumps(tokens.get("color", {}).get("bg", {}).get("canvas", {}).get("$extensions", {}))
    except AttributeError:
        pass
    font_voice = ("serif-display" if fam or any(w in fam_name for w in ("serif", "literata", "georgia", "garamond"))
                  else "mono" if "mono" in fam_name else "technical-sans" if "geist" in fam_name or "plex" in fam_name
                  else "neutral-sans")
    rules = []
    # R1 палитра: нейтрали UI + акцент ≤ 3 % площади
    image_palette = [
        {"role": "background", "hex": canvas, "name": name_for(canvas), "share_max": 0.6, "applies_to": "walls, paper, empty surfaces", "source": "token", "token": "color.bg.canvas"},
        {"role": "dominant", "hex": n200, "name": name_for(n200), "share_max": 0.4, "applies_to": "large surfaces", "source": "token", "token": "primitive.color.neutral.200"},
        {"role": "secondary", "hex": n400, "name": name_for(n400), "share_max": 0.2, "applies_to": "secondary objects", "source": "token", "token": "primitive.color.neutral.400"},
        {"role": "shadow", "hex": text, "name": name_for(text), "share_max": 0.12, "applies_to": "shadows and dark details", "source": "token", "token": "color.text.primary"},
        {"role": "accent", "hex": accent, "name": name_for(accent), "share_max": 0.03, "applies_to": "one small object", "strict": True, "source": "token", "token": "color.accent.solid"}]
    illustration_palette = [
        {"role": "background", "hex": surface, "name": name_for(surface), "share_max": 0.6, "applies_to": "background", "source": "token", "token": "color.bg.surface"},
        {"role": "dominant", "hex": n200, "name": name_for(n200), "share_max": 0.4, "applies_to": "large shapes", "source": "token", "token": "primitive.color.neutral.200"},
        {"role": "text", "hex": text, "name": name_for(text), "share_max": 0.08, "applies_to": "lines and small details", "source": "token", "token": "color.text.primary"},
        {"role": "accent", "hex": accent, "name": name_for(accent), "share_max": 0.1, "applies_to": "one key element", "strict": True, "source": "token", "token": "color.accent.solid"}]
    if a200:
        illustration_palette.insert(2, {"role": "secondary", "hex": a200, "name": name_for(a200), "share_max": 0.2, "applies_to": "secondary shapes", "source": "token", "token": "primitive.color.accent.200"})
    rules.append("R1 палитра — нейтрали UI (canvas, neutral 200/400, text.primary) + акцент ≤ 3 % площади фото, ≤ 10 % иллюстрации")
    # R2 потолок хромы — на ступень ниже UI (ui 11/02 §4.4)
    caps = {"large_area_C_max": round(min(0.02, NC + 0.005), 3), "mid_area_C_max": 0.06, "small_area_C_max": round(min(AC, 0.2), 3)}
    rules.append("R2 хрома картинок по площади на ступень ниже UI: > 30 % кадра ≤ min(0,02; C нейтрали + 0,005)")
    # R3 запрещённые оттенки: 270–320° вне бренда
    if hue_in(AH, 270, 320):
        lo, hi = max(270, AH - 12), min(320, AH + 12)
        bands = [{"from": 270, "to": round(lo, 1), "reason": "пурпур (IMG-M05) вне бренд-акцента"} if lo > 270 else None,
                 {"from": round(lo, 1), "to": round(hi, 1), "reason": "полоса бренд-акцента: только акцент", "except_share_max": 0.03},
                 {"from": round(hi, 1), "to": 330, "reason": "пурпур и маджента (IMG-M05)"} if hi < 330 else None]
        bands = [b for b in bands if b]
        rules.append(f"R3 акцент {AH:.0f}° внутри 270–320°: полоса акцента ±12° только для акцента ≤ 3 %")
    else:
        bands = [{"from": 270, "to": 320, "reason": "пурпур и неон (IMG-M05); в бренде нет"}]
        rules.append("R3 полоса 270–320° запрещена: в бренде нет")
    # R4 баланс белого по температуре нейтрали
    tb, tol = WB_TARGET_B[temp]
    rules.append(f"R4 нейтраль {temp} (C {NC:.3f}, H {NH:.0f}°) → b нейтралей кадра {tb:+.3f} ± {tol}")
    # R5 грейд из характера: хрома по акценту, чёрная точка по теме
    chroma = 0.85 if AC < 0.12 else 0.92 if AC < 0.2 else 1.0
    grade = {"wb_ab": list(WB[temp]), "chroma": chroma, "black": 0.02 if dark else 0.03, "white": 0.98, "contrast": 0.1,
             "grain_pct": 1.0, "lut": {"size": 33, "file": None}, "applies_to": ["photo", "icon3d", "render3d", "video"],
             "note": "выведено из токенов (R5); утвердить глазом на canaries"}
    rules.append(f"R5 грейд: хрома ×{chroma} (акцент C {AC:.2f}), баланс белого по нейтрали, зерно 1 %")
    rules.append("R6 свет сверху-слева = направление теней UI (ui 07/02 §2.2)")
    depth = "soft-shadow" if has_raised else "border"
    ill = {"medium": "flat-illustration", "line_px": 1.5, "display_px": 160, "radius_px": radius,
           "perspective": "three-quarter" if has_raised else "flat-front", "fills": "flat",
           "shadows": "soft" if has_raised else "none", "background": "transparent", "accents_per_image": 2, "detail_min_px": 4,
           "saturation_offset": "на 1–2 шага ниже UI", "dark_theme": "two-files"}
    rules.append(f"R7 иллюстрации: радиус {radius:g} px = radius.md, линия 1,5 = штрих иконок, детали ≥ 4 px")
    rules.append("R8 абстрактный фон — кодом (CSS/SVG/WebGL), не генерацией")
    acc_name = name_for(accent)
    dna = {
        "dna_version": "0.1", "id": dna_id, "brand": "скелет из токенов UI", "checked_at": today(), "status": "draft", "approved_by": None,
        "derived_from_ui": {"tokens": tokens_path or "", "knobs": {
            "accent_hex": accent, "accent_oklch": [round(AL, 3), round(AC, 3), round(AH, 1)], "neutral_temp": temp,
            "neutral_C": round(NC, 3), "base_L": round(hex_oklch(canvas)[0], 3), "radius_px": radius, "font_voice": font_voice,
            "depth_model": depth, "theme": "both" if dark else "light"}, "rules_applied": rules},
        "character": {"adjectives": (adjectives or ["?", "?", "?"])[:3], "boldness": "restrained" if AC < 0.14 else "balanced"},
        "palette": {"image_palette": image_palette, "illustration_palette": illustration_palette, "chroma_caps": caps,
                    "median_chroma_max": 0.04, "forbidden_hues": bands, "neutral_wb": {"target_b": tb, "tol": tol},
                    "env_color": {"hex": canvas, "token": "color.bg.canvas", "note": "фон 3D и выреза = цвет секции страницы"}},
        "grade": grade,
        "light": {"direction": "left", "detail": "soft daylight from the upper left", "quality": "soft", "source": "window"},
        "camera": {"lens_mm": 50, "height": "eye-level", "angle": "eye-level", "depth_of_field": "medium",
                   "capture": "documentary, no styling"},
        "composition": {"subject_region": "right-third", "text_zone_default": {"side": "left", "share": 0.4},
                        "negative_space_min": 0.35, "max_elements": 3, "asymmetry": True, "edge_cut_allowed": True,
                        "master_ratio": "16:9", "phone_frame": "separate-master"},
        "subject_matter": {"domain_props": ["?", "?", "?"], "people_policy": "real-only", "product_policy": "real-photo-only"},
        "illustration": ill,
        "icon3d": {"material": f"matte ceramic in {name_for(n200)} with one {acc_name} part", "camera": "3/4 view from 30 degrees above, 50mm",
                   "key_light": "soft key from the upper left at 45 degrees, fill 20 percent", "fill_pct": 20,
                   "contact_shadow_alpha_max": 0.15, "margin_pct": 8, "accent_share_max": 0.15},
        "abstract": {"policy": "code-first"},
        "canaries": ["object: ?", "interior: ?", "nature: ?", "product-like: ?", "abstract: ?"],
        "style_blocks": {
            "illustration": (f"Flat vector illustration: simple geometric shapes with {radius:g} px rounded corners, flat fills in "
                             f"{name_for(n200)} {n200} and {name_for(surface)} with {acc_name} {accent} as the only accent, "
                             f"1.5 px lines in {name_for(text)} {text}, smooth flat colour only, one light from the upper left, "
                             f"plain flat {name_for(surface)} {surface} background, generous empty space."),
            "icon3d": (f"Single object as a matte ceramic figure in {name_for(n200)} with one {acc_name} part; 3/4 view from 30 "
                       f"degrees above, 50mm; soft key light from the upper left, gentle fill; soft contact shadow; plain light "
                       f"background; clean text-free surfaces.")},
        "exclusions": {"forbidden_markers": list(DEFAULT_MARKERS), "banned_words": list(DEFAULT_BANNED), "replace_with": [
            {"what": "people", "kind": "object", "replace_with": "no one in the frame"},
            {"what": "readable text", "kind": "artifact", "replace_with": "clean unmarked surfaces"}]},
        "post": {"grain_pct": 1.0, "scrim": {"color": text, "max_alpha": 0.55, "shape": "gradient", "percentile": 99.9},
                 "focal_required": True},
        "acceptance": dict(ACCEPTANCE_DEFAULT),
        "provenance": {"created_by": "script", "runs": 0, "notes": "vlm_to_dna.py from-tokens; фото-стиль (style_blocks.photo), "
                       "сюжеты и canaries заполняет человек или VLM по брендовым фото"},
    }
    return dna


# ---------------------------------------------------------------- паспорт → спецификация ассета (05-prompting v0.2)
MEDIUM_3D = (("glass", "glass-3d"), ("clay", "clay-3d"), ("ceramic", "clay-3d"), ("matte", "clay-3d"))


def pick_palette(entries, limit=5):
    order = {"dominant": 0, "background": 1, "secondary": 2, "accent": 3, "text": 4, "shadow": 5, "highlight": 6}
    sel = sorted(entries, key=lambda e: order.get(e["role"], 9))[:limit]
    acc = sum(e["share_max"] for e in sel if e["role"] == "accent")
    rest = sum(e["share_max"] for e in sel if e["role"] != "accent")
    k = min(1.0, (0.98 - acc) / rest) if rest > 0 else 1.0
    out = []
    for e in sel:
        p = {"role": e["role"], "hex": e["hex"].upper(), "name": e["name"],
             "share": round(e["share_max"] * (1 if e["role"] == "accent" else k), 3)}
        if e.get("applies_to"):
            p["applies_to"] = e["applies_to"]
        if e.get("strict"):
            p["strict"] = True
        out.append(p)
    return out


def to_spec(dna, kind, task, subject, slot="hero", ratio=None, text_zone=True, ref_class=None, dna_path=None, out_path=None,
            shot=None, section=None, purpose=None):
    comp, cam, light, pal = dna["composition"], dna["camera"], dna["light"], dna["palette"]
    if kind not in dna["style_blocks"]:
        raise SystemExit(f"в паспорте нет style_blocks.{kind}")
    entries = pal["image_palette"] if kind == "photo" else pal.get("illustration_palette") or pal["image_palette"]
    spec = {"spec_version": "0.2", "id": f"{dna['id']}-{slot}-{kind}", "checked_at": today(), "brief_language": "en",
            "task": task, "role": {"section": section or slot, "slot": slot, "purpose": purpose or f"{kind} of the {dna['id']} series",
                                   "series_id": dna["id"]},
            "subject": {"summary": subject},
            "composition": {"shot": shot or {"photo": "medium", "illustration": "medium", "icon3d": "close-up"}[kind]},
            "palette": pick_palette(entries, 4 if kind == "photo" and dna.get("references") else 5), "text": {"mode": "none"},
            "output": {"primary_ratio": ratio or (comp.get("master_ratio", "16:9") if kind == "photo" else "1:1"), "resolution": "1K"}}
    c = spec["composition"]
    if kind == "photo":
        c["subject_region"] = comp["subject_region"]
        if cam.get("angle"):
            c["angle"] = cam["angle"]
        spec["camera"] = {k: cam[k] for k in ("lens_mm", "depth_of_field", "capture") if k in cam}
        spec["light"] = {k: light[k] for k in ("direction", "quality", "time_of_day", "source") if light.get(k)}
        if dna.get("materials"):
            spec["materials"] = dna["materials"][:3]
        spec["style"] = {"medium": "photograph"}
        gp = dna["grade"].get("grain_pct", 0)
        if gp:
            spec["style"]["grain"] = "fine natural film grain" if gp < 2.5 else "visible natural film grain"
        tz = comp.get("text_zone_default")
        if text_zone and tz:
            s = tz["share"]
            rect = {"left": [0, 0, s, 1], "right": [round(1 - s, 3), 0, 1, 1], "top": [0, 0, 1, s], "bottom": [0, round(1 - s, 3), 1, 1]}[tz["side"]]
            bg = next((e for e in pal["image_palette"] if e["role"] == "background"), None)
            surface = tz.get("surface") or (bg["applies_to"] if bg and bg.get("applies_to") else "plain, evenly lit area")
            c["text_zone"] = {"side": tz["side"], "rect": rect, "tone": "even, low contrast", "surface": surface,
                              "purpose": "caption" if tz["side"] == "bottom" and s <= 0.3 else "headline"}
            spec["text"] = {"mode": "html_overlay"}
    elif kind == "icon3d":
        c["subject_region"] = "center"
        c["angle"] = "high-angle"
        ic = dna.get("icon3d", {})
        spec["light"] = {"direction": "left", "quality": "soft", "source": ic.get("key_light", "soft key from the upper left")}
        mat = ic.get("material", "")
        spec["style"] = {"medium": next((m for w, m in MEDIUM_3D if w in mat.lower()), "3d-render")}
        ents = pal.get("illustration_palette") or pal["image_palette"]
        bgc = next((e for e in ents if e["role"] == "background"), None)
        env = pal.get("env_color")
        if env:  # фон 3D-иконки = цвет секции страницы (W5 §8): рефлексы и контактная тень под него
            bgc = {"role": "background", "hex": env["hex"], "name": name_for(env["hex"]), "share_max": 0.55}
        body = next((e for e in ents if e["role"] in ("dominant", "secondary")), None)
        acc = next((e for e in ents if e["role"] == "accent"), None)
        spec["palette"] = pick_palette([dict(e, applies_to=t, share_max=sh) for e, t, sh in
                                        ((bgc, "plain background", 0.55), (body, "object body", 0.3), (acc, "single accent part of the object", 0.1)) if e])
        if mat:
            spec["materials"] = [mat]
    else:
        il = dna.get("illustration", {})
        medium = il.get("medium", "flat-illustration")
        spec["style"] = {"medium": medium if medium in ("flat-illustration", "vector", "line-art", "watercolor", "gouache", "collage") else "other"}
        if il.get("line_px"):
            spec["style"]["line"] = f"uniform {il['line_px']:g} px lines at {il.get('display_px', 160)} px width"
        c["subject_region"] = "center"
    spec["series"] = {"id": dna["id"], "block": dna["style_blocks"][kind], "avoid_average": bool(comp.get("asymmetry")) and kind == "photo"}
    refs = [r for r in dna.get("references", []) if r["role"] in ("style", "palette", "material")
            and (ref_class is None or r.get("class") == ref_class)][:3]
    if refs:
        base_in = Path(dna_path).parent if dna_path else Path.cwd()
        base_out = Path(out_path).parent if out_path else Path.cwd()
        spec["references"] = []
        for i, r in enumerate(refs, 1):
            src = r["src"] if re.match(r"^[a-z]+://", r["src"]) else os.path.relpath((base_in / r["src"]).resolve(), base_out.resolve())
            e = {"id": f"ref{i}", "src": src, "role": r["role"]}
            if r.get("note"):
                e["note"] = r["note"]
            spec["references"].append(e)
        spec["series"]["reference_ids"] = [e["id"] for e in spec["references"]]
    ex = dna["exclusions"].get("replace_with", [])
    if kind != "photo":  # фото-замены («soft late-morning daylight», «desk») не вносить в иллюстрации и 3D
        ex = [e for e in ex if e.get("kind") in ("artifact", "service")]
    if ex:
        spec["exclusions"] = [{k: e[k] for k in ("what", "kind", "replace_with") if e.get(k)} for e in ex]
    return spec


# ---------------------------------------------------------------- команды
def cmd_grid(a):
    size = make_grid(a.images, a.out, a.cell, a.cols)
    print(json.dumps({"grid": a.out, "size": size}, ensure_ascii=False))


def build_job(grid, out, model=VLM_MODEL, variant=1, tag="F-05-vlm-brand-brief"):
    rel = os.path.relpath(Path(grid).resolve(), Path(out).resolve().parent)
    return {"channel": "polza-chat", "method": "POST", "path": "/api/v1/chat/completions",
            "body": {"model": model, "temperature": 0.2, "response_format": {"type": "json_object"},
                     "messages": [{"role": "system", "content": VLM_SYSTEM},
                                  {"role": "user", "content": [{"type": "text", "text": VLM_USER},
                                                               {"type": "image_url", "image_url": {"url": rel}}]}]},
            "tag": tag, "agent": "F", "variant": variant, "max_rub": 3, "price_rub": 0.8, "price_source": PRICE_NOTE,
            "docs": "99-raw/cache/polza/2026-09-23/docs-repo/gaidy/chat-completions.mdx; gaidy/media-input.mdx (§2 base64)",
            "notes": "Паспорт визуала собирает машина по сетке бренд-картинок, утверждает человек [V:I9xdmNZxIfA 24:48]. "
                     "Локальный путь в image_url клиент кодирует в data:image/jpeg;base64. Разбор: vlm_to_dna.py parse.",
            "meta": {"test": tag.split("-vlm")[0] if tag.startswith("F-05") else tag, "judge": "metric+human", "repeat": 2}}


def cmd_build(a):
    job = build_job(a.grid, a.out, a.model, a.variant, a.tag)
    dump_json(job, a.out)
    print(json.dumps({"job": a.out, "model": a.model, "image": job["body"]["messages"][1]["content"][1]["image_url"]["url"]}, ensure_ascii=False))


def parse_response(resp_obj, dna_id, brand=None, grid=None, model=VLM_MODEL):
    v = extract_json(resp_obj)
    probs = vlm_problems(v)
    if any(p.startswith("нет ключа") or p.startswith("grade.") or p == "palette пуст" for p in probs):
        return None, {"vlm_problems": probs}
    measured = measure_image(grid) if grid else None
    dna = vlm_to_dna(v, dna_id, brand, measured, model)
    report = {"vlm_problems": probs}
    if measured:
        rows = palette_check(v["palette"], measured)
        report["palette_check"] = rows
        report["f05_palette_criterion"] = f"{sum(r['ok'] for r in rows)} из {len(rows)} hex в ΔE ≤ 0,05 (успех — ≥ 3 из 5)"
        report["f05_palette_pass"] = sum(r["ok"] for r in rows) >= 3
        report["invented_colours"] = [r["hex"] for r in rows if r.get("invented")]
    errs, eng = schema_errors(dna)
    lerrs, lwarns = lint(dna)
    report.update({"schema_errors": errs, "validator": eng, "lint_errors": lerrs, "lint_warnings": lwarns})
    return dna, report


def cmd_parse(a):
    resp = load_json(a.response)
    dna_id = a.id or re.sub(r"[^a-z0-9-]+", "-", Path(a.response).stem.lower()).strip("-")[:60] or "vlm-draft"
    dna, rep = parse_response(resp, dna_id, a.brand, a.grid, a.model)
    if dna is None:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        sys.exit(2)
    dump_json(dna, a.out)
    print(json.dumps({"dna": a.out, **rep}, ensure_ascii=False, indent=1))
    sys.exit(0 if not rep["schema_errors"] and not rep["lint_errors"] else 1)


def cmd_validate(a):
    bad = 0
    for p in a.files:
        dna = load_json(p)
        errs, eng = schema_errors(dna, force_builtin=a.builtin)
        lerrs, lwarns = lint(dna, p)
        ok = not errs and not lerrs
        bad += not ok
        print(json.dumps({"file": p, "ok": ok, "validator": eng, "schema_errors": errs[:20], "lint_errors": lerrs,
                          "lint_warnings": lwarns}, ensure_ascii=False, indent=1))
    sys.exit(1 if bad else 0)


def cmd_compare(a):
    print(json.dumps(compare(load_json(a.a), load_json(a.b)), ensure_ascii=False, indent=1))


def cmd_lut(a):
    dna = load_json(a.dna)
    write_lut(dna, a.out, a.size)
    print(json.dumps({"lut": a.out, "size": a.size, "grade": dna["grade"]}, ensure_ascii=False))


def cmd_from_tokens(a):
    tokens = load_json(a.tokens)
    adj = [x.strip() for x in a.adjectives.split(",")] if a.adjectives else None
    dna = from_tokens(tokens, a.id, adj, a.tokens)
    dump_json(dna, a.out)
    errs, eng = schema_errors(dna)
    lerrs, lwarns = lint(dna)
    print(json.dumps({"dna": a.out, "knobs": dna["derived_from_ui"]["knobs"], "schema_errors": errs, "validator": eng,
                      "lint_errors": lerrs, "lint_warnings": lwarns}, ensure_ascii=False, indent=1))


def cmd_to_spec(a):
    dna = load_json(a.dna)
    spec = to_spec(dna, a.kind, a.task, a.subject, a.slot, a.ratio, not a.no_text_zone, a.ref_class, a.dna, a.out, a.shot)
    errs, eng = schema_errors(spec, SPEC_SCHEMA_PATH)
    if a.out:
        dump_json(spec, a.out)
    print(json.dumps({"spec": a.out or "(stdout)", "asset_spec_errors": errs, "validator": eng,
                      **({} if a.out else {"body": spec})}, ensure_ascii=False, indent=1))
    sys.exit(1 if errs else 0)


# ---------------------------------------------------------------- самопроверка
STUB_GOOD = {  # правдоподобный ответ VLM по сетке autumn: цвета близко к снятым локально
    "character": {"adjectives": ["calm", "natural", "seasonal"]},
    "palette": [{"hex": "#7A6A33", "name": "olive ochre", "role": "dominant", "share": 0.3},
                {"hex": "#5E4E22", "name": "dark ochre grass", "role": "secondary", "share": 0.25},
                {"hex": "#9C8A50", "name": "dry khaki", "role": "secondary", "share": 0.15},
                {"hex": "#2A2210", "name": "umber shadow", "role": "shadow", "share": 0.12},
                {"hex": "#9FC9EA", "name": "pale sky", "role": "background", "share": 0.06}],
    "grade": {"white_balance": "warm", "contrast": "medium", "saturation": "natural", "black_point": "neutral", "grain": "fine"},
    "light": {"direction": "late-morning sun from the upper left", "quality": "soft", "time_of_day": "late morning", "color_temp_K": 5200},
    "camera": {"lens_mm": 35, "height": "eye-level", "depth_of_field": "deep"},
    "composition": {"subject_region": "tree line across the upper third", "horizon_position": "top-third", "negative_space": "high",
                    "crop_style": "wide, lawn fills the lower half"},
    "subject_matter": {"domain_props": ["lawn", "fallen leaves", "birch trees", "pine trees", "maple with red leaves"],
                       "motifs": ["autumn foliage", "open lawn"], "people_policy": "none"},
    "style_block_photo": ("Documentary outdoor photograph of a city park in early autumn, soft late-morning sun, yellow and rust "
                          "foliage over a muted green lawn with scattered fallen leaves, pale clear sky, 35mm at eye level, deep "
                          "depth of field, fine natural grain, no retouching."),
    "exclusions": ["golden-hour glow", "shallow depth of field", "saturated orange cast", "people posing", "fog or mist", "lens flare"],
    "canaries": ["a ceramic mug on a garden table", "a small cafe interior at noon", "a riverside path with one oak",
                 "soft abstract shapes of leaves", "a folded paper map on a bench"]}
STUB_BAD = copy.deepcopy(STUB_GOOD)  # «идеализированные» насыщенные цвета — как часто пишет VLM
STUB_BAD["palette"] = [{"hex": "#E8A33D", "name": "golden yellow", "role": "dominant", "share": 0.3},
                       {"hex": "#C4452B", "name": "rust red", "role": "accent", "share": 0.1},
                       {"hex": "#4F7A2E", "name": "grass green", "role": "secondary", "share": 0.3},
                       {"hex": "#87CEEB", "name": "sky blue", "role": "background", "share": 0.2},
                       {"hex": "#3B2A1A", "name": "bark brown", "role": "shadow", "share": 0.1}]
STUB_BAD["grade"]["saturation"] = "vivid"
STUB_BAD["style_block_photo"] = "A stunning cinematic autumn park, vibrant golden foliage, dramatic light."


def selftest():
    import tempfile
    res, fails = [], []

    def check(name, cond, info=""):
        res.append(("PASS" if cond else "FAIL", name, info))
        if not cond:
            fails.append(name)

    tmp = Path(tempfile.mkdtemp(prefix="vlm_to_dna_"))
    # 1. build воспроизводит задание F-05 (текст запроса, модель, формат ответа)
    job = build_job(ROOT / "99-raw/phase5/inputs/F/brand_grid_autumn.jpg", F05_JOB)
    ref = load_json(F05_JOB)
    same = (job["body"]["model"] == ref["body"]["model"] and job["body"]["messages"][0] == ref["body"]["messages"][0]
            and job["body"]["messages"][1]["content"][0] == ref["body"]["messages"][1]["content"][0]
            and job["body"]["messages"][1]["content"][1]["image_url"]["url"] == ref["body"]["messages"][1]["content"][1]["image_url"]["url"]
            and job["body"]["response_format"] == ref["body"]["response_format"])
    check("build = задание F-05 (модель, system, текст, путь картинки, json_object)", same)
    # 2. разбор ответа: chat completion с ```json и хвостом
    wrapped = {"choices": [{"message": {"content": "Here you go:\n```json\n" + json.dumps(STUB_GOOD) + "\n```\nDone."}}]}
    grid = ROOT / "99-raw/phase5/inputs/F/brand_grid_autumn.jpg"
    dna, rep = parse_response(wrapped, "vlm-autumn-good", "заглушка", str(grid))
    check("parse: ответ в ```json → паспорт проходит схему", dna is not None and not rep["schema_errors"], rep.get("schema_errors"))
    check("parse: линт без ошибок", dna is not None and not rep["lint_errors"], rep.get("lint_errors"))
    check("parse: критерий F-05 по палитре (правдоподобная заглушка) — выполнен", rep.get("f05_palette_pass") is True, rep.get("f05_palette_criterion"))
    check("parse: баланс белого из замера сетки тёплый (b > 0,005)", dna["palette"]["neutral_wb"]["target_b"] > 0.005, dna["palette"]["neutral_wb"])
    dump_json(dna, tmp / "good.json")
    dna_b, rep_b = parse_response(STUB_BAD, "vlm-autumn-bad", "заглушка", str(grid))
    check("parse: «идеализированная» палитра — критерий F-05 не выполнен", rep_b.get("f05_palette_pass") is False, rep_b.get("f05_palette_criterion"))
    check("parse: «golden yellow 30 %» — цвет с покрытием < 1/3 заявленной доли помечен как придуманный",
          "#E8A33D" in rep_b.get("invented_colours", []) and not rep.get("invented_colours"), (rep_b.get("invented_colours"), rep.get("invented_colours")))
    check("parse: слова stunning/cinematic/vibrant/dramatic ловит линт", any("запрещённые слова" in e for e in rep_b["lint_errors"]), rep_b["lint_errors"])
    broken = copy.deepcopy(STUB_GOOD)
    del broken["grade"]
    d0, r0 = parse_response(broken, "x", None, None)
    check("parse: нет grade → отказ с причиной", d0 is None and any("grade" in p for p in r0["vlm_problems"]), r0["vlm_problems"][:3])
    # 3. сравнение двух прогонов
    c = compare(dna, dna_b)
    check("compare: разная насыщенность → «grade и light не совпали»", c["same_grade_and_light"] is False, c)
    c2 = compare(dna, load_json(tmp / "good.json"))
    check("compare: тот же прогон → совпали, ΔE палитр 0", c2["same_grade_and_light"] and c2["palette_dE_sym_mean"] == 0, c2)
    # 4. три примера паспортов: схема (jsonschema или встроенный) и линт
    for p in sorted(EXAMPLES.glob("dna-*.json")):
        d = load_json(p)
        e1, eng = schema_errors(d)
        e2, _ = schema_errors(d, force_builtin=True)
        le, lw = lint(d, p)
        check(f"пример {p.name}: схема ({eng}) и встроенный валидатор — 0 ошибок, линт — 0 ошибок", not e1 and not e2 and not le, (e1 or e2 or le)[:3])
    # 5. сломанный паспорт ловят оба валидатора
    d = load_json(EXAMPLES / "dna-warm-consumer.json")
    d["palette"]["image_palette"][0]["hex"] = "#7B6A3"
    d["composition"]["subject_region"] = "left"
    d["grade"]["chroma"] = 2
    d["extra"] = 1
    e1, eng = schema_errors(d)
    e2, _ = schema_errors(d, force_builtin=True)
    check("сломанный паспорт: ≥ 4 ошибки у обоих валидаторов", len(e1) >= 4 and len(e2) >= 4, (len(e1), len(e2), eng))
    d = load_json(EXAMPLES / "dna-strict-saas.json")
    d["palette"]["image_palette"].append({"role": "secondary", "hex": "#8B5CF6", "name": "violet", "share_max": 0.2})
    le, _ = lint(d)
    check("линт: фиолетовый #8B5CF6 (293°) с долей 0,2 в запрещённой полосе", any("запрещённой полосе" in e for e in le), le)
    # 6. LUT из паспорта = LUT опыта F/05
    lut = write_lut(load_json(EXAMPLES / "dna-warm-consumer.json"), tmp / "warm.cube")
    a_, b_ = cube_numbers(lut), cube_numbers(F05 / "brand_warm_consumer.cube")
    diff = max(max(abs(x - y) for x, y in zip(r1, r2)) for r1, r2 in zip(a_, b_)) if a_ and len(a_) == len(b_) else None
    check("lut: паспорт warm-consumer → .cube совпадает с F/05 brand_warm_consumer.cube", diff is not None and diff < 1e-6, f"max|Δ| = {diff}")
    # 7. from-tokens на мини-наборе DTCG (алиасы, oklch+hex, px)
    toks = {"primitive": {"color": {"neutral": {"200": {"$value": {"colorSpace": "oklch", "components": [0.929, 0.013, 255.5], "hex": "#e2e8f0"}},
                                                "400": {"$value": {"hex": "#90a1b9"}}, "500": {"$value": {"hex": "#62748e"}},
                                                "50": {"$value": {"hex": "#f8fafc"}}},
                                    "accent": {"600": {"$value": {"hex": "#155dfc"}}, "200": {"$value": {"hex": "#bedbff"}}}},
                          "font": {"family": {"sans": {"$value": ["Inter", "sans-serif"]}}}, "size": {"6": {"$value": {"value": 6, "unit": "px"}}}},
            "color": {"bg": {"canvas": {"$value": "{primitive.color.neutral.50}"}, "surface": {"$value": "#ffffff"}},
                      "text": {"primary": {"$value": "#0f172b"}}, "accent": {"solid": {"$value": "{primitive.color.accent.600}"}},
                      "border": {"subtle": {"$value": "{primitive.color.neutral.200}"}}},
            "radius": {"md": {"$value": "{primitive.size.6}"}}}
    dt_ = from_tokens(toks, "tokens-demo", ["строгий", "плотный", "технический"])
    e1, _ = schema_errors(dt_)
    le, lw = lint(dt_)
    k = dt_["derived_from_ui"]["knobs"]
    check("from-tokens: скелет проходит схему и линт", not e1 and not le, (e1 or le)[:3])
    check("from-tokens: алиасы разрешены (canvas #F8FAFC, акцент #155DFC, радиус 6)", dt_["palette"]["image_palette"][0]["hex"] == "#F8FAFC"
          and k["accent_hex"] == "#155DFC" and k["radius_px"] == 6, k)
    check("from-tokens: холодная slate-нейтраль → cool, b −0,004", k["neutral_temp"] == "cool" and dt_["palette"]["neutral_wb"]["target_b"] == -0.004, k)
    # 8. паспорт → спецификация ассета проходит схему 05-prompting; компилятор D2 вставляет блок стиля дословно
    wc = EXAMPLES / "dna-warm-consumer.json"
    spec = to_spec(load_json(wc), "photo", "IMG-HERO-PHOTO", "a weathered wooden park bench under a birch tree", "hero", None, True,
                   "exterior-park-autumn", wc, tmp / "spec.json")
    e1, eng = schema_errors(spec, SPEC_SCHEMA_PATH)
    check(f"to-spec: спецификация проходит asset-spec.schema.json ({eng})", not e1, e1[:3])
    check("to-spec: сумма долей палитры ≤ 1, ≤ 5 цветов", sum(p["share"] for p in spec["palette"]) <= 1.0 and len(spec["palette"]) <= 5,
          [p["share"] for p in spec["palette"]])
    dump_json(spec, tmp / "spec.json")
    venv = Path(kbpaths.python())
    py = str(venv) if venv.exists() else sys.executable
    r = subprocess.run([py, str(TOOLS / "prompt_compile.py"), "compile", str(tmp / "spec.json"), "--model", "openai/gpt-image-2.5-sunburst"],
                       capture_output=True, text=True, timeout=120)
    block = load_json(wc)["style_blocks"]["photo"]
    check("prompt_compile: блок стиля паспорта дословно в промте GPT Image 2.5", r.returncode == 0 and block in r.stdout,
          (r.stderr or r.stdout)[-300:] if r.returncode else "")
    for s in res:
        print(f"{s[0]}  {s[1]}" + (f"  → {s[2]}" if s[0] == "FAIL" or (s[2] and 'F-05' in s[1]) else ""))
    print(f"итого: {len(res) - len(fails)}/{len(res)} PASS; временные файлы: {tmp}")
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("grid"); s.add_argument("images", nargs="+"); s.add_argument("--out", required=True)
    s.add_argument("--cell", type=int, default=640); s.add_argument("--cols", type=int, default=3); s.set_defaults(f=cmd_grid)
    s = sub.add_parser("build"); s.add_argument("grid"); s.add_argument("--out", required=True); s.add_argument("--model", default=VLM_MODEL)
    s.add_argument("--variant", type=int, default=1); s.add_argument("--tag", default="F-05-vlm-brand-brief"); s.set_defaults(f=cmd_build)
    s = sub.add_parser("parse"); s.add_argument("response"); s.add_argument("--out", required=True); s.add_argument("--grid")
    s.add_argument("--id"); s.add_argument("--brand"); s.add_argument("--model", default=VLM_MODEL); s.set_defaults(f=cmd_parse)
    s = sub.add_parser("validate"); s.add_argument("files", nargs="+"); s.add_argument("--builtin", action="store_true"); s.set_defaults(f=cmd_validate)
    s = sub.add_parser("compare"); s.add_argument("a"); s.add_argument("b"); s.set_defaults(f=cmd_compare)
    s = sub.add_parser("lut"); s.add_argument("dna"); s.add_argument("--out", required=True); s.add_argument("--size", type=int, default=33)
    s.set_defaults(f=cmd_lut)
    s = sub.add_parser("from-tokens"); s.add_argument("tokens"); s.add_argument("--out", required=True); s.add_argument("--id", default="from-tokens")
    s.add_argument("--adjectives"); s.set_defaults(f=cmd_from_tokens)
    s = sub.add_parser("to-spec"); s.add_argument("dna"); s.add_argument("--kind", required=True, choices=["photo", "illustration", "icon3d"])
    s.add_argument("--task", required=True); s.add_argument("--subject", required=True); s.add_argument("--slot", default="hero")
    s.add_argument("--ratio"); s.add_argument("--shot"); s.add_argument("--no-text-zone", action="store_true"); s.add_argument("--ref-class")
    s.add_argument("--out"); s.set_defaults(f=cmd_to_spec)
    s = sub.add_parser("selftest"); s.set_defaults(f=lambda a: sys.exit(selftest()))
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
