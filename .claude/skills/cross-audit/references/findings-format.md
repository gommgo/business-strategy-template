# Формат findings из агентов

Каждый агент-lens возвращает **строго** валидный JSON-массив. Без
preamble, без пояснений. Скилл парсит ответ и обрабатывает.

## Schema

```json
[
  {
    "lens": "<lens-name>",
    "project": "<project-slug>" | null,
    "business-problem": "<business-problem-slug>" | null,
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
| `project` | string \| null | slug проекта, к которому относится finding (для project-скоупленных углов); `null` для верхнеуровневых (общие слои business ↔ business-problem) |
| `business-problem` | string \| null | slug проблемы из реестра `business-problem`, если finding касается конкретной проблемы (углы business-problem ↔ продукт, `addresses-problem-bizproblem`); иначе `null` |
| `severity` | enum | `error` / `warning` / `hint` — уровень тяжести |
| `title` | string | одна строка, что найдено |
| `evidence` | string | конкретные доказательства: какие slug, какие поля, какой контраст |
| `suggestion` | string | что аналитику дальше делать (текст, какую команду запустить) |
| `source-refs` | array | ссылки на source-слой (file или file:slug; project-скоупленные пути уже несут `docs/projects/<slug>/...`) |
| `destination-refs` | array | ссылки на destination-слой |

`project` обязателен (не `null`) у всех project-скоупленных углов; агент
получает свой `<project-slug>` в промпте и проставляет его. `business-problem`
заполняется, когда finding можно отнести к конкретной проблеме реестра.

## Примеры

### Error (project-скоупленный угол)

```json
{
  "lens": "user-who",
  "project": "referral-network",
  "business-problem": null,
  "severity": "error",
  "title": "user:doctor не имеет соответствия в interface.who проекта",
  "evidence": "user:doctor.context = «врач инициирующей клиники, делает направление». В projects/referral-network/interface/who.md нет ни одной роли, выполняющей эту функцию. Существующие who: nurse, scheduler, any — не покрывают.",
  "suggestion": "Завести who:doctor через /interface-deep-dive referral-network who, или пересмотреть user в /project-deep-dive referral-network user:doctor (возможно, user = клиника как организация, а действующий — nurse).",
  "source-refs": ["docs/projects/referral-network/user.md:doctor"],
  "destination-refs": ["docs/projects/referral-network/interface/who.md"]
}
```

### Error (верхнеуровневый M:N — addresses-problem ↔ business-problem)

```json
{
  "lens": "addresses-problem-bizproblem",
  "project": "partner-portal",
  "business-problem": "legacy-sync",
  "severity": "error",
  "title": "проект partner-portal бьёт в несуществующую проблему legacy-sync",
  "evidence": "projects/partner-portal/vision.md addresses-problem = [`paid-churn`, `legacy-sync`]. В docs/business/business-problem.md строки: `paid-churn`, `slot-utilization`. Проблемы `legacy-sync` нет.",
  "suggestion": "Завести проблему `legacy-sync` через /business-deep-dive business-problem, либо убрать ref в /project-deep-dive partner-portal (опечатка slug?).",
  "source-refs": ["docs/projects/partner-portal/vision.md"],
  "destination-refs": ["docs/business/business-problem.md"]
}
```

### Warning (project-скоупленный угол)

```json
{
  "lens": "capability-domain",
  "project": "referral-network",
  "business-problem": null,
  "severity": "warning",
  "title": "capability:send-referral не имеет домена в domains/ проекта",
  "evidence": "capability:send-referral.value = «один клик вместо звонка». В projects/referral-network/domains/ существуют: auth, billing, inventory. Ни один не покрывает доменную область направлений.",
  "suggestion": "Добавить домен `referrals` через /domain-deep-dive, или подтвердить, что capability реализуется на уровне адаптеров (тогда уточнить в state).",
  "source-refs": ["docs/projects/referral-network/capability.md:send-referral"],
  "destination-refs": ["docs/projects/referral-network/domains/"]
}
```

### Hint (верхнеуровневый — общие слои)

```json
{
  "lens": "currentmetric-metric",
  "project": null,
  "business-problem": "paid-churn",
  "severity": "hint",
  "title": "текущий KPI no-show-rate не стал ни одной целевой метрикой",
  "evidence": "business/current-metric.md:no-show-rate = 18% (as-of 2026-Q1). В hypothesis-map/metric.md нет целевой метрики, чей baseline опирался бы на этот KPI.",
  "suggestion": "Решить через /hypothesis-map-deep-dive: возможно, no-show-rate — кандидат в целевую метрику для проблемы paid-churn.",
  "source-refs": ["docs/business/current-metric.md:no-show-rate"],
  "destination-refs": ["docs/hypothesis-map/metric.md"]
}
```

### Hint (project-скоупленный угол)

```json
{
  "lens": "market-capability",
  "project": "partner-portal",
  "business-problem": null,
  "severity": "hint",
  "title": "Конкурент klara-app покрывает mobile-experience, у нас этой capability нет",
  "evidence": "market:klara-app.description = «mobile-first referrals app». В projects/partner-portal/capability.md → 0 записей с упоминанием mobile-контекста.",
  "suggestion": "Решить через /project-deep-dive partner-portal capability: завести capability mobile-flow или зафиксировать boundary «не делаем mobile, потому что Y».",
  "source-refs": ["docs/projects/partner-portal/market.md:klara-app"],
  "destination-refs": ["docs/projects/partner-portal/capability.md"]
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
- ❌ Не забывать `project`: для project-скоупленного угла это slug из
  промпта, не `null`. Перепутанный или пропущенный slug ломает
  группировку отчёта по проектам.
- ❌ Не тащить в finding записи чужого проекта. Сопоставление держится в
  границах своего `<project-slug>` (для углов business-problem↔продукт —
  в границах проблем, которые этот проект закрывает).

## Suppressions context

Если в `audit-state/suppressions.md` есть relevant записи для текущей пары
`(проект, lens)` — а для верхнеуровневого угла для самого `lens` —
агенту передаются они в промпте:

```
Suppressions для lens <lens> (проект <project-slug | —>):
- "<pattern>": <reason>
- ...

НЕ генерируй findings, подпадающие под эти suppressions.
```

Подавление в одном проекте не приходит агенту другого проекта по тому же
lens. Агент сам решает, подпадает ли его finding под suppression (по
семантике, не строковому матчу).
