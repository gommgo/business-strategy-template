---
# иллюстрация: экран демо-кабинета фикстуры cabinet — для самопроверок утилит скилла, не данные проекта
slug: plan-dashboard
name: 'План замеров'
description: 'Сколько замеров проведено против плана месяца'
type: dashboard
object: plan
main-task: track-plan
key-action: —
zone: plan
shell: app-shell
blocks: [plan-tile]
situations: [check-plan]
who: [manager]
route: /
params: —
access: roles
indexed: false
viewport: any
entrypoint: true
transitions-to-screen:
  - {to: requests-list, trigger: 'переход по плитке плана', keeps: '—', back: 'назад'}
status: stable
---

# plan-dashboard

Стартовый экран менеджера — плитка плана месяца. Плитка грузит данные сама, поэтому её загрузка и ошибка — в её
разделе `states`.

```yaml
slot-fills:
  main:
    - layout:grid columns=3 gap=md:
        - block:plan-tile
  overlay: —

states:
  empty-first-run:
    main:
      - ui:EmptyState:
          - text:plan.dashboard.empty-first-run.empty
  partial-few: 'не применимо: на экране одна плитка'
  loading-initial: 'не применимо: плитка грузит данные сама и держит свою загрузку'
  error-load: 'не применимо: плитка держит свою ошибку, других источников у экрана нет'
  partial-failure: 'не применимо: у экрана один источник — плитка'
  no-permission:
    main:
      - layout:stack align=center gap=md:
          - text:plan.dashboard.no-permission.title
          - text:plan.dashboard.no-permission.body
```
