---
# иллюстрация: экран демо-кабинета фикстуры cabinet — для самопроверок утилит скилла, не данные проекта
slug: requests-list
name: 'Список заявок'
description: 'Все заявки на замер с поиском, фильтром по статусу и созданием новой'
type: list
object: request
main-task: schedule-visit
key-action: create
zone: requests
shell: app-shell
blocks: [requests-list]
situations: [find-request, create-request]
who: [manager, surveyor]
route: /requests
params: —
access: roles
url-state: [filters, sort, page]
indexed: false
viewport: any
entrypoint: true
transitions-to-screen:
  - {to: request-card, trigger: 'выбор строки', keeps: 'фильтры, сортировка, страница', back: 'назад, крошки'}
  - {to: request-new, trigger: create, keeps: '—', back: 'отмена возвращает сюда'}
status: stable
---

# requests-list

Рабочий список менеджера и замерщика. Главная кнопка «Создать заявку» стоит в шапке блока `requests-list`, поэтому
пустое состояние на неё только указывает.

```yaml
slot-fills:
  main: block:requests-list
  overlay: —

states:
  loading-initial:
    main:
      - ui:Skeleton
  loading-refresh:
    main:
      - ui:Progress
      - block:requests-list
  empty-first-run:
    main:
      - ui:EmptyState:
          - text:requests.list.empty-first-run.empty
  empty-filtered:
    main:
      - ui:EmptyState:
          - text:requests.list.empty-filtered.empty
          - ui:Button level=secondary:
              - text:requests.list.reset-filters.action
  partial-few: 'не применимо: одна-три строки таблица держит в обычной раскладке'
  overflow-many: 'не применимо: пагинация и счётчик найденного — в дереве блока requests-list'
  error-load:
    main:
      - ui:Alert:
          - text:requests.list.error-load.inline-message
          - ui:Button level=secondary:
              - text:requests.list.retry.action
  error-action: 'не применимо: список только ведёт к бланку, создание и его ошибка — на экране request-new'
  no-permission:
    main:
      - layout:stack align=center gap=md:
          - text:requests.list.no-permission.title
          - text:requests.list.no-permission.body
```
