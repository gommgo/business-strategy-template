#!/bin/sh
# Пересборка производных ДС фикстуры cabinet-ds и копирование их в её файлы
set -e
SK=/home/mm/git/stit-core/business-strategy-template/.claude/skills/design-deep-dive
SP=/home/mm/.cache/tmp/claude-1000/-home-mm-git-stit-core-business-strategy-template/9704e581-2959-4b4d-8243-494959f577e7/scratchpad
PY=/home/mm/.cache/design-deep-dive/venv/bin/python
rm -rf $SP/fx
$PY $SK/scripts/tests/fixture_project.py build cabinet-ds --out $SP/fx >/dev/null
$PY $SK/scripts/project/ds_build.py build otves-office --repo $SP/fx
D=$SP/fx/docs/projects/otves-office/design
FXD=$SK/scripts/tests/fixtures/cabinet-ds/files/design
cp $D/system.tokens.css $D/DESIGN.md $FXD/
cp $D/_design-system/project/tokens.json $D/_design-system/project/README.md $FXD/_design-system/project/
