---
# иллюстрация: блок вольной записи фикстуры cabinet-freeform — для самопроверки нормализатора, не данные проекта
slug: requests-list
name: 'Список заявок'
description: 'Таблица заявок с поиском, фильтром по статусу, созданием и пагинацией'
interface-block: requests-list
ux-substrates:
  - requests-search
  - status-filter
  - requests-table
  - open-create
data:
  items: data:request
source: screen
collection:
  task: find
  volume: {typical: 60, max: 3000}
  filters: [status]
  sort: {by: visit-date, direction: desc}
  bulk: —
  narrow: priority-columns
used-by-screens: [requests-list]
status: draft
---

# requests-list

Блок в вольной записи: дерево по отступам, имена компонентов из aka, вид и размер кнопки, тексты литералами.

```yaml
tree:
  block-header:                # поиск, фильтр и создание
    - layout:row justify=between gap=md
      - ui:Search
      - ui:Dropdown items=data:request.status
      - ui:Button variant=accent size=lg action=create
        - icon:plus
        - 'Создать заявку'
  block-body:
    - ui:Table
        items: data:request
        columns:
          - {field: data:request.number, label: 'Номер'}
          - {field: data:request.client, label: 'Клиент'}
          - {field: data:request.status, label: 'Статус'}
  block-footer:
    - ui:Pagination
```
