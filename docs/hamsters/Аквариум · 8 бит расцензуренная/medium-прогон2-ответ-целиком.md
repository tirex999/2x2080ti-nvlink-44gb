

# 🐠 3D Аквариум с Реалистичными Рыбками

Готовый файл `aquarium.html` — сохраните и откройте в браузере:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; }
  canvas { display: block; }

  .panel {
    position: absolute;
    background: rgba(10, 30, 60, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(120, 200, 255, 0.25);
    border-radius: 14px;
    padding: 16px 20px;
    color: #d8ecff;
    box-shadow: 0 8px 32px rgba(0, 40, 100, 0.4), inset 0 0 20px rgba(80, 160, 255, 0.05);
    user-select: none;
  }

  #info { top: 20px; left: 20px; max-width: 280px; }
  #info h1 {
    font-size: 20px; margin-bottom: 10px;
    background: linear-gradient(90deg, #4fc3f7, #81d4fa, #fff59d);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  #info ul { list-style: none; font-size: 12px; line-height: 1.7; opacity: 0.85; }
  #info li::before { content: "▸ "; color: #4fc3f7; }

  #stats { top: 20px; right: 20px; min-width: 170px; font-size: 14px; }
  #stats .row { display: flex; justify-content: space-between; margin-bottom: 6px; }
  #stats .val { color: #ffd54f; font-weight: bold; }

  .btn-row { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
  button {
    flex: 1;
    padding: 9px 12px;
    border: none; border-radius: 8px;
    background: linear-gradient(135deg, #1e88e5, #00acc1);
    color: #fff; font-size: 12px; font-weight: 600;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s, filter 0.15s;
    box-shadow: 0 3px 10px rgba(0, 120, 200, 0.4);
  }
  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 180, 255, 0.6);
    filter: brightness(1.15);
  }
  button:active { transform: translateY(0); }

  @media (max-width: 640px) {
    #info { max-width: 200px; padding: 10px 14px; }
    #info ul { display: none; }
  }
</style>
</head>
<body>

<div class="panel" id="info">
  <h1>🐠 3D Аквариум</h1>
  <ul>
    <li>ЛКМ + движение — вращение камеры</li>
    <li>ПКМ + движение — панорама</li>
    <li>Колесо — зум</li>
    <li><b>Клик по воде</b> — покормить рыбок 🍤</li>
  </ul>
  <div class="btn-row">
    <button id="btnFish">+ Рыбка</button>
    <button id="btnBubbles">+ Пузыри</button>
  </div>
  <div class="btn-row">
    <button id="btnLight">💡 Свет: Вкл</button>
  </div>
</div>

<div class="panel" id="stats">
  <div class="row"><span>🐟 Рыбки:</span><span class="val" id="fishCount">15</span></div>
  <div class="row"><span>🍤 Корм:</span><span class="val" id="foodCount">0</span></div>
  <div class="row"><span>⚡ FPS:</span><span class="val" id="fps">--</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* ============================================================
   ОСНОВА: сцена, камера, рендерер
============================================================ */
const TANK = { W: 36, H: 24, D: 20 };           // размеры аквариума
const HW = TANK.W / 2, HH = TANK.H / 2, HD = TANK.D / 2;

const scene = new THREE.Scene();

// Градиентный фон (canvas-текстура)
(function makeBg() {
  const c = document.createElement('canvas');
  c.width = 2; c.height = 256;
  const ctx = c.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, 256);
  g.addColorStop(0, '#0a2a5c');
  g.addColorStop(0.6, '#073061');
  g.addColorStop(1, '#031833');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 2, 256);
  scene.background = new THREE.CanvasTexture(c);
})();

scene.fog = new THREE.FogExp2(0x073061, 0.012);   // имитация воды

const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 200);
camera.position.set(0, 18, 42);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 11, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

/* ============================================================
   ОСВЕЩЕНИЕ
============================================================ */
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sun = new THREE.DirectionalLight(0xfff4e0, 1.1);
sun.position.set(12, 34, 14);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -25;  sun.shadow.camera.right = 25;
sun.shadow.camera.top = 25;    sun.shadow.camera.bottom = -25;
sun.shadow.camera.far = 80;
scene.add(sun);

const pl1 = new THREE.PointLight(0x40c4ff, 0.6, 40);
pl1.position.set(-12, 16, 0);
scene.add(pl1);
const pl2 = new THREE.PointLight(0x2060ff, 0.5, 40);
pl2.position.set(12, 14, 0);
scene.add(pl2);

/* ============================================================
   ОКРУЖЕНИЕ: стекло, песок, камни, водоросли
============================================================ */
// --- Стеклянный контейнер ---
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xbfe8ff, transmission: 0.95, transparent: true,
  opacity: 0.25, roughness: 0.05, metalness: 0,
  side: THREE.DoubleSide, depthWrite: false
});
const glassGeo = new THREE.BoxGeometry(TANK.W, TANK.H, TANK.D);
const glass = new THREE.Mesh(glassGeo, glassMat);
glass.position.y = HH;
scene.add(glass);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(glassGeo),
  new THREE.LineBasicMaterial({ color: 0x9fdcff, transparent: true, opacity: 0.5 })
);
edges.position.copy(glass.position);
scene.add(edges);

// --- Песчаное дно с процедурными неровностями ---
const sandGeo = new THREE.PlaneGeometry(TANK.W, TANK.D, 36, 20);
sandGeo.rotateX(-Math.PI / 2);
{
  const pos = sandGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), z = pos.getZ(i);
    pos.setY(i,
      Math.sin(x * 0.5) * Math.cos(z * 0.7) * 0.25 +
      Math.sin(x * 1.7 + z * 1.3) * 0.12);
  }
  sandGeo.computeVertexNormals();
}
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({
  color: 0xd9c08a, roughness: 0.95
}));
sand.receiveShadow = true;
scene.add(sand);

// --- Декоративные камни (деформированные додекаэдры) ---
for (let i = 0; i < 8; i++) {
  const geo = new THREE.DodecahedronGeometry(1, 0);
  const p = geo.attributes.position;
  for (let v = 0; v < p.count; v++) {
    p.setXYZ(v,
      p.getX(v) * (0.7 + Math.random() * 0.6),
      p.getY(v) * (0.5 + Math.random() * 0.4),
      p.getZ(v) * (0.7 + Math.random() * 0.6));
  }
  geo.computeVertexNormals();
  const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.15, 0.3 + Math.random() * 0.2),
    roughness: 0.9
  }));
  rock.position.set((Math.random() - 0.5) * (TANK.W - 6), 0.4, (Math.random() - 0.5) * (TANK.D - 4));
  rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
  rock.scale.setScalar(0.6 + Math.random() * 1.2);
  rock.castShadow = rock.receiveShadow = true;
  scene.add(rock);
}

// --- Водоросли (TubeGeometry + CatmullRomCurve3) ---
const weeds = [];
for (let i = 0; i < 12; i++) {
  const pts = [];
  const h = 3 + Math.random() * 4;
  const bx = (Math.random() - 0.5) * (TANK.W - 6);
  const bz = (Math.random() - 0.5) * (TANK.D - 4);
  for (let j = 0; j <= 5; j++) {
    const t = j / 5;
    pts.push(new THREE.Vector3(
      bx + Math.sin(t * 4 + i) * 0.5 * t,
      t * h,
      bz + Math.cos(t * 3 + i) * 0.5 * t));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const weed = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 10, 0.14, 5),
    new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(0.32 + Math.random() * 0.1, 0.7, 0.3 + Math.random() * 0.15),
      roughness: 0.8
    }));
  weed.castShadow = true;
  weed.userData = { phase: Math.random() * Math.PI * 2, speed: 0.6 + Math.random() * 0.8, bx, bz };
  scene.add(weed);
  weeds.push(weed);
}

/* ============================================================
   БУБЛЬКИ
============================================================ */
const bubbles = [];
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xcfeaff, transmission: 0.9, transparent: true, opacity: 0.35,
  roughness: 0, metalness: 0, depthWrite: false
});
function spawnBubble() {
  const r = 0.1 + Math.random() * 0.2;
  const m = new THREE.Mesh(new THREE.SphereGeometry(r, 8, 8), bubbleMat);
  m.position.set(
    (Math.random() - 0.5) * (TANK.W - 4),
    0.5 + Math.random() * TANK.H * 0.5,
    (Math.random() - 0.5) * (TANK.D - 4));
  scene.add(m);
  bubbles.push({
    mesh: m, baseX: m.position.x, baseZ: m.position.z,
    speed: 1.5 + Math.random() * 2.5,
    phase: Math.random() * Math.PI * 2, amp: 0.3 + Math.random() * 0.5
  });
}
for (let i = 0; i < 30; i++) spawnBubble();

/* ============================================================
   РЫБКИ
============================================================ */
const COLOR_SCHEMES = [
  { body: 0xff8c1a, fin: 0xffb347 },   // оранжевая
  { body: 0x2196f3, fin: 0x64b5f6 },   // синяя
  { body: 0xffd54f, fin: 0xef5350 },   // жёлто-красная
  { body: 0x9c27b0, fin: 0xce93d8 },   // фиолетовая
  { body: 0xe53935, fin: 0xff8a65 },   // красная
  { body: 0x43a047, fin: 0xa5d6a7 },   // зелёная
  { body: 0xec407a, fin: 0xf8bbd0 },   // розовая
  { body: 0xffc107, fin: 0xfff176 }    // золотая
];

const fishArray = [];
const _v1 = new THREE.Vector3(), _v2 = new THREE.Vector3();

function createFish() {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const g = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.35, metalness: 0.15 });
  const finMat  = new THREE.MeshStandardMaterial({
    color: scheme.fin, roughness: 0.5, transparent: true, opacity: 0.85, side: THREE.DoubleSide
  });

  // Тело — вытянутая сфера (вдоль Z)
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
  body.scale.set(0.35, 0.55, 1.15);
  body.castShadow = true;
  g.add(body);

  // Хвост — плоский конус, вращается в своей группе
  const tailPivot = new THREE.Group();
  tailPivot.position.set(0, 0, -1.05);
  const tailGeo = new THREE.ConeGeometry(0.5, 0.9, 8);
  tailGeo.rotateX(Math.PI / 2);   // вершина к телу (+Z)
  const tail = new THREE.Mesh(tailGeo, finMat);
  tail.scale.set(0.12, 0.7, 1);
  tail.position.z = -0.45;
  tail.castShadow = true;
  tailPivot.add(tail);
  g.add(tailPivot);

  // Верхний плавник
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.6, 6), finMat);
  topFin.scale.set(0.1, 1, 0.7);
  topFin.position.set(0, 0.5, -0.1);
  g.add(topFin);

  // Боковые плавники
  const finGeo = new THREE.SphereGeometry(0.35, 8, 6);
  const leftFin = new THREE.Mesh(finGeo, finMat);
  leftFin.scale.set(0.08, 0.5, 0.9);
  leftFin.position.set(-0.38, -0.05, 0);
  g.add(leftFin);
  const rightFin = new THREE.Mesh(finGeo, finMat);
  rightFin.scale.set(0.08, 0.5, 0.9);
  rightFin.position.set(0.38, -0.05, 0);
  g.add(rightFin);

  // Глаза
  const eyeWhite = new THREE.Mesh(new THREE.SphereGeometry(0.14, 8, 8),
    new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 }));
  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8),
    new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 }));
  [-1, 1].forEach(s => {
    const e = eyeWhite.clone();
    e.position.set(s * 0.28, 0.18, 0.85);
    const p = pupil.clone();
    p.position.set(s * 0.28, 0.18, 0.97);
    g.add(e, p);
  });

  // Индивидуальные параметры
  const scale = 0.6 + Math.random() * 0.6;
  g.scale.setScalar(scale);
  g.position.set(
    (Math.random() - 0.5) * (TANK.W - 8),
    3 + Math.random() * (TANK.H - 8),
    (Math.random() - 0.5) * (TANK.D - 6));
  scene.add(g);

  fishArray.push({
    mesh: g, tail: tailPivot, leftFin, rightFin,
    velocity: new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).normalize(),
    speed: 2.5 + Math.random() * 2.5,
    tailSpeed: 6 + Math.random() * 5,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 3 + Math.random() * 1.5,
    wanderT: 1 + Math.random() * 3,
    baseScale: scale
  });
}
for (let i = 0; i < 15; i++) createFish();

/* ============================================================
   СИСТЕМА КОРМЛЕНИЯ
============================================================ */
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.22, 8, 8);
const foodMat = new THREE.MeshStandardMaterial({ color: 0x8d5524, roughness: 0.8 });

function dropFood(point) {
  const f = new THREE.Mesh(foodGeo, foodMat);
  f.position.copy(point).clamp(
    new THREE.Vector3(-HW + 1, 1, -HD + 1),
    new THREE.Vector3(HW - 1, TANK.H - 1, HD - 1));
  f.castShadow = true;
  scene.add(f);
  foods.push({ mesh: f, vy: 0, active: true });
}

const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();
renderer.domElement.addEventListener('pointerdown', e => {
  if (e.button !== 0) return;
  mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  raycaster.setFromCamera(mouseNDC, camera);
  const hit = raycaster.intersectObject(glass)[0];
  if (hit) {
    // точку уводим внутрь аквариума
    const p = hit.point.clone().lerp(new THREE.Vector3(0, HH, 0), 0.35);
    dropFood(p);
  }
});

/* ============================================================
   UI
============================================================ */
const elFish = document.getElementById('fishCount');
const elFood = document.getElementById('foodCount');
const elFps  = document.getElementById('fps');
const btnLight = document.getElementById('btnLight');
let lightOn = true;

document.getElementById('btnFish').onclick = () => { createFish(); elFish.textContent = fishArray.length; };
document.getElementById('btnBubbles').onclick = () => { for (let i = 0; i < 10; i++) spawnBubble(); };
btnLight.onclick = () => {
  lightOn = !lightOn;
  sun.intensity = lightOn ? 1.1 : 0.25;
  btnLight.textContent = lightOn ? '💡 Свет: Вкл' : '🌙 Свет: Выкл';
};

/* ============================================================
   ГЛАВНЫЙ ЦИКЛ
============================================================ */
const clock = new THREE.Clock();
let frames = 0, fpsTimer = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  /* ---- Рыбки: ИИ ---- */
  for (const f of fishArray) {
    const p = f.mesh.position;

    // Избегание столкновений
    for (const o of fishArray) {
      if (o === f) continue;
      _v1.subVectors(p, o.mesh.position);
      const d = _v1.length();
      if (d < f.avoidanceRadius && d > 0.001) {
        f.velocity.addScaledVector(_v1.normalize(), (f.avoidanceRadius - d) * 3 * dt);
      }
    }

    // Отражение от стен
    const M = 1.8, K = 4 * dt;
    if (p.x < -HW + M) f.velocity.x += K;
    if (p.x >  HW - M) f.velocity.x -= K;
    if (p.y <  1.5)     f.velocity.y += K;
    if (p.y >  TANK.H - 1.5) f.velocity.y -= K;
    if (p.z < -HD + M) f.velocity.z += K;
    if (p.z >  HD - M) f.velocity.z -= K;

    // Случайное блуждание
    f.wanderT -= dt;
    if (f.wanderT <= 0) {
      f.velocity.x += (Math.random() - 0.5);
      f.velocity.y += (Math.random() - 0.5) * 0.5;
      f.velocity.z += (Math.random() - 0.5);
      f.wanderT = 2 + Math.random() * 3;
    }

    // Поиск / погоня за кормом
    if (f.targetFood && !f.targetFood.active) f.targetFood = null;
    if (!f.targetFood) {
      let best = 15;
      for (const fd of foods) {
        const d = p.distanceTo(fd.mesh.position);
        if (d < best) { best = d; f.targetFood = fd; }
      }
    }
    let mult = 1;
    if (f.targetFood) {
      _v1.subVectors(f.targetFood.mesh.position, p).normalize();
      f.velocity.lerp(_v1, 2.5 * dt).normalize();
      mult = 1.6;
      // Съедание
      if (p.distanceTo(f.targetFood.mesh.position) < 1.2 * f.mesh.scale.x) {
        f.targetFood.active = false;
        scene.remove(f.targetFood.mesh);
        foods.splice(foods.indexOf(f.targetFood), 1);
        f.targetFood = null;
        // Рост на 5%
        const ns = Math.min(f.baseScale * 2.2, f.mesh.scale.x * 1.05);
        f.mesh.scale.setScalar(ns);
      }
    }

    f.velocity.setLength(f.speed * mult);
    p.addScaledVector(f.velocity, dt);
    p.clamp(new THREE.Vector3(-HW + 1, 1, -HD + 1), new THREE.Vector3(HW - 1, TANK.H - 1, HD - 1));

    // Плавный поворот в направлении движения
    _v2.copy(p).add(f.velocity);
    const m4 = new THREE.Matrix4().lookAt(p, _v2, new THREE.Vector3(0, 1, 0));
    const q = new THREE.Quaternion().setFromRotationMatrix(m4);
    f.mesh.quaternion.slerp(q, Math.min(1, 6 * dt));

    // Анимация хвоста и плавников
    f.tail.rotation.y = Math.sin(t * f.tailSpeed * mult + f.phase) * 0.55;
    f.leftFin.rotation.z  =  0.25 + Math.sin(t * f.tailSpeed + f.phase) * 0.3;
    f.rightFin.rotation.z = -0.25 - Math.sin(t * f.tailSpeed + f.phase) * 0.3;
  }

  /* ---- Корм: гравитация ---- */
  for (let i = foods.length - 1; i >= 0; i--) {
    const fd = foods[i];
    fd.vy -= 3 * dt;                       // замедленная гравитация в воде
    fd.mesh.position.y += fd.vy * dt;
    if (fd.mesh.position.y < 0.35) {       // достиг дна — растворяется
      scene.remove(fd.mesh);
      foods.splice(i, 1);
    }
  }

  /* ---- Бубльки ---- */
  for (const b of bubbles) {
    b.mesh.position.y += b.speed * dt;
    b.mesh.position.x = b.baseX + Math.sin(t * 1.5 + b.phase) * b.amp;
    b.mesh.position.z = b.baseZ + Math.cos(t * 1.2 + b.phase) * b.amp * 0.6;
    if (b.mesh.position.y > TANK.H - 0.5) {
      b.mesh.position.y = 0.5;
      b.baseX = (Math.random() - 0.5) * (TANK.W - 4);
      b.baseZ = (Math.random() - 0.5) * (TANK.D - 4);
      b.mesh.position.x = b.baseX;
      b.mesh.position.z = b.baseZ;
    }
  }

  /* ---- Водоросли: покачивание ---- */
  for (const w of weeds) {
    w.rotation.x = Math.sin(t * w.userData.speed + w.userData.phase) * 0.07;
    w.rotation.z = Math.cos(t * w.userData.speed * 0.8 + w.userData.phase) * 0.07;
  }

  /* ---- Подводные огни: лёгкое мерцание ---- */
  pl1.intensity = 0.55 + Math.sin(t * 0.7) * 0.1;
  pl2.intensity = 0.45 + Math.cos(t * 0.9) * 0.1;

  controls.update();
  renderer.render(scene, camera);

  /* ---- Статистика ---- */
  frames++;
  fpsTimer += dt;
  if (fpsTimer >= 1) {
    elFps.textContent = frames;
    elFood.textContent = foods.length;
    elFish.textContent = fishArray.length;
    frames = 0; fpsTimer = 0;
  }
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

## ✅ Что реализовано

| Раздел | Детали |
|---|---|
| **Рыбки** | 15 шт., 8 цветовых схем, тело/глаза/хвост/3 плавника, масштаб 0.6–1.2, индивидуальный хвост-цикл |
| **ИИ** | Отталкивание (O(n²)), мягкое отражение от стен, блуждание с таймером, погоня за кормом (радиус 15), рост +5% со штрафом скорости погони ×1.6 |
| **Окружение** | Стекло с `transmission: 0.95` + wireframe-рамка, песок с процедурным рельефом, 8 деформированных камней, 12 водорослей из `TubeGeometry` |
| **Пузыри** | 30 шт., физический материал, синусоидальное покачивание, респаун у дна |
| **Кормление** | Raycast по стеклу → точка смещается внутрь (lerp к центру 35%), замедленная гравитация, удаление у дна |
| **Свет** | Ambient + Directional (тени 2048², PCFSoft) + 2 мерцающих PointLight, туман `FogExp2` |
| **UI** | Glassmorphism-панели, градиентный заголовок, FPS, счётчики, 3 кнопки, адаптив |

## 💡 Возможные улучшения
- **Текстуры** — заменить цвета на `CanvasTexture` с полосами (клоун-рыба, неон)
- **Web Audio** — звук бульканья и всплесков
- **Bloom** — `UnrealBloomPass` для свечения рыбок ночью (режим «Выкл» света)
- **Подсветка корма** — `PointLight` на частице еды для эффекта «свечения»

Просто сохраните код как `.html` — никаких сборщиков не нужно. 🎉