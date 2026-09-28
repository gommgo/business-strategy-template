---
name: hypothesis-map-audit
description: "Семантический аудит Карты гипотез в `docs/hypothesis-map/` роем агентов, по каждой проблеме бизнеса: проблема без цели, метрика как гарантия, форма цели и гипотезы, метрика без влияющей гипотезы и без guardrail, исполнитель на месте субъекта, задача-сирота. Лучи проверяют смысл, а не slug. Только отчёт, правки — через `/hypothesis-map-deep-dive`; `<business-problem-slug>` сужает прогон до проблемы, `<lens>` — до луча, `--quick` — четыре ключевых луча. Звать перед коммитом карты, по предложению `/hypothesis-map-deep-dive`, перед `/cross-audit` или при подозрении на разрыв причинной цепи."
---

# hypothesis-map-audit

Семантический аудит **инвариантов методологии Карты гипотез** внутри
`docs/hypothesis-map/` (`goal`, `metric`, `subject`, `hypothesis`, `task`).
Канон — `docs/hypothesis-map/README.md`.

Связи слоя **не валидируются slug-целостностью** (они семантические).
Поэтому аудит **не grep'ит ссылки** — он запускает **рой агентов**, каждый
читает слой и спрашивает «соблюдён ли этот инвариант методологии по
смыслу». Это требует LLM, не регулярок.

Слой **многопроблемный**: реестр проблем — `docs/business/business-problem.md`
(одна строка = одна проблема), каждая запись 5 kind несёт колонку `business-problem`
(массив строк реестра, M:N). **Все инварианты считаются в пределах одной
проблемы**: запись с проблемой P замыкается на записи той же P. Лучи
скоупятся **по строке реестра** (метрика без влияния, guardrail,
проблема-без-цели и т.п. — per-problem).

`/cross-audit` ловит стыки **между слоями** (hypothesis-map ↔ business ↔
swot ↔ ajtbd ↔ проекты). `/swot-audit` — инварианты LinkedSWOT. Здесь —
только инварианты **внутри** hypothesis-map (плюс проверка покрытия реестра
проблем целями и юр-рамки метрик). Аудит **читает и сообщает**, ничего не
правит: правки — через `/hypothesis-map-deep-dive`.

## Точки входа

| вызов | поведение |
|---|---|
| `/hypothesis-map-audit` | полный прогон всех применимых лучей по всем проблемам |
| `/hypothesis-map-audit <lens>` | один луч (по всем проблемам) |
| `/hypothesis-map-audit <business-problem-slug>` | все лучи, но только в пределах одной проблемы |
| `/hypothesis-map-audit --quick` | 4 ключевых: `problem-goal`, `task-orphan`, `hypothesis-shape`, `metric-influence` |

`lens` ∈ {`problem-tag`, `problem-goal`, `problem-guarantee`, `goal-shape`,
`metric-influence`, `guardrail`, `subject-selfmotion`, `hypothesis-shape`,
`task-orphan`}.

См. `references/rays.md`.

## Что делать при запуске

1. Прочитать `docs/hypothesis-map/README.md` + `references/rays.md`.
2. **Прочитать реестр проблем** `docs/business/business-problem.md` —
   перечислить проблемы (строки). Это контуры, по которым скоупятся лучи.
   Если задан `<business-problem-slug>` — ограничиться этой проблемой.
3. Определить применимые лучи (по args или полный прогон). Луч,
   требующий пустого слоя (нет гипотез → `hypothesis-shape` нечего
   проверять), пропускается с пометкой. Лучи `problem-goal`,
   `problem-guarantee` применимы, если в реестре есть хотя бы одна строка.
4. **Спавнить агентов параллельно** — все вызовы в **одном**
   message-блоке. `subagent_type: general-purpose` (Read + Grep). Каждому
   агенту передать список проблем и инструкцию считать инвариант
   **per-problem**.
5. Собрать findings (единый JSON, см. `references/findings-format.md`).
   Каждый finding несёт `business-problem`, в пределах которой найдено нарушение.
6. Сгруппировать по проблеме (внутри — по лучу), отсортировать по severity.
7. Через `AskUserQuestion` пройти top-K findings: «принять корректным» /
   «нужна правка» / «false positive».
8. Перезаписать `audit-state/last-report.md` с reasoning-trace.

## Рой агентов

Каждый агент получает: путь к `docs/hypothesis-map/`; реестр проблем
`docs/business/business-problem.md`; свой lens; список проблем; инструкцию
из `references/rays.md`; схему findings; relevant suppressions.

### Промпт-каркас

```
Lens: <name>
Слой: docs/hypothesis-map/ (Карта гипотез, многопроблемный)
Реестр проблем: docs/business/business-problem.md
Проблемы: [<business-problem-slug>, ...]   # или одна, если задан scope

Цель: проверить инвариант методологии Карты гипотез семантически (не
slug-валидация), по каждой проблеме отдельно. Каждая запись 5 kind несёт
колонку business-problem (массив строк реестра, M:N). Инвариант замыкается
внутри одной проблемы: запись с проблемой P учитывается вместе с записями
той же P.

Прочитай нужные файлы слоя + реестр проблем + ветку state слоя
hypothesis-map (`../entrypoint/state/hypothesis-map/`, если есть). Для
каждой проблемы из списка найди смысловые нарушения по паттернам этого
луча. В каждом finding укажи поле "business-problem".

Артефакты не правишь. Ответ — JSON-массив по схеме findings-format.md, без
текста вокруг: ответы лучей сводятся в один отчёт. Пустой массив [] —
нормальный результат; находки ради количества не нужны.
```

## Уровни тяжести

Все примеры считаются **в пределах одной проблемы**:

| severity | смысл | пример |
|---|---|---|
| `error` | разрыв методологии, ломает карту | проблема без цели; запись 5 kind с пустым/невалидным `business-problem`; задача-сирота; «тогда» не бьёт в метрику той же проблемы; метрика-цель без влияющей гипотезы; цель без метрики; метрика подана как гарантия |
| `warning` | подозрительное нарушение | целевая без guardrail в её проблеме; «потому что» слабо связано с мотивацией; позитивный субъект без сегмента (`segments` пуст; негативному сегмент не нужен); цель с цифрой внутри |
| `hint` | повод подумать | очень короткая мотивация субъекта; цель близка к задаче |

## Формат отчёта

Findings группируются по проблеме (строке реестра), внутри — по лучу:

```
=== /hypothesis-map-audit ===
Слой: hypothesis-map · Проблемы: 2 · Лучи: 9 запущено, 9 ответили

── Проблема: paid-outflow ──

[error] problem-goal → у проблемы paid-outflow нет ни одной цели.
  Доказательство: в goal.md ни одна запись не несёт paid-outflow в
    business-problem. Проблема повисла — нечего раскрывать в метрики.
  Что делать: завести goal с business-problem=[`paid-outflow`] через
  /hypothesis-map-deep-dive goal.

[error] task-orphan → task:ab-reminders не привязана ни к одной гипотезе.
  Доказательство: task.hypothesis = «—»; в hypothesis.md нет записи,
    которую эта задача проверяет.
  Что делать: привязать к гипотезе через /hypothesis-map-deep-dive
  task:ab-reminders, либо удалить задачу (ресурсный фильтр методологии).

[error] hypothesis-shape → hypothesis:remind-rebook «тогда» не ссылается
  на метрику.
  Доказательство: so = «станет лучше»; metric = «—». Нечем оценить
    эффективность.
  Что делать: указать метрику в «тогда» через /hypothesis-map-deep-dive.

[warning] guardrail → metric:paid-churn (целевая) без балансирующей.
  Доказательство: kind=lagging, direction=down; ни одной metric с
    kind=balancing на ту же goal:retain-paid в проблеме paid-outflow.
  Что делать: завести guardrail (напр. удержать CAC) через
  /hypothesis-map-deep-dive metric.

── Проблема: slow-onboarding ──

[warning] subject-selfmotion → subject:ops-lead без сегмента.
  Доказательство: subject.segments = «—». Субъект влияния не опёрт на
    сегмент рынка — мотивация может быть выдумана.
  Что делать: связать с ajtbd/segment через /hypothesis-map-deep-dive
  subject:ops-lead.

Сводка: 3 error / 2 warning / 0 hint (по 2 проблемам).
```

После отчёта — `AskUserQuestion` по top-K (до 4 в раунде): «принять
корректным» / «нужна правка» (в next-actions, скилл **не вызывает**
deep-dive сам) / «false positive» (→ suppressions) / «обсудить позже».

## `audit-state/last-report.md`

Лежит **рядом со скиллом**, перезаписывается каждый прогон (не журнал, в git):

```
.claude/skills/hypothesis-map-audit/audit-state/last-report.md
```

```markdown
---
ran-on: <scope>
problems: [<business-problem-slug>, ...]
lenses-run: 9
findings: { error: X, warning: Y, hint: Z }
verdicts: { accepted: A, needs-fix: B, false-positive: C, deferred: D }
---

# Reasoning trace
## Lens: task-orphan
- agent-id / duration / business-problem / findings / verdicts / details
...
```

## Suppressions

Findings «false positive» → `audit-state/suppressions.md` (lens + pattern
+ reason + ts). Передаются агенту-лучу как контекст; он семантически не
генерирует подпадающие. Удаляются вручную, чтобы всплыли заново.

## Границы

- **Только отчёт.** Правки — через `/hypothesis-map-deep-dive`, его
  запускает аналитик; `stable → draft` аудит не понижает — сообщает error.
- **Территория — внутри hypothesis-map** (плюс покрытие реестра проблем
  целями и юридическая рамка метрик). Стыки с business, swot, ajtbd и
  проектами (в т.ч. покрыта ли проблема проектом) сверяет `/cross-audit`,
  инварианты LinkedSWOT — `/swot-audit`.
- **Один рой за сессию.** Если findings много — проходить их постепенно.
- **Инструмент аналитика.** В клиент-режиме (`entrypoint-for-business`)
  аудит клиенту не предлагается.
