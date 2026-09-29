---
# иллюстрация: экран демо-кабинета фикстуры cabinet — для самопроверок утилит скилла, не данные проекта
slug: request-new
name: 'Новая заявка'
description: 'Бланк заявки, пришедшей звонком: клиент, телефон, адрес'
type: edit
object: request
main-task: create-request
key-action: create
zone: requests
shell: app-shell
blocks: [request-form]
situations: [create-request]
who: [manager]
route: /requests/new
params: —
access: roles
indexed: false
viewport: any
transitions-to-screen:
  - {to: request-card, trigger: create, keeps: '—', back: 'назад к списку заявок'}
  - {to: requests-list, trigger: 'отмена', keeps: 'фильтры, сортировка, страница', back: 'кнопка «Создать заявку»'}
status: stable
---

# request-new

Бланк новой заявки со слов клиента. После создания открывается карточка новой заявки.

```yaml
slot-fills:
  main: block:request-form
  overlay: —

states:
  loading-initial: 'не применимо: у бланка нет справочников — поля пустые сразу'
  saving:
    main:
      - ui:Progress:
          - text:requests.new.saving.status
      - block:request-form
  success: 'не применимо: после создания открывается карточка новой заявки'
  error-action:
    main:
      - ui:Alert:
          - text:requests.new.error-action.inline-message
      - block:request-form
  error-load: 'не применимо: бланк не грузит данных'
  no-permission:
    main:
      - layout:stack align=center gap=md:
          - text:requests.new.no-permission.title
          - text:requests.new.no-permission.body
```
