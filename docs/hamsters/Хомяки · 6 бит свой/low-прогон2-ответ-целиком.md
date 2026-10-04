

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
  position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
  color: #fff; background: rgba(0,0,0,0.5); padding: 10px 24px;
  border-radius: 20px; font-size: 14px; pointer-events: none;
  backdrop-filter: blur(4px);
}
#info span { color: #ffb347; font-weight: bold; }
</style>
</head>
<body>
<div id="info">🐹 <span>Low-Poly Hamster Playground</span> — Drag to rotate, scroll to zoom</div>

<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// --- SCENE SETUP ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 15, 30);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(5, 4, 6);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI / 2.1;
controls.minDistance = 3;
controls.maxDistance = 15;
controls.target.set(0, 1, 0);

// --- LIGHTS ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xfff5e6, 1.2);
dirLight.position.set(5, 8, 3);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(1024, 1024);
dirLight.shadow.camera.left = -5;
dirLight.shadow.camera.right = 5;
dirLight.shadow.camera.top = 5;
dirLight.shadow.camera.bottom = -5;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight(0xb3d9ff, 0.3);
fillLight.position.set(-3, 4, -2);
scene.add(fillLight);

// --- MATERIALS HELPER ---
function mat(color, flat = true) {
  return new THREE.MeshStandardMaterial({ color, flatShading: flat, roughness: 0.8, metalness: 0.05 });
}

// --- FLOOR / TRAY ---
const trayGroup = new THREE.Group();

// Base tray
const trayGeo = new THREE.BoxGeometry(6, 0.3, 5);
const trayMesh = new THREE.Mesh(trayGeo, mat(0x8b5e3c));
trayMesh.position.y = -0.15;
trayMesh.receiveShadow = true;
trayGroup.add(trayMesh);

// Floor (wood shavings color)
const floorGeo = new THREE.BoxGeometry(5.8, 0.1, 4.8);
const floorMesh = new THREE.Mesh(floorGeo, mat(0xf5deb3));
floorMesh.position.y = 0.05;
floorMesh.receiveShadow = true;
trayGroup.add(floorMesh);

// Some scattered "shaving" bits
for (let i = 0; i < 20; i++) {
  const bitGeo = new THREE.BoxGeometry(0.15, 0.03, 0.05);
  const bit = new THREE.Mesh(bitGeo, mat(0xe8c170));
  bit.position.set((Math.random() - 0.5) * 5, 0.11, (Math.random() - 0.5) * 4);
  bit.rotation.y = Math.random() * Math.PI;
  trayGroup.add(bit);
}

scene.add(trayGroup);

// --- CAGE (WIRE FRAME) ---
const cageGroup = new THREE.Group();
const wireMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, roughness: 0.4, metalness: 0.6 });
const wireRadius = 0.02;

function makeWire(x1, y1, z1, x2, y2, z2) {
  const dir = new THREE.Vector3(x2 - x1, y2 - y1, z2 - z1);
  const len = dir.length();
  const geo = new THREE.CylinderGeometry(wireRadius, wireRadius, len, 5);
  const mesh = new THREE.Mesh(geo, wireMat);
  mesh.position.set((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  return mesh;
}

const cageH = 2.5;
const cageW = 5.5;
const cageD = 4.5;
const cx = 0, cz = 0, cy = 0.1;

// Vertical posts at corners
[[-cageW/2, -cageD/2], [cageW/2, -cageD/2], [-cageW/2, cageD/2], [cageW/2, cageD/2]].forEach(([x, z]) => {
  cageGroup.add(makeWire(x, cy, z, x, cy + cageH, z));
});

// Horizontal rails - top
cageGroup.add(makeWire(-cageW/2, cy + cageH, -cageD/2, cageW/2, cy + cageH, -cageD/2));
cageGroup.add(makeWire(-cageW/2, cy + cageH, cageD/2, cageW/2, cy + cageH, cageD/2));
cageGroup.add(makeWire(-cageW/2, cy + cageH, -cageD/2, -cageW/2, cy + cageH, cageD/2));
cageGroup.add(makeWire(cageW/2, cy + cageH, -cageD/2, cageW/2, cy + cageH, cageD/2));

// Middle rails
cageGroup.add(makeWire(-cageW/2, cy + cageH * 0.5, -cageD/2, cageW/2, cy + cageH * 0.5, -cageD/2));
cageGroup.add(makeWire(-cageW/2, cy + cageH * 0.5, cageD/2, cageW/2, cy + cageH * 0.5, cageD/2));
cageGroup.add(makeWire(-cageW/2, cy + cageH * 0.5, -cageD/2, -cageW/2, cy + cageH * 0.5, cageD/2));
cageGroup.add(makeWire(cageW/2, cy + cageH * 0.5, -cageD/2, cageW/2, cy + cageH * 0.5, cageD/2));

// Side vertical wires
for (let i = 1; i < 5; i++) {
  const x = -cageW/2 + (cageW / 5) * i;
  cageGroup.add(makeWire(x, cy, -cageD/2, x, cy + cageH, -cageD/2));
  cageGroup.add(makeWire(x, cy, cageD/2, x, cy + cageH, cageD/2));
}
for (let i = 1; i < 4; i++) {
  const z = -cageD/2 + (cageD / 4) * i;
  cageGroup.add(makeWire(-cageW/2, cy, z, -cageW/2, cy + cageH, z));
  cageGroup.add(makeWire(cageW/2, cy, z, cageW/2, cy + cageH, z));
}

scene.add(cageGroup);

// --- RUNNING WHEEL ---
const wheelGroup = new THREE.Group();
wheelGroup.position.set(-2, 0, -1.5);

// Wheel rim
const rimGeo = new THREE.TorusGeometry(0.6, 0.05, 6, 16);
const rimMesh = new THREE.Mesh(rimGeo, mat(0xff6b6b));
rimMesh.castShadow = true;
wheelGroup.add(rimMesh);

// Spokes
for (let i = 0; i < 6; i++) {
  const angle = (i / 6) * Math.PI * 2;
  const spokeGeo = new THREE.CylinderGeometry(0.02, 0.02, 1.1, 4);
  const spoke = new THREE.Mesh(spokeGeo, mat(0xff6b6b));
  spoke.position.set(Math.cos(angle) * 0.55, Math.sin(angle) * 0.55, 0);
  spoke.rotation.z = angle - Math.PI / 2;
  wheelGroup.add(spoke);
}

// Hub
const hubGeo = new THREE.SphereGeometry(0.08, 6, 4);
const hubMesh = new THREE.Mesh(hubGeo, mat(0xff9f43));
wheelGroup.add(hubMesh);

// Stand
const standGeo = new THREE.CylinderGeometry(0.04, 0.06, 0.5, 5);
const standL = new THREE.Mesh(standGeo, mat(0x555555));
standL.position.set(0, -0.85, -0.15);
wheelGroup.add(standL);
const standR = standL.clone();
standR.position.z = 0.15;
wheelGroup.add(standR);

// Stand base
const baseGeo = new THREE.BoxGeometry(0.5, 0.05, 0.5);
const baseMesh = new THREE.Mesh(baseGeo, mat(0x555555));
baseMesh.position.y = -1.1;
wheelGroup.add(baseMesh);

// Position wheel so it sits on floor
wheelGroup.position.y = 0.7;
scene.add(wheelGroup);

// --- FOOD BOWL ---
const bowlGroup = new THREE.Group();
bowlGroup.position.set(1.8, 0, 1.5);

const bowlGeo = new THREE.CylinderGeometry(0.3, 0.2, 0.15, 8);
const bowlMesh = new THREE.Mesh(bowlGeo, mat(0x4ecdc4));
bowlMesh.position.y = 0.075;
bowlMesh.castShadow = true;
bowlGroup.add(bowlMesh);

// Food pellets
for (let i = 0; i < 5; i++) {
  const pelletGeo = new THREE.SphereGeometry(0.04, 5, 4);
  const pellet = new THREE.Mesh(pelletGeo, mat(0xd4a03c));
  const a = (i / 5) * Math.PI * 2;
  pellet.position.set(Math.cos(a) * 0.12, 0.15, Math.sin(a) * 0.12);
  bowlGroup.add(pellet);
}
scene.add(bowlGroup);

// --- TUNNEL ---
const tunnelGroup = new THREE.Group();
tunnelGroup.position.set(0.5, 0, -1.5);
tunnelGroup.rotation.y = 0.3;

const tunnelGeo = new THREE.CylinderGeometry(0.25, 0.25, 1.2, 8, 1, false, 0, Math.PI);
const tunnelMesh = new THREE.Mesh(tunnelGeo, mat(0xa29bfe));
tunnelMesh.rotation.z = Math.PI / 2;
tunnelMesh.position.y = 0.25;
tunnelMesh.castShadow = true;
tunnelGroup.add(tunnelMesh);

// Tunnel ends (rings)
const ringGeo = new THREE.TorusGeometry(0.25, 0.03, 5, 8, Math.PI);
const ringL = new THREE.Mesh(ringGeo, mat(0x6c5ce7));
ringL.position.set(-0.6, 0.25, 0);
ringL.rotation.z = Math.PI / 2;
tunnelGroup.add(ringL);
const ringR = new THREE.Mesh(ringGeo, mat(0x6c5ce7));
ringR.position.set(0.6, 0.25, 0);
ringR.rotation.z = -Math.PI / 2;
tunnelGroup.add(ringR);

scene.add(tunnelGroup);

// --- HIDEOUT HOUSE ---
const houseGroup = new THREE.Group();
houseGroup.position.set(2, 0, -1.2);

const houseBody = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.5, 0.6), mat(0xfd79a8));
houseBody.position.y = 0.25;
houseBody.castShadow = true;
houseGroup.add(houseBody);

const roofGeo = new THREE.ConeGeometry(0.55, 0.3, 4);
const roofMesh = new THREE.Mesh(roofGeo, mat(0xe84393));
roofMesh.position.y = 0.65;
roofMesh.rotation.y = Math.PI / 4;
roofMesh.castShadow = true;
houseGroup.add(roofMesh);

// Door
const doorGeo = new THREE.CircleGeometry(0.12, 6, 0, Math.PI);
const doorMesh = new THREE.Mesh(doorGeo, mat(0x2d3436));
doorMesh.position.set(0, 0.15, 0.31);
houseGroup.add(doorMesh);

scene.add(houseGroup);

// --- HAMSTER FACTORY ---
const hamsterColors = [
  { body: 0xf39c12, belly: 0xfdebd0, ear: 0xe67e22 },
  { body: 0xecf0f1, belly: 0xffffff, ear: 0xbdc3c7 },
  { body: 0xd35400, belly: 0xf5cba7, ear: 0xae4a00 },
  { body: 0xfab1a0, belly: 0xfff5ee, ear: 0xe17055 },
];

function createHamster(colorSet, scale = 1) {
  const group = new THREE.Group();

  // Body
  const bodyGeo = new THREE.SphereGeometry(0.22, 7, 5);
  const body = new THREE.Mesh(bodyGeo, mat(colorSet.body));
  body.scale.set(1, 0.85, 1.1);
  body.position.y = 0.2;
  body.castShadow = true;
  group.add(body);

  // Belly
  const bellyGeo = new THREE.SphereGeometry(0.15, 6, 4);
  const belly = new THREE.Mesh(bellyGeo, mat(colorSet.belly));
  belly.scale.set(0.9, 0.7, 0.8);
  belly.position.set(0, 0.15, 0.08);
  group.add(belly);

  // Head
  const headGeo = new THREE.SphereGeometry(0.15, 7, 5);
  const head = new THREE.Mesh(headGeo, mat(colorSet.body));
  head.position.set(0, 0.28, 0.2);
  head.castShadow = true;
  group.add(head);

  // Snout
  const snoutGeo = new THREE.SphereGeometry(0.06, 5, 4);
  const snout = new THREE.Mesh(snoutGeo, mat(colorSet.belly));
  snout.position.set(0, 0.24, 0.33);
  group.add(snout);

  // Nose
  const noseGeo = new THREE.SphereGeometry(0.025, 4, 3);
  const nose = new THREE.Mesh(noseGeo, mat(0xff6b81));
  nose.position.set(0, 0.25, 0.38);
  group.add(nose);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.03, 4, 3);
  const eyeMat = mat(0x2d3436);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(-0.07, 0.3, 0.3);
  group.add(eyeL);
  const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
  eyeR.position.set(0.07, 0.3, 0.3);
  group.add(eyeR);

  // Eye highlights
  const hlGeo = new THREE.SphereGeometry(0.012, 3, 2);
  const hlMat = mat(0xffffff);
  const hlL = new THREE.Mesh(hlGeo, hlMat);
  hlL.position.set(-0.06, 0.31, 0.32);
  group.add(hlL);
  const hlR = new THREE.Mesh(hlGeo, hlMat);
  hlR.position.set(0.08, 0.31, 0.32);
  group.add(hlR);

  // Ears
  const earGeo = new THREE.ConeGeometry(0.05, 0.08, 4);
  const earL = new THREE.Mesh(earGeo, mat(colorSet.ear));
  earL.position.set(-0.09, 0.4, 0.15);
  earL.rotation.z = 0.3;
  group.add(earL);
  const earR = new THREE.Mesh(earGeo, mat(colorSet.ear));
  earR.position.set(0.09, 0.4, 0.15);
  earR.rotation.z = -0.3;
  group.add(earR);

  // Inner ears
  const innerEarGeo = new THREE.ConeGeometry(0.03, 0.05, 4);
  const innerEarL = new THREE.Mesh(innerEarGeo, mat(0xffb8c6));
  innerEarL.position.set(-0.09, 0.39, 0.17);
  innerEarL.rotation.z = 0.3;
  group.add(innerEarL);
  const innerEarR = new THREE.Mesh(innerEarGeo, mat(0xffb8c6));
  innerEarR.position.set(0.09, 0.39, 0.17);
  innerEarR.rotation.z = -0.3;
  group.add(innerEarR);

  // Cheeks (fluffy balls)
  const cheekGeo = new THREE.SphereGeometry(0.06, 5, 4);
  const cheekL = new THREE.Mesh(cheekGeo, mat(colorSet.belly));
  cheekL.position.set(-0.12, 0.22, 0.25);
  group.add(cheekL);
  const cheekR = new THREE.Mesh(cheekGeo, mat(colorSet.belly));
  cheekR.position.set(0.12, 0.22, 0.25);
  group.add(cheekR);

  // Feet (tiny)
  const footGeo = new THREE.SphereGeometry(0.04, 4, 3);
  const footMat = mat(colorSet.ear);
  [[-0.08, 0.04, 0.15], [0.08, 0.04, 0.15], [-0.08, 0.04, -0.12], [0.08, 0.04, -0.12]].forEach(pos => {
    const foot = new THREE.Mesh(footGeo, footMat);
    foot.position.set(...pos);
    group.add(foot);
  });

  // Tiny tail
  const tailGeo = new THREE.SphereGeometry(0.03, 4, 3);
  const tail = new THREE.Mesh(tailGeo, mat(colorSet.body));
  tail.position.set(0, 0.2, -0.25);
  group.add(tail);

  group.scale.setScalar(scale);
  return group;
}

// --- HAMSTER AI ---
class Hamster {
  constructor(colorSet, startPos) {
    this.mesh = createHamster(colorSet, 0.8 + Math.random() * 0.3);
    this.mesh.position.copy(startPos);
    this.mesh.position.y = 0;
    scene.add(this.mesh);

    this.state = 'idle';
    this.target = new THREE.Vector3();
    this.speed = 0.3 + Math.random() * 0.3;
    this.timer = 0;
    this.idleTime = 1 + Math.random() * 3;
    this.walkTime = 2 + Math.random() * 4;
    this.bobPhase = Math.random() * Math.PI * 2;
    this.wheelAngle = 0;
    this.atWheel = false;
    this.pickingUpFood = false;
    this.foodInMouth = false;

    this.pickRandomTarget();
  }

  pickRandomTarget() {
    const x = (Math.random() - 0.5) * 4.5;
    const z = (Math.random() - 0.5) * 3.5;
    this.target.set(x, 0, z);
  }

  update(dt) {
    this.timer += dt;
    const pos = this.mesh.position;

    switch (this.state) {
      case 'idle':
        // Bob up and down slightly
        this.mesh.position.y = Math.sin(this.timer * 3 + this.bobPhase) * 0.01;
        // Random look around
        if (Math.random() < 0.02) {
          this.mesh.rotation.y += (Math.random() - 0.5) * 0.5;
        }
        if (this.timer > this.idleTime) {
          this.state = 'walking';
          this.timer = 0;
          this.walkTime = 2 + Math.random() * 4;
          this.pickRandomTarget();
        }
        break;

      case 'walking': {
        const dir = new THREE.Vector3().subVectors(this.target, pos);
        dir.y = 0;
        const dist = dir.length();

        if (dist < 0.2) {
          this.state = 'idle';
          this.timer = 0;
          this.idleTime = 1 + Math.random() * 3;
        } else {
          dir.normalize();
          // Smoothly face direction
          const targetAngle = Math.atan2(dir.x, dir.z);
          let angleDiff = targetAngle - this.mesh.rotation.y;
          while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
          while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
          this.mesh.rotation.y += angleDiff * Math.min(dt * 5, 1);

          // Move
          pos.addScaledVector(dir, this.speed * dt);

          // Bob while walking
          this.mesh.position.y = Math.abs(Math.sin(this.timer * 8 + this.bobPhase)) * 0.03;

          // Check if near wheel
          const wheelDist = pos.distanceTo(new THREE.Vector3(-2, 0, -1.5));
          if (wheelDist < 0.8 && !this.atWheel) {
            this.state = 'wheel';
            this.timer = 0;
            this.atWheel = true;
            this.wheelDuration = 2 + Math.random() * 3;
          }

          // Check if near food bowl
          const bowlDist = pos.distanceTo(new THREE.Vector3(1.8, 0, 1.5));
          if (bowlDist < 0.5 && !this.foodInMouth) {
            this.state = 'eating';
            this.timer = 0;
            this.eatDuration = 1.5 + Math.random() * 2;
          }

          if (this.timer > this.walkTime) {
            this.state = 'idle';
            this.timer = 0;
            this.idleTime = 1 + Math.random() * 2;
          }
        }
        break;
      }

      case 'wheel': {
        // Face the wheel
        const wheelPos = new THREE.Vector3(-2, 0, -1.5);
        const dir = new THREE.Vector3().subVectors(wheelPos, pos);
        const targetAngle = Math.atan2(dir.x, dir.z);
        let angleDiff = targetAngle - this.mesh.rotation.y;
        while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
        while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
        this.mesh.rotation.y += angleDiff * Math.min(dt * 5, 1);

        // Run in place (fast bob)
        this.mesh.position.y = Math.abs(Math.sin(this.timer * 15)) * 0.05;
        this.wheelAngle += dt * 8;

        if (this.timer > this.wheelDuration) {
          this.state = 'idle';
          this.timer = 0;
          this.atWheel = false;
          this.idleTime = 1 + Math.random() * 2;
        }
        break;
      }

      case 'eating': {
        // Face bowl
        const bowlPos = new THREE.Vector3(1.8, 0, 1.5);
        const dir = new THREE.Vector3().subVectors(bowlPos, pos);
        const targetAngle = Math.atan2(dir.x, dir.z);
        let angleDiff = targetAngle - this.mesh.rotation.y;
        while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
        while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
        this.mesh.rotation.y += angleDiff * Math.min(dt * 5, 1);

        // Nibble animation
        this.mesh.position.y = Math.abs(Math.sin(this.timer * 10)) * 0.02;
        this.mesh.rotation.x = Math.sin(this.timer * 10) * 0.1;

        if (this.timer > this.eatDuration) {
          this.state = 'idle';
          this.timer = 0;
          this.mesh.rotation.x = 0;
          this.idleTime = 1 + Math.random() * 3;
        }
        break;
      }
    }

    // Clamp to cage bounds
    pos.x = THREE.MathUtils.clamp(pos.x, -2.5, 2.5);
    pos.z = THREE.MathUtils.clamp(pos.z, -2, 2);
  }
}

// Create hamsters
const hamsters = [];
const startPositions = [
  new THREE.Vector3(-1, 0, 0.5),
  new THREE.Vector3(1, 0, -0.5),
  new THREE.Vector3(0, 0, 1),
  new THREE.Vector3(-0.5, 0, -1),
];

hamsterColors.forEach((colors, i) => {
  hamsters.push(new Hamster(colors, startPositions[i]));
});

// --- DECORATIVE PLANTS ---
function makePlant(x, z) {
  const g = new THREE.Group();
  const potGeo = new THREE.CylinderGeometry(0.12, 0.09, 0.15, 6);
  const pot = new THREE.Mesh(potGeo, mat(0xe17055));
  pot.position.y = 0.075;
  g.add(pot);

  for (let i = 0; i < 3; i++) {
    const leafGeo = new THREE.ConeGeometry(0.05, 0.2, 4);
    const leaf = new THREE.Mesh(leafGeo, mat(0x00b894));
    leaf.position.set((Math.random() - 0.5) * 0.08, 0.25, (Math.random() - 0.5) * 0.08);
    leaf.rotation.z = (Math.random() - 0.5) * 0.4;
    g.add(leaf);
  }

  g.position.set(x, 0, z);
  scene.add(g);
}
makePlant(-2.2, 1.5);
makePlant(2.3, 0.5);

// --- ANIMATION LOOP ---
const clock = new THREE.Clock();
let wheelSpinSpeed = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);

  // Update hamsters
  hamsters.forEach(h => h.update(dt));

  // Spin wheel if any hamster is on it
  let anyOnWheel = false;
  hamsters.forEach(h => {
    if (h.state === 'wheel') anyOnWheel = true;
  });

  if (anyOnWheel) {
    wheelSpinSpeed = THREE.MathUtils.lerp(wheelSpinSpeed, 6, dt * 3);
  } else {
    wheelSpinSpeed = THREE.MathUtils.lerp(wheelSpinSpeed, 0, dt * 2);
  }
  wheelGroup.rotation.z += wheelSpinSpeed * dt;

  // Gentle camera float
  controls.update();

  renderer.render(scene, camera);
}

animate();

// --- RESIZE ---
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

## What You Get

| Feature | Details |
|---------|---------|
| **4 Hamsters** | Each with unique colors, fluffy cheeks, tiny feet, and expressive eyes |
| **Running Wheel** | Spins smoothly when a hamster approaches and "runs" on it |
| **Food Bowl** | Hamsters walk over, nibble with a head-bob animation |
| **Tunnel & House** | Decorative low-poly props for visual interest |
| **Cage** | Wire-frame structure with corner posts and grid rails |
| **AI States** | `idle → walking → wheel/eating → idle` with smooth transitions |
| **Camera** | OrbitControls with damping, zoom limits, and polar angle clamp |
| **Visual Style** | Flat shading, warm palette, soft shadows, fog for depth |

Just save as `index.html` and open in any modern browser — no build step needed.