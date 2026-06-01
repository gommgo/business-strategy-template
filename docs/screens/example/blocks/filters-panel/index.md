---
slug: filters-panel
name: 'Панель фильтров'
description: 'Форма из выборов статуса, диапазона дат, владельца + apply/reset'
interface-block: filters-panel
ux-substrates:
  - filter-status
  - filter-date-range
  - filter-owner
  - apply-filters
  - reset-filters
used-by-screens: [studies-workspace, filters-m]
status: draft
---

# filters-panel

Форма-блок: набор полей выборов и пара кнопок-действий. Используется
двумя экранами разных viewport: на desktop в side-слоте
`studies-workspace`, на mobile в main-слоте `filters-m`. Сам блок не
знает, как именно его обрамляет screen — про шапку «Фильтры» и
кнопку «Сбросить» в шапке отвечает screen, а не блок.

```yaml
tree:
  block-body:
    - ui:Form
      - ui:Stack gap=lg
        - ui:Field label='Статус'
          - ui:Select options=[all, draft, in-review, archived]
        - ui:Field label='Период'
          - ui:DateInput range=true
        - ui:Field label='Владелец'
          - ui:Select options=data:user
  block-footer:
    - ui:Row justify=between align=center gap=sm
      - ui:Button variant=ghost label='Сбросить'
      - ui:Button variant=primary label='Применить'
```
