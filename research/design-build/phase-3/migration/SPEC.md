# Спецификация переноса — часть «Содержимое» (агент A, 26.09.2026)

Вход: `../SKILL-MAP.md` (источник правды раскладки), `../../DECISIONS.md` (Р-номер = строка), SYNTHESIS §3, §5, §6.9, §10, §12,
свежий инвентарь `../../freeze/inventory/`, манифест заморозки `../../freeze/manifest.tsv.gz`, выжимки Ф2. Выход — файлы этой папки:

| файл | что это |
|---|---|
| `manifest-rules.yaml` | упорядоченные правила: содержимое баз, калибровка, журнал (§2) |
| `rules_eval.py` | применяет правила к замороженной базе и журналу → `expected-content.tsv`; с `--scan` — сканы; модуль для `migrate.py` (§3) |
| `expected-content.tsv` | ожидаемый состав: копии и псевдонимы с местом, purpose, основанием, байтами, токенами, sha256 |
| `scan-rules.tsv` | каждое правило: действие, основание, сколько файлов, байт, токенов |
| `scan-handoff.tsv` | исполняемый код и сопутствующее, которое решает агент B (266 файлов) |
| `scan-open.tsv` | файлы открытых пунктов (§10) с ценой |
| `scan-links.tsv`, `scan-links-examples.tsv`, `scan-rewrites.tsv` | базовые числа ссылок; примеры по категориям; все 2 026 токенов, которые перепишутся |
| `scan-identifiers.tsv`, `scan-fields.tsv`, `scan-secrets.tsv` | имена баз вне путей; поля машинных файлов; секреты (пусто) |

Воспроизвести: `python3 rules_eval.py --scan` (≈ 20 с; база только читается). Базовые числа ниже — прогон 26.09 после заморозки
(`freeze.py --verify` должен давать 0 изменений). Журнал `_skill-build/` живой: его строки в `expected-content.tsv` меняются с каждым
новым файлом сборки, содержимое баз — нет.

## 1. Итог в цифрах

Файлы / МБ / токены Opus 5.5 (оценка калибровкой `count_tokens`). Ассеты, бандлы и бинарники — 0 токенов.

| часть | kb | raw-norm | build-input | ref-code | asset-min | code-data | calibration | итого |
|---|---|---|---|---|---|---|---|---|
| ux | 75 / 6,73 / 1 949K | 1 / 0,18 / 61K | 1 / 0,04 / 16K | | | | | 77 / 6,96 / 2 026K |
| ui | 125 / 5,72 / 2 041K | | | | | | | 125 / 5,72 / 2 041K |
| site | 106 / 4,47 / 1 573K | 6 / 0,38 / 127K | 1 / 0,03 / 12K | | | | | 113 / 4,88 / 1 712K |
| text | 108 / 4,26 / 1 393K | 7 / 0,20 / 70K | 1 / 0,05 / 19K | | | | | 116 / 4,51 / 1 482K |
| creative | 110 / 3,40 / 1 246K | 6 / 0,18 / 61K | 1 / 0,05 / 19K | 1 / 0,04 / 19K | 23 / 1,19 / 0 | | | 141 / 4,86 / 1 344K |
| ai-media | 164 / 5,01 / 1 904K | 11 / 0,09 / 33K | | | | 26 / 0,11 / 40K | | 201 / 5,21 / 1 977K |
| blender | 319 / 6,20 / 2 428K | 8 / 0,19 / 72K | 1 / 0,01 / 6K | 174 / 1,46 / 654K | 10 / 0,91 / 0 | 1 / 1,62 / 0 | | 513 / 10,39 / 3 159K |
| claude-design | 60 / 0,95 / 343K | | | | | | | 60 / 0,95 / 343K |
| калибровка | | | | | | | 41 / 15,40 / 0 | 41 / 15,40 / 0 |
| **итого в скилл** | 1 067 / 36,73 / 12 878K | 39 / 1,22 / 423K | 5 / 0,19 / 71K | 175 / 1,50 / 673K | 33 / 2,11 / 0 | 27 / 1,72 / 40K | 41 / 15,40 / 0 | **1 387 / 58,87 / 14 084K** |

Ещё: 4 псевдонима (побайтные дубли, §7.1) без копии; журнал `research/design-build/` — 103 файла, 4,1 МБ, ≈ 1,6 млн токенов на момент
прогона (растёт вместе с `_skill-build/`); код — 266 файлов переданы агенту B (`scan-handoff.tsv`, из них взятое решит `tools-map.tsv`).

Сверка с оценками: текст kb ≈ 14,1 млн токенов против 14,5–16 млн SYNTHESIS §3.5 с кодом (код B добавит ≈ 1,5–2 млн — вписывается).
Объём шаблона — выше принятого (Р96: ≈ 45–50 МБ, ≈ 1,3–1,5 тыс. файлов): содержимое 58,9 МБ + журнал ≈ 4 МБ + код B ≈ 3–5 МБ ≈ 66–68 МБ,
≈ 1,7 тыс. файлов; разница — калибровочный набор 15,4 МБ (Р107: 3D оригиналами, размер не ограничиваем). На решение — §10 п. 1.

## 2. Формат `manifest-rules.yaml`

- Заголовок: `roots` (источник, шаблон, `skill` = `.claude/skills/design-deep-dive`, `journal` = `research/design-build`), `bases`
  (папка → имя без `-research`), `inventory` (классы по умолчанию, служебные папки, мусор, запретное, файлы-инструкции — справочно;
  действует код `inventory.py`), `purposes` (8 значений из брифа).
- Два упорядоченных набора, в каждом **первое совпадение решает**: `rules` — всё в `*-research/` и калибровка (73 правила, покрывают
  все 58 156 файлов манифеста; файл без правила — ошибка), `journal` — всё в `_skill-build/` (8 правил). Файл `_skill-build/` проходит
  оба набора: калибровка получает место в `assets/`, остальное — только журнал.
- Поля правила: `id`; `match` — glob или список glob от корня app-design (`**` — любое число сегментов, `*` и `?` — внутри сегмента,
  `{a,b}` — варианты); `class` — условие на класс `inventory.py` (prose, data, code, root-doc, tool, asset, bundle, junk, service,
  forbidden, other); `when: symlink` — только симлинки; `action`; `dest`; `purpose`; `why`; `note`; `open`; `alias_of`; `dedupe`.
- `action`: `take` — копировать в `dest`; `skip` — не переносить; `handoff` — исполняемый код, место и судьбу решает `tools-map.tsv`
  (агент B); `alias` — побайтный дубль взятого файла `alias_of`: не копируется, ссылки на него ведут к канону, в `path-map.tsv` —
  строка «старый путь → место канона»; `none` — не содержимое скилла (файлы журнала вне калибровки).
- `dest` — от корня шаблона, подстановки `{skill}`, `{journal}`, `{base}`, `{path}` (путь внутри базы), `{rest}` (путь после
  буквального префикса `match`), `{name}`. По умолчанию: `rules` — `{skill}/kb/{base}/{path}`, `journal` — `{journal}/{rest}`.
- `why` — Р-номер, раздел SKILL-MAP или SYNTHESIS. Без решения — `why: open` и блок `open` (`question`, `recommend`, `alt`, `ref`);
  текущее `action` открытого правила = рекомендация агента A. Сменить решение — поменять `action` и `why` на Р-номер.
- `dedupe: true` (механизм есть, в правилах не включён): копия, побайтно равная взятому файлу другого правила, становится псевдонимом.
  Для исходников дорожек blender отказались: рвёт относительные импорты внутри деревьев `KB/08-pages`, `SD/pages`.

Порядок правил (`rules`): страховка (запретный кэш cd, симлинки, файлы-инструкции) → исключения из «без ассетов» → мусор (класс
junk) → код агенту B → данные кода → отобранное из `99-raw` → тематика «не берём» по решениям → открытые пункты → служебное баз →
калибровка → умолчания по классу (`d-root-docs`, `d-kb`, `d-skip`).

**Совмещение с `tools-map.tsv` (для агента C).** Строка `tools-map.tsv` на точный путь источника главнее правил содержимого (её
`verdict` и `dest`). Файл под правилом `handoff` без строки в `tools-map` — ошибка «код не учтён». Строка `tools-map` на файл, который
правила содержимого берут в kb, допустима только с тем же `dest` или явной пометкой в `notes` — иначе конфликт в отчёт. `path-map.tsv`
= копии содержимого + копии журнала + копии `tools-map` + псевдонимы (`alias` и `dup-of` B), с sha256 источника.

## 3. `rules_eval.py`

- Читает правила, манифест заморозки (пути, байты, sha256 базы) и `_skill-build/` на диске (sha256 считает сам; временные папки
  `phase-3/migration/.staging*` и симлинки не обходит). Класс каждого файла базы считает `inventory.classify` с тем же чтением текста,
  что `inventory.walk` (итоги по умолчанию сходятся со срезами инвентаря). Токены — `inventory.tokens` по классу.
- Пишет только `expected-content.tsv`: `source, dest, purpose, why, bytes, tokens_est, sha256, kind, rule, class` (сверх брифа — `kind`
  = copy | alias, `rule`, `class`; у псевдонима `purpose` = alias, `dest` — место канона, `tokens_est` = 0); строки — копии
  содержимого, копии журнала, псевдонимы; сортировка по `dest`. С `--scan` — ещё
  `scan-*.tsv` рядом. Итоги по базам и purpose — в stdout.
- Падает (SystemExit) при: файле без правила, коллизии мест назначения, псевдониме без взятого канона или с другим sha256, ошибке
  формата правила.
- API для `migrate.py`: `load_rules`, `evaluate` (список решений), `new_places` (источник → новое место; содержимое главнее журнала),
  `dir_new_place`, `resolve_old`, `file_links` (токены с позициями), `rewrite_token`, `new_resolve`, `new_layout_exists`, `link_scan`;
  `--derive-blender-sources` — воспроизводит список правила `bl-tracks`.

## 4. По базам

Общее для всех: корневые `README.md`, `PLAN.md` (Р89), `CONTRADICTIONS.md` и тематика `NN-*` — классы prose, data, code, root-doc
1:1 (SKILL-MAP §2.1); `90-sources/`, `91-videos/`, `99-raw/` кроме отобранного — нет; ассеты, бандлы, мусор, симлинки — нет;
`99-raw/tools/` — агенту B, из него `bin/`, `models/`, `.locks/` — окружение, не в git (Р55, Р59, Р90). `skills-map.md` site, text,
creative — не берём (SKILL-MAP §2.1). Всё «к разбору» ложится в `kb/<база>/99-raw/<старый путь>`.

**ux** — kb 75 файлов (корневой `00-glossary.md` — тоже). Сверх умолчания ничего не снимаем. Из `99-raw`: `reports/wave4-X-audit.md`
(Р50: §2.1 — таблица канонов 54 строки нормой; 61K), `handoff-to-ui-research.md` (вход сверки ux ↔ ui, аналог handoff-to-neighbours;
открытый пункт, берём; 16K). Ассетов нет. B: 10 файлов `99-raw/tools/` (из них по SYNTHESIS §4 берётся `checklist_export.py`).

**ui** — kb 125. При переносе ничего не снимаем: `14-recipes/examples/audit/` (≈ 0,29 млн ток.), листинги `09/04` §4–§6 и лишний
глоссарий убираются при уборке (Р76 п. 21). Из `99-raw` — ничего: отчёта X у ui нет (аудит — `wave4-Q-*`); пара «дефолт против брифа»,
предложенная выжимкой, лежит в `99-raw/cache/measurements/generated/pages/` — `cache` не переносится (SKILL-MAP §5), числа из неё
уже в 12/02 §5. B: 10 файлов `99-raw/tools/` (ui_audit, color, measure_ui, build_reference_tokens, check_links…).

**site** — kb 106 (с `pages.csv` — Р66, `crosswalk.tsv` — источник правды, Р76 п. 20; с четырьмя схемами v0/v0.9 — открытый пункт).
Не берём: примеры v0/v0.9 — `01-foundations/site-brief.example.yaml`, `04-blocks/examples/**`, `06-multipage-ia/examples/**`, 7 файлов,
71K (Р76 п. 19); проекция в Kimi — `01-foundations/site-brief.kimi-map.tsv` и `10-…/examples/*/brief.kimi.home.yaml` ×3, 24K
(открытый, не берём). Из `99-raw`: `reports/wave4-X-audit.md` (реестры С-, Д-, §9.3; 74K), `notes/triad-contract-2026-09-24.md` (контракт
тройки; 16K), `experiments/K/02-ux-profile/ac-profile.tsv` (246 решений по AC-*; 5K) — всё Р66; `handoff-to-neighbours.md` (вход
сверки); `prompts/_common.md` (таблица «Кто чем владеет», открытый, берём); README опытов K/02, K/03 (открытый, берём). B: 29 файлов
`99-raw/tools/` (с README и `node/package.json`), `K/03-gates-v1/run_axe_targets.py`, `K/02-ux-profile/build_profile.py` (Р66).

**text** — kb 108. Не берём: `03-corpus-measured/measurements.tsv` и `corpus.tsv` — 2,34 МБ, ≈ 1,22 млн ток. (Р32). Из `99-raw`:
`notes/temp-vocabulary-v0.yaml` (читают 4 утилиты, Р33), `reports/wave4-X-audit.md` (§6 канон дублей, §7 К1–К31; Р34),
`handoff-to-neighbours.md`; README пяти папок опытов (открытый, берём; на `I/04-chain-manual/README.md` 10 ссылок). Копия контракта
тройки `99-raw/notes/triad-contract-2026-09-24.md` — псевдоним копии site (побайтно равны). Факты `99-raw/experiments/E/facts-demo-*`
не равны копиям в `10/examples/facts/` — не псевдонимы, ссылки на них уйдут в уборку. B: 20 файлов `99-raw/tools/`, 7 скриптов опытов
(Р33), `J/08-examples/run_checks.py` (без решения).

**creative** — kb 110. Не берём: `06-effects-catalog/lab/**` (212 файлов, из них 181 текстовых — 165K; Р39); данные
`03-live-sites-measured/` (`sites.csv` и записи, 32 текстовых — 97K; Р39; md README, 01, 02 остаются). Открытый, берём:
`01-…/drafts-for-site/site-brief-creative-fields.yaml` (11K). Из `99-raw`: `reports/wave4-X-audit.md` (§2, §9), `prompts/_common.md`
(вторая нумерация «решений заказчика»), `handoff-to-neighbours.md` — SKILL-MAP §2.4; `experiments/J/04-light-pass/src/scene.js` —
исходник бандла L2 (Р76 п. 17); README четырёх папок валидаторов (открытый); копия контракта тройки — псевдоним. Минимальные ассеты
(Р41): `10-recipes/examples/_shared/fonts/**` (10 woff2 + 5 LICENSE), `l2-zveno/img/*.webp` (7), `l2-zveno/js/three-scene.js` (бандл) —
23 файла, 1,19 МБ; `img/render.log` — мусор. B: 25 файлов `99-raw/tools/`, 7 валидаторов (Р37: spec_check, compat_check, ad_check,
recipe_check, registry_check, validate_stack, idle_probe).

**ai-media** — kb 164 (шаблоны `10-web-integration/pages/` и демо — кодом и описанием, без ассетов, Р76 п. 14). Не берём: 63 карточки
моделей `03-image-models/models/**`, `04-video-models/models/**` (160K) и `13-routing-matrix/routing.v0.yaml`, `routing.v1.yaml`
(41K) — Р54; журналы `14-recipes/examples/demo-landing/measure/**/*.json` (99K; открытый, не берём); `brand/forest-roast.cube` — класс
other, не берётся. Из `99-raw`: `reports/wave4-X-audit.md` (SKILL-MAP §2.4 «отчёты X целиком»; по выжимке — история поправок),
`phase5/README.md` (формат заданий генерации, Р54), README девяти папок модулей (открытый). Данные кода: `experiments/G/01-llm-svg-icons/
lucide-ref/` → `scripts/ai-media/data/lucide-ref/` (25 SVG, ISC; Р54), `experiments/P/04-ru-aggregators/genapi_prices_2026-09-23.json` →
`scripts/ai-media/data/` (цены Gen-API для `mp_client.py`; Р54, «прайс P/04»); `routerai_models.json` — нет (Р76 п. 15). B: 40 файлов
`99-raw/tools/` (с `tests/` и фикстурами, README, `node/package.json`), 14 модулей и шагов (Р54), 3 модуля `3D/` (без решения).

**blender** — kb 319. Не берём: данные регрессионного набора `11-evaluation-qa/regression/{manifest,results_baseline,results_negcheck}.json`
(Р58; протокол `04-regression-set.md` и README едут, скрипты — B); чанк `zveno/c-hybrid/js/chunks/chunk-2RVMEKYY.js` (SYNTHESIS §3.4).
Открытые, не берём: журналы витрины (`_shared/rules-journal.{md,json}`, `vote/ai-screen.{md,json}`, `verdict/index.html`,
`_shared/index-draft-s1.html`, `_shared/digests/01-references.md`, `03-web-delivery.md`; 219K; дайджесты 02 и 04 едут — на них ссылаются
нормы), данные страниц `keyboard/*/assets/data/**` (148K), замеры `09-web-runtime/examples/hero-lazy/probe/**/*.json` (41K), телефонный
набор hero-lazy (0,61 МБ ассетов). Из `99-raw`: `reports/wave4-X-audit.md` (§4 нормой, Р76 п. 23), `handoff-to-neighbours.md`; исходники
рецептов 13–17 — 165 файлов кода дорожек Z, CD, KB, SD, VD (1,37 МБ, 620K; Р57, Р76 п. 16; правило `bl-tracks`: без `out/`, `dist/`,
бандлов, отладки и запускалок итераций, из семейства версий — без версии или старшая) + `99-raw/notes/trial/RC-checks/*.py` (4, в т. ч.
`rc_vote_tally.py`); итоговые `HANDOFF-3.md` дорожек (открытый, берём); псевдонимы: `VD/01-build/velmora_v6_final.py` = `velmora.py`,
`CD/src/scene-v2.js` = creative `J/04-light-pass/src/scene.js`; README семи папок библиотек (открытый). Минимальные ассеты (Р57,
вариант А): `12-recipes/examples/01-hero-product/{case.glb,poster.avif,poster.webp}` + `dist/` (7 файлов, класс junk — берётся
исключением) — 10 файлов, 0,91 МБ. Данные кода: `99-raw/experiments/E/_assets/studio_small_09_1k.hdr` → `scripts/blender/data/`
(Р76 п. 18; 1,62 МБ — не «мал», как в SYNTHESIS §12). Шрифты витрины — копии creative, не берём (ассеты). B: 49 файлов `99-raw/tools/`,
17 утилит в тематике, 11 библиотек опытов (Р57).

**claude-design** — kb 60, с `06-design-process/` (24 файла: процесс под Claude Design, данные, брифы стенда S1/S2 — Р68). `kit`
целиком — B (→ `scripts/claude-design/kit/`). `99-raw/cache/` — запрещено (13 373 файла). Из `99-raw` — ничего. B: 11 файлов
`99-raw/tools/` (`mockup_checks.py`, `stand_page.py`, `shot_v3.py`, `lang_check.py` и утилиты сбора §4.2).

## 5. Калибровочный набор

`_skill-build/phase-3/calibration/frames/*` (40 кадров, 15,33 МБ) → `assets/calibration/frames/`, `index.yaml` →
`assets/calibration/index.yaml` (Р109). Подпапка `frames/` сохранена, чтобы утверждённый `index.yaml` не менялся: `file: frames/<кадр>`
разрешается от него, `rubric` уже записаны в раскладке шаблона (`kb/<база>/…` от корня скилла), `source.path` — провенанс в
непереносимом `99-raw`, не переписывается. Проверка: 84 ссылки `rubric` и 40 `file` → все находят файл в новой раскладке.
`_superseded/` (31 файл) — никуда; `tools/` набора, `BRIEF.md`, `REPORT.md`, `contact-sheet.html` — только журнал (кадры в журнал не
идут, поэтому картинки контактного листа в журнале не откроются — старые пути переводит `path-map.tsv`).

## 6. Журнал сборки

`_skill-build/` → `research/design-build/` (Р91, SKILL-MAP §2.6), файлы побайтно, без переписывания путей (старые пути переводит
`path-map.tsv`). Не едут: `phase-2/inventory/{files,links}.tsv`, `freeze/inventory/{files,links}.tsv` (4 файла, 28,3 МБ),
`freeze/manifest.tsv.gz` (3,0 МБ), `__pycache__` и `*.pyc`, временные папки `phase-3/migration/.staging*` (`.staging` — migrate.py,
`.staging-code` — агент B, с симлинками на базы), кадры калибровки (едут в `assets/`), `phase-3/calibration/_superseded/`; открытый —
`phase-3/migration/overlay/` (§10 п. 3). На момент прогона — 103 файла, 4,1 МБ (с этой спецификацией и сканами). `index.yaml` калибровки есть и в `assets/`, и в
журнале (68 КБ) — журнал остаётся зеркалом. `STATE.md`, `PLAN.md`, `NEXT-SESSION-PROMPT.md` переписываются до переноса (не часть этой
спецификации); `rules_eval.py` надо перезапустить после них — журнальные строки `expected-content.tsv` изменятся.

## 7. Переписывание путей

### 7.1. Правило для `migrate.py`

1. **Где.** Переносимые в kb файлы md, прочие текстовые (`.txt`) и машинные (YAML, JSON, JSONL, TSV, CSV и др. класса data), плюс
   `assets/calibration/index.yaml`. Код kb (эталонные html, css, js, py) и журнал не переписываются (SKILL-MAP §3; §2.6).
2. **Токены** — тем же кодом, что `inventory.py`: в md — ссылки `[..](..)`, пути в обратных кавычках (`looks_like_path`), голые пути
   с расширением (`PATHLIKE` по строке без ссылок, кавычек и URL — добавлено по SKILL-MAP §3); в остальных — `PATHLIKE` по строке без
   URL. Короткие адреса «NN/MM» и «<база> NN/MM» — не пути, не трогаем (структура сохраняется, 7 641 из них верны и после). Позиции
   токенов — `file_links` (строка, начало, конец); замены — справа налево.
3. **Разрешить** (`resolve_old`): папка файла → корень базы → корень app-design (+ абсолютные пути), как `inventory.resolve_path`, с
   запоминанием, какой корень сработал.
4. **Сопоставить**: новое место цели — `path-map` (содержимое главнее журнала; псевдоним → место канона; код → `dest` из `tools-map`);
   каталог — `dir_new_place` (каталог базы → `kb/<база>/<тот же путь>`; каталог, уехавший целиком, — его новое место; `_skill-build` →
   `research/design-build`). Цель без нового места — токен не трогаем (ссылка останется битой до уборки).
5. **Новый токен** (`rewrite_token`): сначала только смена сегментов `x-research` → `x` (SKILL-MAP §3); если так токен в новой раскладке
   ведёт к новому месту цели — берём его. Иначе путь пересчитывается от корня того же рода: папка файла → папка нового файла; корень
   базы → `kb/<база>`; корень app-design → `kb/`, корень скилла или шаблона. Якорь `#…`, `?…`, хвостовая пунктуация, `./` и `/` в конце
   сохраняются. Совпал со старым — не меняем.
6. **Разрешение в новой раскладке** (`new_resolve`; то же должен делать `check_links` шаблона): папка файла → `kb/<база>` → `kb/` →
   корень скилла → корень шаблона.
7. **Идентификаторы не трогаем никогда** — это следует из п. 2 и 5: меняются только сегменты путей, которые разрешились в файл или
   каталог с новым местом.

На замороженной базе правило даёт: 2 026 изменённых токенов (1 339 в обратных кавычках, 667 в машинных файлах, 20 голых путей в md;
все — `scan-rewrites.tsv` со старым и новым значением), 11 426 токенов остаются как есть; после замены все 13 452 ссылки на перенесённое
разрешаются в свою цель (моделирование по местам назначения: 0 расхождений). Пересчёт (не просто смена сегмента) — 18 токенов:
псевдонимы (контракт тройки из creative и text → копия site, `velmora_v6_final.py` → `velmora.py`), цели, уехавшие из `99-raw` в
`scripts/…/data/`, пути в `_skill-build/` → `research/design-build/`, абсолютные пути `/home/mm/…` в md.

### 7.2. Защищённые идентификаторы

Вхождения имён баз с `-research` в переносимом тексте (`scan-identifiers.tsv`):

| класс | ux | ui | site | text | creative | ai-media | blender | cd | всего | что делает перенос |
|---|---|---|---|---|---|---|---|---|---|---|
| в разрешимом пути | 338 | 45 | 1 024 | 154 | 354 | 96 | 142 | 46 | 2 199 | сегмент `x-research` → `x` |
| в пути, который не разрешается | 3 | 0 | 282 | 54 | 70 | 3 | 17 | 35 | 464 | не трогаем |
| похоже на путь, но не токен (без расширения в прозе) | 13 | 2 | 29 | 25 | 22 | 14 | 334 | 2 | 441 | не трогаем |
| неймспейс `org.<база>-research.*` | 0 | 289 | 0 | 0 | 103 | 0 | 0 | 0 | 392 | не трогаем |
| URN `urn:app-design:<база>-research:<схема>:<версия>` | 0 | 0 | 25 | 12 | 17 | 0 | 0 | 0 | 54 | не трогаем |
| URL `$id` `https://<база>-research.local/…` | 0 | 0 | 0 | 0 | 1 | 2 | 0 | 0 | 3 | не трогаем |
| ключ YAML (`ux-research:` и т. п.) | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 3 | не трогаем |
| проза (имя базы в тексте, строки кода) | 15 | 8 | 609 | 225 | 172 | 54 | 82 | 22 | 1 187 | не трогаем |

Шаблоны: `org.ui-research.llm` (243), `org.ui-research.modes*` (≈ 91), `org.creative-research.{reduce,fluid,css,meta}` (≈ 55, в т. ч.
`$extensions.*` DTCG); URN схем site (`site-brief`, `site-map`, `blocks`, `page-plan`), text (`meaning`, `facts`, `voc`, `voice`,
`copy-deck`, `message-hierarchy`), creative (`treatment`, `art-direction`, `motion-spec`, `recipe`, `refs-library`). Внутри разрешимых
путей идентификаторов нет (0 конфликтов): URN и неймспейсы без `/` и расширения не попадают под `PATHLIKE`, URL маскируются. `$ref` в
переносимых YAML и JSON: 961 внутренних (`#/…`) и 12 URN — ни одного файлового, то есть «`$ref` — строковое значение» из SKILL-MAP §2.3
на деле сводится к тем же токенам. Проверка после переноса: число вхождений каждого не-пути по каждому файлу не изменилось.

### 7.3. Поля машинных файлов

Разобраны все переносимые YAML, JSON, JSONL, TSV, CSV (0 ошибок разбора): 17 672 строковых значения в 354 полях с путями
(`scan-fields.tsv`). Значение целиком разрешается в файл — 2 594 (из них 2 049 — в перенесённое), в каталог — 1 107; ещё 1 984 пути
вложены в длинные значения. Главные поля с путями: `source_file` (crosswalk site — 457, YAML site — 265, `master-checklist.yaml` ux — 498), `rule_ref` (`before-after.tsv` text — 342 + 525 вложенных; ux — 9), ссылки примеров site (`blocks`, `events`, `budgets`,
`head_kit`, `lead_forms`, `legal_requirements`, `page_plan`, `site_map`, `brief`, `facts` — по 15–27), `stack_ref`, `doc`, `thresholds`,
`playbook`, `copy_slots_ref`, `voice_ref`, `motion_spec_ref` и др.

**Вывод: общее правило «разрешить → сопоставить» для всех строковых значений небезопасно.** 1 255 значений в 51 поле разрешаются,
не будучи путями: колонка `source_base` crosswalk site — 462 имени баз («text-research» — идентификатор базы, от корня app-design
разрешается в каталог), `variant: c-hybrid` blender (41 — имя варианта совпало с каталогом), `logo_link: "/"` (26 — корень ФС),
`vocabulary: site-research`. Безопасно — ровно то, что считает `inventory.py`: токены `PATHLIKE` (путь со слэшем и расширением) в строке
машинного файла. Список полей не нужен: значения-каталоги без расширения, которые действительно пути (`src`, `demo` creative,
`where_in_base` blender, `lexicon_dir`, `page_plans`, `path`), либо относительны внутри своей базы и остаются верными по построению, либо
ведут в непереносимое (`99-raw`, `lab/`). Абсолютные пути `/home/mm/…` в JSON-журналах blender (121) не трогаются и уходят в уборку.

### 7.4. Ссылки из переносимого — базовые числа

md и машинные файлы kb (зона переписывания), по базам — `scan-links.tsv`, примеры — `scan-links-examples.tsv`:

| категория | ux | ui | site | text | creative | ai-media | blender | cd | всего | после переноса |
|---|---|---|---|---|---|---|---|---|---|---|
| на перенесённое: файл | 2 458 | 1 575 | 2 645 | 1 224 | 773 | 1 160 | 969 | 90 | 10 894 | обязаны разрешаться |
| на перенесённое: каталог | 656 | 799 | 152 | 119 | 161 | 216 | 388 | 67 | 2 558 | обязаны разрешаться |
| — из них переписать | 325 | 45 | 955 | 133 | 314 | 90 | 123 | 41 | 2 026 | `scan-rewrites.tsv` |
| на код агента B: файл / каталог | 19 / 0 | 92 / 3 | 134 / 9 | 142 / 5 | 142 / 7 | 350 / 17 | 270 / 32 | 28 / 9 | 1 177 / 82 | разрешаются, если B взял цель |
| на непереносимое: файл | 181 | 212 | 293 | 346 | 253 | 934 | 594 | 35 | 2 848 | битые до уборки |
| на непереносимое: каталог | 35 | 66 | 127 | 98 | 105 | 277 | 211 | 30 | 949 | битые до уборки |
| не разрешаются уже сейчас | 548 | 881 | 792 | 610 | 637 | 1 115 | 1 541 | 236 | 6 360 | не больше |
| вне базы (абсолютные) | 3 | 0 | 0 | 6 | 0 | 0 | 1 | 0 | 10 | не больше |
| короткие адреса: верны / не найдены | 1 317 / 51 | 50 / 321 | 1 145 / 148 | 1 483 / 79 | 1 487 / 212 | 753 / 287 | 1 347 / 151 | 59 / 96 | 7 641 / 1 345 | верны все 7 641 |

Эталонный код kb (html, css, js, py) не переписывается: 231 ссылка на перенесённое (менять пришлось бы одну — комментарий в
`Z/lib/zpass.py` со ссылкой на `creative-research/…/scene.js`), 617 — на непереносимое (ассеты страниц), 470 не разрешаются. Базовые
числа — для отчёта, не для порога.

## 8. Проверки и базовые значения

| проверка | как | базовое значение |
|---|---|---|
| источник не менялся | `tools/freeze.py --verify` | 0 добавлено / удалено / изменено (58 156 файлов, отпечаток `2a31038c…`) |
| состав | staging ↔ `expected-content.tsv` + `tools-map.tsv` + overlay; `path-map.tsv` ↔ staging в обе стороны | содержимое 1 387 копий + 4 псевдонима; журнал — по прогону (сейчас 103); sha256 копии = sha256 источника (кроме переписанных файлов: для них sha256 источника и число замен) |
| нет запретного и мусора | правила `g-forbidden`, `g-cache`, `g-junk`, `kimi-research` | 0; мусор-класс допустим только в `asset-min` (7 файлов `dist/` blender, Р57) |
| нет файлов-инструкций | имена `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `SKILL.md`, `GEMINI.md`, `.mcp.json`, каталоги `.claude/`, `.git/` под `kb/`, `scripts/`, `assets/` и в журнале | 0 (при `j-overlay: skip`; вне `99-raw/cache` такие файлы есть в `99-raw/experiments` site и text — 15, не переносятся) |
| нет секретов | шаблоны `scan-secrets` (ключи, токены, приватные ключи, Bearer, присваивания) по всему переносимому тексту и журналу | 0; широкий поиск — только ложные (имена токенов дизайна, имена переменных, md5/коммиты) |
| ссылки на перенесённое | §7.4, разрешение в новой раскладке | 13 452 → 0 битых; переписано ровно 2 026 токенов (совпадение с `scan-rewrites.tsv`) |
| ссылки на непереносимое | §7.4 | ≤ 3 797 + ссылки на код, который B не взял |
| неразрешимые сейчас | §7.4 | ≤ 7 715 (6 360 + 10 + 1 345 коротких) |
| идентификаторы | §7.2, по файлам | счётчики неймспейсов (392), URN (54), URL `$id` (3), ключей (3) — равны |
| калибровка | `index.yaml`: `rubric` и `file` → файлы новой раскладки | 124 / 124 |
| места назначения | коллизии; совпадение с `.gitignore` шаблона (`credentials*`, `*.pem`, `*.key`, `.env*`, `*~`…); файлы > 5 МБ | 0 / 0 / 0; не-ASCII имена — 2, только в журнале (`phase-2/ux/ux-верх.md`, `ux-низ.md`) |
| размер и токены | итоги `rules_eval.py` по частям + код B | §1 |

«Битых ссылок не больше, чем до переноса» (SKILL-MAP §5) раскрыто тремя строками выше: ссылки на перенесённое — 0 битых, на
непереносимое и неразрешимые — не больше базовых. Пути `/home/mm` в `scripts/` и смоук — часть агента B.

## 9. Передача агенту B

Полный список — `scan-handoff.tsv` (266 файлов: `source`, `rule`, `why`, `bytes`, `class`, `sha256`). По правилам: `g-tools` — 194
(`99-raw/tools/` всех баз без `bin/`, `models/`, `.locks/`), `cd-kit` — 10, `bl-utils-thematic` — 17, модули и шаги опытов — 45.

| база | `99-raw/tools/` | прочее |
|---|---|---|
| ux | 10 | — |
| ui | 10 | — |
| site | 29 (с README, `node/package.json`) | `experiments/K/03-gates-v1/run_axe_targets.py`, `experiments/K/02-ux-profile/build_profile.py` (Р66) |
| text | 20 (с README) | Р33: `experiments/I/04-chain-manual/{check_intake,chain_inputs,make_skeleton,validate_any}.py`, `B1/03-schema-validate/validate.py`, `B2/01-schema-validate/validate.py`, `F/03-schema-lint/validate_voice.py`; без решения — `J/08-examples/run_checks.py` |
| creative | 25 (с README) | Р37: `experiments/I/01-schemas/{spec_check,compat_check}.py`, `A/01-art-direction-examples/ad_check.py`, `J/03-recipes-check/recipe_check.py`, `H/03-registry-check/registry_check.py`, `G/00-registry/validate_stack.py`, `J/02-l2-zveno/idle_probe.py` |
| ai-media | 40 (с README, `tests/` и фикстурами, `node/package.json`) | Р54: `experiments/A/04-image-marker-metrics/image_metrics.py`, `F/02-text-zone/text_zone.py`, `F/04-slop-metrics/composition_metrics.py`, `F/05-color/palette.py`, `F/06-series-metrics/{series_metrics,split_grid}.py`, `G/check_icons.py`, `B/14-landing-assets/split_recraft.py`, `M/06-og-marketplace/layout_check.py`, `N/04-update-dryrun/channel_diff.py`, `M/10-recipes-yaml/validate_recipes.py`, `99-raw/phase5/runs/MS-marea/loop_rife_bridge.py`, `phase5/runs/S4-capability/tools/{svg_sheet,vm_sheet}.py`; без решения — `experiments/3D/**/{glb_pipeline,compare_video,glb_probe}.py` |
| blender | 49 (с README, `node/`) | Р57: `experiments/D1/_lib/{d1lib,d1exp}.py`, `D2/_lib/d2lib.py`, `E/24-presets/presets.py`, `C1/10-scene-audit/scene_audit.py`, `C1/16-passport-asserts/passport_asserts.py`, `E/26-doc-snippets/{preflight_block,glb_lint_block}.py`, `F1/02-hero-variants/serve_br.py`, `H/_lib/animx.py`, `K/01-run-recipes/run_recipes.py`; утилиты в тематике — `03-bpy-api/snippets/*.py` (bpyx, agent_scene, hygiene + 2 теста), `12-recipes/examples/_kit/rk.py`, `11-evaluation-qa/regression/{run_set,make_manifest}.py`, `15-showcase/_shared/{img_metrics,sheet}.py`, `15-showcase/vote/{build_pairs,tally,vote_server}.py` + `vote/index.html`; §4.2 «не брать» — `15-showcase/_shared/{build_index,rules_journal}.py`, `15-showcase/gallery/build.py` |
| claude-design | 11 (`mockup_checks.py`, `stand_page.py`, `shot_v3.py`, `lang_check.py` и сбор §4.2) | `04-claude-code-native/kit/**` целиком (shot, diffshots, export, canvas.html, marks.js, `example/` с `canvas.json`) → `scripts/claude-design/kit/` |

Что важно знать B:
- **Копий утилит в `claude-design-research/06-design-process/stand/` нет** — там только md, `brief.yaml`, `fixtures.json` брифов S1/S2
  (остаются в kb). Копии `mockup_checks.py` и `stand_page.py` (Р62, Р68) лежат в `claude-design-research/99-raw/tools/`.
- **README утилит** `99-raw/tools/README.md` есть у ai-media, blender, creative, site, text (→ `scripts/<база>/README.md`, SKILL-MAP §1);
  у ux, ui, claude-design — нет.
- **Данные, которые читает код, уже размещены мной:** `scripts/ai-media/data/lucide-ref/` (для `check_icons`),
  `scripts/ai-media/data/genapi_prices_2026-09-23.json` (для `mp_client.py`), `scripts/blender/data/studio_small_09_1k.hdr` (для
  `gltf_diff.py`), `kb/text/99-raw/notes/temp-vocabulary-v0.yaml` (`VOCAB_PATH` copydeck, claims_check, copy_lint, copy_extract),
  `kb/site/99-raw/experiments/K/02-ux-profile/ac-profile.tsv` (выход `build_profile.py`), `kb/ai-media/99-raw/phase5/README.md` (формат
  заданий). Пути для `kbpaths` — из `expected-content.tsv`.
- **Данные модулей внутри папок опытов** (схемы `creative …/I/01-schemas/`, фикстуры самопроверок, `tests/fixtures`) правилами
  содержимого не берутся (`99-raw` — нет) — нужны коду → строкой `tools-map` с `kind=data`. `package-lock.json` в `99-raw/tools/node/`
  inventory считает мусором (правило `g-junk`); если нужен — строкой `tools-map` (она главнее, §2).
- **Эталонный код рецептов остаётся в kb**: `12-recipes/examples/*/{build,post,make_poster}.py`, `09-web-runtime/examples/**`
  (`build_scene.py`, `make_poster.py`, `hero.js`, `Hero.jsx`, `build.sh`), `15-showcase/_shared/code3d/**`, страницы витрины, исходники
  дорожек в `kb/blender/99-raw/experiments/…`. Они импортируют `rk`, `bpyx` и библиотеки `99-raw` — если B решит править их механически
  в kb, это строка `tools-map` с `dest` в kb.
- **Никогда не брать** файлы-инструкции: `text-research/99-raw/experiments/J/08-examples/templates/AGENTS.md` и `…/out/**/AGENTS.md`
  рядом с `run_checks.py`.
- **`check_links` в `scripts/maint/`** должен разрешать пути как `new_resolve` (§7.1 п. 6): папка файла → `kb/<база>` → `kb/` → корень
  скилла → корень шаблона; иначе проверка «после» не сойдётся с моделированием.
- Ссылки из kb на код: 1 177 на файлы и 82 на каталоги (§7.4) — перепишутся по `dest` из `tools-map`; для не взятого B — станут
  ссылками на непереносимое.

## 10. На решение

Цена — если выбрать альтернативу к рекомендации (МБ, токены); файлы — `scan-open.tsv`.

| № | пункт | рекомендация | цена альтернативы |
|---|---|---|---|
| 1 | **Объём выше принятого (Р96).** Итог ≈ 66–68 МБ и ≈ 1,7 тыс. файлов против ≈ 45–50 МБ и 1,3–1,5 тыс.: калибровка 15,4 МБ (Р107 — 3D оригиналами, без лимита), HDRI 1,6 МБ, исходники дорожек 1,5 МБ; текст kb 36,7 МБ — как в оценке. Затрагивает решение заказчика | принять, показать заказчику одной строкой | сжать кадры калибровки — против Р107 |
| 2 | **Каталоги в правиле путей.** SKILL-MAP §3 говорит «в реальный файл»; 2 558 ссылок md и данных ведут на перенесённые каталоги (`../ui-research/08-motion/`) | переписывать и каталоги (`dir_new_place`, §7.1) | +2 558 битых ссылок после переноса |
| 3 | **Overlay в журнале** (`j-overlay`): копия дала бы второй `.claude/skills/design-deep-dive/SKILL.md` внутри `research/design-build/` — Claude Code находит вложенные `.claude/skills` | не копировать overlay в журнал (он и так в шаблоне); проверку файлов-инструкций распространить на журнал | 4 файла, 8 КБ |
| 4 | `ux-handoff-ui` — handoff ux → ui как вход сверки | брать | не брать: −0,04 МБ, −16K |
| 5 | `site-common` — site `_common.md` («Кто чем владеет»; 9 ссылок) | брать | −0,06 МБ, −17K |
| 6 | `site-v0-schemas` — 4 схемы site v0/v0.9 (35 ссылок из README, PLAN, схем v1, `crawlers.yaml`, `head-kit.yaml`, `lead-forms.yaml`, text) | брать до сверки | −0,15 МБ, −63K, +35 битых |
| 7 | `site-kimi` — kimi-map и `brief.kimi.home.yaml` ×3 (Р80) | не брать | +0,08 МБ, +24K |
| 8 | `cr-site-brief-fields` — черновик полей creative для site-brief (вхождение в v1 не проверено) | брать, судьбу решит сверка | −0,03 МБ, −11K |
| 9 | `am-demo-measure` — JSON-журналы замеров демо-лендинга | не брать | +0,20 МБ, +99K |
| 10 | `bl-showcase-journals` — журнал правил, ИИ-отсев, `verdict/index.html`, черновик индекса, дайджесты 01, 03 | не брать | +0,64 МБ, +219K |
| 11 | `bl-showcase-page-data` — данные страниц клавиатуры | не брать | +0,28 МБ, +148K |
| 12 | `bl-hero-lazy-probe` — замеры эталона hero-lazy | не брать | +0,08 МБ, +41K |
| 13 | `bl-hero-lazy-phone` — телефонный набор ассетов hero-lazy | не брать (вариант А уже 0,91 МБ) | +0,61 МБ |
| 14 | `bl-track-handoff` — итоговые `HANDOFF-3.md` пяти дорожек: карта финальных исходников рецептов 13–17 | брать | −0,07 МБ, −26K |
| 15 | `g-module-readmes` — README 27 папок опытов, чьи модули уходят в `scripts/` (21 ссылка) | брать «к разбору» | −0,15 МБ, −57K |
| 16 | `text-run-checks`, `am-3d` — код без решения | решает B в `tools-map` | — |

Факты, расходящиеся с текстами решений (действий не требуют): в бриф-формулировке «копии утилит в `06-design-process/stand/`» — там
кода нет (§9); Р97 «файлы-инструкции есть только в `99-raw/cache`» — ещё 15 в `99-raw/experiments` site и text (не переносятся, правило
`g-instructions` страхует); HDRI 1,6 МБ, а не «мал» (SYNTHESIS §12 п. 18); пара ui из `99-raw/cache/` взята быть не может (SKILL-MAP §5).
