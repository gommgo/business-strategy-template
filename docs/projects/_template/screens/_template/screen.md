# screen

> Экран (screen) — route/view с типизированными слотами, заполненными
> блоками (block) или inline-деревьями. Фиксирует, **что в каком слоте**
> shell-каркаса и **как меняется содержимое в нештатных состояниях**
> (loading, empty, error, permission-denied, offline, not-found).

## Критерии screen

1. **Route/view.** Один screen = одна точка маршрута (URL или
   именованный view). На разных viewport один сценарий может занимать
   разные screen — связь через `flow`.
2. **Ссылается на shell.** Поле `shell` обязательно: каркас задаёт
   слоты, которые screen заполняет.
3. **Заполняет слоты, не определяет их.** Слоты декларирует shell;
   screen в `slot-fills` указывает содержимое (один блок, inline-дерево
   или ничего, если слот опционален).
4. **Состояния — поле, не отдельный файл.** Loading/empty/error/...
   живут секцией `states` в том же `index.md`, как delta-overrides
   слотов.
5. **Знает свои блоки и ситуации.** Frontmatter перечисляет
   `blocks: [...]` и `situations: [...]` — для трассировки до interface.

## Что screen НЕ

- ❌ Не block: содержимое слота — это блок (block); screen — это
  оркестратор слотов.
- ❌ Не shell: каркас приложения — shell.
- ❌ Не flow: связь desktop ↔ mobile — flow.
- ❌ Не data-слой: контракт данных — `data:` ссылки на data-items, а
  реальная загрузка/хранение — в коде.
- ❌ Не FSD-узел: screen не упоминает `pages/`/`widgets/`. FSD-структура
  появляется в коде вручную при сборке wireframe/hi-fi, не здесь.

## Тест-критерий

«Это одна точка маршрута / view с заполненными слотами shell и
описанными нештатными состояниями — а не shell, не блок, не сценарий
desktop↔mobile?»

- «**Рабочее место исследований**» (`/studies`) → `studies-workspace` ✅
- «**Список исследований**» как содержимое main → это block
  `studies-list`, не screen ❌
- «**Browse исследований**» как объединение desktop+mobile → flow,
  не screen ❌

## Форма frontmatter

| поле | тип | обязательность | смысл |
|---|---|---|---|
| `slug` | string | yes | kebab-case идентификатор |
| `name` | string | yes | человекочитаемое имя |
| `description` | string | yes | одна фраза о screen |
| `shell` | `shell-slug` | yes | каркас, чьи слоты заполняются |
| `blocks` | `[block-slug]` | yes | блоки, которые встречаются на экране |
| `situations` | `[situation-slug]` | yes | ситуации interface, разыгрываемые здесь |
| `who` | `[who-slug]` | yes | роли interface, для которых экран существует |
| `route` | string | yes | URL или именованный view (`/studies`, `modal:archive-confirm`) |
| `viewport` | `desktop \| mobile \| any` | yes | для какого viewport назначен экран |
| `entrypoint` | bool | optional | стартовая точка (по аналогии с `block.entrypoint`) |
| `transitions-to-screen` | `[screen-slug]` | optional | явные переходы наружу (между viewport одного flow не пишутся) |
| `mobile-of` | `flow-slug` | optional | для mobile-screen-членов flow — поток-родитель |
| `role` | string | optional | роль внутри flow (`master`, `detail`, `filters`, …) |
| `assets` | `[имя-файла]` | optional | визуальные референсы в `assets/screen/<slug>/` (только имена файлов; без ассетов поле отсутствует) |
| `status` | `draft \| stable` | yes | зрелость записи |

## Тело: slot-fills и states

```yaml
slot-fills:
  side:    block:filters-panel
  main:    block:studies-list
  detail:  block:study-preview
  overlay: —

states:
  loading:
    main:    [ui:Skeleton (planned)]
    detail:  [ui:Spinner size=lg]
  empty:
    main:
      - layout:stack align=center gap=md
        - 'Исследований пока нет'
        - ui:Button variant=accent
          - 'Создать'
  error:
    main:
      - layout:stack align=center gap=md
        - 'Не удалось загрузить список'
        - ui:Button variant=outline
          - 'Повторить'
  permission-denied:
    main: ['Нет доступа к исследованиям — запросите права у администратора']
  offline:
    main: ['Нет соединения — список появится при восстановлении сети']
  not-found:
    main: ['Исследование не найдено']
```

`slot-fills` — основная композиция: для каждого слота shell либо
`block:<slug>`, либо inline-дерево, либо `—` (если опционален). `states`
— delta-overrides на слот (другие слоты унаследованы из `slot-fills`).
Облик состояния — композиция и текст; компонент из манифеста
(`ui:Spinner`) или forward-реф (`ui:Skeleton (planned)`) — когда он
действительно есть/запланирован в `@stit/ui`.

## Пример

```markdown
---
slug: studies-workspace
name: 'Рабочее место исследований'
description: 'Master/detail: список + фильтры + превью одного'
shell: app-shell
blocks: [filters-panel, studies-list, study-preview]
situations: [browse-studies, archive-study, open-study-preview]
who: [doctor, nurse]
route: /studies
viewport: desktop
entrypoint: false
transitions-to-screen: [study-detail, new-study]
status: draft
---

# studies-workspace

Основной desktop-экран сценария `studies-browse`. На mobile сценарий
разворачивается через flow `studies-browse` в три экрана.

​```yaml
slot-fills:
  side:    block:filters-panel
  main:    block:studies-list
  detail:  block:study-preview

states:
  loading:
    main:   [ui:Skeleton (planned)]
    detail: [ui:Spinner size=lg]
  empty:
    main:
      - layout:stack align=center gap=md
        - 'Исследований пока нет'
        - ui:Button variant=accent
          - 'Создать'
  error:
    main:
      - layout:stack align=center gap=md
        - 'Не удалось загрузить список'
        - ui:Button variant=outline
          - 'Повторить'
  permission-denied:
    main: ['Нет доступа к исследованиям — запросите права у администратора']
​```
```

## Anti-patterns

- ❌ Облик в `slot-fills` (цвета, пиксели, шрифты).
- ❌ Оси контекста (`brand`, `scheme`, `density`, `mode`, `dir`) как
  props компонентов в дереве — они живут на корне приложения
  (`data-*` / `StitProvider`).
- ❌ Breakpoints в `slot-fills`. Облицовочный адаптив — в `shell`,
  структурный — через `flow`.
- ❌ FSD-имена (`widget`, `feature`) в дереве или в frontmatter.
- ❌ `state` без явного override (пустая секция).
- ❌ Расхождение `screen.blocks` и реально используемых `block:<slug>`
  в `slot-fills` / `states`.
- ❌ `screen.situations`, не покрывающий ситуации (situation), чьи
  ux-substrates на этом экране есть.
- ❌ Один screen-slug в `desktop` и `mobile` одновременно у flow.
