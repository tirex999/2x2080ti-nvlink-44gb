```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Tidehaven</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; background: #1a1a2e; font-family: 'Segoe UI', system-ui, sans-serif; }
canvas { display: block; }

#ui-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 10;
}

#title-panel {
  position: absolute; top: 20px; left: 20px;
  background: rgba(15, 25, 40, 0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;
  padding: 16px 24px; pointer-events: auto;
}
#title-panel h1 {
  font-size: 28px; font-weight: 300; color: #e8f4f8;
  letter-spacing: 3px; margin-bottom: 4px;
}
#title-panel p {
  font-size: 12px; color: rgba(200, 230, 240, 0.7);
  letter-spacing: 1px; font-weight: 300;
}

#controls-panel {
  position: absolute; top: 20px; right: 20px;
  background: rgba(15, 25, 40, 0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;
  padding: 16px; pointer-events: auto; width: 240px;
  max-height: calc(100vh - 40px); overflow-y: auto;
}
#controls-panel::-webkit-scrollbar { width: 4px; }
#controls-panel::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 2px; }

.control-section { margin-bottom: 14px; }
.control-section:last-child { margin-bottom: 0; }
.control-label {
  font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px;
  color: rgba(200, 230, 240, 0.6); margin-bottom: 6px; font-weight: 500;
}

.btn-row { display: flex; gap: 6px; flex-wrap: wrap; }
.btn {
  padding: 7px 12px; border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.05); color: #c8e6f0;
  border-radius: 8px; font-size: 11px; cursor: pointer;
  transition: all 0.2s; font-family: inherit; letter-spacing: 0.5px;
}
.btn:hover { background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.3); }
.btn.active { background: rgba(100, 200, 220, 0.25); border-color: rgba(100, 200, 220, 0.5); color: #fff; }

.slider-container { display: flex; align-items: center; gap: 8px; }
.slider-container input[type="range"] {
  flex: 1; -webkit-appearance: none; height: 4px;
  background: rgba(255,255,255,0.15); border-radius: 2px; outline: none;
}
.slider-container input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 14px; height: 14px;
  background: #64c8dc; border-radius: 50%; cursor: pointer;
}
.slider-value { font-size: 10px; color: rgba(200,230,240,0.5); min-width: 28px; text-align: right; }

#mobile-toggle {
  display: none; position: absolute; top: 20px; right: 20px;
  background: rgba(15, 25, 40, 0.8); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px; padding: 10px 14px; color: #c8e6f0;
  font-size: 18px; cursor: pointer; pointer-events: auto; z-index: 20;
}

#audio-panel {
  position: absolute; bottom: 20px; left: 20px;
  background: rgba(15, 25, 40, 0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;
  padding: 12px 16px; pointer-events: auto;
  display: flex; align-items: center; gap: 12px;
}
#audio-panel .btn { padding: 6px 10px; }
#audio-panel input[type="range"] {
  width: 80px; -webkit-appearance: none; height: 3px;
  background: rgba(255,255,255,0.15); border-radius: 2px; outline: none;
}
#audio-panel input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 12px; height: 12px;
  background: #64c8dc; border-radius: 50%; cursor: pointer;
}

@media (max-width: 768px) {
  #title-panel { top: 12px; left: 12px; padding: 12px 16px; }
  #title-panel h1 { font-size: 20px; }
  #controls-panel {
    top: auto; bottom: 70px; right: 12px; left: 12px;
    width: auto; max-height: 50vh; transform: translateY(120%);
    transition: transform 0.3s ease;
  }
  #controls-panel.open { transform: translateY(0); }
  #mobile-toggle { display: block; }
  #audio-panel { bottom: 12px; left: 12px; right: 12px; justify-content: center; }
}
</style>
</head>
<body>
<div id="ui-overlay">
  <div id="title-panel">
    <h1>Tidehaven</h1>
    <p>A cozy island diorama</p>
  </div>
  <button id="mobile-toggle">☰</button>
  <div id="controls-panel">
    <div class="control-section">
      <div class="control-label">Camera</div>
      <div class="btn-row">
        <button class="btn active" data-cam="iso">Isometric</button>
        <button class="btn" data-cam="cabin">Cabin</button>
        <button class="btn" data-cam="under">Underwater</button>
        <button class="btn" data-cam="orbit">Free</button>
      </div>
    </div>
    <div class="control-section">
      <div class="control-label">Time of Day</div>
      <div class="btn-row">
        <button class="btn active" data-time="day">Day</button>
        <button class="btn" data-time="sunset">Sunset</button>
        <button class="btn" data-time="night">Night</button>
      </div>
    </div>
    <div class="control-section">
      <div class="control-label">Actions</div>
      <div class="btn-row">
        <button class="btn" id="btn-kayak">Launch Kayak</button>
        <button class="btn" id="btn-ray">Ray Leap</button>
      </div>
    </div>
    <div class="control-section">
      <div class="control-label">Tide Level</div>
      <div class="slider-container">
        <input type="range" id="slider-tide" min="0" max="100" value="50">
        <span class="slider-value" id="val-tide">50%</span>
      </div>
    </div>
    <div class="control-section">
      <div class="control-label">Wind</div>
      <div class="slider-container">
        <input type="range" id="slider-wind" min="0" max="100" value="30">
        <span class="slider-value" id="val-wind">30%</span>
      </div>
    </div>
    <div class="control-section">
      <div class="control-label">Quality</div>
      <div class="btn-row">
        <button class="btn" data-quality="low">Low</button>
        <button class="btn active" data-quality="med">Med</button>
        <button class="btn" data-quality="high">High</button>
      </div>
    </div>
    <div class="control-section">
      <div class="control-label">World</div>
      <div class="btn-row">
        <button class="btn" id="btn-pause">Pause</button>
        <button class="btn" id="btn-reset">Reset</button>
      </div>
    </div>
  </div>
  <div id="audio-panel">
    <button class="btn" id="btn-music">♪ Music</button>
    <input type="range" id="slider-volume" min="0" max="100" value="60">
  </div>
</div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ============ GLOBALS ============
let scene, camera, renderer, controls, clock;
let paused = false, quality = 'med';
let timeOfDay = 'day', targetTime = 'day';
let tideLevel = 0.5, windStrength = 0.3;
let audioStarted = false, musicPlaying = false;
let audioCtx, masterGain, musicGain, sfxGain;
let waterSurface, waterGroup, dioramaGroup;
let kayak, kayakLaunched = false, kayakAngle = 0;
let rayMeshes = [], fishSchools = [], seaPlants = [];
let lanternLights = [], cabinWindowLight;
let bubbles = [], ripples = [];
let animTime = 0;
let cameraTransition = null;

// Camera presets
const CAM_PRESETS = {
  iso: { pos: new THREE.Vector3(8, 7, 8), target: new THREE.Vector3(0, 0.5, 0) },
  cabin: { pos: new THREE.Vector3(3, 2.5, 4), target: new THREE.Vector3(0.5, 1.5, 0) },
  under: { pos: new THREE.Vector3(4, -1, 3), target: new THREE.Vector3(0, -1, 0) },
  orbit: null
};

// ============ INIT ============
function init() {
  clock = new THREE.Clock();
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x87ceeb, 0.015);

  camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.copy(CAM_PRESETS.iso.pos);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  document.body.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.copy(CAM_PRESETS.iso.target);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.maxPolarAngle = Math.PI * 0.85;
  controls.minDistance = 3;
  controls.maxDistance = 20;
  controls.update();

  setupLighting();
  buildDiorama();
  buildIsland();
  buildCabin();
  buildPier();
  buildWater();
  buildUnderwaterLife();
  buildDetails();
  setupUI();

  window.addEventListener('resize', onResize);
  animate();
}

// ============ LIGHTING ============
let sunLight, ambientLight, hemisphereLight, fillLight;

function setupLighting() {
  ambientLight = new THREE.AmbientLight(0x404060, 0.4);
  scene.add(ambientLight);

  hemisphereLight = new THREE.HemisphereLight(0x87ceeb, 0x3d5c3a, 0.5);
  scene.add(hemisphereLight);

  sunLight = new THREE.DirectionalLight(0xffeedd, 1.2);
  sunLight.position.set(5, 8, 3);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(2048, 2048);
  sunLight.shadow.camera.near = 0.5;
  sunLight.shadow.camera.far = 30;
  sunLight.shadow.camera.left = -8;
  sunLight.shadow.camera.right = 8;
  sunLight.shadow.camera.top = 8;
  sunLight.shadow.camera.bottom = -8;
  sunLight.shadow.bias = -0.001;
  scene.add(sunLight);

  fillLight = new THREE.DirectionalLight(0x8899bb, 0.3);
  fillLight.position.set(-3, 4, -5);
  scene.add(fillLight);
}

function updateLighting(t) {
  const presets = {
    day: { sun: 0xffeedd, sunI: 1.2, amb: 0x404060, ambI: 0.4, hemi: [0x87ceeb, 0x3d5c3a], hemiI: 0.5, fog: 0x87ceeb, exposure: 1.0 },
    sunset: { sun: 0xff8844, sunI: 1.0, amb: 0x302040, ambI: 0.3, hemi: [0xff9966, 0x2a1a3a], hemiI: 0.4, fog: 0xff9966, exposure: 0.9 },
    night: { sun: 0x4466aa, sunI: 0.2, amb: 0x101030, ambI: 0.2, hemi: [0x112244, 0x0a0a1a], hemiI: 0.2, fog: 0x0a1020, exposure: 0.6 }
  };
  const p = presets[targetTime];
  const lerpFactor = Math.min(t * 2, 1);

  sunLight.color.lerp(new THREE.Color(p.sun), lerpFactor);
  sunLight.intensity += (p.sunI - sunLight.intensity) * lerpFactor;
  ambientLight.color.lerp(new THREE.Color(p.amb), lerpFactor);
  ambientLight.intensity += (p.ambI - ambientLight.intensity) * lerpFactor;
  hemisphereLight.color.lerp(new THREE.Color(p.hemi[0]), lerpFactor);
  hemisphereLight.groundColor.lerp(new THREE.Color(p.hemi[1]), lerpFactor);
  hemisphereLight.intensity += (p.hemiI - hemisphereLight.intensity) * lerpFactor;
  scene.fog.color.lerp(new THREE.Color(p.fog), lerpFactor);
  renderer.toneMappingExposure += (p.exposure - renderer.toneMappingExposure) * lerpFactor;

  // Lanterns and cabin windows
  const isEvening = targetTime === 'sunset' || targetTime === 'night';
  const targetIntensity = isEvening ? (targetTime === 'night' ? 2.0 : 1.0) : 0;
  lanternLights.forEach(l => { l.intensity += (targetIntensity - l.intensity) * lerpFactor; });
  if (cabinWindowLight) {
    cabinWindowLight.intensity += (targetIntensity * 1.5 - cabinWindowLight.intensity) * lerpFactor;
  }
}

// ============ DIORAMA ============
function buildDiorama() {
  dioramaGroup = new THREE.Group();
  scene.add(dioramaGroup);

  // Glass container (aquarium walls)
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, transparent: true, opacity: 0.08,
    roughness: 0.05, metalness: 0.0, transmission: 0.95,
    side: THREE.DoubleSide, depthWrite: false
  });

  const boxW = 10, boxH = 6, boxD = 10;
  // Front face
  const frontGeo = new THREE.PlaneGeometry(boxW, boxH);
  const front = new THREE.Mesh(frontGeo, glassMat);
  front.position.set(0, boxH/2 - 2, boxD/2);
  front.renderOrder = 100;
  dioramaGroup.add(front);

  // Right face
  const right = new THREE.Mesh(frontGeo, glassMat);
  right.rotation.y = -Math.PI / 2;
  right.position.set(boxW/2, boxH/2 - 2, 0);
  right.renderOrder = 100;
  dioramaGroup.add(right);

  // Frame edges
  const frameMat = new THREE.MeshStandardMaterial({ color: 0x2a3a4a, roughness: 0.6, metalness: 0.3 });
  const frameGeo = new THREE.BoxGeometry(0.08, boxH, 0.08);
  const corners = [
    [boxW/2, boxH/2-2, boxD/2], [-boxW/2, boxH/2-2, boxD/2],
    [boxW/2, boxH/2-2, -boxD/2], [-boxW/2, boxH/2-2, -boxD/2]
  ];
  corners.forEach(p => {
    const f = new THREE.Mesh(frameGeo, frameMat);
    f.position.set(...p);
    dioramaGroup.add(f);
  });

  // Top/bottom frame
  const topFrameGeo = new THREE.BoxGeometry(boxW, 0.08, 0.08);
  [[0, boxH-2, boxD/2], [0, -2, boxD/2], [0, boxH-2, -boxD/2], [0, -2, -boxD/2]].forEach(p => {
    const f = new THREE.Mesh(topFrameGeo, frameMat);
    f.position.set(...p);
    dioramaGroup.add(f);
  });

  const sideFrameGeo = new THREE.BoxGeometry(0.08, 0.08, boxD);
  [[boxW/2, boxH-2, 0], [boxW/2, -2, 0], [-boxW/2, boxH-2, 0], [-boxW/2, -2, 0]].forEach(p => {
    const f = new THREE.Mesh(sideFrameGeo, frameMat);
    f.position.set(...p);
    dioramaGroup.add(f);
  });

  // Base platform
  const baseGeo = new THREE.BoxGeometry(boxW + 0.4, 0.3, boxD + 0.4);
  const baseMat = new THREE.MeshStandardMaterial({ color: 0x1a2530, roughness: 0.8 });
  const base = new THREE.Mesh(baseGeo, baseMat);
  base.position.set(0, -2.15, 0);
  base.receiveShadow = true;
  dioramaGroup.add(base);
}

// ============ ISLAND ============
function buildIsland() {
  // Main island shape - procedural terrain
  const islandGroup = new THREE.Group();
  dioramaGroup.add(islandGroup);

  // Sandy shore (underwater base)
  const shoreGeo = new THREE.CylinderGeometry(3.5, 4.2, 1.5, 32, 1);
  const shoreMat = new THREE.MeshStandardMaterial({ color: 0xd4a86a, roughness: 0.9 });
  const shore = new THREE.Mesh(shoreGeo, shoreMat);
  shore.position.set(0, -1.2, 0);
  shore.receiveShadow = true;
  islandGroup.add(shore);

  // Main landmass
  const landGeo = new THREE.CylinderGeometry(2.5, 3.2, 2.5, 24, 4);
  const positions = landGeo.attributes.position;
  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i), y = positions.getY(i), z = positions.getZ(i);
    const dist = Math.sqrt(x*x + z*z);
    if (y > 0.5) {
      positions.setY(i, y + Math.sin(dist * 2) * 0.2 + (Math.random() - 0.5) * 0.1);
    }
    // Add noise to edges
    if (dist > 2.0) {
      positions.setX(i, x + (Math.random() - 0.5) * 0.3);
      positions.setZ(i, z + (Math.random() - 0.5) * 0.3);
    }
  }
  landGeo.computeVertexNormals();
  const landMat = new THREE.MeshStandardMaterial({ color: 0x5a8a4a, roughness: 0.85 });
  const land = new THREE.Mesh(landGeo, landMat);
  land.position.set(0, 0.5, 0);
  land.castShadow = true;
  land.receiveShadow = true;
  islandGroup.add(land);

  // Sandy beach ring
  const beachGeo = new THREE.CylinderGeometry(3.0, 3.5, 0.6, 32, 1);
  const beachMat = new THREE.MeshStandardMaterial({ color: 0xe8c87a, roughness: 0.95 });
  const beach = new THREE.Mesh(beachGeo, beachMat);
  beach.position.set(0, -0.3, 0);
  beach.receiveShadow = true;
  islandGroup.add(beach);

  // Rocks
  const rockMat = new THREE.MeshStandardMaterial({ color: 0x6a6a72, roughness: 0.9 });
  const rockGeo = new THREE.DodecahedronGeometry(0.3, 1);
  const rockPositions = [
    [2.8, -0.2, 1.5], [-2.5, -0.1, 2.0], [1.5, -0.3, -2.8],
    [-1.8, -0.2, -2.2], [3.0, -0.5, -0.5], [-2.8, -0.4, 0.5]
  ];
  rockPositions.forEach(p => {
    const rock = new THREE.Mesh(rockGeo, rockMat);
    rock.position.set(...p);
    rock.scale.set(0.7 + Math.random()*0.6, 0.5 + Math.random()*0.4, 0.7 + Math.random()*0.6);
    rock.rotation.set(Math.random(), Math.random(), Math.random());
    rock.castShadow = true;
    islandGroup.add(rock);
  });

  // Trees (instanced)
  buildTrees(islandGroup);
}

function buildTrees(parent) {
  const trunkGeo = new THREE.CylinderGeometry(0.06, 0.1, 0.8, 8);
  const trunkMat = new THREE.MeshStandardMaterial({ color: 0x6b4226, roughness: 0.9 });
  const leafGeo = new THREE.ConeGeometry(0.4, 0.9, 8);
  const leafMat = new THREE.MeshStandardMaterial({ color: 0x2d7a3a, roughness: 0.8 });

  const treePositions = [
    [-1.2, 1.5, -0.8], [0.8, 1.4, -1.5], [-0.5, 1.3, 1.2],
    [1.5, 1.2, 0.8], [-1.5, 1.1, 0.5], [0.3, 1.5, -0.3]
  ];

  treePositions.forEach((pos, i) => {
    const tree = new THREE.Group();
    const trunk = new THREE.Mesh(trunkGeo, trunkMat);
    trunk.position.y = 0.4;
    trunk.castShadow = true;
    tree.add(trunk);

    // Multiple leaf layers
    for (let l = 0; l < 3; l++) {
      const leaf = new THREE.Mesh(leafGeo, leafMat);
      leaf.position.y = 0.8 + l * 0.35;
      leaf.scale.setScalar(1 - l * 0.25);
      leaf.castShadow = true;
      tree.add(leaf);
    }

    tree.position.set(...pos);
    tree.scale.setScalar(0.7 + Math.random() * 0.5);
    tree.userData.swayOffset = Math.random() * Math.PI * 2;
    parent.add(tree);
    seaPlants.push(tree); // reuse for wind animation
  });
}

// ============ CABIN ============
function buildCabin() {
  const cabinGroup = new THREE.Group();
  cabinGroup.position.set(0.5, 1.5, 0.3);
  dioramaGroup.add(cabinGroup);

  // A-frame structure
  const frameMat = new THREE.MeshStandardMaterial({ color: 0x8b6b4a, roughness: 0.85 });
  const copperMat = new THREE.MeshStandardMaterial({ color: 0x4a8a7a, roughness: 0.3, metalness: 0.7 });

  // A-frame walls (triangular)
  const wallShape = new THREE.Shape();
  wallShape.moveTo(-0.7, 0);
  wallShape.lineTo(0.7, 0);
  wallShape.lineTo(0, 1.4);
  wallShape.closePath();

  const wallGeo = new THREE.ExtrudeGeometry(wallShape, { depth: 1.2, bevelEnabled: false });
  const wall1 = new THREE.Mesh(wallGeo, frameMat);
  wall1.position.set(0, 0, -0.6);
  wall1.castShadow = true;
  cabinGroup.add(wall1);

  // Roof panels (copper)
  const roofGeo = new THREE.PlaneGeometry(1.6, 1.2);
  const roof1 = new THREE.Mesh(roofGeo, copperMat);
  roof1.position.set(-0.35, 0.85, 0);
  roof1.rotation.set(0, 0, Math.atan2(1.4, 0.7));
  roof1.castShadow = true;
  cabinGroup.add(roof1);

  const roof2 = new THREE.Mesh(roofGeo, copperMat);
  roof2.position.set(0.35, 0.85, 0);
  roof2.rotation.set(0, 0, -Math.atan2(1.4, 0.7));
  roof2.castShadow = true;
  cabinGroup.add(roof2);

  // Floor
  const floorGeo = new THREE.BoxGeometry(1.5, 0.08, 1.3);
  const floor = new THREE.Mesh(floorGeo, frameMat);
  floor.position.set(0, 0.02, 0);
  cabinGroup.add(floor);

  // Windows (glowing)
  const windowMat = new THREE.MeshStandardMaterial({
    color: 0xffcc44, emissive: 0xffaa22, emissiveIntensity: 0.5
  });
  const windowGeo = new THREE.PlaneGeometry(0.3, 0.4);

  const win1 = new THREE.Mesh(windowGeo, windowMat);
  win1.position.set(0, 0.6, 0.61);
  cabinGroup.add(win1);

  const win2 = new THREE.Mesh(windowGeo, windowMat);
  win2.position.set(-0.71, 0.5, 0);
  win2.rotation.y = Math.PI / 2;
  cabinGroup.add(win2);

  // Window light
  cabinWindowLight = new THREE.PointLight(0xffaa44, 0, 3);
  cabinWindowLight.position.set(0.5, 2.1, 0.3);
  dioramaGroup.add(cabinWindowLight);

  // Deck
  const deckGeo = new THREE.BoxGeometry(1.8, 0.06, 1.0);
  const deckMat = new THREE.MeshStandardMaterial({ color: 0x9a7b5a, roughness: 0.9 });
  const deck = new THREE.Mesh(deckGeo, deckMat);
  deck.position.set(0, -0.02, 1.1);
  deck.receiveShadow = true;
  cabinGroup.add(deck);

  // Deck planks (detail lines)
  const plankGeo = new THREE.BoxGeometry(1.8, 0.02, 0.02);
  const plankMat = new THREE.MeshStandardMaterial({ color: 0x7a5b3a, roughness: 0.9 });
  for (let i = 0; i < 8; i++) {
    const plank = new THREE.Mesh(plankGeo, plankMat);
    plank.position.set(0, 0.02, 0.7 + i * 0.12);
    cabinGroup.add(plank);
  }

  // Door
  const doorGeo = new THREE.PlaneGeometry(0.35, 0.6);
  const doorMat = new THREE.MeshStandardMaterial({ color: 0x5a3a2a, roughness: 0.9 });
  const door = new THREE.Mesh(doorGeo, doorMat);
  door.position.set(0, 0.3, 0.61);
  cabinGroup.add(door);
}

// ============ PIER ============
function buildPier() {
  const pierGroup = new THREE.Group();
  pierGroup.position.set(2.5, 0.2, 2.0);
  pierGroup.rotation.y = -0.3;
  dioramaGroup.add(pierGroup);

  const woodMat = new THREE.MeshStandardMaterial({ color: 0x8a6b4a, roughness: 0.9 });
  const darkWoodMat = new THREE.MeshStandardMaterial({ color: 0x5a4030, roughness: 0.9 });

  // Pier planks
  const plankGeo = new THREE.BoxGeometry(0.8, 0.05, 0.15);
  for (let i = 0; i < 14; i++) {
    const plank = new THREE.Mesh(plankGeo, woodMat);
    plank.position.set(0, 0, i * 0.17);
    plank.castShadow = true;
    plank.receiveShadow = true;
    pierGroup.add(plank);
  }

  // Support posts
  const postGeo = new THREE.CylinderGeometry(0.04, 0.05, 2.5, 8);
  [[-0.35, 0], [0.35, 0], [-0.35, 1.2], [0.35, 1.2], [-0.35, 2.2], [0.35, 2.2]].forEach(p => {
    const post = new THREE.Mesh(postGeo, darkWoodMat);
    post.position.set(p[0], -1.2, p[1]);
    post.castShadow = true;
    pierGroup.add(post);
  });

  // Railings
  const railGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.6, 6);
  [-0.38, 0.38].forEach(x => {
    [0.5, 1.5, 2.2].forEach(z => {
      const rail = new THREE.Mesh(railGeo, darkWoodMat);
      rail.position.set(x, 0.3, z);
      pierGroup.add(rail);
    });
  });
  const railTopGeo = new THREE.CylinderGeometry(0.02, 0.02, 2.0, 6);
  [-0.38, 0.38].forEach(x => {
    const rail = new THREE.Mesh(railTopGeo, darkWoodMat);
    rail.rotation.x = Math.PI / 2;
    rail.position.set(x, 0.6, 1.35);
    pierGroup.add(rail);
  });

  // Ladder
  const ladderGroup = new THREE.Group();
  ladderGroup.position.set(0.38, -0.5, 2.3);
  const ladderSideGeo = new THREE.CylinderGeometry(0.02, 0.02, 1.5, 6);
  [-0.1, 0.1].forEach(x => {
    const side = new THREE.Mesh(ladderSideGeo, darkWoodMat);
    side.position.set(x, 0, 0);
    ladderGroup.add(side);
  });
  for (let i = 0; i < 5; i++) {
    const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.2, 6), darkWoodMat);
    rung.rotation.z = Math.PI / 2;
    rung.position.set(0, -0.5 + i * 0.3, 0);
    ladderGroup.add(rung);
  }
  pierGroup.add(ladderGroup);

  // Lanterns on pier
  const lanternGeo = new THREE.BoxGeometry(0.1, 0.15, 0.1);
  const lanternMat = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.5, metalness: 0.5 });
  const lanternGlowMat = new THREE.MeshStandardMaterial({ color: 0xffcc44, emissive: 0xffaa22, emissiveIntensity: 0.3 });

  [[-0.38, 0.7, 0.5], [0.38, 0.7, 1.5], [-0.38, 0.7, 2.2]].forEach(p => {
    const lantern = new THREE.Group();
    const body = new THREE.Mesh(lanternGeo, lanternMat);
    lantern.add(body);
    const glow = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.1, 0.06), lanternGlowMat);
    glow.position.y = -0.02;
    lantern.add(glow);

    const light = new THREE.PointLight(0xffaa44, 0, 2);
    light.position.set(0, 0, 0);
    lantern.add(light);
    lanternLights.push(light);

    lantern.position.set(...p);
    pierGroup.add(lantern);
  });

  // Kayak
  buildKayak(pierGroup);
}

function buildKayak(parent) {
  const kayakGroup = new THREE.Group();

  // Hull
  const hullShape = new THREE.Shape();
  hullShape.moveTo(0, -0.6);
  hullShape.quadraticCurveTo(0.2, -0.3, 0.18, 0);
  hullShape.quadraticCurveTo(0.15, 0.4, 0, 0.6);
  hullShape.quadraticCurveTo(-0.15, 0.4, -0.18, 0);
  hullShape.quadraticCurveTo(-0.2, -0.3, 0, -0.6);

  const hullGeo = new THREE.ExtrudeGeometry(hullShape, { depth: 0.12, bevelEnabled: true, bevelSize: 0.02, bevelThickness: 0.02 });
  const hullMat = new THREE.MeshStandardMaterial({ color: 0xcc4444, roughness: 0.4 });
  const hull = new THREE.Mesh(hullGeo, hullMat);
  hull.rotation.x = -Math.PI / 2;
  hull.position.y = 0.05;
  hull.castShadow = true;
  kayakGroup.add(hull);

  // Interior
  const intGeo = new THREE.BoxGeometry(0.2, 0.05, 0.8);
  const intMat = new THREE.MeshStandardMaterial({ color: 0x882222, roughness: 0.7 });
  const interior = new THREE.Mesh(intGeo, intMat);
  interior.position.y = 0.12;
  kayakGroup.add(interior);

  // Paddle
  const paddleGeo = new THREE.CylinderGeometry(0.01, 0.01, 0.9, 6);
  const paddleMat = new THREE.MeshStandardMaterial({ color: 0x6a5030, roughness: 0.8 });
  const paddle = new THREE.Mesh(paddleGeo, paddleMat);
  paddle.rotation.z = Math.PI / 6;
  paddle.position.set(0.15, 0.2, 0);
  kayakGroup.add(paddle);

  kayakGroup.position.set(-0.1, -0.3, 2.5);
  kayakGroup.rotation.y = Math.PI / 2;
  parent.add(kayakGroup);
  kayak = kayakGroup;
}

// ============ WATER ============
function buildWater() {
  waterGroup = new THREE.Group();
  dioramaGroup.add(waterGroup);

  // Water volume (box with animated top)
  const waterVolGeo = new THREE.BoxGeometry(9.8, 3, 9.8);
  const waterVolMat = new THREE.MeshPhysicalMaterial({
    color: 0x1a8a8a, transparent: true, opacity: 0.35,
    roughness: 0.1, metalness: 0.0, transmission: 0.6,
    side: THREE.BackSide, depthWrite: false
  });
  const waterVol = new THREE.Mesh(waterVolGeo, waterVolMat);
  waterVol.position.set(0, -0.5, 0);
  waterVol.renderOrder = 50;
  waterGroup.add(waterVol);

  // Water surface (animated plane)
  const surfGeo = new THREE.PlaneGeometry(9.8, 9.8, 48, 48);
  const surfMat = new THREE.MeshPhysicalMaterial({
    color: 0x2a9a9a, transparent: true, opacity: 0.5,
    roughness: 0.1, metalness: 0.1,
    side: THREE.DoubleSide, depthWrite: false
  });
  waterSurface = new THREE.Mesh(surfGeo, surfMat);
  waterSurface.rotation.x = -Math.PI / 2;
  waterSurface.position.y = 1.0;
  waterSurface.renderOrder = 60;
  waterGroup.add(waterSurface);

  // Seabed
  const seabedGeo = new THREE.PlaneGeometry(9.8, 9.8, 32, 32);
  const seabedMat = new THREE.MeshStandardMaterial({ color: 0xc4a870, roughness: 0.95 });
  const seabed = new THREE.Mesh(seabedGeo, seabedMat);
  seabed.rotation.x = -Math.PI / 2;
  seabed.position.y = -1.95;
  seabed.receiveShadow = true;
  waterGroup.add(seabed);

  // Caustics on seabed (animated light pattern)
  const causticGeo = new THREE.PlaneGeometry(9.8, 9.8, 1, 1);
  const causticMat = new THREE.MeshBasicMaterial({
    color: 0x44cccc, transparent: true, opacity: 0.15,
    blending: THREE.AdditiveBlending, depthWrite: false
  });
  const caustics = new THREE.Mesh(causticGeo, causticMat);
  caustics.rotation.x = -Math.PI / 2;
  caustics.position.y = -1.9;
  caustics.renderOrder = 55;
  waterGroup.add(caustics);
  waterGroup.userData.caustics = caustics;

  // Shore foam ring
  const foamGeo = new THREE.RingGeometry(2.8, 3.6, 32);
  const foamMat = new THREE.MeshBasicMaterial({
    color: 0xffffff, transparent: true, opacity: 0.4,
    side: THREE.DoubleSide, depthWrite: false
  });
  const foam = new THREE.Mesh(foamGeo, foamMat);
  foam.rotation.x = -Math.PI / 2;
  foam.position.y = 1.02;
  foam.renderOrder = 65;
  waterGroup.add(foam);
  waterGroup.userData.foam = foam;
}

function animateWater(t) {
  if (!waterSurface) return;
  const positions = waterSurface.geometry.attributes.position;
  const windFactor = windStrength;
  const tideOffset = (tideLevel - 0.5) * 1.5;

  waterSurface.position.y = 1.0 + tideOffset;

  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i), z = positions.getZ(i);
    const wave1 = Math.sin(x * 2 + t * 1.5) * 0.04 * windFactor;
    const wave2 = Math.sin(z * 3 + t * 2) * 0.03 * windFactor;
    const wave3 = Math.sin((x + z) * 1.5 + t * 1.2) * 0.02 * windFactor;
    positions.setZ(i, wave1 + wave2 + wave3);
  }
  positions.needsUpdate = true;
  waterSurface.geometry.computeVertexNormals();

  // Foam animation
  if (waterGroup.userData.foam) {
    waterGroup.userData.foam.position.y = 1.02 + tideOffset;
    waterGroup.userData.foam.material.opacity = 0.3 + Math.sin(t * 2) * 0.1;
  }

  // Caustics
  if (waterGroup.userData.caustics) {
    waterGroup.userData.caustics.material.opacity = 0.1 + Math.sin(t * 1.5) * 0.05;
  }
}

// ============ UNDERWATER LIFE ============
function buildUnderwaterLife() {
  // Rays
  for (let i = 0; i < 3; i++) {
    const ray = createRay();
    ray.userData.angle = (i / 3) * Math.PI * 2;
    ray.userData.radius = 2.0 + Math.random() * 1.5;
    ray.userData.speed = 0.3 + Math.random() * 0.2;
    ray.userData.yBase = -0.8 + Math.random() * 0.5;
    ray.userData.phase = Math.random() * Math.PI * 2;
    rayMeshes.push(ray);
    dioramaGroup.add(ray);
  }

  // Fish schools (instanced)
  buildFishSchools();

  // Sea plants
  buildSeaPlants();

  // Underwater rocks
  const rockMat = new THREE.MeshStandardMaterial({ color: 0x4a5a5a, roughness: 0.9 });
  const rockGeo = new THREE.DodecahedronGeometry(0.2, 1);
  for (let i = 0; i < 8; i++) {
    const rock = new THREE.Mesh(rockGeo, rockMat);
    const angle = Math.random() * Math.PI * 2;
    const r = 3 + Math.random() * 1.5;
    rock.position.set(Math.cos(angle) * r, -1.8, Math.sin(angle) * r);
    rock.scale.set(0.5 + Math.random(), 0.3 + Math.random() * 0.5, 0.5 + Math.random());
    rock.rotation.set(Math.random(), Math.random(), Math.random());
    dioramaGroup.add(rock);
  }

  // Bubbles (instanced)
  buildBubbles();
}

function createRay() {
  const rayGroup = new THREE.Group();

  // Body (flattened ellipsoid)
  const bodyGeo = new THREE.SphereGeometry(0.4, 16, 8);
  bodyGeo.scale(1, 0.15, 0.8);
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x5a7a8a, roughness: 0.6 });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  rayGroup.add(body);

  // Fins (wings)
  const finGeo = new THREE.PlaneGeometry(0.8, 0.5);
  const finMat = new THREE.MeshStandardMaterial({ color: 0x4a6a7a, roughness: 0.7, side: THREE.DoubleSide });

  const leftFin = new THREE.Mesh(finGeo, finMat);
  leftFin.position.set(-0.5, 0, 0);
  leftFin.rotation.x = -Math.PI / 2;
  leftFin.rotation.z = 0.2;
  leftFin.userData.isFin = true;
  leftFin.userData.side = -1;
  rayGroup.add(leftFin);

  const rightFin = new THREE.Mesh(finGeo, finMat);
  rightFin.position.set(0.5, 0, 0);
  rightFin.rotation.x = -Math.PI / 2;
  rightFin.rotation.z = -0.2;
  rightFin.userData.isFin = true;
  rightFin.userData.side = 1;
  rayGroup.add(rightFin);

  // Tail
  const tailGeo = new THREE.PlaneGeometry(0.1, 0.6);
  const tail = new THREE.Mesh(tailGeo, finMat);
  tail.position.set(0, 0, -0.5);
  tail.rotation.x = -Math.PI / 2;
  tail.userData.isTail = true;
  rayGroup.add(tail);

  rayGroup.scale.setScalar(0.7);
  return rayGroup;
}

function animateRays(t) {
  rayMeshes.forEach((ray, idx) => {
    const d = ray.userData;
    d.angle += d.speed * 0.01;
    const x = Math.cos(d.angle) * d.radius;
    const z = Math.sin(d.angle) * d.radius;
    const y = d.yBase + Math.sin(t * 0.5 + d.phase) * 0.2;

    ray.position.set(x, y, z);
    ray.rotation.y = -d.angle + Math.PI / 2;

    // Undulating fins
    ray.children.forEach(child => {
      if (child.userData.isFin) {
        const wave = Math.sin(t * 3 + d.phase + child.userData.side * 0.5) * 0.3;
        child.rotation.z = child.userData.side * (0.2 + wave * 0.3);
      }
      if (child.userData.isTail) {
        child.rotation.z = Math.sin(t * 2 + d.phase) * 0.2;
      }
    });
  });
}

function buildFishSchools() {
  const fishGeo = new THREE.ConeGeometry(0.04, 0.12, 6);
  fishGeo.rotateX(Math.PI / 2);
  const fishMat = new THREE.MeshStandardMaterial({ color: 0xffaa44, roughness: 0.4 });
  const fishMat2 = new THREE.MeshStandardMaterial({ color: 0x44aaff, roughness: 0.4 });
  const fishMat3 = new THREE.MeshStandardMaterial({ color: 0xff6688, roughness: 0.4 });

  const schoolConfigs = [
    { count: 15, mat: fishMat, radius: 3.5, y: -0.5, speed: 0.4 },
    { count: 12, mat: fishMat2, radius: 2.5, y: -1.0, speed: 0.5 },
    { count: 10, mat: fishMat3, radius: 4.0, y: -0.3, speed: 0.35 }
  ];

  schoolConfigs.forEach(config => {
    const instanced = new THREE.InstancedMesh(fishGeo, config.mat, config.count);
    instanced.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    const school = { mesh: instanced, config, offsets: [] };

    for (let i = 0; i < config.count; i++) {
      school.offsets.push({
        angle: Math.random() * Math.PI * 2,
        radius: config.radius + (Math.random() - 0.5) * 1.0,
        y: config.y + (Math.random() - 0.5) * 0.5,
        speed: config.speed + (Math.random() - 0.5) * 0.1,
        phase: Math.random() * Math.PI * 2
      });
    }

    fishSchools.push(school);
    dioramaGroup.add(instanced);
  });
}

const _dummy = new THREE.Object3D();
function animateFish(t) {
  fishSchools.forEach(school => {
    const { mesh, config, offsets } = school;
    for (let i = 0; i < offsets.length; i++) {
      const o = offsets[i];
      const angle = o.angle + t * o.speed;
      const x = Math.cos(angle) * o.radius;
      const z = Math.sin(angle) * o.radius;
      const y = o.y + Math.sin(t * 2 + o.phase) * 0.1;

      _dummy.position.set(x, y, z);
      _dummy.rotation.y = -angle + Math.PI / 2;
      _dummy.rotation.z = Math.sin(t * 5 + o.phase) * 0.1;
      _dummy.updateMatrix();
      mesh.setMatrixAt(i, _dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  });
}

function buildSeaPlants() {
  const plantGeo = new THREE.PlaneGeometry(0.15, 0.8);
  const plantMat = new THREE.MeshStandardMaterial({
    color: 0x2a7a4a, roughness: 0.8, side: THREE.DoubleSide, transparent: true, opacity: 0.8
  });

  for (let i = 0; i < 20; i++) {
    const angle = Math.random() * Math.PI * 2;
    const r = 2.5 + Math.random() * 2;
    const plant = new THREE.Group();

    for (let j = 0; j < 3; j++) {
      const blade = new THREE.Mesh(plantGeo, plantMat);
      blade.position.set(j * 0.05 - 0.05, 0.4, j * 0.03);
      blade.rotation.y = j * 0.5;
      plant.add(blade);
    }

    plant.position.set(Math.cos(angle) * r, -1.9, Math.sin(angle) * r);
    plant.userData.swayOffset = Math.random() * Math.PI * 2;
    plant.userData.isSeaPlant = true;
    dioramaGroup.add(plant);
    seaPlants.push(plant);
  }
}

function animatePlants(t) {
  seaPlants.forEach(p => {
    if (p.userData.isSeaPlant) {
      p.rotation.x = Math.sin(t * 1.5 + p.userData.swayOffset) * 0.1 * windStrength;
      p.rotation.z = Math.sin(t * 1.2 + p.userData.swayOffset + 1) * 0.08 * windStrength;
    } else {
      // Trees
      p.rotation.z = Math.sin(t * 1.0 + p.userData.swayOffset) * 0.03 * windStrength;
      p.rotation.x = Math.sin(t * 0.8 + p.userData.swayOffset + 0.5) * 0.02 * windStrength;
    }
  });
}

function buildBubbles() {
  const bubbleGeo = new THREE.SphereGeometry(0.03, 8, 6);
  const bubbleMat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, transparent: true, opacity: 0.4,
    roughness: 0.0, metalness: 0.1, depthWrite: false
  });

  for (let i = 0; i < 15; i++) {
    const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
    bubble.userData = {
      x: (Math.random() - 0.5) * 6,
      z: (Math.random() - 0.5) * 6,
      speed: 0.3 + Math.random() * 0.5,
      phase: Math.random() * Math.PI * 2,
      startY: -1.5 + Math.random() * 0.5
    };
    bubbles.push(bubble);
    dioramaGroup.add(bubble);
  }
}

function animateBubbles(t) {
  const tideOffset = (tideLevel - 0.5) * 1.5;
  bubbles.forEach(b => {
    const d = b.userData;
    const progress = ((t * d.speed + d.phase) % 3) / 3;
    b.position.y = d.startY + progress * (2.5 + tideOffset);
    b.position.x = d.x + Math.sin(t * 2 + d.phase) * 0.1;
    b.position.z = d.z + Math.cos(t * 1.5 + d.phase) * 0.1;
    b.material.opacity = 0.4 * (1 - progress);
    b.visible = b.position.y < 1.0 + tideOffset;
  });
}

// ============ DETAILS ============
function buildDetails() {
  const woodMat = new THREE.MeshStandardMaterial({ color: 0x7a5b3a, roughness: 0.9 });

  // Bench
  const benchGroup = new THREE.Group();
  const seatGeo = new THREE.BoxGeometry(0.6, 0.04, 0.25);
  const seat = new THREE.Mesh(seatGeo, woodMat);
  seat.position.y = 0.2;
  benchGroup.add(seat);
  const legGeo = new THREE.BoxGeometry(0.04, 0.2, 0.2);
  [-0.25, 0.25].forEach(x => {
    const leg = new THREE.Mesh(legGeo, woodMat);
    leg.position.set(x, 0.1, 0);
    benchGroup.add(leg);
  });
  benchGroup.position.set(-0.5, 1.5, 1.5);
  benchGroup.rotation.y = 0.5;
  dioramaGroup.add(benchGroup);

  // Crates
  const crateMat = new THREE.MeshStandardMaterial({ color: 0x9a7b4a, roughness: 0.9 });
  const crateGeo = new THREE.BoxGeometry(0.25, 0.25, 0.25);
  [[1.8, 1.5, 1.2], [2.0, 1.5, 1.0], [1.9, 1.75, 1.1]].forEach(p => {
    const crate = new THREE.Mesh(crateGeo, crateMat);
    crate.position.set(...p);
    crate.rotation.y = Math.random() * 0.5;
    crate.castShadow = true;
    dioramaGroup.add(crate);
  });

  // Towels (colored planes)
  const towelGeo = new THREE.PlaneGeometry(0.3, 0.5);
  const towel1 = new THREE.Mesh(towelGeo, new THREE.MeshStandardMaterial({ color: 0xff6666, roughness: 0.9, side: THREE.DoubleSide }));
  towel1.position.set(2.8, 0.25, 2.5);
  towel1.rotation.set(-Math.PI / 4, 0.3, 0);
  dioramaGroup.add(towel1);

  const towel2 = new THREE.Mesh(towelGeo, new THREE.MeshStandardMaterial({ color: 0x6666ff, roughness: 0.9, side: THREE.DoubleSide }));
  towel2.position.set(3.0, 0.25, 2.7);
  towel2.rotation.set(-Math.PI / 4, -0.2, 0);
  dioramaGroup.add(towel2);

  // Potted plants near cabin
  const potGeo = new THREE.CylinderGeometry(0.08, 0.06, 0.12, 8);
  const potMat = new THREE.MeshStandardMaterial({ color: 0xb85a3a, roughness: 0.8 });
  const plantGeo = new THREE.SphereGeometry(0.1, 8, 6);
  const plantMat = new THREE.MeshStandardMaterial({ color: 0x3a8a4a, roughness: 0.8 });

  [[-0.3, 1.5, 1.2], [1.3, 1.5, 1.0], [1.5, 1.5, 1.3]].forEach(p => {
    const pot = new THREE.Mesh(potGeo, potMat);
    pot.position.set(p[0], p[1] + 0.06, p[2]);
    dioramaGroup.add(pot);
    const plant = new THREE.Mesh(plantGeo, plantMat);
    plant.position.set(p[0], p[1] + 0.2, p[2]);
    dioramaGroup.add(plant);
  });

  // Ripples pool (for ray jump)
  const rippleGeo = new THREE.RingGeometry(0.1, 0.15, 32);
  const rippleMat = new THREE.MeshBasicMaterial({
    color: 0xffffff, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false
  });
  for (let i = 0; i < 5; i++) {
    const ripple = new THREE.Mesh(rippleGeo, rippleMat.clone());
    ripple.rotation.x = -Math.PI / 2;
    ripple.visible = false;
    ripple.userData = { active: false, time: 0 };
    ripples.push(ripple);
    dioramaGroup.add(ripple);
  }
}

// ============ RAY JUMP ============
let rayJumping = false, rayJumpTime = 0, rayJumpTarget = null;
let droplets = [];

function triggerRayJump() {
  if (rayJumping) return;
  rayJumping = true;
  rayJumpTime = 0;
  rayJumpTarget = rayMeshes[0];
  rayJumpTarget.userData.jumpStart = rayJumpTarget.position.clone();
}

function animateRayJump(dt) {
  if (!rayJumping) return;
  rayJumpTime += dt;
  const duration = 2.5;
  const progress = rayJumpTime / duration;
  const tideOffset = (tideLevel - 0.5) * 1.5;
  const waterY = 1.0 + tideOffset;

  if (progress < 0.5) {
    // Going up
    const t = progress * 2;
    const start = rayJumpTarget.userData.jumpStart;
    rayJumpTarget.position.y = start.y + (waterY - start.y) * t + Math.sin(t * Math.PI) * 2.5;
    rayJumpTarget.position.x = start.x + Math.sin(t * Math.PI) * 0.5;
    rayJumpTarget.rotation.x = -t * Math.PI * 2;
  } else if (progress < 0.7) {
    // Splash
    const t = (progress - 0.5) / 0.2;
    rayJumpTarget.position.y = waterY - t * 1.5;
    rayJumpTarget.rotation.x = -Math.PI * 2 - t * Math.PI;

    // Create ripples
    if (t < 0.1) {
      ripples.forEach((r, i) => {
        r.visible = true;
        r.userData.active = true;
        r.userData.time = -i * 0.15;
        r.position.set(rayJumpTarget.position.x, waterY + 0.05, rayJumpTarget.position.z);
        r.scale.setScalar(0.1);
        r.material.opacity = 0.6;
      });

      // Droplets
      for (let i = 0; i < 12; i++) {
        const drop = new THREE.Mesh(
          new THREE.SphereGeometry(0.02, 6, 4),
          new THREE.MeshBasicMaterial({ color: 0x88ddff, transparent: true, opacity: 0.7 })
        );
        drop.position.copy(rayJumpTarget.position);
        drop.position.y = waterY;
        drop.userData = {
          vx: (Math.random() - 0.5) * 2,
          vy: 2 + Math.random() * 3,
          vz: (Math.random() - 0.5) * 2,
          life: 1.0
        };
        droplets.push(drop);
        dioramaGroup.add(drop);
      }
    }
  } else if (progress < 1.0) {
    // Return to water
    const t = (progress - 0.7) / 0.3;
    const start = rayJumpTarget.userData.jumpStart;
    rayJumpTarget.position.y = (waterY - 1.5) + (start.y - (waterY - 1.5)) * t;
    rayJumpTarget.rotation.x = -Math.PI * 3 * (1 - t);
  } else {
    rayJumping = false;
    rayJumpTarget.rotation.x = 0;
  }

  // Animate ripples
  ripples.forEach(r => {
    if (!r.userData.active) return;
    r.userData.time += dt;
    if (r.userData.time > 0) {
      const rp = r.userData.time / 2;
      r.scale.setScalar(0.1 + rp * 3);
      r.material.opacity = Math.max(0, 0.6 * (1 - rp));
      if (rp >= 1) { r.visible = false; r.userData.active = false; }
    }
  });

  // Animate droplets
  for (let i = droplets.length - 1; i >= 0; i--) {
    const d = droplets[i];
    d.userData.vy -= 9.8 * dt;
    d.position.x += d.userData.vx * dt;
    d.position.y += d.userData.vy * dt;
    d.position.z += d.userData.vz * dt;
    d.userData.life -= dt;
    d.material.opacity = d.userData.life * 0.7;
    if (d.userData.life <= 0) {
      dioramaGroup.remove(d);
      droplets.splice(i, 1);
    }
  }
}

// ============ KAYAK ============
let kayakAnimState = 'docked'; // docked, launching, sailing, returning
let kayakSailTime = 0;

function toggleKayak() {
  if (kayakAnimState === 'docked') {
    kayakAnimState = 'launching';
    kayakSailTime = 0;
    document.getElementById('btn-kayak').textContent = 'Return Kayak';
    document.getElementById('btn-kayak').classList.add('active');
  } else if (kayakAnimState === 'sailing') {
    kayakAnimState = 'returning';
    document.getElementById('btn-kayak').textContent = 'Launch Kayak';
    document.getElementById('btn-kayak').classList.remove('active');
  }
}

function animateKayak(dt, t) {
  const tideOffset = (tideLevel - 0.5) * 1.5;
  const waterY = 1.0 + tideOffset;

  if (kayakAnimState === 'launching') {
    kayakSailTime += dt;
    if (kayakSailTime > 2) {
      kayakAnimState = 'sailing';
      kayakAngle = 0;
    }
    // Move from pier to water
    const p = Math.min(kayakSailTime / 2, 1);
    kayak.position.y = -0.3 + (waterY - (-0.3)) * p;
    kayak.position.z = 2.5 + p * 2;
  }

  if (kayakAnimState === 'sailing') {
    kayakAngle += dt * 0.4;
    const r = 3.5;
    kayak.position.x = Math.cos(kayakAngle) * r + 2.5;
    kayak.position.z = Math.sin(kayakAngle) * r + 2.0;
    kayak.position.y = waterY - 0.05 + Math.sin(t * 2) * 0.03;
    kayak.rotation.y = -kayakAngle + Math.PI / 2;
    kayak.rotation.z = Math.sin(t * 1.5) * 0.05;
  }

  if (kayakAnimState === 'returning') {
    kayakSailTime += dt;
    const p = Math.min(kayakSailTime / 2, 1);
    const targetX = -0.1, targetZ = 2.5;
    kayak.position.x += (targetX - kayak.position.x) * p * 0.05;
    kayak.position.z += (targetZ - kayak.position.z) * p * 0.05;
    kayak.position.y += ((-0.3) - kayak.position.y) * p * 0.03;
    kayak.rotation.y += (Math.PI / 2 - kayak.rotation.y) * p * 0.03;

    if (p >= 1 && Math.abs(kayak.position.x - targetX) < 0.1) {
      kayakAnimState = 'docked';
      kayak.position.set(-0.1, -0.3, 2.5);
      kayak.rotation.set(0, Math.PI / 2, 0);
    }
  }
}

// ============ CAMERA ============
function setCamera(preset) {
  document.querySelectorAll('[data-cam]').forEach(b => b.classList.remove('active'));
  document.querySelector(`[data-cam="${preset}"]`).classList.add('active');

  if (preset === 'orbit') {
    controls.enabled = true;
    cameraTransition = null;
    return;
  }

  controls.enabled = false;
  const target = CAM_PRESETS[preset];
  cameraTransition = {
    startPos: camera.position.clone(),
    endPos: target.pos.clone(),
    startTarget: controls.target.clone(),
    endTarget: target.target.clone(),
    progress: 0
  };
}

function updateCamera(dt) {
  if (cameraTransition) {
    cameraTransition.progress += dt * 1.5;
    if (cameraTransition.progress >= 1) {
      cameraTransition.progress = 1;
      camera.position.copy(cameraTransition.endPos);
      controls.target.copy(cameraTransition.endTarget);
      cameraTransition = null;
      controls.enabled = true;
    } else {
      const t = smoothstep(cameraTransition.progress);
      camera.position.lerpVectors(cameraTransition.startPos, cameraTransition.endPos, t);
      controls.target.lerpVectors(cameraTransition.startTarget, cameraTransition.endTarget, t);
    }
  }
  controls.update();
}

function smoothstep(t) {
  return t * t * (3 - 2 * t);
}

// ============ AUDIO ============
function initAudio() {
  if (audioStarted) return;
  audioStarted = true;
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  masterGain = audioCtx.createGain();
  masterGain.gain.value = 0.6;
  masterGain.connect(audioCtx.destination);

  musicGain = audioCtx.createGain();
  musicGain.gain.value = 0;
  musicGain.connect(masterGain);

  sfxGain = audioCtx.createGain();
  sfxGain.gain.value = 0.3;
  sfxGain.connect(masterGain);

  startAmbientMusic();
  startWaterSound();
  startWindSound();
}

function startAmbientMusic() {
  const notes = [261.6, 293.7, 329.6, 392.0, 440.0, 523.3]; // C major pentatonic-ish
  const baseFreqs = [130.8, 164.8, 196.0, 220.0, 261.6];

  // Pad layer
  baseFreqs.forEach((freq, i) => {
    const osc = audioCtx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = freq * 0.5;
    const gain = audioCtx.createGain();
    gain.gain.value = 0.04;
    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 400;
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(musicGain);
    osc.start();

    // Slow modulation
    const lfo = audioCtx.createOscillator();
    lfo.frequency.value = 0.1 + i * 0.03;
    const lfoGain = audioCtx.createGain();
    lfoGain.gain.value = 0.02;
    lfo.connect(lfoGain);
    lfoGain.connect(gain.gain);
    lfo.start();
  });

  // Melody arpeggios
  function playNote() {
    if (!musicPlaying) { setTimeout(playNote, 2000); return; }
    const freq = notes[Math.floor(Math.random() * notes.length)];
    const osc = audioCtx.createOscillator();
    osc.type = 'triangle';
    osc.frequency.value = freq;
    const gain = audioCtx.createGain();
    gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 2);
    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 1200;
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(musicGain);
    osc.start();
    osc.stop(audioCtx.currentTime + 2);
    setTimeout(playNote, 1500 + Math.random() * 2000);
  }
  playNote();
}

function startWaterSound() {
  // Filtered noise for water
  const bufferSize = audioCtx.sampleRate * 2;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = (Math.random() * 2 - 1) * 0.3;
  }
  const source = audioCtx.createBufferSource();
  source.buffer = buffer;
  source.loop = true;

  const filter = audioCtx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.value = 600;
  filter.Q.value = 1;

  const gain = audioCtx.createGain();
  gain.gain.value = 0.05;

  // Modulate with LFO
  const lfo = audioCtx.createOscillator();
  lfo.frequency.value = 0.3;
  const lfoGain = audioCtx.createGain();
  lfoGain.gain.value = 200;
  lfo.connect(lfoGain);
  lfoGain.connect(filter.frequency);
  lfo.start();

  source.connect(filter);
  filter.connect(gain);
  gain.connect(sfxGain);
  source.start();
}

function startWindSound() {
  const bufferSize = audioCtx.sampleRate * 3;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = (Math.random() * 2 - 1) * 0.2;
  }
  const source = audioCtx.createBufferSource();
  source.buffer = buffer;
  source.loop = true;

  const filter = audioCtx.createBiquadFilter();
  filter.type = 'bandpass';
  filter.frequency.value = 300;
  filter.Q.value = 0.5;

  const gain = audioCtx.createGain();
  gain.gain.value = 0.03;

  const lfo = audioCtx.createOscillator();
  lfo.frequency.value = 0.15;
  const lfoGain = audioCtx.createGain();
  lfoGain.gain.value = 0.02;
  lfo.connect(lfoGain);
  lfoGain.connect(gain.gain);
  lfo.start();

  source.connect(filter);
  filter.connect(gain);
  gain.connect(sfxGain);
  source.start();
}

function toggleMusic() {
  if (!audioStarted) initAudio();
  musicPlaying = !musicPlaying;
  if (musicGain) {
    musicGain.gain.linearRampToValueAtTime(musicPlaying ? 0.5 : 0, audioCtx.currentTime + 0.5);
  }
  document.getElementById('btn-music').classList.toggle('active', musicPlaying);
}

// ============ UI ============
function setupUI() {
  // Camera buttons
  document.querySelectorAll('[data-cam]').forEach(btn => {
    btn.addEventListener('click', () => setCamera(btn.dataset.cam));
  });

  // Time buttons
  document.querySelectorAll('[data-time]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-time]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      targetTime = btn.dataset.time;
    });
  });

  // Quality
  document.querySelectorAll('[data-quality]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-quality]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      quality = btn.dataset.quality;
      applyQuality();
    });
  });

  // Sliders
  document.getElementById('slider-tide').addEventListener('input', e => {
    tideLevel = e.target.value / 100;
    document.getElementById('val-tide').textContent = e.target.value + '%';
  });
  document.getElementById('slider-wind').addEventListener('input', e => {
    windStrength = e.target.value / 100;
    document.getElementById('val-wind').textContent = e.target.value + '%';
  });
  document.getElementById('slider-volume').addEventListener('input', e => {
    if (masterGain) masterGain.gain.value = e.target.value / 100;
  });

  // Buttons
  document.getElementById('btn-kayak').addEventListener('click', () => {
    if (!audioStarted) initAudio();
    toggleKayak();
  });
  document.getElementById('btn-ray').addEventListener('click', () => {
    if (!audioStarted) initAudio();
    triggerRayJump();
  });
  document.getElementById('btn-pause').addEventListener('click', () => {
    paused = !paused;
    document.getElementById('btn-pause').classList.toggle('active', paused);
    document.getElementById('btn-pause').textContent = paused ? 'Resume' : 'Pause';
  });
  document.getElementById('btn-reset').addEventListener('click', resetWorld);
  document.getElementById('btn-music').addEventListener('click', toggleMusic);

  // Mobile toggle
  document.getElementById('mobile-toggle').addEventListener('click', () => {
    document.getElementById('controls-panel').classList.toggle('open');
  });

  // Start audio on first interaction
  document.addEventListener('click', () => { if (!audioStarted) initAudio(); }, { once: true });
}

function applyQuality() {
  const settings = {
    low: { pixelRatio: 1, shadows: false, shadowSize: 512 },
    med: { pixelRatio: Math.min(window.devicePixelRatio, 1.5), shadows: true, shadowSize: 1024 },
    high: { pixelRatio: Math.min(window.devicePixelRatio, 2), shadows: true, shadowSize: 2048 }
  };
  const s = settings[quality];
  renderer.setPixelRatio(s.pixelRatio);
  renderer.shadowMap.enabled = s.shadows;
  if (sunLight) {
    sunLight.castShadow = s.shadows;
    sunLight.shadow.mapSize.set(s.shadowSize, s.shadowSize);
  }
}

function resetWorld() {
  tideLevel = 0.5; windStrength = 0.3;
  targetTime = 'day'; paused = false;
  kayakAnimState = 'docked'; kayakAngle = 0;
  kayak.position.set(-0.1, -0.3, 2.5);
  kayak.rotation.set(0, Math.PI / 2, 0);
  rayJumping = false;

  document.getElementById('slider-tide').value = 50;
  document.getElementById('val-tide').textContent = '50%';
  document.getElementById('slider-wind').value = 30;
  document.getElementById('val-wind').textContent = '30%';
  document.getElementById('btn-pause').textContent = 'Pause';
  document.getElementById('btn-pause').classList.remove('active');
  document.getElementById('btn-kayak').textContent = 'Launch Kayak';
  document.getElementById('btn-kayak').classList.remove('active');

  document.querySelectorAll('[data-time]').forEach(b => b.classList.remove('active'));
  document.querySelector('[data-time="day"]').classList.add('active');

  setCamera('iso');
}

// ============ RESIZE ============
function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

// ============ ANIMATE ============
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);

  if (!paused) {
    animTime += dt;
    updateLighting(dt);
    animateWater(animTime);
    animateRays(animTime);
    animateFish(animTime);
    animatePlants(animTime);
    animateBubbles(animTime);
    animateKayak(dt, animTime);
    animateRayJump(dt);
  }

  updateCamera(dt);
  renderer.render(scene, camera);
}

// ============ START ============
init();
</script>
</body>
</html>
```

This is a complete, self-contained `index.html` file that creates **Tidehaven** — a fully interactive 3D coastal island diorama. Here's what's included:

**Visual Features:**
- Procedural island with sandy shore, rocks, grass, and layered trees
- A-frame cabin with copper roof, glowing windows, wooden deck, and door
- Wooden pier with railings, ladder, lanterns, and a moored kayak
- Cutaway aquarium-style diorama with glass front/side panels and metal frame
- Animated water surface with waves, shoreline foam, and caustic light effects
- Underwater sandy seabed, rocks, and swaying sea plants

**Underwater Life:**
- 3 undulating rays swimming in circular paths with animated fins/tails
- 3 schools of instanced fish (15+12+10) in different colors
- Rising bubbles with fade-out
- Ray jump animation with droplets and expanding ripples

**Interactions:**
- **Camera presets** (Isometric, Cabin, Underwater, Free Orbit) with smooth transitions
- **Time of Day** (Day/Sunset/Night) with smooth lighting interpolation
- **Launch Kayak** — sends it on a circuit around the lagoon
- **Ray Leap** — triggers a dramatic jump with splash effects
- **Tide slider** — adjusts water level, floating objects follow
- **Wind slider** — affects wave amplitude and plant/tree sway
- **Quality settings** (Low/Med/High) adjusting pixel ratio and shadows
- **Pause/Resume** and **Reset**

**Audio:**
- Procedural ambient music (sine pads + triangle wave arpeggios)
- Filtered noise water and wind sounds
- Music toggle and volume slider
- Audio starts on first user interaction

**UI:**
- Translucent glassmorphism panels with backdrop blur
- Collapsible on mobile via hamburger menu
- Active button states, clean typography, English labels