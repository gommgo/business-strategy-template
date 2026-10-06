// stacked-alpha.js — прозрачное видео «двойной высоты» (сверху RGB, снизу альфа) → WebGL2-canvas.
// Один файл играет везде, где есть WebGL2 и кодек (AV1 → HEVC → H.264 в <source>): VP9-alpha Safari не показывает,
// HEVC-alpha кодируется только на macOS (ai-media 09/02). Проверено: Chromium 153, альфа 0/255 в углу/центре.
// Фильтрация LINEAR с отступом полтекселя от середины кадра — без «перетекания» альфы в цвет (NEAREST ступенчат при масштабе).
const RM = matchMedia('(prefers-reduced-motion: reduce)');

const VS = `#version 300 es
in vec2 p; out vec2 uv;
void main() { uv = vec2((p.x + 1.0) * 0.5, 1.0 - (p.y + 1.0) * 0.5); gl_Position = vec4(p, 0.0, 1.0); }`;
const FS = `#version 300 es
precision mediump float;
in vec2 uv; uniform sampler2D t; uniform float halfTexel; out vec4 o;
void main() {
  float yc = clamp(uv.y * 0.5, 0.0, 0.5 - halfTexel);           // верхняя половина — цвет
  float ya = clamp(0.5 + uv.y * 0.5, 0.5 + halfTexel, 1.0);     // нижняя — альфа (яркость)
  vec3 c = texture(t, vec2(uv.x, yc)).rgb;
  float a = texture(t, vec2(uv.x, ya)).r;
  o = vec4(c * a, a);                                            // премультиплицированный вывод
}`;

export function stackedAlpha(root) {
  const canvas = root.querySelector('canvas'), video = root.querySelector('video'), still = root.querySelector('img');
  const fail = (why) => { root.dataset.alphaMode = 'still:' + why; if (canvas) canvas.hidden = true; if (video) video.remove(); };
  if (RM.matches) return fail('reduce');
  const gl = canvas.getContext('webgl2', {premultipliedAlpha: true, alpha: true, antialias: false});
  if (!gl) return fail('no-webgl2');
  const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; };
  const pr = gl.createProgram();
  gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr);
  if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) return fail('shader');
  gl.useProgram(pr);
  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
  for (const [k, v] of [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]])
    gl.texParameteri(gl.TEXTURE_2D, k, v);
  const uHalf = gl.getUniformLocation(pr, 'halfTexel');
  let visible = true, running = false, budgetEnds = 0;
  const LIMIT = Number(root.dataset.motionSeconds || 3);   // + добег до конца цикла (2 с) ≤ 5 с — WCAG 2.2.2 без кнопки
  const draw = () => {
    if (!video.videoWidth) return;
    const w = video.videoWidth, h = video.videoHeight / 2;
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; gl.viewport(0, 0, w, h); }
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, video);
    gl.uniform1f(uHalf, 0.5 / video.videoHeight);
    gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  };
  const loop = () => {
    draw();
    if (running && performance.now() > budgetEnds && video.currentTime < 0.12) {   // досмотрели цикл — стоп на кадре 0
      video.pause(); running = false; root.dataset.alphaState = 'rested'; return;
    }
    if (running) video.requestVideoFrameCallback(loop);
  };
  const replay = () => { budgetEnds = performance.now() + LIMIT * 1000; sync(); };
  root.addEventListener('pointerenter', replay); root.addEventListener('focusin', replay);
  const sync = () => {
    const go = visible && !RM.matches && document.visibilityState === 'visible' && performance.now() < budgetEnds;
    if (go) video.play().then(() => { if (!running) { running = true; video.requestVideoFrameCallback(loop); } root.dataset.alphaMode = 'webgl2'; })
                        .catch((e) => fail('play:' + e.name));
    else { video.pause(); running = false; }
  };
  video.addEventListener('error', () => fail('media-error'), true);
  video.addEventListener('loadeddata', () => { draw(); canvas.classList.add('is-live'); if (still) still.classList.add('is-hidden'); }, {once: true});
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; sync(); }).observe(root);
  document.addEventListener('visibilitychange', sync);
  RM.addEventListener('change', () => { if (RM.matches) { video.pause(); running = false; canvas.hidden = true; still && still.classList.remove('is-hidden'); } });
  for (const s of video.querySelectorAll('source[data-src]')) s.src = s.dataset.src;   // src только сейчас: при reduce — 0 байт
  video.preload = 'auto'; video.load(); budgetEnds = performance.now() + LIMIT * 1000; sync();
}

document.querySelectorAll('[data-stacked-alpha]').forEach(stackedAlpha);
