---
# иллюстрация: блок демо-кабинета фикстуры cabinet — для самопроверок утилит скилла, не данные проекта
slug: plan-tile
name: 'План месяца'
description: 'Плитка «проведено замеров против плана месяца» со своим источником данных'
interface-block: plan-tile
ux-substrates:
  - plan-progress
data:
  item: data:plan
source: own
tiles:
  - value: data:plan.done
    question: 'сколько замеров проведено против плана месяца'
    precision: 'целое'
    baseline: 'план месяца'
    good: up
    thresholds: '<пороги от заказчика>'
    delta: 'разница с планом на сегодня'
    period: 'месяц, обновление раз в час'
    link: requests-list
    action: —
    no-data: text:plan.dashboard.plan-tile.empty
used-by-screens: [plan-dashboard]
status: stable
---

# plan-tile

Плитка плана: проведено замеров за месяц против плана. Источник — свой, поэтому загрузка и ошибка плитки — в её
разделе `states`.

```yaml
tree:
  block-body:
    - ui:KpiTile value=data:plan.done

states:
  loading-initial:
    block-body:
      - ui:Skeleton
  error-load:
    block-body:
      - ui:Alert:
          - text:plan.dashboard.plan-tile-error.inline-message
```
