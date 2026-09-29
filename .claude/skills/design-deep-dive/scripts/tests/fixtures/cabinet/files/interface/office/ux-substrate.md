# ux-substrate

> Иллюстрация: субстраты поверхности `office` демо-кабинета фикстуры `cabinet` — для самопроверок утилит скилла, не
> данные проекта.

| slug | name | description | type | situation | status |
|---|---|---|---|---|---|
| `requests-search` | Поиск заявок | Поле поиска по номеру, клиенту и адресу | `ввод` | `find-request` | `draft` |
| `status-filter` | Фильтр по статусу | Выбор статуса заявок в списке | `выбор` | `find-request` | `draft` |
| `requests-table` | Таблица заявок | Строки заявок: номер, клиент, адрес, дата замера, статус | `список` | `find-request` | `draft` |
| `open-create` | Переход к созданию | Команда создать заявку из списка | `команда` | `create-request` | `draft` |
| `client-input` | Ввод клиента | Имя или фамилия клиента | `ввод` | `create-request` | `draft` |
| `phone-input` | Ввод телефона | Телефон клиента | `ввод` | `create-request` | `draft` |
| `address-input` | Ввод адреса | Адрес объекта | `ввод` | `create-request` | `draft` |
| `save-request` | Сохранение заявки | Команда создать заявку из бланка | `команда` | `create-request` | `draft` |
| `request-fields` | Данные заявки | Номер, клиент, адрес, телефон, дата замера, статус | `инфо` | `schedule-visit` | `draft` |
| `schedule-command` | Назначение замера | Команда назначить дату и замерщика | `команда` | `schedule-visit` | `draft` |
| `measured-command` | Отметка замера | Команда отметить проведённый замер | `команда` | `mark-measured` | `draft` |
| `plan-progress` | Ход плана | Проведено замеров против плана месяца | `инфо` | `check-plan` | `draft` |
