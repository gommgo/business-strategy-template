# pages

> Маршрут (page) — слайс «1 page = 1 route»: адресуемое место поверхности с
> минимальной композицией из widgets/features/entities. Источник — экран
> (screen) своей поверхности. `pages.widgets` / `pages.features` /
> `pages.entities` — канонические источники использования (зеркало —
> `widgets.pages`).

## Критерии page

1. **Есть экран-источник.** `screen` указывает на экран
   `screens/<surface>/screens/<slug>/` — page не выдумывается без экрана.
2. **Адресуемость.** У page есть `path` (маршрут) и `guard` (кто может
   войти: `public` / `authenticated` / роль из `interface who`).
3. **Композиция, не логика.** Page собирает widgets/features/entities;
   собственной бизнес-логики не описывает.
4. **Pages-first.** Блок, живущий на одной page, остаётся её частью — в
   widget не выносится.

## Что page НЕ

- ❌ Переиспользуемый блок — это widget (при ≥2 page-референсах).
- ❌ Сценарий действия — это feature.
- ❌ Модальное окно/степ внутри экрана — это композиция самого экрана
  (screens), если оно не адресуемо маршрутом.

## Тест-критерий

«Сюда можно прийти по адресу, и это соответствует экрану из screens?»

- «**/orders** — список заказов» (есть screen `orders`) → `orders` ✅
- «**Фильтр заказов**» — часть экрана → блок/widget ❌

## Колонки

- `slug` — идентификатор маршрута · строка-идентификатор · обяз.
- `name` — человекочитаемое имя · строка · обяз.
- `description` — что здесь происходит · строка · обяз.
- `screen` — экран-источник · реф → `screens/<surface>/screens/<slug>/` · обяз.
- `path` — маршрут (`/orders/:id`) · строка · обяз.
- `guard` — доступ · `public` \| `authenticated` \| реф → `interface/<surface>/who.md` · обяз.
- `widgets` — используемые widgets · массив ссылок → `widgets` (или `—`) · опц.
- `features` — используемые сценарии · массив ссылок → `features` (или `—`) · опц.
- `entities` — используемые сущности · массив ссылок → `entities` (или `—`) · опц.
- `status` — зрелость записи · `draft | stable` · обяз.

| slug | name | description | screen | path | guard | widgets | features | entities | status |
|---|---|---|---|---|---|---|---|---|---|
| `<slug>` | <имя> | <что происходит> | `<screen>` | </path> | `public` \| `authenticated` \| `<who>` | [`<widget>`] \| — | [`<feature>`] \| — | [`<entity>`] \| — | `draft` \| `stable` |
