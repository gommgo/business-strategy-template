#!/usr/bin/env python3
"""make_skeleton.py — иерархия сообщений (B1) → скелет copy deck v1 (J) для шага S5 цепочки.

text-research · волна 3 · агент I (I3, фаза 2) · 2026-09-24 · опыт 99-raw/experiments/I/04-chain-manual/
Промт P3 §4: «make_skeleton.py переносит section_role, question, message, carries, proof_ids → fact_ids / missing_ids в
секции copy deck J». Поля секции схемы J: section_id, section_role, question, message, carries; доказательства и
возражения секции — в расширениях x-fact-ids, x-missing-ids, x-objection-ids, x-next-step (схема разрешает x-…).
Слоты — по роли секции (раскладка ниже, [мнение] I3: E задаёт правила слотов, но не состав секции — это site page-plan);
число вариантов — x-variants-n (headline и subheadline — 3, cta-label — 2, остальное — 1: решение I2, W1-4).

Запуск (из корня text-research, системный python3 с PyYAML):
    python3 99-raw/experiments/I/04-chain-manual/make_skeleton.py HIERARCHY.yaml --facts FACTS.yaml --voice VOICE.yaml \
        --meaning MEANING.yaml --page-id ID --product-name ИМЯ -o SKELETON.yaml
"""
import argparse
import datetime
import os
import re

import yaml

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


def main():
    ap = argparse.ArgumentParser(description="иерархия → скелет copy deck")
    ap.add_argument("hierarchy")
    ap.add_argument("--facts", required=True)
    ap.add_argument("--voice", required=True)
    ap.add_argument("--meaning", required=True)
    ap.add_argument("--page-id", required=True)
    ap.add_argument("--product-name", default="")
    ap.add_argument("-o", required=True)
    a = ap.parse_args()
    h = yaml.safe_load(open(a.hierarchy, encoding="utf-8"))
    out_dir = os.path.dirname(os.path.abspath(a.o))
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
    deck = {"copy_deck": {
        "version": 1, "date": datetime.date.today().isoformat(), "site": h.get("site", "site"), "product_name": a.product_name,
        "lang": h.get("lang", "ru"), "voice_ref": r(a.voice), "facts_ref": r(a.facts), "meaning_ref": r(a.meaning),
        "jurisdiction": "ru", "legal_category": ["general"], "authors": ["агент I3 (ai-self, опыт I/04)"],
        "notes": f"Скелет из {os.path.basename(a.hierarchy)} (make_skeleton.py, шаг S5); тексты пишет P4/P5.",
        "pages": [{"page_id": a.page_id, "page_type": page.get("page_type", "landing-lead-services"), "status": "draft",
                   "hierarchy_ref": r(a.hierarchy), "awareness": page.get("awareness"),
                   "meta": {"title": "", "description": "", "og_title": "", "og_description": ""},
                   "sections": sections}]}}
    with open(a.o, "w", encoding="utf-8") as f:
        f.write("# Скелет copy deck (S5, make_skeleton.py): секции и слоты из иерархии, тексты пусты\n")
        f.write(yaml.safe_dump(deck, allow_unicode=True, sort_keys=False, width=120))
    n = sum(len(s["slots"]) for s in sections)
    print(f"make_skeleton: секций {len(sections)}, слотов {n}, вариантов к написанию "
          f"{sum(sl.get('x-variants-n', 1) for s in sections for sl in s['slots'])} → {a.o}")


if __name__ == "__main__":
    main()
