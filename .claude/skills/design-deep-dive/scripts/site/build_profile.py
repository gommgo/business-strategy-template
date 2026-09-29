#!/usr/bin/env python3
"""build_profile.py — маркетинговый профиль UX-чек-листа для страниц сайта: решение по каждому пункту UX-* сводного чек-листа ux.

Читает пункты kb/ux/12-evaluation-checklists/master-checklist.yaml и пишет
kb/site/09-ai-generation-evaluation/ux-marketing-profile.tsv с колонками (строго):
    ux_id  block  ux_text_short  site_action  site_replacement  reason  source
site_action:
    keep      — действует на сайте как есть (та же проверка; серьёзность может сдвинуться на ступень по маршруту
                «визит → действие»); site_replacement — пункт SITE-*, где правило уже учтено (если есть);
    modify    — действует с поправкой (порог, серьёзность, условие или объём); site_replacement — пункт с поправкой;
    off       — в профиле site не проверяется: объекта на сайте нет (таблицы данных, настройки, админка, ИИ-функции,
                деструктив) или правило — визуальный слой creative; причина — в reason;
    replaced  — заменён пунктом SITE-* (или CRV-*, COPY-* — нормы creative и text) с нормой сайта; замена обязательна.
Решения — по блокам (BLOCK_DEFAULT) с точечными исключениями (DECISIONS); основание решения — колонка source (пути —
от kb/site/). Рядом — наследование для автопроверок AC-* ux (ac-profile.tsv) и сводка в $DDD_HOME/out/site/build_profile/.

Сверка с версией чек-листа ux: решения сверены с версией CHECKLIST_REVIEWED (поле source_sha256_16 файла чек-листа).
Новая версия чек-листа — отказ записи и находка --check со списком новых, снятых и изменённых пунктов (сравнение с
профилем на диске): пункт без точечного решения получает умолчание блока, изменённый пункт с точечным решением —
на пересмотр; после сверки версия записывается в CHECKLIST_REVIEWED, профиль пересобирается.

Запуск (от корня скилла):
    python3 scripts/site/build_profile.py              # записать профиль, ac-profile.tsv и сводку
    python3 scripts/site/build_profile.py --check      # профиль совпадает с решениями и версией чек-листа? (код 1 — нет)
    python3 scripts/site/build_profile.py --selftest   # сверка версии, замены, ссылки источников — на подложенных данных
Проверки: строк — столько, сколько пунктов в чек-листе (items_count); действие из четырёх; у replaced непустая замена;
каждый SITE-* есть в site-checklist.yaml, COPY-* — в copy-checklist.yaml или copy-rubric.yaml text, CRV-* — в
определениях creative (ambition-levels.yaml и чек-листы разделов); путь в source ведёт в существующий файл или папку;
решения только для существующих id; пункты, которые аудит UX назвал спорными для лендинга, не оставлены keep.
Только стандартная библиотека + PyYAML.
"""
import argparse
import collections
import io
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('site'))
APP = str(kbpaths.kb())
UX_YAML = os.path.join(APP, 'ux', '12-evaluation-checklists', 'master-checklist.yaml')
UX_AC_MD = os.path.join(APP, 'ux', '12-evaluation-checklists', '03-automated-checks.md')
SITE_YAML = os.path.join(ROOT, '09-ai-generation-evaluation', 'site-checklist.yaml')
COPY_YAMLS = [os.path.join(APP, 'text', '09-ai-generation-evaluation', f) for f in ('copy-checklist.yaml', 'copy-rubric.yaml')]
CRV_YAML = os.path.join(APP, 'creative', '01-creative-direction', 'ambition-levels.yaml')
CRV_DIR = os.path.join(APP, 'creative')
OUT_TSV = os.path.join(ROOT, '09-ai-generation-evaluation', 'ux-marketing-profile.tsv')
OUT_AC = str(kbpaths.kb('site', '99-raw', 'experiments', 'K', '02-ux-profile', 'ac-profile.tsv'))
ACTIONS = ('keep', 'modify', 'off', 'replaced')
COLS = ('ux_id', 'block', 'ux_text_short', 'site_action', 'site_replacement', 'reason', 'source')
ID_RX = re.compile(r'\b(?:SITE-[A-Z0-9]{2,5}-\d{2}|COPY-[A-Z]-\d{2}|CRV-[A-Z]+-\d{2})\b')
CRV_DEF_RX = re.compile(r'^\s*(?:-\s+(?:id:\s*)?|id:\s*)(CRV-[A-Z]+-\d{2})\b', re.M)   # определение: «- CRV-…» или «id: CRV-…»
PATH_RX = re.compile(r'^[\w.-]*/[\w./-]*$|^[\w./-]+\.(?:md|yaml|yml|json|tsv|csv|py)$')    # путь-основание в колонке source

# Версия чек-листа ux (source_sha256_16 master-checklist.yaml), с которой сверены решения профиля.
CHECKLIST_REVIEWED = '77bad8ab0088c710'

# Пункты, которые аудит UX (§4 п.1–17, §7 п.3) называет ложными блокерами или спорными для лендинга: keep запрещён.
AUDIT_FLAGGED = ('UX-FBK-14', 'UX-FBK-15', 'UX-LAY-02', 'UX-LAY-16', 'UX-LAY-03', 'UX-LAY-09', 'UX-LAY-13', 'UX-NAV-12',
                 'UX-AIG-01', 'UX-AIG-06', 'UX-OVL-02', 'UX-CNS-23', 'UX-TXT-13', 'UX-TXT-14', 'UX-FLW-18', 'UX-ETH-12',
                 'UX-FBK-12', 'UX-PRE-05')

# Решение по блоку: (действие, замена, причина, источник) — для пунктов без точечного решения.
BLOCK_DEFAULT = {
    'PRE': ('off', '', 'входной контракт приложения; вход сайта — бриф, факты, карта и планы (блок SITE-PRE)', 'PLAN №10; аудит UX §4 п.13'),
    'BLD': ('keep', '', 'общее условие сборки', '../ux/12-evaluation-checklists/03-automated-checks.md §3.1'),
    'A11': ('keep', '', 'доступность маркетинговой страницы — как у сервиса (WCAG 2.2 AA); серьёзность — профиль I по маршруту «визит → действие»',
            '08-legal-trust-a11y/03-a11y-marketing-pages.md §8'),
    'STA': ('off', '', 'состояний данных у посадочной нет (коллекций, загрузки данных, прав)', 'PLAN №10; 09-ai-generation-evaluation/02-site-checklist.md §2'),
    'NAV': ('keep', '', 'навигация сайта — чек-лист G (SITE-NAV)', '06-multipage-ia/02-navigation-linking-i18n.md'),
    'LAY': ('keep', '', 'правило раскладки действует', '../ux/03-layout-placement/'),
    'FRM': ('keep', '', 'лид-форма — та же форма: канон форм ux действует (lead-forms.yaml defaults)', '05-conversion-funnels/lead-forms.yaml defaults'),
    'DAT': ('off', '', 'таблиц данных, фильтров, дашбордов и экранов объекта у маркетинговой страницы нет', 'PLAN №10'),
    'OVL': ('keep', '', 'окна сайта (форма в окне, меню, баннер) подчиняются тем же правилам оверлеев', '05-conversion-funnels/01-cta-and-lead-capture.md §11'),
    'FLW': ('off', '', 'многошаговых рабочих сценариев у сайта нет: маршрут «визит → действие» — одна форма или квиз', 'PLAN №10'),
    'ACT': ('off', '', 'изменяющих и деструктивных действий у посетителя сайта нет; действие сайта — призыв и форма', 'PLAN №9, №10'),
    'SET': ('off', '', 'настроек, прав и админки у маркетинговой страницы нет', 'PLAN №10'),
    'FBK': ('keep', '', 'обратная связь на действие посетителя', '../ux/06-feedback-states-motion/02-system-status-and-waiting.md'),
    'ETH': ('keep', '', 'тёмные паттерны на сайте запрещены так же', '08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §4'),
    'AIG': ('keep', '', 'ошибка генерации встречается и на сайте', '../ux/11-ai-generated-ui/01-failure-modes-catalog.md'),
    'TXT': ('off', '', 'тексты сайта — зона text (copy-checklist.yaml); site проверяет только подписи действия и формы', 'контракт v2 §2'),
    'MOB': ('keep', '', 'мобильная адаптация действует', '../ux/09-mobile/'),
    'CNS': ('off', '', 'консистентность дизайн-системы продукта; визуальная система сайта — creative (04-visual-language, marketing-tokens), единство многостраничника — SITE-NAV-09',
            'PLAN №8; ../creative/04-visual-language/03-color-surfaces-product.md'),
    'APP': ('off', '', 'подблоки APP (ADM, CLI, AIF, PRC) — типы приложений; ветку «сайт» играет сводный чек-лист SITE-*', 'PLAN №10; аудит UX §4 п.13, §7 п.3'),
    'OUT': ('keep', '', 'ворота выдачи действуют', '../ux/12-evaluation-checklists/02-master-checklist.md §3'),
}

# Точечные решения: id|действие|замена (через запятую)|причина|источник
DECISIONS = r"""
UX-PRE-01|replaced|SITE-PRE-04|вместо ролей и частоты работы — источники трафика: температура, устройство, доля, обещание источника; осведомлённость по главному источнику|PLAN №10; 01-foundations/01-how-visitors-decide.md §3
UX-PRE-02|replaced|SITE-PRE-03|одно целевое действие страницы (macro-id action); вторая цель — secondary_actions иным стилем|PLAN №1, №10; 01-foundations/03-site-brief.md §2.3
UX-PRE-03|modify|SITE-PRE-16|выводы исследований на сайте — возражения и голос клиента в брифе и copy-deck; ограничение — хвост из возражений страницы|PLAN №10; 03-page-structure/01-narratives-and-section-order.md §3.4
UX-PRE-04|off||постура и плотность — для инструментов с повторным использованием; визит на сайт разовый, ритм и воздух — подача creative|PLAN №2
UX-PRE-05|off||объектная модель посадочной не нужна (OOUX к лендингу не применяется)|PLAN №9, №10; аудит UX §4 п.13
UX-PRE-06|replaced|SITE-PRE-10|карта экранов → карта сайта site-map: страницы брифа в pages[], шаблоны, «спасибо», build_order|PLAN №10; 06-multipage-ia/01-sitemaps-templates-content-model.md
UX-PRE-07|modify|SITE-TRK-03|переход на сайте переживают метки источника и выбор посетителя (тариф, город) до формы и CRM; фильтров и черновиков нет|05-conversion-funnels/03-multi-page-funnels.md §2.2
UX-PRE-08|replaced|SITE-PRE-20|состояния сайта — у формы: набор lead-forms.yaml задаёт ошибку, отправку и успех («спасибо»)|PLAN №10; 05-conversion-funnels/lead-forms.yaml
UX-PRE-09|replaced|SITE-PRE-15, SITE-PRE-18|компоненты сайта — блоки blocks.yaml в плане; заземление — «нет факта — нет блока»; визуальная система — treatment creative|PLAN №10; 04-blocks/blocks.yaml conventions.no-fact-no-block
UX-PRE-10|replaced|SITE-PRE-05|вместо набора данных с крайними случаями — инвентарь фактов (источник, дата, разрешение); длины текстов — text|PLAN №10, №26; 01-foundations/03-site-brief.md §3
UX-PRE-11|replaced|COPY-C-05|словарь и запреты текста — линтер text в профиле жанра|контракт v2 §2 (тексты — text)
UX-PRE-12|modify|SITE-PRE-11, SITE-PRE-25|эталон подачи — референсы и treatment creative; описание взаимодействий — page-plan (секции, действия, события)|PLAN №10; ../creative/01-creative-direction/02-art-direction-document.md
UX-PRE-13|modify|SITE-OUT-08|запреты сайта — маркеры AIL с полем allow (законный приём разрешает бриф), а не безусловный бан-лист|09-ai-generation-evaluation/ai-landing-markers.yaml
UX-PRE-14|off||таблиц данных у посадочной нет; сравнение ≤ 5 вариантов — SITE-BLK-10|PLAN №10
UX-PRE-15|replaced|SITE-PRE-20, SITE-FRM-02|контракт поля — набор формы lead-forms.yaml (form.ref): поля, why, autocomplete, проверка, успех|05-conversion-funnels/lead-forms.yaml; 05-conversion-funnels/01-cta-and-lead-capture.md §3
UX-PRE-16|replaced|SITE-PRF-05|вместо шаблона плитки KPI — число-доказательство: подпись, источник, дата, округление вниз|04-blocks/01-blocks-catalog.md §4.2
UX-PRE-17|off||изменяющих необратимых действий у посетителя нет; отправка формы — SITE-FRM-01|PLAN №10
UX-PRE-18|keep|SITE-A11Y-08, SITE-A11Y-11|целевой уровень WCAG 2.2 AA, видимый фокус и цели касания объявляются в TASK так же|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-BLD-01|keep||сборка без ошибок — общее условие приёмки|../claude-design/06-design-process/04-checks.md §3
UX-BLD-02|modify|SITE-GEO-01|мало «рендерит непустое»: H1, смысл, цены и CTA — в HTML сервера без JS|07-seo-geo-performance-analytics/head-kit.yaml hk-access-ssr
UX-BLD-04|modify|SITE-OUT-13|у многостраничника маршруты = страницы site-map (ia_probe); у посадочной — одна страница|06-multipage-ia/01-sitemaps-templates-content-model.md; ../../scripts/site/ia_probe.py
UX-BLD-05|keep|SITE-OUT-13|битых ссылок меню и подвала нет; href="#" у призыва — маркер AIL-44|../../scripts/site/ia_probe.py; 09-ai-generation-evaluation/ai-landing-markers.yaml
UX-BLD-06|modify|SITE-NAV-15|индексируемая страница — не сирота; посадочная под рекламу законно вне меню|06-multipage-ia/02-navigation-linking-i18n.md §3.5
UX-BLD-07|keep|SITE-PRE-10|страниц вне site-map нет (выдуманные страницы — дефект сборки)|06-multipage-ia/01-sitemaps-templates-content-model.md
UX-BLD-08|keep|SITE-FRM-01, SITE-BLK-14, SITE-CTA-13|каждая кнопка и ссылка что-то делает: форма отправляется, призыв нажимается, кнопки — button и a href|05-conversion-funnels/01-cta-and-lead-capture.md §9
UX-BLD-09|modify|SITE-BLK-01|секции — из каталога blocks.yaml в объявленном варианте; визуальные компоненты — система creative|04-blocks/01-blocks-catalog.md §1.1
UX-BLD-10|off||шкала токенов — визуальный слой creative (marketing-tokens.json), не пункт site|../creative/04-visual-language/marketing-tokens.json; контракт v2 §2
UX-BLD-11|keep|SITE-OUT-07|правка не выходит за область; после правки — полный прогон, регресс — откат|../claude-design/06-design-process/03-edit-loop-and-stop.md §4
UX-BLD-12|modify|SITE-CTA-01, SITE-FRM-11|тупик сайта — страница без целевого действия и «спасибо» без следующего шага; одноэкранная арт-страница без ссылок вне шапки — не дефект|05-conversion-funnels/01-cta-and-lead-capture.md §10; 05-conversion-funnels/03-multi-page-funnels.md
UX-A11-01|modify|SITE-A11Y-04|B — для H1, лида, призыва и строки согласия (и на медиа по F83), прочий текст — S; тема обычно одна|08-legal-trust-a11y/03-a11y-marketing-pages.md §4, §8
UX-A11-02|modify|SITE-A11Y-09|S; B — для логотипов клиентов и схем; декоративные — alt=""|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-A11-03|keep|SITE-A11Y-06, SITE-FRM-18|подпись поля и галочки согласия — B на маршруте действия|08-legal-trust-a11y/03-a11y-marketing-pages.md §6, §8
UX-A11-04|keep|SITE-A11Y-05|иконки соцсетей, мессенджеров, стрелки — с именем|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-A11-05|keep|SITE-A11Y-10|lang задан и верен (для поиска — SITE-SEO-08)|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-A11-06|keep|SITE-BLK-03, SITE-SEO-19|ровно один H1 — в hero, а не в «шапке страницы»; дисплейный заголовок = H1|04-blocks/blocks.yaml conventions.one-h1
UX-A11-07|modify|SITE-BLK-02|<header> — только шапка сайта; hero и секции — <section> внутри одного <main>|PLAN №4, №15; 04-blocks/blocks.yaml conventions.landmarks
UX-A11-08|keep||skip-ссылка при меню в шапке (WCAG 2.4.1); у шапки landing-minimal достаточно лендмарков|../ux/08-accessibility/02-keyboard-focus-semantics.md
UX-A11-09|keep|SITE-A11Y-11|фокус видим, контраст ≥ 3:1 (1.4.11)|../creative/01-creative-direction/ambition-levels.yaml CRV-AL-07
UX-A11-10|keep|SITE-A11Y-12|Tab проходит шапку, призыв, форму и баннер; перехват колеса не мешает|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-A11-11|keep|SITE-A11Y-12, SITE-BLK-04|порядок фокуса = визуальному, без CSS order|04-blocks/blocks.yaml conventions.dom-order
UX-A11-12|modify|SITE-A11Y-11|на сайте — B: баннер cookie, липкая шапка, липкий призыв и чат есть почти всегда|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-A11-13|keep||не только цветом (ошибки формы, тарифы, «популярный»)|../ux/08-accessibility/01-wcag22-as-build-rules.md
UX-A11-14|keep|SITE-A11Y-08|цель ≥ 24×24 или зазор везде (2.5.8, AA); на таче каждая цель ≥ 44×44 зоной нажатия, видимый контрол может быть меньше; исключения 2.5.8 — ссылка в абзаце|../ux/08-accessibility/01-wcag22-as-build-rules.md §12.4
UX-A11-15|keep|SITE-NAV-05|подменю по клику и Enter, не только по наведению; слайдер «до/после» — с кнопками|06-multipage-ia/02-navigation-linking-i18n.md §1.3
UX-A11-16|keep|SITE-A11Y-14|успех и ошибка формы, выбор в баннере — объявляются|08-legal-trust-a11y/03-a11y-marketing-pages.md §5
UX-A11-17|keep|SITE-A11Y-18, SITE-MOB-01|зум 200 %: кегли на clamp с max ≤ 2,5 × min; 320 px без горизонтальной прокрутки|../creative/04-visual-language/01-display-typography.md §2.2
UX-A11-18|keep|SITE-FRM-06|введённое сохраняется при ошибке; «повторите почту» запрещено|05-conversion-funnels/lead-forms.yaml forbidden
UX-A11-19|keep||видимая подпись входит в доступное имя (2.5.3)|../ux/08-accessibility/01-wcag22-as-build-rules.md
UX-A11-20|keep|SITE-CTA-03|ссылки и призывы называют результат, не «Подробнее»|05-conversion-funnels/01-cta-and-lead-capture.md §1.3
UX-A11-21|keep|SITE-NAV-05|ARIA — только без нативного решения; role="menu" в навигации сайта — дефект (AIL-22)|06-multipage-ia/02-navigation-linking-i18n.md §1.3
UX-A11-22|keep|SITE-NAV-09|контакты и помощь — в одном месте шапки и подвала на всех страницах (3.2.6)|06-multipage-ia/02-navigation-linking-i18n.md §1.5
UX-STA-01|modify|SITE-FRM-06, SITE-FRM-11|состояния на сайте — у формы (ошибка, отправка, успех) и у виджетов с данными; экранов данных нет|05-conversion-funnels/lead-forms.yaml defaults.success
UX-STA-06|modify|SITE-NAV-12|только на многостраничнике с поиском по сайту; результаты — noindex|06-multipage-ia/02-navigation-linking-i18n.md §2.4
UX-STA-08|keep|SITE-PERF-03|CLS ≤ 0,1 (> 0,25 — B по профилю)|07-seo-geo-performance-analytics/page-gates.yaml SG-PERF-03
UX-STA-09|modify|SITE-FRM-06|ошибки сайта — ошибка отправки формы и 404 (SITE-SEO-01): причина, шаг, выход|05-conversion-funnels/lead-forms.yaml defaults.validation
UX-STA-11|modify|SITE-PERF-06|сторонние виджеты (карта, отзывы, чат) — фасадом по видимости; их отказ не ломает страницу|07-seo-geo-performance-analytics/03-performance-budgets-gates.md §5
UX-STA-12|keep|SITE-FRM-06|ввод сохраняется при любой ошибке отправки|05-conversion-funnels/lead-forms.yaml defaults.validation
UX-STA-13|modify|SITE-PRF-04|«мало — расчётно — много» на сайте — минимумы доказательств: логотипов ≥ 4, чисел 2–5, отзывов ≥ 2; без фактов блока нет|05-conversion-funnels/02-proof-pricing-risk.md §1.3
UX-STA-14|keep||hover, focus-visible, active, loading у кнопки отправки; disabled до нажатия — запрет (SITE-FRM-05)|05-conversion-funnels/lead-forms.yaml defaults
UX-STA-15|off||организация кода компонентов — зона исполнителя и creative; на приёмку сайта не влияет|контракт v2 §2
UX-STA-16|replaced|SITE-PRF-01, SITE-OUT-03|на сайте не фикстуры, а публикуемые доказательства: связка с fact:, заглушки — блокер|PLAN №7; 08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §1.3
UX-STA-17|modify|SITE-A11Y-03, SITE-A11Y-18|среда сайта: reduce (конечные состояния, 0 байт видео), зум; тёмная тема — если есть в подаче|../creative/01-creative-direction/ambition-levels.yaml CRV-AL-01
UX-STA-18|modify|SITE-FRM-06, SITE-PERF-01|режимы сайта — ошибка отправки формы и медленная сеть телефона (троттлинг)|07-seo-geo-performance-analytics/03-performance-budgets-gates.md §2.1
UX-NAV-01|replaced|SITE-NAV-03|архетип шапки — по типу сайта с записанной причиной; «Главная · Услуги · О нас · Блог · Контакты» без хабов — маркер AIL-11|PLAN №3, №24; 06-multipage-ia/02-navigation-linking-i18n.md §1.2
UX-NAV-02|keep|SITE-NAV-09|шапка и подвал одинаковы на всех страницах (3.2.3)|06-multipage-ia/02-navigation-linking-i18n.md §1.5
UX-NAV-03|off||сайдбара у сайта нет: навигация — шапка сверху|PLAN №3
UX-NAV-04|modify|SITE-NAV-11|на многостраничнике — D: разделы не рабочие режимы; у посадочной разделов нет|06-multipage-ia/02-navigation-linking-i18n.md §2.3
UX-NAV-05|replaced|SITE-NAV-05|подменю шапки — по клику и Enter, aria-expanded, Esc, без каскада второго уровня|06-multipage-ia/02-navigation-linking-i18n.md §1.3
UX-NAV-06|keep|SITE-NAV-06|на десктопе без гамбургера|06-multipage-ia/02-navigation-linking-i18n.md §1.3
UX-NAV-07|replaced|SITE-NAV-10|крошки — на многостраничнике с глубины ≥ 2 у разделов с хабом; на посадочной — нет|PLAN №4; 06-multipage-ia/02-navigation-linking-i18n.md §2.1
UX-NAV-08|off||кнопки «Назад» приложения у сайта нет|PLAN №4
UX-NAV-09|keep|SITE-BLK-12|для блока feature-tabs: ≤ 7 вкладок в ряд, короткие подписи, содержимое в HTML|04-blocks/blocks.yaml
UX-NAV-10|replaced|SITE-NAV-20|логотип слева → главная на всех страницах, включая посадочные без меню; на сайте — S, не D|04-blocks/blocks.yaml conventions.logo-home
UX-NAV-11|off||утилит приложения (уведомления, аккаунт) у сайта нет; «Войти» и язык — ссылки шапки|PLAN №3
UX-NAV-12|modify|SITE-MOB-05, SITE-CTA-06|допустимы липкая шапка и липкий призыв снизу, вместе ≤ 20 % высоты телефона; расхождение ux (UX-NAV-12 против AC-NAV-06) снято|аудит UX §4 п.6; 03-page-structure/03-first-screen-and-mobile.md §4.2
UX-NAV-13|keep|SITE-CTA-03|одно действие — одна подпись во всех местах; повтор призыва законен|05-conversion-funnels/01-cta-and-lead-capture.md §1.3
UX-NAV-14|modify|SITE-NAV-06, SITE-MOB-02|телефон: кнопка «Меню» с полноэкранным списком и липкий призыв; нижняя панель вкладок — не для сайта|PLAN №3
UX-NAV-15|modify|SITE-NAV-12|только на многостраничнике с поиском; решение записано в chrome.search.why|06-multipage-ia/02-navigation-linking-i18n.md §2.4
UX-LAY-01|modify|SITE-STR-06, SITE-STR-08|точка входа первого экрана — оффер и призыв; у формы poster — образ, призыв в шапке и признак продолжения|PLAN №23; 03-page-structure/03-first-screen-and-mobile.md §1.3, §2.2
UX-LAY-02|replaced|SITE-CTA-02, SITE-CTA-04|одно целевое действие, его повтор в местах решения — норма (медиана 4 призыва); второй путь — иным стилем|PLAN №1; аудит UX §4 п.2
UX-LAY-03|replaced|SITE-BLK-03, SITE-NAV-20|H1 живёт в hero; путь назад — логотип и шапка; крошки — на многостраничнике с третьего уровня|PLAN №4; аудит UX §4 п.3
UX-LAY-04|modify|SITE-STR-06|squint — по первому экрану и по секции: одна точка входа на экран, а не на страницу|03-page-structure/03-first-screen-and-mobile.md §1.3
UX-LAY-05|keep||иерархия в оттенках серого; для призыва работает контраст, а не цвет|../ux/03-layout-placement/03-hierarchy-and-attention.md §10.2
UX-LAY-06|off||ритм и отступы секций — «этажи» creative; шкала — marketing-tokens|../creative/04-visual-language/02-composition-rhythm-sections.md §3.1
UX-LAY-07|off||рамки и разделители — визуальный слой creative|контракт v2 §2
UX-LAY-08|keep||45–75 знаков — для текста тела; display-заголовки — роли creative|../creative/04-visual-language/01-display-typography.md
UX-LAY-09|off||три кегля ложно срабатывают на display-заголовках; роли кеглей — creative (display-s…xl, poster)|аудит UX §4 п.4; ../creative/04-visual-language/01-display-typography.md
UX-LAY-10|off||цвет сайта задают бренд и уровень (creative); ошибка формы — не только цветом (UX-A11-13)|../creative/04-visual-language/03-color-surfaces-product.md
UX-LAY-11|off||панелей рабочего экрана у сайта нет|PLAN №10
UX-LAY-12|replaced|SITE-STR-09|ложный пол: hero на весь экран — с признаком продолжения; offer-cta — 60–85 % высоты окна|PLAN №2; 03-page-structure/03-first-screen-and-mobile.md §2.2
UX-LAY-13|replaced|SITE-A11Y-01, SITE-A11Y-02, CRV-AL-02|бюджет одновременного движения — по уровню амбиций (creative); site держит паузу для движения > 5 с и вспышки|PLAN №21; аудит UX §4 п.5
UX-LAY-14|off||счётчиков-бейджей у сайта нет|PLAN №10
UX-LAY-15|modify|SITE-LEGAL-09, SITE-MOB-05|на сайте законны баннер cookie и закреплённая полоса акции (с маркировкой); липкие слои ≤ 20 % экрана|08-legal-trust-a11y/01-law-ru-eu.md; 03-page-structure/03-first-screen-and-mobile.md §4.2
UX-LAY-16|replaced|SITE-CTA-02|повтор призыва в шапке, hero, после доказательств, в финале и липким — норма; не после каждой секции (AIL-33)|PLAN №1; аудит UX §4 п.2
UX-LAY-17|keep|SITE-FRM-04|кнопка под полями, одна колонка|05-conversion-funnels/lead-forms.yaml defaults.layout
UX-LAY-18|modify|SITE-STR-06, SITE-STR-09|первый экран 1440×900 и 390×844 показывает обязательное по first_screen_policy и признак продолжения|03-page-structure/03-first-screen-and-mobile.md §1.3
UX-FRM-01|keep|SITE-FRM-01, SITE-FRM-04|<form>, type=submit, видимые подписи; без <form> не работают отправка без JS и цель|05-conversion-funnels/01-cta-and-lead-capture.md §9
UX-FRM-02|keep|SITE-FRM-04|autocomplete у каждого поля|05-conversion-funnels/lead-forms.yaml defaults
UX-FRM-03|modify|SITE-FRM-06|у короткой лид-формы (1–3 поля) сводка не нужна: сообщение у поля и фокус на первом ошибочном|05-conversion-funnels/lead-forms.yaml defaults.validation
UX-FRM-04|keep|SITE-FRM-06|сообщение у каждого поля|05-conversion-funnels/lead-forms.yaml defaults.validation
UX-FRM-05|keep|SITE-FRM-06|введённое сохраняется после ошибки|05-conversion-funnels/lead-forms.yaml defaults.validation
UX-FRM-06|keep|SITE-FRM-05|кнопка активна до нажатия, блокируется после; повтор не создаёт второй заявки|05-conversion-funnels/lead-forms.yaml forbidden
UX-FRM-07|keep|SITE-FRM-04|одна колонка|05-conversion-funnels/lead-forms.yaml defaults.layout
UX-FRM-09|keep|SITE-FRM-04|подписи над полями, плейсхолдер ≠ подпись|05-conversion-funnels/lead-forms.yaml defaults.layout
UX-FRM-11|keep|SITE-FRM-04|прощающая маска телефона, вставка не блокируется|05-conversion-funnels/lead-forms.yaml defaults
UX-FRM-13|keep|SITE-FRM-06|ошибка у поля, не только цветом|05-conversion-funnels/lead-forms.yaml defaults.validation
UX-FRM-14|modify|SITE-FRM-06|сводка ошибок — только у длинной формы и квиза; у лид-формы — сообщение у поля|05-conversion-funnels/lead-forms.yaml defaults.validation
UX-FRM-16|keep|SITE-CTA-03, SITE-FRM-13|одна кнопка отправки; подпись называет результат и совпадает на «спасибо»|05-conversion-funnels/01-cta-and-lead-capture.md §1.3
UX-FRM-17|keep|SITE-FRM-05|type=reset и «Очистить» запрещены|05-conversion-funnels/lead-forms.yaml forbidden
UX-FRM-18|keep|SITE-A11Y-12|порядок Tab = визуальному|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-FRM-19|modify|SITE-FRM-03|строже: ≤ 3 видимых поля в первом экране, ≤ 5 в потоке; квиз — 3–7 вопросов по одному|05-conversion-funnels/lead-forms.yaml defaults; 05-conversion-funnels/01-cta-and-lead-capture.md §5.3
UX-FRM-20|keep|SITE-FRM-03|форма в окне — ≤ 4 поля без прокрутки|05-conversion-funnels/lead-forms.yaml defaults.modal_max_fields
UX-FRM-23|off||переключателей настроек у лид-формы нет|PLAN №10
UX-FRM-24|keep|SITE-LEGAL-01, SITE-LEGAL-03|согласие ПД и рассылки — пустые отдельные галочки (152-ФЗ в ред. 156-ФЗ, с 01.09.2025)|08-legal-trust-a11y/legal-requirements.yaml LR-RU-01, LR-RU-11
UX-FRM-25|off||disabled и read-only у лид-формы не нужны; кнопка отправки не disabled до нажатия (SITE-FRM-05)|05-conversion-funnels/lead-forms.yaml forbidden
UX-FRM-26|replaced|SITE-FRM-07, SITE-A11Y-15|антиспам без трения: honeypot, time-trap, лимиты; видимой капчи и reCAPTCHA для РФ по умолчанию нет|05-conversion-funnels/01-cta-and-lead-capture.md §8
UX-FRM-27|off||длинных необратимых процессов у сайта нет; у квиза — «Назад» (SITE-FRM-09)|PLAN №10
UX-FRM-28|off||формы входа на маркетинговой странице нет|PLAN №10
UX-DAT-02|modify|SITE-NAV-13|только хабы многостраничника (каталог, блог): пагинация и «Показать ещё» — ссылками <a href>; фильтры не индексируются|06-multipage-ia/02-navigation-linking-i18n.md §3.2
UX-DAT-10|modify|SITE-BLK-10|таблицы тарифов и сравнения: строки одинаковы по смыслу, числа выровнены, не картинкой|04-blocks/01-blocks-catalog.md §6.3
UX-DAT-13|modify|SITE-NAV-13, SITE-SEO-18|фильтры каталога — в URL, но закрыты от индексации|06-multipage-ia/02-navigation-linking-i18n.md §3.2; 07-seo-geo-performance-analytics/crawlers.yaml rt-infinite-spaces
UX-DAT-17|modify|SITE-PRF-05|число на сайте — доказательство: подпись, источник, дата; база сравнения — если число относительное|04-blocks/01-blocks-catalog.md §4.2
UX-DAT-18|off||плиток дашборда у сайта нет; ряд чисел — доказательство (SITE-PRF-04), «ряд чисел ↔ фичи» — маркер AIL-02|03-page-structure/01-narratives-and-section-order.md §3.4
UX-DAT-19|keep||если на странице есть график (кейс, отчёт) — длина и позиция, круговые — с причиной|../ux/04-components-patterns/03-dashboards-and-kpi.md §5
UX-DAT-20|keep||у графика — текстовая альтернатива; цвет не единственный канал|../ux/08-accessibility/03-forms-tables-dynamic-content.md
UX-DAT-24|modify|SITE-FRM-13|услуга и тариф называются одинаково на странице, в форме, на «спасибо» и в письме|05-conversion-funnels/03-multi-page-funnels.md §2
UX-OVL-01|keep|SITE-FRM-03|контейнер по критериям: форма в окне ≤ 4 полей, баннер cookie — немодальный|05-conversion-funnels/lead-forms.yaml defaults.modal_max_fields
UX-OVL-02|replaced|SITE-CTA-07, SITE-CTA-08, SITE-LEGAL-06, SITE-A11Y-14|обязательный баннер cookie — законное исключение (немодальный, равные кнопки, не закрывает фокус); окно захвата и чат сами не открываются|PLAN №6; аудит UX §4 п.10
UX-OVL-04|keep|SITE-FRM-03|окно формы не прокручивается|05-conversion-funnels/lead-forms.yaml defaults.modal_max_fields
UX-OVL-06|keep|SITE-FRM-05|Esc и видимая кнопка закрывают окно, фокус возвращается|05-conversion-funnels/lead-forms.yaml
UX-OVL-09|keep|SITE-CTA-09|в окне ≤ 2 действий; отказ нейтральной подписью|08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §4
UX-OVL-12|modify|SITE-MOB-04, SITE-CTA-08|типичный сбой сайта — баннер cookie, окно и чат одновременно над призывом; баннер обязателен, остальное — по нажатию|03-page-structure/03-first-screen-and-mobile.md §1.4
UX-OVL-13|keep|SITE-FRM-06|ошибка отправки — у формы, не тостом и не alert()|05-conversion-funnels/01-cta-and-lead-capture.md §9
UX-OVL-14|off||тостов у сайта нет; всплывающие «Мария купила» — запрет (SITE-PRF-16)|08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §4
UX-OVL-15|off||тостов у сайта нет|PLAN №10
UX-OVL-16|modify|SITE-CTA-08, SITE-CTA-13|на сайте перекрывают не тосты, а плавающие мессенджеры, чат и баннер: призыв нажимается (elementFromPoint)|05-conversion-funnels/01-cta-and-lead-capture.md §2
UX-OVL-17|keep|SITE-FRM-11|успех — одним состоянием («спасибо»), не alert() и страницей сразу|05-conversion-funnels/01-cta-and-lead-capture.md §10
UX-OVL-18|modify|SITE-LEGAL-06|баннер cookie закрывается только выбором; полоса акции — закрываемая|08-legal-trust-a11y/legal-requirements.yaml LR-RU-10, LR-EU-02
UX-FLW-01|modify|SITE-FRM-01, SITE-TRK-01|сценарий сайта — «визит → призыв → форма → спасибо» на своём стенде; на чужих сайтах формы не отправлять|09-ai-generation-evaluation/02-site-checklist.md §1.3
UX-FLW-02|modify|SITE-FRM-09|«Назад» — в шагах квиза; «Назад» браузера закрывает окно формы и меню телефона|05-conversion-funnels/01-cta-and-lead-capture.md §5.3
UX-FLW-05|modify|SITE-FRM-09|у квиза — честный прогресс и понятно, что осталось|05-conversion-funnels/01-cta-and-lead-capture.md §5.3
UX-FLW-08|keep|SITE-FRM-05|ничего не спрашивается дважды (3.3.7): «повторите почту» — запрет|05-conversion-funnels/lead-forms.yaml forbidden
UX-FLW-09|modify|SITE-PRE-20|форма, квиз или калькулятор выбираются по набору lead-forms.yaml и задаче страницы|05-conversion-funnels/01-cta-and-lead-capture.md §3
UX-FLW-10|modify|SITE-FRM-09|шаги квиза: честное число шагов|05-conversion-funnels/01-cta-and-lead-capture.md §5.3
UX-FLW-11|replaced|SITE-FRM-11|«спасибо»: статус первым, что дальше, кто и когда, канал, номер, один шаг|05-conversion-funnels/01-cta-and-lead-capture.md §10
UX-FLW-12|modify|SITE-FRM-11|на «спасибо» — один следующий шаг, а не 2–3|05-conversion-funnels/lead-forms.yaml defaults.success
UX-FLW-14|modify|SITE-SEO-01|404 — честный код, шапка и подвал сайта, пути дальше|07-seo-geo-performance-analytics/head-kit.yaml hk-access-404
UX-FLW-17|replaced|SITE-STR-06, SITE-STR-07|первые секунды — первый экран: категория, оффер, призыв; пятисекундный тест (03)|03-page-structure/03-first-screen-and-mobile.md §1.2; 09-ai-generation-evaluation/03-expert-review-and-judge.md
UX-FLW-18|replaced|SITE-CTA-07|окна при входе нет; автопоказ — только решением заказчика по условиям F|PLAN №5; 05-conversion-funnels/01-cta-and-lead-capture.md §11
UX-FLW-20|modify|SITE-MOB-04, SITE-CTA-07|прерывания маршрута «визит → действие»: баннер, окно, чат — считать на телефоне|03-page-structure/03-first-screen-and-mobile.md §1.4
UX-ACT-01|replaced|SITE-PRE-20|действие сайта — слот action плана: id действия, стиль, подпись, форма, событие|10-playbooks-contracts/schemas/page-plan.schema.json
UX-ACT-02|keep|SITE-FRM-13|одно имя действия на кнопке, в форме, на «спасибо», в письме|05-conversion-funnels/03-multi-page-funnels.md §2
UX-ACT-03|modify|SITE-CTA-03|подпись призыва называет результат («Вызвать замерщика»); формулировку проверяет text (COPY-R-09)|05-conversion-funnels/01-cta-and-lead-capture.md §1.3
UX-ACT-14|keep|SITE-FRM-05|защита от двойной отправки: кнопка блокируется после нажатия, дубли заявок не создаются|05-conversion-funnels/lead-forms.yaml defaults
UX-ACT-18|keep||у перетаскивания (слайдер «до/после») — кнопки и клавиатура (2.5.7)|../ux/04-components-patterns/10-actions-menus-bulk-shortcuts.md §6
UX-FBK-01|keep|SITE-PERF-04|реакция на нажатие ≤ 100 мс; ворота — INP ≤ 200 мс|07-seo-geo-performance-analytics/page-gates.yaml SG-PERF-04
UX-FBK-02|keep||индикатор отправки формы — с задержкой показа|../ux/06-feedback-states-motion/02-system-status-and-waiting.md §3
UX-FBK-03|replaced|SITE-PERF-05, SITE-GEO-01|скелетоны сайту не нужны: LCP — H1 и постер в исходном HTML|PLAN №13
UX-FBK-04|keep||долгая отправка — оценка и выход|../ux/06-feedback-states-motion/02-system-status-and-waiting.md §2.2
UX-FBK-05|keep|SITE-FRM-09|честный прогресс квиза|05-conversion-funnels/01-cta-and-lead-capture.md §5.3
UX-FBK-06|off||фоновых операций у сайта нет|PLAN №10
UX-FBK-07|off||оптимистичных обновлений у сайта нет|PLAN №10
UX-FBK-08|keep|SITE-FRM-11|успех отправки — одним каналом («спасибо»)|05-conversion-funnels/01-cta-and-lead-capture.md §10
UX-FBK-09|keep|SITE-PERF-08, SITE-PERF-03|баннер и виджеты не сдвигают содержимое|07-seo-geo-performance-analytics/page-gates.yaml SG-PERF-10
UX-FBK-10|modify|SITE-A11Y-01|движение и автообновление дольше 5 с (счётчики, бегущая строка, карусель) — с паузой|08-legal-trust-a11y/03-a11y-marketing-pages.md §2.1
UX-FBK-11|modify|SITE-A11Y-03|выразительное движение законно (creative); обязательно — смысл без анимации на месте (reduce)|../creative/01-creative-direction/ambition-levels.yaml CRV-AL-01
UX-FBK-12|off||длительности и кривые — движение creative; «чем чаще видят, тем короче» для разового визита не работает|аудит UX §4 п.1
UX-FBK-13|replaced|SITE-A11Y-03, CRV-AL-01|под reduce — конечные состояния, 0 байт видео, WebGL в покое (строже ux)|../creative/01-creative-direction/ambition-levels.yaml CRV-AL-01
UX-FBK-14|replaced|SITE-A11Y-01, CRV-MO-04, CRV-MO-06, CRV-AL-02, CRV-AL-10|появление — одноразовое, системой по ролям (CRV-MO-04); бесконечные фоны и пульсации — в бюджете движения уровня (CRV-MO-06); site держит паузу для движения > 5 с и стоящие вне экрана циклы|../creative/05-motion/01-motion-principles-and-access.md §2; PLAN №11; аудит UX §4 п.1
UX-FBK-15|replaced|SITE-A11Y-02, SITE-A11Y-01, SITE-BLK-07, CRV-AL-03, CRV-MO-06|блокер — вспышки > 3/с и автозвук > 3 с; немое автовидео и карусели — непрерывное движение в бюджете уровня (CRV-MO-06), с паузой и не для главного сообщения|../creative/05-motion/01-motion-principles-and-access.md §2; PLAN №11; аудит UX §4 п.1, п.14
UX-FBK-16|off||ИИ-функций с потоком вывода у маркетинговой страницы нет|PLAN №10
UX-ETH-01|modify|SITE-LEGAL-06|симметрия «дать / не дать» — баннер cookie и согласия: ЕС — B, РФ — S (позиция I)|08-legal-trust-a11y/legal-requirements.yaml LR-EU-02, LR-RU-10
UX-ETH-02|modify||на сайте — отказ от рассылки и отзыв согласия в один шаг; отмена подписки — в продукте (ux)|05-conversion-funnels/03-multi-page-funnels.md
UX-ETH-03|keep|SITE-LEGAL-01, SITE-LEGAL-03|согласия выключены, согласие ПД — отдельный элемент|08-legal-trust-a11y/legal-requirements.yaml LR-RU-01, LR-RU-02
UX-ETH-04|modify|SITE-LEGAL-06|равные кнопки баннера: ЕС — B, РФ — S; вычисленные стили подтверждать кадром (cmp_reject_equal ненадёжен)|08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §4; 02-site-types/03-live-pages-measured.md §9
UX-ETH-05|keep|SITE-PRF-14|таймер — реальная дата факта, не сбрасывается|08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §4
UX-ETH-06|keep|SITE-PRF-15|остаток — живые данные|08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §4
UX-ETH-07|keep|SITE-PRF-07, SITE-PRF-16|выдуманных отзывов, рейтингов и активности нет|08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §3, §4
UX-ETH-08|keep|SITE-PRF-09, SITE-PRF-13|полная цена в месте решения; доплаты рядом|05-conversion-funnels/02-proof-pricing-risk.md §2
UX-ETH-09|keep|SITE-CTA-09|без конфирмшейминга|08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §4
UX-ETH-10|keep|SITE-A11Y-04, SITE-LEGAL-06|условия и строка согласия — основным кеглем и контрастом|08-legal-trust-a11y/03-a11y-marketing-pages.md §4
UX-ETH-11|keep|SITE-CTA-07|отклонённое не предлагается снова|05-conversion-funnels/01-cta-and-lead-capture.md §11
UX-ETH-12|modify|SITE-CTA-07, SITE-PRE-08|лид-форма в hero — законная просьба с явным обменом; окно захвата и exit-intent по умолчанию выключены, включает заказчик по условиям F|PLAN №5; аудит UX §4 п.15
UX-ETH-13|modify|SITE-LEGAL-09|на сайте в РФ — B: «Реклама», рекламодатель, erid (38-ФЗ)|08-legal-trust-a11y/legal-requirements.yaml LR-RU-17, LR-RU-18
UX-ETH-14|modify|SITE-LEGAL-13, SITE-PRF-08|ИИ-чат называет себя ИИ (ЕС); ИИ-люди в роли клиентов и команды — запрет|08-legal-trust-a11y/legal-requirements.yaml LR-EU-11; 08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §2
UX-AIG-01|replaced|SITE-OUT-03, SITE-PRF-01|заглушки — блокер; «Нам доверяют», «10 000+», «4,9» законны со связкой fact:, проверка по связке, не регуляркой|PLAN №7; аудит UX §4 п.7
UX-AIG-02|replaced|SITE-PRF-01, SITE-PRF-05|каждое число — слот data с fact: (источник, дата, разрешение)|PLAN №7; 08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §1.2
UX-AIG-03|modify|SITE-FRM-13|на сайте — одно имя услуги и действия везде; слова клиента и жаргон — text (линтер)|../text/09-ai-generation-evaluation/copy-checklist.yaml COPY-C-05
UX-AIG-04|keep|SITE-FRM-01, SITE-CTA-13|обещанное работает: форма отправляется, призыв ведёт к действию; href="#" — AIL-44|09-ai-generation-evaluation/ai-landing-markers.yaml
UX-AIG-05|replaced|SITE-STR-01, SITE-PRE-15|у секции роль и вопрос посетителя; шаблон порядка — маркеры AIL-01, AIL-02|03-page-structure/01-narratives-and-section-order.md §3.1
UX-AIG-06|modify|SITE-BLK-08|структурная часть — три одинаковые карточки вместо продукта (AIL-07); надзаголовок над каждой секцией — text (COPY-C-18); радиусы, тени, градиенты — creative|аудит UX §4 п.8, п.11
UX-AIG-07|keep|SITE-BLK-12|содержимое вкладок, аккордеонов и FAQ — в HTML; кнопка без содержимого — блокер|04-blocks/blocks.yaml
UX-AIG-08|keep|SITE-GEO-01, CRV-AL-05|страница не пуста без JS и без WebGL|07-seo-geo-performance-analytics/head-kit.yaml hk-access-ssr
UX-AIG-09|keep|SITE-PERF-11|картинки с размерами не ломают раскладку|07-seo-geo-performance-analytics/page-gates.yaml SG-PERF-14
UX-AIG-10|keep|SITE-MOB-01|без горизонтальной прокрутки на 360|../claude-design/06-design-process/04-checks.md §3
UX-AIG-11|modify|SITE-TRK-03|между страницами сайта переживают метки источника и выбор (тариф), а не состояние приложения|05-conversion-funnels/03-multi-page-funnels.md §2.2
UX-AIG-12|modify|SITE-OUT-01|варианты сборки отбираются воротами страницы; три провала подряд — пересмотр входного контракта|09-ai-generation-evaluation/02-site-checklist.md §1.4
UX-AIG-13|replaced|SITE-OUT-07|после каждой правки — полный прогон автопроверок, регресс — откат|../claude-design/06-design-process/03-edit-loop-and-stop.md §4
UX-AIG-14|keep|SITE-OUT-09|находка = что, где, правило, доказательство, серьёзность, правка|09-ai-generation-evaluation/03-expert-review-and-judge.md
UX-TXT-01|replaced|SITE-CTA-03, COPY-R-09|подпись призыва называет результат; формулировку проверяет text|05-conversion-funnels/01-cta-and-lead-capture.md §1.3
UX-TXT-02|keep|SITE-FRM-13|одно имя действия|05-conversion-funnels/03-multi-page-funnels.md §2
UX-TXT-03|keep|SITE-FRM-06|ошибка формы: что, почему, что сделать|05-conversion-funnels/lead-forms.yaml defaults.validation
UX-TXT-04|keep||сообщения формы и 404 не обвиняют посетителя|../ux/07-ux-writing/01-principles-voice-and-tone.md §7
UX-TXT-05|keep|SITE-FRM-04|подпись поля 1–3 слова, плейсхолдер — пример|05-conversion-funnels/lead-forms.yaml defaults.layout
UX-TXT-06|modify|SITE-CTA-03|«Подробнее» как главный призыв — дефект (AIL-32); ссылки в тексте — text|05-conversion-funnels/01-cta-and-lead-capture.md §1.3
UX-TXT-08|modify|SITE-NAV-12|только поиск по сайту многостраничника|06-multipage-ia/02-navigation-linking-i18n.md §2.4
UX-TXT-10|keep|SITE-FRM-13|один объект — одно слово|05-conversion-funnels/03-multi-page-funnels.md §2
UX-TXT-11|keep|SITE-NAV-04|пункты меню отвечают на один вопрос|06-multipage-ia/02-navigation-linking-i18n.md §1.2
UX-TXT-12|replaced|COPY-C-07|длины — по слотам copy-slots.yaml text, ядро первого экрана ≤ 40 слов; правило 15/50 слов — для интерфейса|../text/09-ai-generation-evaluation/copy-checklist.yaml
UX-TXT-13|replaced|COPY-C-05|канцелярит и маркетинговую лексику ловит линтер text в профиле жанра (роль marketing у ux не описана)|аудит UX §4 п.9
UX-TXT-14|replaced|COPY-C-14|типографика — text (typography-rules.yaml); капс надзаголовков и display — законный стиль creative; AC-TXT-13 «нет капса» на сайте ложное|аудит UX §4 п.8
UX-TXT-15|keep||числа в тексте — через плюрализацию ICU|../ux/07-ux-writing/05-localization-and-i18n.md §2
UX-TXT-16|keep|SITE-STR-18|подстановки по метке — из белого списка, без склейки после предлога|03-page-structure/02-length-goal-message-match.md §3.3
UX-TXT-17|keep|SITE-PRF-09|цены одним форматом; сумма в месте решения полностью|05-conversion-funnels/02-proof-pricing-risk.md §2
UX-TXT-18|keep||инструкции не опираются на «справа» и цвет (1.3.3)|../ux/08-accessibility/01-wcag22-as-build-rules.md
UX-TXT-19|keep|SITE-A11Y-05|имя иконки = действие + объект|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-TXT-20|modify|SITE-CTA-09|на сайте — S: отказ в окне не ломает действие; словарь отказа — text|08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §4
UX-TXT-21|replaced|SITE-OUT-03, SITE-PRF-01, COPY-C-04|заглушки — блокер выдачи; числа — только с fact:|PLAN №7
UX-TXT-22|keep|SITE-FRM-06|сообщения об ошибке формы — по рубрике NN/g|../ux/05-flows-journeys/04-errors-and-recovery.md §8
UX-TXT-23|modify|SITE-STR-16|банановый тест — конвенции взаимодействия (логотип, шапка, кнопка, форма) узнаются без слов|контракт v2 §6 п.11
UX-MOB-01|keep|SITE-MOB-01|без горизонтальной прокрутки на 390 и 360 (320 — зум 400 %)|../claude-design/06-design-process/04-checks.md §3
UX-MOB-02|keep|SITE-A11Y-07|зум не запрещён|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-MOB-03|keep|SITE-A11Y-08|на таче каждая цель ≥ 44×44 зоной нажатия (видимый контрол может быть меньше); с мышью — ≥ 24×24 или зазор|../ux/08-accessibility/01-wcag22-as-build-rules.md §12.4
UX-MOB-04|modify|SITE-CTA-06|главное действие — липкий призыв снизу (≤ 72 px + safe area), меню — сверху; у ux позиция [спорно]|05-conversion-funnels/01-cta-and-lead-capture.md §2
UX-MOB-05|off||деструктивных целей у сайта нет|PLAN №10
UX-MOB-06|replaced|SITE-NAV-06, SITE-MOB-02|нижняя панель вкладок — не для сайта: кнопка «Меню» и липкий призыв|PLAN №3
UX-MOB-07|keep|SITE-MOB-09|порядок и названия секций как на десктопе|03-page-structure/03-first-screen-and-mobile.md §5.1
UX-MOB-08|keep||«Назад» закрывает окно формы и полноэкранное меню, а не уводит со страницы|../ux/09-mobile/02-mobile-navigation-and-actions.md §4
UX-MOB-09|off||списков с деталями у посадочной нет; на хабе возврат обеспечивает браузер (bfcache)|PLAN №10
UX-MOB-10|keep|SITE-BLK-07|свайп карусели и слайдера — с кнопками|04-blocks/01-blocks-catalog.md §3.1
UX-MOB-11|replaced|SITE-MOB-07, SITE-CTA-06|hero — svh или проценты, 100vh и 100dvh для hero нет; липкое — с safe area|03-page-structure/03-first-screen-and-mobile.md §2.4
UX-MOB-12|keep|SITE-CTA-06|липкий призыв скрыт при клавиатуре; поле и ошибка видны|05-conversion-funnels/01-cta-and-lead-capture.md §2
UX-MOB-13|keep|SITE-MOB-03|кегль полей ≥ 16 px|../ux/09-mobile/03-mobile-content-tables-forms-dashboards.md §3.4
UX-MOB-14|keep|SITE-FRM-04|type=tel, inputmode, autocomplete|05-conversion-funnels/lead-forms.yaml defaults
UX-MOB-15|keep||ошибки полей видны при открытой клавиатуре|../ux/09-mobile/03-mobile-content-tables-forms-dashboards.md §3
UX-MOB-16|replaced|SITE-MOB-12|тарифы и сравнение на телефоне: две колонки и переключатель, рядом ≤ 2|04-blocks/01-blocks-catalog.md §6.3
UX-MOB-17|keep||если таблица сравнения прокручивается — region с именем и фокусом|../ux/09-mobile/04-platform-conventions-and-browser-quirks.md §4.8
UX-MOB-18|keep||hover-стили — в @media (hover: hover)|../ux/09-mobile/04-platform-conventions-and-browser-quirks.md §4.12
UX-MOB-19|keep||ориентация не заблокирована|../ux/09-mobile/04-platform-conventions-and-browser-quirks.md §6.5
UX-MOB-20|keep||телефон — ссылка tel:; автоопределение выключить для ИНН, ОГРН и номеров-идентификаторов|../ux/09-mobile/04-platform-conventions-and-browser-quirks.md §4.9
UX-MOB-21|replaced|SITE-PERF-01, SITE-PERF-02, SITE-PERF-03, SITE-PERF-04|цели — профиль типа страницы и уровня; B — только «плохо»|PLAN №17; 07-seo-geo-performance-analytics/budgets.yaml
UX-MOB-22|modify|SITE-A11Y-16, SITE-A11Y-12|axe на десктопе и телефоне в двух состояниях баннера, клавиатура, зум; скринридер — перед публикацией|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-MOB-23|modify|SITE-MOB-11|встроенный браузер — для трафика из соцсетей и мессенджеров|03-page-structure/02-length-goal-message-match.md §4
UX-MOB-24|keep||обучающих оверлеев нет|../ux/09-mobile/02-mobile-navigation-and-actions.md §5
UX-CNS-03|keep|SITE-PRF-09|форматы цен и дат одинаковы|05-conversion-funnels/02-proof-pricing-risk.md §2
UX-CNS-04|modify|SITE-BLK-05|один вариант блока доказательства на странице; разнообразие блоков между секциями — норма|04-blocks/blocks.yaml conventions.vary-blocks
UX-CNS-05|keep|SITE-NAV-09, SITE-STR-16|конвенции размещения одинаковы на всех страницах|06-multipage-ia/02-navigation-linking-i18n.md §1.5
UX-CNS-06|keep|SITE-NAV-03|отклонение от конвенции — с записанной причиной (архетип шапки, x-gate-exception)|06-multipage-ia/02-navigation-linking-i18n.md §1.2
UX-CNS-10|modify|SITE-BLK-01|один блок каталога на потребность секции|04-blocks/01-blocks-catalog.md §1.1
UX-CNS-11|keep|SITE-CTA-03|одно действие — одна подпись|05-conversion-funnels/01-cta-and-lead-capture.md §1.3
UX-CNS-12|modify|SITE-NAV-09|единые шапка, подвал и раскладка формы на всех страницах сайта|06-multipage-ia/02-navigation-linking-i18n.md §1.5
UX-CNS-14|modify|SITE-FRM-13|на сайте — одно имя услуги и действия; id — словарь vocabulary.yaml; слова — text|02-site-types/vocabulary.yaml
UX-CNS-18|modify|SITE-BLK-01, SITE-PRF-01|заземление сайта — блоки из каталога и данные из фактов|04-blocks/blocks.yaml conventions.no-fact-no-block
UX-CNS-20|modify|SITE-PRE-15|инвентарь страничных композиций — макроструктуры и блоки; эталон палитры и типографики — creative (marketing-tokens)|03-page-structure/01-narratives-and-section-order.md §4
UX-CNS-21|keep|SITE-MOB-10|перестроение на границах 60/40 rem, проверка произвольных ширин|04-blocks/blocks.yaml conventions.breakpoints
UX-CNS-22|keep|SITE-STR-16|логотип слева, навигация сверху, формы предсказуемы|контракт v2 §6 п.11
UX-CNS-23|modify|SITE-STR-16|конвенции взаимодействия — как в ux; уникальность — в сюжете и подаче (creative), различия ради выразительности законны в подаче|PLAN №8; аудит UX §4 п.12
UX-CNS-25|modify|SITE-CTA-02, SITE-BLK-05|повтор призыва — норма; повтор секции с тем же содержимым — дефект|PLAN №1
UX-CNS-26|replaced|SITE-OUT-07|полный прогон после каждой правки|../claude-design/06-design-process/03-edit-loop-and-stop.md §4
UX-CNS-27|modify|SITE-OUT-01, SITE-OUT-07|дрейф ловят ворота и полный прогон на каждой итерации|07-seo-geo-performance-analytics/page-gates.yaml
UX-CNS-29|keep|SITE-OUT-09|прохождение ворот ≠ качество: экспертный проход и рубрика|09-ai-generation-evaluation/03-expert-review-and-judge.md
UX-CLI-02|replaced|SITE-NAV-06|навигация видима на десктопе, иконки с подписями|06-multipage-ia/02-navigation-linking-i18n.md §1.3
UX-CLI-08|replaced|SITE-PRF-13, SITE-FRM-17|сумма, период и дата списания — у кнопки; пробный период — до ввода карты|05-conversion-funnels/02-proof-pricing-risk.md §2.7
UX-CLI-11|replaced|SITE-FRM-07|капчи-головоломки нет|05-conversion-funnels/01-cta-and-lead-capture.md §8
UX-CLI-13|replaced|SITE-FRM-11|«спасибо» с номером обращения|05-conversion-funnels/01-cta-and-lead-capture.md §10
UX-CLI-15|modify|SITE-NAV-08, SITE-NAV-09|контакты — в подвале каждой страницы (3.2.6); номер обращения — на «спасибо»|06-multipage-ia/02-navigation-linking-i18n.md §1.4
UX-CLI-16|replaced|SITE-LEGAL-01, SITE-LEGAL-06|согласие ПД отдельное, без предотметки; баннер с равными кнопками|08-legal-trust-a11y/legal-requirements.yaml
UX-CLI-17|replaced|SITE-PRF-14, SITE-PRF-15|таймеры и остатки — только с реальными данными|08-legal-trust-a11y/02-proof-authenticity-dark-patterns.md §4
UX-CLI-18|modify|SITE-LEGAL-16, SITE-A11Y-16|ЕС и продажа потребителю: заявление о доступности (EAA)|08-legal-trust-a11y/legal-requirements.yaml LR-EU-10
UX-CLI-19|replaced|SITE-MOB-01, SITE-FRM-04|форма проходится на 390 и 360; подписи над полями|03-page-structure/03-first-screen-and-mobile.md
UX-AIF-15|modify|SITE-LEGAL-13|ИИ-чат на сайте называет себя ИИ (ЕС)|08-legal-trust-a11y/legal-requirements.yaml LR-EU-11
UX-AIF-16|modify|SITE-LEGAL-13|чат, собирающий телефон: согласие и политика до поля|08-legal-trust-a11y/legal-requirements.yaml LR-RU-23
UX-PRC-01|replaced|SITE-PRE-01|бриф approved с подписью; допущения и открытые вопросы — в брифе|01-foundations/03-site-brief.md §4
UX-PRC-07|replaced|SITE-PRE-10, SITE-PRE-11|карта сайта и планы страниц; у страницы одно целевое действие|06-multipage-ia/01-sitemaps-templates-content-model.md
UX-PRC-09|modify|SITE-PRE-15|инвентарь блоков — blocks.yaml; контейнер действия — слот action|04-blocks/01-blocks-catalog.md
UX-PRC-11|modify|SITE-A11Y-12, SITE-BLK-02|лендмарки, порядок Tab и мобильная трансформация — в плане и блоках|04-blocks/blocks.yaml conventions.landmarks
UX-PRC-12|replaced|SITE-PRE-25|бриф подачи — treatment creative по уровню амбиций|../creative/09-ai-execution-evaluation/treatment.schema.json
UX-PRC-13|replaced|SITE-PRE-26|вход холста собран проекцией из брифа и планов (x-canvas-map), а не написан заново|../../references/claude-design.md §6
UX-PRC-14|keep||журнал решений «проблема → влияние → альтернатива» (x-gate-exception, decisions)|10-playbooks-contracts/01-procedure-brief-to-pages.md
UX-PRC-15|modify|SITE-OUT-01, SITE-OUT-08, SITE-STR-02|автопроверки плана и страницы, маркеры; форма страницы не повторяет прошлую страницу проекта|09-ai-generation-evaluation/ai-landing-markers.yaml
UX-OUT-01|keep|SITE-GEO-01|сборка проходит; главная страница непуста и без JS|07-seo-geo-performance-analytics/head-kit.yaml hk-access-ssr
UX-OUT-02|keep|SITE-OUT-06|ограничения проверены своими инструментами, а не заявлены|../claude-design/06-design-process/04-checks.md §2
UX-OUT-03|modify|SITE-A11Y-16|axe: десктоп и телефон × первый визит (баннер) и после выбора; тема обычно одна|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-OUT-04|modify|SITE-OUT-01|ворота доступности сайта — SG-A11Y (B: контраст, имена, label, viewport; S: target-size, alt, frame-title, lang), а не «0 Serious»|07-seo-geo-performance-analytics/page-gates.yaml SG-A11Y-01, SG-A11Y-02
UX-OUT-05|modify|SITE-FRM-01, SITE-TRK-01|сценарий сайта — «визит → форма → спасибо» и цель по успеху сервера|05-conversion-funnels/01-cta-and-lead-capture.md §9.3
UX-OUT-06|off||состояния между маршрутами приложения у сайта нет; метки источника — SITE-TRK-03|PLAN №10
UX-OUT-07|modify|SITE-A11Y-12, SITE-A11Y-16|ручные проходы: клавиатура, зум, телефон; скринридер — перед публикацией|08-legal-trust-a11y/03-a11y-marketing-pages.md §8
UX-OUT-08|keep|SITE-A11Y-11, SITE-FRM-05, SITE-FRM-07, SITE-NAV-09|2.4.11, 2.5.7, 3.2.6, 3.3.7, 3.3.8 проверяются руками|../ux/08-accessibility/04-inclusive-design-and-testing.md §5.3
UX-OUT-09|replaced|SITE-PERF-01, SITE-PERF-03, SITE-PERF-04|CWV — цели профиля типа и уровня; поле p75 — в живой фазе (SG-PERF-07)|PLAN №17
UX-OUT-10|modify|SITE-OUT-01|варианты — отбором по воротам страницы|09-ai-generation-evaluation/02-site-checklist.md §1.4
UX-OUT-11|replaced|SITE-OUT-10|судья по site-rubric.json: 3 прогона — находки и второе мнение, 5 — сортировка трёх и более вариантов, оба порядка; вердикт не решает — решает человек|../common/judge.md §5; 09-ai-generation-evaluation/03-expert-review-and-judge.md
UX-OUT-12|keep|SITE-OUT-09|ноль находок — неудачный прогон|../ux/12-evaluation-checklists/01-expert-review-protocols.md §10.1
UX-OUT-13|modify|SITE-OUT-12|решения вкуса, фактов, прав и тона — заказчику одним блоком; уместность — экспертный проход и рубрика|../claude-design/06-design-process/04-checks.md §8
UX-OUT-14|keep||конфликты правил записаны|../ux/12-evaluation-checklists/01-expert-review-protocols.md §10.3
"""


def short(text, n=100):
    t = re.sub(r'\*\*|`', '', text)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(' ', 1)[0].rstrip(',;:—- ')
    return cut + '…'


def parse_decisions():
    out, problems = {}, []
    for ln, line in enumerate(DECISIONS.strip().split('\n'), 1):
        parts = line.split('|')
        if len(parts) != 5:
            problems.append(f'строка решений {ln}: {len(parts)} полей вместо 5: {line[:60]}')
            continue
        uid, act, rep, why, src = (p.strip() for p in parts)
        if uid in out:
            problems.append(f'решение для {uid} повторено')
        out[uid] = (act, rep, why, src)
    return out, problems


def known_ids():
    site = {i['id'] for i in (yaml.safe_load(io.open(SITE_YAML, encoding='utf-8')).get('items') or [])}
    copy = set()
    for p in COPY_YAMLS:
        t = io.open(p, encoding='utf-8').read()
        copy |= set(re.findall(r'\bCOPY-[A-Z]-\d{2}\b', t))
    crv = set(CRV_DEF_RX.findall(io.open(CRV_YAML, encoding='utf-8').read()))
    for dirpath, dirs, files in os.walk(CRV_DIR):   # чек-листы разделов creative: строки «- CRV-XX-NN …»
        dirs[:] = [d for d in dirs if d != '99-raw']
        for f in files:
            if f.endswith('.md'):
                crv |= set(CRV_DEF_RX.findall(io.open(os.path.join(dirpath, f), encoding='utf-8').read()))
    return site, copy, crv


def source_paths(source):
    """Пути-основания колонки source: первое слово каждой части «;», похожее на путь (от kb/site/)."""
    out = []
    for part in source.split(';'):
        word = part.strip().split(' ')[0] if part.strip() else ''
        if word and PATH_RX.match(word):
            out.append(word)
    return out


def build(ux=None):
    ux = ux if ux is not None else yaml.safe_load(io.open(UX_YAML, encoding='utf-8'))
    items = ux['items']
    dec, problems = parse_decisions()
    ux_ids = {i['id'] for i in items}
    for uid in dec:
        if uid not in ux_ids:
            problems.append(f'решение для несуществующего пункта {uid}')
    rows = []
    for i in items:
        blk = i['block']
        act, rep, why, src = dec.get(i['id'], BLOCK_DEFAULT[blk])
        rows.append({'ux_id': i['id'], 'block': blk, 'ux_text_short': short(i['text']), 'site_action': act,
                     'site_replacement': rep, 'reason': why, 'source': src,
                     '_explicit': i['id'] in dec, '_sev': i['severity'], '_method': ','.join(i['check_method'])})
    return rows, problems, ux


def validate(rows, problems, ux, known=None):
    errors = list(problems)
    site, copy_ids, crv = known if known is not None else known_ids()
    want = ux.get('items_count')
    if want is not None and len(rows) != want:
        errors.append(f'строк {len(rows)}, а в чек-листе ux items_count {want}')
    if len(rows) != len(ux.get('items') or []):
        errors.append(f"строк {len(rows)}, пунктов в чек-листе ux {len(ux.get('items') or [])}")
    for r in rows:
        if r['site_action'] not in ACTIONS:
            errors.append(f"{r['ux_id']}: действие {r['site_action']!r}")
        if r['site_action'] == 'replaced' and not r['site_replacement']:
            errors.append(f"{r['ux_id']}: replaced без замены")
        for x in ID_RX.findall(r['site_replacement']):
            ok = (x in site) if x.startswith('SITE-') else (x in copy_ids) if x.startswith('COPY-') else (x in crv)
            if not ok:
                errors.append(f"{r['ux_id']}: {x} нет в каталоге владельца")
        rest = ID_RX.sub('', r['site_replacement']).replace(',', '').strip()
        if rest:
            errors.append(f"{r['ux_id']}: в замене не только id: {rest!r}")
        for c in COLS:
            if '\t' in r[c] or '\n' in r[c]:
                errors.append(f"{r['ux_id']}: табуляция или перевод строки в {c}")
        for pth in source_paths(r['source']):
            if not os.path.exists(os.path.normpath(os.path.join(ROOT, pth))):
                errors.append(f"{r['ux_id']}: основание {pth} не найдено (путь — от kb/site/)")
    by = {r['ux_id']: r for r in rows}
    for uid in AUDIT_FLAGGED:
        if by.get(uid, {}).get('site_action') == 'keep':
            errors.append(f'{uid}: назван аудитом UX, но оставлен keep')
    return errors


def reconcile(rows, old_tsv, version, reviewed=None):
    """Сверка с версией чек-листа ux → (строки отчёта, сверено ли). Новые, снятые и изменённые пункты — против профиля
    на диске (колонки block и ux_text_short)."""
    reviewed = CHECKLIST_REVIEWED if reviewed is None else reviewed
    if version == reviewed:
        return [], True
    old = {}
    for line in (old_tsv or '').splitlines()[1:]:
        cells = line.split('\t')
        if len(cells) == len(COLS):
            old[cells[0]] = dict(zip(COLS, cells))
    new = {r['ux_id']: r for r in rows}
    out = [f'чек-лист ux: решения профиля сверены с версией {reviewed or "—"}, в базе — версия {version or "—"}']
    added = [u for u in new if u not in old]
    removed = [u for u in old if u not in new]
    changed = [u for u in new if u in old and (old[u]['block'], old[u]['ux_text_short']) != (new[u]['block'], new[u]['ux_text_short'])]
    for u in added:
        r = new[u]
        how = 'точечное решение' if r['_explicit'] else f"умолчание блока {r['block']}: {r['site_action']}"
        out.append(f'  новый пункт {u} — {how}; подтвердить или записать точечное решение')
    for u in removed:
        out.append(f'  снятый пункт {u} — строка уходит из профиля')
    for u in changed:
        r = new[u]
        what = 'точечное решение — пересмотреть' if r['_explicit'] else f"умолчание блока {r['block']} — подтвердить"
        out.append(f"  изменён пункт {u}: «{old[u]['ux_text_short']}» → «{r['ux_text_short']}» ({what})")
    if not (added or removed or changed):
        out.append('  пункты профиля не изменились (правка — вне пунктов или дальше первых 100 знаков формулировки): сверить')
    out.append(f'  после сверки — CHECKLIST_REVIEWED = {version!r} в scripts/site/build_profile.py и пересборка профиля')
    return out, False


def render_tsv(rows):
    out = ['\t'.join(COLS)]
    for r in rows:
        out.append('\t'.join(r[c] for c in COLS))
    return '\n'.join(out) + '\n'


def ac_profile(rows):
    """AC-* (ux 03) наследуют действие пункта UX, который закрывают (колонка «Закрывает»; первый id — главный)."""
    by = {r['ux_id']: r for r in rows}
    out = ['ac_id\tcloses\tsite_action\tsite_replacement\tline']
    n = collections.Counter()
    for ln, line in enumerate(io.open(UX_AC_MD, encoding='utf-8'), 1):
        if not line.startswith('| AC-'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        closes = re.findall(r'UX-[A-Z0-9]{3}-\d{2}', cells[-1])
        if not closes:
            closes = re.findall(r'UX-[A-Z0-9]{3}-\d{2}', line)
        if not closes:
            act, rep = 'n/a', ''
        else:
            main = by.get(closes[0])
            act, rep = (main['site_action'], main['site_replacement']) if main else ('n/a', '')
        n[act] += 1
        out.append(f'{cells[0]}\t{",".join(closes)}\t{act}\t{rep}\t{ln}')
    return '\n'.join(out) + '\n', n


def summary_md(rows, n_ac):
    blocks = list(collections.OrderedDict((r['block'], 1) for r in rows))
    t = ['| Блок | Пунктов | keep | modify | off | replaced | точечных решений |', '|---|---|---|---|---|---|---|']
    tot = collections.Counter()
    for b in blocks:
        rs = [r for r in rows if r['block'] == b]
        c = collections.Counter(r['site_action'] for r in rs)
        ex = sum(r['_explicit'] for r in rs)
        tot.update(c)
        tot['n'] += len(rs)
        tot['ex'] += ex
        t.append(f"| {b} | {len(rs)} | {c['keep']} | {c['modify']} | {c['off']} | {c['replaced']} | {ex} |")
    t.append(f"| **итого** | **{tot['n']}** | **{tot['keep']}** | **{tot['modify']}** | **{tot['off']}** | **{tot['replaced']}** | {tot['ex']} |")
    sev = collections.Counter((r['_sev'], r['site_action']) for r in rows)
    t.append('')
    t.append('Серьёзность ux × действие: ' + '; '.join(f"{s}: " + ', '.join(f"{a} {sev[(s, a)]}" for a in ACTIONS)
                                                     for s in 'BSD'))
    t.append('')
    t.append('AC-* ux 03 по наследству от закрываемого UX-пункта: ' + ', '.join(f'{k} {v}' for k, v in sorted(n_ac.items())))
    return '\n'.join(t) + '\n'


def selftest():
    """Сверка версии чек-листа, число строк, замены и основания — на чек-листе базы и подложенных строках; без записи."""
    import copy
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(('PASS ' if cond else 'FAIL ') + name)

    ux = yaml.safe_load(io.open(UX_YAML, encoding='utf-8'))
    rows, problems, _ = build(ux)
    errors = validate(rows, problems, ux)
    check(f'чек-лист базы: строк {len(rows)}, ошибок {len(errors)}' + (f' (первая: {errors[0]})' if errors else ''),
          not errors and len(rows) == len(ux['items']))
    tsv = render_tsv(rows)
    notes, same = reconcile(rows, tsv, 'v1', reviewed='v1')
    check('та же версия чек-листа — сверено', same and not notes)
    notes, same = reconcile(rows, tsv, 'v2', reviewed='v1')
    check('новая версия без изменений пунктов — версию записать после сверки', not same and any('не изменились' in n for n in notes))
    ux2 = copy.deepcopy(ux)
    items = ux2['items']
    next(i for i in items if i['id'] == 'UX-FBK-14')['text'] = 'Нет появления при прокрутке — изменённая формулировка пункта'
    gone = items.pop(next(k for k, i in enumerate(items) if i['id'] == 'UX-OUT-14'))
    items.append(dict(gone, id='UX-OUT-99', text='Новый пункт ворот выдачи'))
    rows2, problems2, _ = build(ux2)
    text = '\n'.join(reconcile(rows2, tsv, 'v2', reviewed='v1')[0])
    check('новый пункт — умолчание блока, подтвердить', 'новый пункт UX-OUT-99 — умолчание блока OUT: keep' in text)
    check('изменённый пункт с точечным решением — пересмотреть', 'изменён пункт UX-FBK-14' in text and 'пересмотреть' in text)
    check('снятый пункт назван', 'снятый пункт UX-OUT-14' in text)
    check('решение для снятого пункта — ошибка', any('UX-OUT-14' in p for p in problems2))
    check('число строк — из items_count чек-листа', any('items_count' in e for e in validate(rows2, [], dict(ux2, items_count=len(items) + 1))))
    known = ({'SITE-OUT-10'}, {'COPY-C-05'}, {'CRV-MO-04'})
    fake = [dict(rows[0], ux_id='UX-T-01', site_action='replaced', site_replacement='', source='PLAN №1'),
            dict(rows[0], ux_id='UX-T-02', site_action='replaced', site_replacement='CRV-MO-99', source='PLAN №1'),
            dict(rows[0], ux_id='UX-T-03', site_action='keep', site_replacement='', source='99-raw/tools/nope.py'),
            dict(rows[0], ux_id='UX-T-04', site_action='modify', site_replacement='CRV-MO-04',
                 source='../../scripts/site/ia_probe.py; PLAN №3')]
    errs = validate(fake, [], {'items': fake}, known=known)
    check('replaced без замены — ошибка', any(e.startswith('UX-T-01: replaced без замены') for e in errs))
    check('CRV-* вне определений creative — ошибка', any(e.startswith('UX-T-02: CRV-MO-99') for e in errs))
    check('основание в пустоту — ошибка', any(e.startswith('UX-T-03') and 'nope.py' in e for e in errs))
    check('основание — утилита скилла от kb/site/ — проходит', not any(e.startswith('UX-T-04') for e in errs))
    crv = known_ids()[2]
    check(f'определения CRV creative: {len(crv)} id, среди них CRV-MO-04, CRV-MO-06', {'CRV-AL-01', 'CRV-MO-04', 'CRV-MO-06'} <= crv)
    print('SELFTEST', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--check', action='store_true',
                    help='сверить профиль на диске с решениями и версией чек-листа ux; ничего не пишет (код 1 — расходится)')
    ap.add_argument('--selftest', action='store_true', help='самопроверка без записи')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    rows, problems, ux = build()
    errors = validate(rows, problems, ux)
    old = io.open(OUT_TSV, encoding='utf-8').read() if os.path.exists(OUT_TSV) else ''
    notes, reviewed = reconcile(rows, old, str(ux.get('source_sha256_16') or ''))
    tsv = render_tsv(rows)
    if a.check:
        same = old == tsv
        print('TSV совпадает с решениями' if same else 'TSV УСТАРЕЛ: пересобрать (build_profile.py без ключей)')
        for line in notes:
            print(line)
        for e in errors:
            print('ОШИБКА', e)
        return 0 if same and reviewed and not errors else 1
    for line in notes:
        print(line)
    for e in errors:
        print('ОШИБКА', e)
    if errors or not reviewed:
        return 1
    ac, n_ac = ac_profile(rows)
    summ = summary_md(rows, n_ac)
    out_sum = kbpaths.out('site', 'build_profile') / 'summary.md'
    io.open(OUT_TSV, 'w', encoding='utf-8').write(tsv)
    io.open(OUT_AC, 'w', encoding='utf-8').write(ac)
    out_sum.write_text(summ, encoding='utf-8')
    print(summ)
    print(f'записано: {os.path.relpath(OUT_TSV, ROOT)} ({len(rows)} строк), {os.path.relpath(OUT_AC, ROOT)}, {out_sum}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
