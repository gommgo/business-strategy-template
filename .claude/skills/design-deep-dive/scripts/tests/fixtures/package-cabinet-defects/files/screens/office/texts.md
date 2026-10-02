# texts

> Иллюстрация: реестр текстов интерфейса поверхности `office` демо-кабинета фикстуры `cabinet` — для самопроверок
> утилит скилла, не данные проекта; тексты — демо. Форма — `docs/projects/_template/screens/_template/texts.md`.

| key | role | text | maxlen | action | object | group | context | status |
|---|---|---|---|---|---|---|---|---|
| `app.shell.help.link` | `link` | Помощь | 16 | — | — | — | ссылка на справку в шапке каркаса | `approved` |
| `app.shell.service-unavailable.banner` | `banner` | Кабинет временно недоступен. Заявки не пропадут — попробуйте позже | 120 | — | — | — | баннер под шапкой при сбое сервиса | `approved` |
| `app.shell.maintenance.banner` | `banner` | {date} ночью кабинет будет недоступен — плановые работы | 120 | — | — | — | подстановка date — дата работ | `approved` |
| `app.shell.session-expiry.confirm-title` | `confirm-title` | Продлить сеанс? | 40 | — | — | — | окно до истечения сессии | `approved` |
| `app.shell.session-expiry.action` | `action` | Продлить | 20 | — | — | — | кнопка в окне продления сессии | `approved` |
| `app.shell.connection-lost.banner` | `banner` | Нет связи. Введённое сохранится и уйдёт, когда связь вернётся | 120 | — | — | — | баннер при потере сети | `approved` |
| `requests.list.search.placeholder` | `placeholder` | Номер, клиент или адрес | 40 | — | `request` | — | подсказка в пустом поле поиска списка | `approved` |
| `requests.list.status-filter.placeholder` | `placeholder` | Все статусы | 24 | — | `request` | — | фильтр по статусу без выбора | `approved` |
| `requests.list.create.action` | `action` | Создать заявку | 24 | `create` | `request` | — | главная кнопка шапки списка | `approved` |
| `requests.list.number.column-header` | `column-header` | Номер | 16 | — | `request` | колонки списка заявок | — | `approved` |
| `requests.list.client.column-header` | `column-header` | Клиент | 16 | — | `request` | колонки списка заявок | — | `approved` |
| `requests.list.address.column-header` | `column-header` | Адрес | 16 | — | `request` | колонки списка заявок | — | `approved` |
| `requests.list.visit-date.column-header` | `column-header` | Дата замера | 16 | — | `request` | колонки списка заявок | — | `approved` |
| `requests.list.status.column-header` | `column-header` | Статус | 16 | — | `request` | колонки списка заявок | — | `approved` |
| `requests.list.empty-first-run.empty` | `empty` | Здесь появятся заявки с сайта и из звонков — первую можно создать кнопкой «Создать заявку» над списком | 140 | — | `request` | — | пустой список: указывает на кнопку в шапке | `approved` |
| `requests.list.empty-filtered.empty` | `empty` | По запросу «{query}» заявок нет | 80 | — | `request` | — | подстановка query — текст поиска | `approved` |
| `requests.list.reset-filters.action` | `action` | Сбросить фильтры | 24 | — | — | — | кнопка в пустом результате поиска | `approved` |
| `requests.list.error-load.inline-message` | `inline-message` | Список заявок не загрузился: нет ответа сервера | 100 | — | `request` | — | ошибка загрузки списка | `approved` |
| `requests.list.retry.action` | `action` | Повторить | 16 | — | — | — | повтор загрузки списка | `approved` |
| `requests.list.no-permission.title` | `title` | Нет доступа к заявкам | 40 | — | `request` | — | заголовок экрана без прав | `approved` |
| `requests.list.no-permission.body` | `body` | Доступ к заявкам выдаёт руководитель студии | 120 | — | `request` | — | — | `approved` |
| `requests.card.title.title` | `title` | Заявка {number} | 32 | — | `request` | — | подстановка number — номер заявки | `approved` |
| `requests.card.schedule.action` | `action` | Назначить замер | 24 | `schedule` | `request` | — | главная кнопка карточки | `approved` |
| `requests.card.complete.action` | `action` | Отметить замер | 24 | `complete` | `request` | — | кнопка замерщика в карточке | `approved` |
| `requests.card.error-load.inline-message` | `inline-message` | Заявка не загрузилась: нет ответа сервера | 100 | — | `request` | — | — | `approved` |
| `requests.card.retry.action` | `action` | Повторить | 16 | — | — | — | повтор загрузки карточки | `approved` |
| `requests.card.error-action.inline-message` | `inline-message` | Не сохранилось — выбранное осталось в карточке, можно повторить | 100 | — | `request` | — | ошибка назначения или отметки замера | `approved` |
| `requests.card.no-permission.title` | `title` | Нет доступа к заявке | 40 | — | `request` | — | — | `approved` |
| `requests.card.no-permission.body` | `body` | Заявка есть, но открыть её может руководитель студии | 120 | — | `request` | — | — | `approved` |
| `requests.card.not-found.title` | `title` | Заявки нет | 40 | — | `request` | — | заявки по адресу нет или она скрыта | `approved` |
| `requests.card.not-found.body` | `body` | Проверьте номер в адресе: такой заявки нет или её убрали из списка | 120 | — | `request` | — | — | `approved` |
| `requests.card.back-to-list.link` | `link` | К списку заявок | 24 | — | — | — | путь из пустой карточки | `approved` |
| `requests.card.offline.banner` | `banner` | Нет связи: заявка показана из памяти, отметка замера уйдёт, когда связь вернётся | 120 | `complete` | `request` | — | что доступно без сети и что отложено | `approved` |
| `requests.new.saving.status` | `status` | Сохраняем заявку | 32 | `create` | `request` | — | — | `approved` |
| `requests.new.error-action.inline-message` | `inline-message` | Заявка не сохранилась — всё введённое на месте, можно повторить | 100 | `create` | `request` | — | — | `approved` |
| `requests.new.no-permission.title` | `title` | Нет доступа к созданию заявок | 40 | — | `request` | — | — | `approved` |
| `requests.new.no-permission.body` | `body` | Заявки создаёт менеджер по замерам | 120 | — | `request` | — | — | `approved` |
| `requests.new.client.label` | `label` | Клиент | 24 | — | `request` | поля бланка заявки | — | `approved` |
| `requests.new.client.error` | `error` | Укажите имя или фамилию клиента | 60 | — | `request` | — | — | `approved` |
| `requests.new.phone.label` | `label` | Телефон | 24 | — | `request` | поля бланка заявки | — | `approved` |
| `requests.new.phone.error` | `error` | Укажите телефон целиком, с кодом города | 60 | — | `request` | — | — | `approved` |
| `requests.new.address.label` | `label` | Адрес объекта | 24 | — | `request` | поля бланка заявки | — | `approved` |
| `requests.new.address.error` | `error` | Укажите улицу и дом | 60 | — | `request` | — | — | `approved` |
| `requests.new.cancel.action` | `action` | Отмена | 16 | — | — | — | возврат к списку без сохранения | `approved` |
| `requests.new.create.action` | `action` | Создать заявку | 24 | `create` | `request` | — | главная кнопка бланка | `approved` |
| `plan.dashboard.empty-first-run.empty` | `empty` | Плана на этот месяц ещё нет — его ставит руководитель студии | 120 | — | `plan` | — | — | `approved` |
| `plan.dashboard.no-permission.title` | `title` | Нет доступа к плану | 40 | — | `plan` | — | — | `approved` |
| `plan.dashboard.no-permission.body` | `body` | План замеров видит менеджер по замерам | 120 | — | `plan` | — | — | `approved` |
| `plan.dashboard.plan-tile.empty` | `empty` | Замеров в этом месяце ещё не было | 60 | — | `plan` | — | плитка без данных | `approved` |
| `plan.dashboard.plan-tile-error.inline-message` | `inline-message` | План не загрузился | 60 | — | `plan` | — | ошибка плитки | `approved` |
| `system.not-found.title.title` | `title` | Такой страницы нет | 40 | — | — | — | — | `approved` |
| `system.not-found.body.body` | `body` | Адрес устарел или в нём опечатка | 120 | — | — | — | — | `approved` |
| `system.not-found.to-requests.link` | `link` | К заявкам | 24 | — | — | — | путь со служебного экрана | `approved` |
