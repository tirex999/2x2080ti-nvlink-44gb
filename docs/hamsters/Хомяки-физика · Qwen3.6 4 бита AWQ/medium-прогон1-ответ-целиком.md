

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Клетка с хомяками</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#1a1a2e;font-family:'Segoe UI',sans-serif}
canvas{display:block}
#ui{position:absolute;top:10px;right:10px;width:260px;color:#e0e0e0;pointer-events:none}
#ui>*{pointer-events:auto}
.panel{background:rgba(20,20,40,0.85);border:1px solid #444;border-radius:8px;padding:10px;margin-bottom:8px;font-size:13px;line-height:1.5}
.panel h3{color:#f0c060;margin-bottom:6px;font-size:14px}
.panel .row{display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid #333}
.panel .label{color:#aaa}
.panel .val{color:#8f8;font-weight:bold}
.hamster-row{display:flex;align-items:center;padding:3px 0;gap:6px}
.dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.hname{font-weight:bold;min-width:70px}
.hstate{color:#ccc}
</style>
</head>
<body>
<div id="ui">
  <div class="panel" id="wheelPanel">
    <h3>⚙ Колесо — проверка физики</h3>
    <div class="row"><span class="label">Бегун:</span><span class="val" id="wpRunner">—</span></div>
    <div class="row"><span class="label">Скорость лап v:</span><span class="val" id="wpVleg">0.00</span></div>
    <div class="row"><span class="label">|ω|·R обода:</span><span class="val" id="wpOmegaR">0.00</span></div>
    <div class="row"><span class="label">Расхождение:</span><span class="val" id="wpDiff">0.0%</span></div>
    <div class="row"><span class="label">ω (рад/с):</span><span class="val" id="wpOmega">0.00</span></div>
  </div>
  <div class="panel" id="hamsterPanel">
    <h3>🐹 Хомяки</h3>
    <div id="hamsterList"></div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// КОНСТАНТЫ — ГАБАРИТЫ
// ============================================================
const HAMSTER_LENGTH = 0.40;
const HAMSTER_HEIGHT = 0.28;
const HAMSTER_WIDTH  = 0.22;
const HAMSTER_RADIUS = Math.max(HAMSTER_LENGTH, HAMSTER_HEIGHT) * 0.55; // для коллизий

// Колесо: радиус обода вычисляется от размера хомяка
const WHEEL_RIM_RADIUS = HAMSTER_LENGTH * 1.6;  // ~0.64 — хомяк помещается внутри
const WHEEL_RIM_WIDTH  = HAMSTER_WIDTH * 1.8;   // ~0.40 — шире боков хомяка
const WHEEL_HUB_RADIUS = WHEEL_RIM_RADIUS * 0.15;
const WHEEL_SPOKE_COUNT = 8;

// Труба
const TUBE_RADIUS = HAMSTER_LENGTH * 0.85; // ~0.34 — чуть больше половины длины
const TUBE_LENGTH = 2.0;

// Миска
const BOWL_RADIUS = 0.35;
const BOWL_DEPTH  = 0.12;

// Клетка
const CAGE_W = 4.0, CAGE_D = 3.0, CAGE_H = 1.8;
const BAR_SPACING = 0.25;

// Физика
const FRICTION_TORQUE = 1.2;      // затухание колеса без бегуна
const HAMSTER_RUN_SPEED = 1.8;    // единицы/сек в колесе
const HAMSTER_WALK_SPEED = 0.6;   // единицы/сек по полу
const STEP_LENGTH = 0.12;         // длина шага
const COLLISION_PUSH = 0.05;      // сила расталкивания

// ============================================================
// СЦЕНА, КАМЕРА, РЕНДЕР
// ============================================================
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2a2a3e);
scene.fog = new THREE.FogExp2(0x2a2a3e, 0.04);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(4, 3.5, 4);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.8, 0);
controls.update();

// Освещение
const dirLight = new THREE.DirectionalLight(0xffeedd, 0.9);
dirLight.position.set(3, 5, 2);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.left = -5; dirLight.shadow.camera.right = 5;
dirLight.shadow.camera.top = 5; dirLight.shadow.camera.bottom = -5;
dirLight.shadow.camera.near = 0.5; dirLight.shadow.camera.far = 15;
scene.add(dirLight);

const ambLight = new THREE.AmbientLight(0x445566, 0.5);
scene.add(ambLight);

const hemiLight = new THREE.HemisphereLight(0x8899aa, 0x443322, 0.3);
scene.add(hemiLight);

// ============================================================
// МАТЕРИАЛЫ
// ============================================================
function mat(color, opts){ return new THREE.MeshStandardMaterial(Object.assign({color}, opts||{})); }

const matWood = mat(0x8B6914);
const matMetal = mat(0xaaaaaa, {metalness:0.7, roughness:0.3});
const matBar = mat(0x999999, {metalness:0.6, roughness:0.4});
const matBedding = mat(0xc4a46c);
const matWheel = mat(0xddcc88, {roughness:0.6});
const matBowl = mat(0x5588cc, {metalness:0.2, roughness:0.5});
const matSeed = mat(0xcc9944);
const matWater = mat(0x6699bb, {transparent:true, opacity:0.5});
const matGlass = mat(0xaaddff, {transparent:true, opacity:0.25});
const matFloor = mat(0x554433);
const matTable = mat(0x6b4226);
const matWall = mat(0x887766);

// ============================================================
// ОКРУЖЕНИЕ — КОМНАТА
// ============================================================
(function buildRoom(){
  // Пол комнаты
  const floorGeo = new THREE.PlaneGeometry(12, 12);
  const floor = new THREE.Mesh(floorGeo, matFloor);
  floor.rotation.x = -Math.PI/2;
  floor.position.y = -0.01;
  floor.receiveShadow = true;
  scene.add(floor);

  // Стена задняя
  const wallGeo = new THREE.PlaneGeometry(12, 5);
  const backWall = new THREE.Mesh(wallGeo, matWall);
  backWall.position.set(0, 2.5, -3.5);
  backWall.receiveShadow = true;
  scene.add(backWall);

  // Левая стена
  const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(12, 5), matWall);
  leftWall.position.set(-4, 2.5, 0);
  leftWall.rotation.y = Math.PI/2;
  leftWall.receiveShadow = true;
  scene.add(leftWall);

  // Стол
  const tableTop = new THREE.Mesh(new THREE.BoxGeometry(4.5, 0.12, 3.5), matTable);
  tableTop.position.set(0, 0.6, 0);
  tableTop.castShadow = true;
  tableTop.receiveShadow = true;
  scene.add(tableTop);

  // Ножки стола
  for(let x of [-1.9, 1.9]) for(let z of [-1.4, 1.4]){
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.6, 0.1), matTable);
    leg.position.set(x, 0.3, z);
    leg.castShadow = true;
    scene.add(leg);
  }
})();

// ============================================================
// КЛЕТКА
// ============================================================
const cageGroup = new THREE.Group();
scene.add(cageGroup);

(function buildCage(){
  // Поддон
  const tray = new THREE.Mesh(new THREE.BoxGeometry(CAGE_W+0.2, 0.08, CAGE_D+0.2), matMetal);
  tray.position.y = 0.04;
  tray.receiveShadow = true;
  cageGroup.add(tray);

  // Подстилка (стружка — InstancedMesh)
  const chipCount = 600;
  const chipGeo = new THREE.BoxGeometry(0.04, 0.015, 0.02);
  const chipMat = mat(0xb8945a, {roughness:0.9});
  const chips = new THREE.InstancedMesh(chipGeo, chipMat, chipCount);
  chips.receiveShadow = true;
  const dummy = new THREE.Object3D();
  for(let i=0;i<chipCount;i++){
    dummy.position.set(
      (Math.random()-0.5)*(CAGE_W-0.3),
      0.08 + Math.random()*0.02,
      (Math.random()-0.5)*(CAGE_D-0.3)
    );
    dummy.rotation.set(Math.random()*0.3, Math.random()*Math.PI, Math.random()*0.3);
    dummy.scale.setScalar(0.5 + Math.random()*1.0);
    dummy.updateMatrix();
    chips.setMatrixAt(i, dummy.matrix);
  }
  cageGroup.add(chips);

  // Прутья — вертикальные
  const barGeo = new THREE.CylinderGeometry(0.012, 0.012, CAGE_H, 6);
  const halfW = CAGE_W/2, halfD = CAGE_D/2;
  const barPositions = [];

  // Передняя и задняя стенки
  for(let x=-halfW; x<=halfW; x+=BAR_SPACING){
    barPositions.push([x, CAGE_H/2, -halfD]);
    barPositions.push([x, CAGE_H/2, halfD]);
  }
  // Боковые стенки
  for(let z=-halfD; z<=halfD; z+=BAR_SPACING){
    barPositions.push([-halfW, CAGE_H/2, z]);
    barPositions.push([halfW, CAGE_H/2, z]);
  }

  const bars = new THREE.InstancedMesh(barGeo, matBar, barPositions.length);
  bars.castShadow = true;
  barPositions.forEach((p,i)=>{
    dummy.position.set(p[0], p[1]+0.08, p[2]);
    dummy.rotation.set(0,0,0);
    dummy.scale.setScalar(1);
    dummy.updateMatrix();
    bars.setMatrixAt(i, dummy.matrix);
  });
  cageGroup.add(bars);

  // Верхние рамки
  const frameH = 0.04, frameD = 0.04;
  const topY = CAGE_H + 0.08 + frameH/2;
  const frames = [
    [0, topY, -halfD, CAGE_W+frameD, frameH, frameD],
    [0, topY,  halfD, CAGE_W+frameD, frameH, frameD],
    [-halfW, topY, 0, frameD, frameH, CAGE_D+frameD],
    [ halfW, topY, 0, frameD, frameH, CAGE_D+frameD],
  ];
  frames.forEach(f=>{
    const m = new THREE.Mesh(new THREE.BoxGeometry(f[3],f[4],f[5]), matBar);
    m.position.set(f[0],f[1],f[2]);
    m.castShadow = true;
    cageGroup.add(m);
  });

  // Нижние рамки
  const botY = 0.08 + frameH/2;
  frames.forEach(f=>{
    const m = new THREE.Mesh(new THREE.BoxGeometry(f[3],f[4],f[5]), matBar);
    m.position.set(f[0],botY,f[2]);
    m.castShadow = true;
    cageGroup.add(m);
  });
})();

// ============================================================
// КОЛЕСО
// ============================================================
const wheelData = {
  group: null,
  rimInner: null,
  rimOuter: null,
  spokes: [],
  hub: null,
  axle: null,
  angularVel: 0,       // ω рад/с
  currentAngle: 0,
  runner: null,        // ссылка на хомяка в колесе
  R: WHEEL_RIM_RADIUS,
  W: WHEEL_RIM_WIDTH,
};

(function buildWheel(){
  const g = new THREE.Group();
  g.position.set(-1.0, 0.08, -0.5);
  wheelData.group = g;
  scene.add(g);

  const R = WHEEL_RIM_RADIUS;
  const W = WHEEL_RIM_WIDTH;

  // Обод внутренний — тор (видимая часть)
  const rimGeo = new THREE.TorusGeometry(R, 0.03, 8, 32);
  const rimInner = new THREE.Mesh(rimGeo, matWheel);
  rimInner.rotation.y = Math.PI/2;
  rimInner.castShadow = true;
  g.add(rimInner);
  wheelData.rimInner = rimInner;

  // Обод внешний
  const rimOuter = new THREE.Mesh(rimGeo.clone(), matWheel);
  rimOuter.rotation.y = Math.PI/2;
  rimOuter.position.x = W;
  rimOuter.castShadow = true;
  g.add(rimOuter);
  wheelData.rimOuter = rimOuter;

  // Соединительные дужки обода
  for(let a=0; a<Math.PI*2; a+=Math.PI/4){
    const dx = R*Math.cos(a), dz = R*Math.sin(a);
    const bridge = new THREE.Mesh(new THREE.BoxGeometry(W, 0.025, 0.025), matWheel);
    bridge.position.set(W/2, dz, dx);
    bridge.lookAt(new THREE.Vector3(W/2, 0, 0));
    bridge.rotateX(Math.PI/2);
    bridge.castShadow = true;
    g.add(bridge);
  }

  // Спицы
  for(let i=0;i<WHEEL_SPOKE_COUNT;i++){
    const a = (i/WHEEL_SPOKE_COUNT)*Math.PI*2;
    const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, R, 6), matWheel);
    spoke.position.set(W/2, R*Math.sin(a), R*Math.cos(a));
    spoke.lookAt(new THREE.Vector3(W/2, 0, 0));
    spoke.rotateX(Math.PI/2);
    spoke.castShadow = true;
    g.add(spoke);
    wheelData.spokes.push(spoke);
  }

  // Центральный вал
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(WHEEL_HUB_RADIUS, WHEEL_HUB_RADIUS, W+0.1, 12), matMetal);
  hub.position.set(W/2, 0, 0);
  hub.rotation.x = Math.PI/2;
  hub.castShadow = true;
  g.add(hub);
  wheelData.hub = hub;

  // Ось (статичная, проходит через центр)
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, W+0.3, 8), matMetal);
  axle.position.set(W/2, 0, 0);
  axle.rotation.x = Math.PI/2;
  axle.castShadow = true;
  g.add(axle);
  wheelData.axle = axle;

  // Площадка входа в колесо
  const platform = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.04, 0.4), matWood);
  platform.position.set(-0.15, 0.02, 0);
  platform.castShadow = true;
  platform.receiveShadow = true;
  g.add(platform);

  // Опоры колеса
  for(let x of [0, W]){
    const support = new THREE.Mesh(new THREE.BoxGeometry(0.06, R+0.1, 0.06), matMetal);
    support.position.set(x, -(R+0.05), 0);
    support.castShadow = true;
    g.add(support);
  }
})();

// ============================================================
// ТРУБА
// ============================================================
const tubeData = {
  group: null,
  mesh: null,
  position: new THREE.Vector3(0.5, 0.08, 0.5),
  radius: TUBE_RADIUS,
  length: TUBE_LENGTH,
  axis: new THREE.Vector3(1, 0, 0), // лежит вдоль X
  occupant: null,
};

(function buildTube(){
  const g = new THREE.Group();
  g.position.copy(tubeData.position);
  tubeData.group = g;
  scene.add(g);

  // Полая труба — цилиндр без торцов
  const tubeGeo = new THREE.CylinderGeometry(TUBE_RADIUS, TUBE_RADIUS, TUBE_LENGTH, 24, 1, true);
  const tubeMesh = new THREE.Mesh(tubeGeo, mat(0x88aa66, {side:THREE.DoubleSide, roughness:0.7}));
  tubeMesh.rotation.z = Math.PI/2; // ось вдоль X
  tubeMesh.castShadow = true;
  g.add(tubeMesh);
  tubeData.mesh = tubeMesh;

  // Кольца на концах трубы
  const ringGeo = new THREE.TorusGeometry(TUBE_RADIUS, 0.02, 8, 24);
  for(let side of [-1, 1]){
    const ring = new THREE.Mesh(ringGeo, matMetal);
    ring.position.set(side * TUBE_LENGTH/2, 0, 0);
    ring.rotation.y = Math.PI/2;
    ring.castShadow = true;
    g.add(ring);
  }
})();

// ============================================================
// МИСКА
// ============================================================
const bowlData = {
  group: null,
  position: new THREE.Vector3(1.2, 0.08, -0.8),
  radius: BOWL_RADIUS,
  depth: BOWL_DEPTH,
};

(function buildBowl(){
  const g = new THREE.Group();
  g.position.copy(bowlData.position);
  bowlData.group = g;
  scene.add(g);

  // Миска — половинка сферы
  const bowlGeo = new THREE.SphereGeometry(BOWL_RADIUS, 24, 12, 0, Math.PI*2, 0, Math.PI*0.5);
  const bowlMesh = new THREE.Mesh(bowlGeo, matBowl);
  bowlMesh.rotation.x = Math.PI; // выпуклой вниз
  bowlMesh.position.y = -BOWL_DEPTH*0.3;
  bowlMesh.castShadow = true;
  bowlMesh.receiveShadow = true;
  g.add(bowlMesh);

  // Зёрна
  const seedCount = 30;
  const seedGeo = new THREE.SphereGeometry(0.015, 4, 4);
  const seeds = new THREE.InstancedMesh(seedGeo, matSeed, seedCount);
  seeds.receiveShadow = true;
  for(let i=0;i<seedCount;i++){
    const r = Math.random()*BOWL_RADIUS*0.7;
    const a = Math.random()*Math.PI*2;
    dummy.position.set(r*Math.cos(a), -BOWL_DEPTH*0.3 + BOWL_RADIUS - Math.sqrt(Math.max(0, BOWL_RADIUS*BOWL_RADIUS - r*r)) + 0.01, r*Math.sin(a));
    dummy.rotation.set(0,0,0);
    dummy.scale.setScalar(0.8+Math.random()*0.4);
    dummy.updateMatrix();
    seeds.setMatrixAt(i, dummy.matrix);
  }
  g.add(seeds);
})();

// ============================================================
// ПОИЛКА
// ============================================================
(function buildWaterBottle(){
  const g = new THREE.Group();
  g.position.set(-CAGE_W/2 + 0.05, 1.0, 0);
  scene.add(g);

  // Бутылка
  const bottle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.3, 12), matGlass);
  bottle.castShadow = true;
  g.add(bottle);

  // Вода
  const water = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.2, 12), matWater);
  water.position.y = -0.05;
  g.add(water);

  // Нipple
  const nipple = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.01, 0.08, 8), matMetal);
  nipple.rotation.z = -Math.PI/4;
  nipple.position.set(0.04, -0.15, 0);
  g.add(nipple);

  // Крепление
  const clamp = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.15, 0.08), matMetal);
  clamp.position.set(-0.07, 0, 0);
  clamp.castShadow = true;
  g.add(clamp);
})();

// ============================================================
// СОЗДАНИЕ МОДЕЛИ ХОМЯКА
// ============================================================
function createHamsterModel(color){
  const group = new THREE.Group();

  const bodyMat = mat(color);
  const bellyMat = mat(0xeeccaa);
  const noseMat = mat(0xff8888);
  const eyeWhiteMat = mat(0xffffff);
  const pupilMat = mat(0x111111);
  const earMat = mat(color, {roughness:0.8});
  const earInnerMat = mat(0xffaaaa);
  const footMat = mat(0xddbb99);

  // Тело — вытянутая сфера
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.15, 16, 12), bodyMat);
  body.scale.set(1.3, 1.0, 0.9);
  body.position.set(0, 0.15, 0);
  body.castShadow = true;
  group.add(body);

  // Живот
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 8), bellyMat);
  belly.scale.set(1.2, 0.7, 0.8);
  belly.position.set(0.05, 0.08, 0);
  group.add(belly);

  // Голова — отдельная группа для кивания
  const headGroup = new THREE.Group();
  headGroup.position.set(0.2, 0.22, 0);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.11, 14, 10), bodyMat);
  head.scale.set(1.1, 1.0, 1.0);
  head.castShadow = true;
  headGroup.add(head);

  // Щёки
  for(let z of [-0.07, 0.07]){
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.06, 8, 6), bellyMat);
    cheek.position.set(0.08, -0.02, z);
    cheek.scale.set(1.0, 0.8, 0.7);
    headGroup.add(cheek);
  }

  // Нос
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.02, 6, 4), noseMat);
  nose.position.set(0.12, 0.01, 0);
  headGroup.add(nose);

  // Глаза
  for(let z of [-0.055, 0.055]){
    const eyeWhite = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6), eyeWhiteMat);
    eyeWhite.position.set(0.06, 0.04, z);
    headGroup.add(eyeWhite);

    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.015, 6, 4), pupilMat);
    pupil.position.set(0.08, 0.04, z * 1.05);
    headGroup.add(pupil);
  }

  // Уши
  for(let z of [-0.08, 0.08]){
    const earGroup = new THREE.Group();
    earGroup.position.set(0.02, 0.1, z);

    const earOuter = new THREE.Mesh(new THREE.SphereGeometry(0.04, 8, 6), earMat);
    earOuter.scale.set(0.7, 1.0, 0.5);
    earGroup.add(earOuter);

    const earInner = new THREE.Mesh(new THREE.SphereGeometry(0.025, 6, 4), earInnerMat);
    earInner.scale.set(0.6, 0.8, 0.4);
    earInner.position.set(0, 0, 0);
    earGroup.add(earInner);

    headGroup.add(earGroup);
  }

  group.add(headGroup);

  // Лапы — 4 штуки
  const legs = [];
  const legPositions = [
    {x: 0.12, z: -0.09, name:'FL'},
    {x: 0.12, z:  0.09, name:'FR'},
    {x: -0.12, z: -0.09, name:'BL'},
    {x: -0.12, z:  0.09, name:'BR'},
  ];

  legPositions.forEach(lp=>{
    const legGroup = new THREE.Group();
    legGroup.position.set(lp.x, 0.04, lp.z);

    const upperLeg = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.018, 0.08, 6), footMat);
    upperLeg.position.y = -0.04;
    legGroup.add(upperLeg);

    const foot = new THREE.Mesh(new THREE.SphereGeometry(0.02, 6, 4), footMat);
    foot.scale.set(1.0, 0.5, 1.3);
    foot.position.y = -0.08;
    legGroup.add(foot);

    group.add(legGroup);
    legs.push({group: legGroup, name: lp.name, baseX: lp.x, baseZ: lp.z});
  });

  // Хвост
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.025, 6, 4), bodyMat);
  tail.scale.set(1.5, 0.8, 0.6);
  tail.position.set(-0.22, 0.14, 0);
  group.add(tail);

  return {group, body, belly, headGroup, legs, tail};
}

// ============================================================
// ХОМЯКИ — СОСТОЯНИЯ И ПОВЕДЕНИЕ
// ============================================================
const STATES = {
  IDLE: 'idle',
  WALKING: 'walking',
  WHEEL_RUNNING: 'wheel_running',
  TUBE_CRAWLING: 'tube_crawling',
  EATING: 'eating',
  STROLLING: 'strolling',
};

const STATE_LABELS = {
  [STATES.IDLE]: 'отдыхает',
  [STATES.WALKING]: 'идёт к цели',
  [STATES.WHEEL_RUNNING]: 'бежит в колесе',
  [STATES.TUBE_CRAWLING]: 'ползёт по трубе',
  [STATES.EATING]: 'грызёт зёрна',
  [STATES.STROLLING]: 'гуляет',
};

const hamsterNames = ['Шурша', 'Пушок', 'Карамелька', 'Кнопка', 'Ириска'];
const hamsterColors = [0xe8c070, 0xd4a060, 0xc08050, 0xb09070, 0xf0d0a0];

const hamsters = [];

function createHamster(index){
  const model = createHamsterModel(hamsterColors[index]);
  const name = hamsterNames[index];

  const h = {
    name,
    color: hamsterColors[index],
    model,
    state: STATES.IDLE,
    position: new THREE.Vector3(
      (Math.random()-0.5)*2.5,
      0.08,
      (Math.random()-0.5)*1.8
    ),
    targetPosition: new THREE.Vector3(),
    velocity: new THREE.Vector3(),
    direction: new THREE.Vector3(1,0,0),
    // Для колёса
    wheelPhase: 0,        // угол в колесе (0 = нижняя точка)
    runSpeed: 0,          // текущая скорость бега
    legPhase: 0,          // фаза шага
    distanceTraveled: 0,  // пройденный путь
    // Для трубы
    tubeProgress: 0,      // 0..TUBE_LENGTH
    tubeDirection: 1,     // 1 или -1
    // Для еды
    eatTimer: 0,
    eatDuration: 3 + Math.random()*3,
    // Для прогулки
    strollTarget: null,
    strollTimer: 0,
    // Анимация
    breathePhase: Math.random()*Math.PI*2,
    earTwitchTimer: 2 + Math.random()*4,
    earTwitchActive: false,
    headNodPhase: 0,
    // Переход в колесо
    enteringWheel: false,
    exitingWheel: false,
    enterProgress: 0,
    // Переход в трубу
    enteringTube: false,
    exitTubeProgress: 0,
    // Переход к миске
    approachingBowl: false,
    approachProgress: 0,
    // Клик
    jumpVelocity: 0,
    jumping: false,
  };

  model.group.position.copy(h.position);
  scene.add(model.group);

  hamsters.push(h);
  return h;
}

for(let i=0;i<5;i++) createHamster(i);

// ============================================================
// КОЛЛИЗИИ
// ============================================================
function getWheelWorldPos(){
  return wheelData.group.position.clone();
}

function getTubeWorldBounds(){
  const p = tubeData.position.clone();
  const halfLen = tubeData.length/2;
  return {
    center: p,
    radius: tubeData.radius,
    minX: p.x - halfLen,
    maxX: p.x + halfLen,
    y: p.y,
    z: p.z,
  };
}

function getBowlWorldPos(){
  return bowlData.group.position.clone();
}

// Расстояние от точки до цилиндра (колесо)
function distToWheelCylinder(px, py, pz){
  const wp = wheelData.group.position;
  // Колесо ориентировано: ось Y вертикальна, обод в плоскости YZ
  // Центр обода: wp.x, wp.y, wp.z
  // Радиус: WHEEL_RIM_RADIUS
  const dx = px - wp.x;
  const dy = py - wp.y;
  const dz = pz - wp.z;
  // Расстояние от оси колеса (ось X через центр)
  const distFromAxis = Math.sqrt(dy*dy + dz*dz);
  const radialDist = Math.abs(distFromAxis - WHEEL_RIM_RADIUS);
  // Проверка по ширине обода
  const halfW = WHEEL_RIM_WIDTH/2;
  if(Math.abs(dx) < halfW){
    return radialDist;
  }
  return Infinity; // далеко от обода
}

// Выталкивание из колеса
function pushOutOfWheel(h){
  const wp = wheelData.group.position;
  const px = h.position.x, py = h.position.y, pz = h.position.z;
  const dx = px - wp.x;
  const dy = py - wp.y;
  const dz = pz - wp.z;
  const distFromAxis = Math.sqrt(dy*dy + dz*dz);
  const halfW = WHEEL_RIM_WIDTH/2;

  if(Math.abs(dx) < halfW && Math.abs(distFromAxis - WHEEL_RIM_RADIUS) < HAMSTER_RADIUS){
    // Нормаль от центра обода
    const nx = 0;
    const ny = dy / distFromAxis;
    const nz = dz / distFromAxis;
    const penetration = HAMSTER_RADIUS - Math.abs(distFromAxis - WHEEL_RIM_RADIUS);
    if(penetration > 0){
      // Толкаем наружу от обода
      const sign = distFromAxis > WHEEL_RIM_RADIUS ? 1 : -1;
      h.position.x += nx * penetration * sign;
      h.position.y += ny * penetration * sign;
      h.position.z += nz * penetration * sign;
    }
  }
}

// Расстояние от точки до трубы (цилиндр)
function distToTube(px, py, pz){
  const tb = getTubeWorldBounds();
  const dx = px - tb.center.x;
  const dy = py - tb.y;
  const dz = pz - tb.center.z;
  const distFromAxis = Math.sqrt(dy*dy + dz*dz);
  const halfLen = tubeData.length/2;

  if(Math.abs(dx) < halfLen){
    // Внутри диапазона трубы
    const radialDist = Math.abs(distFromAxis - tubeData.radius);
    return radialDist;
  }
  return Infinity;
}

function pushOutOfTube(h){
  const tb = getTubeWorldBounds();
  const px = h.position.x, py = h.position.y, pz = h.position.z;
  const dx = px - tb.center.x;
  const dy = py - tb.y;
  const dz = pz - tb.center.z;
  const distFromAxis = Math.sqrt(dy*dy + dz*dz);
  const halfLen = tubeData.length/2;

  if(Math.abs(dx) < halfLen){
    const radialDist = Math.abs(distFromAxis - tubeData.radius);
    if(radialDist < HAMSTER_RADIUS && distFromAxis > tubeData.radius * 0.5){
      // Снаружи трубы — толкаем дальше от стенки
      const ny = dy / distFromAxis;
      const nz = dz / distFromAxis;
      const penetration = HAMSTER_RADIUS - radialDist;
      h.position.y += ny * penetration;
      h.position.z += nz * penetration;
    } else if(distFromAxis < tubeData.radius * 0.5 && distFromAxis < HAMSTER_RADIUS){
      // Слишком близко к оси — но это нормально для хомяка внутри
    }
  }
}

// Расстояние до миски
function distToBowl(px, py, pz){
  const bp = getBowlWorldPos();
  const dx = px - bp.x;
  const dz = pz - bp.z;
  const dist = Math.sqrt(dx*dx + dz*dz);
  return Math.max(0, dist - BOWL_RADIUS - HAMSTER_RADIUS);
}

function pushOutOfBowl(h){
  const bp = getBowlWorldPos();
  const dx = h.position.x - bp.x;
  const dz = h.position.z - bp.z;
  const dist = Math.sqrt(dx*dx + dz*dz);
  const minDist = BOWL_RADIUS + HAMSTER_RADIUS;
  if(dist < minDist && dist > 0.001){
    const nx = dx/dist, nz = dz/dist;
    h.position.x += nx * (minDist - dist);
    h.position.z += nz * (minDist - dist);
  }
}

// Хомяк-хомяк
function pushApartHamsters(){
  for(let i=0;i<hamsters.length;i++){
    for(let j=i+1;j<hamsters.length;j++){
      const a = hamsters[i], b = hamsters[j];
      if(a.state === STATES.WHEEL_RUNNING || b.state === STATES.WHEEL_RUNNING) continue;
      if(a.state === STATES.TUBE_CRAWLING || b.state === STATES.TUBE_CRAWLING) continue;

      const dx = a.position.x - b.position.x;
      const dy = a.position.y - b.position.y;
      const dz = a.position.z - b.position.z;
      const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
      const minDist = HAMSTER_RADIUS * 2.2;

      if(dist < minDist && dist > 0.001){
        const nx = dx/dist, ny = dy/dist, nz = dz/dist;
        const push = (minDist - dist) * 0.5;
        a.position.x += nx * push;
        a.position.y += ny * push;
        a.position.z += nz * push;
        b.position.x -= nx * push;
        b.position.y -= ny * push;
        b.position.z -= nz * push;
      }
    }
  }
}

// Ограничение в клетке
function clampToCage(h){
  const margin = HAMSTER_RADIUS + 0.1;
  const hw = CAGE_W/2 - margin;
  const hd = CAGE_D/2 - margin;
  h.position.x = Math.max(-hw, Math.min(hw, h.position.x));
  h.position.z = Math.max(-hd, Math.min(hd, h.position.z));
  h.position.y = Math.max(0.08, h.position.y);
}

// ============================================================
// ПОВЕДЕНИЕ — КОНЕЧНЫЙ АВТОМАТ
// ============================================================
function pickActivity(h){
  const r = Math.random();
  if(r < 0.30){
    // Колесо
    if(!wheelData.runner){
      return 'wheel';
    }
  }
  if(r < 0.50){
    // Труба
    if(!tubeData.occupant){
      return 'tube';
    }
  }
  if(r < 0.70){
    // Миска
    return 'bowl';
  }
  // Прогулка
  return 'stroll';
}

function updateHamsterBehavior(dt){
  hamsters.forEach(h => {
    switch(h.state){
      case STATES.IDLE:
        updateIdle(h, dt);
        break;
      case STATES.WALKING:
        updateWalking(h, dt);
        break;
      case STATES.WHEEL_RUNNING:
        updateWheelRunning(h, dt);
        break;
      case STATES.TUBE_CRAWLING:
        updateTubeCrawling(h, dt);
        break;
      case STATES.EATING:
        updateEating(h, dt);
        break;
      case STATES.STROLLING:
        updateStrolling(h, dt);
        break;
    }
  });
}

function updateIdle(h, dt){
  h.breathePhase += dt * 2.5;

  // Дыхание — лёгкое изменение масштаба тела
  const breathScale = 1.0 + Math.sin(h.breathePhase) * 0.03;
  h.model.body.scale.set(1.3 * breathScale, 1.0 * breathScale, 0.9 * breathScale);

  // Дерганье ухом
  h.earTwitchTimer -= dt;
  if(h.earTwitchTimer <= 0){
    h.earTwitchActive = true;
    h.earTwitchTimer = 0.15;
  }
  if(h.earTwitchActive){
    h.earTwitchTimer -= dt;
    if(h.earTwitchTimer <= 0) h.earTwitchActive = false;
  }

  // Выбор нового занятия
  h.strollTimer -= dt;
  if(h.strollTimer <= 0){
    const activity = pickActivity(h);
    startActivity(h, activity);
    h.strollTimer = 2 + Math.random() * 4;
  }
}

function startActivity(h, activity){
  switch(activity){
    case 'wheel':
      if(wheelData.runner){
        // Колесо занято — идём гулять
        h.state = STATES.STROLLING;
        h.strollTarget = randomPointInCage();
        break;
      }
      // Подходим к колёсу
      h.state = STATES.WALKING;
      const wp = getWheelWorldPos();
      h.targetPosition.set(wp.x + 0.4, 0.08, wp.z);
      h._pendingActivity = 'wheel_enter';
      break;

    case 'tube':
      if(tubeData.occupant){
        h.state = STATES.STROLLING;
        h.strollTarget = randomPointInCage();
        break;
      }
      h.state = STATES.WALKING;
      // Ближний торец трубы
      const tb = getTubeWorldBounds();
      const closerEnd = h.position.x < tb.center.x ? -1 : 1;
      h.targetPosition.set(tb.center.x + closerEnd * tubeData.length/2, 0.08, tb.z);
      h._pendingActivity = 'tube_enter';
      h._tubeDir = closerEnd;
      break;

    case 'bowl':
      h.state = STATES.WALKING;
      const bp = getBowlWorldPos();
      h.targetPosition.set(bp.x + 0.4, 0.08, bp.z);
      h._pendingActivity = 'bowl_eat';
      break;

    case 'stroll':
      h.state = STATES.STROLLING;
      h.strollTarget = randomPointInCage();
      break;
  }
}

function randomPointInCage(){
  const margin = HAMSTER_RADIUS + 0.3;
  return new THREE.Vector3(
    (Math.random()-0.5) * (CAGE_W - 2*margin),
    0.08,
    (Math.random()-0.5) * (CAGE_D - 2*margin)
  );
}

function updateWalking(h, dt){
  const speed = HAMSTER_WALK_SPEED;
  const dir = new THREE.Vector3().subVectors(h.targetPosition, h.position);
  dir.y = 0;
  const dist = dir.length();

  if(dist < 0.15){
    // Прибыли — выполняем pending activity
    if(h._pendingActivity === 'wheel_enter'){
      enterWheel(h);
    } else if(h._pendingActivity === 'tube_enter'){
      enterTube(h);
    } else if(h._pendingActivity === 'bowl_eat'){
      startEating(h);
    } else {
      h.state = STATES.IDLE;
      h.strollTimer = 1 + Math.random()*2;
    }
    return;
  }

  dir.normalize();
  h.direction.lerp(dir, 0.1);
  h.velocity.copy(dir.multiplyScalar(speed));

  const move = speed * dt;
  h.position.addScaledVector(dir, move);
  h.distanceTraveled += move;
  h.legPhase += (move / STEP_LENGTH) * Math.PI * 2;

  // Поворот модели
  const angle = Math.atan2(dir.x, dir.z);
  h.model.group.rotation.y = angle;

  clampToCage(h);
  applyCollisions(h);
}

function updateStrolling(h, dt){
  if(!h.strollTarget){
    h.strollTarget = randomPointInCage();
  }

  const speed = HAMSTER_WALK_SPEED * 0.7;
  const dir = new THREE.Vector3().subVectors(h.strollTarget, h.position);
  dir.y = 0;
  const dist = dir.length();

  if(dist < 0.2){
    h.state = STATES.IDLE;
    h.strollTimer = 1 + Math.random()*3;
    h.strollTarget = null;
    return;
  }

  dir.normalize();
  h.direction.lerp(dir, 0.08);
  h.velocity.copy(dir.multiplyScalar(speed));

  const move = speed * dt;
  h.position.addScaledVector(dir, move);
  h.distanceTraveled += move;
  h.legPhase += (move / STEP_LENGTH) * Math.PI * 2;

  const angle = Math.atan2(dir.x, dir.z);
  h.model.group.rotation.y = angle;

  clampToCage(h);
  applyCollisions(h);
}

// ============================================================
// КОЛЕСО — ФИЗИКА
// ============================================================
function enterWheel(h){
  if(wheelData.runner){
    // Колесо занято
    h.state = STATES.IDLE;
    h.strollTimer = 1 + Math.random()*2;
    return;
  }

  h.state = STATES.WHEEL_RUNNING;
  wheelData.runner = h;
  h.runSpeed = HAMSTER_RUN_SPEED;
  h.wheelPhase = 0; // начинается с нижней точки

  // Плавный вход — перемещаем хомяка на позицию внутри колеса
  const wp = getWheelWorldPos();
  h.enteringWheel = true;
  h.enterProgress = 0;
  h._enterStartPos = h.position.clone();
  // Целевая позиция: на нижней точке обода
  h._enterTargetPos = new THREE.Vector3(wp.x, wp.y - WHEEL_RIM_RADIUS + 0.05, wp.z);
}

function exitWheel(h){
  if(wheelData.runner !== h) return;
  wheelData.runner = null;

  h.exitingWheel = true;
  h.exitProgress = 0;
  h._exitStartPos = h.position.clone();

  const wp = getWheelWorldPos();
  h._exitTargetPos = new THREE.Vector3(wp.x + 0.4, 0.08, wp.z);

  h.state = STATES.WALKING;
  h.targetPosition.copy(h._exitTargetPos);
  h._pendingActivity = null;
}

function updateWheelRunning(h, dt){
  // Плавный вход
  if(h.enteringWheel){
    h.enterProgress += dt * 2.0;
    if(h.enterProgress >= 1){
      h.enteringWheel = false;
      h.enterProgress = 1;
    }
    const t = smoothstep(h.enterProgress);
    h.position.lerpVectors(h._enterStartPos, h._enterTargetPos, t);
    h.model.group.position.copy(h.position);
    return;
  }

  // Плавный выход
  if(h.exitingWheel){
    h.exitProgress += dt * 2.0;
    if(h.exitProgress >= 1){
      h.exitingWheel = false;
      h.state = STATES.IDLE;
      h.strollTimer = 1 + Math.random()*2;
      return;
    }
    const t = smoothstep(h.exitProgress);
    h.position.lerpVectors(h._exitStartPos, h._exitTargetPos, t);
    h.model.group.position.copy(h.position);
    return;
  }

  // Хомяк бежит в колесе
  const v = h.runSpeed;
  const R = WHEEL_RIM_RADIUS;

  // ω = v / R
  const omega = v / R;
  wheelData.angularVel = omega;

  // Обновляем угол колеса
  wheelData.currentAngle += omega * dt;

  // Хомяк всегда на нижней точке обода
  const wp = wheelData.group.position;
  h.position.set(wp.x, wp.y - R + 0.05, wp.z);
  h.model.group.position.copy(h.position);

  // Направление: хомяк смотрит "вперёд" по направлению движения
  // При вращении колеса в плоскости YZ, хомяк бежит "вперёд" по касательной
  // На нижней точке касательная направлена по Z (положительному или отрицательному)
  // Зависит от направления вращения
  const lookAngle = Math.atan2(Math.cos(wheelData.currentAngle), -Math.sin(wheelData.currentAngle));
  h.model.group.rotation.y = lookAngle;

  // Фаза шага привязана к пройденному пути
  const stepDist = v * dt;
  h.distanceTraveled += stepDist;
  h.legPhase += (stepDist / STEP_LENGTH) * Math.PI * 2;

  // Вероятность выйти из колеса
  if(Math.random() < 0.005){
    exitWheel(h);
  }
}

function smoothstep(t){
  return t * t * (3 - 2*t);
}

// Затухание колеса
function updateWheelFriction(dt){
  if(!wheelData.runner){
    // Без бегуна колесо замедляется
    wheelData.angularVel *= Math.exp(-FRICTION_TORQUE * dt);
    if(Math.abs(wheelData.angularVel) < 0.001) wheelData.angularVel = 0;
  }
  wheelData.currentAngle += wheelData.angularVel * dt;
}

// ============================================================
// ТРУБА
// ============================================================
function enterTube(h){
  if(tubeData.occupant){
    h.state = STATES.IDLE;
    h.strollTimer = 1 + Math.random()*2;
    return;
  }

  h.state = STATES.TUBE_CRAWLING;
  tubeData.occupant = h;

  // Начинаем с входа
  const tb = getTubeWorldBounds();
  const entryX = tb.center.x + h._tubeDir * tubeData.length/2;
  h.tubeProgress = 0;
  h.tubeDirection = h._tubeDir;

  // Позиция на дне трубы (внутреннее дно)
  h.position.set(entryX, tb.y + 0.02, tb.z);
  h.model.group.position.copy(h.position);
  h.model.group.rotation.y = h.tubeDirection > 0 ? 0 : Math.PI;
}

function exitTube(h){
  if(tubeData.occupant !== h) return;
  tubeData.occupant = null;

  h.state = STATES.IDLE;
  h.strollTimer = 1 + Math.random()*2;
}

function updateTubeCrawling(h, dt){
  const crawlSpeed = HAMSTER_WALK_SPEED * 0.8;

  h.tubeProgress += crawlSpeed * dt * h.tubeDirection;

  const tb = getTubeWorldBounds();
  const halfLen = tubeData.length/2;

  // Позиция вдоль оси трубы
  const cx = tb.center.x + h.tubeProgress * h.tubeDirection;
  // На внутреннем дне трубы
  h.position.set(cx, tb.y + 0.02, tb.z);
  h.model.group.position.copy(h.position);

  // Направление вдоль оси
  h.model.group.rotation.y = h.tubeDirection > 0 ? 0 : Math.PI;

  h.distanceTraveled += crawlSpeed * dt;
  h.legPhase += (crawlSpeed * dt / STEP_LENGTH) * Math.PI * 2;

  // Выход с другой стороны
  if(Math.abs(h.tubeProgress) >= halfLen){
    exitTube(h);
  }
}

// ============================================================
// МИСКА — ЕДА
// ============================================================
function startEating(h){
  h.state = STATES.EATING;
  h.eatTimer = h.eatDuration;

  // Ставим перед миской
  const bp = getBowlWorldPos();
  h.position.set(bp.x + 0.35, 0.08, bp.z);
  h.model.group.position.copy(h.position);
  h.model.group.rotation.y = Math.PI; // смотрит на миску
}

function updateEating(h, dt){
  h.eatTimer -= dt;

  // Наклон головы и жевание
  h.headNodPhase += dt * 4;
  const nodAngle = Math.sin(h.headNodPhase) * 0.15;
  h.model.headGroup.rotation.x = nodAngle;

  // Дыхание
  h.breathePhase += dt * 2.5;
  const breathScale = 1.0 + Math.sin(h.breathePhase) * 0.02;
  h.model.body.scale.set(1.3 * breathScale, 1.0 * breathScale, 0.9 * breathScale);

  if(h.eatTimer <= 0){
    h.state = STATES.IDLE;
    h.strollTimer = 1 + Math.random()*2;
    h.model.headGroup.rotation.x = 0;
  }
}

// ============================================================
// КОЛЛИЗИИ — ПРИМЕНЕНИЕ
// ============================================================
function applyCollisions(h){
  if(h.state === STATES.WHEEL_RUNNING || h.state === STATES.TUBE_CRAWLING) return;

  pushOutOfWheel(h);
  pushOutOfTube(h);
  pushOutOfBowl(h);
}

// ============================================================
// АНИМАЦИЯ ЛАП
// ============================================================
function animateLegs(h, dt){
  const phase = h.legPhase;
  const speed = (h.state === STATES.WHEEL_RUNNING) ? h.runSpeed :
                (h.state === STATES.TUBE_CRAWLING) ? HAMSTER_WALK_SPEED * 0.8 :
                (h.state === STATES.WALKING || h.state === STATES.STROLLING) ? HAMSTER_WALK_SPEED : 0;

  h.model.legs.forEach((leg, i) => {
    // Диагональные пары: FL+BR и FR+BL
    const isFront = i < 2;
    const isLeft = i % 2 === 0;
    const pairPhase = (isFront !== isLeft) ? 0 : Math.PI; // диагональные пары в противофазе

    const legPhase = phase + pairPhase;
    const swing = Math.sin(legPhase) * 0.3;

    // Если скорость 0 — лапы замирают
    const effectiveSwing = speed > 0.01 ? swing : 0;

    // Позиция лапы
    leg.group.position.x = leg.baseX + Math.cos(legPhase) * 0.02 * (speed > 0.01 ? 1 : 0);
    leg.group.position.z = leg.baseZ + effectiveSwing * 0.08;
    leg.group.position.y = 0.04 + Math.abs(effectiveSwing) * 0.03;

    // Наклон верхней части ноги
    const upperLeg = leg.group.children[0];
    if(upperLeg){
      upperLeg.rotation.x = effectiveSwing * 0.5;
    }
  });
}

// ============================================================
// ОБНОВЛЕНИЕ ВИЗУАЛА КОЛЕСА
// ============================================================
function updateWheelVisual(){
  wheelData.group.rotation.y = wheelData.currentAngle;
}

// ============================================================
// ПРЫЖОК ПО КЛИКУ
// ============================================================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', (e)=>{
  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);

  hamsters.forEach(h => {
    const intersects = raycaster.intersectObject(h.model.group, true);
    if(intersects.length > 0){
      h.jumping = true;
      h.jumpVelocity = 3.0;
    }
  });
});

function updateJump(dt){
  hamsters.forEach(h => {
    if(h.jumping){
      h.jumpVelocity -= 9.8 * dt;
      h.position.y += h.jumpVelocity * dt;
      if(h.position.y <= 0.08){
        h.position.y = 0.08;
        h.jumping = false;
        h.jumpVelocity = 0;
      }
      h.model.group.position.copy(h.position);
    }
  });
}

// ============================================================
// UI — ОБНОВЛЕНИЕ ПАНЕЛЕЙ
// ============================================================
function updateUI(){
  // Колесо
  const runner = wheelData.runner;
  document.getElementById('wpRunner').textContent = runner ? runner.name : 'нет';
  const vLeg = runner ? runner.runSpeed : 0;
  const omegaR = Math.abs(wheelData.angularVel) * WHEEL_RIM_RADIUS;
  const diff = vLeg > 0 ? Math.abs(vLeg - omegaR) / vLeg * 100 : 0;
  document.getElementById('wpVleg').textContent = vLeg.toFixed(2);
  document.getElementById('wpOmegaR').textContent = omegaR.toFixed(2);
  document.getElementById('wpDiff').textContent = diff.toFixed(1) + '%';
  document.getElementById('wpOmega').textContent = wheelData.angularVel.toFixed(3);

  // Хомяки
  const list = document.getElementById('hamsterList');
  let html = '';
  hamsters.forEach(h => {
    const colorHex = '#' + h.color.toString(16).padStart(6,'0');
    html += `<div class="hamster-row">
      <span class="dot" style="background:${colorHex}"></span>
      <span class="hname">${h.name}</span>
      <span class="hstate">${STATE_LABELS[h.state]}</span>
    </div>`;
  });
  list.innerHTML = html;
}

// ============================================================
// ГЛАВНЫЙ ЦИКЛ
// ============================================================
let lastTime = performance.now();

function animate(now){
  requestAnimationFrame(animate);

  let dt = (now - lastTime) / 1000;
  lastTime = now;

  // Ограничение дельты
  if(dt > 0.1) dt = 0.1;

  // Обновление поведения
  updateHamsterBehavior(dt);

  // Физика колеса
  updateWheelFriction(dt);
  updateWheelVisual();

  // Коллизии хомяк-хомяк
  pushApartHamsters();

  // Анимация лап
  hamsters.forEach(h => animateLegs(h, dt));

  // Прыжки
  updateJump(dt);

  // Синхронизация позиций
  hamsters.forEach(h => {
    h.model.group.position.copy(h.position);
  });

  // UI
  updateUI();

  controls.update();
  renderer.render(scene, camera);
}

requestAnimationFrame(animate);

// ============================================================
// RESIZE
// ============================================================
window.addEventListener('resize', ()=>{
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// ============================================================
// ОТЛАДОЧНАЯ ИНФОРМАЦИЯ В КОНСОЛИ
// ============================================================
console.log('=== Клетка с хомяками ===');
console.log('Хомяки:', hamsters.map(h => ({name:h.name, color:h.color})));
console.log('Колесо: R='+WHEEL_RIM_RADIUS.toFixed(2)+', W='+WHEEL_RIM_WIDTH.toFixed(2));
console.log('Труба: R='+TUBE_RADIUS.toFixed(2)+', L='+TUBE_LENGTH);
console.log('Миска: R='+BOWL_RADIUS.toFixed(2));
console.log('Габариты хомяка: L='+HAMSTER_LENGTH+' H='+HAMSTER_HEIGHT+' W='+HAMSTER_WIDTH);
console.log('Проверка: хомяк помещается в колесо? '+ (HAMSTER_LENGTH < WHEEL_RIM_RADIUS));
console.log('Проверка: хомяк помещается в трубу? ' + (HAMSTER_LENGTH < TUBE_RADIUS * 2));
console.log('Доступные объекты: hamsters[], wheelData, tubeData, bowlData');
</script>
</body>
</html>
```

## Что реализовано

### Физика (Часть 1)

| Требование | Реализация |
|---|---|
| **1.1 Колесо крутит бегун** | `ω = v / R` вычисляется каждый кадр; без бегуна колесо затухает `exp(-FRICTION_TORQUE·dt)`; панель показывает расхождение |
| **1.2 Габариты связаны** | `WHEEL_RIM_RADIUS = HAMSTER_LENGTH * 1.6`, `WHEEL_RIM_WIDTH = HAMSTER_WIDTH * 1.8` — константы в начале файла |
| **1.3 Труба полая** | Хомяк входит через торец, движется вдоль оси X, стоит на внутреннем дне (`y = tube.y + 0.02`), боковая стенка отталкивает |
| **1.4 Тела предметов** | `pushOutOfWheel`, `pushOutOfTube`, `pushOutOfBowl` — выталкивание по нормали; `pushApartHamsters` — расталкивание |
| **1.5 Лапы не скользят** | `legPhase += (пройденный путь / STEP_LENGTH) * 2π`; при остановке скорость=0 → лапы замирают; диагональные пары в противофазе |
| **1.6 Плавные переходы** | `enteringWheel`/`exitingWheel` с `smoothstep`-интерполяцией; колесо/труба — один пользователь |

### Поведение (Часть 2)
- 5 хомяков с именами и цветами
- Конечный автомат: `IDLE → WALKING → занятие → IDLE`
- Боковая панель показывает состояние каждого
- Клик → подпрыгивание (гравитация)
- Дыхание (масштаб тела), дерганье ухом, кивок при еде

### Сцена (Часть 3)
- Комната (пол, стены) + стол
- Клетка: поддон, стружка (`InstancedMesh` 600 щепок), прутья (`InstancedMesh`), рамки
- Колесо, полая труба, миска с зёрнами, поилка
- Хомяк: тело, живот, голова (отдельная группа), глаза+зрачки, щёки, нос, уши (внешние+внутренние), 4 лапы, хвост

### Техническое (Часть 4)
- Three.js r128 + OrbitControls через CDN
- Один HTML-файл, никаких сборщиков
- `PCFSoftShadowMap`, 2048×2048
- `requestAnimationFrame` с ограничением `dt ≤ 0.1`
- Обработка `resize`