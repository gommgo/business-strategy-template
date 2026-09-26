# Английский текст интерфейса

Волна 3 · Агент G · 22 сентября 2026.

Короткий файл: только то, что специфично для английского и не выводится из общих принципов. Общее —
`01-principles-voice-and-tone.md`, формулы по компонентам — `02-microcopy-by-component.md`, русский —
`03-russian-interface-text.md`, локализация — `05-localization-and-i18n.md`, запреты — `06`.

**Зачем он нужен, если продукт русскоязычный.** Три причины: английская версия часто делается параллельно и по ней
пишут русскую (что само по себе ошибка, см. `05` §2); большая часть дизайн-систем и компонентных библиотек
приходит с английскими текстами по умолчанию; агент-генератор обучен преимущественно на английском и по умолчанию
воспроизводит английские конвенции даже в русском интерфейсе — значит, эти конвенции надо знать, чтобы отличать
правильный перенос от неправильного.

## Выжимка для агента

1. **Sentence case по умолчанию для всего**: заголовки, кнопки, подписи, пункты меню. Title Case — только если
   продукт сознательно выбрал его для конкретного типа элементов и держит везде. `[консенсус]` → §1
2. **Никакой точки в конце** заголовков, подписей, кнопок, пунктов списка, заголовков UI. `[система]` → §2.1
3. **Оксфордская запятая обязательна**: «Android, iOS, and Windows». `[система]` → §2.2
4. **Contractions (it's, you'll, we're) — норма**, они делают тон разговорным; отсутствие делает формальным.
   `[система]` → §3.1
5. **Кнопка = {verb} + {noun}**, без артиклей: «Create collection», не «Create a collection». Исключения — Done,
   Close, Cancel, Next, Back. `[система]` → §4.1
6. **Начинать высказывание с глагола**; убирать «you can»; избегать «there is / there are». `[система]` → §3.2
7. **Устоявшиеся пары** (Sign in / Log in, Sign up / Register, Save / Done, Create / Add, Select / Choose, Edit /
   Manage, Change / Switch, View / See, Export / Download, Import / Upload) — выбирать по смыслу, а не по вкусу, и
   держать один вариант на продукт. `[система]` → §4.2
8. **Американская орфография как стандарт продуктов**: color, canceled, center, license (сущ. и глаг.), analyze.
   `[практика]` → §5
9. **Запрещено**: «Oops!», «Uh-oh», «Something went wrong», «Are you sure?», «Invalid input», «Error 500»,
   «Click here», «Submit», «OK» как подтверждение, «Please» в каждой строке, «Simply», «Just», «Easy».
   `[консенсус]` → §6
10. **Числа цифрами, даты в локализуемом формате**, время 12-часовое для США и 24-часовое для остального мира —
    берётся из локали, а не хардкодится. `[стандарт]` → §7
11. **Инклюзивный язык**: гендерно-нейтральные термины, единичное «they», никаких «he/she» и «s/he», никаких
    «master/slave», фокус на людях, а не на ограничениях. `[система]` → §8
12. **Короткий и простой английский переводится надёжнее**: «Join» машинный перевод не портит, «Become a member» во
    французском теряет нюанс. `[практика]` → §9

---

## 1. Регистр: sentence case против Title Case

### 1.1. Позиции источников

| Источник | Позиция |
|---|---|
| **Microsoft** [S1] | «When in doubt, don't capitalize. Default to sentence-style capitalization… Don't use title-style capitalization (Like This)». Причина, названная отдельно [S2]: sentence case «makes content more readable and **ensures better localizability**» |
| **Shopify Polaris** [S3] | Sentence case для заголовков, подзаголовков и кнопок без исключений |
| **Apple HIG** [S4] | «Title case is generally considered formal, while sentence case is more casual. Choose a style for each UI element type and use it consistently» — то есть выбор за продуктом, но внутри типа элемента единообразно |
| **Google Material** | Sentence case для кнопок, подписей, заголовков (по документации content design) |

**Позиция базы** `[консенсус]` с оговоркой: **sentence case по умолчанию**. Три из четырёх источников требуют его
прямо, четвёртый (Apple) допускает Title Case только как осознанный выбор продукта, применённый ко всему типу
элементов. Дополнительный аргумент Microsoft о локализуемости решает вопрос для продуктов, у которых есть русская
версия: в русском Title Case не существует как норма, и параллельные версии разойдутся визуально.

### 1.2. Исключения Microsoft

Sentence case не применяется к [S2]:

- названиям книг, белых книг и отчётов: «Unraveling HTML5, CSS3, and JavaScript»;
- названиям игр: «Sea of Thieves 2023 Edition»;
- названиям мероприятий и вебинаров: «Microsoft Envision AI Tour».

Плюс, разумеется, имена собственные, названия продуктов и торговые марки внутри строки.

### 1.3. Практические следствия

| Элемент | Правильно | Неправильно |
|---|---|---|
| Заголовок страницы | «Payment methods» | «Payment Methods» |
| Кнопка | «Add payment method» | «Add Payment Method» |
| Пункт меню | «Account settings» | «Account Settings» |
| Заголовок колонки | «Due date» | «Due Date» |
| Чекбокс | «Send me product updates» | «Send Me Product Updates» |
| Название плана (имя собственное) | «Business Pro plan» | — |

**Жирный вместо курсива** для названий внутри текста [S2]: лучше читается и доступнее.

---

## 2. Пунктуация

### 2.1. Точка

`[система]` Microsoft [S1], Polaris [S3], Carbon, Atlassian.

| Нет точки | Есть точка |
|---|---|
| Заголовок, подзаголовок, заголовок UI | Связный текст из двух и более предложений |
| Кнопка, ссылка вне предложения | Тело письма, развёрнутое пояснение |
| Подпись поля, подсказка (hint) | Описание настройки из двух предложений |
| Пункт списка из одного предложения или фрагмента | Пункт списка, состоящий из полных предложений (тогда точка у всех) |
| Тост, бейдж, статус | — |
| Сообщение об ошибке в одну фразу | — |

Polaris отдельно: заголовки «avoid using punctuation such as periods, commas, or semicolons» и не заканчиваются
восклицательным знаком.

Ссылки вне предложения — без пунктуации, **кроме вопросительного знака**: «Learn more», «Forgot password?» [S3].

### 2.2. Оксфордская запятая

`[система]` Microsoft [S1]: «In a list of three or more items, include a comma before the conjunction.»
«Android, iOS, and Windows», не «Android, iOS and Windows».

Причина — снятие двусмысленности при перечислении составных элементов. Правило принимается как конвенция продукта
и применяется везде, включая перечисления внутри строк интерфейса.

### 2.3. Пробелы и тире

`[система]` Microsoft [S1]:

- один пробел после точки, вопросительного знака и двоеточия;
- **никаких пробелов вокруг em dash**: «Use pipelines—logical groups of activities—to consolidate activities».

Это прямо противоположно русской норме (в русском тире отбивается пробелами) и часто переносится ошибочно в обе
стороны. Проверка при двуязычном продукте — отдельная.

### 2.4. Восклицательные знаки

Не используются в сообщениях об ошибках, предупреждениях, подтверждениях и деструктивных действиях
[V:AVKz9ZYoxgo 1:04:28]. Допустимы точечно в поздравлении с завершением крупного сценария; **не более одного на
экран** и никогда подряд.

---

## 3. Грамматика и лексика

### 3.1. Contractions

`[система]` Microsoft [S1]: «Use contractions like it's, you'll, you're, we're, and let's.»

Contractions — главный инструмент настройки формальности в английском, и он же отсутствует в русском. Развёртка
NN/g [S5] показывает механику: «We are experiencing a problem» → «We're experiencing a problem» сдвигает тон к
разговорному без изменения содержания.

Где не сокращать: юридические тексты, сообщения о безопасности и инцидентах, тексты, где важна максимальная
однозначность (сокращения хуже читаются неносителями).

### 3.2. Глагол первым, без разрешительных конструкций

`[система]` Microsoft [S1]: «Most of the time, start each statement with a verb. Edit out *you can* when it isn't
necessary. Avoid weak phrasing like *there is*, *there are*, and *there were*.»

Polaris [S3] жёстче: «Don't use permissive language like "you can"».

| Слабо | Сильно |
|---|---|
| «You can access Office apps across your devices, and you get online file storage and sharing.» | «Store files online, access them from all your devices, and share them with coworkers.» |
| «Products appear in your store after you add them.» | «Add your first product and see how it looks in your store.» |
| «There are three ways to invite a teammate.» | «Invite a teammate by email, link, or CSV import.» |
| «You can now export your report.» | «Export your report.» |

### 3.3. Простые слова

`[система]` Microsoft [S6] — прямые таблицы замен:

| Use this | Not this |
|---|---|
| use | utilize, make use of |
| remove | extract, take away, eliminate |
| tell | inform, let know |
| to | in order to, as a means to |
| also | in addition |
| connect | establish connectivity |
| because | since (у «since» два значения) |
| need | must |

Убирать наречия, если они не меняют смысл: quite, very, quickly, easily, effectively.

Осторожно со словами, которые одновременно существительное и глагол: file, post, mark, screen, record, report —
снимать неоднозначность структурой предложения.

### 3.4. Артикли

`[система]` Polaris [S3] — единственный источник с явным правилом:

- **Разговорные места** (карточки на главной, пустые состояния, онбординг) — артикли есть: «Secure your account
  with two-step authentication».
- **Микрокопи** (подписи, заголовки, кнопки) — артиклей нет: «Create collection», не «Create a collection»;
  «Add menu item», не «Add a menu item».

Apple добавляет то же для команд: 2–4 слова, «убирайте артикли, чтобы ускорить сканирование».

Бирман честно признаёт, что универсального правила не знает, и советует смотреть, как сделали Apple и Google
[V:6Vh49gMvirE 47:21]. Правило Polaris выше — и есть тот явный источник, которого в его ответе не хватало.

### 3.5. Reading level

`[исследование]` [S7]: 6–8 класс для широкой аудитории, 10–12 для экспертов, выше 12 — никто. Для сообщений об
ошибках критерий уровня Excellent — **7–8 класс по Флешу-Кинкейду или ниже** [S8]. Проверяется встроенными
средствами текстовых редакторов и онлайн-анализаторами.

Длина предложения — 15–20 слов [S7]; норма GOV.UK — до 50 слов в абзаце и максимум 20 в предложении
[V:AVKz9ZYoxgo 42:04].

---

## 4. Устоявшиеся формулировки

### 4.1. Кнопки

`[система]` Polaris [S3]: формула `{verb} + {noun}`, кроме общеизвестных «Done», «Close», «Cancel», «OK»
(последнее — с оговоркой §6).

| Do | Don't |
|---|---|
| Activate Apple Pay | Try Apple Pay |
| Explore free themes | Free themes |
| View shipping settings | Settings |
| Buy new domain | Buy New Domain |
| Add menu item | Add a menu item |

Apple [S4]: «just saying "Send" often works better than "Let's do it!"».

Многошаговый поток [S4]: «Get Started» в начале, «Continue» или «Next» между шагами, «Done» в конце — и
последовательно во всём продукте.

### 4.2. Словарь пар

`[система]` Polaris [S3] — самый полный найденный словарь различений. Русские эквиваленты —
`02-microcopy-by-component.md` §1.7.

| Пара | Первое | Второе |
|---|---|---|
| **Save / Done** | сохранение сразу в базу | отложенное применение (модалка вносит несохранённые изменения на страницу) |
| **Close / Accept** | подтвердить прочтение | юридическое согласие на условия |
| **Close / Cancel** | режим только чтения | есть изменения, которые отменяются; Cancel всегда слева от Save/Done |
| **Select / Choose** | ограниченный набор однородных, очевидное решение, списки | субъективное, стратегическое решение (theme, pricing plan) |
| **Edit / Manage** | изменить содержимое поля | несколько действий или настройки раздела |
| **Change / Switch** | заменить вариант без правки свойств | переключение между аккаунтами, локациями, режимами; предыдущее выключается |
| **Create / Add** | создать с нуля (order, collection, discount) | внести существующее (product, customer) |
| **View / See** | кнопки, CTA, ссылки | разговорные описания: «Customers will see this name at checkout» |
| **Need / Must** | всегда | никогда |
| **Export / Download** | с конвертацией формата (Export CSV file) | копия того же формата (Download PDF) |
| **Import / Upload** | с конвертацией формата (Import CSV file) | файл того же формата (Upload image) |

Дополнительно, из общей практики `[практика]`:

| Пара | Как выбирать |
|---|---|
| **Sign in / Log in** | Оба приняты. «Sign in» преобладает у Apple, Google, Microsoft, Shopify; «Log in» — у части разработческих продуктов. Выбрать один и держать; парные глаголы: Sign in ↔ Sign out, Log in ↔ Log out. **Не смешивать: «Sign in» и «Logout» на одном продукте — дефект** |
| **Sign up / Register / Create account** | «Create account» самое ясное и не путается с «Sign in»; «Sign up» короче, но визуально близко к «Sign in», что даёт ошибки на экране входа. Для сервисов с формальной регистрацией («Register») — по домену |
| **Delete / Remove** | «Delete» — объект перестаёт существовать; «Remove» — объект убирается отсюда, но существует где-то ещё (убрать участника из проекта). Polaris запрещает «Remove» в роли удаления |
| **Archive / Delete** | «Archive» обратимо и не требует подтверждения; «Delete» — по правилам деструктивных действий |
| **Apply / Save** | «Apply» — применить к текущему виду (фильтры); «Save» — записать в базу |
| **Submit** | **не использовать**: называет механику формы, а не результат. Заменять на «Send message», «Place order», «Create account» |
| **Next / Continue** | Выбрать один на весь мастер |
| **Got it / OK** | «Got it» лучше «OK» для закрытия информационного сообщения; ещё лучше — «Close» |

### 4.3. Ссылки

`[система]` Polaris [S3], Apple [S4], Walter [V:2juq00vrvl0 20:35]:

- никогда «Click here», «Here», «Read more», «Learn more» как единственный текст ссылки;
- вне предложения — `{verb} + {noun}`, без пунктуации, кроме вопросительного знака: «Learn more», «Forgot
  password?»;
- в предложении линковать **только фрагмент, называющий назначение**, а не всю фразу — прямо по соображениям
  интернационализации: «word order might change, which would break the link into two parts»;
- «Learn more about …» отдельным предложением — только если текст затрагивает больше одного понятия.

### 4.4. Сообщения об ошибках

Шаблоны по типу нарушения (Фридман, проект на 23 правила) [V:AVKz9ZYoxgo 1:05:28]:

| Нарушение | Формулировка |
|---|---|
| пусто | «Enter your {X}» |
| слишком коротко | «Must be at least {N} characters» |
| слишком длинно | «Must be {N} characters or fewer» |
| не те символы | «Use letters and hyphens only» |
| не тот тип | «Must be a number» |
| не тот формат | «Enter a date in the format mm/dd/yyyy, for example 03/14/2026» |
| выбор | «Select an option» / «Select all that apply» |

Apple [S4]: **инструктировать, а не отчитывать** — «Use only letters for your name» вместо «Don't use numbers or
symbols»; «Choose a password with at least 8 characters» вместо «That password is too short».

Microsoft [S1]: «Invalid ID» → «You need an ID that looks like this: someone@example.com».

### 4.5. Подтверждения

`[система]` Polaris [S3]:

| Do | Don't |
|---|---|
| «Discard unsaved changes?» | «Discard?» |
| «Delete 2 collections?» | «Are you sure you want to delete?» |
| «Delete Dark Blue Tee?» | «Are you sure you want to delete Dark Blue Tee?» |
| «Leave page with unsaved changes?» | «This page has unsaved changes are you sure you want to leave?» |
| «This can't be undone.» | «Are you sure you want to delete the variant Dark Blue Tee/Small/Silk? This action cannot be reversed.» |

Пары кнопок: удаление — `[Cancel] [Delete]`; отказ от изменений — `[Keep editing] [Discard]`; уход со страницы —
`[Stay] [Leave page]`.

---

## 5. Орфография

`[практика]`. **Американская орфография — фактический стандарт продуктовых интерфейсов**: её используют Apple,
Microsoft, Google, Shopify, Atlassian, Figma. Британская остаётся у GOV.UK и продуктов, ориентированных на UK.

| US | UK |
|---|---|
| color, behavior, favorite | colour, behaviour, favourite |
| center, meter, fiber | centre, metre, fibre |
| canceled, canceling, labeled, modeling | cancelled, cancelling, labelled, modelling |
| analyze, organize, customize | analyse, organise, customise |
| license (и сущ., и глагол) | licence (сущ.) / license (глагол) |
| enrollment, fulfillment, installment | enrolment, fulfilment, instalment |
| catalog, dialog (в UI), program | catalogue, dialogue, programme |
| defense, offense | defence, offence |

**Правило**: выбрать один вариант на продукт и включить в линтер. Смешение («customise» и «color» в одном
интерфейсе) — заметный дефект качества.

Отдельно: `dialog` как элемент интерфейса пишется без `ue` даже в британских продуктах (термин закрепился через
код и ARIA-роль `dialog`).

---

## 6. Запрещённые формулировки

`[консенсус]`. Полный словарь с регулярными выражениями — `06-banned-words-and-patterns.md` §4.

| Запрещено | Почему | Замена |
|---|---|---|
| **Oops!**, **Uh-oh**, **Whoops** | «typically unnecessary and can sound insincere» [S4]; добавляют воодушевление там, где человек раздражён [S5] | Убрать; сразу к сути |
| **Something went wrong** | Не говорит ни что случилось, ни что делать; оставляет вопрос «не я ли виноват» | «We couldn't load your reports. Try again in a minute.» |
| **An error occurred** | То же [S8] | Назвать, что именно не удалось |
| **Are you sure?** | Не называет ни действие, ни объект [S3] | «Delete Dark Blue Tee?» |
| **Invalid input**, **Invalid name**, **Illegal**, **Incorrect** | Обвиняют пользователя; «The proper usage of any system lies with its creators» [S8]. «There are no invalid names» [V:AVKz9ZYoxgo 1:13:34] | Сказать, что нужно: «Use letters and hyphens only» |
| **Error 500**, голый код | Код — не сообщение [V:hDqJzydcHMc 34:57] | «Service unavailable. We're working on it.» Код — визуально второстепенно |
| **Click here**, **Here**, **Read more** | Список ссылок скринридера превращается в «click here, click here» [V:2juq00vrvl0 20:35] | Назвать назначение |
| **Submit** | Механика формы вместо результата (F7.2) | «Send message», «Place order» |
| **OK** как подтверждение действия | «OK is an exclamation, not an action» [S3]; смысл неоднозначен [S4] | «Close», «Got it», конкретный глагол |
| **Please** в каждой строке | Становится шумом; в проекте Фридмана запрещено целиком, но он сам оговаривает неуниверсальность | Один раз там, где система просит лишнюю работу |
| **Simply**, **Just**, **Easy**, **Quick** | Обещают лёгкость, которой может не быть; «making things easy is not the same as making things seem easy» [V:vxGrL3YSBvw 26:32] | Убрать |
| **Powerful**, **Seamless**, **Intuitive**, **Robust**, **Cutting-edge** | Маркетинговая интонация в продукте (F7.4) | Назвать, что конкретно делает функция |
| **Welcome back, John** | Дефект F12.1 каталога; фейковая персонализация в шаблоне | Убрать приветствие; показать содержание |
| **Lorem ipsum**, **Your text here**, **Feature 1** | Заглушки (F7.1) | Реальный текст |
| **We're sorry for any inconvenience** | Шаблон без содержания | Сказать, что случилось и что делается |
| **Unfortunately** | Наполнитель перед плохой новостью | Сразу к сути и к решению |
| **Above / below / right / left** | Directional language: ломается для скринридера, в RTL и на мобильном [S3] | Назвать элемент по имени |
| **He/she**, **s/he** | Microsoft [S9] | Переписать на «you», множественное, роль или единичное «they» |
| **Master / slave**, **blacklist / whitelist** (в новых продуктах) | Microsoft [S9] | primary/subordinate; allowlist/blocklist |

---

## 7. Числа, даты, время

`[стандарт]`. Правило первое: **форматы берутся из локали через `Intl`, а не хардкодятся** —
`05-localization-and-i18n.md` §5. Здесь — конвенции, которые надо знать, чтобы понимать, что именно локализуется.

| Элемент | en-US | en-GB | Комментарий |
|---|---|---|---|
| Дата числом | 3/14/2026 | 14/03/2026 | **Самый опасный формат**: 03/04 читается по-разному. В интерфейсе предпочитать месяц словом |
| Дата словом | March 14, 2026 | 14 March 2026 | Запятая перед годом только в US-формате |
| Время | 2:05 PM | 14:05 | 12-часовой формат — только для US |
| Разряды числа | 1,500.00 | 1,500.00 | Запятая — разряды, точка — дробная часть (обратно русскому) |
| Валюта | $1,500.00 | £1,500.00 | Знак **перед** числом (обратно русскому) |
| Проценты | 20% | 20% | **Без пробела** (обратно русскому) |
| Диапазон | 10–15 March | 10–15 March | En dash, без пробелов |
| Порядковые | 1st, 2nd, 3rd, 21st | то же | `Intl.PluralRules` с `type: 'ordinal'` |

**Числа цифрами**, включая маленькие: NN/g отдельно рекомендует «show numbers as numerals when writing for online
readers» [S10] — цифра работает якорем для сканирования и экономит место.

**Относительное время**: `Intl.RelativeTimeFormat`, не ручные строки. Правила выбора между относительным и
абсолютным — `01-principles-voice-and-tone.md` §11.4 (они не зависят от языка).

---

## 8. Инклюзивный язык

`[система]` Microsoft [S9], Apple [S4].

### 8.1. Гендер

| Use this | Not this |
|---|---|
| chair, moderator | chairman |
| humanity, people, humankind | man, mankind |
| operates, staffs | mans |
| sales representative | salesman |
| synthetic, manufactured | manmade |
| workforce, staff, personnel | manpower |

**Не использовать he, him, his, she, her, hers в родовых упоминаниях.** Пять способов переписать [S9]:

1. Второе лицо: «you».
2. Множественное число: существительное и местоимение.
3. «The» или «a» вместо местоимения: «the document».
4. Роль: reader, employee, customer, client.
5. «Person», «individual».

Если переписать не удаётся — **единичное «they»** допустимо. **Конструкции «he/she» и «s/he» запрещены.**

Когда речь о конкретном реальном человеке — использовать местоимения, которые он использует сам.

### 8.2. Термины

| Use this | Not this |
|---|---|
| primary / subordinate | master / slave |
| perimeter network | demilitarized zone (DMZ) |
| stop responding | hang |
| allowlist / blocklist | whitelist / blacklist |

### 8.3. Инвалидность

«Focus on people, not disabilities»: «readers who are blind or have low vision», «customers with limited
dexterity». **Не использовать слова, подразумевающие жалость** («stricken with», «suffering from»). Не упоминать
ограничение, если оно не относится к делу [S9].

### 8.4. Поля идентичности

`[практика]` ДиЛалло [V:vxGrL3YSBvw 23:09, 24:18] — проверяемый чек-лист для форм регистрации:

- **Возрастные диапазоны** несут скрытые утверждения: «до 18 вас нет», «в 45 вы ближе к 55, чем к 44», «после 56
  разницы с 96 нет». Спрашивать возраст числом, если он вообще нужен (то же у Бирмана [V:0Cf80XFusHg 08:07]:
  «когда у человека спрашиваешь возраст, он отвечает числом лет, а не тем, к какой возрастной категории он
  относится»).
- **Имена**: не подчёркивать красным фамилию с заглавной внутри слова; не ограничивать набор символов и длину —
  «there are no invalid names» [V:AVKz9ZYoxgo 1:13:34]. Подробно — `05-localization-and-i18n.md` §7.
- **Пол**: спрашивать только если это влияет на функцию; предусматривать вариант «предпочитаю не указывать».
- **Списки стран**: юридический и политический риск, а не вопрос текста — `05-localization-and-i18n.md` §9.

---

## 9. Английский как исходный язык перевода

`[практика]` ДиЛалло [V:vxGrL3YSBvw 30:48]:

- довести английский до идеала до начала перевода;
- **короткий и простой текст переводится надёжнее**: «Join» машинный перевод не портит, «Become a member» во
  французском теряет нюанс (получается не то членство);
- привлекать носителя языка, даже если английский идеален.

**Ограничение, которое надо знать** (оговорка дайджеста и позиция базы): совет «довести английский, потом
переводить» **плохо работает для интерфейсов, проектируемых сразу на русском**. Русский длиннее, грамматически
сложнее, и правила порядка слов, склонения и плюрализации из английского оригинала не выводятся. Для продуктов с
русским как основным языком английская версия делается **параллельно**, а не выводится переводом —
`05-localization-and-i18n.md` §2.

---

## Частые ошибки

Дефекты каталога `../11-ai-generated-ui/01-failure-modes-catalog.md`, закрываемые этим файлом:

| Дефект | Раздел |
|---|---|
| **F7.2** системный язык | §4.2 («Submit»), §6 |
| **F7.4** маркетинговая интонация | §6 (Powerful, Seamless, Intuitive) |
| **F7.1** заглушки | §6 (Lorem ipsum, Feature 1) |
| **F12.1** фейковые люди | §6 («Welcome back, John») |
| **F13.1(5)** шаблонная обвязка | §1 (Title Case), §2.4 (восклицательные знаки) |

Ошибки, специфичные для английского в русскоязычной команде:

1. **Title Case по инерции**: «Create New Project».
2. **Точка в конце кнопки и заголовка** по русской привычке к точкам в предложении.
3. **Пробелы вокруг em dash** по русской норме.
4. **Запятая как разделитель дробной части**: «1 500,00» в английской версии.
5. **Знак валюты после числа**: «1,500 $».
6. **Пробел перед знаком процента**: «20 %» в английской версии.
7. **Смешение US и UK орфографии**.
8. **«Sign in» и «Logout»** в одном продукте.
9. **«Submit»** на кнопке отправки формы.
10. **Артикли в микрокопи**: «Create a collection» на кнопке.
11. **Отсутствие contractions** там, где продукт заявил разговорный тон.
12. **Оксфордская запятая то есть, то нет.**
13. **«Please» в каждой второй строке** — калька с русской вежливости.
14. **Буквальный перевод русского канцелярита**: «It is necessary to carry out the saving of data».
15. **Буквальный перевод русской конструкции с «не удалось»**: «It was not possible to save» вместо «Couldn't save
    your changes».

---

## Чек-лист

1. Sentence case применён ко всем заголовкам, кнопкам, подписям, пунктам меню?
2. Точек нет в заголовках, кнопках, подписях, пунктах списка, тостах?
3. Оксфордская запятая стоит во всех перечислениях из трёх и более элементов?
4. Em dash без пробелов; один пробел после точки?
5. Восклицательных знаков нет в ошибках, предупреждениях и подтверждениях?
6. Contractions используются последовательно (или последовательно не используются)?
7. Каждое высказывание начинается с глагола; «you can» убрано; нет «there is / there are»?
8. Кнопки — `{verb} + {noun}` без артиклей; исключения только Done/Close/Cancel/Next/Back?
9. Пары глаголов выбраны по смыслу и не смешиваются (Save/Done, Create/Add, Select/Choose, Edit/Manage,
   Change/Switch, View/See, Export/Download, Import/Upload)?
10. «Sign in» и «Sign out» (или «Log in» и «Log out») — одна пара на весь продукт?
11. «Submit» отсутствует?
12. «OK» не используется как подтверждение действия?
13. Ни одной ссылки «Click here», «Here», «Read more»?
14. В предложении залинкован только фрагмент, называющий назначение?
15. Орфография (US или UK) выбрана и выдержана; включена в линтер?
16. Ни одного «Oops», «Something went wrong», «An error occurred», «Are you sure?», «Invalid»?
17. Reading level проверен: 6–8 класс для широкой аудитории, 7–8 для сообщений об ошибках?
18. Предложения ≤ 20 слов, абзацы ≤ 50 слов?
19. Числа, даты, время, валюты идут через `Intl`, а не хардкодом?
20. Даты в интерфейсе с месяцем словом там, где возможна путаница 03/04?
21. Инклюзивный язык: нет he/she, нет master/slave, фокус на людях?
22. Поля возраста, имени и пола проверены отдельно?
23. Английский не выводится переводом с русского и не выводит русский переводом с себя?

---

## Открытые вопросы и противоречия

1. **Title Case** `[спорно]`. Apple допускает его как осознанный выбор продукта, Microsoft и Polaris запрещают.
   Позиция базы (sentence case по умолчанию) опирается на большинство и на аргумент локализуемости, но прямого
   сравнительного измерения читаемости заголовков в двух регистрах в интерфейсе не найдено.
2. **Артикли в микрокопи**. Правило Polaris — единственный найденный явный источник; Apple формулирует мягче
   («убирайте артикли, чтобы ускорить сканирование»), Бирман честно говорит, что не знает. Измерений нет.
3. **«Please»** `[спорно]`. Фридман приводит проект, где оно запрещено целиком, и тут же оговаривает, что это
   решение конкретного проекта. Универсального правила нет.
4. **Sign in против Log in.** Практика расходится; данных о влиянии на успешность входа не найдено. Правило
   базы — про непротиворечивость пары, а не про выбор.
5. **Восклицательный знак после успеха.** Polaris запрещает в заголовках, Mailchimp допускает как часть голоса.
   Не разрешено измерениями.
6. **Не удалось открыть**: полный A-to-Z GOV.UK style guide (страница переехала на
   `guidance.publishing.service.gov.uk`, найденные URL дали 404), Mailchimp «Writing technical content» (404),
   Polaris «Grammar and mechanics» и «Voice and tone» (архив вернул 429). Правила Polaris взяты только из
   «Actionable language».

---

## Источники

1. `[S1]` Microsoft Writing Style Guide, «Top 10 tips for Microsoft style and voice», обновлено 06.07.2026.
   https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice
2. `[S2]` Microsoft Writing Style Guide, «Formatting titles», 26.02.2024.
   https://learn.microsoft.com/en-us/style-guide/text-formatting/formatting-titles
3. `[S3]` Shopify Polaris, «Actionable language», архивная копия 2024.
   https://web.archive.org/web/2024/https://polaris.shopify.com/content/actionable-language
4. `[S4]` Apple Human Interface Guidelines, «Writing», обновлено 16.12.2025.
   https://developer.apple.com/design/human-interface-guidelines/writing
5. `[S5]` NN/g, «The Four Dimensions of Tone of Voice».
   https://www.nngroup.com/articles/tone-of-voice-dimensions/
6. `[S6]` Microsoft Writing Style Guide, «Use simple words, concise sentences», 24.06.2022.
   https://learn.microsoft.com/en-us/style-guide/word-choice/use-simple-words-concise-sentences
7. `[S7]` NN/g, «Plain Language Is for Everyone, Even Experts».
   https://www.nngroup.com/articles/plain-language-experts/
8. `[S8]` NN/g, «Error-Message Guidelines» и «An Error Messages Scoring Rubric».
   https://www.nngroup.com/articles/error-message-guidelines/ ,
   https://www.nngroup.com/articles/error-messages-scoring-rubric/
9. `[S9]` Microsoft Writing Style Guide, «Bias-free communication», 18.04.2024.
   https://learn.microsoft.com/en-us/style-guide/bias-free-communication
10. `[S10]` NN/g, «First 2 Words: A Signal for the Scanning Eye» (в тексте — рекомендация показывать числа
    цифрами). https://www.nngroup.com/articles/first-2-words-a-signal-for-scanning/
11. `[S11]` Mailchimp Content Style Guide, «Voice and Tone». https://styleguide.mailchimp.com/voice-and-tone/

Видеодайджесты: `[V:AVKz9ZYoxgo]` Vitaly Friedman, 2025 (шаблоны ошибок, «no invalid names»); `[V:vxGrL3YSBvw]`
Nick DiLallo, 2024 (перевод, поля идентичности, «making things easy»); `[V:2juq00vrvl0]` Stéphanie Walter, 2025
(«click here» и скринридер); `[V:6Vh49gMvirE]` Илья Бирман, 2023 (артикли); `[V:0Cf80XFusHg]` Илья Бирман, 2022
(возраст числом); `[V:hDqJzydcHMc]` Анна Кочеткова, 2019 (код ошибки).
