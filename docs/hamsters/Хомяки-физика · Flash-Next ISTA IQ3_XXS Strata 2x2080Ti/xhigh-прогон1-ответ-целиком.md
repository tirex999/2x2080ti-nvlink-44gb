Ниже — один самодостаточный HTML-файл. Физика сделана «честной»: колесо крутится от скорости бега хомяка, радиус колеса вычисляется из габарита зверя, труба проходится только через торцы и вдоль оси, предметы имеют формы столкновения, фаза шага считается от пройденного пути, переходы в колесо/трубу плавные.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>3D клетка с хомяками — честная физика</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #101318;
    font-family: "Segoe UI", Arial, sans-serif;
    color: #e8eef6;
  }
  canvas { display: block; }

  #panel {
    position: fixed;
    left: 14px;
    top: 14px;
    width: 330px;
    background: rgba(12, 16, 22, 0.78);
    border: 1px solid rgba(140, 180, 220, 0.22);
    border-radius: 12px;
    padding: 12px 14px;
    backdrop-filter: blur(6px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    font-size: 13px;
    line-height: 1.35;
    z-index: 10;
  }
  #panel h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
    color: #9fd0ff;
    letter-spacing: 0.3px;
  }
  #panel .row {
    display: grid;
    grid-template-columns: 12px 64px 1fr 42px;
    gap: 7px;
    align-items: center;
    padding: 3px 0;
  }
  #panel .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.35);
  }
  #panel .state { color: #cfe2f5; }
  #panel .speed { color: #8fb8d8; text-align: right; font-variant-numeric: tabular-nums; }
  #panel .debug {
    margin-top: 10px;
    padding-top: 9px;
    border-top: 1px solid rgba(140, 180, 220, 0.18);
    font-family: ui-monospace, Consolas, monospace;
    font-size: 12px;
    color: #d7e7f5;
    white-space: pre;
  }
  #panel .hint {
    margin-top: 8px;
    color: #8ca7bf;
    font-size: 11px;
  }
</style>
</head>
<body>

<div id="panel">
  <h3>Хомяки</h3>
  <div id="hamsterList"></div>

  <div class="debug" id="wheelDebug"></div>
  <div class="debug" id="tubeDebug"></div>

  <div class="hint">Клик по хомяку — прыжок. Колесо крутится только от бега внутри.</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
/*
  ВАЖНЫЕ ФИЗИЧЕСКИЕ СВЯЗКИ:
  - R колеса считается из габарита хомяка.
  - omega колеса = v_лап / R.
  - фаза шага += (пройденный путь / длина шага) * 2π.
  - труба проходится только через торцы, вдоль оси, на внутреннем дне.
*/

const BED_Y = 0.12;

const HAM = {
  length: 0.62,
  height: 0.42,
  width: 0.44,
  radius: 0.28,
  stride: 0.26,
  walkSpeed: 0.58
};

/* Радиус колеса не подбирается на глаз, а выводится из габарита зверя:
   - зверь должен влезть по высоте;
   - бока не должны касаться обода;
   - длина тела должна помещаться на нижней дуге. */
const WHEEL_R = Math.max(
  HAM.height * 1.35,
  (HAM.height * HAM.height + (HAM.width * 0.5) * (HAM.width * 0.5)) / (2 * HAM.height) + 0.15,
  HAM.length * 0.9
);

const WHEEL_WIDTH = HAM.width * 2.2;
const WHEEL_WALL = 0.06;
const WHEEL_R_OUT = WHEEL_R + WHEEL_WALL;
const WHEEL_AXIS_Y = BED_Y + WHEEL_R + WHEEL_WALL;

const TUBE_R_IN = Math.max(HAM.height * 0.75, HAM.width * 0.82);
const TUBE_WALL = 0.045;
const TUBE_R_OUT = TUBE_R_IN + TUBE_WALL;
const TUBE_X0 = -1.90;
const TUBE_X1 = 0.90;
const TUBE_Z = -1.25;
const TUBE_CENTER_Y = BED_Y + TUBE_R_OUT;
const TUBE_INNER_Y = BED_Y + TUBE_WALL;

const BOWL_R = 0.42;
const BOWL_X = -2.35;
const BOWL_Z = 1.35;

const CAGE = {
  minX: -3.20,
  maxX: 3.20,
  minZ: -2.20,
  maxZ: 2.20,
  height: 2.60
};

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x151a22);
scene.fog = new THREE.Fog(0x151a22, 18, 42);

const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 120);
camera.position.set(7.2, 5.1, 8.4);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.15, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.07;
controls.minDistance = 3.2;
controls.maxDistance = 18;
controls.maxPolarAngle = Math.PI / 2 - 0.03;

/* ------------------------- Свет ------------------------- */

const hemi = new THREE.HemisphereLight(0xbfd4ff, 0x7a6248, 0.55);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff1d6, 1.18);
sun.position.set(6.5, 10.5, 5.5);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 35;
sun.shadow.camera.left = -9;
sun.shadow.camera.right = 9;
sun.shadow.camera.top = 9;
sun.shadow.camera.bottom = -9;
sun.shadow.bias = -0.00045;
scene.add(sun);

const fill = new THREE.DirectionalLight(0x7fa8ff, 0.22);
fill.position.set(-7, 5, -5);
scene.add(fill);

/* ------------------------- Комната и стол ------------------------- */

const roomFloorMat = new THREE.MeshStandardMaterial({ color: 0x394049, roughness: 0.95 });
const roomFloor = new THREE.Mesh(new THREE.PlaneGeometry(44, 44), roomFloorMat);
roomFloor.rotation.x = -Math.PI / 2;
roomFloor.position.y = -2.0;
roomFloor.receiveShadow = true;
scene.add(roomFloor);

const wallMat = new THREE.MeshStandardMaterial({ color: 0x596473, roughness: 0.92 });

const backWall = new THREE.Mesh(new THREE.PlaneGeometry(44, 14), wallMat);
backWall.position.set(0, 5, -11);
backWall.receiveShadow = true;
scene.add(backWall);

const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(44, 14), wallMat);
leftWall.rotation.y = Math.PI / 2;
leftWall.position.set(-11, 5, 0);
leftWall.receiveShadow = true;
scene.add(leftWall);

const rightWall = new THREE.Mesh(new THREE.PlaneGeometry(44, 14), wallMat);
rightWall.rotation.y = -Math.PI / 2;
rightWall.position.set(11, 5, 0);
rightWall.receiveShadow = true;
scene.add(rightWall);

const tableMat = new THREE.MeshStandardMaterial({ color: 0x8b5a33, roughness: 0.78 });
const tableTop = new THREE.Mesh(new THREE.BoxGeometry(9.2, 0.18, 7.2), tableMat);
tableTop.position.set(0, -0.39, 0);
tableTop.castShadow = true;
tableTop.receiveShadow = true;
scene.add(tableTop);

for (let sx of [-1, 1]) {
  for (let sz of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.22, 1.82, 0.22), tableMat);
    leg.position.set(sx * 4.15, -1.10, sz * 3.15);
    leg.castShadow = true;
    leg.receiveShadow = true;
    scene.add(leg);
  }
}

/* ------------------------- Клетка: поддон, прутья, рамки ------------------------- */

const trayMat = new THREE.MeshStandardMaterial({ color: 0x2f6f8f, roughness: 0.55 });
const tray = new THREE.Mesh(
  new THREE.BoxGeometry(CAGE.maxX - CAGE.minX + 0.45, 0.30, CAGE.maxZ - CAGE.minZ + 0.45),
  trayMat
);
tray.position.set(0, -0.15, 0);
tray.castShadow = true;
tray.receiveShadow = true;
scene.add(tray);

const innerFloor = new THREE.Mesh(
  new THREE.PlaneGeometry(CAGE.maxX - CAGE.minX, CAGE.maxZ - CAGE.minZ),
  new THREE.MeshStandardMaterial({ color: 0x8b7355, roughness: 0.95 })
);
innerFloor.rotation.x = -Math.PI / 2;
innerFloor.position.y = 0.001;
innerFloor.receiveShadow = true;
scene.add(innerFloor);

const barMat = new THREE.MeshStandardMaterial({ color: 0xb4bcc4, metalness: 0.65, roughness: 0.35 });
const barGeo = new THREE.CylinderGeometry(0.022, 0.022, CAGE.height, 8);

let barCount = 0;
const barStep = 0.22;
for (let x = CAGE.minX; x <= CAGE.maxX + 1e-6; x += barStep) barCount += 2;
for (let z = CAGE.minZ; z <= CAGE.maxZ + 1e-6; z += barStep) barCount += 2;

const bars = new THREE.InstancedMesh(barGeo, barMat, barCount);
bars.castShadow = true;
bars.receiveShadow = true;

{
  const dummy = new THREE.Object3D();
  let idx = 0;

  for (let x = CAGE.minX; x <= CAGE.maxX + 1e-6; x += barStep) {
    dummy.position.set(x, CAGE.height / 2, CAGE.minZ);
    dummy.rotation.set(0, 0, 0);
    dummy.updateMatrix();
    bars.setMatrixAt(idx++, dummy.matrix);

    dummy.position.set(x, CAGE.height / 2, CAGE.maxZ);
    dummy.updateMatrix();
    bars.setMatrixAt(idx++, dummy.matrix);
  }

  for (let z = CAGE.minZ; z <= CAGE.maxZ + 1e-6; z += barStep) {
    dummy.position.set(CAGE.minX, CAGE.height / 2, z);
    dummy.updateMatrix();
    bars.setMatrixAt(idx++, dummy.matrix);

    dummy.position.set(CAGE.maxX, CAGE.height / 2, z);
    dummy.updateMatrix();
    bars.setMatrixAt(idx++, dummy.matrix);
  }

  bars.instanceMatrix.needsUpdate = true;
}
scene.add(bars);

const frameMat = new THREE.MeshStandardMaterial({ color: 0x9aa4ad, metalness: 0.55, roughness: 0.42 });

function addFrameRail(x, y, z, sx, sy, sz) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), frameMat);
  m.position.set(x, y, z);
  m.castShadow = true;
  m.receiveShadow = true;
  scene.add(m);
}

const cageW = CAGE.maxX - CAGE.minX;
const cageD = CAGE.maxZ - CAGE.minZ;

addFrameRail(0, CAGE.height + 0.04, CAGE.minZ, cageW + 0.18, 0.08, 0.08);
addFrameRail(0, CAGE.height + 0.04, CAGE.maxZ, cageW + 0.18, 0.08, 0.08);
addFrameRail(CAGE.minX, CAGE.height + 0.04, 0, 0.08, 0.08, cageD + 0.18);
addFrameRail(CAGE.maxX, CAGE.height + 0.04, 0, 0.08, 0.08, cageD + 0.18);

addFrameRail(0, 0.04, CAGE.minZ, cageW + 0.18, 0.07, 0.07);
addFrameRail(0, 0.04, CAGE.maxZ, cageW + 0.18, 0.07, 0.07);
addFrameRail(CAGE.minX, 0.04, 0, 0.07, 0.07, cageD + 0.18);
addFrameRail(CAGE.maxX, 0.04, 0, 0.07, 0.07, cageD + 0.18);

/* ------------------------- Подстилка: один InstancedMesh ------------------------- */

const shavingCount = 1700;
const shavingGeo = new THREE.BoxGeometry(0.16, 0.012, 0.038);
const shavingMat = new THREE.MeshStandardMaterial({ color: 0xd8c091, roughness: 0.95 });
const shavings = new THREE.InstancedMesh(shavingGeo, shavingMat, shavingCount);
shavings.receiveShadow = true;

{
  const dummy = new THREE.Object3D();
  for (let i = 0; i < shavingCount; i++) {
    const x = CAGE.minX + Math.random() * (CAGE.maxX - CAGE.minX);
    const z = CAGE.minZ + Math.random() * (CAGE.maxZ - CAGE.minZ);
    const y = 0.025 + Math.random() * 0.095;

    dummy.position.set(x, y, z);
    dummy.rotation.set(
      Math.random() * 0.7 - 0.35,
      Math.random() * Math.PI * 2,
      Math.random() * 0.55 - 0.275
    );
    const s = 0.65 + Math.random() * 0.85;
    dummy.scale.set(s, 0.7 + Math.random() * 0.8, s);
    dummy.updateMatrix();
    shavings.setMatrixAt(i, dummy.matrix);
  }
  shavings.instanceMatrix.needsUpdate = true;
}
scene.add(shavings);

/* ------------------------- Колесо ------------------------- */

const wheel = {
  cx: 2.15,
  cz: 0.25,
  R: WHEEL_R,
  Rout: WHEEL_R_OUT,
  width: WHEEL_WIDTH,
  wall: WHEEL_WALL,
  axisY: WHEEL_AXIS_Y,
  bottomY: WHEEL_AXIS_Y - WHEEL_R,
  angle: 0,
  omega: 0,
  rimSpeed: 0,
  pawSpeed: 0,
  diff: 0,
  user: null,
  bottomPos: new THREE.Vector3(2.15, WHEEL_AXIS_Y - WHEEL_R, 0.25)
};

const wheelGroup = new THREE.Group();
wheelGroup.position.set(wheel.cx, wheel.axisY, wheel.cz);
scene.add(wheelGroup);

const wheelRingMat = new THREE.MeshStandardMaterial({ color: 0xd7dde3, metalness: 0.45, roughness: 0.42 });

const ringMajor = wheel.R + wheel.wall * 0.5;
const ringTube = wheel.wall * 0.5;

const ringGeo = new THREE.TorusGeometry(ringMajor, ringTube, 12, 48);

const ringL = new THREE.Mesh(ringGeo, wheelRingMat);
ringL.position.z = -wheel.width / 2;
ringL.castShadow = true;
ringL.receiveShadow = true;
wheelGroup.add(ringL);

const ringR = new THREE.Mesh(ringGeo, wheelRingMat);
ringR.position.z = wheel.width / 2;
ringR.castShadow = true;
ringR.receiveShadow = true;
wheelGroup.add(ringR);

const rungCount = 18;
const rungGeo = new THREE.CylinderGeometry(0.025, 0.025, wheel.width, 8);
const rungMat = new THREE.MeshStandardMaterial({ color: 0xe3e8ed, metalness: 0.35, roughness: 0.55 });
const rungs = new THREE.InstancedMesh(rungGeo, rungMat, rungCount);
rungs.castShadow = true;
rungs.receiveShadow = true;

{
  const dummy = new THREE.Object3D();
  const runRadius = wheel.R - 0.025; // верхняя точка беговой поверхности ≈ R
  for (let i = 0; i < rungCount; i++) {
    const a = (i / rungCount) * Math.PI * 2;
    dummy.position.set(Math.cos(a) * runRadius, Math.sin(a) * runRadius, 0);
    dummy.rotation.set(Math.PI / 2, 0, 0);
    dummy.scale.set(1, 1, 1);
    dummy.updateMatrix();
    rungs.setMatrixAt(i, dummy.matrix);
  }
  rungs.instanceMatrix.needsUpdate = true;
}
wheelGroup.add(rungs);

const axle = new THREE.Mesh(
  new THREE.CylinderGeometry(0.032, 0.032, wheel.width + 0.30, 12),
  new THREE.MeshStandardMaterial({ color: 0x8f979f, metalness: 0.7, roughness: 0.35 })
);
axle.rotation.x = Math.PI / 2;
axle.castShadow = true;
wheelGroup.add(axle);

/* Подставка держит ось снаружи, не проходит сквозь беговую поверхность. */
const standMat = new THREE.MeshStandardMaterial({ color: 0x6f7b86, metalness: 0.55, roughness: 0.45 });

for (let side of [-1, 1]) {
  const postX = wheel.cx - wheel.Rout - 0.12;
  const postZ = wheel.cz + side * (wheel.width / 2 + 0.12);

  const post = new THREE.Mesh(new THREE.BoxGeometry(0.10, wheel.axisY, 0.10), standMat);
  post.position.set(postX, wheel.axisY / 2, postZ);
  post.castShadow = true;
  post.receiveShadow = true;
  scene.add(post);

  const armLen = wheel.Rout + 0.12;
  const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, armLen, 10), standMat);
  arm.rotation.z = Math.PI / 2;
  arm.position.set(wheel.cx - armLen / 2, wheel.axisY, postZ);
  arm.castShadow = true;
  scene.add(arm);
}

/* Площадки у входа в колесо. */
const platformMat = new THREE.MeshStandardMaterial({ color: 0xb99a6b, roughness: 0.85 });
for (let side of [-1, 1]) {
  const p = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.055, 0.55), platformMat);
  p.position.set(wheel.cx, BED_Y - 0.035, wheel.cz + side * (wheel.width / 2 + 0.65));
  p.castShadow = true;
  p.receiveShadow = true;
  scene.add(p);
}

/* ------------------------- Труба ------------------------- */

const tube = {
  x0: TUBE_X0,
  x1: TUBE_X1,
  z: TUBE_Z,
  Rin: TUBE_R_IN,
  Rout: TUBE_R_OUT,
  wall: TUBE_WALL,
  centerY: TUBE_CENTER_Y,
  innerY: TUBE_INNER_Y,
  user: null
};

const tubeLen = tube.x1 - tube.x0;
const tubeOuterMat = new THREE.MeshStandardMaterial({
  color: 0x9fc0cf,
  roughness: 0.55,
  side: THREE.DoubleSide
});
const tubeInnerMat = new THREE.MeshStandardMaterial({
  color: 0x7d99a8,
  roughness: 0.72,
  side: THREE.DoubleSide
});

const tubeOuter = new THREE.Mesh(
  new THREE.CylinderGeometry(tube.Rout, tube.Rout, tubeLen, 36, 1, true),
  tubeOuterMat
);
tubeOuter.rotation.z = Math.PI / 2;
tubeOuter.position.set((tube.x0 + tube.x1) / 2, tube.centerY, tube.z);
tubeOuter.castShadow = true;
tubeOuter.receiveShadow = true;
scene.add(tubeOuter);

const tubeInner = new THREE.Mesh(
  new THREE.CylinderGeometry(tube.Rin, tube.Rin, tubeLen, 36, 1, true),
  tubeInnerMat
);
tubeInner.rotation.z = Math.PI / 2;
tubeInner.position.set((tube.x0 + tube.x1) / 2, tube.centerY, tube.z);
tubeInner.receiveShadow = true;
scene.add(tubeInner);

const endRingGeo = new THREE.RingGeometry(tube.Rin, tube.Rout, 32);
const endRingMat = new THREE.MeshStandardMaterial({ color: 0x8fa9b8, roughness: 0.65, side: THREE.DoubleSide });

const endL = new THREE.Mesh(endRingGeo, endRingMat);
endL.rotation.y = Math.PI / 2;
endL.position.set(tube.x0, tube.centerY, tube.z);
endL.castShadow = true;
scene.add(endL);

const endR = new THREE.Mesh(endRingGeo, endRingMat);
endR.rotation.y = Math.PI / 2;
endR.position.set(tube.x1, tube.centerY, tube.z);
endR.castShadow = true;
scene.add(endR);

/* ------------------------- Миска и зёрна ------------------------- */

const bowl = { x: BOWL_X, z: BOWL_Z, r: BOWL_R, user: null };

const bowlPoints = [
  new THREE.Vector2(0.00, 0.00),
  new THREE.Vector2(0.30, 0.00),
  new THREE.Vector2(0.40, 0.05),
  new THREE.Vector2(0.44, 0.14),
  new THREE.Vector2(0.42, 0.16),
  new THREE.Vector2(0.38, 0.09),
  new THREE.Vector2(0.28, 0.035),
  new THREE.Vector2(0.00, 0.035)
];

const bowlGeo = new THREE.LatheGeometry(bowlPoints, 36);
const bowlMat = new THREE.MeshStandardMaterial({
  color: 0xc46b2f,
  roughness: 0.55,
  side: THREE.DoubleSide
});
const bowlMesh = new THREE.Mesh(bowlGeo, bowlMat);
bowlMesh.position.set(bowl.x, BED_Y - 0.035, bowl.z);
bowlMesh.castShadow = true;
bowlMesh.receiveShadow = true;
scene.add(bowlMesh);

const seedCount = 90;
const seedGeo = new THREE.SphereGeometry(0.024, 8, 6);
const seedMat = new THREE.MeshStandardMaterial({ color: 0xd9b45f, roughness: 0.75 });
const seeds = new THREE.InstancedMesh(seedGeo, seedMat, seedCount);
seeds.castShadow = true;
seeds.receiveShadow = true;

{
  const dummy = new THREE.Object3D();
  for (let i = 0; i < seedCount; i++) {
    const a = Math.random() * Math.PI * 2;
    const r = Math.random() * 0.27;
    dummy.position.set(
      bowl.x + Math.cos(a) * r,
      BED_Y + 0.035 + Math.random() * 0.035,
      bowl.z + Math.sin(a) * r
    );
    dummy.rotation.set(Math.random(), Math.random(), Math.random());
    dummy.scale.setScalar(0.8 + Math.random() * 0.5);
    dummy.updateMatrix();
    seeds.setMatrixAt(i, dummy.matrix);
  }
  seeds.instanceMatrix.needsUpdate = true;
}
scene.add(seeds);

/* ------------------------- Поилка ------------------------- */

const bottleGroup = new THREE.Group();
bottleGroup.position.set(CAGE.maxX - 0.18, 1.55, -1.65);
scene.add(bottleGroup);

const bottleMat = new THREE.MeshStandardMaterial({
  color: 0xcfd8e0,
  transparent: true,
  opacity: 0.55,
  roughness: 0.25
});
const bottle = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.55, 20), bottleMat);
bottle.castShadow = true;
bottleGroup.add(bottle);

const water = new THREE.Mesh(
  new THREE.CylinderGeometry(0.11, 0.11, 0.42, 20),
  new THREE.MeshStandardMaterial({ color: 0x4f9ed8, transparent: true, opacity: 0.72, roughness: 0.2 })
);
water.position.y = -0.05;
bottleGroup.add(water);

const spout = new THREE.Mesh(
  new THREE.CylinderGeometry(0.018, 0.018, 0.34, 10),
  new THREE.MeshStandardMaterial({ color: 0xa8b0b8, metalness: 0.7, roughness: 0.35 })
);
spout.position.y = -0.42;
spout.castShadow = true;
bottleGroup.add(spout);

const bracket = new THREE.Mesh(
  new THREE.BoxGeometry(0.06, 0.18, 0.28),
  new THREE.MeshStandardMaterial({ color: 0x8f979f, metalness: 0.6, roughness: 0.4 })
);
bracket.position.set(0.12, 0.12, 0);
bottleGroup.add(bracket);

/* ------------------------- Хомяки ------------------------- */

const hamsters = [];
const hamsterGroups = [];

const hamsterDefs = [
  { name: "Пух",    color: 0xd9a066, belly: 0xf0d7b0, paw: 0xb87f4d },
  { name: "Тёмка",  color: 0x6b4a2b, belly: 0xa8815a, paw: 0x4f351f },
  { name: "Снежок", color: 0xf2e6d8, belly: 0xffffff, paw: 0xd8cfc4 },
  { name: "Серый",  color: 0x8f96a0, belly: 0xc8cdd3, paw: 0x666d75 },
  { name: "Рыжик",  color: 0xc46b2f, belly: 0xe8b07a, paw: 0x8f4a20 }
];

const spawnPoints = [
  [-1.05, 0.85],
  [ 0.55, -0.15],
  [-2.05, -0.55],
  [ 1.55, 1.25],
  [ 0.05, 1.55]
];

function createHamster(def, x, z) {
  const h = {
    name: def.name,
    color: def.color,
    pos: new THREE.Vector3(x, BED_Y, z),
    heading: Math.random() * Math.PI * 2,
    speed: 0,
    phase: Math.random() * Math.PI * 2,
    phaseOffset: Math.random() * Math.PI * 2,
    state: "IDLE",
    stateTime: 0,
    idleDur: 1 + Math.random() * 3,
    activity: null,
    target: new THREE.Vector3(x, BED_Y, z),
    waypoints: [],
    wpIndex: 0,
    jumping: false,
    jumpVel: 0,
    earTimer: 1 + Math.random() * 4,
    earTwitch: 0,
    runSpeed: 1.3,
    activityDur: 6,
    wheelDir: 1,
    tubeSide: -1
  };

  const group = new THREE.Group();
  h.group = group;

  const furMat = new THREE.MeshStandardMaterial({ color: def.color, roughness: 0.92 });
  const bellyMat = new THREE.MeshStandardMaterial({ color: def.belly, roughness: 0.95 });
  const pawMat = new THREE.MeshStandardMaterial({ color: def.paw, roughness: 0.9 });
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.28 });
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.18 });
  const noseMat = new THREE.MeshStandardMaterial({ color: 0x332222, roughness: 0.45 });
  const earInMat = new THREE.MeshStandardMaterial({ color: 0xe8a7a7, roughness: 0.82 });

  const bodyGroup = new THREE.Group();
  h.bodyGroup = bodyGroup;
  group.add(bodyGroup);

  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), furMat);
  body.scale.set(HAM.length * 0.5, HAM.height * 0.5, HAM.width * 0.5);
  body.position.y = 0.24;
  body.castShadow = true;
  bodyGroup.add(body);

  const belly = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), bellyMat);
  belly.scale.set(HAM.length * 0.38, HAM.height * 0.36, HAM.width * 0.42);
  belly.position.set(0.02, 0.18, 0);
  belly.castShadow = true;
  bodyGroup.add(belly);

  const headGroup = new THREE.Group();
  headGroup.position.set(0.28, 0.27, 0);
  h.headGroup = headGroup;
  bodyGroup.add(headGroup);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.16, 20, 16), furMat);
  head.scale.set(1.15, 1, 1);
  head.castShadow = true;
  headGroup.add(head);

  const snout = new THREE.Mesh(new THREE.SphereGeometry(0.085, 16, 12), furMat);
  snout.position.set(0.12, -0.02, 0);
  snout.castShadow = true;
  headGroup.add(snout);

  for (let s of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 12, 10), eyeMat);
    eye.position.set(0.11, 0.045, s * 0.085);
    headGroup.add(eye);

    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.022, 10, 8), pupilMat);
    pupil.position.set(0.145, 0.045, s * 0.09);
    headGroup.add(pupil);

    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.075, 14, 12), furMat);
    cheek.position.set(0.03, -0.03, s * 0.12);
    cheek.castShadow = true;
    headGroup.add(cheek);

    const earPivot = new THREE.Group();
    earPivot.position.set(-0.01, 0.13, s * 0.10);
    headGroup.add(earPivot);

    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.07, 14, 12), furMat);
    ear.scale.set(0.35, 1, 1);
    ear.castShadow = true;
    earPivot.add(ear);

    const earIn = new THREE.Mesh(new THREE.SphereGeometry(0.045, 12, 10), earInMat);
    earIn.position.set(0.02, 0, 0);
    earIn.scale.set(0.3, 1, 1);
    earPivot.add(earIn);

    if (s < 0) h.earL = earPivot;
    else h.earR = earPivot;
  }

  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.025, 10, 8), noseMat);
  nose.position.set(0.20, -0.01, 0);
  headGroup.add(nose);

  h.legs = [];
  const legDefs = [
    { x:  0.18, z:  0.16, off: 0 },
    { x:  0.18, z: -0.16, off: Math.PI },
    { x: -0.18, z:  0.16, off: Math.PI },
    { x: -0.18, z: -0.16, off: 0 }
  ];

  for (const ld of legDefs) {
    const pivot = new THREE.Group();
    pivot.position.set(ld.x, 0.18, ld.z);
    bodyGroup.add(pivot);

    const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.038, 0.12, 10), furMat);
    upper.position.y = -0.06;
    upper.castShadow = true;
    pivot.add(upper);

    const paw = new THREE.Mesh(new THREE.SphereGeometry(0.045, 12, 10), pawMat);
    paw.position.y = -0.135;
    paw.castShadow = true;
    pivot.add(paw);

    h.legs.push({
      pivot,
      baseX: ld.x,
      baseZ: ld.z,
      baseY: 0.18,
      off: ld.off
    });
  }

  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.055, 12, 10), furMat);
  tail.position.set(-0.33, 0.12, 0);
  tail.castShadow = true;
  h.tail = tail;
  bodyGroup.add(tail);

  group.position.copy(h.pos);
  group.rotation.y = -h.heading;

  group.traverse(o => {
    if (o.isMesh) o.userData.hamster = h;
  });

  scene.add(group);
  hamsters.push(h);
  hamsterGroups.push(group);
  return h;
}

for (let i = 0; i < hamsterDefs.length; i++) {
  createHamster(hamsterDefs[i], spawnPoints[i][0], spawnPoints[i][1]);
}

/* ------------------------- Вспомогательные функции ------------------------- */

function angleLerp(a, b, t) {
  let d = ((b - a + Math.PI) % (Math.PI * 2)) - Math.PI;
  if (d < -Math.PI) d += Math.PI * 2;
  return a + d * Math.min(1, t);
}

function releaseActivity(h) {
  if (h.activity === "wheel" && wheel.user === h) wheel.user = null;
  if (h.activity === "tube" && tube.user === h) tube.user = null;
  if (h.activity === "bowl" && bowl.user === h) bowl.user = null;
  h.activity = null;
}

function abortActivity(h) {
  releaseActivity(h);
  h.state = "IDLE";
  h.stateTime = 0;
  h.idleDur = 1 + Math.random() * 2;
}

function isBlocked(x, z) {
  if (
    x > wheel.cx - wheel.Rout - HAM.radius &&
    x < wheel.cx + wheel.Rout + HAM.radius &&
    z > wheel.cz - wheel.width / 2 - HAM.radius &&
    z < wheel.cz + wheel.width / 2 + HAM.radius
  ) return true;

  if (
    x > tube.x0 - HAM.radius &&
    x < tube.x1 + HAM.radius &&
    z > tube.z - tube.Rout - HAM.radius &&
    z < tube.z + tube.Rout + HAM.radius
  ) return true;

  if (Math.hypot(x - bowl.x, z - bowl.z) < bowl.r + HAM.radius) return true;

  return false;
}

function randomTarget() {
  for (let i = 0; i < 40; i++) {
    const x = CAGE.minX + 0.55 + Math.random() * (CAGE.maxX - CAGE.minX - 1.1);
    const z = CAGE.minZ + 0.55 + Math.random() * (CAGE.maxZ - CAGE.minZ - 1.1);
    if (!isBlocked(x, z)) return new THREE.Vector3(x, BED_Y, z);
  }
  return new THREE.Vector3(0, BED_Y, 0);
}

function chooseActivity(h) {
  releaseActivity(h);

  const opts = [];
  if (!wheel.user) opts.push("wheel");
  if (!tube.user) opts.push("tube");
  if (!bowl.user) opts.push("bowl");
  opts.push("walk", "walk");

  const act = opts[Math.floor(Math.random() * opts.length)];
  h.activity = act;
  h.stateTime = 0;

  if (act === "wheel") {
    wheel.user = h;
    h.state = "WALK_TO_WHEEL";
    h.entrySide = (h.pos.z > wheel.cz) ? 1 : -1;
    h.target = new THREE.Vector3(
      wheel.cx,
      BED_Y,
      wheel.cz + h.entrySide * (wheel.width / 2 + 0.75)
    );
  } else if (act === "tube") {
    tube.user = h;
    h.state = "WALK_TO_TUBE";
    h.tubeSide = (h.pos.x < (tube.x0 + tube.x1) / 2) ? -1 : 1;
    h.target = new THREE.Vector3(
      h.tubeSide === -1 ? tube.x0 - 0.65 : tube.x1 + 0.65,
      BED_Y,
      tube.z
    );
  } else if (act === "bowl") {
    bowl.user = h;
    h.state = "WALK_TO_BOWL";

    let dx = h.pos.x - bowl.x;
    let dz = h.pos.z - bowl.z;
    let d = Math.hypot(dx, dz);
    if (d < 0.1) { dx = 1; dz = 0; d = 1; }

    const r = bowl.r + 0.32;
    h.target = new THREE.Vector3(bowl.x + dx / d * r, BED_Y, bowl.z + dz / d * r);
  } else {
    h.state = "WALK";
    h.target = randomTarget();
  }
}

function wheelEnterWaypoints(h) {
  const side = h.entrySide;
  const zEntry = wheel.cz + side * (wheel.width / 2 + 0.75);
  const zMouth = wheel.cz + side * (wheel.width / 2 + 0.02);

  return [
    new THREE.Vector3(wheel.cx, BED_Y, zEntry),
    new THREE.Vector3(wheel.cx, wheel.bottomY + 0.18, zMouth),
    new THREE.Vector3(wheel.cx, wheel.bottomY + 0.18, wheel.cz),
    new THREE.Vector3(wheel.cx, wheel.bottomY, wheel.cz)
  ];
}

function wheelExitWaypoints(h) {
  const side = h.entrySide;
  const zEntry = wheel.cz + side * (wheel.width / 2 + 0.75);
  const zMouth = wheel.cz + side * (wheel.width / 2 + 0.02);

  return [
    new THREE.Vector3(wheel.cx, wheel.bottomY + 0.18, wheel.cz),
    new THREE.Vector3(wheel.cx, wheel.bottomY + 0.18, zMouth),
    new THREE.Vector3(wheel.cx, BED_Y, zEntry)
  ];
}

function tubeEnterWaypoints(h) {
  if (h.tubeSide === -1) {
    return [
      new THREE.Vector3(tube.x0 - 0.65, BED_Y, tube.z),
      new THREE.Vector3(tube.x0 - 0.02, tube.innerY + 0.14, tube.z),
      new THREE.Vector3(tube.x0 + 0.35, tube.innerY + 0.14, tube.z),
      new THREE.Vector3(tube.x0 + 0.35, tube.innerY, tube.z)
    ];
  } else {
    return [
      new THREE.Vector3(tube.x1 + 0.65, BED_Y, tube.z),
      new THREE.Vector3(tube.x1 + 0.02, tube.innerY + 0.14, tube.z),
      new THREE.Vector3(tube.x1 - 0.35, tube.innerY + 0.14, tube.z),
      new THREE.Vector3(tube.x1 - 0.35, tube.innerY, tube.z)
    ];
  }
}

function tubeExitWaypoints(h) {
  if (h.tubeSide === -1) {
    return [
      new THREE.Vector3(tube.x1 - 0.35, tube.innerY + 0.14, tube.z),
      new THREE.Vector3(tube.x1 + 0.02, tube.innerY + 0.14, tube.z),
      new THREE.Vector3(tube.x1 + 0.65, BED_Y, tube.z)
    ];
  } else {
    return [
      new THREE.Vector3(tube.x0 + 0.35, tube.innerY + 0.14, tube.z),
      new THREE.Vector3(tube.x0 - 0.02, tube.innerY + 0.14, tube.z),
      new THREE.Vector3(tube.x0 - 0.65, BED_Y, tube.z)
    ];
  }
}

function tubeCrawlTarget(h) {
  if (h.tubeSide === -1) {
    return new THREE.Vector3(tube.x1 - 0.35, tube.innerY, tube.z);
  } else {
    return new THREE.Vector3(tube.x0 + 0.35, tube.innerY, tube.z);
  }
}

function moveTo(h, target, speed, dt, ySpeed) {
  const dx = target.x - h.pos.x;
  const dz = target.z - h.pos.z;
  const dist = Math.hypot(dx, dz);

  if (dist > 1e-4) {
    const desired = Math.atan2(dz, dx);
    h.heading = angleLerp(h.heading, desired, 12 * dt);

    const step = Math.min(speed * dt, dist);
    h.pos.x += Math.cos(h.heading) * step;
    h.pos.z += Math.sin(h.heading) * step;

    /* Фаза шага — от пройденного пути. */
    h.phase += (step / HAM.stride) * Math.PI * 2;
    h.speed = step / dt;
  } else {
    h.speed = 0;
  }

  if (!h.jumping && ySpeed > 0) {
    const dy = target.y - h.pos.y;
    if (Math.abs(dy) > 1e-4) {
      const step = Math.min(ySpeed * dt, Math.abs(dy));
      h.pos.y += Math.sign(dy) * step;
    }
  }

  return dist < 0.07 && (h.jumping || Math.abs(target.y - h.pos.y) < 0.07);
}

function followWaypoints(h, speed, ySpeed, dt) {
  if (h.wpIndex >= h.waypoints.length) return true;

  const reached = moveTo(h, h.waypoints[h.wpIndex], speed, dt, ySpeed);
  if (reached) h.wpIndex++;

  return h.wpIndex >= h.waypoints.length;
}

function groundYFor(h) {
  if (h.state === "RUN_WHEEL") return wheel.bottomY;
  if (h.state === "CRAWL_TUBE") return tube.innerY;
  return BED_Y;
}

/* ------------------------- Физика колеса ------------------------- */

function updateWheel(dt) {
  const runner = (wheel.user && wheel.user.state === "RUN_WHEEL") ? wheel.user : null;

  if (runner) {
    const v = runner.runSpeed;
    const targetOmega = -runner.wheelDir * v / wheel.R;

    /* omega = v / R, с короткой инерционной подтяжкой. */
    wheel.omega += (targetOmega - wheel.omega) * (1 - Math.exp(-18 * dt));
    wheel.pawSpeed = v;
  } else {
    /* Пустое колесо замедляется трением. */
    wheel.omega *= Math.exp(-1.15 * dt);
    if (Math.abs(wheel.omega) < 1e-4) wheel.omega = 0;
    wheel.pawSpeed = 0;
  }

  wheel.angle += wheel.omega * dt;
  wheel.rimSpeed = Math.abs(wheel.omega) * wheel.R;

  if (wheel.pawSpeed > 0.01) {
    wheel.diff = Math.abs(wheel.pawSpeed - wheel.rimSpeed) / wheel.pawSpeed * 100;
  } else {
    wheel.diff = 0;
  }

  wheelGroup.rotation.z = wheel.angle;
}

/* ------------------------- Столкновения предметов ------------------------- */

function applyObjectCollisions(h) {
  const insideWheel =
    h.state === "RUN_WHEEL" ||
    h.state === "ENTER_WHEEL" ||
    h.state === "EXIT_WHEEL";

  const insideTube =
    h.state === "CRAWL_TUBE" ||
    h.state === "ENTER_TUBE" ||
    h.state === "EXIT_TUBE";

  /* Колесо: прямоугольная форма столкновения для гуляющих. */
  if (!insideWheel) {
    const minX = wheel.cx - wheel.Rout - HAM.radius;
    const maxX = wheel.cx + wheel.Rout + HAM.radius;
    const minZ = wheel.cz - wheel.width / 2 - HAM.radius;
    const maxZ = wheel.cz + wheel.width / 2 + HAM.radius;

    if (h.pos.x > minX && h.pos.x < maxX && h.pos.z > minZ && h.pos.z < maxZ) {
      const d1 = h.pos.x - minX;
      const d2 = maxX - h.pos.x;
      const d3 = h.pos.z - minZ;
      const d4 = maxZ - h.pos.z;
      const m = Math.min(d1, d2, d3, d4);

      if (m === d1) h.pos.x = minX;
      else if (m === d2) h.pos.x = maxX;
      else if (m === d3) h.pos.z = minZ;
      else h.pos.z = maxZ;
    }
  }

  /* Труба: прямоугольник, гуляющие не проходят сквозь боковину и торцы. */
  if (!insideTube) {
    const minX = tube.x0 - HAM.radius;
    const maxX = tube.x1 + HAM.radius;
    const minZ = tube.z - tube.Rout - HAM.radius;
    const maxZ = tube.z + tube.Rout + HAM.radius;

    if (h.pos.x > minX && h.pos.x < maxX && h.pos.z > minZ && h.pos.z < maxZ) {
      const d1 = h.pos.x - minX;
      const d2 = maxX - h.pos.x;
      const d3 = h.pos.z - minZ;
      const d4 = maxZ - h.pos.z;
      const m = Math.min(d1, d2, d3, d4);

      if (m === d1) h.pos.x = minX;
      else if (m === d2) h.pos.x = maxX;
      else if (m === d3) h.pos.z = minZ;
      else h.pos.z = maxZ;
    }
  }

  /* Миска: круг. */
  let dx = h.pos.x - bowl.x;
  let dz = h.pos.z - bowl.z;
  let dist = Math.hypot(dx, dz);
  const minDist = bowl.r + HAM.radius;

  if (dist < minDist) {
    if (dist < 1e-4) { dx = 1; dz = 0; dist = 1; }
    const push = minDist - dist;
    h.pos.x += dx / dist * push;
    h.pos.z += dz / dist * push;
  }

  /* Стенки клетки. */
  h.pos.x = Math.max(CAGE.minX + HAM.radius, Math.min(CAGE.maxX - HAM.radius, h.pos.x));
  h.pos.z = Math.max(CAGE.minZ + HAM.radius, Math.min(CAGE.maxZ - HAM.radius, h.pos.z));
}

function resolveHamsterCollisions() {
  const inside = new Set([
    "RUN_WHEEL", "ENTER_WHEEL", "EXIT_WHEEL",
    "CRAWL_TUBE", "ENTER_TUBE", "EXIT_TUBE"
  ]);

  for (let i = 0; i < hamsters.length; i++) {
    for (let j = i + 1; j < hamsters.length; j++) {
      const a = hamsters[i];
      const b = hamsters[j];

      if (inside.has(a.state) || inside.has(b.state)) continue;

      let dx = b.pos.x - a.pos.x;
      let dz = b.pos.z - a.pos.z;
      let dist = Math.hypot(dx, dz);
      const minDist = HAM.radius * 2;

      if (dist < minDist) {
        if (dist < 1e-4) {
          dx = Math.random() - 0.5;
          dz = Math.random() - 0.5;
          dist = Math.hypot(dx, dz) || 1;
        }

        const overlap = (minDist - dist) * 0.5 * 0.72;
        const nx = dx / dist;
        const nz = dz / dist;

        a.pos.x -= nx * overlap;
        a.pos.z -= nz * overlap;
        b.pos.x += nx * overlap;
        b.pos.z += nz * overlap;
      }
    }
  }

  for (const h of hamsters) {
    h.pos.x = Math.max(CAGE.minX + HAM.radius, Math.min(CAGE.maxX - HAM.radius, h.pos.x));
    h.pos.z = Math.max(CAGE.minZ + HAM.radius, Math.min(CAGE.maxZ - HAM.radius, h.pos.z));
  }
}

/* ------------------------- Конечный автомат хомяка ------------------------- */

function updateHamster(h, dt, t) {
  h.stateTime += dt;

  switch (h.state) {
    case "IDLE":
      h.speed = 0;
      if (h.stateTime > h.idleDur) chooseActivity(h);
      break;

    case "WALK":
      if (moveTo(h, h.target, HAM.walkSpeed, dt, 1)) {
        h.state = "IDLE";
        h.stateTime = 0;
        h.idleDur = 1 + Math.random() * 3;
      }
      if (h.stateTime > 14) abortActivity(h);
      break;

    case "WALK_TO_WHEEL":
      if (moveTo(h, h.target, HAM.walkSpeed, dt, 1)) {
        h.state = "ENTER_WHEEL";
        h.waypoints = wheelEnterWaypoints(h);
        h.wpIndex = 0;
        h.stateTime = 0;
      }
      if (h.stateTime > 16) abortActivity(h);
      break;

    case "ENTER_WHEEL":
      if (followWaypoints(h, 0.58, 0.85, dt)) {
        h.state = "RUN_WHEEL";
        h.stateTime = 0;
        h.wheelDir = Math.random() < 0.5 ? 1 : -1;
        h.runSpeed = 1.25 + Math.random() * 0.45;
        h.activityDur = 5 + Math.random() * 8;

        /* Начальная согласованность: omega = v / R. */
        wheel.omega = -h.wheelDir * h.runSpeed / wheel.R;
      }
      if (h.stateTime > 12) abortActivity(h);
      break;

    case "RUN_WHEEL": {
      /* Плавное удержание на нижней точке обода, без мгновенной установки. */
      const k = 1 - Math.exp(-12 * dt);
      h.pos.x += (wheel.bottomPos.x - h.pos.x) * k;
      h.pos.y += (wheel.bottomPos.y - h.pos.y) * k;
      h.pos.z += (wheel.bottomPos.z - h.pos.z) * k;

      h.heading = h.wheelDir > 0 ? 0 : Math.PI;

      h.runSpeed =
        1.25 +
        0.35 * Math.sin(t * 0.8 + h.phaseOffset) +
        0.15 * Math.sin(t * 2.3 + h.phaseOffset * 0.7);

      h.speed = h.runSpeed;

      /* Шаг в колесе привязан к скорости обода / скорости лап. */
      h.phase += (h.runSpeed * dt / HAM.stride) * Math.PI * 2;

      if (h.stateTime > h.activityDur) {
        h.state = "EXIT_WHEEL";
        h.waypoints = wheelExitWaypoints(h);
        h.wpIndex = 0;
        h.stateTime = 0;
      }
      break;
    }

    case "EXIT_WHEEL":
      if (followWaypoints(h, 0.58, 0.85, dt)) {
        releaseActivity(h);
        h.state = "IDLE";
        h.stateTime = 0;
        h.idleDur = 1 + Math.random() * 2;
      }
      if (h.stateTime > 12) abortActivity(h);
      break;

    case "WALK_TO_TUBE":
      if (moveTo(h, h.target, HAM.walkSpeed, dt, 1)) {
        h.state = "ENTER_TUBE";
        h.waypoints = tubeEnterWaypoints(h);
        h.wpIndex = 0;
        h.stateTime = 0;
      }
      if (h.stateTime > 16) abortActivity(h);
      break;

    case "ENTER_TUBE":
      if (followWaypoints(h, 0.48, 0.75, dt)) {
        h.state = "CRAWL_TUBE";
        h.target = tubeCrawlTarget(h);
        h.stateTime = 0;
      }
      if (h.stateTime > 12) abortActivity(h);
      break;

    case "CRAWL_TUBE":
      /* Строго вдоль оси трубы, на внутреннем дне. */
      if (moveTo(h, h.target, 0.46, dt, 0.7)) {
        h.state = "EXIT_TUBE";
        h.waypoints = tubeExitWaypoints(h);
        h.wpIndex = 0;
        h.stateTime = 0;
      }
      if (h.stateTime > 18) abortActivity(h);
      break;

    case "EXIT_TUBE":
      if (followWaypoints(h, 0.50, 0.75, dt)) {
        releaseActivity(h);
        h.state = "IDLE";
        h.stateTime = 0;
        h.idleDur = 1 + Math.random() * 2;
      }
      if (h.stateTime > 12) abortActivity(h);
      break;

    case "WALK_TO_BOWL":
      if (moveTo(h, h.target, HAM.walkSpeed, dt, 1)) {
        h.state = "EAT";
        h.stateTime = 0;
        h.activityDur = 4 + Math.random() * 5;
      }
      if (h.stateTime > 16) abortActivity(h);
      break;

    case "EAT":
      h.speed = 0;
      if (h.stateTime > h.activityDur) {
        releaseActivity(h);
        h.state = "IDLE";
        h.stateTime = 0;
        h.idleDur = 1 + Math.random() * 2;
      }
      break;
  }

  /* Прыжок по клику. */
  if (h.jumping) {
    h.jumpVel -= 9.8 * dt;
    h.pos.y += h.jumpVel * dt;

    const ground = groundYFor(h);
    if (h.pos.y <= ground) {
      h.pos.y = ground;
      h.jumping = false;
      h.jumpVel = 0;
    }
  }

  applyObjectCollisions(h);
  updateHamsterVisual(h, dt, t);
}

/* ------------------------- Визуальная анимация хомяка ------------------------- */

function updateHamsterVisual(h, dt, t) {
  h.group.position.copy(h.pos);
  h.group.rotation.y = -h.heading;

  const speedFactor = Math.min(1.3, h.speed / 0.65);
  const amp = 0.48 * speedFactor;
  const liftAmp = 0.075 * speedFactor;

  for (const leg of h.legs) {
    const ph = h.phase + leg.off;
    const swing = Math.sin(ph) * amp;
    leg.pivot.rotation.z = swing;

    let surfaceOffset = 0;

    /* В колесе лапы адаптируются к нижней дуге обода. */
    if (h.state === "RUN_WHEEL") {
      const dx = leg.baseX;
      const R = wheel.R;
      surfaceOffset = R - Math.sqrt(Math.max(0, R * R - dx * dx));
    }

    /* В трубе лапы адаптируются к внутреннему дну трубы. */
    if (h.state === "CRAWL_TUBE") {
      const dz = leg.baseZ;
      const R = tube.Rin;
      surfaceOffset = R - Math.sqrt(Math.max(0, R * R - dz * dz));
    }

    const lift = Math.max(0, Math.cos(ph)) * liftAmp;
    leg.pivot.position.y = leg.baseY + surfaceOffset + lift;
  }

  const bob = Math.sin(h.phase * 2) * 0.012 * speedFactor;
  h.bodyGroup.position.y = bob;

  const breath = (h.speed < 0.05)
    ? Math.sin(t * 2.1 + h.phaseOffset) * 0.035
    : Math.sin(t * 4.0 + h.phaseOffset) * 0.012;

  h.bodyGroup.scale.set(
    1 + breath * 0.4,
    1 + breath,
    1 + breath * 0.4
  );

  if (h.state === "EAT") {
    h.headGroup.position.y = 0.215 + Math.sin(t * 8 + h.phaseOffset) * 0.015;
    h.headGroup.rotation.x = -0.50 + Math.sin(t * 9 + h.phaseOffset) * 0.14;
  } else {
    h.headGroup.position.y = 0.27 + Math.sin(h.phase * 2 + 0.5) * 0.012 * speedFactor;
    h.headGroup.rotation.x = Math.sin(h.phase * 2) * 0.05 * speedFactor;
  }

  h.earTimer -= dt;
  if (h.earTimer <= 0) {
    h.earTwitch = 0.4 + Math.random() * 0.3;
    h.earTimer = 2 + Math.random() * 6;
  }
  h.earTwitch = Math.max(0, h.earTwitch - dt * 1.2);

  const twitch = Math.sin(t * 28) * h.earTwitch;
  if (h.earL) h.earL.rotation.z = 0.12 + twitch * 0.35;
  if (h.earR) h.earR.rotation.z = -0.12 - twitch * 0.35;

  if (h.tail) h.tail.rotation.z = Math.sin(t * 1.7 + h.phaseOffset) * 0.12;
}

/* ------------------------- Клик: прыжок ------------------------- */

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let pointerDown = null;

function jumpHamster(h) {
  if (
    h.state === "ENTER_WHEEL" ||
    h.state === "EXIT_WHEEL" ||
    h.state === "ENTER_TUBE" ||
    h.state === "EXIT_TUBE"
  ) return;

  if (h.state === "RUN_WHEEL") {
    h.state = "EXIT_WHEEL";
    h.waypoints = wheelExitWaypoints(h);
    h.wpIndex = 0;
    h.stateTime = 0;
    return;
  }

  if (h.state === "CRAWL_TUBE") {
    h.state = "EXIT_TUBE";
    h.waypoints = tubeExitWaypoints(h);
    h.wpIndex = 0;
    h.stateTime = 0;
    return;
  }

  if (!h.jumping) {
    h.jumping = true;
    h.jumpVel = 2.15;
  }
}

renderer.domElement.addEventListener("pointerdown", e => {
  pointerDown = { x: e.clientX, y: e.clientY };
});

renderer.domElement.addEventListener("pointerup", e => {
  if (!pointerDown) return;
  const moved = Math.hypot(e.clientX - pointerDown.x, e.clientY - pointerDown.y);
  pointerDown = null;

  if (moved > 5) return;

  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(hamsterGroups, true);

  if (hits.length > 0) {
    let obj = hits[0].object;
    while (obj && !obj.userData.hamster) obj = obj.parent;
    if (obj && obj.userData.hamster) jumpHamster(obj.userData.hamster);
  }
});

/* ------------------------- UI ------------------------- */

const stateLabel = {
  IDLE: "стоит",
  WALK: "гуляет",
  WALK_TO_WHEEL: "идёт к колесу",
  ENTER_WHEEL: "забирается в колесо",
  RUN_WHEEL: "бежит в колесе",
  EXIT_WHEEL: "выходит из колеса",
  WALK_TO_TUBE: "идёт к трубе",
  ENTER_TUBE: "заползает в трубу",
  CRAWL_TUBE: "ползёт по трубе",
  EXIT_TUBE: "вылезает из трубы",
  WALK_TO_BOWL: "идёт к миске",
  EAT: "грызёт зёрна"
};

const hamsterListEl = document.getElementById("hamsterList");
const wheelDebugEl = document.getElementById("wheelDebug");
const tubeDebugEl = document.getElementById("tubeDebug");

function hexColor(c) {
  return "#" + c.toString(16).padStart(6, "0");
}

function updateUI() {
  let html = "";
  for (const h of hamsters) {
    html +=
      `<div class="row">` +
      `<span class="dot" style="background:${hexColor(h.color)}"></span>` +
      `<b>${h.name}</b>` +
      `<span class="state">${stateLabel[h.state] || h.state}</span>` +
      `<span class="speed">${h.speed.toFixed(2)}</span>` +
      `</div>`;
  }
  hamsterListEl.innerHTML = html;

  const runner = (wheel.user && wheel.user.state === "RUN_WHEEL") ? wheel.user : null;

  wheelDebugEl.textContent =
    `КОЛЕСО\n` +
    `R = ${wheel.R.toFixed(3)} м\n` +
    `габарит зверя = ${HAM.length.toFixed(2)} × ${HAM.height.toFixed(2)} × ${HAM.width.toFixed(2)}\n` +
    `ω = ${wheel.omega.toFixed(3)} рад/с\n` +
    `скорость лап = ${wheel.pawSpeed.toFixed(3)} м/с\n` +
    `|ω|·R = ${wheel.rimSpeed.toFixed(3)} м/с\n` +
    `расхождение = ${wheel.diff.toFixed(2)} %\n` +
    (runner ? `бегун: ${runner.name}` : `бегуна нет — трение гасит колесо`);

  const tubeH = hamsters.find(h => h.state === "CRAWL_TUBE");
  if (tubeH) {
    const devZ = Math.abs(tubeH.pos.z - tube.z);
    const devY = Math.abs(tubeH.pos.y - tube.innerY);
    tubeDebugEl.textContent =
      `ТРУБА\n` +
      `хомяк: ${tubeH.name}\n` +
      `отклонение от оси z = ${devZ.toFixed(4)} м\n` +
      `отклонение от дна y = ${devY.toFixed(4)} м`;
  } else {
    tubeDebugEl.textContent = `ТРУБА\nсейчас пустая`;
  }
}

/* ------------------------- Цикл ------------------------- */

let last = performance.now();
let uiAccum = 0;

function animate(now) {
  requestAnimationFrame(animate);

  let dt = (now - last) / 1000;
  last = now;
  if (dt > 0.05) dt = 0.05;

  const t = now / 1000;

  updateWheel(dt);

  for (const h of hamsters) {
    updateHamster(h, dt, t);
  }

  resolveHamsterCollisions();

  controls.update();
  renderer.render(scene, camera);

  uiAccum += dt;
  if (uiAccum > 0.12) {
    updateUI();
    uiAccum = 0;
  }
}

requestAnimationFrame(animate);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* Снаружи можно прочитать состояние: */
window.hamsters = hamsters;
window.wheel = wheel;
window.tube = tube;
window.bowl = bowl;
window.HAM = HAM;
</script>

</body>
</html>
```