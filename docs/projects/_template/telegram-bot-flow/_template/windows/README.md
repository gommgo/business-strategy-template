# window

> Окно (window) — один шаг диалога (dialog): **одно сообщение** бота
> (текст + медиа) с виджетами (кнопки, выбор, ввод), контрактом данных
> (`getter`) и переходами. Одно окно = одно состояние (`state`) группы
> диалога. Реализует блок (block) interface той же поверхности — как
> `block`-артефакт слоя экранов, но в понятиях Telegram.

## Критерии window

1. **Одно сообщение.** Всё, что участник (who) видит на шаге, — один
   текст (с плейсхолдерами `{…}`) + опц. медиа + клавиатура из виджетов.
   Серия сообщений — это несколько окон или пагинация внутри одного.
2. **Принадлежит одному диалогу.** `dialog` — ровно один; `state` —
   уникальное имя состояния внутри его группы.
3. **Каждый плейсхолдер обеспечен.** Любой `{ключ}` текста и каждый
   `items` виджета имеет запись в `getter` с источником и `fallback` —
   окно не падает, когда источник недоступен.
4. **Действия — к домену, переходы — к окнам.** `action` виджета ссылается
   на use-case (`use-case:<ctx>.<Operation>`); `transition` — на окно
   этого же диалога, `back`, `done` или `start:<dialog-slug>`. Условные
   переходы (`when`) маршрутизируют **исходы use-case**, не собственные
   правила окна.
5. **Зеркалит interface.** `interface-block` указывает блок-источник;
   `ux-substrates` повторяет его набор атомов; каждый виджет и
   предъявление текста соотносим с атомом (`команда` → `button`, `ввод` →
   `text-input`, `выбор` → `select`/`multiselect`/`calendar`, `инфо`/
   `список` → текст и `items`).

## Что window НЕ

- ❌ Не диалог (dialog): сценарий из шагов — это dialog.
- ❌ Не блок (block) interface: блок — UX-анализ; окно — его воплощение в
  боте (`window.interface-block` — авторское ребро).
- ❌ Не уведомление (notification): окно отвечает на действие участника;
  сообщение, которое бот шлёт первым, — реестр `notification.md`.
- ❌ Не носитель бизнес-правил: ветвление и валидацию решает домен
  (use-case / policy), окно показывает и маршрутизирует.
- ❌ Не код: классы виджетов, `.ftl`-ключи, callback-строки — забота
  код-репо.

## Тест-критерий

«Это один шаг диалога — одно сообщение с виджетами, данными и переходами,
— а не сценарий, не UX-анализ и не исходящее сообщение?»

- «**Выбор услуг**»: текст-приглашение + multiselect + «Далее»/«Назад» ✅
- «**Оформление заказа целиком**» — это dialog ❌
- «**Напоминание о брони за час**» — это notification ❌

## Форма frontmatter

| поле | тип | обязательность | смысл |
|---|---|---|---|
| `slug` | string | yes | kebab-case идентификатор |
| `name` | string | yes | человекочитаемое имя |
| `description` | string | yes | одна фраза об окне |
| `dialog` | `dialog-slug` | yes | диалог, которому окно принадлежит (ровно один) |
| `state` | string (UPPER_SNAKE, англ.) | yes | имя состояния в группе диалога — структурный идентификатор для кода |
| `interface-block` | `block-slug` | yes | блок interface той же поверхности, который окно реализует |
| `ux-substrates` | `[ux-substrate-slug]` | yes | зеркало набора атомов блока-источника |
| `situations` | `[situation-slug]` | yes | ситуации interface, разыгрываемые в окне |
| `who` | `[who-slug]` | yes | роли interface, для которых окно существует |
| `status` | `draft \| stable` | yes | зрелость записи |

## Тело: message, widgets, getter, errors

```yaml
message:
  text: |
    Выберите дополнительные опции:
    {selected_summary}
  media: —                       # или assets/windows/<slug>/…, или data:<slug>.<поле>

widgets:
  - widget: multiselect
    id: services
    items: services              # ключ getter'а
    label: '{item.name}'
    selected-label: '✅ {item.name}'
  - row:
      - widget: button
        id: svc_back
        label: '← Назад'
        transition: back
      - widget: button
        id: svc_next
        label: 'Далее →'
        action: use-case:booking.SetServices
        transition: guests

getter:
  services:
    source: use-case:catalog.ListServices
    data: data:service
    fallback: пустой список — окно живо, «Далее» доступна
  selected_summary:
    source: dialog-data
    fallback: '—'

errors:
  backend-unavailable: 'Сервис недоступен — попробуйте позже'
  invalid-input: —               # ввода в окне нет
```

- `message.text` — русский текст сообщения; плейсхолдеры `{…}` — ключи
  getter'а. `media` — опц.: референс из `assets/` или датум.
- `widgets` — список сверху вниз (= порядок клавиатуры); `row:` группирует
  кнопки в ряд. Поля по виджетам — в каноне слоя
  (`../../README.md § Виджет-язык`).
- `getter` — контракт данных: ключ → `source` (`use-case:…` |
  `dialog-data` | `start-data` | `const`), опц. `data` (реф `data:<slug>`
  на словарь interface), обязательный `fallback`.
- `errors` — содержательные ошибки окна: канонические ключи
  `backend-unavailable` и `invalid-input` (текст или `—`); технический
  recovery (протухшая кнопка, неизвестное состояние) — общий, в код-репо,
  здесь не описывается.

Условный переход — списком исходов use-case:

```yaml
- widget: button
  id: guests_next
  label: 'Далее →'
  action: use-case:booking.SetGuests
  transition:
    - { to: address, when: 'use-case вернул «нужен адрес»' }
    - { to: confirm, when: 'иначе' }
```

## Пример

```markdown
---
slug: guests
name: 'Количество гостей'
description: 'Свободный ввод числа гостей с валидацией диапазона'
dialog: booking
state: GUESTS
interface-block: booking-guests
ux-substrates: [guests-input, guests-confirm]
situations: [specify-guests]
who: [client]
status: draft
---

# guests

Второй шаг заказа: участник вводит число гостей сообщением; валидацию
диапазона задаёт домен.

​```yaml
message:
  text: |
    Сколько гостей? Введите число от 1 до {max}.

widgets:
  - widget: text-input
    id: guests
    value-type: int
    validation: 'число от 1 до {max}'
    action: use-case:booking.SetGuests
    transition:
      - { to: address, when: 'use-case вернул «нужен адрес»' }
      - { to: confirm, when: 'иначе' }
  - widget: button
    id: guests_back
    label: '← Назад'
    transition: back

getter:
  max:
    source: use-case:booking.GetLimits
    fallback: '10'

errors:
  backend-unavailable: 'Сервис недоступен — попробуйте позже'
  invalid-input: 'Нужно число от 1 до {max}'
​```
```

## Anti-patterns

- ❌ Плейсхолдер без ключа в `getter`, ключ без `fallback`.
- ❌ `action` мимо домена: «кнопка сама сохраняет в базу» — действие
  ссылается на use-case или отсутствует.
- ❌ Бизнес-правило в `when` («если сумма > 1000 — скидка») — условие
  перехода формулируется как исход use-case.
- ❌ Тупик: ни одного `transition` и окно не последнее перед `done`.
- ❌ `transition` на окно чужого диалога (между диалогами — только
  `start:<dialog-slug>` / `done`).
- ❌ Дубль `id` виджета в одном окне.
- ❌ Облик в артефакте: эмодзи-оформление, HTML/Markdown-разметка,
  «жирная кнопка» — забота кода и контента.
- ❌ `ux-substrates`, расходящийся с блоком-источником interface
  (зеркало обязано сходиться).
- ❌ Текст с «inline-логикой» («если X, показываем Y») — вариативность
  текста выражается ключами getter'а или разными окнами.
