# K/03 · Ворота страницы v1.1 → v1.2 на 8 страницах: 5 из выборки M и 3 демо генераторов

Опыт агента оценки (волна 3 site-research): данные и прогоны 1–2 — K3, адреса узлов axe, прогон 3, README — K4; 2026-09-24 22:34.

**Цель.** Проверить ворота `07-seo-geo-performance-analytics/page-gates.yaml` и их автопроверку `../../scripts/site/page_gates.py` на
живых страницах: сколько провалов уровня B верные, сколько ложных; откалибровать строки, дающие ложные блокеры, и не пропустить
настоящие. Вход задания K: «чек-лист и ворота на 5 страницах M и 3 открытых демо генераторов».

## Страницы

| id | URL | Группа | Профиль (решение 20: уровень по умолчанию) | Право |
|---|---|---|---|---|
| ru-azbukaokon | https://azbukaokon63.ru/ | M: лидогенерация РФ | landing-lead-services@L1 | ru |
| en-capsule | https://capsulecrm.com/ | M: SaaS, международный | landing-saas@L1 | eu |
| ru-matemarketing | https://matemarketing.ru/ | M: мероприятие РФ | landing-event@L1 | ru |
| en-headspace | https://www.headspace.com/ | M: приложение, международный | landing-app@L1 | eu |
| mp-taradash-home | https://www.chicagodivorceatty.com/ | M: многостраничник США | home-multipage@L1 | none |
| demo-lovable-evebcn | https://evebcn.com/ | сайт на Lovable («Made with Lovable», винные туры) | home-multipage@L1 | eu |
| demo-framer-makro | https://makro.framer.website/ | демо шаблона SaaS с маркетплейса Framer («View Live Demo») | landing-saas@L1 | none |
| demo-durable-naturepure | https://naturepurecleaning.com/ | сайт на Durable (список makingthatwebsite.com «12 Real-world Durable AI website examples», 2024-09; в HTML 54 упоминания durable) | home-multipage@L1 | none |

Пять страниц — из итогового `02-site-types/pages.csv` (M2), три — открытые демо и витрины генераторов (без входа, формы не
отправлялись). `jurisdiction` — профиль права строки ворот: `eu` у международных страниц, открытых из ЕС, `none` — строки
LEGAL не считаются (США, демо шаблона).

## Входы и команды

| Вход | Откуда | Команда |
|---|---|---|
| анатомия (десктоп и телефон) | M: `../../M/03-sample/<id>/` (5 страниц); демо — `demos/<id>/` | `../../scripts/site/page_anatomy.py URL OUT [--mobile] --inp` (K3, 21:03–21:53; Durable десктоп — попытка 2, попытка 1 — goto timeout, в `demos/demo-durable-naturepure/try1/`) |
| geo (сырой HTML, robots, боты) | H: `../../H/02-geo-probe-sample-m/out/` (4); свои — `geo/` (taradash и 3 демо) | `../../scripts/site/geo_probe.py URL` (K3, 21:27) |
| ia (сайт) | G: `../../G/01-ia-probe/out/taradash/ia.json` | — |
| axe, счётчики | I: `../../I/02-axe/out/` (3); свои — `axe/` (5) | `../../I/02-axe/run_axe.py` (K3, 21:32–21:46) |
| axe с адресами узлов | `axe-targets/<id>.json` (7 из 8) | `run_axe_targets.py ID URL MARKET axe-targets` (K3, 22:02–22:15; axe-core 4.13, десктоп 1440×900, баннер не трогается) → `axe_classify.py` → `axe_classes.tsv` |
| сырой HTML и CSS | `pages/<id>.html`, `.css`; журнал `fetch_log.tsv` | `fetch_html.py` (K3, 21:00–21:01) |
| прогон ворот | `out/<id>.json`, `result.tsv`, `matrix.md`, `b_list.tsv` | `python3 99-raw/experiments/K/03-gates-v1/run_gates.py` (браузер не нужен; берёт axe с адресами узлов, если снят) |

Прогон 1 (v1.1) — `run1-v1.1/`; прогон 2 (v1.2, код K3) — `run2-v1.2/`; прогон 3 (v1.2, K4) — файлы в корне опыта. Резервы
кода и строк до правок: `page_gates.v0.py`, `page_gates.v1.1-before-K3.py`, `page_gates.v1.2-before-K4.py`,
`page-gates.v0-H2.yaml`, `page-gates.v1.yaml`, `page-gates.v1-before-K2.yaml`, `page-gates.v1.1-before-K3.yaml` (= строки до K4),
`run_gates.before-K4.py`; `make_v1.py` — сборка v1 (K).

**Условия.** Chromium 153.0.8010.12 headless (Playwright); десктоп 1440×900, CPU ×1; телефон 412×839, CPU ×4; сеть без
троттлинга (строки LCP телефона помечены `lab-unthrottled`: диагностика, не приёмка); VPN с раздельной маршрутизацией — зарубежные
сайты через выход в Литве (у части замеров проверка маршрута не ответила — `route_before.split = None`), русские — с российского
адреса; язык контекста en-US или ru-RU по рынку. Анатомия M — 24.09 13:02–17:00, демо — 21:03–21:53. Браузер — под двумя
блокировками (`.locks/browser.lock` тройки и site), очередь делили агенты creative: axe с адресами узлов для Durable не снят (ждал
блокировку до остановки K3 в 22:17).

## Итог по страницам (прогон 3, v1.2)

| Страница | Вердикт | строк B | строк S | ворот B | ворот S | ворот D | PASS | SKIP |
|---|---|---|---|---|---|---|---|---|
| ru-azbukaokon | blocked | 6 | 29 | 4 | 17 | 2 | 12 | 1 |
| en-capsule | blocked | 5 | 13 | 3 | 7 | 1 | 20 | 1 |
| ru-matemarketing | accepted_with_notes | 0 | 11 | 0 | 6 | 0 | 28 | 0 |
| en-headspace | blocked | 4 | 21 | 3 | 13 | 2 | 14 | 1 |
| mp-taradash-home | accepted_with_notes | 0 | 5 | 0 | 3 | 1 | 30 | 0 |
| demo-lovable-evebcn | blocked | 5 | 13 | 3 | 8 | 1 | 19 | 1 |
| demo-framer-makro | blocked | 1 | 6 | 1 | 3 | 2 | 22 | 2 |
| demo-durable-naturepure | blocked | 2 | 17 | 2 | 11 | 1 | 14 | 2 |

Строка — ворота × устройство (LEGAL и PERF считаются на двух устройствах); «ворот» — по худшему устройству.

## Ворота × страницы (прогон 3; B / S / D — провал, PASS, SKIP — нет данных, · — строка не считалась)

| Ворота | azbuka | capsule | matemark | headspace | taradash | Lovable | Framer | Durable |
|---|---|---|---|---|---|---|---|---|
| SG-PERF-01 | S | PASS | PASS | B | PASS | PASS | PASS | S |
| SG-PERF-02 | S | PASS | PASS | S | PASS | PASS | PASS | PASS |
| SG-PERF-03 | S | PASS | PASS | S | S | B | PASS | S |
| SG-PERF-04 | PASS | PASS | PASS | PASS | PASS | PASS | SKIP | SKIP |
| SG-PERF-05 | S | S | PASS | S | PASS | S | PASS | S |
| SG-PERF-06 | PASS | PASS | PASS | PASS | PASS | D | D | PASS |
| SG-PERF-09 | S | PASS | PASS | PASS | PASS | PASS | PASS | S |
| SG-WEIGHT-01 | S | S | S | PASS | PASS | S | PASS | PASS |
| SG-WEIGHT-02 | S | S | S | PASS | PASS | S | PASS | PASS |
| SG-WEIGHT-03 | S | S | PASS | S | PASS | S | S | S |
| SG-WEIGHT-04 | S | S | PASS | S | PASS | PASS | PASS | PASS |
| SG-WEIGHT-05 | S | S | PASS | S | S | S | S | S |
| SG-WEIGHT-06 | S | S | PASS | S | S | S | S | S |
| SG-WEIGHT-07 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| SG-WEIGHT-09 | PASS | D | S | D | PASS | PASS | PASS | PASS |
| SG-SEO-01 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| SG-SEO-02 | S | PASS | PASS | PASS | PASS | PASS | PASS | S |
| SG-SEO-03 | PASS | PASS | PASS | S | PASS | PASS | D | PASS |
| SG-SEO-04 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| SG-GEO-01 | D | PASS | PASS | PASS | PASS | S | PASS | S |
| SG-GEO-02 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | B |
| SG-A11Y-01 | B | B | S | B | PASS | S | B | B |
| SG-A11Y-02 | S | PASS | PASS | S | PASS | PASS | PASS | PASS |
| SG-A11Y-08 | SKIP | SKIP | PASS | SKIP | PASS | SKIP | SKIP | SKIP |
| SG-LEGAL-01 | S | B | S | S | · | B | · | · |
| SG-LEGAL-02 | S | B | S | B | · | B | · | · |
| SG-LEGAL-03 | B | · | · | · | · | · | · | · |
| SG-LEGAL-04 | PASS | · | · | S | · | · | · | · |
| SG-LEGAL-05 | B | · | PASS | · | · | · | · | · |
| SG-LEGAL-07 | S | · | PASS | · | · | · | · | · |
| SG-SEO-05 | D | PASS | PASS | PASS | D | PASS | PASS | D |
| SG-SEO-06 | · | · | · | · | PASS | · | · | · |
| SG-SEO-08 | · | · | · | · | PASS | · | · | · |
| SG-NAV-01 | · | · | · | · | PASS | · | · | · |
| SG-NAV-02 | · | · | · | · | PASS | · | · | · |
| SG-MOB-01 | B | PASS | PASS | D | PASS | PASS | PASS | PASS |
| SG-MOB-02 | S | PASS | PASS | S | PASS | PASS | PASS | S |
| SG-CONTENT-05 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| SG-CONTENT-06 | PASS | PASS | PASS | S | PASS | PASS | PASS | PASS |
| SG-CONTENT-07 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | S |

Не считались ни на одной странице (нет входа — человек, код, поле, curl): PERF-07, PERF-08, PERF-10, PERF-11, PERF-12, PERF-13, PERF-14, PERF-15, WEIGHT-08, A11Y-03, A11Y-04, A11Y-05, A11Y-06, A11Y-07, LEGAL-06, LEGAL-08, LEGAL-09, CONTENT-01, CONTENT-02, CONTENT-03, CONTENT-04, SEO-07.

## Разбор B: 32 → 25 → 23

| Страница | Ворота × устройство | Прогон 1 (v1.1) | Что на странице | Прогон 3 (v1.2) | Итог разбора |
|---|---|---|---|---|---|
| azbuka | SG-PERF-03 телефон | B (0,42) | сумма всех сдвигов 0,42, web-vitals CLS окна сессии 0,15 | S | **ложный B** — правка K3: `fin.wv_cls` |
| azbuka | SG-LEGAL-03 ×2 | B | галочка «согласен с политикой» — не отдельное согласие на ПД | B | верный (152-ФЗ в ред. 156-ФЗ) |
| azbuka | SG-LEGAL-05 ×2 | B | ОГРНИП нет нигде на странице (не только в подвале) | B | верный |
| azbuka | SG-MOB-01 телефон | B (45 px) | область телефона расширена: 457 > 412 px | B | верный |
| azbuka | SG-A11Y-01 | B | button-name 12, label 2, link-name 47, meta-viewport; контраст призывов 16 узлов («ЗАКАЗАТЬ» 3,99:1), формы 10 | B | верный |
| capsule | SG-LEGAL-01 ×2 | B | до выбора — события GA4 и Ads, cookie UET (MUID, _uetsid) | B | верный |
| capsule | SG-LEGAL-02 ×2 | B | модальный баннер CookieYes без «Отклонить» на первом уровне | B | верный (подтверждено данными баннера) |
| capsule | SG-A11Y-01 | B | link-name 5; второй `meta viewport` с `user-scalable=0` | B | верный |
| matemark | SG-GEO-01 телефон | B (h1-js-only) | H1 в сыром HTML есть; `innerText` склеил слова на скрытых `<br>` | PASS | **ложный B** — правка K3: сверка буквами |
| matemark | SG-A11Y-01 | B | контраст только у неключевых узлов: подписи спикеров 4,34:1, текст о cookie в подвале 2,95:1 (12 px, 10 358 px от верха; настоящий баннер — отдельный элемент) | S | **ложный B** — правка K4: контраст по классам узлов |
| headspace | SG-PERF-01 телефон | B (5 640 мс) | LCP 5,6 с даже без троттлинга сети | B | верный (с троттлингом хуже) |
| headspace | SG-MOB-01 телефон | B (1 307 px) | дорожка карусели под `html, body {overflow-x: hidden}`, область не расширена | D | **ложный B** — правка K3 |
| headspace | SG-LEGAL-01 ×2 | B | до выбора только `gtm.js` и SDK Amplitude, без событий и cookie | S | **ложный B** `[спорно]` — правка K3 (передача IP поставщику остаётся) |
| headspace | SG-LEGAL-02 ×2 | B | OneTrust: «I Agree» и «Sharing Settings», отказа на первом уровне нет | B | верный (баннер при выходе из ЕС; CMP таргетирует по стране) |
| headspace | SG-LEGAL-04 ×2 | B | у формы нет ссылки на уведомление | S | **завышен** — правка K3: ЕС — S (LR-EU-06) |
| headspace | SG-A11Y-01 | B | button-name 7; лид «Feel less anxious» 1,66:1, «Try for free» 3,74:1 | B | верный |
| Lovable | SG-PERF-03 телефон | B (0,46) | один сдвиг 0,46 при прокрутке (вероятно, ленивое монтирование секции) | B | верный |
| Lovable | SG-LEGAL-01 ×2 | B | до выбора — события GA4 и Ads (возможно, Consent Mode без cookie) | B | верный `[спорно]` |
| Lovable | SG-LEGAL-02 ×2 | B | «REJECT» контуром против сплошного «ACCEPT ALL» | B | верный (эвристика `cmp_reject_equal` — подтверждено размерами кнопок) |
| Lovable | SG-A11Y-01 | B | контраст 27 узлов — все неключевые (карточки туров, H2 ниже первого экрана 2,8:1 при 36 px) | S | **ложный B** — правка K4 |
| Framer | SG-A11Y-01 | B | button-name 3, link-name 1; контраст «Trusted by solopreneurs» 2,99:1 в первом экране | B | верный (класс «лид» у надписи шаблона — эвристика) |
| Durable | SG-GEO-02 | B | `robots.txt`: `Disallow: /` для всех ботов | B | верный |
| Durable | SG-A11Y-01 | B | link-name 2 (контраста в axe нет) | B | верный |

Итог: из 32 строк B прогона 1 — **9 ложных или завышенных** (28 %; из них 2 `[спорно]`), 23 верных. Прогон 3 оставляет 23 строки B
(16 пар «страница × ворота»), ложных среди них не найдено; с оговорками — LEGAL-01 Lovable (Consent Mode), LEGAL-02 (эвристика
баннера — подтверждать кадром), ключевой контраст (класс узла — эвристика).

## Новые D прогона 3 — SG-PERF-06 «H1 выпал из LCP» (creative E/01)

- **Framer, оба устройства — D**: H1 в обёртке `data-framer-appear-id` со `style="opacity:0.001;transform:translateY(48px)"` — H1
  остаётся кандидатом LCP, но время LCP раньше, чем текст виден (creative E/01, вариант `opacity: .01`).
- **Lovable, телефон — D**: LCP — H2 «Visit the best wineries…», H1 не кандидат; признаков в HTML и CSS нет (`@keyframes hero-reveal`
  стартует с `opacity: .35`, H1 виден) — вероятно, H2 просто больше H1 по площади.
- **Durable — PASS, но показательно**: H1 внутри `div.opacity-0.translate-y-8` и сам с `color: transparent` — кандидатом LCP не
  становится ни на одном устройстве (на телефоне первый кандидат — абзац), однако итоговый LCP — картинка, и метрику это не
  искажает. Появление главного сообщения по скрипту — вопрос подачи (creative), у генератора это умолчание.
- Capsule, телефон: H1 не кандидат, LCP — видео после абзаца; признаков нет, итоговый LCP — медиа → PASS.

## Ограничения

- axe с адресами узлов для Durable не снят (очередь браузера); в снятом axe со счётчиками (`axe/demo-durable-naturepure.json`,
  21:46) нарушений контраста нет — вывод SG-A11Y-01 от адресов узлов не зависит.
- Класс узла контраста (`axe_classify.py`, `page_gates.py` `axe_node_class`) — эвристика: призыв — по совпадению текста с
  кнопками анатомии, лид — «текст первого экрана вне шапки, не ссылка» (ловит и надписи шаблона: Framer «Hero options:»),
  баннер — по классу или id с cookie/consent вне подвала; ключевой провал подтверждать кадром.
- `cmp_reject_equal` у M ненадёжен (эвристика вида кнопок) — LEGAL-02 подтверждать кадром `cmp_<device>.jpg`.
- Лабораторный INP (сценарий после загрузки) — нижняя граница: SG-PERF-04 прошёл на всех 6 страницах с данными, а TBT
  (SG-PERF-05, прокси INP) — S у 5 из 8.
- Сеть без троттлинга: LCP телефона — диагностика; вес мерился тем же прогоном (решение creative A2: вес — отдельным прогоном без
  замедления, исходы — с замедлением — здесь не разделено).
- 8 страниц, один прогон на устройство; 22 строки ворот из 62 не считались (нужен `page_accept.py`, человек, код, поле).
- Правка строк по этим же 8 страницам — подгонка под выборку: новые ложные B возможны на других страницах (живая фаза).

## Вывод

1. Ворота v1.1 давали **28 % ложных или завышенных B** (9 из 32): пороги были верны, ошибались способы замера — сумма сдвигов
   вместо окна CLS, `innerText` вместо сырого HTML, `scrollWidth` вместо расширения области, загрузка библиотеки вместо отправки
   события, контраст любого узла вместо ключевого. v1.2 убирает все 9 без потери верных B (23 из 23 остались).
2. **Контраст — главный источник шума**: color-contrast нарушен у 5 из 8 страниц (I/02 — у 9 из 10), у двух из пяти все узлы
   неключевые. Для B нужен axe с адресами узлов; счётчики дают S, которое исключение не снимает.
3. **Все три демо генераторов не проходят ворота** (blocked): Durable — `robots.txt` закрывает сайт от всех ботов; Lovable —
   трекинг до выбора и неравный баннер для ЕС, CLS 0,46 при прокрутке; Framer — кнопки и ссылки без имени. Умолчания генераторов
   — предмет проверки, а не доверия (`09-ai-generation-evaluation/01-generators-and-ai-landing-markers.md` §5).
4. Строки права (LEGAL) дают больше всего верных B на живых страницах (14 из 23 строк прогона 3) — рынок не образец.

## Файлы

`run_gates.py`, `fetch_html.py`, `run_axe_targets.py`, `axe_classify.py` — скрипты; `out/`, `result.tsv`, `matrix.md`, `b_list.tsv`
— прогон 3; `run1-v1.1/`, `run2-v1.2/` — прогоны 1–2; `axe_classes.tsv` — классы узлов (7 страниц); `pages/`, `geo/`, `axe/`,
`axe-targets/`, `demos/` — входы; `events.before-K.yaml` — резерв `07-…/events.yaml` до правки K (снято «не проверено» с
`utm_source=chatgpt.com`).
