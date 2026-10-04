

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐹 Low-Poly Hamster Playground</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; background: #1a1a2e; font-family: 'Segoe UI', sans-serif; }
canvas { display: block; }
#info {
  position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
  color: #fff; text-align: center; pointer-events: none;
  text-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
#info h1 { font-size: 22px; margin-bottom: 4px; letter-spacing: 1px; }
#info p  { font-size: 13px; opacity: 0.7; }
#tooltip {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  background: rgba(0,0,0,0.6); color: #ffd; padding: 8px 18px;
  border-radius: 20px; font-size: 13px; pointer-events: none;
  transition: opacity 0.3s; opacity: 0;
}
#stats {
  position: absolute; top: 16px; right: 16px;
  color: #ffd; font-size: 12px; text-align: right;
  background: rgba(0,0,0,0.4); padding: 10px 14px; border-radius: 10px;
  line-height: 1.6;
}
</style>
</head>
<body>

<div id="info">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Click &amp; drag to rotate · Scroll to zoom · Watch them play!</p>
</div>
<div id="tooltip"></div>
<div id="stats"></div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ─── SCENE SETUP ────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87CEEB);
scene.fog = new THREE.Fog(0x87CEEB, 25, 50);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(0, 10, 14);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 2, 0);
controls.maxPolarAngle = Math.PI / 2.05;
controls.minDistance = 6;
controls.maxDistance = 25;

// ─── LIGHTING ───────────────────────────────────────────
const ambientLight = new THREE.AmbientLight(0xffeedd, 0.6);
scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(0xfff4e0, 1.4);
sunLight.position.set(8, 15, 6);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(1024, 1024);
sunLight.shadow.camera.near = 1;
sunLight.shadow.camera.far = 30;
sunLight.shadow.camera.left = -10;
sunLight.shadow.camera.right = 10;
sunLight.shadow.camera.top = 10;
sunLight.shadow.camera.bottom = -10;
sunLight.shadow.bias = -0.001;
scene.add(sunLight);

const fillLight = new THREE.DirectionalLight(0xc8d8ff, 0.4);
fillLight.position.set(-6, 8, -4);
scene.add(fillLight);

const rimLight = new THREE.PointLight(0xffaa66, 0.5, 20);
rimLight.position.set(-5, 6, 5);
scene.add(rimLight);

// ─── MATERIALS ──────────────────────────────────────────
const mat = {
  cageBar:    new THREE.MeshStandardMaterial({ color: 0x8899aa, roughness: 0.4, metalness: 0.6 }),
  floor:      new THREE.MeshStandardMaterial({ color: 0xf5deb3, roughness: 0.9 }),
  bedding:    new THREE.MeshStandardMaterial({ color: 0xffe4b5, roughness: 1.0 }),
  wheel:      new THREE.MeshStandardMaterial({ color: 0xff6b35, roughness: 0.5 }),
  wheelInner: new THREE.MeshStandardMaterial({ color: 0xffa070, roughness: 0.5 }),
  tunnel:     new THREE.MeshStandardMaterial({ color: 0x4ecdc4, roughness: 0.7 }),
  tunnelDark: new THREE.MeshStandardMaterial({ color: 0x2a9d8f, roughness: 0.8 }),
  bowl:       new THREE.MeshStandardMaterial({ color: 0xe07040, roughness: 0.6 }),
  food:       new THREE.MeshStandardMaterial({ color: 0x8B4513, roughness: 0.9 }),
  seed:       new THREE.MeshStandardMaterial({ color: 0xdaa520, roughness: 0.8 }),
  grass:      new THREE.MeshStandardMaterial({ color: 0x6abf69, roughness: 0.9 }),
  water:      new THREE.MeshStandardMaterial({ color: 0x4fc3f7, roughness: 0.2, metalness: 0.1, transparent: true, opacity: 0.6 }),
  platform:   new THREE.MeshStandardMaterial({ color: 0xc9a96e, roughness: 0.8 }),
  rope:       new THREE.MeshStandardMaterial({ color: 0xb8860b, roughness: 0.9 }),
};

// ─── HAMSTER COLORS ─────────────────────────────────────
const hamsterPalettes = [
  { body: 0xf4c778, belly: 0xfff8e7, ear: 0xffb6c1, stripe: 0xd4a056, cheek: 0xffaaaa },
  { body: 0xc8a882, belly: 0xfff0dd, ear: 0xffc0cb, stripe: 0xa08060, cheek: 0xff9999 },
  { body: 0xe8dcc8, belly: 0xfffef5, ear: 0xffb0b0, stripe: 0xc0b090, cheek: 0xffb0b0 },
  { body: 0xb89060, belly: 0xffeedd, ear: 0xffa0a0, stripe: 0x907040, cheek: 0xff8888 },
  { body: 0xffd090, belly: 0xfffff0, ear: 0xffc0c0, stripe: 0xe0b070, cheek: 0xffc0c0 },
];

// ─── CAGE ───────────────────────────────────────────────
const CAGE_W = 10, CAGE_D = 7, CAGE_H = 5;

function buildCage() {
  const cage = new THREE.Group();

  // Floor tray
  const floorGeo = new THREE.BoxGeometry(CAGE_W + 0.4, 0.3, CAGE_D + 0.4);
  const floor = new THREE.Mesh(floorGeo, mat.floor);
  floor.position.y = -0.15;
  floor.receiveShadow = true;
  cage.add(floor);

  // Bedding layer
  const bedGeo = new THREE.BoxGeometry(CAGE_W, 0.15, CAGE_D);
  const bed = new THREE.Mesh(bedGeo, mat.bedding);
  bed.position.y = 0.075;
  bed.receiveShadow = true;
  cage.add(bed);

  // Bars function
  function addBar(x, y, z, w, h, d) {
    const geo = new THREE.BoxGeometry(w, h, d);
    const bar = new THREE.Mesh(geo, mat.cageBar);
    bar.position.set(x, y, z);
    bar.castShadow = true;
    cage.add(bar);
  }

  const barThick = 0.08;
  const barGapX = 0.9;
  const barGapZ = 0.9;

  // Vertical bars on X sides
  for (let z = -CAGE_D / 2; z <= CAGE_D / 2 + 0.01; z += barGapZ) {
    addBar(-CAGE_W / 2, CAGE_H / 2, z, barThick, CAGE_H, barThick);
    addBar( CAGE_W / 2, CAGE_H / 2, z, barThick, CAGE_H, barThick);
  }

  // Vertical bars on Z sides
  for (let x = -CAGE_W / 2 + barGapX; x < CAGE_W / 2; x += barGapX) {
    addBar(x, CAGE_H / 2, -CAGE_D / 2, barThick, CAGE_H, barThick);
    addBar(x, CAGE_H / 2,  CAGE_D / 2, barThick, CAGE_H, barThick);
  }

  // Top frame
  addBar(0, CAGE_H, -CAGE_D / 2, CAGE_W, barThick, barThick);
  addBar(0, CAGE_H,  CAGE_D / 2, CAGE_W, barThick, barThick);
  addBar(-CAGE_W / 2, CAGE_H, 0, barThick, barThick, CAGE_D);
  addBar( CAGE_W / 2, CAGE_H, 0, barThick, barThick, CAGE_D);

  // Horizontal support rails
  for (let y = 1.5; y < CAGE_H; y += 2) {
    addBar(0, y, -CAGE_D / 2, CAGE_W, barThick * 0.6, barThick * 0.6);
    addBar(0, y,  CAGE_D / 2, CAGE_W, barThick * 0.6, barThick * 0.6);
    addBar(-CAGE_W / 2, y, 0, barThick * 0.6, barThick * 0.6, CAGE_D);
    addBar( CAGE_W / 2, y, 0, barThick * 0.6, barThick * 0.6, CAGE_D);
  }

  scene.add(cage);
}
buildCage();

// ─── WHEEL ──────────────────────────────────────────────
let wheelGroup, wheelBody;
function buildWheel() {
  wheelGroup = new THREE.Group();

  // Outer ring
  const ringGeo = new THREE.TorusGeometry(1.2, 0.12, 8, 24);
  wheelBody = new THREE.Mesh(ringGeo, mat.wheel);
  wheelBody.castShadow = true;
  wheelGroup.add(wheelBody);

  // Inner ring (smaller, for grip)
  const innerGeo = new THREE.TorusGeometry(0.8, 0.08, 6, 20);
  const inner = new THREE.Mesh(innerGeo, mat.wheelInner);
  wheelGroup.add(inner);

  // Spokes
  for (let i = 0; i < 8; i++) {
    const angle = (i / 8) * Math.PI * 2;
    const spokeGeo = new THREE.CylinderGeometry(0.04, 0.04, 1.2, 5);
    const spoke = new THREE.Mesh(spokeGeo, mat.wheel);
    spoke.rotation.z = Math.PI / 2;
    spoke.rotation.y = angle;
    spoke.position.x = 0;
    spoke.castShadow = true;
    wheelGroup.add(spoke);
  }

  // Hub
  const hubGeo = new THREE.CylinderGeometry(0.15, 0.15, 0.5, 8);
  const hub = new THREE.Mesh(hubGeo, mat.wheel);
  hub.rotation.x = Math.PI / 2;
  hub.castShadow = true;
  wheelGroup.add(hub);

  // Axle stand
  const standGeo = new THREE.CylinderGeometry(0.06, 0.06, 2.5, 6);
  const standL = new THREE.Mesh(standGeo, mat.cageBar);
  standL.position.set(-0.8, -1.25, 0);
  wheelGroup.add(standL);
  const standR = new THREE.Mesh(standGeo, mat.cageBar);
  standR.position.set(0.8, -1.25, 0);
  wheelGroup.add(standR);

  // Base plate
  const baseGeo = new THREE.BoxGeometry(2, 0.1, 0.8);
  const base = new THREE.Mesh(baseGeo, mat.platform);
  base.position.y = -2.5;
  base.receiveShadow = true;
  wheelGroup.add(base);

  wheelGroup.position.set(-3, 2.5, -1.5);
  wheelGroup.rotation.y = 0.3;
  scene.add(wheelGroup);
}
buildWheel();

// ─── TUNNEL ─────────────────────────────────────────────
let tunnelGroup;
function buildTunnel() {
  tunnelGroup = new THREE.Group();

  // Main tube
  const tubeGeo = new THREE.CylinderGeometry(0.6, 0.6, 3, 12, 1, true);
  const tube = new THREE.Mesh(tubeGeo, mat.tunnel);
  tube.rotation.z = Math.PI / 2;
  tube.castShadow = true;
  tunnelGroup.add(tube);

  // End rims
  const rimGeo = new THREE.TorusGeometry(0.6, 0.06, 6, 12);
  const rim1 = new THREE.Mesh(rimGeo, mat.tunnelDark);
  rim1.position.x = 1.5;
  tunnelGroup.add(rim1);
  const rim2 = new THREE.Mesh(rimGeo, mat.tunnelDark);
  rim2.position.x = -1.5;
  tunnelGroup.add(rim2);

  // Dark interior hint
  const darkGeo = new THREE.CylinderGeometry(0.55, 0.55, 2.9, 10, 1, true);
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x1a3a3a, roughness: 1 });
  const dark = new THREE.Mesh(darkGeo, darkMat);
  dark.rotation.z = Math.PI / 2;
  tunnelGroup.add(dark);

  tunnelGroup.position.set(2, 0.6, 1.5);
  tunnelGroup.rotation.y = -0.5;
  scene.add(tunnelGroup);
}
buildTunnel();

// ─── FOOD BOWL ──────────────────────────────────────────
let foodBowlGroup;
function buildFoodBowl() {
  foodBowlGroup = new THREE.Group();

  // Bowl (half sphere)
  const bowlGeo = new THREE.SphereGeometry(0.5, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2);
  const bowl = new THREE.Mesh(bowlGeo, mat.bowl);
  bowl.position.y = 0.05;
  bowl.castShadow = true;
  foodBowlGroup.add(bowl);

  // Rim
  const rimGeo = new THREE.TorusGeometry(0.5, 0.04, 6, 16);
  const rim = new THREE.Mesh(rimGeo, mat.bowl);
  rim.rotation.x = Math.PI / 2;
  rim.position.y = 0.08;
  foodBowlGroup.add(rim);

  // Seeds/food inside
  for (let i = 0; i < 12; i++) {
    const angle = Math.random() * Math.PI * 2;
    const r = Math.random() * 0.3;
    const seedGeo = new THREE.SphereGeometry(0.04 + Math.random() * 0.03, 4, 4);
    const seed = new THREE.Mesh(seedGeo, Math.random() > 0.5 ? mat.seed : mat.food);
    seed.position.set(Math.cos(angle) * r, 0.1 + Math.random() * 0.05, Math.sin(angle) * r);
    seed.castShadow = true;
    foodBowlGroup.add(seed);
  }

  foodBowlGroup.position.set(3, 0.1, -2);
  scene.add(foodBowlGroup);
}
buildFoodBowl();

// ─── WATER BOWL ─────────────────────────────────────────
function buildWaterBowl() {
  const group = new THREE.Group();

  const bowlGeo = new THREE.SphereGeometry(0.35, 10, 6, 0, Math.PI * 2, 0, Math.PI / 2);
  const bowl = new THREE.Mesh(bowlGeo, mat.cageBar);
  bowl.position.y = 0.05;
  bowl.castShadow = true;
  group.add(bowl);

  const waterGeo = new THREE.CircleGeometry(0.3, 10);
  const water = new THREE.Mesh(waterGeo, mat.water);
  water.rotation.x = -Math.PI / 2;
  water.position.y = 0.15;
  group.add(water);

  group.position.set(-2, 0.1, 2);
  scene.add(group);
}
buildWaterBowl();

// ─── PLATFORM / BRIDGE ──────────────────────────────────
function buildPlatform() {
  const group = new THREE.Group();

  // Wooden platform
  const platGeo = new THREE.BoxGeometry(2, 0.1, 1.2);
  const plat = new THREE.Mesh(platGeo, mat.platform);
  plat.position.y = 1.5;
  plat.castShadow = true;
  plat.receiveShadow = true;
  group.add(plat);

  // Support legs
  const legGeo = new THREE.CylinderGeometry(0.06, 0.06, 1.5, 6);
  [[-0.8, 0.75, -0.4], [0.8, 0.75, -0.4], [-0.8, 0.75, 0.4], [0.8, 0.75, 0.4]].forEach(p => {
    const leg = new THREE.Mesh(legGeo, mat.cageBar);
    leg.position.set(...p);
    leg.castShadow = true;
    group.add(leg);
  });

  // Small house on platform
  const houseBase = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.7, 0.7), mat.platform);
  houseBase.position.set(0.3, 1.9, 0);
  houseBase.castShadow = true;
  group.add(houseBase);

  const roofGeo = new THREE.ConeGeometry(0.65, 0.4, 4);
  const roofMat = new THREE.MeshStandardMaterial({ color: 0xd4553a, roughness: 0.8 });
  const roof = new THREE.Mesh(roofGeo, roofMat);
  roof.position.set(0.3, 2.55, 0);
  roof.rotation.y = Math.PI / 4;
  roof.castShadow = true;
  group.add(roof);

  // Door hole
  const doorGeo = new THREE.CircleGeometry(0.2, 8);
  const doorMat = new THREE.MeshStandardMaterial({ color: 0x2a1a0a, roughness: 1 });
  const door = new THREE.Mesh(doorGeo, doorMat);
  door.position.set(0.3, 1.8, 0.351);
  group.add(door);

  group.position.set(0, 0, 0);
  scene.add(group);
}
buildPlatform();

// ─── GRASS PATCHES ──────────────────────────────────────
function buildGrass() {
  for (let i = 0; i < 30; i++) {
    const x = (Math.random() - 0.5) * (CAGE_W - 1);
    const z = (Math.random() - 0.5) * (CAGE_D - 1);
    const bladeGeo = new THREE.ConeGeometry(0.04, 0.15 + Math.random() * 0.1, 3);
    const blade = new THREE.Mesh(bladeGeo, mat.grass);
    blade.position.set(x, 0.18, z);
    blade.rotation.z = (Math.random() - 0.5) * 0.3;
    scene.add(blade);
  }
}
buildGrass();

// ─── SCATTERED SEEDS ON FLOOR ──────────────────────────
function buildScatteredSeeds() {
  for (let i = 0; i < 20; i++) {
    const x = (Math.random() - 0.5) * (CAGE_W - 0.5);
    const z = (Math.random() - 0.5) * (CAGE_D - 0.5);
    const seedGeo = new THREE.SphereGeometry(0.03 + Math.random() * 0.02, 4, 4);
    const seed = new THREE.Mesh(seedGeo, Math.random() > 0.5 ? mat.seed : mat.food);
    seed.position.set(x, 0.12, z);
    seed.scale.y = 0.5;
    scene.add(seed);
  }
}
buildScatteredSeeds();

// ─── HAMSTER BUILDER ────────────────────────────────────
function buildHamster(paletteIndex) {
  const pal = hamsterPalettes[paletteIndex % hamsterPalettes.length];
  const group = new THREE.Group();

  // Body - stretched sphere for low-poly look
  const bodyGeo = new THREE.IcosahedronGeometry(0.45, 1);
  const bodyMat = new THREE.MeshStandardMaterial({ color: pal.body, roughness: 0.8, flatShading: true });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.scale.set(1, 0.85, 1.3);
  body.position.set(0, 0.35, 0);
  body.castShadow = true;
  group.add(body);

  // Belly (lighter patch)
  const bellyGeo = new THREE.IcosahedronGeometry(0.32, 1);
  const bellyMat = new THREE.MeshStandardMaterial({ color: pal.belly, roughness: 0.8, flatShading: true });
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.scale.set(0.9, 0.7, 1.1);
  belly.position.set(0, 0.25, 0.1);
  group.add(belly);

  // Head
  const headGeo = new THREE.IcosahedronGeometry(0.32, 1);
  const headMat = new THREE.MeshStandardMaterial({ color: pal.body, roughness: 0.8, flatShading: true });
  const head = new THREE.Mesh(headGeo, headMat);
  head.scale.set(1.1, 1, 1);
  head.position.set(0, 0.48, 0.42);
  head.castShadow = true;
  group.add(head);

  // Ears
  const earGeo = new THREE.ConeGeometry(0.1, 0.15, 4);
  const earMat = new THREE.MeshStandardMaterial({ color: pal.ear, roughness: 0.7, flatShading: true });

  const earL = new THREE.Mesh(earGeo, earMat);
  earL.position.set(-0.18, 0.65, 0.35);
  earL.rotation.z = 0.3;
  group.add(earL);

  const earR = new THREE.Mesh(earGeo, earMat);
  earR.position.set(0.18, 0.65, 0.35);
  earR.rotation.z = -0.3;
  group.add(earR);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.05, 6, 6);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.3 });

  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(-0.14, 0.52, 0.62);
  group.add(eyeL);

  const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
  eyeR.position.set(0.14, 0.52, 0.62);
  group.add(eyeR);

  // Eye shine
  const shineGeo = new THREE.SphereGeometry(0.02, 4, 4);
  const shineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const shineL = new THREE.Mesh(shineGeo, shineMat);
  shineL.position.set(-0.13, 0.54, 0.66);
  group.add(shineL);
  const shineR = new THREE.Mesh(shineGeo, shineMat);
  shineR.position.set(0.15, 0.54, 0.66);
  group.add(shineR);

  // Nose
  const noseGeo = new THREE.SphereGeometry(0.04, 5, 5);
  const noseMat = new THREE.MeshStandardMaterial({ color: 0xff8888, roughness: 0.5 });
  const nose = new THREE.Mesh(noseGeo, noseMat);
  nose.position.set(0, 0.46, 0.7);
  group.add(nose);

  // Cheeks (chubby!)
  const cheekGeo = new THREE.SphereGeometry(0.12, 6, 6);
  const cheekMat = new THREE.MeshStandardMaterial({ color: pal.cheek, roughness: 0.7, flatShading: true });

  const cheekL = new THREE.Mesh(cheekGeo, cheekMat);
  cheekL.scale.set(1, 0.7, 0.8);
  cheekL.position.set(-0.22, 0.42, 0.55);
  group.add(cheekL);

  const cheekR = new THREE.Mesh(cheekGeo, cheekMat);
  cheekR.scale.set(1, 0.7, 0.8);
  cheekR.position.set(0.22, 0.42, 0.55);
  group.add(cheekR);

  // Whiskers
  const whiskerMat = new THREE.MeshStandardMaterial({ color: 0xdddddd, roughness: 0.5 });
  const whiskerGeo = new THREE.CylinderGeometry(0.005, 0.005, 0.2, 3);
  for (let side of [-1, 1]) {
    for (let i = 0; i < 3; i++) {
      const whisker = new THREE.Mesh(whiskerGeo, whiskerMat);
      whisker.position.set(side * (0.2 + 0.05 * i), 0.44, 0.65 + i * 0.03);
      whisker.rotation.z = Math.PI / 2 + side * (0.1 + i * 0.1);
      group.add(whisker);
    }
  }

  // Back stripe
  const stripeGeo = new THREE.BoxGeometry(0.15, 0.02, 0.5);
  const stripeMat = new THREE.MeshStandardMaterial({ color: pal.stripe, roughness: 0.8, flatShading: true });
  const stripe = new THREE.Mesh(stripeGeo, stripeMat);
  stripe.position.set(0, 0.52, 0.05);
  group.add(stripe);

  // Legs
  const legGeo = new THREE.CylinderGeometry(0.06, 0.05, 0.15, 5);
  const legMat = new THREE.MeshStandardMaterial({ color: pal.body, roughness: 0.8, flatShading: true });

  const legPositions = [
    [-0.2, 0.12, 0.25], [0.2, 0.12, 0.25],
    [-0.2, 0.12, -0.25], [0.2, 0.12, -0.25]
  ];
  legPositions.forEach(p => {
    const leg = new THREE.Mesh(legGeo, legMat);
    leg.position.set(...p);
    leg.castShadow = true;
    group.add(leg);
  });

  // Tiny paws
  const pawGeo = new THREE.SphereGeometry(0.05, 5, 5);
  const pawMat = new THREE.MeshStandardMaterial({ color: pal.ear, roughness: 0.7, flatShading: true });
  legPositions.forEach(p => {
    const paw = new THREE.Mesh(pawGeo, pawMat);
    paw.position.set(p[0], p[1] - 0.07, p[2]);
    group.add(paw);
  });

  // Tail (tiny nub)
  const tailGeo = new THREE.SphereGeometry(0.08, 5, 5);
  const tail = new THREE.Mesh(tailGeo, tailMat || mat.belly);
  tail.position.set(0, 0.3, -0.5);
  tail.scale.set(0.8, 0.7, 0.6);
  group.add(tail);

  return group;
}

// ─── HAMSTER AI ─────────────────────────────────────────
class HamsterAI {
  constructor(mesh, paletteIndex) {
    this.mesh = mesh;
    this.paletteIndex = paletteIndex;
    this.state = 'idle'; // idle, walking, turning, eating, running_wheel, sleeping
    this.stateTimer = Math.random() * 3;
    this.targetPos = new THREE.Vector3();
    this.targetAngle = 0;
    this.speed = 0.8 + Math.random() * 0.6;
    this.walkCycle = Math.random() * Math.PI * 2;
    this.bobPhase = Math.random() * Math.PI * 2;
    this.interactionTarget = null;
    this.energy = 100;
    this.happiness = 80;
    this.name = ['Nugget', 'Mochi', 'Biscuit', 'Peanut', 'Cookie'][paletteIndex % 5];
    this.earWiggle = 0;
    this.tailWag = 0;
    this.eyeBlink = 0;
    this.blinkTimer = Math.random() * 5;

    // Pick random start position
    this.pickNewTarget();
    mesh.position.copy(this.targetPos);
  }

  pickNewTarget() {
    const margin = 0.5;
    this.targetPos.set(
      (Math.random() - 0.5) * (CAGE_W - 2 * margin),
      0,
      (Math.random() - 0.5) * (CAGE_D - 2 * margin)
    );
  }

  update(dt, time) {
    this.stateTimer -= dt;
    this.walkCycle += dt * this.speed * 8;
    this.bobPhase += dt * 4;
    this.earWiggle += dt * 6;
    this.tailWag += dt * 3;
    this.blinkTimer -= dt;

    // Blink
    if (this.blinkTimer <= 0) {
      this.eyeBlink = 0.15;
      this.blinkTimer = 2 + Math.random() * 4;
    }
    if (this.eyeBlink > 0) this.eyeBlink -= dt;

    switch (this.state) {
      case 'idle':
        this.updateIdle(dt, time);
        break;
      case 'walking':
        this.updateWalking(dt, time);
        break;
      case 'turning':
        this.updateTurning(dt, time);
        break;
      case 'eating':
        this.updateEating(dt, time);
        break;
      case 'running_wheel':
        this.updateRunningWheel(dt, time);
        break;
      case 'sleeping':
        this.updateSleeping(dt, time);
        break;
    }

    // Apply bobbing animation
    if (this.state === 'walking' || this.state === 'running_wheel') {
      this.mesh.position.y = Math.abs(Math.sin(this.walkCycle)) * 0.05;
    } else if (this.state === 'sleeping') {
      this.mesh.position.y = Math.sin(time * 1.5) * 0.01;
    }

    // Clamp to cage bounds
    this.mesh.position.x = Math.max(-CAGE_W / 2 + 0.5, Math.min(CAGE_W / 2 - 0.5, this.mesh.position.x));
    this.mesh.position.z = Math.max(-CAGE_D / 2 + 0.5, Math.min(CAGE_D / 2 - 0.5, this.mesh.position.z));
  }

  updateIdle(dt, time) {
    if (this.stateTimer <= 0) {
      const roll = Math.random();
      if (roll < 0.4) {
        this.state = 'walking';
        this.pickNewTarget();
        this.stateTimer = 2 + Math.random() * 3;
      } else if (roll < 0.6) {
        this.state = 'turning';
        this.targetAngle = Math.random() * Math.PI * 2;
        this.stateTimer = 0.5 + Math.random() * 0.5;
      } else if (roll < 0.75 && foodBowlGroup) {
        this.state = 'eating';
        this.interactionTarget = foodBowlGroup;
        this.stateTimer = 2 + Math.random() * 3;
      } else if (roll < 0.85 && wheelGroup) {
        this.state = 'running_wheel';
        this.stateTimer = 3 + Math.random() * 4;
      } else {
        this.state = 'sleeping';
        this.stateTimer = 2 + Math.random() * 3;
      }
    }

    // Gentle breathing
    const breathe = Math.sin(time * 2) * 0.005;
    this.mesh.scale.setScalar(1 + breathe);
  }

  updateWalking(dt, time) {
    const dir = new THREE.Vector3().subVectors(this.targetPos, this.mesh.position);
    const dist = dir.length();

    if (dist < 0.2) {
      this.state = 'idle';
      this.stateTimer = 0.5 + Math.random() * 2;
      return;
    }

    dir.normalize();
    const targetAngle = Math.atan2(dir.x, dir.z);

    // Smooth rotation
    let angleDiff = targetAngle - this.mesh.rotation.y;
    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
    this.mesh.rotation.y += angleDiff * Math.min(1, dt * 5);

    // Move
    this.mesh.position.addScaledVector(dir, this.speed * dt);

    // Leg animation via scale wobble
    const wobble = Math.sin(this.walkCycle) * 0.03;
    this.mesh.children.forEach((child, i) => {
      if (i >= 14 && i <= 17) { // legs
        child.rotation.x = wobble * (i % 2 === 0 ? 1 : -1);
      }
    });
  }

  updateTurning(dt, time) {
    let angleDiff = this.targetAngle - this.mesh.rotation.y;
    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
    this.mesh.rotation.y += angleDiff * Math.min(1, dt * 6);

    if (this.stateTimer <= 0) {
      this.state = Math.random() < 0.5 ? 'walking' : 'idle';
      if (this.state === 'walking') {
        this.pickNewTarget();
        this.stateTimer = 2 + Math.random() * 3;
      } else {
        this.stateTimer = 1 + Math.random() * 2;
      }
    }
  }

  updateEating(dt, time) {
    if (!this.interactionTarget) {
      this.state = 'idle';
      this.stateTimer = 1;
      return;
    }

    const bowlPos = this.interactionTarget.position;
    const dir = new THREE.Vector3().subVectors(bowlPos, this.mesh.position);
    const dist = dir.length();

    if (dist > 0.3) {
      dir.normalize();
      const targetAngle = Math.atan2(dir.x, dir.z);
      let angleDiff = targetAngle - this.mesh.rotation.y;
      while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
      while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
      this.mesh.rotation.y += angleDiff * Math.min(1, dt * 5);
      this.mesh.position.addScaledVector(dir, this.speed * 0.7 * dt);
    } else {
      // Eating animation - little head bobs
      this.mesh.children[3].position.y = 0.48 + Math.sin(time * 8) * 0.02; // head bob
      this.happiness = Math.min(100, this.happiness + dt * 5);
    }

    if (this.stateTimer <= 0) {
      this.state = 'idle';
      this.stateTimer = 1 + Math.random() * 2;
      this.interactionTarget = null;
    }
  }

  updateRunningWheel(dt, time) {
    if (!wheelGroup) {
      this.state = 'idle';
      this.stateTimer = 1;
      return;
    }

    const wheelPos = wheelGroup.position.clone();
    wheelPos.y -= 0.5; // position at wheel level
    const dir = new THREE.Vector3().subVectors(wheelPos, this.mesh.position);
    const dist = dir.length();

    if (dist > 0.5) {
      dir.normalize();
      const targetAngle = Math.atan2(dir.x, dir.z);
      let angleDiff = targetAngle - this.mesh.rotation.y;
      while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
      while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
      this.mesh.rotation.y += angleDiff * Math.min(1, dt * 5);
      this.mesh.position.addScaledVector(dir, this.speed * 1.2 * dt);
    } else {
      // Running in place animation
      this.mesh.position.y = Math.abs(Math.sin(this.walkCycle * 2)) * 0.08;
      this.mesh.rotation.y = wheelGroup.rotation.y + Math.PI;
      this.happiness = Math.min(100, this.happiness + dt * 8);

      // Spin the wheel!
      if (wheelBody) {
        wheelBody.rotation.z += dt * 5;
        wheelGroup.children.forEach(child => {
          if (child !== wheelBody && child.geometry?.type === 'CylinderGeometry') {
            // Rotate spokes with the wheel
          }
        });
      }
    }

    if (this.stateTimer <= 0) {
      this.state = 'idle';
      this.stateTimer = 1 + Math.random() * 3;
    }
  }

  updateSleeping(dt, time) {
    // Tilt down to sleep
    const sleepTilt = Math.sin(Math.min(1, (3 - this.stateTimer) / 1) * Math.PI / 6);
    this.mesh.rotation.x = -sleepTilt;

    if (this.stateTimer <= 0) {
      this.state = 'idle';
      this.stateTimer = 1 + Math.random() * 2;
      this.mesh.rotation.x = 0;
    }
  }
}

// ─── CREATE HAMSTERS ────────────────────────────────────
const hamsters = [];
const hamsterMeshes = [];

for (let i = 0; i < 5; i++) {
  const mesh = buildHamster(i);
  const ai = new HamsterAI(mesh, i);
  hamsters.push(ai);
  hamsterMeshes.push(mesh);
  scene.add(mesh);
}

// ─── PARTICLES (dust/fluff) ────────────────────────────
const particleCount = 60;
const particleGeo = new THREE.BufferGeometry();
const particlePositions = new Float32Array(particleCount * 3);
const particleSpeeds = [];

for (let i = 0; i < particleCount; i++) {
  particlePositions[i * 3] = (Math.random() - 0.5) * CAGE_W;
  particlePositions[i * 3 + 1] = Math.random() * CAGE_H;
  particlePositions[i * 3 + 2] = (Math.random() - 0.5) * CAGE_D;
  particleSpeeds.push({
    x: (Math.random() - 0.5) * 0.1,
    y: (Math.random() - 0.5) * 0.05,
    z: (Math.random() - 0.5) * 0.1,
  });
}
particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

const particleMat = new THREE.PointsMaterial({
  color: 0xffffff,
  size: 0.04,
  transparent: true,
  opacity: 0.3,
  sizeAttenuation: true,
});
const particles = new THREE.Points(particleGeo, particleMat);
scene.add(particles);

// ─── TOOLTIP ────────────────────────────────────────────
const tooltipEl = document.getElementById('tooltip');
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('mousemove', (e) => {
  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);

  let hit = false;
  for (const ai of hamsters) {
    const intersects = raycaster.intersectObject(ai.mesh, true);
    if (intersects.length > 0) {
      const stateEmoji = {
        idle: '😴', walking: '🚶', turning: '🔄',
        eating: '🍽️', running_wheel: '🏃', sleeping: '💤'
      };
      tooltipEl.textContent = `${stateEmoji[ai.state]} ${ai.name} — ${ai.state.replace('_', ' ')}`;
      tooltipEl.style.opacity = '1';
      hit = true;
      break;
    }
  }

  if (!hit) {
    tooltipEl.style.opacity = '0';
  }
});

// ─── STATS PANEL ────────────────────────────────────────
const statsEl = document.getElementById('stats');

// ─── ANIMATION LOOP ────────────────────────────────────
const clock = new THREE.Clock();
let frameCount = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.getElapsedTime();
  frameCount++;

  controls.update();

  // Update hamsters
  for (const ai of hamsters) {
    ai.update(dt, time);
  }

  // Update particles
  const positions = particles.geometry.attributes.position.array;
  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] += particleSpeeds[i].x * dt;
    positions[i * 3 + 1] += particleSpeeds[i].y * dt + Math.sin(time + i) * 0.001;
    positions[i * 3 + 2] += particleSpeeds[i].z * dt;

    // Wrap around
    if (positions[i * 3] > CAGE_W / 2) positions[i * 3] = -CAGE_W / 2;
    if (positions[i * 3] < -CAGE_W / 2) positions[i * 3] = CAGE_W / 2;
    if (positions[i * 3 + 1] > CAGE_H) positions[i * 3 + 1] = 0;
    if (positions[i * 3 + 1] < 0) positions[i * 3 + 1] = CAGE_H;
    if (positions[i * 3 + 2] > CAGE_D / 2) positions[i * 3 + 2] = -CAGE_D / 2;
    if (positions[i * 3 + 2] < -CAGE_D / 2) positions[i * 3 + 2] = CAGE_D / 2;
  }
  particles.geometry.attributes.position.needsUpdate = true;

  // Wheel auto-spin decay
  if (wheelBody) {
    let anyRunning = hamsters.some(h => h.state === 'running_wheel');
    if (!anyRunning) {
      wheelBody.rotation.z *= 0.98;
    }
  }

  // Update stats every 30 frames
  if (frameCount % 30 === 0) {
    let stateCounts = {};
    hamsters.forEach(h => {
      stateCounts[h.state] = (stateCounts[h.state] || 0) + 1;
    });
    let lines = ['🐹 Hamsters:', ...hamsters.map(h => `  ${h.name}: ${h.state}`)];
    statsEl.innerHTML = lines.join('<br>');
  }

  renderer.render(scene, camera);
}

animate();

// ─── RESIZE ─────────────────────────────────────────────
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## What You Get 🐹

**Save as `index.html` and open in any modern browser.** Here's what's inside:

### Scene Elements
- **Wire cage** with vertical bars, horizontal rails, and a wooden floor tray with bedding
- **5 unique low-poly hamsters** — each with distinct warm color palettes (Nugget, Mochi, Biscuit, Peanut, Cookie), complete with chubby cheeks, whiskers, tiny paws, ear wiggles, and eye shine
- **Exercise wheel** (orange with spokes) that actually spins when a hamster runs on it
- **Tunnel** (teal cylinder with dark interior)
- **Food bowl** filled with scattered seeds
- **Water bowl** with translucent blue water
- **Wooden platform** with a tiny red-roofed house
- **Grass patches** and scattered seeds on the floor
- **Floating dust/fluff particles**

### Hamster AI Behaviors
Each hamster independently cycles through states:
| State | Behavior |
|-------|----------|
| 😴 **Idle** | Gentle breathing animation |
| 🚶 **Walking** | Steers toward random targets with smooth rotation + leg wobble |
| 🔄 **Turning** | Spins in place |
| 🍽️ **Eating** | Walks to the food bowl and does little head-bob nibbles |
| 🏃 **Running Wheel** | Jogs to the wheel, then runs in place while spinning it |
| 💤 **Sleeping** | Tilts down into a sleepy pose with slow breathing |

### Interactivity
- **Click & drag** to orbit the camera
- **Scroll** to zoom in/out
- **Hover** over any hamster to see their name and current activity in a tooltip
- **Stats panel** (top-right) shows all hamster states live