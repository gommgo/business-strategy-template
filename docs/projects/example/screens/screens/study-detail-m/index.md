---
slug: study-detail-m
name: 'Карточка исследования (mobile)'
description: 'Mobile detail: полный study-card в main'
shell: mobile-shell
blocks: [study-card]
situations: [open-study-detail]
who: [doctor]
route: /m/studies/:id
viewport: mobile
mobile-of: studies-browse
role: detail
entrypoint: false
transitions-to-screen: [studies-list-m, confirm-archive]
status: draft
---

# study-detail-m

Detail-экран mobile-серии. Шапка mobile-shell содержит навигацию
назад и контекстное меню; main — полный `study-card`. Возврат к
master — через `transitions` в flow `studies-browse`.

```yaml
slot-fills:
  header:
    - ui:Row justify=between align=center gap=sm
      - ui:IconButton icon=back
      - ui:Text variant=h-mobile label='Исследование'
      - ui:IconButton icon=more
  main:    block:study-card
  overlay: —

states:
  loading:
    main: [ui:Skeleton variant=card large=true]
  error:
    main: [ui:ErrorState retry=true]
  not-found:
    main: [ui:NotFoundState]
  offline:
    main: [ui:OfflineState retry=true]
```
