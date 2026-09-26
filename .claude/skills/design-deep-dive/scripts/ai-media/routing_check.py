#!/usr/bin/env python3
"""routing_check.py 1.1 — проверка 13-routing-matrix/routing.yaml (агент N, волна 3, 24.09.2026; v1.1 — агент U, 25.09.2026).

Без сети и без ключей. Проверяет:
  1. yaml.safe_load, version, checked_at, все 31 код таксономии (+ предложения с `proposal: true`);
  2. у каждого варианта (`options`) — канал из `enums.channel`, роль, `final`;
  3. polza: модель есть в снимке каталога; провайдер — из списка провайдеров модели (или top_provider);
     параметры проходят `polza_catalog.validate` (0 ошибок); цена = `polza_catalog.estimate` (± 1 % или ± 0,02 ₽);
  4. routerai / genapi: модель (сеть) есть в своём снимке каталога; цена — по прайсу канала (± 2 %; у токенных GPT Image —
     выход medium по формуле mp_client не выше заявленной цены, заявленная ≤ выход × 2,5 — вход картинки);
  5. polza-chat: чат-модель есть в снимке polza; polza-images: модель есть, цена ≥ ступени 1K;
  6. external — есть `access`; local / code / blender — есть `tool`;
  7. диалект — семейство есть в 05-prompting/dialects.yaml и формат совпадает;
  8. check.audit_mode — из enums; check.rubric — файл 11-evaluation-qa/rubrics/<имя>.rubric.json;
  9. legal.flags и флаги вариантов — из enums; модель с флагом research (qwen/image-2.1) — только `final: false`;
     `minimax/*` — с флагом `visible-vendor-mark` (ToS: метка в контенте); строки политики 12–14 (люди) — флаг
     маршрута `people-consent` (X2, 24.09.2026; CONTRADICTIONS X35, X42);
 10. устаревшие модели (defaults.deprecated) — не среди вариантов (в `not` можно);
 11. phase5_test — есть задание 99-raw/phase5/jobs/<ID>-* или строка плана 99-raw/phase5/*-plan.md, T0–T9
     (коды с цифрой в начале и трёхбуквенные — `3D-21`, `VAR-01` — с v1.1);
 12. label — из enums.labels (каждая метка в квадратных скобках — известная).
 v1.1 (агент U, сессия 5, 25.09.2026) — routing.yaml v2:
 13. version — 1 или 2;
 14. defaults.unavailable_<дата> (выбывшие модели: model, error) — такая модель не может быть вариантом с final: true
     (в `not` и с final: false — можно); у записи обязательны model и error;
 15. defaults.not_routes — у каждой записи есть what и why.

Запуск:  python3 99-raw/tools/routing_check.py [13-routing-matrix/routing.yaml] [--json OUT.json] [--md OUT.md]
Код выхода: 0 — ошибок нет (предупреждения допустимы), 1 — есть ошибки.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))  # перенос: scripts/lib
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


TEST_ID = r"[A-Z0-9][A-Z0-9]{0,2}\d?-\d{2}"   # E-08, D2-01, CM-09, MS-05, 3D-21, VAR-01 (v1.1: цифра в начале, 3 буквы)


def known_test_ids() -> set[str]:
    ids = set()
    jobs = kbpaths.out("ai-media", "phase5", "jobs")  # перенос: задания — выход stand_run, не kb
    for f in jobs.iterdir() if jobs.is_dir() else []:
        m = re.match(rf"^({TEST_ID})-", f.name)
        if m:
            ids.add(m.group(1))
    drafts = ROOT / "99-raw/experiments/N/02-phase5-plan/jobs"   # заготовки N сводного плана (до переноса в jobs/)
    for f in drafts.iterdir() if drafts.is_dir() else []:
        m = re.match(rf"^({TEST_ID})-", f.name)
        if m:
            ids.add(m.group(1))
    for plan in [*(ROOT / "99-raw/phase5").glob("*-plan.md"), ROOT / "99-raw/phase5/plan.md"]:
        if not plan.exists():
            continue
        txt = plan.read_text(encoding="utf-8")
        for m in re.finditer(rf"^\|\s*({TEST_ID})\s*\|", txt, re.M):
            ids.add(m.group(1))
    ids.update(f"T{i}" for i in range(10))
    return ids


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
                return val, "прайс Gen-API P/04"
    return None, "цена не найдена в прайсе"


def people_rows(rows) -> bool:
    """Есть ли среди policy_rows строки 12–14 таблицы L 12/04 §2 (люди-декор, реальные люди, клиенты и команда)."""
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("routing", nargs="?", default=str(ROOT / "13-routing-matrix/routing.yaml"))
    ap.add_argument("--json")
    ap.add_argument("--md")
    a = ap.parse_args(argv)

    rep = Report()
    path = Path(a.routing)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
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
    # v1.1: выбывшие модели (defaults.unavailable_<дата>) и «не маршруты» (defaults.not_routes)
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

    snaps = data.get("catalog_snapshots", {})
    snap = pc.Snapshot(Path(ROOT / snaps["polza"]).name if snaps.get("polza") else None)
    ra = ga = None
    if mp is not None:
        try:
            ra = mp.RouterCatalog(str(ROOT / snaps["routerai"])) if snaps.get("routerai") else mp.RouterCatalog()
        except SystemExit as e:
            rep.warn("routerai", f"каталог не загружен: {e}")
        try:
            ga = mp.GenapiCatalog(str(ROOT / snaps["genapi"])) if snaps.get("genapi") else mp.GenapiCatalog()
        except SystemExit as e:
            rep.warn("genapi", f"каталог не загружен: {e}")
    dialects = yaml.safe_load((ROOT / "05-prompting/dialects.yaml").read_text(encoding="utf-8"))
    families = dialects.get("families", {})
    rubrics = {p.name.replace(".rubric.json", "") for p in (ROOT / "11-evaluation-qa/rubrics").glob("*.rubric.json")}
    test_ids = known_test_ids()

    routes = data.get("routes", {})
    for code in TAXONOMY:
        if code not in routes:
            rep.err(code, "нет маршрута для кода таксономии")
    for code, r in routes.items():
        if code not in TAXONOMY and not r.get("proposal"):
            rep.err(code, "код вне таксономии без proposal: true")
        where = code
        for key in ("name", "options", "dialect", "check", "delivery", "legal", "label", "checked", "phase5_test", "decides"):
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
            rep.err(where, "строки политики 12–14 (люди) без флага people-consent (L 12/04 §2)")
        # тесты фазы 5
        for t in r.get("phase5_test") or []:
            if t not in test_ids:
                rep.err(where, f"тест {t} не найден в jobs/ и планах фазы 5")
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
                rep.err(w, "MiniMax без флага visible-vendor-mark (ToS: «prominent mark… within generated content», L 12/01 §2)")
            if mid == "qwen/image-2.1" or "research" in (o.get("legal") or []):
                if o.get("final") is not False:
                    rep.err(w, "модель с флагом research должна быть final: false (L 12/01 §5)")
                if "research" not in (o.get("legal") or []):
                    rep.err(w, "qwen/image-2.1 без флага legal research")
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

    ok = not rep.errors
    lines = [f"# routing_check.py — {path.name} v{data.get('version')} · снимок polza {snap.dir.name} · "
             f"RouterAI {ra.path.parent.name if ra else '—'} · Gen-API {ga.path.parent.name if ga else '—'}", "",
             f"Маршрутов: {len(routes)} (кодов таксономии {sum(1 for c in routes if c in TAXONOMY)}/{len(TAXONOMY)}); "
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
        Path(a.json).write_text(json.dumps({"ok": ok, "errors": rep.errors, "warnings": rep.warnings, "rows": rep.rows},
                                           ensure_ascii=False, indent=1), encoding="utf-8")
    print(text if (a.md is None) else f"Маршрутов {len(routes)}, вариантов {len(rep.rows)}, ошибок {len(rep.errors)}, "
                                      f"предупреждений {len(rep.warnings)} → {a.md}")
    if rep.errors and a.md:
        print("\n".join(rep.errors))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
