#!/usr/bin/env python3
"""fixture_gen — пересборка фикстур `scripts/tests/fixtures/`, в которых лежат файлы, собранные утилитами скилла.

Такая фикстура держит вывод утилит: производные ДС (`ds_build build`), манифест готовности (`ready build`), вход холста
(`canvas_input build`), copy deck, прошедший `copydeck check --promote` и `approve`, правки `replace` по точному тексту
примера базы. Когда меняется формат этих утилит или примеров баз, фикстура пересобирается рецептом, а не правится
руками: иначе правки `replace` не найдут свой текст, а самопроверки аудита потеряют посеянный дефект. Список фикстур,
рецепты и файлы, которые рецепт пишет (`owns`), — `scripts/maint/data/fixtures.yaml`; там же дата сборок (`today`): от
неё зависят сроки фактов, записи проверок и одобрение, и повтор сборки даёт те же байты.

Рецепты пишут во временную копию папки фикстур, поэтому фикстура, собранная раньше в том же вызове, служит входом
следующей (`after`). `build` переносит в фикстуры только файлы из `owns`: новые и изменённые пишет, лишние в папке,
которой рецепт владеет целиком, убирает; свои файлы фикстуры вне `owns` не трогает. `build --check` ничего не пишет —
сравнивает байт в байт и печатает расхождения.

    python3 .claude/skills/design-deep-dive/scripts/maint/fixture_gen.py list
    python3 .claude/skills/design-deep-dive/scripts/maint/fixture_gen.py build ИМЯ… | --all [--check] [--fixtures DIR]
    python3 .claude/skills/design-deep-dive/scripts/maint/fixture_gen.py --selftest

`--fixtures DIR` — другая папка фикстур (самопроверка, пробы). Утилиты скилла запускаются Python окружения
(`kbpaths.python()`), временные сборки — во временной папке (`TMPDIR`); сети рецепты не зовут. Код выхода: 0 — собрано
или совпало; 1 — `--check` нашёл расхождение; 2 — ошибка вызова, данных, фикстуры или утилиты.
"""
from __future__ import annotations

import argparse
import contextlib
import difflib
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import kbpaths  # noqa: E402

kbpaths.use("tests")
import fixture_project  # noqa: E402

DATA = kbpaths.data("maint", "fixtures.yaml")
FIXTURES = fixture_project.FIXTURES
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DIFF_LINES = 30


class GenError(RuntimeError):
    """Ошибка данных, фикстуры или утилиты (код выхода 2)."""


@dataclass
class Ctx:
    fixtures: Path      # временная копия папки фикстур: рецепты пишут сюда
    today: str


# ─────────────────────────────── общее ───────────────────────────────

class Dumper(yaml.SafeDumper):
    """Строки манифестов: длинные многострочные — блоком «|», прочие с переводом строки или ведущим пробелом — в кавычках."""


def _str(d, s):
    if "\n" in s.rstrip("\n") and (len(s) > 160 or s.count("\n") > 2):
        return d.represent_scalar("tag:yaml.org,2002:str", s, style="|")
    if "\n" in s or s.startswith(" "):
        return d.represent_scalar("tag:yaml.org,2002:str", s, style='"')
    return d.represent_scalar("tag:yaml.org,2002:str", s)


Dumper.add_representer(str, _str)


def dump_manifest(path: Path, head: str, m: dict):
    body = yaml.dump(m, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=120, default_flow_style=None)
    text = head + body
    if yaml.safe_load(text) != m:
        raise GenError(f"{path}: разбор манифеста не равен замыслу")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(domain: str, tool: str, *args):
    """Утилита скилла Python окружения; код 0 или 1 (находки) — норма, прочее — ошибка рецепта."""
    cmd = [kbpaths.python(), str(kbpaths.scripts(domain, tool)), *map(str, args)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode not in (0, 1):
        raise GenError(f"{domain}/{tool} {' '.join(map(str, args))}: код {r.returncode}\n{r.stdout[-2000:]}\n"
                       f"{r.stderr[-2000:]}")
    return r


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def reset(d: Path):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)


def R(find, to, count=None):
    e = {"find": find, "to": to}
    if count:
        e["count"] = count
    return e


# ─────────────────────────────── рецепты ───────────────────────────────

def recipe_ds_derived(ctx: Ctx, spec: dict):
    """Производные ДС: сборка фикстуры, `ds_build build`, файлы `owns` — из собранного проекта."""
    name = spec["name"]
    with tempfile.TemporaryDirectory(prefix=f"fixture_gen-{name}-") as td:
        b = fixture_project.build(name, Path(td) / "root", fixtures=ctx.fixtures)
        run("project", "ds_build.py", "build", b.slug, "--repo", b.root)
        for rel in spec["owns"]:
            if not rel.startswith("files/"):
                raise GenError(f"{name}: owns «{rel}» — файл проекта, путь начинается с files/")
            src = b.project / rel[len("files/"):]
            if not src.is_file():
                raise GenError(f"{name}: ds_build не собрал {rel[len('files/'):]}")
            dst = ctx.fixtures / name / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)


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

PACKAGE_LANDING_HEAD = """\
# Фикстура package-landing — иллюстрация для самопроверок scripts/project/ready.py и design_audit.py: лендинг promo
# фикстуры input-landing, приведённый к раскладке проекта для структурного аудита. Ссылки брифа, смысла, иерархий,
# голоса и планов ведут в файлы проекта, а не в примеры базы; главная — план в работе (proposed) без copy deck;
# страница «спасибо» — план примера lead-services-otves (approved) и copy deck, собранный правкой из примера copy deck
# text по слотам этого плана (тексты — черновик агента, assumed; ссылок на факты нет — демо-факт в закрытом copy deck
# сеет package-landing-defects), свой файл — каркас плана ассетов страницы «спасибо» (plan_to_assets.py build, draft).
# design_audit check — 0 error; ready build → check — 0.
# Формат манифеста — докстринг fixture_project.py.
"""


def recipe_package_landing(ctx: Ctx, spec: dict):
    """Манифест лендинга: copy deck «спасибо» — правка хвоста примера text по его точному тексту на текст SPASIBO."""
    case = kbpaths.kb("text", "10-templates-recipes", "examples", "ru-otves-case.yaml").read_text(encoding="utf-8")
    anchor = "  notes: >-\n"
    if anchor not in case:
        raise GenError("пример text ru-otves-case.yaml: нет строки «  notes: >-» — начала хвоста copy deck")
    tail = case[case.index(anchor):]
    m = {
        "example": True,
        "description": "лендинг promo для манифеста готовности и аудита: ссылки файлов — по раскладке проекта, страница "
                       "«спасибо» с планом и copy deck, сошедшимися по слотам",
        "project": "otves-remont-nn",
        "extends": ["input-landing"],
        "layers": [
            {"kb": {"site/promo/plans/spasibo.yaml":
                    "site/10-playbooks-contracts/examples/lead-services-otves/plans/spasibo.yaml",
                    "site/promo/copy/spasibo.yaml": "text/10-templates-recipes/examples/ru-otves-case.yaml"}},
            {"drop": ["site/promo/copy/home.yaml"]},
            {"files": "files"},
            {"replace": {
                "site/promo/site-brief.yaml": [
                    R("  facts_ref: ../../../../text/02-strategy-messaging/examples/facts-service-renovation.yaml\n",
                      "  facts_ref: ../../facts.yaml\n"),
                    R("  proof_ref: ../../../../text/02-strategy-messaging/examples/facts-service-renovation.yaml\n",
                      "  proof_ref: ../../facts.yaml\n")],
                "site/promo/meaning.yaml": [R('proof_ref: "facts-service-renovation.yaml"\n',
                                              'proof_ref: "../../facts.yaml"\n')],
                "site/promo/hierarchy/home-product-aware.yaml": [R("meaning_ref: meaning-otves.yaml\n",
                                                                   "meaning_ref: ../meaning.yaml\n")],
                "site/promo/hierarchy/home-problem-aware.yaml": [R("meaning_ref: meaning-otves.yaml\n",
                                                                   "meaning_ref: ../meaning.yaml\n")],
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
                    R("  voice_ref: ../../05-voice-editorial/examples/voice-otves-warm.yaml\n",
                      "  voice_ref: ../../../voice.yaml\n"),
                    R("  facts_ref: ../../02-strategy-messaging/examples/facts-service-renovation.yaml\n",
                      "  facts_ref: ../../../facts.yaml\n"),
                    R("  meaning_ref: ../../02-strategy-messaging/examples/meaning-otves.yaml\n",
                      "  meaning_ref: ../meaning.yaml\n"),
                    R(tail, SPASIBO)],
            }},
        ],
    }
    dump_manifest(ctx.fixtures / spec["name"] / "manifest.yaml", PACKAGE_LANDING_HEAD, m)


LANDING_DEFECTS_HEAD = """\
# Фикстура package-landing-defects — иллюстрация: лендинг promo фикстуры package-landing (0 error у design_audit) и
# посеянные дефекты проекта otves-remont-nn — вход проверки сценария «пакет» (ready build → design_audit). Дефект —
# правило реестра .claude/skills/design-audit/references/rules.md — место:
#   R-SURF-004   screens/promo/map.md — у поверхности рода landing есть папка screens/promo/
#   R-SURF-001   site/old-promo/ — папка слоя страницы у slug, которого нет в surface.md
#   R-STRUCT-006 design/system.tokens.json — алиас {primitive.color.neutral.950} ведёт в несуществующий токен
#   R-REF-001    site/promo/site-brief.yaml — brand.ref ведёт в несуществующий design/brand-old.yaml
#   R-REF-003    site/promo/copy/spasibo.yaml — слот confirmation/reschedule, которого нет в плане spasibo
#   R-COV-002    site/promo/copy/spasibo.yaml — у текстового слота footer/privacy-label утверждённого плана нет текста
#   R-COV-003    site/promo/plans/spasibo.yaml — слот данных footer/company ведёт в fact:legal-details, которого нет
#   R-FRESH-006  design/promo/ready.yaml — манифест собран на основе до посевов и отстал от источников
#   R-MAT-008    design/promo/assets/logo.svg — файл ассета слота header-logo при плане ассетов spasibo в draft
#   R-COV-007    voice.yaml — канал product-ui при поверхности рода app без профиля голоса продукта
#   R-DEBT-002   site/promo/copy/spasibo.yaml — демо-факт company-since-2014 в закрытом copy deck (approved); у основы
#                в copy deck ссылок на факты нет
# У основы — та же находка R-COV-007 в voice.yaml другим условием: канала product-ui нет; посев — канал есть, профиля
# голоса продукта нет. copy deck страницы spasibo заменён целиком: он прошёл copydeck.py check --update --promote и
# approve (записи проверок lint и claims с text_hash, approval страницы) уже с посевами R-REF-003, R-COV-002 и
# R-DEBT-002.
# Манифест готовности не пересобирать перед аудитом: иначе он совпадёт с источниками. Формат — докстринг
# fixture_project.py.
"""

MAP_MD = """---
surface: promo
status: draft
---

# map

> Иллюстрация: свод карты экранов у лендинга `promo` — посеянный дефект фикстуры package-landing-defects (R-SURF-004):
> у поверхности рода landing экранов нет, их место занимает слой страницы site/promo/ того же проекта.
"""

OLD_PROMO_MD = """# old-promo

> Иллюстрация: папка слоя страницы поверхности, которой нет в реестре `surface.md`, — посеянный дефект фикстуры
> package-landing-defects (R-SURF-001).
"""

LOGO = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 32" role="img" aria-label="Отвес">'
        '<title>Отвес — иллюстрация фикстуры</title><rect width="120" height="32" fill="#0f172a"/>'
        '<text x="8" y="22" fill="#ffffff" font-size="16">Отвес</text></svg>\n')

LANDING_TOKENS = {
    "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
    "$description": "Иллюстрация: токены ДС лендинга «Отвес» фикстуры package-landing-defects — посеянный дефект: алиас "
                    "color.text.default ведёт в несуществующий токен primitive.color.neutral.950 (R-STRUCT-006).",
    "example": True,
    "primitive": {"color": {"$type": "color",
                            "neutral": {"0": {"$value": {"colorSpace": "srgb", "components": [1.0, 1.0, 1.0],
                                                         "hex": "#ffffff"}},
                                        "900": {"$value": {"colorSpace": "srgb",
                                                           "components": [0.0588, 0.0902, 0.1647], "hex": "#0f172a"}}}}},
    "color": {"$type": "color",
              "bg": {"canvas": {"$value": "{primitive.color.neutral.0}"}},
              "text": {"default": {"$value": "{primitive.color.neutral.950}"}}},
    "space": {"$type": "dimension", "4": {"$value": {"value": 16, "unit": "px"}},
              "8": {"$value": {"value": 32, "unit": "px"}}},
    "breakpoint": {"$type": "dimension", "md": {"$value": {"value": 40, "unit": "rem"}},
                   "lg": {"$value": {"value": 60, "unit": "rem"}}},
    "size": {"$type": "dimension", "panel": {"sidebar": {"$value": {"value": 16, "unit": "rem"}}}},
}


def _cut_slot(text: str, slot_id: str) -> str:
    m = re.search(r"(      - slot_id: " + re.escape(slot_id) + r"\n(?:        .*\n)+)", text)
    if not m:
        raise GenError(f"copy deck основы: нет слота {slot_id}")
    return m.group(1)


def recipe_landing_defects(ctx: Ctx, spec: dict):
    """Лендинг с посевами: манифест готовности основы, свои файлы дефектов, copy deck «спасибо» после check и approve."""
    L = ctx.fixtures / spec["name"]
    reset(L)
    files = L / "files"
    with tempfile.TemporaryDirectory(prefix="fixture_gen-landing-") as td:
        b = fixture_project.build("package-landing", Path(td) / "root", fixtures=ctx.fixtures)
        proj = b.project
        run("project", "ready.py", "build", b.slug, "promo", "--repo", b.root, "--today", ctx.today)
        ready = (proj / "design/promo/ready.yaml").read_text(encoding="utf-8")
        lines = ready.splitlines(keepends=True)
        i = next(k for k, x in enumerate(lines) if x.startswith("surface:"))
        lines.insert(i, "example: true   # пометка иллюстрации фикстуры: манифест собран на чистой основе "
                        "package-landing\n")
        (files / "design/promo").mkdir(parents=True)
        (files / "design/promo/ready.yaml").write_text("".join(lines), encoding="utf-8")
        deck = (proj / "site/promo/copy/spasibo.yaml").read_text(encoding="utf-8")
    (files / "screens/promo").mkdir(parents=True)
    (files / "screens/promo/map.md").write_text(MAP_MD, encoding="utf-8")
    (files / "site/old-promo").mkdir(parents=True)
    (files / "site/old-promo/README.md").write_text(OLD_PROMO_MD, encoding="utf-8")
    (files / "design").mkdir(parents=True, exist_ok=True)
    (files / "design/system.tokens.json").write_text(json.dumps(LANDING_TOKENS, ensure_ascii=False, indent=2) + "\n",
                                                     encoding="utf-8")
    (files / "design/promo/assets").mkdir(parents=True)
    (files / "design/promo/assets/logo.svg").write_text(LOGO, encoding="utf-8")
    (files / "design/promo/assets/manifest.yaml").write_text(f"""\
# Манифест ассетов поверхности promo — иллюстрация фикстуры package-landing-defects: посеянный дефект R-MAT-008 —
# файл сгенерированного логотипа лежит, а план ассетов страницы spasibo ещё draft (генерация — только после
# status: approved и approval плана).
example: true
assets:
  - slot: header-logo
    file: logo.svg
    role: informational
    license: права у заказчика по договору (демо)
    origin: генерация по плану ассетов spasibo; исходник — у дизайнера (демо)
    ai: true
    sha256: {sha(LOGO)}
    status: draft
""", encoding="utf-8")
    privacy = _cut_slot(deck, "privacy-label")
    nexts = _cut_slot(deck, "next-steps")
    extra = nexts + """      - slot_id: reschedule
        slot_type: body
        variants:
        - {id: a, text: 'Если планы изменились — позвоните, перенесём замер', status: assumed, source: ai-self}
        chosen: a
        fact_ids: []
        claim_flags: []
"""
    # R-DEBT-002: у основы в copy deck ссылок на факты нет — посев ставит демо-факт в мета страницы до закрытия
    meta = [("      description: 'Заявка на замер принята. Студия ремонта «Отвес», Нижний Новгород.'\n",
             "      description: 'Заявка на замер принята. Ремонтируем квартиры в Нижнем Новгороде с 2014 года.'\n"),
            ("      og_description: 'Прораб позвонит и договорится о дне замера.'\n      fact_ids: []\n",
             "      og_description: 'Прораб позвонит и договорится о дне замера.'\n      fact_ids: [company-since-2014]\n")]
    seeded = deck.replace(privacy, "").replace(nexts, extra)
    for find, to in meta:
        if seeded.count(find) != 1:
            raise GenError(f"copy deck основы: строка мета не найдена ровно один раз: {find.strip()}")
        seeded = seeded.replace(find, to)
    with tempfile.TemporaryDirectory(prefix="fixture_gen-deck-") as td:
        b = fixture_project.build("package-landing", Path(td) / "root", fixtures=ctx.fixtures)
        cdir = b.project / "site/promo/copy"
        d1, d2, d3 = cdir / "_d1.yaml", cdir / "_d2.yaml", cdir / "_d3.yaml"
        d1.write_text(seeded, encoding="utf-8")
        run("text", "copydeck.py", "check", d1, "--facts", b.project / "facts.yaml", "--today", ctx.today,
            "--update", d2, "--promote", "--quiet")
        r = run("text", "copydeck.py", "approve", d2, "--page", "spasibo", "--by", "владелец продукта (демо)",
                "--at", ctx.today, "-o", d3)
        if not d3.is_file():
            raise GenError(f"copydeck approve не записал copy deck:\n{r.stdout}\n{r.stderr}")
        approved = d3.read_text(encoding="utf-8")
    if not ("status: approved" in approved and "reschedule" in approved and "privacy-label" not in approved
            and "company-since-2014" in approved and "company-since-2014" not in deck):
        raise GenError("copy deck после approve: посевы R-REF-003, R-COV-002, R-DEBT-002 не на месте")
    m = {
        "example": True,
        "description": "лендинг promo с посеянными дефектами слоёв страницы и дизайна для проверки design_audit и ready",
        "project": "otves-remont-nn",
        "extends": ["package-landing"],
        "layers": [
            {"files": "files"},
            {"replace": {
                "site/promo/site-brief.yaml": [
                    {"find": "brand:\n  ref: ../../design/brand.yaml\n", "to": "brand:\n  ref: ../../design/brand-old.yaml\n"}],
                "site/promo/plans/spasibo.yaml": [
                    {"find": "      fact: missing:legal-details\n", "to": "      fact: fact:legal-details\n"}],
                "voice.yaml": [
                    {"find": "    - {surface: marketing-site, voice: brand}\n",
                     "to": "    - {surface: marketing-site, voice: brand}\n"
                           "    - {surface: product-ui, voice: product, note: \"кабинет клиента — голос продукта\"}\n"}],
                "site/promo/copy/spasibo.yaml": [{"find": deck, "to": approved}],
            }},
        ],
    }
    dump_manifest(L / "manifest.yaml", LANDING_DEFECTS_HEAD, m)


CABINET_DEFECTS_HEAD = """\
# Фикстура package-cabinet-defects — иллюстрация: кабинет office фикстуры package-cabinet (0 error у design_audit),
# вход холста этапа mockup, собранный canvas_input на этой основе (файлы входа — с пометками иллюстрации, отпечатки в
# INPUT.md — их), и посеянные дефекты проекта otves-office — вход проверки сценария «пакет». Дефект — правило — место:
#   R-COV-005    design/system.yaml — у типа ui:Pagination stable-экрана requests-list нет компонента ДС (снят ключ)
#   R-FRESH-001  design/system.tokens.json — значение primitive.color.accent.700 изменено без пересборки производных
#   R-FRESH-003  design/office/input/copy.md — файл входа правлен руками после сборки
# Правки токенов и карты решений сделаны после сборки входа — вход устарел (R-FRESH-002, warning). Формат —
# докстринг fixture_project.py.
"""

MARK_MD = ("<!-- Иллюстрация: вход холста фикстуры package-cabinet-defects, собранный canvas_input на основе "
           "package-cabinet. -->\n")


def recipe_cabinet_defects(ctx: Ctx, spec: dict):
    """Кабинет с посевами: вход холста mockup основы с пометками иллюстрации, правка copy.md после сборки."""
    C = ctx.fixtures / spec["name"]
    reset(C)
    cfiles = C / "files"
    with tempfile.TemporaryDirectory(prefix="fixture_gen-cabinet-") as td:
        b = fixture_project.build("package-cabinet", Path(td) / "root", fixtures=ctx.fixtures)
        run("project", "canvas_input.py", "build", b.slug, "office", "--stage", "mockup", "--repo", b.root,
            "--today", ctx.today)
        inp = b.project / "design/office/input"
        built = {p.relative_to(inp).as_posix(): p.read_text(encoding="utf-8") for p in sorted(inp.rglob("*"))
                 if p.is_file()}
        tokens_c = (b.project / "design/system.tokens.json").read_text(encoding="utf-8")
        system_c = (b.project / "design/system.yaml").read_text(encoding="utf-8")
    if "INPUT.md" not in built:
        raise GenError("canvas_input build не записал INPUT.md")
    out = {}
    for name, text in built.items():
        if name == "INPUT.md":
            continue
        if name.endswith(".md"):
            out[name] = MARK_MD + text
        elif name.endswith(".yaml"):
            lines = text.splitlines(keepends=True)
            k = next(i for i, x in enumerate(lines) if not x.startswith("#"))
            lines.insert(k, "example: true\n")
            out[name] = "".join(lines)
        else:
            if json.loads(text).get("example") is not True:
                raise GenError(f"вход кабинета: {name} без example: true")
            out[name] = text
    edited = "copy.md"
    fm_text = built["INPUT.md"]
    for name, text in out.items():
        if name == edited:
            continue
        old = sha(built[name])
        if fm_text.count(old) != 1:
            raise GenError(f"INPUT.md: отпечаток {name} не найден ровно один раз")
        fm_text = fm_text.replace(old, sha(text))
    fm_text = fm_text.replace("---\n", "---\n# Иллюстрация: манифест входа фикстуры package-cabinet-defects; отпечатки "
                                       "файлов — с пометками иллюстрации.\n", 1)
    lines = out[edited].splitlines(keepends=True)
    k = next(i for i, x in enumerate(lines) if x.startswith("|") and "approved" in x)
    lines[k] = lines[k].replace("approved", "approved (правка руками после сборки)", 1)
    out[edited] = "".join(lines)
    for name, text in out.items():
        p = cfiles / "design/office/input" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    (cfiles / "design/office/input/INPUT.md").write_text(fm_text, encoding="utf-8")
    pag = "  Pagination: {component: Pagination}\n"
    hexv = '[0.1137, 0.3059, 0.8471], "hex": "#1d4ed8"'
    if system_c.count(pag) != 1 or tokens_c.count(hexv) != 1:
        raise GenError("основа package-cabinet: нет строки Pagination в system.yaml или значения акцента в токенах")
    m = {
        "example": True,
        "description": "кабинет office с посеянными дефектами ДС и входа холста для проверки design_audit",
        "project": "otves-office",
        "extends": ["package-cabinet"],
        "layers": [
            {"files": "files"},
            {"replace": {
                "design/system.yaml": [{"find": pag, "to": ""}],
                "design/system.tokens.json": [{"find": hexv, "to": '[0.1176, 0.251, 0.6863], "hex": "#1e40af"'}],
            }},
        ],
    }
    dump_manifest(C / "manifest.yaml", CABINET_DEFECTS_HEAD, m)


BOTH_DEFECTS_HEAD = """\
# Фикстура package-defects — иллюстрация: вход проверки сценария «пакет» — два демо-проекта с посеянными дефектами:
# лендинг otves-remont-nn (фикстура package-landing-defects) и кабинет otves-office (package-cabinet-defects). Ключ
# дефектов — шапки манифестов этих фикстур; design_audit check по каждому проекту находит свои. Формат — докстринг
# fixture_project.py.
"""


def recipe_both_defects(ctx: Ctx, spec: dict):
    """Оба проекта с посевами: манифест из двух extends."""
    D = ctx.fixtures / spec["name"]
    reset(D)
    dump_manifest(D / "manifest.yaml", BOTH_DEFECTS_HEAD, {
        "example": True, "description": "два проекта с посеянными дефектами: лендинг и кабинет",
        "project": "otves-remont-nn", "extends": ["package-landing-defects", "package-cabinet-defects"], "layers": []})


RECIPES = {
    "ds-derived": recipe_ds_derived,
    "package-landing": recipe_package_landing,
    "landing-defects": recipe_landing_defects,
    "cabinet-defects": recipe_cabinet_defects,
    "both-defects": recipe_both_defects,
}


# ─────────────────────────────── данные и сверка ───────────────────────────────

def load_data(path: Path = DATA) -> dict:
    d = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(d, dict) or not DATE.match(str(d.get("today", ""))) or not isinstance(d.get("fixtures"), list):
        raise GenError(f"{path}: нужны today (ГГГГ-ММ-ДД) и список fixtures")
    seen = []
    for f in d["fixtures"]:
        if not isinstance(f, dict) or not f.get("name") or f.get("recipe") not in RECIPES:
            raise GenError(f"{path}: у фикстуры name и recipe из {', '.join(RECIPES)}: {f}")
        if not isinstance(f.get("owns"), list) or not f["owns"]:
            raise GenError(f"{path}: {f['name']}: owns — непустой список путей")
        for a in f.get("after") or []:
            if a not in seen:
                raise GenError(f"{path}: {f['name']}: after «{a}» — не раньше в списке")
        if f["name"] in seen:
            raise GenError(f"{path}: фикстура {f['name']} дважды")
        seen.append(f["name"])
    return d


def owned(folder: Path, owns: list[str]) -> dict[str, Path]:
    """Файлы рецепта в папке фикстуры: {путь от папки: файл}."""
    out = {}
    for o in owns:
        base = folder if o in (".", "") else folder / o
        if base.is_file():
            out[o] = base
        elif base.is_dir():
            for f in sorted(base.rglob("*")):
                if f.is_file() and "__pycache__" not in f.parts:
                    out[f.relative_to(folder).as_posix()] = f
    return out


def compare(gen: Path, real: Path, owns: list[str]) -> list[tuple[str, str]]:
    """Расхождения собранного и фикстуры: [(вид, путь)] — «расходится», «нет в фикстуре», «лишний в фикстуре»."""
    g, r = owned(gen, owns), owned(real, owns)
    out = []
    for k in sorted(set(g) | set(r)):
        if k not in r:
            out.append(("нет в фикстуре", k))
        elif k not in g:
            out.append(("лишний в фикстуре", k))
        elif g[k].read_bytes() != r[k].read_bytes():
            out.append(("расходится", k))
    return out


def text_diff(a: Path, b: Path, name: str) -> list[str]:
    try:
        x, y = a.read_text(encoding="utf-8").splitlines(), b.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return ["    (двоичный файл)"]
    lines = list(difflib.unified_diff(y, x, f"фикстура/{name}", f"сборка/{name}", lineterm="", n=1))
    more = len(lines) - DIFF_LINES
    return ["    " + ln for ln in lines[:DIFF_LINES]] + ([f"    … ещё строк диффа: {more}"] if more > 0 else [])


def sync(gen: Path, real: Path, diffs: list[tuple[str, str]]) -> tuple[int, int]:
    wrote = removed = 0
    for kind, k in diffs:
        target = real / k
        if kind == "лишний в фикстуре":
            target.unlink()
            removed += 1
            parent = target.parent
            while parent != real and parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(gen / k, target)
            wrote += 1
    return wrote, removed


def select(data: dict, names: list[str], all_: bool) -> list[dict]:
    known = [f["name"] for f in data["fixtures"]]
    unknown = [n for n in names if n not in known]
    if unknown:
        raise GenError(f"нет рецепта для {', '.join(unknown)} (есть: {', '.join(known)})")
    return [f for f in data["fixtures"] if all_ or f["name"] in names]


def build(names: list[str], all_: bool, check: bool, fixtures: Path = FIXTURES, data: dict | None = None) -> int:
    data = data or load_data()
    specs = select(data, names, all_)
    if not specs:
        raise GenError("назовите фикстуры или --all")
    fixtures = Path(fixtures).resolve()
    status = 0
    with tempfile.TemporaryDirectory(prefix="fixture_gen-") as td:
        work = Path(td) / "fixtures"
        shutil.copytree(fixtures, work, ignore=shutil.ignore_patterns("__pycache__"))
        ctx = Ctx(fixtures=work, today=str(data["today"]))
        for spec in specs:
            RECIPES[spec["recipe"]](ctx, spec)
        for spec in specs:
            name = spec["name"]
            diffs = compare(work / name, fixtures / name, spec["owns"])
            n = len(owned(work / name, spec["owns"]))
            if not diffs:
                print(f"{name}: {'совпадает' if check else 'без изменений'} (файлов {n})")
                continue
            if check:
                status = 1
                print(f"{name}: РАСХОДИТСЯ — {len(diffs)} из {n} (пересобрать: fixture_gen.py build {name})")
                for kind, k in diffs:
                    print(f"  {kind}: {k}")
                    if kind == "расходится":
                        print("\n".join(text_diff(work / name / k, fixtures / name / k, k)))
            else:
                wrote, removed = sync(work / name, fixtures / name, diffs)
                print(f"{name}: записано {wrote}, убрано {removed} (файлов {n})")
                for kind, k in diffs:
                    print(f"  {kind}: {k}")
    return status


# ─────────────────────────────── самопроверка ───────────────────────────────

def selftest() -> int:
    """Данные и сверка на копии фикстур: сборка, повтор без изменений, ручная правка и удалённый файл — расхождение с
    именем файла, свои файлы вне owns не трогаются. Рецепты с утилитами copy deck и входа холста гоняет --check всех."""
    ok = fail = 0

    def ok_if(name, cond):
        nonlocal ok, fail
        print(("OK   " if cond else "FAIL ") + name)
        ok, fail = ok + bool(cond), fail + (not cond)

    def quiet(fn, *a, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                rc = fn(*a, **kw)
            except GenError as e:
                print(e)
                rc = 2
        return rc, buf.getvalue()

    data = load_data()
    ok_if("данные: рецепт у каждой фикстуры, after — раньше в списке", all(f["recipe"] in RECIPES
                                                                           for f in data["fixtures"]))
    ok_if("данные: каждая фикстура списка есть в папке фикстур",
          all((FIXTURES / f["name"] / "manifest.yaml").is_file() for f in data["fixtures"]))
    names = ["cabinet-ds", "package-landing"]
    with tempfile.TemporaryDirectory(prefix="fixture_gen-selftest-") as td:
        A = Path(td) / "fixtures"
        shutil.copytree(FIXTURES, A, ignore=shutil.ignore_patterns("__pycache__"))
        own = A / "package-landing" / "files" / "design" / "promo" / "assets" / "plans" / "spasibo.yaml"
        own_bytes = own.read_bytes()
        rc, _ = quiet(build, names, False, False, A, data)
        rc2, out2 = quiet(build, names, False, True, A, data)
        ok_if("build, затем --check — совпадает", rc == 0 and rc2 == 0 and "РАСХОДИТСЯ" not in out2)
        man = A / "package-landing" / "manifest.yaml"
        man.write_text(man.read_text(encoding="utf-8") + "# правка руками\n", encoding="utf-8")
        derived = A / "cabinet-ds" / "files" / "design" / "system.tokens.css"
        derived.unlink()
        rc3, out3 = quiet(build, names, False, True, A, data)
        ok_if("ручная правка манифеста — расхождение с именем файла и диффом",
              rc3 == 1 and "расходится: manifest.yaml" in out3 and "+# правка руками" not in out3
              and "-# правка руками" in out3)
        ok_if("удалённый производный файл — «нет в фикстуре»", "нет в фикстуре: files/design/system.tokens.css" in out3)
        rc4, _ = quiet(build, names, False, False, A, data)
        rc5, out5 = quiet(build, names, False, True, A, data)
        ok_if("build восстанавливает, повторный --check — совпадает", rc4 == 0 and rc5 == 0 and derived.is_file())
        ok_if("свой файл фикстуры вне owns не тронут", own.read_bytes() == own_bytes)
        rc6, out6 = quiet(build, ["no-such-fixture"], False, True, A, data)
        ok_if("неизвестная фикстура — ошибка вызова", rc6 == 2 and "нет рецепта" in out6)
    print(f"selftest: {ok} OK, {fail} FAIL")
    return 0 if not fail else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 epilog=__doc__.split("\n", 2)[2], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true", help="самопроверка на копии фикстур, без сети")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list", help="фикстуры, рецепты и файлы, которые рецепт пишет")
    b = sub.add_parser("build", help="пересобрать фикстуры (с --check — только сверить)")
    b.add_argument("names", nargs="*", help="имена фикстур из data/fixtures.yaml")
    b.add_argument("--all", action="store_true", help="все фикстуры списка по порядку")
    b.add_argument("--check", action="store_true", help="собрать во временную папку и сверить байт в байт, не писать")
    b.add_argument("--fixtures", type=Path, default=FIXTURES, help="папка фикстур (по умолчанию scripts/tests/fixtures)")
    a = ap.parse_args(argv)
    try:
        if a.selftest:
            return selftest()
        if a.cmd == "list":
            data = load_data()
            print(f"дата сборок: {data['today']}")
            for f in data["fixtures"]:
                after = f" (после {', '.join(f['after'])})" if f.get("after") else ""
                print(f"{f['name']}: {f['recipe']}{after} — {f.get('what', '')}")
                print(f"  пишет: {', '.join(f['owns'])}")
            return 0
        if a.cmd == "build":
            return build(a.names, a.all, a.check, a.fixtures)
        ap.print_help()
        return 2
    except (GenError, fixture_project.FixtureError, OSError) as e:
        print(f"fixture_gen: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
