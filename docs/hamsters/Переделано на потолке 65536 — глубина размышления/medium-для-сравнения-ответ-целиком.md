

# Low-Poly Hamster Playground 🐹

Here's the complete single-file project. Save it as `index.html` and open it in any modern browser — no build step needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #aee2f5; }
  canvas { display: block; }
  #ui {
    position: fixed; top: 16px; left: 16px; pointer-events: none;
    font-family: "Comic Sans MS", "Chalkboard SE", cursive, sans-serif;
    color: #4a3b2a; text-shadow: 0 2px 0 rgba(255,255,255,.6);
  }
  #ui h1 { margin: 0; font-size: 26px; }
  #ui p  { margin: 4px 0 0; font-size: 14px; opacity: .85; }
</style>
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
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to orbit &bull; scroll to zoom &bull; watch them zoom the wheel</p>
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ---------------------------------------------------------- renderer */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xaee2f5);
scene.fog = new THREE.Fog(0xaee2f5, 30, 60);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 100);
camera.position.set(12, 9, 15);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 2, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI * 0.49;
controls.minDistance = 8;
controls.maxDistance = 30;

/* ---------------------------------------------------------- lights */
scene.add(new THREE.AmbientLight(0xfff2e0, 0.55));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(10, 16, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -14; sun.shadow.camera.right = 14;
sun.shadow.camera.top = 14;   sun.shadow.camera.bottom = -14;
scene.add(sun);

/* ---------------------------------------------------------- helpers */
const mat = (color, opts = {}) =>
  new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9, ...opts });

function box(w, h, d, m, x = 0, y = 0, z = 0, parent = scene) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m);
  mesh.position.set(x, y, z);
  mesh.castShadow = mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

/* ---------------------------------------------------------- ground */
const ground = new THREE.Mesh(
  new THREE.CircleGeometry(40, 24),
  mat(0x9fd98a, { flatShading: true })
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.5;
ground.receiveShadow = true;
scene.add(ground);

/* ---------------------------------------------------------- cage */
const CAGE_W = 15, CAGE_D = 7, CAGE_H = 4.5;
const cage = new THREE.Group();
scene.add(cage);

// wooden tray + sandy bedding
box(CAGE_W, 0.6, CAGE_D, mat(0xc98d4e), 0, -0.3, 0, cage);
box(CAGE_W - 0.6, 0.3, CAGE_D - 0.6, mat(0xf2d8a7), 0, 0.12, 0, cage);

// corner posts
const postMat = mat(0x8fa8bd, { metalness: 0.5, roughness: 0.4 });
for (const [sx, sz] of [[-1,-1],[1,-1],[1,1],[-1,1]]) {
  const post = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, CAGE_H, 6), postMat);
  post.position.set(sx * CAGE_W/2, CAGE_H/2, sz * CAGE_D/2);
  post.castShadow = true;
  cage.add(post);
}
// horizontal rails (top & middle)
function rail(y) {
  for (const [w, z] of [[CAGE_W, 0], [0, CAGE_D]]) {
    const r = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, w || CAGE_D, 5), postMat);
    r.rotation.z = w ? Math.PI / 2 : 0;
    r.rotation.x = w ? 0 : Math.PI / 2;
    r.position.set(0, y, z);
    cage.add(r);
  }
}
rail(CAGE_H); rail(CAGE_H * 0.5);
// vertical bars on the two long sides
for (let i = 1; i < 12; i++) {
  const x = -CAGE_W/2 + (CAGE_W / 12) * i;
  for (const z of [-CAGE_D/2, CAGE_D/2]) {
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, CAGE_H, 4), postMat);
    bar.position.set(x, CAGE_H/2, z);
    cage.add(bar);
  }
}
// glassy front wall
const glass = new THREE.Mesh(
  new THREE.PlaneGeometry(CAGE_W, CAGE_H),
  new THREE.MeshPhongMaterial({ color: 0xcdefff, transparent: true, opacity: 0.14, side: THREE.DoubleSide })
);
glass.position.set(0, CAGE_H/2, CAGE_D/2);
cage.add(glass);

/* ---------------------------------------------------------- wheel */
const WHEEL_POS = new THREE.Vector3(-5.2, 0, -1.6);
const wheelAssembly = new THREE.Group();
wheelAssembly.position.copy(WHEEL_POS);
scene.add(wheelAssembly);

const wheelSpin = new THREE.Group();
wheelSpin.rotation.y = Math.PI / 2;           // face sideways
wheelSpin.position.y = 1.5;
wheelAssembly.add(wheelSpin);

const rimMat = mat(0xff7eb6, { roughness: 0.6 });
const rim = new THREE.Mesh(new THREE.TorusGeometry(1.25, 0.13, 6, 14), rimMat);
rim.castShadow = true;
wheelSpin.add(rim);
for (let i = 0; i < 4; i++) {                 // spokes
  const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.4, 5), rimMat);
  spoke.rotation.z = (i / 4) * Math.PI;
  wheelSpin.add(spoke);
}
const hub = new THREE.Mesh(new THREE.SphereGeometry(0.18, 6, 5), rimMat);
wheelSpin.add(hub);
// legs
box(0.25, 1.5, 0.25, mat(0x8fa8bd, { metalness: 0.5 }), 0, 0.75, 0, wheelAssembly);
box(0.25, 0.15, 1.4, mat(0x8fa8bd, { metalness: 0.5 }), 0, 0.08, 0, wheelAssembly);
box(0.25, 0.15, 1.4, mat(0x8fa8bd, { metalness: 0.5 }), 0, 1.5, 0, wheelAssembly);

/* ---------------------------------------------------------- food bowl */
const BOWL_POS = new THREE.Vector3(5.2, 0, 1.8);
const bowl = new THREE.Group();
bowl.position.copy(BOWL_POS);
scene.add(bowl);
const bowlMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.65, 0.5, 8), mat(0x7ec8e3));
bowlMesh.position.y = 0.25; bowlMesh.castShadow = true;
bowl.add(bowlMesh);
for (let i = 0; i < 9; i++) {                 // seeds
  const seed = new THREE.Mesh(new THREE.SphereGeometry(0.12, 5, 4),
    mat([0xe8a33d, 0xd97b29, 0x9c6b30][i % 3]));
  const a = Math.random() * Math.PI * 2, r = Math.random() * 0.5;
  seed.position.set(Math.cos(a) * r, 0.45, Math.sin(a) * r);
  bowl.add(seed);
}
// little apple next to it
const apple = new THREE.Mesh(new THREE.SphereGeometry(0.35, 7, 5), mat(0xef5350));
apple.position.set(6.6, 0.35, 0.6); apple.castShadow = true;
scene.add(apple);
const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.25, 4), mat(0x6b4423));
stem.position.set(6.6, 0.75, 0.6);
scene.add(stem);

/* ---------------------------------------------------------- tunnel */
const tunnel = new THREE.Mesh(
  new THREE.CylinderGeometry(0.85, 0.85, 2.6, 8, 1, true, 0, Math.PI),
  mat(0xffd166, { side: THREE.DoubleSide })
);
tunnel.rotation.z = Math.PI / 2;
tunnel.position.set(2.5, 0.85, -2.2);
tunnel.castShadow = true;
scene.add(tunnel);

// hay tufts
const hayMat = mat(0xd9b44a);
[[ -2, 0.2, 2.5 ], [ 0.5, 0.2, 2.8 ], [ -3.5, 0.2, -2.6 ]].forEach(([x, y, z]) => {
  for (let i = 0; i < 3; i++) {
    const tuft = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.7, 4), hayMat);
    tuft.position.set(x + (Math.random()-0.5)*0.5, y + 0.3, z + (Math.random()-0.5)*0.5);
    tuft.rotation.set((Math.random()-0.5)*0.6, 0, (Math.random()-0.5)*0.6);
    scene.add(tuft);
  }
});

/* ---------------------------------------------------------- hamsters */
const HAMSTER_COLORS = [0xf5a962, 0xf7e3c0, 0xd98c5f];
const CHEEK_COLOR    = 0xffe8d6;

function buildHamster(color) {
  const g = new THREE.Group();
  const bodyMat = mat(color);

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 7, 5), bodyMat);
  body.scale.set(1, 0.85, 1.15);
  body.position.y = 0.5;
  body.castShadow = true;
  g.add(body);

  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.4, 6, 4), mat(CHEEK_COLOR));
  belly.scale.set(0.85, 0.6, 0.9);
  belly.position.set(0, 0.38, 0.25);
  g.add(belly);

  // ears
  for (const s of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.14, 5, 4), bodyMat);
    ear.position.set(s * 0.28, 0.95, -0.05);
    ear.castShadow = true;
    g.add(ear);
    const inner = new THREE.Mesh(new THREE.SphereGeometry(0.08, 5, 4), mat(0xffb3ba));
    inner.position.set(s * 0.28, 0.95, 0.02);
    g.add(inner);
  }
  // eyes
  for (const s of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.07, 5, 4), mat(0x2b2b2b));
    eye.position.set(s * 0.22, 0.62, 0.5);
    g.add(eye);
  }
  // nose + cheeks
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.06, 5, 4), mat(0xff8fab));
  nose.position.set(0, 0.5, 0.63);
  g.add(nose);
  for (const s of [-1, 1]) {
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.16, 5, 4), mat(CHEEK_COLOR));
    cheek.position.set(s * 0.4, 0.45, 0.42);
    g.add(cheek);
  }
  // legs (animated)
  const legs = [];
  const legGeo = new THREE.BoxGeometry(0.14, 0.25, 0.18);
  for (const [lx, lz] of [[-0.3, 0.35],[0.3, 0.35],[-0.3,-0.35],[0.3,-0.35]]) {
    const leg = new THREE.Mesh(legGeo, bodyMat);
    leg.position.set(lx, 0.12, lz);
    leg.castShadow = true;
    g.add(leg);
    legs.push({ mesh: leg, phase: (lx < 0) === (lz > 0) ? 0 : Math.PI });
  }
  return { group: g, body, legs };
}

class Hamster {
  constructor(color, x, z) {
    const built = buildHamster(color);
    this.group = built.group;
    this.body  = built.body;
    this.legs  = built.legs;
    this.pos   = new THREE.Vector3(x, 0, z);
    this.yaw   = Math.random() * Math.PI * 2;
    this.speed = 0;
    this.state = 'idle';
    this.timer = 1 + Math.random() * 2;
    this.target = new THREE.Vector3();
    this.onWheel = false;
    this.onBowl  = false;
    this.wheelTimer = 0;
    scene.add(this.group);
  }

  setState(s) { this.state = s; this.onWheel = false; this.onBowl = false; }

  pickTarget() {
    this.target.set(
      THREE.MathUtils.randFloat(-CAGE_W/2 + 1.2, CAGE_W/2 - 1.2),
      0,
      THREE.MathUtils.randFloat(-CAGE_D/2 + 1.2, CAGE_D/2 - 1.2)
    );
  }

  decide() {
    const r = Math.random();
    if (r < 0.5)       { this.pickTarget(); this.setState('wander'); }
    else if (r < 0.72) { this.target.copy(WHEEL_POS).add(new THREE.Vector3(1.9, 0, 0)); this.setState('toWheel'); }
    else if (r < 0.92) { this.target.copy(BOWL_POS).add(new THREE.Vector3(-1.6, 0, 0.4)); this.setState('toBowl'); }
    else               { this.setState('idle'); this.timer = 1 + Math.random() * 2; }
  }

  steerTo(target, dt, arriveDist) {
    const dx = target.x - this.pos.x, dz = target.z - this.pos.z;
    const dist = Math.hypot(dx, dz);
    if (dist < arriveDist) return true;
    const want = Math.atan2(dx, dz);
    let diff = want - this.yaw;
    while (diff >  Math.PI) diff -= Math.PI * 2;
    while (diff < -Math.PI) diff += Math.PI * 2;
    this.yaw += THREE.MathUtils.clamp(diff, -2.5 * dt, 2.5 * dt);
    this.speed = 1.6;
    this.pos.x += Math.sin(this.yaw) * this.speed * dt;
    this.pos.z += Math.cos(this.yaw) * this.speed * dt;
    return false;
  }

  update(dt, t) {
    this.timer -= dt;

    switch (this.state) {
      case 'idle':
        this.speed = THREE.MathUtils.lerp(this.speed, 0, 6 * dt);
        if (this.timer <= 0) this.decide();
        break;

      case 'wander':
        if (this.steerTo(this.target, dt, 0.35)) {
          this.setState('idle');
          this.timer = 0.8 + Math.random() * 2.5;
        }
        break;

      case 'toWheel':
        if (this.steerTo(this.target, dt, 0.25)) { this.setState('onWheel'); this.wheelTimer = 3 + Math.random() * 3; }
        break;

      case 'onWheel':
        this.onWheel = true;
        this.speed = 0;
        this.yaw = THREE.MathUtils.lerp(this.yaw, Math.atan2(WHEEL_POS.x - this.pos.x, WHEEL_POS.z - this.pos.z), 8 * dt);
        this.wheelTimer -= dt;
        if (this.wheelTimer <= 0) { this.setState('idle'); this.timer = 1 + Math.random(); }
        break;

      case 'toBowl':
        if (this.steerTo(this.target, dt, 0.25)) { this.setState('eating'); this.timer = 2 + Math.random() * 2; }
        break;

      case 'eating':
        this.onBowl = true;
        this.speed = 0;
        this.yaw = THREE.MathUtils.lerp(this.yaw, Math.atan2(BOWL_POS.x - this.pos.x, BOWL_POS.z - this.pos.z), 8 * dt);
        if (this.timer <= 0) { this.setState('idle'); this.timer = 1 + Math.random(); }
        break;
    }

    // keep inside cage
    this.pos.x = THREE.MathUtils.clamp(this.pos.x, -CAGE_W/2 + 0.9, CAGE_W/2 - 0.9);
    this.pos.z = THREE.MathUtils.clamp(this.pos.z, -CAGE_D/2 + 0.9, CAGE_D/2 - 0.9);

    // apply transform
    this.group.position.set(this.pos.x, 0, this.pos.z);
    this.group.rotation.y = this.yaw;

    // bobbing while moving, chewing while eating
    const moving = this.speed > 0.1;
    const bobAmp = moving ? 0.05 : 0.015;
    const bobFreq = moving ? 12 : 3;
    this.group.position.y = Math.sin(t * bobFreq) * bobAmp;
    this.body.scale.y = 0.85 * (1 + (this.state === 'eating' ? Math.sin(t * 14) * 0.05 : 0));

    // leg animation
    const run = this.speed > 0.1 ? 11 : 0;
    for (const leg of this.legs) {
      const targetRot = run ? Math.sin(t * run + leg.phase) * 0.7 : 0;
      leg.mesh.rotation.x = THREE.MathUtils.lerp(leg.mesh.rotation.x, targetRot, 10 * dt);
    }
  }
}

const hamsters = [
  new Hamster(HAMSTER_COLORS[0], -2, 1),
  new Hamster(HAMSTER_COLORS[1],  2, -1.5),
  new Hamster(HAMSTER_COLORS[2],  0, 2),
];

/* ---------------------------------------------------------- loop */
let wheelSpeed = 0;
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  for (const h of hamsters) h.update(dt, t);

  // wheel spins while anyone is on it
  const targetSpeed = hamsters.some(h => h.onWheel) ? 9 : 0;
  wheelSpeed = THREE.MathUtils.lerp(wheelSpeed, targetSpeed, 2.5 * dt);
  wheelSpin.rotation.z += wheelSpeed * dt;

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

**Scene**
- A wooden tray cage with sandy bedding, metal corner posts, rails, side bars, and a faintly tinted glass front
- A **spinning exercise wheel** (pink rim + spokes) that speeds up and slows down naturally
- A **food bowl** with scattered seeds, a red apple, a yellow half-tube **tunnel**, and hay tufts
- Pastel grass ground with soft fog and warm sunlight + shadows

**Three hamsters** in different fur colors, each built from low-poly spheres/boxes with ears, pink noses, rosy cheeks, and animated stubby legs.

**Behavior (simple state machine)**
- `idle` → pauses with gentle breathing bob
- `wander` → steers smoothly toward a random point, legs gallop, body bounces
- `toWheel` / `onWheel` → walks to the wheel, faces it, "runs" in place while the wheel spins fast, then hops off
- `toBowl` / `eating` → walks over and chews with a little head-bob

**Controls:** drag to orbit, scroll to zoom, camera clamped so you never go under the floor. Everything is clamped inside the cage, `dt` is capped, and the whole thing runs on a single `requestAnimationFrame` loop — stable and easy to read.