# Low-Poly Hamster Playground 🐹

Here's the complete single-file project. Save it as `index.html` and open it in any modern browser — no build step needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; height: 100%; }
  #info {
    position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
    font-family: 'Comic Sans MS', 'Segoe UI', sans-serif;
    background: rgba(255, 255, 255, 0.85);
    color: #7a4a1e; padding: 10px 22px; border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15); pointer-events: none;
    text-align: center; z-index: 10;
  }
  #info h1 { margin: 0; font-size: 20px; }
  #info p  { margin: 4px 0 0; font-size: 13px; color: #9a6a3e; }
</style>
</head>
<body>
<div id="info">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate &bull; Scroll to zoom &bull; Watch the little guys live their best lives</p>
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

// ---------------------------------------------------------------
// BASIC SETUP
// ---------------------------------------------------------------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xbfe8ff);
scene.fog = new THREE.Fog(0xbfe8ff, 30, 60);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(10, 8, 14);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 2, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.maxPolarAngle = Math.PI / 2 - 0.05;
controls.minDistance = 5;
controls.maxDistance = 30;

// Lights — warm and cozy
scene.add(new THREE.AmbientLight(0xfff2e0, 0.7));
const sun = new THREE.DirectionalLight(0xffffff, 1.2);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12;  sun.shadow.camera.bottom = -12;
scene.add(sun);

// ---------------------------------------------------------------
// HELPERS
// ---------------------------------------------------------------
const mat = (color, extra = {}) =>
  new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9, ...extra });

function box(w, h, d, material, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  return m;
}

// Cage dimensions
const CW = 12, CD = 8, CH = 5;   // width, depth, height

// ---------------------------------------------------------------
// THE CAGE
// ---------------------------------------------------------------
const cage = new THREE.Group();
scene.add(cage);

// Floor tray
const tray = box(CW + 0.6, 0.5, CD + 0.6, mat(0xf5d8a8), 0, 0.25, 0);
tray.receiveShadow = true;
cage.add(tray);

// Wood shavings — a bunch of tiny colorful pebbles on the floor
const shavingColors = [0xf0e0b8, 0xe8cf9a, 0xf5e8c8];
for (let i = 0; i < 60; i++) {
  const s = new THREE.Mesh(
    new THREE.ConeGeometry(0.12 + Math.random() * 0.1, 0.08, 4),
    mat(shavingColors[i % 3])
  );
  s.position.set((Math.random() - 0.5) * (CW - 1), 0.52, (Math.random() - 0.5) * (CD - 1));
  s.rotation.y = Math.random() * Math.PI;
  cage.add(s);
}

// Transparent glass walls
const glassMat = new THREE.MeshStandardMaterial({
  color: 0xcfeaff, transparent: true, opacity: 0.18, side: THREE.DoubleSide
});
const walls = [
  box(CW, CH, 0.05, glassMat, 0, CH / 2 + 0.5, -CD / 2),
  box(CW, CH, 0.05, glassMat, 0, CH / 2 + 0.5,  CD / 2),
  box(0.05, CH, CD, glassMat, -CW / 2, CH / 2 + 0.5, 0),
  box(0.05, CH, CD, glassMat,  CW / 2, CH / 2 + 0.5, 0),
];
walls.forEach(w => cage.add(w));

// Wooden frame: 4 vertical posts + top rim
const frameMat = mat(0x8a5a2e);
[[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([sx, sz]) => {
  cage.add(box(0.3, CH + 0.5, 0.3, frameMat, sx * CW / 2, (CH + 0.5) / 2, sz * CD / 2));
});
cage.add(box(CW + 0.3, 0.3, 0.3, frameMat, 0, CH + 0.5, -CD / 2));
cage.add(box(CW + 0.3, 0.3, 0.3, frameMat, 0, CH + 0.5,  CD / 2));
cage.add(box(0.3, 0.3, CD + 0.3, frameMat, -CW / 2, CH + 0.5, 0));
cage.add(box(0.3, 0.3, CD + 0.3, frameMat,  CW / 2, CH + 0.5, 0));

// A few horizontal wire bars on the front for that "cage" feel
const wireMat = mat(0xcccccc, { metalness: 0.6, roughness: 0.4 });
for (let i = 0; i < 5; i++) {
  cage.add(box(CW, 0.06, 0.06, wireMat, 0, 1.2 + i * 0.9, CD / 2 + 0.05));
}

// ---------------------------------------------------------------
// INTERACTIVE OBJECTS
// ---------------------------------------------------------------

// --- Exercise wheel (back-left corner) ---
const wheel = new THREE.Group();
wheel.position.set(-CW / 2 + 1.4, 0.5, -CD / 2 + 1.4);
const wheelSpin = new THREE.Group();
const ring = new THREE.Mesh(new THREE.TorusGeometry(1.1, 0.12, 6, 12), mat(0xff7eb6));
ring.castShadow = true;
wheelSpin.add(ring);
for (let i = 0; i < 4; i++) {
  const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.2, 5), mat(0xffaacc));
  spoke.rotation.z = (i / 4) * Math.PI;
  wheelSpin.add(spoke);
}
const hub = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 5), mat(0xffd166));
wheelSpin.add(hub);
wheel.add(wheelSpin);
// little stand
wheel.add(box(0.15, 1.1, 0.15, mat(0x8a5a2e), 0, -0.5, 0));
wheel.add(box(0.8, 0.12, 0.8, mat(0x8a5a2e), 0, -1.05, 0));
cage.add(wheel);
let wheelSpeed = 0;          // current
let wheelTargetSpeed = 0.4;   // idle spin

// --- Food bowl (front-right) ---
const bowl = new THREE.Group();
bowl.position.set(CW / 2 - 1.6, 0.5, CD / 2 - 1.6);
const bowlBody = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.35, 0.35, 8), mat(0x6ec6ff));
bowlBody.position.y = 0.18; bowlBody.castShadow = true;
bowl.add(bowlBody);
// seed pile
const seedMat = mat(0xd99548);
for (let i = 0; i < 7; i++) {
  const seed = new THREE.Mesh(new THREE.SphereGeometry(0.09, 5, 4), seedMat);
  seed.scale.y = 0.7;
  seed.position.set((Math.random() - 0.5) * 0.5, 0.38, (Math.random() - 0.5) * 0.5);
  bowl.add(seed);
}
cage.add(bowl);

// --- Tunnel (center) ---
const tunnel = new THREE.Group();
tunnel.position.set(0, 0.5, -0.5);
tunnel.rotation.y = 0.6;
const tube = new THREE.Mesh(
  new THREE.CylinderGeometry(0.55, 0.55, 2.6, 8, 1, false, 0, Math.PI),
  mat(0x9be79b, { side: THREE.DoubleSide })
);
tube.rotation.x = Math.PI / 2;
tube.castShadow = true;
tunnel.add(tube);
cage.add(tunnel);

// A cute ball toy
const ball = new THREE.Mesh(new THREE.IcosahedronGeometry(0.35, 0), mat(0xffe066));
ball.position.set(2.5, 0.85, 1.5);
ball.castShadow = true;
cage.add(ball);

// ---------------------------------------------------------------
// HAMSTERS
// ---------------------------------------------------------------
const HAMSTER_COLORS = [
  { fur: 0xf5a25a, belly: 0xffe8cc },  // golden
  { fur: 0xffe3c2, belly: 0xffffff },  // cream
  { fur: 0xa9744f, belly: 0xe8d0b0 },  // chocolate
  { fur: 0xe8e8e8, belly: 0xffffff },  // snowball
];

function makeHamster(colorSet) {
  const g = new THREE.Group();
  const furMat = mat(colorSet.fur);
  const bellyMat = mat(colorSet.belly);

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 7, 6), furMat);
  body.scale.set(0.85, 0.8, 1.15);
  body.position.y = 0.5;
  body.castShadow = true;
  g.add(body);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.34, 6, 5), furMat);
  head.position.set(0, 0.62, 0.5);
  head.castShadow = true;
  g.add(head);

  // Ears
  [-1, 1].forEach(side => {
    const ear = new THREE.Mesh(new THREE.ConeGeometry(0.13, 0.22, 4), furMat);
    ear.position.set(side * 0.18, 0.92, 0.42);
    ear.rotation.z = side * -0.4;
    g.add(ear);
    const inner = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.12, 4), bellyMat);
    inner.position.set(side * 0.18, 0.9, 0.46);
    inner.rotation.z = side * -0.4;
    g.add(inner);
  });

  // Eyes
  const eyeMat = mat(0x222222, { roughness: 0.3 });
  [-1, 1].forEach(side => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.06, 5, 4), eyeMat);
    eye.position.set(side * 0.16, 0.68, 0.76);
    g.add(eye);
  });

  // Nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 5, 4), mat(0xff8fa3));
  nose.position.set(0, 0.58, 0.84);
  g.add(nose);

  // Cheeks (these puff out when eating!)
  const cheeks = [];
  [-1, 1].forEach(side => {
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.16, 5, 4), bellyMat);
    cheek.position.set(side * 0.22, 0.5, 0.62);
    g.add(cheek);
    cheeks.push(cheek);
  });

  // Tiny tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.09, 5, 4), bellyMat);
  tail.position.set(0, 0.45, -0.55);
  g.add(tail);

  return { group: g, body, head, cheeks };
}

// ---------------------------------------------------------------
// SIMPLE AUTONOMOUS BEHAVIOR (state machine)
// ---------------------------------------------------------------
const BOUNDS = { x: CW / 2 - 0.9, z: CD / 2 - 0.9 };
const hamsters = [];

function rand(min, max) { return min + Math.random() * (max - min); }
function randomPoint() {
  return new THREE.Vector3(rand(-BOUNDS.x, BOUNDS.x), 0, rand(-BOUNDS.z, BOUNDS.z));
}

HAMSTER_COLORS.forEach((c, i) => {
  const h = makeHamster(c);
  h.group.position.copy(randomPoint());
  h.state = 'wander';
  h.target = randomPoint();
  h.timer = rand(1, 3);
  h.speed = rand(1.1, 1.7);
  h.cheekAmount = 0;
  scene.add(h.group);
  hamsters.push(h);
});

function updateHamster(h, dt, t) {
  h.timer -= dt;
  const pos = h.group.position;
  let moving = false;

  // Decide whether to change plans
  if (h.timer <= 0) {
    const r = Math.random();
    if (r < 0.18) {
      h.state = 'eat';
      h.target = bowl.position.clone().add(new THREE.Vector3(0, 0, 1.2));
      h.timer = 999; // resolved below
    } else if (r < 0.30) {
      h.state = 'wheel';
      h.target = wheel.position.clone().add(new THREE.Vector3(0.8, 0, 0.8));
      h.timer = 999;
    } else if (r < 0.45) {
      h.state = 'pause';
      h.timer = rand(1, 3);
    } else {
      h.state = 'wander';
      h.target = randomPoint();
      h.timer = rand(2, 5);
    }
  }

  const distToTarget = pos.distanceTo(h.target);

  switch (h.state) {
    case 'wander': {
      if (distToTarget < 0.3 || h.timer <= 0) {
        h.target = randomPoint();
        h.timer = rand(2, 5);
      }
      stepToward(h, h.target, h.speed, dt);
      moving = true;
      break;
    }
    case 'pause':
      // Occasional head tilt for cuteness
      h.head.rotation.z = Math.sin(t * 6) * 0.3;
      break;

    case 'eat': {
      if (distToTarget > 0.4) {
        stepToward(h, h.target, h.speed, dt);
        moving = true;
      } else {
        // Munch! Face the bowl, cheeks puff
        faceToward(h, bowl.position, dt, 4);
        h.cheekAmount = Math.min(1, h.cheekAmount + dt * 2);
        h.head.rotation.y = Math.sin(t * 12) * 0.25; // chomping
        if (h.timer <= 0) { h.state = 'wander'; h.target = randomPoint(); h.timer = rand(2, 4); }
      }
      break;
    }

    case 'wheel': {
      if (distToTarget > 0.5) {
        stepToward(h, h.target, h.speed * 1.3, dt);
        moving = true;
      } else {
        // Running on the wheel!
        faceToward(h, wheel.position, dt, 4);
        h.group.position.y = 0.5 + Math.abs(Math.sin(t * 14)) * 0.12; // gallop bounce
        wheelTargetSpeed = 6;
        if (h.timer <= 0) {
          h.state = 'wander'; h.target = randomPoint(); h.timer = rand(2, 4);
          h.group.position.y = 0;
        }
      }
      break;
    }
  }

  // Smoothly relax cheeks when not eating
  if (h.state !== 'eat') h.cheekAmount = Math.max(0, h.cheekAmount - dt * 2);
  h.cheeks.forEach(c => c.scale.setScalar(1 + h.cheekAmount * 0.8));

  // Bobbing while walking
  if (moving) {
    h.group.position.y = Math.abs(Math.sin(t * 10)) * 0.05;
    h.head.rotation.z *= 0.9;
  } else if (h.state !== 'wheel' && h.state !== 'pause') {
    h.group.position.y *= 0.85;
  }
}

function stepToward(h, target, speed, dt) {
  const dir = new THREE.Vector3().subVectors(target, h.group.position);
  dir.y = 0;
  const dist = dir.length();
  if (dist > 0.001) {
    dir.normalize();
    h.group.position.addScaledVector(dir, speed * dt);
    faceToward(h, target, dt, 6);
  }
  // Keep inside the cage
  h.group.position.x = THREE.MathUtils.clamp(h.group.position.x, -BOUNDS.x, BOUNDS.x);
  h.group.position.z = THREE.MathUtils.clamp(h.group.position.z, -BOUNDS.z, BOUNDS.z);
}

function faceToward(h, target, dt, turnSpeed) {
  const desired = Math.atan2(target.x - h.group.position.x, target.z - h.group.position.z);
  let diff = desired - h.group.rotation.y;
  while (diff > Math.PI) diff -= Math.PI * 2;
  while (diff < -Math.PI) diff += Math.PI * 2;
  h.group.rotation.y += diff * Math.min(1, turnSpeed * dt);
}

// ---------------------------------------------------------------
// ANIMATION LOOP
// ---------------------------------------------------------------
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // Wheel: nobody riding → slow idle spin
  wheelTargetSpeed = hamsters.some(h => h.state === 'wheel') ? 6 : 0.4;
  wheelSpeed += (wheelTargetSpeed - wheelSpeed) * Math.min(1, dt * 2);
  wheelSpin.rotation.z -= wheelSpeed * dt;

  hamsters.forEach(h => updateHamsteinSafe(h, dt, t));

  // Ball toy wobbles gently
  ball.rotation.y += dt * 0.5;
  ball.rotation.x += dt * 0.3;

  controls.update();
  renderer.render(scene, camera);
}

// (small alias so the code above reads cleanly)
function updateHamsteinSafe(h, dt, t) { updateHamster(h, dt, t); }

window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

animate();
</script>
</body>
</html>
```

## What you get

| Element | Details |
|---|---|
| **Cage** | Wood-shaved tray, wooden frame, translucent glass walls, horizontal wire bars on the front |
| **4 hamsters** | Golden, cream, chocolate, and snowball — each built from ~15 low-poly primitives with flat shading, puffy cheeks, and tiny tails |
| **Behaviors** | A small state machine: `wander` → `pause` (with a cute head tilt) → `eat` (walks to the bowl, cheeks puff up, chomping head) → `wheel` (gallop-bounce while the wheel spins up) |
| **Interactive objects** | Pink exercise wheel (spins slowly when idle, fast when a hamster rides), blue food bowl with seeds, green tunnel, wobbling yellow ball toy |
| **Camera** | OrbitControls with damping, zoom limits, and a floor clamp so you can't go under the ground |

## Design choices kept simple on purpose

- **No textures, no loaders, no external assets** — everything is procedural geometry and solid colors, so it loads instantly.
- **Clamped delta time** (`Math.min(dt, 0.05)`) prevents physics jumps if the tab loses focus.
- **Boundary clamping** keeps hamsters inside the cage no matter how the pathfinding goes.
- **Single wheel-speed variable** means multiple hamsters can queue for the wheel without conflicts — last one standing wins, which is honestly very hamster-like. 🐹