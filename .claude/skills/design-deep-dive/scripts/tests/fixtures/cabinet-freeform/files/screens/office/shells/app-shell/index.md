---
# иллюстрация: каркас вольной записи фикстуры cabinet-freeform — для самопроверки нормализатора, не данные проекта
slug: app-shell
name: 'Основной каркас кабинета'
description: 'Шапка с поиском и помощью, навигация по разделам, основное содержимое и оверлей'
slots:
  main:    { required: true,  accepts: 'block | tree', landmark: main }
  overlay: { required: false, accepts: 'block (modal/drawer)', landmark: — }
status: draft
---

# app-shell

Каркас в вольной записи: дерево по отступам без двоеточий, слоты — «(fills: …)», шапка — именем из aka.

```yaml
tree:
  - layout:stack
    - ui:Navbar
      - ui:SearchInput
      - ui:Link
        - text:app.shell.help.link
    - layout:row
      - ui:Sidebar items=nav
      - layout:stack           (fills: $main)
    - layout:layer             (fills: $overlay)
```

## Состояния приложения

| состояние | где видно | форма | тексты |
|---|---|---|---|
| `service-unavailable` | под шапкой, над всеми слотами | баннер | `text:app.shell.service-unavailable.banner` |
| `maintenance` | под шапкой | баннер заранее, за сутки до работ | `text:app.shell.maintenance.banner` |
| `session-expiry` | слот `overlay` | модальное окно с продлением — заранее, а не после | `text:app.shell.session-expiry.confirm-title`, `text:app.shell.session-expiry.action` |
| `connection-lost` | под шапкой | баннер, введённое сохраняется | `text:app.shell.connection-lost.banner` |
| `demo-mode` | не применимо: демо-режима у кабинета нет | — | — |
