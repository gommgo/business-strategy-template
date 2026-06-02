---
slug: study-preview
name: 'Превью исследования'
description: 'Минимальный блок: только block-body с ключевыми полями'
interface-block: study-preview
ux-substrates:
  - preview-meta
  - preview-actions
data:
  study: data:study
used-by-screens: [studies-workspace]
status: draft
---

# study-preview

Минимальный пример блока — одна зона `block-body`. Шапки и футера
нет: блок предназначен для тесного detail-слота и сам не несёт
действий-шапки. Действия — внутри тела через `preview-actions`.

```yaml
tree:
  block-body:
    - ui:Pad gap=md
      - ui:Stack gap=md
        - ui:Text variant=h-sub field=data:study.name
        - ui:Row gap=md wrap=true
          - ui:Field label='Дата'    inline=true value=data:study.date
          - ui:Field label='Статус'  inline=true value=data:study.status
          - ui:Field label='Владелец' inline=true value=data:study.owner
        - ui:Row gap=sm
          - ui:Button variant=primary label='Открыть полностью'
          - ui:Button variant=ghost   icon=archive label='Архивировать'
```
