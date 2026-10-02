---
# иллюстрация: экран демо-кабинета фикстуры cabinet — для самопроверок утилит скилла, не данные проекта
slug: request-card
name: 'Карточка заявки'
description: 'Одна заявка: клиент, адрес, дата замера, назначение и отметка замера'
type: object
object: request
main-task: schedule-visit
key-action: schedule
zone: request-card
shell: app-shell
blocks: [request-details]
situations: [schedule-visit, mark-measured]
who: [manager, surveyor]
route: /requests/:id
params: {id: request}
access: roles
indexed: false
viewport: any
transitions-to-screen:
  - {to: requests-list, trigger: 'назад к списку', keeps: 'фильтры, сортировка, страница', back: 'выбор строки в списке'}
status: stable
---

# request-card

Карточка одной заявки: менеджер назначает замер, замерщик отмечает проведённый. Заявку открывают из списка или
ссылкой из письма о назначенном замере.

```yaml
slot-fills:
  main: block:request-details
  overlay: —

states:
  loading-initial:
    main:
      - ui:Skeleton
  error-load:
    main:
      - ui:Alert:
          - text:requests.card.error-load.inline-message
          - ui:Button level=secondary:
              - text:requests.card.retry.action
  error-action:
    main:
      - ui:Alert:
          - text:requests.card.error-action.inline-message
      - block:request-details
  success: 'не применимо: результат виден сменой статуса заявки'
  no-permission:
    main:
      - layout:stack align=center gap=md:
          - text:requests.card.no-permission.title
          - text:requests.card.no-permission.body
  not-found:
    main:
      - layout:stack align=center gap=md:
          - text:requests.card.not-found.title
          - text:requests.card.not-found.body
          - ui:Link:
              - text:requests.card.back-to-list.link
  offline:
    main:
      - ui:Banner:
          - text:requests.card.offline.banner
      - block:request-details
```
