# Карта знаний: маркетинг — site, text, creative (черновик разделов 3–6)

Черновик группы «маркетинг» для `kb/INDEX.md`. Разделы 3–6 — в окончательной форме текста скилла; «Заметки сборщику» —
только для журнала. Адреса — от `kb/`; короткий адрес «site 07/03 §4» — база, папка, файл, раздел.

## 3. Базы

Страницу проектируют три базы: site — логика, text — слова, creative — подача; кто ведёт часть общей темы —
`common/owners.md` (он старше текстов баз). README баз — 30–38 тыс. токенов: открывают названный раздел.

### site — логика сайта и лендинга

**Вопрос:** какие страницы и секции нужны, как страница ведёт к действию и как её принять. **Владеет:** брифом, типами
и картой сайта, планом страницы, блоками, словарём id, конверсией, техникой SEO и GEO, бюджетом, воротами и правом.
Глубже всего проработаны лидогенерация услуг, SaaS или продукт, кампания L2, корпоративный сайт
(`site/README.md §Решения заказчика и открытые вопросы`).

| вход | открывать, когда |
|---|---|
| `site/README.md` — §Как пользоваться, §Реестр разрешённых противоречий, §Свод поправок к соседям | нужен маршрут; два файла site спорят; норма ux или ui ложится на страницу иначе |
| `site/10-playbooks-contracts/01-procedure-brief-to-pages.md` | шаги от брифа (§1), пропуски по типу заказа (§1.2); плейбуки типов — site 10/02, site 10/03 |
| `site/01-foundations/03-site-brief.md` | бриф: поля (§2), минимум по типу (§3); тип сайта — site 02/01 §6 |
| `site/03-page-structure/01-narratives-and-section-order.md` | роли и порядок секций (§3), макроструктуры (§4) |
| `site/04-blocks/03-slots-and-page-plan.md` | план: слоты (§1), «бриф → план» (§5) |
| `site/05-conversion-funnels/01-cta-and-lead-capture.md` | призывы и формы; воронка — site 05/03 |
| `site/07-seo-geo-performance-analytics/03-performance-budgets-gates.md` | бюджет (§3), ворота (§4) |
| `site/09-ai-generation-evaluation/02-site-checklist.md` | приёмка; ≈ 57 тыс. — разделами (§2, §7) |

**Машинные файлы.** `site/02-site-types/vocabulary.yaml` — единые id (типы страниц, роли секций, блоки, слоты), чужие
словари — строками `site/02-site-types/crosswalk.tsv`; схемы v1 и образцы — `site/10-playbooks-contracts/` (старые схемы в
папках 01, 04, 06 — не для новых файлов); блоки — `site/04-blocks/blocks.yaml`; бюджеты и ворота — YAML папки 07.

**Утилиты** (`scripts/site/`): `site_validate.py` — бриф, карта, планы по схемам; `vocab_lint.py` — id вне словаря;
`plan_to_assets.py` — каркас плана ассетов; `page_gates.py` — профиль (`--resolve`) и ворота; `page_anatomy.py`,
`geo_probe.py` — замер собранной страницы.

### text — смысл, факты и тексты

**Вопрос:** что сказать на странице и как проверить сказанное. **Владеет:** смыслом и сообщениями, фактами и их сверкой,
copy deck и правилами слотов, голосом бренда, антислопом, содержанием SEO и GEO, правом формулировок и набором. Микрокопи
интерфейса — у ux.

| вход | открывать, когда |
|---|---|
| `text/README.md` — §Как пользоваться, §Поправки к соседям (свод) | маршрут с командами; правило text расходится с ux 07; два файла text спорят — `text/CONTRADICTIONS.md` |
| `text/09-ai-generation-evaluation/02-generation-pipeline.md` | цепочка S1–S11 (§1), точки человека (§5) |
| `text/02-strategy-messaging/03-proof-and-facts.md` | факты: сбор (§2), формат (§4), отзывы (§5) |
| `text/02-strategy-messaging/02-awareness-hierarchy-objections.md` | осведомлённость (§1), иерархия (§2), возражения (§4); позиционирование — text 02/01 |
| `text/04-copy-by-block/01-hero-and-cta.md` | первый экран и кнопка; секции — text 04/02, типы страниц — text 04/03 |
| `text/05-voice-editorial/01-brand-voice.md` | голос бренда и продукта (§2), вывод из брифа (§3) |
| `text/06-anti-slop/01-text-slop-markers-by-genre.md` | слоп по жанрам; линтер — text 06/02; право формулировок — text 08/01, набор — text 08/02 |
| `text/10-templates-recipes/01-copy-deck-workflow.md` | copy deck: статусы (§1), варианты (§4), ассеты (§8) |

**Машинные файлы.** Схемы фактов, смысла и иерархии — `text/02-strategy-messaging/`, голоса — папка 05, copy deck —
`text/10-templates-recipes/copy-deck.schema.json`; правила слотов — `text/04-copy-by-block/copy-slots.yaml`; правила
проверок — YAML папок 06–09. Id страниц, секций и слотов — словарь site: законный id, отвергнутый утилитой text, —
дефект утилиты (`common/CONTRADICTIONS.md §1`).

**Утилиты** (`scripts/text/`): `copydeck.py` — copy deck целиком (сверка → линтер → формат), статусы, варианты;
`claims_check.py` — текст или HTML против фактов и права; `copy_lint.py` — слоп и набор по жанру; `chain_inputs.py` —
смысл против фактов до текста.

### creative — подача

**Вопрос:** как страница выглядит и движется, чтобы продавать и не быть шаблоном. **Владеет:** уровнями амбиций и
бюджетом подачи, концепцией и направлениями, референсами, визуальным языком маркетинга (расширяет токены ui), движением и
эффектами, стеком, политикой клише, спецификацией подачи, воротами эффектов и рубрикой эффектности.

| вход | открывать, когда |
|---|---|
| `creative/README.md` — §Как пользоваться | маршрут «подача · проверка · правка»; два файла creative спорят — `creative/CONTRADICTIONS.md` |
| `creative/01-creative-direction/03-ambition-levels.md` | уровень: выбор (§5), разрешённое (§3), бюджеты (§4), секции (§6) |
| `creative/01-creative-direction/01-concept-and-directions.md` | концепция (§3), главный приём (§5), направления (§6); документ — creative 01/02 |
| `creative/02-references-moodboards/03-moodboard-and-handoff.md` | мудборд (§1), описание референса (§3), роли (§4) |
| `creative/04-visual-language/01-display-typography.md` | дисплей (§2), кириллица (§4); композиция — creative 04/02, цвет — creative 04/03 |
| `creative/05-motion/01-motion-principles-and-access.md` | ≈ 35 тыс. — разделами: WCAG (§3), reduce (§4), бюджет внимания (§5) |
| `creative/08-uniqueness-anti-slop/01-cliche-policy.md` | приём или клише (§1), нормы соседей на сайте (§4) |
| `creative/09-ai-execution-evaluation/01-presentation-spec-and-block-treatments.md` | `treatment` (§2), пакет исполнителя (§6); движение — creative 09/02 |
| `creative/09-ai-execution-evaluation/03-verification-loop-and-gates.md` | проверка (§1), ворота эффектов (§3), профиль `marketing` (§4) |

**Машинные файлы.** `creative/01-creative-direction/ambition-levels.yaml` — уровни: разрешённое, бюджеты подачи,
умолчания по типу, уровень движения; схемы подачи — `creative/09-ai-execution-evaluation/`; токены —
`creative/04-visual-language/marketing-tokens.json` (поверх схемы ui); эффекты — `creative/06-effects-catalog/effects.yaml`;
рецепты и примеры L0–L2 — `creative/10-recipes/`.

**Утилиты** (`scripts/creative/`): `spec_check.py` — `treatment` и `motion-spec` по схемам и уровню; `refs_client.py` —
клиент референсов; `marketing_audit.py` — визуальные проверки страницы поверх `ui_audit.py` с приметами клише;
`motion_check.py` — движение и цена по записи, ворота эффектов.

## 4. Межбазовые связи (предложения группы «маркетинг»)

Обмен внутри тройки и владелец каждой части формата — `common/owners.md §Форматы обмена`; здесь — что тройка передаёт
соседям. Копии в базах уступают канону.

| что передаётся | канон | пишет | читает |
|---|---|---|---|
| id страниц, секций, слотов, блоков | `site/02-site-types/vocabulary.yaml`; поля — `site/10-playbooks-contracts/schemas/page-plan.schema.json` (3D-слот называет рецепт `recipe:`) | site | copy deck, `treatment`, план ассетов, blender, вход холста |
| план ассетов | формат — ai-media 01/01 §8; медиа-слот — site 04/03 §1.4; тексты ассетов — text 10/01 §8 | site — слоты (`plan_to_assets.py`); text — alt, подписи, текст в кадре | ai-media; ассеты холста (cd 06/02 §3) |
| люди и доказательства — только реальные | `site/08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §2.1` | site | ai-media, холст |
| паспорт визуала из арт-дирекции | creative 01/02 §4.1 → ai-media 06/01 §2 | creative, ai-media | генерация ассетов |
| референсы — словами, не картинкой | creative 02/03 §5 | creative | ai-media, blender, холст |
| бриф 3D; 3D по секциям | creative 01/02 §4.2; site 04/01 §3.2 | creative, site | blender |
| уровень L0–L2 → бюджеты и ворота | `creative/01-creative-direction/ambition-levels.yaml`; `site/07-seo-geo-performance-analytics/budgets.yaml`; порядок ворот — site 07/03 §4 | creative, site | ворота эффектов, ассетов, 3D (blender 09/05 §7.2) |
| вход холста | cd 06/02 §1 (позиция): бриф — проекция `site/10-playbooks-contracts/schemas/site-brief.schema.json`, «Нельзя утверждать» — из `text/02-strategy-messaging/facts.schema.yaml`, тексты — утверждённый copy deck, подача — `treatment` и `motion-spec`, голос — проекция `text/05-voice-editorial/voice.schema.yaml` | site, text, creative | Claude Design; своих форматов брифа, текстов и фактов не заводит |
| направления страницы | creative 01/01 §6; `common/glossary.md#направление` | creative | страница «Направления» холста (cd 06/01 §5) |
| приметы, блок «чего не ставить» | `common/tells.yaml`; `site/09-ai-generation-evaluation/ai-landing-markers.yaml`; `creative/08-uniqueness-anti-slop/cliche-registry.yaml`; text 06/01 | site, creative, text | бан-лист задания (cd 06/05 §2), судья |

## 5. Маршруты «этап → нормы → проверка»

**Сайт и лендинг.** Слой страницы — бриф с уровнем, смысл и факты, воронка, структура, тексты; слой дизайна — мудборд и
направление, ключевые ассеты, ДС страницы, макет, проверки. Структуру задаёт план страницы, а не объекты продукта.

| этап | нормы | проверка |
|---|---|---|
| бриф | поля и минимум — site 01/03 §2, §3; вопросы — site 01/03 §5, о подаче — creative 01/01 §2.3; тип — site 02/01 §6; уровень — creative 01/03 §5 | `site_validate.py`; `page_gates.py --resolve` |
| смысл и факты | факты — text 02/03 §2, §4; позиционирование — text 02/01 §2; осведомлённость и иерархия — text 02/02 §1, §2; голос — text 05/01 §3 | `claims_check.py lint-facts`; `chain_inputs.py meaning-claims` |
| воронка | шаги — site 05/03 §1, §2; призыв — site 05/01 §1; формы — `site/05-conversion-funnels/lead-forms.yaml`; согласие — site 08/01 §1.2; тексты у формы — text 04/04 | `site_validate.py` |
| структура | план — site 04/03 §5; порядок секций — site 03/01 §3; первый экран — site 03/03 §2; SEO и GEO — site 07/01, site 07/02; бюджет — `site/07-seo-geo-performance-analytics/budgets.yaml#levels` | `site_validate.py`, `vocab_lint.py`; блок PRE — site 09/02 §2 |
| тексты | цепочка — text 09/02 §1; слоты — text 04/01, text 04/02; слоп — text 06/01; право — text 08/01; набор — text 08/02; мета — `text/07-seo-geo-copy/meta-rules.yaml`; GEO-слой — text 07/03 §4 | `copydeck.py check`; порядок — text 09/03 §2 |
| мудборд и направления | концепция и направления — creative 01/01 §3–§7; мудборд — creative 02/03 §1; клише — creative 08/01 §1; итог — `art-direction` (creative 01/02) | `refs_client.py`; правила — creative 01/02 §8.1 |
| ДС страницы | токены — `creative/04-visual-language/marketing-tokens.json`; дисплей и гарнитуры — creative 04/01 §2, §4; цвет — creative 04/03 §1; ритм секций — creative 04/02 §3; голос в README ДС — text 05/01 §8.3 | контраст пар — cd 06/02 §2 |
| макет | `treatment` — creative 09/01 §4; движение — creative 09/02; нормы соседей — creative 08/01 §4; бан-лист — cd 06/05 §2; тексты — утверждённый copy deck | `spec_check.py`; `claims_check.py` на HTML-копии; `marketing_audit.py` |
| проверки | порядок — site 09/02 §1.4; ворота — site 07/03 §4; исходы — в репозитории кода (`site/07-seo-geo-performance-analytics/page-gates.yaml#phases`, позиция); подача — creative 09/03 §1; тексты — text 09/03 §2 | чек-лист — site 09/02 §3, §7; `page_gates.py`; `motion_check.py`; судья — `common/judge.md §3` |

Этапам ассетов тройка даёт паспорт визуала из `art-direction` (creative 01/02 §4.1), план ассетов из медиа-слотов
(`plan_to_assets.py`), тексты ассетов (text 10/01 §8) и бриф 3D (creative 01/02 §4.2).

**Многостраничник.** До планов — карта сайта (site 10/01 §5; карты и шаблоны — site 06/01 §2, §3; навигация —
site 06/02). Главная — маршрутизатор, а не посадочная (site 02/01 §4.1); тексты — по шаблонам (text 04/03 §4); единство
системы — creative 04/03 §6; собранный сайт проверяет `ia_probe.py`.

**SaaS.** Кабинету тройка даёт линтер с жанром «интерфейс» (`text/06-anti-slop/profiles.yaml`; маркетинговые слова и
числа в интерфейсе — text 06/01 §11), голос продукта (text 05/01 §2; профиль — `text/05-voice-editorial/voice.schema.yaml`,
позиция) и право (согласие на ПД — site 08/01 §1.2, пробный период — site 05/03 §4.2). Лендинг SaaS — маршрут сайта.

## 6. Предметный указатель

| вопрос | место |
|---|---|
| где задаётся уровень амбиций; какой по умолчанию | `site/10-playbooks-contracts/schemas/site-brief.schema.json#ambition`; `creative/01-creative-direction/ambition-levels.yaml#defaults_by_page_type` |
| можно ли число, отзыв, логотип без источника | text 02/03; формат — `text/02-strategy-messaging/facts.schema.yaml` |
| фактов нет — что ставить на страницу | site 05/02 §1.5; пробел в тексте — text 10/01 §1.3 |
| сколько полей в лид-форме; форма в первом экране | `site/05-conversion-funnels/lead-forms.yaml`; место — site 05/01 §4 |
| квиз, калькулятор или форма | site 05/01 §5.2, §5.4 |
| можно ли попап, exit-intent, таймер акции | site 05/01 §11; срочность — site 05/02 §4 |
| как оформить согласие на ПД и баннер cookie | site 08/01 §1.2, §1.3 (cookie — позиция) |
| в каком порядке секции и сколько их | site 03/01 §3; число — site 03/02 §1.3 |
| один H1 или дисплейный заголовок | site 04/01 §3.2 |
| какой бюджет веса и CWV у страницы | `site/07-seo-geo-performance-analytics/budgets.yaml#levels` |
| какой длины заголовок hero и кнопка | `text/04-copy-by-block/copy-slots.yaml`; кнопка — text 04/01 §6.2 |
| можно ли «лучший», «№ 1», «бесплатно» | `text/08-russian-legal-typography/claims-rules.yaml#COPY-L-SUP-01`; цены — text 08/01 §4 |
| сколько надзаголовков капсом | `text/09-ai-generation-evaluation/copy-checklist.yaml#COPY-C-18` |
| сколько направлений и чем они различаются | creative 01/01 §6 |
| можно ли «в духе Linear»; чужую работу — генератору | creative 02/03 §3, §5.2 |
| сколько гарнитур; какой кириллический дисплей | creative 04/01 §4.4; `creative/04-visual-language/cyrillic-display-fonts.yaml` (позиция) |
| сколько смелых приёмов, цветов, движущихся объектов на уровне | ключи `levels.signature_moves_max` и `levels.motion_hints` в `creative/01-creative-direction/ambition-levels.yaml` (бюджет внимания — позиция) |
| какие длительности у подачи страницы | `creative/04-visual-language/marketing-tokens.json#motion.marketing.duration` (позиция) |
| какой уровень движения передать исполнителю | `creative/01-creative-direction/ambition-levels.yaml#levels.maps_to` |
| можно ли градиенты, стекло, прелоадер | creative 08/01 §4.1; `creative/06-effects-catalog/effects.yaml#glass-panel`; creative 05/02 §9 |
| как сделать паузу движения и reduce на странице | creative 05/01 §3.3, §4 |

## Заметки сборщику

Только для журнала (агент 02 MK, Ф5); в `kb/INDEX.md` не переносится.

**Объём.** Разделы 3–6 ≈ 8,3 тыс. токенов (калибровка prose): §3 — 3,7 (site 1,1, text 1,1, creative 1,3), §4 — 1,3,
§5 — 1,9, §6 — 1,4. Выше ориентира на ≈ 0,3: дороже всего полные пути входов §3 и канонические адреса YAML в §5–§6 (замена
разделов-копий на каноны добавила ≈ 0,2). Сжимать первым: абзацы «Многостраничник» и «SaaS» §5 (строки SaaS пересекаются
с §5 черновика 01), затем строки §6, которые повторяют ячейки §5 (порядок секций, лид-форма, бюджет).

**Спорное и что проверить.**
1. Пакет исполнителя в README баз. `site/README.md` §Как пользоваться (сценарий 1, шаги 8–9) и `text/README.md`
   §Как пользоваться (сценарий 1, шаг 7, `export-kimi`) ведут в пакет kimi, `creative/README.md` — в T7s и MOTION.md для K3.
   Скрипта site_brief_to_kimi.py, на который ссылается шаг 8 site, в скилле нет (остался в `99-raw` исходной базы). Канон —
   вход холста (TR-44, позиция; cd 06/02 §1; `common/owners.md` §Правила владения). Карта ведёт в §Как пользоваться ради
   маршрута; 05 QA — проверить, не уходит ли агент в пакет kimi. Выравнивание README — Ф10.
2. Временный словарь text. `text/README.md` §Как пользоваться: id — из `text/99-raw/notes/temp-vocabulary-v0.yaml` «(site
   ещё не выпустил)» — против канона TR-03. В карте — строка о дефекте утилиты (TR-04, `common/CONTRADICTIONS.md` §1). Утилиты — Ф8,
   README — Ф10.
3. Утилиты только на примерах. `ad_check.py`, `validate_facts.py`, `validate_meaning.py`, `recipe_check.py` зашиты на
   примеры базы; для файлов проекта работают `validate_any.py FILE`, `validate_voice.py FILE`, `claims_check.py lint-facts`,
   `spec_check.py plan|spec`. Для `art-direction` проекта утилиты нет — в маршруте правила creative 01/02 §8.1. Предложение
   Ф8: `ad_check.py FILE`.
4. Разделы-копии (сверка с колонкой `copies` канона). Где норма названа прямо, стоит канон: формы — `lead-forms.yaml`
   (CN-35), бюджет — `budgets.yaml#levels` (GT-11), мета — `meta-rules.yaml` (CN-53), бан-лист задания — cd 06/05 §2
   (VI-06), движение во входе холста — creative 09/02 файлом (NU-37), 3D-слот — `page-plan.schema.json` (TR-57). Оставлены
   как объяснение этапа разделы, которые держат несколько норм и копию одной: creative 04/03 §1 (копия GT-28), creative 01/03
   §5 (GT-24, GT-25), site 07/03 §3 (GT-11, GT-15, GT-24, GT-25), creative 04/02 §3 (канон VI-25, копия NU-22); канон этих
   чисел — в §6. cd 06/01 §5, cd 06/02 §3 стоят читателями, не нормой.
5. Этап «ДС страницы». Со стороны тройки — дельта creative к ДС ui (маркетинговые токены, дисплей, гарнитуры, цвет по
   уровню) и голос в README ДС; сама ДС — ui 14 и cd 05–06 (черновики 01 и 03). Порядок «ключевые ассеты до ДС» (Р101) —
   во вводной строке маршрута; место и контракт этапа ассетов — черновик 03 и Ф6.
6. Проверки исходов (GT-03, позиция): LCP, CLS, INP, вес — в репозитории кода на собранной странице; в репозитории
   стратегии — план, макет, ассеты. `page_anatomy.py`, `geo_probe.py`, `ia_probe.py`, `page_gates.py` без `--resolve` —
   утилиты ветки «после сборки».
7. Приоритет типов (CN-106) — фразой в §3 site со ссылкой на `site/README.md` §Решения заказчика и открытые вопросы. Раздел
   журнальный по форме (решения 1–22 PLAN site); если Ф10 его перенесёт, адрес CN-106 в `canon.tsv` и в карте меняются вместе.
8. Позиции помечены «(позиция)»: TR-44, GT-03, CN-36, VI-21, NU-33, NU-26, TX-31. Не вынесены: TR-22 (бриф — надмножество;
   правила проекции — Ф6), TR-10 (типы `proposed`), TR-12 (реклама ли текст своего сайта, erid — site 08/01 §3), TR-28,
   TR-47 (кнопка мероприятия — text 04/03 §3.5), GT-17, GT-21, GT-25 (`ambition-levels.yaml#levels.L0.appropriate_for.conditions`),
   NU-22, NU-34, NU-37, CN-90, CN-101, VI-11, VI-39, VI-40, JU-13, JU-14, JU-15. Если сборщик даст в разделе 1 правило
   «позиция действует до решения, запись — `common/CONTRADICTIONS.md`», пометки в строках можно снять.
9. §6 — 21 вопрос. Выпали при сжатии (вернуть, если хватит места): тип страницы (site 02/01 §6; запуск продукта —
   `vocabulary.yaml#page_type`, TR-09), температура трафика против осведомлённости (TR-11), люди на сайте (VI-37 — есть в
   §4), первый экран (TR-45 — в §5), FAQ (TR-29, site 03/01 §3.2), английская версия (CN-111, text 10/01 §6), 3D на
   лидогенерации (GT-31 — в §4), 404 и «спасибо» (TR-58, site 05/01 §10), аналитика по умолчанию (CN-108,
   `events.yaml#defaults.systems`), один сигнал на URL (CN-38, site 07/01 §2), поверхности GEO (CN-109, site 07/02), блок
   «коротко» (CN-57, text 07/03 §3.6), тире и знак диапазона (TX-24, TX-25, text 08/02 §1.2, §1.3), переходы страниц (GT-29,
   `effects.yaml#page-transition`), высота hero-CTA (NU-11), киты (VI-14, creative 08/01 §1.3), лицензия GSAP (CN-89),
   `data-motion` (NU-31), пульсация призыва (NU-35).

**Межбазовое — для 03 AS** (со стороны site, text, creative; в §4 — сжато).
- ai-media: план ассетов — формат ai-media 01/01 §8, каркас — `plan_to_assets.py` из медиа- и 3D-слотов, строки ассетов —
  `copydeck.py export-assets` (text 10/01 §8); слот `real-only` → `ai_fit: forbidden` (TR-40), люди — одно правило
  подлинности (VI-37); текст в кадре — только из фактов (TR-42), текст не в пикселях (VI-42 = TX-33, text 05/01 §8); картинка
  OG — по слоту OG плана ассетов, разметка — `head-kit.yaml` (TR-39); паспорт из `art-direction` — creative 01/02 §4.1
  (`boldness` по уровню; снятые умолчания — `lifted_markers`, VI-05); референсы генераторам — роль и hex словами (VI-57);
  зерно страницы ≠ зерно ассета (VI-20, creative 04/03 §4.2); hero продолжает объявление (VI-41, creative 04/02 §2); вес
  первого экрана — профиль страницы, 2,5 МБ ai-media — профиль L0 (GT-14); видео первого экрана — порог по уровню (GT-21,
  позиция), постер видео-hero — SG-PERF-16 (GT-33); `page_accept.py` — одна копия (GT-43); Lottie (CN-90, позиция).
- blender: 3D-слот называет рецепт `recipe:` с тегами словаря site (TR-57); бриф 3D — `art-direction.handoff.blender`,
  creative 01/02 §4.2; 3D по секциям, в конверсии нет (GT-31); LCP и CLS страницы с 3D — профиль site (GT-04); доля 3D —
  ворота blender 09/05 §7.2 (GT-05); 3D за сессию по уровню — creative (GT-07, позиция); 3D-сцена входит в бюджет внимания
  (NU-33, позиция); клише 3D — записи `cliche-registry.yaml` (VI-36); витрина blender стоит на примерах creative
  (`creative/10-recipes/examples/`, узел 19 SYNTHESIS §2.2).
- claude-design: вход холста (TR-44, позиция); бриф холста — проекция `site-brief` (TR-22, позиция; правила проекции —
  Ф6); «Нельзя утверждать» — выгрузка `never_claim` (TR-46); тексты — литералы утверждённого copy deck, ключевые слоты в
  макете на основных артбордах (COPY-C-33, `copy-checklist.yaml`); голос — проекция `voice_ref` (TR-50); движение —
  `motion-spec` и стек уровня (NU-37, позиция), уровень движения — проекция уровня амбиций (GT-27), видео-референс — лист и
  кадры (CN-68, creative 09/02 §4); направления страницы (VI-45) ↔ страница «Направления» холста (cd 06/01 §5, GL-24);
  первый экран — политика плана (TR-45), A3 в ACCEPTANCE cd 06/02 §4 — копия; проверки исполнителя ниже ворот страницы,
  приёмка сайта добавляет блоки SEO и мета, права, форм и событий (GT-42, позиция); бан-лист — блок creative 08/01 §6 в форме
  cd 06/05 §2 (VI-06); нормы соседей на странице — умолчание L0 (VI-05); сведения об эффектах исполнителю — сам
  `effects.yaml` (CN-100); `build.perf` из профиля (GT-14).

**Не вошло сознательно.** Шаги пакета kimi из README site, text, creative (site_brief_to_kimi.py, `export-kimi`, T7s) —
исполнитель макета — Claude Design, вход холста. Утилиты обслуживания и опытов (`checklist_export.py`,
`build_profile.py`, `ux_dict_to_yaml.py`, `run_checks.py`, `registry_check.py`, `validate_stack.py`, `recipe_check.py`,
`idle_probe.py`, `ad_check.py`, `validate_facts.py`, `validate_meaning.py`). Рабочие, но выпавшие при сжатии §3 и §5:
`check_intake.py` (разбор брифа), `validate_any.py` (схема смысла), `validate_voice.py` (профиль голоса), `make_skeleton.py`
(скелет copy deck из иерархии), `copy_extract.py` (текст собранной страницы по слотам), `ab_plan.py` (выполнимость A/B),
`run_axe_targets.py`. Числа норм — только адресом.

**Не прочитано.** Тела тематических файлов: читал «Выжимки для агента» site 01/03, 04/03, 05/03, 10/01; text 02/02, 09/02,
10/01; creative 01/01, 01/03, 02/03, 09/01; разделы creative 01/02 §4, §8 и cd 06/02 §1–§4; остальное — заголовками.
README баз — §Как пользоваться, §Утилиты, реестры, §Карта файлов, §Что не покрыто, у site — §Решения заказчика; блоки
«Выжимка: N правил» — заголовками групп. `text/CONTRADICTIONS.md`, `creative/CONTRADICTIONS.md`, `scripts/*/README.md`
трёх баз — оглавлением. PLAN.md баз — не норма. Раздел PLAN Ф5 «Типовые вопросы» — не открывал по заданию.
