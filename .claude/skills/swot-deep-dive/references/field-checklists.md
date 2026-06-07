# Чек-листы полей по kind

Что заполнять при заведении/углублении каждого kind, что обязательно для
stable, и разумный порядок копания. Универсально обязательное: `slug`,
`name`, `description`, `status`. Для обоих kind обязателен **непустой
`business-problem`** — массив slug-рефов на строки реестра проблем
`docs/business/business-problem.md` (M:N): к какой проблеме(ам) относится
запись.

## factor

**Для stable:** `business-problem` (≥1 строка реестра проблем), `area` (enum
`strength`/`weakness`/`trend`/`threat`), `priority`, формулировка по
шаблону квадранта.
**Порядок:** fundamentals → business-problem → area → формулировка → priority.
Главная проверка: правильный квадрант (про устройство бизнеса vs про мир;
действие = это `bet`, не factor). `priority` считается внутри пары
квадрант × проблема. Один фактор бизнеса часто питает несколько проблем.
**Доказательство из AJTBD:** сильное трение клиента
(`ajtbd/segment-problem.strength` высок при низкой удовлетворённости
решением) питает фактор (обычно `weakness`/`threat`). Заглянуть в
`docs/ajtbd/segment-problem.md` (read-only) как evidence; перенос — через
`AskUserQuestion`, трения не выдумывать.

## bet

**Для stable:** `business-problem` (≥1 строка реестра проблем), `factors` (≥1
внутренний `strength`/`weakness` + ≥1 внешний `trend`/`threat`),
`promoted-to` (`goal:`/`hypothesis:` в `docs/hypothesis-map/`), формат
«⟨действие⟩, чтобы ⟨ценность⟩», `priority`.
**Порядок:** fundamentals → business-problem → factors → форма «действие, чтобы
ценность» → promoted-to → priority.
Главная проверка: баланс факторов + доведённость до карты гипотез. Одна
ставка может закрывать несколько проблем; её факторы тоже бывают общими.

## Универсальные нюансы

- `slug` — kebab-case, английский, короткий, уникальный в файле, не
  меняется после заведения; **скилл выводит его из `name`** (транслит в
  kebab-case), у аналитика не спрашивается (см. `.claude/rules/naming.md`).
- `name` — человекочитаемое, русский по умолчанию.
- `description` — одно предложение, в языке бизнеса, без маркетинга.
- `priority` — целое, 1 = высший, без дублей.
- `business-problem` — массив slug-рефов на строки реестра проблем, питон-стиль с
  бэктиками (`` [`paid-outflow`, `slow-onboarding`] ``). Непустой у обоих
  kind. M:N — одна сущность бизнеса часто работает на несколько проблем.
- `factors` (у `bet`) — питон-стиль массив slug-рефов на `factor`.
- `promoted-to` (у `bet`) — одиночный slug-реф `goal:<slug>` или
  `hypothesis:<slug>` на сущность слоя `docs/hypothesis-map/`.
- `status` — дефолт `draft`; повышение только через чек-лист; понижение
  руками аналитика.
