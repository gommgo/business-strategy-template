<!-- Иллюстрация: вход холста фикстуры package-cabinet-defects, собранный canvas_input на основе package-cabinet. -->
# Контракт генерации экранов — `office`

Проект `otves-office`, поверхность `office` (web рода app). Этап `mockup`: тексты — строки `approved` реестра.

Контракт производный: его собирает `scripts/project/contract.py` из файлов слоя проекта, руками он не правится — правка идёт в источник раздела, вход собирается заново. Десять разделов — шаблон ux 11/04 §7.3; за ними — раздел на каждый экран поверхности. Данные — `demo-data.json` рядом.

## Контекст продукта

Источник: `docs/projects/otves-office/vision.md` § Problem, Users · `docs/projects/otves-office/user.md` § Постура · `docs/projects/otves-office/screens/office/map.md` § Решения

Пользователи:

- `manager` — менеджер по замерам: принимает заявки и назначает замер.
- `surveyor` — замерщик: выезжает на объект и отмечает проведённый замер.

| пользователь | часов в день | возврат | основная работа | постура | плотность | ускорители | обучение |
|---|---|---|---|---|---|---|---|
| `manager` — Менеджер по замерам | 6–8 | `daily` | `yes` | `sovereign` | `high` | поиск заявки, фильтр по статусу | `expected` |
| `surveyor` — Замерщик | 0,5 | `daily` | `no` | `mixed` | `medium` | отметка замера | `minimal` |

Задача экрана: в разделе экрана — `main-task`, возможность поверхности.

Ключевое действие: в разделе экрана — `key-action`, действие словаря.

Выводы исследований как ограничения:

> Заявки на бесплатный замер приходят с сайта и по телефону; менеджер ведёт их в таблице, замерщик узнаёт адрес и время звонком из офиса.

Плотность: в разделе экрана — из постуры пользователей и типа экрана (свод map.md); режим продукта — `compact` (бриф на вид).

Решения поверхности:

- одно приложение для менеджера и замерщика — почему: по вопросам ux 13/04 §17 — одно «да» из пяти (демо); кто теряет: замерщик видит раздел плана недоступным для своей роли
- навигация — боковая панель на два раздела — почему: вариант A ux 02/02 §1.6: разделов мало, переключения частые; кто теряет: никто: разделов два
- мобильный — адаптив той же поверхности — почему: замерщику хватает карточки и отметки (ux 09/01 §2); нативное приложение отвергнуто — один сценарий на телефоне; кто теряет: замерщик без сети ждёт связи для отметки
- работа без сети — только отметка замера откладывается до связи — почему: замерщик бывает в подвалах и на новостройках без связи (демо); кто теряет: менеджер видит отметку с задержкой
- экран `not-found` без объекта — почему: служебный маршрут вне реестра (ux 13/04 §22); кто теряет: никто

## Объектная модель

Источник: `docs/projects/otves-office/object.md` § Объекты, Атрибуты · `docs/projects/otves-office/action.md` · `docs/projects/otves-office/capability/office.md` § возможности: user · object · action

Сущности и поля:

**`request` — Заявка на замер.** Просьба клиента приехать и снять размеры квартиры до сметы. Статусы: `new` — новая · `scheduled` — замер назначен · `measured` — замер проведён · `declined` — отказ. Создают: `manager`, `system`; удаляют: `manager`.

| атрибут | имя | ранг | тип | обязателен | длина | значения |
|---|---|---|---|---|---|---|
| `number` | Номер заявки | 1 | `text` | да | 6 / 6 / 8 | — |
| `client` | Клиент | 2 | `text` | да | 2 / 18 / 60 | — |
| `address` | Адрес объекта | 3 | `text` | да | 10 / 40 / 120 | — |
| `phone` | Телефон | 4 | `text` | да | 11 / 16 / 18 | — |
| `visit-date` | Дата замера | 5 | `datetime` | нет | — | — |
| `status` | Статус | 6 | `enum` | да | — | новая, замер назначен, замер проведён, отказ |
| `surveyor` | Замерщик | 7 | `text` | нет | 5 / 16 / 40 | — |
| `budget` | Бюджет ремонта | 8 | `money` | нет | — | — |
| `urgent` | Срочно | 9 | `bool` | нет | — | — |
| `rooms` | Помещения | 10 | `enum[]` | нет | — | кухня, санузел, комната, коридор |
| `photo` | Фото объекта | 11 | `file` | нет | — | — |

**`plan` — План замеров.** Сколько замеров студия берётся провести за месяц. Статусы: —. Создают: `manager`; удаляют: `manager`.

| атрибут | имя | ранг | тип | обязателен | длина | значения |
|---|---|---|---|---|---|---|
| `month` | Месяц | 1 | `date` | да | — | — |
| `target` | План | 2 | `number` | да | — | — |
| `done` | Проведено | 3 | `number` | да | — | — |
| `requests` | Заявки месяца | 4 | `ref:request[]` | нет | — | — |

Действия над сущностями:

| действие | имя | на кнопке | в сообщении | обратимость | объекты |
|---|---|---|---|---|---|
| `create` | Создание заявки | Создать | Создано | undo | `request` |
| `schedule` | Назначение замера | Назначить | Назначено | undo | `request` |
| `complete` | Отметка замера | Отметить замер | Замер отмечен | confirm | `request` |

Права — матрица «пользователь × объект × действие» из возможностей поверхности и колонок creates · deletes:

- `manager`: `request` — Создать, Назначить, создаёт, удаляет · `plan` — создаёт, удаляет
- `surveyor`: `request` — Отметить замер

## Карта экранов

Источник: `docs/projects/otves-office/screens/office/map.md` § Маршруты, Навигация, Переход, Узкий экран · `docs/projects/otves-office/screens/office/screens` § поля route, params, access, url-state, transitions-to-screen

Маршруты:

| маршрут | экран | параметры | доступ | состояние в адресе |
|---|---|---|---|---|
| `*` | `not-found` | — | `authenticated` | — |
| `/` | `plan-dashboard` | — | `roles` | — |
| `/requests` | `requests-list` | — | `roles` | filters, sort, page |
| `/requests/:id` | `request-card` | `{id: request}` | `roles` | — |
| `/requests/new` | `request-new` | — | `roles` | — |

Переходы:

- `not-found` → `requests-list`: ссылка «К заявкам»; сохраняется: —; назад: назад в браузере
- `plan-dashboard` → `requests-list`: переход по плитке плана; сохраняется: —; назад: назад
- `request-card` → `requests-list`: назад к списку; сохраняется: фильтры, сортировка, страница; назад: выбор строки в списке
- `request-new` → `request-card`: `create` — «Создать»; сохраняется: —; назад: назад к списку заявок
- `request-new` → `requests-list`: отмена; сохраняется: фильтры, сортировка, страница; назад: кнопка «Создать заявку»
- `requests-list` → `request-card`: выбор строки; сохраняется: фильтры, сортировка, страница; назад: назад, крошки
- `requests-list` → `request-new`: `create` — «Создать»; сохраняется: —; назад: отмена возвращает сюда

Состояние между экранами:

- фильтры, сортировка и страница списка заявок: URL, пока открыта вкладка; переживает — переход в карточку и назад · перезагрузку · другую вкладку; проверка — открыть карточку, вернуться и сравнить адрес и строки до и после
- введённое в бланке заявки: память вкладки, до отправки или отмены; переживает — ошибку отправки; проверка — вызвать ошибку отправки: ни одно поле не очищено

ЗАПРЕТ: создавать маршруты вне списка; ссылка на незарегистрированный маршрут — ошибка.

Навигация:

| уровень | элемент | пункты | для кого | активное | на узкой ширине |
|---|---|---|---|---|---|
| 1 | `ui:Sidebar` | `` [`requests`] `` | `` [`manager`, `surveyor`] `` | подсветка пункта и aria-current | нижняя панель вкладок |
| 1 | `ui:Sidebar` | `` [`plan`] `` | `` [`manager`] `` | подсветка пункта и aria-current | нижняя панель вкладок |

На узкой ширине:

| тип экрана | reveal | divide | resize | reposition | swap |
|---|---|---|---|---|---|
| каркас | — | — | — | — | навигация: нижняя панель вкладок |
| `list` | номер, клиент, статус — по рангам атрибутов | одна панель | — | поиск над таблицей | таблица — приоритетные колонки |
| `object` | данные заявки по рангам | одна панель | — | команды внизу экрана | — |
| `edit` | все три поля | одна панель | поля на всю ширину | кнопки внизу экрана | — |
| `dashboard` | плитка плана | одна колонка | плитка на всю ширину | — | — |
| `service` | сообщение и ссылка | одна панель | — | — | — |

## Дизайн-система

Источник: `docs/projects/otves-office/design/_design-system/project` · `docs/projects/otves-office/design/system.tokens.json` · `docs/projects/otves-office/design/system.tokens.css` · `docs/projects/otves-office/design/DESIGN.md` · `docs/projects/otves-office/design/system.yaml` · `docs/projects/otves-office/design/app-brief.yaml` · `docs/projects/otves-office/screens/office/map.md` § Конвенции · `kb/common/components.yaml` § types

Источник (по убыванию ценности): артефакт Design System — исходники `docs/projects/otves-office/design/_design-system/project`; адрес артефакта — `docs/projects/otves-office/design/ARTIFACTS.md`

Токены: `docs/projects/otves-office/design/system.tokens.json`, `docs/projects/otves-office/design/system.tokens.css`, `docs/projects/otves-office/design/DESIGN.md` — значения только из токенов

Конвенции размещения:

- порядок кнопок в форме: отмена слева, главная справа (позиция kb/ux/README.md, «Реестр разрешённых противоречий» (демо))
- фокус при открытии и закрытии оверлея: в оверлее — на заголовке, после закрытия — на кнопке, которая его открыла (ux 13/04 §23)
- помощь: одна ссылка «Помощь» в шапке каркаса (ux 13/04 §23)
- range_sign: –
- thousands_space: U+00A0
- empty_state: {"align": "center"}
- icons: {"set": "lucide", "sizes": [16, 20], "stroke": 1.5}
- status_colors: {"request.new": "color.status.info", "request.scheduled": "color.status.warning", "request.measured": "color.status.success", "request.declined": "color.status.danger"}
- object_markers: {"request": {"icon": "clipboard-list", "color": "color.status.info"}}

ПРАВИЛО ЗАЗЕМЛЕНИЯ: не использовать компонент, проп или токен, который нельзя подтвердить источником.

Устаревшее и запрещённое: раздел «Запреты» — бан-лист холста и запреты брифа на вид.

Типы экранов → компоненты ДС (карта решений `components` и `extensions`):

| тип | компонент ДС | где |
|---|---|---|
| `AddressMap` | расширение AddressMap | request-card |
| `Alert` | Callout | request-card, request-new, requests-list |
| `Banner` | Callout | request-card |
| `Button` | Button | request-card, request-new, requests-list |
| `DescriptionList` | DescriptionList | request-card |
| `EmptyState` | EmptyState | plan-dashboard, requests-list |
| `Field` | Field | request-new |
| `KpiTile` | KpiTile | plan-dashboard |
| `Link` | Link | not-found, request-card, каркас app-shell |
| `Pagination` | Pagination | requests-list |
| `Progress` | Progress | request-new, requests-list |
| `SearchInput` | SearchInput | requests-list, каркас app-shell |
| `Select` | Select | requests-list |
| `Sidebar` | Sidebar | каркас app-shell |
| `Skeleton` | Skeleton | request-card, requests-list |
| `Table` | Table | requests-list |
| `TextInput` | TextInput | request-new |
| `TopBar` | TopBar | каркас app-shell |

## Обязательные состояния

Источник: `docs/projects/otves-office/screens/office/screens` § states · `docs/projects/otves-office/interface/office/situation.md` § refusals · `docs/projects/otves-office/capability/office.md` § Паспорта: duration · `docs/projects/otves-office/screens/office/shells/app-shell/index.md` § Состояния приложения · `kb/ux/06-feedback-states-motion/screen-states.yaml`

Экран, коллекция, форма: состояния — по id словаря, а не словами; набор каждого экрана — в его разделе ниже: ключи `states` ∪ обязательный набор, «не применимо» — с причиной.

Приоритет, когда состояний несколько: `no-permission` > `offline` > `not-found` > `error-load` > `loading-initial` > `empty-filtered` > `empty-first-run`; поверх содержимого: `stale`, `limit-reached`.

**Пусто — только после загрузки**: пустое состояние показывается, когда загрузка закончилась без ошибки и данных нет; «нет данных» во время загрузки — дефект (ux 06/01 §4.6).

Состояния поверхности — что показать и что предложить (ux 06/01 §2):

| S-id | ключ | когда | показать | предложить |
|---|---|---|---|---|
| S01 | `empty-first-run` | Объектов этого типа у пользователя ещё нет ни одного | Что здесь будет, когда данные появятся; одно предложение о ценности | Главное действие создания или указание на элемент шапки; ссылка «Подробнее»; демо-данные, если есть |
| S02 | `empty-filtered` | Запрос или фильтр не дал результатов | Что искали (повтор запроса), какие фильтры применены | Сбросить фильтры по одному и все; исправление опечатки; ослабленный запрос; соседние категории |
| S04 | `partial-few` | Данных мало: 1–3 элемента при раскладке, рассчитанной на 10+ | Реальные данные без «растягивания» на весь экран | Подсказка следующего шага; прогресс заполнения, если он честный |
| S05 | `overflow-many` | Элементов кратно больше расчётного: 500, 5 000, 50 000 | Ограниченную порцию + общее число | Пагинация, виртуализация, «показать ещё», сортировка и фильтры |
| S07 | `loading-initial` | Первый показ экрана или блока | Скелетон при известной структуре, спиннер в модуле, прогресс при измеримой длительности (§02) | Ничего; не блокировать остальную страницу |
| S08 | `loading-refresh` | Повторный запрос: сменили фильтр, нажали «обновить», сработал автообновляющий таймер | Старые данные остаются видимыми, поверх — приглушение или тонкий индикатор | Отмену запроса, если он долгий |
| S11 | `saving` | Изменение отправлено, ответ не получен (в т. ч. оптимистичное обновление) | «Сохраняется…» рядом с изменённым объектом; при оптимистичном обновлении — новое значение приглушённым | Блокировку повторной отправки |
| S12 | `success` | Значимое действие завершено | Подтверждение одним каналом: смена состояния объекта, инлайн-подпись или тост | Отмену, если действие обратимо (детали — E1) |
| S13 | `error-load` | Данные не получены | Причину человеческим языком и область, которая пострадала | Повторить; открыть журнал; сообщить, если причина на стороне сервиса |
| S14 | `error-action` | Действие пользователя не выполнено | Что именно не выполнилось и почему; ввод сохранён | Повторить; исправить; сохранить как черновик (E1) |
| S15 | `partial-failure` | Часть блоков загрузилась, часть нет; массовая операция прошла частично | Успешные результаты и перечень неуспешных с причинами | Повторить только неуспешные; выгрузить список ошибок |
| S16 | `offline` | Нет связи | Признак отсутствия связи; что доступно из кэша; что отложено | Продолжить работу локально; очередь отправки; повтор при возврате связи |
| S18 | `no-permission` | У роли нет прав на объект или раздел | Что объект существует (если это не утечка) либо что раздел недоступен; кто выдаёт доступ | Запросить доступ; посмотреть свои права; вернуться |
| S23 | `not-found` | Объекта по адресу нет или его существование скрыто | Что искали и могло ли это быть удалено — строка 404 `../05-flows-journeys/04-errors-and-recovery.md` §4.1; каркас приложения на месте | Пути выхода строки 404 (там же); архивный объект — S20, а не S23 |

Состояния приложения — раз на продукт, в основном каркасе `app-shell`:

| состояние | где видно | форма | тексты |
|---|---|---|---|
| `service-unavailable` | под `ui:TopBar`, над всеми слотами | баннер | `text:app.shell.service-unavailable.banner` |
| `maintenance` | под `ui:TopBar` | баннер заранее, за сутки до работ | `text:app.shell.maintenance.banner` |
| `session-expiry` | слот `overlay` | модальное окно с продлением — заранее, а не после | `text:app.shell.session-expiry.confirm-title`, `text:app.shell.session-expiry.action` |
| `connection-lost` | под `ui:TopBar` | баннер, введённое сохраняется | `text:app.shell.connection-lost.banner` |
| `demo-mode` | не применимо: демо-режима у кабинета нет | — | — |

Элемент: default / hover / focus-visible / active / disabled / selected / loading / error — состояния компонента ДС по `kb/common/components.yaml` (`states` типа).

## Данные

Источник: `docs/projects/otves-office/object.md` § Объекты, Атрибуты · `docs/projects/otves-office/interface/office/data-items.md` § object · `docs/projects/otves-office/screens/office/blocks/requests-list/index.md` § collection.volume

Набор: `demo-data.json` рядом с контрактом — производный (`scripts/project/demo_data.py`, зерно `otves-office`, «сегодня» — 2026-10-01); каждая запись и набор — `example: true`: макет на нём допустим, публикация — нет. Числа на экране — только из набора.

ЗАПРЕТ: числа без источника в наборе; «10k+ users»; «Welcome back, John»; выдуманные отзывы и логотипы.

Коллекции — `collections.<id>.sets` (записи — не больше 50, count — полный объём):

| коллекция | объект | экраны | empty | few | typical | max | объём |
|---|---|---|---|---|---|---|---|
| `requests-list` | `request` | `requests-list` | 0 | 1 | 60 | 3 000 | collection.volume |

Объекты — `objects.<объект>`: записи `records`, крайние случаи `edge_cases`:

- `request` — Заявка на замер: записей 50; крайние случаи: longest, shortest, exotic, missing, null, zero, negative, large, date-past, date-future, date-today, timezone, duplicate, no-file; не применимо: no-relations — нет связей — атрибутов ref:<object>; many-relations — нет атрибутов ref:<object>[]
- `plan` — План замеров: записей 2; крайние случаи: missing, null, zero, negative, large, date-past, date-future, date-today, no-relations, many-relations; не применимо: longest — нет атрибутов text без образца по имени; shortest — нет атрибутов text без образца по имени; exotic — нет атрибутов text без образца по имени; timezone — нет атрибутов datetime; duplicate — нет узнающего атрибута text рангов 1–3; no-file — нет атрибутов file

Самая длинная строка каждой роли реестра — `localization`: подпись переносится, фиксированные ширины не ломаются.

## Тексты

Источник: `docs/projects/otves-office/screens/office/texts.md` · `docs/projects/otves-office/object.md` § Объекты: name, aliases · `docs/projects/otves-office/action.md` § verb, past, banned · `kb/ux/07-ux-writing/06-banned-words-and-patterns.md`

Пробел: строки не того статуса (`checked` — 45): на артборде — заглушка [PLACEHOLDER: текст на утверждении]; ключи — `app.shell.help.link`, `app.shell.service-unavailable.banner`, `app.shell.maintenance.banner`, `app.shell.session-expiry.confirm-title`, `app.shell.session-expiry.action`, `app.shell.connection-lost.banner`, `requests.list.search.placeholder`, `requests.list.status-filter.placeholder`, `requests.list.create.action`, `requests.list.empty-first-run.empty`, `requests.list.empty-filtered.empty`, `requests.list.reset-filters.action`, `requests.list.error-load.inline-message`, `requests.list.retry.action`, `requests.list.no-permission.title`, `requests.list.no-permission.body`, `requests.card.title.title`, `requests.card.schedule.action`, `requests.card.complete.action`, `requests.card.error-load.inline-message`, `requests.card.retry.action`, `requests.card.error-action.inline-message`, `requests.card.no-permission.title`, `requests.card.no-permission.body`, `requests.card.not-found.title`, `requests.card.not-found.body`, `requests.card.back-to-list.link`, `requests.card.offline.banner`, `requests.new.saving.status`, `requests.new.error-action.inline-message`, `requests.new.no-permission.title`, `requests.new.no-permission.body`, `requests.new.client.error`, `requests.new.phone.error`, `requests.new.address.error`, `requests.new.cancel.action`, `requests.new.create.action`, `plan.dashboard.empty-first-run.empty`, `plan.dashboard.no-permission.title`, `plan.dashboard.no-permission.body`, `plan.dashboard.plan-tile.empty`, `plan.dashboard.plan-tile-error.inline-message`, `system.not-found.title.title`, `system.not-found.body.body`, `system.not-found.to-requests.link`

Глоссарий — объекты называются своим именем, синонимы не говорим:

- `request` — Заявка на замер: Просьба клиента приехать и снять размеры квартиры до сметы. Не говорим: лид, обращение.
- `plan` — План замеров: Сколько замеров студия берётся провести за месяц.

Действия — один корень по всему потоку: кнопка, заголовок, сообщение, статус:

- `create` — «Создать» / «Создано»; не говорим: добавить, завести
- `schedule` — «Назначить» / «Назначено»; не говорим: запланировать, записать
- `complete` — «Отметить замер» / «Замер отмечен»; не говорим: закрыть, завершить

Правила: CTA называет результат; имя действия одинаково во всём потоке; ошибка называет причину и шаг; пустой экран предлагает действие.

Запрещённые слова: лид, обращение, добавить, завести, запланировать, записать, закрыть, завершить; словарь запретов по ролям строк — `kb/ux/07-ux-writing/06-banned-words-and-patterns.md`.

Строки этапа `mockup` — статусы `approved`; текст — дословно, число и имя — из данных (подстановки `{…}`):

| ключ | роль | текст | maxlen | статус |
|---|---|---|---|---|
| `requests.list.number.column-header` | `column-header` | Номер | 16 | `approved` |
| `requests.list.client.column-header` | `column-header` | Клиент | 16 | `approved` |
| `requests.list.address.column-header` | `column-header` | Адрес | 16 | `approved` |
| `requests.list.visit-date.column-header` | `column-header` | Дата замера | 16 | `approved` |
| `requests.list.status.column-header` | `column-header` | Статус | 16 | `approved` |
| `requests.new.client.label` | `label` | Клиент | 24 | `approved` |
| `requests.new.phone.label` | `label` | Телефон | 24 | `approved` |
| `requests.new.address.label` | `label` | Адрес объекта | 24 | `approved` |

## Запреты

Источник: `kb/ux/11-ai-generated-ui/04-constraints-prompts-and-checks.md` § 7.3 (список сбоев ux 11/01 F11.1, F13.1) · `kb/ux/06-feedback-states-motion/04-dark-patterns-and-ethics.md` § 8.1 · `docs/projects/otves-office/design/app-brief.yaml` § core.bans

Сбои, которых на макете нет (шаблон ux 11/04 §7.3; ux 11/01 F11.1, F13.1):

- отсутствующий интерактивный элемент
- элемент без реакции
- частичная реализация
- не тот тип контрола
- эффект на чужом элементе
- одинаковые карточки с одним радиусом и тенью
- ALL-CAPS eyebrow над каждым заголовком
- анимация появления на каждой секции

Этика — закрытый список ux 06/04 §8.1:

1. Ничего не добавляется в корзину, заказ, счёт или подписку без явного действия пользователя.
2. Никаких предотмеченных чекбоксов согласий, рассылок, передачи данных, платных опций.
3. Никакого объединения нескольких согласий в одно действие (bundled consent).
4. Отказ не прячется внутри списка значений и не ставится вне ожидаемого порядка.
5. Кнопки согласия и отказа равного визуального веса; отказ не приглушён и не замаскирован.
6. Никакого текста с существенным условием мелким или низкоконтрастным шрифтом.
7. Никаких уничижительных формулировок отказа (confirmshaming).
8. Никаких двойных отрицаний в вопросах согласия.
9. Заголовок блока называет то, что реально произойдёт.
10. Никаких таймеров обратного отсчёта без реального дедлайна; таймер не сбрасывается.
11. Никаких сообщений о низком остатке без реальных данных; никаких «мало» без числа при известном числе.
12. Никаких выдуманных отзывов, рейтингов и сообщений о чужой активности.
13. Полная стоимость раскрывается там же, где названа начальная, до вложения времени.
14. Любое действие, создающее регулярный платёж, называет сумму, период и дату первого списания до подтверждения.
15. Отмена: тот же канал, число шагов не больше, чем при подключении, ни одного удерживающего экрана.
16. Никаких повторных просьб о том, что человек уже отклонил; у любой просьбы есть окончательный отказ.
17. Никаких просьб о разрешениях, данных, оценке до получения ценности.
18. Никаких exit-intent попапов и подмены заголовка вкладки.
19. Никакого автовоспроизведения со звуком; никакой анимации как средства давления; никакого мигания.
20. Реклама и промо явно помечены и не занимают место функциональных элементов.
21. Сгенерированное ИИ помечено как сгенерированное; ассистент не выдаёт себя за человека.
22. Никаких выдуманных чисел, метрик, логотипов и имён в интерфейсе (см. 01-state-matrix.md §6.3).

Бан-лист холста — `brief.yaml` этого входа (`design_system.bans`: приметы дефолтного вида и запреты проекта); запреты брифа на вид: градиенты в фоне и кнопках; тень у карточек на странице — карточка держится на границе.

## Примеры

Источник: `docs/projects/otves-office/interface/office/scenario.md` § Happy path, Ветвления · `docs/projects/otves-office/screens/office/map.md` § События

Пробел: эталонных экранов нет: они появляются после приёмки первых экранов макета (`design/system.yaml`, `starter`)

Эталонный экран: —

Описание взаимодействий текстом:

Сценарий `schedule-visit` — Назначить замер:

1. `find-request`: находит заявку в списке → заявку с адресом и статусом
2. `schedule-visit`: выбирает дату и замерщика → заявку в статусе «замер назначен»
- если заявки нет в списке (шаг 1) → create-request: менеджер заводит заявку со слов клиента

События — одна форма сообщения на событие (map.md):

- `create` → ничего: открывается карточка новой заявки
- `schedule` → смена статуса в карточке
- `complete` → смена статуса в карточке
- ошибка сохранения → инлайн-сообщение над формой, введённое на месте

## Критерии приёмки

Источник: `docs/projects/otves-office/interface/office/scenario.md` § Приёмка · `kb/ux/06-feedback-states-motion/screen-states.yaml` § check

Все перечисленные функции, состояния, ограничения и контент присутствуют.

Ничего не добавлено сверх перечисленного.

Сборка проходит; все маршруты достижимы; все сценарии проходятся; axe без Critical и Serious в обеих темах.

Сценарии:

- `schedule-visit`: менеджер назначает замер по новой заявке за минуту

Состояния — как проверить (ux 06/01 §2):

| S-id | ключ | проверка |
|---|---|---|
| S01 | `empty-first-run` | Замокать пустой массив: в области контента есть текст длиннее строки и ровно один интерактивный элемент |
| S02 | `empty-filtered` | Задать заведомо пустой фильтр: виден исходный запрос и хотя бы один способ его изменить |
| S04 | `partial-few` | Замокать один элемент: раскладка не разваливается, ряд не растягивает один тайл на всю ширину без решения |
| S05 | `overflow-many` | Замокать 500 и 5 000 элементов: страница не вешается, число видно, есть способ сузить |
| S07 | `loading-initial` | Задержка 3 с на API: не белый экран, раскладка не прыгает при подстановке данных |
| S08 | `loading-refresh` | Сменить фильтр: содержимое не пропадает в пустоту и не мигает |
| S11 | `saving` | Задержать PATCH на 2 с: повторное нажатие не создаёт дубль |
| S12 | `success` | После действия видно изменение результата, а не только тост |
| S13 | `error-load` | Ответ 500: текст содержит причину и действие, не содержит кода без объяснения |
| S14 | `error-action` | Ошибка при отправке формы: ни одно поле не очищено |
| S15 | `partial-failure` | Сломать один из нескольких источников: остальные блоки работают |
| S16 | `offline` | Отключить сеть: приложение не показывает белый экран и не теряет ввод |
| S18 | `no-permission` | Войти под ролью без прав: не 404, не пустой список, не «Произошла ошибка» |
| S23 | `not-found` | Открыть адрес с несуществующим ключом: состояние области контента, а не ошибка загрузки и не пустой список (там же) |

Маршруты — только из списка «Карты экранов»; приёмка холста по роду и уровню — `ACCEPTANCE.md` этого входа.

## Экран `not-found` — Страница не найдена

Источник: `docs/projects/otves-office/screens/office/screens/not-found/index.md` § поля, slot-fills, states

- Тип `service` · объект — · статус `stable`
- Главная задача: —
- Ключевое действие: — (экран только для чтения)
- Для кого: `manager`, `surveyor` · плотность: высокая · точки входа: адрес вне реестра
- Маршрут `*` · параметры — · доступ `authenticated` · в адресе: — · вьюпорт `any`
- Каркас `app-shell`: `main` — дерево; `overlay` — пусто
- Блоки: —; компоненты: Link
- Переходы: → `requests-list` (ссылка «К заявкам»; сохраняется: —; назад: назад в браузере)
- Ситуации: —; сценарии: —
- Данные: —
- Тексты — 3 ключа, строки — в разделе «Тексты»: `system.not-found.title.title`, `system.not-found.body.body`, `system.not-found.to-requests.link`; не этого этапа или нет строки: `system.not-found.title.title`, `system.not-found.body.body`, `system.not-found.to-requests.link`

### Обязательные состояния

| S-id | ключ | покрытие | почему в наборе |
|---|---|---|---|
| S07 | `loading-initial` | не применимо: служебный экран статичный, приходит вместе с каркасом | строка «Экран или маршрут целиком» — у каждого экрана |
| S13 | `error-load` | не применимо: служебный экран не грузит данных | строка «Экран или маршрут целиком» — у каждого экрана |

По решению поверхности — `offline`: работа без сети — решение поверхности («Решения» map.md); состояние решает экран, в набор оно не входит.

## Экран `plan-dashboard` — План замеров

Источник: `docs/projects/otves-office/screens/office/screens/plan-dashboard/index.md` § поля, slot-fills, states · `docs/projects/otves-office/screens/office/blocks/plan-tile/index.md` § tree

- Тип `dashboard` · объект `plan` — План замеров · статус `stable`
- Главная задача: `track-plan` — Сверить план замеров
- Ключевое действие: — (экран только для чтения)
- Для кого: `manager` · плотность: высокая · точки входа: старт, навигация
- Маршрут `/` · параметры — · доступ `roles` · в адресе: — · вьюпорт `any`
- Каркас `app-shell`: `main` — дерево; `overlay` — пусто
- Блоки: `plan-tile`; компоненты: EmptyState, KpiTile
- Переходы: → `requests-list` (переход по плитке плана; сохраняется: —; назад: назад)
- Ситуации: `check-plan`; сценарии: —
- Данные: `plan` → `objects.plan.records` (`plan-1` …), крайние случаи — `objects.plan.edge_cases`
- Тексты — 5 ключей, строки — в разделе «Тексты»: `plan.dashboard.empty-first-run.empty`, `plan.dashboard.no-permission.title`, `plan.dashboard.no-permission.body`, `plan.dashboard.plan-tile-error.inline-message`, `plan.dashboard.plan-tile.empty`; не этого этапа или нет строки: `plan.dashboard.empty-first-run.empty`, `plan.dashboard.no-permission.title`, `plan.dashboard.no-permission.body`, `plan.dashboard.plan-tile-error.inline-message`, `plan.dashboard.plan-tile.empty`

### Обязательные состояния

| S-id | ключ | покрытие | почему в наборе |
|---|---|---|---|
| S01 | `empty-first-run` | дельта | строка типа экрана «Дашборд и плитка показателя» |
| S04 | `partial-few` | не применимо: на экране одна плитка | строка типа экрана «Дашборд и плитка показателя» |
| S07 | `loading-initial` | не применимо: плитка грузит данные сама и держит свою загрузку | строка типа экрана «Дашборд и плитка показателя»; строка «Экран или маршрут целиком» — у каждого экрана |
| S13 | `error-load` | не применимо: плитка держит свою ошибку, других источников у экрана нет | строка типа экрана «Дашборд и плитка показателя»; строка «Экран или маршрут целиком» — у каждого экрана; отказ ситуации check-plan |
| S15 | `partial-failure` | не применимо: у экрана один источник — плитка | строка типа экрана «Дашборд и плитка показателя» |
| S18 | `no-permission` | дельта | строка «Экран или маршрут целиком» — у каждого экрана; доступ к маршруту ограничен ролями (access: roles) |

Блок `plan-tile` со своим источником — свой набор: S07 `loading-initial` (дельта), S13 `error-load` (дельта)

По решению поверхности — `offline`: работа без сети — решение поверхности («Решения» map.md); состояние решает экран, в набор оно не входит.
По решению поверхности — `stale`: живые данные — решение поверхности (дашборд); состояние решает экран, в набор оно не входит.

## Экран `request-card` — Карточка заявки

Источник: `docs/projects/otves-office/screens/office/screens/request-card/index.md` § поля, slot-fills, states · `docs/projects/otves-office/screens/office/blocks/request-details/index.md` § tree

- Тип `object` · объект `request` — Заявка на замер · статус `stable`
- Главная задача: `schedule-visit` — Назначить замер
- Ключевое действие: `schedule` — «Назначить»
- Для кого: `manager`, `surveyor` · плотность: высокая · точки входа: `request-new`, `requests-list`, письмо о назначенном замере
- Маршрут `/requests/:id` · параметры `{id: request}` · доступ `roles` · в адресе: — · вьюпорт `any`
- Каркас `app-shell`: `main` — блок `request-details`; `overlay` — пусто
- Блоки: `request-details`; компоненты: AddressMap, Alert, Banner, Button, DescriptionList, Link, Skeleton
- Переходы: → `requests-list` (назад к списку; сохраняется: фильтры, сортировка, страница; назад: выбор строки в списке)
- Ситуации: `schedule-visit`, `mark-measured`; сценарии: `schedule-visit`
- Данные: `request` → `objects.request.records` (`request-1` …), крайние случаи — `objects.request.edge_cases`
- Тексты — 12 ключей, строки — в разделе «Тексты»: `requests.card.error-load.inline-message`, `requests.card.retry.action`, `requests.card.error-action.inline-message`, `requests.card.no-permission.title`, `requests.card.no-permission.body`, `requests.card.not-found.title`, `requests.card.not-found.body`, `requests.card.back-to-list.link`, `requests.card.offline.banner`, `requests.card.title.title`, `requests.card.schedule.action`, `requests.card.complete.action`; не этого этапа или нет строки: `requests.card.error-load.inline-message`, `requests.card.retry.action`, `requests.card.error-action.inline-message`, `requests.card.no-permission.title`, `requests.card.no-permission.body`, `requests.card.not-found.title`, `requests.card.not-found.body`, `requests.card.back-to-list.link`, `requests.card.offline.banner`, `requests.card.title.title`, `requests.card.schedule.action`, `requests.card.complete.action`

### Обязательные состояния

| S-id | ключ | покрытие | почему в наборе |
|---|---|---|---|
| S07 | `loading-initial` | дельта | экран грузит данные (ui:DescriptionList items=data:request); строка типа экрана «Карточка объекта»; строка «Экран или маршрут целиком» — у каждого экрана |
| S12 | `success` | не применимо: результат виден сменой статуса заявки | строка типа экрана «Карточка объекта» |
| S13 | `error-load` | дельта | экран грузит данные (ui:DescriptionList items=data:request); строка типа экрана «Карточка объекта»; строка «Экран или маршрут целиком» — у каждого экрана |
| S14 | `error-action` | дельта | строка типа экрана «Карточка объекта»; отказ ситуации schedule-visit; отказ ситуации mark-measured |
| S16 | `offline` | дельта | отказ ситуации mark-measured |
| S18 | `no-permission` | дельта | строка «Экран или маршрут целиком» — у каждого экрана; доступ к маршруту ограничен ролями (access: roles) |
| S23 | `not-found` | дельта | у маршрута параметр объекта (id: request) |

## Экран `request-new` — Новая заявка

Источник: `docs/projects/otves-office/screens/office/screens/request-new/index.md` § поля, slot-fills, states · `docs/projects/otves-office/screens/office/blocks/request-form/index.md` § tree

- Тип `edit` · объект `request` — Заявка на замер · статус `stable`
- Главная задача: `create-request` — Создать заявку
- Ключевое действие: `create` — «Создать»
- Для кого: `manager` · плотность: средняя · точки входа: навигация, `requests-list`
- Маршрут `/requests/new` · параметры — · доступ `roles` · в адресе: — · вьюпорт `any`
- Каркас `app-shell`: `main` — блок `request-form`; `overlay` — пусто
- Блоки: `request-form`; компоненты: Alert, Button, Field, Progress, TextInput
- Переходы: → `request-card` (`create` — «Создать»; сохраняется: —; назад: назад к списку заявок); → `requests-list` (отмена; сохраняется: фильтры, сортировка, страница; назад: кнопка «Создать заявку»)
- Ситуации: `create-request`; сценарии: —
- Данные: `request` → `objects.request.records` (`request-1` …), крайние случаи — `objects.request.edge_cases`
- Тексты — 12 ключей, строки — в разделе «Тексты»: `requests.new.saving.status`, `requests.new.error-action.inline-message`, `requests.new.no-permission.title`, `requests.new.no-permission.body`, `requests.new.client.label`, `requests.new.client.error`, `requests.new.phone.label`, `requests.new.phone.error`, `requests.new.address.label`, `requests.new.address.error`, `requests.new.cancel.action`, `requests.new.create.action`; не этого этапа или нет строки: `requests.new.saving.status`, `requests.new.error-action.inline-message`, `requests.new.no-permission.title`, `requests.new.no-permission.body`, `requests.new.client.error`, `requests.new.phone.error`, `requests.new.address.error`, `requests.new.cancel.action`, `requests.new.create.action`

### Обязательные состояния

| S-id | ключ | покрытие | почему в наборе |
|---|---|---|---|
| S07 | `loading-initial` | не применимо: у бланка нет справочников — поля пустые сразу | экран грузит данные (ui:TextInput value=data:request.client); строка типа экрана «Форма» (загрузка справочников); строка «Экран или маршрут целиком» — у каждого экрана |
| S11 | `saving` | дельта | строка типа экрана «Форма» |
| S12 | `success` | не применимо: после создания открывается карточка новой заявки | строка типа экрана «Форма» |
| S13 | `error-load` | не применимо: бланк не грузит данных | экран грузит данные (ui:TextInput value=data:request.client); строка «Экран или маршрут целиком» — у каждого экрана |
| S14 | `error-action` | дельта | строка типа экрана «Форма»; отказ ситуации create-request |
| S18 | `no-permission` | дельта | строка «Экран или маршрут целиком» — у каждого экрана; доступ к маршруту ограничен ролями (access: roles) |

По решению поверхности — `offline`: работа без сети — решение поверхности («Решения» map.md); состояние решает экран, в набор оно не входит.

## Экран `requests-list` — Список заявок

Источник: `docs/projects/otves-office/screens/office/screens/requests-list/index.md` § поля, slot-fills, states · `docs/projects/otves-office/screens/office/blocks/requests-list/index.md` § tree

- Тип `list` · объект `request` — Заявка на замер · статус `stable`
- Главная задача: `schedule-visit` — Назначить замер
- Ключевое действие: `create` — «Создать»
- Для кого: `manager`, `surveyor` · плотность: высокая · точки входа: старт, навигация, `not-found`, `plan-dashboard`, `request-card`, `request-new`
- Маршрут `/requests` · параметры — · доступ `roles` · в адресе: filters, sort, page · вьюпорт `any`
- Каркас `app-shell`: `main` — блок `requests-list`; `overlay` — пусто
- Блоки: `requests-list`; компоненты: Alert, Button, EmptyState, Pagination, Progress, SearchInput, Select, Skeleton, Table
- Переходы: → `request-card` (выбор строки; сохраняется: фильтры, сортировка, страница; назад: назад, крошки); → `request-new` (`create` — «Создать»; сохраняется: —; назад: отмена возвращает сюда)
- Ситуации: `find-request`, `create-request`; сценарии: `schedule-visit`
- Данные: коллекция `requests-list` → `demo-data.json` `collections.requests-list` (empty 0 · few 1 · typical 60 · max 3 000); `request` → `objects.request.records` (`request-1` …), крайние случаи — `objects.request.edge_cases`
- Тексты — 15 ключей, строки — в разделе «Тексты»: `requests.list.empty-first-run.empty`, `requests.list.empty-filtered.empty`, `requests.list.reset-filters.action`, `requests.list.error-load.inline-message`, `requests.list.retry.action`, `requests.list.no-permission.title`, `requests.list.no-permission.body`, `requests.list.search.placeholder`, `requests.list.status-filter.placeholder`, `requests.list.create.action`, `requests.list.number.column-header`, `requests.list.client.column-header`, `requests.list.address.column-header`, `requests.list.visit-date.column-header`, `requests.list.status.column-header`; не этого этапа или нет строки: `requests.list.empty-first-run.empty`, `requests.list.empty-filtered.empty`, `requests.list.reset-filters.action`, `requests.list.error-load.inline-message`, `requests.list.retry.action`, `requests.list.no-permission.title`, `requests.list.no-permission.body`, `requests.list.search.placeholder`, `requests.list.status-filter.placeholder`, `requests.list.create.action`

### Обязательные состояния

| S-id | ключ | покрытие | почему в наборе |
|---|---|---|---|
| S01 | `empty-first-run` | дельта | на экране коллекция: ui:Table (ui:Table items=data:request); строка типа экрана «Список и таблица»; компонент ui:Table — строка «Список и таблица» |
| S02 | `empty-filtered` | дельта | поиск или фильтр: ui:SearchInput; строка типа экрана «Список и таблица»; строка типа экрана «Поиск»; компонент ui:SearchInput — строка «Поиск»; компонент ui:Table — строка «Список и таблица» |
| S04 | `partial-few` | не применимо: одна-три строки таблица держит в обычной раскладке | на экране коллекция: ui:Table (ui:Table items=data:request); строка типа экрана «Список и таблица»; компонент ui:Table — строка «Список и таблица» |
| S05 | `overflow-many` | не применимо: пагинация и счётчик найденного — в дереве блока requests-list | строка типа экрана «Список и таблица»; компонент ui:Table — строка «Список и таблица» |
| S07 | `loading-initial` | дельта | экран грузит данные (ui:Select items=data:request.status); строка типа экрана «Список и таблица»; строка типа экрана «Поиск»; строка «Экран или маршрут целиком» — у каждого экрана; компонент ui:SearchInput — строка «Поиск»; компонент ui:Table — строка «Список и таблица» |
| S08 | `loading-refresh` | дельта | строка типа экрана «Список и таблица»; компонент ui:Table — строка «Список и таблица» |
| S13 | `error-load` | дельта | экран грузит данные (ui:Select items=data:request.status); строка типа экрана «Список и таблица»; строка типа экрана «Поиск»; строка «Экран или маршрут целиком» — у каждого экрана; компонент ui:SearchInput — строка «Поиск»; компонент ui:Table — строка «Список и таблица»; отказ ситуации find-request |
| S14 | `error-action` | не применимо: список только ведёт к бланку, создание и его ошибка — на экране request-new | отказ ситуации create-request |
| S18 | `no-permission` | дельта | строка «Экран или маршрут целиком» — у каждого экрана; доступ к маршруту ограничен ролями (access: roles) |

По решению поверхности — `offline`: работа без сети — решение поверхности («Решения» map.md); состояние решает экран, в набор оно не входит.
