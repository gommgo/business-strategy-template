# Т-код-creative — строки зон кода в базе `creative`

Коммит начала — `1e0cd2a`. Первый заход (03.10) оборвал лимит модели на чтении источников, своих правок тогда не было;
работа сделана 06.10 за один заход. Правки — 8 пакетов точных замен (`$DDD_HOME/out/f10/Т-код-creative/patches/`,
76 замен) в 21 статье `kb/creative/**/*.md` и 7 рецептах `10-recipes/recipes/04…10-*.recipe.yaml`; 28 файлов,
+120 / −74 строки. Пути ниже — от `kb/creative/`, утилиты — от корня скилла. Git — только чтение.

Итог по строкам (32): внесено — 26, уже так — 3, по коду иначе — 1, не внесено — 2.

## Строки и итог

| источник (отчёт, пункт) | файл и место | итог |
|---|---|---|
| К8а: LCP-элемент, CRV-AL-09 | `09-ai-execution-evaluation/02-motion-spec-storyboard-handoff.md`: п. 7 выжимки, §1.6, CRV-MS-05, шаблон MOTION.md | внесено; та же норма и в строке `lcp: is-lcp` таблицы §1.3 (там стояло «только transform» — по коду MS-09 иначе) |
| К8а: CRV-AL-09 и исключения свойств | `01-creative-direction/03-ambition-levels.md`: строка CRV-AL-09 §2.3; таблица исключений — §3.2 | внесено; таблицы в статье не было — поставлена в §3.2 из `ambition-levels.yaml#property_exceptions` |
| К8а: поля `directions[].bans`, `notes`, `treatment_variants[]` | `01-creative-direction/02-art-direction-document.md` §2 | внесено (строка `directions` и новая строка `treatment_variants`, с пометкой v1) |
| К8а: `viewer`; сводка `page.treatment` | `09-…/01-presentation-spec-and-block-treatments.md` §2.1 (строка `viewer`), §2.4 (TR-07, TR-08) | внесено |
| К8а: LV-03 | `06-effects-catalog/01-effects-catalog.md` §1.2 | внесено (строкой под таблицей уровней) |
| К8б: 56 → 59, три приёма, классы движения, длина закрепления | `06-effects-catalog/01-effects-catalog.md`: шапка, §1.2 (строка L0), §5.1, §7, §10, §12.6, §12.7 | внесено: `light-sweep` — пункт §7 (наведение, семейство `image`), `expanding-columns` и `overlay-viewer` — §12.6 и §12.7; тексты — из записей `effects.yaml`, норм сверх данных нет |
| К8б: длина петли | `06-effects-catalog/02-hero-video-background.md:42` | внесено (`thresholds.yaml#thresholds.video`, `loop_len_min_s`, `loop_len_max_s`) |
| К8б: `motion.properties` | `06-effects-catalog/README.md`, строка `effects.yaml` | внесено |
| К8б: Science Gothic и Tektur | `04-visual-language/01-display-typography.md` §4.2 | внесено |
| К8б: поля варианта, `routes-scene`, `grid-quiet`, роль `calm` | `09-…/01-presentation-spec-and-block-treatments.md` §3.1, §3.2 | внесено |
| К8б: числа закрепления → токены | `09-…/02-motion-spec-storyboard-handoff.md` §1.4 | внесено |
| К8б: надзаголовок ceil(N/3), `caps-share` | `08-uniqueness-anti-slop/01-cliche-policy.md` §4.3 | внесено |
| К8б: прежняя утилита и исполнитель, `compat.mockup_checks` | `08-…/01-cliche-policy.md` (§4.1, §4.2, §6.1, CRV-CL-12, CRV-CL-14), `08-…/02-uniqueness-and-variation.md` §5.1; `08-…/README.md` | внесено по коду (`mockup_checks.py`); README папки — уже так; `compat.` в статьях не встречается |
| К9: `line_height_css` | `04-visual-language/README.md`, строка токенов | внесено |
| К4в: шкала MS-06, MS-07 | `09-…/02-motion-spec-storyboard-handoff.md` §1.3 | внесено |
| К4в: описания `refs.tokens`, `$defs.token-ref` | `09-…/motion-spec.schema.json` | уже так (внесла зона данных) |
| К12: внешний `flock … browser.lock` | `10-recipes/examples/README.md:15, 23` | внесено: обёртка снята, объяснение — «утилита берёт замок браузера сама» |
| К12: «путь машины» | `02-references-moodboards/02-refs-client-and-library.md:26, 154, 155`; `06-effects-catalog/03-effects-lab-method.md:87`; `PLAN.md:726, 748` | внесено: `$DDD_HOME/locks/browser.lock`, `$DDD_HOME/locks/browser-refs.lock`, Node — `node_env()` в `kbpaths.py` |
| Д-creative-1: сборка `build_effects.py`, `entries.py` | `06-effects-catalog/README.md`, `03-effects-lab-method.md` (чек-лист), `README.md:362, 478, 544`, `CONTRADICTIONS.md:125, 234, 530`, `PLAN.md:714` | внесено: каталог правится по месту; проверка — своя схема, `registry_check.py`, `spec_check.py levels --check`. `PLAN.md` «Как расширять базу» — живая процедура (на неё ссылается `README.md`) |
| Д-creative-1: «контракт §3 п.6 + поля E» | `06-effects-catalog/01-effects-catalog.md` §1.1 | внесено |
| Д-creative-1: `check_refs.py` | `README.md:362` | внесено (статусы клише — `registry_check.py`) |
| Д-creative-1: `id_map` | `06-effects-catalog/README.md:5`, `01-effects-catalog.md` §1.1, `09-…/01-presentation-spec…` [S12], `CONTRADICTIONS.md:495` | внесено |
| Д-creative-1: поле `src` замеров | — | уже так (статьи поле не описывают) |
| Д-creative-2: `kimi_crosswalk` в описании папки | `01-creative-direction/README.md:15` | внесено |
| Д-creative-2: `kimi_crosswalk` | `01-creative-direction/01-concept-and-directions.md` §7 п. 4 | внесено: бриф холста, поля — ключ `x-canvas-map` схемы art-direction v1 |
| Д-creative-2: `handoff.kimi.*` | `01-creative-direction/02-art-direction-document.md` §4.3 (строки 129 и 138), §2 (строка `handoff`) | внесено: у 129 снят `handoff.kimi`, строка 138 снята (поля нет в данных) |
| Д-creative-2: `site_validate.py` и `treatment.v0` | `09-…/01-presentation-spec…` §2.6 и п. 14 выжимки | по коду иначе: `site_validate.py` грузит treatment v1, `page-plan` ссылается на `:1` — текст приведён к коду |
| Д-creative-2: исходник сцены в `99-raw` | `10-recipes/examples/README.md:74–75`, `10-recipes/03-product-launch-l2.md:110` | не внесено: перенос исходника — открытый вопрос (Д-creative-2, вопрос 2) |
| Д-creative-2: `sites.csv` | `03-live-sites-measured/README.md` | не внесено: готовой строки нет, а файла нет — решать владельцу |
| Д-creative-2: заметка Oswald | `04-visual-language/cyrillic-display-fonts.yaml` | уже так (машинный файл, правила зона данных) |
| Задание (в): журнал `changes`, проекция для исполнителя | `09-…/03-verification-loop-and-gates.md:134`; `00-glossary/glossary.md:93` («`brief.yaml` входа холста») | внесено; `sync_point` и `x-kimi-projection` статьи не называют |
| Д-creative-2 «Оркестратору»: рецепты 04…10 | строка 1 семи рецептов; `04-…:10`, `06-…:10` | внесено; `recipe_check.py` — рецептов 10: error 0, warning 0 |

## Расхождения строк с кодом

- `site_validate.py` грузит `creative/09-ai-execution-evaluation/treatment.schema.json`, `page-plan.schema.json` ссылается на
  `urn:app-design:creative:treatment:1`, подмены `:0` → v1 в `spec_check.py` нет. Абзац §2.6 говорил о v0 и «двух правках у site».
- `k3_checks.py` в скилле нет. Утилита макета — `scripts/claude-design/mockup_checks.py`: ключи `--allow` берутся из
  `kb/common/tells.yaml#checks`. Строка 08/02 §5.1 приведена к данным `tells.yaml`: 23 проверки `LOOK-*`, у 20 есть ключ `--allow`.
  Тот же переход сделан в `01-creative-direction/02-art-direction-document.md` §4.3 и §5.3.
- Схемой `effects.yaml` не проверяет ни одна утилита скилла: `accept.py` сверяет схемы только с метасхемой,
  `registry_check.py` проверяет статусы клише, `spec_check.py levels --check` — уровни и LV-03. В текстах стоит «своя схема»
  без имени утилиты.
- В статье 01/03 таблицы исключений свойств не было, в 06/01 нет подразделов §10.1 и §10.3. Таблица поставлена в §3.2,
  классы движения дописаны в первый и третий пункты §10 (`mask-reveal`, `text-mask-media`, по `motion.kind`).
- Числа каталога в `README.md` базы и в README папки 06 взяты из `effects.yaml`: 59 записей (L0 19, L1 31, L2 9).
- Команда в `10-recipes/examples/README.md:23` зовёт `../../scripts/creative/idle_probe.py`, а такой утилиты в скилле нет.
  Обёртка снята, сама команда осталась.

## Проверки

- `spec_check.py --selftest` — OK; `spec_check.py levels --check` — error 0, warning 0, info 0; `registry_check.py` — ошибок 0,
  расхождений 0; `smoke.py --only scripts/creative` — PASS 21, FAIL 0, XFAIL 0, XPASS 1; `recipe_check.py` — 10 рецептов, 0 / 0.
- `sync_check.py` — генераторы OK 17, FAIL 0; копий расходится 0. Блоки `x-effect-levels` не тронуты.
- `normcheck.py --base HEAD --list-lost` (21 статья) — 245 находок НОРМА (потеряно 74, появилось 170, изменено 1). Все — замены
  из строк выше: числа 56, 150, 400, 6–12 с уступили токенам и данным, пропали снятые имена (`id_map`, `build_effects.py`,
  `k3_checks.py`, `handoff.kimi.*`), пути машины и флаги обёртки. На строках с вырезанным потерь 0.
- `refcheck.py` (21 статья) — в изменённых строках 9 битых путей; все они есть в тех же строках HEAD (`effect_bench.py`,
  `99-raw/…`, `idle_probe.py`, `07-stack-implementation/stack.yaml` от папки статьи). Новых битых нет. Путь машины в статьях
  creative — 0 (было 5).
- `canon_check.py` — код 0 (ошибок 0); `mapcheck.py kb/INDEX.md` — код 0; `git diff --check` — чисто.
- `accept.py --base HEAD --masks-file` (28 файлов зоны): разбор OK (7), следы OK (0). Строка «ссылки» — 9 прежних путей,
  названных выше. Строка «маски» — FAIL из-за 613 файлов других зон в общем дереве.

## Соседям

- Машинный файл вне списка: в `01-creative-direction/drafts-for-site/treatment.v0.schema.json:25` поле `x-effect-ids-note`
  ведёт к снятому `id_map` (оркестратору, зоне Д-creative-2).
- Уборке текстов: здесь остались проекции в пакет прежнего исполнителя макета — `01-creative-direction/02-art-direction-document.md`
  §4.3 (заголовок и таблица «→ kimi») и строка `motion_system` §2 («шкала kimi»), `09-…/01-presentation-spec…` §6.1–6.2,
  `08-…/01-cliche-policy.md` §6.2 «Блок для K3» и `08-…/README.md:7`. Остальное: `CONTRADICTIONS.md:126` («пересобран»),
  `PLAN.md:654` (список опытных утилит), буква A в `10-recipes/recipes/08-…:10`.
- Утилит нет в `scripts/`, но тексты их называют: `orch_check.py` (`README.md:544`, `PLAN.md` «Новый файл»), `fill_tables.py`
  (`06-effects-catalog/01-effects-catalog.md` §1.3), `idle_probe.py` (`README.md:362`, `10-recipes/examples/README.md:23`).

## Вопросы

1. Нужна ли утилита, которая проверяет `effects.yaml` его схемой (`registry_check.py` или `spec_check.py`)? Сейчас тексты
   говорят «своя схема», а запустить такую проверку нечем.
2. Строки с `idle_probe.py` снять или вернуть утилиту в `scripts/creative/`?
3. Проекции в пакет прежнего исполнителя (01/02 §4.3, 09/01 §6) переписать на бриф холста по `x-canvas-map` или снять целиком?

## Доработка по решениям оркестратора

Пакет `patches/p9-decisions.py` — 24 замены в 10 файлах. Вместе с основной правкой это 24 статьи и 7 рецептов, 31 файл,
+135 / −89 строк.

1. **Сверка каталога приёмов — по коду.** Слова «проверка — своя схема» сняты во всех шести местах: README папки 06,
   `01-effects-catalog.md` §1.1, чек-лист `03-effects-lab-method.md`, `README.md` (две строки), `PLAN.md` «Эффект». Теперь
   там сказано: схема `effects.schema.json` описывает поля каталога; сверку ведут `registry_check.py` и
   `spec_check.py levels --check`; схема проходит метасхему при приёмке правки (`scripts/maint/accept.py`). Где строка
   короткая (чек-лист, таблица `README.md`), назван только шаг сверки. Новой утилиты нет — пункт в список развития.
2. **Утилит нет — упоминание снято вместе с фразой.**
   - `idle_probe.py`: метод остался словами — «зонд покоя: два снимка счётчика вызовов WebGL в одной паузе». Места:
     `README.md:133`, `10-recipes/README.md:29`, `10-recipes/00-how-to-use.md:61`, `00-glossary/glossary.md:396`,
     `10-recipes/03-product-launch-l2.md:199, 219, 227`. Строка команды в `10-recipes/examples/README.md` снята целиком.
     Из таблицы утилит `README.md:362` убраны имя и путь; ушёл и путь `99-raw/experiments/F/07-yaml/`, который держался на
     снятых `build_effects.py` и `check_refs.py`.
   - `orch_check.py`: `README.md:348, 360, 545`, `PLAN.md:712, 763, 786`; где был шаг приёмки, осталась проверка
     `check_links.py`.
   - `fill_tables.py`: `06-effects-catalog/01-effects-catalog.md` §1.3 — «таблицы разделов — из замеров лаборатории».
   - В списке утилит `PLAN.md:654` сняты все три отсутствующих имени: `build_effects.py`, `check_refs.py`, `idle_probe.py`.
3. **Проекции в пакет прежнего исполнителя** (01/02 §4.3, 09/01 §6, 08/01 §6.2) не тронуты — их снимет уборка текстов.

Проверки после доработки:
- `refcheck.py` (24 статьи): в изменённых строках новых битых нет. 18 находок в этих строках есть и в HEAD тех же файлов
  (`extract_for_audit.py`, `ctx_watch.py`, пути `99-raw/…`, `drawElements/drawArrays`).
- `normcheck.py --base HEAD --list-lost`: 287 находок НОРМА (потеряно 108, появилось 178, изменено 1); на строках с
  вырезанным потерь 0. Новые потери — снятые имена `idle_probe.py`, `orch_check.py`, `fill_tables.py` с числами их
  прогонов (120, 123 файла). `check_links.py` в таблице `README.md:360` записан путём `../../scripts/maint/check_links.py`.
- `smoke.py --only scripts/creative`: PASS 21, FAIL 0, XPASS 1; `git diff --check` — чисто.
- Других утилит, которых тоже нет в `scripts/`, это решение не касалось: `extract_for_audit.py` и `ctx_watch.py`
  (`README.md:360`, `PLAN.md:763`) остались.
