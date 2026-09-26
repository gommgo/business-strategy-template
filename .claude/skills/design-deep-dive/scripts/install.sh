#!/usr/bin/env bash
# install.sh — окружение утилит скилла design-deep-dive вне репозитория: $DDD_HOME, по умолчанию
# ${XDG_CACHE_HOME:-~/.cache}/design-deep-dive — одно на машину для всех клонов шаблона (Р90). В репозиторий ничего не пишет.
#
#   scripts/install.sh --dry-run                     # план и что уже стоит; ничего не меняет, в сеть не ходит
#   scripts/install.sh                               # venv + pip (группа core), npm-зависимости, каталоги out/cache/locks
#   scripts/install.sh --groups all --bin --models --browsers
#   scripts/install.sh --bin --from DIR              # бинарники из локальной папки с той же раскладкой, что $DDD_HOME/bin
#   scripts/install.sh --models --models-from DIR    # модели ONNX из локальной папки (rembg/, depth/, ocr/)
#   scripts/install.sh --catalogs                    # снимки каталогов polza, RouterAI, Gen-API и список доверия C2PA (сеть, 0 ₽)
#   scripts/install.sh --check                       # сверить установленное (версии, sha256), ничего не ставить
#
# Группы pip — секции «# [группа]» в requirements.txt: core, net, morph, svg, ocr, media (all — все).
# Идемпотентно: повторный запуск ставит только недостающее. Бинарник или модель с другим sha256 — ошибка, а не молчание.
# sha256 — установленного файла (Р55, Р59). Адреса загрузки записаны по релизам, но при сборке скилла сетью не проверялись:
# если архив не сошёлся с sha256, поставьте файл вручную (раскладка — таблица ниже) или укажите --from.
# Системные и без установки отсюда (путь — PATH или переменная DDD_*): Blender 5.2.2 LTS (DDD_BLENDER; запуск blender -b),
# ffmpeg 7.1 (DDD_FFMPEG), Node 24 + npm (DDD_NODE), Brave 153 для refs_client (DDD_BRAVE), bwrap и systemd-run для
# blender_supervisor, flock, системная libcairo2 для группы svg. MCP для Blender не нужен (основной путь — blender -b, Р59).
set -euo pipefail

SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$SKILL/scripts"
DDD_HOME="${DDD_HOME:-${XDG_CACHE_HOME:-$HOME/.cache}/design-deep-dive}"
PYTHON_BASE="${PYTHON:-python3}"
DRY=0; CHECK=0; PIP_GROUPS="core"; DO_NPM=1; DO_BIN=0; DO_MODELS=0; DO_BROWSERS=0; DO_CATALOGS=0; FROM=""; MODELS_FROM=""

usage() { sed -n '2,24p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --check) CHECK=1; DRY=1 ;;
    --groups) PIP_GROUPS="$2"; shift ;;
    --python) PYTHON_BASE="$2"; shift ;;
    --no-npm) DO_NPM=0 ;;
    --bin) DO_BIN=1 ;;
    --from) FROM="$2"; DO_BIN=1; shift ;;
    --models) DO_MODELS=1 ;;
    --models-from) MODELS_FROM="$2"; DO_MODELS=1; shift ;;
    --browsers) DO_BROWSERS=1 ;;
    --catalogs) DO_CATALOGS=1 ;;
    --all) PIP_GROUPS="all"; DO_BIN=1; DO_MODELS=1; DO_BROWSERS=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "install.sh: неизвестный ключ $1 (см. --help)" >&2; exit 2 ;;
  esac
  shift
done
[ "$PIP_GROUPS" = "all" ] && PIP_GROUPS="core,net,morph,svg,ocr,media"
[ "$CHECK" = 1 ] && { DO_BIN=1; DO_MODELS=1; }

say()  { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
run()  { if [ "$DRY" = 1 ]; then printf '  (план) %s\n' "$*"; else printf '  + %s\n' "$*"; "$@"; fi; }
sha()  { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }
ERR=0
fail() { printf '  ОШИБКА: %s\n' "$*" >&2; ERR=1; }

VENV="$DDD_HOME/venv"; PY="$VENV/bin/python"; NODE_HOME="$DDD_HOME/node"
say "скилл:     $SKILL"
say "DDD_HOME:  $DDD_HOME$([ "$DRY" = 1 ] && echo '   (--dry-run: ничего не меняется)')"

# ------------------------------------------------------------------ каталоги
step "каталоги окружения"
for d in "$DDD_HOME" "$DDD_HOME/out" "$DDD_HOME/cache" "$DDD_HOME/locks" "$DDD_HOME/bin" "$DDD_HOME/models" "$NODE_HOME"; do
  if [ -d "$d" ]; then say "  есть: $d"; else run mkdir -p "$d"; fi
done

# ------------------------------------------------------------------ Python
step "Python: venv и pip (группы: $PIP_GROUPS)"
if [ -x "$PY" ]; then
  say "  venv есть: $VENV ($("$PY" -c 'import sys; print(sys.version.split()[0])'))"
else
  command -v "$PYTHON_BASE" >/dev/null || fail "нет $PYTHON_BASE (нужен Python 3.10–3.13)"
  run "$PYTHON_BASE" -m venv "$VENV"
fi
REQ_TMP="$(mktemp)"; trap 'rm -f "$REQ_TMP"' EXIT
awk -v groups=",$PIP_GROUPS," '
  /^# \[[a-z]+\]/ { g = $2; gsub(/[\[\]]/, "", g); take = index(groups, "," g ",") > 0; next }
  /^[[:space:]]*(#|$)/ { next }
  take { print }' "$SCRIPTS/requirements.txt" > "$REQ_TMP"
say "  пакетов к установке: $(wc -l < "$REQ_TMP")"
if [ -x "$PY" ] && [ "$DRY" = 1 ]; then
  missing=$("$PY" - "$REQ_TMP" <<'PYEOF'
import sys
from importlib import metadata
miss = []
for line in open(sys.argv[1]):
    name, _, ver = line.strip().partition("==")
    try:
        have = metadata.version(name)
        if ver and have != ver:
            miss.append(f"{name} {have} → {ver}")
    except metadata.PackageNotFoundError:
        miss.append(f"{name}=={ver} (нет)")
print("\n".join(miss))
PYEOF
)
  if [ -n "$missing" ]; then say "  не хватает или другая версия:"; printf '%s\n' "$missing" | sed 's/^/    /'; else say "  все пакеты групп уже стоят"; fi
else
  run "$PY" -m pip install --disable-pip-version-check -q -r "$REQ_TMP"
fi

# ------------------------------------------------------------------ npm
if [ "$DO_NPM" = 1 ]; then
  step "npm: зависимости утилит в $NODE_HOME"
  NODE="${DDD_NODE:-$(command -v node || true)}"; NPM="${DDD_NPM:-$(command -v npm || true)}"
  if [ -z "$NODE" ] || [ -z "$NPM" ]; then
    say "  нет node/npm в PATH (DDD_NODE, DDD_NPM) — пропуск; нужен Node 24"
  else
    say "  node $("$NODE" --version) ($NODE)"
    want="$(sha "$SCRIPTS/package.json")"
    have="$(cat "$NODE_HOME/.package.sha256" 2>/dev/null || true)"
    if [ "$want" = "$have" ] && [ -d "$NODE_HOME/node_modules" ]; then
      say "  node_modules соответствует scripts/package.json"
    else
      run cp "$SCRIPTS/package.json" "$NODE_HOME/package.json"
      run "$NPM" install --prefix "$NODE_HOME" --no-audit --no-fund
      if [ "$DRY" = 0 ]; then printf '%s\n' "$want" > "$NODE_HOME/.package.sha256"; fi
    fi
    # validate.mjs (gltf_check.py) ищет gltf-validator рядом с собой: копия в $DDD_HOME/node, не симлинк (ESM идёт по realpath)
    if cmp -s "$SCRIPTS/blender/node/validate.mjs" "$NODE_HOME/validate.mjs"; then say "  validate.mjs на месте";
    else run cp "$SCRIPTS/blender/node/validate.mjs" "$NODE_HOME/validate.mjs"; fi
  fi
fi

# ------------------------------------------------------------------ бинарники
# id | версия | файл для сверки (от $DDD_HOME/bin) | sha256 файла | адрес архива (не проверен сетью; «-» — ставить вручную)
BINS='c2patool|0.27.22|c2patool/c2patool|0707d482c319f70bb668e4cafc96274abffa381b7e51063c86071dd7556c8b67|https://github.com/contentauth/c2pa-rs/releases/download/c2patool-v0.27.22/c2patool-v0.27.22-x86_64-unknown-linux-gnu.tar.gz
exiftool|13.59|exiftool/exiftool|a6b8018093845ac93011307bac4ab630d6604b2365fc7f66bb88c88d7dedb5ed|https://sourceforge.net/projects/exiftool/files/Image-ExifTool-13.59.tar.gz/download
libavif|1.4.2|libavif/avifenc|bfa76fdb43b4903972ed2baedbff889d4f1e0b19efe7fe934044cf83e4b709a5|-
libavif|1.4.2|libavif/avifdec|a71ee96957d05b6a288b3269fc14227340a2a2b64da84b721e1ed09567df641e|-
libjxl|0.12.0|libjxl/tools/ssimulacra2|a7de3fb2fcc802bec6d7c8372060c2853c6e03fc06879a0263385dfa7a069691|https://github.com/libjxl/libjxl/releases/download/v0.12.0/jxl-linux-x86_64-static-v0.12.0.tar.gz
libjxl|0.12.0|libjxl/tools/cjxl|c43d5bfbf1b359947a6edb61edb0bfc079924ee9801b30895533ff1fce83ee28|https://github.com/libjxl/libjxl/releases/download/v0.12.0/jxl-linux-x86_64-static-v0.12.0.tar.gz
libjxl|0.12.0|libjxl/tools/djxl|67bdc98fdca7f93d7b77f3473e818b251ba107109ee83b3b37ccbd90066f2454|https://github.com/libjxl/libjxl/releases/download/v0.12.0/jxl-linux-x86_64-static-v0.12.0.tar.gz
libwebp|1.6.0|libwebp/cwebp|5ac7ece6bdda1587f3c169ce74ab2734994f9d14e07fc5358208443c1b29edec|https://storage.googleapis.com/downloads.webp/releases/libwebp-1.6.0-linux-x86-64.tar.gz
libwebp|1.6.0|libwebp/dwebp|f4b035afc457f08d18124c822e554af5f8537c9e6c1e0e4a871297f90eda145b|https://storage.googleapis.com/downloads.webp/releases/libwebp-1.6.0-linux-x86-64.tar.gz
rife-ncnn-vulkan|20221029 (модель rife-v4.6)|rife-ncnn-vulkan/rife-ncnn-vulkan|5c256556195216ddfca103073b0fd37e33e154c8aa40666775fcae8d6a6580b4|https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/rife-ncnn-vulkan-20221029-ubuntu.zip
realesrgan-ncnn-vulkan|v0.2.0 (20220424)|realesrgan-ncnn-vulkan/realesrgan-ncnn-vulkan|22c2296a39b40cc43ac92615c827ab6d4b60b7142e8cee59f718e3f8e2cdbda9|https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip
vtracer|1.0.0-alpha.4 (musl)|vtracer-1.0.0a4/vtracer|43ad969fdac4f9d36e31a2f5d8650781248ba8bb7438c3778b378d9a7eaaa52e|-
potrace|1.16|potrace-1.16/potrace|e2d26f8322a7770a6ccdcf30889503b6c61e27ed8a30f13fc8f340174eb435b0|https://potrace.sourceforge.net/download/1.16/potrace-1.16.linux-x86_64.tar.gz
gltfpack|1.2|gltfpack-1.2/gltfpack|7e0dc08489835df804a83ca111c2cac6f8431f5a7b0e5453d94d6749a988b32f|https://github.com/zeux/meshoptimizer/releases/download/v1.2/gltfpack-ubuntu.zip
KTX-Software|4.4.2|KTX-Software-4.4.2-Linux-x86_64/bin/toktx|2a11939550fcc2d9b324c66d08f756ce3f512c8a02f6f5b03885e1a8b28f67f4|https://github.com/KhronosGroup/KTX-Software/releases/download/v4.4.2/KTX-Software-4.4.2-Linux-x86_64.tar.bz2'

# id | файл (от $DDD_HOME/models) | sha256 | адрес (не проверен сетью; «-» — вручную)
MODELS='u2netp|rembg/u2netp.onnx|309c8469258dda742793dce0ebea8e6dd393174f89934733ecc8b14c76f4ddd8|https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx
isnet-general-use|rembg/isnet-general-use.onnx|60920e99c45464f2ba57bee2ad08c919a52bbf852739e96947fbb4358c0d964a|https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-general-use.onnx
depth-anything-v2-small|depth/depth_anything_v2_small.onnx|afb6a5c28f3b6bf1618c6e43f02073ef9dfdc70e937502d51603e57b0a1df10c|https://huggingface.co/onnx-community/depth-anything-v2-small/resolve/main/onnx/model.onnx
pp-ocrv5-rec-eslav|ocr/eslav_PP-OCRv5_rec_mobile.onnx|08705d6721849b1347d26187f15a5e362c431963a2a62bfff4feac578c489aab|-
pp-ocrv5-rec-en|ocr/en_PP-OCRv5_rec_mobile.onnx|c3461add59bb4323ecba96a492ab75e06dda42467c9e3d0c18db5d1d21924be8|-
pp-ocrv5-rec-cyrillic|ocr/cyrillic_PP-OCRv5_rec_mobile.onnx|90f761b4bfcce0c8c561c0cb5c887b0971d3ec01c32164bdf7374a35b0982711|-
pp-ocrv5-det|ocr/ch_PP-OCRv5_det_mobile.onnx|4d97c44a20d30a81aad087d6a396b08f786c4635742afc391f6621f5c6ae78ae|-'

fetch_unpack() {  # url → распаковать архив в $1dir (первая папка пути), корень архива с одной папкой снимается
  local url="$1" top="$2" tmp; tmp="$(mktemp -d)"
  run curl -fL --retry 2 -o "$tmp/pkg" "$url"
  [ "$DRY" = 1 ] && { rm -rf "$tmp"; return 0; }
  "$PYTHON_BASE" - "$tmp/pkg" "$tmp/x" <<'PYEOF'
import shutil, sys, tarfile, zipfile
src, dst = sys.argv[1], sys.argv[2]
if zipfile.is_zipfile(src):
    zipfile.ZipFile(src).extractall(dst)
elif tarfile.is_tarfile(src):
    t = tarfile.open(src)
    try:
        t.extractall(dst, filter="data")
    except TypeError:                   # Python < 3.12
        t.extractall(dst)
else:
    import os; os.makedirs(dst); shutil.copy(src, dst + "/file")
PYEOF
  local n; n=$(find "$tmp/x" -mindepth 1 -maxdepth 1 | wc -l)
  if [ "$n" = 1 ] && [ -d "$(find "$tmp/x" -mindepth 1 -maxdepth 1)" ]; then src="$(find "$tmp/x" -mindepth 1 -maxdepth 1)"; else src="$tmp/x"; fi
  mkdir -p "$DDD_HOME/bin/$top"; cp -a "$src/." "$DDD_HOME/bin/$top/"; rm -rf "$tmp"
}

place() {  # kind(bin|models) rel sha url from_dir
  local kind="$1" rel="$2" want="$3" url="$4" from="$5" dst="$DDD_HOME/$1/$2"
  if [ -f "$dst" ]; then
    if [ "$(sha "$dst")" = "$want" ]; then say "  ok   $rel"; return 0; fi
    fail "$rel: sha256 $(sha "$dst" | cut -c1-12)… ≠ $(printf %.12s "$want")…"; return 0
  fi
  [ "$CHECK" = 1 ] && { say "  нет  $rel"; return 0; }
  if [ -n "$from" ]; then
    if [ -f "$from/$rel" ]; then
      if [ "$(sha "$from/$rel")" != "$want" ]; then fail "$from/$rel: sha256 не совпал"; return 0; fi
      local top="${rel%%/*}"
      if [ "$kind" = bin ] && [ -d "$from/$top" ]; then run mkdir -p "$DDD_HOME/bin/$top"; run cp -a "$from/$top/." "$DDD_HOME/bin/$top/";
      else run mkdir -p "$(dirname "$dst")"; run cp "$from/$rel" "$dst"; fi
      return 0
    fi
    say "  в $from нет $rel"
  fi
  if [ "$url" = "-" ]; then say "  вручную: $rel (sha256 $want)"; return 0; fi
  if [ "$kind" = models ]; then run mkdir -p "$(dirname "$dst")"; run curl -fL --retry 2 -o "$dst" "$url";
  else fetch_unpack "$url" "${rel%%/*}"; fi
  if [ "$DRY" = 0 ]; then
    if [ -f "$dst" ] && [ "$(sha "$dst")" = "$want" ]; then say "  ok   $rel"; chmod +x "$dst" 2>/dev/null || true;
    else fail "$rel: после загрузки файла нет или sha256 другой — поставьте вручную (раскладка выше)"; fi
  fi
}

if [ "$DO_BIN" = 1 ]; then
  step "бинарники в $DDD_HOME/bin (версии и sha256)"
  while IFS='|' read -r id ver rel want url; do
    say "  $id $ver"; place bin "$rel" "$want" "$url" "$FROM"
  done <<< "$BINS"
fi
if [ "$DO_MODELS" = 1 ]; then
  step "модели ONNX в $DDD_HOME/models (sha256; OCR — kb/ai-media/11-evaluation-qa/thresholds.yaml → ocr_models)"
  while IFS='|' read -r id rel want url; do
    say "  $id"; place models "$rel" "$want" "$url" "$MODELS_FROM"
  done <<< "$MODELS"
fi

# ------------------------------------------------------------------ браузеры Playwright
if [ "$DO_BROWSERS" = 1 ]; then
  step "браузеры Playwright в $DDD_HOME/browsers (kbpaths ставит PLAYWRIGHT_BROWSERS_PATH, если каталог есть)"
  if [ -d "$DDD_HOME/browsers" ] && ls "$DDD_HOME/browsers" | grep -q chromium; then say "  chromium есть";
  else run env PLAYWRIGHT_BROWSERS_PATH="$DDD_HOME/browsers" "$PY" -m playwright install chromium; fi
fi

# ------------------------------------------------------------------ снимки каталогов (данные, пересоздаются бесплатно)
if [ "$DO_CATALOGS" = 1 ]; then
  step "снимки каталогов и список доверия C2PA в $DDD_HOME/cache/ai-media (бесплатные GET)"
  run "$PY" "$SCRIPTS/ai-media/polza_catalog.py" snapshot
  run "$PY" "$SCRIPTS/ai-media/mp_client.py" snapshot --channel all
  TRUST_DIR="$DDD_HOME/cache/ai-media/c2pa-trust-2026-09-23"
  TRUST_SHA=75cacc98b79ecac33713c7ecfb58d4a0ef383f3c1f886e7409f9e37e8664aea5
  if [ -f "$TRUST_DIR/C2PA-TRUST-LIST.pem" ]; then say "  список доверия C2PA есть";
  else
    run mkdir -p "$TRUST_DIR"
    run curl -fL --retry 2 -o "$TRUST_DIR/C2PA-TRUST-LIST.pem" https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TRUST-LIST.pem
    if [ "$DRY" = 0 ] && [ "$(sha "$TRUST_DIR/C2PA-TRUST-LIST.pem")" != "$TRUST_SHA" ]; then
      say "  список доверия C2PA обновился после 23.09.2026 (sha256 другой) — это нормально; путь задаёт C2PA_TRUST_PEM"
    fi
  fi
fi

# ------------------------------------------------------------------ системное (только проверка)
step "системное (не ставится отсюда; путь — PATH или DDD_*)"
for b in blender ffmpeg ffprobe node npm flock bwrap systemd-run brave-browser; do
  case "$b" in blender|ffmpeg|ffprobe|node|npm) v="DDD_$(echo "$b" | tr 'a-z' 'A-Z')" ;; brave-browser) v=DDD_BRAVE ;; *) v=DDD_NONE ;; esac
  p="${!v:-$(command -v "$b" || true)}"
  if [ -n "$p" ]; then say "  есть $b: $p"; else say "  нет  $b"; fi
done
say ""
[ "$ERR" = 0 ] && say "готово$([ "$DRY" = 1 ] && echo ' (--dry-run: ничего не менялось)')" || { say "есть ошибки (выше)"; exit 1; }
