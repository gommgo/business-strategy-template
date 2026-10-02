#!/usr/bin/env python3
"""build_text_zones — раскладка работ текстовой уборки kb/ по зонам (журнальный инструмент Ф10, стандартная библиотека).

Собирает `phase-10/text-zones/<зона>.tsv`, `_unplaced.tsv`, `_mechanics.tsv` и свод зон `_zones.tsv` из:
  - действий сверки баз с фазой «Ф10» (`phase-4/actions.tsv`, адреса и каноны — `phase-4/registry.tsv`);
  - списка упоминаний снятых утилит (`phase-9/DF9-F10-kb-mentions.tsv`);
  - таблицы прочих пунктов ниже (`EXTRA`: находки пилота, хвосты отчётов зон) — дополняется из отчётов W1;
  - счёта маркеров `tools/kbscan.py` на момент запуска.

Адрес действия разбирается так: короткие адреса «[база] NN/MM», README базы и папки, глоссарии, реестры противоречий,
id чек-листов и имена машинных файлов — в частях действия до тире; адрес после слов-отсылок («ссылкой на», «из», «по»,
«→») — цель ссылки, а не место правки. База без имени берётся из канона строки реестра, затем из её копий. Действие
без адреса с «копии — …», «ссылкой», «так же» раскладывается по колонке `copies`. Место в `99-raw` и в `PLAN.md` базы —
в `_mechanics.tsv` (закрывается снятием файлов), место вне `kb/` и неразобранный адрес — в `_unplaced.tsv`.

Запуск из корня репозитория: python3 research/design-build/phase-10/tools/build_text_zones.py [--dry]
"""
import csv
import importlib.util
import os
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
JOURNAL = HERE.parents[1]                                # research/design-build
REPO = JOURNAL.parents[1]
KB = REPO / ".claude" / "skills" / "design-deep-dive" / "kb"
OUT = HERE.parent / "text-zones"

spec = importlib.util.spec_from_file_location("kbscan", JOURNAL / "tools" / "kbscan.py")
kbscan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kbscan)

BASES = ("ui", "ux", "site", "text", "creative", "ai-media", "blender", "claude-design")
ALIAS = {b: b for b in BASES}
ALIAS["cd"] = "claude-design"
BASE_RX = r"(?:ai-media|claude-design|creative|blender|site|text|ui|ux|cd)"

# Зоны: имя → (база, папки; «.» — файлы корня базы). Раскладка — непрерывные папки под потолок 350 тыс. токенов md.
ZONES = OrderedDict([
    ("T-site-1", ("site", [".", "00-glossary", "01-foundations", "02-site-types", "03-page-structure"])),
    ("T-site-2", ("site", ["04-blocks", "05-conversion-funnels", "06-multipage-ia", "07-seo-geo-performance-analytics"])),
    ("T-site-3", ("site", ["08-legal-trust-a11y", "09-ai-generation-evaluation", "10-playbooks-contracts"])),
    ("T-text-1", ("text", [".", "00-glossary", "01-foundations", "02-strategy-messaging"])),
    ("T-text-2", ("text", ["03-corpus-measured", "04-copy-by-block", "05-voice-editorial", "06-anti-slop"])),
    ("T-text-3", ("text", ["07-seo-geo-copy", "08-russian-legal-typography", "09-ai-generation-evaluation", "10-templates-recipes"])),
    ("T-creative-1", ("creative", [".", "00-glossary", "01-creative-direction"])),
    ("T-creative-2", ("creative", ["02-references-moodboards", "03-live-sites-measured", "04-visual-language", "05-motion", "06-effects-catalog"])),
    ("T-creative-3", ("creative", ["07-stack-implementation", "08-uniqueness-anti-slop", "09-ai-execution-evaluation", "10-recipes"])),
    ("T-cd-1", ("claude-design", [".", "01-product", "02-claude-code-bridge", "03-practice-pipelines", "04-claude-code-native", "05-design-artifacts", "06-design-process"])),
    ("T-ai-media-1", ("ai-media", [".", "00-glossary", "01-web-assets-landscape"])),
    ("T-ai-media-2", ("ai-media", ["02-providers-platforms"])),
    ("T-ai-media-3", ("ai-media", ["03-image-models", "04-video-models"])),
    ("T-ai-media-4", ("ai-media", ["05-prompting", "06-art-direction-consistency"])),
    ("T-ai-media-5", ("ai-media", ["07-vector-svg-icons", "08-image-post-processing", "09-video-pipeline", "10-web-integration", "11-evaluation-qa"])),
    ("T-ai-media-6", ("ai-media", ["12-legal-provenance", "13-routing-matrix", "14-recipes", "15-tools-atlas"])),
    ("T-ui-1", ("ui", [".", "00-glossary"])),
    ("T-ui-2", ("ui", ["01-color", "02-typography"])),
    ("T-ui-3", ("ui", ["03-spacing-sizing", "04-shape-elevation", "05-layout-grid"])),
    ("T-ui-4", ("ui", ["06-components-visual", "07-iconography-imagery", "08-motion"])),
    ("T-ui-5", ("ui", ["09-design-tokens"])),
    ("T-ui-6", ("ui", ["10-design-systems-atlas", "11-styles-trends"])),
    ("T-ui-7", ("ui", ["12-ai-generated-ui", "13-evaluation-checklists", "14-recipes"])),
    ("T-ux-1", ("ux", [".", "01-foundations"])),
    ("T-ux-2", ("ux", ["02-ia-navigation", "03-layout-placement"])),
    ("T-ux-3", ("ux", ["04-components-patterns"])),
    ("T-ux-4", ("ux", ["05-flows-journeys", "06-feedback-states-motion"])),
    ("T-ux-5", ("ux", ["07-ux-writing", "08-accessibility"])),
    ("T-ux-6", ("ux", ["09-mobile", "10-design-systems-consistency", "11-ai-generated-ui"])),
    ("T-ux-7", ("ux", ["12-evaluation-checklists", "13-app-types"])),
    ("T-blender-1", ("blender", [".", "00-glossary", "01-web-3d-landscape"])),
    ("T-blender-2", ("blender", ["02-blender-workflow", "03-bpy-api"])),
    ("T-blender-3", ("blender", ["04-ai-agents-mcp", "05-modeling", "06-materials-lighting-render"])),
    ("T-blender-4", ("blender", ["07-animation", "08-export-gltf", "09-web-runtime"])),
    ("T-blender-5", ("blender", ["10-ai-3d-generation-assets", "11-evaluation-qa", "12-recipes"])),
    ("T-blender-6", ("blender", ["13-tools-atlas", "14-code-3d", "15-showcase"])),
    ("T-common-1", ("common", ["."])),                  # плюс kb/INDEX.md — последней
])

# Прочие пункты: файл от kb/ → строки. Источники: находки пилота (phase-9/pilots/FINDINGS.tsv), разделы «Для текстов»
# и «Не сделано — в Ф10» отчётов W1, §8 отчётов ДФ9 и C17, пункт «Ф10» плана сборки. Дополняется из отчётов W1.
EXTRA = [
    ("claude-design/06-design-process/07-prompt-templates.md", "F9-052: артборд направления — ширины приёмки десктопа и телефона вместо 880 × 560; числа first_viewport — диапазоном или с замером метрик шрифта (§1)"),
    ("claude-design/06-design-process/01-brief-and-questions.md", "F9-052: §5 — артборд направления по ширинам приёмки; F9-046: §5 — число направлений и границы тона ссылкой на норму creative (01/01 §6), шрифты «с кириллицей» — ссылкой на creative 04/01 §4.2"),
    ("site/03-page-structure/01-narratives-and-section-order.md", "F9-024: строки seo-landing-page (порядок секций §3, трио форм §4.2); формулировку даёт владелец нормы — без неё строка не пишется, пункт в «Не сделано»"),
    ("site/03-page-structure/02-length-goal-message-match.md", "F9-024: строки длины для seo-landing-page и portfolio-page (§1.3) — как выше"),
    ("site/03-page-structure/03-first-screen-and-mobile.md", "F9-024: строка первого экрана seo-landing-page (§1.3) — как выше"),
    ("site/04-blocks/03-slots-and-page-plan.md", "F9-026: §5, §7, §8 — ссылки на схему v0.9, `examples/page-plan-*.yaml` и `validate.py` → `schemas/page-plan.schema.json` v1, `examples/*/plans/`, `site_validate.py`"),
    ("site/07-seo-geo-performance-analytics/head-kit.yaml", "F9-020 (данные, зона кода): `home-multipage.notes` советует LocalBusiness, PL-SEO01 отклоняет — сверить с правкой `site_validate.py`"),
    ("text/02-strategy-messaging/proof-intake.md", "F9-020: вопрос почты владельца сайта для заявлений (вид company; LR-RU-13) — строкой анкеты"),
    ("creative/01-creative-direction/01-concept-and-directions.md", "F9-044: оговорка CRV-CD-11 — канон направлений может повторять форму плана; F9-046: §6.2 — одно цветовое пространство (OKLCH) и одна граница различия тона акцента"),
    ("creative/02-references-moodboards/03-moodboard-and-handoff.md", "F9-046: §1.3 — граница различия тона 10–110° против 10–60° в 01/01 §6.2: одна граница в одном пространстве, второе место — ссылкой; W1-Z8: F9-010 — число «12–18» согласовать со сбором кандидатов (§1.2: 30–60 кандидатов — другой шаг)"),
    ("ai-media/06-art-direction-consistency/01-visual-dna-from-ui.md", "F9-075: §7.3 — способ доставки зерна: слой страницы по умолчанию, впекание — только в мастер-файл"),
    ("ai-media/08-image-post-processing/03-color-tiling-depth-layers.md", "F9-075: §3 — та же строка о зерне ссылкой на 06/01 §7.3"),
    ("claude-design/06-design-process/04-checks.md", "W1-Z5: строка «подписи и alt против списка ассетов» — картинка `/_blob/<id>` находится через реестр загрузок; в командах §4 — ключ `--uploads`; порог M-BODY-16 — «абзацы внутри `main`»; D5: §3 (группа B «навигация — critical», группа C «приметы без заказа — 0 major») и §9 — по поведению `mockup_checks.py`; расхождение с ui 11/04 §1.3 о маркерах экрана — одна формулировка, второе место ссылкой"),
    ("claude-design/06-design-process/02-input-package.md", "W1-Z5: «так её читает `mockup_checks.py`» — колонки «файл», «слот», «подпись», «alt», «id загрузки»"),
    ("claude-design/06-design-process/06-test-stand.md", "W1-Z5: имена видов `desktop-…-00`, `mobile-…-00` — у собранной страницы; у копии артборда кадр назван по копии"),
    ("claude-design/05-design-artifacts/02-staying-current.md", "W1-Z8 (F9-001): §6 — строки журнала о релизах типов и снимке `snapshots/2026-10-01-types.json` (даты в таблице снимков — данные)"),
    ("claude-design/05-design-artifacts/README.md", "W1-Z8 (F9-001): таблица файлов называет только снимок 2026-09-26 — назвать действующий снимок"),
    ("claude-design/README.md", "W1-Z8 (F9-001): строка о снимке (≈ стр. 301) — действующий снимок; «Как пользоваться» — вход холста (`references/claude-design.md`, cd 06/02 §1) и этапы (`references/phases.md`); раздел «Сравнение с Kimi K3» — снять (выводы — «LLM-вёрстка 2026»)"),
    ("claude-design/05-design-artifacts/01-design-system-and-canvas-in-session.md", "W1-Z8 (F9-001): §3.1, §3.2, §8 — пересказ расходится со справкой типа: сверить с `reference_changes` снимка"),
    ("creative/06-effects-catalog/01-effects-catalog.md", "W1-Z8 (F9-155): §10.1–§10.2 — строка о загрузке кадра у приёмов (правило стоит в `effects.yaml`)"),
    ("creative/09-ai-execution-evaluation/02-motion-spec-storyboard-handoff.md", "W1-Z9: §1.3 — расхождение CRV-AL-09 (transform, clip-path, появление из 0,01) и MS-09 (только transform, translate): одна формулировка по решению владельца нормы, без решения — в «Не сделано»"),
    ("creative/09-ai-execution-evaluation/motion-spec.schema.json", "W1-Z9 (данные, зона кода): описание `track.property` называет исключением только `block-size` — после правки `property_exceptions` дополнить"),
    ("creative/01-creative-direction/ambition-levels.yaml", "PLAN Ф10 (данные, зона кода): «решение заказчика п. 13» в тексте полей; D4: `forbidden` — проза о тяжести; W1-Z9: `property_exceptions` — строка `clip-path` (вносит оркестратор)"),
    ("site/10-playbooks-contracts/01-procedure-brief-to-pages.md", "OE2-17: §8 п. 26 и §9 — стыки с прежним исполнителем макета → вход холста; OE5-25: §1.2 — статус подачи L0; D4: §12 — проза о тяжести находок по текущему поведению утилит; строки ≈ 30, 178 «по решению 20» — норма без номера"),
    ("creative/01-creative-direction/01-concept-and-directions.md", "PLAN Ф10: §6.3 — проза о тяжести находок по текущему поведению утилит"),
    ("text/10-templates-recipes/01-copy-deck-workflow.md", "PLAN Ф10: таблица статусов — утверждение copy deck с пустой метой и заглушкой пробела `missing[]`; D10: шаг «шот … 1440 и 390» (≈ стр. 257) — ширины приёмки, без имени прежнего исполнителя"),
    ("text/10-templates-recipes/README.md", "PLAN Ф10: утверждение copy deck с пустой метой и заглушкой пробела `missing[]`"),
    ("text/10-templates-recipes/copy-deck.schema.json", "PLAN Ф10 (данные, зона кода): имена проверок `x-status-rules`"),
    ("text/09-ai-generation-evaluation/02-generation-pipeline.md", "D8: §1.3, §1.5, §2 «Данные между шагами», «Источники» — снятые подкоманды `chain_inputs` и `make_skeleton.py` → `copydeck.py skeleton` и этапы скилла"),
    ("ux/README.md", "C17: `screen-states.yaml` в списке машинных файлов базы"),
    ("ux/06-feedback-states-motion/README.md", "C17: `screen-states.yaml` в списке машинных файлов папки"),
    ("ui/11-styles-trends/04-anti-slop-ui.md", "C17: §3 — запуск скрипта по текущему пути утилиты; PLAN Ф10: §1.3 — маркеры экрана против cd 06/04 §3: одна формулировка, второе место ссылкой"),
    ("common/README.md", "D10: стр. ≈ 34 — описание файла ширин приёмки по названию нормы NU-01"),
    ("common/canon.tsv", "D10: название нормы NU-01 (≈ стр. 204); PLAN Ф10: CN-62 — `verify-page` в тексте нормы; следы журнала в колонке `topic` и две ссылки на журнал (≈ стр. 103, 159) — правит оркестратор через реестр, пока журнал в main"),
    ("blender/09-web-runtime/examples/hero-lazy/README.md", "PLAN Ф10: пример без постера — назвать, чем постер собирается (`make_poster.py`), или снять слово «проверенный»"),
    ("blender/09-web-runtime/examples/camera-path-scroll/README.md", "PLAN Ф10: пример без постера — как выше"),
    ("ai-media/05-prompting/asset-plan.schema.json", "W1-Z1 (данные, зона кода): `x-canvas-map`, `note` правил «файл» и «id загрузки» — «по странице и слоту, принятое, по варианту и формату» и «строка холста поверхности»"),
    ("text/10-templates-recipes/copy-deck.schema.json", "W1-Z2 (данные, зона кода): описание `site_page_id` — «у страницы-образца шаблона коллекции — id плана шаблона»; W1-Z4: `x-canvas-map.copy_md.syntax` — пустая строка между строками продолжения — граница абзаца внутри значения"),
    ("site/10-playbooks-contracts/01-procedure-brief-to-pages.md", "W1-Z3: §5 и §12 — SM-22 «у шаблона есть план» — три уровня (шаблон без плана — `info`, служебный — `warning`); в таблице кодов нет строк SB-B* и SB-C*"),
    ("site/04-blocks/blocks.yaml", "W1-Z3 (данные, зона кода): шапка файла — журнал версий с датами и волнами"),
    ("text/02-strategy-messaging/02-awareness-hierarchy-objections.md", "W1-Z4: норма «блокер закрыт до `final-cta`» — оговорка о справочных и служебных страницах (`x-blocker-optional` схемы)"),
    ("text/10-templates-recipes/02-examples-ru.md", "W1-Z4: §4 и §6 — числа таблиц проверок и фраза «`approve` отказал: две заглушки» — по текущему поведению (заглушка названного пробела — `warning`)"),
    ("ui/09-design-tokens/04-reference-token-schema.md", "W1-Z6: §2.5 и вывод 6 выжимки («`calc(20 / 14)` — точно, без накопления ошибки») — оговорка, если проверка браузером подтвердит модель интерлиньяжа; результата проверки нет — пункт в «Не сделано»"),
    ("ai-media/02-providers-platforms/01-polza-api.md", "W1-Z7: §4 и таблица команд — операция с id исходника и тем же файлом не выполняется; коды выхода — по текущему поведению `polza.py`"),
    ("ai-media/02-providers-platforms/07-multichannel-client.md", "W1-Z7: отказ канала — паспорт с ответом канала"),
    ("ai-media/05-prompting/03-asset-spec-and-dialects.md", "W1-Z7: `output.format: svg` и поле `output_format` модели канала"),
    ("ui/04-shape-elevation/03-tools-checks-and-ai-errors.md", "D10: «1440 и 390» в прозе — ширины приёмки (`common/acceptance-widths.yaml`); если файл не называет пару — пункт в «Не сделано» с местом"),
    ("ui/13-evaluation-checklists/03-automated-checks.md", "D10: «1440 и 390» в прозе — ширины приёмки (`common/acceptance-widths.yaml`); как выше"),
    ("text/09-ai-generation-evaluation/03-evaluation.md", "D10: «1440 и 390» в прозе — ширины приёмки"),
    ("creative/09-ai-execution-evaluation/04-effectiveness-rubric.md", "D10: «1440 и 390» в прозе — ширины приёмки"),
]

ID_FILES = [                                              # id чек-листов → файл нормы (md) и производный машинный файл
    (r"\bUX-[A-Z0-9]{2,4}-\d+\b", ["ux/12-evaluation-checklists/02-master-checklist.md"]),
    (r"\bAC-[A-Z]{2,4}-\d+\b", ["ux/12-evaluation-checklists/03-automated-checks.md"]),
    (r"\bSITE-[A-Z0-9]{2,5}-\d+\b", ["site/09-ai-generation-evaluation/02-site-checklist.md"]),
    (r"\bAIL-\d+\b", ["site/09-ai-generation-evaluation/ai-landing-markers.yaml"]),
    (r"\bCOPY-(?:C|GEO)-\d+\b", ["text/09-ai-generation-evaluation/copy-checklist.yaml"]),
    (r"\b(?:WEB|MAT)-\d+\b", ["blender/11-evaluation-qa/05-master-checklist.md"]),
]
CUE = re.compile(r"ссылк\w*|→|(?<!\w)из(?!\w)|(?<!\w)по(?!\w)|см\.|вместо|как у|(?<!\w)на(?!\w)|довод|(?<!\w)к(?!\w)")
MECH_RAW = re.compile(r"99-raw|handoff|контракт\w*|_common\.md|(?<![\w-])X §|отчёт\w* X|временн\w+ словар\w+|kimi-\d+|\b(?:ux|ui|aim|cs|ck)-\d+\b")
MECH_PLAN = re.compile(r"(?<![\w-])PLAN(?![\w-])")
OUTSIDE = re.compile(r"scripts/|\.py\b|docs/projects|код-репо|<org>/|references/")


def read_tsv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def kb_index():
    """Файлы kb/: список; (база, NN, MM) → md; (база, NN) → папка; имя файла → пути."""
    files = kbscan.list_files(KB)
    by_addr, folders, by_name = {}, {}, defaultdict(list)
    for rel in files:
        parts = rel.split("/")
        by_name[parts[-1]].append(rel)
        if len(parts) >= 3 and re.match(r"\d\d-", parts[1]):
            folders[(parts[0], parts[1][:2])] = parts[0] + "/" + parts[1]
            m = re.match(r"(\d\d)-.*\.md$", parts[2])
            if m and len(parts) == 3:
                by_addr.setdefault((parts[0], parts[1][:2], m.group(1)), rel)
    return files, by_addr, folders, by_name


FILES, BY_ADDR, FOLDERS, BY_NAME = kb_index()
FILESET = set(FILES)
GLOSSARY = {"site": "site/00-glossary/glossary.md", "text": "text/00-glossary/glossary.md",
            "creative": "creative/00-glossary/glossary.md", "ui": "ui/00-glossary/glossary.md",
            "ai-media": "ai-media/00-glossary/glossary.md", "blender": "blender/00-glossary/README.md",
            "ux": "ux/00-glossary.md"}


def kb_paths(cell):
    """Пути kb/ из клетки реестра (canon, copies, sides): без раздела и якоря, без префикса «база:»."""
    out = []
    for item in (cell or "").split(";"):
        p = item.strip()
        if not p or p == "—":
            continue
        p = re.sub(r"^[a-z-]+:(?=[a-z.])", "", p)
        p = p.split(" §")[0].split("#")[0].strip()
        out.append(p)
    return out


def zone_of(rel):
    if rel == "INDEX.md" or rel.startswith("common/"):
        return "T-common-1"
    parts = rel.split("/")
    if "99-raw" in parts:
        return None
    key = "." if len(parts) == 2 else parts[1]
    for name, (base, dirs) in ZONES.items():
        if base == parts[0] and key in dirs:
            return name
    return None


def default_base(row):
    for p in kb_paths(row["canon"]):
        if p.split("/")[0] in BASES:
            return p.split("/")[0]
    cnt = defaultdict(int)
    for p in kb_paths(row["copies"]):
        if p.split("/")[0] in BASES:
            cnt[p.split("/")[0]] += 1
    if cnt:
        return max(cnt, key=cnt.get)
    return None


def cell_items(cell):
    """Клетка реестра → [(путь от kb/, раздел)]: «site/README.md §В-10» → ("site/README.md", "§В-10")."""
    out = []
    for item in (cell or "").split(";"):
        p = item.strip()
        if not p or p == "—":
            continue
        p = re.sub(r"^[a-z-]+:(?=[a-z.])", "", p)
        path, _, sec = p.partition(" §")
        out.append((path.split("#")[0].strip(), ("§" + sec.strip()) if sec else ""))
    return out


_TEXT = {}


def text_of(rel):
    if rel not in _TEXT:
        try:
            _TEXT[rel] = (KB / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            _TEXT[rel] = ""
    return _TEXT[rel]


def usable(rel):
    """Файл kb/, который может быть местом правки зоны: не 99-raw."""
    return rel in FILESET and "/99-raw/" not in rel


def is_base_plan(rel):
    return rel.endswith("/PLAN.md") and rel.count("/") == 1


ADDR = re.compile(
    r"(?:(?P<b>" + BASE_RX + r")\s+)?(?:[A-Z]\d?\s+)?(?P<nn>\d\d)/(?P<mm>\d\d|README)(?!\s*%)"
    r"|(?P<b2>" + BASE_RX + r")\s+(?P<word>README|глоссари\w*|CONTRADICTIONS)(?:\s+(?P<wn>\d\d)(?![/\d-]))?"
    r"|(?P<word2>README|[Гг]лоссари\w*|CONTRADICTIONS)\s+(?:базы\s+)?(?P<b3>" + BASE_RX + r")\b"
    r"|README\s+(?P<rn>\d\d(?:\s*(?:,|и|[–-])\s*\d\d(?![/\d-]))*)(?![/\d-])"
    r"|(?P<gl>[Гг]лоссари\w*)\s+(?P<gn>\d\d(?:\s*(?:,|и)\s*\d\d(?![/\d-]))*)(?![/\d-])"
    r"|(?P<bare>README|[Гг]лоссари\w*|00-glossary)"
    r"|(?P<bs>" + BASE_RX + r")\s+§\s*(?P<sec>\d+)"
    r"|(?<![\w/])(?P<ag>(?!P[1-7]\b)[A-Z]\d?)\s+§\s*(?P<agsec>\d+(?:\.\d+)*)"
    r"|(?P<bf>" + BASE_RX + r")\s+(?P<fn>\d\d)(?![/\d])"
    r"|`?(?P<file>[\w.-]+\.(?:ya?ml|json|tsv|md|html|css))`?"
    r"|(?P<rec>рецепт\w*)\s+(?P<recn>\d\d)\b"
    r"|(?P<pb>плейбук\w*)\s+(?P<pbb>" + BASE_RX + r")"
    r"|(?P<x>(?<![\w-])X-?\d+\b)|(?P<c>\[?C\d+\]?)|(?P<v>(?<![\w-])В-\d+\b)|(?P<r>(?<![\w-])R\d{1,2}\b)"
    r"|(?P<kit>\bKIT\b)|(?P<p>\bP[1-7]\b)|(?P<svod>свод\w*)|(?P<reg>реестр\w*\s+№)|(?P<ltp>live-test-plan)"
    r"|`(?P<tok>[A-Za-z_][\w.:-]{2,40}(?: [\w.:-]+)?)`"
    r"|(?P<bonly>(?<![\w/-])" + BASE_RX + r")(?=[\s,]|$)")
ID_RX = [(re.compile(rx), t) for rx, t in ID_FILES]
MANUAL = {                                                # действия без адреса в тексте: места названы здесь
    "CN-122": ["site/README.md", "ux/README.md", "blender/README.md", "text/CONTRADICTIONS.md",
               "creative/CONTRADICTIONS.md", "ui/CONTRADICTIONS.md", "ai-media/CONTRADICTIONS.md"],
    "GL-46": ["site/00-glossary/glossary.md", "text/00-glossary/glossary.md", "blender/00-glossary/README.md",
              "common/glossary.md"],
}
UMBRELLA = {                                              # зонтичные строки: своих мест нет
    "JU-01": "зонтичное действие: места названы в JU-25…JU-32",
    "TR-02": "вместе с TR-01 (таблицы контракта — в `common/owners.md`); пункты о прежнем исполнителе макета — TR-44",
    "GT-02": "вместе с TR-01 (таблицы контракта — в `common/owners.md`)",
}


def parse_action(aid, text, row):
    """→ (места: {файл: пометка}, механика: set, вне kb: bool, неразобранное: [фрагмент])."""
    items = [it for col in ("canon", "copies", "sides") for it in cell_items(row[col])]
    cand_kb = [p for p, _ in items if usable(p)]
    canon_kb = [p for p, _ in cell_items(row["canon"]) if usable(p)]
    copies_kb = [p for p, _ in cell_items(row["copies"]) if usable(p) and not is_base_plan(p) and p not in canon_kb]
    copy_dirs = [p for p, _ in cell_items(row["copies"]) if p not in FILESET and (KB / p).is_dir() and "99-raw" not in p]
    base = default_base(row)
    places, mech, unresolved = OrderedDict(), set(), []
    masked = re.sub(r"«[^»]*»", lambda m: "«" + "·" * (len(m.group(0)) - 2) + "»", text)
    masked = re.sub(r"»\s*→\s*«", "» ⇒ «", masked)

    def add(rel, note=""):
        if rel not in FILESET:
            return False
        if "/99-raw/" in rel:
            mech.add("99-raw")
        else:
            if is_base_plan(rel):
                mech.add("PLAN.md")
            places.setdefault(rel, note)
        return True

    def add_copies(only_bases=None, note="по колонке copies"):
        got = False
        for p in copies_kb:
            if only_bases and p.split("/")[0] not in only_bases:
                continue
            got = add(p, note) or got
        for d in copy_dirs:
            if only_bases and d.split("/")[0] not in only_bases:
                continue
            places.setdefault(d.rstrip("/") + "/", "папка целиком, по колонке copies")
            got = True
        return got

    if aid in MANUAL:
        for rel in MANUAL[aid]:
            add(rel, "место названо вручную")

    for clause in masked.split(";"):
        segs = clause.split(" — ")
        clause_places = len(places)
        named = set()
        for si, seg in enumerate(segs):
            for m in ADDR.finditer(seg):
                start = max(seg.rfind(",", 0, m.start()) + 1, 0)
                scope = seg[start:m.start()] if (si == 0 or "," in seg[:m.start()]) else seg[:m.start()]
                is_ref = bool(CUE.search(scope))
                if m.group("bonly"):
                    lead = seg[:m.start()].strip()
                    if lead == "" or lead.endswith((",", " и", "(", "тексты", "мест", "в текстах")):
                        base = ALIAS[m.group("bonly")]
                        if si == 0:
                            named.add(base)
                    continue
                b = m.group("b") or m.group("b2") or m.group("b3") or m.group("bf") or m.group("bs") or m.group("pbb")
                if b and not is_ref:
                    base = ALIAS[b]
                    if si == 0:
                        named.add(base)
                if is_ref:
                    continue
                if m.group("nn"):
                    nn, mm = m.group("nn"), m.group("mm")
                    bb_list = [ALIAS[m.group("b")]] if m.group("b") else ([base] if base else [])
                    if not m.group("b"):
                        bb_list += [p.split("/")[0] for p in cand_kb if p.split("/")[0] not in bb_list]
                    done = False
                    for bb in bb_list:
                        if mm == "README":
                            f = FOLDERS.get((bb, nn))
                            done = bool(f) and add(f + "/README.md")
                        elif (bb, nn, mm) in BY_ADDR:
                            done = add(BY_ADDR[(bb, nn, mm)])
                        if done:
                            break
                    if not done:
                        unresolved.append(m.group(0).strip())
                elif m.group("word") or m.group("word2"):
                    w = (m.group("word") or m.group("word2")).lower()
                    folder = FOLDERS.get((base, m.group("wn"))) if m.group("wn") else None
                    if folder:
                        (w.startswith("глоссари") and add(folder + "/glossary.md")) or add(folder + "/README.md") \
                            or unresolved.append(m.group(0))
                    elif w.startswith("readme"):
                        add(base + "/README.md") or unresolved.append(m.group(0))
                    elif w.startswith("глоссари"):
                        add(GLOSSARY.get(base, "")) or unresolved.append(m.group(0))
                    else:
                        add(base + "/CONTRADICTIONS.md") or add(base + "/README.md") or unresolved.append(m.group(0))
                elif m.group("rn"):
                    nums = re.findall(r"\d\d", m.group("rn"))
                    if re.search(r"[–-]", m.group("rn")) and len(nums) >= 2:
                        lo, hi = int(nums[-2]), int(nums[-1])
                        nums = nums[:-2] + ["%02d" % i for i in range(lo, hi + 1)]
                    for nn in nums:
                        f = FOLDERS.get((base, nn)) if base else None
                        if not (f and add(f + "/README.md")):
                            unresolved.append("README " + nn)
                elif m.group("gl"):
                    for nn in re.findall(r"\d\d", m.group("gn")):
                        f = FOLDERS.get((base, nn)) if base else None
                        if not (f and (add(f + "/glossary.md") or add(f + "/README.md"))):
                            unresolved.append("глоссарий " + nn)
                elif m.group("bare"):
                    w = m.group("bare").lower()
                    if not base:
                        unresolved.append(m.group(0))
                    elif w.startswith("readme"):
                        add(base + "/README.md") or unresolved.append(m.group(0))
                    else:
                        add(GLOSSARY.get(base, "")) or unresolved.append(m.group(0))
                elif m.group("bs"):
                    sec = "§" + m.group("sec")
                    hit = [p for p, s_ in items if usable(p) and p.startswith(base + "/") and re.match(re.escape(sec) + r"(?!\d)", s_)]
                    if hit:
                        for h in hit:
                            add(h)
                    else:
                        unresolved.append(m.group(0))
                elif m.group("ag"):
                    if m.group("ag") == "X":
                        continue                          # «X §…» — отчёт аудита в 99-raw: уходит с ним
                    sec = "§" + m.group("agsec")
                    hit = [p for p, s_ in items if usable(p) and (not base or p.startswith(base + "/")) and s_.startswith(sec)
                           and not s_[len(sec):len(sec) + 1].isdigit()]
                    if len(set(hit)) == 1:
                        add(hit[0], "по разделу %s в реестре" % sec)
                    else:
                        unresolved.append(m.group(0))
                elif m.group("fn"):
                    f = FOLDERS.get((base, m.group("fn")))
                    if not (f and add(f + "/README.md", "папка целиком — место уточнить по тексту действия")):
                        unresolved.append(m.group(0))
                elif m.group("file"):
                    name = m.group("file")
                    hits = [p for p in cand_kb if p.endswith("/" + name) or p == name]
                    if not hits:
                        pool = [p for p in BY_NAME.get(name, []) if "/99-raw/" not in p]
                        own = [p for p in pool if base and p.startswith(base + "/")]
                        hits = own if len(own) == 1 else (pool if len(pool) == 1 else [])
                    if hits:
                        for h in dict.fromkeys(hits):
                            add(h)
                    elif any(p.endswith("/" + name) and "/99-raw/" in p for p, _ in items):
                        mech.add("99-raw")
                    elif name not in ("judge.md", "evidence.md", "glossary.md"):
                        unresolved.append(name)
                elif m.group("rec"):
                    hit = [p for p in cand_kb if re.search(r"-recipes/%s-[^/]*\.md$" % m.group("recn"), p)]
                    if not hit and base:
                        hit = [p for p in FILES if p.startswith(base + "/") and re.search(r"-recipes/%s-[^/]*\.md$" % m.group("recn"), p)]
                    [add(h) for h in hit] or unresolved.append(m.group(0))
                elif m.group("pb"):
                    hit = [p for p in cand_kb if p.startswith(base + "/") and "playbook" in p]
                    [add(h) for h in hit] or unresolved.append(m.group(0))
                elif m.group("x"):
                    tok = m.group("x")
                    b2 = "creative" if "-" in tok else ("ai-media" if base == "ai-media" else "text")
                    add(b2 + "/CONTRADICTIONS.md") or unresolved.append(tok)
                elif m.group("c"):
                    if base == "ui" or "ui/CONTRADICTIONS.md" in cand_kb:
                        add("ui/CONTRADICTIONS.md")
                elif m.group("v"):
                    add("site/README.md")
                elif m.group("r"):
                    if base == "blender":
                        add("blender/README.md")
                    elif base == "ai-media" or any(p.startswith("ai-media/06-") for p in cand_kb):
                        add("ai-media/06-art-direction-consistency/01-visual-dna-from-ui.md")
                elif m.group("kit"):
                    add("blender/15-showcase/KIT.md")
                elif m.group("p"):
                    if base == "text" or row["node"] in ("JU", "TX"):
                        for name_, paths in BY_NAME.items():
                            if name_.startswith("p%s-" % m.group("p")[1]) and name_.endswith(".md"):
                                add(paths[0])
                elif m.group("svod"):
                    add(("site" if base == "site" else "text") + "/README.md")
                elif m.group("reg"):
                    if base in ("ux", "site", "blender"):
                        add(base + "/README.md")
                elif m.group("ltp"):
                    add("text/09-ai-generation-evaluation/live-test-plan.md")
                elif m.group("tok"):
                    tok = m.group("tok")
                    sides = [p for p in dict.fromkeys(cand_kb) if p not in canon_kb and p not in copies_kb]

                    def holders(word):                    # имя ищется в копиях, затем в сторонах, затем в каноне
                        if len(word) < 5:                 # короткое имя (`def`, `hr`) — только поле самого канона
                            return [p for p in canon_kb if word in text_of(p)]
                        for pool in (copies_kb, sides, canon_kb):
                            got = [p for p in pool if word in text_of(p)]
                            if got:
                                return got
                        return []

                    hit = holders(tok)
                    if not hit and "." in tok:
                        hit = holders(tok.split(".")[0])
                    for h in hit[:6]:
                        add(h, "по имени `%s` в файле" % tok)
            for rx, targets in ID_RX:
                for m in rx.finditer(seg):
                    start = max(seg.rfind(",", 0, m.start()) + 1, 0)
                    if not CUE.search(seg[start:m.start()]):
                        for t in targets:
                            add(t)
        first = segs[0].strip().lower()
        if len(places) == clause_places and re.match(r"(копии|тексты|в текстах|метки|пять мест|места|разделы)", first):
            add_copies(named or None)
        elif len(places) == clause_places and named and len(segs) > 1 and not re.search(r"\d\d/\d\d", clause):
            add_copies(named, "по колонке copies (база названа, адреса нет)")

    only_mech = bool(MECH_RAW.search(text)) and not places
    if MECH_RAW.search(text) and re.search(r"уход\w+|убрать|снять|при переносе|при уборке|опустоша|закрыт|выполнено", text):
        mech.add("99-raw")
    if MECH_PLAN.search(text):
        mech.add("PLAN.md")
    if not places and not only_mech and aid not in UMBRELLA:
        if re.search(r"копи\w+|ссылк\w+|так же", text):
            add_copies()
        else:
            for p in canon_kb:
                add(p, "по канону — место уточнить по тексту действия")
            add_copies(note="по колонке copies — место уточнить по тексту действия")
    if only_mech:
        mech.add("99-raw")
    outside = bool(OUTSIDE.search(text))
    return places, mech, outside, unresolved


def main():
    dry = "--dry" in sys.argv
    actions = [a for a in read_tsv(JOURNAL / "phase-4" / "actions.tsv") if a["phase"].strip() == "Ф10"]
    reg = {r["id"]: r for r in read_tsv(JOURNAL / "phase-4" / "registry.tsv")}

    per_file = defaultdict(lambda: {"actions": [], "extra": [], "ids": []})
    unplaced, mechanics = [], []
    stat = defaultdict(int)
    for a in actions:
        row = reg[a["id"]]
        places, mech, outside, unresolved = parse_action(a["id"], a["action"], row)
        how = "copies" if places and all("copies" in (n or "") for n in places.values()) else "адрес"
        label = "%s: %s" % (a["id"], a["action"])
        if places:
            for rel, note in places.items():
                z = zone_of(rel + "x" if rel.endswith("/") else rel)
                if z is None:
                    unplaced.append((a["id"], a["action"], "файл вне зон: " + rel))
                    continue
                per_file[rel]["actions"].append(label + (" [%s]" % note if note else ""))
                per_file[rel]["ids"].append(a["id"])
            stat["размещено (%s)" % how] += 1
            if unresolved:
                stat["из них с неразобранной частью"] += 1
                unplaced.append((a["id"], a["action"], "часть адреса не разобрана: " + ", ".join(unresolved)
                                 + "; размещено в: " + ", ".join(places)))
            if mech:
                mechanics.append((a["id"], a["action"], "+".join(sorted(mech)), "часть действия; остальное — в зонах: "
                                  + ", ".join(sorted({zone_of(p) or "?" for p in places}))))
        elif mech:
            stat["закрывается механикой"] += 1
            mechanics.append((a["id"], a["action"], "+".join(sorted(mech)), "действие целиком"))
        else:
            stat["не размещено"] += 1
            why = UMBRELLA.get(a["id"]) or ("место вне kb/ (код, канон слоя, код-репо)" if outside else (
                "адрес не разобран: " + ", ".join(unresolved) if unresolved else "в действии нет адреса, колонка copies пуста или ведёт вне kb/"))
            unplaced.append((a["id"], a["action"], why + "; канон: " + row["canon"] + "; копии: " + row["copies"]))

    # упоминания снятых утилит
    mentions = 0
    with open(JOURNAL / "phase-9" / "DF9-F10-kb-mentions.tsv", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            path, _, names = line.rstrip("\n").partition("\t")
            rel = path.replace("kb/", "", 1)
            if zone_of(rel) and rel in FILESET:
                per_file[rel]["extra"].append("снятые утилиты: " + names.strip())
                mentions += 1
    for rel, note in EXTRA:
        if rel in FILESET and zone_of(rel):
            per_file[rel]["extra"].append(note)
        else:
            unplaced.append(("прочее", note, "файла нет в kb/ или он вне зон: " + rel))

    # счёт маркеров и запись зон
    classes = kbscan.compile_classes()
    names = list(classes)
    targets = [n for n in names if classes[n][0]]
    zone_rows = defaultdict(list)
    for rel in FILES:
        z = zone_of(rel)
        if z is None:
            continue
        kind, lines, tokens, counts = kbscan.scan_file(KB / rel, classes)
        info = per_file.get(rel, {"actions": [], "extra": [], "ids": []})
        if kind != "prose" and not info["actions"] and not info["extra"]:
            continue                                      # машинный файл без названной работы в список зоны не входит
        marks = "; ".join("%s %d" % (n, counts[n]) for n in names if counts[n])
        zone_rows[z].append((rel, kind, lines, tokens, "; ".join(info["actions"]), "; ".join(info["extra"]), marks,
                             sum(counts[n] for n in targets), list(info["ids"])))

    for rel, info in per_file.items():
        if rel.endswith("/") and zone_of(rel + "x"):
            zone_rows[zone_of(rel + "x")].append((rel, "dir", 0, 0, "; ".join(info["actions"]), "; ".join(info["extra"]), "",
                                                  0, list(info["ids"])))
    summary = []
    for z in ZONES:
        rows = zone_rows.get(z, [])
        md = [r for r in rows if r[1] == "prose"]
        summary.append((z, len(md), sum(r[2] for r in md), sum(r[3] for r in md), len(rows) - len(md),
                        sum(len(r[8]) for r in rows), len({i for r in rows for i in r[8]}),
                        sum(1 for r in rows if r[5]), sum(r[7] for r in md)))
    if not dry:
        OUT.mkdir(parents=True, exist_ok=True)
        for z, rows in zone_rows.items():
            with open(OUT / (z + ".tsv"), "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, delimiter="\t", lineterminator="\n")
                w.writerow(["file", "kind", "lines", "tokens", "actions", "other", "markers"])
                for r in rows:
                    w.writerow(r[:7])
        with open(OUT / "_unplaced.tsv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["id", "action", "reason"])
            w.writerows(unplaced)
        with open(OUT / "_mechanics.tsv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["id", "action", "closed_by", "scope"])
            w.writerows(mechanics)
        with open(OUT / "_zones.tsv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["zone", "md_files", "md_lines", "md_tokens", "machine_files_named", "action_rows", "action_ids",
                        "files_with_other", "markers_md"])
            w.writerows(summary)
    print("действий Ф10: %d" % len(actions))
    for k, v in sorted(stat.items()):
        print("  %s: %d" % (k, v))
    print("строк _unplaced: %d; строк _mechanics: %d; файлов со снятыми утилитами в зонах: %d" % (len(unplaced), len(mechanics), mentions))
    print("\t".join(["zone", "md", "lines", "tokens", "machine", "act_rows", "act_ids", "other", "markers"]))
    for s in summary:
        print("\t".join(str(x) for x in s))
    print("ИТОГО\t%d\t%d\t%d\t%d\t%d\t-\t%d\t%d" % tuple(sum(s[i] for s in summary) for i in (1, 2, 3, 4, 5, 7, 8)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
