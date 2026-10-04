

# Low-Poly Hamster Playground 🐹

Here's the complete single-file project. Save it as `index.html` and open it in any modern browser:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; background: #ffe9d6; }
  #ui {
    position: fixed; top: 16px; left: 50%; transform: translateX(-50%);
    font-family: "Comic Sans MS", "Chalkboard SE", cursive, sans-serif;
    color: #6b4226; text-align: center; pointer-events: none;
    text-shadow: 0 2px 0 rgba(255,255,255,.6);
  }
  #ui h1 { margin: 0; font-size: 26px; }
  #ui p  { margin: 4px 0 0; font-size: 14px; opacity: .8; }
</style>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate &nbsp;•&nbsp; Scroll to zoom</p>
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ---------------------------------------------------------------
   BASICS
---------------------------------------------------------------- */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9d6);
scene.fog = new THREE.Fog(0xffe9d6, 18, 40);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 100);
camera.position.set(9, 7, 11);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 5;
controls.maxDistance = 22;
controls.maxPolarAngle = Math.PI * 0.49;

/* Lights */
scene.add(new THREE.HemisphereLight(0xfff2e0, 0xd8a878, 0.9));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(6, 10, 4);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -8; sun.shadow.camera.right = 8;
sun.shadow.camera.top = 8;   sun.shadow.camera.bottom = -8;
scene.add(sun);

/* Helpers */
const mat = (color, opts = {}) =>
  new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.85, ...opts });
function mesh(geo, material, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, material);
  m.position.set(x, y, z);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

/* ---------------------------------------------------------------
   ROOM FLOOR (outside the cage)
---------------------------------------------------------------- */
const roomFloor = mesh(new THREE.BoxGeometry(30, 0.3, 30), mat(0xf7cfa2), 0, -0.15, 0);
roomFloor.receiveShadow = true;
scene.add(roomFloor);

/* ---------------------------------------------------------------
   CAGE  (tray 10 x 6, walls ~2.4 high)
---------------------------------------------------------------- */
const CAGE = { w: 10, d: 6, h: 2.4, bx: 4.3, bz: 2.3 }; // bx/bz = hamster bounds

// Tray
const tray = mesh(new THREE.BoxGeometry(CAGE.w, 0.5, CAGE.d), mat(0x8ecae6), 0, -0.25, 0);
scene.add(tray);
// Sand bedding
const sand = mesh(new THREE.BoxGeometry(CAGE.w - 0.4, 0.2, CAGE.d - 0.4), mat(0xe9d8a6), 0, 0.1, 0);
scene.add(sand);

// Glass walls (subtle)
const glassMat = new THREE.MeshStandardMaterial({
  color: 0xcdeef7, transparent: true, opacity: 0.18, roughness: 0.2, side: THREE.DoubleSide
});
[[0, CAGE.h / 2 + 0.2, -CAGE.d / 2, CAGE.w, 0],
 [0, CAGE.h / 2 + 0.2,  CAGE.d / 2, CAGE.w, 0],
 [-CAGE.w / 2, CAGE.h / 2 + 0.2, 0, CAGE.d, Math.PI / 2],
 [ CAGE.w / 2, CAGE.h / 2 + 0.2, 0, CAGE.d, Math.PI / 2]
].forEach(([x, y, z, len, ry]) => {
  const g = new THREE.Mesh(new THREE.PlaneGeometry(len, CAGE.h), glassMat);
  g.position.set(x, y, z); g.rotation.y = ry;
  scene.add(g);
});

// Wire bars (vertical) + top frame
const barGeo = new THREE.CylinderGeometry(0.035, 0.035, CAGE.h, 5);
const barMat = mat(0x9aa5ad, { metalness: 0.6, roughness: 0.4 });
for (let i = 0; i <= 10; i++) {
  const x = -CAGE.w / 2 + i * (CAGE.w / 10);
  scene.add(mesh(barGeo, barMat, x, CAGE.h / 2 + 0.2, -CAGE.d / 2));
  scene.add(mesh(barGeo, barMat, x, CAGE.h / 2 + 0.2,  CAGE.d / 2));
}
for (let i = 0; i <= 6; i++) {
  const z = -CAGE.d / 2 + i * (CAGE.d / 6);
  scene.add(mesh(barGeo, barMat, -CAGE.w / 2, CAGE.h / 2 + 0.2, z));
  scene.add(mesh(barGeo, barMat,  CAGE.w / 2, CAGE.h / 2 + 0.2, z));
}
// Top frame rails
const railMat = mat(0x7f8c99, { metalness: 0.6, roughness: 0.4 });
[[-CAGE.d / 2, CAGE.w], [CAGE.d / 2, CAGE.w]].forEach(([z, len]) =>
  scene.add(mesh(new THREE.BoxGeometry(len, 0.1, 0.1), railMat, 0, CAGE.h + 0.2, z)));
[[-CAGE.w / 2, CAGE.d], [CAGE.w / 2, CAGE.d]].forEach(([x, len]) =>
  scene.add(mesh(new THREE.BoxGeometry(0.1, 0.1, len), railMat, x, CAGE.h + 0.2, 0)));

/* ---------------------------------------------------------------
   INTERACTIVE OBJECTS
---------------------------------------------------------------- */
// --- Exercise wheel (corner, facing inward) ---
const WHEEL_POS = new THREE.Vector3(3.4, 0, -1.7);
const WHEEL_STAND = new THREE.Vector3(2.2, 0, -1.7); // where hamster stands
const wheel = new THREE.Group();
{
  const tire = mesh(new THREE.TorusGeometry(0.85, 0.11, 6, 14), mat(0xff8fab));
  const rim  = mesh(new THREE.TorusGeometry(0.55, 0.06, 5, 12), mat(0xffb3c6));
  wheel.add(tire, rim);
  const spokeGeo = new THREE.CylinderGeometry(0.03, 0.03, 1.6, 4);
  for (let i = 0; i < 3; i++) {
    const s = mesh(spokeGeo, mat(0xffffff), 0, 0, 0);
    s.rotation.z = i * Math.PI / 3;
    wheel.add(s);
  }
  wheel.add(mesh(new THREE.SphereGeometry(0.1, 6, 5), mat(0xffffff)));
  wheel.position.set(WHEEL_POS.x, 1.0, WHEEL_POS.z);
  wheel.rotation.y = -Math.PI / 4; // face into the cage
  scene.add(wheel);
  // Stand
  const stand = mesh(new THREE.BoxGeometry(0.5, 0.9, 0.7), mat(0x7fb069));
  stand.position.set(WHEEL_POS.x, 0.45, WHEEL_POS.z);
  scene.add(stand);
}
let wheelSpeed = 0;

// --- Tunnel (half pipe) ---
{
  const t = mesh(new THREE.CylinderGeometry(0.55, 0.55, 1.6, 8, 1, false, 0, Math.PI),
                 mat(0xb5e48c, { side: THREE.DoubleSide }), -2.6, 0.55, 1.4);
  t.rotation.z = Math.PI / 2;
  t.rotation.y = Math.PI / 6;
  scene.add(t);
  const base = mesh(new THREE.BoxGeometry(1.9, 0.12, 1.2), mat(0x9ccf6f), -2.6, 0.06, 1.4);
  base.rotation.y = Math.PI / 6;
  scene.add(base);
}

// --- Food bowl ---
const BOWL_POS = new THREE.Vector3(0.4, 0, 1.9);
const BOWL_EAT = new THREE.Vector3(0.4, 0, 1.15);
{
  const bowl = mesh(new THREE.CylinderGeometry(0.42, 0.3, 0.22, 8), mat(0xf4a261));
  bowl.position.set(BOWL_POS.x, 0.11, BOWL_POS.z);
  scene.add(bowl);
  const seedMat = mat(0x6f4e37);
  for (let i = 0; i < 7; i++) {
    const a = Math.random() * Math.PI * 2, r = Math.random() * 0.22;
    scene.add(mesh(new THREE.SphereGeometry(0.05, 5, 4), seedMat,
      BOWL_POS.x + Math.cos(a) * r, 0.24, BOWL_POS.z + Math.sin(a) * r));
  }
}

// --- Wood shaving confetti ---
const shavingColors = [0xf0dcae, 0xe3c893, 0xd9bd85];
for (let i = 0; i < 40; i++) {
  const s = mesh(new THREE.BoxGeometry(0.18, 0.03, 0.1),
    mat(shavingColors[i % 3]),
    (Math.random() - 0.5) * (CAGE.w - 1),
    0.22,
    (Math.random() - 0.5) * (CAGE.d - 1));
  s.rotation.set(0, Math.random() * Math.PI, 0);
  scene.add(s);
}

/* ---------------------------------------------------------------
   HAMSTERS
---------------------------------------------------------------- */
const hamsters = [];

function createHamster(fur, belly) {
  const g = new THREE.Group();

  const body = mesh(new THREE.SphereGeometry(0.42, 7, 5), mat(fur));
  body.scale.set(1.25, 0.95, 1.05);
  body.position.y = 0.45;
  g.add(body);

  const head = mesh(new THREE.SphereGeometry(0.3, 7, 5), mat(fur), 0.42, 0.55, 0);
  g.add(head);

  const belly = mesh(new THREE.SphereGeometry(0.28, 6, 4), mat(belly), 0.35, 0.38, 0);
  belly.scale.set(1.1, 0.8, 1.1);
  g.add(belly);

  const earGeo = new THREE.SphereGeometry(0.09, 5, 4);
  const earL = mesh(earGeo, mat(fur), 0.42, 0.82, 0.16);
  const earR = mesh(earGeo, mat(fur), 0.42, 0.82, -0.16);
  g.add(earL, earR);

  const eyeGeo = new THREE.SphereGeometry(0.05, 5, 4);
  const eyeMat = mat(0x222222, { roughness: 0.3 });
  const eyeL = mesh(eyeGeo, eyeMat, 0.66, 0.62, 0.13);
  const eyeR = mesh(eyeGeo, eyeMat, 0.66, 0.62, -0.13);
  g.add(eyeL, eyeR);

  const nose = mesh(new THREE.SphereGeometry(0.05, 5, 4), mat(0xff7eb6), 0.72, 0.52, 0);
  g.add(nose);

  const cheekL = mesh(new THREE.SphereGeometry(0.09, 5, 4), mat(0xffc2d4), 0.6, 0.46, 0.2);
  const cheekR = mesh(new THREE.SphereGeometry(0.09, 5, 4), mat(0xffc2d4), 0.6, 0.46, -0.2);
  g.add(cheekL, cheekR);

  const tail = mesh(new THREE.SphereGeometry(0.07, 5, 4), mat(fur), -0.55, 0.45, 0);
  g.add(tail);

  const footGeo = new THREE.SphereGeometry(0.07, 5, 4);
  [[0.35, 0.18], [0.35, -0.18], [-0.35, 0.18], [-0.35, -0.18]].forEach(([fx, fz]) =>
    g.add(mesh(footGeo, mat(belly), fx, 0.08, fz)));

  scene.add(g);

  return {
    group: g, body, head, eyeL, eyeR,
    pos: g.position,
    yaw: Math.random() * Math.PI * 2,
    speed: 1.1 + Math.random() * 0.4,
    state: 'wander',
    timer: 1 + Math.random() * 2,
    targetDir: Math.random() * Math.PI * 2,
    target: null,
    blinkTimer: 2 + Math.random() * 4,
    bobPhase: Math.random() * 10,
    onWheel: false
  };
}

hamsters.push(createHamster(0xf4a261, 0xfff1dc)); // golden
hamsters.push(createHamster(0xfdf6ec, 0xffe8cc)); // cream
hamsters.push(createHamster(0xa8a29e, 0xe7e5e4)); // grey
hamsters.push(createHamster(0xffc9a3, 0xfff5ea)); // peach

/* ---------------------------------------------------------------
   SIMPLE AI  (wander / pause / wheel / eat)
---------------------------------------------------------------- */
const tmpVec = new THREE.Vector3();

function setTarget(h, point) {
  h.target = point.clone();
  h.timer = 10; // generous timeout
}

function updateHamster(h, dt, t) {
  h.timer -= dt;

  switch (h.state) {
    case 'wander': {
      const dir = h.targetDir;
      h.pos.x += Math.sin(dir) * h.speed * dt;
      h.pos.z += Math.cos(dir) * h.speed * dt;
      h.yaw = dir + Math.PI / 2;
      if (h.timer <= 0) {
        const r = Math.random();
        if (r < 0.22) { h.state = 'pause'; h.timer = 0.8 + Math.random() * 1.8; }
        else if (r < 0.38) { h.state = 'toWheel'; setTarget(h, WHEEL_STAND); }
        else if (r < 0.52) { h.state = 'toBowl'; setTarget(h, BOWL_EAT); }
        else { h.state = 'wander'; h.timer = 1 + Math.random() * 2.5;
               h.targetDir = Math.random() * Math.PI * 2; }
      }
      break;
    }
    case 'pause': {
      if (h.timer <= 0) {
        h.state = 'wander';
        h.timer = 1 + Math.random() * 2;
        h.targetDir = Math.random() * Math.PI * 2;
      }
      break;
    }
    case 'toWheel': case 'toBowl': {
      const arrived = moveToward(h, h.target, dt);
      if (arrived || h.timer <= 0) {
        if (h.state === 'toWheel') { h.state = 'onWheel'; h.onWheel = true; h.timer = 3 + Math.random() * 2.5; }
        else                       { h.state = 'eating';  h.timer = 1.5 + Math.random() * 1.5; }
      }
      break;
    }
    case 'onWheel': {
      if (h.timer <= 0) { h.state = 'wander'; h.onWheel = false;
                          h.timer = 1.5; h.targetDir = Math.random() * Math.PI * 2; }
      break;
    }
    case 'eating': {
      if (h.timer <= 0) { h.state = 'wander';
                          h.timer = 1.5; h.targetDir = Math.random() * Math.PI * 2; }
      break;
    }
  }

  /* Keep inside the cage — bump off walls */
  if (Math.abs(h.pos.x) > CAGE.bx || Math.abs(h.pos.z) > CAGE.bz) {
    h.pos.x = THREE.MathUtils.clamp(h.pos.x, -CAGE.bx, CAGE.bx);
    h.pos.z = THREE.MathUtils.clamp(h.pos.z, -CAGE.bz, CAGE.bz);
    h.targetDir = Math.atan2(-Math.sin(h.targetDir), -Math.cos(h.targetDir)) + (Math.random() - 0.5);
  }

  /* Gentle hamster-vs-hamster separation (fluffy pushy friends) */
  for (const o of hamsters) {
    if (o === h) continue;
    const dx = h.pos.x - o.pos.x, dz = h.pos.z - o.pos.z;
    const d2 = dx * dx + dz * dz;
    if (d2 < 0.45 && d2 > 0.0001) {
      const d = Math.sqrt(d2);
      h.pos.x += (dx / d) * 0.03;
      h.pos.z += (dz / d) * 0.03;
    }
  }

  /* Apply yaw + idle bobbing / activity animation */
  h.group.rotation.y = h.yaw;

  const moving = (h.state === 'wander') || h.state === 'toWheel' || h.state === 'toBowl';
  let bobY = 0, headTilt = 0;
  if (moving) {
    bobY = Math.sin(t * 14 + h.bobPhase) * 0.04;
  } else if (h.state === 'onWheel') {
    bobY = Math.abs(Math.sin(t * 10 + h.bobPhase)) * 0.12; // scurrying!
  } else if (h.state === 'eating') {
    headTilt = Math.sin(t * 8 + h.bobPhase) * 0.35 + 0.3;  // nibbling
  } else if (h.state === 'pause') {
    bobY = Math.sin(t * 3 + h.bobPhase) * 0.02;            // breathing
  }
  h.body.position.y = 0.45 + bobY;
  h.head.rotation.x = headTilt;

  /* Blinking */
  h.blinkTimer -= dt;
  if (h.blinkTimer <= 0) h.blinkTimer = 2 + Math.random() * 4;
  const squish = h.blinkTimer < 0.15 ? 0.1 : 1;
  h.eyeL.scale.y += (squish - h.eyeL.scale.y) * 0.6;
  h.eyeR.scale.y = h.eyeL.scale.y;
}

function moveToward(h, target, dt) {
  tmpVec.subVectors(target, h.pos);
  tmpVec.y = 0;
  const dist = tmpVec.length();
  if (dist < 0.2) return true;
  const dir = Math.atan2(tmpVec.x, tmpVec.z);
  h.yaw = dir + Math.PI / 2;
  h.pos.x += (tmpVec.x / dist) * h.speed * dt;
  h.pos.z += (tmpVec.z / dist) * h.speed * dt;
  return false;
}

/* ---------------------------------------------------------------
   MAIN LOOP
---------------------------------------------------------------- */
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  hamsters.forEach((h, i) => updateHamster(h, dt, t + i));

  // Wheel spins when someone is using it
  const anyoneOnWheel = hamsters.some(h => h.onWheel);
  wheelSpeed += ((anyoneOnWheel ? 7 : 0) - wheelSpeed) * Math.min(dt * 2.5, 1);
  wheel.rotation.z -= wheelSpeed * dt;

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

**Scene contents**
- 🏠 A cage with a blue tray, sandy bedding, subtle glass walls, and a metal bar frame
- 🎡 A pink exercise wheel with spokes and a green stand
- 🟢 A green half-pipe tunnel
- 🥣 An orange food bowl with seed pellets
- ✨ Scattered wood shavings for cozy detail

**The hamsters** (4 of them: golden, cream, grey, peach)
- Built entirely from flat-shaded low-poly spheres — big heads, blushing cheeks, tiny tails
- **Autonomous AI**: they wander, pause (with breathing idle), scurry to the wheel (which starts spinning!), and nibble at the food bowl (head bobbing)
- They bump gently off each other like fluffy pushy friends, and bounce off the cage walls
- Random blinking for extra charm

**Interaction**
- Drag to orbit, scroll to zoom (OrbitControls with smooth damping)

Everything runs straight from the file — no build step, no assets, just Three.js from a CDN.