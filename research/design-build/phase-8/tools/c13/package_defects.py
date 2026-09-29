"""Генератор фикстур с посеянными дефектами: package-landing-defects, package-cabinet-defects, package-defects."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

SK = Path("/home/mm/git/stit-core/business-strategy-template/.claude/skills/design-deep-dive")
FIX = SK / "scripts/tests/fixtures"
PY = "/home/mm/.cache/design-deep-dive/venv/bin/python"
TODAY = "2026-09-29"
sys.path.insert(0, str(SK / "scripts/tests"))
sys.path.insert(0, str(SK / "scripts/lib"))
import fixture_project  # noqa: E402


def run(*args):
    r = subprocess.run([PY, *map(str, args)], capture_output=True, text=True)
    if r.returncode not in (0, 1):
        raise SystemExit(f"{args}: {r.returncode}\n{r.stdout}\n{r.stderr}")
    return r


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def str_style(d, s):
    if "\n" in s.rstrip("\n") and (len(s) > 160 or s.count("\n") > 2):
        return d.represent_scalar("tag:yaml.org,2002:str", s, style="|")
    if "\n" in s or s.endswith("\n") or s.startswith(" "):
        return d.represent_scalar("tag:yaml.org,2002:str", s, style='"')
    return d.represent_scalar("tag:yaml.org,2002:str", s)


yaml.add_representer(str, str_style, Dumper=yaml.SafeDumper)


def dump_manifest(path, head, m):
    body = yaml.dump(m, Dumper=yaml.SafeDumper, allow_unicode=True, sort_keys=False, width=120,
                     default_flow_style=None)
    text = head + body
    assert yaml.safe_load(text) == m
    path.write_text(text, encoding="utf-8")


def reset(d):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)


# ------------------------------------------------------------------ лендинг
L = FIX / "package-landing-defects"
reset(L)
files = L / "files"
with tempfile.TemporaryDirectory() as td:
    b = fixture_project.build("package-landing", Path(td) / "root")
    proj = b.project
    run(SK / "scripts/project/ready.py", "build", "otves-remont-nn", "promo", "--repo", b.root, "--today", TODAY)
    ready = (proj / "design/promo/ready.yaml").read_text(encoding="utf-8")
    lines = ready.splitlines(keepends=True)
    i = next(k for k, x in enumerate(lines) if x.startswith("surface:"))
    lines.insert(i, "example: true   # пометка иллюстрации фикстуры: манифест собран на чистой основе package-landing\n")
    (files / "design/promo").mkdir(parents=True)
    (files / "design/promo/ready.yaml").write_text("".join(lines), encoding="utf-8")
    brief = (proj / "site/promo/site-brief.yaml").read_text(encoding="utf-8")
    deck = (proj / "site/promo/copy/spasibo.yaml").read_text(encoding="utf-8")
    plan = (proj / "site/promo/plans/spasibo.yaml").read_text(encoding="utf-8")
    voice = (proj / "voice.yaml").read_text(encoding="utf-8")

(files / "screens/promo").mkdir(parents=True)
(files / "screens/promo/map.md").write_text("""---
surface: promo
status: draft
---

# map

> Иллюстрация: свод карты экранов у лендинга `promo` — посеянный дефект фикстуры package-landing-defects (R-SURF-004):
> у поверхности рода landing экранов нет, их место занимает слой страницы site/promo/ того же проекта.
""", encoding="utf-8")
(files / "site/old-promo").mkdir(parents=True)
(files / "site/old-promo/README.md").write_text("""# old-promo

> Иллюстрация: папка слоя страницы поверхности, которой нет в реестре `surface.md`, — посеянный дефект фикстуры
> package-landing-defects (R-SURF-001).
""", encoding="utf-8")
tokens = {
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
(files / "design").mkdir(parents=True, exist_ok=True)
(files / "design/system.tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + "\n",
                                                 encoding="utf-8")
logo = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 32" role="img" aria-label="Отвес">'
        '<title>Отвес — иллюстрация фикстуры</title><rect width="120" height="32" fill="#0f172a"/>'
        '<text x="8" y="22" fill="#ffffff" font-size="16">Отвес</text></svg>\n')
(files / "design/promo/assets").mkdir(parents=True)
(files / "design/promo/assets/logo.svg").write_text(logo, encoding="utf-8")
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
    sha256: {sha(logo)}
    status: draft
""", encoding="utf-8")


def cut_slot(text, slot_id):
    m = re.search(r"(      - slot_id: " + re.escape(slot_id) + r"\n(?:        .*\n)+)", text)
    assert m, slot_id
    return m.group(1)


privacy = cut_slot(deck, "privacy-label")
nexts = cut_slot(deck, "next-steps")
extra = nexts + """      - slot_id: reschedule
        slot_type: body
        variants:
        - {id: a, text: 'Если планы изменились — позвоните, перенесём замер', status: assumed, source: ai-self}
        chosen: a
        fact_ids: []
        claim_flags: []
"""
with tempfile.TemporaryDirectory() as td:
    b = fixture_project.build("package-landing", Path(td) / "root")
    cdir = b.project / "site/promo/copy"
    d1, d2, d3 = cdir / "_d1.yaml", cdir / "_d2.yaml", cdir / "_d3.yaml"
    d1.write_text(deck.replace(privacy, "").replace(nexts, extra), encoding="utf-8")
    run(SK / "scripts/text/copydeck.py", "check", d1, "--facts", b.project / "facts.yaml", "--today", TODAY,
        "--update", d2, "--promote", "--quiet")
    r = run(SK / "scripts/text/copydeck.py", "approve", d2, "--page", "spasibo", "--by", "владелец продукта (демо)",
            "-o", d3)
    assert d3.is_file(), r.stdout + r.stderr
    approved = d3.read_text(encoding="utf-8")
assert "status: approved" in approved and "reschedule" in approved and "privacy-label" not in approved
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
head = """\
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
#   R-DEBT-002   site/promo/copy/spasibo.yaml — демо-факт company-since-2014 в закрытом copy deck (approved)
# copy deck страницы spasibo заменён целиком: он прошёл copydeck.py check --update --promote и approve (записи проверок
# lint и claims с text_hash, approval страницы) уже с посевами R-REF-003 и R-COV-002.
# Манифест готовности не пересобирать перед аудитом: иначе он совпадёт с источниками. Формат — докстринг
# fixture_project.py.
"""
dump_manifest(L / "manifest.yaml", head, m)

# ------------------------------------------------------------------ кабинет
C = FIX / "package-cabinet-defects"
reset(C)
cfiles = C / "files"
MARK_MD = "<!-- Иллюстрация: вход холста фикстуры package-cabinet-defects, собранный canvas_input на основе package-cabinet. -->\n"
with tempfile.TemporaryDirectory() as td:
    b = fixture_project.build("package-cabinet", Path(td) / "root")
    r = run(SK / "scripts/project/canvas_input.py", "build", "otves-office", "office", "--stage", "mockup",
            "--repo", b.root, "--today", TODAY)
    inp = b.project / "design/office/input"
    built = {p.relative_to(inp).as_posix(): p.read_text(encoding="utf-8") for p in sorted(inp.rglob("*"))
             if p.is_file()}
    tokens_c = (b.project / "design/system.tokens.json").read_text(encoding="utf-8")
    system_c = (b.project / "design/system.yaml").read_text(encoding="utf-8")
print("вход кабинета:", sorted(built))
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
        data = json.loads(text)
        assert data.get("example") is True, name
        out[name] = text
EDITED = "copy.md"
fm_text = built["INPUT.md"]
for name, text in out.items():
    if name == EDITED:
        continue
    old = sha(built[name])
    assert fm_text.count(old) == 1, name
    fm_text = fm_text.replace(old, sha(text))
fm_text = fm_text.replace("---\n", "---\n# Иллюстрация: манифест входа фикстуры package-cabinet-defects; отпечатки файлов — с пометками иллюстрации.\n", 1)
edited = out[EDITED]
lines = [x for x in edited.splitlines(keepends=True)]
k = next(i for i, x in enumerate(lines) if x.startswith("|") and "approved" in x)
lines[k] = lines[k].replace("approved", "approved (правка руками после сборки)", 1)
out[EDITED] = "".join(lines)
for name, text in out.items():
    p = cfiles / "design/office/input" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
(cfiles / "design/office/input/INPUT.md").write_text(fm_text, encoding="utf-8")
pag = "  Pagination: {component: Pagination}\n"
assert system_c.count(pag) == 1
hexv = '[0.1137, 0.3059, 0.8471], "hex": "#1d4ed8"'
assert tokens_c.count(hexv) == 1
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
head = """\
# Фикстура package-cabinet-defects — иллюстрация: кабинет office фикстуры package-cabinet (0 error у design_audit),
# вход холста этапа mockup, собранный canvas_input на этой основе (файлы входа — с пометками иллюстрации, отпечатки в
# INPUT.md — их), и посеянные дефекты проекта otves-office — вход проверки сценария «пакет». Дефект — правило — место:
#   R-COV-005    design/system.yaml — у типа ui:Pagination stable-экрана requests-list нет компонента ДС (снят ключ)
#   R-FRESH-001  design/system.tokens.json — значение primitive.color.accent.700 изменено без пересборки производных
#   R-FRESH-003  design/office/input/copy.md — файл входа правлен руками после сборки
# Правки токенов и карты решений сделаны после сборки входа — вход устарел (R-FRESH-002, warning). Формат —
# докстринг fixture_project.py.
"""
dump_manifest(C / "manifest.yaml", head, m)

# ------------------------------------------------------------------ оба проекта
D = FIX / "package-defects"
reset(D)
head = """\
# Фикстура package-defects — иллюстрация: вход проверки сценария «пакет» — два демо-проекта с посеянными дефектами:
# лендинг otves-remont-nn (фикстура package-landing-defects) и кабинет otves-office (package-cabinet-defects). Ключ
# дефектов — шапки манифестов этих фикстур; design_audit check по каждому проекту находит свои. Формат — докстринг
# fixture_project.py.
"""
dump_manifest(D / "manifest.yaml", head, {"example": True,
                                          "description": "два проекта с посеянными дефектами: лендинг и кабинет",
                                          "project": "otves-remont-nn",
                                          "extends": ["package-landing-defects", "package-cabinet-defects"],
                                          "layers": []})
print("ok")
