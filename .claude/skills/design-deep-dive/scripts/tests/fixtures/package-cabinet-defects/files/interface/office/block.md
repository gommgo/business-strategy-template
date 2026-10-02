# block

> Иллюстрация: блоки поверхности `office` демо-кабинета фикстуры `cabinet` — для самопроверок утилит скилла, не
> данные проекта.

| slug | name | description | zone | who | ux-substrates | entrypoint | transition-to-block | transition-from-zone | status |
|---|---|---|---|---|---|---|---|---|---|
| `requests-list` | Список заявок | Поиск, фильтр, таблица заявок и создание | `requests` | [`manager`, `surveyor`] | [`requests-search`, `status-filter`, `requests-table`, `open-create`] | true | [`request-details`] | — | `draft` |
| `request-details` | Карточка заявки | Данные заявки и команды замера | `request-card` | [`manager`, `surveyor`] | [`request-fields`, `schedule-command`, `measured-command`] | false | — | [`requests`] | `draft` |
| `request-form` | Бланк заявки | Поля новой заявки и сохранение | `requests` | [`manager`] | [`client-input`, `phone-input`, `address-input`, `save-request`] | false | [`request-details`] | — | `draft` |
| `plan-tile` | План месяца | Плитка «проведено против плана» | `plan` | [`manager`] | [`plan-progress`] | true | [`requests-list`] | — | `draft` |
