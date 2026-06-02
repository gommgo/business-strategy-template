---
slug: confirm-archive
name: 'Подтверждение архивации'
description: 'Модалка-подтверждение поверх любого рабочего экрана'
shell: app-shell
blocks: [confirm-archive]
situations: [archive-study]
who: [doctor]
route: 'modal:confirm-archive'
viewport: any
entrypoint: false
transitions-to-screen: [studies-workspace, studies-list-m, study-detail, study-detail-m]
status: stable
---

# confirm-archive

Overlay-screen: один блок `confirm-archive` ложится в overlay-слот
поверх любого экрана-источника. `route` не URL, а именованный
view-marker (`modal:…`); все другие слоты пустуют — содержимое
наследуется от screen-источника (визуально это «диалог поверх
рабочего экрана»).

```yaml
slot-fills:
  header:  —
  side:    —
  main:    —
  detail:  —
  overlay: block:confirm-archive
  footer:  —
```
