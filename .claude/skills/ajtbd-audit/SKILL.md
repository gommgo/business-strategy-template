---
name: ajtbd-audit
description: "Семантический аудит Advanced JTBD в `docs/ajtbd/` роем агентов, по каждому сегменту: бандл с одной Big Job, непрерывность «чтобы», Core-работа с нанятым решением, трение на паре «решение + работа», вычислимый Score у stable-сегмента, CPR без разрывов, ложные работы, сироты, трение клиента под видом проблемы бизнеса. Лучи проверяют смысл, а не slug. Только отчёт, правки — через `/segment-deep-dive` и `/job-graph-deep-dive`; `<segment-slug>` сужает прогон до сегмента, `<lens>` — до луча. Звать перед коммитом ajtbd, перед `/cross-audit` или при подозрении на разрыв графа работ."
---

# ajtbd-audit

Семантический аудит **инвариантов методологии** внутри `docs/ajtbd/`
(Advanced JTBD: сегменты по работам + граф работ). Канон —
`docs/ajtbd/README.md` § «Связи и методологические инварианты».

Связи слоя **не валидируются slug-целостностью** (они семантические, как
в business-problem и project). Поэтому аудит **не grep'ит ссылки** — он
запускает **рой агентов**, каждый читает слой и спрашивает «соблюдён ли
этот инвариант методологии по смыслу». Это требует LLM, не регулярок.

Слой держится на **сегментах**: `segment.md` — таблица сегментов (одна
строка = один сегмент), у каждого свой бандл работ (Core Jobs + одна Big
Job). **Граф работ (job · job-graph · solution · segment-problem)
собирается внутри одного сегмента.** Поэтому большинство инвариантов
считаются **в пределах одного сегмента**: работа / решение / трение / граф
с сегментом S замыкаются на сущности того же S. Лучи скоупятся **по
строке `segment`** — луч проверяет инвариант внутри сегмента, не через
весь слой скопом.

`/cross-audit` ловит стыки **между слоями** (ajtbd ↔ business ↔
business-problem ↔ проекты `docs/projects/<slug>/`). Здесь — только
инварианты **внутри** ajtbd. Аудит **читает и сообщает**, ничего не
правит: правки — через `/segment-deep-dive` (сегменты и Score) и
`/job-graph-deep-dive` (работы, решения, трения, граф).

## Точки входа

| вызов | поведение |
|---|---|
| `/ajtbd-audit` | полный прогон всех применимых лучей по всем сегментам |
| `/ajtbd-audit <lens>` | один луч (по всем сегментам) |
| `/ajtbd-audit <segment-slug>` | все лучи, но только в пределах одного сегмента |
| `/ajtbd-audit --quick` | 4 ключевых: `segment-bundle`, `so-that-chain`, `problem-pair`, `graph-cpr` |

`lens` ∈ {`segment-bundle`, `so-that-chain`, `job-segment`,
`core-solution`, `problem-pair`, `score-computable`, `graph-cpr`,
`false-job`, `orphan-refs`, `layer-mixup`}.

См. `references/rays.md`.

## Что делать при запуске

1. Прочитать `docs/ajtbd/README.md` + `references/rays.md`.
2. **Прочитать таблицу `segment.md`** — перечислить сегменты (строки). Это
   контуры, по которым скоупятся лучи. Если задан `<segment-slug>` —
   ограничиться этим сегментом.
3. Определить применимые лучи (по args или полный прогон). Луч,
   требующий пустого набора (нет графов → `graph-cpr` нечего проверять;
   нет трений → `problem-pair`; нет Core-работ → `core-solution`),
   пропускается с пометкой. Лучи `segment-bundle` применимы, если в
   `segment` есть хотя бы одна строка.
4. **Спавнить агентов параллельно** — все вызовы в **одном**
   message-блоке. Спавн через `Agent` tool, **subagent_type:
   general-purpose** (Read + Grep). Каждому агенту передать список
   сегментов и инструкцию считать инвариант **per-segment** (сущности с
   сегментом S замыкаются на сущности того же S).
5. Собрать findings (единый JSON, см. `references/findings-format.md`).
   Каждый finding несёт `segment`, в пределах которого найдено нарушение.
6. Сгруппировать по сегменту, внутри — по лучу, отсортировать по severity.
7. Через `AskUserQuestion` пройти top-K findings: «принять корректным» /
   «нужна правка» / «false positive».
8. Перезаписать `audit-state/last-report.md` с reasoning-trace.

## Рой агентов

Каждый агент получает: путь к `docs/ajtbd/`; свой lens; список сегментов
(строк `segment.md`); инструкцию из `references/rays.md`; схему findings;
relevant suppressions. Спавн — через `Agent` tool, **subagent_type:
general-purpose**, чтобы агент мог `Read` файлы слоя и `Grep` для быстрых
проверок упоминаний. Все агенты — в **одном** message-блоке для
параллельности.

### Промпт-каркас

```
Lens: <name>
Слой: docs/ajtbd/ (сегменты + граф работ Advanced JTBD)
Сегменты (строки segment.md): [<segment-slug>, ...]   # или один, если задан scope

Цель: проверить инвариант методологии семантически (не slug-валидация),
по каждому сегменту отдельно. Граф работ собирается внутри одного
сегмента: работа/решение/трение/граф с сегментом S учитываются вместе с
сущностями того же S. Связи семантические — решай по смыслу, не по
строковому совпадению.

Прочитай нужные файлы слоя (segment.md, job.md, job-graph.md, solution.md,
segment-problem.md) + ветку state слоя ajtbd (`../entrypoint/state/ajtbd/`,
если есть). Для каждого сегмента из списка найди смысловые нарушения по
паттернам этого луча. В каждом finding укажи поле "segment".

Артефакты не правишь. Ответ — JSON-массив по схеме findings-format.md, без
текста вокруг: ответы лучей сводятся в один отчёт. Пустой массив [] —
нормальный результат; находки ради количества не нужны.
```

## Уровни тяжести

Все примеры считаются **в пределах одного сегмента**:

| severity | смысл | пример |
|---|---|---|
| `error` | разрыв методологии, ломает карту спроса | сегмент без Big Job или с несколькими; работа без segment; разрыв «чтобы» (so-that ≠ want родителя); Core-работа без решения с оценками; segment-problem без пары solution+job; Score stable-сегмента не вычислим; граф без CPR / с разрывом / без разметки type; работа-сирота; ссылка на несуществующую сущность; segment-problem подан как проблема бизнеса |
| `warning` | подозрительное нарушение | подозрение на ложную работу без пометки type=ложная; strength трения без обоснования; оценки решения «на глаз»; «pain»/«боль» вместо недостижимого результата; solution как наш будущий продукт |
| `hint` | повод подумать | сегмент описан демографией, а не бандлом работ; работа похожа на задачу/фичу/шаг интерфейса |

## Формат отчёта

Findings группируются по сегменту, внутри — по лучу:

```
=== /ajtbd-audit ===
Слой: ajtbd · Сегменты: 2 · Лучи: 10 запущено, 10 ответили

── Сегмент: dacha-owner ──

[error] segment-bundle → у сегмента dacha-owner две Big Job.
  Доказательство: segment.md:dacha-owner big-job = `enjoy-outdoors`, но в
    core-jobs затесалась `feel-free` с job.level=big. Сегмент держится на
    ровно одной Big Job.
  Что делать: оставить одну big-job, лишнюю вынести в отдельный сегмент
  или понизить уровень — через /segment-deep-dive dacha-owner.

[error] so-that-chain → job:buy-gear «чтобы» рвёт цепочку вверх.
  Доказательство: buy-gear.so-that = «остаться сухим»; parent-job =
    plan-trip, у которого want = «спланировать маршрут» — so-that нижней
    работы не совпадает с want верхней. Цепочка не доходит до
    big-job enjoy-outdoors.
  Что делать: выправить so-that/parent-job через /job-graph-deep-dive
  dacha-owner (so-that = want родителя, цепочка → big-job).

[error] core-solution → core-работа buy-gear без нанятого решения с
  оценками.
  Доказательство: ни одно solution.hired-for не содержит buy-gear (или
    содержит, но satisfaction/price-value-fit = «—»). Score сегмента не
    вычислить.
  Что делать: завести нанятое решение с оценками через /job-graph-deep-dive
  dacha-owner.

── Сегмент: contractor ──

[error] problem-pair → segment-problem:slow-quotes без пары solution+job.
  Доказательство: solution = «—», job = `make-estimate`. Трение без
    нанятого решения — нарушение ядра «проблема — следствие решения».
  Что делать: указать нанятое решение через /job-graph-deep-dive contractor
  segment-problem:slow-quotes.

Сводка: 4 error / 0 warning / 0 hint (по 2 сегментам).
```

После отчёта — `AskUserQuestion` по top-K (до 4 в раунде): «принять
корректным» / «нужна правка» (в next-actions, скилл **не вызывает**
deep-dive сам) / «false positive» (→ suppressions) / «обсудить позже».

## `audit-state/last-report.md`

Лежит рядом со скиллом, перезаписывается каждый прогон (не журнал, в git):

```markdown
---
ran-on: <scope>
segments: [<segment-slug>, ...]
lenses-run: 10
findings: { error: X, warning: Y, hint: Z }
verdicts: { accepted: A, needs-fix: B, false-positive: C, deferred: D }
---

# Reasoning trace
## Lens: so-that-chain
- agent-id / duration / segment / findings / verdicts / details
...
```

## Suppressions

Findings «false positive» → `audit-state/suppressions.md` (lens + segment
+ pattern + reason + ts). Suppression несёт `segment` (для лучей без
сегментного контекста — `segment: —`), чтобы подавление в одном сегменте
не глушило тот же паттерн в другом. Передаются агенту-лучу как контекст;
он семантически не генерирует подпадающие. Удаляются вручную, чтобы
всплыли заново.

## Границы

- **Только отчёт.** Правки — через `/segment-deep-dive` (сегменты и Score)
  и `/job-graph-deep-dive` (работы, решения, трения, граф), их запускает
  аналитик. `stable → draft` аудит не понижает: сообщает error, понижает
  аналитик.
- **Территория — внутри ajtbd.** Стыки с business, business-problem
  (`segment-problem` → `business/business-problem`, `segment` → `subject`,
  `value-mechanics` → `capability`) и проектами `docs/projects/<slug>/`
  сверяет `/cross-audit`. Луч `layer-mixup` ловит только **путаницу слоёв
  изнутри** (трение клиента, поданное как проблема бизнеса) и читает
  `business-problem.md` лишь для контраста, не как источник findings.
- **Проспективный сегмент** (`served=prospective`) — нормальная разведка
  рынка, который бизнес ещё не обслуживает: без обслуживающих оферов и
  каналов он валиден и находкой не является.
- **Один рой за сессию.** Если findings много — проходить их постепенно.
- **Инструмент аналитика.** В клиент-режиме (`entrypoint-for-business`)
  аудит клиенту не предлагается.

## Что дальше (next-actions)

Аудит сам ничего не правит и скилы не вызывает — в конце отчёта предлагает
аналитику руками:

- по находкам сегментов/Score — `/segment-deep-dive <segment-slug>`;
- по находкам работ / решений / трений / графа —
  `/job-graph-deep-dive <segment-slug>`;
- для межслойной проверки (ajtbd ↔ business ↔ business-problem ↔ проекты)
  — `/cross-audit`.
