# Low-Poly Hamster Playground 🐹

A complete single-file project. Save it as `index.html` and open it in any modern browser — it loads Three.js from a CDN and runs immediately. Drag to orbit, scroll to zoom.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #1b2430; font-family: system-ui, sans-serif; }
  #app { position: fixed; inset: 0; }
  .ui {
    position: fixed; left: 16px; top: 14px; color: #fff; pointer-events: none;
    text-shadow: 0 2px 6px rgba(0,0,0,.5); user-select: none;
  }
  .ui h1 { margin: 0; font-size: 20px; letter-spacing: .5px; }
  .ui p  { margin: 4px 0 0; font-size: 13px; opacity: .85; }
  .legend {
    position: fixed; right: 14px; bottom: 12px; color: #fff; font-size: 12px;
    background: rgba(0,0,0,.35); padding: 8px 12px; border-radius: 10px;
    pointer-events: none; user-select: none; line-height: 1.5;
  }
</style>

<!-- Import map so we can use ES modules (Three.js + OrbitControls) straight from CDN -->
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>
<div id="app"></div>
<div class="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate • Scroll to zoom • The hamsters have a mind of their own</p>
</div>
<div class="legend">
  States: walk · pause · turn · run on wheel · snack at bowl
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================================================
   SCENE / RENDERER / CAMERA
   ============================================================ */
const app = document.getElementById('app');

const scene = new THREE.Scene();
scene.background = new THREE.Color('#cfe8ff');
scene.fog = new THREE.Fog('#cfe8ff', 26, 60);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 200);
camera.position.set(11, 9, 13);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.2, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 6;
controls.maxDistance = 30;
controls.maxPolarAngle = Math.PI * 0.49; // don't go under the floor

/* ============================================================
   LIGHTS
   ============================================================ */
scene.add(new THREE.HemisphereLight('#ffffff', '#8a6b4f', 0.9));

const sun = new THREE.DirectionalLight('#fff4e0', 1.1);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 40;
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12;  sun.shadow.camera.bottom = -12;
sun.shadow.bias = -0.0005;
scene.add(sun);

/* ============================================================
   HELPERS
   ============================================================ */
// Low-poly friendly material (flat shading + few segments = faceted look)
const mat = (color, opts = {}) =>
  new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.85, metalness: 0.0, ...opts });

const rand = (a, b) => a + Math.random() * (b - a);

/* ============================================================
   TRAY / BEDDING FLOOR
   ============================================================ */
const CAGE = { w: 14, d: 10, wallH: 0.9 }; // cage footprint

const tray = new THREE.Group();
scene.add(tray);

// bedding surface
const bedding = new THREE.Mesh(
  new THREE.BoxGeometry(CAGE.w, 0.6, CAGE.d),
  mat('#e7c084')
);
bedding.position.y = -0.3;
bedding.receiveShadow = true;
tray.add(bedding);

// scattered "wood shavings" (tiny low-poly boxes) for texture
const shavGeo = new THREE.BoxGeometry(0.5, 0.12, 0.18);
const shavMat = mat('#d3a35e');
for (let i = 0; i < 70; i++) {
  const s = new THREE.Mesh(shavGeo, shavMat);
  s.position.set(rand(-CAGE.w/2+1, CAGE.w/2-1), 0.02, rand(-CAGE.d/2+1, CAGE.d/2-1));
  s.rotation.y = rand(0, Math.PI);
  s.receiveShadow = true;
  tray.add(s);
}

// raised wooden rim around the tray
const rimMat = mat('#9c6b3f');
function addRim(w, d, x, z) {
  const r = new THREE.Mesh(new THREE.BoxGeometry(w, CAGE.wallH, d), rimMat);
  r.position.set(x, CAGE.wallH / 2 - 0.15, z);
  r.castShadow = r.receiveShadow = true;
  tray.add(r);
}
addRim(CAGE.w + 0.6, 0.5, 0, -CAGE.d/2);
addRim(CAGE.w + 0.6, 0.5, 0,  CAGE.d/2);
addRim(0.5, CAGE.d + 0.6, -CAGE.w/2, 0);
addRim(0.5, CAGE.d + 0.6,  CAGE.w/2, 0);

/* ============================================================
   CAGE BARS (top + sides) — thin cylinders, kept sparse so we see inside
   ============================================================ */
const cage = new THREE.Group();
scene.add(cage);
const barMat = mat('#cfd6dd', { metalness: 0.4, roughness: 0.4 });
const barGeoV = new THREE.CylinderGeometry(0.05, 0.05, 3.2, 5);
const barGeoH = new THREE.CylinderGeometry(0.05, 0.05, 1, 5);

const cageTopY = 3.4;
// vertical bars around perimeter
for (let x = -CAGE.w/2 + 0.6; x <= CAGE.w/2 - 0.6; x += 1.1) {
  for (const z of [-CAGE.d/2 + 0.2, CAGE.d/2 - 0.2]) {
    const b = new THREE.Mesh(barGeoV, barMat);
    b.position.set(x, cageTopY/2, z);
    cage.add(b);
  }
}
for (let z = -CAGE.d/2 + 0.6; z <= CAGE.d/2 - 0.6; z += 1.1) {
  for (const x of [-CAGE.w/2 + 0.2, CAGE.w/2 - 0.2]) {
    const b = new THREE.Mesh(barGeoV, barMat);
    b.position.set(x, cageTopY/2, z);
    cage.add(b);
  }
}
// top grid
function topBar(len, x, z, ry) {
  const g = new THREE.CylinderGeometry(0.05, 0.05, len, 5);
  const b = new THREE.Mesh(g, barMat);
  b.rotation.z = Math.PI / 2;
  b.rotation.y = ry;
  b.position.set(x, cageTopY, z);
  cage.add(b);
}
for (let z = -CAGE.d/2 + 0.2; z <= CAGE.d/2 - 0.2; z += 1.1) topBar(CAGE.w, 0, z, 0);
for (let x = -CAGE.w/2 + 0.2; x <= CAGE.w/2 - 0.2; x += 1.1) topBar(CAGE.d, x, 0, Math.PI/2);

/* ============================================================
   INTERACTIVE OBJECTS: WHEEL + FOOD BOWL
   ============================================================ */
// ---- Hamster wheel ----
const wheel = new THREE.Group();
wheel.position.set(CAGE.w/2 - 1.4, 1.7, -CAGE.d/2 + 2.2);
scene.add(wheel);

const wheelSpin = new THREE.Group(); // this rotates
wheel.add(wheelSpin);

const rimRing = new THREE.Mesh(
  new THREE.TorusGeometry(1.5, 0.18, 6, 16),
  mat('#ff7eb3')
);
rimRing.castShadow = true;
wheelSpin.add(rimRing);

// rungs
for (let i = 0; i < 8; i++) {
  const rung = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.12, 0.12), mat('#ffd166'));
  rung.rotation.z = (i / 8) * Math.PI * 2;
  rung.castShadow = true;
  wheelSpin.add(rung);
}
// hub
wheelSpin.add(new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.5, 8), mat('#8ecae6')).rotateX(Math.PI/2));

// stand (two arms holding the wheel)
const standMat = mat('#a0aec0', { metalness: 0.3 });
for (const s of [-1, 1]) {
  const arm = new THREE.Mesh(new THREE.BoxGeometry(0.18, 2.6, 0.18), standMat);
  arm.position.set(0, -0.2, s * 0.45);
  wheel.add(arm);
}
const baseBar = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.2, 1.4), standMat);
baseBar.position.set(0, -1.5, 0);
wheel.add(baseBar);

// ---- Food bowl ----
const bowl = new THREE.Group();
bowl.position.set(-CAGE.w/2 + 2.2, 0, CAGE.d/2 - 2.2);
scene.add(bowl);

const bowlMesh = new THREE.Mesh(
  new THREE.CylinderGeometry(0.9, 0.55, 0.6, 10),
  mat('#4cc9f0')
);
bowlMesh.position.y = 0.3;
bowlMesh.castShadow = bowlMesh.receiveShadow = true;
bowl.add(bowlMesh);

// food pellets inside
const pelletGeo = new THREE.DodecahedronGeometry(0.16, 0);
for (let i = 0; i < 9; i++) {
  const p = new THREE.Mesh(pelletGeo, mat(i % 2 ? '#c77dff' : '#f4a261'));
  const a = rand(0, Math.PI * 2), r = rand(0, 0.45);
  p.position.set(Math.cos(a) * r, 0.55, Math.sin(a) * r);
  p.castShadow = true;
  bowl.add(p);
}

// ---- A little toy ball for extra fun ----
const ball = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 0), mat('#ff5d8f'));
ball.position.set(1.5, 0.55, 1.2);
ball.castShadow = true;
scene.add(ball);

/* ============================================================
   LOW-POLY HAMSTER BUILDER
   ============================================================ */
const HAMSTER_COLORS = [
  { body: '#f4a261', belly: '#ffe0b3' },
  { body: '#e9c46a', belly: '#fff3d6' },
  { body: '#b5838d', belly: '#f0cdd2' },
  { body: '#cdb4db', belly: '#f3e6ff' },
  { body: '#8ecae6', belly: '#e0f4ff' },
];

function makeHamster(colorSet) {
  const g = new THREE.Group();
  const bodyMat = mat(colorSet.body);
  const bellyMat = mat(colorSet.belly);

  // body (squashed sphere)
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.7, 7, 5), bodyMat);
  body.scale.set(1.25, 1, 1);
  body.position.y = 0.7;
  body.castShadow = true;
  g.add(body);

  // belly patch
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.45, 6, 4), bellyMat);
  belly.scale.set(1.1, 0.9, 0.7);
  belly.position.set(0, 0.55, 0.35);
  g.add(belly);

  // head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.45, 7, 5), bodyMat);
  head.position.set(0, 0.85, 0.75);
  head.castShadow = true;
  g.add(head);

  // snout
  const snout = new THREE.Mesh(new THREE.SphereGeometry(0.2, 6, 4), bellyMat);
  snout.scale.set(1, 0.8, 1.1);
  snout.position.set(0, 0.75, 1.12);
  g.add(snout);

  // nose (wiggles!)
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.08, 5, 4), mat('#ff8fab'));
  nose.position.set(0, 0.78, 1.28);
  g.add(nose);

  // eyes
  const eyeMat = mat('#1a1a1a', { roughness: 0.3 });
  for (const s of [-1, 1]) {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.09, 6, 5), eyeMat);
    e.position.set(s * 0.22, 0.95, 1.05);
    g.add(e);
  }

  // ears
  for (const s of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.18, 6, 4), bodyMat);
    ear.scale.set(1, 1, 0.5);
    ear.position.set(s * 0.32, 1.22, 0.7);
    g.add(ear);
  }

  // tiny tail nub
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.12, 5, 4), bodyMat);
  tail.position.set(0, 0.7, -0.78);
  g.add(tail);

  // legs (animated while walking)
  const legGeo = new THREE.CylinderGeometry(0.1, 0.12, 0.45, 5);
  const legs = [];
  const legPos = [[-0.4,0.5],[0.4,0.5],[-0.4,-0.45],[0.4,-0.45]];
  for (const [lx, lz] of legPos) {
    const leg = new THREE.Mesh(legGeo, bodyMat);
    leg.position.set(lx, 0.25, lz);
    leg.castShadow = true;
    g.add(leg);
    legs.push(leg);
  }

  g.userData = { legs, nose, head };
  return g;
}

/* ============================================================
   HAMSTER AGENTS + AUTONOMOUS BEHAVIOR (state machine)
   ============================================================ */
const STATES = { WALK: 'walk', PAUSE: 'pause', TURN: 'turn', RUN_WHEEL: 'run_wheel', EAT: 'eat' };
const hamsters = [];

const wheelWorld = wheel.position.clone();
wheelWorld.y = 0; // ground target near wheel
const bowlWorld = bowl.position.clone();

function spawnHamster(i) {
  const mesh = makeHamster(HAMSTER_COLORS[i % HAMSTER_COLORS.length]);
  const x = rand(-CAGE.w/2+2, CAGE.w/2-2);
  const z = rand(-CAGE.d/2+2, CAGE.d/2-2);
  mesh.position.set(x, 0, z);
  scene.add(mesh);

  hamsters.push({
    mesh,
    heading: rand(0, Math.PI * 2),
    speed: rand(1.1, 1.7),
    state: STATES.PAUSE,
    timer: rand(0.5, 2.0),
    target: null,
    walkPhase: rand(0, Math.PI * 2),
    wheelAngle: 0,
  });
}
for (let i = 0; i < 5; i++) spawnHamster(i);

function pickNewTarget(h) {
  // weighted choice of next activity
  const roll = Math.random();
  if (roll < 0.18) {
    h.state = STATES.RUN_WHEEL;
    h.target = wheelWorld.clone();
  } else if (roll < 0.36) {
    h.state = STATES.EAT;
    h.target = bowlWorld.clone();
  } else {
    h.state = STATES.WALK;
    h.target = new THREE.Vector3(
      rand(-CAGE.w/2+1.5, CAGE.w/2-1.5), 0, rand(-CAGE.d/2+1.5, CAGE.d/2-1.5)
    );
  }
}

function updateHamster(h, dt, t) {
  const m = h.mesh;
  const legs = m.userData.legs;
  const nose = m.userData.nose;

  // constant cute nose wiggle
  nose.position.x = Math.sin(t * 8 + h.walkPhase) * 0.02;

  switch (h.state) {
    case STATES.PAUSE:
      h.timer -= dt;
      legs.forEach(l => l.rotation.x *= 0.8);
      if (h.timer <= 0) pickNewTarget(h);
      break;

    case STATES.TURN:
      h.timer -= dt;
      m.rotation.y += dt * 3; // spin around
      if (h.timer <= 0) { h.state = STATES.WALK; }
      break;

    case STATES.WALK: {
      if (!h.target) pickNewTarget(h);
      const toTarget = h.target.clone().sub(m.position); toTarget.y = 0;
      const dist = toTarget.length();
      const desired = Math.atan2(toTarget.x, toTarget.z);

      // steer heading toward target (shortest angle)
      let diff = desired - m.rotation.y;
      diff = Math.atan2(Math.sin(diff), Math.cos(diff));
      m.rotation.y += THREE.MathUtils.clamp(diff, -dt * 4, dt * 4);

      // move forward
      const step = h.speed * dt;
      m.position.x += Math.sin(m.rotation.y) * step;
      m.position.z += Math.cos(m.rotation.y) * step;

      // keep inside cage bounds
      m.position.x = THREE.MathUtils.clamp(m.position.x, -CAGE.w/2+1.2, CAGE.w/2-1.2);
      m.position.z = THREE.MathUtils.clamp(m.position.z, -CAGE.d/2+1.2, CAGE.d/2-1.2);

      // leg animation + body bob
      h.walkPhase += dt * 12;
      legs.forEach((l, i) => l.rotation.x = Math.sin(h.walkPhase + (i % 2) * Math.PI) * 0.7);
      m.position.y = Math.abs(Math.sin(h.walkPhase)) * 0.06;

      if (dist < 0.6) {
        if (h.state === STATES.WALK && h.target && h.target.distanceTo(m.position) < 0.6) {
          // reached a wander point -> maybe pause/turn
          h.timer = rand(0.6, 1.8);
          h.state = Math.random() < 0.5 ? STATES.PAUSE : STATES.TURN;
        }
      }
      break;
    }

    case STATES.RUN_WHEEL: {
      // move to wheel front then run
      const tp = wheelWorld.clone(); tp.x -= 0.0; tp.z += 0.0;
      const d = tp.distanceTo(m.position);
      if (d > 0.9) {
        m.lookAt(tp.x, m.position.y, tp.z);
        const step = h.speed * dt;
        m.position.x += Math.sin(m.rotation.y) * step;
        m.position.z += Math.cos(m.rotation.y) * step;
        legs.forEach((l, i) => l.rotation.x = Math.sin((t*14) + (i%2)*Math.PI) * 0.8);
      } else {
        // running in place on wheel + spin wheel
        m.position.copy(wheelWorld);
        m.rotation.y = Math.PI; // face into wheel
        legs.forEach((l, i) => l.rotation.x = Math.sin((t*16) + (i%2)*Math.PI) * 1.0);
        m.position.y = 0.05;
        wheelSpin.rotation.z -= dt * 6; // wheel turns!
        h.timer -= dt;
        if (h.timer <= 0) { h.state = STATES.PAUSE; h.timer = rand(0.8, 1.6); h.target = null; }
      }
      break;
    }

    case STATES.EAT: {
      const tp = bowlWorld.clone();
      const d = tp.distanceTo(m.position);
      if (d > 1.1) {
        m.lookAt(tp.x, m.position.y, tp.z);
        const step = h.speed * dt;
        m.position.x += Math.sin(m.rotation.y) * step;
        m.position.z += Math.cos(m.rotation.y) * step;
        legs.forEach((l, i) => l.rotation.x = Math.sin((t*12) + (i%2)*Math.PI) * 0.7);
      } else {
        m.lookAt(tp.x, m.position.y, tp.z);
        // head bobbing while munching
        m.userData.head.position.y = 0.85 + Math.sin(t * 10) * 0.06;
        legs.forEach(l => l.rotation.x *= 0.8);
        h.timer -= dt;
        if (h.timer <= 0) {
          m.userData.head.position.y = 0.85;
          h.state = STATES.PAUSE; h.timer = rand(0.6, 1.4); h.target = null;
        }
      }
      break;
    }
  }

  // start running timer when first entering wheel
  if (h.state === STATES.RUN_WHEEL && h.timer > 6) h.timer = rand(3, 5);
  if (h.state === STATES.EAT && h.timer > 6) h.timer = rand(2.5, 4);
}

/* ============================================================
   ANIMATION LOOP
   ============================================================ */
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  for (const h of hamsters) updateHamster(h, dt, t);

  // idle wheel slow spin when nobody uses it
  let anyoneOnWheel = hamsters.some(h => h.state === STATES.RUN_WHEEL && h.mesh.position.distanceTo(wheelWorld) < 1);
  if (!anyoneOnWheel) wheelSpin.rotation.z -= dt * 0.4;

  // gentle ball bounce
  ball.position.y = 0.55 + Math.abs(Math.sin(t * 2)) * 0.15;

  controls.update();
  renderer.render(scene, camera);
}
animate();

/* ============================================================
   RESIZE
   ============================================================ */
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## How it works

**Scene layout**
- A wooden **tray** with scattered low-poly "shavings" for bedding.
- A sparse **cage** of thin cylinders (sides + top grid) so the inside stays visible.
- An interactive **hamster wheel** (torus + rungs) that actually spins when a hamster runs on it.
- A **food bowl** with pellets, plus a bouncy toy ball for extra charm.

**Low-poly style**
- Every material uses `flatShading: true` and low segment counts on spheres/tori → crisp faceted look.
- Pastel palette (peach, cream, mauve, lavender, sky-blue hamsters).

**Autonomous behavior (state machine per hamster)**
Each of the 5 hamsters cycles through: `WALK → PAUSE / TURN`, with weighted chances to head for the **wheel** (`RUN_WHEEL`) or the **bowl** (`EAT`). They steer toward targets, clamp to cage bounds, animate their legs while walking, wiggle their noses constantly, bob their heads when eating, and spin the wheel when running.

**Controls**: OrbitControls — drag to rotate, scroll to zoom, with damping for a smooth feel.

Everything is self-contained in one file and pulls Three.js + OrbitControls via an import map from a CDN, so it runs immediately in any modern browser.