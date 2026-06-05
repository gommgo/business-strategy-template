---
slug: login
name: 'Вход'
description: 'Центрированная форма входа; единая для desktop и mobile'
shell: auth-shell
blocks: [login-form]
situations: [enter-credentials]
who: [any]
route: /login
viewport: any
entrypoint: true
transitions-to-screen: [studies-workspace, studies-list-m]
status: stable
---

# login

Глобальный entrypoint системы. Один и тот же экран на desktop и
mobile (`viewport: any`), потому что облик центрированной формы не
требует viewport-вариативности — только адаптива внутри блока, что
закрыто `@sftbmb/ui`. После успешного входа — переход на
рабочий экран (desktop) или mobile-master.

```yaml
slot-fills:
  main: block:login-form

states:
  loading:
    main: [ui:Skeleton variant=form rows=3]
  error:
    main:
      - ui:Stack gap=md
        - ui:ErrorState
            title: 'Не удалось войти'
            description: 'Проверьте логин и пароль'
        - block:login-form
  offline:
    main: [ui:OfflineState retry=true]
```
