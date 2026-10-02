# Векторные генераторы (Recraft) и векторизация растра: каналы, запросы, гигиена SVG

Волна 2 · агент G · 23.09.2026 · опыты: G/02 (8 настоящих SVG Recraft V4: svgo, подпись, фон, нарезка, перекраска),
G/03 (векторизация с эталоном: vtracer 1.0.0-alpha.4, potrace 1.16) · источники: документация Recraft (28 + 6 файлов
кэша), RouterAI, OpenRouter, Gen-API (дайджест помощника G), каталоги RouterAI и OpenRouter 23.09.2026, 4 ролика ·
каналы и цены — на 23.09.2026, ключей ни к одному каналу нет, всё о поведении API — `[не проверено]` до фазы 5.

## Выжимка для агента

1. **Recraft — единственный массовый генератор настоящего SVG**; маршрут для `VEC-ILLUSTR` и `VEC-ICON-FILLED`,
   **не** для линейных иконок интерфейса (только заливки, 0 `stroke`, «линии» тоньше 1 px при 24 px). → §4 [проверено]
2. **Канал — RouterAI**: `POST https://routerai.ru/api/v1/images`, `recraft/recraft-v4.1-vector` 8,74 ₽, Pro 32,79 ₽,
   `recraft/recraft-v4-styles-vector` 5,46 ₽ (+ ≈ 0,55 ₽ за запрос с референсом); SVG приходит в `data[0].b64_json`. → §1 [документация, каталог 23.09.2026]
   [поправка фазы 5, 25.09.2026: паспорта — Vector 8,83, Pro Vector 33,11 (×3,75), Styles Vector 6,07 и Styles Pro 13,80 с референсом,
   Flash 0,77; CM-01: Pro — ровно 8 иконок из 8, 35 путей, 0 градиентов, Vector — 12 с повторами, 63 пути → наборы и спот — Pro,
   фоны и черновики — Vector → `99-raw/phase5/runs/5-vector/analysis/icons/metrics.md`]
3. **Палитру и стиль через RouterAI — только гипотеза**: в его документации нет `provider.options`; у OpenRouter это
   `provider.options.recraft.controls` (и `style_id`, `style_match`, `random_seed` у Styles). Первый тест — G-07 (8,74 ₽). → §2 [не проверено]
   [поправка фазы 5, 25.09.2026: зонд B2-01 — ответ 200 без `data[]` (0 ₽): неверный `controls` доходит до Recraft и ломает запрос;
   палитра словами держится только по тону (ΔE00 заливок медиана 3,3–8,4) → точная палитра и тёмная тема — перекраской SVG
   (`svg_sheet.py recolor`, 0 ₽) → `99-raw/phase5/runs/5-vector/palette-exact/`]
4. **Запасной канал Gen-API** (`recraft-v4`, 20 ₽): задать явно `"model":"vector"`, `"pro":false` (иначе 75 ₽),
   `"translate_input":false` (иначе переведёт и надписи); `colors` — `[{"r","g","b"}]` без весов; это V4, не V4.1. → §2 [документация Gen-API]
5. **У V4/V4.1 из `controls` работают только `colors` и `background_color`**; `negative_prompt`, `text_layout`,
   `artistic_level`, `no_text`, библиотека `style` — только V2/V3. → §2 [документация Recraft]
6. **Вес цвета — «relative preference», не доля площади**: веса всем цветам или никому, сумма ≤ 1, ≤ 10 цветов;
   дублировать палитру словами; чем сложнее промт, тем хуже держится палитра. → §3 [документация Recraft]
7. **Промт вектора — 6 пунктов в порядке важности**: тип графики → логика формы → строгая палитра → дисциплина линии →
   раскладка → запреты; без слов о фактуре и материале; набор — «exactly N» + перечень + сетка + «No text.». → §3 [документация Recraft]
8. **Градиент и свечение векторная модель не делает** (плоские заливки) — растровая модель + векторизация или CSS
   поверх SVG. → §3 [V:AOPKK0LlI_Q 13:21] [мнение вендора]
9. **SVG Recraft — только после конвейера**: удалить фон-прямоугольник (у 5 из 8) **до** svgo → убрать
   `preserveAspectRatio="none"` и пиксельные `width`/`height` → svgo `multipass` + `floatPrecision: 1` = **−57…−65 %**
   без видимых потерь (p99 разницы ≤ 10 из 255). → §4 [проверено]
10. **Подпись `<recraft-signature>` (Ed25519) не удалять**: условия Recraft запрещают удалять метаданные провенанса;
    `removeMetadata: false` её не спасает — нужен ещё `removeUnknownsAndDefaults: {unknownContent: false}` (+400 байт). → §4 [проверено: G/02; документация DT §6.4]
    [поправка фазы 5, 25.09.2026: через RouterAI `<recraft-signature>` нет ни в одном из 9 SVG; в `<metadata>` — манифест C2PA
    17 700 байт (CM-02 — 50 156), тот же конфиг его сохраняет, но манифест валиден только в исходнике: после чистки путей c2patool —
    `Invalid`, svgo `preset-default` удаляет `<metadata>` → **мастер SVG хранить побайтно, на страницу — без `<metadata>`, провенанс —
    паспорт генерации** → `99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md`]
11. **Иллюстрации и после svgo тяжёлые (68–123 КБ)** — не inline: `<img src="*.svg">` с кэшем или AVIF. → §4 [проверено]
    [поправка фазы 5, 25.09.2026: было «68–123 КБ — не inline» (публичные образцы V4); у V4.1 через RouterAI без манифеста — набор
    иконок 6,7 КБ (Pro) / 10,1 (Vector, Pro легче на 34 %), спот 4,5 / 6,9, фон 5,1 / 2,3, Styles 3,0 / 2,7 → inline и спрайт
    допустимы; тяжёл только «фото → вектор» (CM-02, 131 путь) — 52,7 КБ → `99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md`]
12. **Набор иконок приходит одним файлом с подписями** — резать по кластерам растра (4 из 4, 5 из 6 — звёзды ушли
    как «подпись») и нормализовать в 24×24 с живой областью 20. → §5 [проверено]
13. **`currentColor` для иконок Recraft небезопасен**: у 3 из 5 «линейных» иконок отверстия нарисованы светлой заливкой
    поверх тёмной → в тёмной теме сплошное пятно. Лечение — растр 480 px → potrace (настоящие отверстия, 0,8–3,0 КБ). → §5 [проверено]
14. **Серия** — V4 Styles от **одного** чистого референса, тот же `aspect_ratio` и seed; разные референсы «сталкиваются».
    Через RouterAI стиль передаётся картинкой в `input_references` (1–10): создать `style_id` там негде. → §6 [документация Recraft; не проверено]
    [поправка фазы 5, 25.09.2026: CM-03 — Styles по своей Pro-иконке переносят палитру и вес, но не состав набора (у Styles Pro
    «календарь» стал лицом); у V4.1 Vector `input_references` (1) — это image-to-image, не стиль (CM-02: фото перерисовано слоями)]
15. **Векторизация плоской картинки с ≤ 4–8 цветами почти без потерь**: vtracer `--palette` дал 8,0 КБ против 8,4 КБ
    «родного» вектора, SSIM 0,985. → §7 [проверено]
16. **Сложная иллюстрация (20+ цветов) векторизуется плохо**: по умолчанию 811 оттенков и 2,8× вес; с палитрой 8 —
    1,5× вес, SSIM 0,79–0,85. Просить у модели плоскую графику с заданным числом цветов (≤ 8). → §7 [проверено]
17. **Палитру vtracer задавать полностью**: цвета бренда + цвет контура + фон. «8 самых частых» и «8 по площади»
    потеряли чёрный — волосы и контуры стали зелёными. → §7 [проверено]
18. **Монохром (логотип, силуэт, иконка) — potrace**: 0,01–0,1 с, 4–8 путей, цвет — `currentColor`. → §7 [проверено]
19. **Кириллица**: V3 не пишет (только буквы-двойники латиницы), у V4/V4.1 не документирована → G-09 (7,64 ₽); текст
    в SVG Recraft — контуры, поэтому текст на сайте — HTML поверх. → §3 [документация; не проверено]
    [поправка фазы 5, 25.09.2026: растровые V4.1 и V4.1 Utility (3,86 ₽) написали короткую кириллицу дословно в 3 из 3 картинок
    (E-07 — промт E-02 побайтно, G-09) — глаз и OCR (pass у E-07 и G-09 V4.1, у Utility ложная тревога на мелком) → с Recraft в
    сравнении E-02 дословно 7 моделей из 10 → `99-raw/phase5/runs/S5-analysis/E-07.ocr.json`]

## 1. Каналы и цены (23.09.2026)

| Канал | Вектор | Pro-вектор | Серия в стиле | Векторизация | Ключ | Ответ |
|---|---|---|---|---|---|---|
| **RouterAI** (рубли, клон OpenRouter) | `recraft/recraft-v4.1-vector`, `recraft/recraft-v4-vector` — 8,74 ₽ | 32,79 ₽ | `recraft/recraft-v4-styles-vector` 5,46 ₽ (+ ≈ 0,55 ₽ за запрос с референсом), Pro 13,11 | — | заводит заказчик | синхронно, `data[].b64_json`, `usage.cost` в ₽ |
| **Gen-API** (рубли) | `recraft-v4` `model:"vector"`, `pro:false` — 20 ₽ | 75 ₽ | нет `style_id` | `image-2-svg` — 1 ₽ | заводит заказчик | задача → `GET /api/v1/request/get/{id}` → `result[0]` (ссылка 24 ч) |
| Recraft напрямую ($) | `recraftv4_1_vector` $0,08 | `recraftv4_1_pro_vector` $0,30 | `recraftv4_styles_vector` $0,05 | `vectorize` $0,01 (без палитры) | не будет (оплата вне РФ) | `data[].url` ≈ 24 ч |
| polza | — | — | — | — | есть к фазе 5 | Recraft в polza нет |

- Время по документации вендора: V4.1 vector ≈ 12 с, utility vector 14 с, pro 15–17 с; лимит 100 картинок/мин,
  5 запросов/с; промт ≤ 10 000 символов [S1].
- `Utility`-вектор («clean, predictable, flat lighting») в каталоге RouterAI **отсутствует** — там только растровые
  `recraft/recraft-v4.1-utility` (3,82 ₽) и `…-utility-pro` (22,95 ₽) [S3]. Тест W6 №7 сведён в G-13 «растр Utility → vtracer».
- Соотношения сторон: Recraft — 14, RouterAI/OpenRouter — 5 (+ `auto`), у Styles — 11, у Gen-API — 5 [S1][S3][S5].

## 2. Тела запросов

```json
// RouterAI · recraft/recraft-v4.1-vector · 23.09.2026 · [не проверено: passthrough provider.options — гипотеза G-07]
{"model": "recraft/recraft-v4.1-vector", "prompt": "…", "aspect_ratio": "1:1", "output_format": "svg", "n": 1,
 "provider": {"options": {"recraft": {"controls": {
   "colors": [{"rgb": [15, 23, 42], "weight": 0.5}, {"rgb": [13, 148, 136], "weight": 0.3}, {"rgb": [245, 158, 11], "weight": 0.2}],
   "background_color": {"rgb": [248, 250, 252]}}}}}}
```

```json
// Gen-API · POST https://api.gen-api.ru/api/v1/networks/recraft-v4 · 23.09.2026 · [документация; не проверено]
{"model": "vector", "pro": false, "translate_input": false, "is_sync": false, "aspect_ratio": "1:1", "prompt": "…",
 "colors": [{"r": 15, "g": 23, "b": 42}, {"r": 13, "g": 148, "b": 136}], "background_color": {"r": 248, "g": 250, "b": 252}}
```

- RouterAI: в документации эндпоинта `output_format` — только png/jpeg/webp, `svg` — только в каталоге моделей;
  `provider` не описан [S2]. OpenRouter: `allowed_passthrough_parameters` у vector — `style`, `controls`, `text_layout`,
  у styles-vector — `style_id`, `style_match`, `controls`, `random_seed` [S4]. Для V4 из них реально работают только
  `controls.colors`/`background_color` и стилевые [S1].
- Gen-API: заголовки `Authorization: Bearer`, JSON; `callback_url` или опрос; результаты 14 дней, ссылки 24 ч;
  что в `result[0]` придёт `.svg` — не проверено [S5].
- Готовые задания — `99-raw/phase5/jobs/G-07…G-16` (план — `99-raw/phase5/G-plan.md`).

## 3. Промтинг Recraft V4/V4.1 для вектора

Структура вендора для вектора и логотипов — **тип → форма → палитра → линия → раскладка → запреты**; «Avoid texture
or material-focused language. Vector output responds to structural definition and geometric clarity» [S1]. У V4.1
короткий промт сильнее; разведка — 3–6 слов, финал — структурированный промт [S1].

```text
// recraft/recraft-v4.1-vector · RouterAI · 23.09.2026 · [не проверено — задание G-07/G-08]
A set of 4 flat vector UI icons for an online store, arranged in a 2x2 grid with generous equal spacing: a delivery
truck, a parcel box, a credit card, a chat bubble with three dots. Simple geometric shapes with rounded corners,
flat color blocks, consistent visual weight and size, front view, each icon centered in its cell.
No labels, no text, no gradients, no shadows, no texture.
```

```text
// recraft/recraft-v4.1-vector · 23.09.2026 · [не проверено — задание G-10; без слов о настроении, проверка «moody»]
Flat vector illustration for an empty shopping cart state on an e-commerce website: a single shopping cart with a
small paper bag beside it. Simple rounded geometric shapes, flat color blocks, three colors plus white, centered
composition with generous empty space, front view, plain light background. No text, no people, no gradients,
no shadows, no texture. Palette: deep navy #0F172A, teal #0D9488 accent, amber #F59E0B highlights.
```

- **Запреты — прозой** («no gradients, no realism, no shadows»): у V4 нет поля негатива [S1][V:nBd9JJuAT1Y 35:51].
- **Набор иконок**: «exactly N», перечень, сетка («four per row»), «No text.» — иначе подписи под каждой (P/07 ex7, ex8).
- **Упрощать явно**: «minimalist vector simplified …, no details, flat color blocks»; V4 «overdesigned» простую
  иконку руки, V4.1 — пригодно [V:AOPKK0LlI_Q 18:34, 24:40] [мнение вендора].
- **Без слов о настроении** модель часто уходит в «moody» (дождь, снег) [V:nBd9JJuAT1Y 52:16] — задавать свет и время
  явно или «plain light background».
- **Hex в промте** у Recraft не документирован; палитра — `controls` + названия цветов [S1].
- **Текст** — в кавычках с иерархией; в SVG станет контурами; кириллица не документирована (G-09).

## 4. Что приходит и как чистить (G/02)

Структура (8 публичных выходов V4): только `<path>` с `fill="rgb(…)"`, 0 `stroke`, 0 `<text>`, `<g>` нет; корень —
`preserveAspectRatio="none"`, `width`/`height` в пикселях, `viewBox` в сетке 2048; фон-прямоугольник первым путём у
иконок и логотипа; `linearGradient` у 3 из 8; подпись `<metadata><recraft-signature>{… "signing_algo":"Ed25519" …}` [S6].

| Шаг | Что делать | Результат G/02 |
|---|---|---|
| 1. Фон | первый путь на весь холст светлого цвета — удалить **до** svgo (после — относительные координаты, hex) | удалён у 5 из 8 |
| 2. Корень | убрать `preserveAspectRatio="none"`, `width`/`height`, `style`; `viewBox` оставить | — |
| 3. svgo | `multipass`, `floatPrecision: 1` | −57…−65 %: 194,8 → 80,3 КБ; 45,5 → 15,8 КБ; разница растра p99 ≤ 10/255 |
| 4. Подпись | конфиг ниже (оставить) | +400 байт |
| 5. Поставка | иллюстрация 68–123 КБ — `<img>`/AVIF; иконка 0,7–5,2 КБ — спрайт | — |

```js
// svgo 4.1.0 — svgo.keep-signature.config.mjs — [проверено]
export default { multipass: true, floatPrecision: 1,
  plugins: [{ name: 'preset-default', params: { overrides: {
    removeMetadata: false,                                // пресет удаляет <metadata>
    removeUnknownsAndDefaults: { unknownContent: false }  // иначе удалит <recraft-signature> как неизвестный элемент
  } } }] };
```

## 5. Нарезка набора и перекраска

- **Нарезка** (`slice.py`): тёмные пути → растр 1024 → дилатация 8 px → кластеры; кластеры ниже 45 % высоты
  максимального — подписи; для каждой иконки — квадратный `viewBox` вокруг кластера × 24/20 (живая область 20 из 24).
- **Перекраска**: заменить тёмную заливку на `currentColor` можно, только если отверстия настоящие. У «линейных»
  иконок ex8 3 из 5 (сумка, метка, карта) — тёмная фигура + светлые фигуры поверх: без светлых — сплошной силуэт, со
  светлыми — белые пятна в тёмной теме. Проверка — рендер на тёмном фоне; лечение — растр 480 px → potrace:

```bash
# potrace 1.16 — [проверено]
potrace icon.pbm -s -o icon.svg --turdsize 4 --alphamax 1 --opttolerance 0.2   # затем fill="#000000" → currentColor
```

- **Вес «линий» Recraft**: покрытие при 24 px 0,20–0,53 от `circle`/`square` Lucide (набор Lucide — 0,75–1,50) —
  рядом со штрихом 2 выглядят вдвое-втрое тоньше; `VEC-ICON-LINE` — только LLM (`01-svg-by-llm.md`).

## 6. Серия и палитра

- **V4 Styles**: стиль от одного чистого референса — «the safe move»; несколько референсов — только из одного
  визуального мира («Mixed references… collide»); тот же `size` и `random_seed`; разнообразие — новым промтом, а не
  референсами; «Color matching is a maybe, not a promise» [S1]. `style_match`: `precise` (по умолчанию) или `flexible`.
- **Иконки отдельными файлами одного вида** — вендор советует Styles от одной иконки-референса: «The style handles line
  weight, corner radius, and fill logic» [S1] — это путь для `VEC-ICON-FILLED`, проверка — G-11.
- **Блок стиля прозой** (стиль-промт без сюжета, до 10 000 символов) — приём вендора, когда стилей нет [V:AOPKK0LlI_Q
  24:40]; сравнение со Styles — G-12 (W6 №9).
- **Проверка палитры в SVG точная**: заливки читаются из файла, ΔE00 к палитре бренда считает `../../scripts/lib/color.py`;
  порог — 3 (незаметно), > 5 — нормализовать заменой на ближайший цвет паспорта (ui 07/02 §11.2 п. 5).

## 7. Векторизация растра (G/03)

| Образец | Вариант | КБ после svgo | путей | цветов | SSIM |
|---|---|---|---|---|---|
| плоская иллюстрация, 22 цвета («родной» вектор 80,2 КБ) | vtracer по умолчанию | 224,1 | 1016 | 811 | 0,899 |
| | `--max-colors 8 --simplify 1.5 --optimize 2` | 124,8 | 704 | 8 | 0,845 |
| | `--palette` 8 частых заливок | 118,4 | 474 | 8 | 0,790 (чёрный потерян) |
| | `--palette` 12 цветов по площади | 119,9 | 527 | 11 | 0,851 |
| | potrace, ч/б силуэт | 46,7 | 4 | 1 | 0,958 (к ч/б) |
| 6 иконок, 4 цвета («родной» 8,4 КБ) | vtracer по умолчанию | 15,0 | 77 | 62 | 0,989 |
| | `--palette` 4 цвета | **8,0** | 34 | 4 | 0,985 |
| | potrace ч/б | 8,5 | 8 | 1 | 0,994 |

```bash
# vtracer 1.0.0-alpha.4 (99-raw/tools/bin/vtracer-1.0.0a4) — [проверено]
vtracer -i in.png -o out.svg --palette '#0f172a,#0d9488,#f59e0b,#ffffff' --simplify 1.5 --optimize 2
svgo out.svg -o out.min.svg --multipass --precision 1
```

- **Когда да**: иконки, логотипы, дуотон, плоские иллюстрации с ≤ 8 цветами, сгенерированные растровой моделью
  по промту «flat vector illustration, N colors, no gradients» [V:_Bc4g6fFMp0 00:31] [практика].
- **Когда нет**: фото, свечение, градиенты, сложные картинки («у медведя 12 когтей» [V:cEw5iTNTfZg 16:22]) — оставлять
  растром (AVIF).
- **Каналы за деньги**: Gen-API Image2svg 1 ₽ — те же параметры, что у vtracer 0.6 (без палитры), тест G-16; Recraft
  `vectorize` $0,01 — без управления цветами, SVG на вход не принимает [S1][S5]. Локальный vtracer бесплатен и даёт палитру.
- **Время**: vtracer 0,1–5 с на 1024², potrace 0,01–0,1 с (1 поток).

## Частые ошибки

1. Recraft для линейных иконок интерфейса — нет `stroke`, вес втрое легче набора.
2. Gen-API со значениями по умолчанию: растр вместо вектора, Pro за 75 ₽, перевод промта с надписями.
3. Параметры V3 (`negative_prompt`, `text_layout`, `style` по имени, `no_text`) в запросе к V4/V4.1.
4. Вес цвета как «доля площади» — у Recraft это предпочтение.
5. svgo по умолчанию на Recraft — удаляет подпись провенанса (нарушение условий).
6. Удаление фона после svgo — регулярка по абсолютным координатам уже не срабатывает.
7. `currentColor` на иконки Recraft без проверки на тёмном фоне.
8. Inline-вставка иллюстрации на 100+ КБ в HTML.
9. `vtracer` без палитры (сотни оттенков) или палитра без цвета контура.
10. Ошибки агентов «по памяти»: id `recraftv4.1` (верно `recraftv4_1`), «Recraft умеет inpaint и фон у V4» (только V3),
    «V4.1 Flash $0,007 в API» (нет в API), «поле негатива у V4» (нет).

## Чек-лист

- [ ] Задача — иллюстрация или цветная иконка (не линейная)?
- [ ] Канал и цена выбраны; в Gen-API явно `model:"vector"`, `pro:false`, `translate_input:false`?
- [ ] Промт по 6 пунктам, запреты прозой, «No text.» у наборов?
- [ ] Фон-прямоугольник удалён до svgo, корень поправлен, подпись сохранена?
- [ ] Иллюстрация отдаётся `<img>`/AVIF, иконки — нарезаны и нормализованы в 24×24?
- [ ] Перекраска проверена на тёмном фоне (нарисованные отверстия → potrace)?
- [ ] ΔE00 заливок к палитре ≤ 3 (иначе — замена на ближайший цвет паспорта)?
- [ ] Для векторизации — ≤ 8 цветов, палитра с цветом контура, SSIM против растра ≥ 0,95?

## Открытые вопросы и противоречия

1. Пропускает ли RouterAI `provider.options.recraft` (controls, style_id) — главный вопрос G-07; документация RouterAI
   о нём молчит, каталог перечисляет только `aspect_ratio`, `output_format`, `n`, `input_references`. [поправка фазы 5,
   25.09.2026: пропускает — неверный `controls` доходит до Recraft и ломает запрос (B2-01, 0 ₽); G-07 заменён CM-01]
2. Пишет ли Recraft V4.1 кириллицу — G-09; для V4 вендор пишет «multi-language» без списка.
3. Тезис «Recraft без `stroke`» проверен на 8 образцах V4; V4.1, Utility и Styles — не проверены (G-07, G-11, G-13).
4. Pro-вектор: «только выше разрешение и меньше шума» (вендор) против «больше деталей» [V:nBd9JJuAT1Y 02:02] — G-14.
   [поправка фазы 5, 25.09.2026: CM-01 — Pro точнее по заданию (8 из 8 иконок против 12 с повторами) и чище геометрия (путей −44 %);
   фон — лучше у Vector; голоса заказчика нет («сложно выбрать»)]
5. Условия Recraft: «ассеты — ваши» (DT §6.2) и «кэш у приложения ≤ 30 дней, без постоянной базы» (DT §3.6) — к агенту L.
6. Стили Recraft во времени: 2025 — есть (V3), июнь 2026 — у V4.1 нет, август 2026 — V4 Styles; правила о стилях датировать.
7. Карточка C1 `recraft-v4-1.yaml` и `05-prompting/01` §11.3, §13 расходятся с документацией (id, inpaint, `style`,
   негатив, смысл веса) — поправить при синтезе.

## Источники

- [S1] Recraft. API reference (endpoints, models, styles, appendix, image inputs), Prompting with Recraft V4, V4 Styles creation guide, Developer Terms — снимки 23.09.2026 (`99-raw/cache/recraft-2026-09-23/`, `recraft-D/`, `www.recraft.ai_*`); первоисточник, прочитан помощником целиком.
- [S2] RouterAI. «Генерация изображений», routerai.ru/docs/guides/overview/multimodal/image-generation, 23.09.2026 (`99-raw/cache/routerai.ru_docs_guides_overview_multimodal_image-generation_753f42c7.md`).
- [S3] RouterAI. Каталог `routerai.ru/api/v1/models`, 23.09.2026 (`99-raw/experiments/P/04-ru-aggregators/routerai_models.json`) — id, параметры, цены.
- [S4] OpenRouter. Image Generation guide + `/api/v1/images/models/recraft/*/endpoints`, 23.09.2026 (`99-raw/cache/openrouter-2026-09-23/`) — passthrough.
- [S5] Gen-API. Документация (генерации, результат, webhooks, перевод параметров), страницы `recraft-v4` и `image-2-svg`, прайс 23.09.2026 (`99-raw/cache/gen-api.ru_*`, `99-raw/experiments/P/04-ru-aggregators/genapi_prices_2026-09-23.txt`).
- [S6] Агент P. Опыт P/07 «Структура SVG Recraft V4» (8 образцов Replicate) — `99-raw/experiments/P/07-recraft-svg-structure/`.
- [S7] Дайджесты и транскрипты: `nBd9JJuAT1Y` (Recraft V4, основательница), `AOPKK0LlI_Q` (Office Hours V4.1, W6), `_Bc4g6fFMp0`, `cEw5iTNTfZg` (ЦЕХ) — `91-videos/`.
- [S8] vtracer (visioncortex/vtracer, релиз 1.0.0-alpha.4 от 29.08.2026, MIT), potrace 1.16 (P. Selinger, GPL) — справка CLI.
- [S9] Опыты G/02, G/03 (`99-raw/experiments/G/`) — все числа §4, §5, §7.
