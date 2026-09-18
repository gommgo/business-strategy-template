# Промоушн draft → stable

Контракт перевода записи mobile-слоя в `status: stable`. Повышение — только
по явному подтверждению аналитика; скилл не повышает сам.

## Чек-лист

1. **Обязательные слоты заполнены** по канону файла (`Колонки` в
   `docs/projects/_template/mobile/_template/<kind>.md`; порядок и состав —
   `field-checklists.md`); опциональные могут быть `—`.

2. **Ссылки на источники валидны** (в слоях той же поверхности того же
   проекта):
   - `screens.situation-ref`, `features.situation`,
     `permissions.situation`, `system-actions.situation`,
     `widgets.situation-ref`, `background-tasks.situation` → записи
     `interface/<surface>/situation.md`;
   - `entities.source` / `domain-ref` → агрегат/сущность в
     `services/<svc>/domains/<ctx>/` либо `local`;
   - `shared-api.владелец` → сервис реестра `services/service.md`;
   - `event:<ctx>.<Event>` (`entry-points.trigger`, `widgets.refresh`,
     `background-tasks.when`) → событие в `services/*/domains/<ctx>/events/`.
   Доменные рефы — семантические: при отсутствующем домене фиксируются
   требованием в state и stable не блокируют. Ситуации — блокируют: записи
   без источника в interface в stable не поднимаются.

3. **Внутрислойная согласованность и инварианты канона:**
   - все рефы (`screens.key`, slug'и фич, сущностей, точек входа,
     разрешений, системных действий, виджетов, фоновых задач) указывают на
     существующие записи поверхности;
   - экран достижим (оболочка, сценарий, точка входа или `target`
     системного действия); экран с сетью несёт `loading` и `error`;
   - фича имеет носитель (экран, точка входа, системное действие или
     фоновая задача); cross-feature отсутствует;
   - вход `kind: widget` ↔ запись `widgets.md` (`pattern` = slug виджета,
     `widgets.tap` = slug входа);
   - зеркало `widgets.actions` = системные действия с каналом
     `widget:<slug>`;
   - системное действие: `voice` ⇒ `phrases`; `opens-app` ⇒ `target`;
     `response` непуст;
   - фоновая задача: `fallback` непуст; `exact` ⇒ `result ∋
     notification:<slug>`; `continuous` ⇒ разрешение названо и видимость
     пользователю описана;
   - `shell.md#Offline: full` ⇒ есть задача синхронизации
     (`trigger: connectivity`);
   - `shared-api` покрывает все сущности с `source ≠ local` (сущность без
     покрытия — blocker для stable самого `shared-api`).

4. **Тест-критерий** из `Тест-критерий` файла-канона явно подтверждён
   аналитиком в этой сессии.

5. **Нет `**blocker**`-вопросов** в
   `../entrypoint/state/projects/<project-slug>/mobile/<surface>/<kind>/<slug>.md`.

6. **Нет платформенной механики и кода** в ячейках записи: интервалы и
   расписания в минутах, планировщики, имена API, файлов, модулей,
   библиотек; обещания точного времени исполнения кода в фоне.

## Эскалация при сомнении

Сомнение по пункту — строка в `## Открытые вопросы` заметки state:

```
- <короткий falsifiable-вопрос>? (**blocker**)
```

И не промоушить, пока не закрыта. Помни: stable-записи читает `/scaffold`
форка `<org>/mobile` — незрелый stable материализуется в код на двух
платформах сразу.
