---
slug: mobile-shell
name: 'Mobile-каркас'
description: 'Header + Main + Overlay; без sidebar и detail'
slots:
  header:  { required: true,  accepts: 'tree' }
  main:    { required: true,  accepts: 'block | tree' }
  overlay: { required: false, accepts: 'block (modal/drawer)' }
status: draft
---

# mobile-shell

Капсула для mobile-экранов: только шапка, основная область и overlay.
Без бокового и detail-слотов — на mobile эти роли выносятся в
отдельные screen и связаны через `flow`.

```yaml
tree:
  - ui:MobileShell
    - ui:Header (fills: $header)
    - ui:Main (fills: $main)
    - ui:OverlayLayer (fills: $overlay)
```
