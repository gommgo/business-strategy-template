---
slug: login-form
name: 'Форма входа'
description: 'Form-блок: header+body+footer, без aside'
interface-block: login-form
ux-substrates:
  - login-input
  - password-input
  - login-confirm
used-by-screens: [login]
status: stable
---

# login-form

Каноничный form-блок: заголовок-шапка, форма-тело, действие-футер.
`block-aside` нет — формы у нас не имеют боковой дорожки.

```yaml
tree:
  block-header:
    - ui:Stack gap=xs align=center
      - ui:Logo size=lg
      - ui:Text variant=h label='Вход в систему'
  block-body:
    - ui:Form
      - ui:Stack gap=md
        - ui:Field label='Логин'
          - ui:Input placeholder='username'
        - ui:Field label='Пароль'
          - ui:Input type=password
  block-footer:
    - ui:Stack gap=sm align=stretch
      - ui:Button variant=primary label='Войти' full-width=true
      - ui:Button variant=ghost   label='Забыли пароль?' full-width=true
```
