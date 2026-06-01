# Формат findings из агентов

Каждый агент-lens возвращает **строго** валидный JSON-массив. Без
preamble, без пояснений. Скилл парсит ответ и обрабатывает.

## Schema

```json
[
  {
    "lens": "<lens-name>",
    "severity": "error" | "warning" | "hint",
    "title": "<одна строка>",
    "evidence": "<2-4 строки>",
    "suggestion": "<1-2 строки>",
    "source-refs": ["<file>:<slug>" or "<file>"],
    "destination-refs": ["<file>:<slug>" or "<file>"]
  }
]
```

### Поля

| поле | тип | назначение |
|---|---|---|
| `lens` | string | имя угла (как в angles.md) — для группировки в отчёте |
| `severity` | enum | `error` / `warning` / `hint` — уровень тяжести |
| `title` | string | одна строка, что найдено |
| `evidence` | string | конкретные доказательства: какие slug, какие поля, какой контраст |
| `suggestion` | string | что аналитику дальше делать (текст, какую команду запустить) |
| `source-refs` | array | ссылки на source-слой (file или file:slug) |
| `destination-refs` | array | ссылки на destination-слой |

## Примеры

### Error

```json
{
  "lens": "persona-who",
  "severity": "error",
  "title": "persona:doctor не имеет соответствия в interface.who",
  "evidence": "persona:doctor.context = «врач инициирующей клиники, делает направление». В who.md нет ни одной роли, выполняющей эту функцию. Существующие who: nurse, scheduler, any — не покрывают.",
  "suggestion": "Завести who:doctor через /interface-deep-dive who, или пересмотреть persona в /project-deep-dive persona:doctor (возможно, persona = клиника как организация, а действующий — nurse).",
  "source-refs": ["docs/project/persona.md:doctor"],
  "destination-refs": ["docs/interface/who.md"]
}
```

### Warning

```json
{
  "lens": "capability-domain",
  "severity": "warning",
  "title": "capability:send-referral не имеет домена в docs/domains/",
  "evidence": "capability:send-referral.value = «один клик вместо звонка». В docs/domains/ существуют: auth, billing, inventory. Ни один не покрывает доменную область направлений.",
  "suggestion": "Добавить домен `referrals` через /domain-deep-dive, или подтвердить, что capability реализуется на уровне адаптеров (тогда уточнить в state).",
  "source-refs": ["docs/project/capability.md:send-referral"],
  "destination-refs": ["docs/domains/"]
}
```

### Hint

```json
{
  "lens": "market-capability",
  "severity": "hint",
  "title": "Конкурент klara-app покрывает mobile-experience, у нас этой capability нет",
  "evidence": "market:klara-app.description = «mobile-first referrals app». Наш capability.md → 0 записей с упоминанием mobile-контекста.",
  "suggestion": "Решить через /project-deep-dive capability: завести capability mobile-flow или зафиксировать boundary «не делаем mobile, потому что Y».",
  "source-refs": ["docs/project/market.md:klara-app"],
  "destination-refs": ["docs/project/capability.md"]
}
```

## Пустой результат

Если агент ничего не нашёл:

```json
[]
```

Это **нормально**, не повод выдумывать. Скилл в отчёте пишет «N
findings» = 0 для этого lens, и это сигнал, что слой в этом углу
согласован.

## Что НЕ делать в findings

- ❌ Не выдумывать ради количества. Лучше пустой массив, чем
  пять натянутых.
- ❌ Не путать severity. error = ломает целостность; warning =
  подозрительно, требует разбора; hint = размышление, не действие.
- ❌ Не указывать в `evidence` общие фразы («не похоже на правильное»).
  Только конкретные slug / поля / тексты.
- ❌ Не предлагать в `suggestion` действия от первого лица («я
  исправлю»). Это рекомендация аналитику, что делать.
- ❌ Не повторять одинаковый finding многократно. Один finding = один
  семантический пробел.
- ❌ Не возвращать markdown вместо JSON. Парсер строгий: первые
  символы должны быть `[`, последние `]`.

## Suppressions context

Если в `audit-state/suppressions.md` есть relevant записи для текущего
lens, агенту передаются они в промпте:

```
Suppressions для lens <lens>:
- "<pattern>": <reason>
- ...

НЕ генерируй findings, подпадающие под эти suppressions.
```

Агент сам решает, подпадает ли его finding под suppression (по
семантике, не строковому матчу).
