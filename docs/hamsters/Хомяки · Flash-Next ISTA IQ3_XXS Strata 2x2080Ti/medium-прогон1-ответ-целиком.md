# Low-Poly Hamster Playground

A complete single-file project. Save it as `index.html` and open it in any modern browser — no build step, no assets needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #ffe9d6; }
  canvas { display: block; }
  #ui {
    position: fixed; top: 16px; left: 16px; pointer-events: none;
    font-family: "Comic Sans MS", "Segoe UI", sans-serif; color: #6b4a2f;
    text-shadow: 0 1px 0 #fff;
  }
  #ui h1 { margin: 0; font-size: 22px; }
  #ui p  { margin: 4px 0 0; font-size: 13px; opacity: 0.8; }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate &nbsp;•&nbsp; Scroll to zoom</p>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
/* ============================================================
   SCENE SETUP
   ============================================================ */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9d6);
scene.fog = new THREE.Fog(0xffe9d6, 30, 60);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Lights
const hemi = new THREE.HemisphereLight(0xfff2e0, 0xb08968, 0.9);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff0dd, 0.8);
sun.position.set(10, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -10; sun.shadow.camera.right = 10;
sun.shadow.camera.top = 10;   sun.shadow.camera.bottom = -10;
scene.add(sun);

// Helper: cute flat-shaded material
function mat(color, opts = {}) {
  return new THREE.MeshStandardMaterial({
    color, flatShading: true, roughness: 0.9, ...opts
  });
}

/* ============================================================
   CAGE: TRAY, FLOOR, BARS
   ============================================================ */
const CAGE_R = 6;
const FLOOR_Y = 0.51;

// Tray
const tray = new THREE.Mesh(
  new THREE.CylinderGeometry(6.5, 6.3, 0.5, 20), mat(0xd9b382));
tray.position.y = 0.25;
tray.receiveShadow = true;
scene.add(tray);

// Sandy floor
const floor = new THREE.Mesh(
  new THREE.CircleGeometry(6.1, 20), mat(0xf0d9a8));
floor.rotation.x = -Math.PI / 2;
floor.position.y = FLOOR_Y + 0.005;
floor.receiveShadow = true;
scene.add(floor);

// Vertical bars + rings
const barMat = mat(0x5f7d8c);
for (let i = 0; i < 26; i++) {
  const a = (i / 26) * Math.PI * 2;
  const bar = new THREE.Mesh(
    new THREE.CylinderGeometry(0.06, 0.06, 3.5, 5), barMat);
  bar.position.set(Math.cos(a) * CAGE_R, 0.5 + 1.75, Math.sin(a) * CAGE_R);
  bar.castShadow = true;
  scene.add(bar);
}
const ringTop = new THREE.Mesh(new THREE.TorusGeometry(CAGE_R, 0.09, 5, 30), barMat);
ringTop.rotation.x = Math.PI / 2; ringTop.position.y = 4.0;
scene.add(ringTop);
const ringBot = new THREE.Mesh(new THREE.TorusGeometry(CAGE_R, 0.09, 5, 30), barMat);
ringBot.rotation.x = Math.PI / 2; ringBot.position.y = 0.55;
scene.add(ringBot);

// Wood chips scattered on the floor
const chipColors = [0x9c6b3c, 0xb8875a, 0x7fa66a, 0xc9a86a];
for (let i = 0; i < 22; i++) {
  const a = Math.random() * Math.PI * 2;
  const r = 1 + Math.random() * 4.8;
  const chip = new THREE.Mesh(
    new THREE.BoxGeometry(0.15, 0.06, 0.35),
    mat(chipColors[i % chipColors.length]));
  chip.position.set(Math.cos(a) * r, FLOOR_Y + 0.03, Math.sin(a) * r);
  chip.rotation.y = Math.random() * Math.PI;
  chip.rotation.z = (Math.random() - 0.5) * 0.4;
  chip.receiveShadow = true;
  scene.add(chip);
}

/* ============================================================
   INTERACTIVE OBJECT: RUNNING WHEEL
   ============================================================ */
const WHEEL_POS = new THREE.Vector3(4.2, 1.9, -1.5);
const wheelGroup = new THREE.Group();
const wheelSpin = new THREE.Group();   // this part rotates

const wheelRim = new THREE.Mesh(
  new THREE.TorusGeometry(1.3, 0.22, 6, 18), mat(0xf2789f));
wheelSpin.add(wheelRim);

for (let i = 0; i < 6; i++) {
  const spoke = new THREE.Mesh(
    new THREE.BoxGeometry(2.3, 0.1, 0.1), mat(0xffd166));
  spoke.rotation.z = (i / 6) * Math.PI;
  wheelSpin.add(spoke);
}
const hub = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 5), mat(0x4d6da8));
wheelSpin.add(hub);
wheelGroup.add(wheelSpin);

// Supports + axle
const supMat = mat(0x4d6da8);
[-1, 1].forEach(s => {
  const sup = new THREE.Mesh(new THREE.BoxGeometry(0.15, 1.5, 0.15), supMat);
  sup.position.set(WHEEL_POS.x, 1.25, WHEEL_POS.z + s * 1.0);
  sup.castShadow = true;
  scene.add(sup);
});
const axle = new THREE.Mesh(
  new THREE.CylinderGeometry(0.08, 0.08, 2.2, 6), supMat);
axle.rotation.x = Math.PI / 2;
axle.position.copy(WHEEL_POS);
scene.add(axle);

wheelGroup.position.copy(WHEEL_POS);
scene.add(wheelGroup);

/* ============================================================
   FOOD BOWL
   ============================================================ */
const BOWL_POS = new THREE.Vector3(-3.2, 0, 2.2);
const bowl = new THREE.Mesh(
  new THREE.CylinderGeometry(0.75, 0.5, 0.4, 9), mat(0x62b2a0));
bowl.position.set(BOWL_POS.x, FLOOR_Y + 0.2, BOWL_POS.z);
bowl.castShadow = true;
scene.add(bowl);
// Food pellets
for (let i = 0; i < 5; i++) {
  const pellet = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.14, 0), mat(0xd97b3f));
  pellet.position.set(
    BOWL_POS.x + (Math.random() - 0.5) * 0.6,
    FLOOR_Y + 0.42,
    BOWL_POS.z + (Math.random() - 0.5) * 0.6);
  scene.add(pellet);
}

/* ============================================================
   TUNNEL (decoration)
   ============================================================ */
const tunnel = new THREE.Mesh(
  new THREE.CylinderGeometry(0.65, 0.65, 2.0, 8, 1, true),
  mat(0xe8935c, { side: THREE.DoubleSide }));
tunnel.rotation.z = Math.PI / 2;
tunnel.position.set(-2.6, FLOOR_Y + 0.65, -2.8);
tunnel.castShadow = true;
scene.add(tunnel);

/* ============================================================
   HAMSTERS
   ============================================================ */
function createHamster(color) {
  const g = new THREE.Group();
  const bodyMat = mat(color);
  const earMat  = mat(0xf5b8c4);

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 7, 5), bodyMat);
  body.scale.set(1.05, 0.95, 1.25);
  body.position.y = 0.5;
  body.castShadow = true;
  g.add(body);

  const head = new THREE.Group();
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.36, 7, 5), bodyMat);
  skull.castShadow = true;
  head.add(skull);

  // Cheeks
  [-1, 1].forEach(s => {
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.16, 5, 4), bodyMat);
    cheek.position.set(s * 0.26, -0.05, 0.22);
    head.add(cheek);
  });
  // Ears
  [-1, 1].forEach(s => {
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.14, 5, 4), earMat);
    ear.position.set(s * 0.22, 0.28, -0.1);
    head.add(ear);
  });
  // Eyes + nose
  [-1, 1].forEach(s => {
    const eye = new THREE.Mesh(
      new THREE.SphereGeometry(0.055, 5, 4), mat(0x222222, { roughness: 0.3 }));
    eye.position.set(s * 0.15, 0.08, 0.31);
    head.add(eye);
  });
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.06, 5, 4), earMat);
  nose.position.set(0, -0.03, 0.35);
  head.add(nose);

  head.position.set(0, 0.78, 0.55);
  g.add(head);

  // Tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.1, 5, 4), bodyMat);
  tail.position.set(0, 0.45, -0.72);
  g.add(tail);

  // Legs
  const legs = [];
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([sx, sz]) => {
    const pivot = new THREE.Group();
    pivot.position.set(sx * 0.28, 0.24, sz * 0.3);
    const leg = new THREE.Mesh(
      new THREE.CylinderGeometry(0.08, 0.07, 0.24, 5), bodyMat);
    leg.position.y = -0.12;
    pivot.add(leg);
    g.add(pivot);
    legs.push(pivot);
  });

  g.userData = {
    isHamster: true,
    body, head, legs,
    state: 'idle',
    timer: 0.5 + Math.random() * 2,
    target: new THREE.Vector3(),
    heading: Math.random() * Math.PI * 2,
    speed: 0.9 + Math.random() * 0.5,
    walkPhase: Math.random() * 10,
    phaseOffset: Math.random() * 10
  };
  return g;
}

const hamsterColors = [0xf5d9a0, 0xb0703c, 0x9aa0a6, 0xffffff, 0xe8b04a];
const hamsters = [];
for (let i = 0; i < 5; i++) {
  const h = createHamster(hamsterColors[i]);
  const a = (i / 5) * Math.PI * 2 + 0.4;
  const r = 2 + Math.random() * 2;
  h.position.set(Math.cos(a) * r, FLOOR_Y, Math.sin(a) * r);
  h.rotation.y = -a;
  h.userData.heading = -a + Math.PI;
  scene.add(h);
  hamsters.push(h);
}

/* ============================================================
   HAMSTER BRAIN (simple state machine)
   ============================================================ */
function pickNextAction(h) {
  const u = h.userData;
  const r = Math.random();
  if (r < 0.18) {
    // Go run on the wheel
    u.state = 'toWheel';
    u.target.set(WHEEL_POS.x - 2.0, FLOOR_Y, WHEEL_POS.z + (Math.random() - 0.5));
  } else if (r < 0.45) {
    // Go eat
    u.state = 'toBowl';
    const dir = BOWL_POS.clone().normalize();
    u.target.set(BOWL_POS.x + dir.x * 1.1, FLOOR_Y, BOWL_POS.z + dir.z * 1.1);
  } else {
    // Random wander target
    let a = Math.random() * Math.PI * 2;
    let rr = 1 + Math.random() * 4;
    let x = Math.cos(a) * rr, z = Math.sin(a) * rr;
    // Avoid the wheel footprint
    if (Math.hypot(x - WHEEL_POS.x, z - WHEEL_POS.z) < 1.8) {
      x = -x * 0.6; z = -z * 0.6;
    }
    u.state = 'walk';
    u.target.set(x, FLOOR_Y, z);
  }
}

function walkTowards(h, dt, arriveDist) {
  const u = h.userData;
  const dx = u.target.x - h.position.x;
  const dz = u.target.z - h.position.z;
  const dist = Math.hypot(dx, dz);
  if (dist < arriveDist) return true;

  // Smoothly turn toward target
  const desired = Math.atan2(dx, dz);
  let diff = desired - u.heading;
  while (diff >  Math.PI) diff -= Math.PI * 2;
  while (diff < -Math.PI) diff += Math.PI * 2;
  u.heading += THREE.MathUtils.clamp(diff, -4 * dt, 4 * dt);
  h.rotation.y = u.heading;

  // Move
  const step = Math.min(u.speed * dt, dist);
  h.position.x += (dx / dist) * step;
  h.position.z += (dz / dist) * step;

  // Keep inside the cage
  const r = Math.hypot(h.position.x, h.position.z);
  if (r > 5.3) {
    h.position.x *= 5.3 / r;
    h.position.z *= 5.3 / r;
  }

  // Leg animation
  u.walkPhase += dt * u.speed * 9;
  animateLegs(h, 0.65);
  return false;
}

function animateLegs(h, amp) {
  const u = h.userData;
  u.legs.forEach((leg, i) => {
    leg.rotation.x = Math.sin(u.walkPhase + i * Math.PI) * amp;
  });
}

function updateHamster(h, dt, time) {
  const u = h.userData;
  // Idle breathing
  u.body.scale.y = 0.95 + Math.sin(time * 3 + u.phaseOffset) * 0.03;

  switch (u.state) {
    case 'idle':
      u.timer -= dt;
      animateLegs(h, 0);
      u.head.rotation.x = 0;
      if (u.timer <= 0) pickNextAction(h);
      break;

    case 'walk':
      if (walkTowards(h, dt, 0.3)) {
        u.state = 'idle';
        u.timer = 1 + Math.random() * 2.5;
      }
      break;

    case 'toWheel':
      if (walkTowards(h, dt, 0.35)) {
        u.state = 'wheeling';
        u.timer = 4 + Math.random() * 4;
      }
      break;

    case 'wheeling':
      u.timer -= dt;
      // Stand inside the wheel, run fast
      h.position.set(WHEEL_POS.x, FLOOR_Y + 0.32, WHEEL_POS.z);
      u.heading = Math.PI / 2;
      h.rotation.y = u.heading;
      u.walkPhase += dt * 22;
      animateLegs(h, 0.9);
      h.position.y += Math.sin(u.walkPhase) * 0.03;
      wheelSpin.rotation.z += dt * 3.5;   // wheel turns as hamster runs!
      if (u.timer <= 0) {
        u.state = 'idle';
        u.timer = 1 + Math.random() * 2;
        h.position.y = FLOOR_Y;
      }
      break;

    case 'toBowl':
      if (walkTowards(h, dt, 0.4)) {
        u.state = 'eating';
        u.timer = 2 + Math.random() * 3;
      }
      break;

    case 'eating':
      u.timer -= dt;
      animateLegs(h, 0);
      // Pecking head bob
      u.head.rotation.x = Math.sin(time * 10 + u.phaseOffset) * 0.35;
      if (u.timer <= 0) {
        u.state = 'idle';
        u.timer = 0.5 + Math.random() * 2;
        u.head.rotation.x = 0;
      }
      break;
  }
}

/* ============================================================
   CAMERA CONTROLS (simple custom orbit)
   ============================================================ */
const camTarget = new THREE.Vector3(0, 1.6, 0);
let theta = 0.7, phi = 1.1, radius = 15;
let dragging = false, lastX = 0, lastY = 0;

function updateCamera() {
  camera.position.set(
    camTarget.x + radius * Math.sin(phi) * Math.sin(theta),
    camTarget.y + radius * Math.cos(phi),
    camTarget.z + radius * Math.sin(phi) * Math.cos(theta)
  );
  camera.lookAt(camTarget);
}

const el = renderer.domElement;
el.addEventListener('pointerdown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; });
addEventListener('pointerup',   () => dragging = false);
addEventListener('pointermove', e => {
  if (!dragging) return;
  theta -= (e.clientX - lastX) * 0.006;
  phi   -= (e.clientY - lastY) * 0.004;
  phi = THREE.MathUtils.clamp(phi, 0.35, 1.45);
  lastX = e.clientX; lastY = e.clientY;
});
el.addEventListener('wheel', e => {
  radius = THREE.MathUtils.clamp(radius + e.deltaY * 0.01, 8, 24);
}, { passive: true });

/* ============================================================
   MAIN LOOP
   ============================================================ */
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;

  hamsters.forEach(h => updateHamster(h, dt, time));

  // Gentle auto-rotation when the user isn't dragging
  if (!dragging) theta += dt * 0.06;
  updateCamera();

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
| **Cage** | 26 low-poly bars, top/bottom rings, sandy tray with scattered wood chips |
| **Hamsters** | 5 hamsters in different colors, built from low-segment spheres with cheeks, ears, pink noses, and animated legs |
| **Autonomous behavior** | State machine: wander → pause → run on wheel → eat from bowl → repeat |
| **Interactive wheel** | When a hamster climbs in, the wheel actually spins and its legs sprint |
| **Food bowl** | Hamsters walk over and bob their heads pecking at pellets |
| **Camera** | Drag to orbit, scroll to zoom, gentle auto-rotation when idle |
| **Style** | Flat shading, warm pastel palette, soft shadows, fog for depth |

Everything runs from a single file with only the Three.js CDN — just open it and the hamsters start living their lives. 🐹