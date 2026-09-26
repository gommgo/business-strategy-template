# G/00 — реестр стека: npm, GitHub, поддержка браузеров (2026-09-24)

- `pkgs.txt` → `npm view <пакет> name version license time.modified dist.unpackedSize deprecated` → `npm_view.raw/json`;
  `npm view <пакет> time` → `time_*.json` → `npm_release.json` (версия, дата релиза последней версии, стабильных релизов за
  365 дней, дата создания). Node 24.21, npm 12.0.2.
- `github.tsv` — GitHub API без токена (звёзды, `pushed_at`, архив, лицензия SPDX, открытые issues), 20 репозиториев, пауза 2 с.
- `support.mjs` — `@mdn/browser-compat-data` 8.1.3 (timestamp 2026-09-24T13:25:51Z) и `web-features` 3.39.0 (npm в этой папке)
  → `support.json`, `support.txt`: версии «с которой» по 8 браузерам для 67 ключей BCD и Baseline (low/high даты) для 37 фич.
  Текущие версии на дату BCD: Chrome 154 (2026-09-22), Edge 153, Firefox 156 (2026-09-15), Safari/iOS 27 (2026-09-14), Samsung 30.
- Выводы — в `07-stack-implementation/01-stack-choice.md` §3.1, §5, §7 и `stack.yaml` (`support`, `alive`).
- node_modules ≈ 25 МБ (восстановление `npm ci`).
