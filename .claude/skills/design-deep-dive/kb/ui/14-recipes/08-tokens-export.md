# Рецепт 08. Выпуск токенов: DTCG → CSS-переменные → Tailwind

Волна 3 · агент I · 22 сентября 2026 · собрано из `09-design-tokens/`, внешние источники в §Источники

Вход: значения из рецептов 01–05. Выход: `tokens.json` (DTCG 2025.10), `tokens.css`, `theme.css`, отчёт
проверок. Время: 20 минут, если значения уже выбраны.

---

## Шаг 1. Взять стабильную версию стандарта

**Design Tokens Format Module 2025.10**, Final Community Group Report от 28.10.2025: «This specification is
considered stable». `$schema` — `https://www.designtokens.org/schemas/2025.10/format.json`.

`https://tr.designtokens.org/format/` — **не она**: там редакторский черновик с пометкой «⚠️ Do not attempt
to implement this version… do not reference this version as authoritative».

## Шаг 2. Собрать файл по правилам формата

| Правило | Пример |
|---|---|
| Токен — объект с `$value`; группа — объект без него. Узел и с тем, и с другим — ошибка | |
| Имена не начинаются с `$`, не содержат `{`, `}`, `.`; регистрозависимы | `space.inset.card` |
| `$type` наследуется от ближайшей группы; инструменты **MUST NOT** угадывать тип по значению | `"$type": "dimension"` на группе |
| `dimension` — объект `{value, unit}`, единица `px` или `rem`, обязательна даже при нуле | `{"value": 16, "unit": "px"}` |
| `em` и `%` в `dimension` не поддерживаются: трекинг считается в px на каждую роль | −0.01em при 20 px = −0.2px |
| `lineHeight` внутри составного `typography` **MUST** быть числом (множителем кегля) | `1.428571`, в CSS `calc(20 / 14)` |
| `shadow` может быть объектом или массивом объектов | многослойная тень выражается штатно |
| Цвет — объект с `colorSpace` и `components`; `hex` только шестизначный, `alpha` отдельным полем | `{"colorSpace": "oklch", "components": [0.5465, 0.2455, 262.87], "hex": "#155dfc"}` |
| Ссылаться можно только на токен целиком, не на группу | `{color.accent.600}` |
| Токена прозрачности в стандарте нет — используется `number` | `"$type": "number", "$value": 0.32` |
| `$extensions` — ключи в обратной доменной нотации; инструменты **MUST** сохранять непонятные им расширения | `org.ui-research.llm` |

**Альфу нельзя навесить на алиас.** `{color.neutral.950}` с другой прозрачностью в DTCG не выражается:
`$value` — либо ссылка целиком, либо собственный объект. Цвета теней и скрим поэтому задаются собственными
значениями с `alpha`. Carbon обходит это нестандартным расширением `{value, alpha}`.

## Шаг 3. Записать правила применения внутрь токена

Формат скопирован с `org.primer.llm` у GitHub Primer — единственной системы, которая документирует себя для
языковых моделей прямо в токенах.

```json
"$extensions": {
  "org.ui-research.llm": {
    "usage": ["input-border", "checkbox-border", "select-border"],
    "rules": "MUST use for the border of any control that the user can type in or toggle. Gives 4.76:1 against bg.surface, which satisfies WCAG 1.4.11. Do NOT use for dividers: it is too strong and turns the layout into a grid.",
    "doNotUse": ["divider", "card-border"],
    "alternatives": ["border.subtle", "border.default"]
  }
}
```

**Грамматика `rules`: одно-два предложения, три уровня модальности.**

| Формула | Когда |
|---|---|
| `MUST use for…` | нарушение ломает доступность или контраст |
| `RECOMMENDED default for…` | выбор по умолчанию, отклонение требует причины |
| `Use for…` | обычное применение |
| `Do NOT use for… because…` | запрет с обоснованием в том же предложении |

Расширение ставится **только на семантические токены**, на примитивах его нет.

## Шаг 4. Контролируемый словарь меток `usage`

Свободные метки вырождаются: в эталонной схеме на 184 семантических токена пришлось **307 уникальных
меток** при 484 вхождениях, то есть большинство встречается один раз и ничего не даёт ни поиску, ни модели.
Словарь ниже — **84 метки в шести фасетах**. Правило: **каждому семантическому токену 1–3 метки, по одной
из первых трёх граней**; метки берутся только из списка, новые добавляются через изменение словаря.

**Грань 1. Слот (где применяется), 30 меток**

```
page · surface · card · panel · sidebar · rail · topbar · toolbar · page-header
table · table-header · table-row · table-cell · list-row · tree
form-field · button · icon-button · checkbox · switch · slider · select
menu · menu-item · tabs · breadcrumb · pagination
overlay · modal · drawer · popover · tooltip · toast · banner
empty-state · chart · code · avatar · badge · progress
```

**Грань 2. Роль (что именно красится или измеряется), 18 меток**

```
background · foreground · border · divider · icon · label · placeholder · value
heading · metric · link · ring · scrim · shadow · indicator · track · thumb · illustration
```

**Грань 3. Мера (для нецветовых токенов), 10 меток**

```
inset · stack · inline · gap · size · width · height · radius · elevation · duration
```

**Грань 4. Состояние (необязательно), 10 меток**

```
rest · hover · active · selected · focus · disabled · loading · invalid · readonly · dragging
```

**Грань 5. Вариант (необязательно), 9 меток**

```
primary · secondary · tertiary · ghost · solid · subtle · inverse · destructive · accent
```

**Грань 6. Семантика статуса (необязательно), 7 меток**

```
info · success · warning · danger · neutral · magic · chart-series
```

Примеры разметки:

| Токен | Метки |
|---|---|
| `color.border.strong` | `form-field` · `border` |
| `color.bg.component-hover` | `button` · `background` · `hover` |
| `color.danger.solid` | `button` · `background` · `destructive` · `danger` |
| `color.fg.tertiary` | `surface` · `placeholder` |
| `space.inset.card` | `card` · `inset` |
| `size.row.table` | `table-row` · `height` |
| `elevation.overlay` | `modal` · `shadow` |
| `motion.popup.enter` | `popover` · `duration` |
| `color.chart.1` | `chart` · `chart-series` |

Проверка словаря автоматическая: множество всех `usage` минус словарь должно быть пустым; число меток на
токен 1–3; у каждого семантического токена есть хотя бы одна метка грани 1 или 3.

## Шаг 5. Темы и режимы

Осей обычно четыре: **бренд × режим цвета × контраст × плотность**. Хранить надо **оси, а не их
произведение**: 5 + 2 + 2 + 3 = 12 наборов вместо 5 × 2 × 2 × 3 = 60.

Два способа:

1. **Внутри токена** — `$extensions.<ns>.modes.dark`. Так делают Primer (`org.primer.overrides`, шесть
   режимов, включая два под дальтонизм) и Carbon (`carbon.themes`, четыре темы).
2. **Resolver Module 2025.10** — отдельный файл `.resolver.json` с `sets`, `modifiers`, `resolutionOrder`.
   Модификатор должен иметь ≥ 2 контекста и **MUST NOT** ссылаться на другой модификатор.

Высокий контраст — **отдельный полный набор**, а не модификатор: так у Fluent (`highContrastColor` 15.9 КБ
отдельным файлом) и у Atlassian.

## Шаг 6. Компиляция в CSS

```css
:root {
  color-scheme: light dark;
  /* примитивы */
  --palette-accent-600: #155dfc;
  /* семантика */
  --accent-solid: var(--palette-accent-600);
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { /* … */ } }
:root[data-theme="dark"] { /* то же */ }
[data-density="compact"] { /* только семантика */ }
```

Три правила компиляции:

1. **Переменная-ссылка разрешается в точке объявления.** Переключатель темы вешается туда же, где объявлена
   семантика (`:root`). Тема на `<body>` при семантике на `:root` не сработает. Подтверждено документацией
   Tailwind и Terrazzo независимо.
2. **Блок режима содержит транзитивное замыкание** изменившихся токенов, включая алиасы второго порядка.
   Список вычисляется, а не пишется руками.
3. **Плотность переопределяет только семантику**, поэтому её можно включить на поддереве
   (`[data-density]` без `:root`).

## Шаг 7. Тема Tailwind v4

```css
@import "tailwindcss";
@import "./tokens.css";

@theme inline {
  --color-accent: var(--accent-solid);
  --spacing-md: var(--space-md);
  --radius-md: var(--corner-md);
  /* обнуление дефолтных пространств, чтобы в проекте не осталось двух шкал */
  --breakpoint-*: initial;
  --breakpoint-tablet: 640px;
  --breakpoint-desktop: 1024px;
  --breakpoint-wide: 1440px;
}
```

- **`@theme inline`, а не `@theme`.** Без `inline` Tailwind подставит в утилиту ссылку на переменную,
  вычисленную в месте объявления темы, и тёмная тема перестанет переключаться.
- **Пространства имён Tailwind нельзя занимать в обычном `:root`.** Поэтому семантические переменные в
  эталонной схеме названы `--fg-*` (а не `--text-*`), `--corner-*` (а не `--radius-*`), `--elevation-*`
  (а не `--shadow-*`), `--bp-*` (а не `--breakpoint-*`): иначе `--radius-md: var(--radius-md)` внутри
  `@theme inline` даёт самоссылку.
- **Мост к shadcn/ui — 19 строк**: `--color-primary: var(--accent-solid)`,
  `--color-input: var(--border-strong)` и так далее. Компоненты shadcn работают без правок, при этом их
  слабые дефолты контраста (`--input` 1.23:1) заменены на проверенные значения.

## Шаг 8. Инструменты

| Инструмент | Статус на сентябрь 2026 |
|---|---|
| **Terrazzo** | заявляет полную поддержку формата; `tz check` валидирует, `tz bundle` сворачивает резолвер |
| **Style Dictionary v4** | DTCG поддерживает, но **не 2025.10**: «the latest format 2025.10 does not have full support yet… work in progress in v5». Конвертер v3 → DTCG не переименовывает типы: `"$type": "size"` не станет `dimension` |
| **Figma Variables** | не DTCG: четыре типа (Color, Number, String, Boolean), лимит 5000 переменных на коллекцию, составных типов нет |
| **Penpot, Tokens Studio** | поддерживают арифметику в значениях (`{spacing.base} * 1.5`) — это расширение, за их пределами формула не переносится |
| Минимальный конвейер без Figma | `tokens.json` → Terrazzo или Style Dictionary → CSS. Ни плагинов, ни аккаунтов, ни облака |

---

## Выход

```
dist/
  tokens.json   — DTCG 2025.10, 289 токенов (104 примитива + 185 семантических)
  tokens.css    — :root + [data-theme] + [data-density] + @media reduced-motion
  theme.css     — @theme inline + мост к shadcn/ui
  report.txt    — 87 пар контраста, коридор APCA отключённого текста, ΔE палитры графиков в трёх симуляциях CVD, арифметика интерлиньяжа
```

Генератор: `python3 ../../scripts/ui/build_reference_tokens.py --out ./dist`.

---

## Проверки

**На сборке токенов:**

| Проверка | Чем | Что ловит |
|---|---|---|
| валидность формата | `npx tz check tokens.json` или `ajv validate` | строковые размеры, отсутствующий `$type`, узел-токен-и-группа |
| все ссылки резолвятся, нет циклов, глубина ≤ 3 | обход графа | опечатки, лишние уровни |
| каждый примитив использован семантикой | разность множеств | мёртвые примитивы |
| у каждого семантического токена есть `usage` и `rules` | подсчёт | недокументированные токены |
| метки `usage` из словаря, 1–3 на токен | разность множеств | вырождение словаря |
| контраст всех пар | `color.py` поверх набора | нарушения 1.4.3 и 1.4.11 |
| ΔE палитры графиков в трёх симуляциях CVD | свой скрипт | неразличимые серии |
| произведение кегля на отношение целое | свой скрипт | дробный интерлиньяж |

**На компонентах — пять грепов:**

```bash
grep -rnE '#[0-9a-fA-F]{3,8}\b|rgba?\(' src/components/          # 1. литералы цвета
grep -rnE '\b(bg|text|border|ring)-(slate|gray|zinc|blue|red)-[0-9]{2,3}\b' src/   # 2. числовые утилиты
grep -rnE 'var\(--(palette|scale|font-size|curve)' src/components/  # 3. примитивы в компонентах
grep -rnE 'z-index:\s*[0-9]+' src/ | grep -v 'var(--z-'          # 4. z-index вне шкалы
grep -rnoE '\b[0-9]+px' src/components/ | awk -F'[:p]' '{print $NF}' | sort -n | uniq -c   # 5. размеры
```

Пятый грет даёт не «пусто», а список для просмотра: 1px (границы), 2px (фокус), 6px и 10px (штатные
исключения) допустимы, 13px и 17px — нет.

**На готовом экране:** `ui_audit.py --tokens tokens.json` — проверка I6 «цвета, которых нет в наборе
токенов» плюс сверка шкал отступов, радиусов, кеглей, z-index и длительностей с набором.

**Линтеры.** `stylelint-declaration-strict-value` (rule id `scale-unlimited/declaration-strict-value`)
требует, чтобы значение было переменной или функцией, а не литералом. Дефолты плагина: `ignoreVariables: true`,
`ignoreFunctions: true`, `ignoreValues: null`; `expandShorthand` и `recurseLonghand` выключены.
`declaration-property-value-allowed-list` фиксирует допустимые значения по свойству; регулярка в нём
матчится **против целого значения декларации**, поэтому `"/^solid/"` не совпадёт с `"10px solid red"`, а
`"/\\bsolid\\b/"` совпадёт. Для Tailwind — `eslint-plugin-tailwindcss` с правилами
`no-arbitrary-value` (по умолчанию **выключено**, включать явно) и `no-custom-classname`.

---

## Типичные ошибки

1. **Ссылка на черновик вместо стабильной версии.**
2. **`"$value": "16px"` строкой.** Самая частая ошибка при генерации токенов: так выглядит большинство
   примеров в интернете, но они относятся к Style Dictionary v3.
3. **Потеря единицы при нуле.** `{"value": 0}` невалидно.
4. **Токен без `$type`** ни на себе, ни на предках; расчёт на то, что инструмент угадает тип.
5. **Изобретение типов**: `"$type": "spacing"`, `"size"`, `"opacity"`. Есть `dimension` и `number`.
6. **Тень строкой** вместо массива объектов; **цвет строкой** при `$type: color`.
7. **`lineHeight` размером** внутри составного `typography`.
8. **Смешение формата v3 и DTCG в одном файле**: `value` рядом с `$value`, `comment` рядом с `$description`.
9. **Жизненно важные значения в `$extensions`.** Инструмент обязан сохранить расширение, но не обязан его
   понять: тёмная тема, лежащая только в расширении, для чужого инструмента не существует.
10. **Значение в имени семантического токена** (`color.blue.primary`, `space-16`): при смене акцента или
    плотности имя становится ложью.
11. **Сокращения в путях токенов** (`bg`, `fg`, `bdr`). DTCG рекомендует `background`.
12. **Последовательная нумерация шкалы 1, 2, 3** без запаса на вставку. Шаг 100 или фиксированная семантика
    ступеней, как у Radix.
13. **Тема и режим в одной оси** (`brand-a-dark-compact`).
14. **Переключатель темы не на том элементе, где объявлена семантика.**
15. **`@theme` без `inline`.**
16. **Компонентный токен под один компонент.** Правило перехода — три и более компонента.
17. **Мёртвый токен** (ноль использований) — такой же дефект, как магическое значение.
18. **Магическое значение вне токенов.** Авито при смене бренда нашли нетокенизированный логотип более чем
    в **120 местах**.
19. **Изобретение параллельных имён**: `--text-color-main` рядом с существующим `--fg-primary`. Лечится
    подачей полного списка токенов в контекст и правилом «не создавать новых токенов без явной просьбы».
20. **Смена акцента без перепроверки контраста.**

---

## Ссылки на базу и источники

- Архитектура и именование: `../09-design-tokens/01-architecture-and-naming.md`
- DTCG и инструменты: `../09-design-tokens/02-dtcg-format-and-tooling.md`
- Темы и режимы: `../09-design-tokens/03-theming-and-modes.md`
- Эталонная схема 289 токенов, CSS, Tailwind, проверки: `../09-design-tokens/04-reference-token-schema.md`
- Антипаттерны, депрекация, конвейер, карточка стиля: `../09-design-tokens/05-anti-patterns-and-pipeline.md`
- Stylelint: `https://stylelint.io/user-guide/rules/declaration-property-value-allowed-list`
- Плагин строгих значений: `https://github.com/AndyOGo/stylelint-declaration-strict-value`
- ESLint для Tailwind: `https://github.com/francoismassart/eslint-plugin-tailwindcss`
