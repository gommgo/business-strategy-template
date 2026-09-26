# Сводный глоссарий базы ui-research

Волна 4 · агент Q (аудит) · 22.09.2026. Собран из 13 папочных глоссариев `01-color/glossary.md` … `13-evaluation-checklists/glossary.md`
(у папки `14-recipes/` своего глоссария нет; её термины — пресет, ручки характера, цикл правок — присутствуют в глоссариях 09, 11, 12, 13).
Исходных записей: 944; после объединения дублей: 825 терминов, из них 86 встречаются в двух и более папках.
Определения не переписаны: каждая формулировка взята из глоссария своей папки; при объединении оставлена самая полная,
а расхождения других папок сохранены фразой «В NN то же под именем …» или «В NN: …».

## Как пользоваться

- **Формат записи**: `**RU термин** (EN термин, синонимы) — определение. Пример: значение. → путь к файлу [§раздел]; папки, где термин тоже определён.`
  Стрелка `→` ведёт к файлу, где термин раскрыт: указатель из папочного глоссария (`01-color/01-…` §2.3), иначе файл папки,
  в котором термин встречается чаще всего, иначе папка целиком.
- **Поиск**: `grep -n "^\*\*Термин" 00-glossary/glossary.md` по русскому термину, `grep -in "(.*english term" …` по английскому,
  либо алфавитные указатели в конце файла (EN и RU, термин → номер раздела).
- **Разделы**: 1 цвет · 2 типографика · 3 отступы и размеры · 4 форма и глубина · 5 сетка и раскладка · 6 компоненты и состояния ·
  7 иконки и изображения · 8 движение · 9 токены и темы · 10 дизайн-системы и измерения · 11 стили и арт-дирекция ·
  12 нейросети и генерация · 13 оценка и метрики · 14 несовместимая терминология (что принято в базе) · 15–16 указатели.
- **Метки** `[V15]` внутри определений ведут к дайджестам `91-videos/digests/`; `[S17 папки 02]` — к разделу «Источники» указанной папки.
- Термин с одинаковым названием, но разным смыслом в разных папках (например «Плейсхолдер» поля ввода и «Плейсхолдер» изображения,
  «Индикатор» компонента и «Индикатор» рубрики, «Овершут» иконки и «Перелёт» движения) оставлен двумя записями; такие пары собраны в разделе 14.

## Содержание

| Раздел | Терминов |
|---|---|
| 1. Цвет | 82 |
| 2. Типографика | 85 |
| 3. Отступы и размеры | 34 |
| 4. Форма и глубина | 43 |
| 5. Сетка и раскладка | 93 |
| 6. Компоненты и состояния | 104 |
| 7. Иконки и изображения | 60 |
| 8. Движение | 59 |
| 9. Токены и темы | 55 |
| 10. Дизайн-системы и измерения | 23 |
| 11. Стили и арт-дирекция | 50 |
| 12. Нейросети и генерация | 66 |
| 13. Оценка и метрики | 71 |
| 14. Несовместимая терминология | 27 строк таблицы |
| 15. Указатель EN | 957 |
| 16. Указатель RU | 743 |
## 1. Цвет

**Оттенок** (hue) — положение цвета на цветовом круге, 0–360°. В OKLCH: красный ≈ 20°, жёлтый ≈ 90°, зелёный ≈ 140°, синий ≈ 220°, фиолетовый ≈ 320°. → `01-color/01-color-models-and-scales.md` §1.1.

**Насыщенность** (saturation) — доля пигмента относительно максимума ДАННОЙ модели, 0–100 %. Есть в HSL и HSB; у разных оттенков одинаковый диапазон, хотя реальные максимумы различаются. Пример: `hsl(210 60% 64%)`. → `01-color/06-character-gradients-tools.md`.

**Хрома** (chroma) — абсолютная «цветность» без верхнего предела. OKLCH: 0 … ~0.37; LCH: 0 … 130+; HCT (Material): 0 … 120+. Пример: `oklch(0.62 0.214 260)` — C = 0.214. → `01-color/01-color-models-and-scales.md`.

**Светлота** (lightness) — воспринимаемая яркость. В HSL математическая и неточная, в LCH/OKLCH перцептивная. Пример: OKLCH L 0.54 у #0969da. → `01-color/01-color-models-and-scales.md`.

**Яркость** (brightness, value) — координата модели HSB/HSV, 0–100 %. Не равна воспринимаемой светлоте. → `01-color/01-color-models-and-scales.md`.

**Относительная яркость** (relative luminance) — физическая мера света 0–1 по формуле WCAG: `0.2126·R + 0.7152·G + 0.0722·B` в линейном sRGB. → `01-color/03-contrast.md` §1.1.

**OKLCH** — цилиндрическая запись пространства Oklab: `oklch(L C H / a)`. Создано Björn Ottosson в 2020. Пример: `oklch(0.683 0.169 258)`. → `01-color/01-color-models-and-scales.md` §1.3.

**Oklab** — декартова запись того же пространства: `oklab(L a b)`, где `a` — зелёный↔красный, `b` — синий↔жёлтый. Используется для градиентов: `linear-gradient(in oklab, …)`. → `01-color/06-character-gradients-tools.md`.

**CIELAB** (Lab) — перцептивно равномерное пространство CIE 1976. L* 0–100. Пример лестницы: 98, 93.3, 88.6, 79.9, 71.2, 60.5, 49.8, 38.4, 27, 15.6 (Postmark). → `01-color/01-color-models-and-scales.md`.

**LCH** (CIELCh, Lch(ab)) — цилиндрическая запись CIELAB. Имеет баг: сдвиг синего в фиолетовый при смене хромы в диапазоне H 270–330°. → `01-color/01-color-models-and-scales.md` §1.3.

**HCT** — пространство Material 3 (Hue, Chroma, Tone) на базе CAM16 и L* из CIELAB. Chroma в HCT не равна chroma в OKLCH: Material задаёт нейтраль chroma 4–6 HCT. → `01-color/01-color-models-and-scales.md` §3.3.

**Гамут** (gamut) — множество цветов, воспроизводимых устройством. sRGB покрывает ~35 % видимых человеку цветов, P3 добавляет ещё ~30 %. → `01-color/01-color-models-and-scales.md` §1.4.

**Отображение в гамут** (gamut mapping) — приведение цвета в доступный диапазон. Два способа: клиппинг каналов (быстро, меняет оттенок) и снижение хромы в OKLCH (правильно). Спека CSS Color 4 требует второй. → `01-color/01-color-models-and-scales.md`.

**Максимальная хрома** (max chroma) — наибольшая C, при которой пара (L, H) остаётся в гамуте. Находится бинарным поиском. Пример: при L 0.30 и H 90° (тёмно-жёлтый) она почти нулевая. → `01-color/01-color-models-and-scales.md` §1.4.

**Шаг шкалы** (step, shade, tone, scale step) — одно значение в шкале. У Radix и Geist за шагом закреплена РОЛЬ, у Tailwind и Polaris — положение на шкале светлоты. → `01-color/01-color-models-and-scales.md`; `06-components-visual/`. В 06: способ Radix: состояние = следующий шаг палитры. Пример: 3 → 4 → 5.

**Тональная палитра** (tonal palette) — термин Material 3: 13 тонов одного (hue, chroma): 0, 10…90, 95, 98, 99, 100. Пример: `primary40` — тон 40 палитры primary. → `01-color/01-color-models-and-scales.md` §3.3.

**Ключевой цвет** (key color) — вход алгоритма Material: из него выводятся пять тональных палитр (primary, secondary, tertiary, neutral, neutral-variant) плюс error. → `01-color/01-color-models-and-scales.md`.

**Тинт** (tint) — цвет, смешанный с белым. GOV.UK: `tint-25`, `tint-50`, `tint-80`, `tint-95`. Пример: blue tint-80 = #d2e2f1. → `01-color/01-color-models-and-scales.md`.

**Шейд** (shade) — цвет, смешанный с чёрным. GOV.UK: `shade-25`, `shade-50`. Пример: blue shade-50 = #0f385c. → `01-color/01-color-models-and-scales.md`.

**Тон** (tone) — цвет, смешанный с серым; у Material — ступень тональной палитры. → `01-color/06-character-gradients-tools.md`.

**Лестница светлоты** (lightness ladder) — заданный набор L для всех шагов шкалы. У Tailwind разные лестницы для хроматических и нейтральных семейств: на шаге 500 средняя L 68.3 % против 55.5 %. → `01-color/01-color-models-and-scales.md` §2.3.

**Кривая хромы** (chroma curve) — распределение C по шагам, колокол с пиком на 500–600. Tailwind: 0.018 на 50, 0.214 на 500, 0.088 на 950. → `01-color/01-color-models-and-scales.md` §2.4.

**Сдвиг оттенка** (hue shift) — изменение H по шкале. Tailwind amber: 95.3° на 50 → 45.6° на 950 (−50°). Ant Design задаёт формулой ±2° на шаг. → `01-color/01-color-models-and-scales.md` §2.5.

**Компенсация оттенка** (hue compensation) — намеренный отрицательный сдвиг для жёлтых, чтобы тёмные шаги не зеленели (термин Accessible Palette). → `01-color/01-color-models-and-scales.md`.

**Якорение** (anchoring) — привязка точного цвета бренда к шагу шкалы, чья светлота ближе всего к его светлоте. → `01-color/01-color-models-and-scales.md` §3.3.

**Чистый оттенок** (pure hue) — оттенок 0/60/120/180/240/300°, у которого минимум два RGB-канала равны. Признак: `rgb(77, 232, 232)`. В интерфейсе выглядит ядовито; отступать 5–10°. → `01-color/01-color-models-and-scales.md` §2.5.

**Нейтраль, нейтральная шкала** (neutral scale, gray scale) — шкала серых, на которой строятся фоны, границы и текст. «Almost everything in an interface is grey» (Refactoring UI). → `01-color/01-color-models-and-scales.md`.

**Чистый серый** (pure gray) — OKLCH C = 0. Tailwind `neutral`, Radix `gray`. → `01-color/01-color-models-and-scales.md`.

**Тонированная нейтраль** (tinted neutral) — серый с малой хромой в оттенок акцента. Рабочий диапазон OKLCH C 0.005–0.05. Пример: Radix `slate`/`mauve`/`sage`/`olive`/`sand`; Tailwind `slate`/`zinc`/`stone`/ `taupe`/`mist`/`mauve`/`olive`. → `01-color/01-color-models-and-scales.md` §4.2.

**Нейтраль-вариант** (neutral variant) — вторая, чуть более насыщенная нейтральная палитра Material (HCT chroma 8 против 4–6 у основной); используется для границ (`outline`). → `01-color/`.

**Тёплая / холодная нейтраль** (warm / cool neutral) — нейтраль с оттенком H 40–110° (тёплая: stone, taupe, sand) или H 200–330° (холодная: slate, gray, mist, zinc, mauve). → `01-color/`.

**Парный контентный цвет** (on-color, foreground token) — цвет текста и иконок на данной поверхности: `--md-sys-color-on-primary`, `--primary-foreground`. Расстояние до фона у Material — 50–60 тонов. → `01-color/02-semantic-roles-and-architecture.md` §1.2; `01-color/04-dark-theme.md`.

**Поверхность** (surface) — фон элемента, лежащего над фоном страницы: карточка, панель, поповер. Material различает 5 контейнеров: `surface-container-lowest/low/base/high/highest`. → `01-color/02-semantic-roles-and-architecture.md`.

**Слой** (layer) — термин Carbon: `background`, `layer-01`, `layer-02`, `layer-03`. → `01-color/05-states-and-interaction.md`.

**Инверсная поверхность** (inverse surface, inverted, knockout token) — тёмная плашка в светлой теме и наоборот: тултип, снекбар. Material `inverse-surface`, Polaris `color-bg-inverse`. → `06-components-visual/`; `09-design-tokens/`. В 06: тёмная поверхность в светлой теме. Пример: тултип, тост. В 09 то же под именем «Инверсная роль»: роль для компонента на противоположном фоне внутри текущей темы: тёмный тултип на светлой странице. В эталонной схеме — `color.bg.inverse` и `color.text.on-inverse`.

**Статусный цвет** (semantic status color) — info, success, warning/caution, danger/critical, neutral. ВНИМАНИЕ: `warning` у Polaris оранжевый, а у Primer оранжевый называется `severe`, жёлтый — `attention`. → `01-color/02-semantic-roles-and-architecture.md` §4.1.

**Субтильный стиль статуса** (muted, subtle, soft) — светлая плашка + тёмный текст того же оттенка + граница. Primer: `bgColor.<role>.muted` = hue.0, текст = hue.5. Реальный контраст 7–11:1. → `01-color/02-semantic-roles-and-architecture.md`.

**Сплошной стиль статуса** (emphasis, solid, fill) — насыщенная заливка + контрастный текст. Primer: `bgColor.<role>.emphasis` = hue.5. → `01-color/02-semantic-roles-and-architecture.md`.

**Magic** — роль Polaris для ИИ-функций (пурпурный). Аналог у Carbon — «AI tokens». → `01-color/02-semantic-roles-and-architecture.md` §4.5.

**Контрастное отношение WCAG** (contrast ratio) — `(L1 + 0.05) / (L2 + 0.05)`, диапазон 1:1 … 21:1. Пороги AA: 4.5:1 текст, 3:1 крупный текст и нетекстовые элементы. AAA: 7:1 и 4.5:1. → `01-color/03-contrast.md` §1; `10-design-systems-atlas/`. В 10 то же под именем «Контраст WCAG 2»: отношение относительных яркостей, от 1:1 до 21:1. Пороги: 4.5 для мелкого текста, 3.0 для крупного текста и нетекстовых элементов.

**APCA** (Accessible Perceptual Contrast Algorithm) — перцептивный метод Andrew Somers (Myndex), кандидат в WCAG 3. Величина Lc от 0 до ±106. → `01-color/03-contrast.md` §2.

**Lc** (lightness contrast) — значение APCA. Знак кодирует полярность: положительный — тёмный текст на светлом, отрицательный — светлый на тёмном. Уровни: 90 / 75 / 60 / 45 / 30 / 15. → `01-color/03-contrast.md`; `10-design-systems-atlas/`. В 10 то же под именем «APCA Lc»: перцептивный контраст со знаком: положительный означает тёмное на светлом, отрицательный — светлое на тёмном. Используется рядом с WCAG, а не вместо.

**Полярность контраста** (contrast polarity) — положительная (светлая тема, тёмный текст на светлом) или отрицательная (тёмная тема). Термин из литературы по читаемости. → `01-color/04-dark-theme.md` §1.

**Пространственная частота** (spatial frequency) — размер и толщина элемента. Чем выше (мельче и тоньше), тем больше нужно контраста. По Somers, влияет сильнее, чем цвет. → `01-color/03-contrast.md` §2.3.

**Критический контраст** (critical contrast) — минимальный контраст, при котором скорость чтения и понимание перестают расти. Для fluent reading нужен контраст ≥ 10× порога различимости (JND), предпочтительно 20×. → `01-color/`.

**Запас остроты** (acuity reserve) — по Lovie-Kitchin: spot-чтение 1.3:1, fluent 2:1, максимальная скорость 3:1 … 8:1. → `01-color/`.

**Fluent / sub-fluent / spot readability** — категории ARC: беглое чтение (body и основной контент), мягкое чтение (вторичное), точечное чтение (плейсхолдеры, disabled, копирайт). → `01-color/03-contrast.md` §2.2.

**Галация** (halation) — ореол вокруг светлого текста на тёмном фоне при избыточной яркости. Лечится затемнением самого светлого элемента, а не осветлением тёмного. → `01-color/04-dark-theme.md` §5.3.

**Композитинг альфы** (alpha compositing) — вычисление фактического цвета полупрозрачного слоя над фоном: `out = fg·α + bg·(1−α)`. Контраст меряется ПОСЛЕ него. → `01-color/03-contrast.md` §6.1; `13-evaluation-checklists/`. В 13: наложение полупрозрачного цвета на непрозрачный. Пример: `rgb(2 6 24 / .32)` над `#f8fafc` → `#a9acb3`.

**CVD** (color vision deficiency) — сниженная способность различать оттенки, около 5 % населения. → `01-color/`.

**Протанопия / протаномалия** (protan) — проблема с L/красным конусом. Красный на чёрном для них почти не контрастен: пара запрещена. → `01-color/03-contrast.md`.

**Дейтеранопия / дейтераномалия** (deutan) — проблема с M/зелёным конусом. Самый частый тип. → `01-color/03-contrast.md`.

**Тританопия** (tritan) — проблема с S/синим конусом, редко. → `01-color/03-contrast.md`.

**Ахроматопсия** (achromatopsia) — отсутствие цветового зрения, очень редко; сопровождается низкой остротой и светобоязнью. → `01-color/`.

**ΔE** (delta E, color difference) — мера различия цветов. Формулы: CIEDE2000, CMC, евклидово расстояние в Oklab. Ориентир для различимости категорий: ΔE(OKLab) ≥ 0.05 в норме и во всех симуляциях CVD. → `01-color/02-semantic-roles-and-architecture.md` §5.2; `10-design-systems-atlas/`. В 10 то же под именем «ΔE OKLab»: расстояние между цветами в перцептивно равномерном пространстве. Порог приёмки для палитры графиков: минимальное ΔE ≥ 0.05 во всех трёх симуляциях дальтонизма.

**Правило «не только цветом»** (WCAG 1.4.1 Use of Color, уровень A) — цвет не может быть единственным носителем смысла. → `01-color/`.

**«Get it right in black & white»** — приём Datawrapper: перевести палитру в ч/б; если категории неразличимы, значит различаются только оттенком. → `01-color/`.

**Hover / active (pressed) / selected / focus / disabled** — состояния. Active — момент нажатия, selected — устойчивое состояние выбора; разводить их обязательно. → `01-color/`.

**Выделение** (selection) — `::selection`; если не задать, браузер возьмёт системный `Highlight`. → `01-color/05-states-and-interaction.md`.

**`prefers-color-scheme`** — медиафича предпочтения светлой/тёмной темы. → `01-color/`.

**`light-dark()`** — CSS-функция, возвращающая первое значение при светлой схеме, второе при тёмной. Baseline с мая 2024. Принимает и `<color>`, и `<image>`. → `01-color/04-dark-theme.md`; `09-design-tokens/`. В 09: CSS-функция выбора значения по текущей схеме. Экономит половину объявлений, но третий режим в неё не помещается.

**`forced-colors`** — режим принудительных системных цветов (Windows High Contrast). Подменяет `color`, `background-color`, `border-color`, `outline-color`, SVG `fill`/`stroke` и др.; принудительно убирает `box-shadow`, `text-shadow` и не-url-овые `background-image`. → `01-color/04-dark-theme.md` §9.3; `09-design-tokens/`. В 09: режим принудительных цветов операционной системы. Не тема, а отказ от темы: цвета задаёт ОС, токены цвета перестают действовать.

**`forced-color-adjust`** — свойство управления подменой: `auto` | `none` | `preserve-parent-color`. → `01-color/`.

**Системные цвета CSS** (system colors) — `Canvas`, `CanvasText`, `LinkText`, `ButtonFace`, `ButtonText`, `ButtonBorder`, `Field`, `FieldText`, `Highlight`, `HighlightText`, `GrayText`, `AccentColor` и др. → `01-color/`.

**Backplate** — подложка, которую браузер рисует под текстом в forced-colors, чтобы сохранить контраст поверх изображений. → `01-color/04-dark-theme.md`.

**`prefers-contrast`** — медиафича: `no-preference` | `more` | `less` | `custom`. → `01-color/`.

**Категориальная палитра** (categorical, qualitative palette) — 6–10 цветов для несравнимых категорий. Требует РАЗНОЙ светлоты, иначе схлопывается при CVD. → `01-color/02-semantic-roles-and-architecture.md` §5.2.

**Последовательная палитра** (sequential palette) — один оттенок, монотонная светлота, ΔL ≈ 10 п.п. при 7 ступенях. Для непрерывной величины. → `01-color/`.

**Расходящаяся палитра** (diverging palette) — два оттенка через нейтральную середину, симметричные светлоты, нечётное число ступеней. Для величины с осмысленной серединой. Не красный↔зелёный. → `01-color/`.

**Viridis** — семейство перцептивно равномерных шкал, монотонных по светлоте и пригодных при CVD. → `01-color/02-semantic-roles-and-architecture.md`.

**Радуга** (rainbow, jet) — шкала, немонотонная по светлоте; для непрерывных данных не годится. → `01-color/02-semantic-roles-and-architecture.md`.

**Leonardo** (`@adobe/leonardo-contrast-colors`) — генерация шкал по СПИСКУ ЦЕЛЕВЫХ КОНТРАСТОВ, а не по светлотам. Параметры темы: `lightness`, `contrast`, `saturation`. → `01-color/06-character-gradients-tools.md`.

**Huetone** — генератор шкал с отображением контраста каждого шага по WCAG и APCA; использует chroma.js. → `01-color/01-color-models-and-scales.md`.

**culori** — JS-библиотека: конвертации, `wcagContrast`, `clampChroma`, `toGamut`, `filterDeficiency*`, `interpolate`. → `01-color/06-character-gradients-tools.md`.

**colorjs.io** — JS-библиотека с классом `Color`: `.oklch.l`, `.inGamut('srgb')`, `.toGamut()`. → `01-color/`.

**Accessible Palette** — веб-инструмент: лестница светлот CIELAB + компенсация оттенка + двойная проверка контраста. → `01-color/01-color-models-and-scales.md`.

**oklch.com** — пикер OKLCH с графиком границы гамута sRGB/P3 (Evil Martians). → `01-color/`.

**Bridge-PCA** — метод, обратно совместимый с WCAG 2, но с перцептивной математикой. → `01-color/`.

**`stylelint-gamut`** — линтер, находящий цвета вне sRGB, не обёрнутые в `@media (color-gamut: p3)`. → `01-color/`.

**Крупный текст** (large text) — от 24 px обычного веса или от 18.5 px полужирного; для него порог контраста 3:1 вместо 4.5:1. → `01-color/`; `13-evaluation-checklists/`. В 01: 18 pt (24 px) и больше, либо 14 pt (≈ 18.67 px) и больше при `font-weight` ≥ 700. В 13: текст, к которому применяется порог 3:1. Пример: 18 pt = 24 CSS px, 14 pt bold = 18.667 px.

**Принудительные цвета** (forced colors) — режим высокой контрастности ОС. Пример: `@media (forced-colors: active)`. → `04-shape-elevation/`.

**`color-scheme`** — CSS-свойство, сообщающее браузеру, какие темы поддерживает страница. Без него скроллбары и встроенные элементы формы остаются светлыми на тёмном фоне. → `01-color/`. В 01: CSS-свойство, объявляющее поддерживаемые схемы. `light dark` обязательно, иначе не работает `light-dark()` и нативные контролы остаются светлыми.

## 2. Типографика

**Гарнитура** (typeface, font family) — рисунок шрифта во всех его начертаниях. Пример: Inter, Golos Text. → `02-typography/01-font-selection.md`.

**Начертание** (font, style) — конкретный файл: вес + курсив + ширина. Пример: Inter SemiBold Italic. → `02-typography/02-type-scale.md`.

**Вес, насыщенность** (weight) — толщина штриха, числом 100–900. Интерфейсу нужны 400, 500, 600; у Polaris из переменного шрифта взяты 450 / 550 / 650 / 700. → `02-typography/04-weight-hierarchy-color.md`.

**Переменный шрифт** (variable font) — один файл с непрерывными осями. Пример: InterVariable, оси `wght` 100–900 и `opsz` 14–32. → `02-typography/01-font-selection.md`.

**Ось** (axis) — параметр переменного шрифта. `wght` вес, `wdth` ширина, `opsz` оптический размер, `slnt` наклон, `ital` курсив. → `02-typography/`.

**Гротеск, рубленый** (sans serif) — шрифт без засечек. Основной класс для интерфейсов. → `02-typography/01-font-selection.md`.

**Неогротеск** (neo-grotesque) — закрытая апертура, вертикальная ось, почти нулевой контраст, наклонный вместо курсива. Пример: Inter, Roboto, Helvetica, IBM Plex Sans. → `02-typography/01-font-selection.md`.

**Гуманистический гротеск** (humanist sans) — наследует динамику широкого пера. Пример: PT Sans, Open Sans, Fira Sans, Commissioner. → `02-typography/01-font-selection.md`.

**Геометрический гротеск** (geometric sans) — построен на круге и прямой. Пример: Poppins, Montserrat, Futura. В интерфейсах почти не применяется. → `02-typography/`.

**Антиква, шрифт с засечками** (serif) — пример: IBM Plex Serif, Literata. В интерфейсе только для «редакторских» режимов. → `02-typography/01-font-selection.md`.

**Моноширинный** (monospace) — все знаки одной ширины. Пример: JetBrains Mono, ширина знака 0.600 em. → `02-typography/01-font-selection.md`.

**Униширинный** (uniwidth) — ширина знака не меняется при смене веса, так что строка не «дышит» при выделении. Пример: Golos UI, PT Root UI. → `02-typography/`.

**Системный стек** (system font stack) — список системных шрифтов вместо веб-шрифта. Пример: `system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`. → `02-typography/01-font-selection.md`.

**Кегль, размер шрифта** (font size, point size) — заданный размер. Пример: 14 px = 0.875rem. → `02-typography/03-leading-tracking-measure.md`.

**Кегельная площадка** (em) — условный квадрат, в который вписан рисунок. `unitsPerEm` обычно 1000 или 2048. → `02-typography/`.

**Рост строчных** (x-height) — высота буквы «х» без выносных элементов. Пример: Inter 0.546 em, то есть 8.73 px при кегле 16 px. → `02-typography/`.

**Высота прописных** (cap height) — высота заглавной буквы. Пример: Inter 0.728 em. → `02-typography/`.

**Верхний выносной элемент** (ascender) — часть буквы выше роста строчных: `b`, `d`, `б`. → `02-typography/`.

**Нижний выносной элемент** (descender) — часть ниже базовой линии: `p`, `y`, `у`, `д`. → `02-typography/`.

**Базовая линия** (baseline) — линия, на которой стоят буквы. → `02-typography/05-numbers-rhythm-opentype.md`.

**Апертура** (aperture) — ширина «выхода» в незамкнутых знаках `c`, `e`, `s`. Открытая апертура улучшает читаемость мелкого. → `02-typography/01-font-selection.md`.

**Контраст штриха** (stroke contrast) — разница толщин основного и соединительного штриха. У интерфейсных гротесков близок к нулю. → `02-typography/`.

**Обратный контраст** (reverse contrast) — дефект, когда восходящая диагональ толще нисходящей. Частая претензия к кириллице: «И», «К», «У», «М». → `02-typography/`.

**Инктрап** (ink trap) — вырез в месте схождения штрихов, компенсирующий растекание. Есть у Inter, PT Sans Caption. → `02-typography/01-font-selection.md`.

**Текстура шрифта** (texture) — общий «серый тон» и ритм набора. Оценивается увеличением: в мелком размере кривой и ровный шрифт неразличимы, при увеличении видны дефекты контура `[V15]`. → `02-typography/`.

**Контур** (outline) — кривая, из которой состоит глиф. Признаки плохого контура: тонкие линии «гуляют» по толщине, контур ломается у петли, линия приплющена `[V15]`. → `02-typography/01-font-selection.md`.

**Тест «ухо»** — способ найти предел отрицательного трекинга: набрать слово «ухо» и уменьшать значение, пока буквы не соприкоснутся; предыдущее значение — предел `[V15]`. → `02-typography/`.

**Оптический размер** (optical size, `opsz`) — подстройка рисунка под кегль: мелкий текст получает более открытые формы, крупный — тонкие детали. CSS: `font-optical-sizing: auto`. → `02-typography/05-numbers-rhythm-opentype.md`; `07-iconography-imagery/`. В 07: вариант знака, нарисованный под конкретный размер показа, а не масштабированный. Пример: ось `opsz` 20–48 у Material Symbols; семь готовых размеров у Fluent.

**Вертикальные метрики** (vertical metrics) — `hhea`, `typo` (`sTypo*`), `win` (`usWin*`): три набора значений ascender/descender/lineGap, из которых браузер выбирает в зависимости от ОС. → `02-typography/01-font-selection.md`.

**Интерлиньяж** (line-height, leading) — расстояние между базовыми линиями строк. Пример: 14/20 px = 1.43. → `02-typography/03-leading-tracking-measure.md`.

**Полулидинг** (half-leading) — половина разницы между интерлиньяжем и кеглем, добавляемая сверху и снизу строки. Для 32/40 это 4 px с каждой стороны. → `02-typography/05-numbers-rhythm-opentype.md`.

**Обрезка полулидинга** (leading trim, `text-box-trim`) — удаление этого лишнего пространства. CSS: `text-box: trim-both cap alphabetic`, Baseline с августа 2026. → `02-typography/`.

**Трекинг, межбуквенное расстояние** (tracking, letter-spacing) — равномерное изменение просветов между всеми буквами. Пример: −0.01 em на заголовке 24 px. → `02-typography/03-leading-tracking-measure.md`.

**Кернинг** (kerning) — точечная подгонка просвета между конкретной парой знаков. CSS: `font-kerning`. → `02-typography/05-numbers-rhythm-opentype.md`.

**Длина строки, формат** (measure, line length) — число знаков в строке. Норма 45–75, потолок 80 (WCAG 1.4.8). → `02-typography/03-leading-tracking-measure.md`; `03-spacing-sizing/`. В 03 то же под именем «Мера строки»: длина строки текста в символах. Пример: 45–75, детали в `02-typography/`.

**Абзацный отбив** (paragraph spacing) — вертикальный отступ между абзацами. Atlassian: 16 px при теле 16 px. → `02-typography/02-type-scale.md`.

**Выключка по формату** (justify) — выравнивание по обоим краям. В интерфейсах не применяется. → `02-typography/03-leading-tracking-measure.md`.

**Висячая строка** (orphan, widow) — одинокая строка абзаца, оторванная от остальных. CSS: `text-wrap: pretty` минимизирует их число. → `02-typography/05-numbers-rhythm-opentype.md`.

**Балансировка строк** (`text-wrap: balance`) — выравнивание числа знаков по строкам. Работает для блоков до 6 строк в Chromium и 10 в Firefox. → `02-typography/`.

**Висячая пунктуация** (hanging punctuation) — вынос кавычки или скобки в поле. CSS: `hanging-punctuation`, поддержка ограниченная. → `02-typography/`.

**Базовая сетка** (baseline grid) — общая сетка базовых линий. В вебе заменяется кратностью 4 px. → `02-typography/05-numbers-rhythm-opentype.md`; `05-layout-grid/`. В 05 то же под именем «Базовая линия»: горизонтальные линии, по которым сидят строки текста. Пример: Fluent 2, один из четырёх типов.

**Вертикальный ритм** (vertical rhythm) — согласованность вертикальных величин: интерлиньяж и отступы кратны одному шагу (4 px, у GOV.UK 5 px). → `02-typography/05-numbers-rhythm-opentype.md`.

**Типографическая шкала** (type scale, type ramp) — набор размеров и связанных с ними интерлиньяжей, весов и трекингов. Пример: Fluent 2 web ramp 10/12/14/16/20/24/28/32/40/68 px. → `02-typography/02-type-scale.md`.

**Модульная шкала** (modular scale) — шкала с постоянным коэффициентом: 1.125, 1.2, 1.25, 1.333. Ant Design использует `e^(1/5) ≈ 1.2214` с округлением до чётных. → `02-typography/02-type-scale.md`.

**База, базовый размер** (base font size) — размер основного текста. 14 px для админок, 16 px для клиентских сервисов, 13 px у Polaris, 19 px у GOV.UK. → `02-typography/02-type-scale.md`.

**Роль** (role, text style, variant) — именованная комбинация размера, интерлиньяжа, веса и трекинга. Пример: Carbon `body-compact-01` = 14/18/400/+0.16 px. → `02-typography/02-type-scale.md`.

**Тип-сет** (type set) — группа ролей под сценарий. Carbon: productive (продукт) и expressive (маркетинг). → `02-typography/02-type-scale.md`.

**Плавная типографика** (fluid type) — размер, зависящий от ширины окна через `clamp()`. В приложениях не применяется. → `02-typography/02-type-scale.md`.

**Dynamic Type** — системное укрупнение текста в iOS/iPadOS/watchOS/visionOS. Тело меняется с 14 до 23 pt без учёта accessibility-размеров. → `02-typography/02-type-scale.md`.

**Табличные цифры** (tabular figures, `tnum`, tabular numerals) — цифры одинаковой ширины для выравнивания в столбик. CSS: `font-variant-numeric: tabular-nums`. → `02-typography/05-numbers-rhythm-opentype.md`; `06-components-visual/`. В 06: моноширинные цифры для колонок. Пример: `font-variant-numeric: tabular-nums`.

**Пропорциональные цифры** (proportional figures, `pnum`) — цифры разной ширины, для текста. → `02-typography/`.

**Маюскульные цифры** (lining figures, `lnum`) — в рост прописных. Стандарт для интерфейса. → `02-typography/`.

**Минускульные, старостильные цифры** (oldstyle figures, `onum`) — с выносными элементами. Для книг. → `02-typography/`.

**Перечёркнутый ноль** (slashed zero, `zero`) — отличает 0 от O. CSS: `font-variant-numeric: slashed-zero`. → `02-typography/05-numbers-rhythm-opentype.md`.

**Стилистический набор** (stylistic set, `ss01`–`ss20`) — альтернативный набор глифов. Пример: Inter `ss02` «Disambiguation» разводит похожие знаки. → `02-typography/`.

**Вариант знака** (character variant, `cv01`–`cv99`) — альтернатива одного знака. Пример: Inter `cv11` одноэтажная `a`, `cv05` строчная `l` с хвостом. → `02-typography/`.

**Контекстные альтернативы** (`calt`) — подстановка глифов в зависимости от соседей. Включены по умолчанию. → `02-typography/05-numbers-rhythm-opentype.md`.

**Лигатуры** (`liga` обычные, `dlig` декоративные) — слитные начертания `fi`, `fl`. В коде и идентификаторах отключаются: `font-variant-ligatures: none`. → `02-typography/05-numbers-rhythm-opentype.md`.

**Капитель** (small caps, `smcp`, `c2sc`) — прописные ростом со строчные. → `02-typography/`.

**Формы под прописные** (`case`) — подтягивание скобок и знаков под высоту прописных при капсе. → `02-typography/04-weight-hierarchy-color.md`.

**Локальные формы** (`locl`) — варианты глифов по языку, подставляются по атрибуту `lang`. → `02-typography/05-numbers-rhythm-opentype.md`.

**Веб-шрифт** (web font) — шрифт, загружаемый страницей через `@font-face`. → `02-typography/`.

**Сабсеттинг** (subsetting) — сборка файла только с нужными знаками. Кириллица и латиница разводятся по `unicode-range`. → `02-typography/01-font-selection.md`.

**`font-display`** — стратегия отображения до загрузки: `swap`, `optional`, `block`, `fallback`. → `02-typography/`.

**FOUT** (flash of unstyled text) — вспышка текста фолбэком до подмены. → `02-typography/`.

**Метрический фолбэк** (font metric override) — подгонка локального шрифта под метрики веб-шрифта через `size-adjust`, `ascent-override`, `descent-override`, `line-gap-override`. → `02-typography/`.

**`size-adjust`** — множитель контуров и метрик шрифта в `@font-face`. Baseline с сентября 2023. → `02-typography/`.

**Сглаживание** (`-webkit-font-smoothing`) — `antialiased` отключает субпиксельное сглаживание на macOS. Глобально включать не рекомендуется. → `02-typography/04-weight-hierarchy-color.md`.

**Хинтинг** (hinting) — инструкции в шрифте для точной отрисовки на пиксельной сетке. Критичен на Windows без Retina. → `02-typography/01-font-selection.md`.

**Ёлочки** (guillemets) — русские внешние кавычки «…», U+00AB и U+00BB. → `02-typography/06-localization-and-ai-errors.md`.

**Лапки** — вложенные русские кавычки „…“, U+201E и U+201C. → `02-typography/`.

**Программистские кавычки** (straight quotes) — `"` U+0022 и `'` U+0027. Только в коде. → `02-typography/06-localization-and-ai-errors.md`.

**Длинное тире** (em dash) — `—` U+2014, между словами с пробелами. → `02-typography/06-localization-and-ai-errors.md`.

**Короткое тире** (en dash) — `–` U+2013, в диапазонах без пробелов: `10–20`. → `02-typography/06-localization-and-ai-errors.md`.

**Минус** (minus sign) — `−` U+2212, в отрицательных числах. → `02-typography/06-localization-and-ai-errors.md`.

**Неразрывный пробел** (no-break space) — U+00A0, связывает слова, которые нельзя разрывать переносом. → `02-typography/05-numbers-rhythm-opentype.md`.

**Узкий неразрывный пробел** (narrow no-break space) — U+202F, разделитель разрядов; его вставляет `Intl.NumberFormat('ru-RU')`. → `02-typography/06-localization-and-ai-errors.md`.

**Знак номера** — `№` U+2116, входит в кириллический `unicode-range`. → `02-typography/01-font-selection.md`.

**Знак рубля** — `₽` U+20BD, в Unicode с 2014 года, есть не во всех шрифтах. → `02-typography/05-numbers-rhythm-opentype.md`.

**Sentence case** — прописная только в первом слове и в именах собственных. Единственный допустимый регистр заголовков в русском. → `02-typography/04-weight-hierarchy-color.md`.

**Title Case** — прописная в каждом значимом слове. Английская конвенция, в русском ошибка. → `02-typography/04-weight-hierarchy-color.md`.

**Болгарская кириллица** — начертания, похожие на прямой курсив: круглая «в» с верхним выносным элементом, курсивные формы «й», «п», «т» в прямом начертании. В заголовке и логотипе допустимы, в тексте для русского читателя неуместны `[V15]`, `[S17 папки 02]`. → `02-typography/06-localization-and-ai-errors.md`.

**WCAG 1.4.4 Resize Text** — текст масштабируется до 200 % без потери контента. → `02-typography/`.

**WCAG 1.4.8 Visual Presentation** — не более 80 знаков в строке (40 для CJK). → `02-typography/`.

**WCAG 1.4.12 Text Spacing** — интерфейс не ломается при `line-height: 1.5`, отступе абзаца `2em`, `word-spacing: 0.16em`, `letter-spacing: 0.12em`. → `02-typography/`.

## 3. Отступы и размеры

**Базовая единица** (base unit, grid unit) — наименьший шаг, на который кратны все отступы и размеры системы. Пример: 4 px (Polaris, Primer, Tailwind), 8 px (Atlassian «space.100»). → `03-spacing-sizing/01-spacing-scale.md`; `10-design-systems-atlas/`. В 10: число, на которое кратны значения шкалы отступов: 4 px у большинства, 5 у GOV.UK, 8 у Carbon (в miniUnits), 2 у Core Components.

**Шкала отступов** (spacing scale) — закрытый список разрешённых значений отступов. Пример: 2, 4, 8, 12, 16, 24, 32, 48, 64, 96. → `03-spacing-sizing/01-spacing-scale.md`.

**Мини-юнит** (mini-unit, mini unit) — имя базовой единицы в Carbon; токены выражаются в кратных ему. Пример: `miniUnit = 8`, `spacing-05 = miniUnits(2) = 16px`. → `05-layout-grid/`. В 05 то же под именем «Базовая единица сетки»: квадрат, кратными которому задаются размеры. Пример: Carbon 8 × 8 px.

**Внутренний отступ** (padding, inset) — расстояние от границы контейнера до его содержимого. Пример: карточка 16, модалка 24. → `03-spacing-sizing/01-spacing-scale.md`.

**Внешний отступ** (margin) — расстояние снаружи элемента; в современных системах вытесняется `gap`. Пример: не используется внутри компонентов (Carbon Stack). → `03-spacing-sizing/01-spacing-scale.md`.

**Зазор** (gap) — расстояние между соседними элементами, задаётся родителем. Пример: `gap: 8px` в группе кнопок. → `03-spacing-sizing/01-spacing-scale.md`.

**Сжатый внутренний отступ** (inset squish) — внутренний отступ с уменьшенной (обычно вдвое) вертикалью. Пример: кнопка 6 × 12, ячейка 8 × 16. → `03-spacing-sizing/01-spacing-scale.md`.

**Растянутый внутренний отступ** (inset stretch) — внутренний отступ с увеличенной вертикалью. Пример: textarea 12 × 12 при однострочном 8 × 12. → `03-spacing-sizing/01-spacing-scale.md`.

**Стек** (stack) — вертикальный ритм между блоками; компонент-обёртка с `gap`. Пример: Primer stack: condensed 8, normal 16, spacious 24. → `03-spacing-sizing/01-spacing-scale.md`.

**Инлайн-набор** (inline) — горизонтальный набор с переносом: теги, крошки, кнопки. Пример: gap 8. → `03-spacing-sizing/02-density.md`.

**Внешние поля страницы** (page margins, page inline padding) — расстояние от края окна до контента. Пример: 16 / 24 / 32–40 по брейкпоинтам. → `03-spacing-sizing/`.

**Воздух, белое пространство** (whitespace, negative space) — незанятая площадь; инструмент группировки и иерархии. Пример: «double your whitespace» (Kennedy). → `03-spacing-sizing/01-spacing-scale.md`; `07-iconography-imagery/`. В 07 то же под именем «Негативное пространство»: пустое поле вокруг объекта. У Polaris используется для выравнивания оптического веса картинок одного слота.

**Оптическая компенсация** (optical adjustment) — ручная правка на 1–2 px ради визуального баланса. Пример: иконка сдвинута на 1 px вправо в круглой кнопке. → `03-spacing-sizing/01-spacing-scale.md`.

**Отрицательный отступ** (negative space token) — токен с отрицательным значением для выхода за padding контейнера. Пример: `space.negative.200` = −16. → `03-spacing-sizing/`.

**Плотность** (density, density mode) — количество информации на единицу площади; задаётся высотами и padding. Пример: compact / default / comfortable. → `03-spacing-sizing/02-density.md`; `06-components-visual/`; `09-design-tokens/`; `10-design-systems-atlas/`. В 06: режим отступов и высот. Пример: compact / default / spacious. В 09: ось, меняющая отступы, высоты контролов и высоты строк. Не меняет кегль, радиусы, цвета и цель нажатия. В 10 то же под именем «Режим плотности»: ось темы, меняющая отступы и высоты, но не кегль, радиусы, цвета и цель нажатия.

**Шаг плотности** (density interval) — на сколько меняется высота при переходе на соседний режим. Пример: 4 px (Material `$interval`). → `03-spacing-sizing/02-density.md`.

**Шкала плотности** (density scale) — числовой параметр режима. Пример: Material 0, −1, −2, −3. → `03-spacing-sizing/02-density.md`.

**Компактный алгоритм** (compact algorithm) — производная тема Ant Design с уменьшенными размерами. Пример: `controlHeight` 32 → 28. → `03-spacing-sizing/`.

**Масштабный множитель** (scaling factor) — глобальный коэффициент для всех размеров темы. Пример: Radix `--scaling` 0.9…1.1, Mantine `scale`. → `03-spacing-sizing/`.

**Высота контрола** (control height) — внешняя высота кнопки, поля, select. Пример: 24 / 28 / 32 / 36 / 40 / 48. → `03-spacing-sizing/03-control-and-panel-sizes.md`.

**Контейнерный токен** (container token) — токен высоты интерактивного элемента в Carbon. Пример: `container-03 = 40px`. → `03-spacing-sizing/`.

**Цель нажатия** (touch target, target size, hit area, hit target) — область, реагирующая на клик или касание. Пример: 24 × 24 (WCAG AA), 44 × 44 (AAA), 48 dp (Material). → `03-spacing-sizing/02-density.md`; `06-components-visual/`; `10-design-systems-atlas/`. В 06: минимальная зона взаимодействия. Пример: 24 (WCAG AA), 44 (тач). В 10: bounding box интерактивного элемента. Порог WCAG 2.2 SC 2.5.8 — 24 px; в практике медиана 14.1 % элементов меньше порога.

**Недоразмерная цель** (undersized target) — цель меньше 24 × 24, проверяется правилом кругов. Пример: 20 × 20 с зазором 4 проходит. → `03-spacing-sizing/`.

**Правило кругов** (spacing exception) — круги диаметром 24 px вокруг центров недоразмерных целей не должны пересекаться. Пример: из Understanding 2.5.8. → `13-evaluation-checklists/`. В 13: исключение SC 2.5.8 для недоразмерных целей. Пример: круги 24 px вокруг центров не пересекаются.

**Расширенная зона нажатия** (expanded hit area) — увеличение активной области без изменения видимой. Пример: `::after { inset: -6px }`. → `03-spacing-sizing/`.

**Асимметрия «видно/нажимается»** (view–tap asymmetry) — элемент читается, но слишком мал для касания. Пример: точки каруселей iOS, свотчи 1 мм. → `03-spacing-sizing/`.

**Закон Фиттса** (Fitts's law) — время достижения цели растёт при уменьшении размера и росте расстояния. Пример: обоснование крупных частых кнопок. → `03-spacing-sizing/`.

**Плотность указателя** (pointer type) — медиа-признак типа ввода. Пример: `@media (pointer: coarse)` → цели 44+. → `03-spacing-sizing/`.

**Размерный вариант** (size variant) — именованный набор размеров компонента. Пример: small / medium / large. → `03-spacing-sizing/`.

**Оверлей** (overlay) — общее имя для всплывающих слоёв (меню, поповер, диалог). Пример: Primer overlay 192/320/480/640/960. → `03-spacing-sizing/03-control-and-panel-sizes.md`.

**Смещение слоя** (overlay offset) — зазор между триггером и всплывающим слоем. Пример: 4 px (Primer). → `03-spacing-sizing/`.

**Класс ширины поля** (width class) — привязка ширины поля к ожидаемой длине данных. Пример: GOV.UK: 2, 4, 10, 20 символов, full. → `03-spacing-sizing/`.

**Высота строки списка** (row height) — внешняя высота строки таблицы или списка. Пример: 32 / 40 / 48 / 56. → `03-spacing-sizing/`.

**Правило внутреннего и внешнего** (law of proximity, proximity rule, inner/outer spacing) — внутри группы расстояния меньше, чем между группами. Пример: 12 внутри → ≥ 24 снаружи. → `05-layout-grid/04-alignment-whitespace-composition.md`; `03-spacing-sizing/`. В 03 то же под именем «Правило близости»: принцип восприятия: близкие элементы читаются как группа. Пример: отступ между группами ≥ 2× внутреннего.

## 4. Форма и глубина

**Радиус скругления** (border radius, corner radius) — радиус дуги, которой скруглён угол элемента. Пример: 6 px (Primer, Ant), 8 px (Polaris). → `04-shape-elevation/`.

**Шкала форм** (shape scale) — набор разрешённых радиусов системы. Пример: Material 3: 0/4/8/12/16/28/full. → `04-shape-elevation/`.

**Вложенный радиус** (nested radius) — радиус внутреннего элемента, согласованный с внешним. Пример: внутренний = внешний − padding. → `06-components-visual/`. В 06: внутренний радиус = внешний − padding. Пример: 12 − 4 = 8.

**Концентричные углы** (concentric corners) — углы вложенных элементов с общим центром кривизны. Пример: Apple: контролы концентричны углам окна. → `04-shape-elevation/02-shadows-layers-depth.md`.

**Пилюля** (pill) — форма с радиусом, равным половине высоты. Пример: `border-radius: 9999px`. → `04-shape-elevation/01-radius-and-borders.md`; `06-components-visual/`; `10-design-systems-atlas/`. В 06: полное скругление по высоте. Пример: `border-radius: 9999px`. В 10: радиус, заведомо больший половины высоты элемента. Кодируется магическим числом: 9999 px (Tailwind, Chakra, Polaris), 10000 (Fluent), 999999 (Carbon), 624.9375rem (Atlassian), 15rem (Salesforce), 99px (Core Components).

**Полный радиус** (full radius) — токен «максимального» радиуса. Пример: 9999 px (Polaris), 10000 (Fluent), 999999 (Carbon). → `04-shape-elevation/`.

**Частичный радиус** (partial radius, corner token) — скругление только части углов. Пример: `corner-large-top` = 16 16 0 0. → `04-shape-elevation/`.

**Суперэллипс** (superellipse) — кривая `x^(2K)+y^(2K)=1`, обобщение окружности. Пример: `superellipse(2)` = squircle. → `04-shape-elevation/01-radius-and-borders.md`.

**Сквиркл** (squircle) — суперэллипс с K = 2, «эппловское» скругление. Пример: `corner-shape: squircle`. → `04-shape-elevation/01-radius-and-borders.md`.

**Сглаживание углов** (corner smoothing) — плавное изменение кривизны на переходе сторона-угол. Пример: ползунок в Figma, `superellipse()` в CSS. → `04-shape-elevation/01-radius-and-borders.md`.

**Непрерывные углы** (continuous corners) — термин Apple для сглаженных углов. Пример: `RoundedRectangle(style: .continuous)`. → `04-shape-elevation/`.

**Скос** (bevel) — прямой срез угла. Пример: `corner-shape: bevel` = `superellipse(0)`. → `04-shape-elevation/01-radius-and-borders.md`.

**Вогнутый угол** (scoop) — угол, выгнутый внутрь по дуге. Пример: `corner-shape: scoop` = `superellipse(-1)`. → `04-shape-elevation/01-radius-and-borders.md`.

**Вырез** (notch) — прямоугольный вырез в углу. Пример: `corner-shape: notch` = `superellipse(-∞)`. → `04-shape-elevation/01-radius-and-borders.md`.

**Библиотека форм** (shape library) — набор именованных фигур системы. Пример: Material 3 Expressive: 35 фигур. → `04-shape-elevation/`.

**Язык форм** (shape language) — согласованный набор форм, задающий характер продукта. Пример: один параметр `--radius` и множители. → `04-shape-elevation/01-radius-and-borders.md`.

**Граница** (border) — линия по периметру элемента, входит в габарит. Пример: 1 px. → `04-shape-elevation/01-radius-and-borders.md`.

**Обводка** (outline) — линия вокруг элемента, не влияющая на поток. Пример: `outline: 2px solid` + `outline-offset: 2px`. → `04-shape-elevation/01-radius-and-borders.md`.

**Кольцо** (ring) — граница, нарисованная тенью с нулевым blur. Пример: `box-shadow: 0 0 0 1px`. → `04-shape-elevation/02-shadows-layers-depth.md`; `06-components-visual/`; `09-design-tokens/`; `10-design-systems-atlas/`. В 06: обводка, нарисованная тенью `0 0 0 Npx` вместо `border`. Пример: `0 0 0 1px` у аватара. В 09 то же под именем «`shadow.ring` (кольцо, hairline ring)»: слой `0 0 0 1px` внутри тени, заменяющий границу. Применяется вместо `border`, чтобы не сдвигать раскладку (приём Primer: «used instead of a border to prevent layout shift»). В тёмной теме меняет полярность на светлый: чёрное кольцо на тёмном холсте невидимо. В режиме `forced-colors` исчезает, поэтому требует запасного `border`. В 10: слой `0 0 0 1px` внутри тени, заменяющий границу. Приём Radix (во всех шести уровнях) и Atlassian (вторая тень `0 0 1px`).

**Внутренняя тень-граница** (inset border shadow) — граница через `inset box-shadow` без сдвига раскладки. Пример: Primer `boxShadow.thin`, Polaris `shadow-border-inset`. → `04-shape-elevation/`.

**Разделитель** (divider, separator, rule) — линия между блоками или строками. Пример: 1 px, 0.66 px на HiDPI. → `04-shape-elevation/01-radius-and-borders.md`; `06-components-visual/`. В 06: линия между блоками или пунктами. Пример: 1 px, поля 4–12.

**Поле с обводкой** (outlined field) — поле ввода с границей по периметру. Пример: стандарт большинства систем. → `04-shape-elevation/`.

**Поле с заливкой** (filled field) — поле с фоновой подложкой и нижней линией. Пример: Material filled text field. → `04-shape-elevation/`.

**Высота, глубина** (elevation) — условное расстояние элемента от базовой плоскости. Пример: Material 3: 0/1/3/6/8/12 dp. → `04-shape-elevation/02-shadows-layers-depth.md`.

**Ключевая тень** (key shadow) — короткая резкая тень от направленного света. Пример: M3 level3: `0 1px 3px 0`, opacity 0.3. → `09-design-tokens/`. В 09 то же под именем «`shadow.key` (ключевой слой, key shadow, key light)»: ближний, плотный слой тени: малое смещение, малое размытие, нулевой или нулевой-отрицательный spread. Отвечает за «отрыв от плоскости». Пример: `0 1px 2px 0 rgb(2 6 24 / 0.08)`.

**Рассеянная тень** (ambient shadow) — мягкая тень от окружающего света. Пример: M3 level3: `0 4px 8px 3px`, opacity 0.15. → `09-design-tokens/`. В 09 то же под именем «`shadow.ambient` (рассеянный слой, ambient shadow, ambient light)»: дальний, диффузный слой тени: большое смещение и размытие, отрицательный spread. Отвечает за ощущение высоты. Пример: `0 4px 8px -2px rgb(2 6 24 / 0.08)`.

**Ядро тени** (umbra) — самый плотный слой тени в модели Material 2. Пример: alpha 0.2. → `04-shape-elevation/02-shadows-layers-depth.md`.

**Полутень** (penumbra) — средний слой тени в модели Material 2. Пример: alpha 0.14. → `04-shape-elevation/02-shadows-layers-depth.md`.

**Слоёная тень** (layered box-shadow) — тень из нескольких box-shadow с растущими offset и blur. Пример: 5 слоёв с alpha 0.12. → `04-shape-elevation/`.

**Контактная тень** (contact shadow) — короткая тень у самой поверхности. Пример: `0 1px 3px rgb(0 0 0 / .05)`. → `04-shape-elevation/`.

**Размытие** (blur radius) — радиус растушёвки тени. Пример: blur ≈ 2 × offset. → `04-shape-elevation/02-shadows-layers-depth.md`.

**Разброс** (spread) — расширение или сжатие тени до размытия. Пример: `-4px` поджимает, `+3px` расширяет. → `04-shape-elevation/02-shadows-layers-depth.md`.

**Тень-подсказка переполнения** (overflow shadow) — Inset-тень у края прокручиваемой области. Пример: `inset 10px 0 8px -8px` (Ant). → `04-shape-elevation/`.

**Оттенок поверхности** (surface tint) — подмешивание акцента в поверхность с ростом высоты. Пример: Material 3. → `04-shape-elevation/`.

**Скрим** (scrim, backdrop, mask, blanket) — затемняющая подложка под модалкой. Пример: `rgb(0 0 0 / .40)`. → `04-shape-elevation/02-shadows-layers-depth.md`; `01-color/`; `03-spacing-sizing/`; `05-layout-grid/`; `06-components-visual/`; `08-motion/`. В 01: затемнение под модалкой. 32–50 % чёрного в светлой теме, 60–75 % в тёмной. Polaris: 71 %. В 03: затемняющая подложка под модалкой. Пример: 32–60 % чёрного. В 05: затемнение под модальным слоем. Пример: `rgb(0 0 0 / .32)` плотный, `.48` клиентский. В 06: затемнение под модальным слоем. Пример: `rgb(0 0 0 / .32)`. В 08 то же под именем «Скрим, подложка»: затемняющий слой под модальным окном. Имеет собственные токены движения. Пример: `motion.blanket.enter` = 250 ms fade (Atlassian).

**Контекст наложения** (stacking context) — область, внутри которой действуют свои z-index. Пример: создаётся `transform`, `filter`, `opacity < 1`. → `04-shape-elevation/02-shadows-layers-depth.md`.

**Шкала z-index** (z-index scale) — набор значений слоёв в виде токенов. Пример: Bootstrap 1000–1090, MUI 1000–1500. → `04-shape-elevation/`.

**Портал** (portal) — рендер всплывающего слоя в конец документа. Пример: обходит контексты наложения. → `04-shape-elevation/02-shadows-layers-depth.md`; `06-components-visual/`. В 06: рендер оверлея вне DOM-родителя. Пример: меню, модалка.

**Размытие подложки** (backdrop-filter) — фильтр, применённый к тому, что за элементом. Пример: `blur(12px) saturate(180%)`. → `04-shape-elevation/02-shadows-layers-depth.md`.

**Подъём при наведении** (hover lift) — рост тени и сдвиг элемента при наведении. Пример: тень на уровень выше, `translateY(-1px)`. → `04-shape-elevation/02-shadows-layers-depth.md`.

**Оверлей высоты** (elevation overlay) — приём Material 2: белый с альфой поверх тёмной поверхности, 0 % при 0 dp … 16 % при 24 dp. Заменяет тени в тёмной теме. → `04-shape-elevation/`. В 04 то же под именем «Наложение высоты»: белая плёнка поверх поверхности в тёмной теме. Пример: `--mdc-elevation-overlay-opacity`.

**Морфинг формы** (shape morphing) — переход между двумя контурами. В M3 Expressive относится к spatial-пружинам. В веб-сервисах применяется редко. → `08-motion/02-what-to-animate-in-apps.md`; `04-shape-elevation/`. В 04: плавный переход одной фигуры в другую. Пример: `Morph.toPath(progress)` в Compose.

**Liquid Glass** — системный материал Apple с WWDC 2025: преломляет и отражает окружение, меняет цвет от подложки, морфится. В вебе воспроизводится частично. → `11-styles-trends/01-style-dictionary-for-quiz.md`; `04-shape-elevation/`. В 04: материал Apple (2025): прозрачность, преломление, блики. Пример: воспроизводим в вебе частично.

## 5. Сетка и раскладка

**Колоночная сетка** (column grid) — раскладка из равных колонок с промежутками, к которым выравниваются контейнеры верхнего уровня. Пример: 12 колонок (Bootstrap, Atlassian, Fluent), 16 (Carbon), 24 (Ant). → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Колонка** (column) — одна вертикальная дорожка сетки. Пример: при контейнере 1200, 12 колонках и гаттере 24 колонка = 78 px. → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Гаттер, межколонник** (gutter) — расстояние между соседними колонками. Пример: Bootstrap 24, Atlassian 12/16, Carbon wide 32 / narrow 16 / condensed 1. → `05-layout-grid/01-grids-breakpoints-containers.md`; `03-spacing-sizing/`. В 03 то же под именем «Гаттер»: расстояние между колонками сетки. Пример: Carbon 16–24, GOV.UK 30.

**Поле сетки** (margin) — расстояние от края вьюпорта до первой колонки. Пример: 16 / 24 / 32–40 по брейкпоинтам. → `05-layout-grid/05-responsive-and-overlays.md`.

**Резиновая сетка** (fluid grid) — число колонок фиксировано, ширина колонки растёт с окном. Пример: Carbon fluid. → `05-layout-grid/`.

**Фиксированная сетка** (fixed grid) — ширина блока фиксирована, число колонок растёт с окном. Пример: Carbon fixed: плитка 320 × 160. → `05-layout-grid/`.

**Гибридная сетка** (hybrid grid) — сочетание fluid и fixed в одной раскладке. Пример: Carbon hybrid. → `05-layout-grid/`.

**Ключевая линия** (key line) — видимая вертикаль или горизонталь, по которой выровнено несколько объектов. Пример: левый край контента: заголовок, тулбар, таблица, кнопки. → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Модель раскладки за максимумом** (style model) — что происходит с сеткой выше максимального брейкпоинта. Пример: Carbon: editorial (центр), product and docs (влево), high-density (вся ширина). → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Влияющий на сетку** (grid influencer) — элемент каркаса, меняющий сетку при появлении. Пример: левая навигация не меняет число колонок, выезжающая панель уменьшает. → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Вложенная сетка** (subgrid, nested grid) — дочерняя сетка внутри колонки родительской. Пример: Carbon v11 через CSS Grid. → `05-layout-grid/`.

**Модульная сетка** (modular grid) — колонки плюс ряды: матрица модулей. Пример: Fluent 2, один из четырёх типов. → `05-layout-grid/`.

**Рукописная сетка** (manuscript grid) — одна колонка для длинного текста. Пример: статья, документация. → `05-layout-grid/`.

**Брейкпоинт** (breakpoint) — ширина вьюпорта, на которой меняется раскладка. Пример: Tailwind 640 / 768 / 1024 / 1280 / 1536. → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Класс окна** (window size class) — именованный диапазон ширин. Пример: Material 3: compact < 600, medium 600–839, expanded 840–1199, large 1200–1599, extra-large ≥ 1600. → `05-layout-grid/`.

**Класс размера** (size class) — пара значений compact/regular по каждой оси (Apple). Пример: iPhone в портрете: compact × regular. → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Запрос к контейнеру** (container query) — медиазапрос по размеру родительского контейнера, а не окна. Пример: `@container panel (min-width: 400px)`. → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Тип контейнера** (container-type) — объявление контекста для container query. Пример: `inline-size` — рабочий вариант. → `05-layout-grid/`.

**Единицы контейнера** (cqw, cqi, cqb) — проценты от размеров контейнера запроса. Пример: `font-size: max(1.5em, 1.23em + 2cqi)`. → `05-layout-grid/`.

**Перетекание** (reflow) — перестроение контента без двумерной прокрутки. Пример: WCAG 1.4.10: 320 CSS px ширины, 256 высоты. → `05-layout-grid/05-responsive-and-overlays.md`.

**Пять приёмов адаптации** (reposition, resize, reflow, show/hide, re-architect) — классификация Fluent 2. Пример: reflow: 4 колонки → 2 → 1. → `05-layout-grid/05-responsive-and-overlays.md`.

**Внутренняя раскладка** (intrinsic layout) — раскладка без медиазапросов, правила задаются самим компонентом. Пример: `flex-basis: 280px; flex-grow: 999; min-inline-size: 50%`. → `05-layout-grid/`.

**Безопасная зона** (safe area) — область экрана, не перекрытая вырезом и системными полосами. Пример: `env(safe-area-inset-bottom)` ≈ 34 px на iPhone. → `05-layout-grid/`.

**Малый вьюпорт** (svh) — высота при развёрнутых панелях браузера. Пример: `max-height: 85svh` у нижнего листа. → `05-layout-grid/`.

**Большой вьюпорт** (lvh) — высота при скрытых панелях; равен `vh`. Пример: `100vh` = `100lvh`. → `05-layout-grid/`.

**Динамический вьюпорт** (dvh) — высота, меняющаяся при прокрутке. Пример: `height: 100dvh` у каркаса. → `05-layout-grid/`.

**Каркас приложения** (app shell) — постоянные зоны вокруг сменяемого контента. Пример: сайдбар + шапка + рабочая область. → `05-layout-grid/`.

**Скаффолд** (layout scaffold) — имя каркаса экрана в Material 3 (с мая 2026). → `05-layout-grid/`.

**Зоны экрана** (screen regions) — нумерованный перечень зон каркаса. Пример: Carbon: header, global sidenav, local sidenav, dropdown, content, footer, dialog. → `05-layout-grid/02-app-shells.md`.

**Баннер** (banner) — полоса над всем каркасом (объявления, окружение). Пример: Atlassian, высота по контенту. → `05-layout-grid/02-app-shells.md`.

**Боковая навигация** (sidebar, side navigation, side nav, navigation drawer) — вертикальная панель навигации слева. Пример: Atlassian 320, Polaris 240, Carbon 256, shadcn 256. → `05-layout-grid/02-app-shells.md`; `03-spacing-sizing/`. В 03 то же под именем «Сайдбар»: боковая навигационная панель. Пример: 240–280, свёрнутый 48–72.

**Панель** (pane) — одна из областей многопанельной раскладки (термин Material 3). Пример: фиксированная панель 360 dp на expanded, 412 на large. → `05-layout-grid/02-app-shells.md`.

**Рабочая область** (main, content) — основная сменяемая область. Пример: 1440 − 256 − 2 × 32 = 1120. → `05-layout-grid/02-app-shells.md`.

**Разделитель панелей** (spacer) — зазор между панелями многопанельной раскладки. Пример: Material 3: 24 dp на medium и выше. → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Гибкая панель** (flexible panel) — сворачиваемая панель фиксированной ширины (Carbon). Пример: сайдбар, сворачивающийся в рейку. → `05-layout-grid/`.

**Фиксированная панель** (fixed panel) — статичная ширина, вне резиновой сетки (Carbon). Пример: инспектор 320. → `05-layout-grid/02-app-shells.md`.

**Плавающая панель** (floating panel) — плавает над контентом, не влияет на сетку, закрывается пользователем (Carbon). Пример: панель инструментов канваса. → `05-layout-grid/`.

**Флайаут** (flyout) — временное раскрытие свёрнутого сайдбара по наведению. Пример: Atlassian, закрывается при отводе курсора. → `05-layout-grid/05-responsive-and-overlays.md`.

**Уезжающая панель** (offcanvas) — панель, сдвинутая за край окна. Пример: shadcn: `margin-left: calc(var(--sidebar-width) * -1)`. → `05-layout-grid/05-responsive-and-overlays.md`.

**Ссылка пропуска** (skip link) — первая в порядке фокуса ссылка «к основному контенту». Пример: требование Carbon UI Shell, WCAG 2.4.1. → `05-layout-grid/`.

**Канонические раскладки** (canonical layouts) — три типовые многопанельные раскладки Material 3. Пример: feed, list-detail, supporting pane. → `05-layout-grid/`.

**Мастер-детали** (list-detail, master-detail) — список слева, детали справа. Пример: список 320–400, детали остаток; M3 фиксирует 360/412 dp. → `05-layout-grid/`.

**Вспомогательная панель** (supporting pane) — основная область плюс дополняющая. Пример: «основная обычно около двух третей». → `05-layout-grid/03-page-anatomy.md`.

**Разделённые панели** (split pane) — две резиновые панели. Пример: Material 3 на medium: 50/50. → `05-layout-grid/`.

**Лента** (feed) — сетка однотипных карточек. Пример: `repeat(auto-fill, minmax(280px, 1fr))`. → `05-layout-grid/`.

**Шапка страницы** (page header) — полоса с крошками, заголовком, действиями, описанием и вкладками. Пример: ≤ 120 px суммарно. → `05-layout-grid/02-app-shells.md`.

**Панель инструментов** (toolbar) — полоса с поиском, фильтрами и переключателями вида над контентом. Пример: 48 (плотно) / 56–64 (просторно). → `05-layout-grid/01-grids-breakpoints-containers.md`.

**Контекстная полоса** (context bar) — слот шапки страницы, видимый только на узких вьюпортах (Primer). Пример: родительская ссылка + действия контекста. → `05-layout-grid/02-app-shells.md`.

**Дашборд** (dashboard) — набор визуализаций в один экран, дающий информацию с одного взгляда. Пример: NN/g; 44 % корпуса влезают без прокрутки. → `05-layout-grid/03-page-anatomy.md`.

**Операционный дашборд** (operational dashboard) — непрерывно обновляемые данные, срочные решения. Пример: мониторинг, диспетчеризация. → `05-layout-grid/`.

**Аналитический дашборд** (analytical dashboard) — сводка для анализа без срочности. Пример: продажи, посещаемость. → `05-layout-grid/`.

**Слоистая раскладка дашборда** (stratified) — виджеты сверху вниз по важности. Пример: 49 % из 144 дашбордов (Bach et al.). → `05-layout-grid/03-page-anatomy.md`.

**Сгруппированная раскладка** (grouped) — два и более виджета под общим заголовком. Пример: 33 %. → `05-layout-grid/03-page-anatomy.md`.

**Открытая раскладка** (open) — виджеты разных размеров без приоритета. Пример: 22 %. → `05-layout-grid/03-page-anatomy.md`.

**Табличная раскладка** (table (dashboard pattern)) — виджеты в осмысленных строках и колонках. Пример: 19 %. → `05-layout-grid/03-page-anatomy.md`.

**Влезает в экран** (screenfit) — дашборд помещается без прокрутки. Пример: 44 %. → `05-layout-grid/03-page-anatomy.md`.

**Переполнение** (overflow (dashboard)) — страница длиннее экрана, вертикальная прокрутка. Пример: 22 %. → `05-layout-grid/02-app-shells.md`.

**Параметризация** (parameterization) — фильтры, слайдеры, выбор периода на дашборде. Пример: 52 %. → `05-layout-grid/03-page-anatomy.md`.

**Оптическое выравнивание** (optical alignment) — выравнивание по зрительному, а не геометрическому центру. Пример: сдвиг треугольной иконки на 1–2 px. → `05-layout-grid/04-alignment-whitespace-composition.md`.

**Оптический центр** (optical center) — точка, воспринимаемая как центр; чуть выше геометрического. → `05-layout-grid/`.

**Точка высокого контраста** (high-contrast point) — граница, от которой реально отмеряется расстояние. Пример: край заливки, а не текст внутри. → `05-layout-grid/`.

**Якорный объект** (anchor object) — крупный элемент, задающий левый верхний угол блока. Пример: заголовок карточки 16 px вес 600. → `05-layout-grid/04-alignment-whitespace-composition.md`.

**Визуальный вес** (visual weight) — сила притяжения взгляда: площадь, контраст, насыщенность, вес шрифта. Пример: одно пятно первого уровня на экран. → `05-layout-grid/`.

**Ритм** (rhythm) — повтор элементов и интервалов. Пример: строки таблицы 36 через 0. → `05-layout-grid/04-alignment-whitespace-composition.md`.

**Повтор, чередование, градация** (repetition, alternation, gradation) — три способа создать ритм. Пример: одинаковые карточки; заголовок/текст; шкала кеглей. → `05-layout-grid/03-page-anatomy.md`.

**F-паттерн** (F-pattern) — сканирование «стены текста»: горизонталь, вторая короче, вертикаль слева. Пример: худший из паттернов, возникает при отсутствии зацепок. → `05-layout-grid/`.

**Слоёный пирог** (layer-cake) — сканирование по заголовкам с пропуском текста между ними. Пример: целевой паттерн интерфейса. → `05-layout-grid/`.

**Пятнистое сканирование** (spotted) — взгляд прыгает по выделенным словам и числам. → `05-layout-grid/`.

**Отметка** (marking) — взгляд удерживается в одной точке при прокрутке. Пример: чаще на мобильном. → `05-layout-grid/04-alignment-whitespace-composition.md`.

**Обход** (bypassing) — пропуск одинаковых первых слов в строках списка. Пример: «Заказ № …» игнорируется. → `05-layout-grid/04-alignment-whitespace-composition.md`.

**Диаграмма Гутенберга** (Gutenberg diagram) — схема движения взгляда от левого верха к правому низу. Пример: **не применима** к интерфейсам с иерархией. → `05-layout-grid/04-alignment-whitespace-composition.md`.

**Залежная зона** (fallow area) — угол, который по диаграмме Гутенберга получает мало внимания. Пример: правый верх — сильная, левый низ — слабая. → `05-layout-grid/04-alignment-whitespace-composition.md`.

**Сгиб** (fold) — нижняя граница первого экрана. Пример: 57 % времени просмотра выше сгиба. → `05-layout-grid/02-app-shells.md`.

**Ложное дно** (false floor) — первый экран выглядит законченным, и дальше не прокручивают. Пример: лечится обрезкой блока по краю экрана. → `05-layout-grid/04-alignment-whitespace-composition.md`.

**Нижний лист** (bottom sheet) — панель, выезжающая снизу на мобильном. Пример: `max-height: 85svh`, ручка 32–40 × 4. → `05-layout-grid/05-responsive-and-overlays.md`.

**Смещение** (offset) — расстояние от слоя до триггера. Пример: Floating UI по умолчанию 0, ставить 4–8. → `05-layout-grid/05-responsive-and-overlays.md`.

**Переворот** (flip) — перенос слоя на противоположную сторону при нехватке места. Пример: по обеим осям по умолчанию. → `05-layout-grid/05-responsive-and-overlays.md`.

**Сдвиг** (shift) — сдвиг слоя вдоль края, чтобы он влез. Пример: по главной оси по умолчанию. → `05-layout-grid/05-responsive-and-overlays.md`.

**Отступ от столкновения** (collision padding) — зазор между слоем и краем окна. Пример: Radix по умолчанию 0, ставить 8–16. → `05-layout-grid/`.

**Ширина триггера** (trigger width) — CSS-переменная с шириной элемента-триггера. Пример: `--radix-popover-trigger-width`. → `05-layout-grid/`.

**Доступная высота** (available height) — остаток до края окна, доступный слою. Пример: `--radix-popover-content-available-height`. → `05-layout-grid/`.

**Именованные области** (grid-template-areas) — декларативная запись каркаса строками-схемами. Пример: `"topbar topbar" "sidebar main"`. → `05-layout-grid/`.

**Минимакс** (minmax) — дорожка с минимальной и максимальной шириной. Пример: `minmax(280px, 1fr)`. → `05-layout-grid/06-ai-errors-and-checks.md`.

**Автозаполнение** (auto-fill) — создаёт пустые дорожки, не растягивая существующие. Пример: сетка карточек с переменным числом. → `05-layout-grid/`.

**Автоподгонка** (auto-fit) — схлопывает пустые дорожки и растягивает существующие. Пример: KPI-ряд. → `05-layout-grid/`.

**Доля свободного места** (fr) — распределяет остаток после фиксированных дорожек и зазоров. Пример: `grid-template-columns: 256px 1fr 320px`. → `05-layout-grid/`.

**Логические свойства** (logical properties) — свойства в терминах письма, а не сторон экрана. Пример: `padding-inline`, `min-inline-size`, `inset-inline-end`. → `05-layout-grid/`.

**Рельс** (rail, navigation rail) — свёрнутый сайдбар с одними иконками. Пример: Carbon 48 px. → `03-spacing-sizing/03-control-and-panel-sizes.md`; `05-layout-grid/`; `06-components-visual/`. В 05 то же под именем «Рейка»: узкая иконочная навигация. Пример: Carbon 48, Material 3 80, практика 56–72. В 06: свёрнутая боковая навигация. Пример: 48–64.

**Верхняя панель** (top bar, app bar, masthead, top nav, app header) — горизонтальная панель приложения сверху. Пример: 48–64. → `03-spacing-sizing/03-control-and-panel-sizes.md`; `05-layout-grid/`. В 05 то же под именем «Верхняя навигация»: горизонтальная полоса вверху окна. Пример: Atlassian 56, Polaris 56, Carbon 48, Ant 64.

**Панель свойств, инспектор** (inspector, properties panel, panel, side sheet) — правая панель с параметрами выбранного объекта. Пример: 280–400. → `03-spacing-sizing/03-control-and-panel-sizes.md`; `05-layout-grid/`; `06-components-visual/`. В 05 то же под именем «Правая панель»: панель свойств выбранного объекта. Пример: Atlassian 365, Primer 256/296/320, M3 side sheet max 400. В 06 то же под именем «Инспектор»: правая панель свойств. Пример: 280–400.

**Липкая область** (sticky header, sticky, sticky region) — шапка, тулбар или футер, закреплённые при прокрутке. Пример: `position: sticky; top: 0`. → `03-spacing-sizing/`; `05-layout-grid/`. В 03 то же под именем «Липкая шапка»: закреплённая шапка таблицы или страницы. Пример: тень появляется при скролле. В 05 то же под именем «Прилипание»: закрепление элемента при прокрутке. Пример: Primer: панель `sticky; top: var(--offset-header); max-height: 100vh` от 768 px.

**Сдвиг раскладки** (cumulative layout shift, layout shift, CLS) — скачок контента из-за того, что место под картинку не зарезервировано. Лечится `aspect-ratio` и атрибутами `width`/`height`. → `07-iconography-imagery/02-illustration-system-avatars-images.md`; `02-typography/`; `08-motion/`. В 02 то же под именем «CLS»: накопленный сдвиг вёрстки; подмена шрифта — одна из причин. В 08: скачок контента из-за изменения размеров. `clip-path` и `transform` его не вызывают, `height` вызывает.

**Оптическая поправка** (optical correction) — отступление от математики ради восприятия. Пример: круг в keyline-сетке на 11 % больше квадрата; иконка опускается на 11.5 % кегля к базовой линии текста. → `06-components-visual/`; `07-iconography-imagery/`. В 06 то же под именем «Оптическая коррекция»: сдвиг на 1–2 px для выравнивания по восприятию. Пример: чекбокс в ячейке: `translate-y-[2px]`. В 07 то же под именем «Оптическая коррекция»: локальное отступление от сетки ради читаемости. Пример: штрих 1.5 dp вместо 2 у иконки скрепки в Material.

## 6. Компоненты и состояния

**Анатомия компонента** (anatomy) — перечень частей компонента с их размерами и отступами. Пример: кнопка: контейнер, ведущая иконка, лейбл, замыкающая иконка. → `06-components-visual/`.

**Контейнер** (container) — внешний бокс компонента, несущий высоту, фон, границу и радиус. Пример: высота 32, радиус 6, граница 1 px. → `06-components-visual/03-tables-and-lists.md`.

**Замыкающий визуал** (trailing visual) — иконка справа: шеврон, внешняя ссылка, счётчик, шорткат. Пример: шеврон 16. → `05-layout-grid/`. В 05: статус или признак приватности справа от заголовка. Пример: бейдж 20–24.

**Лейбл** (label) — подпись элемента: текст кнопки, подпись поля, заголовок колонки. Пример: 14/20/500. → `06-components-visual/02-forms-and-inputs.md`.

**Плейсхолдер** (placeholder) — текст-пример внутри пустого поля. Пример: `#6a7282`, 4.84:1 к белому. → `06-components-visual/02-forms-and-inputs.md`.

**Подсказка** (helper text, hint) — пояснение под полем. Пример: 12/16, `--text-muted`. → `06-components-visual/02-forms-and-inputs.md`.

**Текст ошибки** (error text) — сообщение о неверном значении под полем. Пример: 12/16, `--danger-text`. → `06-components-visual/`.

**Слот** (slot) — место внутри контейнера под произвольный элемент (иконку, кнопку). Пример: ширина = высоте поля − 2. → `06-components-visual/02-forms-and-inputs.md`.

**Префикс / суффикс** (prefix / suffix) — неинтерактивный текст или иконка внутри поля. Пример: «₽», отступ 12 / 6. → `06-components-visual/`.

**Индикатор** (indicator) — полоса, точка или галочка, показывающая состояние. Пример: индикатор вкладки 2–3 px. → `06-components-visual/04-navigation-and-surfaces.md`.

**Ручка** (thumb, handle) [также: переключателя] — подвижный кружок внутри трека. Пример: 16 при треке 36 × 20. → `06-components-visual/02-forms-and-inputs.md`.

**Трек** (track) — дорожка переключателя, слайдера или прогресса. Пример: 36 × 20; прогресс 8. → `06-components-visual/04-navigation-and-surfaces.md`.

**Ручка дровера** (drag handle) — полоска для захвата нижнего дровера. Пример: 32 × 5, зона 44. → `06-components-visual/`.

**Зебра** (zebra striping) — чередование фона строк таблицы. Пример: `#fafafa`, ΔL 1.5 п.п. → `06-components-visual/03-tables-and-lists.md`.

**Иконочная кнопка** (icon button) — квадратная кнопка без текста. Пример: 32 × 32, глиф 16. → `06-components-visual/01-buttons-and-actions.md`.

**Разделённая кнопка** (split button) — основное действие + отдельный триггер меню. Пример: 32 + 24, разделитель 1 px. → `06-components-visual/`.

**Сегментированный переключатель** (segmented control) — ряд взаимоисключающих кнопок в общем треке. Пример: трек 36, padding 3. → `06-components-visual/04-navigation-and-surfaces.md`.

**Группа кнопок** (button group) — ряд связанных кнопок. Пример: зазор 8 либо слитно. → `06-components-visual/01-buttons-and-actions.md`.

**Чип** (chip) — компактный элемент выбора или фильтра. Пример: 32, иконка 18. → `06-components-visual/05-feedback-and-overlays.md`.

**Тег** (tag) — метка объекта, часто с крестиком. Пример: 24, padding 0 × 8, радиус 16. → `06-components-visual/`.

**Бейдж** (badge) — статус или счётчик. Пример: 20, padding 2 × 8. → `06-components-visual/05-feedback-and-overlays.md`.

**Точка-статус** (status dot) — кружок, показывающий состояние. Пример: 6–8, кольцо 2 px. → `06-components-visual/`.

**Комбобокс** (combobox) — поле с выпадающим списком и вводом. Пример: поле 32, список 240. → `06-components-visual/`.

**Селект** (select, picker) — поле выбора из списка. Пример: шеврон 16, `padding-right: 32`. → `06-components-visual/07-states-matrix.md`.

**Дата-пикер** (date picker) — календарь для выбора даты. Пример: ячейка 40 × 40, календарь 288. → `06-components-visual/`.

**Слайдер** (slider) — выбор значения на шкале. Пример: трек 4, ручка 16–20. → `06-components-visual/02-forms-and-inputs.md`.

**Поле тегов** (tag input, token field) — поле, где значения становятся тегами. Пример: min-height 44 / 56. → `06-components-visual/02-forms-and-inputs.md`.

**Зона загрузки** (dropzone) — область для перетаскивания файлов. Пример: пунктир 1–2 px, max-width 320. → `06-components-visual/02-forms-and-inputs.md`.

**Тултип** (tooltip) — всплывающая подсказка по наведению. Пример: 12 px, padding 4 × 8, max 240. → `06-components-visual/05-feedback-and-overlays.md`; `03-spacing-sizing/`; `05-layout-grid/`. В 03: короткая подсказка при наведении. Пример: max-width 240–320, padding 6–8 × 8–12. В 05: подсказка по наведению. Пример: `max-width` 240–320, задержка 300–500 мс.

**Карточка по наведению** (hover card) — поповер, открывающийся по наведению. Пример: 280–320, задержка 300–700 мс. → `06-components-visual/`.

**Алерт** (alert, banner, callout) — постоянное сообщение в потоке. Пример: padding 12–16, иконка 16. → `06-components-visual/05-feedback-and-overlays.md`.

**Скелетон** (skeleton) — заглушка формы контента при загрузке. Пример: строка 12–16, радиус 4. → `06-components-visual/06-data-display-and-misc.md`.

**Спиннер** (spinner) — индикатор неопределённой загрузки. Пример: 16 в кнопке, 800 мс. → `06-components-visual/06-data-display-and-misc.md`.

**Степпер** (stepper) — индикатор шагов процесса. Пример: кружок 32, точка 8. → `06-components-visual/06-data-display-and-misc.md`.

**KPI-плитка** (metric card, stat tile) — карточка с одним числом. Пример: значение 28–32/600. → `06-components-visual/`.

**Спарклайн** (sparkline) — микрографик без осей. Пример: высота 32–48. → `06-components-visual/06-data-display-and-misc.md`.

**Клавиша** (kbd) — изображение клавиши в тексте. Пример: 0.75em, radius 0.35em. → `06-components-visual/06-data-display-and-misc.md`.

**Хлебные крошки** (breadcrumbs) — путь по иерархии. Пример: высота 32–40, разделитель поля 8. → `06-components-visual/04-navigation-and-surfaces.md`.

**Первичная** (primary, filled) — главное действие, сплошная заливка акцентом. Пример: `bg-accent`, белый текст. → `06-components-visual/01-buttons-and-actions.md`.

**Вторичная** (secondary, default) — второе по важности действие. Пример: белая с границей или мягкая заливка. → `06-components-visual/01-buttons-and-actions.md`.

**Третичная** (tertiary, subtle, ghost) — прозрачная кнопка, фон появляется при наведении. Пример: hover α 4–5 %. → `06-components-visual/01-buttons-and-actions.md`.

**Текстовая** (text, plain, link) — только текст, без фона и границ. Пример: подчёркивание при hover. → `06-components-visual/02-forms-and-inputs.md`.

**Контурная** (outlined) — прозрачный фон, видимая граница. Пример: граница 1 px. → `06-components-visual/02-forms-and-inputs.md`.

**Тональная** (tonal, soft) — мягкая заливка акцентом. Пример: `accent-a3`. → `06-components-visual/01-buttons-and-actions.md`.

**Деструктивная** (destructive, danger, critical) — необратимое действие. Пример: красный текст или заливка. → `06-components-visual/05-feedback-and-overlays.md`.

**Инверсная** (inverse) — светлое на тёмном (тултип, тост). Пример: `gray-12` фон, `gray-1` текст. → `06-components-visual/05-feedback-and-overlays.md`.

**Плотный режим** (compact, condensed) — вариант с уменьшенными отступами. Пример: строка 32, padding 8. → `06-components-visual/03-tables-and-lists.md`.

**Просторный режим** (spacious, comfortable) — вариант с увеличенными отступами. Пример: строка 48, padding 16. → `06-components-visual/03-tables-and-lists.md`.

**Заливной вариант поля** (filled) — поле с фоном и нижней границей. Пример: Carbon `$field`. → `06-components-visual/02-forms-and-inputs.md`.

**Подчёркнутый вариант** (underline) — поле только с нижней границей. Пример: Fluent `underline`. → `06-components-visual/`.

**Плавающий лейбл** (floating label) — подпись внутри поля, поднимающаяся при вводе. Пример: Material. → `06-components-visual/`.

**Блочная кнопка** (block button) — кнопка во всю ширину контейнера. Пример: `width: 100%`. → `06-components-visual/`.

**Покой** (rest, default, enabled) — исходное состояние. → `06-components-visual/07-states-matrix.md`.

**Наведение** (hover) — указатель над элементом. Пример: ΔL 2–6 п.п., α 4–5 %. → `06-components-visual/07-states-matrix.md`.

**Нажатие** (active, pressed) — момент нажатия. Пример: ΔL 5–9 п.п., α 8 %. → `06-components-visual/07-states-matrix.md`.

**Фокус** (focus) — элемент получил фокус. Пример: кольцо 2 px. → `06-components-visual/07-states-matrix.md`.

**Фокус внутри** (focus-within) — фокус на потомке контейнера. Пример: показ кнопки очистки. → `06-components-visual/`.

**Выбрано** (selected) — устойчивый выбор строки, вкладки, пункта. Пример: фон `accent-a8` + второй признак. → `06-components-visual/07-states-matrix.md`.

**Отмечено** (checked) — состояние чекбокса, радио, переключателя. Пример: заливка акцентом. → `06-components-visual/07-states-matrix.md`.

**Раскрыто** (expanded) — открытый триггер меню или аккордеона. Пример: `[aria-expanded='true']` = active. → `06-components-visual/07-states-matrix.md`.

**Неопределённое** (indeterminate) — частичный выбор в группе чекбоксов. Пример: горизонтальная черта 8–10 × 2. → `06-components-visual/02-forms-and-inputs.md`.

**Отключено** (disabled) — недоступно для взаимодействия. Пример: APCA Lc 30–45. → `06-components-visual/07-states-matrix.md`.

**Только чтение** (readonly) — значение показано и копируется, но не меняется. Пример: граница прозрачная. → `06-components-visual/02-forms-and-inputs.md`.

**Ошибка** (invalid, error) — значение не прошло проверку. Пример: граница + иконка + текст. → `06-components-visual/07-states-matrix.md`.

**Предупреждение** (warning) — значение допустимо, но требует внимания. Пример: граница `warning`. → `06-components-visual/05-feedback-and-overlays.md`.

**Загрузка** (loading, busy) — операция выполняется. Пример: спиннер 16, ширина сохранена. → `06-components-visual/07-states-matrix.md`.

**Перетаскивание** (dragged) — элемент тащат. Пример: слой 16 % (Material). → `06-components-visual/07-states-matrix.md`.

**Зона вставки** (drop target) — куда упадёт элемент. Пример: линия 2 px акцентом. → `06-components-visual/`.

**Посещено** (visited) — ссылка уже открывалась. Пример: фиолетовый в контентных разделах. → `06-components-visual/07-states-matrix.md`.

**Устойчиво нажато** (pressed (toggle)) — кнопка-переключатель во включённом виде. Пример: `bg-fill-selected`. → `06-components-visual/07-states-matrix.md`.

**Дельта состояния** (state delta) — насколько меняется светлота между состояниями. Пример: hover −4 п.п. L. → `06-components-visual/`.

**Альфа-слой** (alpha layer) — полупрозрачная нейтраль поверх фона. Пример: 4 % чёрного → `#f5f5f5`. → `06-components-visual/`.

**Смещение кольца** (outline-offset) — зазор между элементом и кольцом. Пример: 2 снаружи, −1 внутрь. → `06-components-visual/`.

**Зона захвата** (hit area) — невидимое расширение цели нажатия. Пример: `::before` 44 × 44. → `06-components-visual/`.

**Компенсация иконки** (icon padding compensation) — уменьшение padding при наличии иконки. Пример: 16 → 12. → `06-components-visual/`.

**Множитель ширины** (width multiplier) — минимальная ширина как доля высоты. Пример: кнопка 2.25 ×, поле 1.5 ×. → `06-components-visual/`.

**Усечение** (truncation) — обрезка текста с многоточием. Пример: `text-overflow: ellipsis`. → `06-components-visual/03-tables-and-lists.md`.

**Резервирование места** (space reservation) — место под элемент, который может появиться. Пример: `min-height` строки ошибки. → `06-components-visual/`.

**Порядок разделения** (separation order) — отступ → линия → фон → тень. Пример: карточка админки: граница. → `06-components-visual/04-navigation-and-surfaces.md`.

**Парные тона** (paired tones) — светлая и плотная версия одного статуса. Пример: Polaris `tone` / `tone-strong`. → `06-components-visual/`.

**Граница тенью** (shadow border) — граница, нарисованная `box-shadow: inset 0 0 0 1px`. Пример: Radix, Polaris. → `06-components-visual/`.

**Невидимая граница** (invisible border) — граница цвета фона, чтобы высота не менялась при подсветке. Пример: Carbon `border-block-start`. → `06-components-visual/03-tables-and-lists.md`.

**Заливка тенью** (shadow fill) — анимируемая заливка через `inset 0 0 0 32px`. Пример: чекбокс Polaris. → `06-components-visual/`.

**Сетка из трёх зон** (three-area grid) — `grid-template-areas: 'lead text trail'` у кнопки. Пример: Primer. → `06-components-visual/`.

**Скрытие лейбла при загрузке** (label hiding) — `visibility: hidden` вместо `display: none`. Пример: Primer loading. → `06-components-visual/`.

**Авторост поля** (auto-grow) — `field-sizing: content` у textarea. Пример: shadcn. → `06-components-visual/`.

**Отрицательное поле слота** (negative slot margin) — прижатие слота к границе поля. Пример: Radix `Slot`. → `06-components-visual/`.

**Маска-шиммер** (shimmer mask) — анимированная маска для скелетона и прогресса. Пример: Primer, Ant. → `06-components-visual/`.

**Ripple без JS** (CSS ripple) — `outline: 0.5em` при `pointer: coarse`. Пример: Radix. → `06-components-visual/`.

**Container queries** — перестроение набора кнопок по ширине контейнера. Пример: Carbon ButtonSet. → `06-components-visual/01-buttons-and-actions.md`.

**Слой состояния** (state layer, state layers) — полупрозрачный слой цвета `on-<container>` поверх контейнера. Material v0.192: hover 0.08, focus 0.12, pressed 0.12, dragged 0.16. → `01-color/05-states-and-interaction.md` §1.2; `04-shape-elevation/`; `06-components-visual/`. В 04: полупрозрачный слой поверх элемента для hover/pressed. Пример: M3: hover 0.08, pressed 0.12. В 06 то же под именем «Подложка состояния»: полупрозрачный слой поверх контейнера, дающий hover и pressed. Пример: Material: 8 %, 12 %. В 06 то же под именем «Слои состояний»: модель Material: фиксированные альфы на все компоненты. Пример: 0.08 / 0.12 / 0.12 / 0.16.

**Фокус-ринг** (focus ring, focus indicator) — визуальный индикатор клавиатурного фокуса. 2 px толщина, 2 px offset, ≥ 3:1 к обоим соседним цветам. Реализуется через `outline`, а не `box-shadow`. → `04-shape-elevation/`; `06-components-visual/`. В 04 то же под именем «Индикатор фокуса»: видимая рамка у элемента с клавиатурным фокусом. Пример: 2 px, offset 2 px, контраст 3:1. В 06 то же под именем «Кольцо фокуса»: видимый индикатор фокуса. Пример: 2 px, offset 2, ≥ 3:1.

**Двойной ринг** (double ring, two-color focus indicator) — обводка из двух контрастных линий (тёмная + светлая), работает на любом фоне; так делают современные Chrome и Edge. → `01-color/05-states-and-interaction.md`; `04-shape-elevation/`; `06-components-visual/`. В 04 то же под именем «Двухцветное кольцо»: индикатор из светлой и тёмной части для любого фона. Пример: GOV.UK: жёлтый фон + чёрная полоса 4 px. В 06 то же под именем «Двойное кольцо»: тёмное + светлое кольцо для любого фона. Пример: Chrome, Cal.com, Plausible.

**Каретка** (caret) — курсор ввода; `caret-color`. → `01-color/05-states-and-interaction.md`; `06-components-visual/`. В 06: курсор ввода в поле. Пример: `caret-color: var(--text)`.

**Дровер** (drawer, side panel, sheet) — выезжающая панель поверх контента. Пример: 400–560 или 40 % ширины. → `03-spacing-sizing/03-control-and-panel-sizes.md`; `05-layout-grid/`; `06-components-visual/`. В 05 то же под именем «Дровер, выезжающая панель»: панель, выезжающая с края экрана. Пример: 400–560 или `min(560px, 40vw)`. В 06: панель, выезжающая с края. Пример: 480; нижний с ручкой.

**Выпадающее меню** (dropdown menu) — список действий, привязанный к кнопке. Пример: 160–280, пункт 32. → `06-components-visual/`. В 06: список действий. Пример: min-width 160, пункт 32.

**Видимый фокус** (`:focus-visible`, focus-visible) — псевдокласс, срабатывающий при клавиатурной навигации. Пример: заменяет `:focus` для колец. → `06-components-visual/`. В 06: фокус, показываемый при клавиатурной навигации. Пример: `:focus-visible`.

**Ведущий визуал** (leading visual) — иконка или аватар слева от заголовка страницы; виден на всех вьюпортах. Пример: 16–32. → `06-components-visual/`. В 06: иконка, аватар или индикатор слева от текста. Пример: иконка 16, зазор 8.

**Пустое состояние** (empty state) — экран без данных с объяснением и действием. Пример: блок 320–400, иллюстрация 96–160, текст ≤ 420. → `05-layout-grid/03-page-anatomy.md`; `06-components-visual/`. В 06: экран без данных. Пример: иллюстрация ≤ 160, текст ≤ 420.

**Модальное окно** (modal, dialog) — блокирующий слой поверх страницы. Пример: 400 / 560–640 / 800–960, `max-width: calc(100vw − 32px)`. → `05-layout-grid/05-responsive-and-overlays.md`; `06-components-visual/`. В 06 то же под именем «Модалка»: слой, блокирующий работу с фоном. Пример: 400 / 560 / 880.

**Поповер** (popover) — неблокирующий слой, привязанный к триггеру. Пример: 240–320, отступ 4–8. → `05-layout-grid/05-responsive-and-overlays.md`; `03-spacing-sizing/`; `06-components-visual/`. В 03: всплывающий блок, привязанный к триггеру. Пример: 240–320. В 06: всплывающая панель с содержимым. Пример: 288, padding 16.

**Тост** (toast, snackbar) — временное уведомление в углу экрана. Пример: 320–400, отступ от края 16–24. → `05-layout-grid/05-responsive-and-overlays.md`; `03-spacing-sizing/`; `06-components-visual/`. В 03 то же под именем «Тост, снэкбар»: временное уведомление. Пример: ширина 320–400. В 06: временное уведомление в углу. Пример: 356, 4 с.

**Командная палитра** (command palette) — поиск по командам, открываемый с клавиатуры. Пример: 560–640, сверху 10–20 % (практика). → `05-layout-grid/05-responsive-and-overlays.md`; `06-components-visual/`. В 06: поиск по действиям с клавиатуры. Пример: 560–640, радиус 12.

**Плейсхолдер** (placeholder) — заглушка тех же габаритов на время загрузки: скелетон, доминирующий цвет, BlurHash. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

## 7. Иконки и изображения

**Иконка интерфейса** (UI icon) — монохромный знак размером 12–32 px, обозначающий действие, объект или статус. Пример: 16 × 16 со штрихом 2 при исходном холсте 24. → `07-iconography-imagery/01-icons.md`.

**Холст, кадр** (canvas, frame, trim area) — квадрат, в котором рисуется иконка; за него не выходит ничто. Пример: 24 × 24 dp у Material и Lucide, 15 × 15 у Radix. → `07-iconography-imagery/01-icons.md`.

**Живая область** (live area) — внутренняя область холста, где размещается основной рисунок. Пример: 20 × 20 внутри 24 у Material, 22 × 22 у Lucide. → `07-iconography-imagery/01-icons.md`.

**Защитная зона** (safe zone, padding) — поле между живой областью и краем холста. Пример: 2 dp у Material, 1 px у Lucide. → `07-iconography-imagery/01-icons.md`.

**Keyline-формы, ключевые формы** (keyline shapes, key shapes) — эталонные фигуры, задающие оптический вес набора: круг, квадрат, вертикальный и горизонтальный прямоугольники. Пример у Material: круг ⌀ 20, квадрат 18 × 18, прямоугольники 20 × 16 и 16 × 20. → `07-iconography-imagery/`.

**Первичная и вторичная сетки** (primary grid, secondary grid) — units и subunits внутри кадра. Пример: 24-сетка Material — вторичная при первичной 12. → `07-iconography-imagery/`.

**Оптический вес** (optical weight) — воспринимаемая плотность знака. Проверяется размытием рядом с эталонными кругом и квадратом набора. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Овершут** (overshoot) — намеренное увеличение круглых форм, чтобы они не казались меньше квадратных. Пример: круг 20 против квадрата 18, то есть +11 %. → `07-iconography-imagery/01-icons.md`.

**Штрих** (stroke, stroke-width) — толщина линии иконки. Пример: 2 px у Lucide при 24, 1.5 у Heroicons 24/outline и Iconoir. → `07-iconography-imagery/01-icons.md`.

**Терминал штриха** (stroke terminal, line cap) — окончание открытой линии: round, butt или square. Пример: round у Lucide и Heroicons, **квадратные у Material**. → `07-iconography-imagery/`.

**Соединение линий** (line join) — стык двух сегментов: round, miter, bevel. Пример: round у Lucide. → `07-iconography-imagery/`.

**Контрштрих, внутренняя форма** (counter stroke, counter area) — просвет внутри знака. Пример: минимум 2 px между различимыми элементами у Lucide. → `07-iconography-imagery/`.

**Переменный шрифт-иконки** (variable icon font) — набор, реализованный как переменный шрифт с осями. Пример: Material Symbols с осями weight 100–700, fill 0–1, grade −25…+200, optical size 20–48. → `07-iconography-imagery/`.

**Grade** — ось тонкой подстройки веса, слабее влияющая на габариты, чем weight. Пример: grade −25 для светлой иконки на тёмном фоне, компенсация «visual bleed». → `07-iconography-imagery/01-icons.md`.

**Fill** — ось или вариант заливки, передающий состояние. Пример: активный пункт навигации fill 1, остальные fill 0. → `07-iconography-imagery/01-icons.md`.

**Масштаб SF Symbols** (scale: small, medium, large) — три ступени относительно cap height системного шрифта San Francisco, меняющие акцент без нарушения совпадения веса с текстом. → `07-iconography-imagery/`.

**Режим отрисовки** (rendering mode) — у SF Symbols: monochrome, hierarchical, palette, multicolor. → `07-iconography-imagery/`.

**`currentColor`** — значение CSS, позволяющее иконке наследовать цвет текста. Пример: `<svg stroke="currentColor">`. → `07-iconography-imagery/01-icons.md`.

**Спрайт** (SVG sprite) — один файл с набором `<symbol>`, из которого иконки подключаются через `<use href="#id">`. → `07-iconography-imagery/`.

**Шрифтовая иконка** (icon font) — иконки, поставленные как глифы шрифта. Наследие; проигрывает SVG в чёткости и доступности. → `07-iconography-imagery/`.

**Пиктограмма** (pictogram) — знак крупнее иконки и проще иллюстрации, от 48 px. Пример: IBM Pictogram Library, минимум 48 px, клиренс 1/4 сетки. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**directionType** — поле метаданных Fluent, указывающее, зеркалится ли иконка в RTL (`mirror`) или нет (`unique`). → `07-iconography-imagery/`.

**Система иллюстраций** (illustration system) — набор правил, делающих серию картинок узнаваемо одной: палитра, свет, ракурс, линия, детализация, персонажи, фон, размеры. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Паспорт системы** — заполняемый шаблон этих правил, фиксируемый до генерации первой картинки. Пример — `02-illustration-system-avatars-images.md` §3. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Spot-иллюстрация** (spot illustration) — небольшая картинка, передающая один концепт. Пример: 120–160 px в пустом состоянии. У Atlassian существует в цветной и нейтральной версиях. → `07-iconography-imagery/`.

**Hero-иллюстрация** (hero illustration) — крупная картинка, задающая тон экрану. Пример: 240–320 px на странице ошибки. → `07-iconography-imagery/`.

**Low-fidelity UI** — схематичное изображение интерфейса из простых фигур и серых тонов вместо скриншота. Применяется в онбординге и турах. → `07-iconography-imagery/`.

**Ambient pattern** (фоновый паттерн) — текстура, задающая атмосферу без конкретного образа. Пример: фон промо-блока у Atlassian. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Screen-within-screen** — антипаттерн: скриншот интерфейса внутри самого интерфейса. → `07-iconography-imagery/`.

**Плоская перспектива** (flat perspective) — отсутствие схождения линий; вся площадь картинки равнозначна. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Изометрия** (isometric projection) — объём без перспективы, обычно под 30°. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Corporate Memphis** (он же Alegria, Humaaans style) — стиль плоских безликих персонажей с удлинёнными конечностями, массовый в 2018–2022. Сегодня читается как штамп. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**3D clay** — стиль мягких пластилиновых объёмов со скруглёнными формами и рассеянным светом. → `07-iconography-imagery/`.

**Векторизация** (vectorization, image trace) — перевод растровой картинки в векторный контур. Инструменты: Recraft, Illustrator Image Trace, vtracer. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Дрейф стиля** (style drift) — расхождение параметров между картинками одной серии при генерации: толщина линии, палитра, свет, пропорции. → `07-iconography-imagery/`.

**Аватар** (avatar) — изображение, представляющее пользователя или сущность. Размеры: 16, 24, 32, 40, 48, 64. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Инициалы** (initials, monogram) — 1–2 буквы на цветной плашке вместо фотографии. Кегль ≈ 40 % размера аватара. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Хеш-цвет** (hashed color) — детерминированный выбор фона из палитры по идентификатору пользователя. Пример: 8–10 оттенков, контраст текста ≥ 4.5:1. → `07-iconography-imagery/`.

**Индикатор присутствия** (presence indicator) — точка состояния «на месте / отошёл / занят / не беспокоить». Ставится снизу-справа. Пример: 12 px на аватаре 24. → `07-iconography-imagery/`.

**Индикатор статуса** (status indicator) — знак дополнительного смысла (одобрено, ошибка). Ставится сверху-справа. → `07-iconography-imagery/`.

**Группа аватаров, стопка** (avatar group, avatar stack) — перекрывающиеся аватары участников. Наложение −8 px, обводка 2 px цветом фона, счётчик `+N` после 3–5. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Обводка аватара** (avatar border) — кольцо цветом подложки, отделяющее аватар от соседей. Ширина 2 px. → `07-iconography-imagery/`.

**Соотношение сторон** (aspect ratio) — пропорция кадра. Пример: 16:9, 4:3, 1:1; в CSS `aspect-ratio: 16 / 9`. → `05-layout-grid/`. В 05 то же под именем «Соотношение сторон блока»: пропорция плитки сетки. Пример: Carbon: 1:1, 2:1, 2:3, 3:2, 4:3, 16:9.

**`object-fit`** — правило вписывания картинки в бокс: `cover` (заполнить с обрезкой), `contain` (вписать целиком). → `07-iconography-imagery/`.

**`object-position`** — точка кадрирования. Пример: `center` по умолчанию, `top` для портретов. → `07-iconography-imagery/`.

**BlurHash / LQIP** (low quality image placeholder) — компактное размытое представление картинки, показываемое до загрузки оригинала. → `07-iconography-imagery/`.

**Ленивая загрузка** (lazy loading) — `loading="lazy"` для изображений ниже первого экрана. → `07-iconography-imagery/`.

**Приглушение в тёмной теме** (dimming) — снижение яркости фотографий на 10–20 % через `filter: brightness()` или наложение слоя. → `07-iconography-imagery/`.

**Images of text** — картинки, содержащие текст. Не читаются скринридером, не переводятся, не масштабируются; допустимы только когда текст essential. → `07-iconography-imagery/`.

**Safe zone** (защитное поле логотипа) — минимальный отступ вокруг знака. Пример: не менее половины высоты знака. → `07-iconography-imagery/01-icons.md`.

**Локап** (lockup) — фиксированная композиция знака и надписи. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Монохромный вариант** — одноцветная версия логотипа для тёмной темы и печати. → `07-iconography-imagery/`.

**Оптическое выравнивание логотипов** — нормализация по площади, а не по высоте, при показе логотипов разных брендов в одном ряду. → `07-iconography-imagery/`.

**Эмодзи** (emoji) — символы Unicode, отрисовываемые шрифтом ОС. Допустимы в пользовательском контенте, запрещены как иконки интерфейса. → `07-iconography-imagery/02-illustration-system-avatars-images.md`.

**Эмодзи-стек** — `font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji"` для контейнеров с эмодзи. → `07-iconography-imagery/`.

**MIT, ISC, Apache 2.0** — свободные лицензии без обязательной атрибуции в интерфейсе. Пример: Lucide (ISC), Heroicons, Tabler, Phosphor, Iconoir, Radix (MIT), Material Symbols (Apache 2.0). → `07-iconography-imagery/`.

**CC BY 4.0** — свободная лицензия **с обязательной атрибуцией**. Пример: иконки Font Awesome Free. → `07-iconography-imagery/`.

**Запрет на обработку моделями ИИ** (AI/ML training prohibition) — новый тип ограничения: лицензия unDraw прямо запрещает подавать иллюстрации в модели. Проверяется **до** того, как ассет попадёт в промт генератора изображений. → `07-iconography-imagery/`. В 07 то же под именем «Запрет на обучение ИИ»: пункт лицензии, запрещающий использовать ресурсы как обучающий или референсный материал для моделей. Пример: unDraw.

**CC0** — отказ от прав: можно всё, включая обработку моделью. Так лицензированы Humaaans и Open Peeps. → `07-iconography-imagery/`. В 07: передача в общественное достояние без условий. Пример: Humaaans, Open Peeps.

**SIL OFL** — лицензия шрифтов (в частности Geist): свободное использование, но с условиями на переиздание и переименование. → `07-iconography-imagery/`. В 07 то же под именем «SIL OFL 1.1»: лицензия для шрифтов, включая шрифтовые иконки.

## 8. Движение

**Движение** (motion) — визуальное изменение состояния интерфейса во времени. В отличие от «анимации» как жанра, движение в UI служебно: объясняет, что изменилось и откуда взялось. Пример: поповер вырастает из кнопки за 150 ms. → `08-motion/03-reduced-motion-and-motion-tokens.md`.

**Переход** (transition) — изменение свойства от одного значения к другому за заданное время по заданной кривой. В CSS прерываем: при смене цели плавно уходит к новому значению. Пример: `transition: opacity 150ms cubic-bezier(0,0,0.2,1)`. → `08-motion/02-what-to-animate-in-apps.md`.

**Анимация по ключевым кадрам** (keyframe animation) — движение, заданное набором состояний в процентах от длительности. В CSS не прерывается. Пример: `@keyframes spin { to { transform: rotate(360deg) } }`. → `08-motion/`.

**Длительность** (duration) — время перехода. Основная единица — миллисекунда. Пример: 150 ms (дефолт Tailwind, Carbon, Atlassian). → `08-motion/03-reduced-motion-and-motion-tokens.md`.

**Задержка** (delay) — пауза перед началом перехода. Отдельное свойство `transition-delay`. Пример: 300 ms на выходе меню, чтобы оно не гасло при случайном уводе курсора. → `08-motion/03-reduced-motion-and-motion-tokens.md`.

**Кривая, функция плавности** (easing function, timing function) — зависимость прогресса от времени. Задаётся `cubic-bezier()`, `linear()` или ключевыми словами. Пример: `cubic-bezier(0.4, 0, 0.2, 1)`. → `08-motion/01-durations-easings-springs.md`.

**Кубическая кривая Безье** (cubic-bezier) — кривая по четырём числам `[P1x, P1y, P2x, P2y]`; x в диапазоне [0, 1], y произвольный. Пример: `cubic-bezier(0, 0, 0.2, 1)` — ease-out Material 2. → `08-motion/`.

**Перелёт** (overshoot) — проскок цели с последующим возвратом. В кривой Безье это y > 1, в пружине — ζ < 1. Пример: `cubic-bezier(0.12, 0.4, 0.29, 1.46)` у Ant Design, перелёт до 146 %. → `08-motion/01-durations-easings-springs.md`.

**Подсед** (undershoot, anticipation) — отступ в противоположную сторону перед движением. В кривой это y < 0. Пример: `cubic-bezier(0.71, −0.46, 0.88, 0.6)` у Ant Design. → `08-motion/01-durations-easings-springs.md`.

**Замедление, вход** (decelerate, entrance, ease-out) — резкий старт, мягкое торможение. Для появляющихся элементов. Пример: `cubic-bezier(0, 0, 0.2, 1)`. → `08-motion/01-durations-easings-springs.md`.

**Ускорение, выход** (accelerate, exit, ease-in) — мягкий старт, уход «в стену». Для исчезающих насовсем элементов. Пример: `cubic-bezier(0.4, 0, 1, 1)`. → `08-motion/01-durations-easings-springs.md`.

**Стандартная** (standard, ease-in-out) — симметричная; для элементов, которые видны от начала до конца и перемещаются внутри экрана. Пример: `cubic-bezier(0.4, 0, 0.2, 1)`. → `08-motion/01-durations-easings-springs.md`.

**Линейная** (linear) — постоянная скорость; только для циклов: спиннер, прогресс, шиммер. Пример: `linear` у `animate-spin`. → `08-motion/01-durations-easings-springs.md`.

**Emphasized** — усиленная кривая Material 3 для крупных акцентных переходов. На Android это составной путь из двух кривых, в CSS не переводится: документация M3 честно пишет «N/A (Use Standard as a fallback)». → `08-motion/01-durations-easings-springs.md`.

**Bold против practical** (Atlassian) — драматичная и повседневная кривые. Пример: ease-out bold `cubic-bezier(0, 0.4, 0, 1)` для входа панели, ease-out practical `cubic-bezier(0.4, 1, 0.6, 1)` для hover. → `08-motion/01-durations-easings-springs.md`.

**Пружина** (spring) — модель движения через физику, а не через время: параметры задают силу, а длительность получается сама. Пример: `{mass: 1, stiffness: 380, damping ratio: 0.8}`. → `08-motion/01-durations-easings-springs.md`.

**Жёсткость** (stiffness, tension) — сила возврата пружины. Чем выше, тем быстрее и резче. Пример: 1400 у M3 standard fast spatial. → `08-motion/01-durations-easings-springs.md`.

**Демпфирование** (damping, friction) — сила торможения. Пример: коэффициент затухания ζ = 0.9 у standard-схемы M3. → `08-motion/01-durations-easings-springs.md`.

**Коэффициент затухания** (damping ratio, ζ) — безразмерная мера демпфирования. ζ = 1 — критическое затухание без перелёта; ζ < 1 — колебания с перелётом; ζ > 1 — вялый подход без перелёта. Пример: ζ = 0.6 у M3 expressive fast spatial даёт перелёт 9.5 %. → `08-motion/`.

**Масса** (mass) — инерция объекта. Обычно 1. Пример: `{mass: 1.75, tension: 200, friction: 12}` у Comeau. → `08-motion/01-durations-easings-springs.md`.

**Собственная частота** (natural frequency, ω_n) — `√(k/m)`, определяет темп. Пример: k = 380, m = 1 → ω_n = 19.5 рад/с. → `08-motion/`.

**Воспринимаемая длительность** (perceptual duration) — параметр пружины у Apple: «approximately equal to the settling duration, but for very bouncy springs, will be the duration of the period of oscillation». Пример: 0.5 s у всех трёх системных пружин SwiftUI. → `08-motion/01-durations-easings-springs.md`.

**Bounce** — параметр Apple, равный `1 − ζ` для недодемпфированных пружин. Пример: `smooth` 0, `snappy` 0.15, `bouncy` 0.3. → `08-motion/01-durations-easings-springs.md`.

**Spatial и effects** (M3 Expressive) — две категории пружин: пространственные (меняют форму или положение) и эффекты (цвет, прозрачность). Effects всегда ζ = 1.0, то есть не пружинят. Пример: default spatial ζ 0.8 / k 380, default effects ζ 1.0 / k 1600. → `08-motion/01-durations-easings-springs.md`.

**`linear()`** — CSS-функция кусочно-линейной интерполяции, позволяющая записать пружину без JS. Baseline с декабря 2023. Пример: `linear(0, 0.036, 0.124, …, 1)` из 24–75 точек. → `08-motion/01-durations-easings-springs.md`.

**Reversing shortening factor** — правило спецификации CSS Transitions, пропорционально сокращающее длительность прерванного перехода. Причина, по которой `linear()`-пружина плохо ведёт себя на прерываниях: пружина на 1600 ms может перезапуститься за 400 ms. → `08-motion/01-durations-easings-springs.md`.

**Прерываемость** (interruptibility) — возможность прервать движение новым действием без ожидания конца. Свойство `transition` и JS-пружин; у `@keyframes` отсутствует. → `08-motion/01-durations-easings-springs.md`.

**Origin-aware появление** — рост элемента из точки привязки, а не из центра. Реализуется через `transform-origin`. Пример: `--radix-popover-content-transform-origin`. → `08-motion/`.

**Стаггер** (stagger) — последовательные задержки у элементов серии. Пример: 20 ms на элемент, суммарно не более 500 ms (Carbon). → `08-motion/03-reduced-motion-and-motion-tokens.md`.

**Хореография** (choreography) — согласование нескольких одновременных движений: порядок, пути, задержки. Пример: порядок появления контента у Carbon из пяти категорий. → `08-motion/02-what-to-animate-in-apps.md`.

**Движение от действия** (action-driven motion) — разные настройки перехода на вход и на выход состояния. Пример: hover кнопки 125 ms на приход курсора, 450 ms на уход (Comeau). → `08-motion/`.

**FLIP** (First, Last, Invert, Play) — приём анимации перестановки: измерить позиции до и после, применить обратный `transform`, снять его с переходом. Даёт анимацию раскладки без анимации layout-свойств. → `08-motion/`.

**Шиммер** (shimmer) — бегущая или пульсирующая подсветка скелетона. Пример: `pulse 2s cubic-bezier(0.4,0,0.6,1) infinite`, keyframes `50% { opacity: 0.5 }`. → `08-motion/03-reduced-motion-and-motion-tokens.md`.

**Подсветка изменившегося** (flash, highlight-on-change) — короткая заливка элемента после внешнего обновления. Пример: затухание 1000–2000 ms. → `08-motion/02-what-to-animate-in-apps.md`.

**Композитный слой** (compositing layer) — слой, который GPU двигает без перерисовки. Свойства, не выходящие за пределы композитинга: `transform`, `opacity`. → `08-motion/`.

**Layout, paint, composite** — три шага рендера. `width`/`height`/`top` задевают все три, `background-color` — два, `transform`/`opacity` — один. → `08-motion/02-what-to-animate-in-apps.md`.

**Бюджет кадра** (frame budget) — 16.6 ms при 60 fps. → `08-motion/`.

**`will-change`** — подсказка браузеру, что элемент будет анимироваться; удерживает его на GPU и включает субпиксельный рендер. Цена — память GPU на каждый слой. → `08-motion/`.

**Субпиксельный рендер** (sub-pixel rendering) — плавное смещение между пикселями. Доступен `transform`, недоступен `margin`/`top`. → `08-motion/`.

**`@starting-style`** — блок начальных стилей для элементов, появляющихся из `display: none` или в top layer. Baseline 2024. → `08-motion/`.

**`transition-behavior: allow-discrete`** — разрешает переход дискретных свойств (`display`, `overlay`), чтобы выход элемента был виден. → `08-motion/`.

**`overlay`** — свойство, отвечающее за присутствие элемента в top layer; включается в список переходов, чтобы удаление отложилось до конца анимации. → `08-motion/02-what-to-animate-in-apps.md`.

**View Transitions API** — браузерный механизм переходов между состояниями документа или между документами. `document.startViewTransition()` (SPA) и `@view-transition { navigation: auto }` (MPA). → `08-motion/`.

**Scroll-driven animations** — привязка прогресса анимации к прокрутке (`animation-timeline: scroll()` / `view()`). В веб-сервисах почти не применимо. → `08-motion/`.

**`clip-path`** — обрезка элемента геометрической фигурой. Аппаратно ускоряется, не влияет на раскладку. Пример: `inset(0 0 100% 0) → inset(0)` для раскрытия изображения. → `08-motion/`.

**`prefers-reduced-motion`** — медиа-фича, сообщающая о настройке ОС «сократить анимацию». Значения `no-preference` и `reduce`. Baseline с января 2020. → `08-motion/`.

**`prefers-reduced-transparency`** — то же для прозрачности; при `reduce` снимается `backdrop-filter`. → `08-motion/`.

**Reduce, not remove** — принцип: пространственное движение заменяется непространственным (затухание, цвет), а не отключается полностью. → `08-motion/03-reduced-motion-and-motion-tokens.md`.

**Вестибулярный триггер** (vestibular trigger) — движение, вызывающее головокружение и тошноту. Три фактора: доля экрана, рассогласование направления и скорости, пройденная дистанция. → `08-motion/02-what-to-animate-in-apps.md`.

**Change blindness** — неспособность заметить изменение, произошедшее мгновенно. Одна из причин, по которой движение полностью убирать нельзя. → `08-motion/03-reduced-motion-and-motion-tokens.md`.

**WCAG 2.3.3 Animation from Interactions** — уровень AAA: анимацию, запущенную действием пользователя, можно отключить. → `08-motion/`.

**WCAG 2.2.2 Pause, Stop, Hide** — уровень A: у движения, запущенного автоматически и идущего дольше 5 секунд параллельно с другим контентом, должен быть контрол паузы. → `08-motion/`.

**WCAG 2.3.1 Three Flashes** — уровень A: не более трёх вспышек в секунду. → `08-motion/`.

**Токен длительности** (duration token) — в DTCG объект `{value: number, unit: "ms" | "s"}`. Пример: `{"value": 150, "unit": "ms"}`. → `08-motion/`.

**Токен кривой** (cubicBezier token) — массив из четырёх чисел. Пример: `[0, 0, 0.2, 1]`. → `08-motion/`.

**Составной токен перехода** (transition token) — `{duration, delay, timingFunction}`. Пример: `motion.transition.popupEnter`. → `08-motion/`.

**Семантический токен движения** — токен, названный по назначению, а не по значению. Пример: `motion.popup.enter.top` (Atlassian). → `08-motion/`.

**Токен-keyframe** — именованный набор ключевых кадров, вынесенный в систему токенов. Пример: `motion.keyframe.scale.in.small` = 95 → 100 % (Atlassian), `--p-keyframes-bounce` (Polaris). → `08-motion/`.

**`motionUnit`** — множитель скорости всего продукта. Пример: 0.1 s у Ant Design, от него считаются Fast/Mid/Slow. → `08-motion/01-durations-easings-springs.md`.

## 9. Токены и темы

**Дизайн-токен** (design token) — именованное решение о визуальном свойстве, хранимое отдельно от кода компонента. Термин ввёл Salesforce в 2014 (Jina Anne). Пример: `space.md` = 16px. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Примитив** (primitive, reference token, global token, base token, seed) — точка шкалы без смысла: `primitive.color.accent.600` = `#155dfc`, `primitive.size.16` = 16px. Имя описывает значение. → `09-design-tokens/04-reference-token-schema.md`; `01-color/`. В 01: точка шкалы без смысла: `blue-600`, `neutral.9`, `primary40`. Компоненты их НЕ используют.

**Семантический токен** (semantic token, system token, alias, alias token, functional token) — роль в интерфейсе: `color.bg.canvas`, `space.inset.card`. Имя описывает назначение, значение — ссылка на примитив. → `09-design-tokens/01-architecture-and-naming.md`; `01-color/`; `03-spacing-sizing/`. В 01 то же под именем «Семантический алиас»: роль в интерфейсе: `--color-accent-solid`, `fgColor.muted`, `--md-sys-color-primary`. В 03: токен роли, ссылающийся на значение шкалы. Пример: `--space-card-padding: var(--space-5)`.

**Компонентный токен** (component token) — значение, принадлежащее одному компоненту: `button.primary.background`. Заводится, когда значение нужно трём и более компонентам, — до этого живёт в коде компонента. → `09-design-tokens/01-architecture-and-naming.md` §1.4.; `09-design-tokens/05-anti-patterns-and-pipeline.md`; `01-color/`; `06-components-visual/`. В 01: значение одного компонента: `$button-primary-hover`, `--color-input-border`. В 06: токен, привязанный к части компонента и состоянию. Пример: `button.primary.bg.hover`.

**Контекстный токен** (contextual token) — токен, значение которого подставляется в рантайме по месту в дереве: `$layer` у Carbon без номера, значение определяется глубиной вложенности `<Layer>`. В DTCG не выражается. → `09-design-tokens/03-theming-and-modes.md` §4.2.; `01-color/`. В 01: термин Carbon: значение подставляется в зависимости от слоя, на котором находится компонент. `$layer` без номера против `$layer-02`.

**Псевдотокен** (pseudo-token) — переменная уровня компонента, указывающая на токен системы и скрытая от публикации. Приём Uber: компонент параметризован, словарь системы не растёт. → `09-design-tokens/05-anti-patterns-and-pipeline.md` §1.1..

**Алиас** (alias, reference) — значение токена в виде ссылки на другой токен: `"$value": "{primitive.color.accent.600}"`. Ссылаться можно только на токен целиком, не на группу. → `09-design-tokens/01-architecture-and-naming.md`.

**Мёртвый токен** (dead token) — токен, на который никто не ссылается. Дефект: занимает место в словаре, который читают человек и модель. → `09-design-tokens/05-anti-patterns-and-pipeline.md`.

**DTCG** (Design Tokens Community Group, W3C DTCG format) — рабочая группа W3C и её формат описания токенов. Стабильная версия — Design Tokens Format Module **2025.10**, Final Community Group Report от 28.10.2025. → `09-design-tokens/02-dtcg-format-and-tooling.md`; `01-color/`; `12-ai-generated-ui/`. В 01 то же под именем «Design Tokens (W3C DTCG)»: формат описания токенов; поддерживается на выходе Leonardo. Подробности — папка `09-design-tokens/`. В 12 то же под именем «Формат токенов W3C»: стандарт обмена дизайн-токенами. Пример: версия 2025.10; DESIGN.md экспортирует в него.

**Design Tokens Format Module** — основной модуль формата: `$value`, `$type`, `$description`, `$extensions`, `$deprecated`, группы, алиасы, базовые и составные типы. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Color Module** — модуль формата про цвет: 14 цветовых пространств, `colorSpace`, `components`, `alpha`, шестизначный `hex`, ключевое слово `none`. → `09-design-tokens/01-architecture-and-naming.md`.

**Resolver Module** — модуль формата про темы: `sets`, `modifiers`, `contexts`, `resolutionOrder`. Отдельный файл `.resolver.json`. → `09-design-tokens/03-theming-and-modes.md` §2.; `09-design-tokens/02-dtcg-format-and-tooling.md`.

**`$value`** — зарезервированное свойство, делающее объект токеном. Объект без `$value` — группа. → `09-design-tokens/04-reference-token-schema.md`.

**`$type`** — тип токена; наследуется от ближайшей родительской группы. Если не определён нигде, токен невалиден; инструменты не имеют права угадывать тип по значению. → `09-design-tokens/04-reference-token-schema.md`.

**`$extensions`** — объект с произвольными метаданными; ключи в обратной доменной нотации (`org.primer.llm`). Инструменты обязаны сохранять расширения, которых не понимают. → `09-design-tokens/04-reference-token-schema.md`.

**`$deprecated`** — пометка «устарел»: `true`, строка-объяснение или `false` (перебивает значение группы). → `09-design-tokens/05-anti-patterns-and-pipeline.md`.

**`$root`, `$extends`, `$ref`** — свойства из черновика 2026 года (корневой токен группы, наследование группы, JSON Pointer). Реализовывать пока нельзя. → `09-design-tokens/04-reference-token-schema.md`.

**Составной тип** (composite type) — тип, значение которого объект из нескольких подзначений: `typography`, `shadow`, `border`, `transition`, `gradient`, `strokeStyle`. → `09-design-tokens/`.

**`dimension`** — тип размера; значение — объект `{value, unit}` с единицей `px` или `rem`. Единица обязательна даже при нуле. Единиц `em` и `%` в типе нет. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Двойной узел** (double node) — узел, который одновременно токен и группа (`background` плюс `background.hover`). По спецификации 2025.10 — ошибка; используется Carbon и Panda CSS; в черновике 2026 легализуется через `$root`. → `09-design-tokens/`.

**Тема** (theme) — набор значений, связанный с брендом, продуктом или заказчиком. Ортогональна режиму: каждому бренду нужны и светлый, и тёмный режим. → `09-design-tokens/04-reference-token-schema.md`.

**Режим** (mode) — контекст внутри одной оси: `light` / `dark`, `compact` / `comfortable`, `normal` / `increased` контраст. → `09-design-tokens/04-reference-token-schema.md`.

**Ось темизации** (axis, modifier) — независимое измерение вариативности: бренд, режим цвета, контраст, плотность, платформа. Хранить надо оси, а не их произведение. → `09-design-tokens/`.

**Set** [также: набор] — в резолвере: коллекция токенов без вариантов. Конфликт внутри набора решается «побеждает последний». → `09-design-tokens/`.

**Modifier** [также: модификатор] — в резолвере: ось с двумя и более контекстами. Не может ссылаться на другой модификатор. → `09-design-tokens/03-theming-and-modes.md`.

**`resolutionOrder`** — порядок наложения наборов и модификаторов; позднее перебивает раннее. → `09-design-tokens/03-theming-and-modes.md`.

**Ортогональность** (orthogonality) — свойство осей трогать непересекающиеся множества токенов. Рекомендация резолвера; при пересечении обязателен явный приоритет. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Комбинаторный взрыв** (combinatorial explosion) — рост числа наборов как произведения контекстов всех осей. 5 брендов × 2 режима × 2 контраста × 3 плотности = 60 против 12 при хранении по осям. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Слой поверхности** (surface layer) — уровень «высоты» фона: холст → поверхность → всплывающая поверхность. Material: пять контейнеров, Carbon: `layer.01–03`, эталонная схема: три плюс `subtle`. → `09-design-tokens/`.

**Namespace** — префикс системы в имени токена: `md-`, `slds-`, `g-`. Нужен, когда на странице живут две системы. → `09-design-tokens/01-architecture-and-naming.md`.

**Category / concept / property / variant / state / scale / mode** — части имени по модели Nathan Curtis. Пример разложения: `color` (category) + `action` (concept) + `background` (property) + `primary` (variant) + `hover` (state). → `09-design-tokens/`.

**Полиерархия** (polyhierarchy) — принадлежность одного решения двум наборам («error red» — и статус, и цвет текста контрола). Решается сохранением обоих имён и алиасом между ними. → `09-design-tokens/01-architecture-and-naming.md`.

**Полнота** (completeness) — свойство набора содержать все нужные роли. Не означает, что каждое имя должно содержать все части: `shape-tile-corner-radius-default-on-light` — антипример. → `09-design-tokens/01-architecture-and-naming.md`.

**Scoping** — ограничение, в каких свойствах переменная предлагается (Figma, `org.primer.figma.scopes`). В CSS аналога нет. → `09-design-tokens/01-architecture-and-naming.md`.

**`codeSyntax`** — поле Primer с готовой строкой для вставки в код: `var(--fgColor-default) /* utility class: .color-fg-default */`. → `09-design-tokens/01-architecture-and-naming.md`.

**Style Dictionary** — компилятор токенов (Amazon, Danny Banks). С версии 4 понимает DTCG; формат 2025.10 поддержан не полностью («work in progress in v5»). → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Terrazzo** (бывший Cobalt) — компилятор токенов с командами `tz check`, `tz build`, `tz bundle`. Заявляет полную поддержку формата; резолверы обещаны в 2.0. Умеет раскладывать цвет по гамутам. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Tokens Studio** — плагин Figma; его формат `$themes.json` + `$metadata.json` стал де-факто стандартом обмена наборами. Resolver Module вырос из их модели. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Figma Variables** — модель переменных Figma: четыре типа (Color, Number, String, Boolean), коллекции, режимы, scoping, лимит 5000 переменных на коллекцию. Составных типов нет. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Penpot tokens** — реализация DTCG в открытом редакторе; добавляет арифметику в значениях (17 функций) и модель sets / themes. → `09-design-tokens/`.

**Panda CSS** — CSS-in-JS-движок с разделением `tokens` и `semanticTokens`; режим записан внутрь значения (`base` / `_dark`). → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Open Props** — набор готовых CSS-переменных-примитивов без семантики и компонентов. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**`@theme`** — директива Tailwind v4, объявляющая переменные, порождающие utility-классы. Модификатор `inline` подставляет значение ссылки, а не саму ссылку, и без него тема не переключается. → `09-design-tokens/04-reference-token-schema.md`.

**Пространство имён Tailwind** (namespace) — префикс переменной темы, определяющий, какие утилиты она порождает: `--color-*`, `--text-*`, `--spacing-*`, `--radius-*`, `--shadow-*`, `--breakpoint-*`, `--ease-*` и другие. → `09-design-tokens/01-architecture-and-naming.md`.

**Трансформ** (transform) — функция Style Dictionary, меняющая имя или значение токена при выводе: `name/kebab`, `size/pxToRem`, `color/css`. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**Permutation** — в Terrazzo: одна комбинация контекстов резолвера, выводимая в собственный CSS-селектор. → `09-design-tokens/02-dtcg-format-and-tooling.md`.

**`outputReferences`** — режим компилятора, при котором семантический токен выводится как `var(--примитив)`, а не как готовое значение. Требует переобъявления всей цепочки в блоках режимов. → `09-design-tokens/04-reference-token-schema.md`.

**Правило трёх компонентов** — значение становится общим токеном, когда его используют три и более компонента. → `09-design-tokens/05-anti-patterns-and-pipeline.md`.

**Закон убывающей отдачи** (Nathan Curtis) — чем больше компонентов в системе, тем выше стоимость каждого следующего и ниже его ценность. → `09-design-tokens/01-architecture-and-naming.md`.

**Бритва Оккама для систем** — число компонентов, цветов, стилей текста и теней должно быть необходимым минимумом. → `09-design-tokens/`.

**Магическое значение** (magic value) — размер или цвет, записанный литералом в компоненте вместо токена. → `09-design-tokens/`.

**`usage` / `rules` / `doNotUse` / `alternatives`** — поля расширения с правилами применения токена для языковой модели. Формат `org.primer.llm` у GitHub Primer; в эталонной схеме — `org.ui-research.llm`. → `09-design-tokens/`.

**Модальность правила** — три уровня в тексте `rules`: `MUST use for…` (нарушение ломает доступность), `RECOMMENDED default for…` (выбор по умолчанию), `Use for…` (обычное применение); запрет — `Do NOT use for…` с причиной. → `09-design-tokens/`.

**Инлайн-тема** (inline theming) — кусок страницы в другой теме (шелл или боковая панель в тёмной при светлой основной). Термин Carbon. → `01-color/02-semantic-roles-and-architecture.md`; `09-design-tokens/`. В 09 то же под именем «Inline theming»: рендер куска страницы в другой теме (`<Theme theme="g100">` у Carbon). Оговорка документации: только для крупных сдвигов цвета.

**Шкала** (scale, ramp) — упорядоченный ряд значений одной категории. Сравнивать шкалы разных систем можно только по значениям, не по номеру шага: `space-400` у Polaris = 16px, `spacing-04` у Carbon = 12px, `space.400` у Atlassian = 32px. → `10-design-systems-atlas/02-system-profiles.md`; `01-color/`; `09-design-tokens/`. В 01: упорядоченный набор оттенков одного цвета. Tailwind 11 шагов (50–950), Radix 12 (1–12), Geist 10, Polaris 16, Primer 14/10, Material 13 тонов. В 09: упорядоченный ряд значений. Пять видов: enumerated (1, 2, 3), ordered (50…900), bounded (`slate-42`), proportion (`2-x`), t-shirt (s, m, l).

## 10. Дизайн-системы и измерения

**Декларация** (declared value) — значение, которое система объявляет в документации или, что надёжнее, в исходниках. В атласе колонка «декларация». Правило приоритета: если документация и исходник расходятся, верен исходник, а расхождение отмечается. → `10-design-systems-atlas/01-atlas-table.md`.

**Практика** (measured value) — значение, снятое с живого экрана через `getComputedStyle`. В атласе колонка «практика». Показывает **применение токена на конкретном экране, а не сам токен**: продукт может объявлять `--radius: 10px` и рисовать карточки `rounded-xl`, тогда измерение даст 14. → `10-design-systems-atlas/01-atlas-table.md`.

**Мода** (mode) — самое частое значение в выборке. В атласе чаще полезна моды, чем среднее: «высота кнопки 32 у 8 продуктов из 24» информативнее, чем «в среднем 34.7». → `10-design-systems-atlas/04-live-products-measured.md`.

**По продуктам против по вхождениям** — два способа считать. «По продуктам» даёт один голос с продукта (n = 24) и показывает решения дизайнеров; «по вхождениям» считает каждый элемент на всех экранах и показывает, что человек реально видит, но смещено в сторону мелких повторяющихся элементов. → `10-design-systems-atlas/`.

**Прочерк `—`** — в таблицах атласа означает «не собрано в этой работе», а не «отсутствует». «Нет» означает, что параметра в системе нет. → `10-design-systems-atlas/`.

**Дизайн-система** (design system) — набор токенов, компонентов, правил и документации, выпускаемый как продукт для других продуктов. → `10-design-systems-atlas/02-system-profiles.md`.

**Набор примитивов** (primitive set) — токены без семантики и без компонентов: Tailwind v4, Open Props. Основа под собственную систему, но не система. → `10-design-systems-atlas/01-atlas-table.md`.

**Библиотека поведения** (headless, unstyled primitives) — компоненты без визуала: Radix Primitives, React Aria, Ark UI. Дают фокус, клавиатуру, порталы и ARIA, не навязывая эстетики. → `10-design-systems-atlas/`.

**Копируемые компоненты** (copy-in components) — компоненты, которые не ставятся пакетом, а копируются в репозиторий проекта и дальше правятся как свой код: shadcn/ui. → `10-design-systems-atlas/`.

**Движок токенов** (token engine) — инструмент, превращающий описание токенов в CSS или JS: Panda CSS, Style Dictionary, Terrazzo. → `10-design-systems-atlas/`.

**Витрина** (showcase, playground) — страница, где показаны все варианты компонента сразу. В измерениях витрины смещают статистику: у playground Radix Themes 18 кеглей, 17 радиусов и 25 теней на одном экране. → `10-design-systems-atlas/04-live-products-measured.md`.

**Единый ряд размеров** (single size ramp) — подход Polaris: одна шкала обслуживает отступы, размеры и ширины; остальные категории выводятся из неё алиасами. → `10-design-systems-atlas/`.

**Полушаг** (nudge) — промежуточная ступень шкалы отступов между основными: `sNudge` 6 и `mNudge` 10 у Fluent 2. → `10-design-systems-atlas/01-atlas-table.md`.

**Алиас-назначение** (purpose alias) — токен, фиксирующий конкретное решение: `space-card-padding` = `space-400` у Polaris, `space.inset.table-cell-x` в эталонной схеме. → `10-design-systems-atlas/`.

**Кусочно-линейная шкала** (piecewise scale) — шкала, выведенная функцией с разными правилами на разных участках: `genRadius` у Ant Design сжимает мелкую часть шкалы радиусов, чтобы маленькие элементы не выглядели переокруглёнными. → `10-design-systems-atlas/`.

**Фасет имени** (name facet) — часть имени токена как поле объекта, а не как сегмент строки: у Adobe Spectrum имя токена — объект `{property, size, structure, density, scale…}`. → `10-design-systems-atlas/`.

**Модель слоёв** (layering model) — способ показать «высоту» поверхности. Три встреченных варианта: уровни контейнера (Material, пять), нумерованные слои (Carbon, три плюс контекстные токены), светлота поверхностей без границ и теней (Linear, по публикации). → `10-design-systems-atlas/03-choosing-a-base.md`.

**Тонирование нейтрали** (neutral tint) — ненулевая хрома у серых. В практике медиана 0.004–0.019 OKLCH, оттенок всегда синий (H 244–286); тёплых нейтралей в выборке из 24 продуктов нет ни одной. → `10-design-systems-atlas/01-atlas-table.md`.

**`getComputedStyle`** — итоговые вычисленные стили элемента. Проценты, `em` и `rem` в них уже разрешены в px, поэтому `padding: 0.75rem` попадает в выборку как 12. → `10-design-systems-atlas/`.

**Кратность 4** (4× coverage) — доля значений `padding` + `gap`, кратных четырём. Читать эту метрику без объявленной шкалы продукта нельзя: у GitLab она 38.7 %, потому что 2 и 6 px — штатные значения его шкалы Pajamas. → `10-design-systems-atlas/02-system-profiles.md`.

**Симуляция дальтонизма** (CVD simulation) — пересчёт цвета по модели Viénot–Brettel–Mollon для протанопии, дейтеранопии и тританопии. → `10-design-systems-atlas/`.

**BSD 3-Clause** — лицензия токенов Salesforce Lightning: требует сохранять уведомление об авторских правах. → `10-design-systems-atlas/`.

**Productive против expressive** (Carbon) — две «личности» движения: рабочая (незаметная, для задач) и выразительная (для смены контекста, уведомлений). Пример: productive standard `cubic-bezier(0.2, 0, 0.38, 0.9)`, expressive standard `cubic-bezier(0.4, 0.14, 0.3, 1)`. → `08-motion/01-durations-easings-springs.md`; `07-iconography-imagery/`. В 07: две личности знаков: рабочая (простая, для большинства случаев) и выразительная (градиенты, слои, прозрачность, применяется выборочно).

## 11. Стили и арт-дирекция

**Арт-дирекция** (art direction) — управление визуальным впечатлением продукта: какие приёмы применяются, с какой силой и где. Отвечает на вопрос «что мы делаем и чего не делаем», а не «какие значения». Пример: «один акцент, тёплая нейтраль, серифные заголовки, никаких градиентов». → `07-iconography-imagery/`. В 07: управление визуальным языком серии: что изображаем, как и чем это ограничено.

**Визуальный язык** (visual language) — набор повторяющихся решений (цвет, форма, типографика, движение), по которому продукт узнаётся. Пример: у Vercel — чёрно-белая сетка линиями 1 px без скруглений и теней. → `11-styles-trends/02-style-tiles-and-character-knobs.md`; `07-iconography-imagery/`. В 07: согласованный набор форм, цветов и приёмов, по которому узнаётся продукт.

**Бриф** (brief) — словесная постановка: предмет, аудитория, главная задача экрана, ограничения. Для генеративного конвейера — три прилагательных плюс тип продукта. Пример: «строгий, плотный, технический; внутренняя админка биллинга». → `11-styles-trends/04-anti-slop-ui.md`.

**Мудборд** (moodboard) — подборка референсов, отвечающая на вопрос «на что это похоже». Для агента полезен только как источник **словесного описания**. Пример описания: «split-screen, заголовки капсом гротеском, монохром с одним акцентом». → `11-styles-trends/02-style-tiles-and-character-knobs.md`; `07-iconography-imagery/`; `12-ai-generated-ui/`. В 07: подборка референсов без привязки к интерфейсу. В 12: набор изображений как источник стиля, без текстового описания. Пример: функция Moodboards в Midjourney.

**Style tile** [также: плитка стиля] — артефакт между мудбордом и макетом: шрифты, цвета и элементы интерфейса **без раскладки**. Термин выбран как отсылка к cascading stylesheets. Пример: один экран с палитрой, двумя гарнитурами, кнопкой, полем, карточкой и отчётом контраста. → `11-styles-trends/02-style-tiles-and-character-knobs.md`; `07-iconography-imagery/`; `12-ai-generated-ui/`. В 07: промежуточный артефакт между мудбордом и макетом: шрифты, цвета и элементы интерфейса без раскладки. Автор понятия — Samantha Warren. В 12 то же под именем «Стилевая плитка»: промежуточный артефакт между мудбордом и макетом: палитра, шрифты, атомы UI. Пример: `../11-styles-trends/02` §2.

**Component style guide** [также: гид по компонентам] — проведение стиля через функциональность без рисования целых страниц; промежуточный шаг между плиткой и дизайн-системой. → `11-styles-trends/`.

**Ручка характера** (character knob, character knobs) — параметр, меняющий впечатление, не меняя структуры системы. Семь штук: акцент, нейтраль, радиус, плотность, шрифт, тени, тема. Пример: `radius = 6`. → `12-ai-generated-ui/`. В 12 то же под именем «Семь ручек характера»: акцент, нейтраль, радиус, плотность, шрифт, тени, тема. Пример: `../11-styles-trends/02` §3.

**Фирменный приём** (signature move) — один узнаваемый визуальный жест поверх конвенций. Пример: тень-подложка `0 2px 0` под кнопкой; кольцо вместо тени на hover у GitHub. → `11-styles-trends/`.

**Шкала точности артефактов** (fidelity scale) — мудборд → style tile → макет. Плитка применяется, когда мудборд слишком расплывчат, а макет слишком буквален. → `11-styles-trends/`.

**Catalog of assumptions** — формулировка Ethan Marcotte про статические макеты в адаптивном процессе: макет фиксирует допущения о ширине и устройстве, которых может не быть. → `11-styles-trends/02-style-tiles-and-character-knobs.md`.

**Плоский дизайн** (flat design) — отсутствие глянца и трёхмерных эффектов; сплошные заливки. Происхождение: Microsoft Metro, 2011. Пример палитры: `#3498db`, `#ecf0f1`, `#2c3e50`. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Flat 2.0** (semi flat, almost flat, flatty) — плоская основа плюс тонкие тени, подсветки и слои. Термин NN/g (2015) и Erik Kennedy («flatty», 2014). Пример: карточка на границе 1 px, тень только на оверлее. → `11-styles-trends/`.

**Скевоморфизм** (skeuomorphism) — копирование материала и устройства физического прототипа **ради метафоры**. Пример: полка из дерева в Kindle Fire. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Реализм** (realism) — те же текстуры, но **без метафоры**, ради эстетики. Отличие от скевоморфизма сформулировано NN/g. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Неоморфизм** (neumorphism, soft UI) — элементы выдавлены из фона двумя тенями противоположных направлений; фон и элемент одного цвета. Декабрь 2019, Michal Malewicz. Пример: `6px 6px 12px #bec3c9, -6px -6px 12px #ffffff`. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Клейморфизм** (claymorphism) — «надутые» объёмные формы: две внутренние тени плюс одна большая внешняя, скругление больше 50 %. 2021–2022, тот же автор. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Стеклянный стиль** (glassmorphism, frosted glass) — полупрозрачные панели с размытой подложкой и светлой обводкой. В дизайн-системах называется материалом: Acrylic (Fluent), Material (SwiftUI). Пример: белый 72 % + `blur(16px) saturate(180%)`. → `11-styles-trends/01-style-dictionary-for-quiz.md`; `04-shape-elevation/`. В 04 то же под именем «Стекло»: полупрозрачная поверхность с размытием подложки. Пример: фон 72 % + blur 12 px.

**Бенто** (bento grid) — сетка разновеликих скруглённых плиток, каждая с одной мыслью. Пример: gap 16, радиус 20, 12 колонок. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Брутализм** (brutalism) — сырой, неукрашенный интерфейс: голый HTML, синие ссылки, моноширинный текст. Пример: Craigslist, Drudge Report. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Антидизайн** (antidesign) — намеренно уродливый и дезориентирующий интерфейс без визуальной иерархии. Отличается от брутализма целью; оправдан только для аудитории дизайнеров или в развлечении. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Необрутализм** (neobrutalism, neubrutalism) — толстые границы, жёсткие тени без размытия, яркие плоские цвета, крупная «неотполированная» типографика. Пример: `box-shadow: 4px 4px 0 #000`. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Швейцарский стиль** (Swiss style, International Typographic Style) — модульная сетка, гротеск, асимметрия, минимум декора. 1950–60-е; Ernst Keller, Josef Müller-Brockmann. → `11-styles-trends/`.

**Журнальный стиль** (editorial) — приёмы печатной вёрстки в интерфейсе: серифные заголовки, длинная колонка, тёплая бумажная нейтраль. Пример: Notion, Substack. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Минимализм** (minimalism) — стратегия упрощения через удаление элементов, не поддерживающих задачу пользователя. Относится к контенту и раскладке; flat относится к текстурам и графике. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Material Design** — дизайн-система Google; M3 (2021) — тональные контейнеры и динамические палитры; **M3 Expressive** (2025) — намеренно «громкие» формы, размеры и движение. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Material theming** — механизм внедрения бренда в Material, придуманный как ответ на то, что система сделала приложения похожими (признание Google, 2019). → `11-styles-trends/`.

**«Плотный тёмный инструмент»** — линия продуктов 2021–2026 (Linear, Vercel, Raycast, Warp): тёмный фон L 14–18 %, границы через альфу, радиус 4–8, кегль 13–14, глубина светлотой. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**«Stripe-стиль»** — светлый, щедрый, чёткий: белый фон, синеватая нейтраль, синий акцент, мягкие тени. → `11-styles-trends/`.

**«shadcn по умолчанию»** — нейтрали с нулевой хромой, `--radius: 0.625rem` (10 px), `--primary` = `#171717`. → `11-styles-trends/`.

**Корпоративная классика** — Carbon, Fluent, Lightning, Ant: нулевые или малые радиусы, отсутствие теней на контенте, один синий акцент, очень высокая плотность. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Millennial grey of UI** — публичное прозвище обесцвеченных интерфейсов 2024–2026; из комментариев к видео о «правильном» цвете. → `11-styles-trends/`.

**Слоп в интерфейсе** (AI slop) — визуальный результат, в котором ни одно решение не было принято: каждое поле заполнено наиболее вероятным значением. «Design with no author». Слово года Macquarie 2025. → `11-styles-trends/01-style-dictionary-for-quiz.md`; `12-ai-generated-ui/`. В 12 то же под именем «Нейрослоп»: сгенерированный результат, узнаваемый по набору дефолтных приёмов. Пример: 34 маркера в `../11-styles-trends/04`.

**Median aesthetic** [также: медианная эстетика] — статистическое среднее обучающих данных как результат неограниченной генерации. Пример: Inter + индиго-градиент + три карточки. → `11-styles-trends/`.

**Template chrome** [также: шаблонный хром] — набор оформительских приёмов, появляющихся независимо от предмета: капс-eyebrow, `A · B · C`, `WORD — fragment`, `#0B0B0B` вместо чёрного, моно для подписей, `→` в кнопках. → `11-styles-trends/04-anti-slop-ui.md`.

**SaaS-card kit** — контент, нарезанный на одинаковые скруглённые карточки с одним радиусом и одной тенью `rgba(0,0,0,.1)`. → `11-styles-trends/`.

**Eyebrow-лейбл** (eyebrow) — мелкая надпись капсом над заголовком. Маркер шаблона, если стоит над каждым. → `11-styles-trends/04-anti-slop-ui.md`.

**Tell** (generation marker) [также: выдаёт] — деталь, по которой опознаётся происхождение работы. Пример: терракота `#D97757` в чужом брифе. → `11-styles-trends/01-style-dictionary-for-quiz.md`; `12-ai-generated-ui/`. В 12 то же под именем «Маркер генерации»: признак, по которому интерфейс опознаётся как сгенерированный. Пример: тень у карточек 84,9 %, эмодзи вместо иконок.

**Model collapse** [также: схлопывание модели] — потеря хвостов распределения при обучении на сгенерированных данных; объяснение, почему выразительные решения исчезают. → `11-styles-trends/04-anti-slop-ui.md`.

**Петля самоусиления** (feedback loop) — заметный сгенерированный интерфейс попадает в следующий срез обучающих данных и закрепляет паттерн. → `11-styles-trends/04-anti-slop-ui.md`.

**Polished slop** [также: полированный слоп] — чисто исполненный безликий результат; опознаётся труднее сырого. → `11-styles-trends/04-anti-slop-ui.md`.

**Happy path bias** — склонность генерации показывать только успешный сценарий с данными; пустое состояние, загрузка и ошибка отсутствуют. → `11-styles-trends/`.

**Крафт** (craft) — сумма мелких решений, которые не видно сразу, но которые чувствуются через несколько минут работы. Пример формулировки: «hundreds of design decisions made by someone obsessing over the tiniest margins so that when they work, no one has to think about». → `11-styles-trends/03-dated-vs-crafted.md`.

**Консистентность** (consistency) — малое число повторяющихся значений. Измеримо: 3–5 радиусов, 0–3 тени, 4–7 кеглей на экране. → `11-styles-trends/03-dated-vs-crafted.md`.

**Сдержанность** (restraint) — сознательный отказ от приёмов. Правило Шанель: перед выходом снять один аксессуар. → `11-styles-trends/03-dated-vs-crafted.md`.

**Поляризация стиля** (style polarization) — разброс оценок по группам пользователей. Измерено: плоские макеты 18–25 лет оценивают на 0.53 балла из 7 выше, чем 35+; у не-плоского контроля разница 0.01. → `11-styles-trends/`.

**Сигнификатор** (signifier) — воспринимаемая подсказка, что элемент интерактивен. Слабые сигнификаторы дают +22 % времени и +25 % фиксаций. → `11-styles-trends/01-style-dictionary-for-quiz.md`.

**Click uncertainty** [также: неопределённость клика] — состояние, когда пользователь не уверен, что элемент кликабелен; приводит к пробным кликам и наведениям. → `11-styles-trends/`.

**Три визуальных поколения** — измеримые профили 2006 (шаг 2 px, тени по диагонали, границы до 5.7:1), 2015 (`em`-вёрстка, дробные отступы), 2024–2026 (шаг 4, граница 1 px 1.2–1.5:1, тень только на оверлее). → `11-styles-trends/`.

**Тест выброшенного контента** — убрать с макета текст и данные; если по цветам и формам продукт не отличим от конкурентов, ручек характера не хватает. → `11-styles-trends/`.

**Карточка стиля** (style card) — 10–15 строк с hex-значениями, шрифтом, кеглями, радиусом и размерами плотности, которые передаются генератору изображений вместо JSON токенов. → `09-design-tokens/05-anti-patterns-and-pipeline.md` §5.; `11-styles-trends/`; `12-ai-generated-ui/`. В 11: 10–15 строк для генератора картинок: 8–10 hex, шрифт, три кегля, четыре размера плотности, описание глубины словами, 2–3 слова о характере. Без имён токенов и JSON. В 12: 10–15 строк с hex, шрифтом, тремя кеглями, радиусом, плотностью и характером — для генератора картинок. Пример: `../09-design-tokens/05` §5.

## 12. Нейросети и генерация

**Генератор изображений, текст-в-картинку** (text-to-image model, T2I) — модель, создающая растровое изображение по текстовому описанию. Пример: GPT-Image-2.5, Nano Banana Pro, FLUX.2. → `12-ai-generated-ui/`.

**Картинка-из-картинки** (image-to-image, img2img) — генерация нового изображения на основе входного с заданной силой преобразования. Пример: скриншот каркаса → стилизованный макет. → `12-ai-generated-ui/`.

**Вес стиля** (style weight) — сила влияния референса стиля на результат. Пример: Midjourney `--sw`. → `12-ai-generated-ui/`.

**Мультиреференс** (multi-reference) — несколько входных изображений в одном запросе. Пример: FLUX.2 до 10, Nano Banana Pro до 14. → `12-ai-generated-ui/`.

**Сид** (seed) — число, инициализирующее генерацию; должно давать повторяемость. Пример: у Midjourney V8.1/8.2 даёт «99 % identical», то есть неполную. → `12-ai-generated-ui/01-image-models-for-ui.md`.

**Шаги** (steps) — число итераций сэмплирования; влияет на детализацию и точность типографики. Пример: FLUX.2 [flex]: 6 / 20 / 50. → `12-ai-generated-ui/01-image-models-for-ui.md`.

**Негативный промт** (negative prompt) — явное перечисление того, чего не должно быть в результате. Пример: «no gradients, no glow, no emoji». → `12-ai-generated-ui/`.

**Открытые веса** (open weights) — модель, чьи веса опубликованы и запускаются локально. Пример: FLUX.2 [dev] 32B, Qwen-Image (Apache 2.0). → `12-ai-generated-ui/01-image-models-for-ui.md`.

**Векторная генерация** (vector generation) — выдача SVG, а не растра. Пример: Recraft `Vector art`, V4 Styles. → `12-ai-generated-ui/`.

**Цифровой водяной знак** (digital watermark) — скрытая или видимая метка происхождения. Пример: SynthID у Google; видимая «искра» Gemini на free и Pro. → `12-ai-generated-ui/`.

**Управляющая карта** (ControlNet, Canny, Depth) — карта контуров или глубины, задающая геометрию при генерации. Пример: вайрфрейм как карта контуров. → `12-ai-generated-ui/01-image-models-for-ui.md`.

**Макет-в-код** (design-to-code, UI-to-code) — генерация кода по скриншоту или прототипу. Пример: Design2Code, DesignBench. → `12-ai-generated-ui/`.

**Переход состояния за один шаг** (single-step transition) — генерация следующего состояния интерфейса по одному действию. Пример: GEBench: > 80 у двух лидеров. → `12-ai-generated-ui/`.

**Многошаговая траектория** (multi-step planning) — пять последовательных состояний по общей цели. Пример: GEBench: падение ниже 60, у открытых моделей ниже 10. → `12-ai-generated-ui/`.

**Привязка к координате** (grounding) — генерация изменения в заданной точке `[0,1000]`. Пример: GOAL 23,9 % у лучшей модели. → `12-ai-generated-ui/01-image-models-for-ui.md`.

**Пертурбация** (perturbation) — то же для метаданных макета: сдвиг, смена шрифта, смена цвета. Пример: 1–3 на макет в AesEval-Bench. → `12-ai-generated-ui/`.

**Совпадение блоков** (Block-Match) — доля воспроизведённых и невыдуманных визуальных блоков. Пример: GPT-4o 93,0 из 100. → `12-ai-generated-ui/`.

**Сходство позиции** (Position similarity) — нормированное расстояние между центрами сопоставленных блоков. Пример: 85,5 у лучшей модели. → `12-ai-generated-ui/`.

**Сходство цвета** (Color similarity) — близость цвета текста по CIEDE2000. Пример: 84,1 у лучшей, 71,4 у Claude 3 Opus. → `12-ai-generated-ui/`.

**Похожесть по CLIP** (CLIP similarity) — косинусная близость эмбеддингов скриншотов. Пример: 90,4 у лучшей. → `12-ai-generated-ui/`.

**Сходство модификации кода** (Code Modification Similarity, CMS) — насколько правка попала туда, куда нужно. Пример: 0,23–0,68 при компиляции > 0,9. → `12-ai-generated-ui/`.

**Средний обратный ранг** (Mean Reciprocal Rank, MRR) — метрика качества поиска по образцам. Пример: UIClip 0,3851 против 0,2534 у базового CLIP. → `12-ai-generated-ui/`.

**Каппа Фляйсса** (Fleiss' Kappa) — согласие нескольких оценщиков. Пример: 0,29–0,31 у экспертов-дизайнеров на критиках. → `12-ai-generated-ui/`.

**Лучший из N** (best-of-n sampling) — сгенерировать N вариантов и выбрать лучший по метрике. Пример: UIClip ранжирует 5 вариантов HTML. → `12-ai-generated-ui/`.

**Самокритика** (self-revision) — просьба к модели исправить собственный вывод без внешнего измерителя. Пример: вредит слабым моделям: 39,7 → 30,1. → `12-ai-generated-ui/`.

**Обогащение текстом** (text-augmented prompting) — подача распознанного текста списком вместе со скриншотом. Пример: block-match с 0,25 до 0,84 в примере. → `12-ai-generated-ui/`.

**Визуально-языковая модель** (vision-language model, VLM, multimodal LLM, MLLM) — модель, принимающая изображение и текст. Пример: GPT-5, Gemini 3, Qwen3-VL. → `12-ai-generated-ui/`.

**Модель как судья** (LLM-as-a-judge, VLM-as-a-judge) — использование модели для оценки чужого результата по рубрике. Пример: Пирсон 0,9892 с экспертами на рубрике GEBench. → `12-ai-generated-ui/`.

**Индикатор** (indicator) — конкретный проверяемый аспект внутри измерения. Пример: balance, layering, whitespace, alignment. → `12-ai-generated-ui/03-research-2024-2026.md`.

**Локализация замечания** (grounding of a critique) — привязка замечания к области экрана. Пример: второй вызов, номера патчей. → `12-ai-generated-ui/`.

**Жёсткое ограничение** (hard constraint) — правило вида «делай / не делай» с числом. Пример: 228 в KB-Comp DesignRepair, recall починки 92,3 %. → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Мягкое ограничение** (soft constraint) — рекомендация без порога. Пример: 399 в KB-Comp, recall починки 70,4 %. → `12-ai-generated-ui/`.

**Валидная критика** (valid critique) — замечание одновременно точное и полезное. Пример: 13,1 % у Gemini zero-shot. → `12-ai-generated-ui/`.

**Профиль вместо балла** (profile, not a score) — результат оценки как вектор по измерениям, а не одно число. Пример: см. `../13-evaluation-checklists/02` §2.2. → `12-ai-generated-ui/`.

**Центроид обучающих данных** (training centroid) — среднее по корпусу, к которому модель возвращается без различающего сигнала. Пример: Inter + zinc + фиолетовый + `rounded-2xl` + тень. → `12-ai-generated-ui/`.

**Регрессия к среднему** (regression to the mean) — механизм: наиболее вероятное продолжение и есть среднее. Пример: «Variance is penalized; the mean is rewarded». → `12-ai-generated-ui/02-codegen-tools-and-default-look.md`.

**Шлак** (shit, crud) — избыточное или ненужное; захламлённое, неуклюже сложное; намеренно вводящее в заблуждение. Пример: определение Брэда Фроста, 2013. → `12-ai-generated-ui/02-codegen-tools-and-default-look.md`.

**Набор SaaS-карточек** (SaaS-card kit) — контент, нарезанный на одинаковые скруглённые карточки с одной тенью. Пример: кластер 4 в списке Anthropic. → `12-ai-generated-ui/`.

**Шаблонная обвязка** (template chrome) — приёмы, появляющиеся независимо от темы: ALL-CAPS eyebrow, `A · B · C`, стрелка `→`. Пример: кластер 5 в списке Anthropic. → `12-ai-generated-ui/`.

**Дефолты библиотеки** (library defaults, library default) — значения, которые применяются, если слой темы не переопределён. Пример: принцип shadcn «Beautiful Defaults». → `13-evaluation-checklists/`. В 13 то же под именем «Дефолт библиотеки»: узнаваемый неизменённый набор значений. Пример: shadcn: `--radius: 10px`, zinc, Inter, почти чёрный primary.

**Эффект расползания** (ripple effect) — правка одного элемента меняет остальной интерфейс. Пример: описали 5 из 14 участников CHI '26. → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Визуальный оптимизм** (visual over-optimism) — высокое визуальное качество при нелогичном или галлюцинированном содержимом. Пример: парадокс GEBench. → `12-ai-generated-ui/`.

**Галлюцинированный виджет** (hallucinated widget) — элемент интерфейса, которого не может быть или который ничего не делает. Пример: «карточки-пустышки». → `12-ai-generated-ui/`.

**Кодогенератор UI** (AI UI builder) — инструмент, выдающий работающий интерфейс по промту. Пример: v0, Lovable, Bolt, Figma Make, Stitch. → `12-ai-generated-ui/`.

**Пакет инструкций** (instruction package) — всё, что модель читает перед генерацией: токены, правила, каталог, эталон. Пример: `DESIGN.md` + `guidelines/` + `starter/`. → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Четыре уровня семантик** (semantic framework) — Product → Design System → Feature → Component. Пример: CHI '26, анализ 907 фрагментов. → `12-ai-generated-ui/`.

**Дерево решений** (decision tree) — вопрос в кавычках и ветки «условие → токен». Пример: формат Figma Make. → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Частотность цвета** (colour frequency) — пометка Dominant / Sparse / Internal у роли цвета. Пример: доля площади, а не значение. → `12-ai-generated-ui/`.

**Стартовое приложение** (starter) — эталонный собранный экран, сохранённый в пакет инструкций. Пример: `v0.json` → `starter`. → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Правило верифицируемости** (verifiability rule) — запрет использовать то, чего нет в источниках. Пример: «If a component, prop, or token cannot be verified… should not use it». → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Машиночитаемое самоописание** (LLM-facing documentation) — документация системы, предназначенная модели, а не человеку. Пример: `/llms.txt`, `org.primer.llm`, `CLAUDE.md`, MCP. → `12-ai-generated-ui/`.

**Протокол контекста модели** (Model Context Protocol, MCP) — протокол, по которому модель запрашивает данные у сервера инструмента. Пример: MCP-серверы shadcn, Adobe, Figma. → `12-ai-generated-ui/`.

**Скилл** (skill) — компактный набор инструкций, подгружаемый моделью по релевантности. Пример: v0 Design Systems 2.0, скиллы shadcn. → `12-ai-generated-ui/02-codegen-tools-and-default-look.md`.

**DESIGN.md** — открытый формат описания визуальной идентичности для агентов: YAML-токены + проза + запреты. Пример: github.com/google-labs-code/design.md, статус alpha. → `12-ai-generated-ui/`.

**Раздел «делай / не делай»** (Do's and Don'ts) — обязательный последний раздел в порядке секций DESIGN.md. Пример: запреты в явном виде. → `12-ai-generated-ui/`.

**Опущенные секции** (`omitted`) — поле, которым автор помечает намеренно пропущенные разделы. Пример: отличает «забыл» от «решил не задавать». → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Осиротевший токен** (orphaned token) — цвет определён, но ни один компонент на него не ссылается. Пример: правило линтера DESIGN.md, уровень warning. → `12-ai-generated-ui/`.

**Битая ссылка токена** (broken reference) — `{colors.primary}` не резолвится. Пример: правило линтера, уровень error. → `12-ai-generated-ui/`.

**Инструкция в репозитории** (`CLAUDE.md`) — файл с правилами проекта, который читает агент. Пример: образец Untitled UI. → `12-ai-generated-ui/`.

**Каркас кодом** (coded skeleton) — свёрстанная геометрия без стилизации, как основа для измерения и img2img. Пример: шаг перед скриншотом. → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Машинный отчёт** (machine report) — таблица «правило → найдено → порог → где» из измерений. Пример: `measure_ui.py` + `ui_audit.py`. → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Обратный маршрут** (reverse check) — снятие фактических значений с готовой картинки и сверка с токенами. Пример: ΔE OKLab, ±2 px по высотам. → `12-ai-generated-ui/01-image-models-for-ui.md`.

**Цикл правок** (review loop) — измерение → отчёт → критика → правка → повторное измерение. Пример: `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md` §5.1. → `12-ai-generated-ui/`.

**Регрессия правки** (fix regression) — нарушения, появившиеся после исправления других. Пример: ловится диффом отчётов. → `12-ai-generated-ui/`.

**Приёмка** (acceptance) — решение человека о том, что результат достаточен. Пример: не автоматизируется. → `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`.

**Референс стиля** (style reference) — картинка, задающая образец для последующих. Для генеративной системы берётся первая принятая картинка серии, а не чужая библиотека. → `07-iconography-imagery/02-illustration-system-avatars-images.md`; `12-ai-generated-ui/`. В 12: изображение или код, задающие эстетику всей серии. Пример: Midjourney `--sref`, Ideogram Style Code, Recraft `style_id`.

## 13. Оценка и метрики

**Чек-лист** (checklist) — закрытый список проверок «да/нет» с порогом у каждой. Пример: 117 проверок в 13 группах. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Якорь балла** (anchor, descriptor) — словесное описание того, что значит конкретный балл. Пример: «3 — система есть, нарушения единичны». → `12-ai-generated-ui/`. В 12 то же под именем «Якорь шкалы»: словесное описание того, что означает каждый балл. Пример: «3 — иерархия читается, но два уровня спорят».

**Критика** (critique) — проза с замечаниями, без оценки и без таблицы. Пример: «правая колонка, третья карточка: …». → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Аудит** (audit) — таблица по пунктам чек-листа со статусом у каждого. Пример: пройдено / частично / нет / неприменимо / не видно. → `13-evaluation-checklists/01-visual-qa-checklist.md`.

**Дизайн-ревью** (design review) — процесс приёмки визуального слоя перед выпуском. Пример: второй человек обязателен. → `13-evaluation-checklists/`.

**Приёмочный шлюз** (acceptance gate) — бинарное условие, без которого релиз не выпускается. Пример: контраст 4.5:1, цели 24 px. → `13-evaluation-checklists/`.

**Порог приёмки** (acceptance threshold) — числовое условие прохождения проверки. Пример: «доля отступов из шкалы ≥ 95 %». → `13-evaluation-checklists/`.

**Серьёзность** (severity) — уровень нарушения: блокер, серьёзно, полировка. Пример: блокер — нарушение норматива A/AA. → `13-evaluation-checklists/01-visual-qa-checklist.md`.

**Профиль оценки** (score profile) — набор баллов по измерениям вместо одного числа. Пример: десять столбиков вместо «3.4». → `13-evaluation-checklists/`.

**Скрининг** (screening) — отбор кандидатов метриками до человеческой проверки. Пример: отсеять перегруженные раскладки. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Definition of done** — список условий, при которых работа считается законченной. Пример: восемь измерений качества компонента. → `13-evaluation-checklists/`.

**Kitchen sink** (kitchen sink page) — страница со всеми вариантами и состояниями компонента для QA. Пример: `buttons-sink.html`. → `13-evaluation-checklists/`.

**Визуальная сложность** (visual complexity) — воспринимаемое количество и разнообразие элементов. Пример: R² модели .65 (Reinecke). → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Прототипичность** (prototypicality) — насколько страница похожа на типичную страницу своего класса. Пример: η²p .55–.81 (Tuch). → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Цветность** (colorfulness) — формула Хаслера–Зюсструнка `σ_rgyb + 0.3 µ_rgyb`. Пример: 33 «умеренно», 59 «весьма». → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Доминирующие цвета** (dominant colors) — число цветовых кластеров, покрывающих заметную площадь. Пример: коррелирует с красотой **отрицательно**. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Глубина цвета** (color range, color depth) — число различных значений цвета. Пример: коррелирует **положительно**, r +.56. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Плотность контуров** (contour density, edge density) — доля контурных пикселей. Пример: хорошо 0–0.0296, плохо ≥ 0.0495. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Сгущение контуров** (contour congestion) — доля контуров, у которых есть сосед в 20 px. Пример: хорошо 0–0.6033. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Контраст фигуры и фона** (figure-ground contrast) — взвешенная сумма краёв, найденных Canny на семи порогах. Пример: хорошо ≥ 0.6856. → `13-evaluation-checklists/`.

**Feature Congestion** — мера зрительного шума через локальную ковариацию признаков. Пример: хорошо 0–3.771. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Subband entropy** — энтропия вейвлет-поддиапазонов; веса 0.84 яркость, 0.08 + 0.08 цветность. Пример: хорошо 0–2.7153. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Квадродерево** (quadtree decomposition) — рекурсивное деление кадра по энтропии. Пример: r .28 со сложностью — слабо. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Пространственная сегментация** (space-based decomposition) — рекурсивный X-Y cut по видимым разделителям. Пример: r .50 со сложностью. → `13-evaluation-checklists/`.

**Белое пространство** (white space ratio) — доля кадра, не покрытая визуальными блоками. Пример: практически не коррелирует. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Grid quality** — пять мер сетки: число блоков, точек выравнивания, размеров блоков, покрытие. Пример: допуск выравнивания 2 px. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Баланс** (balance) — равномерность визуального веса по осям. Пример: r .57–.72 с красотой (Zheng). → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Равновесие** (equilibrium) — центрирование массы вокруг середины кадра. Пример: на веб-страницах **не коррелирует ни с чем**. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Симметрия** (symmetry) — совпадение объектов по осям. Пример: частичная симметрия нравится меньше всего. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Экономность** (economy (Ngo)) — `1 / число различных размеров`. Пример: аналог правила «размеров ≤ 8». → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Однородность** (homogeneity (Ngo)) — равномерность распределения объектов по квадрантам через энтропию Больцмана. Пример: 0…1. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**AIM** (Aalto Interface Metrics) — открытый каталог из 26 метрик с порогами good/normal/bad. Пример: `github.com/aalto-ui/aim`. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Аффект внимания** (saliency) — предсказание того, куда смотрит глаз. Пример: UMSI, MD-EAM (0.5 / 3 / 5 с). → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Модель-критик** (VLM critic) — визуально-языковая модель, оценивающая скриншот. Пример: GPT-5, Gemini, UIClip. → `13-evaluation-checklists/`.

**Zero-shot** — запрос без примеров. Пример: 13 % валидных критик. → `13-evaluation-checklists/`.

**Few-shot** — запрос с примерами, подобранными по сходству. Пример: 8-shot: качество 0.58 против 0.24. → `13-evaluation-checklists/`.

**Визуальное сходство** (visual similarity) — подбор примеров по эмбеддингу изображения. Пример: лучший способ отбора примеров. → `13-evaluation-checklists/`.

**Задачное сходство** (task similarity) — подбор примеров по задаче экрана. Пример: вместе с визуальным даёт максимум. → `13-evaluation-checklists/`.

**Качество комментария** (comment quality) — валидный 1, частично валидный 0.5, невалидный 0. Пример: человек 0.75, few-shot 0.58. → `13-evaluation-checklists/02-rubrics-and-vlm-critic.md`.

**Точность рейтинга** (rating accuracy) — точное совпадение 1, отклонение на 1 пункт 0.5. Пример: 0.53 у лучшего набора. → `13-evaluation-checklists/`.

**CRAP** (contrast, repetition, alignment, proximity) — четыре принципа, по которым строятся порчи в UIClip. → `13-evaluation-checklists/03-automated-checks.md`.

**Попарное сравнение** (pairwise comparison) — «Какой из двух лучше» вместо абсолютной оценки. Пример: UI-Bench: 4 075 матчей, 194 эксперта. → `13-evaluation-checklists/`.

**TrueSkill** — рейтинг по парным сравнениям. Пример: старт μ 25.0, σ 8.33. → `13-evaluation-checklists/`.

**Слепая зона** (blind spot) — класс дефектов, который инструмент не видит. Пример: локализация, стабильность, 1.4.11. → `13-evaluation-checklists/`.

**Правило** (rule) — именованная проверка в линтере. Пример: `color-contrast`, `target-size`. → `13-evaluation-checklists/03-automated-checks.md`.

**Тег правила** (tag) — метка стандарта у правила axe. Пример: `wcag2aa`, `wcag143`, `ACT`. → `13-evaluation-checklists/`.

**Нарушение** (violation) — проверка провалена. Пример: `violations[]` в axe. → `13-evaluation-checklists/03-automated-checks.md`.

**Требует проверки** (incomplete, needs review) — проверка не завершена по техническим причинам. Пример: градиент под текстом. → `13-evaluation-checklists/03-automated-checks.md`.

**Неприменимо** (inapplicable) — на странице нет элементов для этой проверки. Пример: `inapplicable[]`. → `13-evaluation-checklists/01-visual-qa-checklist.md`.

**Воздействие** (impact) — серьёзность нарушения в axe. Пример: minor / moderate / serious / critical. → `13-evaluation-checklists/03-automated-checks.md`.

**Инлайновое исключение** (inline exception) — ссылка внутри строки текста не нормируется по размеру. Пример: SC 2.5.8, SC 2.5.5. → `13-evaluation-checklists/`.

**Строгое значение** (strict value) — требование, чтобы в CSS стояла переменная, а не литерал. Пример: `scale-unlimited/declaration-strict-value`. → `13-evaluation-checklists/`.

**Произвольное значение** (arbitrary value) — значение в квадратных скобках у Tailwind. Пример: `p-[13px]` — сюда уходят числа вне шкалы. → `13-evaluation-checklists/`.

**Порог диффа** (diff threshold) — допустимое различие при сравнении скриншотов. Пример: Playwright 0.2 (YIQ), Chromatic 0.063. → `13-evaluation-checklists/`.

**Маска** (mask) — область, исключённая из сравнения скриншотов. Пример: `maskColor: "#FF00FF"`. → `13-evaluation-checklists/03-automated-checks.md`.

**Эталон** (baseline, golden) — снимок, с которым сравнивают новый. Пример: `<test>-snapshots/*.png`. → `13-evaluation-checklists/03-automated-checks.md`.

**Эмуляция медиа** (media emulation) — подмена системных настроек в браузере. Пример: `color_scheme`, `reduced_motion`, `forced_colors`, `contrast`. → `13-evaluation-checklists/`.

**Обход табом** (tab walk) — последовательное нажатие Tab со снятием состояния фокуса. Пример: 20–24 остановки. → `13-evaluation-checklists/`.

**Эффективный фон** (effective background) — непрозрачный цвет под элементом после композитинга альфы. Пример: нужен для честного контраста. → `13-evaluation-checklists/03-automated-checks.md`.

**Антислоп** (anti-slop) — группа проверок против типовых следов генерации. Пример: эмодзи, градиенты, `scale` на hover. → `13-evaluation-checklists/`.

**Ручка узнаваемости** (recognisability knob) — значение, смена которого снимает «вид из коробки». Пример: нейтраль, радиус, тень, шрифт, акцент. → `13-evaluation-checklists/`.

**Кластер маркеров** (marker cluster) — совпадение нескольких признаков генерации на одном экране. Пример: Inter + индиго-градиент + три карточки + тень 0.1. → `13-evaluation-checklists/`.

**Карточка, которая ничего не делает** (non-functional card) — блок в оформлении карточки без действия и без данных. → `13-evaluation-checklists/03-automated-checks.md`.

**Оптимизированный бриф** (optimised prompt) — промт с явными значениями и запретами. Пример: 86 с → 28 с, 63 % → 100 % (Electronics 2026). → `13-evaluation-checklists/`.

**«Почти, но не совсем»** (almost-but-not-quite) — разница в 1–3 px между величинами, которые должны быть равны. Пример: карточки 204 и 208. → `05-layout-grid/04-alignment-whitespace-composition.md`; `13-evaluation-checklists/`. В 13: разница 1–3 px между величинами, которые должны быть равны. Пример: карточки 204 и 208.

**Эстетико-юзабилити эффект** (aesthetic-usability effect) — привлекательные продукты воспринимаются как более удобные; маскирует мелкие проблемы, но не крупные. → `13-evaluation-checklists/`. В 13 то же под именем «Эффект эстетики и юзабилити»: красивый интерфейс делает пользователя терпимее к мелким проблемам и маскирует их при тестировании. Пример: «this effect can mask UI problems».

**Тест прищура** (squint test) — размыть макет до неразличимости букв; должен остаться один очевидный первичный элемент и понятная сетка блоков. → `05-layout-grid/`; `13-evaluation-checklists/`. В 05 то же под именем «Тест на прищур»: проверка иерархии на размытом макете. Пример: Gaussian blur 6–10 px при ширине 1440. В 13 то же под именем «Тест на прищур»: проверка иерархии на размытом макете. Пример: Gaussian blur 6–10 px при 1440.

**Дрожание, порча макета** (jitter) — контролируемое внесение дефекта в исходный макет для обучения и оценки. Пример: 9 функций JitterWeb, до трёх одновременно. → `12-ai-generated-ui/03-research-2024-2026.md`; `13-evaluation-checklists/`. В 13 то же под именем «Джиттер»: контролируемая порча дизайна для обучения. Пример: смена цвета, кегля, отступов, контраста.

**Пересечение по объединению** (Intersection over Union, IoU) — мера совпадения предсказанной и эталонной рамки. Пример: 0,004 без разметки, 0,222 с патчами. → `13-evaluation-checklists/`. В 13 то же под именем «IoU»: пересечение предсказанного и истинного bbox. Пример: < 0.20 у всех моделей.

**Рубрика** (rubric) — набор измерений со шкалой и описанными якорями. Пример: 10 измерений (папка 13), 12 индикаторов AesEval, 5 измерений GEBench. → `12-ai-generated-ui/03-research-2024-2026.md`; `13-evaluation-checklists/`. В 13: шкала с якорями по каждому измерению. Пример: 0–5 по десяти измерениям.

**Визуальный промт** (visual prompting) — разметка поверх скриншота, помогающая модели отвечать о местоположении. Пример: пронумерованные патчи, координатные подписи по краям. → `12-ai-generated-ui/03-research-2024-2026.md`; `13-evaluation-checklists/`. В 13 то же под именем «Visual prompting»: подсказки, нанесённые на кадр. Пример: координатная рамка: IoU 0.186; сетка поверх кадра: 1.1e−5.

## 14. Несовместимая терминология: где источники расходятся и что принято в базе

Термины ниже в разных дизайн-системах, у разных авторов или в разных папках базы означают разное или называются по-разному.
Колонка «Принято в базе» фиксирует значение, которое используют файлы и эталонная схема токенов; при чтении чужого источника
сверяйте смысл по числам, а не по слову.

| Термин | Как расходятся источники | Принято в базе | Где |
|---|---|---|---|
| **key / ambient тень** | У Material 3 и Fluent 2 `key` — короткая плотная тень, `ambient` — дальняя рассеянная. У Steve Schoger (Refactoring UI, `[V01]`, `[V02]`) «ambient» — короткая плотная тень у самого объекта, а большая называется «direct» | Значение Material/Fluent: `shadow.key` = малое смещение и размытие, `shadow.ambient` = большое смещение и размытие с отрицательным spread. Встретив слова в чужом тексте, определять по числам | `09-design-tokens/glossary.md` (предупреждение), `04-shape-elevation/02-shadows-layers-depth.md`, эталонная схема `09-design-tokens/04-reference-token-schema.md` |
| **декларация / практика** | «Декларация» — значение, объявленное системой в документации или исходниках; «практика» — значение, снятое с живого экрана через `getComputedStyle`, то есть применение токена на конкретном экране, а не сам токен | Обе колонки в атласе; при расхождении правило берёт практику, если она измерена (padding кнопки 8/16, а не 12; шапка 48, а не 56; контрол 32, а не 40) и помечает декларацию | `10-design-systems-atlas/glossary.md`, `10-design-systems-atlas/README.md` (выжимка, п. 2–3), `10-design-systems-atlas/04-live-products-measured.md` §6, `CONTRADICTIONS.md` |
| **брейкпоинт / класс окна / класс размера** | Material 3 в 2026 переименовал window size classes в breakpoints, а «responsive layout» в «adaptive design»; Apple — size classes (compact/regular по каждой оси); Fluent 2 — шесть size classes | Общий термин — **брейкпоинт** (ширина вьюпорта, на которой меняется раскладка); «класс окна» и «класс размера» только при цитировании Material и Apple. Приложению хватает 3–4 брейкпоинтов: < 640, 640–1023, 1024–1439, ≥ 1440 | `05-layout-grid/01-grids-breakpoints-containers.md`, `05-layout-grid/README.md` |
| **overshoot** | В иконографии овершут — намеренное увеличение круглых форм (+11 %), чтобы круг не казался меньше квадрата; в движении перелёт — проскок цели с возвратом (y > 1 в кривой Безье, ζ < 1 у пружины) | Два разных термина: «овершут» (иконки) и «перелёт» (движение); Carbon перелёт в рабочих интерфейсах запрещает, M3 Expressive требует | `07-iconography-imagery/01-icons.md`, `08-motion/01-durations-easings-springs.md` |
| **productive / expressive (Carbon)** | Одна и та же пара слов у Carbon означает три вещи: тип-сеты типографики (база 14 против 16 px), «личности» иконок, «личности» движения (кривые) | Всегда уточнять область: «тип-сет productive», «кривая productive», «иконка expressive» | `02-typography/02-type-scale.md`, `07-iconography-imagery/01-icons.md`, `08-motion/01-durations-easings-springs.md` |
| **слой состояния / альфа-слой / шаг шкалы / дельта светлоты** | Три модели состояний: Material — полупрозрачный слой цвета `on-container` (hover 0.08, focus и pressed 0.12, dragged 0.16); Radix — состояние = следующий шаг шкалы (3 → 4 → 5, 9 → 10); сдвиг светлоты ΔL 2–6 п.п. на hover, 5–9 на active | Любая из трёх, но одна на продукт; в базе дельты сведены в матрице состояний | `01-color/05-states-and-interaction.md`, `06-components-visual/07-states-matrix.md` |
| **warning / caution / attention / severe** | Polaris: `warning` оранжевый, `caution` жёлтый; Primer: `attention` жёлтый, `severe` оранжевый; у части систем только `warning` | Пять-шесть статусов: info, success, warning (caution), danger (critical), neutral, при ИИ-функциях magic. Жёлтый и оранжевый — светлая заливка с тёмным текстом, остальные — тёмная заливка с белым | `01-color/02-semantic-roles-and-architecture.md` §4.1, `01-color/README.md` |
| **tone / tint / shade / step** | GOV.UK: tint — смесь с белым, shade — с чёрным; Material: tone — ступень тональной палитры HCT (0…100); Polaris: `tone` / `tone-strong` — парные версии одного статуса; Tailwind и Radix нумеруют шаги (50–950, 1–12) | «Шаг шкалы» для положения на шкале; «тон» только в контексте Material; «парные тона» только в контексте Polaris | `01-color/01-color-models-and-scales.md` §2, `06-components-visual/glossary.md` |
| **уровни токенов** | Примитив = reference = global = base = seed; семантический = alias = system = functional; у Ant Design seed → map → alias; у Material md-ref / md-sys / md-comp | Два обязательных уровня: **примитив** и **семантический токен**; третий, **компонентный**, заводится по правилу трёх компонентов | `09-design-tokens/01-architecture-and-naming.md` §1, `01-color/02-semantic-roles-and-architecture.md` §1 |
| **граница / обводка / кольцо** | `border` входит в габарит; `outline` не влияет на поток; «кольцо» (ring) — тень `0 0 0 1px` вместо границы (Radix, Primer, Polaris), в тёмной теме светлое, в `forced-colors` исчезает | Фокус рисуется `outline` 2 px с `outline-offset` 2 px и контрастом ≥ 3:1; кольцо-тень только там, где граница сдвинула бы раскладку, и с запасным `border` для `forced-colors` | `04-shape-elevation/01-radius-and-borders.md`, `04-shape-elevation/02-shadows-layers-depth.md`, `09-design-tokens/glossary.md` (`shadow.ring`) |
| **плотность: compact / default / comfortable / spacious** | Material: density scale 0, −1, −2, −3 с шагом 4 px; Ant Design: compact-алгоритм (`controlHeight` 32 → 28); Spectrum, Uber, Carbon (пять плотностей таблицы) — свои имена режимов | Плотность — ось темы, меняющая отступы, высоты контролов и строк, но не кегль, радиусы, цвета и цель нажатия; шаг 4 px, режимов два, максимум три | `03-spacing-sizing/02-density.md`, `09-design-tokens/03-theming-and-modes.md`, `10-design-systems-atlas/glossary.md` |
| **крупный текст** | WCAG: 18 pt = 24 px обычного веса или 14 pt полужирного = 18.67 px; в отдельных файлах округлено до «18.5 px полужирного» | 24 px, либо 18.67 px при `font-weight` ≥ 700; порог для него 3:1 вместо 4.5:1 | `01-color/03-contrast.md` §1, `13-evaluation-checklists/03-automated-checks.md` |
| **скрим / backdrop / mask / blanket / оверлей** | Одно и то же затемнение под модальным слоем: Polaris `backdrop`, Atlassian `blanket`, Ant `mask`; в папке 13 «маска» — область, исключённая из сравнения скриншотов; «оверлей» в 03 — общее имя всплывающих слоёв | «Скрим» для затемнения (32–50 % чёрного в светлой теме, 60–75 % в тёмной); «маска» только в контексте визуальной регрессии; «оверлей» — любой всплывающий слой | `01-color/05-states-and-interaction.md`, `04-shape-elevation/02-shadows-layers-depth.md`, `13-evaluation-checklists/03-automated-checks.md` |
| **дровер / side panel / sheet / navigation drawer** | В папке 03 drawer — выезжающая панель поверх контента (400–560 или 40 % ширины); у Material navigation drawer — боковая навигация 360 dp; у shadcn и Vaul — sheet, в том числе нижний | «Дровер» — временная панель поверх контента; «сайдбар» (боковая навигация) — постоянная зона каркаса; «нижний лист» — мобильный вариант дровера | `03-spacing-sizing/03-control-and-panel-sizes.md`, `05-layout-grid/02-app-shells.md`, `06-components-visual/05-feedback-and-overlays.md` |
| **рельс / рейка (rail)** | Папки 03 и 06 пишут «рельс», папка 05 — «рейка»; Carbon 48 px, Material 3 80 dp, практика 56–72 px | Одно понятие — свёрнутый сайдбар с одними иконками; в сводном глоссарии «рельс», «рейка» как синоним | `05-layout-grid/02-app-shells.md` |
| **baseline** | В типографике — базовая линия и базовая сетка; в визуальной регрессии — эталонный снимок (golden) | Два разных термина: «базовая линия/сетка» и «эталон» | `02-typography/glossary.md`, `13-evaluation-checklists/03-automated-checks.md` |
| **плейсхолдер** | В компонентах — текст-пример в пустом поле (оформляется как вторичный текст, 4.7–6:1, а не как disabled); в изображениях — заглушка тех же габаритов на время загрузки (скелетон, доминирующий цвет, BlurHash) | Две записи; в проверках контраста плейсхолдер поля — отдельный порог | `06-components-visual/02-forms-and-inputs.md`, `07-iconography-imagery/02-illustration-system-avatars-images.md` |
| **индикатор** | В компонентах — полоса, точка или галочка состояния (индикатор вкладки 2–3 px); в рубриках оценки — проверяемый аспект внутри измерения (balance, whitespace) | Две записи | `06-components-visual/glossary.md`, `12-ai-generated-ui/glossary.md` |
| **чек-лист / рубрика / аудит / критика** | Чек-лист — закрытый список «да/нет» с порогом; рубрика — шкала 0–5 с якорями по измерениям; аудит — таблица со статусом у каждого пункта; критика — проза с замечаниями | Балл не ставится: результат оценки — профиль по десяти измерениям плюс список нарушенных порогов | `13-evaluation-checklists/02-rubrics-and-vlm-critic.md` §2, `13-evaluation-checklists/01-visual-qa-checklist.md` |
| **APCA Lc и контраст WCAG 2** | WCAG 2 — отношение яркостей 1:1…21:1 без знака; APCA Lc — перцептивный контраст со знаком (положительный — тёмное на светлом, отрицательный — светлое на тёмном), уровни 90 / 75 / 60 / 45 / 30 / 15; в тёмной теме WCAG 2 систематически завышает | Считать дважды: WCAG 2 обязателен, APCA уточняет; расхождения разобраны в `01-color/03` §4 | `01-color/03-contrast.md`, `10-design-systems-atlas/glossary.md` |
| **px / dp / pt** | Material задаёт значения в dp, Apple в pt, веб — в CSS px | В базе всё в px; dp и pt только с пометкой мобильного источника | `99-raw/prompts/_common.md` (формат), все папки |
| **style tile / карточка стиля** | Style tile (Samantha Warren) — артефакт между мудбордом и макетом: шрифты, цвета и элементы интерфейса без раскладки; карточка стиля — 10–15 строк с hex, шрифтом, кеглями, радиусом и плотностью для генератора картинок | Два разных артефакта конвейера: style tile для брифа и квиза, карточка стиля — для промта генератору изображений | `11-styles-trends/02-style-tiles-and-character-knobs.md`, `09-design-tokens/05-anti-patterns-and-pipeline.md` §5 |
| **AI slop / нейрослоп / шлак** | Папка 11 — «слоп в интерфейсе», папка 12 — «нейрослоп» (одно понятие: результат, в котором ни одно решение не принято); «шлак» (crud) — более широкое определение Брэда Фроста 2013 года | «Нейрослоп» и «слоп» взаимозаменяемы; диагноз ставится по кластеру из 4 и более маркеров, а не по одному признаку | `11-styles-trends/04-anti-slop-ui.md`, `12-ai-generated-ui/02-codegen-tools-and-default-look.md` |
| **цель нажатия / зона захвата / hit target** | Папка 03: цель нажатия — область, реагирующая на касание (24 × 24 по WCAG 2.2 AA, 44 × 44 AAA, 48 dp Material); папка 06: «зона захвата» (hit area) — невидимое расширение цели; папка 10: hit target — bounding box измеренного элемента | «Цель нажатия» ≥ 24 px (44 на тач); «зона захвата» — её невидимое расширение через псевдоэлемент; правило кругов для недоразмерных целей | `03-spacing-sizing/02-density.md`, `06-components-visual/07-states-matrix.md`, `10-design-systems-atlas/04-live-products-measured.md` |
| **mode: режим / мода** | В токенах mode — контекст внутри оси темы (`light` / `dark`, `compact` / `comfortable`); в атласе измерений мода — самое частое значение выборки | Две записи; в атласе мода информативнее среднего («32 у 8 продуктов из 24») | `09-design-tokens/glossary.md`, `10-design-systems-atlas/glossary.md` |
| **шкала** | В цвете — упорядоченный набор оттенков одного цвета (Tailwind 11 шагов, Radix 12); в токенах — пять видов рядов (enumerated, ordered, bounded, proportion, t-shirt); в атласе — сравнивать шкалы систем можно только по значениям, не по номеру шага (`space-400` у Polaris = 16 px, `space.400` у Atlassian = 32 px) | При сравнении систем всегда переводить шаг в значение | `01-color/01-color-models-and-scales.md` §2, `09-design-tokens/01-architecture-and-naming.md` §2.5, `10-design-systems-atlas/glossary.md` |
| **тень в тёмной теме** | Hobday запрещает тени в тёмных интерфейсах; Radix и Fluent оставляют с повышенной альфой; Material заменяет на осветление поверхности (оверлей высоты 0–16 %) | Глубина в тёмной теме передаётся осветлением поверхности и усиленным кольцом, тень остаётся слабым дополнением `[спорно]` | `04-shape-elevation/02-shadows-layers-depth.md` §6, `01-color/04-dark-theme.md` |

## 15. Указатель по английским терминам

Термин → номер раздела (1–13). Термины с двумя номерами определены в двух разделах в разном смысле.

**A**: `@adobe/leonardo-contrast-colors` → 1; Aalto Interface Metrics → 13; accelerate → 8; acceptance → 12; acceptance gate → 13; acceptance threshold → 13; Accessible Palette → 1; Accessible Perceptual Contrast Algorithm → 1; achromatopsia → 1; action-driven motion → 8; active → 6; acuity reserve → 1; aesthetic-usability effect → 13; AI slop → 11; AI UI builder → 12; AI/ML training prohibition → 7; alert → 6; alias → 9; alias token → 9; alignment → 13; almost flat → 11; almost-but-not-quite → 13; alpha compositing → 1; alpha layer → 6; alternation → 5; ambient shadow → 4; analytical dashboard → 5; anatomy → 6; anchor → 13; anchor object → 5; anchoring → 1; anti-slop → 13; anticipation → 8; antidesign → 11; aperture → 2; app bar → 5; app header → 5; app shell → 5; arbitrary value → 13; art direction → 11; ascender → 2; aspect ratio → 7; Atlassian → 8; audit → 13; auto-fill → 5; auto-fit → 5; auto-grow → 6; available height → 5; avatar → 7; avatar border → 7; avatar group → 7; avatar stack → 7; axis → 2, 9

**B**: backdrop → 4; backdrop-filter → 4; Backplate → 1; badge → 6; balance → 13; banner → 5, 6; base font size → 2; base token → 9; base unit → 3; baseline → 2, 13; baseline grid → 2; bento grid → 11; best-of-n sampling → 12; bevel → 4; blanket → 4; blind spot → 13; block button → 6; Block-Match → 12; blur radius → 4; border → 4; border radius → 4; bottom sheet → 5; Bounce → 8; breadcrumbs → 6; breakpoint → 5; Bridge-PCA → 1; brief → 11; brightness → 1; broken reference → 12; brutalism → 11; BSD 3-Clause → 10; busy → 6; button group → 6; bypassing → 5

**C**: `c2sc` → 2; callout → 6; `calt` → 2; Canny → 12; canonical layouts → 5; canvas → 7; cap height → 2; Carbon → 10; caret → 6; `case` → 2; Catalog of assumptions → 11; categorical → 1; Category / concept / property / variant / state / scale / mode → 9; CC BY 4.0 → 7; CC0 → 7; Change blindness → 8; character knob → 11; character knobs → 11; character variant → 2; checked → 6; checklist → 13; chip → 6; choreography → 8; chroma → 1; chroma curve → 1; CIELCh → 1; `CLAUDE.md` → 12; claymorphism → 11; Click uncertainty → 11; CLIP similarity → 12; `clip-path` → 8; CLS → 5; CMS → 12; Code Modification Similarity → 12; coded skeleton → 12; `codeSyntax` → 9; collision padding → 5; color depth → 13; color difference → 1; Color Module → 9; color range → 13; Color similarity → 12; color vision deficiency → 1; `color-scheme` → 1; colorfulness → 13; colorjs.io → 1; colour frequency → 12; column → 5; column grid → 5; combinatorial explosion → 9; combobox → 6; comfortable → 6; command palette → 6; comment quality → 13; compact → 6; compact algorithm → 3; completeness → 9; Component style guide → 11; component token → 9; composite type → 9; compositing layer → 8; concentric corners → 4; condensed → 6; consistency → 11; contact shadow → 4; container → 6; Container queries → 6; container query → 5; container token → 3; container-type → 5; content → 5; context bar → 5; contextual token → 9; continuous corners → 4; contour congestion → 13; contour density → 13; contrast → 13; contrast polarity → 1; contrast ratio → 1; control height → 3; ControlNet → 12; copy-in components → 10; corner radius → 4; corner smoothing → 4; corner token → 4; counter area → 7; counter stroke → 7; cqb → 5; cqi → 5; cqw → 5; craft → 11; critical → 6; critical contrast → 1; critique → 13; crud → 12; CSS ripple → 6; cubic-bezier → 8; cubicBezier token → 8; culori → 1; cumulative layout shift → 5; `currentColor` → 7; `cv01`–`cv99` → 2; CVD simulation → 10

**D**: `$deprecated` → 9; damping → 8; damping ratio → 8; danger → 6; dashboard → 5; date picker → 6; dead token → 9; decelerate → 8; decision tree → 12; declared value → 10; default → 6; Definition of done → 13; delay → 8; delta E → 1; density → 3; density interval → 3; density mode → 3; density scale → 3; Depth → 12; descender → 2; descriptor → 13; design review → 13; design system → 10; design token → 9; Design Tokens Community Group → 9; Design Tokens Format Module → 9; design-to-code → 12; DESIGN.md → 12; destructive → 6; deutan → 1; dialog → 6; diff threshold → 13; digital watermark → 12; `dimension` → 9; dimming → 7; directionType → 7; disabled → 6; diverging palette → 1; divider → 4; dominant colors → 13; Do's and Don'ts → 12; double node → 9; double ring → 6; drag handle → 6; dragged → 6; drawer → 6; drop target → 6; dropdown menu → 6; dropzone → 6; duration → 8; duration token → 8; dvh → 5; Dynamic Type → 2

**E**: `$extensions` → 9; ease-in → 8; ease-in-out → 8; ease-out → 8; easing function → 8; economy (Ngo) → 13; edge density → 13; editorial → 11; effective background → 13; elevation → 4; elevation overlay → 4; em → 2; em dash → 2; emoji → 7; emphasis → 1; Emphasized → 8; empty state → 6; en dash → 2; enabled → 6; entrance → 8; equilibrium → 13; error → 6; error text → 6; exit → 8; expanded → 6; expanded hit area → 3; eyebrow → 11

**F**: `:focus-visible` → 6; F-pattern → 5; fallow area → 5; false floor → 5; Feature Congestion → 13; feed → 5; feedback loop → 11; Few-shot → 13; fidelity scale → 11; Figma Variables → 9; figure-ground contrast → 13; fill → 1; Fill → 7; filled → 6; filled field → 4; First → 8; Fitts's law → 3; fix regression → 12; fixed grid → 5; fixed panel → 5; flash → 8; flash of unstyled text → 2; flat design → 11; flat perspective → 7; flatty → 11; Fleiss' Kappa → 12; flexible panel → 5; flip → 5; floating label → 6; floating panel → 5; Fluent / sub-fluent / spot readability → 1; fluid grid → 5; fluid type → 2; flyout → 5; focus → 6; focus indicator → 6; focus ring → 6; focus-visible → 6; focus-within → 6; fold → 5; font → 2; font family → 2; font metric override → 2; font size → 2; `font-display` → 2; forced colors → 1; `forced-color-adjust` → 1; `forced-colors` → 1; foreground token → 1; fr → 5; frame → 7; frame budget → 8; friction → 8; frosted glass → 11; full radius → 4; functional token → 9

**G**: gamut → 1; gamut mapping → 1; gap → 3; generation marker → 11; geometric sans → 2; `getComputedStyle` → 10; ghost → 6; glassmorphism → 11; global token → 9; golden → 13; gradation → 5; Grade → 7; gray scale → 1; grid influencer → 5; Grid quality → 13; grid unit → 3; grid-template-areas → 5; grounding → 12; grounding of a critique → 12; grouped → 5; guillemets → 2; Gutenberg diagram → 5; gutter → 5

**H**: halation → 1; half-leading → 2; hallucinated widget → 12; handle → 6; hanging punctuation → 2; Happy path bias → 11; hard constraint → 12; hashed color → 7; HCT → 1; headless → 10; helper text → 6; hero illustration → 7; high-contrast point → 5; highlight-on-change → 8; hint → 6; hinting → 2; hit area → 3, 6; hit target → 3; homogeneity (Ngo) → 13; hover → 6; Hover / active (pressed) / selected / focus / disabled → 1; hover card → 6; hover lift → 4; hue → 1; hue compensation → 1; hue shift → 1; Huetone → 1; Humaaans style → 7; humanist sans → 2; hybrid grid → 5

**I**: icon button → 6; icon font → 7; icon padding compensation → 6; illustration system → 7; image trace → 7; image-to-image → 12; Images of text → 7; img2img → 12; impact → 13; inapplicable → 13; incomplete → 13; indeterminate → 6; indicator → 6, 12; initials → 7; ink trap → 2; inline → 3; inline exception → 13; inline theming → 9; inner/outer spacing → 3; inset → 3; inset border shadow → 4; inset squish → 3; inset stretch → 3; inspector → 5; instruction package → 12; International Typographic Style → 11; interruptibility → 8; Intersection over Union → 13; intrinsic layout → 5; invalid → 6; inverse → 6; inverse surface → 1; Invert → 8; inverted → 1; invisible border → 6; IoU → 13; isometric projection → 7

**J**: jet → 1; jitter → 13; justify → 2

**K**: kbd → 6; kerning → 2; key color → 1; key line → 5; key shadow → 4; key shapes → 7; keyframe animation → 8; keyline shapes → 7; kitchen sink page → 13; knockout token → 1

**L**: Lab → 1; label → 6; label hiding → 6; large → 7; large text → 1; Last → 8; law of proximity → 3; layer → 1; layer-cake → 5; layered box-shadow → 4; layering model → 10; layout scaffold → 5; layout shift → 5; Layout, paint, composite → 8; lazy loading → 7; Lch(ab) → 1; leading → 2; leading trim → 2; leading visual → 6; letter-spacing → 2; library default → 12; library defaults → 12; `light-dark()` → 1; lightness → 1; lightness contrast → 1; lightness ladder → 1; line cap → 7; line join → 7; line length → 2; line-height → 2; linear → 8; `linear()` → 8; lining figures → 2; link → 6; Liquid Glass → 4; list-detail → 5; live area → 7; LLM-as-a-judge → 12; LLM-facing documentation → 12; `lnum` → 2; loading → 6; lockup → 7; `locl` → 2; logical properties → 5; low quality image placeholder → 7; Low-fidelity UI → 7; lvh → 5

**M**: M3 Expressive → 8; machine report → 12; Magic → 1; magic value → 9; main → 5; manuscript grid → 5; margin → 3, 5; marker cluster → 13; marking → 5; mask → 4, 13; mass → 8; master-detail → 5; masthead → 5; Material Design → 11; Material theming → 11; max chroma → 1; MCP → 12; Mean Reciprocal Rank → 12; measure → 2; measured value → 10; media emulation → 13; Median aesthetic → 11; medium → 7; metric card → 6; Millennial grey of UI → 11; mini unit → 3; mini-unit → 3; minimalism → 11; minmax → 5; minus sign → 2; MIT, ISC, Apache 2.0 → 7; MLLM → 12; modal → 6; mode → 9, 10; Model collapse → 11; Model Context Protocol → 12; modifier → 9; Modifier → 9; modular grid → 5; modular scale → 2; monogram → 7; monospace → 2; moodboard → 11; motion → 8; `motionUnit` → 8; MRR → 12; multi-reference → 12; multi-step planning → 12; multimodal LLM → 12; muted → 1

**N**: name facet → 10; Namespace → 9; namespace → 9; narrow no-break space → 2; Nathan Curtis → 9; natural frequency → 8; navigation drawer → 5; navigation rail → 5; needs review → 13; negative prompt → 12; negative slot margin → 6; negative space → 3; negative space token → 3; neo-grotesque → 2; neobrutalism → 11; nested grid → 5; nested radius → 4; neubrutalism → 11; neumorphism → 11; neutral scale → 1; neutral tint → 10; neutral variant → 1; no-break space → 2; non-functional card → 13; not a score → 12; notch → 4; nudge → 10

**O**: `object-fit` → 7; `object-position` → 7; offcanvas → 5; offset → 5; Oklab → 1; OKLCH → 1; oklch.com → 1; oldstyle figures → 2; `omitted` → 12; on-color → 1; `onum` → 2; open → 5; Open Props → 9; open weights → 12; operational dashboard → 5; `opsz` → 2; optical adjustment → 3; optical alignment → 5; optical center → 5; optical correction → 5; optical size → 2; optical weight → 7; optimised prompt → 13; orphan → 2; orphaned token → 12; orthogonality → 9; outline → 2, 4; outline-offset → 6; outlined → 6; outlined field → 4; `outputReferences` → 9; overflow (dashboard) → 5; overflow shadow → 4; overlay → 3; `overlay` → 8; overlay offset → 3; overshoot → 7, 8

**P**: padding → 3, 7; page header → 5; page inline padding → 3; page margins → 3; paired tones → 6; pairwise comparison → 13; Panda CSS → 9; pane → 5; panel → 5; paragraph spacing → 2; parameterization → 5; partial radius → 4; Penpot tokens → 9; penumbra → 4; perceptual duration → 8; Permutation → 9; perturbation → 12; picker → 6; pictogram → 7; piecewise scale → 10; pill → 4; placeholder → 6; plain → 6; Play → 8; playground → 10; `pnum` → 2; point size → 2; pointer type → 3; Polished slop → 11; polyhierarchy → 9; popover → 6; portal → 4; Position similarity → 12; `prefers-color-scheme` → 1; `prefers-contrast` → 1; `prefers-reduced-motion` → 8; `prefers-reduced-transparency` → 8; prefix / suffix → 6; presence indicator → 7; pressed → 6; pressed (toggle) → 6; primary → 6; primary grid → 7; primitive → 9; primitive set → 10; profile → 12; properties panel → 5; proportional figures → 2; protan → 1; prototypicality → 13; proximity → 13; proximity rule → 3; pseudo-token → 9; pure gray → 1; pure hue → 1; purpose alias → 10

**Q**: quadtree decomposition → 13; qualitative palette → 1

**R**: `$root`, `$extends`, `$ref` → 9; rail → 5; rainbow → 1; ramp → 9; rating accuracy → 13; re-architect → 5; readonly → 6; realism → 11; recognisability knob → 13; Reduce, not remove → 8; reference → 9; reference token → 9; reflow → 5; regression to the mean → 12; relative luminance → 1; rendering mode → 7; repetition → 5, 13; reposition → 5; resize → 5; `resolutionOrder` → 9; Resolver Module → 9; rest → 6; restraint → 11; reverse check → 12; reverse contrast → 2; Reversing shortening factor → 8; review loop → 12; rhythm → 5; ring → 4; ripple effect → 12; role → 2; row height → 3; rubric → 13; rule → 4, 13

**S**: `@starting-style` → 8; SaaS-card kit → 11, 12; safe area → 5; safe zone → 7; saliency → 13; sans serif → 2; saturation → 1; scale → 9; scale step → 1; scale: small → 7; scaling factor → 3; scoop → 4; Scoping → 9; score profile → 13; screen regions → 5; Screen-within-screen → 7; screenfit → 5; screening → 13; scrim → 4; Scroll-driven animations → 8; secondary → 6; secondary grid → 7; seed → 9, 12; segmented control → 6; select → 6; selected → 6; selection → 1; self-revision → 12; semantic framework → 12; semantic status color → 1; semantic token → 9; semi flat → 11; Sentence case → 2; separation order → 6; separator → 4; sequential palette → 1; serif → 2; Set → 9; severity → 13; shade → 1; shadow border → 6; shadow fill → 6; shape language → 4; shape library → 4; shape morphing → 4; shape scale → 4; sheet → 6; shift → 5; shimmer → 8; shimmer mask → 6; shit → 12; show/hide → 5; showcase → 10; side nav → 5; side navigation → 5; side panel → 6; side sheet → 5; sidebar → 5; signature move → 11; signifier → 11; SIL OFL → 7; single size ramp → 10; single-step transition → 12; size class → 5; size variant → 3; `size-adjust` → 2; skeleton → 6; skeuomorphism → 11; skill → 12; skip link → 5; slashed zero → 2; slider → 6; slot → 6; small caps → 2; `smcp` → 2; snackbar → 6; soft → 1, 6; soft constraint → 12; soft UI → 11; solid → 1; space reservation → 6; space-based decomposition → 13; spacer → 5; spacing exception → 3; spacing scale → 3; spacious → 6; sparkline → 6; spatial frequency → 1; spinner → 6; split button → 6; split pane → 5; spot illustration → 7; spotted → 5; spread → 4; spring → 8; squint test → 13; squircle → 4; `ss01`–`ss20` → 2; stack → 3; stacking context → 4; stagger → 8; standard → 8; starter → 12; stat tile → 6; state delta → 6; state layer → 6; state layers → 6; status dot → 6; status indicator → 7; step → 1; stepper → 6; steps → 12; sticky → 5; sticky header → 5; sticky region → 5; stiffness → 8; straight quotes → 2; stratified → 5; strict value → 13; stroke → 7; stroke contrast → 2; stroke terminal → 7; stroke-width → 7; style → 2; style card → 11; Style Dictionary → 9; style drift → 7; style model → 5; style polarization → 11; style reference → 12; Style tile → 11; style weight → 12; `stylelint-gamut` → 1; stylistic set → 2; sub-pixel rendering → 8; Subband entropy → 13; subgrid → 5; subsetting → 2; subtle → 1, 6; superellipse → 4; supporting pane → 5; surface → 1; surface layer → 9; surface tint → 4; SVG sprite → 7; svh → 5; Swiss style → 11; symmetry → 13; system colors → 1; system font stack → 2; system token → 9

**T**: `$type` → 9; `@theme` → 9; T2I → 12; tab walk → 13; table (dashboard pattern) → 5; tabular figures → 2; tabular numerals → 2; tag → 6, 13; tag input → 6; target size → 3; task similarity → 13; Template chrome → 11; template chrome → 12; tension → 8; tertiary → 6; text → 6; text style → 2; text-augmented prompting → 12; `text-box-trim` → 2; text-to-image model → 12; `text-wrap: balance` → 2; texture → 2; theme → 9; three-area grid → 6; thumb → 6; timing function → 8; tint → 1; tinted neutral → 1; Title Case → 2; `tnum` → 2; toast → 6; token engine → 10; token field → 6; Tokens Studio → 9; tonal → 6; tonal palette → 1; tone → 1; toolbar → 5; tooltip → 6; top bar → 5; top nav → 5; touch target → 3; track → 6; tracking → 2; trailing visual → 6; training centroid → 12; transform → 9; transition → 8; transition token → 8; `transition-behavior: allow-discrete` → 8; trigger width → 5; trim area → 7; tritan → 1; TrueSkill → 13; truncation → 6; two-color focus indicator → 6; type ramp → 2; type scale → 2; type set → 2; typeface → 2

**U**: UI icon → 7; UI-to-code → 12; umbra → 4; underline → 6; undershoot → 8; undersized target → 3; uniwidth → 2; unstyled primitives → 10; `usage` / `rules` / `doNotUse` / `alternatives` → 9

**V**: `$value` → 9; valid critique → 12; value → 1; variable font → 2; variable icon font → 7; variant → 2; vector generation → 12; vectorization → 7; verifiability rule → 12; vertical metrics → 2; vertical rhythm → 2; vestibular trigger → 8; View Transitions API → 8; view–tap asymmetry → 3; violation → 13; Viridis → 1; vision-language model → 12; visited → 6; visual complexity → 13; visual language → 11; visual over-optimism → 12; visual prompting → 13; visual similarity → 13; visual weight → 5; VLM → 12; VLM critic → 13; VLM-as-a-judge → 12

**W**: `-webkit-font-smoothing` → 2; W3C DTCG format → 9; warm / cool neutral → 1; warning → 6; WCAG 1.4.1 Use of Color → 1; WCAG 1.4.12 Text Spacing → 2; WCAG 1.4.4 Resize Text → 2; WCAG 1.4.8 Visual Presentation → 2; WCAG 2.2.2 Pause, Stop, Hide → 8; WCAG 2.3.1 Three Flashes → 8; WCAG 2.3.3 Animation from Interactions → 8; web font → 2; weight → 2; white space ratio → 13; whitespace → 3; widow → 2; width class → 3; width multiplier → 6; `will-change` → 8; window size class → 5

**X**: x-height → 2

**Z**: z-index scale → 4; zebra striping → 6; `zero` → 2; Zero-shot → 13

**Ζ**: ζ → 8

**Ω**: ω_n → 8

**0–9**: 4× coverage → 10

## 16. Указатель по русским терминам

Термин → номер раздела (1–13). Термины с двумя номерами определены в двух разделах в разном смысле.

**B**: Bold против practical → 8

**E**: Eyebrow-лейбл → 11

**F**: F-паттерн → 5

**H**: Hero-иллюстрация → 7

**K**: Keyline-формы, ключевые формы → 7; KPI-плитка → 6

**O**: Origin-aware появление → 8

**P**: Productive против expressive → 10

**R**: Ripple без JS → 6

**S**: «shadcn по умолчанию» → 11; `shadow.ambient` (рассеянный слой, ambient shadow, ambient light) → 4; `shadow.key` (ключевой слой, key shadow, key light) → 4; `shadow.ring` (кольцо, hairline ring) → 4; Spatial и effects → 8; Spot-иллюстрация → 7; «Stripe-стиль» → 11

**Ё**: Ёлочки → 2

**А**: Абзацный отбив → 2; Аватар → 7; Автозаполнение → 5; Автоподгонка → 5; Авторост поля → 6; Алерт → 6; Алиас → 9; Алиас-назначение → 10; Альфа-слой → 6; Аналитический дашборд → 5; Анатомия компонента → 6; Анимация по ключевым кадрам → 8; Антидизайн → 11; Антиква, шрифт с засечками → 2; Антислоп → 13; Апертура → 2; Арт-дирекция → 11; Асимметрия «видно/нажимается» → 3; Аудит → 13; Аффект внимания → 13; Ахроматопсия → 1

**Б**: База, базовый размер → 2; Базовая единица → 3; Базовая единица сетки → 3; Базовая линия → 2; Базовая сетка → 2; Баланс → 13; Балансировка строк → 2; Баннер → 5; Безопасная зона → 5; Бейдж → 6; Белое пространство → 13; Бенто → 11; Библиотека поведения → 10; Библиотека форм → 4; Битая ссылка токена → 12; Блочная кнопка → 6; Боковая навигация → 5; Болгарская кириллица → 2; Большой вьюпорт → 5; Брейкпоинт → 5; Бритва Оккама для систем → 9; Бриф → 11; Брутализм → 11; Бюджет кадра → 8

**В**: Валидная критика → 12; Вариант знака → 2; Веб-шрифт → 2; Ведущий визуал → 6; Векторизация → 7; Векторная генерация → 12; Вертикальные метрики → 2; Вертикальный ритм → 2; Верхний выносной элемент → 2; Верхняя навигация → 5; Верхняя панель → 5; Вес стиля → 12; Вес, насыщенность → 2; Вестибулярный триггер → 8; Видимый фокус → 6; Визуальная сложность → 13; Визуально-языковая модель → 12; Визуальное сходство → 13; Визуальный вес → 5; Визуальный оптимизм → 12; Визуальный промт → 13; Визуальный язык → 11; Висячая пунктуация → 2; Висячая строка → 2; Витрина → 10; Влезает в экран → 5; Влияющий на сетку → 5; Вложенная сетка → 5; Вложенный радиус → 4; Внешние поля страницы → 3; Внешний отступ → 3; Внутренний отступ → 3; Внутренняя раскладка → 5; Внутренняя тень-граница → 4; Вогнутый угол → 4; Воздействие → 13; Воздух, белое пространство → 3; Воспринимаемая длительность → 8; Вспомогательная панель → 5; Вторичная → 6; Выбрано → 6; выдаёт → 11; Выделение → 1; Выключка по формату → 2; Выпадающее меню → 6; Вырез → 4; Высота контрола → 3; Высота прописных → 2; Высота строки списка → 3; Высота, глубина → 4

**Г**: Галация → 1; Галлюцинированный виджет → 12; Гамут → 1; Гарнитура → 2; Гаттер → 5; Гаттер, межколонник → 5; Генератор изображений, текст-в-картинку → 12; Геометрический гротеск → 2; Гибкая панель → 5; Гибридная сетка → 5; гид по компонентам → 11; Глубина цвета → 13; Граница → 4; Граница тенью → 6; Гротеск, рубленый → 2; Группа аватаров, стопка → 7; Группа кнопок → 6; Гуманистический гротеск → 2

**Д**: Дата-пикер → 6; Дашборд → 5; Движение → 8; Движение от действия → 8; Движок токенов → 10; Двойное кольцо → 6; Двойной ринг → 6; Двойной узел → 9; Двухцветное кольцо → 6; Дейтеранопия / дейтераномалия → 1; Декларация → 10; Дельта состояния → 6; Демпфирование → 8; Дерево решений → 12; Деструктивная → 6; Дефолт библиотеки → 12; Дефолты библиотеки → 12; Джиттер → 13; Диаграмма Гутенберга → 5; Дизайн-ревью → 13; Дизайн-система → 10; Дизайн-токен → 9; Динамический вьюпорт → 5; Длина строки, формат → 2; Длинное тире → 2; Длительность → 8; Доля свободного места → 5; Доминирующие цвета → 13; Доступная высота → 5; Дрейф стиля → 7; Дровер → 6; Дровер, выезжающая панель → 6; Дрожание, порча макета → 13

**Е**: Единицы контейнера → 5; Единый ряд размеров → 10

**Ж**: Живая область → 7; Журнальный стиль → 11; Жёсткое ограничение → 12; Жёсткость → 8

**З**: Загрузка → 6; Задачное сходство → 13; Задержка → 8; Зазор → 3; Закон убывающей отдачи → 9; Закон Фиттса → 3; Залежная зона → 5; Заливка тенью → 6; Заливной вариант поля → 6; Замедление, вход → 8; Замыкающий визуал → 6; Запас остроты → 1; Запрет на обработку моделями ИИ → 7; Запрет на обучение ИИ → 7; Запрос к контейнеру → 5; Защитная зона → 7; Зебра → 6; Знак номера → 2; Знак рубля → 2; Зона вставки → 6; Зона загрузки → 6; Зона захвата → 6; Зоны экрана → 5

**И**: Изометрия → 7; Иконка интерфейса → 7; Иконочная кнопка → 6; Именованные области → 5; Инверсная → 6; Инверсная поверхность → 1; Инверсная роль → 1; Индикатор → 6, 12; Индикатор присутствия → 7; Индикатор статуса → 7; Индикатор фокуса → 6; Инициалы → 7; Инктрап → 2; Инлайн-набор → 3; Инлайн-тема → 9; Инлайновое исключение → 13; Инспектор → 5; Инструкция в репозитории → 12; Интерлиньяж → 2

**К**: Канонические раскладки → 5; Капитель → 2; Каппа Фляйсса → 12; Каретка → 6; Каркас кодом → 12; Каркас приложения → 5; Картинка-из-картинки → 12; Карточка по наведению → 6; Карточка стиля → 11; Карточка, которая ничего не делает → 13; Категориальная палитра → 1; Качество комментария → 13; Квадродерево → 13; Кегельная площадка → 2; Кегль, размер шрифта → 2; Кернинг → 2; Клавиша → 6; Класс окна → 5; Класс размера → 5; Класс ширины поля → 3; Кластер маркеров → 13; Клейморфизм → 11; Ключевая линия → 5; Ключевая тень → 4; Ключевой цвет → 1; Кодогенератор UI → 12; Колонка → 5; Колоночная сетка → 5; Кольцо → 4; Кольцо фокуса → 6; Командная палитра → 6; Комбинаторный взрыв → 9; Комбобокс → 6; Компактный алгоритм → 3; Компенсация иконки → 6; Компенсация оттенка → 1; Композитинг альфы → 1; Композитный слой → 8; Компонентный токен → 9; Консистентность → 11; Контактная тень → 4; Контейнер → 6; Контейнерный токен → 3; Контекст наложения → 4; Контекстная полоса → 5; Контекстные альтернативы → 2; Контекстный токен → 9; Контраст WCAG 2 → 1; Контраст фигуры и фона → 13; Контраст штриха → 2; Контрастное отношение WCAG → 1; Контрштрих, внутренняя форма → 7; Контур → 2; Контурная → 6; Концентричные углы → 4; Копируемые компоненты → 10; Короткое тире → 2; Корпоративная классика → 11; Коэффициент затухания → 8; Кратность 4 → 10; Крафт → 11; Кривая хромы → 1; Кривая, функция плавности → 8; Критика → 13; Критический контраст → 1; Крупный текст → 1; Кубическая кривая Безье → 8; Кусочно-линейная шкала → 10

**Л**: Лапки → 2; Лейбл → 6; Ленивая загрузка → 7; Лента → 5; Лестница светлоты → 1; Лигатуры → 2; Линейная → 8; Липкая область → 5; Липкая шапка → 5; Логические свойства → 5; Ложное дно → 5; Локализация замечания → 12; Локальные формы → 2; Локап → 7; Лучший из N → 12

**М**: Магическое значение → 9; Макет-в-код → 12; Максимальная хрома → 1; Малый вьюпорт → 5; Маркер генерации → 11; Маска → 13; Маска-шиммер → 6; Масса → 8; Мастер-детали → 5; Масштаб SF Symbols → 7; Масштабный множитель → 3; Машинный отчёт → 12; Машиночитаемое самоописание → 12; Маюскульные цифры → 2; медианная эстетика → 11; Мера строки → 2; Метрический фолбэк → 2; Мини-юнит → 3; Минимакс → 5; Минимализм → 11; Минус → 2; Минускульные, старостильные цифры → 2; Многошаговая траектория → 12; Множитель ширины → 6; Мода → 10; Модалка → 6; Модальное окно → 6; Модальность правила → 9; Модель как судья → 12; Модель раскладки за максимумом → 5; Модель слоёв → 10; Модель-критик → 13; модификатор → 9; Модульная сетка → 5; Модульная шкала → 2; Монохромный вариант → 7; Моноширинный → 2; Морфинг формы → 4; Мудборд → 11; Мультиреференс → 12; Мягкое ограничение → 12; Мёртвый токен → 9

**Н**: набор → 9; Набор SaaS-карточек → 12; Набор примитивов → 10; Наведение → 6; Нажатие → 6; Наложение высоты → 4; Нарушение → 13; Насыщенность → 1; Начертание → 2; Невидимая граница → 6; Негативное пространство → 3; Негативный промт → 12; Недоразмерная цель → 3; Нейрослоп → 11; Нейтраль, нейтральная шкала → 1; Нейтраль-вариант → 1; Необрутализм → 11; Неогротеск → 2; Неоморфизм → 11; Неопределённое → 6; неопределённость клика → 11; Непрерывные углы → 4; Неприменимо → 13; Неразрывный пробел → 2; Нижний выносной элемент → 2; Нижний лист → 5

**О**: Обводка → 4; Обводка аватара → 7; Обогащение текстом → 12; Обратный контраст → 2; Обратный маршрут → 12; Обрезка полулидинга → 2; Обход → 5; Обход табом → 13; Оверлей → 3; Оверлей высоты → 4; Овершут → 7; Однородность → 13; Операционный дашборд → 5; Оптимизированный бриф → 13; Оптическая компенсация → 3; Оптическая коррекция → 5; Оптическая поправка → 5; Оптический вес → 7; Оптический размер → 2; Оптический центр → 5; Оптическое выравнивание → 5; Оптическое выравнивание логотипов → 7; Опущенные секции → 12; Ортогональность → 9; Осиротевший токен → 12; Ось → 2; Ось темизации → 9; Отключено → 6; Открытая раскладка → 5; Открытые веса → 12; Отметка → 5; Отмечено → 6; Относительная яркость → 1; Отображение в гамут → 1; Отрицательное поле слота → 6; Отрицательный отступ → 3; Отступ от столкновения → 5; Оттенок → 1; Оттенок поверхности → 4; Ошибка → 6

**П**: Пакет инструкций → 12; Панель → 5; Панель инструментов → 5; Панель свойств, инспектор → 5; Параметризация → 5; Парные тона → 6; Парный контентный цвет → 1; Паспорт системы → 7; Первичная → 6; Первичная и вторичная сетки → 7; Переворот → 5; переключателя → 6; Перелёт → 8; Переменный шрифт → 2; Переменный шрифт-иконки → 7; Переполнение → 5; Пересечение по объединению → 13; Перетаскивание → 6; Перетекание → 5; Переход → 8; Переход состояния за один шаг → 12; Перечёркнутый ноль → 2; Пертурбация → 12; Петля самоусиления → 11; Пиктограмма → 7; Пилюля → 4; Плавающая панель → 5; Плавающий лейбл → 6; Плавная типографика → 2; Плейсхолдер → 6; плитка стиля → 11; Плоская перспектива → 7; Плоский дизайн → 11; Плотность → 3; Плотность контуров → 13; Плотность указателя → 3; Плотный режим → 6; «Плотный тёмный инструмент» → 11; По продуктам против по вхождениям → 10; Поверхность → 1; Повтор, чередование, градация → 5; Подложка состояния → 6; Подсветка изменившегося → 8; Подсед → 8; Подсказка → 6; Подчёркнутый вариант → 6; Подъём при наведении → 4; Покой → 6; Поле с заливкой → 4; Поле с обводкой → 4; Поле сетки → 5; Поле тегов → 6; Полиерархия → 9; полированный слоп → 11; Полнота → 9; Полный радиус → 4; Полулидинг → 2; Полутень → 4; Полушаг → 10; Поляризация стиля → 11; Полярность контраста → 1; Попарное сравнение → 13; Поповер → 6; Порог диффа → 13; Порог приёмки → 13; Портал → 4; Порядок разделения → 6; Посещено → 6; Последовательная палитра → 1; Похожесть по CLIP → 12; «Почти, но не совсем» → 13; Правая панель → 5; Правило → 13; Правило близости → 3; Правило верифицируемости → 12; Правило внутреннего и внешнего → 3; Правило кругов → 3; Правило «не только цветом» → 1; Правило трёх компонентов → 9; Практика → 10; Предупреждение → 6; Прерываемость → 8; Префикс / суффикс → 6; Привязка к координате → 12; Приглушение в тёмной теме → 7; Прилипание → 5; Примитив → 9; Принудительные цвета → 1; Приёмка → 12; Приёмочный шлюз → 13; Программистские кавычки → 2; Произвольное значение → 13; Пропорциональные цифры → 2; Просторный режим → 6; Пространственная сегментация → 13; Пространственная частота → 1; Пространство имён Tailwind → 9; Протанопия / протаномалия → 1; Протокол контекста модели → 12; Прототипичность → 13; Профиль вместо балла → 12; Профиль оценки → 13; Прочерк `—` → 10; Пружина → 8; Псевдотокен → 9; Пустое состояние → 6; Пятнистое сканирование → 5; Пять приёмов адаптации → 5

**Р**: Рабочая область → 5; Равновесие → 13; Радиус скругления → 4; Радуга → 1; Разброс → 4; Раздел «делай / не делай» → 12; Разделитель → 4; Разделитель панелей → 5; Разделённая кнопка → 6; Разделённые панели → 5; Размерный вариант → 3; Размытие → 4; Размытие подложки → 4; Раскрыто → 6; Рассеянная тень → 4; Растянутый внутренний отступ → 3; Расходящаяся палитра → 1; Расширенная зона нажатия → 3; Реализм → 11; Регрессия к среднему → 12; Регрессия правки → 12; Режим → 9; Режим отрисовки → 7; Режим плотности → 3; Резервирование места → 6; Резиновая сетка → 5; Рейка → 5; Рельс → 5; Референс стиля → 12; Ритм → 5; Роль → 2; Рост строчных → 2; Рубрика → 13; Рукописная сетка → 5; Ручка → 6; Ручка дровера → 6; Ручка узнаваемости → 13; Ручка характера → 11

**С**: Сабсеттинг → 2; Сайдбар → 5; Самокритика → 12; Светлота → 1; Сгиб → 5; Сглаживание → 2; Сглаживание углов → 4; Сгруппированная раскладка → 5; Сгущение контуров → 13; Сдвиг → 5; Сдвиг оттенка → 1; Сдвиг раскладки → 5; Сдержанность → 11; Сегментированный переключатель → 6; Селект → 6; Семантический алиас → 9; Семантический токен → 9; Семантический токен движения → 8; Семь ручек характера → 11; Серьёзность → 13; Сетка из трёх зон → 6; Сжатый внутренний отступ → 3; Сигнификатор → 11; Сид → 12; Симметрия → 13; Симуляция дальтонизма → 10; Система иллюстраций → 7; Системные цвета CSS → 1; Системный стек → 2; Скаффолд → 5; Сквиркл → 4; Скевоморфизм → 11; Скелетон → 6; Скилл → 12; Скос → 4; Скрим → 4; Скрим, подложка → 4; Скрининг → 13; Скрытие лейбла при загрузке → 6; Слайдер → 6; Слепая зона → 13; Слои состояний → 6; Слоистая раскладка дашборда → 5; Слой → 1; Слой поверхности → 9; Слой состояния → 6; Слоп в интерфейсе → 11; Слот → 6; Слоёная тень → 4; Слоёный пирог → 5; Смещение → 5; Смещение кольца → 6; Смещение слоя → 3; Собственная частота → 8; Совпадение блоков → 12; Соединение линий → 7; Соотношение сторон → 7; Соотношение сторон блока → 7; Составной тип → 9; Составной токен перехода → 8; Спарклайн → 6; Спиннер → 6; Сплошной стиль статуса → 1; Спрайт → 7; Средний обратный ранг → 12; Ссылка пропуска → 5; Стаггер → 8; Стандартная → 8; Стартовое приложение → 12; Статусный цвет → 1; Стек → 3; Стекло → 11; Стеклянный стиль → 11; Степпер → 6; Стилевая плитка → 11; Стилистический набор → 2; Строгое значение → 13; Субпиксельный рендер → 8; Субтильный стиль статуса → 1; Суперэллипс → 4; схлопывание модели → 11; Сходство модификации кода → 12; Сходство позиции → 12; Сходство цвета → 12

**Т**: Табличная раскладка → 5; Табличные цифры → 2; Тег → 6; Тег правила → 13; Текст ошибки → 6; Текстовая → 6; Текстура шрифта → 2; Тема → 9; Тень-подсказка переполнения → 4; Терминал штриха → 7; Тест выброшенного контента → 11; Тест на прищур → 13; Тест прищура → 13; Тест «ухо» → 2; Тинт → 1; Тип контейнера → 5; Тип-сет → 2; Типографическая шкала → 2; Токен длительности → 8; Токен кривой → 8; Токен-keyframe → 8; Только чтение → 6; Тон → 1; Тональная → 6; Тональная палитра → 1; Тонирование нейтрали → 10; Тонированная нейтраль → 1; Тост → 6; Тост, снэкбар → 6; Точка высокого контраста → 5; Точка-статус → 6; Точность рейтинга → 13; Трансформ → 9; Требует проверки → 13; Трек → 6; Трекинг, межбуквенное расстояние → 2; Третичная → 6; Три визуальных поколения → 11; Тританопия → 1; Тултип → 6; Тёплая / холодная нейтраль → 1

**У**: Уезжающая панель → 5; Узкий неразрывный пробел → 2; Униширинный → 2; Управляющая карта → 12; Усечение → 6; Ускорение, выход → 8; Устойчиво нажато → 6

**Ф**: Фасет имени → 10; Фиксированная панель → 5; Фиксированная сетка → 5; Фирменный приём → 11; Флайаут → 5; Фокус → 6; Фокус внутри → 6; Фокус-ринг → 6; Формат токенов W3C → 9; Формы под прописные → 2

**Х**: Хеш-цвет → 7; Хинтинг → 2; Хлебные крошки → 6; Холст, кадр → 7; Хореография → 8; Хрома → 1

**Ц**: Цветность → 13; Цель нажатия → 3; Центроид обучающих данных → 12; Цикл правок → 12; Цифровой водяной знак → 12

**Ч**: Частичный радиус → 4; Частотность цвета → 12; Чек-лист → 13; Четыре уровня семантик → 12; Чип → 6; Чистый оттенок → 1; Чистый серый → 1

**Ш**: Шаблонная обвязка → 12; шаблонный хром → 11; Шаг плотности → 3; Шаг шкалы → 1; Шаги → 12; Шапка страницы → 5; Швейцарский стиль → 11; Шейд → 1; Шиммер → 8; Ширина триггера → 5; Шкала → 9; Шкала z-index → 4; Шкала отступов → 3; Шкала плотности → 3; Шкала точности артефактов → 11; Шкала форм → 4; Шлак → 12; Шрифтовая иконка → 7; Штрих → 7

**Э**: Экономность → 13; Эмодзи → 7; Эмодзи-стек → 7; Эмуляция медиа → 13; Эстетико-юзабилити эффект → 13; Эталон → 13; Эффект расползания → 12; Эффект эстетики и юзабилити → 13; Эффективный фон → 13

**Я**: Ядро тени → 4; Язык форм → 4; Якорение → 1; Якорный объект → 5; Якорь балла → 13; Якорь шкалы → 13; Яркость → 1
