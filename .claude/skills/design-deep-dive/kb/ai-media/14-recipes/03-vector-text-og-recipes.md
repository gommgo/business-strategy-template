# Рецепты вектора и текста: набор иконок, Recraft-иллюстрация, паттерны и текстуры, OG с кириллицей, фавиконы, инфографика маркетплейса

Волна 3 · агент M · 24.09.2026 · опора — G (`07/01–04`, опыты G/01–G/05), H (`08/03` §2–§3), J (`01` §7, `pages/08`),
K (`01` §4 — OCR кириллицы), B2 (`07` — каналы), L, E (блок кириллицы E-02…E-07) · опытов M — 4 (`99-raw/experiments/M/06-og-marketplace`,
`07-texture`, `08-svg-favicons`, `09-demo-acceptance`) · снимок каталога polza `2026-09-24`; RouterAI и Gen-API — прайсы
23.09.2026 (B2, P). Каркас рецепта — `01-hero-recipes.md` §0.

## Выжимка для агента

1. **Знакомую иконку не генерировать — брать из набора** (`lucide-static` 1.47.0, ISC, 2 112 SVG): LLM воспроизводит известные
   по памяти (9 из 20 с IoU ≥ 0,92) → генерация только для метафор, которых в наборе нет → §1.1 `[проверено]`.
2. **Новая метафора — LLM по шаблону G** (`99-raw/phase5/inputs/G/llm-svg-icons.{system,user}.txt`: шапка дословно, геометрия в
   [2, 22], зазор ≥ 2 px, ≤ 8 элементов) → `check_icons.py` → лист 16/24/48 на светлом и тёмном → узнаваемость отдельно → §1.2
   `[проверено]` [поправка фазы 5, 25.09.2026: G-01…G-04 прогнаны — GPT-5.6 Sol (3,43 ₽) и Gemini 3.8 Flash (0,84 ₽)
   дали 6 из 6 валидных SVG 24/2; Sonnet 5 — 9,77 ₽ за пустой ответ (рассуждения съели лимит), DeepSeek V4.1 Flash — 1,17 ₽ и 0 SVG;
   по полю и зазору (`check_icons.py`) — 4 из 6 у обеих (Claude в сессии — 6 из 6); новые метафоры съезжают к знакомым глифам (гиря ≈
   Lucide `lock` 0,547, коляска ≈ `shopping-cart` 0,497) → `99-raw/phase5/runs/S5-analysis/G-llm-svg/G-01-gpt56sol.check.md`].
3. **Геометрию чинит правка по флагам, узнаваемость — нет**: наша «кофемолка» за 3 прохода — зазор 1,64 → 0,85 → 3,1 px
   (рукоять и ручка одним путём), но глазом похожа на банку или рюкзак → новая метафора всегда с подписью → §1.3 `[проверено]`.
4. **Поставка иконок — спрайт `<symbol>` + `<use>` и `currentColor`**: 9 иконок — 2,6 КБ; внешний `sprite.svg#id` работает
   только по http(s), не с `file://` → §1.4 `[проверено: демо]`.
5. **Recraft — не для линейных иконок** (залитые контуры тоньше 1 px при 24 px, без `stroke`); для иллюстраций и цветных
   иконок — `recraft/recraft-v4.1-vector` через RouterAI, 8,74 ₽; Pro — 32,79 ₽ → §2.1 `[проверено: G/02; документация B2]`
   [поправка фазы 5, 25.09.2026: цены 25.09 — 8,83 / 33,11 ₽ (курс +1 %); CM-01: Pro Vector — ровно 8 иконок из 8, 35 путей,
   0 градиентов; Vector — 12 с повторами, 63 пути, 2 градиента → наборы иконок и споты — Pro, фоны и черновики — Vector; фото →
   вектор — `input_references` = image-to-image (CM-02) → `99-raw/phase5/runs/5-vector/analysis/icons/metrics.md`].
6. **Палитра Recraft через RouterAI — до зондов B2-01/B2-02 только словами** (G-08); `provider.options.recraft.controls` —
   гипотеза: неподдерживаемое «игнорируется», 400 не придёт → §2.2 `[не проверено: B2-01]` [поправка фазы 5, 25.09.2026: было —
   «игнорируется»; B2-01 — ответ 200 без `data[]` (0 ₽): неверный `controls` доходит до Recraft и ломает запрос; палитра словами
   держится только по тону (ΔE00 заливок медиана 3,3–8,4) → точная палитра и тёмная тема — перекраской SVG `svg_sheet.py recolor`
   за 0 ₽ → `99-raw/phase5/runs/5-vector/palette-exact/`].
7. **SVG Recraft на сайт — только после конвейера G/02**: удалить фон-прямоугольник до svgo → убрать `preserveAspectRatio="none"`
   и пиксельные размеры → svgo `multipass` + `floatPrecision: 1` = −57…−65 % → §2.3 `[проверено]`.
8. **Подпись `<recraft-signature>` не удалять** (условия Recraft §6.4): svgo-конфиг `keep-signature` (`removeMetadata: false` +
   `removeUnknownsAndDefaults.unknownContent: false`), +400 байт → §2.3 `[проверено: G/02; документация L]` [поправка фазы 5,
   25.09.2026: через RouterAI `<recraft-signature>` нет ни в одном из 9 SVG, вместо неё в `<metadata>` — манифест C2PA 17 700 байт
   (CM-02 — 50 156); тот же конфиг его сохраняет (+17,7 КБ на файл), но после чистки путей манифест `Invalid`, а svgo `preset-default`
   удаляет `<metadata>` → мастер SVG — побайтно, на страницу — без `<metadata>`, провенанс — паспорт генерации; при нарезке — манифест
   в `_source/`, в иконке `<desc>` → `99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md`].
9. **Иллюстрации Recraft и после svgo 68–123 КБ** — не inline: `<img src="*.svg">` с кэшем или растр AVIF; `currentColor` у
   иконок Recraft небезопасен (отверстия нарисованы цветом фона) → растр 480 px → potrace → §2.4 `[проверено]`
   [поправка фазы 5, 25.09.2026: у V4.1 через RouterAI без манифеста — набор иконок 6,7 КБ (Pro) / 10,1 (Vector, Pro легче на 34 %),
   спот 4,5 / 6,9, фон 5,1 / 2,3, иконка после нарезки 0,98–2,5 КБ → inline и спрайт допустимы; 68–123 КБ — публичные образцы V4
   волны 2; тяжёл только «фото → вектор» (CM-02) — 52,7 КБ → `99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md`].
10. **Геометрический паттерн — кодом** (плитка 133–177 байт, `mask-image` + цвет из токена); штрих через край плитки продлевать
    на период, проверять повтором 4×4 глазом → §3.1 `[проверено]`.
11. **Бесшовность промтом не получается** (параметра tile нет ни у одной модели polza); органика — разрез минимальной ошибки
    `tile_check.py cut --overlap 96` (шов ≤ 1,3), регулярная сетка — код или заделка креста маской → §3.2 `[проверено]`.
12. **Готовый тайл библиотеки CC0 брать целиком**: Poly Haven `hessian_230` — шов 1,18 / 0,67 (бесшовен по построению); вырез
    1024 из него — 2,87 / 4,27 → cut96 — 1,19 / 1,36 (на границе) → §3.3 `[проверено]`.
13. **Текстура-оверлей — в оттенках серого, AVIF 4:0:0** (`avifenc -y 400`): мешковина 256 px — 9,8 КБ, 384 — 24,5 КБ при s2 ≥ 70;
    цветной AVIF не дошёл до 70 к q60, WebP 384 — 49,6 КБ; цвет — CSS `background-color` + `mix-blend-mode: multiply` → §3.4 `[проверено]`.
14. **Зерно и шум — поверх CSS/SVG (280 Б)**, не в файле: дизеринг до кодека съедается (ступень 0,33–0,40 как без него) →
    §3.5 `[проверено]`.
15. **OG с кириллицей — HTML-шаблон поверх кадра → Playwright → JPEG**: у демо 1200×630 q86 — 46,4 КБ; ключевое в центральных
    1100×530; AVIF в OG не ставить; `og:image:width/height/alt` обязательно → §4 `[проверено]`.
16. **Кириллица моделью — только после итогов блока E-02…E-07 и с OCR K**; по умолчанию текст на картинке — HTML/шаблон
    (A, routing `IMG-TEXT-CYR` primary) → §4.1 `[не проверено: E-02…E-07]` [поправка фазы 5, 25.09.2026: E-02 — баннер из 3 строк
    дословно у 6 из 9 моделей (Flare, GPT Image 2, NB2, NB Pro, Seedream 5 Pro, Seedream 4.5 — трафаретом), Sunburst — «– 30»,
    Qwen 2.1 и FLUX.2 Pro — ошибки; E-07 (промт E-02 побайтно) и G-09 (Recraft V4.1 растр и Utility, 3,86 ₽) — дословно 3 из 3 (глаз;
    OCR — pass у E-07 и G-09 V4.1, у Utility ложная тревога на мелком) → с Recraft дословно 7 моделей из 10; E-03…E-06 (3 из 3, язык промта, перевод) — отменены 25.09 → HTML остаётся умолчанием →
    `99-raw/phase5/runs/2.1-cyrillic/E-02.ocr.txt`].
17. **Текст шаблона проверять в два слоя: вёрстку — по DOM, буквы — OCR по слою текста без товара**: `layout_check.py`
    (прямоугольники строк против альфы товара, переполнения, nowrap-флекс-элементы) поймал «1–2 дня» на банке — ошибку вёрстки,
    которую OCR прочитал честно, а разбор принял за «склейку строк OCR»; OCR слоя текста (товар скрыт) — 7 из 7 строк, CER 0, а
    с исправленной вёрсткой и банкой в кадре детектор склеивает строку колонки с этикеткой на той же высоте («ИСНЯ ОБЖА», 0,40);
    OG со всеми 5 строками в `--expect` — pass, CER 0 → §4.4, §6.2 `[проверено]`.
18. **Фавиконы — 3 файла** (ICO 32 одним размером, SVG с тёмной темой внутри, apple-touch 180 с цветным фоном и полем ≈ 20 px) ≈ 4 КБ;
    PWA — ещё 192, 512, maskable 512 (рисунок в круге ⌀ 409,6) и манифест; из готового знака, логотип не генерировать → §5
    `[проверено: G/04; M/08 — 1 005 + 469 + 2 778 байт]`.
19. **Инфографика маркетплейса — HTML-шаблон 900×1200 + настоящий вырез + CSS-фон** → WebP по s2 ≥ 80 (48,8 КБ); ИИ —
    только фон/сцена; диапазоны «1–2 дня» — `white-space: nowrap` **внутри одного элемента подписи**: nowrap-`span` прямо во
    флекс-`li` становится отдельным флекс-элементом и уезжает на товар → §6.3 `[проверено: M/06, layout_check]`.
20. **Текст-факты (цены, характеристики, даты) — никогда в пикселях модели** (L строка 24, 38-ФЗ ст. 5) — только HTML/SVG →
    §6.1 `[документация L]`.
21. **Набор слайдов карточки** (фичи, выгоды, инструкция, сравнение) — один HTML-шаблон 3:4 с разными раскладками, товар —
    вырез; «modern and clean», «mobile optimized» у нас — крупный кегль и ≤ 3 строк на слайд → §6.4 [V:12pQ0W2bCDE 16:18]
    [V:12pQ0W2bCDE 22:24] `[практика; мнение M]`.

## 1. Набор иконок (`VEC-ICON-LINE`)

### 1.1 Маршрут

| Шаг | Что | Цена | Статус |
|---|---|---|---|
| 1 | выбор из набора продукта: `99-raw/tools/node/node_modules/lucide-static/icons/<name>.svg` (ISC) | 0 | [проверено: G/01, демо — flame, bean, truck, repeat, sprout, arrow-right, pause, play] |
| 2 | нет метафоры → LLM по шаблону G; по умолчанию — Claude в сессии (0 ₽); модели polza — G-01…G-04 (0,17–4,92 ₽ за 6 иконок) | 0–5 ₽ | [проверено: G/01; модели — не проверено] [поправка фазы 5, 25.09.2026: факт G-01…G-04 — 3,43 / 0,84 / 9,77 (пусто) / 1,17 (0 SVG) ₽; валидны 6 из 6, по полю и зазору — 4 из 6 у GPT-5.6 Sol и Gemini 3.8 Flash → Claude в сессии остаётся умолчанием] |
| 3 | `check_icons.py` (venv-G) + один проход правки по флагам | 0 | [проверено] |
| 4 | лист 16/24/48 на светлом и тёмном | 0 | [проверено: M/08 `icons_sheet.png`] |
| 5 | узнаваемость: VLM без подсказки (G-06) или человек за 5 с | 0,26 ₽ | [не проверено] [поправка фазы 5, 25.09.2026: G-06 (0,21 ₽, лист G/01) — с глазом совпал 12 из 12, новые метафоры узнаны 2 из 5, уверенность на промахах 0,75–0,9 → сито, не мера] |

### 1.2 Проверка

```bash
# check_icons.py (G) · venv-G (svgelements 1.9.6, cairosvg 2.9.1) — [проверено: G/01; M/08 new-icons]
99-raw/tools/venv-G/bin/python ../../scripts/ai-media/check_icons.py new-icons/ \
   --ref 99-raw/tools/node/node_modules/lucide-static/icons --json check_icons.json
```

Флаги — шапка и жёсткий цвет (fail), остальное — предупреждения: зазор < 2 px, «узкие» участки фона, вес против `circle`/`square`
Lucide (коридор 0,75–1,50), доля узлов на сетке, центр масс.

### 1.3 Пример: новая метафора «ручная кофемолка»

```xml
<!-- своя иконка по правилам Lucide · check_icons: зазор 3,1 px, 1 предупреждение «узко 3,05» · узнаваемость — сомнительна · [проверено] -->
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="10" rx="2"/>
<path d="M7 11a5 5 0 0 1 10 0"/><path d="M12 6V2h5v3"/><path d="M10 16h4"/></svg>
```

Итерации: рукоять `M12 6V3h5` в 1,42 px от купола → зазор 1,64 (флаг); рукоять выше и отдельная ручка `M17 2v3` → два элемента
касаются, зазор 0,85; рукоять и ручка одним путём `M12 6V2h5v3` → 3,1 px. Глазом на 48 px — «банка/рюкзак с ручкой»: G/01 —
узнаются 2 из 5 новых метафор → в демо иконка стоит только рядом с подписью «Помол под способ».

### 1.4 Поставка

```html
<!-- спрайт: один файл, currentColor, в тёмной теме меняется токен, а не файл · [проверено: демо, J pages/08] -->
<svg aria-hidden="true" width="24" height="24"><use href="assets/svg/sprite.svg#i-flame"/></svg>
```

- Спрайт собирается скриптом из файлов набора (`99-raw/experiments/M/08-svg-favicons/build.py`): тело `<svg>` → `<symbol id viewBox
  fill stroke …>`; 9 иконок — 2 652 байта.
- 16 px при штрихе 2 = 1,33 px — для плотного интерфейса держать вариант набора со `stroke-width="1.5"` (G `07/01` §6).
- Анимация иконки — CSS `@keyframes` + `@media (prefers-reduced-motion: reduce)`; SMIL reduce не слушает (G/05).

## 2. Иллюстрация пустого состояния через Recraft V4.1 Vector (`VEC-ILLUSTR`)

### 2.1 Канал и цена (23.09.2026)

| Канал | Модель | Цена | Заметки |
|---|---|---|---|
| RouterAI `POST /api/v1/images` | `recraft/recraft-v4.1-vector` | 8,74 ₽ | SVG в `data[0].b64_json`, `usage.cost` в рублях; Pro — 32,79 ₽ (G-14, ценность 1) |
| RouterAI | `recraft/recraft-v4-styles-vector` | 5,46 ₽ + ≈ 0,55 ₽ за референс-стиль | стиль — `input_references` в каждом вызове (`style_id` витрина не возвращает) |
| Gen-API | `recraft-v4`, `"model": "vector"`, `"pro": false`, `"translate_input": false` | 20 ₽ | запас, если RouterAI режет `controls` (G-15); `pro` по умолчанию 1 = 75 ₽ |

[поправка фазы 5, 25.09.2026: паспорта RouterAI — V4.1 Vector 8,83 ₽, V4.1 Pro Vector 33,11 ₽, V4 Styles Vector 6,07 ₽, Styles Pro
Vector 13,80 ₽, V4.1 Flash (растр, черновик) 0,77 ₽; Styles по своей иконке переносят палитру и вес, но не состав набора (CM-03);
Gen-API-запас не понадобился → `04-capability-map.md` §2.4]

### 2.2 Запрос (формат задания фазы 5, `mp_client.py`)

```json
// routerai · recraft/recraft-v4.1-vector · 2026-09-23 · [не проверено: G-10; controls — гипотеза до B2-01]
{"channel": "routerai", "method": "POST", "path": "/api/v1/images",
 "body": {"model": "recraft/recraft-v4.1-vector", "aspect_ratio": "1:1", "n": 1, "output_format": "svg",
  "prompt": "Flat vector illustration for an empty shopping cart state on an e-commerce website: a single shopping cart with a small paper bag beside it. Simple rounded geometric shapes, flat color blocks, three colors plus white, centered composition with generous empty space, front view, plain light background. No text, no people, no gradients, no shadows, no texture. Palette: deep navy #0F172A for main shapes, teal #0D9488 accent, amber #F59E0B small highlights, background #F8FAFC."},
 "tag": "G-10-recraft-illustration", "max_rub": 10.6, "price_rub": 8.74}
```

Промт вектора — 6 пунктов по важности (D2 `05/05` §7): тип графики → логика формы → строгая палитра → дисциплина линии →
раскладка → запреты; без фактур и материалов; градиент и свечение векторная модель не делает (плоские заливки).
Исполнение: `python3 ../../scripts/ai-media/mp_client.py run 99-raw/phase5/jobs/G-10-recraft-illustration.routerai.json` (сухой прогон) →
`… --live` только в фазе 5 при заданном `ROUTERAI_BUDGET_TOTAL`.
[поправка фазы 5, 25.09.2026: G-10 не запускался — его заменил CM-01 (иконки 4 × 2, спот 4:3, фон 16:9 в парах Vector и Pro
Vector, 125,83 ₽): спот Pro — геометричнее (14 путей против 20), фон — лучше у Vector (Pro дал белый фон вместо заданного) →
`99-raw/phase5/runs/5-vector/analysis/illustrations/metrics.md`]

### 2.3 Чистка SVG

```bash
# svgo 4.1.0 · конфиг G/02 keep-signature — [проверено: G/02: −57…−65 %, p99 разницы растра ≤ 10 из 255]
# 1) фон-прямоугольник (первый путь во весь viewBox) — удалить ДО svgo; 2) корень: убрать preserveAspectRatio="none",
#    пиксельные width/height, style="display:block", оставить viewBox — скрипт 99-raw/experiments/G/02-recraft-svg-hygiene/process.py
99-raw/tools/node/node_modules/.bin/svgo in.svg -o out.svg \
   --config ../../scripts/ai-media/data/svgo.keep-signature.config.mjs
python3 ../../scripts/ai-media/provenance_check.py scan out.svg          # подпись <recraft-signature> на месте
python3 ../../scripts/ai-media/asset_audit.py audit out.svg --mode svg-icon --out audit_svg/   # фон, preserveAspectRatio, <image>, <text>, подпись
```

### 2.4 Доставка

- Иллюстрация 68–123 КБ после svgo → `<img src="empty-cart.svg" width height alt="" loading="lazy">` (кэш) или растр AVIF 320/640
  по s2 ≥ 70; inline — нет (у Linear 530 тыс. символов разметки).
- Размеры по ui-research 07/02: пустое состояние 120–240 px, онбординг 160–240, ошибка 240–320 (A `01/01` §2.12).
- Метки: иллюстрация — строка 3 L (сам; XMP в растровой производной; SVG-разметка — вне 50(2) `[спорно]`), подпись Recraft — сохранить.
- Серия иллюстраций — эталон G-10 → V4 Styles по нему (G-11) или блок стиля прозой (G-12); порог — VLM «одна серия» 4/5, ΔE заливок ≤ 5.

## 3. Паттерны и текстуры (`VEC-PATTERN`, `IMG-TEXTURE`)

### 3.1 Паттерн кодом

```css
/* CSS · плитка штриховки 166 байт, цвет из токена · [проверено: G/04, G/05 Chromium] */
.section-pattern { background-color: var(--brand);
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16'%3E%3Cpath d='M-2 2 2-2M0 16 16 0M14 18l4-4' stroke='%23000' stroke-width='2'/%3E%3C/svg%3E") repeat;
          mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16'%3E%3Cpath d='M-2 2 2-2M0 16 16 0M14 18l4-4' stroke='%23000' stroke-width='2'/%3E%3C/svg%3E") repeat; }
```

URL-кодирование (одинарные кавычки внутри, кодировать `%`, `#`, `<`, `>`) на 20–25 % короче base64; `background-image: url(data:…)`
переменные CSS не видит — цвет через `mask-image` + `background-color`; плотность фона секции — непрозрачность 0,05–0,2, шаг ≥ 12 px.

### 3.2 Текстура генерацией

| Материал | Как сделать тайл | Порог |
|---|---|---|
| органика (камень, шум, жаккард, мешковина с неровным плетением) | `tile_check.py cut in.png tile.png --overlap 96` (Efros–Freeman) | шов ≤ 1,3; 1,3–1,5 — смотреть 2×2; > 1,5 — чинить |
| регулярная сетка (ткань, плитка, кирпич) | SVG/CSS-паттерн кодом или заделка креста шва маской | разрез оставляет сдвиг фазы нитей |
| бесструктурный фон | смешивание со сдвинутой на 50 % копией | двоение −12 % ВЧ — только для «тумана» |

Генерация: `bytedance/seedream-4` 2K 1:1 3 ₽ (routing `IMG-TEXTURE`; H-09 проверяет, что «seamless» промтом не тайлится);
заделка маской — `qwen/image-2.1` (исследовательская лицензия весов: только черновики до решения L — финал регулярной сетки
делать кодом).

### 3.3 Проверка (демо: CC0 Poly Haven `hessian_230`, 2K)

```bash
# tile_check.py (H2) — [проверено: M/07 — цифры ниже]
python3 ../../scripts/ai-media/tile_check.py check tile.png            # seam_ratio (гор., верт.)
python3 ../../scripts/ai-media/tile_check.py cut crop.png tile.png --overlap 96
python3 ../../scripts/ai-media/tile_check.py preview tile.png preview.jpg   # сдвиг 50 % | плитка 2×2 — глазами
```

| Вход | Шов (гор. / верт.) | Вердикт |
|---|---|---|
| тайл Poly Haven целиком → 512 | 1,18 / 0,67 | SEAMLESS |
| вырез 1024 из середины («как ИИ-текстура») | 2,87 / 4,27 | SEAM |
| вырез → `cut --overlap 96` (928²) | 1,19 / 1,36 | BORDERLINE (у H на другом вырезе 1,40 / 1,15) |
| серый тайл 256 / 384 | 0,99 / 1,01 · 1,17 / 0,70 | SEAMLESS |

### 3.4 Вес: серый оверлей вместо цветной текстуры

| Тайл мешковины | AVIF | WebP | Бюджет A ≤ 30 КБ |
|---|---|---|---|
| цветной 384 | не достиг s2 70 к q60 | 49,6 КБ (q80, s2 74,0) | нет |
| цветной 512 | — | 67,3 КБ (q70) | нет |
| **серый 4:0:0 256** | **9,8 КБ** (q65, s2 72,7) | 17,1 КБ | да |
| серый 4:0:0 384 | 24,5 КБ (q65, s2 70,7) | 39,9 КБ | да (AVIF) |

```css
/* CTA демо: цвет — CSS, фактура — серый тайл поверх в multiply · [проверено: демо, page_accept PASS] */
.band { position: relative; isolation: isolate; background: #1F4D3A; }
.band::before { content: ""; position: absolute; inset: 0; z-index: -1; opacity: .5; mix-blend-mode: multiply;
  background-image: image-set(url("burlap-gray-256.avif") type("image/avif"), url("burlap-gray-256.webp") type("image/webp"));
  background-size: 256px 256px; }
```

```bash
# avifenc 1.4.2 — монохромный AVIF · [проверено]
avifenc -q 65 -s 6 -y 400 -j 4 tile_gray_256.png burlap-gray-256.avif
```

### 3.5 Зерно

SVG `feTurbulence` 280 байт (`../10-web-integration/pages/assets/svg/noise.svg`), 5–9 % `soft-light` поверх hero; шум, «впечённый»
в файл до сжатия, AVIF/WebP съедают и платите весом ×12 (H/05b); на AVIF-ступени бандинга шум 5 % не прячет (J/03).

## 4. OG-картинка с кириллицей (`IMG-TEXT-CYR` → шаблон)

### 4.1 Маршрут

Фон — кадр hero (кроп 40:21 из 16:9 теряет 6,7 % высоты: 1 − (16/9)/(40/21) `[поправка X2 24.09.2026: было 5,5 %]`) или отдельная генерация «место под текст слева 45 %» (`IMG-BG-ABSTRACT`/
`IMG-HERO-PHOTO`); текст — HTML-шаблоном (routing `IMG-TEXT-CYR` primary). Кириллица моделью — только если блок E-02…E-07 покажет
дословность у лидера (3 из 3 строк) и всегда с OCR (K) и вычиткой человеком; `IMG-TEXT-LATIN` — то же, декоративная надпись —
`openai/gpt-5.4-image-2` 1K 4 ₽ `[не проверено]`.

### 4.2 Шаблон (демо, `99-raw/experiments/M/06-og-marketplace/og-template.html`)

```html
<!-- OG 1200×630 · кириллица — HTML поверх кадра; ключевое внутри 1100×530 · [проверено: M/06 — JPEG q86 46,4 КБ] -->
<style>*{margin:0;box-sizing:border-box} html,body{width:1200px;height:630px}
body{position:relative;overflow:hidden;font-family:"Noto Sans",sans-serif;color:#1C1B18}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.s{position:absolute;inset:0;background:linear-gradient(90deg,rgb(244 239 230/.78) 0,rgb(244 239 230/.55) 44%,rgb(244 239 230/0) 66%)}
.c{position:absolute;left:78px;top:50px;bottom:50px;width:600px;display:flex;flex-direction:column;justify-content:center;gap:22px}
h1{font-family:"Noto Serif Display","Noto Serif",serif;font-weight:600;font-size:70px;line-height:1.02}</style>
<img class="bg" src="og_bg.png" alt=""><div class="s"></div>
<div class="c"><div class="k">Обжарочная · кофе в зёрнах</div><h1>Лесная обжарка</h1>
<p class="l">Кофе, который обжаривают раз в неделю — и привозят за два дня.</p></div>
```

### 4.3 Рендер

```python
# Playwright 1.63 (Chromium 153 CfT) · Pillow 11.3 — [проверено: M/06 render.py; J/05 make_og.py] · запускать под browser.lock
from playwright.sync_api import sync_playwright
from PIL import Image
import io, os
with sync_playwright() as p:
    b = p.chromium.launch(channel='chromium', headless=True)
    pg = b.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
    pg.goto('file://' + os.path.abspath('og-template.html')); pg.wait_for_timeout(600)
    png = pg.screenshot(); b.close()
im = Image.open(io.BytesIO(png)).convert('RGB')
for q in (86, 82, 78):                              # ≤ 300 КБ (A); у демо хватило q86 — 46,4 КБ
    im.save('og-1200x630.jpg', quality=q, optimize=True, progressive=True)
    if os.path.getsize('og-1200x630.jpg') <= 300 * 1024: break
```

- Шрифты: рендер берёт шрифты машины (у нас Noto Serif Display / Noto Sans с кириллицей); на сервере генерации OG — те же файлы
  шрифтов или `@font-face` локальными путями, иначе подмена на DejaVu и «другой бренд».
- Разметка: `og:image` абсолютным URL на проде, `og:image:width`, `:height`, `:alt`, `twitter:card summary_large_image`; не AVIF.
- Для шаблона на поток страниц (статьи, товары) — генерация по запросу (`/api/og`, как Linear) или сборкой; проверять битые адреса.

### 4.4 Проверка

```bash
# asset_audit.py --mode og · OCR RapidOCR 3.9.2 (venv-K) — берёт heavy.lock сам · [проверено]
python3 ../../scripts/ai-media/asset_audit.py audit og-1200x630.jpg --mode og --slot og --stage web \
   --expect "Лесная обжарка" --expect "ОБЖАРОЧНАЯ · КОФЕ В ЗЁРНАХ" --expect "Кофе, который обжаривают раз в" \
   --expect "неделю — и привозят за два дня." --expect "Демо-бренд · свежая обжарка по средам" --out audit_og/
```

Каждую строку шаблона — в `--expect` так, как она нарисована: с `text-transform: uppercase` — заглавными, каждая строка вёрстки
отдельно. У демо с 2 строками из 5: «лишний текст» + кластер M04 (тёплый белый) + M12 (текст в кадре) → `needs_human`; со всеми
5 строками — текст pass, CER 0 у каждой, итог `warn` (только тёплый белый, стиль бренда) `[проверено]`. Вычитка человеком на
200 % всё равно обязательна: OCR «исправляет» латиницу-близнеца (u вместо и ловится 1 раз из 15, K/01). Вёрстку OG — по DOM
до OCR: у демо текст в безопасной зоне 1100×530 (рамка строк 78–666 × 172–455 px), переполнений нет (`results_layout_og.json`).

## 5. Фавиконы (3 файла; 6 — для PWA)

```html
<!-- Evil Martians 2026 · [проверено: G/04; демо M/08] -->
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">          <!-- только PWA: 192, 512, maskable 512 -->
```

```xml
<!-- icon.svg демо: знак бренда, тёмная тема внутри SVG (работает и в <img>, G/05) · 469 байт · [проверено] -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><style>.p{fill:#1F4D3A}.b{fill:#C9A227}.c{stroke:#1F4D3A}
@media (prefers-color-scheme:dark){.p{fill:#C9A227}.b{fill:#1F4D3A}.c{stroke:#C9A227}}</style>
<circle class="p" cx="16" cy="16" r="16"/><g transform="rotate(-32 16 16)"><ellipse class="b" cx="16" cy="16" rx="6.4" ry="9.4"/>
<path class="c" d="M16 6.9c-2.6 3.1-2.6 6.2 0 9.1s2.6 6 0 9.1" fill="none" stroke-width="1.7" stroke-linecap="round"/></g></svg>
```

| Файл | Байт (демо) | Правило |
|---|---|---|
| `favicon.ico` 32×32 | 1 005 | один размер (16+32+48 — 3 485 Б без пользы, G/04); в корне сайта |
| `icon.svg` | 469 | `@media (prefers-color-scheme: dark)` внутри |
| `apple-touch-icon.png` 180 | 2 778 | цветной фон на весь квадрат, поле ≈ 20 px, без своего скругления |
| `icon-192.png` / `icon-512.png` | 3 011 / 8 101 | манифест |
| `icon-mask.png` 512 | 8 101 | рисунок внутри круга ⌀ 409,6 px (80 %): у знака демо r ≈ 151 ≤ 204,8 |

Рендер SVG → PNG — `node 99-raw/experiments/G/svg2png.mjs in.svg out.png <zoom>` (resvg-js 2.6.2), ICO — Pillow `save(sizes=[(32,32)])`
(`99-raw/experiments/M/08-svg-favicons/build.py`). Знак — из готового логотипа (только знак без надписи, проверка на 16 px);
растровый логотип — сначала potrace/vtracer. Логотип генерацией — «не делаю» (L строка 15). Метки: иконки и фавиконы — вне 50(2).

## 6. Инфографика карточки маркетплейса с кириллицей (шаблон)

### 6.1 Цепочка

Настоящий вырез товара (альфа фото/рендера; E `product_rgba.png`) → HTML-шаблон 900×1200 (3:4) — бренд, название, 3 преимущества с
иконками набора, подвал; фон — CSS-градиент бренда (или ИИ-фон без текста, строка 1 L) → **DOM-проверка вёрстки** → Playwright →
WebP по s2 ≥ 80 → **OCR слоя текста** (второй снимок с `.tin{visibility:hidden}`) → глаз по итоговой картинке.
Все цифры и факты — только текстом шаблона (строка 24 L: цены, характеристики, даты в пикселях модели — «нет»).

```bash
# M/06b layout_check.py (Playwright, DOM) + asset_audit OCR по слою текста · [проверено: M/06, 24.09.2026 06:05]
flock -w 900 99-raw/tools/.locks/browser.lock python3 ../../scripts/ai-media/layout_check.py   # before/after + textlayer.png
python3 ../../scripts/ai-media/asset_audit.py audit marketplace_textlayer.png --slot product --expect "ЛЕСНАЯ ОБЖАРКА" --expect "Кофе в зёрнах" \
   --expect "Арабика 100 % · 250 г" --expect "Обжарка раз в неделю" --expect "Средняя обжарка: орех и какао" \
   --expect "Доставка за 1–2 дня" --expect "Дата обжарки — на крышке каждой банки" --out audit_mp_textlayer/
```

Строку с переносом (`Обжарка раз` / `в неделю`) в `--expect` писать целиком: `asset_audit` выравнивает ожидаемое по склеенной
расшифровке всех строк, перенос не мешает (`fit_align`, CER 0).

### 6.2 Числа демо (`99-raw/experiments/M/06-og-marketplace/`)

| Что | Значение |
|---|---|
| рендер Playwright (Noto Serif Display + Noto Sans) | < 1 с на карточку (OG + карточка — 4 с с запуском браузера) |
| WebP 900×1200 | q85, s2 80,5, **48,8 КБ** (бюджет A ≤ 150 КБ) |
| превью 450×600 | 19,0 КБ |
| `layout_check` первой версии (05:12) | **fail**: «1–2 дня» — отдельный флекс-элемент, заходит на банку на 1 588 px², переполнение `li` 325 > 290 px и `span` 107 > 72 px; на картинке «Доставка   1–2 дн[я]» поверх этикетки, «за» — строкой ниже |
| OCR первой версии | «о Доставка 1-2 дн ЛЕСНАЯ ОБЖАРКА» (0,31) + «за» отдельно — OCR прочитал сломанную вёрстку честно; я сначала списал это на «склейку строк OCR» — ошибка разбора; заметил глазом на листе и на мастере, DOM-проверка подтвердила и измерила |
| `layout_check` исправленной (подпись — один `<span>`) | pass: пересечений с альфой банки 0, переполнений 0, nowrap-флекс 0 |
| OCR исправленной с банкой | «ИСНЯ ОБЖА» (0,40) на рамке 109–819 px: детектор склеил «Доставка за» с этикеткой на той же высоте → `omission`, `substitution`, needs_human |
| OCR слоя текста (банка скрыта) | **pass**: 7 из 7 строк, CER 0, точность слов 1,0, минимальный балл 0,94; итог `needs_human` только из-за угловой эвристики L |

### 6.3 Ловушки шаблона

- «Доставка за 1–2 дня» рвётся на тире («1–» / «2 дня») даже с `&nbsp;` перед числом → `<span style="white-space:nowrap">1–2 дня</span>`,
  **но только внутри элемента подписи**: во флекс-`li` (`display:flex; gap`) голый текст и nowrap-`span` становятся двумя
  флекс-элементами — между словами встаёт `gap`, `span` не сжимается и вылезает из колонки (у нас — на банку, в демо — разрыв
  «Доставка   1–2 дня» в полосе иконок). Правило: `<li><svg/><span>Доставка за <span class="nw">1–2&nbsp;дня</span></span></li>`
  + `li > span { min-width: 0 }`; проверка — `layout_check.py` (DOM), а не OCR.
- Карточка и её миниатюра на сайте — один файл со `srcset` (у демо дубль 450 + 900 стоил телефону лишние 19 КБ).
- Требования площадок (Ozon, Wildberries) к главному фото и доле текста — не собраны (A, открытый вопрос №5): инфографика —
  на дополнительных слайдах, главное фото — пакшот на белом `[не проверено]`.

### 6.4 Набор слайдов карточки (из практики Amazon, 12.2025)

Практик Amazon собирает набор слайдов одним чатом NB Pro: главное фото, 2–3 «в интерьере» (с человеком и без), фичи (подписанные
иконки со стрелками к частям товара), выгоды, инструкция по шагам, сравнение «мы / конкурент»; всего типов слайдов около 22
[V:12pQ0W2bCDE 16:18]. Рабочие слова для графики — «modern and clean style» и «mobile optimized» [V:12pQ0W2bCDE 22:24];
первый вариант фич без них — мелкий текст и «мультяшные» иконки [V:12pQ0W2bCDE 10:11] `[практика: один автор — мнение]`. Для
нас (кириллица, факты): слайды фич, выгод, инструкции и сравнения — **тем же HTML-шаблоном 3:4** с разными раскладками (текст —
шаблоном, строка 24 L; у NB Pro латиница в том ролике вышла без ошибок, кириллицу модели ломают — A `01/01` §2.11, IMG-M12,
замер — тесты E-02…E-07); товар — настоящим вырезом; «в интерьере» — рецепт PDP (`02` §2) с проверкой масштаба (`02` §3.1:
модель трижды увеличила товар). Сравнение с конкурентом — только своими фактами без чужих знаков (строка 18 L); «mobile
optimized» у нас — проверка шаблона на ширине превью карточки в выдаче (крупный кегль, ≤ 3 строк на слайд) `[мнение M; не
проверено]`.

## Частые ошибки

- Генерировать знакомую иконку (корзина, настройки) — у набора она лучше и бесплатна.
- Принимать новую метафору по `check_icons.py` без проверки узнаваемости — геометрия проходит, смысл нет (кофемолка, матрёшка → «8»).
- Recraft для линейных иконок UI; `fill → currentColor` у иконок Recraft (дырки цветом фона).
- svgo `preset-default` по SVG Recraft — удаляет подпись провенанса (нарушение условий).
- Inline-вставка иллюстрации 100 КБ в HTML каждой страницы.
- «Seamless tileable» в промте как гарантия тайла; зеркальная плитка 2×2 для узнаваемой фактуры («Роршах»).
- Цветная ВЧ-текстура в бюджет 30 КБ — только серый оверлей 4:0:0 + цвет CSS.
- OG в AVIF; OG без `width/height/alt`; OG 8 МБ (Lightship); кириллица в OG, нарисованная моделью.
- Фавиконы «20 файлов из генератора»; ICO с тремя размерами; apple-touch с прозрачностью (iOS заливает чёрным).
- Цифры и характеристики в пикселях инфографики, нарисованные моделью.
- Проверять вёрстку шаблона только OCR: OCR читает и сломанную вёрстку, а склейку строк с этикеткой товара легко принять за
  особенность OCR (так было у нас) — сначала DOM (`layout_check.py`), потом OCR по слою текста.
- **Ошибки агентов**: `recraft-v4` в Gen-API без `"pro": false` (75 ₽ вместо 20); `translate_input` по умолчанию 1 у `recraft-v4`
  (переведёт надписи); палитра Recraft `controls` через RouterAI как «работает» (гипотеза до B2-01); внешний спрайт `<use href>` в
  странице, открытой файлом (не работает в Chromium по `file://`); текст `text-transform: uppercase` в `--expect` строчными.

## Чек-лист

- [ ] Иконка есть в наборе продукта? Если нет — LLM по шаблону G, `check_icons.py` без fail, лист 16/24/48 светлый/тёмный?
- [ ] Новая метафора проверена на узнаваемость (VLM без подсказки или человек за 5 с) и стоит с подписью?
- [ ] SVG Recraft: фон удалён до svgo, корень поправлен, svgo `keep-signature`, подпись на месте (`provenance_check scan`)?
- [ ] Иллюстрация > 40 КБ — через `<img>` или AVIF, не inline?
- [ ] Паттерн кодом с продлёнными штрихами; текстура — шов ≤ 1,3 (`tile_check`), серый 4:0:0 для оверлея?
- [ ] OG: HTML-шаблон, 1200×630, ключевое в 1100×530, JPEG ≤ 300 КБ, все строки в `--expect`, вычитка человеком?
- [ ] Фавиконы: ICO 32, SVG с тёмной темой, apple-touch 180 с фоном; PWA — манифест и maskable в круге 80 %?
- [ ] Инфографика: товар — настоящий вырез, факты — текстом, диапазоны `nowrap` внутри подписи, `layout_check` pass (0 пересечений
  с альфой товара, 0 переполнений), WebP ≤ 150 КБ, OCR слоя текста — все строки в `--expect`, CER 0?

## Открытые вопросы и противоречия

1. Узнаваемость новых метафор (кофемолка) — VLM G-06 против человека; порог «узнано ≥ 4 из 6» у G — на контрольном листе.
2. Палитра Recraft через RouterAI (`provider.options.recraft.controls`) — ответ даст B2-01 (0 ₽ при 400); до него — словами.
3. Требования Ozon/Wildberries к инфографике и главному фото — не собраны; нужен отдельный быстрый обзор правил площадок (L/M).
4. Шаблон OG на сервере: какие шрифты с кириллицей доступны рендеру в проде (у нас — системные Noto на этой машине).
5. `asset_audit --mode og` без списка строк считает всё «лишним текстом» — предложение K: режим «текст шаблона» с одним
   `--template-html`, откуда берутся ожидаемые строки.
6. SVG-разметка иллюстрации — «исходный код» вне 50(2) или ИИ-выход с меткой — `[спорно]` (L).

## Источники

- [S1] G `../07-vector-svg-icons/01-svg-by-llm.md` — набор против LLM, шаблон, `check_icons.py`, узнаваемость.
- [S2] G `../07-vector-svg-icons/02-vector-generators-and-tracing.md` — Recraft, каналы, чистка SVG, векторизация.
- [S3] G `../07-vector-svg-icons/03-icon-sets-and-patterns.md` §4–§5 — паттерны кодом, фавиконы (Evil Martians 2026).
- [S4] H `../08-image-post-processing/03-color-tiling-depth-layers.md` §2–§3 — тайлинг, метрика шва, бандинг.
- [S5] J `../10-web-integration/01-images-delivery.md` §7, `03-…` §4.3, `pages/08` — OG, зерно, SVG на странице.
- [S6] K `../11-evaluation-qa/01-metrics-and-asset-audit.md` §3.7–§4 — SVG-проверки, OCR кириллицы.
- [S7] B2 `../02-providers-platforms/07-multichannel-client.md` §1–§3 — RouterAI, Gen-API, `mp_client.py`.
- [S8] L `../12-legal-provenance/04-agent-policy.md` §2 строки 2, 3, 15, 24; `02` §4 — подпись Recraft, иконки вне 50(2).
- [S9] A `../01-web-assets-landscape/01-asset-slots-by-page-type.md` §2.7, §2.8, §2.11 — OG, фавиконы, маркетплейс.
- [S10] E `99-raw/phase5/E-plan.md` — блок кириллицы E-02…E-07; G `G-plan.md` — G-01…G-18; B2 `B2-plan.md` — зонды.
- [S11] Лицензии: `lucide-static` 1.47.0 — ISC; Poly Haven — CC0 (polyhaven.com/license, через H/05 и F/01).
- [S12] Транскрипт без дайджеста `91-videos/transcripts/12pQ0W2bCDE.md` (Chris Rawlings, NB Pro, 10.12.2025) — набор слайдов
  карточки товара (§6.4) `[практика; один автор]`.
- Опыты M: `06-og-marketplace`, `07-texture`, `08-svg-favicons`, `09-demo-acceptance`; опыты соседей: G/01–G/05, H/05, J/05.
