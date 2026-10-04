# 🐹 Low-Poly Hamster Playground

A complete single-file project. Save as `index.html` and open in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐹 Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #bfe3ff; font-family: 'Segoe UI', 'Comic Sans MS', sans-serif; }
  canvas { display: block; }
  #ui {
    position: fixed; top: 14px; left: 14px; z-index: 10;
    background: rgba(255,255,255,0.82); border-radius: 16px;
    padding: 12px 18px; box-shadow: 0 4px 18px rgba(0,0,0,0.15);
    color: #5a4632; pointer-events: none;
  }
  #ui h1 { margin: 0 0 4px; font-size: 20px; }
  #ui p { margin: 2px 0; font-size: 13px; }
  #stats { color: #b5651d; font-weight: bold; }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate · Scroll to zoom</p>
  <p id="stats">Snacks eaten: 0 · Wheel runs: 0</p>
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
scene.background = new THREE.Color(0xbfe3ff);
scene.fog = new THREE.Fog(0xbfe3ff, 30, 60);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(10, 8, 12);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.6, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 6;
controls.maxDistance = 28;
controls.maxPolarAngle = Math.PI * 0.49;

/* ============ LIGHTS ============ */
scene.add(new THREE.HemisphereLight(0xfff4e0, 0x8a7a5f, 0.85));
const sun = new THREE.DirectionalLight(0xfff0d0, 1.4);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -10; sun.shadow.camera.right = 10;
sun.shadow.camera.top = 10; sun.shadow.camera.bottom = -10;
scene.add(sun);

/* ============ HELPERS ============ */
const mat = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9, ...extra });
function addShadow(mesh) { mesh.castShadow = true; mesh.receiveShadow = true; return mesh; }

/* ============ GROUND ============ */
const ground = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(24, 24, 0.5, 24), mat(0x9fd98a)));
ground.position.y = -0.65;
scene.add(ground);

/* ============ CAGE TRAY ============ */
const cage = new THREE.Group();
scene.add(cage);

const tray = addShadow(new THREE.Mesh(new THREE.BoxGeometry(11, 1.0, 11), mat(0x63c7d2)));
tray.position.y = -0.25;
cage.add(tray);

// Tray rim
[[0, 5.2], [0, -5.2], [5.2, 0], [-5.2, 0]].forEach(([x, z], i) => {
  const rim = addShadow(new THREE.Mesh(
    new THREE.BoxGeometry(i < 2 ? 11.4 : 0.5, 0.5, i < 2 ? 0.5 : 11.4), mat(0x4fb3bf)));
  rim.position.set(x, 0.35, z);
  cage.add(rim);
});

// Bedding floor inside tray
const bedding = addShadow(new THREE.Mesh(new THREE.BoxGeometry(10.4, 0.15, 10.4), mat(0xe8c98f)));
bedding.position.y = 0.20;
cage.add(bedding);

// Scattered wood chips for flavor
for (let i = 0; i < 30; i++) {
  const chip = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.06, 0.12), mat(0xd9b877));
  chip.position.set((Math.random() - 0.5) * 9.5, 0.30, (Math.random() - 0.5) * 9.5);
  chip.rotation.y = Math.random() * Math.PI;
  cage.add(chip);
}

/* ============ CAGE BARS ============ */
const barMat = mat(0xfdfdfd, { roughness: 0.4, metalness: 0.3 });
const barGeo = new THREE.CylinderGeometry(0.06, 0.06, 5.2, 5);
for (let i = -6; i <= 6; i++) {
  const x = i * 0.82;
  [[x, 5.1], [x, -5.1], [5.1, x], [-5.1, x]].forEach(([bx, bz]) => {
    const bar = new THREE.Mesh(barGeo, barMat);
    bar.position.set(bx, 3.0, bz);
    bar.castShadow = true;
    cage.add(bar);
  });
}
// Top rails + lid crossbars
[[0, 5.1], [0, -5.1], [5.1, 0], [-5.1, 0]].forEach(([x, z], i) => {
  const rail = new THREE.Mesh(
    new THREE.CylinderGeometry(0.09, 0.09, 10.6, 6), barMat);
  rail.rotation.z = Math.PI / 2;
  if (i >= 2) rail.rotation.y = Math.PI / 2;
  rail.position.set(x, 5.6, z);
  cage.add(rail);
});
for (let i = -4; i <= 4; i++) {
  const lid = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 10.2, 5), barMat);
  lid.rotation.x = Math.PI / 2;
  lid.position.set(i * 1.2, 5.62, 0);
  cage.add(lid);
}
// Cute handle on top
const handle = new THREE.Mesh(new THREE.TorusGeometry(0.7, 0.09, 5, 10, Math.PI), barMat);
handle.position.set(0, 5.7, 0);
cage.add(handle);

/* ============ EXERCISE WHEEL (interactive) ============ */
const wheelGroup = new THREE.Group();
wheelGroup.position.set(3.3, 1.25, -2.6);
wheelGroup.rotation.y = Math.PI / 2;   // axis along X → hamster enters from +X
cage.add(wheelGroup);

const wheelSpin = new THREE.Group();
wheelGroup.add(wheelSpin);

const wheelColor = 0xff7b9c;
const rim = addShadow(new THREE.Mesh(new THREE.TorusGeometry(1.05, 0.13, 5, 14), mat(wheelColor)));
wheelSpin.add(rim);
const innerRim = new THREE.Mesh(new THREE.TorusGeometry(0.72, 0.06, 5, 14), mat(0xffa5be));
wheelSpin.add(innerRim);
for (let i = 0; i < 6; i++) {   // spokes = rungs
  const spoke = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.07, 0.09), mat(0xffd1dc));
  spoke.rotation.z = (i / 6) * Math.PI;
  wheelSpin.add(spoke);
}
const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.5, 6), mat(0x8a5a3b));
hub.rotation.x = Math.PI / 2;
wheelGroup.add(hub);
// Stand legs
[-0.35, 0.35].forEach(z => {
  const leg = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.16, 1.4, 0.16), mat(0x8a5a3b)));
  leg.position.set(0, -0.6, z);
  wheelGroup.add(leg);
});

let wheelSpeed = 0;
let wheelBusy = false;
let wheelRuns = 0;

/* ============ FOOD BOWL (interactive) ============ */
const bowlGroup = new THREE.Group();
bowlGroup.position.set(-3.0, 0.28, 2.8);
cage.add(bowlGroup);
const bowl = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.45, 0.42, 8), mat(0xffb14f)));
bowlGroup.add(bowl);
const bowlInner = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.62, 0.1, 8), mat(0xd98f2e));
bowlInner.position.y = 0.18;
bowlGroup.add(bowlInner);
const pellets = [];
for (let i = 0; i < 7; i++) {
  const p = new THREE.Mesh(new THREE.DodecahedronGeometry(0.11, 0), mat(0xb5651d));
  const a = (i / 7) * Math.PI * 2;
  p.position.set(Math.cos(a) * 0.28, 0.28, Math.sin(a) * 0.28);
  bowlGroup.add(p);
  pellets.push(p);
}
let snacksEaten = 0;

/* ============ TUNNEL (decor) ============ */
const tunnel = addShadow(new THREE.Mesh(
  new THREE.CylinderGeometry(0.75, 0.75, 2.6, 9, 1, true), mat(0xa06cd5, { side: THREE.DoubleSide })));
tunnel.rotation.x = Math.PI / 2;
tunnel.position.set(-2.6, 1.0, -2.8);
cage.add(tunnel);
const tunnelCap = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.75, 0.15, 9), mat(0x8a54b8)));
tunnelCap.rotation.x = Math.PI / 2;
tunnelCap.position.set(-2.6, 1.0, -4.1);
cage.add(tunnelCap);

/* ============ HAMSTER BUILDER ============ */
function buildHamster(color, cheekColor) {
  const g = new THREE.Group();
  const bodyMat = mat(color);
  const bellyMat = mat(0xfff2e0);
  const cheekMat = mat(cheekColor);

  const body = addShadow(new THREE.Mesh(new THREE.SphereGeometry(0.5, 7, 5), bodyMat));
  body.scale.set(1.15, 0.92, 0.95);
  body.position.y = 0.48;
  g.add(body);

  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.38, 6, 4), bellyMat);
  belly.scale.set(1.0, 0.8, 0.75);
  belly.position.set(0.12, 0.36, 0);
  g.add(belly);

  const head = addShadow(new THREE.Mesh(new THREE.SphereGeometry(0.32, 7, 5), bodyMat));
  head.position.set(0.55, 0.72, 0);
  g.add(head);

  // Cheeks (the important part)
  [1, -1].forEach(s => {
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.14, 6, 4), cheekMat);
    cheek.position.set(0.62, 0.62, s * 0.22);
    g.add(cheek);
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.12, 5, 4), mat(0xf0a5a5));
    ear.scale.set(1, 1, 0.4);
    ear.position.set(0.45, 1.0, s * 0.2);
    g.add(ear);
  });

  [1, -1].forEach(s => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 5, 5), mat(0x1a1a1a, { roughness: 0.2 }));
    eye.position.set(0.80, 0.78, s * 0.13);
    g.add(eye);
  });

  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 5, 4), mat(0xff8fa3));
  nose.position.set(0.87, 0.70, 0);
  g.add(nose);

  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.09, 5, 4), bodyMat);
  tail.position.set(-0.60, 0.45, 0);
  g.add(tail);

  // Stubby legs
  const legs = [];
  [[0.3, 0.28], [0.3, -0.28], [-0.3, 0.28], [-0.3, -0.28]].forEach(([x, z]) => {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.22, 0.14), bodyMat);
    leg.position.set(x, 0.14, z);
    leg.castShadow = true;
    g.add(leg);
    legs.push(leg);
  });

  return { group: g, body, head, legs };
}

/* ============ HAMSTER BRAIN ============ */
class Hamster {
  constructor(color, cheek, x, z) {
    const parts = buildHamster(color, cheek);
    this.parts = parts;
    this.mesh = parts.group;
    this.mesh.position.set(x, 0.28, z);
    this.mesh.rotation.y = Math.random() * Math.PI * 2;
    scene.add(this.mesh);

    this.speed = 1.1 + Math.random() * 0.5;
    this.state = 'idle';
    this.timer = Math.random() * 2;
    this.target = new THREE.Vector3();
    this.animT = 0;
    this.onWheel = false;
  }

  pickAction() {
    const roll = Math.random();
    if (roll < 0.45) {           // wander
      this.state = 'walk';
      this.target.set((Math.random() - 0.5) * 7.5, 0, (Math.random() - 0.5) * 7.5);
      this.timer = 6;
    } else if (roll < 0.72) {    // go eat
      this.state = 'walk';
      this.target.set(-3.0 + 1.1, 0, 2.8 + (Math.random() - 0.5));
      this.next = 'eat';
      this.timer = 8;
    } else {                     // go run on wheel
      this.state = 'walk';
      this.target.set(3.3 + 1.3, 0, -2.6);
      this.next = 'wheel';
      this.timer = 9;
    }
  }

  arrive() {
    if (this.next === 'eat' && pellets.length > 0) {
      this.state = 'eat'; this.timer = 2.5;
    } else if (this.next === 'wheel' && !wheelBusy) {
      wheelBusy = true; this.onWheel = true;
      this.state = 'wheel'; this.timer = 4 + Math.random() * 3;
      wheelRuns++;
    } else {
      this.state = 'idle'; this.timer = 0.5 + Math.random() * 1.5;
    }
    this.next = null;
  }

  update(dt) {
    const m = this.mesh;
    this.animT += dt;
    this.timer -= dt;

    const legSwing = (amp) => {
      this.parts.legs.forEach((leg, i) => {
        leg.rotation.x = Math.sin(this.animT * 12 + (i % 2 ? Math.PI : 0)) * amp;
      });
    };

    if (this.state === 'idle') {
      legSwing(0);
      // Cute sniffing bob
      this.parts.head.position.y = 0.72 + Math.sin(this.animT * 6) * 0.03;
      if (this.timer <= 0) this.pickAction();

    } else if (this.state === 'walk') {
      const dx = this.target.x - m.position.x;
      const dz = this.target.z - m.position.z;
      const dist = Math.hypot(dx, dz);
      const desired = Math.atan2(-dz, dx);
      let diff = desired - m.rotation.y;
      while (diff > Math.PI) diff -= Math.PI * 2;
      while (diff < -Math.PI) diff += Math.PI * 2;
      m.rotation.y += diff * Math.min(1, dt * 6);

      if (Math.abs(diff) < 0.4 && dist > 0.15) {
        m.position.x += Math.cos(m.rotation.y) * this.speed * dt;
        m.position.z -= Math.sin(m.rotation.y) * this.speed * dt;
        m.position.y = 0.28 + Math.abs(Math.sin(this.animT * 11)) * 0.06; // waddle-hop!
        legSwing(0.7);
      }
      if (dist < 0.25 || this.timer <= 0) this.arrive();

    } else if (this.state === 'eat') {
      legSwing(0);
      // Peck at food, nom nom
      this.parts.head.position.y = 0.72 + Math.sin(this.animT * 10) * 0.12 - 0.06;
      this.parts.head.rotation.x = Math.sin(this.animT * 10) * 0.25;
      if (this.timer < 2 && pellets.length > 0 && Math.random() < dt * 3) {
        bowlGroup.remove(pellets.pop());   // chomp!
        snacksEaten++;
      }
      if (this.timer <= 0) {
        this.parts.head.position.y = 0.72;
        this.parts.head.rotation.x = 0;
        this.state = 'idle'; this.timer = 0.5 + Math.random() * 1.5;
      }

    } else if (this.state === 'wheel') {
      // Sit inside the wheel, sprint for dear life
      m.position.set(3.3, 1.05 + Math.abs(Math.sin(this.animT * 14)) * 0.05, -2.6);
      m.rotation.y = -Math.PI / 2;
      legSwing(1.2);
      wheelSpeed = THREE.MathUtils.lerp(wheelSpeed, 9, dt * 2);
      if (this.timer <= 0) {
        wheelBusy = false; this.onWheel = false;
        wheelSpeed = 0;
        m.position.y = 0.28;
        this.state = 'idle'; this.timer = 0.5 + Math.random() * 1.5;
      }
    }

    if (this.state !== 'wheel') {
      // Keep inside the cage
      m.position.x = THREE.MathUtils.clamp(m.position.x, -4.3, 4.3);
      m.position.z = THREE.MathUtils.clamp(m.position.z, -4.3, 4.3);
      if (!this.onWheel) m.position.y = THREE.MathUtils.lerp(m.position.y, 0.28, dt * 5);
    }
  }
}

/* ============ SPAWN THE SQUAD ============ */
const hamsters = [
  new Hamster(0xe8a95c, 0xf7c9a3, 1, 1),        // golden
  new Hamster(0xfaf3e8, 0xf5b8c4, -1.5, -0.5),  // cream
  new Hamster(0x9b8f84, 0xe8b8b8, 0.5, -2),     // grey "dwarf"
  new Hamster(0xc97a3d, 0xf0c090, -1, 2.5),     // cinnamon
];

/* ============ UI STATS ============ */
const statsEl = document.getElementById('stats');
function refreshStats() {
  statsEl.textContent = `Snacks eaten: ${snacksEaten} · Wheel runs: ${wheelRuns}`;
}
setInterval(refreshStats, 500);

/* ============ MAIN LOOP ============ */
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05); // clamp for tab-switch stability

  hamsters.forEach(h => h.update(dt));

  // Wheel physics: spin while sprinting, wobble to a stop after
  wheelSpin.rotation.z += wheelSpeed * dt;
  if (!wheelBusy) wheelSpeed = THREE.MathUtils.lerp(wheelSpeed, 0, dt * 1.5);

  // Pellets gently bob (they're on caffeine)
  pellets.forEach((p, i) => { p.position.y = 0.28 + Math.sin(clock.elapsedTime * 3 + i) * 0.02; });

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

**Scene** 🏠
- Pastel cage tray with rim, wooden bedding floor, scattered wood chips, bars all around, a lid with crossbars and a cute top handle
- Grass ground disc, soft fog, warm directional light with soft shadows

**Hamsters** 🐹 (4 of them: golden, cream, grey, cinnamon)
- Low-poly flat-shaded spheres with big cheeks, tiny ears, beady eyes, pink nose, stubby legs, and a nub tail
- **State machine**: `idle` (sniffing bob) → `walk` (waddle-hopping with leg swings) → `eat` (head-pecking at the bowl, eats pellets!) or `wheel` (sprints inside the exercise wheel)
- Cage-bounded so they never escape

**Interactive objects**
- **Exercise wheel** — spins fast while a hamster runs, wobbles to a stop when they leave; only one hamster claims it at a time
- **Food bowl** — hamsters walk over and *nom* pellets (they disappear, with a running "snacks eaten" counter)
- Decorative purple tunnel for extra charm

**Stability touches**: delta-time clamping (no teleporting after tab switches), angle wrapping for smooth turns, resize handling, capped pixel ratio. Just open it and enjoy the waddling. 🎉