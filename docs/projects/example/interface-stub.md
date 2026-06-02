# interface-stub

Упрощённое зеркало канона interface (`docs/projects/_canon/interface/`)
для example. Канон interface — 7 плоских таблиц, по одному файлу на kind;
здесь они собраны в один файл, без претензии на полное углубление.
Используется только этим образцом — реальный проект ведёт interface в
`docs/projects/<slug>/interface/`.

## who

| slug | name | description | status |
|---|---|---|---|
| `doctor` | врач | смотрит исследования, формирует заключения | `stable` |
| `nurse` | медсестра | заводит исследования, поддерживает картотеку | `draft` |
| `any` | любой пользователь | до аутентификации либо когда роль не важна | `stable` |

## stage

| slug | name | description | status |
|---|---|---|---|
| `auth` | вход в систему | пользователь входит и получает доступ | `stable` |
| `daily-work` | ежедневная работа | основные операции с исследованиями | `draft` |

## zone

| slug | name | description | parent-zone | status |
|---|---|---|---|---|
| `auth` | аутентификация | экраны входа | — | `stable` |
| `studies` | исследования | работа с каталогом исследований | — | `draft` |

## situation

| slug | name | description | stage | who | when | action | goal | entry-data | exit-data | using-what | ux-substrate | block | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `enter-credentials` | ввод кред | пользователь авторизуется | `auth` | `any` | при заходе в систему | вводит логин-пароль | получить сессию | — | [`user`] | форма входа | [`login-input`, `password-input`, `login-confirm`] | [`login-form`] | `stable` |
| `browse-studies` | просмотр списка | врач изучает список исследований | `daily-work` | `doctor` | при заходе в раздел | смотрит, фильтрует, ищет | найти нужное | — | — | каталог исследований | [`studies-search`, `studies-table`, `studies-pagination`, `filter-status`, `filter-date-range`, `filter-owner`, `apply-filters`, `reset-filters`] | [`studies-list`, `filters-panel`] | `draft` |
| `open-study-preview` | открытие превью | врач смотрит ключевые данные одного исследования | `daily-work` | `doctor` | после выбора строки | открывает превью | оценить детали без полного перехода | [`study`] | — | превью исследования | [`preview-meta`, `preview-actions`] | [`study-preview`] | `draft` |
| `open-study-detail` | открытие полного card | врач переходит к полному исследованию | `daily-work` | `doctor` | при необходимости полного просмотра | открывает card-страницу | работать с исследованием в полном объёме | [`study`] | — | карточка исследования | [`card-meta`, `card-timeline`, `card-actions`, `card-related`] | [`study-card`] | `draft` |
| `archive-study` | архивация | врач переводит исследование в архив | `daily-work` | `doctor` | по решению о завершении | подтверждает архивацию | убрать из активного списка | [`study`] | — | модалка подтверждения | [`archive-confirm`, `archive-cancel`, `study-row-menu`, `create-study`] | [`confirm-archive`] | `draft` |

## block

| slug | name | description | zone | who | ux-substrates | entrypoint | transition-to-block | transition-from-zone | status |
|---|---|---|---|---|---|---|---|---|---|
| `login-form` | форма входа | поля и подтверждение | `auth` | [`any`] | [`login-input`, `password-input`, `login-confirm`] | `true` | [`studies-list`] | — | `stable` |
| `filters-panel` | панель фильтров | параметры фильтрации списка | `studies` | [`doctor`] | [`filter-status`, `filter-date-range`, `filter-owner`, `apply-filters`, `reset-filters`] | `false` | — | — | `draft` |
| `studies-list` | список исследований | таблица + поиск + создание + пагинация | `studies` | [`doctor`, `nurse`] | [`studies-search`, `create-study`, `studies-table`, `study-row-menu`, `studies-pagination`] | `false` | [`study-card`, `confirm-archive`] | [`auth`] | `stable` |
| `study-preview` | превью исследования | компактная карта в detail-слоте | `studies` | [`doctor`] | [`preview-meta`, `preview-actions`] | `false` | [`study-card`] | — | `draft` |
| `study-card` | карточка исследования | полное представление исследования | `studies` | [`doctor`] | [`card-meta`, `card-timeline`, `card-actions`, `card-related`] | `false` | [`confirm-archive`] | — | `draft` |
| `confirm-archive` | подтверждение архивации | модалка-подтверждение действия | `studies` | [`doctor`] | [`archive-confirm`, `archive-cancel`] | `false` | [`studies-list`] | — | `stable` |

## ux-substrate

| slug | name | description | type | situation | status |
|---|---|---|---|---|---|
| `login-input` | ввод логина | поле логина | `ввод` | `enter-credentials` | `stable` |
| `password-input` | ввод пароля | поле пароля | `ввод` | `enter-credentials` | `stable` |
| `login-confirm` | подтверждение входа | действие отправки формы | `команда` | `enter-credentials` | `stable` |
| `studies-search` | поиск | свободный поиск по списку | `ввод` | `browse-studies` | `draft` |
| `create-study` | новое исследование | действие создания | `команда` | `browse-studies` | `draft` |
| `studies-table` | таблица исследований | предъявление коллекции | `список` | `browse-studies` | `draft` |
| `studies-pagination` | пагинация | переключение страниц | `выбор` | `browse-studies` | `draft` |
| `filter-status` | фильтр статуса | выбор одного из статусов | `выбор` | `browse-studies` | `draft` |
| `filter-date-range` | фильтр диапазона дат | выбор интервала | `выбор` | `browse-studies` | `draft` |
| `filter-owner` | фильтр владельца | выбор владельца | `выбор` | `browse-studies` | `draft` |
| `apply-filters` | применить | действие применения фильтров | `команда` | `browse-studies` | `draft` |
| `reset-filters` | сбросить | действие сброса | `команда` | `browse-studies` | `draft` |
| `study-row-menu` | меню строки | контекстные действия над исследованием | `команда` | `archive-study` | `draft` |
| `preview-meta` | мета превью | ключевые поля исследования | `инфо` | `open-study-preview` | `draft` |
| `preview-actions` | действия превью | действия с открытым исследованием | `команда` | `open-study-preview` | `draft` |
| `card-meta` | мета карты | полные поля исследования | `инфо` | `open-study-detail` | `draft` |
| `card-timeline` | лента событий | хронология изменений | `список` | `open-study-detail` | `draft` |
| `card-actions` | действия карты | действия с карточкой | `команда` | `open-study-detail` | `draft` |
| `card-related` | связанные | связанные исследования | `список` | `open-study-detail` | `draft` |
| `archive-confirm` | подтвердить | действие подтверждения архивации | `команда` | `archive-study` | `stable` |
| `archive-cancel` | отменить | действие отмены | `команда` | `archive-study` | `stable` |

## data-items

| slug | name | description | status |
|---|---|---|---|
| `user` | пользователь | учётная запись клинициста | `stable` |
| `study` | исследование | основной объект каталога | `draft` |
