#!/usr/bin/env python3
"""Ф8, зона C15 — правка kb/text/04-copy-by-block/copy-slots.yaml по месту (TR-06, TR-08, TR-58), без переформатирования.

- шапка: файл — источник правды, правится руками (Р33); ключ `build` снят; словарь — site v1;
- `site_slot: ''` у всех записей и фраза «site_slot … заполнить после S1» в `crosswalk.note` сняты (TR-08);
- роли `specs`, `audience`, `story`, `services`, `offer`, `promo`, `awards-press`, `cross-sell`, `related`, `seo-text`,
  `legal`, `confirmation`, `not-found` дописаны в `section_roles` тех типов слотов, которые несут блоки site, служащие
  этой роли (`kb/site/04-blocks/blocks.yaml`: `serves` и `slots[].slot`); запись без `section_roles` (любая роль) не
  трогается (TR-06, TR-58);
- записи слотов site без правил text: `lint_as` (ближайший тип), `rules_owner` (H, G, E), `fact_required` — класс факта
  из `blocks.yaml#text_slot_defaults`, имя и назначение — из словаря site (TR-06; 11-я — `email-sender-name`).

Запуск: python3 copy_slots_tr06.py [--write] — без ключа печатает сводку правок, с ключом пишет файл. Повторный запуск
ничего не меняет.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[5] / ".claude" / "skills" / "design-deep-dive" / "kb"
CS = ROOT / "text" / "04-copy-by-block" / "copy-slots.yaml"
VOCAB = ROOT / "site" / "02-site-types" / "vocabulary.yaml"
BLOCKS = ROOT / "site" / "04-blocks" / "blocks.yaml"

NEW_ROLES = ["specs", "audience", "story", "services", "offer", "promo", "awards-press", "cross-sell", "related",
             "seo-text", "legal", "confirmation", "not-found"]

# слот site без правил text → (lint_as, rules_owner, жанры)
LINT_AS = {
    "disclaimer": ("footer-legal", "H — 08-russian-legal-typography (оговорки у утверждений: claims-rules.yaml, 01-advertising-law-claims.md)", ["landing", "site-page"]),
    "ad-marking": ("footer-legal", "H — 08-russian-legal-typography (маркировка рекламы, 38-ФЗ ст. 18.1; строки права — site legal-requirements.yaml)", ["landing", "site-page", "email-form"]),
    "cookie-text": ("form-consent", "H — 08-russian-legal-typography (текст согласия; право — site legal-requirements.yaml)", ["landing", "site-page"]),
    "article-date": ("article-author", "G — 07-seo-geo-copy/03-geo-copy.md (дата публикации и обновления статьи)", ["article"]),
    "article-sources": ("list-item", "G — 07-seo-geo-copy/03-geo-copy.md (источники статьи)", ["article"]),
    "event-meta": ("cta-note", "E — 04-copy-by-block (строка «когда, где, формат» события)", ["landing", "site-page"]),
    "quiz-question": ("faq-q", "E — 04-copy-by-block (квиз)", ["landing", "site-page"]),
    "quiz-option": ("list-item", "E — 04-copy-by-block (квиз)", ["landing", "site-page"]),
    "result-summary": ("form-success", "E — 04-copy-by-block/04-form-emails-notifications.md (итог квиза или калькулятора)", ["landing", "site-page"]),
    "contact-info": ("footer-legal", "E — 04-copy-by-block (контакты текстом); набор телефона и адреса — typography-rules.yaml", ["landing", "site-page"]),
    "email-sender-name": ("email-subject", "E — 04-copy-by-block/04-form-emails-notifications.md §3.3 (имя отправителя)", ["email-form"]),
}

# класс факта слота, которого нет в blocks.yaml#text_slot_defaults: имя отправителя — без утверждений (04/04 §3.3)
FACT = {"email-sender-name": "never"}

HEAD_OLD = [
    "# copy-slots.yaml — правила текста по типам слотов (text-research, 04-copy-by-block, агент E, волна 2, 2026-09-24).\n",
    "# СОБИРАЕТСЯ СКРИПТОМ: python3 99-raw/experiments/E/02-copy-slots/build_copy_slots.py --lengths final\n",
    "# Руками не править — правки в 99-raw/experiments/E/02-copy-slots/src-*.yaml и crosswalk.yaml, затем пересборка.\n",
    "# Читают: J (copydeck.py validate: length.{ru,en}.{words,chars}.{min,max}, fact_required, section_roles, genre),\n",
    "# I (промты по слотам), F (образцы строк по slot_type), G (мета и FAQ — ссылкой), creative (длины строк в макете).\n",
    "# Длины — D thresholds.yaml v2 (03-corpus-measured/thresholds.yaml → genres.<жанр>.slots, 03-thresholds-by-genre.md §4; лидеры, выборка «marketing» = лендинги + страницы сайта; сообщение оркестратора 2026-09-24).\n",
]
HEAD_NEW = (
    "# copy-slots.yaml — правила текста по типам слотов: назначение, роли секций, длины RU и EN, структура, формулы,\n"
    "# запреты, роль ux и жанры для линтера, нужен ли факт, юридические правила, примеры «плохо / хорошо». Файл — источник\n"
    "# правды и правится руками; id типа слота — id слота вида text словаря site (../site/02-site-types/vocabulary.yaml).\n"
    "# Читают: copydeck.py validate (length.{ru,en}.{words,chars}.{min,max}, fact_required, section_roles, genre),\n"
    "# copy_lint.py (ux_role, genres, lint_as), промты по слотам, образцы строк голоса, длины строк в макете (creative).\n"
    "# Слот site без своих правил держит lint_as — тип, правилами которого его проверяет линтер, и rules_owner — владельца\n"
    "# правил; длины таких слотов даст замер пилотов.\n"
    "# Длины — замер корпуса: 03-corpus-measured/thresholds.yaml → genres.<жанр>.slots (03-thresholds-by-genre.md §4;\n"
    "# лидеры, выборка «marketing» = лендинги + страницы сайта).\n"
)


def q(s):
    """Строка YAML в двойных кавычках (JSON-строка — корректный скаляр YAML)."""
    return json.dumps(str(s), ensure_ascii=False)


def entry(y):
    """Запись типа слота в стиле файла: списки ролей и жанров — строкой, источники — блоком."""
    out = [f"- id: {y['id']}", f"  name: {y['name']}", f"  purpose: {q(y['purpose'])}"]
    if y.get("section_roles"):
        out.append("  section_roles: [" + ", ".join(y["section_roles"]) + "]")
    out += ["  genres: [" + ", ".join(y["genres"]) + "]", f"  genre: {y['genre']}", f"  ux_role: {y['ux_role']}",
            f"  lint_as: {y['lint_as']}", f"  rules_owner: {q(y['rules_owner'])}", f"  fact_required: {y['fact_required']}",
            "  sources:"] + [f"  - {q(s)}" for s in y["sources"]]
    return "\n".join(out) + "\n"


def roles_by_slot(blocks, text_slots):
    out = {}
    for bid, b in (blocks.get("blocks") or {}).items():
        for r in b.get("serves") or []:
            for s in b.get("slots") or []:
                if s.get("slot") in text_slots:
                    out.setdefault(s["slot"], [])
                    if r not in out[s["slot"]]:
                        out[s["slot"]].append(r)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    text = CS.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    vocab = yaml.safe_load(VOCAB.read_text(encoding="utf-8"))["namespaces"]
    blocks = yaml.safe_load(BLOCKS.read_text(encoding="utf-8"))
    slot_def = {x["id"]: x for x in vocab["slot"]["values"]}
    text_slots = {k for k, v in slot_def.items() if v.get("kind") == "text"}
    role_ids = {x["id"] for x in vocab["section_role"]["values"]}
    assert set(NEW_ROLES) <= role_ids, set(NEW_ROLES) - role_ids
    rbs = roles_by_slot(blocks, text_slots)
    defaults = blocks.get("text_slot_defaults") or {}
    by_id = {s["id"]: s for s in data["slot_types"]}
    log = []
    # шапка
    if HEAD_OLD[0] in text:
        for ln in HEAD_OLD:
            assert ln in text, ln
            text = text.replace(ln, "", 1)
        text = HEAD_NEW + text
        log.append("шапка: источник правды, словарь site")
    text2 = re.sub(r'^build: "python3 99-raw/experiments/E/02-copy-slots/build_copy_slots.py --lengths final"\n', "", text,
                   flags=re.M)
    if text2 != text:
        log.append("ключ build снят")
        text = text2
    text2 = text.replace(' Ключ — slot_type; site_slot — id слота site после S1."', ' Ключ — slot_type: id слота вида text словаря site."')
    if text2 != text:
        log.append("description: без site_slot")
        text = text2
    text2 = re.sub(r'^vocabulary: "99-raw/notes/temp-vocabulary-v0\.yaml \(63 slot_type\) \+ предложения E \(proposal: true\)"\n',
                   'vocabulary: "../site/02-site-types/vocabulary.yaml (слоты вида text; id типа слота = id слота site)"\n',
                   text, flags=re.M)
    if text2 != text:
        log.append("vocabulary: словарь site")
        text = text2
    n = len(re.findall(r"^  site_slot: ''\n", text, flags=re.M))
    if n:
        text = re.sub(r"^  site_slot: ''\n", "", text, flags=re.M)
        log.append(f"site_slot снят: {n}")
    old_note = ' site_slot (id слота blocks.yaml site) — заполнить после S1."'
    if old_note in text:
        text = text.replace(old_note, '"')
        log.append("crosswalk.note: без «заполнить после S1»")
    # роли секций
    lines = text.split("\n")
    cur = None
    added = {}
    for i, ln in enumerate(lines):
        m = re.match(r"^- id: (\S+)$", ln)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"^  section_roles: \[(.*)\]$", ln)
        if m and cur:
            have = [x.strip() for x in m.group(1).split(",") if x.strip()]
            want = [r for r in NEW_ROLES if r in rbs.get(cur, []) and r not in have]
            if want:
                lines[i] = "  section_roles: [" + ", ".join(have + want) + "]"
                added[cur] = want
    text = "\n".join(lines)
    for k, v in added.items():
        log.append(f"section_roles {k}: + {', '.join(v)}")
    # новые записи
    missing = [s for s in LINT_AS if s not in by_id]
    if missing:
        chunks = []
        for sid in missing:
            lint_as, owner, genres = LINT_AS[sid]
            base = by_id[lint_as]
            sd = slot_def[sid]
            roles = [r for r in rbs.get(sid, []) if r in role_ids]
            fact = (defaults.get(sid) or {}).get("fact") or FACT.get(sid) or base.get("fact_required") or "if-claim"
            y = {"id": sid, "name": sd["name"], "purpose": sd["def"]}
            if roles:
                y["section_roles"] = roles
            y.update({"genres": genres, "genre": genres[0], "ux_role": base.get("ux_role") or "",
                      "lint_as": lint_as, "rules_owner": owner, "fact_required": fact,
                      "sources": ["../site/02-site-types/vocabulary.yaml#slot (имя и назначение)",
                                  "../site/04-blocks/blocks.yaml#text_slot_defaults (класс факта)"]})
            chunks.append(entry(y))
            log.append(f"запись {sid}: lint_as {lint_as}, fact_required {fact}, роли {roles}")
        anchor = "\ncrosswalk:\n"
        assert anchor in text
        text = text.replace(anchor, "\n" + "".join(chunks).rstrip("\n") + anchor, 1)
    for ln in log:
        print(ln)
    if not log:
        print("правок нет")
    if a.write and log:
        CS.write_text(text, encoding="utf-8")
        yaml.safe_load(text)
        print(f"записано: {CS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
