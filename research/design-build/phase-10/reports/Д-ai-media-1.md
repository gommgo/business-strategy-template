# Д-ai-media-1 — машинные файлы базы ai-media, кроме `14-recipes`

Коммит начала — `1e0cd2a`. Список зоны — 40 файлов: 39 изменены, 1 не тронут (`05-prompting/asset-plan.schema.json`).
Правки — четырьмя пакетами точных замен `kbpatch.py` (файлы замен `p1_routing.py`, `p2_rest.py`, `p3_letters.py`,
`p4_followup.py` в
`$DDD_HOME/out/f10/Д-ai-media-1/`), сериализатором ни один файл не пересобирался. Пути `kb/…`, `scripts/…` — от
`.claude/skills/design-deep-dive/`.

## Маркеры «было → стало» (kbscan по списку зоны)

| класс | было | стало |
|---|---|---|
| raw | 141 | 26 |
| research | 8 | 0 |
| process | 299 | 21 |
| decision | 8 | 0 |
| showcase | 1 | 1 |
| letters | 57 | 23 |
| words | 5 | 2 |
| **сумма** | **519** | **73** |

Из 73 оставшихся: 47 — значения и ключ, которые читает код (их правит зона кода вместе со `stand_run.py` и
`prompt_compile.py`); 25 — не след (id строк таблицы источников, имена моделей и кодеков, уровень WCAG, имя поля схемы);
1 — ссылка на витрину blender.

## Файл → что сделано → маркеры до / после

| файл (`kb/ai-media/…`) | что сделано | до | после |
|---|---|---|---|
| `05-prompting/asset-plan.schema.json` | не тронут: ссылка на витрину blender — остаток | 1 | 1 |
| `05-prompting/asset-spec.schema.json` | `$id` → `urn:app-design:ai-media:asset-spec:0.2`; `x-changelog` снят (код не читает); штамп волн и букв в `description` (5 мест); `ui-research` → `ui` | 9 | 0 |
| `05-prompting/dialects.yaml` | `catalog_snapshot` → `$DDD_HOME/cache/ai-media/polza/…`; `catalog_extract` снят (путь сырья, код не читает); `run` снят у 9 записей `ab_results`; источник семейства bria-fibo и `channels.routerai.catalog` — название без пути; «п. 16», «фаза 5», W3; ключ `phase5` семейства `bria-fibo` → `note`; фраза «решение заказчика» снята (2 места) | 32 | 6 |
| `06-art-direction-consistency/examples/dna-warm-consumer.json` | id опытов в заметках → адрес статьи или сняты; пути входов не тронуты | 12 | 7 |
| `06-art-direction-consistency/visual-dna.schema.json` | `$id` → `urn:app-design:ai-media:visual-dna:0.1`; описания: `ui-research` → `ui`, опыты F/NN и буквы A, W5 → адреса статей | 9 | 1 |
| `10-web-integration/pages/00-hero-summary.html` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 7 | 0 |
| `10-web-integration/pages/01-image-hero.html` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 5 | 0 |
| `10-web-integration/pages/02-video-hero.html` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 3 | 0 |
| `10-web-integration/pages/02b-video-source-media.html` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 1 | 0 |
| `10-web-integration/pages/03-alpha-object-hero.html` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 3 | 0 |
| `10-web-integration/pages/04-two-states-spotlight.html` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 3 | 0 |
| `10-web-integration/pages/05-scroll-sequence.html` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 2 | 0 |
| `10-web-integration/pages/07-effects-grain-layers.html` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 5 | 0 |
| `10-web-integration/pages/08-svg-icons-favicons.html` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 3 | 0 |
| `10-web-integration/pages/css/base.css` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 4 | 0 |
| `10-web-integration/pages/js/focal.js` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 2 | 0 |
| `10-web-integration/pages/js/hero-video.js` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 2 | 0 |
| `10-web-integration/pages/js/scroll-seq.js` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 2 | 0 |
| `10-web-integration/pages/js/spotlight.js` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 1 | 0 |
| `10-web-integration/pages/js/stacked-alpha.js` | штамп «Агент J, волна 3, дата · проверено: 99-raw/…» снят, условия проверки (Chromium 153, размеры) остались; id опытов в комментариях → адрес статьи или сняты | 2 | 0 |
| `11-evaluation-qa/rubrics/bg-abstract.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 6 | 0 |
| `11-evaluation-qa/rubrics/cutout.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 6 | 0 |
| `11-evaluation-qa/rubrics/edit.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 7 | 0 |
| `11-evaluation-qa/rubrics/hero-photo.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 10 | 0 |
| `11-evaluation-qa/rubrics/icon3d.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 6 | 0 |
| `11-evaluation-qa/rubrics/illustration.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 6 | 0 |
| `11-evaluation-qa/rubrics/product.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 7 | 0 |
| `11-evaluation-qa/rubrics/series.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 7 | 0 |
| `11-evaluation-qa/rubrics/svg-icon.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 8 | 0 |
| `11-evaluation-qa/rubrics/text-image.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 9 | 0 |
| `11-evaluation-qa/rubrics/video-loop.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 8 | 0 |
| `11-evaluation-qa/rubrics/video-product.rubric.json` | `author` → `ai-media`; служебные поля (`checklist_note`, `not_allowed`, `decision`, `automated.checks`, `sources`, `defect_questions[].source`): опыты и буквы → адреса статей; в `human[]` id опыта снят, буква перед адресом → `ai-media NN/MM`; вопросы `q` не тронуты | 7 | 0 |
| `11-evaluation-qa/thresholds.yaml` | шапка без штампа; `source` порогов: буква перед адресом → `ai-media NN/MM` (61), опыт → адрес статьи-нормы, «K:», E-helper, id предложений W/C/A сняты | 44 | 2 |
| `13-routing-matrix/routing.yaml` | 100 замен: пути сырья в `src` (40), метках (22) и прозе (17) сняты; «фаза 5» → «живой прогон» (26); номера решений «п. N» (8); буквы исполнителей → адрес статьи; `evidence` записи not_routes снят (одни пути); правка К7 поля `post` маршрута VEC-ICON-FILLED; фраза «решение заказчика» снята (7 мест и комментарий блока `not_routes`); нарезка листа иконок — та же формулировка в `defaults.delivery.svg` и в `note` варианта | 225 | 22 |
| `13-routing-matrix/stand/briefs/S01-hero-interior.spec.json` | `notes`: штамп и путь сырья сняты | 1 | 0 |
| `13-routing-matrix/stand/briefs/S03-product-scene.spec.json` | `notes`: штамп и путь сырья сняты | 3 | 2 |
| `13-routing-matrix/stand/briefs/S04-illustr-onboarding.spec.json` | `notes`: штамп и путь сырья сняты | 1 | 0 |
| `13-routing-matrix/stand/briefs/S05-bg-abstract.spec.json` | `notes`: штамп и путь сырья сняты | 2 | 0 |
| `13-routing-matrix/stand/briefs/S09-product-tea-count.spec.json` | `notes`: штамп и путь сырья сняты | 2 | 0 |
| `13-routing-matrix/stand/tasks.yaml` | комментарии (шапка, два заголовка блоков, заметка о заглушке), заметка пресета nbpro-2k; `phase5: later` у задач S21–S24 снят (код не читает); остальные значения рецептов не тронуты — читает код | 46 | 32 |

## Решения по формам (каждая форма решена один раз)

1. **Путь сырья в доказательстве живого прогона** (`src` записи `class: run`): хвост «— 99-raw/…» с именами листов,
   ключей и журналов снят вместе с тире — 40 вхождений одной регулярной заменой; запись SC-04 (два пути в середине
   фразы) и запись G-01…G-06 — точными заменами.
2. **Метка `[проверено: 99-raw/…, условия]`** → `[проверено: условия]` — 21 вхождение регулярной заменой и одно
   точной (`[проверено: шов 1,28; …]`). Условия, выборка и числа остались. Шапка матрицы: «`[проверено: путь от корня
   базы]`» → «`[проверено: условия]`».
3. **«Фаза 5»** (26 вхождений в матрице, по одному в `dialects.yaml` и `thresholds.yaml`) → «живой прогон» в нужном
   падеже — так класс доказательства `run` назван в `enums.evidence_class` самой матрицы; числа прогонов остались.
4. **Решение заказчика исследования** — след: номер «(п. 12)…(п. 16)» и сама фраза «решение заказчика 25.09» сняты, норма
   осталась (7 мест матрицы, 1 в диалектах; та же фраза без даты — комментарий блока `not_routes` матрицы и запись
   D2-12 диалектов). Другие упоминания заказчика в доказательствах не тронуты: «голос заказчика вслепую», «выбор
   заказчика», «вердикт заказчика 25.09 13:40: «…»» (`routing.yaml`:72), «отменено заказчиком 25.09» (19 мест матрицы) —
   см. вопрос.
5. **Буква исполнителя перед адресом** («A 01/03 §5.1», «H 08-image-post-processing/01 §5», «L 04 §2») → короткий адрес
   базы «ai-media NN/MM §N»: `thresholds.yaml` — 61, рубрики — служебные поля, схема паспорта — 5, матрица — 5. Файлы по
   всем адресам существуют (`kb/ai-media/NN-*/MM-*`).
6. **Id опыта «X/NN»** → адрес статьи-нормы, где он однозначен: F/02 и F/03 → 06/03, F/04 и F/05 → 06/04,
   F/06 → 06/02, F/07 → 06/01, G/01 → 07/01, G/02, G/03 и P/07 → 07/02, G/05 → 07/04, H/00 и H/01 → 08/01, H/02 и H/03 →
   08/02, H/05 и H/06 → 08/03, I/02 → 09/01, I/03 → 09/02, I/04 → 09/03, J/01 → 10/01, J/03, J/06 → 10/03, K/01, K/02,
   K/03 → 11/01, C2/02 → 04/03. Где адрес нормы уже стоял рядом или статьи нет (A/04, P/06, B/10, J/05, J/07, blender A/06) — id снят.
   Соответствие взято поиском id опыта и ключевого факта по статьям базы.
7. **Голая буква как источник**: (C1) → `ai-media 03/03`, (C2) → `ai-media 04/03` (арены — `04/01`), (L) → `ai-media
   12/01 §5` и `12/03`, (K) → `ai-media 11/01` или снята, (B2), (W2), W5, W6, W1-8, W3-13, «агент V», «агенты U и V»,
   «разбор V», «N 24.09», «D2b», «оркестратор, сессия 5», «задания G» — сняты. В рубриках метка дайджеста практиков
   в поле `source` вопроса («W2: «сток»») → «практика: «сток»» (в матрице тот же источник носит метку `[практика]`).
   В `human[]` рубрик id опыта снят (K/01 — 2, I/03 — 1), буква перед адресом → `ai-media NN/MM` (3 пункта); вопросы
   `q` судьи не тронуты.
8. **Id тестов стенда через дефис** (E-08, F-04, D2-01, CM-01, MS-05, VM-01, T7, K-05 …) — не тронуты: это id записей
   доказательств внутри матрицы (метка, `note`, `gate`, `decides` ссылаются на запись `class: run` того же маршрута),
   E-NN — ещё и id рецептов `stand/tasks.yaml`. kbscan их маркером не считает.
9. **(J1)…(J26)** — id строк таблицы источников `13-routing-matrix/02-existing-evidence.md §2.1`, не буква
   исполнителя: оставлены (см. «Для текстов»).
10. **Поле из одних путей сырья** снято: `defaults.not_routes[0].evidence` матрицы, `catalog_extract` и `run` девяти
    записей `ab_results` диалектов. Код эти поля не читает (поиск ключей по `scripts/`). **Ключ с именем фазы, который
    код не читает**: `phase5: later` у задач S21–S24 стенда снят; `phase5` семейства `bria-fibo` в диалектах → `note`.
11. **Журнал версий** `x-changelog` схемы `asset-spec` снят (поиск по `scripts/` — 0 чтений).
12. **`$id` двух схем** — `https://ai-media-research.local/…` (механика их не взяла: не `urn`) →
    `urn:app-design:ai-media:asset-spec:0.2` и `urn:app-design:ai-media:visual-dna:0.1` по образцу соседних схем базы;
    по `$id` на них никто не ссылается (поиск по `kb/` и `scripts/`).
13. **Правка сверх следов (отчёт К7)**: `routing.yaml`, маршрут `VEC-ICON-FILLED`, поле `post`: «сетка иконок одним
    SVG → нарезка по рамкам путей (…)» → «сетка иконок одним SVG → нарезка по ячейкам сетки из задания
    (`split_recraft.py --grid … --names …`)». Та же формулировка — в `defaults.delivery.svg` (строка 86, числа «8 SVG по
    0,9–2,5 КБ» остались в скобке) и в `note` основного варианта маршрута (строка 804).

## Остаток маркеров (файл:строка — почему остаётся)

**Читает код — не тронуто** (подробности — следующий раздел):
- `13-routing-matrix/stand/tasks.yaml`:10, 61, 66, 68, 151, 186, 202, 203, 213, 215, 229–232, 240, 241, 250, 251.
- `05-prompting/dialects.yaml`:531, 533, 540, 541, 549, 550.
- `06-art-direction-consistency/examples/dna-warm-consumer.json`:178, 281, 289, 297.
- `13-routing-matrix/stand/briefs/S03-product-scene.spec.json`:91.

**Не след**:
- `13-routing-matrix/routing.yaml`:117, 118, 150, 152, 178, 181, 235, 268, 289, 347, 348, 411, 453, 496, 497, 792 —
  (J1)…(J25): id строк таблицы источников `02-existing-evidence.md §2.1`.
- `routing.yaml`:44 — «у H3 Max» — модель MiniMax Hailuo 3; :78, :487, :500 — «у Z-Image» — модель, (T6), (T7) — id
  проверки канала; :536 — (T9) — то же.
- `routing.yaml`:781 — «Claude в сессии 0 ₽»: сессия Claude Code и цена, не номер сессии исследования.
- `11-evaluation-qa/thresholds.yaml`:93 — «SC 2.3.1 (A)» — уровень WCAG; :107 — «у H.264/AV1» — кодек.
- `06-art-direction-consistency/visual-dna.schema.json`:1235 — `handoff.visual_dna` — имя поля арт-дирекции creative.

**Витрина**:
- `05-prompting/asset-plan.schema.json`:214 — ссылка на `../../blender/15-showcase/VERDICT.md §3`; файл существует,
  судьба ссылки — за решением о витрине.

## Ключи и значения, которые читает код

| место | что не так | читатель | предложение |
|---|---|---|---|
| `stand/tasks.yaml`:151 — ключ `phase5` | имя фазы исследования | `stand_run.py`: `cfg["phase5"]` (строка 118), поле задания `recompile_before_phase5` (162) | переименовать одним шагом с кодом (`recipes`) |
| `stand/tasks.yaml`:10 — `catalog_snapshot: 99-raw/cache/polza/2026-09-23` | путь сырья | `stand_run.py`:165 → `meta.catalog` задания | имя папки снимка `"2026-09-23"` (в кавычках: без них YAML читает дату), как `catalog_snapshots` матрицы |
| `stand/tasks.yaml`:11 — `compiler: "… (прототип D, 2026-09-23)"` | буква исполнителя и дата | `stand_run.py`:162 → `meta.compiler` | `"../../scripts/ai-media/prompt_compile.py"` |
| `stand/tasks.yaml`:61, 66, 68 — `source`, `target` задач S12, S14, S15; :186–241 — `images`, `mask` рецептов (11 строк) | читает `99-raw`: `99-raw/phase5/inputs/E/{banner_en,scene,scene_mask_wall,scene_mask_cup_dilated,product_ref,stub_16x9}.png` — файлов в репозитории нет | `stand_run.py`:176, 451–456 (`_img` от `kb/ai-media`), `meta.ref`; `images`, `mask` — `polza.py` от папки файла заданий | место входов стенда — вопрос 1 отчёта К7 |
| `stand/tasks.yaml`:80, 81 — `source` задач S23, S24 | в ключе пути входа лежит id предложения исследования («W2-11 [V:…]», «C1-11») | `stand_run.py`:176 кладёт `source` в задание как путь картинки | перенести в `note` или снять |
| `stand/tasks.yaml`:71–74 — `owner: H` задач S17–S20 | буква исполнителя | `stand_run.py`:998 (задача с `owner` не идёт в мини-стенд) | значение без буквы или булев признак |
| `stand/tasks.yaml` — `overlaps: [W3-5, C1-12, …]` (17 мест) | id предложений исследования | `stand_run.py`:164, 198 → `meta.overlaps` | снять поле вместе с чтением |
| `stand/tasks.yaml`:250, 251 — `price_source`, `docs` блока `external` | путь сырья в тексте источника | `stand_run.py`:196 → поля задания | `"routerai.ru/api/v1/models, 23.09.2026"`; `"routerai.ru/docs/guides/overview/multimodal/image-generation"` |
| `dialects.yaml`:531, 549 — `channels.*.docs` | путь сырья | `prompt_compile.py`:2191 → поле `docs` задания канала | `"routerai.ru/docs/guides/overview/multimodal/image-generation"`; `"gen-api.ru/model/flux-2/api; gen-api.ru/docs/v1/generations/getting-the-result"` |
| `dialects.yaml`:533, 550 — `channels.*.price_source` | путь сырья | `prompt_compile.py`:2190 → `price_source` задания | `"ai-media 02/03: таблица цен 23.09.2026 (RouterAI ×1,30 к ЦБ)"`; `"прайс Gen-API 23.09.2026"` |
| `dialects.yaml`:540, 541 — `price_unit: "… (P/05)"` | id опыта | `prompt_compile.py`:2190 дописывает к `price_source` задания | `(ai-media 02/03)` |
| `examples/dna-warm-consumer.json`:178 — `grade.lut.file`; :281, 289, 297 — `references[].src` | читает `99-raw`: `../../99-raw/experiments/F/05-color/brand_warm_consumer.cube`, `../../99-raw/phase5/inputs/F/style_autumn_{1,2,3}.jpg` — файлов нет | `vlm_to_dna.py`:304, 306 (сверка существования), 865 (`to-spec`) | файлы в папку примера или вымышленные имена без `99-raw` |
| `stand/briefs/S03-product-scene.spec.json`:91 — `references[0].src` | читает `99-raw`: `99-raw/phase5/inputs/E/product_ref.png` | `prompt_compile.py` (`_abs_src`), `stand_run.py` | вместе с входами стенда |

Тексты-источники `docs`, `price_source`, `price_unit`, `compiler`, `catalog_snapshot` код не разбирает — передаёт
строкой в задание; самопроверки и тесты их значения не сверяют (поиск по `scripts/ai-media/tests/`), поэтому замена
безопасна и без правки кода. Не тронуты: всё, что читает код, правит зона кода вместе со `stand_run.py` и
`prompt_compile.py` — таблица выше для неё.

Изменённые значения, которые код читает, но не разбирает: `routing.yaml` — текст `tool` вариантов (буква и id опыта
в скобках; `../blender-research` → `../blender`) и `name` маршрута `IMG-LAYERS` («разложение на слои RGBA (предложение
кода)»): `routing_check.py` требует только наличие полей и показывает первые 60 знаков `tool` в таблице отчёта — отчёт
до и после отличается тремя ячейками (`IMG-ICON3D`, `IMG-TEXT-LATIN`, `IMG-OUTPAINT`). `dialects.yaml` —
`catalog_snapshot` (компилятор поле не читает, берёт последний снимок), `families.bria-fibo.source`,
`channels.routerai.catalog` (не читаются).

## Сверх маркеров kbscan

Убрано то же по форме, но не пойманное счётчиком: «разбор V» (9), «(L, 25.09)», «(J make_og)» (2), «E-helper…»
(`thresholds.yaml` — 4, рубрики — 12), «K:» в начале `source` порогов (7), id предложений W6-4, A-3, C1-12, W2-12,
W3-13, F-plan, «PLAN «что красиво»», «ворота L», «OCR K», элемент `sources` «W5-4» рубрики `icon3d` (снят: кроме id
в нём ничего нет), «D2b:» в двух описаниях схемы `asset-spec`.

Осталось и не считается счётчиком: в рубриках `decision.choice` «только если K-01 показал ≥ 0,8 согласия», `vlm.role`
«после калибровки K-01/K-02», `decision.video` «(K-03 проверит)» — id тестов калибровки судьи (форма 8); `thresholds.yaml`
— «F-05» (2 порога палитры), «D2-03»; `thresholds.yaml`:29 — адрес `08-image-post-processing/02-upscale-edit-outpaint.md`
ведёт в несуществующий файл (статья называется `02-upscale-outpaint-edit.md`) — не след, правка адреса за оркестратором.

В `note` основного варианта `VEC-ICON-FILLED` (`routing.yaml`:804) перед нормой нарезки стоит итог теста CM-01 «сетку 4×2
не держит (ряды 2 + 4 + 2)»: лист, не сошедшийся с заданием, `split_recraft.py` не режет (код 1) — связку факта и нормы
сверить зоне кода или текстов.

## Производные

Производных файлов в списке зоны нет.

## Для фикстур

`fixture_gen.py build --all --check` — совпадает; расхождений от правок зоны нет.

## Для текстов

- `kb/ai-media/13-routing-matrix/02-existing-evidence.md §2.1` — id строк J1–J26 сохранить: на них ссылаются записи
  `evidence` маршрутов `routing.yaml`.
- `kb/ai-media/05-prompting/06-ab-protocol.md`:47 (п. 18) и `02-structured-json-prompting.md`:291, 363 — «с датой,
  ссылкой на прогон»: поле `run` из `ab_results` снято, запись несёт дату, плечи, Δ, ДИ и решение.
- Статьи `13-routing-matrix/` (`03-routing-matrix.md`, `04-update-procedure.md`, `README.md`) — где сказано, что метка
  живого прогона несёт путь к листу или журналу: в матрице метка — `[проверено: условия]`, пути нет.
- `kb/ai-media/11-evaluation-qa/02-vlm-critic-and-rubrics.md` — формат вопросов чек-листа (атомарные, позитивные, с
  `depends`) должен остаться в статье: поле `checklist_note` рубрик теперь ведёт на `ai-media 11/02`, а не на файл сырья.
- Адреса статей, поставленные вместо id опытов (форма 6), — сверить при уборке текстов: если статья-норма переедет,
  адрес в данных меняется вместе с ней.
- `kb/ai-media/07-vector-svg-icons/03-icon-sets-and-patterns.md`:16 — «нарезка по рамкам путей» против новой нормы
  поля `post` (ячейки сетки из задания).

## Файлы к снятию

Нет.

## Проверки

- Разбор: 40 файлов из 40 читаются (JSON, YAML); три схемы проходят метасхему Draft 2020-12.
- `routing_check.py --selftest` — все проверки пройдены; `routing_check.py` по матрице — код 0: маршрутов 33, вариантов
  137, ошибок 0, предупреждений 12 (столько же у матрицы коммита начала; таблица отчёта отличается тремя ячейками `tool`).
- `stand_run.py selftest` — OK; `stand_run.py --jobs-dir <временная папка> build --only E-08,E-15` — задания собраны
  (9 и 8).
- `prompt_compile.py validate` — 5 брифов стенда OK; тесты `scripts/ai-media/tests/`: `test_prompt_compile.py`
  140/140, `test_prompt_compile_x2.py` 15/15, `test_asset_audit.py` 128/128.
- `asset_audit.py thresholds --check` — код 0; `vlm_to_dna.py selftest` 48/48, `vlm_to_dna.py validate` примера — код 0.
- Читатели схем из соседних баз: `creative/ad_check.py --selftest` OK, `site/plan_to_assets.py --selftest` OK.
- `scripts/tests/smoke.py --only scripts/ai-media` — PASS 63, FAIL 0, XFAIL 0, XPASS 3; XPASS — `provenance_check.py`
  selftest и `svg_sheet.py` (справка, selftest): файлы зоны они не читают.
- `scripts/maint/sync_check.py` — генераторы OK 17, FAIL 0, находок 0; `fixture_gen.py build --all --check` — совпадает.
- `scripts/maint/accept.py --base 1e0cd2a --masks-file …/Д-ai-media-1.masks` — под масками 39 файлов: разбор OK
  (24 файла данных), ссылки, код, следы — OK; строка «маски» — FAIL: 340 изменённых файлов вне масок (другие зоны и
  оркестратор в том же дереве) и 1 маска без изменений (`asset-plan.schema.json`).
- Проверки пройдены после каждого пакета; числа — после последнего.

## Вопросы

1. «Отменено заказчиком 25.09» (19 мест матрицы) и «вердикт заказчика 25.09 13:40: «…»» (`routing.yaml`:72) — тот же
   след, что «решение заказчика», или условие доказательства? Не тронуты.

