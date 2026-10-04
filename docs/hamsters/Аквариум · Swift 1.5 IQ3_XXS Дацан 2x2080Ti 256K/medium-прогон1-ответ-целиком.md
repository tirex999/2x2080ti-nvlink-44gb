# 🐠 3D Аквариум с Реалистичными Рыбками

Полный самодостаточный HTML-файл. Просто сохраните как `aquarium.html` и откройте в браузере.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #041a3a; }
  #canvas-container { position: fixed; inset: 0; }

  .glass-panel {
    position: fixed;
    background: rgba(10, 40, 80, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(120, 200, 255, 0.3);
    border-radius: 14px;
    padding: 16px;
    color: #d8f0ff;
    box-shadow: 0 8px 32px rgba(0, 20, 60, 0.5);
    z-index: 10;
  }
  #info-panel { top: 16px; left: 16px; max-width: 260px; }
  #stats-panel { top: 16px; right: 16px; text-align: right; min-width: 150px; }

  h1 {
    font-size: 18px;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #6fd3ff, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  .instructions { font-size: 12px; line-height: 1.6; opacity: 0.85; margin-bottom: 12px; }

  button {
    display: block;
    width: 100%;
    margin: 6px 0;
    padding: 9px 14px;
    border: none;
    border-radius: 9px;
    background: linear-gradient(135deg, #2f8fd6, #1c5fa8);
    color: #fff;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.25s ease;
    box-shadow: 0 3px 10px rgba(40, 130, 220, 0.35);
  }
  button:hover {
    background: linear-gradient(135deg, #46a8f0, #2b74c9);
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(70, 170, 255, 0.55), 0 0 12px rgba(90, 180, 255, 0.4);
  }
  button:active { transform: translateY(0); }

  .stat-line { font-size: 13px; margin: 3px 0; }
  .stat-value { color: #7fd6ff; font-weight: bold; font-size: 15px; }

  @media (max-width: 640px) {
    #info-panel { max-width: 180px; padding: 10px; }
    h1 { font-size: 14px; }
    .instructions { display: none; }
  }
</style>
</head>
<body>
<div id="canvas-container"></div>

<div id="info-panel" class="glass-panel">
  <h1>🐠 3D Аквариум</h1>
  <div class="instructions">
    🖱️ ЛКМ — вращение камеры<br>
    🖱️ ПКМ — панорамирование<br>
    ⚙️ Колесо — зум<br>
    👆 Клик по воде — бросить корм
  </div>
  <button id="btnAddFish">➕ Добавить рыбку</button>
  <button id="btnAddBubbles">💭 Больше пузырей</button>
  <button id="btnLight">💡 Свет: ВКЛ</button>
</div>

<div id="stats-panel" class="glass-panel">
  <div class="stat-line">Рыбки: <span class="stat-value" id="fishCount">0</span></div>
  <div class="stat-line">Корм: <span class="stat-value" id="foodCount">0</span></div>
  <div class="stat-line">FPS: <span class="stat-value" id="fpsCounter">0</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============ БАЗОВАЯ СЦЕНА ============
const TANK = { x: 18, y: 12, z: 10 }; // полуразмеры аквариума

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x062a52);
scene.fog = new THREE.FogExp2(0x0a3a66, 0.018);

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
controls.target.set(0, 2, 0);

// ============ ОСВЕЩЕНИЕ ============
const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xfff4e0, 1.1);
dirLight.position.set(15, 35, 12);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.left = -25;
dirLight.shadow.camera.right = 25;
dirLight.shadow.camera.top = 25;
dirLight.shadow.camera.bottom = -25;
scene.add(dirLight);

const ptLight1 = new THREE.PointLight(0x3a86ff, 0.8, 45);
ptLight1.position.set(-12, 10, -6);
scene.add(ptLight1);

const ptLight2 = new THREE.PointLight(0x2f6bdf, 0.6, 40);
ptLight2.position.set(12, 8, 8);
scene.add(ptLight2);

// ============ СТЕКЛЯННЫЙ КОНТЕЙНЕР ============
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xbfe8ff,
  transparent: true,
  opacity: 0.12,
  transmission: 0.95,
  roughness: 0.05,
  metalness: 0,
  side: THREE.DoubleSide,
  depthWrite: false
});
const tankGeo = new THREE.BoxGeometry(TANK.x * 2, TANK.y * 2, TANK.z * 2);
const tankMesh = new THREE.Mesh(tankGeo, glassMat);
tankMesh.position.y = 2;
scene.add(tankMesh);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(tankGeo),
  new THREE.LineBasicMaterial({ color: 0x7fd6ff, transparent: true, opacity: 0.6 })
);
edges.position.y = 2;
scene.add(edges);

// ============ ПЕСЧАНОЕ ДНО ============
const sandGeo = new THREE.PlaneGeometry(TANK.x * 2 - 0.5, TANK.z * 2 - 0.5, 40, 24);
const posAttr = sandGeo.attributes.position;
for (let i = 0; i < posAttr.count; i++) {
  posAttr.setZ(i, Math.random() * 0.45 + Math.sin(posAttr.getX(i) * 0.8) * 0.15);
}
sandGeo.computeVertexNormals();
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({
  color: 0xd9c28a, roughness: 0.95
}));
sand.rotation.x = -Math.PI / 2;
sand.position.y = -9.7;
sand.receiveShadow = true;
scene.add(sand);

// ============ КАМНИ ============
for (let i = 0; i < 8; i++) {
  const rockGeo = new THREE.DodecahedronGeometry(0.7 + Math.random() * 1.3, 0);
  const rp = rockGeo.attributes.position;
  for (let j = 0; j < rp.count; j++) {
    rp.setXYZ(j,
      rp.getX(j) * (0.75 + Math.random() * 0.5),
      rp.getY(j) * (0.75 + Math.random() * 0.5),
      rp.getZ(j) * (0.75 + Math.random() * 0.5));
  }
  rockGeo.computeVertexNormals();
  const rock = new THREE.Mesh(rockGeo, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.08, 0.15, 0.3 + Math.random() * 0.2),
    roughness: 0.9
  }));
  rock.position.set(
    (Math.random() - 0.5) * (TANK.x * 2 - 4),
    -9.2,
    (Math.random() - 0.5) * (TANK.z * 2 - 4)
  );
  rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
  rock.castShadow = true;
  rock.receiveShadow = true;
  scene.add(rock);
}

// ============ ВОДОРОСЛИ ============
const seaweeds = [];
for (let i = 0; i < 12; i++) {
  const height = 4 + Math.random() * 6;
  const baseX = (Math.random() - 0.5) * (TANK.x * 2 - 3);
  const baseZ = (Math.random() - 0.5) * (TANK.z * 2 - 3);
  const pts = [];
  for (let j = 0; j <= 6; j++) {
    pts.push(new THREE.Vector3(
      Math.sin(j * 0.9) * 0.5,
      j * height / 6,
      Math.cos(j * 0.7) * 0.4
    ));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const plant = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 20, 0.18, 6, false),
    new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(0.28 + Math.random() * 0.12, 0.7, 0.3 + Math.random() * 0.15),
      roughness: 0.7
    })
  );
  const pivot = new THREE.Group();
  pivot.add(plant);
  pivot.position.set(baseX, -9.5, baseZ);
  pivot.castShadow = true;
  scene.add(pivot);
  seaweeds.push({ mesh: pivot, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.6 });
}

// ============ ПУЗЫРИ ============
const bubbles = [];
const bubbleGeo = new THREE.SphereGeometry(0.22, 10, 10);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xffffff, transparent: true, opacity: 0.35,
  transmission: 0.9, roughness: 0.1, metalness: 0
});
function spawnBubble() {
  const b = new THREE.Mesh(bubbleGeo, bubbleMat);
  b.position.set((Math.random() - 0.5) * TANK.x * 1.8, -9 + Math.random() * 18, (Math.random() - 0.5) * TANK.z * 1.8);
  b.scale.setScalar(0.4 + Math.random() * 1.2);
  scene.add(b);
  bubbles.push({ mesh: b, speed: 1.5 + Math.random() * 2, phase: Math.random() * Math.PI * 2 });
}
for (let i = 0; i < 30; i++) spawnBubble();

// ============ РЫБКИ ============
const COLOR_SCHEMES = [
  { body: 0xff7f2a, fin: 0xffb066 }, // оранжевая
  { body: 0x2a6fff, fin: 0x8ab8ff }, // синяя
  { body: 0xffd12a, fin: 0xff5a2a }, // желто-красная
  { body: 0x9b4dff, fin: 0xc9a0ff }, // фиолетовая
  { body: 0xe63030, fin: 0xff8080 }, // красная
  { body: 0x35c24a, fin: 0x90e89a }, // зеленая
  { body: 0xff6fa8, fin: 0xffb8d4 }, // розовая
  { body: 0xe0aa30, fin: 0xffdd88 }  // золотая
];

const fishArray = [];
const fishGroup = new THREE.Group();
scene.add(fishGroup);

function createFish() {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const scale = 0.6 + Math.random() * 0.6;

  const fish = new THREE.Group();

  // Тело — вытянутая сфера
  const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
  bodyGeo.scale(1.7, 0.85, 0.7);
  const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.4, metalness: 0.15 });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.castShadow = true;
  fish.add(body);

  // Хвост
  const tailGeo = new THREE.ConeGeometry(0.55, 1.1, 6);
  tailGeo.scale(0.35, 1, 1.4);
  tailGeo.rotateZ(Math.PI / 2);
  const finMat = new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.5, side: THREE.DoubleSide });
  const tailPivot = new THREE.Group();
  const tail = new THREE.Mesh(tailGeo, finMat);
  tail.position.x = -0.35;
  tailPivot.add(tail);
  tailPivot.position.x = -1.55;
  fish.add(tailPivot);

  // Плавники (верхний + боковые)
  function makeFin() {
    const g = new THREE.ConeGeometry(0.4, 0.8, 5);
    g.scale(0.25, 1, 1);
    return new THREE.Mesh(g, finMat);
  }
  const topFin = makeFin();
  topFin.position.set(0.1, 0.75, 0);
  fish.add(topFin);

  const leftFin = makeFin();
  leftFin.position.set(0.2, -0.1, 0.55);
  leftFin.rotation.x = 0.5;
  fish.add(leftFin);

  const rightFin = makeFin();
  rightFin.position.set(0.2, -0.1, -0.55);
  rightFin.rotation.x = -0.5;
  fish.add(rightFin);

  // Глаза
  const eyeGeo = new THREE.SphereGeometry(0.16, 8, 8);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilGeo = new THREE.SphereGeometry(0.08, 8, 8);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x101010 });
  [1, -1].forEach(s => {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(1.15, 0.18, s * 0.42);
    fish.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(1.28, 0.18, s * 0.46);
    fish.add(pupil);
  });

  fish.scale.setScalar(scale);
  fish.position.set(
    (Math.random() - 0.5) * TANK.x * 1.6,
    (Math.random() - 0.5) * TANK.y * 1.4 + 2,
    (Math.random() - 0.5) * TANK.z * 1.6
  );
  fishGroup.add(fish);

  fishArray.push({
    mesh: fish,
    tail: tailPivot,
    leftFin, rightFin,
    velocity: new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.2, Math.random() - 0.5).normalize(),
    speed: 1.5 + Math.random() * 2.5,
    tailSpeed: 4 + Math.random() * 5,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 2.5 + Math.random() * 1.5,
    wanderTimer: Math.random() * 3
  });
}
for (let i = 0; i < 15; i++) createFish();

// ============ КОРМ ============
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.28, 8, 8);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xb5732a, roughness: 0.9 });
const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();
let clickStart = { x: 0, y: 0 };

function spawnFood(point) {
  const f = new THREE.Mesh(foodGeo, foodMat);
  f.position.copy(point);
  f.position.y = Math.min(f.position.y, TANK.y + 1.5);
  f.castShadow = true;
  scene.add(f);
  foods.push({ mesh: f, vy: 0 });
}

renderer.domElement.addEventListener('pointerdown', e => {
  clickStart.x = e.clientX; clickStart.y = e.clientY;
});
renderer.domElement.addEventListener('pointerup', e => {
  // отличаем клик от перетаскивания камеры
  if (Math.hypot(e.clientX - clickStart.x, e.clientY - clickStart.y) > 6) return;
  if (e.button !== 0) return;
  mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  raycaster.setFromCamera(mouseNDC, camera);
  // плоскость кормления на уровне центра аквариума
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1).applyQuaternion(camera.quaternion.clone().multiply(
    new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), 0)
  )).set(0, 1, 0).normalize(), 0);
  // упрощённый вариант: кидаем корм на плоскость Y = 6
  const feedPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -6);
  const hit = new THREE.Vector3();
  if (raycaster.ray.intersectPlane(feedPlane, hit)) {
    hit.x = THREE.MathUtils.clamp(hit.x, -TANK.x + 1, TANK.x - 1);
    hit.z = THREE.MathUtils.clamp(hit.z, -TANK.z + 1, TANK.z - 1);
    spawnFood(hit);
  }
});

// ============ UI ============
document.getElementById('btnAddFish').onclick = () => { createFish(); updateStats(); };
document.getElementById('btnAddBubbles').onclick = () => { for (let i = 0; i < 10; i++) spawnBubble(); };
let lightOn = true;
document.getElementById('btnLight').onclick = function () {
  lightOn = !lightOn;
  dirLight.intensity = lightOn ? 1.1 : 0.15;
  this.textContent = lightOn ? '💡 Свет: ВКЛ' : '💡 Свет: ВЫКЛ';
};

function updateStats() {
  document.getElementById('fishCount').textContent = fishArray.length;
  document.getElementById('foodCount').textContent = foods.length;
}

// ============ АНИМАЦИЯ ============
const clock = new THREE.Clock();
let fpsFrames = 0, fpsTime = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // --- Рыбки ---
  for (let i = fishArray.length - 1; i >= 0; i--) {
    const f = fishArray[i];
    const pos = f.mesh.position;

    // Поиск корма
    f.targetFood = null;
    let bestDist = 15;
    for (const fd of foods) {
      const d = pos.distanceTo(fd.mesh.position);
      if (d < bestDist) { bestDist = d; f.targetFood = fd; }
    }

    // Случайное блуждание
    f.wanderTimer -= dt;
    if (f.wanderTimer <= 0 && !f.targetFood) {
      f.wanderTimer = 2 + Math.random() * 4;
      f.velocity.y += (Math.random() - 0.5) * 0.8;
      f.velocity.x += (Math.random() - 0.5) * 0.8;
      f.velocity.z += (Math.random() - 0.5) * 0.8;
    }

    // Преследование корма
    if (f.targetFood) {
      const toFood = new THREE.Vector3().subVectors(f.targetFood.mesh.position, pos);
      const dist = toFood.length();
      if (dist < 1.1 * f.mesh.scale.x + 0.3) {
        // Съедено!
        scene.remove(f.targetFood.mesh);
        foods.splice(foods.indexOf(f.targetFood), 1);
        f.mesh.scale.multiplyScalar(1.05); // рост +5%
        f.targetFood = null;
        updateStats();
      } else {
        f.velocity.lerp(toFood.normalize(), 0.08);
      }
    }

    // Избегание столкновений
    for (let j = 0; j < fishArray.length; j++) {
      if (j === i) continue;
      const other = fishArray[j].mesh.position;
      const dx = pos.x - other.x, dy = pos.y - other.y, dz = pos.z - other.z;
      const d2 = dx * dx + dy * dy + dz * dz;
      if (d2 < f.avoidanceRadius * f.avoidanceRadius && d2 > 0.001) {
        const d = Math.sqrt(d2);
        const push = (f.avoidanceRadius - d) / f.avoidanceRadius;
        f.velocity.x += (dx / d) * push * 3 * dt;
        f.velocity.y += (dy / d) * push * 3 * dt;
        f.velocity.z += (dz / d) * push * 3 * dt;
      }
    }

    f.velocity.normalize();

    // Движение
    pos.addScaledVector(f.velocity, f.speed * dt);

    // Отражение от стен (плавное)
    const margin = 1.2;
    if (pos.x > TANK.x - margin) f.velocity.x -= (pos.x - (TANK.x - margin)) * 2 * dt + 0.5 * dt;
    if (pos.x < -TANK.x + margin) f.velocity.x += ((-TANK.x + margin) - pos.x) * 2 * dt + 0.5 * dt;
    if (pos.y > TANK.y - margin) f.velocity.y -= (pos.y - (TANK.y - margin)) * 2 * dt + 0.5 * dt;
    if (pos.y < -TANK.y + margin + 11.5 - 9) f.velocity.y += ((-TANK.y + 1.8) - pos.y) * 2 * dt + 0.5 * dt;
    if (pos.y < -7.5) f.velocity.y += 1.5 * dt;
    if (pos.z > TANK.z - margin) f.velocity.z -= (pos.z - (TANK.z - margin)) * 2 * dt + 0.5 * dt;
    if (pos.z < -TANK.z + margin) f.velocity.z += ((-TANK.z + margin) - pos.z) * 2 * dt + 0.5 * dt;
    f.velocity.normalize();

    // Ориентация по направлению движения
    const targetAngle = Math.atan2(-f.velocity.z, f.velocity.x);
    let da = targetAngle - f.mesh.rotation.y;
    while (da > Math.PI) da -= Math.PI * 2;
    while (da < -Math.PI) da += Math.PI * 2;
    f.mesh.rotation.y += da * Math.min(1, 5 * dt);

    // Анимация хвоста и плавников
    const wave = Math.sin(t * f.tailSpeed + f.phase);
    f.tail.rotation.y = wave * 0.6;
    f.leftFin.rotation.z = wave * 0.3;
    f.rightFin.rotation.z = -wave * 0.3;
    f.mesh.position.y += Math.sin(t * 2 + f.phase) * 0.004;
  }

  // --- Корм (гравитация) ---
  for (let i = foods.length - 1; i >= 0; i--) {
    const fd = foods[i];
    fd.vy -= 4 * dt;
    fd.mesh.position.y += fd.vy * dt;
    fd.mesh.rotation.x += dt * 2;
    if (fd.mesh.position.y < -9.2) {
      scene.remove(fd.mesh);
      foods.splice(i, 1);
      updateStats();
    }
  }

  // --- Пузыри ---
  for (const b of bubbles) {
    b.mesh.position.y += b.speed * dt;
    b.mesh.position.x += Math.sin(t * 2 + b.phase) * 0.015;
    b.mesh.position.z += Math.cos(t * 1.7 + b.phase) * 0.015;
    if (b.mesh.position.y > TANK.y - 0.5) {
      b.mesh.position.y = -9.3;
      b.mesh.position.x = (Math.random() - 0.5) * TANK.x * 1.8;
      b.mesh.position.z = (Math.random() - 0.5) * TANK.z * 1.8;
    }
  }

  // --- Водоросли ---
  for (const s of seaweeds) {
    s.mesh.rotation.x = Math.sin(t * s.speed + s.phase) * 0.12;
    s.mesh.rotation.z = Math.cos(t * s.speed * 0.8 + s.phase) * 0.12;
  }

  controls.update();
  renderer.render(scene, camera);

  // FPS
  fpsFrames++;
  fpsTime += dt;
  if (fpsTime >= 0.5) {
    document.getElementById('fpsCounter').textContent = Math.round(fpsFrames / fpsTime);
    fpsFrames = 0; fpsTime = 0;
  }
}

window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

updateStats();
animate();
</script>
</body>
</html>
```

## ✨ Что реализовано

| Модуль | Описание |
|---|---|
| **🐠 15 рыбок** | Тело (вытянутая сфера), глаза с зрачками, анимированный хвост, 3 плавника, 8 цветовых схем, случайный масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, отражение от стен, блуждание, преследование корма (радиус 15), рост +5% при поедании |
| **🌊 Окружение** | Стеклянный контейнер 36×24×20 с `transmission: 0.95` и wireframe-рамкой, процедурное песчаное дно, 8 деформированных камней, 12 покачивающихся водорослей (TubeGeometry + CatmullRomCurve3) |
| **💭 Пузыри** | 30 штук, стеклянный материал, синусоидальное движение вверх, респаун у поверхности |
| **🍽️ Корм** | Клик по воде → Raycaster, гравитация, поедание с ростом, удаление на дне (клики отделены от drag-камеры) |
| **💡 Свет** | Ambient + Directional с PCFSoftShadowMap 2048² + 2 PointLight, переключаемая кнопка |
| **🎮 Камера** | OrbitControls с damping, зум 10–60, ограничение polar angle |
| **🖥️ UI** | Glass-панели с blur, градиентный заголовок, счётчики рыбок/корма/FPS, адаптивный дизайн |

**Совет:** для лучшего FPS на слабых устройствах уменьшите `shadow.mapSize` до 1028 и число пузырей.