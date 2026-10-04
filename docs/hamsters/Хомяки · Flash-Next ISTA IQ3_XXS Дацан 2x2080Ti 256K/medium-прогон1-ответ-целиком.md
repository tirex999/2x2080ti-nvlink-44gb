# 🐹 Low-Poly Hamster Playground

A complete single-file project. Save it as `index.html` and open in any modern browser — no build step needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #ffe9f0; }
  #hud {
    position: fixed; top: 14px; left: 16px; z-index: 10;
    font-family: "Comic Sans MS", "Segoe UI", sans-serif;
    color: #5a3b2c; pointer-events: none;
    text-shadow: 0 1px 0 rgba(255,255,255,.7);
  }
  #hud h1 { margin: 0; font-size: 22px; }
  #hud p  { margin: 4px 0 0; font-size: 13px; opacity: .8; }
</style>
</head>
<body>
<div id="hud">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate &nbsp;•&nbsp; Scroll to zoom &nbsp;•&nbsp; Watch them run, snack &amp; nap</p>
</div>

<script type="importmap">
{ "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
} }
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============ BASICS ============ */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9f0);
scene.fog = new THREE.Fog(0xffe9f0, 22, 40);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(9, 8, 11);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.4, 0);
controls.enableDamping = true;
controls.minDistance = 5;
controls.maxDistance = 24;
controls.maxPolarAngle = Math.PI * 0.49;

/* Lights */
scene.add(new THREE.HemisphereLight(0xbfd4ff, 0xf5c9a0, 0.9));
const sun = new THREE.DirectionalLight(0xfff2d8, 1.2);
sun.position.set(8, 12, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -9; sun.shadow.camera.right = 9;
sun.shadow.camera.top = 9;   sun.shadow.camera.bottom = -9;
scene.add(sun);

/* Helper: cute flat-shaded material */
const mat = (c, opts = {}) => new THREE.MeshStandardMaterial({ color: c, flatShading: true, roughness: .9, ...opts });

const TRAY_TOP = 0.45;

/* ============ TRAY + BEDDING ============ */
const tray = new THREE.Mesh(new THREE.CylinderGeometry(6, 6.35, TRAY_TOP, 26), mat(0xf2d3a7));
tray.position.y = TRAY_TOP / 2;
tray.receiveShadow = true;
scene.add(tray);

// wood chips
const chipGeo = new THREE.BoxGeometry(0.22, 0.07, 0.12);
for (let i = 0; i < 34; i++) {
  const chip = new THREE.Mesh(chipGeo, mat([0xd9b06f, 0xc79a58, 0xe6c98a][i % 3]));
  const a = Math.random() * Math.PI * 2, r = Math.sqrt(Math.random()) * 5.1;
  chip.position.set(Math.cos(a) * r, TRAY_TOP + 0.035, Math.sin(a) * r);
  chip.rotation.y = Math.random() * Math.PI;
  chip.rotation.z = (Math.random() - .5) * .5;
  chip.receiveShadow = true;
  scene.add(chip);
}

/* ============ CAGE BARS ============ */
const barMat = new THREE.MeshStandardMaterial({ color: 0xb8c0cc, metalness: .55, roughness: .35 });
const barGeo = new THREE.CylinderGeometry(0.06, 0.06, 3.4, 6);
for (let i = 0; i < 22; i++) {
  const a = (i / 22) * Math.PI * 2;
  const bar = new THREE.Mesh(barGeo, barMat);
  bar.position.set(Math.cos(a) * 5.9, TRAY_TOP + 1.7, Math.sin(a) * 5.9);
  bar.castShadow = true;
  scene.add(bar);
}
for (const y of [TRAY_TOP + 0.15, TRAY_TOP + 3.3]) {
  const ring = new THREE.Mesh(new THREE.TorusGeometry(5.9, 0.08, 6, 40), barMat);
  ring.rotation.x = Math.PI / 2;
  ring.position.y = y;
  scene.add(ring);
}

/* ============ HAMSTER WHEEL (interactive) ============ */
const wheelGroup = new THREE.Group();
wheelGroup.position.set(-3.4, TRAY_TOP, -1.5);
wheelGroup.rotation.y = 0.5;
scene.add(wheelGroup);

const plasticMat = mat(0xe86a6a);
for (const s of [1.32, -1.32]) {          // side supports
  const leg = new THREE.Mesh(new THREE.BoxGeometry(0.14, 1.55, 0.4), plasticMat);
  leg.position.set(s, 0.78, 0);
  leg.castShadow = true;
  wheelGroup.add(leg);
}
const base = new THREE.Mesh(new THREE.BoxGeometry(3.1, 0.18, 0.55), plasticMat);
base.position.y = 0.09; base.castShadow = true;
wheelGroup.add(base);

const wheelSpin = new THREE.Group();      // rotating part
wheelSpin.position.y = 1.35;
wheelGroup.add(wheelSpin);

const rim = new THREE.Mesh(new THREE.TorusGeometry(1.22, 0.13, 6, 18), mat(0xf6f0e6));
rim.rotation.y = Math.PI / 2;             // wheel plane = YZ, axis = X
rim.castShadow = true;
wheelSpin.add(rim);

const plateMat = mat(0xfad4d4, { transparent: true, opacity: 0.35 });
for (const s of [0.2, -0.2]) {
  const plate = new THREE.Mesh(new THREE.CylinderGeometry(1.15, 1.15, 0.06, 18), plateMat);
  plate.rotation.z = Math.PI / 2;
  plate.position.x = s;
  wheelSpin.add(plate);
}
for (let i = 0; i < 8; i++) {             // running rungs
  const a = (i / 8) * Math.PI * 2;
  const rung = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.26, 0.07), mat(0xe9dcc3));
  rung.position.set(0, Math.cos(a) * 1.05, Math.sin(a) * 1.05);
  rung.rotation.x = -a - Math.PI / 2;
  wheelSpin.add(rung);
}

/* ============ FOOD BOWL ============ */
const bowlPos = new THREE.Vector3(2.7, TRAY_TOP, 2.3);
const bowl = new THREE.Group();
bowl.position.copy(bowlPos);
const bowlMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.4, 0.36, 12), mat(0x4fa3d1));
bowlMesh.position.y = 0.18; bowlMesh.castShadow = true;
bowl.add(bowlMesh);
const food = new THREE.Group(); food.position.y = 0.34;
for (let i = 0; i < 7; i++) {
  const f = new THREE.Mesh(new THREE.IcosahedronGeometry(0.1, 0), mat([0x8fbf5c, 0xb07b4f, 0xd9a441][i % 3]));
  const a = (i / 7) * Math.PI * 2;
  f.position.set(Math.cos(a) * 0.24, Math.random() * 0.08, Math.sin(a) * 0.24);
  food.add(f);
}
bowl.add(food);
scene.add(bowl);

/* ============ TUNNEL (decor) ============ */
const tunnel = new THREE.Group();
tunnel.position.set(1.2, TRAY_TOP + 0.7, -3.2);
const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.72, 0.72, 2.4, 10, 1, true), mat(0x7ec8a6, { side: THREE.DoubleSide }));
tube.rotation.z = Math.PI / 2; tube.castShadow = true;
tunnel.add(tube);
for (const s of [1.2, -1.2]) {
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.74, 0.08, 6, 14), mat(0x5aa988));
  ring.rotation.y = Math.PI / 2; ring.position.x = s;
  tunnel.add(ring);
}
scene.add(tunnel);

/* ============ HAMSTERS ============ */
const COLORS = [0xe8a05c, 0xf3d9b1, 0xc96f4a, 0x8d7b6a];

function createHamster(color) {
  const g = new THREE.Group();
  const bodyMat = mat(color);
  const bellyMat = mat(new THREE.Color(color).lerp(new THREE.Color(0xffffff), 0.5));

  const bodyGroup = new THREE.Group();
  g.add(bodyGroup);

  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 1), bodyMat);
  body.scale.set(1.15, 1.0, 1.28);
  body.position.y = 0.44;
  body.castShadow = true;
  bodyGroup.add(body);

  const belly = new THREE.Mesh(new THREE.IcosahedronGeometry(0.3, 1), bellyMat);
  belly.scale.set(0.9, 0.8, 1.0);
  belly.position.set(0, 0.34, 0.22);
  bodyGroup.add(belly);

  const tail = new THREE.Mesh(new THREE.IcosahedronGeometry(0.09, 0), bodyMat);
  tail.position.set(0, 0.4, -0.56);
  bodyGroup.add(tail);

  // head
  const head = new THREE.Group();
  head.position.set(0, 0.66, 0.4);
  bodyGroup.add(head);
  const skull = new THREE.Mesh(new THREE.IcosahedronGeometry(0.3, 1), bodyMat);
  skull.scale.set(1, 0.95, 0.9);
  skull.castShadow = true;
  head.add(skull);
  for (const s of [1, -1]) {
    const cheek = new THREE.Mesh(new THREE.IcosahedronGeometry(0.13, 0), bellyMat);
    cheek.position.set(s * 0.21, -0.05, 0.12);
    head.add(cheek);
    const ear = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.17, 5), bodyMat);
    ear.position.set(s * 0.17, 0.28, -0.02);
    ear.rotation.z = s * -0.35;
    head.add(ear);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 6, 6), new THREE.MeshBasicMaterial({ color: 0x1a1a1a }));
    eye.position.set(s * 0.13, 0.06, 0.26);
    head.add(eye);
  }
  const nose = new THREE.Mesh(new THREE.IcosahedronGeometry(0.05, 0), mat(0xf28a8a));
  nose.position.set(0, -0.02, 0.3);
  head.add(nose);

  // legs (pivot at hip so they can swing)
  const legs = [];
  for (const [x, z] of [[0.24, 0.3], [-0.24, 0.3], [0.24, -0.3], [-0.24, -0.3]]) {
    const hip = new THREE.Group();
    hip.position.set(x, 0.2, z);
    bodyGroup.add(hip);
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.08, 0.22, 5), bodyMat);
    leg.position.y = -0.11;
    leg.castShadow = true;
    hip.add(leg);
    legs.push(hip);
  }

  g.scale.setScalar(0.9);
  return { group: g, bodyGroup, head, legs };
}

const hamsters = [];
const wheelPoint = new THREE.Vector3(wheelGroup.position.x, TRAY_TOP, wheelGroup.position.z);
const wheelHeading = Math.atan2(-Math.sin(wheelGroup.rotation.y), -Math.cos(wheelGroup.rotation.y)) + Math.PI;

for (let i = 0; i < 4; i++) {
  const parts = createHamster(COLORS[i]);
  const a = (i / 4) * Math.PI * 2 + 0.7;
  parts.group.position.set(Math.cos(a) * 3, TRAY_TOP, Math.sin(a) * 3);

  hamsters.push({
    ...parts,
    state: 'idle',
    timer: 1 + Math.random() * 2,
    heading: a + Math.PI,
    target: new THREE.Vector3(),
    phase: Math.random() * 10,
    wheelSpinSpeed: 0,
  });
}

let wheelUser = null, bowlUser = null;

/* ============ BEHAVIOR ============ */
const wrapAngle = a => { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; };

function pickTarget(h) {
  const a = Math.random() * Math.PI * 2, r = 1.5 + Math.random() * 3.2;
  h.target.set(Math.cos(a) * r, TRAY_TOP, Math.sin(a) * r);
}

function setState(h, state) {
  // release shared resources
  if (wheelUser === h) wheelUser = null;
  if (bowlUser === h) bowlUser = null;

  h.state = state;
  if (state === 'idle') h.timer = 1 + Math.random() * 2.5;
  if (state === 'walk') { h.timer = 8; pickTarget(h); }
  if (state === 'wheel' && !wheelUser) { wheelUser = h; h.timer = 4 + Math.random() * 4; h.target.copy(wheelPoint); }
  if (state === 'eat' && !bowlUser) {
    bowlUser = h; h.timer = 2.5 + Math.random() * 3;
    const out = bowlPos.clone().setY(0).normalize();
    h.target.copy(bowlPos).addScaledVector(out, 0.85); h.target.y = TRAY_TOP;
  }
  if (state === 'wheel' || state === 'eat') if (wheelUser !== h && bowlUser !== h) setState(h, 'walk');
}

function chooseNext(h) {
  const r = Math.random();
  if (r < 0.3 && !wheelUser) setState(h, 'wheel');
  else if (r < 0.5 && !bowlUser) setState(h, 'eat');
  else if (r < 0.8) setState(h, 'walk');
  else setState(h, 'idle');
}

function updateHamster(h, dt, t) {
  h.timer -= dt;
  const pos = h.group.position;
  let legSpeed = 0, legAmp = 0;

  if (h.state === 'idle') {
    // cute breathing
    h.bodyGroup.scale.y = 1 + Math.sin(t * 3 + h.phase) * 0.03;
    h.head.rotation.x = Math.sin(t * 2 + h.phase) * 0.05;
    if (h.timer <= 0) chooseNext(h);
  }

  else if (h.state === 'walk') {
    const dx = h.target.x - pos.x, dz = h.target.z - pos.z;
    const dist = Math.hypot(dx, dz);
    const desired = Math.atan2(dx, dz);
    const diff = wrapAngle(desired - h.heading);
    h.heading += THREE.MathUtils.clamp(diff, -2.5 * dt, 2.5 * dt);

    if (Math.abs(diff) < 0.4 && dist > 0.25) {
      const speed = 1.3;
      pos.x += Math.sin(h.heading) * speed * dt;
      pos.z += Math.cos(h.heading) * speed * dt;
      // waddle bob
      pos.y = TRAY_TOP + Math.abs(Math.sin(t * 9 + h.phase)) * 0.05;
      h.bodyGroup.rotation.z = Math.sin(t * 9 + h.phase) * 0.06;
      legSpeed = 10; legAmp = 0.55;
    }
    // keep inside tray
    if (Math.hypot(pos.x, pos.z) > 4.7) { pos.setLength(4.7); pos.y = TRAY_TOP; pickTarget(h); }
    if (dist < 0.3 || h.timer <= 0) chooseNext(h);
  }

  else if (h.state === 'wheel') {
    const dx = wheelPoint.x - pos.x, dz = wheelPoint.z - pos.z;
    const dist = Math.hypot(dx, dz);
    if (dist > 0.35) {                       // run to the wheel
      const desired = Math.atan2(dx, dz);
      h.heading += THREE.MathUtils.clamp(wrapAngle(desired - h.heading), -3 * dt, 3 * dt);
      pos.x += Math.sin(h.heading) * 1.4 * dt;
      pos.z += Math.cos(h.heading) * 1.4 * dt;
      legSpeed = 11; legAmp = 0.55;
    } else {                                 // running inside!
      h.heading = wheelHeading + Math.PI;    // face forward along the wheel
      pos.y = TRAY_TOP + Math.abs(Math.sin(t * 12)) * 0.04;
      h.wheelSpinSpeed = THREE.MathUtils.lerp(h.wheelSpinSpeed, 7, dt * 2);
      wheelSpin.rotation.x += h.wheelSpinSpeed * dt;   // wheel turns!
      legSpeed = 13; legAmp = 0.7;
    }
    if (h.timer <= 0) { h.wheelSpinSpeed = 0; chooseNext(h); }
  }

  else if (h.state === 'eat') {
    const dx = h.target.x - pos.x, dz = h.target.z - pos.z;
    const dist = Math.hypot(dx, dz);
    if (dist > 0.2) {
      const desired = Math.atan2(dx, dz);
      h.heading += THREE.MathUtils.clamp(wrapAngle(desired - h.heading), -3 * dt, 3 * dt);
      pos.x += Math.sin(h.heading) * 1.3 * dt;
      pos.z += Math.cos(h.heading) * 1.3 * dt;
      legSpeed = 10; legAmp = 0.5;
    } else {                                 // munching at the bowl
      h.heading = Math.atan2(h.target.x - bowlPos.x, h.target.z - bowlPos.z) + Math.PI;
      h.head.rotation.x = 0.35 + Math.sin(t * 9 + h.phase) * 0.22;   // pecking head
      h.head.position.z = 0.4 + Math.sin(t * 9 + h.phase) * 0.04;
      food.children.forEach((f, i) => f.rotation.y = t * 3 + i);     // wiggling snacks
    }
    if (h.timer <= 0) { h.head.rotation.x = 0; h.head.position.z = 0.4; chooseNext(h); }
  }

  // apply facing direction
  h.group.rotation.y = h.heading;

  // swing legs
  h.legs.forEach((leg, i) => {
    const phaseOff = (i % 2 === 0 ? 0 : Math.PI) + (i < 2 ? 0 : Math.PI * 0.3);
    leg.rotation.x = legAmp > 0 ? Math.sin(t * legSpeed + h.phase + phaseOff) * legAmp : 0;
  });
}

/* ============ LOOP ============ */
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;
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

| Feature | Details |
|---|---|
| **Cage** | Circular tray with wood chips, 22 metal bars + top/bottom rings (open top so you can peek in) |
| **Hamsters** | 4 chubby flat-shaded hamsters in different colors — cheeks, ears, tiny black eyes, pink nose |
| **Wheel** | Real rotating wheel with rungs and translucent side plates; hamsters run to it and *actually spin it* |
| **Bowl** | Snack pile that wiggles while a hamster pecks at it |
| **Behavior** | State machine: `idle → walk → wheel / eat → idle…` with turn-then-walk steering, waddling bob, breathing animation, swinging legs, and one-hamster-per-station queuing |
| **Camera** | Orbit controls with damping, zoom limits, and floor clamp so you never go under the tray |

Everything is procedural (no external models), so it loads instantly and runs smoothly even on modest hardware.