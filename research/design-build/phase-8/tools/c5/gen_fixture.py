#!/usr/bin/env python3
"""Генератор своих файлов фикстуры cabinet-ds: токены DTCG и компоненты артефакта (одноразовый, вне репозитория)."""
import json
import sys
from pathlib import Path

FX = Path(sys.argv[1])            # .../fixtures/cabinet-ds/files
D = FX / "design"


def srgb(hexv, alpha=None):
    h = hexv.lstrip("#")
    comps = [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]
    v = {"colorSpace": "srgb", "components": comps}
    if alpha is not None:
        v["alpha"] = alpha
    v["hex"] = hexv
    return v


def dimn(px, unit="px"):
    return {"value": px, "unit": unit}


def ref(p):
    return "{" + p + "}"


def tok(value, desc=None, modes=None, art=None, llm=None, typ=None):
    t = {}
    if typ:
        t["$type"] = typ
    t["$value"] = value
    if desc:
        t["$description"] = desc
    ext = {}
    if modes:
        ext["org.ui-research.modes"] = modes
    if llm:
        ext["org.ui-research.llm"] = llm
    if art:
        ext["org.design-deep-dive.artifact"] = art
    if ext:
        t["$extensions"] = ext
    return t


NEUTRAL = {"0": "#ffffff", "50": "#f8fafc", "100": "#f1f5f9", "200": "#e2e8f0", "300": "#cbd5e1", "500": "#64748b",
           "600": "#475569", "700": "#334155", "800": "#1e293b", "900": "#0f172a", "950": "#020617"}
ACCENT = {"50": "#eff6ff", "400": "#60a5fa", "600": "#2563eb", "700": "#1d4ed8"}
RED = {"400": "#f87171", "600": "#dc2626"}
GREEN = {"400": "#4ade80", "600": "#16a34a"}
AMBER = {"400": "#fbbf24", "600": "#d97706"}
SIZES = [2, 4, 8, 12, 14, 16, 20, 24, 28, 32, 36, 40, 48, 240, 1280]

N = "primitive.color.neutral."
A = "primitive.color.accent."
S = "primitive.size."

dtcg = {
    "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
    "$description": "Иллюстрация: токены ДС демо-кабинета «Отвес» (фикстура cabinet-ds) — пресет плотной админки, светлая "
                    "тема по умолчанию и тёмная, плотность compact и comfortable, сокращённое движение.",
    "example": True,
    "primitive": {
        "color": {
            "$type": "color",
            "neutral": {k: tok(srgb(v)) for k, v in NEUTRAL.items()},
            "accent": {k: tok(srgb(v)) for k, v in ACCENT.items()},
            "red": {k: tok(srgb(v)) for k, v in RED.items()},
            "green": {k: tok(srgb(v)) for k, v in GREEN.items()},
            "amber": {k: tok(srgb(v)) for k, v in AMBER.items()},
            "shadow": {"key": tok(srgb("#020617", 0.08)), "key-dark": tok(srgb("#020617", 0.4))},
        },
        "size": {"$type": "dimension", **{str(px): tok(dimn(px)) for px in SIZES}},
        "weight": {"$type": "fontWeight", "regular": tok(400), "medium": tok(500), "semibold": tok(600)},
    },
    "color": {
        "$type": "color",
        "bg": {
            "canvas": tok(ref(N + "50"), "Фон страницы кабинета за карточками и таблицами.", {"dark": ref(N + "900")}),
            "surface": tok(ref(N + "0"), "Карточки, таблицы, поля ввода и боковая панель.", {"dark": ref(N + "800")}),
            "subtle": tok(ref(N + "100"), "Шапка таблицы, скелетон, фон неактивного поля.", {"dark": ref(N + "950")}),
            "selected": tok(ref(A + "50"), "Выбранная строка и текущий пункт навигации.", {"dark": ref(N + "700")}),
        },
        "text": {
            "default": tok(ref(N + "900"), "Основной текст и заголовки; 17,1:1 к color-bg-canvas.",
                           {"dark": ref(N + "50")}),
            "muted": tok(ref(N + "600"), "Подписи, подсказки, метаданные; 7,2:1 к color-bg-canvas.",
                         {"dark": ref(N + "300")}),
            "on-accent": tok(ref(N + "0"), "Текст и иконки на color-accent-solid.", {"dark": ref(N + "950")}),
        },
        "border": {
            "default": tok(ref(N + "200"), "Границы карточек, таблиц и разделителей.", {"dark": ref(N + "700")}),
            "strong": tok(ref(N + "500"), "Граница поля ввода: 4,8:1 к фону — порог 3:1 для контролов (WCAG 1.4.11).",
                          {"dark": ref(N + "500")}),
        },
        "accent": {
            "solid": tok(ref(A + "700"), "Главное действие «Назначить замер», текущий пункт навигации; белый на нём 6,7:1.",
                         {"dark": ref(A + "400")},
                         llm={"usage": ["primary-action", "selected-nav"],
                              "rules": "Use for the one primary action per area. Do NOT use for large backgrounds."}),
            "text": tok(ref(A + "700"), "Ссылки и текст действия на светлом фоне.", {"dark": ref(A + "400")}),
        },
        "focus": tok(ref(A + "600"), "Кольцо фокуса: outline 2px с отступом 2px.", {"dark": ref(A + "400")}),
        "status": {
            "info": tok(ref(A + "600"), "Статус «новая»: информационная метка.", {"dark": ref(A + "400")}),
            "success": tok(ref("primitive.color.green.600"), "Статус «замер проведён».",
                           {"dark": ref("primitive.color.green.400")}),
            "warning": tok(ref("primitive.color.amber.600"), "Статус «замер назначен»: ждёт выезда.",
                           {"dark": ref("primitive.color.amber.400")}),
            "danger": tok(ref("primitive.color.red.600"), "Статус «отказ», ошибки загрузки и полей.",
                          {"dark": ref("primitive.color.red.400")}),
        },
    },
    "font": {
        "sans": tok(["Golos Text", "Arial", "sans-serif"], "Гарнитура интерфейса: кириллица проверена отрисовкой.",
                    typ="fontFamily"),
    },
    "space": {
        "$type": "dimension",
        "$description": "Шкала отступов кабинета — одна на продукт; режимы плотности сдвигают шаги, а не шкалу.",
        "2xs": tok(ref(S + "2"), "Иконка и счётчик в пункте навигации."),
        "xs": tok(ref(S + "4"), "Подпись и поле, зазоры в меню."),
        "sm": tok(ref(S + "8"), "Кнопки в ряду, ячейки плотной таблицы.", {"compact": ref(S + "4"),
                                                                           "comfortable": ref(S + "12")}),
        "md": tok(ref(S + "16"), "Отступ карточки, между полями формы.", {"compact": ref(S + "12"),
                                                                         "comfortable": ref(S + "20")}),
        "lg": tok(ref(S + "24"), "Между блоками экрана.", {"compact": ref(S + "16"), "comfortable": ref(S + "32")}),
        "xl": tok(ref(S + "32"), "Отступ области содержимого от каркаса."),
    },
    "size": {
        "$type": "dimension",
        "$description": "Размеры контролов, строк и панелей каркаса.",
        "control": {"md": tok(ref(S + "32"), "Высота кнопок и полей на десктопе; на таче зона нажатия не меньше 44px."),
                    "lg": tok(ref(S + "40"), "Высота главной кнопки формы.")},
        "row": {"table": tok(ref(S + "36"), "Высота строки таблицы заявок.", {"compact": ref(S + "28")})},
        "panel": {"sidebar": tok(ref(S + "240"), "Ширина боковой навигации каркаса."),
                  "topbar": tok(ref(S + "48"), "Высота верхней панели каркаса."),
                  "content-max": tok(ref(S + "1280"), "Наибольшая ширина области содержимого.")},
    },
    "radius": {
        "$type": "dimension",
        "$description": "Два радиуса: у контролов и у контейнеров.",
        "sm": tok(ref(S + "4"), "Кнопки, поля, метки статуса."),
        "md": tok(ref(S + "8"), "Карточки, плитки, выпадающие списки."),
    },
    "elevation": {
        "$type": "shadow",
        "raised": tok([{"color": ref("primitive.color.shadow.key"), "offsetX": dimn(0), "offsetY": dimn(1),
                        "blur": dimn(2), "spread": dimn(0)},
                       {"color": ref("primitive.color.shadow.key"), "offsetX": dimn(0), "offsetY": dimn(4),
                        "blur": dimn(8), "spread": dimn(-2)}],
                      "Выпадающий список и всплывающая карточка; у карточек на странице тени нет — граница.",
                      {"dark": [{"color": ref("primitive.color.shadow.key-dark"), "offsetX": dimn(0), "offsetY": dimn(1),
                                 "blur": dimn(2), "spread": dimn(0)},
                                {"color": ref("primitive.color.shadow.key-dark"), "offsetX": dimn(0), "offsetY": dimn(4),
                                 "blur": dimn(8), "spread": dimn(-2)}]}),
    },
    "breakpoint": {
        "$type": "dimension",
        "tablet": tok(dimn(640), "Планшет и шире: ниже — одна колонка, навигация в выдвижной панели."),
        "desktop": tok(dimn(1024), "Главная граница приложения: боковая навигация видна постоянно."),
        "wide": tok(dimn(1440), "Широкий экран: инспектор рядом со списком."),
    },
    "motion": {
        "duration": {"$type": "duration",
                     "fast": tok(dimn(100, "ms"), "Наведение и нажатие."),
                     "default": tok(dimn(150, "ms"), "Раскрытие меню и выпадающего списка."),
                     "slow": tok(dimn(200, "ms"), "Выдвижная панель.", {"reduced": dimn(150, "ms")})},
        "easing": {"$type": "cubicBezier",
                   "standard": tok([0.4, 0, 0.2, 1], "Кривая по умолчанию для отклика компонентов.")},
    },
    "type": {
        "$type": "typography",
        "title": tok({"fontFamily": ref("font.sans"), "fontSize": ref(S + "20"), "fontWeight": ref("primitive.weight.semibold"),
                      "letterSpacing": dimn(-0.2), "lineHeight": 1.4},
                     "Заголовок экрана и окна подтверждения: 20/28, 600.",
                     art={"group": "Заголовки", "sample": "Заявки на замер"}),
        "metric": tok({"fontFamily": ref("font.sans"), "fontSize": ref(S + "24"), "fontWeight": ref("primitive.weight.semibold"),
                       "letterSpacing": dimn(-0.36), "lineHeight": 1.333333},
                      "Число плитки плана: 24/32, 600, табличные цифры.",
                      art={"group": "Заголовки", "sample": "32 из 40"}),
        "body": tok({"fontFamily": ref("font.sans"), "fontSize": ref(S + "14"), "fontWeight": ref("primitive.weight.regular"),
                     "letterSpacing": dimn(0), "lineHeight": 1.428571},
                    "Основной текст, ячейки таблицы, сообщения: 14/20; ниже tablet — 16 (сборка ДС).",
                    art={"group": "Текст", "sample": "З-0412 · Сормово, двухкомнатная"}),
        "body-strong": tok({"fontFamily": ref("font.sans"), "fontSize": ref(S + "14"),
                            "fontWeight": ref("primitive.weight.semibold"), "letterSpacing": dimn(0),
                            "lineHeight": 1.428571},
                           "Текст кнопок и акцент в строке: 14/20, 600.",
                           art={"group": "Текст", "sample": "Назначить замер"}),
        "label": tok({"fontFamily": ref("font.sans"), "fontSize": ref(S + "12"), "fontWeight": ref("primitive.weight.medium"),
                      "letterSpacing": dimn(0.12), "lineHeight": 1.333333},
                     "Подписи полей, заголовки колонок: 12/16, 500.",
                     art={"group": "Текст", "sample": "Дата замера"}),
        "caption": tok({"fontFamily": ref("font.sans"), "fontSize": ref(S + "12"), "fontWeight": ref("primitive.weight.regular"),
                        "letterSpacing": dimn(0.12), "lineHeight": 1.333333},
                       "Подсказки, ошибки у поля, статусы: 12/16.",
                       art={"group": "Текст", "sample": "Перезвоним, чтобы подтвердить время"}),
    },
}


def compact(v):
    return json.dumps(v, ensure_ascii=False, separators=(", ", ": "))


def dump_dtcg(obj, ind=0):
    pad = "  " * ind
    items = []
    for k, v in obj.items():
        key = json.dumps(k, ensure_ascii=False)
        if isinstance(v, dict) and "$value" not in v and not k.startswith("$"):
            items.append(f"{pad}  {key}: {dump_dtcg(v, ind + 1)}")
        elif isinstance(v, dict) and "$value" in v:
            inner = ",\n".join(f"{pad}    {json.dumps(k2, ensure_ascii=False)}: {compact(v2)}" for k2, v2 in v.items())
            items.append(f"{pad}  {key}: {{\n{inner}\n{pad}  }}")
        else:
            items.append(f"{pad}  {key}: {compact(v)}")
    return "{\n" + ",\n".join(items) + f"\n{pad}}}"


D.mkdir(parents=True, exist_ok=True)
(D / "system.tokens.json").write_text(dump_dtcg(dtcg) + "\n", encoding="utf-8")

# компоненты артефакта: имя → (группа словаря, типы, состояния, подпись карточки, заголовок, сводка, образец)
COMP = {
    "Button": ("Действия", ["Button"], ["rest", "hover", "focus-visible", "active", "disabled", "loading"],
               "Кнопка", "Кнопка действия кабинета: основная — «Назначить замер», вторичная — рядом.",
               '<button class="btn btn-primary" type="button" data-state="{s}">Назначить замер</button>'),
    "Link": ("Действия", ["Link"], ["rest", "hover", "focus-visible", "active"], "Ссылка",
             "Ссылка перехода: к списку заявок, в карточку заявки.",
             '<a class="link" href="#requests" data-state="{s}">К заявкам</a>'),
    "Field": ("Ввод и выбор", ["Field"], ["rest", "disabled", "invalid"], "Поле формы",
              "Поле формы заявки: подпись над полем, подсказка или ошибка под ним.",
              '<div class="field" data-state="{s}"><label>Телефон</label><input class="input" type="tel">'
              '<span class="hint">Позвоним один раз, чтобы договориться о замере</span></div>'),
    "TextInput": ("Ввод и выбор", ["TextInput"], ["rest", "hover", "focus-visible", "disabled", "readonly", "invalid"],
                  "Текстовое поле", "Однострочное текстовое поле формы заявки.",
                  '<input class="input" type="text" value="Сормово, ул. Коминтерна" data-state="{s}">'),
    "SearchInput": ("Ввод и выбор", ["SearchInput"], ["rest", "hover", "focus-visible", "disabled"], "Поиск",
                    "Поиск заявки по номеру, клиенту и адресу в шапке списка.",
                    '<input class="input input--search" type="search" placeholder="Номер, клиент или адрес" '
                    'data-state="{s}">'),
    "Select": ("Ввод и выбор", ["Select"], ["rest", "hover", "focus-visible", "disabled", "invalid", "expanded"],
               "Выпадающий список", "Выбор замерщика или статуса заявки из списка.",
               '<select class="input" data-state="{s}"><option>Замерщик не назначен</option></select>'),
    "Sidebar": ("Навигация", ["Sidebar"], ["rest", "hover", "focus-visible", "active", "selected"], "Боковая навигация",
                "Боковая навигация каркаса: разделы «Заявки» и «План».",
                '<a class="nav-item" href="#requests" data-state="{s}">Заявки</a>'),
    "TopBar": ("Навигация", ["TopBar"], ["rest"], "Верхняя панель", "Верхняя панель каркаса: название и пользователь.",
               '<header class="topbar" data-state="{s}"><span>Отвес · заявки</span></header>'),
    "Pagination": ("Навигация", ["Pagination"], ["rest", "hover", "focus-visible", "active", "selected", "disabled"],
                   "Страницы", "Переход по страницам списка заявок.",
                   '<a class="page" href="#p2" data-state="{s}">2</a>'),
    "Callout": ("Обратная связь", ["Alert", "Banner"], ["rest"], "Сообщение",
                "Сообщение о состоянии: в блоке (ошибка загрузки) и баннером на всю ширину (нет сети).",
                '<div class="callout" data-state="{s}">Не удалось загрузить заявки</div>'),
    "Progress": ("Обратная связь", ["Progress"], ["rest"], "Прогресс", "Полоса выполнения плана замеров месяца.",
                 '<div class="progress" data-state="{s}"><span style="width: 80%"></span></div>'),
    "Skeleton": ("Обратная связь", ["Skeleton"], ["rest"], "Скелетон", "Заглушка строк и карточек при первой загрузке.",
                 '<div class="skeleton" data-state="{s}"></div>'),
    "EmptyState": ("Обратная связь", ["EmptyState"], ["rest"], "Пустое состояние",
                   "Пустой список заявок: что здесь будет и одно действие.",
                   '<div class="empty" data-state="{s}"><p>Заявок пока нет</p></div>'),
    "Table": ("Данные", ["Table"], ["rest", "hover", "focus-visible", "selected"], "Таблица",
              "Таблица заявок: номер, клиент, адрес, дата замера, статус.",
              '<table class="table"><tr data-state="{s}"><td>З-0412</td><td>Сормово</td></tr></table>'),
    "DescriptionList": ("Данные", ["DescriptionList"], ["rest", "skeleton"], "Список свойств",
                        "Свойства заявки по рангам атрибутов в карточке.",
                        '<dl class="props" data-state="{s}"><dt>Клиент</dt><dd>Ирина В.</dd></dl>'),
    "KpiTile": ("Данные", ["KpiTile"], ["rest", "skeleton"], "Плитка показателя",
                "Плитка плана замеров месяца: число, план и прогресс.",
                '<div class="kpi" data-state="{s}"><span class="metric">32</span> из 40</div>'),
    "AddressMap": ("Данные", ["AddressMap"], ["rest", "focus-visible"], "Карта адреса",
                   "Карта адреса объекта в карточке заявки — расширение словаря проекта.",
                   '<div class="map" tabindex="0" role="region" aria-label="Адрес объекта на карте" data-state="{s}"></div>'),
}
LABELS = {"rest": "покой", "hover": "наведение", "focus-visible": "фокус", "active": "нажатие", "disabled": "неактивно",
          "loading": "загрузка", "readonly": "только чтение", "invalid": "ошибка", "expanded": "раскрыт",
          "selected": "выбран", "skeleton": "скелетон"}
comp_dir = D / "_design-system" / "project" / "components"
for name, (group, types, states, title, summary, sample) in COMP.items():
    d = comp_dir / name
    d.mkdir(parents=True, exist_ok=True)
    subtitle = ", ".join(LABELS[s] for s in states).capitalize()
    height = 80 + 40 * len(states)
    body = "\n".join(f"  {sample.format(s=s)}" for s in states)
    (d / "preview.html").write_text(
        f'<!-- @dsCard group="{group}" height={height} subtitle="{subtitle}" -->\n'
        "<!doctype html>\n<html lang=\"ru\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{title}</title>\n</head>\n<body>\n"
        "<!-- Иллюстрация фикстуры cabinet-ds: образец на каждое состояние; data-state — состояние словаря компонентов. -->\n"
        f'<div class="ds-states" style="padding: 24px; display: grid; gap: 12px;">\n{body}\n</div>\n'
        "</body>\n</html>\n", encoding="utf-8")
    (d / "README.md").write_text(
        f"# {name}\n\n{summary}\n\nИллюстрация фикстуры cabinet-ds (демо-кабинет «Отвес»), не данные проекта.\n\n"
        f"- **Типы словаря:** {', '.join(types)}.\n- **Состояния:** {', '.join(states)}.\n", encoding="utf-8")
print("ok", len(COMP))
