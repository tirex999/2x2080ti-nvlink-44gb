

**Причина:** `init()` вызывается в начале скрипта и внутри него 30 раз вызывается `addBubble()`, который обращается к `bubbleGeo` / `bubbleMat` — а эти `const` объявлены *ниже* по тексту. Из-за temporal dead zone `const` ещё не инициализированы → `ReferenceError` → `init()` обрывается → `animate()` никогда не запускается → `renderer.render()` не вызывается ни разу, и через прозрачный canvas (`alpha:true`) виден только CSS-градиент и HTML-панели.

Исправление: перенёс вызовы `init(); animate();` в самый конец скрипта, чтобы все объявления уже были выполнены.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; }
  body {
    background: linear-gradient(180deg, #021a3a 0%, #0a3d7a 60%, #12559e 100%);
  }
  canvas { display: block; }

  .panel {
    position: absolute;
    background: rgba(10, 40, 80, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(120, 200, 255, 0.25);
    border-radius: 14px;
    color: #dff1ff;
    padding: 16px 18px;
    box-shadow: 0 8px 32px rgba(0, 20, 60, 0.4), inset 0 0 20px rgba(80, 180, 255, 0.08);
    user-select: none;
  }
  #info { top: 16px; left: 16px; max-width: 280px; }
  #info h1 {
    font-size: 20px; margin-bottom: 10px;
    background: linear-gradient(90deg, #4dd0ff, #a0e9ff, #ffd76e);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 8px rgba(80, 200, 255, 0.5));
  }
  #info ul { list-style: none; font-size: 12.5px; line-height: 1.7; opacity: 0.9; }
  #info li::before { content: "▸ "; color: #4dd0ff; }
  .btn-row { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px; }
  button {
    cursor: pointer; border: none; border-radius: 8px;
    padding: 8px 12px; font-size: 12.5px; font-weight: 600; color: #fff;
    background: linear-gradient(135deg, #1e7fd4, #12a3c9);
    box-shadow: 0 3px 10px rgba(20, 120, 200, 0.4);
    transition: transform .15s, box-shadow .15s, filter .15s;
  }
  button:hover { transform: translateY(-2px); filter: brightness(1.15); box-shadow: 0 6px 18px rgba(40, 180, 255, 0.6); }
  button:active { transform: translateY(0); }
  button.off { background: linear-gradient(135deg, #44586e, #2c3e50); }

  #stats { top: 16px; right: 16px; min-width: 150px; font-size: 13px; }
  #stats div { display: flex; justify-content: space-between; gap: 16px; line-height: 1.9; }
  #stats span:last-child { color: #4dd0ff; font-weight: 700; }
</style>
</head>
<body>

<div class="panel" id="info">
  <h1>🐠 3D Аквариум</h1>
  <ul>
    <li>ЛКМ + движение — вращение камеры</li>
    <li>ПКМ + движение — панорама</li>
    <li>Колесо — зум</li>
    <li><b>Клик по воде</b> — покормить рыбок</li>
  </ul>
  <div class="btn-row">
    <button id="btnFish">➕ Добавить рыбку</button>
    <button id="btnBubbles">💨 Больше пузырей</button>
    <button id="btnLight">💡 Свет: вкл</button>
  </div>
</div>

<div class="panel" id="stats">
  <div><span>Рыбки:</span><span id="fishCount">0</span></div>
  <div><span>Пузыри:</span><span id="bubbleCount">0</span></div>
  <div><span>FPS:</span><span id="fps">--</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* ============================== ГЛОБАЛЬНОЕ ============================== */
let scene, camera, renderer, controls, clock;
const fishArray = [], bubbles = [], foods = [], weeds = [];
let dirLight, feedPlane, dragStart = null;
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
const _v = new THREE.Vector3(), _obj = new THREE.Object3D();
const TANK = { w: 36, h: 24, d: 20 };
const BOUNDS = { x: 16, z: 9, yMin: 1.6, yMax: 22 };

const COLOR_SCHEMES = [
  { body: 0xff8c00, fin: 0xffb347 },
  { body: 0x1e90ff, fin: 0x87cefa },
  { body: 0xffd700, fin: 0xff4500 },
  { body: 0x9370db, fin: 0xda70d6 },
  { body: 0xdc143c, fin: 0xff6347 },
  { body: 0x2e8b57, fin: 0x98fb98 },
  { body: 0xff69b4, fin: 0xffb6c1 },
  { body: 0xd4af37, fin: 0xf5deb3 },
];

/* ============================== ОКРУЖЕНИЕ ============================== */
function buildTank() {
  const glass = new THREE.Mesh(
    new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d),
    new THREE.MeshPhysicalMaterial({
      color: 0xbfe8ff, transmission: 0.95, transparent: true, opacity: 0.25,
      roughness: 0.05, metalness: 0, thickness: 0.5,
      side: THREE.DoubleSide, depthWrite: false
    })
  );
  glass.position.y = TANK.h / 2;
  scene.add(glass);

  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(glass.geometry),
    new THREE.LineBasicMaterial({ color: 0x9fd8ff, transparent: true, opacity: 0.6 })
  );
  edges.position.copy(glass.position);
  scene.add(edges);
}

function buildSand() {
  const geo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 26);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i);
    pos.setZ(i,
      Math.sin(x * 0.5) * Math.cos(y * 0.4) * 0.18 +
      Math.sin(x * 1.7 + y * 2.3) * 0.08 +
      (Math.random() - 0.5) * 0.06);
  }
  geo.computeVertexNormals();
  const sand = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0xd9c27f, roughness: 1 }));
  sand.rotation.x = -Math.PI / 2;
  sand.receiveShadow = true;
  scene.add(sand);
}

function buildRocks() {
  for (let i = 0; i < 8; i++) {
    const r = 0.8 + Math.random() * 1.2;
    const geo = new THREE.DodecahedronGeometry(r, 0);
    const pos = geo.attributes.position;
    for (let j = 0; j < pos.count; j++) {
      pos.setXYZ(j,
        pos.getX(j) * (0.8 + Math.random() * 0.4),
        pos.getY(j) * (0.8 + Math.random() * 0.4),
        pos.getZ(j) * (0.8 + Math.random() * 0.4));
    }
    geo.computeVertexNormals();
    const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(0.08, 0.15, 0.25 + Math.random() * 0.2),
      roughness: 0.95
    }));
    rock.position.set((Math.random() - 0.5) * 30, r * 0.45, (Math.random() - 0.5) * 16);
    rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
    rock.castShadow = rock.receiveShadow = true;
    scene.add(rock);
  }
}

function buildWeeds() {
  for (let i = 0; i < 12; i++) {
    const h = 3 + Math.random() * 4.5;
    const pts = [];
    const lean = (Math.random() - 0.5) * 1.5;
    for (let j = 0; j <= 4; j++) {
      const t = j / 4;
      pts.push(new THREE.Vector3(
        lean * t * t + Math.sin(t * 5 + i) * 0.3,
        t * h,
        Math.cos(t * 4 + i) * 0.3
      ));
    }
    const geo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 20, 0.13, 5, false);
    const weed = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(0.32 + Math.random() * 0.1, 0.7, 0.3 + Math.random() * 0.15),
      roughness: 0.8
    }));
    weed.position.set((Math.random() - 0.5) * 30, 0.1, (Math.random() - 0.5) * 16);
    weed.castShadow = true;
    weed.userData.phase = Math.random() * Math.PI * 2;
    scene.add(weed);
    weeds.push(weed);
  }
}

/* ============================== РЫБКИ ============================== */
function createFishMesh(scheme) {
  const g = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.45, metalness: 0.15 });
  const finMat  = new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.6, transparent: true, opacity: 0.85, side: THREE.DoubleSide });

  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 18, 14), bodyMat);
  body.scale.set(0.65, 0.85, 1.5);
  body.castShadow = true;
  g.add(body);

  const stripe = new THREE.Mesh(new THREE.SphereGeometry(0.98, 18, 14),
    new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.6 }));
  stripe.scale.set(0.62, 0.45, 1.45);
  stripe.position.y = -0.32;
  g.add(stripe);

  const eyeGeo = new THREE.SphereGeometry(0.16, 10, 8);
  const pupilGeo = new THREE.SphereGeometry(0.08, 8, 6);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a, roughness: 0.1 });
  [-1, 1].forEach(s => {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(0.32 * s, 0.22, 0.95);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(0.07, 0, 0.1);
    eye.add(pupil);
    g.add(eye);
  });

  const tailPivot = new THREE.Group();
  tailPivot.position.z = -1.35;
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.55, 1.1, 8), finMat);
  tail.rotation.x = Math.PI / 2;
  tail.scale.y = 0.22;
  tail.position.z = -0.5;
  tailPivot.add(tail);
  g.add(tailPivot);

  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.9, 6), finMat);
  topFin.rotation.x = -Math.PI / 2.4;
  topFin.scale.z = 0.25;
  topFin.position.set(0, 0.7, -0.1);
  g.add(topFin);

  const finGeo = new THREE.ConeGeometry(0.3, 0.7, 6);
  const leftFin = new THREE.Mesh(finGeo, finMat);
  leftFin.rotation.z = Math.PI / 2;
  leftFin.scale.x = 0.25;
  leftFin.position.set(-0.55, -0.1, 0.15);
  const rightFin = new THREE.Mesh(finGeo, finMat);
  rightFin.rotation.z = -Math.PI / 2;
  rightFin.scale.x = 0.25;
  rightFin.position.set(0.55, -0.1, 0.15);
  g.add(leftFin, rightFin);

  return { group: g, tailPivot, tail, topFin, leftFin, rightFin };
}

function addFish() {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const parts = createFishMesh(scheme);
  const scale = 0.6 + Math.random() * 0.6;
  parts.group.scale.setScalar(scale);
  parts.group.position.set(
    (Math.random() - 0.5) * 28,
    3 + Math.random() * 17,
    (Math.random() - 0.5) * 14
  );
  scene.add(parts.group);

  const velocity = new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.3, Math.random() - 0.5)
    .normalize().multiplyScalar(2);

  fishArray.push({
    mesh: parts.group,
    tail: parts.tail,
    tailPivot: parts.tailPivot,
    topFin: parts.topFin,
    leftFin: parts.leftFin,
    rightFin: parts.rightFin,
    velocity,
    speed: 1.6 + Math.random() * 1.6,
    tailSpeed: 6 + Math.random() * 6,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 2.5 + Math.random() * 1.5,
    wanderT: Math.random() * 4
  });
  updateCounts();
}

function updateFish(dt, t) {
  for (const f of fishArray) {
    const pos = f.mesh.position;

    f.wanderT -= dt;
    if (f.wanderT <= 0) {
      _v.set(Math.random() - 0.5, (Math.random() - 0.5) * 0.4, Math.random() - 0.5)
        .normalize().multiplyScalar(f.speed * 0.7);
      f.velocity.add(_v);
      f.wanderT = 2 + Math.random() * 4;
    }

    f.targetFood = null;
    let bestDist = 15;
    for (const food of foods) {
      const d = pos.distanceTo(food.mesh.position);
      if (d < bestDist) { bestDist = d; f.targetFood = food; }
    }
    if (f.targetFood) {
      _v.copy(f.targetFood.mesh.position).sub(pos).normalize();
      f.velocity.addScaledVector(_v, f.speed * 2.2 * dt);
      if (bestDist < 1.4 * f.mesh.scale.x) eatFood(f, f.targetFood);
    }

    for (const o of fishArray) {
      if (o === f) continue;
      const d = pos.distanceTo(o.mesh.position);
      if (d < f.avoidanceRadius && d > 0.001) {
        _v.copy(pos).sub(o.mesh.position).normalize();
        f.velocity.addScaledVector(_v, (f.avoidanceRadius - d) * dt * 3);
      }
    }

    if (pos.x >  BOUNDS.x)  f.velocity.x -= (pos.x - BOUNDS.x) * dt * 4;
    if (pos.x < -BOUNDS.x)  f.velocity.x += (-BOUNDS.x - pos.x) * dt * 4;
    if (pos.z >  BOUNDS.z)  f.velocity.z -= (pos.z - BOUNDS.z) * dt * 4;
    if (pos.z < -BOUNDS.z)  f.velocity.z += (-BOUNDS.z - pos.z) * dt * 4;
    if (pos.y >  BOUNDS.yMax)  f.velocity.y -= (pos.y - BOUNDS.yMax) * dt * 4;
    if (pos.y <  BOUNDS.yMin)  f.velocity.y += (BOUNDS.yMin - pos.y) * dt * 4;

    f.velocity.normalize().multiplyScalar(f.speed);
    pos.addScaledVector(f.velocity, dt);
    pos.x = THREE.MathUtils.clamp(pos.x, -BOUNDS.x, BOUNDS.x);
    pos.y = THREE.MathUtils.clamp(pos.y, BOUNDS.yMin, BOUNDS.yMax);
    pos.z = THREE.MathUtils.clamp(pos.z, -BOUNDS.z, BOUNDS.z);

    _obj.position.copy(pos);
    _obj.lookAt(_v.copy(pos).add(f.velocity));
    f.mesh.quaternion.slerp(_obj.quaternion, Math.min(1, dt * 5));

    f.tailPivot.rotation.z = Math.sin(t * f.tailSpeed + f.phase) * 0.55;
    f.topFin.rotation.x = -Math.PI / 2.4 + Math.sin(t * f.tailSpeed * 0.7 + f.phase) * 0.2;
    f.leftFin.rotation.y  =  Math.sin(t * f.tailSpeed * 0.8 + f.phase) * 0.35;
    f.rightFin.rotation.y = -Math.sin(t * f.tailSpeed * 0.8 + f.phase) * 0.35;
    f.mesh.rotation.y += Math.sin(t * f.tailSpeed + f.phase) * 0.004;
  }
}

/* ============================== КОРМ ============================== */
const foodGeo = new THREE.SphereGeometry(0.25, 10, 8);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xff7722, emissive: 0xcc4400, emissiveIntensity: 0.6 });

function spawnFood(e) {
  ndc.x = (e.clientX / innerWidth) * 2 - 1;
  ndc.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(ndc, camera);
  const hits = raycaster.intersectObject(feedPlane);
  if (!hits.length) return;
  const p = hits[0].point;
  p.x = THREE.MathUtils.clamp(p.x, -BOUNDS.x + 1, BOUNDS.x - 1);
  p.y = THREE.MathUtils.clamp(p.y, BOUNDS.yMin + 1, BOUNDS.yMax - 1);
  p.z = THREE.MathUtils.clamp(p.z, -BOUNDS.z + 1, BOUNDS.z - 1);
  const mesh = new THREE.Mesh(foodGeo, foodMat);
  mesh.position.copy(p);
  scene.add(mesh);
  foods.push({ mesh, velocity: new THREE.Vector3(0, 0, 0) });
}

function eatFood(fish, food) {
  scene.remove(food.mesh);
  foods.splice(foods.indexOf(food), 1);
  if (fish.targetFood === food) fish.targetFood = null;
  const s = fish.mesh.scale.x * 1.05;
  if (s < 2.6) fish.mesh.scale.setScalar(s);
}

function updateFoods(dt) {
  for (let i = foods.length - 1; i >= 0; i--) {
    const f = foods[i];
    f.velocity.y -= 9.8 * 0.35 * dt;
    f.mesh.position.addScaledVector(f.velocity, dt);
    f.mesh.rotation.x += dt * 2;
    if (f.mesh.position.y < 0.5) {
      scene.remove(f.mesh);
      foods.splice(i, 1);
    }
  }
}

/* ============================== ПУЗЫРИ ============================== */
const bubbleGeo = new THREE.SphereGeometry(0.15, 10, 8);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xffffff, transmission: 0.9, transparent: true, opacity: 0.35,
  roughness: 0, metalness: 0
});

function addBubble() {
  const mesh = new THREE.Mesh(bubbleGeo, bubbleMat);
  const b = {
    mesh,
    x0: (Math.random() - 0.5) * 30,
    z0: (Math.random() - 0.5) * 16,
    speed: 1.2 + Math.random() * 2.2,
    phase: Math.random() * Math.PI * 2,
    scale: 0.5 + Math.random()
  };
  mesh.scale.setScalar(b.scale);
  mesh.position.set(b.x0, Math.random() * TANK.h, b.z0);
  scene.add(mesh);
  bubbles.push(b);
  updateCounts();
}

function updateBubbles(dt, t) {
  for (const b of bubbles) {
    b.mesh.position.y += b.speed * dt;
    b.mesh.position.x = b.x0 + Math.sin(t * 2 + b.phase) * 0.45;
    b.mesh.position.z = b.z0 + Math.cos(t * 1.7 + b.phase) * 0.45;
    if (b.mesh.position.y > TANK.h - 1) b.mesh.position.y = 0.4;
  }
}

/* ============================== UI ============================== */
let frames = 0, fpsTime = 0;
function updateCounts() {
  document.getElementById('fishCount').textContent = fishArray.length;
  document.getElementById('bubbleCount').textContent = bubbles.length;
}
function updateFPS(dt) {
  frames++; fpsTime += dt;
  if (fpsTime >= 0.5) {
    document.getElementById('fps').textContent = Math.round(frames / fpsTime);
    frames = 0; fpsTime = 0;
  }
}

/* ============================== ЦИКЛ ============================== */
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clockDelta(), 0.05);
  const t = performance.now() / 1000;

  updateFish(dt, t);
  updateFoods(dt);
  updateBubbles(dt, t);

  for (const w of weeds) {
    w.rotation.x = Math.sin(t * 0.8 + w.userData.phase) * 0.07;
    w.rotation.z = Math.cos(t * 0.6 + w.userData.phase) * 0.07;
  }

  controls.update();
  renderer.render(scene, camera);
  updateFPS(dt);
}

let lastTime = performance.now();
function clockDelta() {
  const now = performance.now();
  const d = (now - lastTime) / 1000;
  lastTime = now;
  return d;
}

/* ============================== ИНИЦИАЛИЗАЦИЯ ============================== */
function init() {
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0a3d7a, 0.011);

  camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 300);
  camera.position.set(0, 20, 44);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 11, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 10;
  controls.maxDistance = 60;
  controls.maxPolarAngle = Math.PI / 1.8;

  scene.add(new THREE.AmbientLight(0x404040, 0.4));

  dirLight = new THREE.DirectionalLight(0xfff3dc, 1.0);
  dirLight.position.set(18, 40, 12);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(2048, 2048);
  dirLight.shadow.camera.left = -28; dirLight.shadow.camera.right = 28;
  dirLight.shadow.camera.top = 28;   dirLight.shadow.camera.bottom = -28;
  dirLight.shadow.camera.far = 100;
  scene.add(dirLight);

  const p1 = new THREE.PointLight(0x00ccff, 0.55, 70); p1.position.set(-13, 18, -8);
  const p2 = new THREE.PointLight(0x0066ff, 0.55, 70); p2.position.set(13, 6, 9);
  scene.add(p1, p2);

  buildTank();
  buildSand();
  buildRocks();
  buildWeeds();

  for (let i = 0; i < 15; i++) addFish();
  for (let i = 0; i < 30; i++) addBubble();

  feedPlane = new THREE.Mesh(
    new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d),
    new THREE.MeshBasicMaterial({ visible: false })
  );
  feedPlane.position.y = TANK.h / 2;
  scene.add(feedPlane);

  addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });
  renderer.domElement.addEventListener('mousedown', e => dragStart = { x: e.clientX, y: e.clientY });
  renderer.domElement.addEventListener('mouseup', e => {
    if (dragStart && Math.hypot(e.clientX - dragStart.x, e.clientY - dragStart.y) < 5) spawnFood(e);
    dragStart = null;
  });

  document.getElementById('btnFish').onclick = () => addFish();
  document.getElementById('btnBubbles').onclick = () => { for (let i = 0; i < 10; i++) addBubble(); };
  const btnL = document.getElementById('btnLight');
  let lightOn = true;
  btnL.onclick = () => {
    lightOn = !lightOn;
    dirLight.intensity = lightOn ? 1.0 : 0.12;
    btnL.textContent = '💡 Свет: ' + (lightOn ? 'вкл' : 'выкл');
    btnL.classList.toggle('off', !lightOn);
  };
  updateCounts();
}

/* ============================== СТАРТ (после всех объявлений) ============================== */
init();
animate();
</script>
</body>
</html>
```