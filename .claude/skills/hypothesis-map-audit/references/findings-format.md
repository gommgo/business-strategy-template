# Формат findings из агентов

Каждый агент-луч возвращает валидный JSON-массив и ничего больше
(первый символ `[`, последний `]`): ответы лучей сводятся в один отчёт.

## Schema

```json
[
  {
    "lens": "<lens-name>",
    "business-problem": "<business-problem-slug>",
    "severity": "error" | "warning" | "hint",
    "title": "<одна строка>",
    "evidence": "<2-4 строки: какие slug, какие поля, какой контраст>",
    "suggestion": "<1-2 строки: что аналитику сделать, какую команду>",
    "refs": ["<file>:<slug>", "..."]
  }
]
```

| поле | назначение |
|---|---|
| `lens` | имя луча (как в rays.md) — для группировки |
| `business-problem` | строка реестра, в пределах которой найдено нарушение — для группировки по проблеме (для `problem-tag`, когда `business-problem` пуст/невалиден, — `"—"`) |
| `severity` | `error` (разрыв методологии) / `warning` (подозрение) / `hint` (повод подумать) |
| `title` | одна строка, что найдено |
| `evidence` | конкретика: slug, поля, смысловой контраст |
| `suggestion` | рекомендация аналитику (текст, какую команду запустить) |
| `refs` | ссылки на записи слоя (`file:slug`) |

## Пример

```json
[
  {
    "lens": "hypothesis-shape",
    "business-problem": "paid-outflow",
    "severity": "error",
    "title": "hypothesis:remind-rebook «тогда» не ссылается на метрику",
    "evidence": "so = «станет лучше с возвратами»; metric = «—». Нет привязки к метрике цели проблемы paid-outflow — эффективность нельзя оценить.",
    "suggestion": "Указать метрику в «тогда» (вероятно metric:paid-churn) через /hypothesis-map-deep-dive hypothesis:remind-rebook.",
    "refs": ["hypothesis.md:remind-rebook", "metric.md"]
  }
]
```

## Пустой результат

```json
[]
```

Нормально — не повод выдумывать. В отчёте «0 findings» по этому лучу =
инвариант соблюдён.

## Требования к findings

- Каждый finding — реальное нарушение: пустой массив лучше натянутых
  находок.
- Severity по смыслу: `error` — разрыв методологии, `warning` —
  подозрение, `hint` — повод подумать.
- `evidence` — конкретные slug и поля, а не общие фразы.
- `suggestion` — рекомендация аналитику, а не действие от первого лица
  («я исправлю»).
- Ответ — JSON, не markdown.

## Suppressions context

Если в `audit-state/suppressions.md` есть relevant записи для луча — они
передаются агенту в промпте: «findings, подпадающие под "<pattern>":
<reason>, не генерируй — аналитик уже разобрал их как ложные». Агент
решает по семантике, не строковому матчу.
