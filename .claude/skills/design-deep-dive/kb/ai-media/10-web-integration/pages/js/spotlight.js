// spotlight.js — hero с двумя состояниями: нижний слой «ночь», верхний «рассвет» под маской-прожектором за курсором
// (приём ролика SLnGJ9iezYo, собранный по правилам базы).
// Прожектор: mask-image: radial-gradient по CSS-переменным --x/--y/--r; уход курсора — радиус плавно в 0 (@property --r);
// касание (hover: none) — прожектора нет, состояния переключает кнопка; reduce — без видео, переключение мгновенное.
// Две петли: одинаковая длина, общий старт, подтяжка расхождения > 1 кадра; пауза обеих одной кнопкой (WCAG 2.2.2).
const RM = matchMedia('(prefers-reduced-motion: reduce)');
const HOVER = matchMedia('(hover: hover) and (pointer: fine)');
const conn = navigator.connection || {};
const LOW_DATA = conn.saveData === true || /(^|-)2g$/.test(conn.effectiveType || '');

function fill(video) {
  const ok = [...video.querySelectorAll('source[data-src]')].filter((s) =>
    (!s.dataset.media || matchMedia(s.dataset.media).matches) && (!s.type || video.canPlayType(s.type)));
  video.querySelectorAll('source').forEach((s) => s.remove());
  for (const s of ok) { const n = document.createElement('source'); n.src = s.dataset.src; if (s.type) n.type = s.type; video.append(n); }
  return ok.length > 0;
}

export function spotlight(root) {
  const [base, top] = root.querySelectorAll('video[data-video]');
  const pauseBtn = root.querySelector('.media-toggle'), stateBtn = root.querySelector('[data-state-toggle]');
  let started = false, topStarted = false, userPaused = false, visible = true, raf = 0;

  // ---- прожектор
  const move = (e) => {
    const r = root.getBoundingClientRect();
    root.style.setProperty('--x', `${e.clientX - r.left}px`); root.style.setProperty('--y', `${e.clientY - r.top}px`);
    root.style.setProperty('--r', root.classList.contains('is-dawn') ? '0px' : `${Math.round(Math.min(280, innerWidth * 0.3))}px`);
  };
  if (HOVER.matches) {
    root.addEventListener('pointermove', (e) => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => move(e)); });
    root.addEventListener('pointerleave', () => root.style.setProperty('--r', '0px'));      // гаснет плавно (transition --r)
  }
  // ---- два состояния
  stateBtn.addEventListener('click', () => {
    const dawn = root.classList.toggle('is-dawn');
    stateBtn.setAttribute('aria-pressed', String(dawn));
    stateBtn.querySelector('span').textContent = dawn ? 'Показать ночь' : 'Показать рассвет';
    root.style.setProperty('--r', '0px');
  });
  // ---- видео
  const playing = () => started && !userPaused && visible && !RM.matches && document.visibilityState === 'visible';
  const sync = () => {
    if (!started) return;
    for (const v of topStarted ? [base, top] : [base]) playing() ? v.play().catch(() => {}) : v.pause();
    if (pauseBtn) {
      pauseBtn.hidden = false; pauseBtn.setAttribute('aria-pressed', String(!playing()));
      pauseBtn.querySelector('.sr-only').textContent = playing() ? 'Остановить фоновое видео' : 'Запустить фоновое видео';
      pauseBtn.querySelector('.i-pause').style.display = playing() ? '' : 'none';
      pauseBtn.querySelector('.i-play').style.display = playing() ? 'none' : '';
    }
  };
  const start = () => {                       // основа — после load и простоя
    if (started || RM.matches || LOW_DATA) return;
    if (!fill(base)) return;
    base.load(); started = true;
    base.addEventListener('canplay', () => { base.classList.add('is-on'); sync(); }, {once: true});
  };
  const startTop = () => {                    // верхний слой — только при первом взаимодействии: 0 байт, если его не открыли
    if (topStarted || !started || RM.matches || LOW_DATA || !fill(top)) return;
    top.load(); topStarted = true;
    top.addEventListener('canplay', () => { top.currentTime = base.currentTime; top.classList.add('is-on'); sync(); }, {once: true});
    // подтяжка: петли одной длины расходятся (буферизация, разный старт) — выравниваем верхний слой по основе
    setInterval(() => { if (!base.paused && Math.abs(top.currentTime - base.currentTime) > 2 / 24 && top.duration - base.currentTime > 0.2)
      top.currentTime = base.currentTime; }, 1000);
  };
  root.addEventListener('pointerenter', startTop, {once: true});
  stateBtn.addEventListener('click', startTop);
  if (pauseBtn) pauseBtn.addEventListener('click', () => { userPaused = !userPaused; sync(); });
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; sync(); }).observe(root);
  document.addEventListener('visibilitychange', sync);
  RM.addEventListener('change', () => { if (!RM.matches) start(); sync(); });
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 200));
  const go = () => idle(start, {timeout: 1500});
  if (document.readyState === 'complete') go(); else addEventListener('load', go, {once: true});
}

document.querySelectorAll('[data-spotlight]').forEach(spotlight);
