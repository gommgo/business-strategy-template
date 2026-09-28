# Вывод прогона cross-audit: чат, last-report и suppressions

Форматы вывода прогона: что показать аналитику в чате, чем перезаписать
`audit-state/last-report.md` и как записать подавление в
`audit-state/suppressions.md`. Примеры иллюстративные (проекты, slug и числа
условные); форма — обязательная.

## Отчёт в чат

Findings сгруппированы по `(проект, поверхность, угол)`, внутри группы — по
severity; верхнеуровневые — первой группой «Общие слои», углы одного
проекта по всем его поверхностям — группой «все поверхности». Каждый finding
несёт доказательство (конкретные файлы, slug, поля) и рекомендацию, какой
скилл запустить.

```
=== /cross-audit ===
Слои: business (+ стейкхолдеры), ajtbd, swot, hypothesis-map, project-map, infrastructure (общие) + проекты: referral-network (поверхности: web-partner, tg-bot), loyalty-app (поверхности: mobile)
Проектов: 2 · агентов: 15 верхнеуровневых + referral-network (7 пар + 15 и 18 троек по web-partner и tg-bot + 1 dataitems) + loyalty-app (6 пар + 13 троек по mobile) = 75
Пропущено: surface-screen, surface-design у web-partner (нет screens/web-partner/, design/web-partner/); surface-design у tg-bot и mobile (у бота и мобильного своего макета нет); facts-business, promise-product у обоих проектов (нет facts.yaml и слоя страницы); capability-domain, integration-domain, surface-service, service-capability, mobile-domain, mobile-service у loyalty-app (нет services/)
Время: <duration>

— Общие слои —

[error] addresses-problem-bizproblem → проект loyalty-app бьёт в проблему
  `legacy-sync`, которой нет в docs/business/business-problem.md.
  Доказательство: projects/loyalty-app/vision.md addresses-problem =
    [`paid-churn`, `legacy-sync`]; business/business-problem.md → строки [`paid-churn`,
    `slot-utilization`] — `legacy-sync` отсутствует.
  Что делать: завести проблему `legacy-sync` через
  /business-deep-dive business-problem, либо убрать ref в /project-deep-dive
  loyalty-app.

[error] projectmap-reciprocity → ребро `loyalty-to-store` ссылается на
  to-project `web-store`, которого нет в docs/projects/.
  Доказательство: project-map.md:loyalty-to-store to-project=`web-store`;
    каталога docs/projects/web-store/ нет (есть referral-network, loyalty-app).
  Что делать: исправить to-project на реальный проект или удалить ребро
  через /project-deep-dive loyalty-app integration.

[warning] segmentproblem-bizproblem → проблему бизнеса `paid-churn` не
  доказывает ни одно трение клиента из docs/ajtbd/segment-problem.md.
  Доказательство: business/business-problem.md:paid-churn; в segment-problem.md нет ни одной
    записи с feeds-problem=`paid-churn` или семантически бьющей в эту
    проблему.
  Что делать: разведать трение клиента под эту проблему через
  /job-graph-deep-dive, либо зафиксировать другой источник доказательства.

— Проект referral-network · все поверхности —

[error] integration-crossproject → integration:loyalty-sync (target:
  sibling-project, sibling-project=`loyalty-app`) не сведена в project-map.
  Доказательство: integration.md:loyalty-sync target=sibling-project,
    sibling-project=`loyalty-app`; в project-map.md нет ребра с
    via=`integration:loyalty-sync` от referral-network.
  Что делать: завести ребро в project-map.md (через /project-deep-dive),
  или поправить target, если это внешняя система.

— Проект referral-network · поверхность web-partner —

[error] surface-capability → поверхность web-partner объявлена stable, но
  capability/web-partner.md пуст.
  Доказательство: surface.md:web-partner status=stable;
    projects/referral-network/capability/web-partner.md — 0 записей.
  Что делать: завести возможности через /project-deep-dive referral-network
  capability:web-partner, или понизить поверхность.

[error] user-who → user:doctor не несётся ни одним who поверхности
  web-partner.
  Доказательство: user:doctor.context = «врач инициирующей клиники»;
    surface:web-partner.user ∋ `doctor`; в interface/web-partner/who.md нет
    роли, выполняющей действия врача.
  Что делать: завести who:doctor через /interface-deep-dive referral-network
  web-partner who, либо пересмотреть, обслуживает ли web-partner врача.

[warning] capability-domain → capability:send-referral (web-partner) не имеет
  домена в projects/referral-network/services/*/domains/.
  Доказательство: capability/web-partner.md:send-referral.value = «один
    клик»; в доменах сервисов есть только `auth`, `billing`, `inventory`.
  Что делать: добавить домен `referrals` через /domain-deep-dive, или
  пересмотреть capability.

— Проект referral-network · поверхность tg-bot —

[hint] capability-situation → ситуация confirm-via-bot в
  interface/tg-bot/situation.md не имеет capability-якоря в
  capability/tg-bot.md.
  Доказательство: situation:confirm-via-bot.action = «переподтвердить слот»;
    в capability/tg-bot.md нет возможности про переподтверждение.
  Что делать: завести capability на tg-bot или решить, что ситуация лишняя.

— Проект loyalty-app · поверхность mobile —

[hint] market-capability → конкурент klara-app покрывает push-кампании,
  у mobile нет такой возможности.
  Доказательство: market:klara-app.description = «push loyalty campaigns»;
    projects/loyalty-app/capability/mobile.md → нет записи про кампании.
  Что делать: рассмотреть через /project-deep-dive loyalty-app
  capability:mobile, или зафиксировать boundary.

Сводка: 5 error / 2 warning / 2 hint.
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
