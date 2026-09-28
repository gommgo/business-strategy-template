# block

> Блок (block) — раскрытие interface-block в дерево узлов. Аналитический блок (block) в
> `docs/projects/<project-slug>/interface/<surface>/block.md` объявляет навигационный узел и набор ux-substrates;
> здесь — как эти субстраты собираются в композицию из компонентов (типов закрытого словаря `ui:`), узлов раскладки и
> вложенных блоков. Используется на экранах (screen) как содержимое слотов каркаса (shell).
>
> Блок с полями формы, коллекцией или плитками показателей несёт во frontmatter их контракт — `form`, `collection`,
> `tiles`: без него макет не знает, какой контрол у поля, сколько строк в таблице и с чем сравнивать показатель. Блок
> со своим источником данных (`source: own`) держит свои состояния в разделе `states`.

## Критерии block

1. **Раскрытие interface-block.** Каждый `block` в screens ссылается на ровно один `interface-block` через поле
   `interface-block`. Slug совпадает (одно имя на двух слоях).
2. **Реализует объявленные ux-substrates.** Все ux-substrates соответствующего interface-block перечислены во
   frontmatter `ux-substrates: [...]` (зеркало). Не больше, не меньше; у каждого субстрата — узел в дереве.
3. **Внутренние области как роли.** Дерево начинается с внутренних областей блока: `block-header`, `block-body`,
   `block-footer`, `block-aside`. Области опциональны; минимум — `block-body`. Облик областей — слой дизайна, в дерево
   не пишется.
4. **Композиция компонентов, не один компонент.** Если «блок» сводится к одному `ui:Button` — это не блок, а
   ux-substrate, и не нужен отдельный артефакт.
5. **Может переиспользоваться.** Один `block` может стоять в слотах нескольких screen — поле `used-by-screens` для
   удобства; согласовано с фактическими ссылками `block:<slug>` в screens.
6. **Контракт — по составу дерева.** Субстрат `ввод` или `выбор` — `form`; `ui:Table`, `ui:List`, `ui:TreeView` или
   повторяемая `ui:Card` — `collection`; `ui:KpiTile` — `tiles`.
7. **Свой источник — свои состояния.** Блок, который грузит данные сам, отдельно от экрана (плитка дашборда, панель с
   другим источником), — `source: own` и раздел `states`: `loading-initial`, `error-load`, у коллекции — ещё
   `empty-first-run`, `empty-filtered`, `partial-few`.

## Что block НЕ

- ❌ Не screen: «весь экран» — это screen.
- ❌ Не shell: каркас — shell.
- ❌ Не один компонент: «главная кнопка „Создать“» — узел `ui:Button level=primary` в дереве блока, не блок.
- ❌ Не data-слой: блок объявляет контракт `data:` ссылками; реальная загрузка — в коде.
- ❌ Не FSD-узел: блок не упоминает widgets/features.

## Тест-критерий

«Это раскрытие одного interface-block в композицию компонентов — а не экран, не каркас и не один компонент?»

- «**Список исследований**» (шапка с поиском и созданием + таблица + пагинация) → `studies-list` ✅
- «**Кнопка "Создать"**» — это `ui:Button` с текстом-ребёнком ❌
- «**Рабочее место исследований**» — это screen ❌

## Форма frontmatter

| поле | тип | обязательность | смысл |
|---|---|---|---|
| `slug` | string | yes | совпадает с `interface-block.slug` |
| `name` | string | yes | человекочитаемое имя |
| `description` | string | yes | одна фраза о блоке |
| `interface-block` | `block-slug` (interface) | yes | источник в `docs/projects/<project-slug>/interface/<surface>/block.md` |
| `ux-substrates` | `[ux-substrate-slug]` | yes | зеркало списка из interface |
| `data` | `{ <param>: data:<slug> }` | optional | контракт входных данных |
| `slots` | `[slot-name]` | optional | если блок — контейнер (вложение `block:` внутрь) |
| `source` | `screen \| own` | optional | источник данных: `screen` — общий с экраном (по умолчанию), `own` — свой; тогда раздел `states` блока |
| `form` | `[ {field, control, required, format, validation, error, default, autocomplete} ]` | yes у блока с субстратом `ввод` или `выбор` | контракт полей формы |
| `collection` | `{task, volume, filters, sort, bulk, narrow}` | yes у блока с `ui:Table`, `ui:List`, `ui:TreeView`, повторяемой `ui:Card` | контракт коллекции |
| `tiles` | `[ {value, question, precision, baseline, good, thresholds, delta, period, link, action, no-data} ]` | yes у блока с `ui:KpiTile` | контракт плиток показателей |
| `used-by-screens` | `[screen-slug]` | optional | где встречается (выводимое поле для удобства) |
| `assets` | `[имя-файла]` | optional | сырьё блока в `assets/block/<slug>/` (только имена файлов; без ассетов поле отсутствует) |
| `status` | `draft \| stable` | yes | зрелость записи |

`data` — карта именованных входов в slug-и `data-items` из interface. `used-by-screens` — зеркало; реальный источник —
ссылки `block:<slug>` в screens.

### Контракт поля формы — `form`

Запись на поле (ux 04/05 §1.1). Тип данных, длины и перечень значений — у атрибута объекта глоссария, на который
ведёт `field`: здесь они не повторяются.

- `field` — поле: `data:<item>.<атрибут>`.
- `control` — тип `ui:` узла, привязанного к полю (`TextInput`, `Select`, `Combobox`, `RadioGroup`, `Checkbox`,
  `Switch`, `DatePicker` …); сверяется с деревом. Выбор контрола — по числу вариантов и выборов (ux 04/06 §1).
- `required` — `—` (как у атрибута) \| `true` \| `false`.
- `format` — формат или маска \| `—`.
- `validation` — правило словами и момент проверки (ux 04/05 §4.2); если правило — инвариант домена, ссылка на него,
  второго места правила нет.
- `error` — ключ `text:` строки роли `error`.
- `default` — значение \| «нет: причина» — пустое умолчание тоже решение.
- `autocomplete` — токен автозаполнения \| «нет: причина»; зависит от контекста формы (новый и текущий пароль, адрес
  доставки и оплаты), поэтому живёт у формы, а не у атрибута.

Правило поля формулирует аналитик; инвариант домена — архитектор. Число полей на шаге и в модальном окне — ux 04/05
§2.5; согласия по умолчанию выключены.

### Контракт коллекции — `collection`

Для таблицы, списка, дерева и повторяемых карточек (ux 04/01 §2, ux 06/01 §6.1):

- `task` — задача пользователя над коллекцией: `find` (найти) \| `compare` (сравнить) \| `one-record` (работа с одной
  записью) \| `act` (обработать) — ux 04/01 §1.1.
- `volume` — `{typical, max}`: типичный и максимальный объём; ноль и одна-три записи — состояния `empty-first-run` и
  `partial-few`. Объём питает демо-данные и `overflow-many`, а пороги ux 04/01 §2 решают, нужны ли пагинация, поиск или
  фильтр, управление колонками, `url-state` экрана, массовые действия и экспорт.
- `filters` — атрибуты объекта, по которым фильтруют, \| `—`.
- `sort` — атрибут и направление по умолчанию.
- `bulk` — массовые действия словаря \| `—`.
- `narrow` — способ на узком экране (ux 09/03 §2.2): `priority-columns` \| `scroll-sticky` \| `accordion-row` \|
  `column-tabs` \| `detail-screen`.

### Контракт плитки показателя — `tiles`

Запись на плитку (ux 04/03 §4.3). Незаполненное поле контракта — решение «показатель не выводить»: показатель без базы
сравнения на экран не попадает (ux 04/03 §4.2); подсветка — только за порогами. Вопрос, базу и пороги формулирует
бизнес или аналитик (CLAUDE.md §3).

- `value` — показатель: `data:<item>.<атрибут>`; величина и единица — у атрибута.
- `question` — вопрос роли, на который отвечает плитка.
- `precision` — точность показа.
- `baseline` — база сравнения (план, прошлый период, норма).
- `good` — направление «хорошо»: `up` \| `down` \| `target`.
- `thresholds` — пороги внимания.
- `delta` — изменение против базы.
- `period` — период и частота обновления.
- `link` — экран, где видно, из чего сложился показатель.
- `action` — действие словаря \| `—`.
- `no-data` — ключ `text:` строки, когда данных нет.

## Тело: tree и states

```yaml
tree:
  block-header:
    - layout:row justify=between align=center gap=md:
        - ui:SearchInput
        - ui:Button level=primary action=create:
            - icon:plus
            - text:<раздел>.<экран>.create.action
  block-body:
    - ui:Table items=data:<item>:
        columns:
          - {field: data:<item>.<атрибут>, label: text:<раздел>.<экран>.<атрибут>.column-header}
  block-footer:
    - ui:Pagination

states:                                   # только при source: own
  loading-initial:
    block-body:
      - ui:Skeleton
  error-load:
    block-body:
      - ui:Alert:
          - text:<раздел>.<экран>.error-load.inline-message
```

Текст и иконка — дети узла (`- text:<key>`, `- icon:plus`), не атрибуты. `ui:`-имена — типы закрытого словаря
`kb/common/components.yaml` или расширения проекта; атрибуты узлов — закрытый список канона слоя (`../README.md`,
«Нотация дерева»). Раздел `states` есть только у блока со своим источником: ключи — из словаря состояний экрана,
значение — дельта внутренних областей блока или `'не применимо: причина'`.

## Пример

Иллюстрация формы, не образец ответа: числа объёма и названия — выдуманные.

```markdown
---
slug: studies-list
name: 'Список исследований'
description: 'Таблица исследований с поиском, созданием, экспортом и пагинацией'
interface-block: studies-list
ux-substrates:
  - studies-search
  - create-study
  - studies-table
  - studies-pagination
  - export-studies
data:
  items: data:study
source: screen
collection:
  task: find
  volume: {typical: 40, max: 2000}
  filters: [status, date]
  sort: {by: date, direction: desc}
  bulk: [archive]
  narrow: detail-screen
used-by-screens: [studies-workspace, studies-list-m, archive-view]
status: draft
---

# studies-list

Список исследований с шапкой действий, табличным телом и пагинацией. Источник данных — общий с экраном, поэтому
состояния загрузки, пустоты и ошибки описывает экран, который этот блок размещает.

​```yaml
tree:
  block-header:
    - layout:row justify=between align=center gap=md:
        - ui:SearchInput
        - layout:row gap=sm:
            - ui:Button level=secondary:
                - text:studies.list.filters.action
            - ui:Button level=primary action=create:
                - icon:plus
                - text:studies.list.create.action
  block-body:
    - ui:ScrollArea:
        - ui:Table items=data:study:
            columns:
              - {field: data:study.name, label: text:studies.list.name.column-header}
              - {field: data:study.date, label: text:studies.list.date.column-header}
              - {field: data:study.status, label: text:studies.list.status.column-header}
  block-footer:
    - layout:row justify=between:
        - ui:Pagination
        - ui:Button level=tertiary action=export:
            - text:studies.list.export.action
​```
```

Контракт формы и плитки — иллюстрация полей:

```yaml
form:
  - field: data:referral.patient
    control: Combobox
    required: —
    format: —
    validation: 'пациент выбран из своей клиники; проверка при отправке'
    error: text:referrals.new.patient.error
    default: 'нет: пациента выбирает врач'
    autocomplete: 'нет: выбор из справочника'
tiles:
  - value: data:referrals-summary.sent
    question: 'сколько направлений ушло за неделю'
    precision: 'целое'
    baseline: 'прошлая неделя'
    good: up
    thresholds: '<пороги от заказчика>'
    delta: 'разница с прошлой неделей'
    period: 'неделя, обновление раз в час'
    link: referrals-list
    action: —
    no-data: text:dashboard.referrals-sent.empty
```

## Anti-patterns

- ❌ Расхождение `ux-substrates` с зеркалом в `docs/projects/<project-slug>/interface/<surface>/block.md` (одни и те же
  блок-slug в обоих слоях — одни и те же субстраты).
- ❌ Дерево без `block-body`.
- ❌ Облик в дереве (цвет, тень, шрифт, вид и размер компонента) — облик решает слой дизайна.
- ❌ Оси контекста приложения (тема, бренд, плотность, направление письма) как атрибуты узлов — их решают бриф на вид
  и дизайн-система, применяет корень приложения в коде.
- ❌ Breakpoints в дереве (облицовочный адаптив — `shell.responsive`, структурный — `flow`).
- ❌ Один и тот же `data:<slug>` под разными именованными слотами — переиспользовать data-items напрямую.
- ❌ Индикаторы и состояния в `tree` блока: у блока со своим источником они живут в разделе `states`, у остальных — в
  `states` экрана.
- ❌ Форма без `form`, коллекция без `volume`, плитка без базы сравнения — макет по ним не собирается.
- ❌ Тип, длины или перечень поля в `form` вместо ссылки на атрибут объекта.
