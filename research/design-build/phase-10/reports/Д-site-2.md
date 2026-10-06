# Д-site-2 — зона данных: машинные файлы базы site (все папки, кроме `02-site-types` и `09-ai-generation-evaluation`)

Коммит начала — `1e0cd2a`. В списке зоны 30 файлов, изменено 27 (три каркаса плана ассетов без правок). Замены —
шестью пакетами `kbpatch` (540 записей замен): `~/.cache/design-deep-dive/out/f10/Д-site-2/p1.py … p6.py`; спецификации
`s1.py … s6.py`, числа совпадений сняты с текста утилитой `gen.py` там же. Пути ниже — от `kb/site/`.

Маркеры по счётчику `kbscan`: **было 325 → стало 10** (kimi 33 → 0; research 26 → 0; process 90 → 0; decision 30 → 0;
raw 14 → 0; k3 7 → 0; plan 6 → 0; showcase 1 → 1; letters 104 → 4; words 14 → 5). Сверх счётчика сняты буквы
исполнителей, которые он не ловит («— I», «C 01 §1.2», «словарь B», «решение H»): всего изменено 569 строковых значений
и комментарии шапок.

## Правила, по которым шла правка

- Буква исполнителя → короткий адрес раздела базы: A — `site 01`, B — `site 02`, C — `site 03`, E — `site 04`,
  F — `site 05`, G — `site 06`, H и P — `site 07`, I — `site 08`, K — `site 09`, J — `site 10`; буква перед адресом
  статьи — «C 02 §2.3» → «site 03/02 §2.3», «F 03 §6.1» → «site 05/03 §6.1». В `page-gates.yaml` адрес внутри базы
  пишется без имени базы («I 08/03» → «08/03»), как остальные владельцы строк этого файла («07/03 §2.1»).
  Файлы по адресам существуют; номера § перенесены как были.
- Буквы базы text: B1 → `text 02-strategy-messaging/meaning.schema.yaml`, «B1 02 §4.1» → `text 02/02 §4.1`,
  B2 → `text 02/03` (§5.1, §5.4 сверены по заголовкам), H → `text 08` / `text 08/01 §7`, F → `text 05-voice-editorial`.
- Опыт → адрес нормы, где лежат те же числа (сверено поиском чисел): C/01 → `site 03/01`, C/02 → `site 03/03`,
  E/04 → `site 04/01`; в списках `evidence` и в метках `[проверено]` id опыта снят, числа и выборка остались.
  F/01, F/02, H/01, H/02, K/03, I/02 — id снят, слова «замер …» и числа остались.
- Прежний исполнитель макета: проекции полей схемы v0 — «(→ product.name брифа холста)», как в схеме v1; ссылки на его
  базу и чек-лист приёмки сняты; «пакет исполнителя kimi» → «пакет исполнителя макета».
- «Решение заказчика N», «PLAN №…», «PLAN поправка N», «решение 20» — сняты, норма осталась («выключен по умолчанию»,
  «умолчания — в default полей»).
- Владелец: `owner`, `x-owner` — имя базы и раздел без букв и волн.

## Файл → что сделано → маркеры до / после

| файл | что сделано | до | после |
|---|---|---|---|
| `01-foundations/site-brief.schema.json` | описание и `x-owner` без букв и волн; проекции kimi → бриф холста; ключ `x-kimi-projection` снят; `x-fill-legend`, `x-vocabulary` без PLAN.md и букв | 34 | 0 |
| `04-blocks/blocks.schema.json` | описание схемы v0.9, версии и статусы без букв; путь `99-raw` и опыты сняты; «решение 15» → «по умолчанию выключен» | 7 | 0 |
| `04-blocks/blocks.yaml` | легенда букв в шапке → строка об адресах; 30 «C NN §» → «site 03/NN §», буквы разделов → адреса; опыты → адреса норм; «поправка PLAN №…», «решение 15» сняты; `text_slot_defaults`: «(S1: запрос text)» и «оценка E» сняты | 44 | 0 |
| `04-blocks/page-plan.schema.json` | описание схемы v0.9 без букв, kimi и пути `99-raw`; буквы → адреса; заметка о подсхеме creative — текущим состоянием (подключена в схеме v1) | 19 | 0 |
| `05-conversion-funnels/lead-forms.yaml` | шапка без штампа; журнал «v0.9 → v1» (9 строк комментария) снят; `owner: "site"`; буквы и id опытов в `why`, `evidence` и комментариях сняты; строка шапки о событиях приведена к данным файла («здесь — id словаря событий») | 21 | 1 (words) |
| `06-multipage-ia/site-map.schema.json` | описание, `x-owner`, версии без букв и волн; kimi → «исполнитель макета»; буквы → адреса и имена файлов | 10 | 0 |
| `07-…/budgets.yaml` | шапка и `owner` без штампа; источник `S-plan20` снят; «решение 20», «аудит X», «S1» сняты; `owner: H` → `owner: head-kit.yaml` | 13 | 2 (showcase 1; words 1) |
| `07-…/crawlers.yaml` | шапка, `owner`, комментарий `status` без штампа; пути `99-raw` сняты; опыты H/01, H/02 → «замер корпуса text», «замер посадочных» | 14 | 0 |
| `07-…/events.yaml` | шапка и `owner` без штампа; «решение заказчика 15» снято; путь `99-raw` и «H2», «правка K» сняты; буквы → адреса | 12 | 0 |
| `07-…/head-kit.yaml` | шапка, `owner`, комментарий `status` без штампа; буквы → адреса; источники h01, h02, g01, w2-digests: заголовки без id опытов, `url` с путём сырья снят | 24 | 0 |
| `07-…/page-gates.yaml` | шапка и `owner` без штампа; `changelog` снят; `calibration` — текущим состоянием; `owner` 41 строки ворот — адресами; заметки без версий правки и id опытов; ссылки на прежнего исполнителя в `maps_to` сняты; **правка К1в: `method` и `threshold` строки SG-MOB-01** | 55 | 4 (letters) |
| `08-legal-trust-a11y/legal-requirements.yaml` | шапка без штампа; «решение заказчика 11» снято; буквы → адреса (`text 08/01 §7`) | 5 | 0 |
| `10-…/examples/corporate-b2b-stalkon/asset-plan.home.yaml` | без правок | 1 | 1 (words) |
| `10-…/examples/corporate-b2b-stalkon/site-brief.yaml` | шапка «ПРИМЕР v1»; `prepared_by`, `legal_note` без буквы; «решение 20» снято | 1 | 0 |
| `10-…/examples/corporate-b2b-stalkon/site-map.yaml` | шапка без буквы и пути несуществующего примера; буквы → адреса | 2 | 0 |
| `10-…/examples/lead-services-otves/asset-plan.home.yaml` | без правок | 1 | 1 (words) |
| `10-…/examples/lead-services-otves/plans/home.yaml` | шапка без «перевод плана E», опыта A/02; буквы → адреса; опыты → адреса норм; «решение заказчика 15» снято | 6 | 0 |
| `10-…/examples/lead-services-otves/site-brief.yaml` | шапка без буквы и пути несуществующего примера; `prepared_by`, `voice_ref`, `legal_note`, вопросы без букв и волн | 4 | 0 |
| `10-…/examples/lead-services-otves/stubs-sisters.yaml` | «ЗАГЛУШКА J» → «ЗАГЛУШКА»; опыт creative A/02 снят | 1 | 0 |
| `10-…/examples/saas-okoshko/asset-plan.home.yaml` | без правок | 1 | 1 (words) |
| `10-…/examples/saas-okoshko/facts.yaml` | шапка без пути `text-research/99-raw` и букв; «ДЕМО-факт E.» → «ДЕМО-факт.» ×17; `collected_by`, `who` без буквы; B2, H → адреса text | 9 | 0 |
| `10-…/examples/saas-okoshko/plans/home.yaml` | шапка; буквы → адреса | 6 | 0 |
| `10-…/examples/saas-okoshko/plans/{not-found,pricing,privacy,spasibo}.yaml` | шапка без буквы и `planlib.py`; «C 01 §3.1» → «site 03/01 §3.1»; «(I)» → «(site 08)» | 4 | 0 |
| `10-…/examples/saas-okoshko/site-brief.yaml` | шапка (строка «перевод демо-брифа E/03» снята); `prepared_by`, `agent`, заметки без букв | 3 | 0 |
| `10-…/schemas/blocks.schema.json` | как `04-blocks/blocks.schema.json` | 6 | 0 |
| `10-…/schemas/site-brief.schema.json` | `x-owner` без букв и волн; `x-fill-legend` без PLAN.md; буквы → адреса; «решения заказчика 15 и 20» сняты; блок `x-canvas-map` не тронут | 20 | 0 |
| `10-…/schemas/site-map.schema.json` | «решение 20» в двух описаниях снято | 2 | 0 |

## Остаток маркеров (10) и причина

- `07-…/page-gates.yaml:85, 250, 274, 344` — letters: «(accept)», «(S)», «(html-has-lang, S)», «(B)» — имя инструмента и
  буква серьёзности ворот B / S / D, не исполнитель.
- `05-conversion-funnels/lead-forms.yaml:445` — words: ключ данных `handoff` набора формы.
- `07-…/budgets.yaml:118` и каркасы `asset-plan.home.yaml` (stalkon:25, otves:24, okoshko:25) — words: «сессия» — слой
  веса `session_kb`.
- `07-…/budgets.yaml:60` — showcase: `basis: "blender 15-showcase: …"` — адрес существующей папки
  `kb/blender/15-showcase`; слово «испытание» и id «(T23)» сняты. Ссылка остаётся или уходит по решению о витрине.

Без адреса (файл по букве не определить — оставлено имя базы): `creative C`, `creative F`, `creative G`, опыты
`creative E/01`, `E/02`, `A/02`, `ai-media J/01`, `blender A/03`, `blender VD3 (T26)` в `budgets.yaml` и
`page-gates.yaml` → «creative», «ai-media», «blender» (у `creative C` — `creative 03-live-sites-measured`, как в
соседней строке источника).

Оставлено как условие проверки, счётчик не ловит: `crawlers.yaml`, `network_note` — «сняты через выход в ЕС (VPN,
Литва), Яндекса — с российского адреса, 24.09.2026»; `budgets.yaml`, `sources.S-M` — «pages.csv 15:23» (метка
выгрузки замера).

## Ключи и значения, которые читает код (не тронуты)

- **`structured_data: H`** — буква исполнителя как значение перечисления: `"const": "H"` в
  `06-multipage-ia/site-map.schema.json:359` и `10-…/schemas/site-map.schema.json:1025`, значение в примере
  `corporate-b2b-stalkon/site-map.yaml:617`. Читает проверка схемы (`site_validate.py`); менять — вместе со схемами,
  примерами и фикстурами `input-site`.
- **`owner` строки ворот** (`page-gates.yaml`, 63 строки) — `page_gates.py --selftest` требует непустое значение. Значения
  переписаны адресами и остались непустыми; строки с владельцем-буквой «K» получили адрес чек-листа `09/02` (поле
  `site_checklist` строки ведёт туда же).
- **`threshold.S`** строки ворот — `page_gates.py` читает как порог профиля (`profile.<путь>`): такие значения не
  тронуты; у SG-A11Y-01 правлена проза порога («счётчики I/02» → «только счётчики нарушений»).
- **Ключи с именами опытов и выборок** — код их не читает (поиск по `scripts/`), как ключи не тронуты:
  `budgets.yaml` — `sources.S-creative-C1` (текст `basis` с этим id `plan_to_assets.py` копирует в каркасы планов
  ассетов и фикстуры), `sources.S-M`, `creative_C_L2_desktop_first_screen_mb_no_video`,
  `creative_C_first_screen_video_max_mb`; `crawlers.yaml` — `observed.h01_corpus_d`, `observed.h02_sample_m`;
  `head-kit.yaml` — id источников `h01`, `h02`, `g01`, `g-06-02`, `w2-digests`.
- **«M»** в текстах `basis` (`budgets.yaml`, каркасы `asset-plan.home.yaml`) — имя выборки, определено в
  `sources.S-M` («замер M»); текст копируется генератором каркаса, поэтому оставлен.
- **Блок `x-canvas-map`** схемы брифа v1 — не тронут; `spec_check.py canvas-map` — error 0.

Снятые ключи и элементы (код не читает, ссылок на них нет): `x-kimi-projection` (схема брифа v0; файла
`site-brief.kimi-map.tsv` нет); `changelog` и `maps_to` строки SG-PERF-16 в `page-gates.yaml`, по одному элементу
`maps_to` с прежним исполнителем у SG-PERF-01, SG-PERF-06, SG-WEIGHT-01, SG-CONTENT-04, SG-MOB-01;
`sources.S-plan20` в `budgets.yaml`; `url` источников `h01`, `h02`, `g01` (путь `../99-raw/…`) и `w2-digests`
(путь `../91-videos/…`, файла нет) в `head-kit.yaml`. Остальная структура, id, перечисления, числа и пороги совпадают с
`1e0cd2a`: сравнение разобранных данных до и после — нестроковых расхождений 0.

## Правка зоны кода К1в

`07-…/page-gates.yaml`, строка `SG-MOB-01`: `method` и `threshold` заменены дословно текстом отчёта К1в (вылет телефонных
строк `acceptance[]` на ширинах приёмки, анатомия — запасной источник). `version: "1.3"` файла не менялась.

## Производные

Производных файлов из перечня брифа в списке зоны нет. Два места с пометкой о выводе:

- `04-blocks/blocks.yaml`, блок `text_slot_defaults` («ВЫВЕДЕНО … руками не править») — генератора в `scripts/` нет
  (`derive_text_defaults.py` отсутствует, ключ не читает ни одна утилита); правка внесена в данные: `copy: "нет правила
  text"` ×10, `note` ×10.
- Каркасы `asset-plan.home.yaml` трёх примеров («каркас из home.yaml (plan_to_assets.py)») — не правились.

## Для фикстур

`fixture_gen.py build --all --check` — совпадает, расхождений от правки нет. Следы в самих фикстурах (чужая зона):
`scripts/tests/fixtures/input-site/files/site/corp/` — шапки «# ПРИМЕР J v1 · … planlib.py; факты — демо J.»,
`prepared_by: Claude (агент site J, …)`, «карта G (06-multipage-ia/examples/site-map-corporate-b2b.yaml)»; замены те же,
что в примерах базы (`p4.py`).

## Для текстов

- `README.md:515`, `01-foundations/README.md:13–14, 21`, `01-foundations/03-site-brief.md:6, 11, 94, 350`,
  `01-foundations/01-how-visitors-decide.md:166`, `10-playbooks-contracts/01-procedure-brief-to-pages.md:323`,
  `04-blocks/03-slots-and-page-plan.md:349` — называют
  `site-brief.kimi-map.tsv` и `site-brief.example.yaml`: этих файлов в `01-foundations/` нет.
- `06-multipage-ia/README.md:15`, `01-sitemaps-templates-content-model.md:6, 107`,
  `02-navigation-linking-i18n.md:524` — `examples/site-map-corporate-b2b.yaml`: папки `06-multipage-ia/examples` нет.
- `04-blocks/03-slots-and-page-plan.md:78` — «выведено `derive_text_defaults.py`»: утилиты нет.
- `03-page-structure/03-first-screen-and-mobile.md`, `01-narratives-and-section-order.md:386`,
  `04-blocks/01-blocks-catalog.md:123, 444`, `02-blocks-catalog-specialized.md:343`, `04-blocks/README.md:38` — опыты
  C/01, C/02, E/04: в данных они заменены адресами этих статей.

## Файлы вне списка зоны со следами

20 планов примеров, которых нет в списке и масках зоны (счётчик их не ловит): `10-…/examples/corporate-b2b-stalkon/plans/*.yaml`
(15) и `lead-services-otves/plans/{consent,guide,not-found,privacy,spasibo}.yaml` (5) — шапка «# ПРИМЕР J v1 · …
planlib.py; факты — демо J.» и «(C 01 §3.1)». Готовый файл замен, сухой прогон прошёл, **не применён**:
`~/.cache/design-deep-dive/out/f10/Д-site-2/p-extra-examples.py` (40 замен).

## Файлы к снятию

В списке зоны нет. Ссылок на `kb/site/99-raw/` в данных зоны не осталось.

## Проверки

- Разбор: 30 из 30 (YAML 23, JSON 7); 7 схем проходят метасхему (`accept.py`).
- `site_validate.py --all` — error 0, warning 7 (SB-P02, SB-P03, SB-L03, PL-E02 — состав фактов и событий примеров);
  `--selftest` — SELFTEST OK.
- `spec_check.py canvas-map` — error 0, warning 0, info 12.
- `page_gates.py --selftest` — 116/116 PASS.
- `smoke.py --only scripts/site` — PASS 28, FAIL 0.
- Смоук читателей вне `scripts/site`, по одному вызову `--only <файл>`: `project/canvas_input.py`, `text/copydeck.py`,
  `creative/spec_check.py`, `claude-design/kit/kit_manifest.py`, `claude-design/mockup_checks.py`,
  `project/ds_coverage.py`, `project/design_audit.py`, `creative/recipe_check.py`, `creative/refs_client.py`,
  `creative/motion_check.py`, `maint/canon_check.py`, `maint/normcheck.py`, `blender/gate_check.py`,
  `maint/check_links.py` — 14 вызовов, PASS 31, FAIL 0; у `refs_client.py` XPASS 1 (самопроверка помечена ожидаемым
  провалом без браузера Brave, на этой машине он есть).
- `sync_check.py` — генераторы OK 17, FAIL 0; копий расходится 0.
- `fixture_gen.py build --all --check` — совпадает.
- `accept.py --base 1e0cd2a --masks-file …/Д-site-2.masks` — под масками 27 файлов: разбор 27, находок 0; следы 0;
  ссылки OK. Строка «маски» — FAIL: 341 изменённый файл других зон вне масок (на прогоне 01:34) и 3 маски без изменений
  (каркасы `asset-plan.home.yaml`).
- `kbscan` — 325 → 10, остаток разобран выше.

## Вопросы

1. `budgets.yaml:60` — ссылка `blender 15-showcase`: оставить или снять вместе с решением о витрине.
2. Значение `structured_data: H` в схемах карты сайта — переименовывать ли (контракт: две схемы, пример, фикстуры).
3. Ключи с именами опытов и выборок (`h01_corpus_d`, `h02_sample_m`, `S-creative-C1`, `S-M`, `creative_C_*`, id
   источников `h01`, `h02`, `g01`, `w2-digests`) — переименовывать ли; код их не читает, `S-creative-C1` и «M» уходят в
   каркасы планов ассетов и фикстуры текстом.
4. 20 планов примеров вне списка — применить ли готовый файл замен.
5. `page-gates.yaml`: после правки SG-MOB-01 `version` осталась «1.3» — поднимать ли версию, решает владелец ворот.
