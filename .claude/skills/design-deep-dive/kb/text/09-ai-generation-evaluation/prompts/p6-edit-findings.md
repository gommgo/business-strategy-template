# P6 · Правка по находкам проверок: кластеры, проходы, стоп

Волна 3 · агент I2 · 2026-09-24 · промт `p6-edit-findings@1` (RU и EN) · `[не проверено]` · живой тест — LT-03 (C1, C5) в
`../live-test-plan.md` · опыт `99-raw/experiments/I/04-chain-manual/` (шаг S9, три прохода)

Шаг S9 цепочки `../02-generation-pipeline.md`: находки `copydeck.py check --json` (сверка B2 и право H → линтер C →
формат, длины, голос, мета J) → правки слотов → снова `check`. Протокол — C `../../06-anti-slop/02-linter-spec-and-profiles.md`
§9: проход 1 — все error; проходы 2–3 — warning кластерами (≤ 5 на 300 слов прозы, одна правка на короткий слот);
после 3 проходов — человеку. Промт не принимает «перепиши живее»: правка без находки — не шаг цепочки.

## Выжимка для агента

1. **Правь по находкам, не перегенерацией:** новая генерация приносит новые выдумки, правка — только то, что найдено.
   `[мнение: C, B2]` → LT-03 все → §2
2. **Проход 1 — все error; проходы 2–3 — warning кластерами, ≤ 5 кластеров на 300 слов прозы, одна правка на короткий
   слот.** `[мнение: C/01, C/04]` все → §2
3. **Каждая правка: удалить → заменить фактом → сказать проще;** синоним из того же ряда — не правка. `[практика: C §9]` все → §2
4. **Нет факта для числа — `[PLACEHOLDER]` и вопрос заказчику;** выдумать число, чтобы снять находку, — худший исход.
   `[проверено: B2/02]` все → §2
5. **Ложная находка — `lint_allow` с причиной, а не правка текста;** ART и CNT не подавляются. `[стандарт базы: C §9 п. 8]` → §2
6. **После каждого прохода — `copydeck.py check` целиком;** стало хуже — откат. `[практика: C §9 п. 6]` все → §4
7. **Правка — новый вариант слота, старый — `rejected` с причиной, запись `edit_log`** (схема J). `[стандарт базы: J]` → §4
8. **Четвёртого прохода нет:** остаток — человеку; иначе сверхкоррекция. `[проверено: C/04]` все → §4

## 1. Входы и выход

| Переменная | Откуда | Проекция (скрипт `chain_inputs.py edit-input`) |
|---|---|---|
| `{{PASS}}` | номер прохода | 1, 2 или 3 |
| `{{SLOTS}}` | copy deck | путь `<page>/<section>/<slot>`, `slot_type`, выбранный текст, `fact_ids`, `missing_ids`, длина по карточке E |
| `{{FINDINGS}}` | `copydeck.py check --json` | `tool`, `level`, `rule`, `where`, `message`, `fix`, `fragment`; проход 1 — только error |
| `{{FACTS}}`, `{{NEVER_CLAIM}}` | `facts.yaml` | факты слотов с находками |
| `{{VOICE_BRIEF}}` | `voice.yaml` | `prompt_brief`, `vocabulary.avoid` |
| `{{KEEP}}` | правило C §9 п. 5 | цитаты отзывов, дословные факты, условия, цена, кнопка, названия |

Выход — YAML правок; код переносит их в copy deck (§4).

## 2. Промт RU

```text
// модель: правщик из кандидатов 09/01 §2.2 (правка без потери стиля — сигнал MERA SAGE), t = 0,3 · 2026-09-24 · [не проверено]
// id: p6-edit-findings/ru@1 · вход: находки copydeck.py check · выход: YAML правок · после — снова copydeck.py check
Ты — редактор. Исправь только то, на что указывают находки проверки. Не переписывай текст целиком и не улучшай то,
о чём находок нет.

ВХОД
<pass>проход {{PASS}} из 3</pass>
<slots>{{SLOTS}}</slots>
<findings>{{FINDINGS}}</findings>
<facts>{{FACTS}}</facts>
<never>{{NEVER_CLAIM}}</never>
<voice>{{VOICE_BRIEF}}</voice>
<keep>{{KEEP}}</keep>

ПРАВИЛА
1. Проход 1 — исправь все error. Число, имя, условие без факта: поставь fact_ids на запись из <facts> и её
   формулировку, либо [PLACEHOLDER: что нужно] и id в missing_ids. Не придумывай факт, чтобы снять находку.
2. Проходы 2–3 — warning кластерами: сгруппируй находки по слоту и предложению, начни с семьи правил, где их больше.
   Не больше 5 кластеров на 300 слов прозы; у короткого слота (заголовок, кнопка, строка у кнопки, мета) — одна правка.
3. Каждая правка — по порядку: удалить → заменить фактом из <facts> → сказать проще. Синоним из того же ряда,
   «как X, так и Y» вместо «не только… но и», двоеточие вместо каждого тире — не правка.
4. Info правь, только если оно стоит в одном предложении с warning.
5. Сохрани функцию слота (призыв, оффер, срок, цена, условие), голос <voice>, всё из <keep> и длину по карточке слота.
6. Находка неверна (законный термин отрасли, слоган из брифа, обязательное по грамматике тире) — текст не меняй,
   добавь запись в lint_allow с причиной. Находки артефактов (ART) и данных (CNT) не подавляются.
7. Не делай текст рваным: связки и нормальные предложения остаются; короткие фразы — точечно.
8. Что нельзя исправить без заказчика (нет факта, спорное право), — в left_for_human с причиной.

ВЫХОД — один YAML-документ без пояснений:
edits:
  - path: "<page>/<section>/<slot>"
    from_variant: a
    to_variant: b
    text: "…"
    fact_ids: ["…"]
    missing_ids: ["…"]
    fixes:
      - {rule: "…", cluster: 1, action: delete|fact|simplify|placeholder, note: "что сделано"}
lint_allow:
  - {path: "…", rule: "…", reason: "…"}
left_for_human:
  - {path: "…", rule: "…", why: "…"}
clusters_used: 0
```

## 3. Промт EN

```text
// model: an editor from the 09/01 §2.2 candidates (style-preserving edits — MERA SAGE as a weak signal), t = 0.3 · 2026-09-24 · [не проверено]
// id: p6-edit-findings/en@1 · input: copydeck.py check findings · output: YAML edits · then copydeck.py check again
You are an editor. Fix only what the check findings point at. Do not rewrite the text as a whole and do not improve
anything that has no finding.

INPUT
<pass>pass {{PASS}} of 3</pass>
<slots>{{SLOTS}}</slots>
<findings>{{FINDINGS}}</findings>
<facts>{{FACTS}}</facts>
<never>{{NEVER_CLAIM}}</never>
<voice>{{VOICE_BRIEF}}</voice>
<keep>{{KEEP}}</keep>

RULES
1. Pass 1 — fix every error. A number, name or condition without a fact: point fact_ids to a record in <facts> and
   use its wording, or write [PLACEHOLDER: what is needed] and put the id in missing_ids. Never invent a fact to
   clear a finding.
2. Passes 2–3 — warnings in clusters: group findings by slot and sentence, start with the rule family that has most
   findings. At most 5 clusters per 300 words of prose; one edit per short slot (title, button, button note, meta).
3. Every edit, in this order: delete → replace with a fact from <facts> → say it more simply. A synonym from the same
   family or a colon in place of every dash is not an edit.
4. Touch info findings only when they share a sentence with a warning.
5. Keep the slot's job (call to action, offer, deadline, price, condition), the <voice>, everything in <keep>, and
   the slot card length.
6. A wrong finding (a legitimate industry term, a slogan from the brief, a required punctuation mark) — leave the text,
   add a lint_allow entry with the reason. Artefact (ART) and data (CNT) findings are never suppressed.
7. Do not make the text choppy: keep connectives and normal sentences.
8. Whatever cannot be fixed without the client (a missing fact, a legal question) goes to left_for_human with the reason.

OUTPUT — one YAML document, same keys as the RU version.
```

## 4. Выход и проверки после вызова

1. **Код переносит правки:** новый вариант `to_variant` (`status: draft`, `source: model` или `ai-self`, `generated`
   с `prompt_ref` P6), старый — `status: rejected`, `reason: "правка по находкам: <правила>"`, `chosen` — на новый;
   запись `edit_log: {pass, rules, clusters, by, date, from_variant, to_variant}`; `lint_allow` — в слот.
2. `copydeck.py check` после прохода: error = 0 после прохода 1; плотность маркеров ниже прежней; нет новых семей;
   вердикт не `overcorrected`; `fact_ids` на месте. Хуже — откатить правку (вернуть `chosen`).
3. **Стоп:** `clean` или `review` без warning в `headline`, `subheadline`, `cta-label`, мета — иначе после третьего
   прохода остаток (`left_for_human` + находки) уходит человеку и в `notes` слота.

## Частые ошибки

1. **«Перепиши без слопа»** вместо находок — правка всего текста, новые выдумки, потеря фактов.
2. **Число вместо заглушки:** находка «число без факта» закрыта другим числом, тоже без факта.
3. **Правка цитаты отзыва** под голос бренда или под линтер.
4. **Рваный текст:** все связки удалены ради плотности — вердикт `overcorrected`.
5. **Четвёртый проход** «до чистого отчёта»: warning о длине слота правят, сокращая условие гарантии.

## Чек-лист

1. Правка идёт по списку находок, а не по впечатлению?
2. Проход 1 снял все error без новых чисел?
3. Кластеров в проходе ≤ 5 на 300 слов, короткий слот — одна правка?
4. Ложные находки оформлены `lint_allow` с причиной?
5. Старый вариант `rejected` с причиной, `edit_log` записан?
6. После прохода — `copydeck.py check`, стало не хуже?

## Открытые вопросы и противоречия

1. Числа протокола (5 кластеров, 3 прохода) — `[мнение]` C по опытам C/01 и C/04; на генерации — LT-03 (C1).
2. Кластер на коротком слоте и кластер на абзаце весят по-разному. В I/04 правка короткого слота (OG) с двумя фактами
   в одной фразе породила новую error — понадобилась вторая итерация прохода 1; «одна правка на короткий слот» —
   правило проходов 2–3, проверено на одном deck.
3. Находки валидатора J (длина слота, ядро первого экрана) — сигнал, а не ворота (E): правщик вправе оставить их с
   причиной в `notes`, если сокращение режет факт или условие.

## Источники

- C `../../06-anti-slop/02-linter-spec-and-profiles.md` §7 (порядок проверок), §9 (протокол правки), §12; опыты C/01, C/04.
- B2 `../../02-strategy-messaging/03-proof-and-facts.md` §7 (правка по находкам сверки, не перегенерацией).
- J `../../10-templates-recipes/copy-deck.schema.json` (`edit_log`, `lint_allow`, `variant.reason`); `../../scripts/text/README.md`
  (раздел `copydeck.py`: `--json`, правила `COPY-D-…`).
- Опыт I/04 — `99-raw/experiments/I/04-chain-manual/README.md` (шаг S9: проходы, числа находок).
