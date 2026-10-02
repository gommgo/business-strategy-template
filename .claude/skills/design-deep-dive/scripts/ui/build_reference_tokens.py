#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор эталонной схемы токенов ui (`09-design-tokens/04-reference-token-schema.md`).

Один источник истины -> три листинга, которые гарантированно не расходятся:
  * DTCG JSON (Design Tokens Format Module 2025.10),
  * CSS-переменные (светлая тема, тёмная тема, два режима плотности, сокращённое движение),
  * блок `@theme inline` для Tailwind CSS v4 (+ мост совместимости с shadcn/ui).
Плюс отчёт проверок: контраст семантических пар в обеих темах, коридор APCA отключённого текста, палитра графиков
при симуляции дальтонизма, арифметика интерлиньяжа, светлота слоёв поверхностей.

Запуск:
    python3 build_reference_tokens.py [--out <каталог>]
Пишет tokens.json, tokens.css, theme.css, report.txt в каталог --out (по умолчанию `$DDD_HOME/out/ui/reference-tokens`)
и печатает отчёт; строка «<<<» в отчёте — непройденный порог контраста. `tokens.css` — эталонные токены
`kb/ui/14-recipes/examples/tokens.css`, по ним `ui_audit.py` проверяет экран, когда токенов ДС проекта нет.

Правила применения (`$extensions.org.design-deep-dive.llm`) пишутся на английском: их читают модель и код. `size.control.*` —
высота видимого контрола; зона нажатия на таче — не меньше 44×44 у каждой цели (правило `size.control.lg`), режимы
плотности её не уменьшают. Метки `usage` описывают экраны приложения: H1 страницы сайта — роли display базы creative.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import kbpaths  # noqa: E402
from color import hex2oklch, wcag, apca, composite, sim_cvd, dE_oklab  # noqa: E402

EXT = "org.design-deep-dive.llm"
EXT_MODES = "org.design-deep-dive.modes"

# --------------------------------------------------------------------------------------
# 1. Примитивы: цветовые шкалы (значения Tailwind v4 theme.css, OKLCH -> hex, см. F-notes S23)
# --------------------------------------------------------------------------------------
PALETTE = OrderedDict([
    ("neutral", OrderedDict([  # slate
        (50, "#f8fafc"), (100, "#f1f5f9"), (200, "#e2e8f0"), (300, "#cad5e2"),
        # 350 и 450 — не Tailwind: интерполированы в OKLCH между соседними ступенями
        # (350: L 0.79 C 0.031 H 255; 450: L 0.645 C 0.043 H 257.3). Зачем они:
        # 400 не проходит 4.5:1 на surface-raised тёмной темы, 500 даёт disabled APCA Lc 25 (< 30).
        (350, "#aebccf"), (400, "#90a1b9"), (450, "#7d8fa8"),
        (500, "#62748e"), (600, "#45556c"), (700, "#314158"), (800, "#1d293d"), (900, "#0f172b"),
        (950, "#020618"),
    ])),
    ("accent", OrderedDict([  # blue
        (50, "#eff6ff"), (100, "#dbeafe"), (200, "#bedbff"), (300, "#8ec5ff"), (400, "#51a2ff"),
        (500, "#2b7fff"), (600, "#155dfc"), (700, "#1447e6"), (800, "#193cb8"), (900, "#1c398e"),
        (950, "#162456"),
    ])),
    # у статусных семейств оставлены только те ступени, на которые реально ссылается
    # семантический слой: полные 11-шаговые рампы нужны лишь нейтрали и акценту
    ("red", OrderedDict([
        (100, "#ffe2e2"), (300, "#ffa2a2"), (500, "#fb2c36"),
        (600, "#e7000b"), (700, "#c10007"), (900, "#82181a"), (950, "#460809"),
    ])),
    ("amber", OrderedDict([
        (100, "#fef3c6"), (300, "#ffd230"), (400, "#ffb900"),
        (600, "#e17100"), (900, "#7b3306"), (950, "#461901"),
    ])),
    ("green", OrderedDict([
        (100, "#dcfce7"), (300, "#7bf1a8"), (400, "#05df72"), (500, "#00c950"),
        (700, "#008236"), (900, "#0d542b"), (950, "#032e15"),
    ])),
])
# Палитры графиков: сгенерированы и проверены (CVD ΔE >= 0.05, контраст к фону >= 3:1)
CHART_LIGHT = ["#00468c", "#824700", "#007974", "#c360bc", "#708500"]
CHART_DARK = ["#4699fe", "#f68c11", "#00d9d1", "#bd5ab6", "#c3e151"]

# Единый размерный ряд (Polaris-подход: одна шкала на отступы, размеры и ширины)
SCALE = [0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 36, 40, 44, 48, 56, 64, 80, 96,
         180, 240, 280, 288, 360, 400, 480, 560, 640, 880, 1280]

FONT_SIZES = [11, 12, 14, 16, 20, 24, 28, 32]
FONT_WEIGHTS = OrderedDict([("regular", 400), ("medium", 500), ("semibold", 600)])
# Слой движения — набор 08-motion/03-reduced-motion-and-motion-tokens.md §4-§6, взятый целиком:
# 8 примитивов длительности, 5 кривых, 4 пространственные величины, 6 семантических
# длительностей, 4 семантические кривые, 14 составных переходов = 41 токен.
DURATIONS = [0, 50, 100, 150, 200, 300, 400, 600]
EASINGS = OrderedDict([
    ("standard",   [0.4, 0.0, 0.2, 1.0]),
    ("entrance",   [0.0, 0.0, 0.2, 1.0]),
    ("exit",       [0.4, 0.0, 1.0, 1.0]),
    ("emphasized", [0.05, 0.7, 0.1, 1.0]),
    ("linear",     [0.0, 0.0, 1.0, 1.0]),
])

# --------------------------------------------------------------------------------------
# 2. Модель токена
# --------------------------------------------------------------------------------------
class T:
    """Один токен."""

    __slots__ = ("path", "type", "value", "desc", "usage", "rules", "do_not_use",
                 "alternatives", "modes", "css", "tw")

    def __init__(self, path, type_, value, desc="", usage=None, rules="", do_not_use=False,
                 alternatives=None, modes=None, css=None, tw=None):
        self.path = path            # список сегментов
        self.type = type_
        self.value = value
        self.desc = desc
        self.usage = usage or []
        self.rules = rules
        self.do_not_use = do_not_use
        self.alternatives = alternatives or []
        self.modes = modes or {}    # {"dark": value, "compact": value, "comfortable": value}
        self.css = css              # имя CSS-переменной без "--"
        self.tw = tw                # список пар (namespace-имя, значение) для @theme

    @property
    def dotted(self):
        return ".".join(self.path)


TOKENS: list[T] = []


def add(path, type_, value, desc="", usage=None, rules="", css=None, modes=None,
        do_not_use=False, alternatives=None, tw=None):
    t = T(path.split("."), type_, value, desc, usage, rules, do_not_use, alternatives,
          modes, css, tw)
    TOKENS.append(t)
    return t


def color_value(hex_, alpha=None):
    L, C, H = hex2oklch(hex_)
    v = OrderedDict([("colorSpace", "oklch"),
                     ("components", [round(L, 4), round(C, 4), round(H, 2)])])
    if alpha is not None:
        v["alpha"] = alpha
    v["hex"] = hex_
    return v


def dim(px):
    return OrderedDict([("value", px), ("unit", "px")])


def dur(ms):
    return OrderedDict([("value", ms), ("unit", "ms")])


dur_ms = dur


def ref(path):
    return "{%s}" % path


# --------------------------------------------------------------------------------------
# 3. Примитивы
# --------------------------------------------------------------------------------------
def build_primitives():
    for fam, steps in PALETTE.items():
        for step, hx in steps.items():
            add(f"primitive.color.{fam}.{step}", "color", color_value(hx),
                desc=f"{fam} {step}", css=f"palette-{fam}-{step}")
    add("primitive.color.white", "color", color_value("#ffffff"), desc="Pure white",
        css="palette-white")
    for px in SCALE:
        add(f"primitive.size.{px}", "dimension", dim(px), desc=f"{px}px step of the size scale",
            css=f"scale-{px}")
    add("primitive.font.family.sans", "fontFamily",
        ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto",
         "Helvetica Neue", "Arial", "sans-serif"],
        desc="UI sans-serif stack", css="font-family-sans")
    add("primitive.font.family.mono", "fontFamily",
        ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "Menlo", "Consolas",
         "Liberation Mono", "monospace"],
        desc="Monospace stack for code, IDs and tabular data", css="font-family-mono")
    for px in FONT_SIZES:
        add(f"primitive.font.size.{px}", "dimension", dim(px), desc=f"{px}px type size",
            css=f"font-size-{px}")
    for name, w in FONT_WEIGHTS.items():
        add(f"primitive.font.weight.{name}", "fontWeight", w, desc=f"Weight {w}",
            css=f"font-weight-{name}")
    for ms in DURATIONS:
        add(f"primitive.duration.{ms}", "duration", dur(ms), desc=f"{ms}ms",
            css=f"duration-{ms}")
    for name, pts in EASINGS.items():
        add(f"primitive.easing.{name}", "cubicBezier", pts,
            desc=f"cubic-bezier({', '.join(str(p) for p in pts)})",
            css=f"easing-{name}")


# --------------------------------------------------------------------------------------
# 4. Семантика: цвет
# --------------------------------------------------------------------------------------
def p(fam, step):
    return ref(f"primitive.color.{fam}.{step}")


def build_semantic_color():
    C = [
        # ---- фоны и поверхности -----------------------------------------------------
        ("color.bg.canvas", p("neutral", 50), p("neutral", 900),
         "Page background behind every surface.",
         ["page-background", "app-shell", "body"],
         "Use for the outermost page background only. Cards and panels MUST sit on bg.surface, "
         "not on this token."),
        ("color.bg.surface", p("neutral", 50).replace("neutral.50", "white"), p("neutral", 800),
         "Background of a card, panel, table or modal.",
         ["card", "panel", "modal", "table", "sidebar"],
         "RECOMMENDED default surface for content containers. Pair with text.primary and "
         "border.subtle."),
        ("color.bg.surface-raised", p("neutral", 50).replace("neutral.50", "white"), p("neutral", 700),
         "Background of a floating surface: popover, dropdown menu, tooltip body, toast.",
         ["popover", "dropdown", "menu", "toast", "combobox-list"],
         "Use for surfaces rendered in a portal above the page. MUST be combined with "
         "elevation.overlay so the surface separates from the page in both themes."),
        ("color.bg.surface-hover", p("neutral", 100), p("neutral", 700),
         "Hover background of a row or list item that lies on bg.surface.",
         ["table-row-hover", "list-item-hover", "menu-item-hover"],
         "Use for whole-row hover feedback. Do NOT use as a resting background. In the light "
         "theme text.tertiary reads 4.35:1 on it: acceptable for the transient hover state only, "
         "never for resting content."),
        ("color.bg.subtle", p("neutral", 100), p("neutral", 950),
         "Recessed area: zebra striping, code block, empty state, disabled field.",
         ["zebra-row", "code-block", "empty-state", "input-disabled", "well"],
         "Use for areas that read as pushed into the surface. Do NOT use for elevated content. "
         "Text on it is text.primary or text.secondary: text.tertiary gives only 4.35:1 here in "
         "the light theme."),
        ("color.bg.component", p("neutral", 100), p("neutral", 700),
         "Resting background of a low-emphasis control: secondary button, chip, tag, segmented item.",
         ["secondary-button", "chip", "tag", "segmented-control"],
         "Use for controls that need a fill but not the accent. Pair with text.primary."),
        ("color.bg.component-hover", p("neutral", 200), p("neutral", 600),
         "Hover background of a low-emphasis control.",
         ["secondary-button-hover", "chip-hover", "icon-button-hover"],
         "Use only for the hover state of a control already using bg.component."),
        ("color.bg.component-active", p("neutral", 300), p("neutral", 500),
         "Pressed or active background of a low-emphasis control.",
         ["secondary-button-active", "toggle-selected", "segmented-item-selected"],
         "Use for the pressed state and for the selected item of a segmented control."),
        ("color.bg.selected", p("accent", 100), p("accent", 950),
         "Background of a selected row, selected list item or the active navigation item.",
         ["row-selected", "nav-item-active", "option-selected"],
         "Use to mark selection, not hover. MUST be paired with a second signal (checkmark, "
         "left bar or bold label): colour alone is not enough. Hover on a selected item uses "
         "bg.selected-hover. Metadata inside a selected row uses text.secondary: text.tertiary "
         "drops to 3.9:1 on this token in the light theme."),
        ("color.bg.selected-hover", p("accent", 200), p("accent", 900),
         "Hover background of an element that is already selected (selected + hover).",
         ["row-selected-hover", "nav-item-active-hover", "option-selected-hover"],
         "Use ONLY for the hover state of an element that already sits on bg.selected: one step "
         "darker than bg.selected in the light theme and one step lighter in the dark theme, so a "
         "hovered selected row stays distinct from both bg.selected and bg.surface-hover. Do NOT "
         "use for hover on unselected rows: that is bg.surface-hover."),
        ("color.bg.inverse", p("neutral", 800), p("neutral", 100),
         "Inverted surface used for tooltips and snackbars inside the current theme.",
         ["tooltip", "snackbar", "inverse-banner"],
         "MUST be paired with text.on-inverse. Keeps tooltips high-contrast in both themes."),
        # ---- границы ----------------------------------------------------------------
        ("color.border.subtle", p("neutral", 200), p("neutral", 800),
         "Divider and border of a non-interactive container.",
         ["divider", "card-border", "table-rule", "separator"],
         "Use for separators and card outlines. Do NOT use for the border of an input: it is "
         "below the 3:1 non-text contrast threshold."),
        ("color.border.default", p("neutral", 300), p("neutral", 700),
         "Border of a low-emphasis interactive component at rest.",
         ["secondary-button-border", "chip-border", "tab-border"],
         "Use for outlined controls whose shape is already carried by a fill or a label."),
        ("color.border.strong", p("neutral", 500), p("neutral", 500),
         "Border of an input, checkbox, radio or any control whose shape carries meaning.",
         ["input-border", "checkbox-border", "radio-border", "select-border"],
         "MUST use for form control borders: this is the only neutral border token that meets "
         "WCAG 1.4.11 (3:1) in both themes."),
        # ---- текст и иконки ----------------------------------------------------------
        ("color.text.primary", p("neutral", 900), p("neutral", 100),
         "Primary text: body copy, headings, table cell values.",
         ["body-text", "heading", "default-text", "cell-value"],
         "RECOMMENDED default for all text. Use for headings, body text and primary labels."),
        ("color.text.secondary", p("neutral", 600), p("neutral", 300),
         "Secondary text: metadata, captions, column headers, helper text.",
         ["secondary-text", "metadata", "helper-text", "column-header"],
         "Use for supporting text next to primary content. Do NOT use for primary content."),
        ("color.text.tertiary", p("neutral", 500), p("neutral", 350),
         "Tertiary text: placeholders, hints, timestamps in dense lists.",
         ["placeholder", "hint", "timestamp"],
         "Use for the lowest readable tier of text. Do NOT use for anything the user must read "
         "to complete a task. In the dark theme it sits on neutral-350, not 400, so it keeps 4.5:1 "
         "on bg.surface-raised (popover, dialog): neutral-400 gave 3.94:1 there."),
        ("color.text.disabled", p("neutral", 400), p("neutral", 450),
         "Text of a disabled control.",
         ["disabled-text", "disabled-label"],
         "Use ONLY inside a disabled control. It is below 4.5:1 on purpose (WCAG 1.4.3 exempts "
         "inactive components); never use it for active content. Target APCA Lc 30–45 on every "
         "surface (01-color/05 §4.2): neutral-450 gives Lc 31–41 in the dark theme from "
         "surface-raised to subtle, where neutral-500 gave Lc 25 and read as absent."),
        ("color.text.on-accent", p("neutral", 50).replace("neutral.50", "white"),
         p("neutral", 950),
         "Text and icons on a solid accent fill.",
         ["text-on-accent", "primary-button-label", "contrast-text"],
         "MUST use for text and icons on accent.solid. Its polarity flips between themes: white "
         "in the light theme, near-black in the dark theme, because the dark theme moves every "
         "solid fill to a light step. Never hard-code white."),
        ("color.text.on-inverse", p("neutral", 50), p("neutral", 900),
         "Text on bg.inverse.",
         ["tooltip-text", "snackbar-text"],
         "MUST use for text inside a tooltip or snackbar built on bg.inverse."),
        ("color.icon.default", p("neutral", 600), p("neutral", 300),
         "Default icon colour next to primary or secondary text.",
         ["icon", "leading-icon", "trailing-icon"],
         "Use for icons that carry meaning. Match icon size to the adjacent text size."),
        ("color.icon.subtle", p("neutral", 500), p("neutral", 350),
         "Low-emphasis icon: chevrons, drag handles, decorative glyphs.",
         ["chevron", "drag-handle", "decorative-icon"],
         "Use for structural glyphs. Do NOT use for status icons."),
        # ---- акцент -------------------------------------------------------------------
        ("color.accent.bg", p("accent", 50), p("accent", 950),
         "Tinted accent background: info banner, highlighted zone, selected tab strip.",
         ["accent-banner", "highlight-zone", "tinted-panel"],
         "Use as a soft accent fill under accent.text. Do NOT put text.on-accent on it."),
        ("color.accent.border", p("accent", 300), p("accent", 800),
         "Border of an accent-tinted area or an accent-outlined control.",
         ["accent-banner-border", "accent-outline"],
         "Use together with accent.bg. Do NOT use as a focus ring; use focus-ring."),
        ("color.accent.solid", p("accent", 600), p("accent", 400),
         "Solid accent fill: primary button, active toggle, progress bar.",
         ["primary-button", "toggle-on", "progress-fill", "badge-solid"],
         "MUST be paired with text.on-accent. Exactly one solid accent per screen area: more "
         "than one primary button in a view is an error."),
        ("color.accent.solid-hover", p("accent", 700), p("accent", 300),
         "Hover fill of a solid accent control.",
         ["primary-button-hover"],
         "Use only for the hover state of accent.solid. The light theme darkens by one step, "
         "the dark theme lightens by one step."),
        ("color.accent.text", p("accent", 700), p("accent", 300),
         "Accent text and links on a neutral background.",
         ["link", "accent-text", "text-button"],
         "Use for links and text buttons. Do NOT use on accent.solid. In the dark theme it is "
         "accent-300, not accent-400: accent-400 gives 3.93:1 on bg.surface-raised."),
        # ---- служебное ----------------------------------------------------------------
        ("color.focus-ring", p("accent", 600), p("accent", 400),
         "Focus indicator ring.",
         ["focus-indicator", "focus-ring"],
         "MUST use for the keyboard focus ring, 2px wide with a 2px offset. Do NOT reuse "
         "accent.solid: the ring must stay visible on top of an accent fill."),
        ("color.overlay-scrim", None, None,
         "Scrim behind a modal dialog or drawer.",
         ["modal-scrim", "drawer-scrim", "backdrop"],
         "Use under any blocking overlay. Keep one scrim per screen: nested scrims stack and "
         "darken the page twice."),
        ("color.selection-bg", p("accent", 200), p("accent", 800),
         "Background of selected text (::selection).",
         ["text-selection"],
         "Use for ::selection only. Row selection uses bg.selected."),
        ("color.shadow.ring", None, None,
         "Colour of the 1px ring layer present in every elevation token.",
         ["shadow-ring", "hairline"],
         "Carries the outline of a floating surface. In the dark theme it flips polarity to a "
         "translucent white, because a black ring is invisible on a dark canvas."),
        ("color.shadow.key.raised", None, None,
         "Key (near, tight) shadow layer of elevation.raised.",
         ["shadow-key"],
         "Short offset, small blur, no spread. Do NOT raise its alpha in the light theme: above "
         "0.12 the edge starts to read as a border."),
        ("color.shadow.ambient.raised", None, None,
         "Ambient (far, diffuse) shadow layer of elevation.raised.",
         ["shadow-ambient"],
         "Large blur and negative spread. Carries the sense of height, not the edge."),
        ("color.shadow.key.overlay", None, None,
         "Key shadow layer of elevation.overlay.",
         ["shadow-key"],
         "Same role as key.raised but stronger, because a portal surface must separate from "
         "everything under it."),
        ("color.shadow.ambient.overlay", None, None,
         "Ambient shadow layer of elevation.overlay.",
         ["shadow-ambient"],
         "Same role as ambient.raised but stronger and further."),
    ]
    for path, light, dark, desc, usage, rules in C:
        css_name = path.replace("color.", "").replace(".", "-")
        if css_name.startswith("shadow-"):
            css_name = "shadow-color-" + css_name[len("shadow-"):]
        elif css_name.startswith("text-"):
            css_name = "fg-" + css_name[len("text-"):]
        add(path, "color", light, desc=desc, usage=usage, rules=rules,
            css=css_name, modes={"dark": dark})

    # токены с собственными значениями (альфа), не алиасы
    for t in TOKENS:
        if t.dotted == "color.overlay-scrim":
            t.value = color_value("#020618", alpha=0.32)
            t.modes["dark"] = color_value("#020618", alpha=0.6)
        elif t.dotted == "color.shadow.ring":
            t.value = color_value("#020618", alpha=0.06)
            t.modes["dark"] = color_value("#ffffff", alpha=0.1)
        elif t.dotted == "color.shadow.key.raised":
            t.value = color_value("#020618", alpha=0.08)
            t.modes["dark"] = color_value("#020618", alpha=0.4)
        elif t.dotted == "color.shadow.ambient.raised":
            t.value = color_value("#020618", alpha=0.08)
            t.modes["dark"] = color_value("#020618", alpha=0.4)
        elif t.dotted == "color.shadow.key.overlay":
            t.value = color_value("#020618", alpha=0.12)
            t.modes["dark"] = color_value("#020618", alpha=0.5)
        elif t.dotted == "color.shadow.ambient.overlay":
            t.value = color_value("#020618", alpha=0.12)
            t.modes["dark"] = color_value("#020618", alpha=0.5)

    # ---- статусы ----------------------------------------------------------------------
    statuses = [
        ("danger", "red",
         {"bg": (100, 950), "border": (300, 900), "solid": (600, 500), "text": (700, 300)},
         ("white", "neutral.950"),
         "destructive action, failed validation, error banner",
         ["error", "destructive", "failure"]),
        ("warning", "amber",
         {"bg": (100, 950), "border": (300, 900), "solid": (600, 400), "text": (900, 300)},
         ("neutral.950", "neutral.950"),
         "risky action, expiring item, non-blocking problem",
         ["warning", "caution", "at-risk"]),
        ("success", "green",
         {"bg": (100, 950), "border": (300, 900), "solid": (700, 500), "text": (700, 400)},
         ("white", "neutral.950"),
         "completed operation, healthy state, positive delta",
         ["success", "positive", "healthy"]),
        ("info", "accent",
         {"bg": (100, 950), "border": (300, 800), "solid": (600, 400), "text": (700, 300)},
         ("white", "neutral.950"),
         "neutral notification, hint, in-progress state",
         ["info", "neutral-status", "in-progress"]),
    ]
    for name, fam, parts, onsolid, what, usage in statuses:
        for role, (lt, dk) in parts.items():
            rules = {
                "bg": f"Use as the tinted background of a {name} banner, badge or cell. MUST be "
                      f"paired with {name}.text, never with text.primary.",
                "border": f"Use for the 1px border of a {name} banner or badge that sits on "
                          f"{name}.bg. Do NOT use as a focus ring.",
                "solid": f"Use for the solid {name} fill: filled badge, status dot, filled "
                         f"button. MUST be paired with {name}.on-solid.",
                "text": f"Use for {name} text and icons, both on a neutral surface and on "
                        f"{name}.bg. Do NOT put it on {name}.solid.",
            }[role]
            add(f"color.{name}.{role}", "color", p(fam, lt),
                desc=f"{name.capitalize()} {role}: {what}.",
                usage=[f"{name}-{role}"] + usage, rules=rules,
                css=f"{name}-{role}", modes={"dark": p(fam, dk)})
        lt_fg, dk_fg = onsolid
        add(f"color.{name}.on-solid", "color",
            ref("primitive.color." + lt_fg) if "." in lt_fg else ref(f"primitive.color.{lt_fg}"),
            desc=f"Text and icons on {name}.solid.",
            usage=[f"text-on-{name}", "contrast-text"],
            rules=f"MUST use for any label or icon placed on {name}.solid. Its polarity is not "
                  f"the same in both themes: check the value before hard-coding white.",
            css=f"{name}-on-solid",
            modes={"dark": ref("primitive.color." + dk_fg) if "." in dk_fg else ref(f"primitive.color.{dk_fg}")})

    # ---- графики ----------------------------------------------------------------------
    for i, (lt, dk) in enumerate(zip(CHART_LIGHT, CHART_DARK), start=1):
        add(f"color.chart.{i}", "color", color_value(lt),
            desc=f"Categorical chart series {i}.",
            usage=["chart-series", "legend", "data-visualisation"],
            rules="Use for chart series only. Do NOT reuse status colours for categories: a green "
                  "series reads as 'good' even when it just means 'Europe'. The five hues are "
                  "ordered by lightness on purpose; keep the order.",
            css=f"chart-{i}", modes={"dark": color_value(dk)})


# --------------------------------------------------------------------------------------
# 5. Семантика: отступы, размеры, форма, глубина, слои, движение, брейкпоинты
# --------------------------------------------------------------------------------------
def build_semantic_layout():
    space_scale = [("3xs", 2), ("2xs", 4), ("xs", 8), ("sm", 12), ("md", 16), ("lg", 24),
                   ("xl", 32), ("2xl", 40), ("3xl", 48), ("4xl", 64), ("5xl", 96)]
    space_rules = {
        "3xs": "Use between an icon and its label inside a dense control, and for hairline insets.",
        "2xs": "Use inside a control: gap between an icon and text in a button, badge padding.",
        "xs": "RECOMMENDED default gap between sibling controls in a row (button group, toolbar).",
        "sm": "Use for vertical gaps inside a form and for horizontal cell padding in a table.",
        "md": "RECOMMENDED default padding of a card and gap between cards in a grid.",
        "lg": "Use between sections of a page and for panel padding.",
        "xl": "Use between major blocks on a page and for the top padding of a page header.",
        "2xl": "Use for generous separation on wide screens. Rare in a dense admin.",
        "3xl": "Use for empty-state padding and hero blocks inside an application.",
        "4xl": "Use only for empty states and onboarding screens.",
        "5xl": "Use only for full-page empty or error states. Do NOT use between components.",
    }
    # компактный и просторный режимы: сдвиг на один шаг шкалы, см. §3 файла 03-theming-and-modes
    compact_map = {"3xs": 2, "2xs": 2, "xs": 6, "sm": 8, "md": 12, "lg": 16, "xl": 24,
                   "2xl": 32, "3xl": 40, "4xl": 48, "5xl": 80}
    comfortable_map = {"3xs": 4, "2xs": 6, "xs": 10, "sm": 16, "md": 20, "lg": 32, "xl": 40,
                       "2xl": 48, "3xl": 64, "4xl": 80, "5xl": 96}
    for name, px in space_scale:
        add(f"space.{name}", "dimension", ref(f"primitive.size.{px}"),
            desc=f"Spacing step {name} = {px}px.",
            usage=["gap", "padding", "margin", "flex-gap", "grid-gap"],
            rules=space_rules[name], css=f"space-{name}",
            modes={"compact": ref(f"primitive.size.{compact_map[name]}"),
                   "comfortable": ref(f"primitive.size.{comfortable_map[name]}")})

    purpose = [
        ("space.inset.card", "space.md", "Padding inside a card or panel body.",
         ["card-padding", "panel-padding"],
         "RECOMMENDED default padding for a card. Nested radius rule: the inner radius equals "
         "the outer radius minus this padding, clamped at 0."),
        ("space.inset.page", "space.lg", "Horizontal padding of the page content area.",
         ["page-inline", "content-inset"],
         "Use as the left and right inset of the content column. Override per breakpoint: 16 on "
         "mobile, 24 on desktop, 32 above the wide breakpoint."),
        ("space.inset.control-x", "space.sm", "Horizontal padding of a text button and input.",
         ["button-padding-x", "input-padding-x"],
         "Use for the horizontal padding of medium controls. An icon-only button uses a square "
         "box instead: size.control.md."),
        ("space.inset.table-cell-x", "space.sm", "Horizontal padding of a table cell.",
         ["table-cell-x"],
         "Use for td and th horizontal padding. Keep the first and last cell flush with the card "
         "padding by adding space.inset.card to the outer edge."),
        ("space.inset.table-cell-y", "space.3xs", "Vertical padding of a table cell in a dense table.",
         ["table-cell-y"],
         "Use with size.row.table = 36px. Do NOT set a row height and a vertical padding that "
         "contradict each other."),
        ("space.stack.field", "space.sm", "Vertical gap between form fields.",
         ["field-gap", "form-stack"],
         "Use between a field and the next field. The gap between a label and its control is "
         "space.2xs."),
        ("space.stack.section", "space.lg", "Vertical gap between page sections.",
         ["section-gap"],
         "Use between titled blocks of a page. Do NOT use inside a card."),
        ("space.inline.control", "space.xs", "Horizontal gap between adjacent controls.",
         ["control-gap", "button-group-gap", "toolbar-gap"],
         "RECOMMENDED default gap in a toolbar, filter row or button group."),
    ]
    for path, alias, desc, usage, rules in purpose:
        add(path, "dimension", ref(alias), desc=desc, usage=usage, rules=rules,
            css=path.replace(".", "-"))

    sizes = [
        ("size.control.xs", 24, "Height of an extra-small control.",
         ["chip", "inline-tag", "table-inline-button"],
         "Use inside dense tables only. Its hit target MUST be enlarged to 24px minimum by "
         "padding; below that it fails WCAG 2.2 SC 2.5.8."),
        ("size.control.sm", 28, "Height of a small control.",
         ["filter-button", "toolbar-button", "compact-select"],
         "Use in toolbars and filter rows inside a dense admin."),
        ("size.control.md", 32, "Default control height.",
         ["button", "input", "select", "icon-button"],
         "RECOMMENDED default for buttons, inputs and selects in a dense admin. A client-facing "
         "service uses 40px instead."),
        ("size.control.lg", 40, "Large control height.",
         ["primary-cta", "search-field", "mobile-control"],
         "Use for the main call to action and for search fields. On touch screens every target "
         "MUST have a hit area of at least 44x44px: extend the control with padding or a "
         "pseudo-element, the visible control may stay smaller. Density modes do not shrink the "
         "hit area."),
        ("size.icon.sm", 14, "Small icon box.",
         ["icon-in-caption", "icon-in-12px-text"],
         "Use next to 11-12px text. Do NOT go below 14px for a meaningful icon."),
        ("size.icon.md", 16, "Default icon box.",
         ["icon-in-body", "button-icon", "menu-icon"],
         "RECOMMENDED default. 68% of measured production interfaces use a 16x16 icon box."),
        ("size.icon.lg", 20, "Large icon box.",
         ["empty-state-icon", "nav-icon", "status-icon"],
         "Use for navigation and status icons, and next to 16-20px text."),
        ("size.checkbox", 16, "Checkbox and radio box.",
         ["checkbox", "radio"],
         "Use for the visual box. The clickable label area MUST reach 24px in height."),
        ("size.switch.width", 36, "Switch track width.", ["switch"],
         "Use with size.switch.height. The thumb diameter equals the height minus 4px."),
        ("size.switch.height", 20, "Switch track height.", ["switch"],
         "Use with size.switch.width."),
        ("size.avatar.sm", 20, "Small avatar.", ["avatar-in-row", "avatar-in-table"],
         "Use inside table rows and dense lists."),
        ("size.avatar.md", 24, "Default avatar.", ["avatar", "comment-avatar"],
         "RECOMMENDED default avatar in lists and comments."),
        ("size.avatar.lg", 32, "Large avatar.", ["avatar-in-header", "profile-avatar"],
         "Use in headers and profile cards."),
        ("size.row.table", 36, "Height of a data table row.", ["table-row"],
         "Use for dense data tables: 19 rows fit a 1440x900 viewport. A comfortable table uses "
         "44-48px."),
        ("size.row.menu-item", 28, "Height of a dropdown menu item.", ["menu-item"],
         "Use in dropdown menus and command palettes."),
        ("size.row.sidebar-item", 32, "Height of a sidebar navigation item.", ["sidebar-item"],
         "Use for primary navigation entries."),
        ("size.row.tab", 36, "Height of a tab.", ["tab"],
         "Use for the tab strip under a page header."),
        ("size.panel.topbar", 48, "Height of the application top bar.", ["topbar", "app-header"],
         "Use for the fixed application header. 48px is the modal value across measured products."),
        ("size.panel.sidebar", 240, "Width of the expanded sidebar.", ["sidebar"],
         "Use for the primary navigation column. Measured range in production is 224-320px."),
        ("size.panel.sidebar-collapsed", 48, "Width of the collapsed icon rail.",
         ["sidebar-collapsed", "icon-rail"],
         "Use when the sidebar collapses below the desktop breakpoint."),
        ("size.panel.inspector", 288, "Width of a right-hand inspector panel.",
         ["inspector", "details-panel"],
         "Use for properties and details panels. Below the desktop breakpoint it becomes a drawer."),
        ("size.panel.drawer", 480, "Width of a slide-over drawer.", ["drawer", "slide-over"],
         "Use for edit-in-place panels. Do NOT exceed half the viewport width."),
        ("size.modal.confirm", 400, "Width of a confirmation dialog.", ["confirm-dialog", "alert"],
         "Use for one question and two buttons. Do NOT put a form in it."),
        ("size.modal.form", 560, "Width of a form dialog.", ["form-dialog"],
         "RECOMMENDED default modal width: fits a single-column form at 14px base."),
        ("size.modal.wide", 880, "Width of a wide dialog.", ["wide-dialog", "table-in-modal"],
         "Use only when the dialog holds a table or a two-column layout."),
        ("size.overlay.popover", 240, "Default popover width.", ["popover"],
         "Use for filter popovers and small forms attached to a trigger."),
        ("size.overlay.menu-min", 180, "Minimum dropdown menu width.", ["menu", "dropdown"],
         "Use as min-width so a menu never collapses to the width of its shortest item."),
        ("size.overlay.tooltip-max", 280, "Maximum tooltip width.", ["tooltip"],
         "Use as max-width. A tooltip longer than two lines belongs in a popover."),
        ("size.overlay.toast", 360, "Toast width.", ["toast", "snackbar"],
         "Use for the notification stack in the corner of the viewport."),
        ("size.content.form-max", 640, "Maximum width of a single-column form.",
         ["form-column"],
         "Use as max-width on a form column: 560-640px gives 64-73 Cyrillic characters per line."),
        ("size.content.max", 1280, "Maximum width of the content column.",
         ["content-column", "page-max-width"],
         "Use for pages made of text and forms. Data tables and dashboards may go full width."),
    ]
    size_compact = {"size.control.xs": 20, "size.control.sm": 24, "size.control.md": 28,
                    "size.control.lg": 36, "size.row.table": 28, "size.row.menu-item": 24,
                    "size.row.sidebar-item": 28, "size.row.tab": 32, "size.panel.topbar": 40}
    size_comfortable = {"size.control.xs": 28, "size.control.sm": 32, "size.control.md": 40,
                        "size.control.lg": 48, "size.row.table": 48, "size.row.menu-item": 36,
                        "size.row.sidebar-item": 40, "size.row.tab": 44, "size.panel.topbar": 56}
    for path, px, desc, usage, rules in sizes:
        modes = {}
        if path in size_compact:
            modes["compact"] = ref(f"primitive.size.{size_compact[path]}")
        if path in size_comfortable:
            modes["comfortable"] = ref(f"primitive.size.{size_comfortable[path]}")
        add(path, "dimension", ref(f"primitive.size.{px}"), desc=desc, usage=usage, rules=rules,
            css=path.replace(".", "-"), modes=modes)

    radii = [
        ("radius.none", 0, "Square corner.", ["table", "full-bleed", "inline-code"],
         "Use for edge-to-edge tables and for elements flush with a container edge."),
        ("radius.xs", 2, "Extra-small radius.", ["badge", "tag", "checkbox", "progress-bar"],
         "Use for elements under 16px tall. Do NOT use for buttons or cards."),
        ("radius.sm", 4, "Small radius.", ["input", "small-button", "menu-item"],
         "Use for controls up to 28px tall and for items inside a menu."),
        ("radius.md", 6, "Default radius.", ["button", "input", "card", "popover", "container"],
         "RECOMMENDED default for a dense admin. A client-facing service uses 8-10px."),
        ("radius.lg", 8, "Large radius.", ["card", "modal", "drawer", "toast"],
         "Use for containers larger than 200px on their shortest side."),
        ("radius.full", None, "Pill and circle.", ["avatar", "pill-badge", "switch", "spinner"],
         "Use for avatars, pills and switches. Do NOT use for rectangular containers."),
    ]
    for path, px, desc, usage, rules in radii:
        value = dim(9999) if px is None else ref(f"primitive.size.{px}")
        add(path, "dimension", value, desc=desc, usage=usage, rules=rules,
            css="corner-" + path.split(".")[1])

    borders = [
        ("border.width.default", 1, "Default border width.", ["border", "divider", "input-border"],
         "RECOMMENDED default. 95% of borders measured in production are 1px."),
        ("border.width.strong", 2, "Emphasised border width.",
         ["selected-state", "active-tab-underline", "emphasis-border"],
         "Use for selected states and active tab underlines. Do NOT use for subtle dividers."),
        ("border.width.focus", 2, "Focus ring width.", ["focus-indicator"],
         "MUST use for the focus ring, together with a 2px offset and color focus-ring."),
        ("border.offset.focus", 2, "Focus ring offset.", ["focus-indicator"],
         "MUST use as outline-offset so the ring does not touch the control edge."),
    ]
    for path, px, desc, usage, rules in borders:
        add(path, "dimension", ref(f"primitive.size.{px}"), desc=desc, usage=usage, rules=rules,
            css=path.replace(".", "-"))

    # тени: составной тип shadow (массив слоёв)
    def layer(color_ref, x, y, blur, spread):
        return OrderedDict([("color", color_ref), ("offsetX", dim(x)), ("offsetY", dim(y)),
                            ("blur", dim(blur)), ("spread", dim(spread))])

    add("elevation.none", "shadow", [], desc="No shadow.",
        usage=["flat", "inline"],
        rules="Use for elements that lie in the page plane. Explicitly setting elevation.none is "
              "better than leaving box-shadow unset in a component API.",
        css="elevation-none")
    add("elevation.ring", "shadow",
        [layer(ref("color.shadow.ring"), 0, 0, 0, 1)],
        desc="Hairline ring drawn as a shadow instead of a border.",
        usage=["card-outline", "hairline", "no-layout-shift-border"],
        rules="Use instead of a border when a border would shift layout, and as the base layer of "
              "every raised surface.",
        css="elevation-ring")
    add("elevation.raised", "shadow",
        [layer(ref("color.shadow.ring"), 0, 0, 0, 1),
         layer(ref("color.shadow.key.raised"), 0, 1, 2, 0),
         layer(ref("color.shadow.ambient.raised"), 0, 4, 8, -2)],
        desc="Raised surface: card that needs separation, sticky header, dragged row.",
        usage=["card-raised", "sticky-header", "dragging"],
        rules="Use for surfaces that stay in the page flow but need separation. Do NOT use for "
              "portals: they need elevation.overlay.",
        css="elevation-raised")
    add("elevation.overlay", "shadow",
        [layer(ref("color.shadow.ring"), 0, 0, 0, 1),
         layer(ref("color.shadow.key.overlay"), 0, 8, 16, -4),
         layer(ref("color.shadow.ambient.overlay"), 0, 16, 32, -8)],
        desc="Floating surface rendered in a portal: popover, menu, modal, toast.",
        usage=["popover", "menu", "modal", "toast", "dropdown"],
        rules="MUST use together with bg.surface-raised. In the dark theme the ring layer carries "
              "most of the separation, because shadows barely read on a dark canvas.",
        css="elevation-overlay")

    zs = [("z.base", 0, "Page flow.", ["default"],
           "Use 0, not 'auto', when a stacking context must exist."),
          ("z.raised", 10, "Element lifted inside its own container.",
           ["sticky-column", "hovered-row"],
           "Use inside a component. Do NOT use to escape a container: use a portal."),
          ("z.sticky", 100, "Sticky page furniture.", ["sticky-header", "table-head", "toolbar"],
           "Use for sticky table headers and toolbars."),
          ("z.dropdown", 1000, "Dropdown and select list.", ["dropdown", "select-list", "combobox"],
           "Use for menus attached to a trigger."),
          ("z.app-bar", 1100, "Application top bar and sidebar.", ["topbar", "sidebar"],
           "Use for the app shell."),
          ("z.drawer", 1200, "Slide-over drawer.", ["drawer", "slide-over"],
           "Use for drawers and their scrim."),
          ("z.modal", 1300, "Modal dialog.", ["modal", "dialog"],
           "Use for blocking dialogs and their scrim."),
          ("z.toast", 1400, "Toast stack.", ["toast", "snackbar"],
           "Use for notifications, which must sit above a modal."),
          ("z.tooltip", 1500, "Tooltip.", ["tooltip"],
           "Use for tooltips, the topmost layer. Do NOT invent values above this: render into a "
           "portal instead of raising the number.")]
    for path, v, desc, usage, rules in zs:
        add(path, "number", v, desc=desc, usage=usage, rules=rules, css=path.replace(".", "-"))

    ops = [("opacity.disabled", 0.4, "Opacity of a disabled control.", ["disabled"],
            "Use on the whole disabled control, not on its text only."),
           ("opacity.loading", 0.2, "Opacity of content being replaced while loading.",
            ["loading", "pending"],
            "Use for optimistic-update placeholders. Do NOT use for skeletons: they have their "
            "own background."),
           ("opacity.scrim", 0.32, "Alpha baked into overlay-scrim.", ["scrim"],
            "Documented separately so a component can rebuild the scrim colour."),
           ("opacity.state-hover", 0.04, "Alpha of a hover state layer.", ["hover-layer"],
            "Use only when a solid hover token does not exist for the surface in question."),
           ("opacity.state-active", 0.08, "Alpha of a pressed state layer.", ["pressed-layer"],
            "Use only when a solid pressed token does not exist. In the dark theme raise both "
            "state alphas by half (0.06 / 0.12): the same alpha reads weaker on a dark surface.")]
    for path, v, desc, usage, rules in ops:
        add(path, "number", v, desc=desc, usage=usage, rules=rules, css=path.replace(".", "-"))

    # ---- движение: набор 08-motion/03-…md §4-§6, имена и значения согласованы ----
    motion = [
        ("motion.duration.instant", 0, "No animation; lands in the same frame.",
         ["focus", "instant-feedback"],
         "MUST use for the focus ring: focus never animates, because a delayed focus indicator "
         "breaks keyboard navigation."),
        ("motion.duration.fast", 100, "Hover, press, colour change.",
         ["hover", "pressed", "colour-change"],
         "Use for colour and border transitions on hover and press. Do NOT animate layout "
         "properties with it."),
        ("motion.duration.default", 150, "Default duration for any transition.",
         ["default-transition", "popover-enter", "menu-enter"],
         "RECOMMENDED default. Use when nothing suggests a slower or faster value."),
        ("motion.duration.slow", 200, "Popover and menu entrance, block expansion, medium exits.",
         ["expand", "modal-exit", "drawer-exit", "toast-exit"],
         "Use for medium-sized surfaces leaving the screen and for expanding blocks."),
        ("motion.duration.slower", 300, "Modals, drawers, large panels entering.",
         ["modal-enter", "drawer-enter", "toast-enter"],
         "Use for large surfaces entering. Entrances are longer than exits on purpose."),
        ("motion.duration.slowest", 400, "Page-level transitions.",
         ["page-transition", "onboarding-step"],
         "Ceiling for a work interface. Do NOT exceed 400ms in an admin: it reads as lag."),
    ]
    for path, ms, desc, usage, rules in motion:
        add(path, "duration", ref(f"primitive.duration.{ms}"), desc=desc, usage=usage, rules=rules,
            css=path.replace(".", "-"),
            modes=({"reduced": ref("primitive.duration.150")}
                   if path.split(".")[-1] in ("slow", "slower", "slowest") else {}))
    eas = [("motion.easing.standard", "standard", "Movement inside the screen.",
            ["hover", "colour-change", "reorder", "expand"],
            "RECOMMENDED default for transitions that stay on screen."),
           ("motion.easing.entrance", "entrance", "Entering the frame; decelerates to rest.",
            ["enter", "appear", "expand"],
            "Use for anything entering the screen: it starts fast and settles."),
           ("motion.easing.exit", "exit", "Leaving for good; accelerates off the edge.",
            ["exit", "dismiss", "collapse"],
            "Use for anything leaving the screen. Exception: a drawer that will come back uses "
            "motion.easing.standard, so it decelerates at the edge."),
           ("motion.easing.linear", "linear", "Loops: spinner, progress, shimmer.",
            ["spinner", "indeterminate-progress", "shimmer"],
            "MUST use for animation that loops forever: a spinner with an eased curve visibly "
            "stutters at each revolution. Do NOT use for a transition that starts and stops.")]
    for path, prim, desc, usage, rules in eas:
        add(path, "cubicBezier", ref(f"primitive.easing.{prim}"), desc=desc, usage=usage,
            rules=rules, css=path.replace(".", "-"))

    # пространственные величины движения: обнуляются в режиме reduced
    scale = [("motionScale.translateSmall", 4, 0, "Entrance offset of a small surface, px.",
              ["popover-enter", "tooltip-enter"],
              "Equals space.2xs. MUST be driven by this token, not hard-coded, so reduced motion "
              "can zero it out.", "motion-translate-sm"),
             ("motionScale.translateMedium", 8, 0, "Entrance offset of a card or block, px.",
              ["modal-enter", "card-enter", "drawer-enter"],
              "Equals space.xs. Same rule: never hard-code the offset.", "motion-translate-md"),
             ("motionScale.scaleIn", 0.95, 1, "Initial scale of an entering surface.",
              ["scale-in", "modal-enter", "popover-enter"],
              "95 to 100 %, the value Atlassian uses for motion.keyframe.scale.in.small. Becomes 1 "
              "under reduced motion.", "motion-scale-in"),
             ("motionScale.staggerStep", 20, 0, "Delay step inside a series, ms.",
              ["stagger", "list-enter"],
              "Carbon caps the total stagger at 500ms, so with 20ms a series of more than 25 items "
              "MUST animate as one block.", "motion-stagger-step")]
    for path, v, red, desc, usage, rules, cssname in scale:
        add(path, "number", v, desc=desc, usage=usage, rules=rules, css=cssname,
            modes={"reduced": red})

    # составные переходы (тип transition по DTCG)
    def tr(dur, ease):
        return OrderedDict([("duration", ref(f"motion.duration.{dur}")),
                            ("delay", dur_ms(0)),
                            ("timingFunction", ref(f"motion.easing.{ease}"))])
    transitions = [
        ("hover", "fast", "standard", "Hover feedback on a control.", ["hover"]),
        ("press", "fast", "entrance", "Pressed feedback on a control.", ["pressed"]),
        ("popupEnter", "default", "entrance", "Popover entrance.", ["popover-enter"]),
        ("popupExit", "fast", "exit", "Popover exit.", ["popover-exit"]),
        ("menuEnter", "default", "entrance", "Dropdown menu entrance.", ["menu-enter"]),
        ("menuExit", "fast", "exit", "Dropdown menu exit.", ["menu-exit"]),
        ("modalEnter", "slower", "entrance", "Modal dialog entrance.", ["modal-enter"]),
        ("modalExit", "slow", "exit", "Modal dialog exit.", ["modal-exit"]),
        ("blanketEnter", "slower", "entrance", "Modal scrim entrance.", ["scrim-enter"]),
        ("blanketExit", "slow", "exit", "Modal scrim exit.", ["scrim-exit"]),
        ("drawerEnter", "slower", "entrance", "Drawer entrance.", ["drawer-enter"]),
        ("drawerExit", "slow", "standard", "Drawer exit.", ["drawer-exit"]),
        ("toastEnter", "slower", "entrance", "Toast entrance.", ["toast-enter"]),
        ("toastExit", "slow", "exit", "Toast exit.", ["toast-exit"]),
        ("expand", "slow", "standard", "Expanding or collapsing a block.", ["expand", "collapse"]),
    ]
    kebab = {"popupEnter": "popup-enter", "popupExit": "popup-exit", "menuEnter": "menu-enter",
             "menuExit": "menu-exit", "modalEnter": "modal-enter", "modalExit": "modal-exit",
             "blanketEnter": "blanket-enter", "blanketExit": "blanket-exit",
             "drawerEnter": "drawer-enter", "drawerExit": "drawer-exit",
             "toastEnter": "toast-enter", "toastExit": "toast-exit"}
    for name, dur, ease, desc, usage in transitions:
        add(f"motion.transition.{name}", "transition", tr(dur, ease), desc=desc, usage=usage,
            rules=f"Composite token: duration {dur} plus easing {ease}. Apply as "
                  f"`transition: <property> var(--motion-{kebab.get(name, name)});`. "
                  f"Do NOT recombine duration and easing by hand.",
            css=f"motion-{kebab.get(name, name)}")

    bps = [("breakpoint.tablet", 640, "Tablet and up.", ["tablet", "sm"],
            "Below this width: one column, sidebar in an overlay, page inset 16px, tables become "
            "cards."),
           ("breakpoint.desktop", 1024, "Desktop and up.", ["desktop", "lg"],
            "The main threshold of an application: at and above it the sidebar is expanded and "
            "side panels are docked rather than overlaid."),
           ("breakpoint.wide", 1440, "Wide screens.", ["wide", "xl"],
            "Above it, raise the page inset to 32-40px and stop stretching the content column.")]
    for path, px, desc, usage, rules in bps:
        add(path, "dimension", dim(px), desc=desc, usage=usage, rules=rules,
            css="bp-" + path.split(".")[1])


# --------------------------------------------------------------------------------------
# 6. Семантика: композитная типографика
# --------------------------------------------------------------------------------------
TYPE_ROLES = [
    # role, size, line-height px, weight, tracking em, family, description, usage, rules
    ("caption", 11, 16, "regular", 0.01, "sans", "Smallest readable text.",
     ["caption", "chart-label", "legend"],
     "Use for chart labels and dense metadata. Do NOT use for anything the user must read to act."),
    ("caption-strong", 11, 16, "semibold", 0.02, "sans", "Uppercase-like emphasis at caption size.",
     ["table-column-header", "overline", "eyebrow"],
     "Use for table column headers and section eyebrows. Positive tracking compensates for the "
     "small size."),
    ("helper", 12, 16, "regular", 0.01, "sans", "Helper and error text under a form field.",
     ["helper-text", "field-error", "hint"],
     "Use below inputs. Pair with text.secondary, or with danger.text for validation errors."),
    ("label", 12, 16, "medium", 0.01, "sans", "Form label and small UI label.",
     ["form-label", "badge-label", "tab-label"],
     "Use for form labels and badges. Keep the gap between the label and its control at 4px."),
    ("code", 12, 16, "regular", 0.0, "mono", "Inline code, IDs, hashes.",
     ["code", "identifier", "hash", "log"],
     "Use the mono family. Monospace runs visually larger, so it is set 2px smaller than the "
     "surrounding body text."),
    ("body-compact", 14, 18, "regular", 0.0, "sans", "Body text in a dense row.",
     ["table-cell", "list-row", "dense-body"],
     "Use inside table cells and dense list rows where a 20px leading would break the 36px row."),
    ("body", 14, 20, "regular", 0.0, "sans", "Default body text.",
     ["body-text", "paragraph", "default-text"],
     "RECOMMENDED default for a dense admin. A client-facing service uses 16/24 instead."),
    ("body-strong", 14, 20, "semibold", 0.0, "sans", "Emphasised body text.",
     ["emphasis", "key-value", "selected-row"],
     "Use for the emphasised half of a key-value pair. Do NOT use bold for whole paragraphs."),
    ("button", 14, 20, "medium", 0.0, "sans", "Button and control label.",
     ["button-label", "menu-item", "tab"],
     "Use for every control label. Medium weight, never bold."),
    ("card-title", 14, 20, "semibold", 0.0, "sans", "Title of a card or panel.",
     ["card-title", "panel-title", "modal-title-small"],
     "Use for the title bar of a card. A card title is the same size as body text and differs "
     "only by weight."),
    ("section", 16, 24, "semibold", -0.005, "sans", "Section heading inside a page.",
     ["section-heading", "modal-title", "drawer-title"],
     "Use for the heading of a block and for modal titles."),
    ("page-title", 20, 28, "semibold", -0.01, "sans", "Page title.",
     ["page-title", "h1"],
     "Use once per page, in the page header."),
    ("page-title-lg", 24, 32, "semibold", -0.015, "sans", "Large page title.",
     ["page-title-large"],
     "Use on overview and dashboard pages that need a stronger opening."),
    ("metric", 28, 32, "semibold", -0.02, "sans", "Metric value on a dashboard tile.",
     ["kpi", "metric", "stat-value"],
     "Use for the number in a stat tile. Enable tabular numerals so digits do not shift on update."),
    ("metric-lg", 32, 36, "semibold", -0.02, "sans", "Large metric value.",
     ["kpi-large", "hero-metric"],
     "Use for the single headline number of a dashboard."),
]


def build_typography():
    for role, size, lh, weight, tracking_em, family, desc, usage, rules in TYPE_ROLES:
        tracking_px = round(tracking_em * size, 3)
        ratio = round(lh / size, 6)
        value = OrderedDict([
            ("fontFamily", ref(f"primitive.font.family.{family}")),
            ("fontSize", ref(f"primitive.font.size.{size}")),
            ("fontWeight", ref(f"primitive.font.weight.{weight}")),
            ("letterSpacing", dim(tracking_px)),
            ("lineHeight", ratio),
        ])
        add(f"type.{role}", "typography", value,
            desc=f"{desc} {size}/{lh}px, weight {FONT_WEIGHTS[weight]}, tracking {tracking_em:+.3f}em.",
            usage=usage, rules=rules, css=f"type-{role}")


# --------------------------------------------------------------------------------------
# 7. Вывод: DTCG JSON
# --------------------------------------------------------------------------------------
def build_json_tree():
    root = OrderedDict()
    root["$schema"] = "https://www.designtokens.org/schemas/2025.10/format.json"
    root["$description"] = (
        "ui-research reference token set. Preset: dense back-office admin, light theme is the "
        "default, dark theme and two density modes ship as in-token overrides under "
        "$extensions." + EXT_MODES + ". Rules of use for a language model live under "
        "$extensions." + EXT + " on every semantic token.")
    for t in TOKENS:
        node = root
        for seg in t.path[:-1]:
            node = node.setdefault(seg, OrderedDict())
        leaf = OrderedDict()
        leaf["$type"] = t.type
        leaf["$value"] = t.value
        if t.desc:
            leaf["$description"] = t.desc
        ext = OrderedDict()
        if t.modes:
            ext[EXT_MODES] = OrderedDict((k, v) for k, v in t.modes.items() if v is not None)
        if t.usage or t.rules or t.do_not_use:
            llm = OrderedDict()
            if t.usage:
                llm["usage"] = t.usage
            if t.rules:
                llm["rules"] = t.rules
            if t.do_not_use:
                llm["doNotUse"] = True
            if t.alternatives:
                llm["alternatives"] = t.alternatives
            ext[EXT] = llm
        if ext:
            leaf["$extensions"] = ext
        node[t.path[-1]] = leaf
    return root


def _collect_types(node):
    if "$value" in node:
        return {node.get("$type")}
    ts = set()
    for k, v in node.items():
        if not k.startswith("$"):
            ts |= _collect_types(v)
    return ts


def hoist_types(node, inherited=None):
    """`$type` наследуется от ближайшей группы (DTCG 2025.10), поэтому держим его
    на самой высокой группе, где тип единственный, и убираем у потомков."""
    if "$value" in node:
        if node.get("$type") == inherited:
            node.pop("$type", None)
        return
    ts = _collect_types(node)
    if len(ts) == 1 and next(iter(ts)) != inherited:
        inherited = next(iter(ts))
        node["$type"] = inherited
        node.move_to_end("$type", last=False)
    for k, v in list(node.items()):
        if not k.startswith("$"):
            hoist_types(v, inherited)


def enc(o, ind, width=114):
    flat = json.dumps(o, ensure_ascii=False, separators=(", ", ": "))
    if len(flat) + ind <= width:
        return flat
    pad = " " * (ind + 2)
    if isinstance(o, dict):
        parts = [pad + json.dumps(k, ensure_ascii=False) + ": " + enc(v, ind + 2, width)
                 for k, v in o.items()]
        return "{\n" + ",\n".join(parts) + "\n" + " " * ind + "}"
    if isinstance(o, list):
        parts = [pad + enc(v, ind + 2, width) for v in o]
        return "[\n" + ",\n".join(parts) + "\n" + " " * ind + "]"
    return flat


def dumps_compact(obj):
    for k, v in obj.items():
        if not k.startswith("$"):
            hoist_types(v)
    return enc(obj, 0)


# --------------------------------------------------------------------------------------
# 8. Вывод: CSS
# --------------------------------------------------------------------------------------
BY_PATH = {}


def resolve(value, mode=None, depth=0):
    """Разрешает алиас {a.b.c} в конечное значение (при необходимости в заданном режиме)."""
    if depth > 8:
        raise RuntimeError("alias loop")
    if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        target = BY_PATH[value[1:-1]]
        v = target.modes.get(mode, target.value) if mode else target.value
        return resolve(v, mode, depth + 1)
    return value


def css_color(v):
    if isinstance(v, str):
        return v
    hx = v.get("hex")
    alpha = v.get("alpha")
    if alpha is None:
        return hx
    r, g, b = int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16)
    return f"rgb({r} {g} {b} / {alpha})"


def css_value(t, mode=None):
    raw = t.modes.get(mode, t.value) if mode else t.value
    if t.type == "color":
        return css_color(resolve(raw, mode))
    if t.type == "dimension":
        d = resolve(raw, mode)
        return f"{d['value']}px"
    if t.type == "duration":
        d = resolve(raw, mode)
        return f"{d['value']}ms"
    if t.type == "cubicBezier":
        pts = resolve(raw, mode)
        return "cubic-bezier(%s)" % ", ".join(
            ("%g" % x) for x in pts)
    if t.type == "fontFamily":
        return ", ".join(f'"{f}"' if " " in f else f for f in raw)
    if t.type in ("fontWeight", "number"):
        # DTCG-тип number безразмерен, но в CSS этим величинам нужна единица
        # (как в 08-motion/03-…md §6)
        css_units = {"motion-translate-sm": "px", "motion-translate-md": "px",
                     "motion-stagger-step": "ms"}
        return "%s%s" % (raw, css_units.get(t.css, ""))
    if t.type == "transition":
        v = resolve(raw, mode) if isinstance(raw, str) else raw
        d = resolve(v["duration"], mode)
        f = resolve(v["timingFunction"], mode)
        delay = resolve(v["delay"], mode)
        out = "%dms cubic-bezier(%s)" % (d["value"], ", ".join("%g" % x for x in f))
        if delay["value"]:
            out += " %dms" % delay["value"]
        return out
    if t.type == "shadow":
        if not raw:
            return "none"
        parts = []
        for lay in raw:
            col = css_color(resolve(lay["color"], mode))
            parts.append("%dpx %dpx %dpx %dpx %s" % (
                lay["offsetX"]["value"], lay["offsetY"]["value"],
                lay["blur"]["value"], lay["spread"]["value"], col))
        return ", ".join(parts)
    raise RuntimeError("no css for " + t.type)


def mode_block(mode):
    """Строки CSS для режима: только семантические токены, значение которых отличается
    от базового. Диффом ловятся и алиасы второго порядка (space.inset.card -> space.md),
    и тени, у которых поменялись цветовые слои."""
    out = []
    for t in TOKENS:
        if t.path[0] == "primitive":
            continue
        try:
            base = css_value(t, None)
            now = css_value(t, mode)
        except Exception:
            continue
        if base != now:
            out.append(f"  --{t.css}: {now};")
    return out


def build_css():
    L = []
    L.append("/* ------------------------------------------------------------------")
    L.append("   Эталонный набор токенов ui-research, пресет «плотная админка».")
    L.append("   Сгенерировано из tokens.json (99-raw/tools/build_reference_tokens.py).")
    L.append("   Слой 1 — примитивы, слой 2 — семантика. Компоненты используют")
    L.append("   ТОЛЬКО переменные слоя 2.")
    L.append("   ------------------------------------------------------------------ */")
    L.append("")
    L.append(":root {")
    L.append("  color-scheme: light dark;")
    L.append("")
    groups = [("примитивы: цвет", lambda t: t.path[:2] == ["primitive", "color"]),
              ("примитивы: размеры", lambda t: t.path[:2] == ["primitive", "size"]),
              ("примитивы: шрифт", lambda t: t.path[:2] == ["primitive", "font"]),
              ("примитивы: движение", lambda t: t.path[0] == "primitive" and t.path[1] in ("duration", "easing"))]
    for title, pred in groups:
        L.append(f"  /* {title} */")
        for t in TOKENS:
            if pred(t):
                L.append(f"  --{t.css}: {css_value(t)};")
        L.append("")
    sem_groups = [("семантика: цвет", "color"), ("семантика: отступы", "space"),
                  ("семантика: размеры", "size"), ("семантика: форма", "radius"),
                  ("семантика: границы и фокус", "border"), ("семантика: глубина", "elevation"),
                  ("семантика: слои", "z"), ("семантика: прозрачность", "opacity"),
                  ("семантика: движение", "motion"),
                  ("семантика: пространственные величины движения", "motionScale"),
                  ("семантика: брейкпоинты", "breakpoint")]
    for title, top in sem_groups:
        L.append(f"  /* {title} */")
        for t in TOKENS:
            if t.path[0] == top:
                L.append(f"  --{t.css}: {css_value(t)};")
        L.append("")
    L.append("  /* семантика: типографика (составные роли разложены по свойствам) */")
    for role, size, lh, weight, tracking_em, family, *_ in TYPE_ROLES:
        tr = round(tracking_em * size, 3)
        L.append(f"  --type-{role}-family: var(--font-family-{family});")
        L.append(f"  --type-{role}-size: var(--font-size-{size});")
        L.append(f"  --type-{role}-leading: calc({lh} / {size});")
        L.append(f"  --type-{role}-weight: var(--font-weight-{weight});")
        L.append(f"  --type-{role}-tracking: {tr}px;")
    L.append("}")
    L.append("")
    # --- тёмная тема ---
    # Выводим ВЕСЬ транзитивный список семантических токенов, у которых изменилось
    # разрешённое значение: алиас, объявленный выше по дереву, сам не пересчитается.
    body = mode_block("dark")
    body.append("  --opacity-state-hover: 0.06;")
    body.append("  --opacity-state-active: 0.12;")
    L.append("/* Тёмная тема. Объявляется на том же элементе, что и светлая (:root),")
    L.append("   иначе семантические алиасы не пересчитаются: пользовательское свойство")
    L.append("   наследуется уже вычисленным. */")
    L.append("@media (prefers-color-scheme: dark) {")
    L.append("  :root:not([data-theme=\"light\"]) {")
    L.append("    color-scheme: dark;")
    for b in body:
        L.append("  " + b)
    L.append("  }")
    L.append("}")
    L.append("")
    L.append(":root[data-theme=\"dark\"] {")
    L.append("  color-scheme: dark;")
    for b in body:
        L.append(b)
    L.append("}")
    L.append("")
    # --- сокращённое движение ---
    red = mode_block("reduced")
    if red:
        L.append("/* Сокращённое движение. Модификатор ортогонален теме и плотности:")
        L.append("   трогает только токены движения. Согласовано с 08-motion/03-… §5.3. */")
        L.append("@media (prefers-reduced-motion: reduce) {")
        L.append("  :root {")
        for line in red:
            L.append("  " + line)
        L.append("  }")
        L.append("}")
        L.append("")
        L.append(':root[data-motion="reduced"] {')
        for line in red:
            L.append(line)
        L.append("}")
        L.append("")

    # --- плотность ---
    for mode, sel in (("compact", '[data-density="compact"]'),
                      ("comfortable", '[data-density="comfortable"]')):
        L.append(f"/* Плотность: {mode}. Переопределяется ТОЛЬКО семантический слой,")
        L.append("   поэтому режим можно включить на поддереве, а не только на :root. */")
        L.append(f"{sel} {{")
        for line in mode_block(mode):
            L.append(line)
        L.append("}")
        L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------------------
# 9. Вывод: Tailwind v4 @theme
# --------------------------------------------------------------------------------------
TW_COLOR_MAP = [
    ("canvas", "bg-canvas"), ("surface", "bg-surface"), ("surface-raised", "bg-surface-raised"),
    ("surface-hover", "bg-surface-hover"), ("subtle", "bg-subtle"), ("component", "bg-component"),
    ("component-hover", "bg-component-hover"), ("component-active", "bg-component-active"),
    ("selected", "bg-selected"), ("selected-hover", "bg-selected-hover"), ("inverse", "bg-inverse"),
    ("border-subtle", "border-subtle"), ("border-default", "border-default"),
    ("border-strong", "border-strong"),
    ("fg", "fg-primary"), ("fg-secondary", "fg-secondary"), ("fg-tertiary", "fg-tertiary"),
    ("fg-disabled", "fg-disabled"), ("fg-on-accent", "fg-on-accent"),
    ("fg-on-inverse", "fg-on-inverse"),
    ("icon", "icon-default"), ("icon-subtle", "icon-subtle"),
    ("accent-subtle", "accent-bg"), ("accent-border", "accent-border"),
    ("accent-solid", "accent-solid"), ("accent-solid-hover", "accent-solid-hover"),
    ("accent-fg", "accent-text"),
    ("focus-ring", "focus-ring"), ("scrim", "overlay-scrim"), ("selection", "selection-bg"),
]
for _st in ("danger", "warning", "success", "info"):
    for _r in ("bg", "border", "solid", "on-solid", "text"):
        TW_COLOR_MAP.append((f"{_st}-{_r}" if _r != "solid" else _st, f"{_st}-{_r}"))
for _i in range(1, 6):
    TW_COLOR_MAP.append((f"chart-{_i}", f"chart-{_i}"))

SHADCN_BRIDGE = [
    ("background", "bg-canvas"), ("foreground", "fg-primary"),
    ("card", "bg-surface"), ("card-foreground", "fg-primary"),
    ("popover", "bg-surface-raised"), ("popover-foreground", "fg-primary"),
    ("primary", "accent-solid"), ("primary-foreground", "fg-on-accent"),
    ("secondary", "bg-component"), ("secondary-foreground", "fg-primary"),
    ("muted", "bg-subtle"), ("muted-foreground", "fg-tertiary"),
    ("accent", "bg-component-hover"), ("accent-foreground", "fg-primary"),
    ("destructive", "danger-solid"), ("destructive-foreground", "danger-on-solid"),
    ("border", "border-subtle"), ("input", "border-strong"), ("ring", "focus-ring"),
]


def build_tailwind():
    L = []
    L.append("/* ------------------------------------------------------------------")
    L.append("   Tailwind CSS v4. Подключается после tokens.css:")
    L.append("       @import \"tailwindcss\";")
    L.append("       @import \"./tokens.css\";")
    L.append("       @import \"./theme.css\";")
    L.append("   `@theme inline` подставляет ЗНАЧЕНИЕ ссылки, а не саму ссылку, —")
    L.append("   без `inline` тёмная тема не переключалась бы.")
    L.append("   ------------------------------------------------------------------ */")
    L.append("")
    L.append("@custom-variant dark (&:where([data-theme=\"dark\"], [data-theme=\"dark\"] *));")
    L.append("@custom-variant compact (&:where([data-density=\"compact\"], [data-density=\"compact\"] *));")
    L.append("")
    L.append("@theme inline {")
    L.append("  /* обнуляем дефолтную палитру и шкалы Tailwind, чтобы в проекте")
    L.append("     не осталось двух параллельных систем значений */")
    L.append("  --color-*: initial;")
    L.append("  --text-*: initial;")
    L.append("  --radius-*: initial;")
    L.append("  --shadow-*: initial;")
    L.append("  --breakpoint-*: initial;")
    L.append("")
    L.append("  /* служебные цвета, которые стёр `--color-*: initial` */")
    L.append("  --color-transparent: transparent;")
    L.append("  --color-current: currentColor;")
    L.append("  --color-white: var(--palette-white);")
    L.append("")
    L.append("  /* цвет -> bg-*, text-*, border-*, ring-*, fill-*, stroke-* */")
    for tw, css in TW_COLOR_MAP:
        L.append(f"  --color-{tw}: var(--{css});")
    L.append("")
    L.append("  /* мост совместимости с shadcn/ui: имена компонентов shadcn работают без правок */")
    for tw, css in SHADCN_BRIDGE:
        L.append(f"  --color-{tw}: var(--{css});")
    L.append("")
    L.append("  /* отступы -> p-*, gap-*, m-*, space-* */")
    L.append("  --spacing: 4px; /* база для числовых утилит: p-4 = 16px */")
    for t in TOKENS:
        if t.path[0] == "space" and len(t.path) == 2:
            L.append(f"  --spacing-{t.path[1]}: var(--{t.css});")
    for t in TOKENS:
        if t.path[0] == "space" and len(t.path) == 3:
            L.append(f"  --spacing-{t.path[1]}-{t.path[2]}: var(--{t.css});")
    L.append("")
    L.append("  /* размеры -> w-*, h-*, size-*, min-w-*, max-w-* */")
    for t in TOKENS:
        if t.path[0] == "size":
            L.append(f"  --spacing-{'-'.join(t.path[1:])}: var(--{t.css});")
    L.append("")
    L.append("  /* типографика -> text-body, text-page-title, … */")
    for role, size, lh, weight, tracking_em, family, *_ in TYPE_ROLES:
        L.append(f"  --text-{role}: var(--type-{role}-size);")
        L.append(f"  --text-{role}--line-height: var(--type-{role}-leading);")
        L.append(f"  --text-{role}--font-weight: var(--type-{role}-weight);")
        L.append(f"  --text-{role}--letter-spacing: var(--type-{role}-tracking);")
    L.append("  --font-sans: var(--font-family-sans);")
    L.append("  --font-mono: var(--font-family-mono);")
    L.append("")
    L.append("  /* радиусы -> rounded-* */")
    for t in TOKENS:
        if t.path[0] == "radius":
            L.append(f"  --radius-{t.path[1]}: var(--{t.css});")
    L.append("")
    L.append("  /* тени -> shadow-* */")
    for t in TOKENS:
        if t.path[0] == "elevation":
            L.append(f"  --shadow-{t.path[1]}: var(--{t.css});")
    L.append("")
    L.append("  /* брейкпоинты -> tablet:*, desktop:*, wide:* */")
    for t in TOKENS:
        if t.path[0] == "breakpoint":
            L.append(f"  --breakpoint-{t.path[1]}: var(--{t.css});")
    L.append("")
    L.append("  /* движение: `--ease-*` — штатное пространство имён Tailwind v4 (ease-enter);\n     `--duration-*` пространством имён не является, эти переменные\n     используются как duration-[var(--duration-state)] */")
    for t in TOKENS:
        if t.path[:2] == ["motion", "duration"]:
            L.append(f"  --duration-{t.path[2]}: var(--{t.css});")
    for t in TOKENS:
        if t.path[:2] == ["motion", "easing"]:
            L.append(f"  --ease-{t.path[2]}: var(--{t.css});")
    L.append("  /* составные переходы: пространства имён в Tailwind нет, применяются как")
    L.append("     transition: colors var(--motion-hover); */")
    L.append("}")
    L.append("")
    L.append("/* Утилиты, которых в Tailwind нет: слои и прозрачности */")
    L.append("@layer utilities {")
    for t in TOKENS:
        if t.path[0] == "z":
            L.append(f"  .z-{t.path[1]} {{ z-index: var(--{t.css}); }}")
    L.append("}")
    return "\n".join(L)


# --------------------------------------------------------------------------------------
# 10. Проверки
# --------------------------------------------------------------------------------------
def hex_of(path, mode=None):
    t = BY_PATH[path]
    v = t.modes.get(mode, t.value) if mode else t.value
    v = resolve(v, mode)
    return v["hex"], v.get("alpha")


def check():
    rep = []
    prim = [t for t in TOKENS if t.path[0] == "primitive"]
    sem = [t for t in TOKENS if t.path[0] != "primitive"]
    rep.append(f"ВСЕГО ТОКЕНОВ: {len(TOKENS)}   примитивов: {len(prim)}   семантических: {len(sem)}")
    by_top = OrderedDict()
    for t in TOKENS:
        key = ".".join(t.path[:2]) if t.path[0] == "primitive" else t.path[0]
        by_top[key] = by_top.get(key, 0) + 1
    rep.append("по группам: " + ", ".join(f"{k} {v}" for k, v in by_top.items()))
    n_dark = sum(1 for t in TOKENS if "dark" in t.modes and t.modes["dark"] is not None)
    n_comp = sum(1 for t in TOKENS if "compact" in t.modes)
    rep.append(f"переопределений dark: {n_dark}; compact/comfortable: {n_comp}")
    n_rules = sum(1 for t in TOKENS if t.rules)
    rep.append(f"токенов с блоком {EXT}: {n_rules} "
               f"({100.0 * n_rules / len(sem):.0f}% семантических, 0% примитивов)")

    # неиспользуемые примитивы
    used = set()
    for t in TOKENS:
        def walk(v):
            if isinstance(v, str) and v.startswith("{"):
                used.add(v[1:-1])
            elif isinstance(v, dict):
                for x in v.values():
                    walk(x)
            elif isinstance(v, list):
                for x in v:
                    walk(x)
        walk(t.value)
        for m in t.modes.values():
            walk(m)
    # Полные рампы хранятся целиком, даже если часть ступеней не имеет семантической роли:
    # нейтраль и акцент нужны для вывода новых ролей, шкала длительностей и кривая
    # `emphasized` взяты из набора 08-motion/03-…md §4 как есть.
    FULL_RAMPS = ("primitive.color.neutral.", "primitive.color.accent.",
                  "primitive.duration.", "primitive.easing.emphasized")
    unused = [t.dotted for t in prim if t.dotted not in used
              and not t.dotted.startswith(FULL_RAMPS)]
    unused_ramp = [t.dotted for t in prim if t.dotted not in used
                   and t.dotted.startswith(FULL_RAMPS)]
    rep.append("примитивы вне полных рамп, не использованные семантикой: " +
               (", ".join(unused) if unused else "нет"))
    rep.append("ступени полных рамп neutral/accent/duration без семантической роли (это норма, "
               "рампа хранится целиком): " + (", ".join(unused_ramp) if unused_ramp else "нет"))

    rep.append("")
    rep.append("КОНТРАСТ СЕМАНТИЧЕСКИХ ПАР (WCAG 2 / APCA Lc)")
    pairs = [
        ("light", "color.text.primary", "color.bg.surface", 4.5),
        ("light", "color.text.primary", "color.bg.canvas", 4.5),
        ("light", "color.text.secondary", "color.bg.surface", 4.5),
        ("light", "color.text.tertiary", "color.bg.surface", 4.5),
        ("light", "color.text.disabled", "color.bg.surface", 0.0),
        ("light", "color.accent.text", "color.bg.surface", 4.5),
        ("light", "color.accent.text", "color.accent.bg", 4.5),
        ("light", "color.text.on-accent", "color.accent.solid", 4.5),
        ("light", "color.border.strong", "color.bg.surface", 3.0),
        ("light", "color.border.default", "color.bg.surface", 0.0),
        ("light", "color.border.subtle", "color.bg.surface", 0.0),
        ("light", "color.focus-ring", "color.bg.surface", 3.0),
        ("light", "color.accent.solid", "color.bg.canvas", 3.0),
        ("light", "color.danger.text", "color.danger.bg", 4.5),
        ("light", "color.danger.on-solid", "color.danger.solid", 4.5),
        ("light", "color.danger.solid", "color.bg.canvas", 3.0),
        ("light", "color.warning.text", "color.warning.bg", 4.5),
        ("light", "color.warning.on-solid", "color.warning.solid", 4.5),
        ("light", "color.warning.solid", "color.bg.canvas", 3.0),
        ("light", "color.success.text", "color.success.bg", 4.5),
        ("light", "color.success.on-solid", "color.success.solid", 4.5),
        ("light", "color.success.solid", "color.bg.canvas", 3.0),
        ("light", "color.info.text", "color.info.bg", 4.5),
        ("light", "color.info.on-solid", "color.info.solid", 4.5),
        ("light", "color.text.primary", "color.bg.selected", 4.5),
        ("light", "color.text.on-inverse", "color.bg.inverse", 4.5),
        ("light", "color.text.primary", "color.bg.subtle", 4.5),
        # текст на приподнятой поверхности, selected + hover,
        # информативные пары (порог 0) для третичного текста на неосновных поверхностях
        ("light", "color.text.primary", "color.bg.surface-raised", 4.5),
        ("light", "color.text.secondary", "color.bg.surface-raised", 4.5),
        ("light", "color.text.tertiary", "color.bg.surface-raised", 4.5),
        ("light", "color.text.disabled", "color.bg.surface-raised", 0.0),
        ("light", "color.accent.text", "color.bg.surface-raised", 4.5),
        ("light", "color.danger.text", "color.bg.surface-raised", 4.5),
        ("light", "color.warning.text", "color.bg.surface-raised", 4.5),
        ("light", "color.success.text", "color.bg.surface-raised", 4.5),
        ("light", "color.info.text", "color.bg.surface-raised", 4.5),
        ("light", "color.text.secondary", "color.bg.selected", 4.5),
        ("light", "color.text.primary", "color.bg.selected-hover", 4.5),
        ("light", "color.text.secondary", "color.bg.selected-hover", 4.5),
        ("light", "color.accent.text", "color.bg.selected-hover", 4.5),
        ("light", "color.text.tertiary", "color.bg.subtle", 0.0),
        ("light", "color.text.tertiary", "color.bg.surface-hover", 0.0),
        ("light", "color.text.tertiary", "color.bg.selected", 0.0),
        ("dark", "color.text.primary", "color.bg.surface", 4.5),
        ("dark", "color.text.primary", "color.bg.canvas", 4.5),
        ("dark", "color.text.secondary", "color.bg.surface", 4.5),
        ("dark", "color.text.tertiary", "color.bg.surface", 4.5),
        ("dark", "color.text.disabled", "color.bg.surface", 0.0),
        ("dark", "color.accent.text", "color.bg.surface", 4.5),
        ("dark", "color.accent.text", "color.accent.bg", 4.5),
        ("dark", "color.text.on-accent", "color.accent.solid", 4.5),
        ("dark", "color.border.strong", "color.bg.surface", 3.0),
        ("dark", "color.border.default", "color.bg.surface", 0.0),
        ("dark", "color.border.subtle", "color.bg.canvas", 0.0),
        ("dark", "color.focus-ring", "color.bg.canvas", 3.0),
        ("dark", "color.accent.solid", "color.bg.canvas", 3.0),
        ("dark", "color.accent.solid", "color.bg.surface", 3.0),
        ("dark", "color.accent.solid-hover", "color.bg.surface", 3.0),
        ("dark", "color.danger.solid", "color.bg.surface", 3.0),
        ("dark", "color.warning.solid", "color.bg.surface", 3.0),
        ("dark", "color.success.solid", "color.bg.surface", 3.0),
        ("dark", "color.danger.text", "color.danger.bg", 4.5),
        ("dark", "color.danger.on-solid", "color.danger.solid", 4.5),
        ("dark", "color.warning.text", "color.warning.bg", 4.5),
        ("dark", "color.warning.on-solid", "color.warning.solid", 4.5),
        ("dark", "color.success.text", "color.success.bg", 4.5),
        ("dark", "color.success.on-solid", "color.success.solid", 4.5),
        ("dark", "color.info.text", "color.info.bg", 4.5),
        ("dark", "color.text.primary", "color.bg.selected", 4.5),
        ("dark", "color.text.on-inverse", "color.bg.inverse", 4.5),
        ("dark", "color.text.primary", "color.bg.subtle", 4.5),
        ("dark", "color.text.primary", "color.bg.surface-raised", 4.5),
        ("dark", "color.text.secondary", "color.bg.surface-raised", 4.5),
        ("dark", "color.text.tertiary", "color.bg.surface-raised", 4.5),
        ("dark", "color.text.disabled", "color.bg.surface-raised", 0.0),
        ("dark", "color.accent.text", "color.bg.surface-raised", 4.5),
        ("dark", "color.danger.text", "color.bg.surface-raised", 4.5),
        ("dark", "color.warning.text", "color.bg.surface-raised", 4.5),
        ("dark", "color.success.text", "color.bg.surface-raised", 4.5),
        ("dark", "color.info.text", "color.bg.surface-raised", 4.5),
        ("dark", "color.text.secondary", "color.bg.selected", 4.5),
        ("dark", "color.text.primary", "color.bg.selected-hover", 4.5),
        ("dark", "color.text.secondary", "color.bg.selected-hover", 4.5),
        ("dark", "color.accent.text", "color.bg.selected-hover", 4.5),
        ("dark", "color.text.tertiary", "color.bg.subtle", 0.0),
        ("dark", "color.text.tertiary", "color.bg.surface-hover", 0.0),
        ("dark", "color.text.tertiary", "color.bg.selected", 0.0),
    ]
    fails = 0
    for mode, fg, bg in [(m, a, b) for m, a, b, _ in pairs]:
        pass
    for mode, fg, bg, threshold in pairs:
        m = None if mode == "light" else "dark"
        fh, fa = hex_of(fg, m)
        bh, ba = hex_of(bg, m)
        if fa is not None:
            fh = composite(fh, fa, bh)
        w, a = wcag(fh, bh), apca(fh, bh)
        mark = ""
        if threshold and w < threshold:
            mark = f"   <<< ниже {threshold}"
            fails += 1
        rep.append(f"  {mode:5s} {fg.replace('color.',''):24s} на {bg.replace('color.',''):18s} "
                   f"{fh} / {bh}  {w:6.2f} / {a:7.1f}{mark}")
    rep.append(f"  порогов не пройдено: {fails} (ожидаемо 0 при threshold > 0)")

    # отключённый текст проверяется по APCA, а не по WCAG
    rep.append("")
    rep.append("ОТКЛЮЧЁННЫЙ ТЕКСТ: APCA |Lc| в коридоре 30–60 на каждой поверхности "
               "(цель 30–45 по 01-color/05 §4.2; ui_audit.py I1c принимает 30–60)")
    corridor_fails = 0
    for mode in ("light", "dark"):
        m = None if mode == "light" else "dark"
        fh, _ = hex_of("color.text.disabled", m)
        for bg in ("color.bg.surface", "color.bg.canvas", "color.bg.surface-raised",
                   "color.bg.subtle"):
            bh, _ = hex_of(bg, m)
            lc = abs(apca(fh, bh))
            mark = "" if 30 <= lc <= 60 else "   <<< вне коридора 30–60"
            if mark:
                corridor_fails += 1
            rep.append(f"  {mode:5s} text.disabled на {bg.replace('color.',''):18s} "
                       f"{fh} / {bh}  Lc {lc:6.1f}{mark}")
    rep.append(f"  вне коридора: {corridor_fails} (ожидаемо 0)")

    rep.append("")
    rep.append("ПАЛИТРА ГРАФИКОВ: минимальное ΔE OKLab при симуляции дальтонизма (порог 0.05)")
    for name, pal, bg in (("светлая", CHART_LIGHT, "#f8fafc"), ("тёмная", CHART_DARK, "#0f172b")):
        line = [f"  {name}:"]
        for cvd in ("protan", "deutan", "tritan"):
            sims = [sim_cvd(c, cvd) for c in pal]
            mn = min(dE_oklab(a, b) for a, b in itertools.combinations(sims, 2))
            line.append(f"{cvd} {mn:.3f}")
        mn_con = min(wcag(c, bg) for c in pal)
        line.append(f"| минимальный контраст к фону {mn_con:.2f}")
        rep.append("  ".join(line))

    rep.append("")
    rep.append("ТИПОГРАФИКА: проверка, что кегль × отношение даёт целые 4px")
    for role, size, lh, weight, tr, fam, *_ in TYPE_ROLES:
        got = size * (lh / size)
        rep.append(f"  {role:16s} {size:>2}px × {lh/size:.6f} = {got:.4f}px  "
                   f"(цель {lh}px, кратно 4: {'да' if lh % 4 == 0 else 'НЕТ'})  "
                   f"tracking {round(tr*size,3)}px")

    rep.append("")
    rep.append("СЛОИ ПОВЕРХНОСТЕЙ: светлота OKLCH (L, %)")
    for mode in (None, "dark"):
        vals = []
        for path in ("color.bg.canvas", "color.bg.surface", "color.bg.surface-raised",
                     "color.bg.subtle"):
            h, _ = hex_of(path, mode)
            vals.append(f"{path.split('.')[-1]} {hex2oklch(h)[0]*100:.1f}%")
        rep.append(f"  {'светлая' if mode is None else 'тёмная '}: " + "   ".join(vals))
    return "\n".join(rep)


# --------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Эталонная схема токенов ui: tokens.json, tokens.css, theme.css и отчёт")
    ap.add_argument("--out", default=str(kbpaths.out("ui", "reference-tokens", create=False)),
                    help="каталог вывода (по умолчанию $DDD_HOME/out/ui/reference-tokens)")
    args = ap.parse_args()
    build_primitives()
    build_semantic_color()
    build_semantic_layout()
    build_typography()
    for t in TOKENS:
        BY_PATH[t.dotted] = t
    os.makedirs(args.out, exist_ok=True)
    tree = build_json_tree()
    with open(os.path.join(args.out, "tokens.json"), "w", encoding="utf-8") as f:
        f.write(dumps_compact(tree) + "\n")
    with open(os.path.join(args.out, "tokens.css"), "w", encoding="utf-8") as f:
        f.write(build_css() + "\n")
    with open(os.path.join(args.out, "theme.css"), "w", encoding="utf-8") as f:
        f.write(build_tailwind() + "\n")
    report = check()
    with open(os.path.join(args.out, "report.txt"), "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(report)


if __name__ == "__main__":
    main()
