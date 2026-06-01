---
slug: studies-workspace
name: 'Рабочее место исследований'
description: 'Desktop master-detail: фильтры + список + превью'
shell: app-shell
blocks: [filters-panel, studies-list, study-preview]
situations: [browse-studies, open-study-preview, archive-study]
who: [doctor, nurse]
route: /studies
viewport: desktop
entrypoint: false
transitions-to-screen: [study-detail, confirm-archive]
status: draft
---

# studies-workspace

Главный desktop-экран сценария `studies-browse`. Слева — панель
фильтров, в центре — список исследований, справа — превью выбранного.
Переход к полному card — через `study-detail`. Архивация —
через overlay `confirm-archive`. На mobile сценарий разворачивается
через flow `studies-browse` в три отдельных screen.

```yaml
slot-fills:
  header:
    - ui:Row justify=between align=center gap=md
      - ui:Logo
      - ui:Nav items=[Studies, Patients, Reports]
      - ui:UserMenu
  side:    block:filters-panel
  main:    block:studies-list
  detail:  block:study-preview
  overlay: —
  footer:
    - ui:StatusBar

states:
  loading:
    main:   [ui:Skeleton variant=list rows=12]
    detail: [ui:Skeleton variant=card]
  empty:
    main:
      - ui:EmptyState
          illustration: no-studies
          title: 'Исследований пока нет'
          description: 'Создайте первое или измените параметры фильтра'
          action: ui:Button variant=primary icon=plus label='Новое исследование'
    detail: [ui:EmptyState illustration: select-study, title: 'Выберите исследование']
  error:
    main:
      - ui:ErrorState
          title: 'Не удалось загрузить список'
          retry: true
  permission-denied:
    main:
      - ui:Stack gap=lg align=center
        - ui:AccessDeniedState
            title: 'Доступ ограничен'
            description: 'Раздел доступен ролям doctor и nurse'
        - ui:Button variant=ghost label='Вернуться на главную'
    side:   —
    detail: —
  offline:
    main: [ui:OfflineState retry=true]
  not-found:
    main: [ui:NotFoundState]
```
