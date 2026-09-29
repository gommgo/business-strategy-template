#!/usr/bin/env python3
"""chain_inputs.py — проекции входов промтов P2–P7 и «код между шагами» цепочки генерации copy deck.

Цепочка: kb/text/09-ai-generation-evaluation/02-generation-pipeline.md; промты: 09-ai-generation-evaluation/prompts/p1…p7.
Зависимости: Python 3.10+ и PyYAML. Сеть и модели не нужны: скрипт собирает входы промтов и переносит выходы в copy
deck, текст пишет агент сессии (ai-self). Тексты агента входят в copy deck со статусом assumed — черновик
«допущением», который утверждает владелец продукта.

Команды (python3 scripts/text/chain_inputs.py <команда> …):
  digest-meaning  [--schema S] [--meaning M] [--call-inputs F…] [-o OUT]   проекция meaning.schema для P2 + замер длины
  meaning-claims  --meaning M [--hierarchy H …] -o OUT.yaml               смысл и иерархии → copy deck для claims_check (P2, P3 §4)
  hierarchy-input --meaning M --awareness L --traffic S[,S] [--promise T] [--page-type T] [-o OUT]   вход P3
  section-input   --deck D --page P --section S --hierarchy H --meaning M --voice V [--lang ru] [-o OUT]   вход P4
  edit-input      --deck D --check J.json --pass N [--voice V] [-o OUT]    вход P6 (проход 1 — error, 2–3 — warning)
  judge-input     --deck D --page P --criterion ID [--scope …] --hierarchy H --meaning M [--lang ru] [-o OUT]   вход P7
  judge-score     --answers A.json [A2.json …] [-o OUT]                    баллы по ответам судьи (формула рубрики)
  assemble        --skeleton S --parts F.yaml [F2.yaml …] --by WHO -o DECK выходы P4/P5 → copy deck (assumed, generated, promise)
  apply-edits     --deck D --edits E.yaml --pass N --by WHO -o OUT         выход P6 → новые варианты assumed, rejected, edit_log
  canvas-texts    --deck D [--page P] [--stage wireframe] [--out DIR]      тексты во вход холста: copydeck.py export
                                                                           (pages/<page-id>/copy.md и facts.md)
  --selftest                                                               проверки подсчёта баллов и переноса правок
Каркас copy deck: у страницы с планом — copydeck.py skeleton, без плана — make_skeleton.py. Факты: facts_ref copy deck
или meaning.proof_ref; правила слотов — 04-copy-by-block/copy-slots.yaml; голос — voice.yaml; рубрика —
09-ai-generation-evaluation/copy-rubric.yaml; вопросы GEO — 07-seo-geo-copy/geo-checklist.yaml; роли секций — словарь
site (kb/site/02-site-types/vocabulary.yaml).
"""
import argparse
import copy
import datetime
import json
import os
import re
import sys
from collections import Counter, defaultdict

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb("text"))
P = lambda *a: os.path.join(ROOT, *a)  # noqa: E731
MEANING_SCHEMA = P("02-strategy-messaging", "meaning.schema.yaml")
FACTS_SCHEMA = P("02-strategy-messaging", "facts.schema.yaml")
SLOTS = P("04-copy-by-block", "copy-slots.yaml")
RULES_H = P("08-russian-legal-typography", "claims-rules.yaml")
RUBRIC = P("09-ai-generation-evaluation", "copy-rubric.yaml")
GEO = P("07-seo-geo-copy", "geo-checklist.yaml")
VOCAB = str(kbpaths.kb("site", "02-site-types", "vocabulary.yaml"))   # словарь id системы: роли секций
TODAY = datetime.date.today().isoformat()
VARIANTS_N = {"headline": 3, "subheadline": 3, "cta-label": 2, "meta-title": 3}   # остальное — 1
SHORT_SLOTS = {"headline", "subheadline", "eyebrow", "cta-label", "cta-note", "cta-secondary-label", "section-title",
               "card-title", "step-title", "stat-value", "stat-label", "case-title", "pricing-price", "badge",
               "meta-title", "meta-description", "og-title", "og-description", "faq-q", "form-title",
               "testimonial-attribution", "hero-proof"}
GEO_PASS_IF_NO = {"COPY-GEO-10", "COPY-GEO-18", "COPY-GEO-26"}
# таблица уровней осведомлённости — проекция 02-strategy-messaging/02-awareness-hierarchy-objections.md §1.2, §1.4 (для P3)
AWARENESS_RULES = {
    "most-aware": {"hero_approach": "direct-offer", "first_screen": "предложение: цена, условия, срок; кнопка; строка снятия риска",
                   "avoid": "объяснять проблему и категорию", "depth": "short",
                   "proof_order": "условия сделки → что сделка настоящая (цена, возврат, доставка) → вопросы сделки"},
    "product-aware": {"hero_approach": "product-benefit", "first_screen": "имя + превосходство и доказательство (рейтинг, кейс, новое)",
                      "avoid": "историю проблемы", "depth": "short–medium",
                      "proof_order": "стороннее доказательство (рейтинг с датой, отзывы, кейс) → гарантия → предложение → цифры"},
    "solution-aware": {"hero_approach": "solution-vs-alternatives", "first_screen": "категория словами клиента + чем лучше привычных подходов",
                       "avoid": "«мы лучшие», общие выгоды категории", "depth": "medium",
                       "proof_order": "механизм отличия → сравнение с подходами → кейс и числа → гарантия → предложение"},
    "problem-aware": {"hero_approach": "problem-story", "first_screen": "узнаваемая ситуация, её цена, намёк на выход, призыв",
                      "avoid": "цену и характеристики как главное", "depth": "long",
                      "proof_order": "ситуация и её цена → механизм → кейс → отзыв → числа → предложение"},
    "unaware": {"hero_approach": "identity", "first_screen": "узнавание себя, история; продукт в конце",
                "avoid": "цену, название, прямое обещание", "depth": "long",
                "proof_order": "узнавание и история → проблема → далее как problem-aware"},
}
TONE_SITUATION = {"hero": "hero", "testimonials": "testimonials", "pricing": "pricing-terms", "guarantee": "guarantee",
                  "lead-form": "form-success", "final-cta": "hero"}


# ---------------------------------------------------------------- общее
def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump(obj, out=None):
    text = yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=120)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return text


def rel(target, start_dir):
    return os.path.relpath(os.path.abspath(target), os.path.abspath(start_dir))


def deck_root(d):
    return d["copy_deck"] if "copy_deck" in d else d


def find_page(cd, page_id):
    for p in cd["pages"]:
        if p["page_id"] == page_id:
            return p
    raise SystemExit(f"страница {page_id} не найдена")


def chosen_text(slot):
    ch = slot.get("chosen") or (slot["variants"][0]["id"] if slot.get("variants") else None)
    for v in slot.get("variants", []):
        if v["id"] == ch:
            return v.get("text", "")
    return ""


def facts_file_for_deck(deck_path, cd):
    ref = cd.get("facts_ref")
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(deck_path)), ref)) if ref else None


def facts_file_for_meaning(meaning_path, m):
    ref = m.get("proof_ref")
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(meaning_path)), ref)) if ref else None


def split_ids(proof_ids):
    f, m = [], []
    for p in proof_ids or []:
        k, _, v = str(p).partition(":")
        (f if k == "fact" else m if k == "missing" else f).append(v or k)
    return f, m


def est_tokens(text):
    """Оценка числа токенов по знакам [оценка, не токенизатор]: кириллица 2,5–4 знака на токен, прочее 3,5–4,5."""
    cyr = sum(1 for c in text if "а" <= c.lower() <= "я" or c in "ёЁ")
    other = len(text) - cyr
    return round(cyr / 4 + other / 4.5), round(cyr / 2.5 + other / 3.5)


# ---------------------------------------------------------------- digest-meaning (P2)
NAMED = {"basis": "basis", "proof-ids": "proof_ids", "voc-ids": "voc_ids", "id": "id", "date": "date", "lang": "lang",
         "question": "question", "section-role": "section_role", "traffic-source": "traffic_source"}


def _resolve(node, root):
    seen = 0
    while isinstance(node, dict) and "$ref" in node and seen < 10:
        name = node["$ref"].split("/")[-1]
        if name in NAMED:
            return {"x-named": NAMED[name]}
        base = dict(root["$defs"][name])
        base.update({k: v for k, v in node.items() if k != "$ref"})
        node, seen = base, seen + 1
    return node


def _sig(node, root, depth):
    node = _resolve(node, root)
    if not isinstance(node, dict):
        return ""
    if "x-named" in node:
        return f":{node['x-named']}"
    if "enum" in node:
        return "(" + "|".join(map(str, node["enum"])) + ")"
    if "const" in node:
        return f"={node['const']}"
    for alt in ("oneOf", "anyOf"):
        if alt in node and "properties" not in node:
            return " one of " + " / ".join(_sig(x, root, depth) or "…" for x in node[alt])
    t = node.get("type")
    if t == "array" or "items" in node:
        return "[" + (_sig(node.get("items", {}), root, depth) or "") + "]"
    if t == "object" or "properties" in node:
        if depth <= 0:
            return "{…}"
        req = set(node.get("required", []))
        parts = [k + ("*" if k in req else "") + _sig(v, root, depth - 1)
                 for k, v in node.get("properties", {}).items() if not k.startswith("x-")]
        return "{" + ", ".join(parts) + "}"
    if t in ("integer", "number"):
        mn, mx = node.get("minimum"), node.get("maximum")
        return f":int{'' if mn is None else f' {mn}–{mx}'}" if t == "integer" else ":num"
    if node.get("maxLength"):
        return f":str≤{node['maxLength']}"
    return ""


def digest_meaning(schema):
    req = set(schema.get("required", []))
    lines = ["# meaning.schema.yaml — проекция для P2 (обязательные поля — *, варианты — (a|b); полная схема — в коде проверки)"]
    for k, v in schema.get("properties", {}).items():
        lines.append(f"{k}{'*' if k in req else ''}{_sig(v, schema, 3)}")
    lines.append("basis: {kind*(brief|customer|voc|fact|public-page|research|inferred|assumption), ref, date, question_id}; "
                 "ref обязателен у voc, fact, public-page, research, inferred; assumption — только с question_id вопроса из open_questions")
    lines.append("question: {id*, q*, why*, options[] (для фактов пусто), default*, affects*[], priority 1–3}")
    lines.append("proof_ids: только \"fact:<id>\" из facts.yaml или \"missing:<id>\"; voc_ids: id из voc.yaml")
    lines.append("id — латиница kebab-case; даты — строкой \"ГГГГ-ММ-ДД\"; расширения — только ключи x-…")
    return "\n".join(lines) + "\n"


def cmd_digest_meaning(a):
    schema = load(a.schema)
    raw = open(a.schema, encoding="utf-8").read()
    dg = digest_meaning(schema)
    if a.o:
        open(a.o, "w", encoding="utf-8").write(dg)
    stats = {"schema": {"bytes": len(raw.encode()), "chars": len(raw), "tokens_est": est_tokens(raw)},
             "digest": {"bytes": len(dg.encode()), "chars": len(dg), "tokens_est": est_tokens(dg)}}
    if a.meaning:
        mo = open(a.meaning, encoding="utf-8").read()
        stats["output_meaning"] = {"bytes": len(mo.encode()), "chars": len(mo), "tokens_est": est_tokens(mo)}
    if a.call_inputs:
        inp = "".join(open(f, encoding="utf-8").read() for f in a.call_inputs)
        stats["other_inputs"] = {"files": a.call_inputs, "chars": len(inp), "tokens_est": est_tokens(inp)}
        for mode, sch in (("full_schema", raw), ("digest", dg)):
            tot = sch + inp + (open(a.meaning, encoding="utf-8").read() if a.meaning else "")
            stats[f"call_{mode}"] = {"chars": len(tot), "tokens_est": est_tokens(tot),
                                     "fits_32k": [t <= 32000 for t in est_tokens(tot)]}
    print(json.dumps(stats, ensure_ascii=False, indent=1), file=sys.stderr if not a.o else sys.stdout)
    if not a.o:
        sys.stdout.write(dg)


# ---------------------------------------------------------------- meaning-claims (P2, P3 §4)
def _slot(slot_id, slot_type, text, fact_ids=(), missing_ids=(), note=""):
    return {"slot_id": slot_id, "slot_type": slot_type,
            "variants": [{"id": "a", "text": text, "status": "draft", "source": "ai-self"}], "chosen": "a",
            "fact_ids": list(dict.fromkeys(fact_ids)), "missing_ids": list(dict.fromkeys(missing_ids)),
            "claim_flags": [], "notes": note}


def cmd_meaning_claims(a):
    m = load(a.meaning)
    fpath = facts_file_for_meaning(a.meaning, m)
    out_dir = os.path.dirname(os.path.abspath(a.o))
    pages = []
    secs = []
    vp = m.get("value_proposition", {})
    s = [_slot("core", "subheadline", vp.get("core", {}).get("text", ""), note="meaning.value_proposition.core")]
    if m.get("offering_summary"):
        s.append(_slot("offering", "body", m["offering_summary"]["text"], note="meaning.offering_summary"))
    secs.append({"section_id": "m-core", "section_role": "hero", "slots": s})
    if m.get("offer"):
        f, mi = split_ids(m["offer"].get("proof_ids"))
        secs.append({"section_id": "m-offer", "section_role": "pricing",
                     "slots": [_slot("offer", "pricing-price-note", m["offer"].get("summary", ""), f, mi, "meaning.offer.summary")]})
    ua = (m.get("positioning") or {}).get("unique_attributes") or []
    if ua:
        secs.append({"section_id": "m-attributes", "section_role": "solution", "slots": [
            _slot(x["id"], "card-body", x["attribute"], *split_ids(x.get("proof_ids")), note=f"unique_attributes.{x['id']} ({x.get('proof_status')})")
            for x in ua]})
    ob = [o for o in m.get("objections") or [] if o.get("answer")]
    if ob:
        secs.append({"section_id": "m-objections", "section_role": "objections", "slots": [
            _slot(o["id"], "objection-answer", o["answer"], *split_ids(o.get("proof_ids")), note=f"objections.{o['id']}.answer ({o.get('severity')})")
            for o in ob]})
    rr = m.get("risk_reversal") or []
    if rr:
        secs.append({"section_id": "m-risk", "section_role": "guarantee", "slots": [
            _slot(r["id"], "guarantee-text", r["summary"], *split_ids([r.get("fact_id")]), note=f"risk_reversal.{r['id']}")
            for r in rr]})
    pages.append({"page_id": "meaning", "page_type": "landing-lead-services", "sections": secs})
    for hp in a.hierarchy or []:
        h = load(hp)
        hs = []
        cm = h.get("core_message") or {}
        fs = h.get("first_screen") or {}
        f, mi = split_ids(cm.get("proof_ids"))
        f2, mi2 = split_ids(fs.get("proof_ids"))
        slots = [_slot("core", "subheadline", cm.get("text", ""), f, mi, "core_message")]
        fs_text = "; ".join(fs[k] for k in ("what", "for_whom", "outcome", "differentiator", "next_step") if fs.get(k))
        if fs_text:   # поля первого экрана — одним слотом: оговорка факта засчитывается по всему экрану
            slots.append(_slot("first-screen", "body", fs_text, f2, mi2, "first_screen: what; for_whom; outcome; differentiator; next_step"))
        hs.append({"section_id": "h-core", "section_role": "hero", "slots": slots})
        pl = h.get("pillars") or []
        if pl:
            hs.append({"section_id": "h-pillars", "section_role": "benefits", "slots": [
                _slot(p["id"], "card-body", p["message"], *split_ids(p.get("proof_ids")), note=f"pillars.{p['id']} ({p.get('proof_status')})")
                for p in pl]})
        for sc in sorted(h.get("sections") or [], key=lambda x: x.get("order", 0)):
            ff, mm = split_ids(sc.get("proof_ids"))
            hs.append({"section_id": f"s{sc['order']:02d}-{sc['section_role']}", "section_role": sc["section_role"],
                       "slots": [_slot("message", "subheadline" if sc["section_role"] == "hero" else "body", sc.get("message", ""),
                                       ff, mm, f"sections[{sc['order']}].message")]})
        pages.append({"page_id": re.sub(r"[^a-z0-9-]", "-", h.get("id", os.path.basename(hp).split(".")[0])),
                      "page_type": (h.get("page") or {}).get("page_type", "landing-lead-services"), "sections": hs})
    deck = {"copy_deck": {"version": 1, "date": TODAY, "site": m.get("site", "site"), "lang": "ru",
                          "facts_ref": rel(fpath, out_dir) if fpath else "",
                          "notes": "Проекция смысла и иерархий для сверки до текста (chain_inputs.py meaning-claims): "
                                   "это не тексты страницы, а внутренние формулировки; путь слота → поле смысла в notes.",
                          "pages": pages}}
    dump(deck, a.o)
    print(f"meaning-claims: страниц {len(pages)}, слотов {sum(len(s['slots']) for p in pages for s in p['sections'])} → {a.o}", file=sys.stderr)


# ---------------------------------------------------------------- hierarchy-input (P3)
def facts_index(fx, fields=("id", "canonical", "claim_class")):
    out = []
    for f in fx.get("facts", []):
        out.append({k: f.get(k) for k in fields if f.get(k) is not None})
    return {"facts": out, "missing": [{"id": x["id"], "what": x.get("what")} for x in fx.get("missing", [])]}


def cmd_hierarchy_input(a):
    m = load(a.meaning)
    fx = load(facts_file_for_meaning(a.meaning, m))
    prim = next((x for x in m.get("audience", []) if x.get("primary")), None)
    pos = m.get("positioning") or {}
    proj = {
        "MEANING_PROJECTION": {
            "audience_primary": {k: prim.get(k) for k in ("id", "name", "situation", "trigger", "knows", "jobs", "pains", "gains") if prim and prim.get(k)},
            "awareness_by_source": (m.get("awareness") or {}).get("by_source"),
            "sophistication": {k: v for k, v in (m.get("sophistication") or {}).items() if k != "basis"},
            "alternatives": [{k: x.get(k) for k in ("id", "name", "limits", "mention_on_page")} for x in pos.get("alternatives", [])],
            "unique_attributes": [{k: x.get(k) for k in ("id", "attribute", "versus", "proof_status", "proof_ids")} for x in pos.get("unique_attributes", [])],
            "value_themes": [{k: x.get(k) for k in ("id", "theme", "customer_measure", "pain_refs", "proof_ids")} for x in pos.get("value_themes", [])],
            "value_proposition_core": (m.get("value_proposition") or {}).get("core", {}).get("text"),
            "offer": m.get("offer"),
            "objections": [{k: o.get(k) for k in ("id", "text", "severity", "answer", "proof_ids", "where", "awareness_stage", "status")} for o in m.get("objections", [])],
            "risk_reversal": m.get("risk_reversal"),
            "boundaries": m.get("boundaries"),
        },
        "FACTS_INDEX": facts_index(fx),
        "TARGET": {"page_type": a.page_type, "traffic_sources": a.traffic.split(","), "awareness": a.awareness,
                   "promise_of_source": a.promise or next((s.get("promise_of_source") for s in (m.get("traffic") or {}).get("sources", [])
                                                           if s.get("source") in a.traffic.split(",")), "")},
        "SECTION_ROLES": section_roles(),
        "AWARENESS_RULES": {a.awareness: AWARENESS_RULES[a.awareness]},
        "TODAY": TODAY,
    }
    txt = dump(proj, a.o)
    print(f"hierarchy-input: {len(txt)} знаков, токенов ≈ {est_tokens(txt)} [оценка]", file=sys.stderr)


# ---------------------------------------------------------------- section-input (P4)
def slot_card(st, slot, lang, rules_h):
    card = {"slot_id": slot["slot_id"], "slot_type": slot["slot_type"],
            "variants_n": slot.get("x-variants-n", VARIANTS_N.get(slot["slot_type"], 1))}
    if slot.get("group"):
        card["group"] = slot["group"]
    if not st:
        card["note"] = "тип слота не найден в copy-slots.yaml"
        return card
    card["purpose"] = st.get("purpose")
    if st.get("structure"):
        card["structure"] = st["structure"]
    ln = (st.get("length") or {}).get(lang) or {}
    unit = ln.get("primary", "chars")
    if ln.get(unit):
        card["length"] = {"unit": unit, **{k: ln[unit].get(k) for k in ("min", "target", "max")}}
    card["rules"] = [r[:220] for r in (st.get("rules") or [])[:4]]
    card["bans"] = [b[:220] for b in (st.get("bans") or [])]
    card["fact_required"] = st.get("fact_required")
    lr = []
    for rid in st.get("legal_rules") or []:
        r = rules_h.get(rid)
        if r:
            lr.append({"id": rid, "title": r.get("title"), "replacement": (r.get("replacement") or "")[:240]})
    if lr:
        card["legal"] = lr
    return card


def fact_view(f, lang):
    v = {"id": f["id"], "verbatim": f.get("verbatim"), "canonical": f.get("canonical")}
    use = f.get("use") or {}
    if use.get("requires_nearby"):
        v["requires_nearby"] = use["requires_nearby"]
    if (f.get("valid") or {}).get("until"):
        v["valid_until"] = f["valid"]["until"]
    ps = (f.get("permission") or {})
    if ps.get("shows"):
        v["permission_shows"] = ps["shows"]
    if ps.get("status") and ps["status"] not in ("granted", "not-required"):
        v["permission_status"] = ps["status"]
    if lang != "ru" and (f.get("translations") or {}).get(lang):
        v["translation"] = f["translations"][lang]
    return v


def voice_brief(voice, section_role, slot_types):
    tm = [t for t in voice.get("tone_map", []) if t.get("situation") == TONE_SITUATION.get(section_role, section_role)]
    samples = [s for s in voice.get("samples", []) if s.get("slot_type") in slot_types and s.get("lang", "ru") == "ru"][:2]
    return {"prompt_brief": (voice.get("projections") or {}).get("prompt_brief"),
            "avoid": [x["term"] for x in (voice.get("vocabulary") or {}).get("avoid", [])],
            "tone_map": [{"situation": t["situation"], "rules": t.get("rules")} for t in tm],
            "samples": [{"slot_type": s["slot_type"], "text": s["text"]} for s in samples]}


def voc_block(m):
    prim = next((x for x in m.get("audience", []) if x.get("primary")), {})
    return {"situation": prim.get("situation"),
            "jobs": [{"id": j["id"], "statement": j["statement"]} for j in prim.get("jobs", [])],
            "pains": [{"id": p["id"], "text": p["text"]} for p in prim.get("pains", [])],
            "gains": [{"id": g["id"], "text": g["text"]} for g in prim.get("gains", [])],
            "voc": "voc.yaml нет — голос клиента только из meaning (отзывы — факты с разрешением)"}


def never_block(fx):
    out = [{"id": n["id"], "text": n["text"]} for n in fx.get("never_claim", [])]
    if fx.get("never_claim_defaults"):
        try:
            for n in load(FACTS_SCHEMA).get("x-never-claim-defaults", []):
                out.append({"id": n["id"], "text": n["text"]})
        except Exception:  # noqa: BLE001
            pass
    return out


def cmd_section_input(a):
    d = load(a.deck)
    cd = deck_root(d)
    page = find_page(cd, a.page)
    sec = next(s for s in page["sections"] if s["section_id"] == a.section)
    h = load(a.hierarchy)
    m = load(a.meaning)
    fx = load(facts_file_for_deck(a.deck, cd))
    voice = load(a.voice)
    st = {s["id"]: s for s in load(SLOTS)["slot_types"]}
    rules_h = {r["id"]: r for r in load(RULES_H)["rules"]}
    facts = {f["id"]: f for f in fx.get("facts", [])}
    missing = {x["id"]: x for x in fx.get("missing", [])}
    props = {x["id"]: x for x in m.get("x-missing-proposals", [])}
    fids, mids = sec.get("x-fact-ids", []), sec.get("x-missing-ids", [])
    objs = {o["id"]: o for o in m.get("objections", [])}
    prev = []
    for s in page["sections"]:
        if s["section_id"] == a.section:
            break
        for sl in s["slots"]:
            if sl["slot_type"] in ("headline", "section-title", "case-title") and chosen_text(sl):
                prev.append(f"{s['section_role']}: {chosen_text(sl)}")
    cm = h.get("core_message") or {}
    hero_cta = next((chosen_text(sl) for s in page["sections"] if s["section_role"] == "hero" for sl in s["slots"]
                     if sl["slot_type"] == "cta-label" and chosen_text(sl)), None)
    proj = {
        "PAGE_HEADER": {"lang": a.lang, "page_type": page["page_type"], "awareness": page.get("awareness"),
                        "hero_approach": cm.get("hero_approach"), "core_message": cm.get("text"),
                        "primary_action": page.get("primary_action") or hero_cta or (h.get("first_screen") or {}).get("next_step"),
                        "brand": cd.get("product_name"), "must_not_say": cm.get("must_not_say")},
        "SECTION": {"section_id": sec["section_id"], "section_role": sec.get("section_role"), "question": sec.get("question"),
                    "message": sec.get("message"), "carries": sec.get("carries"), "next_step": sec.get("x-next-step"),
                    "objections": [{"id": o, "text": objs[o]["text"], "answer": objs[o].get("answer")} for o in sec.get("x-objection-ids", []) if o in objs]},
        "PREV_TITLES": prev,
        "SLOT_CARDS": [slot_card(st.get(sl["slot_type"]), sl, a.lang, rules_h) for sl in sec["slots"]],
        "FACTS": [fact_view(facts[f], a.lang) for f in fids if f in facts],
        "MISSING": [{"id": x, "placeholder": (missing.get(x) or {}).get("placeholder", f"[PLACEHOLDER: {(props.get(x) or {}).get('what', x)}]"),
                     "fallback": (missing.get(x) or {}).get("fallback", "placeholder"), "what": (missing.get(x) or props.get(x) or {}).get("what")}
                    for x in mids],
        "NEVER_CLAIM": never_block(fx),
        "VOICE_BRIEF": voice_brief(voice, sec.get("section_role"), {sl["slot_type"] for sl in sec["slots"]}),
        "VOC": voc_block(m),
        "MODE": "write",
    }
    txt = dump(proj, a.o)
    print(f"section-input {a.section}: {len(txt)} знаков, токенов ≈ {est_tokens(txt)} [оценка]", file=sys.stderr)


# ---------------------------------------------------------------- edit-input (P6)
def iter_slots(page):
    for s in page["sections"]:
        for sl in s["slots"]:
            yield s, sl


def cmd_edit_input(a):
    d = load(a.deck)
    cd = deck_root(d)
    chk = json.load(open(a.check, encoding="utf-8"))
    st = {s["id"]: s for s in load(SLOTS)["slot_types"]}
    fx = load(facts_file_for_deck(a.deck, cd))
    facts = {f["id"]: f for f in fx.get("facts", [])}
    lvl = {"error"} if a.pass_ == 1 else {"warning"}
    by = defaultdict(list)
    for f in chk["findings"]:
        by[f.get("where", "")].append(f)
    slots_out, findings_out = [], []
    for p in cd["pages"]:
        for s, sl in iter_slots(p):
            path = f"{p['page_id']}/{s['section_id']}/{sl['slot_id']}"
            fs = by.get(path, [])
            main = [f for f in fs if f["level"] in lvl]
            if not main:
                continue
            extra = [f for f in fs if f["level"] == "info"] if a.pass_ > 1 else []
            text = chosen_text(sl)
            words = len(re.findall(r"\w+", text))
            ln = ((st.get(sl["slot_type"]) or {}).get("length") or {}).get(cd.get("lang", "ru")) or {}
            unit = ln.get("primary", "chars")
            slots_out.append({"path": path, "slot_type": sl["slot_type"], "text": text, "fact_ids": sl.get("fact_ids", []),
                              "missing_ids": sl.get("missing_ids", []),
                              "length": {"unit": unit, **{k: (ln.get(unit) or {}).get(k) for k in ("min", "target", "max")}} if ln else None,
                              "clusters_max": 1 if sl["slot_type"] in SHORT_SLOTS else max(1, round(5 * words / 300))})
            for f in main + extra:
                findings_out.append({k: f.get(k) for k in ("tool", "level", "rule", "where", "message", "fix", "fragment")})
        for field, text in (p.get("meta") or {}).items():   # мета: путь <page>/meta/<поле>
            path = f"{p['page_id']}/meta/{field}"
            main = [f for f in by.get(path, []) if f["level"] in lvl]
            if main and isinstance(text, str):
                slots_out.append({"path": path, "slot_type": "meta-" + field.replace("_", "-") if not field.startswith("og") else field.replace("_", "-"),
                                  "text": text, "fact_ids": (p.get("meta") or {}).get("fact_ids", []), "missing_ids": [], "length": None, "clusters_max": 1})
                findings_out += [{k: f.get(k) for k in ("tool", "level", "rule", "where", "message", "fix", "fragment")} for f in main]
        page_level = [f for f in by.get(p["page_id"], []) if f["level"] in lvl]
        findings_out += [{k: f.get(k) for k in ("tool", "level", "rule", "where", "message", "fix", "fragment")} for f in page_level]
    used = {fid for s in slots_out for fid in s["fact_ids"]}
    proj = {"PASS": a.pass_, "SLOTS": slots_out, "FINDINGS": findings_out,
            "FACTS": [fact_view(facts[f], cd.get("lang", "ru")) for f in sorted(used) if f in facts],
            "NEVER_CLAIM": never_block(fx),
            "VOICE_BRIEF": voice_brief(load(a.voice), "", set()) if a.voice else None,
            "KEEP": "цитаты отзывов, дословные факты (verbatim, canonical), условия (в черте города, без материалов, даты), цена, текст кнопки, названия"}
    txt = dump(proj, a.o)
    print(f"edit-input pass {a.pass_}: слотов {len(slots_out)}, находок {len(findings_out)}, {len(txt)} знаков, "
          f"токенов ≈ {est_tokens(txt)} [оценка]", file=sys.stderr)


# ---------------------------------------------------------------- judge-input / judge-score (P7)
DEFAULT_SCOPE = {"COPY-R-01": "first-screen", "COPY-R-05": "page", "COPY-R-09": "first-screen+ctas",
                 "COPY-R-07": "titles", "COPY-R-08": "risk", "COPY-R-04": "page", "COPY-R-02": "page",
                 "COPY-R-03": "page", "COPY-R-06": "page"}
RISK_TYPES = {"cta-note", "guarantee-text", "faq-q", "faq-a", "pricing-price-note", "objection-answer", "cta-label"}


def scope_text(page, scope):
    lines = []
    for s, sl in iter_slots(page):
        t = chosen_text(sl)
        if not t:
            continue
        role = s.get("section_role")
        if scope == "first-screen" and role != "hero":
            continue
        if scope == "first-screen+ctas" and role != "hero" and sl["slot_type"] not in ("cta-label", "cta-note", "form-next-steps"):
            continue
        if scope == "titles" and sl["slot_type"] not in ("headline", "section-title", "case-title"):
            continue
        if scope == "risk" and sl["slot_type"] not in RISK_TYPES:
            continue
        if scope.startswith("section:") and s["section_id"] != scope.split(":", 1)[1]:
            continue
        lines.append(f"[{s['section_id']}/{sl['slot_id']} · {sl['slot_type']}] {t}")
    return "\n".join(lines)


def cmd_judge_input(a):
    d = load(a.deck)
    cd = deck_root(d)
    page = find_page(cd, a.page)
    rub = load(RUBRIC)
    crit = next(c for c in rub["criteria"] if c["id"] == a.criterion)
    scope = a.scope or DEFAULT_SCOPE.get(a.criterion, "page")
    lang = a.lang
    qs = [{"id": q["id"], lang: q.get(lang), **({"read": q["read"]} if q.get("read") else {})} for q in crit["judge"]["questions"]]
    proj = {"PATH": a.page, "SCOPE": scope, "TEXT": scope_text(page, scope),
            "CRITERION": {"id": crit["id"], "name": crit["name"], "questions": qs}}
    num = crit["id"].split("-")[-1]
    if num in ("03", "08"):
        fx = load(facts_file_for_deck(a.deck, cd))
        proj["FACTS"] = [{"id": f["id"], "canonical": f.get("canonical"),
                          **({"requires_nearby": f["use"]["requires_nearby"]} if (f.get("use") or {}).get("requires_nearby") else {})}
                         for f in fx.get("facts", []) if (f.get("permission") or {}).get("status") in ("granted", "not-required", None)]
    if num in ("02", "04"):
        m = load(a.meaning)
        pos = m.get("positioning") or {}
        proj["MEANING_EXCERPT"] = {"alternatives": [{"id": x["id"], "name": x["name"]} for x in pos.get("alternatives", [])],
                                   "unique_attributes": [{"attribute": x["attribute"], "proof_status": x.get("proof_status")} for x in pos.get("unique_attributes", [])],
                                   "claims_heard": (m.get("sophistication") or {}).get("claims_heard")}
    if num in ("01", "05", "07", "08"):
        h = load(a.hierarchy)
        m = load(a.meaning)
        objs = {o["id"]: o for o in m.get("objections", [])}
        blockers = sorted({o for s in h.get("sections", []) for o in s.get("objection_ids", []) or [] if (objs.get(o) or {}).get("severity") == "blocker"})
        proj["HIERARCHY_EXCERPT"] = {"core_message": (h.get("core_message") or {}).get("text"),
                                     "hero_approach": (h.get("core_message") or {}).get("hero_approach"),
                                     "must_not_say": (h.get("core_message") or {}).get("must_not_say"),
                                     "first_screen": h.get("first_screen"),
                                     "sections": [{"order": s["order"], "role": s["section_role"], "question": s.get("question")} for s in h.get("sections", [])],
                                     "blocker_objections": [{"id": o, "text": objs[o]["text"]} for o in blockers],
                                     "not_said": h.get("not_said"), "argument_depth": (h.get("page") or {}).get("argument_depth")}
    txt = dump(proj, a.o)
    print(f"judge-input {a.criterion} ({scope}): {len(txt)} знаков, токенов ≈ {est_tokens(txt)} [оценка]", file=sys.stderr)


def round_half_up(x):
    return int(x + 0.5)


def score_answers(answers, caps):
    """answers: {qid: yes|no|unsure|n/a}; caps: {qid: cap_if_no}. Формула copy-rubric.yaml → judge_scoring."""
    answered = [q for q, v in answers.items() if v != "n/a"]
    if len(answered) < 2:
        return None, 0, 0
    yes = sum(1 for q in answered if answers[q] == "yes")
    share = yes / len(answered)
    score = max(1, round_half_up(5 * share))
    nos = [caps[q] for q in answered if answers[q] == "no" and caps.get(q) is not None]
    if nos:
        score = min(score, min(nos))
    return score, yes, len(answered)


def majority(vals):
    c = Counter(vals)
    top, n = c.most_common(1)[0]
    if n * 2 > len(vals):
        return top
    return "unsure"


def cmd_judge_score(a):
    rub = load(RUBRIC)
    caps = {c["id"]: {q["id"]: q.get("cap_if_no") for q in c["judge"]["questions"]} for c in rub["criteria"] if c.get("judge")}
    runs = defaultdict(lambda: defaultdict(list))   # (criterion, path) → qid → [answers]
    quotes = defaultdict(list)
    pairs = defaultdict(list)                       # (slot, frozenset(pair)) → [(shown, winner)]
    for fp in a.answers:
        data = json.load(open(fp, encoding="utf-8"))
        for r in (data if isinstance(data, list) else [data]):
            if "shown" in r:                        # попарный режим P7: shown = [вариант в A, вариант в B]
                pairs[(r["slot"], frozenset(r["shown"]))].append((r["shown"], r["winner"]))
                continue
            key = (r["criterion"], r.get("path", ""))
            for x in r["answers"]:
                runs[key][x["id"]].append(x["answer"])
                if x["answer"] == "no":
                    quotes[key].append({"q": x["id"], "where": x.get("where")})
    out = []
    for (crit, path), qa in sorted(runs.items()):
        ans = {q: majority(v) for q, v in qa.items()}
        n_runs = max(len(v) for v in qa.values())
        if crit.startswith("COPY-GEO-"):
            v = ans.get("q1") or next(iter(ans.values()))
            ok = (v == "no") if crit in GEO_PASS_IF_NO else (v == "yes")
            out.append({"criterion": crit, "path": path, "runs": n_runs, "answer": v, "pass": ok if v in ("yes", "no") else None})
            continue
        score, yes, answered = score_answers(ans, caps.get(crit, {}))
        out.append({"criterion": crit, "path": path, "runs": n_runs, "answers": ans, "yes": yes, "answered": answered,
                    "score": score, "judge_no": quotes[(crit, path)] or None,
                    "unstable": sorted(q for q, v in qa.items() if len(set(v)) > 1) or None})
    pw, a_wins, decisive = [], 0, 0
    for (slot, _), calls in sorted(pairs.items(), key=lambda x: (x[0][0], sorted(x[0][1]))):
        winners = []
        for shown, w in calls:
            if w in ("A", "B"):
                decisive += 1
                a_wins += w == "A"
                winners.append(shown[0] if w == "A" else shown[1])
            else:
                winners.append(w)
        both = len(calls) >= 2 and len(set(winners)) == 1 and winners[0] not in ("tie", "neither")
        pw.append({"slot": slot, "pair": sorted({v for sh, _ in calls for v in sh}), "calls": len(calls),
                   "winners_by_order": winners, "result": winners[0] if both else "tie (порядки не совпали или ничья)"})
    if pw:
        share = a_wins / decisive if decisive else None
        out.append({"pairwise": pw, "a_share": share, "biased": (share is not None and not 0.35 <= share <= 0.65)})
    dump({"rubric_version": rub.get("version"), "scored_at": TODAY, "results": out}, a.o)


def section_roles():
    """Роли секций словаря site v1 (namespaces.section_role.values[].id)."""
    ns = (load(VOCAB) or {}).get("namespaces") or {}
    return [x["id"] for x in (ns.get("section_role") or {}).get("values") or [] if isinstance(x, dict) and x.get("id")]


# ---------------------------------------------------------------- assemble (P4/P5 → deck) и apply-edits (P6)
AGENT_STATUS = "assumed"   # текст агента в copy deck — черновик «допущением»; утверждает владелец продукта


def agent_status(v):
    """Статус варианта из выхода промта: пустой или draft → assumed; checked, approved, rejected — как есть."""
    if v.get("status") in (None, "", "draft"):
        v["status"] = AGENT_STATUS
def gen_block(prompt_ref, technique, by, run_id):
    return {"model": by, "channel": "none (ai-self)", "prompt_ref": prompt_ref, "run_id": run_id, "date": TODAY,
            "params": {"mode": "ai-self"}, **({"technique": technique} if technique else {})}


def cmd_assemble(a):
    d = load(a.skeleton)
    cd = deck_root(d)
    page = cd["pages"][0] if not a.page else find_page(cd, a.page)
    by_id = {s["section_id"]: s for s in page["sections"]}
    run = f"assemble-{TODAY}"
    parts = [x for fp in a.parts for x in yaml.safe_load_all(open(fp, encoding="utf-8")) if x]   # файл — один или несколько документов
    for part in parts:
        fp = part.get("section", {}).get("section_id") or "meta/faq"
        if "section" in part:
            sec = part["section"]
            target = by_id.get(sec["section_id"])
            if target is None:
                raise SystemExit(f"{fp}: секции {sec['section_id']} нет в скелете")
            keep = {k: v for k, v in target.items() if k.startswith("x-")}
            for k in ("section_role", "question", "message", "carries"):
                if sec.get(k):
                    target[k] = sec[k]
            for sl in sec["slots"]:
                for v in sl["variants"]:
                    g = v.get("generated") or {}
                    v["source"] = "ai-self"
                    agent_status(v)
                    v["generated"] = gen_block(g.get("prompt_ref"), g.get("technique"), a.by, run)
            target["slots"] = sec["slots"]
            target.update(keep)
        if "meta" in part:
            mt = part["meta"]
            for vv in (mt.get("variants") or {}).values():
                for v in vv:
                    v["source"] = "ai-self"
                    agent_status(v)
                    v["generated"] = gen_block("09-ai-generation-evaluation/prompts/p5-meta-geo.md#ru@1", v.get("x-technique"), a.by, run)
                    v.pop("x-technique", None)
            page["meta"] = mt
        if "faq_section" in part:
            fs = part["faq_section"]
            for sl in fs["slots"]:
                for v in sl["variants"]:
                    v["source"] = "ai-self"
                    agent_status(v)
                    v["generated"] = gen_block("09-ai-generation-evaluation/prompts/p5-meta-geo.md#ru@1", None, a.by, run)
            if fs["section_id"] in by_id:
                by_id[fs["section_id"]].update({k: v for k, v in fs.items() if k != "section_id"})
            else:
                idx = next((i for i, s in enumerate(page["sections"]) if s.get("section_role") == "final-cta"), len(page["sections"]))
                page["sections"].insert(idx, fs)
    hero = next((s for s in page["sections"] if s.get("section_role") == "hero"), None)
    if hero:
        lead = next((sl for sl in hero["slots"] if sl["slot_type"] == "subheadline"), None)
        cta = next((sl for sl in hero["slots"] if sl["slot_type"] == "cta-label"), None)
        if lead:
            page["promise"] = {"from": f"{page['page_id']}/{hero['section_id']}/{lead['slot_id']}", "basis": "hierarchy.core_message"}
        if cta and chosen_text(cta):
            page["cta_primary"] = f"{page['page_id']}/{hero['section_id']}/{cta['slot_id']}"
            page["primary_action"] = chosen_text(cta)
    cd["date"] = TODAY
    dump(d, a.o)
    print(f"assemble: {len(parts)} частей из {len(a.parts)} файлов → {a.o}", file=sys.stderr)


def cmd_apply_edits(a):
    d = load(a.deck)
    cd = deck_root(d)
    ed = load(a.edits) or {}
    n_ed = n_allow = n_left = 0
    idx = {}
    for p in cd["pages"]:
        for s, sl in iter_slots(p):
            idx[f"{p['page_id']}/{s['section_id']}/{sl['slot_id']}"] = sl
    for e in ed.get("edits") or []:
        path = e["path"]
        if "/meta/" in path:
            pid, _, field = path.split("/")
            page = find_page(cd, pid)
            page["meta"][field] = e["text"]
            vv = (page["meta"].setdefault("variants", {})).setdefault(field, [])
            for v in vv:
                if v["id"] == e.get("from_variant"):
                    v["status"] = "rejected"
                    v["reason"] = "правка по находкам: " + ", ".join(sorted({f["rule"] for f in e.get("fixes", [])}))
            vv.append({"id": e["to_variant"], "text": e["text"], "status": AGENT_STATUS, "source": "ai-self",
                       "generated": gen_block("09-ai-generation-evaluation/prompts/p6-edit-findings.md#ru@1", "edit-findings", a.by, f"p6-pass{a.pass_}")})
            n_ed += 1
            continue
        sl = idx.get(path)
        if sl is None:
            raise SystemExit(f"слот {path} не найден")
        old = next(v for v in sl["variants"] if v["id"] == e.get("from_variant", sl.get("chosen")))
        rules = sorted({f["rule"] for f in e.get("fixes", [])})
        old["status"] = "rejected"
        old["reason"] = "правка по находкам: " + ", ".join(rules)
        sl["variants"].append({"id": e["to_variant"], "text": e["text"], "status": AGENT_STATUS, "source": "ai-self",
                               "generated": gen_block("09-ai-generation-evaluation/prompts/p6-edit-findings.md#ru@1", "edit-findings", a.by, f"p6-pass{a.pass_}")})
        sl["chosen"] = e["to_variant"]
        if "fact_ids" in e:
            sl["fact_ids"] = e["fact_ids"]
        if "missing_ids" in e:
            sl["missing_ids"] = e["missing_ids"]
        sl.setdefault("edit_log", []).append({"pass": a.pass_, "rules": rules, "clusters": len({f.get("cluster") for f in e.get("fixes", [])}),
                                              "by": a.by, "date": TODAY, "from_variant": old["id"], "to_variant": e["to_variant"]})
        n_ed += 1
    for la in ed.get("lint_allow") or []:
        sl = idx.get(la["path"])
        if sl is not None:
            sl.setdefault("lint_allow", []).append({"rule": la["rule"], "reason": la["reason"]})
            n_allow += 1
    for lf in ed.get("left_for_human") or []:
        sl = idx.get(lf["path"])
        if sl is not None:
            sl["notes"] = (sl.get("notes", "") + f" · человеку (проход {a.pass_}): {lf['rule']} — {lf['why']}").strip(" ·")
            n_left += 1
    cd["date"] = TODAY
    dump(d, a.o)
    print(f"apply-edits pass {a.pass_}: правок {n_ed}, lint_allow {n_allow}, человеку {n_left} → {a.o}", file=sys.stderr)


# ---------------------------------------------------------------- canvas-texts (тексты во вход холста)
def cmd_canvas_texts(a):
    """Выгрузка текстов страницы во вход холста — copydeck.py export: pages/<page-id>/copy.md и facts.md по протоколу
    references/claude-design.md § 6 (этап wireframe — тексты assumed, checked, approved; mockup — только approved)."""
    import copydeck  # noqa: E402 — владелец выгрузки
    argv = ["export", a.deck, "--stage", a.stage, "--facts-scope", a.facts_scope]
    for k, v in (("--page", a.page), ("--out", a.out), ("--facts", a.facts), ("--today", a.today)):
        if v:
            argv += [k, v]
    return copydeck.main(argv)


# ---------------------------------------------------------------- selftest
def selftest():
    res = []
    rub = load(RUBRIC)
    for ex in rub["judge_scoring"]["examples"]:
        ans = {f"q{i}": "yes" for i in range(ex["yes_count"])}
        no_caps = list(ex["caps"])
        for i in range(ex["answered"] - ex["yes_count"]):
            ans[f"n{i}"] = "no"
        caps = {f"n{i}": (no_caps[i] if i < len(no_caps) else None) for i in range(ex["answered"] - ex["yes_count"])}
        sc, _, _ = score_answers(ans, caps)
        res.append((f"judge_scoring пример yes={ex['yes_count']}/{ex['answered']} caps={ex['caps']} → {ex['score']}", sc == ex["score"]))
    res.append(("большинство при расхождении прогонов → unsure", majority(["yes", "no"]) == "unsure" and majority(["yes", "yes", "no"]) == "yes"))
    dg = digest_meaning(load(MEANING_SCHEMA))
    res.append(("проекция схемы meaning ≤ 5 000 знаков и содержит все обязательные поля",
                len(dg) <= 5000 and all(k in dg for k in load(MEANING_SCHEMA)["required"])))
    deck = {"copy_deck": {"version": 1, "date": "2026-09-24", "site": "t", "lang": "ru", "pages": [{"page_id": "p", "page_type": "landing-lead-services", "sections": [
        {"section_id": "hero", "section_role": "hero", "slots": [{"slot_id": "h1", "slot_type": "headline", "variants": [{"id": "a", "text": "Старый", "status": "draft"}], "chosen": "a"}]}]}]}}
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        dp, ep, op = (os.path.join(td, x) for x in ("d.yaml", "e.yaml", "o.yaml"))
        dump(deck, dp)
        dump({"edits": [{"path": "p/hero/h1", "from_variant": "a", "to_variant": "b", "text": "Новый",
                         "fixes": [{"rule": "ru-x", "cluster": 1, "action": "delete"}]}]}, ep)
        ns = argparse.Namespace(deck=dp, edits=ep, pass_=2, by="test", o=op)
        _stderr, sys.stderr = sys.stderr, open(os.devnull, "w")
        try:
            cmd_apply_edits(ns)
        finally:
            sys.stderr = _stderr
        sl = load(op)["copy_deck"]["pages"][0]["sections"][0]["slots"][0]
        res.append(("apply-edits: новый вариант выбран и assumed, старый rejected с причиной, edit_log записан",
                    sl["chosen"] == "b" and sl["variants"][0]["status"] == "rejected" and "ru-x" in sl["variants"][0]["reason"]
                    and sl["variants"][1]["status"] == "assumed" and sl["edit_log"][0]["pass"] == 2))
    v1, v2 = {"status": "draft"}, {"status": "checked"}
    agent_status(v1)
    agent_status(v2)
    res.append(("выход промта: draft → assumed, checked остаётся", v1["status"] == "assumed" and v2["status"] == "checked"))
    roles = section_roles()
    res.append(("роли секций — словарь site v1 (hero, final-cta)", "hero" in roles and "final-cta" in roles and len(roles) >= 20))
    ok = sum(1 for _, r in res if r)
    for n, r in res:
        print(("OK   " if r else "FAIL ") + n)
    print(f"selftest: {ok} из {len(res)}")
    return 0 if ok == len(res) else 2


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("digest-meaning"); s.add_argument("--schema", default=MEANING_SCHEMA); s.add_argument("--meaning")
    s.add_argument("--call-inputs", nargs="*"); s.add_argument("-o")
    s = sub.add_parser("meaning-claims"); s.add_argument("--meaning", required=True); s.add_argument("--hierarchy", nargs="*"); s.add_argument("-o", required=True)
    s = sub.add_parser("hierarchy-input"); s.add_argument("--meaning", required=True); s.add_argument("--awareness", required=True)
    s.add_argument("--traffic", required=True); s.add_argument("--promise"); s.add_argument("--page-type", default="landing-lead-services"); s.add_argument("-o")
    s = sub.add_parser("section-input")
    for k in ("--deck", "--page", "--section", "--hierarchy", "--meaning", "--voice"):
        s.add_argument(k, required=True)
    s.add_argument("--lang", default="ru"); s.add_argument("-o")
    s = sub.add_parser("edit-input"); s.add_argument("--deck", required=True); s.add_argument("--check", required=True)
    s.add_argument("--pass", dest="pass_", type=int, required=True); s.add_argument("--voice"); s.add_argument("-o")
    s = sub.add_parser("judge-input")
    for k in ("--deck", "--page", "--criterion"):
        s.add_argument(k, required=True)
    s.add_argument("--scope"); s.add_argument("--hierarchy"); s.add_argument("--meaning"); s.add_argument("--lang", default="ru"); s.add_argument("-o")
    s = sub.add_parser("judge-score"); s.add_argument("--answers", nargs="+", required=True); s.add_argument("-o")
    s = sub.add_parser("assemble"); s.add_argument("--skeleton", required=True); s.add_argument("--parts", nargs="+", required=True)
    s.add_argument("--page"); s.add_argument("--by", required=True); s.add_argument("-o", required=True)
    s = sub.add_parser("apply-edits"); s.add_argument("--deck", required=True); s.add_argument("--edits", required=True)
    s.add_argument("--pass", dest="pass_", type=int, required=True); s.add_argument("--by", required=True); s.add_argument("-o", required=True)
    s = sub.add_parser("canvas-texts"); s.add_argument("--deck", required=True); s.add_argument("--page")
    s.add_argument("--stage", default="wireframe", choices=["directions", "wireframe", "mockup"]); s.add_argument("--out")
    s.add_argument("--facts"); s.add_argument("--today"); s.add_argument("--facts-scope", default="all", choices=["all", "used"])
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    fn = {"digest-meaning": cmd_digest_meaning, "meaning-claims": cmd_meaning_claims, "hierarchy-input": cmd_hierarchy_input,
          "section-input": cmd_section_input, "edit-input": cmd_edit_input, "judge-input": cmd_judge_input,
          "judge-score": cmd_judge_score, "assemble": cmd_assemble, "apply-edits": cmd_apply_edits,
          "canvas-texts": cmd_canvas_texts}.get(a.cmd)
    if not fn:
        ap.print_help()
        sys.exit(1)
    rc = fn(a)
    if isinstance(rc, int):
        sys.exit(rc)


if __name__ == "__main__":
    main()
