---
# иллюстрация: экран вольной записи фикстуры cabinet-freeform — для самопроверки нормализатора, не данные проекта
slug: request-card
name: 'Карточка заявки'
description: 'Одна заявка: клиент, адрес, дата замера, назначение и отметка замера'
shell: app-shell
blocks: [request-details]
situations: [schedule-visit, mark-measured]
who: [manager, surveyor]
route: /requests/:id
viewport: any
transitions-to-screen: [requests-list]
status: draft
---

# request-card

Карточка заявки в вольной записи: ключи состояний мобильного слоя, тексты литералами, переход строкой; типа, объекта,
задачи, действия, зоны, параметров и доступа у экрана нет.

```yaml
slot-fills:
  main: block:request-details
  overlay: —

states:
  loading:
    main:
      - ui:Skeleton
  error:
    main:
      - ui:Alert
        - 'Заявка не загрузилась'
  permission-denied:
    main:
      - layout:stack align=center
        - 'Нет доступа к заявке'
        - 'Заявку открывает руководитель студии'
  not-found:
    main:
      - layout:stack align=center
        - 'Заявки нет'
        - ui:Link
          - 'К списку заявок'
  offline:                 # здесь не применимо — карточка без сети не открывается
```
