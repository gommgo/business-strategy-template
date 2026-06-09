# Контекст project-слоя

Домены проекта живут **внутри** его папки (`<P>/domains/`, где
`<P>` = `docs/projects/<project-slug>`), рядом с продуктовым слоем
(`<P>/vision.md`, `<P>/capability/<surface>.md`, `<P>/integration.md`, …).
Project описывает **продукт** (capability/integration/constraint), domains
— **бизнес-код бэкенда** того же проекта. Семантическая связь есть, но
**slug-валидаций нет** — её ловит `/cross-audit`.

Домены остаются по bounded-context и **surface-агностичны**: бэкенд не
партиционируется по поверхности (surface) — одна доменная модель обслуживает
все поверхности продукта. Поверхность входит в домен только через `Channel`
use-case'а (`HTTP API …`) и через внешние/межпроектные интеграции (см. ниже).
Возможности же (capability), наоборот, лежат **по поверхности** —
`<P>/capability/<surface>.md`, файл на поверхность. Use-case реализует
возможность той или иной поверхности.

Связь бывает двух родов:

- **внутрипроектная** — контекст/use-case/адаптер этого проекта цепляется к
  возможности (capability) или интеграции (integration) **этого же проекта**;
- **межпроектная** — порт/событие use-case'а обменивается с **соседним
  проектом** того же бизнеса; это интеграция с `target: sibling-project`,
  ребро которой сводится в `docs/projects/project-map.md`.

## Маппинг

Возможности (capability) лежат **по поверхности**: продуктовый слой —
`<P>/capability/<surface>.md` (файл на поверхность из реестра `surface.md`).
Один use-case реализует возможность той или иной поверхности; кандидаты для
раунда связи собираются **по всем файлам** `<P>/capability/*.md`.

| domain | project | как использовать |
|---|---|---|
| контекст (`<ctx>/`) | возможность (`capability/<surface>.md`) | контекст бэкенда (surface-агностичный) обычно несёт одну+ возможность одной или нескольких поверхностей. При заведении нового контекста — предложи опции = существующие capability из всех `<P>/capability/*.md` + «технический контекст без capability» |
| aggregate / event / use-case | возможность (`capability/<surface>.md`, более точный якорь) | use-case — реализация одной возможности поверхности. При заведении use-case — предложи опции = существующие capability из всех `<P>/capability/*.md` |
| адаптер / клиент в контексте | `integration` (внешняя система или соседний проект) | если контекст содержит код, ходящий во внешнюю систему **или** к соседнему проекту бизнеса — это адаптер/порт интеграции. При заведении такого артефакта — предложи опции = существующие записи `<P>/integration.md`. Выбранная интеграция заполняет колонку `integration` в use-case `## Dependencies` |
| технические контексты (auth, logging, audit) | — | допустимы без capability/integration — это инфра-домены. Не показывать связь |

## Когда показывать связь

### Заведение нового контекста

В сводке состояния, когда аналитик решает «завести новый контекст».
Опции собираются из возможностей всех поверхностей (`<P>/capability/*.md`):

```
AskUserQuestion:
header: "Какая capability реализуется этим контекстом"
options:
  - "capability:<slug-1>  (поверхность <surface>)"
  - "capability:<slug-2>  (поверхность <surface>)"
  - "Технический контекст (auth/audit/logging) — без capability"
  - Other
```

Запись — в README контекста (`<ctx>/README.md` секция «Ubiquitous
Language» или отдельный раздел «Связь с продуктом»). Свободный текст,
не frontmatter slug-ссылка. Контекст surface-агностичен: одна доменная
модель может нести возможности разных поверхностей.

### Заведение use-case

В режиме A — раунд связи (возможности из всех `<P>/capability/*.md`):

```
AskUserQuestion:
header: "Какую capability реализует этот use-case"
options:
  - "capability:<slug-1>  (поверхность <surface>)"
  - "capability:<slug-2>  (поверхность <surface>)"
  - "Технический use-case (без capability)"
  - Other
```

Запись — в `state/<project-slug>/<ctx>/use-case/<Name>.md` секция
`## Доменные решения`:

```markdown
- Реализует capability:<slug> (поверхность <surface>).
```

### Заведение адаптера / клиента / порта

Когда заводится артефакт или порт в `## Dependencies`, описывающий
взаимодействие с **внешней системой** или с **соседним проектом** бизнеса
(имя содержит «client», «adapter», «provider», «port»; либо порт `## Dependencies`
ведёт наружу из кода):

```
AskUserQuestion:
header: "Какую integration адаптирует / к чему ходит порт"
options:
  - "integration:<slug-1>  (target external)"
  - "integration:<slug-2>  (target sibling-project → <project>)"
  - "Внутренняя инфра (репозиторий / Clock / reader другого контекста этого проекта) — без integration"
  - Other  ← нужна новая запись integration
```

Опции собираются из `<P>/integration.md`. Выбранная интеграция:

1. **заполняет колонку `integration`** в use-case `## Dependencies` (slug
   записи в бэктиках); для внутренней инфры колонка остаётся `—`;
2. фиксируется в `state/<project-slug>/<ctx>/<kind>/<Name>.md`.

Если нужной записи в `<P>/integration.md` ещё нет (выбрано Other) — это
**аналитический пробел продуктового слоя**: домен ссылается на интеграцию,
которой нет. Зафиксируй `**blocker**`-вопрос в state-заметке use-case
(«порт `<port>` ходит наружу, а записи integration нет — завести через
`/project-deep-dive <project-slug>`») и оставь колонку с предложенным
slug'ом до заведения. Скилл доменов **не** пишет в `<P>/integration.md` —
это зона `/project-deep-dive`.

### Межпроектный порт / событие (`target: sibling-project`)

Если порт use-case'а — это HTTP-клиент к API **соседнего проекта** бизнеса
(синхронно) или подписка `consumes` на его событие (асинхронно), либо
событие use-case'а потребляет соседний проект:

- запись integration имеет `target: sibling-project` и `sibling-project` →
  slug соседнего проекта;
- колонка `integration` в `## Dependencies` ссылается на эту запись;
- **ребро стыка** сводится в `docs/projects/project-map.md` (с `via:`
  `` `integration:<slug>` ``, `` `event:<name>` `` или `` `domain-port:<ctx>.<Op>` ``).

Скилл доменов авторит **только** колонку `integration` в use-case'е и
state-заметку. Запись `integration.md` и ребро `project-map.md` ведёт
`/project-deep-dive`; согласованность трёх сторон (порт ↔ integration ↔
project-map) сверяет `/cross-audit`. Если соседнего проекта или ребра
нет — `**blocker**`-вопрос в state-заметке.

## Что делать, если продуктовый слой проекта пуст

Если папка `<P>/capability/` отсутствует или ни в одном файле
`<P>/capability/*.md` нет нужных записей — раунд связи **не задаётся**.
Скилл продолжает обычный flow.

При закрытии сессии нового контекста — `AskUserQuestion`:

> «В продуктовом слое проекта нет capability, к которой можно прицепить
> этот контекст. Это ОК, но обычно бэкенд растёт под продуктовые
> capabilities. Открыть `/project-deep-dive <project-slug>`?»

## Если capability в project меняется

Если в state-заметке зафиксирована связь с `capability:X`, а ни в одном
файле `<P>/capability/*.md` этой записи больше нет — это **разрыв связи**
(возможность могла быть удалена или переехать на другую поверхность —
файл `capability/<surface>.md` сменился). Скилл при следующем заходе:

1. Не молча удаляет.
2. `AskUserQuestion`: «Capability X удалена из project. Этот use-case
   теперь привязан к чему?» — опции: новая capability / технический /
   удалить use-case.

## Cross-audit

После каждой сессии скилл предлагает `/cross-audit` (lenses
`capability-domain`, `integration-domain`) — это поможет аналитику
увидеть, не осталась ли возможность (capability) поверхности без
бизнес-кода или интеграция (integration) без адаптера. Для межпроектных
портов `/cross-audit` сверяет три стороны: колонка `integration` в
use-case `## Dependencies` ↔ запись `<P>/integration.md`
(`target: sibling-project`) ↔ ребро `docs/projects/project-map.md`.
