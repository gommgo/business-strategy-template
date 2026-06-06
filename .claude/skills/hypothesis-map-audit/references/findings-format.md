# Формат findings из агентов

Каждый агент-луч возвращает **строго** валидный JSON-массив. Без preamble,
без пояснений. Первый символ `[`, последний `]`.

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

## Что НЕ делать

- ❌ Не выдумывать ради количества. Пустой массив > натянутых.
- ❌ Не путать severity. error = разрыв методологии; warning =
  подозрение; hint = размышление.
- ❌ Не давать общих фраз в `evidence` — только конкретные slug/поля.
- ❌ Не писать `suggestion` от первого лица («я исправлю») — это
  рекомендация аналитику.
- ❌ Не возвращать markdown вместо JSON.

## Suppressions context

Если в `audit-state/suppressions.md` есть relevant записи для луча — они
передаются агенту в промпте: «НЕ генерируй findings, подпадающие под:
"<pattern>": <reason>». Агент решает по семантике, не строковому матчу.
