# Д-text-1 — машинные файлы базы text: `07-seo-geo-copy`, `08-russian-legal-typography`, `09-ai-generation-evaluation`, `10-templates-recipes`

Коммит начала — `1e0cd2a`. Список зоны — 20 файлов, пройдены и тронуты все 20 (правки по месту, пакетами `kbpatch.py`;
файлы замен — `~/.cache/design-deep-dive/out/f10/Д-text-1/p-*.py`). Маркеры зоны: 480 → 3; остаток — номер решения ФАС и
значение перечисления `draft-phase-1` в двух файлах. Ключи, id, перечисления, числа, пороги, порядок записей, тексты,
факты и цены демо-примеров не менялись: сверка разобранных YAML и JSON с `HEAD` по путям данных — в 19 файлах
изменились 317 значений полей-пояснений (`notes` 75, `source` 50, `description` схемы 36, `evidence` 30, `ref` 14,
`tool` 10, `authors` 10, `note`, `reason`, `who`, `owner`, `limits`, `basis` и подобные), типы значений прежние, новых
путей нет; снято 12 путей — журнал версий `changelog` рубрики (3 записи) и по одному элементу списков `sources` у трёх
критериев рубрики (путь сырья соседней базы, путь опыта, `PLAN.md`). Git — только чтение. Пути ниже — от
`.claude/skills/design-deep-dive/kb/text/`, утилиты — от корня скилла.

## Файлы

Маркеры — сумма по классам `kbscan.py` с классами `--extra`; «→» — до и после.

| файл | что сделано | маркеры |
|---|---|---|
| `07-seo-geo-copy/geo-checklist.yaml` | шапка без штампа «text-research · волна 2 · агент G · дата», «решения оркестратора» и теста загрузки из `99-raw`; `owner` → `text/07-seo-geo-copy`; в `methods`, `how.ref`, `source`, `evidence`, `note` буквы исполнителей → адреса базы («A 03 §2.2» → «text 01/03 §2.2», «B2 03-proof-and-facts.md» → путь от корня базы, «(C)» у id правил → «(06-anti-slop)», «site H / G» → «site 07 / site 06»); сняты «контракт тройки §3 п.10», «решение заказчика … (PLAN)», «отчёт G §5», путь опыта в `example.note` | 17 → 0 |
| `07-seo-geo-copy/geo-rules.yaml` | шапка без штампа и теста из `99-raw`; «временный словарь `99-raw/notes/temp-vocabulary-v0.yaml`» → «словарь — `04-copy-by-block/copy-slots.yaml`» (все восемь слотов там есть); `owner`; буквы в `source` и `note` → адреса базы | 6 → 0 |
| `07-seo-geo-copy/meta-rules.yaml` | шапка без штампа; «скрипт опыта `99-raw/…/run.py`» → `../../scripts/text/copydeck.py validate` (ведёт `checks_outside_linter`); `owner`; «корпус D», «(01-meta-corpus)», путь опыта в `source` → «корпус 03-corpus-measured»; «W2», «(B2)», «site H» сняты или заменены адресом | 7 → 0 |
| `08-russian-legal-typography/claims-rules.yaml` | шапка без штампа и букв; `owner` → `text/08-russian-legal-typography`; в `source` сняты «(дайджест W2)» ×3, «опыт H/01», «опыт H/02», «(B2)»; «B1 01», «B2 03», «A 03», «B2 04» → «text 02/01», «text 02/03», «text 01/03», «text 02/03 §6»; заметки `overrides` без букв | 13 → 1 |
| `08-russian-legal-typography/typography-rules.yaml` | шапка без штампа и букв; `owner`; «по решению C» ×3, «решение заказчика п. 16» ×2 сняты; «B2 03 §5» → «text 02/03 §5» | 8 → 0 |
| `09-ai-generation-evaluation/copy-checklist.yaml` | шапка без штампа, «решения оркестратора», теста из `99-raw` и журнала версии «v1.1 …»; `owner` → `text/09-ai-generation-evaluation`; комментарий-план у `status` снят (значение не тронуто); в `evidence` сняты id опытов (B2/02, H/01, C/04, D/03, E/01, C/02, I/01, I/03, C/05, A/02, F/02) и пути сырья — слова, выборка и числа проверки остались; в `source` путь отчёта `99-raw/reports/wave1-B2-report.md` → `live-test-plan.md B2-2`, `../site-research/` → `../site/`; `tool`: путь `../kimi-research/99-raw/…` → `../../scripts/ai-media/stand_run.py page`, «kimi shot.py, copy_extract.py D» → `claude-design/kit/shot.py` и `claude-design/dc_texts.py`; «демо K3» → «демо LLM-вёрстки»; `example_run.deck` — путь сырья → описание словами | 55 → 1 |
| `09-ai-generation-evaluation/copy-rubric.yaml` | шапка без штампа и путей `99-raw` (опыты → `03-evaluation.md §3.4`, проверка → `chain_inputs.py --selftest`); `owner`; `changelog` (3 записи) снят — код ключ не читает; id опытов и буквы в `evidence`, `limits`, `why`, `why_not`, `read`, `inputs` сняты или заменены адресом; из `sources` убраны `../kimi-research/99-raw/…`, `99-raw/…`, `PLAN.md …`; `91-videos/digests/<id>.md` → `[V:<id>]` ×4 | 35 → 1 |
| `10-templates-recipes/before-after.tsv` | `rule_ref` (97 ячеек): сырые deck v0 → `10-templates-recipes/examples/ru-*.yaml#секция/слот` (25; слоты и тексты `after` сверены с примерами), хвост «· 99-raw/…/pairs.yaml#id» снят (17), `…/I/04-chain-manual/…` → `09-ai-generation-evaluation/02-generation-pipeline.md §4` (3), `…/A/02-…/pairs.tsv#pN` → `01-foundations/02-what-copy-changes-evidence.md §4` (9), `91-videos/digests/<id>.md [t]` → `[V:<id> t]` (43); `evidence` (152): id опытов и сырой `test_examples.py` сняты, слова проверки остались; `why` (34): буквы и id опытов. Колонки `before`, `after`, `lang`, `genre`, `marker_id` не тронуты; 541 строка × 8 колонок, пустых `why` — 0 | 255 → 0 |
| `10-templates-recipes/copy-deck.schema.json` | `x-owner` → `text · 10-templates-recipes`; 36 описаний без букв исполнителей, «предложение I / G», «v1.1 (I3)», «(T2)», «PLAN.md», «решение заказчика п. 16»; блок `x-canvas-map` не тронут (все правки — строки 9–449, блок с 513-й) | 14 → 0 |
| `10-templates-recipes/examples/en-okoshko-saas.yaml`, `en-otves-case.yaml`, `ru-otves-article-faq.yaml`, `ru-otves-case.yaml` | шапка-штамп «(…, J3, дата)», «ai-self J3», «набор B2», «решение заказчика п. 16»; `authors` «J3 (…)» → «агент (…)»; буквы в `notes`, `basis`, `test_plan` → адреса базы и id правил | 1 → 0 (каждый) |
| `10-templates-recipes/examples/ru-kvarts-preorder.yaml`, `ru-okoshko-saas.yaml`, `ru-otves-lead.yaml` | шапка-штамп; `authors` (две записи, число прежнее); в `notes` слотов «B2», «H DIST-01», «голос F», «граница D» → «пробел фактов», `COPY-L-DIST-01`, «образец голоса», «граница корпуса»; заметка страницы: «Пример J3 (фаза 2 J): основа — E3 `99-raw/…`, upgrade v0 → v1, у E3 было…» → «Правки примера — в notes слотов и в 02-examples-ru.md» | 4 → 0, 4 → 0, 6 → 0 |
| `10-templates-recipes/examples/facts/facts-demo-saas-okoshko.yaml`, `facts-demo-saas-okoshko-en.yaml` | шапка: «КОПИЯ демо-фактов агента E … md5 …», «Источник правды — файл E … `99-raw/…`», штамп «text-research · волна 2 · агент E» сняты; `collected_by`, `source.who` «агент E (демо)» → «демо-набор»; `notes` «ДЕМО-факт E.» → «ДЕМО-факт.» ×17; буквы в `notes`, `note`, `reason`, `missing.what` → адреса и id правил | 15 → 0, 12 → 0 |
| `10-templates-recipes/examples/facts/facts-demo-webinar-okoshko.yaml`, `facts-otves-en.yaml` | шапка-штамп; `collected_by`, `source.who`; `notes`, `note`, `reason` без «J3», «E», «B2», «F/04», путей `99-raw` | 10 → 0, 15 → 0 |

По классам: `raw` 83 → 0; `kimi` 3 → 0; `k3` 1 → 0; `research` 19 → 0; `process` 224 → 0; `decision` 1 → 1; `journal` 2 → 2;
`removed` 1 → 0; `plan` 3 → 0; `letters` 95 → 0; `words` 49 → 0; сумма 480 → 3.

Буквы, которых шаблоны `kbscan` не видят («(B2)», «H DIST-01», «голос F», «E 03 §3.2», «J3», «корпус D» и подобные),
найдены своим поиском (`letters.py` в папке выхода зоны) и сняты во всех 20 файлах. Карта замен: A → `01-foundations`,
B1 и B2 → `02-strategy-messaging` («B2 §N» = `text 02/03 §N`), C → `06-anti-slop`, D → `03-corpus-measured`, E →
`04-copy-by-block`, F → `05-voice-editorial`, G → `07-seo-geo-copy`, H → `08-russian-legal-typography`, I →
`09-ai-generation-evaluation`, J → `10-templates-recipes`; у базы site: G → `site 06`, H → `site 07`, I → `site 08/01`
(так же у соседа Д-text-2). Каждый адрес «text NN/MM §N», появившийся в заменах, сверен с заголовком в md; буква рядом с
уже названным файлом просто снята.

## Остаток маркеров

- `08-russian-legal-typography/claims-rules.yaml:53` — `decision`: «ФАС: решение № 08/22689/25 от 13.03.2025» — номер
  решения ФАС (правоприменение), не решение исследования.
- `09-ai-generation-evaluation/copy-checklist.yaml:13`, `copy-rubric.yaml:15` — `journal` (`phase-1`): значение
  `status: draft-phase-1` — см. «Ключи и значения».

Вне шаблонов `kbscan`, оставлено с причиной:

- `10-templates-recipes/copy-deck.schema.json` — «(v0)» в описаниях полей (19 мест) и «v0» в `description`, `x-status`:
  привязаны к ключу `x-v0-fields` — см. «Ключи и значения».
- `copy-checklist.yaml`, `copy-rubric.yaml` — id `LT-03…LT-05`, `B2-2`, `W1-7`, `A4` (строки таблиц `live-test-plan.md`),
  `DR-1…DR-6` (правила решения рубрики), «CONTRADICTIONS X24» — id записей базы, не буквы исполнителей.
- `before-after.tsv` (`why`), `claims-rules.yaml:1224` — «[S9]», «[S14]», «04/03 §4.7 [S19]» — номера источников md базы.
- `07-seo-geo-copy/geo-rules.yaml:55` — «(симуляция, уровень E)» — уровень доказательства исследования, не буква.
- `geo-checklist.yaml` — комментарии-разделы «A. … D.» — метки групп пунктов.
- Примеры — «ai-self» (значение `source` варианта и слово шапок): значение перечисления схемы copy deck.
- Заметки примеров — «(01 §8)», «(02 §3)», «(02 §9)», «(03 §2)», «(01 §6.3)»: адреса статей `04-copy-by-block` без
  имени папки — не маркер, адрес неполный (см. «Вопросы»).

## Ключи и значения, которые читает код

- `09-ai-generation-evaluation/copy-rubric.yaml:15`, `copy-checklist.yaml:13` — `status: draft-phase-1`: значение
  перечисления, общее с рубрикой site (`kb/site/09-ai-generation-evaluation/site-rubric.json`, `"status":
  "draft-phase-1"`); в имени — фаза исследования. Не тронуто (у рубрики строка совпадает с `HEAD` байт в байт, у
  чек-листа снят только комментарий-план «фаза 2 добавит… правила E, F, G, H»). Менять — одним решением для трёх файлов.
- `10-templates-recipes/copy-deck.schema.json:448–458` — ключи `x-v0-fields`, `status_values_v0`: читает
  `scripts/text/copydeck.py --selftest` (сверка списка полей и статусов); в имени — версия черновика исследования. Не
  тронуты; пометки «(v0)» в описаниях полей оставлены как ссылки на этот список.
- `10-templates-recipes/before-after.tsv`, колонка `rule_ref` — читает `copydeck.py before-after` (шаблон «файл.md §N» у
  строк с пустым `why`). Значения менялись только у строк с заполненным `why`; `before-after --check` — к заполнению 0.
  112 ячеек `why` вида «норма: <заголовок> (<rule_ref>)» не тронуты.
- `09-ai-generation-evaluation/copy-checklist.yaml:245` — `pass_when` пункта `COPY-C-18`: `mockup_checks.py` и
  `marketing_audit.py` берут из него число шаблоном «не чаще 1 на (\d+) секци». Снята только буква «D» после
  `thresholds.yaml`; фраза с числом на месте.
- `copy-checklist.yaml`, `copy-rubric.yaml` — `scripts/site/build_profile.py` собирает id `COPY-X-NN` шаблоном по всему
  тексту файлов, включая комментарии: набор id до и после один и тот же (65).
- `copy-rubric.yaml`, `criteria[].judge.questions[].read` — `scripts/text/chain_inputs.py` кладёт текст в проекцию
  судье: из `read` вопроса `COPY-R-04 q1` снят id опыта «(I/03)».
- Файлы правил (`meta-rules.yaml`, `geo-rules.yaml`, `claims-rules.yaml`, `typography-rules.yaml`) — `copy_lint.py`
  отдаёт `source` и `evidence` правила в находке, `overrides[].note` дописывает к заметке правила: тексты этих полей
  теперь без букв; ключи, уровни, шаблоны и примеры правил не менялись.
- `examples/facts/facts-demo-saas-okoshko.yaml:352` — `missing[].what` уходит в `facts.md` входа холста
  (`copydeck.py export`): «(сведения о продавце — site I; блок «продавец» — H)» → «(… — site 08/01; блок «продавец» —
  COPY-L-DIST-01)» — единственная разница в выводах проверок примеров до и после правки.
- `copy-checklist.yaml:205` — `tool: "copy_metrics.py readability — справочно"`: утилиты `copy_metrics.py` в `scripts/`
  нет. Снята только буква; имя утилиты оставлено — решение за владельцем чек-листа.
- Вне зоны, к сведению зоны кода: `scripts/text/copydeck.py` называет формат `meta-rules.yaml` буквой (`'format': 'G'`),
  `copy_lint.py` — «внешнем файле правил (G, H, …)» в комментарии.

## Производные

Производных файлов из перечня брифа в зоне нет. `before-after.tsv` стоит в `scripts/maint/data/sync.yaml`
(`text-before-after`): генератор дописывает только пустой `why` по заголовку раздела `rule_ref` и ячейки с текстом не
пересобирает. Если текстовая зона меняет заголовки разделов md, 112 ячеек «норма: <заголовок> (…)» останутся со
старыми заголовками — править их руками или очисткой `why` с `copydeck.py before-after --write`.

## Для фикстур

`fixture_gen.py build --all --check` — совпадает: рецепты базу не читают, правка примеров сборку не меняет. В фикстурах
лежат копии шапок-штампов и заметок примеров зоны с теми же следами:
`scripts/tests/fixtures/package-landing/files/site/promo/copy/spasibo.yaml` и
`package-landing-defects/files/site/promo/copy/spasibo.yaml` (шапка `ru-otves-case.yaml`: «…, J3, 2026-09-24»),
`input-landing/files/site/promo/copy/home.yaml` (шапка и заметки `ru-otves-lead.yaml`: «J3», «E3
deck-otves-lead-v0.yaml», «B2», «H DIST-01», «голос F»).

## Для текстов

- `10-templates-recipes/README.md:22,91`, `README.md:343,345,350,549` (база text) — `99-raw/tools/before_after_build.py`,
  `99-raw/tools/copy_metrics.py`, `orch_check.py`, «`10/before-after.tsv` — только скриптами»: таблицу ведёт
  `copydeck.py before-after`, остальное — данные.
- `10-templates-recipes/02-examples-ru.md:172` — «источник `J3-examples`» у строк `before-after.tsv`: такого значения в
  таблице нет.
- `09-ai-generation-evaluation/live-test-plan.md` — id строк `B2-2`, `W1-7`, `A4` и `CONTRADICTIONS.md` — `X24`: на них
  ссылаются `copy-checklist.yaml:275–276` и `copy-rubric.yaml` (limits `COPY-R-01`, `COPY-R-10`, read `COPY-R-07 q2`);
  переименование id в md — вместе с этими ссылками.
- `09-ai-generation-evaluation/03-evaluation.md §3.4` — заголовок «Что показали опыты I/01 и I/03»: на раздел ведёт
  шапка `copy-rubric.yaml`.
- `copy-checklist.yaml:350` (`COPY-C-32`, `tool`) — «для текстов карточки-картинки или адаптация»: слепой выбор текстов
  ведёт `copydeck.py export-variants` и `apply-selection`; уточнение формулировки — содержательная правка владельца.
- `copy-checklist.yaml:363` (`COPY-C-33`, `tool`) — имена живых утилит (`claude-design/kit/shot.py`,
  `claude-design/dc_texts.py`) подставлены вместо «kimi shot.py, copy_extract.py»: сверить с этапом приёмки макета.

## Файлы к снятию

В зоне нет. После правки файлы зоны не ссылаются на `kb/text/99-raw/` (в том числе на
`99-raw/notes/temp-vocabulary-v0.yaml`, который называл `geo-rules.yaml`).

## Соседям

- Оркестратору, Д-text-2: `10-templates-recipes/examples/ru-okoshko-webinar.yaml` нет ни в одном списке зон (`kbscan`
  даёт 0 маркеров), но следы в нём есть: шапка «(…, J3, 2026-09-24)», «ai-self J3», «ДЕМО J3», «демо-сервис E»,
  `authors: ['J3 (…)']`, в `notes` и `basis` — «E 03 §3.5», «H COPY-L-FREE-01», «профиль F», «решение J3», «Шаблон G»,
  «голос F, линтер C», `selection.by: 'редактор J3 (демо)'`, «С 24.09 (аудит X34, правка S1a)». На файл ссылаются
  `before-after.tsv:44` и шапка `facts-demo-webinar-okoshko.yaml`.
- Д-text-2: буквы базы site переведены в те же короткие адреса, что в `02-strategy-messaging/examples/` («site H» →
  «site 07», «site I» → «site 08/01»), плюс «site G» → «site 06»; `owner` файлов правил этой зоны — `text/<папка>`.
- Д-site-1: `status: draft-phase-1` в двух файлах text оставлен как есть.

## Проверки

- Разбор: 18 YAML читаются, пути данных сверены с `HEAD`; `copy-deck.schema.json` проходит метасхему Draft 2020-12;
  `before-after.tsv` — 541 строка по 8 колонок.
- `scripts/tests/smoke.py --only text` — PASS 24, FAIL 0 (в составе: `copy_lint.py --selftest`, `claims_check.py
  --selftest`, `copydeck.py --selftest`, `copydeck.py before-after --check`, `run_checks.py` по всем примерам,
  `chain_inputs.py --selftest`, `validate_facts.py`, `validate_meaning.py`, `validate_voice.py --selftest`).
- Сверка примеров «до → после» (`claims_check`, `copy_lint`, `copydeck check`, `validate`, `export` на 7 deck): коды
  выхода равны, выводы равны, кроме одной строки `facts.md` (см. `missing[].what` выше). `validate_facts.py` — PASS 76,
  FAIL 0.
- Читатели вне `scripts/text`: `claude-design/dc_texts.py --selftest` — OK; `claude-design/mockup_checks.py selftest` —
  OK; `creative/marketing_audit.py --selftest` — OK; `site/build_profile.py --check` и `--selftest` — OK.
- `scripts/maint/sync_check.py` — генераторы OK 17, FAIL 0, находок 0; `fixture_gen.py build --all --check` — совпадает;
  `scripts/creative/spec_check.py canvas-map` — error 0, warning 0.
- `scripts/maint/accept.py --base 1e0cd2a --masks-file …/Д-text-1.masks` — под масками 20 файлов: разбор 19 (схем — 1),
  находок 0, следы 0; строка «маски» — FAIL: вне масок 353 файла на момент прогона — правки соседних зон в том же дереве
  и отчёты `reports/`; машинных файлов базы text из папок 07–10 среди них нет.
- Все прогоны повторены после последней правки зоны; упавших прогонов в чужих файлах не было.

## Вопросы

1. `91-videos/digests/<id>.md` → `[V:<id> мм:сс]` (папки `91-videos` в скилле нет, метку `[V:…]` описывает README базы):
   подтвердить форму для колонки `rule_ref` и списков `sources`.
2. `rule_ref` снятых слотов — «`examples/ru-*.yaml#секция/слот (снят)`»: адрес ведёт в файл примера, где слота уже
   нет; оставить так или вести на `10-templates-recipes/02-examples-ru.md`?
3. `owner` файлов правил — `text/<папка>`, `x-owner` схемы — `text · 10-templates-recipes`: оставить папку или
   сократить до `text`?
4. Короткие адреса в заметках примеров («01 §8», «02 §9», «03 §2») — дополнять до «text 04/01 §8» в зоне данных или
   оставить текстовой зоне?
