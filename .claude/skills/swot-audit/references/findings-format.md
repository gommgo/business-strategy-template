# Формат findings из агентов

Каждый агент-луч возвращает **строго** валидный JSON-массив. Без preamble,
без пояснений. Первый символ `[`, последний `]`.

## Schema

```json
[
  {
    "lens": "<lens-name>",
    "problem": "<problem-slug>",
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
| `problem` | строка реестра, в пределах которой найдено нарушение — для группировки по проблеме (для `problem-tag`, когда `problem` пуст/невалиден, — `"—"`) |
| `severity` | `error` (разрыв методологии) / `warning` (подозрение) / `hint` (повод подумать) |
| `title` | одна строка, что найдено |
| `evidence` | конкретика: slug, поля, смысловой контраст |
| `suggestion` | рекомендация аналитику (текст, какую команду запустить) |
| `refs` | ссылки на записи слоя (`file:slug`) |

## Пример

```json
[
  {
    "lens": "bet-promotion",
    "problem": "paid-outflow",
    "severity": "warning",
    "title": "bet:online-booking-push не доведена до карты гипотез",
    "evidence": "promoted-to = «—». Ни в goal.md, ни в hypothesis.md (docs/hypothesis-map/) нет сущности, в которую эта ставка целит. Мост SWOT→карта оборван.",
    "suggestion": "Довести до goal/hypothesis через /hypothesis-map-deep-dive, затем проставить promoted-to через /swot-deep-dive bet:online-booking-push.",
    "refs": ["bet.md:online-booking-push"]
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
