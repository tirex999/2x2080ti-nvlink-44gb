# 🐠 3D Аквариум с Реалистичными Рыбками

Вот полноценная реализация проекта в одном HTML-файле:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #001133; }
  canvas { display: block; }

  .panel {
    position: absolute;
    padding: 16px 20px;
    background: rgba(10, 40, 80, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(120, 200, 255, 0.3);
    border-radius: 14px;
    color: #d0eeff;
    box-shadow: 0 8px 32px rgba(0, 20, 60, 0.5), inset 0 0 20px rgba(80, 160, 255, 0.08);
    user-select: none;
    z-index: 10;
  }
  #info-panel { top: 20px; left: 20px; max-width: 280px; }
  #stats-panel { top: 20px; right: 20px; text-align: right; min-width: 150px; }

  h1 {
    font-size: 20px;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #4dffd2, #4dc3ff, #b44dff);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: hueShift 6s linear infinite;
  }
  @keyframes hueShift { to { filter: hue-rotate(360deg); } }

  .instructions { font-size: 12px; line-height: 1.7; opacity: 0.85; margin-bottom: 12px; }
  .instructions b { color: #7de0ff; }

  button {
    display: block;
    width: 100%;
    margin: 6px 0;
    padding: 9px 14px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    color: white;
    background: linear-gradient(135deg, #1e7fd4, #0e4f9c);
    box-shadow: 0 3px 10px rgba(0, 80, 180, 0.4);
    transition: all 0.2s ease;
  }
  button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 6px 18px rgba(60, 160, 255, 0.6), 0 0 12px rgba(80, 180, 255, 0.4);
    background: linear-gradient(135deg, #2b9af0, #1663bd);
  }
  button:active { transform: translateY(0) scale(0.98); }
  button.off { background: linear-gradient(135deg, #555, #333); }

  .stat { font-size: 14px; margin: 4px 0; }
  .stat span { color: #6df0c8; font-weight: bold; font-size: 17px; }
  #fps { color: #ffd76d; }

  @media (max-width: 640px) {
    #info-panel { max-width: 200px; padding: 10px; }
    #info-panel .instructions { display: none; }
    h1 { font-size: 15px; }
  }
</style>
</head>
<body>

<div class="panel" id="info-panel">
  <h1>🐠 3D Аквариум</h1>
  <div class="instructions">
    <b>ЛКМ + движение</b> — вращение камеры<br>
    <b>ПКМ + движение</b> — панорамирование<br>
    <b>Колесо мыши</b> — приближение<br>
    <b>Клик по аквариуму</b> — бросить корм!
  </div>
  <button id="btnFish">🐟 Добавить рыбку</button>
  <button id="btnBubbles">💭 Больше пузырей</button>
  <button id="btnLight">💡 Свет: ВКЛ</button>
</div>

<div class="panel" id="stats-panel">
  <div class="stat">Рыбки: <span id="fishCount">15</span></div>
  <div class="stat">Корм: <span id="foodCount">0</span></div>
  <div class="stat">FPS: <span id="fps">60</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// СЦЕНА, КАМЕРА, РЕНДЕРЕР
// ============================================================
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x041b3d);
scene.fog = new THREE.FogExp2(0x062a55, 0.012);

const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 200);
camera.position.set(28, 16, 30);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// OrbitControls
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.target.set(0, 0, 0);

// ============================================================
// РАЗМЕРЫ АКВАРИУМА
// ============================================================
const TANK = { w: 36, h: 24, d: 20 };
const BOUNDS = { x: TANK.w / 2 - 2, y: TANK.h / 2 - 2, z: TANK.d / 2 - 2 };

// ============================================================
// ОСВЕЩЕНИЕ
// ============================================================
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sunLight = new THREE.DirectionalLight(0xffffff, 1.0);
sunLight.position.set(20, 35, 15);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -30;
sunLight.shadow.camera.right = 30;
sunLight.shadow.camera.top = 25;
sunLight.shadow.camera.bottom = -25;
sunLight.shadow.camera.far = 100;
scene.add(sunLight);

const blueLight1 = new THREE.PointLight(0x3388ff, 0.8, 50);
blueLight1.position.set(-12, 8, 0);
scene.add(blueLight1);

const blueLight2 = new THREE.PointLight(0x22ccff, 0.6, 45);
blueLight2.position.set(12, -4, 5);
scene.add(blueLight2);

// ============================================================
// СТЕКЛЯННЫЙ АКВАРИУМ
// ============================================================
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xaaddff,
  transparent: true,
  opacity: 0.08,
  transmission: 0.95,
  roughness: 0.05,
  metalness: 0,
  side: THREE.DoubleSide,
  depthWrite: false
});

const tankGeo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
const tank = new THREE.Mesh(tankGeo, glassMat);
scene.add(tank);

// Рамка (wireframe edges)
const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(tankGeo),
  new THREE.LineBasicMaterial({ color: 0x66ccff, transparent: true, opacity: 0.6 })
);
scene.add(edges);

// ============================================================
// ПЕСЧАНОЕ ДНО С ПРОЦЕДУРНЫМИ Неровностями
// ============================================================
const floorGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 30);
const posAttr = floorGeo.attributes.position;
for (let i = 0; i < posAttr.count; i++) {
  const x = posAttr.getX(i), y = posAttr.getY(i);
  const h = Math.sin(x * 0.7) * Math.cos(y * 0.9) * 0.35
          + Math.sin(x * 1.8 + y * 1.2) * 0.15
          + (Math.random() - 0.5) * 0.1;
  posAttr.setZ(i, h);
}
floorGeo.computeVertexNormals();

const floor = new THREE.Mesh(
  floorGeo,
  new THREE.MeshStandardMaterial({ color: 0xd9b878, roughness: 0.95 })
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -TANK.h / 2 + 0.05;
floor.receiveShadow = true;
scene.add(floor);

// ============================================================
// КАМНИ (8 штук, деформированные додекаэдры)
// ============================================================
for (let i = 0; i < 8; i++) {
  const geo = new THREE.DodecahedronGeometry(0.7 + Math.random() * 1.2, 1);
  const p = geo.attributes.position;
  for (let j = 0; j < p.count; j++) {
    p.setXYZ(j,
      p.getX(j) * (0.8 + Math.random() * 0.4),
      p.getY(j) * (0.6 + Math.random() * 0.4),
      p.getZ(j) * (0.8 + Math.random() * 0.4));
  }
  geo.computeVertexNormals();
  const shade = 0.35 + Math.random() * 0.3;
  const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: new THREE.Color(shade, shade * 0.95, shade * 0.85), roughness: 0.9
  }));
  rock.position.set(
    (Math.random() - 0.5) * (TANK.w - 6),
    -TANK.h / 2 + 0.4,
    (Math.random() - 0.5) * (TANK.d - 5)
  );
  rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
  rock.castShadow = true;
  rock.receiveShadow = true;
  scene.add(rock);
}

// ============================================================
// ВОДОРОСЛИ (12 кустов, TubeGeometry + CatmullRomCurve3)
// ============================================================
const seaweeds = [];
for (let i = 0; i < 12; i++) {
  const bush = new THREE.Group();
  const baseX = (Math.random() - 0.5) * (TANK.w - 4);
  const baseZ = (Math.random() - 0.5) * (TANK.d - 4);
  const hue = 0.28 + Math.random() * 0.14;
  const blades = 3 + Math.floor(Math.random() * 3);

  for (let b = 0; b < blades; b++) {
    const height = 3 + Math.random() * 5;
    const pts = [];
    const bendX = (Math.random() - 0.5) * 2;
    const bendZ = (Math.random() - 0.5) * 2;
    for (let s = 0; s <= 6; s++) {
      const t = s / 6;
      pts.push(new THREE.Vector3(
        bendX * t * t * 1.5,
        height * t,
        bendZ * t * t * 1.5
      ));
    }
    const curve = new THREE.CatmullRomCurve3(pts);
    const tube = new THREE.TubeGeometry(curve, 10, 0.12, 5, false);
    const blade = new THREE.Mesh(tube, new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(hue, 0.7, 0.3 + Math.random() * 0.15),
      roughness: 0.8
    }));
    bush.add(blade);
  }
  bush.position.set(baseX, -TANK.h / 2, baseZ);
  bush.castShadow = true;
  scene.add(bush);
  seaweeds.push({ mesh: bush, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.8 });
}

// ============================================================
// ЦВЕТОВЫЕ СХЕМЫ РЫБОК
// ============================================================
const COLOR_SCHEMES = [
  { body: 0xff7b1a, fin: 0xffb347 }, // оранжевая
  { body: 0x1a6bff, fin: 0x7db8ff }, // синяя
  { body: 0xffd700, fin: 0xff3b30 }, // желто-красная
  { body: 0x9b30ff, fin: 0xd9a0ff }, // фиолетовая
  { body: 0xe01f1f, fin: 0xff8080 }, // красная
  { body: 0x1fae3c, fin: 0x8de89f }, // зеленая
  { body: 0xff5eb0, fin: 0xffc0dd }, // розовая
  { body: 0xd4af37, fin: 0xffe98a }  // золотая
];

// ============================================================
// СОЗДАНИЕ РЫБКИ
// ============================================================
const fishArray = [];

function createFish(pos) {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const group = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.4, metalness: 0.25 });
  const finMat  = new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.5, transparent: true, opacity: 0.85, side: THREE.DoubleSide });

  // Тело — вытянутая сфера
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
  body.scale.set(1.7, 0.85, 0.55);
  body.castShadow = true;
  group.add(body);

  // Глаза
  const eyeGeo = new THREE.SphereGeometry(0.2, 10, 8);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilGeo = new THREE.SphereGeometry(0.1, 8, 6);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

  [1, -1].forEach(side => {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(1.25, 0.18, side * 0.35);
    group.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(1.38, 0.18, side * 0.42);
    group.add(pupil);
  });

  // Хвост (анимируется вращением вокруг Y для «махания»)
  const tailGeo = new THREE.ConeGeometry(0.8, 1.4, 4);
  const tail = new THREE.Mesh(tailGeo, finMat);
  tail.position.set(-1.9, 0, 0);
  tail.rotation.z = Math.PI / 2;
  tail.scale.set(1, 1, 0.25);
  group.add(tail);
  // Хвост вращаем через родительский объект для чистого махания
  const tailPivot = new THREE.Group();
  tailPivot.position.set(-1.6, 0, 0);
  tail.position.set(-0.3, 0, 0);
  tailPivot.add(tail);
  group.add(tailPivot);

  // Верхний плавник
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.5, 1.0, 4), finMat);
  topFin.position.set(0.1, 0.85, 0);
  topFin.scale.set(1, 1, 0.2);
  group.add(topFin);

  // Боковые плавники
  const sideFinGeo = new THREE.ConeGeometry(0.35, 0.8, 4);
  const finL = new THREE.Mesh(sideFinGeo, finMat);
  finL.position.set(0.4, -0.3, 0.55);
  finL.rotation.x = Math.PI / 2.5;
  finL.scale.set(1, 1, 0.2);
  group.add(finL);

  const finR = new THREE.Mesh(sideFinGeo, finMat);
  finR.position.set(0.4, -0.3, -0.55);
  finR.rotation.x = -Math.PI / 2.5;
  finR.scale.set(1, 1, 0.2);
  group.add(finR);

  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  group.position.copy(pos || new THREE.Vector3(
    (Math.random() - 0.5) * BOUNDS.x * 1.8,
    (Math.random() - 0.5) * BOUNDS.y * 1.8,
    (Math.random() - 0.5) * BOUNDS.z * 1.8
  ));
  scene.add(group);

  const fish = {
    mesh: group,
    tail: tailPivot,
    leftFin: finL,
    rightFin: finR,
    velocity: new THREE.Vector3(
      (Math.random() - 0.5), (Math.random() - 0.5) * 0.3, (Math.random() - 0.5)
    ).normalize(),
    speed: 2 + Math.random() * 3,
    tailSpeed: 4 + Math.random() * 4,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 2.5 + Math.random() * 1.5,
    wanderTimer: 0,
    scale: scale
  };
  fishArray.push(fish);
  updateFishCount();
  return fish;
}

// ============================================================
// ПУЗЫРИ
// ============================================================
const bubbles = [];
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xcceeff,
  transparent: true,
  opacity: 0.35,
  transmission: 0.9,
  roughness: 0.1,
  metalness: 0
});
const bubbleGeo = new THREE.SphereGeometry(1, 10, 8);

function spawnBubble(y) {
  const size = 0.15 + Math.random() * 0.3;
  const b = new THREE.Mesh(bubbleGeo, bubbleMat);
  b.scale.setScalar(size);
  b.position.set(
    (Math.random() - 0.5) * (TANK.w - 4),
    y !== undefined ? y : -TANK.h / 2 + Math.random() * TANK.h,
    (Math.random() - 0.5) * (TANK.d - 4)
  );
  scene.add(b);
  bubbles.push({
    mesh: b,
    speed: 1.5 + Math.random() * 2,
    wobblePhase: Math.random() * Math.PI * 2,
    wobbleAmp: 0.3 + Math.random() * 0.5
  });
}
for (let i = 0; i < 30; i++) spawnBubble();

// ============================================================
// КОРМ
// ============================================================
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.22, 8, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xc46a2e, roughness: 0.8 });

function spawnFood(point) {
  const f = new THREE.Mesh(foodGeo, foodMat);
  f.position.copy(point);
  f.castShadow = true;
  scene.add(f);
  foods.push({ mesh: f, vy: 0 });
  updateFoodCount();
}

// ============================================================
// КЛИКИ — RAYCASTER (корм в точку на плоскости z=0 перед камерой)
// ============================================================
const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();
let downPos = null;

renderer.domElement.addEventListener('pointerdown', e => {
  downPos = { x: e.clientX, y: e.clientY };
});
renderer.domElement.addEventListener('pointerup', e => {
  if (!downPos) return;
  const moved = Math.hypot(e.clientX - downPos.x, e.clientY - downPos.y);
  downPos = null;
  if (moved > 6 || e.button !== 0) return; // это было вращение камеры, не клик

  mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  raycaster.setFromCamera(mouseNDC, camera);

  // Пересечение с горизонтальной плоскостью на уровне y = BOUNDS.y (у поверхности)
  const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -BOUNDS.y + 1);
  const hit = new THREE.Vector3();
  if (raycaster.ray.intersectPlane(plane, hit)) {
    hit.x = THREE.MathUtils.clamp(hit.x, -BOUNDS.x, BOUNDS.x);
    hit.z = THREE.MathUtils.clamp(hit.z, -BOUNDS.z, BOUNDS.z);
    spawnFood(hit);
  }
});

// ============================================================
// UI КНОПКИ
// ============================================================
let lightOn = true;
document.getElementById('btnFish').addEventListener('click', () => createFish());
document.getElementById('btnBubbles').addEventListener('click', () => {
  for (let i = 0; i < 10; i++) spawnBubble(-TANK.h / 2 + Math.random() * 3);
});
document.getElementById('btnLight').addEventListener('click', function() {
  lightOn = !lightOn;
  sunLight.intensity = lightOn ? 1.0 : 0.08;
  ambient.intensity = lightOn ? 0.4 : 0.15;
  this.textContent = lightOn ? '💡 Свет: ВКЛ' : '🌙 Свет: ВЫКЛ';
  this.classList.toggle('off', !lightOn);
});

function updateFishCount() { document.getElementById('fishCount').textContent = fishArray.length; }
function updateFoodCount() { document.getElementById('foodCount').textContent = foods.length; }

// ============================================================
// СТАРТОВЫЕ РЫБКИ
// ============================================================
for (let i = 0; i < 15; i++) createFish();

// ============================================================
// ЦИКЛ АНИМАЦИИ
// ============================================================
const clock = new THREE.Clock();
const _tmp = new THREE.Vector3();
const _steer = new THREE.Vector3();

let fpsFrames = 0, fpsTime = 0;
const fpsEl = document.getElementById('fps');

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // --- РЫБКИ ---
  for (let i = fishArray.length - 1; i >= 0; i--) {
    const f = fishArray[i];
    const p = f.mesh.position;
    _steer.set(0, 0, 0);

    // 1. Стены — мягкое отражение
    const margin = 3;
    ['x', 'y', 'z'].forEach(axis => {
      const lim = axis === 'x' ? BOUNDS.x : axis === 'y' ? BOUNDS.y : BOUNDS.z;
      if (p[axis] > lim - margin) _steer[axis] -= (p[axis] - (lim - margin)) * 2;
      if (p[axis] < -lim + margin) _steer[axis] += ((-lim + margin) - p[axis]) * 2;
    });

    // 2. Избегание других рыбок
    for (let j = 0; j < fishArray.length; j++) {
      if (j === i) continue;
      const o = fishArray[j];
      const d = p.distanceTo(o.mesh.position);
      if (d < f.avoidanceRadius && d > 0.001) {
        _tmp.subVectors(p, o.mesh.position).normalize().multiplyScalar((f.avoidanceRadius - d) * 1.5);
        _steer.add(_tmp);
      }
    }

    // 3. Поиск корма
    if (!f.targetFood || !foods.includes(f.targetFood)) {
      f.targetFood = null;
      let best = 15; // радиус обнаружения
      for (const food of foods) {
        const d = p.distanceTo(food.mesh.position);
        if (d < best) { best = d; f.targetFood = food; }
      }
    }
    if (f.targetFood) {
      _tmp.subVectors(f.targetFood.mesh.position, p).normalize().multiplyScalar(4);
      _steer.add(_tmp);
      if (p.distanceTo(f.targetFood.mesh.position) < 1.2) {
        // Съедено!
        scene.remove(f.targetFood.mesh);
        foods.splice(foods.indexOf(f.targetFood), 1);
        f.targetFood = null;
        f.scale = Math.min(f.scale * 1.05, 2.0); // рост +5%
        f.mesh.scale.setScalar(f.scale);
        updateFoodCount();
      }
    }

    // 4. Случайное блуждание
    f.wanderTimer -= dt;
    if (f.wanderTimer <= 0) {
      f.wanderTimer = 2 + Math.random() * 3;
      _steer.x += (Math.random() - 0.5) * 2;
      _steer.y += (Math.random() - 0.5) * 1;
      _steer.z += (Math.random() - 0.5) * 2;
    }
    // Лёгкая синусоидальная вертикальная волна
    _steer.y += Math.sin(t * 0.7 + f.phase) * 0.3;

    // Применение
    f.velocity.add(_steer.multiplyScalar(dt));
    f.velocity.y *= 0.98; // рыбы реже меняют высоту
    f.velocity.normalize();

    const spd = f.targetFood ? f.speed * 1.8 : f.speed;
    p.addScaledVector(f.velocity, spd * dt);

    // Жёсткая граница
    p.x = THREE.MathUtils.clamp(p.x, -BOUNDS.x, BOUNDS.x);
    p.y = THREE.MathUtils.clamp(p.y, -BOUNDS.y, BOUNDS.y);
    p.z = THREE.MathUtils.clamp(p.z, -BOUNDS.z, BOUNDS.z);

    // Поворот в направлении движения
    const targetYaw = Math.atan2(-f.velocity.z, f.velocity.x);
    let dy = targetYaw - f.mesh.rotation.y;
    while (dy > Math.PI) dy -= Math.PI * 2;
    while (dy < -Math.PI) dy += Math.PI * 2;
    f.mesh.rotation.y += dy * Math.min(dt * 4, 1);
    f.mesh.rotation.z = THREE.MathUtils.lerp(f.mesh.rotation.z, f.velocity.y * 0.6, dt * 3);

    // Анимация хвоста и плавников
    const wave = Math.sin(t * f.tailSpeed + f.phase);
    f.tail.rotation.y = wave * 0.6;
    f.leftFin.rotation.z = 0.3 + wave * 0.3;
    f.rightFin.rotation.z = -0.3 - wave * 0.3;
  }

  // --- ПУЗЫРИ ---
  for (const b of bubbles) {
    b.mesh.position.y += b.speed * dt;
    b.mesh.position.x += Math.sin(t * 2 + b.wobblePhase) * b.wobbleAmp * dt;
    b.mesh.position.z += Math.cos(t * 1.7 + b.wobblePhase) * b.wobbleAmp * dt;
    if (b.mesh.position.y > TANK.h / 2 - 0.5) {
      b.mesh.position.y = -TANK.h / 2 + 0.5;
      b.mesh.position.x = (Math.random() - 0.5) * (TANK.w - 4);
      b.mesh.position.z = (Math.random() - 0.5) * (TANK.d - 4);
    }
  }

  // --- КОРМ (гравитация) ---
  for (let i = foods.length - 1; i >= 0; i--) {
    const fd = foods[i];
    fd.vy -= 4 * dt;
    fd.vy = Math.max(fd.vy, -2.5);
    fd.mesh.position.y += fd.vy * dt;
    fd.mesh.position.x += Math.sin(t * 3 + i) * 0.3 * dt;
    if (fd.mesh.position.y <= -TANK.h / 2 + 0.3) {
      scene.remove(fd.mesh);
      foods.splice(i, 1);
      updateFoodCount();
    }
  }

  // --- ВОДОРОСЛИ (покачивание) ---
  for (const s of seaweeds) {
    s.mesh.rotation.x = Math.sin(t * s.speed + s.phase) * 0.12;
    s.mesh.rotation.z = Math.cos(t * s.speed * 0.8 + s.phase) * 0.1;
  }

  // Лёгкое движение подводных огней
  blueLight1.position.x = -12 + Math.sin(t * 0.3) * 4;
  blueLight2.position.z = 5 + Math.cos(t * 0.25) * 4;

  controls.update();
  renderer.render(scene, camera);

  // FPS
  fpsFrames++;
  fpsTime += dt;
  if (fpsTime >= 0.5) {
    fpsEl.textContent = Math.round(fpsFrames / fpsTime);
    fpsFrames = 0; fpsTime = 0;
  }
}
animate();

// ============================================================
// RESIZE
// ============================================================
window.addEventListener('resize', () => {
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
| **🐠 Рыбки** | 15 шт., 8 цветовых схем, глаза с зрачками, анимированный хвост (pivot), верхний и боковые плавники, масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, мягкое отражение от стен, блуждание, преследование корма (радиус 15), рост +5% при поедании |
| **🌊 Окружение** | Стеклянный бак 36×24×20 с `transmission: 0.95`, wireframe-рамка, процедурное песчаное дно, 8 деформированных камней, 12 кустов водорослей на `TubeGeometry` |
| **💭 Пузыри** | 30 штук, `MeshPhysicalMaterial`, синусоидальное покачивание, сброс у поверхности |
| **🍽️ Корм** | Raycaster-клики, гравитация, удаление на дне (клик отличается от вращения камеры!) |
| **💡 Свет** | Ambient + Directional с PCFSoftShadow 2048², 2 блуждающих PointLight, переключатель |
| **🎮 UI** | Glass-панели с blur, градиентные кнопки, FPS-счетчик, живой счетчик рыбок и корма |

**Совет:** кликните один раз по воде — стайка рыбок мгновенно сорвётся к корму! 🐟💨