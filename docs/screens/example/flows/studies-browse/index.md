---
slug: studies-browse
name: 'Просмотр исследований'
description: 'Master/detail на desktop, серия из 3 экранов на mobile'
desktop: [studies-workspace]
mobile: [studies-list-m, study-detail-m, filters-m]
transitions:
  - { from: studies-list-m, to: study-detail-m, trigger: 'tap row' }
  - { from: studies-list-m, to: filters-m,       trigger: 'tap filter button' }
  - { from: filters-m,      to: studies-list-m, trigger: 'apply / close' }
  - { from: study-detail-m, to: studies-list-m, trigger: 'back' }
who: [doctor, nurse]
status: draft
---

# studies-browse

Поток просмотра каталога. На desktop master/detail/filters
сосуществуют на одном экране (`studies-workspace`); на mobile
разворачиваются в три самостоятельных экрана с собственной
навигацией. Полный card исследования (`study-detail` desktop /
`study-detail-m` mobile) — за пределами flow: туда уходит явный
`transitions-to-screen` из master-экрана.
