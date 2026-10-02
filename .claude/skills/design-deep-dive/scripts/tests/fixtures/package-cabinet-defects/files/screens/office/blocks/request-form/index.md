---
# иллюстрация: блок демо-кабинета фикстуры cabinet — для самопроверок утилит скилла, не данные проекта
slug: request-form
name: 'Бланк заявки'
description: 'Поля новой заявки — клиент, телефон, адрес — и сохранение'
interface-block: request-form
ux-substrates:
  - client-input
  - phone-input
  - address-input
  - save-request
data:
  item: data:request
source: screen
form:
  - field: data:request.client
    control: TextInput
    required: —
    format: —
    validation: 'имя или фамилия клиента; проверка при отправке'
    error: text:requests.new.client.error
    default: 'нет: имя называет клиент'
    autocomplete: 'нет: имя клиента, а не менеджера'
  - field: data:request.phone
    control: TextInput
    required: —
    format: 'телефон в формате +7'
    validation: 'десять цифр после +7; проверка при уходе с поля'
    error: text:requests.new.phone.error
    default: 'нет: номер называет клиент'
    autocomplete: 'нет: телефон клиента, а не менеджера'
  - field: data:request.address
    control: TextInput
    required: —
    format: —
    validation: 'улица и дом; проверка при отправке'
    error: text:requests.new.address.error
    default: 'нет: адрес объекта называет клиент'
    autocomplete: 'нет: адрес объекта, а не менеджера'
used-by-screens: [request-new]
status: stable
---

# request-form

Бланк заявки со слов клиента: три поля и сохранение главной кнопкой подвала.

```yaml
tree:
  block-body:
    - layout:stack gap=md:
        - ui:Field:
            - ui:Field.Label:
                - text:requests.new.client.label
            - ui:TextInput value=data:request.client
            - ui:Field.Error:
                - text:requests.new.client.error
        - ui:Field:
            - ui:Field.Label:
                - text:requests.new.phone.label
            - ui:TextInput value=data:request.phone
            - ui:Field.Error:
                - text:requests.new.phone.error
        - ui:Field:
            - ui:Field.Label:
                - text:requests.new.address.label
            - ui:TextInput value=data:request.address
            - ui:Field.Error:
                - text:requests.new.address.error
  block-footer:
    - layout:row justify=end gap=sm:
        - ui:Button level=tertiary:
            - text:requests.new.cancel.action
        - ui:Button level=primary action=create:
            - text:requests.new.create.action
```
