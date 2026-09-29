#!/usr/bin/env python3
"""check_intake.py — проверка выхода промта P1 (разбор брифа) кодом.

Промт: kb/text/09-ai-generation-evaluation/prompts/p1-brief-intake.md §4.

Запуск (Python с PyYAML):
    python3 scripts/text/check_intake.py INTAKE.yaml --brief BRIEF.txt [--json OUT] [--quiet]
    python3 scripts/text/check_intake.py --selftest

Проверки (error — нарушение правила промта; warning — эвристика или правило «по смыслу»):
  E1  YAML читается, корень intake, все поля формата P1 на месте;
  E2  каждая quote — подстрока брифа после нормализации (пробелы, кавычки, тире, регистр, ё);
  E3  в facts_from_brief нет числа вне цитаты (число из text есть в quote);
  E4  вопросов не больше 7; у каждого есть why, default, affects и priority 1–3;
  E5  id в kebab-case и уникальны (gaps, assumptions, questions, missing);
  E6  допущение kind: assumption ссылается на question_id из questions; kind: inferred — с полем from;
  E7  missing: fallback из {placeholder, omit-block, rewrite-without}; question — id вопроса или текст;
  W1  просьб к заказчику (вопросы + просьбы документов из missing, не привязанные к вопросу) больше 7;
  W2  допущение не повторено ни в going_with, ни в default его вопроса (пересечение основ слов < 0,3);
  W3  в message_to_customer нет строки «Беру по умолчанию» / «Going with» или пронумерованных вопросов больше 7;
  W4  у вопроса-факта заданы options (факты спрашивают свободным ответом — эвристика по словам «сколько», «какой»…);
  W5  never_claim_candidates пуст.
Код выхода: 0 — ошибок нет, 2 — есть ошибки, 1 — ошибка входа.
"""
import argparse
import json
import re
import sys

import yaml

FIELDS = ["lang", "page_type", "ordered", "domain", "facts_from_brief", "constraints", "gaps", "assumptions",
          "questions", "missing", "never_claim_candidates", "going_with", "message_to_customer"]
FALLBACKS = {"placeholder", "omit-block", "rewrite-without"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NUM = re.compile(r"\d+(?:[   ]\d{3})*(?:[.,]\d+)?")
FACT_Q = re.compile(r"\b(сколько|какой|какая|какие|как часто|с какого|когда|пришлите|how many|how often|which|what)\b", re.I)
STOP = {"это", "того", "чтобы", "если", "когда", "только", "страница", "клиент", "клиенты", "которые", "который"}


def norm(s):
    s = (s or "").lower().replace("ё", "е")
    s = re.sub(r"[«»“”„\"']", '"', s)
    s = re.sub(r"[‐‑‒–—−]", "-", s)
    s = re.sub(r"[  \s]+", " ", s)
    return s.strip()


def nums(s):
    return {re.sub(r"[   ]", "", m).replace(",", ".") for m in NUM.findall(s or "")}


def stems(s):
    words = re.findall(r"[a-zа-яё]{4,}", (s or "").lower())
    return {w[:5] for w in words if w not in STOP}


def check(intake_doc, brief):
    errors, warnings, info = [], [], {}
    if not isinstance(intake_doc, dict) or not isinstance(intake_doc.get("intake"), dict):
        return ["E1: корень документа — не intake"], warnings, info
    it = intake_doc["intake"]
    for f in FIELDS:
        if f not in it:
            errors.append(f"E1: нет поля {f}")
    nb = norm(brief)
    facts = it.get("facts_from_brief") or []
    for i, f in enumerate(facts):
        q = f.get("quote", "")
        if not q or norm(q) not in nb:
            errors.append(f"E2: facts_from_brief[{i}] — цитаты нет в брифе: «{q[:70]}»")
        extra = nums(f.get("text", "")) - nums(q)
        if extra:
            errors.append(f"E3: facts_from_brief[{i}] — числа вне цитаты: {sorted(extra)}")
    qs = it.get("questions") or []
    qids = {q.get("id") for q in qs}
    if len(qs) > 7:
        errors.append(f"E4: вопросов {len(qs)} > 7")
    for q in qs:
        for k in ("why", "default", "affects"):
            if not q.get(k):
                errors.append(f"E4: вопрос {q.get('id')} — нет поля {k}")
        if q.get("priority") not in (1, 2, 3):
            errors.append(f"E4: вопрос {q.get('id')} — priority не 1–3")
        if q.get("options") and FACT_Q.search(q.get("q", "")):
            warnings.append(f"W4: вопрос {q.get('id')} похож на вопрос о факте, но у него есть options")
    seen = {}
    for block in ("gaps", "assumptions", "questions", "missing"):
        for x in it.get(block) or []:
            xid = x.get("id", "")
            if not KEBAB.match(xid or ""):
                errors.append(f"E5: {block}: id «{xid}» не kebab-case")
            if xid in seen:
                errors.append(f"E5: id «{xid}» повторяется ({seen[xid]} и {block})")
            seen[xid] = block
    gw = it.get("going_with") or []
    for a in it.get("assumptions") or []:
        if a.get("kind") == "assumption":
            if a.get("question_id") not in qids:
                errors.append(f"E6: допущение {a.get('id')} — question_id «{a.get('question_id')}» нет среди вопросов")
        elif a.get("kind") == "inferred":
            if not a.get("from"):
                errors.append(f"E6: вывод {a.get('id')} — нет поля from")
        else:
            errors.append(f"E6: допущение {a.get('id')} — kind «{a.get('kind')}» не inferred/assumption")
        st = stems(a.get("text"))
        cands = [stems(g) for g in gw]
        qd = next((q.get("default", "") for q in qs if q.get("id") == a.get("question_id")), "")
        if qd:
            cands.append(stems(qd))
        best = max((len(st & c) / max(1, len(st)) for c in cands), default=0)
        if best < 0.3:
            warnings.append(f"W2: допущение {a.get('id')} не повторено в going_with / default вопроса ({best:.2f})")
    standalone = []
    for m in it.get("missing") or []:
        if m.get("fallback") not in FALLBACKS:
            errors.append(f"E7: missing {m.get('id')} — fallback «{m.get('fallback')}»")
        mq = m.get("question") or ""
        if not mq:
            errors.append(f"E7: missing {m.get('id')} — нет question")
        elif mq not in qids:
            standalone.append(m.get("id"))
    asks = len(qs) + len(standalone)
    if asks > 7:
        warnings.append(f"W1: просьб к заказчику {asks} (вопросов {len(qs)} + документов вне вопросов {len(standalone)}: "
                        f"{', '.join(standalone)}) > 7 — документы спрашивать внутри тематических вопросов (proof-intake §4)")
    msg = it.get("message_to_customer") or ""
    numbered = re.findall(r"(?m)^\s*\d+\.\s", msg)
    if len(numbered) > 7:
        warnings.append(f"W3: в сообщении {len(numbered)} пронумерованных вопросов > 7")
    if not re.search(r"(беру по умолчанию|going with)", msg, re.I):
        warnings.append("W3: в сообщении нет строки «Беру по умолчанию» / «Going with»")
    if not it.get("never_claim_candidates"):
        warnings.append("W5: never_claim_candidates пуст")
    info = {"facts_from_brief": len(facts), "questions": len(qs), "questions_p1": sum(1 for q in qs if q.get("priority") == 1),
            "assumptions": len(it.get("assumptions") or []), "missing": len(it.get("missing") or []),
            "standalone_document_asks": len(standalone), "asks_total": asks,
            "never_claim_candidates": len(it.get("never_claim_candidates") or []), "going_with": len(gw)}
    return errors, warnings, info


def selftest():
    brief = "Цена — от 9 800 ₽ за метр. Гарантия 3 года по договору."
    good = {"intake": {k: [] for k in FIELDS}}
    good["intake"].update({"lang": "ru", "page_type": "landing-lead-services", "domain": "x",
                           "message_to_customer": "1. Вопрос?\nБеру по умолчанию: x",
                           "never_claim_candidates": [{"text": "лучший"}],
                           "facts_from_brief": [{"text": "цена от 9 800 ₽", "quote": "Цена - от 9 800 ₽ за метр", "kind": "price"}],
                           "questions": [{"id": "q-a", "q": "Какой срок?", "why": "w", "default": "d", "affects": ["x"], "priority": 1, "options": []}],
                           "assumptions": [{"id": "as-a", "text": "срок в договоре", "kind": "assumption", "question_id": "q-a"}],
                           "going_with": ["срок в договоре указан"]})
    cases = []
    e, w, _ = check(good, brief)
    cases.append(("исправный intake — 0 ошибок", not e))
    import copy
    b = copy.deepcopy(good); b["intake"]["facts_from_brief"][0]["quote"] = "Цена — от 9 900 ₽"
    cases.append(("цитаты нет в брифе → E2", any(x.startswith("E2") for x in check(b, brief)[0])))
    b = copy.deepcopy(good); b["intake"]["facts_from_brief"][0]["text"] = "12 лет и цена от 9 800 ₽"
    cases.append(("число вне цитаты → E3", any(x.startswith("E3") for x in check(b, brief)[0])))
    b = copy.deepcopy(good); b["intake"]["questions"] = [dict(good["intake"]["questions"][0], id=f"q-{i}") for i in range(8)]
    b["intake"]["assumptions"] = []
    cases.append(("8 вопросов → E4", any(x.startswith("E4") for x in check(b, brief)[0])))
    b = copy.deepcopy(good); b["intake"]["assumptions"][0]["question_id"] = "q-none"
    cases.append(("допущение без вопроса → E6", any(x.startswith("E6") for x in check(b, brief)[0])))
    b = copy.deepcopy(good); b["intake"]["missing"] = [{"id": f"m-{i}", "question": "Пришлите файл", "fallback": "placeholder"} for i in range(7)]
    cases.append(("7 документов + 1 вопрос → W1", any(x.startswith("W1") for x in check(b, brief)[1])))
    b = copy.deepcopy(good); b["intake"]["missing"] = [{"id": "Bad_Id", "question": "q-a", "fallback": "none"}]
    ee = check(b, brief)[0]
    cases.append(("id не kebab и fallback вне списка → E5, E7", any(x.startswith("E5") for x in ee) and any(x.startswith("E7") for x in ee)))
    ok = sum(1 for _, r in cases if r)
    for name, r in cases:
        print(("OK   " if r else "FAIL ") + name)
    print(f"selftest: {ok} из {len(cases)}")
    return 0 if ok == len(cases) else 2


def main():
    ap = argparse.ArgumentParser(description="Проверка выхода P1 (intake) кодом")
    ap.add_argument("intake", nargs="?")
    ap.add_argument("--brief")
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.intake or not a.brief:
        ap.error("нужны INTAKE и --brief")
    try:
        doc = yaml.safe_load(open(a.intake, encoding="utf-8"))
        brief = open(a.brief, encoding="utf-8").read()
    except Exception as ex:  # noqa: BLE001
        print(f"ошибка входа: {ex}", file=sys.stderr)
        sys.exit(1)
    e, w, info = check(doc, brief)
    if not a.quiet:
        for x in e:
            print("ОШИБКА:", x)
        for x in w:
            print("предупреждение:", x)
        print("сводка:", json.dumps(info, ensure_ascii=False))
        print(f"ИТОГ: ошибок {len(e)}, предупреждений {len(w)}")
    if a.json:
        json.dump({"tool": "check_intake.py", "version": "1.0", "input": a.intake, "errors": e, "warnings": w, "info": info},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(2 if e else 0)


if __name__ == "__main__":
    main()
