# shell

> Каркас (shell) — «капсула» экрана: объявляет типизированные слоты и
> описывает облицовочный адаптив (sidebar→drawer при xs). screen
> заполняет слоты; shell задаёт сами слоты, их обязательность, тип
> принимаемого содержимого и responsive-поведение.

## Критерии shell

1. **Объявляет слоты.** Поле `slots: {...}` — единственный источник
   правды о наборе слотов. screen не вводит новых слотов, только
   заполняет существующие.
2. **Каждый слот типизирован.** Для слота указано `required` (bool) и
   `accepts` (`block`, `tree`, `block | tree`, `block (modal/drawer)`).
3. **Облицовочный адаптив — здесь.** Поле `responsive` фиксирует, как
   слот меняет облик на разных viewport (visible / drawer-via-burger /
   overlay / stacked / hidden). Структурный адаптив (разные screen) —
   через `flow`, не здесь.
4. **Не содержимое.** Дерево shell описывает каркас (Header, Sidebar,
   Main, …) с пустыми слотами; что в слотах — задача screen.
5. **Может быть несколько shell.** `app-shell` (основной),
   `auth-shell` (логин/регистрация), `fullscreen-shell`
   (модалки/мастера) — разные капсулы под разный смысл.

## Что shell НЕ

- ❌ Не screen: каркас без контента — это shell; route с контентом —
  screen.
- ❌ Не block: содержимое слота — это блок.
- ❌ Не layout-примитив: `ui:Stack` — это узел дерева, не shell.
- ❌ Не контракт навигации (sitemap): shell ничего не знает о других
  экранах.

## Тест-критерий

«Это объявление набора слотов + responsive-поведение, а не сам route с
контентом, не блок и не layout-примитив?»

- «**Основной каркас приложения**» (header / side / main / detail /
  overlay / footer) → `app-shell` ✅
- «**Каркас экрана аутентификации**» (только centered main, без
  sidebar) → `auth-shell` ✅
- «**Список исследований**» — это block ❌
- «**Рабочее место исследований**» — это screen ❌

## Форма frontmatter

| поле | тип | обязательность | смысл |
|---|---|---|---|
| `slug` | string | yes | kebab-case идентификатор |
| `name` | string | yes | человекочитаемое имя |
| `description` | string | yes | одна фраза о капсуле |
| `slots` | `{ <name>: { required, accepts } }` | yes | объявление слотов |
| `responsive` | `{ <breakpoint>: { <slot>: <behaviour> } }` | optional | облицовочный адаптив |
| `status` | `draft \| stable` | yes | зрелость записи |

Допустимые `accepts`:
- `block` — только ссылка `block:<slug>`.
- `tree` — только inline-дерево.
- `block | tree` — любое из двух.
- `block (modal/drawer)` — блок-overlay (модалка/шторка).

Допустимые `breakpoint`: `xs`, `sm`, `md`, `lg`, `xl` (токены из ui-lib).

Допустимые `behaviour` слота на breakpoint:
- `visible` — слот рендерится как объявлено в `tree`.
- `drawer-via-burger` — слот скрывается, доступен через бургер-меню.
- `overlay` — слот рендерится поверх main.
- `stacked` — слот рендерится после main в потоке.
- `hidden` — слот не рендерится вообще.

## Тело: tree каркаса

```yaml
tree:
  - ui:AppShell
    - ui:Header
      - ui:Row justify=between
        - ui:Logo
        - ui:Nav
        - ui:UserMenu
    - ui:Sidebar     (fills: $side)
    - ui:Main        (fills: $main)
    - ui:Detail      (fills: $detail)
    - ui:OverlayLayer (fills: $overlay)
    - ui:Footer
      - ui:StatusBar
```

`(fills: $<slot>)` помечает узел shell, в который screen вставит
содержимое слота с таким именем.

## Пример

```markdown
---
slug: app-shell
name: 'Основной каркас приложения'
description: 'Header + Sidebar + Main + Detail + Overlay + Footer'
slots:
  side:    { required: false, accepts: 'block | tree' }
  main:    { required: true,  accepts: 'block | tree' }
  detail:  { required: false, accepts: 'block' }
  overlay: { required: false, accepts: 'block (modal/drawer)' }
responsive:
  xs:
    side:    drawer-via-burger
    detail:  stacked
  sm:
    side:    drawer-via-burger
    detail:  overlay
  md:
    side:    visible
    detail:  visible
status: draft
---

# app-shell

Основная капсула рабочих экранов. На xs/sm sidebar сворачивается под
бургер; detail на mobile уходит в стек (или становится отдельным
screen в рамках flow).

​```yaml
tree:
  - ui:AppShell
    - ui:Header
      - ui:Row justify=between align=center
        - ui:Logo
        - ui:Nav
        - ui:UserMenu
    - ui:Sidebar     (fills: $side)
    - ui:Main        (fills: $main)
    - ui:Detail      (fills: $detail)
    - ui:OverlayLayer (fills: $overlay)
    - ui:Footer
      - ui:StatusBar
​```
```

## Anti-patterns

- ❌ Содержимое в shell-tree (конкретный блок, конкретный текст).
- ❌ Тематические props (`density`/`brand`/`scheme`) на узлах shell.
- ❌ Пиксели/raw-CSS в `tree` или `responsive`.
- ❌ Слот без `accepts` или без `required`.
- ❌ `responsive`-поведение, не покрытое доступными `behaviour`.
- ❌ Структурный адаптив через `responsive` (когда меняется не облик
  слота, а число экранов) — это `flow`.
- ❌ shell без `slots`.
