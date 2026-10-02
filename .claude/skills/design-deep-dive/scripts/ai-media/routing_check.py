#!/usr/bin/env python3
"""routing_check.py — сверка матрицы маршрутов kb/ai-media/13-routing-matrix/routing.yaml с каталогами моделей.

Сигнал, а не стоп: расхождение варианта с каталогом (модель выбыла, сменился id, цена или параметр) говорит, что строку
матрицы надо сверить перед заданием; генерацию останавливают `estimate` задания с ошибкой и отсутствие «да» заказчика,
а не этот отчёт. Без сети и без ключей.

Снимки каталогов — последние в $DDD_HOME/cache/ai-media/{polza,routerai,genapi}/ (ставит `scripts/install.sh
--catalogs`, обновляют `polza_catalog.py snapshot` и `mp_client.py snapshot --channel all`); другой снимок — ключами
--polza, --routerai, --genapi (имя папки или путь). Поле `catalog_snapshots` матрицы — имена папок снимков, с которыми её
сверяли при обновлении (имя без пути; путь в поле — предупреждение); отчёт показывает их рядом со снимками прогона.

Проверяет:
  1. разбор YAML, `version` (1 или 2), `checked_at`, маршрут на каждый код таксономии (код вне таксономии — с
     `proposal: true`), обязательные поля маршрута, `delivery` из `defaults.delivery`, метки `label` из `enums.labels`;
  2. у варианта (`options`) — роль, канал из `enums.channel`, поле `final`;
  3. polza: модель есть в снимке, провайдер — из провайдеров модели (или `top_provider`), параметры проходят
     `polza_catalog.validate`, цена = `polza_catalog.estimate` (± 1 % или ± 0,02 ₽);
  4. routerai, genapi: модель (сеть) есть в своём снимке, цена — по прайсу канала (± 2 %; у токенных GPT Image — выход
     medium по формуле mp_client не выше заявленной цены, заявленная ≤ выход × 2,5 — вход картинки);
  5. polza-chat: чат-модель есть в снимке polza; polza-images: модель есть, цена не ниже ступени 1K;
  6. external — есть `access`; local, code, blender — есть `tool`;
  7. диалект — семейство есть в 05-prompting/dialects.yaml, формат совпадает;
  8. `check.audit_mode` — из enums, `check.rubric` — файл 11-evaluation-qa/rubrics/<имя>.rubric.json;
  9. флаги `legal` маршрута и варианта — из enums; модель с флагом research — только `final: false`; `minimax/*` — с
     флагом `visible-vendor-mark` (условия вендора: метка в контенте); строки политики 12–14 (люди) — флаг маршрута
     `people-consent`;
 10. устаревшие модели (`defaults.deprecated`) — не среди вариантов (в `not` можно; с `until` не раньше `checked_at` —
     предупреждение);
 11. выбывшие модели (`defaults.unavailable` и `defaults.unavailable_<дата>`: `model`, `error`) — вариантом только с
     `final: false` или в `not`; `defaults.not_routes` — у записи `what` и `why`;
 12. покрытие компилятора: модель варианта канала, описанного в `channels` файла 05-prompting/dialects.yaml (routerai,
     genapi), есть в `channels.<канал>.models` — иначе предупреждение: prompt_compile.py задание канала для неё не соберёт;
 13. поля маршрута: `conditions` — список непустых строк; `resolution_by` — у каждой модели `param` из параметров
     каталога (значения `values` — из значений параметра; у параметра не `resolution` `values` обязательны) или
     `operations` из операций модели в каталоге.

Запуск:  routing_check.py [ROUTING.yaml] [--polza SNAP] [--routerai SNAP] [--genapi SNAP] [--json OUT.json] [--md OUT.md]
         routing_check.py --selftest        проверки матрицы на вымышленных данных: без сети и без снимков каталогов
Код выхода: 0 — расхождений нет (предупреждения допустимы); 1 — есть расхождения (раздел «Ошибки» отчёта) или упала
самопроверка; 2 — нет снимка каталога polza.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))  # scripts/lib: kbpaths
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("ai-media")
sys.path.insert(0, str(HERE))
import polza_catalog as pc  # noqa: E402

try:
    import mp_client as mp  # noqa: E402
except Exception:  # pragma: no cover
    mp = None

TAXONOMY = [
    "IMG-HERO-PHOTO", "IMG-PRODUCT", "IMG-ILLUSTR", "IMG-SERIES", "IMG-ICON3D", "IMG-CUTOUT", "IMG-BG-ABSTRACT",
    "IMG-TEXTURE", "IMG-TEXT-LATIN", "IMG-TEXT-CYR", "IMG-EDIT", "IMG-OUTPAINT", "IMG-MOCKUP", "IMG-UPSCALE", "IMG-DRAFT",
    "VID-HERO-LOOP", "VID-CINEMAGRAPH", "VID-I2V-PRODUCT", "VID-ABSTRACT", "VID-CAMERA", "VID-CHARACTER", "VID-LONG",
    "VID-V2V", "VID-ALPHA", "VID-SCROLL", "VID-UPSCALE",
    "VEC-ICON-LINE", "VEC-ICON-FILLED", "VEC-ILLUSTR", "VEC-PATTERN", "VEC-ANIM", "VEC-TRACE",
]
MODEL_CHANNELS = {"polza", "polza-chat", "polza-images", "routerai", "genapi"}
TOOL_CHANNELS = {"local", "code", "blender"}
ROLES = {"primary", "alt", "fallback", "cheap", "premium", "draft", "alpha", "mask", "scheme", "ultrawide", "regen",
         "local", "external", "exact"}


class Report:
    def __init__(self):
        self.errors, self.warnings, self.rows = [], [], []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def near(a: float, b: float, rel: float, abs_: float = 0.02) -> bool:
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def ra_price(cat, mid: str, params: dict) -> tuple[float | None, str]:
    m = cat.models.get(mid)
    ip = (m.get("image_pricing") or [{}])[0] if m else {}
    unit, price = ip.get("unit"), ip.get("price")
    if price is None:
        return None, "цена в каталоге не указана"
    price = float(price)
    if unit == "image":
        return price, "за картинку"
    if unit == "megapixel":
        return price * 1.0, "за 1 Мп (1024²)"
    if unit == "token" and mp is not None:
        fam = mp.gpt_family(mid)
        if fam:
            w, h = mp.GPT25_SIZES.get(params.get("aspect_ratio", "1:1"), (1024, 1024)) if fam == "gpt-image-2.5" \
                else mp.GPT2_SIZES.get(params.get("aspect_ratio", "1:1"), (1024, 1024))
            q = params.get("quality", "medium")
            tok = mp.gpt_image_tokens(fam, w, h, q)
            return tok * price, f"выход {tok} ток. × {price:.6f} ₽ ({fam}, {q}, {w}×{h}); вход — сверху"
    return None, f"единица {unit} не разобрана"


def ga_price(cat, slug: str, params: dict) -> tuple[float | None, str]:
    n = cat.nets.get(slug)
    if n is None:
        return None, "нет сети"
    if n.get("cost") is not None:
        return float(n["cost"]), "cost каталога"
    rows = mp.genapi_table(cat.prices.get(slug)) if mp else []
    want = {"vector": params.get("model"), "pro": params.get("pro")}
    for r in rows:
        model_ok = want["vector"] is None or str(r.get("Модель", "")).lower() == str(want["vector"]).lower()
        pro_ok = want["pro"] is None or (("Выключен" in str(r.get("Pro", ""))) == (want["pro"] is False))
        if model_ok and pro_ok:
            val = mp.rub_of(r.get("Цена за изображение") or r.get("Цена"))
            if val is not None:
                return val, "прайс Gen-API"
    return None, "цена не найдена в прайсе"


def people_rows(rows) -> bool:
    """Есть ли среди policy_rows строки 12–14 таблицы ai-media 12/04 §2 (люди-декор, реальные люди, клиенты и команда)."""
    nums = set()
    for row in rows or []:
        for chunk in re.findall(r"стр\. ([0-9][0-9,–\- ]*)", str(row)):
            for part in re.split(r",\s*", chunk.strip()):
                m = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part.strip())
                if m:
                    nums.update(range(int(m.group(1)), int(m.group(2)) + 1))
                elif part.strip().isdigit():
                    nums.add(int(part.strip()))
    return bool(nums & {12, 13, 14})


def check_matrix(rep: Report, data: dict, snap, ra, ga, dialects: dict, rubrics: set) -> dict:
    """Проверки матрицы data против снимка polza snap, каталогов RouterAI ra и Gen-API ga (None — каталог не загружен),
    файла диалектов и имён рубрик. Находки — в rep.errors и rep.warnings, строки вариантов — в rep.rows. Возвращает
    снимки матрицы (`catalog_snapshots`: канал → имя папки)."""
    if data.get("version") not in (1, 2):
        rep.err("root", f"version = {data.get('version')!r}, ожидается 1 или 2")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(data.get("checked_at", ""))):
        rep.err("root", "checked_at не дата")
    enums = data.get("enums", {})
    channels = set(enums.get("channel", {}))
    flags_ok = set(enums.get("legal_flags", {}))
    labels_ok = set(enums.get("labels", []))
    modes_ok = set(enums.get("audit_modes", []))
    defaults = data.get("defaults", {}) or {}
    deprecated = [str(x).split(" ")[0] for x in defaults.get("deprecated", [])]
    # выбывшие модели (defaults.unavailable, defaults.unavailable_<дата>) и «не маршруты» (defaults.not_routes)
    unavailable = {}
    for key, lst in defaults.items():
        if not str(key).startswith("unavailable"):
            continue
        for i, u in enumerate(lst or []):
            if not isinstance(u, dict) or not u.get("model") or not u.get("error"):
                rep.err(f"defaults.{key}#{i + 1}", "нужны поля model и error")
                continue
            unavailable[str(u["model"])] = key
    for i, nr in enumerate(defaults.get("not_routes") or []):
        if not isinstance(nr, dict) or not nr.get("what") or not nr.get("why"):
            rep.err(f"defaults.not_routes#{i + 1}", "нужны поля what и why")

    pinned = {}
    for k, v in (data.get("catalog_snapshots") or {}).items():
        if not v:
            continue
        pinned[k] = Path(str(v)).name
        if pinned[k] != str(v):
            rep.warn(f"catalog_snapshots.{k}", f"{v!r} — путь: в поле пишется имя папки снимка ({pinned[k]})")
    families = dialects.get("families", {})
    compiler = {c: set((v or {}).get("models") or {}) for c, v in (dialects.get("channels") or {}).items()}
    routes = data.get("routes", {})
    for code in TAXONOMY:
        if code not in routes:
            rep.err(code, "нет маршрута для кода таксономии")
    for code, r in routes.items():
        if code not in TAXONOMY and not r.get("proposal"):
            rep.err(code, "код вне таксономии без proposal: true")
        where = code
        for key in ("name", "options", "dialect", "check", "delivery", "legal", "label", "checked", "decides"):
            if key not in r:
                rep.err(where, f"нет поля {key}")
        if r.get("delivery") and r["delivery"] not in data.get("defaults", {}).get("delivery", {}):
            rep.err(where, f"delivery {r['delivery']!r} не описан в defaults.delivery")
        # метки
        for lab in re.findall(r"\[[^\]]+\]", str(r.get("label", ""))):
            base = lab.split(":")[0] + ("]" if ":" in lab else "")
            if base not in labels_ok:
                rep.err(where, f"метка {lab} не из enums.labels")
        # диалект
        dia = r.get("dialect") or {}
        fam = dia.get("family")
        if fam:
            if fam not in families:
                rep.err(where, f"семейство диалекта {fam!r} нет в dialects.yaml")
            elif dia.get("format") and families[fam].get("format") != dia["format"]:
                rep.err(where, f"формат {dia['format']!r} ≠ dialects.yaml {families[fam].get('format')!r} ({fam})")
        # проверка
        chk = r.get("check") or {}
        if chk.get("audit_mode") not in modes_ok:
            rep.err(where, f"audit_mode {chk.get('audit_mode')!r} не из enums.audit_modes")
        if chk.get("rubric") and chk["rubric"] not in rubrics:
            rep.err(where, f"рубрики {chk['rubric']!r} нет в 11-evaluation-qa/rubrics/")
        # право
        for f in (r.get("legal") or {}).get("flags", []):
            if f not in flags_ok:
                rep.err(where, f"флаг legal {f!r} не из enums.legal_flags")
        if people_rows((r.get("legal") or {}).get("policy_rows", [])) and \
                "people-consent" not in ((r.get("legal") or {}).get("flags") or []):
            rep.err(where, "строки политики 12–14 (люди) без флага people-consent (ai-media 12/04 §2)")
        # варианты
        if not r.get("options"):
            rep.err(where, "пустой options")
        for i, o in enumerate(r.get("options") or []):
            w = f"{code}#{i + 1}({o.get('role')})"
            ch = o.get("channel")
            if o.get("role") not in ROLES:
                rep.err(w, f"роль {o.get('role')!r} не из списка")
            if ch not in channels:
                rep.err(w, f"канал {ch!r} не из enums.channel")
                continue
            if "final" not in o:
                rep.err(w, "нет поля final")
            for f in o.get("legal", []) or []:
                if f not in flags_ok:
                    rep.err(w, f"флаг {f!r} не из enums")
            mid = o.get("model")
            if mid and any(mid == d for d in deprecated):
                until = str(o.get("until") or "")
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", until) and until >= str(data.get("checked_at")):
                    rep.warn(w, f"устаревающая модель {mid} — только до {until}")
                else:
                    rep.err(w, f"устаревшая модель {mid} среди вариантов (нет until ≥ checked_at)")
            if mid and mid in unavailable and o.get("final") is not False:
                rep.err(w, f"модель {mid} выбыла (defaults.{unavailable[mid]}) — вариантом только с final: false или в not")
            if mid and mid.startswith("minimax/") and "visible-vendor-mark" not in (o.get("legal") or []):
                rep.err(w, "MiniMax без флага visible-vendor-mark (ToS: «prominent mark… within generated content», ai-media 12/01 §2)")
            if mid == "qwen/image-2.1" or "research" in (o.get("legal") or []):
                if o.get("final") is not False:
                    rep.err(w, "модель с флагом research должна быть final: false (ai-media 12/01 §5)")
                if "research" not in (o.get("legal") or []):
                    rep.err(w, "qwen/image-2.1 без флага legal research")
            if mid and ch in compiler and mid not in compiler[ch]:
                rep.warn(w, f"модели {mid} нет в channels.{ch}.models файла 05-prompting/dialects.yaml — prompt_compile.py "
                            f"задание канала для неё не соберёт")
            row = {"code": code, "role": o.get("role"), "channel": ch, "model": mid or o.get("tool", "")[:60],
                   "provider": o.get("provider"), "declared": o.get("price_rub"), "catalog": None, "status": "ok", "note": ""}
            if ch in TOOL_CHANNELS:
                if not o.get("tool"):
                    rep.err(w, "нет tool")
            elif ch == "external":
                if not o.get("access"):
                    rep.err(w, "нет access у внешнего варианта")
            elif ch == "polza":
                m = snap.by_id.get(mid)
                if m is None:
                    rep.err(w, f"модели {mid} нет в снимке polza {snap.dir.name}")
                    row["status"] = "нет модели"
                else:
                    provs = [p.get("slug") or p.get("name") for p in (snap.providers.get(mid) or [])]
                    top = (m.get("top_provider") or {})
                    top_name = top.get("slug") or top.get("name")
                    prov = o.get("provider")
                    if prov and provs and prov not in provs:
                        rep.err(w, f"провайдер {prov} не из {provs}")
                    if prov and not provs and prov != top_name:
                        rep.err(w, f"провайдер {prov} ≠ top_provider {top_name}")
                    params = dict(o.get("params") or {})
                    # заглушки входов: inputs: {images: N, videos: N, first_frame_url: true, last_frame_url: true}
                    ins = o.get("inputs") or {}
                    full = dict(params)
                    if ins.get("images"):
                        full["images"] = ["ref.png"] * int(ins["images"])
                    if ins.get("videos"):
                        full["videos"] = ["ref.mp4"] * int(ins["videos"])
                    for fld in ("first_frame_url", "last_frame_url", "mask_url"):
                        if ins.get(fld):
                            full[fld] = "ref.png"
                    try:
                        inp2, _notes = pc.coerce_input(pc.provider_view(m, prov, snap.providers.get(mid))[2], full)
                    except Exception:
                        inp2 = full
                    issues = pc.validate(m, inp2, provider=prov, providers=snap.providers.get(mid))
                    for iss in issues:
                        if iss.get("level") == "error" and iss.get("param") not in ("prompt", "images", "videos"):
                            rep.err(w, f"параметр {iss['param']}: {iss['msg']}")
                    est = pc.estimate(m, inp2, provider=prov, providers=snap.providers.get(mid),
                                      ref_seconds=o.get("ref_seconds"))
                    row["catalog"] = est.get("rub")
                    if o.get("price_rub") is None:
                        rep.err(w, "нет price_rub")
                    elif est.get("rub") is None:
                        rep.warn(w, "каталог не дал цену")
                    elif not near(float(o["price_rub"]), float(est["rub"]), 0.01):
                        rep.err(w, f"цена {o['price_rub']} ≠ каталог {est['rub']} ({est.get('formula', '')})")
                        row["status"] = "цена"
                    # ценовые параметры явно
                    pparams = pc.price_params(m, None, None) if hasattr(pc, "price_params") else []
                    try:
                        _n, pr, prm = pc.provider_view(m, prov, snap.providers.get(mid))
                        pparams = pc.price_params(m, pr, prm)
                    except Exception:
                        pass
                    for pp in pparams or []:
                        if pp in ("images", "videos", "has_video", "prompt"):
                            continue
                        if pp not in params and pp in (prm or {}):
                            rep.warn(w, f"ценовой параметр {pp} не задан явно")
            elif ch in ("polza-chat", "polza-images"):
                m = snap.by_id.get(mid)
                if m is None:
                    rep.err(w, f"модели {mid} нет в снимке polza")
                elif ch == "polza-chat" and m.get("type") != "chat":
                    rep.err(w, f"{mid} — не чат-модель ({m.get('type')})")
                elif ch == "polza-images":
                    est = pc.estimate(m, {"image_resolution": "1K"}, providers=snap.providers.get(mid))
                    row["catalog"] = est.get("rub")
                    if est.get("rub") and o.get("price_rub") is not None and float(o["price_rub"]) + 0.01 < float(est["rub"]):
                        rep.err(w, f"цена {o['price_rub']} ниже ступени 1K {est['rub']}")
            elif ch == "routerai":
                if ra is None:
                    rep.warn(w, "каталог RouterAI не загружен")
                elif mid not in ra.models:
                    rep.err(w, f"модели {mid} нет в каталоге RouterAI {ra.path.parent.name}")
                    row["status"] = "нет модели"
                else:
                    val, how = ra_price(ra, mid, o.get("params") or {})
                    row["catalog"], row["note"] = val, how
                    dec = o.get("price_rub")
                    if val is None:
                        if dec is not None:
                            rep.warn(w, f"RouterAI: {how}, заявлено {dec}")
                    elif (ra.models[mid].get("image_pricing") or [{}])[0].get("unit") == "token":
                        if dec is None or dec + 0.01 < val or dec > val * 2.5:
                            rep.err(w, f"RouterAI токены: заявлено {dec}, выход {val:.4f} ({how})")
                    elif dec is None or not near(float(dec), val, 0.02):
                        rep.err(w, f"RouterAI цена {dec} ≠ каталог {val:.4f} ({how})")
                        row["status"] = "цена"
            elif ch == "genapi":
                if ga is None:
                    rep.warn(w, "каталог Gen-API не загружен")
                elif mid not in ga.nets:
                    rep.err(w, f"сети {mid} нет в каталоге Gen-API {ga.path.parent.name}")
                    row["status"] = "нет модели"
                else:
                    val, how = ga_price(ga, mid, o.get("params") or {})
                    row["catalog"], row["note"] = val, how
                    dec = o.get("price_rub")
                    if val is not None and (dec is None or not near(float(dec), val, 0.02)):
                        rep.err(w, f"Gen-API цена {dec} ≠ {val} ({how})")
                        row["status"] = "цена"
            rep.rows.append(row)
        for n in r.get("not") or []:
            if not n.get("why"):
                rep.err(where, f"в not у {n.get('model')} нет why")
        conds = r.get("conditions")
        if conds is not None and not (isinstance(conds, list) and conds and all(isinstance(c, str) and c.strip() for c in conds)):
            rep.err(where, "conditions — список непустых строк")
        for mid, spec in (r.get("resolution_by") or {}).items():
            w = f"{code}.resolution_by[{mid}]"
            m, spec = snap.by_id.get(mid), spec or {}
            if m is None:
                rep.err(w, f"модели нет в снимке polza {snap.dir.name}")
                continue
            params = m.get("parameters") or (m.get("top_provider") or {}).get("parameters") or {}
            par, ops = spec.get("param"), spec.get("operations") or {}
            if par is None and not ops:
                rep.err(w, "нужен param или operations")
            if par is not None and par not in params:
                rep.err(w, f"параметра {par} нет в каталоге модели")
            elif par is not None:
                known = [str(v) for v in params[par].get("values") or []]
                extra = [str(v) for v in (spec.get("values") or {}) if str(v) not in known]
                if extra:
                    rep.err(w, f"значений {extra} нет у параметра {par} в каталоге ({known})")
                if par != "resolution" and not spec.get("values"):
                    rep.err(w, f"параметр {par} — не resolution: нужны values (значение → разрешение)")
            have = [o.get("id") for o in m.get("operations") or []]
            for op in ops:
                if op not in have:
                    rep.err(w, f"операции {op} нет у модели в каталоге (есть: {have})")
    return pinned


def selftest() -> int:
    """Проверки матрицы на вымышленных данных: матрица, каталог polza, диалекты и рубрики собираются в памяти и во
    временной папке; сети, ключей и снимков машины нет."""
    import copy
    import tempfile

    catalog = {"data": [
        {"id": "demo/image", "type": "image", "name": "Demo Image", "parameters": {"prompt": {"max_length": 500}},
         "top_provider": {"name": "demo", "pricing": {"per_request": "2.00"}}},
        {"id": "demo/video-mode", "type": "video", "name": "Demo Video", "top_provider": {"name": "demo", "pricing": {
            "per_request": "30.00"}}, "parameters": {"prompt": {"max_length": 500}, "mode": {
                "default": "std", "values": ["std", "pro"]}},
         "operations": [{"id": "upscale_1080p", "async": False, "pricing": {"per_request": "10.00"}}]},
    ]}
    option = {"role": "primary", "channel": "local", "tool": "demo", "price_rub": 0, "final": True}
    route = {"name": "demo", "options": [option], "dialect": {"family": None}, "check": {"audit_mode": "image",
             "rubric": "demo"}, "delivery": "image", "legal": {"flags": [], "policy_rows": []}, "label": "[проверено]",
             "checked": "2030-01-31", "decides": "demo"}
    base = {"version": 2, "checked_at": "2030-01-31", "catalog_snapshots": {"polza": "2030-01-31"},
            "enums": {"channel": {"polza": "", "routerai": "", "local": ""}, "legal_flags": {},
                      "labels": ["[проверено]"], "audit_modes": ["image"]},
            "defaults": {"delivery": {"image": "demo"}},
            "routes": {code: copy.deepcopy(route) for code in TAXONOMY}}
    dialects = {"families": {}, "channels": {"routerai": {"models": {"demo/known": {}}}}}
    polza = {"role": "alt", "channel": "polza", "provider": "demo", "model": "demo/image", "params": {},
             "price_rub": 2.0, "final": True}
    code = TAXONOMY[0]
    checks = []

    def ok(name, cond, got=""):
        checks.append(bool(cond))
        print(("OK  " if cond else "FAIL"), name + (f" — {got}" if got != "" and not cond else ""))

    with tempfile.TemporaryDirectory(prefix="routing-check-selftest-") as t:
        snap_dir = Path(t) / "2030-01-31"
        snap_dir.mkdir()
        (snap_dir / "api-v1-models.json").write_text(json.dumps(catalog), encoding="utf-8")
        snap = pc.Snapshot(str(snap_dir))

        def run(change) -> Report:
            data = copy.deepcopy(base)
            change(data)
            rep = Report()
            check_matrix(rep, data, snap, None, None, dialects, {"demo"})
            return rep

        def has(found: list, *parts) -> bool:
            return any(all(p in line for p in parts) for line in found)

        rep = run(lambda d: None)
        ok("матрица без расхождений: 0 ошибок, 0 предупреждений", not rep.errors and not rep.warnings,
           (rep.errors[:3], rep.warnings[:3]))
        rep = run(lambda d: d["routes"][code]["options"].append(dict(polza)))
        ok("вариант polza: цена и параметры сходятся с каталогом", not rep.errors and not rep.warnings, rep.errors)
        rep = run(lambda d: d["routes"][code]["options"].append(dict(polza, price_rub=3.0)))
        ok("вариант polza: цена не из каталога — ошибка", has(rep.errors, code, "цена 3.0"), rep.errors)

        def unavailable(final):
            def change(d):
                d["defaults"]["unavailable"] = [{"model": "demo/image", "error": "внутренняя ошибка × 2"}]
                d["routes"][code]["options"].append(dict(polza, final=final))
            return change

        rep = run(unavailable(True))
        ok("выбывшая модель (defaults.unavailable) вариантом с final: true — ошибка",
           has(rep.errors, "demo/image", "выбыла", "defaults.unavailable"), rep.errors)
        ok("выбывшая модель вариантом с final: false — без ошибки", not run(unavailable(False)).errors)

        def dated(d):
            d["defaults"]["unavailable_2030_01_31"] = [{"model": "demo/image"}]

        ok("запись выбывшей модели без error — ошибка", has(run(dated).errors, "unavailable_2030_01_31", "model и error"))
        rep = run(lambda d: d["catalog_snapshots"].update(polza="cache/polza/2030-01-31"))
        ok("catalog_snapshots с путём — предупреждение с именем папки",
           has(rep.warnings, "catalog_snapshots.polza", "2030-01-31") and not rep.errors, rep.warnings)

        def channel_model(mid):
            return lambda d: d["routes"][code]["options"].append(
                {"role": "alt", "channel": "routerai", "model": mid, "params": {}, "price_rub": 1.0, "final": False})

        rep = run(channel_model("demo/unknown"))
        ok("покрытие компилятора: модели канала нет в channels диалектов — предупреждение",
           has(rep.warnings, "demo/unknown", "channels.routerai.models") and not rep.errors, rep.warnings)
        ok("покрытие компилятора: модель канала из channels диалектов — без этого предупреждения",
           not has(run(channel_model("demo/known")).warnings, "channels.routerai.models"))

        def field(name, value):
            return lambda d: d["routes"][code].update({name: value})

        ok("conditions: список строк — без ошибки", not run(field("conditions", ["кадр без знака"])).errors)
        ok("conditions: пустой список и пустая строка — ошибка",
           has(run(field("conditions", [])).errors, code, "conditions")
           and has(run(field("conditions", [" "])).errors, code, "conditions"))
        good = {"demo/video-mode": {"param": "mode", "values": {"std": "720p", "pro": "1080p"}}}
        ok("resolution_by: параметр и значения из каталога, операция из каталога — без ошибки",
           not run(field("resolution_by", good)).errors
           and not run(field("resolution_by", {"demo/video-mode": {"operations": {"upscale_1080p": "1080p"}}})).errors,
           run(field("resolution_by", good)).errors)
        for label, spec, part in (
                ("значение не из каталога", {"param": "mode", "values": {"4K": "2160p"}}, "значений ['4K'] нет"),
                ("параметра нет в каталоге", {"param": "resolution"}, "параметра resolution нет"),
                ("параметр не resolution без values", {"param": "mode"}, "нужны values"),
                ("операции нет в каталоге", {"operations": {"upscale_4k": "2160p"}}, "операции upscale_4k нет"),
                ("ни param, ни operations", {}, "нужен param или operations")):
            rep = run(field("resolution_by", {"demo/video-mode": spec}))
            ok(f"resolution_by: {label} — ошибка", has(rep.errors, "resolution_by[demo/video-mode]", part), rep.errors)
        ok("resolution_by: модели нет в снимке — ошибка",
           has(run(field("resolution_by", {"demo/none": {"param": "mode"}})).errors, "resolution_by[demo/none]", "нет в снимке"))
    print("ИТОГО:", "все проверки пройдены" if all(checks) else f"{checks.count(False)} ошибок")
    return 0 if all(checks) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("routing", nargs="?", default=str(ROOT / "13-routing-matrix/routing.yaml"),
                    help="матрица маршрутов (по умолчанию — routing.yaml базы)")
    ap.add_argument("--polza", metavar="SNAP", help="снимок каталога polza: имя папки или путь (по умолчанию — последний)")
    ap.add_argument("--routerai", metavar="SNAP", help="снимок каталога RouterAI (по умолчанию — последний)")
    ap.add_argument("--genapi", metavar="SNAP", help="снимок каталога Gen-API (по умолчанию — последний)")
    ap.add_argument("--json", metavar="OUT.json", help="отчёт JSON: ok, errors, warnings, rows, snapshots")
    ap.add_argument("--md", metavar="OUT.md", help="отчёт Markdown в файл (без ключа — в stdout)")
    ap.add_argument("--selftest", action="store_true",
                    help="самопроверка проверок матрицы на вымышленных данных: без сети и без снимков каталогов")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    rep = Report()
    path = Path(a.routing)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    try:
        snap = pc.Snapshot(a.polza)
    except SystemExit as e:
        print(f"{e} — снимок каталога polza: scripts/install.sh --catalogs или polza_catalog.py snapshot (бесплатный GET)",
              file=sys.stderr)
        return 2
    ra = ga = None
    if mp is not None:
        try:
            ra = mp.RouterCatalog(a.routerai)
        except SystemExit as e:
            rep.warn("routerai", f"каталог не загружен: {e}")
        try:
            ga = mp.GenapiCatalog(a.genapi)
        except SystemExit as e:
            rep.warn("genapi", f"каталог не загружен: {e}")
    used = {"polza": snap.dir.name, "routerai": ra.path.parent.name if ra else None,
            "genapi": ga.path.parent.name if ga else None}
    dialects = yaml.safe_load((ROOT / "05-prompting/dialects.yaml").read_text(encoding="utf-8"))
    rubrics = {p.name.replace(".rubric.json", "") for p in (ROOT / "11-evaluation-qa/rubrics").glob("*.rubric.json")}
    pinned = check_matrix(rep, data, snap, ra, ga, dialects, rubrics)
    routes = data.get("routes", {})

    ok = not rep.errors
    lines = [f"# routing_check.py — {path.name} v{data.get('version')} · снимок polza {used['polza']} · "
             f"RouterAI {used['routerai'] or '—'} · Gen-API {used['genapi'] or '—'}", ""]
    if pinned:
        lines += ["Снимки, с которыми матрицу сверяли при обновлении (`catalog_snapshots`): "
                  + ", ".join(f"{k} {v}" for k, v in pinned.items()) + ".", ""]
    lines += [f"Маршрутов: {len(routes)} (кодов таксономии {sum(1 for c in routes if c in TAXONOMY)}/{len(TAXONOMY)}); "
              f"вариантов: {len(rep.rows)}; ошибок: {len(rep.errors)}; предупреждений: {len(rep.warnings)}", "",
              "| Код | Роль | Канал | Модель / инструмент | Провайдер | ₽ заявлено | ₽ каталог | Статус |", "|---|---|---|---|---|---|---|---|"]
    for row in rep.rows:
        cat = "" if row["catalog"] is None else f"{row['catalog']:.4f}".rstrip("0").rstrip(".")
        dec = "" if row["declared"] is None else f"{row['declared']}"
        lines.append(f"| {row['code']} | {row['role']} | {row['channel']} | `{row['model']}` | {row['provider'] or ''} | {dec} | {cat} | {row['status']} |")
    if rep.errors:
        lines += ["", "## Ошибки", ""] + [f"- {e}" for e in rep.errors]
    if rep.warnings:
        lines += ["", "## Предупреждения", ""] + [f"- {w}" for w in rep.warnings]
    text = "\n".join(lines) + "\n"
    if a.md:
        Path(a.md).write_text(text, encoding="utf-8")
    if a.json:
        Path(a.json).write_text(json.dumps({"ok": ok, "errors": rep.errors, "warnings": rep.warnings, "rows": rep.rows,
                                            "snapshots": {"used": used, "matrix": pinned}},
                                           ensure_ascii=False, indent=1), encoding="utf-8")
    print(text if (a.md is None) else f"Маршрутов {len(routes)}, вариантов {len(rep.rows)}, ошибок {len(rep.errors)}, "
                                      f"предупреждений {len(rep.warnings)} → {a.md}")
    if rep.errors and a.md:
        print("\n".join(rep.errors))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
