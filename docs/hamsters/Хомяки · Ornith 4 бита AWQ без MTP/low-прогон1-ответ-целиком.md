Let me create a Low-Poly 3D Hamster Playground using Three.js in a single HTML file. I'll make it cute, colorful, and fun with:

1. A cage (enclosure)
2. A floor/tray
3. Several low-poly hamsters with autonomous behavior
4. An interactive object (exercise wheel)

Let me build this step by step:

- Set up the scene, camera, renderer
- Create the cage walls (transparent-ish)
- Create the floor tray
- Create multiple hamsters with body, head, ears, legs, tail
- Add an exercise wheel that's interactive (click to spin faster, or hamsters run in it)
- Add autonomous behavior: walking, pausing, turning
- Add nice lighting and colors
- Make it responsive

Let me write clean, well-organized code. I'll use Three.js from CDN.

For the hamsters, I'll build them from primitive geometries (icosahedron, spheres, boxes) merged into a group so they can be animated as a unit.

Behavior logic:
- Each hamster has a state machine: WALKING, PAUSING, TURNING
- They wander around the floor area
- When they hit boundaries, they turn around
- Random pauses
- Cute bobbing animation while walking

Interactive object: an exercise wheel that spins continuously, and clicking it makes it speed up temporarily. Maybe hamsters occasionally enter the wheel.

Let me keep it manageable but complete.

I'll write the full HTML now.
</think>

Here's a complete single-file **Low-Poly Hamster Playground**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #1a1526; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; }
  #canvas-container { width: 100vw; height: 100vh; display: block; }
  #ui {
    position: fixed; top: 14px; left: 14px; z-index: 10;
    background: rgba(255,245,255,0.9); border-radius: 16px;
    padding: 14px 18px; max-width: 280px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    backdrop-filter: blur(6px);
    color: #4a3a2a;
  }
  #ui h1 { font-size: 18px; margin-bottom: 6px; color: #d6679b; }
  #ui p { font-size: 12px; line-height: 1.5; color: #6b5a4a; }
  #ui b { color: #b57ec2; }
  .badge {
    display: inline-block; background: #ffe0ef; color: #c44da0;
    border-radius: 8px; padding: 2px 8px; font-size: 11px;
    margin-top: 8px; font-weight: bold;
  }
  #hint {
    position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
    background: rgba(255,224,239,0.9); color: #a0307a;
    padding: 8px 16px; border-radius: 20px; font-size: 12px;
    z-index: 10; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Hamster Playground</h1>
  <p>A tiny low-poly colony of happy hamsters roaming their cage.</p>
  <p><b>Drag</b> to rotate · <b>Scroll</b> to zoom · <b>Click</b> the wheel!</p>
  <span class="badge" id="counter">Hamsters: 0</span>
</div>
<div id="hint">🎡 Click the running wheel to boost it!</div>
<div id="canvas-container"></div>

<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js"
  }
}
</script>

<script type="module">
import * as THREE from 'three';

// ---------- Core setup ----------
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2a2040);
scene.fog = new THREE.Fog(0x2a2040, 30, 60);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 200);
camera.position.set(12, 10, 16);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// ---------- Orbit controls (manual, no extra import) ----------
let camTheta = 0.7, camPhi = 0.9, camDist = 26;
let target = new THREE.Vector3(0, 1, 0);
let dragging = false, lastX = 0, lastY = 0;
const el = renderer.domElement;

el.addEventListener('pointerdown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; });
window.addEventListener('pointerup', () => dragging = false);
window.addEventListener('pointermove', e => {
  if (!dragging) return;
  const dx = e.clientX - lastX, dy = e.clientY - lastY;
  camTheta -= dx * 0.005;
  camPhi = Math.max(0.25, Math.min(1.45, camPhi - dy * 0.005));
  lastX = e.clientX; lastY = e.clientY;
});
el.addEventListener('wheel', e => {
  camDist += e.deltaY * 0.02;
  camDist = Math.max(10, Math.min(50, camDist));
}, { passive: true });

function updateCamera() {
  const x = camDist * Math.cos(camPhi) * Math.sin(camTheta);
  const y = camDist * Math.sin(camPhi);
  const z = camDist * Math.cos(camPhi) * Math.cos(camTheta);
  camera.position.set(target.x + x, target.y + y, target.z + z);
  camera.lookAt(target);
}

// ---------- Lighting ----------
const hemi = new THREE.HemisphereLight(0xfff0ff, 0x8060a0, 0.8);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff5e0, 1.1);
sun.position.set(10, 18, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1; sun.shadow.camera.far = 60;
sun.shadow.camera.left = -20; sun.shadow.camera.right = 20;
sun.shadow.camera.top = 20; sun.shadow.camera.bottom = -20;
sun.shadow.bias = 0.0008;
scene.add(sun);

const fill = new THREE.DirectionalLight(0xff99cc, 0.4);
fill.position.set(-8, 6, -6);
scene.add(fill);

// ---------- Materials ----------
const mat = (color, opts = {}) => new THREE.MeshStandardMaterial({
  color, flatShading: true, roughness: 0.85, metalness: 0, ...opts
});

// ---------- Cage ----------
const cage = new THREE.Group();
scene.add(cage);

// Tray (floor)
const tray = new THREE.Mesh(
  new THREE.BoxGeometry(28, 1.2, 20),
  mat(0x6ec6ff)
);
tray.position.y = -0.6;
tray.receiveShadow = true;
cage.add(tray);

// Bedding (wood shavings look — scattered little boxes)
const beddingMat = mat(0xf5deb3);
for (let i = 0; i < 140; i++) {
  const s = 0.25 + Math.random() * 0.4;
  const shaving = new THREE.Mesh(new THREE.BoxGeometry(s, 0.15, s*0.8), beddingMat);
  shaving.position.set((Math.random()-0.5)*26, 0.08, (Math.random()-0.5)*18);
  shaving.rotation.y = Math.random()*Math.PI;
  cage.add(shaving);
}

// Walls (semi-transparent acrylic)
const wallMat = new THREE.MeshPhysicalMaterial({
  color: 0xbfe9ff, transmission: 0.8, transparent: true,
  opacity: 0.25, roughness: 0.2, thickness: 1, side: THREE.DoubleSide
});
const WALL_H = 6, WALL_T = 0.3;
function addWall(w, d, x, z) {
  const wall = new THREE.Mesh(new THREE.BoxGeometry(w, WALL_H, d), wallMat);
  wall.position.set(x, WALL_H/2 - 0.1, z);
  cage.add(wall);
}
addWall(28, WALL_T, 0, -10);
addWall(28, WALL_T, 0, 10);
addWall(WALL_T, 20, -14, 0);
addWall(WALL_T, 20, 14, 0);

// Bars on top back wall for style
const barMat = mat(0xdfe6ed, { metalness: 0.6, roughness: 0.3 });
for (let i = 0; i < 12; i++) {
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, WALL_H, 6), barMat);
  bar.position.set(-13 + i*2.2, WALL_H/2, -9.8);
  cage.add(bar);
}

// ---------- Exercise Wheel (interactive) ----------
const wheelGroup = new THREE.Group();
const WHEEL_X = -8, WHEEL_Z = -6;
wheelGroup.position.set(WHEEL_X, 0.6, WHEEL_Z);
cage.add(wheelGroup);

const wheelRimMat = mat(0xff8a5c);
const wheelSpokeMat = mat(0xffd166);
const wheelHub = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 2.4, 12), wheelSpokeMat);
wheelHub.rotation.z = Math.PI/2;
wheelGroup.add(wheelHub);

const spokes = [];
for (let i = 0; i < 16; i++) {
  const a = (i/16) * Math.PI * 2;
  const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.2, 0.15), wheelSpokeMat);
  spoke.position.set(0, Math.cos(a)*1.4, Math.sin(a)*1.4);
  spoke.rotation.x = a;
  wheelGroup.add(spoke);
  spokes.push(spoke);
}
// side rims
for (const sx of [-1.2, 1.2]) {
  const rim = new THREE.Mesh(new THREE.TorusGeometry(1.5, 0.12, 8, 20), wheelRimMat);
  rim.rotation.y = Math.PI/2;
  rim.position.x = sx;
  wheelGroup.add(rim);
}

let wheelSpeed = 0.4, wheelTargetSpeed = 0.4;
wheelGroup.userData = { spin: 0 };

// Click detection
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
window.addEventListener('click', e => {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObject(wheelGroup, true);
  if (hits.length > 0) {
    wheelTargetSpeed = 3.5;
    setTimeout(() => wheelTargetSpeed = 0.4, 1500);
    popText();
  }
});

function popText() {
  const hint = document.getElementById('hint');
  hint.textContent = '💨 Vroom! Wheel boosted!';
  hint.style.background = 'rgba(255,230,120,0.95)';
  setTimeout(() => { hint.textContent = '🎡 Click the running wheel to boost it!'; hint.style.background=''; }, 1400);
}

// ---------- Food bowl ----------
const bowlGroup = new THREE.Group();
const BOWL_X = 9, BOWL_Z = 5;
bowlGroup.position.set(BOWL_X, 0.1, BOWL_Z);
cage.add(bowlGroup);
const bowl = new THREE.Mesh(new THREE.ConeGeometry(1.1, 0.7, 16, 1, true), mat(0x9b5de5));
bowl.position.y = 0.35; bowl.rotation.x = Math.PI;
bowlGroup.add(bowl);
const foodBase = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 1.05, 0.1, 16), mat(0x8e44ad));
bowlGroup.add(foodBase);
for (let i = 0; i < 12; i++) {
  const seed = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 5), mat(0xf39c12));
  seed.position.set((Math.random()-0.5)*0.9, 0.5, (Math.random()-0.5)*0.9);
  bowlGroup.add(seed);
}

// ---------- Tunnel ----------
const tunnel = new THREE.Group();
const TUN_X = 6, TUN_Z = -6;
tunnel.position.set(TUN_X, 0.6, TUN_Z);
tunnel.rotation.z = Math.PI/2;
cage.add(tunnel);
const tunnelMat = mat(0x2ecc71, { side: THREE.DoubleSide });
const tunnelMesh = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 6, 12, 1, true, 0, Math.PI*1.6), tunnelMat);
tunnel.add(tunnelMesh);

// ---------- Hamster factory ----------
const hamsterColors = [0xffb3a0, 0xfad7a1, 0xd1a3ff, 0xa0e7ff, 0xffb7c5, 0xc8b6ff];
const hamsters = [];
const BOUNDS = { minX: -12, maxX: 12, minZ: -8.5, maxZ: 8.5 };

function makeHamster(colorHex) {
  const g = new THREE.Group();
  const bodyMat = mat(colorHex);
  const darkMat = mat(new THREE.Color(colorHex).multiplyScalar(0.75));
  const whiteMat = mat(0xffffff);
  const blackMat = mat(0x111111);

  // Body
  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.75, 1), bodyMat);
  body.scale.set(1, 0.9, 1.25);
  body.position.y = 0.7;
  body.castShadow = true;
  g.add(body);

  // Belly
  const belly = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 1), mat(new THREE.Color(colorHex).multiplyScalar(1.25)));
  belly.scale.set(1, 0.8, 1.1);
  belly.position.set(0, 0.55, 0.25);
  g.add(belly);

  // Head
  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 1), bodyMat);
  head.position.set(0, 1.05, 0.75);
  head.castShadow = true;
  g.add(head);
  g.head = head;

  // Cheeks
  for (const sx of [-1, 1]) {
    const cheek = new THREE.Mesh(new THREE.IcosahedronGeometry(0.28, 0), bodyMat);
    cheek.position.set(sx*0.35, 0.95, 0.55);
    g.add(cheek);
  }

  // Ears
  for (const sx of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.35, 6), darkMat);
    ear.position.set(sx*0.3, 1.5, 0.7);
    g.add(ear);
    const inner = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.25, 6), mat(0xff9aa2));
    inner.position.set(sx*0.3, 1.5, 0.73);
    g.add(inner);
  }

  // Eyes
  for (const sx of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.11, 10, 10), blackMat);
    eye.position.set(sx*0.24, 1.12, 1.05);
    g.add(eye);
    const shine = new THREE.Mesh(new THREE.SphereGeometry(0.04, 6, 6), whiteMat);
    shine.position.set(sx*0.22, 1.16, 1.13);
    g.add(shine);
  }

  // Nose
  const nose = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.14, 5), mat(0xff6b81));
  nose.position.set(0, 0.98, 1.22); nose.rotation.x = -0.4;
  g.add(nose);

  // Feet (4)
  const feet = [];
  const footPositions = [[-0.35,0.25,0.4],[0.35,0.25,0.4],[-0.35,0.25,-0.35],[0.35,0.25,-0.35]];
  for (let i=0;i<4;i++){
    const f = new THREE.Mesh(new THREE.SphereGeometry(0.16, 8, 6), darkMat);
    f.scale.set(1,0.6,1.3);
    f.position.set(...footPositions[i]);
    g.add(f); feet.push(f);
  }

  // Tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 6), mat(0xffe0b2));
  tail.position.set(0, 0.6, -0.9);
  g.add(tail);

  g.userData.feet = feet;
  return g;
}

// Behavior states
const STATES = { WALK: 'walk', PAUSE: 'pause', TURN: 'turn' };

function spawnHamster(i) {
  const h = makeHamster(hamsterColors[i % hamsterColors.length]);
  const angle = (i / 6) * Math.PI * 2;
  const r = 4 + Math.random()*4;
  h.position.set(Math.cos(angle)*r, 0.02, Math.sin(angle)*r);
  scene.add(h);
  hamsters.push(h);

  h.state = STATES.WALK;
  h.timer = 2 + Math.random()*3;
  h.speed = 1.5 + Math.random()*1.2;
  h.targetHeading = Math.random()*Math.PI*2;
  h.wobble = Math.random()*Math.PI*2;
}

for (let i = 0; i < 6; i++) spawnHamster(i);
document.getElementById('counter').textContent = 'Hamsters: ' + hamsters.length;

// ---------- Update loop ----------
const clock = new THREE.Clock();
const tmp = new THREE.Vector3();

function stepHamster(h, dt) {
  h.timer -= dt;
  h.wobble += dt * 6;

  if (h.state === STATES.WALK) {
    // move forward along facing
    h.position.x += Math.sin(h.targetHeading) * h.speed * dt;
    h.position.z += Math.cos(h.targetHeading) * h.speed * dt;
    // gentle body yaw
    h.rotation.y = h.targetHeading;
    // bobbing feet
    const feet = h.userData.feet;
    feet.forEach((f, idx) => {
      f.position.y = 0.25 + Math.abs(Math.sin(h.wobble + idx)) * 0.12;
    });

    // keep inside bounds — turn around if near edge
    if (h.position.x > BOUNDS.maxX || h.position.x < BOUNDS.minX ||
        h.position.z > BOUNDS.maxZ || h.position.z < BOUNDS.minZ) {
      h.state = STATES.TURN;
      h.timer = 0.6;
      h.targetHeading += Math.PI;
    }
    if (h.timer <= 0) {
      h.state = STATES.PAUSE;
      h.timer = 1.5 + Math.random()*2.5;
    }
  }
  else if (h.state === STATES.PAUSE) {
    // idle — slight head turn, random new heading
    h.rotation.y += Math.sin(h.wobble*0.5) * 0.002;
    if (h.timer <= 0) {
      h.targetHeading = Math.random()*Math.PI*2;
      h.state = STATES.WALK;
      h.timer = 2 + Math.random()*4;
    }
  }
  else if (h.state === STATES.TURN) {
    // face target then resume
    if (h.timer <= 0) {
      h.state = STATES.WALK;
      h.timer = 2 + Math.random()*4;
    }
  }

  // soft boundary clamp just in case
  h.position.x = Math.max(BOUNDS.minX+0.5, Math.min(BOUNDS.maxX-0.5, h.position.x));
  h.position.z = Math.max(BOUNDS.minZ+0.5, Math.min(BOUNDS.maxZ-0.5, h.position.z));
}

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // Wheel physics
  wheelSpeed += (wheelTargetSpeed - wheelSpeed) * dt * 3;
  wheelGroup.userData.spin += wheelSpeed * dt;
  wheelGroup.rotation.x = wheelGroup.userData.spin;

  // Occasionally a hamster "runs" the wheel
  hamsters.forEach((h, i) => {
    stepHamster(h, dt);

    // interaction: near wheel -> enter it briefly
    const dx = h.position.x - WHEEL_X;
    const dz = h.position.z - WHEEL_Z;
    const dist = Math.hypot(dx, dz);
    if (dist < 2.2 && h.state === STATES.WALK) {
      // park hamster in wheel, spin it hard
      h.position.set(WHEEL_X, 0.05, WHEEL_Z);
      h.rotation.y = 0;
      h.state = STATES.PAUSE;
      h.timer = 1.2 + Math.random()*1.5;
      wheelTargetSpeed = Math.max(wheelTargetSpeed, 1.2);
      // fade it out slightly (peeking hamster)
      h.scale.setScalar(0.85);
    } else if (h.state === STATES.PAUSE && h.scale.x < 1 && dist > 2.5) {
      h.scale.lerp(new THREE.Vector3(1,1,1), dt*2);
    }
  });

  // subtle breathing on all hamsters
  hamsters.forEach((h, i) => {
    const b = 1 + Math.sin(t*3 + i)*0.03;
    h.children[0].scale.y = 0.9*b;
  });

  updateCamera();
  renderer.render(scene, camera);
}
animate();

// ---------- Resize ----------
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

## What it does

**🏠 The cage** — A translucent acrylic-style tank (using `MeshPhysicalMaterial` transmission) with a blue tray floor, scattered wood-shaving bedding, and decorative metal bars along the back wall.

**🐹 Six low-poly hamsters** — Built from icosahedrons/spheres/cones in pastel colors (peach, yellow, lavender, sky-blue, pink). Each has a chubby body, big head, rosy cheeks, perky ears, shiny eyes, a little nose, four wiggling feet, and a stubby tail.

**🧠 Autonomous behavior** — Each hamster cycles through three states:
- **WALK** — strides around with a bobbing gait, keeps within bounds and bounces off walls
- **TURN** — pivots to reface when it hits a wall
- **PAUSE** — stops to sniff around, then picks a fresh random heading

**🎡 Interactive running wheel** — Click it to trigger a "Vroom!" boost (spin speeds up for 1.5s). Hamsters also wander over and *pile into the wheel*, peeking out while it spins.

**🥣 Extras** — A purple food bowl with orange seeds, and a green tunnel for flavor.

**🎮 Controls** — Drag to orbit, scroll to zoom (custom orbit, no extra imports needed). Everything runs instantly in a modern browser via the Three.js CDN import map.

Just save it as `index.html` and open it — no build step required.