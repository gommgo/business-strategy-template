# Реестр правил `mobile-audit`

Каждое правило: `id`, `severity`, что проверяет, как обнаружить,
рекомендация в отчёт.

Категории:

- **R-SURF** — целостность хребта поверхностей (папка ↔ реестр `surface.md`).
- **R-XSURF** — изоляция поверхностей.
- **R-STRUCT** — форма артефактов: файлы, колонки, enum'ы, словари, регистр
  идентификаторов, дубли.
- **R-SRC** — ссылки на источники (interface той же поверхности, домены
  сервисов).
- **R-REF** — внутрислойные ссылки между 12 файлами.
- **R-MIRROR** — зеркало и парные записи.
- **R-REACH** — достижимость и носители.
- **R-INV** — инварианты kind'ов вне экранов (системные действия, виджеты,
  фоновые задачи) и офлайна.
- **R-SEM** — семантические подозрения, anti-patterns канона (смысловой
  разбор, не grep).
- **R-MAT** — зрелость записей.
- **R-COV** — coverage.

Сокращения: `…/mobile/` — `docs/projects/<project-slug>/mobile/<surface>/`;
`…/interface/` — `docs/projects/<project-slug>/interface/<surface>/` (**та
же поверхность**); `…/domains/` —
`docs/projects/<project-slug>/services/*/domains/` (по всем сервисам;
контекст уникален в проекте). Все правила, кроме R-SURF/R-XSURF,
применяются **в пределах одной поверхности**.

`docs/projects/_template/mobile/` — канон формы; из него читаются только
колонки, enum'ы, словари состояний и anti-patterns, не данные.

---

## R-SURF (хребет поверхностей)

### R-SURF-001 «папка поверхности вне реестра»

- **severity**: `error`.
- **проверка**: каждая подпапка `mobile/<X>/` имеет строку `slug: X` в
  `surface.md`.
- **рекомендация**: «Завести строку `<X>` в `surface.md` через
  `/project-deep-dive <project-slug>` либо удалить осиротевшую папку».

### R-SURF-002 «папка слоя для surface с `type ≠ mobile`»

- **severity**: `error`.
- **проверка**: для каждой подпапки `mobile/<X>/` строка `X` реестра имеет
  `type: mobile`. Слой встаёт на место `screens/` только у мобильной
  поверхности; фронтовая поверхность получает экраны и FSD-карту, бот — диалоги.
- **рекомендация**: «Поправить `type` поверхности через
  `/project-deep-dive`, либо композиция этой поверхности живёт в
  `screens/<X>/` / `telegram-bot-flow/<X>/` — папку `mobile/<X>/` удалить».

### R-SURF-003 «мобильная поверхность реестра без папки слоя»

- **severity**: `hint` (coverage).
- **проверка**: для каждой строки `surface.md` с `type: mobile` существует
  папка `mobile/<slug>/`.
- **рекомендация**: «Поверхность объявлена мобильной, но карта приложения не
  начата — завести через `/mobile-deep-dive <project-slug> <slug>`, либо это
  сознательно отложено».

### R-SURF-004 «`screens/` или `fsd/` у мобильной поверхности»

- **severity**: `error`.
- **проверка**: для поверхности с `type: mobile` нет папок
  `screens/<slug>/` и `fsd/<slug>/` — их место занимает `mobile/<slug>/`.
- **рекомендация**: «Композиция мобильной поверхности ведётся в
  `mobile/<slug>/`; папку `screens/`/`fsd/` удалить, нужное перенести через
  `/mobile-deep-dive`».

## R-XSURF (изоляция поверхностей)

### R-XSURF-001 «ссылка из одной поверхности в другую»

- **severity**: `error`.
- **проверка**: реф (ситуация, сущность, экран, виджет…) резолвится только
  в `…/mobile/` и `…/interface/` **этой** поверхности; реф, находимый лишь
  в папке другой поверхности, — нарушение.
- **рекомендация**: «Завести запись в своей поверхности; общее между
  поверхностями сводит `/cross-audit`».

## R-STRUCT (форма)

### R-STRUCT-001 «состав файлов и заголовки»

- **severity**: `error`.
- **проверка**: все 12 файлов на месте; H1 = имя файла; таблицы несут
  колонки канона формы в каноническом порядке; у `shell.md` и
  `shared-lib.md` — секции канона.
- **рекомендация**: «Восстановить форму из
  `docs/projects/_template/mobile/_template/<kind>.md` через
  `/mobile-deep-dive`».

### R-STRUCT-002 «дубль идентификатора»

- **severity**: `error`.
- **проверка**: `slug` уникален в своём файле; `key` экрана уникален в
  поверхности; push-категория (`pattern` у `kind: push`) уникальна; пути
  deep link не пересекаются.

### R-STRUCT-003 «регистр структурных идентификаторов»

- **severity**: `error`.
- **проверка**: `key` — PascalCase (англ.); `slug` — kebab-case;
  push-категория — UPPER_SNAKE. Это handoff-контракт: из них код-репо
  выводит имена.

### R-STRUCT-004 «enum вне канона»

- **severity**: `error`.
- **проверка** (значения — из форм канона):
  `entities.cache`; `screens.entry`, `screens.platforms`;
  `features.shared`, `features.platforms`; `shell.root`, офлайн-политика
  (`read-only` \| `full` \| `blocked`); `entry-points.kind`;
  `system-actions.channels` (в т.ч. формы `widget:<slug>` /
  `notification:<slug>`), `system-actions.mode`; `widgets.kind`,
  `widgets.refresh`; `background-tasks.trigger`, `timing`, `conditions`,
  `result`; `shared-lib` роль локали; `status` (`draft` \| `stable`).

### R-STRUCT-005 «состояние вне словаря»

- **severity**: `error`.
- **проверка**: `screens.states` ⊆ `{loading, empty, populated, error,
  offline, permission-denied, not-found, update-required, maintenance}`;
  `widgets.states` ⊆ `{placeholder, populated, empty, signed-out, stale}`.

### R-STRUCT-006 «`platforms` шире рамки поверхности»

- **severity**: `warning`.
- **проверка**: запись с `platforms: ios` / `android` согласована с
  колонками разрешения (`permissions.android` / `ios` не `—` для заявленной
  платформы).

## R-SRC (ссылки на источники)

### R-SRC-001 «битая ссылка на ситуацию»

- **severity**: `error`.
- **проверка**: `screens.situation-ref`, `features.situation`,
  `permissions.situation`, `system-actions.situation`,
  `widgets.situation-ref`, `background-tasks.situation` существуют в
  `…/interface/situation.md`.
- **рекомендация**: «Завести ситуацию через `/interface-deep-dive
  <project-slug> <surface>` либо поправить реф через `/mobile-deep-dive`».

### R-SRC-002 «сущность без источника»

- **severity**: `error` (пустой `source`) / `warning` (не резолвится).
- **проверка**: `entities.source` — `local` либо ресурс `shared-api.md`;
  `domain-ref` (не `—`) резолвится в агрегат/сущность `…/domains/<ctx>/`.
  Сервисного слоя нет — `warning` с пометкой «домен ещё не спроектирован».

### R-SRC-003 «событие-триггер вне доменов»

- **severity**: `warning`.
- **проверка**: каждый `event:<ctx>.<Event>` (`entry-points.trigger`,
  `widgets.refresh`, `background-tasks.when`) существует в
  `…/domains/<ctx>/events/`. Глубину (payload, публикация в брокер) ведёт
  `/cross-audit`.

### R-SRC-004 «владелец ресурса вне реестра сервисов»

- **severity**: `warning`.
- **проверка**: `shared-api.владелец` указывает на сервис/контекст,
  существующий в `services/service.md` / `…/domains/`.

### R-SRC-005 «операции вне спецификации бэкенда» (advisory)

- **severity**: `hint`.
- **проверка**: только если доступен `../backend/api/openapi.yaml` —
  операции `shared-api.md` существуют в спецификации. Недоступен —
  правило пропускается без находки.

## R-REF (внутрислойные ссылки)

### R-REF-001 «битый внутрислойный реф»

- **severity**: `error`.
- **проверка**: существуют адресаты рефов:
  `screens.entities` / `features.entities` / `widgets.shows` /
  `background-tasks.entities` → `entities`;
  `screens.features` / `system-actions.feature` / `background-tasks.runs` →
  `features`;
  `flows.шаги` / `features.screens` / `entry-points.target` /
  `system-actions.target` / `shell` (табы, `start`, auth-gate, офлайн) →
  `screens.key`;
  `features.api-ops` → операции `shared-api.md`;
  `widgets.tap` → `entry-points`; `widgets.actions` → `system-actions`;
  каналы `widget:<slug>` → `widgets`, `notification:<slug>` → push-записи
  `entry-points`;
  `background:<slug>` (`entry-points.trigger`, `widgets.refresh`,
  `permissions.используется`) → `background-tasks`;
  `action:<slug>` (`permissions.используется`) → `system-actions`;
  `background-tasks.result` (`notification:` / `widget:`) и
  `background-tasks.permissions` → соответствующие записи;
  `shared-lib` флаги и события → `features` / `screens.key`.

### R-REF-002 «cross-feature»

- **severity**: `error`.
- **проверка**: ни одна колонка фичи не ссылается на другую фичу; общее
  поднимается в сущности.

## R-MIRROR (зеркало и парные записи)

### R-MIRROR-001 «`widgets.actions` ↔ `system-actions.channels`»

- **severity**: `error`.
- **проверка**: `widgets.actions` виджета `<w>` = множество системных
  действий, у которых `channels ∋ widget:<w>`. Канон — каналы.
- **рекомендация**: «Пересчитать зеркало через `/mobile-deep-dive …
  widgets:<w>`».

### R-MIRROR-002 «вход `widget` ↔ виджет»

- **severity**: `error`.
- **проверка**: у записи `entry-points` с `kind: widget` `pattern` — slug
  существующего виджета, и у этого виджета `tap` = slug входа; у виджета с
  непустым `tap` вход имеет `kind: widget`.

## R-REACH (достижимость и носители)

### R-REACH-001 «экран-сирота»

- **severity**: `error`.
- **проверка**: экран присутствует хотя бы в одном из: `shell.md` (таб,
  `start`, auth-gate), `flows.шаги`, `entry-points.target`,
  `system-actions.target`.

### R-REACH-002 «фича без носителя»

- **severity**: `error`.
- **проверка**: фича упомянута хотя бы в одном из: `screens.features` (или
  её `screens` непусто), `system-actions.feature`, `background-tasks.runs`;
  либо на неё ведёт точка входа через экран фичи.

### R-REACH-003 «сущность без потребителя»

- **severity**: `hint`.
- **проверка**: сущность не упомянута ни экраном, ни фичей, ни виджетом, ни
  фоновой задачей.

### R-REACH-004 «разрешение без использования»

- **severity**: `error`.
- **проверка**: `permissions.используется` непусто и все адресаты
  существуют.

## R-INV (инварианты вне экранов и офлайна)

### R-INV-001 «экран с сетью без `loading` / `error`»

- **severity**: `error`.
- **проверка**: экран, чьи сущности имеют `source ≠ local` или чьи фичи
  несут `api-ops`, содержит `loading` и `error` в `states`.

### R-INV-002 «голосовое действие без фраз»

- **severity**: `error`.
- **проверка**: `channels ∋ voice` ⇒ `phrases` непусто.

### R-INV-003 «`opens-app` без экрана / `headless` с экраном»

- **severity**: `error`.
- **проверка**: `mode: opens-app` ⇒ `target` — существующий `screens.key`;
  `mode: headless` ⇒ `target = —`.

### R-INV-004 «системное действие без ответа»

- **severity**: `error`.
- **проверка**: `response` непусто.

### R-INV-005 «виджет без базовых состояний / без тапа»

- **severity**: `error`.
- **проверка**: `widgets.states ⊇ {placeholder, populated}`; `tap` непуст у
  `kind ≠ tile`; у `tile` с `tap = —` непусто `actions`.

### R-INV-006 «`exact` без уведомления»

- **severity**: `error`.
- **проверка**: `timing: exact` ⇒ `result ∋ notification:<slug>`. Точным
  бывает только показ уведомления.

### R-INV-007 «`continuous` без разрешения и видимости»

- **severity**: `error`.
- **проверка**: `timing: continuous` ⇒ `trigger: user-started`,
  `permissions` непусто, в `description` названо, что пользователь видит,
  пока работа длится, и как её останавливает.

### R-INV-008 «фоновая задача без `fallback`»

- **severity**: `error`.
- **проверка**: `fallback` непусто.

### R-INV-009 «`remote-event` без события»

- **severity**: `error`.
- **проверка**: `trigger: remote-event` ⇒ `when` несёт
  `event:<ctx>.<Event>`.

### R-INV-010 «офлайн-правки без синхронизации»

- **severity**: `hint`.
- **проверка**: строка `shell.md#Offline` со значением `full` ⇒ есть
  фоновая задача с `trigger: connectivity`, трогающая эту сущность.

### R-INV-011 «кэш ↔ офлайн-политика»

- **severity**: `warning`.
- **проверка**: сущность с офлайн-политикой `read-only` / `full` имеет
  `cache ≠ none`; `shared-api.offline-кэш` согласован с `entities.cache`.

### R-INV-012 «сценарий с сетью без ветки ошибки»

- **severity**: `error`.
- **проверка**: сценарий, чьи шаги включают экраны с сетью, несёт непустые
  `ветки ошибок`.

## R-SEM (семантика, anti-patterns канона)

Смысловой разбор ячеек, не grep: искать по сути, а не по ключевым словам.

### R-SEM-001 «платформенная механика в ячейке»

- **severity**: `warning`.
- **обнаружение**: интервалы и расписания в минутах/часах как механизм,
  cron, имена планировщиков и платформенных API в `freshness`, `when`,
  `fallback`, `description`. Требование формулируется смыслом; механика —
  `docs/stack/` код-репо.

### R-SEM-002 «код в артефакте»

- **severity**: `warning`.
- **обнаружение**: имена Kotlin/Swift-файлов, классов, Gradle-модулей,
  SwiftPM-таргетов, библиотек в любой ячейке.

### R-SEM-003 «обещание точного исполнения в фоне»

- **severity**: `warning`.
- **обнаружение**: формулировки вида «синхронизируется ровно в…»,
  «обновляется каждую минуту» у записей с `timing ≠ exact` или у виджетов.

### R-SEM-004 «запись на всякий случай»

- **severity**: `warning`.
- **обнаружение**: разрешение, виджет, системное действие или фоновая
  задача, чья ситуация-источник по смыслу их не требует (ситуация не про
  «вне приложения», «на лету», «без пользователя»).

### R-SEM-005 «собственное прослушивание как голосовой ввод»

- **severity**: `warning`.
- **обнаружение**: системное действие или фича описывает постоянное
  прослушивание микрофона, а записи `background-tasks` с
  `timing: continuous` и разрешения на микрофон нет.

### R-SEM-006 «`live` без длящегося события»

- **severity**: `warning`.
- **обнаружение**: виджет `kind: live`, чьё описание не называет событие с
  началом и концом.

### R-SEM-007 «запрос разрешения на первом экране»

- **severity**: `warning`.
- **обнаружение**: `permissions.когда` указывает на старт приложения /
  первый экран, а не на момент ценности.

### R-SEM-008 «чувствительное на заблокированном экране»

- **severity**: `hint`.
- **обнаружение**: виджет `lock` / `live` или системное действие с
  `на заблокированном экране: да`, работающие с данными, которые по смыслу
  чувствительны, без оговорки в `description`.

### R-SEM-009 «FSD- и web-смыслы в слое»

- **severity**: `warning`.
- **обнаружение**: `page`, FSD-`widget` как блок страницы, URL-маршрут как
  адрес экрана, desktop ↔ mobile-декомпозиция сценария.

### R-SEM-010 «`description` дублирует `name`»

- **severity**: `hint`.

## R-MAT (зрелость)

### R-MAT-001 «пустой обязательный слот в stable»

- **severity**: `error`.
- **проверка**: состав обязательного — `Колонки` формы kind'а (условные:
  `phrases` при `voice`, `target` при `opens-app`, `tabs` при `root: tabs`,
  `trigger` у `push`).

### R-MAT-002 «stable с blocker'ом в state»

- **severity**: `error`.
- **проверка**: в
  `../entrypoint/state/projects/<project-slug>/mobile/<surface>/<kind>/<slug>.md`
  у stable-записи нет строк с `**blocker**` / `**жду аналитика**`.

### R-MAT-003 «stable ссылается на draft»

- **severity**: `hint`.

## R-COV (coverage)

### R-COV-001 «ситуация interface без носителя»

- **severity**: `hint`.
- **проверка**: каждая ситуация `…/interface/situation.md` отражена хотя бы
  в одном: `screens.situation-ref`, `features.situation`,
  `system-actions.situation`, `widgets.situation-ref`,
  `background-tasks.situation`.

### R-COV-002 «`shared-api` не покрывает сущности»

- **severity**: `error` (у stable-ресурсов) / `warning`.
- **проверка**: для каждой сущности с `source ≠ local` есть ресурс
  `shared-api.md`.

### R-COV-003 «обязательные сценарии»

- **severity**: `error`.
- **проверка**: сценарий `app-start` есть всегда; `login` — если
  `shell.md#Auth-gate` объявляет экраны под сессией.

### R-COV-004 «вход `demo`»

- **severity**: `warning`.
- **проверка**: если приложение публикуется в магазинах — есть точка входа
  `kind: demo` (ревью магазина проходит по demo-доступу). Признак
  публикации — рамка приложения в ветке state (`_frame.md`) либо
  заполненная секция `shell.md#Legal`. Личная установка без магазинов
  `demo` не требует.

### R-COV-005 «локали и флаги»

- **severity**: `warning`.
- **проверка**: `shared-lib.locales ⊇ ru`; каждый флаг используется ≥ 1
  фичей.

## Что не делает mobile-audit

- Не сверяет payload событий, публикацию в брокер, сервис-владельца,
  общий путь ссылок с web-поверхностью — это `/cross-audit` (углы
  `mobile-domain` · `mobile-service` · `mobile-web`).
- Не читает код форка `<org>/mobile` и его `docs/stack/`.
- Не предлагает promotion `draft → stable` и не вызывает
  `/mobile-deep-dive` сам.
