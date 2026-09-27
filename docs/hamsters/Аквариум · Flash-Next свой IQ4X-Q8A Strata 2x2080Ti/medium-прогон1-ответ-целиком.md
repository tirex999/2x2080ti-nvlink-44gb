# 🐠 3D Аквариум с Реалистичными Рыбками

Полный код интерактивного 3D аквариума в одном HTML-файле:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #041e42; }
  #canvas-container { position: fixed; inset: 0; }

  .panel {
    position: fixed; padding: 18px 22px; border-radius: 16px;
    background: rgba(10, 40, 80, 0.45);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(120, 200, 255, 0.25);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), 0 0 20px rgba(50, 150, 255, 0.1);
    color: #d8f0ff; z-index: 10; user-select: none;
  }
  #info-panel { top: 20px; left: 20px; max-width: 280px; }
  #stats-panel { top: 20px; right: 20px; text-align: right; min-width: 160px; }

  h1 {
    font-size: 22px; margin-bottom: 10px;
    background: linear-gradient(90deg, #4dd0ff, #a78bfa, #ff8ac2);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .instructions { font-size: 12.5px; line-height: 1.7; opacity: 0.85; margin-bottom: 14px; }
  .instructions b { color: #7dd3fc; }

  button {
    display: block; width: 100%; margin: 6px 0; padding: 10px 14px;
    border: none; border-radius: 10px; cursor: pointer;
    font-size: 13px; font-weight: 600; color: #fff;
    background: linear-gradient(135deg, #0ea5e9, #2563eb);
    box-shadow: 0 4px 14px rgba(14, 165, 233, 0.35);
    transition: transform .15s, box-shadow .15s, filter .15s;
  }
  button:hover { transform: translateY(-2px); filter: brightness(1.15); box-shadow: 0 6px 20px rgba(14, 165, 233, 0.55); }
  button:active { transform: translateY(0); }
  #btn-light { background: linear-gradient(135deg, #f59e0b, #ef4444); box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35); }
  #btn-bubbles { background: linear-gradient(135deg, #06b6d4, #3b82f6); }

  .stat { font-size: 14px; margin: 4px 0; }
  .stat .val { color: #7dd3fc; font-weight: 700; font-size: 17px; }

  #hint {
    position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
    padding: 8px 22px; border-radius: 30px; font-size: 13px;
    background: rgba(10, 40, 80, 0.5); backdrop-filter: blur(10px);
    border: 1px solid rgba(120, 200, 255, 0.25); color: #bde3ff;
    pointer-events: none; animation: pulse 3s infinite;
  }
  @keyframes pulse { 0%,100% { opacity: .65; } 50% { opacity: 1; } }

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
    <b>Колесо мыши</b> — приближение<br>
    <b>Клик по аквариуму</b> — бросить корм 🍞
  </div>
  <button id="btn-fish">➕ Добавить рыбку</button>
  <button id="btn-bubbles">🫧 Больше пузырей</button>
  <button id="btn-light">💡 Свет вкл/выкл</button>
</div>

<div class="panel" id="stats-panel">
  <div class="stat">Рыбки: <span class="val" id="fish-count">15</span></div>
  <div class="stat">FPS: <span class="val" id="fps">60</span></div>
  <div class="stat">Корм: <span class="val" id="food-count">0</span></div>
</div>

<div id="hint">Кликните по воде, чтобы покормить рыбок!</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// БАЗА: СЦЕНА, КАМЕРА, РЕНДЕРЕР
// ============================================================
const TANK = { w: 36, h: 24, d: 20 };
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a3d6e, 0.012);

// Градиентный фон
{
  const c = document.createElement('canvas');
  c.width = 2; c.height = 512;
  const ctx = c.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, 512);
  g.addColorStop(0, '#0b4d8c');
  g.addColorStop(0.5, '#0a3d6e');
  g.addColorStop(1, '#041e42');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 2, 512);
  const tex = new THREE.CanvasTexture(c);
  scene.background = tex;
}

const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 200);
camera.position.set(28, 14, 30);

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

const sunLight = new THREE.DirectionalLight(0xfff5e0, 1.0);
sunLight.position.set(15, 30, 10);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -25; sunLight.shadow.camera.right = 25;
sunLight.shadow.camera.top = 25; sunLight.shadow.camera.bottom = -25;
sunLight.shadow.camera.far = 80;
scene.add(sunLight);

const underwater1 = new THREE.PointLight(0x3b9dff, 0.8, 50);
underwater1.position.set(-12, 5, 0);
scene.add(underwater1);

const underwater2 = new THREE.PointLight(0x2266ff, 0.7, 50);
underwater2.position.set(12, -3, 4);
scene.add(underwater2);

// ============================================================
// АКВАРИУМ: СТЕКЛО, ДНО, РАМКА
// ============================================================
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xaaddff, transparent: true, opacity: 0.08,
  transmission: 0.95, roughness: 0.05, metalness: 0,
  side: THREE.DoubleSide, depthWrite: false
});
const glass = new THREE.Mesh(new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d), glassMat);
scene.add(glass);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(glass.geometry),
  new THREE.LineBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.6 })
);
scene.add(edges);

// Песчаное дно с процедурными неровностями
const floorGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 30);
floorGeo.rotateX(-Math.PI / 2);
{
  const pos = floorGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), z = pos.getZ(i);
    pos.setY(i, Math.sin(x * 0.7) * 0.25 + Math.cos(z * 0.9) * 0.2 + Math.random() * 0.12);
  }
  floorGeo.computeVertexNormals();
}
const floor = new THREE.Mesh(floorGeo, new THREE.MeshStandardMaterial({ color: 0xd9b982, roughness: 0.95 }));
floor.position.y = -TANK.h / 2 + 0.1;
floor.receiveShadow = true;
scene.add(floor);

// Камни
const rockMat = new THREE.MeshStandardMaterial({ color: 0x7a746b, roughness: 0.9 });
for (let i = 0; i < 8; i++) {
  const geo = new THREE.DodecahedronGeometry(0.6 + Math.random() * 1.1, 0);
  const pos = geo.attributes.position;
  for (let j = 0; j < pos.count; j++) {
    pos.setXYZ(j,
      pos.getX(j) * (0.75 + Math.random() * 0.5),
      pos.getY(j) * (0.6 + Math.random() * 0.4),
      pos.getZ(j) * (0.75 + Math.random() * 0.5));
  }
  geo.computeVertexNormals();
  const rock = new THREE.Mesh(geo, rockMat.clone());
  rock.material.color.offsetHSL(0, 0, (Math.random() - 0.5) * 0.15);
  rock.position.set(
    (Math.random() - 0.5) * (TANK.w - 5),
    -TANK.h / 2 + 0.5,
    (Math.random() - 0.5) * (TANK.d - 4)
  );
  rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
  rock.castShadow = rock.receiveShadow = true;
  scene.add(rock);
}

// Водоросли
const seaweeds = [];
for (let i = 0; i < 12; i++) {
  const height = 3 + Math.random() * 6;
  const baseX = (Math.random() - 0.5) * (TANK.w - 4);
  const baseZ = (Math.random() - 0.5) * (TANK.d - 3);
  const pts = [];
  for (let j = 0; j <= 5; j++) {
    pts.push(new THREE.Vector3(
      Math.sin(j * 0.8) * 0.4,
      (height / 5) * j,
      Math.cos(j * 0.6) * 0.3
    ));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const color = new THREE.Color().setHSL(0.28 + Math.random() * 0.12, 0.7, 0.3 + Math.random() * 0.15);
  const stem = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 16, 0.12 + Math.random() * 0.1, 6, false),
    new THREE.MeshStandardMaterial({ color, roughness: 0.8 })
  );
  stem.position.set(baseX, -TANK.h / 2 + 0.2, baseZ);
  stem.castShadow = true;
  stem.userData.phase = Math.random() * Math.PI * 2;
  stem.userData.speed = 0.5 + Math.random() * 0.8;
  scene.add(stem);
  seaweeds.push(stem);
}

// ============================================================
// РЫБКИ
// ============================================================
const COLOR_SCHEMES = [
  { body: 0xff7b25, fin: 0xffb066 }, // оранжевая
  { body: 0x2b6bff, fin: 0x7fb0ff }, // синяя
  { body: 0xffd700, fin: 0xff4422 }, // желто-красная
  { body: 0x9b59ff, fin: 0xcfa8ff }, // фиолетовая
  { body: 0xe63946, fin: 0xff8fa0 }, // красная
  { body: 0x2ecc71, fin: 0xa8f0c8 }, // зеленая
  { body: 0xff6fb0, fin: 0xffc2dd }, // розовая
  { body: 0xdaa520, fin: 0xffe9a0 }, // золотая
];

const fishArray = [];

function createFish() {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const group = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.4, metalness: 0.15 });
  const finMat = new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.6, transparent: true, opacity: 0.85, side: THREE.DoubleSide });

  // Тело
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
  body.scale.set(1.6, 0.85, 0.6);
  body.castShadow = true;
  group.add(body);

  // Глаза
  const eyeGeo = new THREE.SphereGeometry(0.2, 10, 8);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilGeo = new THREE.SphereGeometry(0.1, 8, 6);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });
  for (const side of [1, -1]) {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(1.15, 0.22, 0.42 * side);
    group.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(1.3, 0.22, 0.48 * side);
    group.add(pupil);
  }

  // Хвост (пивот на заднем крае)
  const tailPivot = new THREE.Group();
  tailPivot.position.set(-1.5, 0, 0);
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.75, 1.3, 4), finMat);
  tail.scale.set(0.15, 1, 0.9);
  tail.rotation.z = Math.PI / 2;
  tail.position.x = -0.6;
  tailPivot.add(tail);
  group.add(tailPivot);

  // Верхний плавник
  const dorsal = new THREE.Mesh(new THREE.ConeGeometry(0.45, 0.8, 4), finMat);
  dorsal.scale.set(1.4, 1, 0.15);
  dorsal.position.set(0.1, 0.75, 0);
  group.add(dorsal);

  // Боковые плавники
  const finGeo = new THREE.ConeGeometry(0.35, 0.7, 4);
  const leftFin = new THREE.Mesh(finGeo, finMat);
  leftFin.scale.set(1, 1, 0.12);
  leftFin.position.set(0.3, -0.25, 0.55);
  leftFin.rotation.x = 0.6;
  group.add(leftFin);
  const rightFin = new THREE.Mesh(finGeo, finMat);
  rightFin.scale.set(1, 1, 0.12);
  rightFin.position.set(0.3, -0.25, -0.55);
  rightFin.rotation.x = -0.6;
  group.add(rightFin);

  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  group.position.set(
    (Math.random() - 0.5) * (TANK.w - 8),
    (Math.random() - 0.5) * (TANK.h - 8),
    (Math.random() - 0.5) * (TANK.d - 6)
  );
  scene.add(group);

  fishArray.push({
    mesh: group,
    tail: tailPivot,
    leftFin, rightFin,
    velocity: new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.3, Math.random() - 0.5).normalize(),
    speed: 1.5 + Math.random() * 2.5,
    tailSpeed: 4 + Math.random() * 5,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 2.5 + Math.random() * 1.5,
    wanderTimer: Math.random() * 3,
    scale
  });
  document.getElementById('fish-count').textContent = fishArray.length;
}
for (let i = 0; i < 15; i++) createFish();

// ============================================================
// ПУЗЫРИ
// ============================================================
const bubbles = [];
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xcceeff, transparent: true, opacity: 0.35,
  transmission: 0.9, roughness: 0.1, metalness: 0
});
function addBubble(y) {
  const size = 0.12 + Math.random() * 0.28;
  const b = new THREE.Mesh(new THREE.SphereGeometry(size, 10, 8), bubbleMat);
  b.position.set(
    (Math.random() - 0.5) * (TANK.w - 4),
    y !== undefined ? y : -TANK.h / 2 + Math.random() * TANK.h,
    (Math.random() - 0.5) * (TANK.d - 3)
  );
  b.userData.speed = 1 + Math.random() * 2;
  b.userData.wobblePhase = Math.random() * Math.PI * 2;
  b.userData.wobbleAmp = 0.3 + Math.random() * 0.6;
  scene.add(b);
  bubbles.push(b);
}
for (let i = 0; i < 30; i++) addBubble();

// ============================================================
// КОРМ
// ============================================================
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.3, 8, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xc47a2c, roughness: 0.8 });

function addFood(point) {
  const f = new THREE.Mesh(foodGeo, foodMat);
  f.position.copy(point);
  f.position.y = Math.min(f.position.y, TANK.h / 2 - 1);
  f.userData.velY = 0;
  scene.add(f);
  foods.push(f);
  document.getElementById('food-count').textContent = foods.length;
}

// Кормление кликом (Raycaster)
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
  const hits = raycaster.intersectObject(glass);
  if (hits.length) {
    // Кормим в точке чуть внутри стекла
    const p = hits[0].point.clone();
    const dir = p.clone().sub(camera.position).normalize();
    p.addScaledVector(dir, 1.5);
    p.x = THREE.MathUtils.clamp(p.x, -TANK.w/2 + 1, TANK.w/2 - 1);
    p.y = THREE.MathUtils.clamp(p.y, -TANK.h/2 + 2, TANK.h/2 - 1);
    p.z = THREE.MathUtils.clamp(p.z, -TANK.d/2 + 1, TANK.d/2 - 1);
    addFood(p);
  } else {
    // Клик «в пустоту» — кормим в центре сверху
    addFood(new THREE.Vector3((Math.random()-0.5)*10, TANK.h/2 - 2, (Math.random()-0.5)*6));
  }
});

// ============================================================
// UI КНОПКИ
// ============================================================
document.getElementById('btn-fish').addEventListener('click', () => createFish());
document.getElementById('btn-bubbles').addEventListener('click', () => { for (let i = 0; i < 10; i++) addBubble(-TANK.h/2 + 0.5); });
let lightOn = true;
document.getElementById('btn-light').addEventListener('click', () => {
  lightOn = !lightOn;
  sunLight.intensity = lightOn ? 1.0 : 0.12;
});

// ============================================================
// ЦИКЛ АНИМАЦИИ
// ============================================================
const clock = new THREE.Clock();
const BOUNDS = { x: TANK.w/2 - 2.5, y: TANK.h/2 - 2.5, z: TANK.d/2 - 2.5 };
const tmpVec = new THREE.Vector3();

let fpsFrames = 0, fpsTime = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // --- Рыбки ---
  for (const fish of fishArray) {
    const pos = fish.mesh.position;
    const accel = new THREE.Vector3();

    // 1. Поиск корма (радиус 15)
    fish.targetFood = null;
    let bestDist = 15;
    for (const f of foods) {
      const d = pos.distanceTo(f.position);
      if (d < bestDist) { bestDist = d; fish.targetFood = f; }
    }
    if (fish.targetFood) {
      tmpVec.copy(fish.targetFood.position).sub(pos).normalize();
      accel.addScaledVector(tmpVec, fish.speed * 3);
      // Съедание
      if (bestDist < 1.2 * fish.scale + 0.4) {
        scene.remove(fish.targetFood);
        foods.splice(foods.indexOf(fish.targetFood), 1);
        document.getElementById('food-count').textContent = foods.length;
        fish.scale = Math.min(fish.scale * 1.05, 2.5); // рост +5%
        fish.targetFood = null;
      }
    }

    // 2. Избегание столкновений
    for (const other of fishArray) {
      if (other === fish) continue;
      const d = pos.distanceTo(other.mesh.position);
      if (d < fish.avoidanceRadius && d > 0.001) {
        tmpVec.copy(pos).sub(other.mesh.position).normalize();
        accel.addScaledVector(tmpVec, (fish.avoidanceRadius - d) * 2.5);
      }
    }

    // 3. Отталкивание от стен
    const wallForce = 4;
    if (pos.x >  BOUNDS.x) accel.x -= (pos.x - BOUNDS.x) * wallForce;
    if (pos.x < -BOUNDS.x) accel.x -= (pos.x + BOUNDS.x) * wallForce;
    if (pos.y >  BOUNDS.y) accel.y -= (pos.y - BOUNDS.y) * wallForce;
    if (pos.y < -BOUNDS.y) accel.y -= (pos.y + BOUNDS.y) * wallForce;
    if (pos.z >  BOUNDS.z) accel.z -= (pos.z - BOUNDS.z) * wallForce;
    if (pos.z < -BOUNDS.z) accel.z -= (pos.z + BOUNDS.z) * wallForce;

    // 4. Случайное блуждание
    fish.wanderTimer -= dt;
    if (fish.wanderTimer <= 0 && !fish.targetFood) {
      fish.wanderTimer = 2 + Math.random() * 3;
      accel.x += (Math.random() - 0.5) * fish.speed * 2;
      accel.y += (Math.random() - 0.5) * fish.speed;
      accel.z += (Math.random() - 0.5) * fish.speed * 2;
    }

    // Интеграция
    fish.velocity.addScaledVector(accel, dt);
    const maxSpeed = fish.targetFood ? fish.speed * 2 : fish.speed;
    if (fish.velocity.length() > maxSpeed) fish.velocity.setLength(maxSpeed);
    if (fish.velocity.length() < fish.speed * 0.3) fish.velocity.setLength(fish.speed * 0.3);
    pos.addScaledVector(fish.velocity, dt);

    // Жёсткий кламп
    pos.clamp(
      new THREE.Vector3(-BOUNDS.x, -BOUNDS.y, -BOUNDS.z),
      new THREE.Vector3(BOUNDS.x, BOUNDS.y, BOUNDS.z)
    );

    // Поворот в направлении движения
    const target = pos.clone().add(fish.velocity);
    fish.mesh.lookAt(target);
    // Модель смотрит в +X, а lookAt целится в -Z → компенсируем
    fish.mesh.rotateY(Math.PI / 2);

    // Анимация хвоста и плавников
    const wig = Math.sin(t * fish.tailSpeed + fish.phase);
    fish.tail.rotation.y = wig * 0.55;
    fish.leftFin.rotation.y = Math.sin(t * fish.tailSpeed * 0.8 + fish.phase) * 0.4;
    fish.rightFin.rotation.y = -Math.sin(t * fish.tailSpeed * 0.8 + fish.phase) * 0.4;

    // Плавное изменение масштаба (после роста)
    fish.mesh.scale.lerp(tmpVec.set(fish.scale, fish.scale, fish.scale), dt * 3);
  }

  // --- Корм (гравитация) ---
  for (let i = foods.length - 1; i >= 0; i--) {
    const f = foods[i];
    f.userData.velY -= 3.5 * dt;
    f.position.y += f.userData.velY * dt;
    f.position.x += Math.sin(t * 2 + i) * 0.15 * dt;
    f.rotation.y += dt * 2;
    if (f.position.y < -TANK.h / 2 + 0.4) {
      scene.remove(f);
      foods.splice(i, 1);
      document.getElementById('food-count').textContent = foods.length;
    }
  }

  // --- Пузыри ---
  for (const b of bubbles) {
    b.position.y += b.userData.speed * dt;
    b.position.x += Math.sin(t * 2 + b.userData.wobblePhase) * b.userData.wobbleAmp * dt;
    b.position.z += Math.cos(t * 1.6 + b.userData.wobblePhase) * b.userData.wobbleAmp * dt;
    if (b.position.y > TANK.h / 2 - 0.5) {
      b.position.y = -TANK.h / 2 + 0.5;
      b.position.x = (Math.random() - 0.5) * (TANK.w - 4);
      b.position.z = (Math.random() - 0.5) * (TANK.d - 3);
    }
  }

  // --- Водоросли ---
  for (const s of seaweeds) {
    s.rotation.x = Math.sin(t * s.userData.speed + s.userData.phase) * 0.12;
    s.rotation.z = Math.cos(t * s.userData.speed * 0.8 + s.userData.phase) * 0.1;
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

## ✨ Реализованные возможности

| Система | Детали |
|---|---|
| 🐠 **Рыбки** | 8 цветовых схем, глаза с зрачками, анимированные хвост/плавники, случайный масштаб 0.6–1.2 |
| 🧠 **ИИ** | Избегание столкновений, упругое отражение от стен, блуждание, преследование корма (радиус 15), рост +5% при поедании |
| 🌊 **Окружение** | Стекло с `transmission: 0.95`, wireframe-рамка, процедурное песчаное дно, 8 деформированных камней, 12 качающихся водорослей (TubeGeometry + CatmullRomCurve3) |
| 🫧 **Пузыри** | 30 штук, физика MeshPhysicalMaterial, синусоидальное покачивание, сброс у поверхности |
| 🍽️ **Корм** | Клик через Raycaster (с отличием клика от вращения камеры), гравитация, удаление на дне |
| 💡 **Свет** | Ambient + Directional с PCFSoftShadow 2048², 2 подводных PointLight, переключение кнопкой |
| 🎮 **Камера** | OrbitControls с damping, зум 10–60, ограничение polar angle |
| 🖥️ **UI** | Glassmorphism-панели, градиентный заголовок, FPS-счетчик, статистика, адаптивность |

**Лайфхак:** клик засчитывается как кормление только если мышь не сдвинулась больше чем на 6 пикселей — иначе это вращение камеры. Просто сохраните код в `aquarium.html` и откройте в браузере! 🎣