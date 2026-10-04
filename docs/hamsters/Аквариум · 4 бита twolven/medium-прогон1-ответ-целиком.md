

# 🐠 3D Аквариум — полный код

Сохраните как `aquarium.html` и откройте в браузере. Всё в одном файле: Three.js подгружается с CDN.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; }
  body { font-family: 'Segoe UI', Roboto, system-ui, sans-serif; background: #04122b; }
  canvas { display: block; }

  /* Glass UI — полупрозрачные панели */
  .panel {
    position: fixed; z-index: 10;
    background: rgba(8, 30, 58, 0.55);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(130, 205, 255, 0.28);
    border-radius: 16px;
    padding: 16px 18px;
    color: #dcedff;
    box-shadow: 0 10px 34px rgba(0, 0, 0, 0.4);
  }

  #infoPanel { top: 18px; left: 18px; max-width: 280px; }
  #infoPanel h1 {
    font-size: 1.35rem; letter-spacing: 0.5px; margin-bottom: 10px;
    background: linear-gradient(92deg, #8fd9ff 10%, #ffe08a 90%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  #infoPanel p { font-size: 0.83rem; line-height: 1.6; opacity: 0.93; }

  .btns { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 14px; }
  .btns button {
    cursor: pointer; border: none; border-radius: 10px;
    padding: 9px 13px; font-size: 0.82rem; font-weight: 700;
    color: #052a44;
    background: linear-gradient(135deg, #9adcff 0%, #ffe28f 100%);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.32);
    transition: transform .16s ease, box-shadow .16s ease, filter .16s ease;
  }
  .btns button:hover {
    transform: translateY(-2px);
    filter: brightness(1.09);
    box-shadow: 0 7px 18px rgba(90, 190, 255, 0.5);
  }
  .btns button:active { transform: translateY(0) scale(.97); }

  #statsPanel { top: 18px; right: 18px; min-width: 148px; text-align: right; }
  #statsPanel .row { font-size: 0.92rem; margin-bottom: 5px; }
  #fishCount { color: #ffd76e; font-weight: 700; }
  #fps { color: #7fd4ff; }

  @media (max-width: 680px) {
    #infoPanel { max-width: 215px; padding: 12px 13px; }
    #infoPanel p { display: none; }
    #statsPanel { min-width: 120px; padding: 12px; }
  }
</style>
</head>
<body>

<!-- Информационная панель -->
<div class="panel" id="infoPanel">
  <h1>🐠 3D Аквариум</h1>
  <p>🖱️ ЛКМ + движение — вращение камеры</p>
  <p>🖱️ ПКМ + движение — панорама</p>
  <p>🖱️ Колесо — зум</p>
  <p>🍽️ Клик по воде — бросить корм</p>
  <div class="btns">
    <button id="btnFish">➕ Рыбка</button>
    <button id="btnBubbles">💧 Пузыри</button>
    <button id="btnLight">💡 Свет</button>
  </div>
</div>

<!-- Статистика -->
<div class="panel" id="statsPanel">
  <div class="row" id="fishCount">🐟 Рыбок: 15</div>
  <div class="row" id="fps">— FPS</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
'use strict';

/* ============================================================
   УТИЛИТЫ
============================================================ */
const rand = (a, b) => a + Math.random() * (b - a);
const pick = arr => arr[(Math.random() * arr.length) | 0];

/* ============================================================
   СЦЕНА, ФОН, ТУМАН
============================================================ */
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x082540, 0.011); // имитация водной среды

// Градиентный фон: тёмно-синий → синий
(function () {
  const cv = document.createElement('canvas');
  cv.width = 2; cv.height = 512;
  const cx = cv.getContext('2d');
  const gr = cx.createLinearGradient(0, 0, 0, 512);
  gr.addColorStop(0, '#030f24');
  gr.addColorStop(0.55, '#0a2d52');
  gr.addColorStop(1, '#11406b');
  cx.fillStyle = gr;
  cx.fillRect(0, 0, 2, 512);
  const tex = new THREE.CanvasTexture(cv);
  tex.encoding = THREE.sRGBEncoding;
  scene.background = tex;
})();

/* ============================================================
   КАМЕРА
============================================================ */
const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 400);
camera.position.set(26, 13, 40);

/* ============================================================
   РЕНДЕРЕР
============================================================ */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // мягкие тени
document.body.appendChild(renderer.domElement);

/* ============================================================
   OrbitControls
============================================================ */
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.target.set(0, 0, 0);

/* ============================================================
   ОСВЕЩЕНИЕ
============================================================ */
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sun = new THREE.DirectionalLight(0xfff1d6, 1.15);
sun.position.set(28, 42, 18);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -26;
sun.shadow.camera.right = 26;
sun.shadow.camera.top = 26;
sun.shadow.camera.bottom = -26;
sun.shadow.camera.near = 5;
sun.shadow.camera.far = 110;
sun.shadow.bias = -0.0005;
scene.add(sun);

// Подводное освещение
const pLight1 = new THREE.PointLight(0x3fd0ff, 0.75, 70);
pLight1.position.set(-14, 6, 9);
const pLight2 = new THREE.PointLight(0x3355ff, 0.75, 70);
pLight2.position.set(14, 9, -9);
scene.add(pLight1, pLight2);

/* ============================================================
   АКВАРИУМ: стекло, рамка, песок
============================================================ */
const TANK = { w: 36, h: 24, d: 20 };
const BOUNDS = { x: 16.6, y: 10.6, z: 8.6 }; // границы для рыбок
const FLOOR_Y = -11.7;

const glass = new THREE.Mesh(
  new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d),
  new THREE.MeshPhysicalMaterial({
    color: 0xbfe6ff,
    metalness: 0,
    roughness: 0.06,
    transmission: 0.95,       // преломление
    transparent: true,
    opacity: 0.32,
    side: THREE.DoubleSide,
    depthWrite: false
  })
);
scene.add(glass);

// Видимая рамка (wireframe edges)
const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(glass.geometry),
  new THREE.LineBasicMaterial({ color: 0x9fd8ff, transparent: true, opacity: 0.9 })
);
scene.add(edges);

// Песчаное дно с procedural неровностями
(function () {
  const g = new THREE.PlaneGeometry(TANK.w - 1, TANK.d - 1, 42, 26);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i);
    p.setZ(i,
      Math.sin(x * 0.55) * Math.cos(y * 0.65) * 0.28 +
      Math.sin(x * 1.7 + y * 1.3) * 0.09
    );
  }
  g.computeVertexNormals();
  const sand = new THREE.Mesh(g,
    new THREE.MeshStandardMaterial({ color: 0xd8bf8b, roughness: 1 })
  );
  sand.rotation.x = -Math.PI / 2;
  sand.position.y = FLOOR_Y;
  sand.receiveShadow = true;
  scene.add(sand);
})();

/* ============================================================
   ДЕКОРАТИВНЫЕ КАМНИ (8 шт., деформированные додекаэдры)
============================================================ */
(function () {
  const geo = new THREE.DodecahedronGeometry(1, 0);
  const p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    // Детерминированная деформация — без трещин между гранями
    const s = 1 + (Math.sin(x * 3.1) + Math.cos(y * 2.7) + Math.sin(z * 3.3)) * 0.14;
    p.setXYZ(i, x * s, y * s, z * s);
  }
  geo.computeVertexNormals();

  const palette = [0x5c6770, 0x6d6a5f, 0x57606b, 0x71767a, 0x666f66];
  for (let i = 0; i < 8; i++) {
    const m = new THREE.Mesh(geo,
      new THREE.MeshStandardMaterial({ color: pick(palette), roughness: 0.95 })
    );
    const s = rand(0.9, 2.0);
    m.scale.set(s, s * rand(0.7, 1.1), s);
    m.position.set(rand(-15.5, 15.5), FLOOR_Y + s * 0.45, rand(-7.8, 7.8));
    m.rotation.set(rand(0, Math.PI), rand(0, Math.PI), rand(0, Math.PI));
    m.castShadow = m.receiveShadow = true;
    scene.add(m);
  }
})();

/* ============================================================
   ВОДОРОСЛИ (12 кустов: TubeGeometry + CatmullRomCurve3)
============================================================ */
const weeds = [];
(function () {
  for (let i = 0; i < 12; i++) {
    const h = rand(2.6, 6.0); // случайная высота
    const base = new THREE.Vector3(rand(-15.5, 15.5), FLOOR_Y + 0.1, rand(-7.8, 7.8));

    // Кривая стеbla, начинающаяся из точки (0,0,0)
    const pts = [new THREE.Vector3(0, 0, 0)];
    const segs = 7;
    const drift = new THREE.Vector3(0, 0, 0);
    for (let s = 1; s <= segs; s++) {
      drift.x += rand(-0.5, 0.5);
      drift.z += rand(-0.5, 0.5);
      pts.push(new THREE.Vector3(drift.x, (h / segs) * s, drift.z));
    }
    const curve = new THREE.CatmullRomCurve3(pts);
    const tube = new THREE.TubeGeometry(curve, 18, rand(0.10, 0.22), 6, false);

    // Случайный зелёный оттенок
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(rand(0.28, 0.42), 0.65, rand(0.22, 0.4)),
      roughness: 0.85,
      side: THREE.DoubleSide
    });

    // Пивот в точке роста — для покачивания
    const pivot = new THREE.Group();
    pivot.position.copy(base);
    const mesh = new THREE.Mesh(tube, mat);
    mesh.castShadow = true;
    pivot.add(mesh);
    scene.add(pivot);

    weeds.push({ pivot, phase: Math.random() * Math.PI * 2, amp: rand(0.03, 0.07) });
  }
})();

/* ============================================================
   СИСТЕМА ПУЗЫРЕЙ (30 на старте)
============================================================ */
const bubbles = [];
const bubbleGeo = new THREE.SphereGeometry(1, 10, 8);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xd8f2ff,
  metalness: 0,
  roughness: 0.08,
  transmission: 0.55,
  transparent: true,
  opacity: 0.5
});

function addBubble() {
  const m = new THREE.Mesh(bubbleGeo, bubbleMat);
  m.scale.setScalar(rand(0.12, 0.34));
  m.position.set(rand(-16.4, 16.4), rand(-11, 10.5), rand(-8.4, 8.4));
  scene.add(m);
  bubbles.push({
    mesh: m,
    speed: rand(1.3, 3.2),
    phase: Math.random() * Math.PI * 2
  });
}
for (let i = 0; i < 30; i++) addBubble();

function updateBubbles(dt, t) {
  for (let i = 0; i < bubbles.length; i++) {
    const b = bubbles[i];
    const p = b.mesh.position;
    // Вверх с покачиванием (sin/cos)
    p.y += b.speed * dt;
    p.x += Math.sin(t * 1.6 + b.phase) * dt * 0.5;
    p.z += Math.cos(t * 1.2 + b.phase) * dt * 0.5;
    // Сброс при достижении поверхности
    if (p.y > 11.2) {
      p.y = -11.2;
      p.x = rand(-16.4, 16.4);
      p.z = rand(-8.4, 8.4);
      b.speed = rand(1.3, 3.2);
      b.phase = Math.random() * Math.PI * 2;
    }
  }
}

/* ============================================================
   РЫБКИ: общие геометрии, цветовые схемы, создание
============================================================ */
const SCHEMES = [
  { name: 'Оранжевая',     body: 0xff8c1a, fin: 0xffb35c },
  { name: 'Синяя',           body: 0x2e7dff, fin: 0x7fb2ff },
  { name: 'Жёлто-красная',   body: 0xffd23f, fin: 0xff5522 },
  { name: 'Фиолетовая',      body: 0x8a4fd8, fin: 0xb98cff },
  { name: 'Красная',         body: 0xe03a2f, fin: 0xff7a6b },
  { name: 'Зелёная',           body: 0x3fae5a, fin: 0x8fe0a0 },
  { name: 'Розовая',             body: 0xf77fb0, fin: 0xffc2dd },
  { name: 'Золотая',             body: 0xf5b942, fin: 0xffe08a }
];

// Общие геометрии (низкополигональные, переиспользуемые)
const SHARED = {
  bodyGeo: (() => { const g = new THREE.SphereGeometry(1, 18, 14); g.scale(0.62, 0.85, 1.5); return g; })(),
  eyeGeo: new THREE.SphereGeometry(0.14, 10, 8),
  pupilGeo: new THREE.SphereGeometry(0.07, 8, 6),
  tailGeo: (() => { const g = new THREE.ConeGeometry(0.5, 1.0, 8); g.rotateX(Math.PI / 2); g.scale(0.35, 1, 1); return g; })(),
  pectGeo: (() => { const g = new THREE.SphereGeometry(0.28, 8, 6); g.scale(0.25, 0.5, 0.9); return g; })(),
  dorsalGeo: (() => { const g = new THREE.ConeGeometry(0.35, 0.5, 8); g.scale(0.3, 1, 1); return g; })(),
  whiteMat: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.25 }),
  blackMat: new THREE.MeshStandardMaterial({ color: 0x101010, roughness: 0.2 })
};

// Материалы по схемам (кэшируются)
const schemeMats = {};
function getSchemeMats(s) {
  if (!schemeMats[s.name]) {
    schemeMats[s.name] = {
      body: new THREE.MeshStandardMaterial({ color: s.body, roughness: 0.45, metalness: 0.12 }),
      fin: new THREE.MeshStandardMaterial({ color: s.fin, roughness: 0.6, transparent: true, opacity: 0.92 })
    };
  }
  return schemeMats[s.name];
}

// Создание детализированной рыбки (голова в +Z)
function createFish(scheme) {
  const mats = getSchemeMats(scheme);
  const g = new THREE.Group();

  // Вытянутое тело
  const body = new THREE.Mesh(SHARED.bodyGeo, mats.body);
  body.castShadow = true;
  g.add(body);

  // Реалистичные глаза с зрачками
  const eL = new THREE.Mesh(SHARED.eyeGeo, SHARED.whiteMat);
  eL.position.set(-0.38, 0.16, 1.02);
  const eR = eL.clone(); eR.position.x = 0.38;
  const pL = new THREE.Mesh(SHARED.pupilGeo, SHARED.blackMat);
  pL.position.set(-0.41, 0.16, 1.11);
  const pR = pL.clone(); pR.position.x = 0.41;
  g.add(eL, eR, pL, pR);

  // Анимируемый хвост: точка вращения на задней части тела
  const tailPivot = new THREE.Group();
  tailPivot.position.set(0, 0, -1.48);
  const tail = new THREE.Mesh(SHARED.tailGeo, mats.fin);
  tail.position.z = -0.5; // узкая часть — у тела
  tailPivot.add(tail);
  g.add(tailPivot);

  // Боковые плавники
  const leftFin = new THREE.Mesh(SHARED.pectGeo, mats.fin);
  leftFin.position.set(-0.5, -0.05, 0.55);
  leftFin.rotation.z = 0.55;
  const rightFin = leftFin.clone();
  rightFin.position.x = 0.5;
  rightFin.rotation.z = -0.55;
  g.add(leftFin, rightFin);

  // Верхний плавник
  const dorsal = new THREE.Mesh(SHARED.dorsalGeo, mats.fin);
  dorsal.position.set(0, 0.72, -0.15);
  g.add(dorsal);

  return { group: g, tailPivot, tail, leftFin, rightFin, dorsal };
}

/* ============================================================
   РОЙ РЫБОК + ИНДИВИДУАЛЬНЫЕ ПАРАМЕТРЫ
============================================================ */
const fishArray = [];

function spawnFish(scheme) {
  scheme = scheme || pick(SCHEMES);
  const f = createFish(scheme);

  f.group.position.set(rand(-13, 13), rand(-8.5, 8.5), rand(-6.5, 6.5));
  f.group.scale.setScalar(rand(0.6, 1.2)); // разнообразие размеров

  f.scheme = scheme;
  f.speed = rand(1.6, 3.2);
  f.velocity = new THREE.Vector3(rand(-1, 1), rand(-0.4, 0.4), rand(-1, 1));
  if (f.velocity.lengthSq() < 0.01) f.velocity.set(1, 0, 0);
  f.velocity.normalize().multiplyScalar(f.speed);

  f.tailSpeed = rand(4.5, 8.5); // разная частота маха
  f.phase = Math.random() * Math.PI * 2;
  f.targetFood = null;
  f.avoidanceRadius = rand(2.6, 3.8);
  f.wanderTimer = rand(1, 4);

  scene.add(f.group);
  fishArray.push(f);
  updateStats();
  return f;
}

// Стартовый состав: 15 разноцветных тропических рыбок
for (let i = 0; i < 15; i++) spawnFish(SCHEMES[i % SCHEMES.length]);

/* ============================================================
   ИИ И ПОВЕДЕНИЕ РЫБОК
============================================================ */
const _lookTarget = new THREE.Vector3();

function updateFish(dt, t) {
  const n = fishArray.length;
  for (let i = 0; i < n; i++) {
    const f = fishArray[i];
    const pos = f.group.position;
    const acc = new THREE.Vector3();

    /* 1) Избегание столкновений: отталкивание от соседей */
    for (let j = 0; j < n; j++) {
      if (j === i) continue;
      const o = fishArray[j].group.position;
      const dx = pos.x - o.x, dy = pos.y - o.y, dz = pos.z - o.z;
      const d2 = dx * dx + dy * dy + dz * dz;
      const ar = f.avoidanceRadius;
      if (d2 < ar * ar && d2 > 1e-4) {
        const d = Math.sqrt(d2);
        const k = (1 - d / ar) * 3.0 / d;
        acc.x += dx * k; acc.y += dy * k; acc.z += dz * k;
      }
    }

    /* 2) Плавное отражение от стенок */
    const B = BOUNDS;
    if (pos.x < -B.x) acc.x += (-B.x - pos.x) * 2.2;
    else if (pos.x > B.x) acc.x -= (pos.x - B.x) * 2.2;
    if (pos.y < -B.y) acc.y += (-B.y - pos.y) * 2.2;
    else if (pos.y > B.y) acc.y -= (pos.y - B.y) * 2.2;
    if (pos.z < -B.z) acc.z += (-B.z - pos.z) * 2.2;
    else if (pos.z > B.z) acc.z -= (pos.z - B.z) * 2.2;

    /* 3) Преследование корма (радиус обнаружения — 15) */
    let target = f.targetFood;
    if (target && target.eaten) { f.targetFood = null; target = null; }
    if (!target) {
      let bd = 15 * 15;
      for (let k = 0; k < foods.length; k++) {
        if (foods[k].eaten) continue;
        const p2 = foods[k].mesh.position;
        const dx = p2.x - pos.x, dy = p2.y - pos.y, dz = p2.z - pos.z;
        const d2 = dx * dx + dy * dy + dz * dz;
        if (d2 < bd) { bd = d2; target = foods[k]; }
      }
      f.targetFood = target;
    }
    if (target) {
      const tp = target.mesh.position;
      const dx = tp.x - pos.x, dy = tp.y - pos.y, dz = tp.z - pos.z;
      const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (d < 1.5) {
        // Съедено: удалить корм + рост на 5%
        target.eaten = true;
        f.targetFood = null;
        f.group.scale.setScalar(Math.min(f.group.scale.x * 1.05, 2.4));
      } else {
        const w = 3.4 / d;
        acc.x += dx * w; acc.y += dy * w; acc.z += dz * w;
      }
    }

    /* 4) Случайное блуждание: периодический сдвиг траектории */
    f.wanderTimer -= dt;
    if (f.wanderTimer <= 0) {
      f.wanderTimer = rand(1.8, 4.5);
      f.velocity.x += rand(-0.9, 0.9);
      f.velocity.y += rand(-0.5, 0.5);
      f.velocity.z += rand(-0.9, 0.9);
    }

    /* Интеграция движения */
    f.velocity.addScaledVector(acc, dt);
    const sp = f.velocity.length();
    if (sp > 1e-4) {
      const goal = f.speed * (target ? 1.45 : 1); // быстрее при погоне
      f.velocity.multiplyScalar(1 + (goal / sp - 1) * Math.min(1, dt * 2.5));
    }
    pos.addScaledVector(f.velocity, dt);

    /* Поворот в направлении движения */
    if (f.velocity.lengthSq() > 0.02) {
      _lookTarget.copy(pos).add(f.velocity);
      f.group.lookAt(_lookTarget);
    }

    /* Плавная анимация: хвост, плавники, лёгкое «дыхание» */
    const w = t * f.tailSpeed + f.phase;
    f.tailPivot.rotation.y = Math.sin(w) * 0.55;
    f.leftFin.rotation.z = 0.55 + Math.sin(w * 0.7) * 0.28;
    f.rightFin.rotation.z = -0.55 - Math.sin(w * 0.7) * 0.28;
    f.dorsal.rotation.x = Math.sin(w * 0.5) * 0.16;
    f.group.rotation.z = Math.sin(w * 0.4) * 0.05;
  }
}

/* ============================================================
   СИСТЕМА КОРМЛЕНИЯ: падение с гравитацией
============================================================ */
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.3, 10, 8);
const foodMat = new THREE.MeshStandardMaterial({
  color: 0xffa636, roughness: 0.55, emissive: 0x2a1200
});

function spawnFood(at) {
  const m = new THREE.Mesh(foodGeo, foodMat);
  m.position.copy(at);
  m.castShadow = true;
  scene.add(m);
  foods.push({
    mesh: m,
    velocity: new THREE.Vector3(rand(-0.3, 0.3), rand(0.2, 0.8), rand(-0.3, 0.3)),
    eaten: false
  });
}

function updateFoods(dt) {
  for (let i = foods.length - 1; i >= 0; i--) {
    const fd = foods[i];
    if (fd.eaten) { // съедена рыбкой
      scene.remove(fd.mesh);
      foods.splice(i, 1);
      continue;
    }
    fd.velocity.y -= 4.2 * dt; // гравитация
    fd.mesh.position.addScaledVector(fd.velocity, dt);
    fd.mesh.rotation.x += dt * 2.2;
    fd.mesh.rotation.z += dt * 1.4;
    // Удаление при достижении дна
    if (fd.mesh.position.y < FLOOR_Y + 0.35) {
      scene.remove(fd.mesh);
      foods.splice(i, 1);
    }
  }
}

/* ============================================================
   КЛИК ПО АКВАРИУМУ = ПОКРМИТЬ (Raycaster)
============================================================ */
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
const _camDir = new THREE.Vector3();
const _plane = new THREE.Plane();
const _hit = new THREE.Vector3();
let downXY = null;

renderer.domElement.addEventListener('pointerdown', e => {
  downXY = { x: e.clientX, y: e.clientY };
});
renderer.domElement.addEventListener('pointerup', e => {
  if (!downXY) return;
  const moved = Math.hypot(e.clientX - downXY.x, e.clientY - downXY.y);
  downXY = null;
  if (moved > 6) return; // это было вращение камеры, а не клик

  ndc.x = (e.clientX / innerWidth) * 2 - 1;
  ndc.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(ndc, camera);

  // Плоскость, перпендикулярная взгляду, через центр аквариума
  camera.getWorldDirection(_camDir);
  _plane.setFromNormalAndCoplanarPoint(_camDir, new THREE.Vector3(0, 0, 0));

  if (raycaster.ray.intersectPlane(_plane, _hit)) {
    _hit.x = THREE.MathUtils.clamp(_hit.x, -BOUNDS.x + 0.4, BOUNDS.x - 0.4);
    _hit.y = THREE.MathUtils.clamp(_hit.y, -9.5, 11);
    _hit.z = THREE.MathUtils.clamp(_hit.z, -BOUNDS.z + 0.4, BOUNDS.z - 0.4);
    spawnFood(_hit);
  }
});

/* ============================================================
   КНОПКИ ИНТЕРФЕЙСА
============================================================ */
const uiFish = document.getElementById('fishCount');
const uiFps = document.getElementById('fps');
function updateStats() { uiFish.textContent = '🐟 Рыбок: ' + fishArray.length; }

let lightOn = true;
document.getElementById('btnFish').addEventListener('click', () => spawnFish(null));
document.getElementById('btnBubbles').addEventListener('click', () => {
  for (let i = 0; i < 10; i++) addBubble();
});
document.getElementById('btnLight').addEventListener('click', e => {
  lightOn = !lightOn;
  sun.intensity = lightOn ? 1.15 : 0.22;
  e.currentTarget.textContent = lightOn ? '💡 Свет: вкл' : '💡 Свет: выкл';
});

/* ============================================================
   ПОКАЧИВАНИЕ ВОДОРОСЛЕЙ
============================================================ */
function updateWeeds(t) {
  for (let i = 0; i < weeds.length; i++) {
    const wd = weeds[i];
    wd.pivot.rotation.x = Math.sin(t * 0.9 + wd.phase) * wd.amp;
    wd.pivot.rotation.z = Math.cos(t * 0.7 + wd.phase) * wd.amp;
  }
}

/* ============================================================
   ГЛАВНЫЙ ЦИКЛ (requestAnimationFrame + дельта-время)
============================================================ */
const clock = new THREE.Clock();
let frames = 0, fpsT = performance.now();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  updateFoods(dt);
  updateFish(dt, t);
  updateBubbles(dt, t);
  updateWeeds(t);

  controls.update(); // damping
  renderer.render(scene, camera);

  // FPS-счётчик
  frames++;
  const now = performance.now();
  if (now - fpsT >= 500) {
    uiFps.textContent = Math.round(frames * 1000 / (now - fpsT)) + ' FPS';
    frames = 0;
    fpsT = now;
  }
}
animate();

/* ============================================================
   RESIZE
============================================================ */
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, height = innerHeight);
});
</script>
</body>
</html>
```

---

## 🔍 Что реализовано

| Система | Детали |
|---|---|
| **Рыбки** | 15 шт., 8 цветовых схем, тело/глаза/зрачки/хвост/плавники, масштаб 0.6–1.2 |
| **ИИ** | Отталкивание соседей, отражение от стенок, блуждание, погоня за кормом (радиус 15), рост +5% |
| **Аквариум** | Стекло `transmission: 0.95`, wireframe-рамка, 36×24×20 |
| **Декор** | Песок с procedural-неровностями, 8 камней, 12 водорослей (CatmullRom + Tube) |
| **Пузыри** | 30 шт., подъём + sin/cos покачивание, сброс на дно |
| **Кормление** | Клик → Raycaster → плоскость через центр, гравитация, удаление у дна |
| **Свет** | Ambient + Directional (2048², PCFSoft) + 2 PointLight, туман `FogExp2` |
| **Камера** | OrbitControls: зум 10–60, `maxPolarAngle π/1.8`, damping |
| **UI** | Glass-панели, градиентный заголовок, кнопки с hover-glow, счётчик рыбок + FPS |

**Оптимизации:** общие геометрии и материалы переиспользуются между рыбками (15 рыбок ≈ 150 мешей, но всего ~12 уникальных геометрич