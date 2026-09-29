# capability

> Иллюстрация: возможности поверхности `office` демо-кабинета фикстуры `cabinet` — для самопроверок утилит скилла, не
> данные проекта.

| slug | name | description | value | user | object | action | priority | trace | status |
|---|---|---|---|---|---|---|---|---|---|
| `create-request` | Создать заявку | Менеджер заводит заявку, которая пришла звонком | Звонок не теряется в блокноте | `` [`manager`] `` | `` `request` `` | `` `create` `` | `regular` | `—` | `draft` |
| `schedule-visit` | Назначить замер | Менеджер ставит заявке дату и замерщика | Клиент слышит дату замера в тот же день | `` [`manager`] `` | `` `request` `` | `` `schedule` `` | `hub` | `—` | `draft` |
| `mark-measured` | Отметить замер | Замерщик отмечает, что замер проведён | Офис узнаёт о замере без звонка | `` [`surveyor`] `` | `` `request` `` | `` `complete` `` | `critical` | `—` | `draft` |
| `track-plan` | Сверить план замеров | Менеджер видит, сколько замеров проведено против плана месяца | Видно, успевает ли студия | `` [`manager`] `` | `` `plan` `` | `—` | `regular` | `—` | `draft` |

## Паспорта

### schedule-visit

```yaml
need: клиент узнаёт дату замера, пока ещё выбирает подрядчика
trigger: новая заявка в списке; звонок клиента
outcome: заявка в статусе «замер назначен»
acceptance:
  - у заявки есть дата и замерщик
  - менеджер · новая заявка с сайта · назвать клиенту дату замера
frequency: hours-daily
error-cost: medium — клиент ждёт напрасно
reversibility: undo
scope: all
duration: instant
posture-exception: —
depends-on: —
metric: —
justification: —
ai: no
```

### mark-measured

```yaml
need: офис начинает смету сразу после замера
trigger: замер на объекте закончен
outcome: заявка в статусе «замер проведён»
acceptance:
  - у заявки статус «замер проведён» и время отметки
  - замерщик · вышел с объекта · сообщить офису о замере
frequency: daily
error-cost: medium — смета откладывается
reversibility: confirm
scope: own
duration: short
posture-exception: —
depends-on: —
metric: —
justification: —
ai: no
```
