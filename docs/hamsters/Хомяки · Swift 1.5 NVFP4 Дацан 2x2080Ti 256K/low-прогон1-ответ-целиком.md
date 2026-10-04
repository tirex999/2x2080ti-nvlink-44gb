Here is the complete single-file project. Save it as `index.html` and open it in any modern browser — no build step, no dependencies beyond the Three.js CDN import map.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #ffe9d6; font-family: system-ui, sans-serif; }
  #app { position: fixed; inset: 0; }
  .ui {
    position: fixed; left: 16px; top: 14px; color: #5a3a22;
    text-shadow: 0 1px 0 #fff; pointer-events: none; user-select: none;
  }
  .ui h1 { margin: 0; font-size: 20px; letter-spacing: .5px; }
  .ui p  { margin: 4px 0 0; font-size: 13px; opacity: .85; }
</style>
</head>
<body>
<div id="app"></div>
<div class="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate · Scroll to zoom · Click the wheel to spin it</p>
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

/* ------------------------------------------------------------------ *
 *  Basic scene setup
 * ------------------------------------------------------------------ */
const app = document.getElementById('app');

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9d6);
scene.fog = new THREE.Fog(0xffe9d6, 26, 48);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(9, 8, 11);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.4, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 6;
controls.maxDistance = 26;
controls.maxPolarAngle = Math.PI * 0.49; // don't go under the floor

/* ------------------------------------------------------------------ *
 *  Lighting
 * ------------------------------------------------------------------ */
scene.add(new THREE.HemisphereLight(0xfff3e0, 0xb08968, 0.9));

const sun = new THREE.DirectionalLight(0xffffff, 1.1);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 40;
const s = 12;
sun.shadow.camera.left = -s; sun.shadow.camera.right = s;
sun.shadow.camera.top = s;  sun.shadow.camera.bottom = -s;
sun.shadow.bias = -0.0005;
scene.add(sun);

/* ------------------------------------------------------------------ *
 *  Materials (low-poly = flat shading)
 * ------------------------------------------------------------------ */
const mat = (color, opts = {}) =>
  new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.85, metalness: 0.0, ...opts });

/* ------------------------------------------------------------------ *
 *  Tray / floor
 * ------------------------------------------------------------------ */
const TRAY = 9;            // half-size of the play area
const trayGroup = new THREE.Group();

const floor = new THREE.Mesh(new THREE.BoxGeometry(TRAY * 2, 0.6, TRAY * 2), mat(0xf3c58a));
floor.position.y = -0.3;
floor.receiveShadow = true;
trayGroup.add(floor);

// raised rim of the tray
const rimMat = mat(0xe08a4f);
const rimT = 0.6, rimH = 0.9;
[
  [0, -TRAY, TRAY * 2 + rimT, rimT],
  [0,  TRAY, TRAY * 2 + rimT, rimT],
  [-TRAY, 0, rimT, TRAY * 2 + rimT],
  [ TRAY, 0, rimT, TRAY * 2 + rimT],
].forEach(([x, z, w, d]) => {
  const rim = new THREE.Mesh(new THREE.BoxGeometry(w, rimH, d), rimMat);
  rim.position.set(x, rimH / 2, z);
  rim.castShadow = rim.receiveShadow = true;
  trayGroup.add(rim);
});

// a few soft "bedding" mounds for charm
for (let i = 0; i < 6; i++) {
  const mound = new THREE.Mesh(new THREE.IcosahedronGeometry(0.9 + Math.random() * 0.5, 0), mat(0xf6d3a3));
  mound.scale.y = 0.4;
  mound.position.set((Math.random() - 0.5) * 14, 0.15, (Math.random() - 0.5) * 14);
  mound.receiveShadow = true;
  trayGroup.add(mound);
}
scene.add(trayGroup);

/* ------------------------------------------------------------------ *
 *  Cage (bars + frame)
 * ------------------------------------------------------------------ */
const cage = new THREE.Group();
const barMat = mat(0x9b6bff, { roughness: 0.5 });
const frameMat = mat(0x6d4bd8);

function addBar(x, z) {
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 7, 6), barMat);
  bar.position.set(x, 3.5, z);
  bar.castShadow = true;
  cage.add(bar);
}
const N = 9;
for (let i = 0; i <= N; i++) {
  const t = -TRAY + (i / N) * TRAY * 2;
  addBar(t, -TRAY); addBar(t, TRAY);
  addBar(-TRAY, t); addBar(TRAY, t);
}
// corner posts
[[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([sx, sz]) => {
  const post = new THREE.Mesh(new THREE.BoxGeometry(0.4, 7.4, 0.4), frameMat);
  post.position.set(sx * TRAY, 3.7, sz * TRAY);
  post.castShadow = true;
  cage.add(post);
});
// top frame
[
  [0, -TRAY, TRAY * 2 + 0.4, 0.4],
  [0,  TRAY, TRAY * 2 + 0.4, 0.4],
  [-TRAY, 0, 0.4, TRAY * 2 + 0.4],
  [ TRAY, 0, 0.4, TRAY * 2 + 0.4],
].forEach(([x, z, w, d]) => {
  const beam = new THREE.Mesh(new THREE.BoxGeometry(w, 0.4, d), frameMat);
  beam.position.set(x, 7.2, z);
  beam.castShadow = true;
  cage.add(beam);
});
scene.add(cage);

/* ------------------------------------------------------------------ *
 *  Interactive wheel
 * ------------------------------------------------------------------ */
const wheelGroup = new THREE.Group();
wheelGroup.position.set(5.5, 0, -4.5);
wheelGroup.rotation.y = Math.PI * 0.25;

// support stand
const standMat = mat(0x4ecdc4);
[-1, 1].forEach(side => {
  const leg = new THREE.Mesh(new THREE.BoxGeometry(0.3, 3.4, 0.3), standMat);
  leg.position.set(0, 1.7, side * 1.4);
  leg.castShadow = true;
  wheelGroup.add(leg);
});
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 3.0, 8), standMat);
axle.rotation.x = Math.PI / 2;
axle.position.y = 2.6;
wheelGroup.add(axle);

// the spinning wheel itself (ring + spokes)
const wheel = new THREE.Group();
wheel.position.y = 2.6;
const ring = new THREE.Mesh(new THREE.TorusGeometry(1.7, 0.35, 6, 18), mat(0xff6b6b));
ring.castShadow = true;
wheel.add(ring);
for (let i = 0; i < 6; i++) {
  const spoke = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.12, 0.12), mat(0xffd166));
  spoke.rotation.z = (i / 6) * Math.PI;
  wheel.add(spoke);
}
wheelGroup.add(wheel);
scene.add(wheelGroup);

// world position of the running spot on top of the wheel
const wheelRunSpot = new THREE.Vector3();
function updateWheelSpot() {
  const local = new THREE.Vector3(0, 1.7 + 0.35, 0); // top of the ring
  wheelGroup.localToWorld(local);
  wheelRunSpot.copy(local);
}

/* ------------------------------------------------------------------ *
 *  Food bowl (extra charm object)
 * ------------------------------------------------------------------ */
const bowl = new THREE.Group();
bowl.position.set(-4.5, 0, 3.5);
const bowlBase = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 0.7, 0.6, 10), mat(0x06d6a0));
bowlBase.position.y = 0.3; bowlBase.castShadow = true; bowl.add(bowlBase);
for (let i = 0; i < 8; i++) {
  const seed = new THREE.Mesh(new THREE.IcosahedronGeometry(0.16, 0), mat(0xc77dff));
  seed.position.set((Math.random()-0.5)*1.2, 0.62, (Math.random()-0.5)*1.2);
  bowl.add(seed);
}
scene.add(bowl);

/* ------------------------------------------------------------------ *
 *  Hamster factory (low-poly)
 * ------------------------------------------------------------------ */
function createHamster(color) {
  const g = new THREE.Group();
  const bodyMat = mat(color);
  const bellyMat = mat(0xfff1e6);

  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.7, 0), bodyMat);
  body.scale.set(1.1, 0.95, 1.25);
  body.position.y = 0.7;
  body.castShadow = true;
  g.add(body);

  const belly = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 0), bellyMat);
  belly.scale.set(0.9, 0.8, 1.0);
  belly.position.set(0, 0.62, 0.35);
  g.add(belly);

  // head
  const head = new THREE.Group();
  head.position.set(0, 0.95, 0.85);
  const skull = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 0), bodyMat);
  skull.castShadow = true;
  head.add(skull);

  const earGeo = new THREE.ConeGeometry(0.18, 0.3, 5);
  [-1, 1].forEach(sx => {
    const ear = new THREE.Mesh(earGeo, mat(0xffb4a2));
    ear.position.set(sx * 0.28, 0.35, -0.05);
    ear.rotation.z = sx * 0.3;
    head.add(ear);
  });

  const eyeGeo = new THREE.SphereGeometry(0.07, 6, 6);
  [-1, 1].forEach(sx => {
    const eye = new THREE.Mesh(eyeGeo, mat(0x222222));
    eye.position.set(sx * 0.2, 0.08, 0.36);
    head.add(eye);
  });
  const nose = new THREE.Mesh(new THREE.IcosahedronGeometry(0.08, 0), mat(0xff6b6b));
  nose.position.set(0, -0.02, 0.42);
  head.add(nose);
  g.add(head);

  // little legs (animated while walking)
  const legs = [];
  const legGeo = new THREE.BoxGeometry(0.16, 0.3, 0.16);
  [[-0.4, 0.45],[0.4, 0.45],[-0.4, -0.45],[0.4, -0.45]].forEach(([x, z]) => {
    const leg = new THREE.Mesh(legGeo, bodyMat);
    leg.position.set(x, 0.18, z);
    leg.castShadow = true;
    g.add(leg);
    legs.push(leg);
  });

  // tail stub
  const tail = new THREE.Mesh(new THREE.IcosahedronGeometry(0.12, 0), bodyMat);
  tail.position.set(0, 0.7, -0.85);
  g.add(tail);

  g.userData = { head, legs, body };
  return g;
}

/* ------------------------------------------------------------------ *
 *  Hamster autonomous behaviour (state machine)
 * ------------------------------------------------------------------ */
const COLORS = [0xd9a066, 0xf4f1de, 0x9c89b8, 0xa47148];
const hamsters = [];

function makeTarget() {
  const r = TRAY - 1.5;
  return new THREE.Vector3((Math.random()*2-1)*r, 0, (Math.random()*2-1)*r);
}

function angleLerp(a, b, t) {
  let d = b - a;
  while (d > Math.PI) d -= Math.PI * 2;
  while (d < -Math.PI) d += Math.PI * 2;
  return a + d * t;
}

for (let i = 0; i < COLORS.length; i++) {
  const h = createHamster(COLORS[i]);
  h.position.copy(makeTarget());
  h.rotation.y = Math.random() * Math.PI * 2;
  scene.add(h);
  hamsters.push({
    mesh: h,
    state: 'pause',
    timer: 0.5 + Math.random(),
    target: makeTarget(),
    speed: 1.4 + Math.random() * 0.6,
    isRunner: i === 0,           // first hamster loves the wheel
    runTimer: 0,
    phase: Math.random() * 10,
  });
}

const WHEEL_POS = wheelGroup.position;

function updateHamster(h, dt) {
  const m = h.mesh;
  const legs = m.userData.legs;
  const head = m.userData.head;

  // ---- state transitions ----
  h.timer -= dt;

  if (h.isRunner) {
    // runner cycle: wander -> toWheel -> onWheel -> wander ...
    if (h.state === 'pause' && h.timer <= 0) {
      h.state = Math.random() < 0.5 ? 'toWheel' : 'walk';
      h.target = makeTarget();
      h.timer = 2 + Math.random() * 2;
    }
  } else if (h.state === 'pause' && h.timer <= 0) {
    h.state = 'walk';
    h.target = makeTarget();
    h.timer = 2.5 + Math.random() * 3;
  }

  if (h.state === 'toWheel') {
    const dir = new THREE.Vector3().subVectors(WHEEL_POS, m.position); dir.y = 0;
    const dist = dir.length();
    m.rotation.y = angleLerp(m.rotation.y, Math.atan2(dir.x, dir.z), 0.1);
    if (dist > 1.2) {
      dir.normalize();
      m.position.addScaledVector(dir, h.speed * dt);
      animateLegs(legs, h, dt, true);
    } else {
      h.state = 'onWheel';
      h.runTimer = 4 + Math.random() * 3;
    }
  }
  else if (h.state === 'onWheel') {
    // snap onto the running spot
    updateWheelSpot();
    m.position.lerp(wheelRunSpot, 0.25);
    m.rotation.y = angleLerp(m.rotation.y, wheelGroup.rotation.y + Math.PI/2, 0.2);
    animateLegs(legs, h, dt, true, 2.2);
    m.userData.body.position.y = 0.7 + Math.sin(h.phase * 14) * 0.04;
    wheelSpinBoost += dt * 6;     // running spins the wheel
    h.runTimer -= dt;
    if (h.runTimer <= 0) { h.state = 'pause'; h.timer = 1 + Math.random(); h.target = makeTarget(); }
  }
  else if (h.state === 'walk') {
    const dir = new THREE.Vector3().subVectors(h.target, m.position); dir.y = 0;
    if (dir.length() < 0.6) {
      h.state = 'pause'; h.timer = 0.8 + Math.random() * 1.8; h.target = makeTarget();
    } else {
      m.rotation.y = angleLerp(m.rotation.y, Math.atan2(dir.x, dir.z), 0.08);
      dir.normalize();
      m.position.addScaledVector(dir, h.speed * dt);
      animateLegs(legs, h, dt, true);
    }
  }
  else { // pause: idle wiggle
    animateLegs(legs, h, dt, false);
    head.rotation.z = Math.sin(h.phase * 6) * 0.08;
    m.userData.body.position.y = 0.7 + Math.sin(h.phase * 4) * 0.03;
    if (h.timer <= 0) {
      h.state = 'walk'; h.target = makeTarget(); h.timer = 2.5 + Math.random() * 3;
    }
  }

  // keep inside the tray
  const lim = TRAY - 0.8;
  m.position.x = THREE.MathUtils.clamp(m.position.x, -lim, lim);
  m.position.z = THREE.MathUtils.clamp(m.position.z, -lim, lim);
}

function animateLegs(legs, h, dt, walking, speedMul = 1) {
  h.phase += dt * (walking ? 10 * speedMul : 3);
  legs.forEach((leg, i) => {
    const swing = walking ? Math.sin(h.phase + (i % 2 === 0 ? 0 : Math.PI)) * 0.5 : 0;
    leg.rotation.x = swing;
  });
}

/* ------------------------------------------------------------------ *
 *  Click the wheel to spin it
 * ------------------------------------------------------------------ */
let wheelSpinBoost = 0;
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
renderer.domElement.addEventListener('pointerdown', (e) => {
  pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
  pointer.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObject(wheel, true);
  if (hits.length) wheelSpinBoost += 14;
});

/* ------------------------------------------------------------------ *
 *  Loop
 * ------------------------------------------------------------------ */
const clock = new THREE.Clock();
function tick() {
  const dt = Math.min(clock.getDelta(), 0.05);

  for (const h of hamsters) updateHamster(h, dt);

  // wheel: decay spin boost, keep a gentle idle spin
  wheelSpinBoost = THREE.MathUtils.lerp(wheelSpinBoost, 0, dt * 1.5);
  wheel.rotation.z += (0.4 + wheelSpinBoost) * dt;

  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}
tick();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

### What you get
- **Scene:** a sandy tray with a raised rim and bedding mounds, a colorful cage made of vertical bars, corner posts and a top frame.
- **Hamsters:** four low-poly hamsters built from faceted icosahedra/cones (body, belly, head, ears, eyes, nose, animated legs, tail) in tan, cream, purple-gray and brown, all with flat shading for the cute low-poly look.
- **Autonomous behavior:** a small state machine per hamster — `walk` toward random targets, `pause` and wiggle, turn smoothly (shortest-angle lerp), and stay clamped inside the tray.
- **Interactive object:** the running wheel. One "runner" hamster periodically walks to it, hops on, runs (spinning the wheel), then dismounts. You can also **click the wheel** to give it a spin boost.
- **Controls:** OrbitControls (drag to rotate, scroll to zoom, damped, with sensible limits so you can't go under the floor).

### Notes
- Uses an import map with Three.js r160 from unpkg, so it runs straight from a file in any modern browser (Chrome/Edge/Firefox/Safari).
- Tuning knobs are easy to find: `TRAY` for cage size, `COLORS` for hamster roster, `h.speed` and the state timers for pacing, and `wheelSpinBoost` for wheel feel.

If you'd like, I can add a second interactive object (a tunnel the hamsters walk through), a day/night lighting toggle, or a "drop food" click that makes hamsters gather at the bowl.