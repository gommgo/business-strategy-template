# situation

> Иллюстрация: ситуации поверхности `office` демо-кабинета фикстуры `cabinet` — для самопроверок утилит скилла, не
> данные проекта.

| slug | name | description | stage | who | when | action | goal | entry-data | exit-data | using-what | ux-substrate | block | jobs | capabilities | hypotheses | frequency | refusals | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `find-request` | Поиск заявки | Менеджер находит заявку в общем списке | `intake` | `manager` | клиент перезвонил | ищет по фамилии, номеру или адресу | ответить клиенту о его заявке | — | [`request`] | общий список заявок | [`requests-search`, `status-filter`, `requests-table`] | [`requests-list`] | — | [`schedule-visit`] | — | `hours-daily` | [`error-load`] | `draft` |
| `create-request` | Заведение заявки | Менеджер заводит заявку, пришедшую звонком | `intake` | `manager` | клиент позвонил | записывает имя, телефон и адрес | чтобы заявка попала в работу | — | [`request`] | бланк заявки | [`open-create`, `client-input`, `phone-input`, `address-input`, `save-request`] | [`requests-list`, `request-form`] | — | [`create-request`] | — | `daily` | [`error-action`] | `draft` |
| `schedule-visit` | Назначение замера | Менеджер ставит заявке дату и замерщика | `intake` | `manager` | заявка новая | выбирает дату и замерщика | чтобы клиент узнал дату замера | [`request`] | [`request`] | календарь замерщиков | [`request-fields`, `schedule-command`] | [`request-details`] | — | [`schedule-visit`] | — | `hours-daily` | [`error-action`] | `draft` |
| `mark-measured` | Отметка замера | Замерщик отмечает проведённый замер | `visit` | `surveyor` | замер на объекте закончен | отмечает замер в заявке | чтобы офис начал смету | [`request`] | [`request`] | список заявок замерщика | [`measured-command`] | [`request-details`] | — | [`mark-measured`] | — | `daily` | [`error-action`, `offline`] | `draft` |
| `check-plan` | Сверка с планом | Менеджер смотрит, сколько замеров проведено против плана | `planning` | `manager` | в конце дня | смотрит ход плана месяца | понять, успевает ли студия | [`plan`] | — | сводка плана | [`plan-progress`] | [`plan-tile`] | — | [`track-plan`] | — | `daily` | [`error-load`] | `draft` |
