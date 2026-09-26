# Таблица замен ссылок: kimi-research → claude-design-research/06-design-process (и соседи)

Переписчик kimi → Claude Design · 26.09.2026 · Claude Opus 5.5. Основа — `kimi-to-claude-design.md` §4 (адреса и счёт вхождений в
переносимых файлах соседей: «всего (строк `links.tsv`)»), новые файлы `claude-design-research/06-design-process/` и копии. Здесь Kimi
упоминать можно; в самой базе — нет. Сокращения: `06/NN` — `claude-design-research/06-design-process/NN-….md`; `cd` —
`claude-design-research/`; «удалить» — ссылку убрать, текст соседа оставить; «вне задачи» — переписчик не трогал, действует
предложение `kimi-to-claude-design.md` §4.

## 1. Что создано

| Путь | Строк | Что |
|---|---|---|
| `cd/06-design-process/README.md` | 33 | карта папки, выжимка, дополнительные метки |
| `cd/06-design-process/01-brief-and-questions.md` | 211 | бриф, четыре списка, вывод Claude, ≤ 7 вопросов (Q1–Q8), оси направлений, решения до экранов, поля брифа |
| `cd/06-design-process/02-input-package.md` | 185 | единый вход холста и ДС, токены и `DESIGN.md`, факты, тексты, референсы, бренд, ассеты, приёмка A–H, раскладка, проверка входа |
| `cd/06-design-process/03-edit-loop-and-stop.md` | 189 | раунд, пакет ≤ 7 и формат пункта, эхо, решения, W, стоп, смена стратегии, паспорт, редизайн и антипримеры |
| `cd/06-design-process/04-checks.md` | 215 | слои, таблица «проверка → порог → при провале» A–F, команды, 10 приёмов, рубрика, аудит, «только заказчик», ворота, ложные находки |
| `cd/06-design-process/05-default-look.md` | 188 | бан-лист с порогами и частотами, дом-стиль Claude поимённо, «оставить как вкус», блок запретов, исключения замера |
| `cd/06-design-process/06-test-stand.md` | 187 | стенд S1/S2, честность, что меряем, страница слепых пар, правило решения и мощность, рубрика, варианты, журнал |
| `cd/06-design-process/07-prompt-templates.md` | 169 | 8 заданий: направления, ДС, вайрфрейм, макет, правки, мобильная, движение, аудит |
| `cd/06-design-process/stand/S1-kvarts/` | 241 + 72 | копии `brief.yaml` и `01-description-and-questions.md` + заголовок «что убрать» |
| `cd/06-design-process/stand/S2-smena/` | 225 + 50 + 79 | то же + `fixtures.json` (побайтно) |
| `cd/99-raw/tools/mockup_checks.py` | 1 537 | копия `k3_checks.py` без правок кода + 20 строк заголовка |
| `cd/99-raw/tools/stand_page.py` | 442 | копия `stand_page.py` без правок кода + 14 строк заголовка |
| `cd/99-raw/tools/shot_v3.py` | 395 | копия `shot.py` v3 без правок кода + 18 строк заголовка (дополнение 26.09 по решению заказчика) |
| `cd/99-raw/tools/lang_check.py` | 94 | копия `lang_check.py` (версия с патчем v1) без правок кода + 15 строк заголовка (то же) |
| `cd/06-design-process/data/` | 11 файлов, 89,6 КБ | сводки замеров за частотами `06/05` (обезличены: имена → G, числа сверены) + `README.md` с легендой (то же) |
| `cd/README.md` | +2 строки | «Карта файлов» и «Маршруты» |

## 2. Замены по адресам kimi

| Адрес kimi | Вхождений | Раздел kimi → куда |
|---|---|---|
| `05-reviews-practice/03-default-look-k3.md` | 115 (51) | §2 таблица примет → `06/05` §3; §3.1 цвет → `06/05` §3 (бумага, подписи); §3.2 типографика → `06/05` §3 и выжимка п. 9–10; §3.3 композиция → `06/05` §1, §3 (hero, карточки); §3.4 форма → `06/05` §5; §3.5 движение → `06/05` §3 (WebGL, анимация); §3.6 ассеты → `06/02` §3; §3.7 копирайт → `06/05` §3 (тире, «X, not Y»); §3.8 мобильная → `06/05` §3, `06/04` §3 B; §3.9 дефекты → `06/05` §3 (контент-баги); §4 → `06/05` §1; §5.1 → `06/05` §5; §5.2 → `06/05` §6; §5.3 → `06/05` §3 + §6; §1.3 исключения замера → `06/05` §7. Строки источника в `creative 99-raw/tools/marketing_audit.py` (стр. ≈ 655, «kimi 05/03») → `claude-design-research/06-design-process/05-default-look.md` |
| `07-brief-handoff/01-from-app-description-to-brief.md` | 63 (44) | §1 → `06/01` §1; §2.1 → `06/01` §2; §2.2–2.3 → `06/01` §2; §2.4 → `06/01` §5 (+ `cd/05-design-artifacts/01` §5); §2.5 → `06/02` §3; §2.6 → `06/01` §2, `06/02` §3; §3 → `06/01` §3; §4.1–4.2 → `06/01` §4; §4.3 (вопросы из пустых полей) → `06/01` §7, `06/02` §6; §4.4 → `06/01` §4 + `stand/S1-kvarts/01-description-and-questions.md`; §5.1 → `06/01` §7; §5.2 → `06/01` §5 (шрифты), §7; §5.3 → `06/01` §7; §6.1 → `06/01` §6; §6.2 → `06/01` §6 + creative `01-creative-direction/ambition-levels.yaml` (`motion_level` — своя норма); §6.3 → `06/01` §6, `06/02` §3; §6.4 → `06/01` §6 + blender `12-recipes/00-how-to-use.md` §1; §6.5 → `06/01` §6, `06/06` §8; §7 (компиляция в задачу K3, первый промт) → удалить; вместо — `06/07` |
| `07-brief-handoff/02-task-package.md` | 8 (7) | §1 → `06/02` §5; §2 → `06/02` §1; §3, §6, §7 (каналы, два харнесса, скилл исполнителя) → удалить; §4.4 → `06/02` §2 (+ `cd/05-design-artifacts/01` §3.2, §4; ui DTCG); §4.5 → `06/02` §4; §4.6 → `cd/04-claude-code-native/kit/shot.py`; §5 → `06/02` §6; §8.1 → creative `07-stack-implementation/01-stack-choice.md` §11 (раздел переименовать, вне задачи) + `06/01` §7 (`build.allowed_packages`); §9 → `06/01` §2, `06/02` §3; §10 → `06/03` §1 |
| `07-brief-handoff/03-references-brand-assets.md` | 43 (30) | §1 → `06/02` §3 «Референсы»; §2.1–2.2 → `06/02` §3 (+ решение заказчика: картинки с площадок не выкачивать); §2.3 видео-референс → creative 02/03 §5.1 (ветка Claude: лист 3×3 + кадры + таймлайн текстом; вне задачи) и `06/07` §7; §3 → `06/02` §3; §4, §4.1–4.3, §4.5 → `06/02` §3 «Бренд», §2; §4.4 → `06/01` §5, `06/02` §2; §5 → `06/02` §3; §6 → `06/02` §3 «Ассеты» (+ ai-media 01/01, 10); §7 → `06/01` §6 + blender 12/00; §8 → `06/02` §6; §9 → удалить |
| `07-brief-handoff/` (папка), `README.md` | 22 (4) | в cd → `06-design-process/`; в прочих — удалить |
| `07-brief-handoff/templates/brief.yaml` | 12 (11) | `06/01` §7 (поля) + `06-design-process/stand/*/brief.yaml`; в site — свой бриф (`site-research/01-foundations/03-site-brief.md`, схема); дизайн-поля — creative `art-direction` |
| `templates/ACCEPTANCE.md` | 11 (11) | `06/02` §4; в site блоки I–L оставить своими, привязку к A–H — на `06/02` §4 |
| `templates/DESIGN.md`, `tokens.css` | — | `06/02` §2; пример токенов — `cd/04-claude-code-native/kit/example/tokens.css` |
| `templates/facts.md`, `copy.md` (3 + …) | 8 + 13 (на всю папку) | `06/02` §3; каноны — text `02-strategy-messaging/facts.schema.yaml`, copy deck `10-templates-recipes/01-copy-deck-workflow.md` |
| `templates/brand.json`, `refs-README.md` (2), `assets-README.md` | — | `06/02` §3 «Бренд», «Референсы», «Ассеты» |
| `templates/design-executor.md` | — | бан-лист → `06/05` §6; «делать только заказанное, остальное — «предлагаю ещё»» → `06/03` §2, `06/07` §4; фронтматтер и `${base_prompt}` → удалить |
| `templates/TASK.md`, `AGENTS.md`, `first-prompt.txt` | — | удалить (канал исполнителя); задания — `06/07` |
| `templates/build_package.py` (5) | — | проверки входа → `06/02` §6 (скрипт — при сборке скилла); ссылку удалить |
| `templates/shot.py` (1) | — | `cd/04-claude-code-native/kit/shot.py`; для `--expect-fonts`, `--routes`, `--views` — `cd/99-raw/tools/shot_v3.py` |
| `08-director-loop-qa/01-loop-protocol.md` | 17 (17) | §1 → `06/03` §1; §2 → `06/03` §1 (шаг 0), `06/02` §6; §3 → `06/01` §4, `06/07` §1, §3; §4–§6, §9, §13, §14 (запуск, сторож, транспорт, сессии, сбои, бюджеты K3) → удалить; §7 → `06/04`; §8, §8.3 → `06/03` §2; §8.1 → `06/03` §4; §8.2 → `06/03` §1 (мелочь мышью заказчика); §10 → `06/03` §5; §11.1 → `06/03` §5; §11.2 → `06/03` §5 (бюджет в раундах); §11.3 → `06/03` §6; §11.4 → `06/03` §5 «жёсткий»; §12 → `06/04` §7; §15 → `06/03` §7. site шаг 9 `step:build-loop` → `06/03` |
| `08-director-loop-qa/02-checks-k3.md` | 61 (56) | §1 → `06/04` §2; §2 A (транспорт) → `06/04` §3 A (публикация); §2 B → `06/04` §3 B; §2 C → `06/04` §3 C + `06/05` §3; §2 D → `06/04` §3 D; §2 E → `06/04` §3 E; §2 F → `06/04` §3 F; §3 → `06/05` §3; §4 → `06/04` §4 + заголовок `cd/99-raw/tools/mockup_checks.py`; §5 → `06/04` §5; §6 → `06/04` §6; §7 → `06/04` §8; §8 и ложные находки → `06/04` §9. site `site-checklist.yaml` (`source_file`), `ux-marketing-profile.tsv`, `page-gates.yaml` (`owner: kimi 08/02 M-NAV`, `kimi F-FILLER`) → `06/04` §3 + новые id (§5) |
| `08-director-loop-qa/03-critique-messages.md` | 1 + (08/04, 08/03: 2) | §1–§2, §3.1 → `06/03` §2; §3.2 → `06/07` §6, `06/03` §2; §3.3–3.9 → `06/03` §2 (таблица тем); §3.10 → `06/03` §4; §3.11 → `06/03` §8; §3.12–3.16, §3.18 (доказательства, STOP, сбой, новая сессия, ответы K3) → удалить («не закончено» ≤ 2 → `06/03` §5); §3.17 → `06/04` §7, `06/07` §8; §4 → `06/03` §8; §5 → `06/03` §5. cd `04-claude-code-native/01` §2.5 п. 3 («формат пункта kimi 08/03») → `06/03` §2 |
| `08-director-loop-qa/04-variants-selection.md` | (в строке выше) | §1–§2 → `06/06` §8, `06/01` §5; §4 → `06/06` §5, §6, §8; §5 → `06/06` §8 (слияние); §6 → `06/06` §8; + `cd/05-design-artifacts/01` §5 |
| `08-director-loop-qa/` (папка) | 16 | в cd → `06-design-process/` (`03`, `04`); в site → то же |
| `03-prompting/04-template-library.md` и «kimi T…» | 17 (15) + 37 | T2a → `06/07` §1 (+ `06/01` §5, `cd/05-design-artifacts/01` §5); T2b → `06/06` §8; T3a, T3b → `06/02` §3 (референсы; «ДНК» с тремя намеренными отличиями — не перенесено, §6); T3c → creative 02/03 §5.1 и `06/07` §7; T4 → `06/02` §3; T5 → `06/03` §2, `06/07` §5; T6 → `06/07` §6; T7 → `06/07` §7 (+ creative 09/02 motion-spec); T8 → `06/03` §2 (тема «типографика»; + ui 02, text); T9 → удалить (самопроверка исполнителя; проверки — `06/04`); T10 → `06/02` §3; T11 → `06/03` §6 («сузить задачу»); T12 → `06/07` §8, `06/04` §7; T13 → `06/01` §4; T15 → `06/03` §5; T0, T14, T16 → удалить. Комментарии «kimi T8» в blender `15-showcase/sdano/*/style.css` и копии creative `10-recipes/examples/l0-sdano/style.css` — удалить упоминание, норма (h1 ≤ 2 строк на 1440 и ≤ 4 на 390) — `06/02` §4 C3 |
| `03-prompting/03-prompt-anatomy-k3.md` | 6 (5) | §3.3–3.4 → `06/01` §3; §3.6 → `06/01` §5; §3.17 → `06/05` §6; §5 → `06/01` §7; §8 → `06/01` §1 (таблица антипримеров); §9 → `06/07` (стопы этапов); §1–§2, §6–§7 → удалить |
| `03-prompting/02-community-practice.md` | 3 (3) | §14 (hero ≤ 7 слов, text отверг, X3) → удалить; §10 → `06/07` §6; §13 → `06/03` §8 |
| `03-prompting/01-official-guidance.md` | 1 (1) | удалить; руководства Anthropic — внешние адреса platform.claude.com (с датой снятия) |
| `04-skills-tools-repos/01-design-skills.md` | 11 (10) | вне задачи: удалить, если норма уже в тексте creative; каталог Hallmark — внешний адрес `Nutlope/hallmark@13ac0ec` |
| `04-skills-tools-repos/03-…` (04/03) | 2 (2) | вне задачи (не читался) |
| `09-test-plan/01-test-plan.md` | 6 (5) на всю папку | §3.2 → `06/06` §3; §3.4 → `06/06` §4; §3.5 → `06/06` §6; §3.6, §5–§14 (тесты K3, каналы, ToS) → удалить; план тестов Claude — cd README «План тестов» |
| `09-test-plan/02-stand-briefs.md` | (в строке выше) | §1–§2 → `06/06` §2 + `stand/`; §0.4 (шрифты с кириллицей) → `06/01` §5; S3–S7 → `06/06` §2 (кандидаты, пересоздать на пилотах) |
| `09-test-plan/03-protocol-logging.md` | — | §5.1–5.4 → `06/06` §5–§6; §5.5 → `06/06` §7; §7 → `06/06` §9; остальное → удалить |
| `09-test-plan/tests.yaml` | — | удалить; тесты — cd README «План тестов» |
| `10-playbook-skill/PLAYBOOK.md` | 1 (на папку) | → `06-design-process/README.md`; §0 роли → `06/04` §8; §6.3 → `06/04` §3, `06/05`; «Решения по противоречиям»: длинное тире → `06/05` §3; один маркер `[PLACEHOLDER: …]` → `06/02` §3; «архетип без фактов — секцию не строить» → `06/02` §3 |
| `10-playbook-skill/skills/kimi-design-director/SKILL.md` | — | → `06-design-process/` (`03`, `04`) |
| `…/kimi-design-director/scripts/stand_page.py` | 1 (1) | `cd/99-raw/tools/stand_page.py` (cd README стр. 237) |
| `…/scripts/k3_checks.py`, `99-raw/tools/k3_checks.py` | 12 (12) | `cd/99-raw/tools/mockup_checks.py`; creative `09-ai-execution-evaluation/effect-gates.yaml` стр. 32 (`kimi: …k3_checks.py`), text `PLAN.md` стр. 112, 214 и `99-raw/handoff-to-neighbours.md`, text `10-templates-recipes/01-copy-deck-workflow.md` §9 (`verify-page` «по образцу k3_checks F-COPY / F-NUMBERS») → тот же путь + новые id (§5) |
| `…/scripts/variants_page.py`, `kimi_run.py`, `lang_check.py`; прочие `99-raw/tools/` | 28 (на `99-raw/experiments` и `tools`) | `variants_page.py` → `cd/99-raw/tools/stand_page.py` или ai-media `stand_run.py page/tally`; `kimi_run.py` → удалить; `lang_check.py` → `cd/99-raw/tools/lang_check.py` |
| `99-raw/experiments/F/03-package-from-description/` | (в строке выше) | `cd/06-design-process/stand/` (`landing-kvarts/` → `S1-kvarts/`, `webapp-smena/` → `S2-smena/`, `webapp-smena/src/fixtures.json` → `S2-smena/fixtures.json`). Зависят: creative `01-creative-direction/examples/art-direction-kvarts.json` (поле `brief`), text `PLAN.md` стр. 48, site `02-site-types/02-vocabulary-and-crosswalk.md` [S8], site `90-sources/sources.tsv` стр. 98 |
| `99-raw/experiments/E/01-kilo-pairs`, `E/03-kimi-page-measure`, `E/04-sulat-pairs` (сводки) | — | `cd/06-design-process/data/` (§4); сырьё (кадры, `probe/*.json`, замеры, `prompts.json`) — удалить |
| прочие `99-raw/experiments/*` (Q, G, D, Z, T, A/04, остальное E) | — | удалить (метки `[проверено: …]` оставить силой доказательства без пути) |
| `99-raw/cache/repos/*` (Hallmark, ui-ux-pro-max, claude-code-router) | 157 (156) | не Kimi: внешние адреса `Nutlope/hallmark@13ac0ec`, `nextlevelbuilder/ui-ux-pro-max-skill@dcc40ff`, `musistudio/claude-code-router@75e9e75`; site `crosswalk.tsv` — 119 строк |
| `99-raw/notes/wave1/C-notes.md`, `E-notes.md`, `99-raw/cache/platform.claude.com_*` | 6 (6) | внешние адреса руководств Anthropic (prompting best practices, Opus 4.8, Opus 5.5) с датой снятия |
| `91-videos/digests/weoV4dm-X1A.md`, `p1J5uWcn3hI.md`, `EwTOiqWWqEc.md` | 13 + 9 + … | путь удалить, метку ролика `[V:<id> mm:ss]` оставить |
| `01-model-k3/03-…`, `99-raw/experiments/A/04-arena-snapshots` | 3 | удалить или внешний адрес Arena.ai с датой снимка |
| `02-harness-orchestration/05-…` | 2 (2) | удалить (cd `02-claude-code-bridge/01` §11 «Контраст с архитектурой Kimi» — снять раздел при уборке) |
| папки `03`, `04`, `05`, `06` | 9 | удалить |
| корень `kimi-research/`, `README.md`, `CONTRADICTIONS.md` | 21 (21) | удалить; решения X, на которые опирались нормы, уже в текстах `06/03`, `06/05`, `06/02` |

## 3. Ссылки на kimi внутри claude-design-research (для уборки cd)

| Файл, строка | Сейчас | Заменить на |
|---|---|---|
| `README.md` стр. 6 | «бриф, пакет задачи и цикл арт-директора — `../kimi-research/` (07, 08, 09). Здесь на них только ссылки» | «— `06-design-process/`» |
| `README.md` стр. 90–91 (рабочий цикл) | `brief.yaml (kimi 07)`, «шаблоны kimi 07» | `06/01` §7, `06/02` §2 |
| `README.md` правило 7 (стр. 157–158) | «артборды пишут только `var(--…)`… kimi 07/02 §4.4» | конфликт К1 снят решением 26.09: холст — литералы из токенов ДС, `kit` и код — `var(--…)` → `06/02` §2 |
| `README.md` правило 8 (стр. 159–160), 18 (стр. 184–185) | kimi 07/01 §4–§5; kimi 08/01 | `06/01` §4; `06/03` §2, §5 |
| `README.md` «План тестов» (стр. 234–237, 241), «Маршруты» стр. 285 | стенд, правило §3.5, `stand_page.py` в kimi; «K3 по kimi T-501» | `06/06` §2, §6; `99-raw/tools/stand_page.py`; плечо K3 — снять |
| `README.md` «Сравнение с Kimi K3» (стр. 251–267), стр. 80, 320, 339 | раздел, «Ответ заказчику» п. 6, «Что устаревает», соседние базы | снять при финальной уборке (решение 26.09: Kimi в шаблоне не упоминается); переносимое уже в `06-design-process/` |
| `04-claude-code-native/01` стр. 11, 30, 69–75, 172–192 (§2.6), 395–411 (§7), 490, 535–538 | kimi 07/08, формат kimi 08/03, T-D7 «против Kimi K3» | `06/01`, `06/02`, `06/03`; §2.6 и T-D7 — снять |
| `03-practice-pipelines/01` стр. 5, 39–40, 217, 237–239, 291–297, 437–455 (§8.2), 461, 560–572, 610–614 | цикл kimi 08/01, кэш kimi, арены kimi | §8.2 → `06/03`; руководства — внешние адреса; арены — дата снимка без пути |
| `02-claude-code-bridge/01` стр. 7, 325, 424, 441–445 (§11), 489, 526 | kimi 07, 02/05, T-501 | `06/01`; §11 — снять |
| `01-product/01` (2 вхождения), `03-practice-pipelines/README.md` | kimi | удалить или `06-design-process/` |
| `04-claude-code-native/kit/shot.py` стр. 5 | «перенесены из kimi-research/07-…/shot.py v3» | провенанс убрать при уборке (код не менять) |
| `PLAN.md` стр. 5, 12, 29, 54, 79, 95, 109, 161, 205 | журнал ресёрча | архив (серая зона, `kimi-to-claude-design.md` §6.2) |

## 4. Копии

| Откуда (kimi) | Куда | md5 оригинала | Что добавлено |
|---|---|---|---|
| `99-raw/tools/k3_checks.py` (= копия в `10-playbook-skill/…/scripts/`) | `cd/99-raw/tools/mockup_checks.py` | `7dde044e876c83b9ad6e5a03d212af5c` | 20 строк комментария после shebang: брать `page`, `resize`, `selftest`; убрать `watch`; переименовать id K3-*/F-* (маркеры site, реестр creative); `ALLOW_KEYS` не менять; входы — markdown-таблицы. `selftest` из нового места — OK |
| `10-playbook-skill/skills/kimi-design-director/scripts/stand_page.py` (= `99-raw/experiments/T/01-stand-page/`) | `cd/99-raw/tools/stand_page.py` | `7cae69382f00cdc712b416741e0c7d6d` | 14 строк: зависимость от ai-media `stand_run.py` по абсолютному пути; имена условий K3 в умолчаниях и selftest; имена кадров; `PYTHONDONTWRITEBYTECODE=1`. `selftest` — PASS |
| `99-raw/experiments/F/03-…/landing-kvarts/brief.yaml`, `01-description-and-questions.md` | `cd/06-design-process/stand/S1-kvarts/` | в заголовке файлов | YAML- и HTML-комментарий «что убрать»; синтетические картинки, GLB-заглушка и `out/` не копировались |
| `…/webapp-smena/brief.yaml`, `01-description-and-questions.md`, `src/fixtures.json` | `cd/06-design-process/stand/S2-smena/` | `fixtures.json` — `19391c3db9e637fd57ef2a2dc3021d49` | то же; `fixtures.json` побайтно (JSON без комментариев, пометка SYNTHETIC — в поле `_note`) |
| `07-brief-handoff/templates/shot.py` (= копии в `10-playbook-skill/…/templates/` и `…/kimi-design-executor/scripts/`) | `cd/99-raw/tools/shot_v3.py` (md5 копии `870a97417062d672a6b7596ec1a8baac`) | `6a5c3a872785d1aa748b1df76f654dd0` | 18 строк: отличия от `kit/shot.py` (`--views`, `--routes`, `--expect-fonts` → `fonts_unexpected`, кадры по экранам, `--selector`, `--map`, `--strict`); убрать бюджет байт под чтение картинок другим исполнителем; при слиянии с kit не держать два набора проверок. `--help` работает |
| `10-playbook-skill/skills/kimi-design-director/scripts/lang_check.py` (патч v1, = копия в `…/kimi-design-executor/scripts/`) | `cd/99-raw/tools/lang_check.py` (md5 копии `0c25f3363079a9a27c49a39d7bd35c68`) | `53aae9fcd072e971fbd8a1110e7e06ea`; исходник без патча `99-raw/experiments/Z/04-lang-check/lang_check.py` — `007b868f6fe74729a1b43ac7273b0474` (не копировался) | 15 строк: назначение; разбор файла текстов заточен под markdown старого пакета — для copy deck text адаптировать; ссылки на Z/04 и «P-патч»; язык ru зашит. Прогон на `kit/example/landing.html` — 0 находок |
| `99-raw/experiments/E/01-kilo-pairs/README.md` · `palette_temp.json` | `data/pairs-first-screens.md` · `data/pairs-first-screens-palette.json` | `7f2297d5cc6308791e6408dc8e1b9249` · `aef5db5d7a0ac1972344b2d2beebaefc` | обезличено (K3 → G, файлы `-k3` → `-g`); в `.md` — строка-комментарий о копии |
| `…/E/03-kimi-page-measure/README.md` · `probe_summary.md` · `probe_summary.tsv` · `measure_summary.md` · `audit_summary.md` | `data/showcase-method.md` · `showcase-probe-summary.md` · `showcase-probe-summary.tsv` · `showcase-measure-summary.md` · `showcase-audit-summary.md` | `c575a2bd7a8cb5b15b6c96a19849f612` · `15d3e7667150e91b7786cb50beaeec43` · `29cc51ded758506cc344d6b68d175018` · `7b7ef529af818cbbca9c3b72e562937b` · `0e1f632b2e9ab5f5248235eff15475c6` | обезличено: K3 → G, K2 → G0, Kimi / Moonshot → «вендор G», Kimi Websites → «сайтостроитель G», домены `*.kimi.page`, `*.ok.kimi.link`, `*.kimi.pro`, `*.kimi.site` → `*.хостинг-G`, слаги `k3-`/`k2-` → `g-`/`g0-`; строка `K3` правил `ui_audit.py` (длительности 300 мс) сохранена; `measure_summary.tsv` не брался (дубль `.md`) |
| `…/E/04-sulat-pairs/README.md` · `probe_summary.md` · `probe_summary.tsv` | `data/model-pairs.md` · `model-pairs-probe-summary.md` · `model-pairs-probe-summary.tsv` | `af86883531767c6e3658e77fcaaebb24` · `3e31a418c96cccad6fd66792d8565a42` · `2fab9ba5bb482757a3d849dfe5ff3940` | обезличено (K3 → G, `__k3` → `__g`, `pair-k3` → `pair-g`, `*.k3.demos.sulat.com` → `*.G.demos.sulat.com`, r/kimi → Reddit) |

Сверка сводок: для каждого файла последовательность всех чисел совпала с оригиналом (скриптом; из оригинала убраны цифры имён K2/K3 и
заменённого пути к старому файлу примет); остатков «kimi», «moonshot», «k3» — 0, кроме id проверки `ui_audit.py`. Кадры, `probe/*.json`,
отдельные замеры `measure_ui.py`, `prompts.json`, `previews.json` и HTML каталога Sulat — сырьё, не брались.

## 5. Предложение: новые id проверок `mockup_checks.py` (не применено, решает уборка)

| Сейчас | Предлагаю | Зависят |
|---|---|---|
| `K3-BG-WARM`, `K3-ACCENT-WORD`, `K3-SERIF-DISPLAY`, `K3-EYEBROW`, `K3-HERO-OVERLAY`, `K3-HERO-CENTER`, `K3-STATS-ROW`, `K3-THREE-CARDS` | `LOOK-BG-WARM`, `LOOK-ACCENT-WORD`, `LOOK-SERIF-DISPLAY`, `LOOK-EYEBROW`, `LOOK-HERO-OVERLAY`, `LOOK-HERO-CENTER`, `LOOK-STATS-ROW`, `LOOK-THREE-CARDS` | creative `cliche-registry.yaml` (35 вхождений), site `ai-landing-markers.yaml` (11), `page-gates.yaml` |
| `K3-GRADIENT-TEXT`, `K3-GLASS`, `K3-PILL`, `K3-META-DOTS`, `K3-ARROWS`, `K3-MONO-LABELS`, `K3-NUMBERED`, `K3-MARQUEE`, `K3-DRAWN-CHROME`, `K3-CAPS`, `K3-WARM-CONTRAST` | `LOOK-…` с тем же хвостом | те же |
| `F-UNSPLASH`, `F-STOCK`, `F-HOTLINK`, `F-CAPTION`, `F-NUMBERS`, `F-COPY`, `F-FILLER`, `F-QUOTE` | `HON-…` с тем же хвостом (буква F занята группой «ассеты и скорость» приёмки A–H) | site `page-gates.yaml` (`kimi F-FILLER`), text `PLAN.md`, `01-copy-deck-workflow.md` §9, `claims_check.py` (провенанс F-NUMBERS) |
| `M-NAV`, `M-BODY-16`, `M-OVERFLOW`, `M-H1-LINES`, `V-OVERLAP`, `E-LOW-DOM` | без изменений | site `page-gates.yaml` (`kimi 08/02 M-NAV`) — снять только слово «kimi» |
| ключи `--allow` (`warm`, `serif`, …) | без изменений; поле `k3_allow` creative → например `allowed_tells` | creative `art-direction.schema.json` (v0 и v1), `recipe.schema.json`, примеры `art-direction-*.json`, `cliche-registry.yaml` (`compat.k3_checks`) |

Старые id — «не Kimi» в ui: `K3` у `ui_audit.py` (доля длительностей 300 мс, стр. 977) — не трогать при замене по слову.

## 6. Что сознательно не взято (исчезнет вместе с kimi)

- Всё про K3 и её харнесс: модель, арены, цены и квоты, Kimi Code, `kimi -p`, сторож, `kimi_run.py`, два харнесса в одной папке, файл
  агента, каналы по силе, EN-язык инструкций, ToS, китайская экосистема, тесты K3 (64 теста `tests.yaml`, правила R1–R13).
- Шаблоны T0, T9, T14, T16; сообщения STOP, «покажи доказательства», продолжение после сбоя, новая сессия с резюме.
- Брифы стенда S3–S7 (только описание кандидатов в `06/06` §2), каталог Hallmark (04/01), разбор «ДНК» референса с тремя намеренными
  отличиями (T3a — в `06/02` §3 только суть), видео-референс для K3.
- Утилиты: `build_package.py` (сборщик пакета; его проверки — списком в `06/02` §6), `prep_ref.py` (ужатие референсов под чтение
  картинок), `variants_page.py`, паспорт `PASSPORT.yaml` целиком (в `06/03` §7 — сокращённый). `shot.py` v3 и `lang_check.py` взяты
  26.09 по решению заказчика (§4).
- Сырьё замеров `E/01`, `E/03`, `E/04` (кадры, JSON по страницам, промты витрины) — сводки взяты в `06/data/`; оценки «на глаз» (надзаголовки
  над h2, декоративная нумерация, контент-баги, вордмарк, круговой текст, меню на 390) сводной таблицы не имели — только текст 05/03 §3.
- Симуляция мощности правила решения (`T/01`) — метка `[проверено: симуляция]` в `06/06` без пути (пересчёт — `stand_page.py power`).

## 7. Спорные места

1. **Метки.** Приметы и частоты `06/05` измерены на вёрстке другого генератора (и частично Claude Fable 5, июль); для Opus 5.5 — нет.
   Пакет ≤ 7 и W — позиция базы для модели с управляемостью 1,99 %; для Claude помечено `[мнение базы]` `[спорно]`.
2. **`.dc.html` и `kit`.** Номера `#N`, `diffshots` и все скрипты работают на HTML-копиях; как рендерить артборд типа локально — открытый
   вопрос (`cd/05-design-artifacts/01` §7). Процесс `06/03`–`06/04` на это опирается.
3. **Единый вход** (`06/02` §5) — предложение раскладки `input/`; окончательно — при сборке скилла (решение 26.09).
4. **Входы `mockup_checks.py`** — markdown-таблицы; факты text — YAML: нужен перевод или адаптация утилиты.
5. **Бюджет раунда** для Claude (время, доля лимита) не мерился — стоп пока в раундах (≤ 3 на экран).
6. **Референсы**: решение «картинки с площадок не выкачиваем» против «референс — файл с кадром» из kimi; в `06/02` §3 — ссылка + роль +
   значения текстом, кадр — от заказчика или замер живого сайта.
7. **Эталон «Кварц»** у creative (`art-direction-kvarts.json`) и text (`PLAN.md`) ссылается на kimi — перенаправить на `06/stand/S1-kvarts/`.
8. **Сводки в `06/data/` обезличены** (правило «Kimi в базе не упоминать»): имена заменены, числа сверены; оригиналы с именами исчезнут
   вместе с kimi. Строка `K3` в `showcase-audit-summary.md` — id проверки `ui_audit.py`, при уборке по слову «K3» не трогать.
