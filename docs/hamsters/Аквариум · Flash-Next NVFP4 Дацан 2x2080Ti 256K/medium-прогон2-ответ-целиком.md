# 🐠 3D Аквариум с Реалистичными Рыбками

Вот полная реализация проекта в одном HTML-файле:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    overflow: hidden;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: linear-gradient(180deg, #021026 0%, #0a2a52 100%);
  }

  #canvas-container { position: fixed; inset: 0; }

  .panel {
    position: fixed;
    background: rgba(10, 40, 80, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(120, 200, 255, 0.25);
    border-radius: 16px;
    padding: 18px;
    color: #d8f0ff;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.1);
    z-index: 10;
  }

  #info-panel { top: 20px; left: 20px; max-width: 280px; }

  #info-panel h1 {
    font-size: 22px;
    background: linear-gradient(90deg, #4dd0ff, #a78bfa, #ffb347);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
  }

  #info-panel p { font-size: 12.5px; line-height: 1.6; opacity: 0.85; margin-bottom: 12px; }

  .btn {
    display: block;
    width: 100%;
    margin: 8px 0;
    padding: 10px 14px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    color: #fff;
    background: linear-gradient(135deg, #0891b2, #2563eb);
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
    transition: all 0.25s ease;
  }
  .btn:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 6px 20px rgba(56, 189, 248, 0.6), 0 0 18px rgba(56, 189, 248, 0.35);
  }
  .btn:active { transform: translateY(0) scale(0.98); }
  .btn.orange { background: linear-gradient(135deg, #ea580c, #f59e0b); box-shadow: 0 4px 14px rgba(234, 88, 12, 0.4); }
  .btn.green { background: linear-gradient(135deg, #059669, #34d399); box-shadow: 0 4px 14px rgba(5, 150, 105, 0.4); }

  #stats-panel { top: 20px; right: 20px; text-align: right; min-width: 150px; }
  #stats-panel div { font-size: 14px; margin: 4px 0; }
  .stat-value { color: #4dd0ff; font-weight: bold; font-size: 17px; }

  @media (max-width: 640px) {
    #info-panel { max-width: 200px; padding: 12px; }
    #info-panel h1 { font-size: 16px; }
    #info-panel p { font-size: 10.5px; }
  }
</style>
</head>
<body>
<div id="canvas-container"></div>

<div class="panel" id="info-panel">
  <h1>🐠 3D Аквариум</h1>
  <p>
    🖱️ <b>ЛКМ + движение</b> — вращение<br>
    🖱️ <b>ПКМ + движение</b> — панорама<br>
    🖱️ <b>Колесо</b> — зум<br>
    🍽️ <b>Клик по аквариуму</b> — покормить рыбок!
  </p>
  <button class="btn orange" id="btn-fish">➕ Добавить рыбку</button>
  <button class="btn" id="btn-bubbles">💭 Больше пузырей</button>
  <button class="btn green" id="btn-light">💡 Свет вкл/выкл</button>
</div>

<div class="panel" id="stats-panel">
  <div>Рыбки: <span class="stat-value" id="fish-count">15</span></div>
  <div>Корм: <span class="stat-value" id="food-count">0</span></div>
  <div>FPS: <span class="stat-value" id="fps">60</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// БАЗОВАЯ СЦЕНА
// ============================================================
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x062040);
scene.fog = new THREE.FogExp2(0x083058, 0.012);

const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 200);
camera.position.set(28, 16, 30);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.getElementById('canvas-container').appendChild(renderer.domElement);

// OrbitControls
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.target.set(0, 8, 0);

// ============================================================
// ОСВЕЩЕНИЕ
// ============================================================
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sunLight = new THREE.DirectionalLight(0xfff2d8, 1.1);
sunLight.position.set(15, 35, 10);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -25;
sunLight.shadow.camera.right = 25;
sunLight.shadow.camera.top = 25;
sunLight.shadow.camera.bottom = -25;
sunLight.shadow.camera.far = 80;
scene.add(sunLight);

const blueLight1 = new THREE.PointLight(0x3aa6ff, 0.9, 50);
blueLight1.position.set(-12, 18, -6);
scene.add(blueLight1);

const blueLight2 = new THREE.PointLight(0x2255ff, 0.7, 50);
blueLight2.position.set(12, 6, 8);
scene.add(blueLight2);

// ============================================================
// АКВАРИУМ (СТЕКЛО)
// ============================================================
const TANK = { w: 36, h: 24, d: 20 };

const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xaaddff,
  transparent: true,
  opacity: 0.12,
  transmission: 0.95,
  roughness: 0.05,
  metalness: 0,
  side: THREE.DoubleSide,
  depthWrite: false
});

const glassBox = new THREE.Mesh(new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d), glassMat);
glassBox.position.y = TANK.h / 2;
scene.add(glassBox);

// Рамка (wireframe edges)
const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d)),
  new THREE.LineBasicMaterial({ color: 0x7fd4ff, transparent: true, opacity: 0.55 })
);
edges.position.y = TANK.h / 2;
scene.add(edges);

// ============================================================
// ПЕСЧАНОЕ ДНО (procedural неровности)
// ============================================================
const sandGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 30);
const posAttr = sandGeo.attributes.position;
for (let i = 0; i < posAttr.count; i++) {
  const x = posAttr.getX(i), y = posAttr.getY(i);
  // не поднимать у краёв
  const edgeFade = Math.min(1, Math.min(
    Math.abs(Math.abs(x) - TANK.w / 2),
    Math.abs(Math.abs(y) - TANK.d / 2)
  ) / 3);
  posAttr.setZ(i, (Math.sin(x * 0.9) * Math.cos(y * 1.1) * 0.35 + Math.random() * 0.25) * edgeFade);
}
sandGeo.computeVertexNormals();

const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({
  color: 0xd9b978, roughness: 1
}));
sand.rotation.x = -Math.PI / 2;
sand.receiveShadow = true;
scene.add(sand);

// ============================================================
// КАМНИ (деформированные додекаэдры)
// ============================================================
for (let i = 0; i < 8; i++) {
  const geo = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.4, 0);
  const p = geo.attributes.position;
  for (let j = 0; j < p.count; j++) {
    p.setXYZ(j,
      p.getX(j) * (0.75 + Math.random() * 0.5),
      p.getY(j) * (0.6 + Math.random() * 0.4),
      p.getZ(j) * (0.75 + Math.random() * 0.5)
    );
  }
  geo.computeVertexNormals();
  const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.07 + Math.random() * 0.06, 0.15, 0.28 + Math.random() * 0.2),
    roughness: 0.95
  }));
  rock.position.set(
    (Math.random() - 0.5) * (TANK.w - 5),
    0.4,
    (Math.random() - 0.5) * (TANK.d - 5)
  );
  rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
  rock.castShadow = true;
  rock.receiveShadow = true;
  scene.add(rock);
}

// ============================================================
// ВОДОРОСЛИ (TubeGeometry + CatmullRomCurve3)
// ============================================================
const seaweeds = [];
for (let i = 0; i < 12; i++) {
  const baseX = (Math.random() - 0.5) * (TANK.w - 4);
  const baseZ = (Math.random() - 0.5) * (TANK.d - 4);
  const height = 3 + Math.random() * 6;

  const points = [];
  for (let j = 0; j <= 5; j++) {
    const t = j / 5;
    points.push(new THREE.Vector3(
      Math.sin(t * 3) * 0.5,
      t * height,
      Math.cos(t * 2.5) * 0.4
    ));
  }
  const curve = new THREE.CatmullRomCurve3(points);
  const strand = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 12, 0.12, 5, false),
    new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(0.28 + Math.random() * 0.14, 0.7, 0.3 + Math.random() * 0.15),
      roughness: 0.8
    })
  );
  strand.position.set(baseX, 0, baseZ);
  strand.castShadow = true;

  // куст из 2-3 прядей
  const bush = new THREE.Group();
  bush.add(strand);
  const strands = 2 + Math.floor(Math.random() * 2);
  for (let s = 1; s < strands; s++) {
    const clone = strand.clone();
    clone.rotation.y = Math.random() * Math.PI * 2;
    clone.position.x = (Math.random() - 0.5) * 0.8;
    clone.position.z = (Math.random() - 0.5) * 0.8;
    bush.add(clone);
  }
  bush.userData.phase = Math.random() * Math.PI * 2;
  bush.userData.speed = 0.5 + Math.random() * 0.7;
  scene.add(bush);
  seaweeds.push(bush);
}

// ============================================================
// ПУЗЫРИ
// ============================================================
const bubbles = [];
const bubbleGeo = new THREE.SphereGeometry(1, 10, 8);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xcceeff,
  transparent: true,
  opacity: 0.35,
  transmission: 0.9,
  roughness: 0.1,
  metalness: 0
});

function addBubble(x, z, radius) {
  const b = new THREE.Mesh(bubbleGeo, bubbleMat);
  const r = radius || 0.12 + Math.random() * 0.3;
  b.scale.setScalar(r);
  b.position.set(
    x !== undefined ? x : (Math.random() - 0.5) * (TANK.w - 4),
    Math.random() * TANK.h * 0.9 + 0.5,
    z !== undefined ? z : (Math.random() - 0.5) * (TANK.d - 4)
  );
  b.userData = {
    speed: 1.5 + Math.random() * 2.5,
    wobblePhase: Math.random() * Math.PI * 2,
    wobbleAmp: 0.3 + Math.random() * 0.6,
    baseX: b.position.x,
    baseZ: b.position.z
  };
  scene.add(b);
  bubbles.push(b);
}
for (let i = 0; i < 30; i++) addBubble();

// ============================================================
// РЫБКИ
// ============================================================
const COLOR_SCHEMES = [
  { body: 0xff7a1a, fin: 0xffb066 }, // оранжевая
  { body: 0x2266ff, fin: 0x7fb2ff }, // синяя
  { body: 0xffd400, fin: 0xff4422 }, // желто-красная
  { body: 0x9944dd, fin: 0xc99bff }, // фиолетовая
  { body: 0xdd2233, fin: 0xff7788 }, // красная
  { body: 0x22bb55, fin: 0x88eeaa }, // зеленая
  { body: 0xff66aa, fin: 0xffb8d9 }, // розовая
  { body: 0xddaa22, fin: 0xffe27a }  // золотая
];

const fishArray = [];

function createFish() {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const group = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.35, metalness: 0.25 });
  const finMat = new THREE.MeshStandardMaterial({
    color: scheme.fin, roughness: 0.5, transparent: true, opacity: 0.85, side: THREE.DoubleSide
  });

  // Тело — вытянутая сфера
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
  body.scale.set(1.6, 0.85, 0.55);
  body.castShadow = true;
  group.add(body);

  // Глаза
  const eyeGeo = new THREE.SphereGeometry(0.18, 8, 8);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilGeo = new THREE.SphereGeometry(0.09, 6, 6);
  const pupilMat = new THREE.MeshBasicMaterial({ color: 0x000000 });

  [-1, 1].forEach(side => {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(1.15, 0.2, side * 0.38);
    group.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(1.28, 0.2, side * 0.42);
    group.add(pupil);
  });

  // Хвост (крепится к основанию у тела — точка вращения сзади)
  const tailPivot = new THREE.Group();
  tailPivot.position.set(-1.5, 0, 0);
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.75, 1.3, 4), finMat);
  tail.scale.set(1, 1, 0.2);
  tail.rotation.z = Math.PI / 2;
  tail.position.x = -0.65;
  tailPivot.add(tail);
  group.add(tailPivot);

  // Верхний плавник
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.45, 0.9, 4), finMat);
  topFin.scale.set(1.4, 1, 0.18);
  topFin.position.set(0.1, 0.85, 0);
  group.add(topFin);

  // Боковые плавники (пивоты для анимации)
  const fins = [];
  [-1, 1].forEach(side => {
    const pivot = new THREE.Group();
    pivot.position.set(0.45, -0.2, side * 0.4);
    const fin = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.7, 4), finMat);
    fin.scale.set(1, 1, 0.18);
    fin.position.z = side * 0.3;
    fin.rotation.x = side * Math.PI / 2.4;
    pivot.add(fin);
    group.add(pivot);
    fins.push(pivot);
  });

  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  group.position.set(
    (Math.random() - 0.5) * (TANK.w - 8),
    3 + Math.random() * (TANK.h - 7),
    (Math.random() - 0.5) * (TANK.d - 6)
  );
  scene.add(group);

  const dir = new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.3, Math.random() - 0.5).normalize();

  fishArray.push({
    mesh: group,
    tail: tailPivot,
    leftFin: fins[0],
    rightFin: fins[1],
    velocity: dir.multiplyScalar(1 + Math.random()),
    speed: 2.2 + Math.random() * 3,
    tailSpeed: 5 + Math.random() * 5,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 2.5 + Math.random() * 1.5,
    wanderTimer: 0
  });
  updateFishCount();
}

for (let i = 0; i < 15; i++) createFish();

// ============================================================
// КОРМ
// ============================================================
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.22, 6, 5);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xc47a2e, roughness: 0.9 });

function addFood(point) {
  const f = new THREE.Mesh(foodGeo, foodMat);
  f.position.copy(point);
  f.position.y = Math.min(f.position.y, TANK.h - 0.5);
  f.userData.vy = 0;
  scene.add(f);
  foods.push(f);
  updateFoodCount();

  // рыбки в радиусе 15 обнаруживают корм
  fishArray.forEach(fish => {
    if (!fish.targetFood && fish.mesh.position.distanceTo(point) < 15) {
      fish.targetFood = f;
    }
  });
}

// Клик по аквариуму (Raycaster)
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let dragStart = null;

renderer.domElement.addEventListener('pointerdown', e => {
  dragStart = { x: e.clientX, y: e.clientY };
});
renderer.domElement.addEventListener('pointerup', e => {
  if (!dragStart) return;
  const moved = Math.hypot(e.clientX - dragStart.x, e.clientY - dragStart.y);
  dragStart = null;
  if (moved > 6 || e.button !== 0) return; // это был drag камеры

  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);

  // плоскость кормления на ближней стенке аквариума
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
  const hit = new THREE.Vector3();
  if (raycaster.ray.intersectPlane(plane, hit)) {
    hit.x = THREE.MathUtils.clamp(hit.x, -TANK.w / 2 + 1, TANK.w / 2 - 1);
    hit.y = THREE.MathUtils.clamp(hit.y, 1, TANK.h - 1);
    hit.z = THREE.MathUtils.clamp(hit.z, -TANK.d / 2 + 1, TANK.d / 2 - 1);
    addFood(hit);
  } else {
    addFood(new THREE.Vector3(0, TANK.h - 2, 0));
  }
});

// ============================================================
// UI КНОПКИ
// ============================================================
document.getElementById('btn-fish').addEventListener('click', () => {
  if (fishArray.length < 40) createFish();
});
document.getElementById('btn-bubbles').addEventListener('click', () => {
  for (let i = 0; i < 10; i++) addBubble();
});
let lightOn = true;
document.getElementById('btn-light').addEventListener('click', () => {
  lightOn = !lightOn;
  sunLight.intensity = lightOn ? 1.1 : 0.12;
  scene.fog.density = lightOn ? 0.012 : 0.025;
  scene.background.setHex(lightOn ? 0x062040 : 0x020c1c);
});

function updateFishCount() {
  document.getElementById('fish-count').textContent = fishArray.length;
}
function updateFoodCount() {
  document.getElementById('food-count').textContent = foods.length;
}

// ============================================================
// ЦИКЛ АНИМАЦИИ
// ============================================================
const clock = new THREE.Clock();
const _tmp = new THREE.Vector3();
const BOUNDS = {
  x: TANK.w / 2 - 2.5,
  yMin: 1.5, yMax: TANK.h - 1.5,
  z: TANK.d / 2 - 2.5
};

let fpsTime = 0, frames = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // --- Рыбки ---
  for (let i = fishArray.length - 1; i >= 0; i--) {
    const fish = fishArray[i];
    const p = fish.mesh.position;
    const v = fish.velocity;

    // 1. Целевое направление — к корму
    if (fish.targetFood) {
      if (!foods.includes(fish.targetFood)) {
        fish.targetFood = null;
      } else {
        _tmp.copy(fish.targetFood.position).sub(p);
        const dist = _tmp.length();
        if (dist < 1.2 * fish.mesh.scale.x * 2) {
          // съедено!
          scene.remove(fish.targetFood);
          foods.splice(foods.indexOf(fish.targetFood), 1);
          fish.mesh.scale.multiplyScalar(1.05); // рост +5%
          fish.targetFood = null;
          updateFoodCount();
        } else {
          _tmp.normalize().multiplyScalar(fish.speed * 1.6);
          v.lerp(_tmp, 3 * dt);
        }
      }
    }

    // 2. Случайное блуждание
    fish.wanderTimer -= dt;
    if (fish.wanderTimer <= 0 && !fish.targetFood) {
      fish.wanderTimer = 2 + Math.random() * 3;
      _tmp.set(
        (Math.random() - 0.5),
        (Math.random() - 0.5) * 0.4,
        (Math.random() - 0.5)
      ).normalize().multiplyScalar(fish.speed);
      v.lerp(_tmp, 0.6);
    }

    // 3. Избегание других рыбок
    for (let j = 0; j < fishArray.length; j++) {
      if (j === i) continue;
      const other = fishArray[j].mesh.position;
      const dx = p.x - other.x, dy = p.y - other.y, dz = p.z - other.z;
      const d2 = dx * dx + dy * dy + dz * dz;
      const r = fish.avoidanceRadius;
      if (d2 < r * r && d2 > 0.001) {
        const d = Math.sqrt(d2);
        const push = (r - d) / r * 8 * dt;
        v.x += dx / d * push;
        v.y += dy / d * push;
        v.z += dz / d * push;
      }
    }

    // 4. Отражение от стен (плавное)
    const margin = 3, turnForce = 6 * dt;
    if (p.x > BOUNDS.x - margin) v.x -= turnForce * (p.x - BOUNDS.x + margin) / margin;
    if (p.x < -BOUNDS.x + margin) v.x += turnForce * (-BOUNDS.x + margin - p.x) / margin * -1 * -1;
    if (p.x < -BOUNDS.x + margin) v.x += turnForce;
    if (p.y > BOUNDS.yMax - margin) v.y -= turnForce;
    if (p.y < BOUNDS.yMin + margin) v.y += turnForce;
    if (p.z > BOUNDS.z - margin) v.z -= turnForce;
    if (p.z < -BOUNDS.z + margin) v.z += turnForce;

    // Ограничение скорости
    const len = v.length();
    const maxSpeed = fish.targetFood ? fish.speed * 1.8 : fish.speed;
    if (len > maxSpeed) v.multiplyScalar(maxSpeed / len);
    if (len < fish.speed * 0.4) v.multiplyScalar(1.02);

    // Позиция
    p.addScaledVector(v, dt);
    p.x = THREE.MathUtils.clamp(p.x, -BOUNDS.x, BOUNDS.x);
    p.y = THREE.MathUtils.clamp(p.y, BOUNDS.yMin, BOUNDS.yMax);
    p.z = THREE.MathUtils.clamp(p.z, -BOUNDS.z, BOUNDS.z);

    // Поворот в направлении движения
    if (len > 0.01) {
      const targetYaw = Math.atan2(-v.z, v.x);
      let dy2 = targetYaw - fish.mesh.rotation.y;
      while (dy2 > Math.PI) dy2 -= Math.PI * 2;
      while (dy2 < -Math.PI) dy2 += Math.PI * 2;
      fish.mesh.rotation.y += dy2 * Math.min(1, 4 * dt);
      fish.mesh.rotation.z = THREE.MathUtils.lerp(fish.mesh.rotation.z, -v.y * 0.15, 3 * dt);
    }

    // Анимация хвоста и плавников
    const wig = Math.sin(t * fish.tailSpeed + fish.phase);
    fish.tail.rotation.y = wig * 0.6;
    fish.leftFin.rotation.x = wig * 0.35 + 0.2;
    fish.rightFin.rotation.x = -wig * 0.35 - 0.2;
  }

  // --- Корм (гравитация) ---
  for (let i = foods.length - 1; i >= 0; i--) {
    const f = foods[i];
    f.userData.vy -= 4 * dt;
    f.position.y += f.userData.vy * dt;
    f.position.x += Math.sin(t * 2 + i) * 0.3 * dt;
    if (f.position.y <= 0.3) {
      scene.remove(f);
      fishArray.forEach(fish => { if (fish.targetFood === f) fish.targetFood = null; });
      foods.splice(i, 1);
      updateFoodCount();
    }
  }

  // --- Пузыри ---
  bubbles.forEach(b => {
    const u = b.userData;
    b.position.y += u.speed * dt;
    b.position.x = u.baseX + Math.sin(t * 2 + u.wobblePhase) * u.wobbleAmp;
    b.position.z = u.baseZ + Math.cos(t * 1.6 + u.wobblePhase) * u.wobbleAmp;
    if (b.position.y > TANK.h - 0.5) {
      b.position.y = 0.5;
      u.baseX = (Math.random() - 0.5) * (TANK.w - 4);
      u.baseZ = (Math.random() - 0.5) * (TANK.d - 4);
    }
  });

  // --- Водоросли (покачивание) ---
  seaweeds.forEach(sw => {
    sw.rotation.x = Math.sin(t * sw.userData.speed + sw.userData.phase) * 0.09;
    sw.rotation.z = Math.cos(t * sw.userData.speed * 0.8 + sw.userData.phase) * 0.09;
  });

  // --- Свет слегка мерцает ---
  blueLight1.intensity = 0.9 + Math.sin(t * 1.3) * 0.15;
  blueLight2.intensity = 0.7 + Math.cos(t * 1.7) * 0.12;

  // --- FPS ---
  frames++;
  fpsTime += dt;
  if (fpsTime >= 0.5) {
    document.getElementById('fps').textContent = Math.round(frames / fpsTime);
    frames = 0; fpsTime = 0;
  }

  controls.update();
  renderer.render(scene, camera);
}
animate();

// Ресайз
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## ✨ Что реализовано

| Система | Детали |
|---|---|
| **🐠 Рыбки** | 15 штук, 8 цветовых схем, глаза с зрачками, анимируемый хвост (пивот), верхний + боковые плавники, масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, мягкое отражение от стен, блуждание по таймеру, преследование корма (радиус 15), рост +5% при поедании |
| **🌊 Окружение** | Стеклянный бак 36×24×20 (transmission 0.95) с wireframe-рамкой, procedural песчаное дно, 8 деформированных камней, 12 кустов водорослей из TubeGeometry |
| **💭 Пузыри** | 30 штук, MeshPhysicalMaterial, синусоидальное покачивание, сброс у поверхности |
| **🍽️ Корм** | Raycaster-клик (с отличием от drag камеры!), гравитация, удаление на дне |
| **💡 Свет** | Ambient + Directional с PCFSoftShadow 2048², 2 мерцающих PointLight, переключаемый режим |
| **🎮 UI** | Glass-панели с backdrop-blur, градиентные кнопки со hover-glow, FPS-счетчик, адаптивность |

**Логика клика vs вращение камеры:** корм создается только если курсор сместился менее чем на 6 пикселей — иначе это drag камеры. Просто сохраните код в файл `aquarium.html` и откройте в браузере! 🐟