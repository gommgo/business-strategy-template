# Спецификация ассета и диалекты: от брифа к промту

Волна 1 · агент D · 2026-09-23 · источников ≈ 30 (гайды вендоров из `01`, соседние базы, каталог polza) · опытов 3
(`99-raw/experiments/D/01…03`: каталог, схема, компилятор) · снимок каталога polza 2026-09-23 · машиночитаемо:
`asset-spec.schema.json` (v0.1), `dialects.yaml` (v0.1), прототип `../../scripts/ai-media/prompt_compile.py`

## Выжимка для агента

1. **Сначала спецификация, потом промт**: бриф → спецификация по `asset-spec.schema.json` → компилятор по
   `dialects.yaml` → промт и параметры. Ручной промт — только для быстрой разведки. → §1 `[мнение]`
2. **Дефект чинится в спецификации, а не в промте**: паспорт генерации хранит спецификацию, диалект и промт. → §1,
   §12 `[мнение]`
3. **Описательные поля — по-английски**, служебные — как удобно; русский бриф переводится при заполнении,
   культурный контекст — полем `subject.culture`. → §2, §7 `[исследование]`
4. **`subject.summary` — конкретный сюжет из предметной области** (≤ 240 символов), а не «futuristic technology»;
   элементы — объект + признаки + связь + позиция, счёт — полем `count`, не больше 8. → §2 `[документация]`
5. **Зона под текст — прямоугольник в долях кадра + поверхность + тон + назначение**; фокусная точка — вне зоны,
   субъект — на противоположной стороне. → §3 `[проверено: 99-raw/experiments/D/02-schema-validate]`
6. **Безопасные зоны кадрирования — прямоугольник на каждое соотношение страницы**, фокусная точка внутри каждого;
   генерируй в основном широком соотношении и кадрируй. → §3 `[проверено: D/02]` `[не проверено]` генерацией
7. **Камера — носитель, объектив, диафрагма, глубина резкости**; для видео движение камеры — только в
   `motion.camera`. → §4 `[документация]`
8. **Свет — источник, направление, качество, взаимодействие с поверхностями**; не «warm» как грейд. → §4
   `[документация]` `[мнение вендора]`
9. **Палитра — 3–5 цветов; у каждого роль, hex, название, доля площади и объект**; сумма долей ≤ 1. → §5
   `[документация]` `[проверено: D/02]`
10. **hex уходит в промт только FLUX.2 (и Ideogram 4 в JSON)**; остальным — название цвета с ролью и местом; цвет со
    `strict: true` доводится постобработкой или HTML. → §5 `[документация]`
11. **Стиль — видимые признаки** (`style.anchors`, ≤ 4), серия — дословный `style.series_block`, который компилятор
    ставит первым. → §6 `[документация]` `[проверено: D/03]`
12. **Запреты двух видов**: `service` (текст, водяной знак, логотип, субтитры, музыка) и `object`/`style`/`artifact` с
    позитивной заменой `replace_with`. → §6 `[документация]`
13. **Текст: `none` / `html_overlay` (по умолчанию) / `in_image`** — строка дословно, язык, письменность, позиция,
    типографика; `in_image` + кириллица → проверка OCR и запасной путь. → §7 `[документация]` `[исследование]`
14. **Выход: основное соотношение — из поддерживаемых моделью** (компилятор сверяет с каталогом); прозрачность — только
    у моделей с параметром (`qwen/image-2.1`). → §8 `[проверено: D/02]`
15. **Видео: длительность — из значений модели в каталоге**, одна камера (`move` + `amplitude` + `speed`), одно действие,
    движение среды, петля `first_last_same`, звук `false`. → §8 `[документация]` `[проверено: D/02]`
16. **Image-to-video: при заданном `start_frame` компилятор отдаёт только движение** — сцену задаёт кадр. → §8, §10
    `[документация]` `[проверено: 99-raw/experiments/D/03-compile-prototype]`
17. **Диалект — по `dialects.yaml`**: формат, порядок блоков, форма отрицаний, текст, палитра, лимит, параметры. →
    §9 `[документация]`
18. **Порядок блоков — по семейству**: FLUX.2 — стиль сразу после субъекта; GPT Image — сначала сцена; серия — всегда
    первой. → §10 `[документация]`
19. **Длину проверяй по каталогу и не обрезай**: сократи спецификацию или смени модель (Z-Image — 1 000, Wan 2.5 —
    800 символов). → §10, §12 `[проверено: D/03]`
20. **Параметры запроса — только те, что есть у модели в каталоге**: звук `"false"`, `fixed_lens` при неподвижной
    камере (Seedance 1.5 Pro), усилители `false`, `negative_prompt` — только `wan/2.5`. → §10 `[проверено: D/03]`
21. **Противоречия ловятся до генерации**: static + tracking, петля + склейки, фокус в зоне под текст, субъект и зона
    на одной стороне, неподдерживаемые длительность и соотношение. → §12 `[проверено: D/02]`

## 1. Зачем спецификация и где она в конвейере

Конвейер базы (`PLAN.md`): план ассетов страницы → **спецификация ассета** → маршрутизация (модель, параметры, запасная
модель) → **компилятор промта** → генерация (`polza.py`) → отбор и проверка → постобработка → доставка. Спецификация —
единственный источник правды об ассете, промт — производная.

Почему не писать промт сразу:

- **Модели меняются ежемесячно, диалекты разные** (`01-vendor-prompt-guides.md` §13): одна спецификация даёт промт для
  Nano Banana, FLUX.2, Qwen, Seedance без переписывания брифа.
- **Проверке нужны поля**: ΔE палитры, пустота зоны под текст, OCR строки, шов петли меряются по полям спецификации
  (агент K), а не по тексту промта.
- **Прецеденты**: BFL для агентов требует бриф до промта — «Resolve the decisions that change routing, payload, or
  production method before a brief becomes a prompt» и шаблон `brief.md` с полями Outcome / Shot / Camera and Look /
  Text strategy / First iteration variable [S1]; Bria FIBO — «Users continue to write natural language, which is
  translated into a structured intermediate dialect» [S2]; в ui-research — бриф с палитрой по ролям и частоте [S3].
- **Что спецификация не делает**: не выбирает модель (это `routing.yaml`, агенты E и N) и не хранит платёжные и
  служебные параметры провайдера.

## 2. Поля спецификации

Схема — `asset-spec.schema.json` (JSON Schema Draft 2020-12, v0.1, `x-checked-at: 2026-09-23`).

| Поле | Зачем | В промт? | Проверки компилятора | Правило-источник |
|---|---|---|---|---|
| `id`, `spec_version`, `checked_at`, `brief_language` | учёт и версии | нет | схема | — |
| `task` | код задачи из таксономии `_common.md` | нет | enum из 32 кодов | — |
| `role` (`page_type`, `section`, `slot`, `purpose`, `priority`, `series_id`) | место на странице, серия | нет | — | план ассетов (агент A) |
| `subject.summary` | сюжет одной фразой | да, первым | ≤ 240 символов; слова без видимого содержания — предупреждение | Google: «Describe the scene» [S4]; Ideogram — запрет «stunning» [S5] |
| `subject.elements[]` | объекты: что, сколько, признаки, связь, позиция, действие | да | ≤ 8 | Seedream — перечень по местам [S6]; GenEval — счёт и позиция слабы [S7] |
| `subject.environment` | место и контекст | да | — | формулы Google, BFL [S4][S8] |
| `subject.culture` | культурный контекст словами | да | — | LingT2I: явная метка сильнее языка промта [S9] |
| `composition` (`shot`, `angle`, `subject_region`, `focal_point`, `depth_layers`, `layout_note`) | кадр | да | фокус вне зоны текста | словарь Vertex [S10] |
| `composition.text_zone` | зона под HTML-текст | да | прямоугольник; не на стороне субъекта | шаблон Google «negative space» [S4] |
| `composition.safe_zones[]` | кадрирование под соотношения | нет | фокус внутри каждой | граф ассетов №1 в `PLAN.md` |
| `camera` | носитель, объектив, диафрагма | да | — | OpenAI: «cues for appearance» [S11] |
| `light` | источник, направление, качество, взаимодействие | да | — | BFL: свет — главный рычаг [S8] |
| `palette[]` | роли, hex, название, доля, объект, `strict` | да (форма по семейству) | сумма долей ≤ 1; > 5 цветов — предупреждение | BFL hex [S8]; «Frequency» ui-research [S3] |
| `materials` | фактуры | да | ≤ 6 | Google «materiality» [S4] |
| `style` (`medium`, `anchors`, `grain`, `finish`, `line`, `series_block`) | стиль видимыми признаками | да | слова без содержания — предупреждение | BFL «Style must be visible» [S1] |
| `references[]` | референсы с ролью | как «Image N: роль» (D2) | число ≤ лимита модели | OpenAI, BFL, Google [S11][S8][S4] |
| `mood` | настроение, ≤ 3 слов | да, в конце | — | — |
| `exclusions[]` | запреты: `service` / `object` / `style` / `artifact` + `replace_with` | да, по форме семейства | без замены у «позитивных» семейств — выпадает с предупреждением | §12.1 файла 01 |
| `text` (`none` / `html_overlay` / `in_image`) | стратегия текста | только `in_image` | письменность против модели; кириллица → OCR | BFL «Text strategy» [S1] |
| `output` (`primary_ratio`, `aspect_ratios`, `resolution`, `format`, `alpha`, `max_kb`) | выход | параметры, не текст | соотношение, разрешение, альфа по каталогу | каталог polza [S12] |
| `motion` (`kind`, `duration_s`, `camera`, `subject_motion`, `environment_motion`, `loop`, `start_frame`, `end_frame`, `cuts`, `audio`, `timeline`) | видео | да (i2v — только это) | длительность по каталогу; противоречия | Vertex, Wan, Runway, BFL [S10][S13][S14][S1] |
| `variants` (`count`, `vary`, `first_iteration_variable`) | серия проб | нет | — | BFL prompt-doctor [S1] |

## 3. Композиция: кадр, фокусная точка, зона под текст, безопасные зоны

- **Координаты** — в долях кадра основного соотношения: `x` слева направо, `y` сверху вниз; прямоугольник `[x0, y0,
  x1, y1]`.
- **`text_zone`**: `side` (left / right / top / bottom / center / углы), `rect`, `surface` («evenly lit warm-grey
  plaster wall», «clear pale sky»), `tone` («even, low contrast»), `purpose` (headline / body / cta / logo / caption),
  `text_color_on_top` — цвет HTML-текста для проверки контраста по худшему пикселю зоны (агент K).
- **Как компилятор говорит о зоне** (все семейства): «The left 40 percent of the frame is an empty, uncluttered
  warm-grey plaster wall, evenly lit and low in contrast, creating clean negative space for a headline.» — сторона и
  доля кадра (OpenAI: «subject centered with negative space on left» [S11]), пустая поверхность и назначение (Google:
  «a vast, empty [color] canvas, creating significant negative space for text» [S4]), ровный тон (читаемость).
  Для семейств с позитивными отрицаниями — «empty, uncluttered», без «no objects» `[не проверено]`.
- **Субъект — на противоположной стороне** (`subject_region`), фокусная точка — вне зоны; иначе ошибка компилятора
  `[проверено: D/02]`.
- **Безопасные зоны кадрирования** (`safe_zones`): для каждого соотношения страницы — прямоугольник, который должен
  остаться после кадрирования; фокус обязан лежать внутри. Пример E1: мастер 16:9, для 4:5 — `[0.5, 0.1, 0.95, 0.95]`,
  для 9:16 — `[0.55, 0.15, 0.9, 0.95]`. Если в безопасную зону не помещается субъект с воздухом — не кадрировать, а
  аутпейнтить (агент H) `[мнение]`.
- **Ideogram 4** принимает зоны числами: `bbox` 0–1000 в порядке `[y_min, x_min, y_max, x_max]` [S5]; у остальных
  моделей — только словами.

## 4. Камера и свет

| Поле | Как компилируется | Пример |
|---|---|---|
| `composition.shot`, `angle` | крупность и ракурс словами Vertex | `medium-wide`, `eye-level` → «Medium-wide shot, at eye level» |
| `camera.capture` | носитель | «Shot as a 35mm film photograph» (OpenAI: «Shot like a 35mm film photograph» [S11]) |
| `camera.lens_mm`, `aperture`, `depth_of_field` | объектив | «35mm lens, f/4, medium depth of field» |
| `light.quality` + `source` | качество и источник | «Soft window daylight» |
| `light.direction` | направление | «light from the right»; `top` → «light from above» |
| `light.interaction` | что свет делает с поверхностями | «long soft shadows across the wooden floor» |

Словарь — `01-vendor-prompt-guides.md` §12.8. Температуру света задавать источником («candle flame»), а не словом «warm»
[S5] `[мнение вендора]`.

## 5. Палитра: роли, hex, доли площади

- **Роли**: `background`, `dominant`, `secondary`, `accent`, `text`, `shadow`, `highlight`; **доля** `share` — часть
  площади кадра (0–1); **объект** `applies_to` — к чему привязан цвет; `strict: true` — бренд-цвет, обязанный
  совпасть.
- **Соответствие «Frequency» из ui-research** [S3]: Dominant ↔ `share` ≥ 0.45; Sparse ↔ `accent` с малой долей;
  Internal ↔ цвет внутри объекта (`applies_to`).
- **Как компилируется доля** (прототип): `share` ≥ 0.45 → «dominates, filling most of the frame»; 0.2–0.45 → «covers a
  large secondary area»; < 0.2 → «is used only on the …». Проценты цифрами в промте — `[не проверено]` (тест 7 отчёта).
- **Форма цвета по семействам** (`dialects.yaml` → `palette`):

| Семейство | Форма | Статус |
|---|---|---|
| FLUX.2 | «color #C9A227 (mustard) is used only on the armchair» — hex + название + объект | `[документация]` BFL [S8] |
| Ideogram 4 (вне polza) | `color_palette` ≤ 16 hex в верхнем регистре; у элемента ≤ 5 | `[документация]` [S5] |
| Recraft V4 (вне polza) | параметр `controls.colors [{rgb, weight}]`, сумма весов ≤ 1 = доли | `[документация]` [S15] |
| Nano Banana, GPT Image, Seedream, Qwen, Z-Image, видео | название цвета + роль + объект | `[документация]` (hex не документирован) |

- **Проверка**: ΔE OKLab доминирующих цветов к палитре и ошибка доли (`../../scripts/lib/color.py`, `dE_oklab`); порог —
  агент K (`02-structured-json-prompting.md` §9.4).

## 6. Материалы, стиль-якоря, серия, настроение, запреты

- **`materials`** — фактуры, которые должны читаться («velvet, oak, linen, plaster»): материальность — отдельная ось
  у Google [S4].
- **`style.anchors`** — видимые признаки, не оценки: «editorial interior photography», «flat vector shapes», «named
  capture format, grain structure, practical light» (BFL: «Style must be visible» [S1]). Слова «stunning, vibrant,
  luminous, cinematic, masterpiece, 8k» — предупреждение компилятора (список Ideogram [S5]).
- **`style.series_block`** — постоянный блок серии, дословно одинаковый во всех спецификациях с одним
  `role.series_id`; компилятор ставит его первым во всех диалектах `[проверено: D/03]`. Эталон серии — в `references`
  с ролью `style` и пометкой «keep line weight, palette and shapes».
- **`mood`** — до 3 слов в конце промта; настроение без визуальных признаков модели выполняют плохо (OpenAI: задавать
  масштаб, атмосферу, цвет, а не только слова настроения [S11]).
- **`exclusions`**: `service` — текст, водяной знак, логотип, субтитры, музыка, реплики: у класса A и у видео-семейств —
  короткие предложения («No watermark.»), у FLUX.2 — позитивные замены из `dialects.yaml` («pristine image», «clean
  unmarked surfaces»); `object` / `style` / `artifact` — только через `replace_with` («an empty room with nobody
  present», «flat solid fills»); в поле `negative_prompt` (`wan/2.5`) — существительные через запятую.

## 7. Текст: нет, поверх HTML, в картинке

| `text.mode` | Когда | Что делает компилятор |
|---|---|---|
| `none` | иллюстрации, фоны без текста рядом | служебный запрет текста (форма по семейству) |
| `html_overlay` (по умолчанию) | заголовки, кнопки, любые важные слова, кириллица | запрет текста + зона под текст; строки из `copy` в промт **не идут** |
| `in_image` | декоративная надпись, вывеска в сцене, баннер как картинка | строки дословно в кавычках, язык и письменность, место, типографика, цвет, размер, «No other text» (у Qwen — «No other text appears in the image.») |

- Соответствие стратегии BFL [S1]: absent → `none`; deterministic post → `html_overlay`; physical in-scene / generated
  → `in_image` (`surface` — «painted on the shop window»).
- **Кириллица** (`script: Cyrillic`): компилятор предупреждает про OCR, у Z-Image — ошибка (надписи только EN/ZH);
  `fallback: html_overlay` — что делать, если OCR не совпал. Данные о провалах — `01-vendor-prompt-guides.md` §12.7.
- **1–4 слова на строку, не больше 3 строк** (`maxLength` 40 символов) — BFL: «Keep text short (1-4 words work
  best)» [S8].

## 8. Выход, движение, варианты

- **`output.primary_ratio`** — соотношение генерации (компилятор сверяет с `aspect_ratio` модели в каталоге);
  `aspect_ratios` — все соотношения страницы (кадрирование по `safe_zones` или аутпейнт); `resolution` — ступень
  модели (1K / 2K / 4K для картинок, 480p–1080p для видео); `alpha: true` — только если у модели есть параметр
  `background` (в polza — `qwen/image-2.1`) `[проверено: D/02]`.
- **`motion`** (только видео):
  - `kind`: loop / cinemagraph / camera-move / i2v-product / abstract / character;
  - `duration_s` — из значений модели (Seedance 1.5 Pro — 4/8/12, Omni — 4/6/8/10, MiniMax H3 Max — 5–15, Wan 2.5 —
    5/10) `[проверено: D/02]`;
  - `camera.move` + `amplitude` + `speed` — одно движение (MiniMax: тип + амплитуда + скорость [S16]);
  - `subject_motion` — одно действие общими словами; `environment_motion` — туман, пар, листва, свет (Vertex: три
    типа движения [S10]);
  - `loop: first_last_same` + одинаковые `start_frame` и `end_frame`; `cuts: none`;
  - `audio: false` → `generate_audio: "false"` / `sound: "false"` там, где параметр есть;
  - `timeline` — только для семейств с таймкодами (у Seedance 2.0 — опускается с предупреждением).
- **i2v**: если задан `start_frame`, в промт идут только движение, служебные запреты и контракт непрерывности — сцену,
  свет и внешность задаёт кадр (Vertex: «Prompt for motion only» [S10]; Wan: «Motion + Camera movement» [S13]; BFL:
  «redescribing visible pixels invites re-imagination» [S1]; Runway: «almost exclusively on motion» [S14]).
- **`variants`**: число проб, что варьировать (`seed` и т. п.) и `first_iteration_variable` — что менять первым при
  промахе (BFL prompt-doctor [S1]).

## 9. `dialects.yaml`: что описано по семействам

Файл — `05-prompting/dialects.yaml` (v0.1, `checked_at: 2026-09-23`, снимок каталога указан в заголовке). 20 семейств:
16 в polza (40 моделей) и 4 вне polza (Ideogram 4, Recraft V4, Midjourney, Runway). Лимиты промта и число референсов
совпадают с каталогом — проверяет тест `[проверено: 99-raw/experiments/D/03-compile-prototype]`.

| Ключ | Что значит | Пример |
|---|---|---|
| `class` | класс входа по `01` §1.1: A (LLM-фронт), B (языковой энкодер), C (T5/CLIP), D (обучена на структуре) | `nano-banana: A`, `minimax-h3: D` |
| `models.{id}` | лимит промта (`max_prompt_chars`), референсы (`max_refs`), цена, `seed`, маска, звук по умолчанию | `wan/2.5: {max_prompt_chars: 800, negative_field: {…}}` |
| `safe_max_prompt_chars` | меньший из лимитов документации и каталога | Veo — 2 000; Seedance 2 — 1 536 |
| `format`, `alt_formats` | форма по умолчанию и допустимые для A/B | `flux2: prose`, `[sections, json]` |
| `order` | порядок смысловых блоков | FLUX.2: subject → action → style → environment … |
| `labels` | метки разделов (для `sections`) | GPT Image: Scene / Subject / Details / Constraints |
| `negative` | поле негатива и форма запретов (`service`, `object`: `sentence` или `positive`) | FLUX.2: `positive` + таблица замен |
| `language` | язык описания, допустим ли русский | Nano Banana: `russian_description_ok: true` |
| `references` | синтаксис ссылок на входы | Seedance 2: `<Image_{n}>`; Omni: `<IMAGE_REF_{n}>` |
| `text` | кавычки, указание языка, закрывающая фраза, допустимые письменности | Qwen: «No other text appears in the image.»; Z-Image: только Latin |
| `palette` | hex или названия, форма | FLUX.2: `color {hex} ({name})` |
| `text_zone`, `edit` | шаблоны вендоров (для D2) | Google «negative space», OpenAI «change only» |
| `timestamps`, `camera`, `i2v`, `audio` | таймкоды, фраза неподвижной камеры, «только движение», параметр звука | Wan: `fixed camera`, `Shot {k} [{t0}–{t1} s]` |
| `enhancer` | встроенный переписчик у вендора и в polza | Qwen: `enhance_prompt` (`false`) |
| `status` | `documented` / `untested` | Z-Image, Grok, H3 Max — `untested` |
| `ab_results` | результаты A/B фазы 5 с датой и ссылкой | пусто до фазы 5 |

## 10. Правила отображения «поле → фраза или ключ»

Главные колонки — формы, которые компилятор реально собирает `[проверено: D/03]`; формулировки — `[не проверено]`
генерацией.

| Поле спецификации | Проза / разделы (FLUX.2, Nano Banana, GPT Image, Seedream, Qwen, Z-Image) | JSON (базовая схема BFL) | Ideogram 4 (JSON подписи) | MiniMax H3 (IR) |
|---|---|---|---|---|
| `style.series_block` | первым, дословно; в разделах — «Series style (keep identical): …» | — (в `style`) | `style_description.aesthetics` | в `[Shot 1]` |
| `subject.summary` | первое предложение | `scene` | `high_level_description` (≤ 50 слов) | `[Shot 1] …` |
| `subject.elements[]` | «A … with …, to the left of …, in the right third»; `count` 2–12 — словами | `subjects[{description, count, position, relation, action}]` | `elements[{type: "obj", desc}]` | в описании шота |
| `subject.environment` | «Setting: …» / предложение | `background` | `compositional_deconstruction.background` | в описании |
| `subject.culture` | «Cultural context: …» | — | — | — |
| `composition.*` | «Medium-wide shot, at eye level, main subject in the right third of the frame» | `composition.framing` | (bbox — D2) | «a medium-wide shot frames…» |
| `composition.text_zone` | «The left 40 percent of the frame is an empty, uncluttered {surface}, {tone}, creating clean negative space for a {purpose}.» | `composition.negative_space` | «minimal, sparse, empty negative space on the left» в `background` | — |
| `camera` | «Shot as a 35mm film photograph, 35mm lens, f/4, medium depth of field» | `camera` | `style_description.photo` (D2) | — |
| `light` | «Soft window daylight, light from the right, …» | `lighting` | `style_description.lighting` | в описании |
| `palette[]` | FLUX.2: «color #HEX (name) … on the …»; прочие: «Warm grey dominates… mustard is used only on the armchair» | `color_palette: ["#HEX name (NN percent) on …"]` | `color_palette` (hex) | в описании |
| `materials` | «Materials: …» | `materials` | — | — |
| `style` | «Photograph, editorial interior photography, subtle film grain» (у FLUX.2 — сразу после субъекта) | `style` | `style_description.aesthetics`, `medium` | «Live-action, …» |
| `mood` | «Mood: calm, unhurried.» | `mood` | — | — |
| `exclusions` `service` | класс A и видео: «No watermark. No text.»; FLUX.2 / Z-Image / Grok: замены («pristine image, clean unmarked surfaces») | `constraints` | (поле негатива — вне схемы подписи) | `non_diegetic_music: N/A` |
| `exclusions` `object` + `replace_with` | замена позитивом («An empty room with nobody present») | `constraints` | — | — |
| `text` `in_image` | «The headline reads "…", in Russian (Cyrillic script), set in …, placed …» + «No other text.» | `text[{content, language, position, typography}]` | `elements[{type: "text", text, desc}]`, длинные строки — через `\n` | надписи — в кавычках, без перевода |
| `motion.camera` | «Locked camera. The camera remains still.» / «The camera slowly dollies in with small amplitude at slow speed.»; фраза неподвижности — из семейства | `motion` | — | «The camera holds a static shot.» |
| `motion.subject_motion`, `environment_motion` | предложения движения | `motion` | — | в описании |
| `motion.loop` | «The camera must start and end on the exact same frame to create a perfect loop.»; Omni — объявление `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]` и закрывающая фраза | `motion` | — | строка FL2VA «Picture 1… 0.00-second… Picture 2… S.SS-second» |
| `motion.cuts: none` | «One continuous shot, same set and geometry, no cuts.»; Omni — «In a single continuous shot. No scene cuts.» | `motion` | — | «One continuous shot» |
| `motion.audio: false` | параметр `generate_audio` / `sound` = `"false"`; в тексте — «No background music.» при запрете | — | — | `overall_soundscape: N/A` |
| `output.primary_ratio`, `resolution` | параметры `aspect_ratio`, `image_resolution` / `resolution` из каталога | — | — | параметры |
| `output.alpha` | параметр `background: "transparent"` (только `qwen/image-2.1`) | — | — | — |

**Порядок блоков** — по `order` семейства (прототип: `ordered_keys`): Nano Banana — субъект → место → композиция →
зона → камера → свет → палитра → материалы → стиль → настроение → текст → ограничения; GPT Image — сцена → субъект →
детали (материалы) → композиция → …; FLUX.2 — субъект → стиль → место → композиция → зона → свет → камера → палитра;
Qwen — субъект → место → композиция → зона → свет → материалы → палитра → стиль → текст. Серия — всегда первой.

**Параметры запроса** собираются только из каталога модели (`build_params`): `aspect_ratio` (с проверкой значения),
`image_resolution` / `resolution`, `duration` (с проверкой), `generate_audio` / `sound` = `"false"`, `fixed_lens` при
`move: static`, усилители (`enhance_prompt`, `enable_prompt_expansion`, `isEnhance`) = выключено в типе каталога
(`false` или `"false"`), `negative_prompt` из предметных запретов, `background: "transparent"` при `alpha`.

## 11. Примеры: пять спецификаций в трёх–четырёх диалектах

Собраны прототипом `../../scripts/ai-media/prompt_compile.py` из спецификаций `99-raw/experiments/D/02-schema-validate/specs/`
(полный вывод со всеми моделями — `99-raw/experiments/D/03-compile-prototype/examples.md`). Генерацией не проверялись.

### 11.1 E1 — Hero-фото с зоной под текст (`IMG-HERO-PHOTO`)

Спецификация целиком — `../../scripts/ai-media/tests/fixtures/D02/E1.spec.json`. Ключевые поля:

| Поле | Значение |
|---|---|
| `subject.summary` | a quiet reading nook by a tall window in a small city apartment |
| `composition` | medium-wide, eye-level, субъект right-third |
| `text_zone` | left, rect [0.0, 0.0, 0.4, 1.0], «warm-grey plaster wall», headline |
| `safe_zones` | 4:5 → [0.5, 0.1, 0.95, 0.95]; 9:16 → [0.55, 0.15, 0.9, 0.95] |
| `palette` | background #D9D4CC warm grey 55 % → wall; secondary #A0785A light oak 20 % → floor and side table; accent #C9A227 mustard 15 % → armchair; accent #2F4A3A deep green 5 % → book spines |
| `text` | html_overlay |
| `exclusions` | people (object → «an empty room with nobody present»); watermark (service) |
| `output` | 16:9, 2K, avif |

```text
// google/gemini-3-pro-image-preview · sections · 1453 симв. · polza 2026-09-23 · [не проверено]
Subject: A quiet reading nook by a tall window in a small city apartment. A mustard velvet armchair with slightly worn armrests in the right third. A small round oak side table to the left of the armchair. A white ceramic mug with a thin wisp of steam on the side table. Stack of three hardcover books on the floor beside the armchair.
Setting: Early morning in a small apartment, tall window with a sheer linen curtain on the right.
Composition: Medium-wide shot, at eye level, main subject in the right third of the frame, layers: foreground: armchair and side table; background: window with a sheer curtain.
Negative space: The left 40 percent of the frame is an empty, uncluttered warm-grey plaster wall, evenly lit and low in contrast, creating clean negative space for a headline.
Camera: Shot as a 35mm film photograph, 35mm lens, f/4, medium depth of field.
Lighting: Soft window daylight, light from the right, early morning, long soft shadows across the wooden floor.
Color palette: Warm grey dominates, filling most of the frame on the wall; light oak covers a large secondary area on the floor and side table; mustard is used only on the armchair; deep green is used only on the book spines.
Materials: velvet, oak, linen, plaster, ceramic.
Style: Photograph, editorial interior photography, natural color balance, subtle film grain.
Mood: calm, unhurried.
Requirements: An empty room with nobody present.
Constraints: No watermark. No text.
```

параметры: `{"aspect_ratio": "16:9", "image_resolution": "2K"}`

```text
// black-forest-labs/flux.2-pro · prose · 1421 симв. · polza 2026-09-23 · [не проверено]
A quiet reading nook by a tall window in a small city apartment. A mustard velvet armchair with slightly worn armrests in the right third. A small round oak side table to the left of the armchair. A white ceramic mug with a thin wisp of steam on the side table. Stack of three hardcover books on the floor beside the armchair. Photograph, editorial interior photography, natural color balance, subtle film grain. Early morning in a small apartment, tall window with a sheer linen curtain on the right. Medium-wide shot, at eye level, main subject in the right third of the frame, layers: foreground: armchair and side table; background: window with a sheer curtain. The left 40 percent of the frame is an empty, uncluttered warm-grey plaster wall, evenly lit and low in contrast, creating clean negative space for a headline. Soft window daylight, light from the right, early morning, long soft shadows across the wooden floor. Shot as a 35mm film photograph, 35mm lens, f/4, medium depth of field. Color #D9D4CC (warm grey) dominates, filling most of the frame on the wall; color #A0785A (light oak) covers a large secondary area on the floor and side table; color #C9A227 (mustard) is used only on the armchair; color #2F4A3A (deep green) is used only on the book spines. Materials: velvet, oak, linen, plaster, ceramic. Mood: calm, unhurried. An empty room with nobody present, pristine image, clean unmarked surfaces.
```

параметры: `{"aspect_ratio": "16:9", "image_resolution": "2K"}`

```json
// black-forest-labs/flux.2-pro · json · 1647 симв. · polza 2026-09-23 · [не проверено]
{"scene": "a quiet reading nook by a tall window in a small city apartment", "subjects": [{"description": "mustard velvet armchair, with slightly worn armrests", "position": "right third"}, {"description": "small round oak side table", "relation": "to the left of the armchair"}, {"description": "white ceramic mug with a thin wisp of steam", "relation": "on the side table"}, {"description": "stack of three hardcover books", "relation": "on the floor beside the armchair"}], "background": "early morning in a small apartment, tall window with a sheer linen curtain on the right", "style": "Photograph, editorial interior photography, natural color balance, subtle film grain", "color_palette": ["#D9D4CC warm grey (55 percent) on wall", "#A0785A light oak (20 percent) on floor and side table", "#C9A227 mustard (15 percent) on armchair", "#2F4A3A deep green (5 percent) on book spines"], "lighting": "Soft window daylight, light from the right, early morning, long soft shadows across the wooden floor", "mood": "calm, unhurried", "composition": {"framing": "Medium-wide shot, at eye level, main subject in the right third of the frame, layers: foreground: armchair and side table; background: window with a sheer curtain", "negative_space": "The left 40 percent of the frame is an empty, uncluttered warm-grey plaster wall, evenly lit and low in contrast, creating clean negative space for a headline"}, "camera": "Shot as a 35mm film photograph, 35mm lens, f/4, medium depth of field", "materials": ["velvet", "oak", "linen", "plaster", "ceramic"], "constraints": "An empty room with nobody present, pristine image, clean unmarked surfaces."}
```

параметры: `{"aspect_ratio": "16:9", "image_resolution": "2K"}`

### 11.2 E2 — Иллюстрация серии (шаг онбординга) (`IMG-SERIES`)

Спецификация целиком — `../../scripts/ai-media/tests/fixtures/D02/E2.spec.json`. Ключевые поля:

| Поле | Значение |
|---|---|
| `subject.summary` | a paper plane flying above a neat stack of documents |
| `composition` | medium, субъект center |
| `palette` | background #F6F1E7 cream 70 % → background; dominant #1F3A5F deep navy 20 % → outlines and documents; accent #FF6B5B coral 8 % → paper plane |
| `style.series_block` | Flat vector illustration for a product onboarding series: uniform 2 px deep navy outlines with rounded caps, flat solid fills, generous cream background, coral only on the key object, soft rounded geometric shapes. |
| `text` | none |
| `exclusions` | gradients and shading (style → «flat solid fills») |
| `output` | 4:3, 1K, webp |

```text
// gpt-image-2-5-flare · sections · 1009 симв. · polza 2026-09-23 · [не проверено]
Series style (keep identical): Flat vector illustration for a product onboarding series: uniform 2 px deep navy outlines with rounded caps, flat solid fills, generous cream background, coral only on the key object, soft rounded geometric shapes.
Setting: Plain cream background with two short dotted motion lines behind the plane.
Subject: A paper plane flying above a neat stack of documents. A folded paper plane in coral in the upper center, gliding upward to the right. Three flat documents with simple line details stacked below the plane.
Composition: Medium shot, main subject in the center of the frame.
Color palette: Cream (#F6F1E7) dominates, filling most of the frame on the background; deep navy (#1F3A5F) covers a large secondary area on the outlines and documents; coral (#FF6B5B) is used only on the paper plane.
Style: Flat illustration, flat vector shapes, soft rounded geometry, uniform 2 px deep navy outlines with rounded caps, matte.
Requirements: Flat solid fills.
Constraints: No text.
```

параметры: `{"aspect_ratio": "4:3", "image_resolution": "1K"}`

```text
// bytedance/seedream-4.5 · prose · 868 симв. · polza 2026-09-23 · [не проверено]
Flat vector illustration for a product onboarding series: uniform 2 px deep navy outlines with rounded caps, flat solid fills, generous cream background, coral only on the key object, soft rounded geometric shapes. A paper plane flying above a neat stack of documents. A folded paper plane in coral in the upper center, gliding upward to the right. Three flat documents with simple line details stacked below the plane. Plain cream background with two short dotted motion lines behind the plane. Medium shot, main subject in the center of the frame. Flat illustration, flat vector shapes, soft rounded geometry, uniform 2 px deep navy outlines with rounded caps, matte. Cream dominates, filling most of the frame on the background; deep navy covers a large secondary area on the outlines and documents; coral is used only on the paper plane. Flat solid fills. No text.
```

параметры: `{"aspect_ratio": "4:3"}`

```text
// qwen/image-2.1 · prose · 868 симв. · polza 2026-09-23 · [не проверено]
Flat vector illustration for a product onboarding series: uniform 2 px deep navy outlines with rounded caps, flat solid fills, generous cream background, coral only on the key object, soft rounded geometric shapes. A paper plane flying above a neat stack of documents. A folded paper plane in coral in the upper center, gliding upward to the right. Three flat documents with simple line details stacked below the plane. Plain cream background with two short dotted motion lines behind the plane. Medium shot, main subject in the center of the frame. Cream dominates, filling most of the frame on the background; deep navy covers a large secondary area on the outlines and documents; coral is used only on the paper plane. Flat illustration, flat vector shapes, soft rounded geometry, uniform 2 px deep navy outlines with rounded caps, matte. Flat solid fills. No text.
```

параметры: `{"aspect_ratio": "4:3", "image_resolution": "1K", "enhance_prompt": false}`

### 11.3 E3 — Абстрактный фон под центральный заголовок (`IMG-BG-ABSTRACT`)

Спецификация целиком — `../../scripts/ai-media/tests/fixtures/D02/E3.spec.json`. Ключевые поля:

| Поле | Значение |
|---|---|
| `subject.summary` | large soft overlapping organic shapes like out-of-focus paper cutouts lit from above |
| `composition` | full-bleed-abstract, субъект full-frame |
| `text_zone` | center, rect [0.25, 0.3, 0.75, 0.7], «smooth area of deep teal», headline |
| `palette` | background #0F4C5C deep teal 60 % → background and large shapes; secondary #E3C9A8 sand 30 % → overlapping shapes at the edges; accent #E36F5B coral 10 % → one small shape in the lower right |
| `text` | html_overlay |
| `exclusions` | hard vector edges (artifact → «soft, slightly blurred edges») |
| `output` | 16:9, 2K, avif |

```text
// black-forest-labs/flux.2-pro · prose · 787 симв. · polza 2026-09-23 · [не проверено]
Large soft overlapping organic shapes like out-of-focus paper cutouts lit from above. Abstract gradient, soft paper-cutout shapes, gentle depth, matte, fine film grain. Full-bleed abstract composition, the small coral shape sits in the lower right corner. The central 50 percent of the frame is an empty, uncluttered smooth area of deep teal, even, darker and low in contrast, creating clean negative space for a headline. Soft diffuse top light, light from above. Color #0F4C5C (deep teal) dominates, filling most of the frame on the background and large shapes; color #E3C9A8 (sand) covers a large secondary area on the overlapping shapes at the edges; color #E36F5B (coral) is used only on the one small shape in the lower right. Soft, slightly blurred edges, clean unmarked surfaces.
```

параметры: `{"aspect_ratio": "16:9", "image_resolution": "2K"}`

```text
// tongyi-mai/z-image · prose · 714 симв. · polza 2026-09-23 · [не проверено]
Large soft overlapping organic shapes like out-of-focus paper cutouts lit from above. Full-bleed abstract composition, the small coral shape sits in the lower right corner. The central 50 percent of the frame is an empty, uncluttered smooth area of deep teal, even, darker and low in contrast, creating clean negative space for a headline. Soft diffuse top light, light from above. Deep teal dominates, filling most of the frame on the background and large shapes; sand covers a large secondary area on the overlapping shapes at the edges; coral is used only on the one small shape in the lower right. Abstract gradient, soft paper-cutout shapes, gentle depth, matte, fine film grain. Soft, slightly blurred edges.
```

параметры: `{"aspect_ratio": "16:9"}`; предупреждение: служебный запрет «text» опущен: у семейства только позитивные формулировки

```text
// google/gemini-3.1-flash-lite-image · sections · 820 симв. · polza 2026-09-23 · [не проверено]
Subject: Large soft overlapping organic shapes like out-of-focus paper cutouts lit from above.
Composition: Full-bleed abstract composition, the small coral shape sits in the lower right corner.
Negative space: The central 50 percent of the frame is an empty, uncluttered smooth area of deep teal, even, darker and low in contrast, creating clean negative space for a headline.
Lighting: Soft diffuse top light, light from above.
Color palette: Deep teal dominates, filling most of the frame on the background and large shapes; sand covers a large secondary area on the overlapping shapes at the edges; coral is used only on the one small shape in the lower right.
Style: Abstract gradient, soft paper-cutout shapes, gentle depth, matte, fine film grain.
Requirements: Soft, slightly blurred edges.
Constraints: No text.
```

параметры: `{"aspect_ratio": "16:9"}`

### 11.4 E4 — Петля hero (i2v, первый = последний кадр) (`VID-HERO-LOOP`)

Спецификация целиком — `../../scripts/ai-media/tests/fixtures/D02/E4.spec.json`. Ключевые поля:

| Поле | Значение |
|---|---|
| `subject.summary` | a ceramic cup of tea on a sunlit windowsill |
| `composition` | medium, eye-level, субъект right-third |
| `text_zone` | left, rect [0.0, 0.0, 0.4, 1.0], «warm white wall», headline |
| `palette` | background #EFE9E1 warm white 60 % → wall; secondary #A9B8A0 sage 20 % → curtain; accent #B8742A amber 8 % → tea |
| `text` | html_overlay |
| `motion` | loop, 4 с, камера static, петля first_last_same, звук False |
| `exclusions` | subtitles (service); music (service) |
| `output` | 16:9, 720p, mp4 |

```text
// bytedance/seedance-1.5-pro · prose · 328 симв. · polza 2026-09-23 · [не проверено]
Locked camera. The camera remains still. Thin steam rises slowly from the cup and drifts to the left. The sheer curtain sways gently in a light breeze. One continuous shot, same set and geometry, no cuts. The camera must start and end on the exact same frame to create a perfect loop. No subtitles. No background music. No text.
```

параметры: `{"aspect_ratio": "16:9", "resolution": "720p", "duration": "4", "generate_audio": "false", "fixed_lens": "true"}`

```text
// google/veo3_fast · prose · 314 симв. · polza 2026-09-23 · [не проверено]
The camera remains static. Thin steam rises slowly from the cup and drifts to the left. The sheer curtain sways gently in a light breeze. One continuous shot, same set and geometry, no cuts. The camera must start and end on the exact same frame to create a perfect loop. No subtitles. No background music. No text.
```

параметры: `{"aspect_ratio": "16:9"}`

```text
// gemini-omni-video · prose · 410 симв. · polza 2026-09-23 · [не проверено]
[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]
The camera stays locked. Thin steam rises slowly from the cup and drifts to the left. The sheer curtain sways gently in a light breeze. In a single continuous shot. No scene cuts. The camera must start and end on the exact same frame to create a perfect loop. No subtitles. No background music. No text.
Use this image as the first frame and the last frame.
```

параметры: `{"aspect_ratio": "16:9", "resolution": "720p", "duration": "4"}`

```text
// minimax/hailuo-3-max · ir · 580 симв. · polza 2026-09-23 · ошибка компилятора — см. ниже
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 4.00-second mark of the target video.
integrated_multimodal_description: [Shot 1] The camera holds a static shot. Thin steam rises slowly from the cup and drifts to the left. The sheer curtain sways gently in a light breeze. One continuous shot, same set and geometry, no cuts. The camera must start and end on the exact same frame to create a perfect loop.
overall_soundscape: N/A
non_diegetic_music: N/A
```

параметры: `{"aspect_ratio": "16:9", "resolution": "768p"}`; предупреждение: minimax/hailuo-3-max: resolution 720p нет в ['768p', '480p'], беру 768p; **ошибка**: minimax/hailuo-3-max: длительность 4 с не из ['5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']

### 11.5 E5 — Баннер с кириллицей в картинке (`IMG-TEXT-CYR`)

Спецификация целиком — `../../scripts/ai-media/tests/fixtures/D02/E5.spec.json`. Ключевые поля:

| Поле | Значение |
|---|---|
| `subject.summary` | a flat lay of spring gardening tools and seed packets on a light wooden table |
| `composition` | flat-lay, top-down, субъект right-third |
| `text_zone` | left, rect [0.04, 0.08, 0.5, 0.6], «clear light wood surface», headline |
| `palette` | background #E8DCC8 light birch wood 55 % → tabletop; secondary #8FA382 sage green 20 % → tool handles and leaves; accent #C1653A terracotta 10 % → flower pot; text #1F3A2E dark forest green 5 % → headline |
| `text` | in_image: «Весенняя распродажа» (ru, Cyrillic, in the upper left area) / «до 31 марта» (ru, Cyrillic, directly below the headline) |
| `exclusions` | watermark (service); logo (service) |
| `output` | 16:9, 2K, webp |

```text
// google/gemini-3.1-flash-image-preview · sections · 1362 симв. · polza 2026-09-23 · [не проверено]
Subject: A flat lay of spring gardening tools and seed packets on a light wooden table. Small trowel and pruning shears with sage-green handles in the right half. Plain kraft-paper seed packets in the right half. A terracotta pot with a young seedling in the lower right.
Setting: Light wooden tabletop.
Cultural context: Russian dacha spring gardening.
Composition: Flat lay, from directly above, main subject in the right third of the frame.
Negative space: The left 46 percent of the frame is an empty, uncluttered clear light wood surface, even, creating clean negative space for a headline.
Lighting: Soft overcast daylight, light from above.
Color palette: Light birch wood dominates, filling most of the frame on the tabletop; sage green covers a large secondary area on the tool handles and leaves; terracotta is used only on the flower pot; dark forest green is used only on the headline.
Style: Photograph, clean product flat lay, true-to-life colors.
Text (exact): The headline reads "Весенняя распродажа", in Russian (Cyrillic script), set in bold rounded sans-serif, in color #1F3A2E, very large size, placed in the upper left area. The subhead reads "до 31 марта", in Russian (Cyrillic script), set in regular rounded sans-serif, in color #1F3A2E, medium size, placed directly below the headline. No other text.
Constraints: No watermark. No logos.
```

параметры: `{"aspect_ratio": "16:9", "image_resolution": "2K"}`; предупреждение: кириллица в картинке: обязательна проверка OCR; запасной путь — HTML-слой

```text
// qwen/image-2.1 · prose · 1277 симв. · polza 2026-09-23 · [не проверено]
A flat lay of spring gardening tools and seed packets on a light wooden table. Small trowel and pruning shears with sage-green handles in the right half. Plain kraft-paper seed packets in the right half. A terracotta pot with a young seedling in the lower right. Light wooden tabletop. Cultural context: Russian dacha spring gardening. Flat lay, from directly above, main subject in the right third of the frame. The left 46 percent of the frame is an empty, uncluttered clear light wood surface, even, creating clean negative space for a headline. Soft overcast daylight, light from above. Light birch wood dominates, filling most of the frame on the tabletop; sage green covers a large secondary area on the tool handles and leaves; terracotta is used only on the flower pot; dark forest green is used only on the headline. Photograph, clean product flat lay, true-to-life colors. The headline reads "Весенняя распродажа", in Russian (Cyrillic script), set in bold rounded sans-serif, in color #1F3A2E, very large size, placed in the upper left area. The subhead reads "до 31 марта", in Russian (Cyrillic script), set in regular rounded sans-serif, in color #1F3A2E, medium size, placed directly below the headline. No other text appears in the image. No watermark. No logos.
```

параметры: `{"aspect_ratio": "16:9", "image_resolution": "2K", "enhance_prompt": false}`; предупреждение: кириллица в картинке: обязательна проверка OCR; запасной путь — HTML-слой

```text
// openai/gpt-image-2.5-sunburst · sections · 1489 симв. · polza 2026-09-23 · [не проверено]
Setting: Light wooden tabletop.
Cultural context: Russian dacha spring gardening.
Subject: A flat lay of spring gardening tools and seed packets on a light wooden table. Small trowel and pruning shears with sage-green handles in the right half. Plain kraft-paper seed packets in the right half. A terracotta pot with a young seedling in the lower right.
Composition: Flat lay, from directly above, main subject in the right third of the frame.
Negative space: The left 46 percent of the frame is an empty, uncluttered clear light wood surface, even, creating clean negative space for a headline.
Lighting: Soft overcast daylight, light from above.
Color palette: Light birch wood (#E8DCC8) dominates, filling most of the frame on the tabletop; sage green (#8FA382) covers a large secondary area on the tool handles and leaves; terracotta (#C1653A) is used only on the flower pot; dark forest green (#1F3A2E) is used only on the headline.
Style: Photograph, clean product flat lay, true-to-life colors.
Text (exact): The headline reads "Весенняя распродажа", in Russian (Cyrillic script), set in bold rounded sans-serif, in color #1F3A2E, very large size, placed in the upper left area. The subhead reads "до 31 марта", in Russian (Cyrillic script), set in regular rounded sans-serif, in color #1F3A2E, medium size, placed directly below the headline. Render each text exactly once, clearly and legibly. No extra text, no watermarks, no unrelated logos.
Constraints: No watermark. No logos.
```

параметры: `{"aspect_ratio": "16:9", "image_resolution": "2K"}`; предупреждение: кириллица в картинке: обязательна проверка OCR; запасной путь — HTML-слой

```json
// ideogram/ideogram-4 · ideogram_json · 1070 симв. · вне polza · [не проверено]
{"high_level_description":"A flat lay of spring gardening tools and seed packets on a light wooden table. Small trowel and pruning shears with sage-green handles in the right half. Plain kraft-paper seed packets in the right half. A terracotta pot with a young seedling in the lower right.","style_description":{"aesthetics":"Photograph, clean product flat lay, true-to-life colors","lighting":"Soft overcast daylight, light from above","medium":"photograph","color_palette":["#E8DCC8","#8FA382","#C1653A","#1F3A2E"]},"compositional_deconstruction":{"background":"light wooden tabletop; minimal, sparse, empty negative space on the left","elements":[{"type":"obj","desc":"small trowel and pruning shears with sage-green handles"},{"type":"obj","desc":"plain kraft-paper seed packets"},{"type":"obj","desc":"terracotta pot with a young seedling"},{"type":"text","text":"Весенняя\nраспродажа","desc":"bold rounded sans-serif headline, in the upper left area"},{"type":"text","text":"до 31 марта","desc":"regular rounded sans-serif subhead, directly below the headline"}]}}
```

параметры: `{"aspect_ratio": "16:9"}`; предупреждение: кириллица в картинке: обязательна проверка OCR; запасной путь — HTML-слой; предупреждение: ideogram/ideogram-4: модель вне polza — параметры запроса не собираются

## 12. Компилятор: прототип, проверки, заметки для D2

### 12.1 Прототип

```bash
# Python 3.13.5 + venv-D (jsonschema 4.26.0, PyYAML 6.0.3) — [проверено: 99-raw/experiments/D/03-compile-prototype]
99-raw/tools/venv-D/bin/python ../../scripts/ai-media/prompt_compile.py validate SPEC.json --model qwen/image-2.1
99-raw/tools/venv-D/bin/python ../../scripts/ai-media/prompt_compile.py compile SPEC.json --model black-forest-labs/flux.2-pro --dialect json
99-raw/tools/venv-D/bin/python ../../scripts/ai-media/prompt_compile.py jobs B1.spec.json B2.spec.json --models qwen/image-2.1 \
    --dialects prose,sections,json --repeats 2 --seeds 101,202 --tag D --out jobs.jsonl
python3 ../../scripts/ai-media/polza.py estimate jobs.jsonl        # сверка заданий клиентом агента B, без сети
```

Устройство: спецификация → смысловые блоки по-английски (`blocks`) → сборка в форме семейства (`to_prose`,
`to_sections`, `to_json`, `to_ir`, `to_ideogram_json`) в порядке `order` → режим i2v → теги ролей Omni → параметры из
каталога (`build_params`) → проверка длины. Результаты опытов: 19 компиляций примеров (18 без ошибок; E4 для H3 Max
отклонён — 4 с вне 5–15), 60 компиляций A/B, 30/30 офлайн-тестов, `jobs.jsonl` — 90 заданий на 327 ₽ по
`polza.py estimate` (0 ошибок) `[проверено: D/03]`.

### 12.2 Проверки до генерации

| Проверка | Источник правила | Где |
|---|---|---|
| схема JSON (типы, enum задач, hex, прямоугольники) | `asset-spec.schema.json` | `validate_spec` |
| сумма долей палитры ≤ 1; > 5 цветов — предупреждение | BFL «3-5 colors» [S8] | `validate_spec` |
| фокус вне зоны под текст; субъект и зона не на одной стороне; фокус внутри каждой безопасной зоны | §3 | `validate_spec` |
| static + движение камеры в тексте; петля + склейки; разные первый и последний кадр петли; таймлайн вне длительности; extreme close-up + establishing | BFL prompt-doctor [S1] | `validate_spec` |
| слова без видимого содержания | Ideogram magic prompt [S5] | предупреждение |
| письменность надписи против модели (Z-Image — только латиница); кириллица → OCR | `01` §12.7 | `validate_spec` |
| картинка ↔ видео; число референсов ≤ лимита модели | каталог [S12] | `validate_spec` |
| соотношение, разрешение, длительность, альфа — из значений каталога | каталог [S12] | `build_params` |
| длина промта ≤ меньшего лимита (каталог, документация); без обрезки | `02` §9.2 | `compile_prompt` |
| слов больше рекомендации вендора (Seedream — 600; FLUX.2 > 300 — предупреждение) | [S6][S8] | `compile_prompt` |

### 12.3 Заметки для D2 (полная реализация, волна 2)

1. **Шаблоны семейств из `dialects.yaml`** (`text_zone.template`, `edit.template`, `operation_verbs`,
   `intended_use_line`) прототип пока не использует — общий построитель фраз одинаков для всех.
2. **Правки (`IMG-EDIT`, `IMG-OUTPAINT`)**: в схему — блок `edit {target, change, keep[], mask, source}`; шаблоны
   Google / OpenAI / BFL / Qwen (инпейнт и аутпейнт «The original caption is: …»); полярность маски по модели
   (`openai/gpt-5-image` — чёрное меняется, `qwen/image-2.1` — белое; маска Qwen — только с одним референсом).
3. **Референсы**: сборка ролей в синтаксис семейства («Image 1: …», `<Image_1>`, «@Image 1», `@Name`,
   `<IMAGE_REF_0>`), порядок `images[]` = порядок упоминания (Qwen: «Порядок — тот, на который ссылается промпт»).
4. **Видео**: мульти-шот Kling («shot n, m, words;» [S21]), Wan (`multi_shots`, «Shot k [t0–t1 s]»), Seedance 2.5
   (разделы Asset Referencing / One-Sentence Summary / Detailed Plot / Additional Notes [S22]), полный IR H3 для
   референсов (`subject_definitions`, `retention_analysis` [S16]); «no BGM» с синонимами в начале и в конце для
   Seedance 2.5.
5. **Бюджет длины**: при превышении лимита — не обрезать, а выбрасывать блоки по приоритету (настроение → материалы
   → камера) с предупреждением; для Z-Image — «короткий профиль» спецификации.
6. **Ideogram 4**: `bbox` из `text_zone` и `subject_region`, `style_description.photo` из `camera`, проверка порядка
   ключей по `CaptionVerifier` вендора [S5].
7. **Язык**: детектор кириллицы в описательных полях → ошибка (описание должно быть английским), кроме
   `text.strings[].text`.
8. **Паспорт генерации**: в паспорт `polza.py` добавлять хэш спецификации, семейство, диалект, версию `dialects.yaml`
   [S17].
9. **Словарь слопа** — заменить встроенный короткий список на список агентов A и F.
10. **Анализ A/B** (`02` §9.5): скрипт бутстрепа и знакового критерия; запись `ab_results` в `dialects.yaml`.
11. **Обновление при новом снимке каталога**: `polza_catalog.py diff` → перезапуск `D/01` → тест «лимиты
    `dialects.yaml` = каталог» (агент N).
12. **Правило ui-research** [S18]: в модель картинок не кладут полную спецификацию — только визуальную карточку;
    компилятор так и делает, служебные поля в промт не идут.

## Частые ошибки

1. **Отправлять спецификацию целиком** (со слотом, бюджетом, форматами) как «JSON-промт».
2. **Hex без названия и без объекта** («use #FF0000 somewhere») — BFL прямо называет это ненадёжным.
3. **Доли палитры в сумме больше 1** или шесть и больше цветов.
4. **Субъект в зоне под текст** или зона на той же стороне, что и субъект.
5. **Одна зона под текст для всех соотношений** без безопасных зон — при кадрировании 9:16 заголовок ложится на лицо.
6. **Русский текст в описательных полях** (ошибка агентов при переносе брифа) — описание должно быть английским.
7. **`in_image` для важного текста** (кнопки, цены, длинные заголовки) вместо `html_overlay`.
8. **Запрет предмета без `replace_with`** у семейств, где отрицания не работают (FLUX.2) — запрет молча выпадает.
9. **Видео-длительность «как удобно»** (5 с для Seedance 1.5 Pro, 4 с для H3 Max) — модель отвергнет запрос.
10. **Полное описание сцены в i2v** — перерисовка кадра и выход за лимит (Wan 2.5 — 800 символов).
11. **Перефразированный `series_block`** в разных спецификациях серии.
12. **Параметры не из каталога** (`seed` у FLUX.2, `background` у GPT Image в polza).

## Чек-лист

- [ ] Спецификация проходит `prompt_compile.py validate` без ошибок?
- [ ] `subject.summary` конкретен и из предметной области?
- [ ] Описательные поля по-английски, культура — в `subject.culture`?
- [ ] Зона под текст задана прямоугольником, поверхностью, тоном и назначением; субъект — напротив?
- [ ] Для каждого соотношения страницы есть безопасная зона с фокусом внутри?
- [ ] Палитра: 3–5 цветов, роли, доли (сумма ≤ 1), объекты; бренд-цвета помечены `strict`?
- [ ] Стиль — видимые признаки; для серии — общий `series_block` и эталон в `references`?
- [ ] Предметные запреты имеют `replace_with`?
- [ ] Режим текста выбран осознанно; для кириллицы в картинке — `ocr_check` и `fallback`?
- [ ] Выход (соотношение, разрешение, альфа) совместим с моделью маршрута?
- [ ] Видео: длительность из значений модели, одна камера, одно действие, `audio: false`, петля — один кадр на двух концах?
- [ ] Компиляция укладывается в лимит модели без обрезки?

## Открытые вопросы и противоречия

1. **Проценты в промте** («the left 40 percent») против словесных долей — какая форма надёжнее, не измерено (тест 2
   отчёта D).
2. **Прямой JSON против прозы по разделам** для FLUX.2 — решает A/B (`02` §9).
3. **Шаблоны вендоров против общего построителя**: даст ли дословный шаблон Google «negative space» выигрыш у Nano
   Banana — проверяется тем же тестом 2.
4. **Безопасные зоны**: кадрировать мастер 16:9 или генерировать каждое соотношение отдельно — решают агенты H и E
   (цена против согласованности).
5. **Кириллица**: какой режим текста по умолчанию для баннеров — зависит от итогов теста кириллицы (C1/E, фаза 5).
6. **Схема v0.1 не покрывает** правки, мокапы, векторные задачи (`VEC-*`), 3D-иконки с прозрачностью — расширяет D2
   вместе с G и H.

## Источники

- [S1] Black Forest Labs. GitHub `black-forest-labs/skills` — `flux-3-prompt-doctor` (шаблон `brief.md`, противоречия),
  `flux-3-cinematic-inserts`, `flux-3-keyframes-continuation` (MIT; 119★; push 2026-09-09).
  https://github.com/black-forest-labs/skills — вендорский бриф до промта; высокая.
- [S2] Bria AI. «Generating an Image From 1,000 Words» (FIBO), arXiv 2511.06876. https://arxiv.org/abs/2511.06876 —
  промежуточный структурный диалект; `[исследование]`.
- [S3] База `ui`: `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md` §2.2 — палитра по ролям и частоте.
  `../../ui/12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.
- [S4] Google. Gemini API «Nano Banana image generation» (шаблон «Minimalist & negative space»), Google Cloud Blog
  «The ultimate Nano Banana prompting guide» (2026-03-06). https://ai.google.dev/gemini-api/docs/image-generation —
  первоисточник.
- [S5] Ideogram. GitHub `ideogram-oss/ideogram4`: `docs/prompting.md`, Magic Prompt v1 (2 849★; push 2026-06-30).
  https://github.com/ideogram-oss/ideogram4 — схема подписи, bbox, антислоп; высокая.
- [S6] BytePlus ModelArk. «Seedream 4.0-4.5 prompt guide» и «Seedream 4.0-5.0 tutorial».
  https://docs.byteplus.com/en/docs/ModelArk/1829186 — первоисточник.
- [S7] D. Ghosh et al. «GenEval», NeurIPS 2023, arXiv 2310.11513. https://arxiv.org/abs/2310.11513 — счёт и позиция;
  `[исследование]`.
- [S8] Black Forest Labs. «Prompting Guide — FLUX.2», HEX Color Prompting, Typography; скилл
  `flux-image-best-practices`. https://docs.bfl.ml/guides/prompting_guide_flux2 — первоисточник.
- [S9] Zhang et al. «LingT2I», arXiv 2608.11002. https://arxiv.org/abs/2608.11002 — культурная метка против языка;
  `[исследование]`.
- [S10] Google Cloud Vertex AI. «Video generation prompt guide», «Video generation best practices».
  https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/best-practice — первоисточник.
- [S11] OpenAI. «Image prompting»; Cookbook «GPT Image Generation Models Prompting Guide».
  https://developers.openai.com/api/docs/guides/image-prompting — первоисточник.
- [S12] polza.ai. Каталог `GET /api/v1/models`, снимок 2026-09-23; извлечение `99-raw/experiments/D/01-catalog-prompt-limits`
  — первоисточник параметров и лимитов.
- [S13] Alibaba Cloud Model Studio. «Text-to-video / image-to-video prompt guide».
  https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt — первоисточник.
- [S14] Runway. «Image to Video Prompting Guide». https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide
  — первоисточник.
- [S15] Recraft. API reference (`controls.colors`). https://www.recraft.ai/docs/api-reference/endpoints — первоисточник.
- [S16] MiniMax. GitHub `MiniMax-AI/MiniMax-H3` — README и скилл `h3-prompt-writing` (9 116★; push 2026-08-15).
  https://github.com/MiniMax-AI/MiniMax-H3 — IR, камера «тип + амплитуда + скорость»; высокая.
- [S17] Агент B. `../02-providers-platforms/01-polza-api.md` §12 — клиент `polza.py`, формат заданий, паспорт.
- [S18] База `ui`: `11-styles-trends/02-style-tiles-and-character-knobs.md` §5 — «полный JSON в промт
  генератора картинок не кладут», карточка 10–15 строк. `../../ui/11-styles-trends/02-style-tiles-and-character-knobs.md`.
- [S19] Google AI for Developers. «Gemini Omni Flash» — теги ролей медиа. https://ai.google.dev/gemini-api/docs/omni —
  первоисточник.
- [S20] QwenLM. GitHub `QwenLM/Qwen-Image` — `prompt_utils_2512.py` (8 363★; push 2026-02-10).
  https://github.com/QwenLM/Qwen-Image — закрывающая фраза «No other text appears in the image.»; высокая.
- [S21] Kuaishou. Kling API 3.0. https://kling.ai/document-api — синтаксис мульти-шота; первоисточник.
- [S22] BytePlus ModelArk. «Dreamina Seedance 2.0 series prompt guide», «Dreamina Seedance 2.5 prompt guide».
  https://docs.byteplus.com/en/docs/ModelArk/2607689 — первоисточник.
