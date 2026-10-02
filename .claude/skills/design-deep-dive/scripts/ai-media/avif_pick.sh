#!/bin/bash
# avif_pick.sh — самый лёгкий файл для страницы, который проходит порог SSIMULACRA2 и укладывается в бюджет веса.
# Запуск: avif_pick.sh [-b КБ] [-d 8|10|12] [-y 444|422|420|400] [-s СКОРОСТЬ] [-r МИН:МАКС] ВХОД ВЫХОД.avif|.webp [ПОРОГ=80]
#   -b КБ        бюджет веса файла (max_kb слота плана ассетов); без ключа вес не ограничен
#   -d ГЛУБИНА   глубина цвета AVIF, бит (по умолчанию 10); -y — цветовая субдискретизация (по умолчанию 444);
#   -s СКОРОСТЬ  пресет avifenc 0–10, меньше — медленнее и плотнее (по умолчанию 4); -r — границы качества (35:85)
# AVIF — двоичный поиск по качеству: наименьшее q с оценкой не ниже порога; оценка — по декоду без усечения глубины
# (avifdec -d 16 → PNG 16 бит → ssimulacra2 к входу). WebP (выход .webp, cwebp -m 6 -sharp_yuv) — перебор каждого q в
# границах: оценка у WebP не монотонна по q, выбирается самый лёгкий файл, прошедший порог.
# С бюджетом: файл, прошедший порог, тяжелее бюджета или порог в границах не достигнут — берётся лучшее качество,
# которое в бюджет укладывается (у AVIF — двоичным поиском по весу), и код выхода 3.
# Порог: ≥ 80 — hero и крупные фото (не видно при сравнении рядом), ≥ 70 — второстепенные; числа —
# kb/ai-media/11-evaluation-qa/thresholds.yaml (encoding.ssimulacra2_hero_min, encoding.ssimulacra2_min).
# Вывод: строка на пробу «q=… <байт> B s2=…» и итог «PICK q=… <байт> B s2=…».
# Код выхода: 0 — файл записан, порог и бюджет выдержаны; 1 — файл не записан (в бюджет не укладывается и наименьшее
# качество, без бюджета — порог не достигнут и при наибольшем); 2 — ошибка вызова или окружения (нет входа, программы
# scripts/install.sh --bin); 3 — файл записан в бюджете, но оценка ниже порога.
B="${DDD_HOME:-${XDG_CACHE_HOME:-$HOME/.cache}/design-deep-dive}/bin"
usage() { sed -n '2,4p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }
budget=""; depth=10; yuv=444; speed=4; range="35:85"
while getopts "b:d:y:s:r:h" o; do
  case $o in
    b) budget=$OPTARG ;; d) depth=$OPTARG ;; y) yuv=$OPTARG ;; s) speed=$OPTARG ;; r) range=$OPTARG ;;
    h) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) usage ;;
  esac
done
shift $((OPTIND - 1))
[ $# -ge 2 ] || usage
in=$1; out=$2; thr=${3:-80}
qmin=${range%%:*}; qmax=${range##*:}
case "$qmin$qmax$depth$speed" in *[!0-9]*|"") echo "avif_pick.sh: -r, -d и -s — целые числа" >&2; exit 2 ;; esac
[ "$qmin" -le "$qmax" ] || { echo "avif_pick.sh: границы качества -r МИН:МАКС — МИН не больше МАКС" >&2; exit 2; }
[ -f "$in" ] || { echo "avif_pick.sh: нет входа $in" >&2; exit 2; }
case "$out" in
  *.avif) kind=avif; need="libavif/avifenc libavif/avifdec libjxl/tools/ssimulacra2" ;;
  *.webp) kind=webp; need="libwebp/cwebp libwebp/dwebp libjxl/tools/ssimulacra2" ;;
  *) echo "avif_pick.sh: выход — .avif или .webp" >&2; exit 2 ;;
esac
for p in $need; do
  [ -x "$B/$p" ] || { echo "avif_pick.sh: нет $B/$p — поставьте scripts/install.sh --bin" >&2; exit 2; }
done
limit=""
if [ -n "$budget" ]; then
  limit=$(awk -v b="$budget" 'BEGIN{ if (b + 0 > 0) printf "%d", b * 1024; }')
  [ -n "$limit" ] || { echo "avif_pick.sh: бюджет -b — число КБ больше нуля" >&2; exit 2; }
fi
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

# try Q → файл $tmp/q$Q.$kind, размер и оценка в SIZE[Q], SCORE[Q]; повторная проба не кодируется
declare -A SIZE SCORE
try() {
  local q=$1
  [ -n "${SIZE[$q]:-}" ] && return 0
  if [ $kind = avif ]; then
    "$B/libavif/avifenc" -q "$q" -s "$speed" -y "$yuv" -d "$depth" -j 4 "$in" "$tmp/q$q.avif" >/dev/null 2>&1 \
      && "$B/libavif/avifdec" -d 16 "$tmp/q$q.avif" "$tmp/q$q.png" >/dev/null 2>&1
  else
    "$B/libwebp/cwebp" -quiet -q "$q" -m 6 -sharp_yuv "$in" -o "$tmp/q$q.webp" >/dev/null 2>&1 \
      && "$B/libwebp/dwebp" -quiet "$tmp/q$q.webp" -o "$tmp/q$q.png" >/dev/null 2>&1
  fi
  [ -s "$tmp/q$q.png" ] || { echo "avif_pick.sh: проба q=$q не закодирована (вход $in)" >&2; exit 2; }
  SIZE[$q]=$(stat -c %s "$tmp/q$q.$kind")
  SCORE[$q]=$("$B/libjxl/tools/ssimulacra2" "$in" "$tmp/q$q.png" 2>/dev/null | tail -1)
  rm -f "$tmp/q$q.png"
  echo "q=$q ${SIZE[$q]} B s2=${SCORE[$q]}"
}
passes() { awk -v s="${SCORE[$1]}" -v t="$thr" 'BEGIN{exit !(s + 0 >= t + 0)}'; }
fits() { [ -z "$limit" ] || [ "${SIZE[$1]}" -le "$limit" ]; }

pick=""; fallback=""
if [ $kind = avif ]; then
  lo=$qmin; hi=$qmax                      # наименьшее q, проходящее порог
  while [ "$lo" -le "$hi" ]; do
    mid=$(( (lo + hi) / 2 )); try $mid
    if passes $mid; then pick=$mid; hi=$((mid - 1)); else lo=$((mid + 1)); fi
  done
  if [ -n "$limit" ] && { [ -z "$pick" ] || ! fits "$pick"; }; then
    pick=""; lo=$qmin; hi=$qmax           # наибольшее q, которое укладывается в бюджет
    while [ "$lo" -le "$hi" ]; do
      mid=$(( (lo + hi) / 2 )); try $mid
      if fits $mid; then fallback=$mid; lo=$((mid + 1)); else hi=$((mid - 1)); fi
    done
  fi
else
  for q in $(seq "$qmin" "$qmax"); do
    try "$q"
    if fits "$q"; then
      if passes "$q"; then
        { [ -z "$pick" ] || [ "${SIZE[$q]}" -lt "${SIZE[$pick]}" ]; } && pick=$q
      elif [ -z "$fallback" ] || awk -v a="${SCORE[$q]}" -v b="${SCORE[$fallback]}" 'BEGIN{exit !(a + 0 > b + 0)}'; then
        fallback=$q
      fi
    fi
  done
fi
if [ -n "$pick" ]; then
  cp "$tmp/q$pick.$kind" "$out"; echo "PICK q=$pick ${SIZE[$pick]} B s2=${SCORE[$pick]}"; exit 0
fi
if [ -n "$limit" ] && [ -n "$fallback" ]; then
  cp "$tmp/q$fallback.$kind" "$out"
  echo "PICK q=$fallback ${SIZE[$fallback]} B s2=${SCORE[$fallback]}"
  echo "avif_pick.sh: в бюджете $budget КБ порог $thr не достигнут — записано лучшее качество в бюджете" >&2
  exit 3
fi
if [ -n "$limit" ]; then
  echo "avif_pick.sh: в бюджет $budget КБ не укладывается и качество q=$qmin — файл не записан" >&2
else
  echo "avif_pick.sh: порог $thr не достигнут и при q=$qmax — файл не записан" >&2
fi
exit 1
