# Пункты зон кода для текстов базы `site`

Готовые строки из разделов «Для текстов» отчётов зон кода: вносит та зона, в чьём списке стоит файл пункта.
Пункт о файле вне списка зоны — не твой.

**К1а**
| `kb/site/10-playbooks-contracts/01-procedure-brief-to-pages.md` | проверки фактов плана (стр. 252–253) | «`use.page_types` содержит тип страницы (PL-F04); у факта общей шапки или подвала с ролью секции в `use.section_roles` тип страницы не сверяется»; «минимумы блоков (PL-F07); секция с пробелом `missing:` и `on_missing: omit-block` — info: она снимается до факта» |

**К1а**
| то же | таблица полей страницы (стр. 270–273) | `navigation.{header, archetype, breadcrumbs, local_nav, footer}` — «PL-N02: архетип = карте, крошки и `local_nav` = шаблону»; «PL-SEO01: типы разметки — типы страницы и подтипы `structured_data_subtypes` head-kit»; «`x-gate-exception` — id ворот страницы `SG-…` или ворот эффектов `EG-…`» |

**К1а**
| то же | §12, таблица кодов (стр. 434–452) | SB-F01, SB-M00: «файла по ссылке ещё нет: у брифа `draft` — info, со статуса `proposed` — error»; SB-D01: «система аналитики не `yandex-metrica` и не `none`»; SB-L03: «уведомление РКН — у сайта с формой (канал-форма брифа или action-слот с формой в планах) или с необязательными cookie»; SM-01: «цель призыва шапки — страница карты, `#якорь` или `messenger:<fact-id>` с фактом в `facts.yaml`»; новые строки: «PL-U01 · план `approved` без записи `approval` · warning», «BL-14 · информационная картинка каталога без парного элемента `image-alt` · warning»; к PL-A03 и PL-F01: «`target.prefill` — текстовый слот `messenger-prefill` своей секции; цель `messenger:<fact-id>` — факт есть» |

**К1а**
| `kb/site/06-multipage-ia/02-navigation-linking-i18n.md` | таблица шапки, строка «Главное действие» (стр. 90) | «`utilities.cta`: `action` и цель — страница, `#якорь` формы или `messenger:<fact-id>` (канал из фактов, когда своей формы у сайта нет)» |

**К1а**
| то же | локальная навигация | «`templates[].local_nav` карты повторяется в `page.navigation.local_nav` плана — из плана она идёт во вход холста» |

**К1а**
| `kb/site/04-blocks/03-slots-and-page-plan.md` | поля плана | «запись утверждения — `approval {by, date, note}` в корне плана; у плана `approved` она обязательна по смыслу (валидатор — warning PL-U01)» |

**К1а**
| `kb/site/07-seo-geo-performance-analytics/01-seo-google-yandex.md` | разметка по типам страниц | «подтипы, допустимые вместо типа страницы, — поле `structured_data_subtypes` в `head-kit.yaml` (`home-multipage`: `LocalBusiness` вместо `Organization` у сайта услуг)» |

**К1б**
| `kb/site/04-blocks/01-blocks-catalog.md` | таблица соглашений, «Цели касания» (стр. 106) | «≥ 24 × 24 CSS px или зазор — WCAG 2.2 AA (2.5.8); на таче каждая цель ≥ 44 × 44 зоной нажатия, видимый контрол может быть меньше (2.5.5 AAA)» |

**К1б**
| то же | таблица блоков, `stat-strip` (стр. 214) | «3–5 чисел-фактов с датой и источником; иначе ряд снять» |

**К1б**
| то же | таблица блоков, `feature-grid` (стр. 250) | к «3–6 равных выгод с механизмом» добавить «в роли `objections` — 1–3 карточки» |

**К1б**
| `kb/site/04-blocks/01-blocks-catalog.md`, `02-blocks-catalog-specialized.md` | карточки блоков | подписи ссылок секции `<id ссылки>-label` у 12 блоков; `messenger-prefill` у блоков с действием; необязательный alt у каждой информационной картинки (23 новых элемента: перечень — «Пункты», F9-014, и «Отступления», п. 9); группа `viewer` у `portfolio-grid` и `gallery` (`effect:overlay-viewer`); вариант `related-links.section-siblings` |

**К1б**
| `kb/site/04-blocks/03-slots-and-page-plan.md` | §, где «Вариант hero должен ей отвечать» (стр. 178) | «у варианта каталога `first_screen_policy` — значение или список допустимых политик» |

**К1б**
| то же | запись слотов в плане | «готовое сообщение мессенджера — текстовый слот `messenger-prefill` той же секции, на него ссылается `target.prefill`»; «подписи кнопок окна просмотра — слоты `viewer.close-label`, `viewer.prev-label`, `viewer.next-label`, экземпляр `viewer-1`» |

**К1б**
| `kb/site/04-blocks/README.md` | строка `blocks.yaml` (стр. 13) и команда проверки (стр. 24) | без счёта версий; проверка — `scripts/site/site_validate.py --all` и `scripts/site/vocab_lint.py kb/site/04-blocks/blocks.yaml --keys-as-ids blocks=block` от корня скилла |

**К1б**
| `kb/site/02-site-types/README.md` | строка `vocabulary.yaml` (стр. 11) | «словарь v1 (released): 445 id в 17 пространствах …» — без «журнал — `changelog`» |

**К1б**
| `kb/site/02-site-types/02-vocabulary-and-crosswalk.md` | §4.7 (стр. 203) | «`scroll-story` (сайт-референс W3, `landing.csv`)» |

**К1б**
| то же | описание пространств `slot` и `traffic_temperature` | «`messenger-prefill` — готовое сообщение мессенджера (текст, уровень секции)»; «у `traffic_temperature` — `def`: температура ≠ осведомлённость» |
