# 02-claude-code-bridge — мост Claude Code ↔ Claude Design

| Файл | Что внутри |
|---|---|
| `01-claude-code-and-claude-design.md` | Что на самом деле есть в Claude Code 2.1.281 для Claude Design: четыре режима `/design`, инструмент `ClaudeDesign` (MCP `/v1/design/mcp`), canvas-скилл, Artifact-тип «Design», `/design-sync` + `DesignSync`, `/design-login` и consent, handoff; ответы на вопросы 1–6, схемы связки А/Б/В, 10 тестов |

Выжимка:

- Серверного агента Claude Design «бриф → результат» из Claude Code вызвать нельзя: во всех путях дизайн делает модель Claude Code
  (Opus 5.5) в формате и хранилище Claude Design; агент приложения работает, только когда заказчик открывает проект в claude.ai.
  `[исходник]`
- `/design` в 2.1.281 — четыре режима за флагами сервера и политикой: types (Artifact «Design»), canvas (превью редактора), hub
  (`ClaudeDesign`: живой промт Claude Design, файлы проекта, `render_preview`), consent. **У заказчика на 25.09 — только consent.**
  `[проверено: флаги ~/.claude.json]`
- `/design-sync` — односторонний push собранной React-ДС в проект-дизайн-систему (бандл, `.d.ts`, `.prompt.md`, карточки
  `@dsCard`, конвенции в системный промт агента); первый синк — часы. `DesignSync` для макетов не годится. `[исходник]`
- Handoff Design → Code у нас — только «Download zip instead» (промт с «Claude Design connector» без коннектора не работает, #69246).
- Браузерная автоматизация claude.ai/design — нет (Consumer Terms п. 3.7).
- Сейчас основной путь — схема А (Claude Code + `frontend-design` + наши базы), Claude Design — руками заказчика для сравнения;
  при включении types/hub — схема Б.
