# flow

> Поток (flow) — серия экранов одной задачи по вьюпортам: объединяет desktop-screen и его mobile-декомпозицию.
> Существует только потому, что один desktop-экран может распадаться на серию mobile-экранов с собственной навигацией.
> Облицовочный адаптив (сайдбар становится выдвижной панелью) — не flow, это `shell.responsive`.
>
> **Поток — не пользовательский сценарий.** Сценарий задачи — шаги, ветвления, ошибки, конечные состояния — kind
> `scenario` в `interface/<surface>/` той же поверхности; какой экран на шаге, что сохраняется при переходе и как
> вернуться — поля экрана и раздел «Переход» `map.md`. Поток лишь раскладывает экраны задачи по вьюпортам.

## Критерии flow

1. **Серия экранов одной задачи, не экран.** flow — «одна задача участника (who)», которая на разных viewport имеет
   разное число экранов. На desktop обычно один screen, на mobile — серия (master / detail / filters).
2. **Список screen-slug на viewport.** `desktop: [screen-slug, …]` и `mobile: [screen-slug, …]` — обязательны оба, даже
   если на каком-то viewport один screen.
3. **Transitions внутри mobile-серии.** `transitions` фиксирует навигацию внутри mobile-экранов потока (master→detail,
   master→filters). Между desktop и mobile transition не нужен — это разные viewport одного flow.
4. **Без облицовочного адаптива.** Когда экран один и меняется только облик (сайдбар становится выдвижной панелью) —
   flow не нужен. Это `shell.responsive`.
5. **Один источник правды по viewport-связке.** Если screen принадлежит flow — поле `viewport` у screen и его участие в
   flow согласованы.
6. **Master-detail на телефоне — поток.** Экран `type: master-detail` на узкой ширине раскладывается потоком минимум из
   двух экранов: список и детали.
7. **Ширины приёмки — по вьюпорту.** Экраны из списка `desktop` принимают на ширинах от первого брейкпоинта
   дизайн-системы, экраны из списка `mobile` — на ширинах ниже него с проверкой вылета на самой узкой ширине:
   `kb/common/acceptance-widths.yaml` (ключ `by_viewport`).

## Что flow НЕ

- ❌ Не screen: «studies-workspace» — это screen, не flow.
- ❌ Не shell: каркас приложения — shell.
- ❌ Не пользовательский сценарий: сценарий задачи — `scenario` в interface той же поверхности; ситуация (situation) —
  шаг сценария, flow — вьюпорт-вариативность экранов.
- ❌ Не сценарий (flow) мобильного приложения: у поверхности `mobile` навигационный сценарий — запись
  `mobile/<surface>/flows.md`.
- ❌ Не маршрутизация: routes — поле `screen.route` и реестр маршрутов `map.md`, не flow.
- ❌ Не state: loading/empty — поле `screen.states`.

## Тест-критерий

«Это объединение N screen-slug разных viewport вокруг одной задачи — а не сам screen, не shell, не одна точка маршрута
и не сценарий задачи по ситуациям?»

- «**Browse исследований**» — на desktop один screen, на mobile три: `studies-browse` (flow) → desktop:
  `[studies-workspace]`, mobile: `[studies-list-m, study-detail-m, filters-m]` ✅
- «**studies-workspace**» — это screen, не flow ❌
- «**Сайдбар становится выдвижной панелью**» — это `shell.responsive`, не flow ❌
- «**Передать направление: заполнить, проверить, отправить**» — это сценарий (scenario) interface ❌

## Форма frontmatter

| поле | тип | обязательность | смысл |
|---|---|---|---|
| `slug` | string | yes | kebab-case идентификатор |
| `name` | string | yes | человекочитаемое имя |
| `description` | string | yes | одна фраза о flow |
| `desktop` | `[screen-slug]` | yes | список desktop-screen (обычно 1) |
| `mobile` | `[screen-slug]` | yes | список mobile-screen (обычно ≥2) |
| `transitions` | `[ {from, to, trigger} ]` | optional | переходы внутри mobile-серии; `trigger` — действие словаря или событие словами |
| `who` | `[who-slug]` | optional | роли interface, к которым относится flow |
| `assets` | `[имя-файла]` | optional | сырьё потока в `assets/flow/<slug>/` (только имена файлов; без ассетов поле отсутствует) |
| `status` | `draft \| stable` | yes | зрелость записи |

## Пример

Иллюстрация формы, не образец ответа.

```markdown
---
slug: studies-browse
name: 'Просмотр исследований'
description: 'Список + фильтры + превью одного'
desktop: [studies-workspace]
mobile: [studies-list-m, study-detail-m, filters-m]
transitions:
  - { from: studies-list-m, to: study-detail-m, trigger: 'нажатие на строку' }
  - { from: studies-list-m, to: filters-m,      trigger: 'кнопка фильтров' }
  - { from: filters-m,      to: studies-list-m, trigger: 'применить или закрыть' }
  - { from: study-detail-m, to: studies-list-m, trigger: 'назад' }
who: [doctor, nurse]
status: draft
---

# studies-browse

Поток просмотра списка исследований. На desktop список, фильтры и детали живут на одном экране `master-detail`; на
mobile разводятся на серию.
```

## Anti-patterns

- ❌ flow с пустым `desktop` или пустым `mobile`.
- ❌ Один и тот же screen-slug в обоих списках (это разные viewport — должны быть разные screen).
- ❌ transitions между desktop- и mobile-screen.
- ❌ flow с одним screen и в `desktop`, и в `mobile` (тогда это не flow, а просто screen с `viewport: any`).
- ❌ Шаги, ветвления и ошибки задачи в потоке — это сценарий (scenario) interface.
- ❌ Экран `master-detail` без mobile-серии в потоке.
