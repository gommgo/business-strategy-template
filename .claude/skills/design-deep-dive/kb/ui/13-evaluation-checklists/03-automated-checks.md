# Автоматические проверки визуального слоя

Волна 3 · агент I · 22 сентября 2026 · инструментов разобрано по исходникам и документации: 15

Что можно проверить машиной, какими инструментами, с какими порогами и чего эти инструменты **не умеют**.
Главный вывод вперёд: ни один готовый инструмент не проверяет то, ради чего собрана эта база (шкалы,
кратность, высоты, радиусы, принадлежность токенам), поэтому для этого написан собственный прогон.

## Выжимка для агента

1. **`../../scripts/ui/ui_audit.py` — один прогон на всё**: измерение страницы + сверка с пресетом или набором
   токенов + отчёт «правило → найдено → порог → вердикт» в Markdown и JSON. 14 групп, 81 проверка в каталоге, 55–66 на прогон на
   прогон. → §1
2. **axe-core не проверяет 1.4.11, 1.4.10, 2.4.11 и 2.4.13.** Правил с такими тегами в нём нет вовсе.
   Контраст границ, иконок и фокус-индикаторов не проверяется ни одним публичным линтером. → §2.1
3. **`target-size` и `color-contrast-enhanced` в axe выключены по умолчанию** (`"enabled": false`).
   Lighthouse включает `target-size` явно. → §2.1, §2.3
4. **Любой градиент или фоновая картинка под текстом переводит проверку контраста в `incomplete`**, а не в
   `fail`. То же делают перекрытие элементом, псевдоэлемент крупнее 25 % площади, соотношение ровно 1:1,
   один символ текста и текст только из эмодзи. → §2.1
5. **axe сравнивает строго больше порога** (`contrast > expected`) и **усекает вниз** до двух знаков:
   4.499 становится 4.49. Округлять контраст нельзя: 4.47 не равно 4.5. → §2.1
6. **Крупный текст в axe — 18 pt = 24 CSS px** обычного веса и **14 pt = 18.667 CSS px** полужирного
   (`boldValue: 700`). → §2.1
7. **APCA даёт не отношение, а Lc со знаком.** Пороги: Lc 90 body предпочтительно, 75 минимум для колонок
   текста, 60 прочий читаемый текст, 45 крупный и заголовки, 30 плейсхолдер и disabled, 15 порог
   видимости. Порядок аргументов важен: текст первым, фон вторым. → §2.4
8. **colorjs.io считает шесть алгоритмов**: `WCAG21`, `APCA`, `Michelson`, `weber`, `Lstar`, `DeltaPhi`.
   В `APCA` порядок обратный: `background.contrast(text, "APCA")`. → §2.5
9. **Playwright эмулирует `color_scheme`, `reduced_motion`, `forced_colors` и `contrast`** на уровне
   контекста; в Python API **нет `to_have_screenshot`** — визуальная регрессия эксклюзив JS-раннера. → §3.2
10. **В Python `page.screenshot` по умолчанию `animations="allow"`**, тогда как в `toHaveScreenshot` —
    `"disabled"`. Для стабильных кадров ставить явно. → §3.2
11. **Пороги визуальной регрессии по умолчанию**: Playwright `threshold 0.2` (YIQ), Chromatic
    `diffThreshold 0.063`, Percy `widths [375, 1280]` и `min-height 1024`. → §5
12. **`stylelint-declaration-strict-value`** (id `scale-unlimited/declaration-strict-value`) — единственный
    способ удержать шкалу в проекте, где часть кода пишет генератор. Дефолты: `ignoreVariables: true`,
    `ignoreFunctions: true`, `expandShorthand` и `recurseLonghand` выключены. → §4.1
13. **`eslint-plugin-tailwindcss`: правило `no-arbitrary-value` по умолчанию выключено**, включать явно.
    Автофикса у него нет. → §4.2
14. **Figma Design Lint проверяет только одно: привязан ли слой к стилю.** Ни контраста, ни размеров целей,
    ни сетки. Дефолтные радиусы `[0, 2, 4, 8, 16, 24, 32]`. → §6
15. **Lighthouse удалил аудит `font-size` в 13.0.0 и заменил `tap-targets` на `target-size`.** Старые числа
    (12 px / 40 % текста, 48 × 48 px) больше не проверяются. → §2.3

---

## 1. Собственный прогон: `ui_audit.py`

### 1.1 Что делает

Запускает Chromium через Playwright, снимает `getComputedStyle` и геометрию всех видимых узлов, считает
эффективный фон каждого элемента с композитингом полупрозрачных слоёв, сверяет значения с пресетом или с
набором токенов DTCG и печатает отчёт.

```bash
python3 ../../scripts/ui/ui_audit.py ПУТЬ_ИЛИ_URL \
  --preset admin|consumer \
  --tokens dist/tokens.json \
  --scheme light|dark|both \
  --reduced-motion --hover --tab 24 --touch \
  --viewport 1440x900 --viewport 1280x800 \
  --out ./audit --fail-on serious
```

`--selftest` проверяет парсеры (`box-shadow`, длительности, кратность, зазоры) и контрольные точки
контраста без браузера: 14 утверждений.

### 1.2 Группы проверок

| Код | Группа | Что проверяет |
|---|---|---|
| A | Отступы | доля из шкалы, кратность 5, уникальные `gap`, дробные, внешний padding ≥ внутренних зазоров |
| B | Размеры | уникальные высоты, ряд высот, одна высота на ряд, квадратность иконочных кнопок, размеры иконок, один набор иконок, высоты строк |
| C | Форма | уникальные радиусы, радиусы вне шкалы, вложенный радиус, толщины границ, радиус ≤ 25 % стороны |
| D | Глубина | уникальные тени, источник света, `backdrop-filter`, свечения, доля блоков с тенью, вложенность теней |
| E | Слои | `z-index` вне шкалы и выше 1500 |
| F | Цели | цели < 24 (44 на тач) без зазора, общее число мелких целей |
| G | Фокус | наличие индикатора на каждой остановке Tab, толщина, обрезка, контраст кольца |
| H | Типографика | кегли, веса, `line-height`, интерлиньяж тела, ширина абзаца, `lang`, регистр, `justify`, `tabular-nums`, русские нормы |
| I | Цвет | контраст текста, контраст границы поля, число цветов, семейство нейтрали, коридор disabled, цвета вне набора токенов, тёмная тема |
| J | Раскладка | ширина формы, сайдбар, контентная область, прилипшие полосы, горизонтальная прокрутка, жёсткие сетки, центрирование, шапка страницы |
| K | Движение | `transition: all`, длительности вне шкалы, доля 300 ms |
| M | Сокращённое движение | сокращаются ли длительности, выключаются ли циклы |
| S | Состояния | наличие hover, ΔL в коридоре, элементы под оверлеем |
| L | Антислоп | эмодзи, «почти, но не совсем», литералы в inline-стилях, крупные градиенты, число гарнитур |

### 1.3 Устройство, которое стоит повторить

1. **Эффективный фон считается обходом предков с композитингом.** Иначе контраст текста на полупрозрачной
   подложке считается неверно. Элементы, у которых фон получен композитингом, помечаются и выводятся из
   проверки «цвета вне набора токенов»: результат наложения — вычисляемое значение, а не токен.
2. **Фокус проверяется обходом Tab с двумя снимками.** Сначала снимаются «спокойные» стили всех
   фокусируемых элементов, затем при каждом Tab читается активный элемент и сравнивается со своим же
   спокойным состоянием. Это ловит и `outline`, и `box-shadow`, и смену границы — у **7 продуктов из 24**
   кольцо фокуса сделано `box-shadow`, и проверка только по `outline-width` их пропустит.
3. **Обрезка кольца считается геометрией**, а не фактом `overflow: hidden` у предка: прямоугольник
   элемента расширяется на `outline-width + outline-offset` и сравнивается с прямоугольником обрезающего
   предка. Иначе флагом помечается любая кнопка в прокручиваемой таблице.
4. **Контраст кольца при положительном `outline-offset` считается к фону вокруг элемента**, а не к самому
   элементу. Иначе синее кольцо на синей кнопке всегда даёт 1.00, и проверка бесполезна.
5. **Hover снимается только с видимых в окне и не перекрытых элементов.** Проверка попадания — через
   `document.elementFromPoint`. Иначе у страницы с открытой модалкой «нет hover» у всего под скримом.
6. **ΔL hover не считается, если в покое фон прозрачный** (ghost-кнопка): иначе получается «ΔL 96.8 п.п.».
   В тёмной теме потолок коридора поднят с 8 до 12 п.п.: шаг между поверхностями там больше.

### 1.4 Ложные срабатывания, которые пришлось убрать

Важнее самих проверок: без этих поправок отчёт не читается.

| Что | Почему поправлено |
|---|---|
| «Почти, но не совсем» | 11 и 12 px, 6 и 8 px — соседние ступени шкалы, а не дефект. Проверка срабатывает, только если хотя бы одно значение вне шкалы |
| Цель < 24 × 24 | SC 2.5.8 разрешает недоразмерную цель при зазоре и выводит из-под нормы инлайновые ссылки. Блокер — только нарушение правила кругов |
| Квадратность | требуется от иконочной кнопки, но не от переключателя 36 × 20 и чекбокса |
| Вложенный радиус | полностью круглые элементы (аватар, пилюля, переключатель) — отдельный класс |
| Высота контрола | `textarea` многострочна, в правило «одна высота на ряд» не входит |
| Иконка против пиктограммы | в ряд 12/14/16/20/24 входит только `svg` до 32 px; крупнее — пиктограмма или иллюстрация |
| Внешний padding ≥ зазоров | правило относится к зазорам уровня раскладки (≥ 12 px), а не к иконка–текст 8 px |
| Прилипшая полоса | это полоса: ширина > 40 % окна и высота ≤ 25 % окна. Иначе в сумму попадает скрим модалки на весь экран |
| Семейство нейтрали | считается по цветам текста и границ: статусные подложки `#dcfce7`, `#ffe2e2` тоже низкохроматичны |
| Отключённые элементы | выведены из 1.4.3 (WCAG их не нормирует) и проверяются по коридору APCA Lc 30–60 |

### 1.5 Чего не ловит

Иерархия, осмысленность метрик на дашборде, повторяемость KPI между страницами, «ложное дно», семантическая
правильность применения токена (`bg-subtle` там, где нужен `bg-component` — значение из набора, правило
нарушено), вкус. Кросс-доменные iframe и `canvas` не разбираются. Контраст текста на градиенте и на
картинке помечается как недостоверный.

---

## 2. Контраст и доступность

### 2.1 axe-core 4.13

Правила, относящиеся к визуальному слою (дословные id, impact, теги):

| Rule ID | Impact | Теги | По умолчанию |
|---|---|---|---|
| `color-contrast` | Serious | `cat.color, wcag2aa, wcag143, ACT` | включено |
| `color-contrast-enhanced` | Serious | `cat.color, wcag2aaa, wcag146, ACT` | **выключено** |
| `link-in-text-block` | Serious | `cat.color, wcag2a, wcag141` | включено |
| `target-size` | Serious | `cat.sensory-and-visual-cues, wcag22aa, wcag258` | **выключено** |
| `meta-viewport` | Moderate | `cat.sensory-and-visual-cues, wcag2aa, wcag144, ACT` | включено |
| `avoid-inline-spacing` | Serious | `cat.structure, wcag21aa, wcag1412, ACT` | включено |
| `p-as-heading` | Serious | `cat.semantics, wcag2a, wcag131, experimental` | экспериментальное |
| `css-orientation-lock` | Serious | `cat.structure, wcag134, wcag21aa, experimental` | экспериментальное |
| `scrollable-region-focusable` | Serious | `cat.keyboard, wcag2a, wcag211` | включено |
| `label-title-only` | Serious | `cat.forms, best-practice` | best-practice |

Правил с `cat.color` ровно **три**, с `cat.sensory-and-visual-cues` — **три**.

**Пороги (дословно из `lib/checks/color/color-contrast.json`):**

```json
"options": { "ignoreUnicode": true, "ignoreLength": false, "ignorePseudo": false,
  "boldValue": 700, "boldTextPt": 14, "largeTextPt": 18,
  "contrastRatio": { "normal": { "expected": 4.5 }, "large": { "expected": 3 } },
  "pseudoSizeThreshold": 0.25, "shadowOutlineEmMax": 0.2, "textStrokeEmMin": 0.03 }
```

Для AAA: `normal.expected 7` с `minThreshold 4.5`, `large.expected 4.5` с `minThreshold 3`,
`shadowOutlineEmMax 0.1`.

Механика, которую надо знать:

- `ptSize = Math.ceil(fontSize * 72) / 96`; `isSmallFont = (bold && ptSize < 14) || (!bold && ptSize < 18)`.
  То есть **крупный текст = 24 CSS px обычного и 18.667 CSS px полужирного**.
- Сравнение **строгое**: `contrast > expected`. Ровно 4.5 не проходит.
- Результат **усекается вниз**: `Math.floor(contrast * 100) / 100`.
- `target-size`: `minSize: 24`, `minOffset: 24`; цель больше 240 px сразу проходит; цель **не в tab order**
  понижается с провала до `incomplete`; полностью перекрытая цель считается **пройденной**.
- `link-in-text-block`: порог **3:1** между цветом ссылки и цветом окружающего текста; блочные ссылки
  (`display: block|flex|grid|table|inline-block`) пропускаются.

**Чего axe не умеет.** Ключи `incomplete`: `bgImage`, `bgGradient`, `imgNode`, `bgOverlap`, `fgAlpha`,
`elmPartiallyObscured`, `elmPartiallyObscuring`, `outsideViewport`, `equalRatio`, `shortTextContent`,
`emptyValue`, `nonBmp`, `pseudoContent`, `colorParse`, `complexTextShadows`, `hidden`.

- Любой `background-image` или градиент под текстом → `incomplete`.
- Элемент из `IMG, CANVAS, OBJECT, IFRAME, VIDEO, SVG` в стеке фона → `incomplete`.
- Псевдоэлемент площадью > 25 % бокса у элемента или любого предка → `incomplete`.
- Соотношение ровно 1:1 → `incomplete`.
- Один символ текста или только эмодзи → `incomplete`.
- Не проверяются вовсе: `<option>`, `input[type=hidden|range|color|checkbox|radio|image]`, отключённые и
  инертные элементы и их подписи, элементы без прямых текстовых узлов, `font-size: 0`, шрифтовые иконки.
- Официально: «Axe does not test hidden regions, such as inactive menus or modal windows».

**Пробел в покрытии, важный для этой базы:** ноль правил с тегами `wcag1411` (контраст нетекстовых
элементов), `wcag1410` (reflow), `wcag2411` и `wcag2413` (фокус). **Контраст границ полей, иконок и
фокус-колец axe не проверяет.** Поэтому проверки Ц5, Ц6, К8 и А1 из чек-листа закрываются только
`ui_audit.py` или глазами.

Производительность: правило `color-contrast` смотрит почти каждый элемент и считает перекрытия; документация
рекомендует гонять его на нескольких репрезентативных страницах, а не на всех.

### 2.2 Pa11y 10

Требует Node ≥ 22.13. Движки: `htmlcs` (HTML_CodeSniffer, по умолчанию) и `axe`; можно оба сразу.

Дефолты: `standard: "WCAG2AA"`, `runners: ["htmlcs"]`, `threshold: 0`, `level: "error"`,
`includeNotices: false`, `includeWarnings: false`, `timeout: 30000`, `wait: 0`,
`viewport: { width: 1280, height: 1024 }`, `reporter: "cli"`.

Коды возврата: 0 — ок, 1 — техническая ошибка, 2 — есть проблемы. `--threshold N` пропускает до N−1 ошибок.

`pa11y-ci` добавляет `concurrency: 1`, `useIncognitoBrowserContext: true`, работу по sitemap.

Actions позволяют довести страницу до нужного состояния перед проверкой: `click element <sel>`,
`set field <sel> to <value>`, `wait for element <sel> to be <state>`, `screen capture <path.png>`.

Собственных визуальных проверок у Pa11y нет: он обёртка над axe и HTML_CodeSniffer.

### 2.3 Lighthouse 13.5

Оценка доступности — **взвешенное среднее бинарных аудитов**; веса по оценке пользовательского воздействия
из axe. Частичного зачёта нет.

Веса, относящиеся к визуальному слою: `color-contrast` **7**, `link-in-text-block` **7**,
**`target-size` 7**, `meta-viewport` **10**, `image-alt` **10**. Шкала весов: 10 / 7 / 3 / 1 / 0.

Внутри Lighthouse axe запускается так:

```js
axe.run(document, {
  runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] },
  resultTypes: ['violations', 'inapplicable'],
  rules: { 'link-in-text-block': {enabled: true}, 'meta-viewport': {enabled: true},
           'target-size': {enabled: true}, 'heading-order': {enabled: true}, … }
});
```

**Что изменилось и устарело:**

- **`seo/tap-targets` удалён** и заменён на `accessibility/target-size` (Lighthouse 12). Старые числа
  (цель < 48 × 48 px и ≥ 25 % перекрытия в радиусе 48 px) больше не проверяются.
- **`font-size` (legible font sizes) полностью удалён в Lighthouse 13.0.0** (2025-10-10). Старый порог:
  провал, если **40 % и больше** текста мельче **12 px**; цель — «≥ 12 px на ≥ 60 % текста». Эти числа
  остаются полезным ориентиром, но автоматически не проверяются.
- **CLS** живёт в категории Performance с весом **25**. Пороги: «хорошо» ≤ **0.1**, «плохо» > **0.25**,
  измеряется на 75-м перцентиле. Это единственная визуальная метрика стабильности в стандартном наборе.

### 2.4 APCA

Пакет `apca-w3` 0.1.9, алгоритм 0.0.98G-4g. Возвращает **Lc со знаком**: положительный — тёмное на
светлом, отрицательный — светлое на тёмном. Диапазон примерно −108 … +106.

```js
import { APCAcontrast, sRGBtoY, alphaBlend, fontLookupAPCA } from 'apca-w3';
APCAcontrast(txYs, bgYs)   // первый аргумент — ТЕКСТ, второй — ФОН
fontLookupAPCA(Lc)         // -> ['LcValue', размер для веса 100, …, 900]
```

Пороги (дословные минимумы из «APCA in a Nutshell»):

| Lc | Что можно |
|---|---|
| **90** | предпочтительно для body: 18 px/300, 14 px/400; не-body от 12 px/400. Это же **рекомендуемый максимум** для текста крупнее 36 px bold и для больших плашек |
| **75** | минимум для колонок body: 24 px/300, 18 px/400, 16 px/500, 14 px/700 |
| **60** | минимум для читаемого не-body текста: 36 px/300, 24 px/400, 18 px/600, 16 px/700 |
| **45** | минимум для крупного текста (36 px обычного или 24 px bold), заголовков, тонких контурных иконок |
| **30** | абсолютный минимум «spot readable»: плейсхолдер, disabled, копирайт; сплошные иконки не тоньше 5.5 px |
| **15** | порог видимости для несемантичного нетекста; ниже считать невидимым |

Эквивалент AAA — **+ Lc 15** ко всем значениям. Размеры предполагают отношение x-height 0.52; Times New
Roman (0.45) требует +16 %.

**bridge-PCA** — отдельный пакет, сохраняющий обратную совместимость с WCAG 2: «Lc 60 always exceeds WCAG
3:1, Lc 75 always exceeds 4.5:1, Lc 90 always exceeds 7:1». Ограничение: альфа парсится, но **не
вычисляется** — цвета считаются непрозрачными.

Собственная реализация APCA в `../../scripts/lib/color.py` проверена на контрольных точках:
`apca(#000,#fff) = 106.0`, `apca(#fff,#000) = −107.9`, `apca(#888,#fff) = 63.1`.

### 2.5 colorjs.io

```js
color1.contrast(color2, "WCAG21" | "APCA" | "Michelson" | "weber" | "Lstar" | "DeltaPhi")
```

Без указания алгоритма метод **бросает `TypeError`**.

| Алгоритм | Формула | Особенности |
|---|---|---|
| `WCAG21` | `(Y_max + 0.05) / (Y_min + 0.05)` | только sRGB; порядок цветов не важен; до 21 |
| `APCA` | версия 0.0.98G-4g | **порядок важен**: `background.contrast(text, "APCA")`; белое на чёрном −110 |
| `weber` | `(Y_max − Y_min) / Y_min` | обрезается на 50 000 |
| `Michelson` | `(Y_max − Y_min) / (Y_max + Y_min)` | 0…1 |
| `Lstar` | `L*_max − L*_min` | разница **30 единиц L\*** достаточна для читаемости (Zuffi); это же разница Tone в Material HCT |
| `DeltaPhi` | `((L_bg^φ − L_txt^φ) · √2) − 40`, при < 7.5 обнуляется | 0…101, полярно-нечувствительный |

Большинство методов дают 0 для цвета на самом себе (WCAG 2.1 даёт 1) и ~100 для максимального контраста
(WCAG 2.1 даёт 21).

---

## 3. Аудит computed styles

### 3.1 Что снимать

Минимальный набор на элемент: `padding*`, `margin*`, `rowGap`, `columnGap`, `border*Radius`,
`border*Width`, `border*Color`, `boxShadow`, `zIndex`, `backdropFilter`, `fontSize`, `lineHeight`,
`fontWeight`, `letterSpacing`, `fontFamily`, `fontVariantNumeric`, `textTransform`, `textAlign`, `color`,
`backgroundColor`, `backgroundImage`, `outline*`, `transitionProperty`, `transitionDuration`,
`animationName`, `position`, `overflow`, `maxWidth`, `gridTemplateColumns`, `display`, плюс
`getBoundingClientRect()` и признак «есть собственный текстовый узел».

Три производных, которые надо считать в странице, а не потом:

1. **Эффективный фон** — обход предков с композитингом альфы.
2. **Родитель** — индекс ближайшего предка среди собранных узлов (нужен для вложенных радиусов, теней,
   строк таблиц).
3. **Попадание в элемент** — `document.elementFromPoint` для проверок hover.

### 3.2 Эмуляция режимов в Playwright

Python, точные имена и дефолты:

```python
browser.new_context(
    color_scheme="light" | "dark" | "no-preference" | "null",   # по умолчанию "light"
    reduced_motion="reduce" | "no-preference" | "null",         # по умолчанию "no-preference"
    forced_colors="active" | "none" | "null",                   # по умолчанию "none"
    contrast="no-preference" | "more" | "null",                 # по умолчанию "no-preference"
    viewport={"width": 1440, "height": 900},
    device_scale_factor=1, has_touch=False, is_mobile=False,
)
page.emulate_media(color_scheme="dark")      # с 1.9
page.emulate_media(reduced_motion="reduce")  # с 1.12
page.emulate_media(forced_colors="active")   # с 1.15
page.emulate_media(contrast="more")          # с 1.51
```

`page.screenshot` в Python: **`animations="allow"` по умолчанию** (в отличие от `toHaveScreenshot`, где
`"disabled"`), `caret="hide"`, `full_page=False`, `scale="css"`, `mask_color="#FF00FF"`.

**В Python API нет `to_have_screenshot`.** `PageAssertions` содержит только `to_have_title`, `to_have_url`,
`to_match_aria_snapshot`. Для визуальной регрессии на Python нужен `page.screenshot()` плюс сторонний
сравниватель.

### 3.3 Что проверять на каждом режиме

| Режим | Что искать |
|---|---|
| `color_scheme="dark"` | контраст на каждой поверхности, полярность кольца тени, направление hover, отсутствие чистого белого текста, совпадение геометрии со светлой темой |
| `reduced_motion="reduce"` | сокращение длительностей без обнуления, исчезновение `translate`/`scale`, выключение циклических анимаций, `scroll-behavior: auto` |
| `forced_colors="active"` | видимость фокуса (там `box-shadow` принудительно `none`), различимость selected, наличие границ у элементов, которые различались только фоном |
| `contrast="more"` | подхватывается ли высококонтрастная тема, если она объявлена |
| `has_touch=True, 390x844` | цели ≥ 44, кегль полей ≥ 16, hover-зависимые действия, сайдбар в оверлее |

---

## 4. Линтеры

### 4.1 Stylelint

**`scale-unlimited/declaration-strict-value`** (плагин `stylelint-declaration-strict-value` 1.12.1) —
требует, чтобы значение было переменной или функцией, а не литералом. Единственный способ удержать шкалу
там, где часть кода пишет генератор.

```json
{
  "plugins": ["stylelint-declaration-strict-value"],
  "rules": {
    "scale-unlimited/declaration-strict-value": [
      ["/^padding/", "/^margin/", "gap", "row-gap", "column-gap",
       "/^border-radius/", "box-shadow", "z-index", "border-width", "/color$/", "font-size"],
      { "ignoreValues": ["0", "auto", "inherit", "none", "initial", "1px", "100%"],
        "expandShorthand": true }
    ]
  }
}
```

Дефолты плагина: `ignoreVariables: true`, `ignoreFunctions: true`, `ignoreValues: null`;
`expandShorthand` и `recurseLonghand` **выключены**. Принимает как валидные `$sass`, `@less`,
`var(--x)`, `@value`, функции и унарный минус.

Ограничение `expandShorthand`, названное авторами: раскрытие «is not 100% standard conform» — нельзя
определить, какой longhand задан (`background: white` — это `background-color`? `text-decoration: none` —
это цвет или стиль?), динамические значения не резолвятся.

Автофикс **не автоматический**: нужно написать свой `autoFixFunc(node, validation, root, config)`.

**`declaration-property-value-allowed-list`** — фиксирует допустимые значения по свойству:

```json
{ "declaration-property-value-allowed-list": {
    "border-width": ["0", "1px", "2px"],
    "outline-width": ["2px", "3px"],
    "text-transform": ["none"],
    "text-align": ["left", "right", "center", "start", "end"] } }
```

Подводный камень: **регулярка матчится против целого значения декларации**. `"/^solid/"` не совпадёт с
`"10px solid red"`; нужно `"/\\bsolid\\b/"`. И `"/red/"` совпадёт с `"white url(/site/red.png)"`.

Смежные правила: `unit-allowed-list` (с `ignoreProperties` и `ignoreFunctions`),
`declaration-property-unit-allowed-list` (пустой массив = запретить любые единицы; опция
`ignore: ["inside-function"]`), `color-no-hex` (с `ignoreFunctions: ["var"]`), `color-named`,
`function-disallowed-list`.

### 4.2 eslint-plugin-tailwindcss 3.18

| Правило | Что делает | Автофикс |
|---|---|---|
| `classnames-order` | порядок классов по алгоритму `prettier-plugin-tailwindcss` | есть |
| `enforces-shorthand` | `mx-5 my-5` → `m-5` | есть |
| `no-contradicting-classname` | `p-2 p-3` | нет |
| `no-unnecessary-arbitrary-value` | `m-[1.25rem]` → `m-5` | есть |
| **`no-arbitrary-value`** | запрещает `p-[13px]`, `rounded-[7px]` | **нет**; правило **выключено по умолчанию** |
| `no-custom-classname` | только классы Tailwind плюс `whitelist` | нет |
| `enforces-negative-arbitrary-values` | `-top-[5px]` → `top-[-5px]` | есть |

Дефолты настроек: `callees: ["classnames", "clsx", "ctl", "cva", "tv"]`, `config: "tailwind.config.js"`,
`cssFiles: ["**/*.css", "!**/node_modules", …]`, `whitelist: []`, `classRegex: "^class(Name)?$"`.
`whitelist` — массив **регулярок**; приём с negative lookahead `["(?!(bg|text)\\-).*"]` разрешает любой
кастомный класс, но продолжает валидировать `bg-` и `text-`.

Именно в произвольные значения в квадратных скобках генератор сливает числа вне шкалы, поэтому
`no-arbitrary-value` надо включать явно.

### 4.3 Проверка токенов

- **Валидность формата**: `npx tz check tokens.json` (Terrazzo) или `ajv validate` по схеме 2025.10.
- **Все ссылки резолвятся, нет циклов, глубина ≤ 3**: обход графа.
- **Каждый примитив использован семантикой**: разность множеств.
- **У каждого семантического токена есть `usage` и `rules`**, метки из контролируемого словаря
  (`14-recipes/08-tokens-export.md` §4).
- **Пять грепов по компонентам**: литералы цвета, числовые утилиты Tailwind, примитивы в компонентах,
  `z-index` числом, размеры вне шкалы.

---

## 5. Визуальная регрессия

Числа сравнивают значения, скриншоты ловят композиционные дефекты: «карточка в карточке», двойные границы,
слипшиеся группы, обрезанное кольцо фокуса, прыжок соседей при подъёме карточки.

### 5.1 Playwright `toHaveScreenshot` (только JS-раннер)

Движок диффа — pixelmatch. Дефолты:

| Опция | Значение |
|---|---|
| `threshold` | **0.2** — «acceptable perceived color difference in the YIQ color space», 0 строго … 1 мягко |
| `maxDiffPixels` | не задано |
| `maxDiffPixelRatio` | не задано |
| `animations` | **`"disabled"`** — конечные анимации перематываются в конец, бесконечные отменяются |
| `caret` | `"hide"` |
| `scale` | `"css"` |
| `fullPage` | `false` |
| `maskColor` | `"#FF00FF"` |

Имя снапшота: `<test>-snapshots/example-1-chromium-darwin.png`. `stylePath` «pierces the Shadow DOM».
Предупреждение из документации: рендеринг зависит от ОС, версии, настроек, железа, **источника питания
(батарея против сети)** и headless-режима.

### 5.2 Chromatic

- **`diffThreshold` по умолчанию `.063`** — «balances high visual accuracy with low false positives (for
  example, from artifacts like anti-aliasing)». Порог `0.8` «may prevent Chromatic from detecting
  positioning changes».
- Антиалиасинговые пиксели по умолчанию **игнорируются**; включаются опцией `diffIncludeAntiAliasing`.
- Таймауты: **15 с на рендер story + 15 с на interaction-тесты**.
- CSS-переходы, CSS/SVG-анимации и видео ставятся на паузу автоматически; **JS-анимации (framer-motion) —
  нет**, нужен `MotionGlobalConfig.skipAnimations = isChromatic()`.

### 5.3 Percy

Дефолты из `percy config:create`:

```yaml
snapshot:
  widths: [375, 1280]
  min-height: 1024
  percy-css: ""
  disable-shadow-dom: false
discovery:
  network-idle-timeout: 100
  retry: false
```

Percy-on-Automate добавляет `freeze-animated-image` (по умолчанию `false`), `ignore-regions`,
`consider-regions`, `full-page` (`false`), `enable-javascript` (`false`).

### 5.4 Storybook addon-a11y

Построен на axe-core. Параметры и дефолты:

| Свойство | Default |
|---|---|
| `parameters.a11y.context` | `'body'` |
| `parameters.a11y.config` | отключает правило `region` |
| `parameters.a11y.test` | `undefined` → `'off'` \| `'todo'` \| `'error'` |
| `globals.a11y.manual` | `undefined` |

`'todo'` — нарушения показываются как предупреждения в UI, **в CI не дают ни ошибок, ни вывода**;
`'error'` — падающий тест. Дефолтный набор тегов — WCAG 2.0 A/AA + 2.1 A/AA + best practice; чтобы добавить
AAA или 2.2, приходится переписывать весь список `runOnly`.

### 5.5 Как снимать

Эталоны в **трёх режимах** (светлая, тёмная, `forced-colors: active`) и **двух ширинах** (1440 и 390),
порог различия 0.1 %. Анимации отключены, каретка скрыта, шрифты загружены (`document.fonts.ready`).

---

## 6. Figma Design Lint

`github.com/destefanis/design-lint`. Единственное, что проверяет из коробки: **привязан ли слой к стилю**.
«Out of the box, Design Lint only checks for layers that are not using styles.»

Типы ошибок: `fill`, `text`, `effect`, `stroke`, `radius`. Дефолтные допустимые радиусы —
**`[0, 2, 4, 8, 16, 24, 32]`** (правятся в `src/app/components/App.tsx` и `src/plugin/controller.ts`).

Не проверяет: контраст, размеры целей, сетку, расстояния. Пропускает заблокированные слои. Если у
текстового слоя несколько стилей (`typeof node.fillStyleId === "symbol"`), линтинг невозможен.

**Вывод для конвейера без Figma:** Design Lint не нужен. Его роль (привязка значений к источнику истины)
закрывается Stylelint и проверкой `--tokens` в `ui_audit.py`, причём строже.

---

## 7. Что встраивается в конвейер без Figma

Минимальный рабочий набор, всё оффлайн и в CI:

```bash
# 1. Токены валидны и проходят пороги
npx tz check dist/tokens.json
python3 ../../scripts/ui/build_reference_tokens.py --out ./dist && grep '<<<' dist/report.txt

# 2. Код не содержит литералов и чужих значений
npx stylelint "src/**/*.css"
npx eslint "src/**/*.{ts,tsx}"
bash checks.sh                     # пять грепов

# 3. Визуальный слой страницы
python3 ../../scripts/ui/ui_audit.py http://localhost:3000/orders \
  --preset admin --tokens dist/tokens.json --scheme both \
  --reduced-motion --hover --tab 24 --fail-on serious

# 4. Доступность по нормативу
npx pa11y-ci --sitemap http://localhost:3000/sitemap.xml

# 5. Визуальная регрессия (JS-раннер)
npx playwright test --update-snapshots=missing
```

Что из популярного **не** нужно: Figma Design Lint (нет Figma), Chromatic и Percy (облако и оплата; их
роль закрывает Playwright), Lighthouse в CI по каждому коммиту (медленно; достаточно на релизе).

---

## 8. Сводная таблица: кто что проверяет

| Проверка чек-листа | axe / Pa11y / Lighthouse | Stylelint / ESLint | Визуальная регрессия | `ui_audit.py` | Человек |
|---|---|---|---|---|---|
| Контраст текста (1.4.3) | да, кроме градиентов и картинок | нет | нет | да | — |
| Контраст границ и иконок (1.4.11) | **нет** | нет | нет | да | — |
| Фокус: наличие, толщина, контраст (2.4.7, 2.4.13) | **нет** | нет | частично | да | да |
| Цели нажатия (2.5.8) | `target-size`, **выключено по умолчанию** | нет | нет | да | — |
| Reflow 320 px (1.4.10) | **нет** | нет | да (снимок на 320) | да | да |
| Text spacing (1.4.12) | `avoid-inline-spacing` частично | нет | нет | нет | да |
| Шкала отступов, кратность | нет | да | нет | да | — |
| Высоты контролов, ряд высот | нет | частично | да | да | — |
| Радиусы, тени, `z-index` | нет | да | да | да | — |
| Принадлежность токенам | нет | да | нет | да (`--tokens`) | — |
| Число кеглей, весов, цветов | нет | частично | нет | да | — |
| Состояния (hover, selected) | нет | нет | да (снимки состояний) | да (`--hover`) | да |
| Сокращённое движение | нет | нет | нет | да | да |
| Тёмная тема | нет | нет | да | да | да |
| Композиция: «карточка в карточке», двойные границы | нет | нет | **да** | частично | да |
| Иерархия, осмысленность, ложное дно | нет | нет | нет | **нет** | **да** |

---

## Частые ошибки

1. **Считать зелёный Lighthouse доказательством доступности.** Он проверяет `wcag2a` и `wcag2aa` из axe и
   не покрывает 1.4.11, 1.4.10, 2.4.11, 2.4.13.
2. **Не смотреть на `incomplete`.** Половина реальных проблем контраста уходит именно туда: градиенты,
   картинки, перекрытия, псевдоэлементы.
3. **Округлять контраст.** axe усекает вниз и сравнивает строго больше: 4.499 → 4.49 → провал.
4. **Считать APCA как WCAG.** Это Lc со знаком, не отношение; порядок аргументов важен.
5. **Забыть включить `target-size` и `color-contrast-enhanced`** — оба выключены по умолчанию.
6. **Снимать скриншоты с `animations="allow"`** в Python: кадр случайный.
7. **Ожидать `to_have_screenshot` в Python** — его там нет.
8. **Полагаться на `expandShorthand`** в strict-value: раскрытие неполное и неоднозначное по спецификации.
9. **Забыть включить `no-arbitrary-value`** в eslint-plugin-tailwindcss: именно в квадратные скобки
   уходят числа вне шкалы.
10. **Ставить порог визуальной регрессии слишком мягким**: `diffThreshold: 0.8` перестаёт ловить сдвиги
    позиции.
11. **Проверять только светлую тему на одной ширине.**
12. **Проверять разметку вместо отрендеренного экрана.**
13. **Гонять `color-contrast` на всех страницах.** Правило дорогое; хватает репрезентативной выборки.
14. **Считать Figma Design Lint инструментом качества.** Он проверяет только привязку к стилям.

---

## Чек-лист

- [ ] `ui_audit.py --selftest` проходит (14 утверждений)?
- [ ] Прогон делается в светлой и тёмной теме, с `--reduced-motion`, `--hover`, `--tab`?
- [ ] Есть прогон с `--touch` (порог целей 44) и на ширине 320 CSS px?
- [ ] Набор токенов подан через `--tokens`, и проверка «цвета вне набора» пуста?
- [ ] `target-size` и (при необходимости) `color-contrast-enhanced` включены в конфиге axe?
- [ ] Результаты `incomplete` просмотрены, а не отброшены?
- [ ] Stylelint запрещает литералы для padding, margin, gap, radius, shadow, z-index, color, font-size?
- [ ] `no-arbitrary-value` включён в eslint-plugin-tailwindcss?
- [ ] Токены валидируются (`tz check` или `ajv`) на каждой сборке?
- [ ] Пять грепов по компонентам пусты?
- [ ] Визуальная регрессия снимается в трёх режимах и двух ширинах, анимации отключены, шрифты загружены?
- [ ] Отчёт «правило → найдено → порог → вердикт» сохраняется вместе со сборкой?
- [ ] `--fail-on serious` подключён в CI?

---

## Открытые вопросы

1. **Контраст нетекстовых элементов (1.4.11) не проверяет ни один публичный линтер.** Собственная проверка
   в `ui_audit.py` покрывает поля ввода; иконки и графические объекты остаются на человеке.
2. **Фокус (2.4.13) не проверяет никто.** Площадь индикатора «не меньше площади периметра толщиной 2 CSS
   px» в `ui_audit.py` не считается — проверяется только толщина, обрезка и контраст.
3. **Text spacing (1.4.12) автоматизируется плохо.** Букмарклет меняет стили, но оценка «потерян ли
   контент» остаётся визуальной.
4. **Визуальная регрессия на Python требует своего сравнивателя.** Готового решения уровня
   `toHaveScreenshot` в Python API нет.
5. **Нестабильность рендеринга между машинами.** Playwright прямо предупреждает про зависимость от ОС,
   железа и источника питания. Эталоны надо снимать в том же окружении, где идёт проверка.
6. **Порог «доля отступов из шкалы ≥ 95 %» не проверен на большой выборке сгенерированных страниц.**
   У семи собственных примеров он даёт 100 %, у живых продуктов медиана 72 %. Где проходит граница между
   «строго» и «нереалистично», не установлено.
7. **Проверка семантики применения токена невозможна.** `bg-subtle` вместо `bg-component` — значение из
   набора, правило нарушено; ловится только ревью.
8. **Нет открытого инструмента, который локализует визуальный дефект.** Ни у моделей (IoU < 0.20), ни у
   метрик.

---

## Источники

1. **axe-core 4.13**, Deque. Список правил:
   `https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md`; API:
   `.../doc/API.md`; исходники чеков `lib/checks/color/*.json`, `color-contrast-evaluate.js`,
   `target-size-evaluate.js`, `link-in-text-block-evaluate.js`. Описание ограничений:
   `https://dequeuniversity.com/rules/axe/4.10/color-contrast`.
2. **Pa11y 10** и **pa11y-ci**, `https://github.com/pa11y/pa11y`. Дефолты конфигурации, actions, коды
   возврата.
3. **Lighthouse 13.5**, `https://developer.chrome.com/docs/lighthouse/accessibility/scoring`; исходник
   `core/config/default-config.js` (веса), `core/gather/gatherers/accessibility.js` (конфиг axe),
   changelog (удаление `tap-targets` и `font-size`).
4. **Web Vitals: CLS**, `https://web.dev/articles/cls` — пороги 0.1 и 0.25 на 75-м перцентиле.
5. **apca-w3 0.1.9** (Myndex), `https://github.com/Myndex/apca-w3`; «APCA in a Nutshell»,
   `https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell` — пороги Lc и таблицы размеров.
6. **bridge-pca** (Myndex) — соответствия Lc 60 / 75 / 90 порогам WCAG 3:1 / 4.5:1 / 7:1.
7. **colorjs.io**, `https://colorjs.io/docs/contrast` — шесть алгоритмов, формулы, порядок аргументов.
8. **Stylelint 17**, `https://stylelint.io/user-guide/rules/declaration-property-value-allowed-list`,
   `unit-allowed-list`, `declaration-property-unit-allowed-list`, `color-no-hex`, `color-named`,
   `function-disallowed-list`.
9. **stylelint-declaration-strict-value 1.12.1**,
   `https://github.com/AndyOGo/stylelint-declaration-strict-value` — схема опций, дефолты, ограничения
   `expandShorthand`.
10. **eslint-plugin-tailwindcss 3.18**, `https://github.com/francoismassart/eslint-plugin-tailwindcss` —
    восемь правил, настройки, `whitelist` как массив регулярок.
11. **Playwright**: `https://playwright.dev/docs/test-snapshots` (дефолты `toHaveScreenshot`),
    `https://playwright.dev/python/docs/emulation` и API-референс Python (сигнатуры `color_scheme`,
    `reduced_motion`, `forced_colors`, `contrast`, `page.screenshot`).
12. **Chromatic**, `https://www.chromatic.com/docs/threshold`, `/delay`, `/animations`, `/snapshots` —
    `diffThreshold .063`, таймауты 15 + 15 с, поведение с анимациями.
13. **Percy**, `https://www.browserstack.com/docs/percy/references/config-options` — дефолты
    `widths [375, 1280]`, `min-height 1024`, `network-idle-timeout 100`.
14. **Storybook addon-a11y**, `https://storybook.js.org/docs/writing-tests/accessibility-testing` —
    параметры, значения `test`, отключённое правило `region`, ссылка на исследование Deque («up to 57 % of
    WCAG issues»).
15. **Figma Design Lint** (Daniel Destefanis),
    `https://github.com/destefanis/design-lint` — что проверяет, дефолтные радиусы, ограничения.
16. **WCAG 2.2**, `https://www.w3.org/TR/WCAG22/` и Understanding-документы — пороги 4.5:1, 3:1, 7:1,
    24 × 24, 44 × 44, 320 CSS px, площадь фокус-индикатора.
