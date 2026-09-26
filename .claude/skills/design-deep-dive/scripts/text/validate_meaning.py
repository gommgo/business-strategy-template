#!/usr/bin/env python3
"""Проверка схем B1 (meaning, message-hierarchy) и примеров: загрузка, JSON Schema 2020-12, смысловые проверки.

text-research · волна 1 · агент B1 · 2026-09-24

Запуск (из корня text-research):
    99-raw/tools/venv-B1/bin/python 99-raw/experiments/B1/03-schema-validate/validate.py [--quiet] [--no-negative]

Что проверяет:
  1. Обе схемы загружаются yaml.safe_load и проходят метасхему draft 2020-12.
  2. Каждый examples/meaning-*.yaml и examples/hierarchy-*.yaml проходит свою схему.
  3. Смысловые проверки meaning: уникальность id; все внутренние ссылки (альтернативы, свойства, боли, выгоды,
     возражения, снятие риска, вопросы) разрешаются; допущения ведут в open_questions; ссылки fact:/missing: сверяются с
     facts.yaml из proof_ref (если файл есть рядом), неизвестные missing — предупреждение (кандидаты в missing B2);
     обещания (core, offering, темы ценности) не задевают never_claim с lift: never (урок «Кварца»); вопросов
     приоритета 1 не больше 7 (одно сообщение заказчику, kimi 07/01 §4.1).
  4. Смысловые проверки hierarchy: первая секция — hero; каждая опора несётся хотя бы одной секцией; hero несёт core;
     порядок секций без повторов; ссылки на ценности и возражения разрешаются в meaning_ref; возражения-блокеры
     основного сегмента закрыты до final-cta; тип hero соответствует уровню осведомлённости (предупреждение);
     never_claim в главном сообщении, опорах и сообщениях секций.
  5. Отрицательные случаи (в памяти): каждый должен дать ошибку.
Код выхода: 0 — ошибок нет; 1 — есть ошибки (предупреждения не влияют).
"""
import copy
import glob
import os
import re
import sys

import yaml
from jsonschema import Draft202012Validator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb("text"))
SM = os.path.join(ROOT, "02-strategy-messaging")
EX = os.path.join(SM, "examples")

HERO_BY_AWARENESS = {
    "most-aware": "direct-offer",
    "product-aware": "product-benefit",
    "solution-aware": "solution-vs-alternatives",
    "problem-aware": "problem-story",
    "unaware": "identity",
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def schema_errors(validator, doc):
    return [f"{'/'.join(map(str, e.path)) or '(корень)'}: {e.message[:180]}"
            for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.path))]


def collect_ids(obj, out, path=""):
    """Все значения ключа id внутри блока (кроме x-*) → список (id, путь)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).startswith("x-"):
                continue
            if k == "id" and isinstance(v, str):
                out.append((v, path))
            collect_ids(v, out, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            collect_ids(v, out, f"{path}[{i}]")


def walk_basis(obj, out, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).startswith("x-"):
                continue
            if k == "basis" and isinstance(v, dict):
                out.append((path, v))
            walk_basis(v, out, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk_basis(v, out, f"{path}[{i}]")


def walk_proof_ids(obj, out, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).startswith("x-"):
                continue
            if k in ("proof_ids", "proof_order") and isinstance(v, list):
                for p in v:
                    out.append((f"{path}/{k}", p))
            elif k == "fact_id" and isinstance(v, str):
                out.append((f"{path}/{k}", v))
            else:
                walk_proof_ids(v, out, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk_proof_ids(v, out, f"{path}[{i}]")


def facts_index(meaning_path, meaning):
    """Ищет facts.yaml из proof_ref рядом с meaning; возвращает (facts_ids, missing_ids, never_patterns) или None."""
    ref = (meaning or {}).get("proof_ref")
    if not ref:
        return None
    cand = os.path.normpath(os.path.join(os.path.dirname(meaning_path), ref))
    if not os.path.exists(cand):
        return None
    fx = load(cand)
    fids = {f["id"] for f in fx.get("facts", []) if isinstance(f, dict) and "id" in f}
    mids = {m["id"] for m in fx.get("missing", []) if isinstance(m, dict) and "id" in m}
    pats = []
    for nc in fx.get("never_claim", []) or []:
        if isinstance(nc, dict) and nc.get("lift") == "never":
            for p in nc.get("patterns", []) or []:
                pats.append((nc.get("id"), p))
    return fids, mids, pats, cand


def check_never(texts, pats, where, errors):
    for label, t in texts:
        if not isinstance(t, str):
            continue
        for ncid, p in pats:
            if re.search(p, t, flags=re.I | re.U):
                errors.append(f"{where}: {label} задевает never_claim {ncid} (/{p}/): «{t[:80]}»")


def semantic_meaning(path, m):
    errors, warnings, info = [], [], {}
    ids = []
    collect_ids(m, ids)
    seen = {}
    for i, p in ids:
        if i in seen:
            errors.append(f"id «{i}» повторяется: {seen[i]} и {p}")
        seen[i] = p
    pos = m.get("positioning", {}) or {}
    alts = {a["id"] for a in pos.get("alternatives", [])}
    attrs = {a["id"] for a in pos.get("unique_attributes", [])}
    themes = {t["id"] for t in pos.get("value_themes", [])}
    segs = {s["id"] for s in m.get("audience", [])}
    jobs, pains, gains = set(), set(), set()
    for s in m.get("audience", []):
        jobs |= {j["id"] for j in s.get("jobs", [])}
        pains |= {p["id"] for p in s.get("pains", [])}
        gains |= {g["id"] for g in s.get("gains", [])}
    objs = {o["id"]: o for o in m.get("objections", [])}
    rrs = {r["id"] for r in m.get("risk_reversal", []) or []}
    qs = {q["id"]: q for q in m.get("open_questions", []) or []}

    def need(ref, pool, what, where):
        if ref not in pool:
            errors.append(f"{where}: ссылка на {what} «{ref}» не найдена")

    for s in m.get("audience", []):
        for a in s.get("current_alternative_ids", []) or []:
            need(a, alts, "альтернативу", f"audience/{s['id']}")
        for coll in ("pains", "gains"):
            for it in s.get(coll, []):
                if it.get("job_ref"):
                    need(it["job_ref"], jobs, "работу", f"audience/{s['id']}/{coll}/{it['id']}")
    for a in pos.get("unique_attributes", []):
        for v in a.get("versus", []):
            need(v, alts, "альтернативу", f"unique_attributes/{a['id']}")
    for t in pos.get("value_themes", []):
        for a in t.get("from_attributes", []):
            need(a, attrs, "свойство", f"value_themes/{t['id']}")
        for c in t.get("chain", []) or []:
            need(c["attribute_ref"], attrs, "свойство", f"value_themes/{t['id']}/chain")
        for p in t.get("pain_refs", []) or []:
            need(p, pains, "боль", f"value_themes/{t['id']}")
        for g in t.get("gain_refs", []) or []:
            need(g, gains, "выгоду", f"value_themes/{t['id']}")
    for sid in (pos.get("best_fit", {}) or {}).get("segment_ids", []):
        need(sid, segs, "сегмент", "best_fit")
    for w in pos.get("only_we_can_say", []) or []:
        for a in w.get("checked_against", []):
            need(a, alts, "альтернативу", "only_we_can_say")
    vp = m.get("value_proposition", {}) or {}
    for coll, key, pool, what in (("pain_relievers", "pain_refs", pains, "боль"), ("gain_creators", "gain_refs", gains, "выгоду")):
        for it in vp.get(coll, []) or []:
            for r in it.get(key, []):
                need(r, pool, what, f"value_proposition/{coll}/{it['id']}")
    for force, items in (vp.get("forces", {}) or {}).items():
        for it in items:
            for o in it.get("objection_ids", []) or []:
                need(o, objs, "возражение", f"forces/{force}")
    for o in objs.values():
        for r in o.get("risk_reversal_ids", []) or []:
            need(r, rrs, "снятие риска", f"objections/{o['id']}")
        for s in o.get("segment_ids", []) or []:
            need(s, segs, "сегмент", f"objections/{o['id']}")
    for r in m.get("risk_reversal", []) or []:
        for o in r.get("answers", []) or []:
            need(o, objs, "возражение", f"risk_reversal/{r['id']}")
    for r in (m.get("offer", {}) or {}).get("risk_reversal_ids", []) or []:
        need(r, rrs, "снятие риска", "offer")

    bases = []
    walk_basis(m, bases)
    kinds = {}
    for p, b in bases:
        kinds[b.get("kind")] = kinds.get(b.get("kind"), 0) + 1
        if b.get("kind") == "assumption":
            q = b.get("question_id")
            if q not in qs:
                errors.append(f"{p}: допущение без вопроса в open_questions (question_id={q})")
    info["basis_kinds"] = kinds
    p1 = [q for q in qs.values() if q.get("priority") == 1]
    if len(p1) > 7:
        warnings.append(f"вопросов приоритета 1: {len(p1)} > 7 (одно сообщение заказчику — kimi 07/01 §4.1)")
    info["questions"] = len(qs)
    info["questions_p1"] = len(p1)

    fx = facts_index(path, m)
    proofs = []
    walk_proof_ids(m, proofs)
    info["proof_refs"] = len(proofs)
    proposals = {x.get("id") for x in (m.get("x-missing-proposals") or []) if isinstance(x, dict)}
    unresolved = set()
    if fx:
        fids, mids, pats, fpath = fx
        info["facts_file"] = os.path.relpath(fpath, ROOT)
        for where, pid in proofs:
            kind, _, pid_ = pid.partition(":")
            if kind == "fact" and pid_ not in fids:
                errors.append(f"{where}: fact:{pid_} нет в {os.path.basename(fpath)}")
            if kind == "missing" and pid_ not in mids:
                unresolved.add(pid_)
        for u in sorted(unresolved):
            (warnings if u in proposals else errors).append(
                f"missing:{u} нет в {os.path.basename(fpath)}" + (" — есть в x-missing-proposals (предложение B2)" if u in proposals else " и нет в x-missing-proposals"))
        texts = [("offering_summary", (m.get("offering_summary") or {}).get("text")),
                 ("value_proposition.core", ((vp.get("core") or {}).get("text")))]
        texts += [(f"value_theme {t['id']}", t.get("theme")) for t in pos.get("value_themes", [])]
        check_never(texts, pats, os.path.basename(path), errors)
    else:
        warnings.append("facts.yaml по proof_ref не найден — fact:/missing: не сверены (ожидается сбор фактов B2)")
        info["facts_file"] = None
    info["unresolved_missing"] = sorted(unresolved)
    return errors, warnings, info


def semantic_hierarchy(path, h):
    errors, warnings, info = [], [], {}
    secs = sorted(h.get("sections", []), key=lambda s: s.get("order", 0))
    orders = [s.get("order") for s in secs]
    if len(orders) != len(set(orders)):
        errors.append("повторяется order в sections")
    if secs and secs[0].get("section_role") != "hero":
        errors.append(f"первая секция — {secs[0].get('section_role')}, а должна быть hero")
    pillars = {p["id"]: p for p in h.get("pillars", [])}
    carried = set()
    for s in secs:
        for c in s.get("carries", []) or []:
            if c != "core" and c not in pillars:
                errors.append(f"секция {s.get('order')} ({s.get('section_role')}): несёт неизвестную опору «{c}»")
            carried.add(c)
    for pid in pillars:
        if pid not in carried:
            errors.append(f"опора «{pid}» не несётся ни одной секцией")
    if secs and "core" not in (secs[0].get("carries") or []):
        errors.append("hero не несёт главное сообщение (carries: [core, …])")
    aw = (h.get("page") or {}).get("awareness")
    ha = (h.get("core_message") or {}).get("hero_approach")
    if aw and ha and HERO_BY_AWARENESS.get(aw) != ha:
        warnings.append(f"hero_approach «{ha}» при уровне «{aw}» (ожидается «{HERO_BY_AWARENESS.get(aw)}») — нужно обоснование в notes")
    info["sections"] = len(secs)
    info["pillars"] = len(pillars)

    mref = h.get("meaning_ref")
    if not mref:
        warnings.append("нет meaning_ref — ссылки на ценности и возражения не сверены")
        return errors, warnings, info
    mpath = os.path.normpath(os.path.join(os.path.dirname(path), mref))
    if not os.path.exists(mpath):
        errors.append(f"meaning_ref не найден: {mref}")
        return errors, warnings, info
    m = load(mpath)
    themes = {t["id"] for t in m["positioning"]["value_themes"]}
    objs = {o["id"]: o for o in m.get("objections", [])}
    for t in (h.get("core_message") or {}).get("value_theme_refs", []):
        if t not in themes:
            errors.append(f"core_message: ценность «{t}» не найдена в {os.path.basename(mpath)}")
    for p in pillars.values():
        for t in p.get("value_theme_refs", []):
            if t not in themes:
                errors.append(f"опора {p['id']}: ценность «{t}» не найдена в meaning")
        for o in p.get("objection_ids", []) or []:
            if o not in objs:
                errors.append(f"опора {p['id']}: возражение «{o}» не найдено в meaning")
    final_order = next((s["order"] for s in secs if s.get("section_role") == "final-cta"), None)
    covered_before_final = set()
    for s in secs:
        for o in s.get("objection_ids", []) or []:
            if o not in objs:
                errors.append(f"секция {s.get('order')}: возражение «{o}» не найдено в meaning")
            if final_order is None or s["order"] < final_order:
                covered_before_final.add(o)
    seg = (h.get("page") or {}).get("segment_ref")
    primary = next((a["id"] for a in m["audience"] if a.get("primary")), None)
    seg = seg or primary
    for o in objs.values():
        segs = o.get("segment_ids") or [primary]
        if o.get("severity") == "blocker" and seg in segs and o["id"] not in covered_before_final:
            errors.append(f"возражение-блокер «{o['id']}» не закрыто ни одной секцией до final-cta")
    fx = facts_index(mpath, m)
    proofs = []
    walk_proof_ids(h, proofs)
    if fx:
        fids, mids, pats, fpath = fx
        proposals = {x.get("id") for x in (m.get("x-missing-proposals") or []) if isinstance(x, dict)}
        for where, pid in proofs:
            kind, _, pid_ = pid.partition(":")
            if kind == "fact" and pid_ not in fids:
                errors.append(f"{where}: fact:{pid_} нет в {os.path.basename(fpath)}")
            if kind == "missing" and pid_ not in mids and pid_ not in proposals:
                errors.append(f"{where}: missing:{pid_} нет ни в facts.yaml, ни в x-missing-proposals meaning")
        texts = [("core_message", (h.get("core_message") or {}).get("text"))]
        texts += [(f"pillar {p['id']}", p.get("message")) for p in pillars.values()]
        texts += [(f"section {s.get('order')}", s.get("message")) for s in secs]
        check_never(texts, pats, os.path.basename(path), errors)
    info["proof_refs"] = len(proofs)
    return errors, warnings, info


def run_negative(vm, vh, meanings, hierarchies):
    """Отрицательные случаи: каждый обязан дать хотя бы одну ошибку (схемы или смысла)."""
    results = []
    if meanings:
        mpath, m = meanings[0]

        def mcase(name, mutate):
            d = copy.deepcopy(m)
            mutate(d)
            errs = schema_errors(vm, d) + semantic_meaning(mpath, d)[0]
            results.append((name, bool(errs), errs[:1]))

        mcase("два основных сегмента", lambda d: d["audience"].append(dict(copy.deepcopy(d["audience"][0]), id="seg-dup-x")))
        mcase("допущение без вопроса", lambda d: d["awareness"].__setitem__("basis", {"kind": "assumption", "question_id": "q-nope"}))
        mcase("ссылка на несуществующую альтернативу", lambda d: d["positioning"]["unique_attributes"][0]["versus"].append("alt-ghost"))
        mcase("возражение answered без доказательства и снятия риска",
              lambda d: d["objections"][0].update(status="answered", proof_ids=[], risk_reversal_ids=[]))
        mcase("дата без кавычек (объект даты YAML)", lambda d: d.__setitem__("date", __import__("datetime").date(2026, 9, 24)))
        mcase("свойство has-proof без proof_ids", lambda d: d["positioning"]["unique_attributes"][0].update(proof_status="has-proof", proof_ids=[]))
        mcase("11 вопросов заказчику", lambda d: d.__setitem__("open_questions", [
            {"id": f"q-x{i}", "q": "?", "why": "-", "default": "-", "affects": ["audience"]} for i in range(11)]))
    kv = next(((p, m) for p, m in meanings if os.path.basename(p) == "meaning-kvarts.yaml"), None)
    if kv:
        p, m = kv

        def kv_case(d):
            d["value_proposition"]["core"]["text"] = "Читать вечером без усталости глаз, не настраивая свет"
        d = copy.deepcopy(m)
        kv_case(d)
        errs = semantic_meaning(p, d)[0]
        results.append(("«Кварц»: обещание про глаза в core (урок аудита)", bool(errs), errs[:1]))
    if hierarchies:
        hpath, h = hierarchies[0]

        def hcase(name, mutate):
            d = copy.deepcopy(h)
            mutate(d)
            errs = schema_errors(vh, d) + semantic_hierarchy(hpath, d)[0]
            results.append((name, bool(errs), errs[:1]))

        hcase("две опоры вместо 3–5", lambda d: d.__setitem__("pillars", d["pillars"][:2]))
        hcase("первая секция не hero", lambda d: [s.update(order=99) for s in d["sections"] if s["section_role"] == "hero"])
        hcase("опора без секции", lambda d: d["pillars"].append({"id": "pl-orphan", "message": "x", "value_theme_refs": d["pillars"][0]["value_theme_refs"], "proof_status": "missing", "proof_ids": ["missing:legal-details"]}) if len(d["pillars"]) < 5 else d["pillars"].__setitem__(4, {"id": "pl-orphan", "message": "x", "value_theme_refs": d["pillars"][0]["value_theme_refs"], "proof_status": "missing"}))
        hcase("неизвестное возражение в секции", lambda d: d["sections"][1].setdefault("objection_ids", []).append("obj-ghost"))
        hcase("section_role вне словаря", lambda d: d["sections"][1].update(section_role="testimonial-wall"))

        def drop_blockers(d):
            for s in d["sections"]:
                s["objection_ids"] = []
        hcase("блокеры не закрыты до final-cta", drop_blockers)
    return results


def main():
    quiet = "--quiet" in sys.argv
    neg = "--no-negative" not in sys.argv
    total_err = 0
    ms = load(os.path.join(SM, "meaning.schema.yaml"))
    hs = load(os.path.join(SM, "message-hierarchy.schema.yaml"))
    for name, s in (("meaning.schema.yaml", ms), ("message-hierarchy.schema.yaml", hs)):
        Draft202012Validator.check_schema(s)
        print(f"[схема] {name}: метасхема 2020-12 — OK")
    vm, vh = Draft202012Validator(ms), Draft202012Validator(hs)
    meanings, hierarchies = [], []
    for p in sorted(glob.glob(os.path.join(EX, "meaning-*.yaml"))):
        d = load(p)
        meanings.append((p, d))
        se = schema_errors(vm, d)
        e, w, info = semantic_meaning(p, d)
        total_err += len(se) + len(e)
        print(f"\n[meaning] {os.path.basename(p)}: схема — {len(se)} ошибок; смысл — {len(e)} ошибок, {len(w)} предупр.")
        print(f"  basis: {info['basis_kinds']}; вопросов: {info['questions']} (приоритет 1: {info['questions_p1']}); "
              f"ссылок на факты: {info['proof_refs']}; facts: {info['facts_file']}")
        if info["unresolved_missing"]:
            print(f"  missing вне facts.yaml: {', '.join(info['unresolved_missing'])}")
        for x in se + e:
            print("  ОШИБКА:", x)
        if not quiet:
            for x in w:
                print("  предупреждение:", x)
    for p in sorted(glob.glob(os.path.join(EX, "hierarchy-*.yaml"))):
        d = load(p)
        hierarchies.append((p, d))
        se = schema_errors(vh, d)
        e, w, info = semantic_hierarchy(p, d)
        total_err += len(se) + len(e)
        print(f"\n[hierarchy] {os.path.basename(p)}: схема — {len(se)} ошибок; смысл — {len(e)} ошибок, {len(w)} предупр.; "
              f"секций {info.get('sections')}, опор {info.get('pillars')}, ссылок на факты {info.get('proof_refs')}")
        for x in se + e:
            print("  ОШИБКА:", x)
        if not quiet:
            for x in w:
                print("  предупреждение:", x)
    if neg:
        print("\n[отрицательные случаи]")
        res = run_negative(vm, vh, meanings, hierarchies)
        caught = sum(1 for _, ok, _ in res if ok)
        for name, ok, first in res:
            print(f"  {'пойман' if ok else 'НЕ ПОЙМАН'}: {name}" + (f" → {first[0][:120]}" if ok and first else ""))
        print(f"  итого: {caught} из {len(res)}")
        if caught != len(res):
            total_err += len(res) - caught
    print(f"\nИТОГ: ошибок {total_err}")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
