

# 🐠 3D Аквариум — полный код

Готовый файл `aquarium.html` — просто сохраните и откройте в браузере:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #001a33; }
  canvas { display: block; }

  .panel {
    position: absolute;
    background: rgba(10, 30, 60, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(120, 200, 255, 0.25);
    border-radius: 14px;
    padding: 16px 20px;
    color: #d8f0ff;
    box-shadow: 0 8px 32px rgba(0, 40, 90, 0.5), inset 0 0 20px rgba(80, 180, 255, 0.05);
    z-index: 10;
  }

  #info { top: 20px; left: 20px; max-width: 300px; }
  #info h1 {
    font-size: 22px; margin-bottom: 10px;
    background: linear-gradient(90deg, #4dd0ff, #7bffb0, #ffd76e);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 8px rgba(80, 200, 255, 0.5));
  }
  #info ul { list-style: none; font-size: 13px; line-height: 1.7; opacity: 0.85; }
  #info li::before { content: "▸ "; color: #4dd0ff; }

  .btn {
    display: inline-block; margin-top: 8px; margin-right: 6px;
    padding: 8px 16px; border: none; border-radius: 20px;
    font-size: 13px; font-weight: 600; cursor: pointer;
    color: #fff; transition: all .25s ease;
    background: linear-gradient(135deg, #1e6fd9, #2ec4b6);
    box-shadow: 0 4px 14px rgba(30, 110, 217, 0.4);
  }
  .btn:hover { transform: translateY(-2px) scale(1.04); box-shadow: 0 6px 22px rgba(46, 196, 182, 0.7); }
  .btn:active { transform: translateY(0) scale(0.98); }
  .btn.off { background: linear-gradient(135deg, #555, #333); box-shadow: 0 4px 14px rgba(0,0,0,.4); }

  #stats { top: 20px; right: 20px; text-align: right; min-width: 150px; }
  #stats .row { font-size: 15px; margin: 4px 0; }
  #stats .val { color: #7bffb0; font-weight: 700; font-size: 18px; }
  #fps { color: #ffd76e; }

  #hint {
    bottom: 20px; left: 50%; transform: translateX(-50%);
    font-size: 13px; padding: 10px 22px; opacity: 0.75;
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
    <li>Клик по воде — бросить корм</li>
  </ul>
  <button class="btn" id="btnFish">➕ Добавить рыбку</button>
  <button class="btn" id="btnBubbles">💧 Больше пузырей</button>
  <button class="btn" id="btnLight">💡 Свет: ВКЛ</button>
</div>

<div class="panel" id="stats">
  <div class="row">Рыбки: <span class="val" id="fishCount">0</span></div>
  <div class="row">FPS: <span class="val" id="fps">--</span></div>
</div>

<div class="panel" id="hint">🍽️ Кликните по аквариуму, чтобы покормить рыбок!</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ==================== БАЗА ====================
const TANK = { w: 36, h: 20, d: 24 };
const BX = TANK.w/2 - 1.5, BY = TANK.h/2 - 1.5, BZ = TANK.d/2 - 1.5;
const FLOOR_Y = -TANK.h/2 + 0.6;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

const camera = new THREE.PerspectiveCamera(55, innerWidth/innerHeight, 0.1, 200);
camera.position.set(0, 8, 42);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Градиентный фон
const bgCanvas = document.createElement('canvas');
bgCanvas.width = 2; bgCanvas.height = 256;
const bctx = bgCanvas.getContext('2d');
const grad = bctx.createLinearGradient(0, 0, 0, 256);
grad.addColorStop(0, '#0a2a55'); grad.addColorStop(1, '#031225');
bctx.fillStyle = grad; bctx.fillRect(0, 0, 2, 256);
scene.background = new THREE.CanvasTexture(bgCanvas);

// ==================== КАМЕРА / УПРАВЛЕНИЕ ====================
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.target.set(0, 0, 0);

// ==================== ОСВЕЩЕНИЕ ====================
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sun = new THREE.DirectionalLight(0xcfe8ff, 1.1);
sun.position.set(15, 30, 10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -25; sun.shadow.camera.right = 25;
sun.shadow.camera.top = 25;  sun.shadow.camera.bottom = -25;
scene.add(sun);

const p1 = new THREE.PointLight(0x33ccff, 0.6, 60); p1.position.set(-12, 6, 8);  scene.add(p1);
const p2 = new THREE.PointLight(0x2266ff, 0.6, 60); p2.position.set(12, 6, -8);  scene.add(p2);

// ==================== АКВАРИУМ ====================
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xaaddff, transmission: 0.95, transparent: true, opacity: 0.15,
  roughness: 0.05, metalness: 0, side: THREE.DoubleSide, depthWrite: false
});
const glassBox = new THREE.Mesh(new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d), glassMat);
scene.add(glassBox);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(glassBox.geometry),
  new THREE.LineBasicMaterial({ color: 0x88ccee, transparent: true, opacity: 0.5 })
);
scene.add(edges);

// Песчаное дно с неровностями
const sandGeo = new THREE.PlaneGeometry(TANK.w - 0.5, TANK.d - 0.5, 40, 40);
{
  const pos = sandGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i);
    pos.setZ(i, Math.sin(x * 0.5) * Math.cos(y * 0.4) * 0.25 + Math.sin(x * 1.7 + y) * 0.1);
  }
  sandGeo.computeVertexNormals();
}
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({ color: 0xd8c08a, roughness: 1 }));
sand.rotation.x = -Math.PI / 2;
sand.position.y = FLOOR_Y;
sand.receiveShadow = true;
scene.add(sand);

// Камни
for (let i = 0; i < 8; i++) {
  const r = 0.7 + Math.random() * 1.2;
  const g = new THREE.DodecahedronGeometry(r, 1);
  const p = g.attributes.position;
  for (let j = 0; j < p.count; j++) {
    p.setXYZ(j,
      p.getX(j) * (0.8 + Math.random() * 0.4),
      p.getY(j) * (0.6 + Math.random() * 0.5),
      p.getZ(j) * (0.8 + Math.random() * 0.4));
  }
  g.computeVertexNormals();
  const rock = new THREE.Mesh(g, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.2, 0.25 + Math.random() * 0.15),
    roughness: 0.9, flatShading: true
  }));
  rock.position.set((Math.random() - 0.5) * (TANK.w - 6), FLOOR_Y + r * 0.3, (Math.random() - 0.5) * (TANK.d - 6));
  rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
  rock.castShadow = rock.receiveShadow = true;
  scene.add(rock);
}

// Водоросли
const weeds = [];
for (let i = 0; i < 12; i++) {
  const h = 3 + Math.random() * 5;
  const pts = [];
  const baseX = (Math.random() - 0.5) * (TANK.w - 8);
  const baseZ = (Math.random() - 0.5) * (TANK.d - 8);
  for (let j = 0; j <= 6; j++) {
    const t = j / 6;
    pts.push(new THREE.Vector3(
      baseX + Math.sin(t * 4 + i) * 0.5 * t,
      FLOOR_Y + h * t,
      baseZ + Math.cos(t * 3 + i) * 0.5 * t
    ));
  }
  const weed = new THREE.Mesh(
    new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 12, 0.14 + Math.random() * 0.08, 6),
    new THREE.MeshStandardMaterial({ color: new THREE.Color().setHSL(0.32 + Math.random() * 0.1, 0.7, 0.3), roughness: 0.8 })
  );
  weed.castShadow = true;
  scene.add(weed);
  weeds.push({ mesh: weed, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.8 });
}

// ==================== РЫБКИ ====================
const COLOR_SCHEMES = [
  { body: 0xff7733, fin: 0xffaa55 }, // оранжевая
  { body: 0x3388ff, fin: 0x66bbff }, // синяя
  { body: 0xffcc00, fin: 0xff4422 }, // жёлто-красная
  { body: 0xaa44ff, fin: 0xcc88ff }, // фиолетовая
  { body: 0xff3344, fin: 0xff7788 }, // красная
  { body: 0x33cc66, fin: 0x88ffaa }, // зелёная
  { body: 0xff66aa, fin: 0xffaacc }, // розовая
  { body: 0xffc84d, fin: 0xfff0b0 }  // золотая
];

const fishArray = [];
const bodyGeo   = new THREE.SphereGeometry(1, 12, 10);
const eyeGeo    = new THREE.SphereGeometry(0.16, 8, 8);
const pupilGeo  = new THREE.SphereGeometry(0.08, 6, 6);
const tailGeo   = new THREE.ConeGeometry(0.55, 1.1, 8);
const finGeo    = new THREE.ConeGeometry(0.4, 0.9, 4);

function createFish(x, y, z) {
  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
  const scale = 0.6 + Math.random() * 0.6;

  const group = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.35, metalness: 0.25 });
  const finMat  = new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.5, transparent: true, opacity: 0.85 });

  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.scale.set(1.7, 0.85, 0.55);
  body.castShadow = true;
  group.add(body);

  // Хвост (пивот на стыке с телом)
  const tailPivot = new THREE.Group();
  tailPivot.position.x = -1.6;
  const tail = new THREE.Mesh(tailGeo, finMat);
  tail.rotation.z = Math.PI / 2;
  tail.position.x = -0.55;
  tail.scale.set(1, 1.4, 0.4);
  tailPivot.add(tail);
  group.add(tailPivot);

  // Плавники
  const topFin = new THREE.Mesh(finGeo, finMat);
  topFin.rotation.z = -0.5; topFin.scale.z = 0.3;
  topFin.position.set(0, 0.75, 0);
  group.add(topFin);

  const leftFin = new THREE.Mesh(finGeo, finMat);
  leftFin.rotation.x = Math.PI / 2; leftFin.rotation.y = 0.6; leftFin.scale.z = 0.35;
  leftFin.position.set(0.1, -0.2, 0.45);
  group.add(leftFin);

  const rightFin = new THREE.Mesh(finGeo, finMat);
  rightFin.rotation.x = -Math.PI / 2; rightFin.rotation.y = -0.6; rightFin.scale.z = 0.35;
  rightFin.position.set(0.1, -0.2, -0.45);
  group.add(rightFin);

  // Глаза
  [-1, 1].forEach(side => {
    const eye = new THREE.Mesh(eyeGeo, new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 }));
    eye.position.set(1.15, 0.2, side * 0.38);
    group.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, new THREE.MeshStandardMaterial({ color: 0x111111 }));
    pupil.position.set(1.28, 0.2, side * 0.44);
    group.add(pupil);
  });

  group.scale.setScalar(scale);
  group.position.set(x, y, z);
  scene.add(group);

  const angle = Math.random() * Math.PI * 2;
  fishArray.push({
    mesh: group, tail: tailPivot, topFin, leftFin, rightFin,
    velocity: new THREE.Vector3(Math.cos(angle), 0, Math.sin(angle)),
    speed: 2.5 + Math.random() * 2.5,
    tailSpeed: 6 + Math.random() * 4,
    phase: Math.random() * Math.PI * 2,
    wanderTimer: Math.random() * 3,
    targetFood: null,
    avoidanceRadius: 2.5 + Math.random() * 1.5,
    yaw: angle
  });
}

for (let i = 0; i < 15; i++) {
  createFish((Math.random()-0.5)*(TANK.w-6), (Math.random()-0.5)*(TANK.h-6), (Math.random()-0.5)*(TANK.d-6));
}

// ==================== КОРМ ====================
const foodArray = [];
const foodGeo = new THREE.SphereGeometry(0.22, 8, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0x8a5a2a, roughness: 0.9 });

function spawnFood(pos) {
  const f = new THREE.Mesh(foodGeo, foodMat);
  f.position.copy(pos);
  f.castShadow = true;
  scene.add(f);
  foodArray.push({ mesh: f, vel: new THREE.Vector3((Math.random()-0.5)*0.5, 0, (Math.random()-0.5)*0.5), age: 0 });
}

// ==================== БУБЛЬКИ ====================
const bubbleArray = [];
const bubbleGeo = new THREE.SphereGeometry(0.15, 10, 8);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xbbddff, transmission: 0.9, transparent: true, opacity: 0.35,
  roughness: 0, metalness: 0, clearcoat: 1
});

function addBubble() {
  const b = new THREE.Mesh(bubbleGeo, bubbleMat);
  const s = 0.4 + Math.random() * 1.2;
  b.scale.setScalar(s);
  b.position.set((Math.random()-0.5)*(TANK.w-3), FLOOR_Y + Math.random()*TANK.h, (Math.random()-0.5)*(TANK.d-3));
  scene.add(b);
  bubbleArray.push({ mesh: b, speed: 1 + Math.random() * 2, phase: Math.random() * Math.PI * 2, baseX: b.position.x, baseZ: b.position.z });
}
for (let i = 0; i < 30; i++) addBubble();

// ==================== КЛИК / КОРМЛЕНИЕ ====================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let downPos = null;

renderer.domElement.addEventListener('pointerdown', e => { downPos = { x: e.clientX, y: e.clientY }; });
renderer.domElement.addEventListener('pointerup', e => {
  if (!downPos) return;
  const dx = e.clientX - downPos.x, dy = e.clientY - downPos.y;
  downPos = null;
  if (dx*dx + dy*dy > 25) return; // это было вращение, не клик

  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObject(glassBox);
  if (hits.length) {
    const p = hits[0].point.clone().lerp(new THREE.Vector3(0, 0, 0), 0.35);
    p.x = THREE.MathUtils.clamp(p.x, -BX + 1, BX - 1);
    p.y = THREE.MathUtils.clamp(p.y, FLOOR_Y + 1, BY - 1);
    p.z = THREE.MathUtils.clamp(p.z, -BZ + 1, BZ - 1);
    spawnFood(p);
  }
});

// ==================== UI ====================
document.getElementById('btnFish').onclick = () =>
  createFish((Math.random()-0.5)*(TANK.w-8), TANK.h/2 - 3, (Math.random()-0.5)*(TANK.d-8));
document.getElementById('btnBubbles').onclick = () => { for (let i = 0; i < 10; i++) addBubble(); };
let lightOn = true;
document.getElementById('btnLight').onclick = function() {
  lightOn = !lightOn;
  sun.intensity = lightOn ? 1.1 : 0.15;
  this.textContent = lightOn ? '💡 Свет: ВКЛ' : '💡 Свет: ВЫКЛ';
  this.classList.toggle('off', !lightOn);
};

// ==================== АНИМАЦИЯ ====================
const clock = new THREE.Clock();
let fpsFrames = 0, fpsTime = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // FPS
  fpsFrames++; fpsTime += dt;
  if (fpsTime >= 0.5) {
    document.getElementById('fps').textContent = Math.round(fpsFrames / fpsTime);
    fpsFrames = 0; fpsTime = 0;
  }
  document.getElementById('fishCount').textContent = fishArray.length;

  // --- Рыбки ---
  for (let i = 0; i < fishArray.length; i++) {
    const f = fishArray[i];
    const v = f.velocity;

    // Поиск корма
    f.targetFood = null;
    let best = 15;
    for (const fd of foodArray) {
      const d = f.mesh.position.distanceTo(fd.mesh.position);
      if (d < best) { best = d; f.targetFood = fd; }
    }

    if (f.targetFood) {
      const dir = f.targetFood.mesh.position.clone().sub(f.mesh.position).normalize();
      v.lerp(dir.multiplyScalar(f.speed * 1.6), 0.04);
      // Съедание
      if (best < 1.0) {
        scene.remove(f.targetFood.mesh);
        foodArray.splice(foodArray.indexOf(f.targetFood), 1);
        f.mesh.scale.multiplyScalar(1.05); // рост на 5%
      }
    } else {
      // Случайное блуждание
      f.wanderTimer -= dt;
      if (f.wanderTimer <= 0) {
        f.wanderTimer = 2 + Math.random() * 4;
        v.add(new THREE.Vector3((Math.random()-0.5), (Math.random()-0.5)*0.5, (Math.random()-0.5)).multiplyScalar(f.speed * 0.6));
      }
      v.normalize().multiplyScalar(f.speed);
    }

    // Избегание других рыбок
    for (let j = 0; j < fishArray.length; j++) {
      if (i === j) continue;
      const other = fishArray[j];
      const diff = f.mesh.position.clone().sub(other.mesh.position);
      const dist = diff.length();
      if (dist < f.avoidanceRadius && dist > 0.001) {
        v.add(diff.normalize().multiplyScalar((f.avoidanceRadius - dist) * 2 * dt * 4));
      }
    }

    // Отражение от стен (плавное)
    const p = f.mesh.position;
    if (p.x >  BX - 1) v.x -= (p.x - (BX-1)) * 3 * dt * 8;
    if (p.x < -BX + 1) v.x -= (p.x - (-BX+1)) * 3 * dt * 8;
    if (p.y >  BY - 1) v.y -= (p.y - (BY-1)) * 3 * dt * 8;
    if (p.y < FLOOR_Y + 1.5) v.y -= (p.y - (FLOOR_Y+1.5)) * 3 * dt * 8;
    if (p.z >  BZ - 1) v.z -= (p.z - (BZ-1)) * 3 * dt * 8;
    if (p.z < -BZ + 1) v.z -= (p.z - (-BZ+1)) * 3 * dt * 8;

    p.addScaledVector(v, dt);

    // Поворот в направлении движения (плавный)
    const targetYaw = Math.atan2(-v.z, v.x);
    let dy = targetYaw - f.yaw;
    while (dy >  Math.PI) dy -= Math.PI * 2;
    while (dy < -Math.PI) dy += Math.PI * 2;
    f.yaw += dy * Math.min(1, dt * 4);
    f.mesh.rotation.y = f.yaw;
    f.mesh.rotation.z = THREE.MathUtils.clamp(dy * 0.5, -0.4, 0.4); // наклон при повороте
    f.mesh.rotation.x = THREE.MathUtils.clamp(v.y * 0.15, -0.3, 0.3);

    // Анимация хвоста и плавников
    const wag = Math.sin(t * f.tailSpeed + f.phase);
    f.tail.rotation.y = wag * 0.55;
    f.topFin.rotation.z = -0.5 + Math.sin(t * f.tailSpeed * 0.7 + f.phase) * 0.2;
    f.leftFin.rotation.y  =  0.6 + Math.sin(t * f.tailSpeed + f.phase) * 0.35;
    f.rightFin.rotation.y = -0.6 - Math.sin(t * f.tailSpeed + f.phase) * 0.35;
  }

  // --- Корм ---
  for (let i = foodArray.length - 1; i >= 0; i--) {
    const fd = foodArray[i];
    fd.vel.y -= 3.5 * dt; // гравитация
    fd.mesh.position.addScaledVector(fd.vel, dt);
    fd.age += dt;
    if (fd.mesh.position.y < FLOOR_Y + 0.25 || fd.age > 25) {
      scene.remove(fd.mesh);
      foodArray.splice(i, 1);
    }
  }

  // --- Пузыри ---
  for (const b of bubbleArray) {
    b.mesh.position.y += b.speed * dt;
    b.mesh.position.x = b.baseX + Math.sin(t * 2 + b.phase) * 0.5;
    b.mesh.position.z = b.baseZ + Math.cos(t * 1.7 + b.phase) * 0.5;
    if (b.mesh.position.y > BY - 0.5) {
      b.mesh.position.y = FLOOR_Y + 0.5;
      b.baseX = (Math.random()-0.5)*(TANK.w-3);
      b.baseZ = (Math.random()-0.5)*(TANK.d-3);
      b.mesh.position.x = b.baseX; b.mesh.position.z = b.baseZ;
    }
  }

  // --- Водоросли ---
  for (const w of weeds) {
    w.mesh.rotation.x = Math.sin(t * w.speed + w.phase) * 0.08;
    w.mesh.rotation.z = Math.cos(t * w.speed * 0.8 + w.phase) * 0.08;
  }

  // Лёгкое мерцание подводных огней
  p1.intensity = 0.5 + Math.sin(t * 1.3) * 0.15;
  p2.intensity = 0.5 + Math.cos(t * 1.1) * 0.15;

  controls.update();
  renderer.render(scene, camera);
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

## ✅ Что реализовано

| Раздел | Детали |
|---|---|
| **Рыбки** | 15 шт., тело/глаза/зрачки/хвост/3 плавника, 8 цветовых схем, масштаб 0.6–1.2, индивидуальная скорость и фаза анимации |
| **ИИ** | Отталкивание между рыбками, плавное отражение от стен, блуждание, преследование корма (радиус 15), рост +5% после еды |
| **Аквариум** | Стекло с `transmission: 0.95` + wireframe-рамка, песчаное дно с процедурными неровностями и тенями, 8 деформированных камней, 12 покачивающихся водорослей (TubeGeometry + CatmullRom) |
| **Пузыри** | 30 шт., стеклянные, подъём с синусоидальным покачиванием, сброс на дно |
| **Кормление** | Клик (с фильтром «клик vs drag»), гравитация, съедание, удаление у дна |
| **Свет** | Ambient + Directional (тени 2048², PCFSoft) + 2 мерцающих PointLight, кнопка вкл/выкл |
| **UI** | Glass-панели с blur, градиентный заголовок, счётчики, FPS, 3 кнопки с hover-эффектами |
| **Производительность** | Дельта-время, raycaster, низкополигональные геометрии, общий `pixelRatio ≤ 2` |

Хотите, чтобы я добавил что-то ещё — например, ночной режим, звук, или сохранение размера рыбок в `localStorage`?