"""Генератор манифеста фикстуры package-landing: длинная правка copy deck — точным текстом примера базы.

Запуск: python3 research/design-build/phase-8/tools/c13/package_landing.py (первым — до package_defects.py)."""
import sys
from pathlib import Path
import yaml

SKILL = Path(__file__).resolve().parents[5] / ".claude/skills/design-deep-dive"
KB = SKILL / "kb"
OUT = SKILL / "scripts/tests/fixtures/package-landing"
case = (KB / "text/10-templates-recipes/examples/ru-otves-case.yaml").read_text(encoding="utf-8")
i = case.index("  notes: >-\n")
tail = case[i:]

SPASIBO = """\
  notes: >-
    Страница «спасибо» после заявки на замер: статус заявки первым, затем кто и когда свяжется, одно следующее
    действие. Реквизиты продавца — пробел legal-details: в подвале — имя студии и город до ответа заказчика.
  pages:
  - page_id: spasibo
    page_type: thank-you-page
    status: draft
    awareness: product-aware
    primary_action: Вызвать замерщика
    cta_primary: spasibo/header/cta-label
    promise:
      from: spasibo/confirmation/title
      basis: 'подтверждение заявки — первое, что видит человек после формы'
    meta:
      title: 'Заявка на замер принята — студия «Отвес»'
      description: 'Заявка на замер принята. Студия ремонта «Отвес», Нижний Новгород.'
      og_title: 'Заявка на замер принята'
      og_description: 'Прораб позвонит и договорится о дне замера.'
      fact_ids: []
      notes: 'Служебная страница: не индексируется (seo.indexable плана — false).'
    sections:
    - section_id: header
      section_role: header
      message: 'Куда вернуться и как связаться'
      slots:
      - slot_id: cta-label
        slot_type: cta-label
        variants:
        - {id: a, text: 'Вызвать замерщика', status: assumed, source: ai-self}
        chosen: a
        fact_ids: []
        claim_flags: []
    - section_id: confirmation
      section_role: confirmation
      message: 'Заявка дошла; прораб позвонит и договорится о замере'
      question: 'Заявка дошла? Что дальше?'
      slots:
      - slot_id: title
        slot_type: form-success
        variants:
        - {id: a, text: 'Заявка на замер принята', status: assumed, source: ai-self}
        chosen: a
        fact_ids: []
        claim_flags: []
      - slot_id: next-steps
        slot_type: form-next-steps
        variants:
        - {id: a, text: 'Прораб позвонит и договорится о дне замера', status: assumed, source: ai-self}
        chosen: a
        fact_ids: []
        claim_flags: []
    - section_id: footer
      section_role: footer
      message: 'Кто продавец и где документы'
      slots:
      - slot_id: legal
        slot_type: footer-legal
        variants:
        - {id: a, text: 'Студия ремонта «Отвес», Нижний Новгород', status: assumed, source: ai-self}
        chosen: a
        fact_ids: []
        claim_flags: []
      - slot_id: privacy-label
        slot_type: nav-label
        variants:
        - {id: a, text: 'Политика обработки персональных данных', status: assumed, source: ai-self}
        chosen: a
        fact_ids: []
        claim_flags: []
"""


class Lit(str):
    pass


def str_style(d, s):
    if "\n" in s.rstrip("\n") and (len(s) > 160 or s.count("\n") > 2):
        return d.represent_scalar("tag:yaml.org,2002:str", s, style="|")
    if "\n" in s:
        return d.represent_scalar("tag:yaml.org,2002:str", s, style='"')
    if s.endswith("\n") or s.startswith(" "):
        return d.represent_scalar("tag:yaml.org,2002:str", s, style='"')
    return d.represent_scalar("tag:yaml.org,2002:str", s)


yaml.add_representer(str, str_style, Dumper=yaml.SafeDumper)
yaml.add_representer(Lit, str_style, Dumper=yaml.SafeDumper)


def R(find, to, count=None):
    e = {"find": find, "to": to}
    if count:
        e["count"] = count
    return e


m = {
    "example": True,
    "description": "лендинг promo для манифеста готовности и аудита: ссылки файлов — по раскладке проекта, страница "
                   "«спасибо» с планом и copy deck, сошедшимися по слотам",
    "project": "otves-remont-nn",
    "extends": ["input-landing"],
    "layers": [
        {"kb": {"site/promo/plans/spasibo.yaml": "site/10-playbooks-contracts/examples/lead-services-otves/plans/spasibo.yaml",
                "site/promo/copy/spasibo.yaml": "text/10-templates-recipes/examples/ru-otves-case.yaml"}},
        {"drop": ["site/promo/copy/home.yaml"]},
        {"files": "files"},
        {"replace": {
            "site/promo/site-brief.yaml": [
                R("  facts_ref: ../../../../text/02-strategy-messaging/examples/facts-service-renovation.yaml\n",
                  "  facts_ref: ../../facts.yaml\n"),
                R("  proof_ref: ../../../../text/02-strategy-messaging/examples/facts-service-renovation.yaml\n",
                  "  proof_ref: ../../facts.yaml\n")],
            "site/promo/meaning.yaml": [R('proof_ref: "facts-service-renovation.yaml"\n', 'proof_ref: "../../facts.yaml"\n')],
            "site/promo/hierarchy/home-product-aware.yaml": [R("meaning_ref: meaning-otves.yaml\n", "meaning_ref: ../meaning.yaml\n")],
            "site/promo/hierarchy/home-problem-aware.yaml": [R("meaning_ref: meaning-otves.yaml\n", "meaning_ref: ../meaning.yaml\n")],
            "voice.yaml": [
                R('  meaning_ref: "../../02-strategy-messaging/examples/meaning-otves.yaml"\n',
                  '  meaning_ref: "site/promo/meaning.yaml"\n'),
                R('  facts_ref: "../../02-strategy-messaging/examples/facts-service-renovation.yaml"\n',
                  '  facts_ref: "facts.yaml"\n')],
            "site/promo/plans/home.yaml": [
                R("\nstatus: approved\n", "\nstatus: proposed\n"),
                R("  facts: ../../../../../text/02-strategy-messaging/examples/facts-service-renovation.yaml\n",
                  "  facts: ../../../facts.yaml\n"),
                R("  copy_deck: ../copy/home.yaml\n", ""),
                R("  treatment: ../../../../../creative-research/99-raw/experiments/A/02-c1-check/treatments.yaml\n",
                  "  treatment: ../../../design/promo/art-direction.json\n")],
            "site/promo/plans/spasibo.yaml": [
                R("\nstatus: proposed\n", "\nstatus: approved\n"),
                R("  facts: ../../../../../text/02-strategy-messaging/examples/facts-service-renovation.yaml\n",
                  "  facts: ../../../facts.yaml\n"),
                R("  events: ../../../../07-seo-geo-performance-analytics/events.yaml\n",
                  "  events: ../../../../07-seo-geo-performance-analytics/events.yaml\n"
                  "  asset_plan: ../../../design/promo/assets/plans/spasibo.yaml\n")],
            "site/promo/copy/spasibo.yaml": [
                R("  voice_ref: ../../05-voice-editorial/examples/voice-otves-warm.yaml\n", "  voice_ref: ../../../voice.yaml\n"),
                R("  facts_ref: ../../02-strategy-messaging/examples/facts-service-renovation.yaml\n",
                  "  facts_ref: ../../../facts.yaml\n"),
                R("  meaning_ref: ../../02-strategy-messaging/examples/meaning-otves.yaml\n", "  meaning_ref: ../meaning.yaml\n"),
                R(tail, SPASIBO)],
        }},
    ],
}
head = """\
# Фикстура package-landing — иллюстрация для самопроверок scripts/project/ready.py и design_audit.py: лендинг promo
# фикстуры input-landing, приведённый к раскладке проекта для структурного аудита. Ссылки брифа, смысла, иерархий,
# голоса и планов ведут в файлы проекта, а не в примеры базы; главная — план в работе (proposed) без copy deck;
# страница «спасибо» — план примера lead-services-otves (approved) и copy deck, собранный правкой из примера copy deck
# text по слотам этого плана (тексты — черновик агента, assumed; ссылок на факты нет — демо-факт в закрытом copy deck
# сеет package-landing-defects), свой файл — каркас плана ассетов страницы «спасибо» (plan_to_assets.py build, draft).
# design_audit check — 0 error; ready build → check — 0.
# Формат манифеста — докстринг fixture_project.py.
"""
OUT.mkdir(parents=True, exist_ok=True)
body = yaml.dump(m, Dumper=yaml.SafeDumper, allow_unicode=True, sort_keys=False, width=120, default_flow_style=None)
back = yaml.safe_load(head + body)
assert back == m, "разбор манифеста не равен замыслу"
(OUT / "manifest.yaml").write_text(head + body, encoding="utf-8")
print("written", OUT / "manifest.yaml", len((head + body).splitlines()))
