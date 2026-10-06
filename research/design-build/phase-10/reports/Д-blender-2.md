# Д-blender-2 — машинные файлы базы blender: витрина `15-showcase` (страницы четырёх предметов и `_shared/code3d`)

Коммит начала — `1e0cd2a`. Список зоны — 76 файлов (51 разный по содержимому, остальные — копии) и 6 файлов витрины,
добавленных решением координатора (маски расширены); тронуто 70 из 76 и 3 из 6 (+377 −464 строки; строк в файлах списка
16 893 → 16 815). Маркеры зоны: 382 → 93; все целевые классы — 0; остаток — 93 ложных срабатывания класса-подсказки `letters`.
Исполняемый код не менялся: у 33 `.js`, 20 `.css` и `build.sh` дифф вне комментариев пуст; числа в JSON и YAML прежние.
Git — только чтение. Пути ниже — от `.claude/skills/design-deep-dive/kb/blender/15-showcase/`, утилиты — от корня скилла.
Файлы замен и выводы проверок — `~/.cache/design-deep-dive/out/f10/Д-blender-2/` (`patch-01…10`, `checks/`).

## Решения координатора и что по ним сделано

1. «Фаза N» в `_shared/code3d` — оставлено: имя вида сцены.
2. Журнал времени и ключи прогонов в `numbers.json` — оставлены: данные примера, на них ссылаются README.
3. `version` и строки консоли — оставлены.
4. `refs` четырёх спецификаций — переведены 13 путей из 16; три `page_plan` оставлены: с планом `spec_check.py` даёт новые
   находки (раздел «`refs` спецификаций»).
5. Списки кадров несуществующей `zveno/judge/` — сняты: `zveno/a-code/numbers.json` — три блока `files` (21 кадр),
   `zveno/numbers.json` — `b-blender.frames` (2 кадра).
6. `velmora/ai/01-mouse-scrub/index.html` — ссылки сняты, текст остался: «Исходник: SC-03 · kling/v3 · 3,7 МБ (кадр-вход SC-02
   Sunburst 2K)» (`:106`, `:107`), подвал без «все приёмы» (`:166`). Сверх названного: четвёртая ссылка на тот же отсутствующий
   `../index.html` — хлебная крошка шапки `:65`: `<a class="crumb" href>` → `<span class="crumb">`, текст «Галерея приёмов» и
   вид те же (стиль `.topbar .crumb` от тега не зависит). Ссылок `<a>` на странице больше нет.
7. Файлы вне первого списка пройдены по тем же правилам: `keyboard/numbers.json`, `velmora/numbers.json`,
   `velmora/judge/metrics.json` — правлены; три `manifest.json` — без правок (строки таблицы ниже).

## Файлы

Маркеры — сумма по классам `kbscan.py` с классами `--extra`; «→» — до и после.

| файл | что сделано | маркеры |
|---|---|---|
| `_shared/code3d/build.sh` | шапка без «дорожка CD»; «из npm-trial» → «из npm-зависимостей скилла»; пример: `$R/15-showcase/zveno/c-hybrid/js` → `zveno/c-hybrid/js` | 3 → 0 |
| `_shared/code3d/src/{detail,rig,util}.js` (3) | шапка без «дорожка CD» | 1 → 0 |
| `_shared/code3d/src/ik.js`, `ktx2.js` | шапка без «дорожка CD» | 2 → 1 |
| `_shared/code3d/src/glb-modules.js` | шапка без «дорожка CD, фаза 2», «npm-trial»; «v2 (26.09)» → «v2»; «ловушка CD3» → «ловушка»; снято «как j2.glb дорожки Z» | 4 → 2 |
| `_shared/code3d/src/modules-code.js` | шапка без «дорожка CD», «v2 J2» → «v2»; «у ассета Z» → «у ассета Blender»; «паспорт Z §4» → `zveno/art-direction.md §4` | 10 → 8 |
| `_shared/code3d/src/post.js` | шапка без «дорожка CD; из CD/src/post.js фазы 1»; сняты «(CD dbg-programs)», «(CD2)», `out/p2/zoom-spark3.png`, «CD f-v3 19:37» | 1 → 0 |
| `_shared/code3d/src/scene.js` | шапка без «дорожка CD», «npm-trial», пути `99-raw/experiments/CD/src/scene-v3p1.js`, «(26.09)»; сняты «(CD3)», «CD3 sweep s5→t2», «CD shots-v3»; «опыты AO» → «замеры AO» | 6 → 3 |
| `_shared/code3d/src/studio.js` | шапка без «дорожка CD»; сняты «(J2)», «(CD2)» | 2 → 0 |
| `_shared/code3d/src/trail.js` | шапка без «дорожка CD, фаза 3»; снято «— CD3, out/cd3/f-p3-ik» | 1 → 0 |
| `_shared/code3d/src/world.js` | шапка без «дорожка CD»; снято «CD3:» | 4 → 3 |
| `keyboard/{a-code,b-blender,c-hybrid}/src/model_a.js` (3) | «Фаза 2:» в шапке и «KB3:» (2) сняты; копии равны `12-recipes/examples/14-product-in-code/src/model_a.js` | 8 → 8 |
| `keyboard/*/src/model_c.js` (3) | «KB3» (2) сняты; `06-export/export_web.py` → «export_web.py рецепта 17»; копии равны `12-recipes/examples/15-hybrid-blender-code/src/model_c.js` | 1 → 1 |
| `keyboard/*/src/capture.js`, `stage3d.js` (6) | не тронуты: S1, S2 — схемы света, остальное — код | 1 → 1, 4 → 4 |
| `keyboard/gallery.json` | `cost` без «фаза 1», «фаза 2»; `gates` (2) без «финал 04:34», «ночь 26.09» | 3 → 3 |
| `sdano/gallery.json` | `cost` (6): id сессий SD2, SD3, «фаза 1», «фаза 2 SD» и время суток сняты, длительности остались («00:06–01:05» → «в пределах 59 мин»); `gates`, `helped`: пути `gates/c-hybrid/fx/fx_bench2.json`, `judge/…webm` сняты; `how`: `scripts/topdown_hf.py` → «Скрипт Blender»; «SD2 хранил» → «прежний вариант хранил»; сняты «SD2», «у SD3» | 2 → 2 |
| `velmora/gallery.json` | `cost` (2) без «VD2:», «(фаза 1)» | 1 → 1 |
| `zveno/gallery-CD.json` | `gates` (9): «тишина 26.09 01:47–01:53» → «тишина»; `cost` (3) и `title` (2) без фаз; `how`: «Опыт CD/17:» → «На одной сцене:» | 2 → 1 |
| `zveno/gallery-Z.json` | `cost` (4), `how` (2) без Z2, Z3; «к H4m фазы 1» → «к кадру H4m» | 4 → 1 |
| `{sdano,zveno}/*/_shared/fonts.css` (6) | шапка без «агент J · волна 3 · дата»; `[проверено: 99-raw/…/fallback_metrics.py → …json]` → `[проверено]`; «Способ — D (…)» → «Способ — creative 04-visual-language/marketing-tokens.css» | 2 → 0 |
| `{sdano,zveno}/*/_shared/marketing-tokens.css` (6) | шапка: «creative-research … · D · дата» → «creative …»; `[проверено: 99-raw/…/D/01-clamp-display (строки, зум), D/03-font-swap-cls (метрический фолбэк)]` → `[проверено: строки, зум, метрический фолбэк]`; `[проверено: D/03]`, `[проверено: 99-raw/…/E/01-lcp-reveal]` → `[проверено]`; «E (волна 2)» (2), «D/02» сняты; `ui-research 08-motion` → `ui 08-motion` | 10 → 1 |
| `sdano/*/index.html` (3) | штамп без агента, волны, даты, «15-showcase … фаза 2 · дорожка SD»; рецепт — `creative 10-recipes/01-lead-services-l0.md`; «F2:», «SD2/SD3» сняты; видимый текст: «базы creative-research» → «базы creative» (`meta description`, подвал) | 3 → 0, 5 → 0, 5 → 0 |
| `sdano/*/style.css` (3) | шапка без «агент J · дата»; «kimi T8» → «правило исполнителя макета»; сняты «J1:», «(SD3)», «(SD2/SD3)», «SD3:», «15-showcase … фаза 2 · дорожка SD» | 2 → 0, 4 → 0, 5 → 1 |
| `sdano/*/motion-spec.yaml` (3) | шапка: штамп снят; команды проверки → `$DDD_HOME/venv/bin/python scripts/creative/spec_check.py spec <файл>`, `python3 scripts/creative/motion_check.py …`; `unit_note`, `note`: «(SD3)», «решение оркестратора SD3 (2):» сняты; C: комментарий бюджета петель без «SD4 (26.09 05:45)», «прогона SD3 04:55»; A: `refs.tokens`, `effects`, `block_treatments` → `../../../../creative/…` | 4 → 0, 6 → 1, 7 → 2 |
| `sdano/numbers.json` | заметки: id сессий, время запуска и `scripts/*.py` сырья сняты (`note` 2, `when` 3, `cmd` 2, `shot`, `video`, `bench_window`, `note_noise`, `SD3_from_to`); `phase` → «1 + 2 + ночь»; снят лист `…/sd3_run_04_55/copy` (путь `99-raw`) | 4 → 2 |
| `velmora/ai/01-mouse-scrub/index.html` | комментарий: «Агент B, сессия 4, дата. Сборка ассетов — 99-raw/…/build_scrub.py» снят; подвал: «ai-media-research, фаза 5, сессия 4 (25.09.2026)» → «ai-media»; четыре ссылки в пустоту сняты (решение 6) | 6 → 0 |
| `velmora/{ai,b-blender}/css/demos.css` (2) | шапка без «(агент B, сессия 4, дата)» | 2 → 0 |
| `velmora/ai/js/hero-video.js` | «канон J …» → «канон — ai-media `10-web-integration/pages/js/hero-video.js`» (файл есть); штамп снят | 2 → 0 |
| `velmora/{ai,b-blender}/js/scrub.js` (2) | штамп снят; «build_scrub.py» → «веса и пути ассетов»; «замер B/10» → «замер» | 3 → 0 |
| `velmora/b-blender/index.html` | комментарий: «Дорожка VD, фазы 2–3, даты. Сборка — 99-raw/experiments/VD/ (…)» снят; «VD3 (26.09, ворота телефона):» снят; подвал без «15-showcase, дорожка VD, фазы 2–3 (даты)» | 4 → 0 |
| `zveno/*/index.html` (3) | штамп без агента, волны, даты; рецепт — `creative 10-recipes/03-product-launch-l2.md`; B, C: без «15-showcase», «дорожка Z2, дата», «дорожка CD», «дорожка Z»; «F2» (2) сняты; видимый текст: «базы creative-research» → «базы creative» | 3 → 0, 4 → 0, 6 → 0 |
| `zveno/{a-code,c-hybrid}/js/main.js` (2) | шапка: «агент J · дата», «CD (15-showcase, дата, …)», «как у J», «J2 (… 99-raw/…/scene.js)», «дорожки Z2→Z3, 15-showcase», «CD3, 26.09 01:36» сняты; в теле: «CD2:», «(фаза 1)», «CD3 (фаза 3):», «F2», «(Z3, 26.09)» | 7 → 3 |
| `zveno/b-blender/js/main.js` | шапка без «дорожка Z2 испытания 15-showcase · дата» | 1 → 0 |
| `zveno/*/js/motion.js` (3) | шапка без «продолжатель F2 · дата»; «по E 05-motion/01 §4.4» → «по creative 05/01 §4.4»; «токены --mm-* E» → «токены --mm-*» | 1 → 0 |
| `zveno/*/style.css` (3) | шапка без «агент J · дата»; сняты «J2:», «кадры J/04 `out/…jpg`», «, D», «кадры J/02, прогон 1:», «(J/00)» | 3 → 0 |
| `zveno/*/motion-spec.yaml` (3) | шапка и команды проверки — как у sdano; «CD (15-showcase, дата, вариант A «код v3»):» → «Вариант A «код v3»:»; «в прогоне K — …, 99-raw/…, прогон 1» → «в отчёте зонда»; снят `storyboard.sheets` (единственное значение — путь `99-raw`); `open_questions`: «(shoot_stations.py I/02)» снято, запись MS-05 — в текущем состоянии, без «прогон J2 0.1.3», «(F)», «(I)», «CONTRADICTIONS.md X-64 (X2, дата)», «Закрыто S1b …»; A, C — так же комментарий MS-05 у `hero-wake`; B — без «решение задания Z2»; `refs.tokens`, `effects`, `block_treatments` → `../../../../creative/…`, у B — и `page_plan` | 9 → 0, 10 → 0, 9 → 0 |
| `zveno/numbers.json` | `target` (2): путь машины → `b-blender/index.html`, `c-hybrid/index.html`; `out` (2, машина + `99-raw`) сняты; заметки без «(out/engine)», «CD3 01:36», «(замер CD3)»; снят блок `b-blender.frames` (2 кадра `judge/…`) | 12 → 0 |
| `zveno/a-code/numbers.json` | `title` (3) без «(дорожка CD)»; `target` (3) → `index.html`; `source` (2), `hybrid_hook.path` → `../../_shared/code3d/…`; сняты 48 листьев: 27 путей сырья — `motion_check_L2.*.out` (3), `marketing_audit_L2_00_54.report`, `gates_dir`, `files.sheets` трёх фаз (19 путей), `hybrid_hook.test_glb`, `.frames`, `.sheet` — и три списка `files.judge` (21 кадр `zveno/judge/`), блоки `files` сняты целиком; заметки без «CD/15», «J/04», «(сборка 26.09 01:36)», «(out/kb.json)», «(см. NOTES)» | 71 → 7 |
| `keyboard/numbers.json` (добавлен) | `A_code.frame`: `05-code-a/a_H1_v6.png` → `a_H1_v6.png`; `atlas_webp_vs_ktx2.what` без «KB2», «KB3»; `loaf_probe_KB3.probe` без `10-check/loaf_probe.py —`; сняты 3 листа с путями сырья: `atlas_webp_vs_ktx2.evidence`, `before_KB2_motion_check_c_desk.src`, `trigger_timing_desk.src` | 0 → 0 |
| `velmora/numbers.json` (добавлен) | заметки: `phase1.machine.note` без «журнал .locks/slot_run.log, метки VD-*»; `phase2.note` без «(VD2, 25.09 20:13–21:36)», «(VD3, 26.09 ночь)»; `phase2.scene`: «velmora_v6_final.py (i3)» → «сцена i3»; `full_spp_test` без «(07-orbit/full_spp_test.json, full_t64/…png)» | 0 → 0 |
| `velmora/judge/metrics.json` (добавлен) | `phase`: «3 (VD3, 26.09.2026): …» → «3: …»; сняты 4 листа `views.*.b-blender_src` (пути сырья `07-orbit/…png`) | 0 → 0 |
| `velmora/b-blender/assets/manifest.json`, `…/full360/manifest.json`, `velmora/ai/01-mouse-scrub/assets/manifest.json` (добавлены) | без правок: путей сырья и машины нет; `source` — описание ассета с датой рендера и id генерации SC-03, слово в слово со встроенным манифестом страницы | 0 → 0 |

Итог по классам (76 файлов списка): `machine` 10 → 0; `raw` 68 → 0; `kimi` 3 → 0; `research` 41 → 0; `process` 105 → 0;
`showcase` 41 → 0; `words` 11 → 0; `letters` 103 → 93; сумма 382 → 93. Шесть добавленных файлов: 0 → 0 — их следы образцы
сканера не ловят.

Видимый текст страниц изменён в 14 строках восьми `index.html`: `meta description` и подвал `foot__demo` шести страниц
sdano и zveno («базы creative-research» → «базы creative»), подвалы двух страниц velmora. На странице нейросети velmora
сняты четыре ссылки, текст на месте. Остальной дифф HTML — комментарии.

## `refs` спецификаций (решение 4)

Файлы-цели есть все: `creative/10-recipes/recipes/01-lead-services-l0.recipe.yaml`, `…/03-product-launch-l2.recipe.yaml`,
`creative/04-visual-language/marketing-tokens.json`, `creative/06-effects-catalog/effects.yaml`,
`creative/09-ai-execution-evaluation/block-treatments.yaml`. Переведены на `../../../../creative/…` и разрешаются 13 путей:
`tokens`, `effects`, `block_treatments` в четырёх спецификациях и `page_plan` у `zveno/b-blender`.

Оставлены как были три `page_plan` — `sdano/a-code`, `zveno/a-code`, `zveno/c-hybrid` (`../../recipes/…recipe.yaml`, не
разрешается): с планом `spec_check.py` даёт новые находки. Вывод «до → после» (`checks/spec-full-before.txt`,
`spec-full-after.txt`, проба с ключом `--plan` — `checks/spec-plan-sim.txt`):

| спецификация | до | после (как в дереве) | если перевести и `page_plan` (проба `--plan`) |
|---|---|---|---|
| `sdano/a-code` | error 0, warning 0, info 0 | то же | error 4: MS-03 `page.lcp: target hero.headline не найден в плане`; MS-01 «секции нет в плане (id v1)» — `hero`, `faq`, `sticky-cta` |
| `zveno/a-code`, `zveno/c-hybrid` | error 2: MS-24 `uniform:uWake`, `uniform:uStory` | то же | error 7: те же 2 и MS-03 `target hero.hero-visual не найден в плане`; MS-01 — `hero`, `story-modules`, `story-inside`, `product-demo` |
| `zveno/b-blender` | error 2: MS-S `canvas:frame` (2) | то же | `page_plan` переведён: ошибки схемы останавливают проверку до сверки с планом |
| `sdano/b-blender`, `sdano/c-hybrid` (не менялись) | error 5 и error 8, info MS-00 | то же | — |

Те же 4 и 7 находок дают исходники в базе creative на своём месте (`creative/10-recipes/examples/l0-sdano/motion-spec.yaml`,
`…/l2-zveno/motion-spec.yaml`): расхождение — между id секций примеров и планами рецептов, не в путях.

## Остаток маркеров

Все 93 — класс-подсказка `letters`, следов процесса среди них нет.

- Код — имя переменной или параметра в скобках (54):
  `_shared/code3d/src/glb-modules.js:44, 49` (K); `ik.js:19` (A); `ktx2.js:19` (L); `modules-code.js:135, 150, 161, 168, 172, 179, 187, 195` (D);
  `scene.js:102, 286, 339` (G, O); `world.js:166, 169, 170` (N); `keyboard/*/src/model_a.js:69, 92, 200, 232, 255, 307` (T0, P — 3 копии);
  `keyboard/*/src/stage3d.js:16, 89, 104, 135` (J, L, W, H — 3 копии); `zveno/{a-code,c-hybrid}/js/main.js:70, 82, 93` и `:72, 84, 95` (S).
- Вариант страницы A, B, C (19): `keyboard/*/src/model_a.js:294, 365` (3 копии); `keyboard/*/src/model_c.js:23` (3 копии); `keyboard/gallery.json:17, 19, 72`;
  `sdano/gallery.json:8, 58`; `sdano/numbers.json:485, 679`; `sdano/b-blender/motion-spec.yaml:174`; `sdano/c-hybrid/motion-spec.yaml:218`;
  `zveno/gallery-CD.json:87`.
- Уровень амбиции L0, L1, L2 (8): `{sdano,zveno}/*/_shared/marketing-tokens.css:48` (6); `sdano/c-hybrid/style.css:279`;
  `sdano/c-hybrid/motion-spec.yaml:3`.
- Схема света S2, S3 из `art-direction.md` предмета (4): `keyboard/*/src/capture.js:24` (3); `velmora/gallery.json:30`.
- Строка видеокарты «Intel(R) Iris(R)» (7): `zveno/a-code/numbers.json:779, 876, 973, 1076, 1190, 1293, 1396`.
- Вызов `build(P)` в описании приёма (1): `zveno/gallery-Z.json:61`.

Вне классов сканера оставлено решениями 1–3:

- «фаза 1», «фаза 2», «фаза 3» в комментариях кода `_shared/code3d/src/`: `scene.js:3, 4, 32, 50, 141, 322, 326`; `studio.js:3, 30, 41, 42`;
  `post.js:36, 39`; `modules-code.js:12, 78`; `ik.js:10`; `world.js:17` — имя вида сцены `LOOKS.p1`, `p2`, `p3`.
- `numbers.json` четырёх предметов — учёт времени и прогонов по сессиям: ключи и время суток (раздел ниже).
- `checked_at: "2026-09-25"` в шести `motion-spec.yaml` — поле схемы; «(npm, 2026-09-25)» в `fonts.css` — дата версий пакетов.

## Ключи и значения, которые читает код

- `_shared/code3d/src/scene.js:29` — `export const version = 'zveno-scene v3 (CD, _shared/code3d) 2026-09-25'`: значение отдаёт
  API сцены (`createScene().version`), в нём буквы дорожки и дата. Не тронуто (решение 3).
- `_shared/code3d/build.sh` и `src/*.js` — имена `__CD_STUDIO__`, `__CD_IK__`, `__CD_WORLD__`, `__CD_POST__`, `__CD_DETAIL__`, `__CD_GLB__`,
  `__CD_KTX2__`, `__CD_BEAM__`, `__CD_TRAIL__` (define сборки): буквы дорожки в именах кода. Не тронуты.
- Строки консоли: `zveno/a-code/js/main.js:77`, `zveno/c-hybrid/js/main.js:79` — `'CD timing '`; `sdano/b-blender/index.html:247`,
  `sdano/c-hybrid/index.html:249` — `'SD stamp'`; `velmora/b-blender/index.html:193` — `'VD timing hero-first-frame '`
  (на строку ссылается `velmora/README.md:123`). Не тронуты (решение 3); комментарий «строка «CD timing» в консоль» оставлен под код.
- `refs.page_plan` трёх спецификаций — раздел выше.
- Имена файлов `zveno/gallery-CD.json`, `zveno/gallery-Z.json` и id записей `cd-a-*`, `z-b-*`, `z-c-*` — буквы дорожек; на файлы
  ссылаются README предмета. Не тронуты.
- Ключи `numbers.json` (решение 2): `lane` («SD», «KB»), `track` («Z», «VD»), `tracks` («Z2 (25.09 20:17–21:36) → Z3 …»,
  «… + CD2/CD3 …»), `SD2`, `SD3`, `SD4`, `SD2_from_to`, `SD3_from_to`, `SD4_from_to`, `SD_phase2_from_to`, `SD3_queue_wait_gates_A_s`,
  `c_fonarik_sd2`, `sd3_run_04_55`, `z_machine_phase2.Z2`, `.Z3` и 35 ключей `Z2-*`, `Z3-*`; у keyboard — `queue_KB3`,
  `loaf_probe_KB3`, `before_KB2_motion_check_c_desk`, `after_KB3`, `gates_KB2_c_before_fixes`, `agent_time.KB`, `.KB2`, `.KB3` и
  ключи очереди `KB-*`, `KB2-*`, `KB3-*`; у velmora — `agent_clock_vd2`, `agent_clock_vd3`, `machine_vd2`; общие — `phase`, `phase1`,
  `phase2`, `night`, `experiments_phase3`, `*_phase3`, `agent_clock*`, `agent_time`, `updated`, `date`, `when`, время суток `t0`,
  `first_batch_t`, `last_batch_t`. На `phase2`, `night`, `b-blender` ссылаются `sdano/README.md:144` и `zveno/README.md:51`.
  Код `scripts/` файлы не читает. Не тронуты.
- Манифесты `scrub-manifest`: встроенные — `velmora/ai/01-mouse-scrub/index.html:169` (`source`: «SC-03 · … · 25.09.2026»),
  `velmora/b-blender/index.html:174, 175` (`source` с датой рендера) — и три файла `manifest.json` с тем же текстом; id генерации
  SC-03 — и в комментарии `:2`, и в тексте `:106`. Поле `source` скрипт `scrub.js` не читает. Не тронуто.

Имена файлов без папки, которых в базе нет (не пути сырья, оставлены): `velmora/judge/metrics.json` — `first_screen.ai`,
`first_screen.b-blender` (`…__first-screen-desk.png`; в `velmora/judge/` лежит только `metrics.json`);
`keyboard/numbers.json` — `main_face.frame` (`hero_H1.png`, `a_H1_v6.png`); `sdano/numbers.json` — `night.judge.video`
(«c-hybrid__fonarik-10s.webm — …»). Ассеты страниц (шрифты, кадры, постеры, GLB) в базу не входят — ссылки страниц на них
к следам не отношу.

Сняты листья данных — 63, код их не читает; в md базы blender снятые ключи не упоминаются:
пути сырья — 40: `sdano/numbers.json` — `copy` (1); `zveno/numbers.json` — `out` (2); `zveno/a-code/numbers.json` — 27;
`zveno/*/motion-spec.yaml` — `storyboard.sheets` (3, ключ схемой не обязателен); `keyboard/numbers.json` — `evidence`, `src` (3);
`velmora/judge/metrics.json` — `b-blender_src` (4); кадры `zveno/judge/` — 23: `zveno/a-code/numbers.json` — `files.judge`
трёх фаз (21), `zveno/numbers.json` — `b-blender.frames` (2).

## Производные

Файлов из перечня брифа в списке нет. `numbers.json` и `gallery*.json` писали генераторы сырья
(`99-raw/experiments/{CD,Z,SD}/write_numbers*.py`, `make_gallery_z.py` и соседние) — правка сделана руками; повторный запуск
генератора вернёт пути и id сессий.

## Для фикстур

Нет: `scripts/maint/fixture_gen.py build --all --check` — все наборы совпадают; файлов зоны фикстуры не содержат.

## Для текстов

- md витрины со следами (строк с «дорожка», id сессий, `99-raw`, `npm-trial`): `VERDICT.md` — 92, `KIT.md` — 33,
  `sdano/README.md` — 29, `zveno/README.md` — 28, `keyboard/README.md` — 17, `velmora/README.md` — 16,
  `_shared/code3d/README.md` — 12, `_shared/code3d/CHANGELOG.md` — 7 (журнал версий), `zveno/a-code/README.md` — 5.
- `_shared/code3d/README.md`: «npm-trial» — в `build.sh` теперь «npm-зависимости скилла»; «Пишет только дорожка CD»;
  «паспорт Z» — в коде теперь `zveno/art-direction.md §4`.
- `keyboard/README.md:59, 90, 132` — пути сырья `10-check/…`, `12-metrics/…` (в `numbers.json` те же пути сняты).
- `zveno/art-direction.md:119–159` называет кадры и листы `judge/` (`b-blender__*.png`, `sheet_z_*.jpg`); `judge/` упоминают и
  README: sdano — 4 строки, keyboard — 6, velmora — 7. В базе есть только `velmora/judge/metrics.json`; списки кадров
  `zveno/judge/` из `numbers.json` сняты.
- Копии тех же файлов в базе creative (`04-visual-language/marketing-tokens.css`, `10-recipes/examples/_shared/{fonts,marketing-tokens}.css`,
  `10-recipes/examples/{l0-sdano,l2-zveno}/…`) — зона Д-creative: формулировки копий витрины — в таблице выше, для сведения к одним словам.

## Файлы к снятию

В списке зоны — нет.

## Проверки

- Разбор: 14 JSON (8 списка и 6 добавленных) и 6 YAML читаются; сверка листьев данных с `1e0cd2a` — чисел изменено 0, снято
  63 листа, строковых значений изменено 101 (`checks/jsondiff.txt`).
- `scripts/creative/spec_check.py spec` на шести спецификациях — полный вывод до и после совпадает, новых находок нет.
- `node --check` — 33 из 33; `bash -n build.sh` — чисто; дифф вне комментариев: `.js` 0 из 33, `.css` 0 из 20, `.sh` 0 из 1.
- `scripts/tests/smoke.py --only blender` — PASS 86, FAIL 0 (строк с браузером в списках нет).
- `scripts/maint/sync_check.py` — генераторы OK 17, FAIL 0; копий расходится 0.
- `scripts/maint/fixture_gen.py build --all --check` — совпадает.
- `kbscan.py`: список зоны 382 → 93 (`letters`); шесть добавленных файлов 0 → 0.
- `scripts/maint/accept.py --base 1e0cd2a --masks-file …/Д-blender-2.masks` и шесть `--mask` добавленных файлов — под масками
  73 файла: разбор 17 — OK, код — OK, следы — OK, ссылки — OK; строка «маски» — FAIL из-за файлов других зон в общем дереве
  (вне масок на момент прогона 300) и 9 масок без изменений (`keyboard/*/src/capture.js`, `stage3d.js`, три `manifest.json`).

## Вопросы

1. `page_plan` в `sdano/a-code`, `zveno/a-code`, `zveno/c-hybrid`: перевести на `../../../../creative/10-recipes/recipes/…` и
   принять 4, 5 и 5 новых находок `spec_check.py` (MS-03, MS-01 — те же, что у исходников в creative) или оставить
   неразрешаемым, как сейчас? У `zveno/b-blender` путь переведён: сверку с планом там закрывают две ошибки схемы MS-S.
