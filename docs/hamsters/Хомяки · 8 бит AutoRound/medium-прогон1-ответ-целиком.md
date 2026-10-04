# Low-Poly Hamster Playground

Here's the complete single-file project. Save it as `index.html` and open it in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #ffe9d6; }
  #info {
    position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
    font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
    color: #7a4a2b; background: rgba(255,255,255,0.75);
    padding: 8px 18px; border-radius: 14px; font-size: 15px;
    pointer-events: none; text-align: center;
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
<div id="info">🐹 Low-Poly Hamster Playground — drag to rotate, scroll to zoom!</div>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============ SCENE / CAMERA / RENDERER ============ */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9d6);
scene.fog = new THREE.Fog(0xffe9d6, 25, 45);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
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
controls.minDistance = 5;
controls.maxDistance = 25;
controls.maxPolarAngle = Math.PI * 0.49;

/* ============ LIGHTS ============ */
scene.add(new THREE.AmbientLight(0xfff2e0, 0.9));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12;  sun.shadow.camera.bottom = -12;
scene.add(sun);

/* ============ HELPERS ============ */
function mat(color) { return new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.85 }); }
function mesh(geo, material, x=0, y=0, z=0, castShadow=true) {
  const m = new THREE.Mesh(geo, material);
  m.position.set(x, y, z);
  m.castShadow = castShadow;
  m.receiveShadow = true;
  return m;
}

/* ============ CAGE: TRAY + GLASS WALLS ============ */
const cage = new THREE.Group();
const CAGE_W = 10, CAGE_D = 8, CAGE_H = 4.5;

// wooden base frame
cage.add(mesh(new THREE.BoxGeometry(CAGE_W+0.8, 0.5, CAGE_D+0.8), mat(0x8b5a2b), 0, -0.25, 0));
// bedding floor
cage.add(mesh(new THREE.BoxGeometry(CAGE_W, 0.35, CAGE_D), mat(0xf5deb3), 0, 0.12, 0, false));
// little bedding "fluff" chunks
for (let i = 0; i < 26; i++) {
  const s = 0.15 + Math.random()*0.2;
  const chunk = mesh(new THREE.IcosahedronGeometry(s, 0),
    mat([0xfdf3e3, 0xfae6c8, 0xf3d9b0][i % 3]),
    (Math.random()-0.5)*(CAGE_W-1), 0.32, (Math.random()-0.5)*(CAGE_D-1), false);
  chunk.rotation.set(Math.random()*3, Math.random()*3, 0);
  cage.add(chunk);
}

// glass walls (front, back, left, right)
const glassMat = new THREE.MeshStandardMaterial({
  color: 0xbfe8ff, transparent: true, opacity: 0.18, roughness: 0.1, side: THREE.DoubleSide
});
const wallGeoH = new THREE.PlaneGeometry(CAGE_W, CAGE_H);
const wallGeoV = new THREE.PlaneGeometry(CAGE_D, CAGE_H);
[[0, CAGE_H/2+0.3, -CAGE_D/2, 0], [0, CAGE_H/2+0.3, CAGE_D/2, Math.PI]].forEach(([x,y,z,ry]) => {
  const w = new THREE.Mesh(wallGeoH, glassMat);
  w.position.set(x,y,z); w.rotation.y = ry; w.receiveShadow = true;
  cage.add(w);
});
[[-CAGE_W/2, CAGE_H/2+0.3, 0, Math.PI/2], [CAGE_W/2, CAGE_H/2+0.3, 0, -Math.PI/2]].forEach(([x,y,z,ry]) => {
  const w = new THREE.Mesh(wallGeoV, glassMat);
  w.position.set(x,y,z); w.rotation.y = ry; w.receiveShadow = true;
  cage.add(w);
});

// metal frame edges
const edgeMat = new THREE.MeshStandardMaterial({ color: 0x9aa5ad, roughness: 0.4, metalness: 0.6 });
const barV = new THREE.CylinderGeometry(0.07, 0.07, CAGE_H, 6);
[[-CAGE_W/2,-CAGE_D/2],[CAGE_W/2,-CAGE_D/2],[-CAGE_W/2,CAGE_D/2],[CAGE_W/2,CAGE_D/2]].forEach(([x,z]) => {
  cage.add(mesh(barV, edgeMat, x, CAGE_H/2+0.3, z));
});
const barH = new THREE.CylinderGeometry(0.07, 0.07, CAGE_W, 6);
const barH2 = new THREE.CylinderGeometry(0.07, 0.07, CAGE_D, 6);
[[-CAGE_D/2],[CAGE_D/2]].forEach(([z]) => {
  const b = mesh(barH, edgeMat, 0, CAGE_H+0.3, z); b.rotation.z = Math.PI/2; cage.add(b);
});
[[-CAGE_W/2],[CAGE_W/2]].forEach(([x]) => {
  const b = mesh(barH2, edgeMat, x, CAGE_H+0.3, 0); b.rotation.x = Math.PI/2; cage.add(b);
});
scene.add(cage);

/* ============ WHEEL (interactive object) ============ */
const wheelGroup = new THREE.Group();
wheelGroup.position.set(-3.2, 0, -2.2);
const rimMat = mat(0x5ec8e5);
const rim = mesh(new THREE.TorusGeometry(1.1, 0.14, 8, 18), rimMat);
rim.rotation.x = Math.PI/2; // stand upright facing Z... we want it facing X so hamster runs along Z? Face it toward +Z
rim.rotation.set(0, 0, 0);
rim.rotation.y = 0;
wheelGroup.add(rim);
// spokes
const spokeMat = mat(0xd9f3fb);
for (let i = 0; i < 5; i++) {
  const s = mesh(new THREE.CylinderGeometry(0.045, 0.045, 2.2, 6), spokeMat);
  s.rotation.z = (i / 5) * Math.PI;
  wheelGroup.add(s);
}
// hub
wheelGroup.add(mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.3, 8), mat(0xff8fab)));
wheelGroup.children.forEach(c => { if (c.geometry.type === 'CylinderGeometry' && c.material.color.getHex() !== 0xff8fab) c.rotation.order = 'ZYX'; });
// stand
const stand = mesh(new THREE.CylinderGeometry(0.1, 0.16, 1.15, 6), mat(0x8b5a2b), 0, 0.55, 0);
stand.rotation.x = 0;
wheelGroup.add(stand);
const basePlate = mesh(new THREE.BoxGeometry(1.0, 0.12, 1.0), mat(0x8b5a2b), 0, 0.06, 0);
wheelGroup.add(basePlate);
scene.add(wheelGroup);

const WHEEL_POS = wheelGroup.position.clone().add(new THREE.Vector3(0, 0, 0));
const WHEEL_FACING = new THREE.Vector3(0, 0, 1); // hamster faces +Z while running
let wheelSpin = 0;

/* ============ FOOD BOWL ============ */
const bowl = new THREE.Group();
bowl.position.set(3.4, 0, 2.4);
bowl.add(mesh(new THREE.CylinderGeometry(0.75, 0.5, 0.4, 8), mat(0xff6f61), 0, 0.2, 0));
bowl.add(mesh(new THREE.CylinderGeometry(0.62, 0.62, 0.1, 8), mat(0xc98a3d), 0, 0.38, 0, false));
// seed piles
for (let i = 0; i < 6; i++) {
  const seed = mesh(new THREE.SphereGeometry(0.09, 5, 4), mat(0x8a5a2b),
    (Math.random()-0.5)*0.7, 0.42, (Math.random()-0.5)*0.7, false);
  seed.scale.y = 0.7;
  bowl.add(seed);
}
scene.add(bowl);
const BOWL_POS = bowl.position.clone();

/* ============ TUNNEL ============ */
const tunnel = new THREE.Group();
tunnel.position.set(1.5, 0, -2.6);
tunnel.rotation.y = 0.5;
const tube = mesh(new THREE.CylinderGeometry(0.65, 0.65, 2.6, 8, 1, true), mat(0xa8e6a3), 0, 0.65, 0);
tube.rotation.z = Math.PI/2;
tube.material.side = THREE.DoubleSide;
tunnel.add(tube);
const endCap = mat(0x7cc97a);
const cap1 = mesh(new THREE.TorusGeometry(0.65, 0.09, 6, 8), endCap, -1.3, 0.65, 0);
cap1.rotation.y = Math.PI/2;
const cap2 = cap1.clone(); cap2.position.x = 1.3;
tunnel.add(cap1, cap2);
scene.add(tunnel);

/* ============ HAMSTER FACTORY ============ */
function makeHamster(colors) {
  const g = new THREE.Group();
  const bodyM = mat(colors.body), bellyM = mat(colors.belly), darkM = mat(colors.dark);

  // body
  const body = mesh(new THREE.SphereGeometry(0.42, 8, 6), bodyM, 0, 0.45, 0);
  body.scale.set(1, 0.9, 1.25);
  g.add(body);
  // head
  const head = mesh(new THREE.SphereGeometry(0.3, 8, 6), bodyM, 0, 0.55, 0.5);
  g.add(head);
  // muzzle
  const muzzle = mesh(new THREE.SphereGeometry(0.16, 6, 5), bellyM, 0, 0.45, 0.72);
  g.add(muzzle);
  // nose
  g.add(mesh(new THREE.SphereGeometry(0.05, 5, 4), mat(0xe07a9b), 0, 0.47, 0.86, false));
  // eyes
  [-1, 1].forEach(s => {
    const eye = mesh(new THREE.SphereGeometry(0.06, 5, 4), mat(0x2b2b2b), 0.14*s, 0.6, 0.72, false);
    g.add(eye);
  });
  // ears
  [-1, 1].forEach(s => {
    const ear = mesh(new THREE.ConeGeometry(0.12, 0.2, 5), bodyM, 0.16*s, 0.82, 0.42, false);
    ear.rotation.z = -0.3*s;
    g.add(ear);
    const inner = mesh(new THREE.ConeGeometry(0.06, 0.12, 5), mat(0xffb3c6), 0.16*s, 0.8, 0.46, false);
    inner.rotation.z = -0.3*s;
    g.add(inner);
  });
  // puffy cheeks
  [-1, 1].forEach(s => {
    const cheek = mesh(new THREE.SphereGeometry(0.14, 6, 5), bellyM, 0.2*s, 0.42, 0.62, false);
    g.add(cheek);
  });
  // feet
  const feet = [];
  [[-0.2, 0.28], [0.2, 0.28], [-0.2, -0.3], [0.2, -0.3]].forEach(([x, z]) => {
    const foot = mesh(new THREE.SphereGeometry(0.09, 5, 4), darkM, x, 0.1, z, false);
    foot.scale.y = 0.6;
    g.add(foot);
    feet.push(foot);
  });
  // tiny tail nub
  g.add(mesh(new THREE.SphereGeometry(0.08, 5, 4), darkM, 0, 0.45, -0.55, false));

  g.userData.feet = feet;
  return g;
}

const PALETTES = [
  { body: 0xf2a65a, belly: 0xfde8c8, dark: 0xc97b3a }, // orange
  { body: 0x9b7bd4, belly: 0xe6dcff, dark: 0x6f54a8 }, // purple
  { body: 0x7fd08a, belly: 0xe2f7d9, dark: 0x4f9e5c }, // green
];

/* ============ HAMSTER AI ============ */
const WALK_SPEED = 1.4, TURN_SPEED = 3.0;
const hamsters = [];

function randomPointInCage() {
  return new THREE.Vector3(
    (Math.random()-0.5) * (CAGE_W - 2),
    0,
    (Math.random()-0.5) * (CAGE_D - 2)
  );
}

class Hamster {
  constructor(palette, pos) {
    this.mesh = makeHamster(palette);
    this.mesh.position.copy(pos);
    this.mesh.rotation.y = Math.random() * Math.PI * 2;
    scene.add(this.mesh);

    this.state = 'wander';
    this.timer = 0;
    this.target = randomPointInCage();
    this.wheelPhase = Math.random() * Math.PI * 2;
    this.baseY = 0;
    this.wobble = Math.random() * 10;
  }

  pickNextAction() {
    const r = Math.random();
    if (r < 0.3)      { this.state = 'pause';  this.timer = 1 + Math.random()*2.5; }
    else if (r < 0.5) { this.state = 'wheel';  this.timer = 4 + Math.random()*3; }
    else if (r < 0.65){ this.state = 'eat';    this.timer = 3 + Math.random()*2; }
    else              { this.state = 'wander'; this.timer = 3 + Math.random()*3; this.target = randomPointInCage(); }
  }

  steerTo(point, dt) {
    const desired = Math.atan2(point.x - this.mesh.position.x, point.z - this.mesh.position.z);
    let diff = desired - this.mesh.rotation.y;
    diff = Math.atan2(Math.sin(diff), Math.cos(diff));
    const maxTurn = TURN_SPEED * dt;
    this.mesh.rotation.y += THREE.MathUtils.clamp(diff, -maxTurn, maxTurn);
    return Math.abs(diff) < 0.35;
  }

  update(dt, time) {
    this.timer -= dt;
    const p = this.mesh.position;

    switch (this.state) {
      case 'wander': {
        const arrived = this.steerTo(this.target, dt);
        if (arrived) p.add(new THREE.Vector3(Math.sin(this.mesh.rotation.y), 0, Math.cos(this.mesh.rotation.y)).multiplyScalar(WALK_SPEED * dt));
        this.waddle(dt, time, WALK_SPEED);
        if (this.timer <= 0 || p.distanceTo(this.target) < 0.3) this.pickNextAction();
        break;
      }
      case 'pause': {
        // idle: sniff the ground, twitch an ear
        this.mesh.rotation.y += Math.sin(time * 1.3 + this.wobble) * 0.15 * dt * 4;
        this.mesh.position.y = this.baseY + Math.sin(time * 2 + this.wobble) * 0.015;
        if (this.timer <= 0) this.pickNextAction();
        break;
      }
      case 'wheel': {
        const facing = this.steerTo(WHEEL_POS, dt);
        const dist = p.distanceTo(WHEEL_POS);
        if (facing && dist > 0.55) {
          p.add(new THREE.Vector3(Math.sin(this.mesh.rotation.y), 0, Math.cos(this.mesh.rotation.y)).multiplyScalar(WALK_SPEED * dt));
          this.waddle(dt, time, WALK_SPEED);
        } else {
          // running in the wheel!
          p.lerp(WHEEL_POS, 1 - Math.pow(0.001, dt));
          this.mesh.position.y = this.baseY + Math.abs(Math.sin(time * 14 + this.wheelPhase)) * 0.09;
          this.wheelSpin += dt * 5;
          if (this.timer <= 0) this.pickNextAction();
        }
        break;
      }
      case 'eat': {
        const facing = this.steerTo(BOWL_POS, dt);
        const dist = p.distanceTo(BOWL_POS);
        if (facing && dist > 1.1) {
          p.add(new THREE.Vector3(Math.sin(this.mesh.rotation.y), 0, Math.cos(this.mesh.rotation.y)).multiplyScalar(WALK_SPEED * dt));
          this.waddle(dt, time, WALK_SPEED);
        } else {
          p.lerp(BOWL_POS.clone().add(new THREE.Vector3(0, 0, 0)), 1 - Math.pow(0.001, dt));
          // chomp! cheeks puff & head dips
          this.mesh.position.y = this.baseY - 0.08 + Math.abs(Math.sin(time * 8 + this.wobble)) * 0.05;
          this.mesh.children.forEach(c => {}); // cheeks handled by scale below
          const cheeks = this.mesh.userData.cheeks;
          if (cheeks) cheeks.forEach(c => c.scale.setScalar(1 + 0.5*Math.abs(Math.sin(time*8 + this.wobble))));
          if (this.timer <= 0) this.pickNextAction();
        }
        break;
      }
    }

    // keep inside cage
    p.x = THREE.MathUtils.clamp(p.x, -CAGE_W/2 + 0.8, CAGE_W/2 - 0.8);
    p.z = THREE.MathUtils.clamp(p.z, -CAGE_D/2 + 0.8, CAGE_D/2 - 0.8);
  }

  waddle(dt, time, speed) {
    const phase = time * 10 + this.wobble;
    this.mesh.position.y = this.baseY + Math.abs(Math.sin(phase)) * 0.06;
    this.mesh.rotation.z = Math.sin(phase) * 0.06;
    // feet shuffle
    const f = this.mesh.userData.feet;
    f.forEach((foot, i) => { foot.position.y = 0.1 + Math.max(0, Math.sin(phase + i * Math.PI)) * 0.05; });
  }
}

// tag cheeks for the eating animation
PALETTES.forEach(() => {});
function tagCheeks() {
  hamsters.forEach(h => {
    const children = h.mesh.children;
    // cheeks are the two belly-colored spheres near front — find by position
    h.mesh.userData.cheeks = children.filter(c =>
      c.geometry.type === 'SphereGeometry' &&
      Math.abs(c.position.z - 0.62) < 0.01 &&
      Math.abs(c.position.y - 0.42) < 0.01
    );
  });
}

const startPositions = [
  new THREE.Vector3(-2, 0, 1.5),
  new THREE.Vector3(2.5, 0, -1),
  new THREE.Vector3(0, 0, 2.5),
];
startPositions.forEach((pos, i) => hamsters.push(new Hamster(PALETTES[i], pos)));
tagCheeks();

/* ============ ANIMATION LOOP ============ */
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  hamsters.forEach(h => h.update(dt, t));

  // wheel spins while a hamster is in it, then coasts
  const someoneRunning = hamsters.some(h => h.state === 'wheel' && h.mesh.position.distanceTo(WHEEL_POS) < 0.6);
  if (someoneRunning) wheelSpin += dt * 5;
  wheelSpin *= (1 - dt * 0.8); // coast to a stop
  wheelGroup.rotation.y = wheelSpin;

  // gentle bowl wobble when eaten at
  const eatingNear = hamsters.some(h => h.state === 'eat' && h.mesh.position.distanceTo(BOWL_POS) < 1.2);
  bowl.rotation.z = eatingNear ? Math.sin(t * 12) * 0.04 : 0;

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

| Feature | Details |
|---|---|
| **Cage** | Wooden base, sandy bedding with scattered fluff chunks, translucent glass walls, metal corner posts & top rails |
| **3 hamsters** | Orange, purple, and green — each built from ~15 low-poly primitives (puffy cheeks, cone ears, dark nose, stubby feet, tail nub) |
| **AI states** | `wander` → `pause` (sniffing/idle) → `wheel` (runs into the wheel, bounces, wheel spins & coasts) → `eat` (chomps at the bowl with puffing cheeks and a wobbling bowl) |
| **Interactive objects** | Spinning exercise wheel, food bowl with seeds, decorative tunnel |
| **Feel-good details** | Waddle bobbing, foot shuffling, side-to-side wobble while walking, soft shadows, fog, damped orbit camera clamped above the floor |

**Tuning tips:** change `WALK_SPEED`, the action probabilities in `pickNextAction()`, or add more entries to `PALETTES` / `startPositions` to add hamsters.