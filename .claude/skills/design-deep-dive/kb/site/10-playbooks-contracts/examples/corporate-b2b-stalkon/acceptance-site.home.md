# Блоки приёмки сайта для ACCEPTANCE.md — страница home (home-multipage)

Предложение K (09-ai-generation-evaluation) и J: блоки I–L после блоков A–H kimi. Пока kimi их не принял — проверяет Claude на шаге step:gates.

## I. SEO и мета
- I1 Ровно один `<h1>`, его текст — слот `hero.headline`.
- I2 `<title>`, `meta description`, `canonical` на себя, `<html lang>` заданы и уникальны.
- I3 H1, цены, условия и главный призыв есть в исходном HTML (curl без JS).
- I4 JSON-LD только типов ['Organization', 'WebSite']; каждое значение видно на странице.
- I5 `robots`: index.
- I6 `og:image` — абсолютный URL.

## J. Право
- J1 Согласие на ПД — отдельный неотмеченный чекбокс со ссылкой на текст согласия (req:LR-RU-01, 02).
- J2 Ссылка на политику ПД (/politika-konfidencialnosti/) у каждой формы и в подвале (req:LR-RU-05).
- J3 Реквизиты продавца в подвале — только из facts.md (req:LR-RU-13, 14).
- J4 Баннер cookie (opt-in): «Принять» и «Отклонить» равного вида; счётчики и пиксели — после выбора (req:LR-RU-10).
- J5 Маркировка чужих рекламных блоков: нет таких блоков.
- J6 Рассылка — отдельная неотмеченная галочка (req:LR-RU-11), если есть.

## K. Формы
- K1 Настоящий `<form>` с `type=submit`; отправка без JS-хитростей.
- K2 Поля и видимые подписи = набору lead-forms.yaml; autocomplete.
- K3 Нет запретов lead-forms.yaml `forbidden` (предотметка, «нажимая кнопку», disabled submit, «повторите почту» …).
- K4 Успех — страница «спасибо» или блок по `success.must_show`.
- K5 Антиспам: honeypot + time-trap, без видимой капчи.
- K6 Скрытые поля источника (utm_*, yclid, ym_client_id, landing_url, page_url, form_id, variant).

## L. События
- event:cta-click ← header.cta
- event:phone-click ← header.phone
- event:cta-click ← final-cta.cta
- L1 Каждое событие вызывается на своём триггере с именем из events.yaml.
- L2 `lead-submit` — только по успешному ответу сервера.
- L3 Счётчики — после согласия по юрисдикции.
- L4 Цели не ставятся на клик по кнопке.
