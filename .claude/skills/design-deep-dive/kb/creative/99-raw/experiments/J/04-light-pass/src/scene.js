// scene.js v2 · L2 «Звено» — световой проход кодом · продолжатель J2 (волна 3) · 2026-09-25
// three 0.186.1 (npm) · esbuild 0.28.2 → 10-recipes/examples/l2-zveno/js/three-scene.js
// v1 (агент J, «до»): 99-raw/experiments/J/02-l2-zveno/src/scene.js — геометрия, кинематика, скан и рендер по требованию оттуда.
// Вопрос опыта J/04: сколько разрыва с Unseen (свет, материал, атмосфера, вторичное движение) закрывает код без Blender и ассетов.
// Что добавлено к v1 (0 байт ассетов, всё строится при старте):
//   свет      — своя «студия» для PMREM (верхний софтбокс, две полосы, заливка, тёплый отражатель) вместо RoomEnvironment;
//               ключевой направленный с мягкой тенью PCF 2048 (только quality high), холодный контровой; тон-маппинг Neutral;
//   материал  — MeshPhysicalMaterial: лак на белом пластике и тёмных крышках, анизотропия алюминия (high), лак платы;
//               крышки суставов — точёный профиль (фаска, канавка, пологий купол) вместо плоского диска;
//   атмосфера — фон-шейдер (градиент, свечение за объектом, тёплое пятно у пола, виньетка, дизеринг против полос);
//               пол-циклорама (освещённый пол с тенью, радиальное затухание в фон) + контактная тень;
//   вторичное — подход модуля с «зависанием» и дожимом, щелчок поворота (перелёт ≈ 11 %, bounce ≤ 0,2 — E 01 §7.3), кольцо
//               загорается при фиксации (и гаснет при разборке); инерция висящих модулей от скорости прокрутки (пружина ζ 0,8);
//               дуга камеры на станциях; начинка сустава вращается от прокрутки (генератор волн быстро, колесо медленно).
// Правила ворот K не меняются: кадры только по вводу, хвост ≤ 0,45 с после ввода (motion_check 0.1.2 снимает на +0,5 и +1,2 с),
// один контекст, DPR ≤ 1,5 (телефон 1,25), текст — только в HTML. quality 'low' (телефон): Standard-материалы, без карты теней.
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, Object3D, LatheGeometry, CylinderGeometry, BoxGeometry, TorusGeometry,
  ExtrudeGeometry, Shape, Vector2, Vector3, Matrix4, Quaternion, Euler, Color, MeshStandardMaterial, MeshPhysicalMaterial,
  MeshBasicMaterial, MeshLambertMaterial, ShaderMaterial, PlaneGeometry, SphereGeometry, BufferGeometry, Float32BufferAttribute,
  CanvasTexture, Plane, PMREMGenerator, AgXToneMapping, NeutralToneMapping, ACESFilmicToneMapping, SRGBColorSpace,
  DirectionalLight, DoubleSide, BackSide, PCFShadowMap, Box3,
} from 'three';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

export const version = 'zveno-scene v2 (light pass J2) 2026-09-25';

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));                        // доля отрезка [a, b]
const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2); // in-out cubic
const easeOut = (x) => 1 - Math.pow(1 - x, 3);
const lerp = (a, b, t) => a + (b - a) * t;
const bump = (x, a, b, c) => (x <= a || x >= c ? 0 : x < b ? ease(seg(x, a, b)) : 1 - ease(seg(x, b, c)));   // 0 → 1 → 0
// щелчок по прогрессу (не по времени): затухающий перелёт ≈ 11 % на доле 0,35, к концу ≈ 1 — bounce ≤ 0,2 (E 01 §7.3)
const snap = (u) => (u <= 0 ? 0 : u >= 1 ? 1 : 1 - Math.exp(-6 * u) * Math.cos(9 * u));
const TONE = { agx: AgXToneMapping, neutral: NeutralToneMapping, aces: ACESFilmicToneMapping };

// ---------- материалы: палитра art-direction «Звено» (тёмная студия, белый корпус, сигнальный оранжевый замок)
const PHYS_ONLY = ['clearcoat', 'clearcoatRoughness', 'anisotropy', 'anisotropyRotation'];
function makeMaterials(hq) {
  // high — Physical (лак, анизотропия); low (телефон) — Standard с теми же цветами: одна программа на тип, дешевле фрагмент
  const P = (o) => (hq ? new MeshPhysicalMaterial(o)
    : new MeshStandardMaterial(Object.fromEntries(Object.entries(o).filter(([k]) => !PHYS_ONLY.includes(k)))));
  return {
    // белый — нейтральный (#ecebe6 v1 с тёплым ключом давал бежево-серый: R−B белой точки 15 против 2 у v1 — J/04 white_check)
    shell: P({ color: '#f2f2f0', roughness: hq ? 0.36 : 0.3, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.08 }),
    // тёмные крышки и основание — тёмно-серый лакированный пластик, не металл: ключ падает на крышки вскользь, металл уходил в чёрное
    dark: P({ color: '#3a3e45', roughness: 0.48, metalness: 0.08, clearcoat: 0.5, clearcoatRoughness: 0.22 }),
    // крышки суставов — матовый тёмно-серый: глянцевый чёрный купол отражал тёмную комнату и читался как объектив
    cap: P({ color: '#4b5058', roughness: 0.62, metalness: 0.05, clearcoat: 0.2, clearcoatRoughness: 0.45 }),
    // алюминий — сатиновый (шерох. 0,4, слабая анизотропия): при 0,3 и 0,55 читался как хром с чёрными полосами
    alu: P({ color: '#b7bdc5', roughness: hq ? 0.4 : 0.36, metalness: 1, anisotropy: 0.35, anisotropyRotation: Math.PI / 2 }),
    copper: new MeshStandardMaterial({ color: '#c9824c', roughness: 0.3, metalness: 1 }),
    steel: new MeshStandardMaterial({ color: '#c6cad0', roughness: 0.2, metalness: 1 }),
    pcb: P({ color: '#16251d', roughness: 0.5, metalness: 0.1, clearcoat: 0.6, clearcoatRoughness: 0.3 }),
    // кольцо у каждого модуля своё: загорается при фиксации (emissive), одна программа на все
    ringNew: () => P({ color: '#ff5a1f', roughness: 0.38, metalness: 0.02, clearcoat: 0.5, clearcoatRoughness: 0.2,
      emissive: '#ff4d14', emissiveIntensity: 0 }),
  };
}

// ---------- скан: плоскость отсечения + светящаяся кромка на срезе (onBeforeCompile — свой фрагмент шейдера)
const scanPlane = new Plane(new Vector3(0, -1, 0), 10);                 // мировая: n·p + c ≥ 0 — видимо (так режет three)
const scanLocal = new Plane(new Vector3(0, -1, 0), 10);                 // в системе сустава; мировую считаем каждый кадр
const scanUniforms = { uScanN: { value: new Vector3(0, -1, 0) }, uScanC: { value: 10 }, uScanColor: { value: new Color('#ff6a2a') } };
function scanify(mat) {
  const m = mat.clone();
  m.side = DoubleSide;                                                   // внутренняя стенка видна через срез
  m.clippingPlanes = [scanPlane];
  m.clipShadows = true;                                                  // снятая половина корпуса не бросает тень на начинку
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, scanUniforms);
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vScanW;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvScanW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vScanW; uniform vec3 uScanN; uniform float uScanC; uniform vec3 uScanColor;')
      .replace('#include <emissivemap_fragment>',
        '#include <emissivemap_fragment>\nfloat sd = dot(uScanN, vScanW) + uScanC;\n' +
        'float band = 1.0 - smoothstep(0.0, 0.018, sd);\n' +                 // кромка 18 мм у среза
        'totalEmissiveRadiance += uScanColor * band * 2.6;\n' +
        'if (!gl_FrontFacing) { diffuseColor.rgb *= 0.42; }');               // внутренняя стенка темнее
  };
  m.customProgramCacheKey = () => 'scan';
  return m;
}

// ---------- геометрия: токарный профиль с фасками (выглядит «точёным», а не примитивом)
function lathe(points, segs = 64) { return new LatheGeometry(points.map(([r, y]) => new Vector2(r, y)), segs); }
function rodX(r, len, cham = 0.012, segs = 64) {                          // цилиндр вдоль X с фасками
  const h = len / 2;
  const g = lathe([[0, -h], [r - cham, -h], [r, -h + cham], [r, h - cham], [r - cham, h], [0, h]], segs);
  g.rotateZ(Math.PI / 2);
  return g;
}
function ringX(r, w, x, segs = 64) { const g = new CylinderGeometry(r, r, w, segs, 1, true); g.rotateZ(Math.PI / 2); g.translate(x, 0, 0); return g; }
function discX(r, t, x, segs = 64) { const g = new CylinderGeometry(r, r, t, segs); g.rotateZ(Math.PI / 2); g.translate(x, 0, 0); return g; }
function tubeY(r, y0, y1, segs = 48) { const g = new CylinderGeometry(r, r, y1 - y0, segs); g.translate(0, (y0 + y1) / 2, 0); return g; }
// крышка сустава (v2): фаска по краю, плоское поле с канавкой, пологий купол в центре — ловит полосы студии
// (первый вариант с кольцевым выступом и ступицей читался как объектив камеры); лицо в +X (dir 1) или −X (dir −1)
function capX(r, x, dir, segs = 64) {
  const g = lathe([[0, -0.022], [r, -0.022], [r, -0.012], [0.96 * r, -0.003], [0.9 * r, 0.002], [0.8 * r, 0.002], [0.78 * r, -0.001],
    [0.76 * r, 0.002], [0.42 * r, 0.003], [0.3 * r, 0.008], [0.15 * r, 0.011], [0, 0.012]], segs);
  g.rotateZ(dir > 0 ? -Math.PI / 2 : Math.PI / 2);
  g.translate(x, 0, 0);
  return g;
}

// модуль = группа из мешей по материалам (слитые геометрии) → ≤ 3 вызова на модуль
function moduleGroup(parts, MAT) {
  const grp = new Group();
  for (const [key, geos] of Object.entries(parts)) {
    if (!geos.length) continue;
    const g = geos.length > 1 ? mergeGeometries(geos.map((x) => (x.index ? x.toNonIndexed() : x))) : geos[0];
    const mesh = new Mesh(g, key === 'ring' ? MAT.ringNew() : MAT[key]);
    mesh.userData.key = key;
    grp.add(mesh);
  }
  const box = new Box3().setFromObject(grp);                              // центр модуля — ось инерции
  grp.userData.c = box.getCenter(new Vector3());
  return grp;
}

// Размеры (м). Кинематика: основание → J1 (рыскание, ось Y) → J2 (плечо, ось X) → L1 → J3 (локоть, ось X) → L2 → запястье (ось X) → захват
const L1 = 0.78, L2 = 0.62;
function buildModules(MAT) {
  const M = {};
  // 0 · основание
  M.base = moduleGroup({
    dark: [lathe([[0, 0], [0.44, 0], [0.44, 0.05], [0.34, 0.075], [0.3, 0.1], [0.3, 0.3], [0.27, 0.34], [0, 0.34]]),
      ...[0, 1, 2, 3].map((i) => { const g = new CylinderGeometry(0.03, 0.03, 0.03, 16); const a = Math.PI / 4 + i * Math.PI / 2; g.translate(Math.cos(a) * 0.37, 0.06, Math.sin(a) * 0.37); return g; })],
    ring: [(() => { const g = new CylinderGeometry(0.305, 0.305, 0.04, 64, 1, true); g.translate(0, 0.3, 0); return g; })()],
  }, MAT);
  // 1 · сустав J1 (вертикальный корпус)
  M.j1 = moduleGroup({
    shell: [lathe([[0, 0], [0.235, 0], [0.25, 0.02], [0.25, 0.33], [0.23, 0.36], [0, 0.36]])],
    ring: [(() => { const g = new CylinderGeometry(0.255, 0.255, 0.035, 64, 1, true); g.translate(0, 0.035, 0); return g; })()],
    dark: [(() => { const g = new CylinderGeometry(0.2, 0.2, 0.012, 48); g.translate(0, 0.366, 0); return g; })()],
  }, MAT);
  // 2 · сустав J2 (плечо, ось X) — центр в начале координат модуля
  M.j2 = moduleGroup({ shell: [rodX(0.235, 0.46)], cap: [capX(0.2, 0.246, 1), capX(0.2, -0.246, -1)], ring: [ringX(0.24, 0.035, -0.19)] }, MAT);
  // 3 · звено L1 (труба вверх от центра J2)
  M.l1 = moduleGroup({
    alu: [tubeY(0.1, 0.2, 0.2 + L1)],
    dark: [lathe([[0, 0.17], [0.145, 0.17], [0.145, 0.22], [0.1, 0.24], [0, 0.24]]), lathe([[0, 0.16 + L1], [0.1, 0.16 + L1], [0.14, 0.18 + L1], [0.14, 0.23 + L1], [0, 0.23 + L1]])],
    ring: [(() => { const g = new CylinderGeometry(0.15, 0.15, 0.03, 48, 1, true); g.translate(0, 0.205, 0); return g; })()],
  }, MAT);
  // 4 · сустав J3 (локоть, ось X) — его же показываем крупно в сцене «Внутри»
  M.j3 = moduleGroup({ shell: [rodX(0.2, 0.4)], cap: [capX(0.17, 0.216, 1), capX(0.17, -0.216, -1)], ring: [ringX(0.205, 0.03, 0.16)] }, MAT);
  // 5 · звено L2
  M.l2 = moduleGroup({
    alu: [tubeY(0.085, 0.17, 0.17 + L2)],
    dark: [lathe([[0, 0.15], [0.125, 0.15], [0.125, 0.19], [0.085, 0.21], [0, 0.21]]), lathe([[0, 0.13 + L2], [0.085, 0.13 + L2], [0.12, 0.15 + L2], [0.12, 0.2 + L2], [0, 0.2 + L2]])],
    ring: [(() => { const g = new CylinderGeometry(0.13, 0.13, 0.026, 48, 1, true); g.translate(0, 0.18, 0); return g; })()],
  }, MAT);
  // 6 · запястье (ось X + вращение кисти)
  M.wrist = moduleGroup({
    shell: [rodX(0.14, 0.28), (() => { const g = lathe([[0, 0.12], [0.11, 0.12], [0.11, 0.27], [0.1, 0.285], [0, 0.285]], 48); return g; })()],
    cap: [capX(0.12, 0.156, 1, 48), capX(0.12, -0.156, -1, 48)],
    ring: [ringX(0.145, 0.024, -0.1)],
  }, MAT);
  // 7 · захват (ладонь + два пальца с накладками)
  M.grip = moduleGroup({
    dark: [(() => { const g = new BoxGeometry(0.26, 0.07, 0.14); g.translate(0, 0.035, 0); return g; })(),
      ...[-1, 1].map((s) => { const g = new BoxGeometry(0.034, 0.17, 0.08); g.translate(s * 0.09, 0.155, 0); return g; })],
    ring: [...[-1, 1].map((s) => { const g = new BoxGeometry(0.012, 0.09, 0.066); g.translate(s * 0.07, 0.19, 0); return g; })],
    alu: [(() => { const g = new CylinderGeometry(0.1, 0.1, 0.02, 40); g.translate(0, -0.005, 0); return g; })()],
  }, MAT);
  return M;
}

// начинка сустава J3 (видна только в сцене «Внутри»): вдоль оси X
function buildInternals(MAT) {
  const gear = new Shape();
  const teeth = 72, rOut = 0.155, rIn = 0.147;
  for (let i = 0; i <= teeth * 2; i++) {
    const a = (i / (teeth * 2)) * Math.PI * 2; const r = i % 2 ? rIn : rOut;
    if (i === 0) gear.moveTo(Math.cos(a) * r, Math.sin(a) * r); else gear.lineTo(Math.cos(a) * r, Math.sin(a) * r);
  }
  const hole = new Shape(); hole.absarc(0, 0, 0.118, 0, Math.PI * 2, true); gear.holes.push(hole);
  const gearG = new ExtrudeGeometry(gear, { depth: 0.05, bevelEnabled: false, curveSegments: 4 });
  gearG.rotateY(Math.PI / 2); gearG.translate(-0.02, 0, 0);
  const coil = [];
  for (let i = 0; i < 18; i++) { const g = new BoxGeometry(0.12, 0.022, 0.03); const a = (i / 18) * Math.PI * 2; g.translate(0.07, Math.cos(a) * 0.1, Math.sin(a) * 0.1); coil.push(g); }
  const slots = [];
  for (let i = 0; i < 64; i++) { const g = new BoxGeometry(0.006, 0.018, 0.006); const a = (i / 64) * Math.PI * 2; g.translate(-0.115, Math.cos(a) * 0.118, Math.sin(a) * 0.118); slots.push(g); }
  return moduleGroup({
    copper: [discX(0.118, 0.13, 0.07, 48), ...coil],                      // статор мотора с обмотками
    steel: [gearG, discX(0.028, 0.44, 0, 24), (() => { const g = new TorusGeometry(0.168, 0.012, 12, 64); g.rotateY(Math.PI / 2); g.translate(-0.075, 0, 0); return g; })()],
    dark: [(() => { const g = new CylinderGeometry(0.11, 0.11, 0.028, 64); g.scale(1, 1, 0.82); g.rotateZ(Math.PI / 2); g.translate(-0.005, 0, 0); return g; })()], // волновой генератор (эллипс)
    pcb: [discX(0.13, 0.012, -0.13, 64)],
    ring: [...slots],                                                     // метки энкодера
  }, MAT);
}

// ---------- студия для PMREM (v2): тёмная комната + светящиеся панели = блики «предметной съёмки» на лаке и металле
function studioScene() {
  const s = new Scene();
  const room = new Mesh(new SphereGeometry(40, 32, 16), new ShaderMaterial({
    side: BackSide, depthWrite: false,
    vertexShader: 'varying vec3 vD; void main() { vD = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: 'varying vec3 vD; void main() { float y = vD.y;' +
      ' vec3 c = y < 0.0 ? mix(vec3(0.05, 0.05, 0.055), vec3(0.006), smoothstep(0.0, 0.25, -y))' +     // пол темнее горизонта
      ' : mix(vec3(0.06, 0.062, 0.07), vec3(0.018, 0.019, 0.023), smoothstep(0.0, 0.6, y));' +
      ' gl_FragColor = vec4(c, 1.0); }',
  }));
  s.add(room);
  const quad = new PlaneGeometry(1, 1);
  const lamp = (w, h, x, y, z, color, k) => {
    // только излучение (как RoomEnvironment three: MeshLambertMaterial emissive, #31348)
    const m = new Mesh(quad, new MeshLambertMaterial({ color: 0x000000, emissive: new Color(color), emissiveIntensity: k, side: DoubleSide }));
    m.scale.set(w, h, 1); m.position.set(x, y, z); m.lookAt(0, 1.2, 0); s.add(m);
  };
  lamp(8, 8, -2.5, 12, 3, '#fdfdff', 5);        // верхний софтбокс — широкий мягкий блик сверху (нейтральный: белый не теплеет)
  lamp(1.1, 9, -9, 4, 2, '#ffffff', 8);          // полоса слева — длинный блик вдоль труб и корпусов
  lamp(1.1, 9, 8.5, 4, -3.5, '#dce6ff', 6);      // полоса справа-сзади — холодный контровой
  lamp(12, 5, 1, 2.5, 13, '#ffffff', 1.6);       // фронтальная заливка — белый не уходит в серое, крышки не чёрные
  lamp(7, 6, 8, 3.5, 8, '#ffffff', 2.4);         // большой софтбокс со стороны камеры — «белый остаётся белым» (как отражатель в съёмке)
  lamp(4, 1.4, 6, 0.4, 6, '#ff6d2e', 0.6);       // тёплый отражатель низко справа — фирменный цвет в отражениях металла (слабо: не красит белый)
  return s;
}

// ---------- фон (v2): экранный треугольник — градиент, свечение за объектом, тёплое пятно у пола, виньетка, дизеринг
function backdrop() {
  const g = new BufferGeometry();
  g.setAttribute('position', new Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
  const m = new Mesh(g, new ShaderMaterial({
    depthTest: false, depthWrite: false, toneMapped: false,
    uniforms: {
      uGlow: { value: new Vector2(0.64, 0.55) }, uAspect: { value: 1.6 }, uR: { value: 0.5 },
      uTop: { value: new Color('#111317') }, uBot: { value: new Color('#08090b') },
      uHalo: { value: new Color('#1d2129') }, uWarm: { value: new Color('#22160f') },
    },
    vertexShader: 'varying vec2 vUv; void main() { vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 1.0, 1.0); }',
    fragmentShader: `
      uniform vec2 uGlow; uniform float uAspect, uR; uniform vec3 uTop, uBot, uHalo, uWarm; varying vec2 vUv;
      float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
      void main() {
        vec3 c = mix(uBot, uTop, smoothstep(0.0, 1.0, vUv.y));
        vec2 d = (vUv - uGlow) * vec2(uAspect, 1.0);
        c += uHalo * exp(-dot(d, d) / (uR * uR));
        vec2 w = d + vec2(0.0, 0.42);
        c += uWarm * exp(-dot(w, w) / (0.35 * uR * uR));
        vec2 v = vUv - 0.5; c *= 1.0 - 0.7 * dot(v, v);
        gl_FragColor = vec4(c, 1.0);
        #include <colorspace_fragment>
        gl_FragColor.rgb += (hash(gl_FragCoord.xy) - 0.5) / 255.0;
      }`,
  }));
  m.frustumCulled = false; m.renderOrder = -10;
  return m;
}

// ---------- пол-циклорама (v2): освещённый пол с тенью, альфа — радиальное затухание в фон (G-канал alphaMap, рисуем непрозрачным серым)
function floorMesh(hq) {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const x = c.getContext('2d'); const gr = x.createRadialGradient(128, 128, 0, 128, 128, 128);
  gr.addColorStop(0, '#ffffff'); gr.addColorStop(0.3, '#b4b4b4'); gr.addColorStop(0.62, '#383838'); gr.addColorStop(1, '#000000');
  x.fillStyle = gr; x.fillRect(0, 0, 256, 256);
  const m = new Mesh(new PlaneGeometry(7, 7), new MeshStandardMaterial({ color: '#101215', roughness: 0.86, metalness: 0,
    transparent: true, alphaMap: new CanvasTexture(c), depthWrite: false }));
  m.rotation.x = -Math.PI / 2; m.position.y = -0.001; m.receiveShadow = hq; m.renderOrder = -6;
  return m;
}

// контактная тень под основанием: радиальный градиент на плоскости (затенение там, куда не дотягивается карта теней)
function contactShadow() {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const x = c.getContext('2d'); const gr = x.createRadialGradient(64, 64, 4, 64, 64, 64);
  gr.addColorStop(0, 'rgba(0,0,0,0.6)'); gr.addColorStop(0.5, 'rgba(0,0,0,0.22)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  x.fillStyle = gr; x.fillRect(0, 0, 128, 128);
  const m = new Mesh(new PlaneGeometry(1.7, 1.7), new MeshBasicMaterial({ map: new CanvasTexture(c), transparent: true, depthWrite: false }));
  m.rotation.x = -Math.PI / 2; m.position.y = 0.002; m.renderOrder = -5;
  return m;
}

// ---------- позы суставов (рад): рабочая (hero), прямая (разборка)
const POSE_WORK = { j1: -0.62, j2: 0.42, j3: -1.95, wr: -0.72, roll: 0.35 };
const POSE_REST = { j1: 0, j2: 0, j3: 0, wr: 0, roll: 0 };
const POSE_FIRST = { j1: -1.15, j2: 0.5, j3: -1.85, wr: -0.85, roll: 0.3 };   // «первое движение» после сборки: плоскость изгиба боком к камере
const blendPose = (a, b, t) => Object.fromEntries(Object.keys(a).map((k) => [k, lerp(a[k], b[k], t)]));

// разнесение модулей (мировые смещения при прямой позе) и небольшой разворот — «сборочный чертёж»
const ORDER = ['base', 'j1', 'j2', 'l1', 'j3', 'l2', 'wrist', 'grip'];
const EXPLODE = {   // [dx, dy, dz, наклон] — слева-справа поочерёдно, вверх понемногу: читается как сборочный чертёж
  // v2: основание стоит на полу (в v1 уходило на 10 см вниз — с полом-циклорамой это «проваливание»)
  base: [0, 0, 0, 0], j1: [-0.55, 0.06, 0.12, 0.12], j2: [0.62, 0.16, 0.08, -0.16], l1: [-0.7, 0.26, -0.06, 0.1],
  j3: [0.72, 0.36, 0.12, -0.14], l2: [-0.64, 0.46, 0.08, 0.12], wrist: [0.6, 0.56, -0.08, -0.18], grip: [-0.26, 0.7, 0.14, 0.14],
};

export function createScene(canvas, opts = {}) {
  const dprMax = opts.dprMax || 1.5;
  const hq = opts.quality !== 'low';
  // контекст можно создать заранее (main.js проверяет WebGL2 на том же холсте: без второго контекста и без ошибки three в консоли)
  const renderer = new WebGLRenderer({ canvas, context: opts.context || undefined, antialias: true, alpha: true, powerPreference: 'high-performance', preserveDrawingBuffer: !!opts.preserve });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, dprMax));
  // тон-маппинг Khronos PBR Neutral: фирменный оранжевый и белый не выцветают (AgX при 1,12–1,5 гасил оранжевый, белый — в серый;
  // ACES краснит оранжевый) — сравнение J/04 `out/tone-compare.jpg`
  renderer.toneMapping = TONE[opts.tone] || NeutralToneMapping;
  // экспозиция 1,22 и окружение 1,8 — белый пластик светел как у v1 (медиана L 221 против 218, белая точка 247 против 238, R−B 2,8)
  // при тенях и отражениях; было 1,08 / 1,3 — медиана 183–189 (J/04 white_check, out/white-compare.jpg)
  renderer.toneMappingExposure = opts.exposure || 1.22;
  renderer.outputColorSpace = SRGBColorSpace;
  renderer.localClippingEnabled = true;
  renderer.shadowMap.enabled = hq;
  renderer.shadowMap.type = PCFShadowMap;                               // PCFSoftShadowMap в r186 удалён (предупреждение в консоль)

  const scene = new Scene();
  let envRT = null;                                                      // PMREM студии — в ready (отдельной задачей)
  scene.environmentIntensity = opts.env || 1.8;                          // opts.env / key / rim — ручки опыта J/04 (preview.html)

  const key = new DirectionalLight('#fffaf4', opts.key || (hq ? 2.3 : 2.1));
  key.position.set(-3.2, 6.8, 4.4); key.target.position.set(0, 1.1, 0);
  scene.add(key, key.target);
  if (hq) {
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    const sc = key.shadow.camera; sc.left = -3.2; sc.right = 3.2; sc.top = 3.2; sc.bottom = -3.2; sc.near = 2; sc.far = 16;
    sc.updateProjectionMatrix();
    key.shadow.bias = -0.0004; key.shadow.normalBias = 0.025; key.shadow.radius = 4;
  }
  const rim = new DirectionalLight('#b9c9ff', opts.rim || 2.0); rim.position.set(4.5, 3.2, -5); scene.add(rim);

  const camera = new PerspectiveCamera(30, 1, 0.05, 60);
  const MAT = makeMaterials(hq);
  const M = buildModules(MAT);
  const inner = buildInternals(MAT);
  const bg = backdrop();
  const floor = floorMesh(hq);
  const blob = contactShadow();
  scene.add(bg, floor, blob);

  // кинематика: пустые шарниры; видимые модули лежат в корне и получают мировую матрицу шарнира × разнесение
  const piv = { base: new Object3D(), j1: new Object3D(), j2: new Object3D(), l1: new Object3D(), j3: new Object3D(), l2: new Object3D(), wrist: new Object3D(), grip: new Object3D() };
  piv.j1.position.set(0, 0.34, 0); piv.base.add(piv.j1);
  piv.j2.position.set(0, 0.36 + 0.235, 0); piv.j1.add(piv.j2);
  piv.l1.position.set(0, 0, 0); piv.j2.add(piv.l1);
  piv.j3.position.set(0, 0.2 + L1 + 0.23, 0); piv.l1.add(piv.j3);
  piv.l2.position.set(0, 0, 0); piv.j3.add(piv.l2);
  piv.wrist.position.set(0, 0.17 + L2 + 0.18, 0); piv.l2.add(piv.wrist);
  piv.grip.position.set(0, 0.3, 0); piv.wrist.add(piv.grip);
  const rig = new Group(); rig.add(piv.base); scene.add(rig);
  const RING = {};
  for (const k of ORDER) {
    M[k].matrixAutoUpdate = false; scene.add(M[k]);
    M[k].children.forEach((ch) => { ch.castShadow = hq; ch.receiveShadow = hq; if (ch.userData.key === 'ring') RING[k] = ch.material; });
  }

  // сустав крупно для сцены «Внутри»: копия J3 с материалами скана + начинка
  const big = new Group();
  const j3scan = new Group();
  M.j3.children.forEach((ch) => {
    const m = new Mesh(ch.geometry, scanify(ch.material)); m.castShadow = hq; m.receiveShadow = hq; j3scan.add(m);
    if (ch.userData.key === 'ring') m.material.emissiveIntensity = 0.85;     // кольцо увеличенного сустава горит ровно
  });
  inner.children.forEach((ch) => { ch.castShadow = hq; ch.receiveShadow = hq; });
  const IN = Object.fromEntries(inner.children.map((ch) => [ch.userData.key, ch]));
  big.add(j3scan, inner);
  big.visible = false;
  scene.add(big);

  const tmpM = new Matrix4(), tmpM2 = new Matrix4(), tmpR = new Matrix4(), tmpQ = new Quaternion(), tmpE = new Euler(), tmpV = new Vector3(), tmpC = new Vector3(), one = new Vector3(1, 1, 1);
  const noRot = new Quaternion();
  const state = { phase: 'story', t: 0, px: 0, py: 0, w: 1, h: 1, mobile: false, instant: false };
  const cur = { t: 0, px: 0, py: 0 };
  // инерция висящих модулей: пружина угла крена от скорости разноса (ζ 0,8, ω 14 рад/с → 99 % за ≈ 0,41 с)
  const SP = Object.fromEntries(ORDER.map((k) => [k, { x: 0, v: 0, prev: null }]));
  const SPW = 14, SPZ = 0.8;
  let raf = 0, alive = true, introStart = 0, introMs = 1200, introBump = 0;

  function applyPose(p) {
    piv.j1.rotation.y = p.j1; piv.j2.rotation.x = p.j2; piv.j3.rotation.x = p.j3; piv.wrist.rotation.x = p.wr; piv.grip.rotation.y = p.roll;
    rig.updateMatrixWorld(true);
  }

  // дуга и высота камеры; glow — точка «за объектом» для фона (экранные координаты 0..1)
  function setGlow(x, y, z, r) {
    tmpV.set(x, y, z).project(camera);
    bg.material.uniforms.uGlow.value.set(tmpV.x * 0.5 + 0.5, tmpV.y * 0.5 + 0.5);
    bg.material.uniforms.uR.value = r;
  }

  function storyFrame(t, dt, still) {
    // t: 0..1 — первый экран (рабочая поза), 1..2 — сцена «модули»
    const a = clamp(t - 1, 0, 1);
    // доли сцены = станции motion-spec: s1 0,42 (разнесено), s2 0,8 (сборка), s3 0,99 (первое движение); шаг между станциями ≤ 150vh
    const straighten = ease(seg(a, 0.06, 0.2));
    const explode = ease(seg(a, 0.16, 0.34));
    const firstMove = ease(seg(a, 0.88, 1.0));
    let pose = blendPose(POSE_WORK, POSE_REST, straighten);
    if (firstMove > 0) pose = blendPose(POSE_REST, POSE_FIRST, firstMove);
    if (introBump > 0 && a === 0) {                                       // «пробуждение» первого экрана: один раз, 1,2 с, не петля
      pose = { ...pose, j1: pose.j1 + 0.22 * introBump, wr: pose.wr - 0.3 * introBump, roll: pose.roll + 0.9 * introBump };
    }
    applyPose(pose);
    const power = 1 - explode;                                            // до разборки кольца горят; разобран — погасли
    let quiet = 0;
    ORDER.forEach((k, i) => {
      // сборка снизу вверх: модуль i садится на отрезке [0,52 + 0,04 i; +0,12]: подход → зависание над гнездом → дожим → щелчок поворота
      const s0 = 0.52 + i * 0.04;
      const u = a >= 0.52 ? seg(a, s0, s0 + 0.12) : 0;
      const back = ease(u);
      const out = a < 0.52 ? explode : explode * (1 - back);
      const hover = a >= 0.52 && i > 0 ? 0.07 * bump(u, 0.2, 0.62, 0.86) : 0;          // 7 см над гнездом, затем дожим вниз
      const twist = a >= 0.52 && i > 0 ? seg(u, 0, 0.3) * (1 - snap(seg(u, 0.72, 1))) : 0; // 90° → 0 с перелётом ≈ 10°
      const [ex, ey, ez, er] = EXPLODE[k];
      // инерция: цель крена — от скорости разноса (рад), знак — сторона разноса; пружина догоняет цель
      const sp = SP[k];
      if (still || sp.prev === null) { sp.x = 0; sp.v = 0; }
      else {
        const vOut = (out - sp.prev) / dt;
        const target = clamp(-0.035 * vOut * Math.sign(ex || 1) * (1 + 0.6 * ey), -0.1, 0.1);   // ≤ 5,7° крена
        sp.v += (SPW * SPW * (target - sp.x) - 2 * SPZ * SPW * sp.v) * dt;
        sp.x += sp.v * dt;
      }
      sp.prev = out;
      quiet = Math.max(quiet, Math.abs(sp.x), Math.abs(sp.v) * 0.1);
      tmpE.set(er * out * 0.5, er * out + twist * Math.PI / 2, er * out * 0.3);
      tmpQ.setFromEuler(tmpE);
      tmpM.compose(tmpV.set(ex * out, ey * out + hover, ez * out), noRot, one);
      M[k].matrix.copy(tmpM).multiply(piv[k].matrixWorld).multiply(tmpR.makeRotationFromQuaternion(tmpQ));
      if (Math.abs(sp.x) > 1e-4) {                                        // крен вокруг центра модуля (мировая ось Z)
        tmpC.copy(M[k].userData.c).applyMatrix4(M[k].matrix);
        tmpM.makeTranslation(tmpC.x, tmpC.y, tmpC.z).multiply(tmpR.makeRotationZ(sp.x)).multiply(tmpM2.makeTranslation(-tmpC.x, -tmpC.y, -tmpC.z));
        M[k].matrix.premultiply(tmpM);
      }
      M[k].matrixWorldNeedsUpdate = true;
      M[k].visible = true;
      // кольцо-замок: горит при питании, гаснет при разборке, при фиксации — вспышка и ровный свет
      const lock = i === 0 ? seg(a, 0.52, 0.56) : seg(u, 0.86, 0.94);
      const lit = a < 0.52 ? power : lock;
      RING[k].emissiveIntensity = 0.85 * lit + 1.6 * (a >= 0.52 ? bump(u, 0.84, 0.92, 1.0) : 0) + 0.9 * introBump;
    });
    floor.visible = true; blob.visible = true; big.visible = false;
    // камера: первый экран — рука справа (сдвиг кадра), затем к центру и дальше, чтобы вошла разобранная рука;
    // v2 — дуга на станциях: разнос — обходим сбоку, сборка — ниже («снизу вверх»), первое движение — наезд
    const hTo = ease(clamp(t, 0, 1));
    const far = Math.max(explode * (1 - ease(seg(a, 0.52, 0.9))), straighten * 0.55 * (1 - firstMove));
    const arc = 0.24 * bump(a, 0.16, 0.42, 0.66) - 0.1 * bump(a, 0.6, 0.8, 0.96);
    const low = bump(a, 0.58, 0.8, 0.98);
    const push = ease(seg(a, 0.9, 1.0));
    const dist = lerp(5.9, 10.2, far) * (1 - 0.08 * push) * (state.mobile ? 1.3 : 1);   // v1: 10,9 — модули разноса мелкие
    const yaw = lerp(0.62, 0.38, hTo) + lerp(0, -0.18, a) + arc + cur.px * 0.06;
    const tgtY = lerp(1.28, 2.3, far);
    camera.position.set(Math.sin(yaw) * dist, tgtY + lerp(0.85, 0.45, far) - 0.5 * low + cur.py * 0.12, Math.cos(yaw) * dist);
    camera.lookAt(0.05, tgtY, 0);
    const shift = state.mobile ? 0 : lerp(-0.2, -0.12, hTo);                // доля ширины кадра: рука правее текста и панелей шагов
    const shiftY = state.mobile ? lerp(0.18, 0.1, hTo) : 0;
    camera.setViewOffset(state.w, state.h, shift * state.w, shiftY * state.h, state.w, state.h);
    camera.updateMatrixWorld();
    setGlow(0.05, tgtY * 0.95, 0, lerp(0.5, 0.62, far));
    return quiet;
  }

  function scanFrame(t) {
    ORDER.forEach((k) => { M[k].visible = false; });
    floor.visible = false; blob.visible = false; big.visible = true;
    // станции motion-spec: s4 0,3 (скан на середине — медь видна), s5 0,64 (корпус снят), s6 0,95 (слои разведены)
    const sweep = ease(seg(t, 0.06, 0.52));
    const spread = ease(seg(t, 0.6, 0.92));
    // скан в системе сустава: плоскость ⊥ локальной Y идёт сверху вниз (видимо y ≤ c): верхняя половина корпуса снимается
    const c = lerp(0.26, -0.015, sweep);
    inner.children.forEach((m) => {                                       // слои начинки чуть расходятся по оси в конце
      const k = m.userData.key; const d = { copper: 0.07, steel: 0, dark: -0.03, pcb: -0.07, ring: -0.07 }[k] || 0;
      m.position.x = d * spread * 0.9;
    });
    // v2: привод «живой» от прокрутки — генератор волн (эллипс) 3 оборота на сцену, колесо и энкодер — медленно навстречу
    const spin = t * Math.PI * 6;
    IN.dark.rotation.x = spin; IN.steel.rotation.x = -spin / 12; IN.ring.rotation.x = -spin / 12;
    big.scale.setScalar(state.mobile ? 1.9 : 2.45);
    big.rotation.set(0.42, lerp(-0.2, -0.42, t) + cur.px * 0.05, 0.04);
    big.position.set(0, 1.2, 0);
    big.updateMatrixWorld(true);
    scanLocal.constant = c;
    scanPlane.copy(scanLocal).applyMatrix4(big.matrixWorld);
    scanUniforms.uScanN.value.copy(scanPlane.normal); scanUniforms.uScanC.value = scanPlane.constant;
    const dist = (state.mobile ? 5.0 : 4.3) * (1 - 0.05 * bump(t, 0.5, 0.8, 1.01));   // v2: лёгкий наезд на слоях
    const yaw = 0.18 + 0.1 * bump(t, 0.1, 0.45, 0.8);                      // v2: полуоборот камеры навстречу срезу
    camera.position.set(Math.sin(yaw) * dist, 1.62 + cur.py * 0.08, Math.cos(yaw) * dist);
    camera.lookAt(0, 1.2, 0);
    const shift = state.mobile ? 0 : 0.13;                                // сустав левее, текст шагов — справа
    camera.setViewOffset(state.w, state.h, shift * state.w, state.mobile ? 0.12 * state.h : 0, state.w, state.h);
    camera.updateMatrixWorld();
    setGlow(0, 1.2, 0, 0.55);
  }
  let lastFrame = 0, lastInput = 0;
  function frame(now) {
    raf = 0;
    if (!alive || !isReady) return;                                      // до готовности не рисуем: иначе синхронная компиляция без окружения
    // сглаживание по времени (τ 90 мс, после 0,28 с без ввода — 30 мс): хвост ≤ 0,45 с после последнего ввода при любом FPS,
    // дальше кадры не рисуются — рендер по требованию (EG-A11Y-09/16: 0 вызовов в покое; motion_check 0.1.2 снимает на +0,5 с)
    now = now || performance.now();
    const dt = Math.min(0.05, Math.max(0.001, (now - (lastFrame || now - 16)) / 1000)); lastFrame = now;
    const since = now - lastInput;
    const late = since > 280;
    const k = state.instant ? 1 : 1 - Math.exp(-dt / (late ? 0.03 : 0.09));
    const kp = state.instant ? 1 : 1 - Math.exp(-dt / (late ? 0.04 : 0.16));
    cur.t += (state.t - cur.t) * k; cur.px += (state.px - cur.px) * kp; cur.py += (state.py - cur.py) * kp;
    const cut = since > 450;
    let settled = (Math.abs(state.t - cur.t) < 0.002 && Math.abs(state.px - cur.px) < 0.004 && Math.abs(state.py - cur.py) < 0.004) || cut;
    if (settled) { cur.t = state.t; cur.px = state.px; cur.py = state.py; }
    if (introStart) {
      const u = (performance.now() - introStart) / introMs;
      if (u >= 1) { introStart = 0; introBump = 0; } else { introBump = Math.sin(Math.PI * ease(u)); settled = false; }
    }
    if (state.phase === 'scan') { scanFrame(cur.t); }
    else {
      scanPlane.constant = 10;
      const quiet = storyFrame(cur.t, dt, state.instant || cut);
      if (quiet > 0.002 && !cut) settled = false;                         // пружины инерции ещё не легли
    }
    renderer.render(scene, camera);
    state.instant = false;
    if (settled) lastFrame = 0; else raf = requestAnimationFrame(frame);
  }
  const kick = () => { if (!raf && alive) raf = requestAnimationFrame(frame); };

  function resize(w, h, mobile) {
    state.w = w; state.h = h; state.mobile = !!mobile;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
    bg.material.uniforms.uAspect.value = w / h;
    state.instant = true; kick();
  }

  // Готовность без одной длинной задачи (v2: холодная компиляция Physical + PMREM давала 750 мс на десктопе, J/04 shots):
  // задача 1 — геометрия и материалы (выше), задача 2 — PMREM студии, задача 3 — программы сюжета через compileAsync
  // (KHR_parallel_shader_compile: сборка в процессе GPU, главный поток не ждёт), программы скана — в простое после первого кадра.
  const nextTask = () => new Promise((r) => setTimeout(r, 0));
  const par = renderer.extensions.has('KHR_parallel_shader_compile');
  let isReady = false;
  const ready = (async () => {
    await nextTask();
    if (!alive) return false;                                            // успели разрушить (переключили в reduce)
    const pmrem = new PMREMGenerator(renderer);
    const studio = studioScene();
    envRT = pmrem.fromScene(studio, 0.02);
    scene.environment = envRT.texture;
    pmrem.dispose();
    studio.traverse((o) => { if (o.isMesh) { o.geometry.dispose(); o.material.dispose(); } });
    await nextTask();
    if (!alive) return false;
    // compileAsync без расширения пишет в консоль «KHR_parallel_shader_compile extension not supported» (SwiftShader, J/05) —
    // проверяем через has() (без предупреждения) и тогда компилируем синхронно, но всё равно отдельной задачей
    if (par) await renderer.compileAsync(scene, camera); else renderer.compile(scene, camera);
    if (!alive) return false;
    isReady = true;
    const idle = window.requestIdleCallback || ((f) => setTimeout(f, 300));
    idle(() => {
      if (!alive) return; big.visible = true;
      if (par) renderer.compileAsync(scene, camera); else renderer.compile(scene, camera);
      big.visible = false;
    }, { timeout: 2000 });
    return true;
  })();

  return {
    renderer,
    ready,
    isReady: () => isReady,
    resize,
    set(phase, t, instant) {
      if (phase !== state.phase) { state.phase = phase; cur.t = t; state.instant = true; }
      state.t = t; if (instant) state.instant = true; lastInput = performance.now(); kick();
    },
    pointer(x, y) { state.px = x; state.py = y; lastInput = performance.now(); kick(); },
    intro(ms = 1200) { introMs = ms; introStart = performance.now(); kick(); },
    renderNow() { cur.t = state.t; cur.px = state.px; cur.py = state.py; state.instant = true; if (raf) { cancelAnimationFrame(raf); raf = 0; } frame(); },
    stop() { if (raf) cancelAnimationFrame(raf); raf = 0; },
    dispose() {
      alive = false; if (raf) cancelAnimationFrame(raf);
      const mats = new Set();
      scene.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) mats.add(o.material); });
      mats.forEach((m) => { if (m.map) m.map.dispose(); if (m.alphaMap) m.alphaMap.dispose(); m.dispose(); });
      if (envRT) envRT.dispose();
      renderer.dispose(); renderer.forceContextLoss();
    },
    stats: () => ({ calls: renderer.info.render.calls, tris: renderer.info.render.triangles, programs: renderer.info.programs ? renderer.info.programs.length : null }),
  };
}
