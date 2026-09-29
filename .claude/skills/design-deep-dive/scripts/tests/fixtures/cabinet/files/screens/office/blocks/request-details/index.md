---
# иллюстрация: блок демо-кабинета фикстуры cabinet — для самопроверок утилит скилла, не данные проекта
slug: request-details
name: 'Карточка заявки'
description: 'Данные заявки, назначение замера и отметка проведённого замера'
interface-block: request-details
ux-substrates:
  - request-fields
  - schedule-command
  - measured-command
data:
  item: data:request
source: screen
used-by-screens: [request-card]
status: stable
---

# request-details

Данные одной заявки по рангам атрибутов и две команды: менеджеру — назначить замер, замерщику — отметить проведённый.

```yaml
tree:
  block-header:
    - layout:row justify=between align=center gap=md:
        - text:requests.card.title.title
        - layout:row gap=sm:
            - ui:Button level=primary action=schedule:
                - text:requests.card.schedule.action
            - ui:Button level=secondary action=complete:
                - text:requests.card.complete.action
  block-body:
    - ui:DescriptionList items=data:request
```
