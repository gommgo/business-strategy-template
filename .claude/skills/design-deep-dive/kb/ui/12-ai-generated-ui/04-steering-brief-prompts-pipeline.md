# Управление генерацией: бриф, пакет инструкций, шаблоны промтов, цикл

Волна 3, агент H, 22 сентября 2026. Прочитано целиком 27 внешних источников; шаблоны собраны из
официальных форматов (Figma Make `guidelines/`, v0 Design Systems 2.0, Google DESIGN.md), из
четырёхуровневой схемы CHI '26 и из протокола критики, выведенного из трёх исследований. Сырые заметки:
`../99-raw/notes/wave3/H-notes.md`.

Это рабочий файл папки: из него берутся готовые тексты. Значения (палитра, шкалы, размеры) сюда не
копируются — они приходят из `../09-design-tokens/`, `../11-styles-trends/` и пресетов волн 1–2.
Рубрика оценки из десяти измерений и общий промт модели-критика — у агента I в
`../13-evaluation-checklists/02-rubrics-and-vlm-critic.md`; здесь дана специализация под сгенерированный
экран и протокол вызова, выведенный из исследований.

## Выжимка для агента

1. **Бриф раскладывается на четыре уровня**: Product → Design System → Feature → Component. Схема выведена
   тематическим анализом 907 фрагментов руководств шести инструментов; структурированный ввод против чата
   даёт **p = 0,002, r = 0,87**. → §1.1 `[исследование]`
2. **Design System — это семь ручек**, а не двести решений: акцент, нейтраль, радиус, плотность, шрифт,
   тени, тема. → §1.2, `../09-design-tokens/05` §4.2 `[мнение]`
3. **Состояния и интерактивность обязаны быть в брифе.** В статических таксономиях UI их нет, в
   генеративном контексте они становятся значимыми семантиками. → §1.1 `[исследование]`
4. **Мягкое правило выполняется хуже жёсткого: 70,4 % против 92,3 %.** Формулируй числом и запретом.
   → §1.4 `[исследование]`
5. **Пакет инструкций собирается из трёх форматов**: язык — от Figma Make, стартовое приложение — от v0,
   формат и линтер — от DESIGN.md. → §2 `[система]`
6. **Много коротких файлов лучше нескольких длинных**: «Multiple short guidelines files are better than a
   few large files», верхний файл только маршрутизирует. → §2.1 `[система]`
7. **Императив вместо смягчения**: «"Do not use small text for anything except captions" is better than
   "Use small text sparingly"». → §2.1 `[система]`
8. **Дерево решений вместо описания.** Вопрос в кавычках → ветки «если … → токен». Формат Figma Make.
   → §2.2 `[система]`
9. **Пары CORRECT / WRONG на коде, по одной ошибке на пару.** → §2.2 `[система]`
10. **Колонка «Frequency» у цветов** (Dominant / Sparse / Internal) сообщает модели долю площади, а не
    только значение. → §2.2 `[система]`
11. **Запреты выносятся в отдельный обязательный раздел** «Do's and Don'ts» — последний по порядку в
    спецификации DESIGN.md. → §2.3 `[система]`
12. **Пропущенное поле брифа отдаётся дефолту модели.** Линтер DESIGN.md предупреждает прямо:
    `missing-primary` → «agents will auto-generate one», `missing-typography` → «agents will use default
    fonts». → §2.3 `[система]`
13. **Стартовое приложение — часть инструкции, а не приложение к ней**: «every future app begins from a
    working foundation instead of inheriting the same issue each time». → §2.4 `[система]`
14. **Правило верифицируемости**: «If a component, prop, or token cannot be verified from the sources,
    v0 should not use it». Это лучшая однострочная формулировка запрета на выдумывание. → §2.4 `[система]`
15. **Пять систем уже документируют себя для моделей** — Primer, Carbon, Untitled UI, Adobe, shadcn.
    Разбор как образцов. → §2.5 `[система]`
16. **Промт картинки UI строится из десяти блоков** в фиксированном порядке; полный шаблон — §3.1.
    → `[мнение]`
17. **Промт кодогенерации строится из шести блоков и одного жёсткого ограничения**: только токены, никаких
    литералов. → §3.4 `[мнение]`
18. **Критику и локализацию разводи по разным вызовам** (объединение даёт «task overload»); для
    локализации накладывай пронумерованные патчи: IoU 0,004 → 0,222. → §4.1 `[исследование]`
19. **Давай модели скриншот И машинный отчёт.** Удаление картинки — самое сильное падение; метаданные
    сильнее всего помогают локализации. → §4.1 `[исследование]`
20. **Дефект называй сам.** Самостоятельное обнаружение — 0,2714. → §4.1 `[исследование]`
21. **Промт правки состоит из трёх частей: что сделать, где, что не трогать.** «Ripple effect» описали
    5 из 14 участников CHI '26. → §3.6 `[исследование]`
22. **Цикл строится на отчёте проверок, а не на самокритике**: self-revision вредит слабым моделям
    (39,7 → 30,1). → §5.2 `[исследование]`
23. **Автоматизируется всё, что считается; человеку остаётся выбор направления, приёмка и решение о
    том, что «хватит».** → §5.5 `[мнение]`

---

## 1. Бриф: дизайн-ДНК продукта

### 1.1. Четыре уровня

Схема из CHI '26 `[S19]` — результат тематического анализа 907 фрагментов руководств по промтам шести
инструментов (v0, Stitch, Figma Make, Uizard, Lovable, Relume). Уровни связаны вертикально и
горизонтально: изменение одного элемента каскадом идёт по остальным.

| Уровень | Элементы | Кто заполняет |
|---|---|---|
| **Product** | Description, Target User, Goal | заказчик, один раз на продукт |
| **Design System** | Design Style, Color, Typography, Visual Properties, Visual Mood, Tone of Voice | квиз стиля (`../11-styles-trends/01` §20) → семь ручек → 287 токенов |
| **Feature** | Function, Content, Information Architecture | на каждый экран |
| **Component** | Type, **Interactivity**, **State**, Content, Properties | из спецификаций `../06-components-visual/` |

Два уровня заполняются один раз (Product, Design System) и переиспользуются; два — на каждую задачу.

**Interactivity и State подчёркнуты не случайно:** авторы отмечают, что эти элементы «часто отсутствуют в
статических таксономиях UI», но в генеративном контексте становятся значимыми семантиками. Если в брифе
не сказано, как выглядит выбранная строка и отключённая кнопка, модель придумает.

### 1.2. Шаблон брифа: заполняемая форма

```yaml
# БРИФ ПРОДУКТА — заполняется один раз, хранится рядом с токенами
product:
  description: ""            # что это: «бэк-офис для операторов логистики»
  target_user: ""            # кто: «оператор, 8 часов в смену, два монитора, мышь»
  goal: ""                   # зачем: «обработать заявку за 40 секунд без ошибок»
  primary_action: ""         # одно первичное действие продукта
  screens: []                # список типов экранов: список, форма, объект, дашборд, настройки
  locale: ru                 # язык интерфейса (влияет на ширины: RU длиннее EN в 1,41–1,49 раза)
  platforms: [desktop]       # desktop | desktop+mobile
  viewport_primary: 1440x900

design_system:
  style: ""                  # из словаря стилей: `../11-styles-trends/01-style-dictionary-for-quiz.md`
  knobs:                     # семь ручек характера
    accent: ""               # hex бренда или «нет бренда»
    neutral: ""              # slate | zinc | gray | тонированная в акцент
    radius: ""               # 0 | 4 | 6 | 8 | 10
    density: ""              # compact | default | spacious
    font: ""                 # семейство с кириллицей: `../02-typography/01` §3
    shadows: ""              # ring-only | ring+raised | full-scale
    theme: ""                # light | dark | both, что по умолчанию
  visual_mood: []            # 2–3 слова: «строгий, корпоративный, спокойный»
  tone_of_voice: ""          # для микрокопи; UX-часть — `../../ux/07-ux-writing/`
  bans: []                   # см. §1.4

feature:                     # на каждый экран
  screen_id: ""
  function: ""               # что делает экран
  content: []                # какие сущности и поля показываются, с реальными примерами значений
  information_architecture: ""  # что главное, что второстепенное, что скрыто
  empty_state: ""            # что показать, когда данных нет
  error_state: ""            # что показать при отказе
  loading_state: ""          # скелетон | спиннер | оптимистично

component:                   # на каждый нетиповой компонент
  type: ""
  interactivity: []          # hover, focus-visible, active, drag
  state: []                  # default, selected, disabled, loading, error, empty
  content: ""                # реальный текст, не lorem ipsum
  properties: {}             # отклонения от пресета, с обоснованием
```

**Правило заполнения:** пустое поле — это решение, отданное модели. Линтер DESIGN.md формулирует то же
самое машинно (§2.3).

### 1.3. Откуда берутся значения

| Что | Где взять |
|---|---|
| стиль и семь ручек | `../11-styles-trends/01-style-dictionary-for-quiz.md` (квиз §20, 18 карточек) |
| палитра и контрасты | `../01-color/` + `../../../scripts/lib/color.py` |
| шрифт с кириллицей | `../02-typography/01-font-selection.md` §3 |
| шкала кеглей | `../02-typography/02-type-scale.md` §7 (админка) и §8 (клиент) |
| отступы, высоты, плотность | `../03-spacing-sizing/03-control-and-panel-sizes.md` §8–§9 |
| радиусы и тени | `../04-shape-elevation/01` и `02` |
| каркас и ширины | `../05-layout-grid/02-app-shells.md` §10 |
| спецификации компонентов | `../06-components-visual/08-values-by-system-table.md` |
| иконки и иллюстрации | `../07-iconography-imagery/` |
| движение | `../08-motion/03` §7 (два пресета) |
| токены целиком | `../09-design-tokens/04-reference-token-schema.md` (289 токенов) |
| нормы приёмки | `../10-design-systems-atlas/04-live-products-measured.md` §8 |

### 1.4. Запреты: почему они обязательны и как формулировать

Два числа определяют форму:
- **мягкие ограничения чинятся хуже жёстких: 70,4 % против 92,3 % recall** `[S18]`;
- **запрет снижает вероятность, но не исключает паттерн** — поэтому всегда в паре с проверкой.

Правило формулировки из Figma Make `[S15]`: **«Use clear, concise language: "Do not use small text for
anything except captions" is better than "Use small text sparingly". Be specific and imperative.»**

Базовый список запретов для рабочего веб-сервиса (копируется в бриф и в промты):

```
ЗАПРЕЩЕНО
- Градиенты в качестве фона, заливки кнопок и границ. Градиент допустим только в графиках.
- Свечение: box-shadow с нулевым смещением и blur больше 8.
- backdrop-filter больше чем на двух элементах экрана.
- Тень у карточек. Карточка держится на границе 1px.
- Эмодзи в интерфейсе. Иконки только из набора {назвать набор}.
- Фиолетовые и индиго акценты, если они не заданы брендом.
- Три одинаковые карточки в ряд; repeat(3, 1fr) в сетке карточек.
- Центрирование текстовых блоков, кроме пустого состояния, диалога и карточки входа.
- Кегль крупнее {32} px на экранах приложения.
- Кнопки-пилюли в рабочем интерфейсе.
- z-index числом вне шкалы.
- Произвольные значения вне шкалы отступов: {0,2,4,8,12,16,24,32,48}.
- Литералы цвета и размера в компонентах: только var(--*).
- Новые токены без явной просьбы.
- Lorem ipsum и выдуманные логотипы.
```

---

## 2. Пакет инструкций для генератора

Бриф — это то, что говорит заказчик. Пакет инструкций — то, что читает модель перед каждой генерацией.
Три публичных формата разобраны ниже; §2.6 собирает из них рабочий.

### 2.1. Структура: дерево коротких файлов (Figma Make) `[S15]`

Самый подробный публичный документ «как писать инструкцию для генератора». Ключевые правила авторства:

- **«Multiple short guidelines files are better than a few large files.»** Строить с прогрессивным
  раскрытием и с оглядкой на окно контекста; верхний файл только маршрутизирует.
- Папки соответствуют частям дизайн-системы; несколько обзорных файлов, а не один.
- **Раздел «Reading order»** с пометкой `MUST READ before writing any code` и списком по порядку, плюс
  отдельный список `Read on-demand`.
- **Раздел «Workflows»** — пошаговые процедуры: «Before using a component», «Before using an icon»,
  «When building a layout».
- **Раздел «Rules»** с префиксом `IMPORTANT:` для жёстких инвариантов.

Скелет дерева:

```
guidelines/
  overview.md              # характер продукта, reading order, workflows, жёсткие правила
  setup.md                 # провайдеры, импорты стилей, сборка, что НЕ делать в конфиге
  foundations/
    color.md               # роли, частотность, деревья решений, CORRECT/WRONG
    typography.md          # композитные классы, деревья решений, запрещённые веса
    spacing.md             # шкала, что считается исключением
    modes.md               # светлая/тёмная, плотность
    icons.md               # набор, размеры, выравнивание
  composition/
    layout.md              # каркас, ширины, сетки
    surfaces.md            # слои, что несёт иерархию
    hierarchy.md           # чем задаётся важность
  components/
    overview.md            # каталог с альтернативными именами и ссылками
    button.md, input.md, table.md, navigation.md, feedback.md, modal.md
  icon-discovery.md        # список доступных иконок
```

### 2.2. Язык инструкции: четыре приёма Figma Make

**1. Блок «Product character» вместо прилагательных.** Готовый шаблон из официального примера:

```md
## Product character

This is a **{B2B internal tool}** with a **{strict, dense, utilitarian}** UI style.

- **Density**: {Dense — 32px controls, 36px table rows, 16px card padding}
- **Surface strategy**: {Bordered — white cards on a #f8fafc canvas; borders create hierarchy, not shadows}
- **Color palette**: {~92% neutral surfaces. Accent (#155dfc) is used only for primary actions,
  active states and small accents.}
- **Corner style**: {radius-md 6px default, radius-sm 4px for inputs, radius-full for avatars only}
- **Elevation**: {Border-driven — shadows reserved for floating overlays only}
```

Обратить внимание: **каждое поле — значение с числом или явной стратегией**, а не эпитет.

**2. Дерево решений вместо описания.** Формат: вопрос в кавычках → ветки «условие → токен».

```
┌─ "Какой фон использовать?"
│
├─ Холст страницы?                        └─ bg-canvas
├─ Поднятый контент (карточка, панель)?   └─ bg-surface
├─ Утопленная область внутри карточки?    └─ bg-subtle
├─ Фон поля ввода?                        └─ bg-input
├─ Наведение на интерактивную область?    └─ bg-hover
├─ Первичная кнопка?                      └─ bg-accent + text-on-accent
└─ Подложка модалки?                      └─ bg-scrim
```

Такие деревья пишутся для: варианта кнопки, типа поля ввода, компонента обратной связи, уровня навигации,
цвета фона, цвета текста, цвета границы, цвета иконки, типографической роли. Девять деревьев закрывают
почти все повторяющиеся решения.

**3. Пары CORRECT / WRONG, по одной ошибке на пару.**

```tsx
{/* CORRECT — композитный класс роли */}
<h1 className="text-page-title text-primary">Заказы</h1>

{/* WRONG — произвольный размер и интерлиньяж */}
<h1 className="text-2xl leading-8 font-semibold">Заказы</h1>
```

```tsx
{/* CORRECT — белый текст на акценте */}
<button className="bg-accent text-on-accent">Сохранить</button>

{/* WRONG — основной текст исчезает на акценте */}
<button className="bg-accent text-primary">Сохранить</button>
```

**4. Колонка «Frequency» у цветов.** Она сообщает модели долю площади, а не только значение:

| Роль | Значение | Токен | **Frequency** | Применение |
|---|---|---|---|---|
| Холст | `#f8fafc` | `--bg-canvas` | **Dominant** | фон страницы |
| Поверхность | `#ffffff` | `--bg-surface` | **Dominant** | карточки, панели, сайдбар |
| Основной текст | `#0f172b` | `--text-primary` | **Dominant** | текст |
| Акцент | `#155dfc` | `--accent-solid` | **Sparse** | первичные кнопки, активные вкладки |
| Тёмная поверхность | `#1d293d` | `--surface-inverse` | **Internal** | тултипы |

**Плюс явный список несуществующих значений:** «Do not use variant names that don't exist ("secondary",
"ghost", "destructive"). Valid variants are: "primary", "neutral", "subtle" — nothing else.»

**Плюс правило иерархии**, которое стоит скопировать дословно: **«Reduce importance through scale (smaller
type class), not opacity.»**

### 2.3. Формат файла: DESIGN.md `[S16]`

Открытая спецификация Google Labs (github.com/google-labs-code/design.md, статус alpha).
Два слоя в одном файле: **YAML front matter с токенами** (нормативные значения) и **markdown-проза с
обоснованием** («Tokens give agents exact values. Prose tells them *why* those values exist»).

**Канонический порядок разделов прозы** — готовый каркас брифа:

1. Overview (алиас Brand & Style) → 2. Colors → 3. Typography → 4. Layout (Layout & Spacing) →
5. Elevation & Depth → 6. Shapes → 7. Components → **8. Do's and Don'ts**.

Секции можно опускать, но порядок обязателен; **дубль заголовка — ошибка, файл отклоняется**.

Схема токенов: `version`, `name`, `description`, `omitted`, `colors`, `typography`, `rounded`, `spacing`,
`components`. Типы значений: любой CSS-цвет (включая `oklch()`), размер `число + px|em|rem`, ссылка
`{path.to.token}`, типографический объект (`fontFamily`, `fontSize`, `fontWeight`, `lineHeight`,
`letterSpacing`, `fontFeature`, `fontVariation`).

Компонентные токены: `components.<name>.{backgroundColor, textColor, typography, rounded, padding, size,
height, width}`; **варианты — отдельные записи с родственным ключом** (`button-primary`,
`button-primary-hover`), а не вложенные состояния.

**Одиннадцать правил линтера** (`npx @google/design.md lint DESIGN.md`, вывод JSON, exit 1 при ошибках):

| Правило | Уровень | Что ловит |
|---|---|---|
| `broken-ref` | error | ссылка не резолвится |
| `missing-primary` | warning | цвета есть, `primary` нет — **«agents will auto-generate one»** |
| `contrast-ratio` | warning | пара фон/текст компонента ниже **WCAG AA 4,5:1** |
| `orphaned-tokens` | warning | цвет определён, но не используется ни одним компонентом |
| `missing-typography` | warning | **«agents will use default fonts»** |
| `section-order` | warning | секции не в каноническом порядке |
| `unknown-key` | warning | опечатка в ключе (`colours:` → `colors:`) |
| `token-like-ignored` | warning | неизвестный ключ с токеноподобными значениями |
| `token-summary`, `missing-sections`, `omitted-rules` | info | сводки и проверка конфигурации |

**Два правила прямо описывают механизм слопа:** пропуск поля передаёт решение дефолту модели, и авторы
формата это фиксируют машинно. Это самый сильный аргумент в пользу полноты брифа.

Остальные команды: `diff` (потокенное сравнение двух версий, exit 1 при регрессии), `export --format
json-tailwind | css-tailwind | tailwind | dtcg` (**выгрузка в W3C DTCG и в `@theme {}` Tailwind v4**),
`spec [--rules]` — печать самой спецификации, официально описанная как **«useful for injecting spec
context into agent prompts»**.

Связь с папкой 09: DESIGN.md — это **надстройка «токены + проза + запреты» над DTCG**, а не замена.
Источник истины по значениям остаётся `tokens.json` (`../09-design-tokens/04`); DESIGN.md генерируется из
него и добавляет прозу и запреты.

### 2.4. Стартовое приложение как часть инструкции (v0) `[S13]`

Design Systems 2.0 сохраняет дизайн-систему как **скилл**: «not a copy of your docs; it is an adapter that
tells v0 where your source lives, which components, props, and tokens are safe to use, and how to wire the
system into new apps».

Что берётся как источник (в порядке ценности по документации):
1. **реальное приложение, которое использует систему** — «often the most valuable source because it shows
   providers, global styles, fonts, theme setup, and correct component usage»;
2. пакет или репозиторий дизайн-системы;
3. Storybook, документация, гайдлайны;
4. кадры Figma (импортируется скриншот плюс извлечённый контекст кадра);
5. заметки: глобальные стили, провайдеры, шрифты, **устаревшие компоненты, антипаттерны, подводные камни**.

Два правила, которые стоит перенести в любой собственный пакет:

- **«If a component, prop, or token cannot be verified from the sources, v0 should not use it.»**
  Однострочный запрет на выдумывание.
- **`starter` в `v0.json`** — стартовое приложение сохраняется в скилл, и «every app you build with the
  design system later starts from it… A correct starter means every future app begins from a working
  foundation instead of inheriting the same issue each time».

Практический вывод: **эталонный экран (или три) — обязательная часть пакета**, а не иллюстрация к нему.
Модель копирует структуру из примера гораздо надёжнее, чем выводит её из описания.

### 2.5. Пять систем, которые документируют себя для моделей

Из `../10-design-systems-atlas/` §9; разбор как образцов:

| Система | Механизм | Что заимствовать |
|---|---|---|
| **GitHub Primer** | расширение `org.primer.llm` внутри самих токенов: `usage`, `rules`, `doNotUse`, `alternatives` | **правила применения живут в токене**, а не в отдельном документе; три уровня модальности: `MUST use for…`, `RECOMMENDED default for…`, `Use for…`, запрет `Do NOT use for…` **с причиной в том же предложении** |
| **IBM Carbon** | раздел «Tip for agents» в README, обязательный `$description` у каждого токена | короткая подсказка в точке, где модель читает код |
| **Untitled UI** | `CLAUDE.md` в репозитории | инструкция лежит там же, где код, и обновляется вместе с ним |
| **Adobe Spectrum** | MCP-сервер и плагин для Claude Code | инструмент вместо документа: модель запрашивает данные, а не читает дамп |
| **shadcn/ui** | `/llms.txt`, MCP-сервер, раздел Skills, «Open in v0» | машиночитаемый индекс всего, что есть |

**Правило Primer стоит скопировать дословно**: у каждого семантического токена — поля `usage`, `rules`,
`doNotUse`, `alternatives`; запрет всегда с причиной. Это снимает самую частую ошибку — применение
формально правильного токена не по назначению (`../09-design-tokens/05` §3.4).

### 2.6. Рабочий пакет: что собирать самим

```
design-system/
  DESIGN.md                    # формат Google Labs: YAML-токены + проза + Do's and Don'ts
  tokens.json                  # источник истины, DTCG 2025.10 (папка 09)
  tokens.css, theme.css        # выпуск из tokens.json
  guidelines/                  # дерево коротких файлов по образцу Figma Make
    overview.md                # Product character + Reading order + Workflows + IMPORTANT-правила
    setup.md
    foundations/{color,typography,spacing,icons,modes}.md
    composition/{layout,surfaces,hierarchy}.md
    components/{overview,button,input,table,navigation,feedback,modal}.md
  starter/                     # эталонное приложение: три собранных экрана
    list.tsx, form.tsx, dashboard.tsx
  checks/                      # то, чем проверяется результат
    greps.sh                   # пять грепов (`../09-design-tokens/05` §3.2)
    audit.sh                   # ui_audit.py (`../13-evaluation-checklists/03`)
```

Порядок генерации пакета:
1. бриф (§1.2) → семь ручек → `tokens.json` через генератор (`../../../scripts/ui/build_reference_tokens.py`);
2. `tokens.json` → `DESIGN.md` (токены в front matter, проза из брифа, запреты из §1.4);
3. `npx @google/design.md lint DESIGN.md` — чтобы пропущенные поля стали видны;
4. `guidelines/` пишутся по образцам §2.1–§2.2, значения подставляются из токенов;
5. `starter/` собирается вручную и принимается по чек-листу — это самая дорогая и самая окупающаяся часть;
6. пакет кладётся в контекст генератора (для Claude Code — `CLAUDE.md` со ссылками, для v0 — импорт
   дизайн-системы, для Figma Make — Make kit).

---

## 3. Шаблоны промтов

Все шаблоны с плейсхолдерами в фигурных скобках. Значения подставляются из брифа и токенов.

### 3.1. Картинка интерфейса

Общий каркас из десяти блоков. Ниже — три заполненных варианта.

**Вариант A: светлая плотная админка**

```
UI screenshot of a web admin panel for {логистика: обработка заявок}, desktop 1440×900, light theme,
real product interface, not a concept.

LAYOUT
Left sidebar 240px wide with 9 navigation items, each 32px tall with a 16px icon and a label;
two group captions. Top bar 48px with a breadcrumb on the left and a 24px avatar on the right.
Content area with 24px padding: page title 20px, a subtitle line, a row of 4 KPI cards,
then a data table with 12 rows.

PALETTE (use exactly these)
background #f8fafc, surfaces #ffffff, primary text #0f172b, secondary text #45556c,
borders #e2e8f0, accent #155dfc, text on accent #ffffff,
success #008236, warning #e17100, danger #e7000b.

TYPOGRAPHY
Inter. Body 14px, table cells 14px, captions 12px, page title 20px semibold, KPI numbers 28px semibold.

SHAPE AND DEPTH
Corner radius 6px on buttons and cards, 4px on inputs. Borders 1px.
Cards sit on a 1px border with NO shadow. No elevation anywhere on the page.

DENSITY
Button height 32px, input height 32px, table row height 36px, card padding 16px, cell padding 6px 12px.

CHARACTER
Strict, corporate, utilitarian. Information first, decoration none.

DO NOT
No gradients. No glow. No glassmorphism. No shadows on cards. No emoji. No 3D. No pill buttons.
No centered hero. No three identical feature cards. No purple or violet. No oversized display type.
No invented brand logos. No lorem ipsum.

TECH
16:10 aspect ratio, maximum steps, sharp flat rendering.
```

**Вариант B: тёмный инструмент для разработчика**

```
UI screenshot of a developer tool, desktop 1440×900, dark theme, real product interface.

LAYOUT
Icon rail 56px on the far left, secondary panel 280px, main area split into an editor pane
and a 240px right inspector. Bottom status bar 28px.

PALETTE
background #0d1117, elevated surface #161b22, primary text #e6edf3, secondary text #8b949e,
borders #30363d, accent #2f81f7, text on accent #ffffff, success #3fb950, danger #f85149.

TYPOGRAPHY
Inter for UI, JetBrains Mono for code and identifiers. Body 13px, code 13px, captions 11px,
panel titles 13px semibold.

SHAPE AND DEPTH
Radius 6px. Borders 1px. Depth is shown by surface lightness, not by shadows.
Floating layers get a 1px ring plus a soft shadow.

DENSITY
Control height 28px, tree row 24px, panel padding 8px, list item 24px.

CHARACTER
Dense, technical, quiet. Every pixel carries data.

DO NOT
No neon. No glow. No gradients. No emoji. No rounded pill buttons. No decorative illustrations.
No blurred backgrounds. Do not make it look like a music player.

TECH
16:10, maximum steps, crisp small text.
```

**Вариант C: клиентский личный кабинет**

```
UI screenshot of a customer account area of a web service, desktop 1440×900, light theme.

LAYOUT
Left sidebar 256px with 6 items. Top bar 56px. Content max-width 1200px, centered in the area,
32px page padding. Page title 24px, a two-column block: 2/3 main content, 1/3 summary panel 340px.

PALETTE
background #ffffff, surfaces #ffffff, page sections separated by #f1f5f9,
primary text #0f172b, secondary text #62748e, borders #e2e8f0,
accent {бренд}, text on accent #ffffff.

TYPOGRAPHY
{гарнитура}. Body 16px, captions 13px, section headings 18px semibold, page title 24px semibold.

SHAPE AND DEPTH
Radius 8px on cards, 8px on buttons, 6px on inputs. Borders 1px.
One level of elevation: cards flat, only popovers and modals raised.

DENSITY
Button height 40px, input height 40px, list row 56px, card padding 24px.

CHARACTER
Calm, reassuring, generous whitespace, still a working interface and not a landing page.

DO NOT
No hero section. No marketing copy. No gradients. No glow. No emoji. No stock photography.
No three feature cards. No pricing table.

TECH
16:10, maximum steps.
```

### 3.2. Серия иллюстраций

Заполняется по паспорту системы иллюстраций (`../07-iconography-imagery/02` §3). Постоянный блок
копируется во все кадры серии дословно.

```
[ПОСТОЯННЫЙ БЛОК — копируется во все кадры серии]
Flat vector illustration, single scene, transparent background, square canvas 1024×1024,
8% margin on all sides.
Palette: only these colours — {accent #155dfc}, {secondary #62748e}, {neutral #e2e8f0},
{surface #ffffff}, {one warm accent #e17100}. No other colours.
Line: {no outlines | uniform 2px outline in #0f172b}.
Perspective: flat front view, no vanishing point, no cast shadows.
Detail level: shapes no smaller than 4px at 1024; no textures, no gradients, no noise.
Characters: {no people | simplified figures without facial features}.
Style anchor: {style_id / --sref / reference image}.

[ПЕРЕМЕННЫЙ БЛОК — меняется от кадра к кадру]
Subject: {пустое состояние списка заказов: открытая коробка и пунктирный контур документа}.
```

**Серия иконок** — отдельный промт, только для Recraft или другого векторного генератора:

```
Vector icon, 24×24 canvas, live area 20×20, 2px padding.
Stroke only, 1.5px uniform stroke weight, round caps, round joins, no fills, no colour.
Single centred object, geometric construction, optically balanced.
No text, no shadows, no gradients, no perspective.
Style anchor: {style_id из 3–5 существующих иконок набора}.
Subject: {значение иконки}.
```

После генерации — чек-лист встраивания `../07-iconography-imagery/01` §2.5 и ручная доводка.
Растровую генерацию иконок не использовать (`01-image-models-for-ui.md` §5.2).

### 3.3. Мудборд и style tile

```
A design style tile (not a UI screenshot): a flat board showing, arranged in a grid on a neutral
background —
  a row of 6 colour swatches with hex labels: {перечислить},
  three type specimens in {гарнитура}: 28px heading, 16px body, 12px caption, with the words spelled
    exactly as: "{Заголовок}", "{Строка основного текста}", "{Подпись}",
  three UI atoms: a 32px primary button, a 32px input field, a status badge,
  a texture or pattern sample expressing {характер}.
No device mockups, no screens, no people, no gradients.
Aspect ratio 4:3.
```

Смысл шага — зафиксировать направление до того, как начнётся вёрстка. Процесс и 14 полей цифровой плитки —
`../11-styles-trends/02-style-tiles-and-character-knobs.md` §2.

### 3.4. Кодогенерация страницы с токенами

Шесть блоков плюс одно жёсткое ограничение.

```
ЗАДАЧА
Собери экран «{название}» для {тип продукта}. Фреймворк {React + Tailwind v4}, компоненты {shadcn/ui}.

КОНТЕКСТ (прочитай прежде, чем писать код)
1. design-system/DESIGN.md — характер продукта, палитра, типографика, запреты.
2. design-system/tokens.css — все доступные переменные. Другие значения запрещены.
3. design-system/guidelines/composition/layout.md — каркас и ширины.
4. design-system/guidelines/components/overview.md — каталог компонентов.
5. design-system/starter/{ближайший экран}.tsx — эталон структуры. Следуй ему.

КАРКАС (числа обязательны)
- Сайдбар {240} px, свёрнутый {48}. Шапка приложения {48}. Поля контента {24} (32 от 1440, 16 до 640).
- Контентной области оставлять не меньше {640} px. Панелей не больше трёх.
- Шапка страницы не выше {120} px: крошки {20}, заголовок {20} px, действия справа, описание {640}.
- Тулбар списка {48}. Строка таблицы {36}. Пагинация {32}, не прилипает.
- Абзац max-width {640}. Форма max-width {560}. Карточки: repeat(auto-fill, minmax(280px, 1fr)), gap {16}.

СОДЕРЖИМОЕ
- Сущность: {заказ}. Поля: {номер, клиент, дата, сумма, статус}.
- Реальные значения в примерах, не lorem ipsum; русские строки, длина как в проде.
- Первичное действие одно: «{Новый заказ}», в правом верху шапки страницы.
- Состояния: пустое ({текст и одно действие}), загрузка ({скелетон строк}), ошибка ({текст и повтор}).

КОМПОНЕНТЫ
Используй только из каталога. Если нужного компонента нет — скажи об этом, не изобретай.
Варианты кнопки: только {primary | neutral | subtle}. Одна primary на видимую секцию.

ОГРАНИЧЕНИЕ (жёсткое)
Все цвета, отступы, радиусы, кегли, тени и длительности — только через var(--*) из tokens.css.
Ни одного литерала: ни hex, ни rgb(), ни числовых утилит Tailwind вида bg-zinc-200 или text-slate-600,
ни произвольных значений в квадратных скобках. Новые токены не создавать.

ЗАПРЕТЫ
{вставить блок из §1.4}

РУССКИЙ ИНТЕРФЕЙС
Подписи в 1,45 раза длиннее английских: пункт меню {180}, кнопка {140}, заголовок колонки {120}.
Sentence case, «ёлочки», длинное тире, неразрывные пробелы, формат 1 234 567,89 ₽,
font-variant-numeric: tabular-nums во всех числовых колонках, lang="ru".

ВЫВОД
Один файл компонента и, если нужно, файл с данными-заглушками. Ничего больше.
Не объясняй код. Не добавляй комментариев о том, что ты сделал.
```

Числа каркаса взяты из `../05-layout-grid/06-ai-errors-and-checks.md` §5; там же клиентский вариант.

### 3.5. Критика скриншота моделью

Протокол из двух вызовов (обоснование — `03-research-2024-2026.md` §6.3). Рубрика из десяти измерений и
общий промт — у агента I (`../13-evaluation-checklists/02-rubrics-and-vlm-critic.md` §4.5–§4.6); здесь —
специализация под **сгенерированный** экран: добавлен проход по маркерам генерации и машинный отчёт с
измеренными порогами.

**Вызов 1: маркеры генерации и рубрика**

```
Ты проверяешь экран, собранный генеративной системой. На вход — скриншот и машинный отчёт измерений.

ВХОД
  Скриншот: {изображение}
  Машинный отчёт (посчитан, не пересчитывай и не оспаривай):
  {вставить JSON из measure_ui.py: font_sizes_distinct, font_weights_distinct, radius_top,
   radius_distinct, box_shadow_distinct, cards_with_shadow_pct, button_height_top, sidebar_w,
   header_h, spacing_mult4_pct, z_index_max, targets_under_24_pct, backdrop_filter_used,
   text_secondary.wcag, border_primary.wcag}
  Пресет: {плотная админка}: база 14, контрол 32, строка 36, радиус 6, шкала {0,2,4,8,12,16,24,32,48}.

ЗАДАЧА 1 — маркеры генерации
  Для каждого маркера ответь present: true|false и, если true, назови место словами.
  Список:
   1. тень у карточек (порог: доля карточек с тенью > 20 %)
   2. более двух элементов со стеклом
   3. градиент как фон, заливка или граница
   4. три одинаковые карточки в ряд
   5. центрированный текстовый блок вне пустого состояния, диалога и карточки входа
   6. эмодзи вместо иконки
   7. кегль крупнее 32 px на экране приложения
   8. кнопка-пилюля в рабочем интерфейсе
   9. иконки разной толщины штриха или из разных наборов
  10. градиентный кружок с буквой вместо аватара
  11. повторяющийся блок KPI, не связанный с задачей экрана
  12. карточка, которая ничего не делает (нет действия и нет данных)

ЗАДАЧА 2 — рубрика
  Оцени 0–5 по десяти измерениям: hierarchy, consistency, spacing, color, typography, alignment,
  states, density_fit, distinctiveness, contrast. Якоря — в приложенной рубрике.

ПРАВИЛА
  1. Только то, что видно в кадре.
  2. Замечание без указания конкретного элемента не пишется.
  3. Регион называй словами, не координатами.
  4. Числа из отчёта не оспаривай; если твоя оценка противоречит отчёту, побеждает отчёт.
  5. Каждое замечание из трёх частей: каким должен быть результат, в чём разрыв, что сделать.
  6. Не больше семи замечаний. Больше — признак угадывания.
  7. Назови минимум две сильные стороны.
  8. Только JSON по схеме. Ничего до и после.
```

Схема ответа:

```json
{
  "screen": "orders-list",
  "preset": "dense-admin",
  "generation_markers": [
    {"id": 1, "name": "тень у карточек", "present": true,
     "evidence": "четыре KPI-карточки в верхнем ряду, у всех мягкая тень",
     "metric": "cards_with_shadow_pct = 100, порог 20"},
    {"id": 3, "name": "градиент", "present": true,
     "evidence": "кнопка «Новый заказ» в правом верху залита градиентом",
     "metric": null},
    {"id": 6, "name": "эмодзи вместо иконки", "present": true,
     "evidence": "пункты сайдбара начинаются с эмодзи", "metric": null}
  ],
  "markers_present_count": 3,
  "scores": {
    "hierarchy": 3, "consistency": 3, "spacing": 4, "color": 2, "typography": 3,
    "alignment": 4, "states": 2, "density_fit": 2, "distinctiveness": 2, "contrast": 3
  },
  "below_threshold": ["color", "states", "density_fit", "distinctiveness"],
  "strengths": [
    "Единая левая вертикаль: заголовок, тулбар и таблица начинаются от одного края.",
    "Все отступы принадлежат шкале, дробных значений нет."
  ],
  "findings": [
    {"dimension": "density_fit", "severity": "serious",
     "region": "весь экран: KPI-карточки и заголовок страницы",
     "expected": "Плотная админка: заголовок страницы 20 px, карточка padding 16, кнопка 32.",
     "gap": "Заголовок 30 px, padding карточек 24, кнопка 40 — масштаб маркетинговой страницы.",
     "fix": "Перевести на роли type.page-title, space.inset.card и size.control.md из токенов."},
    {"dimension": "color", "severity": "blocker",
     "region": "подписи под метриками в KPI-карточках",
     "expected": "Вторичный текст не ниже 4,5:1 к фону.",
     "gap": "Измерено 2,46:1.",
     "fix": "Заменить на --text-secondary (измеренный контраст 7,2:1)."}
  ],
  "unclear": ["Не видно состояния наведения на строку таблицы: нужен кадр в hover."]
}
```

**Вызов 2: локализация замечаний**

```
На вход — тот же скриншот, покрытый сеткой пронумерованных патчей, и список замечаний из первого вызова.
Для каждого замечания верни номера патчей, которые оно покрывает.
Ничего не добавляй и не переформулируй. Только JSON: [{"finding_index": 0, "patches": [12, 13, 20, 21]}].
```

Обоснование именно такого способа: IoU рамки 0,004 по голому скриншоту против **0,222 с пронумерованными
патчами**; сетка линий делает хуже (1,1e-5) `[S3]`. Разделение вызовов — потому что совмещение ухудшает
качество самих замечаний.

### 3.6. «Исправь по замечаниям»

Три обязательные части: что сделать, где, что не трогать.

```
ЗАДАЧА
Исправь экран {файл} по отчёту ниже. Больше ничего не меняй.

ОТЧЁТ ПРОВЕРОК (правило → найдено → порог → где)
  card-shadow          → 100 % карточек с тенью → ≤ 20 %   → components/KpiCard.tsx, класс на корне
  control-height       → 40 px                   → 32 px    → components/Button.tsx, вариант default
  type-scale           → заголовок 30 px         → 20 px    → app/orders/page.tsx, строка 24
  secondary-contrast   → 2,46:1                  → ≥ 4,5:1  → components/KpiCard.tsx, подпись
  token-literals       → 7 вхождений hex         → 0        → см. список ниже
  gradient             → 2 элемента              → 0        → components/Button.tsx, app/orders/page.tsx

ПРАВИЛА ПРАВКИ
  1. Правь только перечисленные места. Файлы, которых нет в отчёте, не открывай.
  2. Каждое значение бери из tokens.css через var(--*). Новых токенов не создавать.
  3. Не меняй структуру разметки, порядок элементов, тексты и логику.
  4. Не «улучшай» ничего сверх списка. Не добавляй комментариев.
  5. Если правило нельзя выполнить без структурного изменения — не делай изменение,
     верни пункт в списке «не выполнено» с одной строкой объяснения.

НЕ ТРОГАТЬ
  {перечислить: другие страницы, компоненты вне списка, конфиг, тесты}

ВЫВОД
  Диффы по файлам и список «не выполнено».
```

Обоснования: явное указание места — потому что локализация правки главное узкое место
(`03-…` §3.2); явное «не трогать» — потому что «ripple effect» описали 5 из 14 участников CHI '26;
«не улучшай сверх списка» — потому что модель при починке завышает значения ради доступности и ломает
консистентность `[S18]`.

### 3.7. Повторная проверка

После правки цикл повторяется с нуля: измерение → отчёт → критика. Отдельного промта не нужно.
**Новый отчёт сравнивается с предыдущим**: если появились нарушения, которых не было, правка внесла
регрессию — откатить и переформулировать пункт. Для DESIGN.md это делает `npx @google/design.md diff`.

---

## 4. Рубрика и её место

### 4.1. Откуда что берётся

| Уровень | Что | Источник |
|---|---|---|
| **Числа** | контраст, кратность, высоты, радиусы, число кеглей и теней, цели нажатия | `measure_ui.py` + `ui_audit.py` + `color.py` — **считается кодом** |
| **Маркеры генерации** | 12 пунктов §3.5, 34 маркера у G, 138 пунктов каталогов | часть скриптом, часть моделью |
| **Рубрика 0–5** | десять измерений с якорями | `../13-evaluation-checklists/02` §1 |
| **Полнота критики** | пять тем UICrit: layout, contrast, buttons, learnability, readability | `03-…` §2.2 |
| **Вкус и направление** | соответствие характеру, уместность приёма | человек |

### 4.2. Почему рубрик три, а не одна

- **Десять измерений агента I** — для приёмки любого экрана; проходной уровень 3, по контрасту 4.
- **Двенадцать индикаторов AesEval-Bench** (layout: balance, layering, whitespace, alignment; color:
  harmony, contrast, appeal, psychology; font: legibility, hierarchy; graphics: quality, relevance) — для
  сравнения вариантов между собой: они спроектированы под бинарные вопросы «есть ли дефект», что даёт
  измеримую точность.
- **Пять измерений GEBench** (GOAL, LOGIC, CONS, UI, QUAL, шкала 0–5) — для **последовательностей** кадров
  и для оценки картинок, а не свёрстанных экранов.

Смешивать их в одном вызове не надо: каждая отвечает на свой вопрос.

### 4.3. Надёжность

- Судья без рубрики ≈ монетка (51,58 %).
- Судья с рубрикой и описанными критериями сходится с экспертами: Пирсон 0,9892 при трёх судьях и трёх
  прогонах.
- Согласие самих экспертов между собой — Fleiss' Kappa 0,29–0,31. **Выше этого потолка не прыгнет никто.**
- Для скрининга хватает одного прогона; для приёмки нужен консенсус трёх прогонов или человек
  (`../13-evaluation-checklists/02` §4.7).

---

## 5. Цикл

### 5.1. Схема

```
  бриф (§1.2)
      │  → семь ручек характера → пресет
      ▼
  tokens.json (DTCG) ──► tokens.css + theme.css ──► DESIGN.md ──► guidelines/ ──► starter/
      │                         │                      │
      │                    tz check                 design.md lint
      │                    контрасты                 (11 правил)
      ▼
  КАРКАС КОДОМ (промт §3.4)
      │   только var(--*), числа каркаса в промте
      ▼
  СКРИНШОТ  ◄── measure_ui.py (JSON + PNG)
      │
      ├── (опционально) IMG2IMG поверх скриншота для направления стиля  ──► сверка палитры
      │
      ▼
  МАШИННЫЙ ОТЧЁТ: ui_audit.py + пять грепов + color.py
      │
      ▼
  КРИТИКА (промт §3.5, два вызова)
      │
      ▼
  ПРАВКА (промт §3.6): только по списку, только в токенах
      │
      ▼
  ПОВТОРНОЕ ИЗМЕРЕНИЕ + diff отчётов
      │
      └── регрессия? откат пункта. нарушений нет? приёмка человеком.
```

Ключевое правило, унаследованное от папки 09: **обратная стрелка ведёт в токены, а не в компоненты.**
Правка «кнопка слишком высокая» вносится в `size.control.md`, а не в CSS кнопки.

### 5.2. Почему цикл, а не лучший промт

Три независимых основания:
1. **Самокритика ненадёжна.** Self-revision помогает сильным моделям и обрушивает слабые
   (39,7 → 30,1 и 46,7 → 12,3) `[S21]`.
2. **Модель не видит дефект.** Точность самостоятельного обнаружения 0,2714 `[S4]`.
3. **Промт не накапливается.** «It is not reproducible, it gives variance not direction, and it does not
   compound» `[S11]`.

Отчёт проверок даёт модели то, чего нет ни в промте, ни в самокритике: **измеримую цель**.

### 5.3. Где в цикле картинка

Картинка полезна ровно в двух местах и вредна в остальных:

| Место | Роль | Почему |
|---|---|---|
| **До каркаса** | мудборд, style tile — выбрать направление | дешевле, чем верстать варианты |
| **После каркаса, img2img** | проверить, как выбранное направление ложится на реальную геометрию | геометрия задана кодом, модель отвечает только за поверхность |
| ~~Вместо макета~~ | — | «visual over-optimism»: галлюцинированные виджеты при высоком визуальном качестве `[S1]` |
| ~~Как серия экранов~~ | — | multi-step проваливается, ошибка накапливается `[S1]` |

### 5.4. Что автоматизируется

| Шаг | Автоматически | Человек |
|---|---|---|
| бриф → ручки | частично (квиз) | выбор стиля и характера |
| ручки → токены | **полностью** (генератор) | — |
| токены → CSS, DESIGN.md, guidelines | **полностью** | вычитка прозы один раз |
| starter | нет | **собирается и принимается человеком** |
| каркас кодом | **полностью** | — |
| измерение | **полностью** | — |
| машинный отчёт | **полностью** | — |
| критика по рубрике | **полностью** (скрининг) | приёмка при спорных баллах |
| локализация замечаний | **полностью** (патчи) | — |
| правка по списку | **полностью** | — |
| решение «достаточно» | нет | **человек** |
| вкус, уместность, фирменный приём | нет | **человек** |

Ориентир из `[V13]`: **проверка занимает больше времени, чем генерация.** Автоматизация нужна именно
проверке, а не генерации: там она окупается.

### 5.5. Что остаётся человеку навсегда

1. **Выбор направления.** Никакая рубрика не скажет, должен ли продукт быть строгим или тёплым.
2. **Решение о конфликте правил.** Известная слабость LLM — «неумение расставить приоритет, когда
   гайдлайны конфликтуют» `[S3]`.
3. **Один-два фирменных приёма.** Отличие строится осознанно (`../11-styles-trends/03` §5.2), а не
   выбирается из распределения.
4. **Приёмка.** Согласие экспертов Kappa 0,29–0,31: спорные случаи решает человек, а не третий прогон.
5. **Решение «хватит».** Цикл сходится к нулю нарушений, но не к «хорошо».

---

## Частые ошибки

1. **Оставить поле брифа пустым.** Пропуск — это решение, отданное дефолту модели; линтер DESIGN.md
   говорит это прямым текстом.
2. **Писать бриф прилагательными.** «Современный, чистый, удобный» не несёт различающего сигнала.
3. **Формулировать правило как рекомендацию.** Мягкие выполняются с recall 70,4 % против 92,3 %.
4. **Один длинный файл инструкций.** «Multiple short guidelines files are better than a few large files».
5. **Описывать компонент прозой вместо дерева решений.** Дерево снимает выбор, проза его оставляет.
6. **Забыть состояния в брифе.** Interactivity и state — значимые семантики генеративного контекста.
7. **Не давать эталонного экрана.** Стартовое приложение переносит структуру надёжнее любого описания.
8. **Класть полный JSON токенов в промт картинки.** Нужна карточка стиля на 10–15 строк.
9. **Просить модель найти проблемы.** Точность 0,2714.
10. **Объединять критику и локализацию в один вызов.** Ухудшает критику.
11. **Просить координаты вместо номеров патчей.** 0,186 против 0,222, и хуже по форме ответа.
12. **Давать скриншот без машинного отчёта.** Метаданные сильнее всего помогают локализации.
13. **Не указывать, что не трогать.** «Ripple effect».
14. **Разрешать «заодно улучшить».** Модель завысит значения ради доступности и сломает согласованность.
15. **Править визуал в компоненте, а не в токене.** Через три итерации набор и интерфейс расходятся.
16. **Считать чистый отчёт приёмкой.** Ноль нарушений — это не «хорошо», это «не плохо».
17. **Строить цикл на самокритике модели.**
18. **Не сравнивать отчёты до и после.** Правка вносит регрессию, её видно только диффом.

---

## Чек-лист

**Бриф**
1. Заполнены все четыре уровня (Product, Design System, Feature, Component)?
2. Все семь ручек характера имеют значение?
3. Состояния (default, hover, selected, disabled, loading, error, empty) перечислены?
4. Список запретов есть и содержит числа, а не пожелания?
5. Указана локаль и следствия для ширин (RU в 1,45 раза длиннее)?

**Пакет инструкций**
6. Дерево `guidelines/` разбито на короткие файлы, верхний только маршрутизирует?
7. Есть блок Product character с числами (плотность, стратегия поверхностей, доля нейтрали, радиусы,
   модель глубины)?
8. Есть Reading order с пометкой «MUST READ before writing any code»?
9. Есть Workflows: перед компонентом, перед иконкой, при сборке раскладки?
10. Жёсткие инварианты помечены `IMPORTANT:`?
11. Для каждого повторяющегося решения написано дерево (фон, текст, граница, иконка, вариант кнопки,
    тип поля, обратная связь, уровень навигации, роль текста)?
12. Есть пары CORRECT / WRONG, по одной ошибке на пару?
13. У цветов проставлена частотность (Dominant / Sparse / Internal)?
14. Есть явный список несуществующих значений («valid variants are … — nothing else»)?
15. Есть раздел Do's and Don'ts, и он последний?
16. `DESIGN.md` проходит `lint` без ошибок и без предупреждений `missing-primary` и `missing-typography`?
17. Есть `starter/` из трёх собранных экранов, принятых по чек-листу?
18. Прописано правило верифицируемости: не использовать то, чего нет в источниках?

**Промты**
19. Промт картинки содержит все десять блоков и список запретов?
20. Промт кодогенерации содержит жёсткое ограничение «только `var(--*)`, никаких литералов»?
21. Промт кодогенерации ссылается на эталонный экран?
22. Промт критики получает и скриншот, и машинный отчёт?
23. Локализация вынесена во второй вызов с пронумерованными патчами?
24. Промт правки содержит «где» и «что не трогать»?

**Цикл**
25. Правки вносятся в токены, а не в компоненты?
26. После правки прогоняется повторное измерение?
27. Отчёты до и после сравниваются на регрессию?
28. Решение «достаточно» принимает человек?

---

## Открытые вопросы и противоречия

1. **Эффект карточки стиля не измерен.** Эксперимент «один экран, три условия (без брифа / урезанная
   карточка / полная), десять повторов, расхождение с токенами» предложен агентом F и остаётся
   невыполненным; мой эксперимент (`02-…` §5) его не заменяет, потому что условия A и B написаны мной.
2. **Число девяти деревьев решений взято из примера Figma Make**, а не выведено из данных. Сколько их
   нужно на самом деле — неизвестно.
3. **DESIGN.md в статусе alpha.** «Expect changes to the format as it matures». Привязываться к нему как
   к стабильному формату нельзя; источником истины остаётся `tokens.json` в DTCG.
4. **Неизвестно, читает ли модель весь пакет.** Figma Make строит инструкции «с оглядкой на окно
   контекста», но какая доля файлов реально попадает в контекст при генерации — из документации не
   следует. Проверяемая гипотеза: одинаковый экран с полным пакетом и с усечённым до `overview.md`
   плюс токены.
5. **Противоречие по дефолту shadcn.** Источник `[S11]` описывает нетронутую рампу `zinc` и фиолетовый
   `primary`; агент G, сверившись с документацией shadcn, пишет, что дефолт — **нулевая хрома и радиус
   10 px**, а не zinc и 6–8 (`../11-styles-trends/README.md`). Моё измерение десяти приложений даёт
   доминирующий радиус 12 и фиолетовый только на 3 страницах из 10. Наиболее вероятное объяснение:
   `[S11]` описывает не дефолт библиотеки, а то, что генерировали инструменты в 2024–2025.
   **Опираться следует на документацию shadcn и на измерение, а не на `[S11]`.**
6. **Порог «не больше семи замечаний» взят по аналогии** с наблюдением, что многословность коррелирует с
   галлюцинациями (45 комментариев при оценке 0,24). Точного порога нет.
7. **Не проверено, помогает ли машинный отчёт в промте критики именно VLM-модели.** Абляция
   AesEval-Bench показала пользу метаданных для локализации на их формате JSON; переносится ли это на
   выгрузку `measure_ui.py`, не измерялось.
8. **Двенадцать маркеров генерации в §3.5 — сокращение из 34 маркеров агента G и 138 пунктов каталогов.**
   Критерий сокращения — измеримость и частота по моим данным, а не полнота.
9. **Русский интерфейс в промтах учтён коэффициентом 1,45 из измерений агента B**, но влияние языка
   промта (русский против английского) на результат генерации не проверялось ни здесь, ни в литературе.
10. **Формат «пронумерованные патчи» проверен на мобильных экранах RICO** (UICrit), а не на десктопных
    1440 × 900 с плотной таблицей. Оптимальный размер патча неизвестен.

---

## Источники

- `[S3]` Peitong Duan и др. **UICrit.** arXiv:2407.08850v3, UIST 2024. — протокол критики: два вызова,
  пронумерованные патчи (IoU 0,004 → 0,222), few-shot по близости (+55 %), 13,1 % валидных zero-shot.
- `[S4]` Jingyu Xiao и др. **DesignBench.** arXiv:2506.06251v1. — «explicitly stating the problems allows
  models to focus on targeted solutions»; давать место правки; дробить макет и правки.
- `[S11]` ux-skill. **Why AI-generated apps look the same.** — четыре механизма сходимости, семь осей
  брифа, почему промт не лечит. `[мнение]`, частично опровергнуто измерением (см. «Открытые вопросы» п. 5).
- `[S13]` Vercel. **v0 Docs: Design Systems 2.0.** https://v0.app/docs/design-systems-2 — скилл как
  адаптер, `v0.json`, `starter`, правило верифицируемости.
- `[S14]` Lovable. **Prompting best practices.** https://docs.lovable.dev/prompting/prompting-one —
  «say what to change and what to leave alone», стиль в project knowledge, атомарный словарь.
- `[S15]` Figma. **Write design system guidelines for Make kits.**
  https://developers.figma.com/docs/code/write-design-system-guidelines/ — структура `guidelines/`,
  Product character, Reading order, Workflows, `IMPORTANT:`, деревья решений, CORRECT/WRONG, Frequency.
- `[S16]` Google Labs. **DESIGN.md.** https://github.com/google-labs-code/design.md — два слоя,
  канонический порядок секций с Do's and Don'ts, 11 правил линтера, экспорт в DTCG, `spec` для инъекции
  в промт.
- `[S18]` Mingyue Yuan и др. **DesignRepair.** arXiv:2411.01606v2 — жёсткие и мягкие ограничения
  (70,4 % против 92,3 %), завышение значений при починке.
- `[S19]` Seokhyeon Park и др. **Bridging Gulfs in UI Generation through Semantic Guidance.**
  arXiv:2601.19171v2, CHI '26 — четыре уровня семантик, p = 0,002, r = 0,87, «ripple effect».
- `[S21]` Chenglei Si и др. **Design2Code.** arXiv:2403.03163v3 — опасность self-revision.
- `[S22]` Anthropic. Скилл `frontend-design`, кэш `../99-raw/cache/anthropic_frontend-design_skill.md` —
  двухпроходный процесс, ревью плана против брифа, «spend your boldness in one place».
- `[V13]` Brad Frost. `../91-videos/digests/13-brad-frost-is-atomic-design-dead.md` — «проверка занимает
  больше времени, чем генерация».

Внутренние источники значений и смежные файлы: `../09-design-tokens/04-reference-token-schema.md` и
`05-anti-patterns-and-pipeline.md` §4–§5; `../11-styles-trends/01-style-dictionary-for-quiz.md` (квиз),
`02-style-tiles-and-character-knobs.md` §2, §3, §5; `../13-evaluation-checklists/01-visual-qa-checklist.md`,
`02-rubrics-and-vlm-critic.md` §1, §4, `03-automated-checks.md`; `../05-layout-grid/06-ai-errors-and-checks.md`
§5; `../02-typography/06-localization-and-ai-errors.md` §1, §3; `../../../scripts/ui/measure_ui.py`,
`build_reference_tokens.py`, `color.py`, `ui_audit.py`.
