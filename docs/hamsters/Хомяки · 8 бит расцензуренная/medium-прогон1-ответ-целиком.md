# Low-Poly Hamster Playground 🐹

Here's the complete single-file project. Save it as `index.html` and open it in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #ffe9f2; }
  #info {
    position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
    font-family: "Comic Sans MS", "Chalkboard SE", cursive, sans-serif;
    background: rgba(255,255,255,0.85); padding: 8px 18px; border-radius: 20px;
    color: #7a4b2a; font-size: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.12);
    pointer-events: none; user-select: none;
  }
</style>
</head>
<body>
<div id="info">🐹 Low-Poly Hamster Playground — drag to rotate, scroll to zoom</div>

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

// ---------- Scene / camera / renderer ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9f2);
scene.fog = new THREE.Fog(0xffe9f2, 18, 30);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(6, 5.5, 8);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.2, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI * 0.49;
controls.minDistance = 4;
controls.maxDistance = 16;

// ---------- Lights ----------
scene.add(new THREE.HemisphereLight(0xfff5e6, 0xd9b8ff, 0.9));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(6, 10, 4);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -8; sun.shadow.camera.right = 8;
sun.shadow.camera.top = 8;  sun.shadow.camera.bottom = -8;
scene.add(sun);

// ---------- Materials helper ----------
const mat = (color, flat = true) =>
  new THREE.MeshStandardMaterial({ color, flatShading: flat, roughness: 0.85 });

// ---------- Ground (table) ----------
const table = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 0.4, 10), mat(0xc98a5b));
table.position.y = -0.2;
table.receiveShadow = true;
scene.add(table);

// ---------- Cage tray (floor) ----------
const CAGE_R = 3.2;
const tray = new THREE.Mesh(new THREE.CylinderGeometry(CAGE_R, CAGE_R*0.9, 0.5, 10), mat(0x8fd3f4));
tray.position.y = 0.25;
tray.receiveShadow = true;
tray.castShadow = true;
scene.add(tray);

// bedding
const bed = new THREE.Mesh(new THREE.CylinderGeometry(CAGE_R*0.94, CAGE_R*0.94, 0.12, 10), mat(0xf7d9a0));
bed.position.y = 0.5;
bed.receiveShadow = true;
scene.add(bed);

// ---------- Cage walls (bars + rings) ----------
const cageGroup = new THREE.Group();
const barMat = new THREE.MeshStandardMaterial({ color: 0xe8e8ee, metalness: 0.7, roughness: 0.3 });
const barGeo = new THREE.CylinderGeometry(0.045, 0.045, 2.6, 5);
const BAR_COUNT = 26;
for (let i = 0; i < BAR_COUNT; i++) {
  const a = (i / BAR_COUNT) * Math.PI * 2;
  const bar = new THREE.Mesh(barGeo, barMat);
  bar.position.set(Math.cos(a) * CAGE_R, 1.8, Math.sin(a) * CAGE_R);
  cageGroup.add(bar);
}
const ringGeo = new THREE.TorusGeometry(CAGE_R, 0.07, 6, 40);
[0.55, 3.0].forEach(y => {
  const ring = new THREE.Mesh(ringGeo, barMat);
  ring.rotation.x = Math.PI / 2;
  ring.position.y = y;
  cageGroup.add(ring);
});
scene.add(cageGroup);

// ---------- Exercise wheel (interactive object) ----------
const wheel = new THREE.Group();
const wheelRim = new THREE.Mesh(new THREE.TorusGeometry(0.75, 0.09, 6, 20), mat(0xff8fab));
wheel.add(wheelRim);
const spokeGeo = new THREE.CylinderGeometry(0.03, 0.03, 1.5, 5);
for (let i = 0; i < 5; i++) {
  const s = new THREE.Mesh(spokeGeo, mat(0xffc2d1));
  s.rotation.z = (i / 5) * Math.PI;
  wheel.add(s);
}
const hub = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 6), mat(0xff5c8a));
wheel.add(hub);
const wheelStand = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.7, 0.18), mat(0xff5c8a));
wheelStand.position.y = -0.35;
wheel.add(wheelStand);
const wheelBase = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.1, 0.5), mat(0xff5c8a));
wheelBase.position.y = -0.68;
wheel.add(wheelBase);
wheel.position.set(1.9, 1.25, -1.3);
scene.add(wheel);
let wheelSpin = 0; // radians/sec target speed

// ---------- Food bowl ----------
const bowl = new THREE.Group();
const bowlBody = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.25, 0.22, 8), mat(0x9be79b));
bowl.add(bowlBody);
const food = new THREE.Mesh(new THREE.SphereGeometry(0.28, 7, 5), mat(0xf2a541));
food.scale.y = 0.5;
food.position.y = 0.08;
bowl.add(food);
bowl.position.set(-1.8, 0.62, 1.5);
scene.add(bowl);

// ---------- Tunnel ----------
const tunnel = new THREE.Group();
const tunnelBody = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 1.4, 8, 1, true), mat(0xb197fc));
tunnelBody.material.side = THREE.DoubleSide;
tunnelBody.rotation.z = Math.PI / 2;
tunnel.add(tunnelBody);
tunnel.position.set(-0.4, 0.85, -1.8);
tunnel.rotation.y = 0.6;
scene.add(tunnel);

// ---------- Scatter some seed pellets ----------
const pelletMat = mat(0xd98e3a);
const pelletGeo = new THREE.SphereGeometry(0.05, 5, 4);
for (let i = 0; i < 25; i++) {
  const p = new THREE.Mesh(pelletGeo, pelletMat);
  const a = Math.random() * Math.PI * 2, r = Math.random() * (CAGE_R - 0.5);
  p.position.set(Math.cos(a) * r, 0.58, Math.sin(a) * r);
  scene.add(p);
}

// ---------- Hamster factory ----------
function makeHamster(bodyColor, cheekColor) {
  const g = new THREE.Group();

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.32, 8, 6), mat(bodyColor));
  body.scale.set(1.25, 0.95, 1);
  body.position.y = 0.3;
  body.castShadow = true;
  g.add(body);

  // face bump
  const face = new THREE.Mesh(new THREE.SphereGeometry(0.18, 7, 5), mat(bodyColor));
  face.position.set(0.3, 0.36, 0);
  face.castShadow = true;
  g.add(face);

  // cheeks
  [-1, 1].forEach(s => {
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.09, 6, 5), mat(cheekColor));
    cheek.position.set(0.38, 0.28, s * 0.13);
    g.add(cheek);
  });

  // ears
  [-1, 1].forEach(s => {
    const ear = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.14, 5), mat(bodyColor));
    ear.position.set(0.12, 0.62, s * 0.15);
    ear.rotation.z = -0.3;
    g.add(ear);
    const inner = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.08, 5), mat(0xffb3c1));
    inner.position.set(0.14, 0.6, s * 0.15);
    inner.rotation.z = -0.3;
    g.add(inner);
  });

  // eyes
  [-1, 1].forEach(s => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.035, 5, 4), mat(0x222222, false));
    eye.position.set(0.45, 0.42, s * 0.1);
    g.add(eye);
  });

  // nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.045, 5, 4), mat(0xff7aa2, false));
  nose.position.set(0.48, 0.34, 0);
  g.add(nose);

  // stubby feet
  [-1, 1].forEach(s => {
    const foot = new THREE.Mesh(new THREE.SphereGeometry(0.07, 5, 4), mat(bodyColor));
    foot.scale.set(1.4, 0.6, 1);
    foot.position.set(0.15, 0.06, s * 0.16);
    g.add(foot);
    const back = new THREE.Mesh(new THREE.SphereGeometry(0.07, 5, 4), mat(bodyColor));
    back.scale.set(1.4, 0.6, 1);
    back.position.set(-0.18, 0.06, s * 0.16);
    g.add(back);
  });

  // tail nub
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.06, 5, 4), mat(bodyColor));
  tail.position.set(-0.42, 0.3, 0);
  g.add(tail);

  return g;
}

// ---------- Hamster AI ----------
const HAMSTER_DEFS = [
  { body: 0xf7b267, cheek: 0xffd9b3 }, // orange
  { body: 0xffffff, cheek: 0xffc2d1 }, // white
  { body: 0xc9a227, cheek: 0xf5deb3 }, // gold
];

const hamsters = HAMSTER_DEFS.map((def, i) => {
  const mesh = makeHamster(def.body, def.cheek);
  const a = (i / HAMSTER_DEFS.length) * Math.PI * 2;
  mesh.position.set(Math.cos(a) * 1.2, 0.55, Math.sin(a) * 1.2);
  scene.add(mesh);

  return {
    mesh,
    angle: Math.random() * Math.PI * 2,
    radius: 0.8 + Math.random(),
    speed: 0.9 + Math.random() * 0.5,
    state: 'wander',
    timer: 1 + Math.random() * 3,
    bobPhase: Math.random() * 10,
    target: new THREE.Vector3(),
  };
});

function updateHamster(h, dt, t) {
  h.timer -= dt;

  const pos = h.mesh.position;
  const distToWheel = pos.distanceTo(wheel.position.clone().setY(pos.y));
  const distToBowl  = pos.distanceTo(bowl.position.clone().setY(pos.y));

  // --- State transitions ---
  if (h.state === 'wander' && h.timer <= 0) {
    const roll = Math.random();
    if (distToWheel > 1.2 && roll < 0.35) {
      h.state = 'toWheel';
      h.target.copy(wheel.position).setY(0.55);
    } else if (distToBowl > 0.9 && roll < 0.6) {
      h.state = 'toBowl';
      h.target.copy(bowl.position).setY(0.55);
    } else {
      h.state = 'pause';
      h.timer = 1 + Math.random() * 2.5;
    }
  }
  else if (h.state === 'pause' && h.timer <= 0) {
    h.state = 'wander';
    h.timer = 2 + Math.random() * 4;
  }
  else if (h.state === 'toWheel') {
    if (distToWheel < 0.9) { h.state = 'atWheel'; h.timer = 2.5 + Math.random() * 2; }
  }
  else if (h.state === 'toBowl') {
    if (distToBowl < 0.7) { h.state = 'eat'; h.timer = 1.5 + Math.random() * 2; }
  }
  else if ((h.state === 'atWheel' || h.state === 'eat') && h.timer <= 0) {
    h.state = 'wander';
    h.timer = 2 + Math.random() * 4;
  }

  // --- Movement per state ---
  let moving = false;

  if (h.state === 'wander') {
    // spiral-ish roaming inside the cage
    h.angle += h.speed * dt * (Math.random() > 0.5 ? 1 : -1) * 0.6;
    h.radius += Math.sin(t * 0.7 + h.bobPhase) * dt * 0.8;
    h.radius = THREE.MathUtils.clamp(h.radius, 0.5, CAGE_R - 0.6);
    const nx = Math.cos(h.angle) * h.radius;
    const nz = Math.sin(h.angle) * h.radius;
    const dx = nx - pos.x, dz = nz - pos.z;
    const d = Math.hypot(dx, dz);
    if (d > 0.01) {
      pos.x += (dx / d) * Math.min(d, h.speed * dt);
      pos.z += (dz / d) * Math.min(d, h.speed * dt);
      h.mesh.rotation.y = Math.atan2(dx, dz);
      moving = true;
    }
  }
  else if (h.state === 'toWheel' || h.state === 'toBowl') {
    const dx = h.target.x - pos.x, dz = h.target.z - pos.z;
    const d = Math.hypot(dx, dz);
    if (d > 0.05) {
      pos.x += (dx / d) * Math.min(d, h.speed * 1.1 * dt);
      pos.z += (dz / d) * Math.min(d, h.speed * 1.1 * dt);
      h.mesh.rotation.y = Math.atan2(dx, dz);
      moving = true;
    }
  }
  else if (h.state === 'atWheel') {
    // face the wheel and scurry in place
    h.mesh.lookAt(wheel.position.x, pos.y, wheel.position.z);
    wheelSpin = 4.5;
    moving = true;
  }
  else if (h.state === 'eat') {
    h.mesh.lookAt(bowl.position.x, pos.y, bowl.position.z);
    moving = false;
  }

  // --- Squash & stretch bobbing while moving ---
  if (moving) {
    h.bobPhase += dt * 14;
    h.mesh.scale.y = 1 + Math.sin(h.bobPhase) * 0.08;
    h.mesh.scale.x = 1 - Math.sin(h.bobPhase) * 0.05;
    h.mesh.scale.z = 1 - Math.sin(h.bobPhase) * 0.05;
  } else {
    // idle breathing
    h.mesh.scale.y = 1 + Math.sin(t * 3 + h.bobPhase) * 0.02;
    h.mesh.scale.x = h.mesh.scale.z = 1;
  }
}

// ---------- Animate ----------
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  hamsters.forEach(h => updateHamster(h, dt, t));

  // wheel decays to a slow idle spin
  wheelSpin *= Math.pow(0.25, dt);          // exponential decay
  if (wheelSpin < 0.15) wheelSpin = 0.15;    // gentle idle
  wheel.rotation.x -= wheelSpin * dt;

  // food gently bobs (funny)
  food.rotation.y += dt * 0.5;

  controls.update();
  renderer.render(scene, camera);
}
animate();

// ---------- Resize ----------
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## What's in the scene

| Element | Details |
|---|---|
| **Cage** | 26 low-poly metal bars + two rings, sitting on a pastel blue tray with sandy bedding |
| **Hamsters ×3** | Orange, white, and gold — each built from ~15 primitives (body, face, cheeks, ears, eyes, nose, stubby feet, tail nub) |
| **Interactive wheel** | Spins fast when a hamster reaches it, then decays to a lazy idle spin |
| **Food bowl** | Hamsters walk over and "eat" — the food pellet slowly rotates, which is suspicious but funny |
| **Tunnel + seeds** | Decorative purple tunnel and scattered seed pellets for charm |

## Behavior system

Each hamster runs a tiny state machine: **wander → pause / toWheel / toBowl → atWheel / eat → wander**. While moving they get a squash-and-stretch bob; while idle they do subtle breathing. Each has randomized speed and phase so no two hamsters move in sync.

## Controls
- **Drag** — orbit the camera
- **Scroll / pinch** — zoom (clamped so you can't clip through the floor)
- Damped controls for smooth motion

Just open the file — no build step, no server needed (Three.js loads from CDN via import map).