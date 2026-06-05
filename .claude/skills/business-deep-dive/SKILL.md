---
name: business-deep-dive
description: Углублённая проработка верхнего слоя — профиля бизнеса заказчика в `docs/business/` (profile · segment · offering · channel · competitor · current-metric · material). Самая первая точка входа: складывает полную картину бизнеса заказчика ДО определения проблемы и решения. Принимает материалы клиента (сайт, PDF, презентации, соцсети, интервью), запускает рой агентов для web-research рынка и конкурентов, ведёт аналитика через фазы intake → profile → market → structure → metrics → cohesion, заполняет артефакты через структурированные вопросы (AskUserQuestion), фиксирует контекст в собственной памяти `state/`, не выдумывает факты о бизнесе. Использовать всегда, когда речь о docs/business/, онбординге нового заказчика, разборе его материалов, исследовании рынка и конкурентов, фиксации текущих бизнес-метрик (baseline), или подготовке почвы для слоя business-problem. Единственная точка входа в docs/business/ для аналитика.
---

# business-deep-dive

Профиль **бизнеса заказчика** — самый верхний слой, до проблемы и
решения. Канон — `docs/business/README.md`. Источник истины — **материалы
клиента** и **рой web-research**, не проекция аналитика.

Слой **нестрогий**: жёсткой методологии нет, цель — полная и честная
картина бизнеса. Бизнес — **один** (этот слой общий), но он питает
**многопроблемный** слой `docs/business-problem/` (где `frame` — таблица
проблем) и мир из **множества проектов** (`docs/projects/<slug>/`):
факторы SWOT каждой проблемы растут из профиля и конкурентов, baseline
целевых метрик — из `current-metric.md`.

## Точки входа

| вызов | поведение |
|---|---|
| `/business-deep-dive` | сводка по фазам + предложение следующего шага |
| `/business-deep-dive <kind>` | завести новую сущность (режим A) |
| `/business-deep-dive <kind>:<slug>` | углубить запись (режим C) |
| `/business-deep-dive <свободный текст / ссылка / путь к материалу>` | сырьё → разбор (режим B / intake) |
| `/business-deep-dive --research <тема>` | запустить рой web-research |
| `/business-deep-dive --phase <name>` | работать в указанной фазе |

`kind` ∈ {`profile`, `segment`, `offering`, `channel`, `competitor`,
`current-metric`, `material`}.

`phase` ∈ {`intake`, `profile`, `market`, `structure`, `metrics`,
`cohesion`}.

## Что делать сразу при запуске

1. Прочитать `docs/business/README.md` — освежить канон.
2. Прочитать `references/phases.md` — карту фаз.
3. Если args = ссылка/путь/материал клиента — режим intake (см.
   `references/intake.md`).
4. Если args пустые — сводка по фазам + `AskUserQuestion`.
5. Если `--research` — `references/research-rays.md`.

## Сводка состояния (без args)

1. Прочитать `profile.md` + 6 табличных файлов + `state/`.
2. Определить **текущую фазу**:
   - `material`-таблица пустая → `intake`;
   - `profile` нет/draft → `profile`;
   - `competitor` пустая → `market`;
   - `segment`/`offering`/`channel` пустые → `structure`;
   - `current-metric` пустая → `metrics`;
   - всё заполнено, есть draft → `cohesion`.
3. Вывести карту фаз. Через `AskUserQuestion` предложить следующий шаг.

## Фазы

| фаза | цель | артефакты |
|---|---|---|
| `intake` | принять материалы клиента, завести реестр источников | `material.md` |
| `profile` | чем бизнес занимается, как зарабатывает | `profile.md` |
| `market` | конкуренты и рынок (рой web-research) | `competitor.md` |
| `structure` | сегменты, оферы, каналы | `segment.md`, `offering.md`, `channel.md` |
| `metrics` | текущие KPI — baseline-кандидаты | `current-metric.md` |
| `cohesion` | целостность профиля, передача в многопроблемный business-problem | все |

Полная карта — `references/phases.md`. Порядок — рекомендация.

## Три режима

См. `references/workflow-patterns.md`:

- **A. Новая сущность.** Args = `<kind>`. Батч `AskUserQuestion` по
  критериям kind.
- **B / intake. Сырьё.** Args = материал клиента (текст/ссылка/файл).
  Завести `material`-запись (провенанс), извлечь кандидатов по слоям,
  по подтверждению — stub'ы. См. `references/intake.md`.
- **C. Углубление.** Args = `<kind>:<slug>`. Точечные вопросы по дырам.

## Стиль вопросов

- **Всегда `AskUserQuestion`**, до 4 вопросов в раунде.
- **Опции** — для enum (`offering.kind`, `channel.kind`,
  `competitor.position`, `material.kind`), выбора существующего slug
  соседа, теста-критерия, promotion кандидата из research.
- **Other (значения)** — `name`, `description`, `needs`, `value`,
  `position`, числа метрик. Факты о бизнесе **не выдумывать** — брать из
  материалов клиента или подтверждённого research.

## Web-research через рой агентов

См. `references/research-rays.md`. Основной для `competitor`, полезен для
`profile`-контекста и `current-metric` (отраслевые бенчмарки). Запуск —
только по решению аналитика через `AskUserQuestion` (дефолт 5 агентов).
Кандидаты падают в `state/research/<тема>-<ts>.md`; **авто-вписывание в
артефакты запрещено** — promotion через `AskUserQuestion`.

## Память `state/`

`.claude/skills/business-deep-dive/state/<kind>/<slug>.md` (+
`state/profile.md` singleton, `state/research/`). Формат — см.
`references/state-format.md`. Три секции, forward-only, пустые удаляются.
Единый контекст: read-only видимость соседних `state/` — клиентский режим
(`../business-deep-dive-for-business/state/`) и соседние слои
(`../business-problem-deep-dive*/state/`, `../project-deep-dive*/state/<slug>/`
— проектный по текущему продукту). В чужой state не писать.

## Контракт `draft → stable`

См. `references/draft-stable.md`. Обязательные слоты заполнены · критерии
kind подтверждены · anti-patterns не нарушены · тест-критерий ✅ · факт
прослежен до `material` · нет `**blocker**`. Скилл **не повышает сам**.

## Удаление (каскад)

Найти упоминания slug (`offering.for-segment`, `channel.serves-segment`,
ссылки в profile), показать каскад, через `AskUserQuestion` решить по
каждому, применить пакетом, удалить запись и state-заметку.

## Завершение сессии

1. Перечислить затронутые сущности.
2. Назвать текущую фазу и следующий шаг.
3. Через `AskUserQuestion` предложить: продолжить фазу /
   `/cross-audit` (стык с business-problem/project) / передать наработку
   в `/business-problem-deep-dive` (когда профиль готов) /
   `/business-problem-audit` (если бизнес-проблемный слой уже наполнен —
   проверить методологию SWOT/гипотез в пределах каждой проблемы).

## Запреты

- Не редактировать `profile.md` и таблицы вслепую — сначала `Read`.
- Не выдумывать факты о бизнесе. Только из материалов / подтверждённого
  research.
- Не авто-вписывать research в артефакты — promotion через
  `AskUserQuestion`.
- Не повышать `draft → stable` без подтверждения; не понижать сам.
- Не путать `segment` (клиент бизнеса) с `persona` продукта
  (`projects/<slug>/persona`).
- Не аккумулировать историю в `state/` — forward-only.
- Не пушить и не коммитить. Не вызывать другие скилы.
