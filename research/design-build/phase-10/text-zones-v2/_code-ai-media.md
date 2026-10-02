# Пункты зон кода для текстов базы `ai-media`

Готовые строки из разделов «Для текстов» отчётов зон кода: вносит та зона, в чьём списке стоит файл пункта.
Пункт о файле вне списка зоны — не твой.

**К5**
- `kb/ai-media/09-video-pipeline/01-seamless-loops.md` §1.1, таблица метрик: «`seam_ratio_local` — ≤ 1,5 у мезонина и
  выхода модели, ≤ 2,5 у файла после кодирования; меряется по файлу как есть»; «`dead_start`, `dead_end` — `trim --auto`
  срезает все мёртвые пары; больше 3 — `collapse_suspect`»; новые строки: `ends_motion`, `cuts` (`--montage`),
  `dup_frames` и `timing.held_frames`, `flash`; вердикт: `seam`, `no_cut`, `no_dup_frames`, `no_flash`, `alive_*`,
  `not_static`. Там же, выжимка п. 1 и «Открытые вопросы»: «после среза» → «по файлу как есть».

**К5**
- `kb/ai-media/README.md` (строка «Петля фона»), `kb/ai-media/13-routing-matrix/routing.yaml` (`post`, `tool` RIFE),
  `kb/ai-media/14-recipes/00-cheatsheet.md`: «RIFE-мост 8 кадров» → «мост `loop_rife_bridge.py`: длина — от шва и движения
  у концов».

**К5**
- `kb/ai-media/11-evaluation-qa/01-metrics-and-asset-audit.md`: режим `video-once`; коды `QA-VIDEO-DUP-FRAMES`,
  `QA-VIDEO-FLASH`, `QA-SOURCE-SOFT`, `QA-TEXT-SMALL`; уровни `QA-PROV-VISIBLE-MARK` и `QA-COLOR-WARM` без паспорта —
  info; `QA-LOOP-COLLAPSE` с `--fade-event` — warn; `--expect "строка{×N}"`; бюджет — `max_kb` слота плана (`--plan`).

**К5**
- `kb/ai-media/08-image-post-processing/04-encoding-metadata.md` §1.2 и `10-web-integration/01-images-delivery.md`:
  `avif_pick.sh` — 10 бит, 4:4:4, `-s 4`, бюджет `-b`, оценка по декоду 16 бит.

**К5**
- `kb/ai-media/08-image-post-processing/02-…` §1 — **норма предела увеличения**: числа нет ни в пункте, ни в базе; строку
  нормы пишет владелец после ответа на вопрос 2.

**К5**
- `kb/ai-media/11-evaluation-qa/thresholds.yaml`: шапка-комментарий (строки 1–5) и `ocr_models.source` с адресами `99-raw`
  оставлены отдельному шагу.

**К6а**
| `kb/ai-media/05-prompting/05-edit-reference-series.md` §1, таблица фраз, `remove` | «Remove the {target}{where}; in its place the frame shows {to}. Артикль цели — один: свой артикль снимается, своё местоимение или квантор (its, all …) остаётся» |

**К6а**
| там же, `extend` | «Extend the scene of {источник} to fill a {ratio} frame; keep the original image content unchanged and continue {caption} naturally at the new edges. Затем кадрирование: по предложению на `changes[]` — «The {target}{where} shows {to} ({value}).» — и фраза зоны текста `composition.text_zone` (Qwen — шаблон §2.4, кадрирование после описания исходника)» |

**К6а**
| там же, под таблицей | «Запрет текста в правке — «No added text.»: надписи исходника остаются, `edit.keep` с надписями запрету не противоречит. В генерации с нуля — «No text.»» |

**К6а**
| там же §2.4, абзац об `extend` | «…+ предложения кадрирования (`changes`, зона текста) + новый `aspect_ratio`; модель перерисовывает и исходную часть → `edit_check.py outpaint` и композит: исходные пиксели — на место, из ответа модели — новые области. Вариант маршрута с отсечкой маски и порогом проверки — `routing.yaml`, IMG-PRODUCT» |

**К6а**
| `kb/ai-media/05-prompting/03-asset-spec-and-dialects.md`, таблица полей диалекта, строка `models.{id}` | дописать: «`min_input_px` — меньшая сторона входной картинки, px: вход меньше — ошибка компилятора до вызова» |

**К6а**
| там же, раздел о `role` | «Слово контекста промта — `role.page_class`; `role.page_type` — id типа страницы словаря site, в промт не идёт» |

**К6а**
| `kb/ai-media/06-art-direction-consistency/01-visual-dna-from-ui.md`, таблица «паспорт → спецификация», строка `composition.text_zone_default` | дописать: «`side: center` — центральная полоса шириной `share`; объект при этом — не в центре» |

**К6а**
| там же §6 (утверждение паспорта) | «Новая версия утверждённого паспорта — `lifecycle.version` и запись `lifecycle.history[]`: версия, дата, кто подтвердил, что изменилось» |

**К6а**
| там же, пример команды `to-spec` | добавить ключи `--section hero --slot hero-visual`; рядом — «правка настоящего кадра: `to-spec … --edit кадр.png --operation relight` — без исключений паспорта и композиции генерации с нуля» |

**К6а**
| `kb/ai-media/05-prompting/04-video-prompting.md`, таблица кадров, строка `google/gemini-omni-1.1-flash` | «`first_frame_url` + `last_frame_url` — путь файла или URL: локальный файл в поле `polza.py` загружает в хранилище сам перед отправкой» (сейчас там «`polza.py` загружает только `images`…») |

**К6б**
- `kb/ai-media/02-providers-platforms/01-polza-api.md`: стр. 570 `polza.py balance --live` → `polza.py balance`; стр. 576
  `POLZA_OUT_ROOT` (`99-raw/experiments/_polza`) → (`$DDD_HOME/out/ai-media/_polza`); стр. 608 и 666 `balance --live` →
  `balance`; стр. 676 «`polza.py ledger --sum` против `/v2/balance.spentAmount`» → «`polza.py ledger --balance
  --baseline RUB`».

**К6б**
- `kb/ai-media/02-providers-platforms/07-multichannel-client.md`: стр. 195 — снимок `mp_client.py snapshot` ложится в
  `$DDD_HOME/cache/ai-media/{routerai,genapi}/<дата_ЧЧММ>/`; стр. 370 — «баланс и лимит ключа RouterAI и Gen-API:
  `mp_client.py balance --channel C --path <адрес из документации кабинета>`»; стр. 452 — «после серии: `polza.py
  ledger --balance` и `mp_client.py balance`».

**К6б**
- `kb/ai-media/13-routing-matrix/README.md` стр. 9, `kb/ai-media/README.md` стр. 8, `03-routing-matrix.md` стр. 7:
  «136 вариантов» → «137 вариантов»; README папки, стр. 10–11 — строки о `routing.v1.yaml` и `routing.v0.yaml`
  (файлов нет).

**К6б**
- `kb/ai-media/13-routing-matrix/04-update-procedure.md`: стр. 59 и 184 — в `catalog_snapshots` пишется имя папки
  снимка, не путь; стр. 156 — «для каждого маршрута с `phase5_test`» (поля в матрице нет).

**К6б**
- `kb/ai-media/13-routing-matrix/03-routing-matrix.md`: стр. 176 — к `unavailable_2026_09_25` добавить блок
  `unavailable` (`topaz/image-upscale`); строки маршрутов IMG-PRODUCT (вариант композита с отсечкой маски по глубине),
  IMG-UPSCALE (Topaz — не финал), VID-CAMERA и VID-HERO-LOOP (условие кадра со знаком марки и приёмка знаков по кадрам),
  VID-UPSCALE (`resolution_by`).

**К6б**
- `kb/ai-media/README.md` стр. 413 и `CONTRADICTIONS.md` стр. 403: «кроме управляемого поворота и ракурсов для FLF» —
  исключения у «не маршрута» 3D в `routing.yaml` нет (часть действия CN-92 текстовой зоны).

**К6б**
- `kb/ai-media/README.md` стр. 564: «`defaults.unavailable_<дата>`» → «`defaults.unavailable` и
  `defaults.unavailable_<дата>`».
