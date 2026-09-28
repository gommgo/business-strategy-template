# Z7b — соседние исполнители и аудиты: экраны, FSD, мобильное, бот, сервисы и домены: отчёт Ф7

Пути файлов в таблицах — от `.claude/skills/`. Счёт строк диффа — против `a12b475` (база до зоны; черновики зоны
оркестратор коммитил в `46976b6` и `47baa24`). Файлы правлены по месту: ширина строк каждого файла сохранена, дифф
показывает смысловые правки.

## 1. Файлы

Итого: 23 правки, новых файлов нет; +2 485 / −614 строк; 8 097 строк в файлах зоны.

| файл | новый / правка | строк | что внутри (разделы) |
|---|---|---|---|
| `screen-deep-dive/SKILL.md` | правка, +182 / −81 | 552 | описание (589 знаков); вступление (четыре kind, `map.md`, `texts.md`, облик не выдумывается); «Выбор поверхности» (экраны — у `web` рода `app`, `admin`, `desktop`, `embed`; `landing`, `site` → `/design-deep-dive`; `web` без рода → `/project-deep-dive`); «Точки входа» (+ `map`, `texts`); «Что делать сразу при запуске» (канон слоя, продуктовый слой, шаг 4 — сверка с каноном и пакет «Привести к канону»); «Сводка состояния» (подсчёт `map.md` и строк `texts.md`, порядок этапа «экраны», кандидаты, пример — иллюстрация); «Стиль вопросов» (перечни `type`, `access`, `url-state`, лендмарк, `level`, `source`; не больше четырёх опций); «Нотация дерева»; новый раздел «Карта экранов и тексты интерфейса»; «Контракт `draft → stable`» (набор состояний, лендмарк, свод `map.md`); «Удаление» (пересборка свода, строки-сироты реестра); «Завершение сессии» (следующий шаг по порядку этапа); «Границы» (облик — `design/`, макет — по контракту генерации, FSD, оси контекста, продукт и interface не авторятся) |
| `screen-deep-dive/references/tree-notation.md` | правка, +142 / −60 | 149 | «Грамматика» (блок — дословно README screens, «при расхождении прав канон»; корни, атрибут в одном месте; разбор — утилита `tree`, пока её нет — разборщиком YAML и чтением); «Компонент — тип закрытого словаря» (`types`, `parts`, `aka`, расширение — через слой дизайна блокером); «Опции по месту в дереве»; «Атрибуты — закрытый список» (таблица «узел — атрибут — как выбирается»; `variant`, `size` не пишутся); «Данные, тексты, иконки» (`data:`, ключ текста `{раздел}.{экран}.{элемент}.{роль}`, роль по `text_roles`, литерал только в `draft`); «Пример» (дерево блока формы, YAML парсится) |
| `screen-deep-dive/references/field-checklists.md` | правка, +392 / −117 | 579 | шапка (канон — форма; пустое — не прочерк); flow (сценарий interface как источник, master-detail, ширины приёмки, триггер из `action.md`); screen (поля `type`, `object`, `main-task`, `key-action`, `zone`, `route`, `params`, `access`, `url-state`, `indexed`, переходы `{to, trigger, keeps, back}`; обязательный набор состояний, приоритет, частные правила; заголовок, `## Доступность`); block (`source`, контракты `form`, `collection`, `tiles`, состояния блока со своим источником); shell (лендмарки, навигация по числу разделов, один узел помощи, `responsive` с `sm`, «Состояния приложения»); новые разделы `map.md` (свод не авторится; «Переход», «События», «Конвенции», «Узкий экран», «Решения») и `texts.md` (ключ, роль, статусы `assumed` → `checked` → `approved`, колонки языков) |
| `screen-deep-dive/references/draft-stable.md` | правка, +73 / −18 | 203 | контракт распространён на `map.md`; ссылки в продуктовый слой, реестр текстов, `ui:`; зеркало свода `map.md`; п. 6 «Дерево в теле полное» (грамматика, набор состояний, один заголовок, `source: own`, контракты, лендмарк, состояния приложения, свод); утилиты по имени; два новых пункта «Что НЕ делать» |
| `screen-deep-dive/references/raw-input.md` | правка, +31 / −14 | 165 | шаг 1; таблица кандидатов (навигация, тип экрана, состояния, состояния приложения, тексты — строками `assumed`); stub'ы («пустое — не прочерк»); порядок углубления («Переход» первым); anti-patterns (имена компонентов со скриншота, облик) |
| `screen-deep-dive/references/workflow-patterns.md` | правка, +188 / −50 | 388 | вступление; A — шаги и примеры раундов (screen: тип, объект, главная задача, маршрут; block: источник и контракты); B; C; таблицы стиля; новые разделы «Тексты интерфейса» (этап `ui-texts`: черновик `assumed`, проверки, `approved` словом владельца; правка с холста кабинета — вход с середины по `../design-deep-dive/references/claude-design.md § 5`) и «Привести к канону» (утилита `normalize`; механические правки текущими терминами; «Пустое — не прочерк»; смысловые — аналитику; статусы; порядок по зависимостям) |
| `screen-deep-dive/references/project-context.md` | правка, +65 / −76 | 117 | связь с продуктом — полями экрана по slug (проверяет `/screen-audit`, смысл — `/cross-audit`); «Маппинг» (таблица поле → сущность продукта); вопросы этапа к vision (`MVP`, `Devices and accessibility`), постура, голос продукта; пустой продуктовый слой → заметка `…/screens/<surface>/_phase-jump.md`; углы `surface-screen`, `surface-design` |
| `screen-deep-dive/references/assets-policy.md` | правка, +9 / −7 | 146 | вступление (сырьё для экранов, не мудборд облика); «Связь с кодом» без ручной сборки макета |
| `screen-audit/SKILL.md` | правка, +70 / −29 | 296 | описание (577); вступление; точки входа `map`, `texts`; «Что аудит читает» (`map.md`, `texts.md`, продуктовый слой, словарь компонентов и расширения; утилиты `tree`, `states`, `screen_map` — пока чтением); запуск; уровни тяжести; «Stable как ужесточение»; пример отчёта (иллюстрация; R-STRUCT-021, R-SEM-011); категории отчёта |
| `screen-audit/references/rules.md` | правка, +871 / −54 | 1 433 | категории + R-RT, R-CP, R-TX, R-AX, R-MB; абзац о словарях и чтении; R-SURF-002 сужен, R-SURF-003 новый; R-STRUCT-001/002/006/007/008/009 обновлены, R-STRUCT-020…025 новые; R-SEM-001/005/007 обновлены, R-SEM-011 переписан, R-SEM-014/015 новые; R-COV-003 переписан; R-RT-001…009, R-CP-001…012, R-TX-001…007, R-AX-001…006, R-MB-001…008; 99 правил |
| `fsd-deep-dive/SKILL.md` | правка, +58 / −33 | 249 | описание (556); вступление (потребитель — только `<org>/frontend`); «Выбор проекта и поверхности» (`web` рода `app`, `admin`, `desktop`, `embed`); запуск (сверка с каноном); режимы; стиль; `draft → stable` п. 2; «Границы» (облик — токены ДС; у сайта и лендинга карты нет) |
| `fsd-deep-dive/references/workflow-patterns.md` | правка, +70 / −5 | 141 | A — вывод полей из экранов (`pages.path` = `route`, `guard` = `access`, `shared-ui.ui-type`, сценарии `shared-api` по наборам состояний, локали `shared-lib` = колонки `texts.md`); B, шаг 4; новый раздел «Привести к канону» |
| `fsd-deep-dive/references/draft-stable.md` | правка, +12 / −3 | 56 | стыки в чек-листе; потребитель карты — только `<org>/frontend` |
| `fsd-audit/SKILL.md` | правка, +44 / −13 | 125 | описание (583); структура (карта у `landing`, `site` — error; колонка `ui-type`); ссылки (`path` ≠ `route` — error, экран без page — hint, `guard` ≠ `access` — error, `ui-type` вне словаря — error); семантика (облик, сценарии `shared-api` по наборам, локали `shared-lib`); строка потребителя |
| `mobile-deep-dive/references/field-checklists.md` | правка, +63 / −17 | 179 | новый раздел «Стыки со словарями продукта» (состояния ↔ S-id, тексты и роли, облик из токенов ДС, паритет и «Урезание»); screens (набор через таблицу соответствия, `empty` у экрана с коллекцией); shell (политика темы, отложенные правки); permissions, entry-points (роль `push`), system-actions, shared-api (сценарии по ключам), shared-lib (роли) |
| `mobile-deep-dive/SKILL.md` | правка, +5 / −3 | 344 | описание (564); «Границы» — облик из токенов ДС |
| `mobile-deep-dive/references/interface-context.md` | правка, +2 / −1 | 45 | строка об облике |
| `mobile-audit/references/rules.md` | правка, +62 / −0 | 517 | R-STRUCT-005 — норма; R-INV-013 «экран с коллекцией без `empty`», R-INV-014 «набор экрана неполон по таблице соответствия», R-INV-015 «офлайн-правки без строки «Отложенные правки»», R-SEM-011 «`not-found` у объекта в архиве», R-SEM-012 «состояние приложения в `screens.states`» |
| `telegram-bot-flow-deep-dive/references/field-checklists.md` | правка, +74 / −13 | 449 | новый раздел «Стыки со словарями продукта»; window (тело, anti-patterns, роли сообщений, `escalate`, getter — `empty` и `fallback`, ошибки — роль); use-case (`Outputs` — «передано человеку», `Errors`); command (шаг 8 — команда пути к человеку); notification (шаг 7 — уведомление оператору) |
| `telegram-bot-flow-audit/references/rules.md` | правка, +59 / −9 | 1 160 | R-DATA-001 (рекомендация); R-DATA-002 «ключ getter без `fallback` или коллекция без `empty`»; R-STRUCT-023 «невалидный `escalate`»; R-COV-009 «нет пути к человеку» |
| `service-deep-dive/references/draft-stable.md` | правка, +2 / −2 | 151 | «У слоя сервисов и доменов скрипта-валидатора нет — проверка ручная…» |
| `domain-deep-dive/SKILL.md` | правка, +6 / −5 | 405 | описание (585); та же фраза в двух местах |
| `domain-deep-dive/references/draft-stable.md` | правка, +5 / −4 | 248 | та же фраза; ссылка stable на draft-соседа — подсказка «докопать соседа», не блокер |

## 2. Решения и действия

| id | где реализовано (файл § раздел) | примечание |
|---|---|---|
| A4 | `screen-deep-dive/SKILL.md § Сводка состояния` п. 4 (восемь шагов этапа «экраны» ux 13/04 §13–§24, исключения, затем тексты интерфейса, второй вход дизайна, FSD; маршрут — `../design-deep-dive/references/phases.md § 1`), п. 5 (первый незакрытый шаг — первый кандидат), пример; `§ Завершение сессии` п. 3 | шаги — `screens/README.md § Воркфлоу`, таблица `phases.md` §4 |
| A6 | мобильное: `mobile-deep-dive/references/field-checklists.md § Стыки со словарями продукта`, § screens, § shell, § permissions, § entry-points, § system-actions, § shared-api, § shared-lib; `mobile-audit/references/rules.md` R-STRUCT-005, R-INV-013…015, R-SEM-011, R-SEM-012. Бот: `telegram-bot-flow-deep-dive/references/field-checklists.md § Стыки со словарями продукта`, § window, § use-case, § command, § notification; `telegram-bot-flow-audit/references/rules.md` R-DATA-001, R-DATA-002, R-STRUCT-023, R-COV-009 | ключи обоих слоёв не переименованы — только добавления |
| B8 | `fsd-deep-dive/SKILL.md` (вступление, «Выбор проекта и поверхности», «Границы»), `fsd-deep-dive/references/draft-stable.md`, `fsd-audit/SKILL.md` (структура, строка потребителя); `screen-deep-dive/SKILL.md § Выбор поверхности`; `screen-audit/references/rules.md` R-SURF-003 | `<org>/site` из строк потребителя убран |
| D5 | `screen-deep-dive/SKILL.md § Карта экранов и тексты интерфейса`, точка входа `texts`; `references/workflow-patterns.md § Тексты интерфейса`; `references/field-checklists.md § texts.md`; `references/tree-notation.md § Данные, тексты, иконки`; `references/draft-stable.md` п. 6; `screen-audit` R-TX-001…007; роли по полю — `mobile-deep-dive/references/field-checklists.md`, `telegram-bot-flow-deep-dive/references/field-checklists.md` | черновик — «допущением», утверждает владелец продукта |
| F6 | `screen-deep-dive/references/field-checklists.md § screen`, `§ map.md`; `SKILL.md` (точка входа `map`, «Карта экранов и тексты интерфейса», «Удаление»); `references/draft-stable.md` (свод `map.md`); `screen-audit` R-RT-001…009, R-COV-003, R-STRUCT-006 | |
| F7 | `screen-deep-dive/references/tree-notation.md` (все разделы); `SKILL.md § Нотация дерева`; `field-checklists.md` § screen, § block, § shell (ключи, набор, приоритет, частные правила); `draft-stable.md` п. 6; `screen-audit` R-STRUCT-020…022, R-SEM-001, R-SEM-005, R-SEM-011, R-SEM-014, R-SEM-015 | |
| F10 | `fsd-deep-dive/references/workflow-patterns.md § A. С аналитикой`, `§ Привести к канону`; `fsd-deep-dive/references/draft-stable.md`; `fsd-deep-dive/SKILL.md § Границы`; `fsd-audit/SKILL.md § Проверки` (`source-refs`, `semantics`) | |
| F13 | `screen-deep-dive/SKILL.md § Что делать сразу при запуске` шаг 4, `references/workflow-patterns.md § Привести к канону`; `fsd-deep-dive/SKILL.md § Что делать сразу при запуске`, `references/workflow-patterns.md § Привести к канону` | образец — Z7a |
| F14 | `screen-deep-dive/references/field-checklists.md § block`; `workflow-patterns.md § A` (пример раунда block); `project-context.md § Маппинг`; `screen-audit` R-CP-001…012, R-STRUCT-024 | |
| F15 | `screen-deep-dive/references/field-checklists.md § shell`, `§ screen`, `§ map.md`; `SKILL.md § Сводка состояния` (шаги 7–8); `screen-audit` R-AX-001…006, R-MB-001…008, R-STRUCT-025 | |
| H2 | описания: `screen-deep-dive` 589, `screen-audit` 577, `fsd-deep-dive` 556, `fsd-audit` 583, `mobile-deep-dive` 564, `domain-deep-dive` 585 | сумма 3 454; главный случай первой фразой, без фраз-триггеров |
| H7 | облик вместо «craft» и без ручной сборки wireframe и hi-fi: `screen-deep-dive/SKILL.md § Границы` («макет экранов собирает слой дизайна по контракту генерации»), `references/tree-notation.md`, `references/assets-policy.md § Связь с кодом`, `fsd-deep-dive/SKILL.md § Границы`, `mobile-deep-dive/SKILL.md § Границы`, `references/interface-context.md`; «скрипта-валидатора нет, проверка ручная»: `service-deep-dive/references/draft-stable.md`, `domain-deep-dive/SKILL.md` (два места), `domain-deep-dive/references/draft-stable.md` | запрет облика в экранах, FSD и mobile сохранён по смыслу |
| ST-16 (Ф6, Ф4) | как F6 | кандидаты RT-01…08 — таблица ниже |
| ST-17 (Ф6) | как A4 | |
| ST-19 (Ф6, Ф4) | `telegram-bot-flow-deep-dive/references/field-checklists.md` § window (`escalate` у `text-input`), § use-case (исход «передано человеку»), § command, § notification; `telegram-bot-flow-audit` R-COV-009 (свободный ввод или ИИ — warning, кнопочный бот — hint, неполный путь — hint), R-STRUCT-023 | порог — README бота § Путь к человеку |
| TX-45 (Ф6, Ф4) | как D5 (часть в скиллах) | строка `CLAUDE.md` §3 — зона 4 |
| GL-09 | `screen-deep-dive/references/tree-notation.md § Компонент — тип закрытого словаря` | |
| CM-01 | там же (имя — по `purpose` и `group`, опции — типы группы); `screen-audit` R-STRUCT-021 (`ui:` вне словаря — error, подсказка типа по `aka`) | |
| CM-05 | там же: словарь `components.yaml` + расширение проекта (`extensions` карты решений `design/system.yaml`); расширение заводит слой дизайна — `**blocker**` и `/design-deep-dive <project-slug>` | |
| CM-07 | `tree-notation.md` (имена из `aka` не пишутся: `Navbar` → `TopBar`, `Search` → `SearchInput`; пример); `field-checklists.md`, `raw-input.md` (anti-pattern) | |
| CM-10 | `fsd-deep-dive/references/workflow-patterns.md` (колонка `ui-type` из дерева экранов), `fsd-audit/SKILL.md` (тип существует — error) | |
| CM-12 | `tree-notation.md § Атрибуты — закрытый список`; `screen-audit` R-SEM-014 (warning), R-SEM-001 (`variant`, `size` — облик) | |
| ST-05 | `screen-deep-dive/references/field-checklists.md § screen` (набор по типу и условиям, «не применимо: причина»), `screen-audit` R-SEM-011 (warning, error@stable); `mobile-deep-dive/references/field-checklists.md § screens`, `mobile-audit` R-INV-013 (error), R-INV-014 | тяжесть mobile — §3 п. 8 |
| ST-24 | `telegram-bot-flow-deep-dive/references/field-checklists.md § window` (getter: `empty` у коллекции, `fallback` у каждого ключа); `telegram-bot-flow-audit` R-DATA-002 (error; `fallback`, описывающий пустоту, — warning; пример нормы описывает `empty`), R-DATA-001 | |

Кандидаты журнала и пункты T3 §4.4 → правила `/screen-audit` (номера кандидатов в текст скилла не перенесены):

| кандидат (ux-низ, T3 §4.4) | правило |
|---|---|
| дерево не парсится; `ui:` вне словаря; атрибут вне списка; ключ `states` вне словаря | R-STRUCT-020; R-STRUCT-021; R-SEM-014; R-STRUCT-022 |
| обязательный набор не покрыт (замещает R-SEM-011); `source: own` без S07 и S13 | R-SEM-011 (у блока `source: own` — набор `loading-initial`, `error-load`, у коллекции шире) |
| текст: ключ в реестре; роль; литерал при `stable`; строки stable-экрана не ниже `checked` | R-TX-001; R-TX-002; R-TX-003; R-TX-004 (ещё R-TX-005…007 — форма реестра, сироты, синонимы и числа) |
| свод `map.md` = экраны | R-RT-008 |
| RT-01, RT-02, RT-03, RT-04, RT-05, RT-06, RT-07, RT-08 | R-RT-001, R-COV-003, R-RT-002, R-RT-003, R-RT-004, R-RT-005, R-RT-006, R-RT-007 |
| CP-01…CP-10, CP-12 | R-CP-001…R-CP-010, R-CP-011 |
| CP-11 | R-STRUCT-021 (тип словаря; «одна потребность — один тип» — `tree-notation.md`) + `design-audit` R-COV-005 (компонент ДС на тип) |
| AX-01; AX-02; AX-03…AX-06 | R-AX-001 и R-AX-002; `design-audit` R-COV-005 (`keyboard` у расширения; у типов словаря — `components.yaml`); R-AX-003…R-AX-006 |
| AX-07 | R-STRUCT-025 (истечение сессии — «Состояния приложения» основного каркаса) + R-AX-003 (повторный ввод, вставка, лимит времени — конвенции `map.md`) |
| MB-01…MB-08 | R-MB-001…R-MB-008 |

## 3. Отступления от спецификации

1. **Грамматика дерева в двух местах.** `tree-notation.md § Грамматика` повторяет блок README screens дословно (сверено
   скриптом байт в байт) и говорит «при расхождении прав канон» — так требуют T3 F7 и бриф («одно и то же»). Это спорит
   со стандартом SKILL-MAP §7 «каждая информация — в одном месте». Варианты: (а) оставить копию и добавить сверку блока
   в `static_check.py`; (б) заменить блок ссылкой на README и оставить в скилле только «как вести». Сделано (а) без
   сверки в скрипте — решает оркестратор.
2. **Id `/screen-audit` переписаны по месту.** R-SEM-011 — «обязательный набор состояний не покрыт» (T3: «замещает
   R-SEM-011»); R-COV-003 «screen недостижим» — под RT-02 (от стартового экрана роли по навигации и переходам; hint,
   error@stable), а не новый id: одна проверка — одно правило. R-STRUCT-006 — «поле экрана вне перечня».
3. **Новые категории** `R-RT`, `R-CP`, `R-TX`, `R-AX`, `R-MB` — по группам T3 §4.4, а не раскладкой по R-SEM и R-COV;
   нумерация сквозная внутри категории.
4. **Тяжести, которых T3 не называет,** — по колонке «тяжесть» кандидатов ux-низ с ужесточением к `stable`: RT-03
   (error) → R-RT-002 warning / error@stable; RT-06 (warning) → R-RT-005 warning / error@stable; CP-06 (warning /
   error) → R-CP-006 warning целиком (вариант — включённое по умолчанию согласие — error); CP-07 (error) → R-CP-007:
   объём не объявлен — warning / error@stable, нет инструмента — по пометке основания строки таблицы ux 04/01 §2
   (`[система]`, `[консенсус]` — error, прочие — warning); у MB-кандидатов тяжести нет — R-MB-001/002/005 warning /
   error@stable, R-MB-006 hint / warning, остальные warning.
5. **CP-11 и AX-02 — не в `/screen-audit`.** Компонент ДС на тип и `keyboard` расширения проверяет `design-audit`
   R-COV-005 (зона 6): у экранов нет сведений о компонентах ДС. AX-07 разделён: R-STRUCT-025 и R-AX-003.
6. **Правила сверх кандидатов:** `/screen-audit` — R-SURF-003 (папка экранов у поверхности не маршрута приложения, B8),
   R-STRUCT-023 (ссылка в продуктовый слой в пустоту), R-STRUCT-024 (поле блока вне перечня), R-SEM-015 (частные правила
   состояний F7), R-RT-009 (решение `map.md` без основания), R-CP-012 (частое действие только в меню, ux 04/10 §1.2);
   `/mobile-audit` — R-INV-015 (строка «Отложенные правки», урок Z3), R-SEM-011 (`not-found` у объекта в архиве),
   R-SEM-012 (состояние приложения в `states` экрана, hint); `/telegram-bot-flow-audit` — R-STRUCT-023 (невалидный
   `escalate`).
7. **У `/fsd-audit` проверки без id** — у аудита нет системы `R-*`; новые проверки вписаны в его категории с тяжестью и
   нормой.
8. **Экран mobile с коллекцией без `empty` — error** (R-INV-013), а не warning, как у веба: у соседнего инварианта
   R-INV-001 (`loading` и `error`) тяжесть error, а один ключ `empty` приложения несёт три пустых состояния словаря
   (S01–S03) — без него экрану нечего показать. Неполный набор по таблице соответствия (`not-found`, `offline`,
   `permission-denied`) — warning (R-INV-014).
9. **«Пустое — не прочерк»** (`workflow-patterns.md § Привести к канону`, `field-checklists.md`, `raw-input.md`) против
   T3 §4.5 «новые колонки — `—` в draft»: поле, где прочерк — решение владельца, при переводе остаётся пустым. Так же
   сделала Z7a.
10. **Механическая замена ключей `states`** при приведении к канону опирается на таблицу соответствия mobile README
    (§ Состояния экрана и словарь): T3 §4.5 — только журнал. Ключ, за которым стоят несколько состояний, — вопрос
    аналитику.
11. **Точки входа `map` и `texts`** у `/screen-deep-dive` и `/screen-audit` — сверх T3: у свода и реестра нет kind, а
    этап `ui-texts` нужен как отдельный вход.
12. **У flow нет раунда связи с возможностью:** поток реализует возможность главной задачи своих экранов (`main-task` —
    типизированное поле), а у формы flow поля возможности нет; прежний раунд писал связь только в заметку state.
    Якорный раунд экрана заменён полем `main-task`.
13. **Проход по доменам шире фразы брифа:** в `domain-deep-dive/references/draft-stable.md` вместо «валидатор подсветит
    hint» — «такая ссылка — подсказка «докопать соседа», а не блокер перехода»: валидатора у слоя нет.
14. **Утилиты по имени:** `tree`, `states`, `screen_map`, `normalize` — из `design-deep-dive/scripts/README.md § project`;
    везде рядом — что делается, пока файла нет (разборщик YAML, сборка набора по списку канона, сверка чтением).

## 4. Для следующих зон

- **Шаг 8 (маршруты SaaS).** `/screen-deep-dive <slug> <surface>` — сводка с порядком этапа; `… map` — раздел
  «Переход» первым, до экранов; экраны; `… texts` — этап `ui-texts`; второй вход дизайна —
  `/design-deep-dive <slug> <surface>` после stable-экранов и свода `map.md` без расхождений; FSD — `/fsd-deep-dive`
  только у `web` рода `app`, `admin`, `desktop`, `embed`. Аудиты — `/screen-audit <slug> <surface> map` и `… texts`.
  Заметка пропусков экранов — `…/screens/<surface>/_phase-jump.md` (строка уже есть в
  `entrypoint/references/state-model.md`, зона 8).
- **Правка текста с холста кабинета:** вход с середины — `screen-deep-dive/references/workflow-patterns.md § Тексты
  интерфейса` (строка `texts.md` → `assumed`, проверки, `approved` словом заказчика).
- **Z9 (описания).** Мои шесть — 3 454 знака. Для описаний Z9: `mobile-audit` — набор по таблице соответствия и
  `empty` у экрана с коллекцией; `telegram-bot-flow-audit` — `empty` и `fallback` раздельно, путь к человеку,
  `escalate`; `telegram-bot-flow-deep-dive` — путь к человеку и роли текстов.
- **Зона 6 / оркестратор.** `design-audit` R-COV-005 несёт CP-11 и AX-02 (правило уже проверяет расширение без
  `keyboard`); `screen-audit` R-SEM-014 отсылает сверку метафоры иллюстрации к `design-audit` R-REF-007.
- **Пакет для кода (Ф8, код-репо).** `<org>/frontend` — стыки FSD (`path`, `guard`, `ui-type`, сценарии `shared-api`,
  локали = колонки `texts.md`); `<org>/mobile` — ключа архива (S20) у приложения нет, `not-found` для архива — находка
  R-SEM-011, решение — по договорённости; состояния приложения — оверлеи оболочки (ST-23 — позиция); `<org>/<bot>` —
  ключ `empty` у getter'а и `escalate` у `text-input`.

## 5. Проверка

- `refcheck.py --strict` по 23 файлам, сверка со строками диффа против `a12b475` (скрипт в scratchpad): в изменённых
  строках битых ссылок и следов журнала 0; в нетронутых — 117 находок в 13 файлах (§6).
- `phase-7/tools/static_check.py --base a12b475` (прогон после сдачи Z8): refcheck — 0 в новых файлах и изменённых
  строках (40 md; в нетронутых 245); следы прежнего запрета — 0; YAML, JSON, frontmatter — 0 ошибок; mapcheck «НЕ
  НОРМА» 0; реестр и `canon.tsv` байт в байт; описания длиннее 600 — 16 скиллов, все вне зоны (Z9), мои шесть — ≤ 600.
- Грамматика: блок `tree-notation.md § Грамматика` совпадает с блоком README screens § Нотация дерева байт в байт.
- YAML: пример `tree-notation.md § Пример` и frontmatter шести SKILL.md парсятся (`python3`, `yaml.safe_load`); длины
  описаний — `python3`.
- Id: `screen-audit` — 99 заголовков правил, 99 уникальных; `mobile-audit` — 59/59; `telegram-bot-flow-audit` — 70/70.
- Поиск по файлам зоны: «craft», «wireframe», «hi-fi», «Committed», «теперь», «больше не», «прежн» — 0.
- Глазами: поля экрана, блока, каркаса и разделы `map.md`, `texts.md` — по формам `docs/projects/_template/screens/`;
  стыки FSD, mobile, бота — по README и формам зоны 3 и отчёту Z3 §4; ключи mobile и бота не переименованы (дифф
  `mobile-audit/references/rules.md` — только добавления); поля мест, которые переписаны целиком (`tree-notation.md`,
  `project-context.md`, разделы screen, block, shell `field-checklists.md`), — сверены со старым текстом: ушли свободные
  имена `ui:` поверхности, свободные атрибуты (`variant`, `size`), шесть канон-состояний, «slug-валидаций нет», раунды
  возможности у flow и якоря у экрана — всё заменено текущей формой; поля `viewport`, `mobile-of`, `situations`,
  `slot-fills`, `ux-substrates`, `used-by-screens`, `slots`, `responsive`, `assets` — на месте.
- Ширина строк: 95-й перцентиль длины строки каждого файла до и после — в пределах ±4 знаков, кроме `screen-audit`:
  в SKILL.md длиннее строки примера отчёта, два неразрывных пути и заголовок категорий, в `rules.md` новые правила уже
  прежних.

## 6. Открыто и не прочитано

Открыто:
- копия грамматики в `tree-notation.md` — сверка скриптом или ссылка вместо копии (§3 п. 1; оркестратор);
- утилиты `tree`, `states`, `screen_map`, `normalize` — до их файлов проверка чтением по форме (Ф8);
- тяжести R-CP-006, R-CP-007 (по пометке строки ux 04/01 §2), R-MB-* — проверить на пилоте SaaS;
- `<org>/mobile`: ключ архива и состояния приложения (ST-23 — позиция), `<org>/<bot>`: `empty` и `escalate` — пакет
  для кода;
- 117 находок refcheck в нетронутых строках 13 файлов — ложные срабатывания прежнего текста: папки-токены (`flows/`,
  `blocks/`, `shells/`, `state/`, `threads/`, `index.md`), имена-образцы файлов ассетов, пути код-репо (`shared/`,
  `androidApp/`, `docs/stack/`, `../backend/api/openapi.yaml`), `_N/A_`, примеры путей бота, ссылка
  `screen-deep-dive/references/field-checklists.md` из `screen-audit/references/rules.md` (соседний скилл; база
  `.claude/skills/` в refcheck не входит) и три «было/стало» — упоминания правила forward-only в разделах памяти
  (`screen-deep-dive/SKILL.md`, `domain-deep-dive/SKILL.md`). Уборка или белый список refcheck.

Не прочитано: T2a, T2b; T4 вне вступления, H2, H7; T3 §5–§7; ux-низ — только таблицы кандидатов RT, CP, AX, MB;
база — адресно (`components.yaml` — шапка и группы, `glossary.md` — три статьи); файлы Z8 — поиском
(`state-model.md` — таблица `_phase-jump.md`, `routing.md` — строки экранов); `interface-audit`, `design-audit` —
нужные правила.

## 7. Запись для CHAIN

```
## <NN>. Z7b — соседние исполнители и аудиты: экраны, FSD, мобильное, бот, сервисы и домены (28.09, ≈ <мин — по уведомлению> мин, контекст ≈ 920 тыс. токенов по оценке агента, окно сжималось один раз)
- Сделано: 23 правки, новых нет (+2 485 / −614 строк против `a12b475`; 8 097 строк; правка по месту, ширина строк
  сохранена): `screen-deep-dive` — SKILL (589 знаков; порядок этапа в «Сводке состояния», входы `map` и `texts`,
  «Карта экранов и тексты интерфейса», шаг «Привести к канону»), `tree-notation.md` (грамматика — дословно README),
  `field-checklists.md` (screen, block, shell; новые `map.md`, `texts.md`), `draft-stable.md`, `raw-input.md`,
  `workflow-patterns.md` («Тексты интерфейса», «Привести к канону»), `project-context.md`, `assets-policy.md`;
  `screen-audit` — SKILL (577), `rules.md` (99 правил: R-SURF-003, R-STRUCT-020…025, R-SEM-011/014/015, R-COV-003,
  R-RT, R-CP, R-TX, R-AX, R-MB); `fsd-deep-dive` — SKILL (556), `workflow-patterns.md`, `draft-stable.md`; `fsd-audit` —
  SKILL (583); `mobile-deep-dive` — `field-checklists.md` («Стыки со словарями продукта»), SKILL (564),
  `interface-context.md`; `mobile-audit` — R-INV-013…015, R-SEM-011/012; бот — `field-checklists.md`, аудит —
  R-DATA-002, R-STRUCT-023, R-COV-009; сервисы и домены — три файла (домены SKILL — 585). Решения A4, A6, B8, D5, F6, F7,
  F10, F13, F14, F15, H2, H7 и 15 строк действий — с местом (отчёт §2).
- Отступления (решает оркестратор): грамматика — копия блока README в `tree-notation.md`; R-SEM-011 и R-COV-003
  переписаны по месту; категории R-RT, R-CP, R-TX, R-AX, R-MB; тяжести сверх T3 — по кандидатам с ужесточением к stable,
  R-CP-007 — по пометке основания ux 04/01 §2; CP-11 и AX-02 — в `design-audit` R-COV-005, AX-07 — R-STRUCT-025 +
  R-AX-003; правила сверх кандидатов (отчёт §3 п. 6); `empty` у экрана mobile с коллекцией — error; «пустое — не
  прочерк» против T3 §4.5; ключи `states` при переводе — по таблице mobile README; входы `map`, `texts`; flow без раунда
  возможности; у `fsd-audit` проверки без id.
- Стыки: шаг 8 — маршрут SaaS (сводка → `map` → экраны → `texts` → `/design-deep-dive <slug> <surface>` →
  `/fsd-deep-dive`), `/screen-audit … map | texts`; правка текста с холста — `workflow-patterns.md § Тексты интерфейса`;
  Z9 — 3 454 знака на шесть описаний, новые правила mobile и бота для их описаний; код — `<org>/frontend` (стыки FSD),
  `<org>/mobile` (ключ архива, состояния приложения), `<org>/<bot>` (`empty`, `escalate`).
- Открыто: сверка копии грамматики; утилиты `tree`, `states`, `screen_map`, `normalize` — чтением до Ф8; тяжести
  R-CP-006/007 и R-MB — пилот; 117 находок refcheck в нетронутых строках 13 файлов — уборка.
- Не прочитано: T2a, T2b; T4 вне вступления, H2, H7; T3 §5–§7; ux-низ — только кандидаты; база — адресно; файлы Z8 —
  поиском.
```
