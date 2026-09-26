# N/04 — сухой прогон процедуры обновления маршрутов на снимках 24.09.2026

- **Цель.** Проверить на реальных изменениях каталогов, что процедура `13-routing-matrix/04-update-procedure.md` исполнима
  за минуты и без денег: снимок → разница → валидатор → классификация изменений → задание мини-стенда новой модели → цена.
- **Команды (без сети, кроме публичных GET каталогов; всё бесплатно).**
  1. `python3 ../../scripts/ai-media/polza_catalog.py snapshot` (снят оркестратором в 04:10) и
     `python3 ../../scripts/ai-media/mp_client.py snapshot --channel all` (снят N в 04:24: RouterAI 522 модели, Gen-API 318 сетей).
  2. `python3 ../../scripts/ai-media/polza_catalog.py diff 2026-09-23_1745 2026-09-24` → `polza_diff_1745_to_0924.md`;
     `… diff 2026-09-23 2026-09-24` → `polza_diff_0923_to_0924.md`.
  3. `python3 channel_diff.py` → `channel_diff_2026-09-24.md` (RouterAI и Gen-API: новые/удалённые, сдвиг цен, параметры).
  4. `python3 ../../scripts/ai-media/routing_check.py` → 0 ошибок (`../01-routing-check/report.md`).
  5. Новая модель polza → `99-raw/tools/venv-D/bin/python ../../scripts/ai-media/stand_run.py ministand --model
     grok-imagine-image-2-0/text-to-image --out <scratch>` → пути входов `../../` → `../../../` → `N-MS-grok-image-2-0.jsonl`;
     `python3 ../../scripts/ai-media/polza.py estimate N-MS-grok-image-2-0.jsonl` → **11 заданий, 0 ошибок, 33,00 ₽**.
- **Результат (что поменялось за сутки и что сделано).**

| Изменение | Класс | Действие |
|---|---|---|
| polza: +`google/gemini-omni-1.1-flash` (23.09 17:45) | новая модель, видео | в `routing.yaml` — премиум `VID-HERO-LOOP`, `VID-V2V`, `VID-UPSCALE`; тест I-15 уже есть; вопрос протокола — T9 |
| polza: +`grok-imagine-image-2-0/text-to-image` (23.09 17:45) | новая модель, картинки | `IMG-DRAFT`/`IMG-ILLUSTR` — `final: false`; мини-стенд 11 генераций 33 ₽ (S03 пропущен: нет 4:3) → расширенный уровень плана |
| polza: `gemini-3-pro-image-preview` +`output_format` | новый параметр | компилятор параметр не требует; маршруты не меняются |
| polza: цены долларовых провайдеров +0,2 % (Wan 3.0, HappyHorse, H3 Max, токенные Google/OpenAI) | цена (курс) | I-10: 47,3032 ₽ — валидатор и `polza.py estimate` уже считают по новому снимку |
| RouterAI: цены всех 51 медиа-моделей +0,39 % (одинаково — курс) | цена (курс) | в `routing.yaml` цены 24.09 (Recraft V4.1 vector 8,7773; utility 3,8401; styles vector 5,4858; GPT 2.5 medium 1,445) |
| RouterAI: +`recraft/recraft-v4.1-flash` (0,768 ₽, t2i ≈ 1K за ≈ 1,5 с) | новая модель, вне polza | `IMG-DRAFT` alt, `final: false`; мини-стенд вне polza — только на RouterAI (нет `ministand` для каналов) |
| RouterAI: +`inclusionai/ming-image-0.1-design-layer` (цена не указана) | новая модель, слои | `IMG-LAYERS` alt, `price_rub: null` — зонд после ключа |
| Gen-API: +5 чат-сетей; цены сетей без изменений | не медиа | действий нет |

- **Вывод.** Процедура занимает ≈ 10 минут и 0 ₽ до мини-стенда; мини-стенд новой модели картинок стоит 33–58 ₽ (Grok 2.0
  3 ₽ × 11; NB2 1K 4,8 ₽ × 12). Недостаёт двух вещей: `channel_diff.py` (добавлен здесь) и мини-стенда для моделей каналов
  (`stand_run.py ministand` знает только polza) — кандидат в задачу для B2/E.
- **Файлы.** `channel_diff.py`, `channel_diff_2026-09-24.md`, `polza_diff_*.md`, `N-MS-grok-image-2-0.jsonl` (заготовка
  задания; в `99-raw/phase5/jobs/` не перенесено — решение по плану).
