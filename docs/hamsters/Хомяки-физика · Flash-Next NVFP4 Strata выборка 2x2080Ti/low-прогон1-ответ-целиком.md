```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Клетка с хомяками — честная физика</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; background: #1a1a2e; font-family: 'Segoe UI', sans-serif; }
canvas { display: block; }
#panel {
  position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.85);
  color: #0f0; padding: 12px; border-radius: 8px; font-size: 12px;
  max-width: 280px; line-height: 1.5; border: 1px solid #333;
}
#panel h3 { color: #fff; margin-bottom: 6px; font-size: 13px; }
#panel .hamster-row { margin: 3px 0; padding: 3px 6px; border-radius: 3px; }
#debug {
  position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.85);
  color: #ff0; padding: 12px; border-radius: 8px; font-size: 11px;
  font-family: monospace; border: 1px solid #555; min-width: 220px;
}
#debug h4 { color: #fff; margin-bottom: 5px; }
</style>
</head>
<body>
<div id="panel"><h3>🐹 Хомяки</h3><div id="hamster-status"></div></div>
<div id="debug"><h4>⚙️ Физика колеса</h4><div id="wheel-debug"></div></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// КОНСТАНТЫ РАЗМЕРОВ (габарит зверя определяет колесо и трубу)
// ============================================================
const HAMSTER_BODY_LENGTH = 0.8;
const HAMSTER_BODY_HEIGHT = 0.5;
const HAMSTER_BODY_WIDTH = 0.45;
const HAMSTER_RADIUS = Math.max(HAMSTER_BODY_LENGTH, HAMSTER_BODY_HEIGHT) / 2;

// Колесо: радиус вычислен ОТ размера хомяка
const WHEEL_INNER_RADIUS = HAMSTER_BODY_HEIGHT + HAMSTER_BODY_LENGTH * 0.4 + 0.2; // 1.1
const WHEEL_OUTER_RADIUS = WHEEL_INNER_RADIUS + 0.08;
const WHEEL_WIDTH = HAMSTER_BODY_WIDTH + 0.5; // шире боков зверя
const WHEEL_FRICTION = 1.8;

// Труба: внутренний радиус шире высоты хомяка
const TUBE_INNER_RADIUS = HAMSTER_BODY_HEIGHT * 0.8 + 0.15; // 0.55
const TUBE_WALL = 0.06;
const TUBE_OUTER_RADIUS = TUBE_INNER_RADIUS + TUBE_WALL;
const TUBE_LENGTH = 4.5;

// Клетка
const CAGE_W = 9, CAGE_H = 4.5, CAGE_D = 6;

// Миска
const BOWL_RADIUS = 0.5;
const BOWL_HEIGHT = 0.25;

// ============================================================
// СЦЕНА
// ============================================================
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2a2a3a);
scene.fog = new THREE.Fog(0x2a2a3a, 20, 50);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(8, 6, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Свет
const ambientLight = new THREE.AmbientLight(0x404060, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xfff5e0, 0.9);
dirLight.position.set(5, 10, 7);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.left = -8; dirLight.shadow.camera.right = 8;
dirLight.shadow.camera.top = 8; dirLight.shadow.camera.bottom = -8;
dirLight.shadow.camera.near = 0.5; dirLight.shadow.camera.far = 30;
dirLight.shadow.bias = -0.001;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3);
fillLight.position.set(-3, 4, -5);
scene.add(fillLight);

// ============================================================
// КОМНАТА
// ============================================================
const roomGeo = new THREE.BoxGeometry(30, 15, 30);
const roomMat = new THREE.MeshStandardMaterial({ color: 0x3a3a4a, side: THREE.BackSide });
const room = new THREE.Mesh(roomGeo, roomMat);
room.position.y = 5;
scene.add(room);

// Стол
const tableGeo = new THREE.BoxGeometry(12, 0.3, 8);
const tableMat = new THREE.MeshStandardMaterial({ color: 0x8B6914, roughness: 0.7 });
const table = new THREE.Mesh(tableGeo, tableMat);
table.position.y = -0.15;
table.receiveShadow = true;
scene.add(table);

// Ножки стола
for (let x of [-5.5, 5.5]) for (let z of [-3.5, 3.5]) {
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 2, 8), tableMat);
  leg.position.set(x, -1.3, z);
  scene.add(leg);
}

// ============================================================
// КЛЕТКА
// ============================================================
const cageGroup = new THREE.Group();
scene.add(cageGroup);

// Поддон
const trayMat = new THREE.MeshStandardMaterial({ color: 0xcc4444, roughness: 0.4 });
const trayGeo = new THREE.BoxGeometry(CAGE_W, 0.15, CAGE_D);
const tray = new THREE.Mesh(trayGeo, trayMat);
tray.position.y = 0.075;
tray.receiveShadow = true;
cageGroup.add(tray);

// Подстилка (стружка) — InstancedMesh
const chipGeo = new THREE.BoxGeometry(0.12, 0.04, 0.03);
const chipMat = new THREE.MeshStandardMaterial({ color: 0xd4a843, roughness: 0.9 });
const chipCount = 800;
const chips = new THREE.InstancedMesh(chipGeo, chipMat, chipCount);
chips.receiveShadow = true;
const dummy = new THREE.Object3D();
for (let i = 0; i < chipCount; i++) {
  dummy.position.set(
    (Math.random() - 0.5) * (CAGE_W - 0.5),
    0.17 + Math.random() * 0.03,
    (Math.random() - 0.5) * (CAGE_D - 0.5)
  );
  dummy.rotation.set(Math.random() * 0.5, Math.random() * Math.PI, Math.random() * 0.3);
  dummy.scale.set(0.8 + Math.random() * 0.6, 0.8 + Math.random() * 0.5, 1);
  dummy.updateMatrix();
  chips.setMatrixAt(i, dummy.matrix);
}
cageGroup.add(chips);

// Прутья
const barMat = new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.7, roughness: 0.3 });
const barGeo = new THREE.CylinderGeometry(0.03, 0.03, CAGE_H, 6);

function addBars(count, positions) {
  positions.forEach(p => {
    const bar = new THREE.Mesh(barGeo, barMat);
    bar.position.set(p.x, CAGE_H / 2 + 0.15, p.z);
    bar.castShadow = true;
    cageGroup.add(bar);
  });
}

// Передняя и задняя стенки
for (let i = 0; i <= 20; i++) {
  const x = -CAGE_W / 2 + (CAGE_W / 20) * i;
  addBars(1, [{ x, z: CAGE_D / 2 }]);
  addBars(1, [{ x, z: -CAGE_D / 2 }]);
}
// Левая и правая стенки
for (let i = 0; i <= 14; i++) {
  const z = -CAGE_D / 2 + (CAGE_D / 14) * i;
  addBars(1, [{ x: CAGE_W / 2, z }]);
  addBars(1, [{ x: -CAGE_W / 2, z }]);
}

// Рамки сверху
const frameMat = new THREE.MeshStandardMaterial({ color: 0x666666, metalness: 0.6 });
function addFrame(w, d, x, y, z) {
  const f = new THREE.Mesh(new THREE.BoxGeometry(w, 0.08, d), frameMat);
  f.position.set(x, y, z);
  cageGroup.add(f);
}
addFrame(CAGE_W + 0.1, 0.08, 0, CAGE_H + 0.15, CAGE_D / 2);
addFrame(CAGE_W + 0.1, 0.08, 0, CAGE_H + 0.15, -CAGE_D / 2);
addFrame(0.08, CAGE_D + 0.1, CAGE_W / 2, CAGE_H + 0.15, 0);
addFrame(0.08, CAGE_D + 0.1, -CAGE_W / 2, CAGE_H + 0.15, 0);
// Нижние рамки
addFrame(CAGE_W + 0.1, 0.08, 0, 0.15, CAGE_D / 2);
addFrame(CAGE_W + 0.1, 0.08, 0, 0.15, -CAGE_D / 2);
addFrame(0.08, CAGE_D + 0.1, CAGE_W / 2, 0.15, 0);
addFrame(0.08, CAGE_D + 0.1, -CAGE_W / 2, 0.15, 0);

// ============================================================
// КОЛЕСО
// ============================================================
const wheelGroup = new THREE.Group();
wheelGroup.position.set(-2.5, WHEEL_INNER_RADIUS + 0.15, 0);
cageGroup.add(wheelGroup);

// Обод (вращается)
const wheelRotating = new THREE.Group();
wheelGroup.add(wheelRotating);

const rimGeo = new THREE.TorusGeometry(WHEEL_INNER_RADIUS, 0.04, 8, 48);
const rimMat = new THREE.MeshStandardMaterial({ color: 0xdd6633, roughness: 0.4, metalness: 0.3 });
const rim1 = new THREE.Mesh(rimGeo, rimMat);
rim1.position.z = WHEEL_WIDTH / 2;
rim1.castShadow = true;
wheelRotating.add(rim1);
const rim2 = new THREE.Mesh(rimGeo, rimMat);
rim2.position.z = -WHEEL_WIDTH / 2;
rim2.castShadow = true;
wheelRotating.add(rim2);

// Ступицы обода (поперечные перекладины)
const spokeMat = new THREE.MeshStandardMaterial({ color: 0xcc5522, roughness: 0.5 });
for (let i = 0; i < 12; i++) {
  const angle = (i / 12) * Math.PI * 2;
  const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.03, WHEEL_WIDTH), spokeMat);
  spoke.position.set(
    Math.cos(angle) * WHEEL_INNER_RADIUS,
    Math.sin(angle) * WHEEL_INNER_RADIUS,
    0
  );
  wheelRotating.add(spoke);
}

// Внутренняя поверхность (сетка/решётка для лап)
const innerSurfaceGeo = new THREE.CylinderGeometry(WHEEL_INNER_RADIUS - 0.02, WHEEL_INNER_RADIUS - 0.02, WHEEL_WIDTH - 0.1, 32, 1, true);
const innerSurfaceMat = new THREE.MeshStandardMaterial({ color: 0xbb4422, side: THREE.DoubleSide, transparent: true, opacity: 0.3 });
const innerSurface = new THREE.Mesh(innerSurfaceGeo, innerSurfaceMat);
innerSurface.rotation.x = Math.PI / 2;
wheelRotating.add(innerSurface);

// Ступица и ось
const hubGeo = new THREE.CylinderGeometry(0.08, 0.08, WHEEL_WIDTH + 0.3, 12);
const hubMat = new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.8 });
const hub = new THREE.Mesh(hubGeo, hubMat);
hub.rotation.x = Math.PI / 2;
wheelGroup.add(hub);

// Стойка колеса
const standMat = new THREE.MeshStandardMaterial({ color: 0x666666, metalness: 0.5 });
for (let z of [-WHEEL_WIDTH / 2 - 0.1, WHEEL_WIDTH / 2 + 0.1]) {
  const stand = new THREE.Mesh(new THREE.BoxGeometry(0.08, WHEEL_INNER_RADIUS + 0.15, 0.08), standMat);
  stand.position.set(0, -(WHEEL_INNER_RADIUS + 0.15) / 2 + 0.075, z);
  stand.castShadow = true;
  wheelGroup.add(stand);
}

// Состояние колеса
const wheelState = {
  angularVelocity: 0,
  angle: 0,
  occupant: null,
  radius: WHEEL_INNER_RADIUS
};

// ============================================================
// ТРУБА
// ============================================================
const tubeGroup = new THREE.Group();
tubeGroup.position.set(1.5, TUBE_OUTER_RADIUS + 0.15, -1);
cageGroup.add(tubeGroup);

// Внешняя стенка
const tubeOuterGeo = new THREE.CylinderGeometry(TUBE_OUTER_RADIUS, TUBE_OUTER_RADIUS, TUBE_LENGTH, 24, 1, true);
const tubeMat = new THREE.MeshStandardMaterial({ color: 0x44aa88, side: THREE.DoubleSide, roughness: 0.5 });
const tubeOuter = new THREE.Mesh(tubeOuterGeo, tubeMat);
tubeOuter.rotation.z = Math.PI / 2;
tubeOuter.castShadow = true;
tubeGroup.add(tubeOuter);

// Внутренняя стенка (видна изнутри)
const tubeInnerGeo = new THREE.CylinderGeometry(TUBE_INNER_RADIUS, TUBE_INNER_RADIUS, TUBE_LENGTH, 24, 1, true);
const tubeInnerMat = new THREE.MeshStandardMaterial({ color: 0x339977, side: THREE.BackSide, roughness: 0.6 });
const tubeInner = new THREE.Mesh(tubeInnerGeo, tubeInnerMat);
tubeInner.rotation.z = Math.PI / 2;
tubeGroup.add(tubeInner);

// Состояние трубы
const tubeState = {
  position: new THREE.Vector3(1.5, TUBE_OUTER_RADIUS + 0.15, -1),
  axis: new THREE.Vector3(1, 0, 0),
  halfLength: TUBE_LENGTH / 2,
  innerRadius: TUBE_INNER_RADIUS,
  outerRadius: TUBE_OUTER_RADIUS,
  occupant: null
};

// ============================================================
// МИСКА
// ============================================================
const bowlGroup = new THREE.Group();
bowlGroup.position.set(3, 0.15, 1.5);
cageGroup.add(bowlGroup);

const bowlGeo = new THREE.CylinderGeometry(BOWL_RADIUS, BOWL_RADIUS * 0.7, BOWL_HEIGHT, 16);
const bowlMat = new THREE.MeshStandardMaterial({ color: 0x3366cc, roughness: 0.3 });
const bowl = new THREE.Mesh(bowlGeo, bowlMat);
bowl.position.y = BOWL_HEIGHT / 2;
bowl.castShadow = true;
bowlGroup.add(bowl);

// Зёрна
const seedGeo = new THREE.SphereGeometry(0.04, 6, 4);
const seedMat = new THREE.MeshStandardMaterial({ color: 0xddaa33 });
for (let i = 0; i < 15; i++) {
  const seed = new THREE.Mesh(seedGeo, seedMat);
  const a = Math.random() * Math.PI * 2;
  const r = Math.random() * BOWL_RADIUS * 0.5;
  seed.position.set(Math.cos(a) * r, BOWL_HEIGHT * 0.6 + Math.random() * 0.05, Math.sin(a) * r);
  bowlGroup.add(seed);
}

const bowlState = {
  position: new THREE.Vector3(3, 0.15, 1.5),
  radius: BOWL_RADIUS + 0.1,
  occupant: null
};

// ============================================================
// ПОИЛКА
// ============================================================
const bottleGroup = new THREE.Group();
bottleGroup.position.set(CAGE_W / 2 - 0.3, 1.5, 1);
cageGroup.add(bottleGroup);

const bottleGeo = new THREE.CylinderGeometry(0.15, 0.15, 1.2, 12);
const bottleMat = new THREE.MeshStandardMaterial({ color: 0x88ccff, transparent: true, opacity: 0.5 });
const bottle = new THREE.Mesh(bottleGeo, bottleMat);
bottleGroup.add(bottle);

const spoutGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.3, 8);
const spoutMat = new THREE.MeshStandardMaterial({ color: 0x999999, metalness: 0.8 });
const spout = new THREE.Mesh(spoutGeo, spoutMat);
spout.position.y = -0.7;
bottleGroup.add(spout);

// ============================================================
// СОЗДАНИЕ ХОМЯКА
// ============================================================
const hamsters = [];
const hamsterNames = ['Пушок', 'Рыжик', 'Снежок', 'Уголёк', 'Карамель'];
const hamsterColors = [0xf5c542, 0xe8752a, 0xf0f0f0, 0x444444, 0xf0a050];
const hamsterPositions = [
  new THREE.Vector3(-1, 0.15, 1.5),
  new THREE.Vector3(0.5, 0.15, -1.5),
  new THREE.Vector3(2, 0.15, 0.5),
  new THREE.Vector3(-0.5, 0.15, 2),
  new THREE.Vector3(3.5, 0.15, -0.5)
];

function createHamster(name, color, pos) {
  const group = new THREE.Group();
  group.position.copy(pos);

  const bodyMat = new THREE.MeshStandardMaterial({ color, roughness: 0.8 });
  const bellyMat = new THREE.MeshStandardMaterial({ color: 0xffeedd, roughness: 0.9 });

  // Тело
  const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
  bodyGeo.scale(HAMSTER_BODY_LENGTH / 2, HAMSTER_BODY_HEIGHT / 2, HAMSTER_BODY_WIDTH / 2);
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.castShadow = true;
  group.add(body);

  // Живот
  const bellyGeo = new THREE.SphereGeometry(1, 12, 10);
  bellyGeo.scale(HAMSTER_BODY_LENGTH / 2.5, HAMSTER_BODY_HEIGHT / 2.5, HAMSTER_BODY_WIDTH / 2.2);
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.position.set(0, -HAMSTER_BODY_HEIGHT * 0.15, 0);
  group.add(belly);

  // Голова (отдельная группа для кивания)
  const headGroup = new THREE.Group();
  headGroup.position.set(HAMSTER_BODY_LENGTH / 2 + 0.1, HAMSTER_BODY_HEIGHT * 0.1, 0);
  group.add(headGroup);

  const headGeo = new THREE.SphereGeometry(0.18, 12, 10);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.castShadow = true;
  headGroup.add(head);

  // Щёки
  const cheekGeo = new THREE.SphereGeometry(0.09, 8, 6);
  const cheekMat = new THREE.MeshStandardMaterial({ color: 0xffccaa, roughness: 0.9 });
  const cheekL = new THREE.Mesh(cheekGeo, cheekMat);
  cheekL.position.set(0.1, -0.03, 0.12);
  headGroup.add(cheekL);
  const cheekR = new THREE.Mesh(cheekGeo, cheekMat);
  cheekR.position.set(0.1, -0.03, -0.12);
  headGroup.add(cheekR);

  // Нос
  const noseGeo = new THREE.SphereGeometry(0.035, 8, 6);
  const noseMat = new THREE.MeshStandardMaterial({ color: 0xff6688 });
  const nose = new THREE.Mesh(noseGeo, noseMat);
  nose.position.set(0.18, 0, 0);
  headGroup.add(nose);

  // Глаза
  const eyeGeo = new THREE.SphereGeometry(0.04, 8, 6);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
  const pupilGeo = new THREE.SphereGeometry(0.015, 6, 4);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0xffffff });

  for (let side of [-1, 1]) {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(0.12, 0.06, side * 0.1);
    headGroup.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(0.14, 0.07, side * 0.1);
    headGroup.add(pupil);
  }

  // Уши
  const earGeo = new THREE.SphereGeometry(0.07, 8, 6);
  earGeo.scale(1, 1.2, 0.4);
  const earMat = new THREE.MeshStandardMaterial({ color, roughness: 0.8 });
  const earInnerMat = new THREE.MeshStandardMaterial({ color: 0xffaaaa, roughness: 0.9 });
  const earInnerGeo = new THREE.SphereGeometry(0.05, 6, 4);
  earInnerGeo.scale(1, 1.2, 0.3);

  const ears = [];
  for (let side of [-1, 1]) {
    const ear = new THREE.Mesh(earGeo, earMat);
    ear.position.set(-0.02, 0.16, side * 0.1);
    headGroup.add(ear);
    const earInner = new THREE.Mesh(earInnerGeo, earInnerMat);
    earInner.position.set(0.01, 0.16, side * 0.1);
    headGroup.add(earInner);
    ears.push(ear);
  }

  // Лапы
  const legGeo = new THREE.CylinderGeometry(0.04, 0.035, 0.2, 8);
  const legMat = new THREE.MeshStandardMaterial({ color: 0xddbbaa, roughness: 0.8 });
  const legs = [];
  const legPositions = [
    { x: HAMSTER_BODY_LENGTH * 0.3, z: HAMSTER_BODY_WIDTH * 0.35 },
    { x: HAMSTER_BODY_LENGTH * 0.3, z: -HAMSTER_BODY_WIDTH * 0.35 },
    { x: -HAMSTER_BODY_LENGTH * 0.3, z: HAMSTER_BODY_WIDTH * 0.35 },
    { x: -HAMSTER_BODY_LENGTH * 0.3, z: -HAMSTER_BODY_WIDTH * 0.35 }
  ];
  legPositions.forEach(lp => {
    const legPivot = new THREE.Group();
    legPivot.position.set(lp.x, -HAMSTER_BODY_HEIGHT / 2 + 0.05, lp.z);
    const leg = new THREE.Mesh(legGeo, legMat);
    leg.position.y = -0.1;
    legPivot.add(leg);
    group.add(legPivot);
    legs.push(legPivot);
  });

  // Хвост
  const tailGeo = new THREE.CylinderGeometry(0.025, 0.015, 0.12, 6);
  const tail = new THREE.Mesh(tailGeo, bodyMat);
  tail.position.set(-HAMSTER_BODY_LENGTH / 2 - 0.05, -0.05, 0);
  tail.rotation.z = Math.PI / 4;
  group.add(tail);

  cageGroup.add(group);

  const hamster = {
    name, color, group, body, headGroup, legs, ears, tail, cheekL, cheekR,
    position: pos.clone(),
    velocity: new THREE.Vector3(),
    rotation: 0,
    state: 'idle',
    stateTimer: 0,
    target: null,
    stepPhase: 0,
    distanceTraveled: 0,
    speed: 0,
    breathPhase: Math.random() * Math.PI * 2,
    earTwitchTimer: Math.random() * 3,
    bounceTimer: 0,
    // Wheel specific
    wheelEntryProgress: 0,
    wheelExitProgress: 0,
    // Tube specific
    tubeProgress: 0,
    tubeDirection: 1,
    // Eating
    chewPhase: 0
  };
  hamsters.push(hamster);
  return hamster;
}

hamsterNames.forEach((name, i) => {
  createHamster(name, hamsterColors[i], hamsterPositions[i]);
});

// ============================================================
// ВЗАИМОДЕЙСТВИЕ (клик — прыжок)
// ============================================================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', (e) => {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const meshes = hamsters.map(h => h.body);
  const intersects = raycaster.intersectObjects(meshes);
  if (intersects.length > 0) {
    const h = hamsters.find(h => h.body === intersects[0].object);
    if (h && h.state === 'idle') {
      h.bounceTimer = 0.4;
    }
  }
});

// ============================================================
// КОЛЛИЗИИ
// ============================================================
function resolveCollisions(h) {
  const floorY = 0.15 + HAMSTER_BODY_HEIGHT / 2;
  const wallMargin = 0.3;

  // Стенки клетки
  const hw = CAGE_W / 2 - wallMargin;
  const hd = CAGE_D / 2 - wallMargin;
  if (h.position.x > hw) h.position.x = hw;
  if (h.position.x < -hw) h.position.x = -hw;
  if (h.position.z > hd) h.position.z = hd;
  if (h.position.z < -hd) h.position.z = -hd;

  // Колесо (цилиндр в плоскости XY, ось по Z)
  const wheelCenter2D = new THREE.Vector2(wheelGroup.position.x, wheelGroup.position.y);
  const hDist2D = new THREE.Vector2(h.position.x - wheelGroup.position.x, h.position.y - wheelGroup.position.y);
  const distToWheel = hDist2D.length();
  const minDist = WHEEL_OUTER_RADIUS + HAMSTER_RADIUS * 0.6;

  if (distToWheel < minDist && h.state !== 'running_wheel' && h.state !== 'entering_wheel' && h.state !== 'exiting_wheel') {
    const pushDir = hDist2D.clone().normalize();
    h.position.x = wheelGroup.position.x + pushDir.x * minDist;
    h.position.y = wheelGroup.position.y + pushDir.y * minDist;
    if (h.position.y < floorY) h.position.y = floorY;
  }

  // Миска (круг на полу)
  const distToBowl = Math.sqrt(
    Math.pow(h.position.x - bowlState.position.x, 2) +
    Math.pow(h.position.z - bowlState.position.z, 2)
  );
  const bowlMinDist = bowlState.radius + HAMSTER_BODY_WIDTH * 0.4;
  if (distToBowl < bowlMinDist && h.state !== 'eating' && h.state !== 'walking_to_bowl') {
    const pushDir = new THREE.Vector2(
      h.position.x - bowlState.position.x,
      h.position.z - bowlState.position.z
    ).normalize();
    h.position.x = bowlState.position.x + pushDir.x * bowlMinDist;
    h.position.z = bowlState.position.z + pushDir.y * bowlMinDist;
  }

  // Труба (капсула вдоль X)
  if (h.state !== 'in_tube' && h.state !== 'entering_tube' && h.state !== 'exiting_tube') {
    const tubePos = tubeState.position;
    const dx = h.position.x - tubePos.x;
    const dz = h.position.z - tubePos.z;
    const clampedX = Math.max(-tubeState.halfLength, Math.min(tubeState.halfLength, dx));
    const closestX = tubePos.x + clampedX;
    const distToTubeAxis = Math.sqrt(
      Math.pow(h.position.x - closestX, 2) +
      Math.pow(h.position.z - tubePos.z, 2)
    );
    const tubeMinDist = TUBE_OUTER_RADIUS + HAMSTER_BODY_WIDTH * 0.4;
    if (distToTubeAxis < tubeMinDist && Math.abs(dx) < tubeState.halfLength) {
      const pushDir = new THREE.Vector2(
        h.position.x - closestX,
        h.position.z - tubePos.z
      );
      if (pushDir.length() > 0.001) {
        pushDir.normalize();
        h.position.x = closestX + pushDir.x * tubeMinDist;
        h.position.z = tubePos.z + pushDir.y * tubeMinDist;
      }
    }
  }

  // Хомяк-хомяк
  for (const other of hamsters) {
    if (other === h) continue;
    const dx = h.position.x - other.position.x;
    const dz = h.position.z - other.position.z;
    const dist = Math.sqrt(dx * dx + dz * dz);
    const minHDist = HAMSTER_BODY_WIDTH * 1.2;
    if (dist < minHDist && dist > 0.001) {
      const push = (minHDist - dist) * 0.5;
      const nx = dx / dist;
      const nz = dz / dist;
      h.position.x += nx * push;
      h.position.z += nz * push;
      other.position.x -= nx * push;
      other.position.z -= nz * push;
    }
  }
}

// ============================================================
// ПОВЕДЕНИЕ (конечный автомат)
// ============================================================
const WALK_SPEED = 1.2;
const RUN_SPEED = 2.5;
const STEP_LENGTH = 0.15;

function pickActivity(h) {
  const activities = [];
  if (!wheelState.occupant) activities.push('wheel');
  if (!tubeState.occupant) activities.push('tube');
  if (!bowlState.occupant) activities.push('bowl');
  activities.push('walk');
  activities.push('walk');
  return activities[Math.floor(Math.random() * activities.length)];
}

function updateBehavior(h, dt) {
  h.stateTimer -= dt;

  switch (h.state) {
    case 'idle':
      h.speed = 0;
      if (h.stateTimer <= 0) {
        const act = pickActivity(h);
        if (act === 'wheel') {
          h.state = 'walking_to_wheel';
          h.target = new THREE.Vector3(
            wheelGroup.position.x,
            0.15 + HAMSTER_BODY_HEIGHT / 2,
            WHEEL_WIDTH / 2 + 0.5
          );
          h.stateTimer = 5;
        } else if (act === 'tube') {
          h.state = 'walking_to_tube';
          const enterSide = Math.random() < 0.5 ? -1 : 1;
          h.tubeDirection = enterSide;
          h.target = new THREE.Vector3(
            tubeState.position.x + enterSide * (tubeState.halfLength + 0.3),
            0.15 + HAMSTER_BODY_HEIGHT / 2,
            tubeState.position.z
          );
          h.stateTimer = 5;
        } else if (act === 'bowl') {
          h.state = 'walking_to_bowl';
          h.target = new THREE.Vector3(
            bowlState.position.x + (Math.random() - 0.5) * 0.3,
            0.15 + HAMSTER_BODY_HEIGHT / 2,
            bowlState.position.z + (Math.random() - 0.5) * 0.3
          );
          h.stateTimer = 5;
        } else {
          h.state = 'walking';
          h.target = new THREE.Vector3(
            (Math.random() - 0.5) * (CAGE_W - 2),
            0.15 + HAMSTER_BODY_HEIGHT / 2,
            (Math.random() - 0.5) * (CAGE_D - 2)
          );
          h.stateTimer = 4 + Math.random() * 3;
        }
      }
      break;

    case 'walking':
    case 'walking_to_wheel':
    case 'walking_to_tube':
    case 'walking_to_bowl': {
      if (!h.target) { h.state = 'idle'; h.stateTimer = 1; break; }
      const dx = h.target.x - h.position.x;
      const dz = h.target.z - h.position.z;
      const dist = Math.sqrt(dx * dx + dz * dz);

      if (dist < 0.15) {
        // Достиг цели
        if (h.state === 'walking_to_wheel') {
          h.state = 'entering_wheel';
          h.wheelEntryProgress = 0;
          wheelState.occupant = h;
          h.stateTimer = 6 + Math.random() * 4;
        } else if (h.state === 'walking_to_tube') {
          h.state = 'entering_tube';
          h.tubeProgress = 0;
          tubeState.occupant = h;
          h.stateTimer = 8;
        } else if (h.state === 'walking_to_bowl') {
          h.state = 'eating';
          bowlState.occupant = h;
          h.stateTimer = 4 + Math.random() * 3;
          h.chewPhase = 0;
        } else {
          h.state = 'idle';
          h.stateTimer = 1 + Math.random() * 2;
        }
        h.speed = 0;
      } else {
        const nx = dx / dist;
        const nz = dz / dist;
        h.position.x += nx * WALK_SPEED * dt;
        h.position.z += nz * WALK_SPEED * dt;
        h.position.y = 0.15 + HAMSTER_BODY_HEIGHT / 2;
        h.rotation = Math.atan2(nx, nz);
        h.speed = WALK_SPEED;
      }

      if (h.stateTimer <= 0) {
        h.state = 'idle';
        h.stateTimer = 1;
        h.speed = 0;
      }
      break;
    }

    case 'entering_wheel': {
      h.wheelEntryProgress += dt * 1.5;
      if (h.wheelEntryProgress >= 1) {
        h.wheelEntryProgress = 1;
        h.state = 'running_wheel';
      }
      // Интерполяция позиции к нижней точке колеса
      const wheelBottom = new THREE.Vector3(
        wheelGroup.position.x,
        wheelGroup.position.y - WHEEL_INNER_RADIUS + HAMSTER_BODY_HEIGHT / 2,
        wheelGroup.position.z
      );
      h.position.lerp(wheelBottom, dt * 3);
      h.rotation = Math.PI / 2; // смотрит вперёд (вдоль оси Z колеса)
      h.speed = 0;
      break;
    }

    case 'running_wheel': {
      // Хомяк бежит — задаёт скорость
      h.speed = RUN_SPEED * (0.8 + 0.2 * Math.sin(h.stateTimer * 0.5));

      // Угловая скорость колеса = v / R
      const targetOmega = h.speed / WHEEL_INNER_RADIUS;
      // Плавное приближение к целевой угловой скорости
      wheelState.angularVelocity += (targetOmega - wheelState.angularVelocity) * dt * 5;

      // Позиция в колесе: нижняя точка
      h.position.set(
        wheelGroup.position.x,
        wheelGroup.position.y - WHEEL_INNER_RADIUS + HAMSTER_BODY_HEIGHT / 2,
        wheelGroup.position.z
      );
      h.rotation = Math.PI / 2;

      if (h.stateTimer <= 0) {
        h.state = 'exiting_wheel';
        h.wheelExitProgress = 0;
      }
      break;
    }

    case 'exiting_wheel': {
      h.wheelExitProgress += dt * 1.5;
      if (h.wheelExitProgress >= 1) {
        h.state = 'idle';
        h.stateTimer = 1 + Math.random() * 2;
        wheelState.occupant = null;
        h.speed = 0;
        break;
      }
      // Выход из колеса
      const wheelBottom = new THREE.Vector3(
        wheelGroup.position.x,
        wheelGroup.position.y - WHEEL_INNER_RADIUS + HAMSTER_BODY_HEIGHT / 2,
        wheelGroup.position.z
      );
      const exitTarget = new THREE.Vector3(
        wheelGroup.position.x,
        0.15 + HAMSTER_BODY_HEIGHT / 2,
        WHEEL_WIDTH / 2 + 0.5
      );
      h.position.lerpVectors(wheelBottom, exitTarget, h.wheelExitProgress);
      h.speed = 0;
      break;
    }

    case 'entering_tube': {
      h.tubeProgress += dt * 0.8;
      if (h.tubeProgress >= 1) {
        h.tubeProgress = 0;
        h.state = 'in_tube';
      }
      const tubeEntrance = new THREE.Vector3(
        tubeState.position.x + h.tubeDirection * (tubeState.halfLength + 0.3),
        0.15 + HAMSTER_BODY_HEIGHT / 2,
        tubeState.position.z
      );
      const tubeInside = new THREE.Vector3(
        tubeState.position.x + h.tubeDirection * (tubeState.halfLength - 0.3),
        TUBE_OUTER_RADIUS - TUBE_INNER_RADIUS + HAMSTER_BODY_HEIGHT / 2 + 0.15,
        tubeState.position.z
      );
      h.position.lerpVectors(tubeEntrance, tubeInside, h.tubeProgress);
      h.rotation = h.tubeDirection > 0 ? -Math.PI / 2 : Math.PI / 2;
      h.speed = WALK_SPEED * 0.7;
      break;
    }

    case 'in_tube': {
      h.tubeProgress += dt * 0.3;
      if (h.tubeProgress >= 1) {
        h.state = 'exiting_tube';
        h.tubeProgress = 0;
      }
      // Движение вдоль оси трубы
      const startX = tubeState.position.x + h.tubeDirection * (tubeState.halfLength - 0.3);
      const endX = tubeState.position.x - h.tubeDirection * (tubeState.halfLength - 0.3);
      h.position.x = startX + (endX - startX) * h.tubeProgress;
      h.position.z = tubeState.position.z;
      // Стоит на внутреннем дне трубы
      h.position.y = TUBE_OUTER_RADIUS - TUBE_INNER_RADIUS + HAMSTER_BODY_HEIGHT / 2 + 0.15;
      h.rotation = h.tubeDirection > 0 ? -Math.PI / 2 : Math.PI / 2;
      h.speed = WALK_SPEED * 0.7;
      break;
    }

    case 'exiting_tube': {
      h.tubeProgress += dt * 1.2;
      if (h.tubeProgress >= 1) {
        h.state = 'idle';
        h.stateTimer = 1 + Math.random() * 2;
        tubeState.occupant = null;
        h.speed = 0;
        break;
      }
      const tubeExitStart = new THREE.Vector3(
        tubeState.position.x - h.tubeDirection * (tubeState.halfLength - 0.3),
        TUBE_OUTER_RADIUS - TUBE_INNER_RADIUS + HAMSTER_BODY_HEIGHT / 2 + 0.15,
        tubeState.position.z
      );
      const tubeExitEnd = new THREE.Vector3(
        tubeState.position.x - h.tubeDirection * (tubeState.halfLength + 0.5),
        0.15 + HAMSTER_BODY_HEIGHT / 2,
        tubeState.position.z
      );
      h.position.lerpVectors(tubeExitStart, tubeExitEnd, h.tubeProgress);
      h.speed = WALK_SPEED * 0.7;
      break;
    }

    case 'eating': {
      h.speed = 0;
      h.chewPhase += dt * 8;
      h.position.y = 0.15 + HAMSTER_BODY_HEIGHT / 2;
      if (h.stateTimer <= 0) {
        h.state = 'idle';
        h.stateTimer = 1 + Math.random() * 2;
        bowlState.occupant = null;
      }
      break;
    }
  }
}

// ============================================================
// АНИМАЦИЯ ЛАП (фаза от пройденного пути)
// ============================================================
function updateLegs(h, dt) {
  // Пройденный путь
  const pathDelta = h.speed * dt;
  h.distanceTraveled += pathDelta;

  // Фаза шага: phase += (путь / длина шага) * 2π
  if (h.speed > 0.01) {
    h.stepPhase += (pathDelta / STEP_LENGTH) * Math.PI * 2;
  }
  // При остановке фаза не меняется — лапы замирают

  // Диагональные пары: FL+BR, FR+BL
  const legAngles = [
    Math.sin(h.stepPhase) * 0.4,           // FL
    Math.sin(h.stepPhase + Math.PI) * 0.4, // FR
    Math.sin(h.stepPhase + Math.PI) * 0.4, // BL
    Math.sin(h.stepPhase) * 0.4            // BR
  ];

  h.legs.forEach((leg, i) => {
    leg.rotation.x = legAngles[i];
  });
}

// ============================================================
// АНИМАЦИЯ ДЫХАНИЯ И УШЕЙ
// ============================================================
function updateIdleAnimations(h, dt) {
  h.breathPhase += dt * 2.5;
  const breathScale = 1 + Math.sin(h.breathPhase) * 0.02;
  h.body.scale.set(
    HAMSTER_BODY_LENGTH / 2 * breathScale,
    HAMSTER_BODY_HEIGHT / 2 * (1 + Math.sin(h.breathPhase) * 0.03),
    HAMSTER_BODY_WIDTH / 2 * breathScale
  );

  // Дёрганье ушей
  h.earTwitchTimer -= dt;
  if (h.earTwitchTimer <= 0) {
    h.earTwitchTimer = 2 + Math.random() * 4;
    const ear = h.ears[Math.floor(Math.random() * 2)];
    ear.userData.twitch = 0.3;
  }
  h.ears.forEach(ear => {
    if (ear.userData.twitch > 0) {
      ear.userData.twitch -= dt;
      ear.rotation.x = Math.sin(ear.userData.twitch * 20) * 0.3;
    } else {
      ear.rotation.x = 0;
    }
  });

  // Прыжок
  if (h.bounceTimer > 0) {
    h.bounceTimer -= dt;
    const t = 1 - h.bounceTimer / 0.4;
    h.position.y = 0.15 + HAMSTER_BODY_HEIGHT / 2 + Math.sin(t * Math.PI) * 0.5;
  }

  // Жевание у миски
  if (h.state === 'eating') {
    h.headGroup.rotation.x = Math.sin(h.chewPhase) * 0.15;
    h.cheekL.scale.setScalar(1 + Math.sin(h.chewPhase * 2) * 0.1);
    h.cheekR.scale.setScalar(1 + Math.sin(h.chewPhase * 2 + 1) * 0.1);
  } else {
    h.headGroup.rotation.x = 0;
    h.cheekL.scale.setScalar(1);
    h.cheekR.scale.setScalar(1);
  }
}

// ============================================================
// ОБНОВЛЕНИЕ КОЛЕСА (физика)
// ============================================================
function updateWheel(dt) {
  if (!wheelState.occupant) {
    // Трение — колесо замедляется
    wheelState.angularVelocity *= Math.max(0, 1 - WHEEL_FRICTION * dt);
    if (Math.abs(wheelState.angularVelocity) < 0.01) wheelState.angularVelocity = 0;
  }

  wheelState.angle += wheelState.angularVelocity * dt;
  wheelRotating.rotation.z = wheelState.angle;
}

// ============================================================
// ОБНОВЛЕНИЕ ВИЗУАЛА ХОМЯКА
// ============================================================
function updateHamsterVisual(h) {
  h.group.position.copy(h.position);
  h.group.rotation.y = h.rotation;

  // В колесе: хомяк должен быть ориентирован по касательной к колесу
  if (h.state === 'running_wheel') {
    // Смотрит в сторону движения обода (вниз-вперёд)
    h.group.rotation.y = Math.PI / 2;
    // Тело слегка наклонено
    h.group.rotation.z = 0;
  }
}

// ============================================================
// ПАНЕЛЬ СТАТУСА
// ============================================================
function updatePanel() {
  const statusDiv = document.getElementById('hamster-status');
  let html = '';
  hamsters.forEach(h => {
    let status = '';
    switch (h.state) {
      case 'idle': status = '🧍 стоит'; break;
      case 'walking': status = '🚶 гуляет'; break;
      case 'walking_to_wheel': status = '→ идёт к колесу'; break;
      case 'entering_wheel': status = '🎡 входит в колесо'; break;
      case 'running_wheel': status = '🏃 бежит в колесе'; break;
      case 'exiting_wheel': status = '🎡 выходит из колеса'; break;
      case 'walking_to_tube': status = '→ идёт к трубе'; break;
      case 'entering_tube': status = '🕳️ входит в трубу'; break;
      case 'in_tube': status = '🐛 ползёт по трубе'; break;
      case 'exiting_tube': status = '🕳️ выходит из трубы'; break;
      case 'walking_to_bowl': status = '→ идёт к миске'; break;
      case 'eating': status = '🌾 грызёт зёрна'; break;
    }
    const colorHex = '#' + h.color.toString(16).padStart(6, '0');
    html += `<div class="hamster-row" style="border-left:3px solid ${colorHex}"><b>${h.name}</b>: ${status}</div>`;
  });
  statusDiv.innerHTML = html;
}

// ============================================================
// ПАНЕЛЬ ОТЛАДКИ КОЛЕСА
// ============================================================
function updateWheelDebug() {
  const debugDiv = document.getElementById('wheel-debug');
  const omega = wheelState.angularVelocity;
  const rimSpeed = Math.abs(omega) * WHEEL_INNER_RADIUS;
  const occupant = wheelState.occupant;
  const legSpeed = occupant ? occupant.speed : 0;
  const discrepancy = legSpeed > 0.01 ? Math.abs(rimSpeed - legSpeed) / legSpeed * 100 : 0;

  let html = '';
  html += `ω = ${omega.toFixed(3)} рад/с<br>`;
  html += `R = ${WHEEL_INNER_RADIUS.toFixed(2)} м<br>`;
  html += `Скорость обода |ω|·R = ${rimSpeed.toFixed(3)} м/с<br>`;
  html += `Скорость лап v = ${legSpeed.toFixed(3)} м/с<br>`;
  html += `Расхождение: ${discrepancy.toFixed(1)}%<br>`;
  html += `<br><span style="color:#888">Габарит зверя: ${HAMSTER_BODY_HEIGHT}×${HAMSTER_BODY_LENGTH}<br>`;
  html += `Радиус колеса: ${WHEEL_INNER_RADIUS.toFixed(2)} (> ${HAMSTER_BODY_HEIGHT})</span>`;

  if (occupant) {
    html += `<br><br><span style="color:#0f0">🏃 ${occupant.name} бежит</span>`;
    html += `<br>Позиция Y: ${occupant.position.y.toFixed(3)}`;
    html += `<br>Низ колеса Y: ${(wheelGroup.position.y - WHEEL_INNER_RADIUS + HAMSTER_BODY_HEIGHT/2).toFixed(3)}`;
  } else {
    html += `<br><br><span style="color:#f80">Пустое колесо, ω затухает</span>`;
  }

  debugDiv.innerHTML = html;
}

// ============================================================
// ГЛАВНЫЙ ЦИКЛ
// ============================================================
let lastTime = performance.now();
let panelTimer = 0;

function animate(currentTime) {
  requestAnimationFrame(animate);

  let dt = (currentTime - lastTime) / 1000;
  lastTime = currentTime;
  dt = Math.min(dt, 0.05); // Ограничение дельты

  // Обновление поведения и физики
  hamsters.forEach(h => {
    updateBehavior(h, dt);
    updateLegs(h, dt);
    updateIdleAnimations(h, dt);
    resolveCollisions(h);
    updateHamsterVisual(h);
  });

  // Колесо
  updateWheel(dt);

  // Панели (обновляем не каждый кадр)
  panelTimer += dt;
  if (panelTimer > 0.2) {
    panelTimer = 0;
    updatePanel();
    updateWheelDebug();
  }

  controls.update();
  renderer.render(scene, camera);
}

// ============================================================
// RESIZE
// ============================================================
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Старт
animate(performance.now());
</script>
</body>
</html>
```

Этот файл реализует все ключевые требования:

**Физика колеса (§1.1):**
- `ω = v / R` — угловая скорость вычисляется из скорости бега хомяка
- Пустое колесо замедляется трением (`angularVelocity *= 1 - friction * dt`)
- Панель отладки показывает расхождение |ω|·R vs v в процентах

**Габариты (§1.2):**
- `WHEEL_INNER_RADIUS` вычислен из `HAMSTER_BODY_HEIGHT + HAMSTER_BODY_LENGTH * 0.4 + 0.2`
- `WHEEL_WIDTH > HAMSTER_BODY_WIDTH` — обод шире боков

**Труба (§1.3):**
- Хомяк входит только через торец (`entering_tube` → `in_tube` → `exiting_tube`)
- Внутри стоит на дне (`y = TUBE_OUTER_RADIUS - TUBE_INNER_RADIUS + HAMSTER_BODY_HEIGHT/2`)
- Боковая стенка твёрдая — коллизия выталкивает наружу

**Коллизии (§1.4):**
- Круговые коллизии с колесом, миской, трубой
- Мягкое расталкивание хомяков

**Лапы (§1.5):**
- `stepPhase += (pathDelta / STEP_LENGTH) * 2π` — фаза от пути
- Диагональные пары (FL+BR, FR+BL)
- При остановке фаза не меняется

**Переходы (§1.6):**
- Плавная интерполяция при входе/выходе из колеса и трубы
- `occupant` — блокировка объекта одним хомяком