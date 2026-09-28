# Z7a — соседние исполнители и аудиты: продукт и interface: отчёт Ф7

Зона выполнена целиком: 14 правок в четырёх скиллах, новых файлов нет. Против коммита до зоны (`323fad4`) — +2 969 / −2 467
строк (все 14 файлов переписаны и перенесены под ширину 120, как новые файлы шаблона; прирост нетто — ≈ +350 строк,
было 3 698, стало 4 045). Файлы других зон не тронуты.

## 1. Файлы

Пути — от `.claude/skills/`.

| файл | новый / правка | строк | что внутри (разделы) |
|---|---|---|---|
| `project-deep-dive/SKILL.md` | правка | 327 | описание 570 знаков; мультипроект и заведение (реестр + семь плоских таблиц, `object.md`, `action.md`); вышестоящий вход (`trace`); точки входа (10 kind, 9 фаз); «Что делать сразу» с шагом сверки с каноном; сводка (текущая фаза по девяти фазам, «не нужна» у сайта); фазы проработки и следующий шаг по маршруту; режимы; стиль вопросов («допущение» vision); память (`object`, `action`, `_phase-jump.md`); связи — структурные и смысловые; `draft → stable`; research; завершение; границы (облик, файлы уровня продукта) |
| `project-deep-dive/references/phases.md` | правка | 390 | «Девять фаз»; «Фазы и этапы маршрута» (таблица фаза ↔ этап `phases.md` дизайна); «Какие фазы нужны продукту» (кабинет · сайт и лендинг · мобильное и бот · смешанный); карта фаз 1–9 (`objects` — новая, четвёртая); сводка фаз для UI; перепрыгивание (`_phase-jump.md`, цена) |
| `project-deep-dive/references/field-checklists.md` | правка | 330 | vision (наборы, таблица разделов «что должно быть · формулирует», оси, пометки, порядок); user + «Постура»; surface + `web-kind`; object (объекты, атрибуты, представления); action; capability (реестр, паспорт таблицей, урезание); boundary; integration; constraint; market; универсальные нюансы |
| `project-deep-dive/references/draft-stable.md` | правка | 106 | пять пунктов с особым по kind (vision, user, surface, object, action, capability, integration …); повышение (vision — после `cohesion`); понижение; stable при приведении к канону; когда нельзя пройти; stable на draft |
| `project-deep-dive/references/workflow-patterns.md` | правка | 263 | режимы A (примеры раундов), B (объекты, действия, постура, род), C; стиль вопросов (таблицы опций и Other, «допущение» — только vision); stub (объект и действие со списка функций); удаление (поверхность, объект и действие, пользователь); **«Привести к канону»** (когда, пакет, механические и смысловые правки, «пустое — не прочерк», статусы, порядок, не выдумывать) |
| `project-audit/SKILL.md` | правка | 174 | описание 538 знаков; состав слоя; точки входа (+ `object`, `action`); что делать при запуске (набор vision, чтения за пределами слоя); тяжесть; формат отчёта с разделом матрицы; `last-report.md` (категории R-VS … R-MX, YAML примера парсится); границы |
| `project-audit/references/rules.md` | правка | 930 | состав слоя, что аудит читает кроме слоя, словарь правил (набор vision, маршрут приложения, интерактивная поверхность, «пусто»); R-STRUCT-001…010; R-SEM-001…012; R-COV-001…005; **R-VS-001…008**; **R-RL-001…002**; **R-GL-001…006**; **R-CAP-001…010**; **матрица и R-MX-001…004**; что не делает |
| `interface-deep-dive/SKILL.md` | правка | 237 | описание 554 знака; восемь kind; какая поверхность получает interface (B8); выбор проекта и поверхности (пикер без `landing` и `site`, шаг «Род»); точки входа (+ `scenario`); **порядок работы на поверхности** (сценарии хабов первыми → первый вход дизайна кабинета → экраны; `_phase-jump.md`); что делать сразу (сверка с каноном); сводка (хабы без сценария первыми); режимы; стиль вопросов; память; зеркала; `draft → stable`; stub; удаление; завершение; границы (проход по облику) |
| `interface-deep-dive/references/field-checklists.md` | правка | 278 | who (постура — у пользователя); stage; situation (19 колонок, «Поля шага, которые решают экран»: `frequency`, `refusals`); **scenario**; zone (`order`, `object`, ИА); block (достижимость); ux-substrate; data-items (`object`) |
| `interface-deep-dive/references/draft-stable.md` | правка | 81 | пять пунктов: обязательное (частота, отказы, мета и разделы сценария, `order` и `object`), ссылки (внутри поверхности и на объект, возможность сценария), зеркала, тест, blocker; алгоритм; чего не делать |
| `interface-deep-dive/references/workflow-patterns.md` | правка | 194 | режим A и «Сценарий — отдельно» (порядок ux 05/02 §1.1); B (рассказ о задаче → сценарий); C; стиль вопросов; **«Привести к канону»** (сначала продукт, механика, «пустое — не прочерк», смысловые, папка у сайта или лендинга, статусы, порядок) |
| `interface-deep-dive/references/project-context.md` | правка | 113 | какая поверхность получает interface; маппинг с колонкой «проверка ссылки» (who ↔ user и постура, situation ↔ capability, scenario ↔ capability и статусы объектов, zone и data-items ↔ object); когда показывать связь (who, situation, scenario, zone и data-items); пустой продукт → `_phase-jump.md`; сквозная сверка `/cross-audit --quick` |
| `interface-audit/SKILL.md` | правка | 156 | описание 587 знаков; восемь файлов, что аудит читает кроме папки; выбор; точки входа; что делать (R-SURF, обход блоков); тяжесть; формат отчёта; `last-report.md` (R-SC, R-IA, R-CAP; YAML примера парсится); что не делать |
| `interface-audit/references/rules.md` | правка | 466 | категории (+ R-SC, R-IA, R-CAP); R-SURF-001…003; R-XSURF-001; R-STRUCT-001…010; R-MIRROR-001…002; R-SEM-001…006; R-COV-001…007; **R-SC-001…005**; **R-IA-001…005**; **R-CAP-001** |

## 2. Решения и действия

| id | где реализовано (файл § раздел) | примечание |
|---|---|---|
| A1 (`web-kind`) | `project-deep-dive/references/phases.md` § 3. `surface` («Род веб-поверхности»); `field-checklists.md` § surface; `SKILL.md` § Сводка (`web` без рода → `surface`); `project-audit/references/rules.md` R-STRUCT-003 (перечень), R-STRUCT-009 (род не по типу), R-STRUCT-010 (папки по роду); `interface-deep-dive/SKILL.md` § Какая поверхность, § Выбор (шаг «Род»); `interface-audit/references/rules.md` R-SURF-002, R-SURF-003 | значения `landing` · `site` · `app` · `—` |
| A2 (минимум над слоем страницы) | `project-deep-dive/references/phases.md` § Какие фазы нужны продукту («Сайт и лендинг»: минимум для слоя страницы), § 3 (логичные переходы); `SKILL.md` § Сводка («не нужна»), § Фазы проработки (следующий шаг `/design-deep-dive`); `field-checklists.md` § vision (минимум); `project-audit/references/rules.md` словарь «Набор vision», R-STRUCT-004 | `objects`, `capability` у сайта — по желанию |
| B8 (не для рода `landing`, `site`) | `interface-deep-dive/SKILL.md` § Какая поверхность получает interface, § Выбор (пикер и «Род»), § Границы; `references/workflow-patterns.md` § Привести к канону («Папка у сайта или лендинга»); `references/project-context.md` § Какая поверхность; `interface-audit/references/rules.md` R-SURF-002 (исключение), R-SURF-003 (error); `project-audit/references/rules.md` R-STRUCT-010 | |
| F1 (vision) | `project-deep-dive/references/phases.md` § 1. `discovery` (набор, разделы, «Допущение»), § 9. `cohesion` (`MVP`, сводки); `field-checklists.md` § vision; `draft-stable.md` п. 1 (vision), § Повышение; `workflow-patterns.md` § Стиль вопросов; `SKILL.md` § Стиль вопросов, § Границы; `project-audit/references/rules.md` R-STRUCT-004, R-VS-001…008, R-SEM-008 (+ `Positioning`) | полный набор / минимум — по поверхностям |
| F2 (постура) | `project-deep-dive/references/phases.md` § 2. `user`, § 3 (строки по поверхности, разделение приложений); `field-checklists.md` § user → «Постура»; `draft-stable.md` п. 1 (user); `project-audit/references/rules.md` R-RL-001, R-RL-002, R-STRUCT-003; `interface-deep-dive/references/project-context.md` § Маппинг (who берёт постуру через `who.users`), `field-checklists.md` § who | |
| F3 (capability) | `project-deep-dive/references/phases.md` § 5. `capability`; `field-checklists.md` § capability (реестр, паспорт, урезание); `draft-stable.md` п. 1; `workflow-patterns.md` § A (пример раунда); `SKILL.md` § Вышестоящий вход (`trace`); `project-audit/references/rules.md` R-CAP-001…010, R-STRUCT-001/003, R-SEM-003 (урезание) | `trace` вместо отдельных колонок работ и гипотез |
| F4 (объекты и действия; данные → объект) | `project-deep-dive/references/phases.md` § 4. `objects`; `field-checklists.md` § object, § action; `draft-stable.md` п. 1; `SKILL.md` (kind, заведение, память); `workflow-patterns.md` § Stub-сущности, § Удаление; `project-audit/references/rules.md` R-GL-001…006, матрица R-MX-001…004; `interface-deep-dive/references/field-checklists.md` § data-items, § zone; `project-context.md` § Маппинг; `interface-audit/references/rules.md` R-STRUCT-009 | матрица — вычисляемый раздел отчёта |
| F5 (kind `scenario`) | `interface-deep-dive/SKILL.md` (восемь kind, порядок, первый заход); `references/field-checklists.md` § scenario; `draft-stable.md` пп. 1–2; `workflow-patterns.md` § Сценарий — отдельно, § B; `project-context.md` § Заведение `scenario`; `interface-audit/references/rules.md` R-SC-001…005, R-STRUCT-003/007/008; `project-audit/references/rules.md` R-CAP-006 (хаб без сценария), R-CAP-008 (шаг защиты) | |
| F6 (ИА-поля зон) | `interface-deep-dive/references/field-checklists.md` § zone («Информационная архитектура», `order`, `object`); `workflow-patterns.md` § Стиль вопросов; `interface-audit/references/rules.md` R-IA-001…005, R-STRUCT-008 (`order`), R-STRUCT-009 (`zone.object`), R-STRUCT-010 (зоны навигации в обходе) | числа — адресом ux 02/01 §3.2–§3.3 |
| F12 (порядок; фаза `objects`) | `project-deep-dive/references/phases.md` § Фазы и этапы маршрута (девять фаз, `objects` между `surface` и `capability`); `SKILL.md` § Точки входа (перечень фаз), § Фазы проработки, § Сводка; `interface-deep-dive/SKILL.md` § Порядок работы (сценарии хабов первыми), § Сводка | порядок совпадает с `design-deep-dive/references/phases.md` §1 «SaaS и кабинет» |
| F13 («Привести к канону») | `project-deep-dive/references/workflow-patterns.md` § Привести к канону; `SKILL.md` § Что делать сразу, п. 4; `draft-stable.md` § Понижение; `interface-deep-dive/references/workflow-patterns.md` § Привести к канону; `SKILL.md` § Что делать сразу, п. 4; `draft-stable.md` § Чего не делать; аудиты — «список работ» в § Границы / § Что не делать | таблица «прежнее → текущее» в скиллы не перенесена: правила — в терминах текущей формы |
| F14 (сторона interface) | `interface-deep-dive/references/field-checklists.md` § situation («Поля шага, которые решают экран»), § block («Достижимость»); `draft-stable.md` пп. 1–2; `interface-audit/references/rules.md` R-SEM-003 (`frequency` при stable), R-SEM-006 (`refusals`, warning@stable), R-STRUCT-008 (перечни и ключи), R-STRUCT-010 (достижимость, error@stable), R-SEM-005 (сужен до draft) | |
| F9 / TX-31 (голос продукта) | `project-deep-dive/references/phases.md` § 1 («Голос»); `field-checklists.md` § vision (строка `Voice`); `SKILL.md` § Заведение нового проекта, § Завершение п. 3, § Границы; `project-audit/references/rules.md` R-VS-001 (ссылка на профиль продукта при полном наборе), R-VS-008 (ссылки; подсказка у мобильного и бота) | действие ZONES.tsv TX-31 — место `project-deep-dive/references/{phases,field-checklists}.md` |
| A4 (следующий шаг после сценариев — бриф на вид) | `interface-deep-dive/SKILL.md` § Порядок работы, § Завершение п. 3; `project-deep-dive/references/phases.md` § Какие фазы нужны продукту, § 9; `SKILL.md` § Фазы проработки | «первый вход дизайна кабинета», меток «Д1», «Д2» нет |
| Вход с середины (T3 §3) | `interface-deep-dive/SKILL.md` § Порядок работы, § Память (`…/interface/<surface>/_phase-jump.md`); `project-context.md` § Если продуктовый слой пуст; `project-deep-dive/references/phases.md` § Перепрыгивание | |
| H2 (описания) | четыре `SKILL.md`: 570, 538, 554, 587 знаков | главный случай первой фразой, категории намерений |
| H7 (проход) | `interface-deep-dive/SKILL.md` — описание («облик сюда не пишется»), вступление, § Границы («макет собирает слой дизайна `design/`»); `interface-audit/references/rules.md` R-SEM-002 («маркеры облика», «облика в interface нет, он живёт в слое дизайна `design/`») | «craft» — 0, фраза о ручной сборке wireframe и hi-fi — 0 |

## 3. Отступления от спецификации

1. **Id правил — сквозные внутри категории, а не номера кандидатов.** Кандидаты журнала (VS-01 …) в текст шаблона не
   переносятся, а номера с пропусками (R-CAP-006 нет, R-CAP-008 есть) путали бы читателя без журнала. Соответствие:
   - `/project-audit`: VS-01…06 → R-VS-001…006; **сверх кандидатов** R-VS-007 (сводки vision против источника —
     критерий 9 формы) и R-VS-008 (ссылки vision в пустоту — строка «проверка» таблицы F1, TX-31); RL-01, RL-02 →
     R-RL-001, 002; GL-01…05 → R-GL-001…005, **сверх** R-GL-006 (ссылки глоссария: атрибут, `ref:`, представление,
     `action.objects`, `creates`/`deletes`); CAP-01…05 → R-CAP-001…005, CAP-07 → R-CAP-006, CAP-09 → 007, CAP-10 → 008,
     CAP-11 → 009, CAP-12 → 010; MX-01…04 → R-MX-001…004; состав vision → R-STRUCT-004 (расширен по набору); `web-kind`
     → R-STRUCT-003 (перечень) и **новый** R-STRUCT-009 (род не по типу: `web` без рода, род у не-`web`).
   - `/interface-audit`: SC-01…05 → R-SC-001…005; IA-01…05 → R-IA-001…005; CAP-08 → R-CAP-001; `frequency` →
     R-SEM-003 (обязателен при stable) + R-STRUCT-008 (перечень); `refusals` → R-SEM-006 + R-STRUCT-008 (ключи);
     достижимость блоков → R-STRUCT-010; `data-items.object` (и `zone.object`) → R-STRUCT-009; B8 → R-SURF-003.
     R-STRUCT-008 переименован в «значение вне перечня» (раньше — только `ux-substrate.type`); R-SEM-005 сужен до
     draft-блоков, у stable недостижимость — ошибка R-STRUCT-010.
2. **Тяжести, которых T3 не называл,** — по кандидатам ux-верх §3.3: VS-05 — warning и только у stable; VS-04 —
   error@stable, у draft ссылка в пустоту — warning; MX-01 — error@stable (форма `object.md`: `creates`, `deletes`
   обязательны при stable; T3 писал просто error); R-RL-001 у draft — warning.
3. **Покрытие вниз (R-CAP-006) — только когда `interface/<surface>/` существует;** до начала interface — одна подсказка
   на поверхность. Иначе каждая stable-возможность была бы ошибкой ещё до сценариев, а маршрут требует stable хабов как
   вход сценариев (`phases.md` дизайна, этап `scenarios`).
4. **R-STRUCT-010 в `/project-audit`** (папки слоёв против реестра, типа и рода) — сверх T3 §4.4: держит обещание форм
   зоны 2 («`/project-audit` ловит файлы и папки для поверхностей вне реестра», `surface.md`, README § Связи).
   Пересекается с `design-audit` R-SURF-004/005 (зона 6) и `interface-audit` R-SURF-001/003 — каждый аудит сообщает со
   своей стороны. Вариант: сузить R-STRUCT-010 до «папка вне реестра», а род оставить аудитам слоёв — решает
   оркестратор.
5. **«Пустое — не прочерк» при приведении к канону.** T3 §4.5: «новые колонки — `—` в draft». Но в `refusals`, `order`,
   `object` зон и данных, `web-kind` веб-поверхности, `statuses` объекта прочерк — решение («отказов нет», «вне
   навигации», «не вокруг объекта», «не веб») — поставленный механически, он молча отвечал бы за владельца. В обоих
   «Привести к канону» такие ячейки остаются пустыми до ответа; прочерк ставится, только когда следует из других полей
   (`web-kind: —` у не-`web`). Аудиты считают прочерк в этих полях заполненным (`interface-audit` R-SEM-003, словарь
   «Пусто» `project-audit`). В формах (таблица «Форма ячеек» README project и interface) пустая ячейка не описана —
   см. §6.
6. **`slug` в `interface-deep-dive` больше не спрашивается через Other,** а выводится из `name`: прежний текст спорил с
   `.claude/rules/naming.md`.
7. **Отказы ситуации экрана (R-SEM-006) читают поле `situations` экранов** той же поверхности: иначе «ситуацию экрана»
   не определить (зеркало `situation.block` — не то же, что экран).
8. **Ширина 120 и целые код-спаны** во всех 14 файлах — диф большой, но смысловые правки видны по разделам §1.
9. **Имена полей — по формам зоны 2:** тип приложения в `Name` (кандидат писал `product-kind`), цель доступности в
   `Devices and accessibility` (кандидат — `a11y-target`).

## 4. Для следующих зон

- **Z7b (экраны, FSD).** Образец «Привести к канону» — `project-deep-dive/references/workflow-patterns.md § Привести к
  канону` и `interface-deep-dive/references/workflow-patterns.md § Привести к канону`: когда (сверка при запуске, пакет
  при многих расхождениях) · сначала слой выше · механические правки после одного подтверждения с различием · «пустое
  — не прочерк» · смысловые — владельцу раундами режима C · stable не понижается, находки аудита — список работ ·
  порядок по зависимостям; шаг 4 «Сверить … с каноном» в «Что делать сразу при запуске» обоих `SKILL.md`. У экранов
  прочерк-решение — `object: —` (с решением в `map.md`), `key-action: —`, `url-state: —`, `main-task: —` у `service`.
  `interface-audit` R-SEM-006 читает поле `situations` экранов `screens/<surface>/screens/<slug>/index.md` — имя поля
  не менять. Interface stable → следующий шаг `/screen-deep-dive` (`interface-deep-dive/SKILL.md § Порядок работы`).
- **Z8 (оркестраторы, `/cross-audit`).** `entrypoint/references/state-model.md`: в ветку `project/` — kind `object`,
  `action` (`…/project/<kind>/<slug>.md`; атрибуты и представления — в заметке объекта, постура — пользователя,
  паспорт и урезание — возможности); `project/_phase-jump.md` пишет фазы `project-deep-dive` (`discovery` … `cohesion`,
  соответствие этапам — колонка «ведёт» `phases.md` §1 дизайна); в ветку `interface/<surface>/` — kind `scenario` и
  `_phase-jump.md`. `/cross-audit`: углы `capability-job`, `capability-hypothesis` читают `capability.trace`
  (`job:<slug>`, `hypothesis:<slug>`) — `cross-audit/references/angles.md` (строки ≈ 1127–1165) пишет отдельные поля
  работ и гипотез; `entrypoint/references/routing.md:135` — то же. `interface-deep-dive/references/project-context.md`
  ссылается на `/cross-audit --quick` (углы `user-who`, `capability-situation`, `surface-zone`) и на
  `/cross-audit <project-slug> <lens>`. Роутер: `/project-deep-dive --new`, фазы и их имена — `project-deep-dive/SKILL.md
  § Точки входа`.
- **Z9 (описания).** 570 + 538 + 554 + 587 = 2 249 знаков.
- **Оркестратор.** Пикеры проектов в скиллах шаблона исключают только `_template`, а `docs/projects/infrastructure/` —
  ИТ-периметр, не проект (так исключает только `design-deep-dive`): кандидат в отдельный проход по всем пикерам.
  README interface (§ Связи) называет рёбра `data-items → object`, `zone → object` смысловыми — `interface-audit`
  R-STRUCT-009 добавляет проверку существования по T3 §4.4; строку README можно уточнить (файл зоны 2).

## 5. Проверка

- `refcheck.py --strict` по 14 файлам — битых 0, следов журнала 0. Все строки файлов тронуты переносом, поэтому ложные
  срабатывания прежних строк (`capability/`, `../entrypoint/state/`, `ajtbd/job` без `.md`, «было/стало» в описании
  заметки) переписаны.
- Ссылки вида «`файл.md § раздел`», которые `refcheck` по голому имени не сверяет, проверены скриптом по заголовкам форм
  `docs/projects/_template/{project,interface,screens}/` — все разделы есть.
- Код-спаны не разорваны переносом (скрипт); ширина прозы ≤ 120 знаков; структура списков и заголовков после
  перепаковки совпадает с исходной (сравнение скриптом, текст без пробелов — идентичен).
- YAML: frontmatter четырёх `SKILL.md` и примеры frontmatter `last-report.md` в обоих аудитах — `yaml.safe_load` без
  ошибок. Описания — 570 / 538 / 554 / 587 знаков.
- Фаз `project-deep-dive` — девять, новая — `objects`, между `surface` и `capability`; порядок совпадает с
  `design-deep-dive/references/phases.md` §1 и §4 (`vision` ← `discovery`, `roles` ← `user`, `surfaces` ← `surface`,
  `objects` ← `objects`, `capability` ← `capability` и `cohesion`).
- Поиск по файлам зоны: «craft», wireframe и hi-fi, «вручную» о макете, «Д1», «Д2», «(позиция)», «Committed»,
  «Tailwind», «8 фаз», отдельные колонки работ и гипотез возможности — 0.
- Id правил уникальны в каждом аудите (скрипт): `/project-audit` — R-STRUCT-001…010, R-SEM-001…012, R-COV-001…005,
  R-VS-001…008, R-RL-001…002, R-GL-001…006, R-CAP-001…010, R-MX-001…004; `/interface-audit` — R-SURF-001…003,
  R-XSURF-001, R-STRUCT-001…010, R-MIRROR-001…002, R-SEM-001…006, R-COV-001…007, R-SC-001…005, R-IA-001…005,
  R-CAP-001. Внешних ссылок на прежние id этих аудитов в шаблоне нет (поиск).
- Глазами: forward-only (без «было / стало», имён фаз сборки, адресов журнала); примеры помечены иллюстрацией;
  формулировки — за владельцами, скилл спрашивает; данных проекта нет; углы `/cross-audit` и разделы соседних файлов,
  на которые ссылаюсь, существуют.

## 6. Открыто и не прочитано

**Открыто:**

- Пересечение R-STRUCT-010 с `design-audit` и `interface-audit` (§3 п. 4) — оркестратор.
- Матрица «пользователь × объект × действие»: вид действия («создать · смотреть · изменить · удалить») аудит относит
  чтением — колонки класса в `action.md` нет. Если пилот SaaS покажет разнобой, колонку вида можно добавить в форму
  словаря действий (зона 2 или пилот).
- Пороги ИА (глубина, число корневых разделов) — адресом ux 02/01 §3.2–§3.3, машинного файла нет; утилита проверки
  (Ф8) могла бы держать их числами.
- «Пустое — не прочерк»: таблицы «Форма ячеек» README `project/` и `interface/` не называют пустую ячейку как маркер
  «ждёт ответа» — строку можно добавить (файлы зоны 2).
- Пикеры проектов без исключения `infrastructure` — во всех скиллах, кроме `design-deep-dive` (§4).
- Первая проверка правил аудитов — пилоты (узкие аудиты на шаблоне без данных не прогоняются, `PLAN.md` §6).

**Не прочитано:** T2a, T2b; T4 — кроме вступления, H2, H7; T3 — §5–§7; `phase-4/nodes/*`; база — адресно (все адреса
сверены `refcheck`), целиком — ux 02/01 §3, ux 01/04 §6.8, ux 13/04 «Частые ошибки», ux 01/03 §4 и §6; `cross-audit`
— только поиск по углам; файлы Z7b и Z8 — только поиск по стыкам.

## 7. Запись для CHAIN

```
## 10. Z7a — соседние исполнители и аудиты: продукт и interface (28.09, ≈ <мин — по уведомлению> мин, контекст ≈ 300 тыс. токенов по оценке агента)
- Сделано: 14 правок, новых нет (+2 969 / −2 467 строк против `323fad4`; 4 045 строк, все файлы под ширину 120):
  `project-deep-dive` — SKILL (570 знаков), `phases.md` (девять фаз, `objects` — четвёртая), `field-checklists.md`,
  `draft-stable.md`, `workflow-patterns.md` («Привести к канону»); `project-audit` — SKILL (538), `rules.md` (R-VS,
  R-RL, R-GL, R-CAP, R-MX, R-STRUCT-009/010); `interface-deep-dive` — SKILL (554), `field-checklists.md` (scenario,
  ИА-поля, частота и отказы, `data-items.object`), `draft-stable.md`, `workflow-patterns.md` («Привести к канону»),
  `project-context.md`; `interface-audit` — SKILL (587), `rules.md` (R-SC, R-IA, R-CAP, R-SURF-003, R-STRUCT-009/010,
  R-SEM-006). Решения A1, A2, B8, F1–F6, F9 (TX-31), F12, F13, F14, H2, H7 и действие TX-31 — с местом (отчёт §2).
- Отступления (решает оркестратор): id правил — сквозные по категориям, соответствие кандидатам — отчёт §3 п. 1;
  сверх кандидатов R-VS-007, R-VS-008, R-GL-006, R-STRUCT-009/010 (`/project-audit`); тяжести, не названные T3, — по
  ux-верх; покрытие вниз — только при начатом interface; R-STRUCT-010 пересекается с `design-audit` R-SURF-004/005;
  «пустое — не прочерк» против «новые колонки — `—`» T3 §4.5; `slug` в interface выводится из имени; R-SEM-006 читает
  `situations` экранов.
- Стыки: Z7b — образец «Привести к канону» (разделы обоих `workflow-patterns.md`, шаг 4 запуска), прочерк-решения экрана,
  поле `situations`; Z8 — kind `object`, `action`, `scenario` и `_phase-jump.md` в `state-model.md`, `trace` в углах
  `capability-job`, `capability-hypothesis` и в `routing.md`; Z9 — 2 249 знаков на четыре описания.
- Открыто: пересечение R-STRUCT-010; вид действия в матрице — чтением; пороги ИА — адресом; пустая ячейка в таблицах
  «Форма ячеек» (зона 2); пикеры без исключения `infrastructure` во всех скиллах, кроме дизайна.
- Не прочитано: T2a, T2b; T4 вне вступления, H2, H7; T3 §5–§7; база — адресно; файлы Z7b, Z8 — поиском.
```
