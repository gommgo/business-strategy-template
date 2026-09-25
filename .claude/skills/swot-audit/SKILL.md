---
name: swot-audit
description: "Семантический аудит инвариантов методологии LinkedSWOT в `docs/swot/` (factor · bet) роем агентов, по каждой проблеме реестра `docs/business/business-problem.md` отдельно: привязка записей к проблемам, квадрант фактора, фактор без ставки, баланс факторов ставки, «чтобы» у ставки и её доведённость до Карты гипотез. Связи слоя семантические, поэтому каждый луч проверяет смысл, а не slug. Артефакты не правит, только отчёт; `<business-problem-slug>` сужает прогон до одной проблемы. Использовать перед коммитом артефактов swot, когда `/swot-deep-dive` предлагает прогон в конце сессии, перед `/cross-audit` или при подозрении на разрыв методологии LinkedSWOT."
---

# swot-audit

Семантический аудит **инвариантов методологии LinkedSWOT** внутри
`docs/swot/` (`factor`, `bet`). Канон — `docs/swot/README.md`.

Связи слоя **не валидируются slug-целостностью** (они семантические).
Поэтому аудит **не grep'ит ссылки** — он запускает **рой агентов**, каждый
читает слой и спрашивает «соблюдён ли этот инвариант методологии по
смыслу». Это требует LLM, не регулярок.

Слой **многопроблемный**: реестр проблем — `docs/business/business-problem.md`
(одна строка = одна проблема), каждая запись `factor`/`bet` несёт колонку
`business-problem` (массив строк реестра, M:N). **Все инварианты считаются в
пределах одной проблемы**: запись с проблемой P замыкается на записи той
же P. Лучи скоупятся **по строке реестра** (фактор без ставки,
доведённость ставки и т.п. — per-problem).

`/cross-audit` ловит стыки **между слоями** (swot ↔ business ↔ ajtbd ↔
проекты). `/hypothesis-map-audit` — инварианты Карты гипотез. Здесь —
только инварианты **внутри** swot. Аудит **читает и сообщает**, ничего не
правит: правки — через `/swot-deep-dive`.

## Точки входа

| вызов | поведение |
|---|---|
| `/swot-audit` | полный прогон всех применимых лучей по всем проблемам |
| `/swot-audit <lens>` | один луч (по всем проблемам) |
| `/swot-audit <business-problem-slug>` | все лучи, но только в пределах одной проблемы |

`lens` ∈ {`problem-tag`, `factor-usage`, `bet-promotion`}.

См. `references/rays.md`.

## Что делать при запуске

1. Прочитать `docs/swot/README.md` + `references/rays.md`.
2. **Прочитать реестр проблем** `docs/business/business-problem.md` —
   перечислить проблемы (строки). Это контуры, по которым скоупятся лучи.
   Если задан `<business-problem-slug>` — ограничиться этой проблемой.
3. Определить применимые лучи (по args или полный прогон). Луч,
   требующий пустого слоя (нет ставок → `bet-promotion` нечего
   проверять), пропускается с пометкой.
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

Каждый агент получает: путь к `docs/swot/`; реестр проблем
`docs/business/business-problem.md`; свой lens; список проблем; инструкцию
из `references/rays.md`; схему findings; relevant suppressions.

### Промпт-каркас

```
Lens: <name>
Слой: docs/swot/ (LinkedSWOT, многопроблемный)
Реестр проблем: docs/business/business-problem.md
Проблемы: [<business-problem-slug>, ...]   # или одна, если задан scope

Цель: проверить инвариант методологии LinkedSWOT семантически (не
slug-валидация), по каждой проблеме отдельно. Каждая запись factor/bet
несёт колонку business-problem (массив строк реестра, M:N). Инвариант
замыкается внутри одной проблемы: запись с проблемой P учитывается вместе с
записями той же P.

Прочитай factor.md / bet.md + реестр проблем + ветку state слоя swot
(`../entrypoint/state/swot/`, если есть). Для каждой проблемы из списка
найди смысловые нарушения по паттернам этого луча. В каждом finding укажи
поле "business-problem".

Артефакты не правишь. Ответ — JSON-массив по схеме findings-format.md, без
текста вокруг: ответы лучей сводятся в один отчёт. Пустой массив [] —
нормальный результат; находки ради количества не нужны.
```

## Уровни тяжести

Все примеры считаются **в пределах одной проблемы**:

| severity | смысл | пример |
|---|---|---|
| `error` | разрыв методологии | запись `factor`/`bet` с пустым/невалидным `business-problem`; ставка без «чтобы»/ценности |
| `warning` | подозрительное нарушение | ставка не доведена до карты (`promoted-to = —`); ставка без баланса факторов; фактор в неправильном квадранте |
| `hint` | повод подумать | фактор без ставки (ни по одной проблеме) |

## Формат отчёта

Findings группируются по проблеме (строке реестра), внутри — по лучу:

```
=== /swot-audit ===
Слой: swot · Проблемы: 2 · Лучи: 3 запущено, 3 ответили

── Проблема: paid-outflow ──

[warning] bet-promotion → bet:online-booking-push не доведена до карты.
  Доказательство: promoted-to = «—»; в hypothesis-map нет ни goal, ни
    hypothesis, в которые эта ставка целит.
  Что делать: довести до goal/hypothesis через
  /hypothesis-map-deep-dive, затем проставить promoted-to через
  /swot-deep-dive bet:online-booking-push.

[hint] factor-usage → factor:strong-brand не вошёл ни в одну ставку.
  Доказательство: ни одна bet (по проблемам этого фактора) не содержит
    strong-brand в factors.
  Что делать: использовать в ставке или снизить приоритет через
  /swot-deep-dive.

Сводка: 0 error / 1 warning / 1 hint (по 2 проблемам).
```

После отчёта — `AskUserQuestion` по top-K (до 4 в раунде): «принять
корректным» / «нужна правка» (в next-actions, скилл **не вызывает**
deep-dive сам) / «false positive» (→ suppressions) / «обсудить позже».

## `audit-state/last-report.md`

Лежит **рядом со скиллом**, перезаписывается каждый прогон (не журнал, в git):

```
.claude/skills/swot-audit/audit-state/last-report.md
```

```markdown
---
ran-on: <scope>
problems: [<business-problem-slug>, ...]
lenses-run: 3
findings: { error: X, warning: Y, hint: Z }
verdicts: { accepted: A, needs-fix: B, false-positive: C, deferred: D }
---

# Reasoning trace
## Lens: bet-promotion
- agent-id / duration / business-problem / findings / verdicts / details
...
```

## Suppressions

Findings «false positive» → `audit-state/suppressions.md` (lens + pattern
+ reason + ts). Передаются агенту-лучу как контекст; он семантически не
генерирует подпадающие. Удаляются вручную, чтобы всплыли заново.

## Границы

- **Только отчёт.** Правки — через `/swot-deep-dive`, его запускает
  аналитик; `stable → draft` аудит не понижает — сообщает error.
- **Территория — внутри swot.** Стыки с business, ajtbd и проектами сверяет
  `/cross-audit`, инварианты Карты гипотез — `/hypothesis-map-audit`.
- **Один рой за сессию.** Если findings много — проходить их постепенно.
- **Инструмент аналитика.** В клиент-режиме (`entrypoint-for-business`)
  аудит клиенту не предлагается.
