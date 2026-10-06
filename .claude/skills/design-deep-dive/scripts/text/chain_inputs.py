#!/usr/bin/env python3
"""chain_inputs.py — сверка смысла до текстов и вход судьи текстов: проекции смысла, иерархий и copy deck.

Зависимости: Python 3.10+ и PyYAML. Сеть и модели не нужны: код собирает входы и считает баллы по ответам, тексты
пишет и оценивает агент сессии (судья — по kb/common/judge.md).

Команды (python3 scripts/text/chain_inputs.py <команда> …):
  meaning-claims  --meaning M [--hierarchy H …] [--brief B] -o OUT.yaml    смысл и иерархии → copy deck для сверки
                                                                          copydeck.py claims (этап meaning)
  judge-input     --deck D --page P --criterion ID [--scope …] [--hierarchy H] [--meaning M] [--lang ru] [-o OUT]
                                                                          вход судьи текстов по критерию рубрики
  judge-score     --answers A.json [A2.json …] [-o OUT]                    баллы по ответам судьи (формула рубрики)
  --selftest                                                               проекция смысла и подсчёт баллов
meaning-claims берёт утверждения страницы: из смысла — ядро ценностного предложения, сводку предложения, оффер,
уникальные свойства, снятие риска; из иерархий — главное сообщение, первый экран, опоры и сообщения секций. Возражения,
страхи и альтернативы — слова аудитории, а не утверждения страницы: возражения смысла и секции иерархии с ролью
problem, objections, comparison в проекцию не идут (их число — в выводе). Тип страницы проекции — primary_page_type
брифа (--brief), без брифа — landing-lead-services; у иерархии со своим page.page_type — он. Проекция помечена
projection: meaning: это не страница, поэтому места фактов (use фактов — на каких страницах и в каких секциях факт
уместен) copydeck.py claims на ней не сверяет. Сверка смысла — сигнал до текстов; ворота
текстов — copydeck.py check. Факты — meaning.proof_ref; рубрика — 09-ai-generation-evaluation/copy-rubric.yaml.
"""
import argparse
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
RUBRIC = P("09-ai-generation-evaluation", "copy-rubric.yaml")
TODAY = datetime.date.today().isoformat()
GEO_PASS_IF_NO = {"COPY-GEO-10", "COPY-GEO-18", "COPY-GEO-26"}
AUDIENCE_ROLES = ("problem", "objections", "comparison")   # секции иерархии о страхах, возражениях и альтернативах аудитории


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


# ---------------------------------------------------------------- meaning-claims (этап meaning)
def _slot(slot_id, slot_type, text, fact_ids=(), missing_ids=(), note=""):
    return {"slot_id": slot_id, "slot_type": slot_type,
            "variants": [{"id": "a", "text": text, "status": "draft", "source": "ai-self"}], "chosen": "a",
            "fact_ids": list(dict.fromkeys(fact_ids)), "missing_ids": list(dict.fromkeys(missing_ids)),
            "claim_flags": [], "notes": note}


DEFAULT_PAGE_TYPE = "landing-lead-services"


def brief_page_type(brief_path):
    """primary_page_type брифа сайта — тип страницы проекции смысла; брифа или поля нет — None."""
    if not brief_path:
        return None
    b = load(brief_path)
    pt = b.get("primary_page_type") if isinstance(b, dict) else None
    return str(pt) if pt else None


def cmd_meaning_claims(a):
    m = load(a.meaning)
    ptype = brief_page_type(getattr(a, "brief", None)) or DEFAULT_PAGE_TYPE
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
    n_obj = len(m.get("objections") or [])   # возражения — слова аудитории: ответы на них сверяет copy deck
    n_aud = 0
    rr = m.get("risk_reversal") or []
    if rr:
        secs.append({"section_id": "m-risk", "section_role": "guarantee", "slots": [
            _slot(r["id"], "guarantee-text", r["summary"], *split_ids([r.get("fact_id")]), note=f"risk_reversal.{r['id']}")
            for r in rr]})
    pages.append({"page_id": "meaning", "page_type": ptype, "sections": secs})
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
            if sc.get("section_role") in AUDIENCE_ROLES:
                n_aud += 1
                continue
            ff, mm = split_ids(sc.get("proof_ids"))
            hs.append({"section_id": f"s{sc['order']:02d}-{sc['section_role']}", "section_role": sc["section_role"],
                       "slots": [_slot("message", "subheadline" if sc["section_role"] == "hero" else "body", sc.get("message", ""),
                                       ff, mm, f"sections[{sc['order']}].message")]})
        pages.append({"page_id": re.sub(r"[^a-z0-9-]", "-", h.get("id", os.path.basename(hp).split(".")[0])),
                      "page_type": (h.get("page") or {}).get("page_type") or ptype, "sections": hs})
    deck = {"copy_deck": {"version": 1, "date": TODAY, "site": m.get("site", "site"), "lang": "ru",
                          "projection": "meaning",   # не страница: copydeck.py claims не сверяет места фактов (use)
                          "facts_ref": rel(fpath, out_dir) if fpath else "",
                          "notes": "Проекция смысла и иерархий для сверки до текста (chain_inputs.py meaning-claims): "
                                   "это не тексты страницы, а внутренние формулировки; путь слота → поле смысла в notes. "
                                   "Возражения, страхи и альтернативы — слова аудитории: в проекцию не идут.",
                          "pages": pages}}
    dump(deck, a.o)
    print(f"meaning-claims: страниц {len(pages)}, слотов {sum(len(s['slots']) for p in pages for s in p['sections'])} → {a.o}; "
          f"тип страницы проекции — {ptype}; "
          f"не сверяются (слова аудитории): возражений {n_obj}, секций иерархий {n_aud} ({', '.join(AUDIENCE_ROLES)})", file=sys.stderr)


# ---------------------------------------------------------------- judge-input / judge-score (P7)
def iter_slots(page):
    for s in page["sections"]:
        for sl in s["slots"]:
            yield s, sl


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


# ---------------------------------------------------------------- selftest
def selftest():
    import contextlib
    import io
    import tempfile
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
    m = {"site": "t", "proof_ref": "facts.yaml",
         "offering_summary": {"text": "Ремонт квартир под ключ; замер бесплатно"},
         "value_proposition": {"core": {"text": "Срок и смета в договоре"}},
         "offer": {"summary": "Скидка 10 % на работы до 31 октября", "proof_ids": ["fact:promo"]},
         "positioning": {"alternatives": [{"id": "alt-crew", "name": "Бригада по знакомству", "limits": "нет договора и гарантии"}],
                         "unique_attributes": [{"id": "attr-years", "attribute": "12 лет в городе", "proof_ids": ["fact:since-2014"]}]},
         "objections": [{"id": "obj-price", "text": "Дорого: частники берут меньше", "answer": "Цена — от 9 800 ₽ за м²", "proof_ids": ["fact:price"]}],
         "risk_reversal": [{"id": "rr-free", "summary": "Замер бесплатно в пределах города", "fact_id": "fact:free"}]}
    h = {"id": "h-test", "core_message": {"text": "Ремонт под присмотром прораба"}, "first_screen": {"what": "ремонт квартир"},
         "pillars": [{"id": "pl-contract", "message": "Договор с гарантией"}],
         "sections": [{"order": 1, "section_role": "hero", "message": "Замер бесплатно"},
                      {"order": 2, "section_role": "problem", "message": "Смета растёт, мастера ждут друг друга"},
                      {"order": 3, "section_role": "comparison", "message": "Бригада без договора — спросить не с кого"},
                      {"order": 4, "section_role": "objections", "message": "Дорого? Смета до договора"},
                      {"order": 5, "section_role": "pricing", "message": "От 9 800 ₽ за м² без материалов"}]}
    with tempfile.TemporaryDirectory() as td:
        mp, hp, op = (os.path.join(td, x) for x in ("meaning.yaml", "h.yaml", "claims.yaml"))
        dump(m, mp)
        dump(h, hp)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            cmd_meaning_claims(argparse.Namespace(meaning=mp, hierarchy=[hp], o=op))
        out = load(op)["copy_deck"]
        # смысл многостраничника: факт уместен на своей странице и в своей секции (use), проекция — не страница
        import subprocess
        bp, fp, op2, jp = (os.path.join(td, x) for x in ("site-brief.yaml", "facts.yaml", "claims-site.yaml", "claims.json"))
        dump({"primary_page_type": "home-multipage"}, bp)
        dump({"facts_version": 1, "date": "2026-09-24", "site": "t", "lang": "ru", "jurisdiction": "ru", "missing": [], "never_claim": [],
              "facts": [{"id": "promo", "kind": "promo", "claim_class": ["price-discount", "promo-deadline"],
                         "verbatim": ["Скидка 10 % на работы до 31 октября"], "canonical": "Скидка 10 % на работы до 31 октября 2026 года.",
                         "values": [{"value": 10, "unit": "%", "what": "скидка"}],
                         "source": {"type": "customer-document", "who": "заказчик", "date": "2026-09-01", "document": "prikaz.pdf",
                                    "quote": "скидка 10% на работы до 31.10.2026"},
                         "verification": {"status": "verified"}, "permission": {"status": "not-required"}, "valid": {"until": "2026-10-31"},
                         "use": {"page_types": ["service-page"], "section_roles": ["offer"]}, "lang": "ru"}]}, fp)
        with contextlib.redirect_stderr(err):
            cmd_meaning_claims(argparse.Namespace(meaning=mp, hierarchy=[], brief=bp, o=op2))
        site = load(op2)
        site_meta = (site["copy_deck"]["pages"][0]["page_type"], site["copy_deck"].get("projection"))
        use_n = []
        for marked in (True, False):   # с пометкой проекции и без неё — та же сверка тем же файлом фактов
            if not marked:
                site["copy_deck"].pop("projection")
                dump(site, op2)
            r = subprocess.run([sys.executable, os.path.join(HERE, "copydeck.py"), "claims", op2, "--facts", fp, "--today", "2026-09-24",
                                "--json", jp, "--quiet"], capture_output=True, text=True)
            found = json.load(open(jp, encoding="utf-8"))["findings"] if r.returncode in (0, 1) and os.path.exists(jp) else None
            use_n.append(None if found is None else sum(1 for f in found if f["rule"] == "COPY-F-USE"))
            if os.path.exists(jp):
                os.remove(jp)
    secs = {p["page_id"]: [s["section_id"] for s in p["sections"]] for p in out["pages"]}
    texts = {sl["variants"][0]["text"] for p in out["pages"] for s in p["sections"] for sl in s["slots"]}
    res.append(("meaning-claims: ядро, сводка предложения, оффер, свойства и снятие риска — в проекции",
                secs.get("meaning") == ["m-core", "m-offer", "m-attributes", "m-risk"] and "12 лет в городе" in texts, secs))
    res.append(("meaning-claims: возражения, страхи и альтернативы — не в проекции, их число — в выводе",
                not texts & {"Цена — от 9 800 ₽ за м²", "Дорого: частники берут меньше", "Смета растёт, мастера ждут друг друга",
                             "Бригада без договора — спросить не с кого", "Дорого? Смета до договора"}
                and "возражений 1, секций иерархий 3" in err.getvalue(), err.getvalue().strip()))
    res.append(("meaning-claims: иерархия — главное сообщение, первый экран, опоры, секции hero и pricing",
                secs.get("h-test") == ["h-core", "h-pillars", "s01-hero", "s05-pricing"], secs))
    res.append(("meaning-claims: facts_ref — от папки выхода", out["facts_ref"] == "facts.yaml", out["facts_ref"]))
    res.append(("meaning-claims: без брифа тип страницы проекции — landing-lead-services, с брифом — его primary_page_type; пометка projection",
                out["pages"][0]["page_type"] == DEFAULT_PAGE_TYPE and out.get("projection") == "meaning"
                and site_meta == ("home-multipage", "meaning"), (out["pages"][0]["page_type"], site_meta)))
    res.append(("сверка смысла многостраничника: факт с use своих страниц и секций — 0 COPY-F-USE; без пометки проекции та же сверка их даёт",
                use_n[0] == 0 and (use_n[1] or 0) >= 1, use_n))
    ok = sum(1 for r in res if r[1])
    for r in res:
        print(("OK   " if r[1] else "FAIL ") + r[0] + ("" if r[1] or len(r) < 3 else f": {r[2]}"))
    print(f"selftest: {ok} из {len(res)}")
    return 0 if ok == len(res) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("meaning-claims"); s.add_argument("--meaning", required=True); s.add_argument("--hierarchy", nargs="*"); s.add_argument("-o", required=True)
    s.add_argument("--brief", help="бриф сайта (site-brief.yaml): тип страницы проекции — его primary_page_type")
    s = sub.add_parser("judge-input")
    for k in ("--deck", "--page", "--criterion"):
        s.add_argument(k, required=True)
    s.add_argument("--scope"); s.add_argument("--hierarchy"); s.add_argument("--meaning"); s.add_argument("--lang", default="ru"); s.add_argument("-o")
    s = sub.add_parser("judge-score"); s.add_argument("--answers", nargs="+", required=True); s.add_argument("-o")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    fn = {"meaning-claims": cmd_meaning_claims, "judge-input": cmd_judge_input, "judge-score": cmd_judge_score}.get(a.cmd)
    if not fn:
        ap.print_help(sys.stderr)
        sys.exit(2)
    rc = fn(a)
    if isinstance(rc, int):
        sys.exit(rc)


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:              # текст вместо кода — ошибка входа (страницы нет в copy deck)
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            sys.exit(2)
        raise
