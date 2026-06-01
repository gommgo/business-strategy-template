---
slug: confirm-archive
name: 'Подтверждение архивации'
description: 'Overlay-блок: заголовок + текст + пара кнопок-действий'
interface-block: confirm-archive
ux-substrates:
  - archive-confirm
  - archive-cancel
used-by-screens: [confirm-archive]
status: stable
---

# confirm-archive

Overlay-блок (модалка-подтверждение). Кладётся в overlay-слот
`app-shell` через screen `confirm-archive`. Содержит только три зоны
без скролла и без data-binding (текст подтверждения — литерал).

```yaml
tree:
  block-header:
    - ui:Text variant=h-sub label='Архивировать исследование?'
  block-body:
    - ui:Text variant=body
        label: 'Исследование переместится в архив. Восстановить его можно через раздел "Архив".'
  block-footer:
    - ui:Row justify=end gap=sm
      - ui:Button variant=ghost  label='Отмена'
      - ui:Button variant=danger label='Архивировать'
```
