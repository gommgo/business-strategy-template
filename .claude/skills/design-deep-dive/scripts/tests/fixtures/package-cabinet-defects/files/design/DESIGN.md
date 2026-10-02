---
version: alpha
name: "Отвес — кабинет заявок"
description: "Иллюстрация: токены ДС демо-кабинета «Отвес» (фикстура cabinet-ds) — пресет плотной админки, светлая тема по умолчанию и тёмная, плотность compact и comfortable, сокращённое движение."
colors:
  color-bg-canvas: "#f8fafc"
  color-bg-surface: "#ffffff"
  color-bg-subtle: "#f1f5f9"
  color-bg-selected: "#eff6ff"
  color-text-default: "#0f172a"
  color-text-muted: "#475569"
  color-text-on-accent: "#ffffff"
  color-border-default: "#e2e8f0"
  color-border-strong: "#64748b"
  color-accent-solid: "#1d4ed8"
  color-accent-text: "#1d4ed8"
  color-focus: "#2563eb"
  color-status-info: "#2563eb"
  color-status-success: "#16a34a"
  color-status-warning: "#d97706"
  color-status-danger: "#dc2626"
typography:
  type-title:
    fontFamily: "\"Golos Text\", Arial, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "-0.2px"
  type-metric:
    fontFamily: "\"Golos Text\", Arial, sans-serif"
    fontSize: "24px"
    fontWeight: 600
    lineHeight: 1.333333
    letterSpacing: "-0.36px"
  type-body:
    fontFamily: "\"Golos Text\", Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.428571
    letterSpacing: "0px"
  type-body-strong:
    fontFamily: "\"Golos Text\", Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.428571
    letterSpacing: "0px"
  type-label:
    fontFamily: "\"Golos Text\", Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.333333
    letterSpacing: "0.12px"
  type-caption:
    fontFamily: "\"Golos Text\", Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.333333
    letterSpacing: "0.12px"
rounded:
  radius-sm: "4px"
  radius-md: "8px"
spacing:
  space-2xs: "2px"
  space-xs: "4px"
  space-sm: "8px"
  space-md: "16px"
  space-lg: "24px"
  space-xl: "32px"
x-tokens:
  font-sans: "\"Golos Text\", Arial, sans-serif"
  size-control-md: "32px"
  size-control-lg: "40px"
  size-row-table: "36px"
  size-panel-sidebar: "240px"
  size-panel-topbar: "48px"
  size-panel-content-max: "1280px"
  elevation-raised: "0px 1px 2px 0px rgb(2 6 23 / 0.08), 0px 4px 8px -2px rgb(2 6 23 / 0.08)"
  breakpoint-tablet: "640px"
  breakpoint-desktop: "1024px"
  breakpoint-wide: "1440px"
  motion-duration-fast: "100ms"
  motion-duration-default: "150ms"
  motion-duration-slow: "200ms"
  motion-easing-standard: "cubic-bezier(0.4, 0, 0.2, 1)"
x-modes:
  dark:
    color-bg-canvas: "#0f172a"
    color-bg-surface: "#1e293b"
    color-bg-subtle: "#020617"
    color-bg-selected: "#334155"
    color-text-default: "#f8fafc"
    color-text-muted: "#cbd5e1"
    color-text-on-accent: "#020617"
    color-border-default: "#334155"
    color-accent-solid: "#60a5fa"
    color-accent-text: "#60a5fa"
    color-focus: "#60a5fa"
    color-status-info: "#60a5fa"
    color-status-success: "#4ade80"
    color-status-warning: "#fbbf24"
    color-status-danger: "#f87171"
    elevation-raised: "0px 1px 2px 0px rgb(2 6 23 / 0.4), 0px 4px 8px -2px rgb(2 6 23 / 0.4)"
  compact:
    space-sm: "4px"
    space-md: "12px"
    space-lg: "16px"
    size-row-table: "28px"
  comfortable:
    space-sm: "12px"
    space-md: "20px"
    space-lg: "32px"
  reduced:
    motion-duration-slow: "150ms"
x-narrow:
  below: "640px"
  type-body:
    fontSize: "16px"
---

# Отвес — кабинет заявок

Иллюстрация фикстуры cabinet-ds: дизайн-система демо-кабинета вымышленной студии ремонта «Отвес» — для самопроверок
утилит скилла, не данные проекта. Передняя часть с токенами над прозой собирается из `system.tokens.json`.

## Overview

Рабочий кабинет менеджера и замерщика: плотная админка на 8 часов в день, светлая бумага и один синий акцент, текст
14/20, таблицы с шапкой колонок, карточки на границе без тени. Голос — продуктовый: коротко и по делу.

## Colors

Фон `color-bg-canvas`, поверх — `color-bg-surface` с границей `color-border-default`. Единственный акцент —
`color-accent-solid`: главное действие области и текущий пункт навигации. Статусы заявки — роли `color-status-*`, текст
в метке дублирует цвет. Контраст: `color-text-default` к фону 17,1:1, `color-text-muted` — 7,2:1, граница поля
`color-border-strong` — 4,8:1.

## Typography

Golos Text с кириллицей. Роли: `type-title` для заголовка экрана, `type-body` для текста и ячеек, `type-label` для
подписей и колонок, `type-caption` для подсказок и ошибок, `type-metric` для числа плитки. На ширине меньше
`breakpoint-tablet` основной текст — 16 px.

## Layout

Каркас: боковая навигация `size-panel-sidebar`, верхняя панель `size-panel-topbar`, содержимое не шире
`size-panel-content-max`. Шкала отступов одна — `space-*`; плотность compact сдвигает шаги.

## Elevation & Depth

Карточки и таблицы держатся на границе; тень `elevation-raised` — только у выпадающих списков и всплывающих карточек.

## Shapes

`radius-sm` у контролов и меток статуса, `radius-md` у карточек и плиток; скруглённые и острые контейнеры не смешиваются.

## Components

Карточки артефакта сгруппированы по группам словаря компонентов: действия, ввод и выбор, навигация, обратная связь,
данные. Сопоставление типов компонентам — карта решений `system.yaml`; карта адреса объекта — расширение словаря проекта.

## Do's and Don'ts

- Одна главная кнопка на область; вторичная — рядом, третьей нет.
- Цвет статуса не единственный носитель смысла: у метки всегда есть текст.
- Не градиенты в фоне и кнопках; не тени у карточек на странице.
