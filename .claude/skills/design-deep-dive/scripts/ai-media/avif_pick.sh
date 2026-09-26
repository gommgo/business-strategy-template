#!/bin/bash
# avif_pick.sh — минимальный AVIF, проходящий порог SSIMULACRA2 (агент H2, 23.09.2026). avifenc 1.4.2 (-s 6, 4:2:0), ssimulacra2 (libjxl 0.12.0).
# Запуск: 99-raw/tools/avif_pick.sh in.png out.avif [порог=80]   → строки q / байты / s2 и PICK q=…; [проверено: рендер 1024² → q40, 4,7 КБ, 80,7]
# Порог: ≥ 80 — hero и крупные фото (не видно при сравнении рядом), ≥ 70 — второстепенные (шкала README cloudinary/ssimulacra2).
B="${DDD_HOME:-${XDG_CACHE_HOME:-$HOME/.cache}/design-deep-dive}/bin"  # перенос: бинарники ставит scripts/install.sh
in=$1; out=$2; thr=${3:-80}; tmp=$(mktemp -d)
for q in 35 40 45 50 55 60 65 70 75 80 85; do
  $B/libavif/avifenc -q $q -s 6 -y 420 -j 4 "$in" "$tmp/q$q.avif" >/dev/null 2>&1
  $B/libavif/avifdec "$tmp/q$q.avif" "$tmp/q$q.png" >/dev/null 2>&1
  s=$($B/libjxl/tools/ssimulacra2 "$in" "$tmp/q$q.png")
  echo "q=$q $(stat -c %s "$tmp/q$q.avif") B s2=$s"
  if awk -v s="$s" -v t="$thr" 'BEGIN{exit !(s>=t)}'; then cp "$tmp/q$q.avif" "$out"; echo "PICK q=$q"; break; fi
done
rm -rf "$tmp"
