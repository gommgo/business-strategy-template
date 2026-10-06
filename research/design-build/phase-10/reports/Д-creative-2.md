# Д-creative-2 — машинные файлы базы creative (все папки, кроме 06, 07, 08): следы процесса исследования

Зона данных Ф10. Коммит начала — `1e0cd2a`. Список зоны — `code-zones/Д-creative-2.tsv` (45 файлов), маски —
`Д-creative-2.masks`. Замены — 20 пакетов точных замен (`kbpatch.py`), 505 замен в 45 файлах; файлы замен и выводы
проверок — `$DDD_HOME/out/f10/Д-creative-2/` (`patches/`, `HANDOFF.md`, `kbscan-before.txt`, `kbscan-after.txt`).

## Итог

- Пройдено 45 файлов из 45; изменены все 45; вне списка зоны правок нет (`l2-zveno/js/three-scene.js` не тронут).
- Маркеры `kbscan.py` по зоне, «было → стало»: `raw` 42 → 0 · `kimi` 72 → 0 · `k3` 11 → 0 · `research` 58 → 0 ·
  `process` 170 → 0 · `decision` 10 → 0 · `plan` 3 → 0; подсказки `letters` 86 → 32 · `words` 28 → 16 (остаток — не
  следы, см. «Остаток»).
- Сверх счётчика — три прохода своим поиском (буква исполнителя без скобок, буква перед знаком препинания, слова
  истории «было / против v0 / замена X»): счётчик таких мест не видит, они сняты по тем же правилам.

## Как решены повторяющиеся случаи

- **Буква исполнителя → адрес базы.** `E 05-motion/01 §4.5`, `E 02 §8.3`, `E §4.5` → `creative 05/01 §4.5`,
  `creative 05/02 §8.3`; `G 07/02`, `G 01 §10` → `creative 07/02`, `creative 07/01 §10`; `D 02 §2.1` →
  `creative 04/02 §2.1`; `H 01 §6`, `H 08/02 §3.2` → `creative 08/01 §6`, `creative 08/02 §3.2`;
  `C 03-live-sites-measured/02` → `creative 03/02`; `B 02-references-moodboards/03` → `creative 02/03`;
  `F 03-effects-lab-method` → `creative 06/03`. Буква без адреса: стоит после имени файла («effects.yaml (F)») —
  снята; стоит вместо источника нормы («нормы — E», «[данные: C]», «библиотеки B») — папка базы или слова
  (`05-motion/`, `[данные: creative 03]`, «библиотеки референсов»). Каждый поставленный адрес сверен с заголовком
  статьи.
- **Id опыта → адрес нормы или снят.** `E/01` → `creative 05/02 §10`; `E/02` → `creative 05/02 §3.5`; `G/01` →
  `creative 07/01 §1.1`; `G/02`, `G/03`, «ворота G (N)» → `creative 07/02 §2, §6, §7.2, §8`; `F2/12` →
  `creative 06/01` и `06/03 §7.3`; `blender A/03` → `blender 01/03` (числа бандлов сверены с таблицей статьи);
  `A/04`, `A/07`, `D/01…03`, `I/02`, `J/0N`, `K/02`, `K/03`, `B/01`, `B/02` — сняты, числа и условия оставлены.
- **«Контракт тройки v2 §N»** → `kb/common/owners.md` с разделом: «Форматы обмена, № 5 / № 7 / № 12» (номера
  форматов совпадают), «Темы», «Правила владения» (иерархия ворот), «Общие правила тройки» (префикс `CRV-`,
  конвенции взаимодействия). «Контракт v2 §8 (предложение kimi)» и точка согласования «C1 … §5» — сняты.
- **Прежний исполнитель макета.** В описаниях — «бриф холста», «вход холста», «утилита макета»,
  «исполнитель макета», «LLM-вёрстка»; отсылки к прежней базе: `kimi 07/03 §1` → `cd 06/02 §3`,
  `kimi 07/01 §2.4` → `cd 06/01 §5`, `kimi 03/04 T2a` → `creative 01/01 §6` (те же адреса стоят в схеме v1);
  прочие (`kimi 05/03`, `07/01 §4.1`, `07/03 §4.4`, `08/02 п.6`, `T7`, `T8`) — сняты, вывод оставлен. «Примета K3
  <ключ>» → id приметы реестра `kb/common/tells.yaml` (`stats` → `stats-row`, `serif` → `overused-display-font`,
  `warm` → `warm-paper`); `k3_checks.py` → «утилита макета (kb/common/tells.yaml#checks)».
- **Id реестра противоречий базы** (`X-21`, `X-57`, `X-63`, `X-64` — `creative/CONTRADICTIONS.md`) оставлены как
  адреса; слова рядом («решение оркестратора 2026-09-25», `S1`, `S1b`, `X2`) сняты.
- **Журналы и штампы.** Сняты: штамп в шапке 28 файлов; `changes` в `effect-gates.yaml`; `x-revision`
  в `otves-home.motion-spec.yaml`; строка `sync_point`. `owner` / `x-owner` / `author` — «creative · <папка>».
  `lifecycle.history` примеров не тронут, кроме id опыта в `by` («Claude (пример A/01)» → «Claude (пример)») и
  буквы в `change`.
- **Пути.** `99-raw/tools/venv-I|J/bin/python` → `$DDD_HOME/venv/bin/python`; пути сырья в комментариях, полях
  `source`, `via`, `rules`, `sources` сняты вместе с тире; метки `[проверено: 99-raw/…]` → `[проверено: условия]`
  или `[проверено]`.
- **Шапки «против v0 / было / что изменено»** в двух примерах подачи и история предупреждения MS-05 в
  `l2-zveno/motion-spec.yaml` переписаны текущим состоянием — те же факты без «было».

## Файлы

| файл (от `kb/creative/`) | что сделано | замен | маркеры до | после |
|---|---|---|---|---|
| `01-creative-direction/ambition-levels.yaml` | сокращение опыта и путь сырья в шапке; `source`/`label`: соседние базы без суффикса, `PLAN.md`, id опытов blender → `blender 01/03`, «контракт тройки» → `kb/common/owners.md`, номера решений, «решение оркестратора» | 21 | raw 1; research 4; process 8; decision 2; plan 3; letters 3; words 1 | letters 3 |
| `01-creative-direction/art-direction.schema.json` | описания и `x-owner`: формат обмена № 5, буквы → адреса базы, имя прежнего исполнителя → «бриф холста», приметы → `kb/common/tells.yaml`; блок `handoff.kimi` снят | 28 | kimi 9; k3 2; research 2; process 4; words 3 | words 3 |
| `01-creative-direction/drafts-for-site/site-brief-creative-fields.yaml` | штамп, `owner`, строка `sync_point`, блок `kimi_crosswalk` с шапкой раздела (секции комментариев перенумерованы), имя прежнего исполнителя, номера решений, буквы, путь `99-raw` | 41 | raw 3; kimi 47; research 5; process 5; decision 1; letters 3; words 1 | letters 2 |
| `01-creative-direction/drafts-for-site/treatment.v0.schema.json` | описание, `x-status`, `x-owner`, заметка об id v0; блок `x-kimi-projection` снят; буквы и «волны» в описаниях полей | 24 | raw 1; kimi 5; research 2; process 8; letters 5 | 0 |
| `01-creative-direction/examples/art-direction-forest-roast-l0.json` | «опыт A/01», номер решения, «после фазы 5», примета → `stats-row`, заметки о замене гарнитур без даты и буквы, `history[].by` без id опыта | 7 | k3 1; process 3; decision 1; words 2 | words 2 |
| `01-creative-direction/examples/art-direction-forest-roast-l2.json` | «опыт A/01», номер решения, заметка о замене гарнитуры, `history[].by` | 3 | process 2; decision 1; words 1 | words 1 |
| `01-creative-direction/examples/art-direction-kvarts.json` | номер решения, отсылки к прежней базе, приметы → id реестра примет, `d_refs` без буквы, `blender A/03` → `blender 01/03`, `text B2` → `text 08/01` | 10 | kimi 2; k3 2; process 3; letters 1; words 3 | letters 1; words 3 |
| `01-creative-direction/examples/art-direction-okoshko.json` | `refs.brief/facts/page_plans` → существующие файлы site и text; номер решения, приметы, `technique` «k3:stats» → «примета stats-row», `history[].by` | 10 | raw 2; kimi 1; k3 1; research 3; process 1; decision 1; words 1 | words 1 |
| `01-creative-direction/examples/art-direction-otves.json` | `refs.brief/page_plans` → существующие файлы site; номера решений, приметы, `history` | 7 | k3 2; research 2; process 1; words 1 | words 1 |
| `02-references-moodboards/library-example/library.jsonl` | запись 2: буква в `notes`, «PLAN «Поправки»» в `dont_take` | 2 | letters 1 | 0 |
| `02-references-moodboards/refs-library.schema.json` | заголовок, описание (формат обмена № 7, штамп), буквы в описаниях полей | 6 | research 1; process 2; letters 1 | 0 |
| `02-references-moodboards/sources.yaml` | штамп, `owner`, легенда `alive`; id опытов в `alive`/`adapter` (41 запись), «фундамент», «разведка оркестратора», «кэш других агентов», «агент V», «трек V» | 25 | research 2; process 41; decision 1; letters 3; words 6 | letters 2 |
| `04-visual-language/cyrillic-display-fonts.yaml` | штамп, номер решения, `owner`, пути сырья в `sources`, id опытов в заметках, буквы; фраза шапки с запасом трекинга не тронута | 19 | raw 3; research 3; process 10; decision 1 | 0 |
| `04-visual-language/marketing-tokens.css` | штампы двух блоков, метка `[проверено: …]` без пути, id опыта, `ui-research` | 6 | raw 1; research 2; process 4; letters 1 | letters 1 |
| `04-visual-language/marketing-tokens.json` | пути сырья в `wcag_1_4_4_rule` и `rules`, `ui-research`, `owner` блока движения, метка сессии, буквы в описаниях | 9 | raw 2; research 1; letters 1 | letters 1 |
| `09-ai-execution-evaluation/art-direction.v1.schema.json` | буквы и номера решений в описаниях полей → адреса базы | 13 | letters 1; words 4 | words 4 |
| `09-ai-execution-evaluation/block-treatments.yaml` | штамп, `owner`, `sources` и `conventions` без букв, буквы в заметках → адреса, метки точек согласования (`C3:`, «C9, ответ на пакет W4») | 25 | research 2; process 2; letters 14 | letters 7 |
| `09-ai-execution-evaluation/effect-gates.yaml` | штамп, `owner`, журнал `changes`, `neighbours.kimi`; `source`/`label`/`fix`/`method` ворот: буквы → адреса, id опытов → адреса норм, «контракт» → `owners.md` | 63 | raw 2; kimi 3; k3 1; research 3; process 25; letters 22; words 2 | letters 8 |
| `09-ai-execution-evaluation/effectiveness.rubric.json` | `status`, `author`, соседние базы, якоря медиа и источники без путей сырья и id опытов, буквы → адреса | 27 | raw 4; research 2; process 6; letters 8 | 0 |
| `09-ai-execution-evaluation/examples/art-direction-okoshko.v1.json` | как у `art-direction-okoshko.json`; заметки о замене гарнитур без «v1: X → Y» | 10 | raw 2; kimi 1; k3 1; research 3; process 1; decision 1; words 1 | words 1 |
| `09-ai-execution-evaluation/examples/okoshko-home.motion-spec.yaml` | штамп, «уроки опыта», буква в открытом вопросе | 3 | research 1; process 2 | 0 |
| `09-ai-execution-evaluation/examples/okoshko-home.treatment.yaml` | штамп; шапка «против treatment v0 / было» — текущим состоянием, буквы → адреса | 2 | research 1; process 1 | 0 |
| `09-ai-execution-evaluation/examples/otves-home.motion-spec.yaml` | штамп, путь сырья, `x-revision` снят, id опыта в заметках, буквы | 8 | raw 2; research 1; process 4; letters 1 | letters 1 |
| `09-ai-execution-evaluation/examples/otves-home.treatment.yaml` | штамп, путь окружения → `$DDD_HOME/venv`, шапка «что изменено против v0» — текущим состоянием | 3 | raw 1; research 1; process 1 | 0 |
| `09-ai-execution-evaluation/examples/stalkon-home.motion-spec.yaml` | штамп, буквы → адреса, «решение оркестратора», «до S1» | 4 | research 1; process 1; letters 1; words 1 | letters 1 |
| `09-ai-execution-evaluation/examples/stalkon-home.treatment.yaml` | штамп, буквы → адреса | 3 | research 1; process 1; letters 2 | letters 1 |
| `09-ai-execution-evaluation/motion-spec.schema.json` | строки зоны кода К4в (`refs.tokens`, `$defs.token-ref`); буквы и id опытов в описаниях → адреса, `x-dom-contract.attributes` | 20 | process 4; letters 4 | 0 |
| `09-ai-execution-evaluation/treatment.schema.json` | буквы в описаниях → адреса базы | 15 | letters 5 | 0 |
| `10-recipes/examples/_shared/fonts.css` | штамп, метка `[проверено]` без пути, буква | 2 | raw 1; process 1 | 0 |
| `10-recipes/examples/_shared/marketing-tokens.css` | копия `04-visual-language/marketing-tokens.css` — те же правки, копии совпадают | 6 | raw 1; research 2; process 4; letters 1 | letters 1 |
| `10-recipes/examples/l0-sdano/index.html` | штамп-комментарий, `creative-research` в мета и подвале, буква | 4 | research 2; process 1 | 0 |
| `10-recipes/examples/l0-sdano/motion-spec.yaml` | штамп, путь окружения, буква → адрес | 3 | raw 1; research 1; process 1 | 0 |
| `10-recipes/examples/l0-sdano/style.css` | штамп, отсылка к прежней базе, буквы → адреса | 5 | kimi 1; process 1 | 0 |
| `10-recipes/examples/l1-sverka/index.html` | штамп-комментарий, `creative-research` в мета и подвале | 3 | research 2; process 1 | 0 |
| `10-recipes/examples/l1-sverka/motion-spec.yaml` | штамп, путь окружения, пути сырья и id прогонов | 5 | raw 3; research 1; process 2 | 0 |
| `10-recipes/examples/l1-sverka/style.css` | штамп, буквы и id опытов в комментариях | 5 | process 3; letters 1 | 0 |
| `10-recipes/examples/l2-zveno/index.html` | штамп-комментарий, `creative-research`, буквы | 5 | research 2; process 1 | 0 |
| `10-recipes/examples/l2-zveno/js/main.js` | штамп, путь сырья в комментарии, буква | 3 | raw 1; process 1; letters 3 | letters 3 |
| `10-recipes/examples/l2-zveno/js/motion.js` | штамп, буквы → адрес | 3 | words 1 | 0 |
| `10-recipes/examples/l2-zveno/motion-spec.yaml` | штамп, путь окружения, история MS-05 — текущим состоянием, `storyboard.sheets` и закрытый открытый вопрос сняты | 7 | raw 3; research 1; process 2; letters 1 | 0 |
| `10-recipes/examples/l2-zveno/style.css` | штамп, буквы и id опытов в комментариях | 4 | process 3 | 0 |
| `10-recipes/recipes/01-lead-services-l0.recipe.yaml` | штамп, номер решения, `inputs.kimi` и `example.gates` сняты, буквы, id опытов в `result` | 10 | raw 2; kimi 1; k3 1; research 2; process 3; decision 1; letters 1 | 0 |
| `10-recipes/recipes/02-saas-l1.recipe.yaml` | штамп, номер решения, `example.gates` снят, id опытов | 8 | raw 2; process 3 | 0 |
| `10-recipes/recipes/03-product-launch-l2.recipe.yaml` | штамп, `inputs.kimi` и `example.gates` сняты, буквы, пути сырья в `result` | 13 | raw 3; kimi 1; research 1; process 2; letters 2 | 0 |
| `10-recipes/recipes/recipe.schema.json` | заголовок, описание (путь окружения, буквы), свойство `inputs.kimi` снято | 5 | raw 1; kimi 1; research 1; process 1 | 0 |

## Остаток маркеров

Целевых классов — 0. Подсказки (`letters` 32, `words` 16) — не следы:

- `letters`, уровень подачи или заголовка в скобках — «(L0)», «(L1)», «(L2)», «(H2)», «у L0»:
  `ambition-levels.yaml:314`, `site-brief-creative-fields.yaml:241, 256`, `art-direction-kvarts.json:35`,
  `marketing-tokens.css:48` и копия `_shared/marketing-tokens.css:48`, `marketing-tokens.json:68`,
  `block-treatments.yaml:291, 378, 390, 469, 619, 665, 678`, `otves-home.motion-spec.yaml:1`,
  `stalkon-home.motion-spec.yaml:1`, `stalkon-home.treatment.yaml:1`.
- `letters`, уровень соответствия WCAG «(A)»: `ambition-levels.yaml:46, 50`, `effect-gates.yaml:316, 349`.
- `letters`, серьёзность ворот «(B)», «(S)»: `effect-gates.yaml:130, 141, 318, 362, 554, 608`.
- `letters`, номера пунктов условий площадки «8(F)», «8(I)», «8(B)»: `sources.yaml:1114, 1116`.
- `letters`, переменная `S` в коде (`if (S)`, `done(S)`): `l2-zveno/js/main.js:56, 66, 77`.
- `words`, ключ формата `handoff` и его имя в описаниях: `art-direction.schema.json:5, 233, 287`,
  `art-direction.v1.schema.json:5, 386, 1463, 1701`, примеры `art-direction-*.json` (по 1–3 строки).

Вне счётчика оставлено намеренно: «живая фаза» (слово легенды `kb/common/evidence.md`); «(ACCEPTANCE.md, группа E)» в
`x-canvas-map` файла уровней — группа критериев приёмки, не исполнитель; буквы направлений примеров («выбрал A»,
«из B») и узлов манипулятора в демо «Звено» (`J1`, `J2`, `L1`); id проверок утилит (`B3`, `J1`, `H12`, `G2–G5`).

## Ключи и значения, которые читает код

Не тронуты:

- `k3_allow` (`decisions[].k3_allow`, `exclusions.k3_allow`) — схемы art-direction v0 и v1, примеры,
  `recipe.schema.json`. Читают `scripts/creative/ad_check.py`, `scripts/project/canvas_input.py`,
  `scripts/creative/registry_check.py`. Имя ключа несёт след прежнего исполнителя; переименование — только вместе с
  кодом и форматом проектов.
- `recipe.schema.json`, `$defs.decision.technique.pattern` — `^(cliche|effect|k3):…`: префикс `k3:` в шаблоне
  значения. Рецепты его не используют (0 вхождений в 10 файлах); правка шаблона меняет проверку — владельцу схемы
  и `recipe_check.py`.
- `effect-gates.yaml`, `gates[].label` и `gates[].site` — `motion_check.py` печатает их в `gates.md`. Ключи и
  структура не тронуты, из текста значений сняты буквы и id опытов: отчёт ворот проекта выходит без них.
- `effectiveness.rubric.json`, ключ `doc` — по нему `scripts/ai-media/asset_audit.py` находит рубрику-близнеца.
- `cyrillic-display-fonts.yaml`, строка шапки «трекинг display не ниже tracking_touch + 0,005» — `ad_check.py`
  берёт из неё запас трекинга регулярным выражением: число нормы живёт в комментарии. Строка не тронута;
  перенос числа в ключ данных — владельцу `ad_check.py`.
- Блоки `x-canvas-map` (схемы v1, `ambition-levels.yaml`) — правок внутри блоков нет.
- Ключ `handoff` — формат art-direction (`ad_check.py`, `x-canvas-map`).

Ключи с буквой или именем точки согласования, которые код не читает, но это ключи формата или данных — оставлены,
решение за оркестратором: `d_refs` (art-direction v0 и v1, пример «Кварц»: «ссылки на разделы D» — ключ схемы v1,
он же в проектах форков); `a_examples_check` (`cyrillic-display-fonts.yaml`); `c1`
(`site-brief-creative-fields.yaml`); `x-effect-ids-v0`, `x-effect-ids-note` (`treatment.v0.schema.json`).

Сняты по правилу «ключ с именем прежнего исполнителя, который никто не читает» и как журналы:

| файл | снято |
|---|---|
| `01-creative-direction/art-direction.schema.json` (v0) | `properties.handoff.properties.kimi` (15 строк) |
| `drafts-for-site/treatment.v0.schema.json` | `x-kimi-projection` (8 строк) |
| `drafts-for-site/site-brief-creative-fields.yaml` | `kimi_crosswalk` (27 записей и шапка раздела 4; разделы 5, 6 → 4, 5), `c1.sync_point` |
| `09-ai-execution-evaluation/effect-gates.yaml` | `changes` (3 записи журнала версий), `neighbours.kimi` |
| `10-recipes/recipes/01-…`, `03-…` и `recipe.schema.json` | `inputs.kimi` и свойство схемы |
| `10-recipes/recipes/01-…`, `02-…`, `03-…` | `example.gates` — путь отчёта ворот в `99-raw` |
| `09-…/examples/otves-home.motion-spec.yaml` | `x-revision` |
| `10-recipes/examples/l2-zveno/motion-spec.yaml` | `storyboard.sheets` — путь `99-raw/experiments/J/02-l2-zveno/frames/sheet.jpg` (листа в папке примера нет); закрытый пункт `open_questions` о MS-05 |

Значения, которые изменены и которые видит код:

- `refs.brief`, `refs.facts`, `refs.page_plans` примеров `art-direction-okoshko.json`, `art-direction-okoshko.v1.json`,
  `art-direction-otves.json` вели в `site-research/…` и `text-research/99-raw/…` (файлов нет). Теперь —
  `site/10-playbooks-contracts/examples/saas-okoshko/{site-brief.yaml, plans/home.yaml}`,
  `site/10-playbooks-contracts/examples/lead-services-otves/{site-brief.yaml, plans/home.yaml}`,
  `text/10-templates-recipes/examples/facts/facts-demo-saas-okoshko.yaml`. `ad_check.py` читает `refs.facts`: факты
  примера разрешаются, ошибок 0. Осталось расхождение данных: примеры v0 называют секции прежними id (`funktsii`,
  `tarify`, `kak-rabotaem`, `zamer`), в планах примеров site их нет — правка примеров или их снятие у владельца.
- `decisions[].technique` «k3:stats (ряд цифр)» в двух примерах «Окошко» → «примета stats-row (ряд цифр)»:
  `cliche:stats-row` в реестре клише нет, поэтому значение — слово, как разрешает схема; `ad_check.py` — без изменений.

## Читает `99-raw`

- `10-recipes/examples/l2-zveno/js/three-scene.js` — бандл esbuild сцены v2; исходник —
  `99-raw/experiments/J/04-light-pass/src/scene.js` (v1 — `J/02-l2-zveno/src/scene.js`), в папке примера его нет.
  Комментарий `main.js` теперь называет сборку (`three-scene.js`), путь сырья снят. До снятия `99-raw` исходник
  сцены нужно перенести в пример, иначе бандл останется без исходника.
- Лист кадров раскадровки `99-raw/experiments/J/02-l2-zveno/frames/sheet.jpg` и листы светового прохода
  (`pairs-desk.jpg`, `compare-anchors.jpg`) — якоря подкритерия «ремесло медиа» рубрики называли их; ссылки сняты,
  якоря описаны словами.

## Производные

В списке зоны производных файлов нет. Блок `x-effect-levels` схемы подачи не тронут; `sync_check.py` — генераторы
совпадают.

## Для фикстур

`fixture_gen.py build --all --check` — совпадает, расхождений от правок нет. Свои файлы фикстур
`scripts/tests/fixtures/input-landing/…/home.motion-spec.yaml` и `package-landing-defects/…/home.motion-spec.yaml`
несут те же следы, что были в `otves-home.motion-spec.yaml` (`x-revision` «после опыта I/02», заметки с id опыта) —
правка у оркестратора.

## Для текстов

- `01-creative-direction/README.md:15–16` — описание `drafts-for-site/`: «таблица «поле kimi → поле брифа»» — блока
  больше нет; `01-concept-and-directions.md:408` ссылается на `kimi_crosswalk`;
  `02-art-direction-document.md:129, 138` — строки таблицы о `handoff.kimi.*` (в схеме v1 этого блока нет, из v0 снят).
- `09-ai-execution-evaluation/01-presentation-spec-and-block-treatments.md:143` — «`site_validate.py` грузит
  treatment по пути … `drafts-for-site/treatment.v0.schema.json`»: код этот файл не читает.
- `10-recipes/examples/README.md:74–75`, `10-recipes/03-product-launch-l2.md:110` — исходник сцены в `99-raw`
  (см. «Читает `99-raw`»).
- `03-live-sites-measured/README.md` описывает `sites.csv`, которого в папке нет; на него ссылаются
  `effectiveness.rubric.json` (`anchors.rule`, `sources`) — пути оставлены, в `gates_note` якорей стоит
  `creative 03/01`.
- `04-visual-language/cyrillic-display-fonts.yaml`: заметка Oswald «в примерах … заменить» — примеры уже несут
  Sofia Sans Condensed; заметка переписана как «замена — …».

## Соседям

- **Оркестратору — файлы вне списка зоны со следами** (счётчик их не видит): `10-recipes/recipes/04…10-*.recipe.yaml`,
  строка 1 — штамп « · J · 2026-09-25» (7 файлов); `04-d2c-campaign-l2.recipe.yaml:10` — «(решение заказчика
  п. 13)»; `06-portfolio-studio-l2.recipe.yaml:10` — «L2 по умолчанию A». Готовые замены: хвост штампа снять;
  «кампания — впечатление и есть сообщение; соцсети и инфлюенсеры»; «портфолио студии — L2 по умолчанию
  (ambition-levels.yaml); вау и есть продукт».
- **Зоне кода** — `scripts/creative/recipe_check.py`, докстринг: «creative-research · J · волна 3», запуск через
  `99-raw/tools/venv-J/…` и `99-raw/experiments/J/03-recipes-check/…`, `../site-research/04-blocks/blocks.yaml`,
  буквы H, K, F.
- **Д-creative-1** — `06-effects-catalog/effects.schema.json`, описания `id_map` и `mobile.behavior`, ссылаются на
  `treatment.v0` (`x-effect-ids-v0`, `mobile.strategy`): заметка `x-effect-ids-note` схемы v0 ведёт к `effects.yaml`, `id_map`.

## Файлы к снятию (решение оркестратора)

- `01-creative-direction/drafts-for-site/site-brief-creative-fields.yaml` — журнал согласования полей брифа с site
  (`c1.status: proposal`, списки keep / add / rename / tighten / reject, фрагменты схемы для site-brief v0.1). Код не
  читает; ссылается на `site-brief.example.yaml`, которого в site нет.
- `01-creative-direction/drafts-for-site/treatment.v0.schema.json` — версия v0; код читает
  `09-ai-execution-evaluation/treatment.schema.json`. На v0 ссылаются статьи 01/02, 01/03, 04/01, 04/02, 06/01,
  07/01, 09/01 и `effects.schema.json`.
- `01-creative-direction/art-direction.schema.json` — версия v0; `ad_check.py` проверяет все примеры, включая
  `01-creative-direction/examples/`, по схеме v1.

## Проверки

| проверка | итог |
|---|---|
| разбор 45 файлов (YAML, JSON, JSONL), 7 схем — метасхема Draft 2020-12 | ok 45, ошибок 0 |
| `kbscan.py --zone …` | целевые классы 0; подсказки 48 — разобраны выше |
| `smoke.py --only creative` | PASS 21 · FAIL 0 · XFAIL 0 · XPASS 1 |
| `smoke.py --only scripts/site` (читатели `ambition-levels.yaml`, `effect-gates.yaml`, схемы подачи) | PASS 28 · FAIL 0 |
| `smoke.py --only scripts/project` (`canvas_input.py`, `ready.py`, `ds_build.py`) | PASS 31 · FAIL 0 |
| `smoke.py --only page_accept`, `--only asset_audit` (читатели ворот и рубрики) | PASS 2 · FAIL 0 и PASS 3 · FAIL 0 |
| `ad_check.py` без аргументов — 6 примеров | ok 6; схема 0, паспорт 0, ссылки 0, правила 0; предупреждения те же, что до правки (8) |
| `ad_check.py --selftest`, `spec_check.py --selftest`, `motion_check.py --selftest` | OK (у `motion_check` — 63 проверки, FAIL 0) |
| `spec_check.py canvas-map` | error 0, warning 0; вывод как до правки |
| `spec_check.py levels --check`, `spec_check.py blocks` | error 0, warning 0 |
| `spec_check.py spec` и `plan` — три примера 09 и три спецификации рецептов | вывод до и после правок совпадает построчно |
| `recipe_check.py recipes/*.recipe.yaml` | рецептов 10: error 0, warning 0 |
| запись библиотеки-примера против `refs-library.schema.json` | 5 записей, ошибок 0 |
| `node --check` — `main.js`, `motion.js` | ok |
| `sync_check.py` | генераторы OK 17 · FAIL 0; копий расходится 0 |
| `fixture_gen.py build --all --check` | совпадает (4 набора) |
| `accept.py --base 1e0cd2a --masks-file …/Д-creative-2.masks` | под масками 45: разбор OK (33 файла данных, схем 7), ссылки OK, следы OK; «вне масок» — только файлы параллельных зон (394 на момент прогона) |
| копии `04-visual-language/marketing-tokens.css` и `10-recipes/examples/_shared/marketing-tokens.css` | совпадают |

Падений в чужих файлах при прогонах не было.

## Вопросы

1. Снимать ли версии v0 (`drafts-for-site/` целиком и `01-creative-direction/art-direction.schema.json`)? Следы в них
   убраны, но сами файлы — история согласования и предыдущая версия формата; код их не читает.
2. Исходник сцены `l2-zveno` и лист кадров раскадровки живут только в `99-raw`: перенести в папку примера до снятия
   `99-raw` или считать бандл и станции-картинки достаточными?
3. Рецепты 04–10 со штампом в первой строке — вне списка и масок зоны: добавить в зону или править оркестратору
   (замены — в разделе «Соседям»).
4. Ключи `d_refs`, `a_examples_check`, `c1`, `k3_allow` и префикс `k3:` в шаблоне схемы рецепта — оставить как имена
   формата или переименовать вместе с кодом и схемами?
5. Примеры art-direction v0 называют секции id прежних планов site (`funktsii`, `tarify`, `kak-rabotaem`, `zamer`):
   привести к id планов `site/10-playbooks-contracts/examples/…` или снять вместе с v0?
