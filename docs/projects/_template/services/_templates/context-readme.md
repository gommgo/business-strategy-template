# <Context> — Bounded Context

> 2-3 предложения: какую часть бизнеса этот контекст представляет. Чем не занимается (граница).

## Purpose

- _что делаем_: <бизнес-обязательства контекста>
- _чего не делаем_: <границы — чем занимается другой контекст или платформа>

## Capabilities

> Опциональная секция: какие возможности продукта (`capability/<surface>.md`) несёт этот контекст — свободным текстом, surface — деталь. Для технического контекста (auth / audit / logging) — явное `_нет (технический контекст)_`.

- `capability:<slug>` (<surface>) — <какой частью контекст её реализует>

## Aggregates

| aggregate | role |
|---|---|
| [`<Name>`](<Name>.md) | <бизнес-роль> |

## Use cases

| operation | actor | brief |
|---|---|---|
| [`<Operation>`](use-cases/<Operation>.md) | <actor> | <что делает> |

Read use-case'ы (`Get<Name>`, `List<Name>s`) получают файл, только когда несут бизнес-правила; тривиальная выборка — строкой без ссылки (канон слоя, § Use-case'ы чтения).

## Events

### Published (исходящие)

| event | trigger | consumers |
|---|---|---|
| [`<Name>`](events/<Name>.md) | после `<UseCase>` | <consumer-context> |

<!-- Если событий нет: -->
<!-- | _нет на старте_ | — | — | -->

### Subscribed (входящие)

| event | source | reaction |
|---|---|---|
| [`<other-context>.<Name>`](../<other-context>/events/<Name>.md) | `<other-context>` | <что делаем в ответ> |

<!-- Если нет: -->
<!-- | _нет_ | — | — | -->

## Cross-context dependencies

> Если другой контекст живёт в **другом сервисе**, `nature` обязан называть
> способ: `service:`-порт (sync, через `Exposes` сервиса-владельца) или
> событие через брокер. In-process reader возможен только внутри одного
> сервиса.

| direction | other context | nature |
|---|---|---|
| outbound | `<other-context>` | порт `<OtherDomain>Reader` — чтение данных другого контекста |
| inbound | `iam` / `platform/authgate` | проверка валидной admin-сессии через HTTP-middleware |

## Ubiquitous Language

> Бизнес-термины этого контекста ↔ имена в коде. Также синонимы и **что НЕ называть как**.

| Бизнес-термин | В коде | Синонимы | Не путать с |
|---|---|---|---|
| <термин 1> | `<context>.<Type>` | <синонимы; «избегать» помечать явно> | <ложный друг> |
| <термин 2> | `<context>.<Type>` | — | — |

## Glossary notes

> Дополнения, неоднозначности именований. Все вопросы «почему так названо» — сюда.

- _нет_

## Architecture notes

> Архитектурные решения, специфичные для этого контекста. Что нестандартно? Что отличается от других доменов? Где живут cross-aggregate чтения? Семантика PUT/PATCH? Hard- или soft-delete? Авторизация — middleware или policy?

- _нет_
