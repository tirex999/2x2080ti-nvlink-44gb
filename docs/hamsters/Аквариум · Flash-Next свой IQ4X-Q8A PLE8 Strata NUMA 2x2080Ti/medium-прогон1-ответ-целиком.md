# 🐠 3D Аквариум с Реалистичными Рыбками

Полная реализация в одном HTML-файле:

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
  canvas { display: block; }

  .panel {
    position: absolute;
    padding: 16px 20px;
    background: rgba(10, 30, 60, 0.55);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(100, 180, 255, 0.25);
    border-radius: 14px;
    color: #d0eaff;
    box-shadow: 0 8px 32px rgba(0, 20, 60, 0.5);
    z-index: 10;
  }
  #info-panel { top: 20px; left: 20px; max-width: 280px; }
  #stats-panel { top: 20px; right: 20px; text-align: right; }

  h1 {
    font-size: 20px;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #4dd0ff, #a0f0ff, #ffd76e);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .instructions { font-size: 12px; line-height: 1.7; opacity: 0.85; margin-bottom: 12px; }
  .instructions b { color: #7fdcff; }

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
    color: #fff;
    background: linear-gradient(135deg, #1976d2, #00acc1);
    box-shadow: 0 3px 10px rgba(0, 120, 200, 0.35);
    transition: all 0.2s;
  }
  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 18px rgba(0, 180, 255, 0.55);
    filter: brightness(1.15);
  }
  button:active { transform: translateY(0); }

  .stat { font-size: 14px; margin: 4px 0; }
  .stat span { color: #7fdcff; font-weight: bold; font-size: 17px; }

  @media (max-width: 640px) {
    #info-panel { max-width: 200px; padding: 10px; }
    h1 { font-size: 15px; }
    .instructions { display: none; }
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
    <b>Клик по аквариуму</b> — бросить корм 🍞
  </div>
  <button id="btnFish">➕ Добавить рыбку</button>
  <button id="btnBubbles">🫧 Больше пузырей</button>
  <button id="btnLight">💡 Свет вкл/выкл</button>
</div>

<div class="panel" id="stats-panel">
  <div class="stat">Рыбки: <span id="fishCount">15</span></div>
  <div class="stat">Корм: <span id="foodCount">0</span></div>
  <div class="stat">FPS: <span id="fps">60</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============ БАЗОВАЯ СЦЕНА ============
const TANK = { w: 36, h: 24, d: 20 };
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a2a5a, 0.012);

const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 200);
camera.position.set(28, 14, 32);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Градиентный фон
(function() {
  const c = document.createElement('canvas');
  c.width = 2; c.height = 256;
  const ctx = c.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, 256);
  g.addColorStop(0, '#1a4a8a');
  g.addColorStop(1, '#051530');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 2, 256);
  scene.background = new THREE.CanvasTexture(c);
})();

// ============ ОСВЕЩЕНИЕ ============
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sunLight = new THREE.DirectionalLight(0xfff5e0, 1.0);
sunLight.position.set(15, 30, 10);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -25;
sunLight.shadow.camera.right = 25;
sunLight.shadow.camera.top = 25;
sunLight.shadow.camera.bottom = -25;
scene.add(sunLight);

const blueLight1 = new THREE.PointLight(0x4488ff, 0.8, 50);
blueLight1.position.set(-12, 15, 0);
scene.add(blueLight1);

const blueLight2 = new THREE.PointLight(0x2266dd, 0.6, 50);
blueLight2.position.set(12, 5, 5);
scene.add(blueLight2);

// ============ АКВАРИУМ (СТЕКЛО) ============
const glassGeo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
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
const tank = new THREE.Mesh(glassGeo, glassMat);
scene.add(tank);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(glassGeo),
  new THREE.LineBasicMaterial({ color: 0x66bbff, transparent: true, opacity: 0.6 })
);
scene.add(edges);

// ============ ПЕСЧАНОЕ ДНО ============
const sandGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 40);
const posAttr = sandGeo.attributes.position;
for (let i = 0; i < posAttr.count; i++) {
  posAttr.setZ(i, Math.random() * 0.5 + Math.sin(posAttr.getX(i) * 0.8) * 0.2);
}
sandGeo.computeVertexNormals();
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({
  color: 0xd9b98a, roughness: 0.95
}));
sand.rotation.x = -Math.PI / 2;
sand.position.y = -TANK.h / 2 + 0.2;
sand.receiveShadow = true;
scene.add(sand);

// ============ КАМНИ ============
for (let i = 0; i < 8; i++) {
  const geo = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.4, 0);
  const p = geo.attributes.position;
  for (let j = 0; j < p.count; j++) {
    p.setXYZ(j,
      p.getX(j) * (0.7 + Math.random() * 0.6),
      p.getY(j) * (0.7 + Math.random() * 0.6),
      p.getZ(j) * (0.7 + Math.random() * 0.6));
  }
  geo.computeVertexNormals();
  const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.08, 0.1, 0.25 + Math.random() * 0.2),
    roughness: 0.9
  }));
  rock.position.set(
    (Math.random() - 0.5) * (TANK.w - 6),
    -TANK.h / 2 + 0.8,
    (Math.random() - 0.5) * (TANK.d - 6)
  );
  rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
  rock.castShadow = true;
  rock.receiveShadow = true;
  scene.add(rock);
}

// ============ ВОДОРОСЛИ ============
const seaweeds = [];
for (let i = 0; i < 12; i++) {
  const height = 4 + Math.random() * 7;
  const baseX = (Math.random() - 0.5) * (TANK.w - 4);
  const baseZ = (Math.random() - 0.5) * (TANK.d - 4);
  const pts = [];
  for (let j = 0; j <= 6; j++) {
    pts.push(new THREE.Vector3(
      Math.sin(j * 0.9) * 0.4,
      (height / 6) * j,
      Math.cos(j * 0.7) * 0.3
    ));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const weed = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 12, 0.15, 6, false),
    new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(0.28 + Math.random() * 0.12, 0.7, 0.3 + Math.random() * 0.15),
      roughness: 0.8
    })
  );
  weed.position.set(baseX, -TANK.h / 2 + 0.3, baseZ);
  weed.castShadow = true;
  weed.userData = { phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.8 };
  scene.add(weed);
  seaweeds.push(weed);
}

// ============ ПУЗЫРИ ============
const bubbles = [];
const bubbleGeo = new THREE.SphereGeometry(0.25, 10, 10);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xffffff, transparent: true, opacity: 0.35,
  transmission: 0.9, roughness: 0.1, metalness: 0
});
function addBubble() {
  const b = new THREE.Mesh(bubbleGeo, bubbleMat);
  const s = 0.4 + Math.random() * 1.2;
  b.scale.setScalar(s);
  b.position.set(
    (Math.random() - 0.5) * (TANK.w - 4),
    -TANK.h / 2 + Math.random() * TANK.h,
    (Math.random() - 0.5) * (TANK.d - 4)
  );
  b.userData = { speed: 1.5 + Math.random() * 2, phase: Math.random() * Math.PI * 2, ox: b.position.x, oz: b.position.z };
  scene.add(b);
  bubbles.push(b);
}
for (let i = 0; i < 30; i++) addBubble();

// ============ РЫБКИ ============
const COLOR_SCHEMES = [
  { body: 0xff7722, fin: 0xffaa55 }, // оранжевая
  { body: 0x2266ff, fin: 0x66aaff }, // синяя
  { body: 0xffdd00, fin: 0xff4422 }, // желто-красная
  { body: 0x9944dd, fin: 0xcc88ff }, // фиолетовая
  { body: 0xee2233, fin: 0xff7788 }, // красная
  { body: 0x33bb55, fin: 0x88ee99 }, // зеленая
  { body: 0xff66aa, fin: 0xffaacc }, // розовая
  { body: 0xddaa33, fin: 0xffee88 }, // золотая
];

const fishArray = [];

function createFish() {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const group = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.4, metalness: 0.2 });
  const finMat = new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.6, transparent: true, opacity: 0.85, side: THREE.DoubleSide });

  // Тело
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
  body.scale.set(1.6, 0.85, 0.6);
  body.castShadow = true;
  group.add(body);

  // Глаза
  const eyeWhiteGeo = new THREE.SphereGeometry(0.22, 10, 8);
  const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
  const pupilGeo = new THREE.SphereGeometry(0.11, 8, 6);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
  [-1, 1].forEach(side => {
    const eye = new THREE.Mesh(eyeWhiteGeo, eyeWhiteMat);
    eye.position.set(1.15, 0.22, side * 0.42);
    group.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(1.32, 0.22, side * 0.48);
    group.add(pupil);
  });

  // Хвост
  const tailGeo = new THREE.ConeGeometry(0.7, 1.3, 4);
  const tail = new THREE.Mesh(tailGeo, finMat);
  tail.position.set(-1.9, 0, 0);
  tail.rotation.z = Math.PI / 2;
  tail.scale.set(0.25, 1, 1.4);
  group.add(tail);

  // Верхний плавник
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.5, 1.0, 4), finMat);
  topFin.position.set(0.1, 0.85, 0);
  topFin.scale.set(0.2, 1, 0.8);
  group.add(topFin);

  // Боковые плавники
  const finGeo = new THREE.ConeGeometry(0.4, 0.8, 4);
  const leftFin = new THREE.Mesh(finGeo, finMat);
  leftFin.position.set(0.4, -0.2, 0.55);
  leftFin.rotation.x = -Math.PI / 2.5;
  leftFin.scale.set(0.2, 1, 0.7);
  group.add(leftFin);

  const rightFin = new THREE.Mesh(finGeo, finMat);
  rightFin.position.set(0.4, -0.2, -0.55);
  rightFin.rotation.x = Math.PI / 2.5;
  rightFin.scale.set(0.2, 1, 0.7);
  group.add(rightFin);

  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  group.position.set(
    (Math.random() - 0.5) * (TANK.w - 8),
    (Math.random() - 0.3) * (TANK.h - 6),
    (Math.random() - 0.5) * (TANK.d - 6)
  );
  scene.add(group);

  fishArray.push({
    mesh: group,
    tail, leftFin, rightFin,
    velocity: new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.3, Math.random() - 0.5).normalize(),
    speed: 1.5 + Math.random() * 2.5,
    tailSpeed: 4 + Math.random() * 4,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 3 + Math.random() * 2,
    scale: scale,
    wanderTimer: Math.random() * 3
  });
  document.getElementById('fishCount').textContent = fishArray.length;
}
for (let i = 0; i < 15; i++) createFish();

// ============ КОРМ ============
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.3, 8, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xcc8844, roughness: 0.8 });

function dropFood(point) {
  const f = new THREE.Mesh(foodGeo, foodMat);
  f.position.copy(point);
  f.position.y = TANK.h / 2 - 1;
  f.userData = { vy: 0 };
  scene.add(f);
  foods.push(f);
  document.getElementById('foodCount').textContent = foods.length;
}

// Клик по аквариуму
const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();
let mouseDownPos = null;

renderer.domElement.addEventListener('pointerdown', e => {
  mouseDownPos = { x: e.clientX, y: e.clientY };
});
renderer.domElement.addEventListener('pointerup', e => {
  if (e.button !== 0 || !mouseDownPos) return;
  const dx = e.clientX - mouseDownPos.x, dy = e.clientY - mouseDownPos.y;
  mouseDownPos = null;
  if (Math.hypot(dx, dy) > 5) return; // это было вращение камеры
  if (e.target !== renderer.domElement) return;

  mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  raycaster.setFromCamera(mouseNDC, camera);
  const hits = raycaster.intersectObject(tank);
  if (hits.length > 0) dropFood(hits[0].point);
});

// ============ УПРАВЛЕНИЕ КАМЕРОЙ ============
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

// ============ КНОПКИ UI ============
document.getElementById('btnFish').onclick = () => createFish();
document.getElementById('btnBubbles').onclick = () => { for (let i = 0; i < 10; i++) addBubble(); };
let lightOn = true;
document.getElementById('btnLight').onclick = () => {
  lightOn = !lightOn;
  sunLight.intensity = lightOn ? 1.0 : 0.1;
};

// ============ АНИМАЦИЯ ============
const clock = new THREE.Clock();
let fpsTime = 0, fpsFrames = 0;
const _tmp = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // --- Рыбки ---
  const halfW = TANK.w / 2 - 3, halfH = TANK.h / 2 - 2.5, halfD = TANK.d / 2 - 2;

  for (const fish of fishArray) {
    const m = fish.mesh;

    // Блуждание
    fish.wanderTimer -= dt;
    if (fish.wanderTimer <= 0) {
      fish.wanderTimer = 2 + Math.random() * 3;
      fish.velocity.x += (Math.random() - 0.5) * 0.8;
      fish.velocity.y += (Math.random() - 0.5) * 0.4;
      fish.velocity.z += (Math.random() - 0.5) * 0.8;
    }

    // Преследование корма
    fish.targetFood = null;
    let bestDist = 15;
    for (const f of foods) {
      const d = m.position.distanceTo(f.position);
      if (d < bestDist) { bestDist = d; fish.targetFood = f; }
    }
    if (fish.targetFood) {
      _tmp.copy(fish.targetFood.position).sub(m.position).normalize();
      fish.velocity.lerp(_tmp, 0.08);
      // Съедание
      if (m.position.distanceTo(fish.targetFood.position) < 1.2 + fish.scale) {
        scene.remove(fish.targetFood);
        foods.splice(foods.indexOf(fish.targetFood), 1);
        fish.scale = Math.min(fish.scale * 1.05, 2.0);
        fish.targetFood = null;
        document.getElementById('foodCount').textContent = foods.length;
      }
    }

    // Избегание других рыбок
    for (const other of fishArray) {
      if (other === fish) continue;
      const d = m.position.distanceTo(other.mesh.position);
      if (d < fish.avoidanceRadius && d > 0.01) {
        _tmp.copy(m.position).sub(other.mesh.position).normalize().multiplyScalar(0.05);
        fish.velocity.add(_tmp);
      }
    }

    // Отталкивание от стен
    const soft = 0.06;
    if (m.position.x > halfW) fish.velocity.x -= soft;
    if (m.position.x < -halfW) fish.velocity.x += soft;
    if (m.position.y > halfH) fish.velocity.y -= soft;
    if (m.position.y < -halfH + 1.5) fish.velocity.y += soft;
    if (m.position.z > halfD) fish.velocity.z -= soft;
    if (m.position.z < -halfD) fish.velocity.z += soft;

    fish.velocity.normalize();
    m.position.addScaledVector(fish.velocity, fish.speed * dt);

    // Жесткое отражение на границах
    if (Math.abs(m.position.x) > halfW + 1) fish.velocity.x *= -1;
    if (Math.abs(m.position.y) > halfH + 1) fish.velocity.y *= -1;
    if (Math.abs(m.position.z) > halfD + 1) fish.velocity.z *= -1;

    // Поворот в направлении движения
    const targetYaw = Math.atan2(-fish.velocity.z, fish.velocity.x);
    let dy = targetYaw - m.rotation.y;
    while (dy > Math.PI) dy -= Math.PI * 2;
    while (dy < -Math.PI) dy += Math.PI * 2;
    m.rotation.y += dy * 0.1;
    m.rotation.z = Math.atan2(fish.velocity.y, 1) * 0.5;

    // Анимация хвоста и плавников
    const wig = Math.sin(t * fish.tailSpeed + fish.phase);
    fish.tail.rotation.y = wig * 0.6;
    fish.leftFin.rotation.z = Math.sin(t * fish.tailSpeed * 0.7 + fish.phase) * 0.4;
    fish.rightFin.rotation.z = -Math.sin(t * fish.tailSpeed * 0.7 + fish.phase) * 0.4;

    // Плавный рост
    const cs = m.scale.x;
    if (cs < fish.scale) m.scale.setScalar(Math.min(cs + dt * 0.1, fish.scale));
  }

  // --- Корм (гравитация) ---
  for (let i = foods.length - 1; i >= 0; i--) {
    const f = foods[i];
    f.userData.vy -= 3 * dt;
    f.position.y += f.userData.vy * dt;
    f.position.x += Math.sin(t * 3 + i) * 0.005;
    f.rotation.y += dt * 2;
    if (f.position.y < -TANK.h / 2 + 0.6) {
      scene.remove(f);
      foods.splice(i, 1);
      document.getElementById('foodCount').textContent = foods.length;
    }
  }

  // --- Пузыри ---
  for (const b of bubbles) {
    b.position.y += b.userData.speed * dt;
    b.position.x = b.userData.ox + Math.sin(t * 2 + b.userData.phase) * 0.5;
    b.position.z = b.userData.oz + Math.cos(t * 1.5 + b.userData.phase) * 0.4;
    if (b.position.y > TANK.h / 2 - 0.5) {
      b.position.y = -TANK.h / 2 + 0.5;
      b.userData.ox = (Math.random() - 0.5) * (TANK.w - 4);
      b.userData.oz = (Math.random() - 0.5) * (TANK.d - 4);
    }
  }

  // --- Водоросли ---
  for (const w of seaweeds) {
    w.rotation.x = Math.sin(t * w.userData.speed + w.userData.phase) * 0.12;
    w.rotation.z = Math.cos(t * w.userData.speed * 0.8 + w.userData.phase) * 0.1;
  }

  controls.update();
  renderer.render(scene, camera);

  // FPS
  fpsFrames++;
  fpsTime += dt;
  if (fpsTime >= 0.5) {
    document.getElementById('fps').textContent = Math.round(fpsFrames / fpsTime);
    fpsFrames = 0; fpsTime = 0;
  }
}
animate();

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
| **🐠 Рыбки** | 15 штук, 8 цветовых схем, тело + глаза с зрачками + хвост + 3 плавника, случайный масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, мягкое отражение от стен, блуждание, преследование корма (радиус 15), рост +5% при поедании |
| **🌊 Окружение** | Стеклянный бак 36×24×20 с `transmission: 0.95` и wireframe-рамкой, процедурное песчаное дно, 8 деформированных камней, 12 качающихся водорослей (TubeGeometry + CatmullRomCurve3) |
| **🫧 Пузыри** | 30 штук, стеклянный материал, синусоидальное покачивание, сброс у поверхности |
| **🍽️ Корм** | Клик (с отличием от вращения камеры!), гравитация, поедание, исчезновение на дне |
| **💡 Свет** | Ambient + Directional с PCFSoft-тенями 2048², 2 голубых PointLight, переключение кнопкой |
| **🎥 Камера** | OrbitControls с damping, зум 10–60, ограничение polar angle |
| **🖥️ UI** | Glassmorphism-панели, градиентный заголовок, статистика рыбок/корма/FPS, 3 кнопки |

**Совет:** клик считается кормлением только если мышь не сдвинулась больше чем на 5px — это отличает кормление от вращения камеры. Просто сохраните код в `aquarium.html` и откройте в браузере! 🐟