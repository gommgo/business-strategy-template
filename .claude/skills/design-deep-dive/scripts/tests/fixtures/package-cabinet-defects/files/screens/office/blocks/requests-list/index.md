---
# иллюстрация: блок демо-кабинета фикстуры cabinet — для самопроверок утилит скилла, не данные проекта
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
status: stable
---

# requests-list

Список заявок с шапкой действий, табличным телом и пагинацией. Источник данных — общий с экраном: состояния загрузки,
пустоты и ошибки описывает экран `requests-list`.

```yaml
tree:
  block-header:
    - layout:row justify=between align=center gap=md:
        - layout:row gap=sm:
            - ui:SearchInput:
                - text:requests.list.search.placeholder
            - ui:Select items=data:request.status:
                - text:requests.list.status-filter.placeholder
        - ui:Button level=primary action=create:
            - icon:plus
            - text:requests.list.create.action
  block-body:
    - ui:Table items=data:request:
        columns:
          - {field: data:request.number, label: text:requests.list.number.column-header}
          - {field: data:request.client, label: text:requests.list.client.column-header}
          - {field: data:request.address, label: text:requests.list.address.column-header}
          - {field: data:request.visit-date, label: text:requests.list.visit-date.column-header}
          - {field: data:request.status, label: text:requests.list.status.column-header}
  block-footer:
    - ui:Pagination
```
