```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Аквариум</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; background: #0a1628; font-family: 'Segoe UI', Tahoma, sans-serif; }
canvas { display: block; }

.panel {
  position: absolute;
  background: rgba(10, 25, 50, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(100, 180, 255, 0.2);
  border-radius: 14px;
  padding: 18px 22px;
  color: #c8e6ff;
  box-shadow: 0 8px 32px rgba(0, 40, 100, 0.4), inset 0 1px 0 rgba(255,255,255,0.05);
  transition: all 0.3s ease;
}
.panel:hover {
  border-color: rgba(100, 180, 255, 0.4);
  box-shadow: 0 8px 32px rgba(0, 60, 140, 0.5), inset 0 1px 0 rgba(255,255,255,0.08);
}

#info-panel {
  top: 20px; left: 20px;
  max-width: 280px;
}
#info-panel h1 {
  font-size: 22px;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #4fc3f7, #0288d1, #4fc3f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
}
#info-panel p {
  font-size: 12.5px;
  line-height: 1.7;
  color: #8ab4d8;
  margin-bottom: 4px;
}
#info-panel .highlight { color: #4fc3f7; font-weight: 600; }

#stats-panel {
  top: 20px; right: 20px;
  text-align: right;
  min-width: 180px;
}
#stats-panel .stat-row {
  font-size: 14px;
  margin-bottom: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
#stats-panel .stat-value {
  color: #4fc3f7;
  font-weight: 700;
  font-size: 16px;
  font-variant-numeric: tabular-nums;
}

.btn-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 14px;
}
.btn {
  background: linear-gradient(135deg, rgba(2, 136, 209, 0.6), rgba(79, 195, 247, 0.3));
  border: 1px solid rgba(79, 195, 247, 0.35);
  color: #b8e0ff;
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.25s ease;
  text-align: center;
  letter-spacing: 0.3px;
  position: relative;
  overflow: hidden;
}
.btn::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.5s ease;
}
.btn:hover {
  background: linear-gradient(135deg, rgba(2, 136, 209, 0.85), rgba(79, 195, 247, 0.55));
  border-color: rgba(79, 195, 247, 0.6);
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(2, 136, 209, 0.3);
}
.btn:hover::before { left: 100%; }
.btn:active { transform: translateY(0); }

#light-btn.active {
  background: linear-gradient(135deg, rgba(255, 183, 77, 0.6), rgba(255, 138, 101, 0.3));
  border-color: rgba(255, 183, 77, 0.4);
  color: #ffe0b2;
}

@media (max-width: 768px) {
  .panel { padding: 12px 14px; border-radius: 10px; }
  #info-panel { max-width: 220px; top: 10px; left: 10px; }
  #info-panel h1 { font-size: 16px; }
  #info-panel p { font-size: 11px; }
  #stats-panel { top: 10px; right: 10px; }
  .btn { padding: 8px 12px; font-size: 11px; }
}
</style>
</head>
<body>

<div class="panel" id="info-panel">
  <h1>🐠 3D Аквариум</h1>
  <p><span class="highlight">ЛКМ + движение</span> — вращение камеры</p>
  <p><span class="highlight">ПКМ + движение</span> — перемещение</p>
  <p><span class="highlight">Колёсико</span> — масштаб</p>
  <p><span class="highlight">Клик по воде</span> — покормить рыбок</p>
  <div class="btn-group">
    <button class="btn" id="add-fish-btn">🐟 Добавить рыбку</button>
    <button class="btn" id="bubbles-btn">💨 Больше пузырей</button>
    <button class="btn" id="light-btn">💡 Свет</button>
  </div>
</div>

<div class="panel" id="stats-panel">
  <div class="stat-row"><span>Рыбок:</span><span class="stat-value" id="fish-count">0</span></div>
  <div class="stat-row"><span>FPS:</span><span class="stat-value" id="fps-counter">0</span></div>
  <div class="stat-row"><span>Пузырей:</span><span class="stat-value" id="bubble-count">0</span></div>
  <div class="stat-row"><span>Корма:</span><span class="stat-value" id="food-count">0</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ==================== SCENE SETUP ====================
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 12, 42);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
document.body.appendChild(renderer.domElement);

// Background gradient via a large sphere
const bgGeo = new THREE.SphereGeometry(90, 32, 32);
const bgMat = new THREE.ShaderMaterial({
  side: THREE.BackSide,
  uniforms: {
    topColor: { value: new THREE.Color(0x0a1e3d) },
    bottomColor: { value: new THREE.Color(0x1a5a8a) }
  },
  vertexShader: `
    varying vec3 vWorldPos;
    void main() {
      vec4 wp = modelMatrix * vec4(position, 1.0);
      vWorldPos = wp.xyz;
      gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 topColor;
    uniform vec3 bottomColor;
    varying vec3 vWorldPos;
    void main() {
      float t = smoothstep(-50.0, 50.0, vWorldPos.y);
      gl_FragColor = vec4(mix(bottomColor, topColor, t), 1.0);
    }
  `
});
scene.add(new THREE.Mesh(bgGeo, bgMat));

// ==================== CONTROLS ====================
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.target.set(0, 4, 0);

// ==================== LIGHTING ====================
const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffeedd, 0.8);
dirLight.position.set(15, 30, 10);
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

const pointLight1 = new THREE.PointLight(0x44aaff, 0.6, 50);
pointLight1.position.set(-10, 10, -5);
scene.add(pointLight1);

const pointLight2 = new THREE.PointLight(0x2266cc, 0.5, 50);
pointLight2.position.set(10, 8, 5);
scene.add(pointLight2);

let lightOn = true;

// ==================== AQUARIUM DIMENSIONS ====================
const AW = 36, AH = 24, AD = 20;
const halfW = AW / 2, halfH = AH / 2, halfD = AD / 2;

// ==================== GLASS TANK ====================
function createTank() {
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xaaddff,
    transparent: true,
    opacity: 0.12,
    roughness: 0.05,
    metalness: 0.0,
    transmission: 0.95,
    thickness: 0.5,
    side: THREE.DoubleSide,
    depthWrite: false
  });

  // Six faces
  const faces = [
    { w: AW, h: AH, pos: [0, halfH / 2, -halfD], rot: [0, 0, 0] },       // back
    { w: AW, h: AH, pos: [0, halfH / 2, halfD], rot: [0, 0, 0] },        // front
    { w: AD, h: AH, pos: [-halfW, halfH / 2, 0], rot: [0, Math.PI / 2, 0] }, // left
    { w: AD, h: AH, pos: [halfW, halfH / 2, 0], rot: [0, Math.PI / 2, 0] },  // right
    { w: AW, h: AD, pos: [0, 0, 0], rot: [-Math.PI / 2, 0, 0] },           // bottom (glass)
    { w: AW, h: AD, pos: [0, AH, 0], rot: [-Math.PI / 2, 0, 0] },          // top
  ];

  faces.forEach(f => {
    const geo = new THREE.PlaneGeometry(f.w, f.h);
    const mesh = new THREE.Mesh(geo, glassMat);
    mesh.position.set(...f.pos);
    mesh.rotation.set(...f.rot);
    scene.add(mesh);
  });

  // Wireframe edges
  const edgeGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(AW, AH, AD));
  const edgeMat = new THREE.LineBasicMaterial({ color: 0x4488aa, transparent: true, opacity: 0.4 });
  const edges = new THREE.LineSegments(edgeGeo, edgeMat);
  edges.position.y = halfH / 2;
  scene.add(edges);
}
createTank();

// ==================== SANDY BOTTOM ====================
function createSand() {
  const sandGeo = new THREE.PlaneGeometry(AW - 0.5, AD - 0.5, 80, 60);
  const positions = sandGeo.attributes.position;
  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i);
    const y = positions.getY(i);
    const noise = Math.sin(x * 0.3) * Math.cos(y * 0.4) * 0.3 +
                  Math.sin(x * 0.7 + 1.0) * Math.cos(y * 0.5 + 0.5) * 0.15;
    positions.setZ(i, noise);
  }
  sandGeo.computeVertexNormals();

  const sandMat = new THREE.MeshStandardMaterial({
    color: 0xd4a56a,
    roughness: 0.9,
    metalness: 0.0,
    flatShading: true
  });
  const sand = new THREE.Mesh(sandGeo, sandMat);
  sand.rotation.x = -Math.PI / 2;
  sand.position.y = 0.05;
  sand.receiveShadow = true;
  scene.add(sand);
}
createSand();

// ==================== ROCKS ====================
const rocks = [];
function createRocks() {
  for (let i = 0; i < 8; i++) {
    const rockGeo = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.2, 1);
    // Deform vertices
    const pos = rockGeo.attributes.position;
    for (let j = 0; j < pos.count; j++) {
      const x = pos.getX(j), y = pos.getY(j), z = pos.getZ(j);
      const noise = 1 + (Math.sin(x * 3.7 + i) * Math.cos(z * 2.3 + i * 0.5)) * 0.3;
      pos.setX(j, x * noise);
      pos.setY(j, y * (0.5 + Math.random() * 0.5));
      pos.setZ(j, z * noise);
    }
    rockGeo.computeVertexNormals();

    const shade = 0.3 + Math.random() * 0.3;
    const rockMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(shade * 0.7, shade * 0.65, shade * 0.55),
      roughness: 0.85,
      metalness: 0.05,
      flatShading: true
    });
    const rock = new THREE.Mesh(rockGeo, rockMat);
    rock.position.set(
      (Math.random() - 0.5) * (AW - 6),
      0.5 + Math.random() * 0.5,
      (Math.random() - 0.5) * (AD - 6)
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
function createSeaweed() {
  for (let i = 0; i < 12; i++) {
    const height = 4 + Math.random() * 6;
    const segments = 12 + Math.floor(Math.random() * 8);
    const points = [];
    for (let j = 0; j <= segments; j++) {
      const t = j / segments;
      const sway = Math.sin(t * Math.PI * 2.5) * (0.3 + t * 1.2);
      points.push(new THREE.Vector3(
        sway,
        t * height,
        Math.cos(t * Math.PI * 1.8) * 0.2 * t
      ));
    }
    const curve = new THREE.CatmullRomCurve3(points);
    const tubeGeo = new THREE.TubeGeometry(curve, segments, 0.08 + Math.random() * 0.06, 5, false);

    const greenShade = 0.15 + Math.random() * 0.25;
    const weedMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(greenShade * 0.3, greenShade, greenShade * 0.2),
      roughness: 0.7,
      metalness: 0.0,
      flatShading: true
    });
    const weed = new THREE.Mesh(tubeGeo, weedMat);
    weed.position.set(
      (Math.random() - 0.5) * (AW - 4),
      0,
      (Math.random() - 0.5) * (AD - 4)
    );
    weed.castShadow = true;
    weed.userData.phase = Math.random() * Math.PI * 2;
    weed.userData.swaySpeed = 0.5 + Math.random() * 1.0;
    scene.add(weed);
    seaweeds.push(weed);
  }
}
createSeaweed();

// ==================== FISH COLORS ====================
const FISH_COLORS = [
  { body: 0xff6622, fin: 0xff8844, belly: 0xffddbb },   // orange
  { body: 0x2266ff, fin: 0x4488ff, belly: 0xaaccff },   // blue
  { body: 0xffaa00, fin: 0xff4422, belly: 0xffeecc },   // yellow-red
  { body: 0xaa44ff, fin: 0xcc66ff, belly: 0xddbbff },   // purple
  { body: 0xff2244, fin: 0xff4466, belly: 0xffbbbb },   // red
  { body: 0x22aa44, fin: 0x44cc66, belly: 0xbbffcc },   // green
  { body: 0xff66aa, fin: 0xff88cc, belly: 0xffddff },   // pink
  { body: 0xffcc44, fin: 0xffdd66, belly: 0xffeedd },   // gold
];

// ==================== FISH CREATION ====================
const fishArray = [];

function createFish(colorIdx, scaleOverride) {
  const colors = FISH_COLORS[colorIdx % FISH_COLORS.length];
  const group = new THREE.Group();

  const scale = scaleOverride || (0.6 + Math.random() * 0.6);

  // Body - elongated sphere
  const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
  bodyGeo.scale(1.8, 1.0, 0.7);
  const bodyMat = new THREE.MeshStandardMaterial({
    color: colors.body,
    roughness: 0.3,
    metalness: 0.15,
    flatShading: false
  });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.castShadow = true;
  group.add(body);

  // Belly (lighter underside)
  const bellyGeo = new THREE.SphereGeometry(0.95, 12, 8);
  bellyGeo.scale(1.6, 0.5, 0.65);
  const bellyMat = new THREE.MeshStandardMaterial({
    color: colors.belly,
    roughness: 0.4,
    metalness: 0.1
  });
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.position.y = -0.35;
  belly.position.z = 0.05;
  group.add(belly);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.15, 8, 8);
  const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilGeo = new THREE.SphereGeometry(0.08, 8, 8);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

  [-1, 1].forEach(side => {
    const eye = new THREE.Mesh(eyeGeo, eyeWhiteMat);
    eye.position.set(0.6, 0.25, side * 0.55);
    group.add(eye);
    const pupil = new THREE.Mesh(pupilGeo, pupilMat);
    pupil.position.set(0.7, 0.25, side * 0.62);
    group.add(pupil);
  });

  // Tail
  const tailGroup = new THREE.Group();
  tailGroup.position.set(-1.5, 0, 0);
  const tailGeo = new THREE.BufferGeometry();
  const tailVerts = new Float32Array([
    0, 0, 0,
    -0.6, 0.5, 0.1,
    -0.6, -0.5, 0.1,
    0, 0, 0,
    -0.6, 0.5, -0.1,
    -0.6, -0.5, -0.1,
  ]);
  const tailIndices = [0, 1, 2, 0, 3, 4, 0, 5, 2, 0, 1, 4, 0, 3, 5];
  tailGeo.setAttribute('position', new THREE.BufferAttribute(tailVerts, 3));
  tailGeo.setIndex(tailIndices);
  tailGeo.computeVertexNormals();
  const tailMat = new THREE.MeshStandardMaterial({
    color: colors.fin,
    roughness: 0.35,
    metalness: 0.1,
    side: THREE.DoubleSide
  });
  const tail = new THREE.Mesh(tailGeo, tailMat);
  tailGroup.add(tail);
  group.add(tailGroup);

  // Top fin (dorsal)
  const topFinGroup = new THREE.Group();
  topFinGroup.position.set(0, 0.7, 0);
  const topFinGeo = new THREE.BufferGeometry();
  const tfVerts = new Float32Array([
    -0.5, 0, 0,
    0.5, 0, 0,
    0, 0.5, 0.05,
    0, 0.5, -0.05,
    -0.5, 0, 0,
    0, 0.5, -0.05,
  ]);
  topFinGeo.setAttribute('position', new THREE.BufferAttribute(tfVerts, 3));
  topFinGeo.setIndex([0, 1, 2, 0, 3, 4, 1, 2, 3, 4, 3, 5]);
  topFinGeo.computeVertexNormals();
  const topFinMat = new THREE.MeshStandardMaterial({
    color: colors.fin,
    roughness: 0.4,
    metalness: 0.05,
    side: THREE.DoubleSide
  });
  const topFin = new THREE.Mesh(topFinGeo, topFinMat);
  topFinGroup.add(topFin);
  group.add(topFinGroup);

  // Side fins (pectoral)
  const leftFinGroup = new THREE.Group();
  leftFinGroup.position.set(0.2, -0.1, 0.55);
  const sideFinGeo = new THREE.BufferGeometry();
  const sfVerts = new Float32Array([
    0, 0, 0,
    0.4, -0.3, 0.05,
    0.4, 0.1, 0.05,
    0, 0, 0,
    0.4, 0.1, -0.05,
    0.4, -0.3, -0.05,
  ]);
  sideFinGeo.setAttribute('position', new THREE.BufferAttribute(sfVerts, 3));
  sideFinGeo.setIndex([0, 1, 2, 0, 3, 4, 1, 5, 4, 1, 5, 2]);
  sideFinGeo.computeVertexNormals();
  const sideFinMat = new THREE.MeshStandardMaterial({
    color: colors.fin,
    roughness: 0.4,
    metalness: 0.05,
    side: THREE.DoubleSide
  });
  const leftFin = new THREE.Mesh(sideFinGeo, sideFinMat);
  leftFinGroup.add(leftFin);
  group.add(leftFinGroup);

  const rightFinGroup = new THREE.Group();
  rightFinGroup.position.set(0.2, -0.1, -0.55);
  const rightFin = new THREE.Mesh(sideFinGeo.clone(), sideFinMat.clone());
  rightFinGroup.add(rightFin);
  group.add(rightFinGroup);

  group.scale.setScalar(scale);

  // Random position inside tank
  group.position.set(
    (Math.random() - 0.5) * (AW - 6),
    2 + Math.random() * (AH - 6),
    (Math.random() - 0.5) * (AD - 6)
  );

  scene.add(group);

  const velocity = new THREE.Vector3(
    (Math.random() - 0.5) * 2,
    (Math.random() - 0.5) * 0.5,
    (Math.random() - 0.5) * 2
  ).normalize().multiplyScalar(1.5 + Math.random() * 1.5);

  return {
    mesh: group,
    tail: tailGroup,
    topFin: topFinGroup,
    leftFin: leftFinGroup,
    rightFin: rightFinGroup,
    body: body,
    velocity: velocity,
    speed: 1.5 + Math.random() * 1.5,
    tailSpeed: 3 + Math.random() * 4,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 3.5,
    scale: scale,
    colorIdx: colorIdx
  };
}

// Create initial 15 fish
for (let i = 0; i < 15; i++) {
  fishArray.push(createFish(i % FISH_COLORS.length));
}

// ==================== BUBBLES ====================
const bubbleArray = [];

function createBubble(startY) {
  const size = 0.08 + Math.random() * 0.15;
  const bubbleGeo = new THREE.SphereGeometry(size, 8, 8);
  const bubbleMat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.25,
    roughness: 0.0,
    metalness: 0.0,
    transmission: 0.9,
    thickness: 0.1,
    depthWrite: false
  });
  const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
  bubble.position.set(
    (Math.random() - 0.5) * (AW - 4),
    startY !== undefined ? startY : Math.random() * AH,
    (Math.random() - 0.5) * (AD - 4)
  );
  bubble.userData.speed = 1.5 + Math.random() * 2;
  bubble.userData.phaseX = Math.random() * Math.PI * 2;
  bubble.userData.phaseZ = Math.random() * Math.PI * 2;
  bubble.userData.swayAmpX = 0.3 + Math.random() * 0.5;
  bubble.userData.swayAmpZ = 0.2 + Math.random() * 0.4;
  bubble.userData.baseX = bubble.position.x;
  bubble.userData.baseZ = bubble.position.z;
  scene.add(bubble);
  bubbleArray.push(bubble);
}

for (let i = 0; i < 30; i++) {
  createBubble();
}

// ==================== FOOD SYSTEM ====================
const foodArray = [];

function spawnFood(x, y, z) {
  const foodGeo = new THREE.SphereGeometry(0.15, 8, 8);
  const foodMat = new THREE.MeshStandardMaterial({
    color: 0xdd8833,
    roughness: 0.6,
    metalness: 0.1,
    emissive: 0x442200,
    emissiveIntensity: 0.3
  });
  const food = new THREE.Mesh(foodGeo, foodMat);
  food.position.set(x, y, z);
  food.userData.vy = -2 - Math.random() * 2;
  food.userData.vx = (Math.random() - 0.5) * 0.5;
  food.userData.vz = (Math.random() - 0.5) * 0.5;
  food.userData.alive = true;
  scene.add(food);
  foodArray.push(food);
}

// ==================== RAYCASTER FOR CLICKING ====================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', (event) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);

  // Check intersection with tank interior planes
  // We'll just spawn food at a point along the ray inside the tank
  const tankPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), halfD);
  const intersect = new THREE.Vector3();
  raycaster.ray.intersectPlane(tankPlane, intersect);

  if (intersect) {
    // Clamp to tank bounds
    const fx = Math.max(-halfW + 1, Math.min(halfW - 1, intersect.x));
    const fy = Math.max(1, Math.min(AH - 1, intersect.y));
    const fz = Math.max(-halfD + 1, Math.min(halfD - 1, intersect.z));
    spawnFood(fx, fy, fz);
  }
});

// ==================== BUTTONS ====================
document.getElementById('add-fish-btn').addEventListener('click', () => {
  const ci = Math.floor(Math.random() * FISH_COLORS.length);
  fishArray.push(createFish(ci));
});

document.getElementById('bubbles-btn').addEventListener('click', () => {
  for (let i = 0; i < 10; i++) {
    createBubble(0);
  }
});

document.getElementById('light-btn').addEventListener('click', function() {
  lightOn = !lightOn;
  dirLight.intensity = lightOn ? 0.8 : 0.15;
  pointLight1.intensity = lightOn ? 0.6 : 0.1;
  pointLight2.intensity = lightOn ? 0.5 : 0.05;
  this.classList.toggle('active', lightOn);
  this.textContent = lightOn ? '💡 Свет' : '🌑 Темнота';
});

// ==================== ANIMATION LOOP ====================
let lastTime = performance.now();
let frameCount = 0;
let fpsTime = 0;
let fps = 0;

function animate() {
  requestAnimationFrame(animate);

  const now = performance.now();
  let dt = (now - lastTime) / 1000;
  lastTime = now;
  dt = Math.min(dt, 0.05); // cap delta

  // FPS calculation
  frameCount++;
  fpsTime += dt;
  if (fpsTime >= 0.5) {
    fps = Math.round(frameCount / fpsTime);
    document.getElementById('fps-counter').textContent = fps;
    frameCount = 0;
    fpsTime = 0;
  }

  // ---- Update fish ----
  for (let i = 0; i < fishArray.length; i++) {
    const fish = fishArray[i];
    const pos = fish.mesh.position;
    const vel = fish.velocity;

    // ---- Avoidance from other fish ----
    for (let j = 0; j < fishArray.length; j++) {
      if (i === j) continue;
      const other = fishArray[j];
      const dx = pos.x - other.mesh.position.x;
      const dy = pos.y - other.mesh.position.y;
      const dz = pos.z - other.mesh.position.z;
      const distSq = dx * dx + dy * dy + dz * dz;
      const avoidDist = fish.avoidanceRadius + other.avoidanceRadius;
      if (distSq < avoidDist * avoidDist && distSq > 0.01) {
        const dist = Math.sqrt(distSq);
        const force = (avoidDist - dist) / avoidDist * 0.5;
        vel.x += (dx / dist) * force;
        vel.y += (dy / dist) * force;
        vel.z += (dz / dist) * force;
      }
    }

    // ---- Wall reflection ----
    const margin = 1.5;
    ['x', 'y', 'z'].forEach(axis => {
      let bound;
      if (axis === 'x') bound = halfW - margin;
      else if (axis === 'y') bound = halfH - margin;
      else bound = halfD - margin;

      if (pos[axis] > bound) {
        vel[axis] -= 0.8;
        pos[axis] = bound;
      }
      if (pos[axis] < -bound) {
        vel[axis] += 0.8;
        pos[axis] = -bound;
      }
    });

    // Keep above sand
    if (pos.y < 1.5) {
      vel.y += 1.5;
      pos.y = 1.5;
    }

    // ---- Random wandering ----
    fish.phase += dt * (0.3 + Math.random() * 0.1);
    if (Math.random() < 0.008) {
      vel.x += (Math.random() - 0.5) * 1.5;
      vel.y += (Math.random() - 0.5) * 0.5;
      vel.z += (Math.random() - 0.5) * 1.5;
    }

    // ---- Food chasing ----
    if (!fish.targetFood || !fish.targetFood.userData.alive) {
      fish.targetFood = null;
      // Look for nearest food
      let minDist = 15;
      for (const food of foodArray) {
        if (!food.userData.alive) continue;
        const d = pos.distanceTo(food.position);
        if (d < minDist) {
          minDist = d;
          fish.targetFood = food;
        }
      }
    }

    if (fish.targetFood && fish.targetFood.userData.alive) {
      const foodPos = fish.targetFood.position;
      const dx = foodPos.x - pos.x;
      const dy = foodPos.y - pos.y;
      const dz = foodPos.z - pos.z;
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

      if (dist < 0.6) {
        // Eat!
        fish.targetFood.userData.alive = false;
        scene.remove(fish.targetFood);
        fish.targetFood = null;
        // Grow
        fish.scale *= 1.05;
        fish.mesh.scale.setScalar(fish.scale);
      } else {
        // Steer toward food
        const steerStrength = 0.4;
        vel.x += (dx / dist) * steerStrength;
        vel.y += (dy / dist) * steerStrength;
        vel.z += (dz / dist) * steerStrength;
      }
    }

    // ---- Limit speed ----
    const spd = vel.length();
    const maxSpd = fish.speed * (fish.targetFood ? 1.8 : 1.0);
    if (spd > maxSpd) {
      vel.multiplyScalar(maxSpd / spd);
    }
    // Minimum speed
    if (spd < 0.3) {
      vel.normalize().multiplyScalar(0.3);
    }

    // ---- Move ----
    pos.x += vel.x * dt;
    pos.y += vel.y * dt;
    pos.z += vel.z * dt;

    // ---- Rotate to face direction ----
    const lookTarget = pos.clone().add(vel);
    fish.mesh.lookAt(lookTarget);

    // ---- Tail animation ----
    const tailAngle = Math.sin(now * 0.001 * fish.tailSpeed + fish.phase) * 0.35;
    fish.tail.rotation.y = tailAngle;

    // ---- Fin animation ----
    const finAngle = Math.sin(now * 0.001 * fish.tailSpeed * 1.5 + fish.phase) * 0.2;
    fish.leftFin.rotation.z = finAngle;
    fish.rightFin.rotation.z = -finAngle;
    fish.topFin.rotation.x = Math.sin(now * 0.001 * fish.tailSpeed * 0.8 + fish.phase) * 0.15;
  }

  // ---- Update food ----
  for (let i = foodArray.length - 1; i >= 0; i--) {
    const food = foodArray[i];
    if (!food.userData.alive) {
      foodArray.splice(i, 1);
      continue;
    }
    food.position.x += food.userData.vx * dt;
    food.position.y += food.userData.vy * dt;
    food.position.z += food.userData.vz * dt;
    food.userData.vy -= 3 * dt; // gravity

    // Hit bottom
    if (food.position.y < 0.3) {
      food.position.y = 0.3;
      food.userData.vy = 0;
      food.userData.vx *= 0.95;
      food.userData.vz *= 0.95;
      // Remove after settling
      setTimeout(() => {
        if (food.userData.alive) {
          food.userData.alive = false;
          scene.remove(food);
          const idx = foodArray.indexOf(food);
          if (idx > -1) foodArray.splice(idx, 1);
        }
      }, 3000);
    }
  }

  // ---- Update bubbles ----
  for (const bubble of bubbleArray) {
    bubble.position.y += bubble.userData.speed * dt;
    bubble.position.x = bubble.userData.baseX + Math.sin(now * 0.001 * bubble.userData.swayAmpX + bubble.userData.phaseX) * 0.5;
    bubble.position.z = bubble.userData.baseZ + Math.cos(now * 0.001 * bubble.userData.swayAmpZ + bubble.userData.phaseZ) * 0.3;

    if (bubble.position.y > AH - 1) {
      bubble.position.y = 0;
      bubble.userData.baseX = (Math.random() - 0.5) * (AW - 4);
      bubble.userData.baseZ = (Math.random() - 0.5) * (AD - 4);
      bubble.userData.phaseX = Math.random() * Math.PI * 2;
      bubble.userData.phaseZ = Math.random() * Math.PI * 2;
    }
  }

  // ---- Seaweed sway ----
  for (const weed of seaweeds) {
    const p = weed.userData.phase;
    const s = weed.userData.swaySpeed;
    weed.rotation.x = Math.sin(now * 0.0005 * s + p) * 0.08;
    weed.rotation.z = Math.cos(now * 0.0007 * s + p + 1.0) * 0.06;
  }

  // ---- Point light subtle movement ----
  pointLight1.position.x = -10 + Math.sin(now * 0.0003) * 3;
  pointLight1.position.z = -5 + Math.cos(now * 0.0004) * 2;
  pointLight2.position.x = 10 + Math.cos(now * 0.00035) * 3;
  pointLight2.position.z = 5 + Math.sin(now * 0.0005) * 2;

  // ---- Update stats ----
  document.getElementById('fish-count').textContent = fishArray.length;
  document.getElementById('bubble-count').textContent = bubbleArray.length;
  document.getElementById('food-count').textContent = foodArray.filter(f => f.userData.alive).length;

  controls.update();
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

Этот файл содержит полностью рабочий 3D-аквариум со всеми запрошенными функциями:

**Что реализовано:**

- 🐠 **15 рыбок** с детализированной анатомией (тело, брюшко, глаза с зрачками, хвост, спинной и боковые плавники) в 8 цветовых схемах
- 🧠 **ИИ-поведение**: избегание столкновений, отражение от стен, случайное блуждание, преследование корма, рост после поедания
- 🌊 **Аквариум**: стеклянный контейнер с преломлением, рамка из wireframe-рёбер, песчаное дно с процедурными неровностями, 8 камней, 12 водорослей с покачиванием
- 💨 **30 пузырей** с прозрачным стеклянным материалом, движением вверх и покачиванием
- 🍽️ **Система кормления**: клик по воде → гранула падает с гравитацией → рыбки в радиусе 15 единиц бегут к ней → съели → выросли на 5%
- 💡 **Освещение**: ambient + directional с мягкими тенями 2048×2048 + 2 подвижных point-света с подводным голубым оттенком
- 🎮 **OrbitControls** с damping, ограничениями угла и зума
- 🖥️ **UI-панели** с glassmorphism-эффектом, статистика (рыбки/FPS/пузыри/корм), кнопки управления