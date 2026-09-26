# Стандарт W3C DTCG и инструменты

Волна 2, агент F, 22 сентября 2026. Источников прочитано целиком: 38.

Формат токенов W3C Design Tokens Community Group по состоянию на сентябрь 2026: что стабильно, что в
черновике, какие типы есть и каких нет, и чем это собирать. Полный рабочий пример формата — в
`04-reference-token-schema.md`.

## Выжимка для агента

1. **Стабильная версия одна: Design Tokens Format Module 2025.10, Final Community Group Report от
   28.10.2025.** «This specification is considered stable.» Это не W3C Recommendation, а отчёт
   сообщества, но предназначенный для реализации. → §1 `[стандарт]`
2. **`https://tr.designtokens.org/format/` — это не она.** Там лежит редакторский черновик от 08.09.2026
   с пометкой «⚠️ Do not attempt to implement this version… do not reference this version as
   authoritative». Ссылаться надо на `https://www.designtokens.org/TR/2025.10/format/`. → §1
   `[стандарт]`
3. **`$schema`: `https://www.designtokens.org/schemas/2025.10/format.json`** (проверено, отдаёт 200). →
   §1 `[стандарт]`
4. **Токен — объект с `$value`; группа — объект без `$value`.** Объект и с тем и с другим — ошибка,
   инструменты **MUST** сообщать. → §2 `[стандарт]`
5. **Имена не начинаются с `$` и не содержат `{`, `}`, `.`** Имена регистрозависимы. → §2 `[стандарт]`
6. **`$type` наследуется от ближайшей родительской группы. Если не определён нигде — токен невалиден.
   Инструменты MUST NOT угадывать тип по значению.** → §3 `[стандарт]`
7. **Семь базовых типов:** `color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`,
   `number`. Семь составных: `strokeStyle`, `border`, `transition`, `shadow`, `gradient`, `typography`,
   плюс `color` как объект. → §3 `[стандарт]`
8. **`dimension` — объект `{value, unit}` с единицей `px` или `rem`.** Ни `em`, ни `%`, ни строк
   `"16px"`. Единица обязательна даже при нуле. → §3.2 `[стандарт]`
9. **Токена прозрачности в стандарте нет.** Для opacity используется `number`. Font style, percentage и
   ratio тоже пока не описаны. → §3.5 `[стандарт]`
10. **`lineHeight` внутри составного `typography` MUST быть `number`** и трактуется как множитель кегля.
    Абсолютный px-интерлиньяж туда не записывается (открытый Issue 102). → §3.4 `[стандарт]`
11. **`shadow` может быть объектом или массивом объектов** — многослойные тени выражаются штатно. →
    §3.4 `[стандарт]`
12. **`$extensions` — ключи в обратной доменной нотации** (`org.primer.llm`). Инструменты **MUST
    сохранять расширения, которых не понимают**, но не обязаны их понимать. → §2.3 `[стандарт]`
13. **`$deprecated` принимает `true`, строку-объяснение или `false`** (перебивает значение группы). →
    §2.2 `[стандарт]`
14. **Цветовой модуль: 14 пространств, включая `oklch`.** `hex` только шестизначный, `alpha` отдельным
    полем 0–1, ключевое слово `none` в компонентах. → §4 `[стандарт]`
15. **Resolver Module 2025.10 — отдельный файл `.resolver.json`** с `sets`, `modifiers`,
    `resolutionOrder`. Это стандартный ответ на комбинаторный взрыв тем. → §5 `[стандарт]`
16. **Style Dictionary v4 поддерживает DTCG, но не 2025.10.** Прямая цитата документации: «the latest
    format **2025.10 does not have full support yet**… work in progress in v5». → §6.1 `[система]`
17. **Terrazzo заявляет полную поддержку формата**, резолверы обещаны в 2.0. Команда `tz check`
    валидирует файл, `tz bundle` сворачивает резолвер в один JSON. → §6.2 `[система]`
18. **Конвертер Style Dictionary v3 → DTCG не переименовывает типы.** `"$type": "size"` не станет
    `dimension`: мигрировать типы придётся вручную. → §6.1 `[система]`
19. **Ссылаться можно только на токен целиком, не на группу.** «Referencing a non-value design token
    will cause unexpected results». → §2.4 `[система]`
20. **Style Dictionary делает глубокий merge всех файлов; структура папок на структуру объекта не
    влияет.** Разложить токены по файлам можно как угодно. → §6.1 `[система]`
21. **Figma Variables — не DTCG.** Четыре типа (Color, Number, String, Boolean), лимит 5000 переменных
    на коллекцию, число режимов зависит от тарифа. Составных типов нет: тень и типографика остаются
    стилями. → §6.4 `[система]`
22. **Арифметика в значениях токенов стандартом не предусмотрена.** Penpot её поддерживает как
    расширение (`{spacing.base} * 1.5`, 17 функций), Tokens Studio — тоже. За пределами этих
    инструментов формула не переносится. → §6.5 `[система]`
23. **`$themes.json` и `$metadata.json` — формат Tokens Studio, ставший де-факто стандартом** обмена
    наборами и темами; в спецификации его нет. → §6.5 `[система]`
24. **Минимальный конвейер без Figma: JSON → Terrazzo или Style Dictionary → CSS.** Ни плагинов, ни
    аккаунтов, ни облака. Для генеративной системы этого достаточно. → §7 `[мнение]`
25. **Две живые интерпретации `dimension` одновременно:** Primer пишет `{value, unit}` по спеке, Carbon
    пишет голое число плюс собственный конвертер. Читатель чужих токенов должен уметь оба. → §3.2
    `[спорно]`

---

## 1. Статус спецификации на сентябрь 2026

Два документа с одинаковым названием. Различать их обязательно.

| Документ | URL | Статус | Дата |
|---|---|---|---|
| **Design Tokens Format Module 2025.10** | `https://www.designtokens.org/TR/2025.10/format/` | **Final Community Group Report**, «This specification is considered stable. Further updates will be provided in superseding specifications» | 28.10.2025 |
| Тот же модуль, редакторский preview | `https://tr.designtokens.org/format/` | Draft Community Group Report, «This is a preview… ⚠️ **Do not attempt to implement this version**… do not reference this version as authoritative» | 08.09.2026 |
| Color Module 2025.10 | `https://tr.designtokens.org/color/` | модуль формата | 2025.10 |
| Resolver Module 2025.10 | `https://tr.designtokens.org/resolver/` | модуль формата | 2025.10 |

Редакторы: Louis Chenais, Kathleen McMahon, Drew Powers, Matthew Ström-Awn, Donna Vitan. Авторы: Daniel
Banks (Style Dictionary), Mike Kamminga, Ayesha Mazrana, James Nash, Adekunle Oduye, Kevin Powell.

Что это значит практически: **формат перестал быть движущейся мишенью в октябре 2025**. До этого
ссылаться на «DTCG» без версии было бессмысленно; теперь у стабильной версии есть номер, схема и
намерение авторов не ломать её.

Технические подробности:

- файл — JSON; MIME `application/design-tokens+json` (SHOULD), допускается `application/json`;
- расширения `.tokens` или `.tokens.json`;
- `$schema`: `https://www.designtokens.org/schemas/2025.10/format.json` (проверено: 200).

---

## 2. Базовые правила формата

### 2.1. Токен и группа

- **Токен** — объект, у которого есть `$value`. `$value` — зарезервированное слово; имя токена — ключ
  родительского объекта.
- **Группа** — объект без `$value`.
- Объект, у которого есть и `$value`, и дочерние токены, — **ошибка**; инструменты **MUST** сообщать о
  ней. (Carbon и Panda CSS такие узлы всё же используют, см. `01-architecture-and-naming.md` §2.10; в
  черновике 2026 для этого вводится зарезервированное имя `$root`.)
- Имена токенов и групп **MUST NOT** начинаться с `$` и **MUST NOT** содержать `{`, `}`, `.`.
- Имена регистрозависимы; инструменты **MAY** предупреждать о токенах, различающихся только регистром.

### 2.2. Метаданные

| Свойство | Где | Значение |
|---|---|---|
| `$description` | токен, группа | plain string |
| `$type` | токен, группа | см. §3 |
| `$extensions` | токен, группа | объект с ключами в обратной доменной нотации |
| `$deprecated` | токен, группа | `true` \| строка-объяснение \| `false` (перебивает значение группы) |
| `$extends` | только группа | черновик 2026, см. §8 |

`$deprecated` со строкой — единственный штатный способ сказать «этот токен устарел, вот почему». В
живых системах его пока нет ни у кого из разобранных: Spectrum использует собственный `lifecycle`
с `deprecatedIn`, `deprecatedComment` и `replacedBy` (по uuid), Carbon — `carbon.layout.deprecated:
true`, Atlassian — собственные поля. Подробности — `05-anti-patterns-and-pipeline.md` §4.

### 2.3. `$extensions`

Ключи в обратной доменной нотации (`org.primer.llm`, `carbon.themes`, `com.figma`). Требование к
инструментам: **MUST сохранять расширения, которых не понимают**. Рекомендация спецификации:
расширения — только необязательные метаданные; понимание значения токена не должно от них зависеть.

Эта рекомендация нарушается в двух крупных системах сразу: у Carbon значение токена по теме лежит
**только** в `carbon.themes`, у Primer значения по режимам — **только** в `org.primer.overrides`. То
есть без понимания расширения тёмная тема просто не существует. Расплата: универсальный инструмент
соберёт из их файлов одну светлую тему и не сообщит об ошибке.

Вывод для своих токенов: **всё, без чего набор теряет смысл, должно лежать в `$value`**; в расширения
идут правила применения, метки для Figma, подсказки для модели. Если режимы всё же хранятся в
расширении (как в эталонной схеме, `04-reference-token-schema.md` §2.8) — это сознательный размен на
читаемость, и его надо документировать.

### 2.4. Алиасы

Синтаксис — `{group.token}` в `$value`. Правила:

- ссылаться можно **только на токен целиком**; «referencing a non-value design token will cause
  unexpected results»;
- ссылка подставляет весь `$value`, поэтому **альфу на алиас навесить нельзя** (см.
  `04-reference-token-schema.md` §2.7);
- в Penpot ссылки регистрозависимы;
- в резолвере **алиасы резолвятся только на последнем шаге**, после применения всех модификаторов.

---

## 3. Типы

### 3.1. Наследование `$type`

`$type` наследуется от ближайшей родительской группы. Если не определён ни на токене, ни на одном из
предков — **токен невалиден**. Отдельное требование: **инструменты MUST NOT угадывать тип по значению**.

Практика: ставить `$type` на самой высокой группе, где тип единственный. В эталонной схеме на 266
токенов `$type` встречается 19 раз.

### 3.2. Базовые типы

| `$type` | Значение | Пример |
|---|---|---|
| `color` | объект: `colorSpace` (обяз.), `components` (обяз.), `alpha` (0–1, по умолчанию 1), `hex` (6-значный fallback) | `{"colorSpace": "oklch", "components": [0.5465, 0.2455, 262.87], "hex": "#155dfc"}` |
| `dimension` | **объект `{value: number, unit: "px" \| "rem"}`**; единица обязательна даже при `value: 0` | `{"value": 16, "unit": "px"}` |
| `fontFamily` | строка или массив строк от предпочтительного к запасному | `["Inter", "ui-sans-serif", "sans-serif"]` |
| `fontWeight` | число 1–1000 **или** строковый алиас | `600` или `"semi-bold"` |
| `duration` | объект `{value, unit: "ms" \| "s"}` | `{"value": 150, "unit": "ms"}` |
| `cubicBezier` | массив из 4 чисел `[P1x, P1y, P2x, P2y]`; x в [0, 1], y любые | `[0.2, 0, 0, 1]` |
| `number` | JSON-число | `0.4`, `1.5`, `1300` |

Строковые алиасы `fontWeight`: 100 thin/hairline, 200 extra-light/ultra-light, 300 light,
400 normal/regular/book, 500 medium, 600 semi-bold/demi-bold, 700 bold, 800 extra-bold/ultra-bold,
900 black/heavy, 950 extra-black/ultra-black.

**Про `dimension` — главное расхождение практики со спецификацией.** Два живых прочтения одновременно:

```json5
// Primer — по спеке
{ "$type": "dimension", "$value": {"value": 3, "unit": "px"} }
```
```json
// Carbon — голое число плюс собственное расширение
{ "$type": "dimension", "$value": 2,
  "$extensions": {"carbon.layout": {"converter": "miniUnits"}} }
```

Конвертеры Carbon:

| converter | вход | формула | пример |
|---|---|---|---|
| `miniUnits` | число шагов сетки | `шаги × 8px ÷ 16 = rem` | `2` → `1rem` |
| `rem` | пиксели | `px ÷ 16 = rem` | `4` → `0.25rem` |
| без конвертера | строка с единицей | как есть | `"2vw"`, `"999999px"` |

То есть у Carbon в `$value` может лежать и число, и строка `"2vw"`, а `$type` в обоих случаях
`dimension`. Валидатор по схеме 2025.10 такой файл не примет. Для чтения чужих токенов это значит:
**проверяй фактическое содержимое `$value`, не полагайся на `$type`.**

### 3.3. Чего нельзя выразить в `dimension`

Единицы ограничены `px` и `rem`. Отсюда три следствия:

1. **Трекинг в `em` не выражается.** Нужно считать px на каждый кегль (см.
   `04-reference-token-schema.md` §2.4) либо выходить за стандарт.
2. **Проценты не выражаются.** `radius.tile` = 25 % у Atlassian и `border-radius: 50%` у аватаров
   придётся хранить как `number` со своей интерпретацией или как строку вне стандарта.
3. **Вьюпортные единицы не выражаются.** `fluid-spacing` Carbon (`2vw`, `5vw`, `10vw`) стандартом не
   покрывается вообще.

### 3.4. Составные типы

| `$type` | Поля |
|---|---|
| `strokeStyle` | строка `solid \| dashed \| dotted \| double \| groove \| ridge \| outset \| inset` **или** объект `{dashArray, lineCap: round \| butt \| square}` |
| `border` | `{color, width, style}` |
| `transition` | `{duration, delay, timingFunction}` |
| `shadow` | объект **или массив** объектов/ссылок; поля `color, offsetX, offsetY, blur, spread, inset?` |
| `gradient` | массив `{color, position 0–1}` |
| `typography` | `{fontFamily, fontSize, fontWeight, letterSpacing, lineHeight}` |

Два места, где составные типы важны на практике.

**`shadow` как массив** — единственный штатный способ записать многослойную тень. Все живые системы
многослойны: Atlassian две тени (`0px 1px 1px #1E1F2140, 0px 0px 1px #1E1F214F`), Radix 4–5 слоёв,
Mantine три, Untitled UI до трёх, Tailwind две. Если инструмент не умеет массив, тени придётся хранить
строкой вне стандарта.

**`typography.lineHeight` MUST быть `number`** и трактуется как множитель кегля. Это конфликтует с
практикой: 7 систем из 12 хранят абсолютный px-интерлиньяж (`02-typography/02-type-scale.md` §4.1) —
Radix `--line-height-1…9` = 16, 20, 24, 26, 28, 30, 36, 40, 60 px; Atlassian пишет shorthand
`normal 400 0.875rem/1.25rem`; Carbon и Spectrum тоже в абсолютных. Это открытый Issue 102 в
репозитории DTCG. Разбор выбора и способ подобрать отношения так, чтобы произведение было целым, —
`04-reference-token-schema.md` §2.5.

### 3.5. Чего в стандарте нет

Раздел «Additional types» перечисляет типы, которые пока не описаны:

- **font style** (normal / italic);
- **percentage и ratio** — в том числе **opacity**;
- **file** (ссылка на ассет: иконка, шрифт, иллюстрация).

Следствия: прозрачность хранится как `number` с собственным соглашением; `aspect-ratio` (`16 / 9` у
Tailwind) не выражается; ассеты в токенах не живут. Ещё один пример типа вне стандарта — `motion_path`
у Material: генератор токенов Material выдаёт для него `null`.

Нестандартные типы в живых системах, которые встретятся при чтении чужих файлов:

| Тип | Кто | Что это |
|---|---|---|
| `custom-string` | Primer | `boxShadow.thin/thick/thicker` = `inset 0 0 0 {borderWidth.*}` — граница тенью, «used instead of a border to prevent layout shift» |
| `alias` | Spectrum | токен-ссылка с `$ref` по uuid |
| `multiplier`, `font-size`, `alignment`, `angle` | Spectrum | типы через `$schema` на токен, а не `$type` |
| `motion_path` | Material | составная траектория из двух кривых Безье |

---

## 4. Цветовой модуль

Прочитан целиком (705 строк).

**Поддерживаемые `colorSpace`:** `srgb`, `srgb-linear`, `hsl`, `hwb`, `lab`, `lch`, `oklab`, **`oklch`**,
`display-p3`, `a98-rgb`, `prophoto-rgb`, `rec2020`, `xyz-d65`, `xyz-d50`.

Диапазоны: OKLCH — L [0, 1], C [0, ∞) (на практике ≤ 0.5), H [0, 360). HSL — H [0, 360), S [0, 100],
L [0, 100].

Правила:

- **`hex` — только шестизначный**, чтобы не конфликтовать с `alpha`;
- `alpha` — число 0–1, по умолчанию 1;
- ключевое слово **`none`** в `components` означает «компонент не применим» и отличается от 0 при
  интерполяции (важно для серых: hue у них неопределён).

Раздел 7 «Token naming» (non-normative) разобран в `01-architecture-and-naming.md` §2.3–§2.4: три
категории Base / Alias / Component, шаг 100 вместо 1, 2, 3, рекомендация писать `background`, а не `bg`.

---

## 5. Resolver Module: темы и режимы по стандарту

Отдельный модуль, решающий ровно задачу тем. Мотивация названа прямо: «alternate contexts are
susceptible to combinatorial explosion».

Файл `.resolver.json`, MIME `application/json`. Корневые поля:

| Поле | Обязательно | Что |
|---|---|---|
| `name` | нет | имя набора |
| `version` | **да**, значение `"2025.10"` | версия модуля |
| `description` | нет | — |
| `sets` | нет | коллекции токенов |
| `modifiers` | нет | оси с контекстами |
| `resolutionOrder` | **да** | порядок применения |
| `$schema` | нет | `https://www.designtokens.org/schemas/2025.10/resolver.json` |

Правила:

- **Set** — массив `sources` (инлайн-токены и/или `$ref` на файлы). Конфликт решается «побеждает
  последний в массиве».
- **Modifier** — то же плюс карта `contexts` (`light` / `dark` / `hc`). Modifier **SHOULD** иметь ≥ 2
  контекста (1 контекст = это set, инструменты SHOULD ругаться), **MUST NOT** иметь 0. Может иметь
  `default`.
- **Modifier MUST NOT ссылаться на другой modifier** — даже на другой контекст внутри себя.
- `resolutionOrder` — массив сетов и модификаторов; позднее перебивает раннее.
- Число возможных разрешений = произведение числа контекстов всех модификаторов.
- **Ортогональность** модификаторов — рекомендация: контексты должны трогать непересекающиеся токены.
  «Много сетов после модификаторов — запах непредсказуемой организации токенов».
- Порядок обработки строго: валидация входа → ordering → **алиасы резолвятся только на последнем
  шаге** → результат.
- Входы — объект «строка → строка»; **значения MUST быть строками**: `{"beta": true}` и `{"size": 100}`
  — ошибка. Ключи SHOULD быть регистронезависимы.
- Бандлинг в один файл: либо инлайнить ссылки, либо сложить файлы в `$defs`.

В благодарностях — команда Hyma (Tokens Studio): резолвер вырос из их формата `$themes.json`.

Полный рабочий листинг резолвера для эталонной схемы — `03-theming-and-modes.md` §2.3.

---

## 6. Инструменты

### 6.1. Style Dictionary (v4, v5 в работе)

Исторический формат v3: `value`, `type`, `comment`, `themeable`, `name`, `attributes`. **С версии 4 —
first-class поддержка DTCG** (`$value`, `$type`, `$description`).

Прямая цитата со страницы `/info/dtcg/`: «the latest format **2025.10 does not have full support yet**
in Style Dictionary. This is a work in progress in v5» (issue style-dictionary#1590).

Что важно знать:

- **Конвертер v3 → DTCG переименовывает `value`/`type`/`description` в `$value`/`$type`/`$description`
  и спускает `$type` с верхней общей группы на токены, но НЕ переименовывает сами типы**:
  `"$type": "size"` не станет `dimension`. Миграция типов — руками.
- Метаданные, которые SD дописывает каждому токену и которые видны формату и трансформу: `name`
  (ключ), `path` (массив пути), `original` (нетронутая копия), `filePath`, `isSource`.
- Источники: `source` (глоб) и `include` (подмешивается, но «не своё»); **глубокий merge всех файлов**,
  структура папок на структуру объекта не влияет.
- Поддерживаемые языки файлов: JSON, JSONC, JSON5, ES-модули, плюс кастомные парсеры.
- Ссылки `{size.font.medium}`; ссылаться на группу нельзя.

Предопределённые трансформы (список прочитан целиком, 739 строк документации) покрывают перевод px → rem,
имена в camelCase / kebab-case / snake_case / constant, цвет в hex / rgb / hsl / UIColor / ComposeColor,
`cubicBezier` в CSS-функцию, `shadow` в CSS-строку. Для веба нужны буквально три: `name/kebab`,
`size/pxToRem` (если нужен rem) и `color/css`.

### 6.2. Terrazzo (бывший Cobalt), 2.x

`npm i -D @terrazzo/cli`; `npx tz init` создаёт `terrazzo.config.ts` и может стартовать набор токенов
из популярной открытой дизайн-системы.

Команды: `init`, `build`, `lint`, **`check [file]`** (валидация файла на соответствие DTCG),
**`bundle [file] --output [file]`** (свернуть резолвер со ссылками на несколько файлов в один JSON).

Самоописание: «Terrazzo is the only tool that supports the full DTCG format (support for **resolvers and
other 2025.10 features coming in 2.0**)… But this will change as Style Dictionary is now following
Terrazzo's path in adopting DTCG».

Плагины: `@terrazzo/plugin-css`, `plugin-sass`, `plugin-js`, `plugin-css-in-js`.

Две вещи, которых нет у Style Dictionary:

**Темы как permutations резолвера в произвольные селекторы.** Конфиг задаёт массив `permutations`,
каждая со своим `input` (`{mode: "dark"}`, `{size: "desktop"}`) и функцией `prepare(contents)`,
оборачивающей переменные в любой селектор: `:root`, `[data-theme="dark"]`,
`@media (prefers-color-scheme: dark)`, `@media (width >= 600px)`. Выдачу можно ограничить:
`only: { modifiers: ["mode"], sets: ["foundation"] }`.

**Автоматическая раскладка цвета по гамутам:**

```css
:root { --color-blue-600: oklch(0.5618 0.1686 252.19); }            /* sRGB-safe */
@media (color-gamut: p3)      { :root { --color-blue-600: oklch(0.5618 0.2171 252.19); } }
@media (color-gamut: rec2020) { :root { --color-blue-600: oklch(0.5618 0.227  252.19); } }
```

Гамут-клэмпинг методом Color.js, тем же, что в CSS Color 4. Округление по умолчанию до 30 бит
(`colorDepth: 24 | 30 | 36 | 48 | "unlimited"`).

Там же документировано техническое правило, критичное для тем: **при смене режима все алиасы приходится
переобъявлять** — «if a CSS variable is an alias of another, when the base value changes, all aliases
must be redeclared otherwise they are referencing the old value in the parent scope». Подробный разбор —
`04-reference-token-schema.md` §5.2.

### 6.3. Выбор между ними

| Критерий | Style Dictionary v4 | Terrazzo 2.x |
|---|---|---|
| DTCG 2025.10 | частично, «work in progress in v5» | заявлена полная |
| Резолверы | нет | «coming in 2.0» |
| Валидация файла | через сторонний ajv | `tz check` |
| Гамуты цвета | нет | да, автоматически |
| Платформы | много (iOS, Android, Flutter, Compose) | веб (CSS, Sass, JS, CSS-in-JS) |
| Экосистема, примеры | больше | меньше |

Для генеративного конвейера, который выпускает только веб, **Terrazzo подходит лучше**: он валидирует
файл, понимает резолверы и сам разложит цвета по гамутам. Style Dictionary остаётся, если нужны
нативные платформы.

### 6.4. Figma Variables

Не DTCG, а собственная модель. Прочитана документация целиком.

- **Четыре типа переменных:** Color (сплошная заливка с опциональной прозрачностью), Number (целые и
  дробные до сотых, `12.75`), String (локализация, имена шрифтов, переключение вариантов компонентов в
  прототипе), Boolean (показ/скрытие слоёв).
- **Алиасинг:** переменная может ссылаться на другую переменную **того же типа**. Число можно подложить
  под свойство opacity цветовой переменной (значение < 0 даёт 0 %, > 100 даёт 100 %).
- **Коллекция** = набор переменных + набор режимов. **Лимит 5000 переменных на коллекцию.**
- **Режимы** — колонки значений внутри коллекции; левая колонка — режим по умолчанию. **Число режимов
  зависит от тарифа** (Education / Professional / Organization / Enterprise). На Enterprise можно задать
  режим по умолчанию для команды.
- Объект или страница наследуют режим по умолчанию, пока он не назначен явно; «Auto/Default»
  подхватывает новый дефолт, явно выбранный режим остаётся закреплённым.
- **Scoping** — ограничение, в каких полях переменная предлагается (у Primer это `org.primer.figma.scopes`).
- Отдельный механизм «Extend a variable collection» — для мультибрендовых систем.

**Чего в переменных нет:** составных типов. Тень, градиент и типографика остаются **стилями**. Отсюда
рабочий приём из доклада Config: отдельные переменные (цвет, число) идут в макет; составные
упаковываются в стиль; типографический токен = переменные на каждый параметр → внутрь стиля →
публикуется только стиль `[V16 A]`.

Ограничения, актуальные ещё в 2021 и частично сохранившиеся: экспорт типографики сырой, имя токена не
видно в инспекторе, нет функций lighten/darken `[V12]`.

### 6.5. Tokens Studio, Penpot, Panda, Open Props

**Tokens Studio** (плагин Figma). Его формат `$themes.json` + `$metadata.json` стал де-факто стандартом
обмена наборами и темами; в спецификации DTCG его нет. Документация `docs.tokens.studio` на момент
работы отдавала 404 на всех пробованных путях, поэтому структура восстановлена косвенно — по
документации Penpot, которая её воспроизводит. Команда Hyma (Tokens Studio) указана в благодарностях
Resolver Module: резолвер — это стандартизованная версия их модели.

**Penpot** — единственный открытый редактор, который заявляет прямое соответствие Design Tokens Format
Module: «Tokens can be exported from Penpot or integrated into other tools directly, without conversion».

- Ссылки `{dimension.small}`, **регистрозависимы**.
- **Математика в значениях:** операторы `+ - * / % ^`; функции `abs, ceil, floor, round, max, min, sqrt,
  pow, log, exp, sin, cos, tan, asin, acos, atan, atan2`. Правила: сложные формулы требуют пробелов
  вокруг операторов (`8 * 8`, не `8*8`); можно смешивать литералы и ссылки (`{spacing.base} * 1.5`);
  множитель можно вынести в токен (`{spacing.small} * {spacing.scale}`). **Стандартом это не
  предусмотрено** — за пределами Penpot и Tokens Studio формула не переносится.
- Типы Penpot: border radius, color, **dimension** (с подтипами применения: sizing, spacing, border
  radius, stroke width, X/Y position), opacity, rotation, sizing, spacing, stroke width, typography
  (композитный), font family/size/weight, letter spacing, line height, number.
- Токены биндятся к полям панели Design: ширина, высота, x, y, поворот, радиус, зазоры, паддинги,
  margin, min/max ширина-высота, трекинг, интерлиньяж, композитная типографика, толщина обводки, тень
  (x, y, blur, spread), размытие. **При привязанном токене drag-to-change у поля отключается** — прямая
  защита от «магических» значений.
- **Sets и Themes.** Set — файл или группа токенов. Theme — конфигурация активных сетов «для контекста:
  бренд, режим, точка касания». «Themes are multidimensional… you can have more than one theme active at
  the same time, combining the values of the active themes»; Theme Groups позволяют комбинировать «color
  themes, brands, platforms, density and more» без комбинаторного взрыва.
- Импорт/экспорт: один JSON (ключи первого уровня = имена сетов) либо папка файлов плюс `$themes.json`
  и `$metadata.json`.

**Panda CSS** разделяет `tokens` и `semanticTokens` — два уровня прямо в API. Категории:
`aspectRatios, borders, colors, durations, easings, fonts, fontSizes, fontWeights, letterSpacings,
lineHeights, radii, shadows, sizes, spacing, zIndex, gradients, assets, animations, blurs, opacity`.
Режим записан внутрь значения семантического токена:

```js
semanticTokens: { colors: {
  danger:  { value: { base: '{colors.red}',   _dark: '{colors.darkred}' } },
  primary: { DEFAULT: { value: '{colors.gray.100}' }, muted: { value: '{colors.gray.100}' } } } }
```

Это тот же приём, что `carbon.themes` и `org.primer.overrides`, только встроенный в инструмент. Формат
значения `{ value: … }` общий с Chakra v3 (один движок).

**Open Props** — набор готовых CSS-переменных-примитивов без компонентов и без семантики: sizes, colors,
gradients, shadows, easings, animations, borders, typography, aspect ratios, z-index, masks. Подключается
одним CSS-файлом. Ценен как пример «токены без системы»: даёт примитивный слой, не навязывая ролей.

---

## 7. Минимальный конвейер без Figma

Что реально нужно генеративному агенту:

```
tokens.json (DTCG 2025.10)
    │
    ├── npx tz check tokens.json          # валидация: типы, алиасы, дубли
    │
    ├── npx tz build                      # -> CSS-переменные (+ Sass, JS при нужде)
    │        terrazzo.config.ts:
    │          plugins: [css({ filename: "tokens.css" })]
    │          permutations: [{ input: {}, prepare: wrapIn(":root") },
    │                         { input: {mode: "dark"}, prepare: wrapIn('[data-theme="dark"]') }]
    │
    └── theme.css с @theme inline         # -> utility-классы Tailwind v4
```

Три файла, две команды, ни одного аккаунта. Альтернатива на Style Dictionary — та же схема с
`config.json` и форматом `css/variables`, плюс отдельная сборка на каждую тему.

Третий путь, которым пошла эталонная схема (`04-reference-token-schema.md`): **собственный генератор на
Python**, который держит дерево токенов и печатает JSON, CSS и Tailwind-тему из одного источника. Он
нужен там, где кроме компиляции нужны проверки — контраст каждой пары, ΔE палитры графиков, арифметика
интерлиньяжа, отсутствие мёртвых примитивов. Ни Style Dictionary, ни Terrazzo этого не делают.

Когда что брать:

| Ситуация | Инструмент |
|---|---|
| токены приходят из Figma через Tokens Studio | Style Dictionary (больше примеров) или Terrazzo |
| токены пишутся руками или генерируются кодом | Terrazzo (`tz check` ловит ошибки) |
| нужны нативные платформы | Style Dictionary |
| нужны проверки контраста и палитры на сборке | собственный скрипт поверх любого из них |
| нужен только CSS и ничего больше | собственный скрипт, 300 строк |

---

## 8. Что добавится в следующей редакции

Черновик от 08.09.2026 (реализовывать нельзя, знать полезно):

- **`$root`** — зарезервированное имя корневого токена группы: путь `color.accent.$root`. Легализует
  «двойные узлы», которые сейчас используют Carbon и Panda в обход стандарта.
- **`$extends`** — наследование группы от другой группы, синтаксический сахар над JSON Schema `$ref`,
  deep merge: локальное значение по тому же пути перебивает унаследованное, разные пути сосуществуют,
  замена целиком, а не по свойствам. Циклы запрещены.
- **`$ref`** (JSON Pointer по RFC 6901) — обязателен к поддержке наряду с `{group.token}`. Разница:
  `{token}` целится только в целые токены и всегда добавляет `/$value`; `$ref` — в любое место
  документа, включая `#/colors/blue/$value/components/0`. Экранирование `~` → `~0`, `/` → `~1`.
- Порядок разрешения в группе: локальные токены → `$root` → унаследованные через `$extends` → вложенные
  группы.

Что из этого меняет практику: `$extends` даёт способ выразить мультибренд без дублирования (базовая
группа + переопределения), `$ref` даёт точечные ссылки (например, «взять только светлоту этого цвета»).
До выхода стабильной редакции обе возможности недоступны.

---

## Частые ошибки

1. **Ссылка на черновик вместо стабильной версии.** `tr.designtokens.org/format/` — preview с явным
   запретом на реализацию.
2. **`"$value": "16px"` строкой.** Невалидно; правильно `{"value": 16, "unit": "px"}`.
3. **Потеря единицы при нуле.** `{"value": 0}` невалидно, нужно `{"value": 0, "unit": "px"}`.
4. **Токен без `$type`** ни на себе, ни на предках.
5. **Расчёт на то, что инструмент угадает тип.** Он не имеет права.
6. **Узел, который одновременно токен и группа.** До `$root` это ошибка формата.
7. **Точка в имени токена.** `font.size.2.5` — точка разделяет сегменты пути, имя её содержать не может.
8. **Ссылка на группу** вместо токена.
9. **`lineHeight` размером** внутри составного `typography`.
10. **`em` или `%` в `dimension`.**
11. **Хранение opacity как `dimension` или строки.** Тип — `number`.
12. **Жизненно важные значения в `$extensions`.** Инструмент обязан сохранить расширение, но не обязан
    его понять; тёмная тема, лежащая только в расширении, для чужого инструмента не существует.
13. **Арифметика в `$value` за пределами Penpot и Tokens Studio.** Формула не перенесётся.
14. **Ожидание, что Style Dictionary поймёт 2025.10 целиком.** Пока нет.
15. **Модификатор резолвера с одним контекстом.** Это set; инструменты SHOULD предупреждать.
16. **Модификатор, ссылающийся на другой модификатор.** MUST NOT.
17. **Нестроковые входы резолвера.** `{"size": 100}` — ошибка, нужно `{"size": "100"}`.
18. **Больше 5000 переменных в одной коллекции Figma.**

### Ошибки, типичные для нейросетей

- **Смешение формата Style Dictionary v3 и DTCG в одном файле.** `value` рядом с `$value`, `comment`
  рядом с `$description`. Оба выглядят правдоподобно, вместе — нет.
- **Строковые размеры.** `"$value": "1rem"` — самая частая ошибка при генерации токенов, потому что так
  выглядит большинство примеров в интернете (они относятся к v3).
- **Изобретение типов.** `"$type": "spacing"`, `"$type": "size"`, `"$type": "opacity"` — таких типов
  нет. Есть `dimension` и `number`.
- **Тень строкой.** `"$value": "0 1px 2px rgba(0,0,0,.08)"` вместо массива объектов.
- **Цвет строкой при `$type: color`.** В 2025.10 это объект, а не `"#155dfc"`.
- **Потеря `$type` при копировании токена между группами**, где тип поднят на группу.
- **Использование `$deprecated` как строки-даты.** Значение — `true`, `false` или объяснение.

---

## Чек-лист

1. В файле указан `$schema` стабильной версии 2025.10?
2. Файл проходит `npx tz check` или `ajv validate`?
3. Каждый токен — объект с `$value`; ни один объект не содержит одновременно `$value` и детей?
4. Ни одно имя не начинается с `$` и не содержит `{`, `}`, `.`?
5. У каждого токена есть `$type` — свой или от группы?
6. `$type` не продублирован там, где наследуется?
7. Все `dimension` — объекты `{value, unit}` с `px` или `rem`?
8. Все `duration` — объекты `{value, unit}` с `ms` или `s`?
9. Все `color` — объекты с `colorSpace` и `components`; `hex` шестизначный?
10. `lineHeight` в составных типографических токенах — число?
11. Прозрачность хранится как `number`?
12. Многослойные тени записаны массивом?
13. Все алиасы резолвятся (нет ссылок на несуществующие токены и на группы)?
14. Расширения именованы в обратной доменной нотации?
15. Без расширений набор остаётся осмысленным?
16. Если есть резолвер: `version` = `"2025.10"`, `resolutionOrder` заполнен, у каждого модификатора
    ≥ 2 контекста, ни один модификатор не ссылается на другой?
17. Входы резолвера — строки?
18. Устаревшие токены помечены `$deprecated` с объяснением и указанием замены?

---

## Открытые вопросы и противоречия

1. **Абсолютный интерлиньяж (Issue 102).** Спека требует `number`, семь систем из двенадцати хранят px.
   Решения в спецификации нет.
2. **Альфа на алиасе.** Нет способа взять цвет по ссылке и изменить прозрачность. Carbon и Radix решают
   по-разному, стандарт молчит.
3. **Проценты, `em`, вьюпортные единицы.** Не выражаются. `radius.tile` = 25 % (Atlassian),
   `fluid-spacing` = `2vw` (Carbon), трекинг в `em` (все) остаются вне стандарта.
4. **Opacity, font style, ratio, file.** Типов нет, раздел «Additional types» пуст.
5. **Два прочтения `dimension` в живых системах.** Primer по спеке, Carbon — нет. Оба валидируют свои
   файлы собственными средствами.
6. **Готовность инструментов.** Style Dictionary прямо пишет, что 2025.10 не поддержан полностью;
   Terrazzo заявляет поддержку, но резолверы «coming in 2.0». Проверить это запуском в рамках работы не
   удалось.
7. **Документация Tokens Studio недоступна.** `docs.tokens.studio` отдавал 404 на всех пробованных
   путях; структура `$themes.json` / `$metadata.json` восстановлена косвенно по документации Penpot.
   Значения могли устареть.
8. **Судьба `$extends` и `$ref`.** Черновик 2026 может измениться до релиза; опираться на них нельзя.
9. **Арифметика в токенах.** Нужна практически (Penpot, Tokens Studio, доклад Jan Six), но в стандарт
   не входит и, судя по отсутствию обсуждения в модулях, не планируется.

---

## Источники

1. `[S1a]` W3C DTCG. Design Tokens Format Module 2025.10. Final Community Group Report, 28.10.2025.
   https://www.designtokens.org/TR/2025.10/format/ — стабильная версия; прочитано целиком.
2. `[S1b]` Тот же модуль, редакторский preview 08.09.2026. https://tr.designtokens.org/format/ —
   1463 строки, прочитано целиком; `$root`, `$extends`, `$ref`.
3. `[S1c]` W3C DTCG. Color Module 2025.10. https://tr.designtokens.org/color/ — 705 строк, прочитано
   целиком; пространства, `hex`, `alpha`, `none`, раздел о наименовании.
4. `[S1d]` W3C DTCG. Resolver Module 2025.10. https://tr.designtokens.org/resolver/ — 449 строк,
   прочитано целиком; `sets`, `modifiers`, `resolutionOrder`, ортогональность.
5. `[S4a]` Style Dictionary. Design Tokens. https://styledictionary.com/info/tokens/ — метаданные
   токена, `source` и `include`, правила ссылок.
6. `[S4b]` Style Dictionary. DTCG. https://styledictionary.com/info/dtcg/ — статус поддержки 2025.10,
   поведение конвертера v3 → DTCG.
7. `[S4c]` Style Dictionary. Predefined transforms.
   https://styledictionary.com/reference/hooks/transforms/predefined/ — 739 строк, список прочитан.
8. `[S5a]` Terrazzo. CLI. https://terrazzo.app/docs/cli/ — `init`, `build`, `lint`, `check`, `bundle`.
9. `[S5b]` Terrazzo. CSS plugin. https://terrazzo.app/docs/integrations/css/ — permutations, гамуты,
   правило переобъявления алиасов.
10. `[S19a]` Figma. Overview of variables, collections, and modes.
    https://help.figma.com/hc/en-us/articles/14506821864087
11. `[S19b]` Figma. Modes for variables. https://help.figma.com/hc/en-us/articles/15343816063383
12. `[S19c]` Figma. Guide to variables. https://help.figma.com/hc/en-us/articles/15339657135383
13. `[S20]` Penpot. Design Tokens. https://help.penpot.app/user-guide/design-tokens/ — 868 строк,
    прочитано целиком; математика, типы, sets и themes, `$themes.json`.
14. `[S22a]` Panda CSS. Tokens и semanticTokens. https://panda-css.com/docs/theming/tokens
15. `[S22b]` Open Props. https://open-props.style/ — примитивы без семантики.
16. `[S2]` GitHub Primer. `primer/primitives` — пример `dimension` по спеке и нестандартного типа
    `custom-string`.
17. `[S3]` IBM Carbon. `packages/layout/src/dtcg/layout.json` и README — пример `dimension` голым
    числом плюс `converter`; валидация через `ajv validate -s https://tr.designtokens.org/format/schema.json`.
18. `[S10]` Adobe. `adobe/spectrum-design-data` — типы через `$schema` на токен, `alias` с `$ref` по
    uuid.
19. `[S13]` Material 3. `material-components/material-web`, `tokens/versions/v0_192` — тип `motion_path`
    вне стандарта, генератор выдаёт `null`.
20. `[V16]` Figma Config — `91-videos/digests/`; переменные против стилей, составные типы в Figma.
21. `[V12]` Jan Six. Design Tokens in Figma — `91-videos/digests/`; арифметика, ограничения экспорта.
