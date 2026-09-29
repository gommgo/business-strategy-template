#!/bin/bash
set -u
S=/home/mm/git/stit-core/business-strategy-template/.claude/skills/design-deep-dive
PY=$HOME/.cache/design-deep-dive/venv/bin/python
PAGE=$S/kb/blender/12-recipes/examples/01-hero-product
SP=${C14_SP:-/home/mm/.cache/tmp/claude-1000/-home-mm-git-stit-core-business-strategy-template/b46ce4ca-e779-476f-a684-3ac3106d7ccb/scratchpad/c14}
O=$SP/chain/out
rm -rf $O; mkdir -p $O
mkdir -p $SP/cwd; cd $SP/cwd
$PY -m http.server 18765 --bind 127.0.0.1 --directory $PAGE >/dev/null 2>&1 &
SRV=$!
sleep 1
URL=http://127.0.0.1:18765/index.html
P=landing-product@L1
t() { echo "== $(date +%T) $*"; }
t anatomy desktop; $PY $S/scripts/site/page_anatomy.py $URL $O/anat --inp --label landing-product --net local 2>&1 | tail -1
t anatomy mobile; $PY $S/scripts/site/page_anatomy.py $URL $O/anat --mobile --inp --label landing-product --net local 2>&1 | tail -1
t accept desktop; $PY $S/scripts/ai-media/page_accept.py $PAGE/index.html --out $O/acc --budget-profile $P 2>&1 | tail -1; echo rc=$?
t accept mobile throttle; $PY $S/scripts/ai-media/page_accept.py $PAGE/index.html --out $O/acc --budget-profile $P --mobile --throttle 2>&1 | tail -1
t motion; $PY $S/scripts/creative/motion_check.py $PAGE/index.html --level L1 --page-type landing-product --out $O/motion --modes desk,mob,rm 2>&1 | tail -1
t probe; $PY $S/scripts/blender/site_probe.py $URL $O/probe --quick > /dev/null 2>&1; echo rc=$?
t probe no3d; $PY $S/scripts/blender/site_probe.py $URL $O/probe --quick --no-3d > /dev/null 2>&1; echo rc=$?
t gate3d; $PY $S/scripts/blender/gate_check.py $O/probe/probe_quick.json desktop --baseline $O/probe/probe_no3d_quick.json --profile $P --json > $O/g3d_desktop.json; echo rc=$?
t probe mobile; $PY $S/scripts/blender/site_probe.py $URL $O/probe --quick --mobile --throttle --wait 16000 > /dev/null 2>&1; echo rc=$?
t probe mobile no3d; $PY $S/scripts/blender/site_probe.py $URL $O/probe --quick --mobile --throttle --wait 16000 --no-3d > /dev/null 2>&1; echo rc=$?
t gate3d mobile; $PY $S/scripts/blender/gate_check.py $O/probe/probe_mobile_thr_quick.json mobile --baseline $O/probe/probe_mobile_thr_no3d_quick.json --profile $P --json > $O/g3d_mobile.json; echo rc=$?
t gates; $PY $S/scripts/site/page_gates.py --profile $P --anatomy $O/anat --accept $O/acc --motion $O/motion --gate3d $O/g3d_desktop.json $O/g3d_mobile.json --html $PAGE/index.html --json > $O/verdict.json; echo rc=$?
$PY $S/scripts/site/page_gates.py --profile $P --anatomy $O/anat --accept $O/acc --motion $O/motion --gate3d $O/g3d_desktop.json $O/g3d_mobile.json --html $PAGE/index.html > $O/verdict.txt; echo rc=$?
kill $SRV
t done
