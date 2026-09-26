# Контраст: WCAG 2, APCA, пороги по ролям, цветовая слепота

Волна 1 · агент A · 22.09.2026 · источников прочитано целиком: 34

Контраст здесь рассматривается как визуальная величина: какие числа обязаны выполняться и как их считать.
Доступность как процесс (клавиатура, разметка, тестирование со скринридером) — в `../../ux/08-accessibility/`.

---

## Выжимка для агента

1. **Считай оба: WCAG 2 обязателен юридически, APCA точнее.** Если расходятся — выполняй WCAG 2 и стремись
   к APCA. → §4 `[консенсус]`
2. **WCAG 2 AA: 4.5:1 обычный текст, 3:1 крупный, 3:1 нетекстовые элементы и их состояния.** AAA: 7:1 и 4.5:1.
   → §1 `[исследование]` (это норматив)
3. **Крупный текст = 18 pt (24 px) или 14 pt bold (≈ 18.67 px), где bold — `font-weight` ≥ 700.** → §1.2 `[консенсус]`
4. **Округлять нельзя.** #777777 даёт 4.47:1 и не проходит 4.5:1 [S26]. → §1.1
5. **APCA: Lc 90 предпочтительно для body, Lc 75 минимум для body, Lc 60 для прочего читаемого текста, Lc 45 для
   крупного, Lc 30 для плейсхолдеров и disabled, Lc 15 — порог видимости.** → §2.2 `[исследование]`
6. **Lc 90 — рекомендуемый МАКСИМУМ для шрифтов больше 24–36 px и больших площадей цвета.** «More is not always
   better» [S19]. → §2.2
7. **WCAG 2 завышает контраст в тёмной теме.** Проверено мной: #777777 на чёрном = WCAG 4.69:1 (проходит AA), но
   APCA Lc −30.6 (уровень «еле разобрать»). → §4.1 `[исследование]`
8. **WCAG 2 применим только к светлой теме.** «WCAG 2 values are intended for light-mode only, meaning the
   background is never darker than the equivalent of approximately #aaa» [S19]. → §4.1
9. **Контраст сильнее зависит от размера и толщины, чем от цвета.** В примере Somers переход обводки с 1 px на
   4 px при одном цвете (3:1) даёт больший прирост читаемости, чем поднятие контраста с 3:1 до 7:1. → §2.3
   `[исследование]`
10. **Пороги по ролям** (таблица в §3): основной текст ≥ 7:1 фактически (системы дают 11.7–19.8:1), вторичный
    4.7–6.2:1, третичный 3–4.5:1, отключённый 1.8–3.5:1 (не нормируется), граница контрола ≥ 3:1, фокус-ринг
    ≥ 3:1 к обоим соседям. → §3
11. **Отключённые элементы освобождены от требований контраста** (WCAG 1.4.3 «Incidental», 1.4.11 «inactive
    components») — но APCA всё равно требует Lc 30. → §3.4 `[спорно]`
12. **Плейсхолдер — это текст, и на него 4.5:1 распространяется**, если он несёт информацию. APCA относит
    «non-informative placeholder text» к Lc 30. → §3.3 `[спорно]`
13. **Ссылка без подчёркивания внутри текста требует ОДНОВРЕМЕННО 4.5:1 к фону и 3:1 к цвету обычного текста**
    плюс невизуальный признак при фокусе. Часто это невозможно — подчёркивай. → §7 `[исследование]`
14. **Считай контраст ПОСЛЕ композитинга альфы.** Полупрозрачная граница `white/10%` на тёмном фоне — это
    конкретный непрозрачный цвет, его и меряй. → §6.1 `[консенсус]`
15. **Нетекстовый контраст меряется «to adjacent colors», то есть со всех сторон.** Иконка внутри плашки — два
    измерения: иконка↔плашка и плашка↔фон [S26]. → §5.1
16. **CVD не влияет на потребность в контрасте светлоты.** «For readability, deutan, protan, tritan types have the
    same needs for lightness contrast as standard vision» [S19]. → §8.1 `[исследование]`
17. **Единственное исключение — красный на чёрном.** Для протанопии контраст «greatly diminished»; пара
    красный/чёрный запрещена для текста и смысловой графики [S19]. → §8.1 `[исследование]`
18. **Проверяй палитру симуляцией CVD и в ч/б.** Инструменты: `culori.filterDeficiency*`, myndex.com/CVD/. → §8.3
19. **Чистый чёрный текст на чистом белом не оптимален.** Разница между #fff, #eee и #ddd значима для снижения
    усталости от яркости; цвета темнее #222 функционально не отличаются от #000 [S19]. → §9 `[мнение]`
20. **Не поднимай контраст выше нужного у крупных элементов.** «Excess contrast is nearly always due to excess
    brightness. When something is so contrasty that it seems to have halos, the first thing to try is to make the
    lightest element a little darker» [S19]. → §9 `[исследование]`

---

## 1. WCAG 2.x: что именно требуется

### 1.1. Определение

Контраст в WCAG 2 — отношение относительных яркостей:

```
FUNCTION relative_luminance(hex):
    (r, g, b) = hex → 0..1
    lin(c) = (c <= 0.04045) ? c / 12.92 : ((c + 0.055) / 1.055) ^ 2.4
    RETURN 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b)

FUNCTION wcag_contrast(a, b):
    (L1, L2) = sorted([relative_luminance(a), relative_luminance(b)], desc)
    RETURN (L1 + 0.05) / (L2 + 0.05)
```

Диапазон 1:1 … 21:1. Перестановка текста и фона результат не меняет.

«В WCAG 2 фраза "color contrast" не используется вообще» — речь только о разнице яркости [S26]. Значит два цвета
с одинаковой яркостью и разным оттенком дают контраст 1:1, как бы «по-разному» они ни выглядели.

Отсюда следуют неочевидные значения (из [S26], проверено мной):

| Цвет на белом | WCAG |
|---|---|
| Чистый красный #FF0000 | **4:1** (не проходит) |
| Чистый зелёный #00FF00 | **1.4:1** |
| Чистый синий #0000FF | 8.6:1 |
| #767676 | 4.54:1 (проходит) |
| #777777 | 4.47:1 (**не проходит**) |

«You cannot round a contrast ratio up to 4.5:1» [S26].

Примеры ровно на границе 4.5:1: серый #767676 на белом; пурпурный #CC21CC на белом; синий #000063 на сером
#808080; красный #E60000 на жёлтом #FFFF47. «For many of us, some of these combinations are not very readable.
That is why 4.5:1 is the minimum» [S26].

### 1.2. Три критерия

| Критерий | Уровень | Требование |
|---|---|---|
| 1.4.3 Contrast (Minimum) | AA | 4.5:1 для текста, 3:1 для крупного текста |
| 1.4.6 Contrast (Enhanced) | AAA | 7:1 для текста, 4.5:1 для крупного |
| 1.4.11 Non-text Contrast | AA (с WCAG 2.1, июнь 2018) | 3:1 к соседним цветам для компонентов, их состояний и значимой графики |
| 1.4.1 Use of Color | **A** | цвет не единственный носитель смысла |

Крупный текст: **18 pt и больше, или 14 pt и больше при bold**. В пикселях: 18 pt = 24 px, 14 pt ≈ 18.67 px.
Bold — «`font-weight: bold`, или `font-weight: 700` или больше» [S26].

WCAG 2.2 не изменил требования к контрасту: «The WCAG 2.2 criterion for Contrast (minimum) is the same as
WCAG 2.1» [S13].

### 1.3. Исключения из 1.4.3

Четыре категории «incidental» текста [S26]:
1. **Inactive** — отключённый элемент, «identified visually by its lower-contrast state»;
2. **Pure decoration** — декоративный текст, не предназначенный для чтения;
3. **Not visible to anyone** — скрытый (например skip-link до фокуса);
4. **Part of a picture that contains significant other visual content** — бейдж на футболке человека на фото.

Плюс **логотипы**: «Text that is part of a logo or brand name has no contrast requirement».

Правило отсечения от WebAIM: «text that would be part of the image's alternative text should probably meet
contrast requirements while text that would not be added to alternative text can usually be considered
incidental».

### 1.4. Обводка и свечение

- Цвет обводки текста может считаться цветом текста при измерении;
- свечение (halo) вокруг букв считается фоном [S26].

### 1.5. Что WCAG 2 не покрывает

- **Градиенты, фоновые изображения, полупрозрачность.** «WCAG does not provide any guidance on how to measure
  their contrast. We recommend usually testing the area where contrast is lowest» [S26].
- **Состояния hover/focus/active текста** — упоминания нет, значит каждое состояние проверяется независимо и по
  тем же порогам.

---

## 2. APCA

### 2.1. Что это и статус

APCA (Accessible Perceptual Contrast Algorithm) — метод Andrew Somers (Myndex), часть модели SACAM. Статус на
2026 год:
- «APCA is the candidate contrast method for the future WCAG 3» [S7];
- параллельно существует независимый стандарт **APCA Readability Criterion (ARC)** под эгидой НКО Inclusive
  Reading Technologies (readtech.org/ARC), помеченный как бета: «Content in this resource is still under active
  development and should be considered beta» [S27];
- WCAG 3 не принят, APCA **не является юридическим требованием** ни в одной юрисдикции. Somers прямо пишет: «one
  needs to determine if they have any contractual or other legal requirements to follow the older WCAG 2,
  regardless of WCAG 2's deficiencies» [S19].

Вывод для агента: **APCA — инструмент качества, WCAG 2 — инструмент соответствия.** Выпускай интерфейс,
удовлетворяющий обоим.

### 2.2. Шкала Lc

Величина Lc (lightness contrast) от 0 до ±106. Знак кодирует полярность: **положительный Lc — тёмный текст на
светлом (светлая тема), отрицательный — светлый текст на тёмном** [S7]. При использовании таблиц берётся модуль.

Уровни Bronze Simple Mode [S27], справочный шрифт Helvetica/Arial, отношение x-height 0.52, CSS reference px:

| Lc | Что это | Минимальные размеры |
|---|---|---|
| **90** | предпочтительный для body и колонок текста | 18 px/300 или 14 px/400; не-body от 12 px/400; очень тонкие от 24 px/200. Рекомендуемый МАКСИМУМ для > 36 px bold и больших площадей цвета |
| **75** | минимум для колонок body-текста | 24 px/300, 18 px/400, 16 px/500, 14 px/700; не-body от 15 px/400 |
| **60** | минимум для текста, который читают, но не body | 48 px/200, 36 px/300, 24 px/400, 21 px/500, 18 px/600, 16 px/700 |
| **45** | минимум для крупного и жирного (36 px/400 или 24 px/700), заголовков; минимум для пиктограмм с мелкими деталями и тонких контурных иконок | |
| **30** | абсолютный минимум для прочего текста: плейсхолдеры, текст отключённых элементов, копирайт; минимум для «в основном сплошных» иконок не тоньше 5.5 px | |
| **15** | абсолютный минимум для несмысловой нетекстовой графики не тоньше 5 px: разделители, иногда крупные кнопки и толстые фокус-обводки. «Designers should treat anything below this level as invisible» | |

Аналог AAA = уровни + Lc 15. Максимум для тёмной темы: Lc −90 для крупных шрифтов (preliminary) [S7].

Bronze Conformance Minimums дословно [S27]:
- Body Text: минимум Lc 75, предпочтительно Lc 90;
- Other Content Text: минимум Lc 60;
- Large Fluent Content (> 36 px): минимум Lc 45, **максимум Lc 90**.

Три уровня соответствия ARC: BRONZE (только основной контентный текст, без таблиц шрифтов), SILVER (весь текст,
таблица «вес/размер ↔ Lc»), GOLD (то же + сверка с эталонным шрифтом и поправка веса/размера) [S27].

### 2.3. Почему размер важнее цвета

«Contrast is driven more by "spatial frequency" than by the difference or ratio between two colors» [S19].
Практическая демонстрация из статьи: одинаковый цвет (контраст 3:1), обводка 1 px → 2 px → 3 px → 4 px; рост
читаемости больше, чем при переходе с 3:1 на 7:1 при той же толщине.

Из того же источника:
- «normal weight fonts about 18 px and smaller just become subsumed by the background due to typical
  antialiasing»;
- `-webkit-font-smoothing: antialiased` «wreaks havoc on standard resolution displays with small fonts» —
  применять только за media query по разрешению;
- дизайн надо проверять на обычном (не Retina) мониторе в sRGB.

Эмпирическая база ARC (исследования Lovie-Kitchin и др.) [S27]:

| Скорость чтения | Минимальный запас остроты |
|---|---|
| Spot (~40 слов/мин) | 1.3:1 (0.1 log, 1 строка таблицы) |
| Fluent (≥ 100 слов/мин) | 2:1 (0.3 log, 3 строки) |
| Максимальная | 3:1 … 8:1 (0.5–0.9 log, 5–9 строк) |

«At least ten times more contrast is needed for good readability than the bare minimum contrast needed for
legibility» [S27]; «the preferred contrast reserve is twenty times threshold for best fluent reading» [S7].

### 2.4. Формула (реализована и проверена)

Реализация APCA 0.1.9 (W3/Myndex). Я реализовал её в Python и сверил с официальным калькулятором:
чёрный на белом → Lc **106.0**, белый на чёрном → Lc **−107.9**, #888888 на белом → Lc **63.1**.

```
CONSTANTS: Bclip = 1.414, Bthrsh = 0.022, Wscale = 1.14, Woffset = 0.027
           Rco = 0.2126729, Gco = 0.7151522, Bco = 0.0721750
           Ntx = 0.57, Nbg = 0.56   (нормальная полярность)
           Rtx = 0.62, Rbg = 0.65   (обратная полярность)

FUNCTION apca_Y(hex):
    (r, g, b) = hex → 0..1
    RETURN Rco * r^2.4 + Gco * g^2.4 + Bco * b^2.4      # ВНИМАНИЕ: простая степень 2.4, не sRGB-кривая

FUNCTION soft_clamp(Y):
    RETURN (Y > Bthrsh) ? Y : Y + (Bthrsh - Y)^Bclip

FUNCTION apca(text_hex, bg_hex):
    Ytxt = soft_clamp(apca_Y(text_hex))
    Ybg  = soft_clamp(apca_Y(bg_hex))
    IF |Ybg - Ytxt| < 0.0005: RETURN 0
    IF Ybg > Ytxt:                                       # тёмный текст на светлом
        S = (Ybg^Nbg - Ytxt^Ntx) * Wscale
        out = (S < 0.1) ? 0 : S - Woffset
    ELSE:                                                # светлый текст на тёмном
        S = (Ybg^Rbg - Ytxt^Rtx) * Wscale
        out = (S > -0.1) ? 0 : S + Woffset
    RETURN round(out * 100, 1)
```

Два критичных отличия от WCAG 2:
1. **Порядок аргументов важен.** «Do not swap the foreground & background colors in the tool entry fields. The
   contrast evaluation is based in part on polarity» [S27].
2. **Показатели степени разные для текста и фона** (0.57/0.56 против 0.62/0.65) — это и есть учёт полярности.

---

## 3. Пороги по ролям

### 3.1. Сводная таблица

Колонка «Реальные значения» — посчитано мной по исходникам дизайн-систем.

| Роль | WCAG 2 | APCA | Реальные значения систем |
|---|---|---|---|
| Основной текст | ≥ 4.5:1 (AA) / 7:1 (AAA) | Lc 75 мин., 90 предпоч. | Primer 15.80:1 / Lc 102.8; Polaris 11.69:1 / 91.2; GOV.UK 19.59:1 / 105.8; shadcn 19.80:1 / 105.8; Radix slate12 15.98:1 / 101.6 |
| Вторичный текст | ≥ 4.5:1 | Lc 75 если body, 60 если нет | Primer 6.11:1 / 80.5; Polaris 5.48:1 / 72.6; Radix slate11 5.79:1 / 78.0; shadcn 4.74:1 / 72.9; GOV.UK 9.03:1 / 90.8 |
| Третичный текст, подпись | ≥ 4.5:1 (если контентный) | Lc 60 | Tailwind gray-500 4.84:1 / 73.6 |
| Плейсхолдер | ≥ 4.5:1, если информативен | Lc 30 если неинформативен | Primer использует `fgColor.muted` 6.11:1 |
| Отключённый текст | не нормируется | Lc 30 | Primer 3.45:1 / 62.1; Polaris 1.82:1 / 31.6 |
| Иконка значимая | ≥ 3:1 (1.4.11) | Lc 45 контурная / 30 сплошная | Polaris icon 7.85:1; icon-secondary 3.06:1 |
| Граница контрола, поля ввода | ≥ 3:1 (1.4.11) | Lc 15–30 | Primer 3.45:1; Polaris input-border 3.06:1; **shadcn 1.26:1 (провал)**; Tailwind gray-300 1.47:1 (провал) |
| Разделитель, граница карточки | не нормируется | Lc 15 | Primer 1.43:1; Polaris 1.14:1; Radix slate6 1.37:1 |
| Фокус-ринг | ≥ 3:1 к обоим соседям | Lc 15–45 | Polaris `border-focus` blue[13] 6.11:1 к белому; **shadcn ring 2.58:1 (провал)** |
| Сплошной акцент (кнопка) | ≥ 3:1 как компонент | Lc 60+ для текста на нём | Radix шаг 9 нейтрали 3.22:1; Polaris blue[13] 6.11:1 |
| Текст на сплошном акценте | ≥ 4.5:1 | Lc 75 | Polaris success 5.20:1 / −80.0; critical 5.81:1 / −80.3; emphasis 6.00:1 / −83.4 |

### 3.2. Справочная таблица «серый на белом»

Посчитано мной, обе метрики:

| hex | OKLCH L | WCAG | APCA Lc | Для чего годится |
|---|---|---|---|---|
| #303030 | 30.9 % | 13.20:1 | 99.6 | основной текст |
| #404040 | 37.1 % | 10.37:1 | 94.1 | основной текст |
| #505050 | 43.1 % | 8.06:1 | 88.0 | основной текст / AAA |
| #595959 | — | 7.00:1 | 84.3 | ровно AAA |
| #606060 | 48.9 % | 6.29:1 | 81.3 | вторичный текст |
| #707070 | 54.5 % | 4.95:1 | 74.3 | вторичный текст, граница AA |
| #767676 | — | 4.54:1 | 71.6 | ровно AA для текста |
| #808080 | 60.0 % | 3.95:1 | 66.9 | не текст; иконка, граница |
| #909090 | 65.3 % | 3.19:1 | 59.1 | граница контрола (в притык) |
| #949494 | — | 3.00:1 | 57.1 | ровно 3:1 |
| #a0a0a0 | 70.6 % | 2.61:1 | 51.0 | только декор |
| #b0b0b0 | 75.7 % | 2.17:1 | 42.7 | только декор |
| #b7b7b7 | — | 2.00:1 | 38.9 | отключённое состояние |
| #c0c0c0 | 80.8 % | 1.82:1 | 34.0 | разделитель |

Заметь: **WCAG 4.5:1 ≈ APCA Lc 71.6 на белом фоне**, то есть чуть ниже порога Lc 75 для body. Это согласуется с
позицией Accessible Palette: «considers score 60 as the minimum level recommended for readable text, similar to
the old 4.5:1» [S22] — но Myndex требует 75. Расхождение стоит знать: **Lc 60 ≈ «мягкая» трактовка,
Lc 75 ≈ строгая.**

### 3.3. Плейсхолдер: спор

| Источник | Позиция |
|---|---|
| WCAG 2 / WebAIM | Плейсхолдер — текст. Исключений для него нет, значит 4.5:1 [S26] |
| APCA / ARC | «non-informative placeholder text» относится к spot readability → Lc 30 [S27] |
| Primer | `fgColor.muted` (тот же, что вторичный текст) с пометкой usage «placeholder» → 6.11:1 [S8] |
| shadcn | `muted-foreground` → 4.74:1 [S15] |

Рекомендация: **делай плейсхолдер как вторичный текст (4.7–6:1)**. Это проходит и WCAG, и APCA Lc 60+, и вдобавок
плейсхолдер в реальных формах почти всегда информативен (формат, пример значения).

### 3.4. Отключённое состояние: спор

- WCAG 1.4.3 явно освобождает: «Inactive: An inactive element, like a disabled Submit button, is identified
  visually by its lower-contrast state» [S26];
- WCAG 1.4.11 тоже: «except for inactive components» [S26];
- APCA требует Lc 30 минимум [S7];
- Material традиционно задаёт `opacity: 38 %` для отключённого контента;
- Polaris даёт `color-text-disabled` = gray[11] = 1.82:1 / Lc 31.6 — то есть ровно на границе APCA Lc 30;
- Primer даёт `fgColor.disabled` = neutral.8 = 3.45:1 / Lc 62.1 — существенно выше.

Рекомендация: **целиться в Lc 30–45 (примерно 2–3.5:1)**. Ниже — пользователь не поймёт, что элемент вообще
существует; выше — не поймёт, что он отключён. Подробнее про механику (opacity против отдельных токенов) —
`05-states-and-interaction.md`, §4.

### 3.5. Граница поля ввода: системная проблема

> Разрешение противоречия [C1]: по умолчанию и для любого сгенерированного интерфейса граница поля ≥ 3:1 (в эталонной схеме `border.strong` neutral-500: 4.76 / 3.07); режим практики 1.2–1.5:1 (медиана 24 продуктов 1.30) допустим только в плотной админке при лейбле снаружи, заливке поля и кольце фокуса 2 px ≥ 3:1. См. `../CONTRADICTIONS.md`.

Исключение WCAG: «If you use the default styles provided by the browser, then these contrast requirements do not
apply. In Chrome, the default border for a text box has 2.4:1 contrast… but since this color was determined by the
browser and was not customized by the author, it is exempt» [S26]. WebAIM тут же добавляет: «Because of the low
default contrast, we recommend using CSS to increase the contrast for text boxes and other form inputs.»

Как только автор задаёт `border-color` сам, исключение перестаёт действовать и нужны 3:1.

Проверено мной: **shadcn (`--input` = #e5e5e5, 1.26:1), Tailwind-практика (`border-gray-300`, 1.47:1) и Radix
(slate7 1.53:1, slate8 1.86:1) в дефолте это требование не выполняют.** Выполняют Primer (3.45:1) и Polaris
(3.06:1).

Минимальный серый для 3:1 на белом — **#949494**. Это и есть нижняя граница для границы поля в светлой теме.

---

## 4. Где WCAG 2 и APCA расходятся

### 4.1. Тёмная тема

Проверено мной, светлый текст на тёмном фоне:

| Текст | Фон #000000 | Фон #0a0a0a | Фон #0D1117 | Фон #121212 |
|---|---|---|---|---|
| #ffffff | 21.00:1 / Lc −107.9 | 19.80 / −107.7 | 18.92 / −107.4 | 18.73 / −107.3 |
| #e5e5e5 | 16.67 / −91.0 | 15.72 / −90.9 | 15.02 / −90.5 | 14.87 / −90.4 |
| #a1a1a1 | 8.13 / **−51.4** | 7.66 / −51.2 | 7.32 / −50.9 | 7.25 / −50.8 |
| #9198A1 (Primer muted) | 7.21 / **−46.3** | 6.80 / −46.1 | **6.50 / −45.8** | 6.43 / −45.7 |
| #737373 | 4.43 / **−28.7** | 4.18 / −28.6 | 3.99 / −28.2 | 3.95 / −28.2 |
| #777777 | **4.69 / −30.6** | — | — | — |
| #595959 | 3.00 / −17.7 | 2.83 / −17.5 | 2.70 / −17.2 | 2.67 / −17.1 |

Читается так:
- **#777777 на чёрном проходит WCAG AA (4.69:1), но по APCA это Lc 30.6 — уровень «плейсхолдер и disabled».**
  То есть WCAG 2 разрешает то, что читать нельзя.
- **Вторичный текст Primer в тёмной теме (#9198A1 на #0D1117) даёт отличные 6.50:1 по WCAG, но всего Lc −45.8 —
  ниже минимума Lc 60 даже для не-body текста.** Это уже не гипотетический пример, а реальный продакшен-токен
  крупнейшей системы.

Формулировка Myndex: «WCAG 2.x far overstates contrast for dark colors. The WCAG 4.5:1 ratio can be functionally
unreadable when a color is near black. As a result, WCAG 2.x contrast cannot provide useful guidance when
designing dark mode» [S7].

И прямое ограничение применимости: «WCAG 2 values shown are intended for light-mode only, meaning the background
is never darker than the equivalent of approximately #aaa» [S19].

**Практическое правило для тёмной темы:** вторичный текст в тёмной теме должен быть заметно светлее, чем кажется
по WCAG. Ориентир — APCA Lc 60 минимум, то есть примерно #b4b4b4 и светлее на фоне #111.
Radix dark slate11 = #b0b4ba даёт Lc −61.0, и это правильно подобрано.

### 4.2. Оранжевый и жёлтый

Проверено мной:

| Пара | WCAG | APCA |
|---|---|---|
| белый на #f59e0b (amber-500) | 2.15:1 | Lc −46.4 |
| чёрный на #f59e0b | 9.78:1 | Lc 62.2 |
| белый на #dd6b20 | 3.39:1 | Lc −66.2 |
| белый на #e17100 (amber-600) | 3.20:1 | Lc −63.9 |
| белый на #ff6b00 | 2.86:1 | Lc −59.0 |

Здесь расхождение в другую сторону: **белый текст на среднем оранжевом даёт по WCAG 3.2–3.4:1 (провал 4.5:1), а
по APCA Lc 64–66 (выше порога Lc 60 для не-body текста).** Это тот самый «оранжевый» кейс, о котором пишет APCA:
«studies by others showing that color insensitive types are not well served» и «the WCAG 2 math may fail a color
pair that should pass as very readable» [S7].

Практический вывод: **если сделать белую надпись на оранжевой кнопке, она будет читаемой, но не пройдёт аудит.**
Решение — тёмный текст на оранжевом (проходит оба) или более тёмный оранжевый под белый текст (Tailwind
orange-700 #a94400 → белый текст 5.98:1).

### 4.3. Bridge-PCA

Промежуточный вариант: «a method that is fully backward compatible with WCAG 2, known as Bridge-PCA, intended as a
way to provide better readability and calculate for dark mode but still follow the older WCAG 2 success criterion.
While Bridge PCA fixes some problems, what is lost is the greater design flexibility offered by the full APCA
implementation» [S19]. Доступен на myndex.com/BPCA/. Сам метод я не разбирал — НЕ ПРОВЕРЕНО.

### 4.4. Что делать агенту

```
FUNCTION validate_pair(fg, bg, role, font_px, font_weight):
    w = wcag_contrast(fg, bg)
    a = abs(apca(fg, bg))

    # 1. Жёсткий фильтр: WCAG 2 AA (юридическое требование)
    is_large = (font_px >= 24) OR (font_px >= 18.67 AND font_weight >= 700)
    wcag_min = is_text(role) ? (is_large ? 3.0 : 4.5) : 3.0
    IF role IN [disabled, decorative, logo]: wcag_min = 0
    pass_wcag = (w >= wcag_min)

    # 2. Мягкий фильтр: APCA (качество)
    apca_min = LOOKUP {body: 75, content_text: 60, large_text: 45,
                       placeholder: 30, disabled: 30, non_text: 30, divider: 15}[role]
    pass_apca = (a >= apca_min)

    # 3. Максимум для крупного и больших площадей
    IF (font_px > 36 AND font_weight >= 700) OR role == large_fill:
        IF a > 90: WARN "избыточный контраст, попробуй сделать светлый элемент темнее"

    RETURN pass_wcag AND pass_apca, {wcag: w, apca: a}
```

Если `pass_wcag` без `pass_apca` — цвет юридически годен, но читается плохо; поднимай контраст.
Если `pass_apca` без `pass_wcag` (оранжевый с белым текстом) — цвет читается, но не пройдёт аудит; меняй.

---

## 5. Нетекстовый контраст (1.4.11)

### 5.1. Мерить со всех сторон

«1.4.11 requires contrast of at least 3:1 against **adjacent color(s)**, which means you may need to measure
contrast in more than one place. A non-text element may have different contrast on one side than the other (like a
wedge in a pie chart), or it may contain different-colored components that need 3:1 contrast with each other»
[S26].

Разобранный пример: иконка-предупреждение = белый восклицательный знак в красном треугольнике на сером фоне.
Два измерения: знак↔треугольник (> 3:1, ок) и треугольник↔фон (< 3:1, **провал**). Иконка не проходит 1.4.11.

### 5.2. Что попадает под требование

Два класса [S26]:
1. **User Interface Components** — контролы с отдельной функцией. «Each state of the component must also have 3:1
   contrast.» Пример провала: кастомный чекбокс, при наведении становящийся #00B0F0 → 2.5:1 → провал.
2. **Graphical Objects** — «parts of graphics required to understand the content». Иконка-ссылка на Twitter нужна
   3:1; но если рядом написано слово «Twitter» с контрастом 4.5:1, иконка больше не нужна для понимания и
   требование снимается.

Исключения:
- неактивные компоненты;
- оформление, заданное браузером и не изменённое автором;
- «when a particular presentation of graphics is essential» — тепловые карты, фотографии, скриншоты, логотипы.

### 5.3. Фокус-ринг

- Отсутствие видимого фокуса — провал 2.4.7 Focus Visible (AA) [S26].
- Требование: «use the CSS `:focus` and `outline` properties to customize a focus indicator that always has at
  least 3:1 contrast while also matching your site design» [S26].
- Современные Chrome и Edge рисуют **двойную обводку** (тёмная линия + белая), и она работает на любом фоне;
  Firefox и IE — пунктирную чёрную, которая теряется на тёмном фоне [S26].
- Отдельно предупреждение: «pay close attention to areas like headers and footers that often have different
  background colors» — фокус-ринг должен работать и в шапке, и в сайдбаре с другим фоном.

Числа и реализация фокус-ринга — в `05-states-and-interaction.md`, §5.

---

## 6. Как считать в реальном интерфейсе

### 6.1. Альфа

Полупрозрачный цвет надо сначала скомпозитить с тем, что под ним [S27]:

```
FUNCTION composite(fg_hex, alpha, bg_hex):
    FOR each channel c:
        out[c] = fg[c] * alpha + bg[c] * (1 - alpha)
    RETURN out
```

Пример из shadcn (посчитано мной): `--border: oklch(1 0 0 / 10%)` (белый 10 %) над фоном #0a0a0a даёт реальный
цвет **#232323** и контраст 1.26:1; над карточкой #171717 — **#2e2e2e** и 1.32:1. То же `--input` при 15 % →
#2f2f2f и 1.48:1.

Это одновременно и плюс (одна альфа работает на всех поверхностях), и минус (контраст границы низкий на всех).

### 6.2. Градиенты и изображения

WCAG метода не даёт; WebAIM рекомендует «testing the area where contrast is lowest» [S26].
Практические приёмы:
- под текстом на фото — сплошная подложка или полупрозрачный слой, доведённый до нужного контраста;
- приём Dannaway: белая сплошная подложка под иконку на фотографии даёт гарантированные 3:1 независимо от
  фотографии и заодно увеличивает зону нажатия [S32];
- в forced-colors браузер сам рисует «backplates» под текстом «to preserve contrast when text is placed on top of
  images» [S34] — то есть даже стандарт признаёт подложку правильным решением.

### 6.3. Как брать цвета для проверки

Порядок предпочтения [S27]:
1. **Вычисленные значения браузера** (DevTools, автоматический инструмент) — предпочтительный метод; убедиться,
   что альфа скомпозичена;
2. **аудит CSS** — с ручным композитингом альфы;
3. **пипетка** — обязательна для текста в изображениях; «sample a pixel in the middle of a major stroke of the
   smallest size font… For small and thin fonts… sample at least three to five different letters and average».

Настройка системы для пипетки: профиль дисплея sRGB, пипетка в режиме sRGB, размер сэмпла 1 пиксель [S27].

---

## 7. Ссылки внутри текста

Единственное место, где 1.4.1 и 1.4.3 пересекаются и создают почти невыполнимое требование.

Если ссылка внутри абзаца отличается **только цветом** (подчёркивание убрано), нужны ОДНОВРЕМЕННО [S26]:
1. ссылка ≥ 4.5:1 к фону (1.4.3);
2. ≥ 3:1 между цветом ссылки и цветом обычного текста (1.4.1);
3. визуальный признак не-цветом при фокусе и, желательно, при наведении.

Разобранный пример [S26]: текст #2E2E2E (13.6:1 к белому), ссылка #0079AD (4.8:1 к белому) — но между ними лишь
2.8:1. Более светлый #0081B8 даёт чуть больше 3:1 к тексту, но уже меньше 4.5:1 к фону.
Вывод WebAIM: «With these text and background colors, it is impossible to use non-underlined links and also meet
the WCAG guidelines.»

**Рекомендация: подчёркивай ссылки внутри текста.** Без подчёркивания ссылки допустимы только там, где
интерактивность понятна из контекста: навигация, шапка, меню, кнопки-ссылки.

Дополнительно: цвет ссылки в состояниях hover/focus/active проверяется отдельно и каждый должен давать ≥ 4.5:1.

---

## 8. Цветовая слепота

### 8.1. Что известно точно

- **Около 5 % населения мира** имеет CVD [S19]; преимущественно мужчины [S32].
- Типы: **deutan** (проблема с M/зелёным конусом), **protan** (L/красный), **tritan** (S/синий, редко),
  ахроматические (крайне редко, сопровождаются низкой остротой и светобоязнью) [S19].
- **Ключевое:** «while CVD impairs the ability to distinguish some colors, luminance perception is the same as
  standard vision for the common types of CVD. Therefore for readability, deutan, protan, tritan types have the
  same needs for lightness contrast as standard vision» [S19] `[исследование]`, со ссылкой на Ilhan et al.
- **Единственное исключение:** «when pairing red and black, as those with the protan forms of CVD are insensitive
  to red. As a result, red against black has greatly diminished contrast, and red/black as a pair should be
  avoided for text or semantic non-text» [S19].
- Следствие: CVD влияет не на читаемость, а на **различение** — «visual tasks such as reading a map or charts
  (dataviz), due to the need to discriminate colors» [S7].

### 8.2. Какие пары проблемны

| Пара | Кому | Что делать |
|---|---|---|
| красный ↔ зелёный | deutan, protan (самые частые) | не использовать как единственное различие; менять светлоту |
| зелёный ↔ коричневый, зелёный ↔ оранжевый | deutan, protan | делать зелёный желтоватым или синеватым [S23] |
| синий ↔ фиолетовый | tritan и частично protan | разносить по светлоте |
| красный на чёрном | protan | запрещено для текста и смысловой графики [S19] |
| **синий ↔ оранжевый/красный** | — | **безопасная пара**: «colorblind people can easily distinguish blue and orange/red» [S23] |

Мой численный расчёт (симуляция Viénot–Brettel–Mollon, ΔE в OKLab) для 8 равноотстоящих оттенков при одинаковой
светлоте L = 0.62: минимальное ΔE в норме 0.099, при protan 0.043, **при deutan 0.004, при tritan 0.008**.
С чередующейся светлотой (0.45–0.74) худшая пара поднимается до 0.046–0.083. Подробности — в
`02-semantic-roles-and-architecture.md`, §5.2.

### 8.3. Инструменты

| Инструмент | Что делает |
|---|---|
| `culori.filterDeficiencyProt / Deuter / Trit` | симуляция трёх типов, JS, оффлайн [S33] |
| `culori.filterGrayscale` | перевод в ч/б для проверки «get it right in black & white» [S33] |
| `culori.differenceCiede2000()`, `differenceEuclidean('oklab')` | измерение различимости [S33] |
| myndex.com/CVD/ | симулятор по модели Brettel et al., «includes an sRGB grayscale example, useful for visually assessing luminance contrast» [S7][S27] |
| Adobe Leonardo | «Automatically cycle through your colors to create a colorblind safe palette», фильтр «только цвета с контрастом ≥ 3:1», измерение цветовой разницы для каждого типа CVD [S17] |
| Chrome DevTools | эмуляция зрительных нарушений [S32] |

### 8.4. Правило «не только цветом»

WCAG 1.4.1 (уровень A): «Color is not used as the only visual means of conveying information, indicating an
action, prompting a response, or distinguishing a visual element» [S26].

Разобранные примеры провала и исправления [S26]:
- таблица заданий, где «missing» и «late» различаются только цветом фона → добавить колонку «Статус»;
- пустое поле формы с красной рамкой → добавить иконку в поле И текст ошибки под полем;
- ссылка без подчёркивания → вернуть подчёркивание.

Dannaway добавляет про кнопки: «Avoid solely relying on color to establish a button hierarchy. Consider using
shape and style… filled button, unfilled button, and an "empty" button for the primary, secondary, and tertiary»
[S32].

---

## 9. Слишком большой контраст

Отдельный, редко упоминаемый риск.

- APCA задаёт **максимум Lc 90 для шрифтов больше 24–36 px и для больших площадей цвета**: «More is not always
  better» [S19][S27].
- «While it is possible to have too much contrast, particularly for large and bold elements, this does not suggest
  making dark text lighter. **Excess contrast is nearly always due to excess brightness. When something is so
  contrasty that it seems to have "halos", the first thing to try is to make the lightest element a little
  darker.**» [S19]
- «For the darkest color… you probably won't see any difference for colors darker than about #222. In fact, #222
  and darker is not functionally different than #000, except that for small thin fonts, #000 is helpful to "cut
  through" antialiasing. On the other hand, **the difference between #fff, and #eee or #ddd can be significant in
  terms of reducing visual fatigue due to brightness.**» [S19]

Практические следствия:
1. Фон светлой темы лучше делать не чистым белым: Polaris #f1f1f1, Radix slate1 #fcfcfd, Material neutral98,
   MDN в примере `light-dark(#efedea, #223a2c)`. Чистый белый используют Primer и shadcn.
2. Основной текст темнее #222 смысла не имеет, кроме мелкого текста, где #000 помогает против антиалиасинга.
3. Крупный заголовок белым по чёрному даёт Lc −107.9 — это выше рекомендуемого максимума Lc 90; приглушай либо
   текст (до #e5e5e5, Lc −91), либо фон.

Про галацию (halation) белого текста на чёрном подробнее — `04-dark-theme.md`, §5.

---

## Частые ошибки

1. **Округление контраста.** 4.47:1 не равно 4.5:1 [S26].
2. **Проверка только основного текста.** Вторичный, плейсхолдеры, иконки, границы и все состояния проверяются
   отдельно.
3. **Проверка только состояния покоя.** «Each state of the component must also have 3:1 contrast» [S26].
4. **Измерение контраста цветного текста к белому, когда он на цветной плашке.** Бейдж «Просрочено» тёмно-красным
   на красной плашке — мерить надо к плашке.
5. **Игнорирование альфы.** Граница `rgba(0,0,0,.1)` — это не «чёрный», а конкретный светло-серый.
6. **Контраст меряется только к фону, а не к соседям.** 1.4.11 требует «adjacent colors», то есть иконка внутри
   плашки и плашка на фоне — два измерения.
7. **Белый текст на оранжевом или жёлтом.** Проходит APCA, проваливает WCAG; аудит зафиксирует нарушение.
8. **Ссылка без подчёркивания в тексте.** Почти всегда нарушает либо 4.5:1 к фону, либо 3:1 к тексту.
9. **Тёмная тема по WCAG.** Даёт формально проходящие, но нечитаемые серые. Проверяй APCA.
10. **Фокус-ринг цвета акцента на фоне того же акцента.** На синей шапке синий ринг невидим. Нужны либо двойной
    ринг, либо `outline-offset` с контрастной подложкой.
11. **Отключённая кнопка без контраста вообще.** WCAG освобождает, но APCA требует Lc 30: пользователь должен
    видеть, что кнопка существует.
12. **Избыточный контраст крупного текста.** Белый #fff по чёрному #000 на 48 px — Lc −107.9 при максимуме −90.

### Ошибки, типичные для нейросетей

13. **Серый вторичный текст «на глаз».** `text-gray-400` (2.60:1) вместо `text-gray-500` (4.84:1). Разница
    незаметна в описании, но одно проходит, другое нет.
14. **Копирование светлой темы в тёмную с теми же контрастами.** #737373 на белом — 4.95:1 (проходит); #737373 на
    #0a0a0a — 4.18:1 (провал) при Lc всего −28.6.
15. **Генерация «disabled» как `opacity: 0.5` от уже низкоконтрастного вторичного текста.** Итог: 2.4:1 от 4.8:1,
    ниже Lc 30.
16. **Проверка контраста по значению токена, а не по фактическому цвету после композитинга.** Все полупрозрачные
    границы и оверлеи считаются неверно.
17. **Использование `text-white` на любой цветной кнопке без проверки.** Работает для синего, фиолетового,
    тёмно-зелёного; ломается на жёлтом, светло-оранжевом, лайме, голубом.
18. **Фокус-ринг взят из `ring` shadcn (2.58:1) и оставлен как есть.** Провал 1.4.11.

---

## Чек-лист

- [ ] Основной текст ≥ 4.5:1 (лучше ≥ 7:1) и APCA Lc ≥ 75?
- [ ] Вторичный текст ≥ 4.5:1 и Lc ≥ 60? В тёмной теме проверен отдельно по APCA?
- [ ] Плейсхолдер как вторичный текст (4.7–6:1), а не как disabled?
- [ ] Отключённые элементы в коридоре Lc 30–45 (примерно 2–3.5:1)?
- [ ] Граница поля ввода, чекбокса, переключателя ≥ 3:1 к своему фону? (для белого фона это #949494 и темнее)
- [ ] Значимые иконки ≥ 3:1 к фону, а составные иконки — и внутри себя тоже?
- [ ] Фокус-ринг ≥ 3:1 и к фону, и к самому элементу? Проверен в шапке, сайдбаре и на цветных подложках?
- [ ] Каждое состояние (hover, active, selected, invalid) проверено отдельно?
- [ ] Все полупрозрачные цвета скомпозичены перед проверкой?
- [ ] Текст на градиенте или фото проверен в самом слабом месте либо имеет подложку?
- [ ] Ссылки внутри текста подчёркнуты (или выполняют все три условия одновременно)?
- [ ] Нет пары «красный на чёрном» и «чёрный на красном» для текста и смысловой графики?
- [ ] Ни один статус не различается только цветом?
- [ ] Палитра прогнана через симуляцию protan, deutan, tritan и через grayscale?
- [ ] Крупный текст (> 36 px bold) и большие цветные площади не превышают Lc 90?
- [ ] Фон светлой темы не чистый #ffffff, если это не осознанное решение?
- [ ] Проверка выполнена на обычном sRGB-мониторе, а не только на P3-Retina?

---

## Открытые вопросы и противоречия

1. **Порог APCA для «обычного текста»: Lc 60 или Lc 75.** Myndex требует Lc 75 для body и Lc 60 для прочего
   читаемого [S7][S27]; Accessible Palette трактует Lc 60 как эквивалент 4.5:1 [S22]. Мой расчёт: WCAG 4.5:1 на
   белом = Lc 71.6, то есть ближе к 75. `[спорно]`
2. **Плейсхолдер.** WCAG считает его текстом (4.5:1), APCA — spot-текстом (Lc 30). Системы делают по-разному.
   `[спорно]`
3. **Отключённое состояние.** WCAG освобождает полностью, APCA требует Lc 30, Polaris даёт 1.82:1, Primer 3.45:1.
   Разброс почти вдвое. `[спорно]`
4. **Статус WCAG 3 на 2026 год.** Я не нашёл подтверждения, что WCAG 3 принят или что APCA закреплён в нём
   окончательно. Страницы w3.org отдают 403 при обращении из этой среды; проверял только по документам Myndex и
   readtech.org, которые сами помечены как бета. **НЕ ПРОВЕРЕНО в первоисточнике W3C.**
5. **Bridge-PCA** упомянут в [S19], но сам метод и его формулы я не читал. НЕ ПРОВЕРЕНО.
6. **Данные по CVD (5 % населения)** приведены Somers без ссылки на конкретное эпидемиологическое исследование;
   цифра общепринята, но первоисточник я не проверял.
7. **Порог ΔE ≥ 0.05 в OKLab** для различимости категориальных цветов — мой рабочий ориентир из расчётов, не
   отраслевой стандарт.
8. **Значения APCA у меня посчитаны по версии 0.1.9.** Если Myndex выпустит новые коэффициенты, числа сдвинутся.
   Контрольные точки для сверки: #000 на #fff = 106.0; #fff на #000 = −107.9; #888 на #fff = 63.1.

---

## Источники

- [S3] Radix Colors, исходники. https://github.com/radix-ui/colors
- [S7] A. Somers (Myndex). The Easy Intro to the APCA Contrast Method + APCA in a Nutshell. https://git.apcacontrast.com/documentation/APCAeasyIntro.html , https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html — уровни Lc, критика WCAG 2, определения; первоисточник метода.
- [S8] GitHub Primer, исходники токенов. https://github.com/primer/primitives
- [S13] GOV.UK Design System. Colour. https://design-system.service.gov.uk/styles/colour/ — подтверждение, что WCAG 2.2 не изменил 1.4.3.
- [S15] shadcn/ui. Theming. https://ui.shadcn.com/docs/theming
- [S17] Adobe Leonardo. https://opensource.adobe.com/leonardo/ — проверка CVD и контраста с альфой.
- [S19] A. Somers. The Realities And Myths Of Contrast And Color. Smashing Magazine, сентябрь 2022. https://www.smashingmagazine.com/2022/09/realities-myths-contrast-color/ — spatial frequency, CVD и яркостный контраст, максимум контраста, #222/#fff; авторский текст создателя APCA, редактура Smashing.
- [S22] E. Fedorenko. Accessible Palette. https://wildbit.com/blog/accessible-palette-stop-using-hsl-for-color-systems — трактовка Lc 60 как эквивалента 4.5:1.
- [S23] Datawrapper. How to pick more beautiful colors. https://blog.datawrapper.de/beautifulcolors/ — безопасная пара синий/оранжевый, правила для зелёного.
- [S24] Shopify Polaris, исходники. https://github.com/Shopify/polaris
- [S26] WebAIM. Contrast and Color Accessibility. https://webaim.org/articles/contrast/ — полный разбор 1.4.3, 1.4.6, 1.4.11, 1.4.1 с примерами и исключениями; профильная организация.
- [S27] APCA Readability Criterion. Bronze Simple Mode. https://readtech.org/ARC/tests/bronze-simple-mode/?tn=criterion — уровни соответствия, категории текста, процедура измерения, эмпирическая база; бета-документ.
- [S32] A. Dannaway. 16 little UI design tips. https://www.adhamdannaway.com/blog/ui-design/ui-design-tips — 3:1 для элементов, 4.5:1 для текста, подложка под иконку.
- [S33] culori. https://culorijs.org/api/ — `wcagContrast`, `filterDeficiency*`, `differenceCiede2000`.
- [S34] MDN. `forced-colors`. https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors — backplates под текстом.
