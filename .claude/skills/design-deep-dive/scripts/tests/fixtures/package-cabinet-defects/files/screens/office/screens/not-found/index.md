---
# иллюстрация: экран демо-кабинета фикстуры cabinet — для самопроверок утилит скилла, не данные проекта
slug: not-found
name: 'Страница не найдена'
description: 'Служебный экран для адреса вне реестра маршрутов с путём к списку заявок'
type: service
object: —
main-task: —
key-action: —
zone: —
shell: app-shell
blocks: —
situations: —
who: [manager, surveyor]
route: '*'
params: —
access: authenticated
indexed: false
viewport: any
transitions-to-screen:
  - {to: requests-list, trigger: 'ссылка «К заявкам»', keeps: '—', back: 'назад в браузере'}
status: stable
---

# not-found

Служебный экран маршрута вне реестра: каркас на месте, в основном содержимом — что случилось и путь к списку заявок.

```yaml
slot-fills:
  main:
    - layout:stack align=center gap=md:
        - text:system.not-found.title.title
        - text:system.not-found.body.body
        - ui:Link:
            - text:system.not-found.to-requests.link
  overlay: —

states:
  loading-initial: 'не применимо: служебный экран статичный, приходит вместе с каркасом'
  error-load: 'не применимо: служебный экран не грузит данных'
```
