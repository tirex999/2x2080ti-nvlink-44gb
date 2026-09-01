

# Low-Poly Hamster Playground 🐹

Here's the complete single-file project. Save it as `index.html` and open it in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; background: #ffe9d6; }
  canvas { display: block; }
  #ui {
    position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
    font-family: 'Comic Sans MS', 'Chalkboard SE', cursive, sans-serif;
    text-align: center; pointer-events: none; color: #7a4a21;
  }
  #ui h1 { margin: 0; font-size: 26px; text-shadow: 2px 2px 0 #fff; }
  #ui p  { margin: 4px 0 0; font-size: 14px; opacity: 0.85; }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate &nbsp;•&nbsp; Scroll to zoom &nbsp;•&nbsp; Click the wheel for a turbo spin!</p>
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

/* ============================================================
   BASIC SETUP
============================================================ */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9d6);
scene.fog = new THREE.Fog(0xffe9d6, 25, 45);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 100);
camera.position.set(9, 7, 11);

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
controls.minDistance = 6;
controls.maxDistance = 22;
controls.maxPolarAngle = Math.PI * 0.48;

/* ============================================================
   LIGHTS
============================================================ */
scene.add(new THREE.AmbientLight(0xfff2e0, 0.7));

const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -10;
sun.shadow.camera.right = 10;
sun.shadow.camera.top = 10;
sun.shadow.camera.bottom = -10;
scene.add(sun);

const fill = new THREE.DirectionalLight(0xbfe3ff, 0.35);
fill.position.set(-6, 5, -8);
scene.add(fill);

/* ============================================================
   MATERIAL HELPER (flat-shaded, cute colors)
============================================================ */
const mat = (color, extra = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness: 0.85, flatShading: true, ...extra });

function shadowed(mesh) {
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

/* ============================================================
   CAGE: TRAY + WIRE BARS
============================================================ */
const CAGE_W = 8, CAGE_D = 8, CAGE_H = 4.2;
const cage = new THREE.Group();
scene.add(cage);

// Base tray
const tray = shadowed(new THREE.Mesh(
  new THREE.BoxGeometry(CAGE_W + 0.6, 0.5, CAGE_D + 0.6), mat(0xf78fb3)));
tray.position.y = -0.25;
cage.add(tray);

// Floor (wood shavings look)
const floor = shadowed(new THREE.Mesh(
  new THREE.BoxGeometry(CAGE_W, 0.15, CAGE_D), mat(0xe8c88f)));
floor.position.y = 0.07;
cage.add(floor);

// A few scattered "shaving" pebbles
for (let i = 0; i < 26; i++) {
  const pebble = shadowed(new THREE.Mesh(
    new THREE.DodecahedronGeometry(0.08 + Math.random() * 0.08, 0),
    mat([0xd9b877, 0xc9a765, 0xead2a0][i % 3])));
  pebble.position.set((Math.random() - 0.5) * (CAGE_W - 0.6), 0.16, (Math.random() - 0.5) * (CAGE_D - 0.6));
  pebble.rotation.set(Math.random(), Math.random(), Math.random());
  cage.add(pebble);
}

// Wire bars (vertical) + top/bottom rims
const barMat = mat(0x9aa7b5, { metalness: 0.6, roughness: 0.4 });
const barGeo = new THREE.CylinderGeometry(0.045, 0.045, CAGE_H, 5);
const rimGeoH = new THREE.BoxGeometry(CAGE_W + 0.1, 0.09, 0.09);
const rimGeoV = new THREE.BoxGeometry(0.09, 0.09, CAGE_D + 0.1);

function addBarsAlong(axis) {
  const n = 17;
  for (let i = 0; i <= n; i++) {
    const t = -1 + (2 * i) / n;
    const bar = new THREE.Mesh(barGeo, barMat);
    bar.position.y = CAGE_H / 2 + 0.1;
    if (axis === 'z') { bar.position.x = t * (CAGE_W / 2); bar.position.z = (i % 2 ? 1 : -1) * (CAGE_D / 2); }
    else              { bar.position.z = t * (CAGE_D / 2); bar.position.x = (i % 2 ? 1 : -1) * (CAGE_W / 2); }
    cage.add(bar);
  }
}
addBarsAlong('z');
addBarsAlong('x');

for (const y of [0.15, CAGE_H + 0.1]) {
  for (const s of [1, -1]) {
    const rimX = new THREE.Mesh(rimGeoH, barMat);
    rimX.position.set(0, y, s * (CAGE_D / 2));
    cage.add(rimX);
    const rimZ = new THREE.Mesh(rimGeoV, barMat);
    rimZ.position.set(s * (CAGE_W / 2), y, 0);
    cage.add(rimZ);
  }
}

/* ============================================================
   INTERACTIVE OBJECTS
============================================================ */
// --- Exercise wheel (against back-right corner) ---
const wheelGroup = new THREE.Group();
wheelGroup.position.set(2.4, 0, -2.6);
scene.add(wheelGroup);

const wheelSpin = new THREE.Group(); // this part rotates
wheelGroup.add(wheelSpin);

const ring = shadowed(new THREE.Mesh(
  new THREE.TorusGeometry(1.0, 0.14, 6, 18), mat(0x7ec8e3)));
ring.position.y = 1.35;
wheelSpin.add(ring);

// Spokes
for (let i = 0; i < 6; i++) {
  const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.9, 5), mat(0x5aa9c9));
  spoke.position.y = 1.35;
  spoke.rotation.z = (i / 6) * Math.PI;
  wheelSpin.add(spoke);
}
const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.3, 6), mat(0x5aa9c9));
hub.rotation.x = Math.PI / 2;
hub.position.y = 1.35;
wheelSpin.add(hub);

// Stand
const standL = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.9, 0.4), mat(0x5aa9c9)));
standL.position.set(0, 0.45, 0.25);
const standR = standL.clone(); standR.position.z = -0.25;
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.7, 6), mat(0x4a8fa9));
axle.rotation.x = Math.PI / 2;
axle.position.y = 1.35;
wheelGroup.add(standL, standR, axle);

let wheelSpeed = 0;      // current spin speed (rad/s)
let wheelBoost = 0;      // extra boost from clicking

// --- Food bowl (front-left) ---
const bowlPos = new THREE.Vector3(-2.6, 0, 2.4);
const bowl = new THREE.Group();
bowl.position.copy(bowlPos);
scene.add(bowl);

const dish = shadowed(new THREE.Mesh(
  new THREE.CylinderGeometry(0.55, 0.35, 0.28, 8), mat(0xffb347)));
dish.position.y = 0.28;
bowl.add(dish);
for (let i = 0; i < 9; i++) {
  const seed = shadowed(new THREE.Mesh(
    new THREE.SphereGeometry(0.09, 5, 4), mat(0x8d5524)));
  const a = Math.random() * Math.PI * 2, r = Math.random() * 0.3;
  seed.position.set(Math.cos(a) * r, 0.44, Math.sin(a) * r);
  bowl.add(seed);
}

// --- Tunnel (middle) ---
const tunnel = new THREE.Group();
tunnel.position.set(0.2, 0, 0.8);
tunnel.rotation.y = Math.PI / 3;
scene.add(tunnel);

const tunnelBody = shadowed(new THREE.Mesh(
  new THREE.CylinderGeometry(0.55, 0.55, 2.4, 8, 1, false, 0, Math.PI),
  mat(0xa7e08a, { side: THREE.DoubleSide })));
tunnelBody.rotation.z = Math.PI / 2;
tunnelBody.position.y = 0.55;
tunnel.add(tunnelBody);

// --- Hay pile (decoration) ---
const hay = shadowed(new THREE.Mesh(
  new THREE.IcosahedronGeometry(0.7, 0), mat(0xd9b44a)));
hay.scale.set(1.3, 0.55, 1.1);
hay.position.set(-1.5, 0.2, -1.8);
scene.add(hay);

/* ============================================================
   HAMSTERS
============================================================ */
function makeHamster(bodyColor, bellyColor) {
  const g = new THREE.Group();

  const body = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.42, 8, 6), mat(bodyColor)));
  body.scale.set(1, 0.9, 1.25);
  body.position.y = 0.42;
  g.add(body);

  const belly = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.34, 8, 6), mat(bellyColor)));
  belly.scale.set(0.9, 0.8, 1.1);
  belly.position.set(0, 0.34, 0.1);
  g.add(belly);

  const head = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 6), mat(bodyColor)));
  head.position.set(0, 0.55, 0.48);
  g.add(head);

  // Cheeks
  for (const s of [1, -1]) {
    const cheek = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.13, 6, 5), mat(bellyColor)));
    cheek.position.set(s * 0.22, 0.45, 0.58);
    g.add(cheek);
  }

  // Ears
  for (const s of [1, -1]) {
    const ear = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.11, 6, 5), mat(bodyColor)));
    ear.position.set(s * 0.18, 0.82, 0.4);
    const inner = new THREE.Mesh(new THREE.SphereGeometry(0.06, 5, 4), mat(0xff9eb5));
    inner.position.set(s * 0.18, 0.84, 0.47);
    g.add(ear, inner);
  }

  // Eyes
  for (const s of [1, -1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.05, 6, 5), mat(0x222222, { roughness: 0.3 }));
    eye.position.set(s * 0.14, 0.6, 0.73);
    g.add(eye);
  }

  // Nose + mouth
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.045, 5, 4), mat(0xff7fa5));
  nose.position.set(0, 0.5, 0.78);
  g.add(nose);

  // Tiny feet
  for (const s of [1, -1]) {
    for (const f of [0.18, -0.18]) {
      const foot = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.09, 5, 4), mat(bellyColor)));
      foot.position.set(s * 0.2, 0.1, f);
      g.add(foot);
    }
  }

  // Tail nub
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.09, 5, 4), mat(bodyColor));
  tail.position.set(0, 0.42, -0.52);
  g.add(tail);

  g.userData.head = head;
  return g;
}

const HAMSTER_LOOKS = [
  [0xf5a65b, 0xfff1dc], // golden
  [0xbdb3a8, 0xffffff], // grey
  [0x8d6e4f, 0xf3e2c7], // brown
  [0xffd9a0, 0xffffff], // cream
];

const hamsters = [];
const BOUND = 3.2; // stay inside these x/z limits

for (let i = 0; i < 4; i++) {
  const [c1, c2] = HAMSTER_LOOKS[i];
  const h = makeHamster(c1, c2);
  h.position.set((Math.random() - 0.5) * 4, 0, (Math.random() - 0.5) * 4);
  h.rotation.y = Math.random() * Math.PI * 2;
  scene.add(h);

  hamsters.push({
    mesh: h,
    state: 'wander',
    target: randomPoint(),
    timer: 1 + Math.random() * 3,
    speed: 0.9 + Math.random() * 0.5,
    phase: Math.random() * 10,
  });
}

function randomPoint() {
  return new THREE.Vector3(
    (Math.random() * 2 - 1) * BOUND, 0, (Math.random() * 2 - 1) * BOUND);
}

const WHEEL_POINT = new THREE.Vector3(2.4, 0, -1.2); // in front of the wheel
const BOWL_POINT  = new THREE.Vector3(-2.6, 0, 1.5); // in front of the bowl

function smoothTurn(obj, targetAngle, dt, rate = 6) {
  let diff = targetAngle - obj.rotation.y;
  while (diff > Math.PI) diff -= Math.PI * 2;
  while (diff < -Math.PI) diff += Math.PI * 2;
  obj.rotation.y += diff * Math.min(1, dt * rate);
}

/* ============================================================
   BEHAVIOR STATE MACHINE
============================================================ */
function updateHamster(h, dt, t) {
  const m = h.mesh;
  h.timer -= dt;

  switch (h.state) {

    case 'wander': {
      const to = h.target.clone().sub(m.position);
      to.y = 0;
      const dist = to.length();
      if (dist < 0.25) {
        // Arrived: pause, or maybe go do something fun
        const roll = Math.random();
        if (roll < 0.25) { h.state = 'toWheel'; h.target = WHEEL_POINT.clone(); }
        else if (roll < 0.45) { h.state = 'toBowl'; h.target = BOWL_POINT.clone(); }
        else { h.state = 'pause'; h.timer = 0.8 + Math.random() * 2.5; }
        break;
      }
      to.normalize();
      m.position.addScaledVector(to, h.speed * dt);
      smoothTurn(m, Math.atan2(to.x, to.z), dt);
      // Walk bob + lean
      m.position.y = Math.abs(Math.sin(t * 9 + h.phase)) * 0.06;
      m.userData.head.rotation.x = 0.1;
      break;
    }

    case 'pause': {
      m.position.y = Math.sin(t * 3 + h.phase) * 0.02; // gentle breathing
      m.userData.head.rotation.x = Math.sin(t * 5 + h.phase) * 0.15; // sniffing
      if (h.timer <= 0) { h.state = 'wander'; h.target = randomPoint(); }
      break;
    }

    case 'toWheel':
    case 'toBowl': {
      const to = h.target.clone().sub(m.position);
      to.y = 0;
      const dist = to.length();
      if (dist < 0.3) {
        h.state = h.state === 'toWheel' ? 'wheel' : 'eat';
        h.timer = 3 + Math.random() * 3;
        break;
      }
      to.normalize();
      m.position.addScaledVector(to, h.speed * 1.1 * dt);
      smoothTurn(m, Math.atan2(to.x, to.z), dt);
      m.position.y = Math.abs(Math.sin(t * 10 + h.phase)) * 0.06;
      break;
    }

    case 'wheel': {
      // Face the wheel and run in place!
      const toWheel = WHEEL_POINT.clone().sub(m.position);
      smoothTurn(m, Math.atan2(toWheel.x, toWheel.z), dt, 3);
      m.position.y = Math.abs(Math.sin(t * 14 + h.phase)) * 0.09;
      m.userData.head.rotation.x = -0.25; // looking up at wheel
      wheelSpeed = Math.max(wheelSpeed, 4); // hamster powers the wheel
      if (h.timer <= 0) { h.state = 'wander'; h.target = randomPoint(); }
      break;
    }

    case 'eat': {
      const toBowl = BOWL_POINT.clone().sub(m.position);
      smoothTurn(m, Math.atan2(toBowl.x, toBowl.z), dt, 3);
      m.position.y = 0;
      m.userData.head.rotation.x = 0.45 + Math.sin(t * 8) * 0.2; // nom nom
      if (h.timer <= 0) { h.state = 'wander'; h.target = randomPoint(); }
      break;
    }
  }

  // Keep inside the cage
  m.position.x = THREE.MathUtils.clamp(m.position.x, -BOUND, BOUND);
  m.position.z = THREE.MathUtils.clamp(m.position.z, -BOUND, BOUND);
}

/* ============================================================
   CLICK THE WHEEL (raycast)
============================================================ */
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
renderer.domElement.addEventListener('pointerdown', (e) => {
  pointer.x = (e.clientX / innerWidth) * 2 - 1;
  pointer.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  if (raycaster.intersectObject(wheelGroup, true).length > 0) {
    wheelBoost = 14; // turbo spin!
  }
});

/* ============================================================
   MAIN LOOP
============================================================ */
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  for (const h of hamsters) updateHamster(h, dt, t);

  // Wheel physics: boost decays, natural spin decays slowly
  wheelBoost *= Math.pow(0.25, dt);
  wheelSpeed *= Math.pow(0.55, dt);
  if (wheelSpeed < 0.01 && wheelBoost < 0.01) wheelSpeed = 0;
  wheelSpin.rotation.x -= (wheelSpeed + wheelBoost) * dt;

  controls.update();
  renderer.render(scene, camera);
}
animate();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## What you get

**The scene:**
- 🏠 **Cage** — pink base tray, wood-shaving floor with scattered pebbles, and a full grid of low-poly wire bars with rims
- 🎡 **Exercise wheel** — the star interactive object (spokes, hub, stand)
- 🥣 **Food bowl** with seeds, a green **tunnel**, and a **hay pile**

**The hamsters (4 of them):**
- Golden, grey, brown, and cream — each built from low-segment spheres with cheeks, inner ears, tiny feet, and a tail nub
- **Autonomous state machine**: `wander → pause (sniffing) → wander`, plus they randomly decide to go `run on the wheel` (which actually spins it!) or `eat at the bowl` (head bobs nom-nom style)
- Walking bob animation, smooth turning, and breathing while idle

**Interactivity:**
- Orbit/zoom camera with damping
- **Click the wheel** for a turbo-spin boost (decays naturally)
- Hamsters running on the wheel power it in real time

The code is organized into clearly labeled sections (setup, cage, objects, hamsters, behavior, loop) so it's easy to read and tweak — try changing `HAMSTER_LOOKS` colors or the `BOUND` size.