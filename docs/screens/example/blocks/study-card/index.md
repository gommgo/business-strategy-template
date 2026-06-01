---
slug: study-card
name: 'Карточка исследования'
description: 'Полный блок: header+body+footer+aside, Grid+span+areas, slots-контейнер'
interface-block: study-card
ux-substrates:
  - card-meta
  - card-timeline
  - card-actions
  - card-related
data:
  study: data:study
slots: [details]
used-by-screens: [study-detail, study-detail-m]
status: draft
---

# study-card

Самый «толстый» блок — собирает все четыре internal-zones и
демонстрирует Grid с areas + span. Также объявляет собственный
slot `details` для вложенного блока, который вкладывается на уровне
screen-источника (например, специализированная card-вставка для
разных типов исследований).

Демонстрирует обе формы Grid: классическую (`columns=12` + `span=N`)
и areas-форму. В живом артефакте используется одна из двух, но для
наглядности показаны обе альтернативы.

```yaml
tree:
  block-header:
    - ui:Row justify=between align=center gap=md
      - ui:Stack gap=xs
        - ui:Text variant=h field=data:study.name
        - ui:Text variant=meta field=data:study.date
      - ui:Cluster gap=sm
        - ui:Button variant=ghost   icon=download label='Скачать'
        - ui:Button variant=danger  icon=archive  label='Архивировать'
  block-body:
    # Вариант 1: columns + span
    - ui:Grid columns=12 gap=md
      - ui:Cluster span=8
        - ui:Form
          - ui:Stack gap=md
            - ui:Field label='Название'  value=data:study.name
            - ui:Field label='Описание'  value=data:study.description
            - ui:Field label='Статус'    value=data:study.status
      - ui:Cluster span=4
        - slot: details
    # Вариант 2 (альтернатива той же раскладки): grid-template-areas
    # - ui:Grid
    #     areas:
    #       - [meta,     meta,     details]
    #       - [timeline, timeline, details]
    #       - [related,  related,  details]
    #     fill:
    #       meta:     ui:Form (... те же поля ...)
    #       timeline: ui:Stack ...
    #       related:  ui:Stack ...
    #       details:  { slot: details }
  block-aside:
    - ui:Stack gap=md
      - ui:Text variant=h-sub label='Хронология'
      - ui:Scroll axis=y
        - ui:DataList variant=timeline items=data:study.timeline
      - ui:Text variant=h-sub label='Связанные'
      - ui:DataList items=data:study.related compact=true
  block-footer:
    - ui:Row justify=end gap=sm
      - ui:Button variant=ghost   label='Назад'
      - ui:Button variant=primary label='Сохранить'
```
