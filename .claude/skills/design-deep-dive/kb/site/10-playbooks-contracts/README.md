# 10-playbooks-contracts — процедура, плейбуки, итоговые контракты v1, полные примеры

Владелец — агент J (волна 3, 2026-09-24). Вход — все файлы волн 1–2; выход — то, по чему Claude собирает сайт от сообщения
заказчика до пакета исполнителя и приёмки.

## Файлы

| Файл | Что |
|---|---|
| `01-procedure-brief-to-pages.md` | 13 шагов `step:intake` … `step:measure`: артефакт, проверка SITE-PRE (K), дефекты DEF (K), утилиты, правило пропуска шагов, точки остановки, коды `site_validate.py` |
| `02-playbooks-landings.md` | 9 типов посадочных: когда, три формы, первый экран, длина, уровень и профиль бюджета, набор формы, факты, разметка, право, события, ошибки |
| `03-playbooks-multipage.md` | 7 типов многостраничников: карта по умолчанию, шапка, главная, шаблоны, формы, факты, уровни, SEO и проверки уровня сайта, право, события |
| `schemas/site-brief.schema.json` | бриф v1 (`urn:app-design:site:site-brief:1`) |
| `schemas/page-plan.schema.json` | план страницы v1 (`…:page-plan:1`), подача — `$ref` на `treatment:1` creative (v1 с 2026-09-25) |
| `schemas/site-map.schema.json` | карта сайта v1 (`…:site-map:1`) |
| `schemas/blocks.schema.json` | каталог блоков v1 (`…:blocks:1`) |
| `examples/lead-services-otves/` | лидогенерация услуг РФ «Отвес»: бриф, 6 планов, проекция `brief.kimi.home.yaml`, `acceptance-site.home.md`, `asset-plan.home.yaml`, заглушки сестёр |
| `examples/saas-okoshko/` | лендинг SaaS «Окошко»: бриф (draft), `facts.yaml` (копия демо text + пробел `demo`), 5 планов, проекция, план ассетов |
| `examples/corporate-b2b-stalkon/` | корпоративный многостраничник «Сталькон»: бриф, демо-факты J, карта v1, 15 планов шаблонов, проекция главной, план ассетов |

Утилиты (`../99-raw/tools/`, раздел J в `../../../scripts/site/README.md`): `site_validate.py` (схемы и перекрёстные ссылки, `--all`,
`--selftest`), `site_brief_to_kimi.py` (проекция в `brief.yaml` kimi + блоки приёмки I–L, `--check` — сборщик kimi),
`plan_to_assets.py` (каркас плана ассетов ai-media §8, `--check`). Опыты — `../99-raw/experiments/J/` (00–04). `vocab_lint.py` на файлах
примеров чужих форматов (`asset-plan.home.yaml`, `brief.kimi.home.yaml`, `facts.yaml`, `stubs-sisters.yaml`) — с `--no-default-map`
(без флага — 94 ложные ошибки: ключи `block`, `section` там не id словаря; X2, решение S2).

## Журнал контрактов v1 (2026-09-24)

- **Словарь** `02-site-types/vocabulary.yaml` v1 released (443 id, 17 пространств): + 5 `page_type` G, 5 `proposed`; блок `service-area`;
  слот `qr-code`; пространства `conversion_channel` и `procedure_step` (`step:`); 8 слотов proposed → active; `crosswalk.tsv` пересобран.
- **site-brief v1**: поля C1 creative (`ambition.source | by_section_role | motion_cap | allow | forbid`, `brand.expression`,
  `references[].applies_to | captured`, обязательные `take` и `dont_take`); `policies.capture_popup: engaged` (F); `conversion.response_time_promised`
  → `response_time_ref` (F); `constraints.legal_intake` (I 01 §6); `intake.baseline` (редизайн: V, W); `traffic.sources[].in_app_browser`;
  10 новых `page_type`.
- **page-plan v1**: `page.treatment` и `section.treatment` — `$ref` creative; `navigation` (архетип — `$ref` карты, крошки);
  `legal` (I: `cookie_mode`, `analytics_before_consent`, `cross_border`, `withdraw_link`, `erid_blocks`, `operator_ref`, `requirements`);
  `x-gate-exception` (P); `section.expires` (F); `load` у виджетов (P); `form.ref` по шаблону `lead-forms.yaml#<набор>`, `marketing_consent`;
  `event:<id>`; `template_id`; id секций — из роли или блока (SITE-PRE-15).
- **site-map v1**: `templates[].level` + `level_why` (уровень шаблона ≤ сайта); описание крошек → G `../06-multipage-ia/02-navigation-linking-i18n.md` §2.1.
- **blocks.yaml v1** и **lead-forms.yaml v1** — на месте (журналы в начале файлов): блок `service-area`, `qr-code`, `cta-next-label`,
  вариант `capture-popup.engaged-slide-in`, телефонные правила крошек и подвала, архетип шапки; журнал согласия, события `event:<id>`.
- Схемы сайта — только v1 (`schemas/`): файл другой версии `site_validate.py` не принимает (SB-S01, SM-S01, PL-S01).
- **2026-09-25 (S1, волна 4)**: `page-plan` v1 — подсхема `treatment` v1 creative (`treatment:1`; примеры — цели эффектов по id v1,
  hero «Окошка» без появления); `site-brief` v1 — `constraints.cms` `enum` (8 платформ, аудит X С-20); генератор
  `../99-raw/experiments/J/01-schemas-v1/make_schemas.py` обновлён теми же строками (пересборка даёт те же `site-brief` и `site-map`).

## Выжимка на 10 строк

1. Процедура — 13 шагов; шаги 1, 2, 5, 7, 10 не пропускаются; до сборки — `site_validate.py` с кодом 0 (SITE-PRE блокеры).
2. Бриф — один источник правды; в kimi — только проекция скриптом; открытые вопросы в пакет не идут.
3. Факты — до плана; нет допущенного факта — нет блока; обязательный вид закрыт фактом или блокирующим пробелом.
4. Тип — по дереву B; плейбук даёт форму, первый экран, длину, уровень, профиль, набор формы, разметку, право, события.
5. Карта многостраничника — закрытый список; шапка и подвал один раз; архетип по структуре; нет сирот; крошки с глубины 2.
6. План — цель, трафик, осведомлённость, три формы, политика первого экрана, роли, блоки, слоты; id секций из ролей.
7. Формы — `form.ref` на набор F; согласие ПД в ru — отдельная неотмеченная галочка; события — id `events.yaml`.
8. Уровень страницы ≤ сайта; профиль `<page_type>@L<n>`; превышение — `x-gate-exception`, а не молчание.
9. Сёстры получают id: copy-deck по слотам, treatment по секциям, план ассетов скриптом, 3D по рецепту.
10. Приёмка — свои проверки, не самоотчёт; правка ≤ 7 пунктов с полным повтором проверок; редизайн — по частям.
