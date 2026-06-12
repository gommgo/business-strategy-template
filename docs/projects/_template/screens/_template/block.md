# block

> Блок (block) — раскрытие interface-block в дерево компонентов.
> Аналитический блок (block) в
> `docs/projects/<project-slug>/interface/<surface>/block.md` объявляет
> навигационный узел и набор ux-substrates; здесь — что и как эти
> субстраты собираются в облик через компоненты `@stit/ui`.
> Используется на экранах (screen) как содержимое слотов shell.

## Критерии block

1. **Раскрытие interface-block.** Каждый `block` в screens ссылается
   на ровно один `interface-block` через поле `interface-block`. Slug
   совпадает (одно имя на двух слоях).
2. **Реализует объявленные ux-substrates.** Все ux-substrates
   соответствующего interface-block перечислены во frontmatter
   `ux-substrates: [...]` (зеркало). Не больше, не меньше.
3. **Internal-zones как роли.** Дерево начинается с зон:
   `block-header`, `block-body`, `block-footer`, `block-aside`.
   Зоны опциональны; минимум — `block-body`. Облик зон оформляет
   ui-lib.
4. **Композиция компонентов, не один компонент.** Если «блок» сводится
   к одному `ui:Button` — это не блок, а ux-substrate, и не нужен
   отдельный артефакт.
5. **Может переиспользоваться.** Один `block` может стоять в слотах
   нескольких screen — поле `used-by-screens` для удобства; согласовано
   с фактическими ссылками `block:<slug>` в screens.

## Что block НЕ

- ❌ Не screen: «весь экран» — это screen.
- ❌ Не shell: каркас — shell.
- ❌ Не один компонент: «accent-кнопка размером md» — это props
  `ui:Button`, не блок.
- ❌ Не data-слой: блок объявляет контракт `data:` ссылками; реальная
  загрузка — в коде.
- ❌ Не FSD-узел: блок не упоминает widgets/features.

## Тест-критерий

«Это раскрытие одного interface-block в композицию компонентов
ui-lib — а не экран, не каркас и не один компонент?»

- «**Список исследований**» (toolbar + таблица + пагинация) →
  `studies-list` ✅
- «**Кнопка "Создать"**» — это `ui:Button` с children-текстом ❌
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
| `used-by-screens` | `[screen-slug]` | optional | где встречается (выводимое поле для удобства) |
| `assets` | `[имя-файла]` | optional | визуальные референсы в `assets/block/<slug>/` (только имена файлов; без ассетов поле отсутствует) |
| `status` | `draft \| stable` | yes | зрелость записи |

`data` — карта именованных входов в slug-и `data-items` из interface.
`used-by-screens` — зеркало; реальный источник — ссылки `block:<slug>`
в screens.

## Тело: tree с internal-zones

```yaml
tree:
  block-header:
    - layout:row justify=between align=center gap=md
      - ui:Search size=md
      - layout:row gap=sm
        - ui:Button variant=ghost
          - 'Фильтры'
        - ui:Button variant=accent
          - icon:plus
          - 'Новое'
  block-body:
    - ui:ScrollArea scrollbars=vertical
      - ui:Table (planned)
          items: data:study
          columns:
            - { field: data:study.name,   label: 'Имя' }
            - { field: data:study.date,   label: 'Дата' }
            - { field: data:study.status, label: 'Статус' }
            - { field: data:study.owner,  label: 'Владелец' }
  block-footer:
    - layout:row justify=between
      - ui:Pagination (planned)
      - ui:Button variant=ghost
        - 'Экспорт'
```

Текст и иконка — children-узлы (`- 'Новое'`, `- icon:plus`), не props.
`ui:Table (planned)` / `ui:Pagination (planned)` — forward-рефы на
запланированные компоненты из `notAvailable` манифеста (см. канон слоя,
«Контракт с `@stit/ui`»).

## Пример

```markdown
---
slug: studies-list
name: 'Список исследований'
description: 'Табличный вывод + поиск + создание + пагинация'
interface-block: studies-list
ux-substrates:
  - studies-search
  - create-study
  - studies-table
  - study-row-menu
  - studies-pagination
data:
  items: data:study
used-by-screens: [studies-workspace, studies-list-m, archive-view]
status: draft
---

# studies-list

Стандартный list-block с шапкой действий, табличным телом и пагинацией.
Облик loading/empty/error не описывается здесь — их override живёт в
screen, который этот блок размещает.

​```yaml
tree:
  block-header:
    - layout:row justify=between align=center gap=md
      - ui:Search size=md
      - layout:row gap=sm
        - ui:Button variant=ghost
          - 'Фильтры'
        - ui:Button variant=accent
          - icon:plus
          - 'Новое'
  block-body:
    - ui:ScrollArea scrollbars=vertical
      - ui:Table (planned)
          items: data:study
          columns:
            - { field: data:study.name,   label: 'Имя' }
            - { field: data:study.date,   label: 'Дата' }
            - { field: data:study.status, label: 'Статус' }
  block-footer:
    - layout:row justify=between
      - ui:Pagination (planned)
      - ui:Button variant=ghost
        - 'Экспорт'
​```
```

## Anti-patterns

- ❌ Расхождение `ux-substrates` с зеркалом в
  `docs/projects/<project-slug>/interface/<surface>/block.md` (одни и те же
  блок-slug в обоих слоях — одни и те же субстраты).
- ❌ Дерево без `block-body`.
- ❌ Облик в дереве (цвет, тень, шрифт).
- ❌ Оси контекста (`brand`/`scheme`/`density`/`mode`/`dir`) как props
  узлов — они живут на корне приложения (`data-*` / `StitProvider`).
- ❌ Breakpoints в дереве (адаптив блока — props ui-lib + shell).
- ❌ Один и тот же `data:<slug>` под разными именованными слотами —
  переиспользовать data-items напрямую.
- ❌ Inline-cтейты (loading/empty) в дереве блока — это слой screen.
