# Чек-листы полей по kind

Что заполнять при заведении / углублении каждого kind. Это карта
обязательного и опционального, и порядок, в каком разумно копать.

## vision (singleton)

**Обязательно:**

1. **Problem** — одно-два предложения, чьей боли касаемся.
2. **Success** — что считаем успехом (метрика или наблюдаемый сдвиг).
3. **Non-goals** — список «не делаем X, потому что Y».
4. **addresses-problem** — массив slug-рефов на строки
   `docs/business/business-problem.md` (общий реестр проблем), которые
   продукт закрывает (M:N). Привязку даёт аналитик через `AskUserQuestion`
   (опции — существующие строки реестра); скилл не выдумывает проблемы и
   не заводит их здесь.
5. **Оси инициативы** (enum, опция на каждое значение):
   - **audience** — `b2b` \| `b2c` \| `b2b2c` \| `internal` \| `gov`.
   - **intent** — `new-service` \| `improve-service` \| `internal-problem`
     \| `client-problem`.
   - **market-maturity** — `prospective` (разведка нового рынка) \|
     `served` (обслуживаемый рынок). `prospective` адресует проспективные
     `ajtbd/segment` и `business/business-problem` (`served=prospective`).
6. **lifecycle** — жизненный цикл продукта `draft` → `accepted` → `build`
   → `mvp` → `beta-testing` → `stable` → `updating`. **Отдельно** от
   `status` (зрелость записи). Переход в `stable` запускает восходящий
   поток `project → business` (провенанс `from-project` у offering/
   current-metric/business-problem) — ловит `/cross-audit`.

**Статус:** один маркер `**status:** \`draft\`` или `\`stable\`` в
конце файла; рядом строки `**audience:**`, `**intent:**`,
`**market-maturity:**`, `**lifecycle:**`, `**addresses-problem:**`.

**Порядок копания:**
Problem → Success → Non-goals → audience/intent/market-maturity →
lifecycle → addresses-problem.

Problem задаёт всё остальное; без него Success — про абстракцию,
Non-goals — про вкусовщину. `addresses-problem` закрепляет продукт за
конкретными проблемами бизнеса — без неё vision висит в воздухе, а
`success` не на что целить. Оси и lifecycle — enum **от аналитика** через
`AskUserQuestion`, не угадывать.

## user

**Обязательно:** `slug`, `name`, `description`, `status`.

**Должно быть заполнено для stable:**

- `context` — где user живёт, под каким давлением.
- `jobs` — jobs-to-be-done в её языке.
- `pains` — наблюдаемые боли.
- `success` — что для неё лично «полегчало».

**Опционально:** `segments` — массив slug-рефов на `ajtbd/segment`
(сегменты по работам, к которым принадлежит пользователь). Мягкая связь
снизу-вверх (project → ajtbd), прочерк допустим; обратную сторону сводит
`/cross-audit`. Опции — существующие `docs/ajtbd/segment.md`, не выдумывать.

**Порядок копания:**
fundamentals (slug/name/description) → context → jobs → pains → success →
segments.

`context` идёт первым, потому что от него зависит, как формулировать
jobs и pains. Если context размытый — jobs будут абстракцией.

## surface (реестр-хребет)

**Обязательно:** `slug`, `name`, `description`, `status`.

**Должно быть для stable:**

- `type` — enum: `web` | `mobile` | `api` | `admin` | `bot` | `desktop`
  | `embed` | `other`.
- `lives-at` — где живёт (домен / app-id / messenger / host).
- `user` — массив slug пользователей.

**Порядок копания:**
fundamentals → type → lives-at → user.

`type` влияет на формат `lives-at` (для `web` это домен; для `mobile`
— app-id в магазине приложений либо «личная установка», если приложение
не публикуется; для `bot` — мессенджер). Если type
сменился — `lives-at` чаще всего нужно переформулировать.

`surface` — **ось**: каждая строка реестра открывает поверхности место
в остальных слоях. Завести строку здесь = под эту поверхность можно
завести файл `capability/<surface>.md` (и, отдельными скилами, папки
`interface/<surface>/` и композиции — `screens/<surface>/`, для
`type: bot` — `telegram-bot-flow/<surface>/`, для `type: mobile` —
`mobile/<surface>/`).

Для `type: mobile` уведомления, виджеты, ярлыки, голосовые команды и
фоновая работа приложения — не отдельные поверхности, а части той же: они
проектируются в `mobile/<surface>/` (`/mobile-deep-dive`). Внешние
посредники платформы (сервис доставки push, ассистент системы, облачное
распознавание речи) — кандидаты в `integration`; неснимаемые свойства
платформы и правила магазина — в `constraint`.

## capability (файл на поверхность, `capability/<surface>.md`)

Возможность живёт **не плоским файлом**, а в папке `capability/`, по
файлу на поверхность. Связь capability → surface **структурная**: имя
файла = slug поверхности из реестра `surface.md`. Чек-лист зрелости
считается **по каждой записи внутри файла поверхности**; целостность
файла — что все его записи относятся к существующей поверхности реестра
(ловит `/project-audit`).

**Обязательно:** `slug`, `name`, `description`, `status`.

**Должно быть для stable:**

- `value` — ценность для user, в его языке.
- `user` — массив slug пользователей (минимум один).

**Опционально:**
- `hypotheses` — массив slug-рефов на `hypothesis-map/hypothesis`
  (capability реализует гипотезу). Снизу-вверх (project → hypothesis-map).
- `jobs` — массив slug-рефов на `ajtbd/job` (capability прямо целит в
  работу сегмента). Снизу-вверх (project → ajtbd). Прямое ребро —
  **в дополнение** к выводимому через `job-graph.value-mechanics`.
  Оба — прочерк допустим; обратную сторону сводит `/cross-audit`.

**Порядок копания:**
выбрать поверхность (файл `capability/<surface>.md`) → fundamentals →
value → user → hypotheses → jobs.

Capability нельзя заводить без поверхности: сначала строка в реестре
`surface.md`, затем файл `capability/<surface>.md`. Если user в проекте
ещё нет — отработать **stub** для них (см. SKILL.md), потом вернуться.
Capability без user — мёртвая. Одна ценность на двух поверхностях = две
записи в **разных** файлах, у каждой своё воплощение. `hypotheses` и
`jobs` — опции из существующих сущностей соседних слоёв, не выдумывать.

## boundary

**Обязательно:** `slug`, `name`, `description`, `status`.

**Должно быть для stable:**

- `why` — почему отказ продуктово правильный.

**Порядок копания:**
fundamentals → why.

`why` — основная проверка: если в нём нет продуктового аргумента
(только «нет ресурсов», «потом»), запись не boundary, а backlog.

## integration

Файл несёт **две таблицы**: `## Провайдеры` (строка на систему) и
`## Функции` (строка на функцию интеграции).

### Провайдеры

**Обязательно:** `slug`, `name`, `description`, `status`.

**Должно быть для stable:**

- `direction` — enum: `in` | `out` | `duplex`.
- `payload` — что передаём/получаем в целом, в языке бизнеса.
- `owner` — enum: `we` | `partner` | `both`.
- `surface` — массив slug-рефов на поверхности реестра `surface.md`,
  которые интеграция обслуживает (минимум одна).
- `target` — enum: `external` | `sibling-project`.
- `sibling-project` — **обязателен тогда и только тогда**, когда
  `target: sibling-project`: slug соседнего проекта бизнеса; при
  `target: external` — `—`.

**Порядок копания:**
fundamentals → direction → owner → payload → surface → target →
sibling-project.

`direction` + `owner` дают четверть, через которую полезно посмотреть
на payload (out+we = «мы вызываем их API»; in+partner = «они шлют нам
webhook»; duplex+both — нужна явная синхронизация). `surface` привязывает
интеграцию к точкам входа реестра (slug вне реестра — ошибка, ловит
`/project-audit`). `target: sibling-project` означает обмен с **другим
продуктом того же бизнеса**: тогда `sibling-project` ссылается на его
slug, а ребро сводится в `docs/projects/project-map.md`.

### Функции

**Обязательно:** `slug`, `integration`, `name`, `description`, `direction`,
`status`.

- `integration` — slug провайдера из таблицы выше (M:1); функция без
  провайдера — сирота.
- `description` — что функция делает, в **языке бизнеса**, без техники
  (endpoint/сигнатура — конкретика клиента `services/_shared/`, не сюда).
- `direction` — enum: `out` (мы зовём их функцию) | `in` (они зовут нашу,
  мы обслуживаем). Событие — тоже функция (`out` публикуем / `in` подписка).

`slug` функции — её общая личность на трёх высотах: здесь (бизнес), в
клиенте `services/_shared/integrations/<integration>/` (конкретика) и в
`functions` use-case'а, который её дёргает. Согласованность ловит
`/cross-audit`.

## constraint

**Обязательно:** `slug`, `name`, `description`, `status`.

**Должно быть для stable:**

- `kind` — enum: `regulation` | `sla` | `contract` | `technical` |
  `other`.
- `source` — ссылка на документ (URL / номер закона + статья / номер
  контракта + пункт).

**Порядок копания:**
fundamentals → kind → source.

`source` — главная проверка. Если аналитик не может назвать конкретный
документ — это не constraint, а пожелание.

## market

**Обязательно:** `slug`, `name`, `description`, `status`.

**Должно быть для stable:**

- `url` — основной сайт/продукт.
- `sources` — массив ссылок на статьи/обзоры/официальные страницы.

**Опционально, в `description`:**

- Какую позицию занимает (`direct` / `indirect` / `manual` / `legacy`).
- Чем мы отличаемся (наблюдаемо).

**Порядок копания:**

Не порядок копания, а **поток**: market в основном наполняется через
**рой агентов** (`research-rays.md`); кандидаты приходят сразу с
`url` + `sources` + позицией. Аналитик подтверждает кандидата → запись
заводится. В режиме A (вручную) — то же самое, только источник
кандидатов — аналитик, не агенты.

## Универсальные нюансы

### `description`

- Одно предложение. Не абзац.
- В языке бизнеса / user. Не «JWT-аутентификация», а «вход без
  заполнения паролей».
- Без маркетинговой копии. Не «революционная платформа», а «передача
  направления одним кликом».

### `slug`

- Kebab-case, английский.
- Короткий: 1-3 слова обычно достаточно. `nurse-partner` лучше
  `clinic-partner-receiving-nurse`.
- Уникальный в пределах файла.
- Не меняется после первого заведения (это якорь для ссылок в
  state-заметках и в соседних слоях).

### `name`

- Человекочитаемое, в языке проекта (русский по умолчанию).
- Может быть длиннее `slug`, но короче `description`. Что-то вроде
  заголовка карточки.

### `status`

- Дефолт у новой записи — `draft`.
- Повышение — только через скилл, после чек-листа `draft-stable.md`.
- Понижение — только аналитик руками.
