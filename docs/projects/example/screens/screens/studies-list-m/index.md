---
slug: studies-list-m
name: 'Список исследований (mobile)'
description: 'Mobile master: список + точка входа в фильтры'
shell: mobile-shell
blocks: [studies-list]
situations: [browse-studies]
who: [doctor, nurse]
route: /m/studies
viewport: mobile
mobile-of: studies-browse
role: master
entrypoint: false
transitions-to-screen: [study-detail-m, filters-m, confirm-archive]
status: draft
---

# studies-list-m

Master-экран mobile-серии. Шапка mobile-shell несёт переключатели
фильтров и поиска; main занимает блок `studies-list`. Переход на
detail и на filters — через transitions внутри `flow studies-browse`.

```yaml
slot-fills:
  header:
    - ui:Row justify=between align=center gap=sm
      - ui:IconButton icon=menu
      - ui:Text variant=h-mobile label='Исследования'
      - ui:Row gap=xs
        - ui:IconButton icon=search
        - ui:IconButton icon=filter
  main:    block:studies-list
  overlay: —

states:
  loading:
    main: [ui:Skeleton variant=list rows=8]
  empty:
    main:
      - ui:EmptyState
          illustration: no-studies
          title: 'Исследований пока нет'
          action: ui:Button variant=primary icon=plus label='Новое'
  error:
    main: [ui:ErrorState retry=true]
  offline:
    main: [ui:OfflineState retry=true]
```
