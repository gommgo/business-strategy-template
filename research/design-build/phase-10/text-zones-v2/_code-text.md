# Пункты зон кода для текстов базы `text`

Готовые строки из разделов «Для текстов» отчётов зон кода: вносит та зона, в чьём списке стоит файл пункта.
Пункт о файле вне списка зоны — не твой.

**К4а**
| `kb/text/10-templates-recipes/01-copy-deck-workflow.md` § 4.2 | «`check DECK --all-variants`: каждый живой невыбранный вариант и альтернатива мета сверяются копией страницы с одной заменой; итоги — в отчёте (`--json`: `slots.<путь>.claims.variants`, `.lint.variants`). С `--update` в файл пишутся только записи выбранных текстов.» Строка команды в конце файла: «# варианты — отчётом». |

**К4а**
| тот же файл, выбор варианта | «Открытый выбор — `copydeck.py select DECK --page ID --slot СЕКЦИЯ/СЛОТ --variant ID --by КТО -o OUT`: ставит `chosen` и `selection`. Пока все варианты слота — `draft`, выбор не требуется; вариант вышел из `draft` — без `chosen` warning COPY-D-CHOSEN.» |

**К4а**
| тот же файл, иерархии (норма F9-025) | «У страницы одна иерархия сообщений — под уровень `page.awareness`. Вторая иерархия — только у вариантной страницы: варианты первого экрана — `page.first_screen.variant_map` плана. У страницы без вариантов план одной строкой называет, как уровни сведены в один: `page.awareness_basis.rule`. Иначе `copydeck.py validate` — warning COPY-D-HIERARCHY, каркас — заметка.» |

**К4а**
| тот же файл, запись файла | «Команды записи ставят `copy_deck.date` и шапку о файле: без даты и пути, со строкой всех утверждённых страниц. Относительные ссылки считаются от папки исходного файла и при записи не меняются; файл, записанный в другую папку, возвращают на место исходного.» |

**К4а**
| `kb/text/10-templates-recipes/02-examples-ru.md`, строки о `rebase_refs` и `variant.checks` | снять упоминание `rebase_refs`; «итоги вариантов — в отчёте `check --all-variants`». |

**К4а**
| `kb/text/10-templates-recipes/README.md`, шаг вариантов и строка команды | «итоги — в отчёте; выбирает человек: `select` открыто или вслепую по листу `export-variants`»; «# варианты «как выбранные» — отчётом». |

**К4а**
| `kb/text/04-copy-by-block/04-form-emails-notifications.md`, новый абзац | «Готовое сообщение мессенджера (`messenger-prefill`): слова посетителя — приветствие и просьба, коротко; без обещаний и условий (цена, скидка, срок, гарантия) и без персональных данных; на странице не видно, текст несёт ссылка действия (`target.prefill` плана).» |

**К4а**
| `kb/text/02-strategy-messaging/` или этап `meaning` в `references/phases.md` | «Сверка смысла: `chain_inputs.py meaning-claims --meaning M --brief B -o OUT`; места фактов (`use`) на проекции не сверяются — она не страница.» |

**К4б**
| `kb/text/06-anti-slop/02-linter-spec-and-profiles.md`, п. 5 и раздел о внешних правилах (строки 17, 146–147) | «Внешние файлы правил (`profiles.yaml → external_rules`): `07-seo-geo-copy/meta-rules.yaml`, `geo-rules.yaml`, `08-russian-legal-typography/typography-rules.yaml`. Правила права `claims-rules.yaml` линтер не подключает: право формулировок проверяет `claims_check.py` — одно нарушение даёт одну находку» |

**К4б**
| `kb/text/06-anti-slop/README.md`, строка 36 | «набор — `08-russian-legal-typography/typography-rules.yaml`; право — только `claims_check.py`» |

**К4б**
| `kb/text/06-anti-slop/02-linter-spec-and-profiles.md`, пороги анализаторов | «Плотность маркеров — не выше `warning` (`allow_error: false`): пороги корпуса сняты без морфологии, линтер считает с морфологией» и «Правила микрокопи интерфейса на тексте страницы — один набор уровней у шести жанров сайта, включая `geo` и `email-form`» |

**К4б**
| `kb/text/08-russian-legal-typography/claims-rules.yaml`, шапка и блок `overrides` (файл не зоны) | шапка: «Файл читает `claims_check.py`; `copy_lint.py` его не подключает (разово — ключом `--rules`)»; блок `overrides` (14 строк понижения уровней для линтера) без подключения не работает — снять или оставить решает владелец файла |

**К4б**
| `kb/text/02-strategy-messaging/02-awareness-hierarchy-objections.md`, правила проверки иерархии | те же две нормы: `x-hero-first-optional` и `x-blocker-optional` схемы иерархии |

**К4б**
| `kb/text/05-voice-editorial/01-brand-voice.md` §2.3; `references/phases.md` (голос); `design-audit/references/rules.md` (R-COV-007) | «У продукта без сайта (кабинет, приложение, бот) профиль голоса один — `voice.product.yaml`; профиль бренда ради ссылки на него не заводится» |

**К4б**
| `kb/text/02-strategy-messaging/03-proof-and-facts.md` §7 (сущности) | «Имя услуги или продукта — сущность вида `product`: слово внутри имени не считается маркером условий покупки. Адрес и название места — сущность вида `place`: линтер не читает его как деепричастный оборот» |
