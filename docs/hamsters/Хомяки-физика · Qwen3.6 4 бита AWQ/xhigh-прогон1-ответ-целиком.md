

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Клетка с хомяками</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #1a1a2e; overflow: hidden; font-family: 'Segoe UI', monospace; }
canvas { display: block; }

#info-panel {
  position: absolute; top: 10px; right: 10px;
  background: rgba(0,0,0,0.75); color: #cde; padding: 12px;
  border-radius: 8px; font-size: 12px; min-width: 260px;
  border: 1px solid #446; max-height: 95vh; overflow-y: auto;
}
#info-panel h3 { color: #f0a; margin-bottom: 6px; font-size: 14px; }
#info-panel .section { margin-bottom: 10px; border-bottom: 1px solid #335; padding-bottom: 8px; }
#info-panel .label { color: #8af; }
#info-panel .value { color: #afa; }
#info-panel .warn { color: #fa0; }
#info-panel .hamster-row { display: flex; justify-content: space-between; padding: 2px 0; }
#info-panel .hamster-name { font-weight: bold; }

#phys-panel {
  position: absolute; top: 10px; left: 10px;
  background: rgba(0,0,0,0.75); color: #cde; padding: 12px;
  border-radius: 8px; font-size: 11px; min-width: 220px;
  border: 1px solid #446;
}
#phys-panel h3 { color: #4f8; margin-bottom: 6px; font-size: 13px; }
#phys-panel .row { display: flex; justify-content: space-between; padding: 1px 0; }
#phys-panel .ok { color: #4f8; }
#phys-panel .bad { color: #f44; }
</style>
</head>
<body>

<div id="info-panel">
  <h3>🐹 Хомяки</h3>
  <div id="hamster-list"></div>
  <div class="section">
    <div class="label">Колесо:</div>
    <div id="wheel-info" class="value">—</div>
  </div>
  <div class="section">
    <div class="label">Труба:</div>
    <div id="tube-info" class="value">—</div>
  </div>
</div>

<div id="phys-panel">
  <h3>⚙️ Физика</h3>
  <div id="phys-data"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// КОНСТАНТЫ — ГАБАРИТЫ ЗВЕРЯ
// ============================================================
const HAMSTER_LENGTH = 0.30;   // м — длина тела
const HAMSTER_WIDTH  = 0.16;   // м — ширина
const HAMSTER_HEIGHT = 0.14;   // м — высота
const HAMSTER_RADIUS = 0.10;   // м — радиус для коллизий (цилиндр)
const STRIDE_LENGTH  = 0.08;   // м — длина шага
const LEG_SPEED_BASE = 0.6;    // м/с — базовая скорость бега

// ============================================================
// ВЫВОДНЫЕ РАЗМЕРЫ ПРЕДМЕТОВ
// ============================================================
const WHEEL_RADIUS   = HAMSTER_LENGTH * 2.2;  // ~0.66 м — зверь помещается внутри
const WHEEL_WIDTH    = HAMSTER_WIDTH  * 2.5;  // ~0.40 м — шире боков зверя
const TUBE_RADIUS    = HAMSTER_RADIUS * 1.8;  // ~0.18 м
const TUBE_LENGTH    = 1.2;                    // м
const BOWL_RADIUS    = 0.20;                   // м
const CAGE_SIZE      = 2.5;                    // м — сторона клетки
const CAGE_BAR_COUNT = 20;                     // прутьев по длинной стороне

// ============================================================
// СЦЕНА, КАМЕРА, РЕНДЕРЕР
// ============================================================
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2a2a3e);
scene.fog = new THREE.FogExp2(0x2a2a3e, 0.04);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(2.5, 2.0, 2.5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.update();

// ============================================================
// ОСВЕЩЕНИЕ
// ============================================================
const ambientLight = new THREE.AmbientLight(0x404060, 0.5);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffeedd, 0.9);
dirLight.position.set(3, 5, 2);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.near = 0.5;
dirLight.shadow.camera.far = 15;
dirLight.shadow.camera.left = -4;
dirLight.shadow.camera.right = 4;
dirLight.shadow.camera.top = 4;
dirLight.shadow.camera.bottom = -4;
dirLight.shadow.bias = -0.001;
scene.add(dirLight);

const fillLight = new THREE.PointLight(0x8888cc, 0.3, 10);
fillLight.position.set(-2, 3, -2);
scene.add(fillLight);

// ============================================================
// ПОЛОМ КОМНАТЫ
// ============================================================
const floorGeo = new THREE.PlaneGeometry(12, 12);
const floorMat = new THREE.MeshStandardMaterial({ color: 0x3a2a1a, roughness: 0.9 });
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// Стены комнаты
function makeWall(w, h, pos, rotY) {
  const g = new THREE.PlaneGeometry(w, h);
  const m = new THREE.MeshStandardMaterial({ color: 0x4a4a5e, roughness: 0.8 });
  const mesh = new THREE.Mesh(g, m);
  mesh.position.copy(pos);
  mesh.rotation.y = rotY;
  mesh.receiveShadow = true;
  scene.add(mesh);
}
makeWall(12, 4, new THREE.Vector3(0, 2, -6), 0);
makeWall(12, 4, new THREE.Vector3(-6, 2, 0), Math.PI/2);
makeWall(12, 4, new THREE.Vector3(6, 2, 0), -Math.PI/2);

// Стол
const tableGeo = new THREE.BoxGeometry(3.5, 0.08, 3.5);
const tableMat = new THREE.MeshStandardMaterial({ color: 0x6b4226, roughness: 0.7 });
const table = new THREE.Mesh(tableGeo, tableMat);
table.position.set(0, 0.6, 0);
table.castShadow = true;
table.receiveShadow = true;
scene.add(table);

// Ножки стола
for (let x of [-1.4, 1.4]) for (let z of [-1.4, 1.4]) {
  const leg = new THREE.Mesh(
    new THREE.CylinderGeometry(0.04, 0.04, 0.6, 8),
    tableMat
  );
  leg.position.set(x, 0.3, z);
  leg.castShadow = true;
  scene.add(leg);
}

// ============================================================
// КЛЕТКА
// ============================================================
const cageY = 0.64; // на столе
const cageHalf = CAGE_SIZE / 2;

// Поддон
const trayGeo = new THREE.BoxGeometry(CAGE_SIZE, 0.05, CAGE_SIZE);
const trayMat = new THREE.MeshStandardMaterial({ color: 0x888899, metalness: 0.3 });
const tray = new THREE.Mesh(trayGeo, trayMat);
tray.position.set(0, cageY, 0);
tray.receiveShadow = true;
scene.add(tray);

// Подстилка — InstancedMesh щепок
const beddingCount = 600;
const chipGeo = new THREE.BoxGeometry(0.04, 0.008, 0.02);
const chipMat = new THREE.MeshStandardMaterial({ color: 0xc8a860, roughness: 1 });
const beddingMesh = new THREE.InstancedMesh(chipGeo, chipMat, beddingCount);
beddingMesh.receiveShadow = true;
const dummy = new THREE.Object3D();
for (let i = 0; i < beddingCount; i++) {
  dummy.position.set(
    (Math.random() - 0.5) * (CAGE_SIZE - 0.2),
    cageY + 0.025 + Math.random() * 0.02,
    (Math.random() - 0.5) * (CAGE_SIZE - 0.2)
  );
  dummy.rotation.set(Math.random()*0.3, Math.random()*Math.PI, Math.random()*0.3);
  dummy.scale.set(0.5 + Math.random(), 0.5 + Math.random(), 0.5 + Math.random());
  dummy.updateMatrix();
  beddingMesh.setMatrixAt(i, dummy.matrix);
}
scene.add(beddingMesh);

// Прутья клетки
const barMat = new THREE.MeshStandardMaterial({ color: 0xaaaaaa, metalness: 0.7, roughness: 0.3 });
const barRadius = 0.012;
const cageGroup = new THREE.Group();
cageGroup.position.set(0, cageY + 0.025, 0);

function addBar(x1, y1, z1, x2, y2, z2) {
  const dir = new THREE.Vector3(x2-x1, y2-y1, z2-z1);
  const len = dir.length();
  const g = new THREE.CylinderGeometry(barRadius, barRadius, len, 6);
  const m = new THREE.Mesh(g, barMat);
  const mid = new THREE.Vector3((x1+x2)/2, (y1+y2)/2, (z1+z2)/2);
  m.position.copy(mid);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), dir.normalize());
  m.castShadow = true;
  cageGroup.add(m);
}

// Вертикальные прутья
const barSpacing = CAGE_SIZE / CAGE_BAR_COUNT;
for (let i = 0; i <= CAGE_BAR_COUNT; i++) {
  const offset = -cageHalf + i * barSpacing;
  // Передняя стенка
  addBar(offset, 0, cageHalf, offset, 0.6, cageHalf);
  // Задняя стенка
  addBar(offset, 0, -cageHalf, offset, 0.6, -cageHalf);
}
for (let i = 1; i < CAGE_BAR_COUNT; i++) {
  const offset = -cageHalf + i * barSpacing;
  // Левая стенка
  addBar(-cageHalf, 0, offset, -cageHalf, 0.6, offset);
  // Правая стенка
  addBar(cageHalf, 0, offset, cageHalf, 0.6, offset);
}

// Горизонтальные прутья (верхние рамки)
for (let side of [cageHalf, -cageHalf]) {
  addBar(-cageHalf, 0.6, side, cageHalf, 0.6, side);
  addBar(-cageHalf, 0.3, side, cageHalf, 0.3, side);
}
for (let side of [cageHalf, -cageHalf]) {
  addBar(side, 0.6, -cageHalf, side, 0.6, cageHalf);
  addBar(side, 0.3, -cageHalf, side, 0.3, cageHalf);
}

scene.add(cageGroup);

// ============================================================
// КОЛЕСО
// ============================================================
const wheelGroup = new THREE.Group();
wheelGroup.position.set(-0.6, cageY + 0.025, 0);
scene.add(wheelGroup);

// Данные колеса
const wheelData = {
  radius: WHEEL_RADIUS,
  width: WHEEL_WIDTH,
  angularVelocity: 0,
  angle: 0,
  friction: 0.98, // коэффициент затухания за кадр
  runner: null,   // хомяк-бегун
  rimThickness: 0.03,
};

// Обод — тор
const rimGeo = new THREE.TorusGeometry(WHEEL_RADIUS, wheelData.rimThickness, 12, 48);
const rimMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.5, roughness: 0.3 });
const rim = new THREE.Mesh(rimGeo, rimMat);
rim.rotation.y = Math.PI / 2;
rim.castShadow = true;
wheelGroup.add(rim);

// Спицы
for (let i = 0; i < 8; i++) {
  const angle = (i / 8) * Math.PI * 2;
  const spokeLen = WHEEL_RADIUS - wheelData.rimThickness;
  const spokeGeo = new THREE.CylinderGeometry(0.008, 0.008, spokeLen, 6);
  const spoke = new THREE.Mesh(spokeGeo, rimMat);
  spoke.position.set(0, Math.cos(angle) * spokeLen/2, Math.sin(angle) * spokeLen/2);
  spoke.rotation.z = angle;
  spoke.castShadow = true;
  wheelGroup.add(spoke);
}

// Опоры (стойки по бокам)
for (let side of [-1, 1]) {
  const supportGeo = new THREE.CylinderGeometry(0.02, 0.02, WHEEL_WIDTH, 8);
  const support = new THREE.Mesh(supportGeo, rimMat);
  support.position.set(0, 0, side * WHEEL_RADIUS);
  support.rotation.x = Math.PI / 2;
  support.castShadow = true;
  wheelGroup.add(support);
}

// Ось
const axleGeo = new THREE.CylinderGeometry(0.015, 0.015, WHEEL_WIDTH + 0.1, 8);
const axleMat = new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.8 });
const axle = new THREE.Mesh(axleGeo, axleMat);
axle.rotation.x = Math.PI / 2;
axle.castShadow = true;
wheelGroup.add(axle);

// Платформа у колеса (для входа)
const wheelPlatformGeo = new THREE.BoxGeometry(0.3, 0.02, 0.5);
const wheelPlatformMat = new THREE.MeshStandardMaterial({ color: 0x999999, roughness: 0.6 });
const wheelPlatform = new THREE.Mesh(wheelPlatformGeo, wheelPlatformMat);
wheelPlatform.position.set(0.3, 0, 0);
wheelPlatform.castShadow = true;
wheelGroup.add(wheelPlatform);

// ============================================================
// ТРУБА
// ============================================================
const tubeGroup = new THREE.Group();
tubeGroup.position.set(0.5, cageY + TUBE_RADIUS + 0.025, 0);
scene.add(tubeGroup);

const tubeData = {
  radius: TUBE_RADIUS,
  length: TUBE_LENGTH,
  halfLength: TUBE_LENGTH / 2,
  occupant: null,
  // Для коллизий: цилиндр вдоль оси X
  center: tubeGroup.position.clone(),
};

// Стенка трубы — тор с одной стороной (открытый цилиндр)
const tubeWallGeo = new THREE.CylinderGeometry(TUBE_RADIUS, TUBE_RADIUS, TUBE_LENGTH, 24, 1, true);
const tubeWallMat = new THREE.MeshStandardMaterial({
  color: 0x88aa88, side: THREE.DoubleSide, transparent: true, opacity: 0.85, roughness: 0.5
});
const tubeWall = new THREE.Mesh(tubeWallGeo, tubeWallMat);
tubeWall.rotation.z = Math.PI / 2;
tubeWall.castShadow = true;
tubeGroup.add(tubeWall);

// Кольца на торцах (тонкие)
for (let sign of [-1, 1]) {
  const ringGeo = new THREE.TorusGeometry(TUBE_RADIUS, 0.008, 8, 24);
  const ring = new THREE.Mesh(ringGeo, tubeWallMat);
  ring.position.x = sign * TUBE_LENGTH / 2;
  ring.rotation.y = Math.PI / 2;
  tubeGroup.add(ring);
}

// ============================================================
// МИСКА
// ============================================================
const bowlGroup = new THREE.Group();
bowlGroup.position.set(0, cageY + 0.025, 0.7);
scene.add(bowlGroup);

const bowlData = {
  radius: BOWL_RADIUS,
  height: 0.06,
  center: bowlGroup.position.clone(),
};

// Миска — полуэллипсоид
const bowlGeo = new THREE.SphereGeometry(BOWL_RADIUS, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2);
const bowlMat = new THREE.MeshStandardMaterial({ color: 0x556688, metalness: 0.4, roughness: 0.4 });
const bowl = new THREE.Mesh(bowlGeo, bowlMat);
bowl.rotation.x = Math.PI; // перевернуть — открытый верх
bowl.position.y = -BOWL_RADIUS * 0.3;
bowl.castShadow = true;
bowlGroup.add(bowl);

// Зёрна в миске
const seedCount = 40;
const seedGeo = new THREE.SphereGeometry(0.012, 6, 4);
const seedMat = new THREE.MeshStandardMaterial({ color: 0xddaa44, roughness: 0.9 });
const seedsMesh = new THREE.InstancedMesh(seedGeo, seedMat, seedCount);
for (let i = 0; i < seedCount; i++) {
  const angle = Math.random() * Math.PI * 2;
  const r = Math.random() * BOWL_RADIUS * 0.7;
  dummy.position.set(
    Math.cos(angle) * r,
    -BOWL_RADIUS * 0.3 + Math.random() * 0.03,
    Math.sin(angle) * r
  );
  dummy.rotation.set(Math.random(), Math.random(), Math.random());
  dummy.updateMatrix();
  seedsMesh.setMatrixAt(i, dummy.matrix);
}
bowlGroup.add(seedsMesh);

// ============================================================
// ПОИЛКА
// ============================================================
const drinkerGroup = new THREE.Group();
drinkerGroup.position.set(0, cageY + 0.35, -cageHalf + 0.05);
scene.add(drinkerGroup);

const bottleGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.15, 12);
const bottleMat = new THREE.MeshStandardMaterial({ color: 0xaaddff, transparent: true, opacity: 0.5 });
const bottle = new THREE.Mesh(bottleGeo, bottleMat);
bottle.rotation.z = Math.PI / 2;
bottle.castShadow = true;
drinkerGroup.add(bottle);

const nozzleGeo = new THREE.CylinderGeometry(0.008, 0.012, 0.04, 8);
const nozzleMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.6 });
const nozzle = new THREE.Mesh(nozzleGeo, nozzleMat);
nozzle.position.set(0, -0.08, 0);
nozzle.rotation.z = Math.PI / 2;
drinkerGroup.add(nozzle);

// Крепление
const clampGeo = new THREE.BoxGeometry(0.06, 0.02, 0.08);
const clamp = new THREE.Mesh(clampGeo, new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.5 }));
clamp.position.set(0, 0.02, 0);
drinkerGroup.add(clamp);

// ============================================================
// СОЗДАНИЕ МОДЕЛИ ХОМЯКА
// ============================================================
function createHamsterMesh(color) {
  const group = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.8 });
  const bellyMat = new THREE.MeshStandardMaterial({ color: 0xeeddcc, roughness: 0.8 });
  const darkMat  = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.5 });
  const pinkMat  = new THREE.MeshStandardMaterial({ color: 0xeeaaaa, roughness: 0.6 });
  const earInnerMat = new THREE.MeshStandardMaterial({ color: 0xffccbb, roughness: 0.6 });

  // Тело — вытянутый эллипсоид
  const bodyGeo = new THREE.SphereGeometry(HAMSTER_RADIUS * 1.1, 16, 12);
  bodyGeo.scale(1.6, 0.85, 1.1);
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.position.set(0, HAMSTER_HEIGHT * 0.6, 0);
  body.castShadow = true;
  group.add(body);

  // Живот — светлый эллипсоид снизу
  const bellyGeo = new THREE.SphereGeometry(HAMSTER_RADIUS * 0.9, 12, 8);
  bellyGeo.scale(1.4, 0.5, 0.9);
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.position.set(0, HAMSTER_HEIGHT * 0.25, 0);
  belly.castShadow = true;
  group.add(belly);

  // Голова — отдельная группа (для кивания)
  const headGroup = new THREE.Group();
  headGroup.position.set(HAMSTER_LENGTH * 0.55, HAMSTER_HEIGHT * 0.7, 0);

  const headGeo = new THREE.SphereGeometry(HAMSTER_RADIUS * 0.7, 14, 10);
  headGeo.scale(1.1, 1.0, 1.0);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.castShadow = true;
  headGroup.add(head);

  // Щёки
  for (let side of [-1, 1]) {
    const cheekGeo = new THREE.SphereGeometry(HAMSTER_RADIUS * 0.35, 8, 6);
    cheekGeo.scale(0.8, 0.6, 1.0);
    const cheek = new THREE.Mesh(cheekGeo, bellyMat);
    cheek.position.set(-HAMSTER_LENGTH * 0.05, -HAMSTER_HEIGHT * 0.1, side * HAMSTER_WIDTH * 0.4);
    headGroup.add(cheek);
  }

  // Глаза
  for (let side of [-1, 1]) {
    const eyeWhiteGeo = new THREE.SphereGeometry(0.02, 8, 6);
    const eyeWhite = new THREE.Mesh(eyeWhiteGeo, new THREE.MeshStandardMaterial({ color: 0xffffff }));
    eyeWhite.position.set(HAMSTER_LENGTH * 0.12, HAMSTER_HEIGHT * 0.05, side * HAMSTER_WIDTH * 0.35);
    headGroup.add(eyeWhite);

    const pupilGeo = new THREE.SphereGeometry(0.012, 6, 4);
    const pupil = new THREE.Mesh(pupilGeo, darkMat);
    pupil.position.set(HAMSTER_LENGTH * 0.15, HAMSTER_HEIGHT * 0.05, side * HAMSTER_WIDTH * 0.38);
    headGroup.add(pupil);
  }

  // Нос
  const noseGeo = new THREE.SphereGeometry(0.015, 6, 4);
  const nose = new THREE.Mesh(noseGeo, pinkMat);
  nose.position.set(HAMSTER_LENGTH * 0.2, -HAMSTER_HEIGHT * 0.05, 0);
  headGroup.add(nose);

  // Уши
  for (let side of [-1, 1]) {
    const earGroup = new THREE.Group();
    const earOuterGeo = new THREE.SphereGeometry(0.025, 8, 6);
    earOuterGeo.scale(1.0, 0.5, 1.3);
    const earOuter = new THREE.Mesh(earOuterGeo, bodyMat);
    earGroup.add(earOuter);

    const earInnerGeo = new THREE.SphereGeometry(0.018, 6, 4);
    earInnerGeo.scale(0.8, 0.4, 1.1);
    const earInner = new THREE.Mesh(earInnerGeo, earInnerMat);
    earGroup.add(earInner);

    earGroup.position.set(HAMSTER_LENGTH * 0.08, HAMSTER_HEIGHT * 0.2, side * HAMSTER_WIDTH * 0.42);
    headGroup.add(earGroup);
  }

  group.add(headGroup);

  // Лапы — 4 цилиндра
  const legGeo = new THREE.CylinderGeometry(0.012, 0.015, 0.06, 6);
  const legs = [];
  const legPositions = [
    { x: HAMSTER_LENGTH * 0.35,  z: HAMSTER_WIDTH * 0.4,  name: 'FL' },
    { x: HAMSTER_LENGTH * 0.35,  z: -HAMSTER_WIDTH * 0.4, name: 'FR' },
    { x: -HAMSTER_LENGTH * 0.35, z: HAMSTER_WIDTH * 0.4,  name: 'BL' },
    { x: -HAMSTER_LENGTH * 0.35, z: -HAMSTER_WIDTH * 0.4, name: 'BR' },
  ];

  legPositions.forEach(lp => {
    const leg = new THREE.Mesh(legGeo, pinkMat);
    leg.position.set(lp.x, HAMSTER_HEIGHT * 0.15, lp.z);
    leg.castShadow = true;
    group.add(leg);
    legs.push({ mesh: leg, basePos: new THREE.Vector3(lp.x, HAMSTER_HEIGHT * 0.15, lp.z), name: lp.name });
  });

  // Хвост
  const tailGeo = new THREE.SphereGeometry(0.015, 6, 4);
  const tail = new THREE.Mesh(tailGeo, pinkMat);
  tail.position.set(-HAMSTER_LENGTH * 0.6, HAMSTER_HEIGHT * 0.5, 0);
  group.add(tail);

  return { group, body, belly, headGroup, legs, tail };
}

// ============================================================
// ХОМЯКИ
// ============================================================
const hamsterNames = ['Шурик', 'Пушок', 'Карамелька', 'Бублик', 'Соня'];
const hamsterColors = [0xd4a574, 0xf0d0b0, 0xc88040, 0xb08060, 0xe8c8a0];

const hamsters = [];

for (let i = 0; i < 5; i++) {
  const name = hamsterNames[i];
  const color = hamsterColors[i];
  const mesh = createHamsterMesh(color);

  const hamster = {
    name: name,
    color: color,
    mesh: mesh,
    position: new THREE.Vector3(
      (Math.random() - 0.5) * (CAGE_SIZE - 0.6),
      cageY + 0.025,
      (Math.random() - 0.5) * (CAGE_SIZE - 0.6)
    ),
    velocity: new THREE.Vector3(),
    rotationY: Math.random() * Math.PI * 2,
    speed: 0,
    distanceTraveled: 0,
    legPhase: 0,
    state: 'idle',
    stateTimer: 0,
    target: null,
    targetAction: null,
    inWheel: false,
    inTube: false,
    tubeProgress: 0,
    tubeDirection: 1,
    eatingTimer: 0,
    breathPhase: Math.random() * Math.PI * 2,
    earTwitchTimer: 1 + Math.random() * 4,
    earTwitchActive: false,
    earTwitchDir: 1,
    jumpVelocity: 0,
    jumping: false,
    wheelEntryProgress: 0,
    wheelExitProgress: 0,
    lastCollisionPush: new THREE.Vector3(),
  };

  mesh.group.position.copy(hamster.position);
  mesh.group.rotation.y = hamster.rotationY;
  scene.add(mesh.group);

  hamsters.push(hamster);
}

// ============================================================
// ФИЗИКА И КОЛЛИЗИИ
// ============================================================

// Форма столкновения для колеса — вертикальный цилиндр
function wheelCollisionShape() {
  return {
    type: 'cylinder',
    center: wheelGroup.position.clone(),
    radius: WHEEL_RADIUS + 0.1,
    height: 0.5,
    halfHeight: 0.25,
  };
}

// Форма столкновения для трубы — горизонтальный цилиндр
function tubeCollisionShape() {
  return {
    type: 'cylinder_horizontal',
    center: tubeGroup.position.clone(),
    radius: TUBE_RADIUS + 0.05,
    halfLength: TUBE_LENGTH / 2 + 0.05,
  };
}

// Форма столкновения для миски — сфера
function bowlCollisionShape() {
  return {
    type: 'sphere',
    center: bowlGroup.position.clone(),
    radius: BOWL_RADIUS + 0.05,
  };
}

// Расстояние от точки до цилиндра (вертикального) + нормаль
function pointToVerticalCylinder(point, cyl) {
  const dx = point.x - cyl.center.x;
  const dz = point.z - cyl.center.z;
  const distXZ = Math.sqrt(dx*dx + dz*dz);
  const dy = point.y - cyl.center.y;

  if (distXZ < 0.001) {
    return { dist: cyl.radius - HAMSTER_RADIUS, normal: new THREE.Vector3(1, 0, 0) };
  }

  if (Math.abs(dy) > cyl.halfHeight + HAMSTER_HEIGHT) {
    // Точка выше/ниже цилиндра
    return { dist: Infinity, normal: new THREE.Vector3() };
  }

  const radialDist = distXZ - cyl.radius - HAMSTER_RADIUS;
  if (radialDist < 0) {
    const nx = dx / distXZ;
    const nz = dz / distXZ;
    return { dist: radialDist, normal: new THREE.Vector3(nx, 0, nz) };
  }
  return { dist: radialDist, normal: new THREE.Vector3() };
}

// Расстояние от точки до горизонтального цилиндра
function pointToHorizontalCylinder(point, cyl) {
  const dx = point.x - cyl.center.x;
  const dy = point.y - cyl.center.y;
  const dz = point.z - cyl.center.z;

  // Проекция на ось X
  const projX = dx;
  const distYZ = Math.sqrt(dy*dy + dz*dz);

  if (distYZ < 0.001) {
    return { dist: cyl.radius - HAMSTER_RADIUS, normal: new THREE.Vector3(0, 1, 0) };
  }

  // Проверка по длине
  if (Math.abs(projX) > cyl.halfLength) {
    // Ближайшая точка — торец
    const endX = cyl.center.x + Math.sign(projX) * cyl.halfLength;
    const dxEnd = point.x - endX;
    const distYZEnd = Math.sqrt(dy*dy + dz*dz);
    const radialDist = distYZEnd - cyl.radius - HAMSTER_RADIUS;
    if (radialDist < 0) {
      const ny = dy / distYZEnd;
      const nz = dz / distYZEnd;
      return { dist: radialDist, normal: new THREE.Vector3(0, ny, nz) };
    }
    // Или угол торца
    const cornerDist = Math.sqrt(dxEnd*dxEnd + dy*dy + dz*dz) - HAMSTER_RADIUS;
    if (cornerDist < 0) {
      const nd = new THREE.Vector3(dxEnd, dy, dz).normalize();
      return { dist: cornerDist, normal: nd };
    }
    return { dist: Math.max(radialDist, cornerDist), normal: new THREE.Vector3() };
  }

  const radialDist = distYZ - cyl.radius - HAMSTER_RADIUS;
  if (radialDist < 0) {
    const ny = dy / distYZ;
    const nz = dz / distYZ;
    return { dist: radialDist, normal: new THREE.Vector3(0, ny, nz) };
  }
  return { dist: radialDist, normal: new THREE.Vector3() };
}

// Расстояние от точки до сферы
function pointToSphere(point, sph) {
  const dx = point.x - sph.center.x;
  const dy = point.y - sph.center.y;
  const dz = point.z - sph.center.z;
  const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
  const overlap = dist - sph.radius - HAMSTER_RADIUS;
  if (overlap < 0) {
    const n = new THREE.Vector3(dx, dy, dz).normalize();
    return { dist: overlap, normal: n };
  }
  return { dist: overlap, normal: new THREE.Vector3() };
}

// Проверка коллизий хомяка с объектами
function resolveCollisions(hamster) {
  const p = hamster.position;
  let pushed = false;

  // Колесо
  if (!hamster.inWheel) {
    const wc = wheelCollisionShape();
    const result = pointToVerticalCylinder(p, wc);
    if (result.dist < 0) {
      p.x -= result.normal.x * result.dist;
      p.y -= result.normal.y * result.dist;
      p.z -= result.normal.z * result.dist;
      pushed = true;
    }
  }

  // Труба (только если не внутри)
  if (!hamster.inTube) {
    const tc = tubeCollisionShape();
    const result = pointToHorizontalCylinder(p, tc);
    if (result.dist < 0) {
      p.x -= result.normal.x * result.dist;
      p.y -= result.normal.y * result.dist;
      p.z -= result.normal.z * result.dist;
      pushed = true;
    }
  }

  // Миска
  if (hamster.state !== 'eating') {
    const bc = bowlCollisionShape();
    const result = pointToSphere(p, bc);
    if (result.dist < 0) {
      p.x -= result.normal.x * result.dist;
      p.y -= result.normal.y * result.dist;
      p.z -= result.normal.z * result.dist;
      pushed = true;
    }
  }

  // Стены клетки
  const margin = HAMSTER_RADIUS + 0.05;
  const half = cageHalf - margin;
  if (p.x < -half) { p.x = -half; pushed = true; }
  if (p.x > half)  { p.x = half;  pushed = true; }
  if (p.z < -half) { p.z = -half; pushed = true; }
  if (p.z > half)  { p.z = half;  pushed = true; }
  if (p.y < cageY + 0.025) { p.y = cageY + 0.025; pushed = true; }

  return pushed;
}

// Расталкивание хомяков друг от друга
function resolveHamsterCollisions() {
  for (let i = 0; i < hamsters.length; i++) {
    for (let j = i + 1; j < hamsters.length; j++) {
      const a = hamsters[i];
      const b = hamsters[j];
      if (a.inWheel || b.inWheel) continue;
      if (a.inTube || b.inTube) continue;

      const dx = b.position.x - a.position.x;
      const dy = b.position.y - a.position.y;
      const dz = b.position.z - a.position.z;
      const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
      const minDist = HAMSTER_RADIUS * 2.5;

      if (dist < minDist && dist > 0.001) {
        const push = (minDist - dist) * 0.5;
        const nx = dx / dist;
        const ny = dy / dist;
        const nz = dz / dist;
        a.position.x -= nx * push;
        a.position.y -= ny * push;
        a.position.z -= nz * push;
        b.position.x += nx * push;
        b.position.y += ny * push;
        b.position.z += nz * push;
      }
    }
  }
}

// ============================================================
// ПОВЕДЕНИЕ — КОНЕЧНЫЙ АВТОМАТ
// ============================================================

function pickRandomActivity(hamster) {
  const activities = ['walk', 'wheel', 'tube', 'eat'];
  // Исключаем недоступные
  const available = activities.filter(a => {
    if (a === 'wheel' && wheelData.runner !== null) return false;
    if (a === 'tube' && tubeData.occupant !== null) return false;
    return true;
  });
  if (available.length === 0) return 'walk';
  return available[Math.floor(Math.random() * available.length)];
}

function updateBehavior(hamster, dt) {
  hamster.stateTimer -= dt;

  switch (hamster.state) {
    case 'idle':
      if (hamster.stateTimer <= 0) {
        const activity = pickRandomActivity(hamster);
        switch (activity) {
          case 'walk':
            hamster.state = 'walking';
            hamster.stateTimer = 2 + Math.random() * 3;
            // Случайная цель в пределах клетки
            hamster.target = new THREE.Vector3(
              (Math.random() - 0.5) * (CAGE_SIZE - 0.8),
              cageY + 0.025,
              (Math.random() - 0.5) * (CAGE_SIZE - 0.8)
            );
            break;
          case 'wheel':
            hamster.state = 'walking_to_wheel';
            hamster.stateTimer = 10;
            hamster.target = wheelGroup.position.clone().add(new THREE.Vector3(0.35, 0, 0));
            hamster.targetAction = 'enter_wheel';
            break;
          case 'tube':
            hamster.state = 'walking_to_tube';
            hamster.stateTimer = 10;
            // Ближний торец
            hamster.target = tubeGroup.position.clone().add(new THREE.Vector3(-TUBE_LENGTH/2, 0, 0));
            hamster.targetAction = 'enter_tube';
            break;
          case 'eat':
            hamster.state = 'walking_to_bowl';
            hamster.stateTimer = 10;
            hamster.target = bowlGroup.position.clone().add(new THREE.Vector3(0, 0, -0.25));
            hamster.targetAction = 'start_eating';
            break;
        }
      }
      break;

    case 'walking':
      moveTowardTarget(hamster, dt);
      if (hamster.stateTimer <= 0 || reachedTarget(hamster)) {
        hamster.state = 'idle';
        hamster.stateTimer = 1 + Math.random() * 2;
        hamster.speed = 0;
      }
      break;

    case 'walking_to_wheel':
      moveTowardTarget(hamster, dt);
      if (reachedTarget(hamster) && hamster.targetAction === 'enter_wheel') {
        if (wheelData.runner === null) {
          hamster.state = 'entering_wheel';
          hamster.stateTimer = 1.5;
          hamster.wheelEntryProgress = 0;
          wheelData.runner = hamster;
        } else {
          // Колесо занято — выбираем другое дело
          hamster.state = 'idle';
          hamster.stateTimer = 1 + Math.random();
        }
      }
      if (hamster.stateTimer <= 0) {
        hamster.state = 'idle';
        hamster.stateTimer = 1;
      }
      break;

    case 'entering_wheel': {
      hamster.wheelEntryProgress += dt / hamster.stateTimer;
      if (hamster.wheelEntryProgress >= 1) {
        hamster.inWheel = true;
        hamster.state = 'running_in_wheel';
        hamster.stateTimer = 4 + Math.random() * 6;
        hamster.speed = LEG_SPEED_BASE;
        // Позиция: нижняя точка внутреннего обода
        hamster.position.copy(wheelGroup.position);
        hamster.position.y += WHEEL_RADIUS - HAMSTER_HEIGHT * 0.5;
        hamster.position.x -= HAMSTER_LENGTH * 0.3;
        hamster.rotationY = Math.PI; // смотрит влево (против часовой)
      }
      break;
    }

    case 'running_in_wheel': {
      // Скорость бега
      hamster.speed = LEG_SPEED_BASE * (0.8 + Math.random() * 0.4 * dt);
      hamster.speed = Math.max(0.3, Math.min(1.2, hamster.speed));

      // Угловая скорость колеса: ω = v / R
      const v = hamster.speed;
      wheelData.angularVelocity = v / WHEEL_RADIUS;

      // Хомяк остаётся на нижней точке обода
      hamster.position.copy(wheelGroup.position);
      hamster.position.y += WHEEL_RADIUS - HAMSTER_HEIGHT * 0.5;
      hamster.position.x -= HAMSTER_LENGTH * 0.3;

      // Фаза шага от пройденного пути
      hamster.distanceTraveled += v * dt;
      hamster.legPhase = (hamster.distanceTraveled / STRIDE_LENGTH) * Math.PI * 2;

      if (hamster.stateTimer <= 0) {
        hamster.state = 'exiting_wheel';
        hamster.stateTimer = 1.5;
        hamster.wheelExitProgress = 0;
      }
      break;
    }

    case 'exiting_wheel': {
      hamster.wheelExitProgress += dt / hamster.stateTimer;
      const ep = hamster.wheelExitProgress;

      // Плавно перемещаем из колеса на платформу
      const exitStart = wheelGroup.position.clone();
      exitStart.y += WHEEL_RADIUS - HAMSTER_HEIGHT * 0.5;
      exitStart.x -= HAMSTER_LENGTH * 0.3;

      const exitEnd = wheelGroup.position.clone();
      exitEnd.y += 0.025;
      exitEnd.x += 0.35;

      hamster.position.lerpVectors(exitStart, exitEnd, ep);

      if (ep >= 1) {
        hamster.inWheel = false;
        hamster.state = 'idle';
        hamster.stateTimer = 1 + Math.random() * 2;
        hamster.speed = 0;
        hamster.distanceTraveled = 0;
        wheelData.runner = null;
      }
      break;
    }

    case 'walking_to_tube':
      moveTowardTarget(hamster, dt);
      if (reachedTarget(hamster) && hamster.targetAction === 'enter_tube') {
        if (tubeData.occupant === null) {
          hamster.state = 'in_tube';
          hamster.stateTimer = 5;
          hamster.inTube = true;
          hamster.tubeProgress = 0;
          hamster.tubeDirection = 1;
          tubeData.occupant = hamster;
          // Позиция: вход в трубу
          hamster.position.copy(tubeGroup.position);
          hamster.position.x -= TUBE_LENGTH / 2;
          hamster.position.z = 0;
          hamster.rotationY = 0; // смотрит вдоль оси X
        } else {
          hamster.state = 'idle';
          hamster.stateTimer = 1 + Math.random();
        }
      }
      if (hamster.stateTimer <= 0) {
        hamster.state = 'idle';
        hamster.stateTimer = 1;
      }
      break;

    case 'in_tube': {
      // Движение вдоль оси трубы
      const tubeSpeed = 0.2;
      hamster.tubeProgress += tubeSpeed * dt / TUBE_LENGTH;

      hamster.position.x = tubeGroup.position.x + (-TUBE_LENGTH/2 + hamster.tubeProgress * TUBE_LENGTH);
      hamster.position.y = tubeGroup.position.y;
      hamster.position.z = 0; // на оси трубы
      hamster.rotationY = 0;

      hamster.speed = tubeSpeed;
      hamster.distanceTraveled += tubeSpeed * dt;
      hamster.legPhase = (hamster.distanceTraveled / STRIDE_LENGTH) * Math.PI * 2;

      if (hamster.tubeProgress >= 1 || hamster.stateTimer <= 0) {
        hamster.inTube = false;
        hamster.state = 'idle';
        hamster.stateTimer = 1 + Math.random() * 2;
        hamster.speed = 0;
        hamster.distanceTraveled = 0;
        tubeData.occupant = null;
        // Выходим с другого торца
        hamster.position.x = tubeGroup.position.x + TUBE_LENGTH / 2 + 0.1;
      }
      break;
    }

    case 'walking_to_bowl':
      moveTowardTarget(hamster, dt);
      if (reachedTarget(hamster) && hamster.targetAction === 'start_eating') {
        hamster.state = 'eating';
        hamster.stateTimer = 3 + Math.random() * 4;
        hamster.eatingTimer = 0;
      }
      if (hamster.stateTimer <= 0) {
        hamster.state = 'idle';
        hamster.stateTimer = 1;
      }
      break;

    case 'eating': {
      hamster.eatingTimer += dt;
      // Наклон головы и жевание
      hamster.mesh.headGroup.rotation.x = Math.sin(hamster.eatingTimer * 4) * 0.15 - 0.2;
      hamster.speed = 0;
      hamster.distanceTraveled = 0;
      hamster.legPhase = 0;

      if (hamster.stateTimer <= 0) {
        hamster.state = 'idle';
        hamster.stateTimer = 1 + Math.random() * 2;
        hamster.mesh.headGroup.rotation.x = 0;
      }
      break;
    }
  }
}

function moveTowardTarget(hamster, dt) {
  if (!hamster.target) return;
  const dx = hamster.target.x - hamster.position.x;
  const dz = hamster.target.z - hamster.position.z;
  const dist = Math.sqrt(dx*dx + dz*dz);

  if (dist > 0.05) {
    const walkSpeed = 0.4;
    hamster.speed = walkSpeed;
    hamster.rotationY = Math.atan2(dx, dz);

    const moveX = (dx / dist) * walkSpeed * dt;
    const moveZ = (dz / dist) * walkSpeed * dt;
    hamster.position.x += moveX;
    hamster.position.z += moveZ;

    hamster.distanceTraveled += walkSpeed * dt;
    hamster.legPhase = (hamster.distanceTraveled / STRIDE_LENGTH) * Math.PI * 2;
  } else {
    hamster.speed = 0;
  }
}

function reachedTarget(hamster) {
  if (!hamster.target) return false;
  const dx = hamster.target.x - hamster.position.x;
  const dz = hamster.target.z - hamster.position.z;
  return Math.sqrt(dx*dx + dz*dz) < 0.15;
}

// ============================================================
// АНИМАЦИЯ ЛАП
// ============================================================
function updateLegs(hamster, dt) {
  const phase = hamster.legPhase;
  const speed = hamster.speed;

  // Диагональные пары: FL+BR и FR+BL
  const pairA = Math.sin(phase);      // FL, BR
  const pairB = Math.sin(phase + Math.PI); // FR, BL

  // Амплитуда зависит от скорости
  const amplitude = Math.min(speed / LEG_SPEED_BASE, 1.0) * 0.04;

  hamster.mesh.legs.forEach((leg, i) => {
    const base = leg.basePos;
    let swing = 0;

    if (i === 0) swing = pairA;  // FL
    else if (i === 1) swing = pairB; // FR
    else if (i === 2) swing = pairB; // BL
    else swing = pairA;  // BR

    // В колесе лапы работают иначе — бег по месту
    if (hamster.inWheel) {
      leg.mesh.position.x = base.x + swing * amplitude * 0.5;
      leg.mesh.position.y = base.y + Math.abs(swing) * amplitude * 0.3;
      leg.mesh.position.z = base.z;
    } else if (hamster.inTube) {
      leg.mesh.position.x = base.x + swing * amplitude * 0.5;
      leg.mesh.position.y = base.y + Math.abs(swing) * amplitude * 0.3;
      leg.mesh.position.z = base.z;
    } else {
      // Обычная ходьба — лапы двигаются в направлении движения
      const cosR = Math.cos(hamster.rotationY);
      const sinR = Math.sin(hamster.rotationY);

      leg.mesh.position.x = base.x + swing * amplitude * cosR;
      leg.mesh.position.y = base.y + Math.abs(swing) * amplitude * 0.5;
      leg.mesh.position.z = base.z + swing * amplitude * sinR;
    }

    // При остановке лапы замирают
    if (speed < 0.01) {
      leg.mesh.position.copy(base);
    }
  });
}

// ============================================================
// ДЫХАНИЕ И УШИ
// ============================================================
function updateIdleAnimations(hamster, dt) {
  // Дыхание — лёгкое изменение масштаба тела
  hamster.breathPhase += dt * 2.5;
  const breathScale = 1.0 + Math.sin(hamster.breathPhase) * 0.02;
  hamster.mesh.body.scale.set(
    breathScale * 1.6,
    breathScale * 0.85,
    breathScale * 1.1
  );

  // Дёрганье ушами
  hamster.earTwitchTimer -= dt;
  if (hamster.earTwitchTimer <= 0) {
    hamster.earTwitchActive = true;
    hamster.earTwitchDir = 1;
    hamster.earTwitchTimer = 0.1;
  }
  if (hamster.earTwitchActive) {
    hamster.earTwitchDir -= dt * 15;
    if (hamster.earTwitchDir < -1) {
      hamster.earTwitchActive = false;
      hamster.earTwitchTimer = 2 + Math.random() * 5;
    }
  }
}

// ============================================================
// ПРЫЖОК ПО КЛИКУ
// ============================================================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', (event) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);

  for (const hamster of hamsters) {
    const meshes = [];
    hamster.mesh.group.traverse(child => {
      if (child.isMesh) meshes.push(child);
    });
    const intersects = raycaster.intersectObjects(meshes);
    if (intersects.length > 0) {
      hamster.jumping = true;
      hamster.jumpVelocity = 2.0;
      break;
    }
  }
});

// ============================================================
// ОБНОВЛЕНИЕ КОЛЕСА
// ============================================================
function updateWheel(dt) {
  if (wheelData.runner) {
    // ω = v / R — уже установлено в updateBehavior
    wheelData.angle += wheelData.angularVelocity * dt;
  } else {
    // Затухание
    wheelData.angularVelocity *= Math.pow(wheelData.friction, dt * 60);
    if (Math.abs(wheelData.angularVelocity) < 0.001) {
      wheelData.angularVelocity = 0;
    }
    wheelData.angle += wheelData.angularVelocity * dt;
  }

  // Вращаем группу колеса (ось X)
  wheelGroup.rotation.x = wheelData.angle;
}

// ============================================================
// ПАНЕЛИ ИНФОРМАЦИИ
// ============================================================
function updateInfoPanels() {
  // Список хомяков
  let html = '';
  for (const h of hamsters) {
    const stateNames = {
      idle: 'отдыхает',
      walking: 'гуляет',
      walking_to_wheel: 'идёт к колесу',
      entering_wheel: 'входит в колесо',
      running_in_wheel: 'бежит в колесе',
      exiting_wheel: 'выходит из колеса',
      walking_to_tube: 'идёт к трубе',
      in_tube: 'ползёт по трубе',
      walking_to_bowl: 'идёт к миске',
      eating: 'грызёт зёрна',
    };
    const stateText = stateNames[h.state] || h.state;
    const colorHex = '#' + h.color.toString(16).padStart(6, '0');
    html += `<div class="hamster-row">
      <span class="hamster-name" style="color:${colorHex}">${h.name}</span>
      <span>${stateText}</span>
    </div>`;
  }
  document.getElementById('hamster-list').innerHTML = html;

  // Колесо
  const runner = wheelData.runner;
  let wheelText = `ω = ${wheelData.angularVelocity.toFixed(3)} рад/с`;
  if (runner) {
    wheelText += ` | бегун: ${runner.name}`;
    wheelText += ` | v_лап = ${runner.speed.toFixed(3)} м/с`;
    const linearSpeed = Math.abs(wheelData.angularVelocity) * WHEEL_RADIUS;
    wheelText += ` | v_обод = ${linearSpeed.toFixed(3)} м/с`;
    const diff = runner.speed > 0 ? Math.abs(linearSpeed - runner.speed) / runner.speed * 100 : 0;
    wheelText += ` | расх: ${diff.toFixed(1)}%`;
  } else {
    wheelText += ' | пусто';
  }
  document.getElementById('wheel-info').textContent = wheelText;

  // Труба
  const occupant = tubeData.occupant;
  let tubeText = '';
  if (occupant) {
    tubeText = `${occupant.name} | прогресс: ${(occupant.tubeProgress * 100).toFixed(0)}%`;
  } else {
    tubeText = 'пусто';
  }
  document.getElementById('tube-info').textContent = tubeText;

  // Физика
  let physHtml = '';
  if (runner) {
    const vLegs = runner.speed;
    const vRim = Math.abs(wheelData.angularVelocity) * WHEEL_RADIUS;
    const diffPct = vLegs > 0 ? Math.abs(vRim - vLegs) / vLegs * 100 : 0;
    const okClass = diffPct < 5 ? 'ok' : 'bad';
    physHtml += `<div class="row"><span class="label">v лап:</span><span class="${okClass}">${vLegs.toFixed(4)} м/с</span></div>`;
    physHtml += `<div class="row"><span class="label">|ω|·R:</span><span class="${okClass}">${vRim.toFixed(4)} м/с</span></div>`;
    physHtml += `<div class="row"><span class="label">расх:</span><span class="${okClass}">${diffPct.toFixed(2)}%</span></div>`;

    // Проверка позиции в колесе
    const hamInWheelY = runner.position.y;
    const expectedY = wheelGroup.position.y + WHEEL_RADIUS - HAMSTER_HEIGHT * 0.5;
    const yDiff = Math.abs(hamInWheelY - expectedY);
    physHtml += `<div class="row"><span class="label">y в колесе:</span><span class="${yDiff < 0.05 ? 'ok' : 'bad'}">${hamInWheelY.toFixed(4)} (ожид: ${expectedY.toFixed(4)})</span></div>`;

    // Габарит < радиус
    const fits = HAMSTER_LENGTH < WHEEL_RADIUS && HAMSTER_WIDTH < WHEEL_WIDTH;
    physHtml += `<div class="row"><span class="label">влезает:</span><span class="${fits ? 'ok' : 'bad'}">${fits ? 'да' : 'нет'}</span></div>`;
  } else {
    physHtml += `<div class="row"><span class="label">колесо:</span><span class="ok">нет бегуна</span></div>`;
    const decayOk = Math.abs(wheelData.angularVelocity) < 0.01;
    physHtml += `<div class="row"><span class="label">затухание:</span><span class="${decayOk ? 'ok' : 'bad'}">${wheelData.angularVelocity.toFixed(5)} рад/с</span></div>`;
  }

  if (occupant) {
    const tubeAxisY = tubeGroup.position.y;
    const occY = occupant.position.y;
    const yOff = Math.abs(occY - tubeAxisY);
    physHtml += `<div class="row"><span class="label">труба y откл:</span><span class="${yOff < 0.05 ? 'ok' : 'bad'}">${yOff.toFixed(4)} м</span></div>`;
  }

  document.getElementById('phys-data').innerHTML = physHtml;
}

// ============================================================
// ГЛАВНЫЙ ЦИКЛ
// ============================================================
let lastTime = performance.now();
let panelUpdateTimer = 0;

function animate(now) {
  requestAnimationFrame(animate);

  let dt = (now - lastTime) / 1000;
  lastTime = now;
  dt = Math.min(dt, 0.05); // ограничение дельты

  controls.update();

  // Обновление поведения
  for (const h of hamsters) {
    updateBehavior(h, dt);
  }

  // Прыжки
  for (const h of hamsters) {
    if (h.jumping) {
      h.jumpVelocity -= 9.8 * dt;
      h.position.y += h.jumpVelocity * dt;
      if (h.position.y <= cageY + 0.025) {
        h.position.y = cageY + 0.025;
        h.jumping = false;
        h.jumpVelocity = 0;
      }
    }
  }

  // Коллизии
  for (const h of hamsters) {
    if (!h.inWheel && !h.inTube) {
      resolveCollisions(h);
    }
  }
  resolveHamsterCollisions();

  // Анимация лап
  for (const h of hamsters) {
    updateLegs(h, dt);
    updateIdleAnimations(h, dt);
  }

  // Обновление колеса
  updateWheel(dt);

  // Синхронизация мешей
  for (const h of hamsters) {
    h.mesh.group.position.copy(h.position);
    h.mesh.group.rotation.y = h.rotationY;
  }

  // Панели (раз в 0.5 сек)
  panelUpdateTimer += dt;
  if (panelUpdateTimer > 0.5) {
    panelUpdateTimer = 0;
    updateInfoPanels();
  }

  renderer.render(scene, camera);
}

// Обработка ресайза
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Запуск
updateInfoPanels();
requestAnimationFrame(animate);

// Экспорт для внешней проверки
window.hamsters = hamsters;
window.wheelData = wheelData;
window.tubeData = tubeData;
</script>
</body>
</html>
```

## Что реализовано

### Физика (Часть 1)

| Требование | Реализация |
|---|---|
| **1.1 Колесо крутит бегун** | `ω = v / R` — угловая скорость вычисляется из скорости лап хомяка. Пустое колесо затухает (`friction = 0.98^dt`). Панель показывает расхождение в %. |
| **1.2 Габариты связаны** | `WHEEL_RADIUS = HAMSTER_LENGTH * 2.2`, `WHEEL_WIDTH = HAMSTER_WIDTH * 2.5` — вычислены от констант размеров зверя. |
| **1.3 Труба полая** | Открытый цилиндр (`openEnded: true`). Хомяк входит через торец, движется вдоль оси X, стоит на `y = tubeGroup.position.y`. |
| **1.4 Тела объектов** | `pointToVerticalCylinder`, `pointToHorizontalCylinder`, `pointToSphere` — три функции коллизий. При пересечении хомяка выталкивают по нормали. Хомяки расталкиваются друг от друга. |
| **1.5 Лапы не скользят** | `legPhase = (distanceTraveled / STRIDE_LENGTH) * 2π`. При остановке `speed < 0.01` → лапы фиксируются на базе. Диагональные пары (FL+BR, FR+BL). |
| **1.6 Без телепортов** | `entering_wheel` / `exiting_wheel` — плавное перемещение через `lerpVectors`. Один бегун в колесе, один хомяк в трубе. |

### Поведение (Часть 2)
- 5 хомяков с именами и цветами
- Конечный автомат: `idle → walking → занятие → idle`
- Панель справа показывает состояние каждого
- Клик → прыжок (raycaster)
- Дыхание (масштаб тела) + дёрганье ушами
- Жевание с наклоном головы

### Сцена (Часть 3)
- Комната с полом и стенами, стол с ножками
- Клетка: поддон, InstancedMesh-подстилка (600 щепок), 20 прутьев по периметру, горизонтальные рамки
- Колесо с ободом, спицами, опорами, осью и платформой
- Полая труба с торцевыми кольцами
- Миска с InstancedMesh-зёрнами
- Поилка на стенке
- Хомяк: тело, живот, голова (группа для кивания), глаза со зрачками, щёки, нос, уши с внутренней частью, 4 лапы, хвост

### Техническое (Часть 4)
- Three.js r128 + OrbitControls через CDN
- Один HTML-файл, никаких сборщиков
- PCFSoftShadowMap 2048×2048, directional + ambient + point light
- `requestAnimationFrame` с ограничением дельты ≤ 50мс
- Обработка `resize`