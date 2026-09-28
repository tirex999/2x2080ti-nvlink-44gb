# 🐠 3D Аквариум с Реалистичными Рыбками

Полная реализация в одном HTML файле:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #0a1a3a; }
  #canvas-container { position: fixed; inset: 0; }

  .panel {
    position: fixed;
    background: rgba(10, 30, 70, 0.55);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(100, 180, 255, 0.25);
    border-radius: 16px;
    padding: 18px;
    color: #dceeff;
    box-shadow: 0 8px 32px rgba(0, 20, 60, 0.5), inset 0 1px 0 rgba(255,255,255,0.1);
    z-index: 10;
    user-select: none;
  }

  #info-panel { top: 20px; left: 20px; max-width: 280px; }
  #stats-panel { top: 20px; right: 20px; min-width: 160px; text-align: center; }

  h1 {
    font-size: 22px;
    background: linear-gradient(90deg, #4dd0ff, #a78bfa, #ff8ac4);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
  }

  .instructions { font-size: 12.5px; line-height: 1.7; opacity: 0.85; margin-bottom: 14px; }
  .instructions b { color: #6fd4ff; }

  .btn {
    display: block; width: 100%;
    margin: 8px 0; padding: 10px 14px;
    border: none; border-radius: 10px;
    background: linear-gradient(135deg, #1e6fd9, #3b9eff);
    color: white; font-size: 13.5px; font-weight: 600;
    cursor: pointer;
    transition: transform .15s, box-shadow .15s, filter .15s;
    box-shadow: 0 4px 14px rgba(30, 111, 217, 0.4);
  }
  .btn:hover { transform: translateY(-2px) scale(1.02); filter: brightness(1.15); box-shadow: 0 6px 20px rgba(60,160,255,0.55), 0 0 12px rgba(100,180,255,0.4); }
  .btn:active { transform: scale(0.97); }
  .btn.green { background: linear-gradient(135deg, #0e9f6e, #2dd4a0); box-shadow: 0 4px 14px rgba(14,159,110,0.4); }
  .btn.purple { background: linear-gradient(135deg, #7c3aed, #a78bfa); box-shadow: 0 4px 14px rgba(124,58,237,0.4); }
  .btn.orange { background: linear-gradient(135deg, #d97706, #fbbf24); box-shadow: 0 4px 14px rgba(217,119,6,0.4); }

  .stat { font-size: 14px; margin: 6px 0; }
  .stat .val { color: #6fd4ff; font-weight: 700; font-size: 18px; }

  #hint {
    position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
    background: rgba(10,30,70,0.5); backdrop-filter: blur(8px);
    padding: 8px 22px; border-radius: 30px;
    color: #9fd8ff; font-size: 13px; z-index: 10;
    border: 1px solid rgba(100,180,255,0.2);
    pointer-events: none;
    animation: pulseHint 3s ease-in-out infinite;
  }
  @keyframes pulseHint { 0%,100% { opacity: .65; } 50% { opacity: 1; } }

  @media (max-width: 700px) {
    #info-panel { max-width: 200px; padding: 12px; }
    h1 { font-size: 16px; }
    .instructions { display: none; }
  }
</style>
</head>
<body>
<div id="canvas-container"></div>

<div class="panel" id="info-panel">
  <h1>🐠 3D Аквариум</h1>
  <div class="instructions">
    <b>ЛКМ + движение</b> — вращение камеры<br>
    <b>ПКМ + движение</b> — панорамирование<br>
    <b>Колесо мыши</b> — приближение / отдаление<br>
    <b>Клик по аквариуму</b> — бросить корм 🍞
  </div>
  <button class="btn green" id="btn-fish">➕ Добавить рыбку</button>
  <button class="btn" id="btn-bubbles">🫧 Больше пузырей</button>
  <button class="btn purple" id="btn-light">💡 Свет вкл/выкл</button>
</div>

<div class="panel" id="stats-panel">
  <div class="stat">🐟 Рыбки: <span class="val" id="fish-count">15</span></div>
  <div class="stat">⚡ FPS: <span class="val" id="fps">0</span></div>
  <div class="stat">🍞 Корм: <span class="val" id="food-count">0</span></div>
</div>

<div id="hint">💡 Кликните по воде, чтобы покормить рыбок!</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// БАЗОВАЯ СЦЕНА
// ============================================================
const TANK = { w: 36, h: 24, d: 20 };

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a2a5e, 0.012);

// Градиентный фон через canvas
(function makeBackground() {
  const c = document.createElement('canvas');
  c.width = 2; c.height = 512;
  const ctx = c.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, 512);
  g.addColorStop(0, '#1e5aa8');
  g.addColorStop(0.5, '#0f3a75');
  g.addColorStop(1, '#061a3d');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 2, 512);
  const tex = new THREE.CanvasTexture(c);
  scene.background = tex;
})();

const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 200);
camera.position.set(30, 16, 34);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.getElementById('canvas-container').appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

// ============================================================
// ОСВЕЩЕНИЕ
// ============================================================
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sunLight = new THREE.DirectionalLight(0xfff4e0, 1.0);
sunLight.position.set(20, 40, 15);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -30;
sunLight.shadow.camera.right = 30;
sunLight.shadow.camera.top = 30;
sunLight.shadow.camera.bottom = -30;
sunLight.shadow.camera.far = 100;
scene.add(sunLight);

const bluePoint1 = new THREE.PointLight(0x4488ff, 0.8, 50);
bluePoint1.position.set(-12, 10, 0);
scene.add(bluePoint1);

const bluePoint2 = new THREE.PointLight(0x2266dd, 0.6, 50);
bluePoint2.position.set(12, 5, 4);
scene.add(bluePoint2);

// ============================================================
// СТЕКЛЯННЫЙ АКВАРИУМ
// ============================================================
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

const tankGeo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
const tank = new THREE.Mesh(tankGeo, glassMat);
tank.position.y = TANK.h / 2;
scene.add(tank);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(tankGeo),
  new THREE.LineBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.6 })
);
edges.position.copy(tank.position);
scene.add(edges);

// ============================================================
// ПЕСЧАНОЕ ДНО (procedural неровности)
// ============================================================
const sandGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 30);
const pos = sandGeo.attributes.position;
for (let i = 0; i < pos.count; i++) {
  const x = pos.getX(i), y = pos.getY(i);
  const edgeFade = Math.min(1, Math.min(
    Math.abs(Math.abs(x) - TANK.w/2),
    Math.abs(Math.abs(y) - TANK.d/2)
  ) / 2);
  pos.setZ(i, (Math.sin(x * 0.9) * Math.cos(y * 1.1) * 0.35 + Math.random() * 0.15) * edgeFade);
}
sandGeo.computeVertexNormals();
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({
  color: 0xd9b98a, roughness: 0.95
}));
sand.rotation.x = -Math.PI / 2;
sand.position.y = 0.1;
sand.receiveShadow = true;
scene.add(sand);

// ============================================================
// КАМНИ (деформированные додекаэдры)
// ============================================================
for (let i = 0; i < 8; i++) {
  const g = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.4, 0);
  const p = g.attributes.position;
  for (let j = 0; j < p.count; j++) {
    p.setXYZ(j,
      p.getX(j) * (0.75 + Math.random() * 0.5),
      p.getY(j) * (0.6 + Math.random() * 0.4),
      p.getZ(j) * (0.75 + Math.random() * 0.5));
  }
  g.computeVertexNormals();
  const rock = new THREE.Mesh(g, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.08, 0.1, 0.25 + Math.random() * 0.2),
    roughness: 0.9
  }));
  rock.position.set(
    (Math.random() - 0.5) * (TANK.w - 5),
    0.5 + Math.random() * 0.3,
    (Math.random() - 0.5) * (TANK.d - 4)
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
  const height = 3 + Math.random() * 6;
  const baseX = (Math.random() - 0.5) * (TANK.w - 4);
  const baseZ = (Math.random() - 0.5) * (TANK.d - 3);
  const pts = [];
  for (let j = 0; j <= 6; j++) {
    const t = j / 6;
    pts.push(new THREE.Vector3(
      Math.sin(t * 3 + i) * 0.5 * t,
      t * height,
      Math.cos(t * 2.5 + i) * 0.4 * t
    ));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const geo = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.1, 6, false);
  const hue = 0.28 + Math.random() * 0.14; // зелёно-бирюзовый
  const weed = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(hue, 0.7, 0.35),
    roughness: 0.8
  }));
  weed.position.set(baseX, 0.2, baseZ);
  weed.castShadow = true;
  weed.userData.phase = Math.random() * Math.PI * 2;
  weed.userData.speed = 0.5 + Math.random() * 0.7;
  scene.add(weed);
  seaweeds.push(weed);
}

// ============================================================
// ПУЗЫРИ
// ============================================================
const bubbles = [];
const bubbleGeo = new THREE.SphereGeometry(1, 10, 8);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xffffff,
  transparent: true,
  opacity: 0.3,
  transmission: 0.9,
  roughness: 0.1,
  metalness: 0
});

function spawnBubble() {
  const b = new THREE.Mesh(bubbleGeo, bubbleMat);
  const s = 0.1 + Math.random() * 0.3;
  b.scale.setScalar(s);
  b.position.set(
    (Math.random() - 0.5) * (TANK.w - 2),
    Math.random() * TANK.h,
    (Math.random() - 0.5) * (TANK.d - 2)
  );
  b.userData = { speed: 1.5 + Math.random() * 2.5, phase: Math.random() * Math.PI * 2, amp: 0.3 + Math.random() * 0.7 };
  scene.add(b);
  bubbles.push(b);
}
for (let i = 0; i < 30; i++) spawnBubble();

// ============================================================
// РЫБКИ
// ============================================================
const COLOR_SCHEMES = [
  { body: 0xff7a1a, fin: 0xffb066 }, // оранжевая
  { body: 0x2266ee, fin: 0x77aaff }, // синяя
  { body: 0xffcc00, fin: 0xff4422 }, // желто-красная
  { body: 0x9944dd, fin: 0xcc99ff }, // фиолетовая
  { body: 0xdd2233, fin: 0xff7788 }, // красная
  { body: 0x22bb66, fin: 0x88eebb }, // зеленая
  { body: 0xff66aa, fin: 0xffbbdd }, // розовая
  { body: 0xddaa22, fin: 0xffe688 }, // золотая
];

const fishArray = [];

function createFish() {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const group = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.4, metalness: 0.15 });
  const finMat = new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.6, transparent: true, opacity: 0.85, side: THREE.DoubleSide });

  // Тело — вытянутая сфера
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
  body.scale.set(1.6, 0.85, 0.6);
  body.castShadow = true;
  group.add(body);

  // Глаза
  const eyeGeo = new THREE.SphereGeometry(0.18, 8, 8);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilGeo = new THREE.SphereGeometry(0.09, 8, 8);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });
  [-1, 1].forEach(side => {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(1.25, 0.2, side * 0.38);
    group.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(1.38, 0.2, side * 0.42);
    group.add(pupil);
  });

  // Хвост (крепится к точке вращения)
  const tailPivot = new THREE.Group();
  tailPivot.position.x = -1.5;
  const tailShape = new THREE.ConeGeometry(0.7, 1.2, 4);
  const tail = new THREE.Mesh(tailShape, finMat);
  tail.rotation.z = Math.PI / 2;
  tail.position.x = -0.6;
  tail.scale.set(1, 1, 0.25);
  tailPivot.add(tail);
  group.add(tailPivot);

  // Верхний плавник
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.9, 3), finMat);
  topFin.position.set(0.1, 0.75, 0);
  topFin.scale.set(1.4, 1, 0.2);
  topFin.rotation.x = 0;
  group.add(topFin);

  // Боковые плавники (анимируемые)
  const finGeo = new THREE.ConeGeometry(0.3, 0.7, 3);
  const fins = [-1, 1].map(side => {
    const pivot = new THREE.Group();
    pivot.position.set(0.4, -0.15, side * 0.5);
    const fin = new THREE.Mesh(finGeo, finMat);
    fin.rotation.x = side * Math.PI / 2.3;
    fin.scale.set(1, 1, 0.25);
    pivot.add(fin);
    group.add(pivot);
    return pivot;
  });

  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  group.position.set(
    (Math.random() - 0.5) * (TANK.w - 8),
    3 + Math.random() * (TANK.h - 8),
    (Math.random() - 0.5) * (TANK.d - 6)
  );
  scene.add(group);

  const dir = new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.3, Math.random() - 0.5).normalize();

  fishArray.push({
    mesh: group,
    tail: tailPivot,
    leftFin: fins[0],
    rightFin: fins[1],
    velocity: dir,
    speed: 1.5 + Math.random() * 2.5,
    tailSpeed: 4 + Math.random() * 5,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 2.5 + Math.random() * 1.5,
    wanderTimer: Math.random() * 3,
    scale: scale
  });
  updateFishCount();
}

for (let i = 0; i < 15; i++) createFish();

// ============================================================
// КОРМ
// ============================================================
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.3, 8, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xc98a3d, roughness: 0.8 });

function spawnFood(point) {
  const f = new THREE.Mesh(foodGeo, foodMat);
  f.position.copy(point);
  f.position.y = Math.min(f.position.y, TANK.h - 1);
  f.scale.setScalar(0.7 + Math.random() * 0.6);
  f.userData.velY = 0;
  scene.add(f);
  foods.push(f);
  updateFoodCount();
}

// Клик по аквариуму (Raycaster)
const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();
let downPos = null;

renderer.domElement.addEventListener('pointerdown', e => { downPos = { x: e.clientX, y: e.clientY }; });
renderer.domElement.addEventListener('pointerup', e => {
  if (!downPos) return;
  const moved = Math.hypot(e.clientX - downPos.x, e.clientY - downPos.y);
  downPos = null;
  if (moved > 6 || e.button !== 0) return; // это было вращение камеры

  mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  raycaster.setFromCamera(mouseNDC, camera);

  // Плоскость z=0 как ориентир + сфера у ближайшей точки луча внутри бака
  const origin = raycaster.ray.origin.clone();
  const dir = raycaster.ray.direction.clone();
  // Ищем точку на луче, ближайшую к центру аквариума
  const center = new THREE.Vector3(0, TANK.h / 2, 0);
  const t = dir.dot(center.clone().sub(origin));
  const p = origin.clone().add(dir.clone().multiplyScalar(t));
  // Зажим в границы бака
  p.x = THREE.MathUtils.clamp(p.x, -TANK.w/2 + 1, TANK.w/2 - 1);
  p.y = THREE.MathUtils.clamp(p.y, 2, TANK.h - 1);
  p.z = THREE.MathUtils.clamp(p.z, -TANK.d/2 + 1, TANK.d/2 - 1);
  spawnFood(p);
});

// ============================================================
// UI КНОПКИ
// ============================================================
let lightOn = true;
document.getElementById('btn-fish').addEventListener('click', () => createFish());
document.getElementById('btn-bubbles').addEventListener('click', () => { for (let i = 0; i < 10; i++) spawnBubble(); });
document.getElementById('btn-light').addEventListener('click', () => {
  lightOn = !lightOn;
  sunLight.intensity = lightOn ? 1.0 : 0.1;
});

function updateFishCount() { document.getElementById('fish-count').textContent = fishArray.length; }
function updateFoodCount() { document.getElementById('food-count').textContent = foods.length; }

// ============================================================
// АНИМАЦИЯ
// ============================================================
const clock = new THREE.Clock();
let fpsFrames = 0, fpsTime = 0;
const tmpVec = new THREE.Vector3();
const BOUNDS = {
  x: TANK.w / 2 - 2.5,
  yMin: 1.5, yMax: TANK.h - 1.5,
  z: TANK.d / 2 - 2.0
};

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // --- Рыбки ---
  for (let i = 0; i < fishArray.length; i++) {
    const f = fishArray[i];
    const p = f.mesh.position;

    // Случайное блуждание
    f.wanderTimer -= dt;
    if (f.wanderTimer <= 0) {
      f.wanderTimer = 2 + Math.random() * 4;
      tmpVec.set((Math.random() - 0.5), (Math.random() - 0.5) * 0.4, (Math.random() - 0.5)).normalize();
      f.velocity.lerp(tmpVec, 0.6);
    }

    // Поиск корма (радиус 15)
    f.targetFood = null;
    let bestDist = 15;
    for (const food of foods) {
      const d = p.distanceTo(food.position);
      if (d < bestDist) { bestDist = d; f.targetFood = food; }
    }
    if (f.targetFood) {
      tmpVec.subVectors(f.targetFood.position, p).normalize();
      f.velocity.lerp(tmpVec, 3.5 * dt);
      // Съедание
      if (p.distanceTo(f.targetFood.position) < 1.2 + f.scale) {
        scene.remove(f.targetFood);
        foods.splice(foods.indexOf(f.targetFood), 1);
        f.scale = Math.min(f.scale * 1.05, 2.0); // рост +5%
        f.mesh.scale.setScalar(f.scale);
        f.targetFood = null;
        updateFoodCount();
      }
    }

    // Избегание столкновений
    for (let j = 0; j < fishArray.length; j++) {
      if (j === i) continue;
      const other = fishArray[j].mesh.position;
      const dx = p.x - other.x, dy = p.y - other.y, dz = p.z - other.z;
      const distSq = dx*dx + dy*dy + dz*dz;
      const r = f.avoidanceRadius;
      if (distSq < r * r && distSq > 0.001) {
        const d = Math.sqrt(distSq);
        const push = (1 - d / r) * dt * 4;
        f.velocity.x += (dx / d) * push;
        f.velocity.y += (dy / d) * push;
        f.velocity.z += (dz / d) * push;
      }
    }

    // Отражение от стен (плавное)
    const margin = 2.5, turn = dt * 2.5;
    if (p.x > BOUNDS.x) f.velocity.x -= turn;
    if (p.x < -BOUNDS.x) f.velocity.x += turn;
    if (p.y > BOUNDS.yMax) f.velocity.y -= turn;
    if (p.y < BOUNDS.yMin) f.velocity.y += turn;
    if (p.z > BOUNDS.z) f.velocity.z -= turn;
    if (p.z < -BOUNDS.z) f.velocity.z += turn;

    f.velocity.normalize();

    // Движение
    p.addScaledVector(f.velocity, f.speed * dt);
    p.x = THREE.MathUtils.clamp(p.x, -BOUNDS.x - 1, BOUNDS.x + 1);
    p.y = THREE.MathUtils.clamp(p.y, BOUNDS.yMin - 0.5, BOUNDS.yMax + 0.5);
    p.z = THREE.MathUtils.clamp(p.z, -BOUNDS.z - 1, BOUNDS.z + 1);

    // Поворот в направлении движения (рыба смотрит по +X)
    const targetYaw = Math.atan2(-f.velocity.z, f.velocity.x);
    let dy2 = targetYaw - f.mesh.rotation.y;
    while (dy2 > Math.PI) dy2 -= Math.PI * 2;
    while (dy2 < -Math.PI) dy2 += Math.PI * 2;
    f.mesh.rotation.y += dy2 * Math.min(1, 5 * dt);
    f.mesh.rotation.z = THREE.MathUtils.lerp(f.mesh.rotation.z, THREE.MathUtils.clamp(f.velocity.y * -0.6, -0.4, 0.4), 3 * dt);

    // Анимация хвоста и плавников
    const animSpeed = f.tailSpeed * (f.targetFood ? 1.8 : 1);
    f.tail.rotation.y = Math.sin(t * animSpeed + f.phase) * 0.6;
    f.leftFin.rotation.y = Math.sin(t * animSpeed * 0.8 + f.phase) * 0.35;
    f.rightFin.rotation.y = Math.sin(t * animSpeed * 0.8 + f.phase + Math.PI) * 0.35;
  }

  // --- Корм (гравитация) ---
  for (let i = foods.length - 1; i >= 0; i--) {
    const f = foods[i];
    f.userData.velY -= 4 * dt;
    f.position.y += f.userData.velY * dt;
    f.position.x += Math.sin(t * 2 + i) * 0.3 * dt;
    if (f.position.y <= 0.5) {
      scene.remove(f);
      foods.splice(i, 1);
      updateFoodCount();
    }
  }

  // --- Пузыри ---
  for (const b of bubbles) {
    b.position.y += b.userData.speed * dt;
    b.position.x += Math.sin(t * 2 + b.userData.phase) * b.userData.amp * dt;
    b.position.z += Math.cos(t * 1.6 + b.userData.phase) * b.userData.amp * dt;
    if (b.position.y > TANK.h - 0.5) {
      b.position.y = 0.5;
      b.position.x = (Math.random() - 0.5) * (TANK.w - 2);
      b.position.z = (Math.random() - 0.5) * (TANK.d - 2);
      b.userData.velY = 0;
    }
  }

  // --- Водоросли ---
  for (const w of seaweeds) {
    w.rotation.x = Math.sin(t * w.userData.speed + w.userData.phase) * 0.12;
    w.rotation.z = Math.cos(t * w.userData.speed * 0.8 + w.userData.phase) * 0.1;
  }

  // --- FPS ---
  fpsFrames++;
  fpsTime += dt;
  if (fpsTime >= 0.5) {
    document.getElementById('fps').textContent = Math.round(fpsFrames / fpsTime);
    fpsFrames = 0; fpsTime = 0;
  }

  controls.update();
  renderer.render(scene, camera);
}
animate();

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
|---------|--------|
| **🐠 Рыбки** | 15 штук, 8 цветовых схем, масштаб 0.6–1.2, тело-сфера, глаза с зрачками, анимируемые хвост/плавники |
| **🧠 ИИ** | Избегание столкновений, мягкое отражение от стен, блуждание, поиск корма (r=15), рост +5% при поедании |
| **🌊 Окружение** | Стеклянный бак 36×24×20 с `transmission: 0.95` и wireframe, procedural песчаное дно, 8 деформированных камней, 12 качающихся водорослей из `TubeGeometry` |
| **🫧 Пузыри** | 30 штук, `MeshPhysicalMaterial`, синусоидальное покачивание, респаун у дна |
| **🍞 Корм** | Клик с различением от вращения камеры (порог 6px), гравитация, съедение с ростом |
| **💡 Свет** | Ambient + Directional с PCFSoftShadow 2048², 2 голубых PointLight, переключатель |
| **🎮 Камера** | OrbitControls с damping, зум 10–60, ограничение polar angle |
| **🖥️ UI** | Glass-панели с blur, градиентный заголовок, FPS/счётчики, hover-кнопки, адаптивность |

Просто сохраните как `.html` и откройте в браузере! 🐟