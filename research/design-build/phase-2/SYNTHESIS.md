# Синтез фазы 2: итог изучения базы

26.09.2026 · синтезатор фазы 2 · Claude Opus 5.5 · только чтение, записан один этот файл. Назначение — страница, на которой
заказчик решает следующие фазы, workflow и скилл. Workflow и скилл здесь не проектируются: только сведение и в конце — предложение
порядка шагов для обсуждения.

**Сокращения.** Пути — от `_skill-build/`; внутри баз — от корня базы, `NN/MM` — файл MM папки NN. `Р42` — строка 42 `DECISIONS.md`
(так на решения ссылаются все выжимки). `CHAIN 5` — запись 5 `phase-2/CHAIN.md`. `light/<база>` — `phase-2/light/<база>-research.md`;
у site разделы «Добора до версии 4» — `Д.1…Д.12`, у text — `Д0…Д6` и «Поправки». `ux-верх`, `ux-низ` — `phase-2/ux/…`. `kimi→cd` —
`phase-2/kimi-to-claude-design.md`; `mapping` — `phase-2/kimi-mapping.md`; `ревью` — `phase-2/review/site-pilot-review.md`. `Ф1-05` —
`phase-1/05-gaps-and-insertion.md`. `06/NN` — `claude-design-research/06-design-process/NN-….md`. `cd` — claude-design-research;
ДС — дизайн-система. Свои выводы синтезатора — «(вывод)»; расчёты по инвентарю — «(оценка синтезатора)».

## 0. Как собрано

**Прочитано целиком** (Read, без обрезки строк):
- `DECISIONS.md` (76 решений, строки 5–80), `STATE.md`, `PLAN.md`, `WORKFLOW-INPUTS.md`, `phase-2/CHAIN.md` (записи 1–12),
  `phase-2/inventory/SUMMARY.md`, `phase-1/00-summary.md`;
- все 7 лёгких выжимок, у site и text — вместе с «Добором до версии 4»: site 736 строк, text 1 049, creative 803, ui 844, ux 634,
  ai-media 996, blender 827;
- `ux-верх.md` (438) и `ux-низ.md` (693);
- `kimi→cd` (454), `mapping` (137), `ревью` (269), `claude-design-research/06-design-process/README.md` (33) и листинг папки;
- `Ф1-05`: «Коротко», §1 (А–Г), §3, §4.1–4.7, §7.

**Сверх чтения — агрегаты для манифеста (§3).** Суммы `bytes` и `tokens_est` из `phase-2/inventory/files.tsv` по группам файлов, которые
выжимки и решения исключают; размеры на диске для исключений из `99-raw` (в инвентаре служебные папки без токенов), в токены — по
средним «байт на токен» того же инвентаря (md 2,9; py 2,2; yaml 2,8; json 2,4). Это оценка синтезатора, так и помечена.

**Не прочитано:** файлы самих баз (кроме README `06-design-process`), тексты `06/01–07`, `phase-1/01–04`, `Ф1-05` §2, §5, §6, брифы
`BRIEF-*.md`, дайджесты `digests/*` (по выжимкам — устарели для creative, ux, ai-media, blender), срезы `inventory/<база>.md`.
На момент синтеза в cd **нет** `06-design-process/data/`, `99-raw/tools/shot_v3.py`, `lang_check.py`: докопирование перед удалением
kimi ещё идёт (STATE, листинг 26.09).

## 1. Итог фазы 2 на одной странице

1. **Базы едут только вместе.** Тройка site/text/creative связана кодом и схемами (URN-`$ref`, взаимные валидаторы); витрина blender
   стоит на примерах creative, ai-media — на DTCG-именах ui, линтер text — на словаре ux. [CHAIN 1, 4, 5, 9]
2. **Контракты заморозить:** id UX-*/AC-* (профили site 434 + 246), словарь ux 07/06 → лексикон text (159 правил), id и `ALLOW_KEYS`
   `mockup_checks.py`, неймспейс `org.ui-research.*`, API `ui_audit`. Менять только синхронно. [§2.2]
3. **Сжатый слой отстаёт от реестров** в ux, ui, site, text и уже протёк в YAML и профиль site (UX-A11-14). Реестр главнее, правка
   при уборке (Р48). [light/ux §1.3; light/ui §9]
4. **Kimi вшит в форматы** creative, text, site; под Claude Design не переписано ничего. Процесс макета теперь в `06-design-process`,
   стыки «тексты и бриф → макет» заменит единый вход холста и ДС (Р64). [kimi→cd §5]
5. **Стыков workflow в базе нет:** copy deck → Claude Design, page-plan ↔ copy deck (поля `site_*` пусты, роли секций 28 против
   40–42), мудборд → «направления». [light/text Д3.1; light/creative §1.7]
6. **Код держится на `99-raw`** пяти баз — исключения приняты (Р33, Р37, Р54, Р57, Р66); утилиты — по одной канонической копии;
   валидаторы creative отстают от схем v1. [§4; light/creative §9]
7. **Судья — Opus, и это риск:** калибровки судьи нет ни у одной базы; в опыте J/02 Opus выбрал «богаче» в 3 парах из 4 — все брак.
   Решает человек; пороги почти везде не откалиброваны. [light/blender §9; light/ai-media §1.6]
8. **Токены:** тип Design хочет литералы, базы — `var(--…)`; `tokens.json` ДС без движения, плотности и `rules`. Источник — DTCG ui,
   выпуск в ДС в одну сторону (Р42, Р63, предварительно). [light/ui §1.3]
9. **UX слоя проекта:** capability в базе нет — предложены реестр с паспортом и 13 проверок; vision — 12 разделов; цепочка обрывается
   на экранах; 191 из 434 пунктов чек-листа проверяемы скриптом по артефактам. [ux-верх §3; ux-низ §3.6]
10. **Сверка баз — до сборки** (Р67): ≈ 14 конфликтов норм site с соседями, WEB-01/WEB-04, термины, состояния, компоненты; каркасы
    готовы (site 09/02 §8, 07/03 §6). [light/site Д.6]
11. **Перенос:** по умолчанию 17,8 млн токенов, после решений ≈ 14,5–16 млн (оценка); ассеты — калибровка (50 кандидатов на ≈ 40 мест)
    и эталоны ≈ 2,2 МБ, бинарники — установкой. Уборка большая, с ловушками: «K3» в ui, клоны Hallmark под «kimi», «агент B §…». [§3; §10]
12. **Скоропорт и среда:** снимок ai-media устаревает с 30.09; среда тяжёлая (Chromium, ffmpeg, Blender, ≥ 3 ГБ ОЗУ); умолчания — рынок
    РФ; база ещё менялась — нужна заморозка. [light/ai-media §9; STATE]
13. **Ф3 (предложение):** заморозка и удаление kimi → решения-блокеры (craft, род продукта, слой страницы) → сверка → карта знаний →
    blueprint workflow и слоя проекта → структура скилла → перенос и пилоты. [§13]

## 2. Карта знаний всех баз

Материал для будущей карты `kb/` (принцип «синтез на лету», Р17–Р18): роль базы, ядро, связи. Число ссылок — из выжимок по `links.tsv`.

### 2.1. Базы

**site-research — логика сайта и лендинга до визуала** [light/site §1, Д.3–Д.5, Д.8]
- Роль: владелец брифа, карты сайта, плана страницы, блоков, конверсии, SEO/GEO, права и доступности маркетинговых страниц, ворот и
  приёмки страницы. Ворота страницы стоят выше ворот эффектов и ассетов (контракт тройки §6). Интернет-магазин — вне рамок.
- Процедуры: `10-playbooks-contracts/01-procedure-brief-to-pages.md` — 13 шагов «шаг → артефакт → проверка → DEF»; бриф
  `01-foundations/03-site-brief.md` (≤ 7 вопросов за раз с умолчаниями, `missing.blocking`); «бриф → план» — 12 подшагов `04/03` §5;
  плейбуки 9 посадочных и 7 многостраничников (`10/02`, `10/03`); проверка «план → ворота → маркеры и факты → эксперт → судья → люди»,
  «ноль находок — неудачная проверка», правка ≤ 7 пунктов в артефакт шага, где рождается дефект (DEF → `step:*`, `09/02` §4).
- Каталоги и схемы: `02-site-types/vocabulary.yaml` (443 id в 17 пространствах), `crosswalk.tsv` (710), `04-blocks/blocks.yaml`
  (84 блока), `05/lead-forms.yaml`, `07/page-gates.yaml` (63 ворот, v1.3), `07/budgets.yaml` (`<page_type>@L<n>`, черновик v0),
  `07/head-kit.yaml`, `07/crawlers.yaml`, `07/events.yaml`, `08/legal-requirements.yaml` (37), `09/ai-landing-markers.yaml` (52 AIL),
  `09/02-site-checklist.md` + `site-checklist.yaml` (248 SITE-*, DEF-01…50), `09/site-rubric.json` (8 осей), `09/ux-marketing-profile.tsv`
  (434), схемы v1 `10/schemas/{site-brief,site-map,page-plan,blocks}.schema.json`, эталоны `10/examples/` («Отвес», «Окошко», «Сталькон»).
- Код: `site_validate.py`, `page_gates.py`, `ab_plan.py`, `vocab_lint.py`, `checklist_export.py`, `plan_to_assets.py`; аудит живых
  страниц `page_anatomy.py`, `geo_probe.py`, `ia_probe.py` (§4).
- Связи: text (398 исходящих) — `$ref` на `facts:1`, `meaning:1`, самопроверка на фактах «Отвеса»; creative (81) — `treatment:1`,
  `ambition-levels.yaml` кодом; ux (273) — профили 434 UX-* и 246 AC-*; ai-media (281) — формат плана ассетов, `crosswalk.tsv`;
  blender (45) — WEB-* через `maps_to`. Входящие: creative 110, text 12, cd 2.

**text-research — смысл, факты и тексты** [light/text §1, §1.1, Д1–Д3]
- Роль: «факты раньше слов»; владелец `facts.yaml` и copy deck (контракт тройки §2); проверки текста — ворота честности и права;
  исполнимая копия словаря UX-текстов ux (Р31, Р49). Микрокопи интерфейса — вне рамок базы.
- Процедуры: конвейер S1–S11 (`09/02`), промты P1–P7 `[не проверено]`; процесс copy deck `draft → checked → approved` (`10/01`);
  аудит «claims → lint → validate → судья → человек → люди», ≤ 3 прохода правки (`09/03`, `06/02` §9); раскладка «тип страницы →
  жанр → секции → слоты» (`04/03` §5).
- Каталоги и схемы: `02-strategy-messaging/{facts,meaning,message-hierarchy,voc}.schema.yaml` (URN `urn:app-design:text-research:*:1`),
  `proof-intake.md`, `04-copy-by-block/copy-slots.yaml` (69 `slot_type`), `03-corpus-measured/thresholds.yaml`,
  `05-voice-editorial/voice.schema.yaml`, `06-anti-slop/lexicon/*` (336 правил, из них 159 — копия ux 07/06) и `profiles.yaml`
  (6 жанров), `07/{meta-rules,geo-rules,geo-checklist}.yaml`, `08/claims-rules.yaml` (66), `08/typography-rules.yaml` (27),
  `09/copy-rubric.yaml` (12), `09/copy-checklist.yaml` (32), `10/copy-deck.schema.json` v1.1, 8 эталонных deck, `before-after.tsv` (540),
  `CONTRADICTIONS.md`.
- Код: `copydeck.py`, `claims_check.py`, `copy_lint.py`, `ux_dict_to_yaml.py` + 7 скриптов опытов (§4).
- Связи: site — блоки `meaning`/`proof` брифа, слоты `page-plan` (стык пуст), словарь id (временный словарь text v0 держит код 4
  утилит); ux — канон словаря `07/06`, голос продукта `07/01`; creative — рецепты ссылаются на эталонные deck; ai-media — выгрузка
  плана ассетов, текст в картинке ≤ 40 знаков × ≤ 3 строки. Входящие: site 398, creative 32, cd 2, ux 0.

**creative-research — подача и движение** [light/creative §1]
- Роль: уровень амбиций L0–L2 страницы и секции (его читает код site), концепция и 3–5 направлений, референсы и мудборд, маркетинговый
  визуальный язык (display, композиция, цвет), движение и его доступность, каталог эффектов, стек, политика клише, `treatment` и
  `motion-spec`, ворота эффектов, рубрика эффектности, рецепты.
- Процедуры: `01/01` «бриф → концепция → территории → главный приём → направления → выбор»; мудборд `02/03` §1 (30–60 кандидатов →
  3–6 кластеров → направления → Take / Do not take); маршрут рецептов `10/00`; цикл проверки `09/03` (статичный визуал → движение и
  цена → F83 → ворота site → рубрика → человек).
- Каталоги и схемы: `01/ambition-levels.yaml` v0.2, `art-direction` v0 и v1, `09/treatment.schema.json` v1, `motion-spec.schema.json` v1,
  `block-treatments.yaml` (84 блока — зеркало site), `effect-gates.yaml` (62), `effectiveness.rubric.json`, `06/effects.yaml` (56),
  `08/cliche-registry.yaml` (53), `07/stack.yaml`, `04/marketing-tokens.json` (DTCG, неймспейс ui), `cyrillic-display-fonts.yaml` (37),
  `02/sources.yaml` (36 площадок), `refs-library.schema.json`, рецепты `10-recipes/recipes/*.recipe.yaml` (10; 01–03 `verified`),
  эталоны `10-recipes/examples/` L0 / L1 / L2, `CONTRADICTIONS.md`.
- Код: `marketing_audit.py` (импортирует `ui_audit`), `motion_check.py` (вызывает `page_accept`), `refs_client.py`, валидаторы из
  `99-raw/experiments` (§4).
- Связи: site (схема `page-plan` ссылается на `treatment:1`; валидаторы читают `blocks.yaml`, `vocabulary.yaml`); text (copy deck,
  `copy-slots.yaml`); ui (280 исходящих: маркеры 11/04 → умолчания L0, движение 08, `ui_audit`); ux (06/03 → умолчание L0); ai-media
  (`art-direction` → `visual-dna.schema.json`); blender (витрина на примерах creative); kimi (142 ссылки, формат пакета). Входящие:
  site 81, blender 39, cd 7, text 6, ux 3.

**ui-research — визуальная система интерфейсов** [light/ui §1]
- Роль: источник правды токенов (DTCG, Р42), визуальные спецификации ≈ 50 видов компонентов и матрица 14 состояний, пресеты A–D
  (живой — только A), стили и квиз, маркеры слопа UI, визуальный QA и рубрика. Лендинги и UX-логика — вне рамок.
- Процедуры: рецепты `14-recipes/01–11` (порядок 09 → 01 → 02 → 03 → 04 → 05 → 08 → 06 → 07 → 10); бриф и квиз `14/09`; выпуск
  токенов `14/08`; цикл проверки `14/10`; бриф на 4 уровнях и пакет инструкций `12/04`.
- Каталоги и схемы: `09/04` эталонная схема 289 токенов (`org.ui-research.llm`, `…modes`), `14/11` контракт пресетов, `06/07` матрица
  состояний, `13/01` 117 проверок, `13/02` рубрика 0–5 и промт критика, `11/04` 34 маркера (спор с `frontend-design`), `11/01` 18 стилей,
  `00-glossary` §14 (27 расхождений терминов), `CONTRADICTIONS.md` C1–C49, эталонные экраны `14/examples/*.html` + `app.css` + `tokens.css`.
- Код: `ui_audit.py` (81 проверка), `color.py`, `measure_ui.py`, `build_reference_tokens.py` — канонические копии.
- Связи: ux (38 строк исходящих; ux ждёт от ui формат блока «Дизайн-система» — ответа нет). Входящие 667: creative 280, ux 170,
  ai-media 128, blender 27, text 25, cd 19, site 18.

**ux-research — поведение и структура приложений** [light/ux §1; ux-верх; ux-низ]
- Роль: процедура «бриф → экраны» (30 шагов, 22 артефакта), модель объектов (OOUX, CTA/CRUD), сценарии, ИА и навигация, поведенческие
  контракты компонентов, контракт состояний S01–S22, тексты интерфейса (канон словаря запретов и 31 роль узла), WCAG 2.2, мобильный
  web, дефекты ИИ-генерации и контракт генерации экранов, оценка (434 UX-*, 246 AC-*).
- Процедуры: `13-app-types/04-master-procedure-brief-to-screens.md`; `01/03` «домен → экраны» (14 шагов); шаблон сценария `05/02` §1.4;
  экспертная оценка `12/01`; порядок генерации `11/04` §2.1.
- Каталоги и схемы: `12/02` + `master-checklist.yaml` (434), `12/03` AC-* (246, только спецификации), `06/01` §2 S01–S22, `11/01`
  F1.1–F13.4 (52), `11/04` §1 входной контракт (9 блоков), `07/06` словари и формат правила §7, `07/01` §12 длины (23 типа), `04/10`
  §1.1 контракт действия, `04/05` §1.1 контракт формы, `08/01` §12.4 цели нажатия, реестр № 1–61 (README), перечень канонов
  `99-raw/reports/wave4-X-audit.md` §2.1.
- Код: только `checklist_export.py`; исполняемых UX-проверок в базе нет.
- Связи: ui (170 исходящих: «числа — в ui»). Входящие 646: site 273, text 225, creative 61, ui 44, ai-media 17, blender 16, cd 10. Id
  UX-*/AC-* держит site, словарь исполняет text, S01–S22 — 0 ссылок из соседей.

**ai-media-research — картинки, видео, вектор** [light/ai-media §1]
- Роль: «слот → паспорт визуала → спецификация → маршрут → компиляция → задание → проверка → постобработка → провенанс → доставка»;
  лестница дешевизны «текст → SVG → CSS → картинка → видео → 3D»; право и провенанс; каналы только рублёвые (Р53).
- Процедуры: шпаргалка `14/00`, карта возможностей `14/04`, политика агента `12/04` (25 строк «сам / спрашиваю / не делаю», 10 ворот),
  освежение скоропорта `13/04`, протокол A/B `05/06`, метод стенда `13/01`.
- Каталоги и схемы: план ассетов `01/01` §8 (схемы и валидатора нет), `06-…/visual-dna.schema.json` v0.1,
  `05-prompting/asset-spec.schema.json` v0.2, `dialects.yaml` v0.4, `13-routing-matrix/routing.yaml` v2 (33 маршрута, 136 вариантов),
  `11/thresholds.yaml` (94), `11/rubrics/*.rubric.json` (12) + `judge-response.schema.json`, рецепты `14-recipes/recipes/*.yaml` (17),
  шаблоны доставки `10-web-integration/pages/`, эталон `14-recipes/examples/demo-landing/` (генераций в нём нет).
- Код: `polza.py`, `mp_client.py`, `routing_check.py`, `prompt_compile.py`, `vlm_to_dna.py`, `asset_audit.py`, проверки правок и петель,
  `provenance_check.py`, `page_accept.py`, `stand_run.py` (§4).
- Связи: ui (128 исходящих: паспорт иллюстраций 07/02 → паспорт визуала; `vlm_to_dna.py from-tokens` читает DTCG-имена ui); blender
  (28); ux (17). Входящие 466: site 281, creative 127 (`ad_check.py` → `visual-dna.schema.json` абсолютным путём), text 52, blender 4,
  cd 2. Сама база site, text, creative не упоминает (её рамка «соседей не знать»).

**blender-research — 3D для веба** [light/blender §1]
- Роль: нужен ли 3D и чем его делать (код / Blender / гибрид / предрендер / видео); конвейер «паспорт → `build(P)` → проверки →
  рендер → экспорт → `qa glb` → страница»; ворота 3D. Основной путь — `blender -b` (Р59); 3D-генераторы не используются (Р72).
- Процедуры: деревья выбора `01/02` §7, `12/00` §1, `14-code-3d/README`, `15-showcase/VERDICT.md` §2–3 (карта предложений по типам
  клиентов); протокол «бриф → ассет» `04/04`; работа без окна `04/06`; безопасность `04/07`; каркас рецепта `12/00` §2; попарная
  оценка «вау» `11/06`.
- Каталоги и схемы: бюджеты героя `01/02` §3.1, ворота `09/05` §7 (`LIMITS` в `gate_check.py`), мастер-чек-лист `11/05` (≈ 90 ID,
  §11 — нормализация), дрейф API `03/03` (105 изменений), контракт экспорта `08/01`, 7 пресетов экспорта (`99-raw/experiments/E/24-presets/`),
  контракт GLB гибрида `15-showcase/_shared/code3d/README.md`, реестры R1–R52 и T1–T26 (README), `13-tools-atlas/atlas.tsv`, рецепты
  01–17 и эталонные страницы (`09/examples/*`, `15-showcase/<предмет>/{a-code,b-blender,c-hybrid}`).
- Код: `blender_run.py`, `bpy_probe.py`, `qa_pipeline.py`, `scene_check.py`, `gate_check.py`, `site_probe.py`, `gltf_*`, `rk.py`, `bpyx.py`,
  `img_metrics.py`, `vote/*` (§4).
- Связи: creative (39 исходящих; витрина стоит на `l0-sdano`, `l2-zveno`, сцене `J/04`, шрифтах, рубрике, `motion_check.py` и
  `marketing_audit.py` по абсолютному пути); ui 08 (движение), ux 08, ai-media (эталон Velmora). Входящие 215: creative 136, site 45,
  ai-media 28, text 3–4, cd 3.

**claude-design-research — исполнение макета** [kimi→cd §6; `06-design-process/README.md`]
- Роль: макет в сессии Claude Code — артефакт Design System (`tokens.json`, бренд-бук, компоненты) и холст Design (страницы
  «Направления» → «Вайрфрейм» → «Макет и прототип»); исходники в репозитории, «прочитать → слить → опубликовать»; снимок версий и
  проверка дрейфа; `kit` — автопроверки на HTML-копиях и запасной путь; с 26.09 — процесс вокруг холста (`06-design-process`).
- Процедуры: `05-design-artifacts/01` (процесс страницами холста), `02-staying-current.md` (дрейф), `04-claude-code-native/01` (протокол
  `#N`, спецификация `studio`, тесты T-D1…T-D12), `06/01` бриф, `06/02` единый вход, `06/03` раунд правок и стоп, `06/04` проверки
  слоями, `06/05` бан-лист дефолтного вида, `06/06` стенд и правило решения, `06/07` задания по этапам.
- Каталоги и схемы: снимок `05/snapshots/2026-09-26-types.json`, пример «Спица» `05/example/{design-system,canvas}/project/`, README
  (правила 1–36), дом-стиль Claude `03-practice-pipelines/01` §4, брифы стенда `06-design-process/stand/S1-kvarts`, `S2-smena`.
- Код: `kit/` (`shot.py`, `diffshots.py`, `export.py`, `canvas.html`, `marks.js`), `99-raw/tools/mockup_checks.py` (бывший `k3_checks.py`),
  `99-raw/tools/stand_page.py` (§4).
- Связи: ui (DTCG → `tokens.json`; шаг ревью = `ui_audit` + 34 маркера + рубрика 13/02); creative (направления, референсы, motion-spec);
  site (`page-plan` → холст, акты I–L); text (copy deck → вход холста — не спроектировано); ai-media (`stand_run.py` — канон слепых
  пар); ux (`11/03` §2.5 — снимок Claude Design на 17.04.2026, контракт генерации `11/04`). Входящие 13 (creative 7, ux 6), 11 из них
  ведут в непереносимое.

**kimi-research — донор, не переносится** (Р77). Ценное переписано в `06-design-process`, таблица замен ссылок — `mapping`; удаление в
корзину — по команде заказчика после просмотра `06` (Р68).

### 2.2. Узлы межбазовых связей (основа будущего смешивания норм)

| № | узел | что связывает (файлы) | канон | что делать |
|---|---|---|---|---|
| 1 | Контракт тройки | `site-research/99-raw/notes/triad-contract-2026-09-24.md` (копии в text и creative, md5 совпадает): §2 владельцы 32 тем, §3 16 форматов и префиксы SITE- / CRV- / COPY-, §4 метки, §6 15 сквозных выводов (иерархия ворот, «ничейные зоны») | site | переносить положениями §2–§6 (Р66); базы тройки — только вместе [CHAIN 1; light/site Д.6] |
| 2 | URN-`$ref` и код, читающий соседей | site `page-plan.schema.json` → creative `treatment:1`; `site-brief.schema.json` → text `facts:1`, `meaning:1`; `site_validate.py:78–81` читает creative `ambition-levels.yaml`, `treatment.schema.json`, text `facts`, `meaning`; creative `spec_check`, `recipe_check`, `ad_check`, `c1_check`, `compat_check` читают site `blocks.yaml`, `vocabulary.yaml`, схемы и примеры | владельцы форматов | общий конфиг путей; URN с именами баз менять синхронно; переименование полей ломает проверки обеих сторон [light/site §6 п.1, Д.10 п.4; light/creative §6] |
| 3 | Id UX-* / AC-* | ux `12/02` + `master-checklist.yaml` → site `09/ux-marketing-profile.tsv` (434) и `99-raw/experiments/K/02-ux-profile/ac-profile.tsv` (246), `build_profile.py`, `fp_check.py`; у text 12 и 14 ссылок, у creative 12 и 13 | ux | заморожены (Р49); перенумерация ломает site [light/ux §5, §9 п.3] |
| 4 | Словарь запретов UX-текстов | ux `07-ux-writing/06-banned-words-and-patterns.md` (31 роль, 14 анализаторов) → text `ux_dict_to_yaml.py` → `06-anti-slop/lexicon/ux-07-06.yaml` (159 правил, хеш `ee35b9a3e32a1fdd`) → `copy_lint.py` (роль — через `slot_type` временного словаря, достижимы 17 ролей из 31) | ux (Р49) | роль — напрямую, жанр «интерфейс» (Р31, Р70) [light/text §1.2, Д3.3] |
| 5 | Проверка макета `mockup_checks.py` | `ALLOW_KEYS` ↔ creative `k3_allow` (`cliche-registry.yaml`, `art-direction.schema.json`, `recipe.schema.json`); id K3-* / F-* ↔ site `ai-landing-markers.yaml` (`crosswalk_external`), `page-gates.yaml`; text `claims_check.py` выведен из него, `verify-page` — по его образцу | cd `99-raw/tools/` (Р62, Р68) | id переименовать синхронно (`LOOK-*`, `HON-*` — предложение `mapping` §5), ключи не менять [kimi→cd §1.15] |
| 6 | Токены | ui `09/04` DTCG (неймспейс `org.ui-research.llm`, `.modes`) ↔ creative `04-visual-language/marketing-tokens.json` (тот же неймспейс) ↔ ai-media `vlm_to_dna.py from-tokens` (DTCG-имена; нет имени — молча умолчания) ↔ ДС Claude Design `tokens.json` (`{name, value, usage}`, имя = CSS-переменная без `--`) ↔ `kit` и код (`var(--…)`) ↔ артборды Design (литералы) | ui (Р42) | выпуск в ДС в одну сторону; проверка на холсте — «литерал ∈ токены ДС» (Р63, предварительно) [light/ui §1.3; light/ai-media §9 п.10] |
| 7 | Общий код визуальных проверок | ui `ui_audit.py` (API импортирует creative `marketing_audit.py`), `color.py`; ai-media `page_accept.py` (его зовут creative `motion_check.py --f83` и site `page_gates --accept`); blender `site_probe.py` (→ `gate_check.py`) | ui; ai-media; blender | одна копия каждой; интерфейс модуля — контракт [light/ui §6; light/ai-media §4] |
| 8 | Паспорт визуала | ui `07-iconography-imagery/02` §3 → ai-media `06/01` + `visual-dna.schema.json` ← creative `art-direction` (`ad_check.py` проверяет 8 подсхем) | ai-media | схему не переименовывать без creative [light/ai-media §5] |
| 9 | План ассетов | ai-media `01/01` §8 ← site `plan_to_assets.py` (строки ai-media в `crosswalk.tsv`) ← text `copydeck.py export-assets` (alt, подписи, текст в картинке) | ai-media | у формата нет схемы и валидатора [light/ai-media §1.4] |
| 10 | Иерархия ворот | site `07/page-gates.yaml` (SG-*, выше всех) → creative `09/effect-gates.yaml` (EG-*) → ai-media `page_accept.py`, blender WEB-* (`maps_to` у 22 ворот site); расхождения — site `07/03` §6, `09/02` §8 | site | WEB-01, WEB-04 — на сверке (Р58, Р67) [light/site Д.6; light/blender §2] |
| 11 | Уровни L0–L2 | creative `ambition-levels.yaml` → site `budgets.yaml` `<page_type>@L<n>`, `page_gates --resolve` (решение site 20); blender KIT §5 (бюджеты JS); creative `spec_check.py` (числа уровней в коде) | creative | числа — только в YAML [light/creative §1.4, §9 п.1] |
| 12 | Словари страниц, секций, слотов | site `vocabulary.yaml` (`section_role` 42, слоты 119, `page_type` 46) ↔ text `99-raw/notes/temp-vocabulary-v0.yaml` (28 ролей секций, 63 `slot_type` с `ux_role`) ↔ `crosswalk.tsv` (строки text — по временному словарю) | site — словарь, text — `slot_type` | свести; `site_slot`, `site_id` пусты [light/text Д1; light/site Д.5, §6 п.9] |
| 13 | Состояния | ux S01–S22 экрана и 11 состояний элемента; ui 14 визуальных; слой проекта 6; mobile 9 и 5 | ux — экран, ui — визуальная дельта | свести (Р45; ux-низ §3.1) |
| 14 | Словарь компонентов | ux `04/*` (поведение) + ui `06/01–06`, `06/07`, грань «Слот» словаря `usage` `14/08` §4 (40 меток), классы `14/examples/app.css` | единый, строится в Ф3 (Р45) | screens называют — ДС создаёт (Р29) |
| 15 | Бриф | site `site-brief` (надмножество, у поля — владелец) ← блоки text `meaning`, `proof` ← поля creative; ui `14/09`; ux `13/04` §25 (бриф на визуальный слой); cd `06/01` | site (для сайта) | единый вход холста (Р64) |
| 16 | Направления | creative `01/01` (3–5, 4 оси, словами) ↔ cd `05/01` §5 (2–4 артборда, оси фон / акцент / гарнитура) ↔ `06/01` §5 | — | свести [light/creative §1.7] |
| 17 | Приметы «дефолтного вида» и клише | ui `11/04` (34) ↔ creative `cliche-registry.yaml` (53) ↔ site `ai-landing-markers.yaml` (52) ↔ text COPY-M (93) ↔ ai-media IMG-M / VID-M ↔ cd `06/05` ↔ blender `01/01` §22 | — | общий реестр (вывод) |
| 18 | Судья и рубрики | text `copy-rubric.yaml`, site `site-rubric.json`, creative `effectiveness.rubric.json`, ui `13/02`, ai-media `11/rubrics/*` и `11/02`, blender `11/06`, ux `12/01`, `12/03` §8.2 | — | один протокол Opus (Р27); пороги доверия — ai-media `thresholds.yaml`, группа `judge` |
| 19 | Витрина blender поверх creative | blender `15-showcase` ← creative `10-recipes/examples/l0-sdano`, `l2-zveno`, `99-raw/experiments/J/04-light-pass/src/scene.js`, `_shared/fonts`, `motion-spec` v1 | creative | переносить вместе [light/blender §5] |
| 20 | Реестры противоречий и «поправки к соседям» | §5.1 | каждая база | вход сверки (§9) |

## 3. Перенос — сводный манифест

Правило подсчёта: переносимое по срезу (`inventory/SUMMARY.md`) минус то, что выжимки и решения признали ненужным, плюс исключения из
`99-raw` и ассетов. Колонка «итого» — оценка синтезатора (§0).

### 3.1. По базам

| база | по умолчанию: файлов / МБ / токенов | не переносим сверх умолчания (главное) | исключения из `99-raw` | итого токенов (оценка) |
|---|---|---|---|---|
| site | 144 / 5,9 / 2,21 млн | ≈ 0,38 млн: копии и утилиты ресерча (≈ 0,19 — `ui_audit`, `measure_ui`, `color`, `asset_inventory`, `site_probe`, `page_accept`, `sources_collect`, `site_brief_to_kimi` и др.), схемы v0/v0.9 (63 тыс.), примеры v0 с аналогом v1 (44 тыс.), `site-brief.kimi-map.tsv` и `brief.kimi` ×3 (24 тыс.), `PLAN.md` (53 тыс.; нормы извлечь) | ≈ 0,10–0,16 млн: контракт тройки §2–§6, реестры отчёта X (§1.1, §1.3, §2), `ac-profile.tsv` + `build_profile.py`, `run_axe_targets.py`, разделы `99-raw/tools/README.md` (Р66) | ≈ 1,9–2,0 млн |
| text | 129 / 7,6 / 3,07 млн | ≈ 1,42 млн: `measurements.tsv` + `corpus.tsv` (1,22 млн, Р32), `PLAN.md` (45 тыс.), утилиты ресерча и копии (≈ 0,16) | ≈ 0,05–0,13 млн: `99-raw/notes/temp-vocabulary-v0.yaml`, 7 скриптов опытов (Р33), `J/08 run_checks.py`, разделы `tools/README.md`, отчёт X §6–§7 положениями (Р34) | ≈ 1,7–1,8 млн |
| creative | 352 / 5,1 / 2,03 млн | ≈ 0,63 млн: копии и утилиты ресерча (≈ 0,31), `06-effects-catalog/lab/` (0,16, Р39), `03-live-sites-measured/sites.csv` и записи (0,10, Р39; md 03/01–02 остаются), `PLAN.md` (51 тыс.), черновик `site-brief-creative-fields.yaml` (11 тыс., вывод выжимки) | ≈ 0,13 млн: 6 валидаторов (Р37), `tools/README.md`, `J/04/src/scene.js` (§12), `_common.md` «Решения заказчика» и отчёт X §2, §9 — положениями | ≈ 1,5–1,55 млн + ассеты 1,19 МБ (Р41) |
| ui | 135 / 6,0 / 2,19 млн | ≈ 0,32 млн: `14-recipes/examples/audit/` (0,29 — журнал прогона; решения нет, предложение выжимки), утилиты ресерча (32 тыс.); открыто: дубль `00-glossary` (0,11) и листинги `09/04` §4–§6 | — | ≈ 1,65–1,87 млн |
| ux | 85 / 6,8 / 1,99 млн | ≈ 0,05 млн: утилиты ресерча (33 тыс.), журнал `PLAN.md` (нормы обслуживания — в приложение, Р50) | ≈ 0,01 млн: отчёт X §2.1 (54 строки, Р50) | ≈ 1,9–1,95 млн |
| ai-media | 267 / 6,9 / 2,73 млн | ≈ 0,41 млн: 63 YAML-карточки моделей (0,16, Р54), `routing.v0/v1` (41 тыс., Р54), журналы `demo-landing/measure/*.json` (0,10), журнал `PLAN.md` (≈ 40 тыс.), `ab_analyze.py` и копии (≈ 70 тыс.) | ≈ 0,09 млн: ≈ 15 модулей и шагов (`A/04`, `F/02`, `F/04`, `F/05`, `F/06`, `G/check_icons.py` + `lucide-ref`, прайс `P/04`, `loop_rife_bridge`, `svg_sheet`, `vm_sheet`, `split_recraft`, `layout_check`, `channel_diff`, `validate_recipes`) и `99-raw/phase5/README.md` (Р54); ещё 0,36 млн — если брать `P/04/routerai_models.json` (840 КБ, запасной каталог; §12) | ≈ 2,4 млн (2,8 — с каталогом) |
| blender | 420 / 8,1 / 3,25 млн | ≈ 0,55 млн: журналы витрины (`rules-journal` 0,10, данные страниц `keyboard/*/assets/data` 0,15, `vote/ai-screen`, сгенерированные `index`/`verdict`, дайджесты 01/03), замеры `probe/` (41 тыс.), журнал `PLAN.md`, старые версии и утилиты ресерча (`asr_*`, `ctx_watch_v1`, `slot_run_v1/v21` и др., ≈ 0,1) | ≈ 0,12 млн библиотек (`d1lib`, `d2lib`, `presets`, `scene_audit`, `passport_asserts`, `preflight_block`, `glb_lint_block`, `serve_br`, `animx`, `run_recipes`) + исходники рецептов 13–17 из дорожек `Z`, `CD`, `KB`, `SD`, `VD` (Р57): по выжимке ≈ 2–3 МБ кода, ≈ 0,3–1,0 млн токенов в зависимости от выборки (§12) | ≈ 3,1–3,8 млн + ассеты ≈ 1 МБ (Р57) |
| cd | 53 / 0,8 / 0,31 млн | утилиты ресерча (20 тыс.), `PLAN.md` (12 тыс., серая зона); `99-raw/cache/` — запрещено | новое 26.09: `06-design-process/` (0,32 МБ, ≈ 0,11 млн), `99-raw/tools/mockup_checks.py` и `stand_page.py` (≈ 0,06 млн) (Р62, Р68) | ≈ 0,45 млн |
| kimi | 129 / 3,4 / 1,36 млн | всё (Р77) | — | 0 |

### 3.2. Исключения из «99-raw не переносим»

**Приняты решениями:**
- text (Р33): `99-raw/notes/temp-vocabulary-v0.yaml` (его читают 4 утилиты); 7 скриптов опытов — `I/04-chain-manual/{check_intake,
  chain_inputs,make_skeleton,validate_any}.py`, `B1/03-schema-validate/validate.py`, `B2/01-schema-validate/validate.py`,
  `F/03-schema-lint/validate_voice.py`. Сборку `copy-slots.yaml`, `thresholds.yaml`, `before-after.tsv` из `99-raw` не переносим — файлы
  в шаблоне сами источник правды. Калибровка К1–К31 (отчёт X §7) — при адаптации (Р34).
- creative (Р37): валидаторы `I/01-schemas/spec_check.py`, `A/01-…/ad_check.py`, `J/03-…/recipe_check.py`, `H/03-…/registry_check.py`,
  `G/00-…/validate_stack.py`, `J/02-…/idle_probe.py` («и др.»). Генератор `effects.yaml` не переносим — `effects.yaml` сам источник правды.
- ux (Р50): таблица канонов `99-raw/reports/wave4-X-audit.md` §2.1 — как норма.
- ai-media (Р54): ≈ 15 скриптов опытов, которые импортирует автоприёмка, и формат заданий генерации (`99-raw/phase5/README.md`);
  `routing_check.py` адаптировать, чтобы работал без заданий фазы 5.
- blender (Р57): ≈ 12 библиотек опытов (без них не работают `rk.py` и `qa_pipeline.py`) и исходники рецептов 13–17 из дорожек
  `15-showcase`; регрессионный набор — протокол, без данных (Р58).
- site (Р66): контракт тройки, реестры отчёта аудита X, `ac-profile.tsv` с генератором, `run_axe_targets.py`, нужные разделы
  `tools/README.md`.
- cd (Р62, Р68): `mockup_checks.py`, `stand_page.py` лежат в `cd/99-raw/tools/` (утилиты едут по умолчанию); брифы стенда — в
  `06-design-process/stand/`.

**Предложены выжимками, решения нет** (кандидаты в §12):
- blender: отчёт X §4 (канонические места чисел, 22 темы) и §1 (полный реестр R) — на них ссылается README [light/blender §2, §3.2];
  HDRI `E/_assets/studio_small_09_1k.hdr` (CC0, умолчание `gltf_diff.py`); генераторы карты и глоссария `99-raw/notes/wave4/S2/`.
- text: отчёт X §6 (канон дублей Д1–Д15; README называет его арбитром) — положениями; `J/08-examples/run_checks.py` (самопроверка эталонов).
- creative: `99-raw/prompts/_common.md` «Решения заказчика» п. 1–6 (вторая нумерация решений) и отчёт X §2, §9 — положениями;
  `J/04-light-pass/src/scene.js` (исходник бандла L2; на него ссылаются blender `14-code-3d` и `KIT.md`).
- site: `build_crosswalk.py` — или объявить `crosswalk.tsv` источником правды, как text с `copy-slots.yaml` [light/site Д.7].
- Разделы `99-raw/tools/README.md` у creative, text, blender (45 ссылок), ai-media (переезжает с утилитами).

### 3.3. Исключения из «без ассетов»

- **Калибровочный набор** (Р16, Р56): ≈ 40 кадров WebP/AVIF, свои рендеры и генерации, поровну «уровни» и «типичный брак», с
  разметкой; без выходов Qwen 2.1 и синтетических людей. Кандидатов 50 — §11.
- **Эталоны creative L0–L2** (Р41): `10-recipes/examples/_shared/fonts/` (10 woff2 OFL + LICENSE, ≈ 0,5 МБ), `l2-zveno/img/*.webp`
  (7 своих рендеров, ≈ 0,1 МБ), `l2-zveno/js/three-scene.js` (594 КБ); по инвентарю 23 файла, 1,19 МБ; `img/render.log` — мусор.
- **Эталоны blender, минимум ≈ 1 МБ** (Р57). По выжимке это вариант (А): `12-recipes/examples/01-hero-product/{case.glb, poster.avif,
  poster.webp}` (≈ 25 КБ) + `dist/` (0,88 МБ) или пересборка из `hero.js`; по желанию телефонный набор `hero-lazy` (+0,61 МБ). Варианты
  (Б) «Сдано» +2,1 МБ и (В) «Звено» A +1,4 МБ под «≈ 1 МБ» не проходят (вывод). Шрифты витрины — копии creative, один экземпляр.
- **ai-media:** `G/01-llm-svg-icons/lucide-ref/` (104 КБ SVG, ISC) — входит в исключение Р54 (без него `check_icons` не работает).
  Шаблоны доставки `pages/` (137 ассетов, 7,6 МБ) и демо-лендинг исключения не получили — без ассетов не откроются (§12).
- ui, site, text, ux — эталонам ассеты не нужны.

### 3.4. Не переносим

- **Служебное всех баз:** `90-sources/`, `91-videos/`, `99-raw/` кроме `tools/` и исключений §3.2; `PLAN.md` — файлом (нормы
  извлекаются, §5.5); `99-raw/handoff-to-neighbours.md` — вход сверки, не норма; `skills-map.md` site, text, creative — противоречат Р6
  (пять скиллов, база по абсолютному пути, выход в kimi) [light/site §1.1; light/text §1.4; light/creative §1.8].
- **Мусор:** `venv-*` (ai-media 1,01 ГБ, blender `venv-yt` 100 МБ и др.), `__pycache__`, бандлы и `dist/` (пересобираемы; кроме
  `three-scene.js` creative по Р41), `render.log`, чанк `zveno/c-hybrid/js/chunks/chunk-2RVMEKYY.js` (срез ошибочно пометил кодом).
- **Окружение — не в git, скрипт установки с версиями и sha256** (Р55, Р59): ai-media `bin/` 306 МБ, `models/` 297 МБ, `node/` 201 МБ;
  blender `bin/` 12 МБ, `node/` 56 МБ; site `web-vitals`, `axe-core`; среда вне баз (`~/.claude.json`, `~/.local/share/blender-agent`,
  `~/.cache/blender-research/npm-*`, `app-design/.locks/`).
- **Запрещено:** `claude-design-research/99-raw/cache/` — закрытые тексты Anthropic (`cc-2.1.281-design/`), снимки промта Claude Design
  (`gists/`), клон Open Design 440 МБ [kimi→cd §6.2].
- **Kimi:** `kimi-research` целиком (Р77); Kimi-ветки кода и схем соседей — переписать или снять (§6.2).
- **По решениям:** text замер (Р32) и сборки из `99-raw` (Р33); creative `lab/`, `effect_bench.py`, `03-live-sites-measured/` (Р39),
  генератор `effects.yaml` (Р37); ai-media `routing.v0/v1` и 63 карточки моделей (Р54); blender данные регрессии (Р58), `mcp-for-blender`
  (Р59); UIClip и прочие оценочные модели (Р47).

### 3.5. Итоговый объём (оценка синтезатора)

- Текст и код после решений — **≈ 14,5–16 млн токенов** против 17,8 млн по умолчанию. Главный вычет — замер text (1,22 млн), затем
  журналы и копии утилит. Разброс дают выборка исходников дорожек blender (0,3–1,0 млн) и запасной каталог RouterAI (0,36 млн).
- По размеру: ≈ 40 МБ текста и кода + 2–4 МБ исключений из `99-raw` (без сборок) + ассеты эталонов ≈ 2,2 МБ + калибровочный набор
  (≈ 40 кадров WebP/AVIF, по размерам кандидатов — единицы МБ).
- Файлов ≈ 1,2–1,5 тыс. (по умолчанию 1 585) — зависит от выборки исходников blender.
- Окружение (бинарники, модели ONNX, npm, Blender, Brave, Chromium) — вне git, ≈ 0,9 ГБ, описывается установкой.

## 4. Утилиты

Вердикты — из выжимок и решений; «канон» — копия, которая остаётся одна на систему (сверка md5 в выжимках). Общее для всех: корень
базы вычисляется «два уровня вверх от `99-raw/tools/`», имена папок зашиты в код → нужен один конфиг путей [light/site §3; light/text §4];
venv не переносятся — нужны списки pip; браузерные утилиты работают под `flock` и общей блокировкой `app-design/.locks/browser.lock`.

### 4.1. Сводная таблица

| утилита | канон | вердикт | что делает в будущей работе | зависимости и окружение | что адаптировать |
|---|---|---|---|---|---|
| **общие** | | | | | |
| `ui_audit.py` | ui (= creative, site, kimi) | с адаптацией | визуальный QA экрана и HTML-копий артбордов, 81 проверка; шаг ревью cd | Playwright + Chromium; `color.py` рядом | вывод из `99-raw/cache/audit`; пресеты C, D — в данные; API сохранить (импорт `marketing_audit`); `--tokens` читает только DTCG ui [light/ui §4] |
| `color.py` | ui (= ai-media, creative, site, kimi) | взять | WCAG 2, APCA, OKLCH, ΔE | stdlib | — |
| `measure_ui.py` | ui | с адаптацией | computed styles: Take «measured» референсов, замер своих экранов | Playwright, `color.py` | путь вывода |
| `build_reference_tokens.py` | ui | с адаптацией | выпуск DTCG → `tokens.json`, `tokens.css`, `theme.css`, `report.txt` | stdlib, `color.py` | ручки и пресеты — во вход (сейчас CLI только `--out`); выгрузка в `tokens.json` ДС (Р42) |
| `page_accept.py` | ai-media (надмножество site и creative) | взять одну копию | приёмка страницы: байты, LCP, CLS, F83, пауза, reduce | Playwright, numpy, scipy, Pillow | порог 2 500 КБ — не норма site; блокировка |
| `asset_inventory.py` | ai-media | взять одну копию | инвентарь ассетов живой страницы | Playwright | — |
| `site_probe.py` | blender (6 копий) | взять одну копию | замер страницы и 3D-сайта для ворот | Playwright | — |
| `check_links.py` | один общий (у 7 баз разные версии) | с адаптацией | ссылки, «NN/MM», «→ §», `[V:]`, разделы файлов — после любой правки и при уборке | stdlib | служебные пути (82 у site), раскладка скилла (Р66; light/site Д.1 п.1) |
| `orch_check.py` | site | с адаптацией | формат файлов, YAML, метки | PyYAML | 8 служебных путей (Р66) |
| **site** | | | | | |
| `site_validate.py` | site | с адаптацией | схемы и перекрёстные ссылки брифа, плана, карты, каталога, форм, проекта; `--selftest` на «Отвесе» | PyYAML, jsonschema + referencing | пути к сёстрам `../text-research/…`, `../creative-research/…`; `all_paths()` без v0; URN |
| `page_gates.py` | site | взять | вердикт по 63 воротам; `--resolve` профиля и уровня | PyYAML | код v1.2 при YAML v1.3 (SG-PERF-16 — вручную) |
| `ab_plan.py`, `vocab_lint.py`, `checklist_export.py` (site) | site | взять | A/B-расчёт; id вне словаря; сборка `site-checklist.yaml` из 09/02 | stdlib / PyYAML | — |
| `plan_to_assets.py` | site | с адаптацией | каркас плана ассетов из медиа- и 3D-слотов | PyYAML, `crosswalk.tsv` | формат ai-media `01/01` §8 |
| `page_anatomy.py`, `geo_probe.py`, `ia_probe.py` | site | с адаптацией, если аудит живых страниц в рамках (§12) | анатомия живой страницы и CWV; robots, боты, `llms.txt`, JSON-LD; структура многостраничника | Playwright + Chromium 153, web-vitals (npm), ≥ 3 ГБ, сеть, `PSI_API_KEY` | абсолютная блокировка; каталоги самопроверки в `99-raw`; классификатор по словарю v0 (роль верна в 62 %, блок — в 36 %) |
| `run_axe_targets.py` (`K/03`) | site | с адаптацией (Р66) | axe с адресами узлов → B-контраст лида, призыва, согласия | Playwright, axe-core 4.13 (npm) | путь в чужой опыт |
| `build_profile.py` (`K/02`) | site | взять (Р66) | профили 434 UX-* и 246 AC-* | PyYAML | пути к ux YAML и `12/03` |
| **text** | | | | | |
| `copydeck.py` | text | с адаптацией | copy deck: validate, claims, lint, check, approve, export | PyYAML | Kimi-ветки ≈ 445 строк → вход холста; `VOCAB_PATH`; статус «допущение» в enum, `x-status-rules`, `STATUS_RANK` (Р34, Р69); ключ `--vocab` |
| `claims_check.py` | text | с адаптацией | сверка с фактами и 66 правил права; вход `html` — для HTML-копий макета | PyYAML | формат `kimi-md`, `import-kimi` убрать; демо-факты (Р69) |
| `copy_lint.py` | text | с адаптацией | линтер слопа и набора; словарь ux по ролям | PyYAML (+ pymorphy3) | роль напрямую (Р31); жанр «интерфейс» с длинами по ролям (Р70); К1–К31 (Р34) |
| `ux_dict_to_yaml.py` | text | с адаптацией | ux 07/06 → лексикон, `--check` дрейфа | PyYAML | путь к канону ux |
| 7 скриптов опытов + `run_checks.py` | text | с адаптацией (Р33) | проверки и проекции входов шагов S1, S3–S6, S10–S11; самопроверка эталонов | PyYAML, jsonschema | корень «4 уровня вверх», `sys.path.insert` |
| `copy_extract.py` | text | по решению об аудите живых страниц | страница → текст по слотам | Playwright | абсолютная блокировка, временный словарь |
| `voice_to_lint.py`, `style_to_lint.py` | text | по желанию | голос и таблица стиля → правила линтера | PyYAML | — |
| **creative** | | | | | |
| `marketing_audit.py` | creative | с адаптацией | профиль `marketing` поверх `ui_audit`, приметы клише | Playwright, PIL, numpy | блокировки, вывод; строка источника «kimi 05/03» → `06/05` |
| `motion_check.py` | creative | с адаптацией | ворота эффектов, 5 режимов, сверка с `motion-spec` | Playwright, ffmpeg, numpy, PIL, PyYAML, brotli | `ROOT`, блокировка; известные ложные X-66 |
| `refs_client.py` | creative | с адаптацией, режим «поиск» (Р40) | клиент референсов и мудборда | Playwright + Brave 153, PIL, numpy, `color.py`, сеть | `/opt/brave…`, `~/.config/…`, блокировки; `handoff` в формате kimi → вход холста |
| `spec_check.py` | creative | с адаптацией (Р37) | проверки `treatment`, `motion-spec`, вариантов блоков | jsonschema ≥ 4.18, PyYAML | `SITE = APP/site-research`; числа уровней — из `ambition-levels.yaml`; `moments`, `motion-md` (kimi) снять |
| `ad_check.py` | creative | с адаптацией (Р37) | `art-direction` + 8 подсхем `visual-dna` | jsonschema | абсолютный `APP`; v0 → v1; `treatment.v0` → `effects.yaml` |
| `validate_stack.py` | creative | с адаптацией (Р37) | `stack.yaml` | PyYAML | абсолютный `ROOT`; `use_for` против `treatment.v0` |
| `recipe_check.py`, `registry_check.py`, `idle_probe.py` | creative | взять (Р37) | рецепты; реестр клише; «холст в покое» | PyYAML; Playwright | относительные пути к site |
| **ux** | | | | | |
| `checklist_export.py` (ux) | ux | с адаптацией (Р49) | md `12/02` → `master-checklist.yaml` | stdlib (+ PyYAML) | пути; `source_file` в YAML |
| **ai-media** | | | | | |
| `polza.py`, `polza_catalog.py`, `mp_client.py` | ai-media | с адаптацией | генерация (сухой прогон → `estimate` → `--live` с владельцем), снимки каталогов, RouterAI и Gen-API | stdlib (+ Pillow), сеть, ключи | пути вывода и кэша; ключи вне git (Р53); бюджеты RouterAI и Gen-API по умолчанию 0 |
| `routing_check.py` | ai-media | с адаптацией (Р54) | 15 проверок `routing.yaml` | PyYAML | проверка № 11 — без `99-raw/phase5/jobs` |
| `prompt_compile.py` + тесты | ai-media | взять | спецификация → промт диалекта + параметры + цена | PyYAML, jsonschema, Pillow | — |
| `vlm_to_dna.py` | ai-media | с адаптацией (Р55) | паспорт визуала | numpy, Pillow | VLM Gemini → Opus; `F/05 palette.py` внутрь; тихий откат DTCG-имён |
| `asset_audit.py` + тесты | ai-media | с адаптацией (Р54, Р55) | автоприёмка 9 режимов, OCR, коды `QA-*`, судья | numpy, scipy, Pillow, ffmpeg, RapidOCR/onnxruntime | 6 модулей опытов, `check_icons`, `lucide-ref` — внутрь; `JUDGE_MODEL` → протокол Opus |
| `edit_check.py`, `alpha_check.py`, `tile_check.py`, `video_loop_check.py` | ai-media | взять | правки и композит, альфа, шов тайла, петли | numpy, scipy, Pillow, ffmpeg | — |
| `avif_pick.sh`, `provenance_check.py` | ai-media | с адаптацией / взять | AVIF под SSIMULACRA2; C2PA, XMP, `stamp` | avifenc, ssimulacra2, c2patool, exiftool | абсолютный `B=` к `bin/` |
| `stand_run.py` | ai-media (канон слепых пар) | с адаптацией | мини-стенд, страница слепых голосов, подсчёт | PyYAML, Pillow, numpy | входы `phase5/inputs/E`, `jobs` |
| **blender** | | | | | |
| `blender_run.py`, `bpy_probe.py`, `lint_agent_code.py` | blender | с адаптацией / взять / взять | запуск Blender без окна; справка API из самого Blender; фильтр текста скрипта | Blender 5.2.2 | путь Blender `/home/mm/.local/bin`, журнал в `experiments/_logs` |
| `blender_supervisor.py` | blender | с адаптацией | Blender под надзором: транзакции, откат, `bwrap` | bwrap, systemd | сокет ≤ 107 байт (кириллица в пути) |
| `render_views.py`, `scene_check.py`, `gate_check.py` | blender | взять | рендер-листы; аудит сцены по паспорту; ворота 3D | Blender; stdlib | `LIMITS` — в данные (вывод) |
| `qa_pipeline.py` | blender | с адаптацией | конвейер `scene / glb / page` | Blender, node, Playwright | абсолютный `ROOT`; `E/26`, `F1/02` |
| `gltf_check`, `gltf_web_inspect`, `gltf_diff`, `gltf_load_bench`, `three_probe`, `anim_diff`, `web_view`, `fx_probe` | blender | взять (3 — с адаптацией) | проверки GLB, эффектов, анимации | Playwright, three с jsDelivr, node, Pillow, numpy | абсолютный `TOOLS`; HDRI из `experiments` |
| `bpyx.py`, `agent_scene.py`, `hygiene.py` + тесты | blender | взять | помощники bpy (47 функций, 25/25 тестов) | bpy | — |
| `rk.py` + `build.py` ×12 | blender | с адаптацией (Р57) | рецепты 01–12 | Blender, библиотеки `99-raw`, node | абсолютный `ROOT` |
| `regression/run_set.py`, `make_manifest.py` | blender | протокол (Р58) | регрессия агента и проверок | `qa_pipeline` | данные пересоздать на пилотах |
| `img_metrics.py`, `sheet.py`, `code3d/src` + `build.sh`, `vote/{build_pairs,tally,vote_server}.py` | blender | взять / с адаптацией | числа кадра и листы судьи; код сцены и крюк гибрида; слепое голосование | Pillow, numpy; npm вне базы; сервер 127.0.0.1 | абсолютный PATH node; якоря чужих сайтов убрать |
| `run_doc_blocks.py`, `slot_run.py`, `atlas_collect.py` | blender | по решению | исполняемая документация; очередь агентов; атлас инструментов | Blender; flock; сеть | абсолютные пути (§12) |
| **cd** | | | | | |
| `kit/` (`shot.py`, `diffshots.py`, `export.py`, `canvas.html`, `marks.js`) | cd | взять | автопроверки на HTML-копиях, `#N`, `diffshots`, запасной путь макета | Python 3.10+, Playwright, Pillow, NumPy, pypdf; Google Fonts | блокировка и память — флаги (`--min-free-gb 2`); нет `--views`, `--routes`, `--expect-fonts` (были в `shot.py` v3) |
| `mockup_checks.py` | cd | с адаптацией (Р62) | проверка макета: приметы, честность F-*, мобильная M-*, наложения, ресайз | — | снять `watch`; id → `LOOK-*`/`HON-*`; `ALLOW_KEYS` не менять; входы — md-таблицы (факты text — YAML) [mapping §4, §7] |
| `stand_page.py` | cd | с адаптацией | страница слепых пар стенда | грузит ai-media `stand_run.py` абсолютным путём | путь [mapping §4] |

### 4.2. Не брать

- Сбор источников и роликов: `fetch.py`, `render_fetch.py` (одинаковы в 9 базах), `yt_dl.py`, `yt_transcript.py`, `yt_frames.py`,
  `vtt2md.py`, `transcribe_local.py`, `whisper2md.py`, `asr_*` (12 у blender), `m3_fetch.py`, `ax.sh`, `retry_transcripts.sh`,
  `cc_bunfs_extract.py` (cd; извлекает тексты из бинарника Claude Code).
- Обслуживание ресерча: `sources_collect.py`, `extract_for_audit.py`, `extract_sections.py`, `ctx_watch.py`, `analyze_measurements.py`
  (битый путь к старому месту ui), лишние копии `check_links.py`.
- Замер жанра и пересчёт порогов: text `copy_metrics.py`, `before_after_build.py`, `build_copy_slots.py`, `D/03`; creative
  `effects_probe.py`, `scroll_record.py`, `effect_bench.py`; site `build_crosswalk.py` (или взять — §12), `make_schemas.py`,
  `E/01 validate.py`; ai-media `ab_analyze.py`.
- Под Kimi: site `site_brief_to_kimi.py` (его таксономия «copy / map / derive / drop / claude_fills» пригодна для проекции во вход холста),
  kimi `build_package.py`, `kimi_run.py`, сторож `watch`.
- Сборка витрины blender: `_shared/{build_index,rules_journal}.py`, `gallery/build.py`; старые `slot_run_v1`, `slot_run_v21`,
  `ctx_watch_v1`.

### 4.3. Окружение (описать установкой)

- Python 3.10–3.13: PyYAML, jsonschema ≥ 4.18 + referencing, numpy, scipy, Pillow, brotli, pypdf; pymorphy3 — по желанию (поднимает
  плотность маркеров RU на 0,25–0,35 на 100 слов, пороги сняты без него) [light/text §4].
- Playwright 1.63 + Chromium 153; Brave 153 для `refs_client.py` (мажорные версии должны совпадать); ffmpeg 7.1.5; Node 24 + npm:
  web-vitals 6.2.2, axe-core 4.13; svgo 4.1, resvg-js, lucide-static 1.47; three 0.186.0, postprocessing 6.39.5, n8ao 2.0.1,
  esbuild 0.28.2, gltf-transform 4.5.0.
- Бинарники: c2patool 0.27.22, exiftool 13.59, libavif 1.4.2, libjxl 0.12.0 + ssimulacra2, libwebp 1.6.0, RIFE v4.6, Real-ESRGAN,
  vtracer, potrace (ai-media); gltfpack 1.2, toktx 4.4.2, gltf-validator (blender). Модели ONNX: u2netp, isnet, Depth Anything V2 Small,
  PP-OCRv5 — sha256 в `thresholds.yaml` (Р55, Р71).
- Blender 5.2.2 LTS (`blender -b`), `bwrap`, `systemd-run`; путь сокета ≤ 107 байт, кириллица — 2 байта на символ (путь к базе:
  46 символов, 55 байт) [light/blender §1.6].
- Ресурсы: ≥ 3 ГБ свободной памяти для браузерных утилит ai-media и site, `--min-free-gb 2` у `kit` (STATE); ключи polza, RouterAI,
  Gen-API — вне git (Р53).

## 5. Сквозные нормы и контракты

### 5.1. Реестры противоречий — нормы («два файла расходятся — действует реестр»)

| база | реестр | где | статус | что делать |
|---|---|---|---|---|
| site | В-01…В-36 + «Свод поправок к соседям» (26 правил и 17 вне таблицы) | README 336–430 | В: закрыто 17, X2 — 1, S1 — 14, S2 — 4; Свод: ✔ 19, ◐ 7 | переносить нормой; ссылки на отчёты X, S1 убрать; 240 «PLAN №N» → Свод [light/site Д.6] |
| text | X1–X45 + N1–N10 | `CONTRADICTIONS.md` | решено 15, позиция 22, открыто 8 (X7, X44 решает site; X11; X16; X25; X33; X41; X45) | нормой; P5 п. 10 выровнять с X42 [light/text §2, Д3.4] |
| creative | X-01…X-67 | `CONTRADICTIONS.md` | решено 31, позиция 22, открыто 9 (X-06, X-32, X-38, X-42, X-48, X-58, X-60, X-61, X-66), X-59 — заказчику; X-67 добавлен 25.09 | нормой; счётчики README (66 → 67) [light/creative §2] |
| ui | C1–C49 | `CONTRADICTIONS.md` | все решены, C8 `[спорно]`; 43 врезки в 24 файлах | нормой; сжатый слой против [C5], рецепт 07 против [C14] [light/ui §2, §3.1] |
| ux | № 1–61 + 16 позиций с условием | README 666–775 | 9 прямых закрыты, но № 42, 43, 46 не закрыты в сжатом слое; ≥ 11 строк устарели в копиях; № 56 ошибочен | нормой; выровнять (Р48), исправить № 56 [light/ux §1.3, §2] |
| ai-media | X1–X50 | `CONTRADICTIONS.md` | решено 38 (16 — фазой 5), позиция 10, открыто 2 (X2, X33) | нормой [light/ai-media §2] |
| blender | R1–R52; T1–T26 | README 603–687 | R: 26 закрыто, 26 с условием; T: T15, T18 открыты | нормой [light/blender §2] |

### 5.2. Таблицы канонов («одна норма — одно место»)

- ux: отчёт X §2.1 — 54 строки «правило → где повторяется → расхождения → канон → что сделать» — переносить нормой (Р50).
- text: отчёт X §6 Д1–Д15 (канон дублей, README стр. 33–34 — арбитр) и §7 К1–К31 (известные ложные находки, Р34); §3 — 15 вопросов
  базы (12 закрыты) [light/text §2].
- creative: отчёт X §2 (≈ 20 норм, «число живёт в одном машиночитаемом месте») и §9 (14 порогов: источник, цена ошибки, как
  калибровать) [light/creative §2].
- site: отчёт X §1.3 (С-01…С-32), §2 (Д-01…Д-19, «норма живёт у владельца темы»), §9.3 (что остаётся противоречием) — Р66.
- blender: отчёт X §4 (22 темы канонических мест чисел) и §1 (полный реестр R) — решения нет.
- ai-media: отчёт X §3 и «Продолжение X2» — уже внесённые поправки, история, не норма (вывод выжимки).

### 5.3. Владение форматами и конвейеры

- site `PLAN.md` «Как всё сочетается» (208–259): схема «бриф → карта → план → сёстры и соседи → пакет → проверка → правки → запуск»,
  таблица «формат → владелец → кто пишет → кто потребляет» (11 строк), точки S0–S2 — лучшая карта связей site; звено «пакет kimi»
  устарело [light/site Д.6].
- text `PLAN.md` 190–287: схема «заказчик → site-brief → смысл → план site ↔ арт-дирекция creative → copy deck → проверка → ассеты и
  пакет kimi → сборка K3 → публикация», 14 форматов, точки синхронизации 1–8, черновой формат copy deck v0 (охраняют `x-v0-fields`).
- creative `PLAN.md` 186–233: схема «заказчик → site → creative (уровень → концепция → мудборд → направления → `art-direction` →
  `treatment`) → text, ai-media, blender → kimi (пакет) → K3 или Claude → проверка»; `09/01` §1 «Контур передачи подачи».
- ai-media `PLAN.md` 131–249: 8 исполнителей, слои конвейера, 17 цепочек.
- Контракт тройки §2 (32 темы) и §3 (16 форматов); site `99-raw/prompts/_common.md` «Кто чем владеет» (15 строк; буквы агентов →
  папки — по докстрингу `check_links.py`).
- text `10/README` «Куда уходят поля» и «Границы» — потребители полей copy deck (Claude Design среди них нет).
- blender контракт GLB гибрида (`_shared/code3d/README.md`; «пишет только CD» — CD здесь дорожка испытания, не Claude Design).

### 5.4. Межбазовые контракты: что с ними делать

Список — §2.2. Действия по типам:
- **Заморозить id и ключи:** UX-*/AC-* (Р49), `ALLOW_KEYS` (Р62), неймспейс `org.ui-research.*`, имена DTCG-токенов, которые читает
  `vlm_to_dna.py`.
- **Одна копия, интерфейс — контракт:** `ui_audit`, `color`, `page_accept`, `site_probe`, `asset_inventory`, `check_links`.
- **Переименовывать только синхронно:** URN схем с именами баз; id K3-*/F-* → `LOOK-*`/`HON-*` в creative, site, text; поле `k3_allow`
  (например, `allowed_tells` — `mapping` §5); схема `visual-dna`.
- **Свести на сверке:** словари id (секции, слоты), состояния, компоненты, приметы и клише, направления, протокол судьи (§9).
- **Спроектировать заново:** единый вход холста и ДС на месте Kimi-стыков (Р64), стык `page-plan` ↔ copy deck.

### 5.5. Нормы в «процессных» файлах

- **Метки доказательности:** site `PLAN.md` 311–334 (15) и контракт §4; text `PLAN.md` 375–412 (16); creative `PLAN.md` 390–413;
  ux README (9 меток и 11 оговорок к числам); ai-media README и `13/04` §3 (`[стенд]` — ≥ 2 задачи и ≥ 70 % пар, ни разу не выполнено);
  blender README («в выжимку — не ниже `[консенсус]`»); ui README «Что ненадёжно»; `06/README` п. 9 (метки сверх базовых). Нужна
  одна легенда.
- **«Решения заказчика» баз как умолчания:** site 15, 20 (+ 11, 10, 8, 7); text 16, 17, 8; creative — две нумерации (`PLAN.md` 1–24 и
  `_common.md` 1–6: «решение заказчика 2» ведёт во вторую); ai-media 12, 14, 15–16; blender — «решения 23.09» п. 6.
- **«Как расширять базу»** — нормы обслуживания будущего скилла: site `PLAN.md` 686–722, text 797–834, creative 703–743, ux «Итог»,
  blender 794–841; для ux — только то, что пригодится для обновления скилла (Р50).
- **Границы покрытия:** интернет-магазин, звук, айдентика, настройка рекламы — вне site, text, creative; лендинги и маркетинг — вне ui
  и ux; UX-логика — у ux, 3D — у blender, генерация — у ai-media.

## 6. Что меняет наши решения и главные риски

### 6.1. Сжатый слой устарел

- ux: у ≥ 11 из 61 строки реестра (№ 3, 4, 7, 9, 34, 37, 40, 41, 42, 43, 46) — устаревшие копии в «Выжимках», «Частых ошибках»,
  «Чек-листах»; три из них волна 4 считает закрытыми; строка № 56 ошибочна сама. Причина — политика `PLAN.md` «не разрешать правкой
  файлов»; маршрут README ведёт агента в устаревшее раньше, чем в реестр [light/ux §1.3].
- Устаревшее уже машиночитаемо: UX-A11-14 (44×44 без «на таче») и UX-FRM-20 → YAML → профиль site [light/ux §9 п.2].
- ui: выжимки `01/04` п. 18, `04/02` п. 11 и «Частые ошибки» `11/01` п. 8 спорят с [C5]; рецепт 07 — с [C14]; счётчики 184 / 287 /
  56 / 84 — старые [light/ui §3.1].
- site: сжатый слой `04/03` (v0.9), `01/03` (v0), `10/01` §7 (`treatment:0`), глоссарий §0, «Ждёт сверки S2», статусы handoff
  [light/site Д.7, Д.10].
- text: X42 решён, P5 п. 10 не исправлен; три утверждения README о словаре site устарели [light/text Д3.4, §9 п.8].
- creative: README считает 66 противоречий и 271 источник при 67 и 274; `02/03`:138 держит Dprofile в `hold` [light/creative §9 п.4].
- Дайджесты `digests/` устарели для creative, ux, ai-media, blender.
- **Меняет:** сжатый слой нельзя брать входом скилла без сверки с реестром; YAML и профиль site — перегенерировать (Р48, Р52).

### 6.2. Kimi в форматах

- creative: `k3_allow` (19 ключей), `handoff.kimi`, `maps_to.kimi`, `x-kimi-projection`, пакет `DESIGN.md` / `MOTION.md` / T7s,
  `spec_check.py moments` и `motion-md`, видео-референс только для `k3`, `refs_client.py handoff` в формате kimi; шкала `motion_level`
  родом из kimi, но уже своя норма [light/creative §7; kimi→cd §5].
- text: `copydeck.py export-kimi/import-kimi` (≈ 445 строк), формат `kimi-md` в `claims_check.py`, `x-kimi-map` в 5 схемах, 81 строка
  `copy-slots.yaml`, колонка `kimi` временного словаря, `promise → product.goal`, `verify-page` по образцу `k3_checks` [light/text §7].
- site: `site_brief_to_kimi.py`, `site-brief.kimi-map.tsv` (189 правил), `x-kimi-projection`, шаги 8–9 процедуры, SITE-PRE-26,
  DEF-10, `09/01` §6, акты I–L привязаны к A–H [light/site §5, Д.9].
- cd держал процесс в kimi (README стр. 6) — закрыто `06-design-process` (Р68).
- **Меняет:** Kimi-стыки не переписывать поштучно — заменить единым входом (Р64); нейтральная проверка макета — `mockup_checks.py` (Р62).

### 6.3. Валидаторы отстают от схем

- creative: `ad_check.py` — схема v0 и 29 временных id `treatment.v0`; `validate_stack.py` сверяет `use_for` с `treatment.v0`;
  `spec_check.py` держит числа уровней в коде; `art-direction` v1 объявлен, а примеры и валидатор на v0 [light/creative §9 п.1, §1.4].
- site: `all_paths()` валидатора включает v0-черновики; `page_gates.py` v1.2 при YAML v1.3 [light/site §3, Д.5].
- ai-media: `routing_check.py` падает на 29 из 33 маршрутов без `99-raw/phase5/jobs`; у плана ассетов нет схемы [light/ai-media §9 п.3].
- text: демо-факты код не различает; жанры и статусы зашиты в код в трёх местах [light/text Д «Поправки» п.4, Д4].
- ui: пресеты `ui_audit` — только `admin|consumer` в коде; генератор выпускает только пресет A [light/ui §9 п.1–2].
- **Меняет:** адаптация утилит со смоук-тестами — отдельная работа до пилотов (Р37, Р54, Р69, Р70).

### 6.4. Разнобой терминов

| слово | ux | слой проекта | site | text | creative | ui | ai-media | blender |
|---|---|---|---|---|---|---|---|---|
| зона | область экрана, «тип зоны» | смысловая группа блоков (interface) | не термин | зона ответственности базы | видимая зона экрана | зона каркаса | зона текста в кадре | зона текста, пустышки `zone_*` |
| слот | не термин | регион `shell` с `accepts` | место содержимого в блоке (6 видов, 119 id) | `slot_type` (69) | слот плана site; «слот браузера» | слот компонента | место ассета на странице | слот материала или действия |
| блок | часть экрана | узел навигации, дерево, `widgets.block` | блок каталога (84) | блок site | блок site | блок страницы; «блокер» | блок стиля, композиции, `legal` | 3D-блок страницы |
| flow | сценарий | адаптивная серия экранов; в mobile — граф | семейство макроструктур | не термин | семейство макроструктур | только CSS | не термин | не термин |

Ещё: «уровень» — 4 смысла у site; «паспорт» — по 3 у ai-media и blender, совпадают только словом; «ворота» — 3–4 смысла; «пресет» — 3
у ui, `preset` у mobile — стек; «роль» — 4 у creative; «сценарий» — 3 у text; «состояние» — ux 22 + 11, ui 14, проект 6; «ложный пол»
(site) = «ложное дно» (text); `section_role` ≠ `effect_role` ≠ `visual_role`; «CD» — Claude Design в выжимках и дорожка испытания в
blender; «K3» — Kimi, агент-продолжатель в site, id проверки в ui [CHAIN «Общее», 4–11; ux-низ §5].
**Меняет:** без единого глоссария синтез «на лету» смешает понятия — глоссарий строится на сверке (Р67) из «ложных друзей» 7 глоссариев.

### 6.5. Конфликт токенов на холсте

- Тип Design: на артбордах литералы из токенов ДС (их правит панель свойств), `{{…}}` — только для твиков; базы и `kit` — «только
  `var(--…)`, литералов 0» [kimi→cd §2 К1].
- `tokens.json` ДС: списки `{name, value, usage}`; нет семейства движения (в «Спице» ушло в `bundle.css`), темы только у цвета,
  плотность темой не выражается, `rules` / `doNotUse` / `alternatives` некуда; `ui_audit --tokens` его не прочитает [light/ui §1.3].
- Совпадает: имена CSS-переменных ui = имена токенов ДС без `--`.
- **Меняет:** генератор выпускает и формат ДС (Р42); проверка ДС на холсте — по принадлежности значения набору токенов (Р63,
  сверять с инструкцией типа); движение — вне токенов ДС.

### 6.6. Opus-судья тянет к «богаче»; калибровки нет

- J/02: Opus 5.5 выбрал «богаче» в 3 из 4 пар — все три брак по коду (масштаб ×5–25, процедурный градиент) [light/blender §9 п.9; Р60].
- creative K/03: судья — сам агент, не слепой, самосогласованность 100 % из-за узнавания; оценки craft — `[мнение, один судья]`
  [light/creative §9 п.8]. ИИ-отсев витрины нарушил правило чистых контекстов [light/blender §8 п.2].
- K-01 (согласие судьи с голосами заказчика) не проводился ни для одной модели — Opus калибровать с нуля; пороги доверия уже есть:
  ≥ 0,8 и Уилсон ≥ 0,65 при n ≥ 20 [light/ai-media §1.4].
- Самопредпочтение Claude-судьи на русских текстах не измерено [light/text Д4].
- Claude Sonnet 4.6 — худший IR_Axe (0,45) при лучшем выводе интерактива: ворота доступности не ослаблять [light/ux §8 п.1].
- **Меняет:** судья — фильтр; рубрика штрафует избыточность; решают код и человек (Р27, Р38, Р60); калибровка — на пилотах.

### 6.7. Неоткалиброванные пороги

- site: ворота откалиброваны на 8 страницах, судья без разметки людьми; `budgets.yaml`, `events.yaml` — v0 [light/site §6 п.8].
- text: К1–К31 не внесены (`COPY-F-USE` — 56 предупреждений на 8 эталонах; «₽9,800» читается как 9,8); пороги типов страниц — на 3–15
  страницах [light/text §9 п.7].
- creative: 14 порогов ждут калибровки (X §9); ворота 0/0/0 примеров получены при известных ложных X-66 [light/creative §9 п.9].
- ui: рубрика и пороги антислопа на людях не проверены; «4 маркера» — «мой выбор» [light/ui §1.6].
- ux: IR ≤ 0,15 и Lighthouse ≥ 95 — одно исследование; серьёзность 434 пунктов назначена агентом [ux-низ §7 п.7].
- ai-media: 49 из 94 порогов не откалиброваны на выходах моделей; `[стенд]` не было ни разу [light/ai-media §1.6, §9 п.4].
- blender: правило решения 0,75 / 0,4 при одном судье ничего не различает (гибрид над кодом 0,40, Уилсон [0,12; 0,77]) [light/blender §1.3].
- cd: частоты примет `06/05` сняты не на Claude; пороги `diffshots` — на одном примере; пакет ≤ 7 — позиция для модели с управляемостью
  1,99 % [mapping §7; kimi→cd §6.3].
- **Меняет:** пороги держать как «решения базы» с метками; уточнять калибровочным набором и пилотами.

### 6.8. Быстро устаревающее

- ai-media: снимок каталогов 25.09; сроки 30.09 (preview `gemini-omni-video`), 06.10 (JPEG XL в Chrome 155), 23.10 (`openai/gpt-5-image`),
  01.12 (`gpt-image-1.5`, remove.bg), 02.12 (AI Act ст. 50(2)), 01.03.2027 (243-ФЗ); дешёвая петля держится на снятой вендором Seedance
  1.5 Pro [light/ai-media §1.3, §9 п.6–7].
- site: `crawlers.yaml` — раз в квартал; изменения выдачи 2026 года; право — по редакциям [light/site §6 п.11].
- creative: версии `stack.yaml` на 24.09; реестр клише — 40 насыщенных, 0 свежих, `review_by` 2027-03-24 [light/creative §9 п.5].
- ui: маркеры 11/04 — раз в полгода; база «застыла» на тексте `frontend-design` от 22.09 [light/ui §1.7].
- blender: Blender 5.2.2, three r186, таблица дрейфа bpy (6.0 удалит `use_nodes`) [light/blender §1.5].
- cd: адреса и релизы типов, контракт 0.2.47 (новейший 0.2.60), Claude Code 2.1.281; ux `11/03` §2.5 — снимок на 17.04.2026
  [kimi→cd §6.5; ux-низ §6 в п.8].
- **Меняет:** скоропорт — в датированные YAML с процедурой освежения (Р15; ai-media `13/04`).

### 6.9. Среда, пути, нумерация

- Нумерация как API — адресов «NN/MM» и указателей «→ §»: site ≈ 760 / 659, text 893 / 844, creative 1 349 / 751, ui 371 / 1 406,
  ux 886 / 1 584, ai-media 805 / 1 679, blender 1 147 / 1 455. `check_links.py` их видит — смена раскладки без него ломает молча
  [light/site Д.1 п.1; §6 выжимок].
- Абсолютные пути `/home/mm/…` в коде: blender — 14, creative (`ad_check`, `validate_stack`, Brave), ai-media (`avif_pick.sh`),
  блокировки site и creative.
- Воспроизводимость держится на кэшах вне базы (`npm-trial` 198 МБ; `npm-F1` уже пуст); рецепты blender 13–17 свежими агентами не
  прогонялись [light/blender §9 п.4–5]; `page_accept` фазы 5 не запускался из-за памяти, телефон не проверялся ни разу [light/ai-media §9 п.9].
- **Меняет:** конфиг путей, скрипт установки и смоук-тесты (Ф4); раскладку в шаблоне менять только со скриптовой перезаписью адресов.

### 6.10. Право, регион, лицензии

- Русская рамка по умолчанию: 152-ФЗ, Метрика, Директ, Яндекс (site); право РФ, Алиса, Вордстат (text); рублёвые каналы (ai-media) —
  шаблон для других пользователей окажется региональным [light/site §6 п.10; light/ai-media §7].
- Площадки референсов запрещают автоматический сбор (Dribbble п. 7.1, 7.2, 7.11 и правило API; Dprofile п. 11.3; Adobe п. 6.18) —
  Р40: листает заказчик, картинки не выкачиваем [light/creative §1.3].
- Лицензии: Hallmark и ui-ux-pro-max — MIT; Shadertoy без лицензии — CC BY-NC-SA; `rembg` по умолчанию тянет RMBG-2.0 (CC BY-NC) —
  модель задавать явно; Qwen 2.1 — research; 3D — без вопроса только CC0 [light/site Д.1 п.8; light/ai-media §1.7; light/blender §1.8].
- ПДн: правило text «в модель с хранением в РФ или обезличенно» не применяем (Р74); нормы 152-ФЗ для проектируемых сайтов остаются
  содержанием.

### 6.11. Процессные риски

- База ещё менялась (с 25.09: blender 1 812 файлов, ai-media 70, cd 46) — нужна заморозка [STATE].
- Craft-запрет `CLAUDE.md` §3: без его правки дизайн-слой нелегален [Ф1-05 «Коротко» п. 3].
- Контекст шаблона: всегда ≈ 22 тыс. токенов, 7 описаний скиллов уже не видны в листинге — новым скиллам нужно место [STATE; PLAN].
- «Нужен ли Blender» для живой страницы не измерено: вслепую по кадрам — Blender, вживую — гибрид; второй тур — не сейчас (Р58).
- Claude Design делает макет, а не страницу: ворота исходов (LCP, CLS, INP, вес, SSR) — только к собранной странице; «нет факта — нет
  блока» спорит с макетом на демо-данных — снято меткой демо-фактов (Р69) [light/site §6 п.4].
- Скриншот продукта как доказательство — только настоящий: макет Claude Design доказательством не станет [light/text Д3.3].

### 6.12. Противоречия между документами (показаны, не сглажены)

1. «318 правил» словаря ux (ux-низ §3.4 TX-02, §5, §7 п.5; CHAIN 3) против 159 (light/text §1.2; CHAIN 4): 318 — двойной счёт `id:` и `marker_id:`.
2. Правил с `appliesTo` / `excludes`: 38 / 144 (light/text §1.2) против 37 / 143 (text «Поправки» п.1).
3. «Прямого ввода роли в линтер нет» (light/text §1.2) против ключей CLI `--slot-type`, `--vocab` (text «Поправки» п.3).
4. «Демо-режим фактов есть» (light/text §1.1, §9 п.6) против «соглашение, а не функция кода» (text «Поправки» п.4).
5. site, пилот: `check_links.py`, `orch_check.py` «не брать» (§3) против «общий проверщик» (Д.1 п.1; ревью № 10) — Р66 взял.
6. site, пилот: `pages.csv` «никто не читает» (§2.1) против «читают 19 опытов site и creative A/03» (Д.1 п.4; ревью № 3) — Р66 переносит.
7. site, пилот: `run_axe_targets.py` — «единственный путь к контрасту» против Д.1 п.2 (ревью № 12).
8. «35 расхождений» (пилот, вопрос 5) против ≈ 14 конфликтов норм и 31 «ждёт» после пакетов W4 (Д.1 п.3; ревью № 7).
9. «Для UI-проверок нет маркетингового профиля» (пилот §6 п.13) против creative `marketing_audit.py` (Д.1 п.7).
10. Kimi в site: 783 строки (срез) против ≈ 630–640; «решение N»: 75 против ≈ 129 строк (Д.1 п.6; ревью).
11. Р67 говорит о «≈ 14 реальных конфликтах тройки», а по разбору site это конфликты site со всеми соседями: ai-media M5–M6, blender
    B2–B4, ux U3–U5, ui UI1, text T6–T8, T12, creative C10 [light/site Д.1 п.3].
12. Ролей секций у site: 40 (light/site §1; CHAIN 4; WORKFLOW-INPUTS §3) против 42 (`03/01` в Д.4, `vocabulary.yaml` в Д.5).
13. Состояний элемента в ux: 11 (`06/01` §7.2) против 9 (`06/01` §8.1, UX-STA-14) против 8 (`11/04`); у ui — 14 [ux-низ §6 б п.1].
14. Форма в модалке: «≤ 5 полей» (правило 23, № 7) против «менее пяти» (UX-FRM-20) [ux-низ §6 б п.3].
15. Обязательные шаги процедуры ux: «1–13» (`13/README`) против «1–16» (`13/04` §1) [ux-верх §6 б п.4].
16. Ссылок ux → ui: README «262», срез 170, handoff «130 упоминаний» [light/ux §5].
17. ui: словарь `usage` «84 метки» при 94 по списку; «двадцать» автопроверок при 22 [light/ui §1.3, §1.6].
18. text: уровни лексикона по разбору 124 / 163 / 47 / 2 против `06/02` §1 118 / 164 / 51 / 3 [light/text Д1].
19. ai-media §10: «кадры `MS-marea` не предлагаю — айдентика реального приложения заказчика», и в том же разделе «сверх лимита» — кадр
    стыка петли из `MS-marea/loops/MS-03-…`.
20. creative: `02/03`:138 — Dprofile `hold`, в `02/01`, `02/02`, `DEFAULT_MODES`, `PLAN.md` п. 21 — «поиск».
21. creative `lab/`: по базе «не образец» (X-26), в skills-map — «код-референс» [light/creative §1.6].
22. Направления: creative 3–5 (по умолчанию 4) против cd 2–4 (и «2–3», «три», «4» в разных файлах cd) [light/creative §1.7].
23. Пакет правок ≤ 7: норма kimi против cd `03/01` §8.2 «для Opus лимит можно поднять `[спорно]`» [kimi→cd §2 К3].
24. Ширины: DECISIONS (Р28, Р46) против site (1440×900, 390×844, 360×800), ui (1440 / 1280 / 390 + зум 400 %), ux (три набора, «произвольные
    ширины» в `13/04` §24), `06` (1440 / 1280 / 768 / 390 / 360) [light/site Д.9; light/ui §8 п.4; light/ux §8 п.2].
25. Закрытый словарь `ui:` (Р29, Р76) возвращает контракт, снятый коммитом `1dd3a93` [Ф1-05 §1 Г; ux-низ §8 в.3].
26. `PLAN.md` Ф2 («по 2 агента на ресерч») и Ф3/Ф7 («K3 — по желанию в сравнительном тесте») против хода Ф2 и Р77; `Ф1-05` §4.1
    («Claude или Kimi K3 → скриншоты 1440 / 768 / 390») устарел.
27. STATE (ai-media): «ключи засвечены — перевыпустить» против Р73 (заказчик не перевыпускал).

## 7. UX-дельта для слоя проекта

Сводка ux-верх и ux-низ; решения — из DECISIONS. Каждый слой: как сейчас (Ф1) → главное по базе → проверки.

| слой | главное изменение | проверки | решения |
|---|---|---|---|
| vision | из узкого (Problem, Success, Non-goals, 4 оси) — 12 разделов: имя и род, проблема (наблюдения как ограничения), для кого, позиционирование, принципы опыта с проверкой, голос и тон, успех «цель → сигнал → метрика», объём MVP (slug capability + 12 системных сценариев), устройства и доступность, ограничения, что не делаем, допущения. Позиционирования и принципов опыта в ux нет — нормы из text и creative [ux-верх §3.5, §7 п.7] | VS-01…06 | Р19: расширять в самом `vision.md`, агент предлагает «допущением», новыми разделами владеет владелец vision |
| роли и постуры | у `who` нет постуры → 8 колонок постуры; роли раньше поверхностей: разделение админки и клиентской части по 7 критериям (`13/04` §17) может раздвоить поверхность [ux-верх §3.6, §7 п.3] | RL-01, RL-02 | Р22 |
| объекты и действия | `data-items` без полей → глоссарий объектов (определение, примеры, состояния, кто создаёт и удаляет, атрибуты с рангом) и словарь действий; `data:<объект>.<атрибут>` резолвится | GL-01…05 | Р21: на уровне продукта, рядом с vision и capabilities |
| capability | 8 колонок, критерии не проверяются → реестр ≤ 10 колонок (`slug`, `name` = глагол + объект, `user`, `who`, `object`, `action`, `priority`, `passport`, `status`) + паспорт для хабов, критичных и stable; 7 критериев гранулярности Г1–Г7; двустороннее покрытие capability ↔ ситуация ↔ сценарий; трасса вверх к job, гипотезе или MVP [ux-верх §3.1–3.4] | CAP-01…13 (≈ 80 % — скриптом) | Р20 (название остаётся); форму решает оркестратор (Р23) — решение не записано (§12) |
| матрица «роль × объект × действие» | нет → вычисляемый вид из capability (`who × object × action × scope`) + CRUD-правила; колонки «контейнер / подтверждение / журнал» — в screens | MX-01…04 | — |
| сценарии | у web нет → kind `scenario` на хаб и критичную capability (шаблон `05/02` §1.4): happy path, ветвления, ошибки, 5 конечных состояний | SC-01…05 | Р76 (предварительно): аналитика — interface, маршруты, фокус и сохранение — screens |
| ИА | зоны без предела → ≤ 3 уровня, ≤ 25 корневых, стоп-лист имён, мост «зона → раздел → маршрут» | IA-01…05 | — |
| interface: ситуация, блок, субстрат | нет частоты, исходов, отказов; субстрат без контракта → `frequency`, список отказов, достижимость блоков, контракты семейств (действие — 7 полей, поле формы — 10 колонок, выбор, коллекция) [ux-низ §3.4] | CP-01…12 | — |
| screens: состояния | 6 канон-состояний → закрытый словарь S01–S22: база-5 + набор шаблона + условные S18, S16, S06; `not-found` — служебный маршрут; свои S07/S13 у блока с собственным источником; один словарь web, mobile, бота; «N/A с пояснением» сохранить [ux-низ §3.1] | ST-01…10 | Р45 (состояния элемента — в ДС) |
| screens: маршруты и навигация | `route` — строка, «shell — не sitemap» → карта экранов (шаблон, главная задача, ключевое действие, плотность из постуры), реестр маршрутов, матрица переходов, таблица навигации по ролям, «что переживает переход» | RT-01…08 | — |
| screens: нотация и `ui:` | псевдо-YAML не парсится, `ui:` свободен → валидный YAML или JSON Schema; `ui:` ∈ закрытый словарь типов; облик (`variant`, `size`, `gap`) — в слой дизайна, в дереве только уровень действия | CP-11 | Р29; Р76 (словарь типов на уровне проекта, ДС сопоставляет) |
| тексты интерфейса | дети дерева, «формулировки скилл не подсказывает» → реестр текстов с ролями (31), статус «допущение → утверждён», лексикон и длины по роли, одно имя действия | TX-01…08 | Р25, Р31, Р70 |
| доступность | только термин → цель WCAG 2.2 AA на уровне продукта; на экране — лендмарки, один H1, фокус, альтернативы, объявления | AX-01…07 | Р52 (цели 24×24, на таче 44×44) |
| mobile web | `viewport` без планшета → сценарии на телефоне или «нет», способ реализации, трансформация шаблонов (5 вопросов M3), навигация по числу разделов, класс medium | MB-01…08 | Р28, Р46 (ширины) |
| контракт генерации | звена «screens → макет» нет → пакет из 9 блоков `11/04` §7.3 собирается из stable-артефактов; правило «стоп» возвращает массовый провал в слой проекта; 34 из 52 дефектов закрывает вход [ux-низ §3.2] | GC-01, GC-02 | Р64 (единый вход) |
| оценка | правила без способов, `last-report` перезаписывается → реестр в формате YAML базы + способы `ART`/`MDL`, трасса к UX-*; находка из 6 полей; модельные проверки — ≥ 5 и 11 прогонов. Итог разметки 434 пунктов: скрипт 191 (48 блокеров), модель 23, макет 214, человек 5; из 81 пункта `HUM`/`JDG` 63 проверяемы на артефактах [ux-низ §3.6] | — | Р26 (скрипты), Р27, Р76 (история — в git) |
| граница с FSD | покрытия нет → `pages.path` = маршрут реестра, `guard` — из колонки «доступ», `shared-ui` ⊇ `ui:`, режимы API | — | — |

Открытые развилки UX (для §12): форма capability не записана; где живут представления объекта (у глоссария или в screens); где
конвенции «одно на продукт» (≈ 10 строк реестра ux: № 1, 2, 4, 11, 18, 22, 27, 34, 42, 47) — слой проекта или ДС; «ноль находок —
неудачный прогон» против «пустой массив лучше» у `/cross-audit` [ux-низ §4, §6 в п.7, §6 г п.2].

## 8. Стыки для будущего workflow (сырьё, не проект)

### 8.1. Порядок этапов: набросок заказчика и база

- Заказчик: бриф и анализ репозитория → мудборды и референсы → ассеты, «генерировать или нет», Blender → общий визуал → ДС в Claude
  Design → вайрфреймы → ДС поверх вайрфреймов → слоями 3D, видео, анимации, креатив, уровень амбиций [WORKFLOW-INPUTS §2].
- База: уровень амбиций решается рано (бриф, страница, секция), поздно — только сами эффекты (creative); ассеты — после ДС и
  структуры: план из слотов, паспорт визуала из токенов ДС до первой картинки (ai-media); ДС — до экранов, эстетика — 2–4
  направлениями (cd, ui); мудборд — до направлений (creative `02/03` §1); «ничего не рисуй до артефактов шагов 1–13» (ux `13/04`).
- Расхождения (вывод): у заказчика ассеты идут до ДС, у базы — после; уровень амбиций у заказчика — последним слоем, у базы — в брифе.

### 8.2. Тексты → макет Claude Design

- Стыка нет: среди потребителей copy deck Claude Design не значится (`text 10/README` «Куда уходят поля») [light/text §1.1].
- Есть: факты раньше слов, смысл до текстов, тексты по слотам, аудит ≤ 3 прохода; COPY-C-33 — ключевые слоты в макете на 1440 и
  390 (совпадает с основными артбордами, Р28) [light/text §8 п.3].
- `claims_check.py` принимает HTML — можно гонять по HTML-копиям артбордов; сверка текста страницы с copy deck (F-COPY) есть только в
  `mockup_checks.py` [kimi→cd §1.7, §2 № 7]. Линтер на целой странице строже, чем по слотам (`rewrite` у 16 из 24 лидеров EN) [light/text Д3.2].
- На холст — реальные тексты литералами, недостающее — видимые заглушки; вариант обратного импорта из `.dc.html` при «прочитать →
  слить» [kimi→cd §5].
- Демо-факты: метка в схеме и `validate --final` (Р69) — макет на демо-данных допустим, публикация нет.
- UX-тексты SaaS: реестр с ролями, «допущение» (Р25), линтер text с жанром «интерфейс» (Р70); идут вместе с экранами и состояниями.
- Вероятная точка по вводным: смысл и факты — на брифе, черновик по слотам — со структурой и вайрфреймом, аудит — до чистового макета
  [WORKFLOW-INPUTS §3, вывод оркестратора].

### 8.3. page-plan ↔ copy deck

- Текстовый слот плана site несёт `intent` («из иерархии сообщений text»), `length` (класс), `variants`, `heading`, `required`; у плана —
  поле `copy_deck` (путь) [CHAIN 4; light/text Д3.1].
- В deck — `page_plan_ref`, `site_page_id`, `site_section_id`, `site_slot_id` — пусты; код план не читает; `site_slot` пуст у всех 69
  типов слотов, `site_id` — у 18 типов страниц [light/text Д1].
- Раскладка «роль секции → слоты» — только в опыте `I/04/make_skeleton.py` `[мнение]` (переносится, Р33); эталоны deck — 6 типов
  страниц из 18; `text_slot_defaults` в `blocks.yaml` выведены из `copy-slots.yaml` скриптом site `E/02` [light/text §5, Д3.1].
- Образец для слоя проекта — машиночитаемый план с намерением и классом длины, тексты — отдельным deck [ux-низ §7 п.6].

### 8.4. Единый вход холста и ДС

- Сейчас — несколько Kimi-стыков: site `site_brief_to_kimi.py` (правила «copy / map / derive / drop / claude_fills» пригодны для любой
  проекции), text `export-kimi`, creative `handoff.kimi`, `x-kimi-map`, `x-kimi-projection` [kimi→cd §5].
- `06/02`: вход один на ДС и холст — файлы `input/` в репозитории, у каждой части канон соседа (бриф — site, факты и тексты — text,
  токены — ui, подача — creative, ассеты — ai-media), приёмка A–H; раскладка `input/` — только предложение [mapping §7 п.3]. Р64 —
  спроектировать в Ф3.
- ux `11/04` §7.3 — 9 блоков входного контракта; «детальность входа — единственный фактор, улучшающий всё сразу» `[исследование]`.
- ui `12/04` §2.6: пакет `design-system/` почти совпадает с артефактом Design System (DESIGN.md ↔ бренд-бук, `guidelines/components` ↔
  `components/<Comp>`, `starter/` ↔ эталонные экраны, `checks/` ↔ `kit`) [light/ui §9 п.10]. Формата блока «Дизайн-система», которого
  ждёт ux, нет ни у одной стороны [light/ui §9 п.8].
- site: «три формы страницы из разных семейств» и SITE-PRE-12 «две альтернативы» ложатся на страницу «Направления» [ревью §3.1 п.10;
  CHAIN 11].

### 8.5. Мудборд и референсы

- creative `02/03` §1: оси поиска → 30–60 кандидатов (≤ 20 с площадки) → 3–6 кластеров → 3–5 направлений → мудборд на направление →
  выбор заказчика → `art-direction.moodboard` (≤ 12). Референс уходит словами: роль из 11, `applies_to`, Take (объект + свойство +
  число), Do not take обязателен; лендингу — 1 composition + 1 typography + 1 block-solution + 0–1 motion [light/creative §1.3].
- `refs_client.py` — «поиск» листает заказчик (Р40), «ассистент» и 9 галерей — без входа; Behance `off`, FWA `hold`; превью — вне
  базы; картинки с площадок не выкачиваем (Р40).
- cd: мудборда как этапа нет; вложения холста `/_blob/<id>` — вне git; как тип хранит референсы — `[не проверено]`; `06/02` §3 —
  ссылка + роль + значения текстом, кадр — от заказчика или замер живого сайта `measure_ui.py` [kimi→cd §2 № 6; mapping §7 п.6].
- Куда уходит мудборд: `art-direction`, `treatment.refs`, `site-brief.references`, исполнитель (ветка Claude для видео — лист 3×3 +
  кадры + таймлайн текстом), ai-media (роли словами), blender (текст важнее картинки).

### 8.6. Ассеты: генерация / код / Blender

- Лестница дешевизны ai-media; «нейросеть рисует атмосферу, код — геометрию и текст»; кодом за 0 ₽ — градиенты, паттерны, линейные
  иконки (Claude в сессии — 6 из 6), фавиконы, OG, кириллица; генерацией — атмосфера, свет, материал; главный путь «картинка 2K →
  видео по картинке» [light/ai-media §1.5].
- Слоты-доказательства не генерировать (`12/04` §2: люди в отзывах, команда, товар «как есть», чужие знаки, текст-факты в пикселях) —
  та же норма у site `08/02`.
- 3D: генераторы отвергнуты (Р72); «нужен ли 3D» — `01/02` §7, «чем делать» — `12/00` §1, `14-code-3d`, VERDICT §3 (страница целиком —
  гибрид; стоп-кадр — Cycles; сюжет без ввода — секвенции; модели нет — код; услуга — кадр Blender, оживлённый по проходам) [light/blender §1.3].
- Для макета Claude Design применимы постер, кадры и ассеты; ворота 3D — к собранной странице (вывод выжимки blender §8 п.6).
- Деньги и ключи — у владельца (Р53); `--live` — только с ним.

### 8.7. Уровни L0–L2

- Канон — creative `ambition-levels.yaml`: внутренние страницы L0, лендинги и главные L1, кампании и портфолио L2; конверсия — всегда
  L0; числа только в YAML (JS эффектов 20 / 100 / 150–200 КБ br, WebGL-контекстов 0 / 1 / 1–2, шрифты 150 / 250 / 300 КБ) [light/creative §1.4].
- site: правило L0 для лидогенерации и таблица уровней типов (решение site 20), профили `budgets.yaml`; blender: бюджеты JS 3D для L1,
  L2 (KIT §5).
- Уровень снимает спор с `frontend-design`: бриф задаёт движение и выразительность (Р44).
- Шкала `motion_level` (`none / subtle / expressive / cinematic`) — своя норма creative; `cinematic` требует ролик или 3D.
- Где хранить уровень — поле брифа, продукта или поверхности — открыто (Ф1-05 §7 в. 8).

### 8.8. Процесс из `06-design-process`

- 01 бриф: четыре списка (заказано, факты, ограничения, пробелы) → что Claude выводит сам → ≤ 7 вопросов одним сообщением с
  умолчаниями → оси направлений → решения до экранов (мобильная, движение, ассеты, 3D, варианты, итерации).
- 02 единый вход; 03 раунд: слить правки заказчика → пакет ≤ 7 с «Keep» → эхо → `diffshots` → «прочитать → слить → опубликовать» →
  коммит; W = 3·critical + major, прогресс W(N) ≤ 0,7·W(N−1), две итерации без прогресса — сменить стратегию.
- 04 проверки слоями «скрипты → глаза → рубрика (Opus) → свежий аудит → заказчик» — по постоянной просьбе заказчика; 05 бан-лист
  дефолтного вида (капс ≤ 2 %, ≤ 7 кеглей, кратность 4 ≥ 85 %, шапка ≤ 64 px); 06 стенд S1/S2, «X лучше Y» — Уилсон > 0,5 и ≥ 75 %
  пар, стратегия — на двух брифах; 07 задания по этапам [`06/README` выжимка п. 1–10].
- На Claude процесс целиком не прогонялся; правила формата типов не копируются (Р15). Спорное: частоты примет — не на Claude; локальный
  рендер `.dc.html` для `#N` и `diffshots` — открыт; бюджет раунда не мерился — стоп в раундах, ≤ 3 на экран [mapping §7].

### 8.9. Проверка и приёмка макета

- Постоянная просьба заказчика — один раз на проект (Р64); автопроверки — `kit` на HTML-копиях; основные артборды 1440 и 390, прочие
  ширины и вылет на 320 — HTML-копиями (Р28, Р46); тёмная тема — если есть.
- Ворота по состояниям, сценариям, маршрутам, текстам и данным инструмент макета не держит — только слой проекта и приёмка (ux `11/03`
  §1); колонка «как проверить» S-состояний — готовые критерии; 214 пунктов — только на макете [ux-низ §3.1, §3.6].
- site: проверки уровня плана (SITE-PRE, `site_validate`, AIL, эксперт, судья) применимы к макету, ворота исходов — только к SSR-странице
  [light/site §6 п.4].
- Для SaaS шов «проект → дизайн» — бриф на визуальный слой ux `13/04` §25 и контракт генерации `11/04` [ux-верх §4; ux-низ §3.2].

## 9. Сверка баз — что сверять

| № | что сверять | стороны и файлы | источник | готовый каркас |
|---|---|---|---|---|
| 1 | ≈ 14 конфликтов норм site с соседями: M5, M6, B2–B4, U3–U5, UI1, T6–T8, T12, C10; пограничные M8, M9; ещё 19 строк — согласование id, ссылок, схем, демо-данных | site `99-raw/handoff-to-neighbours.md` (статусы C1–C9 устарели — ответ W4 от 25.09) | light/site Д.1 п.3; ревью № 7; Р67 | «Свод поправок» README site 388–430; `09/02` §8 (14 тем); `07/03` §6; X §1.3 |
| 2 | WEB-01 (LCP десктопа ≤ 1 с) и WEB-04 (вес страницы) — блокеры страницы у blender против site B2 и creative cb-01; B1, B3, B4; cb-03 («парение» 3–4 с против ≥ 10 с), cb-04, cb-09; R2, R19, R20 (бюджеты и TBT) | blender `11/05`, `09/05` §7; site `page-gates.yaml` (`maps_to`); creative handoff | light/blender §2, §9 п.10; Р58 | blender `11/05` §11 |
| 3 | Прочие ворота и бюджеты: ai-media «первый экран ≤ 2,5 МБ = FAIL» и порог `page_accept.py` против веса как S у site; ux CWV (AC-PRF); creative `lcp_s_lab`; бюджеты первого экрана site `07/03` и creative `01/03` | site `07/03` §6 | light/site §6 п.2, Д.6 | site `07/03` §6 |
| 4 | Словари страниц, секций, слотов: 28 ролей и 63 `slot_type` text против 40–42 ролей и 119 слотов site; `site_slot`, `site_id` пусты; 133 строки text в `crosswalk.tsv` — по временному словарю; `landing-product` (site) против `landing-campaign` (creative рецепт 03); 5 `proposed` типов; AIL-52 | site `vocabulary.yaml`, `crosswalk.tsv`; text `temp-vocabulary-v0.yaml`, `copy-slots.yaml` | light/text Д1, Д3.1; light/site §6 п.2, п.9, Д.10 п.6 | README site «Ждёт сверки S2»; пакеты W4 |
| 5 | Единый глоссарий: слова из §6.4 | «ложные друзья»: site `00-glossary` §0 (24), text §13 (≈ 20), creative §0 (19), ui §14 (27), ux (20), ai-media §12 (19), blender (35) | CHAIN «Общее»; ux-низ §5 | — |
| 6 | Словарь компонентов и состояний элемента (Р45) | ux `04/*`; ui `06/01–06`, `06/07` (17 строк), `14/08` §4 (40 меток), `app.css`, `12/04` §2.6; состояния ux 11 / 9 / 8 против ui 14 | light/ui §1.4; ux-низ §6 б п.1 | матрица ui `06/07` |
| 7 | Контракт состояний экрана: S01–S22 против 6 (screens), 9 + 5 (mobile), бот; один словарь | ux `06/01` §2, §3.1 | ux-низ §3.1 | таблица сопоставления ux-низ §3.1 |
| 8 | Шаблоны экранов: ux `03/01` (11) против ui `05/02` (8 каркасов) и `05/03` (8 типов страниц); типология `06/01` §3.1 против `13/04` §14 | ux, ui | light/ui §5; ux-низ §3.1 | — |
| 9 | Ширины и брейкпоинты | §6.12 п. 24 | Р28, Р46 | — |
| 10 | Цели нажатия и плотность: ux правило 46 против UX-A11-14 и handoff; ui пресет A (кнопка 32), B (контрол 40) | ux `08/01` §12.4; ui `03/02`, `14/11` | light/ux §1.3; light/ui §1.8; Р52 | — |
| 11 | Шкала отступов: ux «8 / 4 (+2)» против ui «4 + 2, 6, 10» ([C9]) | ux `03/02`; ui `03/01` | light/ui §1.8 | — |
| 12 | Движение: ux `06/03` 100–400 мс против handoff 100–300; ui 41 против 42 токенов; creative П1–П13 (на сайте — своё, L0 — умолчание соседей); ux № 61 | ux, ui, creative | light/ux §1.3; light/creative §2 | creative `05/01` §2 |
| 13 | Судья: переписать «другое семейство» — site (10 мест), text (правило 55, `09/03`, P7, `09/01`, `09/02`, `copy-rubric` `record_example`, LT-02…04), ux (правило 58, AC-JDG-04, AC-JDG-10, `11/04` §5), creative (рубрика `09/04`), ai-media (`11/02` п. 14, 12 рубрик) → протокол Opus | все | light/site Д.9; light/text «Поправки» п.5, Д4; light/ux §8; Р27 | пороги ai-media `thresholds.yaml` `judge` |
| 14 | Приметы и клише — один реестр; id K3-*/F-* | §2.2 п. 17 | kimi→cd §5; mapping §5 | `06/05` |
| 15 | Направления: 3–5 и 4 оси (creative) против 2–4 и 3 оси (cd) | creative `01/01`; cd `05/01` §5; `06/01` §5 | light/creative §1.7 | — |
| 16 | Тексты ux ↔ text: «Подробнее» (error в интерфейсе, warning на лендинге, X25 открыт); тире «10—15» против «–»; роль `body` вне закрытого списка; дефекты регулярок ux-12; граница голосов бренда и продукта | ux `07/*`; text `06/*`, `05/01` §2 | light/text §1.2, Д3.3 | — |
| 17 | Паспорт 3D-серии: канон blender `06/02` §6 против черновика ui `12/01` §6.2 (30° вместо 35,264°, без Neutral); T26 «постер на 1 px шире» — не внесён в ai-media | blender, ui, ai-media | light/blender §5 | — |
| 18 | Шаблон паспорта иллюстраций ui `07/02` §3 держится на негативе и seed, которых нет в polza | ui, ai-media | light/ai-media §5 | — |
| 19 | Ожидания ux от ui: минимумы, формат блока «Дизайн-система», сверка реестров (handoff §4–§5) | ux `99-raw/handoff-to-ui-research.md` | light/ux §3.2 | — |
| 20 | «Одна норма — одно место»: объединить таблицы канонов | §5.2 | — | site X §2, text X §6, creative X §2, ux X §2.1, blender X §4 |
| 21 | Одна легенда меток доказательности | §5.5 | — | — |
| 22 | Иерархия ворот «страница выше эффектов и ассетов» закрепить | контракт тройки §6 | light/site §2.4 | SITE-OUT-11 |

## 10. Финальная уборка

Правило (Р79): содержимое сохраняем, от внешнего абстрагируемся (служебные папки, процесс ресерча, соседние базы как «чужие», Kimi),
без переисследования.

| база | объём по выжимке | что особенно |
|---|---|---|
| site | Kimi ≈ 630–640 строк в 58 файлах; `[проверено]` 487, `[V:]` 158; «решение N» ≈ 129 строк; «PLAN №N» 240; служебных ссылок 558; «Поправка к `../…`» 42; средне-высокий | переписать по смыслу 4 места (`10/01` §9–§10, `01/03` §7, `09/01` §6, README сценарий 1 п. 8–9, правило 1, гипотезы живой фазы) и 10 мест про судью; `crosswalk.tsv`: 22 строки kimi — удалить, 119 путей клонов — внешние адреса [light/site §5, Д.9] |
| text | Kimi ≈ 714 строк в 62 файлах (без замера); `[проверено]` 301, `[V:]` 113; служебных 733; to-kimi 60; абсолютный путь к гайду заказчика (6); средне-высокий | сценарий 1 п. 7, `10/01` §7 и §9, `10/README`, `09/01`, `live-test-plan.md` (LT-06), правила судьи; `x-kimi-map` в 5 схемах [light/text §7] |
| creative | Kimi 735 строк (231 — пакет и проверки исполнителя); `[V:]` 142; to-kimi 142; служебных 614; 451 строка путей служебных папок; большой | шапки в каждом файле; две нумерации «решений заказчика»; `k3_allow` и проекции [light/creative §7] |
| ui | Kimi 0; ≈ 85 шапок; служебных 282; метки `[V..]` — сотни; 38 ссылок на ux | «K3» — id проверки `ui_audit.py` (стр. 977) и 45 строк отчётов: не трогать; устаревшие счётчики; README примеров с `cd /home/mm/Документы/ui-research` [light/ui §7] |
| ux | Kimi 11 строк («Kimi K2.5» в бенчмарках) — убрать, выводы оставить (Р51); 72 шапки; ≈ 160 служебных строк; `[V:]` ≈ 1 280 — оставить метками; 1 036 относительных путей | «агент B §6.4» и т. п. (277 строк) — это адреса: заменить путями, не удалять (Р51); 3 ссылки на гайд заказчика; `12/README` — счётчики [light/ux §6–§7] |
| ai-media | Kimi 0; служебных строк 1 344; `[проверено: …99-raw…]` 284 — оставить силой доказательства, путь убрать (Р55); 426 путей `phase5/runs`; `routing.yaml` — 106 путей; рецепты — 238; `[V:]` 581; крупнее text и creative | реальный продукт заказчика: `PLAN.md` п. 11–12 и 45 упоминаний папки `MS-marea` (там же лежит переносимый `loop_rife_bridge.py`) [light/ai-media §7] |
| blender | Kimi 3 (комментарии CSS «kimi T8»); служебных строк 1 672, ссылок 1 292; буквы агентов и дорожек — сотни; `[V:]` 515; 14 абсолютных путей в коде; велик | хвост README (испытание, ночь 26.09, цитаты заказчика); рецепты 13–17, `14-code-3d`, `11/06` почти построчно ссылаются на дорожки; `KIT.md:4` → `~/.claude/plans/…` [light/blender §6–§7] |
| cd | kimi 114 строк + K3 22 в 10 файлах; `[V:]` 62; ссылки в `99-raw/cache` (9 на закрытые тексты, 4 на gists) | снять раздел README «Сравнение с Kimi K3», `02/01` §11, `04/01` §2.6, T-D7; таблица замен внутри cd — `mapping` §3; 13 входящих → ux `11/03` §2.6 и creative `07/01` §6.4 [kimi→cd §6.4, §6.6] |

**Правила и ловушки:**
1. Реестр главнее сжатого слоя — выровнять «Выжимки», «Частые ошибки», чек-листы, YAML и профиль site (Р48, Р52).
2. «K3» в ui — id проверки, слепая замена по слову запрещена (Р65); «CD» в blender — дорожка испытания, не Claude Design.
3. 157 ссылок «в kimi» — клоны Hallmark, ui-ux-pro-max, claude-code-router: заменить внешними адресами с коммитом
   (`Nutlope/hallmark@13ac0ec`, `nextlevelbuilder/ui-ux-pro-max-skill@dcc40ff`, `musistudio/claude-code-router@75e9e75`), не удалять (Р65;
   `mapping` §2); руководства Anthropic из кэша kimi — внешними адресами с датой снятия.
4. «Агент B §…» в ux — адреса, заменить путями (Р51); буквы агентов в таблицах site — через соответствие в докстринге `check_links.py`.
5. Метки `[проверено: …]` — оставить силой доказательства без пути (Р55); `[V:<id> mm:ss]` — метка без пути в `91-videos` (`mapping` §2).
6. Короткие адреса «NN/MM» и «→ §» — переписывать скриптом после раскладки и проверять общим `check_links.py` (§6.9).
7. «Решение заказчика N»: у creative две нумерации — извлечь положениями; у site «PLAN №N» → «Свод поправок».
8. Id K3-*/F-* → `LOOK-*`/`HON-*` одним проходом в creative, site, text (`mapping` §5, не применено); `ALLOW_KEYS` не менять.
9. «Кварц» в creative (`art-direction-kvarts.json`) и text (`PLAN.md`) → `06-design-process/stand/S1-kvarts/` (`mapping` §7 п.7).
10. Правила «судья другого семейства» → протокол Opus (§9 п. 13).
11. URN схем с именами баз и неймспейс `org.ui-research.*` — менять синхронно или не менять.
12. Kimi в шаблоне не упоминается (Р77); выводы на данных K3 — переатрибутировать на «LLM-вёрстку 2026», не терять (kimi→cd §1.1).
13. Абсолютные пути `/home/mm/…` — в общий конфиг; пути к реальному продукту заказчика — убрать.

## 11. Калибровочный набор

Требования (Р16, Р56): ≈ 40 кадров, поровну «уровни» и «типичный брак», только свои рендеры и генерации, без Qwen 2.1 и синтетических
людей; у каждого — что иллюстрирует, оценка, на что смотреть, ссылка на рубрику; отбор — отдельным шагом. Ниже все 50 кандидатов
выжимок; site, text, ux своих визуальных результатов не имеют [light/site §2.2; light/text §10; light/ux §10].

| № | база | путь (от корня базы) | что иллюстрирует | тип | оценка | пометка |
|---|---|---|---|---|---|---|
| 1 | creative | `10-recipes/examples/l2-zveno/img/hero-d.webp` (17 КБ) | L2: постер-LCP своего рендера | уровень | ворота 0/0/0; craft 4 (один судья) | — |
| 2 | creative | `…/l2-zveno/img/hero-m.webp` (14 КБ) | L2, кадр телефона | уровень | то же | — |
| 3 | creative | `…/l2-zveno/img/st-scan.webp` (15 КБ) | L2: станция для reduce и без WebGL | уровень | ворота 0/0/0 | — |
| 4 | creative | `99-raw/experiments/J/04-light-pass/sheet-before.jpg` (314 КБ) | L2 до светового прохода | уровень ниже | craft 3, `[мнение]` | пара с № 5 |
| 5 | creative | `…/J/04-light-pass/sheet-after.jpg` (330 КБ) | L2 после светового прохода | уровень | craft 4 | — |
| 6 | creative | `…/J/04-light-pass/gates-l2-before-mob/shot_mob.jpg` (47 КБ) | H1 над белыми корпусами 3D на телефоне | брак | EG-A11Y-27: h1 1,0:1, лид 4,29:1 | — |
| 7 | creative | `99-raw/experiments/J/01-l0-sdano/shots/desk_first.jpg` (110 КБ) | L0, первый экран лидогенерации | уровень | ворота 0/0/0; `marketing_audit` S 7 → 3 → 0 | — |
| 8 | creative | `…/J/01-l0-sdano/shots/mob_first.jpg` (125 КБ) | L0 на телефоне | уровень | то же | — |
| 9 | creative | `99-raw/experiments/J/03-l1-sverka/shots/desk_first.jpg` (63 КБ) | L1, первый экран SaaS | уровень | ворота 0/0/0; 0 B, 0 S | — |
| 10 | creative | `…/J/03-l1-sverka/shots/desk_scroll_sheet.jpg` (154 КБ) | L1: кадры sticky-сцены | уровень | с оговоркой X-66 | — |
| 11 | creative | `99-raw/experiments/J/05-webkit/sheet-l1.jpg` (167 КБ) | счётчик на `@property` в WebKit стоит на 0 | брак | выявлено J2 | пара с № 12 |
| 12 | creative | `…/J/05-webkit/sheet-l1-counter-fix.jpg` (150 КБ) | исправление: стопка цифр | уровень | J2 | — |
| 13 | creative | `99-raw/experiments/F/14-holo-look/before-after-desk.jpg` (236 КБ) | «радуга ИИ» → материал | брак → правка | глазами F2; на людях `[не проверено]` | — |
| 14 | creative | `99-raw/experiments/J/02-l2-zveno/motion/station_desk_story-modules_s2.jpg` (15 КБ) | кадр станции для проверки скраба | иллюстрация проверки | сверка станций `motion_check` | — |
| 15 | ui | `99-raw/cache/screens/gen-a1-orders_1440x900.png` (113 КБ) | «дефолтный вид»: эмодзи, градиенты, тени у всех карточек | брак | замер `measure_ui`, проба маркеров; рубрикой не оценён | страницы написал агент, не генератор |
| 16 | ui | `…/gen-a2-dashboard_1440x900.png` (83 КБ) | три равные карточки, градиент | брак | то же | то же |
| 17 | ui | `…/gen-a3-settings_1440x900.png` (79 КБ) | дефолт | брак | то же | то же |
| 18 | ui | `…/gen-b1-orders_1440x900.png` (95 КБ) | пресет A по карточке стиля | уровень | 0 теней, 0 градиентов, кнопка 32 | то же |
| 19 | ui | `…/gen-b2-dashboard_1440x900.png` (78 КБ) | то же | уровень | то же | то же |
| 20 | ui | `…/gen-b3-settings_1440x900.png` (67 КБ) | то же | уровень | то же | то же |
| 21 | ai-media | `99-raw/phase5/runs/2.5-stand/mockups/F-04-B1_with_headline.jpg` (209 КБ) | hero с блоком композиции: место под заголовок | уровень | `centroid_x` 0,81–0,85; `asset_audit` — только warn; рубрика `hero-photo` | пара с № 22 |
| 22 | ai-media | `…/2.5-stand/mockups/F-04-A1_with_headline.jpg` (276 КБ) | «средний сток»: объект в центре | брак | warn `QA-COMP-CLUTTER`, `QA-COLOR-HDR` | — |
| 23 | ai-media | `…/2.5-stand/E-08-blind/scene1_frame1.png` (2,1 МБ) | фото-интерьер, Sunburst | уровень | голос заказчика вслепую | проверить на синтетических людей (Р56) |
| 24 | ai-media | `…/2.5-stand/E-08-blind/scene1_frame3.png` (1,7 МБ) | тот же бриф, Seedream 5 Pro | брак | «сразу минус» | то же |
| 25 | ai-media | `…/2.5-stand/E-08-zoom/scene2_1_nbpro_hands.jpg` (209 КБ) | предмет в руках неверен (IMG-M15) | брак | `14/04` §2.1 | руки синтетического человека — вероятно исключить (Р56) |
| 26 | ai-media | `…/2.3-series/F-01_sheet.jpg` (703 КБ) | серия: референсы + роль + блок против «только блок» | уровень и брак | ΔE палитры; рубрика `series` | — |
| 27 | ai-media | `…/2.3-series/E-12_blind_sheet.jpg` (178 КБ) | серия по эталону у 4 моделей | уровень и брак | голос вслепую | — |
| 28 | ai-media | `…/4-edits/E-15-check/E-15-S14-a-nb2-1k-1/sheet.jpg` (99 КБ) | правка «только стена»: утечка | брак | `edit_check` LEAK, ΔE00 2,21 | — |
| 29 | ai-media | `…/4-edits/E-15-check/E-15-S15-a-sd5pro-1/sheet.jpg` (129 КБ) | удаление объекта | уровень | PASS | — |
| 30 | ai-media | `…/4-edits/E-15-check/E-15-S15-mask-qwen21-1k-1/sheet.jpg` (54 КБ) | «призрак» контура, невидимый метрике | брак | PASS по метрике | **исключить: Qwen 2.1 (Р56)** |
| 31 | ai-media | `…/4-edits/H-08-check/H-08-outpaint-9x16-sunburst/sheet.jpg` (14 КБ) | аутпейнт перерисовал центр | брак | REGENERATED | — |
| 32 | ai-media | `…/S5-analysis/H-03_sheet.jpg` (168 КБ) | альфа GPT 2.5: мех годен, стекло — облако | уровень и брак | `H-03_alpha.json`; рубрика `cutout` | — |
| 33 | ai-media | `…/2.1-cyrillic/crops/flare.jpg` (117 КБ) | короткая кириллица дословно | уровень | OCR; рубрика `text-image` | пара с № 34 |
| 34 | ai-media | `…/2.1-cyrillic/crops/flux2pro.jpg` (92 КБ) | кириллица с ошибками | брак | E-02 | — |
| 35 | ai-media | `…/SC-showcase/SC-04_endpoints.jpg` (245 КБ) | видео «кадр A → кадр B»: концы совпадают | уровень | `14/04` §2.3 | — |
| 36 | blender | `15-showcase/zveno/judge/b-blender__hero-best.png` (1,44 МБ) | лучший неподвижный кадр продукта L2 (Cycles) | уровень «вау» | вслепую B > A, B > C | один судья |
| 37 | blender | `…/zveno/judge/a-code__hero.png` (2,30 МБ) | тот же кадр кодом | уровень «уверенно» | A > C, A < B | — |
| 38 | blender | `…/zveno/judge/c-hybrid__hero.png` (2,30 МБ) | гибрид | типичный брак дороги C | проиграл во всех 4 парах | — |
| 39 | blender | `15-showcase/sdano/judge/b-blender__first-screen-desk.png` (315 КБ) | услуга L0: изометрия-разрез | уровень | B > A во всех 4 парах | фигура инженера — белый макет, проверить по Р56 |
| 40 | blender | `…/sdano/judge/phase1/b-blender__plan.png` (412 КБ) | изометрия мельче и мягче вектора, подписи ≈ 8 px | брак подачи | VERDICT §4.3 | — |
| 41 | blender | `15-showcase/keyboard/judge/b-blender__first-screen-desk.png` (318 КБ) | первый экран L1, макро «Ё» | уровень якоря класса | A = B | — |
| 42 | blender | `15-showcase/velmora/judge/b-blender__f030.png` + `ai__f030.png` (1,04 + 0,43 МБ) | облёт флакона: Cycles против Kling 3 | пара уровней | 4 ничьи из 4 | кадр Kling — генерация ai-media |
| 43 | blender | `99-raw/notes/trial/FX/t1/A_studio_cycles.png` + `B_hero_cycles.png` (141 + 136 КБ) | «каталожный» свет против героя | брак → уровень | L* грани 83,9 → 95,4 | — |
| 44 | blender | `99-raw/experiments/SD/shots/sd2_c4/c_beam-off.png` + `sd3_c10/c_beam-off.png` (272 + 269 КБ) | тон серит белую бумагу | брак → правка | серого 8,7 → 0,2 % | — |
| 45 | blender | `99-raw/experiments/Z/out/c_judge_tan/cap_compare.jpg` (125 КБ) | «веер» анизотропии без TANGENT | брак → правка | правило 76 | — |
| 46 | blender | `99-raw/notes/trial/AJ/crop_kb_b_exploded_bgdiff_x6.png` (71 КБ) | плашка тени с прямой кромкой (усиление ×6) | брак, невидимый без усиления | ΔE max 3,94 → 0,87 | — |
| 47 | blender | `99-raw/notes/trial/AJ/crop_z_a_scan_x2.png` (1,14 МБ) | искры, шов, лесенка кромки кода | мелкий брак | ИИ-отсев «мелочь» | — |
| 48 | blender | `99-raw/experiments/C1/11-naive-first-try/out/sonnet/views_laptop/sheet.png` + `C1/12-protocol-objects/out/views_laptop/sheet.png` (120 + 154 КБ) | первая попытка против протокола | брак → уровень | регрессия: `dims_mismatch`, `floating_part` | — |
| 49 | blender | `99-raw/experiments/C1/11-naive-first-try/out/haiku/views_tree/sheet.png` (131 КБ) | объект вне кадра | брак | `not_in_frame` | — |
| 50 | blender | `99-raw/experiments/J/02-pairwise-judge/pairs_order1.png` (476 КБ) | 4 пары «протокол против первой попытки» | калибровка судьи | Opus выбрал «богаче» в 3 из 4 — все брак | — |

Сверх лимита, по выжимкам: ai-media `S5-analysis/VAR_sheet_1.jpg` (узнаваемые AirPods — чужой дизайн), `5-vector/blind-icons.jpg`, снимок
демо-лендинга (рендеры Blender, не генерации), кадр стыка петли из `MS-marea` (см. §6.12 п. 19); blender — 41 WebP галерей приёмов с
разметкой `gallery*.json`, `poster_blender.png` («каталожный» свет), `C1/11 …/opus/views_mug/sheet.png` (кружка 2,2 м — брак, невидимый
на листе); ui — отрисовать 7 эталонных экранов в двух темах (готовых PNG нет). Чужие сайты и якоря класса не берутся.
Баланс по колонке «тип» (вывод): «уровней» 22, «брака» 17, смешанных (пары, «брак → правка», листы уровня и брака, калибровка судьи)
11. После исключения № 30 и, вероятно, № 23–25 «брака» останется 14 — нужен добор из ai-media и blender сверх лимита.

## 12. Открытые вопросы

| № | вопрос | источник | рекомендация (вывод) | блокирует |
|---|---|---|---|---|
| 1 | Craft-запрет `CLAUDE.md` §3: «craft легален только в слое дизайна»? Владелец визуальных решений? | Ф1-05 §7 в. 1; PLAN «Риски» | да, по прецеденту «FSD-имена легальны только в FSD» (Ф1-05 §4.2); владелец — владелец продукта, агент — «допущением» | blueprint |
| 2 | Род продукта: колонка у поверхности (Ф1-05 §3) или поле vision `product-kind` (ux-верх §3.5)? | Ф1-05 §7 в. 4 | колонка рода у поверхности + производная сводка в vision (enum ux admin / client / mixed + роды site) | blueprint |
| 3 | Слой страницы для сайта и лендинга: отдельный или внутри дизайна; «один или два слоя» (тексты, маркетинг, воронки) | Ф1-05 §4.3, §7 в. 5; Р24 | отдельный слой страницы (бриф, карта, план, факты, copy deck) на месте screens для сайта; воронки — там же, конверсией уже владеет site | blueprint |
| 4 | «Просто сайт → дизайн»: что пропускать, нужен ли interface лендингу | Ф1-05 §7 в. 6 | через `_phase-jump.md`; interface лендингу не нужен; минимум — vision-минимум, поверхность с родом, site-brief | blueprint |
| 5 | Участие клиента через `/entrypoint-for-business` (бриф, референсы, выбор направлений, утверждение) | Ф1-05 §7 в. 14 | да для брифа, мудборда и выбора направления; утверждает владелец продукта | blueprint |
| 6 | Пара `design-audit` — да или нет; «≤ 7 → стоп» — правило или ориентир | PLAN «Открытые»; Ф1-05 §7 в. 13 | да — третья семья аудита (артефакты + макет по постоянной просьбе); ≤ 7 — ориентир `[спорно]` для Claude | структура скилла |
| 7 | Заморозка базы | STATE «Ждём»; PLAN Ф0 | сразу после удаления kimi: манифест sha256, пересчёт `count_tokens.py`, освежение дайджестов | перенос |
| 8 | Удаление kimi (Р68) | Р68; STATE | после просмотра `06` заказчиком и докопирования `shot_v3.py`, `lang_check.py`, `data/` (на диске их пока нет) | заморозка |
| 9 | Форма capability (реестр ≤ 10 колонок + паспорт, обязательные поля, двустороннее покрытие) | ux-верх §8 в. 3; Р23 | записать решение оркестратора в DECISIONS и показать заказчику (как требует Р23) | модель слоя |
| 10 | Представления объекта — у глоссария или в screens; конвенции «одно на продукт» — слой проекта или ДС | ux-низ §4, §6 г п.2 | представления — рядом с глоссарием; конвенции — одной записью в проекте, ДС исполняет | модель слоя |
| 11 | Аудит живых и собранных страниц (`page_anatomy`, `geo_probe --render`, `ia_probe`, axe, `copy_extract`) — в рамках? | light/site §7 в. 3 | офлайн-ядро обязательно; живой аудит — ветка «после сборки SSR» | манифест утилит |
| 12 | Рынок: РФ по умолчанию или юрисдикция профилем брифа | light/site §7 в. 4 | профиль брифа, умолчание РФ (право покрыто только для РФ и частично ЕС) | — |
| 13 | Параметры этапа макета: темы по умолчанию, бюджет раундов, основной канал просмотра, что публиковать в приватные артефакты | PLAN «Открытые» | канал — редактор claude.ai (Р14), `kit` — проверки; ≤ 3 раундов на экран; публиковать только разрешённое заказчиком | blueprint |
| 14 | Ассеты ai-media: шаблоны `pages/` (7,6 МБ) и демо-лендинг без ассетов не открываются | light/ai-media §8 п.4 | не брать: генераций там нет; шаблоны — как код и описание | — |
| 15 | `P/04/routerai_models.json` (840 КБ) в исключении Р54 | §3.1 (оценка синтезатора) | не переносить — пересоздавать снимком (0 ₽), как кэш каталогов | перенос |
| 16 | Исходники дорожек blender 13–17: какой объём | Р57; light/blender §3.2 | только финальные исходники (`fonarik.js`, `zstudio.py`, `build_pages.py`, `rc_vote_tally.py` и т. п.), без версий v1–v6 и `out/` | перенос |
| 17 | creative `J/04/src/scene.js` (бандл уже по Р41) | light/creative §3.2 | взять (44 КБ): бандл без исходника не правится, на него ссылается blender | перенос |
| 18 | HDRI blender `E/_assets/studio_small_09_1k.hdr` для `gltf_diff.py` | light/blender §3.2 | взять (CC0, мал) или сделать параметром | перенос |
| 19 | site: 3 уникальных примера v0 (школа, услуги города, конференция) | light/site §2.1 | не брать до пилотов (есть 3 полных проекта v1) | — |
| 20 | site: `crosswalk.tsv` — источник правды или сборщик | light/site Д.7 | источник правды, как text с `copy-slots.yaml`; строки text пересобрать на сверке | перенос |
| 21 | ui: сводный глоссарий или 13 глоссариев папок; листинги `09/04` §4–§6 при DTCG-источнике; `examples/audit` | light/ui §3.1, §11 | один сводный + §14; листинги убрать (выпуск — генератором); `audit` — один отчёт как образец формата | перенос |
| 22 | ux: облегчённый YAML без `source_raw` | light/ux §11 в. 2 | да, при перегенерации (Р49) | — |
| 23 | blender: отчёт X §4 и §1; правила многоагентного стенда 94–101, `slot_run`, `atlas_collect`, генераторы карты и глоссария | light/blender §3 | X §4 — нормой (как ux, Р50); остальное — не в скилл, `slot_run` — если Ф3 введёт параллельных агентов | перенос |
| 24 | Развилка «Blender / гибрид» без второго тура (Р58) | light/blender §9 п.1 | в workflow — по VERDICT §3 с меткой «один судья»; тур — на пилоте | blueprint |
| 25 | Новые id `LOOK-*` / `HON-*` | `mapping` §5 | применить одним проходом при уборке | уборка |
| 26 | Порядок этапов (набросок заказчика против базы) и место текстов | WORKFLOW-INPUTS §2–3; §8.1 | решить в blueprint; предложение базы — L0–L2 и смысл в брифе, ассеты после ДС и структуры | blueprint |
| 27 | Локальный рендер `.dc.html` (для `#N` и `diffshots` на артбордах) | cd `05/01` §7; `mapping` §7 п.2 | тест на пилоте (T-D) | пилоты |
| 28 | Перевод базы на английский | Р9 (не утверждено) | не переводить: экономия ≈ 12 % не окупает | — |
| 29 | Сокращение описаний скиллов шаблона под листинг | STATE; PLAN «Риски»; Ф1-05 §7 в. 15 | да, до сборки скилла | структура скилла |
| 30 | `PLAN.md` Ф3–Ф8 устарел (§6.12 п. 26) | — | переписать по итогам обсуждения §13 | — |

## 13. Предложение порядка шагов для Ф3 (для обсуждения)

Опора: Р67 (сверка — отдельный шаг до сборки), Р78–Р80 (перенос как есть → структура → уборка в конце), Р75 (агенты по одному
цепочкой), PLAN Ф3 п. 1–7.

1. **Ф3.0 Предусловия.** Просмотр `06-design-process` заказчиком → докопирование (`shot_v3.py`, `lang_check.py`, `data/`) → удаление kimi в
   корзину (Р68) → заморозка базы: манифест sha256, пересчёт токенов, освежение дайджестов creative, ux, ai-media, blender. Параллельно,
   отдельным шагом, — отбор калибровочного набора из 50 кандидатов §11 (Р16).
2. **Ф3.1 Решения-блокеры с заказчиком:** §12 № 1–6 (craft, род продукта, слой страницы, «просто сайт», клиент, `design-audit`); записать
   форму capability (№ 9). Без них blueprint не собрать.
3. **Ф3.2 Сверка баз (Р67)** — по узлам, агентами цепочкой: (а) тройка и словари id (§9 п. 1, 4); (б) ворота и бюджеты, WEB-01/WEB-04
   (п. 2–3); (в) единый глоссарий (п. 5); (г) компоненты и состояния (п. 6–8); (д) судья, рубрики и метки (п. 13, 20, 21); (е) ширины,
   цели, отступы, движение, тексты (п. 9–12, 16). Выход — таблица «одна норма — одно место» и сводный реестр расхождений; он же вход
   уборки (Р48).
4. **Ф3.3 Карта знаний** (Р17–Р18): узлы §2.2 → карта `kb/` с межбазовыми связями, маршруты «этап → файлы → проверка», прогрессивная
   загрузка «README → Выжимка → раздел» (устройство файлов site и других баз уже это даёт).
5. **Ф3.4 Blueprint workflow:** ветки сайт / лендинг / SaaS; этапы с контрактами входа и выхода по стыкам §8; единый вход холста и ДС
   (Р64); L0–L2 рано; тексты; ассеты; проверка по постоянной просьбе; вход с любого места (детектор состояния).
6. **Ф3.5 Модель слоя проекта:** UX-дельта §7 + слой страницы для сайта; правка `CLAUDE.md` и ≈ 35 общих файлов (Ф1-05 §4.4).
7. **Ф3.6 Структура скилла и бюджеты:** `SKILL.md`-роутер, `workflow/`, `kb/`, `schemas/`, `scripts/` с общим конфигом путей, агенты
   (консультант по базе, критик свежим контекстом), `design-audit`; бюджет листинга и рабочих сессий (≤ 150–250 тыс. токенов).
8. **Ф3.7 Спецификация переноса и пилотов:** манифест §3, утилиты §4, скрипт установки окружения, смоук-тесты; 3 пилота (лендинг,
   многостраничник, SaaS) со стендом `06/06` и тестами T-1…T-6; переписать `PLAN.md` Ф4–Ф8.

Дальше — вне Ф3: перенос скриптом (Ф4) → структура в шаблоне → ужатие и реализация (Ф5–Ф6) → финальная уборка по §10 (Р79) → пилоты (Ф7).
