# flow

> Поток (flow) — пользовательский сценарий, объединяющий desktop-screen
> и mobile-decomposition. Существует только потому, что один desktop-
> экран может распадаться на серию mobile-экранов с собственной
> навигацией. Облицовочный адаптив (sidebar→drawer) — не flow, это
> `shell.responsive`.

## Критерии flow

1. **Сценарий, не экран.** flow — это «одна задача участника (who)»,
   которая на разных viewport имеет разное число шагов. На desktop
   обычно один screen, на mobile — серия (master / detail / filters).
2. **Список screen-slug на viewport.** `desktop: [screen-slug, …]` и
   `mobile: [screen-slug, …]` — обязательны оба, даже если на каком-то
   viewport один screen.
3. **Transitions внутри mobile-серии.** `transitions` фиксирует
   навигацию внутри mobile-экранов потока (master→detail, master→
   filters). Между desktop и mobile transition не нужен — это разные
   viewport одного flow.
4. **Без облицовочного адаптива.** Когда экран один и меняется только
   облик (sidebar становится drawer) — flow не нужен. Это
   `shell.responsive`.
5. **Один источник правды по viewport-связке.** Если screen
   принадлежит flow — поле `viewport` у screen и его участие в flow
   согласованы.

## Что flow НЕ

- ❌ Не screen: «studies-workspace» — это screen, не flow.
- ❌ Не shell: каркас приложения — shell.
- ❌ Не situation interface: ситуация (situation) — бизнес-уровень,
  flow — viewport-вариативность.
- ❌ Не маршрутизация: routes — поле `screen.route`, не flow.
- ❌ Не state: loading/empty — поле `screen.states`.

## Тест-критерий

«Это объединение N screen-slug разных viewport вокруг одной задачи —
а не сам screen, не shell и не одна точка маршрута?»

- «**Browse исследований**» — на desktop один screen, на mobile три:
  `studies-browse` (flow) → desktop: `[studies-workspace]`, mobile:
  `[studies-list-m, study-detail-m, filters-m]` ✅
- «**studies-workspace**» — это screen, не flow ❌
- «**Sidebar становится drawer**» — это `shell.responsive`, не flow ❌

## Форма frontmatter

| поле | тип | обязательность | смысл |
|---|---|---|---|
| `slug` | string | yes | kebab-case идентификатор |
| `name` | string | yes | человекочитаемое имя |
| `description` | string | yes | одна фраза о flow |
| `desktop` | `[screen-slug]` | yes | список desktop-screen (обычно 1) |
| `mobile` | `[screen-slug]` | yes | список mobile-screen (обычно ≥2) |
| `transitions` | `[ {from, to, trigger} ]` | optional | переходы внутри mobile-серии |
| `who` | `[who-slug]` | optional | роли interface, к которым относится flow |
| `status` | `draft \| stable` | yes | зрелость записи |

## Пример

```markdown
---
slug: studies-browse
name: 'Просмотр исследований'
description: 'Список + фильтры + превью одного'
desktop: [studies-workspace]
mobile: [studies-list-m, study-detail-m, filters-m]
transitions:
  - { from: studies-list-m, to: study-detail-m, trigger: 'tap row' }
  - { from: studies-list-m, to: filters-m,       trigger: 'tap filter button' }
  - { from: filters-m,      to: studies-list-m, trigger: 'apply / close' }
  - { from: study-detail-m, to: studies-list-m, trigger: 'back' }
who: [doctor, nurse]
status: draft
---

# studies-browse

Поток просмотра списка исследований. На desktop master/detail/filters
живут на одном экране; на mobile разводятся на серию.
```

## Anti-patterns

- ❌ flow с пустым `desktop` или пустым `mobile`.
- ❌ Один и тот же screen-slug в обоих списках (это разные viewport —
  должны быть разные screen).
- ❌ transitions между desktop- и mobile-screen.
- ❌ flow с одним screen и в `desktop`, и в `mobile` (тогда это не
  flow, а просто screen с `viewport: any`).
