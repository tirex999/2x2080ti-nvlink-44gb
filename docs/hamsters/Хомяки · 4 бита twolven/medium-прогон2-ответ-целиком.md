

# 🐹 Low-Poly Hamster Playground

A single-file Three.js scene: a wire-bar cage on a sunny meadow, four waddling hamsters with their own little schedules (wander → pause → go eat seeds → repeat), one dedicated hamster who never stops running the pink wheel, a seed bowl, and a purple hidey-hole.

Save as `index.html` and open in any modern browser (needs internet for the Three.js CDN).

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; font-family: 'Segoe UI', system-ui, sans-serif; }
  #app { position: fixed; inset: 0; }
  .hud { position: fixed; top: 16px; left: 50%; transform: translateX(-50%); text-align: center; pointer-events: none; z-index: 10; }
  .hud h1 { margin: 0; font-size: 26px; color: #4a3b6b; text-shadow: 0 2px 0 rgba(255,255,255,.75); }
  .hud p { margin: 4px 0 0; font-size: 13px; color: #5d5480; text-shadow: 0 1px 0 rgba(255,255,255,.6); }
</style>
<script type="importmap">
{ "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>
</head>
<body>
<div id="app"></div>
<div class="hud">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>drag to orbit &middot; scroll to zoom &middot; one of them is always on the wheel</p>
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ---------- renderer / scene / camera ---------- */
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#cdeaff');
scene.fog = new THREE.Fog('#cdeaff', 18, 42);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 100);
camera.position.set(7.5, 6, 9.5);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 5;
controls.maxDistance = 22;
controls.maxPolarAngle = Math.PI * 0.49;

/* ---------- lights ---------- */
scene.add(new THREE.HemisphereLight('#ffffff', '#ffd9e8', 0.85));
const sun = new THREE.DirectionalLight('#fff3df', 1.6);
sun.position.set(6, 10, 4);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -7; sun.shadow.camera.right = 7;
sun.shadow.camera.top = 7;   sun.shadow.camera.bottom = -7;
sun.shadow.camera.near = 2; sun.shadow.camera.far = 25;
scene.add(sun);

/* ---------- helpers ---------- */
const M = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, flatShading: true, roughness: .95, metalness: 0, ...o });

/* ---------- ground, trees, flowers ---------- */
const ground = new THREE.Mesh(new THREE.CylinderGeometry(15, 15, 0.3, 28), M('#b7e3a1'));
ground.position.y = -0.15;
ground.receiveShadow = true;
scene.add(ground);

function tree(x, z, s = 1) {
  const g = new THREE.Group();
  const t = new THREE.Mesh(new THREE.CylinderGeometry(.09 * s, .13 * s, .55 * s, 6), M('#a5713f'));
  t.position.y = .27 * s; t.castShadow = true; g.add(t);
  const c = new THREE.Mesh(new THREE.ConeGeometry(.6 * s, 1.2 * s, 7), M('#5fb878'));
  c.position.y = 1.05 * s; c.castShadow = true; g.add(c);
  g.position.set(x, 0, z);
  scene.add(g);
}
tree(-7.6, -4, 1.5); tree(7.2, -5, 1.8); tree(6.6, 4.6, 1.15); tree(-7, 3.2, 1.25);

function flower(x, z, c) {
  const g = new THREE.Group();
  const st = new THREE.Mesh(new THREE.CylinderGeometry(.02, .02, .26, 5), M('#7cc47f'));
  st.position.y = .13; g.add(st);
  const p = new THREE.Mesh(new THREE.SphereGeometry(.09, 6, 5), M(c));
  p.position.y = .31; p.scale.y = .65; g.add(p);
  g.position.set(x, 0, z);
  scene.add(g);
}
flower(-5.8, 1.5, '#ff7bac'); flower(-6.4, -1.2, '#ffd166'); flower(5.2, -2.6, '#c792ea');
flower(4.8, 2.3, '#ff7bac'); flower(-5.4, 3.6, '#ffd166'); flower(2.5, -5.6, '#c792ea');

/* ---------- cage: tray, bedding, wire bars ---------- */
const FLOOR = 0.68; // top of the bedding

const tray = new THREE.Mesh(new THREE.BoxGeometry(8.4, 0.5, 6.4), M('#f6c453'));
tray.position.y = 0.25;
tray.castShadow = tray.receiveShadow = true;
scene.add(tray);

const bedding = new THREE.Mesh(new THREE.BoxGeometry(8.15, 0.18, 6.15), M('#ffe3a8'));
bedding.position.y = 0.59;
bedding.receiveShadow = true;
scene.add(bedding);

const cage = new THREE.Group();
const barGeo = new THREE.CylinderGeometry(0.035, 0.035, 2.4, 5);
const barMat = M('#7c8aa0', { roughness: .5, metalness: .4 });
function bar(x, z) {
  const m = new THREE.Mesh(barGeo, barMat);
  m.position.set(x, 1.7, z);
  return m;
}
for (let x = -4; x <= 4.01; x += 0.66) { cage.add(bar(x, -3.1), bar(x, 3.1)); }
for (let z = -3.1; z <= 3.11; z += 0.66) { cage.add(bar(-4.1, z), bar(4.1, z)); }

const railMat = M('#5d6b82', { roughness: .5, metalness: .4 });
function rail(w, d, x, z, y) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, 0.09, d), railMat);
  m.position.set(x, y, z);
  return m;
}
cage.add(rail(8.4, .1, 0, -3.1, 2.9), rail(8.4, .1, 0, 3.1, 2.9), rail(.1, 6.4, -4.1, 0, 2.9), rail(.1, 6.4, 4.1, 0, 2.9));
cage.add(rail(8.4, .06, 0, -3.1, 1.5), rail(8.4, .06, 0, 3.1, 1.5), rail(.06, 6.4, -4.1, 0, 1.5), rail(.06, 6.4, 4.1, 0, 1.5));
scene.add(cage);

/* ---------- interactive object 1: the wheel ---------- */
const wheel = new THREE.Group();
const wMat = M('#ff8fa3', { roughness: .7 });
wheel.add(new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.07, 6, 14), wMat));
const spokeGeo = new THREE.CylinderGeometry(0.03, 0.03, 1.24, 5);
for (let i = 0; i < 5; i++) {
  const s = new THREE.Mesh(spokeGeo, wMat);
  s.rotation.z = i * Math.PI / 2.5;
  wheel.add(s);
}
const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.22, 8), M('#ffd166'));
hub.rotation.x = Math.PI / 2;
wheel.add(hub);
wheel.position.set(-2.7, 1.35, -2.55);
scene.add(wheel);

/* ---------- hamster model ---------- */
function makeHamster(fur, accent) {
  const g = new THREE.Group();
  const f = M(fur), a = M(accent);

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 7), f);
  body.scale.set(1, 0.85, 1.25);
  body.position.set(0, 0.3, -0.05);
  g.add(body);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.24, 8, 7), f);
  head.scale.set(1, 0.95, 1);
  head.position.set(0, 0.42, 0.22);
  g.add(head);

  for (const s of [-1, 1]) {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.07, 6, 5), a);
    e.scale.set(1, 1, 0.6);
    e.position.set(0.13 * s, 0.62, 0.18);
    g.add(e);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.032, 6, 5), M('#2b2b2b', { roughness: .3 }));
    eye.position.set(0.09 * s, 0.45, 0.43);
    g.add(eye);
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), M('#ffc2cd'));
    cheek.scale.set(1, 0.6, 0.5);
    cheek.position.set(0.16 * s, 0.36, 0.4);
    g.add(cheek);
  }
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.03, 6, 5), M('#ff9db0'));
  nose.position.set(0, 0.38, 0.46);
  g.add(nose);

  for (const [x, z] of [[-0.14, 0.12], [0.14, 0.12], [-0.14, -0.22], [0.14, -0.22]]) {
    const ft = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), a);
    ft.scale.set(1, 0.5, 1.4);
    ft.position.set(x, 0.06, z);
    g.add(ft);
  }
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.05, 6, 5), a);
  tail.position.set(0, 0.28, -0.36);
  g.add(tail);

  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  return g;
}

/* ---------- interactive object 2: seed bowl ---------- */
const bowl = new THREE.Group();
const b = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.3, 0.24, 10), M('#6ec6ff'));
b.position.y = 0.12; b.castShadow = true;
bowl.add(b);
for (let i = 0; i < 7; i++) {
  const s = new THREE.Mesh(new THREE.SphereGeometry(0.055, 5, 4), M('#a06a3a'));
  const ang = i / 7 * Math.PI * 2;
  s.position.set(Math.cos(ang) * 0.2, 0.25, Math.sin(ang) * 0.2);
  bowl.add(s);
}
bowl.position.set(2.5, FLOOR, 1.5);
scene.add(bowl);

/* ---------- hidey hole ---------- */
const den = new THREE.Group();
const db = new THREE.Mesh(new THREE.BoxGeometry(1, 0.75, 0.85), M('#b39ddb'));
db.position.y = 0.375; db.castShadow = db.receiveShadow = true;
den.add(db);
const roof = new THREE.Mesh(new THREE.ConeGeometry(0.75, 0.4, 4), M('#9b7fd4'));
roof.position.y = 0.95; roof.rotation.y = Math.PI / 4;
den.add(roof);
const hole = new THREE.Mesh(new THREE.CircleGeometry(0.18, 12), M('#4a3b6b'));
hole.position.set(0, 0.32, 0.43);
den.add(hole);
den.position.set(-2.4, FLOOR, 1.7);
den.rotation.y = 0.5;
scene.add(den);

/* ---------- the running hamster ---------- */
const runner = makeHamster('#ffb35c', '#ffd9a8');
runner.position.set(-2.7, FLOOR, -2.25);
runner.rotation.y = Math.PI; // face the wheel
scene.add(runner);

/* ---------- the four wandering hamsters ---------- */
const hamsters = [];
const palette = [
  ['#ffb35c', '#ffd9a8'],
  ['#f5e6d3', '#fff6ea'],
  ['#9aa3ad', '#d7dde3'],
  ['#ffffff', '#ffe9f0'],
];
palette.forEach(([fur, acc], i) => {
  const h = makeHamster(fur, acc);
  const ang = i / 4 * Math.PI * 2 + 0.6;
  h.position.set(Math.cos(ang) * 2, FLOOR, Math.sin(ang) * 1.4);
  scene.add(h);
  hamsters.push({
    mesh: h, state: 'idle', t: 0.4 + i * 0.5,
    target: new THREE.Vector3(),
    speed: 0.7 + Math.random() * 0.3,
    phase: Math.random() * 10, legT: 0,
  });
});

/* ---------- autonomous behaviour ---------- */
const BOWL_POS = new THREE.Vector3(2.5, 0, 1.5);
const WHEEL_POS = new THREE.Vector3(-2.7, 0, -2.55);
const DEN_POS = new THREE.Vector3(-2.4, 0, 1.7);
const BOUND = { x: 3.7, z: 2.7 };

function wrapAngle(a) { while (a > Math.PI) a -= Math.PI * 2; while (a < -Math.PI) a += Math.PI * 2; return a; }

function pickTarget(h) {
  const v = new THREE.Vector3();
  if (Math.random() < 0.35) { // snack time!
    v.copy(BOWL_POS);
    v.x += (Math.random() - 0.5) * 0.5;
    v.z += (Math.random() - 0.5) * 0.5;
  } else {
    v.set((Math.random() * 2 - 1) * BOUND.x, 0, (Math.random() * 2 - 1) * BOUND.z);
  }
  if (v.distanceTo(WHEEL_POS) < 1.1) v.x += 1.5;
  if (v.distanceTo(DEN_POS) < 0.8) v.z -= 1.0;
  h.target.copy(v);
}

function updateHamster(h, dt, t) {
  const m = h.mesh;
  h.t -= dt;

  if (h.state === 'idle') {
    m.rotation.z *= Math.max(0, 1 - dt * 5);
    if (h.t <= 0) { pickTarget(h); h.state = 'walk'; }

  } else if (h.state === 'walk') {
    const dx = h.target.x - m.position.x, dz = h.target.z - m.position.z;
    const d = Math.hypot(dx, dz);
    if (d < 0.35) {
      if (h.target.distanceTo(BOWL_POS) < 0.65) { h.state = 'eat'; h.t = 2 + Math.random(); }
      else { h.state = 'idle'; h.t = 0.8 + Math.random() * 2.2; }
    } else {
      const dir = Math.atan2(dx, dz);
      m.rotation.y += wrapAngle(dir - m.rotation.y) * Math.min(1, dt * 5);
      m.position.x += Math.sin(m.rotation.y) * h.speed * dt;
      m.position.z += Math.cos(m.rotation.y) * h.speed * dt;

      // steer around the wheel
      const wx = m.position.x - WHEEL_POS.x, wz = m.position.z - WHEEL_POS.z;
      const wd = Math.hypot(wx, wz);
      if (wd < 0.9 && wd > 0.001) { m.position.x += (wx / wd) * 0.02; m.position.z += (wz / wd) * 0.02; }
      // steer around the hidey hole
      const hx = m.position.x - DEN_POS.x, hz = m.position.z - DEN_POS.z;
      const hd = Math.hypot(hx, hz);
      if (hd < 0.75 && hd > 0.001) { m.position.x += (hx / hd) * 0.02; m.position.z += (hz / hd) * 0.02; }

      m.position.x = THREE.MathUtils.clamp(m.position.x, -BOUND.x, BOUND.x);
      m.position.z = THREE.MathUtils.clamp(m.position.z, -BOUND.z, BOUND.z);

      // waddle!
      h.legT += dt * 9;
      m.rotation.z = Math.sin(h.legT) * 0.08;
      m.position.y = FLOOR + Math.abs(Math.sin(h.legT)) * 0.03;
    }

  } else if (h.state === 'eat') {
    const dir = Math.atan2(BOWL_POS.x - m.position.x, BOWL_POS.z - m.position.z);
    m.rotation.y += wrapAngle(dir - m.rotation.y) * Math.min(1, dt * 4);
    m.position.y = FLOOR + 0.02 + Math.sin(t * 9 + h.phase) * 0.05; // munch munch
    m.rotation.z = Math.sin(t * 9 + h.phase) * 0.05;
    if (h.t <= 0) { h.state = 'idle'; h.t = 1 + Math.random() * 2; }
  }
}

/* ---------- main loop ---------- */
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  wheel.rotation.z -= dt * 5.5; // the eternal runner
  runner.position.y = FLOOR + Math.sin(t * 11) * 0.035;
  runner.rotation.z = Math.sin(t * 11) * 0.07;

  for (const h of hamsters) updateHamster(h, dt, t);

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

## What's inside

| Requirement | How it's covered |
|---|---|
| Three.js, one file | ES-module import map → `three@0.160.0` CDN, everything in `index.html` |
| Camera rotation | Damped `OrbitControls`, clamped zoom/polar angle |
| Cage + tray | Yellow tray, beige bedding layer, ~46 flat-shaded wire bars with top/mid rails |
| Several low-poly hamsters | 4 distinct colors (orange, cream, gray, white), built from flat-shaded spheres: blob body, head, ears, eyes, pink nose, cheek blush, stubby feet, tail nub |
| Interactive object | **Spinning pink wheel** (torus + 5 spokes + hub) with a dedicated hamster standing in it, bobbing forever — plus a **seed bowl** the others visit to "eat" |
| Autonomous behavior | Per-hamster state machine: `idle` → `walk` (smooth turning, waddling bob, boundary clamps, steering around wheel/hideout) → `eat` (turns to bowl, head-bob munching) → `idle`. Each has its own speed, phase, and random targets |
| Cute / low-poly / colorful | `flatShading: true` everywhere, pastel palette, round meadow, low-poly trees, flowers, purple hidey-hole with a dark door hole, soft shadows, gentle fog |
| Stable & readable | Small helper functions (`M`, `makeHamster`, `tree`, `flower`, `bar`, `rail`), one clearly commented section per feature, ~200 draw calls total — runs at 60fps on anything recent |