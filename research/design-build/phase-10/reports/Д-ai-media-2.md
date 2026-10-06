# Ф10 · зона данных Д-ai-media-2 — отчёт

База `ai-media`, папка `14-recipes`: рецепты `recipes/*.yaml`, схема рецепта и демо-пример `examples/demo-landing/`.
Коммит начала `1e0cd2a` (HEAD тот же, git — только чтение). Список зоны — 32 файла: правлено 24, не тронуто 8
(спецификации демо: их маркеры — пути, которые читает код). Сверх списка по слову координатора правлен один файл
папки — `examples/demo-landing/brand/specs/M-07a-floating-beans-chroma.spec.json`. Работа шла в два прохода: уборка
следов (пакеты замен 1 и 2) и доработка по решениям координатора (пакет 3). Один обрыв среды (403) — продолжено по
файлу передачи.

## Итог числами

| класс | было | после уборки | после доработки |
|---|---|---|---|
| raw | 153 | 68 | 17 |
| research | 3 | 0 | 0 |
| process | 183 | 117 | 17 |
| letters | 4 | 3 | 3 |
| words | 46 | 0 | 0 |
| **всего** | **389** | **188** | **37** |

Остаток 37: пути кадров в восьми спецификациях демо (34, читает код) и три ложных срабатывания класса letters.

## Файл → что сделано → маркеры до / после

Пути — от `kb/ai-media/14-recipes/`. В каждом рецепте: штамп шапки снят, `author` снято, блок `phase5:` снят, ключи
`numbers.phase5_*` → `live_*`; в колонке — остальное.

| файл | что сделано | до | после |
|---|---|---|---|
| `recipes/abstract-background.yaml` | 2 × `evidence`; «фаза 5:» в двух `note`; хвост пути в 1 числе; «отменено заказчиком»; 2 ключа `live_*` | 16 | 0 |
| `recipes/cinemagraph.yaml` | 5 × `evidence`; «отменено заказчиком»; `cmd` шага `masked-motion` без вызова скрипта; 1 ключ `live_*` | 18 | 0 |
| `recipes/favicons.yaml` | 1 × `evidence`; `cmd` шага `build` снято | 5 | 0 |
| `recipes/format-family.yaml` | 1 × `evidence`; хвост пути в 1 числе; «отменено заказчиком»; 2 источника-ролика; 2 ключа `live_*` | 15 | 0 |
| `recipes/hero-floating-object.yaml` | 4 × `evidence`; «фаза 5:» в `note`; хвост пути в 2 числах; 1 источник-ролик; 2 ключа `live_*` | 24 | 1 |
| `recipes/hero-loop.yaml` | 7 × `evidence`; «фаза 5» в 3 `note` и 2 `role`; «решение заказчика» в `role`; `spec.example`; хвост пути в 3 числах; 1 источник-ролик; `cmd` шага `crf-sweep` без вызова скрипта; 6 ключей `live_*` | 38 | 0 |
| `recipes/hero-pair.yaml` | 6 × `evidence` (одно — на несуществующую папку); «фаза 5:» в 2 `note`; `(H/02)` → `(ai-media 08/02)`; хвост пути в 4 числах; 5 ключей `live_*` | 28 | 0 |
| `recipes/hero-two-states.yaml` | 2 × `evidence`; «фаза 5:» в `note`; хвост пути в 1 числе; 1 источник-ролик; 1 ключ `live_*` | 15 | 0 |
| `recipes/icon-set.yaml` | 2 × `evidence`; хвост пути в 1 числе; `cmd` шага `sheet` — на `svg_sheet.py`; 1 ключ `live_*` | 16 | 0 |
| `recipes/icon3d-series.yaml` | 3 × `evidence`; «фаза 5:» в `note`; хвост пути в 1 числе; «отменено заказчиком»; 2 источника-ролика; `cmd` шага `render` снято, шага `deliver` — без вызова скрипта; 2 ключа `live_*` | 22 | 0 |
| `recipes/illustration-series.yaml` | 3 × `evidence`; «фаза 5:» в `note`; хвост пути в 4 числах; 2 источника-ролика; 5 ключей `live_*` | 28 | 0 |
| `recipes/marketplace-infographic.yaml` | 4 × `evidence`; 1 источник-ролик; `cmd` шага `render` снято | 9 | 0 |
| `recipes/og-cyrillic.yaml` | 3 × `evidence`; хвост пути в 2 числах; `cmd` шага `render` снято; 2 ключа `live_*` | 17 | 0 |
| `recipes/pdp-packshot-scene.yaml` | 4 × `evidence`; `spec.example`; «строка 8 L» → «строка 8 ai-media 12/04»; хвост пути в 2 числах; «отменено заказчиком»; 3 источника-ролика; 3 ключа `live_*` | 27 | 0 |
| `recipes/product-in-interior.yaml` | 2 × `evidence`; хвост пути в 1 числе; 3 источника-ролика; 1 ключ `live_*` | 16 | 0 |
| `recipes/recraft-illustration.yaml` | 2 × `evidence`; «фаза 5:» в 2 `note` маршрута и в `provenance.note`; `(G/02 process.py)` из `cmd`; хвост пути в 4 числах; 5 ключей `live_*` | 27 | 1 |
| `recipes/texture-pattern.yaml` | 3 × `evidence`; «отменено заказчиком»; 1 ключ `live_*` | 13 | 0 |
| `recipes/recipe.schema.json` | `$id` без суффикса исследования и с настоящей папкой; `title` без буквы и волны; свойство `phase5` снято; `cmd` шага не обязателен | 3 | 0 |
| `examples/demo-landing/brand/dna-forest-roast.json` | `brand` — без пути этикетки; `grade.note` — без «позиция M» и «в фазе 5»; `provenance.notes` — без буквы, даты и «фазы 5» | 5 | 1 |
| `examples/demo-landing/brand/tokens.json` | `$description`: `ui-research 09/04` → `ui 09/04`, штамп и путь этикетки сняты | 3 | 0 |
| `examples/demo-landing/css/site.css` | шапка: штамп, «шаблонов J», `(J/01: …)` → `(ai-media 10/01: …)` | 2 | 0 |
| `examples/demo-landing/index.html` | шапка: штамп, «банка E», «После фазы 5», `(J)`; подвал: «базы ai-media-research» → «базы ai-media», «после живой фазы» → «после генераций»; комментарий скрипта: «страницы J 00» → путь шаблона | 4 | 0 |
| `examples/demo-landing/js/focal.js` | шапка: штамп; «Формула — агент F (…)» → адрес статьи | 2 | 0 |
| `examples/demo-landing/js/hero-video.js` | шапка: штамп; путь опыта после «Проверено: Chromium 153» | 2 | 0 |
| `examples/demo-landing/brand/specs/M-01-hero-16x9-2k.spec.json` | не тронут | 2 | 2 |
| `examples/demo-landing/brand/specs/M-02-hero-phone-3x4-2k.spec.json` | не тронут | 2 | 2 |
| `examples/demo-landing/brand/specs/M-03-cinemagraph-steam.spec.json` | не тронут | 8 | 8 |
| `examples/demo-landing/brand/specs/M-04-icon3d-bean.spec.json` | не тронут | 4 | 4 |
| `examples/demo-landing/brand/specs/M-04-icon3d-box.spec.json` | не тронут | 4 | 4 |
| `examples/demo-landing/brand/specs/M-04-icon3d-cup.spec.json` | не тронут | 4 | 4 |
| `examples/demo-landing/brand/specs/M-06-hero-evening-edit.spec.json` | не тронут | 2 | 2 |
| `examples/demo-landing/brand/specs/M-07b-floating-beans-loop.spec.json` | не тронут | 8 | 8 |
| `examples/demo-landing/brand/specs/M-07a-floating-beans-chroma.spec.json` (вне списка зоны) | `notes`: «(I 09/02 §1.1: …» → «(ai-media 09/02 §1.1: …» | сканер букву не видел | — |

Сверка разобранных YAML и JSON «коммит начала → рабочее дерево»: снято `steps[].evidence` — 54, блоков `phase5` — 17,
`author` — 17, `spec.example` — 2, `steps[].cmd` — 4, свойство схемы `phase5`; переименовано ключей — 39; изменено
значений: `numbers` — 33 (27 хвостов пути, 6 «отменено заказчиком»), `sources[]` — 16, `route.steps[].note` — 13,
`route.steps[].role` — 3, `steps[].cmd` — 6, `provenance.note` — 2, `$id`, `title` и `required` шага в схеме, 3 поля
паспорта, `$description` токенов, `notes` спецификации M-07a. Числа, цены, модели, параметры, пороги, id тестов и
порядок записей не менялись; строки без следа — байт в байт. Всего 25 файлов, 116 строк добавлено, 351 снята.

## Решения первой уборки (подтверждены координатором)

1. **`author:`** (17 рецептов) — строка снята: значение целиком из буквы, волны и сессии; код поле не читает.
2. **`steps[].evidence: 99-raw/…`** (53 строки) — строка снята: значение — один путь сырья, сила шага записана рядом в
   `status: checked`.
3. **`spec.example: 99-raw/phase5/jobs/…`** (`hero-loop.yaml`, `pdp-packshot-scene.yaml`) — строка снята: файла задания в
   скилле нет, живые образцы — `spec.ancestors` там же.
4. **`sources:`** (16 строк в 9 рецептах) — путь `91-videos/…/<id>.md` заменён обозначением ролика базы `'[V:<id>]'`.
5. **`role`** двух шагов `hero-loop.yaml`: `'было «премиум»; фаза 5 — не для петли (routing v2: not)'` → `'не для петли
   (routing v2: not)'`; `финал 1080p (решение заказчика «…»)` → `финал 1080p`.
6. **« — отменено заказчиком 25.09»** после «не запускался» (6 значений) — снято, статус «не запускался» остался.
7. **Буквы перед адресом**: `(H/02)` → `(ai-media 08/02)`; «строка 8 L» → «строка 8 ai-media 12/04»; `(J/01: …)` →
   `(ai-media 10/01: …)` — файлы по адресам существуют. `(G/02 process.py)` — скрипт опыта, снят без замены.
8. **`$id` схемы** → `ai-media/14-recipes/recipes/recipe.schema.json`; на `$id` никто не ссылается.
9. **Видимый текст демо-страницы** (`index.html`, подвал): «демо-бренд базы ai-media», «В версии после генераций».

## Доработка по решениям координатора

1. **Блок `phase5:` снят целиком в 17 рецептах из 17**, свойство `phase5` — в схеме. До снятия: в `required` схемы блока
   нет; читателя нет (`stand_run.py` читает одноимённый ключ другого файла — `13-routing-matrix/stand/tasks.yaml`).
   С блоком ушли 28 путей заданий, 43 id в `reuse` и строка `estimate`.
2. **Ключи `numbers.phase5_*` → `live_*`**: 39 ключей в 15 рецептах (38 разных имён: `phase5_status` был в двух
   рецептах). Совпадений с существующими ключами нет. Схема эти ключи не называет (`numbers` — свободный объект).
   **Упоминаний в статьях `kb/ai-media/**/*.md` нет** — текстовой зоне вносить нечего; в `scripts/`, `references/` и
   машинных файлах других папок упоминаний тоже нет. (`phase5_test` в `13-routing-matrix/04-update-procedure.md` и
   `README.md` — ключ `routing.yaml`, не рецептов.)
3. **Восемь `cmd` со скриптом из `99-raw`** — преемник нашёлся у одного:

   | рецепт · шаг | было | стало |
   |---|---|---|
   | `icon-set.yaml` · `sheet` | `python3 99-raw/experiments/M/08-svg-favicons/build.py (лист 16/24/48, светлый/тёмный; спрайт)` | `python3 ../../scripts/ai-media/svg_sheet.py sheet new-icons/*.svg --out sheet/ --mode icons --current-color (лист 16/24/48, светлый/тёмный)` — преемник; спрайт он не собирает |
   | `cinemagraph.yaml` · `masked-motion` | `python3 99-raw/experiments/M/03-cinemagraph/masked_motion.py (keep_in в маске ≥ 0,75)` | `keep_in в маске ≥ 0,75` — вызов снят, описание шага осталось |
   | `hero-loop.yaml` · `crf-sweep` | `python3 99-raw/experiments/J/05-assets/sweep_crf.py <stem> (motion_keep ≥ 0,75)` | `motion_keep ≥ 0,75` — вызов снят, описание осталось |
   | `icon3d-series.yaml` · `deliver` | `python3 99-raw/experiments/M/01-icon3d-forms/make_icons.py (α < 0,06 → 0; кроп; на цвете секции)` | `α < 0,06 → 0; кроп; на цвете секции` — вызов снят, описание осталось |
   | `icon3d-series.yaml` · `render` | `flock -w 1800 $DDD_HOME/locks/blender.lock python3 ../../scripts/blender/blender_run.py 99-raw/experiments/M/01-icon3d-forms/render_forms.py -- <out>` | поле снято |
   | `favicons.yaml` · `build` | `python3 99-raw/experiments/M/08-svg-favicons/build.py` | поле снято |
   | `marketplace-infographic.yaml` · `render` | `flock -w 900 $DDD_HOME/locks/browser.lock python3 99-raw/experiments/M/06-og-marketplace/render.py` | поле снято |
   | `og-cyrillic.yaml` · `render` | то же | поле снято |

   - Преемник сверен по `--help` и прогоном: `svg_sheet.py sheet … --mode icons` рисует набор при 16/24/48 px на светлом
     и тёмном, `--current-color` — режим одноцветных иконок; команда из рецепта на двух пробных SVG дала `sheet.png`.
   - У `sweep_crf.py`, `masked_motion.py`, `make_icons.py`, `render_forms.py`, `render.py`, `build.py` (фавиконы)
     преемника по имени и по `--help` утилит `scripts/ai-media/` нет. `motion_keep` одного файла меряет
     `asset_audit.py … --master` — это уже отдельный шаг `audit-web` рецепта `hero-loop`.
   - **Отступление от буквы решения, на подтверждение**: у трёх шагов описание жило в самом `cmd` (в скобках после
     вызова) — другого поля для него у шага нет. Снял вызов скрипта, описание оставил значением `cmd`: так же, прозой,
     записаны другие шаги этих рецептов («маска зоны движения…», «глазом итоговую карточку…»). Поле снято целиком у
     четырёх шагов, где описания не было.
   - **Следствие для схемы**: `steps[].cmd` был обязательным — без правки четыре рецепта не проходили бы схему. В
     `recipe.schema.json` у шага `required` теперь `id`, `status`.
4. **`hero-pair.yaml`** — `evidence: 14-recipes/examples/demo-landing/measure` снято, `status: checked` шага остался.
   В рецептах осталось одно `evidence` — `hero-loop.yaml`, шаг `rife-bridge`: путь на живую утилиту.
5. **Спецификации демо не тронуты** — кадров в скилле нет (см. следующий раздел).
6. **`M-07a-floating-beans-chroma.spec.json:68`** — «(I 09/02 §1.1: …» → «(ai-media 09/02 §1.1: …»;
   `09-video-pipeline/02-cinemagraph-alpha.md` § 1.1 «Цвет ключа» существует. Файла нет в масках зоны — приёмка
   показывает его строкой «вне масок».

## Остаток маркеров — почему остаётся

- **Спецификации демо** — 8 файлов, 17 строк, 34 маркера (raw 17, process 17): `references[].src`,
  `motion.start_frame`, `motion.end_frame` ведут в `../../../../../99-raw/phase5/inputs/M/` — **кадров в скилле нет**;
  значения читает `prompt_compile.py` как данные задания, по решению координатора не трогаются. Места:
  `M-01-hero-16x9-2k.spec.json:164`; `M-02-hero-phone-3x4-2k.spec.json:149`; `M-03-cinemagraph-steam.spec.json:44, 49, 75,
  76`; `M-04-icon3d-bean.spec.json:84, 90`; `M-04-icon3d-box.spec.json:84, 90`; `M-04-icon3d-cup.spec.json:84, 90`;
  `M-06-hero-evening-edit.spec.json:126`; `M-07b-floating-beans-loop.spec.json:43, 48, 71, 72`.
- **Ложные срабатывания класса letters (3)**: `dna-forest-roast.json:182` — `(R5)`: id правила вывода грейда (ai-media
  06/01, его же пишет `vlm_to_dna.py`); `hero-floating-object.yaml` — `(T2)` в значении `live_alpha_image`: id пробы из
  таблицы ai-media 02/01; `recraft-illustration.yaml` — «у V4.1 Vector» в `live_cm02_reference`: имя модели.

## Ключи и значения, которые читает код

- **`references[].src`, `motion.start_frame`, `motion.end_frame`** спецификаций демо — `scripts/ai-media/prompt_compile.py`:
  `ref_by_id` (строка 258) сопоставляет правку с референсом по `id` или по `src`; `_abs_src` (1563) разворачивает путь от
  папки спецификации; `collect_inputs` (1572) кладёт пути в задание; проверка петли (360) сравнивает `start_frame` с
  `end_frame`. Шести файлов (`hero-16x9-stub.png`, `beans-chroma-stub.png`, `form_bean.png`, `form_box.png`,
  `form_cup.png`, `material_cube_ceramic.png`) нет ни в `99-raw`, ни в папке примера.
- Спецификации демо читает ещё `scripts/ai-media/tests/test_prompt_compile_x2.py` (M-01, M-02, M-06, M-07b); паспорт
  `brand/dna-forest-roast.json` — самопроверка `scripts/ai-media/vlm_to_dna.py`. Правленые поля паспорта и `notes`
  спецификации M-07a — свободный текст, код их не разбирает.
- Рецепты `recipes/*.yaml` и `recipe.schema.json` не читает ни одна утилита.

## Производные

Производных файлов в зоне нет: генератора и валидатора рецептов в скилле нет, файлы правятся руками.

## Для фикстур

Расхождений нет: `fixture_gen.py build --all --check` — четыре набора совпадают.

## Для текстов

- `kb/ai-media/14-recipes/README.md:22` — строка о `recipes/*.yaml`: называет снятый валидатор
  `scripts/ai-media/validate_recipes.py`, «задания фазы 5» (блока больше нет) и `sources` как «дайджесты и транскрипты
  роликов» (теперь обозначения `[V:<id>]`); числа прогонов лежат под ключами `numbers.live_*`.
- `kb/ai-media/00-glossary/glossary.md:567` — «Рецепт исполнимый»: звено «задание фазы 5».
- Статьи рецептов и README демо называют скрипты `99-raw/experiments/…`, вызовы которых сняты из `cmd`:
  `14-recipes/01-hero-recipes.md:413`, `02-series-product-recipes.md:314–317`, `03-vector-text-og-recipes.md:123, 338`,
  `examples/demo-landing/README.md:15–25`. Для листа иконок преемник — `svg_sheet.py sheet`.
- Метка «голос заказчика» осталась в трёх значениях (`live_crossfade_tail` рецепта `hero-loop`, `live_e08_blind_vote`
  рецепта `hero-pair`, `live_e11_reference` рецепта `illustration-series`) — метка базы, встречается в 15 md; в рецептах
  правится той же заменой, что в статьях.
- В значениях остались факты с историей цены и id: «(было 8,74)», «G-10 заменён CM-01», «(было gpt-image-2-5-flare)»,
  «routing v0 округляет до 12,8» (`illustration-series.yaml`, `recraft-illustration.yaml`, `abstract-background.yaml`).

## Что отдать соседям и оркестратору

- **Д-ai-media-1**: `examples/demo-landing/js/focal.js` и `hero-video.js` — побайтные копии
  `10-web-integration/pages/js/`. После правок обеих зон копии совпадают байт в байт — делать ничего не нужно.
- **Оркестратору**: маска файла `M-07a-floating-beans-chroma.spec.json` в `Д-ai-media-2.masks` не значится — добавить
  при приёмке. Остальные машинные файлы папки вне списка (`hero-16x9.spec.json`, `icon3d-base.spec.json`,
  `M-08-howto-illustrations-grid.spec.json`, `manifest.webmanifest`) следов не несут.
- **Сборка спрайта иконок и фавиконов**: утилиты в `scripts/ai-media/` нет — шаги `build` (favicons) и часть шага
  `sheet` (спрайт) остались без команды; формат доставки `svg-спрайт <symbol>` в рецепте `icon-set` записан.

## Файлы к снятию

Нет. Свойство `author` схемы (`recipe.schema.json:37–39`) осталось необязательным — ни один рецепт его не несёт.

## Проверки (после доработки)

| проверка | итог |
|---|---|
| разбор 32 файлов списка и M-07a | 33 из 33 |
| 17 рецептов против `recipe.schema.json` (Draft 2020-12) | 17 из 17 |
| `recipe.schema.json` против метасхемы | проходит |
| `prompt_compile.py validate` — 12 спецификаций демо | 12 из 12 OK |
| `scripts/ai-media/tests/test_prompt_compile_x2.py` | 15/15 |
| `scripts/ai-media/tests/test_prompt_compile.py` | 140/140 |
| `scripts/ai-media/tests/test_asset_audit.py`, `asset_audit.py selftest` | 128/128 |
| `vlm_to_dna.py selftest` | 48/48 |
| `stand_run.py selftest`, `svg_sheet.py --selftest` | OK |
| `smoke.py --only scripts/ai-media` | PASS 63, FAIL 0, XFAIL 0, XPASS 3 |
| `maint/sync_check.py` | генераторы OK 17, FAIL 0; копий расходится 0 |
| `maint/fixture_gen.py build --all --check` | совпадает, 4 набора |
| `git diff --check` по папке | чисто |
| `kbscan` зоны | 389 → 37 |
| `maint/accept.py --base 1e0cd2a --masks-file …/Д-ai-media-2.masks` | под масками 24 файла: разбор 20 — находок 0, схем 1; ссылки, код, следы — 0. Код выхода 1 из-за 348 файлов вне масок: правки соседних зон в общем дереве и M-07a; масок без изменённых файлов 8 — нетронутые спецификации |

Падений в чужих файлах не было. Пакеты замен — `~/.cache/design-deep-dive/out/f10/Д-ai-media-2/patch-1-recipes.py`,
`patch-2-demo.py`, `patch-3-decisions.py`.

## Вопросы

1. Три шага с описанием в `cmd` (`masked-motion`, `crf-sweep`, `deliver`): оставить описание значением `cmd`, как
   сделано, или снять поле целиком, потеряв параметры шага («keep_in в маске ≥ 0,75», «α < 0,06 → 0; кроп»)?
2. Схема: `cmd` шага стал необязательным — подтвердить; иначе четырём шагам без команды нужен текст.
3. Четыре шага остались только с `id` и `status` (`build`, два `render`, `render` форм): описание им даёт статья
   рецепта — вносить его в YAML текстовой зоне или владельцу базы?
