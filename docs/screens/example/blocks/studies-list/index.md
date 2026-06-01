---
slug: studies-list
name: 'Список исследований'
description: 'Sticky-шапка с поиском, скроллируемая таблица, footer с пагинацией'
interface-block: studies-list
ux-substrates:
  - studies-search
  - create-study
  - studies-table
  - study-row-menu
  - studies-pagination
data:
  items: data:study
used-by-screens: [studies-workspace, studies-list-m]
status: stable
---

# studies-list

Базовый list-блок проекта. Шапка прилипает к верху main, тело
скроллируется, footer с пагинацией остаётся внизу. Облик loading,
empty и error не описывается здесь — это слой screen.

```yaml
tree:
  block-header:
    - ui:Sticky offset=top
      - ui:Row justify=between align=center gap=md wrap=true
        - ui:Search placeholder='Поиск исследований'
        - ui:Cluster gap=sm
          - ui:Button variant=ghost icon=filter label='Фильтры'
          - ui:Button variant=primary icon=plus label='Новое'
  block-body:
    - ui:Scroll axis=y
      - ui:DataList
          items: data:study
          columns:
            - { field: data:study.name,   label: 'Название' }
            - { field: data:study.date,   label: 'Дата' }
            - { field: data:study.status, label: 'Статус' }
            - { field: data:study.owner,  label: 'Владелец' }
          row-actions:
            - ui:Menu trigger=ui:IconButton(icon=more)
              items:
                - { label: 'Открыть',     trigger: 'open' }
                - { label: 'Архивировать', trigger: 'archive', variant: danger }
  block-footer:
    - ui:Row justify=between align=center
      - ui:Pagination
      - ui:Button variant=ghost label='Экспорт'
```
