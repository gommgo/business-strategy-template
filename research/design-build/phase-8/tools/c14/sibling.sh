#!/bin/bash
# соседний чекаут: копия скилла в <tmp>/strategy/.claude/skills/design-deep-dive, рабочая папка — <tmp>/site (код-репо)
set -u
S=/home/mm/git/stit-core/business-strategy-template/.claude/skills/design-deep-dive
PY=$HOME/.cache/design-deep-dive/venv/bin/python
CH=/home/mm/.cache/tmp/claude-1000/-home-mm-git-stit-core-business-strategy-template/9704e581-2959-4b4d-8243-494959f577e7/scratchpad/chain/out
T=$(mktemp -d /home/mm/.cache/tmp/claude-1000/sibling-XXXX)
C=$T/strategy/.claude/skills/design-deep-dive
mkdir -p $C $T/site
cp -r $S/scripts $S/kb $C/
find $C -name __pycache__ -prune -exec rm -rf {} +
cd $T/site
R=../strategy/.claude/skills/design-deep-dive/scripts
ok() { if [ "$1" = 0 ]; then echo "OK   $2"; else echo "FAIL $2 (rc=$1)"; fi; }
# 1. копия читается: правим окно в копии budgets.yaml → --conditions показывает правку
sed -i 's/    window_after_load_s: 5$/    window_after_load_s: 7/' $C/kb/site/07-seo-geo-performance-analytics/budgets.yaml
W=$($PY $R/site/page_gates.py --conditions | $PY -c "import json,sys; print(json.load(sys.stdin)['window_after_load_s'])")
[ "$W" = 7 ]; ok $? "page_gates.py --conditions читает budgets.yaml копии (окно 7 в копии, 5 в оригинале): $W"
$PY $R/site/page_gates.py --resolve landing-product@L1 > $T/res.json; ok $? "page_gates.py --resolve из ../strategy/…"
$PY $R/site/page_gates.py --profile landing-product@L1 --anatomy $CH/anat --accept $CH/acc --motion $CH/motion --gate3d $CH/g3d_desktop.json --json > $T/v.json; rc=$?
V=$($PY -c "import json; d=json.load(open('$T/v.json')); print(d['verdict'], d['B'], d['S'])"); [ $rc -le 1 ]; ok $? "page_gates.py сводка из соседнего чекаута: $V"
$PY $R/site/page_gates.py --selftest > $T/pg.txt; ok $? "page_gates.py --selftest: $(tail -1 $T/pg.txt)"
$PY $R/blender/gate_check.py --selftest > $T/gc.txt; ok $? "gate_check.py --selftest: $(tail -1 $T/gc.txt)"
$PY $R/blender/gate_check.py $CH/probe/probe_quick.json desktop --baseline $CH/probe/probe_no3d_quick.json --profile landing-product@L1 --json > $T/g.json; rc=$?; [ $rc -le 1 ]; ok $? "gate_check.py на отчёте зонда из соседнего чекаута (код $rc)"
$PY $R/creative/motion_check.py --selftest > $T/mc.txt 2>&1; ok $? "motion_check.py --selftest: $(tail -1 $T/mc.txt)"
$PY $R/creative/motion_check.py report --in $CH/motion > $T/mcr.txt 2>&1; rc=$?; [ $rc -le 1 ]; ok $? "motion_check.py report по готовому results.json (код $rc)"
for u in site/page_anatomy.py ai-media/page_accept.py blender/site_probe.py blender/web_view.py site/run_axe_targets.py; do $PY $R/$u --help > /dev/null 2>&1; ok $? "$u --help"; done
$PY $R/site/geo_probe.py --selftest > $T/geo.txt 2>&1; ok $? "geo_probe.py --selftest: $(tail -1 $T/geo.txt)"
$PY $R/site/ia_probe.py --selftest > $T/ia.txt 2>&1; ok $? "ia_probe.py --selftest: $(tail -1 $T/ia.txt | cut -c1-60)"
$PY $R/lib/kbpaths.py > $T/kbp.txt; grep -q "^kb $C/kb" $T/kbp.txt; ok $? "kbpaths: kb — в копии"
ls $T/site | grep -v '^$' > $T/cwd.txt; [ ! -s $T/cwd.txt ]; ok $? "рабочая папка код-репо пуста — выходы не пишутся в cwd"
echo "копия: $T"
