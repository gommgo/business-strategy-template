---
slug: study-detail
name: 'Карточка исследования'
description: 'Полный card исследования на desktop'
shell: app-shell
blocks: [study-card]
situations: [open-study-detail]
who: [doctor]
route: /studies/:id
viewport: desktop
entrypoint: false
transitions-to-screen: [studies-workspace, confirm-archive]
status: draft
---

# study-detail

Полный desktop-экран исследования. Сюда ведёт `transitions-to-screen`
из `studies-workspace`. Sidebar и detail-слот не используются —
содержимое полностью в main.

```yaml
slot-fills:
  header:
    - ui:Row justify=between align=center gap=md
      - ui:Logo
      - ui:Nav items=[Studies, Patients, Reports]
      - ui:UserMenu
  side:    —
  main:    block:study-card
  detail:  —
  overlay: —
  footer:
    - ui:StatusBar

states:
  loading:
    main: [ui:Skeleton variant=card large=true]
  error:
    main: [ui:ErrorState retry=true]
  not-found:
    main: [ui:NotFoundState title='Исследование не найдено']
```
