

# Low-Poly Hamster Playground 🐹

Here's a complete single-file project. Save it as `index.html` and open it in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #ffe9d6; }
  #info {
    position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
    font-family: 'Comic Sans MS', 'Chalkboard SE', cursive, sans-serif;
    color: #7a4a2b; background: rgba(255,255,255,.75); padding: 8px 18px;
    border-radius: 20px; font-size: 15px; pointer-events: none;
    box-shadow: 0 3px 10px rgba(0,0,0,.1);
  }
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
<div id="info">🐹 Low-Poly Hamster Playground — drag to rotate, scroll to zoom</div>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ---------- Renderer / Scene / Camera ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9d6);
scene.fog = new THREE.Fog(0xffe9d6, 30, 60);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(9, 7, 11);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI * 0.49;
controls.minDistance = 5;
controls.maxDistance = 25;

// ---------- Lights ----------
scene.add(new THREE.AmbientLight(0xfff2e0, 0.7));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12;  sun.shadow.camera.bottom = -12;
scene.add(sun);
const fill = new THREE.DirectionalLight(0xaad4ff, 0.35);
fill.position.set(-6, 5, -8);
scene.add(fill);

// ---------- Helpers ----------
const mat = (color) => new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9 });
function box(w, h, d, color, x=0, y=0, z=0, parent=scene) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(color));
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  parent.add(m);
  return m;
}
function ball(r, color, x=0, y=0, z=0, parent=scene) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(r, 7, 6), mat(color));
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  parent.add(m);
  return m;
}

// ---------- Ground (outside cage) ----------
const ground = new THREE.Mesh(new THREE.CylinderGeometry(14, 14, 0.5, 10), mat(0xc9e8a8));
ground.position.y = -0.25;
ground.receiveShadow = true;
scene.add(ground);

// ---------- Cage ----------
const CAGE = { w: 10, d: 7, h: 3.2 }; // interior half-sizes handled below
const HW = CAGE.w / 2, HD = CAGE.d / 2, CH = CAGE.h;

// Tray / floor
box(CAGE.w + 0.8, 0.5, CAGE.d + 0.8, 0x6fb7d9, 0, -0.25, 0);           // outer tray
box(CAGE.w, 0.35, CAGE.d, 0xf5deb3, 0, 0.05, 0);                        // bedding
// scattered bedding bits
for (let i = 0; i < 26; i++) {
  const b = box(0.22, 0.08, 0.22, i % 2 ? 0xe8cfa0 : 0xd9b98a,
    (Math.random() - 0.5) * (CAGE.w - 1), 0.24, (Math.random() - 0.5) * (CAGE.d - 1));
  b.rotation.y = Math.random() * Math.PI;
}

// Cage walls (glass-ish front/back transparent, solid sides)
const glassMat = new THREE.MeshStandardMaterial({
  color: 0xbfe6ff, transparent: true, opacity: 0.18, roughness: 0.1, side: THREE.DoubleSide
});
function panel(w, h, x, y, z, ry, material) {
  const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), material);
  p.position.set(x, y, z); p.rotation.y = ry;
  scene.add(p);
  return p;
}
panel(CAGE.w, CH, 0, CH / 2 + 0.2, -HD, 0, glassMat);          // back
panel(CAGE.w, CH, 0, CH / 2 + 0.2,  HD, 0, glassMat);          // front
panel(CAGE.d, CH, -HW, CH / 2 + 0.2, 0, Math.PI / 2, glassMat);// left
panel(CAGE.d, CH,  HW, CH / 2 + 0.2, 0, Math.PI / 2, glassMat);// right

// Wire frame
const barMat = new THREE.MeshStandardMaterial({ color: 0x555a66, roughness: 0.5, metalness: 0.4 });
function bar(len, x, y, z, horizontal, axis) {
  const g = horizontal
    ? new THREE.CylinderGeometry(0.05, 0.05, len, 6)
    : new THREE.CylinderGeometry(0.05, 0.05, len, 6);
  const m = new THREE.Mesh(g, barMat);
  m.position.set(x, y, z);
  if (horizontal) m.rotation.z = axis === 'x' ? Math.PI / 2 : 0;
  scene.add(m);
}
const topY = CH + 0.2;
bar(CAGE.w, 0, topY, -HD, true, 'x'); bar(CAGE.w, 0, topY, HD, true, 'x');
bar(CAGE.w, 0, 0.2, -HD, true, 'x');  bar(CAGE.w, 0, 0.2, HD, true, 'x');
bar(CAGE.d, -HW, topY, 0, true, 'z'); bar(CAGE.d,  HW, topY, 0, true, 'z');
bar(CAGE.d, -HW, 0.2, 0, true, 'z');  bar(CAGE.d,  HW, 0.2, 0, true, 'z');
for (let x = -HW; x <= HW + 0.01; x += CAGE.w / 5) {
  bar(CH, x, topY / 2 + 0.1, -HD, false);
  bar(CH, x, topY / 2 + 0.1,  HD, false);
}
for (let z = -HD; z <= HD + 0.01; z += CAGE.d / 4) {
  bar(CH, -HW, topY / 2 + 0.1, z, false);
  bar(CH,  HW, topY / 2 + 0.1, z, false);
}
// mid rails
bar(CAGE.w, 0, topY / 2 + 0.1, -HD, true, 'x');
bar(CAGE.w, 0, topY / 2 + 0.1,  HD, true, 'x');

// ---------- Interactive objects ----------
// Wheel
const wheelGroup = new THREE.Group();
wheelGroup.position.set(-HW + 1.1, 0.2, -HD + 1.1);
scene.add(wheelGroup);
const rim = new THREE.Mesh(new THREE.TorusGeometry(0.95, 0.09, 6, 18), mat(0xff8fab));
rim.castShadow = true;
wheelGroup.add(rim);
const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.3, 6), mat(0xffd166));
hub.rotation.x = Math.PI / 2;
wheelGroup.add(hub);
for (let i = 0; i < 6; i++) {
  const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.9, 5), mat(0xffd166));
  spoke.position.set(Math.cos(i * Math.PI / 3) * 0.47, Math.sin(i * Math.PI / 3) * 0.47, 0);
  spoke.rotation.z = i * Math.PI / 3;
  wheelGroup.add(spoke);
}
const wheelStand = box(0.15, 0.5, 0.15, 0x555a66, 0, -0.95, 0, wheelGroup);
wheelStand.position.y = -0.95;
wheelGroup.position.y = 1.15;
const WHEEL_POS = new THREE.Vector3(-HW + 1.1, 0.2, -HD + 1.1);

// Food bowl
const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.4, 0.3, 8, 1, true), mat(0x9b5de5));
bowl.position.set(HW - 1.1, 0.35, HD - 1.1);
bowl.castShadow = true;
scene.add(bowl);
const seeds = new THREE.Group();
seeds.position.copy(bowl.position);
for (let i = 0; i < 8; i++) {
  const s = ball(0.09, [0xf4a261, 0xe9c46a, 0xc9ada7][i % 3],
    (Math.random() - 0.5) * 0.5, 0.25, (Math.random() - 0.5) * 0.5, seeds);
}
scene.add(seeds);
const BOWL_POS = new THREE.Vector3(HW - 1.1, 0.2, HD - 1.1);

// Tunnel
const tunnel = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 2.4, 8, 1, true, 0, Math.PI),
  new THREE.MeshStandardMaterial({ color: 0x06d6a0, flatShading: true, roughness: 0.9, side: THREE.DoubleSide }));
tunnel.rotation.z = Math.PI / 2;
tunnel.rotation.y = Math.PI / 4;
tunnel.position.set(0.8, 0.85, 0.5);
tunnel.castShadow = tunnel.receiveShadow = true;
scene.add(tunnel);
const tunnelBase = box(2.6, 0.15, 1.5, 0x04b892, 0.8, 0.28, 0.5);
tunnelBase.rotation.y = Math.PI / 4;

// Little ball toy
const toyBall = ball(0.3, 0xef476f, 2.5, 0.5, 1.5);

// ---------- Hamsters ----------
const HAMSTER_COLORS = [
  { body: 0xf4a261, cheek: 0xffe0b3, name: 'Nutty' },
  { body: 0xd9d9d9, cheek: 0xffffff, name: 'Snowy' },
  { body: 0x9b6b3f, cheek: 0xe8cfa0, name: 'Biscuit' },
];

function makeHamster(colors) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.45, 0), mat(colors.body));
  body.scale.set(1.25, 0.85, 1);
  body.position.y = 0.45;
  body.castShadow = true;
  g.add(body);

  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.32, 0), mat(colors.body));
  head.position.set(0.45, 0.62, 0);
  head.castShadow = true;
  g.add(head);

  // cheeks
  ball(0.13, colors.cheek, 0.55, 0.52,  0.18, g);
  ball(0.13, colors.cheek, 0.55, 0.52, -0.18, g);
  // eyes
  ball(0.06, 0x222222, 0.68, 0.7,  0.14, g);
  ball(0.06, 0x222222, 0.68, 0.7, -0.14, g);
  // nose
  ball(0.05, 0xff7096, 0.78, 0.58, 0, g);
  // ears
  const earGeo = new THREE.ConeGeometry(0.1, 0.16, 5);
  const earL = new THREE.Mesh(earGeo, mat(colors.body));
  earL.position.set(0.4, 0.95, 0.14); earL.castShadow = true; g.add(earL);
  const earR = earL.clone(); earR.position.z = -0.14; g.add(earR);
  // tail nub
  ball(0.08, colors.cheek, -0.58, 0.42, 0, g);

  // feet (little stubs that waddle)
  const footGeo = new THREE.BoxGeometry(0.12, 0.1, 0.12);
  const feet = [];
  [[0.3, 0.22], [0.3, -0.22], [-0.3, 0.22], [-0.3, -0.22]].forEach(([fx, fz]) => {
    const f = new THREE.Mesh(footGeo, mat(colors.body));
    f.position.set(fx, 0.06, fz);
    g.add(f); feet.push(f);
  });

  g.userData = {
    state: 'wander', timer: 1 + Math.random() * 3,
    target: null, heading: Math.random() * Math.PI * 2,
    speed: 0.9 + Math.random() * 0.5,
    walkPhase: Math.random() * 10,
    feet, body, head,
  };
  return g;
}

const hamsters = [];
HAMSTER_COLORS.forEach((c, i) => {
  const h = makeHamster(c);
  h.position.set((Math.random() - 0.5) * 5, 0.2, (Math.random() - 0.5) * 4);
  scene.add(h);
  hamsters.push(h);
});

// ---------- Behavior ----------
const rand = (a, b) => a + Math.random() * (b - a);

function pickTarget(h) {
  const r = Math.random();
  if (r < 0.25) return { pos: WHEEL_POS.clone().add(new THREE.Vector3(0.6, 0, 0)), kind: 'wheel' };
  if (r < 0.5)  return { pos: BOWL_POS.clone().add(new THREE.Vector3(-0.6, 0, 0)), kind: 'bowl' };
  if (r < 0.65) return { pos: toyBall.position.clone().setY(0.2).add(new THREE.Vector3(0.5, 0, 0)), kind: 'toy' };
  return {
    pos: new THREE.Vector3(rand(-HW + 0.8, HW - 0.8), 0.2, rand(-HD + 0.8, HD - 0.8)),
    kind: 'wander'
  };
}

function updateHamster(h, dt) {
  const u = h.userData;
  u.timer -= dt;

  switch (u.state) {
    case 'wander': {
      if (!u.target || u.timer <= 0) {
        u.target = pickTarget(h);
        u.timer = rand(3, 7);
      }
      // steer toward target
      const to = u.target.pos.clone().sub(h.position); to.y = 0;
      const dist = to.length();
      if (dist < 0.5) {
        if (u.target.kind === 'wheel') { u.state = 'atWheel'; u.timer = rand(2.5, 4.5); }
        else if (u.target.kind === 'bowl') { u.state = 'eating'; u.timer = rand(1.5, 3); }
        else if (u.target.kind === 'toy') { u.state = 'playing'; u.timer = rand(1, 2); }
        else { u.state = 'pause'; u.timer = rand(1, 3); }
      } else {
        const want = Math.atan2(to.x, to.z);
        let diff = want - h.rotation.y;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        h.rotation.y += THREE.MathUtils.clamp(diff, -dt * 2.5, dt * 2.5);
        h.position.add(new THREE.Vector3(Math.sin(h.rotation.y), 0, Math.cos(h.rotation.y)).multiplyScalar(u.speed * dt));
        u.walkPhase += dt * 10;
      }
      break;
    }
    case 'atWheel': {
      h.position.lerp(WHEEL_POS.clone().add(new THREE.Vector3(0.55, 0, 0)), dt * 3);
      h.lookAt(WHEEL_POS.x, 1.15, WHEEL_POS.z);
      u.walkPhase += dt * 16;
      wheelSpin += dt * 6;
      if (u.timer <= 0) { u.state = 'pause'; u.timer = rand(1, 2.5); }
      break;
    }
    case 'eating': {
      h.lookAt(BOWL_POS.x, 0.5, BOWL_POS.z);
      u.head.position.y = 0.62 + Math.sin(performance.now() * 0.02) * 0.06; // nibble bob
      if (u.timer <= 0) { u.head.position.y = 0.62; u.state = 'pause'; u.timer = rand(0.5, 1.5); }
      break;
    }
    case 'playing': {
      h.lookAt(toyBall.position);
      h.position.add(new THREE.Vector3(Math.sin(performance.now() * 0.01) * dt * 0.4, 0, 0));
      if (u.timer <= 0) {
        toyBall.position.x += rand(-1.5, 1.5);
        toyBall.position.z += rand(-1.5, 1.5);
        toyBall.position.x = THREE.MathUtils.clamp(toyBall.position.x, -HW + 0.6, HW - 0.6);
        toyBall.position.z = THREE.MathUtils.clamp(toyBall.position.z, -HD + 0.6, HD - 0.6);
        u.state = 'pause'; u.timer = rand(1, 2);
      }
      break;
    }
    case 'pause': {
      if (u.timer <= 0) u.state = 'wander';
      break;
    }
  }

  // keep inside cage
  h.position.x = THREE.MathUtils.clamp(h.position.x, -HW + 0.6, HW - 0.6);
  h.position.z = THREE.MathUtils.clamp(h.position.z, -HD + 0.6, HD - 0.6);

  // waddle animation
  const moving = u.state === 'wander' || u.state === 'atWheel';
  const amp = moving ? 0.08 : 0.015;
  const t = u.walkPhase;
  u.feet[0].position.y = 0.06 + Math.abs(Math.sin(t)) * amp;
  u.feet[1].position.y = 0.06 + Math.abs(Math.sin(t + Math.PI)) * amp;
  u.feet[2].position.y = 0.06 + Math.abs(Math.sin(t + Math.PI)) * amp;
  u.feet[3].position.y = 0.06 + Math.abs(Math.sin(t)) * amp;
  u.body.position.y = 0.45 + Math.sin(t * 2) * (moving ? 0.03 : 0.008);
  u.body.rotation.z = Math.sin(t) * (moving ? 0.08 : 0.02);
  if (u.state !== 'eating') u.head.position.y = 0.62 + Math.sin(t * 2 + 1) * 0.02;
}

// ---------- Loop ----------
let wheelSpin = 0;
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);

  hamsters.forEach(h => updateHamster(h, dt));

  // wheel spins down slowly when no hamster is running on it
  wheelGroup.rotation.z -= wheelSpin * dt;
  wheelSpin = Math.max(0, wheelSpin - dt * 2);

  // toy ball gentle idle bounce
  toyBall.position.y = 0.5 + Math.abs(Math.sin(performance.now() * 0.003)) * 0.1;

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

**Scene contents:**
- 🏠 **Cage** — blue tray, straw bedding with scattered bits, translucent glass walls, gray wire frame with mid-rails
- 🎡 **Running wheel** — pink rim, yellow spokes; spins up when a hamster runs on it and coasts down after
- 🥣 **Food bowl** — purple bowl with seed "mound"; hamsters do a bobbing nibble animation
- 🌈 **Tunnel** — green half-cylinder arch
- ⚽ **Toy ball** — hamsters bat it around the cage

**Hamster behavior (simple state machine):**
- `wander` → picks a random goal (wheel, bowl, toy, or open space) and steers toward it
- `atWheel` → runs in place, spinning the wheel
- `eating` → faces the bowl, head bobs while nibbling
- `playing` → bats the toy ball, which gets knocked to a new spot
- `pause` → idles with a subtle breathing waddle

**Visual details:** all meshes use `flatShading` for the low-poly look, icosahedron bodies with stubby waddling feet, blush cheeks, cone ears, and soft shadows. Camera uses damped OrbitControls with sensible limits so you can't go under the floor.

Just open the file — no build step, no server needed.