# Контекст project-слоя

Домены проекта живут **внутри** его папки (`<P>/domains/`, где
`<P>` = `docs/projects/<project-slug>`), рядом с продуктовым слоем
(`<P>/vision.md`, `<P>/capability.md`, …). Project описывает **продукт**
(capability/integration/constraint), domains — **бизнес-код бэкенда**
того же проекта. Семантическая связь есть, но **slug-валидаций нет** —
её ловит `/cross-audit`.

Связь всегда **внутрипроектная**: контекст/use-case/адаптер этого проекта
цепляется к capability/integration **этого же проекта**. Чужие проекты в
раунды связи не попадают.

## Маппинг

| domain | project | как использовать |
|---|---|---|
| контекст (`<ctx>/`) | `capability` (бизнес-возможность продукта) | контекст бэкенда обычно несёт одну+ capability. При заведении нового контекста — предложи опции = существующие capability + «технический контекст без capability» |
| aggregate / event / use-case | `capability` (более точный якорь) | use-case — реализация одной capability. При заведении use-case — предложи опции = существующие capability |
| адаптер / клиент в контексте | `integration` (внешняя система) | если контекст содержит код, ходящий во внешнюю систему — это адаптер integration. При заведении такого артефакта — предложи опции = существующие integration |
| технические контексты (auth, logging, audit) | — | допустимы без capability/integration — это инфра-домены. Не показывать связь |

## Когда показывать связь

### Заведение нового контекста

В сводке состояния, когда аналитик решает «завести новый контекст»:

```
AskUserQuestion:
header: "Какая capability реализуется этим контекстом"
options:
  - "capability:<slug-1>"
  - "capability:<slug-2>"
  - "Технический контекст (auth/audit/logging) — без capability"
  - Other
```

Запись — в README контекста (`<ctx>/README.md` секция «Ubiquitous
Language» или отдельный раздел «Связь с продуктом»). Свободный текст,
не frontmatter slug-ссылка.

### Заведение use-case

В режиме A — раунд связи:

```
AskUserQuestion:
header: "Какую capability реализует этот use-case"
options:
  - "capability:<slug-1>"
  - "capability:<slug-2>"
  - "Технический use-case (без capability)"
  - Other
```

Запись — в `state/<project-slug>/<ctx>/use-case/<Name>.md` секция
`## Доменные решения`:

```markdown
- Реализует capability:<slug>.
```

### Заведение адаптера / клиента

Когда заводится артефакт, описывающий взаимодействие с внешней
системой (имя содержит «client», «adapter», «provider»):

```
AskUserQuestion:
header: "Какую integration адаптирует"
options:
  - "integration:<slug-1>"
  - "integration:<slug-2>"
  - "Технический клиент (http/grpc/db) — без integration"
  - Other
```

Запись — в `state/<project-slug>/<ctx>/<kind>/<Name>.md`.

## Что делать, если продуктовый слой проекта пуст

Если `<P>/capability.md` отсутствует или нет нужных записей — раунд
связи **не задаётся**. Скилл продолжает обычный flow.

При закрытии сессии нового контекста — `AskUserQuestion`:

> «В продуктовом слое проекта нет capability, к которой можно прицепить
> этот контекст. Это ОК, но обычно бэкенд растёт под продуктовые
> capabilities. Открыть `/project-deep-dive <project-slug>`?»

## Если capability в project меняется

Если в state-заметке зафиксирована связь с `capability:X`, а в
`<P>/capability.md` эта запись удалена — это **разрыв связи**. Скилл при
следующем заходе:

1. Не молча удаляет.
2. `AskUserQuestion`: «Capability X удалена из project. Этот use-case
   теперь привязан к чему?» — опции: новая capability / технический /
   удалить use-case.

## Cross-audit

После каждой сессии скилл предлагает `/cross-audit` (lenses
`capability-domain`, `integration-domain`) — это поможет аналитику
увидеть, не остались ли capability без бизнес-кода или integration
без адаптера.
