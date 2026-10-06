# Д-text-2 — машинные файлы базы text, папки 01…06

Текст отчёта вернул исполнитель зоны в ответе (инструмент не дал ему записать файл); записан оркестратором дословно.
Корень — репозиторий шаблона, пути файлов — от `.claude/skills/design-deep-dive/kb/text/`. База — `1e0cd2a`.

Итог: пройдено 32 файла, изменён 31 (+708 −725 строк), `ux-07-06.yaml` — производный, не тронут. Маркеры 415 → 13:
raw 35 → 4, kimi 30 → 0, k3 7 → 0, research 38 → 0, process 77 → 0, decision 1 → 0, plan 26 → 0, removed 2 → 2,
letters 197 → 6, words 9 → 1. Сверх сканера в `copy-slots.yaml` сняты формы, которых он не считает: «D thresholds.yaml
v2» — 65, «правило E» — 61, «у D …» — 70, `rules_owner` с буквой — 23, `voice` с «F» — 14.

## Решения по формам (каждая решена один раз)

- **Штамп в шапке** («text-research · волна N · агент X · дата»): у схем строка снята, у примеров осталось «# Формат:
  ../x.schema.yaml (…_version 1)».
- **Буква перед адресом статьи:** B1 §N → `text 02/02 §N`; B2 §N → `text 02/03 §N`; D §N → `text 03/02 §N`; H §N и
  «H 01 §N» → `text 08/01 §N`; A/02 §7 → `text 01/02 §7`. «C §N» — по смыслу: каталог маркеров `text 06/01`,
  спецификация линтера `text 06/02`. Каждый адрес сверен с заголовками статей.
- **Голая буква-указатель:** (H) → `text 08/01` (право) или `text 08/02` (типографика), где видно — с параграфом; G →
  `text 07`, `07/01` или `07/03`; site C → `site 03`, site I → `site 08/01`, site H → `site 07`, site A → `site`; буква
  рядом с именем файла или поля снята.
- **Корпус и правила слотов:** «у D» → «в корпусе» / «в замере корпуса»; «D thresholds.yaml v2» → «thresholds.yaml v2»;
  «правило E», «решение E», «расчёт E» → «…базы»; «предложение B2/E, принято E» → «предложение text к словарю site».
- **Опыты и сырьё:** «опыт X/NN», пути `99-raw/…` и строки-списки с ними сняты, числа и выборки остались.
  «[проверено kimi E/03]» → «[проверено]».
- **Сторонний исполнитель макета:** «kimi 05/03 (… работ K3)» → «разбор LLM-вёрстки (… работ)»; `facts.md` kimi →
  «facts.md входа холста».
- **Видео-конспекты:** `../kimi-research/91-videos/digests/<id>.md` → `[V:<id>]` — нотация базы.
- **PLAN.md:** «PLAN.md поправка к ux …» → «поправка к ux …»; «PLAN.md «Жанры»» → «решение базы» или
  `06-anti-slop/01 §10/§11`; «PLAN.md риск N», «задание C», «аудит UX/UI §N» сняты.
- **Владелец:** `owner` → `text · <папка>`, как уже было в `copy-slots.yaml`; `x-owner` → `text · <папка>` с прежней
  оговоркой о контракте тройки.
- **Статус:** `x-status` с волнами и «T1» → «черновик».
- **Решения заказчика:** «решение заказчика п. 16» и «решение заказчика 24.09.2026» сняты, норма осталась.
- **Соседняя база:** `../site-research/03-page-structure/01` → `../site/03-page-structure/01-narratives-and-section-order.md`
  (7 значений `site_ref`, файл существует); `ai-media-research` → `ai-media` (папка существует).

## Файл → что сделано → маркеры до / после

| файл | строк ± | было | до → после | осталось |
|---|---|---|---|---|
| `01-foundations/formulas.yaml` | +43 −44 | raw 3; kimi 4; research 13; process 2; letters 4; words 4 | 30 → 1 | letters 1 |
| `02-strategy-messaging/examples/facts-kvarts.yaml` | +11 −11 | raw 2; kimi 5; research 2; process 1; letters 1 | 11 → 0 | — |
| `…/examples/facts-service-renovation.yaml` | +4 −4 | research 1 | 1 → 0 | — |
| `…/examples/hierarchy-kvarts-problem-aware.yaml` | +4 −5 | raw 1; kimi 1; research 1; process 1; letters 1 | 5 → 0 | — |
| `…/examples/hierarchy-otves-problem-aware.yaml` | +6 −6 | raw 2; research 1; letters 1 | 4 → 0 | — |
| `…/examples/hierarchy-otves-product-aware.yaml` | +2 −2 | raw 1; research 1 | 2 → 0 | — |
| `…/examples/meaning-kvarts.yaml` | +10 −12 | raw 2; kimi 7; research 2; process 2; letters 1 | 14 → 0 | — |
| `…/examples/meaning-lesnaya-obzharka.yaml` | +9 −9 | research 2; process 1; letters 2 | 5 → 0 | — |
| `…/examples/meaning-otves.yaml` | +11 −11 | raw 1; research 1; process 1; letters 2 | 5 → 0 | — |
| `02-strategy-messaging/facts.schema.yaml` | +28 −29 | research 2; process 1; decision 1; letters 1 | 5 → 0 | — |
| `02-strategy-messaging/meaning.schema.yaml` | +27 −28 | research 2; process 4; letters 7; words 1 | 14 → 1 | words 1 |
| `02-strategy-messaging/message-hierarchy.schema.yaml` | +7 −8 | research 2; process 2; letters 1 | 5 → 0 | — |
| `02-strategy-messaging/voc.schema.yaml` | +3 −4 | research 2; process 1 | 3 → 0 | — |
| `03-corpus-measured/thresholds.yaml` | +10 −10 | raw 1; research 1; process 1; removed 2; letters 2; words 2 | 9 → 2 | removed 2 |
| `04-copy-by-block/copy-slots.yaml` | +361 −367 | raw 8; k3 1; process 23; letters 137; words 2 | 170 → 3 | letters 3 |
| `05-voice-editorial/examples/voice-grafa-b2b.yaml` | +9 −10 | raw 5; research 1; process 3 | 9 → 2 | raw 2 |
| `05-voice-editorial/examples/voice-otves-warm.yaml` | +17 −17 | raw 2; research 1; process 4; letters 3 | 10 → 0 | — |
| `05-voice-editorial/examples/voice-peklo-bold.yaml` | +12 −13 | raw 5; research 1; process 2; letters 4 | 12 → 2 | raw 2 |
| `05-voice-editorial/voice.schema.yaml` | +37 −38 | raw 1; research 2; process 1; letters 18 | 22 → 0 | — |
| `06-anti-slop/lexicon/analyzers.yaml` | +10 −10 | raw 1; kimi 3; k3 1; process 3; plan 2; letters 2 | 11 → 0 | — |
| `06-anti-slop/lexicon/artifacts.yaml` | +8 −8 | kimi 5; k3 3; process 2; plan 2 | 9 → 0 | — |
| `06-anti-slop/lexicon/en-lex.yaml` | +1 −1 | process 1 | 1 → 0 | — |
| `06-anti-slop/lexicon/en-mkt.yaml` | +7 −7 | process 2; plan 2; letters 1 | 5 → 0 | — |
| `06-anti-slop/lexicon/en-syn.yaml` | +2 −2 | process 1; plan 1 | 2 → 0 | — |
| `06-anti-slop/lexicon/marketing-role.yaml` | +12 −12 | process 3; plan 7; letters 1 | 11 → 0 | — |
| `06-anti-slop/lexicon/ru-lex.yaml` | +4 −4 | process 1; plan 2 | 3 → 0 | — |
| `06-anti-slop/lexicon/ru-mkt.yaml` | +17 −17 | process 4; plan 2; letters 1 | 7 → 0 | — |
| `06-anti-slop/lexicon/ru-punct.yaml` | +16 −16 | kimi 5; k3 2; process 4; plan 4; letters 2 | 15 → 0 | — |
| `06-anti-slop/lexicon/ru-struct.yaml` | +7 −7 | process 2; plan 2; letters 2 | 6 → 0 | — |
| `06-anti-slop/lexicon/ru-syn.yaml` | +5 −5 | process 1; plan 1; letters 1 | 3 → 0 | — |
| `06-anti-slop/lexicon/ux-07-06.yaml` | без правок | letters 2 | 2 → 2 | производный |
| `06-anti-slop/profiles.yaml` | +8 −8 | process 3; plan 1 | 4 → 0 | — |
| **итого** | +708 −725 | | **415 → 13** | raw 4; removed 2; letters 6; words 1 |

В словарях линтера слова-образцы и регулярные выражения не менялись. Правились комментарии шапок, `owner`, `source`,
`evidence`, `note` и следы в текстах `message` и `replacement`.

## Остаток маркеров

- `05-voice-editorial/examples/voice-grafa-b2b.yaml:20, :180` и `voice-peklo-bold.yaml:20, :180` — `facts_ref` и
  `claims_boundaries_ref` ведут в `../../99-raw/experiments/F/04-voice-samples/facts-demo-*.yaml`: путь файла-данных,
  файл существует.
- `03-corpus-measured/thresholds.yaml:21, :26` — `copy_extract 0.3.0`: версия утилиты замера корпуса, условие замера.
- `01-foundations/formulas.yaml:223` — «(L2)»: уровень амбиции, не буква исполнителя.
- `04-copy-by-block/copy-slots.yaml:109, :573, :2746` — «(H1)», «(H2)»: уровни заголовков.
- `02-strategy-messaging/meaning.schema.yaml:713` — «дубли сводит оркестратор»: неясно, роль скилла или след.
- `06-anti-slop/lexicon/ux-07-06.yaml:2438, :2513` — производный файл.

## Ключи и значения, которые читает код

- **`brand.facts_ref`** в `voice-grafa-b2b.yaml` и `voice-peklo-bold.yaml` читает `scripts/text/validate_voice.py` —
  сверка `fact:` образцов. Значение — путь в `99-raw`. Снять след можно только переносом двух файлов демо-фактов в
  `05-voice-editorial/examples/` и сменой четырёх значений, включая `claims_boundaries_ref`.
- **`x-canvas-map`** в `facts.schema.yaml`, `meaning.schema.yaml`, `message-hierarchy.schema.yaml`, `voice.schema.yaml`
  не правился; `spec_check.py canvas-map` — error 0.
- **Тексты, которые код выводит в находках:** `copydeck.py` печатает `exceptions[0]` слота из `copy-slots.yaml`;
  `copy_lint.py` отдаёт `source`, `evidence`, `note`, `message`, `replacement` правил. Тексты изменены, самопроверки и
  смоук проходят.
- **Код не читает** (поиск по `scripts/`): `owner` словарей и `formulas.yaml`, `x-owner`, `x-status`, `rules_owner`,
  `proposal_note`, `lengths_source`, `length_rule`, `examples_rule`, `site_ref`, `collected_by`. У `external_rules` в
  `profiles.yaml` читается только `path`, поэтому ключи `owner: G|H` и `wave: 2` сняты.

## Производные

- `06-anti-slop/lexicon/ux-07-06.yaml` собирает `scripts/text/ux_dict_to_yaml.py` из
  `kb/ux/07-ux-writing/06-banned-words-and-patterns.md`. След «(E2 §8.3)» — в строке 331 этой статьи; после её правки —
  пересборка.

## Проверки

YAML 32/32, метасхема 5 схем; `validate_facts`, `validate_meaning` (40/40), `validate_voice` — OK; самопроверки
`copydeck` 212/0, `claims_check` OK, `copy_lint` 92/0; `spec_check.py canvas-map` — error 0, warning 0. Смоук: text
24/0, site 31/0, creative 21/0, claude-design 29/0, project 33/0; `sync_check` 17/0; `fixture_gen --check` совпадает;
`accept.py` — под масками 31, разбор и следы 0 находок.

## Для фикстур

Сборка совпадает. Сами фикстуры несут те же штампы — копии примеров базы: `scripts/tests/fixtures/minimal/files/
{voice,facts}.yaml`, `input-site/files/voice.yaml`, `input-landing/files/site/promo/hierarchy/home-{product,problem}-
aware.yaml`, `input-landing/files/site/promo/copy/home.yaml`, `package-landing-defects/files/{facts,voice}.yaml`,
`package-landing-defects/files/site/promo/meaning.yaml`, три `…/motion/home.motion-spec.yaml`.

## Для текстов

- Заголовки статей text ещё несут буквы и опыты; адреса в данных даны номерами параграфов и остаются верными.
- `03-corpus-measured/README.md:12–13` перечисляет `corpus.tsv` и `measurements.tsv`, которых в папке нет; на них же
  ссылаются шапка и `source` в `thresholds.yaml`.
- `kb/site/01-foundations/site-brief.schema.json:5, :16` — следы в зоне site.

## Вопросы

1. «контракт тройки v2 §N» остался в `x-owner` трёх схем, в шапках `facts.schema.yaml` и `message-hierarchy.schema.yaml`,
   в `source` у `artifacts.yaml`, `marketing-role.yaml`, `ru-mkt.yaml`; норма живёт в `kb/common/owners.md` («Форматы
   обмена») — нужна одна замена на все базы.
2. `thresholds.yaml` → `rows[].source: corpus-D:lead|human:…` (355 строк) — значение с буквой корпуса, код не читает.
3. `x-status` в `meaning.schema.yaml` и `message-hierarchy.schema.yaml` сведён к «черновик» — подтвердить статус форматов.
4. «оркестратор» в `meaning.schema.yaml:713` — роль скилла или след.
5. «`[проверено]` соседом» в `artifacts.yaml:96` и «(стр. 344)» в `marketing-role.yaml:92` оставлены как есть.
