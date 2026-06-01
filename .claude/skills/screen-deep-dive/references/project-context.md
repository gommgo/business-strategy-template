# Контекст project-слоя

Скилл `screen-deep-dive` живёт **на слой ниже** `docs/project/` и
**параллельно** с `docs/interface/`. Project описывает **продукт**
(surface/capability), screens — **визуальную композицию**
(flow/screen/block/shell). Семантическая связь есть, но
**slug-валидаций нет** — её ловит `/cross-audit`.

## Маппинг

| screens | project | как использовать |
|---|---|---|
| `flow` (поток экранов) | `surface` (где продукт работает) | каждый flow живёт на одной surface. При заведении flow — предложи опции = существующие surface |
| `flow` | `capability` (бизнес-возможность) | flow реализует одну+ capability (например, flow «онбординг» = capability «зарегистрироваться»). При заведении flow — раунд после связи с surface |
| `screen` | `capability` (точечно, опционально) | screen может быть якорной точкой capability. Чаще capability — на уровне flow |
| `shell` (каркас навигации) | `surface` (на какой surface висит каркас) | при заведении shell — предложи опции = существующие surface |
| `block` | — (опционально привязать к persona через interface.who) | блок переиспользуется — обычно не имеет прямой связи с project |

## Когда показывать связь

### Заведение `flow`

В режиме A (новая сущность):

1. После раунда фундамента (slug/name/description) — раунд связи с
   surface:

   ```
   AskUserQuestion:
   header: "На какой surface живёт flow"
   options:
     - "surface:<slug-1>" (type)
     - "surface:<slug-2>" (type)
     - Other
   ```

2. После — раунд связи с capability:

   ```
   AskUserQuestion:
   header: "Какую capability реализует flow"
   options:
     - "capability:<slug-1>"
     - "capability:<slug-2>"
     - "Несколько capability (выберу позже)"
     - Other
   ```

3. Запись — в `state/flow/<slug>.md`:

   ```markdown
   ## Доменные решения
   - Surface: surface:web-partner
   - Реализует capability: send-referral
   ```

### Заведение `screen`

В режиме A — опциональный раунд связи (screen наследует surface от
flow):

```
AskUserQuestion:
header: "Этот screen — якорь одной capability"
options:
  - "Да, основной screen для capability:<slug>"
  - "Нет, вспомогательный (без явной capability)"
  - Other
```

### Заведение `shell`

В режиме A — раунд связи:

```
AskUserQuestion:
header: "На какой surface висит shell"
options:
  - "surface:<slug-1>"
  - "surface:<slug-2>"
  - "Общий shell (для всех web-поверхностей)"
  - Other
```

## Что делать, если project-слой пуст

Если `docs/project/` отсутствует или нет нужных surface/capability —
раунд связи **не задаётся**. Скилл продолжает обычный flow.

При закрытии сессии — `AskUserQuestion`:

> «Не вижу `docs/project/` с surface и capability. Без них screens
> "плавают в воздухе". Открыть `/project-deep-dive`?»

## Cross-audit

После каждой сессии скилл предлагает `/cross-audit` (lenses
`surface-screen`) — это покажет surface без экранов и экраны без
surface.
