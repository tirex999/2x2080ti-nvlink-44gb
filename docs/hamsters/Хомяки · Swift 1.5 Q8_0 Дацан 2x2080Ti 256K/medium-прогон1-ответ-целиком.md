# 🐹 Low-Poly Hamster Playground

A complete single-file project. Save as `index.html` and open in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; height: 100%;
    background: linear-gradient(#ffe9c4, #ffd6e0); font-family: 'Segoe UI', Arial, sans-serif; }
  #info {
    position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
    background: rgba(255,255,255,0.75); border-radius: 14px; padding: 8px 18px;
    color: #7a4a2b; font-weight: 700; font-size: 15px; text-align: center;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12); pointer-events: none; user-select: none;
  }
  #info small { display:block; font-weight:400; font-size:11px; color:#a9755a; }
</style>
</head>
<body>
<div id="info">🐹 Low-Poly Hamster Playground <small>drag to rotate &nbsp;•&nbsp; scroll to zoom</small></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ---------------------------------------------------------------
//  SETUP
// ---------------------------------------------------------------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe4c2);
scene.fog = new THREE.Fog(0xffe4c2, 40, 90);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 200);
camera.position.set(14, 12, 16);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 2, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 8;
controls.maxDistance = 45;
controls.maxPolarAngle = Math.PI * 0.49;

// Lights
scene.add(new THREE.HemisphereLight(0xfff2dd, 0xc9a27e, 0.75));
const sun = new THREE.DirectionalLight(0xfff0d0, 0.9);
sun.position.set(12, 20, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -14; sun.shadow.camera.right = 14;
sun.shadow.camera.top = 14;  sun.shadow.camera.bottom = -14;
scene.add(sun);

// ---------------------------------------------------------------
//  CAGE  (tray, sand, bars, ring)
// ---------------------------------------------------------------
const CAGE_R = 9;

const tray = new THREE.Mesh(
  new THREE.CylinderGeometry(CAGE_R + 0.7, CAGE_R + 0.9, 0.9, 24),
  new THREE.MeshStandardMaterial({ color: 0x6fb7d6, flatShading: true })
);
tray.position.y = -0.45;
tray.receiveShadow = true; tray.castShadow = true;
scene.add(tray);

const sand = new THREE.Mesh(
  new THREE.CylinderGeometry(CAGE_R + 0.15, CAGE_R + 0.15, 0.35, 24),
  new THREE.MeshStandardMaterial({ color: 0xf2dfae, flatShading: true })
);
sand.position.y = 0.12;
sand.receiveShadow = true;
scene.add(sand);

const barMat = new THREE.MeshStandardMaterial({ color: 0xf7f3ec, flatShading: true });
for (let i = 0; i < 26; i++) {
  const a = (i / 26) * Math.PI * 2;
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 6, 5), barMat);
  bar.position.set(Math.cos(a) * CAGE_R, 3, Math.sin(a) * CAGE_R);
  bar.castShadow = true;
  scene.add(bar);
}
const ring = new THREE.Mesh(new THREE.TorusGeometry(CAGE_R, 0.14, 6, 30), barMat);
ring.rotation.x = Math.PI / 2;
ring.position.y = 6;
ring.castShadow = true;
scene.add(ring);

// Little decorations: wooden blocks + pebbles
const woodMat = new THREE.MeshStandardMaterial({ color: 0xc98a4b, flatShading: true });
for (let i = 0; i < 5; i++) {
  const b = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.45, 0.7), woodMat);
  const a = i * 1.9 + 0.6;
  b.position.set(Math.cos(a) * 6.8, 0.35, Math.sin(a) * 6.8);
  b.rotation.y = Math.random() * Math.PI;
  b.castShadow = true; b.receiveShadow = true;
  scene.add(b);
}
const pebMat = new THREE.MeshStandardMaterial({ color: 0xb9b3a8, flatShading: true });
for (let i = 0; i < 10; i++) {
  const p = new THREE.Mesh(new THREE.DodecahedronGeometry(0.18 + Math.random() * 0.12, 0), pebMat);
  const a = Math.random() * Math.PI * 2, r = 3 + Math.random() * 5;
  p.position.set(Math.cos(a) * r, 0.28, Math.sin(a) * r);
  p.castShadow = true;
  scene.add(p);
}

// ---------------------------------------------------------------
//  EXERCISE WHEEL (the interactive object)
// ---------------------------------------------------------------
const wheelGroup = new THREE.Group();
wheelGroup.position.set(-5.2, 2.4, 0);
scene.add(wheelGroup);

const wheelMat = new THREE.MeshStandardMaterial({ color: 0xff8fa3, flatShading: true });
const wheelSpin = new THREE.Group();
wheelGroup.add(wheelSpin);

const rim = new THREE.Mesh(new THREE.TorusGeometry(2.1, 0.28, 6, 18), wheelMat);
rim.castShadow = true;
wheelSpin.add(rim);
const tread = new THREE.Mesh(new THREE.CylinderGeometry(2.1, 2.1, 0.9, 18, 1, true),
  new THREE.MeshStandardMaterial({ color: 0xffc7d3, flatShading: true, side: THREE.DoubleSide }));
tread.rotation.y = Math.PI / 2;   // cylinder axis -> Z (wheel rolls in XY plane)
wheelSpin.add(tread);
for (let i = 0; i < 6; i++) {
  const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.12, 4.0, 0.12), wheelMat);
  spoke.rotation.z = (i / 6) * Math.PI;
  wheelSpin.add(spoke);
}
const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 1.3, 8),
  new THREE.MeshStandardMaterial({ color: 0xffb34d, flatShading: true }));
hub.rotation.x = Math.PI / 2;
wheelSpin.add(hub);

// Stand (A-frame)
const standMat = new THREE.MeshStandardMaterial({ color: 0x8ed081, flatShading: true });
[-0.75, 0.75].forEach(z => {
  const leg = new THREE.Mesh(new THREE.BoxGeometry(0.3, 2.6, 0.3), standMat);
  leg.position.set(0.55, -1.15, z);
  leg.rotation.z = -0.42;
  leg.castShadow = true;
  wheelGroup.add(leg);
});

// ---------------------------------------------------------------
//  FOOD BOWL
// ---------------------------------------------------------------
const BOWL = new THREE.Vector3(4.6, 0, -3.2);
const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.95, 0.65, 0.55, 10),
  new THREE.MeshStandardMaterial({ color: 0x7ec8e3, flatShading: true }));
bowl.position.set(BOWL.x, 0.42, BOWL.z);
bowl.castShadow = true; bowl.receiveShadow = true;
scene.add(bowl);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xd9a441, flatShading: true });
for (let i = 0; i < 7; i++) {
  const f = new THREE.Mesh(new THREE.DodecahedronGeometry(0.16, 0), foodMat);
  const a = Math.random() * Math.PI * 2, r = Math.random() * 0.5;
  f.position.set(BOWL.x + Math.cos(a) * r, 0.72, BOWL.z + Math.sin(a) * r);
  f.castShadow = true;
  scene.add(f);
}

// ---------------------------------------------------------------
//  LOW-POLY HAMSTER BUILDER
// ---------------------------------------------------------------
function makeHamster(color) {
  const g = new THREE.Group();
  const mat  = new THREE.MeshStandardMaterial({ color, flatShading: true });
  const mat2 = new THREE.MeshStandardMaterial({
    color: new THREE.Color(color).lerp(new THREE.Color(0xffffff), 0.55), flatShading: true });

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 7, 5), mat);
  body.scale.set(1.35, 1.0, 1.05);
  body.position.y = 0.55;
  body.castShadow = true;
  g.add(body);

  const head = new THREE.Group();
  head.position.set(0.72, 0.72, 0);
  g.add(head);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.38, 7, 5), mat);
  skull.castShadow = true;
  head.add(skull);
  // chubby cheeks
  [-1, 1].forEach(s => {
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.17, 6, 4), mat2);
    cheek.position.set(0.18, -0.05, 0.24 * s);
    head.add(cheek);
  });
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.09, 5, 4),
    new THREE.MeshStandardMaterial({ color: 0xff9aa8, flatShading: true }));
  nose.position.set(0.38, -0.02, 0);
  head.add(nose);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x222222 });
  [-1, 1].forEach(s => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.055, 5, 4), eyeMat);
    eye.position.set(0.28, 0.12, 0.19 * s);
    head.add(eye);
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.13, 6, 4), mat);
    ear.scale.y = 0.7;
    ear.position.set(-0.05, 0.36, 0.22 * s);
    head.add(ear);
  });

  // legs (pivot at hip so they can swing)
  const legs = [];
  [[0.42, 0.24], [0.42, -0.24], [-0.42, 0.24], [-0.42, -0.24]].forEach(([lx, lz]) => {
    const hip = new THREE.Group();
    hip.position.set(lx, 0.34, lz);
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.11, 0.3, 5), mat2);
    leg.position.y = -0.13;
    leg.castShadow = true;
    hip.add(leg);
    g.add(hip);
    legs.push(hip);
  });

  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.09, 5, 4), mat2);
  tail.position.set(-0.78, 0.55, 0);
  g.add(tail);

  scene.add(g);
  return { group: g, head, legs, body };
}

// ---------------------------------------------------------------
//  HAMSTER BRAIN  (walk / pause / eat / run-on-wheel)
// ---------------------------------------------------------------
let wheelSpinSpeed = 0;
let runner = null;

class Hamster {
  constructor(color, x, z, name) {
    const parts = makeHamster(color);
    this.group = parts.group; this.head = parts.head; this.legs = parts.legs;
    this.name = name;
    this.group.position.set(x, 0, z);
    this.state = 'idle';
    this.timer = Math.random() * 2;
    this.walkTime = 0;
    this.target = new THREE.Vector3();
    this.legPhase = 0;
    this.spinGoal = Math.random() * Math.PI * 2;
  }

  pickState() {
    const r = Math.random();
    if (r < 0.42) this.setState('walk');
    else if (r < 0.66) this.setState('idle');
    else if (r < 0.84) this.setState('eat');
    else this.setState('goWheel');
  }

  setState(s) {
    this.state = s;
    if (s === 'walk') {
      const a = Math.random() * Math.PI * 2, r = 2 + Math.random() * 5.5;
      this.target.set(Math.cos(a) * r, 0, Math.sin(a) * r);
      this.walkTime = 0;
    } else if (s === 'idle') {
      this.timer = 1 + Math.random() * 2.5;
      this.spinGoal = this.group.rotation.y + (Math.random() - 0.5) * 2.5;
    } else if (s === 'eat') {
      const a = Math.atan2(this.group.position.z - BOWL.z, this.group.position.x - BOWL.x);
      this.target.set(BOWL.x + Math.cos(a) * 1.35, 0, BOWL.z + Math.sin(a) * 1.35);
      this.walkTime = 0;
    } else if (s === 'goWheel') {
      this.target.set(wheelGroup.position.x + 1.6, 0, wheelGroup.position.z);
      this.walkTime = 0;
    } else if (s === 'run') {
      this.timer = 4 + Math.random() * 4;
      runner = this;
    } else if (s === 'munch') {
      this.timer = 2.5 + Math.random() * 2;
    }
  }

  turnToward(dx, dz, dt) {
    const goal = Math.atan2(-dz, dx);
    let d = goal - this.group.rotation.y;
    while (d >  Math.PI) d -= Math.PI * 2;
    while (d < -Math.PI) d += Math.PI * 2;
    this.group.rotation.y += THREE.MathUtils.clamp(d, -3 * dt, 3 * dt);
  }

  move(dt, speed) {
    const dx = this.target.x - this.group.position.x;
    const dz = this.target.z - this.group.position.z;
    const dist = Math.hypot(dx, dz);
    if (dist < 0.25) return true;
    this.turnToward(dx, dz, dt);
    this.group.position.x += Math.cos(this.group.rotation.y) * speed * dt;
    this.group.position.z -= Math.sin(this.group.rotation.y) * speed * dt;
    return false;
  }

  animateLegs(dt, amp, freq) {
    this.legPhase += dt * freq;
    this.legs[0].rotation.x =  Math.sin(this.legPhase) * amp;
    this.legs[1].rotation.x = -Math.sin(this.legPhase) * amp;
    this.legs[2].rotation.x = -Math.sin(this.legPhase) * amp;
    this.legs[3].rotation.x =  Math.sin(this.legPhase) * amp;
  }

  update(dt, t) {
    const p = this.group.position;
    // keep inside cage
    const distC = Math.hypot(p.x, p.z);
    if (distC > CAGE_R - 1.1 && this.state === 'walk') this.setState('idle');

    switch (this.state) {
      case 'idle': {
        let d = this.spinGoal - this.group.rotation.y;
        while (d >  Math.PI) d -= Math.PI * 2;
        while (d < -Math.PI) d += Math.PI * 2;
        this.group.rotation.y += d * dt * 2;
        this.head.rotation.x = Math.sin(t * 2.5) * 0.12;   // looking around
        this.animateLegs(dt, 0, 0);
        this.timer -= dt;
        if (this.timer <= 0) this.pickState();
        break;
      }
      case 'walk': {
        this.walkTime += dt;
        const done = this.move(dt, 1.7);
        this.animateLegs(dt, 0.65, 11);
        this.group.position.y = Math.abs(Math.sin(this.legPhase)) * 0.06;  // hoppy waddle
        if (done || this.walkTime > 9) { this.group.position.y = 0; this.pickState(); }
        break;
      }
      case 'eat': {
        this.walkTime += dt;
        if (this.move(dt, 1.5) || this.walkTime > 10) { this.setState('munch'); this.head.rotation.x = 0; }
        this.animateLegs(dt, 0.65, 11);
        break;
      }
      case 'munch': {
        // face the bowl and peck at food
        this.turnToward(BOWL.x - p.x, BOWL.z - p.z, dt);
        this.head.rotation.x = 0.5 + Math.sin(t * 14) * 0.35;   // pecking!
        this.timer -= dt;
        if (this.timer <= 0) { this.head.rotation.x = 0; this.pickState(); }
        break;
      }
      case 'goWheel': {
        this.walkTime += dt;
        if (this.move(dt, 1.6) || this.walkTime > 12) this.setState('run');
        this.animateLegs(dt, 0.65, 11);
        break;
      }
      case 'run': {
        // stand inside the wheel, sprint!
        p.set(wheelGroup.position.x, wheelGroup.position.y - 2.1 + 0.02, wheelGroup.position.z);
        this.group.rotation.y = -Math.PI / 2;    // face forward along the tread
        this.animateLegs(dt, 0.9, 24);
        this.head.rotation.x = -0.15;
        wheelSpinSpeed = 11;
        this.timer -= dt;
        if (this.timer <= 0) {
          this.head.rotation.x = 0;
          runner = null;
          p.set(wheelGroup.position.x + 2.2, 0, wheelGroup.position.z);
          this.pickState();
        }
        break;
      }
    }
    if (this.state !== 'walk') this.group.position.y *= 0.85;
  }
}

const hamsters = [
  new Hamster(0xf5b942,  3,  3, 'Nugget'),
  new Hamster(0xd98555, -2,  5, 'Biscuit'),
  new Hamster(0xf7e6c4,  1, -5, 'Snowball'),
  new Hamster(0xb98356,  6, -1, 'Peanut'),
  new Hamster(0xe8a2b8, -4, -4, 'Berry'),
];

// ---------------------------------------------------------------
//  MAIN LOOP
// ---------------------------------------------------------------
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  for (const h of hamsters) h.update(dt, t);

  // wheel physics: spins while a hamster runs, friction slows it down
  if (!runner) wheelSpinSpeed *= Math.pow(0.2, dt);
  wheelSpin.rotation.z -= wheelSpinSpeed * dt;

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

| Requirement | Implementation |
|---|---|
| **Cage** | 26 bars + top ring on a blue tray with sand floor |
| **Hamsters** | 5 flat-shaded low-poly hamsters (chubby cheeks, tiny ears, pink nose, stubby legs) in cute color variants |
| **Interactive object** | A pink exercise wheel — hamsters walk to it, climb in, sprint (legs blur!), and the wheel physically spins with friction after they leave |
| **Autonomous behavior** | State machine per hamster: `walk → idle → eat → run`, with smooth turning, waddling leg animation, body bounce, head-bobbing, and bowl-pecking |
| **Camera** | OrbitControls with damping, zoom limits, and floor clamp |
| **Stability** | Clamped `dt`, cage-boundary checks, single CDN dependency (Three.js r128), no assets to load |

Just open the file — hamsters start wandering immediately. 🐹