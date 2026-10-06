// scroll-seq.js — «оборот товара по прокрутке» (VID-SCROLL): кадр выбирается долей прокрутки липкой секции.
// Режим frames: AVIF-секвенция → <canvas> (точный кадр, без декодера видео; кадры декодируются заранее img.decode()).
// Режим video: один файл с коротким GOP (8) → video.currentTime (перемотка декодирует ≤ 7 кадров, ai-media 09/03).
// reduce: прокрутка не крутит товар — показывается один выразительный кадр (data-rest), текст доступен как обычно.
const RM = matchMedia('(prefers-reduced-motion: reduce)');

export function scrollSeq(root) {
  const mode = new URLSearchParams(location.search).get('mode') || root.dataset.mode || 'frames';
  const canvas = root.querySelector('canvas'), video = root.querySelector('video'), still = root.querySelector('img');
  const n = Number(root.dataset.frames), pattern = root.dataset.pattern, rest = Number(root.dataset.rest || 0);
  const stats = root.__stats = {mode, seeks: 0, seekMs: [], drawn: 0, missing: 0, decodeMs: []};
  if (RM.matches) { root.dataset.state = 'reduce'; return; }        // только статичный кадр <img>
  const progress = () => {
    const r = root.getBoundingClientRect(), total = r.height - innerHeight;
    return Math.min(Math.max(-r.top / (total || 1), 0), 1);
  };
  let want = -1, busy = false;
  if (mode === 'video') {
    video.src = new URLSearchParams(location.search).get('src') || video.dataset.src; video.preload = 'auto'; video.load();
    const seek = () => {
      if (busy) return; const t = Math.min(progress() * video.duration, video.duration - 0.04);
      if (!isFinite(t) || Math.abs(t - video.currentTime) < 1 / 48) return;
      busy = true; const t0 = performance.now(); stats.seeks++;
      video.currentTime = t;
      video.addEventListener('seeked', () => { stats.seekMs.push(performance.now() - t0); busy = false; if (Math.abs(progress() * video.duration - video.currentTime) > 1 / 24) seek(); }, {once: true});
    };
    video.addEventListener('loadeddata', () => { root.dataset.state = 'live'; video.hidden = false; still.hidden = true; }, {once: true});
    addEventListener('scroll', () => requestAnimationFrame(seek), {passive: true});
    return;
  }
  // frames: первый кадр — сразу; остальные — после load, по порядку, с декодированием заранее
  const ctx = canvas.getContext('2d'), imgs = new Array(n);
  const url = (i) => pattern.replace('{i}', String(i).padStart(2, '0'));
  const load = (i) => { if (imgs[i]) return imgs[i]; const im = new Image(); im.src = url(i);
    const t0 = performance.now(); imgs[i] = im.decode().then(() => { stats.decodeMs.push(performance.now() - t0); return im; }).catch(() => null); return imgs[i]; };
  const draw = async () => {
    const i = Math.round(progress() * (n - 1)); if (i === want) return; want = i;
    const im = await load(i);
    if (!im || i !== want) { stats.missing += !im; return; }
    if (canvas.width !== im.naturalWidth) { canvas.width = im.naturalWidth; canvas.height = im.naturalHeight; }
    ctx.drawImage(im, 0, 0); stats.drawn++;
    if (root.dataset.state !== 'live') { root.dataset.state = 'live'; canvas.hidden = false; still.hidden = true; }
  };
  const preloadAll = () => { let i = 0; const next = () => { if (i >= n) return; load(i++).then(next); }; for (let k = 0; k < 4; k++) next(); };
  addEventListener('scroll', () => requestAnimationFrame(draw), {passive: true});
  if (document.readyState === 'complete') preloadAll(); else addEventListener('load', preloadAll, {once: true});
  new IntersectionObserver(([e]) => { if (e.isIntersecting) draw(); }, {rootMargin: '200px'}).observe(root);
}

document.querySelectorAll('[data-scroll-seq]').forEach(scrollSeq);
