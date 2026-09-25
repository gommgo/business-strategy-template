# use-case

> Use-case бота — **оркестратор** одного действия: собрать ввод, дёрнуть
> доменный use-case через backend, поработать со стейтом и вернуть исход.
> **Бизнес-правил не держит** (они в доменах сервисов). Все use-case'ы фичи лежат
> в `use-case.md` — **по H2-секции на use-case**, форма секции зеркалит
> доменный use-case (`services/_templates/use-case.md`) на уровне H3, без
> доменных-only секций (`Called aggregate methods`, `Events emitted`,
> `Side effects`).

## Критерии use-case

1. **Оркестрация, не правило.** Валидация формата ввода → вызов доменного
   use-case → разбор исхода → апдейт `dialog-data` → возврат исхода окну.
   Бизнес-решение принимает **домен**.
2. **Опирается на домен.** `### Dependencies` перечисляет доменные use-case
   (`use-case:<ctx>.<Operation>`); чистая навигация use-case'а не требует.
3. **Исходы объявлены.** `### Outputs` называет исходы, на которые
   ссылаются `when` переходов окон.
4. **Стейт — контракт.** Что читает/пишет в `dialog-data` — в
   `### Dependencies` (JSON-примитивы).
5. **Фичевый.** slug уникален в фиче; рефы `use-case:<uc-slug>` (без точки)
   внутри фичи.

### Форма секции use-case

```markdown
## <uc-slug>

​```yaml
name: <человекочитаемое имя>
operation: <PascalCase>
who: [<who-slug>]
status: draft | stable
​```

<одна-две фразы об оркестрации>

### Actor
- **Role:** <who> · **Trigger:** виджет `<id>` окна `<window-slug>` | вход диалога | system

### Inputs
| field | source | required | description |
|---|---|---|---|
| `<Field>` | `widget:<id>` \| `dialog-data:<key>` \| `start-data:<key>` | yes | <смысл> |

### Outputs
- **On success:** <исход> (на него смотрит `when` окна)
- **On failure:** см. Errors

### Dependencies
| dependency | kind | purpose |
|---|---|---|
| `use-case:<ctx>.<Operation>` | domain use-case | <что делает домен> |
| `dialog-data:<key>` | state (read \| write) | <что лежит, JSON-примитив> |

### Steps
1. **Validate input:** формат (бизнес-валидация — в домене).
2. **Call domain:** `use-case:<ctx>.<Operation>`.
3. **Map outcome:** исход домена → исход bot UC.
4. **Update state:** `dialog-data:<key>`.
5. **Return outcome:** исход окну.

### Errors
| outcome | when | реакция окна |
|---|---|---|
| `backend-unavailable` | backend недоступен | `errors.backend-unavailable` окна |
| `<domain-failure>` | домен вернул отказ | переход/сообщение по `when` |
```

### Что use-case НЕ

- ❌ Не носитель бизнес-правил: инвариант, бизнес-валидация, policy — в
  доменах сервисов (`services/*/domains/`). Bot UC их **вызывает**, не повторяет.
- ❌ Не доменный use-case: реф на доменный — с точкой
  (`use-case:<ctx>.<Operation>`), на bot UC — без точки.
- ❌ Не окно: UC обрабатывает действие и возвращает исход, показ — окно.
- ❌ Не код: класс сервиса, метод API-клиента, формат запроса, ретраи.

### Тест-критерий

«Оркестрация бота — собрать ввод, дёрнуть доменный use-case, разрулить
исход и стейт?» — «submit-booking: собрать draft, вызвать
`booking.CreateOrder`, вернуть «нужен адрес»/«готово»» ✅; «Проверить, что
гостей ≤ вместимости» — бизнес-правило домена ❌; «Окно подтверждения» —
window ❌.
