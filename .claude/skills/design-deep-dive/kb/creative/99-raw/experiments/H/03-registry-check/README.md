# H/03 — проверка реестра клише и ссылок `cliche:<id>`

Агент H, волна 2 · 2026-09-24 · Python 3.13.5 + PyYAML (системный) · без сети и браузера.

**Цель.** Реестр `08-uniqueness-anti-slop/cliche-registry.yaml` — машиночитаемый вход для A (`decisions[].technique`), F
(`effects.yaml` — риск клише), I (`art-direction` v1) и K (сводная проверка с AIL site). Скрипт ловит то, что ломает эти связи.

**Команда.** `python3 registry_check.py [--refs <папка> …]` (по умолчанию ссылки ищутся в `01-creative-direction/` и
`08-uniqueness-anti-slop/`); exit 0 — ок, 1 — ошибки.

**Что проверяет.** Обязательные поля записи (22); словари `status`, `severity` (B/S/D, как AIL), `risk`, `family`; `k3_allow` —
только ключи `ALLOW_KEYS` `k3_checks.py` 1.0; коды `detect.method` — из `detect_codes`; `levels` L0–L2; даты `checked_at`,
`review_by`; id в kebab-case без дублей; кластеры объявлены и их члены существуют; `id_aliases` ведут на записи; каждая
ссылка `cliche:<id>` в файлах разрешается (id или прежний id из `id_aliases`).

**Результат 2026-09-24 (21:55).** 52 записи (saturated 39, dated 13; S 24, D 28; риск high 26, mid 21, low 5); кластеры сверены в
обе стороны (состав кластера = записи с его id в поле `cluster`); 13 ссылок `cliche:` в примерах A и файлах H — неразрешённых 0;
ошибок 0.

**Для K (волна 3).** Скрипт — основа проверки «решение по каждому клише есть» (`LNT`): список `cliche:<id>`, найденных
детекторами на сборке, минус решения `decisions[]` документа `art-direction` = приметы без решения.
