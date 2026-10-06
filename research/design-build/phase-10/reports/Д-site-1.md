# Д-site-1 — машинные файлы базы site: `02-site-types`, `09-ai-generation-evaluation`

Коммит начала — `1e0cd2a`. Список зоны — 4 файла, тронуты все 4 пакетом точных замен (171 замена в четырёх пакетах
`kbpatch.py`). Маркеры зоны: 295 → 11; целевые классы `raw`, `kimi`, `k3`, `research`, `process`, `decision`, `plan`,
`words` — 0; остаток — обозначения уровней и серьёзности и одно значение перечисления. Ключи, id, перечисления, числа,
пороги, порядок записей не менялись; число колонок TSV — 9 у всех 710 строк. Git — только чтение. Пути ниже — от
`.claude/skills/design-deep-dive/kb/site/`, утилиты — от корня скилла.

## Файлы

Маркеры — сумма по классам `kbscan.py` с классами `--extra`; «→» — до и после.

| файл | что сделано | маркеры |
|---|---|---|
| `02-site-types/crosswalk.tsv` | колонка `source_file`: путь сырья → название источника без пути — «временный словарь text v0» (132 строки), «предложения text к словарю site» (13 строк); у тех же 13 строк `source_section` «„Для X“, строка 19 (предложения к словарю)» → «предложения к словарю»; колонка `note` (82 строки): буква исполнителя → адрес базы (`site 03/01 §4`, `site 04`, `site 06` …), «предложение B1 / B2 / E / G text» → «предложение text», «(PLAN, поправка 9)» снято. Строк 710, колонок 9 | 160 → 0 |
| `02-site-types/vocabulary.yaml` | шапка, `vocabulary`, `owner` — без суффикса исследования; `owner`, `fields`, `def`, `foreign_prefixes`: буквы исполнителей → адрес базы, «волна N», «(v0) / (v1)», «черновик B для C», время заметки «12:40», «предложение C:» сняты (числа выборки остались); «решение заказчика 10 / 11 / 15» сняты, норма осталась; «контракт тройки §3 п.3» → `common/owners.md §Форматы обмена`; `ref` уровней: `../creative/PLAN.md …` → `../creative/01-creative-direction/ambition-levels.yaml`; `ux-research`, `ui-research` → `ux`, `ui`; источник формы «сайт-референс W3» → «сайт-референс». Строк 652 | 29 → 4 |
| `09-ai-generation-evaluation/ai-landing-markers.yaml` | штамп шапки и журнал правок сняты (остался комментарий о разборе, чек-листе и сверке `checklist_export.py`); `owner` — `site (09-ai-generation-evaluation)`; прежний исполнитель макета — вывод без имени: проверки `LOOK-*`, `HON-*`, `M-NAV`, `E-LOW-DOM` → `mockup_checks.py`, статьи его базы → `claude-design 06/04 §3`, `06/05`, модель → «LLM-вёрстка», «другой генератор»; пути `99-raw` → адрес нормы в базе или вывод без пути; id опытов и буквы в метках `[проверено: …]` сняты, выборка и числа остались; «решение заказчика 15», «поправка PLAN №…» сняты (четыре записи `sources` из одного номера — строкой целиком, две слиты с соседней записью-адресом); `validate.py E` → `site_validate.py`. Строк 1130 → 1121 | 100 → 5 |
| `09-ai-generation-evaluation/site-rubric.json` | `owner` → `site`; блок `changelog` снят (код не читает); «демо K3» → «демо LLM-вёрстки», «(text I/03)» → «(text 09/03)»; «(живая фаза, отчёт K §5)» → «(живая фаза)»; «по методике P» → «по методике site 07/04». Строк 733 → 726 | 6 → 2 |

По классам (вся зона): `raw` 154 → 0 · `kimi` 27 → 0 · `k3` 9 → 0 · `research` 22 → 0 · `process` 36 → 0 ·
`decision` 16 → 0 · `plan` 3 → 0 · `words` 1 → 0 · `journal` 1 → 1 · `letters` 35 → 10.

Соответствие букв исполнителей адресам базы (проверено по папкам `kb/site/NN-*`): A — `site 01`, B — `site 02`,
M — `site 02/03`, C — `site 03`, E — `site 04`, F — `site 05`, G — `site 06`, H и P — `site 07`, I — `site 08`,
K — `site 09`, J — `site 10`. Адрес статьи ставился, когда раздел найден в файле: `site 02/01 §6`, `site 03/01 §4` и
`§4.1`, `site 03/02`, `site 03/03 §2.2`, `site 05/01 §6.3`, `site 07/04`, `site 10/02`, `10/03`, `text 02/02`, `text 09/03`.

## Остаток маркеров

- `02-site-types/vocabulary.yaml:344`, `:353`, `:403` — `letters`: «(H1)», «(H2)» — уровень заголовка в названии слота.
- `02-site-types/vocabulary.yaml:502` — `letters`: «(L2)» — уровень амбиций подачи.
- `09-ai-generation-evaluation/ai-landing-markers.yaml:252`, `:334`, `:394`, `:474`, `:988` — `letters`: «(B)», «(S)» после
  кода ворот `SG-CONTENT-05 / 06` — серьёзность по шкале `severity_scale` файла, не исполнитель.
- `09-ai-generation-evaluation/site-rubric.json:495` — `letters`: «(D)» — серьёзность.
- `09-ai-generation-evaluation/site-rubric.json:6` — `journal`: `"status": "draft-phase-1"` — значение перечисления
  статуса рубрики (`draft-phase-1 → calibrated → stable`), общее с `text/09-ai-generation-evaluation/copy-rubric.yaml:16`
  и `copy-checklist.yaml:16`; меняется только вместе с text — вопрос 2.

## Ключи и значения, которые читает код

- `crosswalk.tsv`, колонка `source_file` — читают `scripts/site/vocab_lint.py` (`lint_crosswalk`: часть ключа повтора
  строки `source_base, source_file, source_vocab, source_term, namespace, our_id`) и `scripts/site/plan_to_assets.py`
  (`endswith` имени плана ассетов и `asset-spec.schema.json` — только у строк `source_base = ai-media`). Все 145 путей
  сырья стояли у строк `source_base = text`: `plan_to_assets.py` их не читает, ключ повтора остался уникальным (повторов
  0 до и после). Строки ai-media изменены только в `note` — её код читает лишь для подсказки `none`.
- `crosswalk.tsv`, колонка `source_section` — `plan_to_assets.py` читает начала «§8 (page.media_class)»,
  «§8 (page.page_type)», «role.page_type» у строк ai-media: не тронуты.
- `ai-landing-markers.yaml`: `markers[].id` — `scripts/site/checklist_export.py`; `threshold` у `AIL-06` и `AIL-07` —
  `scripts/claude-design/mockup_checks.py` регулярным выражением (`hero ≥ N %`, `CV длины текстов карточек < N`): не
  тронуты. Ключ `crosswalk_external` код не читает, но он — якорь `kb/common/canon.tsv:327` и статей creative: имя
  ключа прежнее. Ключей и id с именем прежнего исполнителя макета в файле не было — имя стояло только в значениях.
- `vocabulary.yaml`: код читает `namespaces.*.values[]` (`id`, `status`, `replaced_by`, `kind`, `class`, `genre`,
  `priority`, `family`, `serves`, `fact_kinds`, `layout_family`), `ref_prefixes`, `id_pattern`,
  `id_pattern_exceptions` — не тронуты. Значение `vocabulary:` (`site-research` → `site`) и поля `owner`, `fields`,
  `def`, `detect`, `source`, `ref`, `foreign_prefixes` код не читает (поиск по `scripts/`).
- `site-rubric.json` код не читает (читатель — агент-судья). Ключ `five_second_test.people.phase` со значением «живая
  фаза» — шаг процедуры базы (`03-expert-review-and-judge.md`, шаг 9), не фаза исследования: оставлен.

## Производные

В список зоны не входят, руками не правились; счёт `kbscan.py`:
- `09-ai-generation-evaluation/site-checklist.yaml` — 125 маркеров (`raw` 24, `kimi` 23, `research` 26, `process` 27,
  `decision` 18, `letters` 7): источник — `09-ai-generation-evaluation/02-site-checklist.md`, сборка
  `scripts/site/checklist_export.py`.
- `09-ai-generation-evaluation/ux-marketing-profile.tsv` — 177 (`decision`): источник — строки данных внутри
  `scripts/site/build_profile.py` (зона кода), сборка той же утилитой; `ac-profile.tsv` — 0.

## Для фикстур

`fixture_gen.py build --all --check` — совпадает: правки зоны фикстуры не меняют. Попутно: комментарий «секции — роли
temp-vocabulary-v0» в `scripts/tests/fixtures/input-landing/files/site/promo/hierarchy/home-problem-aware.yaml:5` и
`…/package-landing-defects/files/site/promo/hierarchy/home-problem-aware.yaml:5`.

## Для текстов

- `02-site-types/02-vocabulary-and-crosswalk.md`: §5.1 (строки 227–232) — «файл генерируется скриптом
  `99-raw/experiments/B/02-crosswalk/build_crosswalk.py` — руками не править»: утилиты в скилле нет, таблицу сверяет
  `scripts/site/vocab_lint.py --check-crosswalk`; §5.2 (236–251) — источники с суффиксом исследования, строка
  «kimi-research 22» (в таблице таких строк нет: есть `jack-roberts` 10 и `claude-design` 9), итог «685 строк» (сейчас
  709: text 234, ai-media 213, hallmark 85, tilda 53, ui-ux-pro-max 34, schema.org 23, relume 18, blender 16,
  unbounce 13, jack-roberts 10, claude-design 9, ux 1); строка 351 — путь временного словаря (в таблице источник назван
  «временный словарь text v0», предложения — «предложения text к словарю site»).
- `02-site-types/README.md:11–12` — «журнал — `changelog`» у словаря (ключа в файле нет), «генерируется» у таблицы.
- `09-ai-generation-evaluation/README.md:13`, `:16` — число строк: `ai-landing-markers.yaml` 1 121, `site-rubric.json` 726.
- `09-ai-generation-evaluation/03-expert-review-and-judge.md:307` — «(живая фаза, отчёт K §5)» ↔ `calibration.status`.
- Адреса, на которые теперь ссылаются файлы зоны, — сохранить при правке статей или поправить ссылку:
  `claude-design 06/04 §3 C`, `§3 D`; `claude-design 06/05 §3`, `§7`; `creative 08/02 §5.3`; `site 02/01 §6`;
  `site 03/01 §4`, `§4.1`; `site 03/03 §2.2`; `site 05/01 §6.3`; `site 07/01 «Частые ошибки» 9–10`; `site 07/02 §8`;
  `site 10/01 §12` (код `PL-N01`); `09/02 «Выжимка для агента» п. 14`; `common/owners.md §Форматы обмена`.

Соседям по данным:
- Д-site-2 — `07-seo-geo-performance-analytics/page-gates.yaml:143`, `:369`: «PLAN поправка 6» — та же норма, что у
  `AIL-43`; здесь адрес нормы — `09-ai-generation-evaluation/02-site-checklist.md «Выжимка для агента» п. 14`. Таблица
  букв → адресов выше — чтобы файлы базы site говорили одинаково.
- Д-creative-1 — `creative/08-uniqueness-anti-slop/cliche-registry.yaml:103`: комментарий о зеркале
  `crosswalk_external` с пометкой «S1 site, 2026-09-25»; имя ключа у site прежнее.
- Д-text-1 — `status: draft-phase-1` (вопрос 2).
- Зоне кода — попутно: `scripts/creative/recipe_check.py:5` (`../site-research/…` в докстринге),
  `scripts/site/ab_plan.py:2` (штамп «агент P, волна 2 site-research»), `scripts/site/ia_probe.py:58`
  (`site-research structure probe` в `USER_AGENT`), `scripts/text/last-run.txt` (журнал прогона).

## Файлы к снятию

В зоне — нет.

## Вопросы

1. **145 строк `crosswalk.tsv`** (2–133, 223–235) описывают соответствие временному словарю text и предложениям к
   словарю — источникам, которых после снятия `99-raw` в базе нет; файл заметок оркестратора text уже снят. 138 из
   них — `equal` с тем же id (термин источника равен нашему id): подсказку `vocab_lint.py` они не дают — id уже в
   словаре; 7 — `none` (шесть жанров text и `ux_role: meta`). Строки — данные, не снимал: источник назван без пути.
   Снимать ли строки — решение оркестратора (вместе с §5.2 статьи 02/02).
2. **`site-rubric.json:6` `draft-phase-1`** — оставить, переименовать вместе с рубриками text или снять «phase-1»?
3. **`validate.py E` → `site_validate.py`** (пять мест `ai-landing-markers.yaml`: `detect_codes.LNT`, `AIL-09`,
   `AIL-18`, `AIL-19`, `AIL-31`): утилита опыта жила в сырье, преемником назван `site_validate.py` (коды `PL-F*`,
   `PL-N01` в его докстринге). Нужен взгляд владельца кода site.
4. **Статьи базы прежнего исполнителя → `claude-design 06/05`**: три вывода («три скелета витрины», «fictional brand ≥
   3 из 15 сборок», «трёхколоночный прайсинг») в статье-преемнице дословно не найдены — адрес поставлен на статью о том
   же замере без номера раздела; «центр 5 из 13», «контент-баги 3 из 15», рамка браузера — в её §3.
5. **Две записи `sources` остались одной меткой** — `AIL-29` («[проверено: llms.txt у 20 из 69 …]») и `AIL-42`
   («[проверено: предотмечено у 2 из 10 …]»): id опыта снят, адреса статьи для чисел `AIL-42` в базе не нашёл.
6. **`crosswalk.tsv:708`** — «реферальная программа — кандидат в v1»: словарь уже версии 1, строка устарела по смыслу;
   буква снята, формулировку не менял.
7. `AIL-13`: подтверждение катящегося срока шло скриптом опыта (`deep_check.py` в сырье) — утилиты в скилле нет, в
   `detect.auto` записано «сценарием: перезагрузка и повторный визит».

## Проверки

- Разбор: `vocabulary.yaml`, `ai-landing-markers.yaml` — YAML читается (17 пространств, 445 id; 52 маркера, 20 строк
  `crosswalk_external`); `site-rubric.json` — JSON читается; `crosswalk.tsv` — 710 строк × 9 колонок, по колонкам
  изменено: `source_file` 145, `source_section` 13, `note` 82, остальные 0. Схем в зоне нет.
- `scripts/site/vocab_lint.py --selftest` — OK; `--check-crosswalk` — 709 строк, ошибок 0, предупреждений 1 (строка 461,
  `none` без причины — было и на `1e0cd2a`).
- `scripts/site/checklist_export.py --check` — совпадает; `scripts/site/site_validate.py --all` — error 0.
- `scripts/tests/smoke.py --only scripts/site` — PASS 28, FAIL 0. Читатели вне site (`mockup_checks.py`,
  `ad_check.py`, `recipe_check.py`, `claims_check.py`, `copy_lint.py`, `copydeck.py`, `validate_meaning.py`,
  `validate_voice.py`, `design_audit.py`) — PASS 19, FAIL 0.
- `scripts/maint/sync_check.py` — генераторы OK 17, FAIL 0. `scripts/maint/fixture_gen.py build --all --check` — совпадает.
- `kbscan.py --zone Д-site-1.tsv --extra …` — 295 → 11 (остаток — выше).
- `scripts/maint/accept.py --base 1e0cd2a --masks-file …/Д-site-1.masks` — под масками 4 файла: разбор 3 / 0 находок,
  следы 0, ссылки 0; строка «маски» — 271 файл других зон, работающих в том же дереве.
- Новые относительные пути в `sources` и `ref` проверены на существование вручную (8 путей `ai-landing-markers.yaml`,
  `ref` уровней в словаре, `common/owners.md`).
