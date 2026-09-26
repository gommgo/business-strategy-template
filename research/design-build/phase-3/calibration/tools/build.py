#!/usr/bin/env python3
"""Сборка калибровочного набора: кадры WebP, index.yaml, contact-sheet.html.

Один источник правды — таблица FRAMES ниже. Скрипт:
  1) берёт исходники из замороженной базы (только чтение), сверяет sha256 с freeze/manifest.tsv.gz;
  2) режет листы (crop) и кодирует WebP без видимой потери (lossless для экранов с текстом и тонких
     различий тона, lossy q92–94 для рендеров, фото и JPEG-исходников; готовый WebP копируется как есть);
  3) пишет index.yaml и contact-sheet.html рядом с папкой frames/.

Запуск (из любого места):
  python3 tools/build.py --ui-ref <папка с рендерами tools/render_ui_ref.py>

Кадры № 13–15 — свой рендер эталонных HTML ui (Playwright, 1440×900): папка с PNG передаётся аргументом,
потому что браузер запускается отдельно (память ≥ 3 ГБ, один браузер, общий замок .locks/browser.lock).
"""
import argparse
import gzip
import hashlib
import html
import re
import io
import json
import pathlib
import shutil
import sys

import yaml
from PIL import Image

ROOT = pathlib.Path('/home/mm/Документы/app-design')
CAL = ROOT / '_skill-build/phase-3/calibration'
FRAMES_DIR = CAL / 'frames'
MANIFEST = ROOT / '_skill-build/freeze/manifest.tsv.gz'

CR = 'creative-research/'
UI = 'ui-research/'
AM = 'ai-media-research/99-raw/phase5/runs/'
BL = 'blender-research/'

# mode: q92 / q94 — WebP с потерями (method 6); lossless — WebP без потерь; copy — готовый WebP без перекодирования.
FRAMES = [
    # ------------------------------------------------------------------ creative
    dict(
        id='01', slug='zveno-v1-flat-light', pair='cr-zveno-light', base='creative', kind='defect', level='L2',
        src=[CR + '99-raw/experiments/J/04-light-pass/out/f-before/hero.png'], mode='q92',
        illustrates='L2-сцена «Звено» кодом до светового прохода: плоский «каталожный» свет — рука висит без пола и '
                    'контактной тени, крышки суставов — плоские чёрные диски, металл без отражений.',
        assessment='сила: один судья (мнение). Агент J2 по рубрике K: craft 3 (после прохода — 4). Сцена v1 проходила '
                   'ворота на десктопе (motion_check 0.1.2, прогон K2: B 0 / S 0 / D 0) — это брак света и материала, '
                   'а не годности; отдельный брак её страницы на телефоне — № 03.',
        look_at='Основание без тени — объект «висит»; крышки — ровные чёрные круги без профиля и блика; труба матовая, '
                'без отражений студии. Сравнить с № 02 той же камеры.',
        rubric=['kb/creative/09-ai-execution-evaluation/04-effectiveness-rubric.md §3.3 (craft), §3.8 (проход по уровню)',
                'kb/creative/10-recipes/03-product-launch-l2.md §9.1 (световой проход кодом)'],
        provenance='свой рендер: three.js 0.186.1, сцена v1 агента J, Chromium 153 (ANGLE), 960×600',
        notes='«Уровень ниже», а не поломка: сцена v1 проходила ворота на десктопе. В паре с № 02 — случай, где «богаче» (свет, отражения, '
              'пол) действительно лучше: судья не штрафует богатство, если это свет и материал, а не декор.'),
    dict(
        id='02', slug='zveno-v2-studio-light', pair='cr-zveno-light', base='creative', kind='level', level='L2',
        src=[CR + '99-raw/experiments/J/04-light-pass/out/f-after/hero.png'], mode='q92',
        illustrates='Та же сцена после светового прохода кодом: своя студия PMREM, пол-циклорама с мягкой тенью, лак на '
                    'белом, сатин алюминия, тон Khronos PBR Neutral.',
        assessment='сила: ворота + метрика + один судья. motion_check 0.1.3 L2: B 0 / S 0 / D 0; белый L50 221, L95 247, '
                   'R−B 2,8 (white_check); craft 4 «уверенный предметный рендер» — один судья J2. В слепой паре '
                   'blender `z-v2-a` эта база v2 проиграла коду v3 (№ 29).',
        look_at='Контактная тень и пол — объект стоит; длинные блики софтбоксов на лаке и трубе; белый нейтральный, '
                'не бежевый; крышки с точёным профилем.',
        rubric=['kb/creative/09-ai-execution-evaluation/04-effectiveness-rubric.md §3.3, §3.8',
                'kb/creative/10-recipes/03-product-launch-l2.md §9.1'],
        provenance='свой рендер: three.js 0.186.1, сцена v2 агента J2, Chromium 153 (ANGLE), 960×600',
        notes='Ступень лестницы одного предмета: v1 (№ 01) < v2 (№ 02) < код v3 (№ 29) < Cycles (№ 28); гибрид (№ 30) < код.'),
    dict(
        id='03', slug='zveno-mob-h1-on-robot', pair='cr-zveno-mob', base='creative', kind='defect', level='L2',
        src=[CR + '99-raw/experiments/J/04-light-pass/gates-l2-before-mob/shot_mob.jpg'], mode='q94',
        illustrates='H1 первого экрана L2 на телефоне лежит на белых корпусах 3D-руки.',
        assessment='сила: ворота. motion_check 0.1.3: FAIL S EG-A11Y-27 — контраст над живым фоном h1 1,0:1 (порог 3,0), '
                   'лид 4,29:1 (порог 4,5). На листе автора читалось как «текст на роботе» и пропускалось глазом.',
        look_at='Слова «которого», «собирают», «минут» — белые буквы на белом пластике; лид лежит на основании руки.',
        rubric=['kb/creative/09-ai-execution-evaluation/effect-gates.yaml EG-A11Y-27',
                'kb/creative/09-ai-execution-evaluation/03-verification-loop-and-gates.md'],
        provenance='свой рендер страницы: кадр ворот motion_check (режим телефона), Chromium 153, 480×977',
        notes='Брак не виден на десктопе и в листе J; ловится только замером по кадрам (перцентиль яркости под строками).'),
    dict(
        id='04', slug='zveno-mob-scrim', pair='cr-zveno-mob', base='creative', kind='level', level='L2',
        src=[CR + '99-raw/experiments/J/04-light-pass/gates-l2/shot_mob.jpg'], mode='q94',
        illustrates='Тот же экран после правки: затемнение `.hero::after` снизу (22 % → 0,82–0,9) — рука уходит в тень, '
                    'текст читается.',
        assessment='сила: ворота. EG-A11Y-27 PASS — h1 10,3:1, лид 10,1:1; L2 B 0 / S 0 / D 0 (два прогона).',
        look_at='H1 и лид на затемнённой части; рука видна сверху, основание утоплено в градиент.',
        rubric=['kb/creative/09-ai-execution-evaluation/effect-gates.yaml EG-A11Y-27',
                'kb/creative/10-recipes/03-product-launch-l2.md (текст над 3D на телефоне — затемнение и --contrast)'],
        provenance='свой рендер страницы: кадр ворот motion_check (режим телефона), Chromium 153, 480×977',
        notes='Правка — одна строка CSS; в паре с № 03 — «до → после».'),
    dict(
        id='05', slug='sdano-l0-svg-plan', pair='sdano-first', base='creative', kind='level', level='L0',
        src=[CR + '99-raw/experiments/J/01-l0-sdano/shots/desk_first.jpg'], mode='q94',
        illustrates='L0 лидогенерации «Сдано»: H1 = LCP, векторный план с отметками дефектов и выдержкой из акта, цена, '
                    'один призыв.',
        assessment='сила: ворота + голос вслепую. motion_check L0 0/0/0; marketing_audit S 7 → 3 → 0; вес 71 КБ, F83 h1 '
                   '18,4:1. В испытании blender вслепую проиграл изометрии Cycles (№ 31) все 4 пары — годный L0, не лучший.',
        look_at='Иерархия H1 → лид → цена → призыв; план векторный и читается, номера отметок совпадают со списком акта; '
                'декора ради декора нет.',
        rubric=['kb/creative/09-ai-execution-evaluation/04-effectiveness-rubric.md §3.6 (clarity), §3.8',
                'kb/creative/10-recipes/01-lead-services-l0.md'],
        provenance='свой рендер страницы: пример рецепта 01 (creative 10-recipes/examples/l0-sdano), Chromium 153, 1440×900',
        notes='Та же страница — дорога A «Сдано» в blender 15-showcase.'),
    dict(
        id='06', slug='sverka-l1-first-screen', pair=None, base='creative', kind='level', level='L1',
        src=[CR + '99-raw/experiments/J/03-l1-sverka/shots/desk_first.jpg'], mode='q94',
        illustrates='Первый экран L1 SaaS «Сверка»: антиква H1, лид с числом, один призыв с условием, спокойный фон; '
                    'продукт показан ниже sticky-сценой (0 КБ JS).',
        assessment='сила: ворота. motion_check L1 0/0/0 (0.1.3); marketing_audit 0 B, 0 S; F83 h1 15,6:1.',
        look_at='Одна мысль на экран; конкретика в лиде («три-пять строк вместо трёхсот»); призыв с условием «Без карты». '
                'Иллюстрации нет сознательно — продукт показан сценой ниже.',
        rubric=['kb/creative/09-ai-execution-evaluation/04-effectiveness-rubric.md §3.2 (concept), §3.6, §3.8',
                'kb/creative/10-recipes/02-saas-l1.md'],
        provenance='свой рендер страницы: пример рецепта 02 (l1-sverka), Chromium 153, 1440×900',
        notes='Лист сцены прокрутки (кандидат № 10) не взят: в первой клетке наложен кроп `first_bottom.jpg` — артефакт '
              'склейки листа, а не страницы.'),
    dict(
        id='07', slug='holo-thin-film-ai-rainbow', pair='cr-holo', base='creative', kind='defect', level='L1',
        src=[CR + '99-raw/experiments/F/14-holo-look/before-after-desk.jpg'], crop=(0, 0, 720, 1386), mode='q94',
        illustrates='Первая модель голо-шейдера (тонкая плёнка + френель): тусклые размытые пятна спектра на тёмном — '
                    '«радуга ИИ»; окно тонов марки — плоский бирюзовый градиент; CSS-фольга — оранжевые полосы.',
        assessment='сила: мнение (глазами агента F2, пары «до → после»); показ людям не проверен. Клише реестра: '
                   'mesh-gradient-bg, iridescent-holo (группа ai-saas-2024).',
        look_at='Три ряда сверху вниз: полный спектр, окно марки, CSS-фольга. Перелив не читается материалом: нет узкой '
                'яркой полосы и структуры — фон «плывёт» пятнами.',
        rubric=['kb/creative/08-uniqueness-anti-slop/cliche-registry.yaml (mesh-gradient-bg, iridescent-holo)',
                'kb/creative/06-effects-catalog/01-effects-catalog.md §8.4'],
        provenance='свой рендер: страница лаборатории эффектов (WebGL2 и CSS), Chromium; лист F2',
        notes='Вырезка левой колонки листа 1452×1386 (x 0–720).'),
    dict(
        id='08', slug='holo-diffraction-grating', pair='cr-holo', base='creative', kind='level', level='L1',
        src=[CR + '99-raw/experiments/F/14-holo-look/before-after-desk.jpg'], crop=(732, 0, 1452, 1386), mode='q94',
        illustrates='Модель дифракционной решётки: узкая яркая полоса блика со штрихами идёт за углом зрения, «мозаика» '
                    'ориентации, тёмная основа; окно марки — «золотая плёнка»; CSS-фольга той же конструкции.',
        assessment='сила: метрика + мнение. Худший контраст из 7 положений полосы ≥ 4,5:1 (H1 ≥ 9,6, лид ≥ 9,4, '
                   'contrast.py); кадр 0,58 мс против 1,74; движение в покое 0 %/с. Вид — оценка F2.',
        look_at='Полоса блика вне текстовой колонки, под текстом скрим; спектр по порядку в узкой полосе, а не пятнами; '
                'ряд 2 — цвета марки вместо радуги.',
        rubric=['kb/creative/06-effects-catalog/01-effects-catalog.md §8.4',
                'kb/creative/09-ai-execution-evaluation/effect-gates.yaml EG-A11Y-23, EG-A11Y-27'],
        provenance='свой рендер: страница лаборатории эффектов (WebGL2 и CSS), Chromium; лист F2',
        notes='Вырезка правой колонки (x 732–1452). Полный спектр (ряд 1) уместен лишь потому, что продукт — буквально '
              'голограмма; по умолчанию — окно тонов марки (ряд 2).'),
    # ------------------------------------------------------------------ ui
    dict(
        id='09', slug='ui-orders-default-look', pair='ui-orders', base='ui', kind='defect', level='n/a',
        src=[UI + '99-raw/cache/screens/gen-a1-orders_1440x900.png'], mode='lossless',
        illustrates='«Дефолтный вид» стека в админке: эмодзи вместо иконок, центрированная шапка-«хиро», три равные '
                    'карточки с тенью, градиент на логотипе и кнопке.',
        assessment='сила: метрика (рубрикой не оценён). Проба маркеров: градиентов 10, эмодзи-узлов 10, карточек с тенью '
                   '4 из 4, трёхколоночный грид; measure_ui: кнопка 36 px (практика — 32).',
        look_at='«✨ Новый заказ» переносится в две строки; аватары «О«» и «А«» — инициалы из кавычек; суммы прижаты '
                'влево; заголовок по центру над таблицей; эмодзи в навигации.',
        rubric=['kb/ui/13-evaluation-checklists/02-rubrics-and-vlm-critic.md §1.8 (плотность), §1.9 (различимость и антислоп)',
                'kb/ui/05-layout-grid/06-ai-errors-and-checks.md §2 C1 (три одинаковые карточки), D1 (шапка-«хиро» в админке)',
                'kb/ui/12-ai-generated-ui/02-codegen-tools-and-default-look.md §5.3 (маркеры «центроида»)'],
        provenance='свой рендер: HTML написан агентом H по документированным дефолтам стека (условие A), не генератором; '
                   'Chromium (measure_ui), 1440×900',
        notes='«Богаче» и хуже. Условие A эксперимента H показывает вид «дефолта», а не поведение моделей.'),
    dict(
        id='10', slug='ui-orders-preset-a', pair='ui-orders', base='ui', kind='level', level='n/a',
        src=[UI + '99-raw/cache/screens/gen-b1-orders_1440x900.png'], mode='lossless',
        illustrates='Те же данные по карточке стиля (пресет A «плотная админка»): плотная таблица, суммы вправо, бейджи '
                    'статусов, крошки, 0 теней, 0 градиентов, кнопка 32.',
        assessment='сила: метрика (рубрикой не оценён). Градиентов 0, эмодзи 0, карточек с тенью 0 из 4; measure_ui: база '
                   '14, 4 кегля, радиус 6, кнопка 32.',
        look_at='Плотность под задачу, числа вправо, первичное действие справа вверху. Мелкий брак: активен пункт «Обзор», '
                'а открыт список заказов — судья должен его назвать, уровень это не отменяет.',
        rubric=['kb/ui/14-recipes/11-presets.md пресет A (A.7 проверочные числа)',
                'kb/ui/13-evaluation-checklists/02-rubrics-and-vlm-critic.md §1'],
        provenance='свой рендер: HTML агента H по карточке стиля (условие B); Chromium (measure_ui), 1440×900',
        notes='Пара с № 09 — те же данные, разный стиль: чистое попарное сравнение.'),
    dict(
        id='11', slug='ui-settings-default-look', pair='ui-settings', base='ui', kind='defect', level='n/a',
        src=[UI + '99-raw/cache/screens/gen-a3-settings_1440x900.png'], mode='lossless',
        illustrates='Настройки в «дефолте»: центрированная шапка, поля во всю ширину, эмодзи в заголовках, кнопка-градиент '
                    'с эмодзи, три равные карточки с тенью.',
        assessment='сила: метрика (рубрикой не оценён). Градиентов 2, эмодзи-узлов 11, карточек с тенью 4 из 4.',
        look_at='Поле «Электронная почта» шириной с экран; «💾 Сохранить изменения» с градиентом; три одинаковые карточки '
                'внизу; заголовок по центру.',
        rubric=['kb/ui/05-layout-grid/06-ai-errors-and-checks.md §2 B1 (форма без max-width), C1, D1',
                'kb/ui/13-evaluation-checklists/01-visual-qa-checklist.md группа Я (антислоп)'],
        provenance='свой рендер: HTML агента H по дефолтам стека (условие A); Chromium (measure_ui), 1440×900',
        notes=''),
    dict(
        id='12', slug='ui-settings-preset-a', pair='ui-settings', base='ui', kind='level', level='n/a',
        src=[UI + '99-raw/cache/screens/gen-b3-settings_1440x900.png'], mode='lossless',
        illustrates='Те же настройки по пресету A: колонка формы, секции с пояснениями, подсказка под полем, первичное и '
                    'вторичное действие.',
        assessment='сила: метрика (рубрикой не оценён). Градиентов 0, эмодзи 0, карточек с тенью 0.',
        look_at='Ширина полей по данным; подписи над полями; «Сохранить» + «Отмена». Мелкий брак: в навигации активен '
                '«Обзор» при открытых настройках.',
        rubric=['kb/ui/14-recipes/11-presets.md пресет A',
                'kb/ui/05-layout-grid/06-ai-errors-and-checks.md §2 B1'],
        provenance='свой рендер: HTML агента H по карточке стиля (условие B); Chromium (measure_ui), 1440×900',
        notes=''),
    dict(
        id='13', slug='ui-ref-dashboard-card-offset', pair=None, base='ui', kind='defect', level='n/a',
        src=[UI + '14-recipes/examples/03-dashboard.html', UI + '14-recipes/examples/tokens.css',
             UI + '14-recipes/examples/app.css'],
        render='03-dashboard_light_1440x900.png', mode='lossless',
        illustrates='Эталонный экран пресета A с неочевидным браком: правило `.card + .card { margin-top: 16px }` '
                    'в сетке сдвигает все карточки, кроме первой; в легенде графика две серии, нарисована одна.',
        assessment='сила: метрика (замер по кадру при отборе). Верх первой KPI-плитки — 128 px против 144 у трёх соседей, '
                   'панели — 266 против 282. ui_audit по этому экрану: 223 проверки, 0 FAIL — брак не пойман.',
        look_at='Верхние края KPI-плиток не на одной линии, первая плитка выше и длиннее; «Заказы по дням» выше «Городов»; '
                'легенда «Доставлено» без столбцов.',
        rubric=['kb/ui/13-evaluation-checklists/02-rubrics-and-vlm-critic.md §1.6 (выравнивание)',
                'kb/ui/13-evaluation-checklists/01-visual-qa-checklist.md группа С (сетка и раскладка)'],
        provenance='свой рендер: эталонный HTML ui (агент I, пресет A), Playwright Chromium, 1440×900, светлая тема, '
                   'reduced-motion (26.09.2026)',
        notes='Найдено при отборе; в замороженной базе не исправлено. Эталон по токенам ≠ безупречный экран: «чистый» '
              'на вид экран с брачной сеткой.'),
    dict(
        id='14', slug='ui-ref-orders-table-dark', pair=None, base='ui', kind='level', level='n/a',
        src=[UI + '14-recipes/examples/01-table-with-filters.html', UI + '14-recipes/examples/tokens.css',
             UI + '14-recipes/examples/app.css'],
        render='01-table-with-filters_dark_1440x900.png', mode='lossless',
        illustrates='Эталонная таблица заказов пресета A в тёмной теме: крошки, тулбар фильтров, выбранная строка, '
                    'бейджи статусов, суммы вправо, пагинация.',
        assessment='сила: ворота (автопроверки). ui_audit: 223 проверки, 0 FAIL (светлая и тёмная темы, reduce, hover, '
                   'обход табом); рубрикой не оценён.',
        look_at='Тёмная тема — не инверсия: поверхности на ступень светлее фона, бейджи тонированные, выбранная строка '
                'видна; активный пункт навигации совпадает со страницей.',
        rubric=['kb/ui/14-recipes/02-dark-theme.md',
                'kb/ui/13-evaluation-checklists/01-visual-qa-checklist.md группа Д (тёмная тема)',
                'kb/ui/14-recipes/11-presets.md пресет A'],
        provenance='свой рендер: эталонный HTML ui (агент I), Playwright Chromium, 1440×900, color-scheme dark (26.09.2026)',
        notes='Единственный «уровень» тёмного интерфейса в наборе.'),
    dict(
        id='15', slug='ui-ref-settings-light', pair=None, base='ui', kind='level', level='n/a',
        src=[UI + '14-recipes/examples/06-settings.html', UI + '14-recipes/examples/tokens.css',
             UI + '14-recipes/examples/app.css'],
        render='06-settings_light_1440x900.png', mode='lossless',
        illustrates='Эталонные настройки: меню раздела 240 + контент 640, ряды «подпись + переключатель», подсказки под '
                    'полями, одно первичное действие.',
        assessment='сила: ворота (автопроверки). ui_audit: 223 проверки, 0 FAIL; рубрикой не оценён.',
        look_at='Ширина контента ограничена; переключатели выровнены по правому краю; подписи и подсказки на своих местах; '
                'активный пункт навигации — «Настройки».',
        rubric=['kb/ui/14-recipes/11-presets.md пресет A (A.6 каркас)',
                'kb/ui/13-evaluation-checklists/02-rubrics-and-vlm-critic.md §1'],
        provenance='свой рендер: эталонный HTML ui (агент I), Playwright Chromium, 1440×900, светлая тема (26.09.2026)',
        notes='Сравнить с № 11 и № 12: тот же тип экрана без «дефолта» и без ошибки навигации.'),
    # ------------------------------------------------------------------ ai-media
    dict(
        id='16', slug='f04-hero-average-stock', pair='am-f04', base='ai-media', kind='defect', level='n/a',
        src=[AM + '2.5-stand/mockups/F-04-A1_with_headline.jpg'], mode='q94',
        illustrates='Hero-фото только по брифу: «средний сток» — чашка в центре, растение, окно с горами, тетрадь, пар; '
                    'заголовок макета ложится на растение и окно.',
        assessment='сила: метрика. F-04, 3 из 3 без блока композиции: центр масс x 0,30–0,39, пестрота 51–53 (с блоком — '
                   '25–31); asset_audit warn QA-COMP-CLUTTER, QA-COLOR-HDR.',
        look_at='«ЛЕСНАЯ ОБЖАРКА» и лид теряются на листьях и раме; золотой контровой свет и дымка — «сток»; предметов '
                'больше, чем нужно сюжету.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/hero-photo.rubric.json (automated.warn_codes QA-COMP-CLUTTER, '
                'QA-COMP-CENTER, QA-ZONE-BUSY; vlm g1, g3)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.1'],
        provenance='генерация: GPT Image 2.5 Sunburst 1K (polza); заголовок наложен макетом стенда',
        notes='«Богаче» и хуже: судья, выбирающий по насыщенности кадра, выберет этот вариант.'),
    dict(
        id='17', slug='f04-hero-composition-block', pair='am-f04', base='ai-media', kind='level', level='n/a',
        src=[AM + '2.5-stand/mockups/F-04-B1_with_headline.jpg'], mode='q94',
        illustrates='Тот же бриф + блок композиции: объект в правой трети, ровная стена под заголовок.',
        assessment='сила: метрика. F-04, 3 из 3: центр масс x 0,81–0,85 (порог ≥ 0,62), края в зоне заголовка 0,001–0,006 '
                   '(порог ≤ 0,06), пестрота 25–31; asset_audit — только warn QA-COLOR-WARM (тёплый сдвиг GPT 2.5, '
                   'лечится грейдом).',
        look_at='Заголовок, лид и кнопка на спокойной стене; свет и зерно «живые»; крошки на столе — деталь сюжета, а не шум.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/hero-photo.rubric.json (vlm g1, g3)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.1'],
        provenance='генерация: GPT Image 2.5 Sunburst 1K (polza); заголовок наложен макетом стенда',
        notes=''),
    dict(
        id='18', slug='e08-armchair-seedream-dirty', pair='am-e08', base='ai-media', kind='defect', level='n/a',
        src=[AM + '2.5-stand/E-08-blind/scene1_frame3.png'], mode='q92',
        illustrates='Hero-интерьер «кресло у окна», Seedream 5 Pro: бархат пятнистый, «грязный» вместо «слегка потёртого», '
                    'тусклая серо-зелёная гамма.',
        assessment='сила: голос вслепую (заказчик, 1 судья, лист из 6 моделей): «сразу минус».',
        look_at='Подлокотники и сиденье в пятнах; табурет вместо дубового столика; экспозиция и тон не дают «утреннего '
                'уюта» брифа. Зона под заголовок слева при этом есть.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/hero-photo.rubric.json (vlm.defect_questions)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.1, §4 (слепые голоса)'],
        provenance='генерация: Seedream 5 Pro (polza), 1312×736',
        notes='Почему минус, заказчик не сказал: «на что смотреть» — наша версия. Бриф просил «slightly worn armrests».'),
    dict(
        id='19', slug='e08-armchair-sunburst-cozy', pair='am-e08', base='ai-media', kind='level', level='n/a',
        src=[AM + '2.5-stand/E-08-blind/scene1_frame1.png'], mode='q92',
        illustrates='Тот же бриф, GPT Image 2.5 Sunburst: тёплое утро, кресло в правой трети, фактуры бархата, льна и дуба.',
        assessment='сила: голос вслепую (заказчик): «хорошо» — вместе с Flare и NB2.',
        look_at='Материалы и свет «живые». Но стена под заголовок в пятнах света и тени листьев, а бриф просил ровную зону — '
                'с заголовком проверять макетом, как № 17.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/hero-photo.rubric.json (vlm g1 — ровная зона под заголовок)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.1'],
        provenance='генерация: GPT Image 2.5 Sunburst 1K (polza), 1672×941',
        notes='Голос человека не отменяет замер зоны текста: уровень по вкусу, зона — под вопросом.'),
    dict(
        id='20', slug='e12-series-palette-drift', pair=None, base='ai-media', kind='defect', level='n/a',
        src=[AM + '2.3-series/E-12_blind_sheet.jpg'], mode='q94',
        illustrates='Серия иллюстраций по эталону (E-11): модели 1, 2, 4 уводят палитру и заливку, модель 3 держит стиль.',
        assessment='сила: мнение — оценка глазами по слепому листу (кто смотрел, в записях не указано), n = 2 сюжета × 4 '
                   'модели. Ключ: 1 — NB2, 2 — Seedream 4.5, 3 — GPT Image 2.5 Flare, 4 — Nano Banana Pro.',
        look_at='Эталон сверху: контур navy, коралл только на ключевом объекте, кремовый фон. 1 — зелёные столбики; '
                '2 — коробка залита коричневым, лупа и столбики синие; 4 — синие столбики и коралловая коробка; 3 — контур, '
                'коралл и крем в обоих сюжетах.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/series.rubric.json (warn QA-SERIES-PALETTE, QA-SERIES-HUE; vlm g2)',
                'kb/ai-media/06-art-direction-consistency/02-series-and-consistency.md §6 (дрейф)'],
        provenance='генерации: эталон — NB2 (E-11); серия — NB2, Seedream 4.5, GPT Image 2.5 Flare, Nano Banana Pro (polza); '
                   'лист слепого голосования',
        notes='Лист целиком: брак виден только рядом с эталоном, «уровень» на том же листе — модель 3. В §11 синтеза '
              'записано «голос вслепую» — в записях базы голоса нет, отсюда сила «мнение».'),
    dict(
        id='21', slug='e15-remove-cup-nb2-leak', pair='am-e15', base='ai-media', kind='defect', level='n/a',
        src=[AM + '4-edits/E-15-check/E-15-S15-a-nb2-1k-1/sheet.jpg'], mode='q94',
        illustrates='Правка «убери чашку, остальное не трогай» у Nano Banana 2: чашка убрана, но стол заменён «более '
                    'богатой» древесиной, стена получила фактуру.',
        assessment='сила: метрика. edit_check 0.2: LEAK — утечка вне цели 0,1719, SSIM вне цели 0,92, защита банки SSIM '
                   '0,888; ΔE00 кадра 1,25.',
        look_at='Панели: оригинал | правка | карта разницы | композит по маске. На правке — волокна дерева, которых не '
                'было; на карте жёлтым весь стол и стена; на композите — заплатка другого стола на месте чашки.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/edit.rubric.json (warn QA-EDIT-LEAK, QA-EDIT-REDRAW; '
                'fail QA-PROTECT-CHANGED)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.8'],
        provenance='генерация-правка: Gemini 3.1 Flash Image — Nano Banana 2 (polza) по своему рендеру Blender (сцена агента E)',
        notes='Добор (соседний прогон того же теста E-15). «Богаче» и хуже: стол красивее оригинала, но правка обязана '
              'не трогать остальное.'),
    dict(
        id='22', slug='e15-remove-cup-seedream-pass', pair='am-e15', base='ai-media', kind='level', level='n/a',
        src=[AM + '4-edits/E-15-check/E-15-S15-a-sd5pro-1/sheet.jpg'], mode='q94',
        illustrates='Та же правка у Seedream 5 Pro: чашка и её тень убраны, остальное на месте.',
        assessment='сила: метрика. edit_check 0.2: PASS — утечка 0,0097, SSIM вне цели 0,982, защита банки 0,984; ΔE00 '
                   'кадра 0,70.',
        look_at='На карте разницы — только место чашки и едва заметные контуры банки (шум пересэмплирования); композит '
                'неотличим от правки.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/edit.rubric.json',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.8'],
        provenance='генерация-правка: Seedream 5 Pro (polza) по своему рендеру Blender (сцена агента E)',
        notes=''),
    dict(
        id='23', slug='h03-cutout-glass-cloud', pair='am-h03', base='ai-media', kind='defect', level='n/a',
        src=[AM + 'S5-analysis/H-03_sheet.jpg'], crop=(0, 330, 1250, 660), mode='q94',
        illustrates='Вырез `background: transparent` у стекла: вокруг флакона облако исходного фона, внутри стекла '
                    'полупрозрачности нет, маска блоками.',
        assessment='сила: метрика. H-03_alpha.json: «полупрозрачных 50,5 %» — это облако до 152 px от тела, внутри тела '
                   '0 %; энергия края на периоде 16 px ×1,6–1,7 от равномерной (блоки).',
        look_at='На тёмном #0E1417 и шахматке — мутный ореол ступенями вокруг флакона; стекло непрозрачное; надпись '
                '«RIVIÈRE / EAU DE PARFUM» дописана моделью без запроса.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/cutout.rubric.json (warn QA-ALPHA-HALO, QA-ALPHA-GLASS; '
                'fail QA-ALPHA-FAKE)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.6'],
        provenance='генерация: GPT Image 2.5 Sunburst через RouterAI, background: transparent',
        notes='Вырезка нижнего ряда листа 1250×660 (y 330–660).'),
    dict(
        id='24', slug='h03-cutout-fur-soft-edge', pair='am-h03', base='ai-media', kind='level', level='n/a',
        src=[AM + 'S5-analysis/H-03_sheet.jpg'], crop=(0, 0, 1250, 330), mode='q94',
        illustrates='Тот же вызов для меха: настоящая мягкая альфа волокон, отверстие кольца прозрачно.',
        assessment='сила: метрика. α = 0 — 27,2 %, частичной — 36,3 % (вся на кайме волокон, медиана 44 px от тела), цвет '
                   'каймы = цвет меха; alpha_check fake → REAL_ALPHA.',
        look_at='Одинаково чистый край на белом, тёмном и шахматке; внутри кольца — фон, а не белый.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/cutout.rubric.json (warn QA-ALPHA-FIBERS)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.6'],
        provenance='генерация: GPT Image 2.5 Sunburst через RouterAI, background: transparent',
        notes='Вырезка верхнего ряда листа (y 0–330).'),
    dict(
        id='25', slug='e02-cyrillic-flux-typos', pair='am-e02', base='ai-media', kind='defect', level='n/a',
        src=[AM + '2.1-cyrillic/crops/flux2pro.jpg'], mode='q94',
        illustrates='Баннер с кириллицей у FLUX.2 Pro: «Весеннаія», «всіо», дефис вместо минуса.',
        assessment='сила: метрика + глаз. OCR E-02 и чтение: ошибки в обеих длинных строках.',
        look_at='«Весеннаія» (і вместо я), «всіо», «-30» с дефисом. Шрифт и вёрстка аккуратны — брак виден только при чтении.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/text-image.rubric.json (fail QA-TEXT-MISMATCH)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.7'],
        provenance='генерация: FLUX.2 Pro (polza); кроп зоны текста из прогона E-02',
        notes=''),
    dict(
        id='26', slug='e02-cyrillic-sunburst-minus-gap', pair='am-e02', base='ai-media', kind='defect', level='n/a',
        src=[AM + '2.1-cyrillic/crops/sunburst.jpg'], mode='q94',
        illustrates='Та же задача у GPT Image 2.5 Sunburst: всё дословно, кроме пробела после минуса — «– 30 %».',
        assessment='сила: глаз (запись фазы 5, E-02). OCR такой брак не различает.',
        look_at='«Скидки до – 30 %» — знак оторван от числа; остальной текст безупречен.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/text-image.rubric.json (fail QA-TEXT-MISMATCH)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.7'],
        provenance='генерация: GPT Image 2.5 Sunburst 1K (polza); кроп зоны текста из прогона E-02',
        notes='Добор (тот же прогон E-02). Тонкий брак: судья, проверяющий «все слова на месте», поставит PASS.'),
    dict(
        id='27', slug='e02-cyrillic-flare-verbatim', pair='am-e02', base='ai-media', kind='level', level='n/a',
        src=[AM + '2.1-cyrillic/crops/flare.jpg'], mode='q94',
        illustrates='Кириллица баннера дословно: «Весенняя распродажа / Скидки до −30 % на всю мебель / Подробнее».',
        assessment='сила: метрика + глаз. OCR E-02 и чтение: дословно.',
        look_at='Все буквы и знаки на месте; «−30 %» — минус слитно с числом.',
        rubric=['kb/ai-media/11-evaluation-qa/rubrics/text-image.rubric.json (vlm g1, g2)',
                'kb/ai-media/11-evaluation-qa/03-checklists-by-asset.md §3.7'],
        provenance='генерация: GPT Image 2.5 Flare (polza); кроп зоны текста из прогона E-02',
        notes=''),
    # ------------------------------------------------------------------ blender
    dict(
        id='28', slug='zveno-hero-cycles', pair='bl-zveno-hero', base='blender', kind='level', level='L2',
        src=[BL + '15-showcase/zveno/judge/b-blender__hero-best.png'], mode='q92',
        illustrates='Лучший неподвижный кадр L2 «Звено»: Cycles 128 спп, длинные мягкие блики на лаке, точёные крышки, '
                    'крепёж фланца, маркировка «ЗВЕНО», кабель, отражение пола.',
        assessment='сила: голос вслепую (1 судья — заказчик, два порядка): B > A, B > C; лак p75 91–96 L*, фон ΔE 3,1–4,2 '
                   'к странице.',
        look_at='Деталь отличает «вау» от «уверенно»: печать поверх лака, крепёж, J1/J2, кабель; белое без пересвета.',
        rubric=['kb/blender/11-evaluation-qa/06-wow-pairwise-3d.md §5, §7',
                'kb/blender/15-showcase/KIT.md §4 п. 4–5 (правки против «каталога», цели-числа)',
                'kb/blender/15-showcase/VERDICT.md §4.1, §5'],
        provenance='свой рендер: Blender 5.2.2 Cycles 128 спп + OIDN, 1600×1000',
        notes=''),
    dict(
        id='29', slug='zveno-hero-code', pair='bl-zveno-hero', base='blender', kind='level', level='L2',
        src=[BL + '15-showcase/zveno/judge/a-code__hero.png'], mode='q92',
        illustrates='Тот же кадр кодом (three.js, вид p3): чистая студия, ореол за рукой, отражение основания.',
        assessment='сила: голос вслепую: A < B, A > C, A > v2 (№ 02); ворота 0 FAIL × 5, motion_check L2 0/0/0.',
        look_at='Крышки темнее и «синтетичнее», чем у Cycles; на крышках J2/J3 — белые искры-точки (мелкий брак, виден при '
                'увеличении); фон — намеренное свечение (ΔE 3,0).',
        rubric=['kb/blender/11-evaluation-qa/06-wow-pairwise-3d.md §5, §7',
                'kb/blender/15-showcase/VERDICT.md §4.1'],
        provenance='свой рендер: three.js r186 кодом (дорожка CD), Chromium ANGLE, 1600×1000',
        notes='Середина лестницы: «уверенно», не «вау».'),
    dict(
        id='30', slug='zveno-hero-hybrid-still', pair='bl-zveno-hero', base='blender', kind='defect', level='L2',
        src=[BL + '15-showcase/zveno/judge/c-hybrid__hero.png'], mode='q92',
        illustrates='Гибрид: модель Blender (GLB) под светом three.js — типичный брак дороги C в неподвижном кадре.',
        assessment='сила: голос вслепую: C < A и C < B во всех четырёх парах по ремеслу (главный кадр, разборка); ворота 0 FAIL.',
        look_at='Пересвеченная белая труба, ореол-засветка вокруг руки, серые «стеклянные» крышки: деталь Blender теряется '
                'при свете кода.',
        rubric=['kb/blender/15-showcase/VERDICT.md §4.1, §5.1',
                'kb/blender/11-evaluation-qa/02-render-critique.md §3'],
        provenance='свой рендер: GLB из Blender 5.2.2 в three.js r186 (гибрид C), Chromium ANGLE, 1600×1000',
        notes='Брак — про стоп-кадр: страницу C целиком (ввод + модель) заказчик вживую выбрал лучшей. Постер гибрида '
              'берут кадром Cycles (№ 28).'),
    dict(
        id='31', slug='sdano-iso-cutaway-first-screen', pair='sdano-first', base='blender', kind='level', level='L0',
        src=[BL + '15-showcase/sdano/judge/b-blender__first-screen-desk.png'], mode='lossless',
        illustrates='L0 услуги: изометрия-разрез Cycles с сюжетом — инженер-манекен, лазер, трещина в круге мелом, булавки = '
                    'пункты акта.',
        assessment='сила: голос вслепую: B > A (№ 05) во всех 4 парах; ворота 9/9/6 OK, motion_check L0 0/0/0.',
        look_at='Сюжет в одном кадре. Мелкий брак в уровне: подписи площадей бледные на светлом рендере, «С/у 4,1 м²» '
                'пересечена стеной, на плане 4 отметки из 7.',
        rubric=['kb/blender/11-evaluation-qa/06-wow-pairwise-3d.md §5, §7',
                'kb/blender/15-showcase/VERDICT.md §4.3'],
        provenance='свой рендер: Blender 5.2.2 Cycles 128 спп на странице, Chromium 1440×900',
        notes='Фигура инженера — безликий белый манекен из примитивов (≈ 60 px), без лица и кистей: оставлена как условный '
              'знак масштаба (решение по Р56 с причиной — вопрос заказчику в REPORT).'),
    dict(
        id='32', slug='sdano-phase1-iso-in-svg-slot', pair=None, base='blender', kind='defect', level='L0',
        src=[BL + '15-showcase/sdano/judge/phase1/sheet__plan-mob.jpg'], mode='q94',
        illustrates='Фаза 1: изометрия Blender поставлена в окно векторного плана — на телефоне мельче и мягче вектора.',
        assessment='сила: мнение (разбор дорожки SD, VERDICT §4.3 — «провал формы подачи»); исправлено в фазе 2 крупным '
                   'кадром и своим кадром телефона (№ 31).',
        look_at='Справа (B): подписи ≈ 8 px, «Гостиная 17,8 м²» пересечена стенами, отметки мелкие; слева (A): вектор читается. '
                'Лист целиком — брак виден только рядом с вектором.',
        rubric=['kb/blender/15-showcase/VERDICT.md §4.3',
                'kb/blender/11-evaluation-qa/02-render-critique.md §3'],
        provenance='свой рендер: кадр Blender 5.2.2 Cycles (B) и SVG (A) на странице, Chromium 390×844 @3; лист дорожки SD',
        notes='Заменяет кандидата № 40 (`phase1/b-blender__plan.png`): на отдельном кадре 1600 px брак подачи не виден. '
              '«Богаче» (3D вместо вектора) и хуже — в том же окне: дело в размере слота.'),
    dict(
        id='33', slug='sdano-beam-off-grey-paper', pair='bl-sdano-paper', base='blender', kind='defect', level='L1',
        src=[BL + '99-raw/experiments/SD/shots/sd2_c4/c_beam-off.png'], mode='lossless',
        illustrates='«Фонарик инженера» в покое: мягкое плечо тона применено ко всему кадру — белая бумага страницы вокруг '
                    'плана посерела.',
        assessment='сила: метрика. Пикселей серого 238–244 — 8,7 % кадра (после правки 0,2 %); бумага 240–241 из 255 '
                   'вместо 255 (находка RC при написании рецептов).',
        look_at='Светло-серый прямоугольник справа от x ≈ 780 — от шапки до строки цифр; слева страница белая. Сравнить с № 34.',
        rubric=['kb/blender/12-recipes/16-relight-by-passes.md п. 9',
                'kb/blender/11-evaluation-qa/02-render-critique.md §2 (автопроверки картинки)'],
        provenance='свой рендер: кадр Blender Cycles + переосвещение WebGL2 без three (сборка SD2), Chromium 1440×900',
        notes='Поодиночке почти невидим; виден в паре или замером. Кодирование без потерь — чтобы замер тона повторялся.'),
    dict(
        id='34', slug='sdano-beam-off-white-paper', pair='bl-sdano-paper', base='blender', kind='level', level='L1',
        src=[BL + '99-raw/experiments/SD/shots/sd3_c10/c_beam-off.png'], mode='lossless',
        illustrates='После правки SD3: полумрак только по маске макета, бумага снова #fff.',
        assessment='сила: метрика + ворота. Серого 0,2 %, белого ≥ 254 — 71 % (было 63,3 %); страница C — ворота 9/9/6 OK, '
                   'motion_check L1 0/0/0 (SD4).',
        look_at='Фон вокруг плана белый, затемнён только сам макет; подсказка «Наведите курсор…» на месте.',
        rubric=['kb/blender/12-recipes/16-relight-by-passes.md п. 9'],
        provenance='свой рендер: кадр Blender Cycles + переосвещение WebGL2 без three (сборка SD3), Chromium 1440×900',
        notes=''),
    dict(
        id='35', slug='zveno-cap-anisotropy-no-tangent', pair=None, base='blender', kind='defect', level='L2',
        src=[BL + '99-raw/experiments/Z/out/c_judge_tan/cap_compare.jpg'], mode='q94',
        illustrates='Анизотропия точёных крышек в GLB без атрибута TANGENT: three строит направление из производных UV — '
                    '«веер» треугольников на 48 гранях.',
        assessment='сила: глаз + причина в коде: `gltf-transform optimize` молча выбрасывает TANGENT без '
                   '`--prune-attributes false` (правило 76); исправление +80 КБ br.',
        look_at='Левая колонка — радиальный «веер» на крышках J2 и J1; правая — ровный точёный металл после возврата '
                'TANGENT. Подписи в углу («без/с TANGENT») отрисовались квадратами — кириллицы не было в шрифте листа.',
        rubric=['kb/blender/README.md правило 76',
                'kb/blender/12-recipes/15-hybrid-blender-code.md',
                'kb/blender/11-evaluation-qa/05-master-checklist.md §7 (EXP)'],
        provenance='свой рендер: GLB из Blender 5.2.2 в three.js r186 (гибрид C), Chromium; лист сравнения Z3',
        notes='Лист целиком: «до» и «после» в одном кадре.'),
    dict(
        id='36', slug='keyboard-ktx2-etc1s-lilac', pair=None, base='blender', kind='defect', level='L1',
        src=[BL + '15-showcase/keyboard/gallery/c-webp-atlas.webp'], mode='copy',
        illustrates='Атлас надписей в KTX2 ETC1S: почти-серые колпачки (tab, caps) уходят в сиреневый.',
        assessment='сила: глаз + метрика веса (KB3): сдвиг есть и при -tq 10; WebP-атлас — цвет как у кода и Cycles, '
                   '−229 КБ br (не нужен транскодер Basis 212 КБ br).',
        look_at='Ряд 1 (KTX2) против ряда 3 (Cycles — эталон цвета): клавиши tab и caps сиреневые; ряд 2 (WebP) — как эталон.',
        rubric=['kb/blender/12-recipes/15-hybrid-blender-code.md п. 6 (WebP по умолчанию)',
                'kb/blender/README.md правило 41, реестр T9'],
        provenance='свой рендер: GLB из Blender (гибрид C) в three.js r186 при двух упаковках + кадр Cycles; лист галереи '
                   '1200×750',
        notes='Добор (галерея приёмов blender). WebP базы скопирован без перекодирования.'),
    dict(
        id='37', slug='c1-laptop-first-try-gradient', pair='bl-c1-laptop', base='blender', kind='defect', level='n/a',
        src=[BL + '99-raw/experiments/C1/11-naive-first-try/out/opus/views_laptop/sheet.png'], mode='lossless',
        illustrates='Ноутбук «с первой попытки» (Claude Opus без протокола): градиент на экране и чистая геометрия — '
                    '«законченнее» на вид.',
        assessment='сила: метрика (проверки кодом). Габарит 3,20 × 2,83 × 2,12 м (×10), экран — процедурный градиент '
                   '(ShaderNodeValToRGB), в glTF не экспортируется; scene_check — fail. В J/02 Opus-судья выбрал этот '
                   'вариант в обоих порядках.',
        look_at='На листе видов масштаб не виден вообще: кадр строится по габариту. Градиент — единственное видимое отличие, '
                'и он исчезнет после экспорта.',
        rubric=['kb/blender/11-evaluation-qa/02-render-critique.md §3, §4.2 (опыт J/02)',
                'kb/blender/11-evaluation-qa/01-scene-geometry-checks.md §3 (паспорт и размеры)',
                'kb/blender/11-evaluation-qa/05-master-checklist.md §3 (GEO), §7 (EXP)'],
        provenance='свой рендер: Blender 5.2.2, скрипт Claude Opus без протокола (C1/11), render_views — 4 ракурса',
        notes='Главный известный риск судьи: «богаче» = брак, невидимый на картинке.'),
    dict(
        id='38', slug='c1-laptop-protocol', pair='bl-c1-laptop', base='blender', kind='level', level='n/a',
        src=[BL + '99-raw/experiments/C1/12-protocol-objects/out/views_laptop/sheet.png'], mode='lossless',
        illustrates='Тот же ноутбук по протоколу: паспорт, реальные размеры, детали мешем, аудит, GLB.',
        assessment='сила: метрика (проверки кодом). 0,304 × 0,284 × 0,213 м, валидатор glTF 0/0, 14 390 треуг., 6 вызовов; '
                   'scene_check — pass.',
        look_at='Экран — плоская заливка-заглушка (честно экспортируется); крышка и петля соединены; на картинке «беднее» № 37.',
        rubric=['kb/blender/11-evaluation-qa/02-render-critique.md §3, §4.2',
                'kb/blender/11-evaluation-qa/01-scene-geometry-checks.md §3'],
        provenance='свой рендер: Blender 5.2.2 по протоколу (C1/12), render_views — 4 ракурса',
        notes='Уровень кандидата № 48; брак № 48 (первая попытка Sonnet с разлетевшимися плитами) заменён вариантом Opus — '
              'его выбрал судья, и брак не виден глазом.'),
    dict(
        id='39', slug='c1-mug-first-try-coffee', pair='bl-c1-mug', base='blender', kind='defect', level='n/a',
        src=[BL + '99-raw/experiments/C1/11-naive-first-try/out/opus/views_mug/sheet.png'], mode='lossless',
        illustrates='Кружка «с первой попытки» (Claude Opus): глянец, кофе внутри — «богаче для hero».',
        assessment='сила: метрика (проверки кодом). Габарит 2,66 × 2,04 × 2,22 м (×23), scene_check — fail. В J/02 судья '
                   'выбрал её в обоих порядках.',
        look_at='На картинке брака нет — он в габарите и паспорте; кофе и глянец — повод выбрать «на глаз».',
        rubric=['kb/blender/11-evaluation-qa/02-render-critique.md §4.2',
                'kb/blender/11-evaluation-qa/01-scene-geometry-checks.md §3'],
        provenance='свой рендер: Blender 5.2.2, скрипт Claude Opus без протокола (C1/11), render_views — 4 ракурса',
        notes='Добор «сверх лимита» (§11): «кружка 2,2 м — брак, невидимый на листе».'),
    dict(
        id='40', slug='c1-mug-protocol', pair='bl-c1-mug', base='blender', kind='level', level='n/a',
        src=[BL + '99-raw/experiments/C1/12-protocol-objects/out/views_mug/sheet.png'], mode='lossless',
        illustrates='Кружка по протоколу: 0,119 × 0,082 × 0,095 м, матовая керамика, полость, ручка.',
        assessment='сила: метрика (проверки кодом). Размеры по паспорту, валидатор glTF 0/0, 5 020 треуг., 2 вызова; '
                   'scene_check — review (не fail).',
        look_at='Честная кружка без «истории»: судья по вкусу выбрал бы № 39.',
        rubric=['kb/blender/11-evaluation-qa/02-render-critique.md §4.2',
                'kb/blender/11-evaluation-qa/01-scene-geometry-checks.md §3'],
        provenance='свой рендер: Blender 5.2.2 по протоколу (C1/12), render_views — 4 ракурса',
        notes=''),
]

# Кодирование по решению заказчика (26.09, через оркестратора):
#   3D (рендеры blender, 3D-сцены creative, код-3D) и листы с усилением — оригинал как есть;
#   прочее — WebP/AVIF без видимой потери, при любом сомнении — оригинал; размер набора не важен.
# orig — файл базы байт в байт; png-crop — вырезка из листа без потерь (PNG); lossless — WebP без потерь (пиксели = PNG).
T3D = '3D: оригинал по решению заказчика.'
JPG2 = ('Исходник — JPEG: перекодирование в WebP — вторая потеря; по правилу «при сомнении — оригинал» оставлен '
        'оригинал.')
ENCODING = {
    '01': ('orig', True, T3D), '02': ('orig', True, T3D), '03': ('orig', True, T3D), '04': ('orig', True, T3D),
    '05': ('orig', False, JPG2 + ' Экономия WebP q94 — 26 КБ, ценой сдвига цвета мелких цветных деталей (отметки плана).'),
    '06': ('orig', False, JPG2 + ' Экономия WebP q94 — 5 КБ.'),
    '07': ('png-crop', False, 'Вырезка без потерь (PNG), пиксели листа не менялись: WebP q94 давал контуры квантования '
                              'на тёмных пятнах спектра (видны при усилении контраста).'),
    '08': ('png-crop', False, 'Вырезка без потерь (PNG), как у № 07: пара кодируется одинаково.'),
    '09': ('lossless', False, ''), '10': ('lossless', False, ''), '11': ('lossless', False, ''),
    '12': ('lossless', False, ''), '13': ('lossless', False, ''), '14': ('lossless', False, ''),
    '15': ('lossless', False, ''),
    '16': ('orig', False, JPG2 + ' Пара с № 17 кодируется одинаково.'),
    '17': ('orig', False, JPG2 + ' WebP q94 сглаживал зерно ровной стены (шум гладких зон −25 %) — а ровность стены '
                                 'и оценивается.'),
    '18': ('lossless', False, ''), '19': ('lossless', False, ''),
    '20': ('orig', False, JPG2 + ' WebP q94 сдвигал цвет тонких цветных штрихов (ΔE76 p95 6,3, p99 8,2) — а '
                                 'оценивается палитра.'),
    '21': ('orig', False, 'Лист с картой разницы (усиление): оригинал без пережатия — шум карты и есть доказательство '
                          'утечки.'),
    '22': ('orig', False, 'Лист с картой разницы (усиление): оригинал без пережатия, как у № 21.'),
    '23': ('png-crop', False, 'Вырезка без потерь (PNG), пиксели листа не менялись: артефакты сжатия могли бы подделать '
                              'оцениваемые «ступени» маски.'),
    '24': ('png-crop', False, 'Вырезка без потерь (PNG), как у № 23: пара кодируется одинаково.'),
    '25': ('orig', False, JPG2 + ' WebP q94 сглаживал фактуру фона (шум гладких зон −40 %); группа E-02 кодируется '
                                 'одинаково.'),
    '26': ('orig', False, JPG2 + ' Группа E-02 кодируется одинаково.'),
    '27': ('orig', False, JPG2 + ' Группа E-02 кодируется одинаково.'),
}
for _i in range(28, 41):
    ENCODING[f'{_i:02d}'] = ('orig', True, T3D)
for _fr in FRAMES:
    _fr['mode'], _fr['is3d'], _fr['why'] = ENCODING[_fr['id']]

# Кандидаты SYNTHESIS §11 и «сверх лимита», не вошедшие в набор (для контактного листа и отчёта).
EXCLUDED = [
    ('§11 № 30', 'ai-media', '4-edits/E-15-check/E-15-S15-mask-qwen21-1k-1/sheet.jpg',
     'выход Qwen 2.1 — лицензия «только для исследований» (Р56)', 'правило'),
    ('§11 № 25', 'ai-media', '2.5-stand/E-08-zoom/scene2_1_nbpro_hands.jpg',
     'лица и руки синтетических людей (Р56)', 'правило'),
    ('§11 № 43', 'blender', '99-raw/notes/trial/FX/t1/{A_studio,B_hero}_cycles.png',
     'кейс наушников рецепта 01 в размерах AirPods Pro (60,6 × 45,2 × 21,7 мм) — узнаваемый чужой дизайн; кадры 360×360',
     'правило'),
    ('сверх лимита', 'blender', '12-recipes/examples/01-hero-product/poster_blender.png',
     'тот же кейс AirPods Pro — узнаваемый чужой дизайн', 'правило'),
    ('сверх лимита', 'ai-media', 'S5-analysis/VAR_sheet_1.jpg', 'узнаваемые AirPods Pro — чужой дизайн', 'правило'),
    ('§11 № 35', 'ai-media', 'SC-showcase/SC-04_endpoints.jpg',
     'входы A и B — фото Poly Haven (CC0, Greg Zaal), кадры видео повторяют их по построению: не своя генерация', 'правило'),
    ('§11 № 26', 'ai-media', '2.3-series/F-01_sheet.jpg',
     'верхний ряд — фото Poly Haven (CC0, Sergej Majboroda); без него сравнения с эталоном нет. Серию представляет № 20',
     'правило'),
    ('сверх лимита', 'ai-media', '5-vector/blind-icons.jpg (CM-01)',
     'бриф и палитра MARÉA — айдентика реального приложения заказчика (тот же довод, что у MS-marea)', 'правило'),
    ('сверх лимита', 'ai-media', 'MS-marea/loops/MS-03-…',
     'айдентика реального приложения заказчика; брак «фантом» — во времени, в одном кадре не виден', 'правило'),
    ('сверх лимита', 'ai-media', '14-recipes/examples/demo-landing/measure/desktop/shot_1440x900.jpg',
     'генераций нет (рендеры Blender, CC0); «уровней» и так достаточно', 'выбор'),
    ('§11 № 1', 'creative', '10-recipes/examples/l2-zveno/img/hero-d.webp',
     'тот же рендер v2 взят кадром сцены `out/f-after/hero.png` (№ 02): паре «до/после» нужны одинаковые камера и размер',
     'заменён'),
    ('§11 № 2', 'creative', '10-recipes/examples/l2-zveno/img/hero-m.webp', 'дубль постера № 1 в кадре телефона', 'выбор'),
    ('§11 № 3', 'creative', '10-recipes/examples/l2-zveno/img/st-scan.webp',
     'показывает функцию (станция для reduce и без WebGL), а не уровень вида; по виду дублирует сцену', 'выбор'),
    ('§11 № 4, 5', 'creative', '99-raw/experiments/J/04-light-pass/sheet-{before,after}.jpg',
     'заменены кадрами сцены того же опыта (№ 01, 02): на листах 1448×2409 из 11 снимков разница света неразличима',
     'заменён'),
    ('§11 № 8', 'creative', '99-raw/experiments/J/01-l0-sdano/shots/mob_first.jpg', 'дубль уровня L0 (№ 05)', 'выбор'),
    ('§11 № 10', 'creative', '99-raw/experiments/J/03-l1-sverka/shots/desk_scroll_sheet.jpg',
     'в первой клетке листа наложен кроп `first_bottom.jpg` (артефакт склейки); L1 дан первым экраном (№ 06)', 'заменён'),
    ('§11 № 11, 12', 'creative', '99-raw/experiments/J/05-webkit/sheet-l1*.jpg',
     'счётчик ≈ 6 px на листе; брак движка ловят кадры WebKit в воротах, а не судья по виду', 'резерв'),
    ('§11 № 14', 'creative', '99-raw/experiments/J/02-l2-zveno/motion/station_desk_story-modules_s2.jpg',
     'иллюстрация проверки станций, не уровень и не брак', 'выбор'),
    ('§11 № 16, 19', 'ui', '99-raw/cache/screens/gen-{a2,b2}-dashboard_1440x900.png',
     'a2 — третий экран того же «дефолта» (повтор № 09, 11); b2 — слабый уровень (пустая заглушка графика, обрезано '
     '«Последние 30 дне»); место отдано эталонным экранам ui (№ 13–15)', 'выбор'),
    ('§11 № 28', 'ai-media', '4-edits/E-15-check/E-15-S14-a-nb2-1k-1/sheet.jpg',
     'утечка 0,0435 видна только на карте разницы; ту же ошибку правки нагляднее показывает № 21', 'резерв'),
    ('§11 № 31', 'ai-media', '4-edits/H-08-check/H-08-outpaint-9x16-sunburst/sheet.jpg',
     'лист 540×320, перерисованный центр глазом не виден; класс «брак только по метрике» уже есть (№ 37, 39)',
     'резерв'),
    ('§11 № 40', 'blender', '15-showcase/sdano/judge/phase1/b-blender__plan.png',
     'на отдельном кадре 1600 px брак подачи не виден; взят лист телефона той же фазы (№ 32)', 'заменён'),
    ('§11 № 41', 'blender', '15-showcase/keyboard/judge/b-blender__first-screen-desk.png',
     'уровень L1 якоря класса (A = B); лимит ≈ 40 и баланс — в резерве', 'резерв'),
    ('§11 № 42', 'blender', '15-showcase/velmora/judge/{b-blender,ai}__f030.png',
     'пара уровней-ничья (4 ничьи из 4): полезна для калибровки «ничьей», но добавила бы 2 уровня сверх баланса — '
     'вопрос заказчику', 'резерв'),
    ('§11 № 46', 'blender', '99-raw/notes/trial/AJ/crop_kb_b_exploded_bgdiff_x6.png',
     'диагностическая карта ×6, а не кадр; класс «брак только при усилении» дают № 21 и № 33', 'выбор'),
    ('§11 № 47', 'blender', '99-raw/notes/trial/AJ/crop_z_a_scan_x2.png',
     'мелкий брак кода (искры, шов, лесенка) — ИИ-отсев назвал «мелочью»; искры видны и на № 29', 'резерв'),
    ('§11 № 48 (брак)', 'blender', '99-raw/experiments/C1/11-naive-first-try/out/sonnet/views_laptop/sheet.png',
     'очевидный брак (разлетевшиеся плиты); в пару к протоколу взят вариант Opus (№ 37) — его выбрал судья J/02', 'заменён'),
    ('§11 № 49', 'blender', '99-raw/experiments/C1/11-naive-first-try/out/haiku/views_tree/sheet.png',
     'на листе видов объект в кадре (ракурсы строит render_views по габариту); «вне кадра» — только на листе камеры, '
     'где смотреть не на что (пустые прямоугольники)', 'выбор'),
    ('§11 № 50', 'blender', '99-raw/experiments/J/02-pairwise-judge/pairs_order1.png',
     'взят не листом, а парами в исходном разрешении (№ 37–40); ракета opus — резерв; подписи листа отрисовались '
     'квадратами', 'заменён'),
    ('сверх лимита', 'blender', '15-showcase/*/gallery/*.webp (41)',
     'иллюстрации приёмов без пары «уровень/брак»; взят один лист — c-webp-atlas.webp (№ 36)', 'выбор'),
]


def load_manifest():
    man = {}
    with gzip.open(MANIFEST, 'rt', encoding='utf-8') as f:
        next(f)
        for line in f:
            research, path, _bytes, _mtime, sha = line.rstrip('\n').split('\t')
            man[f'{research}/{path}'] = sha
    return man


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def encode(fr, ui_ref_dir):
    """Пишет кадр. orig — копия файла базы байт в байт; png-crop — вырезка без потерь; lossless — WebP без потерь."""
    stem = FRAMES_DIR / f"{fr['id']}-{fr['slug']}"
    mode = fr['mode']
    if mode == 'orig':
        src = ROOT / fr['src'][0]
        out = stem.with_suffix(src.suffix.lower())
        shutil.copyfile(src, out)
        with Image.open(out) as im:
            return out, im.size
    if fr.get('render'):
        im = Image.open(pathlib.Path(ui_ref_dir) / fr['render'])
    else:
        im = Image.open(ROOT / fr['src'][0])
    im.load()
    if 'crop' in fr:
        im = im.crop(fr['crop'])
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        if im.getchannel('A').getextrema() == (255, 255):
            im = im.convert('RGB')
    elif im.mode != 'RGB':
        im = im.convert('RGB')
    if mode == 'png-crop':
        out = stem.with_suffix('.png')
        im.save(out, 'PNG', optimize=True)
    elif mode == 'lossless':
        out = stem.with_suffix('.webp')
        im.save(out, 'WEBP', lossless=True, quality=100, method=6)  # метаданные исходника не переносятся
    else:
        raise ValueError(mode)
    return out, im.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ui-ref', required=True, help='папка с PNG из tools/render_ui_ref.py')
    args = ap.parse_args()
    man = load_manifest()
    FRAMES_DIR.mkdir(exist_ok=True)
    index, total, total3d, written = [], 0, 0, set()
    for fr in FRAMES:
        sources = []
        for s in fr['src']:
            sha = sha256_file(ROOT / s)
            if man.get(s) != sha:
                sys.exit(f'sha256 не совпадает с заморозкой: {s}')
            sources.append({'path': s, 'sha256': sha})
        out, size = encode(fr, args.ui_ref)
        written.add(out.name)
        nbytes = out.stat().st_size
        total += nbytes
        total3d += nbytes if fr['is3d'] else 0
        compressed = fr['mode'] == 'lossless'
        conv = {'orig': 'оригинал базы байт в байт', 'png-crop': 'вырезка PNG без потерь',
                'lossless': 'WebP без потерь (пиксели совпадают с исходником)'}[fr['mode']]
        parts = [fr['notes'], fr['why'], f'Кадр {size[0]}×{size[1]}, {conv}, {nbytes / 1024:.0f} КБ.']
        index.append({
            'id': fr['id'], 'file': f'frames/{out.name}', 'compressed': compressed, 'pair': fr['pair'],
            'base': fr['base'], 'kind': fr['kind'], 'level': fr['level'], 'illustrates': fr['illustrates'],
            'assessment': fr['assessment'], 'look_at': fr['look_at'], 'rubric': fr['rubric'],
            'source': sources, 'provenance': fr['provenance'], 'notes': ' '.join(x for x in parts if x),
            '_is3d': fr['is3d'],
        })
        print(f"{fr['id']} {fr['kind']:6} {fr['mode']:8} {size[0]:5}×{size[1]:<5} {nbytes / 1024:7.1f} КБ  {out.name}")
    # устаревшие файлы прошлых сборок не удаляем (правило брифа) — переносим в _superseded/
    sup = CAL / '_superseded'
    for f in sorted(FRAMES_DIR.iterdir()):
        if f.is_file() and f.name not in written:
            sup.mkdir(exist_ok=True)
            shutil.move(str(f), str(sup / f.name))
            print('перенесён в _superseded/:', f.name)
    head = ('# Калибровочный набор design-deep-dive: кадры «уровней» и «типичного брака» с разметкой.\n'
            '# Собран tools/build.py (26.09.2026) из замороженной базы; source.sha256 сверен с freeze/manifest.tsv.gz.\n'
            '# Пути rubric — в раскладке шаблона (kb/<база>/…); source.path — от /home/mm/Документы/app-design/.\n'
            '# compressed: true — WebP без потерь; false — оригинал базы байт в байт или вырезка PNG без потерь\n'
            '# (3D и листы с усилением — оригиналы по решению заказчика; прочее — при любом сомнении в сжатии).\n')
    clean = [{k: v for k, v in x.items() if not k.startswith('_')} for x in index]
    with open(CAL / 'index.yaml', 'w', encoding='utf-8') as f:
        f.write(head)
        yaml.safe_dump({'frames': clean}, f, allow_unicode=True, sort_keys=False, width=110,
                       default_flow_style=False)
    stats = {'n': len(index), 'total_bytes': total, 'bytes_3d': total3d, 'bytes_other': total - total3d,
             'n_3d': sum(1 for x in index if x['_is3d']),
             'n_compressed': sum(1 for x in index if x['compressed']),
             'uncompressed': [(x['id'], x['file']) for x in index if not x['compressed']]}
    json.dump(stats, open(CAL / 'tools/.last_build.json', 'w'), ensure_ascii=False, indent=1)
    print(f"итого {len(index)} кадров, {total / 2**20:.2f} МБ (3D-оригиналы {total3d / 2**20:.2f} МБ, "
          f"прочее {(total - total3d) / 2**20:.2f} МБ)")
    write_contact_sheet(index, total, total3d)



# Разделы отчёта для страницы: субагенту запрещено писать отчётные .md-файлы, поэтому суть REPORT.md — здесь,
# полный текст REPORT.md агент вернул оркестратору в ответе.
REPORT_HTML = """
<section id="report">
  <h2>Решения, хранение, находки, вопросы</h2>
  <div class="notes-grid">
  <div class="panel">
    <h3>Откуда кадры</h3>
    <p>Из 50 кандидатов §11 взято 24 → 27 кадров. Добор — 13 кадров из тех же или соседних прогонов: № 01, 02 (кадры сцены J/04
    вместо листов № 4/5), 04 («после» к № 03), 13–15 (свой рендер эталонных HTML ui: 7 экранов в двух темах, взяты 3), 21 (E-15, NB2),
    26 (E-02, Sunburst), 32 (лист телефона фазы 1 вместо № 40), 36 (галерея blender), 37, 39, 40 (пары J/02 в исходном разрешении).</p>
    <h3>Хранение (решение заказчика 26.09)</h3>
    <p><b>compressed: false — 31 кадр.</b> 3D — оригиналы байт в байт: № 01–04, 28–40 (8,2 МБ). Листы с картой разницы — № 21, 22.
    JPEG-исходники не-3D — № 05, 06, 16, 17, 20, 25–27: WebP q94 сглаживал зерно (стена № 17 −25 %, фон баннеров −40 %) и сдвигал
    цвет тонких штрихов (№ 20: ΔE76 p95 6,3). Вырезки PNG без потерь — № 07, 08, 23, 24. <b>compressed: true — 9 кадров:</b>
    WebP без потерь, пиксели совпадают (№ 09–15, 18, 19). Первая сборка в WebP q92–94 отменена: на тёмных градиентах 3D он снимал
    дизеринг и давал полосы, сглаживал искры; её файлы — в <code>_superseded/</code>, не удалены.</p>
  </div>
  <div class="panel">
    <h3>Решения с причиной</h3>
    <ul>
      <li>Фигура инженера на изометрии «Сдано» (№ 31, в полумраке № 33, 34) — безликий белый манекен из примитивов ≈ 60 px, без лица и
      кистей: условный знак масштаба, а не синтетический человек — оставлен (вопрос 1).</li>
      <li>§11 № 23, 24 — интерьер без людей, взяты (№ 19, 18); № 25 — руки и лица, исключён.</li>
      <li>№ 30 (гибрид) — брак неподвижного кадра; страницу C целиком заказчик вживую выбрал лучшей — это в notes.</li>
      <li>E-12 (№ 20): сила «мнение», а не «голос вслепую», как в §11 — голоса в записях базы нет.</li>
      <li>Кадры одной пары хранятся одинаково — сжатие не сдвигает сравнение.</li>
    </ul>
    <h3>Находки при отборе</h3>
    <ul>
      <li>Эталонный дашборд ui: <code>.card + .card { margin-top }</code> в сетке сдвигает карточки на 16 px, легенда с серией
      без столбцов; ui_audit — 0 FAIL (№ 13). База заморожена — кандидат в правки внутри шаблона.</li>
      <li>В уровнях пресета A (<code>gen-b1</code>, <code>gen-b3</code>) активен «Обзор» вместо текущей страницы.</li>
      <li>Рецепт blender 01 и FX t1 — кейс в размерах AirPods Pro: узнаваемый чужой дизайн в эталоне, который поедет в kb.</li>
      <li>SC-04 и F-01: входы — фото Poly Haven; <code>blind-icons.jpg</code> — айдентика MARÉA; лист № 10 — артефакт склейки;
      № 49 — «вне кадра» на листе видов не виден.</li>
    </ul>
  </div>
  <div class="panel">
    <h3>Резерв (можно вернуть)</h3>
    <p>§11 № 11, 12 (счётчик WebKit), 28 (утечка S14), 31 (аутпейнт), 41 (клавиатура L1), 42 (Velmora — ничья), 47 (мелкий брак кода),
    пара «ракета» из J/02.</p>
    <h3>Вопросы заказчику</h3>
    <ol>
      <li>Фигуру-манекен (№ 31, 33, 34) оставить или исключить по Р56? Исключение — минус 2 уровня и 1 брак.</li>
      <li>Добавить пару-ничью Velmora (Blender против Kling, 4 ничьи из 4) — +2 уровня: калибрует «ничью», когда нейросеть эффектнее?</li>
      <li>Можно удалить <code>_superseded/</code> (30 WebP отменённой сборки, 2,9 МБ)? По брифу я ничего не удаляю.</li>
      <li><code>tools/</code> (сборщик, рендер ui) — переносить в шаблон рядом с набором или оставить в журнале сборки?</li>
    </ol>
  </div>
  </div>
</section>
"""

# ------------------------------------------------------------------ контактный лист
BASE_TITLES = [('creative', 'creative — страницы и эффекты'), ('ui', 'ui — экраны интерфейса'),
               ('ai-media', 'ai-media — генерации изображений'), ('blender', 'blender — 3D и рендер')]


def esc(s):
    return html.escape(s, quote=True)


def rich(s):
    """Экранирует текст и превращает `…` в <code>…</code>."""
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', esc(s))


def mb(n):
    return f'{n / 2**20:.1f}'.replace('.', ',')


def write_contact_sheet(index, total, total3d):
    by_base = {b: [x for x in index if x['base'] == b] for b, _ in BASE_TITLES}
    rows = []
    for b, _ in BASE_TITLES:
        lv = sum(1 for x in by_base[b] if x['kind'] == 'level')
        df = sum(1 for x in by_base[b] if x['kind'] == 'defect')
        rows.append(f'<tr><th scope="row">{b}</th><td>{lv}</td><td>{df}</td><td>{lv + df}</td></tr>')
    lv_all = sum(1 for x in index if x['kind'] == 'level')
    df_all = len(index) - lv_all
    rows.append(f'<tr class="sum"><th scope="row">всего</th><td>{lv_all}</td><td>{df_all}</td><td>{len(index)}</td></tr>')

    sections = []
    for b, title in BASE_TITLES:
        cards = []
        for x in by_base[b]:
            kind = 'Уровень' if x['kind'] == 'level' else 'Брак'
            lvl = '' if x['level'] == 'n/a' else f" {x['level']}"
            pair = f'<span class="tag">пара: {esc(x["pair"])}</span>' if x['pair'] else ''
            src = '<br>'.join(esc(s['path']) for s in x['source'])
            rub = '<br>'.join(esc(r) for r in x['rubric'])
            cards.append(f'''
<article class="card {x['kind']}" id="f{x['id']}">
  <a class="thumb" href="{esc(x['file'])}" target="_blank" rel="noopener" title="Открыть кадр целиком">
    <img src="{esc(x['file'])}" alt="Кадр {x['id']}: {esc(x['illustrates'][:90])}" loading="lazy">
  </a>
  <div class="meta">
    <p class="head"><span class="num">№ {x['id']}</span> <span class="kind">{kind}{lvl}</span>
      <span class="tag">{esc(x['base'])}</span>{pair}</p>
    <p class="slug">{esc(x['file'].split('/')[-1])} · {'WebP без потерь' if x['compressed'] else ('3D, оригинал' if x['_is3d'] else ('вырезка PNG без потерь' if x['file'].endswith('.png') and 'Вырезка' in x['notes'] else 'оригинал'))}</p>
    <p><b>Что:</b> {rich(x['illustrates'])}</p>
    <p><b>Смотреть:</b> {rich(x['look_at'])}</p>
    <p class="small"><b>Оценка:</b> {rich(x['assessment'])}</p>
    <details><summary>Рубрика, источник, примечания</summary>
      <p class="small"><b>Рубрика:</b><br>{rub}</p>
      <p class="small"><b>Источник:</b><br>{src}</p>
      <p class="small"><b>Происхождение:</b> {rich(x['provenance'])}</p>
      <p class="small"><b>Примечания:</b> {rich(x['notes'])}</p>
    </details>
  </div>
</article>''')
        sections.append(f'<section><h2>{esc(title)}</h2><div class="grid">{"".join(cards)}</div></section>')

    ex_rows = ''.join(
        f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class="path">{esc(c)}</td><td>{rich(d)}</td><td>{esc(e)}</td></tr>'
        for a, b, c, d, e in EXCLUDED)

    page = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Калибровочный набор</title>
<style>
  :root {{
    --bg: #f4f5f7; --panel: #ffffff; --ink: #16181d; --muted: #5b6270; --line: #dfe2e8;
    --level: #1f7a4d; --level-bg: #e7f4ec; --defect: #b3261e; --defect-bg: #fbe9e7; --thumb: #e9ebef;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink);
    font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans", sans-serif; }}
  header, main, footer {{ max-width: 1400px; margin: 0 auto; padding: 0 20px; }}
  header {{ padding-top: 28px; }}
  h1 {{ font-size: 26px; margin: 0 0 6px; }}
  h2 {{ font-size: 20px; margin: 36px 0 14px; padding-top: 8px; border-top: 1px solid var(--line); }}
  .lead {{ color: var(--muted); max-width: 980px; margin: 0 0 16px; }}
  .summary {{ display: flex; gap: 28px; flex-wrap: wrap; align-items: flex-start; }}
  table {{ border-collapse: collapse; background: var(--panel); }}
  th, td {{ border: 1px solid var(--line); padding: 6px 10px; text-align: left; vertical-align: top; }}
  .balance td {{ text-align: right; min-width: 64px; }}
  .balance tr.sum {{ font-weight: 600; }}
  .legend {{ max-width: 640px; color: var(--muted); font-size: 14px; margin: 0; }}
  .legend b {{ color: var(--ink); }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 16px; }}
  .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 6px; overflow: hidden;
    display: flex; flex-direction: column; border-top: 4px solid var(--level); }}
  .card.defect {{ border-top-color: var(--defect); }}
  .thumb {{ display: block; background: var(--thumb); height: 280px; }}
  .thumb img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
  .meta {{ padding: 10px 14px 14px; }}
  .meta p {{ margin: 0 0 6px; }}
  .head {{ display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; }}
  .num {{ font-weight: 700; font-size: 17px; }}
  .kind {{ font-weight: 600; color: var(--level); }}
  .card.defect .kind {{ color: var(--defect); }}
  .tag {{ color: var(--muted); font-size: 13px; border-left: 1px solid var(--line); padding-left: 8px; }}
  .slug {{ color: var(--muted); font-size: 13px; word-break: break-all; }}
  .small {{ font-size: 13.5px; color: #2c313a; }}
  details summary {{ cursor: pointer; color: var(--muted); font-size: 13.5px; margin-top: 4px; }}
  .notes-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(380px, 100%), 1fr)); gap: 16px; }}
  .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 4px 16px 10px; }}
  .panel h3 {{ font-size: 16px; margin: 12px 0 6px; }}
  .panel p, .panel li {{ font-size: 14.5px; }}
  .panel ul, .panel ol {{ padding-left: 20px; margin: 0 0 8px; }}
  .scroll {{ overflow-x: auto; }}
  .excluded {{ min-width: 760px; }}
  .excluded td {{ font-size: 14px; }}
  code {{ font-size: 0.92em; background: #eef0f3; padding: 0 3px; border-radius: 3px; }}
  .excluded .path {{ word-break: break-all; color: var(--muted); }}
  footer {{ color: var(--muted); font-size: 13px; padding: 28px 20px 40px; }}
  @media (max-width: 520px) {{ .grid {{ grid-template-columns: 1fr; }} .thumb {{ height: 220px; }} }}
</style>
</head>
<body>
<header>
  <h1>Калибровочный набор: уровни и типичный брак</h1>
  <p class="lead">40 кадров для модели-судьи и агентов design-deep-dive: свои рендеры и генерации баз, без Qwen 2.1 и без
  синтетических людей. Ценнее всего пары, где «богаче» — хуже или брак не виден глазом (урок J/02). Клик по кадру открывает
  его целиком. Размер набора — {mb(total)} МБ: 3D-оригиналы {mb(total3d)} МБ, прочее
  {mb(total - total3d)} МБ (3D, листы с усилением и спорные при сжатии кадры лежат оригиналами). Разметка — <a href="index.yaml">index.yaml</a>; решения, находки и вопросы —
  <a href="#report">в конце страницы</a>.</p>
  <div class="summary">
    <table class="balance" aria-label="Баланс по базам">
      <thead><tr><th scope="col">база</th><th scope="col">уровень</th><th scope="col">брак</th><th scope="col">кадров</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    <p class="legend"><b>Сила оценки</b> (в поле «Оценка»): ворота — автоматический порог; метрика — замер; голос вслепую —
    заказчик выбирал, не зная варианта; один судья — оценка одного агента по рубрике; мнение — глазами без рубрики.
    <b>Пара</b> — кадры с общим id сравниваются между собой. Листы сравнения (№ 20, 32, 35, 36) размечены по главному
    тезису: эталон — на том же листе.</p>
  </div>
</header>
<main>
{''.join(sections)}
{REPORT_HTML}
<section>
  <h2>Кандидаты, не вошедшие в набор</h2>
  <div class="scroll"><table class="excluded">
    <thead><tr><th scope="col">кандидат</th><th scope="col">база</th><th scope="col">файл (от корня базы)</th>
    <th scope="col">причина</th><th scope="col">тип</th></tr></thead>
    <tbody>{ex_rows}</tbody>
  </table></div>
</section>
</main>
<footer>Собрано tools/build.py 26.09.2026 из замороженной базы (sha256 источников сверены с freeze/manifest.tsv.gz).
Страница ссылается на кадры относительными путями и ничего не встраивает.</footer>
</body>
</html>
'''
    (CAL / 'contact-sheet.html').write_text(page, encoding='utf-8')


if __name__ == '__main__':
    main()
