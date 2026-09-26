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
position: absolute; top: 20px; left: 20px;
color: #fff; background: rgba(0,0,0,0.5);
padding: 12px 18px; border-radius: 12px;
font-size: 14px; pointer-events: none;
backdrop-filter: blur(6px);
}
#ui h1 { font-size: 18px; margin-bottom: 4px; }
#ui p { opacity: 0.7; font-size: 12px; }
</style>
</head>
<body>
<div id="ui">
<h1>🐹 Hamster Playground</h1>
<p>Drag to rotate • Scroll to zoom</p>
</div>

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

// --- Scene Setup ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2d1b69);
scene.fog = new THREE.Fog(0x2d1b69, 20, 50);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(8, 7, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.target.set(0, 1.5, 0);
controls.maxPolarAngle = Math.PI / 2.1;

// --- Lighting ---
const ambient = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambient);

const dirLight = new THREE.DirectionalLight(0xfff5e6, 1.2);
dirLight.position.set(5, 10, 5);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(1024, 1024);
dirLight.shadow.camera.near = 0.5;
dirLight.shadow.camera.far = 30;
dirLight.shadow.camera.left = -10;
dirLight.shadow.camera.right = 10;
dirLight.shadow.camera.top = 10;
dirLight.shadow.camera.bottom = -10;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight(0x88ccff, 0.3);
fillLight.position.set(-3, 4, -5);
scene.add(fillLight);

const pointLight = new THREE.PointLight(0xff9966, 0.5, 15);
pointLight.position.set(0, 5, 0);
scene.add(pointLight);

// --- Materials ---
function mat(color, flat = true) {
  return new THREE.MeshLambertMaterial({ color, flatShading: flat });
}

const matFloor = mat(0x8B6914);
const matCageBar = mat(0xcccccc);
const matCageTop = mat(0xaaaaaa);
const matWheel = mat(0xff6b9d);
const matWheelSpoke = mat(0xffd93d);
const matBowl = mat(0x4ecdc4);
const matFood = mat(0x8B4513);
const matTunnel = mat(0xff8c42);
const matBedding = mat(0xf5deb3);
const matWater = mat(0x66ccff);

// --- Floor / Tray ---
const trayGeo = new THREE.CylinderGeometry(5.5, 5.5, 0.5, 12);
const tray = new THREE.Mesh(trayGeo, matFloor);
tray.position.y = 0.25;
tray.receiveShadow = true;
scene.add(tray);

// Bedding layer
const beddingGeo = new THREE.CylinderGeometry(5.2, 5.2, 0.3, 12);
const bedding = new THREE.Mesh(beddingGeo, matBedding);
bedding.position.y = 0.55;
bedding.receiveShadow = true;
scene.add(bedding);

// --- Cage Bars ---
const barGeo = new THREE.CylinderGeometry(0.04, 0.04, 4, 6);
for (let i = 0; i < 24; i++) {
  const angle = (i / 24) * Math.PI * 2;
  const bar = new THREE.Mesh(barGeo, matCageBar);
  bar.position.set(Math.cos(angle) * 5.3, 2.5, Math.sin(angle) * 5.3);
  bar.castShadow = true;
  scene.add(bar);
}

// Cage top ring
const topRingGeo = new THREE.TorusGeometry(5.3, 0.06, 8, 24);
const topRing = new THREE.Mesh(topRingGeo, matCageTop);
topRing.position.y = 4.5;
topRing.rotation.x = Math.PI / 2;
scene.add(topRing);

// Cage lid (mesh top)
const lidGeo = new THREE.CylinderGeometry(5.4, 5.4, 0.1, 12);
const lid = new THREE.Mesh(lidGeo, new THREE.MeshLambertMaterial({ color: 0x999999, transparent: true, opacity: 0.3, flatShading: true }));
lid.position.y = 4.6;
scene.add(lid);

// --- Hamster Wheel ---
const wheelGroup = new THREE.Group();
const wheelOuterGeo = new THREE.TorusGeometry(1.2, 0.12, 8, 16);
const wheelOuter = new THREE.Mesh(wheelOuterGeo, matWheel);
wheelGroup.add(wheelOuter);

// Spokes
for (let i = 0; i < 6; i++) {
  const angle = (i / 6) * Math.PI * 2;
  const spokeGeo = new THREE.CylinderGeometry(0.03, 0.03, 2.2, 4);
  const spoke = new THREE.Mesh(spokeGeo, matWheelSpoke);
  spoke.rotation.z = angle;
  spoke.position.set(Math.cos(angle) * 0.55, Math.sin(angle) * 0.55, 0);
  spoke.rotation.z = angle + Math.PI / 2;
  wheelGroup.add(spoke);
}

// Wheel stand
const standGeo = new THREE.CylinderGeometry(0.08, 0.08, 2.5, 6);
const stand = new THREE.Mesh(standGeo, matCageBar);
stand.position.set(0, -1.5, 0);
wheelGroup.add(stand);

// Wheel axle
const axleGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.6, 6);
const axle = new THREE.Mesh(axleGeo, matCageBar);
axle.rotation.x = Math.PI / 2;
axle.position.z = 0;
wheelGroup.add(axle);

wheelGroup.position.set(-2.5, 2.5, -1);
wheelGroup.rotation.y = Math.PI / 4;
scene.add(wheelGroup);

// --- Food Bowl ---
const bowlGroup = new THREE.Group();
const bowlGeo = new THREE.CylinderGeometry(0.5, 0.35, 0.4, 8);
const bowl = new THREE.Mesh(bowlGeo, matBowl);
bowl.castShadow = true;
bowlGroup.add(bowl);

// Food pellets
for (let i = 0; i < 5; i++) {
  const pelletGeo = new THREE.IcosahedronGeometry(0.08, 0);
  const pellet = new THREE.Mesh(pelletGeo, matFood);
  pellet.position.set((Math.random() - 0.5) * 0.3, 0.25, (Math.random() - 0.5) * 0.3);
  bowlGroup.add(pellet);
}
bowlGroup.position.set(2.5, 0.85, 1.5);
scene.add(bowlGroup);

// --- Water Bottle ---
const bottleGroup = new THREE.Group();
const bottleGeo = new THREE.CylinderGeometry(0.2, 0.2, 1.2, 8);
const bottle = new THREE.Mesh(bottleGeo, matWater);
bottle.castShadow = true;
bottleGroup.add(bottle);
const bottleCapGeo = new THREE.CylinderGeometry(0.12, 0.15, 0.3, 8);
const bottleCap = new THREE.Mesh(bottleCapGeo, matCageBar);
bottleCap.position.y = -0.7;
bottleGroup.add(bottleCap);
bottleGroup.position.set(3.5, 2.5, -2);
scene.add(bottleGroup);

// --- Tunnel ---
const tunnelGeo = new THREE.CylinderGeometry(0.6, 0.6, 2.5, 8, 1, false, 0, Math.PI);
const tunnel = new THREE.Mesh(tunnelGeo, matTunnel);
tunnel.rotation.z = Math.PI / 2;
tunnel.rotation.y = Math.PI / 3;
tunnel.position.set(0, 0.7, 2.5);
tunnel.castShadow = true;
scene.add(tunnel);

// --- Hamster Builder ---
function createHamster(color) {
  const group = new THREE.Group();
  const bodyMat = mat(color);
  const bellyMat = mat(0xffeedd);
  const eyeMat = mat(0x111111);
  const noseMat = mat(0xff6b8a);
  const earInnerMat = mat(0xffb3c1);

  // Body
  const bodyGeo = new THREE.IcosahedronGeometry(0.45, 1);
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.scale.set(1, 0.85, 1.2);
  body.castShadow = true;
  group.add(body);

  // Belly
  const bellyGeo = new THREE.IcosahedronGeometry(0.32, 0);
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.position.set(0, -0.1, 0.15);
  belly.scale.set(0.8, 0.7, 0.9);
  group.add(belly);

  // Head
  const headGeo = new THREE.IcosahedronGeometry(0.28, 1);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.position.set(0, 0.15, 0.4);
  head.castShadow = true;
  group.add(head);

  // Cheeks
  const cheekGeo = new THREE.IcosahedronGeometry(0.12, 0);
  const cheekL = new THREE.Mesh(cheekGeo, bellyMat);
  cheekL.position.set(0.18, 0.05, 0.45);
  group.add(cheekL);
  const cheekR = new THREE.Mesh(cheekGeo, bellyMat);
  cheekR.position.set(-0.18, 0.05, 0.45);
  group.add(cheekR);

  // Ears
  const earGeo = new THREE.SphereGeometry(0.1, 5, 4);
  const earL = new THREE.Mesh(earGeo, bodyMat);
  earL.position.set(0.18, 0.35, 0.2);
  group.add(earL);
  const earR = new THREE.Mesh(earGeo, bodyMat);
  earR.position.set(-0.18, 0.35, 0.2);
  group.add(earR);

  // Inner ears
  const innerEarGeo = new THREE.SphereGeometry(0.06, 4, 3);
  const innerEarL = new THREE.Mesh(innerEarGeo, earInnerMat);
  innerEarL.position.set(0.18, 0.36, 0.22);
  group.add(innerEarL);
  const innerEarR = new THREE.Mesh(innerEarGeo, earInnerMat);
  innerEarR.position.set(-0.18, 0.36, 0.22);
  group.add(innerEarR);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.05, 5, 4);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(0.1, 0.18, 0.55);
  group.add(eyeL);
  const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
  eyeR.position.set(-0.1, 0.18, 0.55);
  group.add(eyeR);

  // Eye shine
  const shineGeo = new THREE.SphereGeometry(0.02, 4, 3);
  const shineMat = mat(0xffffff);
  const shineL = new THREE.Mesh(shineGeo, shineMat);
  shineL.position.set(0.12, 0.2, 0.57);
  group.add(shineL);
  const shineR = new THREE.Mesh(shineGeo, shineMat);
  shineR.position.set(-0.08, 0.2, 0.57);
  group.add(shineR);

  // Nose
  const noseGeo = new THREE.IcosahedronGeometry(0.04, 0);
  const nose = new THREE.Mesh(noseGeo, noseMat);
  nose.position.set(0, 0.08, 0.62);
  group.add(nose);

  // Tail (tiny nub)
  const tailGeo = new THREE.SphereGeometry(0.06, 4, 3);
  const tail = new THREE.Mesh(tailGeo, bodyMat);
  tail.position.set(0, 0.05, -0.5);
  group.add(tail);

  // Legs
  const legGeo = new THREE.CylinderGeometry(0.05, 0.04, 0.2, 5);
  const legPositions = [
    [0.15, -0.35, 0.15], [-0.15, -0.35, 0.15],
    [0.15, -0.35, -0.15], [-0.15, -0.35, -0.15]
  ];
  const legs = [];
  legPositions.forEach(pos => {
    const leg = new THREE.Mesh(legGeo, bodyMat);
    leg.position.set(...pos);
    leg.castShadow = true;
    group.add(leg);
    legs.push(leg);
  });

  return { group, legs, body, head };
}

// --- Create Hamsters ---
const hamsterColors = [0xf4a460, 0xe8d5b7, 0x8B7355, 0xffdab9];
const hamsters = [];

for (let i = 0; i < 4; i++) {
  const { group, legs, body, head } = createHamster(hamsterColors[i]);
  group.position.set(
    (Math.random() - 0.5) * 4,
    0.85,
    (Math.random() - 0.5) * 4
  );
  group.rotation.y = Math.random() * Math.PI * 2;
  scene.add(group);

  hamsters.push({
    mesh: group,
    legs,
    body,
    head,
    state: 'idle',
    stateTimer: 0,
    speed: 0.015 + Math.random() * 0.01,
    turnSpeed: 0.03 + Math.random() * 0.02,
    targetAngle: Math.random() * Math.PI * 2,
    walkTime: 0,
    maxWalkTime: 2 + Math.random() * 3,
    idleTime: 1 + Math.random() * 2,
    bobPhase: Math.random() * Math.PI * 2,
    wheelSpin: 0
  });
}

// --- Wheel rotation state ---
let wheelRotation = 0;
let wheelActive = false;
let wheelSpeed = 0;

// --- Animation ---
const clock = new THREE.Clock();

function updateHamsters(dt, time) {
  hamsters.forEach((h, idx) => {
    h.stateTimer += dt;

    if (h.state === 'idle' && h.stateTimer > h.idleTime) {
      h.state = 'walking';
      h.stateTimer = 0;
      h.targetAngle = Math.random() * Math.PI * 2;
      h.maxWalkTime = 1.5 + Math.random() * 3;
    } else if (h.state === 'walking' && h.stateTimer > h.maxWalkTime) {
      h.state = 'idle';
      h.stateTimer = 0;
      h.idleTime = 1 + Math.random() * 3;
    }

    if (h.state === 'walking') {
      // Turn toward target
      let angleDiff = h.targetAngle - h.mesh.rotation.y;
      while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
      while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
      h.mesh.rotation.y += angleDiff * h.turnSpeed;

      // Move forward
      const dx = Math.sin(h.mesh.rotation.y) * h.speed;
      const dz = Math.cos(h.mesh.rotation.y) * h.speed;
      h.mesh.position.x += dx;
      h.mesh.position.z += dz;

      // Keep in cage
      const dist = Math.sqrt(h.mesh.position.x ** 2 + h.mesh.position.z ** 2);
      if (dist > 4.2) {
        const toCenter = Math.atan2(-h.mesh.position.x, -h.mesh.position.z);
        h.targetAngle = toCenter + (Math.random() - 0.5) * 1;
      }

      // Leg animation
      h.legs.forEach((leg, i) => {
        leg.rotation.x = Math.sin(time * 8 + h.bobPhase + i * Math.PI) * 0.4;
      });

      // Body bob
      h.mesh.position.y = 0.85 + Math.sin(time * 6 + h.bobPhase) * 0.03;

      // Check if near wheel
      const wheelDist = Math.sqrt((h.mesh.position.x - wheelGroup.position.x) ** 2 + (h.mesh.position.z - wheelGroup.position.z) ** 2);
      if (wheelDist < 1.5) {
        wheelActive = true;
      }
    } else {
      // Idle: gentle breathing
      h.mesh.position.y = 0.85 + Math.sin(time * 2 + h.bobPhase) * 0.02;
      h.legs.forEach(leg => { leg.rotation.x *= 0.9; });
    }

    // Check if any hamster is on wheel
    const wheelDist = Math.sqrt((h.mesh.position.x - wheelGroup.position.x) ** 2 + (h.mesh.position.z - wheelGroup.position.z) ** 2);
    if (wheelDist < 1.5 && h.state === 'walking') {
      wheelActive = true;
    }
  });
}

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.getElapsedTime();

  updateHamsters(dt, time);

  // Wheel spin
  if (wheelActive) {
    wheelSpeed = Math.min(wheelSpeed + dt * 2, 4);
    wheelActive = false; // Reset each frame; will be set again if hamster is near
  } else {
    wheelSpeed *= 0.98;
  }
  wheelRotation += wheelSpeed * dt;
  wheelGroup.rotation.z = wheelRotation;

  // Gentle scene rotation for the whole cage
  // (subtle idle animation on bedding)
  bedding.position.y = 0.55 + Math.sin(time * 0.5) * 0.01;

  controls.update();
  renderer.render(scene, camera);
}

animate();

// --- Resize ---
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

This creates a complete, self-contained **Low-Poly Hamster Playground** that runs immediately in any modern browser. Here's what's included:

**Scene Elements:**
- 🪵 Circular wooden tray with a bedding layer
- 🔲 Wire cage bars arranged in a circle with a translucent lid
- 🎡 A colorful spinning hamster wheel (spins when hamsters get near it!)
- 🥣 A food bowl with pellets
- 💧 A water bottle mounted to the cage
- 🕳️ A half-cylinder tunnel

**Hamsters (×4):**
- Built from low-poly icosahedrons and spheres
- Each has a unique color (sandy, cream, brown, peach)
- Cute details: inner ears, cheeks, nose, eye shine, tiny tail nub

**Behavior:**
- State machine: `idle` → `walking` → `idle` (randomized timers)
- Walk with leg animation and body bob
- Turn toward random headings, turn back when near cage wall
- Wheel spins when a hamster walks close to it

**Interaction:**
- OrbitControls for drag-rotate and scroll-zoom
- Damped camera movement for smooth feel