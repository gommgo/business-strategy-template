# Промоушн draft → stable

Контракт перевода записи fsd-слоя в `status: stable`. Повышение — только по
явному подтверждению архитектора; скилл не повышает сам.

## Чек-лист

1. **Обязательные слоты заполнены** по канону файла (`Колонки` в
   `docs/projects/_template/fsd/_template/<kind>.md`); опциональные могут
   быть `—`.

2. **Ссылки на источники валидны** (в слоях той же поверхности того же
   проекта):
   - `features.situation` → запись в `interface/<surface>/situation.md`;
   - `pages.screen` → экран `screens/<surface>/screens/<slug>/`;
   - `widgets.block` (если не `—`) → блок
     `screens/<surface>/blocks/<slug>/`;
   - `entities.source` → агрегат/сущность в `services/<svc>/domains/<ctx>/`
     или запись в `interface/<surface>/data-items.md`;
   - `pages.path` совпадает с маршрутом (`route`) экрана `pages.screen` и
     его параметрами, `pages.guard` — с его доступом (`access`; роли —
     `who` экрана при `access: roles`);
   - `shared-ui.ui-type` — ключ раздела `types` словаря компонентов или
     id расширения проекта (имя из `aka` не принимается);
   - сценарии `shared-api` покрывают обязательные наборы состояний
     экранов поверхности (канон экранов, «Обязательный набор»);
   - локали `shared-lib` — колонки языков реестра текстов
     `screens/<surface>/texts.md` (`text` и `text-<locale>`).

3. **Внутрислойная согласованность**:
   - `features.entities`, `pages.{widgets,features,entities}`,
     `widgets.{entities,features}` ссылаются на существующие записи;
   - зеркало `widgets.pages` соответствует `pages.widgets`;
   - у widget ≥2 page-референсов (или явная пометка зоны каркаса в
     `description`);
   - cross-feature отсутствует;
   - `shared-api` покрывает все entities поверхности (сущность без
     покрытия — blocker для stable самого `shared-api`).

4. **Тест-критерий** из `Тест-критерий` файла-канона явно подтверждён
   архитектором в этой сессии.

5. **Нет `**blocker**`-вопросов** в
   `../entrypoint/state/projects/<project-slug>/fsd/<surface>/<kind>/<slug>.md`.

## Эскалация при сомнении

Сомнение по пункту — строка в `## Открытые вопросы` заметки state:

```
- <короткий falsifiable-вопрос>? (**blocker**)
```

И не промоушить, пока не закрыта: stable-записи читает `/scaffold`
фронт-форка `<org>/frontend`, поэтому незрелый stable материализуется в
код.
