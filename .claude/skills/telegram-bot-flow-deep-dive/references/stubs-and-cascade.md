# Stub-сущности и удаление с каскадом

Читать, когда копаемая сущность ссылается на ещё не существующий slug
(своего слоя или interface) и когда аналитик удаляет сущность.

## Stub внутри telegram-bot-flow

Внутрифичевые рефы (окно в `dialog.windows`, use-case бота в
`widget.action` / `getter.*.source`) резолвятся **в пределах своей
фичи**; межфичевые и root (фича в `command.starts` или
`transition: start:<feature>`, команда в `notification.action`) — по
реестрам корня и фичам поверхности. Если копаемая сущность ссылается на
не существующий slug:

1. Завести stub:
   - окно — H2-секция `## <slug>` в `window.md` **той же фичи** со
     `status: draft`. У окна все мета-поля обязательны и `—` ни в одном
     не допускается, поэтому stub заводится сразу с минимально
     осмысленными значениями (`name`, `state`, `interface-block`,
     `ux-substrates`, `situations`, `who` — из контекста ссылки и
     блока-источника), а дыры — вопросами в state;
   - use-case бота — H2-секция `## <slug>` в `use-case.md` **той же
     фичи** с минимальным мета-блоком (`name` + `operation` +
     `status: draft`) и пустыми/`—` H3-секциями;
   - фича/диалог (новый `start:<feature>`) — папка `features/<feature>/`
     с `dialog.md` (минимальный frontmatter `slug + name + description +
     status=draft` + обязательные поля с `—`) и пустыми `window.md` /
     `use-case.md`;
   - command/notification — строка таблицы реестра корня с `—` в
     незаполненных колонках.
2. В state-заметке stub'а — секция `## Открытые вопросы` с записью
   «Заведён как stub в контексте `<откуда сослались>` — докопать».
3. Возврат в исходную сущность, копание продолжается.

## Ссылка на несуществующий interface-slug

Если `window.interface-block` / `ux-substrates` / `situations` / `who` /
`getter.*.data` (`data:<slug>`) указывает на не существующий
interface-slug **той же поверхности**, в
`docs/projects/<project-slug>/interface/<surface>/` скилл ничего не
заводит — у interface-слоя единая точка входа. Через `AskUserQuestion`
показать аналитику: «Ссылка на `<kind>:<slug>` в interface не валидна. Что
делаем?»

- «запустить `interface-deep-dive <project-slug> <surface> <kind>:<slug>`
  сейчас, я подожду» → скилл говорит «запусти `/interface-deep-dive
  <project-slug> <surface> <kind>:<slug>`», выходит из текущей сущности
  (state-заметка с `**blocker**`) и ждёт возвращения аналитика;
- «удалить эту ссылку» (если поле допускает) → правка слоя бота;
- «заменить на существующий slug» (показать варианты) → правка.

## Удаление сущности (каскад)

1. Прочитать все 5 kind поверхности (фичи
   `features/*/{dialog.md, window.md, use-case.md}` + реестры корня
   `command.md`, `notification.md`) и свою ветку state — найти все ссылки
   на удаляемый slug: `dialog.windows`, `started-by`, `widget.transition`
   (включая `start:<feature>`), `widget.action`, `getter.*.source`,
   `command.starts`, `notification.action`. Проверить и папку ассетов
   фичи `…/features/<feature>/assets/<slug>/`.
2. Показать каскад: «ссылаются X, Y, Z — вот что сломается». Удаление
   фичи/диалога тянет все её окна и use-case'ы (вся папка
   `features/<feature>/`) — показать их списком отдельно. Удаление
   use-case бота тянет `widget.action` / `getter.*.source`, которые на
   него ссылались.
3. Через `AskUserQuestion` по каждому месту — опции: «заменить на
   другой slug» / «поставить `—` (если поле допускает)» / «удалить
   ссылающуюся запись».
4. По подтверждению — выполнить все правки одним пакетом: удалить
   артефакт (папку `features/<feature>/` целиком — при удалении фичи;
   H2-секцию `## <slug>` в `window.md` / `use-case.md` — при удалении
   окна / use-case; строку таблицы реестра — при удалении
   command/notification), его папку ассетов и state-заметку, если
   существуют.
5. Пересчитать сводки `transitions` затронутых диалогов и зеркала
   `dialog.windows`.
