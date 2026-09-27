# Ф4 — карта входов (узел IN)

Карта входов сверки баз: каждая строка реестров противоречий, таблиц канонов, «поправок к соседям», контракта тройки, владения
темами, решений заказчика баз, легенд меток и противоречий SYNTHESIS — одна строка `rows.tsv` с узлом, который её сводит. Узел
ставится по смыслу строки: межбазовая — в GL…JU, строка таблицы канонов — в CN (если тема не принадлежит тематическому узлу),
целиком внутри одной базы и уже решённая её реестром — `—`. Карту начал прерванный агент IN (26.09, файлы 22:26–23:10), довёл
агент «IN-доводка» (27.09) по файлам на диске (Р119): проверил источники и назначения, исправил и дописал недостающее.

## Файлы и запуск

| файл | что |
|---|---|
| `rows.tsv` | карта: 1 264 строки, 11 колонок (`row`, `src_base`, `src_kind`, `src_file`, `line`, `item_id`, `title`, `src_status`, `mentions`, `node`, `note`); ключ строки — `путь#item_id` |
| `assign.tsv` | узел и примечание по ключу строки — источник правды назначений (1 017 ключей). Для видов canon, owners, customer-decision, triad-*, legend узел по умолчанию задаёт `extract_rows.py` (`DEFAULT_NODE`); ключ в `assign.tsv` его заменяет |
| `manual-rows.tsv` | 5 строк мест без табличной структуры: абзац «Не править» отчёта X site §9.3 (2), таблица целей нажатия ux handoff §3 (1), разделы README claude-design «Соседние базы» и «Пробелы» (2) |
| `reading.tsv` | что читает агент узла — для `tools/budget.py`; ориентир, строки узла ведут к нужным местам сами |
| `in-drafts/` | черновики прерванного агента. `assign_spec.py` — генератор первого `assign.tsv`: правки доводки внесены прямо в `assign.tsv`, генератор отстал — не запускать. `budget.md`, `node_tables.md` — прежние таблицы бюджета (их заменяет раздел 4). `dump.tsv`, `registry-test.tsv`, `nodes-test/` — пробные данные. `in-trace.md` не открывался: по имени — след работы прерванного агента (Р119) |

Команды (из `research/design-build/phase-4/`, Python 3.13, только стандартная библиотека):

```
python3 tools/extract_rows.py              # пишет inputs/rows.tsv; повтор даёт тот же файл (md5 4c441f23…)
python3 tools/extract_rows.py --report     # счёт по источникам против заявленного
python3 tools/extract_rows.py --dump       # строки без узла (сейчас нет)
python3 tools/budget.py [--node TR]        # объём чтения и контекста узлов
python3 tools/registry.py check nodes/NN-XX.tsv    # схема строк узла, пути, source
python3 tools/registry.py merge            # nodes/*.tsv → registry.tsv
python3 tools/registry.py coverage         # строки карты с узлом, не названные ни в одном source
python3 tools/registry.py canon            # registry.tsv → kb/common/canon.tsv (пробы — с --registry и --out)
```

Правка назначения — строкой `assign.tsv` (ключ, узел, примечание), затем `extract_rows.py`. **Номера `IN-…` зависят от порядка
групп** (`GROUP_ORDER`): строка, добавленная в середину, сдвигает все следующие номера, а узлы ссылаются на номера. Сейчас номера
выпущены впервые; после старта GL карту можно менять только так, чтобы номера не сдвигались: новые строки — отдельной группой в
конце `GROUP_ORDER`, смена узла или примечания — через `assign.tsv` (номеров не меняет).

## 1. Счёт строк по источникам

Вход (a)–(i) — пункты исходного задания IN; «по узлам» — сколько строк источника ушло в каждый узел.

| вход | база | файл | строк | IN-… | по узлам | «—» |
|---|---|---|---:|---|---|---:|
| (a) | ux | `ux/README.md` | 77 | IN-0001…IN-0077 | GL 1, CM 1, ST 2, NU 5, TX 5, JU 1, CN 2 | 60 |
| (a) | ui | `ui/CONTRADICTIONS.md` | 49 | IN-0078…IN-0126 | GL 1, GT 2, CM 2, NU 10, VI 6, CN 1 | 27 |
| (a) | site | `site/README.md` | 61 | IN-0127…IN-0187 | GL 1, TR 21, GT 7, CM 1, ST 2, NU 3, TX 1, VI 2, CN 2 | 21 |
| (a) | site | `site/99-raw/reports/wave4-X-audit.md` | 17 | IN-0188…IN-0204 | GL 1, TR 7, GT 1, NU 1, TX 1, VI 1, JU 1, CN 1 | 3 |
| (a) | text | `text/CONTRADICTIONS.md` | 55 | IN-0205…IN-0259 | TR 9, TX 8, VI 2, JU 2 | 34 |
| (a) | text | `text/README.md` | 15 | IN-0260…IN-0274 | TR 4, TX 10, VI 1 | 0 |
| (a) | creative | `creative/CONTRADICTIONS.md` | 93 | IN-0275…IN-0367 | GL 1, TR 3, GT 13, NU 15, VI 25, JU 1, CN 3 | 32 |
| (a) | ai-media | `ai-media/CONTRADICTIONS.md` | 50 | IN-0368…IN-0417 | GT 2, NU 1, VI 1, JU 1, CN 1 | 44 |
| (a) | blender | `blender/README.md` | 61 | IN-0418…IN-0478 | GT 7, VI 2, JU 2, CN 2 | 48 |
| (b) | ux | `ux/99-raw/reports/wave4-X-audit.md` | 61 | IN-0479…IN-0539 | TR 2, GT 1, CM 5, ST 7, NU 5, TX 5, JU 4, CN 32 | 0 |
| (b) | site | `site/99-raw/reports/wave4-X-audit.md` | 51 | IN-0540…IN-0590 | GL 1, TR 17, GT 10, CM 1, NU 2, VI 4, CN 16 | 0 |
| (b) | site | `site/99-raw/reports/wave4-X-audit.md §9.3 (пометки, «Не править»)` | 10 | IN-0591…IN-0600 | JU 9, CN 1 | 0 |
| (b) | text | `text/99-raw/reports/wave4-X-audit.md` | 61 | IN-0601…IN-0661 | GL 1, TR 3, TX 8, VI 2, JU 2, CN 45 | 0 |
| (b) | creative | `creative/99-raw/reports/wave4-X-audit.md` | 33 | IN-0662…IN-0694 | GT 16, NU 3, VI 4, CN 10 | 0 |
| (b) | blender | `blender/99-raw/reports/wave4-X-audit.md` | 22 | IN-0695…IN-0716 | GT 3, VI 2, JU 1, CN 16 | 0 |
| (c) | site | `site/99-raw/handoff-to-neighbours.md` | 62 | IN-0717…IN-0778 | GL 1, TR 40, GT 11, CM 1, NU 1, TX 1, VI 5, CN 2 | 0 |
| (c) | text | `text/99-raw/handoff-to-neighbours.md` | 99 | IN-0779…IN-0877 | TR 54, GT 1, TX 25, VI 7, JU 3, CN 2 | 7 |
| (c) | creative | `creative/99-raw/handoff-to-neighbours.md` | 102 | IN-0878…IN-0979 | TR 14, GT 26, NU 19, VI 19, JU 1, CN 9 | 14 |
| (c) | blender | `blender/99-raw/handoff-to-neighbours.md` | 24 | IN-0980…IN-1003 | GT 1, NU 1, VI 20, JU 1 | 1 |
| (c) | ux | `ux/99-raw/handoff-to-ui-research.md` | 22 | IN-1004…IN-1025 | CM 9, NU 4, VI 1 | 8 |
| (c) | site | `site/99-raw/notes/triad-contract-2026-09-24.md` | 5 | IN-1026…IN-1030 | TR 3, GT 2 | 0 |
| (c) | claude-design | `claude-design/README.md` | 2 | IN-1031…IN-1032 | VI 1 | 1 |
| (d) | site | `site/99-raw/notes/triad-contract-2026-09-24.md` | 79 | IN-1033…IN-1111 | TR 52, GT 3, VI 3, JU 18, CN 1 | 2 |
| (e) | site | `site/99-raw/prompts/_common.md` | 15 | IN-1112…IN-1126 | TR 5, GT 1, JU 1, CN 8 | 0 |
| (e) | creative | `creative/99-raw/prompts/_common.md` | 16 | IN-1127…IN-1142 | TR 2, GT 2, VI 1, CN 11 | 0 |
| (f) | site | `site/PLAN.md` | 20 | IN-1143…IN-1162 | TR 2, GT 3, TX 2, VI 1, CN 11 | 1 |
| (f) | text | `text/PLAN.md` | 3 | IN-1163…IN-1165 | JU 1, CN 1 | 1 |
| (f) | creative | `creative/99-raw/prompts/_common.md` | 6 | IN-1166…IN-1171 | VI 1 | 5 |
| (f) | creative | `creative/PLAN.md` | 24 | IN-1172…IN-1195 | VI 5, CN 3 | 16 |
| (f) | ai-media | `ai-media/PLAN.md` | 4 | IN-1196…IN-1199 | CN 3 | 1 |
| (f) | blender | `blender/README.md` | 6 | IN-1200…IN-1205 | CN 5 | 1 |
| (f) | claude-design | `claude-design/PLAN.md` | 2 | IN-1206…IN-1207 | CN 1 | 1 |
| (g) | site | `легенды меток, оговорки к числам` | 2 | IN-1208…IN-1209 | JU 2 | 0 |
| (g) | text | `легенды меток, оговорки к числам` | 1 | IN-1210 | JU 1 | 0 |
| (g) | creative | `легенды меток, оговорки к числам` | 1 | IN-1211 | JU 1 | 0 |
| (g) | ux | `легенды меток, оговорки к числам` | 4 | IN-1212…IN-1224 | JU 4 | 0 |
| (g) | ui | `легенды меток, оговорки к числам` | 3 | IN-1214…IN-1225 | JU 3 | 0 |
| (g) | ai-media | `легенды меток, оговорки к числам` | 4 | IN-1215…IN-1226 | JU 4 | 0 |
| (g) | blender | `легенды меток, оговорки к числам` | 3 | IN-1218…IN-1227 | JU 3 | 0 |
| (g) | claude-design | `легенды меток, оговорки к числам` | 3 | IN-1220…IN-1228 | JU 3 | 0 |
| (h) | — | `phase-2/SYNTHESIS.md` | 14 | IN-1229…IN-1242 | TR 2, GT 1, CM 4, ST 1, NU 1, TX 2, VI 2, CN 1 | 0 |
| (i) | — | `phase-2/SYNTHESIS.md` | 22 | IN-1243…IN-1264 | GL 1, TR 2, GT 3, CM 2, ST 2, NU 4, TX 1, VI 4, JU 2, CN 1 | 0 |
| | | **итого** | **1 264** | | GL 9, TR 242, GT 116, CM 26, ST 14, NU 75, TX 69, VI 122, JU 72, CN 191 | **328** |

Статусы источников (по файлам):
- ux № 1–61: закрыто правкой — 9 (№ 2, 5, 12, 22, 32, 42, 43, 46, 47), позиция с условием — 52; «Позиции, ограниченные
  контекстом» — 16 развилок, не правил.
- ui C1–C49: все решены, у C8 решение `[спорно]`.
- site В-01…В-36: 35 строк (В-13 и В-14 — одной); «Свод поправок»: ✔ 20, ◐ 6; вне таблицы — 17 строк «оформлено».
- text X1–X45: решено 15, позиция 21, открыто 8, «спорно» 1 (X28); N1–N10 — сверено или исправлено; свод README — 15.
- creative X-01…X-67: решено 31, позиция 24, открыто 9, передано 2 (X-28, X-53), решение заказчика 1 (X-59); §Ж — 26.
- ai-media X1–X50: решено 38, позиция 10, открыто 2 (X2, X33).
- blender: R1–R52 — в 35 строках-темах README (статусы — из отчёта X §1), T1–T26 — открыты T15, T18.
- Передача соседям: site — «ждёт» у C1–C9 устарело, ответ W4 от 25.09 вписан в `note` (проверено по PLAN site и creative
  «Статус» и по таблице «Ответ на ваши C1–C10» handoff creative); text — приоритет П1–П3; creative — «не отправлено», «принято»,
  «к сведению»; blender — «не вносить (решение владельца 23.09) — справка».

Выборочная сверка с файлами: у всех 1 264 строк текст файла в строке `line` сверен скриптом с `item_id` и заголовком —
совпадают 1 236; остальные 28 указывают на заголовок раздела, общий пункт списка или абзац, из которого строка
собрана (§4 ux handoff, метки контракта §4, подпункты решения site 20, абзац «Не править»), — это ожидаемо. Статусы вручную
сверены по 3 строки на группу: реестры creative, blender, handoff site, text, creative, ux, таблицы канонов site, text,
creative, blender — расхождений нет.

## 2. Расхождения с заявленными счётчиками

| где | заявлено | в файле | почему |
|---|---|---|---|
| ux README, реестр | «Шестьдесят расхождений» | 61 строка | № 61 дописан из claude-design 25.09 |
| site README, В-01…В-36 | 36 | 35 строк | В-13 и В-14 — одной строкой |
| site «Свод поправок» | ✔ 19, ◐ 7 (SYNTHESIS §5.1) | ✔ 20, ◐ 6 | PLAN №15: в README ✔, в отчёте X §1.2 ◐ «частично» |
| text X1–X45 | позиция 22 | позиция 21, «спорно» 1 | X28: статус в файле «спорно · — · site» |
| creative X-01…X-67 | README и шапка handoff — 66; SYNTHESIS: 31 + 22 + 9 + X-59 = 63 | 67 | X-67 дописан 25.09; SYNTHESIS не посчитал «передано» (X-28, X-53) и одну позицию |
| ux X §2.1 | 54 строки (SYNTHESIS §5.2, Р50) | 61 | сводка самого отчёта X — «47 дублей с каноном»; таблица длиннее обоих чисел |
| creative X §2 | ≈ 20 норм | 19 | — |
| контракт тройки §2 | 32 темы (SYNTHESIS §2.2, §5.3, light/site) | 30 | ошибка счёта Ф2; последняя тема — «Интернет-магазин целиком» |
| text PLAN, легенда | 16 меток (SYNTHESIS §5.5) | 18 в таблице | общий набор 12 + две свои + три от аудита X + `[награда]`; прежний счёт извлечения «42» брал и абзац синонимов |
| ux README, оговорки к числам | 11 (SYNTHESIS §5.5) | 12 пунктов | — |
| легенды ux README, blender README, ui README | — | 9, 10, 11 меток | прежнее извлечение считало все метки раздела (14, 12, 14) — с примерами и ссылками вида `[S7]` |
| SYNTHESIS §6.12 | 27 пунктов | 14 строк | остальные — о счётчиках, журнале и коде, уже закрытом Р-решениями (раздел 5) |
| site, text, creative, blender, ux handoff | 62; 80 + 6 встречных + 13 словаря; 102; 24 (+8 ссылок §2); 21 (+ таблица §3) | так же | совпадает |

## 3. Назначение узлов

Строк с узлом — 936, с `—` — 328, без узла — 0. Узел по умолчанию — по виду строки: canon, owners, customer-decision
→ CN; triad-owner, triad-format, triad-conclusion → TR; triad-label, legend → JU; §9 — по таблице узлов PLAN. Реестры и
передачи назначены построчно в `assign.tsv`. Конфликты site с соседями из §9 п. 1 (M5, M6, B2–B4, U3–U5, UI1, T6–T8, T12, C10,
пограничные M8, M9) разданы по содержанию, у каждого в `note` — «конфликт» (у M8, M9 — «пограничный»).

**Строки `—`** — главный риск потери: проверка покрытия их не видит. Все 365 строк `—` исходной карты просмотрены по
заголовку, упоминаниям и, где тема могла быть у соседа, по файлам соседей (тосты ui 06/05, капча site, юмор text 05/01,
`data-motion` ui и ai-media, тёмный фон ui 11/04 и cd 06/05, расширение RU/EN ui 02/06, пагинация и крошки site, слой проекта
`telegram-bot-flow` и `mobile`). В узлы ушли 38 строк (раздел 7.1): двойники у соседей, пробелы слоя проекта,
межбазовые передачи с действием для Ф8 и Ф10, стыки Kimi. Остались `—`:

| причина | строк |
|---|---:|
| реестр базы: решено внутри базы, двойника у соседей нет | 258 |
| процесс ресерча и среда (Р82, Р90), решение заказчика — не спорит | 27 |
| открыто или задача внутри одной базы | 15 |
| ролики и дайджесты — не нормы | 15 |
| снято Р-решением (Р32, Р39, Р59) | 5 |
| живая фаза, нормы нет | 4 |
| прочее: граница покрытия, указатель на строки узлов, внешний Hallmark | 4 |

**19 помеченных строк** («спорно» или «?» в `note`): по существу спорных — 4. № 31 (TX) и № 45 (TX) — оставлены в TX, «спорно»
заменено обоснованием: граница голосов бренда и продукта (§9 п. 16) и запас на расширение RU/EN (ux 10–30 % против ui 02/06
§1). C8 — `—`: `[спорно]` внутри ui, у ux скрим без чисел. C30 (VI) — капс в интерфейсе против капс-надзаголовков маркетинга,
VI разводит по жанру. Остальные 15 — строки легенд, где `[спорно]` просто входит в перечень меток.

**Kimi** (96 строк: упоминание kimi, «K3», «Kimi»). Kimi в шаблоне нет; нормы kimi переписаны в `claude-design/06` (Р61,
Р68), стыки «тексты и бриф → исполнитель» заменяет единый вход холста и ДС (Р64, Р80), проектируется в Ф6. Строки оставлены в
тематических узлах — узел сверяет норму с её наследником в cd 06; в `note` у каждой — решение:

| решение в note | строк | по узлам |
|---|---:|---|
| норма → наследник в cd 06 (Р61, Р68): сверить | 60 | TR 25, GT 10, NU 6, TX 7, VI 8, JU 1, CN 3 |
| стык → единый вход холста (Р64, Ф6) | 21 | TR 17, CN 4 |
| снято Р-решением или разобрано другими строками (Р76 п. 6, Р80) | 4 | TR 1, CN 3 |
| «K3» — страницы Kimi в выборке калибровки: пересчёт на пилотах (Ф9) | 3 | VI 3 |
| процесс ресерча | 3 | — 3 |
| клоны в кэше kimi → внешние адреса (Р65) | 2 | NU 1, VI 1 |
| «K3» — id проверки ui_audit.py, не Kimi (Р65) | 1 | NU 1 |
| метки: путь kimi — пример в абзаце синонимов (не стык) | 1 | JU 1 |
| id K3-*/F-* → LOOK-*/HON-* при уборке (Р62, Р76 п. 25) | 1 | VI 1 |

Строки только со стыком и без темы узла (видео-референс для K3, частность пакета K15, путь проверки «генерация K3» В-24,
«к сведению» ck-14) — в CN.

**Выборка по узлам:** по 10 строк каждого узла (у GL и ST — все) сверены с назначением; ошибок не найдено. Две строки таблиц
канонов перенесены из CN к тематическим узлам, чтобы одну норму решал один узел: ux §2.1-15 (длительность тоста) — к CM вместе с
№ 11, text Д1 (длины слотов) — к TX вместе с X3, kimi-06, свод-11.

## 4. Узлы: строки, чтение, контекст

Оценка — `tools/budget.py`: токены по калибровке Opus 5.5, чтение × 1,25 (повторы, grep, выводы скриптов) + 65 тыс. постоянной
части (система и инструменты 25 тыс., выход узла 40 тыс.); CN — плюс выходы девяти узлов (200 тыс., оценка), JU — плюс строки
и записи CHAIN предыдущих узлов (50 тыс.).

| узел | строк | чтение | контекст |
|---|---:|---:|---:|
| GL | 9 | 93.5 тыс. | 182 тыс. |
| TR | 242 | 365 тыс. | 521 тыс. |
| GT | 116 | 224 тыс. | 344 тыс. |
| CM | 26 | 125 тыс. | 222 тыс. |
| ST | 14 | 115 тыс. | 209 тыс. |
| NU | 75 | 205 тыс. | 321 тыс. |
| TX | 69 | 112 тыс. | 204 тыс. |
| VI | 122 | 207 тыс. | 324 тыс. |
| JU | 72 | 221 тыс. | 341 тыс. |
| CN | 191 | 301 тыс. | 441 тыс. |

Порог деления (≈ 600 тыс.) не превышен ни у одного узла. Ближе всех TR — ≈ 521 тыс.: половина его чтения — три файла данных
(`crosswalk.tsv` 65,6 тыс., `copy-slots.yaml` 85,2 тыс., `vocabulary.yaml` 35,6 тыс.). Предложение: агент TR не читает
`crosswalk.tsv` и `copy-slots.yaml` целиком, а вынимает ключи скриптом (`section_role`, `slot_type`, `site_slot`, `site_id`,
`ux_role`) — это ≈ 150 тыс. экономии. Если без полного чтения не обойтись — деление: TR-1 «владельцы, форматы, контракт тройки,
конфликты site с соседями, стыки Kimi» (≈ 200 строк) и TR-2 «словари страниц, секций, слотов», §9 п. 4 (≈ 40 строк, три файла
данных). Для CN: выходы узлов читать через `nodes/*.tsv` целиком, а md узлов — разделами «Решено» и «Открыто».

Общее для всех узлов:

| файл | разделы | токены |
|---|---|---:|
| `research/design-build/phase-4/PLAN.md` | весь файл | 5.1 тыс. |
| `research/design-build/phase-4/CHAIN.md` | весь файл | 2.0 тыс. |
| `research/design-build/DECISIONS.md` | весь файл | 17.2 тыс. |
| `research/design-build/phase-2/SYNTHESIS.md` | 9. Сверка баз — что сверять | 2.8 тыс. |

Итого общего: ≈ 27.1 тыс.

#### GL — строк 9; чтение ≈ 93.5 тыс.; контекст ≈ 182 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `ux/00-glossary.md` | Ложные друзья, омонимы и опасные атрибуции | 2.1 тыс. | ложные друзья ux |
| `site/00-glossary/glossary.md` | 0. Ложные друзья и расхождения определений … | 2.9 тыс. | ложные друзья site |
| `text/00-glossary/glossary.md` | 13. Ложные друзья и расхождения определений | 1.6 тыс. | ложные друзья text |
| `creative/00-glossary/glossary.md` | 0. Ложные друзья и расхождения определений … | 3.0 тыс. | ложные друзья creative |
| `ui/00-glossary/glossary.md` | 14. Несовместимая терминология: где источни… | 6.8 тыс. | несовместимая терминология ui |
| `ai-media/00-glossary/glossary.md` | 12. Омонимы и расхождения терминологии | 3.0 тыс. | омонимы ai-media |
| `blender/00-glossary/README.md` | Ложные друзья и путаницы | 3.5 тыс. | ложные друзья blender |
| `research/design-build/phase-2/SYNTHESIS.md` | 6.4. Разнобой терминов | 0.8 тыс. | таблица «ложных друзей» |
| `research/design-build/phase-2/CHAIN.md` | Общее | 0.1 тыс. | общие наблюдения Ф2 |
| `research/design-build/phase-2/ux/ux-низ.md` | 5. Связи с соседними базами (файловые перес… | 2.8 тыс. | термины на стыках |
| `docs/projects/_template/project/README.md` | весь файл | 7.0 тыс. | термины слоя проекта |
| `docs/projects/_template/interface/README.md` | весь файл | 5.0 тыс. | термины слоя проекта |
| `docs/projects/_template/screens/README.md` | весь файл | 6.3 тыс. | термины слоя проекта |
| `docs/projects/_template/mobile/README.md` | весь файл | 7.8 тыс. | термины слоя проекта |
| `docs/projects/_template/telegram-bot-flow/README.md` | весь файл | 9.2 тыс. | термины слоя проекта |
| `docs/projects/_template/fsd/README.md` | весь файл | 3.5 тыс. | термины слоя проекта |

#### TR — строк 242; чтение ≈ 365 тыс.; контекст ≈ 521 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `site/99-raw/notes/triad-contract-2026-09-24.md` | 2. Владельцы пересекающихся тем; 3. Общие форматы обмена; 4. Размер и метод (решения заказчика 24.09.…; 5. Порядок запуска трёх баз и точки синхрон…; 6. Сквозные выводы аудита — обязательны для…; 8. Предложения соседям от тройки (файлы сос… | 14.9 тыс. | контракт тройки §2–§6, §8 |
| `site/99-raw/handoff-to-neighbours.md` | весь файл | 12.7 тыс. | поправки site |
| `text/99-raw/handoff-to-neighbours.md` | весь файл | 20.2 тыс. | поправки text |
| `creative/99-raw/handoff-to-neighbours.md` | site — `../site/` (сестра; раздел пересылае…; text — `../text/` (сестра; раздел пересылае… | 8.3 тыс. | поправки creative сёстрам |
| `site/99-raw/reports/wave4-X-audit.md` | 1.2. С соседями: таблица «Поправки к правил…; 1.3. С сёстрами (text, creative); 2. Дубли и каноническое место; 8. Сверка тройки — подготовка к S2; 9.4. Что передать соседям и сёстрам (раздел… | 19.7 тыс. | отчёт X site |
| `site/README.md` | Реестр разрешённых противоречий; Свод поправок к соседям; Что передано соседям и сёстрам; Сёстры и точки синхронизации | 9.3 тыс. | реестр и свод site |
| `text/CONTRADICTIONS.md` | [X7] Температура трафика: отношения с бренд…; [X26] Google против Яндекса: страницы под в…; [X27] Google против Яндекса: слова запроса …; [X28] Клики из ИИ-ответов; [X32] Текст собственного сайта — реклама ил…; [X43] FAQ как блок против «ответа рядом с р…; [X44] Первый экран страницы кейса без роли …; [X11] Места фактов (`use`) против мест текс…; [X34] Главная кнопка первого экрана меропри… | 3.8 тыс. | позиции text по спорам с site |
| `site/02-site-types/vocabulary.yaml` | весь файл | 35.6 тыс. | словарь site v1 |
| `site/02-site-types/crosswalk.tsv` | весь файл | 65.6 тыс. | соответствие словарей (верхняя граница: читать фильтром) |
| `text/99-raw/notes/temp-vocabulary-v0.yaml` | весь файл | 8.3 тыс. | временный словарь text |
| `text/04-copy-by-block/copy-slots.yaml` | весь файл | 85.2 тыс. | слоты text (верхняя граница: читать частями) |
| `site/99-raw/prompts/_common.md` | Кто чем владеет — чтобы не было дублей | 1.1 тыс. | владение site |
| `creative/99-raw/prompts/_common.md` | Кто чем владеет — чтобы не было дублей | 1.0 тыс. | владение creative |
| `site/PLAN.md` | Как всё сочетается: конвейер и контракты | 2.1 тыс. | конвейер site |
| `text/PLAN.md` | Как всё сочетается: конвейер и контракты | 4.1 тыс. | конвейер text |
| `creative/PLAN.md` | Как всё сочетается: конвейер и контракты | 2.0 тыс. | конвейер creative |
| `claude-design/06-design-process/02-input-package.md` | весь файл | 8.1 тыс. | единый вход холста — куда ушли стыки kimi |
| `research/design-build/phase-2/SYNTHESIS.md` | 2.2. Узлы межбазовых связей (основа будущег…; 5.3. Владение форматами и конвейеры; 8.3. page-plan ↔ copy deck | 5.0 тыс. | узлы связей, владение |
| `creative/CONTRADICTIONS.md` | Е. Сёстры, соседи, условия площадок | 2.9 тыс. | X-56 и соседи тройки |

#### GT — строк 116; чтение ≈ 224 тыс.; контекст ≈ 344 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `site/07-seo-geo-performance-analytics/page-gates.yaml` | весь файл | 21.2 тыс. | ворота страницы |
| `site/07-seo-geo-performance-analytics/budgets.yaml` | весь файл | 7.9 тыс. | бюджеты |
| `site/07-seo-geo-performance-analytics/03-performance-budgets-gates.md` | Выжимка для агента; 3. Профили бюджета «тип страницы × уровень …; 4. Единые ворота страницы (`page-gates.yaml…; 6. Расхождения с воротами соседей | 7.3 тыс. | site 07/03 |
| `site/09-ai-generation-evaluation/02-site-checklist.md` | 5. Профиль UX-чек-листа для сайта; 6. Автопроверки и ворота v1.2; 8. Нормализация со смежными проверками | 6.7 тыс. | site 09/02 §5, §6, §8 |
| `blender/11-evaluation-qa/05-master-checklist.md` | весь файл | 11.8 тыс. | WEB-01, WEB-04 и др. |
| `blender/09-web-runtime/05-performance-a11y-fallbacks.md` | Выжимка для агента; 1. Бюджеты; 7. Чек-лист «страница с 3D готова к публика… | 7.1 тыс. | blender 09/05 §1, §7 |
| `blender/01-web-3d-landscape/02-when-3d-budgets-loading.md` | 3. Бюджеты | 2.9 тыс. | blender 01/02 §3 |
| `creative/01-creative-direction/ambition-levels.yaml` | весь файл | 15.0 тыс. | уровни L0–L2 |
| `creative/01-creative-direction/03-ambition-levels.md` | Выжимка для агента; 4. Бюджеты: два слоя; 7. Соответствие соседям; 8. Поправки к соседям для сайта | 10.2 тыс. | creative 01/03 |
| `creative/09-ai-execution-evaluation/effect-gates.yaml` | весь файл | 16.2 тыс. | ворота эффектов |
| `creative/09-ai-execution-evaluation/03-verification-loop-and-gates.md` | Выжимка для агента; 3. Ворота эффектов `effect-gates.yaml`; 4. Профиль `marketing` для `ui_audit.py` | 14.7 тыс. | creative 09/03 |
| `ai-media/10-web-integration/04-budgets-and-acceptance.md` | весь файл | 9.7 тыс. | page_accept, бюджеты ai-media |
| `ai-media/11-evaluation-qa/thresholds.yaml` | весь файл | 7.8 тыс. | пороги ai-media |
| `ux/12-evaluation-checklists/03-automated-checks.md` | 9. Производительность как UX-порог; 10. Пороги и правила «стоп» | 3.0 тыс. | ux AC-PRF |
| `blender/README.md` | Реестр противоречий | 14.1 тыс. | R2, R19, R20, T-строки |
| `creative/CONTRADICTIONS.md` | Б. Уровни, бюджеты, счёт; А. Движение, прокрутка, доступность; Д. Данные и поддержка браузеров; Е. Сёстры, соседи, условия площадок | 16.0 тыс. | X-17, X-18, X-21, X-45 |
| `creative/99-raw/handoff-to-neighbours.md` | site — `../site/` (сестра; раздел пересылае…; ai-media — `../ai-media/`; blender — `../blender/` | 9.5 тыс. | cs-*, ca-*, cb-* |
| `ai-media/CONTRADICTIONS.md` | Доставка и страница | 1.0 тыс. | X17: LCP полноэкранного hero |
| `claude-design/06-design-process/01-brief-and-questions.md` | 6. Решения до экранов | 0.7 тыс. | уровни движения cd ↔ L0–L2 (X-27, X-28, ck-07) |

#### CM — строк 26; чтение ≈ 125 тыс.; контекст ≈ 222 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `ux/04-components-patterns/01-data-tables.md` | Выжимка для агента | 3.2 тыс. | поведение компонентов ux 04 |
| `ux/04-components-patterns/02-search-filter-sort.md` | Выжимка для агента | 2.4 тыс. | поведение компонентов ux 04 |
| `ux/04-components-patterns/03-dashboards-and-kpi.md` | Выжимка для агента | 2.8 тыс. | поведение компонентов ux 04 |
| `ux/04-components-patterns/04-lists-cards-and-record-view.md` | Выжимка для агента | 2.1 тыс. | поведение компонентов ux 04 |
| `ux/04-components-patterns/05-forms-and-validation.md` | Выжимка для агента | 3.5 тыс. | поведение компонентов ux 04 |
| `ux/04-components-patterns/06-input-controls.md` | Выжимка для агента | 2.6 тыс. | поведение компонентов ux 04 |
| `ux/04-components-patterns/07-overlays-modals-drawers-popovers.md` | Выжимка для агента | 2.3 тыс. | поведение компонентов ux 04 |
| `ux/04-components-patterns/08-notifications-toasts-banners.md` | Выжимка для агента | 1.9 тыс. | поведение компонентов ux 04 |
| `ux/04-components-patterns/09-settings-permissions-admin.md` | Выжимка для агента | 2.1 тыс. | поведение компонентов ux 04 |
| `ux/04-components-patterns/10-actions-menus-bulk-shortcuts.md` | Выжимка для агента | 2.3 тыс. | поведение компонентов ux 04 |
| `ux/06-feedback-states-motion/01-state-matrix.md` | 7. Состояния как свойство компонента; 8. Процедура «каждое состояние спроектирова… | 4.1 тыс. | состояния элемента ux 06/01 §7–8 |
| `ui/06-components-visual/01-buttons-and-actions.md` | Выжимка для агента | 2.7 тыс. | визуальные спецификации ui 06 |
| `ui/06-components-visual/02-forms-and-inputs.md` | Выжимка для агента | 2.4 тыс. | визуальные спецификации ui 06 |
| `ui/06-components-visual/03-tables-and-lists.md` | Выжимка для агента | 2.2 тыс. | визуальные спецификации ui 06 |
| `ui/06-components-visual/04-navigation-and-surfaces.md` | Выжимка для агента | 2.1 тыс. | визуальные спецификации ui 06 |
| `ui/06-components-visual/05-feedback-and-overlays.md` | Выжимка для агента | 2.2 тыс. | визуальные спецификации ui 06 |
| `ui/06-components-visual/06-data-display-and-misc.md` | Выжимка для агента | 1.8 тыс. | визуальные спецификации ui 06 |
| `ui/06-components-visual/07-states-matrix.md` | весь файл | 16.0 тыс. | матрица «компонент × состояние» |
| `ui/14-recipes/08-tokens-export.md` | Шаг 4. Контролируемый словарь меток `usage` | 1.4 тыс. | словарь usage 14/08 §4 |
| `ui/14-recipes/examples/app.css` | весь файл | 10.6 тыс. | классы примеров |
| `ui/12-ai-generated-ui/04-steering-brief-prompts-pipeline.md` | 2.6. Рабочий пакет: что собирать самим | 1.0 тыс. | ui 12/04 §2.6 |
| `ux/99-raw/handoff-to-ui-research.md` | весь файл | 16.7 тыс. | ожидания ux от ui |
| `docs/projects/_template/screens/README.md` | весь файл | 6.3 тыс. | закрытый словарь ui: в screens (Р29) |
| `research/design-build/phase-2/ux/ux-низ.md` | 8. Вопросы к заказчику | 0.7 тыс. | §6.12 п. 25: закрытый словарь ui: (Р29, Р76, Р79) |

#### ST — строк 14; чтение ≈ 115 тыс.; контекст ≈ 209 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `ux/06-feedback-states-motion/01-state-matrix.md` | Выжимка для агента; 2. Закрытый список состояний (S01–S22); 3. Матрица «экран или компонент × состояние» | 9.9 тыс. | S01–S22 |
| `ux/03-layout-placement/01-page-anatomy-templates.md` | весь файл | 25.3 тыс. | 11 шаблонов экранов ux 03/01 |
| `ux/13-app-types/04-master-procedure-brief-to-screens.md` | Выжимка для агента; 1. Карта процедуры: 30 шагов; Фаза D. Экраны и навигация (шаги 14–17) | 7.9 тыс. | процедура ux 13/04 (§14) |
| `ui/05-layout-grid/02-app-shells.md` | Выжимка для агента; 2. Восемь каркасов: схемы и размеры; 3. Выбор каркаса: таблица решений | 14.4 тыс. | 8 каркасов ui 05/02 |
| `ui/05-layout-grid/03-page-anatomy.md` | Выжимка для агента | 2.5 тыс. | 8 типов страниц ui 05/03 |
| `research/design-build/phase-2/ux/ux-низ.md` | 3.1 Контракт S01–S22 против шести канон-сос… | 3.5 тыс. | таблица сопоставления ux-низ §3.1 |
| `docs/projects/_template/screens/README.md` | весь файл | 6.3 тыс. | состояния слоя проекта |
| `docs/projects/_template/mobile/README.md` | весь файл | 7.8 тыс. | состояния слоя проекта |
| `docs/projects/_template/telegram-bot-flow/README.md` | весь файл | 9.2 тыс. | состояния слоя проекта |

#### NU — строк 75; чтение ≈ 205 тыс.; контекст ≈ 321 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `ux/03-layout-placement/02-grid-spacing-density.md` | весь файл | 16.4 тыс. | ux 03/02: шкала 8/4, плотность |
| `ux/08-accessibility/01-wcag22-as-build-rules.md` | 8. Указатель, жесты, размеры целей; 12.4 2.5.8 Target Size (Minimum), AA | 3.6 тыс. | цели нажатия ux 08/01 |
| `ux/06-feedback-states-motion/03-motion-and-microinteractions.md` | весь файл | 26.2 тыс. | движение ux 06/03 |
| `ui/03-spacing-sizing/01-spacing-scale.md` | весь файл | 25.4 тыс. | ui 03 |
| `ui/03-spacing-sizing/02-density.md` | весь файл | 16.7 тыс. | ui 03 |
| `ui/03-spacing-sizing/03-control-and-panel-sizes.md` | весь файл | 20.1 тыс. | ui 03 |
| `ui/14-recipes/11-presets.md` | весь файл | 14.4 тыс. | пресеты A–D |
| `ui/08-motion/01-durations-easings-springs.md` | Выжимка для агента | 2.8 тыс. | движение ui 08 |
| `ui/08-motion/02-what-to-animate-in-apps.md` | Выжимка для агента | 2.1 тыс. | движение ui 08 |
| `ui/08-motion/03-reduced-motion-and-motion-tokens.md` | Выжимка для агента | 1.7 тыс. | движение ui 08 |
| `ui/09-design-tokens/04-reference-token-schema.md` | Выжимка для агента; 1.3. Размерный ряд и шкалы; 2.10. Движение: набор агента M, взятый цели… | 8.0 тыс. | токены: шкалы и движение (без листинга) |
| `ui/05-layout-grid/01-grids-breakpoints-containers.md` | Выжимка для агента | 2.8 тыс. | брейкпоинты ui |
| `creative/05-motion/01-motion-principles-and-access.md` | Выжимка для агента; 2. Поправки к правилам соседей для сайта; 3. WCAG 2.2: 2.2.2, 2.3.1, 2.3.3 — дословно…; 5. Бюджет внимания | 14.5 тыс. | creative 05/01 §2 |
| `ui/CONTRADICTIONS.md` | Отступы, размеры, плотность; Компоненты и состояния | 5.8 тыс. | C9, C11, C16, C10, C19, C20, C43 |
| `research/design-build/phase-2/SYNTHESIS.md` | 6.12. Противоречия между документами (показ… | 2.0 тыс. | п. 24 — ширины |
| `creative/CONTRADICTIONS.md` | А. Движение, прокрутка, доступность | 6.1 тыс. | реестр creative: движение (X-02…X-04, X-12, X-13) |
| `claude-design/06-design-process/01-brief-and-questions.md` | 6. Решения до экранов | 0.7 тыс. | уровни движения cd (наследник норм kimi ck-*) |

#### TX — строк 69; чтение ≈ 112 тыс.; контекст ≈ 204 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `ux/07-ux-writing/01-principles-voice-and-tone.md` | Выжимка для агента; 12. Длина текстов по компонентам | 4.1 тыс. | ux 07/01 §12 (длины по ролям) |
| `ux/07-ux-writing/02-microcopy-by-component.md` | Выжимка для агента | 2.1 тыс. | ux 07/02 |
| `ux/07-ux-writing/03-russian-interface-text.md` | Выжимка для агента | 2.0 тыс. | ux 07/03 |
| `ux/07-ux-writing/06-banned-words-and-patterns.md` | весь файл | 23.7 тыс. | словарь запретов ux 07/06 (канон, Р49) |
| `text/06-anti-slop/01-text-slop-markers-by-genre.md` | Выжимка для агента; 11. Правила для роли marketing: поправки к … | 4.8 тыс. | text 06/01 |
| `text/06-anti-slop/02-linter-spec-and-profiles.md` | Выжимка для агента | 1.8 тыс. | линтер text |
| `text/06-anti-slop/lexicon/marketing-role.yaml` | весь файл | 4.1 тыс. | поправки роли marketing |
| `text/05-voice-editorial/01-brand-voice.md` | Выжимка для агента; 2. Голос бренда и голос продукта: два голос… | 4.6 тыс. | голос бренда (05/01 §2) |
| `text/08-russian-legal-typography/02-typography-for-marketing.md` | Выжимка для агента | 2.4 тыс. | типографика, тире |
| `text/CONTRADICTIONS.md` | Антислоп, тире, типографика; [X2] Длина — сигнал или ворота | 4.7 тыс. | X19–X25 |
| `text/99-raw/reports/wave4-X-audit.md` | 6. Дубли и каноническое место; 7. Калибровка утилит (не правлено; решает з… | 7.6 тыс. | X text §6–7 |
| `text/99-raw/handoff-to-neighbours.md` | ux — `../../ux/` (микрокопи интерфейса); ui — `../../ui/` (как текст выглядит) | 4.7 тыс. | ux-*, ui-* |
| `ui/02-typography/06-localization-and-ai-errors.md` | 1. Расширение текста при переводе; 3. Русские типографские нормы в интерфейсе | 5.4 тыс. | ui: расширение RU/EN и типографика интерфейса (тире, кавычки) — третья сторона §9 п. 16 |
| `claude-design/06-design-process/05-default-look.md` | Выжимка для агента; 3. Единый бан-лист с порогами | 4.6 тыс. | тире и длина hero — наследник норм kimi (kimi-01, свод-05, X3) |

#### VI — строк 122; чтение ≈ 207 тыс.; контекст ≈ 324 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `ui/11-styles-trends/04-anti-slop-ui.md` | весь файл | 21.7 тыс. | 34 маркера ui |
| `ui/07-iconography-imagery/02-illustration-system-avatars-images.md` | 3. Паспорт системы иллюстраций (шаблон) | 2.1 тыс. | паспорт иллюстраций ui 07/02 §3 |
| `ui/12-ai-generated-ui/01-image-models-for-ui.md` | 6. Blender и 3D в конвейере | 1.1 тыс. | черновик паспорта 3D ui 12/01 §6 |
| `creative/08-uniqueness-anti-slop/cliche-registry.yaml` | весь файл | 46.7 тыс. | 53 клише |
| `creative/08-uniqueness-anti-slop/01-cliche-policy.md` | Выжимка для агента | 2.0 тыс. | политика «приём или клише» |
| `creative/01-creative-direction/01-concept-and-directions.md` | 2. Ворота вопросов: что спрашивать и когда; 6. Направления | 5.3 тыс. | направления creative 01/01 |
| `site/09-ai-generation-evaluation/ai-landing-markers.yaml` | весь файл | 31.3 тыс. | 52 маркера AIL |
| `text/06-anti-slop/01-text-slop-markers-by-genre.md` | Выжимка для агента | 3.1 тыс. | COPY-M |
| `ai-media/01-web-assets-landscape/03-ai-fit-trust-and-slop.md` | 5. Каталог маркеров «сгенерированности» | 9.4 тыс. | IMG-M, VID-M |
| `ai-media/06-art-direction-consistency/01-visual-dna-from-ui.md` | 2. Поля паспорта и куда идёт каждое; 3. Правила вывода из токенов и стиля UI (R1… | 5.0 тыс. | паспорт визуала ai-media 06/01 |
| `claude-design/05-design-artifacts/01-design-system-and-canvas-in-session.md` | 5. Холст: процесс Claude Design страницами … | 0.7 тыс. | cd 05/01 §5 |
| `claude-design/06-design-process/01-brief-and-questions.md` | 4. Вопросы заказчику; 5. Направления: оси | 2.4 тыс. | cd 06/01 §4–5 |
| `claude-design/06-design-process/05-default-look.md` | весь файл | 8.7 тыс. | бан-лист дефолтного вида |
| `blender/01-web-3d-landscape/01-effects-catalog.md` | 22. Клише 2024–2026 и чем заменить | 0.6 тыс. | клише 3D |
| `blender/06-materials-lighting-render/02-lighting-camera-composition.md` | 6. Паспорт серии (проверенный, заменяет чер… | 2.4 тыс. | паспорт 3D-серии |
| `blender/99-raw/handoff-to-neighbours.md` | весь файл | 5.9 тыс. | паспорт: черновик ui против blender |
| `research/design-build/phase-2/kimi-mapping.md` | 5. Предложение: новые id проверок `mockup_c… | 1.0 тыс. | LOOK-*, HON-* |
| `creative/CONTRADICTIONS.md` | Г. Клише, уникальность, оценка; В. Концепция и визуальный язык; Е. Сёстры, соседи, условия площадок; И. Дополнение 25.09.2026 из claude-design-r… | 8.4 тыс. | X-29…X-44 |
| `creative/99-raw/handoff-to-neighbours.md` | ui — `../ui/`; ai-media — `../ai-media/`; kimi — `../kimi-research/` | 6.5 тыс. | cu-*, ca-*, ck-* |
| `text/CONTRADICTIONS.md` | [X22] Плотность маркеров слопа как детектор…; [X24] Ярлыки секций: слоп или конвенция | 1.3 тыс. | COPY-M не детектор ИИ; ярлыки секций |

#### JU — строк 72; чтение ≈ 221 тыс.; контекст ≈ 341 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `text/09-ai-generation-evaluation/03-evaluation.md` | 3. Рубрика COPY-R: как применять; 4. ИИ-судья: что известно и как вызывать | 7.2 тыс. | рубрика и судья text |
| `text/09-ai-generation-evaluation/copy-rubric.yaml` | весь файл | 18.1 тыс. | copy-rubric |
| `site/09-ai-generation-evaluation/03-expert-review-and-judge.md` | 4. Рубрика судьи `site-rubric.json`; 5. Когда судье можно верить | 4.5 тыс. | судья site |
| `site/09-ai-generation-evaluation/site-rubric.json` | весь файл | 10.8 тыс. | site-rubric |
| `creative/09-ai-execution-evaluation/04-effectiveness-rubric.md` | 4. Попарное сравнение с референсами того же…; 7. VLM-судья по кадрам | 3.2 тыс. | рубрика creative |
| `creative/09-ai-execution-evaluation/effectiveness.rubric.json` | весь файл | 12.1 тыс. | effectiveness.rubric |
| `ui/13-evaluation-checklists/02-rubrics-and-vlm-critic.md` | 1. Рубрика: десять измерений, шкала 0–5; 4. Модель-критик: промт и формат | 8.0 тыс. | рубрика ui 13/02 |
| `ai-media/11-evaluation-qa/02-vlm-critic-and-rubrics.md` | весь файл | 17.4 тыс. | VLM-критик ai-media |
| `ai-media/11-evaluation-qa/thresholds.yaml` | весь файл | 7.8 тыс. | группа judge |
| `blender/11-evaluation-qa/06-wow-pairwise-3d.md` | весь файл | 12.6 тыс. | попарная оценка blender |
| `ux/12-evaluation-checklists/01-expert-review-protocols.md` | 7. Адаптация протоколов для ИИ-агента | 7.1 тыс. | протокол для ИИ-агента ux |
| `ux/12-evaluation-checklists/03-automated-checks.md` | 8. Мультимодальная критика | 1.7 тыс. | ux 12/03 §8 |
| `claude-design/06-design-process/04-checks.md` | 6. Рубрика: судья-Opus в отдельной сессии | 0.7 тыс. | судья-Opus cd |
| `claude-design/06-design-process/06-test-stand.md` | весь файл | 7.7 тыс. | стенд и правило решения |
| `site/PLAN.md` | Метки доказательности | 0.9 тыс. | легенда меток site |
| `text/PLAN.md` | Метки доказательности | 1.9 тыс. | легенда меток text |
| `creative/PLAN.md` | Метки доказательности | 0.7 тыс. | легенда меток creative |
| `ux/README.md` | Легенда меток уровня доказательности | 2.2 тыс. | легенда меток ux |
| `ai-media/PLAN.md` | Метки доказательности | 0.6 тыс. | легенда меток ai-media |
| `ai-media/README.md` | Уровни доказательности и как читать метки; Что ненадёжно | 1.8 тыс. | легенда меток ai-media |
| `blender/README.md` | Легенда меток; Оговорки к числам | 2.2 тыс. | легенда меток blender |
| `ui/README.md` | Уровни доказательности и как читать метки; Что ненадёжно | 2.2 тыс. | легенда меток ui |
| `claude-design/PLAN.md` | Метки доказательности | 0.5 тыс. | легенда меток claude-design |
| `ux/99-raw/reports/wave4-X-audit.md` | 2.2. Метки уровня доказательности — рассинх… | 0.9 тыс. | легенда меток ux |
| `site/99-raw/reports/wave4-X-audit.md` | 9.3. Что не править (противоречие остаётся … | 1.6 тыс. | легенда меток site |
| `claude-design/README.md` | Метки и доверие | 0.5 тыс. | оговорки о доверии cd |
| — | строки и записи CHAIN предыдущих узлов (оценка) | 50.0 тыс. | сверх списка |

#### CN — строк 191; чтение ≈ 301 тыс.; контекст ≈ 441 тыс.

| файл | разделы | токены | зачем |
|---|---|---:|---|
| `ux/99-raw/reports/wave4-X-audit.md` | 2.1. Одно правило в нескольких файлах | 7.8 тыс. | таблица канонов ux |
| `site/99-raw/reports/wave4-X-audit.md` | 2. Дубли и каноническое место; 9.3. Что не править (противоречие остаётся … | 4.7 тыс. | таблица канонов site |
| `text/99-raw/reports/wave4-X-audit.md` | 3. Пятнадцать вопросов базы (PLAN, «Вопросы…; 6. Дубли и каноническое место; 7. Калибровка утилит (не правлено; решает з… | 10.4 тыс. | таблицы канонов text |
| `creative/99-raw/reports/wave4-X-audit.md` | 2. Дубли и каноническое место; 9. Калибровка утилит — список для S или отд… | 4.6 тыс. | таблицы канонов creative |
| `blender/99-raw/reports/wave4-X-audit.md` | 4. Дубли и рассинхрон чисел — каноническое … | 3.0 тыс. | таблица канонов blender |
| `site/PLAN.md` | Решения заказчика (24.09.2026) | 4.3 тыс. | решения заказчика site |
| `text/PLAN.md` | Решения заказчика (24.09.2026) | 3.2 тыс. | решения заказчика text |
| `creative/PLAN.md` | Решения заказчика (24.09.2026) | 3.5 тыс. | решения заказчика creative |
| `ai-media/PLAN.md` | Решения заказчика (23.09.2026) | 3.1 тыс. | решения заказчика ai-media |
| `blender/README.md` | Решения заказчика (23.09.2026) и что остало… | 2.3 тыс. | решения заказчика blender |
| `creative/99-raw/prompts/_common.md` | Решения заказчика (обязательны) | 0.7 тыс. | решения 1–6 creative |
| `claude-design/PLAN.md` | Решения заказчика (25.09.2026) | 1.1 тыс. | решения cd 6–7 против DECISIONS |
| `creative/CONTRADICTIONS.md` | Е. Сёстры, соседи, условия площадок | 2.9 тыс. | лицензии X-60, X-61 |
| `site/99-raw/prompts/_common.md` | Кто чем владеет — чтобы не было дублей | 1.1 тыс. | владение темами site (строки owners) |
| `creative/99-raw/prompts/_common.md` | Кто чем владеет — чтобы не было дублей | 1.0 тыс. | владение темами creative (строки owners) |
| — | выходы узлов GL…JU (nodes/*.tsv, *.md; оценка) | 200 тыс. | сверх списка |

## 5. Не назначено и не прочитано

- Не назначенных строк нет (`--dump` пуст, `registry.py coverage` — «без узла 0»).
- Не извлекаются, только счёт: ai-media отчёт X §3 (55 строк) и «Продолжение X2» (29) — история поправок, не нормы.
- Не извлекается: blender handoff §2 — 8 строк ссылок на соседей, не поправки.
- SYNTHESIS §6.12 — не строки (13 из 27): пп. 1, 2, 10, 16 (счётчики документов), п. 4 (демо-факты —
  Р69), пп. 5–7 (пилот site — Р66), п. 8 (счёт конфликтов — вместе с п. 11 в TR), п. 19 (кадры MAREA — в строке решения
  ai-media 12, CN), п. 21 (`lab/` creative — Р39), п. 26 (план — Р77), п. 27 (ключи — Р73).
- Решения заказчика баз: взяты номера SYNTHESIS §5.5 и claude-design 6–7 (SYNTHESIS cd не называет). Остальные номера site,
  text, ai-media, claude-design — процесс ресерча (волны, агенты, сеть, лимиты) или дубли взятых (text 7, 11, 12 = site 7, 10,
  11); ai-media 13 (дорогие 3D-модели) — покрыт строками ai-media 12, 14 и X47 (CN, против Р72).
- Не проверено по существу: примечания прерванного агента со ссылками на `phase-2/light/*` («копия устарела: … light/ux §1.3»)
  — `light/*` не читались; содержание глоссариев баз (это чтение GL); сами файлы kb сверх разделов, нужных для проверок выше.
- `in-drafts/in-trace.md` не открывался (Р119).

## 6. Замечания к плану узлов

1. Номера `IN-…` — только дописывать в конец (раздел «Файлы и запуск»). Узлам — ссылаться диапазонами (`IN-0717…IN-0734`),
   `§9 п. N` и `§6.12 п. N` — `registry.py` понимает все три формы.
2. GL: строк 9 — его вход не строки, а глоссарии баз и слоя проекта (чтение). Покрытие GL проверяет только 9 строк; полноту
   глоссария видно лишь по его md.
3. Kimi: 21 строка «стык → единый вход холста (Р64, Ф6)» (TR 17, CN 4). CN стоит собрать их одной строкой реестра `gap` с
   действием «Ф6: единый вход холста — учесть стыки …» и перечнем `IN-…`, чтобы Ф6 получила список.
4. JU: строки оговорок к числам и «что ненадёжно» (ux, ui, ai-media, blender, claude-design) — вторая половина легенды: где метке
   нельзя верить без условия; `evidence.md` без них неполон. `[стенд]` ai-media не выполнен ни разу — это тоже оговорка.
5. ST: кроме состояний и шаблонов — две строки слоя проекта (передача бота человеку, состав мобильных сценариев): в шаблоне этих
   норм нет, действие — Ф6/Ф7.
6. CM: §6.12 п. 25 — закрытый словарь `ui:` (Р29, Р76, Р79) против контракта, снятого коммитом `1dd3a93`; смотреть
   `git show 1dd3a93` и `phase-2/ux/ux-низ.md` §8.
7. CN получает «мелкие поправки к соседям» без темы узла (код — Ф8, текст — Ф10, лицензии, правовая пометка ИИ-контента,
   видео-референс): закрывать строкой реестра с `action`, не разбором.
8. creative X-59 (условия площадок) — в VI (IN-0333): по плану узел готовит его одной строкой с вариантами для заказчика.
9. `registry.py check` предупреждает, если `source` узла называет строки других узлов (у CN — нет): узел может закрыть чужую
   строку, оркестратору это видно сразу.
10. Строки `—` никто не проверяет покрытием. CN при сведении может выборочно пройти их список (раздел 3) — хотя бы строки с
    упоминанием соседа в `mentions`.

## 7. Правки доводки

### 7.1. Узлы строк: было → стало

| строка | источник | было → стало | почему |
|---|---|---|---|
| IN-0011 | ux № 11 — Тосты: угол и длительность | — → CM | из «—»: срок жизни тоста — ux 4–10 с, по умолчанию 5–6 (04/08 §3.2) против ui 06/05 «4 с» (Sonner TOAST_LIFETIME); словарь компонентов (Р45); вместе с ux X §2.1-15 |
| IN-0032 | ux № 32 — Капча | — → CN | из «—»: дубль с site — README «Выжимка» п. 27 и 10/02 «Антиспам» (без видимой капчи; невидимая — при подтверждённой атаке) ↔ ux: «невидимая reCAPTCHA доступна» — предположение; одно место нормы |
| IN-0041 | ux № 41 — Юмор в ошибках | — → TX | из «—»: голос продукта в ошибках ↔ text 05/01 (юмор в голосе бренда; поддержка и жалобы — без юмора) — граница голосов бренда и продукта (§9 п. 16), вместе с № 31 |
| IN-0049 | ux № 49 — Передача чат-бота человеку | — → ST | из «—»: слой проекта — в telegram-bot-flow шаблона передачи человеку нет (пробел); норма ux (явная просьба — сразу, неявный провал — после трёх попыток) — вход Ф6/Ф7 |
| IN-0057 | ux № 57 — Урезать функции в мобильном или паритет | — → ST | из «—»: слой проекта — mobile: состав мобильных сценариев решается в брифе, паритет контента — цель по умолчанию; в README mobile шаблона нормы нет — вход Ф6 |
| IN-0077 | ux поз-16 — Рубрика критичности 0 / 0,2 / 0,5 / 1 по сценарию… | — → JU | из «—»: шкалы серьёзности находок (ux 0 / 0,2 / 0,5 / 1 и Нильсен, axe; ворота site, FAIL / WARN ai-media, EG creative) — кандидат общей нормы; в §9 нет — JU решает, нужна ли |
| IN-0092 | ui C15 — Max-width 960–1024, 1200–1280 или fluid | — → NU | из «—»: мера строки в px (абзац 640–720, форма 480–640) ↔ ux № 44 (45–75 знаков); ширины контейнеров рядом с брейкпоинтами (§9 п. 9) |
| IN-0104 | ui C27 — Тёмный фон серый или чёрный | — → VI | из «—»: тёмный фон OKLCH L 13–19 % (ui C27) ↔ примета № 33 ui 11/04 «тонированный почти-чёрный» (#111) и cd 06/05 «тонированные нейтрали — только из токенов бренда» |
| IN-0105 | ui C28 — WCAG 2 или APCA; Lc 60 или 75 | — → GT | из «—»: контраст — WCAG AA жёстко, APCA по ролям: основа ворот контраста над медиа (ai-media X1, creative §9-07, §9-08, cu-12) |
| IN-0149 | site В-24 — Тройки форм J для приложения, листа ожидания, лид… | — → CN | из «—»: путь проверки «генерация K3» — Kimi в шаблоне нет (Р80): проверка — пилоты Ф9 (Claude Design) |
| IN-0199 | site вне-12 — ux `08-accessibility/02-…`, `03-…`: «переносится… | — → CN | из «—»: строка канона — доступность (правила WCAG как правила сборки) у ux 08, site переносит как есть |
| IN-0206 | text X2 — Длина — сигнал или ворота | — → TX | из «—»: длина — сигнал, не ворота (text) ↔ длины по ролям ux 07/01 §12 в жанре «интерфейс» (Р70): сигнал или ворота |
| IN-0226 | text X22 — Плотность маркеров как детектор ИИ: C/02 против D2 | — → VI | из «—»: COPY-M — порог слоп-прозы, не детектор ИИ: смысл примет для общего реестра (§9 п. 14) |
| IN-0228 | text X24 — Ярлыки секций: слоп (C, COPY-R-07) против конвенц… | — → VI | из «—»: ярлыки секций — конвенции без штрафа ↔ капс-надзаголовки (T12, свод-03, C10) и cd 06/05 |
| IN-0238 | text X34 — Кнопка первого экрана мероприятия: «Посмотреть пр… | — → TR | из «—»: позиция text для site: мероприятие — главное действие «регистрация»; у site типы landing-event, event-site; сторона kimi (kimi-10) → вход холста (Ф6) |
| IN-0281 | creative X-07 — Прелоадер: Paquet (блок прокрутки) против PLAN и E | — → GT | из «—»: прелоадер — site реш. 15.4 (только L2-кампании по явному решению), §Ж №23 (GT), ключ preloader (ck-12) |
| IN-0286 | creative X-12 — Имя переключателя: `data-motion="reduce"` (G) про… | — → NU | из «—»: имя переключателя data-motion="reduced" — ui 08/03, ui 09/04, ai-media 10/02: id-sync, по файлам согласовано |
| IN-0297 | creative X-23 — JS-бюджеты: стартовая таблица PLAN против A | — → GT | из «—»: JS-бюджеты уровней (канон creative A) ↔ site budgets.yaml, blender KIT §5 (§2.2 п. 11) |
| IN-0299 | creative X-25 — Видео-референс K3: ≤ 100 МБ (kimi T3c, PLAN) прот… | — → CN | из «—»: видео-референс — стык Kimi → вход холста (Р64, Ф6); вместе с §2-15, ck-05, ck-13, владение-10 |
| IN-0301 | creative X-27 — L0 → `none/subtle` (схема A v0) против `subtle` (… | — → GT | из «—»: L0 → subtle (creative) ↔ уровни движения cd 06/01 §6 (none / subtle / expressive / cinematic); вместе с X-28, ck-07 |
| IN-0334 | creative X-60 — Лицензия LottieFiles противоречит сама себе | — → CN | из «—»: лицензии — вместе с cz-02, X-61, R13, R12 |
| IN-0384 | ai-media X17 — Полноэкранный hero и LCP: «5 из 12» против синтет… | — → GT | из «—»: полноэкранный hero — LCP = H1 (12/12): к воротам LCP (WEB-01, site page-gates) |
| IN-0449 | blender R12 — Sketchfab Store, Fab и GLB на странице | — → CN | из «—»: магазинные 3D-модели — по согласованию, без вопроса — CC0: лицензии вместе с cz-02; сверить с Р72 («3D — только Blender и код») |
| IN-0493 | ux §2.1-15 — Длительность тоста | CN → CM | канон внутри ux — 04/08 §3.2; межбазовое — ui 06/05 «4 с»: решает CM вместе с № 11 |
| IN-0616 | text Д1 — Длины слотов (hero, подзаголовок, кнопка, тело) | CN → TX | из CN: канон длин слотов text — вместе с X3, kimi-06, свод-11 (длина hero; норма kimi → cd 06, Р68) и № 47 (длины по ролям, Р70) |
| IN-0731 | site K15 — не требовать маршрута для пустых заметок при `mod… | — → CN | из «—»: стык Kimi → единый вход холста (Р64): Ф6 решает, нужна ли частность |
| IN-0808 | text kimi-09 — Вопросы P1 и разбора брифа kimi — одним сообщение… | — → TR | из «—»: стык Kimi → бриф и вход холста: ≤ 7 вопросов — cd 06/01 (Р61), пакет — единый вход (Р64, Ф6) |
| IN-0809 | text kimi-10 — ACCEPTANCE мероприятия: главная кнопка первого эк… | — → TR | из «—»: вместе с X34; приёмка — вход холста (Р64, Ф6) |
| IN-0824 | text aim-08 — Проверка 38-ФЗ ст. 5 для картинок сверена — согла… | — → CN | из «—»: правовая пометка ИИ-контента — 38-ФЗ ст. 5 (картинки, сверено) и AI Act ст. 50(4) (тексты): одно место нормы |
| IN-0933 | creative ca-08 — не подделывать UA и не выключать `AutomationContr… | — → CN | из «—»: норма — контракт тройки §4 (обход антиботов, капч и лимитов запрещён), копия в коде ai-media — Ф8 |
| IN-0938 | creative ca-13 — локальный файл — корень по ссылкам `../` (или клю… | — → GT | из «—»: интерфейс page_accept (--root, как у motion_check) — одна копия, интерфейс — контракт (§2.2 п. 7) |
| IN-0941 | creative cb-02 — искать GSAP по `gsapVersions` и `_gsap`, не тольк… | — → CN | из «—»: поправка к коду blender — Ф8 |
| IN-0945 | creative cb-06 — ссылку «голографию — шейдером (F2)» перевести на… | — → CN | из «—»: ссылка blender → effect:holo-shader-bg каталога эффектов (не лаборатории) — Ф10 |
| IN-0946 | creative cb-07 — «Motion 13 — только DOM/SVG» → есть `motion/three… | — → CN | из «—»: правка текста blender (motion/three) — Ф10 |
| IN-0951 | creative cb-12 — правок нет; добавить `[практика]`: студии использ… | — → CN | из «—»: пометка [практика] у blender (Theatre.js) — Ф10 |
| IN-0952 | creative cb-13 — ветка «без HDRI»: студия кодом для PMREM как дешё… | — → VI | из «—»: свет продуктовой сцены без HDRI — к паспорту 3D-серии (свет) |
| IN-0957 | creative ck-05 — видео-референс: ≤ 20 МБ, 10–20 с, ≤ 1080p, H.264;… | — → CN | из «—»: видео-референс — вместе с X-25 |
| IN-0965 | creative ck-13 — имя кадра с десятыми секунды (наша копия — тоже) | — → CN | из «—»: видео-референс — вместе с X-25 |
| IN-0966 | creative ck-14 — к сведению: `effects.yaml` v0.3 — `page-transitio… | — → CN | из «—»: норма — effects.yaml creative (Р37), стыка нет — закрыть строкой |
| IN-0998 | blender 3.1 — `ux/08-accessibility/01-wcag22-as-build-rules.md`… | — → GT | из «—»: у ux о canvas и 3D нет ни слова — пробел; доступность 3D-блока — blender 09/05 §5, 01/02 §6 (указатель — Ф10) |

### 7.2. Новые строки

| строка | источник | узел | что |
|---|---|---|---|
| IN-1206 | claude-design реш. 6 | CN | (≈ 16:05) Главная цель уточнена: «я бы хотел, чтобы я в Claude Code мог полноценно пользо… |
| IN-1207 | claude-design реш. 7 | — | (≈ 16:10) Дайджест библиотек компонентов (7-й ролик `6XNhZu6mJlE`) — «упомянуть, записать… |
| IN-1224 | ux оговорки README | JU | Оговорки к числам: 12 пунктов |
| IN-1225 | ui что ненадёжно README | JU | Что ненадёжно: 6 пунктов |
| IN-1226 | ai-media что ненадёжно README | JU | Что ненадёжно: 9 пунктов |
| IN-1227 | blender оговорки README | JU | Оговорки к числам: 11 пунктов |
| IN-1228 | claude-design метки и доверие README | JU | Метки и доверие: 5 пунктов |
| IN-1229 | — §6.12 п. 3 | TX | «Прямого ввода роли в линтер нет» (light/text §1.2) против ключей CLI `--slot-type`, `--v… |
| IN-1230 | — §6.12 п. 9 | GT | «Для UI-проверок нет маркетингового профиля» (пилот §6 п.13) против creative `marketing_a… |
| IN-1231 | — §6.12 п. 11 | TR | Р67 говорит о «≈ 14 реальных конфликтах тройки», а по разбору site это конфликты site со… |
| IN-1242 | — §6.12 п. 25 | CM | Закрытый словарь `ui:` (Р29, Р76) возвращает контракт, снятый коммитом `1dd3a93` [Ф1-05 §… |

### 7.3. Только примечания (строк: 62, узел прежний)

- Решение в `note` у строк о Kimi (24): куда ушла норма (cd 06, Р68), стык (единый вход, Р64, Ф6), «K3» — id `ui_audit.py`
  (Р65) или выборка страниц Kimi в калибровке (пересчёт на пилотах), `K3-*`/`F-*` → `LOOK-*`/`HON-*` (Р62, Р76 п. 25).
- «Спорит ли с DECISIONS» у решений заказчика (29): процесс ресерча — «к скиллу не относится — не спорит»; creative `_common` 2 и
  PLAN 6 — «как норма скилла спорила бы с Р47, Р53»; site 15.12 — «спорит частично: Р76 п. 14, Р16»; blender 3, 4 — «снято
  Р59»; creative 5, 11, 19 — точнее к Р40.
- «Спорно» разобрано (4): № 31, № 45, C8, C30 — раздел 3.
- Легенды (5; у всех 16 строк легенд сменились счёт и `src_status`): счёт по таблице «Метка | …», прочие метки — в `note`; пункт 9 выжимки cd 06 — целиком (3 метки из 5 терялись,
  строка файла 23 → 33).

### 7.4. Скрипты и списки чтения

- `extract_rows.py`: легенды считаются по первой колонке таблицы «Метка | …», ссылки `[S7]`, `[C12]`, `[V08 B 03:03]` — не
  метки, род числительного; пункт 9 выжимки cd 06 — через разбор списка; новые группы: оговорки к числам и «что ненадёжно»
  (5 строк), решения заказчика claude-design 6–7, §6.12 пп. 3, 9, 11, 25. Повторный запуск — тот же файл.
- `registry.py`: `canon --registry --out` — пробный выпуск не трогает `kb/common/`; `canon` проверяет одно место у нормы,
  существование пути и «одна тема — одно место» и при ошибках файл не пишет (прежде писал в `kb/common/canon.tsv` всегда);
  `coverage` считает строки без узла или с узлом не из списка ошибкой (прежде молча пропускал — потеря); `source` понимает
  `§6.12 п. N`; номер строки после пути (`путь:120`) — предупреждение; подсказка о строках других узлов в `check`; точное
  сообщение о чужом префиксе `id`; `--rows` у `check` и `coverage`. Проверено на тестовом наборе во временной папке: ошибки
  схемы, путей, двух мест у нормы, повтора `id`, одной темы с двумя местами ловятся; `merge` → `canon` пишет файл только у
  чистого реестра; `coverage` на карте с тремя дырами даёт «без узла 3» и код 1.
- `reading.tsv`: чтение дополнено под перенесённые строки и под строки, чей раздел узел не читал: NU и GT — реестр creative «А»
  (движение), GT — «Д», «Е» и ai-media «Доставка и страница», VI — «Е», «И» и text [X22], [X24], TR — text [X34] и creative
  «Е», TX — text [X2], ui 02/06 §1 и §3, cd 06/05, NU и GT — cd 06/01 §6, CM — ux-низ §8, JU — ai-media «Что ненадёжно»,
  README cd «Метки и доверие», CN — решения заказчика cd, «Кто чем владеет» site и creative, реестр creative «Е».
