# Опыт I/01 — схемы treatment v1 и motion-spec v1, block-treatments.yaml, проверки и проекции

Агент I · волна 3 · 2026-09-24 · Python 3.13 + `99-raw/tools/venv-I` (jsonschema 4.26.0, pyyaml) · без браузера.

## Цель
Сделать контракты подачи исполнимыми: схема проверяет форму, `spec_check.py` — то, чего схема не видит (id секций и слотов, уровни,
счёт пиков, акцентов и фирменных приёмов, эффекты и их пределы, токены, LCP, стаггер, петли), и строит проекции для пакета kimi.

## Файлы и команды
| Файл | Что | Команда |
|---|---|---|
| `compat_check.py` | treatment v1 против всех известных treatment v0 | `venv-I/bin/python compat_check.py` → 69 найдено, 69 валидны по v0, 0 регрессий (`compat_check.out.txt`) |
| `spec_check.py` | проверки и проекции (докстринг — справка) | `blocks`, `plan PLAN --overlay T --spec S --out M`, `spec S --plan P --overlay T`, `moments S`, `motion-md S --out F`, `values S --out DIR`, `levels`, `--selftest` |
| `vocab_lint.block-treatments.txt` | проверка id словарём site | `python3 ../../scripts/site/vocab_lint.py 09-…/block-treatments.yaml --keys-as-ids blocks=block` → 168 id, 0 ошибок |
| `otves-home.merged.yaml` | план «Отвеса» site + overlay treatment v1 (склейка) | `spec_check.py plan … --out` |
| `out/` | проекции примеров: строки T7, `MOTION.md`, JSON чисел по секциям | `moments`, `motion-md`, `values` |

## Результаты
- Схемы валидны (Draft 2020-12). Совместимость: 69 treatment v0 (27 в примерах site v1, 42 в опыте A/02) валидны по v1; две регрессии первой
  версии (обязательный `mobile.note`) убраны в предупреждение скрипта `[проверено]`.
- `spec_check.py blocks`: первая версия block-treatments дала 4 ошибки BT-09 (уровень варианта выше level_max блока) — исправлено; сейчас 0.
- `--selftest`: схема ловит L0 + pin, пик без signature, text-over без контраста, видео без flash_check, cinematic без ролика, LCP из opacity.
- Негативный прогон плана «Отвеса» (подброшены 5 нарушений) — 12 находок: схема (bogus reduce), конверсия не L0, signature в конверсии,
  level_max блока, старый id `kak-rabotaem.step`, счёт signature 3 > 2, peaks/accents/signature_sections ≠ секциям, два пика подряд.
- Примеры «Отвес», «Окошко», «Сталькон»: `plan` и `spec` — 0 ошибок (журнал прогонов — отчёт агента I).

## Ограничения
- План site валидируется схемой page-plan v1, где `$ref` на treatment `:0` подменён v1 (как будто site переключился) — у site сейчас грузится A v0.
  *S1b 2026-09-25:* site переключилась на v1 сама (2026-09-25 00:36, handoff site C2 — закрыто).
- *S1b 2026-09-25 (X-64):* MS-05 принимает `motion.kind` строкой или списком классов (`3d-scene` — `[scroll-linked, one-shot]`); пример L2 «Звено» —
  0 предупреждений; `--selftest` OK.
- Проверка длины текста для `display-poster` (≤ 12 знаков) не сделана: в примерах site copy-deck — заглушки.
- Проекция `moments` пишет строки на смеси английского (структура T7) и русского (описания из спецификации).
