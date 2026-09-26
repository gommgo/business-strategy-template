# Перенос базы в шаблон — `migrate.py`

`migrate.py` собирает скилл `design-deep-dive` и журнал сборки из замороженной базы, правил агентов A и B и overlay,
проверяет собранное и переносит его в шаблон `business-strategy-template`. Сборка детерминирована: те же входы дают побайтно
то же дерево и тот же отпечаток. Раскладка — `../SKILL-MAP.md`, решения — `../../DECISIONS.md`, правила содержимого —
`SPEC.md`, кода — `SPEC-code.md`.

## Запуск

```bash
cd /home/mm/Документы/app-design/_skill-build/phase-3/migration
free -g                                  # для смоука в check нужно ≥ 3 ГБ доступной памяти
python3 migrate.py build                 # ≈ 6 с: дерево → .staging/, печатает отпечаток
python3 migrate.py check                 # ≈ 1,5 мин (из них смоук ≈ 70 с): reports/check.txt
# в шаблоне: ветка feat/design-deep-dive от main, рабочее дерево чистое
git -C /home/mm/git/stit-core/business-strategy-template switch -c feat/design-deep-dive main
python3 migrate.py apply --repo /home/mm/git/stit-core/business-strategy-template --dry-run
python3 migrate.py apply --repo /home/mm/git/stit-core/business-strategy-template
# коммит — оркестратор (Conventional Commits, стиль forward-only); push — по слову заказчика
```

`python3 migrate.py fingerprint [DIR]` — отпечаток любого дерева (по умолчанию `.staging/`).

Нужно: системный `python3` с PyYAML и pathspec, `git`, `bwrap` (песочница смоука), окружение утилит
`~/.cache/design-deep-dive/venv` (смоук запускает утилиты его Python). Коды выхода: 0 — готово; 1 — ошибка сборки или
жёсткий провал check; 2 — отказ apply или check не завершён (смоук не запускался).

Между `build` и `apply` не правь `_skill-build/`: журнал — часть дерева, `apply` пересобирает план и откажет, если входы
изменились после проверки. Порядок перед переносом: переписать `STATE.md`, `PLAN.md`, `NEXT-SESSION-PROMPT.md` под работу
внутри шаблона → `build` → `check` → `apply` → коммит.

## Что делает каждый шаг

### build

Входы только читаются: замороженная база (sha256 каждого взятого файла сверяется с `../../freeze/manifest.tsv.gz`, расхождение
— ошибка), `manifest-rules.yaml` через `rules_eval.py` (A), `tools-map.tsv` и `patches/` через `apply_patches.py` (B),
`overlay/`, живой `_skill-build/`, `.claude/rules/forward-only.md` шаблона из ветки `main` (`git show`). `.staging/`
пересоздаётся целиком; это корень будущего шаблона:

| путь в дереве | откуда |
|---|---|
| `.claude/skills/design-deep-dive/kb/…` | правила A; эталонный код kb с правкой — строка tools-map (она главнее правила) |
| `.claude/skills/design-deep-dive/scripts/…` | tools-map: `take` — копия, `adapt` — результат правки; данные кода — правила A; overlay `scripts/` поверх |
| `.claude/skills/design-deep-dive/assets/calibration/` | утверждённый калибровочный набор, байт в байт |
| `.claude/skills/design-deep-dive/{SKILL.md,.gitignore}` | overlay |
| `.claude/skills/design-deep-dive/kb/INDEX.md` | генерируется: базы → заголовок и первая строка README → папки с числом файлов (заготовка карты знаний) |
| `research/design-build/…` | зеркало `_skill-build/` без §6 SPEC (большие TSV, полный манифест, кэши, `.staging*`, кадры калибровки, `_superseded/`), без overlay (Р110) и без `phase-3/migration/reports/`; `README.md` — из overlay |
| `research/design-build/phase-3/migration/path-map.tsv` | генерируется |
| `.claude/rules/forward-only.md` | файл из `main` + абзац `overlay/snippets/forward-only-exception.md` |

Переписывание путей — SPEC §7.1 кодом A (`file_links`, `resolve_old`, `dir_new_place`, `rewrite_token`, `new_resolve`):
токен меняется, только если разрешается в файл или каталог источника, у которого есть новое место (содержимое — по правилам A,
код — по `dest` tools-map, дубли — к канону, журнал — `research/design-build/`). Зона — md, txt и машинные файлы kb плюс
`scripts/<база>/README.md` (после правки B, от старого места `99-raw/tools/README.md`, Р112). Идентификаторы, короткие
адреса «NN/MM», код kb и журнал не трогаются; окончания строк и всё вне токенов остаются байт в байт. Два исключения:
- `assets/calibration/index.yaml` — копия байт в байт: утверждённый файл (Р109) объявляет `source.path` путями от корня
  app-design (провенанс в паре с sha256 заморозки), SPEC §5 и заметка правила `cal-index` — «файл не меняется»;
  `rubric` и `file` и так в раскладке шаблона — их проверяет check.
- производные файлы генераторов, чей `--check` входит в смоук (по данным B: `code_stage.KB_OUT` и `smoke-list.tsv`), —
  пути к коду не переписываются: генератор после правки B пишет их в старой форме, иначе `--check` видит расхождение.
  Такие токены check перечисляет как исключения.

`path-map.tsv`: `source` (от корня app-design; у сгенерированного `-`) → `dest` (от корня шаблона) → `sha256` источника →
`kind` → `replacements`. Виды: `copy` — байт в байт; `rewritten` — переписаны пути; `patched` — правка кода B (у README
утилит `replacements` = замены правки + переписанные пути); `alias` — дубль без файла, `dest` — место канона;
`generated` — `kb/INDEX.md`, `forward-only.md`, сам `path-map.tsv`. Строки есть для kb, кода, журнала и overlay; у каждого
файла дерева — ровно одна строка не-`alias`.

Отпечаток дерева — sha256 отсортированных строк «путь, бит исполнения, sha256 файла». Отчёты: `reports/build.json`
(отпечаток, состав по видам и частям, sha256 входов, переписывание), `reports/rewrites.tsv` (каждая замена токена).

### check

Пересобирает план в памяти и сверяет с деревом на диске, затем проверяет само дерево. Жёсткие проверки (провал — код 1):

| проверка | что |
|---|---|
| `freeze` | `tools/freeze.py --verify`: база не менялась с заморозки |
| `patches` | `apply_patches.py --check`: 0 ошибок |
| `fidelity`, `determinism` | дерево = план из текущих входов, тот же отпечаток |
| `composition` | содержимое = `expected-content.tsv` (A); код = `tools-map.tsv`, передача `scan-handoff.tsv` учтена целиком (B); overlay; журнал = живой `_skill-build/`; `path-map.tsv` ↔ дерево в обе стороны, sha256 источников |
| `forbidden` | нет `99-raw/cache`, kimi, запретного; мусор-класс только в asset-min (Р57) |
| `instructions` | нет `CLAUDE.md`, `AGENTS.md`, чужих `SKILL.md`, `.claude/`, `.mcp.json`, `.git` в kb, scripts, assets и журнале (Р97, Р110) |
| `secrets` | шаблоны `scan-secrets` по всем текстовым файлам дерева |
| `links` | каждая ссылка зоны на перенесённое разрешается в новой раскладке в свою цель (по файлам на диске); короткие адреса целы; ссылки `kb/INDEX.md` целы; каждая замена — ровно на месте токена |
| `identifiers` | неймспейсы, URN, URL `$id`, ключи, имена баз в прозе — те же числа по каждому файлу |
| `calibration` | `rubric` и `file` из `index.yaml` → файлы дерева; `index.yaml` байт в байт |
| `gitignore`, `symlinks` | ни один файл дерева не спрятан `.gitignore` шаблона (`main`) и скилла; симлинков нет |
| `home-paths` | `/home/mm` в `scripts/` и в эталонном коде kb с правкой — 0 |
| `forward-only` | файл = `main` + абзац, абзац один раз |
| `smoke`, `tree-after-smoke` | `scripts/tests/smoke.py` на дереве в песочнице B (`code_stage.smoke`: bwrap, база только для чтения, без сети, браузеров и Blender) — 0 FAIL; утилиты не меняют файлы дерева |

Предупреждения (код 0, цифры в отчёте): `links-baseline` и `rewrites-baseline` — сравнение с базовыми числами A
(`scan-links.tsv`, `scan-rewrites.tsv`; README утилит и файлы правил, добавленных после скана, — отдельно), `size` — объём
и токены по частям против Р111, `dest-names`, `smoke-outputs` — файлы, которые утилиты пишут внутрь скилла (из `.staging`
убираются; в отчёте — покрывает ли их `.gitignore`).

Читать: `reports/check.txt` — итог, строка на проверку, таблица размеров, XFAIL смоука; подробности — `reports/check.json`;
смоук построчно — `.staging-smoke/code-smoke-staging.raw.tsv` и `smoke-staging.log`. `check --no-smoke` — быстрый прогон
без смоука; такой check не зелёный (код 2), `apply` после него откажет.

### apply

Управляемые пути: `.claude/skills/design-deep-dive/`, `research/design-build/` и абзац-исключение в
`.claude/rules/forward-only.md`. Отметка переноса — `research/design-build/phase-3/migration/applied.json`: отпечаток,
sha256 и бит исполнения каждого записанного файла, sha256 абзаца и итогового `forward-only.md`. Git — только чтение
(`rev-parse`, `symbolic-ref`, `status`, `ls-files`, `check-ignore`).

Порядок: проверка ворот → запись добавленных и изменённых файлов → абзац, если его нет → отметка, если изменилась →
сверка (управляемые пути = `.staging/`, `git check-ignore` ничего не прячет). Ничего не удаляет. Повторный `apply` без
изменений ничего не пишет. `--dry-run` проходит все ворота и показывает план записи.

Незакоммиченное в рабочем дереве допускается только одно: ровно то, что записал прошлый `apply` (файлы совпадают с
отметкой). Так повторный запуск до коммита проверяет идемпотентность, а любая другая правка — отказ.

## Если apply отказал

Отказ печатает причину и перечень; в репозитории при отказе ничего не меняется (код 2). `reports/apply-last.json` — то же.

| причина | что делать |
|---|---|
| нет `reports/check.json`, check не зелёный | `build`, затем `check` до зелёного |
| дерево `.staging` изменилось после check | `check` заново |
| входы изменились после build и check | `build` и `check` заново (правили `_skill-build/`, правила, код или overlay) |
| не корень git-репозитория; ветка не `feat/design-deep-dive` | указать корень шаблона; `git switch feat/design-deep-dive` |
| рабочее дерево не чистое | закоммитить или убрать своё незакоммиченное вне управляемых путей |
| управляемые пути не пусты, а отметки нет | переноса туда не было или отметку удалили: разобраться вручную — вернуть отметку из git или убрать папки отдельным шагом |
| расхождение с отметкой: изменён / добавлен / удалён вручную | в шаблоне правили перенесённое: сохранить правку в истории шаблона и решить, что главнее. Перенос не затирает ручные правки. Если новая сборка совпадает с правкой, отказа нет |
| в управляемых путях файл, которого нет в `.staging` | новая сборка его больше не кладёт, а перенос не удаляет: убрать файл отдельным осознанным шагом (`git rm`) и повторить |
| абзац в `forward-only.md` правили руками | привести абзац к `overlay/snippets/forward-only-exception.md` или обновить сниппет и пересобрать |
| после записи: расхождения или файлы под `.gitignore` (код 1) | не коммитить; разобраться по `reports/apply-last.json` |
