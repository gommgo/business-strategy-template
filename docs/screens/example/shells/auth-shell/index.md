---
slug: auth-shell
name: 'Каркас экрана аутентификации'
description: 'Один центрированный main-слот; без header, sidebar, detail'
slots:
  main: { required: true, accepts: 'block | tree' }
status: stable
---

# auth-shell

Минимальная капсула для экранов до входа в систему. Один
центрированный слот; больше ничего нет.

```yaml
tree:
  - ui:AuthShell
    - ui:Main (fills: $main, centered=true)
```
