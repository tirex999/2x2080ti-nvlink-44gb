

# 🐠 3D Аквариум с Реалистичными Рыбками

Полный код в одном HTML-файле. Сохраните как `aquarium.html` и откройте в браузере.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #001a33; }
  canvas { display: block; }

  .panel {
    position: absolute;
    background: rgba(10, 40, 80, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(100, 200, 255, 0.25);
    border-radius: 14px;
    padding: 16px 20px;
    color: #cfeaff;
    box-shadow: 0 8px 32px rgba(0, 20, 60, 0.5), inset 0 0 20px rgba(80, 180, 255, 0.08);
    z-index: 10;
  }

  #infoPanel { top: 20px; left: 20px; max-width: 300px; }
  #infoPanel h1 {
    font-size: 22px; margin-bottom: 10px;
    background: linear-gradient(90deg, #4dd0ff, #a06bff, #ffb34d);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  #infoPanel p { font-size: 12.5px; line-height: 1.65; opacity: 0.85; margin-bottom: 4px; }

  #statsPanel { top: 20px; right: 20px; min-width: 170px; text-align: center; }
  #statsPanel .stat { font-size: 15px; margin-bottom: 6px; }
  #statsPanel .stat b { color: #ffd75e; }
  #fps { color: #6dff9e !important; }

  .btn-row { margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap; }
  .btn {
    flex: 1;
    padding: 9px 12px;
    border: none; border-radius: 9px;
    font-size: 12.5px; font-weight: 600;
    color: #fff; cursor: pointer;
    background: linear-gradient(135deg, #1e6fd9, #3aa0ff);
    box-shadow: 0 4px 14px rgba(30, 111, 217, 0.45);
    transition: all .2s ease;
    white-space: nowrap;
  }
  .btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(58, 160, 255, 0.7);
    filter: brightness(1.15);
  }
  .btn:active { transform: translateY(0); }
  .btn.gold { background: linear-gradient(135deg, #d98a1e, #ffc43a); box-shadow: 0 4px 14px rgba(217,138,30,.45); }
  .btn.purple { background: linear-gradient(135deg, #7b2fd9, #b06bff); box-shadow: 0 4px 14px rgba(123,47,217,.45); }
</style>
</head>
<body>

<div id="infoPanel" class="panel">
  <h1>🐠 3D Аквариум</h1>
  <p>🖱️ <b>ЛКМ + движение</b> — вращение камеры</p>
  <p>🖱️ <b>ПКМ + движение</b> — панорама</p>
  <p>🔍 <b>Колесо</b> — зум</p>
  <p>🍤 <b>Клик по воде</b> — покормить рыбок</p>
  <div class="btn-row">
    <button class="btn" id="addFishBtn">+ Рыбка</button>
    <button class="btn gold" id="bubbleBtn">+ Пузыри</button>
    <button class="btn purple" id="lightBtn">💡 Свет</button>
  </div>
</div>

<div id="statsPanel" class="panel">
  <div class="stat">🐟 Рыбки: <b id="fishCount">15</b></div>
  <div class="stat">FPS: <b id="fps">60</b></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
//  БАЗОВАЯ СЦЕНА
// ============================================================
const TANK = { w: 36, h: 24, d: 20 };          // размеры аквариума
const BOUNDS = {
  minX: -TANK.w/2 + 1.5, maxX: TANK.w/2 - 1.5,
  minY: 1.5,        maxY: TANK.h - 1.5,
  minZ: -TANK.d/2 + 1.5, maxZ: TANK.d/2 - 1.5
};

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a2a50, 0.012);

// Градиентный фон
(function makeGradientBg() {
  const c = document.createElement('canvas');
  c.width = 2; c.height = 512;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 0, 512);
  grad.addColorStop(0, '#0d3a6e');
  grad.addColorStop(1, '#020b1e');
  g.fillStyle = grad;
  g.fillRect(0, 0, 2, 512);
  const tex = new THREE.CanvasTexture(c);
  scene.background = tex;
})();

const camera = new THREE.PerspectiveCamera(55, innerWidth/innerHeight, 0.1, 500);
camera.position.set(30, 22, 42);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, TANK.h/2, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

// ============================================================
//  ОСВЕЩЕНИЕ
// ============================================================
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const dirLight = new THREE.DirectionalLight(0xfff2d0, 1.1);
dirLight.position.set(25, 45, 20);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.left = -30;
dirLight.shadow.camera.right = 30;
dirLight.shadow.camera.top = 30;
dirLight.shadow.camera.bottom = -30;
dirLight.shadow.bias = -0.0005;
scene.add(dirLight);

const pl1 = new THREE.PointLight(0x33ccff, 0.7, 60);
pl1.position.set(-10, 18, 5);
scene.add(pl1);

const pl2 = new THREE.PointLight(0x2255ff, 0.6, 60);
pl2.position.set(10, 10, -6);
scene.add(pl2);

// ============================================================
//  АКВАРИУМ (СТЕКЛО + РАМКА)
// ============================================================
const tankGeo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
const tankMat = new THREE.MeshPhysicalMaterial({
  color: 0x88ccee,
  metalness: 0, roughness: 0.05,
  transmission: 0.95,
  transparent: true, opacity: 0.35,
  ior: 1.4, thickness: 0.5,
  side: THREE.DoubleSide
});
const tank = new THREE.Mesh(tankGeo, tankMat);
tank.position.y = TANK.h/2;
scene.add(tank);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(tankGeo),
  new THREE.LineBasicMaterial({ color: 0x9fdcff, transparent: true, opacity: 0.6 })
);
edges.position.copy(tank.position);
scene.add(edges);

// ============================================================
//  ПЕСЧАНОЕ ДНО
// ============================================================
(function makeSand() {
  const geo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 28);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i);
    pos.setZ(i,
      Math.sin(x * 0.5) * Math.cos(y * 0.7) * 0.25 +
      Math.sin(x * 1.7 + y * 1.3) * 0.12 +
      (Math.random() - 0.5) * 0.15
    );
  }
  geo.computeVertexNormals();
  const sand = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: 0xd9b877, roughness: 0.95
  }));
  sand.rotation.x = -Math.PI/2;
  sand.position.y = 0.4;
  sand.receiveShadow = true;
  scene.add(sand);
})();

// ============================================================
//  КАМНИ
// ============================================================
for (let i = 0; i < 8; i++) {
  const r = 0.7 + Math.random() * 1.3;
  const geo = new THREE.DodecahedronGeometry(r, 0);
  const pos = geo.attributes.position;
  for (let v = 0; v < pos.count; v++) {
    pos.setXYZ(v,
      pos.getX(v) * (0.8 + Math.random()*0.4),
      pos.getY(v) * (0.6 + Math.random()*0.4),
      pos.getZ(v) * (0.8 + Math.random()*0.4)
    );
  }
  geo.computeVertexNormals();
  const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.08 + Math.random()*0.05, 0.15, 0.25 + Math.random()*0.2),
    roughness: 0.9
  }));
  rock.position.set(
    (Math.random()-0.5) * (TANK.w - 6),
    0.8,
    (Math.random()-0.5) * (TANK.d - 5)
  );
  rock.rotation.set(Math.random()*0.5, Math.random()*Math.PI, Math.random()*0.5);
  rock.castShadow = rock.receiveShadow = true;
  scene.add(rock);
}

// ============================================================
//  ВОДОРОСЛИ
// ============================================================
const weeds = [];
for (let i = 0; i < 12; i++) {
  const h = 3 + Math.random() * 4;
  const pts = [];
  const bx = (Math.random()-0.5) * (TANK.w - 8);
  const bz = (Math.random()-0.5) * (TANK.d - 6);
  for (let j = 0; j <= 6; j++) {
    const t = j / 6;
    pts.push(new THREE.Vector3(
      bx + Math.sin(t * 3 + i) * 0.4 * t,
      0.6 + h * t,
      bz + Math.cos(t * 2.5 + i) * 0.4 * t
    ));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const weed = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 12, 0.18 + Math.random()*0.12, 6),
    new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(0.32 + Math.random()*0.1, 0.7, 0.3 + Math.random()*0.15),
      roughness: 0.8
    })
  );
  weed.castShadow = true;
  weed.userData = { baseRotX: 0, baseRotZ: 0, phase: Math.random()*Math.PI*2, amp: 0.06 + Math.random()*0.08 };
  scene.add(weed);
  weeds.push(weed);
}

// ============================================================
//  ПУЗЫРИ
// ============================================================
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xbbddff, metalness: 0, roughness: 0.05,
  transmission: 0.9, transparent: true, opacity: 0.45,
  clearcoat: 1
});
const bubbles = [];
function addBubble() {
  const r = 0.12 + Math.random() * 0.22;
  const b = new THREE.Mesh(new THREE.SphereGeometry(r, 10, 8), bubbleMat);
  b.position.set(
    (Math.random()-0.5) * (TANK.w - 4),
    0.8 + Math.random() * (TANK.h - 2),
    (Math.random()-0.5) * (TANK.d - 4)
  );
  b.userData = {
    baseX: b.position.x,
    speed: 1.2 + Math.random() * 1.8,
    phase: Math.random() * Math.PI * 2,
    amp: 0.3 + Math.random() * 0.5
  };
  scene.add(b);
  bubbles.push(b);
}
for (let i = 0; i < 30; i++) addBubble();

// ============================================================
//  РЫБКИ
// ============================================================
const COLOR_SCHEMES = [
  { body: 0xff7722, fin: 0xffaa44 },   // оранжевая
  { body: 0x2266ff, fin: 0x55aaff },   // синяя
  { body: 0xffdd00, fin: 0xff3322 },   // жёлто-красная
  { body: 0x9933ff, fin: 0xcc88ff },   // фиолетовая
  { body: 0xee2233, fin: 0xff7788 },   // красная
  { body: 0x22bb66, fin: 0x77eeaa },   // зелёная
  { body: 0xff66aa, fin: 0xffb0d0 },   // розовая
  { body: 0xffc837, fin: 0xffe28a }    // золотая
];

const fishArray = [];
const tmpVec = new THREE.Vector3();

function createFish(scaleOverride) {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const scale = scaleOverride || (0.6 + Math.random() * 0.6);
  const group = new THREE.Group();

  // Тело
  const body = new THREE.Mesh(
    new THREE.SphereGeometry(1, 16, 12),
    new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.45, metalness: 0.15 })
  );
  body.scale.set(1.7, 1, 1);
  body.castShadow = true;
  group.add(body);

  // Глаза (белок + зрачок)
  [-0.38, 0.38].forEach(z => {
    const eye = new THREE.Mesh(
      new THREE.SphereGeometry(0.16, 8, 8),
      new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 })
    );
    eye.position.set(1.15, 0.25, z);
    group.add(eye);
    const pupil = new THREE.Mesh(
      new THREE.SphereGeometry(0.08, 6, 6),
      new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.1 })
    );
    pupil.position.set(1.26, 0.25, z);
    group.add(pupil);
  });

  // Хвост
  const tail = new THREE.Mesh(
    new THREE.ConeGeometry(0.55, 1.4, 8),
    new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.5, side: THREE.DoubleSide })
  );
  tail.geometry.rotateX(Math.PI/2);       // конус "лежит" по X
  tail.geometry.translate(0.7, 0, 0);     // точка вращения у основания
  tail.position.set(-1.6, 0, 0);
  group.add(tail);

  // Верхний плавник
  const dorsal = new THREE.Mesh(
    new THREE.ConeGeometry(0.4, 0.9, 6),
    new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.5, side: THREE.DoubleSide })
  );
  dorsal.position.set(0, 1.05, 0);
  group.add(dorsal);

  // Боковые плавники
  const finGeo = new THREE.ConeGeometry(0.35, 0.9, 6);
  finGeo.rotateZ(Math.PI/2);
  const leftFin = new THREE.Mesh(finGeo, new THREE.MeshStandardMaterial({
    color: scheme.fin, roughness: 0.5, side: THREE.DoubleSide }));
  leftFin.position.set(0.2, -0.3, 0.95);
  leftFin.rotation.x = 0.4;
  group.add(leftFin);

  const rightFin = new THREE.Mesh(finGeo.clone(), leftFin.material);
  rightFin.position.set(0.2, -0.3, -0.95);
  rightFin.rotation.x = -0.4;
  group.add(rightFin);

  group.scale.setScalar(scale);
  group.position.set(
    (Math.random()-0.5) * (TANK.w - 8),
    3 + Math.random() * (TANK.h - 8),
    (Math.random()-0.5) * (TANK.d - 6)
  );
  scene.add(group);

  const vel = new THREE.Vector3(
    (Math.random()-0.5), (Math.random()-0.5)*0.3, (Math.random()-0.5)
  ).normalize().multiplyScalar(0.01);

  fishArray.push({
    mesh: group, tail, leftFin, rightFin,
    velocity: vel,
    speed: 0.025 + Math.random() * 0.025,
    tailSpeed: 8 + Math.random() * 6,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 2.2 + Math.random() * 1.5,
    wanderTimer: Math.random() * 3
  });
}
for (let i = 0; i < 15; i++) createFish();

// ============================================================
//  КОРМ
// ============================================================
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.18, 8, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xff5533, emissive: 0x882200 });

function spawnFood(point) {
  const f = new THREE.Mesh(foodGeo, foodMat);
  f.position.copy(point);
  scene.add(f);
  foods.push({ mesh: f, vy: 0 });
}

// ============================================================
//  КЛИК ПО АКВАРИУМУ (raycaster, отличаем клик от драга)
// ============================================================
const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();
let downPos = null;

addEventListener('mousedown', e => { if (e.button === 0) downPos = { x: e.clientX, y: e.clientY }; });
addEventListener('mouseup', e => {
  if (e.button !== 0 || !downPos) return;
  const dx = e.clientX - downPos.x, dy = e.clientY - downPos.y;
  downPos = null;
  if (dx*dx + dy*dy > 25) return; // это было вращение камеры

  mouseNDC.set((e.clientX/innerWidth)*2 - 1, -(e.clientY/innerHeight)*2 + 1);
  raycaster.setFromCamera(mouseNDC, camera);

  // Плоскость через центр аквариума, перпендикулярная взгляду камеры
  const camDir = new THREE.Vector3();
  camera.getWorldDirection(camDir);
  const plane = new THREE.Plane();
  plane.setFromNormalAndCoplanarPoint(camDir, new THREE.Vector3(0, TANK.h/2, 0));
  const hit = new THREE.Vector3();
  if (raycaster.ray.intersectPlane(plane, hit)) {
    hit.x = THREE.MathUtils.clamp(hit.x, BOUNDS.minX, BOUNDS.maxX);
    hit.y = THREE.MathUtils.clamp(hit.y, BOUNDS.minY + 1, BOUNDS.maxY);
    hit.z = THREE.MathUtils.clamp(hit.z, BOUNDS.minZ, BOUNDS.maxZ);
    spawnFood(hit);
  }
});

// ============================================================
//  UI
// ============================================================
document.getElementById('addFishBtn').onclick = () => createFish();
document.getElementById('bubbleBtn').onclick = () => { for (let i = 0; i < 10; i++) addBubble(); };
let lightOn = true;
document.getElementById('lightBtn').onclick = () => {
  lightOn = !lightOn;
  dirLight.intensity = lightOn ? 1.1 : 0.1;
};
document.getElementById('fishCount').textContent = fishArray.length;
// обновляем счётчик при добавлении
const origCreate = createFish;
// (счётчик обновляется в цикле)

// ============================================================
//  ГЛАВНЫЙ ЦИКЛ
// ============================================================
const clock = new THREE.Clock();
let fpsFrames = 0, fpsTime = 0;
const fpsEl = document.getElementById('fps');
const fishCountEl = document.getElementById('fishCount');
let lastCount = -1;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // ---------- FPS ----------
  fpsFrames++;
  fpsTime += dt;
  if (fpsTime >= 0.5) {
    fpsEl.textContent = Math.round(fpsFrames / fpsTime);
    fpsFrames = 0; fpsTime = 0;
  }
  if (fishArray.length !== lastCount) {
    lastCount = fishArray.length;
    fishCountEl.textContent = lastCount;
  }

  // ---------- Рыбки ----------
  for (let i = 0; i < fishArray.length; i++) {
    const fish = fishArray[i];
    const p = fish.mesh.position;

    // Поиск корма (радиус 15)
    let bestFood = null, bestDist = 15;
    for (let j = 0; j < foods.length; j++) {
      const d = p.distanceTo(foods[j].mesh.position);
      if (d < bestDist) { bestDist = d; bestFood = foods[j]; }
    }
    fish.targetFood = bestFood ? { ref: bestFood, dist: bestDist } : null;

    if (bestFood) {
      // Преследование корма
      tmpVec.subVectors(bestFood.mesh.position, p).normalize();
      fish.velocity.lerp(tmpVec.multiplyScalar(fish.speed * 1.6), 0.06);
      // Съели!
      if (bestDist < 0.9) {
        scene.remove(bestFood.mesh);
        foods.splice(foods.indexOf(bestFood), 1);
        fish.mesh.scale.multiplyScalar(1.05);  // рост на 5%
        fish.targetFood = null;
      }
    } else {
      // Случайное блуждание
      fish.wanderTimer -= dt;
      if (fish.wanderTimer <= 0) {
        fish.wanderTimer = 2 + Math.random() * 4;
        tmpVec.set(
          (Math.random()-0.5), (Math.random()-0.5)*0.4, (Math.random()-0.5)
        ).normalize().multiplyScalar(fish.speed);
        fish.velocity.lerp(tmpVec, 0.04);
      }
    }

    // Избегание других рыбок
    for (let j = i + 1; j < fishArray.length; j++) {
      const other = fishArray[j].mesh.position;
      tmpVec.subVectors(p, other);
      const d = tmpVec.length();
      if (d < fish.avoidanceRadius && d > 0.001) {
        tmpVec.normalize().multiplyScalar(fish.speed * 0.8 * (1 - d/fish.avoidanceRadius));
        fish.velocity.add(tmpVec);
        fishArray[j].velocity.sub(tmpVec);
      }
    }

    // Отражение от стенок
    if (p.x < BOUNDS.minX) { p.x = BOUNDS.minX; fish.velocity.x = Math.abs(fish.velocity.x); }
    if (p.x > BOUNDS.maxX) { p.x = BOUNDS.maxX; fish.velocity.x = -Math.abs(fish.velocity.x); }
    if (p.y < BOUNDS.minY) { p.y = BOUNDS.minY; fish.velocity.y = Math.abs(fish.velocity.y); }
    if (p.y > BOUNDS.maxY) { p.y = BOUNDS.maxY; fish.velocity.y = -Math.abs(fish.velocity.y); }
    if (p.z < BOUNDS.minZ) { p.z = BOUNDS.minZ; fish.velocity.z = Math.abs(fish.velocity.z); }
    if (p.z > BOUNDS.maxZ) { p.z = BOUNDS.maxZ; fish.velocity.z = -Math.abs(fish.velocity.z); }

    p.addScaledVector(fish.velocity, dt * 60);

    // Поворот в направлении движения (плавно)
    if (fish.velocity.lengthSq() > 1e-6) {
      tmpVec.copy(p).add(fish.velocity);
      const desired = new THREE.Quaternion();
      const m = new THREE.Matrix4().lookAt(p, tmpVec, new THREE.Vector3(0, 1, 0));
      desired.setFromRotationMatrix(m);
      fish.mesh.quaternion.slerp(desired, 0.08);
    }

    // Анимация хвоста и плавников
    const swing = Math.sin(t * fish.tailSpeed + fish.phase);
    fish.tail.rotation.y = swing * 0.65;
    fish.leftFin.rotation.z  =  0.3 + Math.sin(t * fish.tailSpeed * 0.8 + fish.phase) * 0.35;
    fish.rightFin.rotation.z = -0.3 - Math.sin(t * fish.tailSpeed * 0.8 + fish.phase) * 0.35;
  }

  // ---------- Корм (гравитация) ----------
  for (let i = foods.length - 1; i >= 0; i--) {
    const f = foods[i];
    f.vy -= 0.004;                    // гравитация
    f.mesh.position.y += f.vy;
    f.mesh.rotation.y += dt * 2;
    if (f.mesh.position.y < 0.7) {    // упал на дно — растворяется
      scene.remove(f.mesh);
      foods.splice(i, 1);
    }
  }

  // ---------- Пузыри ----------
  for (const b of bubbles) {
    const u = b.userData;
    b.position.y += u.speed * dt;
    b.position.x = u.baseX + Math.sin(t * 1.5 + u.phase) * u.amp;
    if (b.position.y > TANK.h - 0.5) {
      b.position.y = 0.8;
      u.baseX = (Math.random()-0.5) * (TANK.w - 4);
    }
  }

  // ---------- Водоросли ----------
  for (const w of weeds) {
    const u = w.userData;
    w.rotation.x = u.baseRotX + Math.sin(t * 1.2 + u.phase) * u.amp;
    w.rotation.z = u.baseRotZ + Math.cos(t * 0.9 + u.phase) * u.amp;
  }

  // ---------- Подводный свет (пульсация) ----------
  pl1.intensity = 0.6 + Math.sin(t * 1.3) * 0.15;
  pl2.intensity = 0.5 + Math.cos(t * 1.1) * 0.15;

  controls.update();
  renderer.render(scene, camera);
}
animate();

// ============================================================
//  RESIZE
// ============================================================
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
| **🐠 Рыбки** | 15 шт., тело-сфера, глаза со зрачками, хвост + 3 плавника, 8 цветовых схем, масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, отражение от стенок, блуждание, преследование корма (радиус 15), рост на 5% после еды |
| **🌊 Окружение** | Стеклянный танк (`transmission: 0.95`) с рамкой, процедурный песок, 8 деформированных камней, 12 покачивающихся водорослей из `TubeGeometry` |
| **💭 Пузыри** | 30 шт., стеклянный материал, синусоидальное покачивание, сброс на дно |
| **🍽️ Кормление** | Клик → raycaster → плоскость через центр → корм падает с гравитацией |
| **💡 Свет** | Directional (тени 2048², PCFSoft) + 2 пульсирующих PointLight, туман `FogExp2`, градиентный фон |
| **🖥️ UI** | Glass-панели с blur, градиентные кнопки, счётчик рыбок и FPS |

**Совет:** чтобы рыбки «собирались» плотнее на корм, уменьшите `avoidanceRadius` или увеличьте множитель преследования `fish.speed * 1.6`. 🐟