# 01-product — Claude Design как продукт

Снимок: 25.09.2026 · источников: 35

| Файл | Что внутри |
|---|---|
| `01-claude-design-product.md` | Статус и доступ, модель и effort, холст и правка («ручки»), дизайн-системы, импорт, экспорт и handoff, лимиты, данные, официальные советы (дословно), ограничения, хронология 17.04 → 24.09 и «2.0/3.0», частые ошибки, 16 тестов, открытые вопросы, 35 источников |

Выжимка:
- С 16.09.2026 Claude Design — шаблон артефакта Design в любом чате, во вкладке Artifacts и в Claude Code (`/design`, с 17.06; Claude
  Code 2.1.265+, нужен `/login`); standalone claude.ai/design работает дальше. Статус — beta на Pro, Max, Team, Enterprise (Ent — выкл.
  по умолчанию); Free — шаблона нет (release notes 16.09 спорят с 4 источниками).
- Модель: запуск на Opus 4.7; сейчас **переключатель модели есть** (help center 21–23.09: Claude Design в списке продуктов с model
  picker и effort; Fable 5/5.1 — «in Claude Design», на Pro за usage credits), но дефолт и набор моделей не названы; «Opus 5.5 в Claude
  Design» официально не подтверждён → выбирать Opus 5.5 вручную (тест T-01).
- «2.0» из роликов ≈ официальное обновление 17.06 (новый редактор, переписанный импорт дизайн-систем, `/design-sync` и `/design`, общий
  лимит с чатом и Claude Code, коннекторы); «3.0» — ярлык блогера.
- Процесс по вендору: сначала дизайн-система (иначе «functional but generic output») → промт goal/layout/content/audience → варианты
  (2–3 или «ten options, then remix») → правка по размеру (chat / inline comments / прямая правка — «use no tokens») → экспорт (.zip,
  PDF, PPTX, HTML, 15 сервисов) или handoff «Send to local coding agent» / «Send to Claude Code Web».
- Ограничения: комментарии иногда пропадают (дублировать в чат), нет истории версий, совместная правка «still basic», нет модели
  картинок, большие репозитории — через Claude Code; что внутри handoff bundle, help center не описывает (разбор — `../02-claude-code-bridge/` §8).
- Данные: Pro/Max — обучение только при включённом «Help Improve our AI models» (выключить до загрузки материалов клиента); Team/Ent —
  без обучения по умолчанию; превью в sandboxed iframe с короткоживущими токенами.
