# library-example — пример библиотеки референсов на публичных наградных сайтах

Волна 1 · агент B · 2026-09-24. Формат — `../refs-library.schema.json` (`refs-library/1`); все 5 записей проходят схему
(jsonschema 4.26). Чужих работ Dribbble, Behance, Dprofile здесь нет: это публичные сайты с главной CSS Design Awards
(24.09.2026), превью — **наши** снимки первого экрана 1440×900 (Brave 153 безголовый), уменьшенные до 400×250 WebP.

| id | роль | что показывает |
|---|---|---|
| `site-farmminerals-com` | composition, material | продукт-3D в центре, заголовок и CTA по диагонали углов |
| `site-forgeautomotive-co-uk` | motion | снят на экране-заставке: скриншот не видит движения |
| `site-quakerschool-org` | motion, imagery | снят посреди анимации входа (фото раскрывается) |
| `site-format-obys-agency` | typography | собственный display во всю ширину у нижнего края |
| `site-emotion-agency-com` | other | звуковой шлюз перед сайтом — пример «не для лидогенерации» |

- Как получено: `refs_client.py get <URL…> --library 02-references-moodboards/library-example --preview-px 400` (robots.txt
  проверен по RFC 9309), затем роли, Take / Do not take и заметки заполнены вручную по превью.
- Не вошли: `secure-the-unknown.cyera.com` — сайт ответил безголовому браузеру «Not Supported»; `dattstudio.com` — 403 с
  челленджем (хост на паузе, повторов нет).
- `rights.use: internal-only`: даже наши снимки чужих сайтов — только для внутренней работы, не ассет страницы.
- Файлы: `library.jsonl` — 5 записей (строка = запись `refs-library/1`), `previews/` — наши снимки 400×250 WebP (`site-<домен>.webp`),
  `.library.lock` — служебная блокировка клиента (строка добавлена X 2026-09-25).
