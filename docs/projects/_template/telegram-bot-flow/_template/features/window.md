# window

> Окно (window) — один шаг диалога: **одно сообщение** бота (текст + медиа)
> с виджетами, контрактом данных (`getter`) и переходами. Одно окно = одно
> состояние (`state`) группы. Реализует блок (block) interface той же
> поверхности. Все окна фичи лежат в `window.md` — **по H2-секции на
> окно**: `## <window-slug>` + мета-блок + тело.

## Критерии window

1. **Одно сообщение.** Всё, что участник видит на шаге, — один текст (с
   плейсхолдерами `{…}`) + опц. медиа + клавиатура из виджетов.
2. **Принадлежит диалогу фичи.** `state` уникален в группе диалога фичи.
3. **Каждый плейсхолдер обеспечен.** Любой `{ключ}` и каждый `items` имеет
   запись в `getter` с источником и `fallback`.
4. **Действия — к use-case бота, переходы — к окнам.** `action` виджета
   ссылается на use-case бота фичи (`use-case:<uc-slug>`); `transition` —
   окно этой фичи, `back`, `done` или `start:<feature>`. Условные переходы
   (`when`) маршрутизируют **исходы use-case бота**, не правила окна.
5. **Зеркалит interface.** `interface-block` указывает блок-источник;
   `ux-substrates` повторяет его набор атомов.

### Форма секции окна

```markdown
## <window-slug>

> <одна фраза об окне>

​```yaml
name: <человекочитаемое имя>
state: <UPPER_SNAKE>
interface-block: <block-slug>
ux-substrates: [<ux-substrate-slug>]
situations: [<situation-slug>]
who: [<who-slug>]
status: draft | stable

message:
  text: |
    <текст с плейсхолдерами {…}>
  media: —                       # или { type: photo|video|document|animation, source: assets/<window-slug>/… | data:<slug>.<поле> }

widgets:
  - widget: <button|url|select|multiselect|text-input|calendar>
    id: <snake_case>
    ...
    action: use-case:<uc-slug>   # use-case бота этой фичи, или опустить
    transition: <window-slug>|back|done|start:<feature>

getter:
  <ключ>:
    source: use-case:<uc-slug> | dialog-data | start-data | const
    data: data:<slug>            # опц., словарь interface
    fallback: <что показывает окно при недоступном источнике>

errors:
  backend-unavailable: <текст или —>
  invalid-input: <текст или —>
​```
```

- Обязательные мета-поля: `name`, `state`, `interface-block`,
  `ux-substrates`, `situations`, `who`, `status` (`slug` — заголовок H2).
- Условный переход — списком исходов use-case бота:
  `transition: [{ to: address, when: 'use-case бота вернул «нужен адрес»' }, { to: confirm, when: 'иначе' }]`.
- Виджет с `items` берёт коллекцию из ключа `getter` (значение `items` —
  имя ключа). Контракт элемента: каждый item несёт `id` (callback-данные
  выбора) и поля, которые `label`/`selected-label` подставляют через
  `{item.<поле>}`; `fallback` ключа-коллекции — пустое состояние. Большая
  коллекция листается внутри окна — опц. `paginated: true` у виджета.
- `value-type` у `text-input` — `str | int | float | date | phone | email`
  (`str` — по умолчанию, поле можно опустить).
- `media` — `—` либо `type` ∈ `photo | video | document | animation` +
  `source` (путь ассета `assets/<window-slug>/…` или реф
  `data:<slug>.<поле>`).
- `errors` — канон-ключи `backend-unavailable`, `invalid-input` (текст или
  `—`); технический recovery — в код-репо.

### Что window НЕ

- ❌ Не диалог (сценарий из шагов) и не блок interface (UX-анализ).
- ❌ Не уведомление: окно отвечает на действие; исходящее первым — реестр
  `notification.md` корня.
- ❌ Не носитель бизнес-правил: ветвление и валидацию решает домен через
  use-case бота; окно показывает и маршрутизирует.
- ❌ Не код: классы виджетов, `.ftl`-ключи, callback-строки.

### Тест-критерий

«Один шаг диалога — одно сообщение с виджетами, данными и переходами?» —
«Выбор услуг: приглашение + multiselect + Далее/Назад» ✅; «Оформление
заказа целиком» — dialog ❌; «Напоминание за час» — notification ❌.
