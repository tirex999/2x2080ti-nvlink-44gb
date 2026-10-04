# 🐠 3D Аквариум — полная реализация

Вот полностью готовый файл `aquarium.html` со всеми запрошенными функциями:

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
  #canvas-container { position: fixed; inset: 0; }

  .panel {
    position: fixed; padding: 16px; border-radius: 14px;
    background: rgba(10, 40, 70, 0.45);
    backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(120, 200, 255, 0.25);
    box-shadow: 0 0 25px rgba(0, 150, 255, 0.25);
    color: #cfeaff; z-index: 10;
  }
  #info-panel { top: 16px; left: 16px; max-width: 260px; }
  #stats-panel { top: 16px; right: 16px; min-width: 160px; }

  h1 {
    font-size: 20px; margin-bottom: 8px;
    background: linear-gradient(90deg, #4fc3f7, #00e5ff, #7cffcb);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  #info-panel p { font-size: 12.5px; line-height: 1.55; opacity: .9; margin-bottom: 10px; }

  button {
    display: block; width: 100%; margin-top: 8px; padding: 9px 12px;
    border: none; border-radius: 9px; cursor: pointer;
    font-size: 13px; font-weight: 600; color: #fff;
    background: linear-gradient(135deg, #1976d2, #00bcd4);
    box-shadow: 0 3px 10px rgba(0, 150, 255, .35);
    transition: transform .15s, box-shadow .15s, filter .15s;
  }
  button:hover { transform: translateY(-2px); filter: brightness(1.15);
    box-shadow: 0 6px 18px rgba(0, 200, 255, .5); }
  button:active { transform: translateY(0); }

  .stat-row { display: flex; justify-content: space-between; font-size: 14px;
    padding: 3px 0; }
  .stat-row span:last-child { color: #7cffcb; font-weight: 700; }
</style>
</head>
<body>
<div id="canvas-container"></div>

<div id="info-panel" class="panel">
  <h1>🐠 3D Аквариум</h1>
  <p>🖱️ <b>ЛКМ + движение</b> — вращение<br>
     🖱️ <b>ПКМ + движение</b> — панорама<br>
     🖱️ <b>Колесо</b> — зум<br>
     🍽️ <b>Клик по аквариуму</b> — бросить корм!</p>
  <button id="btn-fish">➕ Добавить рыбку</button>
  <button id="btn-bubbles">🫧 Больше пузырей</button>
  <button id="btn-light">💡 Переключить свет</button>
</div>

<div id="stats-panel" class="panel">
  <div class="stat-row"><span>🐟 Рыбки:</span><span id="stat-fish">0</span></div>
  <div class="stat-row"><span>🍽️ Корм:</span><span id="stat-food">0</span></div>
  <div class="stat-row"><span>🫧 Пузыри:</span><span id="stat-bub">0</span></div>
  <div class="stat-row"><span>⚡ FPS:</span><span id="stat-fps">0</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* ==================== СЦЕНА ==================== */
const TANK = { w: 36, h: 24, d: 20 };

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x06263f, 0.014);

// Градиентный фон (canvas-текстура)
(function makeBG() {
  const c = document.createElement('canvas'); c.width = 2; c.height = 256;
  const g = c.getContext('2d').createLinearGradient(0, 0, 0, 256);
  g.addColorStop(0, '#02101f'); g.addColorStop(0.5, '#062c4f'); g.addColorStop(1, '#0a4a7a');
  const ctx = c.getContext('2d'); ctx.fillStyle = g; ctx.fillRect(0, 0, 2, 256);
  const tex = new THREE.CanvasTexture(c);
  scene.background = tex;
})();

const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 300);
camera.position.set(0, 16, 40);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.getElementById('canvas-container').appendChild(renderer.domElement);

const controls = new THREE.OrbitControls ? null : null; // placeholder
const orbit = new THREE.OrbitControls(camera, renderer.domElement);
orbit.enableDamping = true; orbit.dampingFactor = 0.06;
orbit.minDistance = 10; orbit.maxDistance = 60;
orbit.maxPolarAngle = Math.PI / 1.8;
orbit.target.set(0, 11, 0);

/* ==================== ОСВЕЩЕНИЕ ==================== */
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xbfe8ff, 1.0);
sun.position.set(15, 40, 20);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -30; sun.shadow.camera.right = 30;
sun.shadow.camera.top = 30; sun.shadow.camera.bottom = -30;
scene.add(sun);

const pl1 = new THREE.PointLight(0x2a9df4, 0.9, 60); pl1.position.set(-12, 20, 0);
const pl2 = new THREE.PointLight(0x0055ff, 0.7, 60); pl2.position.set(12, 6, 0);
scene.add(pl1, pl2);
let lightOn = true;

/* ==================== АКВАРИУМ (стекло) ==================== */
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xaaddff, transmission: 0.95, transparent: true, opacity: 0.25,
  roughness: 0.05, metalness: 0, thickness: 0.5, side: THREE.DoubleSide
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

/* ==================== ПЕСЧАНОЕ ДНО ==================== */
const sandGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 24);
sandGeo.rotateX(-Math.PI / 2);
const pos = sandGeo.attributes.position;
for (let i = 0; i < pos.count; i++)
  pos.setY(i, Math.random() * 0.55 + Math.sin(pos.getX(i)) * 0.2);
sandGeo.computeVertexNormals();
const sand = new THREE.Mesh(sandGeo,
  new THREE.MeshStandardMaterial({ color: 0xd9b26f, flatShading: true, roughness: 1 }));
sand.position.y = 0.3;
sand.receiveShadow = true;
scene.add(sand);

/* ==================== КАМНИ ==================== */
const rockMat = new THREE.MeshStandardMaterial({ color: 0x7a7a72, flatShading: true, roughness: 0.95 });
for (let i = 0; i < 8; i++) {
  const geo = new THREE.DodecahedronGeometry(0.7 + Math.random() * 1.1, 0);
  const p = geo.attributes.position;
  for (let j = 0; j < p.count; j++) {
    p.setXYZ(j, p.getX(j) * (0.7 + Math.random() * 0.6),
                p.getY(j) * (0.7 + Math.random() * 0.6),
                p.getZ(j) * (0.7 + Math.random() * 0.6));
  }
  geo.computeVertexNormals();
  const rock = new THREE.Mesh(geo, rockMat);
  rock.position.set((Math.random() - 0.5) * (TANK.w - 6), 0.5, (Math.random() - 0.5) * (TANK.d - 5));
  rock.rotation.set(Math.random() * 3, Math.random() * 3, Math.random() * 3);
  rock.castShadow = rock.receiveShadow = true;
  scene.add(rock);
}

/* ==================== ВОДОРОСЛИ ==================== */
const plants = [];
const plantColors = [0x1fae5e, 0x0e8a4a, 0x2ecc71, 0x27ae60];
for (let i = 0; i < 12; i++) {
  const group = new THREE.Group();
  const px = (Math.random() - 0.5) * (TANK.w - 5);
  const pz = (Math.random() - 0.5) * (TANK.d - 4);
  const bladeCount = 2 + Math.floor(Math.random() * 3);
  for (let b = 0; b < bladeCount; b++) {
    const h = 3 + Math.random() * 6;
    const pts = [];
    for (let k = 0; k <= 4; k++)
      pts.push(new THREE.Vector3(Math.sin(k) * 0.35, (h / 4) * k, Math.cos(k * 2) * 0.3));
    const curve = new THREE.CatmullRomCurve3(pts);
    const tube = new THREE.Mesh(
      new THREE.TubeGeometry(curve, 12, 0.16, 5, false),
      new THREE.MeshStandardMaterial({
        color: plantColors[Math.floor(Math.random() * plantColors.length)],
        roughness: 0.8, transparent: true, opacity: 0.9 }));
    tube.castShadow = true;
    group.add(tube);
  }
  group.position.set(px, 0.3, pz);
  group.userData = { phase: Math.random() * 6.28, speed: 0.6 + Math.random() * 0.8 };
  scene.add(group);
  plants.push(group);
}

/* ==================== РЫБКИ ==================== */
const schemes = [
  { body: 0xff8c1a, fin: 0xffc46b }, // оранжевая
  { body: 0x1a6bff, fin: 0x8ac0ff }, // синяя
  { body: 0xffd400, fin: 0xff3300 }, // жёлто-красная
  { body: 0x9b30ff, fin: 0xd9a0ff }, // фиолетовая
  { body: 0xe01010, fin: 0xff7b7b }, // красная
  { body: 0x18c964, fin: 0x9dffc9 }, // зелёная
  { body: 0xff5fb0, fin: 0xffc2e0 }, // розовая
  { body: 0xd4af37, fin: 0xfff0a8 }, // золотая
];
const eyeGeo = new THREE.SphereGeometry(0.22, 10, 8);
const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
const pupilMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a, roughness: 0.3 });
const pupilGeo = new THREE.SphereGeometry(0.11, 8, 8);

const fishArray = [];

function createFish() {
  const s = schemes[Math.floor(Math.random() * schemes.length)];
  const bodyMat = new THREE.MeshStandardMaterial({ color: s.body, roughness: 0.35, metalness: 0.25 });
  const finMat  = new THREE.MeshStandardMaterial({ color: s.fin, roughness: 0.5, transparent: true, opacity: 0.9 });

  const group = new THREE.Group();

  const body = new.Mesh ? null : null; // no-op guard
  const bodyMesh = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
  bodyMesh.scale.set(1.5, 0.75, 0.5);
  bodyMesh.castShadow = true;
  group.add(bodyMesh);

  // Хвост (плоский «веер»)
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.8, 10, 8), finMat);
  tail.scale.set(0.16, 0.8, 0.55);
  tail.position.x = -1.85;
  tail.castShadow = true;
  group.add(tail);

  // Верхний плавник
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.9, 4), finMat);
  topFin.scale.set(0.25, 1, 0.6);
  topFin.position.y = 0.75;
  group.add(topFin);

  // Боковые плавники
  const finGeo = new THREE.SphereGeometry(0.45, 8, 6);
  const leftFin = new THREE.Mesh(finGeo, finMat);
  leftFin.scale.set(0.2, 0.55, 1);
  leftFin.position.set(0.1, -0.25, 0.55);
  const rightFin = leftFin.clone();
  rightFin.position.z = -0.55;
  group.add(leftFin, rightFin);

  // Глаза
  for (const z of [0.38, -0.38]) {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(1.15, 0.15, z);
    group.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(1.32, 0.15, z * 1.05);
    group.add(pupil);
  }

  // Рот
  const mouth = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 6), pupilMat);
  mouth.position.set(1.5, -0.1, 0);
  group.add(mouth);

  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  group.position.set(
    (Math.random() - 0.5) * (TANK.w - 8),
    3 + Math.random() * (TANK.h - 6),
    (Math.random() - 0.5) * (TANK.d - 6));
  scene.add(group);

  const angle = Math.random() * Math.PI * 2;
  fishArray.push({
    mesh: group, tail, leftFin, rightFin,
    velocity: new THREE.Vector3(Math.cos(angle), (Math.random() - 0.5) * 0.3, Math.sin(angle)),
    speed: 2 + Math.random() * 3,
    tailSpeed: 4 + Math.random() * 5,
    phase: Math.random() * 6.28,
    wanderAngle: angle,
    wanderTimer: 0,
    targetFood: null,
    avoidanceRadius: 3 + Math.random() * 2
  });
  updateStats();
}

/* ==================== ПУЗЫРИ ==================== */
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xcceeff, transmission: 0.9, transparent: true, opacity: 0.5,
  roughness: 0, metalness: 0, thickness: 0.2
});
const bubbles = [];
function addBubbles(n) {
  for (let i = 0; i < n; i++) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.12 + Math.random() * 0.22, 10, 8), bubbleMat);
    resetBubble(m, true);
    scene.add(m);
    bubbles.push({ mesh: m, speed: 1.5 + Math.random() * 2,
      wob: 0.5 + Math.random(), wobSpeed: 1 + Math.random() * 2, phase: Math.random() * 6.28 });
  }
  updateStats();
}
function resetBubble(m, randY) {
  m.position.set((Math.random() - 0.5) * (TANK.w - 4),
                 randY ? Math.random() * TANK.h : 0.8,
                 (Math.random() - 0.5) * (TANK.d - 4));
}

/* ==================== КОМ (корм) ==================== */
const foodGeo = new THREE.SphereGeometry(0.3, 8, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xc98a3b, roughness: 0.9 });
const foodArray = [];
const raycaster = new THREE.Raycaster();
const clickPlane = new THREE.Plane();

let downPos = null;
renderer.domElement.addEventListener('pointerdown', e => downPos = { x: e.clientX, y: e.clientY });
renderer.domElement.addEventListener('pointerup', e => {
  if (!downPos) return;
  const dx = e.clientX - downPos.x, dy = e.clientY - downPos.y;
  downPos = null;
  if (dx * dx + dy * dy > 25) return; // это было вращение камеры, а не клик

  const ndc = new THREE.Vector2((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  raycaster.setFromCamera(ndc, camera);
  const normal = new THREE.Vector3();
  camera.getWorldDirection(normal);
  clickPlane.setFromNormalAndCoplanarPoint(normal, new THREE.Vector3(0, TANK.h / 2, 0));
  const pt = new THREE.Vector3();
  if (!raycaster.ray.intersectPlane(clickPlane, pt)) return;
  pt.x = THREE.MathUtils.clamp(pt.x, -TANK.w / 2 + 1, TANK.w / 2 - 1);
  pt.y = THREE.MathUtils.clamp(pt.y, 2, TANK.h - 1);
  pt.z = THREE.MathUtils.clamp(pt.z, -TANK.d / 2 + 1, TANK.d / 2 - 1);

  const m = new THREE.Mesh(foodGeo, foodMat);
  m.position.copy(pt);
  m.castShadow = true;
  scene.add(m);
  foodArray.push({ mesh: m, vy: 0 });
  updateStats();
});

/* ==================== UI ==================== */
const $ = id => document.getElementById(id);
function updateStats() {
  $('stat-fish').textContent = fishArray.length;
  $('stat-food').textContent = foodArray.length;
  $('stat-bub').textContent = bubbles.length;
}
$('btn-fish').onclick = () => { createFish(); };
$('btn-bubbles').onclick = () => addBubbles(10);
$('btn-light').onclick = () => { lightOn = !lightOn; sun.intensity = lightOn ? 1.0 : 0.15; };

/* ==================== АНИМАЦИЯ ==================== */
const clock = new THREE.Clock();
let frames = 0, fpsTimer = 0;
const tmp = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // --- Рыбки ---
  for (const f of fishArray) {
    const p = f.mesh.position;
    let steer = new THREE.Vector3();

    // Блуждание
    f.wanderTimer -= dt;
    if (f.wanderTimer <= 0) {
      f.wanderAngle = Math.random() * Math.PI * 2;
      f.wanderTimer = 2 + Math.random() * 3;
    }
    steer.x += Math.cos(f.wanderAngle) * 0.6;
    steer.z += Math.sin(f.wanderAngle) * 0.6;
    steer.y += Math.sin(t * 0.5 + f.phase) * 0.3;

    // Избегание столкновений
    for (const o of fishArray) {
      if (o === f) continue;
      tmp.subVectors(p, o.mesh.position);
      const d = tmp.length();
      if (d < f.avoidanceRadius && d > 0.001)
        steer.addScaledVector(tmp.normalize(), (f.avoidanceRadius - d) * 1.2);
    }

    // Корм
    if (f.targetFood && !foodArray.includes(f.targetFood)) f.targetFood = null;
    if (!f.targetFood) {
      let best = null, bestD = 15;
      for (const fd of foodArray) {
        const d = p.distanceTo(fd.mesh.position);
        if (d < bestD) { bestD = d; best = fd; }
      }
      if (best) f.targetFood = best;
    }
    if (f.targetFood) {
      tmp.subVectors(f.targetFood.mesh.position, p);
      const d = tmp.length();
      if (d < 1.2) {
        // Съедено! Рост +5%
        scene.remove(f.targetFood.mesh);
        foodArray.splice(foodArray.indexOf(f.targetFood), 1);
        f.mesh.scale.multiplyScalar(1.05);
        f.targetFood = null;
        updateStats();
      } else steer.addScaledVector(tmp.normalize(), f.speed * 1.6);
    }

    // Границы — плавное отражение
    const bx = TANK.w / 2 - 2.5, bz = TANK.d / 2 - 2;
    if (p.x > bx) steer.x -= 6; if (p.x < -bx) steer.x += 6;
    if (p.z > bz) steer.z -= 6; if (p.z < -bz) steer.z += 6;
    if (p.y > TANK.h - 2.5) steer.y -= 6; if (p.y < 1.8) steer.y += 6;

    // Скорость и движение
    f.velocity.lerp(steer.normalize().multiplyScalar(f.speed), 0.04);
    p.addScaledVector(f.velocity, dt);
    p.x = THREE.MathUtils.clamp(p.x, -bx, bx);
    p.y = THREE.MathUtils.clamp(p.y, 1.5, TANK.h - 1.5);
    p.z = THREE.MathUtils.clamp(p.z, -bz, bz);

    // Поворот в направлении движения
    const v = f.velocity;
    if (v.lengthSq() > 0.01) {
      const target = Math.atan2(-v.z, v.x);
      let diff = target - f.mesh.rotation.y;
      while (diff > Math.PI) diff -= Math.PI * 2;
      while (diff < -Math.PI) diff += Math.PI * 2;
      f.mesh.rotation.y += diff * Math.min(dt * 5, 1);
    }

    // Анимация хвоста и плавников
    const wag = Math.sin(t * f.tailSpeed + f.phase);
    f.tail.rotation.y = wag * 0.55;
    f.leftFin.rotation.x = wag * 0.35;
    f.rightFin.rotation.x = -wag * 0.35;
  }

  // --- Корм: гравитация + удаление на дне ---
  for (let i = foodArray.length - 1; i >= 0; i--) {
    const fd = foodArray[i];
    fd.vy -= 4 * dt;
    fd.vy = Math.max(fd.vy, -2.5);
    fd.mesh.position.y += fd.vy * dt;
    fd.mesh.rotation.y += dt * 2;
    if (fd.mesh.position.y <= 0.6) {
      scene.remove(fd.mesh);
      foodArray.splice(i, 1);
      updateStats();
    }
  }

  // --- Пузыри ---
  for (const b of bubbles) {
    b.mesh.position.y += b.speed * dt;
    b.mesh.position.x += Math.sin(t * b.wobSpeed + b.phase) * b.wob * dt;
    b.mesh.position.z += Math.cos(t * b.wobSpeed * 0.8 + b.phase) * b.wob * dt;
    if (b.mesh.position.y > TANK.h - 0.5) resetBubble(b.mesh, false);
  }

  // --- Покачивание водорослей ---
  for (const pl of plants) {
    pl.rotation.x = Math.sin(t * pl.userData.speed + pl.userData.phase) * 0.12;
    pl.rotation.z = Math.cos(t * pl.userData.speed * 0.9 + pl.userData.phase) * 0.12;
  }

  // FPS
  frames++; fpsTimer += dt;
  if (fpsTimer >= 1) { $('stat-fps').textContent = Math.round(frames / fpsTimer);
    frames = 0; fpsTimer = 0; }

  orbit.update();
  renderer.render(scene, camera);
}

/* ==================== СТАРТ ==================== */
for (let i = 0; i < 15; i++) createFish();
addBubbles(30);
updateStats();
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
|---|---|
| **🐟 Рыбки** | 15 штук, 8 цветовых схем, глаза с зрачками, рот, 3 плавника, анимированный хвост, масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, мягкое отражение от стен, блуждание с таймером, преследование корма (радиус 15), рост +5% при поедании |
| **🌊 Среда** | Стеклянный бак 36×24×20 с `transmission: 0.95` и wireframe-рамкой, процедурное песчаное дно, 8 деформированных камней, 12 качающихся кустов водорослей |
| **🫧 Пузыри** | 30 стартовых, стеклянный материал, синусоидальное покачивание, сброс на поверхности |
| **🍽️ Корм** | Клик (с отличием от drag-вращения камеры!), гравитация, поглощение рыбкой, удаление на дне |
| **💡 Свет** | Ambient + Directional с PCFSoft тенями 2048², 2 цветных PointLight, кнопка переключения |
| **🎮 Камера** | OrbitControls с damping, зум 10–60, `maxPolarAngle: π/1.8` |
| **🖥️ UI** | Glassmorphism-панели, градиентный заголовок, живой счётчик рыбок/корма/пузырей/FPS |

**Совет:** клики различаются от вращения камеры по порогу смещения 5px — корм не будет рассыпаться при вращении вида. Просто сохраните как `.html` и откройте в браузере! 🐠