# zone

> Иллюстрация: зоны поверхности `office` демо-кабинета фикстуры `cabinet` — для самопроверок утилит скилла, не
> данные проекта.

| slug | name | description | parent-zone | order | object | status |
|---|---|---|---|---|---|---|
| `requests` | Заявки | Список заявок и работа с ними | — | 1 | `request` | `draft` |
| `request-card` | Карточка заявки | Одна заявка: данные и замер | `requests` | — | `request` | `draft` |
| `plan` | План замеров | План месяца и ход его выполнения | — | 2 | `plan` | `draft` |
