---
slug: filters-m
name: 'Фильтры (mobile)'
description: 'Mobile filters: панель фильтров на полном экране'
shell: mobile-shell
blocks: [filters-panel]
situations: [browse-studies]
who: [doctor, nurse]
route: /m/studies/filters
viewport: mobile
mobile-of: studies-browse
role: filters
entrypoint: false
transitions-to-screen: [studies-list-m]
status: draft
---

# filters-m

Filters-экран mobile-серии. На desktop та же `filters-panel`
живёт в side-слоте `studies-workspace`; на mobile разворачивается на
весь main с собственными action-кнопками в шапке.

```yaml
slot-fills:
  header:
    - ui:Row justify=between align=center gap=sm
      - ui:IconButton icon=close
      - ui:Text variant=h-mobile label='Фильтры'
      - ui:Button variant=ghost label='Сбросить'
  main:    block:filters-panel
  overlay: —
```
