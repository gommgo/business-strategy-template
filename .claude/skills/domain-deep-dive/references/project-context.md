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
| клиент интеграции (`_shared/integrations/<slug>/`) | `integration` (провайдер) + его функции | если код ходит во внешнюю систему **или** к соседнему проекту — это **клиент интеграции** в `_shared/integrations/<integration-slug>/` (kind `integration-client`): транспорт + функции с `slug` + ошибки. Use-case дёргает функции по `slug` (колонки `integration` + `functions` в `## Dependencies`), **не зная транспорта**. При заведении — предложи опции = провайдеры из `<P>/integration.md` |
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

### Заведение клиента интеграции и потребления функций

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

Опции — провайдеры из `<P>/integration.md`. Выбранная интеграция тянет
**второй раунд** — какие функции use-case дёргает (опции = функции этого
провайдера из `## Функции` `integration.md`; Other — нужна новая функция).

Выбор фиксируется на двух уровнях:

1. **use-case `## Dependencies`** — колонка `integration` = slug провайдера
   (в бэктиках; внутренняя инфра — `—`), колонка `functions` =
   `` [`<integration>.<fn-slug>`, …] `` (дёрнутые функции; для инфры — `—`);
2. **клиент `_shared/integrations/<integration-slug>/README.md`**
   (`kind: integration-client`) — конкретное воплощение: транспорт, та же
   функция со `slug`, сигнатура, ошибки. Если клиента ещё нет — завести из
   шаблона `_templates/integration-client.md`. Домен зовёт функцию по `slug`,
   **транспорт держит только клиент** (HTTP/gRPC/очередь — домен не знает);
3. фиксируется в `state/<project-slug>/<ctx>/<kind>/<Name>.md`.

Скилл доменов авторит use-case (`integration` + `functions`) и клиент
`_shared/`. Бизнес-каталог `integration.md` (провайдеры + `## Функции` с
бизнес-описанием) ведёт `/project-deep-dive` — **не** этот скилл.

Если нужного **провайдера** или **функции** в `<P>/integration.md` ещё нет
(выбрано Other) — это **аналитический пробел продуктового слоя**: домен
ссылается на то, чего нет. Зафиксируй `**blocker**`-вопрос в state-заметке
use-case («порт `<port>` дёргает функцию `<fn>`, а её/провайдера нет в
`integration.md` — завести через `/project-deep-dive <project-slug>`») и
оставь колонки с предложенными slug'ами до заведения.

### Межпроектный порт / событие (`target: sibling-project`)

Если порт use-case'а — это HTTP-клиент к API **соседнего проекта** бизнеса
(синхронно) или подписка `consumes` на его событие (асинхронно), либо
событие use-case'а потребляет соседний проект:

- запись integration имеет `target: sibling-project` и `sibling-project` →
  slug соседнего проекта;
- колонки `integration` + `functions` в `## Dependencies` ссылаются на эту
  запись и её функции (outbound — мы зовём функцию соседа; inbound — сосед
  зовёт нашу, тогда это наш use-case с соответствующим `Actor`);
- **ребро стыка** сводится в `docs/projects/project-map.md` на бизнес-языке
  (с `via:` `` `integration:<slug>` ``, `` `event:<name>` `` или
  `` `domain-port:<ctx>.<Op>` ``; функции/сигнатуры в карту **не** уезжают).

Скилл доменов авторит use-case (`integration` + `functions`), клиент
`_shared/` и state-заметку. Бизнес-каталог `integration.md` и ребро
`project-map.md` ведёт `/project-deep-dive`; согласованность сторон
(функция в use-case ↔ функция клиента `_shared/` ↔ `## Функции`
`integration.md` ↔ ребро `project-map` ↔ обслуживающий use-case соседа)
сверяет `/cross-audit`. Если соседнего проекта или ребра нет —
`**blocker**`-вопрос в state-заметке.

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
бизнес-кода, функция интеграции без клиента/потребителя или интеграция
без клиента. Для межпроектных портов `/cross-audit` сверяет цепочку:
`functions` в use-case `## Dependencies` ↔ функция клиента
`_shared/integrations/<slug>/` ↔ `## Функции` `<P>/integration.md`
(`target: sibling-project`) ↔ ребро `docs/projects/project-map.md` ↔
обслуживающий use-case у соседа.
