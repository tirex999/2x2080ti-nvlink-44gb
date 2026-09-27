

# 🐠 3D Аквариум с Реалистичными Рыбками

Полный код интерактивного аквариума в одном HTML-файле:

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
    background: rgba(10, 30, 60, 0.55);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(100, 180, 255, 0.3);
    border-radius: 14px;
    padding: 16px 20px;
    color: #e0f0ff;
    box-shadow: 0 4px 30px rgba(0, 100, 200, 0.3);
  }

  #info-panel { top: 20px; left: 20px; max-width: 280px; }
  #info-panel h1 {
    font-size: 22px;
    background: linear-gradient(90deg, #4fc3f7, #00e5ff, #a7ffeb);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
  }
  #info-panel p { font-size: 12px; line-height: 1.6; opacity: 0.85; margin-bottom: 12px; }

  .btn {
    display: block;
    width: 100%;
    margin: 6px 0;
    padding: 9px 14px;
    border: none;
    border-radius: 8px;
    background: linear-gradient(135deg, #0288d1, #00acc1);
    color: white;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.25s ease;
    box-shadow: 0 2px 10px rgba(0, 150, 255, 0.3);
  }
  .btn:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 4px 18px rgba(0, 200, 255, 0.55);
    background: linear-gradient(135deg, #03a9f4, #26c6da);
  }
  .btn:active { transform: scale(0.97); }

  #stats-panel { top: 20px; right: 20px; text-align: right; min-width: 140px; }
  #stats-panel div { font-size: 14px; margin: 4px 0; }
  .stat-value { color: #4fc3f7; font-weight: bold; font-size: 18px; }

  @media (max-width: 600px) {
    #info-panel { max-width: 200px; padding: 10px; }
    #info-panel h1 { font-size: 16px; }
    #info-panel p { display: none; }
  }
</style>
</head>
<body>

<div id="info-panel" class="panel">
  <h1>🐠 3D Аквариум</h1>
  <p>🖱️ Левый клик — вращение<br>
     🖱️ Правый клик — панорама<br>
     ⚙️ Колесо — зум<br>
     🍽️ Клик по аквариуму — покормить рыбок!</p>
  <button class="btn" id="btnAddFish">🐟 Добавить рыбку</button>
  <button class="btn" id="btnBubbles">💭 Больше пузырей</button>
  <button class="btn" id="btnLight">💡 Свет вкл/выкл</button>
</div>

<div id="stats-panel" class="panel">
  <div>Рыбки: <span class="stat-value" id="fishCount">15</span></div>
  <div>Корм: <span class="stat-value" id="foodCount">0</span></div>
  <div>FPS: <span class="stat-value" id="fps">60</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============ БАЗОВАЯ СЦЕНА ============
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x041e3f);
scene.fog = new THREE.FogExp2(0x0a3d62, 0.012);

const camera = new THREE.PerspectiveCamera(60, innerWidth/innerHeight, 0.1, 200);
camera.position.set(28, 16, 30);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

// ============ РАЗМЕРЫ АКВАРИУМА ============
const TANK = { w: 36, h: 24, d: 20 };
const BOUNDS = { x: TANK.w/2 - 2, y: TANK.h/2 - 2, z: TANK.d/2 - 2 };

// ============ ОСВЕЩЕНИЕ ============
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sunLight = new THREE.DirectionalLight(0xffffff, 0.9);
sunLight.position.set(15, 35, 20);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -30;
sunLight.shadow.camera.right = 30;
sunLight.shadow.camera.top = 30;
sunLight.shadow.camera.bottom = -30;
scene.add(sunLight);

const blueLight1 = new THREE.PointLight(0x00bfff, 0.8, 50);
blueLight1.position.set(-10, 8, 0);
scene.add(blueLight1);

const blueLight2 = new THREE.PointLight(0x4169e1, 0.6, 50);
blueLight2.position.set(10, 5, 5);
scene.add(blueLight2);

// ============ СТЕКЛЯННЫЙ КОНТЕЙНЕР ============
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xaaddff, transparent: true, opacity: 0.08,
  transmission: 0.95, roughness: 0.05, metalness: 0,
  side: THREE.DoubleSide
});
const tankGeo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
const tank = new THREE.Mesh(tankGeo, glassMat);
tank.position.y = TANK.h / 2;
scene.add(tank);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(tankGeo),
  new THREE.LineBasicMaterial({ color: 0x66ccff, transparent: true, opacity: 0.6 })
);
edges.position.copy(tank.position);
scene.add(edges);

// ============ ПЕСЧАНОЕ ДНО ============
const sandGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 30);
sandGeo.rotateX(-Math.PI / 2);
const pos = sandGeo.attributes.position;
for (let i = 0; i < pos.count; i++) {
  pos.setY(i, Math.sin(pos.getX(i) * 0.8) * Math.cos(pos.getZ(i) * 0.9) * 0.35);
}
sandGeo.computeVertexNormals();
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({
  color: 0xd2b48c, roughness: 1
}));
sand.receiveShadow = true;
sand.position.y = -TANK.h / 2 + 0.1;
scene.add(sand);

// ============ КАМНИ ============
for (let i = 0; i < 8; i++) {
  const rockGeo = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.4, 1);
  const rp = rockGeo.attributes.position;
  for (let j = 0; j < rp.count; j++) {
    rp.setXYZ(j,
      rp.getX(j) * (0.8 + Math.random() * 0.4),
      rp.getY(j) * (0.7 + Math.random() * 0.3),
      rp.getZ(j) * (0.8 + Math.random() * 0.4));
  }
  rockGeo.computeVertexNormals();
  const rock = new THREE.Mesh(rockGeo, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.08, 0.1, 0.25 + Math.random() * 0.2), roughness: 0.9
  }));
  rock.position.set(
    (Math.random() - 0.5) * (TANK.w - 6),
    -TANK.h / 2 + 0.5,
    (Math.random() - 0.5) * (TANK.d - 6)
  );
  rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
  rock.castShadow = rock.receiveShadow = true;
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
      Math.sin(j * 0.6) * 0.4, j * height / 6, Math.cos(j * 0.5) * 0.3
    ));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const weed = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 12, 0.15 + Math.random() * 0.1, 6, false),
    new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(0.28 + Math.random() * 0.12, 0.7, 0.3 + Math.random() * 0.15),
      roughness: 0.8
    })
  );
  weed.position.set(baseX, -TANK.h / 2, baseZ);
  weed.castShadow = true;
  weed.userData.phase = Math.random() * Math.PI * 2;
  weed.userData.speed = 0.5 + Math.random() * 0.5;
  scene.add(weed);
  seaweeds.push(weed);
}

// ============ ЦВЕТОВЫЕ СХЕМЫ РЫБОК ============
const COLOR_SCHEMES = [
  { body: 0xff8c00, fin: 0xffb347 }, // оранжевая
  { body: 0x1e90ff, fin: 0x87cefa }, // синяя
  { body: 0xffd700, fin: 0xff4500 }, // желто-красная
  { body: 0x9932cc, fin: 0xda70d6 }, // фиолетовая
  { body: 0xdc143c, fin: 0xff6b6b }, // красная
  { body: 0x2e8b57, fin: 0x98fb98 }, // зеленая
  { body: 0xff69b4, fin: 0xffc0cb }, // розовая
  { body: 0xdaa520, fin: 0xffe87c }  // золотая
];

// ============ СОЗДАНИЕ РЫБКИ ============
function createFish(colors) {
  const c = colors || COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const group = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({ color: c.body, roughness: 0.4, metalness: 0.2 });
  const finMat = new THREE.MeshStandardMaterial({
    color: c.fin, roughness: 0.5, transparent: true, opacity: 0.85, side: THREE.DoubleSide
  });

  // Тело
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
  body.scale.set(1.6, 0.85, 0.6);
  body.castShadow = true;
  group.add(body);

  // Глаза
  [-1, 1].forEach(side => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.22, 10, 8),
      new THREE.MeshStandardMaterial({ color: 0xffffff }));
    eye.position.set(1.15, 0.2, side * 0.35);
    group.add(eye);
    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.11, 8, 6),
      new THREE.MeshBasicMaterial({ color: 0x000000 }));
    pupil.position.set(1.32, 0.2, side * 0.4);
    group.add(pupil);
  });

  // Хвост
  const tailGeo = new THREE.ConeGeometry(0.7, 1.4, 4);
  tailGeo.rotateZ(Math.PI / 2);
  const tail = new THREE.Mesh(tailGeo, finMat);
  tail.position.set(-1.9, 0, 0);
  tail.scale.set(0.3, 1, 0.15);
  group.add(tail);

  // Верхний плавник
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.5, 1, 4), finMat);
  topFin.position.set(0.1, 0.85, 0);
  topFin.scale.set(0.2, 1, 0.6);
  group.add(topFin);

  // Боковые плавники
  const leftFin = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.8, 4), finMat);
  leftFin.position.set(0.3, -0.3, 0.5);
  leftFin.rotation.x = 0.6;
  leftFin.scale.set(1, 0.2, 0.6);
  group.add(leftFin);

  const rightFin = leftFin.clone();
  rightFin.position.z = -0.5;
  rightFin.rotation.x = -0.6;
  group.add(rightFin);

  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  group.position.set(
    (Math.random() - 0.5) * 2 * BOUNDS.x,
    (Math.random() - 0.3) * BOUNDS.y,
    (Math.random() - 0.5) * 2 * BOUNDS.z
  );
  scene.add(group);

  return {
    mesh: group, tail, topFin, leftFin, rightFin,
    velocity: new THREE.Vector3(Math.random()-0.5, (Math.random()-0.5)*0.3, Math.random()-0.5).normalize(),
    speed: 2 + Math.random() * 3,
    tailSpeed: 4 + Math.random() * 4,
    phase: Math.random() * Math.PI * 2,
    wanderTimer: Math.random() * 3,
    targetFood: null,
    avoidanceRadius: 2.5 + Math.random() * 1.5
  };
}

const fishArray = [];
for (let i = 0; i < 15; i++) fishArray.push(createFish());

// ============ ПУЗЫРИ ============
const bubbles = [];
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xffffff, transparent: true, opacity: 0.35,
  transmission: 0.9, roughness: 0.1, metalness: 0
});
function addBubble() {
  const b = new THREE.Mesh(new THREE.SphereGeometry(0.15 + Math.random() * 0.25, 8, 6), bubbleMat);
  resetBubble(b);
  b.position.y = -TANK.h/2 + Math.random() * TANK.h;
  scene.add(b);
  bubbles.push(b);
}
function resetBubble(b) {
  b.position.set(
    (Math.random() - 0.5) * (TANK.w - 4),
    -TANK.h / 2 + 0.5,
    (Math.random() - 0.5) * (TANK.d - 4)
  );
  b.userData.speed = 1.5 + Math.random() * 2;
  b.userData.wobble = Math.random() * Math.PI * 2;
}
for (let i = 0; i < 30; i++) addBubble();

// ============ КОРМ ============
const foods = [];
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let mouseDownPos = null;

renderer.domElement.addEventListener('mousedown', e => {
  mouseDownPos = { x: e.clientX, y: e.clientY };
});

renderer.domElement.addEventListener('mouseup', e => {
  if (!mouseDownPos || e.button !== 0) return;
  const dx = e.clientX - mouseDownPos.x, dy = e.clientY - mouseDownPos.y;
  if (Math.sqrt(dx*dx + dy*dy) > 5) return; // это было вращение камеры

  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);

  // Плоскость кормления: горизонтальная на уровне y = BOUNDS.y
  const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -BOUNDS.y);
  const pt = new THREE.Vector3();
  raycaster.ray.intersectPlane(plane, pt);
  if (!pt) return;

  pt.x = THREE.MathUtils.clamp(pt.x, -BOUNDS.x, BOUNDS.x);
  pt.z = THREE.MathUtils.clamp(pt.z, -BOUNDS.z, BOUNDS.z);

  for (let i = 0; i < 3; i++) {
    const food = new THREE.Mesh(
      new THREE.SphereGeometry(0.25, 6, 5),
      new THREE.MeshStandardMaterial({ color: 0xd2691e, roughness: 0.9 })
    );
    food.position.copy(pt).add(new THREE.Vector3(
      (Math.random()-0.5)*0.8, Math.random()*0.5, (Math.random()-0.5)*0.8));
    food.userData.velocity = new THREE.Vector3((Math.random()-0.5)*0.5, 0, (Math.random()-0.5)*0.5);
    food.userData.fallSpeed = 1.5 + Math.random();
    scene.add(food);
    foods.push(food);
  }
});

// ============ UI ============
document.getElementById('btnAddFish').onclick = () => {
  fishArray.push(createFish());
  updateStats();
};
document.getElementById('btnBubbles').onclick = () => {
  for (let i = 0; i < 10; i++) addBubble();
};
let lightOn = true;
document.getElementById('btnLight').onclick = () => {
  lightOn = !lightOn;
  sunLight.intensity = lightOn ? 0.9 : 0.05;
};

function updateStats() {
  document.getElementById('fishCount').textContent = fishArray.length;
  document.getElementById('foodCount').textContent = foods.length;
}

// ============ АНИМАЦИЯ ============
const clock = new THREE.Clock();
let frames = 0, fpsTime = 0;
const tmpVec = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // --- Рыбки ---
  for (const fish of fishArray) {
    const m = fish.mesh;

    // Поиск корма
    fish.targetFood = null;
    let bestDist = 15;
    for (const food of foods) {
      const d = m.position.distanceTo(food.position);
      if (d < bestDist) { bestDist = d; fish.targetFood = food; }
    }

    if (fish.targetFood) {
      // Преследование корма
      tmpVec.copy(fish.targetFood.position).sub(m.position).normalize();
      fish.velocity.lerp(tmpVec, 0.08);
      if (bestDist < 1.2) {
        // Съедено!
        scene.remove(fish.targetFood);
        foods.splice(foods.indexOf(fish.targetFood), 1);
        m.scale.multiplyScalar(1.05); // рост +5%
        fish.targetFood = null;
        updateStats();
      }
    } else {
      // Случайное блуждание
      fish.wanderTimer -= dt;
      if (fish.wanderTimer <= 0) {
        fish.wanderTimer = 2 + Math.random() * 3;
        tmpVec.set(Math.random()-0.5, (Math.random()-0.5)*0.4, Math.random()-0.5).normalize();
        fish.velocity.lerp(tmpVec, 0.5);
      }
    }

    // Избегание столкновений
    for (const other of fishArray) {
      if (other === fish) continue;
      const d = m.position.distanceTo(other.mesh.position);
      if (d < fish.avoidanceRadius && d > 0.001) {
        tmpVec.copy(m.position).sub(other.mesh.position).normalize().multiplyScalar((fish.avoidanceRadius - d) * 0.05);
        fish.velocity.add(tmpVec);
      }
    }

    // Отражение от стен (плавный разворот у границ)
    const margin = 2;
    if (m.position.x > BOUNDS.x - margin) fish.velocity.x -= 0.05;
    if (m.position.x < -BOUNDS.x + margin) fish.velocity.x += 0.05;
    if (m.position.y > BOUNDS.y - margin) fish.velocity.y -= 0.05;
    if (m.position.y < -BOUNDS.y + margin) fish.velocity.y += 0.05;
    if (m.position.z > BOUNDS.z - margin) fish.velocity.z -= 0.05;
    if (m.position.z < -BOUNDS.z + margin) fish.velocity.z += 0.05;

    fish.velocity.normalize();

    // Движение
    m.position.addScaledVector(fish.velocity, fish.speed * dt);
    m.position.clamp(
      new THREE.Vector3(-BOUNDS.x, -BOUNDS.y, -BOUNDS.z),
      new THREE.Vector3(BOUNDS.x, BOUNDS.y, BOUNDS.z)
    );

    // Поворот в направлении движения
    const targetRotY = Math.atan2(-fish.velocity.z, fish.velocity.x);
    let dr = targetRotY - m.rotation.y;
    while (dr > Math.PI) dr -= Math.PI * 2;
    while (dr < -Math.PI) dr += Math.PI * 2;
    m.rotation.y += dr * 0.06;
    m.rotation.z = THREE.MathUtils.lerp(m.rotation.z, fish.velocity.y * 0.5, 0.05);

    // Анимация хвоста и плавников
    fish.tail.rotation.y = Math.sin(t * fish.tailSpeed + fish.phase) * 0.5;
    fish.topFin.rotation.z = Math.sin(t * fish.tailSpeed * 0.7 + fish.phase) * 0.15;
    fish.leftFin.rotation.z = Math.sin(t * fish.tailSpeed + fish.phase) * 0.3;
    fish.rightFin.rotation.z = -Math.sin(t * fish.tailSpeed + fish.phase) * 0.3;
  }

  // --- Корм (гравитация) ---
  for (let i = foods.length - 1; i >= 0; i--) {
    const f = foods[i];
    f.position.y -= f.userData.fallSpeed * dt;
    f.position.x += f.userData.velocity.x * dt;
    f.position.z += f.userData.velocity.z * dt;
    f.rotation.x += dt * 2;
    if (f.position.y < -TANK.h / 2 + 0.5) {
      scene.remove(f);
      foods.splice(i, 1);
      updateStats();
    }
  }

  // --- Пузыри ---
  for (const b of bubbles) {
    b.position.y += b.userData.speed * dt;
    b.position.x += Math.sin(t * 2 + b.userData.wobble) * 0.01;
    b.position.z += Math.cos(t * 1.5 + b.userData.wobble) * 0.01;
    if (b.position.y > TANK.h / 2 - 0.5) resetBubble(b);
  }

  // --- Водоросли ---
  for (const w of seaweeds) {
    w.rotation.x = Math.sin(t * w.userData.speed + w.userData.phase) * 0.12;
    w.rotation.z = Math.cos(t * w.userData.speed * 0.8 + w.userData.phase) * 0.1;
  }

  // --- Свет пульсирует ---
  blueLight1.intensity = 0.7 + Math.sin(t * 0.8) * 0.15;
  blueLight2.intensity = 0.5 + Math.cos(t * 0.6) * 0.12;

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

// ============ RESIZE ============
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## ✨ Реализованные функции

| Система | Описание |
|---------|----------|
| **🐠 15 рыбок** | 8 цветовых схем, случайный масштаб 0.6–1.2, тело + глаза с зрачками + хвост + 3 плавника |
| **🧠 ИИ** | Избегание столкновений, мягкое отражение от стен, блуждание, преследование корма (радиус 15), рост +5% при поедании |
| **🌊 Окружение** | Стеклянный контейнер 36×24×20 (transmission 0.95), procedural песчаное дно, 8 деформированных камней, 12 анимированных водорослей (TubeGeometry + CatmullRomCurve3) |
| **💭 Пузыри** | 30 пузырей с MeshPhysicalMaterial, синусоидальное покачивание, сброс у поверхности |
| **🍽️ Кормление** | Клик спавнит 3颗粒 корма с гравитацией; различие клика и вращения камеры по порогу 5px |
| **💡 Свет** | Ambient + Directional с PCFSoftShadow 2048², 2 пульсирующих PointLight, переключение |
| **🎮 Камера** | OrbitControls с damping, зум 10–60, ограничение polar angle |
| **🖥️ UI** | Glass-панели с backdrop-blur, градиентные кнопки, FPS-счетчик, живой статистик |

**Как использовать:** сохраните как `aquarium.html` и откройте в браузере. Кликайте по воде, чтобы кормить рыбок — они найдут корм, поедят и вырастут! 🐡