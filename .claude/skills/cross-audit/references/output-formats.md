# Вывод прогона cross-audit: чат, last-report и suppressions

Форматы вывода прогона: что показать аналитику в чате, чем перезаписать
`audit-state/last-report.md` и как записать подавление в
`audit-state/suppressions.md`. Примеры иллюстративные (проекты, slug и числа
условные); форма — обязательная.

## Отчёт в чат

Отчёт читает человек, который углы не писал, поэтому в чат он идёт словами
(`.claude/rules/guiding.md` §4, §5):

- **Итог — первым.** Одна-две фразы: что в порядке, что держит работу, что
  можно отложить; затем два-три хода дальше, один рекомендован.
- **Находка — три части:** что нарушено → чем грозит → как исправить (кто
  и каким скиллом). Уровень — словом («ошибка», «предупреждение»,
  «подсказка»); имя угла и уровень латиницей — в скобках в конце. Записи
  обоих слоёв названы словами, их адреса — файл и slug — в скобках: это
  доказательство находки. «Чем грозит» берётся из карточки угла
  (`angles.md`), а не сочиняется.
- **Дефект проверки — не вопрос человеку.** Находку, в которой аудит сам
  видит дефект проверки, а не слоёв (агент прочитал не тот файл, сослался
  на запись, которой нет), он записывает с причиной в reasoning-trace
  отчёта прогона (шаблон — ниже) и называет одной строкой отчёта; вопросом
  выносится только то, где у человека есть выбор.
- **Группировка** — по `(проект, поверхность, угол)`, внутри группы — по
  уровню; верхнеуровневые — первой группой «Общие слои», углы одного
  проекта по всем его поверхностям — группой «все поверхности».
- **Что проверено и что пропущено** — в конце: слои, проекты и
  поверхности, число агентов, пропущенные углы с причиной.

Пример — иллюстрация формы на вымышленных данных:

```
Сверка слоёв (/cross-audit): общие слои и два проекта — «Сеть направлений»
(referral-network) и «Лояльность» (loyalty-app).

Итог. Бизнес, SWOT и Карта гипотез между собой сходятся. Работу держат
пять ошибок: «Лояльность» ссылается на проблему и на проект, которых нет;
у «Сети направлений» стык с «Лояльностью» не попал на карту проектов, а
кабинет партнёра закрыт без возможностей и без роли врача. Два
предупреждения и две подсказки можно отложить.

Дальше можно:
1) закрыть ошибки «Сети направлений» — рекомендую: кабинет партнёра
   объявлен закрытым, а строить его не из чего;
   /project-deep-dive referral-network, затем
   /interface-deep-dive referral-network web-partner, от вас — три решения;
2) начать с «Лояльности» — две ссылки в пустоту: проблема и проект; две
   короткие правки в /project-deep-dive loyalty-app;
3) разобрать предупреждения — трение под проблему оттока и домен
   направлений: это разведка, ошибок она не снимает.

— Общие слои —

Ошибка. Проект «Лояльность» называет своей проблему legacy-sync
  (projects/loyalty-app/vision.md, addresses-problem), а в реестре проблем
  бизнеса её нет: там paid-churn и slot-utilization.
  Чем грозит: продукт решает проблему, которой бизнес не называл.
  Как исправить: аналитик заводит проблему —
  /business-deep-dive business-problem — или убирает ссылку —
  /project-deep-dive loyalty-app (addresses-problem-bizproblem, error).

Ошибка. Стык «Лояльность → магазин» (project-map.md:loyalty-to-store)
  ведёт в проект web-store, которого нет: есть referral-network и
  loyalty-app.
  Чем грозит: карта проектов показывает стык с продуктом, которого нет.
  Как исправить: аналитик правит проект назначения или удаляет стык —
  /project-deep-dive loyalty-app integration
  (projectmap-reciprocity, error).

Предупреждение. Проблему бизнеса «Отток платящих»
  (business-problem.md:paid-churn) не доказывает ни одно трение клиента
  (ajtbd/segment-problem.md).
  Чем грозит: проблема бизнеса стоит без доказательства со стороны
  клиента.
  Как исправить: аналитик разведывает трение — /job-graph-deep-dive — или
  записывает другой источник доказательства
  (segmentproblem-bizproblem, warning).

— Проект «Сеть направлений» (referral-network) · все поверхности —

Ошибка. Интеграция с соседним проектом «Лояльность»
  (integration.md:loyalty-sync) не сведена на карту проектов: в
  project-map.md нет стыка, который на неё опирается.
  Чем грозит: стык между продуктами записан с одной стороны — на карте
  его не видно.
  Как исправить: аналитик заводит стык — /project-deep-dive
  referral-network — или правит адресата, если это внешняя система
  (integration-crossproject, error).

— Проект «Сеть направлений» · кабинет партнёра (web-partner) —

Ошибка. Поверхность закрыта (surface.md:web-partner, stable), а её файл
  возможностей пуст (capability/web-partner.md).
  Чем грозит: кабинет объявлен готовым, а что он умеет — не названо.
  Как исправить: аналитик заводит возможности —
  /project-deep-dive referral-network capability:web-partner — или
  понижает поверхность (surface-capability, error).

Ошибка. Пользователь «Врач» (user:doctor) назван у кабинета партнёра, а
  среди участников interface его нет (interface/web-partner/who.md).
  Чем грозит: для врача не будет ни ситуаций, ни экранов.
  Как исправить: аналитик заводит участника —
  /interface-deep-dive referral-network web-partner who — или решает, что
  кабинет врача не обслуживает (user-who, error).

Предупреждение. У возможности «Отправить направление»
  (capability/web-partner.md:send-referral) нет домена в сервисах проекта:
  там auth, billing и inventory.
  Чем грозит: возможность обещана, а бэкенду её нечем исполнить.
  Как исправить: архитектор добавляет домен направлений —
  /domain-deep-dive — или аналитик пересматривает возможность
  (capability-domain, warning).

— Проект «Сеть направлений» · бот (tg-bot) —

Подсказка. У ситуации «Переподтвердить слот»
  (interface/tg-bot/situation.md:confirm-via-bot) нет возможности в
  capability/tg-bot.md.
  Чем грозит: ситуация есть, а возможности, ради которой она нужна, нет.
  Как исправить: аналитик заводит возможность бота —
  /project-deep-dive referral-network capability:tg-bot — или решает, что
  ситуация лишняя (capability-situation, hint).

— Проект «Лояльность» (loyalty-app) · приложение (mobile) —

Подсказка. Аналог klara-app (market.md:klara-app) ведёт push-кампании, а у
  приложения такой возможности нет (capability/mobile.md).
  Чем грозит: на рынке это есть, у продукта — нет, и не записано почему.
  Как исправить: аналитик рассматривает возможность —
  /project-deep-dive loyalty-app capability:mobile — или записывает
  границу (market-capability, hint).

Что проверено. Слои: бизнес и стейкхолдеры, AJTBD, SWOT, Карта гипотез,
карта проектов, ИТ-периметр; проекты: referral-network (web-partner,
tg-bot), loyalty-app (mobile). Агентов 75: 15 по общим слоям;
referral-network — 7 пар, 15 и 18 троек по web-partner и tg-bot, один по
словарю данных (dataitems-crosssurface); loyalty-app — 6 пар и 13 троек
по mobile. Время: <duration>.
Что пропущено. У web-partner — экраны и макет (surface-screen,
surface-design): папок screens/web-partner/ и design/web-partner/ нет. У
tg-bot и mobile — макет (surface-design): у бота и мобильного своего
макета нет. У обоих проектов — факты и обещания страницы (facts-business,
promise-product): нет facts.yaml и слоя страницы. У loyalty-app — углы
сервисов и доменов (capability-domain, integration-domain,
surface-service, service-capability, mobile-domain, mobile-service): нет
services/.
Счёт: 5 ошибок, 2 предупреждения, 2 подсказки.
```

## `audit-state/last-report.md`

Перезаписывается целиком каждым прогоном: это рабочий срез последнего
прогона, не журнал.

```markdown
---
ran-on: <UTC-ts>
projects: [referral-network, loyalty-app]
surfaces:
  referral-network: [web-partner, tg-bot]
  loyalty-app: [mobile]
top-level-lenses-run: 15
pair-lens-runs: 13        # сумма по всем (проект × пара-lens)
triple-lens-runs: 46      # сумма по всем (проект × поверхность × тройка-lens)
dataitems-runs: 1         # один на мультиповерхностный проект
per-project-layers:
  referral-network: { project: yes, interface: yes, domain: yes, screen: no, botflow: yes, mobile: no,  site: no, design: no }
  loyalty-app:      { project: yes, interface: yes, domain: no,  screen: no, botflow: no,  mobile: yes, site: no, design: no }
findings: { error: X, warning: Y, hint: Z }
verdicts: { accepted: A, needs-fix: B, false-positive: C, deferred: D }
---

# Reasoning trace

## Общие слои

### Lens: addresses-problem-bizproblem
- agent-id: agent-1a
- duration: 12s
- findings: 2
- verdicts: [needs-fix, deferred]
- details:
  - finding-1 (error): project loyalty-app → проблема `legacy-sync` не
    в business-problem → verdict: needs-fix
  - finding-2 (hint): проблему `slot-utilization` не закрывает ни один
    проект → verdict: deferred

### Lens: projectmap-reciprocity
- agent-id: agent-1m
- findings: 1
- details:
  - finding-1 (error): ребро loyalty-to-store → to-project web-store не
    существует → verdict: needs-fix

## Проект: referral-network (пары)

### Lens: integration-crossproject
- agent-id: agent-5a
- findings: 1
- details:
  - finding-1 (error): integration:loyalty-sync без ребра в project-map →
    verdict: needs-fix

## Проект: referral-network · поверхность web-partner (тройки)

### Lens: user-who
- agent-id: agent-7c
- duration: 18s
- findings: 2
- verdicts: [needs-fix, accepted]
- details:
  - finding-1 (error): user:doctor без who поверхности web-partner →
    verdict: needs-fix
  - …

### Lens: capability-situation
- …

## Проект: referral-network · поверхность tg-bot (тройки)

### Lens: …
- …

## Проект: loyalty-app · поверхность mobile (тройки)

### Lens: …
- …

…
```

## `audit-state/suppressions.md`

Одна запись на подавленный паттерн; `reason` — слова аналитика из Other в
`AskUserQuestion`. Для верхнеуровневых углов `project: —`, для пар и
верхнеуровневых `surface: —`.

```markdown
- lens: user-who; project: referral-network; surface: web-partner;
  pattern: "user:doctor without who"; reason: <от аналитика, через Other в
  AskUserQuestion>; suppressed-since: <ts>
```
