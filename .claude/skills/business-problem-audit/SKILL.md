---
name: business-problem-audit
description: Семантический аудит инвариантов методологии слоя `docs/business-problem/` (LinkedSWOT + Карта гипотез) роем агентов. Связи слоя НЕ валидируются slug-целостностью — они семантические, поэтому аудит запускает агентов параллельно, каждый под своим углом методологии: задача-сирота, гипотеза без метрики в «тогда», «потому что» не на мотивации субъекта, метрика-цель без влияющей гипотезы, целевая без guardrail, ставка не доведённая до карты, фактор без ставки, цель-с-цифрой/задача-вместо-цели, метрика-как-гарантия в frame, исполнитель-вместо-субъекта. Каждый агент читает слой + state и ищет смысловые нарушения, не grep. Не правит, только отчёт. Использовать перед коммитом артефактов business-problem, когда `/business-problem-deep-dive` предлагает прогон в конце сессии, перед `/cross-audit`, или когда аналитик подозревает разрыв методологии.
---

# business-problem-audit

Семантический аудит **инвариантов методологии** внутри
`docs/business-problem/` (LinkedSWOT + Карта гипотез). Канон —
`docs/business-problem/README.md`.

Связи слоя **не валидируются slug-целостностью** (они семантические, как
в project). Поэтому аудит **не grep'ит ссылки** — он запускает **рой
агентов**, каждый читает слой и спрашивает «соблюдён ли этот инвариант
методологии по смыслу». Это требует LLM, не регулярок.

`/cross-audit` ловит стыки **между слоями** (business ↔ business-problem
↔ project). Здесь — только инварианты **внутри** business-problem.
Аудит **читает и сообщает**, ничего не правит: правки — через
`/business-problem-deep-dive`.

## Точки входа

| вызов | поведение |
|---|---|
| `/business-problem-audit` | полный прогон всех применимых лучей |
| `/business-problem-audit <lens>` | один луч |
| `/business-problem-audit --quick` | 3 ключевых: `task-orphan`, `hypothesis-shape`, `metric-influence` |

`lens` ∈ {`task-orphan`, `hypothesis-shape`, `metric-influence`,
`guardrail`, `bet-promotion`, `factor-usage`, `goal-shape`,
`frame-guarantee`, `subject-selfmotion`}.

См. `references/rays.md`.

## Что делать при запуске

1. Прочитать `docs/business-problem/README.md` + `references/rays.md`.
2. Определить применимые лучи (по args или полный прогон). Луч,
   требующий пустого слоя (нет гипотез → `hypothesis-shape` нечего
   проверять), пропускается с пометкой.
3. **Спавнить агентов параллельно** — все вызовы в **одном**
   message-блоке. `subagent_type: general-purpose` (Read + Grep).
4. Собрать findings (единый JSON, см. `references/findings-format.md`).
5. Сгруппировать по лучам, отсортировать по severity.
6. Через `AskUserQuestion` пройти top-K findings: «принять корректным» /
   «нужна правка» / «false positive».
7. Перезаписать `audit-state/last-report.md` с reasoning-trace.

## Рой агентов

Каждый агент получает: путь к `docs/business-problem/`; свой lens;
инструкцию из `references/rays.md`; схему findings; relevant suppressions.

### Промпт-каркас

```
Lens: <name>
Слой: docs/business-problem/

Цель: проверить инвариант методологии семантически (не slug-валидация).
Прочитай нужные файлы слоя + state скилла business-problem-deep-dive
(если есть). Найди смысловые нарушения по паттернам этого луча.

Верни ТОЛЬКО валидный JSON-массив по схеме findings-format.md, без
preamble. Пусто → []. Не выдумывай findings ради чисел.
```

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | разрыв методологии, ломает карту | задача-сирота; «тогда» не бьёт в метрику; метрика-цель без влияющей гипотезы; метрика подана как гарантия |
| `warning` | подозрительное нарушение | целевая без guardrail; ставка не доведена до карты; «потому что» слабо связано с мотивацией |
| `hint` | повод подумать | фактор без ставки; очень короткая мотивация субъекта; цель близка к задаче |

## Формат отчёта

```
=== /business-problem-audit ===
Слой: business-problem · Лучи: 9 запущено, 9 ответили

[error] task-orphan → task:ab-reminders не привязана ни к одной гипотезе.
  Доказательство: task.hypothesis = «—»; в hypothesis.md нет записи,
    которую эта задача проверяет.
  Что делать: привязать к гипотезе через /business-problem-deep-dive
  task:ab-reminders, либо удалить задачу (ресурсный фильтр методологии).

[error] hypothesis-shape → hypothesis:remind-rebook.«тогда» не ссылается
  на метрику.
  Доказательство: so = «станет лучше»; metric = «—». Нечем оценить
    эффективность.
  Что делать: указать метрику в «тогда» через /business-problem-deep-dive.

[warning] guardrail → metric:paid-churn (целевая) без балансирующей.
  Доказательство: kind=lagging, direction=down; ни одной metric с
    kind=balancing на ту же goal:retain-paid.
  Что делать: завести guardrail (напр. удержать CAC) через
  /business-problem-deep-dive metric.

Сводка: 2 error / 1 warning / 0 hint.
```

После отчёта — `AskUserQuestion` по top-K (до 4 в раунде): «принять
корректным» / «нужна правка» (в next-actions, скилл **не вызывает**
deep-dive сам) / «false positive» (→ suppressions) / «обсудить позже».

## `audit-state/last-report.md`

Лежит рядом со скиллом, перезаписывается каждый прогон (не журнал, в git):

```markdown
---
ran-on: <scope>
lenses-run: 9
findings: { error: X, warning: Y, hint: Z }
verdicts: { accepted: A, needs-fix: B, false-positive: C, deferred: D }
---

# Reasoning trace
## Lens: task-orphan
- agent-id / duration / findings / verdicts / details
...
```

## Suppressions

Findings «false positive» → `audit-state/suppressions.md` (lens + pattern
+ reason + ts). Передаются агенту-лучу как контекст; он семантически не
генерирует подпадающие. Удаляются вручную, чтобы всплыли заново.

## Что не делать

- **Не править артефакты** — только отчёт; правки через
  `/business-problem-deep-dive`.
- **Не понижать `stable → draft`** — error в отчёте, аналитик понизит.
- **Не выдумывать findings** — пустой массив лучше натянутых.
- **Не делать кросс-слойную проверку** — это `/cross-audit`.
- **Не запускать рой повторно** в одной сессии.
- **Не вызывать `/business-problem-deep-dive`** автоматически.
- **Не предлагать клиенту** запустить аудит — это аналитический
  инструмент.
