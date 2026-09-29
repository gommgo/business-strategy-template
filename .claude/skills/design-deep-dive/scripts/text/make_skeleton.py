#!/usr/bin/env python3
"""make_skeleton.py — каркас copy deck v1 из иерархии сообщений, когда плана страницы нет (шаг S5 цепочки промтов).

Страница с планом (site/<surface>/plans/<page-id>.yaml) получает каркас из плана: `copydeck.py skeleton PLAN -o DECK`
(секции, блоки и слоты плана). Без плана — эта утилита. Промт P3 §4: переносит section_role, question, message, carries,
proof_ids → fact_ids / missing_ids секций иерархии в секции copy deck; доказательства и возражения секции — в
расширениях x-fact-ids, x-missing-ids, x-objection-ids, x-next-step (схема разрешает x-…). Слоты — по роли секции
(раскладка ниже: правила слотов задаёт copy-slots.yaml, состав секции без плана — эта раскладка); число вариантов —
x-variants-n (headline и subheadline — 3, cta-label — 2, остальное — 1). Варианты каркаса — draft с пустым текстом.

Запуск (Python с PyYAML; самопроверке нужен ещё jsonschema — без него сверка со схемой пропускается):
    python3 scripts/text/make_skeleton.py HIERARCHY.yaml --facts FACTS.yaml --voice VOICE.yaml --meaning MEANING.yaml \
        --page-id ID --product-name ИМЯ -o SKELETON.yaml [--date ГГГГ-ММ-ДД] [--force]
    python3 scripts/text/make_skeleton.py --selftest
Есть план этой страницы рядом с папкой иерархии (../plans/<page-id>.yaml) — отказ с кодом 2 и подсказкой
`copydeck.py skeleton`; --force строит каркас из иерархии всё равно.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import docpaths  # noqa: E402
import kbpaths  # noqa: E402

VARIANTS_N = {"headline": 3, "subheadline": 3, "cta-label": 2}


def ids(proof_ids, kind):
    return [p.split(":", 1)[1] for p in proof_ids or [] if p.startswith(kind + ":")]


def slot(slot_id, slot_type, group=None):
    s = {"slot_id": slot_id, "slot_type": slot_type, "variants": [{"id": "a", "text": "", "status": "draft"}],
         "chosen": "a", "fact_ids": [], "missing_ids": [], "claim_flags": []}
    if group:
        s["group"] = group
    if VARIANTS_N.get(slot_type, 1) > 1:
        s["x-variants-n"] = VARIANTS_N[slot_type]
    return s


def layout(sec, pillars, h):
    role = sec["section_role"]
    facts = ids(sec.get("proof_ids"), "fact")
    if role == "hero":
        out = [slot("h1", "headline"), slot("lead", "subheadline"), slot("cta", "cta-label"), slot("cta-note", "cta-note")]
        if any(f.startswith(("rating", "review")) for f in ids((h.get("first_screen") or {}).get("proof_ids"), "fact")):
            out.insert(2, slot("proof", "hero-proof"))
        return out
    if role == "problem":
        return [slot("h2", "section-title"), slot("body", "body")]
    if role == "solution":
        out = [slot("h2", "section-title"), slot("lead", "section-lead")]
        for i, c in enumerate([c for c in sec.get("carries") or [] if c in pillars], 1):
            out += [slot(f"card-{i}-title", "card-title", f"card-{i}"), slot(f"card-{i}-body", "card-body", f"card-{i}")]
        return out
    if role == "how-it-works":
        steps = [x.strip(" .") for x in re.split(r"→", sec.get("message", "")) if x.strip(" .")]
        out = [slot("h2", "section-title")]
        for i, _ in enumerate(steps or [1, 2, 3], 1):
            out += [slot(f"step-{i}-title", "step-title", f"step-{i}"), slot(f"step-{i}-body", "step-body", f"step-{i}")]
        return out
    if role == "case-studies":
        return [slot("h3", "case-title"), slot("summary", "case-summary"), slot("result", "case-result")]
    if role == "testimonials":
        out = [slot("h2", "section-title")]
        for i, f in enumerate([f for f in facts if f.startswith("review")] or ["review"], 1):
            out += [slot(f"quote-{i}", "testimonial-quote", f"review-{i}"), slot(f"author-{i}", "testimonial-attribution", f"review-{i}")]
        return out
    if role == "proof-stats":
        out = [slot("h2", "section-title")]
        for i, f in enumerate(facts, 1):
            out += [slot(f"stat-{i}-value", "stat-value", f"stat-{i}"), slot(f"stat-{i}-label", "stat-label", f"stat-{i}")]
        if any(f.startswith("rating") for f in facts):
            out.append(slot("source", "stat-source"))
        return out
    if role == "pricing":
        return [slot("h2", "section-title"), slot("price", "pricing-price"), slot("price-note", "pricing-price-note")]
    if role == "guarantee":
        return [slot("h2", "section-title"), slot("text", "guarantee-text")]
    if role == "comparison":
        return [slot("h2", "section-title")] + [slot(f"row-{i}", "comparison-row", f"row-{i}") for i in range(1, 4)]
    if role == "faq":
        out = [slot("h2", "section-title")]
        for i, _ in enumerate(sec.get("objection_ids") or [1, 2, 3], 1):
            out += [slot(f"q{i}", "faq-q", f"q{i}"), slot(f"a{i}", "faq-a", f"q{i}")]
        return out
    if role in ("final-cta", "cta-band"):
        return [slot("h2", "section-title"), slot("cta", "cta-label"), slot("cta-note", "cta-note")]
    if role == "lead-form":
        return [slot("title", "form-title"), slot("lead", "form-lead"), slot("cta", "cta-label"), slot("next", "form-next-steps")]
    return [slot("h2", "section-title"), slot("body", "body")]


def plan_for(hierarchy, page_id):
    """План страницы рядом с папкой иерархии (раскладка слоя страницы: hierarchy/ и plans/ — соседи) или None."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(hierarchy)))
    p = os.path.join(base, docpaths.SITE_FILES["plans"], f"{page_id}.yaml")
    return p if os.path.isfile(p) else None


def build(h, hierarchy, facts, voice, meaning, page_id, product_name, out, date=None):
    """Каркас copy deck (словарь) из иерархии h; пути ссылок — от папки out."""
    out_dir = os.path.dirname(os.path.abspath(out))
    r = lambda p: os.path.relpath(os.path.abspath(p), out_dir)  # noqa: E731
    pillars = {p["id"] for p in h.get("pillars", [])}
    pproofs = {p["id"]: p.get("proof_ids") or [] for p in h.get("pillars", [])}
    pproofs["core"] = (h.get("core_message") or {}).get("proof_ids") or []
    sections = []
    for sec in sorted(h["sections"], key=lambda s: s["order"]):
        sid = sec.get("section_id") or sec["section_role"]
        # доказательства секции = её proof_ids + proof_ids опор и главного сообщения, которые она несёт (carries)
        allp = list(dict.fromkeys((sec.get("proof_ids") or []) + [x for c in sec.get("carries") or [] for x in pproofs.get(c, [])]))
        s = {"section_id": sid, "section_role": sec["section_role"], "question": sec.get("question", ""),
             "message": sec.get("message", ""), "carries": sec.get("carries") or [],
             "x-fact-ids": ids(allp, "fact"), "x-missing-ids": ids(allp, "missing"),
             "x-objection-ids": sec.get("objection_ids") or [], "slots": layout(sec, pillars, h)}
        if sec.get("next_step"):
            s["x-next-step"] = sec["next_step"]
        if not s["carries"]:
            del s["carries"]
        sections.append(s)
    page = h.get("page") or {}
    return {"copy_deck": {
        "version": 1, "date": date or datetime.date.today().isoformat(), "site": h.get("site", "site"), "product_name": product_name,
        "lang": h.get("lang", "ru"), "voice_ref": r(voice), "facts_ref": r(facts), "meaning_ref": r(meaning),
        "jurisdiction": "ru", "legal_category": ["general"], "authors": ["каркас: make_skeleton.py"],
        "notes": f"Каркас из {os.path.basename(hierarchy)} без плана страницы (make_skeleton.py, шаг S5); тексты пишут P4/P5.",
        "pages": [{"page_id": page_id, "page_type": page.get("page_type", "landing-lead-services"), "status": "draft",
                   "hierarchy_ref": r(hierarchy), "awareness": page.get("awareness"),
                   "meta": {"title": "", "description": "", "og_title": "", "og_description": ""},
                   "sections": sections}]}}


def write(deck, out):
    with open(out, "w", encoding="utf-8") as f:
        f.write("# Каркас copy deck (S5, make_skeleton.py): секции и слоты из иерархии, тексты пусты\n")
        f.write(yaml.safe_dump(deck, allow_unicode=True, sort_keys=False, width=120))


def main(argv=None):
    ap = argparse.ArgumentParser(description="иерархия → каркас copy deck (страница без плана)")
    ap.add_argument("hierarchy", nargs="?")
    ap.add_argument("--facts")
    ap.add_argument("--voice")
    ap.add_argument("--meaning")
    ap.add_argument("--page-id")
    ap.add_argument("--product-name", default="")
    ap.add_argument("-o")
    ap.add_argument("--date", help="дата каркаса (по умолчанию сегодня)")
    ap.add_argument("--force", action="store_true", help="каркас из иерархии, даже если у страницы есть план")
    ap.add_argument("--selftest", action="store_true", help="самопроверка на примерах базы (вывод — $DDD_HOME/out/text)")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    miss = [n for n in ("hierarchy", "facts", "voice", "meaning", "page_id", "o") if not getattr(a, n)]
    if miss:
        ap.error("нужны: " + ", ".join("--" + m.replace("_", "-") if m != "hierarchy" else "HIERARCHY.yaml" for m in miss))
    plan = plan_for(a.hierarchy, a.page_id)
    if plan and not a.force:
        print(f"make_skeleton: у страницы {a.page_id} есть план {plan} — каркас из плана: "
              f"copydeck.py skeleton {plan} -o {a.o} (из иерархии — --force)", file=sys.stderr)
        return 2
    h = yaml.safe_load(open(a.hierarchy, encoding="utf-8"))
    deck = build(h, a.hierarchy, a.facts, a.voice, a.meaning, a.page_id, a.product_name, a.o, a.date)
    write(deck, a.o)
    sections = deck["copy_deck"]["pages"][0]["sections"]
    n = sum(len(s["slots"]) for s in sections)
    print(f"make_skeleton: секций {len(sections)}, слотов {n}, вариантов к написанию "
          f"{sum(sl.get('x-variants-n', 1) for s in sections for sl in s['slots'])} → {a.o}")
    return 0


def selftest():
    """Каркас из иерархии примера базы: схема copy deck, секции и слоты, доказательства; отказ при плане страницы и --force."""
    kb = kbpaths.kb("text")
    ex = os.path.join(str(kb), "02-strategy-messaging", "examples")
    hier = os.path.join(ex, "hierarchy-otves-product-aware.yaml")
    meaning = os.path.join(ex, "meaning-otves.yaml")
    facts = os.path.join(ex, "facts-service-renovation.yaml")
    voice = os.path.join(str(kb), "05-voice-editorial", "examples", "voice-otves-warm.yaml")
    out_dir = str(kbpaths.out("text", "make_skeleton-selftest"))
    res = []

    def ok(name, cond, detail=""):
        res.append(bool(cond))
        print(("OK   " if cond else "FAIL ") + name + ("" if cond else f" → {detail}"))

    h = yaml.safe_load(open(hier, encoding="utf-8"))
    out = os.path.join(out_dir, "copy", "home.yaml")
    deck = build(h, hier, facts, voice, meaning, "home", "Отвес", out, "2026-01-01")
    page = deck["copy_deck"]["pages"][0]
    secs = page["sections"]
    ok("секций столько же, сколько в иерархии", len(secs) == len(h["sections"]), (len(secs), len(h["sections"])))
    ok("первая секция hero: h1, lead, cta", secs[0]["section_role"] == "hero"
       and {"h1", "lead", "cta"} <= {s["slot_id"] for s in secs[0]["slots"]}, [s["slot_id"] for s in secs[0]["slots"]])
    ok("варианты каркаса — draft с пустым текстом", all(v["status"] == "draft" and v["text"] == ""
                                                     for s in secs for sl in s["slots"] for v in sl["variants"]))
    hf = {p.split(":", 1)[1] for s in h["sections"] for p in s.get("proof_ids") or [] if p.startswith("fact:")}
    df = {f for s in secs for f in s["x-fact-ids"]}
    ok("доказательства секций перенесены (x-fact-ids)", hf <= df, sorted(hf - df))
    ok("ссылки — от папки copy deck", deck["copy_deck"]["facts_ref"].endswith("facts-service-renovation.yaml")
       and not os.path.isabs(deck["copy_deck"]["facts_ref"]), deck["copy_deck"]["facts_ref"])
    try:
        import jsonschema
        schema = json.load(open(os.path.join(str(kb), "10-templates-recipes", "copy-deck.schema.json"), encoding="utf-8"))
        errs = list(jsonschema.Draft202012Validator(schema).iter_errors(deck))
        ok("каркас проходит copy-deck.schema.json", not errs, [f"{list(e.path)}: {e.message[:120]}" for e in errs[:3]])
    except ImportError:
        print("—    сверка со схемой пропущена: нет jsonschema")
    # отказ при плане страницы и обход --force (раскладка слоя страницы во временной папке вывода)
    site = os.path.join(out_dir, "site")
    shutil.rmtree(site, ignore_errors=True)
    os.makedirs(os.path.join(site, docpaths.SITE_FILES["hierarchy"]))
    os.makedirs(os.path.join(site, docpaths.SITE_FILES["plans"]))
    h2 = os.path.join(site, docpaths.SITE_FILES["hierarchy"], "home.yaml")
    shutil.copy(hier, h2)
    deck_out = os.path.join(site, "home.copy.yaml")
    args = [h2, "--facts", facts, "--voice", voice, "--meaning", meaning, "--page-id", "home", "-o", deck_out, "--date", "2026-01-01"]
    ok("без плана — каркас пишется", main(args) == 0 and os.path.isfile(deck_out))
    os.remove(deck_out)
    with open(os.path.join(site, docpaths.SITE_FILES["plans"], "home.yaml"), "w", encoding="utf-8") as f:
        f.write("page_plan: {page: {id: home}}\n")
    ok("есть план страницы — отказ с кодом 2", main(args) == 2 and not os.path.exists(deck_out))
    ok("--force — каркас из иерархии", main(args + ["--force"]) == 0 and os.path.isfile(deck_out))
    print(f"selftest: {sum(res)} из {len(res)}")
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
