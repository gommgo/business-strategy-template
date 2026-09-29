<!-- Иллюстрация: вход холста фикстуры package-cabinet-defects, собранный canvas_input на основе package-cabinet. -->
# Тексты интерфейса — office, этап mockup
# Строки реестра texts.md: этап берёт approved; строка другого статуса — заглушка [PLACEHOLDER: текст на утверждении]. Тексты — дословно, maxlen — предел длины.

| ключ | роль | текст | maxlen | статус |
|---|---|---|---|---|
| `app.shell.help.link` | link | Помощь | 16 | approved (правка руками после сборки) |
| `app.shell.service-unavailable.banner` | banner | Кабинет временно недоступен. Заявки не пропадут — попробуйте позже | 120 | approved |
| `app.shell.maintenance.banner` | banner | {date} ночью кабинет будет недоступен — плановые работы | 120 | approved |
| `app.shell.session-expiry.confirm-title` | confirm-title | Продлить сеанс? | 40 | approved |
| `app.shell.session-expiry.action` | action | Продлить | 20 | approved |
| `app.shell.connection-lost.banner` | banner | Нет связи. Введённое сохранится и уйдёт, когда связь вернётся | 120 | approved |
| `requests.list.search.placeholder` | placeholder | Номер, клиент или адрес | 40 | approved |
| `requests.list.status-filter.placeholder` | placeholder | Все статусы | 24 | approved |
| `requests.list.create.action` | action | Создать заявку | 24 | approved |
| `requests.list.number.column-header` | column-header | Номер | 16 | approved |
| `requests.list.client.column-header` | column-header | Клиент | 16 | approved |
| `requests.list.address.column-header` | column-header | Адрес | 16 | approved |
| `requests.list.visit-date.column-header` | column-header | Дата замера | 16 | approved |
| `requests.list.status.column-header` | column-header | Статус | 16 | approved |
| `requests.list.empty-first-run.empty` | empty | Здесь появятся заявки с сайта и из звонков — первую можно создать кнопкой «Создать заявку» над списком | 140 | approved |
| `requests.list.empty-filtered.empty` | empty | По запросу «{query}» заявок нет | 80 | approved |
| `requests.list.reset-filters.action` | action | Сбросить фильтры | 24 | approved |
| `requests.list.error-load.inline-message` | inline-message | Список заявок не загрузился: нет ответа сервера | 100 | approved |
| `requests.list.retry.action` | action | Повторить | 16 | approved |
| `requests.list.no-permission.title` | title | Нет доступа к заявкам | 40 | approved |
| `requests.list.no-permission.body` | body | Доступ к заявкам выдаёт руководитель студии | 120 | approved |
| `requests.card.title.title` | title | Заявка {number} | 32 | approved |
| `requests.card.schedule.action` | action | Назначить замер | 24 | approved |
| `requests.card.complete.action` | action | Отметить замер | 24 | approved |
| `requests.card.error-load.inline-message` | inline-message | Заявка не загрузилась: нет ответа сервера | 100 | approved |
| `requests.card.retry.action` | action | Повторить | 16 | approved |
| `requests.card.error-action.inline-message` | inline-message | Не сохранилось — выбранное осталось в карточке, можно повторить | 100 | approved |
| `requests.card.no-permission.title` | title | Нет доступа к заявке | 40 | approved |
| `requests.card.no-permission.body` | body | Заявка есть, но открыть её может руководитель студии | 120 | approved |
| `requests.card.not-found.title` | title | Заявки нет | 40 | approved |
| `requests.card.not-found.body` | body | Проверьте номер в адресе: такой заявки нет или её убрали из списка | 120 | approved |
| `requests.card.back-to-list.link` | link | К списку заявок | 24 | approved |
| `requests.card.offline.banner` | banner | Нет связи: заявка показана из памяти, отметка замера уйдёт, когда связь вернётся | 120 | approved |
| `requests.new.saving.status` | status | Сохраняем заявку | 32 | approved |
| `requests.new.error-action.inline-message` | inline-message | Заявка не сохранилась — всё введённое на месте, можно повторить | 100 | approved |
| `requests.new.no-permission.title` | title | Нет доступа к созданию заявок | 40 | approved |
| `requests.new.no-permission.body` | body | Заявки создаёт менеджер по замерам | 120 | approved |
| `requests.new.client.label` | label | Клиент | 24 | approved |
| `requests.new.client.error` | error | Укажите имя или фамилию клиента | 60 | approved |
| `requests.new.phone.label` | label | Телефон | 24 | approved |
| `requests.new.phone.error` | error | Укажите телефон целиком, с кодом города | 60 | approved |
| `requests.new.address.label` | label | Адрес объекта | 24 | approved |
| `requests.new.address.error` | error | Укажите улицу и дом | 60 | approved |
| `requests.new.cancel.action` | action | Отмена | 16 | approved |
| `requests.new.create.action` | action | Создать заявку | 24 | approved |
| `plan.dashboard.empty-first-run.empty` | empty | Плана на этот месяц ещё нет — его ставит руководитель студии | 120 | approved |
| `plan.dashboard.no-permission.title` | title | Нет доступа к плану | 40 | approved |
| `plan.dashboard.no-permission.body` | body | План замеров видит менеджер по замерам | 120 | approved |
| `plan.dashboard.plan-tile.empty` | empty | Замеров в этом месяце ещё не было | 60 | approved |
| `plan.dashboard.plan-tile-error.inline-message` | inline-message | План не загрузился | 60 | approved |
| `system.not-found.title.title` | title | Такой страницы нет | 40 | approved |
| `system.not-found.body.body` | body | Адрес устарел или в нём опечатка | 120 | approved |
| `system.not-found.to-requests.link` | link | К заявкам | 24 | approved |
