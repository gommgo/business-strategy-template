# creative-research — выжимка «лёгкого» агента (фаза 2, бриф v4)

26.09.2026 · агент фазы 2 (Opus 5.5) · база `/home/mm/Документы/app-design/creative-research/`.
- Корневой README — от 25.09, 08:45. Последняя правка содержимого — 25.09, 16:23: дополнение из claude-design-research.
- Пути ниже — от корня базы, если не сказано иное; `NN/MM` — файл MM папки NN.
- Свои выводы помечены «(вывод)». Категоричные утверждения — с доказательством (grep по `app-design`, код); иначе «(вывод, не проверено)».

## 0. Покрытие чтения

Контрольная точка корневого README: последний заголовок — «## Как обновлять», строка 541. Файл — 546 строк, прочитан через
Read кусками 1–250, 251–500, 501–546.

**README-слой — 100 %**

| файл | строк | прочитано | % |
|---|---|---|---|
| `README.md` | 546 | 1–250, 251–500, 501–546 | 100 |
| `00-glossary/README.md` · `01-…/README.md` · `02-…/README.md` · `03-…/README.md` | 29 · 32 · 22 · 58 | целиком | 100 |
| `04-…/README.md` · `05-…` · `06-…` · `07-…` · `08-…` · `09-…` · `10-recipes/README.md` | 21 · 26 · 22 · 23 · 26 · 51 · 35 | целиком | 100 |
| вложенные: `10-recipes/examples/README.md` · `02-…/library-example/README.md` · `06-…/lab/_vendor/README.md` · `lab/_assets/README.md` | 78 · 21 · 25 · 5 | целиком | 100 |

**Ключевые файлы целиком (9) и почему**

| файл | строк | % | почему ключевой |
|---|---|---|---|
| `01-creative-direction/01-concept-and-directions.md` | 535 | 100 | процедура «бриф → концепция → 3–5 направлений»; стык с этапом «направления» Claude Design |
| `01-creative-direction/02-art-direction-document.md` | 441 | 100 | контракт формата `art-direction` и его проекции в ai-media, blender, kimi, site |
| `02-references-moodboards/01-sources-landscape.md` | 345 | 100 | площадки, условия, лицензии (фокус задания) |
| `02-references-moodboards/02-refs-client-and-library.md` | 533 | 100 | клиент, вход, блокировки, формат библиотеки |
| `02-references-moodboards/03-moodboard-and-handoff.md` | 345 | 100 | процедура мудборда, Take / Do not take, передача |
| `09-ai-execution-evaluation/01-presentation-spec-and-block-treatments.md` | 374 | 100 | контракт `treatment` v1, варианты блоков, `art-direction` v1, пакет исполнителя |
| `10-recipes/00-how-to-use.md` | 98 | 100 | указатель рецептов, маршрут, проверка |
| `99-raw/skills-map.md` | 170 | 100 | требование задания |
| `99-raw/tools/README.md` (серая зона) | 271 | 100 | ключи и ограничения утилит |

**Сжатые слои** (Выжимка для агента, Частые ошибки, Чек-лист; иногда соседние разделы):

| файл | строк | прочитано | % |
|---|---|---|---|
| `00-glossary/glossary.md` | 447 | 1–60 (выжимка и §0), 100–116 (§3 «Референсы»), 410–447 | 26 |
| `01/03-ambition-levels.md` | 459 | 1–48, 345–427 (§7–8, ЧО, ЧЛ) | 29 |
| `03/01-effects-sites-measured.md` | 433 | 1–55, 351–390 | 22 |
| `03/02-motion-on-live-sites.md` | 269 | 1–34, 224–248 | 22 |
| `04/01-display-typography.md` | 398 | 1–57, 332–359 | 21 |
| `04/02-composition-rhythm-sections.md` | 248 | 1–43, 207–229 | 27 |
| `04/03-color-surfaces-product.md` | 247 | 1–42, 201–223 | 26 |
| `05/01-motion-principles-and-access.md` | 659 | 1–80, 119–142 (П1–П13), 537–581 | 23 |
| `05/02-choreography-scroll-transitions.md` | 504 | 1–55, 423–457 | 18 |
| `05/03-micro-motion-and-performance.md` | 305 | 1–48, 243–275 | 27 |
| `06/01-effects-catalog.md` | 683 | 1–70, 136–159 (§1.6), 611–683 | 24 |
| `06/02-hero-video-background.md` | 231 | 1–38, 190–209 | 25 |
| `06/03-effects-lab-method.md` | 217 | 1–44, 188–217 | 34 |
| `07/01-stack-choice.md` | 526 | 1–69, 325–344 (§6.4), 420–526 | 37 |
| `07/02-implementation-patterns.md` | 441 | 1–57, 376–407 | 20 |
| `08/01-cliche-policy.md` | 462 | 1–52, 100–129 (§1.3 с оговоркой X-67), 314–462 | 50 |
| `08/02-uniqueness-and-variation.md` | 421 | 1–53, 196–255 (§4 почерк), 335–370 | 35 |
| `09/02-motion-spec-storyboard-handoff.md` | 388 | 1–34, 203–348 (§4–6 про K3) | 46 |
| `09/03-verification-loop-and-gates.md` | 535 | 1–57, 431–480 | 20 |
| `09/04-effectiveness-rubric.md` | 432 | 1–54, 354–384 | 20 |
| `10/01` · `10/02` · `10/03` | 235 · 178 · 342 | выжимка, ЧО, ЧЛ | 31 · 24 · 17 |
| `10/04`–`10/10` | 104–125 | выжимка, ЧО, ЧЛ (через `sed`) | 22–25 |
| `10-recipes/recipes/variation-ledger.md` | 29 | целиком | 100 |

**Нормы-«процессы» и `99-raw` точечно**

| файл | строк | прочитано | % |
|---|---|---|---|
| `PLAN.md` | 789 | 71–234 (рамки, границы, поправки, конвейер), 541–789 (решения, итог, «как расширять», статус) | 52 |
| `CONTRADICTIONS.md` | 566 | 1–89 (сводная X-01…X-67), 455–566 (§Ж, З, И) | 36 |
| `99-raw/handoff-to-neighbours.md` | 237 | 1–20, 192–237 (kimi, заказчику, внутри базы) | 28 |
| `99-raw/reports/wave4-X-audit.md` | 618 | 30–60 (§2 канон дублей), 234–252 (§9 калибровка) | 8 |
| `99-raw/prompts/_common.md` | 311 | 38–57 («Решения заказчика (обязательны)») | 6 |
| `90-sources/README.md` | 203 | 1–25 | 12 |

**Код**
- Докстринги целиком (`ast.get_docstring`): `marketing_audit.py` (34 строки), `motion_check.py` (53), `effect_bench.py` (32),
  `refs_client.py` (56), `spec_check.py` (15), `registry_check.py`, `validate_stack.py`, `build_effects.py`, `check_refs.py`,
  `build_ad_v1.py`, `idle_probe.py`, `cls_sources.py`.
- Докстринги частично: `recipe_check.py` (6 из 9 строк), `ad_check.py` (6 из 11), `c1_check.py` (6 из 12).
- Ветки кода: константы путей (`ROOT`, `APP`, `LOCKS`, `P{}`), чтение YAML, `DEFAULT_MODES` и `TERMS` у `refs_client.py`,
  блок примет клише у `marketing_audit.py`, вызов `page_accept.py` у `motion_check.py`.

**Не читал:** `99-raw/notes/triad-contract-2026-09-24.md`. Его md5 (051dd00b…) совпадает с копиями site и text; суть есть в выжимке site §2.4.

**Дайджест `_skill-build/digests/creative-research.md` отстаёт.** Его §8 пишет, что пусты `00-glossary/` и `90-sources/`, нет
`skills-map.md` и `handoff-to-neighbours.md`, README — черновик. На диске 26.09 всё это есть; README начинается с заголовка.

## 1. Семантическая карта

### 1.1. Папки

| папка | о чём | что внутри прикладного | ценность |
|---|---|---|---|
| `00-glossary` | термины RU–EN: 289 статей в 12 группах и §0 «ложные друзья» (19 строк) | «где в базе» у каждой статьи; собирается скриптом `99-raw/experiments/S2/01-synthesis-tools/gen_glossary.py` из `gl*.tsv` | **сред**: §0 — готовый список расхождений определений |
| `01-creative-direction` | уровни L0–L2, концепция и 3–5 направлений, документ `art-direction` | процедура из 9 шагов (`01/01` §1.2), банк вопросов, схема v0 и 5 примеров, `ambition-levels.yaml` v0.2, черновики C1 для site | **выс**: вход всей подачи; нормы уровней читает код site |
| `02-references-moodboards` | 36 площадок, клиент поиска, мудборд | `sources.yaml`, `refs-library.schema.json`, `library-example/`, процедура мудборда, `refs_client.py` | **сред–выс**: процедуру и Take / Do not take можно переносить; режим «поиск» зависит от решения по условиям площадок |
| `03-live-sites-measured` | замер 49 эффектных страниц 2025–2026 | `sites.csv` (91 строка × 84 колонки), 31 JSON записей прокрутки, 86 контактных листов | **низ–сред**: источник `[данные: C]` для порогов; сайты чужие |
| `04-visual-language` | display, кириллица, композиция, цвет — дельта к ui | `marketing-tokens.json` и `.css` (87 токенов, из них 47 — `motion.marketing`), `cyrillic-display-fonts.yaml` (37 гарнитур) | **выс** |
| `05-motion` | классы движения, WCAG 2.2.2 / 2.3.1 / 2.3.3, reduce, бюджет внимания, хореография, цена кадра | поправки П1–П13 к соседям, чек-листы CRV-MO, CRV-CH, CRV-PF | **выс** |
| `06-effects-catalog` | 56 эффектов, видео-фон hero, лаборатория | `effects.yaml` v0.3 и схема, 42 страницы `lab/`, метод `effect_bench.py` | **выс** — каталог; **низ–сред** — `lab/` (по базе не образец, X-26) |
| `07-stack-implementation` | лестница стоимости, выбор библиотек, паттерны кода | `stack.yaml` (51 запись + 8 платформ), контракт модуля эффекта | **выс**; скоропортящееся (версии на 24.09) |
| `08-uniqueness-anti-slop` | пять проверок «приём или клише», реестр, вариативность, почерк генераторов | `cliche-registry.yaml` (53 записи + watchlist 7), блок «чего не ставить» | **выс** |
| `09-ai-execution-evaluation` | `treatment` v1, `motion-spec` v1, `art-direction` v1, ворота, рубрика | 4 схемы, `block-treatments.yaml` (84 блока), `effect-gates.yaml` (62 ворот), `effectiveness.rubric.json`, 7 примеров | **выс** |
| `10-recipes` | 10 рецептов, 3 рабочих примера L0 / L1 / L2 | 10 YAML и схема, журнал вариативности, код примеров | **выс** — 01–03 (`verified`); **сред** — 04–10 (`proposed`) |
| корень | точка входа, план, реестр | README (3 сценария, 48 правил и П1–П8), `PLAN.md`, `CONTRADICTIONS.md` (X-01…X-67) | README — **выс**; PLAN — журнал с вкраплениями норм; CONTRADICTIONS — норма |

### 1.2. Границы покрытия

**Вне рамок** (`PLAN.md` 90–99):
- логика страницы, SEO и GEO, формы, право, бюджет и ворота всей страницы — у site;
- тексты — у text;
- генерация картинок и видео, паспорт визуала — у ai-media;
- 3D-модели и ворота 3D — у blender;
- механика пакета K3 — у kimi;
- визуальный слой сервисов — у ui; UX — у ux;
- айдентика с нуля, звук на сайтах, интернет-магазин целиком, игры.

**«Что не покрыто»** (README 495–511):
- K3 не запускался;
- реальные телефоны, Safari и Firefox не проверялись; полевых CrUX и INP нет;
- рубрика на людях и кросс-вендорный судья;
- Blender для L2;
- площадки: Behance (`off`), FWA (`hold`), Dribbble п. 7.7;
- P2-ролики без субтитров; Lottie в лаборатории; X-06; замер отступов (X-38); ворота прелоадера;
- генератор проекций `art-direction` → паспорт визуала и `brief.yaml`;
- рабочие примеры рецептов 04–10.

**Статус** (README, стр. 3): «исследование завершено (волны 1–4), живая фаза не начата». Всё про реакцию исполнителя — `[не проверено]`.

### 1.3. Референсы и мудборд (фокус задания; только факты)

**Площадки.** Паспорт — `02/01` и `sources.yaml`: 36 записей, `checked_at` 2026-09-24.
- **Портфолио со входом:**
  - Dribbble — режим «поиск» (решение заказчика ≈ 15:00 24.09, `PLAN.md` п. 16);
  - Dprofile — «поиск» с 16:24; риск по п. 11.3 соглашения принял заказчик (п. 21);
  - Behance — `off`: «давай пока без беханса», 15:33, п. 19. Адаптер написан, вживую не проверен.
- **Галереи** — 9 адаптеров без входа: Awwwards, CSSDA, FWA, Recent (бывший Godly), godly.design, Httpster, Minimal Gallery,
  Landingfolio, SiteInspire.
  - FWA — `hold` из-за условий II.4.
  - Httpster не обновляется с 2025-05-26.
  - Land-book и Lapa Ninja закрыты Cloudflare → только ссылки заказчика (`manual`).
  - One Page Love — ждём API.
- **Интерфейсы:** Refero, Mobbin (есть платные API и MCP — «кандидат ассистента»), Page Flows.
- **Эффекты и движение:** Codrops, CodePen, витрина GSAP, форум three.js, Shadertoy, Vimeo (только трек V), LottieFiles, Rive.
- **Типографика, мудборды, рунет:** Fonts In Use, Typewolf, Are.na (API; аккаунта у заказчика нет), Pinterest (robots закрыт для
  «*»), Savee, Cosmos, Milanote, «Рейтинг Рунета», «Золотой сайт», Tagline.
- Главный русский источник — Dprofile: кириллица и рынок РФ, но обложки кейсов — мокапы (`02/01` выжимка 10).

**Как собирать** (`02/02`; `99-raw/tools/refs_client.py`, ≈ 3 530 строк):
- **Вход — только заказчик.**
  - Команда `refs_client.py login <сервис>` в его терминале открывает обычное окно Brave 153 без автоматизации
    (`/opt/brave.com/brave/brave`, профиль `~/.config/<сервис>/profile/` с правами 700/600).
  - Агент `login` не запускает, cookie и токены не читает (`_common.md` п. 3).
- **Режимы:** «поиск» (клиент сам листает выдачу), «ассистент» (`get`, `enrich <файл>`, `arena pull` — только ссылки
  заказчика), `off`, `hold`.
  - Режим выбирает заказчик: `DEFAULT_MODES` в коде плюс `~/.config/creative-refs/modes.json`; правка — командой `mode … --why`.
- **Браузер:** `launch_persistent_context(executable_path=Brave, headless=True)`.
  - Отдельный слот `/home/mm/Документы/app-design/.locks/browser-refs.lock`: ≤ 280 с на вызов, ≥ 3 ГБ свободной памяти.
  - Вместе с общим слотом тройки — не больше 2 браузеров.
- **Частоты:**
  - ≥ 10 с + U(0; 6) с между загрузками, ≤ 5 порций на запрос;
  - в сутки: Dribbble 60, Behance 40, Dprofile 60, галерея 40 страниц;
  - челлендж, капча, 401/403 → стоп и пауза 6 ч; 429 → Retry-After, но ≥ 1 ч.
- **Без маскировки:** UA `HeadlessChrome`, `webdriver` = true.
- **robots.txt** — свой разбор по RFC 9309. `urllib.robotparser` ошибочно закрывает Awwwards SOTD.
- **Откуда данные:** DOM, серверный HTML и ответы, которые страница получила сама; своих запросов к API сервиса нет.
- **Хранение:** превью ≤ 800 px WebP — в `~/.local/share/creative-refs/` (вне базы). Дубли — по каноническому id и dHash ≤ 6 бит;
  палитра — k-means в OKLab (`color.py`).
- **Скорость:** 30–55 с на 34–68 кандидатов (опыт B/06).
- **Проверено вживую 24.09:** Dribbble — 170 кандидатов, Dprofile — 110, галереи — 173 записи и ни одной картинки галерей.

**Права и лицензии** (`02/01` §3, условия процитированы с редакцией):
- Почти все площадки прямо запрещают автоматический сбор:
  - Dribbble — п. 7.1, 7.2, 7.11 и правило API «Scraping, copying, saving, or storing our data is strictly prohibited»;
  - Dprofile — п. 11.3;
  - Adobe — п. 6.18 и разд. 17 (запрет использовать контент для ИИ);
  - CSSDA — не копировать скриншоты и описания.
- Позиция базы: человеческая частота, только внутренняя работа, удаление по просьбе автора за 24 ч.
- Лицензии кода:
  - демо Codrops — MIT;
  - публичный пен CodePen — MIT (редакция 2017 года);
  - Shadertoy без явной лицензии — CC BY-NC-SA 3.0, для коммерческого сайта нельзя;
  - LottieFiles — противоречие внутри условий (X-60);
  - GSAP — бесплатен, кроме визуального конструктора анимаций (X-61).
- Открыто — решение заказчика (X-59; handoff cz-01; «Итог» PLAN п. 1): Dribbble п. 7.7 (имена авторов в `author`), правило API о
  хранении, FWA II.4. До ответа действует умолчание «как сейчас».
- **В базе нет ни одной чужой работы:** только ссылка, метаданные и Take (`lib export --format base-safe`).
  - `library-example/` — 5 записей по публичным сайтам с главной CSSDA.
  - Превью там — наши снимки 400×250 с пометкой `rights.use: internal-only` (`_common.md` п. 4).

**Take / Do not take и дисциплина** (`02/03` §3–4):
- **Референс уходит словами:**
  - роль — одна из 11: composition, typography, rhythm, motion, block-solution, brand, structure, color, material, imagery, effect;
  - `applies_to` — `section-role:<id>` site или `block:<id>`;
  - Take — объект + свойство + число;
  - Do not take обязателен: логотип, тексты, фото, цвета чужого бренда, приметы бан-листа;
  - один референс — одна секция.
- **Карточка ДНК:** поля Hallmark `study`, роль, `applies_to`, Take / Do not take, «Values as text» с пометкой measured или estimated.
  - У живого сайта значения меряет `shot.py` + `measure_ui.py`.
  - Палитру считает код, а не модель на глаз.
- **Нормы числа:**
  - лендинг: 1 composition + 1 typography + 1 block-solution + 0–1 motion;
  - исполнителю — 3–5 референсов, в `art-direction.moodboard` — ≤ 12, на доске для заказчика — 8–15.
- Шоты Dribbble и Behance — концепты, «только ДНК»; для структуры и движения берут живые сайты.

**Формат мудборда.**
- `board <имя>` создаёт в библиотеке заказчика (не в базе):
  - `boards/<имя>/index.html` — превью, палитра, роль, Take / Do not take;
  - `sheet.jpg` — контактный лист;
  - `board.md` — описание словами для модели без зрения.
- Запись библиотеки — `refs-library/1` (`refs-library.schema.json`, 566 строк, `additionalProperties: false`).
  - id записи = `ref:<id>` брифа site.
  - Поля: `rights`, `take[]`, `dont_take[]`, `boards[]`, `found[]`, `awards[]`.

**Процедура** (`02/03` §1):
1. Бриф → оси поиска: жанр; приём; эпоха, предмет, материал. Запросы на русском и английском.
2. 30–60 кандидатов, не больше 20 с одной площадки.
3. 3–6 кластеров по осям kimi T2a (бумага, display, тон акцента, макроструктура) плюс уровень движения.
4. 3–5 направлений — решает агент A.
5. Мудборд на направление.
6. Выбор заказчика: `chosen_by`, дата.
7. Запись в `art-direction.moodboard`.
8. Передача исполнителю и соседям.

**Что идёт дальше из мудборда**

| получатель | что | чем / где |
|---|---|---|
| `art-direction` | `moodboard[]` ≤ 12: `ref:<id>`, роль, Take, Do not take, `applies_to` | схема A `$defs/reference` |
| `treatment` секции | `sections[].treatment.refs`, одна секция | `01/02` §4.4; проверка TR-14 в `spec_check.py` |
| `site-brief` | `references: [{ref, role, take, dont_take, source: creative-library, note}]` | `lib export --format brief`; роли color, material, imagery, effect уходят как `other` |
| исполнитель (K3 или Claude) | `refs/NN-<источник>-<id>.jpg` (≤ 2000 px, ≤ 262 144 байт, без альфы) + `refs/README.md` по шаблону kimi; сайт-референс снимает Claude; видео — только `k3` + провайдер kimi (≤ 20 МБ, 10–20 с), для Claude Code — лист 3×3 + кадры + таймлайн текстом | `handoff <мудборд> --out DIR`; `02/03` §5.1 |
| ai-media | роли palette, material, style + класс сюжета; чужие работы генератору картинкой не подаются | `02/03` §5.2; проекция `moodboard → references[]` паспорта не проверена (`01/02`, откр. вопр. 7) |
| blender | текст важнее картинки; берут материал, свет, настроение | `02/03` §5.3 |
| Are.na | `arena push … --channel` — только в private-канал | `02/02` §7.2 |

**Несостыковка.** `02/03`, стр. 138 (таблица «площадки по ролям») пишет «Dprofile — `hold` (п. 11.3)». В `02/01`, `02/02`,
`DEFAULT_MODES` и `PLAN.md` п. 21 — «поиск» с 16:24 (вывод: ячейку не обновили).

### 1.4. Уровни L0–L2 и цепочка `art-direction` → `treatment` → `motion-spec`

- **Уровень задаётся странице и секции** (README П1; решение заказчика 13 в `PLAN.md`):
  - внутренние страницы — L0, лендинги и главные — L1, кампании и портфолио — L2;
  - конверсия — всегда L0;
  - лидогенерация — L1 с конверсией L0; L0 целиком при горячем мобильном трафике ≥ 50 % и `decision_context.price_band` low/mid (П2).
- **Канон — `01-creative-direction/ambition-levels.yaml` v0.2**, 321 строка:
  - `mandatory_all_levels` — 12 правил (CRV-AL);
  - `levels[3]`: allowed, forbidden, motion_hints, `budgets.effects` (наш слой) и `budgets.page` (цели site),
    `section_distribution`, `maps_to` → kimi, visual_dna, taste, impeccable, higgsfield;
  - `section_caps`, `defaults_by_page_type`, `motion_caps`.
- **Числа** — только в YAML (README 34–37):
  - JS эффектов 20 / 100 / 150–200 КБ br;
  - WebGL-контекстов 0 / 1 / 1–2;
  - шрифты 150 / 250 / 300 КБ;
  - CWV одни на всех уровнях.
- **Кто читает YAML кодом:**
  - у нас — `motion_check.py` (пороги через `threshold_ref`), `spec_check.py`, `ad_check.py`;
  - у site — `site_validate.py` (стр. 78), `make_schemas.py`, `build_profile.py`.
  - На файл 21 входящая ссылка из site (grep `--include=*.py`, `links.tsv`).
- **Три слоя передачи** (П4, `09/01` §1):
  - `art-direction` — почему и что главное;
  - `treatment` — подача секции в `page-plan` site;
  - `motion-spec` — таймлайн движения.

**Действующие версии**

| формат | что действует | файлы | чем проверяется | старая версия |
|---|---|---|---|---|
| `art-direction` | v1 объявлен форматом (README, сценарий 1, п. 4); на v0 — 5 примеров и валидатор | v0: `01-…/art-direction.schema.json` (`urn:app-design:creative-research:art-direction:0`, 459 строк); v1: `09-…/art-direction.v1.schema.json` (`:1`, 1 883 строки) — собирается `99-raw/experiments/I/03-art-direction-v1/build_ad_v1.py` из v0 | `ad_check.py` — по схеме v0 и 29 временным id эффектов `treatment.v0` (стр. 27–33) | перенос v1 к владельцу и перевод примеров не сделаны (handoff ci-06, «по желанию») |
| `treatment` | v1 (`urn:…:treatment:1`, 393 строки) | `09-…/treatment.schema.json` | `spec_check.py plan`; site `site_validate.py` читает v1 (стр. 81); `page-plan.schema.json` site ссылается на `treatment:1` (стр. 818, 965) | `01-…/drafts-for-site/treatment.v0.schema.json` (304 строки): его `x-effect-ids-v0` ещё читают `validate_stack.py` и `ad_check.py`; на него ссылаются site `08-legal-trust-a11y/03`, стр. 332, и `ux-marketing-profile.tsv`, стр. 418 |
| `motion-spec` | v1 (`:1`, 746 строк, `x-dom-contract`) | `09-…/motion-spec.schema.json` | `spec_check.py spec`; `motion_check.py --spec` | — |
| варианты блоков | 1.0 | `09-…/block-treatments.yaml` | `spec_check.py blocks` | — |
| каталог эффектов | v0.3 | `effects.yaml` + `effects.schema.json` (`$id` — `https://creative-research.local/…`, не urn) | `build_effects.py` (сборка и схема), `check_refs.py` | `id_map` — 29 старых id |
| рецепт | 0 (`urn:…:recipe:0`) | `10-recipes/recipes/recipe.schema.json` | `recipe_check.py` | — |
| библиотека референсов | 1 | `02-…/refs-library.schema.json` | `99-raw/experiments/B/02-gallery-adapters/offline_check.py`; сам клиент записи схемой не проверяет (grep: в `refs_client.py` нет `jsonschema`) | — |

### 1.5. Каталоги, схемы и пороги: что это за нормы и кто их читает

«Кто читает» — grep `--include=*.py` по всему `app-design`, плюс входящие ссылки из `links.tsv`.

| файл | что описывает | поля | записей | версия | кто читает |
|---|---|---|---|---|---|
| `06-effects-catalog/effects.yaml` (3 633 строки, ≈ 105K ток) | каталог эффектов: эффект — только отсюда (README №29) | id, family, effect_role, level_min, limits, motion, implementation, fallback, mobile, a11y, cliche, cost, verified | 56: L0 16, L1 31, L2 9; `demo` у 44, 12 — по `external_ref` | 0.3 | `spec_check.py`, `recipe_check.py`, `check_refs.py`, `effect_bench.py apply`; site `gen_glossary.py`; 2 ссылки blender. Собирается `99-raw/experiments/F/07-yaml/build_effects.py` из `entries.py` (774 строки) и сводок `F/*/summary.json`; руками не править (README «Как обновлять») |
| `09-…/effect-gates.yaml` (747) | ворота эффектов; «прошёл» = 0 B и 0 S, S снимает только `x-gate-exception` | id, group, modes, metric, op, threshold / `threshold_ref`, severity, site, fix | 62: B 7, S 36, D 18, по уровню 1; ручных 6; группы — a11y 27, perf 11, weight 10, fallback 6 и др. | 0.2 | `motion_check.py` (по умолчанию), `spec_check.py`, `recipe_check.py` |
| `08-…/cliche-registry.yaml` (1 554, 43K ток) | условия приёмов «клише» | sign, signals, detect, threshold, first_seen, saturated_since, status, severity, levels, justify_if, twists, replace_with, cluster, k3_allow, neighbors | 53: saturated 40, dated 13, **fresh 0**; S 25, D 28; кластеров 4; watchlist 7; `k3_allow` у 20; `crosswalk_external` 14 (AIL site, COPY text, IMG/VID-M ai-media) | 0.1; `review_by` 2027-03-24 | `marketing_audit.py` (13 примет в коде, id — из реестра), `registry_check.py`, `check_refs.py`, `recipe_check.py`, `spec_check.py`; разовая правка site `batch-E2.py` |
| `07-…/stack.yaml` (829) | библиотеки и платформы | kind, version, license, size_br, init_tbt_ms, support, use_for, levels, status, alternatives, risks, alive | 51: library 16, runtime 11, platform 10, avoid 10, framework 4 + 8 платформ `constraints.cms` | 0.1, `checked_at` 2026-09-24 | `validate_stack.py` — **сверяет `use_for` с 29 id `treatment.v0`** (стр. 6), `check_refs.py`, `entries.py`; site `make_schemas.py` |
| `04-…/cyrillic-display-fonts.yaml` (233) | гарнитуры с кириллицей (README №13) | license, class, axes, cyrillic, quality, metrics (`lh_floor_caps`, `tracking_touch`, k), good_for, pair_with | 37: OFL 32, коммерческих 5; default 16, caution 16, option 5; `avoid` 9, `no_cyrillic` 29 | 1 | `marketing_audit.py` (MKT-T3/T4), `build_ad_v1.py`, `entries.py` |
| `04-…/marketing-tokens.json` + `.css` | маркетинговые токены DTCG (README №27) | type.display-*, space.section-*, size.hero-*, radius, color, surface, gradient, shadow, `motion.marketing` | 87 токенов, из них 47 движения | DTCG 2025.10 | `spec_check.py` (TR-28, токены в motion-spec), `marketing_audit.py`; site `build_profile.py`; 2 ссылки blender. Копия `.css` в `10-recipes/examples/_shared/` (md5 совпадает) |
| `01-…/ambition-levels.yaml` (321) | уровни L0–L2 (см. §1.4) | см. §1.4 | 3 уровня, 12 обязательных правил | 0.2 | §1.4 |
| `09-…/block-treatments.yaml` (723) | визуальные варианты и эффекты для 84 блоков site | level_max, roles, signature, effects {L0,L1,L2}, visual_variants, mobile, a11y, avoid | 84 блока, 16 семейств | 1.0 | `spec_check.py blocks`; site `gen_glossary.py`; ссылки site 04-blocks (4), blender (2) |
| `02-…/sources.yaml` (1 249) | паспорт площадок | alive, value, search, api, login, antibot, robots, terms, client, rate, checked_at | 36 | sources/1 | **кодом не читается**: grep по `app-design` находит только `_skill-build/inventory.py`; режимы клиента живут отдельно в `refs_client.py` (`DEFAULT_MODES`, `TERMS`) |
| `09-…/effectiveness.rubric.json` (298) | рубрика «эффектности» | criteria (anchors, pairwise_q, vlm, weights), pass_rule, pairwise, vlm_judge, human_calibration | 5 критериев; у craft подкритерий `sub.media` | 0.1 | `build_pairs.py` (опыт K/03), `gen_glossary.py`; ссылка blender `11-evaluation-qa/06` |
| схемы `art-direction` v0/v1, `treatment` v1 (и v0), `motion-spec` v1, `effects.schema.json`, `refs-library.schema.json`, `recipe.schema.json` | контракты форматов | см. §1.4 | — | см. §1.4 | см. §1.4 |
| `10-recipes/recipes/*.recipe.yaml` | машиночитаемые рецепты | — | 10 | схема 0 | `recipe_check.py` (0 ошибок, 0 предупреждений) |
| `03-…/sites.csv` | замер 51 страницы × режимы | 84 колонки (описаны в `03/README`) | 91 строка | 2026-09-24 | рабочие утилиты не читают; читают опыты (`budgets.py`, `c_compare.py`, `build_sites.py`, `palette_count.py`, `signals_from_c.py`), пишет `effects_probe.py` |

### 1.6. Рецепты, примеры, лаборатория, замеры чужих сайтов

**Рецепты 01–10 — норма, а не журнал.**
- Это «маршрут решений» (`10/00` §1): 9 шагов, у каждого — файл-владелец.
- `verified`: 01 L0 лидогенерация, 02 L1 SaaS, 03 L2 запуск продукта — у них рабочие примеры с воротами K 0/0/0.
- `proposed`: 04–10, примеров нет.
- Журнал вариативности: 45 пар рецептов, ни одной пары с отличием меньше 4 осей.

**Примеры `10-recipes/examples/` — эталоны (вывод по фактам):**
- на них сверены ворота: `motion_check` 0.1.3, ворота v0.2 — B 0, S 0, D 0 у всех трёх;
- на них держится статус `verified` рецептов 01–03;
- skills-map кладёт их в `templates/`;
- blender строит на них витрину: `../blender-research/15-showcase/sdano/`, `zveno/`, `KIT.md` стр. 66 (шрифты `_shared/fonts`);
- все три — демо: компании и цифры вымышлены.

**Что сломается без ассетов и бандлов** (по срезу asset и bundle — «не переносим»):
- Все три `index.html` предзагружают шрифты `_shared/fonts/*.woff2` (10 файлов OFL, ≈ 0,5 МБ). Без них — 404 и системный
  шрифт; меняются вид, CLS и значение EG-WEIGHT-07.
- L2 «Звено» грузит `js/three-scene.js` (bundle, 594 КБ; `main.js` стр. 52: `import('./three-scene.js')`) и `img/*.webp`
  (7 файлов ≈ 0,1 МБ — постер-LCP и станции для reduce и без WebGL). Без них нет ни 3D, ни запасного варианта.
- Исходник сцены — `99-raw/experiments/J/04-light-pass/src/scene.js` (43,7 КБ; сборка esbuild + three 0.186.1 из npm) — служебная папка.
- `img/render.log` — мусор.

**`06-effects-catalog/lab/`** — 42 страницы, витрина `index.html` (bundle), всего 2,6 МБ.
- По базе — не образец, а «эффект на пределе ворот» (X-26; README «Что ненадёжно»). Часть демо помечена в `lab.json` (`gate_note`)
  как «антипример ворот».
- Нужна для `effect_bench.py` (цены в `effects.yaml`); skills-map предлагает её как код-референс для `effects-build`.
- Без `_vendor/` страницы с библиотеками не работают (срез: 54 ссылки кода на ассеты). Там GSAP 3.15.0 и Lenis 1.3.26
  (bundle) и шрифты OFL (asset), ≈ 0,6 МБ.
- Без `_assets/` (4 своих WebP, CC0) не работают страницы с картинками.

**`03-live-sites-measured/`** — md 2 + `sites.csv` + `recordings/` (31 JSON и 86 JPG контактных листов чужих сайтов, 6,8 МБ).
- Скриншоты чужих сайтов разрешены только для замера и внутренней работы (`_common.md` п. 4: «в базу — контактные листы и миниатюры»).
  Лицензии самих сайтов не оговорены.
- Для скилла это источник чисел `[данные: C]` (вывод: листы не переносить, JSON записей скиллу не нужны).

### 1.7. «Концепция → 3–5 направлений» и этап «направления» в Claude Design (связь без синтеза)

| тема | creative | claude-design-research |
|---|---|---|
| где | `01/01` §1–7 (выжимка 1–22), `02/03` §1.4–1.6, `08/02` §3 (хвост: 8 → 3–5), README №4–8 | `README.md` стр. 92 (этап 3 «направления») и стр. 161 (правило 9); `04-claude-code-native/01-claude-design-in-claude-code-session.md` стр. 43, 237–244, 397; `05-design-artifacts/01-design-system-and-canvas-in-session.md` стр. 37, 158; `01-product/01-claude-design-product.md` стр. 37, 216–217, 437, 464; `03-practice-pipelines/01-practice-and-pipelines.md` стр. 24, 246 |
| сколько | 3–5, по умолчанию 4; 3 — при строгом бренде (`strict`); 5 — только если одно из них канон | 2–4 low-fi артборда (README:92, 04/01:237); «2–3 варианта» (01/01:37); «Ask for three directions» (01/01:437); «4 направления» (03/01:246); вайрфреймы — 3–5 подходов (04/01:244) |
| оси | 4 оси: бумага, стиль заголовков, тон акцента, макроструктура (id словаря site); каждая пара различается ≥ 2 осями; тёплая бумага или антиква — не больше чем у одного | «названные оси»: фон hex / акцент hex / гарнитура (README:92; 05/01:158) + мотивация и компромисс у каждого |
| форма показа | словами и числами: тезис, палитра hex, гарнитуры с кириллицей, первый экран, приём, риск, цена; картинки — только в живой фазе («генерация платная», решение заказчика 2 из `_common.md`) | low-fi артборды на холсте, мотивация стикерами |
| общий первоисточник | `[документация: Anthropic «propose 4 distinct visual directions»]` (`01/01` выжимка 15) | «Prompting Claude Opus 4.8 — propose 4 distinct visual directions … Ask the user to pick one»; перенос в Claude Design помечен `[не проверено]` (01/01:464) |
| выбор | одна рекомендация; `choice.chosen_by` = customer / default / art-director; смешение — `merged_from`; `approved` — только с подписью заказчика | «выбор или ремикс» (README:92) |
| выход | документ `art-direction` (схема) → `treatment`, паспорт ai-media, blender, пакет kimi (`01/01` §7.2) | артборд; этапы 1–2 конвейера README (стр. 90–91) — `brief.yaml` и `DESIGN.md` + `tokens.css` по шаблонам kimi 07 |

Ещё одно различие по файлам: в creative мудборд (кластеры кандидатов) идёт до направлений (`02/03` §1, шаги 3–4). В строках
90–93 README claude-design этапа мудборда нет (вывод по этим 4 строкам, весь файл не проверял).

### 1.8. Авторская карта скиллов `99-raw/skills-map.md` (S2b, 25.09): что предлагают авторы

**Состав.** Пять скиллов вместо восьми из гипотезы задания:
- `creative-direction`;
- `refs-moodboard`;
- `presentation-spec` — визуальный язык и движение живут в его `references/`; если SKILL.md перерастёт 250 строк, первым выделить
  `motion`;
- `effects-build`;
- `verify-presentation`.

Рецепты — не отдельный скилл, а вход и `templates/` скилла спецификации.

**Принципы:**
- Одна копия правил: YAML и схемы остаются в базе, скилл вызывает утилиты по абсолютному пути
  `CR=/home/mm/Документы/app-design/creative-research`.
- SKILL.md — 150–250 строк; `references/` — выжимки дословно с датой снимка; `templates/` — примеры с пометкой ДЕМО.
- Порядок проверок во всех скиллах один: статичный визуал → движение и цена → F83 → ворота site → рубрика → человек.
- Скоропортящееся — только через YAML с датой.
- Чужие работы — только словами.

**Что не идёт в скиллы:**
- замер жанра: `effects_probe.py`, `scroll_record.py`, `sites.csv`;
- реестр противоречий и отчёты — в скиллы попадают только позиции как правила;
- утилиты обслуживания базы;
- логика страницы, тексты, ассеты, 3D и пакет K3 — это чужие скиллы.

**Порядок сборки:** `verify-presentation` → `creative-direction` → `presentation-spec` → `effects-build` → `refs-moodboard`.
Мудборд — последним, потому что зависит от входа заказчика и решения по X-59.

**Полезно независимо от формата (вывод):**
- единый порядок проверок;
- разделение «выбор эффекта — шаг спецификации» и «реализация и замер — отдельная работа»;
- рецепт как вход, а не отдельный скилл;
- мудборд в режиме «ассистент» работает без входа заказчика.

**Расходится с решениями заказчика:** несколько скиллов, абсолютные пути в базу, выход к скиллу kimi `kimi-design-director` (§8).

### 1.9. Карта на уровне файлов (все md-файлы тематических папок)

| файл | что даёт | вид | 2–3 правила или числа | связи |
|---|---|---|---|---|
| `00/glossary.md` | 289 статей RU–EN; §0 «ложные друзья» (19 строк) | каталог | 1 / 2 / 3 — три разные величины; SDA — только CSS или WAAPI; `effect_role` ≠ `visual_role` ≠ `section_role` | §0 → X-01, X-15, X-19–21, X-54, X-57, X-62, X-63; глоссарии site и text |
| `01/01` концепция и направления | бриф → концепция → территории → главный приём → 3–5 направлений → выбор | процедура | тезис ≤ 240 знаков; территорий 5–7, семейств ≥ 3, буквальных ≤ 1; пары направлений различаются ≥ 2 осями из 4; вопросов подачи ≤ 2 в общем сообщении (≤ 7 вопросов всего) | site-brief; text `meaning`, `facts`; kimi T2a и 07/01 §2.4; Hallmark, impeccable, taste, higgsfield (клоны в кэше kimi); CD README:92 |
| `01/02` документ art-direction | поля, статусы, проекции, решения о клише, бюджет, жизненный цикл, `ad_check.py` | контракт | `approved` — только с подписью; 2–5 решений `use` / `twist` / `avoid`; `budget_profile` = `<page_type>@L<n>`, числа не копировать; исключений ≤ 2 | ai-media `visual-dna.schema.json` (§4.1); blender 04/04 (§4.2); kimi `brief.yaml`, `DESIGN.md` (§4.3); site `page-plan`, `budgets.yaml`, `page-gates.yaml` (§4.4, §6) |
| `01/03` уровни амбиций | обязательное, разрешённое, бюджеты двух слоёв, выбор уровня, секции, соответствие соседям, 9 поправок | правила | CRV-AL-01…12; JS 20 / 100 / 150–200 КБ br; первый экран 1,5/2,5 · 2,0/3,5 · 2,5/4,0 МБ; критический путь LCP ≈ 400 КБ | `ambition-levels.yaml`; site `budgets.yaml`, решение 20; kimi 07/01 §6.2, `build.perf`; ai-media 01/03, `page_accept.py`; blender WEB-01, WEB-04 |
| `02/01` площадки | паспорт 36 площадок, условия дословно, лицензии кода, галереи как данные для C | каталог | 10 с + джиттер, 40–60 страниц в сутки; Shadertoy без лицензии — CC BY-NC-SA; robots.txt по RFC 9309 | `sources.yaml`; `sites.csv`; X-59–X-61 |
| `02/02` клиент и библиотека | вход заказчика, режимы, частоты, адаптеры, превью, dHash, OKLab, `refs-library/1`, Are.na | процедура + схема | вход только у заказчика; челлендж → пауза 6 ч; превью ≤ 800 px вне базы; dHash ≤ 6 бит | `refs_client.py`, `color.py`; site-brief `$defs/reference`; kimi 07/03 |
| `02/03` мудборд и передача | процедура, карточка ДНК, роли, передача K3, ai-media, blender, site | процедура | 30–60 кандидатов, ≤ 20 с площадки; 3–5 референсов на направление, ≤ 12 в art-direction; K3: ≤ 2000 px, ≤ 256 КиБ | `01/01`; kimi 03/04 T2a–T3c, 07/03; ai-media 06/01; blender 04/04; site `vocabulary.yaml` |
| `03/01` эффектные сайты в числах | 49 страниц: библиотеки, анимации, WebGL, видео, веса, CWV, reduce, телефон | данные | GSAP 55 %, ScrollTrigger 47 %, SDA — 2 из 49; первый экран без видео — медиана 3,3 МБ; reduce уважают 4 из 21 | `sites.csv`, `effects_probe.py`; A, E, F, K |
| `03/02` движение на живых сайтах | ритм по записям прокрутки 23 страниц | данные | покой между «вау» — у 21 из 23; «вау-переходов» ≤ 4; виртуальная прокрутка — у 3 из 23 | `scroll_record.py`; E (бюджет внимания), K |
| `04/01` display-типографика | роли на clamp, кегль по длине H1, кириллица, гарнитуры, метрический фолбэк, eyebrow, hero-CTA | правила | clamp: max ≤ 2,5 × min; H1 ≤ 2 строк (1440) и ≤ 4 (390); Oswald, Inter, Manrope, Roboto для русского display — нельзя | ui 02-typography; text (длина H1); `cyrillic-display-fonts.yaml`; MKT-T1…T5 |
| `04/02` композиция и ритм | сетка, hero «текст ↔ медиа», высота hero, фоны, шапка | правила | центр — при ≤ 4 элементах; hero `offer-cta` 60–85svh, `poster` 100svh; отступы секций 64–160 px; инверсий фона ≤ 2 | site 03-page-structure/03, `blocks.yaml`; ai-media F/02–03, J/06; ui 05-layout |
| `04/03` цвет, поверхности, продукт | цвет по уровню, тёмные сайты, градиенты, стекло, зерно, подача продукта | правила | хроматических: L0 ≤ 2, L1 ≤ 3, L2 ≤ 4; контраст — в худшей точке градиента; стекла ≤ 2 слоёв в видимой зоне (X-24) | ui 01-color, 11/02; ai-media 01/02, 01/03; MKT-C1/C2 |
| `05/01` принципы движения и доступность | классы движения, П1–П13, WCAG, reduce, переключатель, бюджет внимания, вестибулярка, длительности | правила | петля дольше 5 с — видимая пауза; ≤ 3 вспышек в секунду; бюджет 1 / 2 / 3 (телефон — на 1 меньше); «дыхание» ≤ 2,5 % пикселей/с; вход `cubic-bezier(0.16, 1, 0.3, 1)` | ui 08; ux 06/03, 03/03; blender 07/04, 09/03; kimi 07/01 §6.2, T7; токены `motion.marketing` |
| `05/02` хореография, прокрутка, переходы | ритм, система появления, SDA против ScrollTrigger, pin, горизонталь, Lenis, переходы, прелоадер, LCP | правила | pin-сцена: L1 ≤ 150vh, L2 ≤ 400vh и ≤ 5 шагов; `sticky` или `pinType: 'transform'` (обычный pin — CLS 1,6–2,0); Lenis только на L2, хвост ≤ 1 с | опыты E/01, E/02; `07/01`; X-01, X-10, X-15, X-21 |
| `05/03` микродвижение и цена | наведение, CTA, курсор, магнит, текст; цена свойств, LoAF, INP, телефон | правила | свой курсор — только L2 и мышь; магнит ≤ 8 px; LoAF при прокрутке ≤ 2 % (десктоп) и ≤ 10 % (телефон); в покое 0 кадров | ui 08/02; blender 09; F; K |
| `06/01` каталог эффектов | нормы по семействам; §1.6 — киты компонентов (25.09) | каталог | эффект — только из `effects.yaml`; все эффекты дают 60 к/с, цену меряют мс/с, CLS, покоем; H1 не разбивать; бегущая строка 30–60 px/с | `effects.yaml`; blender 01/01, 09/04; ai-media 10/03; реестр H; `stack.yaml`; дайджест CD `6XNhZu6mJlE` |
| `06/02` видео-фон hero | когда видео, кодирование, постер = LCP, пауза, reduce, синемаграф | рецепт | постер ≥ 0,05 бит/пикс; AV1 → H.264; при reduce, Save-Data, 2G — 0 байт видео; синемаграф ≤ 5 с и ≤ 300 КБ | ai-media 10/02, J/05; site SG-PERF-16; `motion_check --f83` |
| `06/03` метод лаборатории | режимы и метрики `effect_bench.py` | процедура | режимы desk, mob, rm, nojs, nogl, wk, unl; различители — TaskDuration, CLS, движение в покое, клик-зонд | `effect_bench.py`, `cls_sources.py`; blender F2 `fx_probe.py` |
| `07/01` выбор стека | лестница стоимости, уровень × эффект → стек, лицензии, фреймворки, платформы, пакет kimi; §6.4 — киты (25.09) | правила + каталог | L0 без библиотек анимации; GSAP 24–52 КБ br (нельзя no-code-конструктор, нельзя вырезать `@license`); смысл в SSR/SSG, SPA — нет; версии — `npm view` | `stack.yaml`; site 07/01; kimi 07/02 §8.1; blender 01/03; CD S32–S34 |
| `07/02` паттерны реализации | прогрессивное улучшение, reduce-ветка, ленивая инициализация, модуль эффекта, склейка ScrollTrigger + Lenis + VT | паттерны кода | модуль `{id, budget, supports, init, reduce, mobile, pause, resume, destroy}`; в reduce ≈ 2 КБ JS вместо ≈ 35; `ScrollTrigger.refresh()` после смены раскладки | опыты G/02, G/03; ai-media 10/01; site 07/01 |
| `08/01` политика клише | пять проверок, эпоха, доза, маркеры соседей = умолчания L0, блок «чего не ставить», оговорка о китах (X-67) | правила + процедура | исходы `use` / `twist` / `avoid`; доза L0 ≤ 1, L1 ≤ 2, L2 ≤ 3; ≥ 3 записи одного кластера на сцене — провал; у эффекта из кита ≥ 2 параметра отличны от демо | реестр; ai-media IMG-M, R3; blender MAT-07, BR-02; ui 11/04; kimi 05/03, `k3_checks.py`; site AIL |
| `08/02` уникальность и вариативность | прототипичность, что ломать, журнал 8 осей, хвост, почерк K3, Claude, Lovable; детекторы | правила + данные | два теста вместе; проекты подряд — ≥ 4 отличия из 8 осей; детекторы — вход, не вердикт | ui 13/02 (Tuch 2012); kimi 05/03, E/01, E/04; опыты H/01–02; `recipe_check.py --ledger` |
| `09/01` спецификация подачи | `treatment` v1, варианты блоков, `art-direction` v1, пакет исполнителя | контракт | у секции `level`, `visual_role`, `motion_level`; пиков 0 / ≤ 2 / 2–4; конверсия — L0 и `calm`; цели — id v1, разметка `data-*` | site `page-plan` v1, `blocks.yaml`, `site_validate.py`; kimi `build_package.py`; text copy-deck |
| `09/02` спецификация движения | `motion-spec` v1, станции, раскадровка, видео-референсы K3, T7s | контракт + промт | моменты — таймлайном; диапазон — по `subject`; станции — якорями, допуск ±24 px; видео — только `k3`, ≤ 20 МБ | `motion-spec.schema.json`, `spec_check.py`; kimi T3c, T7, T10, 07/03; `motion_check.py` |
| `09/03` цикл проверки и ворота | цикл, что видит VLM, 62 ворот, профиль `marketing`, опыты K/01–02 | процедура + пороги | скриншот движение не проверяет; «прошёл» = 0 B и 0 S; reduce — ≤ 0,3 %/с по всей записи; профиль снял 68 % ложных «серьёзно» | `effect-gates.yaml`, `motion_check.py`, `marketing_audit.py`; site `page-gates.yaml` (выше); ui `ui_audit.py`; ai-media `page_accept.py` |
| `09/04` рубрика эффектности | 5 критериев, попарно с референсами класса, VLM-судья, калибровка | рубрика | сначала ворота; два порядка A/B; VLM-сортировка — при согласии с заказчиком ≥ 0,8; нужен «слепой судья другого вендора» | `effectiveness.rubric.json`; ai-media 11/02; ui 13/02; blender 11-evaluation-qa/06 |
| `10/00` как пользоваться рецептами | маршрут из 9 шагов, выбор рецепта, проверка, журнал | указатель | рецепт — не шаблон; `verified` = 0 B и 0 S | все папки; site 10-playbooks |
| `10/01` лидогенерация L0 | + ветка L1, Тильда, Битрикс | рецепт | H1 ≤ 38 знаков и без анимации; JS подачи 0 КБ; ниже первого экрана появлений нет | site «Отвес»; text copy-deck; пример `l0-sdano` |
| `10/02` SaaS L1 | sticky-сцена на CSS SDA | рецепт | одна сцена ≤ 150vh; 0 КБ JS; начальное состояние — внутри `@supports`; счётчик — стопкой цифр (WebKit) | site «Окошко»; пример `l1-sverka` |
| `10/03` запуск продукта L2 | 3D кодом, световой проход, попарное сравнение с Unseen | рецепт | один холст, рендер только по вводу, 0 кадров в покое; LCP — постер своего рендера; тон-маппинг Khronos PBR Neutral | blender (мир вокруг продукта, KTX2); пример `l2-zveno`; blender 14-code-3d, 15-showcase |
| `10/04` кампания D2C L2 | секвенция по прокрутке | рецепт (`proposed`) | биты истории — HTML; секвенция грузится после LCP, телефону — половина кадров | site 02 §5; ai-media 10/pages/05 |
| `10/05` мероприятие L1 | видео прошлого года, программа | рецепт (`proposed`) | видео — только настоящая съёмка; петель ≤ 2 (телефон ≤ 1, X-65) | ai-media 01/02; `page_accept.py` |
| `10/06` портфолио студии L2 | переход «карточка → кейс» | рецепт (`proposed`) | кросс-документный VT как улучшение; курсор несёт функцию; лента ≤ 5 панелей | `07/01` §5; E/02 |
| `10/07` промо приложения L1 | экран приложения в DOM | рецепт (`proposed`) | same-document VT; официальные значки магазинов | site 02 §8 |
| `10/08` корпоративный сайт L0/L1 | уровни по шаблонам | рецепт (`proposed`) | «вау» — на отдельной промо-странице; переход ≤ 300 мс | site 06-multipage; A `defaults_by_page_type` |
| `10/09` рунет, кириллический display L1 | онлайн-школа на Тильде | рецепт (`proposed`) | проверенные пары гарнитур; preload cyrillic + latin; ось ширины по прокрутке | D; F2 |
| `10/10` тёмный продукт с переливом L1 | перелив = свойство покрытия | рецепт (`proposed`) | перелив — только как свойство продукта; «дыхание» ≤ 2,5 %/с | голо-шейдер F2; blender 12-09 |
| `10/recipes/variation-ledger.md` | журнал 8 осей для 10 рецептов | таблица | 45 пар, 0 пар с отличием < 4 осей | `recipe_check.py`; `08/02` §3 |

### 1.10. Термины (для общего словаря)

- **«уровень»** — уровень амбиций L0–L2 страницы или секции. Ещё есть `level_min` эффекта и `motion_level` — производная шкала
  kimi `none / subtle / expressive / cinematic` (глоссарий §0).
- **«зона»** — видимая зона экрана («петель в видимой зоне» — 24 употребления) и зона текста в кадре (35–45 %). В смысле «зона
  ответственности базы» не употребляется.
- **«слот»** — два смысла:
  - текстовый слот плана site: цель `<секция>.<слот>`, атрибут `data-slot`;
  - «слот браузера» — файловая блокировка `browser-refs.lock`.
- **«блок»** — блок site (`block:<id>`, 84 штуки) и «блок «чего не ставить»» для исполнителя.
- **«flow»** — только как семейство макроструктур (grid, document, poster, flow) в `01/01` §6.2; в смысле «сценарий» не употребляется.
- **«роль»** — четыре смысла: `visual_role` секции, `section_role` site, `effect_role` эффекта, роль референса.
- **«ворота»** — три смысла: ворота эффектов (EG-…), ворота страницы site (SG-…, стоят выше), экран «Enter» перед сайтом.
- **Префиксы:** `CRV-` (чек-листы тройки), `EG-` (ворота эффектов), `MKT-` (профиль `marketing`), `TR-` и `MS-` (правила
  `spec_check.py`), пространства id `effect:`, `cliche:`, `block:`, `ref:`, `recipe:`.

## 2. Нормы, которые легко принять за процесс

| норма | где | суть и статус | на неё опирается |
|---|---|---|---|
| Реестр противоречий | `CONTRADICTIONS.md` (566 строк) | X-01…X-67. По счёту README (66 пунктов, 25.09 08:40): решено 31, позиция 22, открыто 9, передано 2, «позиция и открыто» 1, решение заказчика 1. X-67 (позиция) добавлен 16:23. Открыты: X-06, X-32, X-38, X-42, X-48, X-58, X-60, X-61, X-66; X-59 ждёт решения заказчика. Разделы: §А–Е (темы), §Ж (26 поправок), §З (рецепты), §И (25.09) | 240 упоминаний `X-NN` (53 разных) в содержимом; README: «два файла расходятся — действует `CONTRADICTIONS.md`» |
| Таблица поправок к соседям | `PLAN.md` 113–145 (26 строк) → `CONTRADICTIONS.md` §Ж (где закрыта каждая) → строки «Поправка к `../<база>/<файл> §N` для сайта» в `01/03` §8 (9), `04/*` (5), `05/01` §2 (П1–П13), `05/03`, `09/01`, `09/03`, `10/09` | правила ui, ux, ai-media, blender, kimi — это умолчание L0, на сайте действует своё; все 26 строк закрыты по существу | README П3; «Как расширять базу»; принцип «соседей не правим» |
| Границы с соседями | `PLAN.md` 101–111 | таблица «что берём ссылкой / что наше» для ui, ux, ai-media, blender, kimi, site, text | формула «владелец темы» в файлах |
| Схема конвейера и форматы | `PLAN.md` 186–233 «Как всё сочетается» | схема: заказчик → site → creative (уровень → концепция → мудборд → направления → `art-direction` → `treatment`) → text, ai-media, blender → **kimi (пакет) → K3 или Claude** → проверка. Форматы, которые база создаёт (`art-direction` — № 5, `effects.yaml` — № 6, запись библиотеки — № 7, ещё 11 своих) и потребляет. Точки синхронизации С1–С4; по факту — C1, S0, S1, T2, S2 | `01/01` §1.1, `09/01` §1 |
| Контур передачи подачи | `09/01` §1 | кто пишет какой слой, что он несёт, кто читает и проверяет | — |
| Таблицы соответствия (проекции) | `01/02` §4.1–4.4, `01/03` §7, `ambition-levels.yaml` `maps_to` | `art-direction` → паспорт ai-media, blender, kimi, site; уровни → kimi, паспорт, taste, impeccable, higgsfield | `ad_check.py`, слой 2 |
| Канон дублей | `99-raw/reports/wave4-X-audit.md` §2 | ≈ 20 норм: где встречается → где канон; правило «число живёт в одном машиночитаемом месте» | README 34–37 («таблица канонов — `wave4-X-audit.md` §2») |
| Калибровка утилит | тот же файл, §9 | 14 порогов: источник числа, цена ошибки, как калибровать (например, «абсолютные мс/с между сессиями не воспроизводятся: 42 против 14») | README «Что ненадёжно», «Живая фаза» |
| Решения заказчика — **две нумерации** | `PLAN.md` 541–585 (п. 1–24) и `99-raw/prompts/_common.md` 39–55 «Решения заказчика (обязательны)» (п. 1–6) | «решение заказчика 13» (14 ссылок), 20, 8 — нумерация PLAN. «Решение заказчика 2», «решения 3–4», «правило заказчика 4» — нумерация `_common.md`: платных вызовов нет, вход только у заказчика, чужие работы — только для внутренней работы, видео — только трек V | README П5; `01/01` §6.5; `02/*`; `90-sources/README` |
| Открытые решения заказчика | «Итог» `PLAN.md` 683–695 (5 пунктов) + handoff cz-01…03 | условия площадок; Playwright Firefox; Blender для L2; удалять ли видео YouTube (4,5 ГБ) и `node_modules` (377 МиБ); лицензии GSAP и LottieFiles. До ответа — умолчания | README «Что не покрыто» |
| Передача соседям | `99-raw/handoff-to-neighbours.md` (237 строк; по README — 123 строки: site 35, text 15, ui 16, ux 3, ai-media 14, blender 13, kimi 14, прочее 13) | kimi ck-01…14 — все «не отправлено»; site — ответы на C1–C10 и открытые cs-01…12 (к сверке S2); ci-01…09 — задачи внутри базы | README «Сёстры и соседи» |
| Метки доказательности | `PLAN.md` «Метки» (390–413, не читал) + README 365–386 | легенда меток и «что ненадёжно» | все выжимки |
| Контракт тройки | `99-raw/notes/triad-contract-2026-09-24.md` (копии site и text, md5 совпадает) | `art-direction` — формат № 5, владелец creative; иерархия ворот: страница выше эффектов и ассетов; §4 — правила браузеров | `01/01` [S1], `01/02` [S1], `02/02` [S11] |
| Живая фаза | README 517–539 | 15 гипотез: тест, критерий успеха, где | — |

## 3. Перенос

Итог среза по классам: переносим 352 файла (5,1 МБ, ≈ 2 034K ток). Не переносим: ассеты — 4 910 файлов (5,07 ГБ), мусор — 16 495,
служебное — 1 925. Из них `99-raw` — 20 102 файла (5,5 ГБ), `91-videos` — 3 116 (299 МБ).

### 3.1. По умолчанию «переносим», но на деле не нужно (или нужно частично)

| что | объём | почему | решение |
|---|---|---|---|
| `PLAN.md` | 51K ток | план и журнал волн с вкраплениями норм | Не переносить файлом. Извлечь: рамки и границы (71–112); «Как всё сочетается» (186–233); решения заказчика 5, 13, 16, 19, 21 и нумерацию `_common.md` 1–6; метки (390–413); открытые решения (683–695); «Как расширять базу» (703–743) — сжать под оставшиеся утилиты. Таблица поправок (113–145) уже закрыта в §Ж и строками в файлах |
| `01-…/drafts-for-site/site-brief-creative-fields.yaml` | 331 строка | ранний выпуск C1 для site (site его принял); 47 строк kimi, включая `kimi_crosswalk` | Скиллу не нужен (вывод, не проверено: поля вошли в `site-brief` v1 — сверить со схемой site). Ссылку site `10/01`, стр. 135, переписать |
| `01-…/drafts-for-site/treatment.v0.schema.json` | 304 строки | заменён v1 | **Пока держать**: `x-effect-ids-v0` читают `validate_stack.py` и `ad_check.py`; ссылаются site `08/03`:332 и `ux-marketing-profile.tsv`:418. После перевода валидаторов на `effects.yaml` — не переносить (вывод) |
| `art-direction` v0 и v1 | 459 + 1 883 строки | v1 = v0 + поля, генерируется | Оба взять, пока v1 не перенесён к владельцу (ci-06): примеры и `ad_check.py` работают на v0, README объявляет v1 |
| `03-…/sites.csv`, 31 JSON записей | 28K ток + JSON | сырьё замера чужих сайтов; рабочие утилиты не читают (только опыты A/03, C, H/04, S1/02) | `sites.csv` — только если нужен перезамер порогов (вывод; так же site решила про `pages.csv`); JSON — не переносить; md `03/01–02` — оставить как источник `[данные: C]` |
| Утилиты `99-raw/tools` «только для ресерча» и обслуживания | ≈ 200K ток | `fetch`, `render_fetch`, `yt_*`, `vtt2md`, `transcribe_local`, `site_probe`, `asset_inventory`, `check_links`, `orch_check`, `extract_for_audit`, `ctx_watch`, `sources_collect`, `effects_probe`, `scroll_record` | В скилл не брать (skills-map, «Что не идёт»). `check_links.py` может пригодиться для финальной уборки (7 разных версий в базах) |
| `06-effects-catalog/lab/` | код 132 файла, 2,6 МБ с ассетами | по базе — не образец (X-26) | Опционально: только если переносятся `effect_bench.py` и работа «эффект кодом». Иначе не переносить (вывод); тогда `demo` у 44 записей `effects.yaml` потеряет цель |
| `10-recipes/examples/_shared/marketing-tokens.css` | 13 КБ | копия `04/…css`, md5 совпадает | одна копия (вывод) |
| `l2-zveno/img/render.log` | — | мусор | не брать |

### 3.2. По умолчанию «не переносим», но нужно

| что | зачем | решение |
|---|---|---|
| `99-raw/tools/README.md` (271 строка) | ключи, ограничения, самопроверки утилит; 13 входящих ссылок | взять с адаптацией: только разделы оставленных утилит |
| Валидаторы в `99-raw/experiments/`: `I/01-schemas/spec_check.py` (823 строки), `A/01-…/ad_check.py`, `J/03-…/recipe_check.py`, `H/03-…/registry_check.py`, `G/00-…/validate_stack.py`, `J/02-…/idle_probe.py` | их вызывают сценарии 1–3 README и README папок 01, 09, 10 | перенести в утилиты с адаптацией путей; `ad_check.py` и `validate_stack.py` перевести с `x-effect-ids-v0` на `effects.yaml` (вывод) |
| Генератор `effects.yaml`: `F/07-yaml/build_effects.py` + `entries.py` (774 строки описаний) + `check_refs.py` + сводки `F/*/summary.json`, `results.jsonl` | по README `effects.yaml` правится только сборкой | либо перенести генератор вместе с данными, либо объявить `effects.yaml` исходником и проверять схемой (вывод; вопрос 3) |
| Генератор глоссария `S2/01-synthesis-tools/` (`gen_glossary.py`, `gl*.tsv`) | так глоссарий пополняется по `00/README` | не нужен, если глоссарий станет исходником (вывод) |
| `J/04-light-pass/src/scene.js` (43,7 КБ) | исходник бандла L2; на него ссылаются blender `14-code-3d` (4 ссылки) и `15-showcase/KIT.md` (2) | взять, если L2-пример переносится без бандла (вывод) |
| Ассеты эталонов: `examples/_shared/fonts/` (10 woff2 OFL + LICENSE, ≈ 0,5 МБ), `l2-zveno/img/*.webp` (7 файлов, ≈ 0,1 МБ, свой рендер), bundle `l2-zveno/js/three-scene.js` (594 КБ) | без них примеры не работают (§1.6) | калибровочный минимум (вопрос 2) |
| `99-raw/prompts/_common.md`, раздел «Решения заказчика (обязательны)», п. 1–6 | на них ссылаются «решение заказчика 2», «решения 3–4», «правило заказчика 4» | извлечь положениями, не файлом |
| `wave4-X-audit.md` §2 и §9 | канон дублей (на него ссылается README) и калибровка порогов | извлечь в содержимое |
| `99-raw/handoff-to-neighbours.md` | не-kimi строки «ждёт» и «S2» — список расхождений с соседями; ci-01…09 | файлом не переносить; не-kimi строки — в общий файл расхождений скилла (вывод) |
| `venv-A/B/F/I/J` (6,4 + 3 × 1,3 + 109 МБ) | окружение валидаторов (jsonschema ≥ 4.18, referencing, pyyaml) | не переносить; записать `requirements` |
| `E/01-lcp-reveal/README.md`, `E/02-scroll-scene/README.md` | на них как на доказательства ссылается site (8 ссылок из `site-checklist.yaml` и 09/02) | косметика: заменить ссылку числом (вывод) |
| `A/02-c1-check/treatments.yaml` | на него ссылаются пример site `lead-services-otves/plans/home.yaml`:24 и `01/01` §7.2 («образец») | не нужен: есть overlay-примеры в `09/examples`; ссылку переписать (вывод) |

### 3.3. Серые зоны среза: решения

- **`PLAN.md`** — см. §3.1.
- **`90-sources/`** — README 203 строки и `sources.tsv` (274 источника после 25.09). Не переносить: разделы «Источники» остаются
  в самих файлах (вывод).
- **Служебное, на которое ссылается переносимое** (188 ссылок). Главные цели: `tools/README` (13), handoff (10), X-audit (8),
  `spec_check.py` (8), `90-sources/README` (7), отчёт J (6), контракт тройки (6), промт следующей сессии (6), `ad_check.py` (5),
  `build_effects.py` (5), `91-videos/catalog` (5).
  - Ссылки на валидаторы и генератор — критичны (§3.2).
  - Ссылки на отчёты, заметки и промты — косметика.
- **Код, который ссылается на ассеты** (54 файла): 53 — лаборатория, 1 — `marketing-tokens.css` (`url("noise.svg")`; такого
  файла рядом нет).

### 3.4. Крупные файлы (≥ 25K ток)

| файл | ≈ ток | решение |
|---|---|---|
| `effects.yaml` | 105K | взять (ядро; см. генератор в §3.2) |
| `refs_client.py` | 90K | взять с адаптацией, условно — по решению X-59 |
| `motion_check.py` | 72K | взять |
| `PLAN.md` | 51K | не файлом (§3.1) |
| `check_links.py` · `sources_collect.py` · `effects_probe.py` | 45K · 41K · 40K | нет (обслуживание базы и замер жанра) |
| `cliche-registry.yaml` · `marketing_audit.py` | 43K · 42K | взять |
| `ui_audit.py` · `measure_ui.py` | 36K · 29K | одна копия на всю систему (md5 совпадает в 4 базах) |
| `06/01` · `05/01` · `07/01` · `09/03` | 32K · 32K · 27K · 26K | взять; первые три длиннее нормы 500 строк (ci-09) |
| `CONTRADICTIONS.md` · `README.md` · `glossary.md` | 30K · 29K · 28K | взять (норма, точка входа, словарь) |
| `sites.csv` | 28K | §3.1 |

## 4. Код и утилиты

| утилита | что делает | зачем в работе | зависимости и окружение | зашитые пути и раскладка | вердикт |
|---|---|---|---|---|---|
| `99-raw/tools/marketing_audit.py` 0.1.1 (1 234 строки) | профиль `marketing` поверх `ui_audit.py`: 24 перенастройки порогов, проверки MKT-T, MKT-C, MKT-M, MKT-J1, 13 примет `cliche:*` → `.marketing.md`, `.json`, `.fix.txt`; самотест — 31 проверка | сценарий 2, статичный визуал; `--allow cliche:<id>` — только вместе с решением в `art-direction` | Playwright Chromium, PIL, numpy; импорт `ui_audit.py` и `color.py` из той же папки | блокировки `/home/mm/Документы/app-design/.locks/browser.lock` и `99-raw/tools/.locks/…`; `ROOT = ../..` → `04-…/cyrillic-display-fonts.yaml`; вывод по умолчанию — `99-raw/cache/audit` | **взять с адаптацией** (блокировки, путь вывода) |
| `motion_check.py` 0.1.3 (2 380) | 5 режимов (desk, mob, rm, nojs, nogl): вес по фазам, LCP и «H1 выпал из LCP», CLS, LoAF, хвост и перехват прокрутки, 6-я секунда, петли в зоне и под текстом, вспышки 25 к/с, пауза и переключатель нажатием, WebGL в покое, сверка с `motion-spec` → `gates.md`, `.json`, `fix.txt`; `report` — пересчёт без браузера; самотест — 45 | сценарий 2, движение и цена; ворота эффектов | Playwright, ffmpeg, numpy, PIL, PyYAML, brotli; `flock`; для `--f83` вызывает `page_accept.py` (ключ `no_preference`) | `ROOT` → `09-…/effect-gates.yaml`, `01-…/ambition-levels.yaml`; абсолютная блокировка тройки | **взять с адаптацией**; известные ложные срабатывания — X-66 (цели внутри sticky-слоя, EG-A11Y-25) |
| `effect_bench.py` (893) | прогон `06-effects-catalog/lab/<id>/` в Chromium и WebKit (режимы desk, unl, rm, nogl, nojs, mob, wk, wkrm, wkmob) → `results.jsonl`, `summary.json`; `apply` — числа в YAML; самотест 48 | цена эффекта при добавлении в каталог | Playwright, PIL, numpy, brotli; свой HTTP-сервер с Range | `LAB = ROOT/06-effects-catalog/lab`; абсолютная блокировка | **взять с адаптацией**, только если переносится лаборатория; иначе не брать |
| `refs_client.py` (≈ 3 530) | вход заказчика (Brave), «поиск» (Dribbble, Dprofile; Behance `off`), 9 галерей, «ассистент», библиотека, мудборд, `handoff` в формате kimi, Are.na; самотест — 48 проверок без сети | шаг «мудборд» сценария 1 | Playwright с `executable_path` = Brave 153 (совместимость по мажорной версии Chromium — «use at your own risk»), PIL, numpy, `color.py`; сеть | `/opt/brave.com/brave/brave`; блокировки `…/.locks/browser-refs.lock`; `~/.config/<сервис>/`, `~/.local/share/creative-refs/`; журнал и состояние — `99-raw/cache/refs/` | **взять с адаптацией** по решению заказчика (вопрос 1); режим «ассистент» и галереи работают без входа |
| `page_accept.py` (353; = копия site; у ai-media — 377 строк, другая md5) | F83 по буквам, вес, LCP, reduce | его вызывает `motion_check.py --f83` | Playwright, scipy, numpy | своя блокировка | **взять одну копию**; ключ `no_preference` есть в обеих версиях (grep), версия ai-media добавляет `_ancestor_holds_lock` |
| `ui_audit.py` (1 474), `color.py` (176), `measure_ui.py` (1 214) | визуальный QA ui; расчёт цвета; замер computed styles | нужны `marketing_audit.py`, `refs_client.py` и Take «measured» (`02/03` §3.3) | Playwright | — | **взять одну копию на систему** (md5 одинаков в 4–5 базах) |
| `effects_probe.py` (1 185), `scroll_record.py` (295) | замер эффектного сайта; запись прокрутки | только перезамер жанра и порогов | Playwright, ffmpeg | блокировки | **не брать** в скилл (опционально — для перекалибровки) |
| `fetch.py`, `render_fetch.py`, `yt_dl.py`, `vtt2md.py`, `yt_transcript.py`, `yt_frames.py`, `transcribe_local.py`, `site_probe.py`, `asset_inventory.py` | сбор источников, ролики, транскрипты, чужие замеры | только для ресерча | — | Node и модель ASR — абсолютные пути | **не брать** |
| `check_links.py` (1 653; 7 разных версий в базах), `orch_check.py`, `extract_for_audit.py`, `ctx_watch.py`, `sources_collect.py` | обслуживание базы | только оркестратор | — | служебные пути | **не брать** (`check_links` — разве что для финальной уборки) |
| `experiments/I/01-schemas/spec_check.py` (823) | `blocks`, `plan`, `spec` (проверки TR-, MS-), `moments` (строки T7 для `brief.yaml` kimi), `motion-md` (`MOTION.md` пакета kimi), `values`, `levels`, самотест | сценарий 1, шаги 10–11 | venv с jsonschema ≥ 4.18 и pyyaml | `SITE = APP/site-research` → `04-blocks/blocks.yaml`, `10-playbooks-contracts/schemas/page-plan`, `site-map`; **числа уровней зашиты в код** (`PEAKS`, `ACCENTS_MAX`, `SIGNATURE_MAX`, `LOOPS_MAX`, `PROPS_L0`) | **взять с адаптацией**; `moments` и `motion-md` завязаны на пакет kimi |
| `experiments/A/01-…/ad_check.py` (218) | `art-direction`: схема, 8 подсхем паспорта ai-media, правила вне схемы (оси, тёплое ≤ 1, контраст ≥ 4,5 и др.) | сценарий 1, шаг 4 | venv-A | **`APP = "/home/mm/Документы/app-design"`**; читает ai-media `visual-dna.schema.json`, site `vocabulary.yaml`, v0-схему и `treatment.v0` | **взять с адаптацией** (перевести на v1 и `effects.yaml`) |
| `experiments/J/03-…/recipe_check.py` (127) | рецепты: схема, `block:`, роли и `page_type` по словарю site, `effect:`, `cliche:`, `EG-`, уровни, журнал 8 осей | новый рецепт, журнал вариативности | venv-J (или venv-A — `PLAN` «Как расширять») | site — по относительному пути | **взять** |
| `experiments/H/03-…/registry_check.py` (60), `G/00-…/validate_stack.py` (31) | реестр клише и ссылки `cliche:`; `stack.yaml` | правка каталогов | pyyaml | `validate_stack.py`: `ROOT = '/home/mm/…/creative-research/'`; `use_for` сверяется с `treatment.v0` | `registry_check` — **взять**; `validate_stack` — **взять с адаптацией** |
| `experiments/F/07-yaml/build_effects.py` + `entries.py` + `check_refs.py` | сборка и сверка `effects.yaml` | правка каталога эффектов | venv-F (схема) | читает `99-raw/experiments/F/*/summary.json` | **решение — вопрос 3** |
| `experiments/J/02-…/idle_probe.py` (59), `F/12-…/cls_sources.py` (31) | «рисует ли холст в покое»; атрибуция сдвигов CLS | доказательство ложного срабатывания (сценарий 3) | Playwright; внешний `flock` | блокировки | `idle_probe` — **взять**; `cls_sources` — по желанию |
| `experiments/A/02-…/c1_check.py` (293), `I/01-…/compat_check.py`, `I/03-…/build_ad_v1.py` | проверка раннего выпуска C1; совместимость v0/v1; сборка v1-схемы | история волн | venv | `c1_check`: абсолютный `APP`, v0-схемы и примеры site (пилот site их не переносит) | **не брать** (`build_ad_v1` — пока v1 не перенесён к владельцу) |

**Дубли по md5** (все `*/99-raw/tools/`):
- **Совпадают:**
  - `asset_inventory` = ai-media, site;
  - `color` = ai-media, kimi, site, ui;
  - `fetch` и `render_fetch` — во всех 9 базах;
  - `measure_ui` и `ui_audit` = kimi, site, ui;
  - `site_probe` = ai-media, blender, kimi, site, text;
  - `vtt2md` = ai-media, claude-design, kimi, site, text (у blender и ux — другие);
  - `yt_dl` = 6 баз; `yt_frames` = kimi;
  - `yt_transcript` = 7 баз (у ui и ux — другие);
  - `transcribe_local` = blender, site, text (у ux — другой);
  - `page_accept` = site (у ai-media — другой, 377 строк).
- **Везде разные:** `check_links` (7 баз), `ctx_watch` (4), `orch_check` (3), `extract_for_audit` (3), `sources_collect` (6).
- **Только у creative:** `effect_bench`, `effects_probe`, `marketing_audit`, `motion_check`, `refs_client`, `scroll_record`.

## 5. Связи с соседними базами — в обе стороны

**creative → соседи (на что опирается)**

| сосед | на что | где в creative |
|---|---|---|
| site | `site-brief:1` (`ambition`, `brand`, `references[]`, `decision_context`); `page-plan:1` с `treatment:1`; `blocks.yaml` 1.0 (84 блока — зеркало в `block-treatments.yaml`); `vocabulary.yaml` (`page_type`, `section_role` — 42, макроструктуры — 30); `page-gates.yaml` v1.3 (выше наших ворот); `budgets.yaml` (слой «страница»); примеры «Отвес», «Окошко», «Сталькон» | `01/01` §1.3, `01/02` §4.4, `09/01`, `09/examples/*.treatment.yaml`, `spec_check.py`, `recipe_check.py`, `ad_check.py` |
| text | `copy-deck` v1, `copy-slots.yaml` (длины H1), примеры `meaning` и `facts` (входы концепции), порог капс-надзаголовков COPY-C-18 | `01/01` §1.3 и [S18], рецепты 01–03 и их YAML, `09/01` [S18] |
| ui | `ui_audit.py` (основа профиля `marketing`); 02-typography, 08-motion (умолчание L0), 11-styles-trends/01–04 (кластеры, плитки стиля), 13-evaluation (Tuch, Reinecke), 09-design-tokens/04 (схема DTCG `org.ui-research.llm`) | `04/*`, `05/01` П1–П5, `08/*`, `09/03` §4, `marketing-tokens.json` |
| ux | 06/03 (нормы движения → умолчание L0), 03/03 §9.2 (UX-LAY-13 → бюджет внимания), 08-accessibility, 09-mobile §4.1 (svh), 01/01 §11 | `05/01` П6–П7, `01/03` §8 |
| ai-media | `visual-dna.schema.json` (`art-direction` его питает, `ad_check.py` проверяет 8 подсхем); 01/01 §8 (план ассетов); маркеры IMG-M и VID-M (01/03 §5); `page_accept.py` (F83); 10/* (доставка медиа, текст поверх медиа); 11/02 (судья) | `01/02` §4.1, `08/01` §4, `06/02`, `09/04` |
| blender | 01/01 (70 эффектов), 01/02 (бюджеты), 04/04 (текст важнее картинки), 09/03–05 (прокрутка, reduce, ворота 3D), 12 (рецепты), 14-code-3d (голо-шейдер) | `06/01`, `01/02` §4.2, `02/03` §5.3, `10/03` |
| kimi | 03/04 шаблоны T0–T16 (T2a — оси, T3a–c — референсы, T7 — движение, T10 — видео); 07-brief-handoff (`brief.yaml`, `DESIGN.md`, шаблон `refs-README.md`, `build_package.py`); 05/03 (почерк K3); 04/01 (скиллы Hallmark, impeccable, taste, higgsfield); `k3_checks.py` `ALLOW_KEYS`; клоны внешних скиллов в `kimi-research/99-raw/cache/repos/` | `01/01`, `01/02` §4.3, `02/03`, `08/*`, `09/01` §6, `09/02` §4–6; 142 ссылки to-kimi |
| claude-design | дайджест `91-videos/digests/6XNhZu6mJlE.md`, кэш тарифов Rive (дополнение 25.09) | `06/01` §1.6, `07/01` §6.4 и §9, `08/01` §1.3, X-67 |

**соседи → creative** (входящих 136 по срезу; разбор — `links.tsv`)

| сосед | что | цели |
|---|---|---|
| site (81) | **код:** `site_validate.py` читает `ambition-levels.yaml` (стр. 78) и `treatment.schema.json` (стр. 81); `make_schemas.py` — `ambition-levels.yaml`, `stack.yaml`, `treatment`; `build_profile.py` — токены и уровни; `gen_glossary.py` — `effects.yaml`, `block-treatments.yaml`. **Схема:** `page-plan.schema.json` v1 → `urn:…:treatment:1` (стр. 818, 965). **Текст:** `ambition-levels.yaml` (21 ссылка), `04/03` (13), `05/01` (7), `PLAN.md` (6), `drafts-for-site` (3), `05/02` (3), `07/01` (3) | к служебному: `99-raw/experiments/E/01`, `E/02` (9, из `site-checklist.yaml` и 09/02); `A/02-c1-check/treatments.yaml` (пример «Отвес», `plans/home.yaml`:24) |
| blender (39) | `15-showcase` строит варианты на наших примерах: `sdano/b-blender`, `c-hybrid` (их motion-spec ссылаются на `spec_check.py` и `motion_check.py`), `zveno/*`, `KIT.md` (шрифты `_shared/fonts`, `J/04-light-pass/src/scene.js`, `pairs-desk.jpg`); `14-code-3d/01–04, 07` опираются на `J/02`, `J/04` (сцена, README) и `motion_check.py`; `11-evaluation-qa/06` — рубрика и лист замера illoca | 11 ссылок to-excluded (опыты J, C); плюс `ambition-levels`, `marketing-tokens.json`, `effects.yaml`, `block-treatments`, `recipes`, `cliche-registry`, рубрика, рецепт 03 |
| claude-design (7) | корень базы (4), `07/01` (2), `08/01` (1) | — |
| text (6) | корень базы (4), `PLAN.md` (2); плюс раздел creative в handoff text (crv-01…11) | — |
| ux (3) | `08/01` (2), `05-motion` (1) | — |

## 6. Ссылки: что сломается при переносе

Статусы ссылок по срезу: ok — 2 239; в исключаемое — 614 (ассеты 242, из них 227 — из кода лаборатории и примеров; служебное
367); to-kimi — 142; missing — 488; outside — 1; short-unresolved — 90. Ещё: адресов `NN/MM` — 1 349, указателей `→ §` — 751,
меток `[V:…]` — 142.

**Критично — содержимое или код теряют смысл:**
1. **URN схем.** `$id` и `$ref` вида `urn:app-design:creative-research:{art-direction:0/1, treatment:0/1, motion-spec:1,
   refs-library:1, recipe:0}`. На `treatment:1` ссылается `page-plan.schema.json` site. При переименовании баз URN менять синхронно.
2. **Код, который читает соседей.**
   - `spec_check.py`: site `04-blocks/blocks.yaml`, `10-playbooks-contracts/schemas/page-plan|site-map.schema.json`.
   - `recipe_check.py`: site `blocks.yaml`, `vocabulary.yaml`.
   - `ad_check.py`: ai-media `visual-dna.schema.json`, site `vocabulary.yaml`.
   - `c1_check.py`: v0-схемы и примеры site, text 02.
   - Обратно site `site_validate.py` читает creative `ambition-levels.yaml` и `treatment.schema.json`.
3. **Абсолютные пути:**
   - блокировки `/home/mm/Документы/app-design/.locks/browser.lock` и `browser-refs.lock` (4 утилиты);
   - Brave `/opt/brave.com/brave/brave`;
   - `ROOT = '/home/mm/Документы/app-design/creative-research/'` (`validate_stack.py`);
   - `APP = "/home/mm/Документы/app-design"` (`ad_check.py`, `c1_check.py`);
   - Node — `/home/mm/.nvm/…` (`PLAN.md` «Как расширять», утилиты YouTube);
   - skills-map предлагает абсолютный `CR=`.
4. **Раскладка папок.** `ROOT = ../..` от `99-raw/tools` у всех утилит: пути к `04-…`, `09-…`, `01-…`, `06-…/lab`, `99-raw/cache/refs`.
   Утилиты не работают, если переставить тематические папки или отделить `tools` от них.
5. **Ассеты примеров и лаборатории** — 227 ссылок кода (шрифты, картинки, видео, `_vendor`).

**Косметика:**
- 306 ссылок из md в служебное: отчёты, заметки, опыты `[проверено: F/04]`;
- 142 метки `[V:id mm:ss]` на дайджесты `91-videos`;
- 488 missing — в основном пути соседей в «Источниках», записанные без `../<база>/` (например, `01/01`:517 →
  `01-foundations/site-brief.schema.json`);
- 90 short-unresolved;
- 751 указатель `→ §` зависит от нумерации разделов.
- 142 ссылки to-kimi — это ссылки-доказательства вида `[данные: kimi 05/03]` и шаблоны T0–T16. В шаблоне kimi-research не будет:
  числа останутся без цели.

## 7. «Внешнее» и Kimi

**Какое «внешнее» есть в содержимом:**
- шапки с агентами, волнами и датами («Волна 1 · агент A · 2026-09-24»);
- метки опытов `[проверено: A/01]`;
- 142 метки `[V:…]`;
- `[S#]` с путями кэша;
- «решение заказчика N» в двух нумерациях;
- продолжатели (A2, B2, F2, K2, J2, X2, S1b, S2b);
- «живая фаза № N»;
- снимки версий браузеров и библиотек;
- 451 строка с путями служебных папок.

Объём уборки — большой: шапка и «Источники» есть у каждого файла, плюс README, PLAN и CONTRADICTIONS (вывод).

**Счёт Kimi.**
- Срез: 806 строк в 75 файлах. Мой пересчёт по основному содержимому (README, PLAN, CONTRADICTIONS, md 01–10, YAML, JSON, рецепты):
  735 строк с `kimi` или `K3`.
  - Только путь к клонам в кэше kimi — 13 строк.
  - «K3» — 343 строки, «kimi» — 469.
  - Про пакет и проверки исполнителя (T7s, `MOTION.md`, `k3_allow`, `--allow`, `video_in`, `refs/README`, `DESIGN.md`,
    `build_package`, `k3_checks`) — 231 строка.
- В creative счёт почти не завышен: продолжатели здесь называются K2, J2 и т. п., а «K3» всюду означает исполнителя Kimi.

**Где Kimi вплетён в суть (а не упомянут):**
1. **Адресат базы.**
   - README, стр. 20: «Claude как арт-директор, K3 как исполнитель».
   - Конвейер `PLAN.md` 200–202: «kimi: пакет задачи … K3 или Claude: сборка».
   - Живая фаза № 5–9 — целиком про K3.
2. **Формат пакета исполнителя.**
   - `09/01` §6: `DESIGN.md`, `MOTION.md`, `TASK.md`, `ACCEPTANCE.md`, `refs/`.
   - `spec_check.py moments` — строки T7 для `brief.yaml decisions.motion.moments`; `motion-md` — новый файл пакета kimi.
   - `09/02` §6.4 — текст промта T7s («K3 · Kimi Code 2.0.2»).
   - `09/02` §4 — видео-референс только для `k3` с провайдером kimi (`video_in`).
   - `refs_client.py handoff` — `refs/` по шаблону kimi 07/03 (≤ 2000 px, ≤ 262 144 байт).
3. **Шкала движения kimi** `none / subtle / expressive / cinematic`.
   - Стала полем `motion_level` в `treatment` v1 и `motion_system.level` в `art-direction`.
   - `maps_to.kimi` в `ambition-levels.yaml`.
   - Схема требует для `cinematic` ролик или 3D.
4. **Ключи `k3_allow`:**
   - у 20 записей реестра клише (плюс `compat.k3_checks`);
   - `decisions[].k3_allow` и `exclusions.k3_allow` в `art-direction`;
   - `recipe.schema.json`;
   - флаг `--allow` утилиты kimi `k3_checks.py`.
5. **Проекции:** `handoff.kimi` в `art-direction` (`01/02` §4.3), `x-kimi-projection` в схемах `treatment`, `kimi_crosswalk` в
   `drafts-for-site`.
6. **«Почерк K3»** — `08/02` §4.1 (данные kimi 05/03: капс-хром 14 из 15, анимация раскладки 13 из 13), правило README №39,
   кластер «редакционный люкс». Блок «чего не ставить» (`08/01` §6.2) — английский промт для «K3 · Kimi Code 2.0.2».
7. **Оси направлений** (бумага, display, тон акцента, макроструктура) взяты из kimi T2a и 07/01 §2.4. Сами оси от исполнителя
   не зависят.
8. **Стек** — `07/01` §11 «Пакет kimi и дисциплина версий».

**Что уже переписано под Claude Design: ничего из этого.**
- Добавления 25.09 — `06/01` §1.6, `07/01` §6.4 (+ 3 строки §9, [S32]–[S34]), оговорка после `08/01` §1.3 и [S27], X-67 с §И,
  пересборка `90-sources/` (274 источника). Их внёс агент E claude-design-research по решению заказчика «записать в Юксе и в
  креативе» (`PLAN.md`:789).
- Содержание: киты компонентов для **Claude Code** — Kokonut UI, React Bits, Magic UI и Magic UI MCP, anime.js, Rive. Эффекты
  разложены по `effect:` и `cliche:`, стек и лицензии китов описаны; позиция базы не изменилась (кит — референс, ≥ 2 параметра меняются).
- Счёт в README и «Итоге» не обновлён: там 66 противоречий и 271 источник.
- Claude Design как продукт в содержимом creative не описан. grep «claude design» находит только имя папки
  claude-design-research и заголовок отвергнутого ролика в `91-videos/catalog.md`.
- Нейтральное к исполнителю уже есть:
  - в README — «K3 или Claude»;
  - `02/03` §5.1 и `09/02` §4.2: для Claude Code — лист 3×3 + кадры + таймлайн;
  - T7s проверен только на исполнителе-Claude (опыт I/02).

## 8. Противоречия с решениями заказчика

1. **«Ориентир — Claude Design, Kimi в шаблоне не упоминается»** против формата передачи под Kimi.
   - В чём: поля схем `k3_allow`, `handoff.kimi`, `x-kimi-projection`, `maps_to.kimi`; пакет `DESIGN.md` / `MOTION.md` / T7s;
     видео-референсы только `k3`; `refs/` в формате kimi; проекции `spec_check.py moments` и `motion-md` (§7, п. 1–8).
   - Скилл kimi `kimi-design-director` назван получателем выхода (skills-map, «Выход к kimi»).
2. **«Все агенты — только Claude Opus 5.5»** против рубрики.
   - Рубрика требует «слепого судью другого вендора» (`09/04` выжимка 23; README «Что не покрыто»).
   - `effectiveness.rubric.json` `vlm_judge.models`: «кросс-вендорный контроль — как у ai-media 11/02 §5»; калибровка — голоса
     заказчика и ≥ 2 дизайнеров.
3. **«Один скилл `design-deep-dive` в шаблоне»** против карты авторов: 5 скиллов, база остаётся на месте и вызывается по
   абсолютному пути `CR=/home/mm/…/creative-research` (`skills-map.md`, «Принципы» п. 1).
4. **«Ассеты не переносим»** против эталонов.
   - Примеры L0 / L1 / L2 не работают без шрифтов OFL (≈ 0,5 МБ), своих рендеров L2 (≈ 0,1 МБ) и бандла `three-scene.js`
     (0,59 МБ).
   - Лаборатория не работает без `_vendor` (GSAP, Lenis) и `_assets`.
5. **«Служебные папки не переносим, кроме `99-raw/tools`»** против того, что в `99-raw/experiments` лежат:
   - валидаторы, которые вызывают сценарии README (`spec_check`, `ad_check`, `recipe_check`, `registry_check`, `validate_stack`,
     `idle_probe`);
   - генераторы `effects.yaml` и глоссария;
   - исходник сцены L2.
   - Нормы, на которые ссылается содержимое, лежат в `99-raw/prompts/_common.md` и `99-raw/reports/wave4-X-audit.md`.
6. **Клиент референсов** работает только со входом заказчика в его аккаунты и с риском по условиям площадок (Dribbble 7.1, 7.2,
   7.11; Dprofile 11.3), который заказчик принял для внутренней работы 24.09. Для шаблона, который получат другие пользователи,
   решения нет (вывод; вопрос 1).

## 9. Неожиданное

1. **Валидаторы отстают от формата.**
   - `validate_stack.py` сверяет `use_for` стека, а `ad_check.py` — эффекты `art-direction` с 29 временными id
     `treatment.v0.x-effect-ids-v0`, а не с 56 записями `effects.yaml` v0.3.
   - `ad_check.py` проверяет схему v0, хотя README объявляет v1.
   - `spec_check.py` держит числа уровней (пики, акценты, петли, свойства L0) у себя в коде, а не берёт из `ambition-levels.yaml`.
   - Это нарушает собственное правило базы «одна норма — одно место» (вывод по коду).
2. **Эталоны не самодостаточны** (§1.6). На них же опираются витрина blender `15-showcase` и файлы `14-code-3d` (через
   `J/04-light-pass/src/scene.js`).
3. **Две нумерации «решений заказчика»:** `PLAN.md` п. 1–24 и `_common.md` п. 1–6. Ссылки «решение заказчика 2/3/4/6» молча
   сломаются, если `_common.md` не перенести.
4. **Устаревшие места.**
   - README считает 66 противоречий и 271 источник, а в файлах уже X-67 и 274.
   - Дайджест `_skill-build/digests/creative-research.md` пишет, что глоссарий, skills-map и handoff отсутствуют.
   - `02/03`:138 оставляет Dprofile в `hold`.
5. **Реестр клише — список насыщенных приёмов.** 0 записей `fresh`, 40 `saturated`, 13 `dated`. `review_by` 2027-03-24 — через
   6 месяцев список нужно пересматривать.
6. **Два источника правды о площадках:** `sources.yaml` (поле `client.mode`, код его не читает) и `refs_client.py` (`DEFAULT_MODES`,
   `TERMS`, адаптеры) плюс `~/.config/creative-refs/modes.json`.
7. **Хрупкость клиента.** Brave и Playwright должны совпадать по мажорной версии Chromium (153). Сессия Dribbble живёт до
   2026-10-08, дальше нужен повторный вход заказчика. У Are.na аккаунта нет — `push` работает только в режиме плана.
8. **Судья в опыте K/03 — сам агент (Opus 5.5)** и не слепой: самосогласованность 100 %, потому что узнаёт сайты (`09/04` §9).
   Все оценки «craft 3 → 4» у L2 — `[мнение, один судья]`.
9. **Ворота 0/0/0 у примеров получены при известных ложных срабатываниях** `motion_check` 0.1.3: 9 FAIL сверки станций у L1
   «Сверка» и N/A по EG-A11Y-25 у L2 (X-66, открыто, утилиту не правили).
10. **Мелочи:**
    - `effects.schema.json` имеет `$id` `https://creative-research.local/…`, а не URN, как остальные схемы;
    - `marketing-tokens.css` ссылается на отсутствующий `noise.svg`;
    - файл `07/01` после дополнения 25.09 — 526 строк (норма базы — ≤ 500).
11. **Замер жанра опирается на скриншоты чужих сайтов** (`recordings/`, 86 JPG; `03/01`). Лицензии не оговорены; правило
    заказчика разрешает их только для внутренней работы.

## 10. Кандидаты в калибровочный набор

Только свои визуальные результаты базы. Листы с кадрами Unseen, Illoca, hubtown (`J/04-light-pass/compare-anchors.jpg`,
`pairs-desk.jpg`, `pairs-mob.jpg`), контактные листы `03-…/recordings/` и превью `library-example/` — чужие сайты, их не предлагаю.

| путь | размер | что иллюстрирует | есть ли оценка |
|---|---|---|---|
| `10-recipes/examples/l2-zveno/img/hero-d.webp` | 17 КБ | L2: постер-LCP своего рендера (сцена v2) | ворота 0/0/0; craft 4 — «уверенный предметный рендер» (J2, один судья) |
| `10-recipes/examples/l2-zveno/img/hero-m.webp` | 14 КБ | L2, кадр для телефона | то же |
| `10-recipes/examples/l2-zveno/img/st-scan.webp` | 15 КБ | L2: станция для reduce и без WebGL | ворота 0/0/0 |
| `99-raw/experiments/J/04-light-pass/sheet-before.jpg` | 314 КБ | L2 v1 до светового прохода — уровень ниже | craft 3 (J2, `[мнение]`) |
| `99-raw/experiments/J/04-light-pass/sheet-after.jpg` | 330 КБ | L2 v2 после светового прохода | craft 4 |
| `99-raw/experiments/J/04-light-pass/gates-l2-before-mob/shot_mob.jpg` | 47 КБ | **брак**: H1 над белыми корпусами 3D на телефоне (v1) | EG-A11Y-27 в `gates.md` рядом: h1 1,0:1, лид 4,29:1 (S) |
| `99-raw/experiments/J/01-l0-sdano/shots/desk_first.jpg` | 110 КБ | L0: первый экран лидогенерации | ворота 0/0/0; `marketing_audit` S 7 → 3 → 0; J: «уровень аккуратной студии» (`[мнение]`) |
| `99-raw/experiments/J/01-l0-sdano/shots/mob_first.jpg` | 125 КБ | L0 на телефоне | то же |
| `99-raw/experiments/J/03-l1-sverka/shots/desk_first.jpg` | 63 КБ | L1: первый экран SaaS | ворота 0/0/0; `marketing_audit` 0 B, 0 S |
| `99-raw/experiments/J/03-l1-sverka/shots/desk_scroll_sheet.jpg` | 154 КБ | L1: кадры sticky-сцены по прокрутке | ворота 0/0/0 (с оговоркой X-66) |
| `99-raw/experiments/J/05-webkit/sheet-l1.jpg` | 167 КБ | **брак**: счётчик на `@property` в WebKit стоит на 0 | выявлено J2 |
| `99-raw/experiments/J/05-webkit/sheet-l1-counter-fix.jpg` | 150 КБ | исправление: счётчик стопкой цифр | J2 |
| `99-raw/experiments/F/14-holo-look/before-after-desk.jpg` | 236 КБ | перелив: «радуга ИИ» → материал (узкий блик со структурой) | оценка F2 глазами; на людях `[не проверено]` |
| `99-raw/experiments/J/02-l2-zveno/motion/station_desk_story-modules_s2.jpg` | 15 КБ | кадр станции сцены (как проверяют скраб) | сверка станций `motion_check` |

## 11. Вопросы к заказчику

1. **Клиент референсов в шаблоне.** Брать ли `refs_client.py` в режиме «поиск» (Dribbble, Dprofile с вашим аккаунтом; Behance
   `off`, FWA `hold`)? Или только «ассистент», галереи и ваши ссылки?
   - Открыты: Dribbble 7.7 (имена авторов), правило API о хранении, FWA II.4 (X-59, cz-01).
   - Где будет мудборд относительно этапа «направления» Claude Design?
2. **Минимальный набор ассетов для эталонов.** Переносим ли шрифты OFL (≈ 0,5 МБ), свои рендеры L2 (≈ 0,1 МБ) и бандл
   `three-scene.js` (0,59 МБ)? Вместо бандла можно взять исходник `scene.js` со сборкой. Без этого примеры L0 / L1 / L2 не запускаются.
3. **Валидаторы и генераторы из `99-raw/experiments`.** Переносить ли с адаптацией `spec_check`, `ad_check`, `recipe_check`,
   `registry_check`, `validate_stack` и сборщик `effects.yaml` с данными замеров? Или объявить `effects.yaml` исходником и
   проверять только схемой?
4. **Судья рубрики.** Рубрика требует слепого судью другого вендора. При правиле «только Claude» — оставить VLM только фильтром и
   решать голосами заказчика?
5. **Лаборатория и замер жанра.** Нужны ли в шаблоне лаборатория (42 страницы, по базе не образец) и инструменты перезамера
   (`effects_probe`, `scroll_record`, `sites.csv`, записи чужих сайтов)? Или только числа как пороги?

## 12. Что не прочитано и почему

- **Тела тематических файлов за пределами сжатых слоёв**: `01/03` §1–6, `03/*` §1–13, `04/*` §1–6, `05/*` §1–10, `06/01` §2–13,
  `07/*`, `08/*` (кроме прочитанного), `09/03` §1–5, `09/04` §1–9, рецепты §1–10. Риск: правила TR-, MS-, EG-, MKT- в карте даны
  по выжимкам, без полного перечня.
- **Тела YAML и JSON** — смотрел только структуру, счёт и версии.
- **`PLAN.md`**: 1–70 (зачем, риски), 235–540 (стартовые позиции, структура, формат, метки, окружение, волны, трек V, правила).
  Раздел «Метки» (390–413) я не читал, хотя это норма.
- **`CONTRADICTIONS.md`** §А–Е (90–454): тексты позиций по пунктам.
- **`99-raw`**: контракт тройки (копия site), отчёты волн, кроме X-audit §2 и §9; заметки; README опытов; промты, кроме
  `_common.md` 38–57; кэш.
- **Код**: тела утилит — кроме констант и нужных веток. Самотесты не запускал: по брифу утилиты с браузером и записью файлов не запускаются.
- **claude-design-research** — только строки про этап «направления».
- **Глоссарий** — кроме выжимки, §0 и §3.

Риск для выводов — низкий для карты и решений о переносе. Средний — для полноты списка правил в файлах и для точного
соответствия полей site-brief v1 черновику C1.
