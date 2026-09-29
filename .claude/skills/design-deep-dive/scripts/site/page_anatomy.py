#!/usr/bin/env python3
"""page_anatomy.py — анатомия живой посадочной страницы или страницы сайта: структура, призывы, формы, согласия, скорость, вес.

Что меряет (Playwright + Chromium 153, один браузер на прогон, одна страница × одно устройство):
  1. загрузка: десктоп 1440×900 DPR 1 или --mobile (дескриптор и CPU — budgets.yaml site conditions.lab_mobile: Pixel 7,
     CPU ×4; UA — HeadlessChrome, автоматизация не маскируется); load → окно первого экрана (conditions.first_screen, --wait)
     → снимок первого экрана → cookie-баннер → попапы → прокрутка колесом до конца → возврат наверх → разбор DOM;
  2. cookie-баннер: известные платформы согласия (OneTrust, Cookiebot, Didomi, Usercentrics, Klaro, CookieYes, iubenda,
     Quantcast, TrustArc, Osano, Complianz, баннер Tilda и др.) и текстовые эвристики RU/EN; запись: есть ли «Отклонить» на
     первом слое, равны ли кнопки, модальность, доля экрана, запросы аналитики и cookie ДО выбора; действие: «Отклонить»
     → «Закрыть ×» → скрыть CSS без согласия. «Принять» утилита НЕ нажимает (согласие — решение пользователя; без
     разрешения заказчика не нажимаем) — поле cmp_action: reject | close | hidden | none | kept (--no-cmp-close);
  3. секции: развёртка обёрток (≥ 2 «полос» шириной ≥ 50 % экрана; обёртка — ≥ 2 полос с заголовком уровня секции,
     разные фоны или высота > 2,2 экрана), Tilda `.t-rec`, приклейка «только заголовок» к следующей полосе и мелких полос к
     предыдущей, шапка и подвал отдельно; для секции — позиция, высота, заголовки, слова, призывы, поля форм, медиа,
     повторяющиеся карточки, числа, цены, цитаты, время, шаги, карта, слайдер, аккордеон; класс — роль (`section_role`) и
     блок (`block`) по словарю site (02-site-types/vocabulary.yaml) с баллами top-3 и признаками (пересчёт без замера:
     --reclassify);
  4. призывы (CTA): текст, сила (primary: заявка, запись, купить…; secondary: подробнее…), вид (заливка, контур, ссылка),
     место (шапка, первый экран, секция, липкий, подвал), цель (tel, mailto, мессенджер, якорь, попап, внешняя, внутренняя,
     кнопка формы), повторы;
  5. формы (ничего не вводит и не отправляет): поля по типам, autocomplete, обязательные, шаги и квизы, чекбоксы согласий
     (ПД, рассылка, общий; отмечены ли заранее), текст-уведомление «нажимая кнопку…», ссылка на политику, капча
     (reCAPTCHA, SmartCaptcha, hCaptcha, Turnstile), ловушки honeypot, формы в попапах;
  6. шапка и подвал: пункты меню, подменю и мега-меню, липкость (проверка после прокрутки), прозрачность над hero, телефон,
     мессенджеры, CTA, кнопка меню; подвал — ссылки, группы, реквизиты (ИНН, ОГРН), политика, соцсети, ©;
  7. заголовки и мета: h1 (число, текст), пропуски уровней, lang, title, description, canonical, robots, Open Graph, Twitter,
     hreflang, фавиконы, типы JSON-LD и microdata, платформа сайта;
  8. сеть через CDP: байты первого экрана (load + простой, до действий) и сессии, по категориям; сторонние домены по
     категориям (аналитика, тег-менеджер, пиксели, чаты, колл-трекинг, запись и квизы, капча, CMP, шрифты, видео, карты…);
     запросы трекинга до выбора в баннере; имена cookie (без значений) до и после выбора;
  9. скорость: LCP (элемент, время, до прокрутки), CLS (до прокрутки и за сессию), TBT (до прокрутки), FCP и TTFB
     (web-vitals); показ H1 во времени (h1_paint: прозрачность в первом кадре, когда H1 стал виден и непрозрачен — признак
     SG-PERF-06 для страниц, где HTML признаков не несёт); --inp — лабораторный INP по сценарию: меню → CTA-якорь →
     раскрыть FAQ → фокус в поле формы без ввода (web-vitals onINP, attribution, reportAllChanges, durationThreshold 16 +
     свой наблюдатель Event Timing); --crux — поле CrUX через PageSpeed Insights API (ключ только из окружения PSI_API_KEY,
     не печатается; без ключа квота API = 0 — пишется ответ сервера);
 10. текст без JS: тело ответа главного документа (что сервер отдал браузеру) против отрисованного DOM — доля слов, h1,
     текст главного CTA, цены, заголовки секций, title и description, JSON-LD.

Запуск (замер — на тихой машине: утилита берёт общий тяжёлый замок, замок браузера и замок site — page_gates.heavy_lock;
--no-lock — обёртка их уже держит; не дольше 5 мин на страницу). Код репозитория — соседним чекаутом
../strategy/.claude/skills/design-deep-dive/scripts/site/page_anatomy.py:
  page_anatomy.py URL OUT_DIR [--mobile] [--inp] [--quick] [--no-cmp-close] [--label PAGE_TYPE]
          [--id ID] [--market ru|intl] [--industry X] [--net [auto|ru-direct|vpn-lt|unknown]] [--site-type X]
          [--text-id X] [--template X] [--site-id X] [--timeout 60] [--wait МС] [--cpu N] [--crux] [--no-lock]
  page_anatomy.py --batch pages.tsv --out DIR [--devices desktop,mobile] [--inp] [--only a,b]
          [--skip-done]                      # замки тишины — на каждую страницу × устройство, free ≥ 3 ГБ
  page_anatomy.py --reclassify DIR   # пересчитать классы секций в готовых JSON без браузера
  page_anatomy.py --csv DIR --pages pages.tsv > pages.csv
  page_anatomy.py --net-of HOST [HOST…]   # страна и организация IP сервера (IP не печатается)
  page_anatomy.py --selftest          # локальная тестовая страница во временной папке, без сети
Сеть — только ключом --net: без него замер к сторонним сервисам не обращается (поле net: unknown); --net или --net auto —
страна и организация сервера (ipinfo.io, IP не сохраняется) и проверка раздельной маршрутизации VPN (yandex.ru и
ipinfo.io до и после замера); --net <метка> — своя метка сети и та же проверка маршрута.
Выход: OUT_DIR/anatomy_<desktop|mobile>.json, sheet_<устройство>.jpg (контактный лист секций с подписями),
cmp_<устройство>.jpg (кадр с cookie-баннером, если найден), краткая сводка в stdout.
Ограничения: лаборатория ≠ поле; одна сеть (поле net — метка или проверка с --net); Chromium headless; эмуляция
телефона; антибот (страница-заглушка помечается blocked); INP — только сценарий из 4 взаимодействий после загрузки;
классификатор секций — эвристики: роль и блок — кандидаты top-3 с баллами.
"""
import argparse, contextlib, csv, fcntl, http.server, io, json, os, re, socket, socketserver, statistics, subprocess, sys
import threading, time, urllib.parse, urllib.request
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('site'))
WV_IIFE = str(kbpaths.node_modules('web-vitals', 'dist', 'web-vitals.attribution.iife.js'))
kbpaths.use('site')
import page_gates as PG  # noqa: E402  условия замера, окно первого экрана, тишина машины (budgets.yaml)
TOOL = 'page_anatomy.py 1.2'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

# автоматизация не маскируется: без --disable-blink-features и подмены UA (navigator.webdriver виден сайту)
GPU_ARGS = ["--use-gl=angle", "--use-angle=gl", "--ignore-gpu-blocklist", "--enable-gpu", "--autoplay-policy=no-user-gesture-required"]

# ------------------------------------------------------------------------------------------------ словари признаков
# Призывы: сила primary — глагол целевого действия; secondary — переход «узнать больше». Регэкспы — для JS (флаг i).
CTA_PRIMARY = (r"заявк|заказ|запис|купит|куплю|покупк|оформит|получит|рассчит|расчет|расчёт|посчита|узнать (цену|стоимость|сколько)|"
               r"консультац|позвон|звонок|перезвон|оставить|отправит|начать|начни|попробова|зарегистр|регистрац|скачат|"
               r"подписат|подпишит|забронир|бронир|вызват|связат|напиши|написать|демо|тест-драйв|подобрат|подбор|"
               r"присоедин|вступит|участвоват|принять участие|билет|оплатит|в корзину|получить доступ|бесплатн|воспользова|"
               r"замер|смет[ау]|выезд|проконсульт|записаться|вызов |хочу |"
               r"get started|start (free|now|trial|for free|building|your)|try |try$|sign up|signup|book|buy|order|request|"
               r"contact (sales|us)|talk to|get (a )?(demo|quote|access|in touch|the app|early access|it)|download|subscribe|join|"
               r"register|schedule|apply|claim|reserve|enroll|enrol|install|add to|create (an? )?(free )?account|free trial|"
               r"waitlist|wait list|notify me|pre-?order|rsvp|call now|call us|call today|message us|whatsapp|telegram|estimate|quote|inspection|"
               r"consultation|appointment|get your|claim your|shop now|buy now|start now|start today|contact$|^contact us|let.s talk|speak to|"
               r"book a|request a|get pricing|get offer|see (it|a) demo|watch (the )?demo|try (it )?(free|now)|sign in with|continue with")
CTA_SECONDARY = (r"подробн|узнать больше|узнать|смотреть|посмотреть|читать|все услуги|все работы|все кейсы|все отзывы|"
                 r"каталог|перейти|открыть|показать|ещ[её]|далее|learn more|read more|see (more|all|how|pricing|plans)|"
                 r"explore|view|watch|discover|details|more info|how it works|compare|pricing|tour")
MESSENGER_RE = r"wa\.me|whatsapp|t\.me/|telegram\.(me|org)|tg://|viber:|vk\.me|vk\.com/(write|im)|max\.ru|icq\.im|m\.me/|skype:"

# Роли секций: (регэксп заголовка/идентификатора, регэксп текста). Баллы: заголовок ×4, id/class ×3, текст ×1 (до 3 совпадений).
ROLE_KW = {
    'faq': (r"faq|част\w* (задаваем\w* )?вопрос|вопрос\w*[ -]и[ -]ответ|ответ\w* на (частые )?вопрос|frequently asked|\bquestions?\b|"
            r"остались вопросы|есть вопросы|вопросы", r"\?"),
    'testimonials': (r"отзыв|testimonial|review|говорят (о нас|клиенты)|клиенты о нас|мнени\w* клиент|что говорят|what (our )?"
                     r"(customers|clients|users|people) (say|think)|loved by|благодарност|рекомендац", r"отзыв|review|★|⭐"),
    'pricing': (r"тариф|цен[аыу]\b|цены|стоимост|прайс|сколько стоит|price|pricing|plans?\b|подписк|оплат|abonement|абонемент",
                r"₽|руб\.?|\$|€|/\s?мес|per month|/mo\b|месяц"),
    'how-it-works': (r"как (мы )?(работаем|это работает|проходит|устроен|начать|заказать|получить|всё происходит|это происходит)|"
                     r"этап\w*|шаг\w*|порядок работы|схема работы|процесс|how (it|we) work|steps?\b|process|getting started|"
                     r"как стать|как записаться|алгоритм", r"шаг \d|этап \d|step \d"),
    'team': (r"команд|специалист|врач|доктор|эксперт|преподават|тренер|мастер\w* |наши люди|сотрудник|спикер\w* курса|"
             r"team|our people|experts|doctors|instructors|founders|leadership|кто (будет )?(вас )?(вести|учить|работать)",
             r"опыт работы|стаж|лет опыта|years of experience"),
    'portfolio': (r"портфолио|наши работы|примеры (наших )?работ|реализованн|выполненн|проект[ыов]|галере|фото (работ|объектов)|"
                  r"portfolio|our work|projects|showcase|gallery|selected work", r""),
    'case-studies': (r"кейс|истори\w* (успеха|клиентов)|результат\w* (клиентов|учеников|выпускников)|case stud|success stor|"
                     r"customer stor|results", r"задача|решение|результат"),
    'contacts': (r"контакт|как (нас )?найти|как добраться|адрес|приезжайте|мы на карте|где мы|офис|contact|find us|visit us|"
                 r"get in touch|location", r"ул\.|улица|проспект|пр-т|д\. ?\d|офис \d|street|ave\b|suite|\+7|8 \(\d{3}\)"),
    'about': (r"о (нас|компании|клинике|школе|студии|бюро|центре|проекте|себе|бренде)|кто мы|наша истори|истори\w* компании|"
              r"миссия|about( us)?|our story|who we are|mission|почему мы появились|основател", r"основан|since \d{4}|с \d{4} года|лет на рынке"),
    'benefits': (r"преимуществ|почему (мы|нас|выбирают|стоит)|выгод|плюсы|возможност|особенност|advantages|why (us|choose)|benefits|"
                 r"features|what you get|что (вы )?получ|чем мы лучше|наши (сильные|принципы)|ценност", r""),
    'product-demo': (r"демо|посмотрите|как (это )?выглядит|интерфейс|видео|обзор|в деле|в работе|demo|in action|watch|product tour|"
                     r"take a tour|screenshot", r""),
    'integrations': (r"интеграц|подключ\w* к|работает с|совместим|integrat|connects? with|works with|plug-?ins|apps? directory",
                     r""),
    'awards-press': (r"наград|преми[яиюй]|рейтинг|сми о нас|о нас пишут|пресс|публикац|лиценз|сертифик|аккредит|сро\b|"
                     r"award|press|featured in|as seen|recognition|certif|licen[cs]", r""),
    'guarantee': (r"гаранти|guarantee|warranty|возврат (денег|средств)|вернем деньги|вернём деньги|без риска|money.back|"
                  r"risk.free|бесплатн\w* (замер|выезд|консультац|диагност)", r"гарант|guarantee"),
    'comparison': (r"сравн|compare|comparison|\bvs\.?\b|альтернатив|alternative|отлича\w* от|чем мы отличаемся|в отличие от|"
                   r"против\b", r"✓|✔|✗|✘"),
    'event-program': (r"программ\w*|расписан|спикер|докладчик|agenda|schedule|speakers|line-?up|модул|урок|curriculum|syllabus|"
                      r"что (вы )?(будете )?изуч|чему (вы )?научит", r"\d{1,2}:\d{2}|модуль|урок|lesson|module"),
    'problem': (r"проблем|боль|знакомо|сталкивались|устали|надоело|мешает|ошибк|трудност|сложност|problem|struggl|pain|"
                r"tired of|frustrat|challenge|без (нас|системы)|почему не получается|что будет, если", r""),
    'solution': (r"решени|мы предлагаем|поможем|мы (делаем|создаем|создаём)|introducing|meet |solution|we help|how we help|"
                 r"что мы (делаем|предлагаем)", r""),
    'objections': (r"сомнева|возражен|а (если|что если|вдруг)|почему (так )?дорого|не уверен|страх|objection|but what if|"
                   r"what if|still not sure|not convinced", r""),
    'related': (r"стать[ия]|блог|новост|читайте|полезн|материал|журнал|медиа|related|blog|articles|news|resources|insights|"
                r"guides|events|мероприяти", r"\d{1,2}\.\d{1,2}\.\d{2,4}|\d{1,2} (янв|фев|мар|апр|мая|июн|июл|авг|сен|окт|ноя|дек)"),
    'offer': (r"что входит|в стоимост\w* входит|услуг[иа]|наши услуги|что мы делаем|направлени|каталог|ассортимент|"
              r"предложени|условия|формат|включено|what.s included|includes|services|what we do|our offer|packages?",
              r"входит|включен|included"),
    'audience': (r"для кого|кому подойд|кому подход|подойд\w* (вам|если)|кому (полезен|нужен|будет)|who (is it|it.s|this is) for|"
                  r"use cases?|сценари|решения для|for (teams|startups|agencies|enterprise|developers|marketers|designers)|"
                  r"built for|отрасл|industries", r""),
    'promo': (r"акци[яи]|скидк|спецпредложени|специальное предложение|только до|осталось|предложение действует|распродаж|"
              r"promo|sale\b|discount|limited|offer ends|% off|подарок|бонус", r"-\d{1,2} ?%|до \d{1,2} (сентября|октября|ноября|декабря)"),
    'specs': (r"характеристик|параметр|технически\w* данн|спецификац|specs|specifications|tech specs|комплектац", r""),
    'proof-stats': (r"в цифрах|цифры|факты|статистик|by the numbers|in numbers|our impact|results in numbers", r""),
    'proof-logos': (r"нам доверяют|наши клиенты|клиенты|партн[её]р|с нами работают|бренды|производител|поставщик|работаем (только )?с|сотруднича|"
                    r"официальн\w* (дилер|партн|представит)|trusted by|our clients|customers|"
                    r"partners|companies (that )?(use|trust)|used by|backed by|инвестор", r""),
    'lead-form': (r"заявк|консультац|оставьте|свяжемся|перезвоним|запишитесь|запись на|рассчитать|расчет|расчёт|узнайте стоимость|"
                  r"получите|заполните|обратн\w* связ|напишите нам|contact us|get in touch|request|book a|schedule|let.s talk|"
                  r"sign up|join the waitlist|get early access", r""),
    'story': (r"манифест|наша философия|manifesto|philosophy|история бренда", r""),
    'legal': (r"не является (публичной )?офертой|имеются противопоказания|проконсультируйтесь|disclaimer|юридическ\w* информац|"
              r"реквизиты", r"ИНН|ОГРН"),
}

# словарь ролей по vocabulary.yaml: общие слова сужены, роли services, cross-sell, final-cta (заголовок у конца страницы)
# — по опыту точности классификатора (site 09-ai-generation-evaluation/02-site-checklist.md §6)
ROLE_KW.update({
    'team': (r"наша команда|команда (\w+ )?(специалистов|экспертов|профессионалов|врачей|преподавателей|мастеров)|о команде|"
             r"наши (специалисты|врачи|мастера|преподаватели|клинеры|эксперты|сотрудники|тренеры)|специалисты (клиники|центра|компании)|"
             r"врач|доктор|преподават|тренер|клинер|кто (будет )?(вас )?(вести|учить|работать|делать|убирать|лечить|приедет)|"
             r"проверенные (клинеры|мастера|специалисты)|our team|meet the team|the team\b|our people|experts|doctors|instructors|founders|leadership",
             r"опыт работы|стаж|лет опыта|years of experience"),
    'about': (r"о (нас|компании|клинике|школе|студии|бюро|центре|проекте|себе|бренде)\b|кто мы|наша истори|истори\w* компании|миссия|"
              r"about us|about (the )?company|our story|who we are|our mission|почему мы появились|основател",
              r"основан|since \d{4}|с \d{4} года|лет на рынке"),
    'offer': (r"что (в )?входит|что не входит|в стоимост\w* входит|включено|условия|\d+ вариант|варианта|what.s included|"
              r"(all|every) (paid )?plans? includes?|includes|our offer|packages?",
              r"входит|включен|included"),
    'event-program': (r"программа (конференции|мероприятия|курса|обучения|форума)|расписан|спикер|докладчик|доклад|темы,? форматы|agenda|"
                      r"schedule|speakers|line-?up|модул|урок|curriculum|syllabus|что (вы )?(будете )?изуч|чему (вы )?научит|"
                      r"образовательн\w* маршрут|учебн\w* план|уровни (обучения|языка)",
                      r"\d{1,2}:\d{2}|модуль|урок|lesson|module"),
    'benefits': (r"преимуществ|почему (мы|нас|выбирают|стоит)|почему \w+\?|причин|выгод|плюсы|возможност|особенност|честн|прозрачн|"
                 r"advantages|why (us|choose)|why \w+\?|benefits|features|what you get|что (вы )?получ|чем мы лучше|наши (сильные|принципы)|ценност", r""),
    'audience': (r"для кого|кому подойд|кому подход|подойд\w* (вам|если)|подходит для|идеально подходит|кому (полезен|нужен|будет)|"
                 r"who (is it|it.s|this is) for|use cases?|сценари|решения для|найдите свою (отрасль|нишу|задачу)|отрасл|industries|"
                 r"for (teams|startups|agencies|enterprise|developers|marketers|designers)|built for|not sure (where|which|what)|"
                 r"не знаете,? (что|какую|какой|с чего)", r""),
    'related': (r"стать[ия]|блог|новост|читайте|полезн|материал|журнал|медиа|смотрите также|см\. также|другие услуги|похожие|"
                r"в других городах|районы|areas we serve|service areas|throughout|neighborhoods|popular areas|other services|related|"
                r"blog|articles|news|resources|insights|guides|events|мероприяти",
                r"\d{1,2}\.\d{1,2}\.\d{2,4}|\d{1,2} (янв|фев|мар|апр|мая|июн|июл|авг|сен|окт|ноя|дек)"),
    'awards-press': (r"наград|преми[яиюй]|рейтинг|сми о нас|о нас пишут|пресс|публикац|лиценз|сертифик|аккредит|сро\b|квалификац|свидетельств|"
                     r"award|press|featured in|as seen|recognition|certif|licen[cs]", r""),
    'guarantee': (r"гаранти|guarantee|warranty|возврат (денег|средств)|вернем деньги|вернём деньги|без риска|money.back|risk.free|"
                  r"бесплатн\w* (замер|выезд|консультац|диагност)|ответственност|commitment", r"гарант|guarantee"),
    'lead-form': (r"заявк|консультац|оставьте|свяжемся|перезвоним|запишитесь|запись на|рассчитать|расчет|расчёт|узнайте стоимость|"
                  r"получите|заполните|обратн\w* связ|напишите нам|калькулятор|рассчитайте|calculator|get a quote|free estimate|"
                  r"contact us|get in touch|request|book a|schedule|let.s talk|sign up|join the waitlist|get early access", r""),
    'testimonials': (r"отзыв|testimonial|review|говорят (о нас|клиенты)|клиенты о нас|мнени\w* клиент|что говорят|руководители о|клиенты о|"
                     r"пользователи о|эксперты о|their words|what (our )?(customers|clients|users|people) (say|think)|loved by|благодарност|рекомендац",
                     r"отзыв|review|★|⭐"),
    'services': (r"наши услуги|услуги|направлени|виды (уборк|работ|услуг)|каталог|программы (для|обучения)|выберите (услугу|программу|формат)|"
                 r"choose the right|our services|services|what we offer|what we do|types of (cleaning|service)",
                 r"подробнее|explore|learn more"),
    'cross-sell': (r"установите приложение|скачайте приложение|мобильн\w* приложени|в (вашем )?кармане|download (the|our) app|get the app|"
                   r"дополнительные (программы|услуги|курсы)|смежные (услуги|предложения)|также (мы )?предлагаем|подарочн\w* (сертификат|карт)|gift cards?",
                   r""),
    'final-cta': (r"готовы (начать|к|попробовать)|ready (for|to)|попробуйте \w+ (прямо )?сейчас|начните (сейчас|бесплатно|работать)|"
                  r"get started today|start your free|давайте начн", r""),
})
ARTICLE_TYPES = {'article-page', 'blog-index-page', 'legal-page', 'case-page', 'about-page', 'faq-page', 'case-list-page'}
SERVICE_TYPES = {'landing-lead-services', 'service-page', 'seo-landing-page', 'home-multipage', 'services-index-page', 'landing-course'}

# Сторонние домены: (регэксп хоста, регэксп пути или '', категория, поставщик). Первое совпадение выигрывает.
TP_RULES = [
    (r"(^|\.)mc\.yandex\.(ru|com|by|kz|uz|com\.tr)$|(^|\.)mc\.webvisor\.(org|com)$", "", "analytics", "yandex-metrika"),
    (r"(^|\.)(www\.|region1\.|ssl\.)?google-analytics\.com$|(^|\.)analytics\.google\.com$", "", "analytics", "ga4"),
    (r"(^|\.)googletagmanager\.com$", "", "tag-manager", "gtm"),
    (r"(^|\.)top-fwz1\.mail\.ru$|(^|\.)top\.mail\.ru$", "", "analytics", "top-mail-ru"),
    (r"(^|\.)counter\.yadro\.ru$", "", "analytics", "liveinternet"),
    (r"(^|\.)clarity\.ms$", "", "analytics", "ms-clarity"),
    (r"(^|\.)hotjar\.(com|io)$", "", "analytics", "hotjar"),
    (r"(^|\.)mixpanel\.com$|(^|\.)mxpnl\.com$", "", "analytics", "mixpanel"),
    (r"(^|\.)amplitude\.com$", "", "analytics", "amplitude"),
    (r"(^|\.)segment\.(com|io)$|(^|\.)segmentapis\.com$", "", "analytics", "segment"),
    (r"(^|\.)plausible\.io$", "", "analytics", "plausible"),
    (r"(^|\.)posthog\.com$", "", "analytics", "posthog"),
    (r"(^|\.)heapanalytics\.com$|(^|\.)heap-api\.com$", "", "analytics", "heap"),
    (r"(^|\.)fullstory\.com$", "", "analytics", "fullstory"),
    (r"(^|\.)matomo\.cloud$", "", "analytics", "matomo"),
    (r"(^|\.)vercel-insights\.com$|(^|\.)vercel-scripts\.com$|(^|\.)vitals\.vercel-analytics\.com$", "", "analytics", "vercel-analytics"),
    (r"(^|\.)cloudflareinsights\.com$", "", "analytics", "cloudflare-web-analytics"),
    (r"(^|\.)usefathom\.com$|(^|\.)fathom\w*\.com$", "", "analytics", "fathom"),
    (r"(^|\.)stats\.wp\.com$|(^|\.)pixel\.wp\.com$", "", "analytics", "wp-stats"),
    (r"(^|\.)sentry\.io$|(^|\.)sentry-cdn\.com$|(^|\.)ingest\.\w+\.sentry\.io$", "", "monitoring", "sentry"),
    (r"(^|\.)nr-data\.net$|(^|\.)newrelic\.com$", "", "monitoring", "newrelic"),
    (r"browser-intake-datadoghq\.(com|eu)$|(^|\.)datadoghq-browser-agent\.com$", "", "monitoring", "datadog"),
    (r"(^|\.)vk\.com$|(^|\.)vk\.ru$", r"/rtrg|/js/api/openapi|/pixel", "ads-pixel", "vk-pixel"),
    (r"(^|\.)ads\.vk\.com$|(^|\.)ad\.mail\.ru$|(^|\.)r\.mail\.ru$|(^|\.)privacy-cs\.mail\.ru$|(^|\.)vk-portal\.net$", "", "ads-pixel", "vk-ads"),
    (r"(^|\.)connect\.facebook\.net$", "", "ads-pixel", "meta-pixel"),
    (r"(^|\.)facebook\.com$", r"^/tr", "ads-pixel", "meta-pixel"),
    (r"(^|\.)doubleclick\.net$|(^|\.)googleadservices\.com$|(^|\.)googlesyndication\.com$|(^|\.)adservice\.google\.", "", "ads-pixel", "google-ads"),
    (r"(^|\.)google\.[a-z.]+$", r"^/(pagead|ads|ccm|rmkt)", "ads-pixel", "google-ads"),
    (r"(^|\.)an\.yandex\.ru$|(^|\.)yandexadexchange\.net$|(^|\.)adfox\.ru$|(^|\.)ads\.adfox\.ru$", "", "ads-pixel", "yandex-ads"),
    (r"(^|\.)bat\.bing\.com$|(^|\.)clarity\.ms$", "", "ads-pixel", "microsoft-ads"),
    (r"(^|\.)snap\.licdn\.com$|(^|\.)px\.ads\.linkedin\.com$", "", "ads-pixel", "linkedin-insight"),
    (r"(^|\.)analytics\.tiktok\.com$", "", "ads-pixel", "tiktok-pixel"),
    (r"(^|\.)static\.ads-twitter\.com$|(^|\.)ads-api\.twitter\.com$|(^|\.)analytics\.twitter\.com$|(^|\.)t\.co$", "", "ads-pixel", "x-pixel"),
    (r"(^|\.)criteo\.(com|net)$", "", "ads-pixel", "criteo"),
    (r"(^|\.)adriver\.ru$|(^|\.)tns-counter\.ru$|(^|\.)mediascope\.net$|(^|\.)weborama\.(fr|com)$|(^|\.)adhigh\.net$|(^|\.)otm-r\.com$", "", "ads-pixel", "ru-adtech"),
    (r"(^|\.)redditstatic\.com$|(^|\.)reddit\.com$", r"pixel|/rp\.gif", "ads-pixel", "reddit-pixel"),
    (r"(^|\.)quantserve\.com$|(^|\.)scorecardresearch\.com$|(^|\.)adsrvr\.org$|(^|\.)taboola\.com$|(^|\.)outbrain\.com$", "", "ads-pixel", "adtech-other"),
    (r"(^|\.)code\.jivosite\.com$|(^|\.)jivosite\.com$|(^|\.)jivo\.ru$|(^|\.)jivochat\.com$|(^|\.)jivo\.chat$", "", "chat", "jivo"),
    (r"(^|\.)bitrix24\.(ru|com|by|kz|de|eu|ua|site|tech)$|(^|\.)b24\w*\.bitrix24\.", "", "chat-crm", "bitrix24"),
    (r"(^|\.)carrotquest\.(io|app)$|(^|\.)carrotquest\.", "", "chat", "carrotquest"),
    (r"(^|\.)intercom\.(io|com)$|(^|\.)intercomcdn\.com$|(^|\.)intercomassets\.com$", "", "chat", "intercom"),
    (r"(^|\.)driftt\.com$|(^|\.)drift\.com$", "", "chat", "drift"),
    (r"(^|\.)crisp\.chat$", "", "chat", "crisp"),
    (r"(^|\.)tawk\.to$", "", "chat", "tawk"),
    (r"(^|\.)livechatinc\.com$|(^|\.)livechat\.com$", "", "chat", "livechat"),
    (r"(^|\.)zdassets\.com$|(^|\.)zendesk\.com$|(^|\.)zopim\.com$", "", "chat", "zendesk"),
    (r"(^|\.)usedesk\.ru$|(^|\.)talk-me\.ru$|(^|\.)webim\.ru$|(^|\.)livetex\.ru$|(^|\.)verbox\.ru$|(^|\.)redhelper\.ru$|"
     r"(^|\.)chatra\.(io|com)$|(^|\.)wazzup24\.(com|ru)$|(^|\.)umnico\.com$|(^|\.)textback\.ru$|(^|\.)streamwood\.ru$|(^|\.)onicon\.ru$",
     "", "chat", "chat-other"),
    (r"(^|\.)hs-scripts\.com$|(^|\.)hubspot\.(com|net)$|(^|\.)hsforms\.(com|net)$|(^|\.)hs-analytics\.net$|(^|\.)hscollectedforms\.net$|"
     r"(^|\.)hs-banner\.com$|(^|\.)usemessages\.com$|(^|\.)hsadspixel\.net$|(^|\.)hubspotusercontent\S*\.net$", "", "marketing-automation", "hubspot"),
    (r"(^|\.)marketo\.(com|net)$|(^|\.)mktoresp\.com$|(^|\.)pardot\.com$|(^|\.)salesforce\.com$|(^|\.)mindbox\.ru$|(^|\.)retailrocket\.(ru|net)$|"
     r"(^|\.)flocktory\.com$|(^|\.)gnezdo\.ru$|(^|\.)sendpulse\.com$|(^|\.)unisender\.com$|(^|\.)getresponse\.com$|(^|\.)klaviyo\.com$|"
     r"(^|\.)list-manage\.com$|(^|\.)chimpstatic\.com$|(^|\.)customer\.io$|(^|\.)convertkit\.com$|(^|\.)clearbit\.com$|(^|\.)6sc\.co$",
     "", "marketing-automation", "martech-other"),
    (r"(^|\.)envybox\.io$|(^|\.)envycrm\.com$|(^|\.)callbackhunter\.com$|(^|\.)leadback\.ru$|(^|\.)callbackkiller\.(ru|com)$|"
     r"(^|\.)perezvoni\.com$|(^|\.)getcall\.ru$|(^|\.)leadhit\.ru$|(^|\.)lptracker\.ru$|(^|\.)pozvonim\.com$|(^|\.)callkeeper\.ru$|"
     r"(^|\.)leadgenic\.ru$|(^|\.)yagla\.ru$|(^|\.)cleversite\.ru$|(^|\.)widget\.me$", "", "callback-widget", "callback-other"),
    (r"(^|\.)calltouch\.ru$", "", "call-tracking", "calltouch"),
    (r"(^|\.)comagic\.ru$|(^|\.)uiscom\.(ru|com)$", "", "call-tracking", "comagic-uis"),
    (r"(^|\.)roistat\.com$", "", "call-tracking", "roistat"),
    (r"(^|\.)callibri\.ru$", "", "call-tracking", "callibri"),
    (r"(^|\.)mango-office\.ru$|(^|\.)mangotele\.com$", "", "call-tracking", "mango"),
    (r"(^|\.)alloka\.ru$|(^|\.)ringostat\.(com|net)$|(^|\.)calltracking\.ru$|(^|\.)zadarma\.com$|(^|\.)telfin\.ru$|(^|\.)callrail\.com$|"
     r"(^|\.)invoca\.net$", "", "call-tracking", "calltracking-other"),
    (r"(^|\.)yclients\.com$", "", "booking", "yclients"),
    (r"(^|\.)dikidi\.(net|ru)$", "", "booking", "dikidi"),
    (r"(^|\.)prodoctorov\.ru$|(^|\.)napopravku\.ru$|(^|\.)docdoc\.ru$|(^|\.)sberhealth\.ru$|(^|\.)medflex\.ru$|(^|\.)infoclinica\.ru$|"
     r"(^|\.)medods\.ru$|(^|\.)ident\.ru$|(^|\.)1c-medicine\.ru$", "", "booking", "med-booking"),
    (r"(^|\.)calendly\.com$|(^|\.)cal\.com$|(^|\.)chilipiper\.com$|(^|\.)savvycal\.com$|(^|\.)hubspot\.com$", r"meetings|", "booking", "calendar-booking"),
    (r"(^|\.)marquiz\.(ru|io)$", "", "quiz", "marquiz"),
    (r"(^|\.)enquiz\.(ru|io)$|(^|\.)quizgo\.(ru|io)$|(^|\.)quiz-?\w*\.(ru|io)$|(^|\.)flexbe\.com$", r"quiz|", "quiz", "quiz-other"),
    (r"(^|\.)typeform\.com$|(^|\.)tally\.so$|(^|\.)jotform\.com$|(^|\.)formspree\.io$|(^|\.)getform\.io$|(^|\.)webask\.io$|(^|\.)anketolog\.ru$",
     "", "forms", "forms-service"),
    (r"(^|\.)forms\.tildaapi\.(com|pro)$|(^|\.)forms\.tildacdn\.(com|pro)$", "", "forms", "tilda-forms"),
    (r"(^|\.)recaptcha\.net$", "", "captcha", "recaptcha"),
    (r"(^|\.)google\.com$|(^|\.)gstatic\.com$", r"recaptcha", "captcha", "recaptcha"),
    (r"(^|\.)smartcaptcha\.yandexcloud\.net$|(^|\.)captcha-api\.yandex\.ru$", "", "captcha", "yandex-smartcaptcha"),
    (r"(^|\.)hcaptcha\.com$", "", "captcha", "hcaptcha"),
    (r"(^|\.)challenges\.cloudflare\.com$", "", "captcha", "turnstile"),
    (r"(^|\.)cookielaw\.org$|(^|\.)onetrust\.com$|(^|\.)cookiepro\.com$", "", "cmp", "onetrust"),
    (r"(^|\.)cookiebot\.(com|eu)$", "", "cmp", "cookiebot"),
    (r"(^|\.)privacy-center\.org$|(^|\.)didomi\.io$", "", "cmp", "didomi"),
    (r"(^|\.)usercentrics\.(eu|com)$", "", "cmp", "usercentrics"),
    (r"(^|\.)cookieyes\.com$|(^|\.)cdn-cookieyes\.com$", "", "cmp", "cookieyes"),
    (r"(^|\.)iubenda\.com$", "", "cmp", "iubenda"),
    (r"(^|\.)termly\.io$", "", "cmp", "termly"),
    (r"(^|\.)consensu\.org$|(^|\.)quantcast\.com$", "", "cmp", "quantcast"),
    (r"(^|\.)trustarc\.com$|(^|\.)truste\.com$", "", "cmp", "trustarc"),
    (r"(^|\.)osano\.com$", "", "cmp", "osano"),
    (r"(^|\.)cookie-script\.com$|(^|\.)consentmanager\.(net|de)$|(^|\.)privacy-mgmt\.com$|(^|\.)sourcepoint\.com$|(^|\.)ketchcdn\.com$|"
     r"(^|\.)transcend-cdn\.com$|(^|\.)cookiefirst\.com$|(^|\.)axept\.io$|(^|\.)termsfeed\.com$|(^|\.)clickio\.com$", "", "cmp", "cmp-other"),
    (r"(^|\.)fonts\.googleapis\.com$|(^|\.)fonts\.gstatic\.com$", "", "fonts", "google-fonts"),
    (r"(^|\.)use\.typekit\.net$|(^|\.)p\.typekit\.net$", "", "fonts", "adobe-fonts"),
    (r"(^|\.)fonts\.bunny\.net$|(^|\.)cloud\.typography\.com$|(^|\.)fast\.fonts\.net$|(^|\.)use\.fontawesome\.com$|(^|\.)kit\.fontawesome\.com$|"
     r"(^|\.)ka-f\.fontawesome\.com$", "", "fonts", "fonts-other"),
    (r"(^|\.)youtube\.com$|(^|\.)youtube-nocookie\.com$|(^|\.)ytimg\.com$|(^|\.)googlevideo\.com$|(^|\.)youtu\.be$", "", "video", "youtube"),
    (r"(^|\.)vimeo\.com$|(^|\.)vimeocdn\.com$", "", "video", "vimeo"),
    (r"(^|\.)rutube\.ru$|(^|\.)rtbcdn\.ru$", "", "video", "rutube"),
    (r"(^|\.)kinescope\.io$", "", "video", "kinescope"),
    (r"(^|\.)vkvideo\.ru$|(^|\.)vk\.com$", r"video_ext|/video", "video", "vk-video"),
    (r"(^|\.)wistia\.(com|net)$|(^|\.)mux\.com$|(^|\.)litix\.io$|(^|\.)loom\.com$|(^|\.)vidyard\.com$|(^|\.)brightcove\.(net|com)$|"
     r"(^|\.)jwplayer\.com$|(^|\.)jwpcdn\.com$|(^|\.)boomstream\.com$|(^|\.)facecast\.net$", "", "video", "video-other"),
    (r"(^|\.)api-maps\.yandex\.ru$|(^|\.)yandex\.ru$", r"map-widget|/maps/|api-maps|constructor", "maps", "yandex-maps"),
    (r"(^|\.)api-maps\.yandex\.ru$|(^|\.)core-renderer-tiles\.maps\.yandex\.net$|(^|\.)maps\.yandex\.net$|(^|\.)enterprise\.api-maps\.yandex\.ru$",
     "", "maps", "yandex-maps"),
    (r"(^|\.)maps\.googleapis\.com$|(^|\.)maps\.gstatic\.com$", "", "maps", "google-maps"),
    (r"(^|\.)google\.com$", r"^/maps", "maps", "google-maps"),
    (r"(^|\.)2gis\.(ru|com)$|(^|\.)api\.2gis\.", "", "maps", "2gis"),
    (r"(^|\.)openstreetmap\.org$|(^|\.)mapbox\.com$|(^|\.)tiles\.stadiamaps\.com$", "", "maps", "maps-other"),
    (r"(^|\.)yandex\.ru$", r"sprav|maps-reviews|reviews-widget", "reviews", "yandex-reviews"),
    (r"(^|\.)trustpilot\.com$|(^|\.)g2\.com$|(^|\.)g2crowd\.com$|(^|\.)capterra\.com$|(^|\.)reviews\.io$|(^|\.)yotpo\.com$|"
     r"(^|\.)elfsight(cdn)?\.com$|(^|\.)otzovik\.com$|(^|\.)flamp\.ru$|(^|\.)prodoctorov\.ru$", "", "reviews", "reviews-widget"),
    (r"(^|\.)optimizely\.com$|(^|\.)visualwebsiteoptimizer\.com$|(^|\.)vwo\.com$|(^|\.)abtasty\.com$|(^|\.)growthbook\.io$|"
     r"(^|\.)launchdarkly\.com$|(^|\.)statsig\.com$|(^|\.)varioqub\.\w+$|(^|\.)uxfeedback\.ru$|(^|\.)convert\.com$", "", "ab-testing", "ab-other"),
    (r"(^|\.)cdnjs\.cloudflare\.com$|(^|\.)cdn\.jsdelivr\.net$|(^|\.)unpkg\.com$|(^|\.)code\.jquery\.com$|(^|\.)ajax\.googleapis\.com$|"
     r"(^|\.)(stackpath|maxcdn)\.bootstrapcdn\.com$|(^|\.)polyfill\.io$|(^|\.)cdn\.polyfill\.io$|(^|\.)yastatic\.net$", r"", "cdn-lib", "public-cdn"),
    (r"(^|\.)tildacdn\.(com|pro|one|info)$|(^|\.)tildaapi\.(com|pro)$|(^|\.)tilda\.(ws|cc)$|(^|\.)tildastatic\.com$", "", "platform", "tilda"),
    (r"(^|\.)website-files\.com$|(^|\.)webflow\.(com|io)$", "", "platform", "webflow"),
    (r"(^|\.)framerusercontent\.com$|(^|\.)framer\.(com|website|app|media)$|(^|\.)framercdn\.com$", "", "platform", "framer"),
    (r"(^|\.)wixstatic\.com$|(^|\.)parastorage\.com$|(^|\.)wix\.com$|(^|\.)wixapps\.net$", "", "platform", "wix"),
    (r"(^|\.)squarespace(-cdn)?\.com$|(^|\.)sqspcdn\.com$", "", "platform", "squarespace"),
    (r"(^|\.)cdn\.shopify\.com$|(^|\.)shopifycdn\.com$|(^|\.)shopify\.com$", "", "platform", "shopify"),
    (r"(^|\.)readymag\.(com|website)$|(^|\.)rmcdn\d?\.net$", "", "platform", "readymag"),
    (r"(^|\.)lpgenerator\.ru$|(^|\.)flexbe\.(ru|com)$|(^|\.)nethouse\.ru$|(^|\.)ukit\.com$|(^|\.)craftum\.(com|io)$|(^|\.)creatium\.(io|site)$|"
     r"(^|\.)taplink\.(cc|ru)$|(^|\.)ucoz\.(ru|net)$|(^|\.)megagroup\.ru$|(^|\.)insales\.ru$|(^|\.)1c-umi\.ru$|(^|\.)setup\.ru$", "", "platform", "ru-builder"),
    (r"(^|\.)unbounce\.com$|(^|\.)ubembed\.com$|(^|\.)leadpages\.(net|co)$|(^|\.)instapage\.com$|(^|\.)carrd\.co$|(^|\.)hubspotusercontent\S*$",
     "", "platform", "landing-builder"),
    (r"(^|\.)vk\.com$|(^|\.)userapi\.com$|(^|\.)vk\.ru$|(^|\.)mycdn\.me$|(^|\.)ok\.ru$|(^|\.)vk-cdn\.net$|(^|\.)vkuser\.net$", "", "social", "vk-ok"),
    (r"(^|\.)t\.me$|(^|\.)telegram\.org$", "", "social", "telegram"),
    (r"(^|\.)twitter\.com$|(^|\.)x\.com$|(^|\.)twimg\.com$|(^|\.)platform\.twitter\.com$", "", "social", "x"),
    (r"(^|\.)instagram\.com$|(^|\.)cdninstagram\.com$|(^|\.)facebook\.(com|net)$|(^|\.)fbcdn\.net$", "", "social", "meta"),
    (r"(^|\.)linkedin\.com$|(^|\.)licdn\.com$", "", "social", "linkedin"),
    (r"(^|\.)cloudpayments\.ru$|(^|\.)yookassa\.ru$|(^|\.)yoomoney\.ru$|(^|\.)stripe\.com$|(^|\.)js\.stripe\.com$|(^|\.)paypal\.com$|"
     r"(^|\.)paddle\.com$|(^|\.)tinkoff\.ru$|(^|\.)tbank\.ru$", r"", "payments", "payments"),
    (r"(^|\.)google\.[a-z.]+$|(^|\.)gstatic\.com$|(^|\.)googleapis\.com$|(^|\.)googleusercontent\.com$|(^|\.)ggpht\.com$", "", "google-other", "google"),
    (r"(^|\.)yandex\.(ru|net|com|by|kz)$|(^|\.)yastatic\.net$|(^|\.)yandexcloud\.net$|(^|\.)ya\.ru$|(^|\.)yandex-team\.ru$", "", "yandex-other", "yandex"),
    (r"(^|\.)cloudflare\.com$|(^|\.)cloudflare-static\.com$", "", "cdn-lib", "cloudflare"),
    (r"(^|\.)amazonaws\.com$|(^|\.)cloudfront\.net$|(^|\.)akamaihd\.net$|(^|\.)akamaized\.net$|(^|\.)fastly\.net$|(^|\.)azureedge\.net$|"
     r"(^|\.)b-cdn\.net$|(^|\.)storage\.yandexcloud\.net$|(^|\.)selcdn\.ru$|(^|\.)selectel\.ru$|(^|\.)cdnvideo\.ru$|(^|\.)ngenix\.net$",
     "", "cdn-hosting", "cdn-hosting"),
]
TRACKING_CATS = {"analytics", "tag-manager", "ads-pixel", "call-tracking", "marketing-automation", "ab-testing"}
_TP = [(re.compile(h, re.I), re.compile(p, re.I) if p else None, c, v) for h, p, c, v in TP_RULES]
PSL2 = {"co.uk", "org.uk", "ac.uk", "gov.uk", "com.au", "net.au", "org.au", "com.br", "com.tr", "co.jp", "co.kr", "co.in", "com.cn",
        "com.ua", "kiev.ua", "msk.ru", "spb.ru", "com.ru", "net.ru", "org.ru", "pp.ru", "co.il", "com.mx", "com.ar", "co.nz",
        "co.za", "com.kz", "org.kz", "com.by", "com.sg", "com.hk", "com.tw", "co.id", "com.my", "com.pl", "com.es", "co.th"}


def reg_domain(host):
    host = (host or "").lower().strip(".")
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in PSL2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def tp_classify(url):
    try:
        u = urllib.parse.urlsplit(url)
    except Exception:
        return ("other", "")
    host, path = (u.hostname or "").lower(), u.path or "/"
    for hre, pre, cat, vendor in _TP:
        if hre.search(host) and (pre is None or pre.search(path)):
            return (cat, vendor)
    return ("other", "")

# ------------------------------------------------------------------------------------------------ JS: ранние наблюдатели
INIT_JS = r"""(() => {
  if (window.top !== window || window.__pa) return;
  const P = window.__pa = {lcp: [], cls: 0, clsN: 0, lt: [], ev: [], fi: null, inp: null};
  const desc = el => { try { if (!el || el.nodeType !== 1) return null; let s = el.tagName.toLowerCase();
      if (el.id) s += '#' + String(el.id).slice(0, 40); else if (typeof el.className === 'string' && el.className.trim())
      s += '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.').slice(0, 60); return s; } catch (e) { return null; } };
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) { const el = e.element; let txt = null, rect = null;
      try { if (el && !e.url) txt = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80); } catch (x) {}
      try { if (el) { const r = el.getBoundingClientRect(); rect = [Math.round(r.left), Math.round(r.top + scrollY), Math.round(r.width), Math.round(r.height)]; } } catch (x) {}
      P.lcp.push({t: Math.round(e.startTime), size: e.size, tag: el ? el.tagName : null, url: (e.url || '').slice(0, 240), sel: desc(el), text: txt, rect}); } })
    .observe({type: 'largest-contentful-paint', buffered: true}); } catch (e) {}
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) { P.cls += e.value; P.clsN++; } })
    .observe({type: 'layout-shift', buffered: true}); } catch (e) {}
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) P.lt.push([Math.round(e.startTime), Math.round(e.duration)]); })
    .observe({type: 'longtask', buffered: true}); } catch (e) {}
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (e.interactionId) P.ev.push({id: e.interactionId, name: e.name,
      dur: Math.round(e.duration), st: Math.round(e.startTime), ps: Math.round(e.processingStart), pe: Math.round(e.processingEnd), target: desc(e.target)}); })
    .observe({type: 'event', durationThreshold: 16, buffered: true}); } catch (e) {}
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) P.fi = {name: e.name, dur: Math.round(e.duration), st: Math.round(e.startTime)}; })
    .observe({type: 'first-input', buffered: true}); } catch (e) {}
  // показ H1 во времени: прозрачность (произведение по предкам) и видимость каждый кадр от DOMContentLoaded до полной
  // непрозрачности или 15 с; «виден» — прозрачность не ниже __NZ__ (SG-PERF-06 limits.opacity_near_zero)
  const h1s = () => { const h = document.querySelector('h1'); if (!h) return false; let o = 1, n = h, hid = false;
    while (n && n.nodeType === 1) { const cs = getComputedStyle(n); o *= parseFloat(cs.opacity); if (cs.visibility === 'hidden' || cs.display === 'none') hid = true; n = n.parentElement; }
    const r = h.getBoundingClientRect(), t = Math.round(performance.now());
    if (!P.h1) P.h1 = {first_op: Math.round(o * 1000) / 1000, first_hidden: hid, t_first: t, in_first_screen: r.top + scrollY < innerHeight,
                       t_visible: null, t_opaque: null, samples: 0};
    P.h1.samples++;
    if (P.h1.t_visible === null && !hid && o >= __NZ__) P.h1.t_visible = t;
    if (P.h1.t_opaque === null && !hid && o >= 0.99) P.h1.t_opaque = t;
    return P.h1.t_opaque !== null; };
  const tick = () => { if (!h1s() && performance.now() < 15000) requestAnimationFrame(tick); };
  document.addEventListener('DOMContentLoaded', () => requestAnimationFrame(tick));
})();"""


def init_js():
    return INIT_JS.replace('__NZ__', repr(float(PG.gate_limit('SG-PERF-06', 'opacity_near_zero'))))

WV_START_JS = r""";(function(){ if (window.top !== window) return; const P = window.__pa; if (!P) return;
  try { const W = window.__paWV;
    W.onINP(m => { const a = m.attribution || {}; P.inp = {v: Math.round(m.value), rating: m.rating, target: a.interactionTarget || null,
      type: a.interactionType || null, input_delay: Math.round(a.inputDelay || 0), processing: Math.round(a.processingDuration || 0),
      presentation: Math.round(a.presentationDelay || 0), load_state: a.loadState || null}; }, {reportAllChanges: true, durationThreshold: 16});
    W.onLCP(m => { P.wv_lcp = Math.round(m.value); }, {reportAllChanges: true});
    W.onCLS(m => { P.wv_cls = +m.value.toFixed(4); }, {reportAllChanges: true});
    W.onFCP(m => { P.fcp = Math.round(m.value); });
    W.onTTFB(m => { P.ttfb = Math.round(m.value); });
  } catch (e) { P.wv_err = String(e).slice(0, 200); } })();"""


def wv_script():
    """web-vitals (attribution IIFE) в замыкании, чтобы не трогать глобальный webVitals страницы."""
    try:
        code = open(WV_IIFE, encoding='utf-8').read()
    except Exception:
        return None
    code = code.replace('//# sourceMappingURL=web-vitals.attribution.iife.js.map', '')
    return "(function(){ if (window.top !== window) return; " + code + "\n; window.__paWV = webVitals; })();" + WV_START_JS


# ------------------------------------------------------------------------------------------------ JS: cookie-баннер
COOKIE_JS = r"""(opts) => {
  const VW = innerWidth, VH = innerHeight, norm = s => (s || '').replace(/[\s ]+/g, ' ').trim();
  const COOKIE = /cookie|куки|кук(и|ах|ами)\b/i;
  const NOTICE = /(метрическ\w*|яндекс[\s.]*метрик\w*|веб-?аналитик\w*|google analytics)/i;
  const REJ = /отклон|отказ|запрет|не соглас|не принима|reject|decline|deny|refuse|disagree|only (necessary|essential|required)|necessary only|essential only|just necessary|только (необходим|обязательн|технич|функцион)|continue without|продолжить без|without accept|use necessary/i;
  const ACC = /принят|принима|соглас|разреш|allow|accept|agree|got it|i understand|understood|^ok\b|^ок\b|^okay|хорошо|понятно|ясно|^да\b|^yes\b|confirm|подтверд|continue|продолжить|окей/i;
  const SET = /настро|параметр|управл|подробн|выбрать|preferences|settings|customi[sz]e|manage|options|more info|learn more|details|политик|policy|privacy/i;
  const CLOSE = /^(×|✕|✖|x|close|закрыть)$/i;
  const vis = el => { const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return false;
    try { if (el.checkVisibility) return el.checkVisibility({opacityProperty: true, visibilityProperty: true}); } catch (e) {} return true; };
  const KNOWN = [['#onetrust-banner-sdk','onetrust'],['#onetrust-consent-sdk','onetrust'],['#CybotCookiebotDialog','cookiebot'],
    ['#didomi-host','didomi'],['#didomi-popup','didomi'],['#usercentrics-root','usercentrics'],['#usercentrics-cmp-ui','usercentrics'],
    ['.klaro','klaro'],['#cookiescript_injected','cookie-script'],['.cky-consent-container','cookieyes'],['#iubenda-cs-banner','iubenda'],
    ['.qc-cmp2-container','quantcast'],['#truste-consent-track','trustarc'],['.osano-cm-window','osano'],['#cmplz-cookiebanner-container','complianz'],
    ['.cmplz-cookiebanner','complianz'],['.cc-window','cookieconsent'],['.cc-banner','cookieconsent'],['#cookie-law-info-bar','cookie-law-info'],
    ['#moove_gdpr_cookie_info_bar','gdpr-cookie-compliance'],['.t-cookiesbanner','tilda'],['[class*="t-cookie" i]','tilda'],['.hs-cookie-notification-position-bottom','hubspot'],
    ['#hs-eu-cookie-confirmation','hubspot'],['.termly-styles-root','termly'],['#ketch-banner','ketch'],['.fc-consent-root','google-fc'],
    ['[class*="cookie-banner" i]',''],['[class*="cookiebanner" i]',''],['[class*="cookie-consent" i]',''],['[id*="cookie-consent" i]',''],
    ['[class*="cookie_notice" i]',''],['[class*="cookie-notice" i]',''],['[class*="cookies" i]',''],['[class*="cookie" i]',''],['[id*="cookie" i]',''],
    ['[class*="consent" i]',''],['[id*="consent" i]',''],['[class*="gdpr" i]',''],['[aria-label*="cookie" i]',''],['[class*="kuki" i]','']];
  const cands = new Map();
  for (const [sel, v] of KNOWN) { try { document.querySelectorAll(sel).forEach(e => { if (!cands.has(e)) cands.set(e, v); }); } catch (e) {} }
  const all = document.body ? document.body.getElementsByTagName('*') : [];
  for (let i = 0; i < all.length && i < 40000; i++) { const el = all[i]; const c = getComputedStyle(el);
    if (c.position === 'fixed' || c.position === 'sticky') { const t = el.innerText || ''; if (t.length < 3000 && (COOKIE.test(t) || NOTICE.test(t))) if (!cands.has(el)) cands.set(el, '');
      if (el.shadowRoot) { const st = el.shadowRoot.textContent || ''; if (COOKIE.test(st) && !cands.has(el)) cands.set(el, 'shadow'); } } }
  document.querySelectorAll('dialog[open],[role=dialog],[role=alertdialog],[aria-modal=true]').forEach(el => { if (COOKIE.test(el.innerText || '') && !cands.has(el)) cands.set(el, ''); });
  const out = [];
  for (const [el, vendor] of cands) {
    const root = el.shadowRoot || el; const txt = norm((el.shadowRoot ? el.shadowRoot.textContent : el.innerText) || '');
    if (!(COOKIE.test(txt) || (NOTICE.test(txt) && /продолжа|использ|соглаш|пользуясь|continu|using/i.test(txt)))) continue;
    if (txt.length > 4000) continue;
    if (!vis(el) && !el.shadowRoot) continue;
    const r = el.getBoundingClientRect(); if (r.width < 40 || r.height < 16) { if (!el.shadowRoot) continue; }
    out.push({el, root, vendor, txt, r});
  }
  // только внешние (не вложенные в другой кандидат)
  const top = out.filter(o => !out.some(p => p !== o && p.el.contains(o.el)));
  const res = [];
  const btnInfo = (b, bannerBg) => { const r = b.getBoundingClientRect(), c = getComputedStyle(b);
    const t = norm(b.innerText || b.value || b.getAttribute('aria-label') || b.title || '').slice(0, 60);
    const bgm = (c.backgroundColor.match(/[\d.]+/g) || []).map(Number); const filled = bgm.length >= 3 && (bgm.length < 4 || bgm[3] > 0.35);
    let kind = 'other'; if (REJ.test(t)) kind = 'reject'; else if (CLOSE.test(t) || /close|закрыть|dismiss/i.test(b.getAttribute('aria-label') || '')) kind = 'close';
    else if (ACC.test(t)) kind = 'accept'; else if (SET.test(t)) kind = 'settings'; else if (b.tagName === 'A') kind = 'link';
    return {b, t, kind, w: Math.round(r.width), h: Math.round(r.height), fs: parseFloat(c.fontSize), fw: +c.fontWeight || 400, filled,
            bg: c.backgroundColor, color: c.color, border: parseFloat(c.borderTopWidth) || 0, vis: r.width > 1 && r.height > 1}; };
  top.slice(0, 3).forEach((o, i) => {
    const btns = [...o.root.querySelectorAll('button,a[href],[role=button],input[type=button],input[type=submit],[class*=btn i],[class*=button i]')]
      .filter(b => { const r = b.getBoundingClientRect(); return r.width > 1 && r.height > 1; });
    const uniq = btns.filter(b => !btns.some(p => p !== b && p.contains(b) && (p.innerText || '') === (b.innerText || '')));
    const bi = uniq.slice(0, 12).map(b => btnInfo(b));
    const rej = bi.find(x => x.kind === 'reject'), acc = bi.find(x => x.kind === 'accept'), cls = bi.find(x => x.kind === 'close');
    if (i === 0) { if (rej) rej.b.setAttribute('data-pa-cmp', 'reject'); if (cls) cls.b.setAttribute('data-pa-cmp', 'close'); o.el.setAttribute('data-pa-cmp-root', '1'); }
    const vr = o.r; const area = Math.max(0, Math.min(vr.right, VW) - Math.max(vr.left, 0)) * Math.max(0, Math.min(vr.bottom, VH) - Math.max(vr.top, 0)) / (VW * VH);
    let pos = 'other'; if (vr.top <= 4 && vr.height < VH * 0.6) pos = 'top'; else if (vr.bottom >= VH - 4 && vr.height < VH * 0.6) pos = (vr.width < VW * 0.6 ? (vr.left < VW / 2 ? 'bottom-left' : 'bottom-right') : 'bottom');
    else if (vr.left > VW * 0.1 && vr.right < VW * 0.9 && vr.top > VH * 0.1) pos = 'center';
    let eq = null;
    if (rej && acc) { const a1 = acc.w * acc.h, a2 = rej.w * rej.h; eq = {area_ratio: +(a2 / Math.max(1, a1)).toFixed(2), same_fill: acc.filled === rej.filled,
      same_fs: Math.abs(acc.fs - rej.fs) <= 1, same_weight: Math.abs(acc.fw - rej.fw) <= 100, same_bg: acc.bg === rej.bg};
      eq.equal = eq.area_ratio >= 0.7 && eq.area_ratio <= 1.43 && eq.same_fill && eq.same_fs; }
    // затемнение: фиксированный слой почти на весь экран с полупрозрачным фоном
    let backdrop = false; for (let k = 0; k < all.length && k < 40000; k++) { const e = all[k]; if (e === o.el || e.contains(o.el) || o.el.contains(e)) continue; const c = getComputedStyle(e);
      if (c.position !== 'fixed') continue; const rr = e.getBoundingClientRect(); if (rr.width >= VW * 0.95 && rr.height >= VH * 0.95) { const m = (c.backgroundColor.match(/[\d.]+/g) || []).map(Number);
        if (m.length === 4 && m[3] > 0.1 && m[3] < 0.95) { backdrop = true; if (i === 0) e.setAttribute('data-pa-cmp-root', '1'); break; } } }
    const html = getComputedStyle(document.documentElement), body = getComputedStyle(document.body);
    res.push({vendor: o.vendor || null, text: o.txt.slice(0, 500), words: (o.txt.match(/[\p{L}\p{N}]+/gu) || []).length,
      box: [Math.round(vr.left), Math.round(vr.top), Math.round(vr.width), Math.round(vr.height)], area_pct: +(area * 100).toFixed(1), pos,
      aria_modal: o.el.getAttribute('aria-modal') === 'true' || o.el.getAttribute('role') === 'dialog' || o.el.getAttribute('role') === 'alertdialog',
      backdrop, scroll_locked: html.overflow === 'hidden' || body.overflow === 'hidden', shadow: !!o.el.shadowRoot,
      buttons: bi.map(x => ({t: x.t, kind: x.kind, w: x.w, h: x.h, fs: x.fs, fw: x.fw, filled: x.filled, border: x.border})),
      has_reject: !!rej, has_accept: !!acc, has_close: !!cls, has_settings: bi.some(x => x.kind === 'settings'), equal: eq,
      mentions_metrika: /метрик|metrika|яндекс/i.test(o.txt), mentions_pd: /персональн|personal data|152/i.test(o.txt),
      mentions_policy_link: [...o.root.querySelectorAll('a[href]')].some(a => /polic|privacy|konfid|cookie|политик|конфиденц|персональн/i.test((a.getAttribute('href') || '') + ' ' + (a.innerText || '')))});
  });
  const g = window;
  const vendorsJs = {onetrust: !!g.OneTrust || !!g.Optanon, cookiebot: !!g.Cookiebot, didomi: !!g.Didomi, usercentrics: !!g.UC_UI || !!g.usercentrics,
    klaro: !!g.klaro, cookieyes: !!g.getCkyConsent || !!g.cookieyes, iubenda: !!g._iub, complianz: !!g.complianz, tcf: typeof g.__tcfapi === 'function', gpp: typeof g.__gpp === 'function'};
  return {found: res.length > 0, banners: res, js: vendorsJs};
}"""

POPUP_JS = r"""() => {
  const VW = innerWidth, VH = innerHeight, norm = s => (s || '').replace(/[\s ]+/g, ' ').trim();
  const out = []; const all = document.body ? document.body.getElementsByTagName('*') : [];
  for (let i = 0; i < all.length && i < 40000; i++) { const el = all[i]; const c = getComputedStyle(el); if (c.position !== 'fixed') continue;
    if (el.closest('[data-pa-cmp-root]')) continue; const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
    try { if (el.checkVisibility && !el.checkVisibility({opacityProperty: true, visibilityProperty: true})) continue; } catch (e) {}
    const area = Math.max(0, Math.min(r.right, VW) - Math.max(r.left, 0)) * Math.max(0, Math.min(r.bottom, VH) - Math.max(r.top, 0)) / (VW * VH);
    if (area < 0.25) continue; const idc = (el.id || '') + ' ' + (typeof el.className === 'string' ? el.className : '');
    const t = norm(el.innerText).slice(0, 300); if (!t && !el.querySelector('img,iframe,form,input')) continue;
    if (r.top <= 4 && r.height <= 220) continue;       // шапка
    const inputs = [...el.querySelectorAll('input:not([type=hidden]),textarea')].length;
    out.push({el, idc, t, area, inputs, dialog: el.getAttribute('role') === 'dialog' || el.getAttribute('aria-modal') === 'true' || /modal|popup|overlay|lightbox|t-popup|t702|t390|t868/i.test(idc)}); }
  const top = out.filter(o => !out.some(p => p !== o && p.el.contains(o.el)));
  const res = top.filter(o => o.dialog || o.inputs > 0).slice(0, 2).map((o, i) => { o.el.setAttribute('data-pa-popup', String(i));
    const close = [...o.el.querySelectorAll('button,a,[role=button],[class*=close i]')].find(b => /close|закрыть|×|✕/i.test((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '') + ' ' + (typeof b.className === 'string' ? b.className : '')));
    if (close) close.setAttribute('data-pa-popup-close', String(i));
    return {text: o.t, area_pct: +(o.area * 100).toFixed(1), inputs: o.inputs, sel: o.idc.slice(0, 80), has_close: !!close}; });
  return res;
}"""

STICKY_JS = r"""(o) => {
  const VW = innerWidth, VH = innerHeight; const out = {y: Math.round(scrollY), top: [], bars: []};
  const CTA = new RegExp(o.cta1, 'i'), MSG = new RegExp(o.msg, 'i');
  const all = document.body ? document.body.getElementsByTagName('*') : []; const seen = [];
  for (let i = 0; i < all.length && i < 40000; i++) { const el = all[i]; const c = getComputedStyle(el); if (c.position !== 'fixed' && c.position !== 'sticky') continue;
    if (seen.some(s => s.contains(el))) continue; if (el.closest('[data-pa-cmp-root]')) continue;
    const r = el.getBoundingClientRect(); if (r.width < 30 || r.height < 20 || r.bottom < 0 || r.top > VH) continue;
    try { if (el.checkVisibility && !el.checkVisibility({opacityProperty: true, visibilityProperty: true})) continue; } catch (e) {}
    seen.push(el); const idc = (el.id || '') + ' ' + (typeof el.className === 'string' ? el.className : '');
    const links = [...el.querySelectorAll('a[href],button,[role=button]')].filter(b => { const rr = b.getBoundingClientRect(); return rr.width > 1 && rr.height > 1; });
    if (r.top <= 6 && r.width >= 0.9 * VW && r.height <= 230 && (links.length >= 2 || el.querySelector('img,svg'))) {
      out.top.push({h: Math.round(r.height), pos: c.position, links: links.length, sel: idc.slice(0, 60),
        cta: links.filter(b => CTA.test((b.innerText || '').trim())).map(b => (b.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 40)).slice(0, 3)}); continue; }
    const acts = links.filter(b => CTA.test((b.innerText || b.getAttribute('aria-label') || '').trim()) || /^tel:/i.test(b.getAttribute('href') || '') || MSG.test(b.getAttribute('href') || ''));
    if (!acts.length) continue;
    const chat = /jivo|jdiv|b24-widget|bx-livechat|carrot|intercom|crisp|tawk|hubspot|drift|livechat|chatra|usedesk|talk-me|webim|envybox|callbackhunter|wazzup|umnico|chat/i.test(idc + ' ' + [...el.querySelectorAll('[class],[id],iframe')].slice(0, 12).map(x => (x.id || '') + ' ' + (typeof x.className === 'string' ? x.className : '') + ' ' + (x.src || '')).join(' '));
    out.bars.push({pos: r.top > VH * 0.5 ? 'bottom' : (r.top < VH * 0.2 ? 'top' : 'side'), w: Math.round(r.width), h: Math.round(r.height), chat,
      texts: acts.slice(0, 4).map(b => (b.innerText || b.getAttribute('aria-label') || b.getAttribute('href') || '').trim().replace(/\s+/g, ' ').slice(0, 40)), sel: idc.slice(0, 60)}); }
  out.bars = out.bars.slice(0, 6); out.top = out.top.slice(0, 3); return out;
}"""

# ------------------------------------------------------------------------------------------------ JS: разбор страницы
ANALYZE_JS = r"""(opts) => {
  const T0 = performance.now(), LVW = innerWidth, LVH = innerHeight;
  const VW = Math.min(innerWidth, opts.vw || innerWidth), VH = Math.min(innerHeight, opts.vh || innerHeight), MOB = VW < 700;
  const DOC = document.documentElement, BODY = document.body; if (!BODY) return {error: 'no body'};
  const norm = s => (s || '').replace(/[\s ​]+/g, ' ').trim();
  const WRE = /[\p{L}\p{N}]+/gu, nwords = s => { const m = (s || '').match(WRE); return m ? m.length : 0; };
  const csC = new Map(), CS = el => { let c = csC.get(el); if (!c) { c = getComputedStyle(el); csC.set(el, c); } return c; };
  const RC = el => el.getBoundingClientRect();
  const vis = el => { if (!el || el.nodeType !== 1) return false; const r = RC(el); if (r.width < 2 || r.height < 2) return false;
    try { if (el.checkVisibility) return el.checkVisibility({opacityProperty: true, visibilityProperty: true}); } catch (e) {}
    const c = CS(el); return c.display !== 'none' && c.visibility !== 'hidden' && +c.opacity > 0.01; };
  const cn = el => typeof el.className === 'string' ? el.className : ((el.className && el.className.baseVal) || '');
  const desc = el => { if (!el || el.nodeType !== 1) return null; let s = el.tagName.toLowerCase(); if (el.id) s += '#' + String(el.id).slice(0, 40);
    const c = cn(el).trim(); if (c) s += '.' + c.split(/\s+/).slice(0, 3).join('.').slice(0, 80); return s; };
  const CTA1 = new RegExp(opts.cta1, 'i'), CTA2 = new RegExp(opts.cta2, 'i'), MSG = new RegExp(opts.msg, 'i');
  const PRICE = /(\d[\d\s .,]{0,12}\s?(₽|руб\.?|р\.(?![а-яa-z])|rub\b|usd\b|eur\b))|([$€£]\s?\d)/i;
  const PRICE_G = /(\d[\d\s .,]{0,12}\s?(₽|руб\.?|р\.(?![а-яa-z])|rub\b))|([$€£]\s?\d[\d.,]*)/gi;
  const DATE = /\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b|\b\d{1,2}\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i;
  const STAT = /^[~≈>+<≥]?\s*\d[\d\s.,]*\s*(%|\+|×|x|k|к|тыс\.?|млн\.?|млрд\.?|лет|года?|мин\.?|ч\.?|часов|дн\.?|дней|₽|\$|€|раз|м²|м2|км|km|m|b|bn|mln)?\s*\+?$/i;
  const PHONE = /(\+7|8)[\s\-(]*\d{3}[\s\-)]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}|\+\d{1,3}[\s\-(]*\d{2,4}[\s\-)]*\d{3}[\s\-]*\d{2,4}/;
  const SOC = /vk\.com|vk\.ru|t\.me\/|youtube\.com|youtu\.be|rutube\.ru|dzen\.ru|ok\.ru|instagram\.com|facebook\.com|linkedin\.com|twitter\.com|\/\/x\.com|tiktok\.com|pinterest\.|behance\.net|dribbble\.com|github\.com|vc\.ru|habr\.com|tenchat\.ru|max\.ru/i;
  // ---------- цвета
  const cvs = document.createElement('canvas'); cvs.width = cvs.height = 1; const cx = cvs.getContext('2d', {willReadFrequently: true}); const colC = new Map();
  const col = s => { if (!s) return null; if (colC.has(s)) return colC.get(s); let o = null; try { cx.clearRect(0, 0, 1, 1); cx.fillStyle = 'rgba(0,0,0,0)'; cx.fillStyle = s;
    cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; o = [d[0], d[1], d[2], +(d[3] / 255).toFixed(2)]; } catch (e) {} colC.set(s, o); return o; };
  const bgOwn = el => { const c = CS(el); const k = col(c.backgroundColor); const bi = c.backgroundImage;
    return {c: k && k[3] > 0.08 ? k : null, img: bi && bi !== 'none' ? (/url\(/.test(bi) ? 'url' : 'grad') : null}; };
  const bgKey = el => { let e = el, n = 0; while (e && n < 3) { const b = bgOwn(e); if (b.img) return 'img:' + b.img; if (b.c) return b.c.slice(0, 3).join(',');
      const re = RC(e); const kids = [...e.children].filter(k => { const r = RC(k); return r.height >= 0.85 * re.height && r.width >= 0.85 * re.width; });
      if (kids.length !== 1) break; e = kids[0]; n++; } return null; };
  const effBg = el => { let e = el; while (e && e !== DOC) { const b = bgOwn(e); if (b.c && b.c[3] > 0.5) return b.c; if (b.img === 'url') return null; e = e.parentElement; }
    return col(CS(BODY).backgroundColor) || [255, 255, 255, 1]; };
  const cdist = (a, b) => (a && b) ? Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) : 999;
  // ---------- базовый кегль
  const ps = [...document.querySelectorAll('p')].slice(0, 300).filter(p => nwords(p.innerText) >= 6).map(p => parseFloat(CS(p).fontSize)).filter(x => x > 8).sort((a, b) => a - b);
  const baseFs = ps.length >= 3 ? ps[Math.floor(ps.length / 2)] : (parseFloat(CS(BODY).fontSize) || 16);
  // ---------- все элементы, фиксированные слои
  const ALL = BODY.getElementsByTagName('*'); const N = Math.min(ALL.length, 40000);
  const SKIPT = new Set(['SCRIPT', 'STYLE', 'LINK', 'META', 'NOSCRIPT', 'TEMPLATE', 'BR', 'HR']);
  const fixed = [];
  for (let i = 0; i < N; i++) { const el = ALL[i]; if (SKIPT.has(el.tagName)) continue; const p = CS(el).position; if (p === 'fixed' || p === 'sticky') fixed.push(el); }
  const fixedTop = fixed.filter(el => !fixed.some(o => o !== el && o.contains(el)));
  const CHAT = /jivo|jdiv|b24-widget|bx-livechat|carrot|intercom|crisp|tawk|hubspot-messages|drift|livechat|chatra|usedesk|talk-me|webim|envybox|callbackhunter|wazzup|umnico|chat-?widget|chatwidget|onicon|textback|verbox|redhelper|livetex|zendesk|messenger-?widget|chat-button|chat_button|b24-crm|widget-button|leadback|callback-?widget|pozvonim|wcw|leadconnector|msgsndr|tidio|olark|smartsupp|gorgias|freshchat|kommunicate|helpcrunch|botpress|chatbot|widget-chat/i;
  const COOKIE = /cookie|куки|кук(и|ах|ами)\b/i;
  const overlays = [];
  for (const el of fixedTop) { if (!vis(el)) continue; const r = RC(el); const t = norm(el.innerText).slice(0, 1200);
    const idc = cn(el) + ' ' + (el.id || '') + ' ' + [...el.querySelectorAll('[id],[class],iframe')].slice(0, 25).map(x => (x.id || '') + ' ' + cn(x) + ' ' + (x.src || '')).join(' ');
    const area = Math.max(0, Math.min(r.right, VW) - Math.max(r.left, 0)) * Math.max(0, Math.min(r.bottom, VH) - Math.max(r.top, 0)) / (VW * VH);
    let kind = 'other';
    if (el.closest('[data-pa-cmp-root]') || (COOKIE.test(t) && t.length < 3000)) kind = 'cookie';
    else if (CHAT.test(idc)) kind = 'chat';
    else if (r.top <= 8 && r.width >= 0.9 * VW && r.height <= 220 && (el.querySelectorAll('a[href]').length >= 2 || el.querySelector('img,svg'))) kind = 'header';
    else if ((el.getAttribute('role') === 'dialog' || el.getAttribute('aria-modal') === 'true' || /modal|popup|overlay|lightbox|t-popup/i.test(idc)) && area >= 0.25) kind = 'popup';
    else if (r.bottom >= VH - 4 && r.top >= VH * 0.55 && r.width >= 0.5 * VW && r.height <= 200) kind = 'bottom-bar';
    else if (area < 0.03 && r.width <= 110 && r.height <= 110) kind = 'floating-button';
    el.setAttribute('data-pa-ovl', kind);
    overlays.push({kind, sel: desc(el), box: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)], area_pct: +(area * 100).toFixed(1), text: t.slice(0, 120)}); }
  const inOvl = el => { const o = el.closest('[data-pa-ovl]'); return o ? o.getAttribute('data-pa-ovl') : null; };
  // ---------- шапка
  function pickHeader() { const c = [];
    document.querySelectorAll('header,[role=banner],[class*=header i],[id*=header i],[class*=navbar i],[class*=topbar i],[class*=masthead i],nav,.t228,.t456,.t-menu,[data-record-type="228"],[data-record-type="456"],[data-record-type="257"],[data-record-type="451"],[data-record-type="970"],[data-record-type="967"],[data-record-type="1034"]').forEach(el => {
      if (!vis(el)) return; const r = RC(el); const y = r.top + scrollY; if (y > 200 || r.height > 260 || r.width < 0.8 * VW || r.height < 28) return;
      if (el.closest('footer')) return; const links = [...el.querySelectorAll('a[href]')].filter(vis).length, btns = el.querySelectorAll('button').length;
      if (links + btns < 1) return; c.push({el, y, h: r.height, sem: (el.tagName === 'HEADER' || el.getAttribute('role') === 'banner') ? 1 : 0}); });
    c.sort((a, b) => (b.sem - a.sem) || (a.y - b.y) || (b.h - a.h)); let best = c[0] ? c[0].el : null;
    if (best) for (const x of c) if (x.el !== best && x.el.contains(best) && x.h <= 260) best = x.el;
    if (!best) { const c2 = []; for (let i = 0; i < N; i++) { const el = ALL[i]; if (SKIPT.has(el.tagName)) continue; const r = RC(el);
        if (r.top + scrollY > 60 || r.height < 36 || r.height > 180 || r.width < 0.9 * VW) continue; if (!vis(el)) continue;
        const logo = [...el.querySelectorAll('img,svg')].some(m => { const rr = RC(m); return rr.left < VW * 0.5 && rr.width >= 24 && rr.height >= 16; }); if (!logo) continue;
        const burg = [...el.querySelectorAll('*')].slice(0, 200).some(b => /burger|hamburger|menu|nav-?toggle|toggler|mobile-?nav|offcanvas/i.test((b.getAttribute('aria-label') || '') + ' ' + cn(b) + ' ' + (b.id || '')));
        const links = [...el.querySelectorAll('a[href],button')].filter(vis).length; if (!burg && links < 1) continue; c2.push({el, h: r.height, a: r.width * r.height}); }
      c2.sort((x, y) => y.a - x.a); best = c2[0] ? c2[0].el : null; }
    return best; }
  const HDR = pickHeader(); if (HDR) HDR.setAttribute('data-pa-hdr', '1');
  let SROOT = null; if (Math.max(DOC.scrollHeight, BODY.scrollHeight) <= VH * 1.15) { for (let i = 0; i < N; i++) { const el = ALL[i]; const c = CS(el);
      if (!/(auto|scroll)/.test(c.overflowY) || el.clientHeight < 0.5 * VH || el.scrollHeight < 1.5 * el.clientHeight || RC(el).width < 0.5 * VW) continue;
      if (!SROOT || el.scrollHeight > SROOT.scrollHeight) SROOT = el; } }
  if (SROOT) SROOT.setAttribute('data-pa-scroll', '1');
  const inHdr = el => !!(HDR && HDR.contains(el));
  // ---------- заголовки
  const heads = [];
  document.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]').forEach(el => { if (!vis(el) || inOvl(el)) return; const t = norm(el.innerText); if (!t) return;
    const lvl = /^H\d$/.test(el.tagName) ? +el.tagName[1] : (+el.getAttribute('aria-level') || 2); heads.push({el, lvl, fs: parseFloat(CS(el).fontSize) || 16, t: t.slice(0, 160)}); });
  const vThr = Math.max(MOB ? 20 : 24, baseFs * 1.45);
  for (let i = 0; i < N; i++) { const el = ALL[i]; if (!/^(DIV|P|SPAN|STRONG|B|FONT)$/.test(el.tagName)) continue;
    let own = ''; for (const n of el.childNodes) if (n.nodeType === 3) own += n.nodeValue; if (norm(own).length < 2) continue;
    const fs = parseFloat(CS(el).fontSize); if (!(fs >= vThr)) continue; if (el.closest('h1,h2,h3,h4,h5,h6,[role=heading],button,a,label,[data-pa-ovl]')) continue;
    const t = norm(el.innerText); if (t.length < 2 || t.length > 160) continue; if (!vis(el)) continue; heads.push({el, lvl: 0, fs, t: t.slice(0, 160)}); }
  const h2fs = heads.filter(h => h.lvl === 2).map(h => h.fs).sort((a, b) => a - b); const medH2 = h2fs.length ? h2fs[Math.floor(h2fs.length / 2)] : null;
  const useH2 = h2fs.length >= 2;
  const secHeads = heads.filter(h => !STAT.test(h.t) && (h.lvl === 1 || h.lvl === 2 || (useH2 ? (h.lvl === 0 && h.fs >= medH2) : h.fs >= vThr)));
  const statHeads = heads.filter(h => STAT.test(h.t));
  const countSec = el => secHeads.reduce((a, h) => a + (el.contains(h.el) ? 1 : 0), 0);
  // ---------- полосы и секции
  const isBand = el => { if (SKIPT.has(el.tagName) || el.hasAttribute('data-pa-ovl')) return false; if (HDR && (el === HDR || (el.contains(HDR) && RC(el).height <= RC(HDR).height + 24))) return false;
    const c = CS(el); if (c.display === 'none' || c.visibility === 'hidden' || c.position === 'fixed' || c.position === 'absolute') return false;
    const r = RC(el); return r.height >= 8 && r.width >= (MOB ? 0.85 : 0.5) * VW; };
  const sig = k => k.tagName + '.' + ((cn(k).trim().split(/\s+/)[0]) || '').replace(/\d+/g, '#');
  const wrapperLike = (el, kids) => {
    if (el === BODY || el === SROOT || el.tagName === 'MAIN' || el.getAttribute('role') === 'main' || /^(allrecords|__next|root|app|__nuxt|___gatsby|main|page|wrapper|content|site)$/i.test(el.id || '')) return true;
    if (kids.length >= 3) { const m = new Map(); kids.forEach(k => m.set(sig(k), (m.get(sig(k)) || 0) + 1)); const mx = Math.max(...m.values());
      if (mx >= 0.7 * kids.length && Math.max(...kids.map(k => RC(k).height)) < 0.8 * VH && kids.filter(k => countSec(k) > 0).length < 2) return false; }
    const withHead = kids.filter(k => countSec(k) > 0).length; if (withHead >= 2) return true;
    const tall = kids.filter(k => RC(k).height >= 120); const bgs = new Set(tall.map(k => bgKey(k) || 'none'));
    if (tall.length >= 2 && bgs.size >= 2 && withHead >= 1) return true;
    if (RC(el).height > 2.2 * VH && kids.filter(k => RC(k).height > 0.5 * VH).length >= 2) return true;
    return false; };
  function seg(el, d) { const kids = [...el.children].filter(isBand); if (d > 18 || !kids.length) return [el];
    if (kids.length === 1) return (RC(kids[0]).height >= 0.55 * RC(el).height || el === BODY) ? seg(kids[0], d + 1) : [el];
    return wrapperLike(el, kids) ? kids.flatMap(k => seg(k, d + 1)) : [el]; }
  let bands = seg(SROOT || BODY, 0).filter(el => el !== BODY && el !== SROOT && !(HDR && HDR.contains(el)));
  bands.sort((a, b) => RC(a).top - RC(b).top);
  const mediaN = el => [...el.querySelectorAll('img,video,canvas,iframe,picture,svg')].filter(m => { const r = RC(m); return r.width >= 90 && r.height >= 50 && vis(m); }).length;
  const inputsN = el => [...el.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]),textarea,select')].filter(vis).length;
  const actN = el => [...el.querySelectorAll('a[href],button,[role=button],input[type=submit]')].filter(b => vis(b) && CTA1.test(norm(b.innerText || b.value || ''))).length;
  const bgImgDeep = el => { if (bgOwn(el).img === 'url') return true; const re = RC(el); return [...el.querySelectorAll('*')].slice(0, 60).some(k => { const r = RC(k); return bgOwn(k).img === 'url' && r.height >= 0.5 * re.height && r.width >= 0.5 * re.width; }); };
  const sliderLike = el => /swiper|slick|carousel|splide|glide|owl-|t-slds|flickity|embla|keen-slider|slider|sppb-carousel/i.test(cn(el) + ' ' + [...el.querySelectorAll('[class]')].slice(0, 40).map(cn).join(' '));
  let G = bands.map(el => { const r = RC(el); const t = el.innerText || ''; return {els: [el], y: r.top + scrollY, h: r.height, words: nwords(t), heads: countSec(el), media: mediaN(el), inputs: inputsN(el), act: actN(el), bgimg: bgImgDeep(el), slider: sliderLike(el)}; })
    .filter(g => g.h >= 12 && (g.words > 0 || g.media > 0 || g.inputs > 0 || g.bgimg));
  const hdrBottom = HDR ? RC(HDR).bottom + scrollY : 0; const topbar = [];
  if (HDR) G = G.filter(g => { if (g.y + g.h <= hdrBottom + 6 && g.h < 160) { topbar.push(g); return false; } return true; });
  const headWords = g => secHeads.filter(h => g.els.some(e => e.contains(h.el))).reduce((a, h) => a + nwords(h.t), 0);
  const mergeInto = (dst, src, prepend) => { dst.els = prepend ? src.els.concat(dst.els) : dst.els.concat(src.els); if (prepend) dst.y = src.y;
    dst.h += src.h; dst.words += src.words; dst.heads += src.heads; dst.media += src.media; dst.inputs += src.inputs; dst.act += src.act; dst.bgimg = dst.bgimg || src.bgimg; dst.slider = dst.slider || src.slider; };
  for (let i = 0; i < G.length - 1; i++) { const g = G[i]; if (g.heads >= 1 && g.words - headWords(g) <= 25 && g.media === 0 && g.inputs === 0 && g.act === 0 && g.h < 0.45 * VH
      && !g.bgimg && !g.slider && !(i === 0 && g.h >= 0.3 * VH)) { mergeInto(G[i + 1], g, true); G.splice(i, 1); i--; } }
  for (let i = 1; i < G.length; i++) { const g = G[i]; if (g.h < (MOB ? 50 : 60) && g.words <= 12 && g.inputs === 0 && g.heads === 0 && g.media < 3) { mergeInto(G[i - 1], g, false); G.splice(i, 1); i--; } }
  for (let i = 1; i < G.length; i++) { const g = G[i], pv = G[i - 1];
    if (g.heads === 0 && g.inputs === 0 && g.words < 40 && g.media < 3 && g.h < 0.35 * VH && bgKey(g.els[0]) === bgKey(pv.els[pv.els.length - 1]) && !/©|ИНН|ОГРН|copyright/i.test(g.els.map(e => e.innerText).join(' '))) { mergeInto(pv, g, false); G.splice(i, 1); i--; } }
  // подвал
  const FOOTS = [...document.querySelectorAll('footer,[role=contentinfo]')].filter(f => vis(f) && RC(f).height >= 30 && !inOvl(f));
  const FOOT = FOOTS.length ? FOOTS.reduce((a, b) => (RC(b).top > RC(a).top ? b : a)) : null;
  const footerish = g => { const t = g.els.map(e => e.innerText || '').join(' '); const links = g.els.reduce((a, e) => a + e.querySelectorAll('a[href]').length, 0);
    if (FOOT && g.els.some(e => e === FOOT || e.contains(FOOT) || FOOT.contains(e))) return true;
    if (g.inputs > 0 || g.els.some(e => e.querySelector('[class*=ymaps],.leaflet-container,iframe[src*="map"],iframe[src*="2gis"]'))) return false;
    return (links >= 6 || /©|\(c\)|copyright|все права|all rights|ИНН|ОГРН|политик\w* конфиденц|privacy policy/i.test(t)) && nwords(t) < 600; };
  let fStart = -1; for (let i = G.length - 1; i >= Math.max(0, G.length - 3); i--) { if (footerish(G[i]) && (i >= G.length - 2 || footerish(G[i + 1]))) fStart = i; else if (fStart >= 0) break; }
  if (fStart >= 0 && fStart < G.length - 1) { for (let i = G.length - 1; i > fStart; i--) { mergeInto(G[fStart], G[i], false); G.splice(i, 1); } }
  const isFooterG = i => fStart >= 0 && i === G.length - 1;
  // ---------- призывы
  const ctaCands = [...document.querySelectorAll('a[href],button,[role=button],input[type=submit],input[type=button]')];
  const ctas = []; let ck = 0;
  const groupOf = el => { for (let i = 0; i < G.length; i++) if (G[i].els.some(e => e === el || e.contains(el))) return i; return -1; };
  for (const el of ctaCands) {
    if (!vis(el)) continue; const ov = inOvl(el); if (ov === 'cookie' || ov === 'chat') continue;
    const r = RC(el); if (r.width < 16 || r.height < 12) continue;
    const t = norm(el.innerText || el.value || el.getAttribute('aria-label') || el.title || '').slice(0, 80);
    const hv = el.getAttribute('href') || ''; let tgt = 'js';
    if (/^tel:/i.test(hv)) tgt = 'tel'; else if (/^mailto:/i.test(hv)) tgt = 'mailto'; else if (MSG.test(hv)) tgt = 'messenger';
    else if (/^#(popup|order)/i.test(hv) || el.hasAttribute('data-popup') || el.getAttribute('data-toggle') === 'modal' || el.getAttribute('data-bs-toggle') === 'modal' || /dialog/i.test(el.getAttribute('aria-haspopup') || '')) tgt = 'popup';
    else if (hv.length > 1 && hv[0] === '#') tgt = 'anchor';
    else if (!hv || hv === '#' || /^javascript:/i.test(hv)) tgt = (el.tagName === 'BUTTON' || el.tagName === 'INPUT') && (el.type === 'submit' || (el.closest('form') && (el.getAttribute('type') || 'submit') === 'submit')) ? 'submit' : 'js';
    else { try { const u = new URL(hv, location.href); if (/apps\.apple\.com|play\.google\.com|rustore\.ru|appgallery/i.test(u.hostname)) tgt = 'app-store';
      else if (u.origin !== location.origin) tgt = 'external'; else if (u.pathname === location.pathname && u.hash) tgt = 'anchor'; else tgt = 'internal'; } catch (e) { tgt = 'other'; } }
    const c = CS(el); const bgc = col(c.backgroundColor); const eff = effBg(el.parentElement || el);
    const filled = !!(bgc && bgc[3] > 0.35 && cdist(bgc, eff) > 40); const border = (parseFloat(c.borderTopWidth) >= 1 && c.borderTopStyle !== 'none' && cdist(col(c.borderTopColor), eff) > 40);
    const sized = r.height >= 28 && r.height <= 120 && r.width >= 56 && r.width <= 700;
    const btnCls = /\bbtn\b|button|t-btn|cta|t-submit|wp-block-button|elementor-button|t-form__submit/i.test(cn(el));
    const style = (filled && sized) ? 'filled' : ((border || btnCls) && sized) ? 'outline' : 'link';
    let str = 'other'; if (CTA1.test(t)) str = 'primary'; else if (CTA2.test(t)) str = 'secondary'; else if (tgt === 'tel' || tgt === 'messenger' || tgt === 'mailto') str = 'contact';
    const isCta = t.length <= 80 && (str === 'primary' || str === 'contact' || (style !== 'link' && (str === 'secondary' || ['anchor', 'popup', 'submit', 'app-store'].includes(tgt))));
    if (!isCta) continue; if (!t && !['tel', 'messenger'].includes(tgt)) continue;
    let loc = 'section'; if (inHdr(el)) loc = 'header'; else if (ov) loc = 'sticky'; else if (el.closest('footer,[role=contentinfo]')) loc = 'footer';
    let fixedAnc = false; if (loc === 'section') { let a = el; while (a && a !== BODY) { const pp = CS(a).position; if (pp === 'fixed' || pp === 'sticky') { fixedAnc = true; break; } a = a.parentElement; } if (fixedAnc) loc = 'sticky'; }
    const g = groupOf(el); if (loc === 'section' && g >= 0 && isFooterG(g)) loc = 'footer';
    const y = r.top + scrollY; el.setAttribute('data-pa-cta', String(ck));
    ctas.push({k: ck++, t: t.slice(0, 60), str, style, tgt, href: hv.slice(0, 120), loc, sec: g, first_screen: y < VH && (loc === 'header' || loc === 'section' || loc === 'sticky'), y: Math.round(y), w: Math.round(r.width), h: Math.round(r.height)}); }
  // ---------- формы
  const FSEL = 'input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=image]):not([type=reset]),textarea,select';
  const containers = new Set([...document.querySelectorAll('form')]);
  for (const f of document.querySelectorAll(FSEL)) { if (f.closest('form')) continue; let a = f.parentElement, k = 0, found = null;
    while (a && a !== BODY && k < 7) { if (a.querySelector('button,[type=submit],[role=button],a[class*=btn i]')) { found = a; break; } a = a.parentElement; k++; } containers.add(found || f.parentElement || f); }
  const labelOf = f => { let t = ''; if (f.id) { const l = document.querySelector('label[for="' + CSS.escape(f.id) + '"]'); if (l) t = l.innerText; }
    if (!t) { const l = f.closest('label'); if (l) t = l.innerText; } if (!t) t = f.getAttribute('aria-label') || ''; if (!t && f.parentElement) t = f.parentElement.innerText || ''; return norm(t).slice(0, 240); };
  const PD = /персональн|обработк|пд\b|152-?фз|политик\w* (конфиденц|обработк)|конфиденциальн|privacy|personal (data|information)|data processing|terms|условия|оферт|agree to the|согласие на/i;
  const MKT = /рассылк|реклам|новост|маркетинг|предложени|акци|скидк|newsletter|marketing|promotional|updates|offers|news|subscribe|email me|sms/i;
  const forms = [];
  const hiddenLike = el => { const c = CS(el); const r = RC(el); return c.display === 'none' || c.visibility === 'hidden' || +c.opacity < 0.05 || r.width < 2 || r.height < 2 || r.left < -1000 || r.top + scrollY < -1000 || (c.position === 'absolute' && (r.left < -500 || parseFloat(c.left) < -500)); };
  let fk = 0;
  for (const c of containers) { if (!c || c === BODY) continue; if (inOvl(c) === 'cookie' || inOvl(c) === 'chat') continue;
    const fields = [...c.querySelectorAll(FSEL)]; if (!fields.length) continue;
    const visF = fields.filter(f => vis(f) || (f.type === 'checkbox' || f.type === 'radio') && f.closest('label') && vis(f.closest('label')));
    const info = fields.slice(0, 40).map(f => { const type = f.tagName === 'INPUT' ? (f.getAttribute('type') || 'text').toLowerCase() : f.tagName.toLowerCase();
      const hid = hiddenLike(f) && !((type === 'checkbox' || type === 'radio') && f.closest('label') && vis(f.closest('label')));
      const nm = ((f.getAttribute('name') || '') + ' ' + (f.id || '') + ' ' + cn(f)).toLowerCase();
      const honeypot = hid && ['text', 'email', 'url', 'tel', 'textarea'].includes(type) && (/hp|honey|website|url|fax|bot|trap|leave|nickname|address2|comment_?check|mail_confirm|surname2/.test(nm) || f.getAttribute('tabindex') === '-1' || f.getAttribute('autocomplete') === 'off' || f.getAttribute('aria-hidden') === 'true');
      const lab = ['checkbox', 'radio'].includes(type) ? labelOf(f) : norm(f.getAttribute('placeholder') || labelOf(f)).slice(0, 60);
      return {type, name: (f.getAttribute('name') || '').slice(0, 30), ac: f.getAttribute('autocomplete') || null, req: f.required || f.getAttribute('aria-required') === 'true',
        ph: (f.getAttribute('placeholder') || '').slice(0, 50), label: lab, hidden: hid, honeypot, checked: (type === 'checkbox' || type === 'radio') ? !!(f.checked || f.hasAttribute('checked')) : null,
        mask: !!(f.getAttribute('data-tilda-rule') === 'phone' || f.getAttribute('data-inputmask') || f.getAttribute('data-mask') || /\+7|\(___\)|_{3}/.test(f.getAttribute('placeholder') || ''))}; });
    const txt = norm((c.innerText || '') + ' ' + (c.parentElement ? (c.parentElement.innerText || '').slice(0, 800) : ''));
    const cbs = info.filter(x => x.type === 'checkbox' && !x.hidden);
    const consents = cbs.map(x => ({pd: PD.test(x.label), mkt: MKT.test(x.label), checked: x.checked, req: x.req, label: x.label.slice(0, 160)})).filter(x => x.pd || x.mkt);
    const pdN = consents.filter(x => x.pd && !x.mkt).length, mktN = consents.filter(x => x.mkt && !x.pd).length, both = consents.filter(x => x.pd && x.mkt).length;
    const notice = /(нажимая|отправляя|оставляя|заполняя|регистрируясь|подписываясь)[^.]{0,120}(соглаш|даю соглас|даете соглас|даёте соглас|подтвержда|принима|ознакомлен)|by (clicking|submitting|signing|continuing|registering)[^.]{0,120}(agree|accept|consent|acknowledge)/i.test(txt);
    const pol = [...c.querySelectorAll('a[href]'), ...(c.parentElement ? c.parentElement.querySelectorAll('a[href]') : [])].some(a => /polic|privacy|konfid|confid|personal|politik|soglas|agreement|consent|terms|oferta|offer|\bpd\b|152|legal/i.test(a.getAttribute('href') || '') || /политик|конфиденц|персональн|согласи|оферт|privacy|terms|policy/i.test(a.innerText || ''));
    const cap = {recaptcha: !!(c.querySelector('.g-recaptcha,[data-sitekey],iframe[src*="recaptcha"]') || document.querySelector('.grecaptcha-badge')), smartcaptcha: !!(c.querySelector('.smart-captcha,[class*=smartcaptcha i],iframe[src*="smartcaptcha"]')),
      hcaptcha: !!c.querySelector('.h-captcha,iframe[src*="hcaptcha"]'), turnstile: !!c.querySelector('.cf-turnstile,iframe[src*="turnstile"],iframe[src*="challenges.cloudflare"]')};
    const btns = [...c.querySelectorAll('button,[type=submit],[role=button],a[class*=btn i]')].filter(vis);
    const submit = btns.find(b => b.type === 'submit' || /submit/i.test(cn(b))) || btns[btns.length - 1];
    const nextBtns = btns.filter(b => /^(далее|дальше|следующ|продолжить|вперед|вперёд|next|continue)/i.test(norm(b.innerText || b.value || ''))).length;
    const stepTxt = txt.match(/(шаг|вопрос|step|question|этап)\s*(\d+)\s*(из|of|\/)\s*(\d+)/i);
    const quizCls = /quiz|multistep|multi-step|wizard|stepper|step-form|t-form_steps|t-form__step|marquiz|t1260|t1270|kviz|квиз/i.test(cn(c) + ' ' + [...c.querySelectorAll('[class]')].slice(0, 60).map(cn).join(' '));
    const vt = visF.map(f => f.tagName === 'INPUT' ? (f.getAttribute('type') || 'text').toLowerCase() : f.tagName.toLowerCase());
    const hasPwd = vt.includes('password'); const isSearch = vt.includes('search') || (visF.length <= 2 && /search|поиск|найти|query|\bq\b/i.test(fields.map(f => (f.getAttribute('name') || '') + ' ' + (f.getAttribute('placeholder') || '')).join(' ')));
    const contactish = info.some(x => !x.hidden && (x.type === 'tel' || x.type === 'email' || /phone|tel|телефон|mail|почт|имя|name|фио/i.test(x.name + ' ' + x.ph + ' ' + x.label)));
    let kind = 'other'; if (hasPwd) kind = 'login'; else if (isSearch) kind = 'search'; else if (vt.filter(t => !['checkbox', 'radio'].includes(t)).length === 1 && vt.includes('email') && !vt.includes('tel')) kind = 'email-capture';
    else if (contactish || vt.includes('textarea') || visF.length >= 2) kind = 'lead';
    const visible = visF.length > 0;
    const r = RC(c); const g = groupOf(c); c.setAttribute('data-pa-form', String(fk)); c.setAttribute('data-pa-form-kind', kind);
    const popAnc = !!(inOvl(c) === 'popup') || !!c.closest('.t-popup,[class*=popup i],[class*=modal i],[role=dialog],[class*=lightbox i],[class*=fancybox i],.remodal,.mfp-content');
    forms.push({k: fk++, kind, visible: visible && !popAnc, in_popup: !visible || popAnc, sec: g,
      first_screen: visible && r.top + scrollY < VH, y: Math.round(r.top + scrollY),
      fields_total: info.filter(x => !x.hidden && !['checkbox', 'radio'].includes(x.type)).length, fields: info.filter(x => !x.honeypot).slice(0, 24),
      types: vt, required: info.filter(x => x.req && !x.hidden).length, honeypot: info.filter(x => x.honeypot).length,
      checkboxes: cbs.length, consents, consent_pd_n: pdN, consent_mkt_n: mktN, consent_both_n: both, consent_prechecked: consents.some(x => x.checked), notice, policy_link: pol, captcha: cap,
      steps: {next_buttons: nextBtns, step_text: stepTxt ? stepTxt[0] : null, total: stepTxt ? +stepTxt[4] : null, quiz_class: quizCls}, submit: submit ? norm(submit.innerText || submit.value || '').slice(0, 60) : null,
      phone_mask: info.some(x => x.mask), autocomplete_n: info.filter(x => x.ac && x.ac !== 'off').length}); }
  // iframe-формы и квизы (Marquiz и т. п.)
  const iframes = [...document.querySelectorAll('iframe')].map(f => ({src: (f.src || f.getAttribute('data-src') || '').slice(0, 160), vis: vis(f), w: Math.round(RC(f).width), h: Math.round(RC(f).height), sec: groupOf(f)}));
  // ---------- признаки секций
  const repeatIn = g => { let best = null;
    for (const root of g.els) { const cont = [root, ...root.querySelectorAll('div,ul,ol,section,article,nav,tbody')].slice(0, 1500);
      for (const c of cont) { const kids = c.children; if (kids.length < 2 || kids.length > 80) continue;
        const vk = []; for (const k of kids) { const r = RC(k); if (r.width >= 40 && r.height >= 30 && r.height < 2 * VH) vk.push(k); } if (vk.length < 2) continue;
        const m = new Map(); for (const k of vk) { const s = sig(k); if (!m.has(s)) m.set(s, []); m.get(s).push(k); }
        let top = null; for (const arr of m.values()) if (!top || arr.length > top.length) top = arr; if (!top || top.length < 2) continue;
        const ws = top.map(k => RC(k).width).sort((a, b) => a - b); const mw = ws[Math.floor(ws.length / 2)]; const sim = top.filter(k => Math.abs(RC(k).width - mw) <= 0.3 * mw); if (sim.length < 2) continue;
        const area = sim.reduce((a, k) => a + RC(k).width * RC(k).height, 0); if (!best || sim.length > best.n || (sim.length === best.n && area > best.area)) best = {n: sim.length, area, items: sim}; } }
    if (!best) return null; const it = best.items; const f = fn => +(it.filter(fn).length / it.length).toFixed(2);
    const areas = it.map(k => RC(k).width * RC(k).height); const ma = areas.reduce((a, b) => a + b, 0) / areas.length; const sd = Math.sqrt(areas.reduce((a, b) => a + (b - ma) ** 2, 0) / areas.length);
    return {n: best.n, cols: new Set(it.map(k => Math.round(RC(k).left / 24))).size, rows: new Set(it.map(k => Math.round((RC(k).top + scrollY) / 24))).size,
      w: Math.round(RC(it[0]).width), h: Math.round(it.reduce((a, k) => a + RC(k).height, 0) / it.length),
      img: f(k => k.querySelector('img,picture,svg,video,canvas') || bgOwn(k).img === 'url'),
      bgphoto: f(k => bgOwn(k).img === 'url' || [...k.querySelectorAll('*')].slice(0, 30).some(x => bgOwn(x).img === 'url' && RC(x).width * RC(x).height >= 0.3 * RC(k).width * RC(k).height)), head: f(k => k.querySelector('h2,h3,h4,h5,h6,strong,b,[class*=title i],[class*=name i],[class*=head i]')),
      price: f(k => PRICE.test(k.innerText || '')), quote: f(k => /^[«“"„]/.test(norm(k.innerText)) || !!k.querySelector('blockquote,q')),
      avatar: f(k => [...k.querySelectorAll('img')].some(im => { const r = RC(im); const br = parseFloat(CS(im).borderTopLeftRadius) || 0; return r.width >= 24 && r.width <= 170 && br >= 0.35 * Math.min(r.width, r.height); })),
      words: Math.round(it.reduce((a, k) => a + nwords(k.innerText), 0) / it.length), link: f(k => k.tagName === 'A' || !!k.querySelector('a[href]')),
      num: f(k => /^\s*(0?\d{1,2}[.)]?\s|0?\d{1,2}$|шаг|этап|step)/i.test(norm(k.innerText).slice(0, 14))), date: f(k => DATE.test(k.innerText || '')), varied: ma ? +(sd / ma).toFixed(2) : 0}; };
  const secs = G.map((g, i) => {
    const els = g.els; const r0 = RC(els[0]), r1 = RC(els[els.length - 1]); const y = Math.round(r0.top + scrollY), h = Math.round(r1.bottom - r0.top);
    const inG = sel => els.flatMap(e => [...e.querySelectorAll(sel)]).filter(x => !inHdr(x) && !inOvl(x));
    const text = norm(els.map(e => e.innerText || '').join(' \n '));
    const hs = heads.filter(hh => els.some(e => e.contains(hh.el))).map(hh => ({l: hh.lvl, fs: Math.round(hh.fs), t: hh.t.slice(0, 120), sec: secHeads.includes(hh), y: Math.round(RC(hh.el).top + scrollY)})).sort((a, b) => a.y - b.y).slice(0, 8);
    const idcls = els.flatMap(e => [e, ...[...e.querySelectorAll('[id],[class]')].slice(0, 30)]).map(x => ((x.id || '') + ' ' + cn(x))).join(' ').toLowerCase().replace(/\s+/g, ' ').slice(0, 400);
    const tilda = [...new Set(els.map(e => e.getAttribute('data-record-type') || (e.closest('[data-record-type]') ? e.closest('[data-record-type]').getAttribute('data-record-type') : null)).filter(Boolean))];
    const imgs = inG('img,svg,picture').filter(m => { if (m.tagName === 'svg' && m.parentElement && m.parentElement.closest('svg')) return false; if (m.tagName === 'IMG' && m.closest('picture')) return false; const r = RC(m); return r.width >= 16 && r.height >= 12 && vis(m); });
    const garea = Math.max(1, (MOB ? VW : Math.min(VW, r0.width || VW)) * h);
    const imgInfo = imgs.map(m => { const r = RC(m); const alt = ((m.getAttribute('alt') || '') + ' ' + (m.getAttribute('src') || '') + ' ' + cn(m) + ' ' + (m.getAttribute('aria-label') || '')).toLowerCase();
      const src = m.tagName === 'IMG' ? (m.currentSrc || m.src || '') : (m.tagName === 'PICTURE' ? ((m.querySelector('img') || {}).currentSrc || '') : (m.outerHTML || '').slice(0, 200));
      const br = parseFloat(CS(m).borderTopLeftRadius) || 0; return {src, w: r.width, h: r.height, y: Math.round(r.top + scrollY), logo: (r.height <= 110 && r.width >= 40 && r.width <= 300 && r.width >= 1.2 * r.height) || /logo|partner|client|brand|customer|company|лого/.test(alt),
        round: r.width >= 24 && r.width <= 170 && br >= 0.35 * Math.min(r.width, r.height), big: r.width * r.height >= 0.12 * garea, icon: r.width <= 72 && r.height <= 72}; });
    const logoRows = new Map(); imgInfo.filter(m => m.logo).forEach(m => { const k = Math.round(m.y / 16); logoRows.set(k, (logoRows.get(k) || 0) + 1); });
    const imgRows = new Map(); imgInfo.filter(m => m.h <= 160 && m.w <= 360 && m.w >= 30).forEach(m => { const k = Math.round(m.y / 16); imgRows.set(k, (imgRows.get(k) || 0) + 1); });
    const videos = inG('video').filter(vis).length; const ifr = iframes.filter(f => f.sec === i);
    const vidIfr = ifr.filter(f => /youtube|youtu\.be|vimeo|rutube|vk\.com\/video|vkvideo|kinescope|wistia|loom|boomstream/i.test(f.src)).length;
    const mapIfr = ifr.filter(f => /map|2gis|yandex\.ru\/map|google\.com\/maps/i.test(f.src)).length + inG('[class*=ymaps],.leaflet-container,[class*=gm-style],[id*=map i] canvas').length;
    const bgMedia = [bgOwn(els[0]).img === 'url', ...[...els[0].children].slice(0, 6).map(k => bgOwn(k).img === 'url' && RC(k).height >= 0.5 * h)].some(Boolean);
    let mediaArea = 0; imgInfo.forEach(m => { if (m.w >= 80 && m.h >= 50) mediaArea += m.w * m.h; }); inG('video,canvas').forEach(v => { const r = RC(v); mediaArea += r.width * r.height; });
    const stats = statHeads.filter(sh => els.some(e => e.contains(sh.el))).length + inG('div,span,strong,b,p').filter(x => { if (x.children.length > 1) return false; const t = norm(x.innerText); return t.length > 0 && t.length <= 12 && STAT.test(t) && parseFloat(CS(x).fontSize) >= 1.3 * baseFs; }).length;
    const quotes = inG('blockquote,q').length + (text.match(/[«“„"][^»”"]{60,}/g) || []).length;
    const stars = (text.match(/[★⭐☆]/g) || []).length + inG('[class*=star i],[class*=rating i]').length;
    const times = (text.match(/\b([01]?\d|2[0-3])[:.][0-5]\d\b/g) || []).length;
    const bigNums = inG('div,span,p,strong,b').filter(x => { if (x.children.length) return false; const t = norm(x.innerText); return /^(0?[1-9]|1[0-9])[.)]?$/.test(t) && parseFloat(CS(x).fontSize) >= 1.3 * baseFs; }).length;
    const stepsTxt = (text.match(/\b(шаг|этап|step)\s*\d/gi) || []).length;
    const rows = inG('tr').filter(vis).length; const checks = (text.match(/[✓✔✗✘✕]/g) || []).length + inG('[class*=check i],[class*=tick i]').filter(x => RC(x).width <= 40).length;
    const acc = inG('details').length + inG('[aria-expanded]').length + inG('[class*=accordion i],[class*=faq i],[class*=question i],[class*=spoiler i],[class*=collapse i],.t585,.t668,.t849,.t1047,.t-accordion').length;
    const slider = /swiper|slick|carousel|splide|glide|owl-|t-slds|flickity|embla|keen-slider|slider/i.test(idcls) || inG('[aria-roledescription=carousel]').length > 0;
    const tabs = inG('[role=tablist]').length > 0 || /\btabs?\b|t-tabs|tablist/i.test(idcls);
    const links = inG('a[href]').filter(vis); const tel = links.filter(a => /^tel:/i.test(a.getAttribute('href') || '')).length; const msg = links.filter(a => MSG.test(a.getAttribute('href') || '')).length;
    const soc = links.filter(a => SOC.test(a.getAttribute('href') || '')).length; const apps = links.filter(a => /apps\.apple\.com|play\.google\.com|rustore\.ru|appgallery/i.test(a.getAttribute('href') || '')).length;
    const secCtas = ctas.filter(c => c.sec === i && c.loc !== 'header');
    const inputsV = inG(FSEL).filter(vis); const vforms = forms.filter(f => f.sec === i && f.visible);
    const countdown = /countdown|timer|t-timer|обратн\w* отсч/i.test(idcls) || /\b\d{2}\s?:\s?\d{2}\s?:\s?\d{2}\b/.test(text) || /дн(ей|я)\s*\d*\s*час/i.test(text);
    const beforeAfter = /до и после|до\/после|before.{0,12}after/i.test(text) || /before-?after|twentytwenty|comparison-slider|img-comp/i.test(idcls);
    return {i, y, h, h_vh: +(h / VH).toFixed(2), first_screen: y < VH * 0.9, tag: els[0].tagName.toLowerCase(), sel: desc(els[0]), n_roots: els.length, tilda,
      bg: bgKey(els[0]), bg_media: bgMedia || !!g.bgimg, slider_band: !!g.slider, is_footer: isFooterG(i), has_footer_el: !!(FOOT && els.some(e => e === FOOT || e.contains(FOOT) || FOOT.contains(e))),
      heads: hs, h1: hs.some(x => x.l === 1), words: nwords(text), text: text.slice(0, 700), idcls,
      links: links.length, buttons: inG('button,[role=button]').filter(vis).length, ctas: secCtas.length, ctas_primary: secCtas.filter(c => c.str === 'primary').length,
      cta_texts: [...new Set(secCtas.map(c => c.t))].slice(0, 6), inputs: inputsV.length, forms: vforms.length, form_kinds: vforms.map(f => f.kind),
      imgs: imgs.length, imgs_big: imgInfo.filter(m => m.big).length, logos: imgInfo.filter(m => m.logo).length, logos_distinct: new Set(imgInfo.filter(m => m.logo).map(m => m.src)).size, logo_row_max: Math.max(0, ...logoRows.values()), img_row_max: Math.max(0, ...imgRows.values()), avatars: imgInfo.filter(m => m.round).length,
      icons: imgInfo.filter(m => m.icon).length, videos, iframes_video: vidIfr, maps: mapIfr, canvas: inG('canvas').filter(vis).length,
      media_pct: Math.min(100, Math.round(100 * mediaArea / garea)), li: inG('li').filter(vis).length, p: inG('p').filter(x => nwords(x.innerText) >= 8).length,
      accordion: acc, slider, tabs, table_rows: rows, checks, stats, prices: (text.match(PRICE_G) || []).length, quotes, stars, times, dates: (text.match(new RegExp(DATE.source, 'gi')) || []).length,
      steps: bigNums + stepsTxt, qmarks: (text.match(/\?/g) || []).length, tel, messengers: msg, social: soc, app_badges: apps, countdown, before_after: beforeAfter,
      address: /ул\.|улиц|проспект|пр-т|пр\.\s|шоссе|бульвар|переулок|наб\.|д\.\s?\d|офис\s?\d|street|avenue|\bave\b|suite|road|\bst\.\s/i.test(text),
      legal: (text.match(/ИНН|ОГРН|КПП|ОГРНИП/g) || []).length, copyright: /©|\(c\)|copyright|все права|all rights/i.test(text), repeat: repeatIn(g)}; });
  // ---------- шапка и подвал подробно
  const hdrInfo = (() => { if (!HDR) return null; const r = RC(HDR), c = CS(HDR); const links = [...HDR.querySelectorAll('a[href]')]; const vl = links.filter(vis);
    const logo = vl.find(a => a.querySelector('img,svg,picture') && RC(a).left < VW * 0.45) || null;
    let logoHome = null; if (logo) { try { const u = new URL(logo.getAttribute('href'), location.href); logoHome = u.origin === location.origin && (u.pathname === '/' || u.pathname === '' || u.pathname === location.pathname && !u.hash); } catch (e) { logoHome = false; } }
    const nav = vl.filter(a => a !== logo && !/^tel:|^mailto:/i.test(a.getAttribute('href') || '') && !MSG.test(a.getAttribute('href') || '') && norm(a.innerText).length > 0 && norm(a.innerText).length <= 40);
    let fx = c.position; let a = HDR.parentElement; while (a && a !== BODY && fx !== 'fixed' && fx !== 'sticky') { const pp = CS(a).position; if (pp === 'fixed' || pp === 'sticky') fx = pp + '-anc'; a = a.parentElement; }
    const bgc = col(c.backgroundColor); const inner = [...HDR.querySelectorAll('*')].slice(0, 40).filter(x => { const rr = RC(x); return rr.width >= 0.9 * r.width && rr.height >= 0.6 * r.height; });
    const opaque = (bgc && bgc[3] > 0.1) || (c.backgroundImage !== 'none') || inner.some(x => { const b = bgOwn(x); return (b.c && b.c[3] > 0.1) || b.img; }) || (c.backdropFilter && c.backdropFilter !== 'none');
    const burger = [...HDR.querySelectorAll('button,[role=button],a,div,span')].filter(vis).find(b => { const rr = RC(b); if (rr.width > 90 || rr.height > 90 || rr.width < 14) return false;
      const s = ((b.getAttribute('aria-label') || '') + ' ' + cn(b) + ' ' + (b.id || '') + ' ' + (b.title || '')).toLowerCase();
      return /burger|hamburger|menu-?toggle|nav-?toggle|navbar-toggler|menu-?btn|menu-?button|mobile-?menu|t-menuburger|js-menu|menu-icon|меню|\bmenu\b|open-menu|toggle-menu|offcanvas/.test(s); });
    const hdrText = norm(HDR.innerText);
    return {sel: desc(HDR), tag: HDR.tagName.toLowerCase(), y: Math.round(r.top + scrollY), h: Math.round(r.height), position: fx, transparent: !opaque, over_hero: !opaque && secs.length > 0 && secs[0].y < r.bottom + scrollY - 4,
      nav_links: nav.length, nav_texts: nav.slice(0, 12).map(a => norm(a.innerText).slice(0, 30)), hidden_links: links.length - vl.length,
      submenu_markers: HDR.querySelectorAll('[aria-haspopup],[aria-expanded],.submenu,.sub-menu,.dropdown,[class*=dropdown i],[class*=submenu i],[class*=mega i],.t-menusub').length,
      logo: !!logo, logo_home: logoHome, phone: HDR.querySelectorAll('a[href^="tel:"]').length > 0 || PHONE.test(hdrText), phone_link: HDR.querySelectorAll('a[href^="tel:"]').length,
      messengers: links.filter(x => MSG.test(x.getAttribute('href') || '')).length, burger: !!burger, burger_sel: burger ? desc(burger) : null,
      lang_switch: /\b(EN|RU|ENG|РУС|English|Русский|DE|FR)\b/.test(hdrText) || !!HDR.querySelector('[hreflang],[lang]'), search: !!HDR.querySelector('input[type=search],[aria-label*=search i],[aria-label*=поиск i]'),
      ctas: ctas.filter(c => c.loc === 'header').map(c => c.t).slice(0, 4), words: nwords(hdrText),
      topbar: topbar.length > 0, topbar_words: topbar.reduce((a, g) => a + g.words, 0), topbar_text: norm(topbar.flatMap(g => g.els.map(e => e.innerText || '')).join(' ')).slice(0, 160)}; })();
  const footSec = fStart >= 0 ? secs[secs.length - 1] : null;
  const footInfo = (() => { const els = fStart >= 0 ? G[G.length - 1].els : (FOOT ? [FOOT] : []); if (!els.length) return null;
    const text = norm(els.map(e => e.innerText || '').join(' ')); const links = els.flatMap(e => [...e.querySelectorAll('a[href]')]).filter(vis);
    const groups = els.flatMap(e => [...e.querySelectorAll('ul,ol,nav,div')]).filter(x => x.querySelectorAll(':scope > li > a, :scope > a').length >= 2 && vis(x)).length;
    return {links: links.length, groups, inn: /ИНН\s*:?\s*\d{10,12}/.test(text), ogrn: /ОГРН(ИП)?\s*:?\s*\d{13,15}/.test(text), kpp: /КПП/.test(text), legal_form: /\b(ООО|ИП|АО|ПАО|ЗАО|LLC|Inc\.?|Ltd\.?|GmbH|LLP)\b/.test(text),
      policy: links.some(a => /polic|privacy|konfid|confid|personal|politik|cookie|terms|oferta|legal|soglas/i.test(a.getAttribute('href') || '') || /политик|конфиденц|персональн|cookie|куки|условия|оферт|privacy|terms|legal|соглашени/i.test(a.innerText || '')),
      social: links.filter(a => SOC.test(a.getAttribute('href') || '')).length, phone: links.some(a => /^tel:/i.test(a.getAttribute('href') || '')) || PHONE.test(text), email: links.some(a => /^mailto:/i.test(a.getAttribute('href') || '')) || /@[\w-]+\.\w+/.test(text),
      address: /ул\.|улиц|проспект|пр-т|шоссе|офис|street|avenue|suite|road/i.test(text), copyright: /©|\(c\)|copyright|все права|all rights/i.test(text), year: (text.match(/(20\d\d)/g) || []).slice(-1)[0] || null,
      made_on: /made on tilda|сделано на tilda|tilda publishing|создано на|made with|made in webflow|built with framer|made in framer|сайт создан/i.test(text), words: nwords(text), ad_marking: /erid|реклама\./i.test(text)}; })();
  // ---------- мета и разметка
  const meta = n => { const e = document.querySelector('meta[name="' + n + '" i],meta[property="' + n + '" i]'); return e ? (e.getAttribute('content') || '') : null; };
  const lnk = rel => { const e = document.querySelector('link[rel="' + rel + '" i]'); return e ? (e.getAttribute('href') || '') : null; };
  const jl = []; let jlErr = 0; const collect = (o, d) => { if (!o || d > 6) return; if (Array.isArray(o)) { o.forEach(x => collect(x, d + 1)); return; } if (typeof o !== 'object') return;
    if (o['@type']) (Array.isArray(o['@type']) ? o['@type'] : [o['@type']]).forEach(t => jl.push(String(t))); if (o['@graph']) collect(o['@graph'], d + 1);
    for (const k of ['mainEntity', 'itemListElement', 'offers', 'aggregateRating', 'review', 'author', 'publisher', 'address', 'hasOfferCatalog', 'provider', 'brand', 'location', 'organizer', 'performer', 'subEvent'])
      if (o[k]) collect(o[k], d + 1); };
  document.querySelectorAll('script[type="application/ld+json"]').forEach(s => { try { collect(JSON.parse(s.textContent), 0); } catch (e) { jlErr++; } });
  const allH = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')]; const visH = allH.filter(vis);
  const seq = visH.map(h => +h.tagName[1]); let skips = 0; const skipList = []; for (let i = 1; i < seq.length; i++) if (seq[i] > seq[i - 1] + 1) { skips++; if (skipList.length < 6) skipList.push(seq[i - 1] + '>' + seq[i]); }
  const h1s = allH.filter(h => h.tagName === 'H1'); const h1v = h1s.filter(vis);
  const icons = [...document.querySelectorAll('link[rel~="icon" i],link[rel="apple-touch-icon" i],link[rel="mask-icon" i],link[rel="manifest" i]')].map(l => ((l.getAttribute('rel') || '') + ' ' + (l.getAttribute('type') || '') + ' ' + (l.getAttribute('sizes') || '')).trim()).slice(0, 12);
  const hreflang = [...document.querySelectorAll('link[rel="alternate" i][hreflang]')].map(l => l.getAttribute('hreflang')).slice(0, 30);
  const gen = meta('generator'); const html0 = (document.head ? document.head.innerHTML : '').slice(0, 200000); const scr = [...document.scripts].map(s => s.src || '').join(' ');
  const plat = [];
  if (document.getElementById('allrecords') || /tildacdn|tilda/i.test(scr) || /tilda/i.test(gen || '')) plat.push('tilda');
  if (DOC.hasAttribute('data-wf-page') || /webflow/i.test(gen || '')) plat.push('webflow');
  if (document.querySelector('[data-framer-hydrate-v2],#__framer-badge-container,[data-framer-name]') || /framer/i.test(gen || '')) plat.push('framer');
  if (/wp-content|wp-includes/i.test(html0 + scr) || /wordpress/i.test(gen || '')) plat.push('wordpress');
  if (/\/bitrix\//i.test(html0 + scr) || window.BX) plat.push('1c-bitrix');
  if (/wix\.com|wixstatic|parastorage/i.test(html0 + scr) || /wix/i.test(gen || '')) plat.push('wix');
  if (window.__NEXT_DATA__ || self.__next_f || document.getElementById('__next')) plat.push('nextjs');
  if (window.__NUXT__ || document.getElementById('__nuxt')) plat.push('nuxt');
  if (document.getElementById('___gatsby')) plat.push('gatsby');
  if (document.querySelector('astro-island') || /astro/i.test(gen || '')) plat.push('astro');
  if (/squarespace/i.test(gen || '' ) || /squarespace/i.test(scr)) plat.push('squarespace');
  if (/hubspot/i.test(gen || '') || /hs-scripts|hubspot/i.test(scr)) plat.push('hubspot');
  if (/unbounce|ubembed/i.test(scr + html0)) plat.push('unbounce');
  if (/readymag/i.test(scr + html0)) plat.push('readymag');
  if (/lpgenerator/i.test(scr + html0)) plat.push('lpgenerator');
  if (/flexbe/i.test(scr + html0)) plat.push('flexbe');
  if (/shopify/i.test(scr) || window.Shopify) plat.push('shopify');
  if (/joomla/i.test(gen || '')) plat.push('joomla'); if (/drupal/i.test(gen || '')) plat.push('drupal');
  if (/creatium|craftum|nethouse|ukit|megagroup|taplink|setup\.ru|insales|umi/i.test(scr + (gen || ''))) plat.push('ru-builder');
  if (window.__VUE__ || document.querySelector('[data-v-app]')) plat.push('vue'); if (document.querySelector('[data-reactroot]') || window.React) plat.push('react');
  const bodyText = norm(BODY.innerText);
  const ovx = Math.max(0, Math.max(DOC.scrollWidth, BODY.scrollWidth) - VW); const culprits = [];
  if (ovx > 2) { for (let i = 0; i < N && culprits.length < 400; i++) { const el = ALL[i]; if (SKIPT.has(el.tagName)) continue; const r = RC(el);
      if (r.right <= VW + 2 || r.width < 1 || r.height < 1) continue; const c = CS(el); if (c.position === 'fixed' || ((c.position === 'absolute' || c.transform !== 'none') && r.left >= VW)) continue;
      let clipped = false, an = el.parentElement; while (an && an !== BODY) { const ac = CS(an); if (ac.position === 'fixed' || (/(hidden|clip|auto|scroll)/.test(ac.overflowX) && RC(an).right <= VW + 2)) { clipped = true; break; } an = an.parentElement; }
      if (!clipped) culprits.push({el, over: Math.round(r.right - VW), w: Math.round(r.width)}); }
    culprits.sort((x, y) => y.over - x.over); }
  const culp = culprits.filter(c => !culprits.some(o => o !== c && o.el.contains(c.el) && o.over >= c.over)).slice(0, 4).map(c => ({sel: desc(c.el), over: c.over, w: c.w, sec: groupOf(c.el)}));
  return {vw: VW, vh: VH, layout_vw: LVW, layout_vh: LVH, scroll_root: SROOT ? desc(SROOT) : null, scroll_root_top: SROOT ? Math.round(RC(SROOT).top + scrollY) : null, overflow_x: ovx, overflow_culprits: culp, doc_h: SROOT ? Math.round(RC(SROOT).top + scrollY + SROOT.scrollHeight) : Math.max(DOC.scrollHeight, BODY.scrollHeight), base_fs: baseFs, sec_threshold: useH2 ? 'h2' : vThr, url: location.href, title: document.title,
    lang: DOC.getAttribute('lang') || null, dir: DOC.getAttribute('dir') || null, words_total: nwords(bodyText), elements: ALL.length,
    header: hdrInfo, footer: footInfo, overlays, sections: secs, ctas, forms, iframes: iframes.slice(0, 20),
    headings: {h1_n: h1s.length, h1_visible_n: h1v.length, h1: h1v.slice(0, 3).map(h => norm(h.innerText).slice(0, 160)), h1_first_screen: h1v.some(h => RC(h).top + scrollY < VH),
      counts: [1, 2, 3, 4, 5, 6].map(n => visH.filter(h => +h.tagName[1] === n).length), skips, skip_list: skipList, first_is_h1: seq.length ? seq[0] === 1 : null},
    meta: {title: document.title, title_len: (document.title || '').length, desc: meta('description'), desc_len: (meta('description') || '').length, robots: meta('robots'), googlebot: meta('googlebot'), yandex: meta('yandex'),
      canonical: lnk('canonical'), og_title: meta('og:title'), og_desc: meta('og:description'), og_image: meta('og:image'), og_type: meta('og:type'), og_url: meta('og:url'), og_site_name: meta('og:site_name'), og_locale: meta('og:locale'),
      tw_card: meta('twitter:card'), tw_image: meta('twitter:image'), viewport: meta('viewport'), theme_color: meta('theme-color'), generator: gen, hreflang, icons,
      jsonld_types: [...new Set(jl)].slice(0, 40), jsonld_n: document.querySelectorAll('script[type="application/ld+json"]').length, jsonld_errors: jlErr,
      microdata: [...new Set([...document.querySelectorAll('[itemtype]')].map(e => (e.getAttribute('itemtype') || '').replace(/^https?:\/\/schema\.org\//, '')))].slice(0, 20),
      yandex_verification: !!meta('yandex-verification'), google_verification: !!meta('google-site-verification')},
    platform: [...new Set(plat)], ms: Math.round(performance.now() - T0)};
}"""

# ------------------------------------------------------------------------------------------------ JS: кандидаты для INP
INP_PICK_JS = r"""(o) => {
  const mobile = o.mobile, CTA1 = new RegExp(o.cta1, 'i'); const norm = s => (s || '').replace(/[\s ]+/g, ' ').trim();
  const cn = el => typeof el.className === 'string' ? el.className : ((el.className && el.className.baseVal) || '');
  const vis = el => { const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return false; try { if (el.checkVisibility) return el.checkVisibility({opacityProperty: true, visibilityProperty: true}); } catch (e) {} return true; };
  const desc = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (cn(el).trim() ? '.' + cn(el).trim().split(/\s+/).slice(0, 2).join('.') : '');
  const safeHref = el => { const h = el.getAttribute('href'); return el.tagName !== 'A' || h === null || h === '' || h[0] === '#' || /^javascript:/i.test(h); };
  document.querySelectorAll('[data-pa-inp]').forEach(e => e.removeAttribute('data-pa-inp'));
  const out = {}; const hdr = document.querySelector('[data-pa-hdr]');
  if (hdr) { const c = [...hdr.querySelectorAll('button,[role=button],a,div,span')].filter(vis);
    let m = null;
    if (mobile) m = c.find(b => { const r = b.getBoundingClientRect(); if (r.width > 90 || r.height > 90 || r.width < 14) return false;
      const s = ((b.getAttribute('aria-label') || '') + ' ' + cn(b) + ' ' + (b.id || '') + ' ' + (b.title || '')).toLowerCase();
      return /burger|hamburger|menu-?toggle|nav-?toggle|navbar-toggler|menu-?btn|menu-?button|mobile-?menu|t-menuburger|menu-icon|меню|\bmenu\b|open-menu|toggle-menu|offcanvas/.test(s) && safeHref(b); });
    if (!m) m = c.find(b => (b.getAttribute('aria-haspopup') === 'true' || b.getAttribute('aria-expanded') === 'false') && safeHref(b));
    if (!m && !mobile) m = [...hdr.querySelectorAll('a[href^="#"]')].filter(vis).find(a => a.getAttribute('href').length > 1 && !/^#(popup|order)/i.test(a.getAttribute('href')) && !!document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))));
    if (m) { m.setAttribute('data-pa-inp', 'menu'); out.menu = {sel: desc(m), text: norm(m.innerText).slice(0, 40), kind: m.tagName === 'A' ? 'anchor' : 'toggle'}; } }
  const ctas = [...document.querySelectorAll('[data-pa-cta]')].filter(vis);
  const anchorOk = el => { const h = el.getAttribute('href') || ''; if (!(h.length > 1 && h[0] === '#') || /^#(popup|order)/i.test(h)) return false;
    let id = h.slice(1); try { id = decodeURIComponent(id); } catch (e) {} return !!(document.getElementById(id) || document.querySelector('[name="' + CSS.escape(id) + '"]')); };
  let cta = ctas.find(el => anchorOk(el) && CTA1.test(norm(el.innerText))) || ctas.find(anchorOk); let popup = false;
  if (!cta) { cta = ctas.find(el => /^#(popup|order)/i.test(el.getAttribute('href') || '') || el.getAttribute('data-toggle') === 'modal' || el.getAttribute('data-bs-toggle') === 'modal'); popup = !!cta; }
  if (cta && cta.getAttribute('data-pa-inp') !== 'menu') { cta.setAttribute('data-pa-inp', 'cta'); out.cta = {sel: desc(cta), text: norm(cta.innerText).slice(0, 40), kind: popup ? 'popup' : 'anchor'}; }
  let faq = [...document.querySelectorAll('details:not([open]) > summary')].find(vis);
  if (!faq) faq = [...document.querySelectorAll('[aria-expanded="false"]')].find(b => vis(b) && !b.closest('[data-pa-hdr],nav,[data-pa-ovl],form,[data-pa-inp]') && norm(b.innerText).length >= 8 && norm(b.innerText).length <= 220 && safeHref(b));
  if (!faq) faq = [...document.querySelectorAll('.t585__header,.t668__header,.t849__header,.t1047__header,.t-accordion__header,[class*=accordion] [class*=header i],[class*=accordion] [class*=title i],[class*=faq] [class*=question i],[class*=faq] [class*=title i]')].find(b => vis(b) && !b.closest('a[href]:not([href^="#"])'));
  if (faq) { faq.setAttribute('data-pa-inp', 'faq'); out.faq = {sel: desc(faq), text: norm(faq.innerText).slice(0, 60)}; }
  const fld = [...document.querySelectorAll('[data-pa-form-kind="lead"] input,[data-pa-form-kind="lead"] textarea,[data-pa-form-kind="email-capture"] input')].find(f => vis(f) &&
    ['text', 'tel', 'email', 'number', 'textarea', ''].includes(f.tagName === 'TEXTAREA' ? 'textarea' : (f.getAttribute('type') || 'text').toLowerCase()) && !f.closest('[data-pa-hdr],[data-pa-ovl]') && !f.disabled && !f.readOnly);
  if (fld) { fld.setAttribute('data-pa-inp', 'field'); out.field = {sel: desc(fld), type: fld.getAttribute('type') || fld.tagName.toLowerCase()}; }
  return out;
}"""

# ------------------------------------------------------------------------------------------------ текст без JS
class _Txt(HTMLParser):
    SKIP = {'script', 'style', 'noscript', 'template', 'svg', 'iframe', 'object', 'head', 'canvas'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0; self.parts = []; self.h1 = []; self._h1 = None; self.title = None; self._title = False
        self.meta = {}; self.canon = None; self.jsonld = []; self._ld = False; self._ldbuf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title':
            self._title = True
        if tag == 'meta':
            k = (a.get('name') or a.get('property') or '').lower()
            if k:
                self.meta[k] = a.get('content') or ''
        if tag == 'link' and (a.get('rel') or '').lower() == 'canonical':
            self.canon = a.get('href')
        if tag == 'script' and (a.get('type') or '').lower() == 'application/ld+json':
            self._ld = True; self._ldbuf = []
        if tag in self.SKIP:
            self.depth += 1
        if tag == 'h1' and self.depth == 0:
            self._h1 = []

    def handle_endtag(self, tag):
        if tag == 'title':
            self._title = False
        if tag == 'script' and self._ld:
            self._ld = False; self.jsonld.append(''.join(self._ldbuf))
        if tag in self.SKIP and self.depth > 0:
            self.depth -= 1
        if tag == 'h1' and self._h1 is not None:
            self.h1.append(' '.join(self._h1).strip()); self._h1 = None

    def handle_data(self, data):
        if self._title:
            self.title = (self.title or '') + data
        if self._ld:
            self._ldbuf.append(data)
        if self.depth == 0:
            self.parts.append(data)
            if self._h1 is not None:
                self._h1.append(data)


def _nrm(s):
    return re.sub(r'[\s ​]+', ' ', (s or '')).strip().lower()


WORD_RE = re.compile(r'[^\W_]+', re.U)


def jsonld_types(blobs):
    out = []

    def rec(o, d=0):
        if d > 6 or o is None:
            return
        if isinstance(o, list):
            for x in o:
                rec(x, d + 1)
            return
        if not isinstance(o, dict):
            return
        t = o.get('@type')
        if t:
            out.extend(t if isinstance(t, list) else [t])
        for k in ('@graph', 'mainEntity', 'itemListElement', 'offers', 'aggregateRating', 'review', 'author', 'publisher', 'address',
                  'hasOfferCatalog', 'provider', 'brand', 'location', 'organizer', 'performer', 'subEvent'):
            if k in o:
                rec(o[k], d + 1)
    for b in blobs:
        try:
            rec(json.loads(b))
        except Exception:
            pass
    return sorted(set(map(str, out)))


def nojs_compare(raw_html, dom):
    """Сырой HTML ответа (без исполнения JS) против отрисованной страницы."""
    if not raw_html:
        return {'error': 'нет тела ответа'}
    p = _Txt()
    try:
        p.feed(raw_html); p.close()
    except Exception as ex:
        return {'error': 'parse: ' + str(ex)[:80]}
    raw_text = _nrm(' '.join(p.parts))
    raw_words = len(WORD_RE.findall(raw_text))
    rend_words = dom.get('words_total') or 0
    h1r = [x for x in (_nrm(h) for h in p.h1) if x]
    h1d = [_nrm(h) for h in (dom.get('headings') or {}).get('h1') or []]
    prim = [c for c in dom.get('ctas') or [] if c.get('str') == 'primary' and c.get('loc') in ('header', 'section') and c.get('t')]
    main_cta = None
    if prim:
        fs = [c for c in prim if c.get('first_screen')] or prim
        main_cta = fs[0]['t']
    sec_heads = [_nrm(h['t']) for s in dom.get('sections') or [] for h in s.get('heads') or [] if h.get('sec')]
    sec_heads = [h for h in sec_heads if len(h) >= 4]
    found_heads = sum(1 for h in sec_heads if h[:60] in raw_text)
    price_re = re.compile(r'\d[\d\s .,]{0,12}\s?(?:₽|руб\.?|р\.)|[$€£]\s?\d[\d.,]*', re.I)
    rend_text = ' '.join(_nrm(s.get('text')) for s in dom.get('sections') or [])
    prices = sorted(set(_nrm(m.group(0)) for m in price_re.finditer(rend_text)))[:30]
    raw_c = re.sub(r'\s', '', raw_text)
    pf = sum(1 for x in prices if re.sub(r'\s', '', x) in raw_c)
    ld_raw = jsonld_types(p.jsonld)
    ld_dom = (dom.get('meta') or {}).get('jsonld_types') or []
    return {'raw_words': raw_words, 'rendered_words': rend_words, 'ratio': round(raw_words / rend_words, 2) if rend_words else None,
            'h1_raw_n': len(h1r), 'h1_raw': h1r[:2], 'h1_match': bool(h1d and any(h[:40] in raw_text for h in h1d)),
            'main_cta': main_cta, 'main_cta_in_raw': (_nrm(main_cta)[:40] in raw_text) if main_cta else None,
            'section_heads': len(sec_heads), 'section_heads_in_raw': found_heads,
            'section_heads_ratio': round(found_heads / len(sec_heads), 2) if sec_heads else None,
            'prices_rendered': len(prices), 'prices_in_raw': pf, 'title_raw': bool((p.title or '').strip()), 'desc_raw': bool(p.meta.get('description')),
            'canonical_raw': p.canon, 'robots_raw': p.meta.get('robots'), 'og_image_raw': bool(p.meta.get('og:image')),
            'jsonld_raw': ld_raw, 'jsonld_js_only': sorted(set(ld_dom) - set(ld_raw)), 'html_kb': round(len(raw_html.encode('utf-8', 'ignore')) / 1024, 1)}


# ------------------------------------------------------------------------------------------------ сеть, память, сеть страницы
def mem_available_gb():
    try:
        for line in open('/proc/meminfo'):
            if line.startswith('MemAvailable:'):
                return int(line.split()[1]) / 1024 / 1024
    except Exception:
        pass
    return None


_NET_CACHE = os.path.join(str(kbpaths.cache('site')), 'net_cache.json')
CDN_ORGS = re.compile(r'cloudflare|ddos-guard|qrator|fastly|akamai|amazon|cloudfront|google|incapsula|imperva|stormwall|variti|gcore|g-core|edgecenter|cdnvideo|ngenix', re.I)


def net_of(host):
    """Страна и организация IP сервера (ipinfo.io/<ip сервера>); IP нигде не сохраняется. Кэш — net_cache.json."""
    host = (host or '').lower()
    try:
        cache = json.load(open(_NET_CACHE))
    except Exception:
        cache = {}
    if host in cache:
        return cache[host]
    res = {'country': None, 'org': None}
    try:
        ip = socket.getaddrinfo(host, 443, socket.AF_INET)[0][4][0]
        with urllib.request.urlopen(urllib.request.Request(f'https://ipinfo.io/{ip}/json', headers={'User-Agent': 'Mozilla/5.0'}), timeout=20) as r:
            j = json.loads(r.read().decode())
        res = {'country': j.get('country'), 'org': (j.get('org') or '')[:60]}
        del ip
    except Exception as ex:
        res = {'country': None, 'org': None, 'error': type(ex).__name__}
    if res.get('country') == 'RU':
        res['net'] = 'ru-direct'; res['basis'] = 'geoip-rule'
    elif res.get('country'):
        res['net'] = 'vpn-lt'; res['basis'] = 'geoip-rule'
    else:
        res['net'] = 'unknown'; res['basis'] = 'no-geo'
    if res.get('org') and CDN_ORGS.search(res['org']):
        res['net'] = 'unknown'; res['basis'] = 'cdn:' + res['org'][:30]
    if re.search(r'(^|\.)(yandex\.(ru|com|net)|ya\.ru|mail\.ru|vk\.com)$', host):
        res['net'] = 'ru-direct'; res['basis'] = 'echo'
    cache[host] = res
    try:
        os.makedirs(os.path.dirname(_NET_CACHE), exist_ok=True)
        json.dump(cache, open(_NET_CACHE, 'w'), ensure_ascii=False, indent=0)
    except Exception:
        pass
    return res


def net_probe(a):
    """Ходит ли замер в сеть за страной сервера и маршрутом: только с ключом --net и не в самопроверке."""
    return a.net is not None and not a.selftest


def route_probe():
    """Маршрут: разные ли адреса видят yandex.ru и ipinfo.io (раздельная маршрутизация VPN) и страна выхода.
    Возвращает только булево и страну; адреса машины не сохраняются и не печатаются."""
    def get(u):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=10) as r:
                return r.read(20000).decode('utf-8', 'replace')
        except Exception:
            return None
    y = get('https://yandex.ru/internet/api/v0/ip'); i = get('https://ipinfo.io/json')
    m = re.search(r'\d{1,3}(?:\.\d{1,3}){3}', y or ''); a1 = m.group(0) if m else None
    try:
        j = json.loads(i) if i else {}
    except Exception:
        j = {}
    a2, cc = j.get('ip'), j.get('country')
    res = {'split': (a1 != a2) if (a1 and a2) else None, 'exit_country': cc, 'yandex_ok': bool(a1), 'ipinfo_ok': bool(a2), 't': time.strftime('%H:%M:%S')}
    a1 = a2 = None
    return res


def lighten(u):
    """URL без query-строки для журнала (не хранить идентификаторы визита)."""
    try:
        s = urllib.parse.urlsplit(u)
        return urllib.parse.urlunsplit((s.scheme, s.netloc, s.path, '', ''))[:200]
    except Exception:
        return (u or '')[:200]


# ------------------------------------------------------------------------------------------------ прогон одной страницы
BLOCK_RE = re.compile(r"just a moment|attention required|access denied|доступ ограничен|проверка браузера|checking your browser|ddos-guard|"
                      r"are you a robot|вы не робот|подтвердите, что вы не робот|security check|request unsuccessful|403 forbidden|error 1020|"
                      r"performing security verification|verify you are human|пожалуйста, подождите|please wait while|captcha", re.I)


def detect_block(status, title, text):
    if status in (401, 403, 429, 503):
        return f'http-{status}'
    if BLOCK_RE.search(title or '') or (len(text or '') < 500 and BLOCK_RE.search(text or '')):
        return 'challenge'
    return None


def decode_body(body, ctype):
    cs = None
    m = re.search(r'charset=([\w-]+)', ctype or '', re.I)
    if m:
        cs = m.group(1)
    if not cs:
        m = re.search(rb'<meta[^>]+charset=["\']?([\w-]+)', body[:4000], re.I)
        if m:
            cs = m.group(1).decode('ascii', 'ignore')
    try:
        return body.decode(cs or 'utf-8', 'replace')
    except Exception:
        return body.decode('utf-8', 'replace')


def _bytes_now(creq):
    tot, by = 0, {}
    for r in creq.values():
        b = r['final'] if r['final'] is not None else r['data']
        tot += b
        t = r['type'] or 'other'
        by[t] = by.get(t, 0) + b
    return tot, by


def _cookie_names(ctx):
    try:
        return sorted({(c['name'][:40], c['domain'][:50]) for c in ctx.cookies()})
    except Exception:
        return []


def run_page(a):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    import base64
    mobile = bool(a.mobile)
    device = 'mobile' if mobile else 'desktop'
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    host0 = (urllib.parse.urlsplit(a.url).hostname or '').lower()
    market = a.market or ('ru' if re.search(r'\.(ru|xn--p1ai|su|рф)$', host0) else 'intl')
    locale = 'ru-RU' if market == 'ru' else 'en-US'
    al = 'ru-RU,ru;q=0.9,en;q=0.8' if market == 'ru' else 'en-US,en;q=0.9'
    tz = 'Europe/Moscow' if market == 'ru' else 'Europe/Vilnius'
    cpu = a.cpu if a.cpu is not None else (4 if mobile else 1)
    st = {'tool': TOOL, 'date': time.strftime('%Y-%m-%d %H:%M'), 'url': a.url, 'id': a.id, 'device': device, 'market': market,
          'locale': locale, 'accept_language': al, 'timezone': tz, 'cpu_throttle': cpu, 'page_type': a.label, 'site_type': a.site_type,
          'industry': a.industry, 'text_id': a.text_id, 'template': a.template, 'site_id': a.site_id, 'source': a.source, 'log': []}
    probe = net_probe(a)       # сеть — только ключом --net; без него сторонние сервисы не запрашиваются
    if probe and a.net == 'auto':
        ni = net_of(host0)
        st.update({'net': ni.get('net'), 'net_basis': ni.get('basis'), 'server_country': ni.get('country'), 'server_org': ni.get('org')})
    else:
        st['net'] = 'local' if a.selftest else (a.net or 'unknown')
        if not probe and not a.selftest:
            st['net_basis'] = 'без --net'
    creq, phase, logs = {}, {'v': 'load'}, st['log']
    st['route_before'] = route_probe() if probe else None
    T0 = time.monotonic()
    with sync_playwright() as pw:
        try:
            b = pw.chromium.launch(channel='chromium', headless=True, args=GPU_ARGS)
        except Exception:
            b = pw.chromium.launch(headless=True, args=GPU_ARGS)
        st['browser'] = b.version
        common = dict(locale=locale, timezone_id=tz, extra_http_headers={'Accept-Language': al}, color_scheme='light', reduced_motion='no-preference')
        cond = PG.conditions()
        if mobile:
            ctx = b.new_context(**PG.mobile_device(pw, cond), **common)       # UA — HeadlessChrome, как у самого браузера
        else:
            ctx = b.new_context(viewport={'width': cond['desktop']['width'], 'height': cond['desktop']['height']},
                                device_scale_factor=cond['desktop']['dpr'], **common)
        ctx.add_init_script(init_js())
        wv = wv_script()
        if wv:
            ctx.add_init_script(wv)
        else:
            logs.append('web-vitals не найден: ' + WV_IIFE)
        if a.selftest:     # «аналитика» тестовой страницы: подменяем без выхода в сеть
            ctx.route(re.compile(r'https://mc\.yandex\.ru/.*'), lambda r: r.fulfill(status=200, content_type='application/javascript', body='window.__ym_stub=1;'))
            ctx.route(re.compile(r'https://www\.googletagmanager\.com/.*'), lambda r: r.fulfill(status=200, content_type='application/javascript', body='window.__gtm_stub=1;'))
        p = ctx.new_page()
        W, H = p.viewport_size['width'], p.viewport_size['height']
        st['viewport'] = [W, H]
        cdp = ctx.new_cdp_session(p)
        cdp.send('Network.enable')
        cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})

        def c_will(e):
            try:
                rid = e['requestId']; r = creq.get(rid)
                if r is None:
                    creq[rid] = {'url': e['request']['url'], 'type': (e.get('type') or 'other').lower(), 't': round(time.monotonic() - T0, 2),
                                 'data': 0, 'final': None, 'failed': None, 'status': None, 'mime': None, 'phase': phase['v']}
                else:
                    r['url'] = e['request']['url']
            except Exception:
                pass

        def c_resp(e):
            r = creq.get(e.get('requestId'))
            if r is not None:
                rs = e.get('response') or {}
                r['status'] = rs.get('status'); r['mime'] = (rs.get('mimeType') or '')[:40]

        def c_data(e):
            r = creq.get(e.get('requestId'))
            if r is not None:
                r['data'] += e.get('encodedDataLength', 0) or 0

        def c_fin(e):
            r = creq.get(e.get('requestId'))
            if r is not None:
                r['final'] = e.get('encodedDataLength')

        def c_fail(e):
            r = creq.get(e.get('requestId'))
            if r is not None:
                r['failed'] = (e.get('errorText') or '')[:40]
        cdp.on('Network.requestWillBeSent', c_will)
        cdp.on('Network.responseReceived', c_resp)
        cdp.on('Network.dataReceived', c_data)
        cdp.on('Network.loadingFinished', c_fin)
        cdp.on('Network.loadingFailed', c_fail)
        if cpu and cpu > 1:
            cdp.send('Emulation.setCPUThrottlingRate', {'rate': cpu})
        p.on('pageerror', lambda e: logs.append('pageerror: ' + str(e)[:140]) if len(logs) < 30 else None)
        resp = None
        try:
            resp = p.goto(a.url, wait_until='load', timeout=a.timeout * 1000)
        except Exception as ex:
            logs.append('goto: ' + str(ex).split('\n')[0][:160])
            if p.url in ('about:blank', ''):
                try:
                    resp = p.goto(a.url, wait_until='commit', timeout=45000); st['goto_retry'] = 'commit'
                    p.wait_for_timeout(8000)
                except Exception as ex2:
                    logs.append('goto2: ' + str(ex2).split('\n')[0][:160])
        st['load_s'] = round(time.monotonic() - T0, 2)
        st['status'] = resp.status if resp else None
        raw_html, hdrs = None, {}
        if resp:
            try:
                hdrs = resp.headers or {}
            except Exception:
                hdrs = {}
            try:
                raw_html = decode_body(resp.body(), hdrs.get('content-type', ''))
            except Exception as ex:
                logs.append('body: ' + str(ex)[:100])
        st['x_robots_tag'] = hdrs.get('x-robots-tag')
        st['server_header'] = (hdrs.get('server') or '')[:40]
        p.wait_for_timeout(a.wait)
        st['final_url'] = p.url
        try:   # как страница видит клиента: UA и navigator.webdriver — без подмены
            st['ua'], st['webdriver'] = p.evaluate("() => [navigator.userAgent, navigator.webdriver]")
        except Exception:
            st['ua'] = st['webdriver'] = None
        try:
            title = p.title(); snip = p.evaluate("(document.body && document.body.innerText || '').slice(0, 800)")
        except Exception:
            title, snip = '', ''
        st['title'] = title[:200]
        st['blocked'] = detect_block(st['status'], title, snip)
        try:
            st['nav'] = p.evaluate("""(() => { const n = performance.getEntriesByType('navigation')[0]; if (!n) return null;
              return {ttfb: Math.round(n.responseStart), dcl: Math.round(n.domContentLoadedEventEnd), load: Math.round(n.loadEventEnd),
                      html_kb: Math.round(n.transferSize / 1024), proto: n.nextHopProtocol}; })()""")
        except Exception:
            st['nav'] = None
        tot, by = _bytes_now(creq)
        st['first_screen'] = {'kb': round(tot / 1024, 1), 'by_type_kb': {k: round(v / 1024, 1) for k, v in sorted(by.items(), key=lambda kv: -kv[1])},
                              'requests': len(creq), 't': round(time.monotonic() - T0, 2)}
        try:
            st['pre'] = p.evaluate("""(() => { const P = window.__pa || {}; return {lcp: (P.lcp || []).slice(-3), n: (P.lcp || []).length,
              cls: +(P.cls || 0).toFixed(4), cls_n: P.clsN || 0, lt: (P.lt || []).slice(0, 600), fcp: P.fcp || null, ttfb: P.ttfb || null, wv_lcp: P.wv_lcp || null}; })()""")
        except Exception as ex:
            st['pre'] = {'error': str(ex)[:100]}
        try:
            st['h1_paint'] = p.evaluate("(() => (window.__pa || {}).h1 || null)()")
        except Exception:
            st['h1_paint'] = None
        shots = {}
        try:
            shots['first'] = p.screenshot(type='jpeg', quality=70)
        except Exception as ex:
            logs.append('shot0: ' + str(ex)[:100])
        # ---- cookie-баннер
        phase['v'] = 'cmp'
        st['cookies_before'] = _cookie_names(ctx)
        cmp = {'found': False, 'action': 'none'}
        frame = None
        try:
            cmp.update(p.evaluate(COOKIE_JS, {}))
        except Exception as ex:
            cmp['error'] = str(ex)[:120]
        if not cmp.get('found'):
            for fr in p.frames[1:]:
                if re.search(r'sp_message|privacy-mgmt|consent|cmp|trustarc|cookie|onetrust|didomi|usercentrics|quantcast|sourcepoint', fr.url or '', re.I):
                    try:
                        rf = fr.evaluate(COOKIE_JS, {})
                        if rf.get('found'):
                            cmp.update(rf); cmp['frame'] = lighten(fr.url); frame = fr; break
                    except Exception:
                        pass
        cmp['t_detect'] = round(time.monotonic() - T0, 2)
        if cmp.get('found'):
            try:
                shots['cmp'] = p.screenshot(type='jpeg', quality=65)
            except Exception:
                pass
            if a.no_cmp_close:
                cmp['action'] = 'kept'
            else:
                target = frame or p
                for kind in ('reject', 'close'):
                    try:
                        loc = target.locator(f'[data-pa-cmp="{kind}"]').first
                        if loc.count() == 0:
                            continue
                        cmp['t_action'] = round(time.monotonic() - T0, 2)
                        loc.click(timeout=3000)
                        p.wait_for_timeout(1500)
                        still = p.evaluate("""(() => { const e = document.querySelector('[data-pa-cmp-root]'); if (!e) return false; const r = e.getBoundingClientRect();
                          const c = getComputedStyle(e); return r.width > 1 && r.height > 1 && c.display !== 'none' && c.visibility !== 'hidden' && +c.opacity > 0.05; })()""")
                        if frame is not None:
                            still = False
                        if not still:
                            cmp['action'] = kind; break
                        cmp.setdefault('notes', []).append(f'{kind}: баннер остался')
                    except Exception as ex:
                        cmp.setdefault('notes', []).append(f'{kind}: ' + str(ex).split('\n')[0][:100])
                if cmp['action'] == 'none':
                    cmp.setdefault('t_action', round(time.monotonic() - T0, 2))
                    try:
                        p.add_style_tag(content='[data-pa-cmp-root]{display:none !important}')
                        p.evaluate("document.documentElement.style.overflow='';document.body.style.overflow='';")
                        cmp['action'] = 'hidden'
                    except Exception as ex:
                        cmp.setdefault('notes', []).append('hide: ' + str(ex)[:80])
        st['cmp'] = cmp
        # ---- попапы захвата
        phase['v'] = 'popup'
        try:
            pops = p.evaluate(POPUP_JS)
        except Exception:
            pops = []
        for i, pp in enumerate(pops):
            try:
                p.keyboard.press('Escape'); p.wait_for_timeout(600)
                vis_ = p.evaluate(f"(() => {{ const e = document.querySelector('[data-pa-popup=\"{i}\"]'); if (!e) return false; const r = e.getBoundingClientRect(); return r.width > 1 && r.height > 1 && getComputedStyle(e).display !== 'none' && getComputedStyle(e).visibility !== 'hidden'; }})()")
                if vis_ and pp.get('has_close'):
                    p.locator(f'[data-pa-popup-close="{i}"]').first.click(timeout=2500); p.wait_for_timeout(600)
                    vis_ = p.evaluate(f"(() => {{ const e = document.querySelector('[data-pa-popup=\"{i}\"]'); if (!e) return false; const r = e.getBoundingClientRect(); return r.width > 1 && r.height > 1 && getComputedStyle(e).display !== 'none'; }})()")
                if vis_:
                    p.add_style_tag(content=f'[data-pa-popup="{i}"]{{display:none !important}}'); pp['action'] = 'hidden'
                else:
                    pp['action'] = 'closed'
            except Exception as ex:
                pp['action'] = 'error: ' + str(ex).split('\n')[0][:60]
        st['popups'] = pops
        # ---- прокрутка
        phase['v'] = 'scroll'
        sticky = []
        if not a.quick:
            try:
                total = p.evaluate("Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0) - innerHeight")
            except Exception:
                total = 0
            steps = max(6, min(45, int(total / (0.8 * H)) + 1)) if total > 0.5 * H else 6
            delta = max(250, int(total / steps)) if total > 0.5 * H else 500
            marks = {max(2, round(steps * 0.2)), round(steps * 0.55), max(3, steps - 1)}
            try:
                p.mouse.move(W / 2, H / 2)
                for s_ in range(1, steps + 1):
                    p.mouse.wheel(0, delta); p.wait_for_timeout(200)
                    if s_ in marks:
                        p.wait_for_timeout(350)
                        try:
                            sticky.append(p.evaluate(STICKY_JS, {'cta1': CTA_PRIMARY, 'msg': MESSENGER_RE}))
                        except Exception:
                            pass
                p.wait_for_timeout(900)
                st['scroll'] = {'total_px': total, 'steps': steps, 'delta': delta, 'y_end': p.evaluate('Math.round(scrollY)')}
                p.mouse.wheel(0, -(total + 2000)); p.wait_for_timeout(300)
                p.evaluate('window.scrollTo(0, 0)'); p.wait_for_timeout(1500)
            except Exception as ex:
                logs.append('scroll: ' + str(ex).split('\n')[0][:120])
        st['sticky_scan'] = sticky
        phase['v'] = 'post'
        # ---- разбор (внутренние прокручиваемые контейнеры — в начало)
        try:
            p.evaluate("(() => { for (const e of document.querySelectorAll('body *')) { if (e.scrollTop > 0) e.scrollTop = 0; } window.scrollTo(0, 0); })()"); p.wait_for_timeout(500)
        except Exception:
            pass
        try:
            dom = p.evaluate(ANALYZE_JS, {'cta1': CTA_PRIMARY, 'cta2': CTA_SECONDARY, 'msg': MESSENGER_RE, 'vw': W, 'vh': H})
        except Exception as ex:
            dom = {'error': str(ex).split('\n')[0][:300]}
            logs.append('analyze: ' + dom['error'])
        # ---- контактный лист: полностраничный снимок кусками (или прокрутка внутреннего контейнера)
        sheet_ims = []
        tw = 400 if not mobile else 300
        st['sheet_k'] = tw / W
        if not a.quick and not dom.get('error') and dom.get('scroll_root'):
            try:
                info = p.evaluate("(() => { const e = document.querySelector('[data-pa-scroll]'); const r = e.getBoundingClientRect(); return {x: r.left, y: r.top, w: r.width, h: r.height, sh: e.scrollHeight}; })()")
                yy = 0
                while yy < min(info['sh'], 40000):
                    p.evaluate("(y) => { document.querySelector('[data-pa-scroll]').scrollTop = y; }", yy); p.wait_for_timeout(300)
                    hh = min(info['h'], info['sh'] - yy)
                    shot = p.screenshot(type='jpeg', quality=60, clip={'x': info['x'], 'y': info['y'], 'width': info['w'], 'height': hh})
                    im = Image.open(io.BytesIO(shot)).convert('RGB')
                    cw = max(1, round(info['w'] * tw / W)); im = im.resize((cw, max(1, round(im.height * cw / im.width))))
                    sheet_ims.append(im); yy += info['h']
                p.evaluate("() => { document.querySelector('[data-pa-scroll]').scrollTop = 0; }")
                st['sheet_mode'] = 'inner-scroll'; st['sheet_offset'] = info['y']
            except Exception as ex:
                logs.append('sheet-inner: ' + str(ex).split('\n')[0][:120])
        elif not a.quick and not dom.get('error'):
            try:
                doc_h = min(int(dom.get('doc_h') or H), 60000)
                scale = tw / W
                y = 0
                while y < doc_h:
                    hh = min(5000, doc_h - y)
                    r = cdp.send('Page.captureScreenshot', {'format': 'jpeg', 'quality': 60, 'captureBeyondViewport': True,
                                                            'clip': {'x': 0, 'y': y, 'width': W, 'height': hh, 'scale': scale}})
                    im = Image.open(io.BytesIO(base64.b64decode(r['data']))).convert('RGB')
                    if im.width != tw:
                        im = im.resize((tw, max(1, round(im.height * tw / im.width))))
                    sheet_ims.append(im)
                    y += hh
                p.evaluate('window.scrollTo(0, 0)'); p.wait_for_timeout(400)
            except Exception as ex:
                logs.append('sheet: ' + str(ex).split('\n')[0][:120])
        # ---- лабораторный INP
        if a.inp and not dom.get('error') and not st.get('blocked'):
            st['inp'] = inp_scenario(p, mobile, a)
        # ---- итоговые метрики
        try:
            st['fin'] = p.evaluate("""(() => { const P = window.__pa || {}; return {lcp: (P.lcp || []).slice(-3), cls: +(P.cls || 0).toFixed(4), cls_n: P.clsN || 0,
              lt: (P.lt || []).slice(0, 1000), wv_lcp: P.wv_lcp || null, wv_cls: (P.wv_cls === undefined ? null : P.wv_cls), fcp: P.fcp || null, ttfb: P.ttfb || null,
              wv_err: P.wv_err || null, wv_inp: P.inp || null}; })()""")
        except Exception as ex:
            st['fin'] = {'error': str(ex)[:100]}
        try:
            st['h1_paint'] = p.evaluate("(() => (window.__pa || {}).h1 || null)()")
        except Exception:
            pass
        st['cookies_after'] = _cookie_names(ctx)
        st['t_total_s'] = round(time.monotonic() - T0, 1)
        try:
            ctx.close()
        except Exception:
            pass
        b.close()
    if probe:
        st['route_after'] = route_probe()
        st['route_ok'] = all((r or {}).get('split') is True and (r or {}).get('exit_country') == 'LT' for r in (st['route_before'], st['route_after']))
    st['dom'] = dom
    st['nojs'] = nojs_compare(raw_html, dom) if raw_html and not dom.get('error') else {'error': 'нет тела ответа или разбора'}
    st['network'] = net_summary(creq, st.get('final_url') or a.url, cmp.get('t_action'), cmp.get('action'))
    analyze_post(st)
    base = os.path.join(out, f'anatomy_{device}.json')
    if shots.get('cmp'):
        try:
            im = Image.open(io.BytesIO(shots['cmp'])).convert('RGB'); im = im.resize((im.width // 2, im.height // 2)); im.save(os.path.join(out, f'cmp_{device}.jpg'), quality=70)
            st['cmp_shot'] = f'cmp_{device}.jpg'
        except Exception:
            pass
    if sheet_ims:
        try:
            st['sheet'] = draw_sheet(sheet_ims, st, os.path.join(out, f'sheet_{device}.jpg'))
        except Exception as ex:
            logs.append('draw_sheet: ' + str(ex)[:120])
    elif shots.get('first'):
        try:
            im = Image.open(io.BytesIO(shots['first'])).convert('RGB'); im = im.resize((im.width // 2, im.height // 2)); im.save(os.path.join(out, f'first_{device}.jpg'), quality=70)
        except Exception:
            pass
    json.dump(st, open(base, 'w'), ensure_ascii=False, indent=1)
    return st


def inp_scenario(p, mobile, a):
    res = {'steps': []}
    try:
        p.evaluate('window.scrollTo(0, 0)'); p.wait_for_timeout(700)
        picks = p.evaluate(INP_PICK_JS, {'mobile': mobile, 'cta1': CTA_PRIMARY})
    except Exception as ex:
        return {'error': str(ex).split('\n')[0][:140]}
    res['picks'] = picks
    base = p.url.split('#')[0]
    t_start = p.evaluate('performance.now()')
    for step in ('menu', 'cta', 'faq', 'field'):
        if step not in picks:
            res['steps'].append({'step': step, 'done': False, 'why': 'нет кандидата'}); continue
        t_a = p.evaluate('performance.now()')
        done, err = False, None
        try:
            loc = p.locator(f'[data-pa-inp="{step}"]').first
            loc.scroll_into_view_if_needed(timeout=3000); p.wait_for_timeout(400)
            loc.click(timeout=4000); done = True
            if step == 'field' and a.selftest:
                p.keyboard.type('тест', delay=60)      # ввод — только на своей тестовой странице
            p.wait_for_timeout(1000)
        except Exception as ex:
            err = str(ex).split('\n')[0][:140]
        if p.url.split('#')[0] != base:
            res['navigated'] = step
            try:
                p.go_back(timeout=15000)
            except Exception:
                pass
            break
        ev = p.evaluate('(t) => (window.__pa && window.__pa.ev || []).filter(e => e.st >= t)', t_a)
        by = {}
        for e in ev:
            by.setdefault(e['id'], []).append(e)
        inter = [max(v, key=lambda e: e['dur']) for v in by.values()]
        res['steps'].append({'step': step, 'done': done, 'err': err, 'target': picks[step].get('sel'), 'n': len(inter),
                             'max_ms': max([i['dur'] for i in inter], default=None),
                             'events': [[i['name'], i['dur'], (i.get('target') or '')[:50], i['ps'] - i['st'], i['pe'] - i['ps']] for i in inter][:4]})
        try:
            if step == 'menu' and done and picks['menu'].get('kind') == 'toggle':
                p.locator('[data-pa-inp="menu"]').first.click(timeout=2500); p.wait_for_timeout(500)
            if step == 'cta' and done and picks['cta'].get('kind') == 'popup':
                p.keyboard.press('Escape'); p.wait_for_timeout(500)
        except Exception:
            try:
                p.keyboard.press('Escape')
            except Exception:
                pass
    ev = p.evaluate('(t) => (window.__pa && window.__pa.ev || []).filter(e => e.st >= t)', t_start)
    by = {}
    for e in ev:
        by.setdefault(e['id'], []).append(e)
    durs = sorted((max(x['dur'] for x in v) for v in by.values()), reverse=True)
    res['interactions'] = len(durs)
    res['inp_lab_ms'] = durs[0] if durs else None
    res['durations'] = durs[:10]
    try:
        res['web_vitals'] = p.evaluate('window.__pa && window.__pa.inp || null')
    except Exception:
        res['web_vitals'] = None
    return res


def net_summary(creq, page_url, t_action, action):
    ph = (urllib.parse.urlsplit(page_url).hostname or '').lower()
    prd = reg_domain(ph)
    reqs = []
    for r in creq.values():
        u = r['url'] or ''
        if not u or u.startswith(('data:', 'blob:', 'chrome-extension:')):
            continue
        b = r['final'] if r['final'] is not None else r['data']
        host = (urllib.parse.urlsplit(u).hostname or '').lower()
        cat, vendor = tp_classify(u)
        fp = reg_domain(host) == prd or host.endswith('.' + prd)
        reqs.append({'u': u, 'host': host, 'rd': reg_domain(host), 'b': b, 'type': r['type'], 't': r['t'], 'phase': r['phase'], 'fp': fp, 'cat': cat,
                     'vendor': vendor, 'status': r['status'], 'failed': r['failed']})
    tot = sum(x['b'] for x in reqs)
    by_type = {}
    for x in reqs:
        by_type[x['type']] = by_type.get(x['type'], 0) + x['b']
    tp = {}
    for x in reqs:
        if x['fp']:
            continue
        d = tp.setdefault(x['rd'], {'n': 0, 'kb': 0.0, 'cats': set(), 'vendors': set(), 'first_t': x['t']})
        d['n'] += 1; d['kb'] += x['b'] / 1024; d['cats'].add(x['cat']); d['vendors'].add(x['vendor']); d['first_t'] = min(d['first_t'], x['t'])
    by_cat = {}
    for x in reqs:
        if x['fp'] and x['cat'] in ('other',):
            continue
        c = by_cat.setdefault(x['cat'] if not x['fp'] else ('first-party' if x['cat'] == 'other' else x['cat']), {'n': 0, 'kb': 0.0, 'vendors': set()})
        c['n'] += 1; c['kb'] += x['b'] / 1024; c['vendors'].add(x['vendor'])
    trk = [x for x in reqs if x['cat'] in TRACKING_CATS]
    before = [x for x in trk if t_action is None or x['t'] < t_action]
    after = [x for x in trk if t_action is not None and x['t'] >= t_action]
    vendors_before = sorted({x['vendor'] for x in before})
    vendors_after_new = sorted({x['vendor'] for x in after} - set(vendors_before))
    fails = [x for x in reqs if x['failed'] and not re.search(r'ABORTED|BLOCKED_BY_CLIENT|canceled', x['failed'] or '', re.I)]
    return {'requests': len(reqs), 'failed_n': len(fails), 'failed_hosts': sorted({x['host'] for x in fails})[:8], 'session_kb': round(tot / 1024, 1),
            'by_type_kb': {k: round(v / 1024, 1) for k, v in sorted(by_type.items(), key=lambda kv: -kv[1])},
            'js_kb': round(by_type.get('script', 0) / 1024, 1), 'third_party_domains': len(tp),
            'third_party_kb': round(sum(d['kb'] for d in tp.values()), 1),
            'third_party': sorted([{'domain': k, 'n': d['n'], 'kb': round(d['kb'], 1), 'cats': sorted(d['cats']), 'vendors': sorted(v for v in d['vendors'] if v),
                                    'first_t': d['first_t']} for k, d in tp.items()], key=lambda z: -z['kb'])[:60],
            'by_cat': {k: {'n': v['n'], 'kb': round(v['kb'], 1), 'vendors': sorted(x for x in v['vendors'] if x)} for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1]['kb'])},
            'tracking_vendors': sorted({x['vendor'] for x in trk}), 'tracking_before_action': vendors_before,
            'tracking_after_action_new': vendors_after_new, 'tracking_after_reject': (vendors_after_new if action == 'reject' else None),
            'metrika_webvisor': any('webvisor' in x['u'] for x in reqs),
            'tracking_requests': [{'u': lighten(x['u']), 't': x['t'], 'vendor': x['vendor'], 'phase': x['phase']} for x in sorted(trk, key=lambda z: z['t'])][:50]}


# ------------------------------------------------------------------------------------------------ классификатор секций
VOCAB = 'словарь site 02-site-types/vocabulary.yaml: section_role, block; нераспознанное — other; классификатор секций 1.1'
_RK = {r: (re.compile(h, re.I) if h else None, re.compile(t, re.I) if t else None) for r, (h, t) in ROLE_KW.items()}
ROLE_CLS = {
    'hero': r'hero|first-?screen|firstscreen|intro\b|main-?screen|jumbotron|masthead|promo-?block|t-cover|cover\b|banner-?main|top-?block|offer-?block',
    'faq': r'faq|accordion|question|voprosy|voprosi', 'testimonials': r'review|testimonial|otzyv|otziv|feedback', 'pricing': r'pric|tarif|plans?\b|cost|ceny|price',
    'how-it-works': r'step|process|how-?it|etap|stages?\b', 'team': r'team|doctor|expert|staff|komand|vrach|specialist|teacher|speaker',
    'portfolio': r'portfolio|works?\b|project|gallery|galereya|nashi-raboty', 'case-studies': r'\bcases?\b|case-?stud|keys',
    'contacts': r'contact|kontakt|address|adres|map\b|ymaps', 'about': r'about|o-nas|onas|company|history|istoriya|mission',
    'benefits': r'benefit|advantage|feature|preimush|why|pochemu|plus', 'proof-logos': r'logo|client|partner|brand|trusted|marquee',
    'proof-stats': r'\bstats?\b|numbers|counter|digits|facts|cifry|tsifry', 'lead-form': r'form|zayavk|lead|callback|order|quiz|calc|kviz|zapis',
    'integrations': r'integration', 'event-program': r'agenda|schedule|program|speaker|curriculum|module|raspisanie',
    'related': r'blog|news|article|post|stati|novosti', 'guarantee': r'guarant|warrant|garant', 'comparison': r'compar|versus|\bvs\b|sravn',
    'offer': r'service|uslug|catalog|offer|package|napravlen', 'promo': r'promo|sale|discount|akci|countdown|timer|skidk', 'audience': r'use-?case|audience|for-?whom|dlya-kogo',
}
_RC = {k: re.compile(v, re.I) for k, v in ROLE_CLS.items()}


def classify_sections(d):
    dom = d.get('dom') or {}
    secs = dom.get('sections') or []
    H = dom.get('doc_h') or 0
    ptype = d.get('page_type') or ''
    # полосы меню и объявлений над hero — часть шапки
    hdr = dom.get('header') or {}
    hdr_bottom = (hdr.get('y', 0) + hdr.get('h', 0)) if hdr else 0
    header_dup = set()
    for i, s in enumerate(secs):
        if s.get('is_footer') or s.get('h1') or s.get('forms') or s.get('inputs'):
            break
        big = max([h.get('fs', 0) for h in s.get('heads') or []] or [0])
        if s.get('y', 0) <= max(320, hdr_bottom + 60) and s.get('h', 999) <= 220 and s.get('words', 0) <= 45 and big < 28:
            header_dup.add(i)
            continue
        break
    content_idx = [i for i, s in enumerate(secs) if not s.get('is_footer') and i not in header_dup]
    first_i = content_idx[0] if content_idx else None
    last_i = content_idx[-1] if content_idx else None
    forms = dom.get('forms') or []
    iframes = dom.get('iframes') or []
    res = []
    for i, s in enumerate(secs):
        if i in header_dup:
            res.append({'i': i, 'role': 'header', 'block': 'announcement-bar' if s.get('words', 0) <= 25 and (s.get('links', 0) or 0) <= 3 else 'header',
                        'conf': 0.5, 'top3': [['header', 9.0]], 'why': ['полоса меню или объявления над hero']})
            continue
        sc, why = {}, {}

        def add(role, v, reason):
            sc[role] = sc.get(role, 0) + v
            why.setdefault(role, []).append(reason)
        heads = s.get('heads') or []
        mfs = max([h.get('fs', 0) for h in heads] or [0])
        hs = [h for h in heads if h.get('sec')][:2] + [h for h in heads if h.get('fs', 0) >= 0.8 * mfs][:3]
        if not hs:
            hs = heads[:2]
        seen_t = set(); hs = [h for h in hs if not (h['t'] in seen_t or seen_t.add(h['t']))]
        head = ' | '.join(h['t'] for h in hs[:4]).lower()
        nmain = 2 if hs and len(hs[0]['t'].split()) <= 3 else 1          # короткий надзаголовок + заголовок
        main_h = ' | '.join(h['t'] for h in hs[:nmain]).lower()
        rest = hs[nmain:4] + [h for h in heads if h not in hs][:4]
        rest_h = ' | '.join(h['t'] for h in rest).lower()
        text = (s.get('text') or '').lower()
        idc = s.get('idcls') or ''
        rp = s.get('repeat') or {}
        pos = (s.get('y', 0) / H) if H else 0.0
        head_hit = set()
        for role, (hre, tre) in _RK.items():
            if hre and main_h and hre.search(main_h):
                add(role, 5, 'заголовок'); head_hit.add(role)
            elif hre and rest_h and hre.search(rest_h):
                add(role, 2, 'подзаголовок')
            if tre:
                m = len(tre.findall(text))
                if m:
                    add(role, min(3, m) * 0.6, f'текст×{m}')
        for role, cre in _RC.items():
            if cre.search(idc):
                add(role, 2, 'id/class')
        if s.get('is_footer'):
            add('footer', 30, 'подвал')
        if i == first_i and (s.get('h1') or s.get('h_vh', 0) >= 0.3):
            add('hero', 10, 'первая секция')
        if s.get('h1'):
            add('hero', 4, 'h1')
        if s.get('first_screen') and i == first_i:
            add('hero', 2, 'первый экран')
        vforms = [f for f in forms if f.get('sec') == i and f.get('visible')]
        lead = [f for f in vforms if f.get('kind') in ('lead', 'email-capture')]
        quiz_ifr = [f for f in iframes if f.get('sec') == i and f.get('vis') and re.search(r'marquiz|quiz|typeform|tally|yclients|dikidi|calendly|bitrix24.*form|b24', f.get('src') or '', re.I)]
        if lead:
            add('lead-form', 5 + min(3, max(f.get('fields_total', 0) for f in lead)), 'форма заявки')
        if quiz_ifr:
            add('lead-form', 6, 'встроенная форма/квиз/запись')
        calc = bool(re.search(r'калькулятор|calculator', head)) or (bool(re.search(r'рассчита', head)) and s.get('inputs', 0) >= 2)
        if not lead and not quiz_ifr and 'lead-form' in sc and not calc:
            sc['lead-form'] *= 0.35
        if i == last_i and i != first_i and s.get('ctas_primary', 0) >= 1 and not lead and s.get('words', 0) < 140:
            add('final-cta', 4, 'последняя секция с призывом')
        if i not in (first_i,) and s.get('h_vh', 9) < 0.75 and s.get('ctas', 0) >= 1 and s.get('words', 0) < 70 and not lead:
            add('cta-band', 3, 'короткая полоса с призывом')
        if s.get('logos', 0) >= 4 and s.get('logo_row_max', 0) >= 3 and s.get('words', 0) < 90 and s.get('imgs_big', 0) == 0 and (not rp or rp.get('words', 0) <= 8) and s.get('logos_distinct', 9) >= 3 and (not rp or rp.get('bgphoto', 0) < 0.5):
            add('proof-logos', 6, f"логотипы {s['logos']}")
        elif s.get('img_row_max', 0) >= 4 and s.get('imgs_big', 0) == 0 and s.get('words', 0) <= 40 and not (rp.get('head', 0) >= 0.6 and rp.get('img', 0) >= 0.8):
            add('proof-logos', 3.5, f"ряд мелких картинок {s['img_row_max']}")
        if s.get('stats', 0) >= 2 and s.get('words', 0) < 160:
            add('proof-stats', 3 + min(2, s['stats'] - 2), f"числа {s['stats']}")
        if s.get('quotes', 0) >= 1:
            add('testimonials', 1.5, 'цитаты')
        if rp.get('quote', 0) >= 0.5 and rp.get('n', 0) >= 2:
            add('testimonials', 3, 'карточки-цитаты')
        if rp.get('avatar', 0) >= 0.5 and rp.get('n', 0) >= 2:
            add('testimonials', 1.5, 'аватары'); add('team', 1.5, 'аватары')
        if s.get('stars', 0) >= 3:
            add('testimonials', 2, 'звёзды')
        per_month = re.search(r'/\s?мес|в месяц|per month|/mo\b|/month|per user|/user|за пользовател', text)
        if s.get('prices', 0) >= 2:
            add('pricing', 1.5, f"цены {s['prices']}")
        if rp.get('price', 0) >= 0.6 and rp.get('n', 0) >= 2:
            add('pricing', 3, 'карточки с ценой')
        if s.get('table_rows', 0) >= 3 and s.get('prices', 0) >= 3:
            add('pricing', 3, 'таблица цен')
        # карточки услуг со ссылками «подробнее» или ценами «от» — services (ред. 2 словаря)
        if (rp.get('n', 0) >= 3 and rp.get('head', 0) >= 0.6 and rp.get('words', 99) <= 60 and rp.get('quote', 0) < 0.5 and not per_month
                and (s.get('links', 0) + s.get('ctas', 0) >= rp['n'] - 1 or re.search(r'\bот\s?\d|from \$', text))
                and (ptype in SERVICE_TYPES or re.search(r'\bот\s?\d|from \$', text))):
            add('services', 2.5, 'карточки услуг со ссылками или ценой «от»')
        if s.get('accordion', 0) >= 3:
            add('faq', 3, 'аккордеон')
        if s.get('qmarks', 0) >= 3:
            add('faq', 2, f"вопросы {s['qmarks']}")
        if re.search(r'остались вопросы|есть вопросы|не нашли ответ|задайте вопрос|any questions|still have questions', head) and s.get('accordion', 0) < 2:
            sc['faq'] = sc.get('faq', 0) - 5
            add('lead-form' if lead else 'final-cta', 3, '«остались вопросы» без аккордеона')
        if 'faq' in head_hit and s.get('accordion', 0) < 2 and s.get('qmarks', 0) < 3:
            sc['faq'] = sc.get('faq', 0) * 0.4
        if s.get('steps', 0) >= 3:
            add('how-it-works', 3, f"шаги {s['steps']}")
        if rp.get('num', 0) >= 0.6 and rp.get('n', 0) >= 3 and 'benefits' not in head_hit:
            add('how-it-works', 3, 'нумерованные карточки')
        if rp.get('img', 0) >= 0.8 and rp.get('n', 0) >= 4 and rp.get('words', 99) <= 25:
            add('portfolio', 1.5, 'сетка картинок')
        if s.get('before_after') or re.search(r'до и после|до/после|before (and|&) after', head + ' ' + text[:400]):
            add('case-studies', 4, 'до/после')
        if s.get('maps', 0) >= 1:
            add('contacts', 5, 'карта')
        if s.get('address') and (s.get('tel', 0) >= 1 or re.search(r'\+7|8 ?\(\d{3}\)', text)):
            add('contacts', 3, 'адрес и телефон')
        if s.get('times', 0) >= 3:
            add('event-program', 3, f"время {s['times']}")
        if s.get('table_rows', 0) >= 4 and s.get('checks', 0) >= 4:
            add('comparison', 4, 'таблица с галочками')
        if (s.get('videos', 0) + s.get('iframes_video', 0)) >= 1 and s.get('words', 0) < 160 and i != first_i:
            add('product-demo', 2.5, 'видео')
        if rp.get('n', 0) >= 3 and rp.get('head', 0) >= 0.6 and 4 <= rp.get('words', 0) <= 70 and rp.get('img', 0) >= 0.5 and rp.get('price', 0) < 0.5 and rp.get('quote', 0) < 0.5:
            add('benefits', 2.5, 'карточки с иконкой и заголовком')
        if s.get('icons', 0) >= 3:
            add('benefits', 0.8, 'иконки')
        # функция крупно со скриншотом (и цитатой клиента рядом) — не отзывы
        if s.get('imgs_big', 0) >= 1 and s.get('media_pct', 0) >= 40 and s.get('quotes', 0) <= 1 and rp.get('n', 0) < 2 and 0 < s.get('words', 0) <= 120 and i != first_i:
            if 'testimonials' in sc:
                sc['testimonials'] *= 0.5
            add('benefits', 2.5, 'функция с визуалом')
        if rp.get('date', 0) >= 0.5 and rp.get('n', 0) >= 2:
            add('related', 3, 'карточки с датами')
        nl = s.get('links', 0) or 0
        if nl >= 5 and s.get('words', 0) <= nl * 12 and not lead and s.get('prices', 0) <= nl and rp.get('img', 0) < 0.5 and not s.get('accordion'):
            add('related', 2, f'список ссылок {nl}')
        if s.get('words', 0) >= 400 and s.get('p', 0) >= 5 and rp.get('n', 0) < 3:
            add('article-body', 6 + (3 if s.get('words', 0) >= 700 else 0), 'длинный текст')
        if s.get('countdown'):
            add('promo', 3, 'таймер')
        if s.get('table_rows', 0) >= 5 and s.get('prices', 0) == 0 and s.get('checks', 0) < 3:
            add('specs', 1.5, 'таблица')
        if s.get('media_pct', 0) >= 70 and s.get('words', 0) <= 20 and i != first_i:
            add('story', 2.5, 'визуальная пауза')
        if s.get('legal', 0) >= 1 and not s.get('is_footer') and s.get('words', 0) < 160:
            add('legal', 2, 'реквизиты')
        if s.get('app_badges', 0) >= 1:
            if i != last_i and ptype != 'landing-app':
                add('cross-sell', 3, 'бейджи магазинов не в конце')
            else:
                add('final-cta' if i == last_i else 'cta-band', 1.5, 'бейджи магазинов')
        # текст внизу посадочной (не статьи) — seo-text (ред. 2 словаря)
        if (pos >= 0.55 and s.get('words', 0) >= 60 and not lead and not quiz_ifr and s.get('prices', 0) == 0 and s.get('media_pct', 0) <= 30
                and s.get('ctas', 0) <= 1 and s.get('accordion', 0) < 2 and not s.get('is_footer') and ptype not in ARTICLE_TYPES
                and (rp.get('n', 0) < 3 or (rp.get('words', 0) >= 12 and rp.get('img', 0) < 0.3 and rp.get('head', 0) < 0.3))):
            add('seo-text', 3.5 + (2 if s.get('words', 0) >= 150 else 0), 'текст внизу страницы')
        if 'article-body' in sc and ptype not in ARTICLE_TYPES and pos >= 0.5:
            sc['seo-text'] = sc.get('seo-text', 0) + sc.pop('article-body'); why.setdefault('seo-text', []).append('длинный текст на посадочной')
        # смысл заголовка сильнее ценовых признаков
        if (head_hit - {'pricing', 'hero'}) and 'pricing' not in head_hit and 'pricing' in sc:
            sc['pricing'] *= 0.5
        if 'final-cta' in head_hit and pos < 0.7 and i != last_i:
            sc['cta-band'] = sc.get('cta-band', 0) + sc.pop('final-cta')
        if i != first_i and 'hero' in sc:
            sc['hero'] = min(sc['hero'], 2)
        if 'contacts' in sc and not (s.get('maps', 0) or s.get('address') or s.get('tel', 0) or s.get('messengers', 0)):
            sc['contacts'] *= 0.5
        if i == first_i and s.get('first_screen') and (s.get('h1') or s.get('h_vh', 0) >= 0.3):
            sc['hero'] = max(sc.get('hero', 0), max(sc.values()) + 1); why.setdefault('hero', []).append('первый экран — hero')
        # фоллбэк — секция с заголовком и карточками или визуалом без совпадений → benefits (низкая уверенность)
        if (not sc or max(sc.values()) < 3) and i != first_i and not s.get('is_footer') and hs and s.get('words', 0) >= 10 and 'seo-text' not in sc and (
                (rp.get('n', 0) >= 2 and (rp.get('head', 0) >= 0.5 or rp.get('img', 0) >= 0.5)) or s.get('icons', 0) >= 3 or s.get('imgs_big', 0) >= 1):
            add('benefits', 3, 'по умолчанию: заголовок + карточки или визуал')
        ranked = sorted(sc.items(), key=lambda kv: -kv[1])
        top = ranked[0] if ranked else ('other', 0)
        second = ranked[1][1] if len(ranked) > 1 else 0
        role = top[0] if top[1] >= 3 else 'other'
        conf = round(max(0.0, min(1.0, (top[1] - second) / max(top[1], 1) + (0.15 if top[1] >= 8 else 0))), 2) if role != 'other' else 0.0
        blk = block_for(role, s, lead, quiz_ifr, i == first_i)
        res.append({'i': i, 'role': role, 'block': blk, 'conf': conf, 'top3': [[r, round(v, 1)] for r, v in ranked[:3]],
                    'why': why.get(role, [])[:6]})
    return res


def block_for(role, s, lead, quiz_ifr, first):
    rp = s.get('repeat') or {}
    fk = [f.get('kind') for f in lead]
    if role == 'services':
        return 'service-cards' if rp.get('n', 0) >= 2 else ('pricing-table' if s.get('prices', 0) >= 3 else 'offer-details')
    if role == 'seo-text':
        return 'prose'
    if role == 'cross-sell':
        return 'app-download' if s.get('app_badges', 0) else ('service-cards' if rp.get('n', 0) >= 3 and rp.get('img', 0) >= 0.5 else 'related-links')
    if role == 'hero':
        if lead and max(f.get('fields_total', 0) for f in lead) >= 1 and 'lead' in fk:
            return 'hero-form'
        if lead and 'email-capture' in fk:
            return 'hero-form'
        if s.get('slider') and rp.get('n', 0) >= 2 and rp.get('rows', 1) == 1:
            return 'hero-carousel'
        if s.get('media_pct', 0) >= 30 or s.get('bg_media') or s.get('videos', 0) or s.get('canvas', 0):
            return 'hero-media'
        return 'hero-text'
    if role == 'footer':
        return 'footer'
    if role == 'proof-logos':
        return 'logo-wall'
    if role == 'proof-stats':
        return 'stat-strip'
    if role == 'testimonials':
        if re.search(r'yandex\.ru/(sprav|maps-reviews)|2gis|flamp|otzovik|prodoctorov|trustpilot|g2', ' '.join(s.get('cta_texts') or []) + ' ' + (s.get('idcls') or ''), re.I):
            return 'review-aggregate'
        return 'testimonial-cards' if (rp.get('n', 0) >= 2 or s.get('quotes', 0) >= 2 or s.get('slider')) else 'testimonial-single'
    if role == 'case-studies':
        if s.get('before_after'):
            return 'before-after'
        return 'case-cards' if rp.get('n', 0) >= 2 else 'case-study'
    if role == 'awards-press':
        return 'credentials' if re.search(r'лиценз|сертифик|аккредит|сро\b|certif|licen', (s.get('text') or ''), re.I) else 'awards-press'
    if role == 'benefits':
        if s.get('tabs'):
            return 'feature-tabs'
        if rp.get('n', 0) >= 3 and rp.get('varied', 0) >= 0.45:
            return 'feature-bento'
        if rp.get('n', 0) >= 3:
            return 'feature-grid'
        if s.get('li', 0) >= 3:
            return 'benefit-list'
        if s.get('imgs_big', 0) >= 2:
            return 'feature-alternating'
        return 'feature-spotlight' if s.get('media_pct', 0) >= 40 and s.get('words', 0) <= 60 else 'feature-grid'
    if role == 'problem':
        return 'pain-points'
    if role == 'solution':
        return 'feature-spotlight' if s.get('media_pct', 0) >= 30 else 'prose'
    if role == 'how-it-works':
        return 'steps'
    if role == 'product-demo':
        return 'video-showcase' if (s.get('videos', 0) + s.get('iframes_video', 0)) else ('interactive-demo' if s.get('inputs', 0) and not lead else 'product-showcase')
    if role == 'audience':
        return 'audience-grid'
    if role == 'integrations':
        return 'integrations-grid'
    if role == 'specs':
        return 'spec-sheet'
    if role == 'pricing':
        if rp.get('price', 0) >= 0.6 and rp.get('n', 0) >= 2 and rp.get('rows', 1) <= 2 and s.get('table_rows', 0) < 3:
            return 'pricing-cards'
        if s.get('table_rows', 0) >= 3 or s.get('prices', 0) >= 4:
            return 'pricing-table'
        return 'pricing-single'
    if role == 'comparison':
        return 'comparison-table'
    if role == 'guarantee':
        return 'guarantee'
    if role == 'offer':
        return 'pricing-table' if s.get('prices', 0) >= 3 else 'offer-details'
    if role == 'promo':
        return 'promo-offer'
    if role == 'lead-form':
        f0 = max(lead, key=lambda f: f.get('fields_total', 0)) if lead else None
        if quiz_ifr and re.search(r'marquiz|quiz', ' '.join(q.get('src') or '' for q in quiz_ifr), re.I):
            return 'quiz'
        if quiz_ifr and re.search(r'yclients|dikidi|calendly', ' '.join(q.get('src') or '' for q in quiz_ifr), re.I):
            return 'booking-widget'
        if f0:
            stp = f0.get('steps') or {}
            if stp.get('next_buttons', 0) or stp.get('total') or stp.get('quiz_class'):
                return 'quiz'
            types = [t for t in f0.get('types') or [] if t not in ('checkbox', 'radio', 'hidden')]
            if f0.get('kind') == 'email-capture':
                return 'email-capture'
            if types and all(t == 'tel' for t in types):
                return 'callback-request'
            if 'range' in types or re.search(r'калькулятор|рассчитать стоимость|расч[её]т стоимости|calculator|итого|результат расч', (s.get('text') or '')[:600], re.I):
                return 'calculator'
        if re.search(r'скача|download|получите (гайд|чек-?лист|pdf|книгу|материал)|guide|ebook|checklist', (s.get('text') or '')[:300], re.I):
            return 'lead-magnet'
        return 'lead-form'
    if role in ('cta-band', 'final-cta'):
        if s.get('app_badges', 0):
            return 'app-download'
        if (s.get('tel', 0) + s.get('messengers', 0)) >= 2 and s.get('ctas_primary', 0) <= 1:
            return 'contact-channels'
        return 'cta-band'
    if role == 'faq':
        return 'faq'
    if role == 'about':
        if len(re.findall(r'\b(19|20)\d\d\b', s.get('text') or '')) >= 3:
            return 'timeline'
        if re.search(r'основател|founder|генеральн\w* директор|ceo', s.get('text') or '', re.I):
            return 'founder-note'
        return 'about-story'
    if role == 'team':
        return 'team-grid'
    if role == 'portfolio':
        return 'gallery' if rp.get('words', 99) <= 4 else 'portfolio-grid'
    if role == 'event-program':
        if re.search(r'модул|урок|curriculum|syllabus|module|lesson', s.get('text') or '', re.I):
            return 'curriculum'
        if re.search(r'спикер|speaker|докладчик', s.get('text') or '', re.I) and rp.get('avatar', 0) + rp.get('img', 0) >= 0.5:
            return 'speakers-grid'
        return 'event-agenda'
    if role == 'contacts':
        return 'location-map' if s.get('maps', 0) else 'contact-details'
    if role == 'related':
        return 'article-cards' if rp.get('n', 0) >= 2 else 'related-links'
    if role == 'article-body':
        return 'article-body' if s.get('words', 0) >= 700 and s.get('p', 0) >= 8 else 'prose'
    if role == 'story':
        return 'media-band' if s.get('media_pct', 0) >= 70 else 'prose'
    if role == 'legal':
        return 'legal-text'
    if role == 'objections':
        return 'faq' if s.get('accordion', 0) >= 2 else 'prose'
    if s.get('media_pct', 0) >= 80 and s.get('words', 0) <= 15:
        return 'media-band'
    if s.get('words', 0) >= 120 and rp.get('n', 0) < 3:
        return 'prose'
    return 'other'


def analyze_post(d):
    """Классы секций и сводка страницы (вызывается после замера и при --reclassify)."""
    dom = d.get('dom') or {}
    if dom.get('error'):
        d['summary'] = {'error': dom['error'], 'blocked': d.get('blocked')}
        return d
    cls = classify_sections(d)
    d['classes'] = {'vocab': VOCAB, 'date': time.strftime('%Y-%m-%d %H:%M'), 'sections': cls}
    secs = dom.get('sections') or []
    hdr = dom.get('header')
    roles = ['header'] if hdr else []
    roles += [c['role'] for c in cls if not (c['role'] == 'header' and hdr)]
    ctas = dom.get('ctas') or []
    prim = [c for c in ctas if c.get('str') == 'primary' and c.get('loc') != 'footer']
    norm_t = lambda t: re.sub(r'[^\w]+', ' ', (t or '').lower()).strip()
    cnt = {}
    for c in prim:
        cnt[norm_t(c['t'])] = cnt.get(norm_t(c['t']), 0) + 1
    tg = {}
    for c in ctas:
        if c.get('loc') != 'footer':
            tg[c['tgt']] = tg.get(c['tgt'], 0) + 1
    scan = d.get('sticky_scan') or []
    sticky_bars = [b for sc_ in scan for b in (sc_.get('bars') or []) if not b.get('chat')]
    chat_bars = [b for sc_ in scan for b in (sc_.get('bars') or []) if b.get('chat')]
    sticky_top = [t for sc_ in scan for t in (sc_.get('top') or [])]
    forms = dom.get('forms') or []
    lead_vis = [f for f in forms if f.get('kind') in ('lead', 'email-capture') and f.get('visible') and not f.get('in_popup')]
    lead_pop = [f for f in forms if f.get('kind') in ('lead', 'email-capture') and (f.get('in_popup') or not f.get('visible'))]

    def cmode(f):
        if f.get('consent_pd_n', 0) >= 1 and f.get('consent_mkt_n', 0) >= 1:
            return 'separate'
        if f.get('consent_pd_n', 0) >= 1:
            return 'pd-checkbox'
        if f.get('consent_both_n', 0) >= 1:
            return 'combined'
        if f.get('consents'):
            return 'mkt-only'
        if f.get('notice'):
            return 'notice'
        return 'none'
    modes = [cmode(f) for f in lead_vis + lead_pop]
    order = ['separate', 'pd-checkbox', 'combined', 'mkt-only', 'notice', 'none']
    best_mode = min(modes, key=order.index) if modes else None
    steps_max = 1
    for f in lead_vis + lead_pop:
        stp = f.get('steps') or {}
        if stp.get('total'):
            steps_max = max(steps_max, stp['total'])
        elif stp.get('next_buttons') or stp.get('quiz_class'):
            steps_max = max(steps_max, 2)
    pre = d.get('pre') or {}
    lcp = (pre.get('lcp') or [None])[-1] if pre.get('lcp') else None
    lt = pre.get('lt') or []
    tbt = sum(max(0, x[1] - 50) for x in lt)
    fin = d.get('fin') or {}
    tbt_all = sum(max(0, x[1] - 50) for x in fin.get('lt') or [])
    cmp = d.get('cmp') or {}
    ban = (cmp.get('banners') or [None])[0]
    net = d.get('network') or {}
    meta = dom.get('meta') or {}
    canon = meta.get('canonical')
    canon_self = None
    if canon:
        try:
            cu = urllib.parse.urljoin(d.get('final_url') or d['url'], canon)
            fu = d.get('final_url') or d['url']
            canon_self = urllib.parse.urlsplit(cu)._replace(query='', fragment='').geturl().rstrip('/') == urllib.parse.urlsplit(fu)._replace(query='', fragment='').geturl().rstrip('/')
        except Exception:
            canon_self = None
    inp = d.get('inp') or {}
    fs_ctas = [c for c in prim if c.get('first_screen')]
    d['summary'] = {
        'blocked': d.get('blocked'), 'platform': ';'.join(dom.get('platform') or []),
        'route_ok': d.get('route_ok'), 'net_failed_n': net.get('failed_n'),
        'net_issue': bool(d.get('route_ok') is False or d.get('status') is None or (net.get('failed_n') or 0) >= 10 or any(str(x).startswith('goto') for x in d.get('log') or [])),
        'sections_n': len([c for c in cls if c['role'] not in ('footer', 'header')]), 'section_seq': '>'.join(roles), 'block_seq': '>'.join(c['block'] for c in cls),
        'unknown_n': sum(1 for c in cls if c['role'] == 'other'), 'doc_h_vh': round((dom.get('doc_h') or 0) / (dom.get('vh') or 900), 1),
        'words_total': dom.get('words_total'), 'overflow_x_px': dom.get('overflow_x'), 'layout_zoomed': bool((dom.get('layout_vw') or 0) > (dom.get('vw') or 0) + 2),
        'cta_n': len(prim), 'cta_secondary_n': len([c for c in ctas if c.get('str') == 'secondary' and c.get('loc') != 'footer']),
        'cta_first_screen': len(fs_ctas), 'cta_header': any(c.get('loc') == 'header' for c in prim),
        'cta_filled_n': len([c for c in prim if c.get('style') == 'filled']), 'cta_repeat_max': max(cnt.values()) if cnt else 0, 'cta_distinct': len(cnt),
        'cta_top_text': max(cnt, key=cnt.get) if cnt else None, 'cta_targets': tg,
        'sticky_cta': bool(sticky_bars) or any(c.get('loc') == 'sticky' for c in prim), 'sticky_cta_texts': sorted({t for b in sticky_bars for t in b.get('texts') or []})[:4],
        'chat_widget': bool(chat_bars) or any(o.get('kind') == 'chat' for o in dom.get('overlays') or []),
        'header': bool(hdr), 'header_sticky': bool(sticky_top) or bool(hdr and str(hdr.get('position')).startswith(('fixed', 'sticky'))),
        'header_transparent_over_hero': bool(hdr and hdr.get('over_hero')), 'header_nav_links': hdr.get('nav_links') if hdr else None,
        'header_phone': bool(hdr and hdr.get('phone')), 'header_messengers': hdr.get('messengers') if hdr else None, 'burger': bool(hdr and hdr.get('burger')),
        'logo_home': hdr.get('logo_home') if hdr else None, 'mega_menu': bool(hdr and (hdr.get('hidden_links') or 0) >= 12),
        'forms_n': len(lead_vis), 'forms_popup_n': len(lead_pop), 'form_fields_max': max([f.get('fields_total', 0) for f in lead_vis], default=0),
        'form_fields_min': min([f.get('fields_total', 0) for f in lead_vis], default=0), 'form_steps': steps_max if (lead_vis or lead_pop) else 0,
        'form_first_screen': any(f.get('first_screen') for f in lead_vis), 'consent_mode': best_mode,
        'consent_separate': (best_mode in ('separate', 'pd-checkbox')) if best_mode else None,
        'consent_prechecked': any(f.get('consent_prechecked') for f in lead_vis + lead_pop) if (lead_vis or lead_pop) else None,
        'policy_link_in_form': any(f.get('policy_link') for f in lead_vis) if lead_vis else None,
        'captcha': ';'.join(sorted({k for f in forms for k, v in (f.get('captcha') or {}).items() if v})) or None,
        'honeypot': any(f.get('honeypot') for f in forms) if forms else None, 'phone_mask': any(f.get('phone_mask') for f in lead_vis) if lead_vis else None,
        'h1_n': (dom.get('headings') or {}).get('h1_visible_n'), 'h1_total': (dom.get('headings') or {}).get('h1_n'),
        'h1_first_screen': (dom.get('headings') or {}).get('h1_first_screen'), 'heading_skips': (dom.get('headings') or {}).get('skips'),
        'title_len': meta.get('title_len'), 'desc_len': meta.get('desc_len'), 'canonical': bool(canon), 'canonical_self': canon_self,
        'robots': meta.get('robots'), 'noindex': bool(re.search(r'noindex', (meta.get('robots') or '') + ' ' + (d.get('x_robots_tag') or ''), re.I)),
        'og_image': bool(meta.get('og_image')), 'og_title': bool(meta.get('og_title')), 'tw_card': meta.get('tw_card'), 'hreflang_n': len(meta.get('hreflang') or []),
        'jsonld_types': ';'.join(meta.get('jsonld_types') or []), 'microdata': ';'.join(meta.get('microdata') or []), 'lang': dom.get('lang'),
        'favicon_svg': any('svg' in x for x in meta.get('icons') or []), 'apple_touch': any('apple-touch' in x for x in meta.get('icons') or []),
        'footer_inn': (dom.get('footer') or {}).get('inn'), 'footer_ogrn': (dom.get('footer') or {}).get('ogrn'), 'footer_policy': (dom.get('footer') or {}).get('policy'),
        'footer_social': (dom.get('footer') or {}).get('social'), 'footer_links': (dom.get('footer') or {}).get('links'), 'made_on_badge': (dom.get('footer') or {}).get('made_on'),
        'third_party_n': net.get('third_party_domains'), 'third_party_kb': net.get('third_party_kb'), 'tracking': ';'.join(net.get('tracking_vendors') or []),
        'analytics': ';'.join(v for v in (net.get('tracking_vendors') or []) if v in ('yandex-metrika', 'ga4', 'gtm', 'top-mail-ru', 'liveinternet', 'ms-clarity', 'hotjar', 'posthog', 'mixpanel', 'amplitude', 'segment', 'plausible', 'heap', 'vercel-analytics', 'cloudflare-web-analytics')),
        'metrika_webvisor': net.get('metrika_webvisor'),
        'cmp': (ban.get('vendor') or ('banner' if ban else None)) if ban else 'none', 'cmp_kind': ('choice' if ban and ban.get('has_reject') else ('notice' if ban and not ban.get('has_reject') else None)),
        'cmp_reject_first_layer': ban.get('has_reject') if ban else None, 'cmp_reject_equal': ((ban.get('equal') or {}).get('equal') if ban and ban.get('equal') else None),
        'cmp_modal': (bool(ban.get('aria_modal') or ban.get('backdrop') or ban.get('scroll_locked'))) if ban else None, 'cmp_area_pct': ban.get('area_pct') if ban else None,
        'cmp_pos': ban.get('pos') if ban else None, 'cmp_action': cmp.get('action'),
        'analytics_before_consent': (bool(net.get('tracking_before_action')) if ban else None), 'tracking_before_action': ';'.join(net.get('tracking_before_action') or []),
        'tracking_after_reject': ';'.join(net.get('tracking_after_reject') or []) if net.get('tracking_after_reject') is not None else None,
        'cookies_before_n': len(d.get('cookies_before') or []),
        'lcp_ms': lcp.get('t') if lcp else None, 'lcp_el': ((lcp.get('tag') or '') + (':' + (lcp.get('text') or '')[:30] if lcp.get('text') else (':' + (lcp.get('url') or '').split('/')[-1][:40] if lcp.get('url') else ''))) if lcp else None,
        'cls': pre.get('cls'), 'cls_session': fin.get('cls'), 'tbt_ms': tbt, 'tbt_session_ms': tbt_all, 'fcp_ms': fin.get('fcp') or pre.get('fcp'), 'ttfb_ms': fin.get('ttfb') or pre.get('ttfb'),
        'inp_lab_ms': inp.get('inp_lab_ms'), 'inp_wv_ms': (inp.get('web_vitals') or {}).get('v') if inp.get('web_vitals') else None, 'inp_steps_done': sum(1 for x in inp.get('steps') or [] if x.get('done')),
        'first_screen_kb': (d.get('first_screen') or {}).get('kb'), 'session_kb': net.get('session_kb'), 'js_kb': net.get('js_kb'),
        'nojs_text_ratio': (d.get('nojs') or {}).get('ratio'), 'nojs_h1': (d.get('nojs') or {}).get('h1_match'), 'nojs_cta': (d.get('nojs') or {}).get('main_cta_in_raw'),
        'nojs_heads_ratio': (d.get('nojs') or {}).get('section_heads_ratio'), 'nojs_prices': f"{(d.get('nojs') or {}).get('prices_in_raw')}/{(d.get('nojs') or {}).get('prices_rendered')}" if (d.get('nojs') or {}).get('prices_rendered') else None,
    }
    return d


def draw_sheet(ims, d, path):
    from PIL import Image, ImageDraw, ImageFont
    dom = d.get('dom') or {}
    W = ims[0].width
    full = Image.new('RGB', (W, sum(i.height for i in ims)), (255, 255, 255))
    y = 0
    for im in ims:
        full.paste(im, (0, y)); y += im.height
    k = d.get('sheet_k') or (W / max(1, (dom.get('vw') or W)))
    off = d.get('sheet_offset') or 0
    dr = ImageDraw.Draw(full)
    try:
        font = ImageFont.truetype(FONT, 12)
    except Exception:
        font = ImageFont.load_default()
    cls = {c['i']: c for c in ((d.get('classes') or {}).get('sections') or [])}
    hdr = dom.get('header')
    if hdr:
        yy = int((hdr.get('y', 0) - off) * k)
        dr.rectangle([0, yy, W - 1, yy + max(2, int(hdr.get('h', 0) * k))], outline=(0, 90, 255), width=1)
        dr.rectangle([0, yy, min(W, 120), yy + 15], fill=(0, 90, 255)); dr.text((3, yy + 1), 'header', fill=(255, 255, 255), font=font)
    for s in dom.get('sections') or []:
        c = cls.get(s['i'], {})
        y0 = int((s['y'] - off) * k); y1 = int((s['y'] + s['h'] - off) * k)
        dr.line([0, y0, W, y0], fill=(230, 0, 60), width=2)
        lab = f"#{s['i']} {c.get('role', '?')} · {c.get('block', '?')} {c.get('conf', '')}"
        tw = dr.textlength(lab, font=font) if hasattr(dr, 'textlength') else 7 * len(lab)
        dr.rectangle([0, y0, min(W, int(tw) + 8), y0 + 15], fill=(230, 0, 60)); dr.text((3, y0 + 1), lab, fill=(255, 255, 255), font=font)
        dr.line([0, y1, W, y1], fill=(255, 170, 0), width=1)
    colh = 2600
    cols = [full.crop((0, t, W, min(full.height, t + colh))) for t in range(0, full.height, colh)]
    head = 22
    sheet = Image.new('RGB', (len(cols) * (W + 10), head + max(c.height for c in cols)), (245, 245, 245))
    dr2 = ImageDraw.Draw(sheet)
    try:
        f2 = ImageFont.truetype(FONT, 13)
    except Exception:
        f2 = font
    dr2.text((4, 3), f"{d.get('id') or ''} · {d.get('device')} · {d.get('page_type') or ''} · {d.get('url', '')[:90]} · {d.get('date')}", fill=(0, 0, 0), font=f2)
    for i, c in enumerate(cols):
        sheet.paste(c, (i * (W + 10), head))
    sheet.save(path, 'JPEG', quality=68, optimize=True)
    return os.path.basename(path)


# ------------------------------------------------------------------------------------------------ PSI / CrUX
def psi(url, strategy='mobile'):
    """PageSpeed Insights API v5. Ключ — только из окружения PSI_API_KEY (не печатается). Без ключа квота API = 0."""
    key = os.environ.get('PSI_API_KEY')
    q = {'url': url, 'strategy': strategy, 'category': 'performance'}
    if key:
        q['key'] = key
    api = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?' + urllib.parse.urlencode(q)
    out = {'strategy': strategy, 'date': time.strftime('%Y-%m-%d %H:%M'), 'keyed': bool(key)}
    try:
        with urllib.request.urlopen(urllib.request.Request(api, headers={'User-Agent': 'Mozilla/5.0'}), timeout=150) as r:
            j = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            er = json.loads(e.read().decode()).get('error') or {}
        except Exception:
            er = {}
        out.update({'http': e.code, 'error': (er.get('status') or '') + ' ' + (er.get('message') or '')[:200]})
        return out
    except Exception as e:
        out['error'] = type(e).__name__ + ' ' + str(e)[:120]
        return out

    def pick(x):
        m = x.get('metrics') or {}
        r = {k: (m.get(k) or {}).get('percentile') for k in ('LARGEST_CONTENTFUL_PAINT_MS', 'INTERACTION_TO_NEXT_PAINT', 'CUMULATIVE_LAYOUT_SHIFT_SCORE',
                                                             'FIRST_CONTENTFUL_PAINT_MS', 'EXPERIMENTAL_TIME_TO_FIRST_BYTE')}
        r.update({'category': x.get('overall_category'), 'id': x.get('id'), 'origin_fallback': x.get('origin_fallback')})
        return r
    lh = j.get('lighthouseResult') or {}
    au = lh.get('audits') or {}
    out.update({'url_level': pick(j.get('loadingExperience') or {}), 'origin': pick(j.get('originLoadingExperience') or {}),
                'lab': {'lcp_ms': (au.get('largest-contentful-paint') or {}).get('numericValue'), 'tbt_ms': (au.get('total-blocking-time') or {}).get('numericValue'),
                        'cls': (au.get('cumulative-layout-shift') or {}).get('numericValue'), 'score': ((lh.get('categories') or {}).get('performance') or {}).get('score')},
                'lighthouse': lh.get('lighthouseVersion')})
    return out


# ------------------------------------------------------------------------------------------------ блокировки, пакет
def read_pages(path):
    rows = []
    with open(path, encoding='utf-8') as fh:
        lines = [l for l in fh if l.strip() and not l.startswith('#')]
    for r in csv.DictReader(lines, delimiter='\t'):
        rows.append({k: (v or '').strip() for k, v in r.items() if k})
    return rows


def run_batch(a):
    import signal
    rows = read_pages(a.batch)
    only = set(x.strip() for x in (a.only or '').split(',') if x.strip())
    devices = [d.strip() for d in a.devices.split(',') if d.strip()]
    logp = os.path.join(os.path.abspath(a.out), 'batch.log')
    os.makedirs(os.path.dirname(logp), exist_ok=True)
    for row in rows:
        if only and row.get('id') not in only:
            continue
        if row.get('skip') in ('1', 'yes', 'true'):
            continue
        for dev in devices:
            outdir = os.path.join(os.path.abspath(a.out), row['id'])
            if a.skip_done and os.path.exists(os.path.join(outdir, f'anatomy_{dev}.json')):
                continue
            waited = 0
            while (mem_available_gb() or 99) < 3 and waited < 900:
                time.sleep(30); waited += 30
            mem = mem_available_gb()
            if (mem or 99) < 3:
                open(logp, 'a').write(f"{time.strftime('%H:%M:%S')}\t{row['id']}\t{dev}\tSKIP mem {mem:.1f} GB\n"); continue
            cmd = [sys.executable, os.path.abspath(__file__), row['url'], outdir, '--id', row['id'], '--net', row.get('net') or 'auto',
                   '--wait', str(a.wait), '--timeout', str(a.timeout), '--no-lock']   # замки тишины держит пакетный прогон
            for k, opt_ in (('page_type', '--label'), ('market', '--market'), ('industry', '--industry'), ('site_type', '--site-type'),
                            ('text_id', '--text-id'), ('template', '--template'), ('site_id', '--site-id'), ('source', '--source')):
                if row.get(k):
                    cmd += [opt_, row[k]]
            if dev == 'mobile':
                cmd.append('--mobile')
            if a.inp:
                cmd.append('--inp')
            t0 = time.time(); rc = None; tail = ''
            with PG.heavy_lock(domains=('site',)):
                tl = time.time()
                pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
                try:
                    so, se = pr.communicate(timeout=a.page_timeout); rc = pr.returncode
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(pr.pid, signal.SIGKILL)
                    except Exception:
                        pass
                    so, se = pr.communicate(); rc = 'timeout'
                held = time.time() - tl
            tail = (so or '').strip().splitlines()[-1:] or (se or '').strip().splitlines()[-1:]
            line = f"{time.strftime('%H:%M:%S')}\t{row['id']}\t{dev}\trc={rc}\t{time.time() - t0:.0f}s\tlock {held:.0f}s\tmem {mem:.1f}\t{(tail[0] if tail else '')[:300]}\n"
            open(logp, 'a').write(line)
            print(line.strip(), flush=True)


# ------------------------------------------------------------------------------------------------ CSV
CSV_COLS = ['id', 'url', 'page_type', 'site_type', 'market', 'industry', 'date', 'net', 'device', 'sections_n', 'section_seq', 'cta_n', 'cta_first_screen',
            'sticky_cta', 'forms_n', 'form_fields_max', 'form_steps', 'consent_separate', 'consent_prechecked', 'captcha', 'h1_n', 'title_len', 'desc_len',
            'canonical', 'og_image', 'jsonld_types', 'lang', 'third_party_n', 'analytics', 'cmp', 'cmp_reject_equal', 'analytics_before_consent', 'lcp_ms',
            'lcp_el', 'cls', 'tbt_ms', 'inp_lab_ms', 'crux_lcp_p75', 'crux_inp_p75', 'crux_cls_p75', 'first_screen_kb', 'session_kb', 'js_kb', 'nojs_text_ratio',
            # дополнительные
            'text_id', 'site_id', 'template', 'source', 'locale', 'cpu_throttle', 'status', 'blocked', 'platform', 'block_seq', 'unknown_n', 'doc_h_vh',
            'words_total', 'cta_secondary_n', 'cta_header', 'cta_filled_n', 'cta_repeat_max', 'cta_distinct', 'cta_top_text', 'sticky_cta_texts', 'chat_widget',
            'header_sticky', 'header_transparent_over_hero', 'header_nav_links', 'header_phone', 'header_messengers', 'burger', 'logo_home', 'mega_menu',
            'forms_popup_n', 'form_fields_min', 'form_first_screen', 'consent_mode', 'policy_link_in_form', 'honeypot', 'phone_mask', 'h1_first_screen',
            'heading_skips', 'canonical_self', 'noindex', 'og_title', 'tw_card', 'hreflang_n', 'microdata', 'favicon_svg', 'apple_touch', 'footer_inn',
            'footer_ogrn', 'footer_policy', 'footer_social', 'footer_links', 'made_on_badge', 'third_party_kb', 'tracking', 'metrika_webvisor', 'cmp_kind',
            'cmp_reject_first_layer', 'cmp_modal', 'cmp_area_pct', 'cmp_pos', 'cmp_action', 'tracking_before_action', 'tracking_after_reject',
            'cookies_before_n', 'cls_session', 'tbt_session_ms', 'fcp_ms', 'ttfb_ms', 'inp_wv_ms', 'inp_steps_done', 'nojs_h1', 'nojs_cta', 'nojs_heads_ratio',
            'nojs_prices', 'server_country', 'net_basis', 'crux_level', 'route_ok', 'net_failed_n', 'net_issue']


def _fmt(v):
    if v is None:
        return ''
    if isinstance(v, bool):
        return '1' if v else '0'
    if isinstance(v, float):
        return f'{v:.4g}' if abs(v) < 1 else f'{v:.1f}'.rstrip('0').rstrip('.')
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)[:300]
    return str(v).replace('\t', ' ').replace('\n', ' ')


def build_csv(root, pages_path, fh):
    meta = {r['id']: r for r in read_pages(pages_path)} if pages_path else {}
    w = csv.writer(fh)
    w.writerow(CSV_COLS)
    ids = sorted(os.listdir(root))
    for pid in ids:
        d0 = os.path.join(root, pid)
        if not os.path.isdir(d0):
            continue
        for dev in ('desktop', 'mobile'):
            fp = os.path.join(d0, f'anatomy_{dev}.json')
            if not os.path.exists(fp):
                continue
            d = json.load(open(fp))
            s = d.get('summary') or {}
            m = meta.get(pid, {})
            cr = {}
            cp = os.path.join(d0, f'crux_{dev}.json')
            if os.path.exists(cp):
                try:
                    cj = json.load(open(cp)); lvl = 'url' if not (cj.get('url_level') or {}).get('origin_fallback') and (cj.get('url_level') or {}).get('LARGEST_CONTENTFUL_PAINT_MS') else 'origin'
                    src = cj.get('url_level') if lvl == 'url' else cj.get('origin')
                    src = src or {}
                    cr = {'crux_lcp_p75': src.get('LARGEST_CONTENTFUL_PAINT_MS'), 'crux_inp_p75': src.get('INTERACTION_TO_NEXT_PAINT'),
                          'crux_cls_p75': (src.get('CUMULATIVE_LAYOUT_SHIFT_SCORE') / 100) if src.get('CUMULATIVE_LAYOUT_SHIFT_SCORE') is not None else None,
                          'crux_level': lvl if src.get('LARGEST_CONTENTFUL_PAINT_MS') else ('error' if cj.get('error') else 'none')}
                except Exception:
                    cr = {}
            row = {'id': pid, 'url': d.get('url'), 'page_type': d.get('page_type') or m.get('page_type'), 'site_type': d.get('site_type') or m.get('site_type'),
                   'market': d.get('market'), 'industry': d.get('industry') or m.get('industry'), 'date': d.get('date'), 'net': d.get('net'), 'device': dev,
                   'text_id': d.get('text_id') or m.get('text_id'), 'site_id': d.get('site_id') or m.get('site_id'), 'template': d.get('template') or m.get('template'),
                   'source': d.get('source') or m.get('source'), 'locale': d.get('locale'), 'cpu_throttle': d.get('cpu_throttle'), 'status': d.get('status'),
                   'server_country': d.get('server_country'), 'net_basis': d.get('net_basis')}
            row.update(s); row.update(cr)
            if s.get('net_issue'):
                row['net'] = 'unknown'; row['net_basis'] = 'сбой сети или смена маршрута во время замера'
            row['route_ok'] = s.get('route_ok')
            w.writerow([_fmt(row.get(c)) for c in CSV_COLS])


def reclassify(root):
    n = 0
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.startswith('anatomy_') and f.endswith('.json'):
                p = os.path.join(dp, f)
                d = json.load(open(p))
                analyze_post(d)
                json.dump(d, open(p, 'w'), ensure_ascii=False, indent=1)
                n += 1
    print(f'пересчитано файлов: {n}')


# ------------------------------------------------------------------------------------------------ самопроверка
SELFTEST_HTML = r"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Пластиковые окна в Самаре — установка за 1 день | ОкнаТест</title>
<meta name="description" content="Тестовая страница page_anatomy.py: окна под ключ, замер бесплатно, гарантия 5 лет, установка за один день.">
<link rel="canonical" href="/index.html"><meta property="og:title" content="ОкнаТест — окна за 1 день"><meta property="og:image" content="/og.png">
<meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization","name":"ОкнаТест"},
{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Сколько стоит замер?","acceptedAnswer":{"@type":"Answer","text":"Замер бесплатный."}}]}]}</script>
<script src="https://mc.yandex.ru/metrika/tag.js" async></script>
<style>
*{box-sizing:border-box}body{margin:0;font:16px/1.5 sans-serif;color:#222}a{color:#0a58ca}
.site-header{position:sticky;top:0;z-index:10;display:flex;gap:24px;align-items:center;justify-content:space-between;padding:14px 40px;background:#fff;border-bottom:1px solid #eee}
.site-header nav a{margin-right:18px;text-decoration:none}.phone{white-space:nowrap}.btn{display:inline-block;padding:14px 28px;background:#e8452c;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;border:0;font-size:16px}
.btn2{display:inline-block;padding:12px 24px;border:2px solid #e8452c;border-radius:8px;color:#e8452c;text-decoration:none;margin-left:12px}
section{padding:80px 40px}section h2{font-size:36px;margin:0 0 32px}.hero{display:flex;gap:40px;align-items:center;min-height:620px;background:#f4f7fb}
.hero h1{font-size:52px;margin:0 0 16px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px}.card,.rcard{padding:24px;border:1px solid #ddd;border-radius:12px}
.card h3{font-size:20px;margin:12px 0 8px}.reviews .grid{grid-template-columns:repeat(3,1fr)}.ava{width:64px;height:64px;border-radius:50%}
.reviews{background:#fafafa}details{border-bottom:1px solid #ddd;padding:16px 0}summary{font-size:20px;cursor:pointer}
.lead{background:#1d2b44;color:#fff}.lead form{display:grid;gap:14px;max-width:520px}.lead input[type=text],.lead input[type=tel],.lead input[type=email]{padding:14px;border-radius:8px;border:0;font-size:16px}
.lead a{color:#9cc3ff}footer{padding:40px;background:#111;color:#bbb}footer a{color:#ddd;margin-right:16px}
.cookie{position:fixed;left:24px;bottom:24px;max-width:420px;padding:18px;background:#fff;border:1px solid #ccc;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.2);z-index:50}
.cbtn{padding:10px 20px;margin-right:8px;background:#222;color:#fff;border:0;border-radius:6px;font-size:14px}.burger{display:none;font-size:24px;background:none;border:0}
.mbar{display:none}
@media (max-width:700px){.site-header{padding:10px 16px;gap:10px}.site-header nav,.site-header .btn{display:none}.phone{font-size:14px}.burger{display:block}.hero{flex-direction:column;min-height:auto}.hero h1{font-size:34px}
.grid,.reviews .grid{grid-template-columns:1fr}section{padding:48px 20px}.mbar{display:block;position:fixed;left:0;right:0;bottom:0;padding:10px;background:#fff;box-shadow:0 -4px 12px rgba(0,0,0,.15);z-index:40}
.mbar .btn{display:block;text-align:center}.cookie{left:8px;right:8px;bottom:80px}.hero img{width:100%;height:auto}}
body.menu-open nav{display:flex!important;flex-direction:column;position:fixed;top:60px;left:0;right:0;background:#fff;padding:20px}
</style></head><body>
<header class="site-header"><a href="/" class="logo" aria-label="ОкнаТест"><svg width="120" height="32" viewBox="0 0 120 32"><rect width="120" height="32" rx="6" fill="#1d2b44"/><text x="10" y="22" fill="#fff" font-size="16">ОкнаТест</text></svg></a>
<nav><a href="#benefits">Преимущества</a> <a href="#reviews">Отзывы</a> <a href="#faq">Вопросы</a> <a href="#form">Контакты</a></nav>
<a class="phone" href="tel:+78461234567">+7 (846) 123-45-67</a><a class="btn" href="#form">Оставить заявку</a><button class="burger" aria-label="Меню">≡</button></header>
<main>
<section class="hero"><div><h1>Пластиковые окна за 1 день</h1><p>Замер бесплатно. Гарантия 5 лет. Цена от <span id="price"></span> за окно.</p>
<a class="btn" href="#form">Оставить заявку</a><a class="btn2" href="#benefits">Подробнее</a></div><img src="hero.png" width="600" height="400" alt="Окно в квартире"></section>
<section id="benefits" class="benefits"><h2>Преимущества</h2><div class="grid">
<div class="card"><svg width="40" height="40"><circle cx="20" cy="20" r="18" fill="#e8452c"/></svg><h3>Свой завод</h3><p>Производим окна сами, без посредников и наценок.</p></div>
<div class="card"><svg width="40" height="40"><circle cx="20" cy="20" r="18" fill="#e8452c"/></svg><h3>Монтаж за день</h3><p>Бригада снимает старые окна и ставит новые за один день.</p></div>
<div class="card"><svg width="40" height="40"><circle cx="20" cy="20" r="18" fill="#e8452c"/></svg><h3>Гарантия 5 лет</h3><p>Договор с гарантией на окна, фурнитуру и монтаж.</p></div>
<div class="card"><svg width="40" height="40"><circle cx="20" cy="20" r="18" fill="#e8452c"/></svg><h3>Бесплатный замер</h3><p>Замерщик приедет в удобное время и привезёт образцы.</p></div>
</div></section>
<section id="reviews" class="reviews"><h2>Отзывы клиентов</h2><div class="grid">
<div class="rcard"><img class="ava" src="ava.png" alt="Анна"><blockquote>«Поставили окна за день, всё аккуратно, мусор убрали за собой. Рекомендую компанию друзьям и соседям.»</blockquote><p>Анна, Самара</p></div>
<div class="rcard"><img class="ava" src="ava.png" alt="Игорь"><blockquote>«Замерщик приехал в тот же день, цену не меняли после договора. В квартире стало заметно тише и теплее.»</blockquote><p>Игорь, Тольятти</p></div>
<div class="rcard"><img class="ava" src="ava.png" alt="Мария"><blockquote>«Заказывали три окна и балкон, всё сделали точно в срок, как обещали менеджеры при оформлении.»</blockquote><p>Мария, Самара</p></div>
</div></section>
<section id="faq" class="faq"><h2>Частые вопросы</h2>
<details><summary>Сколько стоит замер?</summary><p>Замер бесплатный в пределах города.</p></details>
<details><summary>Сколько времени занимает монтаж?</summary><p>Один день на квартиру до четырёх окон.</p></details>
<details><summary>Какая гарантия на окна?</summary><p>Пять лет на окна и монтаж по договору.</p></details>
<details><summary>Можно ли оплатить в рассрочку?</summary><p>Да, рассрочка на шесть месяцев без переплаты.</p></details></section>
<section id="form" class="lead"><h2>Оставьте заявку на бесплатный замер</h2><form action="#" onsubmit="return false">
<input type="text" name="name" placeholder="Имя" autocomplete="name"><input type="tel" name="phone" placeholder="+7 (___) ___-__-__" required autocomplete="tel">
<input type="email" name="email" placeholder="E-mail" autocomplete="email"><input type="text" name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px">
<label><input type="checkbox" name="pd" required> Даю согласие на обработку персональных данных</label>
<label><input type="checkbox" name="news"> Согласен получать рекламную рассылку</label>
<a href="/policy.html">Политика конфиденциальности</a><button type="submit" class="btn">Отправить заявку</button></form></section>
</main>
<footer><nav><a href="/">Главная</a> <a href="/policy.html">Политика конфиденциальности</a> <a href="#benefits">Преимущества</a> <a href="#reviews">Отзывы</a> <a href="#faq">Вопросы</a> <a href="#form">Заявка</a></nav>
<p>ООО «ОкнаТест», ИНН 6312345678, ОГРН 1126312345678, г. Самара, ул. Тестовая, д. 1</p><a href="https://vk.com/oknatest">ВКонтакте</a><p>© 2026 ОкнаТест</p></footer>
<div class="cookie" id="cookie-banner"><p>Мы используем файлы cookie и Яндекс Метрику, чтобы сайт работал лучше.</p>
<button class="cbtn" onclick="this.parentNode.remove()">Принять</button><button class="cbtn" onclick="this.parentNode.remove()">Отклонить</button></div>
<div class="mbar"><a class="btn" href="#form">Записаться на замер</a></div>
<script>
document.getElementById('price').textContent = '9 900 ₽';
document.querySelectorAll('summary').forEach(s => s.addEventListener('click', () => { const t = performance.now(); while (performance.now() - t < 220) {} }));
document.querySelector('.burger').addEventListener('click', () => document.body.classList.toggle('menu-open'));
</script></body></html>
"""


def _serve(root):
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *aa, **kk):
            super().__init__(*aa, directory=root, **kk)

        def log_message(self, *aa):
            pass

    class TS(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True
        allow_reuse_address = True
    srv = TS(('127.0.0.1', 0), H)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    return srv


REVEAL_HTML = """<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>H1 появляется</title>
<style>body{margin:0;font:18px sans-serif} h1{font-size:48px;margin:40px;animation:rv 1.2s .4s both} @keyframes rv{from{opacity:0}to{opacity:1}}</style>
</head><body><h1>Заголовок появляется из прозрачности</h1><p style="margin:40px">Текст первого экрана.</p></body></html>"""


def selftest(a):
    """Тестовая страница во временной папке (локальный сервер, «Метрика» подменена без сети): классы секций, призывы, формы,
    согласия, баннер cookie, текст без JS, INP, LCP; UA как есть (HeadlessChrome) и navigator.webdriver; показ H1 во
    времени — на странице, где H1 появляется из прозрачности."""
    import tempfile
    from PIL import Image, ImageDraw
    with tempfile.TemporaryDirectory(prefix='page-anatomy-selftest-') as sd:
        open(os.path.join(sd, 'index.html'), 'w', encoding='utf-8').write(SELFTEST_HTML)
        open(os.path.join(sd, 'reveal.html'), 'w', encoding='utf-8').write(REVEAL_HTML)
        im = Image.new('RGB', (1200, 800), (180, 200, 220)); ImageDraw.Draw(im).rectangle([100, 100, 1100, 700], outline=(255, 255, 255), width=20)
        im.save(os.path.join(sd, 'hero.png'))
        Image.new('RGB', (128, 128), (200, 150, 120)).save(os.path.join(sd, 'ava.png'))
        Image.new('RGB', (1200, 630), (29, 43, 68)).save(os.path.join(sd, 'og.png'))
        open(os.path.join(sd, 'favicon.svg'), 'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect width="16" height="16" fill="#1d2b44"/></svg>')
        open(os.path.join(sd, 'policy.html'), 'w', encoding='utf-8').write('<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Политика</title></head><body><h1>Политика</h1></body></html>')
        srv = _serve(sd)
        base = f'http://127.0.0.1:{srv.server_address[1]}'
        results = {}
        common = dict(no_cmp_close=False, label='landing-lead-services', id='selftest', market='ru', industry='окна', net='local',
                      site_type='landing-site', text_id=None, template='landing', site_id=None, source='selftest', timeout=30, cpu=None, selftest=True)
        try:
            with PG.heavy_lock(domains=('site',)):
                for dev in ('desktop', 'mobile'):
                    ns = argparse.Namespace(url=base + '/index.html', out=os.path.join(sd, 'out'), mobile=(dev == 'mobile'), inp=True, quick=False,
                                            wait=2500, **common)
                    results[dev] = run_page(ns)
                rv = run_page(argparse.Namespace(url=base + '/reveal.html', out=os.path.join(sd, 'out-reveal'), mobile=False, inp=False,
                                                 quick=True, wait=2500, **common))
        finally:
            srv.shutdown(); srv.server_close()
    checks = []

    def ck(name, cond, got):
        checks.append((name, bool(cond), got))
    for dev, d in results.items():
        s = d.get('summary') or {}
        roles = [c['role'] for c in (d.get('classes') or {}).get('sections') or []]
        ck(f'{dev}: порядок ролей', roles[:5] == ['hero', 'benefits', 'testimonials', 'faq', 'lead-form'] and roles[-1] == 'footer', roles)
        ck(f'{dev}: шапка найдена', s.get('header'), s.get('header'))
        ck(f'{dev}: CTA ≥ 3' + (', повтор «оставить заявку» ≥ 2' if dev == 'desktop' else ''), s.get('cta_n', 0) >= 3 and (dev == 'mobile' or s.get('cta_repeat_max', 0) >= 2),
           (s.get('cta_n'), s.get('cta_repeat_max'), s.get('cta_top_text')))
        ck(f'{dev}: нет горизонтального переполнения', not s.get('layout_zoomed') and (s.get('overflow_x_px') or 0) <= 2, (s.get('overflow_x_px'), s.get('layout_zoomed')))
        ck(f'{dev}: форма 3 поля, согласия раздельные, не отмечены', s.get('form_fields_max') == 3 and s.get('consent_mode') == 'separate' and s.get('consent_prechecked') is False,
           (s.get('form_fields_max'), s.get('consent_mode'), s.get('consent_prechecked')))
        ck(f'{dev}: ловушка honeypot и ссылка на политику', s.get('honeypot') and s.get('policy_link_in_form'), (s.get('honeypot'), s.get('policy_link_in_form')))
        ck(f'{dev}: баннер — «Отклонить» на первом слое, кнопки равны, нажато «Отклонить»',
           s.get('cmp_reject_first_layer') and s.get('cmp_reject_equal') and s.get('cmp_action') == 'reject', (s.get('cmp_reject_first_layer'), s.get('cmp_reject_equal'), s.get('cmp_action')))
        ck(f'{dev}: Метрика до выбора', 'yandex-metrika' in (s.get('tracking_before_action') or ''), s.get('tracking_before_action'))
        ck(f'{dev}: цена из JS не в сыром HTML, h1 в сыром HTML', (d.get('nojs') or {}).get('prices_in_raw') == 0 and (d.get('nojs') or {}).get('h1_match'),
           ((d.get('nojs') or {}).get('prices_in_raw'), (d.get('nojs') or {}).get('prices_rendered'), (d.get('nojs') or {}).get('h1_match')))
        ck(f'{dev}: INP ≥ 200 мс (обработчик FAQ 220 мс)', (s.get('inp_lab_ms') or 0) >= 200, (s.get('inp_lab_ms'), s.get('inp_wv_ms'), s.get('inp_steps_done')))
        ck(f'{dev}: JSON-LD Organization и FAQPage, canonical, og:image', 'Organization' in (s.get('jsonld_types') or '') and 'FAQPage' in (s.get('jsonld_types') or '') and s.get('canonical') and s.get('og_image'),
           (s.get('jsonld_types'), s.get('canonical'), s.get('og_image')))
        ck(f'{dev}: подвал — ИНН, ОГРН, политика', s.get('footer_inn') and s.get('footer_ogrn') and s.get('footer_policy'), (s.get('footer_inn'), s.get('footer_ogrn'), s.get('footer_policy')))
        ck(f'{dev}: LCP и контактный лист', s.get('lcp_ms') is not None and d.get('sheet'), (s.get('lcp_ms'), s.get('lcp_el'), d.get('sheet')))
    dm = (results.get('mobile') or {}).get('summary') or {}
    ck('mobile: липкий CTA внизу', dm.get('sticky_cta'), dm.get('sticky_cta_texts'))
    ck('mobile: кнопка меню', dm.get('burger'), dm.get('burger'))
    for dev, d in results.items():
        ck(f"{dev}: UA как есть — HeadlessChrome, navigator.webdriver виден", 'HeadlessChrome/' in (d.get('ua') or '') and d.get('webdriver') is True,
           ((d.get('ua') or '')[-40:], d.get('webdriver')))
    hp = (results.get('desktop') or {}).get('h1_paint') or {}
    ck('desktop: показ H1 — виден с первого кадра (статичный H1)', hp.get('first_op') == 1 and hp.get('t_visible') is not None, hp)
    hr = rv.get('h1_paint') or {}
    ck('показ H1 во времени: H1 из opacity 0 — первый кадр невидим, виден позже', hr.get('first_op') == 0 and hr.get('t_visible') is not None
       and hr['t_visible'] > hr.get('t_first', 0), hr)
    nets = {k: net_probe(argparse.Namespace(net=v, selftest=False)) for k, v in (('без ключа', None), ('auto', 'auto'), ('метка', 'vpn-lt'))}
    ck('сеть — только ключом --net: без ключа замер не ходит в ipinfo.io и yandex.ru', nets == {'без ключа': False, 'auto': True, 'метка': True}
       and all(d.get('net') == 'local' and d.get('route_before') is None for d in (*results.values(), rv)), nets)
    ok = sum(1 for c in checks if c[1])
    rep = [f'# Самопроверка page_anatomy.py', '', 'Страница: временная папка (локальный сервер, «Метрика» подменена без сети).',
           f'Итог: {ok} из {len(checks)} проверок прошли.', '', '| Проверка | Итог | Получено |', '|---|---|---|']
    rep += [f'| {n} | {"OK" if c else "FAIL"} | `{json.dumps(g, ensure_ascii=False)[:160]}` |' for n, c, g in checks]
    print('\n'.join(rep))
    return 0 if ok == len(checks) else 1


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('url', nargs='?'); ap.add_argument('out', nargs='?')
    ap.add_argument('--mobile', action='store_true'); ap.add_argument('--inp', action='store_true'); ap.add_argument('--quick', action='store_true')
    ap.add_argument('--no-cmp-close', action='store_true'); ap.add_argument('--label'); ap.add_argument('--id'); ap.add_argument('--market')
    ap.add_argument('--industry'); ap.add_argument('--site-type'); ap.add_argument('--text-id')
    ap.add_argument('--net', nargs='?', const='auto', default=None,
                    help='сеть: без ключа не проверяется; auto (или без значения) — страна и организация сервера (ipinfo.io) и '
                         'проверка раздельной маршрутизации VPN; ru-direct | vpn-lt | unknown — своя метка и проверка маршрута')
    ap.add_argument('--template'); ap.add_argument('--site-id'); ap.add_argument('--source'); ap.add_argument('--timeout', type=int, default=60)
    ap.add_argument('--wait', type=int, default=None, help='окно первого экрана после load, мс (по умолчанию — budgets.yaml)')
    ap.add_argument('--cpu', type=int, default=None); ap.add_argument('--crux', action='store_true')
    ap.add_argument('--no-lock', action='store_true', help='не брать замки тишины (обёртка их уже держит)')
    ap.add_argument('--selftest', action='store_true'); ap.add_argument('--batch'); ap.add_argument('--devices', default='desktop,mobile')
    ap.add_argument('--only'); ap.add_argument('--skip-done', action='store_true'); ap.add_argument('--page-timeout', type=int, default=270)
    ap.add_argument('--reclassify'); ap.add_argument('--csv'); ap.add_argument('--pages'); ap.add_argument('--net-of', nargs='*')
    ap.add_argument('--crux-batch'); ap.add_argument('--out', dest='out_opt')
    a = ap.parse_args()
    if a.out_opt:
        a.out = a.out_opt
    if a.wait is None:
        a.wait = PG.window_ms()
    if a.selftest and not a.url:
        sys.exit(selftest(a))
    if a.net_of:
        print(json.dumps({h: {k: v for k, v in net_of(h).items()} for h in a.net_of}, ensure_ascii=False, indent=1)); return
    if a.reclassify:
        reclassify(a.reclassify); return
    if a.csv:
        build_csv(a.csv, a.pages, sys.stdout); return
    if a.batch:
        if not a.out:
            a.out = a.url or '.'
        run_batch(a); return
    if a.crux_batch:
        for r in read_pages(a.crux_batch):
            if a.only and r['id'] not in a.only.split(','):
                continue
            od = os.path.join(a.out or '.', r['id']); os.makedirs(od, exist_ok=True)
            for dev, strat in (('mobile', 'mobile'), ('desktop', 'desktop')):
                cj = psi(r['url'], strat); json.dump(cj, open(os.path.join(od, f'crux_{dev}.json'), 'w'), ensure_ascii=False, indent=1)
                print(r['id'], dev, cj.get('http') or 'ok', (cj.get('error') or '')[:90], flush=True)
                time.sleep(2)
        return
    if not a.url or not a.out:
        print(__doc__); sys.exit(2)
    a.selftest = False
    with (contextlib.nullcontext() if a.no_lock else PG.heavy_lock(domains=('site',))):
        d = run_page(a)
    if a.crux:
        cj = psi(a.url, 'mobile' if a.mobile else 'desktop')
        json.dump(cj, open(os.path.join(a.out, f"crux_{'mobile' if a.mobile else 'desktop'}.json"), 'w'), ensure_ascii=False, indent=1)
    s = d.get('summary') or {}
    short = {k: s.get(k) for k in ('blocked', 'sections_n', 'section_seq', 'cta_n', 'cta_first_screen', 'sticky_cta', 'forms_n', 'form_fields_max', 'consent_mode',
                                   'cmp', 'cmp_action', 'analytics_before_consent', 'lcp_ms', 'cls', 'tbt_ms', 'inp_lab_ms', 'first_screen_kb', 'session_kb', 'nojs_text_ratio')}
    print(json.dumps({'id': d.get('id'), 'device': d.get('device'), 'status': d.get('status'), 't': d.get('t_total_s'), **short}, ensure_ascii=False)[:1500])


if __name__ == '__main__':
    main()
