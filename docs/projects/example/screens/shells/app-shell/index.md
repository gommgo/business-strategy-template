---
slug: app-shell
name: 'Основной каркас приложения'
description: 'Header + Sidebar + Main + Detail + Overlay + Footer; sidebar→drawer на xs/sm'
slots:
  header:  { required: true,  accepts: 'tree' }
  side:    { required: false, accepts: 'block | tree' }
  main:    { required: true,  accepts: 'block | tree' }
  detail:  { required: false, accepts: 'block' }
  overlay: { required: false, accepts: 'block (modal/drawer)' }
  footer:  { required: false, accepts: 'tree' }
responsive:
  xs:
    side:    drawer-via-burger
    detail:  stacked
    footer:  hidden
  sm:
    side:    drawer-via-burger
    detail:  overlay
    footer:  visible
  md:
    side:    visible
    detail:  visible
    footer:  visible
status: stable
---

# app-shell

Основная капсула рабочих экранов. На xs/sm sidebar уходит в drawer
под бургер-меню, detail сворачивается либо в стек ниже main, либо в
overlay. На md и выше — полная раскладка с двумя боковыми областями.

```yaml
tree:
  - ui:AppShell
    - ui:Header (fills: $header)
    - ui:Sidebar (fills: $side)
    - ui:Main (fills: $main)
    - ui:Detail (fills: $detail)
    - ui:OverlayLayer (fills: $overlay)
    - ui:Footer (fills: $footer)
```
