```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tidehaven</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; font-family: 'Segoe UI', system-ui, sans-serif; background: #1a1a2e; }
canvas { display: block; }

#ui-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 10;
}

#title-block {
  position: fixed; top: 20px; left: 24px; pointer-events: none;
}
#title-block h1 {
  font-size: 2.2rem; font-weight: 300; color: #f0e6d3;
  letter-spacing: 3px; text-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
#title-block p {
  font-size: 0.85rem; color: rgba(240,230,211,0.7); margin-top: 4px;
  letter-spacing: 1px;
}

#controls {
  position: fixed; right: 16px; top: 20px; width: 260px;
  pointer-events: auto; display: flex; flex-direction: column; gap: 8px;
}

.panel {
  background: rgba(20, 30, 40, 0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
  padding: 12px 14px; color: #e8dcc8;
}
.panel h3 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px;
  color: rgba(232,220,200,0.6); margin-bottom: 8px; }

.btn-row { display: flex; flex-wrap: wrap; gap: 6px; }
.btn {
  padding: 6px 12px; border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.05); color: #e8dcc8; border-radius: 6px;
  font-size: 0.78rem; cursor: pointer; transition: all 0.2s;
  letter-spacing: 0.5px;
}
.btn:hover { background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.3); }
.btn.active { background: rgba(100,200,180,0.2); border-color: rgba(100,200,180,0.5); color: #7ee8d0; }

.slider-row { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
.slider-row label { font-size: 0.72rem; min-width: 40px; color: rgba(232,220,200,0.7); }
.slider-row input[type="range"] {
  flex: 1; height: 4px; -webkit-appearance: none; appearance: none;
  background: rgba(255,255,255,0.15); border-radius: 2px; outline: none;
}
.slider-row input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%;
  background: #7ee8d0; cursor: pointer;
}

#mobile-toggle {
  display: none; position: fixed; right: 16px; top: 20px;
  pointer-events: auto; background: rgba(20,30,40,0.8);
  border: 1px solid rgba(255,255,255,0.15); border-radius: 8px;
  padding: 8px 12px; color: #e8dcc8; font-size: 0.8rem; cursor: pointer;
}

@media (max-width: 768px) {
  #controls { width: 220px; right: 10px; top: 50px; display: none; }
  #controls.visible { display: flex; }
  #mobile-toggle { display: block; }
  #title-block h1 { font-size: 1.5rem; }
}

#audio-btn { position: fixed; bottom: 20px; left: 24px; pointer-events: auto; }
</style>
</head>
<body>
<div id="ui-overlay">
  <div id="title-block">
    <h1>Tidehaven</h1>
    <p>A coastal diorama — living waters, quiet shores</p>
  </div>

  <button id="mobile-toggle">☰ Controls</button>

  <div id="controls">
    <div class="panel">
      <h3>Camera</h3>
      <div class="btn-row">
        <button class="btn active" data-cam="iso">Isometric</button>
        <button class="btn" data-cam="cabin">Cabin</button>
        <button class="btn" data-cam="under">Underwater</button>
        <button class="btn" data-cam="orbit">Free Orbit</button>
      </div>
    </div>

    <div class="panel">
      <h3>Actions</h3>
      <div class="btn-row">
        <button class="btn" id="btn-kayak">Launch Kayak</button>
        <button class="btn" id="btn-ray">Ray Leap</button>
        <button class="btn" id="btn-pause">Pause</button>
        <button class="btn" id="btn-reset">Reset</button>
      </div>
    </div>

    <div class="panel">
      <h3>Environment</h3>
      <div class="slider-row">
        <label>Tide</label>
        <input type="range" id="slider-tide" min="0" max="100" value="50">
      </div>
      <div class="slider-row">
        <label>Wind</label>
        <input type="range" id="slider-wind" min="0" max="100" value="40">
      </div>
    </div>

    <div class="panel">
      <h3>Time of Day</h3>
      <div class="btn-row">
        <button class="btn active" data-time="day">Day</button>
        <button class="btn" data-time="sunset">Sunset</button>
        <button class="btn" data-time="night">Night</button>
      </div>
    </div>

    <div class="panel">
      <h3>Audio</h3>
      <div class="btn-row">
        <button class="btn" id="btn-music">Music Off</button>
      </div>
      <div class="slider-row">
        <label>Volume</label>
        <input type="range" id="slider-volume" min="0" max="100" value="60">
      </div>
    </div>
  </div>

  <button class="btn" id="audio-btn">🔊 Enable Audio</button>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r152/three.min.js"></script>
<script>
// ============================================================
// TIDEHAVEN - Interactive 3D Coastal Diorama
// ============================================================

// --- Globals ---
let scene, camera, renderer, clock;
let isPaused = false;
let currentTime = 'day';
let windStrength = 0.4;
let tideLevel = 0.5;
let audioStarted = false;
let musicPlaying = false;
let kayakState = 'moored'; // 'moored', 'launching', 'returning'
let kayakAngle = 0;
let rayJumping = false;
let rayJumpTime = 0;
let cameraTransition = null;

// Animation state
let animTime = 0;

// Scene objects
let waterGroup, islandGroup, cabinGroup, pierGroup;
let waterMesh, waterSurface;
let glassGroup;
let fishInstances, rayGroup, plantInstances;
let kayak, kayakGroup;
let cabinWindows = [];
let lanterns = [];
let treeMeshes = [];
let foamMesh;
let bubbles = [];
let ripples = [];
let droplets = [];

// Lighting
let sunLight, ambientLight, cabinLight, lanternLights;
let targetLighting = {};

// Audio
let audioCtx, masterGain, musicGain, ambienceGain;
let musicNodes = [];

// --- Initialization ---
function init() {
  clock = new THREE.Clock();
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x8fb8c8, 0.012);

  camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(12, 10, 14);
  camera.lookAt(0, 1, 0);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  document.body.appendChild(renderer.domElement);

  setupLighting();
  createDioramaBox();
  createIsland();
  createCabin();
  createPier();
  createWater();
  createUnderwaterLife();
  createTrees();
  createDetails();
  setupOrbitControls();
  setupUI();
  setupAudio();

  animate();
}

// --- Lighting ---
function setupLighting() {
  ambientLight = new THREE.AmbientLight(0x6688aa, 0.4);
  scene.add(ambientLight);

  sunLight = new THREE.DirectionalLight(0xfff4e0, 1.2);
  sunLight.position.set(8, 12, 6);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(2048, 2048);
  sunLight.shadow.camera.near = 0.5;
  sunLight.shadow.camera.far = 50;
  sunLight.shadow.camera.left = -15;
  sunLight.shadow.camera.right = 15;
  sunLight.shadow.camera.top = 15;
  sunLight.shadow.camera.bottom = -15;
  sunLight.shadow.bias = -0.001;
  scene.add(sunLight);

  const hemiLight = new THREE.HemisphereLight(0x87ceeb, 0x3d2b1f, 0.3);
  scene.add(hemiLight);

  // Cabin warm light
  cabinLight = new THREE.PointLight(0xffaa44, 0, 6);
  cabinLight.position.set(0, 2.5, -1);
  scene.add(cabinLight);

  // Lantern lights
  lanternLights = [];
  for (let i = 0; i < 3; i++) {
    const ll = new THREE.PointLight(0xffcc66, 0, 4);
    scene.add(ll);
    lanternLights.push(ll);
  }
}

// --- Diorama Box (Glass Container) ---
function createDioramaBox() {
  glassGroup = new THREE.Group();

  const boxW = 14, boxH = 8, boxD = 12;

  // Glass material - very subtle tint
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.08,
    roughness: 0.05,
    metalness: 0,
    side: THREE.DoubleSide,
    depthWrite: false
  });

  // Front glass panel
  const frontGeo = new THREE.PlaneGeometry(boxW, boxH);
  const frontPanel = new THREE.Mesh(frontGeo, glassMat);
  frontPanel.position.set(0, boxH / 2 - 1, boxD / 2);
  frontPanel.renderOrder = 100;
  glassGroup.add(frontPanel);

  // Right glass panel
  const rightGeo = new THREE.PlaneGeometry(boxD, boxH);
  const rightPanel = new THREE.Mesh(rightGeo, glassMat);
  rightPanel.position.set(boxW / 2, boxH / 2 - 1, 0);
  rightPanel.rotation.y = -Math.PI / 2;
  rightPanel.renderOrder = 100;
  glassGroup.add(rightPanel);

  // Left glass panel (partial - for cross-section feel)
  const leftGeo = new THREE.PlaneGeometry(boxD, boxH);
  const leftPanel = new THREE.Mesh(leftGeo, glassMat);
  leftPanel.position.set(-boxW / 2, boxH / 2 - 1, 0);
  leftPanel.rotation.y = Math.PI / 2;
  leftPanel.renderOrder = 100;
  glassGroup.add(leftPanel);

  // Bottom base (opaque)
  const baseMat = new THREE.MeshStandardMaterial({ color: 0x2a2520, roughness: 0.9 });
  const baseGeo = new THREE.BoxGeometry(boxW + 0.4, 0.3, boxD + 0.4);
  const base = new THREE.Mesh(baseGeo, baseMat);
  base.position.set(0, -1.15, 0);
  base.receiveShadow = true;
  glassGroup.add(base);

  // Frame edges
  const frameMat = new THREE.MeshStandardMaterial({ color: 0x3a3530, roughness: 0.7, metalness: 0.3 });
  const frameGeo = new THREE.BoxGeometry(0.08, 0.08, 0.08);

  // Vertical edges
  const edgePositions = [
    [-boxW/2, boxH/2-1, boxD/2], [boxW/2, boxH/2-1, boxD/2],
    [boxW/2, boxH/2-1, -boxD/2], [-boxW/2, boxH/2-1, -boxD/2]
  ];
  const vertGeo = new THREE.CylinderGeometry(0.04, 0.04, boxH, 8);
  edgePositions.forEach(p => {
    const edge = new THREE.Mesh(vertGeo, frameMat);
    edge.position.set(p[0], p[1], p[2]);
    glassGroup.add(edge);
  });

  // Top horizontal edges
  const topGeoX = new THREE.CylinderGeometry(0.04, 0.04, boxW, 8);
  const topGeoZ = new THREE.CylinderGeometry(0.04, 0.04, boxD, 8);

  const topFront = new THREE.Mesh(topGeoX, frameMat);
  topFront.rotation.z = Math.PI / 2;
  topFront.position.set(0, boxH - 1, boxD / 2);
  glassGroup.add(topFront);

  const topBack = new THREE.Mesh(topGeoX, frameMat);
  topBack.rotation.z = Math.PI / 2;
  topBack.position.set(0, boxH - 1, -boxD / 2);
  glassGroup.add(topBack);

  const topRight = new THREE.Mesh(topGeoZ, frameMat);
  topRight.rotation.x = Math.PI / 2;
  topRight.position.set(boxW / 2, boxH - 1, 0);
  glassGroup.add(topRight);

  const topLeft = new THREE.Mesh(topGeoZ, frameMat);
  topLeft.rotation.x = Math.PI / 2;
  topLeft.position.set(-boxW / 2, boxH - 1, 0);
  glassGroup.add(topLeft);

  scene.add(glassGroup);
}

// --- Island ---
function createIsland() {
  islandGroup = new THREE.Group();

  // Island terrain using heightmap
  const islandSize = 8;
  const segments = 40;
  const geo = new THREE.PlaneGeometry(islandSize, islandSize, segments, segments);
  geo.rotateX(-Math.PI / 2);

  const positions = geo.attributes.position;
  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i);
    const z = positions.getZ(i);
    const dist = Math.sqrt(x * x + z * z);
    const maxR = islandSize / 2 - 0.5;

    let h = 0;
    if (dist < maxR) {
      // Main island shape
      const t = dist / maxR;
      h = (1 - t * t) * 2.2;
      // Add some noise for natural look
      h += Math.sin(x * 2.3) * Math.cos(z * 1.8) * 0.3;
      h += Math.sin(x * 4.1 + z * 3.2) * 0.15;
      // Flatten top for cabin area
      if (dist < 2 && h > 1.5) h = 1.5 + (h - 1.5) * 0.3;
    } else {
      // Underwater slope
      const t = (dist - maxR) / (islandSize / 2 - maxR + 2);
      h = -t * 2.5;
    }
    positions.setY(i, h);
  }
  geo.computeVertexNormals();

  // Island material with vertex colors
  const colors = [];
  for (let i = 0; i < positions.count; i++) {
    const y = positions.getY(i);
    const x = positions.getX(i);
    const z = positions.getZ(i);
    let color;
    if (y > 1.2) {
      color = new THREE.Color(0x4a7c3f); // grass
    } else if (y > 0.4) {
      color = new THREE.Color(0x8b7355); // earth/transition
    } else if (y > -0.2) {
      color = new THREE.Color(0xd4b896); // sand
    } else {
      color = new THREE.Color(0xc4a87a); // underwater sand
    }
    colors.push(color.r, color.g, color.b);
  }
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

  const islandMat = new THREE.MeshStandardMaterial({
    vertexColors: true, roughness: 0.85, metalness: 0
  });
  const islandMesh = new THREE.Mesh(geo, islandMat);
  islandMesh.castShadow = true;
  islandMesh.receiveShadow = true;
  islandGroup.add(islandMesh);

  // Rocks
  const rockGeo = new THREE.DodecahedronGeometry(0.4, 1);
  const rockMat = new THREE.MeshStandardMaterial({ color: 0x6b6b6b, roughness: 0.9 });
  const rockPositions = [
    [2.8, 0.2, 1.5], [-2.5, 0.1, -2], [3.2, 0.0, -1.5],
    [-3, 0.15, 1.8], [1.5, 0.3, -3], [-1.8, 0.2, 2.8]
  ];
  rockPositions.forEach(p => {
    const rock = new THREE.Mesh(rockGeo, rockMat);
    rock.position.set(p[0], p[1], p[2]);
    rock.scale.set(0.7 + Math.random() * 0.6, 0.5 + Math.random() * 0.4, 0.7 + Math.random() * 0.6);
    rock.rotation.set(Math.random() * 0.5, Math.random() * Math.PI, Math.random() * 0.3);
    rock.castShadow = true;
    rock.receiveShadow = true;
    islandGroup.add(rock);
  });

  // Sandy beach ring
  const beachGeo = new THREE.RingGeometry(3.2, 4.2, 32);
  beachGeo.rotateX(-Math.PI / 2);
  const beachMat = new THREE.MeshStandardMaterial({ color: 0xe8d5b7, roughness: 0.95 });
  const beach = new THREE.Mesh(beachGeo, beachMat);
  beach.position.y = 0.15;
  beach.receiveShadow = true;
  islandGroup.add(beach);

  scene.add(islandGroup);
}

// --- Cabin ---
function createCabin() {
  cabinGroup = new THREE.Group();
  cabinGroup.position.set(0, 1.5, -0.5);

  // A-frame structure
  const cabinW = 2.2, cabinH = 2.4, cabinD = 2.8;

  // Wood walls (triangular A-frame)
  const wallShape = new THREE.Shape();
  wallShape.moveTo(-cabinW / 2, 0);
  wallShape.lineTo(cabinW / 2, 0);
  wallShape.lineTo(0, cabinH);
  wallShape.closePath();

  const wallGeo = new THREE.ExtrudeGeometry(wallShape, { depth: cabinD, bevelEnabled: false });
  const woodMat = new THREE.MeshStandardMaterial({ color: 0x8b6b4a, roughness: 0.8 });
  const walls = new THREE.Mesh(wallGeo, woodMat);
  walls.position.set(0, 0, -cabinD / 2);
  walls.castShadow = true;
  walls.receiveShadow = true;
  cabinGroup.add(walls);

  // Copper roof
  const roofGeo = new THREE.BoxGeometry(cabinW + 0.3, 0.12, cabinD + 0.4);
  const copperMat = new THREE.MeshStandardMaterial({ color: 0x4a8c7a, roughness: 0.4, metalness: 0.7 });

  // Left roof panel
  const roofLeft = new THREE.Mesh(new THREE.BoxGeometry(cabinW * 0.8, 0.1, cabinD + 0.3), copperMat);
  roofLeft.position.set(-cabinW * 0.25, cabinH * 0.55, 0);
  roofLeft.rotation.z = 0.75;
  roofLeft.castShadow = true;
  cabinGroup.add(roofLeft);

  // Right roof panel
  const roofRight = new THREE.Mesh(new THREE.BoxGeometry(cabinW * 0.8, 0.1, cabinD + 0.3), copperMat);
  roofRight.position.set(cabinW * 0.25, cabinH * 0.55, 0);
  roofRight.rotation.z = -0.75;
  roofRight.castShadow = true;
  cabinGroup.add(roofRight);

  // Ridge beam
  const ridgeMat = new THREE.MeshStandardMaterial({ color: 0x3d6b5c, roughness: 0.5, metalness: 0.6 });
  const ridge = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, cabinD + 0.3, 8), ridgeMat);
  ridge.rotation.x = Math.PI / 2;
  ridge.position.set(0, cabinH, 0);
  cabinGroup.add(ridge);

  // Windows (glowing)
  const windowMat = new THREE.MeshStandardMaterial({
    color: 0xffcc66, emissive: 0xffaa33, emissiveIntensity: 0.5, roughness: 0.3
  });

  // Front windows
  const winGeo = new THREE.PlaneGeometry(0.4, 0.5);
  const win1 = new THREE.Mesh(winGeo, windowMat.clone());
  win1.position.set(-0.4, 0.8, cabinD / 2 + 0.01);
  cabinGroup.add(win1);
  cabinWindows.push(win1);

  const win2 = new THREE.Mesh(winGeo, windowMat.clone());
  win2.position.set(0.4, 0.8, cabinD / 2 + 0.01);
  cabinGroup.add(win2);
  cabinWindows.push(win2);

  // Window frames
  const frameMat = new THREE.MeshStandardMaterial({ color: 0x5a4030, roughness: 0.8 });
  const frameGeo = new THREE.BoxGeometry(0.5, 0.6, 0.05);
  const frame1 = new THREE.Mesh(frameGeo, frameMat);
  frame1.position.set(-0.4, 0.8, cabinD / 2 + 0.02);
  cabinGroup.add(frame1);
  const frame2 = new THREE.Mesh(frameGeo, frameMat);
  frame2.position.set(0.4, 0.8, cabinD / 2 + 0.02);
  cabinGroup.add(frame2);

  // Door
  const doorMat = new THREE.MeshStandardMaterial({ color: 0x6b4a2a, roughness: 0.85 });
  const doorGeo = new THREE.BoxGeometry(0.5, 0.9, 0.06);
  const door = new THREE.Mesh(doorGeo, doorMat);
  door.position.set(0, 0.45, cabinD / 2 + 0.02);
  cabinGroup.add(door);

  // Door handle
  const handleMat = new THREE.MeshStandardMaterial({ color: 0xb8860b, metalness: 0.8, roughness: 0.3 });
  const handle = new THREE.Mesh(new THREE.SphereGeometry(0.04, 8, 8), handleMat);
  handle.position.set(0.15, 0.5, cabinD / 2 + 0.06);
  cabinGroup.add(handle);

  // Deck
  const deckGeo = new THREE.BoxGeometry(3.5, 0.12, 2.5);
  const deckMat = new THREE.MeshStandardMaterial({ color: 0x9b7b5a, roughness: 0.8 });
  const deck = new THREE.Mesh(deckGeo, deckMat);
  deck.position.set(0, -0.06, 1.5);
  deck.receiveShadow = true;
  deck.castShadow = true;
  cabinGroup.add(deck);

  // Deck railing posts
  const postGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.7, 6);
  const postMat = new THREE.MeshStandardMaterial({ color: 0x7a5a3a, roughness: 0.8 });
  const postPositions = [
    [-1.6, 0.35, 2.7], [1.6, 0.35, 2.7], [-1.6, 0.35, 0.3], [1.6, 0.35, 0.3],
    [-1.6, 0.35, 1.5], [1.6, 0.35, 1.5]
  ];
  postPositions.forEach(p => {
    const post = new THREE.Mesh(postGeo, postMat);
    post.position.set(p[0], p[1], p[2]);
    post.castShadow = true;
    cabinGroup.add(post);
  });

  // Railing top bars
  const railGeo = new THREE.CylinderGeometry(0.03, 0.03, 3.2, 6);
  const rail1 = new THREE.Mesh(railGeo, postMat);
  rail1.rotation.z = Math.PI / 2;
  rail1.position.set(0, 0.7, 2.7);
  cabinGroup.add(rail1);

  // Bench on deck
  const benchSeat = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.08, 0.4), new THREE.MeshStandardMaterial({ color: 0x7a5a3a, roughness: 0.8 }));
  benchSeat.position.set(-0.8, 0.45, 2.2);
  benchSeat.castShadow = true;
  cabinGroup.add(benchSeat);
  const benchBack = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.5, 0.06), new THREE.MeshStandardMaterial({ color: 0x7a5a3a, roughness: 0.8 }));
  benchBack.position.set(-0.8, 0.72, 2.0);
  cabinGroup.add(benchBack);
  // Bench legs
  const legGeo = new THREE.BoxGeometry(0.06, 0.45, 0.06);
  [[-1.35, 0.22, 2.2], [-0.25, 0.22, 2.2], [-1.35, 0.22, 2.0], [-0.25, 0.22, 2.0]].forEach(p => {
    const leg = new THREE.Mesh(legGeo, postMat);
    leg.position.set(p[0], p[1], p[2]);
    cabinGroup.add(leg);
  });

  // Towel on deck
  const towelMat = new THREE.MeshStandardMaterial({ color: 0x4a90d9, roughness: 0.9 });
  const towel = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.03, 0.4), towelMat);
  towel.position.set(1.2, 0.08, 2.0);
  towel.rotation.y = 0.3;
  cabinGroup.add(towel);

  // Crates
  const crateMat = new THREE.MeshStandardMaterial({ color: 0x8b6b4a, roughness: 0.85 });
  const crateGeo = new THREE.BoxGeometry(0.5, 0.4, 0.5);
  const crate1 = new THREE.Mesh(crateGeo, crateMat);
  crate1.position.set(1.3, 0.2, 0.5);
  crate1.castShadow = true;
  cabinGroup.add(crate1);
  const crate2 = new THREE.Mesh(crateGeo, crateMat);
  crate2.position.set(1.0, 0.2, 0.8);
  crate2.rotation.y = 0.4;
  crate2.castShadow = true;
  cabinGroup.add(crate2);

  // Small plant pot near door
  const potMat = new THREE.MeshStandardMaterial({ color: 0x8b4513, roughness: 0.9 });
  const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.12, 0.25, 8), potMat);
  pot.position.set(0.7, 0.12, 1.6);
  cabinGroup.add(pot);
  const plantMat = new THREE.MeshStandardMaterial({ color: 0x3a8a3a, roughness: 0.7 });
  const plant = new THREE.Mesh(new THREE.SphereGeometry(0.2, 8, 6), plantMat);
  plant.position.set(0.7, 0.45, 1.6);
  plant.scale.y = 1.3;
  cabinGroup.add(plant);

  // Chimney
  const chimney = new THREE.Mesh(
    new THREE.BoxGeometry(0.3, 0.8, 0.3),
    new THREE.MeshStandardMaterial({ color: 0x5a4a3a, roughness: 0.85 })
  );
  chimney.position.set(-0.5, cabinH + 0.2, -0.5);
  chimney.castShadow = true;
  cabinGroup.add(chimney);

  scene.add(cabinGroup);
}

// --- Pier ---
function createPier() {
  pierGroup = new THREE.Group();
  pierGroup.position.set(3.5, 0.1, 2.5);

  const pierMat = new THREE.MeshStandardMaterial({ color: 0x7a5a3a, roughness: 0.85 });

  // Pier planks
  const plankGeo = new THREE.BoxGeometry(0.35, 0.08, 4.5);
  for (let i = 0; i < 5; i++) {
    const plank = new THREE.Mesh(plankGeo, pierMat);
    plank.position.set(i * 0.38 - 0.76, 0, 0);
    plank.castShadow = true;
    plank.receiveShadow = true;
    pierGroup.add(plank);
  }

  // Pier support posts
  const postGeo = new THREE.CylinderGeometry(0.06, 0.06, 2, 8);
  const postMat = new THREE.MeshStandardMaterial({ color: 0x5a4030, roughness: 0.9 });
  const postPos = [[-0.8, -1, -2], [0.8, -1, -2], [-0.8, -1, 2], [0.8, -1, 2]];
  postPos.forEach(p => {
    const post = new THREE.Mesh(postGeo, postMat);
    post.position.set(p[0], p[1], p[2]);
    post.castShadow = true;
    pierGroup.add(post);
  });

  // Cross beams under pier
  const beamGeo = new THREE.BoxGeometry(2.0, 0.08, 0.08);
  [-2, 0, 2].forEach(z => {
    const beam = new THREE.Mesh(beamGeo, postMat);
    beam.position.set(0, -0.2, z);
    pierGroup.add(beam);
  });

  // Ladder
  const ladderMat = new THREE.MeshStandardMaterial({ color: 0x6b4a2a, roughness: 0.8 });
  const ladderSideGeo = new THREE.BoxGeometry(0.05, 1.8, 0.05);
  const ladderSide1 = new THREE.Mesh(ladderSideGeo, ladderMat);
  ladderSide1.position.set(0.9, -0.8, 1.8);
  pierGroup.add(ladderSide1);
  const ladderSide2 = new THREE.Mesh(ladderSideGeo, ladderMat);
  ladderSide2.position.set(1.2, -0.8, 1.8);
  pierGroup.add(ladderSide2);
  // Rungs
  const rungGeo = new THREE.BoxGeometry(0.3, 0.04, 0.04);
  for (let i = 0; i < 5; i++) {
    const rung = new THREE.Mesh(rungGeo, ladderMat);
    rung.position.set(1.05, -0.2 - i * 0.35, 1.8);
    pierGroup.add(rung);
  }

  // Lanterns on pier
  const lanternMat = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.6, metalness: 0.4 });
  const lanternGlassMat = new THREE.MeshStandardMaterial({
    color: 0xffdd88, emissive: 0xffaa33, emissiveIntensity: 0, roughness: 0.3, transparent: true, opacity: 0.8
  });

  const lanternPositions = [[-0.7, 0.6, -1.5], [0.7, 0.6, 0], [-0.7, 0.6, 1.5]];
  lanternPositions.forEach((p, i) => {
    // Lantern body
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.3, 8), lanternMat);
    body.position.set(p[0], p[1], p[2]);
    body.castShadow = true;
    pierGroup.add(body);
    // Lantern glass
    const glass = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.22, 8), lanternGlassMat.clone());
    glass.position.set(p[0], p[1], p[2]);
    pierGroup.add(glass);
    lanterns.push({ mesh: glass, light: lanternLights[i], pos: new THREE.Vector3(
      p[0] + pierGroup.position.x, p[1] + pierGroup.position.y, p[2] + pierGroup.position.z
    )});
    // Lantern top
    const top = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.12, 8), lanternMat);
    top.position.set(p[0], p[1] + 0.21, p[2]);
    pierGroup.add(top);
    // Post
    const lpost = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.5, 6), lanternMat);
    lpost.position.set(p[0], p[1] - 0.35, p[2]);
    pierGroup.add(lpost);
  });

  // Kayak
  kayakGroup = new THREE.Group();
  const kayakMat = new THREE.MeshStandardMaterial({ color: 0xd45a2a, roughness: 0.6 });
  const kayakShape = new THREE.Shape();
  kayakShape.moveTo(0, -0.8);
  kayakShape.quadraticCurveTo(0.25, -0.4, 0.25, 0);
  kayakShape.quadraticCurveTo(0.25, 0.4, 0, 0.8);
  kayakShape.quadraticCurveTo(-0.25, 0.4, -0.25, 0);
  kayakShape.quadraticCurveTo(-0.25, -0.4, 0, -0.8);

  const kayakGeo = new THREE.ExtrudeGeometry(kayakShape, { depth: 0.2, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.05 });
  kayak = new THREE.Mesh(kayakGeo, kayakMat);
  kayak.rotation.x = -Math.PI / 2;
  kayak.castShadow = true;
  kayakGroup.add(kayak);

  // Kayak seat
  const seatMat = new THREE.MeshStandardMaterial({ color: 0x3a3a3a, roughness: 0.7 });
  const seat = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.04, 0.25), seatMat);
  seat.position.set(0, 0.12, 0);
  kayakGroup.add(seat);

  // Paddle
  const paddleMat = new THREE.MeshStandardMaterial({ color: 0x6b4a2a, roughness: 0.7 });
  const paddleShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.2, 6), paddleMat);
  paddleShaft.position.set(0.3, 0.15, 0);
  paddleShaft.rotation.z = Math.PI / 2;
  kayakGroup.add(paddleShaft);
  const bladeGeo = new THREE.BoxGeometry(0.08, 0.25, 0.02);
  const blade1 = new THREE.Mesh(bladeGeo, paddleMat);
  blade1.position.set(0.3, 0.15, 0.6);
  kayakGroup.add(blade1);
  const blade2 = new THREE.Mesh(bladeGeo, paddleMat);
  blade2.position.set(0.3, 0.15, -0.6);
  kayakGroup.add(blade2);

  // Mooring rope
  const ropeMat = new THREE.MeshStandardMaterial({ color: 0x8b7355, roughness: 0.9 });
  const ropeGeo = new THREE.CylinderGeometry(0.015, 0.015, 1.2, 6);
  const rope = new THREE.Mesh(ropeGeo, ropeMat);
  rope.position.set(-0.3, 0.05, -0.5);
  rope.rotation.x = 0.3;
  kayakGroup.add(rope);

  kayakGroup.position.set(0.3, 0.15, 1.2);
  kayakGroup.rotation.y = 0.3;
  pierGroup.add(kayakGroup);

  scene.add(pierGroup);
}

// --- Water System ---
function createWater() {
  waterGroup = new THREE.Group();

  // Water volume (the main water body)
  const waterGeo = new THREE.BoxGeometry(13.5, 5.5, 11.5);
  const waterMat = new THREE.MeshPhysicalMaterial({
    color: 0x2a9a8a,
    transparent: true,
    opacity: 0.55,
    roughness: 0.1,
    metalness: 0,
    transmission: 0.4,
    thickness: 2,
    ior: 1.33,
    depthWrite: false,
    side: THREE.DoubleSide
  });
  waterMesh = new THREE.Mesh(waterGeo, waterMat);
  waterMesh.position.set(0, 1.5, 0);
  waterMesh.renderOrder = 50;
  waterGroup.add(waterMesh);

  // Water surface with waves (custom shader)
  const surfaceGeo = new THREE.PlaneGeometry(13.5, 11.5, 60, 50);
  surfaceGeo.rotateX(-Math.PI / 2);

  const surfaceMat = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    uniforms: {
      uTime: { value: 0 },
      uWind: { value: windStrength },
      uColor: { value: new THREE.Color(0x3ab8a8) },
      uOpacity: { value: 0.6 }
    },
    vertexShader: `
      uniform float uTime;
      uniform float uWind;
      varying vec2 vUv;
      varying float vWave;
      void main() {
        vUv = uv;
        vec3 pos = position;
        float wave1 = sin(pos.x * 2.0 + uTime * 1.5) * 0.08 * uWind;
        float wave2 = sin(pos.z * 3.0 + uTime * 2.0) * 0.05 * uWind;
        float wave3 = sin((pos.x + pos.z) * 1.5 + uTime * 1.0) * 0.06 * uWind;
        pos.y += wave1 + wave2 + wave3;
        vWave = wave1 + wave2 + wave3;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 uColor;
      uniform float uOpacity;
      uniform float uTime;
      varying vec2 vUv;
      varying float vWave;
      void main() {
        vec3 col = uColor + vWave * 2.0;
        // Foam at edges
        float edge = min(min(vUv.x, 1.0 - vUv.x), min(vUv.y, 1.0 - vUv.y));
        float foam = smoothstep(0.0, 0.08, edge) * 0.3;
        col = mix(vec3(0.95, 0.97, 0.98), col, smoothstep(0.0, 0.1, edge));
        float alpha = uOpacity + foam;
        gl_FragColor = vec4(col, alpha);
      }
    `
  });

  waterSurface = new THREE.Mesh(surfaceGeo, surfaceMat);
  waterSurface.position.set(0, 4.0, 0);
  waterSurface.renderOrder = 55;
  waterGroup.add(waterSurface);

  // Seabed
  const seabedGeo = new THREE.PlaneGeometry(13.5, 11.5, 40, 30);
  seabedGeo.rotateX(-Math.PI / 2);
  const seabedMat = new THREE.MeshStandardMaterial({
    color: 0xc4a87a, roughness: 0.95, metalness: 0
  });
  const seabed = new THREE.Mesh(seabedGeo, seabedMat);
  seabed.position.set(0, -1.0, 0);
  seabed.receiveShadow = true;
  waterGroup.add(seabed);

  // Caustics on seabed (animated light pattern)
  const causticGeo = new THREE.PlaneGeometry(13.5, 11.5, 1, 1);
  causticGeo.rotateX(-Math.PI / 2);
  const causticMat = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    uniforms: {
      uTime: { value: 0 }
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      varying vec2 vUv;
      void main() {
        vec2 uv = vUv * 8.0;
        float c1 = sin(uv.x * 3.0 + uTime * 0.8) * cos(uv.y * 2.5 + uTime * 0.6);
        float c2 = sin(uv.x * 2.0 - uTime * 0.5) * cos(uv.y * 3.0 + uTime * 0.7);
        float c3 = sin((uv.x + uv.y) * 2.0 + uTime * 1.0);
        float caustic = (c1 + c2 + c3) * 0.33;
        caustic = smoothstep(0.1, 0.8, caustic);
        vec3 col = vec3(0.4, 0.9, 0.85) * caustic;
        gl_FragColor = vec4(col, caustic * 0.35);
      }
    `
  });
  const caustics = new THREE.Mesh(causticGeo, causticMat);
  caustics.position.set(0, -0.95, 0);
  caustics.renderOrder = 3;
  waterGroup.add(caustics);
  waterGroup.userData.caustics = caustics;

  // Shore foam ring
  const foamGeo = new THREE.RingGeometry(3.5, 4.5, 32);
  foamGeo.rotateX(-Math.PI / 2);
  const foamMat = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    uniforms: { uTime: { value: 0 }, uTide: { value: 0.5 } },
    vertexShader: `
      uniform float uTime;
      uniform float uTide;
      varying vec2 vUv;
      void main() {
        vUv = uv;
        vec3 pos = position;
        pos.y += 3.5 + uTide * 0.5;
        pos.y += sin(atan(pos.z, pos.x) * 6.0 + uTime * 2.0) * 0.03;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      varying vec2 vUv;
      void main() {
        float pulse = sin(vUv.x * 20.0 + uTime * 3.0) * 0.5 + 0.5;
        float alpha = (1.0 - vUv.y) * pulse * 0.5;
        gl_FragColor = vec4(1.0, 1.0, 1.0, alpha);
      }
    `
  });
  foamMesh = new THREE.Mesh(foamGeo, foamMat);
  foamMesh.renderOrder = 60;
  waterGroup.add(foamMesh);

  scene.add(waterGroup);
}

// --- Underwater Life ---
function createUnderwaterLife() {
  // Rays
  rayGroup = new THREE.Group();
  const rayMat = new THREE.MeshStandardMaterial({ color: 0x8ba5b0, roughness: 0.6 });

  for (let i = 0; i < 3; i++) {
    const ray = createRay(rayMat);
    ray.position.set(
      (Math.random() - 0.5) * 6,
      -0.5 + Math.random() * 0.5,
      (Math.random() - 0.5) * 5
    );
    ray.userData = {
      baseY: ray.position.y,
      speed: 0.3 + Math.random() * 0.3,
      phase: Math.random() * Math.PI * 2,
      radius: 2 + Math.random() * 2,
      center: new THREE.Vector3((Math.random() - 0.5) * 3, 0, (Math.random() - 0.5) * 3)
    };
    rayGroup.add(ray);
  }
  waterGroup.add(rayGroup);

  // Fish school using InstancedMesh
  const fishGeo = new THREE.ConeGeometry(0.06, 0.25, 6);
  fishGeo.rotateZ(Math.PI / 2);
  const fishMat = new THREE.MeshStandardMaterial({ color: 0xf0c040, roughness: 0.5 });
  const fishCount = 40;
  fishInstances = new THREE.InstancedMesh(fishGeo, fishMat, fishCount);
  fishInstances.renderOrder = 40;

  const dummy = new THREE.Object3D();
  for (let i = 0; i < fishCount; i++) {
    dummy.position.set(
      (Math.random() - 0.5) * 8,
      -0.3 + Math.random() * 1.5,
      (Math.random() - 0.5) * 7
    );
    dummy.rotation.set(0, Math.random() * Math.PI * 2, 0);
    dummy.scale.setScalar(0.8 + Math.random() * 0.4);
    dummy.updateMatrix();
    fishInstances.setMatrixAt(i, dummy.matrix);
  }
  fishInstances.instanceMatrix.needsUpdate = true;
  waterGroup.add(fishInstances);

  // Aquatic plants using InstancedMesh
  const plantGeo = new THREE.ConeGeometry(0.1, 0.8, 5);
  const plantMat = new THREE.MeshStandardMaterial({ color: 0x2a7a4a, roughness: 0.7 });
  const plantCount = 25;
  plantInstances = new THREE.InstancedMesh(plantGeo, plantMat, plantCount);
  plantInstances.renderOrder = 35;

  for (let i = 0; i < plantCount; i++) {
    dummy.position.set(
      (Math.random() - 0.5) * 10,
      -0.6,
      (Math.random() - 0.5) * 9
    );
    dummy.scale.set(0.6 + Math.random() * 0.8, 0.5 + Math.random() * 1.0, 0.6 + Math.random() * 0.8);
    dummy.updateMatrix();
    plantInstances.setMatrixAt(i, dummy.matrix);
  }
  plantInstances.instanceMatrix.needsUpdate = true;
  waterGroup.add(plantInstances);

  // Underwater rocks
  const uRockGeo = new THREE.DodecahedronGeometry(0.3, 0);
  const uRockMat = new THREE.MeshStandardMaterial({ color: 0x4a5a5a, roughness: 0.9 });
  for (let i = 0; i < 8; i++) {
    const rock = new THREE.Mesh(uRockGeo, uRockMat);
    rock.position.set(
      (Math.random() - 0.5) * 10,
      -0.9,
      (Math.random() - 0.5) * 9
    );
    rock.scale.set(0.5 + Math.random() * 1.0, 0.3 + Math.random() * 0.5, 0.5 + Math.random() * 1.0);
    rock.rotation.set(Math.random(), Math.random(), Math.random());
    waterGroup.add(rock);
  }

  // Bubbles (small spheres that rise)
  const bubbleGeo = new THREE.SphereGeometry(0.03, 6, 6);
  const bubbleMat = new THREE.MeshStandardMaterial({
    color: 0xffffff, transparent: true, opacity: 0.4, roughness: 0.1
  });
  for (let i = 0; i < 15; i++) {
    const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
    bubble.position.set(
      (Math.random() - 0.5) * 8,
      -0.5 + Math.random() * 2,
      (Math.random() - 0.5) * 7
    );
    bubble.userData = { speed: 0.2 + Math.random() * 0.3, startY: bubble.position.y };
    bubbles.push(bubble);
    waterGroup.add(bubble);
  }
}

function createRay(mat) {
  const group = new THREE.Group();

  // Body
  const bodyGeo = new THREE.SphereGeometry(0.5, 12, 8);
  bodyGeo.scale(1.8, 0.3, 1.2);
  const body = new THREE.Mesh(bodyGeo, mat);
  body.castShadow = true;
  group.add(body);

  // Wing fins (left)
  const wingGeo = new THREE.PlaneGeometry(1.2, 0.6, 4, 3);
  const wingLeft = new THREE.Mesh(wingGeo, mat.clone());
  wingLeft.material.side = THREE.DoubleSide;
  wingLeft.position.set(-0.7, 0, 0);
  wingLeft.rotation.x = -Math.PI / 2;
  wingLeft.userData.isWing = true;
  group.add(wingLeft);

  // Wing fins (right)
  const wingRight = new THREE.Mesh(wingGeo, mat.clone());
  wingRight.material.side = THREE.DoubleSide;
  wingRight.position.set(0.7, 0, 0);
  wingRight.rotation.x = -Math.PI / 2;
  wingRight.userData.isWing = true;
  group.add(wingRight);

  // Tail
  const tailGeo = new THREE.PlaneGeometry(0.3, 0.8, 1, 4);
  const tail = new THREE.Mesh(tailGeo, mat.clone());
  tail.material.side = THREE.DoubleSide;
  tail.position.set(0, 0, -1.2);
  tail.rotation.x = -Math.PI / 2;
  tail.userData.isTail = true;
  group.add(tail);

  // Eyes
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x222222 });
  const eyeGeo = new THREE.SphereGeometry(0.05, 6, 6);
  const eye1 = new THREE.Mesh(eyeGeo, eyeMat);
  eye1.position.set(0.15, 0.08, 0.5);
  group.add(eye1);
  const eye2 = new THREE.Mesh(eyeGeo, eyeMat);
  eye2.position.set(-0.15, 0.08, 0.5);
  group.add(eye2);

  group.userData.isRay = true;
  return group;
}

// --- Trees ---
function createTrees() {
  const trunkMat = new THREE.MeshStandardMaterial({ color: 0x5a3a1a, roughness: 0.9 });
  const leafMat = new THREE.MeshStandardMaterial({ color: 0x3a7a2a, roughness: 0.7 });

  const treePositions = [
    [-2.2, 1.8, -1.5], [2.0, 1.6, -2.2], [-1.0, 1.9, -2.8],
    [2.8, 1.4, 0.5], [-3.0, 1.3, 0.2], [1.0, 2.0, -3.2]
  ];

  treePositions.forEach(pos => {
    const tree = new THREE.Group();

    // Trunk
    const trunkH = 1.0 + Math.random() * 0.8;
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.12, trunkH, 6), trunkMat);
    trunk.position.y = trunkH / 2;
    trunk.castShadow = true;
    tree.add(trunk);

    // Foliage layers
    const layers = 2 + Math.floor(Math.random() * 2);
    for (let i = 0; i < layers; i++) {
      const radius = 0.5 - i * 0.12 + Math.random() * 0.1;
      const leafGeo = new THREE.ConeGeometry(radius, 0.6, 7);
      const leaf = new THREE.Mesh(leafGeo, leafMat);
      leaf.position.y = trunkH + i * 0.4 + 0.2;
      leaf.castShadow = true;
      tree.add(leaf);
    }

    tree.position.set(pos[0], pos[1], pos[2]);
    tree.userData.baseRotZ = 0;
    treeMeshes.push(tree);
    islandGroup.add(tree);
  });
}

// --- Additional Details ---
function createDetails() {
  // Small shells on beach (instanced)
  const shellGeo = new THREE.SphereGeometry(0.08, 6, 4);
  shellGeo.scale(1, 0.4, 1.2);
  const shellMat = new THREE.MeshStandardMaterial({ color: 0xf5e6d0, roughness: 0.6 });
  const shellCount = 20;
  const shells = new THREE.InstancedMesh(shellGeo, shellMat, shellCount);
  const dummy = new THREE.Object3D();
  for (let i = 0; i < shellCount; i++) {
    const angle = Math.random() * Math.PI * 2;
    const r = 3.3 + Math.random() * 0.8;
    dummy.position.set(Math.cos(angle) * r, 0.15, Math.sin(angle) * r);
    dummy.rotation.set(0, Math.random() * Math.PI, 0);
    dummy.scale.setScalar(0.5 + Math.random() * 0.5);
    dummy.updateMatrix();
    shells.setMatrixAt(i, dummy.matrix);
  }
  shells.instanceMatrix.needsUpdate = true;
  shells.receiveShadow = true;
  islandGroup.add(shells);

  // Grass tufts (instanced)
  const grassGeo = new THREE.ConeGeometry(0.04, 0.2, 4);
  const grassMat = new THREE.MeshStandardMaterial({ color: 0x5a9a3a, roughness: 0.8 });
  const grassCount = 60;
  const grass = new THREE.InstancedMesh(grassGeo, grassMat, grassCount);
  for (let i = 0; i < grassCount; i++) {
    const angle = Math.random() * Math.PI * 2;
    const r = 1.0 + Math.random() * 2.5;
    dummy.position.set(Math.cos(angle) * r, 1.6 + Math.random() * 0.3, Math.sin(angle) * r);
    dummy.scale.set(1, 1 + Math.random(), 1);
    dummy.updateMatrix();
    grass.setMatrixAt(i, dummy.matrix);
  }
  grass.instanceMatrix.needsUpdate = true;
  islandGroup.add(grass);
}

// --- Orbit Controls (manual implementation) ---
let isDragging = false, prevMouse = { x: 0, y: 0 };
let orbitAngleX = 0.6, orbitAngleY = 0.8, orbitDist = 18;
let targetOrbitAngleX = 0.6, targetOrbitAngleY = 0.8, targetOrbitDist = 18;
let targetLookAt = new THREE.Vector3(0, 1.5, 0);
let currentLookAt = new THREE.Vector3(0, 1.5, 0);
let isOrbitMode = true;

function setupOrbitControls() {
  const canvas = renderer.domElement;

  canvas.addEventListener('mousedown', (e) => {
    isDragging = true;
    prevMouse = { x: e.clientX, y: e.clientY };
  });
  canvas.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const dx = e.clientX - prevMouse.x;
    const dy = e.clientY - prevMouse.y;
    targetOrbitAngleY += dx * 0.005;
    targetOrbitAngleX += dy * 0.005;
    targetOrbitAngleX = Math.max(0.1, Math.min(1.5, targetOrbitAngleX));
    prevMouse = { x: e.clientX, y: e.clientY };
    isOrbitMode = true;
  });
  canvas.addEventListener('mouseup', () => { isDragging = false; });
  canvas.addEventListener('wheel', (e) => {
    targetOrbitDist += e.deltaY * 0.01;
    targetOrbitDist = Math.max(5, Math.min(35, targetOrbitDist));
  });

  // Touch
  canvas.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      isDragging = true;
      prevMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    }
  });
  canvas.addEventListener('touchmove', (e) => {
    if (!isDragging || e.touches.length !== 1) return;
    const dx = e.touches[0].clientX - prevMouse.x;
    const dy = e.touches[0].clientY - prevMouse.y;
    targetOrbitAngleY += dx * 0.005;
    targetOrbitAngleX += dy * 0.005;
    targetOrbitAngleX = Math.max(0.1, Math.min(1.5, targetOrbitAngleX));
    prevMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    isOrbitMode = true;
  });
  canvas.addEventListener('touchend', () => { isDragging = false; });
}

function updateCamera() {
  if (cameraTransition) {
    const t = cameraTransition.progress;
    const ease = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    camera.position.lerpVectors(cameraTransition.from, cameraTransition.to, ease);
    currentLookAt.lerpVectors(cameraTransition.lookFrom, cameraTransition.lookTo, ease);
    camera.lookAt(currentLookAt);
    cameraTransition.progress += 0.015;
    if (cameraTransition.progress >= 1) {
      targetOrbitAngleX = cameraTransition.endAngleX;
      targetOrbitAngleY = cameraTransition.endAngleY;
      targetOrbitDist = cameraTransition.endDist;
      targetLookAt.copy(cameraTransition.lookTo);
      cameraTransition = null;
    }
    return;
  }

  if (isOrbitMode) {
    orbitAngleX += (targetOrbitAngleX - orbitAngleX) * 0.05;
    orbitAngleY += (targetOrbitAngleY - orbitAngleY) * 0.05;
    orbitDist += (targetOrbitDist - orbitDist) * 0.05;
    currentLookAt.lerp(targetLookAt, 0.05);

    camera.position.x = currentLookAt.x + orbitDist * Math.sin(orbitAngleX) * Math.cos(orbitAngleY);
    camera.position.y = currentLookAt.y + orbitDist * Math.cos(orbitAngleX);
    camera.position.z = currentLookAt.z + orbitDist * Math.sin(orbitAngleX) * Math.sin(orbitAngleY);
    camera.lookAt(currentLookAt);
  }
}

// --- UI Setup ---
function setupUI() {
  // Camera buttons
  document.querySelectorAll('[data-cam]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-cam]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cam = btn.dataset.cam;
      transitionCamera(cam);
    });
  });

  // Time buttons
  document.querySelectorAll('[data-time]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-time]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentTime = btn.dataset.time;
      updateLighting();
    });
  });

  // Sliders
  document.getElementById('slider-tide').addEventListener('input', (e) => {
    tideLevel = e.target.value / 100;
    updateTide();
  });
  document.getElementById('slider-wind').addEventListener('input', (e) => {
    windStrength = e.target.value / 100;
  });
  document.getElementById('slider-volume').addEventListener('input', (e) => {
    if (masterGain) masterGain.gain.value = e.target.value / 100;
  });

  // Action buttons
  document.getElementById('btn-kayak').addEventListener('click', toggleKayak);
  document.getElementById('btn-ray').addEventListener('click', triggerRayJump);
  document.getElementById('btn-pause').addEventListener('click', togglePause);
  document.getElementById('btn-reset').addEventListener('click', resetScene);
  document.getElementById('btn-music').addEventListener('click', toggleMusic);

  // Audio enable
  document.getElementById('audio-btn').addEventListener('click', enableAudio);

  // Mobile toggle
  document.getElementById('mobile-toggle').addEventListener('click', () => {
    document.getElementById('controls').classList.toggle('visible');
  });
}

function transitionCamera(type) {
  const from = camera.position.clone();
  const lookFrom = currentLookAt.clone();
  let to, lookTo, endAngleX, endAngleY, endDist;

  switch (type) {
    case 'iso':
      to = new THREE.Vector3(12, 10, 14);
      lookTo = new THREE.Vector3(0, 1.5, 0);
      endAngleX = 0.6; endAngleY = 0.85; endDist = 18;
      break;
    case 'cabin':
      to = new THREE.Vector3(5, 3.5, 6);
      lookTo = new THREE.Vector3(0.5, 2.0, 0.5);
      endAngleX = 0.8; endAngleY = 1.2; endDist = 7;
      break;
    case 'under':
      to = new THREE.Vector3(6, 0.5, 7);
      lookTo = new THREE.Vector3(0, -0.3, 0);
      endAngleX = 1.4; endAngleY = 0.9; endDist = 9;
      break;
    case 'orbit':
      isOrbitMode = true;
      return;
  }

  isOrbitMode = false;
  cameraTransition = { from, to, lookFrom, lookTo, progress: 0, endAngleX, endAngleY, endDist };
}

// --- Interactions ---
function toggleKayak() {
  const btn = document.getElementById('btn-kayak');
  if (kayakState === 'moored') {
    kayakState = 'launching';
    btn.textContent = 'Return Kayak';
    btn.classList.add('active');
  } else if (kayakState === 'launching') {
    kayakState = 'returning';
    btn.textContent = 'Launch Kayak';
    btn.classList.remove('active');
  }
}

function triggerRayJump() {
  if (rayJumping) return;
  rayJumping = true;
  rayJumpTime = 0;
  const btn = document.getElementById('btn-ray');
  btn.classList.add('active');
  setTimeout(() => btn.classList.remove('active'), 3000);

  // Create ripples
  for (let i = 0; i < 3; i++) {
    const rippleGeo = new THREE.RingGeometry(0.1, 0.15, 16);
    rippleGeo.rotateX(-Math.PI / 2);
    const rippleMat = new THREE.MeshBasicMaterial({
      color: 0xffffff, transparent: true, opacity: 0.6, side: THREE.DoubleSide
    });
    const ripple = new THREE.Mesh(rippleGeo, rippleMat);
    ripple.position.set(0, 4.0 + tideLevel * 0.5, 0);
    ripple.userData = { life: 1.0, speed: 2 + i };
    ripples.push(ripple);
    scene.add(ripple);
  }

  // Droplets
  for (let i = 0; i < 8; i++) {
    const dropGeo = new THREE.SphereGeometry(0.04, 4, 4);
    const dropMat = new THREE.MeshStandardMaterial({ color: 0x88ccee, transparent: true, opacity: 0.7 });
    const drop = new THREE.Mesh(dropGeo, dropMat);
    drop.position.set(0, 4.0, 0);
    drop.userData = {
      vel: new THREE.Vector3(
        (Math.random() - 0.5) * 3,
        2 + Math.random() * 3,
        (Math.random() - 0.5) * 3
      ),
      life: 1.5
    };
    droplets.push(drop);
    scene.add(drop);
  }
}

function togglePause() {
  isPaused = !isPaused;
  const btn = document.getElementById('btn-pause');
  btn.textContent = isPaused ? 'Resume' : 'Pause';
  btn.classList.toggle('active', isPaused);
}

function resetScene() {
  // Reset all states
  isPaused = false;
  document.getElementById('btn-pause').textContent = 'Pause';
  document.getElementById('btn-pause').classList.remove('active');

  kayakState = 'moored';
  kayakGroup.position.set(0.3, 0.15, 1.2);
  kayakGroup.rotation.y = 0.3;
  kayakAngle = 0;
  document.getElementById('btn-kayak').textContent = 'Launch Kayak';
  document.getElementById('btn-kayak').classList.remove('active');

  rayJumping = false;
  tideLevel = 0.5;
  document.getElementById('slider-tide').value = 50;
  windStrength = 0.4;
  document.getElementById('slider-wind').value = 40;

  currentTime = 'day';
  document.querySelectorAll('[data-time]').forEach(b => b.classList.remove('active'));
  document.querySelector('[data-time="day"]').classList.add('active');
  updateLighting();

  // Reset camera
  transitionCamera('iso');
  document.querySelectorAll('[data-cam]').forEach(b => b.classList.remove('active'));
  document.querySelector('[data-cam="iso"]').classList.add('active');
}

// --- Tide ---
function updateTide() {
  const waterY = 3.5 + tideLevel * 1.0;
  if (waterMesh) {
    waterMesh.position.y = waterY - 2.75;
    waterMesh.scale.y = 0.5 + tideLevel * 0.5;
  }
  if (waterSurface) {
    waterSurface.position.y = waterY;
  }
  if (foamMesh) {
    foamMesh.material.uniforms.uTide.value = tideLevel;
  }
  // Kayak follows water level
  if (kayakState === 'moored') {
    kayakGroup.position.y = 0.15 + tideLevel * 0.3;
  }
}

// --- Lighting Updates ---
function updateLighting() {
  const targets = {
    day: { sun: 0xfff4e0, sunI: 1.2, amb: 0x6688aa, ambI: 0.4, fog: 0x8fb8c8, exposure: 1.0, cabin: 0, lantern: 0 },
    sunset: { sun: 0xff8844, sunI: 0.9, amb: 0x554466, ambI: 0.3, fog: 0x6a4a5a, exposure: 0.9, cabin: 1.5, lantern: 1.2 },
    night: { sun: 0x334466, sunI: 0.15, amb: 0x1a2244, ambI: 0.2, fog: 0x0a1020, exposure: 0.6, cabin: 2.5, lantern: 2.0 }
  };
  targetLighting = targets[currentTime];
}

function animateLighting() {
  if (!targetLighting.sun) return;
  const lerp = 0.02;
  sunLight.color.lerp(new THREE.Color(targetLighting.sun), lerp);
  sunLight.intensity += (targetLighting.sunI - sunLight.intensity) * lerp;
  ambientLight.color.lerp(new THREE.Color(targetLighting.amb), lerp);
  ambientLight.intensity += (targetLighting.ambI - ambientLight.intensity) * lerp;
  scene.fog.color.lerp(new THREE.Color(targetLighting.fog), lerp);
  renderer.toneMappingExposure += (targetLighting.exposure - renderer.toneMappingExposure) * lerp;

  // Cabin windows
  const targetEmissive = targetLighting.cabin;
  cabinWindows.forEach(w => {
    w.material.emissiveIntensity += (targetEmissive - w.material.emissiveIntensity) * lerp;
  });
  cabinLight.intensity += (targetLighting.cabin * 2 - cabinLight.intensity) * lerp;

  // Lanterns
  lanterns.forEach(l => {
    l.light.intensity += (targetLighting.lantern - l.light.intensity) * lerp;
    l.mesh.material.emissiveIntensity += (targetLighting.lantern * 0.5 - l.mesh.material.emissiveIntensity) * lerp;
  });
  lanternLights.forEach(ll => {
    ll.intensity += (targetLighting.lantern - ll.intensity) * lerp;
  });
}

// --- Audio System ---
function enableAudio() {
  if (audioStarted) return;
  audioStarted = true;
  document.getElementById('audio-btn').style.display = 'none';

  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  masterGain = audioCtx.createGain();
  masterGain.gain.value = 0.6;
  masterGain.connect(audioCtx.destination);

  musicGain = audioCtx.createGain();
  musicGain.gain.value = 0;
  musicGain.connect(masterGain);

  ambienceGain = audioCtx.createGain();
  ambienceGain.gain.value = 0.3;
  ambienceGain.connect(masterGain);

  // Ambient water noise (filtered noise)
  const noiseBuffer = audioCtx.createBuffer(1, audioCtx.sampleRate * 2, audioCtx.sampleRate);
  const data = noiseBuffer.getChannelData(0);
  for (let i = 0; i < data.length; i++) {
    data[i] = (Math.random() * 2 - 1) * 0.3;
  }
  const noiseSource = audioCtx.createBufferSource();
  noiseSource.buffer = noiseBuffer;
  noiseSource.loop = true;
  const noiseFilter = audioCtx.createBiquadFilter();
  noiseFilter.type = 'lowpass';
  noiseFilter.frequency.value = 400;
  const noiseGain = audioCtx.createGain();
  noiseGain.gain.value = 0.15;
  noiseSource.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(ambienceGain);
  noiseSource.start();

  // Breeze (bandpass filtered noise)
  const breezeSource = audioCtx.createBufferSource();
  breezeSource.buffer = noiseBuffer;
  breezeSource.loop = true;
  const breezeFilter = audioCtx.createBiquadFilter();
  breezeFilter.type = 'bandpass';
  breezeFilter.frequency.value = 800;
  breezeFilter.Q.value = 0.5;
  const breezeGain = audioCtx.createGain();
  breezeGain.gain.value = 0.08;
  breezeSource.connect(breezeFilter);
  breezeFilter.connect(breezeGain);
  breezeGain.connect(ambienceGain);
  breezeSource.start();

  // Gentle LFO on breeze
  const lfo = audioCtx.createOscillator();
  lfo.frequency.value = 0.15;
  const lfoGain = audioCtx.createGain();
  lfoGain.gain.value = 200;
  lfo.connect(lfoGain);
  lfoGain.connect(breezeFilter.frequency);
  lfo.start();
}

function toggleMusic() {
  if (!audioStarted) {
    enableAudio();
    return;
  }
  musicPlaying = !musicPlaying;
  const btn = document.getElementById('btn-music');
  btn.textContent = musicPlaying ? 'Music On' : 'Music Off';
  btn.classList.toggle('active', musicPlaying);

  if (musicPlaying) {
    startMusic();
  } else {
    stopMusic();
  }
}

function startMusic() {
  if (musicNodes.length > 0) return;

  // Procedural ambient music - gentle pad with slow arpeggios
  const notes = [220, 261.63, 329.63, 392, 440, 523.25]; // A minor pentatonic-ish
  const baseFreqs = [110, 146.83, 164.81]; // Bass notes

  // Pad - slow evolving chords
  baseFreqs.forEach((freq, i) => {
    const osc = audioCtx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = freq;
    const gain = audioCtx.createGain();
    gain.gain.value = 0;
    gain.gain.linearRampToValueAtTime(0.12, audioCtx.currentTime + 2);

    // Slow detune for warmth
    const osc2 = audioCtx.createOscillator();
    osc2.type = 'sine';
    osc2.frequency.value = freq * 1.002;
    const gain2 = audioCtx.createGain();
    gain2.gain.value = 0;
    gain2.gain.linearRampToValueAtTime(0.08, audioCtx.currentTime + 2);

    osc.connect(gain);
    osc2.connect(gain2);
    gain.connect(musicGain);
    gain2.connect(musicGain);
    osc.start();
    osc2.start();
    musicNodes.push({ osc, osc2, gain, gain2 });
  });

  // Melodic arpeggio
  const arpOsc = audioCtx.createOscillator();
  arpOsc.type = 'triangle';
  arpOsc.frequency.value = notes[0];
  const arpGain = audioCtx.createGain();
  arpGain.gain.value = 0.06;
  arpGain.gain.linearRampToValueAtTime(0.06, audioCtx.currentTime + 1);

  const arpFilter = audioCtx.createBiquadFilter();
  arpFilter.type = 'lowpass';
  arpFilter.frequency.value = 2000;

  arpOsc.connect(arpGain);
  arpGain.connect(arpFilter);
  arpFilter.connect(musicGain);
  arpOsc.start();

  // Cycle through notes
  let noteIdx = 0;
  const arpInterval = setInterval(() => {
    if (!musicPlaying) { clearInterval(arpInterval); return; }
    noteIdx = (noteIdx + 1) % notes.length;
    arpOsc.frequency.linearRampToValueAtTime(notes[noteIdx], audioCtx.currentTime + 0.5);
  }, 2000);

  musicNodes.push({ osc: arpOsc, gain: arpGain, interval: arpInterval });

  musicGain.gain.linearRampToValueAtTime(1, audioCtx.currentTime + 2);
}

function stopMusic() {
  musicNodes.forEach(n => {
    if (n.osc) { n.osc.stop(); }
    if (n.osc2) { n.osc2.stop(); }
    if (n.interval) clearInterval(n.interval);
  });
  musicNodes = [];
  if (musicGain) musicGain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 1);
}

// --- Animation Loop ---
function animate() {
  requestAnimationFrame(animate);

  const delta = clock.getDelta();
  if (!isPaused) {
    animTime += delta;
    updateAnimations(delta);
  }

  updateCamera();
  animateLighting();
  renderer.render(scene, camera);
}

function updateAnimations(delta) {
  // Water surface waves
  if (waterSurface && waterSurface.material.uniforms) {
    waterSurface.material.uniforms.uTime.value = animTime;
    waterSurface.material.uniforms.uWind.value = 0.3 + windStrength * 0.7;
  }

  // Caustics
  if (waterGroup.userData.caustics) {
    waterGroup.userData.caustics.material.uniforms.uTime.value = animTime;
  }

  // Foam
  if (foamMesh) {
    foamMesh.material.uniforms.uTime.value = animTime;
  }

  // Rays
  if (rayGroup) {
    rayGroup.children.forEach((ray, i) => {
      const d = ray.userData;
      if (rayJumping && i === 0) {
        // Ray jump animation
        rayJumpTime += delta;
        const jumpDuration = 2.5;
        const t = rayJumpTime / jumpDuration;

        if (t < 1) {
          // Jump up
          const jumpHeight = 4.5;
          const x = Math.sin(t * Math.PI * 0.5) * 3;
          const y = Math.sin(t * Math.PI) * jumpHeight;
          ray.position.set(x, d.baseY + y, ray.position.z);
          ray.rotation.z = -t * Math.PI * 0.5;
          ray.rotation.x = Math.sin(t * Math.PI) * 0.3;
        } else {
          // Settle back
          ray.position.y = d.baseY;
          ray.position.x = 0;
          ray.rotation.z = 0;
          ray.rotation.x = 0;
          rayJumping = false;
          rayJumpTime = 0;
        }
      } else {
        // Normal swimming
        const angle = animTime * d.speed + d.phase;
        ray.position.x = d.center.x + Math.cos(angle) * d.radius;
        ray.position.z = d.center.z + Math.sin(angle) * d.radius;
        ray.position.y = d.baseY + Math.sin(animTime * 0.5 + d.phase) * 0.2;
        ray.rotation.y = angle + Math.PI / 2;

        // Undulating fins
        ray.children.forEach(child => {
          if (child.userData.isWing) {
            const wingWave = Math.sin(animTime * 2 + d.phase) * 0.15;
            child.rotation.z = wingWave * (child.position.x > 0 ? 1 : -1);
          }
          if (child.userData.isTail) {
            child.rotation.y = Math.sin(animTime * 3 + d.phase) * 0.2;
          }
        });
      }
    });
  }

  // Fish school
  if (fishInstances) {
    const dummy = new THREE.Object3D();
    for (let i = 0; i < 40; i++) {
      fishInstances.getMatrixAt(i, dummy.matrix);
      dummy.matrix.decompose(dummy.position, dummy.quaternion, dummy.scale);

      // Gentle swimming motion
      dummy.position.x += Math.sin(animTime * 0.8 + i * 0.5) * 0.002;
      dummy.position.z += Math.cos(animTime * 0.6 + i * 0.3) * 0.002;
      dummy.position.y += Math.sin(animTime * 1.2 + i * 0.7) * 0.001;

      // Keep in bounds
      if (Math.abs(dummy.position.x) > 6) dummy.position.x *= -0.9;
      if (Math.abs(dummy.position.z) > 5) dummy.position.z *= -0.9;

      // Slight rotation variation
      dummy.rotation.y += Math.sin(animTime + i) * 0.01;

      dummy.updateMatrix();
      fishInstances.setMatrixAt(i, dummy.matrix);
    }
    fishInstances.instanceMatrix.needsUpdate = true;
  }

  // Aquatic plants swaying
  if (plantInstances) {
    const dummy = new THREE.Object3D();
    for (let i = 0; i < 25; i++) {
      plantInstances.getMatrixAt(i, dummy.matrix);
      dummy.matrix.decompose(dummy.position, dummy.quaternion, dummy.scale);
      dummy.rotation.z = Math.sin(animTime * 1.5 + i * 0.8) * 0.1 * windStrength;
      dummy.rotation.x = Math.sin(animTime * 1.2 + i * 0.5) * 0.05 * windStrength;
      dummy.updateMatrix();
      plantInstances.setMatrixAt(i, dummy.matrix);
    }
    plantInstances.instanceMatrix.needsUpdate = true;
  }

  // Trees swaying
  treeMeshes.forEach((tree, i) => {
    const sway = Math.sin(animTime * 1.5 + i * 1.2) * 0.03 * windStrength;
    tree.rotation.z = sway;
    tree.rotation.x = Math.sin(animTime * 1.2 + i * 0.8) * 0.02 * windStrength;
  });

  // Bubbles rising
  bubbles.forEach(bubble => {
    bubble.position.y += bubble.userData.speed * delta;
    bubble.position.x += Math.sin(animTime * 2 + bubble.position.z) * 0.001;
    if (bubble.position.y > 3.5 + tideLevel) {
      bubble.position.y = -0.5;
      bubble.position.x = (Math.random() - 0.5) * 8;
      bubble.position.z = (Math.random() - 0.5) * 7;
    }
  });

  // Ripples
  for (let i = ripples.length - 1; i >= 0; i--) {
    const r = ripples[i];
    r.userData.life -= delta;
    r.scale.setScalar(1 + r.userData.life * -1 + 1);
    const scale = (1 - r.userData.life) * r.userData.speed * 2;
    r.scale.set(scale, 1, scale);
    r.material.opacity = r.userData.life * 0.5;
    r.position.y = 3.5 + tideLevel * 0.5;
    if (r.userData.life <= 0) {
      scene.remove(r);
      r.geometry.dispose();
      r.material.dispose();
      ripples.splice(i, 1);
    }
  }

  // Droplets
  for (let i = droplets.length - 1; i >= 0; i--) {
    const d = droplets[i];
    d.userData.life -= delta;
    d.userData.vel.y -= 9.8 * delta;
    d.position.add(d.userData.vel.clone().multiplyScalar(delta));
    d.material.opacity = Math.max(0, d.userData.life / 1.5) * 0.7;
    if (d.userData.life <= 0 || d.position.y < 3.5 + tideLevel * 0.5) {
      scene.remove(d);
      d.geometry.dispose();
      d.material.dispose();
      droplets.splice(i, 1);
    }
  }

  // Kayak movement
  if (kayakState === 'launching') {
    kayakAngle += delta * 0.4;
    if (kayakAngle >= Math.PI * 2) {
      kayakAngle = 0;
      kayakState = 'returning';
    }
    const radius = 5;
    kayakGroup.position.x = Math.cos(kayakAngle) * radius + 3.5;
    kayakGroup.position.z = Math.sin(kayakAngle) * radius + 2.5;
    kayakGroup.position.y = 0.15 + tideLevel * 0.3 + Math.sin(animTime * 2) * 0.05;
    kayakGroup.rotation.y = kayakAngle + Math.PI / 2;
  } else if (kayakState === 'returning') {
    const targetX = 3.8;
    const targetZ = 3.7;
    kayakGroup.position.x += (targetX - kayakGroup.position.x) * delta * 2;
    kayakGroup.position.z += (targetZ - kayakGroup.position.z) * delta * 2;
    kayakGroup.position.y = 0.15 + tideLevel * 0.3 + Math.sin(animTime * 2) * 0.05;
    kayakGroup.rotation.y += (0.3 - kayakGroup.rotation.y) * delta * 2;

    if (Math.abs(kayakGroup.position.x - targetX) < 0.1) {
      kayakState = 'moored';
      document.getElementById('btn-kayak').textContent = 'Launch Kayak';
    }
  } else {
    // Bobbing on water
    kayakGroup.position.y = 0.15 + tideLevel * 0.3 + Math.sin(animTime * 1.5) * 0.04;
    kayakGroup.rotation.z = Math.sin(animTime * 1.2) * 0.03;
  }

  // Water volume follows tide
  if (waterMesh) {
    const targetY = 3.5 + tideLevel * 1.0 - 2.75;
    waterMesh.position.y += (targetY - waterMesh.position.y) * delta * 2;
  }
  if (waterSurface) {
    const targetY = 3.5 + tideLevel * 1.0;
    waterSurface.position.y += (targetY - waterSurface.position.y) * delta * 2;
  }
}

// --- Window Resize ---
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// --- Start ---
updateLighting();
init();
</script>
</body>
</html>
```

This is a complete, self-contained `index.html` file that creates **Tidehaven** — an interactive 3D coastal diorama. Here's what's included:

**Visual Features:**
- Procedural island with vertex-colored terrain (grass → earth → sand → underwater)
- A-frame cabin with copper roof, glowing windows, deck, bench, crates, towel, plant
- Wooden pier with ladder, 3 lanterns, moored kayak with paddle
- Cutaway glass diorama box revealing the water cross-section
- Animated water surface with wave shader, shoreline foam ring, animated caustics on seabed
- Rising bubbles, expanding ripples, droplet particles

**Underwater Life:**
- 3 rays with undulating fins and tails swimming in circular paths
- 40 instanced fish with gentle swimming motion
- 25 instanced aquatic plants swaying with wind
- Underwater rocks

**Interactions:**
- **Camera presets** (Isometric, Cabin, Underwater, Free Orbit) with smooth cubic-eased transitions
- **Kayak** launches on a circular trip, then returns to the pier
- **Ray Leap** sends a ray jumping out of the water with ripple rings and splash droplets
- **Tide slider** raises/lowers water level (kayak, foam, surface all follow)
- **Wind slider** affects wave amplitude, tree sway, and plant motion
- **Time of Day** (Day/Sunset/Night) with smooth interpolated lighting, fog, and emissive windows/lanterns
- **Pause/Resume** and **Reset**

**Technical:**
- Delta-time-based animations throughout
- InstancedMesh for fish, plants, shells, and grass
- Custom ShaderMaterial for water surface, caustics, and foam
- Capped `devicePixelRatio` at 2 for performance
- Proper resize handling
- Responsive mobile layout with collapsible panel

**Audio:**
- Procedural ambient pad (layered sine oscillators with slight detune)
- Slow melodic arpeggio cycling through pentatonic notes
- Filtered noise for water ambience and breeze
- Master volume slider
- Audio starts only after user interaction (button click)