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
  #ui h1 { font-size: 22px; margin-bottom: 4px; text-shadow: 0 2px 8px rgba(0,0,0,0.5); }
  #ui p { font-size: 13px; opacity: 0.7; }
  #info {
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    color: #fff; font-size: 13px; opacity: 0.6; pointer-events: none;
    text-align: center;
  }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate · Scroll to zoom</p>
</div>
<div id="info">Hamsters wander, pause, and run on the wheel!</div>

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

// ─── Scene Setup ───────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87CEEB);
scene.fog = new THREE.Fog(0x87CEEB, 30, 60);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(8, 7, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI / 2.1;
controls.minDistance = 5;
controls.maxDistance = 25;

// ─── Lights ────────────────────────────────────────────────
const ambientLight = new THREE.AmbientLight(0xfff0e0, 0.6);
scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(0xffeedd, 1.2);
sunLight.position.set(8, 12, 6);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -12;
sunLight.shadow.camera.right = 12;
sunLight.shadow.camera.top = 12;
sunLight.shadow.camera.bottom = -12;
scene.add(sunLight);

const fillLight = new THREE.DirectionalLight(0xaaccff, 0.4);
fillLight.position.set(-6, 8, -4);
scene.add(fillLight);

// ─── Ground ────────────────────────────────────────────────
const groundGeo = new THREE.PlaneGeometry(40, 40);
const groundMat = new THREE.MeshLambertMaterial({ color: 0x7ec850 });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

// ─── Cage ──────────────────────────────────────────────────
const cageGroup = new THREE.Group();
const cageW = 7, cageH = 4, cageD = 5;
const barMat = new THREE.MeshPhongMaterial({ color: 0xcc4444, shininess: 60 });
const barGeo = new THREE.CylinderGeometry(0.04, 0.04, cageH, 6);

// Vertical bars
for (let i = 0; i <= 14; i++) {
  const x = -cageW / 2 + (cageW / 14) * i;
  for (const z of [-cageD / 2, cageD / 2]) {
    const bar = new THREE.Mesh(barGeo, barMat);
    bar.position.set(x, cageH / 2, z);
    bar.castShadow = true;
    cageGroup.add(bar);
  }
}
for (let i = 0; i <= 10; i++) {
  const z = -cageD / 2 + (cageD / 10) * i;
  for (const x of [-cageW / 2, cageW / 2]) {
    const bar = new THREE.Mesh(barGeo, barMat);
    bar.position.set(x, cageH / 2, z);
    bar.castShadow = true;
    cageGroup.add(bar);
  }
}

// Horizontal rails
const railMat = new THREE.MeshPhongMaterial({ color: 0xcc4444, shininess: 60 });
function addRail(x1, z1, x2, z2, y) {
  const dx = x2 - x1, dz = z2 - z1;
  const len = Math.sqrt(dx * dx + dz * dz);
  const geo = new THREE.CylinderGeometry(0.05, 0.05, len, 6);
  const rail = new THREE.Mesh(geo, railMat);
  rail.position.set((x1 + x2) / 2, y, (z1 + z2) / 2);
  rail.rotation.z = Math.PI / 2;
  rail.rotation.y = Math.atan2(dz, dx);
  rail.castShadow = true;
  cageGroup.add(rail);
}
for (const y of [0.05, cageH]) {
  addRail(-cageW/2, -cageD/2, cageW/2, -cageD/2, y);
  addRail(-cageW/2, cageD/2, cageW/2, cageD/2, y);
  addRail(-cageW/2, -cageD/2, -cageW/2, cageD/2, y);
  addRail(cageW/2, -cageD/2, cageW/2, cageD/2, y);
}

// Cage tray / floor
const trayGeo = new THREE.BoxGeometry(cageW + 0.3, 0.15, cageD + 0.3);
const trayMat = new THREE.MeshPhongMaterial({ color: 0xf5e6c8 });
const tray = new THREE.Mesh(trayGeo, trayMat);
tray.position.y = 0.075;
tray.receiveShadow = true;
tray.castShadow = true;
cageGroup.add(tray);

// Bedding (small scattered cubes)
const beddingMat = new THREE.MeshLambertMaterial({ color: 0xf0d9a0 });
for (let i = 0; i < 60; i++) {
  const s = 0.08 + Math.random() * 0.12;
  const bg = new THREE.BoxGeometry(s, s * 0.4, s);
  const bm = new THREE.Mesh(bg, beddingMat);
  bm.position.set(
    (Math.random() - 0.5) * (cageW - 0.5),
    0.15 + s * 0.2,
    (Math.random() - 0.5) * (cageD - 0.5)
  );
  bm.rotation.y = Math.random() * Math.PI;
  bm.castShadow = true;
  cageGroup.add(bm);
}

scene.add(cageGroup);

// ─── Hamster Wheel ─────────────────────────────────────────
const wheelGroup = new THREE.Group();
wheelGroup.position.set(2.5, 1.2, 0);

// Wheel ring
const wheelRingGeo = new THREE.TorusGeometry(1.0, 0.08, 8, 24);
const wheelRingMat = new THREE.MeshPhongMaterial({ color: 0xff6b9d, shininess: 80 });
const wheelRing = new THREE.Mesh(wheelRingGeo, wheelRingMat);
wheelRing.castShadow = true;
wheelGroup.add(wheelRing);

// Wheel spokes
const spokeMat = new THREE.MeshPhongMaterial({ color: 0xff6b9d });
for (let i = 0; i < 8; i++) {
  const angle = (i / 8) * Math.PI * 2;
  const spokeGeo = new THREE.CylinderGeometry(0.03, 0.03, 1.0, 4);
  const spoke = new THREE.Mesh(spokeGeo, spokeMat);
  spoke.position.set(Math.cos(angle) * 0.5, Math.sin(angle) * 0.5, 0);
  spoke.rotation.z = angle + Math.PI / 2;
  spoke.castShadow = true;
  wheelGroup.add(spoke);
}

// Wheel stand
const standMat = new THREE.MeshPhongMaterial({ color: 0x888888 });
const standGeo = new THREE.CylinderGeometry(0.06, 0.06, 1.2, 6);
const stand1 = new THREE.Mesh(standGeo, standMat);
stand1.position.set(0, -0.6, 0.5);
stand1.castShadow = true;
wheelGroup.add(stand1);
const stand2 = new THREE.Mesh(standGeo, standMat);
stand2.position.set(0, -0.6, -0.5);
stand2.castShadow = true;
wheelGroup.add(stand2);

// Axle
const axleGeo = new THREE.CylinderGeometry(0.04, 0.04, 1.2, 6);
const axle = new THREE.Mesh(axleGeo, standMat);
axle.rotation.x = Math.PI / 2;
axle.castShadow = true;
wheelGroup.add(axle);

scene.add(wheelGroup);

// ─── Food Bowl ─────────────────────────────────────────────
const bowlGroup = new THREE.Group();
bowlGroup.position.set(-2.5, 0.15, 1.2);

const bowlGeo = new THREE.CylinderGeometry(0.45, 0.3, 0.3, 8);
const bowlMat = new THREE.MeshPhongMaterial({ color: 0x4ecdc4, shininess: 60 });
const bowl = new THREE.Mesh(bowlGeo, bowlMat);
bowl.position.y = 0.15;
bowl.castShadow = true;
bowlGroup.add(bowl);

// Food pellets
const pelletMat = new THREE.MeshLambertMaterial({ color: 0xd4a056 });
for (let i = 0; i < 8; i++) {
  const pg = new THREE.SphereGeometry(0.06, 4, 4);
  const pm = new THREE.Mesh(pg, pelletMat);
  const a = Math.random() * Math.PI * 2;
  const r = Math.random() * 0.25;
  pm.position.set(Math.cos(a) * r, 0.32, Math.sin(a) * r);
  pm.castShadow = true;
  bowlGroup.add(pm);
}
scene.add(bowlGroup);

// ─── Tunnel ────────────────────────────────────────────────
const tunnelGroup = new THREE.Group();
tunnelGroup.position.set(-1.5, 0.5, -1.5);
tunnelGroup.rotation.y = 0.4;

const tunnelGeo = new THREE.CylinderGeometry(0.5, 0.5, 2.0, 8, 1, true);
const tunnelMat = new THREE.MeshPhongMaterial({ color: 0xffb347, side: THREE.DoubleSide, shininess: 40 });
const tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
tunnel.rotation.z = Math.PI / 2;
tunnel.castShadow = true;
tunnelGroup.add(tunnel);
scene.add(tunnelGroup);

// ─── Hamster Builder ───────────────────────────────────────
function createHamster(color, name) {
  const group = new THREE.Group();
  group.name = name;

  const bodyMat = new THREE.MeshPhongMaterial({ color, shininess: 30 });
  const bellyMat = new THREE.MeshPhongMaterial({ color: 0xfff5e6, shininess: 30 });
  const darkMat = new THREE.MeshPhongMaterial({ color: 0x222222 });
  const pinkMat = new THREE.MeshPhongMaterial({ color: 0xffaaaa });

  // Body
  const bodyGeo = new THREE.SphereGeometry(0.35, 8, 6);
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.scale.set(1, 0.85, 1.2);
  body.position.y = 0.35;
  body.castShadow = true;
  group.add(body);

  // Belly
  const bellyGeo = new THREE.SphereGeometry(0.28, 8, 6);
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.scale.set(1, 0.7, 1.1);
  belly.position.set(0, 0.28, 0.08);
  group.add(belly);

  // Head
  const headGeo = new THREE.SphereGeometry(0.22, 8, 6);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.position.set(0, 0.45, 0.35);
  head.castShadow = true;
  group.add(head);

  // Cheeks
  const cheekGeo = new THREE.SphereGeometry(0.1, 6, 5);
  const cheekL = new THREE.Mesh(cheekGeo, bodyMat);
  cheekL.position.set(-0.15, 0.38, 0.45);
  group.add(cheekL);
  const cheekR = new THREE.Mesh(cheekGeo, bodyMat);
  cheekR.position.set(0.15, 0.38, 0.45);
  group.add(cheekR);

  // Ears
  const earGeo = new THREE.SphereGeometry(0.08, 6, 5);
  const earL = new THREE.Mesh(earGeo, pinkMat);
  earL.position.set(-0.15, 0.62, 0.25);
  earL.scale.set(1, 1.3, 0.6);
  group.add(earL);
  const earR = new THREE.Mesh(earGeo, pinkMat);
  earR.position.set(0.15, 0.62, 0.25);
  earR.scale.set(1, 1.3, 0.6);
  group.add(earR);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.04, 6, 5);
  const eyeL = new THREE.Mesh(eyeGeo, darkMat);
  eyeL.position.set(-0.1, 0.48, 0.52);
  group.add(eyeL);
  const eyeR = new THREE.Mesh(eyeGeo, darkMat);
  eyeR.position.set(0.1, 0.48, 0.52);
  group.add(eyeR);

  // Eye shine
  const shineGeo = new THREE.SphereGeometry(0.015, 4, 4);
  const shineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const shineL = new THREE.Mesh(shineGeo, shineMat);
  shineL.position.set(-0.08, 0.50, 0.55);
  group.add(shineL);
  const shineR = new THREE.Mesh(shineGeo, shineMat);
  shineR.position.set(0.12, 0.50, 0.55);
  group.add(shineR);

  // Nose
  const noseGeo = new THREE.SphereGeometry(0.03, 5, 4);
  const nose = new THREE.Mesh(noseGeo, pinkMat);
  nose.position.set(0, 0.42, 0.56);
  group.add(nose);

  // Legs
  const legGeo = new THREE.CylinderGeometry(0.04, 0.05, 0.15, 5);
  const legMat = new THREE.MeshPhongMaterial({ color: 0xdd8866 });
  const legPositions = [
    [-0.18, 0.08, 0.15], [0.18, 0.08, 0.15],
    [-0.18, 0.08, -0.2], [0.18, 0.08, -0.2]
  ];
  const legs = [];
  for (const pos of legPositions) {
    const leg = new THREE.Mesh(legGeo, legMat);
    leg.position.set(...pos);
    leg.castShadow = true;
    group.add(leg);
    legs.push(leg);
  }

  // Tail
  const tailGeo = new THREE.SphereGeometry(0.06, 5, 4);
  const tail = new THREE.Mesh(tailGeo, bodyMat);
  tail.position.set(0, 0.3, -0.42);
  tail.scale.set(1, 1, 1.5);
  group.add(tail);

  group.userData = {
    legs,
    state: 'WANDER',
    timer: 0,
    targetTimer: 1 + Math.random() * 2,
    direction: Math.random() * Math.PI * 2,
    speed: 0.6 + Math.random() * 0.4,
    bobPhase: Math.random() * Math.PI * 2,
    wheelTimer: 0,
    wheelTarget: 0,
    name
  };

  return group;
}

// ─── Create Hamsters ───────────────────────────────────────
const hamsters = [];
const hamsterConfigs = [
  { color: 0xf4a460, name: 'Biscuit' },
  { color: 0x888888, name: 'Shadow' },
  { color: 0xffcc44, name: 'Sunny' },
  { color: 0xcc6699, name: 'Berry' },
];

for (const cfg of hamsterConfigs) {
  const h = createHamster(cfg.color, cfg.name);
  h.position.set(
    (Math.random() - 0.5) * 4,
    0.15,
    (Math.random() - 0.5) * 3
  );
  h.rotation.y = Math.random() * Math.PI * 2;
  scene.add(h);
  hamsters.push(h);
}

// ─── Behavior Update ───────────────────────────────────────
const WHEEL_POS = new THREE.Vector3(2.5, 0.15, 0);
const BOWL_POS = new THREE.Vector3(-2.5, 0.15, 1.2);
const CAGE_BOUNDS = { x: cageW / 2 - 0.5, z: cageD / 2 - 0.5 };

function updateHamster(h, dt, time) {
  const d = h.userData;
  d.timer += dt;

  // State machine
  if (d.state === 'WANDER') {
    // Move forward
    const vx = Math.cos(d.direction) * d.speed * dt;
    const vz = Math.sin(d.direction) * d.speed * dt;
    h.position.x += vx;
    h.position.z += vz;

    // Face direction
    h.rotation.y = -d.direction + Math.PI / 2;

    // Leg animation
    for (let i = 0; i < d.legs.length; i++) {
      d.legs[i].rotation.x = Math.sin(time * 8 + d.bobPhase + i * Math.PI / 2) * 0.3;
    }

    // Body bob
    h.position.y = 0.15 + Math.sin(time * 6 + d.bobPhase) * 0.02;

    // Check bounds
    if (Math.abs(h.position.x) > CAGE_BOUNDS.x || Math.abs(h.position.z) > CAGE_BOUNDS.z) {
      d.direction += Math.PI + (Math.random() - 0.5) * 1.5;
      h.position.x = THREE.MathUtils.clamp(h.position.x, -CAGE_BOUNDS.x, CAGE_BOUNDS.x);
      h.position.z = THREE.MathUtils.clamp(h.position.z, -CAGE_BOUNDS.z, CAGE_BOUNDS.z);
    }

    // Chance to go to wheel
    const distToWheel = h.position.distanceTo(WHEEL_POS);
    if (distToWheel < 2.5 && Math.random() < 0.003) {
      d.state = 'GO_WHEEL';
      d.wheelTarget = 3 + Math.random() * 4;
      d.wheelTimer = 0;
    }

    // Chance to go to bowl
    const distToBowl = h.position.distanceTo(BOWL_POS);
    if (distToBowl < 2.5 && Math.random() < 0.002) {
      d.state = 'GO_BOWL';
      d.targetTimer = 2 + Math.random() * 3;
      d.timer = 0;
    }

    // Random pause
    if (d.timer > d.targetTimer) {
      d.state = 'PAUSE';
      d.timer = 0;
      d.targetTimer = 0.5 + Math.random() * 2;
    }

  } else if (d.state === 'PAUSE') {
    // Idle wiggle
    h.rotation.y += Math.sin(time * 2 + d.bobPhase) * 0.005;
    for (const leg of d.legs) leg.rotation.x *= 0.9;
    h.position.y = 0.15;

    if (d.timer > d.targetTimer) {
      d.state = 'TURN';
      d.timer = 0;
      d.targetTimer = 0.3 + Math.random() * 0.5;
    }

  } else if (d.state === 'TURN') {
    d.direction += (Math.random() - 0.5) * 2.5;
    h.rotation.y = -d.direction + Math.PI / 2;
    if (d.timer > d.targetTimer) {
      d.state = 'WANDER';
      d.timer = 0;
      d.targetTimer = 1 + Math.random() * 3;
    }

  } else if (d.state === 'GO_WHEEL') {
    // Walk toward wheel
    const dir = WHEEL_POS.clone().sub(h.position);
    const dist = dir.length();
    dir.normalize();
    h.position.x += dir.x * d.speed * dt;
    h.position.z += dir.z * d.speed * dt;
    h.rotation.y = Math.atan2(-dir.z, dir.x) + Math.PI / 2;

    for (let i = 0; i < d.legs.length; i++) {
      d.legs[i].rotation.x = Math.sin(time * 10 + d.bobPhase + i * Math.PI / 2) * 0.4;
    }
    h.position.y = 0.15 + Math.sin(time * 8 + d.bobPhase) * 0.02;

    if (dist < 0.8) {
      d.state = 'RUN_WHEEL';
      d.timer = 0;
    }

  } else if (d.state === 'RUN_WHEEL') {
    // Sit on wheel and run
    h.position.lerp(WHEEL_POS, dt * 3);
    h.position.y = 0.15;
    h.rotation.y = Math.PI / 2;

    // Fast leg animation
    for (let i = 0; i < d.legs.length; i++) {
      d.legs[i].rotation.x = Math.sin(time * 18 + d.bobPhase + i * Math.PI / 2) * 0.6;
    }

    d.wheelTimer += dt;
    if (d.wheelTimer > d.wheelTarget) {
      d.state = 'WANDER';
      d.timer = 0;
      d.targetTimer = 1 + Math.random() * 2;
      d.direction = Math.random() * Math.PI * 2;
    }

  } else if (d.state === 'GO_BOWL') {
    const dir = BOWL_POS.clone().sub(h.position);
    const dist = dir.length();
    dir.normalize();
    h.position.x += dir.x * d.speed * dt;
    h.position.z += dir.z * d.speed * dt;
    h.rotation.y = Math.atan2(-dir.z, dir.x) + Math.PI / 2;

    for (let i = 0; i < d.legs.length; i++) {
      d.legs[i].rotation.x = Math.sin(time * 8 + d.bobPhase + i * Math.PI / 2) * 0.3;
    }

    if (dist < 0.6) {
      d.state = 'EAT';
      d.timer = 0;
      d.targetTimer = 2 + Math.random() * 3;
    }

  } else if (d.state === 'EAT') {
    h.position.y = 0.15;
    // Head bobbing (eating animation)
    const headBob = Math.sin(time * 10) * 0.03;
    h.position.y = 0.15 + headBob;
    for (const leg of d.legs) leg.rotation.x = 0;

    if (d.timer > d.targetTimer) {
      d.state = 'WANDER';
      d.timer = 0;
      d.targetTimer = 1 + Math.random() * 3;
      d.direction = Math.random() * Math.PI * 2;
    }
  }
}

// ─── Wheel Rotation ────────────────────────────────────────
let wheelAngle = 0;
function updateWheel(dt) {
  let anyRunning = false;
  for (const h of hamsters) {
    if (h.userData.state === 'RUN_WHEEL') {
      anyRunning = true;
      break;
    }
  }
  if (anyRunning) {
    wheelAngle += dt * 4;
  } else {
    // Slow decay
    wheelAngle += dt * 0.1;
  }
  wheelRing.rotation.z = wheelAngle;
  for (const child of wheelGroup.children) {
    if (child !== wheelRing && child !== axle && child !== stand1 && child !== stand2) {
      // spokes rotate with wheel
    }
  }
  // Rotate spokes
  const spokes = wheelGroup.children.filter(c => c.geometry && c.geometry.type === 'CylinderGeometry' && c !== axle && c !== stand1 && c !== stand2);
  // Actually let's just rotate the whole inner group
  // Simpler: rotate spokes individually
  let spokeIdx = 0;
  for (const child of wheelGroup.children) {
    if (child.geometry && child.geometry.type === 'CylinderGeometry' && child.geometry.parameters && child.geometry.parameters.height === 1.0) {
      const baseAngle = (spokeIdx / 8) * Math.PI * 2;
      const a = baseAngle + wheelAngle;
      child.position.set(Math.cos(a) * 0.5, Math.sin(a) * 0.5, 0);
      child.rotation.z = a + Math.PI / 2;
      spokeIdx++;
    }
  }
}

// ─── Decorative Elements ───────────────────────────────────
// Small water bottle
const bottleGroup = new THREE.Group();
bottleGroup.position.set(3.2, 2.5, -1.5);
const bottleGeo = new THREE.CylinderGeometry(0.15, 0.15, 0.6, 8);
const bottleMat = new THREE.MeshPhongMaterial({ color: 0x88ccff, transparent: true, opacity: 0.7 });
const bottle = new THREE.Mesh(bottleGeo, bottleMat);
bottleGroup.add(bottle);
const spoutGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.3, 5);
const spoutMat = new THREE.MeshPhongMaterial({ color: 0xaaaaaa });
const spout = new THREE.Mesh(spoutGeo, spoutMat);
spout.position.y = -0.45;
bottleGroup.add(spout);
scene.add(bottleGroup);

// Small exercise ball
const ballGeo = new THREE.SphereGeometry(0.4, 8, 6);
const ballMat = new THREE.MeshPhongMaterial({ color: 0xff6b6b, transparent: true, opacity: 0.5, shininess: 100 });
const exerciseBall = new THREE.Mesh(ballGeo, ballMat);
exerciseBall.position.set(-3, 0.55, -1.8);
exerciseBall.castShadow = true;
scene.add(exerciseBall);

// ─── Animation Loop ────────────────────────────────────────
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;

  for (const h of hamsters) {
    updateHamster(h, dt, time);
  }

  updateWheel(dt);

  // Gentle exercise ball wobble
  exerciseBall.position.y = 0.55 + Math.sin(time * 1.5) * 0.03;
  exerciseBall.rotation.y = time * 0.3;

  controls.update();
  renderer.render(scene, camera);
}

animate();

// ─── Resize ────────────────────────────────────────────────
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## What's Inside

| Element | Details |
|---|---|
| **Cage** | Red wireframe bars (vertical + horizontal rails) with a cream-colored tray and scattered bedding cubes |
| **4 Hamsters** | Biscuit (orange), Shadow (gray), Sunny (yellow), Berry (pink) — each built from spheres, cylinders, and cones with eyes, cheeks, ears, nose, legs, and a tail |
| **Hamster Wheel** | Pink torus ring with 8 spokes on a metal stand — **spins fast** when a hamster is running on it |
| **Food Bowl** | Teal bowl with brown pellets — hamsters walk to it and "eat" (head-bob animation) |
| **Tunnel** | Orange open cylinder hamsters can wander near |
| **Water Bottle** | Translucent blue cylinder with a metal spout |
| **Exercise Ball** | Semi-transparent red sphere that gently wobbles |

### Behavior State Machine (per hamster)
```
WANDER → PAUSE → TURN → WANDER
   ↓                    ↑
GO_WHEEL → RUN_WHEEL ──┘
   ↓
GO_BOWL → EAT ─────────┘
```

Each hamster independently wanders, pauses, turns, occasionally walks to the wheel to run (spinning it), or walks to the bowl to eat. Legs animate with sine-wave stepping, bodies bob while walking, and everything stays clamped inside the cage bounds.