# Д-creative-1 — машинные файлы базы creative: `06-effects-catalog`, `07-stack-implementation`, `08-uniqueness-anti-slop`

Коммит начала — `1e0cd2a`. Список зоны — 4 файла, тронуты все 4 пакетом точных замен (229 замен в пяти пакетах
`kbpatch.py`, из них 8 регулярных с проверкой числа совпадений; пятый пакет — доработка по решениям оркестратора).
Маркеры зоны: 506 → 3; целевые классы `raw`, `kimi`, `research`, `process`, `words` — 0; остаток — три обозначения
уровня, тега и пункта стороннего чек-листа. Id, перечисления, числа, пороги, порядок записей не менялись; из структуры
ушли ключ `src` замеров (345), блок `id_map` каталога (29 записей) со свойством схемы, альтернатива стороннего
исполнителя в шаблоне `external_ref`, один элемент `evidence` и 12 элементов `refs` с id опытов — сверено разбором «до
и после» по путям значений. Git — только чтение. Пути ниже — от `.claude/skills/design-deep-dive/kb/creative/`,
утилиты — от корня скилла.

## Файлы

Маркеры — сумма по классам `kbscan.py` с классами `--extra`; «→» — до и после.

| файл | что сделано | маркеры |
|---|---|---|
| `06-effects-catalog/effects.schema.json` | `$id` → `urn:app-design:creative:effects:0` (вид остальных схем базы); `title` без суффикса исследования; `x-owner` → `creative · 06-effects-catalog`; 13 описаний (`description`): буквы исполнителей, «волна», даты и номера правок аудита, «контракт тройки» — сняты, смысл поля остался; `check_refs.py` → живая `registry_check.py`; шаблон `external_ref` — без альтернативы с именем стороннего исполнителя (оба вхождения); свойство `id_map` снято | 9 → 0 |
| `06-effects-catalog/effects.yaml` | штамп шапки и строка о сборке скриптом из `99-raw` сняты; `owner` → `creative · 06-effects-catalog`; ключ `src` у замеров `cost.measured.<режим>` снят (345, значение — только путь опыта); блок `id_map` снят (29 записей); метки доказательности с путём опыта → метка с условием без пути (9), путь без слов — элемент снят (1); id опытов в `rules`, `note` (12 мест); буквы дайджестов роликов `(W1)`, `(W2)` (12); буква исполнителя перед адресом → адрес базы (`creative 03/01 §4`, `creative 05/01 §5.4`, `05-motion/01 §4.2`); номера правок аудита, «решение оркестратора», «было … до» — сняты, норма осталась | 402 → 1 |
| `07-stack-implementation/stack.yaml` | `measure`: пути `99-raw/…` и имена файлов опыта сняты; `refs`: элементы с id опытов сняты (12 элементов в 11 записях), путь дайджеста ролика → `[V:<id>]`, буква исполнителя → путь статьи; `risks`, `when`, `practice`, `levels`: «C:», «(G/02)», «(W2)», «(H)», «(меряет F)» — сняты или заменены адресом; 4 комментария у `size_br` — без id опытов | 23 → 0 |
| `08-uniqueness-anti-slop/cliche-registry.yaml` | штамп шапки и строки о калибровке и опытах сняты, путь проверки исправлен на `../../../scripts/creative/registry_check.py`; `owner` → `creative · 08-uniqueness-anti-slop`; `[данные: H/02 …]` → метка без id опыта (40), `[данные: C, H/02]` → `[данные: 03-live-sites-measured]`; «поправка PLAN», «аудит UI / BLENDER §…» — сняты, норма осталась (16); буквы исполнителей в `neighbors`, `levels`, `signals`, `detect`, `justify_if`, `replace_with`, `threshold` → адрес базы или сняты | 72 → 2 |

По классам (вся зона): `raw` 363 → 0 · `research` 5 → 0 · `process` 81 → 0 · `words` 3 → 0 · `kimi` 1 → 0 ·
`letters` 53 → 3. Строк: `effects.yaml` 3788 → 3720, `effects.schema.json` 174 → 171, `cliche-registry.yaml`
1554 → 1552, `stack.yaml` без изменения.

Формы вхождений каталога приёмов и решение по каждой:
- `, src: 99-raw/experiments/F/<опыт>[/bench]}` — последний ключ записи режима замера (11 видов хвоста, 345 раз, в том
  числе 36 раз отдельной строкой): ключ снят вместе с запятой; код `src` не читает, схема поле `measured` не описывает.
- `'[проверено: 99-raw/… — <условие>]'` (5) и `'[проверено у E|G: 99-raw/…]'` (4): путь и буква сняты, условие осталось;
  `'[проверено: 99-raw/…, 09-reveal-bottom]'` (1) — рядом уже стоит `'[проверено]'`, элемент снят.
- `(F/09)`, `(F2/15, бенч)`, `(E/02)`, `(F2/16 flip_min.html)`, `G/01` в тексте правил и заметок: id опыта снят, слова
  условия остались.
- `C 03/01 §N` (9) → `creative 03/01 §N`; `E 05/01 §5.4`, `D 04/03 §4.1`, `E 05/03 §2.4`, `E 03 §2.1` → `creative NN/MM §N`;
  `E 05-motion/01 §N` → `05-motion/01 §N` (адрес внутри базы). Все разделы найдены в файлах (24 адреса сверены).
- Буква как владелец нормы: `реестр H` → «реестр клише», `по G` → `07-stack-implementation`, `A:` →
  `ambition-levels.yaml`, `(C: …)`, `(D: …)` — буква снята.

Соответствие букв адресам базы (по папкам `kb/creative/NN-*`): A — 01, B — 02, C — 03, D — 04, E — 05, F — 06, G — 07,
H — 08, I и K — 09, J — 10; W1, W2 — дайджесты роликов, X, S1, S1b — аудит и его правки (сняты).

## Остаток маркеров

- `06-effects-catalog/effects.yaml:2011` — `letters`: «(L0)», «(L1)» — уровни амбиций подачи.
- `08-uniqueness-anti-slop/cliche-registry.yaml:178` — `letters`: «у H1–H2» — теги заголовков.
- `08-uniqueness-anti-slop/cliche-registry.yaml:723` — `letters`: «(E7)» — пункт чек-листа Hallmark, не исполнитель.

Вне классов скана оставлено: `S1, S2, S22`, `S5`, `S6` в `refs` стека — id источников статьи `01-stack-choice.md`;
`B`, `S`, `D` — шкала серьёзности; `C`, `H`, `L` — оси OKLCH; `higgsfield C3`, `Hallmark E3` — коды сторонних каталогов;
«живая фаза» в двух метках `[гипотеза]` и `rules` — условие проверки («людям не показано»).

## Ключи и значения, которые читает код

- `effects.schema.json:73`, шаблон `implementation.external_ref`: перечень баз — `blender|ai-media|ui|ux|site|text` в
  обеих альтернативах. Шаблон исполняет валидатор схемы: все 37 значений `external_ref` каталога его проходят, значение
  с префиксом снятого исполнителя — ошибка схемы (проверено отрицательным случаем).
- `cliche-registry.yaml`, ключ `k3_allow` (53 записи, поле `fields`, текст `compat.mockup_checks`): идентификатор
  контракта арт-дирекции — читают `scripts/creative/registry_check.py` (`REQ`, сверка с `tells.yaml#checks`),
  `scripts/creative/ad_check.py`, `scripts/project/canvas_input.py` и файлы проектов (`decisions[].k3_allow`,
  `exclusions.k3_allow` схемы `art-direction`). Не тронут; там же значение `k3:stats` (`crosswalk_external`, строка 106).
- `effects.yaml`, `implementation.demo` и `variants[].demo` (105 строк, 15 — `null`): путь `lab/<id>/`, схема держит
  его шаблоном `^lab/[a-z0-9-]+/`; папки `06-effects-catalog/lab/` в базе нет, код поле не читает. Не тронуто.
- Имена утилит, которых нет в `scripts/`: `effect_bench.py` (`effects.yaml` — шапка, `method`, три `cost.note`;
  схема — описания `status`, `measured`), `effects_probe.py` (`cliche-registry.yaml`, 28 строк: `detect_codes`,
  `signals`, `detect.auto`). Оставлены как название метода замера; буква исполнителя при них снята.
- `version`, `x-version` (0.3), `checked_at`, `x-checked`, `status: draft` (реестр, стек) — данные, не менялись.

## Блок `id_map`

Блок каталога (29 записей) и свойство `id_map` схемы сняты. До снятия: у 29 записей из 29 `old` равен `new`, каждый id
есть в каталоге, заметка начинается с «без изменений» — соответствия блок не нёс. Поиск `id_map`:
- `scripts/`, `references/`, `SKILL.md` — 0 вхождений: код блок не читает;
- машинные файлы `kb/creative/**` — после снятия одно вхождение в чужой зоне:
  `01-creative-direction/drafts-for-site/treatment.v0.schema.json:25`, поле `x-effect-ids-note` — «соответствие id
  каталога эффектов — 06-effects-catalog/effects.yaml, id_map» (ссылка на снятый блок — зоне Д-creative-2);
- статьи md (не правились):
  - `06-effects-catalog/README.md:5` — строка таблицы о `effects.yaml`;
  - `06-effects-catalog/01-effects-catalog.md:77` — «29 id A сохранены (`id_map`)»;
  - `09-ai-execution-evaluation/01-presentation-spec-and-block-treatments.md:360` — источник [S12];
  - `CONTRADICTIONS.md:495` — «`id_map` — оба „без изменений“»;
- материал к разбору: `99-raw/reports/wave4-X-audit.md` — уходит вместе с `99-raw`.

## Производные

Блоки `x-effect-levels` схем подачи собирает `scripts/creative/spec_check.py levels` из `level_min` и id каталога:
правка каталога их не задела — `spec_check.py levels --check` — 0 ошибок, строка `creative-levels` в `sync_check.py` — OK.
Производных файлов в списке зоны нет.

## Для фикстур

Расхождений от правки нет: строка `fixtures` в `sync_check.py` (`fixture_gen.py build --all --check`) — OK. Попутно:
штамп «creative-research · … · агент I · волна 3» стоит строкой 2 в `scripts/tests/fixtures/{input-landing,input-site,
package-landing-defects}/files/design/*/motion/home.motion-spec.yaml` — файлы фикстур оркестратора.

## Для текстов

- `06-effects-catalog/README.md` (строка схемы и строка каталога), `03-effects-lab-method.md`, `README.md:478` базы,
  `CONTRADICTIONS.md:125`: «сборка `99-raw/experiments/F/07-yaml/build_effects.py`, правьте `entries.py`» — каталог
  правится по месту, строка шапки о сборке снята.
- `06-effects-catalog/01-effects-catalog.md:73`: «контракт §3 п.6 + поля E» — из описания схемы снято.
- `README.md` базы: `check_refs.py` — сверку статуса ведёт `registry_check.py` (описание `cliche.status` схемы).
- Упоминания `id_map` — четыре статьи, список в разделе «Блок `id_map`».
- Поле `src` замеров статьи базы не описывают (поиск по `06-effects-catalog/*.md`) — правки текста по нему нет.

## Файлы к снятию

Нет.

## Проверки

- Разбор: 4 файла читаются; схема проходит метасхему Draft 2020-12; `effects.yaml` против схемы — 0 ошибок (59
  записей), пример схемы — 0. Каталог без `id_map` и схема без `id_map` и альтернативы шаблона равны состоянию до
  доработки во всём остальном (сверка разбором).
- Читатели: `spec_check.py levels --check` — 0 / 0 / 0; `registry_check.py` — ошибок 0, расхождений 0 (53 записи);
  `validate_stack.py` — OK (51 запись).
- `smoke.py --only` (подстрока пути): `scripts/creative` — PASS 21, FAIL 0, XPASS 1 (как до правки); `scripts/ui` —
  PASS 11, FAIL 0; `scripts/site` — PASS 28, FAIL 0. До доработки, на правках реестра и стека: `claude-design` —
  PASS 29, `project` — PASS 33, FAIL 0.
- `sync_check.py` — генераторы OK 17, FAIL 0; копии и описания — OK.
- `accept.py --base 1e0cd2a --masks-file …/Д-creative-1.masks` — под масками 4: разбор OK (схем 1), следы OK; строка
  «маски» — FAIL из-за 369 файлов других зон в общем дереве, файлов этой зоны вне масок нет.
- `git diff --check` по трём папкам — чисто.

## Решения оркестратора

1. `$id` схемы каталога — `urn:app-design:creative:effects:0` (версия — старшая цифра `x-version`); по `$id` схему
   никто не ищет. Прежний вид `https://<база>-research.local/…` остался у двух схем ai-media (`asset-spec`, `visual-dna`).
2. Ключ `src` у `cost.measured.<режим>` снят целиком: число замера остаётся, путь опыта не нужен.
3. Ключ `k3_allow` не меняется; альтернатива стороннего исполнителя в шаблоне `external_ref` снята.
4. Блок `id_map` каталога и свойство схемы сняты; упоминания в статьях перечислены, в чужом машинном файле — названо.
