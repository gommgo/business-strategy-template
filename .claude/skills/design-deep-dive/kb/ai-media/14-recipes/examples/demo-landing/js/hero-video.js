// hero-video.js — видео-слой hero поверх картинки-постера.
// Проверено: Chromium 153. Правила — 10-web-integration/02-video-delivery.md.
// 1) LCP — картинка <picture> (кадр 0 финального видео): видео начинает грузиться только после load + простоя;
// 2) prefers-reduced-motion: reduce, Save-Data, 2G → видео не запрашивается вовсе (0 байт), остаётся картинка;
// 3) источники выбираются по data-media (арт-дирекшн: 4:5 на телефоне, 16:9 на десктопе) и по canPlayType;
// 4) подмена картинки видео — по первому показанному кадру (requestVideoFrameCallback), без мигания;
// 5) кнопка паузы (WCAG 2.2.2, петля > 5 с), пауза вне экрана и в скрытой вкладке, реакция на смену настройки на лету.
const RM = matchMedia('(prefers-reduced-motion: reduce)');
const conn = navigator.connection || {};
const LOW_DATA = conn.saveData === true || /(^|-)2g$/.test(conn.effectiveType || '');

function pickSources(video) {
  const out = [];
  for (const s of video.querySelectorAll('source[data-src]')) {
    const m = s.dataset.media;
    if (m && !matchMedia(m).matches) continue;
    if (s.type && !video.canPlayType(s.type)) continue;   // '' — не умеет; 'maybe'/'probably' — пробуем
    out.push(s);
  }
  return out;
}

export function heroVideo(root) {
  const video = root.querySelector('video[data-video]');
  const btn = root.querySelector('.media-toggle');
  if (!video) return;
  let userPaused = false, visible = true, started = false;
  try { userPaused = sessionStorage.getItem('hero-video-paused') === '1'; } catch (e) { /* приватный режим */ }

  const setBtn = (playing) => {
    if (!btn) return;
    btn.hidden = !started;
    btn.setAttribute('aria-pressed', String(!playing));
    btn.querySelector('.sr-only').textContent = playing ? 'Остановить фоновое видео' : 'Запустить фоновое видео';
    btn.querySelector('.i-pause').style.display = playing ? '' : 'none';
    btn.querySelector('.i-play').style.display = playing ? 'none' : '';
  };
  const shouldPlay = () => started && !userPaused && visible && !RM.matches && document.visibilityState === 'visible';
  const sync = () => {
    if (!started) return;
    if (shouldPlay()) video.play().catch(() => {}); else video.pause();
    root.classList.toggle('is-video', !RM.matches);        // при reduce видео скрыто, видна картинка
    setBtn(shouldPlay());
  };

  const start = () => {
    if (started || RM.matches || LOW_DATA) return;
    const chosen = pickSources(video);
    if (!chosen.length) return;
    for (const s of video.querySelectorAll('source')) s.remove();   // оставляем только подходящие, в порядке приоритета
    for (const s of chosen) { const n = document.createElement('source'); n.src = s.dataset.src; if (s.type) n.type = s.type; video.append(n); }
    video.preload = 'auto';
    video.load();
    started = true;
    const reveal = () => { root.classList.add('is-video'); setBtn(shouldPlay()); };
    if ('requestVideoFrameCallback' in video) video.requestVideoFrameCallback(reveal);   // первый реально показанный кадр
    else video.addEventListener('playing', reveal, {once: true});
    sync();
  };

  if (btn) btn.addEventListener('click', () => {
    userPaused = !userPaused;
    try { sessionStorage.setItem('hero-video-paused', userPaused ? '1' : '0'); } catch (e) {}
    sync();
  });
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; sync(); }, {threshold: 0}).observe(root);
  document.addEventListener('visibilitychange', sync);
  RM.addEventListener('change', () => { if (!RM.matches) start(); sync(); });

  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 200));
  const go = () => idle(start, {timeout: 1500});
  if (document.readyState === 'complete') go(); else addEventListener('load', go, {once: true});
}

document.querySelectorAll('[data-hero-video]').forEach(heroVideo);
