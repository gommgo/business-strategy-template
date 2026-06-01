# example — образец оформления артефактов

Полный образцовый набор артефактов `docs/screens/`, покрывающий все
edge-кейсы канона: 4 kind, ссылочную целостность, layout-язык v2,
состояния, responsive, mobile-decomposition, контракт с
`@stit-design/ui`.

**Это образец, не реальные данные проекта.** Slug-рефы внутри example
замкнуты на самой папке и не валидируются по
`../../interface/`. Зеркало interface-сущностей живёт в
[`interface-stub.md`](interface-stub.md) и используется только этим
примером.

## Сюжет

Каталог исследований клиники. Участники — `doctor` и `nurse`.
Сценарий — «просмотр и архивация исследования».

```
[entrypoint: login]
        ↓
desktop ─── studies-workspace ──→ study-detail
                                  (полный card)

mobile (flow studies-browse):
   studies-list-m ⇄ study-detail-m
        ↕
   filters-m

[overlay поверх любого]
   confirm-archive
```

## Файлы

```
example/
├── README.md                    (этот файл)
├── interface-stub.md            7 мини-таблиц interface для example
├── flows/
│   └── studies-browse/index.md  desktop↔mobile (3 экрана)
├── shells/
│   ├── app-shell/index.md       6 слотов, responsive xs/sm/md
│   ├── mobile-shell/index.md    3 слота, без responsive
│   └── auth-shell/index.md      1 centered, без responsive
├── screens/
│   ├── studies-workspace/index.md  desktop master-detail, все 6 states
│   ├── study-detail/index.md       desktop, target transitions
│   ├── studies-list-m/index.md     mobile master
│   ├── study-detail-m/index.md     mobile detail
│   ├── filters-m/index.md          mobile filters
│   ├── login/index.md              entrypoint, viewport=any
│   └── confirm-archive/index.md    overlay-screen, status=stable
└── blocks/
    ├── filters-panel/index.md   форма, used-by 2 screens
    ├── studies-list/index.md    list+DataList, used-by 2 screens (desktop+mobile), status=stable
    ├── study-preview/index.md   минимум: один block-body
    ├── study-card/index.md      block-aside, Grid+span+areas, slots-контейнер
    ├── login-form/index.md      form-блок
    └── confirm-archive/index.md overlay-блок, status=stable
```

## Карта edge-кейсов

| Edge-кейс | Где смотреть |
|---|---|
| 1 desktop ↔ N mobile screen | [`flows/studies-browse`](flows/studies-browse/index.md) |
| 2 разных shell в одном flow | `app-shell` + `mobile-shell` |
| Responsive shell (xs/sm/md) | [`shells/app-shell`](shells/app-shell/index.md) |
| Минимальный shell (1 слот) | [`shells/auth-shell`](shells/auth-shell/index.md) |
| Все 6 screen-states | [`screens/studies-workspace`](screens/studies-workspace/index.md) |
| Inline-tree в слоте (не `block:`) | `studies-workspace.states.permission-denied` |
| `transitions-to-screen` (cross-flow target) | `studies-workspace → study-detail` |
| `mobile-of` + `role: master/detail/filters` | 3 mobile-screen внутри flow |
| `entrypoint: true` + `viewport: any` | [`screens/login`](screens/login/index.md) |
| Overlay-screen (`route: modal:…`) | [`screens/confirm-archive`](screens/confirm-archive/index.md) |
| Пустой опциональный слот (`—`) | `studies-workspace.slot-fills.overlay` |
| Block со всеми internal-zones | [`blocks/study-card`](blocks/study-card/index.md) (header+body+footer+aside) |
| Block минимальный (только body) | [`blocks/study-preview`](blocks/study-preview/index.md) |
| Block-контейнер с `slots` | `study-card.slots: [details]` |
| Sticky + Scroll внутри блока | [`blocks/studies-list`](blocks/studies-list/index.md) |
| Grid + span | `study-card.block-body` |
| Grid + areas | `study-card.block-body` (вариант) |
| Cluster + Row + justify/align/wrap | `studies-list.block-header` |
| Form / Field / Button | [`blocks/login-form`](blocks/login-form/index.md), `filters-panel` |
| Data binding (`data:study`, `data:study.name`) | [`blocks/studies-list`](blocks/studies-list/index.md) |
| `used-by-screens` разных viewport | `studies-list` (desktop + mobile master) |
| `status: stable` (контраст с `draft`) | `studies-list`, `confirm-archive`, login |
| Все 5 типов ux-substrate | через [`interface-stub`](interface-stub.md) |

## Как читать

1. Сначала [`interface-stub.md`](interface-stub.md) — словарь slug-рефов
   на бизнес-уровне.
2. Затем [`flows/studies-browse`](flows/studies-browse/index.md) — карта
   viewport-вариативности всего сценария.
3. Потом [`shells/`](shells/) — какие каркасы существуют.
4. Дальше [`screens/`](screens/) — какие route-points заполняют слоты.
5. Наконец [`blocks/`](blocks/) — раскрытие interface-block в дерево
   `ui:*`-компонентов.

Канон формы — в `../README.md` и под-README каждого kind. Этот example
показывает «как это выглядит на практике».
