#!/bin/bash
set -u
S=/home/mm/git/stit-core/business-strategy-template/.claude/skills/design-deep-dive
PY=$HOME/.cache/design-deep-dive/venv/bin/python
PAGE=$S/kb/blender/12-recipes/examples/01-hero-product
SP=${C14_SP:-/home/mm/.cache/tmp/claude-1000/-home-mm-git-stit-core-business-strategy-template/b46ce4ca-e779-476f-a684-3ac3106d7ccb/scratchpad/c14}
O=$SP/chain/out
mkdir -p $SP/cwd; cd $SP/cwd
P=landing-product@L1
rm -rf $O/acc $O/motion
t() { echo "== $(date +%T) $*"; }
t accept desktop; $PY $S/scripts/ai-media/page_accept.py $PAGE/index.html --out $O/acc --budget-profile $P 2>&1 | tail -1
t accept mobile throttle; $PY $S/scripts/ai-media/page_accept.py $PAGE/index.html --out $O/acc --budget-profile $P --mobile --throttle 2>&1 | tail -1
t motion; $PY $S/scripts/creative/motion_check.py $PAGE/index.html --level L1 --page-type landing-product --out $O/motion --modes desk,mob,rm 2>&1 | tail -1
t gates; $PY $S/scripts/site/page_gates.py --profile $P --anatomy $O/anat --accept $O/acc --motion $O/motion --gate3d $O/g3d_desktop.json $O/g3d_mobile.json --html $PAGE/index.html --json > $O/verdict.json; echo rc=$?
$PY $S/scripts/site/page_gates.py --profile $P --anatomy $O/anat --accept $O/acc --motion $O/motion --gate3d $O/g3d_desktop.json $O/g3d_mobile.json --html $PAGE/index.html > $O/verdict.txt; echo rc=$?
t done
