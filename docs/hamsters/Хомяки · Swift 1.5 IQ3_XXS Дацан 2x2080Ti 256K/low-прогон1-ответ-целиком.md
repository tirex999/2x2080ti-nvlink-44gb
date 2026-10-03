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
#ui {
  position: fixed; top: 20px; left: 20px; z-index: 10;
  color: #fff; pointer-events: none;
}
#ui h1 {
  font-size: 28px; font-weight: 700;
  background: linear-gradient(135deg, #ff6b9d, #c44dff);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  text-shadow: none; margin-bottom: 6px;
}
#ui p { font-size: 13px; color: #aaa; }
#stats {
  position: fixed; bottom: 20px; left: 20px; z-index: 10;
  color: #ccc; font-size: 12px;
}
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Hamster Playground</h1>
  <p>Drag to rotate • Scroll to zoom</p>
</div>
<div id="stats"></div>

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

// ─── Scene Setup ───────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);
scene.fog = new THREE.FogExp2(0x1a1a2e, 0.035);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(8, 7, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.maxPolarAngle = Math.PI / 2.1;
controls.minDistance = 4;
controls.maxDistance = 20;
controls.target.set(0, 1.5, 0);

// ─── Lights ────────────────────────────────────────────────────
const ambientLight = new THREE.AmbientLight(0x6666aa, 0.4);
scene.add(ambientLight);

const mainLight = new THREE.DirectionalLight(0xffeedd, 1.5);
mainLight.position.set(5, 10, 5);
mainLight.castShadow = true;
mainLight.shadow.mapSize.set(2048, 2048);
mainLight.shadow.camera.near = 0.5;
mainLight.shadow.camera.far = 30;
mainLight.shadow.camera.left = -10;
mainLight.shadow.camera.right = 10;
mainLight.shadow.camera.top = 10;
mainLight.shadow.camera.bottom = -10;
scene.add(mainLight);

const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3);
fillLight.position.set(-5, 3, -5);
scene.add(fillLight);

const rimLight = new THREE.PointLight(0xff6b9d, 0.5, 15);
rimLight.position.set(0, 6, -4);
scene.add(rimLight);

// ─── Materials ─────────────────────────────────────────────────
const matFloor = new THREE.MeshStandardMaterial({ color: 0x3d2b1f, roughness: 0.9 });
const matBedding = new THREE.MeshStandardMaterial({ color: 0xf5e6c8, roughness: 1.0 });
const matCageWire = new THREE.MeshStandardMaterial({ color: 0x888899, metalness: 0.7, roughness: 0.3 });
const matCageWire2 = new THREE.MeshStandardMaterial({ color: 0x666677, metalness: 0.6, roughness: 0.4 });

// ─── Floor / Tray ──────────────────────────────────────────────
const floorGeo = new THREE.CylinderGeometry(5, 5, 0.3, 12);
const floor = new THREE.Mesh(floorGeo, matFloor);
floor.position.y = -0.15;
floor.receiveShadow = true;
scene.add(floor);

// Bedding (wood shavings look)
const beddingGroup = new THREE.Group();
for (let i = 0; i < 80; i++) {
  const angle = Math.random() * Math.PI * 2;
  const radius = Math.random() * 4.5;
  const chunkGeo = new THREE.BoxGeometry(
    0.15 + Math.random() * 0.2,
    0.04 + Math.random() * 0.03,
    0.08 + Math.random() * 0.1
  );
  const shade = 0.85 + Math.random() * 0.15;
  const mat = new THREE.MeshStandardMaterial({
    color: new THREE.Color(shade * 0.96, shade * 0.88, shade * 0.72),
    roughness: 1.0
  });
  const chunk = new THREE.Mesh(chunkGeo, mat);
  chunk.position.set(
    Math.cos(angle) * radius,
    0.02 + Math.random() * 0.02,
    Math.sin(angle) * radius
  );
  chunk.rotation.y = Math.random() * Math.PI;
  chunk.receiveShadow = true;
  beddingGroup.add(chunk);
}
scene.add(beddingGroup);

// ─── Cage (Wire Frame) ─────────────────────────────────────────
const cageGroup = new THREE.Group();
const wireRadius = 4.8;
const wireHeight = 5;
const wireSegments = 24;

// Vertical wires
for (let i = 0; i < wireSegments; i++) {
  const angle = (i / wireSegments) * Math.PI * 2;
  const wireGeo = new THREE.CylinderGeometry(0.03, 0.03, wireHeight, 4);
  const wire = new THREE.Mesh(wireGeo, matCageWire);
  wire.position.set(
    Math.cos(angle) * wireRadius,
    wireHeight / 2,
    Math.sin(angle) * wireRadius
  );
  wire.castShadow = true;
  cageGroup.add(wire);
}

// Horizontal rings
for (let j = 0; j < 6; j++) {
  const y = (j / 5) * wireHeight;
  const ringGeo = new THREE.TorusGeometry(wireRadius, 0.03, 4, wireSegments);
  const ring = new THREE.Mesh(ringGeo, matCageWire2);
  ring.position.y = y;
  ring.rotation.x = Math.PI / 2;
  cageGroup.add(ring);
}

// Top dome (partial)
const topRingGeo = new THREE.TorusGeometry(wireRadius * 0.6, 0.03, 4, wireSegments);
const topRing = new THREE.Mesh(topRingGeo, matCageWire2);
topRing.position.y = wireHeight;
topRing.rotation.x = Math.PI / 2;
cageGroup.add(topRing);

// Connecting wires from top ring to cage edges
for (let i = 0; i < 8; i++) {
  const angle = (i / 8) * Math.PI * 2;
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(Math.cos(angle) * wireRadius * 0.6, wireHeight, Math.sin(angle) * wireRadius * 0.6),
    new THREE.Vector3(Math.cos(angle) * wireRadius * 0.8, wireHeight + 0.5, Math.sin(angle) * wireRadius * 0.8),
    new THREE.Vector3(Math.cos(angle) * wireRadius, wireHeight, Math.sin(angle) * wireRadius)
  ]);
  const tubeGeo = new THREE.TubeGeometry(curve, 6, 0.03, 4, false);
  const tube = new THREE.Mesh(tubeGeo, matCageWire2);
  cageGroup.add(tube);
}

scene.add(cageGroup);

// ─── Running Wheel ─────────────────────────────────────────────
const wheelGroup = new THREE.Group();
const wheelRadius = 1.4;

// Wheel ring (torus)
const wheelRingGeo = new THREE.TorusGeometry(wheelRadius, 0.12, 6, 16);
const wheelRingMat = new THREE.MeshStandardMaterial({ color: 0xff6b9d, roughness: 0.4 });
const wheelRing = new THREE.Mesh(wheelRingGeo, wheelRingMat);
wheelGroup.add(wheelRing);

// Spokes
for (let i = 0; i < 8; i++) {
  const angle = (i / 8) * Math.PI * 2;
  const spokeGeo = new THREE.CylinderGeometry(0.04, 0.04, wheelRadius * 2, 4);
  const spokeMat = new THREE.MeshStandardMaterial({ color: 0xffaacc, roughness: 0.5 });
  const spoke = new THREE.Mesh(spokeGeo, spokeMat);
  spoke.rotation.z = angle;
  spoke.castShadow = true;
  wheelGroup.add(spoke);
}

// Center hub
const hubGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.3, 8);
const hubMat = new THREE.MeshStandardMaterial({ color: 0xcc4488, roughness: 0.3 });
const hub = new THREE.Mesh(hubGeo, hubMat);
hub.rotation.x = Math.PI / 2;
wheelGroup.add(hub);

// Stand
const standGeo = new THREE.BoxGeometry(0.15, 2.2, 0.15);
const standMat = new THREE.MeshStandardMaterial({ color: 0x888899, metalness: 0.5 });
const stand1 = new THREE.Mesh(standGeo, standMat);
stand1.position.set(0, -wheelRadius - 0.5, 0.4);
wheelGroup.add(stand1);
const stand2 = new THREE.Mesh(standGeo, standMat);
stand2.position.set(0, -wheelRadius - 0.5, -0.4);
wheelGroup.add(stand2);

// Base
const baseGeo = new THREE.BoxGeometry(1.2, 0.12, 1.5);
const base = new THREE.Mesh(baseGeo, standMat);
base.position.y = -wheelRadius - 1.5;
base.castShadow = true;
wheelGroup.add(base);

wheelGroup.position.set(3.5, wheelRadius + 1.5, 0);
wheelGroup.castShadow = true;
scene.add(wheelGroup);

// ─── Food Bowl ─────────────────────────────────────────────────
const bowlGroup = new THREE.Group();
const bowlGeo = new THREE.CylinderGeometry(0.6, 0.4, 0.35, 8);
const bowlMat = new THREE.MeshStandardMaterial({ color: 0x44ccaa, roughness: 0.6 });
const bowl = new THREE.Mesh(bowlGeo, bowlMat);
bowl.castShadow = true;
bowlGroup.add(bowl);

// Food inside (pellets)
for (let i = 0; i < 6; i++) {
  const pelletGeo = new THREE.DodecahedronGeometry(0.12, 0);
  const pelletMat = new THREE.MeshStandardMaterial({ color: 0xcc8844, roughness: 0.9 });
  const pellet = new THREE.Mesh(pelletGeo, pelletMat);
  pellet.position.set(
    (Math.random() - 0.5) * 0.4,
    0.1,
    (Math.random() - 0.5) * 0.4
  );
  pellet.rotation.set(Math.random(), Math.random(), Math.random());
  bowlGroup.add(pellet);
}

bowlGroup.position.set(-2.5, 0.18, 1.5);
scene.add(bowlGroup);

// ─── Tunnel ────────────────────────────────────────────────────
const tunnelGroup = new THREE.Group();
const tunnelGeo = new THREE.CylinderGeometry(0.7, 0.7, 2.5, 8, 1, true);
const tunnelMat = new THREE.MeshStandardMaterial({
  color: 0xffcc44, roughness: 0.5, side: THREE.DoubleSide
});
const tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
tunnel.rotation.z = Math.PI / 2;
tunnel.castShadow = true;
tunnelGroup.add(tunnel);

// Tunnel rings for decoration
for (let i = 0; i < 4; i++) {
  const ringGeo = new THREE.TorusGeometry(0.72, 0.05, 4, 8);
  const ringMat = new THREE.MeshStandardMaterial({ color: 0xff9922, roughness: 0.4 });
  const ring = new THREE.Mesh(ringGeo, ringMat);
  ring.position.x = -1.2 + i * 0.8;
  ring.rotation.y = Math.PI / 2;
  tunnelGroup.add(ring);
}

tunnelGroup.position.set(-1, 0.7, -2.5);
scene.add(tunnelGroup);

// ─── Hamster Factory ───────────────────────────────────────────
const hamsterColors = [
  { body: 0xf4a460, belly: 0xfff8dc, cheeks: 0xffb6c1 },
  { body: 0xdeb887, belly: 0xfff8dc, cheeks: 0xffccdd },
  { body: 0xc0c0c0, belly: 0xf5f5f5, cheeks: 0xffb6c1 },
  { body: 0xffd700, belly: 0xfff8dc, cheeks: 0xff9999 },
  { body: 0x8b4513, belly: 0xf5deb3, cheeks: 0xffaa88 },
];

function createHamster(colorSet) {
  const group = new THREE.Group();

  // Body (low-poly sphere - icosahedron detail 1)
  const bodyGeo = new THREE.IcosahedronGeometry(0.45, 1);
  const bodyMat = new THREE.MeshStandardMaterial({ color: colorSet.body, roughness: 0.8 });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.scale.set(1.2, 1.0, 1.0);
  body.castShadow = true;
  group.add(body);

  // Belly (lighter underside)
  const bellyGeo = new THREE.IcosahedronGeometry(0.38, 1);
  const bellyMat = new THREE.MeshStandardMaterial({ color: colorSet.belly, roughness: 0.9 });
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.position.set(0, -0.1, 0);
  belly.scale.set(1.1, 0.8, 0.95);
  group.add(belly);

  // Head
  const headGeo = new THREE.IcosahedronGeometry(0.28, 1);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.position.set(0.4, 0.1, 0);
  head.castShadow = true;
  group.add(head);

  // Cheeks (puffy!)
  const cheekGeo = new THREE.IcosahedronGeometry(0.18, 1);
  const cheekMat = new THREE.MeshStandardMaterial({ color: colorSet.cheeks, roughness: 0.9 });
  const cheekL = new THREE.Mesh(cheekGeo, cheekMat);
  cheekL.position.set(0.35, -0.02, 0.2);
  group.add(cheekL);
  const cheekR = new THREE.Mesh(cheekGeo.clone(), cheekMat);
  cheekR.position.set(0.35, -0.02, -0.2);
  group.add(cheekR);

  // Ears
  const earGeo = new THREE.IcosahedronGeometry(0.1, 1);
  const earMat = new THREE.MeshStandardMaterial({ color: colorSet.cheeks, roughness: 0.8 });
  const earL = new THREE.Mesh(earGeo, earMat);
  earL.position.set(0.35, 0.32, 0.15);
  group.add(earL);
  const earR = new THREE.Mesh(earGeo.clone(), earMat);
  earR.position.set(0.35, 0.32, -0.15);
  group.add(earR);

  // Eyes (black beads)
  const eyeGeo = new THREE.SphereGeometry(0.05, 6, 4);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.2 });
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(0.55, 0.12, 0.12);
  group.add(eyeL);
  const eyeR = new THREE.Mesh(eyeGeo.clone(), eyeMat);
  eyeR.position.set(0.55, 0.12, -0.12);
  group.add(eyeR);

  // Eye shine
  const shineGeo = new THREE.SphereGeometry(0.02, 4, 3);
  const shineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const shineL = new THREE.Mesh(shineGeo, shineMat);
  shineL.position.set(0.57, 0.14, 0.13);
  group.add(shineL);
  const shineR = new THREE.Mesh(shineGeo.clone(), shineMat);
  shineR.position.set(0.57, 0.14, -0.11);
  group.add(shineR);

  // Nose
  const noseGeo = new THREE.IcosahedronGeometry(0.04, 0);
  const noseMat = new THREE.MeshStandardMaterial({ color: 0xff6688, roughness: 0.5 });
  const nose = new THREE.Mesh(noseGeo, noseMat);
  nose.position.set(0.65, 0.02, 0);
  group.add(nose);

  // Tail (tiny nub)
  const tailGeo = new THREE.ConeGeometry(0.06, 0.12, 4);
  const tail = new THREE.Mesh(tailGeo, bodyMat);
  tail.position.set(-0.5, -0.05, 0);
  tail.rotation.z = Math.PI / 2;
  group.add(tail);

  // Feet (tiny stubs)
  const footGeo = new THREE.BoxGeometry(0.12, 0.08, 0.1);
  const footMat = new THREE.MeshStandardMaterial({ color: colorSet.cheeks, roughness: 0.8 });
  const positions = [
    [0.3, -0.4, 0.25], [0.3, -0.4, -0.25],
    [-0.2, -0.4, 0.25], [-0.2, -0.4, -0.25]
  ];
  positions.forEach(pos => {
    const foot = new THREE.Mesh(footGeo, footMat);
    foot.position.set(...pos);
    group.add(foot);
  });

  return group;
}

// ─── Create Hamsters ───────────────────────────────────────────
const hamsters = [];
const hamsterStates = { WALK: 0, PAUSE: 1, INTERACT: 0 };

for (let i = 0; i < 5; i++) {
  const hamster = createHamster(hamsterColors[i % hamsterColors.length]);
  const angle = (i / 5) * Math.PI * 2 + Math.random() * 0.5;
  const radius = 1.5 + Math.random() * 2.5;
  hamster.position.set(
    Math.cos(angle) * radius,
    0.45,
    Math.sin(angle) * radius
  );
  hamster.castShadow = true;

  const data = {
    mesh: hamster,
    state: 'WALK',
    speed: 0.8 + Math.random() * 0.6,
    direction: Math.random() * Math.PI * 2,
    timer: 0,
    stateDuration: 2 + Math.random() * 3,
    bobPhase: Math.random() * Math.PI * 2,
    targetWheel: i < 2, // First two hamsters like the wheel
    targetBowl: i === 3,  // One likes food
    targetTunnel: i === 4, // One likes tunnel
    interactTimer: 0,
  };
  hamsters.push(data);
  scene.add(hamster);
}

// ─── Decorative Elements ───────────────────────────────────────
// Water bottle
const bottleGroup = new THREE.Group();
const bottleGeo = new THREE.CylinderGeometry(0.25, 0.25, 1.2, 8);
const bottleMat = new THREE.MeshStandardMaterial({
  color: 0x88ccff, transparent: true, opacity: 0.6, roughness: 0.2
});
const bottle = new THREE.Mesh(bottleGeo, bottleMat);
bottleGroup.add(bottle);
const capGeo = new THREE.CylinderGeometry(0.12, 0.15, 0.2, 6);
const capMat = new THREE.MeshStandardMaterial({ color: 0xcc4444 });
const cap = new THREE.Mesh(capGeo, capMat);
cap.position.y = -0.7;
bottleGroup.add(cap);
const tubeGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.4, 4);
const tube = new THREE.Mesh(tubeGeo, capMat);
tube.position.y = -1.0;
bottleGroup.add(tube);
bottleGroup.position.set(2, 3.5, -3.5);
scene.add(bottleGroup);

// Small house/hideout
const houseGroup = new THREE.Group();
const houseGeo = new THREE.BoxGeometry(1.2, 0.9, 1.0);
const houseMat = new THREE.MeshStandardMaterial({ color: 0xff8866, roughness: 0.7 });
const house = new THREE.Mesh(houseGeo, houseMat);
house.castShadow = true;
houseGroup.add(house);
// Roof
const roofGeo = new THREE.ConeGeometry(0.9, 0.5, 4);
const roofMat = new THREE.MeshStandardMaterial({ color: 0xcc4444, roughness: 0.6 });
const roof = new THREE.Mesh(roofGeo, roofMat);
roof.position.y = 0.7;
roof.rotation.y = Math.PI / 4;
roof.castShadow = true;
houseGroup.add(roof);
// Door (dark inset)
const doorGeo = new THREE.PlaneGeometry(0.35, 0.5);
const doorMat = new THREE.MeshStandardMaterial({ color: 0x222222 });
const door = new THREE.Mesh(doorGeo, doorMat);
door.position.set(0, -0.1, 0.51);
houseGroup.add(door);
houseGroup.position.set(1.5, 0.45, 3.2);
scene.add(houseGroup);

// ─── Animation Loop ────────────────────────────────────────────
const clock = new THREE.Clock();
let wheelSpeed = 0;
let statsEl = document.getElementById('stats');
let frameCount = 0;
let lastTime = performance.now();

function updateHamster(h, dt, time) {
  const mesh = h.mesh;

  // State machine
  h.timer += dt;
  if (h.timer > h.stateDuration) {
    h.timer = 0;
    h.stateDuration = 2 + Math.random() * 4;

    if (h.state === 'WALK') {
      const roll = Math.random();
      if (roll < 0.35) {
        h.state = 'PAUSE';
        h.stateDuration = 1 + Math.random() * 2;
      } else if (roll < 0.6 && h.targetWheel) {
        h.state = 'WHEEL';
        h.stateDuration = 2 + Math.random() * 3;
      } else if (roll < 0.75 && h.targetBowl) {
        h.state = 'EAT';
        h.stateDuration = 1.5 + Math.random() * 2;
      } else {
        h.state = 'WALK';
        h.direction = Math.random() * Math.PI * 2;
      }
    } else if (h.state === 'PAUSE') {
      h.state = 'WALK';
      h.direction = Math.random() * Math.PI * 2;
    } else if (h.state === 'WHEEL') {
      h.state = 'WALK';
      h.direction = Math.random() * Math.PI * 2;
    } else if (h.state === 'EAT') {
      h.state = 'WALK';
      h.direction = Math.random() * Math.PI * 2;
    }
  }

  // Movement logic
  const cageRadius = 4.2;

  if (h.state === 'WALK') {
    // Gentle direction wobble
    h.direction += (Math.random() - 0.5) * 0.8 * dt;
    const vx = Math.cos(h.direction) * h.speed * dt;
    const vz = Math.sin(h.direction) * h.speed * dt;

    mesh.position.x += vx;
    mesh.position.z += vz;

    // Keep inside cage
    const dist = Math.sqrt(mesh.position.x ** 2 + mesh.position.z ** 2);
    if (dist > cageRadius) {
      h.direction = Math.atan2(-mesh.position.z, -mesh.position.x) + (Math.random() - 0.5) * 0.5;
      const norm = dist / cageRadius;
      mesh.position.x /= norm;
      mesh.position.z /= norm;
    }

    // Face direction of movement
    const targetRotY = -h.direction + Math.PI / 2;
    mesh.rotation.y += (targetRotY - mesh.rotation.y) * 3 * dt;

    // Bobbing walk animation
    const bob = Math.sin(time * 8 + h.bobPhase) * 0.04;
    mesh.position.y = 0.45 + bob;

  } else if (h.state === 'PAUSE') {
    // Idle sway
    mesh.position.y = 0.45 + Math.sin(time * 2 + h.bobPhase) * 0.02;
    mesh.rotation.y += Math.sin(time * 1.5 + h.bobPhase) * 0.3 * dt;

  } else if (h.state === 'WHEEL') {
    // Move toward wheel
    const wheelPos = new THREE.Vector3(3.5, 0.45, 0);
    const dirToWheel = wheelPos.clone().sub(mesh.position).normalize();
    mesh.position.x += dirToWheel.x * h.speed * 1.2 * dt;
    mesh.position.z += dirToWheel.z * h.speed * 1.2 * dt;

    // Face wheel
    const targetRotY = -Math.atan2(dirToWheel.z, dirToWheel.x) + Math.PI / 2;
    mesh.rotation.y += (targetRotY - mesh.rotation.y) * 4 * dt;

    // Running animation when close
    const distToWheel = mesh.position.distanceTo(wheelPos);
    if (distToWheel < 1.8) {
      wheelSpeed = Math.min(wheelSpeed + dt * 2, 4);
      const runBob = Math.sin(time * 12 + h.bobPhase) * 0.06;
      mesh.position.y = 0.45 + runBob;
      // Slight forward lean
      mesh.rotation.x = Math.sin(time * 12) * 0.1;
    }

  } else if (h.state === 'EAT') {
    // Move toward bowl
    const bowlPos = new THREE.Vector3(-2.5, 0.45, 1.5);
    const dirToBowl = bowlPos.clone().sub(mesh.position).normalize();
    mesh.position.x += dirToBowl.x * h.speed * dt;
    mesh.position.z += dirToBowl.z * h.speed * dt;

    // Face bowl
    const targetRotY = -Math.atan2(dirToBowl.z, dirToBowl.x) + Math.PI / 2;
    mesh.rotation.y += (targetRotY - mesh.rotation.y) * 4 * dt;

    // Eating animation - head bobbing
    const distToBowl = mesh.position.distanceTo(bowlPos);
    if (distToBowl < 1.2) {
      const eatBob = Math.sin(time * 6 + h.bobPhase) * 0.03;
      mesh.position.y = 0.45 + eatBob;
      mesh.rotation.x = Math.sin(time * 6) * 0.15;
    }
  }

  // Reset lean when walking/pausing
  if (h.state === 'WALK' || h.state === 'PAUSE') {
    mesh.rotation.x *= 0.95;
  }
}

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;

  // Update hamsters
  hamsters.forEach(h => updateHamster(h, dt, time));

  // Wheel rotation (decays when no hamster running)
  wheelGroup.rotation.x += wheelSpeed * dt;
  wheelSpeed *= 0.97; // Decay

  // Gentle ambient light flicker
  rimLight.intensity = 0.4 + Math.sin(time * 0.5) * 0.1;

  // FPS counter
  frameCount++;
  const now = performance.now();
  if (now - lastTime > 500) {
    const fps = Math.round(frameCount / ((now - lastTime) / 1000));
    statsEl.textContent = `${fps} FPS • ${hamsters.length} hamsters`;
    frameCount = 0;
    lastTime = now;
  }

  controls.update();
  renderer.render(scene, camera);
}

animate();

// ─── Resize Handler ────────────────────────────────────────────
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

## What's Inside 🐹

| Element | Details |
|---------|---------|
| **Cage** | Wire-frame cylinder with 24 vertical bars + 6 horizontal rings + domed top |
| **Floor** | 12-sided tray covered in scattered "wood shaving" bedding chunks |
| **5 Hamsters** | Low-poly (icosahedron detail-1) bodies, puffy cheeks, tiny ears, black bead eyes with shine highlights, stubby feet |
| **Running Wheel** | Torus + spokes on a stand — spins when a hamster approaches it |
| **Food Bowl** | Green bowl with dodecahedron pellets; one hamster walks over to eat |
| **Tunnel** | Yellow tube with decorative rings |
| **House** | Small box house with a pyramid roof and door |
| **Water Bottle** | Translucent cylinder hanging from the cage wall |

### Behavior System
Each hamster runs a simple state machine:
- **WALK** → wander with gentle direction wobble, bobbing gait
- **PAUSE** → idle sway in place
- **WHEEL** → pathfind to wheel, trigger spin + running animation
- **EAT** → pathfind to bowl, head-bob eating animation

Drag to orbit, scroll to zoom. The wheel spins faster the longer a hamster runs on it, then decays when they leave.