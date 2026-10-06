// focal.js — object-position по фокусной точке спецификации для бокса object-fit: cover.
// Формула — 06-art-direction-consistency/03-composition-for-web.md §3.2 (проверена в Chromium 5/5, ошибка ≤ 0,002):
//   s = max(bw/iw, bh/ih); px = (fx·iw·s − tx·bw) / (iw·s − bw), с обрезкой в [0; 1].
// data-focal='{"16:9":[fx,fy,tx,ty], "4:5":[…]}' — ключ по соотношению выбранного файла (арт-дирекшн <picture>),
// tx, ty — где в боксе должна оказаться точка (по умолчанию = fx, fy).
export function objectPosition(fx, fy, iw, ih, bw, bh, tx = fx, ty = fy) {
  const s = Math.max(bw / iw, bh / ih), ox = iw * s - bw, oy = ih * s - bh;
  const clamp = (v) => Math.min(Math.max(v, 0), 1);
  const px = ox < 1e-9 ? 0.5 : clamp((fx * iw * s - tx * bw) / ox);
  const py = oy < 1e-9 ? 0.5 : clamp((fy * ih * s - ty * bh) / oy);
  return `${(px * 100).toFixed(2)}% ${(py * 100).toFixed(2)}%`;
}

function ratioKey(w, h) {
  const r = w / h, table = {'21:9': 21 / 9, '16:9': 16 / 9, '3:2': 1.5, '4:3': 4 / 3, '1:1': 1, '4:5': 0.8, '2:3': 2 / 3, '9:16': 9 / 16};
  let best = '16:9', d = 9;
  for (const [k, v] of Object.entries(table)) if (Math.abs(v - r) < d) { d = Math.abs(v - r); best = k; }
  return best;
}

export function focal(img) {
  const map = JSON.parse(img.dataset.focal || '{}');
  const apply = () => {
    if (!img.naturalWidth) return;
    const f = map[ratioKey(img.naturalWidth, img.naturalHeight)];
    if (!f) return;
    const r = img.getBoundingClientRect();
    img.style.objectPosition = objectPosition(f[0], f[1], img.naturalWidth, img.naturalHeight, r.width, r.height, f[2] ?? f[0], f[3] ?? f[1]);
  };
  img.addEventListener('load', apply);          // срабатывает и при смене источника <picture> на брейкпоинте
  if (img.complete) apply();
  new ResizeObserver(apply).observe(img);
}

document.querySelectorAll('img[data-focal]').forEach(focal);
