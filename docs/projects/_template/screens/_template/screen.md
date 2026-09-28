# screen

> Экран (screen) — маршрут приложения с типом, объектом, главной задачей и ключевым действием, чьи слоты каркаса
> заполнены блоками (block) или деревьями. Фиксирует, **что в каком слоте** каркаса (shell), **по какому маршруту и
> кому** экран доступен, **куда с него переходят** и **как меняется содержимое в состояниях** экрана — по словарю
> состояний канона слоя. Поля экранов — канон карты экранов и реестра маршрутов поверхности; свод по ним — `map.md`.

## Критерии screen

1. **Маршрут.** Один screen = одна точка маршрута (URL или именованный view). На разных viewport одна задача может
   занимать разные screen — связь через `flow`. Маршрут входит в закрытый реестр поверхности.
2. **Для кого, над чем, ради чего.** У экрана тип из закрытого списка (`type`), объект глоссария (`object`), главная
   задача — возможность этой поверхности (`main-task`) и одно ключевое действие словаря (`key-action`). Экран без
   объекта и роли — «главная», «обзор» без обоснования — типовая ошибка; `object: —` требует решения в `map.md`
   (раздел «Решения»).
3. **Ссылается на shell.** Поле `shell` обязательно: каркас задаёт слоты, которые screen заполняет.
4. **Заполняет слоты, не определяет их.** Слоты декларирует shell; screen в `slot-fills` указывает содержимое (один
   блок, дерево или `—`, если слот опционален).
5. **Состояния — поле, не отдельный файл.** Состояния экрана живут секцией `states` в том же `index.md` как дельты
   слотов; ключи — slug словаря состояний экрана (канон слоя, «Состояния экрана»). Обязательный набор — по типу экрана
   и условиям: каждое обязательное состояние описано дельтой или помечено `'не применимо: причина'`.
6. **Доступ и адрес названы.** `access` — кто имеет доступ; `params` — параметры маршрута; `url-state` — какое
   состояние экрана живёт в адресе (у `list` и `master-detail` обязателен).
7. **Знает свои блоки, ситуации и переходы.** Frontmatter перечисляет `blocks` и `situations` — для трассировки до
   interface; `transitions-to-screen` — куда ведут переходы, чем вызваны, что сохраняется и как вернуться.

## Что screen НЕ

- ❌ Не block: содержимое слота — это блок (block); screen — это оркестратор слотов.
- ❌ Не shell: каркас приложения — shell.
- ❌ Не flow: связь desktop ↔ mobile — flow.
- ❌ Не data-слой: контракт данных — `data:` ссылки на data-items, а реальная загрузка/хранение — в коде.
- ❌ Не FSD-узел: screen не упоминает слайсы `pages` и `widgets`. FSD-структура — отдельный слой `fsd/<surface>/`,
  который читает экраны как источник.
- ❌ Не носитель облика: вид, отступы, цвета и размеры компонентов — слой дизайна.

## Тест-критерий

«Это одна точка маршрута с типом, объектом и главной задачей, с заполненными слотами shell и описанными состояниями
обязательного набора — а не shell, не блок, не поток desktop↔mobile?»

- «**Рабочее место исследований**» (`/studies`, `master-detail`, объект — исследование) → `studies-workspace` ✅
- «**Список исследований**» как содержимое main → это block `studies-list`, не screen ❌
- «**Browse исследований**» как объединение desktop+mobile → flow, не screen ❌
- «**Главная**» без объекта, роли и задачи → ❌ (нужна задача или решение в `map.md`)

## Форма frontmatter

| поле | тип | обязательность | смысл |
|---|---|---|---|
| `slug` | string | yes | kebab-case идентификатор |
| `name` | string | yes | человекочитаемое имя |
| `description` | string | yes | одна фраза о screen |
| `type` | `dashboard \| list \| object \| edit \| wizard \| settings \| master-detail \| canvas \| auth \| service` | yes | тип экрана (канон слоя, «Экран: тип, карта и маршрут») |
| `object` | `object-slug` \| `—` | yes | объект глоссария `object.md`; `—` — с решением в `map.md` |
| `main-task` | `capability-slug` \| `—` | yes | возможность этой поверхности, ради которой экран; у `service` — `—` |
| `key-action` | `action-slug` \| `—` | yes | одно ключевое действие словаря `action.md`; `—` у `service` и у экрана только для чтения |
| `zone` | `zone-slug` \| `—` | yes | зона interface: мост «зона → раздел → маршрут»; у `service` — `—` |
| `shell` | `shell-slug` | yes | каркас, чьи слоты заполняются |
| `blocks` | `[block-slug]` | yes | блоки, которые встречаются на экране |
| `situations` | `[situation-slug]` | yes | ситуации interface, разыгрываемые здесь |
| `who` | `[who-slug]` | yes | роли interface, для которых экран существует |
| `route` | string | yes | маршрут как есть (`/studies/:id`, `modal:archive-confirm`) |
| `params` | `{ <имя>: <тип> }` \| `—` | yes | параметры маршрута; тип — объект глоссария (параметр объекта) или тип атрибута |
| `access` | `public \| authenticated \| roles` | yes | кто имеет доступ; `roles` — роли `who` этого экрана |
| `url-state` | подмножество `[tab, page, filters, sort, view, panel]` \| `—` | yes у `list`, `master-detail` | какое состояние экрана живёт в адресе |
| `indexed` | bool | optional | индексируется ли маршрут (по умолчанию `false`) |
| `viewport` | `desktop \| mobile \| any` | yes | для какого вьюпорта назначен экран; ширины приёмки — `kb/common/acceptance-widths.yaml` (ключ `by_viewport`) |
| `entrypoint` | bool | optional | стартовый экран роли (по аналогии с `block.entrypoint`) |
| `transitions-to-screen` | `[ {to, trigger, keeps, back} ]` | optional | переходы наружу: куда; чем вызван — действие словаря или событие; что сохраняется; как вернуться или `irreversible` (между viewport одного flow не пишутся) |
| `mobile-of` | `flow-slug` | optional | для mobile-screen-членов flow — поток-родитель |
| `role` | string | optional | роль внутри flow (`master`, `detail`, `filters`, …) |
| `assets` | `[имя-файла]` | optional | сырьё экрана в `assets/screen/<slug>/` (только имена файлов; без ассетов поле отсутствует) |
| `status` | `draft \| stable` | yes | зрелость записи |

- `params` с объектным типом делает `not-found` обязательным; `access: roles` — `no-permission`; список и
  master-detail без `url-state` теряют фильтры и страницу при переходе.
- `transitions-to-screen.keeps` называет то, что строка раздела «Переход» `map.md` обещает пережить переход;
  `back: irreversible` — у перехода, после которого вернуться нельзя.
- Для `stable`: `type`, `object`, `main-task`, `key-action`, `zone`, `route`, `access` заполнены (или `—` по правилам
  выше), обязательный набор состояний покрыт, у каждого ключа `text:` в дереве есть строка реестра `texts.md` со
  статусом не ниже `checked`.

## Тело: slot-fills и states

```yaml
slot-fills:
  side: block:filters-panel
  main: block:studies-list
  detail: block:study-preview
  overlay: —

states:
  loading-initial:
    main:
      - ui:Skeleton
    detail:
      - ui:Skeleton
  empty-first-run:
    main:
      - ui:EmptyState illustration=<метафора>:
          - text:<раздел>.<экран>.empty-first-run.empty
    detail: —
  error-load:
    main:
      - ui:Alert:
          - text:<раздел>.<экран>.error-load.inline-message
          - ui:Button level=secondary:
              - text:<раздел>.<экран>.retry.action
  partial-few: 'не применимо: <причина>'
```

`slot-fills` — основная (идеальная) композиция: для каждого слота shell либо `block:<slug>`, либо дерево, либо `—`
(если опционален). `states` — ключ состояния из словаря → дельты слотов (другие слоты унаследованы из `slot-fills`;
`—` — слот в этом состоянии пуст) или строка `'не применимо: причина'` для обязательного состояния, которому на этом
экране нечего показать. Нотация деревьев, словарь ключей, обязательный набор и приоритет состояний — канон слоя
(`../README.md`, разделы «Нотация дерева» и «Состояния экрана»).

## Доступность

Необязательный раздел тела экрана — отступления от конвенций поверхности (конвенции доступности живут в `map.md`,
раздел «Конвенции»):

```markdown
## Доступность

- <узел с перетаскиванием> — путь одним указателем и с клавиатуры: <какой>
- <особая фокусировка>: <что и почему>
```

## Пример

Иллюстрация формы, не образец ответа.

```markdown
---
slug: studies-workspace
name: 'Рабочее место исследований'
description: 'Список исследований с фильтрами и превью выбранного'
type: master-detail
object: study
main-task: find-study
key-action: create
zone: studies
shell: app-shell
blocks: [filters-panel, studies-list, study-preview]
situations: [browse-studies, archive-study, open-study-preview]
who: [doctor, nurse]
route: /studies
params: —
access: roles
url-state: [filters, sort, page, panel]
indexed: false
viewport: desktop
entrypoint: false
transitions-to-screen:
  - {to: study-detail, trigger: 'выбор строки', keeps: 'фильтры, страница, прокрутка', back: 'назад, крошки'}
  - {to: new-study, trigger: create, keeps: '—', back: 'отмена возвращает сюда'}
status: draft
---

# studies-workspace

Основной desktop-экран задачи «найти исследование». На mobile задача разворачивается потоком `studies-browse` в три
экрана. Главная кнопка «Создать» стоит в шапке блока `studies-list`, поэтому пустое состояние на неё только
указывает.

​```yaml
slot-fills:
  side: block:filters-panel
  main: block:studies-list
  detail: block:study-preview

states:
  loading-initial:
    main:
      - ui:Skeleton
    detail:
      - ui:Skeleton
  loading-refresh:
    main:
      - ui:Progress
      - block:studies-list
  empty-first-run:
    main:
      - ui:EmptyState illustration=empty-archive:
          - text:studies.workspace.empty-first-run.empty
    detail: —
  empty-filtered:
    main:
      - ui:EmptyState:
          - text:studies.workspace.empty-filtered.empty
          - ui:Button level=secondary:
              - text:studies.workspace.reset-filters.action
    detail: —
  partial-few: 'не применимо: одна-три строки таблица держит в обычной раскладке'
  overflow-many: 'не применимо: пагинация и счётчик найденного — в дереве блока studies-list'
  error-load:
    main:
      - ui:Alert:
          - text:studies.workspace.error-load.inline-message
          - ui:Button level=secondary:
              - text:studies.workspace.retry.action
  error-action:
    detail:
      - ui:Alert:
          - text:studies.workspace.archive-failed.inline-message
      - block:study-preview
  success: 'не применимо: архивное исследование уходит из списка, результат виден без сообщения'
  no-permission:
    main:
      - layout:stack align=center gap=md:
          - text:studies.workspace.no-permission.title
          - text:studies.workspace.no-permission.body
          - ui:Button level=primary:
              - text:studies.workspace.request-access.action
    side: —
    detail: —
​```
```

Экран объекта с параметром маршрута (`route: /studies/:id`, `params: {id: study}`) держит `not-found` и отличает его
от архива — иллюстрация:

```yaml
states:
  not-found:
    main:
      - layout:stack align=center gap=md:
          - text:studies.detail.not-found.title
          - text:studies.detail.not-found.body
          - ui:Link:
              - text:studies.detail.back-to-list.link
  archived-deleted:
    main:
      - ui:Alert:
          - text:studies.detail.archived.inline-message
          - ui:Button level=secondary action=restore:
              - text:studies.detail.restore.action
      - block:study-summary
```

## Anti-patterns

- ❌ Облик в `slot-fills` (цвета, пиксели, шрифты, вид и размер компонента) — облик решает слой дизайна.
- ❌ Оси контекста приложения (тема, бренд, плотность, направление письма) как атрибуты узлов дерева — их решают бриф
  на вид и дизайн-система, применяет корень приложения в коде.
- ❌ Breakpoints в `slot-fills`. Облицовочный адаптив — в `shell`, структурный — через `flow`.
- ❌ FSD-имена (`widget`, `feature`) в дереве или в frontmatter.
- ❌ `state` без явного override (пустая секция) и обязательное состояние без дельты и без «не применимо: причина».
- ❌ Ключ `states` вне словаря состояний экрана; `not-found` вместо `archived-deleted` у архивного объекта.
- ❌ Литерал текста в дереве `stable`-экрана — только `text:<key>` со строкой в реестре.
- ❌ Маршрут вне реестра `map.md`; экран без `type`, `route` или `access`.
- ❌ Расхождение `screen.blocks` и реально используемых `block:<slug>` в `slot-fills` / `states`.
- ❌ `screen.situations`, не покрывающий ситуации (situation), чьи ux-substrates на этом экране есть.
- ❌ Один screen-slug в `desktop` и `mobile` одновременно у flow.
