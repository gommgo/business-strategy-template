# Бриф сайта: поля, владельцы, минимум по типу, вопросы заказчику и проекция в kimi

Волна 1 · агент A · 2026-09-24 · прочитано целиком 16 источников (контракт, kimi, ux, text, creative, словарь B) · опыты
`99-raw/experiments/A/01-schema-validate/` (схема и 16 отрицательных случаев), `A/02-kimi-projection/` (сборка пакета kimi),
`A/03-coverage/` (покрытие полей). Файлы формата: `site-brief.schema.json` (JSON Schema 2020-12, v0),
`site-brief.example.yaml` (лидогенерация услуг в РФ, вымышленная студия «Отвес»), `site-brief.kimi-map.tsv` (189 строк).

## Выжимка для агента

1. **Бриф сайта — один YAML-файл по `site-brief.schema.json`**, надмножество `brief.yaml` kimi; в kimi уходит проекция по
   `site-brief.kimi-map.tsv`, а не сам бриф: `lint_brief` отвергает чужие ключи верхнего уровня. → §1, §7 `[проверено]`
2. **Поля смысла — блок `meaning` по схеме text** (`$ref: urn:app-design:text-research:meaning:1`), доказательства — только
   ссылка `proof.facts_ref` на `facts.yaml` text; свои определения аудитории, возражений и фактов не заводить. → §2.6, §2.7
   `[проверено]`
3. **Один источник на поле**: трафик — `/traffic`, оффер — `/offer`, действие — `/conversion/action`; `meaning` ссылается на
   них JSON Pointer. Источники трафика внутри `meaning` — ошибка схемы. → §2.4–§2.6 `[проверено: A/01 N3]`
4. **Тип — двумя полями**: `site_type` (словарь B: `landing-site`, `services-site`…) и `primary_page_type`; у `landing-site`
   тип посадочной страницы обязателен и из класса landing (`landing-lead-services`, `landing-saas`…). → §2.1 `[проверено: A/01 N15]`
5. **Целевое действие — одно macro-id словаря B** (`booking`, `lead-request`, `start-trial`…); micro (`view-pricing`,
   `watch-video`) целью брифа не бывает; второе действие для неготовых — `secondary_actions`, иным стилем. → §2.3
   `[проверено: A/01 N2, N16]`
6. **Осведомлённость живёт в `meaning.awareness`** (уровень по умолчанию и `by_source`); уровень страницы page-plan берёт по
   её главному источнику (`pages.list[].main_sources`). → §2.4 `[практика]`
7. **Ни одного числа, отзыва, логотипа, рейтинга, цены и человека не из `facts.yaml`**: нет факта — нет блока; нет
   обязательного факта — пробел `missing` с `blocking: true`, страница не публикуется. → §2.7, §6 `[проверено: A/01 N1, N12]`
8. **Минимум доказательств по типу** (`proof.required_kinds`, проверяет схема при `proposed`/`approved`): `company` у всех
   коммерческих (личный бренд — `person`); лидогенерация услуг — ещё `price` или `offer-terms`, география, канал заявки;
   SaaS и приложение — `demo`; товар — `property`, `price`, `demo`; мероприятие — `date`, `offer-terms`; курс — `price`,
   `person`; портфолио — `case` или `demo`. → §3 `[практика]`
9. **Стимул только со сроком**: `offer.incentive_ref` требует `deadline_ref` — факт с `valid.until`; таймер без реальной даты
   запрещён. → §2.5 `[проверено: A/01 N7, N13]`
10. **Пустое поле — решение, отданное модели.** У каждого поля пометка `x-fill`: `customer` — спросить, `claude` — вывести и
    показать в «Going with», `default` — умолчание решений заказчика, `derive` — вычисляется, `sister:*` — заполняет сестра. →
    §3 `[практика: kimi 07/01 §3, ux 13/04 §2]`
11. **Процедура: разбор → черновик (`draft`) → одно сообщение ≤ 7 вопросов → допущения (`assumed`) → `proposed` → ответы →
    `approved`** (подпись `project.approval`, ни одного открытого вопроса приоритета 1). → §4 `[проверено: A/01 N4]`
12. **Факты — свободным ответом, решения — выбором из 2–4 вариантов с умолчанием**; не спрашивать выводимое и вкус
    прилагательными. → §5 `[практика: kimi 07/01 §4.1]`
13. **Один журнал `questions[]` на весь бриф** с полем `block`; `meaning.open_questions` внутри брифа пуст, допущения
    `meaning` ссылаются на id из общего журнала. → §2.11 `[проверено: A/01 SB-Q02]`
14. **Право по умолчанию — `constraints.jurisdiction: [ru]`**, ЕС — второй профиль по запросу; `legal_category` стоит рядом
    (`general` — явное «ничего особого»). → §2.8 `[практика: решение заказчика п. 11]`
15. **Попап захвата, exit-intent, чат, прелоадер — `off` по умолчанию**; включение — только с `policies.rationale` (условия F,
    согласие заказчика). → §2.9 `[проверено: A/01 N9]`
16. **Аналитика по умолчанию — Яндекс Метрика**; в проекции kimi `build.out_of_scope` без «analytics». → §2.9, §7
    `[проверено]`
17. **Уровень амбиций — только id `L0`/`L1`/`L2`** (определения — creative); умолчание заказчика: лендинги L1, кампании L2;
    лидогенерация — L0 при горячем мобильном трафике ≥ 50 % и `decision_context.price_band` low или mid, иначе L1 (решение 20
    PLAN); отклонение от умолчания — с причиной в `ambition.note`. → §2.10 `[практика]`
18. **Ловушки YAML**: `off`, `on`, `yes`, `no` и даты — в кавычках, тексты с запятой, `#` и двоеточием — в кавычках. → §4
    `[проверено: A/01 N10, N11]`
19. **Проверяй бриф до показа заказчику**: `validate.py` (схема + связи с `facts.yaml` и `meaning`), затем проекция —
    `build_package.py questions`, `build`, `check` без ошибок. → §4, §7 `[проверено: A/01–A/03]`
20. **Доказательств нет — анкета text `proof-intake.md`** (минимум блоки 1, 4, 15), разрешения третьих лиц получает заказчик;
    до ответа страница держится на механизме, условиях договора и снятии риска, а не на выдуманной социальной проверке. → §6
    `[практика]`
21. **Визуальных решений в брифе нет**: палитра, шрифты, тезис, макроструктура — creative и Claude при сборке пакета; 30 из 48
    обязательных полей kimi — `claude_fills`. → §7 `[проверено]`
22. **Многостраничник — `pages.list` или `by-type` по карте G**; kimi получает пакет на шаблон страницы (своей модели сайта у
    kimi нет). → §2.10, §7 `[практика]`

## 1. Что такое бриф сайта и где он в конвейере

Бриф — вход процедуры «бриф → карта сайта → планы страниц → пакет исполнителя → приёмка» (`../PLAN.md`, «Как всё
сочетается»). Контракт тройки v2 §3 п.1 задаёт состав, §3 п.14 — правило «один источник правды»: `site-brief` — надмножество
`brief.yaml` kimi, в kimi уходит проекция [S1]. Три причины не писать бриф прямо в формате kimi:
- `brief.yaml` создан для сборки пакета K3: 21 раздел верхнего уровня, `lint_brief` отказывает на неизвестном ключе
  (`build_package.py` стр. 242–262) [S3];
- в нём нет мест для трафика, осведомлённости, оффера, доказательств как ворот, права, SEO, аналитики, карты страниц: из
  11 полей лендинга компилятора C/01 (`../kimi-research/03-prompting/03-prompt-anatomy-k3.md` §5) восемь переехали в
  `direction`, `references`, `build`, `content`, `decisions`, `run`, в блоке `site:` осталось три — `cta.label`,
  `cta.target`, `sections` [S4, S5]; уточнение к аудиту KIMI §2.8 п.1, где сказано «остались три» без оговорки о переезде;
- 30 из 48 обязательных полей kimi — визуальная система и сборка, их заполняют creative и Claude, а не заказчик (опыт A/03).

```
site-brief.yaml (site)                         brief.yaml kimi (проекция, J: site_brief_to_kimi.py)
├─ project, site_type, primary_page_type ──────► project.slug/type/date/status
├─ business, decision_context                  ► product.name, description (derive)
├─ conversion ─────────────────────────────────► product.primary_action, site.cta.target
├─ traffic ────────────────────────────────────► product.target_user, viewport_primary (derive)
├─ offer ──────────────► facts (цены, условия) ► facts[], missing[] (из facts.yaml text)
├─ meaning ($ref text) ────────────────────────► product.goal, target_user, tone_of_voice; site.sections (через иерархию)
├─ proof.facts_ref ─► facts.yaml (text) ───────► facts[], missing[], never_claim[]
├─ constraints, policies, analytics, search ───► decisions.extra, design_system.bans, build.stack (строки, не проверки)
├─ languages, pages ───────────────────────────► product.locale, product.screens
├─ ambition (creative) ────────────────────────► decisions.motion.level (соответствие creative)
├─ brand, references (creative) ───────────────► brand, references (Claude готовит файлы)
└─ questions ──────────────────────────────────► questions[] (только answered и assumed)
          + art-direction creative → design_system, direction; copy-deck text → copy, site.cta.label; page-plan → site.sections
```

## 2. Разделы брифа

Полная схема — `site-brief.schema.json` (25 блоков верхнего уровня, 14 условий `allOf`); пример — `site-brief.example.yaml`.
Пометки: **владелец** — кто определяет поле; **заполнение** — кто вписывает значение (`x-fill` в схеме).

### 2.1. Паспорт и тип

| Путь | Значения | Владелец · заполнение | Правило |
|---|---|---|---|
| `version`, `checked` | `0`; дата строкой | site · claude | `checked` → `project.date` kimi |
| `intake` | `received`, `channel`, `raw_ref`, `what_ordered` (landing, multipage, redesign, new-page, section, audit), `analysis_ref` | site · claude | исходный текст заказчика не копировать в бриф — ссылка |
| `project.slug`, `project.status` | kebab-case; `draft` → `proposed` → `approved` | site · claude | те же пути, что у kimi; `proposed` → `draft` в проекции |
| `project.approval` | `by` (роль), `date`, `channel` | site · customer | обязателен при `approved` |
| `site_type` | словарь B: `landing-site`, `services-site`, `corporate-site`, `saas-marketing-site`, `portfolio-site`, `event-site`, `personal-brand-site`, `school-site`, `campaign-site` | B · claude | магазин, веб-сервис, медиа, документация, площадка — вне рамок брифа сайта [S10] |
| `primary_page_type` | 33 `page_type` словаря B | B · claude | для `landing-site` обязателен и из 9 id класса landing |

### 2.2. Бизнес и контекст решения

| Путь | Значения | Владелец · заполнение | Правило |
|---|---|---|---|
| `business.name`, `what`, `kind` | строка; вид предложения (как `meaning.offering_summary.kind` + `personal-brand`) | site · customer | `what` — словами заказчика, без оценок |
| `business.goal.primary` | leads, sales, signups, bookings, registrations, awareness, hiring | site · claude | цель сайта для P (события, KPI) |
| `business.kpi[]` | метрика, цель, текущее, источник | site · customer | число — из CRM или Метрики, не «из головы» |
| `business.geography` | регионы, радиус, удалённо, `address_ref` (факт) | site · customer | обязательна для лидогенерации услуг |
| `decision_context` | market (b2c, b2b, b2g, b2b2c), price_band (относительно бюджета покупателя), purchase_type, decision_unit (один, пара и семья, группа, комитет), cycle, perceived_risk, risk_kinds, involvement | site A · claude | вход C и F: длина, доля доказательств, сила призыва (`01-how-visitors-decide.md` §6) |

### 2.3. Конверсия

`conversion.action` — одно macro-id словаря B (18: `lead-request`, `request-quote`, `callback-request`, `call`, `message`,
`booking`, `request-demo`, `sign-up`, `start-trial`, `purchase`, `preorder`, `join-waitlist`, `event-registration`,
`download`, `subscribe`, `install-app`, `apply-job`, `visit-location`) [S10]. `target` — куда ведёт главный призыв
(`anchor`, `route`, `url`, `tel`, `messenger`, `store`); `channels` — каналы приёма (форма, квиз, калькулятор, телефон,
обратный звонок, мессенджер, виджет записи; пространства `conversion_channel` в словаре B нет — предложение B; не путать с атрибутом `channel` у `traffic_source` — группой атрибуции P); `secondary_actions` —
вторая цель для неготовых («зашёл заранее — запомнил и вернулся», `[V:b2VdPF9svEU 33:37]` по дайджесту ux);
`response_time_ref` — срок ответа фактом; `qualification_note` — какие заявки не нужны (вход F). Текст кнопки — не бриф, а
слот copy-deck text.

### 2.4. Трафик и осведомлённость

`traffic.sources[]` — `source` (18 id словаря B), `temperature` (cold, warm, hot), `share` (0–1, сумма ≤ 1 — проверка
SB-T01), `device` (mobile, desktop, mixed), `promise_of_source` (текст объявления, запрос, тема письма — первый экран
продолжает это обещание), `entry_page`, `campaign`, `geo`. Осведомлённость — в `meaning.awareness` (text): `level` для
основного трафика и `by_source` по источникам; page-plan берёт уровень страницы по `pages.list[].main_sources`. Чем
осведомлённость и температура меняют страницу — `01-how-visitors-decide.md` §3; словами — `../../text/02-strategy-messaging/02-awareness-hierarchy-objections.md`.

### 2.5. Оффер

`offer` — что посетитель получает за действие: `kind` (бесплатная консультация, замер и смета, КП, пробный период,
бесплатный тариф, демо, покупка, предзаказ, запись, регистрация, материал за контакт, скидка, образец), `summary` (внутренняя
формулировка), `includes`, `price_refs` и `terms_refs` (`fact:`/`missing:`), `incentive_ref` и обязательный при нём
`deadline_ref` (факт с `valid.until`), `risk_reversal_refs` (id из `meaning.risk_reversal`). Слова оффера — copy-deck text;
механика — F.

### 2.6. Смысл

`meaning` — блок text B1 целиком (аудитория и задачи, осведомлённость, искушённость рынка, позиционирование, ценностное
предложение и силы выбора, возражения, снятие риска, границы обещаний, иерархия сообщений, голос) [S7]. Внутри брифа схема
добавляет четыре ограничения: `meaning.traffic` — только `ref: /traffic`; `meaning.offer.ref` = `/offer`;
`meaning.conversion.action_ref` = `/conversion/action`; `open_questions` пуст, `legal_category` не заполняется. Вместо
встроенного блока допустим `meaning_ref` — путь к отдельному `meaning.yaml` (не оба сразу). Валидатор сверяет
`meaning.site` = `project.slug`, `meaning.proof_ref` = `proof.facts_ref`, `meaning.languages` = `languages`.

### 2.7. Доказательства

`proof` — только поля связи (предложение text B2, `x-site-brief-proof`) [S8]: `facts_ref` — путь к `facts.yaml`;
`required_kinds` — виды фактов, без которых страница не публикуется (минимум по типу — §3); `wanted_kinds` — желательные по
возражениям; `collection` — владелец у заказчика, кто ведёт анкету, даты, статус; `intake_form` — версия анкеты. Пробелы не
копируются: они в `facts.yaml` `missing[]`, `blocking: true` — ворота публикации. Виды (`kind`) берутся ссылкой на
`facts.schema.yaml` (22 вида: metric, property, price, offer-terms, guarantee, testimonial, expert-quote, case, client,
partner, award, certificate, press, rating, person, demo, company, date, availability, promo, research, forecast).
Валидатор (SB-P01) считает вид закрытым, если есть публикуемый факт (проверен или со слов заказчика, разрешение есть или не
нужно, не выведен агентом, срок не истёк) или блокирующий пробел.

### 2.8. Ограничения и право

`constraints.jurisdiction` — массив id словаря B (`ru` по умолчанию, `eu` — профиль по запросу, `kz`, `by`, `us`, `other`
не покрыты правом базы); первый элемент — основной и совпадает с `facts.jurisdiction` (SB-F04). `legal_category` —
отраслевой режим формулировок (перечень text B1: finance, medical, dietary-supplements, alcohol, education, real-estate,
other, general). `cms`, `stack`, `hosting` (важно для локализации ПД в РФ — I), `integrations` (CRM, телефония, запись,
оплата), `deadline`, `budget`, `accessibility` (`wcag22-aa` по умолчанию). Требования закона к форме, cookie, реквизитам и
отзывам — I (`../08-legal-trust-a11y/`, волна 2); бриф только выбирает профиль.

### 2.9. Политики, аналитика, поиск

| Путь | По умолчанию | Откуда умолчание | Кто решает иначе |
|---|---|---|---|
| `policies.capture_popup`, `exit_intent` | `off` | решение заказчика п. 15; ux 06/04 §8.1 п.17–18 | заказчик по условиям F (`rationale` обязателен) |
| `policies.chat_widget` | `off` | вес и доступность стороннего виджета (P, I) | заказчик |
| `policies.preloader` | `off` | решение п. 15: только L2-кампании по явному решению | заказчик; вне L2 — ошибка валидатора SB-D02 |
| `policies.cookie_banner` | `auto` | по юрисдикции и составу скриптов (I) | — |
| `analytics.system` | `yandex-metrica` | решение п. 15 | заказчик (GA4 — условия I о трансграничной передаче) |
| `search.engines`, `ai_answers` | Яндекс, Google; Алиса, ИИ Google, ChatGPT Search, Perplexity | решение п. 15 | заказчик |
| `search.ai_bots_policy` | `ask` | решение бизнеса: видимость в ответах против обучения моделей | заказчик; варианты и боты — H (`crawlers.yaml`) |
| `search.regions`, `existing_site`, `profiles`, `queries_known` | — | вход H и G (редиректы, `sameAs`, LocalBusiness) | заказчик |

### 2.10. Языки, страницы, амбиции, бренд, референсы, материалы

- `languages[]` — ровно один `primary`; второй язык — `adaptation` (адаптация под свою аудиторию, не перевод — решение
  заказчика); структура языковых версий — G.
- `pages` — `mode: by-type` (карта по умолчанию для типа — G, плейбук — J) или `listed` со списком `{id, page_type, purpose,
  priority, main_sources, action}`; `exclude` — чего заказчик не хочет. У лендинга в списке — главная и служебные
  («спасибо», политика ПД, согласие отдельным документом — I).
- `ambition.level` — `L0`/`L1`/`L2`, `by_page`, `note`. Определения, бюджеты и соответствие уровням движения kimi — creative
  (`../../creative/PLAN.md`, таблица уровней, гипотеза: L0 ≈ `subtle`, L1 ≈ `expressive`, L2 ≈ `cinematic`).
- `brand` — структура `brand` kimi (`templates/brand.json`: цвета ролями, шрифты с кириллицей, логотип, голос, `status`);
  выражение бренда — creative; очистку ролей и шрифтов делает Claude (`../../kimi-research/07-brief-handoff/03-references-brand-assets.md` §4).
- `references[]` — `ref:<id>` библиотеки creative или `url`, роль, Take / Do not take; файлы-скриншоты и замеры для kimi
  готовит Claude (≤ 262 144 байт, ≤ 2000 px — `build_package.py`).
- `assets_available` — какие настоящие материалы есть: фото (нет, мало, библиотека) и их сюжеты, видео, скриншоты продукта,
  логотип в векторе. Вход плана ассетов ai-media и правила «реальные фото сильнее стока» (`01-how-visitors-decide.md` §5).

### 2.11. Журнал вопросов

`questions[]` — один журнал на весь бриф (ответ на вопрос 4 text B1): `id`, `block` (раздел брифа), `q`, `why`, `options`
(для решений; для фактов пусто), `default` (строка «Going with»), `affects` (JSON Pointer полей), `priority` (1 — без ответа
страницу честно не построить), `asked`, `answer`, `source`, `date`, `status` (`open`, `assumed`, `answered`, `withdrawn`).
Допущение — это вопрос в статусе `assumed`: работа идёт по умолчанию, а заказчик видит строку в «Going with». В проекцию kimi
уходят только `answered` и `assumed` (опыт A/02: открытые вопросы сборщик теряет — 3 GAP в первом прогоне).

## 3. Пустое поле — решение, отданное модели: минимум по типу

Шапка шаблона kimi: «ПУСТОЕ ПОЛЕ = РЕШЕНИЕ, ОТДАННОЕ МОДЕЛИ» (`templates/brief.yaml` стр. 5, правило ui 12/04) [S2]. У K3
предсказуемый почерк на пустых полях (тёплая бумага, выделенное слово, антиква — kimi 07/01 выжимка п.2), у агента,
пишущего страницу, — «медианный лендинг» и выдуманные доказательства. Поэтому в `draft` схема требует только паспорт, тип,
бизнес, действие, ограничения, языки и журнал, а с `proposed` — все разделы контракта и минимум доказательств по типу.

**Минимум по типу** (проверяет схема; `required_kinds` брифа может быть шире):

| `site_type` · `primary_page_type` | `proof.required_kinds` (минимум) | Другие обязательные поля | Действие по умолчанию | Амбиции по умолчанию |
|---|---|---|---|---|
| `landing-site` · `landing-lead-services`; `services-site`; страница `service-page`, `seo-landing-page` | `company` + `price` или `offer-terms` | `business.geography`; `conversion.channels` ∋ форма, квиз, калькулятор, телефон, звонок, мессенджер или запись | `lead-request`, `request-quote`, `callback-request`, `booking` | L1 (решение заказчика); L0 — гипотеза creative для горячего мобильного трафика |
| `landing-site` · `landing-saas`, `landing-app`; `saas-marketing-site` | `company` + `demo` | — | `start-trial`, `sign-up`, `request-demo`, `install-app` | L1 |
| `landing-site` · `landing-product` | `company` + `property` + `price` + `demo` | — | `purchase`, `preorder` | L1 |
| `landing-site` · `landing-campaign`; `campaign-site` | `company` | при стимуле — `offer.deadline_ref` | по кампании | L2 |
| `landing-site` · `landing-event`; `event-site` | `company` + `date` + `offer-terms` | — | `event-registration`, `purchase` | L1 (крупное событие — L2) |
| `landing-site` · `landing-course`; `school-site` | `company` + `price` + `person` | `legal_category` ∋ `education`, если выдаётся документ об обучении (I) | `purchase`, `lead-request`, `sign-up` | L1 |
| `landing-site` · `landing-waitlist` | `company` | — | `join-waitlist`, `preorder` | L1 |
| `landing-site` · `landing-lead-magnet` | `company` | `offer.kind: lead-magnet`; действие `download`, `subscribe` или `lead-request` | `download` | L1 |
| `corporate-site` | `company` | `pages` (карта по умолчанию — G) | `lead-request` | L1 |
| `portfolio-site` | `company` + `case` или `demo` | — | `lead-request` | L2 |
| `personal-brand-site` | `person` | — | `lead-request`, `booking` | L1 |

Происхождение строк: `company` — сведения о продавце и «кто вы такие» как первое возражение (`01-how-visitors-decide.md`
§5; право — I); `demo` для SaaS и приложения — настоящий интерфейс вместо иллюстрации; `property` + `price` для товара —
«продаёте — показывайте цену» (`[V:vxGrL3YSBvw 13:48]` по аудиту UX §2.4); `date` для события; `person` для курса и
личного бренда — кто учит или кто отвечает. Метка всей таблицы — `[практика]`: синтез A по механизму; F (механика
доказательств) и J (плейбуки) уточняют в волнах 2–3.

**Кто заполняет** (`x-fill` в схеме):

| Пометка | Поля | Что делает Claude |
|---|---|---|
| `customer` | `business.*`, `traffic.sources`, `offer`, `proof` (через анкету), `constraints`, `search`, `languages`, `brand`, `assets_available` | спрашивает; факты — свободным ответом |
| `claude` | `intake`, `project`, `site_type`, `primary_page_type`, `decision_context`, `conversion`, `pages`, `questions` | выводит сам, показывает в «Going with» |
| `default` | `policies`, `analytics`, `ambition.level`, `constraints.jurisdiction` | ставит умолчание решений заказчика, меняет только по его слову |
| `derive` | проекция в kimi, `viewport_primary`, доли и связи | вычисляет |
| `sister:text` | `meaning`, `facts.yaml` (формат и анкета) | ведёт процедуру text (`02-strategy-messaging/01` §5, `proof-intake.md`) |
| `sister:creative` | `ambition` (определения), `references`, выражение `brand` | берёт у creative; до C1 — только id уровня |

## 4. Процедура заполнения

Образец — шаг 1 ux 13/04 («разбор брифа»: четыре списка и допущения, помеченные словом «допущение») [S6] и процедура kimi
07/01 §2 [S4]; для сайта добавлены трафик, доказательства как ворота и право.

| Шаг | Что сделать | Артефакт | Проверка на выходе |
|---|---|---|---|
| 1 | Разложить сообщение заказчика на четыре списка: что заказано, факты (с цитатой), ограничения, пробелы | запись «Бриф: разбор» (`intake.analysis_ref`) | каждое допущение помечено «допущение»; ни одного числа «из головы» |
| 2 | Определить `site_type` и `primary_page_type` по признакам (словарь B, `02-site-types/01`) | строка «тип = …, страница = …, плейбук = …» | тип из словаря; у `landing-site` есть тип страницы |
| 3 | Заполнить `business`, `decision_context`, `conversion`, `traffic`, `offer` из сообщения; остальное — черновые умолчания | `site-brief.yaml`, `status: draft` | `validate.py` — 0 ошибок схемы |
| 4 | Запустить анкету доказательств text по `required_kinds` и `wanted_kinds` | `facts.yaml` (text), `proof.collection` | SB-P01: у обязательных видов — факт или блокирующий пробел |
| 5 | Собрать `meaning` по процедуре text (позиционирование, возражения) | блок `meaning` или `meaning_ref` | схема text; допущения ссылаются на вопросы журнала |
| 6 | Свести вопросы: не больше 10 в пуле, ≤ 7 в одном сообщении, у каждого «зачем» и умолчание | `questions[]`, сообщение заказчику + «Going with» | вопросы приоритета 1 — первыми; факты без вариантов |
| 7 | Показать заказчику | `status: proposed` | `validate.py` — 0 ошибок схемы и смысла |
| 8 | Внести ответы; неотвеченное — `assumed` с умолчанием | `questions[].answer`, `status` | нет `open` приоритета 1 |
| 9 | Утвердить | `status: approved`, `project.approval` | схема (N4); `facts.yaml` `status: confirmed` — отдельно у text |
| 10 | Проекция в kimi (J) | `brief.yaml` kimi | `build_package.py questions` — 0 пустых, `build` — 0 GAP, `check` — 0 ошибок |

Ловушки YAML (опыт A/01, N10–N11): значения `off`, `on`, `yes`, `no` без кавычек YAML 1.1 читает как логические, дату
без кавычек — как объект даты; схема их отвергает, но надёжнее писать `"off"` и `"2026-09-24"`. Тексты с запятой внутри
`{…}`, с `#` и двоеточием — в кавычках (kimi 07/01 §5.3).

## 5. Вопросы заказчику по разделам

Правила сообщения — kimi 07/01 §4.1 [S4]: один блок, не больше 7 вопросов (пул — до 10), у каждого «зачем» и умолчание;
факты — свободным ответом («never a fabricated multiple-choice», scroll-world по kimi); не спрашивать выводимое и вкус
прилагательными; не задавать «аудитория, задача, тон» всегда (абляция Hallmark по kimi D: 12 из 40 запусков остановились на
вопросе). Банк вопросов (формулировки — заготовки; слова для заказчика — text):

| Раздел | Вопрос | Форма | Умолчание («Going with») |
|---|---|---|---|
| `business` | Что продаёте и кому; какие заказы не берёте? | свободно | из сообщения; «кому не подойдёт» не пишем |
| `business.kpi` | Сколько заявок (продаж) сейчас, сколько доходит до сделки? | свободно, из CRM | меряем с нуля: цели Метрики |
| `business.geography` | Где работаете: город, выезд, доставка? | свободно | зону обслуживания не пишем |
| `conversion` | Что посетитель должен сделать и что будет сразу после (кто и когда свяжется)? | выбор 2–3 + срок | заявка с перезвоном в рабочее время; срок не обещаем |
| `conversion.channels` | Какие каналы принимаете: форма, телефон, мессенджер, запись на время? | выбор | форма + телефон |
| `traffic` | Откуда придут люди: реклама (какая), карты, рекомендации, поиск, рассылка? Примерные доли | выбор + доли | по сообщению; доли — допущение до месяца Метрики |
| `traffic.promise_of_source` | Какой текст у объявлений или пришлём черновик? | выбор | черновик объявления вместе с первым экраном |
| `offer` | Что человек получает за заявку: консультацию, расчёт, замер, пробный период? Есть ли акция и до какой даты? | свободно | обмен без стимула; акции нет |
| `proof` | Анкета text `proof-intake.md`: реквизиты, цены и условия, чего нельзя утверждать (блоки 1, 4, 15) + по возражениям | свободно, документы | блокирующие пробелы — страница не публикуется |
| `constraints` | Где будет сайт и куда уходят заявки (CRM, почта)? Есть ли CMS? Срок и бюджет? | выбор + свободно | хостинг в РФ, заявки на почту; статическая вёрстка |
| `constraints.legal_category` | Отрасль с особыми правилами (медицина, финансы, образование с документом, БАДы, алкоголь, недвижимость)? | выбор | `general` |
| `brand` | Есть ли логотип, цвета, шрифты? Иначе — выбрать одно из 2–3 направлений creative | выбор | первое направление creative; словесный знак |
| `assets_available` | Есть ли настоящие фото работ, команды, офиса, видео, скриншоты продукта? С разрешениями? | выбор + файлы | без людей; работы — после разрешения |
| `search` | Есть ли старый сайт (адреса, трафик)? Профили на картах и в соцсетях? Пускать ли ИИ-ботов для ответов и обучения? | выбор + ссылки | новый домен; ИИ-ответы — да; обучение — по умолчанию H |
| `languages` | Нужна ли вторая языковая версия и для какой аудитории? | выбор | только русский |
| `ambition` | Какой нужен эффект: спокойно и быстро, выразительно, «вау»-кампания? | выбор 3 | умолчание по типу (§3) |

## 6. Если доказательств нет

Правило одно: **нет факта — нет утверждения**. Выдуманные «10 000+ клиентов», «Нам доверяют» и отзывы — главный риск
генерации (`../PLAN.md`, риск 4). Что делать по шагам:
1. Анкета text `proof-intake.md` [S9] по `required_kinds` и `wanted_kinds`: минимум блоки 1 (компания), 4 (цены и условия),
   15 (чего нельзя утверждать); остальное — по возражениям из `meaning.objections`. Ответ — строка `facts[]` с дословной
   выдержкой или `missing[]` (кто даст, срок, `blocking`).
2. Разрешения третьих лиц (авторы отзывов, клиенты с логотипами, сотрудники на фото) получает заказчик; до ответа факт в
   статусе `pending` не публикуется (фильтр text B2; опыт A/02: отзыв без разрешения ушёл в `missing[]`).
3. Обязательный вид без факта → пробел `blocking: true` → страница не публикуется; бриф можно утвердить, публикацию — нет
   (ворота страницы — P и K).
4. Желательный вид без факта → блок не строится: секция отзывов, логотипов или цифр без фактов не ставится «на вырост».
5. Чем держится честная страница без социальных доказательств (вопросы-заготовки для F — механика, I — право):
   - механизм и процесс: как устроена работа, кто отвечает, что проверяет клиент (свойство — факт `property`);
   - условия договора и оферты: сроки, этапы оплаты, гарантия с пунктом документа (`offer-terms`, `guarantee`);
   - снятие риска: бесплатный первый шаг, пробный период, оплата после (`meaning.risk_reversal` с `fact_id`);
   - реальные люди и места с согласием: основатель, мастер, офис, производство (`person`, `demo`, согласие на изображение —
     I); ИИ-люди в роли клиентов и команды запрещены (`nc-ai-people` text, решение заказчика п. 15);
   - проверяемые сведения третьих сторон: карточка на картах с рейтингом и числом отзывов на дату, реестры, сертификаты
     (`rating`, `certificate` — с датой снимка и ссылкой).
6. Новый бизнес без истории: не имитировать масштаб; показывать первое предложение честно (предзаказ, пилот, «первые
   клиенты — на особых условиях» только с фактом условий).

## 7. Совместимость с kimi

Результаты опытов:
- **A/02** — проекция примера проходит `build_package.py questions` (0 пустых обязательных, 0 ошибок формы), `build`
  (0 полей без маршрута, 0 потерь; `fields_filled=246`) и `check` (0 ошибок; предупреждения: нет своего `.git`, TASK.md
  8 024 знака > 4 000 для `/goal`). Дошло 234 из 457 листьев брифа (51 %); осознанно не идут в kimi 219 — прежде всего
  смысл (159 из 221: K3 тексты не пишет, смысл воплощён в copy-deck) [проверено].
- **A/03** — таблица покрывает 48 из 48 обязательных путей kimi, 19 из 19 полей контракта, 122 из 122 свойств схемы и 21 из
  21 раздела `brief.yaml`; 30 из 48 обязательных путей — `claude_fills` [проверено].
- Прогон 1 A/02 потерял открытые вопросы (3 GAP): сборщик переносит в TASK только вопросы с ответом → правило проекции
  «только `answered` и `assumed`».

**Что теряется и что предложить kimi** (файлы kimi не правим; предложения — в отчёте A, раздел 6):

| Что есть в брифе сайта | Что у kimi | Предложение |
|---|---|---|
| Политика первого экрана (поле page-plan `first_screen_policy`, словарь B: `offer-cta`, `offer-cta-header`, `poster`; условия — C) | A3 «обещание и CTA в первом экране» для любого landing | A3 из `first_screen_policy` страницы (строка 23 таблицы поправок `../PLAN.md`) |
| Ворота публикации по фактам (`required_kinds`, `missing.blocking`) | `missing[]` без `blocking`; блока приёмки нет | поле `blocking` и пункт ACCEPTANCE «доказательства» |
| Проверенные счётчики и рейтинги в `facts[]` | `facts.md` стр. 26–29 запрещает «counts, ratings, "trusted by", awards, press» без оговорки | `{{=NEVER_ROWS}}` из `facts.yaml` вместо четырёх строк (как предложил text B2) |
| Право, SEO, аналитика, формы | только строки `decisions.extra`; `out_of_scope` по умолчанию «backend, analytics, tests»; H7 (формы) только для webapp | блоки ACCEPTANCE «право», «SEO и мета», «события», «формы» (H7 для landing с формой); `out_of_scope` без analytics |
| Многостраничник (`pages.list`) | одна страница на пакет (`build.routes` — только webapp) | пакет на шаблон страницы или `routes` для landing |
| Уровень амбиций (подача целиком) | `decisions.motion.level` (только движение) | поле уровня амбиций или ссылка на `ambition-levels.yaml` creative |
| Раздел-ссылка на бриф сайта | неизвестный ключ — отказ сборки | пропускать `x_site` / `x-*` (контракт v2 §3 п.14) |
| Журнал вопросов с «зачем» и умолчанием | `questions[]` из 5 ключей | ключи `default`, `status` |

## 8. Для сестёр (S0)

Путь схемы — `01-foundations/site-brief.schema.json` (`$id urn:app-design:site-research:site-brief:0`), пример —
`site-brief.example.yaml`. Поля, ждущие определений сестёр (в v0 есть тип и пометка владельца):
- **text**: весь блок `meaning` (через `$ref` на их схему — определения их); `proof.facts_ref` и виды фактов (ссылка на
  `facts.schema.yaml`); `constraints.legal_category` (их перечень); `meaning.voice_ref` и `brand.voice` — профиль голоса
  (волна 2 text); `traffic.sources[].promise_of_source` — как писать продолжение обещания; банк вопросов §5 — слова.
- **creative**: `ambition.level` и `by_page` (определения, бюджеты, соответствие уровням движения kimi); `references[]`
  (формат записи библиотеки и пространство `ref:`); `brand` (выражение бренда); направления для вопроса о бренде.
Ответы на пять вопросов text B1 зафиксированы в схеме: 1) `traffic.sources[]` с `source`, `temperature`, `share`, `device`,
`promise_of_source` (+ `entry_page`, `campaign`, `geo`) — у site; 2) `offer` и `conversion.action` — у site, `meaning`
ссылается `/offer` и `/conversion/action`; 3) осведомлённость — `meaning.awareness` (по умолчанию и `by_source`), уровень
страницы — page-plan по главному источнику страницы; 4) один журнал `questions[]` в брифе с полем `block`,
`meaning.open_questions` внутри брифа пуст; 5) `constraints.legal_category` рядом с `jurisdiction`, в `meaning` не
заполняется.

## Частые ошибки

1. **Бриф свободным текстом** — поля теряются незаметно (компилятор C/01 kimi потерял 13 из 71 поля), пустые уходят модели;
   бриф — только YAML по схеме, проверка — `validate.py`.
2. **Свои определения аудитории, возражений, фактов в брифе** вместо `$ref` на схемы text — два источника правды.
3. **Трафик, оффер и действие дважды** (в `meaning` и в брифе) — расходятся после первой правки; схема это запрещает.
4. **Доказательства «для полноты»**: «10 000+ клиентов», чужие логотипы, «Нам доверяют», отзыв с идеальным аватаром —
   ядро ИИ-лендинга (`../../ux/11-ai-generated-ui/01-failure-modes-catalog.md` F12.1); без факта блока нет.
5. **Свои ключи в `brief.yaml` kimi** (`traffic`, `x_site`) — сборщик отказывает (`lint_brief`); в kimi — только проекция.
6. **`approved` при открытых вопросах приоритета 1** или без подписи — схема отвергает.
7. **Micro-действие как цель** («посмотреть тарифы»), две главные цели на странице, действие вне словаря B.
8. **Акция без даты окончания, таймер со сбросом** — `deadline_ref` без `valid.until` отвергается.
9. **Двадцать вопросов заказчику** или вопросы о вкусе («современно или классически?»); выдуманные варианты вместо
   свободного ответа о фактах.
10. **`capture_popup: off` без кавычек** — YAML превращает в `false`; даты без кавычек — в объект даты.
11. **Уровень амбиций = уровень движения**: L1 — это не только анимация (эффекты, медиа, 3D, бюджет); L2 для лидогенерации —
    только с причиной.
12. **Два журнала вопросов** (`meaning.open_questions` и `questions[]`) — дубли и потерянные ответы.
13. **«Средняя конверсия отрасли» как KPI сайта** — бенчмарк вендора не норма (`02-cro-evidence-and-folklore.md` §4).

## Чек-лист

- Бриф — YAML по `site-brief.schema.json`, `validate.py` — 0 ошибок схемы и смысла?
- `site_type` и `primary_page_type` из словаря B; у `landing-site` тип посадочной страницы класса landing?
- `conversion.action` — одно macro-id; вторая цель — в `secondary_actions`?
- У каждого источника трафика есть температура, устройство и обещание источника (если это реклама или письмо)?
- `offer` описывает обмен, а цены и условия — ссылками `fact:` / `missing:`?
- `proof.facts_ref` ведёт на `facts.yaml`, обязательные виды закрыты фактом или блокирующим пробелом?
- Стимул — только с фактом срока?
- Смысл — блоком `meaning` по схеме text или `meaning_ref`, без дублей трафика и оффера?
- Юрисдикция и отраслевой режим заданы; спорные приёмы выключены или включены с `rationale`?
- Один журнал вопросов; в сообщении заказчику ≤ 7 вопросов, у каждого «зачем» и умолчание; факты — свободным ответом?
- Все допущения — вопросы в статусе `assumed` и строки «Going with»?
- `approved` — с подписью и без открытых вопросов приоритета 1?
- Проекция в kimi проходит `questions`, `build`, `check` без ошибок?

## Открытые вопросы и противоречия

1. **Уровень амбиций лидогенерации**: решение заказчика п. 15 — «лендинги L1»; план creative (гипотеза) относит
   лидогенерацию услуг, тарифы и горячий мобильный трафик к L0. **Закрыто решением 20 PLAN** (≈ 15:25): L0 при горячем
   мобильном трафике ≥ 50 % и `price_band` low или mid, иначе L1; проверка — A/B «L0 против L1» (живая фаза). `[практика]`
2. **Действие «замер»**: text B1 — свободный id `request-measurement`, словарь B — `booking` («запись на время: …замер»),
   ближе по смыслу и `request-quote` («запрос расчёта»). Пример брифа — `booking`; строка соответствия — B (`crosswalk.tsv`).
3. **Пространства `conversion_channel` в словаре B нет** — в схеме временный перечень (предложение B); у B `channel` — атрибут источника трафика для атрибуции, отсюда новое имя.
4. **`facts.schema.yaml` text: `jurisdiction` — ru, eu, us, other**, словарь B — ещё `kz`, `by`: бриф с `kz` не сверится с
   фактами (предложение text).
5. **`meaning.languages` обязателен у text** и дублирует `languages` брифа; пока валидатор сверяет наборы (SB-M04),
   предложение text — ссылка на `/languages` внутри брифа. То же с `meaning.legal_category` (внутри брифа — запрещён).
6. **Минимум по типу — `[практика]`** (синтез A): F (механика доказательств) и J (плейбуки) проверяют на волнах 2–3; спорные
   строки — `person` для онлайн-школ без названных преподавателей, `demo` для SaaS до выпуска продукта.
7. **`decision_context` — качественные шкалы** без порогов; правила по ним — `01-how-visitors-decide.md` §6, их проверка —
   живая фаза.
8. **Многостраничник**: какие поля брифа задаются на страницу (оффер, трафик, амбиции) — G и J; у kimi модели сайта нет.
9. Указатели `questions[].affects` схемой не проверяются (JSON Pointer как строка) — `site_validate.py` J.

## Источники

- [S1] Оркестратор фундамента site. Контракт тройки site · creative · text, v2.1 — `99-raw/notes/triad-contract-2026-09-24.md`,
  2026-09-24. Внутренний договор баз: состав брифа (§3 п.1), факты (§3 п.10), бриф как надмножество kimi (§3 п.14).
- [S2] kimi-research, агент F. `07-brief-handoff/templates/brief.yaml`, 2026-09-24 04:10. Форма брифа K3; шапка «пустое поле =
  решение модели»; проверено сборщиком на двух примерах kimi.
- [S3] kimi-research, агент F. `07-brief-handoff/templates/build_package.py`, 2026-09-24 04:40 (стр. 157–262 — обязательные
  поля и `lint_brief`; 704–735 — маршруты; 789–1043 — проверки). Исполняемый источник; прогнан в опытах A/02–A/03.
- [S4] kimi-research, агент F. `07-brief-handoff/01-from-app-description-to-brief.md`, 2026-09-24, §2–§5. Процедура «описание →
  бриф», вопросы Q1–Q8, правила сообщения заказчику; опора — опыт kimi F/03.
- [S5] kimi-research, агент C. `03-prompting/03-prompt-anatomy-k3.md` §5, 2026-09-24. 11 полей лендинга блока `site:`.
- [S6] ux-research. `13-app-types/04-master-procedure-brief-to-screens.md` §2, §5. Шаблон «Бриф: разбор», правило допущений.
- [S7] text-research, агент B1. `02-strategy-messaging/meaning.schema.yaml`, `$id urn:app-design:text-research:meaning:1`,
  date 2026-09-24 (764 строки). Схема блока «смысл»; `x-kimi-map`, `x-site-brief-meaning`.
- [S8] text-research, агент B2. `02-strategy-messaging/facts.schema.yaml`, v1 волны 1 (841 строка). Формат `facts.yaml`,
  фильтр публикации, `x-site-brief-proof`, умолчания `never_claim`.
- [S9] text-research, агент B2. `02-strategy-messaging/proof-intake.md`, 2026-09-24. Анкета доказательств и разрешений.
- [S10] site-research, агент B. `02-site-types/vocabulary.yaml` v0 draft, revision 1, 2026-09-24 11:48; заметки B «Для A»
  (11:45). Словарь `site_type`, `page_type`, `action`, `traffic_source`, `jurisdiction`; черновик — сверить с v0 на S0.
- [S11] site-research. `PLAN.md`, «Решения заказчика» п. 10–15, 16–18; таблица «Поправки к правилам соседей», строки 23–26.
- [S12] Аудит `kimi-research` через линзу лендинга — `99-raw/notes/audit-2026-09-24/KIMI-report.md` §2.3, §2.7, §2.8, §4
  п.1, 4, 12, 13. Вторичный разбор со ссылками на строки.
- [S13] kimi-research, агент F. `07-brief-handoff/templates/facts.md`, 2026-09-24, стр. 25–29 («Never claim»).
- [S14] creative-research. `PLAN.md`, таблица уровней амбиций L0–L2 (стр. 236–256) — `[гипотеза]` архитектора creative до
  его волн; соответствие уровням движения kimi.
- [S15] text-research, B1 и B2. `../../text/02-strategy-messaging/examples/meaning-otves.yaml`, `../../text/02-strategy-messaging/examples/facts-service-renovation.yaml`,
  `../../text/02-strategy-messaging/examples/hierarchy-otves-product-aware.yaml` — вымышленная студия «Отвес»; основа примера брифа.
- [S16] ux-research. Дайджест `91-videos/digests/b2VdPF9svEU.md` [33:37] (Бирман, 2025): двойная цель страницы.
