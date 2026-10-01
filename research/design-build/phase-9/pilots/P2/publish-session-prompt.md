Пилот P2 — короткая сессия публикации холста и ДС в claude.ai. Основная сессия пилота работает параллельно в этом же
worktree и не может писать в артефакты типов: инструмент Artifact фиксирует флаги при старте сессии, а она стартовала,
когда флаг типов был выключен (находка F9-100). Эта сессия — новая, флаг включён. Задача узкая: опубликовать готовые
исходники из репозитория в два артефакта, больше ничего. Ветка — `pilot/greats`, папка — `/home/mm/git/stit-core/pilot-greats`.
Не коммить, не пушь, файлы скилла не правь. Отвечай по-русски, коротко.

1. Первой строкой — ветка и модель. Затем `Artifact` `list` со `scope: "types"`: в каталоге должны быть Design и Design
   System, а в схеме инструмента — `type_url`. Если нет — стоп: напиши, что каталог недоступен, и ничего не делай.
2. Прочитай протокол `.claude/skills/design-deep-dive/references/claude-design.md` § 3 «Создание и публикация» и § 4
   «Синхронизация». Правила формата — из ответа инструмента (справка типа в каждом артефакте: `SKILL.md`,
   `artifact-type/reference/format.md`).
3. **Холст `web`** — https://claude.ai/artifact/2wNYSLMKMN5mcHBXSJWVhW (тип Design; заказчик создал его вручную, он пуст).
   Прочитай: `read` по адресу и `list` со `scope: "files"`. Если в `project/` есть файлы — это правки заказчика: не
   перезаписывай, стоп и доклад. Если пусто — прочитай целиком каждый файл исходников
   `docs/projects/detailing-greats/design/web/canvas/project/` (`canvas.json` и 16 артбордов `*.dc.html`; их формат уже
   сверен со справкой этого типа) и опубликуй одним вызовом: `url` холста,
   `root: "docs/projects/detailing-greats/design/web/canvas"`, `file_path` — полный путь к `project/canvas.json`,
   `files` — все 16 артбордов `{"project/<имя>.dc.html": "project/<имя>.dc.html"}`. Без `type_url`, `capabilities`,
   `contract`, `favicon`, `icon`.
4. **ДС** — https://claude.ai/artifact/2EXQWzzFHke7xhJo4LGj39 (тип Design System; создан вручную, файлов `project/` нет,
   16 ассетов уже загружены, их id стоят в исходниках и в таблице «Загрузки» `docs/projects/detailing-greats/design/ARTIFACTS.md`).
   Справку типа возьми из `read` этого артефакта (`SKILL.md`, `artifact-type/reference/format.md`). Прочитай целиком
   исходники `docs/projects/detailing-greats/design/_design-system/project/` и опубликуй по справке:
   `root: "docs/projects/detailing-greats/design/_design-system"`, порядок и что последним (индекс `design-system.json`) —
   как велит справка; поле `lastChange` индекса — обнови по справке перед публикацией.
5. Отказ публикации — полное чтение и одна новая попытка; второй отказ того же рода — не повторяй. Если в созданные
   вручную артефакты не пишется вовсе, создай новые штатно: `quickstart` (холст — `intent: "design"`,
   `design_systems: false`; ДС — `intent: "other"`), затем `publish` с `type_url` и `title` без файлов («Detailing Greats —
   сайт» и «Detailing Greats»), и публикуй в них. У новой ДС ассеты загрузи заново (`asset: true`, файлы — по таблице
   «Загрузки») и замени id в `design-system.json` (`assetGroups`) и в превью `components/*/preview.html` (`/_blob/<id>`)
   по карте «старый → новый» — только id (находка F9-099).
6. `ARTIFACTS.md` (`docs/projects/detailing-greats/design/ARTIFACTS.md`): в строках таблицы «Артефакты» — адрес, «релиз
   типа · контракт» из ответа инструмента, версия после публикации, «последнее чтение» — сегодняшняя дата; абзац над
   таблицей — коротко, как созданы артефакты и что опубликовано (без журнала событий). Новые id загрузок — в «Загрузки».
7. Рендер не проверяй, браузер не открывай (артефакт без просьбы заказчика не проверяем). В конце — `list` со
   `scope: "files"` у обоих: все файлы `project/` на месте.
8. Отчёт: адреса, версии после публикации, число файлов `project/` у каждого, отказы — дословно. Напомни заказчику
   переключить оба артефакта в Share на публичную ссылку (его решение — строка «Ссылки» в `ARTIFACTS.md`).
