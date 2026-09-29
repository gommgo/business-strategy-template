#!/bin/bash
# Проверка по сценариям (phase-8/PLAN.md §6, check/KEY.md): свежие сборки фикстур и повтор команд ключа.
#   ct_prepare.sh <папка> key    — сборки <папка>/key/*, команды ключа, вывод — <папка>/key/*.txt и сводка в stdout
#   ct_prepare.sh <папка> agent  — чистые копии для агента: <папка>/agent/{S1,S2,S3,S4A,S4B} и живой tokens.json
#                                  <папка>/agent/live/tokens.json (color-accent-solid light #1d4ed8 → #1e40af)
# Журнальный инструмент: окружение $DDD_HOME, утилиты скилла; в репозиторий ничего не пишет.
set -u
D=${1:?папка}; MODE=${2:?key или agent}
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
S=$ROOT/.claude/skills/design-deep-dive
PY=${DDD_HOME:-$HOME/.cache/design-deep-dive}/venv/bin/python
P=$S/scripts/project
fx() { rm -rf "$2"; $PY $S/scripts/tests/fixture_project.py build "$1" --out "$2" > /dev/null || { echo "сборка $1 — ошибка"; exit 2; }; }
live() {  # копия tokens.json артефакта ДС с правкой заказчика: color-accent-solid, тема light
  mkdir -p "$(dirname "$2")"
  sed '/"name": "color-accent-solid"/s/"light": "#1d4ed8"/"light": "#1e40af"/' "$1" > "$2"
  diff "$1" "$2" | grep -c '^>' | sed 's/^/   правка живого tokens.json — строк: /'
}
case $MODE in
key)
  K=$D/key; mkdir -p $K
  fx input-landing $K/s1; fx input-cabinet $K/s2; fx cabinet-ds $K/s3; fx package-landing $K/s4a; fx package-defects $K/s4b
  cd $K
  r() { local name=$1; shift; "$@" > $K/$name.txt 2>&1; echo "== $name: код $?"; tail -3 $K/$name.txt | sed 's/^/   /'; }
  r s1-build  $PY $P/canvas_input.py build otves-remont-nn promo --stage wireframe --repo $K/s1
  r s1-check  $PY $P/canvas_input.py check otves-remont-nn promo --repo $K/s1
  r s1-rebuild $PY $P/canvas_input.py build otves-remont-nn promo --stage wireframe --repo $K/s1
  r s2-tree   $PY $P/tree.py check otves-office office --repo $K/s2
  r s2-states $PY $P/states.py check otves-office office --repo $K/s2
  r s2-map    $PY $P/screen_map.py check otves-office office --repo $K/s2
  r s2-build  $PY $P/canvas_input.py build otves-office office --stage mockup --repo $K/s2
  r s2-check  $PY $P/canvas_input.py check otves-office office --repo $K/s2
  TJ=$(find $K/s3 -path '*design/_design-system/project/tokens.json' | head -1)
  live "$TJ" $K/live/tokens.json
  r s3-sync-check $PY $P/ds_sync.py check otves-office --live $K/live/tokens.json --repo $K/s3
  r s3-sync-build $PY $P/ds_sync.py build otves-office --live $K/live/tokens.json --repo $K/s3
  r s3-dsbuild $PY $P/ds_build.py check otves-office --repo $K/s3
  r s3-cover  $PY $P/ds_coverage.py check otves-office office --stage mockup --repo $K/s3
  r s4a-build $PY $P/ready.py build otves-remont-nn promo --repo $K/s4a
  r s4a-check $PY $P/ready.py check otves-remont-nn promo --repo $K/s4a
  r s4b-remont $PY $P/design_audit.py check otves-remont-nn --repo $K/s4b
  r s4b-office $PY $P/design_audit.py check otves-office --repo $K/s4b
  ;;
agent)
  A=$D/agent; rm -rf $A; mkdir -p $A/live
  fx input-landing $A/S1; fx input-cabinet $A/S2; fx cabinet-ds $A/S3; fx package-landing $A/S4A; fx package-defects $A/S4B
  TJ=$(find $A/S3 -path '*design/_design-system/project/tokens.json' | head -1)
  live "$TJ" $A/live/tokens.json
  echo "папки: $A/{S1,S2,S3,S4A,S4B}; живой tokens.json: $A/live/tokens.json"
  ;;
*) echo "режим: key или agent"; exit 2 ;;
esac
