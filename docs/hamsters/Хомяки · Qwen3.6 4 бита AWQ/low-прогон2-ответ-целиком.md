

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; background: #1a1a2e; font-family: 'Segoe UI', sans-serif; }
canvas { display: block; }
#info {
  position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
  color: #fff; background: rgba(0,0,0,0.45); padding: 8px 20px;
  border-radius: 20px; font-size: 14px; pointer-events: none;
  backdrop-filter: blur(6px); letter-spacing: 0.5px;
}
#tooltip {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  color: #ffe0b2; background: rgba(0,0,0,0.5); padding: 6px 16px;
  border-radius: 14px; font-size: 12px; pointer-events: none;
  opacity: 0; transition: opacity 0.3s;
}
</style>
</head>
<body>
<div id="info">🐹 Low-Poly Hamster Playground — Drag to rotate · Scroll to zoom</div>
<div id="tooltip"></div>

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

// ─── SCENE SETUP ───
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87CEEB);
scene.fog = new THREE.FogExp2(0x87CEEB, 0.012);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 200);
camera.position.set(10, 9, 10);

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
controls.target.set(0, 1.5, 0);
controls.maxPolarAngle = Math.PI / 2.05;
controls.minDistance = 5;
controls.maxDistance = 25;

// ─── LIGHTING ───
const ambientLight = new THREE.AmbientLight(0xffeedd, 0.6);
scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(0xfff4e0, 1.4);
sunLight.position.set(8, 15, 6);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -10;
sunLight.shadow.camera.right = 10;
sunLight.shadow.camera.top = 10;
sunLight.shadow.camera.bottom = -10;
sunLight.shadow.camera.near = 1;
sunLight.shadow.camera.far = 30;
sunLight.shadow.bias = -0.001;
scene.add(sunLight);

const fillLight = new THREE.DirectionalLight(0xaaccff, 0.3);
fillLight.position.set(-5, 8, -5);
scene.add(fillLight);

// ─── MATERIALS ───
function mat(color, opts = {}) {
  return new THREE.MeshStandardMaterial({
    color, flatShading: true, roughness: opts.rough ?? 0.7,
    metalness: opts.metal ?? 0.0, ...opts
  });
}

const mats = {
  floor: mat(0xd4a574),
  cageBar: mat(0x888888, { metal: 0.4, rough: 0.3 }),
  cageBase: mat(0x5c4033),
  wheelFrame: mat(0xe8a84c),
  wheelRing: mat(0xf0c060, { metal: 0.2 }),
  tunnel: mat(0x6b8e5a),
  tunnelInside: mat(0x4a6b3a),
  bowl: mat(0xcc6644),
  food: mat(0x8B6914),
  grass: mat(0x5a8f3c),
  flower: mat(0xff6b8a),
  flowerCenter: mat(0xffd700),
  water: mat(0x4488cc, { transparent: true, opacity: 0.5 }),
};

const hamsterColors = [
  { body: 0xf5c6a0, belly: 0xfff0d0, ear: 0xe8a080 },
  { body: 0xd4a574, belly: 0xfff5e0, ear: 0xc08060 },
  { body: 0xb0b0b0, belly: 0xe0d8d0, ear: 0x909090 },
  { body: 0xffe0c0, belly: 0xfff8f0, ear: 0xffb090 },
  { body: 0xe8d0a0, belly: 0xfff0d8, ear: 0xd0a070 },
];

// ─── CAGE CONSTRUCTION ───
const cageW = 8, cageH = 4, cageD = 6;

// Floor tray
const floorGeo = new THREE.BoxGeometry(cageW + 0.4, 0.3, cageD + 0.4);
const floor = new THREE.Mesh(floorGeo, mats.cageBase);
floor.position.y = -0.15;
floor.receiveShadow = true;
scene.add(floor);

// Inner floor surface
const innerFloorGeo = new THREE.BoxGeometry(cageW - 0.2, 0.05, cageD - 0.2);
const innerFloor = new THREE.Mesh(innerFloorGeo, mats.floor);
innerFloor.position.y = 0.025;
innerFloor.receiveShadow = true;
scene.add(innerFloor);

// Grass patches
for (let i = 0; i < 8; i++) {
  const gx = (Math.random() - 0.5) * (cageW - 2);
  const gz = (Math.random() - 0.5) * (cageD - 2);
  const grassGeo = new THREE.CylinderGeometry(0.4 + Math.random() * 0.3, 0.5, 0.08, 6);
  const grass = new THREE.Mesh(grassGeo, mats.grass);
  grass.position.set(gx, 0.06, gz);
  grass.rotation.y = Math.random() * Math.PI;
  scene.add(grass);
}

// Cage bars - vertical
const barSpacing = 1.0;
const barGeoV = new THREE.BoxGeometry(0.06, cageH, 0.06);
for (let x = -cageW / 2; x <= cageW / 2 + 0.01; x += barSpacing) {
  // Front and back walls
  [-cageD / 2, cageD / 2].forEach(z => {
    const bar = new THREE.Mesh(barGeoV, mats.cageBar);
    bar.position.set(x, cageH / 2, z);
    bar.castShadow = true;
    scene.add(bar);
  });
}
for (let z = -cageD / 2 + barSpacing; z < cageD / 2; z += barSpacing) {
  // Left and right walls
  [-cageW / 2, cageW / 2].forEach(x => {
    const bar = new THREE.Mesh(barGeoV, mats.cageBar);
    bar.position.set(x, cageH / 2, z);
    bar.castShadow = true;
    scene.add(bar);
  });
}

// Horizontal bars
const barGeoH1 = new THREE.BoxGeometry(cageW + 0.1, 0.06, 0.06);
const barGeoH2 = new THREE.BoxGeometry(0.06, 0.06, cageD + 0.1);
[0, cageH / 2, cageH].forEach(y => {
  [-cageD / 2, cageD / 2].forEach(z => {
    const bar = new THREE.Mesh(barGeoH1, mats.cageBar);
    bar.position.set(0, y, z);
    scene.add(bar);
  });
  [-cageW / 2, cageW / 2].forEach(x => {
    const bar = new THREE.Mesh(barGeoH2, mats.cageBar);
    bar.position.set(x, y, 0);
    scene.add(bar);
  });
});

// Corner posts
const postGeo = new THREE.BoxGeometry(0.12, cageH, 0.12);
[[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([sx, sz]) => {
  const post = new THREE.Mesh(postGeo, mats.cageBar);
  post.position.set(sx * cageW / 2, cageH / 2, sz * cageD / 2);
  post.castShadow = true;
  scene.add(post);
});

// ─── HAMSTER WHEEL ───
const wheelGroup = new THREE.Group();
wheelGroup.position.set(-2.5, 0, -1.5);
scene.add(wheelGroup);

// Wheel platform
const platformGeo = new THREE.BoxGeometry(1.6, 0.15, 1.0);
const platform = new THREE.Mesh(platformGeo, mats.wheelFrame);
platform.position.y = 0.075;
platform.receiveShadow = true;
wheelGroup.add(platform);

// Wheel support pillars
const pillarGeo = new THREE.CylinderGeometry(0.06, 0.06, 1.8, 6);
[-0.6, 0.6].forEach(x => {
  const pillar = new THREE.Mesh(pillarGeo, mats.wheelFrame);
  pillar.position.set(x, 1.05, 0);
  pillar.castShadow = true;
  wheelGroup.add(pillar);
});

// Rotating wheel part
const wheelRotator = new THREE.Group();
wheelRotator.position.set(0, 1.8, 0);
wheelGroup.add(wheelRotator);

// Outer ring
const ringGeo = new THREE.TorusGeometry(0.9, 0.08, 6, 20);
const ring = new THREE.Mesh(ringGeo, mats.wheelRing);
ring.rotation.y = Math.PI / 2;
wheelRotator.add(ring);

// Inner ring (back)
const ringBack = new THREE.Mesh(ringGeo, mats.wheelRing);
ringBack.rotation.y = Math.PI / 2;
ringBack.position.z = -0.35;
wheelRotator.add(ringBack);

// Spokes
for (let i = 0; i < 8; i++) {
  const angle = (i / 8) * Math.PI * 2;
  const spokeGeo = new THREE.BoxGeometry(0.04, 0.04, 0.7);
  const spoke = new THREE.Mesh(spokeGeo, mats.wheelFrame);
  spoke.position.set(Math.cos(angle) * 0.45, Math.sin(angle) * 0.45, 0);
  spoke.rotation.z = angle;
  wheelRotator.add(spoke);
}

// Cross bars
[-0.35, 0, 0.35].forEach(z => {
  const crossGeo = new THREE.BoxGeometry(1.6, 0.04, 0.04);
  const cross = new THREE.Mesh(crossGeo, mats.wheelFrame);
  cross.position.z = z;
  wheelRotator.add(cross);
});

// ─── TUNNEL ───
const tunnelGroup = new THREE.Group();
tunnelGroup.position.set(2.5, 0, 1.5);
tunnelGroup.rotation.y = -0.3;
scene.add(tunnelGroup);

const tunnelLen = 2.0;
const tunnelR = 0.45;
const tunnelGeo = new THREE.CylinderGeometry(tunnelR, tunnelR, tunnelLen, 8, 1, true);
const tunnelMesh = new THREE.Mesh(tunnelGeo, mats.tunnel);
tunnelMesh.rotation.z = Math.PI / 2;
tunnelMesh.position.y = tunnelR + 0.05;
tunnelGroup.add(tunnelMesh);

// Tunnel ends (half cylinders)
const halfGeo = new THREE.SphereGeometry(tunnelR, 8, 6, 0, Math.PI * 2, 0, Math.PI / 2);
[-1, 1].forEach(side => {
  const half = new THREE.Mesh(halfGeo, mats.tunnel);
  half.rotation.z = side > 0 ? -Math.PI / 2 : Math.PI / 2;
  half.position.set(side * tunnelLen / 2, tunnelR + 0.05, 0);
  tunnelGroup.add(half);
});

// Tunnel roof
const roofGeo = new THREE.CylinderGeometry(tunnelR + 0.05, tunnelR + 0.05, tunnelLen, 8, 1, true, 0, Math.PI);
const roof = new THREE.Mesh(roofGeo, mats.tunnel);
roof.rotation.z = Math.PI / 2;
roof.position.y = tunnelR + 0.15;
roof.rotation.x = Math.PI;
tunnelGroup.add(roof);

// ─── FOOD BOWL ───
const bowlGroup = new THREE.Group();
bowlGroup.position.set(2.0, 0, -2.0);
scene.add(bowlGroup);

const bowlGeo = new THREE.CylinderGeometry(0.4, 0.25, 0.2, 8);
const bowl = new THREE.Mesh(bowlGeo, mats.bowl);
bowl.position.y = 0.1;
bowlGroup.add(bowl);

// Food pellets
for (let i = 0; i < 6; i++) {
  const pelletGeo = new THREE.SphereGeometry(0.06, 4, 4);
  const pellet = new THREE.Mesh(pelletGeo, mats.food);
  pellet.position.set(
    (Math.random() - 0.5) * 0.5,
    0.22,
    (Math.random() - 0.5) * 0.5
  );
  bowlGroup.add(pellet);
}

// ─── WATER BOWL ───
const waterGroup = new THREE.Group();
waterGroup.position.set(-2.0, 0, 2.0);
scene.add(waterGroup);

const waterBowlGeo = new THREE.CylinderGeometry(0.3, 0.2, 0.15, 8);
const waterBowl = new THREE.Mesh(waterBowlGeo, mats.bowl);
waterBowl.position.y = 0.075;
waterGroup.add(waterBowl);

const waterGeo = new THREE.CylinderGeometry(0.25, 0.25, 0.02, 8);
const water = new THREE.Mesh(waterGeo, mats.water);
water.position.y = 0.16;
waterGroup.add(water);

// ─── FLOWERS ───
function createFlower(x, z) {
  const group = new THREE.Group();
  group.position.set(x, 0, z);

  // Stem
  const stemGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.5, 4);
  const stem = new THREE.Mesh(stemGeo, mats.grass);
  stem.position.y = 0.25;
  group.add(stem);

  // Petals
  for (let i = 0; i < 5; i++) {
    const petalGeo = new THREE.SphereGeometry(0.08, 4, 4);
    const petal = new THREE.Mesh(petalGeo, mats.flower);
    const a = (i / 5) * Math.PI * 2;
    petal.position.set(Math.cos(a) * 0.1, 0.5, Math.sin(a) * 0.1);
    group.add(petal);
  }

  // Center
  const centerGeo = new THREE.SphereGeometry(0.06, 4, 4);
  const center = new THREE.Mesh(centerGeo, mats.flowerCenter);
  center.position.y = 0.5;
  group.add(center);

  scene.add(group);
}

createFlower(-3.5, 2.5);
createFlower(3.0, -2.5);
createFlower(-1.0, 2.5);

// ─── HAMSTER FACTORY ───
function createHamster(colorSet, scale = 0.5) {
  const hamster = new THREE.Group();
  hamster.userData = {
    state: 'idle',
    stateTimer: 0,
    targetPos: null,
    speed: 0.5 + Math.random() * 0.5,
    walkPhase: Math.random() * Math.PI * 2,
    colors: colorSet,
    atWheel: false,
    wheelAngle: 0,
    eatingTimer: 0,
  };

  const s = scale;
  const bodyMat = mat(colorSet.body);
  const bellyMat = mat(colorSet.belly);
  const earMat = mat(colorSet.ear);

  // Body (main ellipsoid)
  const bodyGeo = new THREE.SphereGeometry(0.4 * s, 8, 6);
  bodyGeo.scale(1, 0.75, 0.85);
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.position.y = 0.35 * s;
  body.castShadow = true;
  hamster.add(body);

  // Belly
  const bellyGeo = new THREE.SphereGeometry(0.28 * s, 6, 4);
  bellyGeo.scale(1, 0.6, 0.7);
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.position.set(0, 0.25 * s, 0.1 * s);
  hamster.add(belly);

  // Head
  const headGeo = new THREE.SphereGeometry(0.28 * s, 8, 6);
  headGeo.scale(1, 0.85, 0.9);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.position.set(0, 0.45 * s, 0.3 * s);
  head.castShadow = true;
  hamster.add(head);

  // Snout
  const snoutGeo = new THREE.SphereGeometry(0.1 * s, 6, 4);
  snoutGeo.scale(1, 0.7, 1.2);
  const snout = new THREE.Mesh(snoutGeo, bellyMat);
  snout.position.set(0, 0.38 * s, 0.5 * s);
  hamster.add(snout);

  // Nose
  const noseGeo = new THREE.SphereGeometry(0.04 * s, 4, 4);
  const noseMat = mat(0xff8888);
  const nose = new THREE.Mesh(noseGeo, noseMat);
  nose.position.set(0, 0.4 * s, 0.58 * s);
  hamster.add(nose);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.05 * s, 6, 4);
  const eyeMat = mat(0x222222);
  [-1, 1].forEach(side => {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(side * 0.14 * s, 0.5 * s, 0.42 * s);
    hamster.add(eye);

    // Eye shine
    const shineGeo = new THREE.SphereGeometry(0.02 * s, 4, 4);
    const shineMat = mat(0xffffff);
    const shine = new THREE.Mesh(shineGeo, shineMat);
    shine.position.set(side * 0.16 * s, 0.52 * s, 0.46 * s);
    hamster.add(shine);
  });

  // Ears
  const earGeo = new THREE.SphereGeometry(0.1 * s, 6, 4);
  earGeo.scale(1, 0.6, 0.8);
  [-1, 1].forEach(side => {
    const ear = new THREE.Mesh(earGeo, earMat);
    ear.position.set(side * 0.2 * s, 0.6 * s, 0.2 * s);
    ear.rotation.z = side * 0.3;
    hamster.add(ear);
  });

  // Cheeks (puffy!)
  const cheekGeo = new THREE.SphereGeometry(0.12 * s, 6, 4);
  const cheekMat = mat(colorSet.belly);
  [-1, 1].forEach(side => {
    const cheek = new THREE.Mesh(cheekGeo, cheekMat);
    cheek.position.set(side * 0.25 * s, 0.35 * s, 0.35 * s);
    hamster.add(cheek);
  });

  // Tail
  const tailGeo = new THREE.SphereGeometry(0.08 * s, 4, 4);
  tailGeo.scale(0.6, 0.6, 1);
  const tail = new THREE.Mesh(tailGeo, bodyMat);
  tail.position.set(0, 0.25 * s, -0.4 * s);
  hamster.add(tail);

  // Legs (4 little legs)
  const legGeo = new THREE.CylinderGeometry(0.04 * s, 0.05 * s, 0.15 * s, 4);
  const legPositions = [
    [-0.15, 0.075, 0.2],
    [0.15, 0.075, 0.2],
    [-0.15, 0.075, -0.2],
    [0.15, 0.075, -0.2],
  ];
  hamster.userData.legs = [];
  legPositions.forEach(pos => {
    const leg = new THREE.Mesh(legGeo, bodyMat);
    leg.position.set(...pos.map(p => p * s));
    leg.castShadow = true;
    hamster.add(leg);
    hamster.userData.legs.push(leg);
  });

  return hamster;
}

// ─── CREATE HAMSTERS ───
const hamsters = [];
const hamsterNames = ['Nugget', 'Mochi', 'Biscuit', 'Cinnamon', 'Peanut'];

for (let i = 0; i < 5; i++) {
  const h = createHamster(hamsterColors[i], 0.45 + Math.random() * 0.1);
  const x = (Math.random() - 0.5) * (cageW - 2);
  const z = (Math.random() - 0.5) * (cageD - 2);
  h.position.set(x, 0, z);
  h.rotation.y = Math.random() * Math.PI * 2;
  h.userData.name = hamsterNames[i];
  h.userData.stateTimer = Math.random() * 3;
  scene.add(h);
  hamsters.push(h);
}

// ─── GROUND OUTSIDE CAGE ───
const groundGeo = new THREE.PlaneGeometry(60, 60);
const groundMat = mat(0x4a7c3f);
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.3;
ground.receiveShadow = true;
scene.add(ground);

// Some outside rocks
for (let i = 0; i < 12; i++) {
  const rockGeo = new THREE.DodecahedronGeometry(0.2 + Math.random() * 0.3, 0);
  const rockMat = mat(0x888877 + Math.floor(Math.random() * 0x222222));
  const rock = new THREE.Mesh(rockGeo, rockMat);
  const angle = Math.random() * Math.PI * 2;
  const dist = 6 + Math.random() * 8;
  rock.position.set(Math.cos(angle) * dist, -0.15, Math.sin(angle) * dist);
  rock.rotation.set(Math.random(), Math.random(), Math.random());
  rock.castShadow = true;
  scene.add(rock);
}

// ─── HAMSTER AI ───
const wheelPos = new THREE.Vector3(-2.5, 0, -1.5);
const bowlPos = new THREE.Vector3(2.0, 0, -2.0);
const tunnelPos = new THREE.Vector3(2.5, 0, 1.5);

function getBounds() {
  return {
    minX: -cageW / 2 + 0.5,
    maxX: cageW / 2 - 0.5,
    minZ: -cageD / 2 + 0.5,
    maxZ: cageD / 2 - 0.5,
  };
}

function randomTarget() {
  const b = getBounds();
  return new THREE.Vector3(
    b.minX + Math.random() * (b.maxX - b.minX),
    0,
    b.minZ + Math.random() * (b.maxZ - b.minZ)
  );
}

function updateHamsterAI(hamster, dt) {
  const ud = hamster.userData;
  ud.stateTimer -= dt;

  switch (ud.state) {
    case 'idle':
      if (ud.stateTimer <= 0) {
        // Pick a new activity
        const r = Math.random();
        if (r < 0.25 && !ud.atWheel) {
          ud.state = 'walkToWheel';
          ud.stateTimer = 999;
        } else if (r < 0.4) {
          ud.state = 'walk';
          ud.targetPos = randomTarget();
          ud.stateTimer = 999;
        } else if (r < 0.55) {
          ud.state = 'eat';
          ud.targetPos = bowlPos.clone();
          ud.stateTimer = 999;
        } else if (r < 0.65) {
          ud.state = 'exploreTunnel';
          ud.stateTimer = 999;
        } else {
          ud.state = 'idle';
          ud.stateTimer = 1 + Math.random() * 3;
        }
      }
      break;

    case 'walk':
      if (ud.targetPos) {
        const dir = ud.targetPos.clone().sub(hamster.position);
        dir.y = 0;
        const dist = dir.length();
        if (dist > 0.2) {
          dir.normalize();
          hamster.position.add(dir.multiplyScalar(ud.speed * dt));
          hamster.rotation.y = Math.atan2(dir.x, dir.z);
          ud.walkPhase += dt * 8;
        } else {
          ud.state = 'idle';
          ud.stateTimer = 1 + Math.random() * 2;
        }
      } else {
        ud.state = 'idle';
      }
      break;

    case 'walkToWheel': {
      const dir = wheelPos.clone().sub(hamster.position);
      dir.y = 0;
      const dist = dir.length();
      if (dist > 0.8) {
        dir.normalize();
        hamster.position.add(dir.multiplyScalar(ud.speed * 1.2 * dt));
        hamster.rotation.y = Math.atan2(dir.x, dir.z);
        ud.walkPhase += dt * 10;
      } else {
        ud.state = 'runWheel';
        ud.stateTimer = 2 + Math.random() * 3;
        ud.atWheel = true;
        // Position at front of wheel
        hamster.position.set(wheelPos.x, 0, wheelPos.z + 0.8);
        hamster.rotation.y = Math.PI;
      }
      break;
    }

    case 'runWheel':
      if (ud.stateTimer <= 0) {
        ud.state = 'idle';
        ud.stateTimer = 2 + Math.random() * 2;
        ud.atWheel = false;
      }
      ud.wheelAngle += dt * 3;
      // Wiggle while running
      hamster.position.x = wheelPos.x + Math.sin(ud.walkPhase * 2) * 0.02;
      ud.walkPhase += dt * 12;
      break;

    case 'eat': {
      const dir = bowlPos.clone().sub(hamster.position);
      dir.y = 0;
      const dist = dir.length();
      if (dist > 0.5) {
        dir.normalize();
        hamster.position.add(dir.multiplyScalar(ud.speed * dt));
        hamster.rotation.y = Math.atan2(dir.x, dir.z);
        ud.walkPhase += dt * 8;
      } else {
        hamster.rotation.y = Math.atan2(bowlPos.x - hamster.position.x, bowlPos.z - hamster.position.z);
        ud.eatingTimer = 2 + Math.random() * 2;
        ud.state = 'eating';
      }
      break;
    }

    case 'eating':
      if (ud.eatingTimer <= 0) {
        ud.state = 'idle';
        ud.stateTimer = 1 + Math.random() * 2;
      } else {
        ud.eatingTimer -= dt;
        // Bobbing animation
        hamster.children[0].position.y = 0.35 * hamster.scale.x + Math.sin(Date.now() * 0.005) * 0.01;
      }
      break;

    case 'exploreTunnel': {
      const dir = tunnelPos.clone().sub(hamster.position);
      dir.y = 0;
      const dist = dir.length();
      if (dist > 0.6) {
        dir.normalize();
        hamster.position.add(dir.multiplyScalar(ud.speed * 0.8 * dt));
        hamster.rotation.y = Math.atan2(dir.x, dir.z);
        ud.walkPhase += dt * 6;
      } else {
        ud.state = 'idle';
        ud.stateTimer = 1 + Math.random() * 1.5;
      }
      break;
    }
  }

  // Clamp to cage bounds
  const b = getBounds();
  hamster.position.x = Math.max(b.minX, Math.min(b.maxX, hamster.position.x));
  hamster.position.z = Math.max(b.minZ, Math.min(b.maxZ, hamster.position.z));
}

// ─── ANIMATION LOOP ───
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.getElapsedTime();

  controls.update();

  // Update hamster AI
  hamsters.forEach(h => updateHamsterAI(h, dt));

  // Animate hamster legs
  hamsters.forEach(h => {
    const ud = h.userData;
    if (ud.state === 'walk' || ud.state === 'walkToWheel' || ud.state === 'runWheel' || ud.state === 'exploreTunnel') {
      ud.legs.forEach((leg, i) => {
        const phase = ud.walkPhase + (i % 2 === 0 ? 0 : Math.PI);
        const side = i < 2 ? 1 : -1;
        leg.rotation.x = Math.sin(phase) * 0.4 * side;
      });
    } else {
      ud.legs.forEach(leg => {
        leg.rotation.x *= 0.9;
      });
    }

    // Subtle breathing
    if (ud.state === 'idle' || ud.state === 'eating') {
      const breathe = Math.sin(time * 2) * 0.005;
      h.scale.setScalar(1 + breathe);
    }
  });

  // Rotate wheel if any hamster is running it
  let wheelSpeed = 0;
  hamsters.forEach(h => {
    if (h.userData.state === 'runWheel') {
      wheelSpeed += 3;
    }
  });
  wheelRotator.rotation.z += wheelSpeed * dt;

  // Gentle water ripple
  water.scale.x = 1 + Math.sin(time * 2) * 0.02;
  water.scale.z = 1 + Math.cos(time * 2.3) * 0.02;

  // Flower sway
  scene.children.forEach(child => {
    if (child.isGroup && child.children.length >= 5) {
      // Check if it's a flower group
      if (child.children[0]?.geometry?.type === 'CylinderGeometry' && child.children[0].geometry.parameters.radiusTop === 0.02) {
        child.rotation.z = Math.sin(time * 1.5 + child.position.x) * 0.05;
        child.rotation.x = Math.cos(time * 1.2 + child.position.z) * 0.03;
      }
    }
  });

  renderer.render(scene, camera);
}

animate();

// ─── RESIZE ───
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// ─── TOOLTIP ON HOVER ───
const tooltip = document.getElementById('tooltip');
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('mousemove', (e) => {
  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);

  let found = false;
  for (const h of hamsters) {
    const intersects = raycaster.intersectObject(h, true);
    if (intersects.length > 0) {
      tooltip.textContent = `🐹 ${h.userData.name} — ${h.userData.state.replace(/([A-Z])/g, ' $1').trim()}`;
      tooltip.style.opacity = '1';
      renderer.domElement.style.cursor = 'pointer';
      found = true;
      break;
    }
  }
  if (!found) {
    tooltip.style.opacity = '0';
    renderer.domElement.style.cursor = 'grab';
  }
});

</script>
</body>
</html>
```

This creates a complete **Low-Poly Hamster Playground** with:

### 🏠 Scene Elements
- **Cage** — wire-bar construction with corner posts, horizontal rails, and a wooden base tray
- **Grass patches** scattered across the floor
- **Hamster wheel** — fully detailed with spokes, cross-bars, and a platform
- **Tunnel** — a green arched tunnel for the hamsters to explore
- **Food bowl** with visible pellets
- **Water bowl** with animated ripple effect
- **Decorative flowers** that gently sway
- **Outside world** with ground and scattered rocks

### 🐹 5 Unique Hamsters
Each named (Nugget, Mochi, Biscuit, Cinnamon, Peanut) with distinct color palettes (golden, brown, gray, peach, cream). Built from low-poly spheres with:
- Puffy cheeks, tiny noses, shiny eyes, little ears
- Animated legs that walk when moving
- Breathing animation when idle

### 🧠 Autonomous AI Behavior
Hamsters cycle through states: **idle → wander → run the wheel → eat from bowl → explore the tunnel**, all with smooth transitions. Multiple hamsters can run the wheel simultaneously (it spins faster!).

### 🎮 Interaction
- **Drag** to orbit the camera
- **Scroll** to zoom in/out
- **Hover** over hamsters to see their name and current activity