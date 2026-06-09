# Формат findings из агентов

Каждый агент-lens возвращает **строго** валидный JSON-массив. Без
preamble, без пояснений. Скилл парсит ответ и обрабатывает.

## Schema

```json
[
  {
    "lens": "<lens-name>",
    "project": "<project-slug>" | null,
    "surface": "<surface-slug>" | null,
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
| `project` | string \| null | slug проекта, к которому относится finding (для пар и троек); `null` для верхнеуровневых (общие слои + граф project-map) |
| `surface` | string \| null | slug поверхности из `surface.md`, к которой относится finding (для троек `проект × поверхность × lens`); `null` для пар, верхнеуровневых и `dataitems-crosssurface` (охватывает все поверхности сразу) |
| `business-problem` | string \| null | slug проблемы из реестра `business-problem`, если finding касается конкретной проблемы (углы business-problem ↔ продукт, `addresses-problem-bizproblem`); иначе `null` |
| `severity` | enum | `error` / `warning` / `hint` — уровень тяжести |
| `title` | string | одна строка, что найдено |
| `evidence` | string | конкретные доказательства: какие slug, какие поля, какой контраст |
| `suggestion` | string | что аналитику дальше делать (текст, какую команду запустить) |
| `source-refs` | array | ссылки на source-слой (file или file:slug; пути уже несут `docs/projects/<slug>/...` и для троек — per-surface `capability/<surface>.md`, `interface/<surface>/...`, `screens/<surface>/...`) |
| `destination-refs` | array | ссылки на destination-слой |

`project` обязателен (не `null`) у всех пар и троек; агент получает свой
`<project-slug>` в промпте и проставляет его. `surface` обязателен (не
`null`) у всех троек; агент получает свой `<surface>` в промпте.
`business-problem` заполняется, когда finding можно отнести к конкретной
проблеме реестра.

## Примеры

### Error (тройка проект × поверхность × lens)

```json
{
  "lens": "user-who",
  "project": "referral-network",
  "surface": "web-partner",
  "business-problem": null,
  "severity": "error",
  "title": "who поверхности web-partner не сводимо ни к одному user (роль external-sync)",
  "evidence": "В interface/web-partner/who.md есть who:external-sync, не соответствующий ни одному user проекта (doctor, nurse, scheduler). Системный интерес не обоснован.",
  "suggestion": "Завести user под этот системный интерес через /project-deep-dive referral-network user, или пометить who:external-sync как намеренного системного актора в state.",
  "source-refs": ["docs/projects/referral-network/user.md"],
  "destination-refs": ["docs/projects/referral-network/interface/web-partner/who.md:external-sync"]
}
```

### Error (тройка — поверхность без возможностей)

```json
{
  "lens": "surface-capability",
  "project": "referral-network",
  "surface": "web-partner",
  "business-problem": null,
  "severity": "error",
  "title": "поверхность web-partner stable, но файл возможностей пуст",
  "evidence": "surface.md:web-partner status=stable, surface.user=[`doctor`]. Файл capability/web-partner.md содержит 0 записей — поверхность объявлена, но ни одного умения для врача нет.",
  "suggestion": "Завести возможности через /project-deep-dive referral-network capability:web-partner, либо понизить поверхность в draft.",
  "source-refs": ["docs/projects/referral-network/surface.md:web-partner"],
  "destination-refs": ["docs/projects/referral-network/capability/web-partner.md"]
}
```

### Error (верхнеуровневый M:N — addresses-problem ↔ business-problem)

```json
{
  "lens": "addresses-problem-bizproblem",
  "project": "loyalty-app",
  "surface": null,
  "business-problem": "legacy-sync",
  "severity": "error",
  "title": "проект loyalty-app бьёт в несуществующую проблему legacy-sync",
  "evidence": "projects/loyalty-app/vision.md addresses-problem = [`paid-churn`, `legacy-sync`]. В docs/business/business-problem.md строки: `paid-churn`, `slot-utilization`. Проблемы `legacy-sync` нет.",
  "suggestion": "Завести проблему `legacy-sync` через /business-deep-dive business-problem, либо убрать ref в /project-deep-dive loyalty-app (опечатка slug?).",
  "source-refs": ["docs/projects/loyalty-app/vision.md"],
  "destination-refs": ["docs/business/business-problem.md"]
}
```

### Error (межпроектный стык — integration ↔ project-map)

```json
{
  "lens": "integration-crossproject",
  "project": "referral-network",
  "surface": null,
  "business-problem": null,
  "severity": "error",
  "title": "integration:loyalty-sync (target: sibling-project) не сведена в project-map",
  "evidence": "integration.md:loyalty-sync target=sibling-project, sibling-project=`loyalty-app`. В docs/projects/project-map.md нет ребра от referral-network с via=`integration:loyalty-sync` (есть только loyalty-to-store). Авторская сторона ребра есть, граф её не несёт.",
  "suggestion": "Завести ребро в project-map.md через /project-deep-dive referral-network (карта сводит интеграции target:sibling-project), либо поправить target, если это внешняя система.",
  "source-refs": ["docs/projects/referral-network/integration.md:loyalty-sync"],
  "destination-refs": ["docs/projects/project-map.md"]
}
```

### Warning (тройка — capability поверхности ↔ домен)

```json
{
  "lens": "capability-domain",
  "project": "referral-network",
  "surface": "web-partner",
  "business-problem": null,
  "severity": "warning",
  "title": "capability:send-referral (web-partner) не имеет домена в domains/ проекта",
  "evidence": "capability/web-partner.md:send-referral.value = «один клик вместо звонка». В projects/referral-network/domains/ существуют контексты: auth, billing, inventory. Ни один не покрывает доменную область направлений.",
  "suggestion": "Добавить домен `referrals` через /domain-deep-dive, или подтвердить, что capability реализуется на уровне адаптеров (тогда уточнить в state).",
  "source-refs": ["docs/projects/referral-network/capability/web-partner.md:send-referral"],
  "destination-refs": ["docs/projects/referral-network/domains/"]
}
```

### Hint (верхнеуровневый — общие слои)

```json
{
  "lens": "currentmetric-metric",
  "project": null,
  "surface": null,
  "business-problem": "paid-churn",
  "severity": "hint",
  "title": "текущий KPI no-show-rate не стал ни одной целевой метрикой",
  "evidence": "business/current-metric.md:no-show-rate = 18% (as-of 2026-Q1). В hypothesis-map/metric.md нет целевой метрики, чей baseline опирался бы на этот KPI.",
  "suggestion": "Решить через /hypothesis-map-deep-dive: возможно, no-show-rate — кандидат в целевую метрику для проблемы paid-churn.",
  "source-refs": ["docs/business/current-metric.md:no-show-rate"],
  "destination-refs": ["docs/hypothesis-map/metric.md"]
}
```

### Hint (тройка — рынок ↔ возможности поверхности)

```json
{
  "lens": "market-capability",
  "project": "loyalty-app",
  "surface": "mobile",
  "business-problem": null,
  "severity": "hint",
  "title": "конкурент klara-app покрывает push-кампании, у поверхности mobile такой возможности нет",
  "evidence": "market:klara-app.description = «push loyalty campaigns». В projects/loyalty-app/capability/mobile.md → 0 записей про кампании/рассылки.",
  "suggestion": "Решить через /project-deep-dive loyalty-app capability:mobile: завести capability push-кампаний или зафиксировать boundary «не делаем кампании, потому что Y».",
  "source-refs": ["docs/projects/loyalty-app/market.md:klara-app"],
  "destination-refs": ["docs/projects/loyalty-app/capability/mobile.md"]
}
```

### Hint (консистентность словаря между поверхностями)

```json
{
  "lens": "dataitems-crosssurface",
  "project": "referral-network",
  "surface": null,
  "business-problem": null,
  "severity": "hint",
  "title": "один датум «направление» под разными slug на web и в боте",
  "evidence": "interface/web-partner/data-items.md:referral («направление пациента»); interface/tg-bot/data-items.md:patient-ref («то же направление, другой slug»). Один бизнес-датум, разошлись имена.",
  "suggestion": "Согласовать имена через /interface-deep-dive (раздельные записи — норма, но имя датума стоит держать единым между поверхностями).",
  "source-refs": ["docs/projects/referral-network/interface/web-partner/data-items.md:referral"],
  "destination-refs": ["docs/projects/referral-network/interface/tg-bot/data-items.md:patient-ref"]
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
- ❌ Не забывать `project` (для пар и троек — slug из промпта, не `null`) и
  `surface` (для троек — slug из промпта, не `null`). Перепутанный или
  пропущенный slug ломает группировку отчёта по проектам/поверхностям.
- ❌ Не тащить в finding записи чужого проекта или **чужой поверхности**.
  Сопоставление держится в границах своего `<project-slug>` и (для троек)
  `<surface>` (для углов business-problem↔продукт — в границах проблем,
  которые этот проект закрывает). Запись другой поверхности — материал
  агента той поверхности.

## Suppressions context

Если в `audit-state/suppressions.md` есть relevant записи для текущей
единицы прогона — тройки `(проект, поверхность, lens)`, пары `(проект,
lens)` или верхнеуровневого `lens` — агенту передаются они в промпте:

```
Suppressions для lens <lens> (проект <project-slug | —>, поверхность <surface | —>):
- "<pattern>": <reason>
- ...

НЕ генерируй findings, подпадающие под эти suppressions.
```

Подавление в одной поверхности/проекте не приходит агенту другой
поверхности/проекта по тому же lens. Агент сам решает, подпадает ли его
finding под suppression (по семантике, не строковому матчу).
