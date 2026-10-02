# Композиция под веб: место под текст, контраст поверх фото, фокус и кадрирование

Волна 2 · агент F (продолжатель F2) · 23.09.2026 · опора: выжимка помощника `99-raw/notes/wave2/F-src-composition.md`
(≈ 30 источников: smartcrop.js, Twitter arXiv 2105.08667, Cloudflare Images, imgix, Cloudinary, Thumbor, W3C CSS Images 3,
MDN, web.dev, WCAG 2.2 (1.4.3, G18, F83, ACT afw4f7), WebAIM, APCA, NN/g ×9, IBM, Uber, Material, Polaris, Atlassian,
GOV.UK), A `01/01` §4, §6 · опыты `99-raw/experiments/F/02-text-zone` (64 комбинации + проверка F83), `F/03-crop-focal`
(Chromium 5/5), `F/04-slop-metrics` · доставка на страницу — J (`../10-web-integration/`), приёмка — K (`../11-evaluation-qa/`).

## Выжимка для агента

1. **Место под текст закладывать в кадр при генерации**: зона 35–45 % hero, слева; спокойная поверхность (небо, ровная стена,
   газон, вода) с плотностью краёв ≤ 0,06 → §1 `[проверено: F/02; практика: A 01/01 §6, Uber, IBM]`.
2. **Блок композиции работает против «среднего вида»** (объект в правой трети, срез краем, 45 % пустой стены, ≤ 3 предмета) —
   F-04 проверяет его метриками F/04 → §1.2 `[не проверено генерацией]` [поправка фазы 5, 25.09.2026: F-04 — блок работает в 3 из 3
   кадров GPT Image 2.5 Sunburst 1K: центр масс x 0,81–0,85 (порог ≥ 0,62), края в зоне 0,0006–0,0064 (≤ 0,06), пестрота 25–31;
   голый бриф — 0,30–0,39 и 51–53 («средний сток») → `99-raw/phase5/runs/2.5-stand/audit-F-04/audit.json`; зону под заголовок из брифа держат
   и другие модели: 4 из 4 новых фото-моделей RouterAI (CM-09, края 0,0004–0,0199) и 9 из 12 сцен витрины разных жанров (VAR, края
   0,0000–0,0339; нет — ночной город с дождём и лес 0,0693–0,0873), 1 образец на сцену → `99-raw/phase5/runs/S5-analysis/VAR_zone.json`]
3. **Без подложки HTML-текст на документальном фото почти не проходит**: практично (p5 под буквами) 14 из 64, белый текст
   0 из 32; строго по F83 (каждый пиксель под буквой) — 6 из 64 → §2.1 `[проверено]`.
4. **Контраст не мерить средней яркостью зоны**: 31 «проходит», из них 25 нарушают F83 → §2.2 `[проверено]`.
5. **p95 зоны не годится ни для «нужен ли скрим», ни для альфы скрима**: против F83 — 2 ложных пропуска и 3 лишних скрима из
   64; скрим по p95 оставляет нечитаемыми 14 из 64 и проходит F83 строго лишь в 15 → §2.2 `[проверено]`.
6. **Позиция F (решение противоречия)**: соответствие — по WCAG F83 (худший участок фона, затем каждая буква); альфу скрима
   считать по p99,9 полосы или зоны, затем проверять F83; не прошло — поднять альфу до значения p100 (медиана +0,02, на бликах
   до +0,2–0,36) или сдвинуть текст → §2.3 `[проверено: F/02 f83_check]`.
7. **Цвет текста — по зоне**: светлый или тёмный, какой требует меньше скрима; медиана альфы 0,46 → 0,21, в 5 из 32 зон скрим
   не нужен → §2.4 `[проверено]`.
8. **Ровная плашка α ≈ 0,5 = «серая коробка»**: порядок — спокойная зона в композиции → цвет текста по зоне → градиентный
   скрим только под полосой текста → §2.5 `[проверено глазом]`.
9. **Скрим с числами**: тёмный 20–40 %, светлый 40–60 %, градиент длиной ≥ 3 высоты шапки, середина на 3/10 к тёмному концу,
   точечно, без «over-scrim» (Material); плашка 30 % не дала и 3:1 на облаках, 50 % — прошла (NN/g) → §2.5 `[практика]`.
10. **Финальная проверка — на странице**: реальный шрифт, переносы, все брейкпоинты, тёмная тема (J/K); до вёрстки — только
    приближение по зоне или полосе → §2.6.
11. **Фокус задаёт автор, а не детектор**: `composition.focal_point {x, y}` + `safe_zones[].keep_rect` в спецификации;
    автокроп Twitter давал перекосы 2–8 % от паритета групп и argmax-сдвиги → §3.1 `[исследование]`.
12. **Две семантики фокусной точки**: CSS `object-position` и Cloudflare `gravity=XxY` — процентное выравнивание; imgix и
    Thumbor — центрирование с прижатием к краю; путаница сдвигает объект на десятки процентов → §3.2 `[документация, код]`.
13. **`object-position` для фокуса в боксе `cover`**: `s = max(bw/iw, bh/ih)`, `px = (fx·iw·s − tx·bw) / (iw·s − bw)` с
    обрезкой в [0; 1]; Chromium 5/5, ошибка ≤ 0,002 ширины бокса → §3.2 `[проверено]`.
14. **Арифметика кадра**: из мастера 16:9 остаётся 3:2 — 84 % ширины, 4:3 — 75 %, 1:1 — 56 %, 4:5 — 45 %, 9:16 — 31,6 % →
    §3.3 `[проверено]`.
15. **Безопасная полоса**: при фокусе 0,68 во всех {16:9, 4:5, 1:1, 9:16} видна только x 0,52–0,84 — зона текста слева
    телефон не переживает → §3.3 `[проверено]`.
16. **Телефону — свой кадр 4:5–9:16** (так у 8 из 10 лидеров) через `<picture><source media … width height>` → §3.4
    `[практика: A 01/02 §9; документация: MDN, web.dev]`.
17. **Главный объект — в центральных 60 %, мастер с запасом 10–15 % по краям**; smartcrop штрафует внешние 20 % каждой
    стороны → §3.3 `[практика A; код smartcrop]`.
18. **Не резать, если можно не резать**: Twitter заменил автокроп показом целиком; автор smartcrop советует dont-crop →
    §3.5 `[исследование, практика]`.
19. **Внимание смещено влево**: 80 % фиксаций на левой половине экрана 1920 px → текст слева, объект справа (LTR и кириллица)
    → §1.1 `[исследование: NN/g]`.
20. **Декоративные картинки — колонкой, по верхнему краю текста**; зигзаг из декоративных картинок работает как препятствия
    для взгляда; картинки с текстом рядом с текстом блока спорят с ним → §4 `[исследование: NN/g]`.
21. **OG 1200 × 630**: ключевое — внутри 1100 × 530 → §3.3 `[практика: A 01/01 §6]`.
22. **Текст поверх «занятого» фона не чинится цветом текста**: автор APCA — «not put text over such a busy background, not
    ever»; IBM и Uber не ставят UI и текст поверх фото и паттернов → §2.5 `[мнение; практика]`.

## 1. Место под текст

### 1.1. Где и сколько

- Hero: зона текста 35–45 % кадра, контраст в самом слабом месте (A `01/01` §6); мастер с запасом 10–15 % по краям.
- Сторона: внимание смещено влево — > 120 участников, > 130 000 фиксаций, монитор 1920 × 1080: **80 %** фиксаций на левой
  половине (в 2010 на 1024 × 768 — 69 %), пик ≈ 600 px от левого края [S13]. «Priority content should be front and center…
  Keep secondary content to the right» [S13] → заголовок слева, объект в правой трети (для LTR, в том числе кириллицы).
- Нижняя часть кадра удобна для «floor fade» — затемнения под подписью [S10].
- Бренды: Uber — «Include negative space around the subject to allow for the placement of additional design elements such
  as typography»; «Simplify the scene rather than overusing shallow depth of field» [S16]; IBM — деление кадра «divisions of
  two» по 2x Grid, «Avoid having no center of interest and drawing attention to an empty center» [S15] `[практика]`.

### 1.2. Как просить модель

```text
// openai/gpt-image-2.5-sunburst · polza 2026-09-23 · 1K, 16:9 · [не проверено; = F-04 B]
Photograph for a website hero, 16:9: a ceramic coffee cup on a wooden table by a window in the morning.
Composition: the cup sits in the right third of the frame and is partly cut off by the right edge; the left 45 percent of the
frame is an empty, evenly lit, low-contrast plaster wall - clean negative space for a headline. Camera slightly above table
height, 35mm lens; not symmetrical, not centred, not a studio product shot. At most three objects: the cup, a folded linen
napkin, a few crumbs. Soft window light from the right, natural colour, fine film grain.
No people. No text. No watermark.
```

[поправка фазы 5, 25.09.2026: этот промт — дословно F-04 B, 3 из 3 кадров прошли судью композиции; предупреждение
`QA-COLOR-WARM` у всех трёх (тёплый сдвиг GPT 2.5 — грейдом); формулировки зоны «google» / «copy space» у Z-Image выигрыша не
дали (D2-04: +5,3 [0; +10,6] и +2,2 п. п.), «copy space» дал самую шумную зону → `99-raw/phase5/runs/2.5-stand/F-04_A-vs-B_sheet.jpg`]

- Шаблоны вендоров: Google — «A minimalist composition featuring a single [subject] positioned in the [bottom-right] of the
  frame. The background is a vast, empty [color] canvas, creating significant negative space» [S19]; D — «The left 40 percent
  of the frame is an empty, uncluttered warm-grey plaster wall, evenly lit and low in contrast, creating clean negative space
  for a headline» (`../05-prompting/03-asset-spec-and-dialects.md`). A/B формулировок — у D2 (`../05-prompting/06-ab-protocol.md`).
- Поверхность зоны называть предметом без артикля в спецификации («evenly lit lawn», «plain plaster wall») — шаблон компилятора
  добавляет «an empty, uncluttered» (`01-visual-dna-from-ui.md` §9) `[проверено]`.
- Для моделей без негативов «no people» → «no one in the frame» (там же, §4.3).

### 1.3. Как проверить до вёрстки

```bash
# text_zone.py (Python 3.13, numpy, Pillow 11.3) — [проверено]
python3 ../../scripts/ai-media/text_zone.py hero.png 0 0 0.4 1 "#ffffff"
# → mean / p95 / worst контраст, перцентили яркости, edge_density, scrim_alpha_4.5_p95 (для p99,9 — scrim_alpha(q=99.9))
python3 ../../scripts/ai-media/composition_metrics.py hero.png   # centroid_x, empty_share, zone_edge, blobs
```

Плотность краёв (доля пикселей с перепадом перцептивной яркости > 0,10): небо и ровные стены 0,001–0,06; листва, трава,
архитектура 0,16–0,52 `[проверено]`. Зона ≤ 0,06 — годна под текст; > 0,15 — только плашка или другой кадр.

## 2. Контраст текста поверх фото

### 2.1. Без подложки

64 комбинации (8 CC0-фото × 4 зоны × белый и тёмный текст), «истина» — фон под настоящими буквами (DejaVu Sans Bold,
маска раздута на 2 px) `[проверено]`:

| Истина | Проходит 4,5:1 без скрима |
|---|---|
| практичная: p5 контраста под буквами | 14 из 64 (белый текст — 0 из 32) |
| строгая, WCAG F83 шаг 2: каждый пиксель под буквой | **6 из 64** |

### 2.2. Чем предсказывать: среднее, p95, худший пиксель

| Предсказатель по всей зоне (порог 4,5) | «Проходит» | К F83: ложный пропуск | К F83: лишний скрим | К практичной: ложный / лишний |
|---|---|---|---|---|
| средняя яркость | 31 | **25** | 0 | 17 / 0 |
| p95 (тёмный текст — p5) | 5 | **2** | 3 | 0 / 9 |
| худший пиксель (WCAG F83 Quickcheck) | 0 | 0 | 6 | 0 / 14 |

**Почему p95 ошибается в обе стороны.** Перцентиль всей зоны не знает, где буквы. Самые яркие 5 % пикселей зоны — просветы неба
между облаками, белый фасад, блик на воде — часто лежат ровно на строке заголовка: p95 их выбрасывает → 2 ложных «проходит»
(буквы на просвете не читаются). И наоборот, яркое пятно в стороне от строки p95 учитывает → 3 лишних скрима там, где под
буквами всё хорошо. Средняя яркость хуже: светлая строка на тёмной зоне «проходит» в 25 случаях из 31, где F83 нарушен.

### 2.3. Решение противоречия: F83 для соответствия, p99,9 для альфы

WCAG не даёт метода для фото: «WCAG does not provide any guidance on how to measure their contrast… testing the area where
contrast is lowest» (WebAIM) [S8]; ACT-правило afw4f7 проверяет лучшую пару пикселей и прямо предупреждает: «Passing this
rule does not mean that the text has sufficient color contrast» [S6]. Нормативная опора — F83: «Quickcheck: …the contrast
between the text and the area of the image that is darkest (for dark text) or lightest (for light text)… If the Quickcheck
is false, then check to see if the background behind each letter has sufficient contrast with the letter» [S6] `[документация]`.
A предлагал p95 (`01/01` §6), первый отчёт F — p99–p99,9. Проверка F83 после скрима, рассчитанного по квантилю
(`f83_check.py`) `[проверено]`:

| Скрим по | Альфа медиана / p90 | p5 под буквами ≥ 4,5 | F83 шаг 2 (каждая буква) | F83 Quickcheck по полосе |
|---|---|---|---|---|
| p95 зоны | 0,38 / 0,52 | 50/64 | 15/64 | 9/64 |
| p99 зоны | 0,43 / 0,52 | 63/64 | 25/64 | 19/64 |
| p99,9 зоны | 0,46 / 0,53 | 64/64 | 45/64 | 39/64 |
| **p100 зоны (худший пиксель)** | **0,48 / 0,53** | 64/64 | **64/64** | **64/64** |
| p99,9 полосы текста (рамка глифов + 8 px) | 0,43 / 0,52 | 64/64 | 24/64 | 8/64 |
| p100 полосы | 0,46 / 0,53 | 64/64 | 64/64 | 64/64 |

**Позиция F** `[проверено; позиция базы]`:
1. **Соответствие стандарту — по F83**: после скрима контраст текста с самым светлым (для светлого текста) участком фона за
   строкой ≥ 4,5:1 (3:1 для крупного); не прошло — фон за каждой буквой. p95 и среднее для соответствия не использовать.
2. **Альфу скрима считать по p99,9** полосы текста или зоны — это устойчиво к одиночным пикселям (шум JPEG, блик), — затем
   проверять F83. Не прошло (19 из 64 для зоны) — поднять альфу до значения p100: медиана +0,02, p90 +0,09, на бликах до
   +0,2 (зона) и +0,36 (полоса). Где добавка > 0,1 — дешевле сдвинуть строку, сменить цвет текста или взять другой кадр.
3. Полоса текста экономит альфу (0,43 против 0,46 по p99,9), но только если строка на странице стоит там, где её считали.

### 2.4. Цвет текста по зоне

Если выбирать светлый или тёмный текст по зоне — какой требует меньше скрима, — медиана альфы падает с 0,38–0,44 до **0,21**;
без скрима обходятся 5 из 32 зон `[проверено]`. NN/g: «consider both the text color and the main color of the image.
Light-colored or faded backgrounds are not well-suited to white text» [S10]. В паспорте — `post.scrim.color` (тёмная нейтраль
бренда, `01-visual-dna-from-ui.md` §7.3).

### 2.5. Форма подложки

- Ровная плашка α 0,48–0,53 даёт 4,7–4,9:1, но выглядит «серой коробкой» (`99-raw/experiments/F/02-text-zone/contact_scrim.jpg`)
  — страховка, не приём `[проверено глазом]`.
- Material 1: «Dark scrims should ideally be between 20%-40% opacity… Light scrims should ideally range from 40%-60%»;
  градиент «long, 3x standard app bar height, with the centerpoint about 3/10 towards the darker side»; «target specific areas
  for text protection instead of blanketing the entire image»; «Don't 'over-scrim' large images» [S17] `[практика Google, M1]`.
  На фото F/02 нужная альфа выше (медиана 0,46): Material писал для контролируемых кадров — отсюда правило «сначала
  композиция».
- NN/g: радиальное затемнение (Spire), размытие под текстом + тёмный текст (Compliments), плашка REI 30 % → 50 %: при 30 %
  заголовок на облаках не давал даже 3:1 [S10]; проверять на **худшем** кадре серии и худшем положении текста [S10].
- G18: затемнить фон за буквами, «thin black outline (at least one pixel wide)», ореол вокруг текста — ореол считается фоном
  [S7]; ACT: `text-shadow: 0 0 2px black` у `#ccc` на фото даёт 5–13:1 [S6].
- Автор APCA о «занятом» фоне (полосатая рубашка): «The APCA guidance is to not put text over such a busy background, not
  ever» [S9] `[мнение автора метода]`; IBM hybrid UI «should not be positioned over photography, busy patterns» [S15].

```css
/* скрим под строку слева: альфа из f83-проверки (здесь 0.55), цвет — тёмная нейтраль паспорта; [не проверено в вёрстке — J] */
.hero__media::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(to right,
    rgb(42 37 32 / .55) 0%, rgb(42 37 32 / .55) 38%,   /* полная альфа на всю ширину колонки текста */
    rgb(42 37 32 / .38) 46%, rgb(42 37 32 / 0) 62%);    /* спад в сторону объекта, без резкой границы */
}
```

### 2.6. Пороги и где проверять

- WCAG 2.2 SC 1.4.3 (AA): 4,5:1; крупный текст (≥ 18 pt ≈ 24 px или ≥ 14 pt жирный ≈ 18,5 px) — 3:1; AAA 7:1 / 4,5:1; 4,499 —
  провал [S5]. APCA (кандидат WCAG 3): Lc 75 — минимум колонок текста, Lc 60 — прочий текст, Lc 45 — заголовки ≥ 36 px или
  24 px жирным, Lc 90 — максимум для очень крупного жирного [S9]; для фото метода нет.
- До вёрстки (генерация, приёмка ассета): зона или полоса по `text_zone.py`, альфа по p99,9 + F83 по полосе.
- На странице (J/K): реальный шрифт, кегль, переносы на каждом брейкпоинте, тёмная тема, скриншот и проверка фона под каждой
  буквой — шаг 2 F83 без этого не выполним: геометрия букв зависит от шрифта и ширины окна.

## 3. Фокус и кадрирование

### 3.1. Фокус задаёт автор

Twitter 2018–2021: модель значимости (DeepGaze II, дистилляция) → одна точка argmax → кроп по ней; отклонения от
демографического паритета — 8 % (мужчины и женщины), 4 % (чёрные и белые), 7 % (чёрные и белые женщины), 2 % (мужчины);
на групповых кадрах argmax систематически отдаёт кадр одному человеку; в мае 2021 кроп стандартных соотношений заменён показом
целиком: «how to crop an image is a decision best made by people» [S1] `[исследование]`. Рекомендация авторов: «Solutions that
preserve the creator's intended focal point without requiring the user to tediously define a crop for each aspect ratio for
each photo are desirable»; «focal point selection… One action of user participation is enough to define cropping on multiple
aspect ratios» [S1]. У генерации автор известен — фокус пишет спецификация: `composition.focal_point {x, y}` и
`safe_zones[{ratio, keep_rect}]` (`../05-prompting/asset-spec.schema.json`).

### 3.2. Две семантики точки и формула `object-position`

| Семантика | Кто | Где окажется точка f | Формула левого края кропа |
|---|---|---|---|
| процентное выравнивание | CSS `object-position: X% Y%`, Cloudflare `gravity=XxY`, текст документации Thumbor | на той же относительной позиции, что в исходнике (всегда видна) | `left = f·(W − cw)` |
| центрирование с прижатием | imgix `crop=focalpoint`, код Thumbor, Twitter | в центре кропа, если хватает запаса | `left = clamp(f·W − cw/2, 0, W − cw)` |

Семантика CSS — по спецификации: «With a value pair of 75% 50%, the point 75% across and 50% down the image is to be placed at
the point 75% across and 50% down the area» (CSS Backgrounds 3), для `object-position` — «concrete object size as the object
area and the content box as the positioning area» (CSS Images 3 §4.6) [S3]. Строка определений «Percentages: refer to width
and height of element itself» вводит в заблуждение — рабочая формула выше [S3].

```js
// object-position, чтобы фокус (fx, fy) встал в точку (tx, ty) бокса при object-fit: cover — [проверено: F/03, Chromium 5/5]
function objectPosition(fx, fy, iw, ih, bw, bh, tx = 0.5, ty = 0.5) {
  const s = Math.max(bw / iw, bh / ih), ox = iw * s - bw, oy = ih * s - bh;
  const clamp = v => Math.min(Math.max(v, 0), 1);
  const px = ox < 1e-9 ? 0.5 : clamp((fx * iw * s - tx * bw) / ox);
  const py = oy < 1e-9 ? 0.5 : clamp((fy * ih * s - ty * bh) / oy);
  return `${(px * 100).toFixed(2)}% ${(py * 100).toFixed(2)}%`;
}
// мастер 2560×1440, фокус (0.68, 0.55): бокс 412×699 → "76.93% 50.00%", 412×515 → "82.73%", 600×600 → "91.14%"
```

Проверка в Chromium: метка встала в ожидаемую точку с ошибкой ≤ 0,002 ширины бокса; `object-position: 50% 50%` по умолчанию
держит центр, а не фокус: для фокуса 0,68 в боксе 9:16 объект уезжает за край (0,68 → 1,07); при нехватке запаса (бокс 1440 ×
900 из 16:9) обрезка даёт 100 % и фокус встаёт на 0,644 ширины — это ожидаемо `[проверено]`. Формула считается на каждом
размере бокса (JS или `@container`), готовый код доставки — J.

### 3.3. Арифметика кадрирования

| Из мастера 16:9 в … | 21:9 | 3:2 | 4:3 | 1:1 | 4:5 | 2:3 | 9:16 |
|---|---|---|---|---|---|---|---|
| доля ширины | 1,0 (высоты 0,762) | 0,844 | 0,75 | 0,562 | 0,45 | 0,375 | **0,316** |

`[проверено: F/03 crop_math.py]`. Из мастера 4:5 в 16:9 остаётся 0,45 высоты.

- **Безопасная полоса**: фокус x = 0,68 в мастере 16:9 → во всех кадрах {16:9, 4:5, 1:1, 9:16} видна только полоса
  **x 0,52–0,84** (32 % ширины); зона текста 0–0,40 в 9:16 не видна вовсе → телефону свой кадр или своя зона текста
  `[проверено]`. Объект, который обязан пережить 9:16 из 16:9, — в полосе шириной ≤ 31 % вокруг фокуса.
- **Центральные 60 %**: правило A совпадает с кодом smartcrop — штраф начинается во внешних 20 % каждой стороны кропа
  (`edgeRadius 0.4`, `edgeWeight −20`), всё за кропом весит −0,5; деталь на пересечении третей весит 4,39 против 1,41 в
  центре (×3,1) [S2] `[код, расчёт]`.
- OG 1200 × 630: ключевое внутри 1100 × 530 (A `01/01` §6); соотношения по слотам — A `01/01` §4.1 (hero 16:9–16:10 / 4:5 /
  9:16; сплит 4:3–3:2; баннер 3:1–4,6:1; галерея 1:1 / 4:5; OG 1,91:1). IBM держит ритм только 16:9, 4:3, 3:2, 2:1, 1:1 [S15].

### 3.4. Телефонный кадр

MDN: «art direction problem» — на телефоне человек в широком кадре становится крошечным, «better to show a smaller, portrait
image on mobile, which zooms in on the person»; `media` — только для арт-дирекшна, без `sizes` с условиями; подмена JS не
годится — браузер начинает грузить картинки до разбора CSS и JS [S4]. web.dev: «the `picture` element gives commands»;
`width` и `height` у каждого `<source>`; `alt` один на все кадры — описывать и полный, и обрезанный [S4]. У 8 из 10 лидеров
на телефоне отдельный hero-кадр 4:5–9:16 (A `01/02` §9). imgix держит одну точку на все размеры и растит зум: 2048 × 900 без
зума → 940 × 360 ×1,5 → 640 × 420 ×1,75 → 300 × 300 ×2,5 [S12]. Семейство форматов из одного кадра с продуктом (1:1 → 10
соотношений) практики делают аутпейнтом с защитой: «product must be pixel perfect, never regenerated» — композит оригинала
и пиксельная проверка [V:AxV8TR3BdqI 26:40–30:46]; процедура — H (`edit_check.py outpaint --composite`,
`../08-image-post-processing/`).

```html
<!-- телефонный кадр — отдельный мастер 4:5 (паспорт: composition.phone_frame = separate-master); [не проверено в вёрстке — J] -->
<picture>
  <source media="(max-width: 699px)" srcset="hero-4x5-800.avif 800w, hero-4x5-1200.avif 1200w" width="1200" height="1500">
  <img src="hero-16x9-1600.avif" srcset="hero-16x9-1600.avif 1600w, hero-16x9-2400.avif 2400w" sizes="100vw"
       width="2400" height="1350" alt="Деревянная скамейка под берёзой в осеннем парке" fetchpriority="high"
       style="object-fit: cover; object-position: 76.93% 50%">
</picture>
```

### 3.5. Автокроп: когда и чем

| Система | Сигнал | Числа по умолчанию |
|---|---|---|
| smartcrop.js 2.0.5 (MIT, 12 957 ★, код 01.2024) | края + «кожа» + насыщенность + boost; центр-вес, штраф краёв, трети | веса 0,2 / 1,8 / 0,1 / 100; анализ на 256 px; ошибка весов яркости («weights blue ~7x higher») не исправлена [S2] |
| Twitter 2018–2021 | значимость, одна точка argmax | почти симметричный кадр → центр; отменён для стандартных соотношений [S1] |
| Thumbor 7.8.0 | лица (HAAR) → углы; центр масс | окно центрируется и прижимается к краю (код; документация описывает иначе) [S12] |
| Cloudinary `g_auto` | «subject» (DL) + «classic»; лица приоритетны | правило третей по умолчанию (`thirds_0` выключает); `custom_coordinates` переопределяют [S12] |
| imgix `crop=auto` | люди, транспорт, животные; лица весомее | цепочка отката `crop=car,vehicle,entropy`; `fp-x/fp-y/fp-z` [S12] |
| Cloudflare `gravity=auto` | «saliency algorithm» | `face` + `zoom` 0–1 [S12] |

Автокроп уместен для галерей и миниатюр без замысла автора; опасен на людях, группах, кадрах с текстом или номерами («a number on
a sports jersey» перетягивает значимость) [S1]. Для сгенерированных ассетов — фокус из спецификации. Лучший кроп — его
отсутствие: показ целиком (Twitter), дополнение фона вместо кропа (dont-crop; imgix `fit=fill&fill=blur`; CSS `object-fit:
contain` вместо Cloudflare `fit=pad`) [S1][S2][S12]. Проверка до публикации: imgix `fp-debug`, Cloudinary `fl_getinfo`,
Thumbor `/meta` [S12].

## 4. Картинки в раскладке страницы

- «The first images in the list set the tone and make users decide whether to ignore the rest»; «Align decorative imagery down
  the page»; «Top-align text with decorative images»; «Always position high-information content on the left side of the first
  row»; «Don't use imagery for the sake of the layout» [S14] `[исследование: NN/g, ~30–35 участников на вариант]`.
- Декоративные картинки в зигзаге — «obstacles for the eye»; хуже всего, когда в картинках есть текст рядом с текстом блока
  [S14] → в генерации — «clean, text-free surfaces» (IMG-M12).
- Люди смотрят информативные картинки (продукт, реальные люди) и пропускают «big feel-good images that are purely decorative»;
  фото реальных сотрудников рассматривают на 10 % дольше биографий при площади на 316 % меньше [S11] `[исследование]`.

## 5. Поля спецификации

```json
{"composition": {"shot": "medium", "subject_region": "right-third", "angle": "eye-level",
  "focal_point": {"x": 0.68, "y": 0.55},
  "text_zone": {"side": "left", "rect": [0, 0, 0.4, 1], "surface": "evenly lit lawn", "tone": "even, low contrast",
                "purpose": "headline", "text_color_on_top": "#FFFFFF"},
  "safe_zones": [{"ratio": "4:5", "keep_rect": [0.52, 0.1, 0.84, 0.95]}, {"ratio": "9:16", "keep_rect": [0.55, 0.15, 0.84, 0.95]}]},
 "output": {"primary_ratio": "16:9", "variants": [{"ratio": "4:5", "strategy": "generate", "subject_region": "bottom",
            "text_zone": {"side": "top", "rect": [0, 0, 1, 0.35], "purpose": "headline"}}]}}
```

Фрагмент проходит `asset-spec.schema.json` v0.2 `[проверено: встроенный валидатор vlm_to_dna.py]`. Паспорт задаёт умолчания
(`composition.text_zone_default`, `phone_frame`: `separate-master` = `strategy: generate`, `crop`, `outpaint`; `master_ratio`),
спецификация — значения ассета;
`vlm_to_dna.py to-spec` переносит зону текста в прямоугольник (`01-visual-dna-from-ui.md` §2.1). Фокус обязан лежать внутри
каждого `keep_rect` (проверяет компилятор D2).

## Частые ошибки

- Мерить контраст по средней яркости зоны или по p95 — 25 и 2 ложных «проходит» против F83 из 64.
- Ровная полупрозрачная плашка на весь кадр вместо спокойной зоны в композиции и градиента под строкой.
- Белый текст по умолчанию: на документальных фото он без подложки не прошёл ни разу (0 из 32).
- `object-position: center` для кадра с фокусом не в центре; путаница семантики imgix и CSS.
- Один мастер 16:9 на телефон «с кропом»: зона текста слева исчезает, объект в 9:16 теряет 68 % ширины.
- Автокроп значимостью на людях и группах.
- **Ошибки нейросетей-агентов**: читать строку «Percentages: refer to width and height of element itself» как формулу
  `object-position`; считать ACT afw4f7 (лучшая пара пикселей) достаточным условием; округлять 4,499 до 4,5; ставить
  `sizes` с условиями вместе с `media`; просить в промте «text on the left» вместо пустой поверхности под HTML-текст.

## Чек-лист

- [ ] Зона текста заложена в кадр: сторона, доля 35–45 %, поверхность, плотность краёв ≤ 0,06?
- [ ] Цвет текста выбран по зоне?
- [ ] Альфа скрима посчитана по p99,9, после скрима F83 пройден (худший участок, затем каждая буква)?
- [ ] Скрим — градиент под строкой, а не плашка на весь кадр?
- [ ] Фокус `{x, y}` и `keep_rect` по соотношениям записаны в спецификации?
- [ ] `object-position` посчитан на каждый размер бокса?
- [ ] Телефонный кадр — отдельный мастер 4:5–9:16 или своя зона текста?
- [ ] Главный объект внутри центральных 60 % и безопасной полосы всех соотношений?
- [ ] Финальная проверка контраста — на странице, на всех брейкпоинтах и в тёмной теме (J/K)?

## Открытые вопросы и противоречия

- **Решено здесь**: F83 (худший участок) — для соответствия; p99,9 — для альфы с последующей проверкой F83; p95 (A) — ни
  то, ни другое (§2.2–§2.3). Поправку к A `01/01` §6 («метрика K: 95-й перцентиль») вносит аудитор X; K берёт F83 + p99,9.
- «Истина» F/02 — геометрия под глифами одного шрифта (DejaVu Sans Bold) и кегля, не чтение людьми; APCA не считался.
- F83 шаг 2 требует положения букв — до вёрстки это приближение полосой; на странице — скриншот (J/K).
- Числа Material (20–60 %) и NN/g (30 → 50 %) — кейсы; на документальных фото F/02 медианная альфа 0,46 выше «тёмного
  скрима» Material.
- Документация Thumbor описывает процентное выравнивание, код — центрирование: верить коду [S12].
- smartcrop: ошибка весов яркости открыта с 2018 года (issue #77), PR 2026 не принят.

## Источники

- [S1] Yee, Tantipongpipat, Mishra (Twitter META), «Image Cropping on Twitter: Fairness Metrics…», arXiv 2105.08667 v2 (09.09.2021) + блоги Twitter Engineering 2018 и 2021 (архив) + `crop_api.py` (255 ★) — автокроп, перекосы, отказ; высокая надёжность по фактам о системе.
- [S2] J. Wagner, smartcrop.js v2.0.5 (MIT, 12 957 ★, последний коммит кода 23.01.2024), https://github.com/jwagner/smartcrop.js — веса, штраф краёв, трети; «magic fuzz factors» по словам автора.
- [S3] W3C CSS Images 3 §4.5–4.6, CSS Backgrounds 3 (percentage); MDN object-position, object-fit, background-position (изм. 20–24.04.2026) — семантика процентов.
- [S4] MDN «Responsive images» (изм. 06.11.2025), `<picture>` (изм. 24.04.2026); web.dev «The picture element», https://web.dev/learn/design/picture-element — арт-дирекшн, width/height у source.
- [S5] W3C, Understanding WCAG 2.2 SC 1.4.3, https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html — пороги.
- [S6] W3C, WCAG 2.2 Technique F83, https://www.w3.org/WAI/WCAG22/Techniques/failures/F83 ; ACT rule afw4f7, https://www.w3.org/WAI/standards-guidelines/act/rules/afw4f7/ — худший участок, каждая буква; ACT как необходимое условие.
- [S7] W3C, WCAG 2.2 Technique G18, https://www.w3.org/WAI/WCAG22/Techniques/general/G18 — затенение, обводка, ореол.
- [S8] WebAIM, «Contrast and Color Accessibility», https://webaim.org/articles/contrast/ — «testing the area where contrast is lowest».
- [S9] APCA (Myndex/SAPC-APCA, 586 ★, push 25.07.2026), ARC Bronze Simple Mode; A. Somers «Busy Background Breaks Bulletin» (2022, прочитано начало) — пороги Lc, мнение о занятом фоне.
- [S10] NN/g, A. Harley «Text Over Images» (18.10.2015, пересмотр 13.01.2026), https://www.nngroup.com/articles/text-over-images/ — приёмы, кейс REI 30 → 50 %.
- [S11] NN/g, J. Nielsen «Photos as Web Content» (2010, пересмотр 13.08.2026), https://www.nngroup.com/articles/photos-as-web-content/ — информативные против декоративных.
- [S12] Cloudflare Images transform-via-url; imgix focal point crop и учебник; Cloudinary automatic gravity и custom focus areas (обновл. 19.06–21.07.2026); Thumbor 7.8.0 документация и `transformer.py` (10 519 ★) — фокус и автокроп в CDN.
- [S13] NN/g, T. Fessenden «Horizontal Attention Leans Left» (2017), https://www.nngroup.com/articles/horizontal-attention-leans-left/ — 80 % фиксаций слева.
- [S14] NN/g, K. Flaherty «Zigzag Image–Text Layouts Make Scanning Less Efficient» (2017), https://www.nngroup.com/articles/zigzag-page-layout/ — раскладка картинок.
- [S15] IBM Design Language — Photography, Illustration (исходники MDX, push 20.09.2026) — 2x Grid, соотношения, «not over photography».
- [S16] Uber Brand Guide 2019 (архив) — негативное пространство под типографику.
- [S17] Google Material Design 1 «Imagery» (не поддерживается), https://m1.material.io/style/imagery.html — скримы с числами.
- [S18] GOV.UK «Images» content guidance — декоративные против информативных, картинки без текста.
- [S19] Google, Gemini API image generation (23.09.2026) — шаблон «negative space».
- Опыты: `99-raw/experiments/F/02-text-zone` (+ `f83_check.py`, `f83_check.json`), `F/03-crop-focal`, `F/04-slop-metrics`; A `01/01` §4, §6, `01/02` §9.
