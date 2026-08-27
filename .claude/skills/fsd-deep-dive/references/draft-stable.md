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
   - `pages.screen` → запись в `screens/<surface>/screen.md`;
   - `widgets.block` (если не `—`) → запись в `screens/<surface>/block.md`;
   - `entities.source` → агрегат/сущность в `services/<svc>/domains/<ctx>/`
     или запись в `interface/<surface>/data-items.md`.

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

И не промоушить, пока не закрыта. Помни: stable-записи читает
`/scaffold` форка `<org>/frontend` — незрелый stable материализуется в код.
