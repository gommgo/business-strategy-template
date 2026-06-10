# Контракт `draft → stable` (сервисный уровень)

Артефакт становится `stable`, когда **все 5 пунктов одновременно** ✅.
Скилл проверяет, архитектор подтверждает, скилл применяет правку `status:`.
Committed-скрипта-валидатора в репо нет — проверка ручная, по этому
чек-листу и `references/field-checklists.md`.

## Чек-лист

### 1. Обязательные H2 / слоты заполнены

По `references/field-checklists.md` для kind'а (строка `service.md`,
строка `platform.md`, паспорт, `architecture.md`). Пустота — только явным
`_N/A_` / `_нет_`, **уместным типу**:

- `Exposes` = `_N/A_` легально для `worker`, подозрительно для `api`;
- `Owned Contexts` = `_N/A (no domains)_` обязательно для
  `gateway`/`edge`/`bot`, подозрительно для `api`/`worker`;
- `Fronts` ≠ `_N/A_` только у `type: gateway`;
- каждый `Workers.trigger` вида `topic:<t>` имеет парную строку `consumes`
  с тем же `topic` в `Messaging`; `backed-by` резолвится в
  `domains/<ctx>/use-cases/` (этого или другого сервиса — тогда это
  подозрение: воркер исполняет чужой домен);
- `Workers.trigger` со schedule — смысл словами, не cron-выражение
  (cron — runtime, `<org>/infra`);
- placeholder'ы формы (`<slug>`, `<одно предложение>`, шаблонная
  mermaid-диаграмма) не остались.

### 2. Каждое ребро резолвится

Все типизированные рефы артефакта указывают на существующие записи:

- `Dependencies.ref`: `` `service:<slug>` `` → строка `service.md` (и папка
  с паспортом); `` `platform:<slug>` `` → строка `platform.md`;
  `` `integration:<slug>` `` → провайдер `<P>/integration.md`;
- `surfaces` (реестр) и `audience` вида `surface:` (Exposes) → slug'и
  `<P>/surface.md`; `audience` вида `service:` → реестр; `integration:` →
  `<P>/integration.md`;
- `Exposes.backed-by` → существующий файл
  `domains/<ctx>/use-cases/<Operation>.md` **этого** сервиса;
- `Owned Contexts.context` → существующая папка `domains/<ctx>/` этого
  сервиса; контекст не числится во втором паспорте;
- `provided-by: shared:<slug>` (platform) → запись
  `docs/projects/infrastructure/shared-platform.md`;
- `Fronts.Integration` → провайдер `integration.md`; `Fronts.Client` →
  существующий `_shared/integrations/<slug>/README.md`, его `fronted-by`
  указывает на этот сервис.

Записи чужих скиллов (`integration.md`, `surface.md`,
`shared-platform.md`, клиент `_shared/`, доменный use-case) отсюда не
заводятся: нет ссылки — `**blocker**`-вопрос в state + отсылка к
`/project-deep-dive` / `/infrastructure-deep-dive` / `/domain-deep-dive`.

`stable` может ссылаться на `draft`-соседа — допустимо, не блокирует
(подсветить как hint).

### 3. Messaging парный и доказанный

- Каждый `consumes` имеет парный `produces` — тот же `broker` + `topic` +
  `event` — у сервиса-владельца контекста события.
- Каждый `produces`-`event:<ctx>.<Event>` существует файлом
  `domains/<ctx>/events/<Event>.md`, и папка `domains/<ctx>/` лежит в
  **этом** сервисе (produces пишет только владелец).
- `broker` — запись `platform.md` с `type: message-broker`.

Для записей `platform.md` и `architecture.md` пункт сводится к
консистентности свода: ресурс востребован хотя бы одним паспортом
(не сирота); диаграмма не несёт рёбер, которых нет в паспортах.

### 4. Тест-критерий kind'а явно подтверждён

В этой сессии, через `AskUserQuestion` с ✅/❌-примерами; конкретные примеры
скилл подставляет из самого артефакта.

#### строка `service.md`

> «Можно ли задеплоить и сломать его, не трогая соседей?» — и есть ли что
> проектировать в этом репо?

- ✅ `orders` — домены заказов, свои ресурсы, своё API.
- ❌ «Postgres под заказы» — ресурс в `Resources` паспорта, не сервис.
- ❌ «Traefik на входе» — запись `platform.md` (`type: api-gateway`), пока
  в нём нет нашего кода.

#### строка `platform.md`

> «Если ресурс убрать — сломается обмен/доставка у нескольких сервисов,
> при том что проектировать в нём нечего?»

- ✅ NATS, через который ходят события `orders` → `billing-worker`.
- ❌ Postgres только под заказы — ресурс сервиса `orders`.
- ❌ Наш фасад к CRM с маппингом моделей — сервис `type: gateway`.

#### паспорт (`service-passport`)

> Deployment-agnostic и без бизнес-правил не на своём месте: ресурсы —
> «потребность + технология»; данные соседа — только через его `Exposes`
> или события; для `gateway`/`edge`/`bot` — никакой доменной логики?

- ✅ `Resources`: `orders-db` · `database` · `postgres` · «владеет
  заказами и позициями».
- ❌ `Resources`: «postgres 16, 2 vCPU, 4Gb, порт 5432» — runtime-механика.
- ❌ `Dependencies` несёт «читаем таблицу users соседа» — shared database;
  нужен `Exposes`-порт или событие.

#### `architecture.md`

> Диаграмма — чистый свод (каждое ребро доказуемо строкой
> паспорта/реестра), а `Decisions` — falsifiable-решения, а не пересказ
> топологии?

- ✅ «Монолит одним `api`: команда 2 человека, домены делят транзакции;
  сигнал пересмотра — независимый релизный цикл notifications».
- ❌ «Система состоит из сервисов orders и billing» — не решение, пересказ.

### 5. State чист по `**blocker**`-вопросам

`../entrypoint/state/projects/<project-slug>/services/<kind>/<slug>.md`:
секции `## Открытые вопросы` нет, либо в ней нет пометок `**blocker**`.
Не-blocker вопросы при stable допустимы («хорошо бы узнать», не «здесь
смысл сломан»). `## Архитектурные решения` живёт и после stable.

## Алгоритм проверки скиллом

После любой правки артефакта:

1. `Read` артефакт; `Read` state-заметку, если есть.
2. Сверить пункты 1, 2, 3, 5 вручную по форме.
3. Если все 4 ✅ — раунд `AskUserQuestion` по тест-критерию kind'а
   (пункт 4) с ✅/❌-вариантами + Other.
4. Если и пункт 4 ✅ — раунд: «Готов к stable, повышаем?» с опциями
   «Да, повысить» / «Нет, ещё не уверен» (Other — что смущает).
5. При «Да» — `Edit`'ом `status: draft → stable`. Пройтись по
   stable-инвариантам ещё раз; что-то не держится → откатить status,
   вернуться в режим C.

## Что НЕ делать

- **Не повышать сам**, без подтверждения архитектора. Даже при всех 5 ✅.
- **Не понижать `stable → draft` сам** — только подсветить и предложить.
- **Не считать пункт 4 пройденным «по умолчанию»**, потому что секции
  заполнены — тест-критерий требует отдельного смыслового подтверждения.
- **Не закрывать `**blocker**` заведением чужой записи** (`integration.md`,
  `shared-platform.md`, доменный use-case) — только отсылка к
  скиллу-владельцу.
- **Не маркировать stable при следах runtime-механики** — это нарушение
  deployment-agnostic, не «деталь».
