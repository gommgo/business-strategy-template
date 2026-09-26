# Архитектура токенов и именование

Волна 2, агент F, 22 сентября 2026. Источников прочитано целиком: 38.

Как устроены уровни токенов в одиннадцати системах (по исходникам, не по документации), из чего состоит
имя токена, в каком порядке идут части, сколько токенов нужно продукту и когда значение переезжает из
компонента в общий набор. Значения шкал не дублируются: они собраны в `10-design-systems-atlas/`
и в папках волны 1.

## Выжимка для агента

1. **Два уровня обязательны, третий — опция.** Примитивы (`color.blue.600`, `size.16`) → семантика
   (`color.bg.canvas`, `space.inset.card`). Компонентные токены заводят позже и не всегда. → §1
   `[консенсус]`
2. **Правило перехода численное: токен становится общим, когда его используют три и более компонента**
   (Nathan Curtis). До этого значение живёт в коде компонента. → §1.4 `[мнение]`
3. **Brad Frost, автор трёхуровневой модели, сам пишет, что три уровня «may be overkill»** и что его
   команда начинает с более худой структуры, а уровни добавляет, «когда осядет пыль». → §1.3 `[мнение]`
4. **Имя строится из четырёх групп частей:** namespace (`esds`, `md`) → object (`button`, `forms`) →
   base (category `color` + concept `action` + property `background`) → modifier (variant `primary`,
   state `hover`, scale `500`, mode `on-dark`). → §2.1 `[мнение]`
5. **Ни один токен не содержит все части.** Попытка обеспечить «полноту» даёт
   `shape-tile-corner-radius-default-on-light` вместо `shape-tile-corner-radius`. → §2.7 `[мнение]`
6. **Порядок частей не унифицирован, но три закономерности устойчивы:** namespace впереди, base в
   середине, modifier в конце; `mode` — последний среди модификаторов. → §2.6 `[консенсус]`
7. **Именуй по назначению, не по значению.** `color.blue.primary` — антипаттерн: при смене акцента имя
   врёт. Исключение — примитивы: там значение в имени и есть смысл имени. → §2.2 `[консенсус]`
8. **Сокращения в семантике не используют.** DTCG рекомендует `background`, а не `bg`; Primer пишет
   `bgColor`, Polaris `bg-fill`, Carbon `background`. Из одиннадцати систем сокращение в именах токенов
   есть только у Primer, и то как часть составного слова. → §2.3 `[стандарт]`
9. **Числовой шаг у цветовых шкал — 100, а не 1, 2, 3.** Так остаётся место вставить цвет между
   существующими. DTCG прямо это рекомендует; у нейтралей допускается шаг 25 в светлой части. → §2.4
   `[стандарт]`
10. **Пять видов шкал:** enumerated (1, 2, 3 — уровни заголовков), ordered (50…900 — Material),
    bounded (`slate-42` — светлота), proportion (`2-x`, `half-x`), t-shirt (s, m, l). Curtis прямо
    поправил себя: **для отступов лучше proportion, чем t-shirt**. → §2.5 `[мнение]`
11. **Тема ≠ режим.** Бренд (Marriott Courtyard) ортогонален светлой/тёмной теме; каждой теме нужны оба
    режима. Смешение этих осей — главная причина комбинаторного взрыва. → §2.8 `[консенсус]`
12. **Одно решение может принадлежать двум наборам** («error red» — это и `color.feedback.error`, и
    `ui-controls.color.text.error`). Правильный ход — сохранить оба имени и связать алиасом, а не
    выбирать одно. → §2.9 `[мнение]`
13. **Уровней алиасов достаточно двух-трёх.** Цепочка `primitive → semantic → component` — предел; в
    четвёртом звене никто уже не понимает, откуда взялось значение. → §1.3 `[консенсус]`
14. **Маршрутизация по группам, а не по префиксам имён.** Carbon: «The group name is the authoritative
    category… no name-prefix inference, no hidden ordering rules». Имя токена — производная от пути в
    дереве, а не самостоятельная строка. → §2.10 `[система]`
15. **Имя токена в макете и в коде должно совпадать** (правило Авито). Иначе дизайнер и разработчик
    обсуждают разные объекты. → §4.3 `[мнение]`
16. **Плоское имя нельзя грепать.** `border-subtle-02` в JSON — это путь `border` → `subtle` → `02`;
    Carbon предупреждает об этом отдельным разделом «Tip for agents». → §2.10 `[система]`
17. **Порядок величин: 596 токенов у Atlassian на платформу, 250+ на тему у Carbon, ~2000 на режим у
    Plasma, 37 переменных у shadcn.** Одному продукту нужно **150–300 семантических**. → §3
    `[система]`
18. **Число компонентных токенов растёт быстрее пользы.** Закон убывающей отдачи Nathan Curtis: чем
    больше компонентов, тем выше стоимость каждого и ниже ценность. → §3.3 `[мнение]`
19. **Четыре живые модели уровней:** ref/sys/comp (Material), base/functional/component (Primer),
    global/alias (Fluent), seed/map/alias (Ant). Пятая — «фасеты имени» (Spectrum), где имя не строка,
    а объект. → §1.2 `[система]`
20. **Ant Design вычисляет средний уровень формулами, а не задаёт вручную:** 12 seed-значений
    разворачиваются в сотни map-токенов. Это единственная из одиннадцати систем, где средний уровень
    порождается кодом. → §1.2 `[система]`
21. **Spectrum хранит ссылки по uuid, а не по имени** — переименование токена не ломает ссылки. Цена:
    файл нечитаем без инструмента. → §2.11 `[система]`
22. **Контекстные токены Carbon** (`$layer` без номера) — отдельный механизм: значение подставляет
    компонент-обёртка по глубине вложенности. В JSON-токенах их нет, только в Sass. → §1.5 `[система]`

---

## 1. Уровни

### 1.1. Канонические уровни

| Уровень | Что это | Имя говорит о | Кто меняет |
|---|---|---|---|
| Примитив (reference, global, base, seed) | точка шкалы без смысла | значении | редко, при ребрендинге |
| Семантический (system, alias, functional) | роль в интерфейсе | назначении | при смене характера продукта |
| Компонентный (component, comp) | значение одного компонента | компоненте | при правке компонента |
| Контекстный | значение зависит от места на странице | контексте | никогда, вычисляется в рантайме |

Первые два есть у всех одиннадцати разобранных систем. Третий — у Material, Carbon, Polaris, Fluent,
Spectrum. Четвёртый — только у Carbon.

### 1.2. Как это названо в живых системах

| Система | Уровни | Как выглядит | Проверено по |
|---|---|---|---|
| **Material 3** | `md-ref-*` → `md-sys-*` → `md-comp-*` | `md-ref-palette-primary40` → `md-sys-color-primary` → `md-comp-filled-button-container-color` | исходники `material-web`, `tokens/versions/v0_192`, ~90 файлов `md-comp-*` |
| **GitHub Primer** | `base` → `functional` → компонентные в коде | `base.color.neutral.13` → `fgColor.default` | `primer/primitives`, `src/tokens/base/**` и `functional/**` |
| **IBM Carbon** | `colors` → `themes` (+ `components/*.json`) + контекстные | `gray.50` → `background.hover` → `button.primary.hover` | `packages/{colors,themes,layout}/src/dtcg/*` |
| **Microsoft Fluent 2** | `global/` → `alias/` | `global/colorPalette` → `alias/lightColor`, `alias/darkColor`, `alias/highContrastColor` | `microsoft/fluentui`, `packages/tokens/src` |
| **Ant Design 5** | `seed` → `map` (**вычисляется**) → `alias` | `colorPrimary #1677ff`, `fontSize 14` → `fontSizeLG`, `borderRadiusLG` → `colorTextHeading` | `components/theme/themes/seed.ts`, `shared/gen*.ts` |
| **Shopify Polaris** | `size`-ряд → `space`/`border-radius`/… → алиасы-назначения | `size-400` → `space-400` → `space-card-padding` | `polaris-tokens/src` |
| **Atlassian** | группы (`color`, `space`, `font`, `elevation`, `radius`, `border`, `opacity`, `motion`, `utility`) → темы файлами | `color.background.accent.blue.subtle` | `@atlaskit/tokens@18.2.1` |
| **Adobe Spectrum 2** | «фасеты имени» + `alias`-токены со ссылкой по uuid | `{property: gap, size: xxl, structure: accessory}` | `adobe/spectrum-design-data` |
| **shadcn/ui** | только семантика (37 переменных) | `--primary`, `--primary-foreground`, `--muted` | `ui.shadcn.com/docs/theming` |
| **Radix Themes** | шкалы 1–12 → семь ручек `<Theme>` | `--accent-9`, `--gray-a3`, `--space-4` | `packages/radix-ui-themes/src/styles/tokens/*` |
| **Tailwind v4** | пространства имён в `@theme` | `--color-blue-600`, `--spacing`, `--radius-md` | `packages/tailwindcss/theme.css` |

Два наблюдения, которые важнее списка.

**Ant Design — единственная система, где средний уровень порождается кодом.** Дизайнер задаёт 12
seed-значений (`colorPrimary`, `fontSize: 14`, `borderRadius: 6`, `controlHeight: 32`, `sizeUnit: 4`,
`sizeStep: 4`, `lineWidth: 1`, `motionUnit: 0.1`, `zIndexBase: 0`, `zIndexPopupBase: 1000`, `wireframe`,
`focusOutline`), а сотни map-токенов выводятся формулами:

```
fontSize_i   = base × e^((i−1)/5), округление до чётного   →  при base 14: 12 14 16 20 24 30 38 46 56 68
lineHeight   = (fontSize + 8) / fontSize                   →  1.667 1.571 1.5 1.4 1.333 …
sizeXXL      = sizeUnit × (sizeStep + 8) = 48;  XL 32, LG 24, MD 20, MS 16, SM 12, XS 8, XXS 4
controlHeightSM = ×0.75 = 24;  XS = ×0.5 = 16;  LG = ×1.25 = 40
motionDurationFast = motionBase + motionUnit = 0.1s;  Mid 0.2s;  Slow 0.3s
lineWidthBold = lineWidth + 1 = 2
```

Радиусы при этом выводятся **не умножением, а кусочно-линейной функцией** `genRadius(borderRadius)`: при
базе 6 получается XS 2, SM 4, base 6, LG 8, Outer 4. Правила: `LG = base + 1` при base ∈ [5, 6),
`base + 2` при [6, 16), 16 при ≥ 16; `SM = 4` при [5, 7), 5 при [7, 8), 6 при [8, 14), 7 при [14, 16),
8 при ≥ 16. То есть Ant сознательно сжимает шкалу радиусов в мелкой части, чтобы маленькие элементы не
выглядели переокруглёнными. shadcn и Radix, наоборот, множат линейно (`--radius-sm:
calc(var(--radius) * 0.6)`, `--radius-1 = calc(3px × scaling × radius-factor)`).

Плюс формульного среднего уровня: тема задаётся двенадцатью числами. Минус: значения нельзя подправить
точечно, не сломав формулу, и их нельзя прочитать глазами — надо выполнить код.

**Spectrum разорвал связь между именем и ссылкой.** Файл токенов — не дерево, а массив; имя — объект
фасетов; ссылки идут по `uuid`:

```json
{ "name": {"property": "gap", "size": "xxl", "structure": "accessory", "legacyKey": "accessory-gap-2x-large"},
  "$schema": "https://opensource.adobe.com/spectrum-design-data/schemas/token-types/dimension.json",
  "value": "9px", "uuid": "60f6e8c5-…", "conceptId": "495812f8-…" }
```

Частота фасетов по 597 токенам `layout` + `typography`: `property` 597 (обязателен), `scale` 370
(desktop/mobile), `legacyKey` 320, `size` 211, `from` 133 и `to` 133 («расстояние от чего до чего»),
`scaleIndex` 127, `structure` 111, `anatomy` 41, `icon` 34, `variant` 33, `density` 28, `weight` 22,
`state` 14, `orientation` 11, `shape` 9, `role` 9, `emphasis` 7, `position` 6, `component` 5, `script` 4,
`alignment` 3, `qualifier` 2, `style` 2, `family` 2.

Это ровно грамматика Nathan Curtis, только машиночитаемая: вместо строки с дефисами — объект с полями.
Плюс: переименование не ломает ссылки, можно запрашивать «все токены с `property: gap` и
`density: compact`». Минус: файл нечитаем без инструмента, `grep` бесполезен.

### 1.3. Сколько уровней алиасов

| Источник | Позиция |
|---|---|
| Brad Frost | три уровня — цель, не старт: «may be overkill… we've started the project with a leaner variable structure, then introduced additional tiers once the dust has settled» |
| DTCG Color Module §7 | три категории: Base / Alias / Component |
| Nathan Curtis | уровней столько, сколько нужно; прямо предупреждает против преждевременной глобализации |
| Carbon | два в DTCG-файлах (`colors` → `themes`) плюс компонентные в отдельных файлах |
| shadcn | один (только семантика), примитивы приходят из Tailwind |

Практический предел цепочки — **три звена**: `primitive.color.accent.600` → `color.accent.solid` →
`button.primary.background`. Четвёртое звено делает невозможным ответ на вопрос «почему кнопка синяя»
без разворачивания всей цепи.

Пример полной цепочки у Frost:

```
Tier 1  --color-brand-starbucks-green: #00704a;
Tier 2  --primary-action-background-color: var(--color-brand-starbucks-green);
Tier 3  --button-background-color: var(--primary-action-background-color);
```

Пример того же у Curtis, с полиерархией:

```
$ui-controls-color-text-error  =  $color-feedback-error  =  $color-red-36  =  #B90000
```

### 1.4. Когда значение переезжает в общий набор

Правило Curtis: **три и более компонента**. Процедура промоушена описана по шагам:

1. добавить `$esds-forms-color-border` в глобальные токены;
2. заменить им `$esds-input-color-border` в Input;
3. удалить локальный токен;
4. применить новый токен в Select, Checkbox, Radio.

Два принципа, которые за этим стоят: **«Start Within, Then Promote Across Components»** и **«Don't
Globalize Decisions Prematurely»**.

Uber делает то же самое механизмом «псевдотокенов»: переменные уровня компонента, которые указывают на
токены системы и **скрыты от публикации** — их видно только внутри файла компонента `[V16 B]`.

### 1.5. Контекстные токены Carbon

Carbon разводит два способа работы со слоями:

- **layering tokens** — явные, с номером: `$layer-01`, `$layer-02`, `$layer-03`, `$field-02`,
  `$border-strong-03`. Для каждого уровня компонент собирается заново.
- **contextual tokens** — те же имена без номера (`$layer`, `$layer-accent`, `$field`, `$border-subtle`);
  значение подставляет компонент-обёртка `<Layer>` по глубине вложенности, до трёх уровней. Один
  компонент работает на всех слоях.

Правило парности: поле — это слой поверх фона, поэтому поле на `$layer-02` использует `$field-03`;
границы парятся по номеру (`$field-03` с `$border-strong-03`).

**В DTCG-файлах Carbon контекстных токенов нет** — только явные номера; контекст живёт в
`packages/styles/scss/layer/_layer-sets.scss`. То есть механизм не выражается в стандарте токенов и
требует кода. Для генеративного конвейера это плохая новость: контекстный слой придётся либо
реализовывать самому, либо отказаться от него в пользу явных номеров.

---

## 2. Грамматика имени

### 2.1. Четыре группы частей (Nathan Curtis)

| Группа | Части | Примеры |
|---|---|---|
| **Base** — костяк | category, concept, property | `color`, `action`, `background` |
| **Modifier** — уточнение | variant, state, scale, mode | `primary`, `hover`, `500`, `on-dark` |
| **Object** — к чему относится | component, element, component group | `button`, `left-icon`, `forms` |
| **Namespace** — чьё | system, theme, domain | `esds`, `ocean`, `retail` |

Разбор частей с правилами.

**Category.** Принцип: избегай омонимов. `type` — омоним (типографика или «тип чего-то»), `text` — и
контент, и property. Поэтому системы выбирают `font`: Atlassian `font.body`, Polaris `font-size`,
Fluent `fontSizeBase300`.

**Property.** Пара category + property (`color-background`) «крайне обща и целенаправленно бесполезна»:
без concept и модификаторов она ничего не сообщает.

**Concept.** Смысловая группа: `feedback` (aka notification / messaging / alert) с вариантами
success / warning / error; `visualization` (dataviz, charting); `commerce` (sale, clearance, inventory).
Принцип отбора: **однородность внутри класса и разнородность между классами**. Не класть `sale` в
`visualization` — смысл разный.

**Variant.** Развилка, которую надо пройти осознанно:

| Подход | Пример | Плюс | Минус |
|---|---|---|---|
| Парсимония | `$color-success` | мало токенов, гибко | пользователь сам решает, куда применить: к фону, тексту или границе |
| Точность | `$color-background-success`, `$color-text-success` | применение однозначно | токенов втрое больше |

Формулировка Curtis: «гибкость ценой специфичности и, следовательно, точности применения». Практика
2026 года на стороне точности: Primer, Polaris, Carbon и Atlassian все разводят фон, текст и границу.

**State.** hover, press/active, focus, disabled, error. Полное имя может выглядеть как
`$color-action-text-secondary-focus`.

**Scale.** Пять видов, см. §2.5.

**Mode.** `on-light` / `on-dark` / `on-brand`. Принцип «явный против усечённого умолчания»: либо светлый
режим считается дефолтом и добавляется только `on-dark`, либо параллельная конструкция требуется во всех
именах. Позиция автора: «моё мнение о том, какая конвенция, слабое; мнение о том, что конвенция должна
быть, сильное».

**Object.** См. §1.4.

**Namespace.** Имя системы ≤ 5 символов или акроним: `slds-` (Salesforce), `mds-`, `md-` (Material),
`g-` (Gravity UI), `esds-` в примерах Curtis. Нужен, когда в одной странице живут две системы.
Обратная сторона: `--g-spacing-base` на два символа длиннее `--spacing-base` во всех вхождениях.

### 2.2. Именование по назначению, не по значению

Антипаттерны и их цена:

| Антипаттерн | Почему плохо | Правильно |
|---|---|---|
| `color.blue.primary` | при смене акцента на фиолетовый имя врёт | `color.accent.solid` |
| `--text-grey-600` | то же плюс привязка к ступени | `--fg-secondary` |
| `space-16` как семантический токен | в режиме compact станет 12 | `space.md` |
| `radius-6` | при смене характера станет 10 | `radius.md` |
| `shadow-blue` | тень не про цвет | `elevation.raised` |
| `font-size-large-but-not-huge` | описание вместо роли | `type.section` |

Исключение — примитивы: там значение в имени и есть смысл. `size.16` = 16px, `neutral.600` = ступень
600. Polaris доводит это до конца: имена — сотые доли от 4px (`size-100` = 4px, `size-400` = 16px,
`size-3200` = 128px).

Правило-детектор: **если после смены одной ручки характера имя токена становится неправдой — имя
семантическое и описывает значение.** Примитивы при смене ручек не переименовываются, потому что их
значения меняются вместе с именами (вся рампа заменяется целиком).

### 2.3. Сокращения

DTCG Color Module §7 прямо рекомендует: **`background`, а не `bg`**. Что в системах:

| Система | Пишет | Сокращает |
|---|---|---|
| Carbon | `background`, `border`, `field`, `layer`, `icon`, `text` | нет |
| Polaris | `bg-fill`, `text`, `border`, `icon` | частично (`bg`) |
| Primer | `bgColor`, `fgColor`, `borderColor` | `bg`, `fg` внутри составного слова |
| Material | `surface`, `on-surface`, `outline` | нет |
| Atlassian | `color.background`, `color.text`, `color.border` | нет |
| shadcn | `background`, `foreground`, `muted`, `accent` | нет |
| Fluent | `colorNeutralForeground1`, `colorNeutralBackground1` | нет |

Вывод: сокращают только Primer и Polaris, и только в одном месте — в паре «фон/передний план». Для
CSS-переменных сокращение оправдано длиной (`--bg-canvas` вместо `--background-canvas` × 200
вхождений), но в JSON-путях токенов лучше писать полностью. В эталонной схеме
(`04-reference-token-schema.md` §6.3) так и сделано: путь `color.bg.canvas` — компромисс, а отображение
в CSS механическое.

### 2.4. Числовой шаг цветовых шкал

DTCG: **не использовать последовательные 1, 2, 3, 4, а шаг 100** — чтобы можно было вставить цвет между
существующими; у нейтралей шаг может быть 25 в светлой части и 100 дальше.

Что в системах:

| Система | Шаг | Шагов |
|---|---|---|
| Tailwind, Primer (base), shadcn | 50, 100, 200 … 950 | 11 |
| Material | 0, 10, 20 … 100 (тон HCT) | 13 |
| Radix, Polaris | 1, 2, 3 … 12 (Radix), 1…16 (Polaris) | 12 / 16 |
| Carbon | 10, 20 … 100 | 10 |
| Fluent | оттенки по имени (`brand.shade10`, `tint20`) | — |

Radix и Polaris используют последовательную нумерацию и прямо назначают смысл каждой ступени
(Radix: шаг 6 — границы неинтерактивных элементов, 7 — границы интерактивных, 8 — усиленные границы и
кольца фокуса, 9 — сплошная заливка, 11 — текст на фоне 1–2, 12 — основной текст). Это второй способ
решить ту же задачу: вместо запаса на вставку — фиксированная семантика ступени. Он работает, пока
шкала ровно 12 шагов и не меняется.

### 2.5. Пять видов шкал

| Вид | Как выглядит | Где уместен | Пример |
|---|---|---|---|
| enumerated | 1, 2, 3 | конечное перечисление уровней | `heading-1`, `layer-01` |
| ordered | 50, 100, … 900 | цветовые рампы, веса | `neutral.600`, `fontWeight.500` |
| bounded | значение внутри имени | светлота, процент | `slate-42`, `slate-90` |
| proportion | `1-x`, `2-x`, `half-x` | **отступы** | `space-2x` = 8px при базе 4 |
| t-shirt | xs, s, m, l, xl | размеры компонентов | `control.md`, `radius.lg` |

**Прямая поправка Curtis к самому себе:** «Size ≠ space, so consider using proportion instead of
t-shirts for space despite what I said four years ago». Аргумент: `space-2x` сообщает соотношение
(вдвое больше базы), `space-md` — нет; при добавлении шага между `sm` и `md` t-shirt-шкала ломается,
пропорциональная — нет.

Практика 2026 года против: t-shirt у Fluent (`spacingHorizontalM`), Chakra, Mantine, Consta, Gravity UI;
числовой у Polaris (`space-400`), Carbon (`spacing-05`), Atlassian (`space.200`), Radix (`--space-4`);
пропорциональный — ни у кого в чистом виде. Причина, вероятно, в том, что `space-2x` требует помнить
базу, а `space-md` не требует.

Компромисс эталонной схемы: t-shirt на шкале (`space.md`) плюс **явные назначения**
(`space.inset.card`, `space.inset.table-cell-x`). Назначения снимают главную претензию Curtis: решение
«padding карточки 16» зафиксировано именем, а не выбирается заново каждым разработчиком. Ровно так же
делает Polaris: `space-card-padding` = `space-400`, `space-table-cell-padding` = `space-150`,
`space-button-group-gap` = `space-200`, `space-card-gap` = `space-400`.

### 2.6. Порядок частей

Единого порядка нет. Устойчивые закономерности (Curtis):

- **namespace впереди**;
- **base в середине**;
- **modifier в конце**;
- **object подчинён namespace и предшествует base**;
- внутри модификаторов **`mode` обычно последний**.

Внутри base порядок зависит от того, что важнее:

| Приоритет | Порядок | Пример | Кто так |
|---|---|---|---|
| иерархическая строгость | category → concept → property | `color-interactive-background` | Material, Atlassian |
| читаемость | concept → property → category | `interactive-background-color` | редко |
| парность category + property | category → property → concept | `color-background-interactive` | Carbon, Atlassian (`color.background.accent.blue.subtle`) |

Реальные схемы из пяти систем (сведено в `01-color/02-semantic-roles-and-architecture.md` §1.3):

| Схема | Пример | Системы |
|---|---|---|
| `<свойство>-<роль>-<модификатор>-<состояние>` | `bg-fill-critical-hover`, `text-success-on-bg-fill` | Polaris |
| `<свойство>Color.<роль>.<сила>` | `fgColor.muted`, `bgColor.danger.emphasis` | Primer |
| `--md-sys-color-<роль>` / `-on-<роль>` | `--md-sys-color-primary-container` | Material |
| `<роль>` + `<роль>-foreground` | `--primary`, `--primary-foreground` | shadcn, Tailwind-экосистема |
| `$<роль>-<номер слоя>` | `$layer-02`, `$border-strong-03` | Carbon |

### 2.7. Полнота: не все части у всех токенов

Антипример из статьи Curtis:

```
Хорошо:               $esds-shape-tile-corner-radius
Плохо (избыточно):    $esds-shape-tile-corner-radius-default-on-light
                      $esds-shape-tile-corner-radius-default-on-dark
```

Радиус не зависит от режима, поэтому `on-light` / `on-dark` в его имени — шум. Некоторые части (domain,
theme, element) нужны редко; scale и variant, как правило, взаимоисключающи.

Проверка: **если часть имени одинакова у всех токенов набора, её надо удалить.** Если `-default` стоит
у 100 % токенов — это не модификатор, а слово-паразит.

### 2.8. Тема ≠ режим

Принцип Curtis: тема (бренд Marriott Courtyard) ортогональна режиму (light / dark); **теме тоже нужны
оба режима**. Смешение осей даёт комбинаторный взрыв: 5 брендов × 2 режима × 2 плотности = 20 наборов,
если хранить их как независимые темы, и 5 + 2 + 2 = 9 наборов, если хранить как три ортогональные оси.

Resolver Module DTCG называет эту проблему прямо: «alternate contexts are susceptible to combinatorial
explosion». Penpot формулирует решение: «Themes are multidimensional… you can have more than one theme
active at the same time». Подробнее — `03-theming-and-modes.md`.

### 2.9. Полиерархия

Одно решение может принадлежать двум наборам. Пример Curtis: «error red» — это и `color-feedback-error`
(набор статусов), и `ui-controls-color-text-error` (набор контролов).

Рекомендация: **сохранить оба имени и связать алиасом**, а не выбирать одно:

```
$ui-controls-color-text-error = $color-feedback-error = $color-red-36 = #B90000
```

Два повода так делать: каждый набор остаётся полным (в наборе контролов есть все нужные токены), и
будущее расхождение значений не потребует переименования — достаточно разорвать алиас.

### 2.10. Имя — производная пути

Carbon формулирует это как правило сборки: «The group name is the authoritative category for a token.
The Style Dictionary pipeline reads `token.path[0]` (the group key) to decide which generated file the
token belongs to — **no name-prefix inference, no hidden ordering rules**». Группа → файл Sass → карта
Sass. Имя в JS — camelCase от собственного ключа: `spacing-05` → `spacing05`.

Следствие, о котором Carbon предупреждает отдельным разделом «Tip for agents»: имя вида
`border-subtle-02` в JSON не существует как строка — это путь `border` → `subtle` → `02`.
**«Do not grep for the full hyphenated name — it will not match».**

То же у Carbon и Panda CSS — «двойные узлы»: токен одновременно значение и группа (`background` плюс
`background.active` плюс `background.hover`). На выходе получаются плоские имена-братья `background`,
`background-active`, `background-hover`. У Panda тот же приём называется `DEFAULT`:

```js
primary: { DEFAULT: { value: '{colors.gray.100}' }, muted: { value: '{colors.gray.100}' } }
```

По спецификации 2025.10 объект с `$value` и дочерними токенами — **ошибка**, инструменты MUST об этом
сообщать. В черновике следующей версии для этого введено зарезервированное имя `$root`: путь
`color.accent.$root`. То есть до выхода следующей редакции двойные узлы — это выход за стандарт, и
Carbon с Panda решают задачу собственными средствами.

### 2.11. Ссылка по имени или по идентификатору

| Способ | Кто | Плюс | Минус |
|---|---|---|---|
| `{group.token}` | DTCG, Style Dictionary, Terrazzo, Penpot, Tokens Studio | читается глазами, грепается | переименование ломает ссылки |
| JSON Pointer `$ref` | DTCG (черновик 2026) | может указывать в любое место документа, включая `#/colors/blue/$value/components/0` | нечитаемо |
| `uuid` | Adobe Spectrum | переименование не ломает ничего | файл нечитаем без инструмента |

Для генеративного конвейера правильный выбор — `{group.token}`: модель работает с текстом, и ссылка,
которую видно, дешевле ссылки, которую надо резолвить.

---

## 3. Сколько токенов

### 3.1. Порядки величин в живых системах

| Система | Токенов | Как посчитано |
|---|---|---|
| **Atlassian** | **596** | `@atlaskit/tokens@18.2.1`, `artifacts/token-names.js`: color 442, motion 72, space 23, font 23, elevation 21, radius 8, border 3, opacity 2, utility 2 |
| **Adobe Spectrum 2** | 597 **только** в `layout` + `typography` | подсчёт по массиву токенов; всего 7 файлов, `color-palette` 487 КБ |
| **IBM Carbon** | 250+ на тему × 4 темы | `themes.json` 93 КБ + `components/*.json` |
| **Plasma (Сбер)** | ~2000 значений на режим | `plasma_b2c.json`: light 1958 листьев, dark 1972, shadow 16; шесть брендовых тем |
| **Material 3** | 49 ролей цвета + shape + typescale + motion + ~90 файлов `md-comp-*` | исходники `material-web` |
| **Fluent 2** | 619 строк плоского списка CSS-переменных в `tokens.ts` | 11 радиусов, 22 отступа (11 × 2 оси), 8 длительностей, 9 кривых |
| **Polaris** | ~250 | по числу `value:` в 11 файлах |
| **shadcn/ui** | **37** | 23 цвета + 5 chart + 8 sidebar + radius |
| **Radix Themes** | шкалы + 7 ручек | 30+ акцентных шкал × 12 шагов + альфа-версии |

Внутри цвета у Atlassian: `color.background` 208, **`color.chart` 100**, `color.text` 49,
`color.border` 40, `color.icon` 23, `color.rovo` 11 (ИИ-функции), `color.link` 4, `color.blanket` 3,
`color.skeleton` 2, `color.interaction` 2.

### 3.2. Сколько нужно продукту

**150–300 семантических токенов.** Обоснование от границ:

- **37** (shadcn) — нижняя граница жизнеспособности. Нет статусов кроме `destructive`, нет шкалы
  отступов, нет размеров контролов, нет z-index, нет движения. Всё это приходится дописывать вручную,
  то есть значения попадают в компоненты как литералы.
- **185 семантических** (эталонная схема, `04-reference-token-schema.md`) — покрывает цвет, отступы,
  размеры, форму, глубину, слои, прозрачность, движение, брейкпоинты и типографику одного продукта с
  двумя темами и двумя режимами плотности.
- **596** (Atlassian) — платформа из десятков продуктов, четыре темы, палитра графиков на 100 значений,
  композитные анимации как токены. Для одного продукта это в 3–4 раза больше нужного.
- **~2000 на режим** (Plasma) — шесть брендов и мобильные приложения.

### 3.3. Закон убывающей отдачи

Nathan Curtis (в пересказе доклада Config): чем больше компонентов в системе, тем **выше стоимость
каждого следующего** и **ниже его ценность** `[V16 A]`. То же справедливо для токенов: 200-й
семантический токен почти наверняка используется один раз.

Числа из практики:

- **Wolt**: «2–3 заголовка и 2 стиля основного текста за глаза»; антипример — столько теней, что нельзя
  выбрать между elevation 6 и 8 `[V18 A]`.
- **Яндекс Маркет**: добавление второго размера основного текста (14 к 16) обсуждали **около двух
  месяцев** `[V18 A]`. Токен — это не строчка в файле, а обязательство.
- **Uber**: 71 компонент, из них ~20 ядро `[V16 B]`.
- **Авито**: при смене бренда нетокенизированный логотип нашли **более чем в 120 местах** `[V18 B]` —
  обратная сторона: недотокенизация стоит дороже, чем лишний токен.

Правило отбора, которое из этого следует: **добавляй токен, когда отсутствие токена уже стоило времени**
(значение продублировано в трёх местах, или его пришлось искать), а не когда «кажется, пригодится».

---

## 4. Практические решения для генеративного конвейера

### 4.1. Что модель должна уметь делать с именем

| Задача | Что нужно от имени |
|---|---|
| выбрать токен под контекст «padding карточки» | метка в `usage`, а не догадка по имени |
| понять, куда нельзя применять | явный запрет в `rules` |
| найти пару «фон → передний план» | конвенция `-foreground` / `on-` |
| не перепутать примитив и семантику | разные префиксы CSS-переменных (`--palette-*` против `--bg-*`) |
| дописать токен в группу | `$type` на группе, чтобы нечего было забыть |

Отсюда вывод: для агента важнее не «красивое имя», а **то, что лежит рядом с именем** — описание, метки
применения и правила. Формат такого блока разобран в `04-reference-token-schema.md` §3.

### 4.2. Конвенция `-foreground` / `on-`

Две записи одного правила:

| Конвенция | Пример | Системы |
|---|---|---|
| `on-<роль>` | `on-primary`, `on-surface`, `on-error-container` | Material, Carbon (частично) |
| `<роль>-foreground` | `--primary-foreground`, `--card-foreground` | shadcn, Tailwind-экосистема |
| `fgColor.on<Роль>` | `fgColor.onEmphasis`, `fgColor.onInverse` | Primer |
| `text-<роль>-on-bg-fill` | `text-success-on-bg-fill` | Polaris |

Formulировка shadcn: «The base token controls the surface color and the `-foreground` token controls the
text and icon color that sits on that surface. The background suffix is omitted for the surface token».

Выбор для конвейера: **суффикс `-foreground` или `on-`, но один на всю систему.** Суффикс удобнее при
сортировке (`primary` и `primary-foreground` стоят рядом), префикс `on-` удобнее при чтении вслух.

### 4.3. Имя в макете = имя в коде

Принцип из доклада о русских системах: токен и компонент в макете должны называться так же, как в коде
`[V18 A]`. Иначе дизайнер говорит «Text/Body/Medium», разработчик слышит `--type-body-size`, и каждое
обсуждение начинается с перевода.

Механизм, который это обеспечивает: Primer кладёт в токен `org.primer.figma.codeSyntax.web` — готовую
строку для вставки в код, `'var(--fgColor-default) /* utility class: .color-fg-default */'`. Figma
показывает её в инспекторе. Без Figma то же достигается механическим правилом «путь токена → имя
переменной» (`04-reference-token-schema.md` §6.3).

### 4.4. Scoping: где переменную вообще можно применять

Figma называет это scoping, Primer записывает в `org.primer.figma.scopes`: `fgColor`, `radius`, `gap`,
`borderWidth`, `effectFloat`. Смысл: переменная толщины границы не предлагается там, где задаётся
отступ `[V16 A]`.

В коде аналога нет — CSS-переменную можно подставить куда угодно. Ближайшее средство: метки `usage` в
расширении токена плюс линтер, проверяющий, что `--corner-*` встречается только в `border-radius`, а
`--z-*` только в `z-index`. Такой линтер — тема волны 3, папка 13.

---

## Частые ошибки

1. **Три уровня токенов в первый день.** Стоимость уровня — не файл, а дисциплина: каждый новый
   компонент требует решения «заводить компонентный токен или нет».
2. **Компонентный токен под один компонент.** Пока компонентов меньше трёх, значение живёт в коде.
3. **Значение в имени семантического токена** (`color.blue.primary`, `space-16`, `radius-6`).
4. **Сокращения ради краткости JSON** (`bg`, `fg`, `bdr`, `clr`). В CSS-переменных допустимо, в путях
   токенов — нет.
5. **Последовательная нумерация цветовой шкалы 1, 2, 3** без запаса на вставку. Либо шаг 100, либо
   фиксированная семантика каждой ступени, как у Radix.
6. **`-default` у всех токенов набора.** Часть имени, одинаковая у 100 % токенов, — шум.
7. **Смешение темы и режима в одной оси.** `theme-dark-compact-brand-a` вместо трёх независимых
   модификаторов.
8. **Выбор одного имени там, где нужны два.** Полиерархия решается алиасом, а не спором.
9. **Грепанье плоского имени.** `border-subtle-02` в JSON не существует как строка.
10. **Токен без описания применения.** Через полгода никто не помнит, чем `bg-component` отличается от
    `bg-subtle`.
11. **Namespace там, где он не нужен.** Префикс системы имеет смысл, только если на странице живут две
    системы; иначе это +3 символа в каждом вхождении.
12. **Формульный средний уровень без возможности переопределить точку.** Ant Design выводит радиусы
    формулой; если нужен радиус 5 на конкретной ступени, формулу придётся ломать.

### Ошибки, типичные для нейросетей

- **Изобретение синонимов.** `--text-color-main`, `--main-text`, `--foreground-primary` рядом с
  существующим `--fg-primary`. Лечится тем, что в `rules` соседние токены названы явно, и тем, что
  список токенов подаётся модели целиком, а не по частям.
- **Смешение уровней.** `background: var(--palette-neutral-100)` вместо `var(--bg-subtle)`. Формально
  работает, ломается при смене темы. Детектор: `--palette-*` и `--scale-*` не должны встречаться в
  файлах компонентов.
- **Достраивание несуществующих ступеней.** Модель, увидев `neutral.100` и `neutral.300`, пишет
  `neutral.200` там, где его нет в наборе статуса. Лечится проверкой «каждая ссылка резолвится».
- **Перевод английских частей имени.** `--фон-холст`. Имена токенов, свойств и систем остаются
  английскими всегда.
- **Копирование грамматики из другой системы в середине файла.** Начали с `bgColor.danger.emphasis`
  (Primer), продолжили `--destructive` (shadcn). Внутри одного набора грамматика должна быть одна.
- **Компонентный токен под каждое свойство компонента.** `--button-primary-hover-border-radius-top-left`.
  Радиус не зависит от варианта и состояния (§2.7).

---

## Чек-лист

1. Уровней токенов два (примитивы + семантика)? Если три — обоснован ли третий тремя компонентами?
2. Длина самой длинной цепочки алиасов ≤ 3?
3. Ни одно семантическое имя не содержит значения (`blue`, `16`, `600`, `bold`)?
4. Все семантические имена описывают роль, а не внешний вид?
5. Сокращения в путях токенов отсутствуют (`background`, а не `bg`)?
6. Шаг числовой шкалы 100 (или ступеням назначена фиксированная семантика, как у Radix)?
7. Для отступов выбран один вид шкалы (t-shirt, числовая или пропорциональная) и он же используется
   везде?
8. Есть ли явные токены-назначения (`space.inset.card`), а не только шкала?
9. Порядок частей имени одинаков во всём наборе?
10. Ни одна часть имени не повторяется у 100 % токенов?
11. Тема и режим разведены по разным осям?
12. Полиерархические решения связаны алиасом, а не продублированы значением?
13. Имя токена выводится из пути, а не задаётся отдельной строкой?
14. Конвенция пары «поверхность → передний план» одна на всю систему (`-foreground` или `on-`)?
15. У каждого семантического токена есть описание применения?
16. Число семантических токенов в диапазоне 150–300?
17. Есть ли в наборе токен, использованный ровно один раз? (это кандидат на удаление)
18. Имена в макете и в коде совпадают?

---

## Открытые вопросы и противоречия

1. **T-shirt против пропорциональной шкалы отступов.** Curtis публично изменил позицию в пользу
   пропорциональной, практика 2026 года почти вся на t-shirt и числовых. Аргумент Curtis не опровергнут,
   просто не принят.
2. **Парсимония против точности в статусах.** `$color-success` (один токен) против
   `$color-background-success` + `$color-text-success` + `$color-border-success` (три). Все крупные
   системы выбрали точность, но никто не измерял, сколько стоит лишний выбор для человека или модели.
3. **Двойные узлы вне стандарта.** Carbon и Panda используют узел, который одновременно токен и группа;
   спека 2025.10 это запрещает, черновик 2026 вводит `$root`. До выхода следующей редакции переносимость
   таких наборов не гарантирована.
4. **Контекстные токены не выражаются в DTCG.** Механизм `<Layer>` у Carbon живёт в Sass. Стандартного
   способа сказать «значение зависит от глубины вложенности» нет.
5. **Нет контролируемого словаря меток применения.** `usage` у Primer — свободные строки; совпадение
   меток между токенами не гарантировано, машинный поиск «какой токен взять для card-padding» работает
   на удачу.
6. **Правило трёх компонентов не проверено данными.** Это эвристика одного автора; исследований, что
   именно три, а не два или пять, нет.
7. **Цена namespace не измерена.** Gravity UI пишет `--g-`, Salesforce `--slds-`, Material `--md-sys-`;
   большинство новых систем префикса не имеют. Аргументов за обе стороны поровну.

---

## Источники

1. `[S17]` Nathan Curtis (EightShapes). Naming Tokens in Design Systems. Через
   https://web.archive.org/web/2024/https://medium.com/eightshapes-llc/naming-tokens-in-design-systems-9e86c7444676
   — 379 строк, прочитано целиком. Основной источник по грамматике имён; уровни имени, пять видов шкал,
   completeness / order / polyhierarchy, правило трёх компонентов.
2. `[S18a]` Brad Frost. The Many Faces of Themeable Design Systems.
   https://bradfrost.com/blog/post/the-many-faces-of-themeable-design-systems/ — семь видов темизации.
3. `[S18b]` Brad Frost. Creating Themeable Design Systems.
   https://bradfrost.com/blog/post/creating-themeable-design-systems/ — Tier 1/2/3 и оговорка про
   overkill.
4. `[S1a]` W3C DTCG. Design Tokens Format Module 2025.10.
   https://www.designtokens.org/TR/2025.10/format/ — правила имён (`$`, `{`, `}`, `.` запрещены),
   наследование `$type`, запрет узла-токена-и-группы.
5. `[S1c]` W3C DTCG. Color Module 2025.10, раздел 7 «Token naming».
   https://tr.designtokens.org/color/ — Base / Alias / Component, шаг 100, `background` вместо `bg`.
6. `[S2]` GitHub Primer. `primer/primitives`, `src/tokens/**` — base / functional, `org.primer.figma`
   со `scopes` и `codeSyntax`, `org.primer.llm`.
7. `[S3]` IBM Carbon. `carbon-design-system/carbon`, `packages/{colors,themes,layout}/src/dtcg/*` и
   README — маршрутизация по группам, двойные узлы, контекстные токены, «Tip for agents».
8. `[S9]` Ant Design 5. `components/theme/themes/seed.ts`, `shared/genRadius.ts`, `genFontSizes.ts`,
   `genControlHeight.ts`, `genSizeMapToken.ts` — seed → map → alias, формулы, кусочно-линейный радиус.
9. `[S10]` Adobe. `adobe/spectrum-design-data`, `packages/design-data/tokens/*.tokens.json` — фасеты
   имени, ссылки по uuid, `conceptId`, `set_schema`, `lifecycle`.
10. `[S11]` Shopify Polaris. `polaris-tokens/src` — единый ряд `size`, алиасы-назначения.
11. `[S12]` Microsoft Fluent 2. `microsoft/fluentui`, `packages/tokens/src` — global / alias, отступы
    по осям, ступени «nudge».
12. `[S13]` Material 3. `material-components/material-web`, `tokens/versions/v0_192` — `md-ref` /
    `md-sys` / `md-comp`, 49 ролей цвета.
13. `[S14]` Atlassian. `@atlaskit/tokens@18.2.1` — 596 токенов и их разбивка по группам.
14. `[S7]` shadcn/ui. Theming. https://ui.shadcn.com/docs/theming — 37 переменных, конвенция
    `-foreground`.
15. `[S8]` Radix Themes. `packages/radix-ui-themes/src/styles/tokens/*` — семантика ступеней 1–12,
    семь ручек.
16. `[S6]` Tailwind CSS v4. `packages/tailwindcss/theme.css` — пространства имён.
17. `[S22a]` Panda CSS. Tokens и semanticTokens. https://panda-css.com/docs/theming/tokens — `DEFAULT`
    как двойной узел, категории токенов.
18. `[S19a]` Figma. Overview of variables, collections, and modes.
    https://help.figma.com/hc/en-us/articles/14506821864087 — scoping, алиасинг, лимиты.
19. `[V16]` Figma Config: Uber и Linear — `91-videos/digests/`; закон убывающей отдачи, scoping,
    псевдотокены уровня компонента.
20. `[V18]` Wolt и Авито — `91-videos/digests/`; бритва Оккама, цена нового значения, имя в макете =
    имя в коде, логотип в 120 местах.
21. `[V12]` Jan Six. Design Tokens in Figma — `91-videos/digests/`; проверка имени «если токен для
    цвета текста применён не к тексту — что-то идёт не так».
22. Внутренние файлы: `01-color/02-semantic-roles-and-architecture.md` §1.1, §1.3;
    `02-typography/02-type-scale.md` §4.1; `03-spacing-sizing/01-spacing-scale.md` §1.2;
    `04-shape-elevation/01-radius-and-borders.md` §1.1; `09-design-tokens/04-reference-token-schema.md`.
