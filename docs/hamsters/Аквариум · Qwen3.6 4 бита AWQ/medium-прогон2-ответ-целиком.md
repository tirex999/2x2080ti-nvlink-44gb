```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; background: #0a1628; font-family: 'Segoe UI', Tahoma, sans-serif; }
canvas { display: block; }

.ui-panel {
  position: absolute;
  background: rgba(10, 30, 60, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(100, 180, 255, 0.2);
  border-radius: 16px;
  padding: 18px 22px;
  color: #c8e6ff;
  box-shadow: 0 8px 32px rgba(0, 50, 120, 0.4), inset 0 1px 0 rgba(255,255,255,0.05);
  transition: all 0.3s ease;
}
.ui-panel:hover { border-color: rgba(100, 180, 255, 0.4); box-shadow: 0 8px 40px rgba(0, 80, 160, 0.5); }

.info-panel { top: 20px; left: 20px; min-width: 260px; }
.info-panel h1 {
  font-size: 22px; margin-bottom: 12px;
  background: linear-gradient(135deg, #00d4ff, #7b68ee, #ff6ec7);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; font-weight: 800; letter-spacing: 1px;
}
.info-panel p { font-size: 12px; line-height: 1.7; opacity: 0.8; margin-bottom: 4px; }
.info-panel .key { color: #00d4ff; font-weight: 600; }

.stats-panel { top: 20px; right: 20px; min-width: 180px; text-align: right; }
.stats-panel .stat-value { font-size: 28px; font-weight: 700; color: #00d4ff; }
.stats-panel .stat-label { font-size: 11px; opacity: 0.6; text-transform: uppercase; letter-spacing: 1px; }

.controls-panel { bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; }

.btn {
  background: linear-gradient(135deg, rgba(0,120,200,0.5), rgba(0,80,160,0.3));
  border: 1px solid rgba(100, 180, 255, 0.3);
  border-radius: 12px; padding: 10px 20px;
  color: #c8e6ff; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: all 0.3s ease;
  backdrop-filter: blur(8px); white-space: nowrap;
  box-shadow: 0 4px 15px rgba(0, 60, 120, 0.3);
}
.btn:hover {
  background: linear-gradient(135deg, rgba(0,150,240,0.7), rgba(0,100,200,0.5));
  border-color: rgba(100, 200, 255, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 100, 200, 0.5);
  color: #fff;
}
.btn:active { transform: translateY(0); }
.btn .emoji { margin-right: 6px; }

.divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(100,180,255,0.3), transparent); margin: 10px 0; }

@media (max-width: 768px) {
  .info-panel { top: 10px; left: 10px; min-width: 200px; padding: 12px 15px; }
  .info-panel h1 { font-size: 16px; }
  .stats-panel { top: 10px; right: 10px; min-width: 140px; padding: 12px 15px; }
  .controls-panel { bottom: 10px; gap: 6px; }
  .btn { padding: 8px 14px; font-size: 11px; }
}
</style>
</head>
<body>

<div class="ui-panel info-panel">
  <h1>🐠 3D Аква́риум</h1>
  <div class="divider"></div>
  <p><span class="key">🖱 ЛКМ</span> — вращение камеры</p>
  <p><span class="key">🖱 ПКМ</span> — перемещение</p>
  <p><span class="key">🖱 Колёсико</span> — масштаб</p>
  <p><span class="key">👆 Клик</span> — покормить рыбок</p>
</div>

<div class="ui-panel stats-panel">
  <div class="stat-value" id="fishCount">15</div>
  <div class="stat-label">Рыбок</div>
  <div class="divider"></div>
  <div class="stat-value" id="fpsCounter">60</div>
  <div class="stat-label">FPS</div>
  <div class="divider"></div>
  <div class="stat-value" id="foodCount">0</div>
  <div class="stat-label">Корма</div>
</div>

<div class="ui-panel controls-panel">
  <button class="btn" onclick="addFish()"><span class="emoji">🐟</span>Добавить рыбку</button>
  <button class="btn" onclick="addBubbles()"><span class="emoji">💭</span>Больше пузырей</button>
  <button class="btn" onclick="toggleLight()"><span class="emoji">💡</span>Свет</button>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ==================== SCENE SETUP ====================
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a1e3a);
scene.fog = new THREE.FogExp2(0x0a1e3a, 0.012);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 12, 45);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
document.body.appendChild(renderer.domElement);

// ==================== CONTROLS ====================
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.target.set(0, 0, 0);

// ==================== LIGHTING ====================
const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffeedd, 0.8);
dirLight.position.set(15, 30, 20);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
dirLight.shadow.camera.near = 1;
dirLight.shadow.camera.far = 80;
dirLight.shadow.camera.left = -25;
dirLight.shadow.camera.right = 25;
dirLight.shadow.camera.top = 25;
dirLight.shadow.camera.bottom = -25;
dirLight.shadow.bias = -0.001;
scene.add(dirLight);

const pointLight1 = new THREE.PointLight(0x0088cc, 0.6, 50);
pointLight1.position.set(-10, 8, -5);
scene.add(pointLight1);

const pointLight2 = new THREE.PointLight(0x0044aa, 0.5, 50);
pointLight2.position.set(10, 5, 5);
scene.add(pointLight2);

let lightOn = true;

// ==================== AQUARIUM DIMENSIONS ====================
const AW = 36, AH = 24, AD = 20;
const HALF_W = AW / 2, HALF_H = AH / 2, HALF_D = AD / 2;

// ==================== GLASS TANK ====================
function createTank() {
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xaaddff,
    transparent: true,
    opacity: 0.12,
    transmission: 0.95,
    roughness: 0.05,
    metalness: 0.0,
    side: THREE.DoubleSide,
    depthWrite: false
  });

  // Front & Back
  const frontGeo = new THREE.PlaneGeometry(AW, AH);
  const front = new THREE.Mesh(frontGeo, glassMat);
  front.position.z = HALF_D;
  scene.add(front);

  const back = new THREE.Mesh(frontGeo, glassMat);
  back.position.z = -HALF_D;
  back.rotation.y = Math.PI;
  scene.add(back);

  // Left & Right
  const sideGeo = new THREE.PlaneGeometry(AD, AH);
  const left = new THREE.Mesh(sideGeo, glassMat);
  left.position.x = -HALF_W;
  left.rotation.y = Math.PI / 2;
  scene.add(left);

  const right = new THREE.Mesh(sideGeo, glassMat);
  right.position.x = HALF_W;
  right.rotation.y = -Math.PI / 2;
  scene.add(right);

  // Top
  const topGeo = new THREE.PlaneGeometry(AW, AD);
  const top = new THREE.Mesh(topGeo, glassMat);
  top.position.y = HALF_H;
  top.rotation.x = -Math.PI / 2;
  scene.add(top);

  // Bottom glass
  const bot = new THREE.Mesh(topGeo, glassMat);
  bot.position.y = -HALF_H;
  bot.rotation.x = Math.PI / 2;
  scene.add(bot);

  // Wireframe edges
  const edgesGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(AW, AH, AD));
  const edgesMat = new THREE.LineBasicMaterial({ color: 0x336699, transparent: true, opacity: 0.4 });
  const edges = new THREE.LineSegments(edgesGeo, edgesMat);
  scene.add(edges);
}
createTank();

// ==================== SAND FLOOR ====================
function createSand() {
  const sandGeo = new THREE.PlaneGeometry(AW, AD, 80, 80);
  const positions = sandGeo.attributes.position;
  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i);
    const y = positions.getY(i);
    positions.setZ(i, (Math.sin(x * 0.5) * Math.cos(y * 0.7) * 0.3 +
                       Math.sin(x * 1.2 + y * 0.8) * 0.15 +
                       Math.random() * 0.08) * 0.5);
  }
  sandGeo.computeVertexNormals();

  const sandMat = new THREE.MeshStandardMaterial({
    color: 0xd4a56a,
    roughness: 0.9,
    metalness: 0.0
  });
  const sand = new THREE.Mesh(sandGeo, sandMat);
  sand.rotation.x = -Math.PI / 2;
  sand.position.y = -HALF_H + 0.05;
  sand.receiveShadow = true;
  scene.add(sand);
}
createSand();

// ==================== ROCKS ====================
const rocks = [];
function createRocks() {
  for (let i = 0; i < 8; i++) {
    const geo = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.2, 1);
    const pos = geo.attributes.position;
    for (let j = 0; j < pos.count; j++) {
      pos.setX(j, pos.getX(j) + (Math.random() - 0.5) * 0.4);
      pos.setY(j, pos.getY(j) + (Math.random() - 0.5) * 0.4);
      pos.setZ(j, pos.getZ(j) + (Math.random() - 0.5) * 0.4);
    }
    geo.computeVertexNormals();

    const shade = 0.3 + Math.random() * 0.3;
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(shade, shade * 0.9, shade * 0.7),
      roughness: 0.85,
      metalness: 0.05
    });
    const rock = new THREE.Mesh(geo, mat);
    rock.position.set(
      (Math.random() - 0.5) * (AW - 6),
      -HALF_H + 0.6 + Math.random() * 0.5,
      (Math.random() - 0.5) * (AD - 4)
    );
    rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    rock.castShadow = true;
    rock.receiveShadow = true;
    scene.add(rock);
    rocks.push(rock);
  }
}
createRocks();

// ==================== SEAWEED ====================
const seaweeds = [];
function createSeaweed(x, z, height, color) {
  const points = [];
  const segments = 12;
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    points.push(new THREE.Vector3(
      Math.sin(t * Math.PI * 2.5) * 0.4 * t,
      t * height,
      Math.cos(t * Math.PI * 1.8) * 0.3 * t
    ));
  }
  const curve = new THREE.CatmullRomCurve3(points);
  const tubeGeo = new THREE.TubeGeometry(curve, 20, 0.08 + Math.random() * 0.06, 5, false);
  const mat = new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.7,
    metalness: 0.0,
    transparent: true,
    opacity: 0.85
  });
  const mesh = new THREE.Mesh(tubeGeo, mat);
  mesh.position.set(x, -HALF_H, z);
  mesh.castShadow = true;
  scene.add(mesh);
  seaweeds.push({ mesh, baseY: -HALF_H, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 });
}

for (let i = 0; i < 12; i++) {
  const x = (Math.random() - 0.5) * (AW - 4);
  const z = (Math.random() - 0.5) * (AD - 4);
  const h = 4 + Math.random() * 8;
  const greens = [0x1a6b3a, 0x2d8a4e, 0x1f5f3f, 0x3a9b5c, 0x0d4a2a];
  createSeaweed(x, z, h, greens[Math.floor(Math.random() * greens.length)]);
}

// ==================== FISH COLORS ====================
const FISH_COLORS = [
  { body: 0xff6600, fin: 0xff8833, belly: 0xffcc88 },
  { body: 0x2266ff, fin: 0x4488ff, belly: 0x88bbff },
  { body: 0xff3300, fin: 0xff6644, belly: 0xffaa88 },
  { body: 0x9933ff, fin: 0xbb55ff, belly: 0xddaaff },
  { body: 0xcc0000, fin: 0xff2222, belly: 0xff8888 },
  { body: 0x22aa22, fin: 0x44cc44, belly: 0x88ff88 },
  { body: 0xff66aa, fin: 0xff88cc, belly: 0xffccdd },
  { body: 0xffaa00, fin: 0xffcc33, belly: 0xffeeaa }
];

// ==================== FISH CREATION ====================
const fishArray = [];
const foodArray = [];
const bubbleArray = [];

function createFishModel(colorScheme, scale) {
  const group = new THREE.Group();

  // Body - elongated sphere
  const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
  bodyGeo.scale(1.6, 0.85, 0.6);
  const bodyMat = new THREE.MeshStandardMaterial({
    color: colorScheme.body,
    roughness: 0.3,
    metalness: 0.1
  });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.castShadow = true;
  group.add(body);

  // Belly (lighter underside)
  const bellyGeo = new THREE.SphereGeometry(0.95, 12, 8);
  bellyGeo.scale(1.4, 0.5, 0.5);
  const bellyMat = new THREE.MeshStandardMaterial({
    color: colorScheme.belly,
    roughness: 0.4,
    metalness: 0.05
  });
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.position.y = -0.25;
  group.add(belly);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.15, 8, 8);
  const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilGeo = new THREE.SphereGeometry(0.08, 8, 8);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

  const leftEye = new THREE.Mesh(eyeGeo, eyeWhiteMat);
  leftEye.position.set(0.8, 0.2, 0.45);
  group.add(leftEye);
  const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
  leftPupil.position.set(0.92, 0.2, 0.5);
  group.add(leftPupil);

  const rightEye = new THREE.Mesh(eyeGeo, eyeWhiteMat);
  rightEye.position.set(0.8, 0.2, -0.45);
  group.add(rightEye);
  const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
  rightPupil.position.set(0.92, 0.2, -0.5);
  group.add(rightPupil);

  // Tail
  const tailGroup = new THREE.Group();
  tailGroup.position.set(-1.5, 0, 0);
  const tailGeo = new THREE.SphereGeometry(0.5, 8, 6);
  tailGeo.scale(0.4, 1.2, 0.3);
  const tailMat = new THREE.MeshStandardMaterial({
    color: colorScheme.fin,
    roughness: 0.35,
    metalness: 0.05,
    transparent: true,
    opacity: 0.9
  });
  const tail = new THREE.Mesh(tailGeo, tailMat);
  tail.position.x = -0.2;
  tailGroup.add(tail);
  group.add(tailGroup);

  // Dorsal fin (top)
  const dorsalGeo = new THREE.SphereGeometry(0.4, 6, 6);
  dorsalGeo.scale(0.6, 0.2, 1.2);
  const dorsalMat = new THREE.MeshStandardMaterial({
    color: colorScheme.fin,
    roughness: 0.4,
    transparent: true,
    opacity: 0.75
  });
  const dorsalFin = new THREE.Mesh(dorsalGeo, dorsalMat);
  dorsalFin.position.set(-0.1, 0.65, 0);
  group.add(dorsalFin);

  // Left pectoral fin
  const pectoralGeo = new THREE.SphereGeometry(0.3, 6, 6);
  pectoralGeo.scale(0.5, 0.15, 1.0);
  const leftFin = new THREE.Mesh(pectoralGeo, dorsalMat.clone());
  leftFin.position.set(0.2, -0.1, 0.55);
  leftFin.rotation.z = -0.3;
  group.add(leftFin);

  // Right pectoral fin
  const rightFin = new THREE.Mesh(pectoralGeo, dorsalMat.clone());
  rightFin.position.set(0.2, -0.1, -0.55);
  rightFin.rotation.z = 0.3;
  group.add(rightFin);

  // Anal fin (bottom)
  const analGeo = new THREE.SphereGeometry(0.3, 6, 6);
  analGeo.scale(0.5, 0.15, 0.8);
  const analFin = new THREE.Mesh(analGeo, dorsalMat.clone());
  analFin.position.set(-0.5, -0.55, 0);
  group.add(analFin);

  group.scale.setScalar(scale);

  return { group, tail: tailGroup, leftFin, rightFin, dorsalFin, analFin };
}

function addFish(customPos) {
  const colorScheme = FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)];
  const scale = 0.6 + Math.random() * 0.6;
  const fishData = createFishModel(colorScheme, scale);

  const pos = customPos || {
    x: (Math.random() - 0.5) * (AW - 6),
    y: (Math.random() - 0.5) * (AH - 6),
    z: (Math.random() - 0.5) * (AD - 6)
  };

  fishData.group.position.set(pos.x, pos.y, pos.z);
  scene.add(fishData.group);

  const velocity = new THREE.Vector3(
    (Math.random() - 0.5) * 2,
    (Math.random() - 0.5) * 1,
    (Math.random() - 0.5) * 2
  ).normalize().multiplyScalar(1 + Math.random() * 1.5);

  fishArray.push({
    mesh: fishData.group,
    tail: fishData.tail,
    leftFin: fishData.leftFin,
    rightFin: fishData.rightFin,
    dorsalFin: fishData.dorsalFin,
    analFin: fishData.analFin,
    velocity: velocity,
    speed: 1 + Math.random() * 2,
    tailSpeed: 3 + Math.random() * 4,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 3 + Math.random() * 1.5,
    scale: scale,
    growTimer: 0
  });

  document.getElementById('fishCount').textContent = fishArray.length;
}

// Create initial 15 fish
for (let i = 0; i < 15; i++) addFish();

// ==================== BUBBLES ====================
function createBubble(x, y, z, radius) {
  const r = radius || 0.1 + Math.random() * 0.2;
  const geo = new THREE.SphereGeometry(r, 8, 8);
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0xaaddff,
    transparent: true,
    opacity: 0.25,
    transmission: 0.9,
    roughness: 0.0,
    metalness: 0.0,
    depthWrite: false
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  scene.add(mesh);

  bubbleArray.push({
    mesh: mesh,
    speed: 1.5 + Math.random() * 2,
    wobblePhase: Math.random() * Math.PI * 2,
    wobbleSpeed: 1 + Math.random() * 2,
    wobbleAmp: 0.3 + Math.random() * 0.5,
    radius: r
  });
}

// Initial 30 bubbles
for (let i = 0; i < 30; i++) {
  createBubble(
    (Math.random() - 0.5) * (AW - 4),
    -HALF_H + Math.random() * AH,
    (Math.random() - 0.5) * (AD - 4)
  );
}

function addBubbles() {
  for (let i = 0; i < 10; i++) {
    createBubble(
      (Math.random() - 0.5) * (AW - 4),
      -HALF_H + Math.random() * 2,
      (Math.random() - 0.5) * (AD - 4)
    );
  }
}

// ==================== FOOD ====================
function spawnFood(x, y, z) {
  const geo = new THREE.SphereGeometry(0.2, 8, 8);
  const mat = new THREE.MeshStandardMaterial({
    color: 0xcc8833,
    roughness: 0.7,
    metalness: 0.0
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  scene.add(mesh);

  foodArray.push({
    mesh: mesh,
    vy: -0.5 - Math.random() * 0.5,
    vx: (Math.random() - 0.5) * 0.3,
    vz: (Math.random() - 0.5) * 0.3,
    alive: true
  });

  document.getElementById('foodCount').textContent = foodArray.length;
}

// ==================== RAYCASTER FOR CLICK ====================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', (event) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);

  // Check intersection with tank interior plane at click direction
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion), 0);
  const target = new THREE.Vector3();
  const intersects = raycaster.ray.intersectPlane(plane, target);

  if (intersects && target) {
    // Clamp to tank bounds
    const fx = Math.max(-HALF_W + 1, Math.min(HALF_W - 1, target.x));
    const fy = Math.max(-HALF_H + 1, Math.min(HALF_H - 1, target.y));
    const fz = Math.max(-HALF_D + 1, Math.min(HALF_D - 1, target.z));
    spawnFood(fx, HALF_H - 1, fz);
  }
});

// ==================== TOGGLE LIGHT ====================
function toggleLight() {
  lightOn = !lightOn;
  dirLight.intensity = lightOn ? 0.8 : 0.1;
  pointLight1.intensity = lightOn ? 0.6 : 0.15;
  pointLight2.intensity = lightOn ? 0.5 : 0.1;
  ambientLight.intensity = lightOn ? 0.4 : 0.15;
}

// ==================== FPS COUNTER ====================
let frameCount = 0;
let lastFpsTime = performance.now();
let currentFps = 60;

// ==================== ANIMATION LOOP ====================
let prevTime = performance.now();

function animate() {
  requestAnimationFrame(animate);

  const now = performance.now();
  const dt = Math.min((now - prevTime) / 1000, 0.05);
  prevTime = now;

  // FPS calculation
  frameCount++;
  if (now - lastFpsTime >= 500) {
    currentFps = Math.round(frameCount / ((now - lastFpsTime) / 1000));
    document.getElementById('fpsCounter').textContent = currentFps;
    frameCount = 0;
    lastFpsTime = now;
  }

  controls.update();

  // ==================== UPDATE FISH ====================
  for (let i = 0; i < fishArray.length; i++) {
    const fish = fishArray[i];
    const pos = fish.mesh.position;

    // --- Collision avoidance ---
    for (let j = 0; j < fishArray.length; j++) {
      if (i === j) continue;
      const other = fishArray[j];
      const diff = new THREE.Vector3().subVectors(pos, other.mesh.position);
      const dist = diff.length();
      if (dist < fish.avoidanceRadius && dist > 0.01) {
        const force = diff.normalize().multiplyScalar((fish.avoidanceRadius - dist) / fish.avoidanceRadius * 0.5);
        fish.velocity.add(force);
      }
    }

    // --- Wall avoidance ---
    const margin = 2;
    const turnStrength = 0.8;
    if (pos.x < -HALF_W + margin) fish.velocity.x += turnStrength * dt;
    if (pos.x > HALF_W - margin) fish.velocity.x -= turnStrength * dt;
    if (pos.y < -HALF_H + margin) fish.velocity.y += turnStrength * dt;
    if (pos.y > HALF_H - margin) fish.velocity.y -= turnStrength * dt;
    if (pos.z < -HALF_D + margin) fish.velocity.z += turnStrength * dt;
    if (pos.z > HALF_D - margin) fish.velocity.z -= turnStrength * dt;

    // --- Random wandering ---
    fish.phase += dt * 0.3;
    if (Math.sin(fish.phase * 1.7) > 0.95) {
      fish.velocity.x += (Math.random() - 0.5) * 0.5;
      fish.velocity.z += (Math.random() - 0.5) * 0.5;
    }

    // --- Food chasing ---
    if (!fish.targetFood || !fish.targetFood.alive) {
      fish.targetFood = null;
      // Find nearest food
      let minDist = 15;
      for (const food of foodArray) {
        if (!food.alive) continue;
        const d = pos.distanceTo(food.mesh.position);
        if (d < minDist) {
          minDist = d;
          fish.targetFood = food;
        }
      }
    }

    if (fish.targetFood && fish.targetFood.alive) {
      const foodDir = new THREE.Vector3().subVectors(fish.targetFood.mesh.position, pos);
      const foodDist = foodDir.length();
      if (foodDist < 0.5) {
        // Eat food
        fish.targetFood.alive = false;
        scene.remove(fish.targetFood.mesh);
        fish.targetFood = null;
        // Grow
        const growAmount = 1.05;
        fish.scale *= growAmount;
        fish.mesh.scale.setScalar(fish.scale);
        document.getElementById('foodCount').textContent = foodArray.filter(f => f.alive).length;
      } else {
        foodDir.normalize();
        fish.velocity.lerp(foodDir.multiplyScalar(fish.speed * 2.5), 0.02);
      }
    }

    // --- Normalize velocity ---
    const spd = fish.velocity.length();
    if (spd > 0.01) {
      fish.velocity.normalize().multiplyScalar(Math.min(spd, fish.speed * 1.5));
    }

    // --- Move ---
    pos.addScaledVector(fish.velocity, dt);

    // --- Rotate fish to face direction ---
    if (spd > 0.05) {
      const targetDir = fish.velocity.clone().normalize();
      const targetQuat = new THREE.Quaternion();
      const lookMatrix = new THREE.Matrix4().lookAt(
        new THREE.Vector3(0, 0, 0),
        targetDir,
        new THREE.Vector3(0, 1, 0)
      );
      targetQuat.setFromRotationMatrix(lookMatrix);
      fish.mesh.quaternion.slerp(targetQuat, 0.08);
    }

    // --- Animate tail ---
    const tailAngle = Math.sin(now * 0.001 * fish.tailSpeed + fish.phase) * 0.4;
    fish.tail.rotation.y = tailAngle;

    // --- Animate fins ---
    const finAngle = Math.sin(now * 0.001 * fish.tailSpeed * 1.3 + fish.phase + 1) * 0.25;
    fish.leftFin.rotation.z = -0.3 + finAngle;
    fish.rightFin.rotation.z = 0.3 - finAngle;

    const dorsalAngle = Math.sin(now * 0.001 * fish.tailSpeed * 0.8 + fish.phase) * 0.15;
    fish.dorsalFin.rotation.z = dorsalAngle;
    fish.analFin.rotation.z = -dorsalAngle;
  }

  // Remove dead food
  for (let i = foodArray.length - 1; i >= 0; i--) {
    const food = foodArray[i];
    if (!food.alive) {
      foodArray.splice(i, 1);
      continue;
    }
    // Gravity
    food.mesh.position.y += food.vy * dt;
    food.mesh.position.x += food.vx * dt;
    food.mesh.position.z += food.vz * dt;

    // Hit bottom
    if (food.mesh.position.y < -HALF_H + 0.3) {
      food.alive = false;
      scene.remove(food.mesh);
      foodArray.splice(i, 1);
      document.getElementById('foodCount').textContent = foodArray.length;
    }
  }

  // ==================== UPDATE BUBBLES ====================
  for (const bubble of bubbleArray) {
    bubble.mesh.position.y += bubble.speed * dt;
    bubble.wobblePhase += bubble.wobbleSpeed * dt;
    bubble.mesh.position.x += Math.sin(bubble.wobblePhase) * bubble.wobbleAmp * dt;
    bubble.mesh.position.z += Math.cos(bubble.wobblePhase * 0.7) * bubble.wobbleAmp * 0.5 * dt;

    // Reset when reaching surface
    if (bubble.mesh.position.y > HALF_H - 0.5) {
      bubble.mesh.position.y = -HALF_H + Math.random() * 1;
      bubble.mesh.position.x = (Math.random() - 0.5) * (AW - 4);
      bubble.mesh.position.z = (Math.random() - 0.5) * (AD - 4);
    }
  }

  // ==================== ANIMATE SEAWEED ====================
  for (const sw of seaweeds) {
    sw.phase += sw.speed * dt;
    sw.mesh.rotation.x = Math.sin(sw.phase) * 0.08;
    sw.mesh.rotation.z = Math.cos(sw.phase * 0.7) * 0.06;
  }

  // ==================== ANIMATE POINT LIGHTS ====================
  pointLight1.position.x = Math.sin(now * 0.0003) * 12;
  pointLight1.position.z = Math.cos(now * 0.0004) * 8;
  pointLight2.position.x = Math.cos(now * 0.00035) * 10;
  pointLight2.position.z = Math.sin(now * 0.0003) * 8;

  renderer.render(scene, camera);
}

animate();

// ==================== RESIZE ====================
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

## Что реализовано

### 🐠 Рыбки (15 штук)
- **Анатомически детализированные**: вытянутое тело (масштабированная сфера), брюшко светлее, глаза со зрачками, хвост, спинной плавник, два грудных плавника, анальный плавник
- **8 цветовых схем**: оранжевая, синяя, жёлто-красная, фиолетовая, красная, зелёная, розовая, золотая
- **Разнообразие размеров**: случайный масштаб 0.6–1.2
- **Плавная анимация**: мах хвоста, движение всех плавников, поворот в направлении движения

### 🧠 ИИ-поведение
- **Избегание столкновений** между рыбками
- **Отражение от стен** аквариума
- **Случайное блуждание** с плавными изменениями курса
- **Преследование корма** в радиусе 15 единиц
- **Рост на 5%** после поедания

### 🌊 Окружение
- **Стеклянный аквариум** 36×24×20 с transmission-эффектом и wireframe-рамкой
- **Песчаное дно** с процедурными неровностями
- **8 декоративных камней** (деформированные додекаэдры с тенями)
- **12 кустов водорослей** (TubeGeometry + покачивание)

### 💭 Пузыри (30 штук)
- Прозрачные сферы с эффектом стекла
- Движение вверх с синусоидальным покачиванием
- Сброс на дно при достижении поверхности

### 🍽️ Кормление
- Клик по аквариуму → корм падает с гравитацией
- Рыбки атакуют ближайший корм
- Съеденный корм удаляется, рыбка растёт

### 💡 Освещение
- AmbientLight + DirectionalLight с мягкими тенями (2048×2048)
- 2 анимированных PointLight (голубые)
- Кнопка переключения света

### 🎮 OrbitControls
- Вращение / панорамирование / зум с damping'ом