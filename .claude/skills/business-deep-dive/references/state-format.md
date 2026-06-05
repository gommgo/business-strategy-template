# Формат заметок `state/`

Рабочее состояние знания. Не журнал. Forward-only.

## Расположение

```
.claude/skills/business-deep-dive/state/
├── profile.md                (singleton)
├── offering/<slug>.md
├── channel/<slug>.md
├── competitor/<slug>.md
├── current-metric/<slug>.md
├── material/<slug>.md
└── research/
    └── <тема>-<UTC-ts>.md
```

## Шаблон kind-заметки

```markdown
---
kind: current-metric
slug: paid-churn
ref: docs/business/current-metric.md#paid-churn
---

## Открытые вопросы
- (**blocker**) Отток считают по визитам или по подписке? Влияет на
  baseline.

## Доменные решения
- Источник = CRM (не биллинг), потому что биллинг отстаёт на месяц.

## Что копать дальше
- Запросить у клиента выгрузку за 12 месяцев для окна усреднения.
```

Frontmatter: `kind`, `slug` (для profile отсутствует), `ref`.

## Секции (все опциональны)

- `## Открытые вопросы` — `**blocker**` блокирует stable. Закрытый —
  удалить.
- `## Доменные решения` — «⟨что⟩ — ⟨почему⟩», без истории.
- `## Что копать дальше` — следующие шаги, выполненные удалять.

## Особый случай: research-отчёт

`state/research/<тема>-<ts>.md` — сырьё с роя. Структура: секции
`## <угол>` + `## Кандидаты` по kind. **Не удаляется** после promotion
(исходник для повторного захода). Не kind-заметка.

## Жизненный цикл

Создаётся при наличии содержимого; перезаписывается свободно; kind-заметка
удаляется при пустых секциях или каскадном удалении записи; research —
не удаляется. Единый контекст: read-only видимость соседних `state/` —
клиентский режим (`../business-deep-dive-for-business/state/`) и соседние
слои (`../business-problem-deep-dive*/state/`,
`../project-deep-dive*/state/<slug>/`); в чужой state не писать.
Не аккумулировать журнал.
