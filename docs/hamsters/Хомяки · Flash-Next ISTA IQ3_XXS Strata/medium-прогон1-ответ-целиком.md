# Low-Poly Hamster Playground

A complete single-file project. Save as `index.html` and open in any modern browser.

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
  #hud {
    position: fixed; top: 14px; left: 14px; font-family: "Comic Sans MS", Verdana, sans-serif;
    color: #5a3b2c; background: rgba(255,255,255,.75); padding: 10px 14px;
    border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.15); user-select: none;
  }
  #hud h1 { margin: 0 0 4px; font-size: 18px; }
  #hud p  { margin: 0; font-size: 12px; }
</style>
</head>
<body>
<div id="hud">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate &nbsp;•&nbsp; Scroll to zoom</p>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ============================================================
//  SCENE / RENDERER / CAMERA
// ============================================================
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9d6);
scene.fog = new THREE.Fog(0xffe9d6, 22, 40);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);

// Simple custom orbit camera (no extra scripts needed)
const orbit = { theta: 0.7, phi: 1.05, radius: 13, target: new THREE.Vector3(0, 1.2, 0) };
function updateCamera() {
  orbit.phi = Math.max(0.35, Math.min(1.45, orbit.phi));
  orbit.radius = Math.max(6, Math.min(24, orbit.radius));
  camera.position.set(
    orbit.target.x + orbit.radius * Math.sin(orbit.phi) * Math.sin(orbit.theta),
    orbit.target.y + orbit.radius * Math.cos(orbit.phi),
    orbit.target.z + orbit.radius * Math.sin(orbit.phi) * Math.cos(orbit.theta)
  );
  camera.lookAt(orbit.target);
}
updateCamera();

let dragging = false, px = 0, py = 0;
renderer.domElement.addEventListener('pointerdown', e => { dragging = true; px = e.clientX; py = e.clientY; });
addEventListener('pointerup',   () => dragging = false);
addEventListener('pointermove', e => {
  if (!dragging) return;
  orbit.theta -= (e.clientX - px) * 0.006;
  orbit.phi   -= (e.clientY - py) * 0.006;
  px = e.clientX; py = e.clientY;
  updateCamera();
});
addEventListener('wheel', e => { orbit.radius += e.deltaY * 0.01; updateCamera(); });

// ============================================================
//  LIGHTS
// ============================================================
scene.add(new THREE.HemisphereLight(0xfff2e0, 0xb08a6a, 0.85));
const sun = new THREE.DirectionalLight(0xffffff, 0.75);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -10; sun.shadow.camera.right = 10;
sun.shadow.camera.top = 10;   sun.shadow.camera.bottom = -10;
scene.add(sun);

// Ground table
const table = new THREE.Mesh(
  new THREE.PlaneGeometry(60, 60),
  new THREE.MeshStandardMaterial({ color: 0xf7c9a0 })
);
table.rotation.x = -Math.PI / 2;
table.receiveShadow = true;
scene.add(table);

// ============================================================
//  CAGE: tray, bedding, bars
// ============================================================
const CAGE = { w: 10, d: 7, wallH: 3.2 };
const cage = new THREE.Group();
scene.add(cage);

const tray = new THREE.Mesh(
  new THREE.BoxGeometry(CAGE.w, 0.7, CAGE.d),
  new THREE.MeshStandardMaterial({ color: 0x4fb3a9, flatShading: true })
);
tray.position.y = 0.35;
tray.castShadow = tray.receiveShadow = true;
cage.add(tray);

const bedding = new THREE.Mesh(
  new THREE.BoxGeometry(CAGE.w - 0.5, 0.12, CAGE.d - 0.5),
  new THREE.MeshStandardMaterial({ color: 0xe8c98a, flatShading: true })
);
bedding.position.y = 0.72;
bedding.receiveShadow = true;
cage.add(bedding);

// Bars
const barMat = new THREE.MeshStandardMaterial({ color: 0xd8d8de, metalness: 0.4, roughness: 0.5 });
const barGeo = new THREE.CylinderGeometry(0.05, 0.05, CAGE.wallH, 5);
function addBar(x, z) {
  const b = new THREE.Mesh(barGeo, barMat);
  b.position.set(x, 0.7 + CAGE.wallH / 2, z);
  b.castShadow = true;
  cage.add(b);
}
for (let x = -CAGE.w/2; x <= CAGE.w/2 + 0.01; x += 0.8) { addBar(x, -CAGE.d/2); addBar(x, CAGE.d/2); }
for (let z = -CAGE.d/2; z <= CAGE.d/2 + 0.01; z += 0.8) { addBar(-CAGE.w/2, z); addBar(CAGE.w/2, z); }

// Top rails
const railGeo = new THREE.CylinderGeometry(0.07, 0.07, CAGE.w, 6);
[-CAGE.d/2, CAGE.d/2].forEach(z => {
  const r = new THREE.Mesh(railGeo, barMat);
  r.position.set(0, 0.7 + CAGE.wallH, z);
  cage.add(r);
});
const railGeo2 = new THREE.CylinderGeometry(0.07, 0.07, CAGE.d, 6);
[-CAGE.w/2, CAGE.w/2].forEach(x => {
  const r = new THREE.Mesh(railGeo2, barMat);
  r.rotation.z = Math.PI / 2; r.rotation.y = Math.PI / 2;
  r.position.set(x, 0.7 + CAGE.wallH, 0);
  cage.add(r);
});

// ============================================================
//  INTERACTIVE OBJECTS: wheel + food bowl
// ============================================================
// Hamster wheel (spins when a hamster is running in it)
const wheel = new THREE.Group();
wheel.position.set(4.1, 1.75, 0);
cage.add(wheel);

const wheelInner = new THREE.Group();
wheel.add(wheelInner);

const rim = new THREE.Mesh(
  new THREE.TorusGeometry(0.95, 0.1, 6, 18),
  new THREE.MeshStandardMaterial({ color: 0xff6f61, flatShading: true })
);
wheelInner.add(rim);

const disc = new THREE.Mesh(
  new THREE.CylinderGeometry(0.9, 0.9, 0.5, 18),
  new THREE.MeshStandardMaterial({ color: 0xffd166, flatShading: true })
);
disc.rotation.x = Math.PI / 2;
wheelInner.add(disc);

for (let i = 0; i < 6; i++) {
  const spoke = new THREE.Mesh(
    new THREE.BoxGeometry(0.06, 1.8, 0.06),
    new THREE.MeshStandardMaterial({ color: 0xff6f61, flatShading: true })
  );
  spoke.rotation.z = i * Math.PI / 6;
  wheelInner.add(spoke);
}
const axle = new THREE.Mesh(
  new THREE.CylinderGeometry(0.08, 0.08, 1.4, 8),
  barMat
);
axle.rotation.x = Math.PI / 2;
wheel.add(axle);

let wheelSpeed = 0.3; // idle spin; boosted when a hamster runs

// Food bowl
const bowl = new THREE.Group();
bowl.position.set(-3.2, 0.78, 1.6);
cage.add(bowl);
const bowlMesh = new THREE.Mesh(
  new THREE.CylinderGeometry(0.5, 0.32, 0.3, 10),
  new THREE.MeshStandardMaterial({ color: 0x7ec8e3, flatShading: true })
);
bowlMesh.castShadow = true;
bowl.add(bowlMesh);
for (let i = 0; i < 6; i++) {
  const pellet = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.09, 0),
    new THREE.MeshStandardMaterial({ color: 0xb5651d, flatShading: true })
  );
  pellet.position.set(Math.cos(i) * 0.22, 0.16, Math.sin(i) * 0.22);
  bowl.add(pellet);
}

// A couple of cute decorations
[[-2, -1.8, 0x90c183], [1.5, 2.2, 0x90c183]].forEach(([x, z, c]) => {
  const rock = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.35, 0),
    new THREE.MeshStandardMaterial({ color: c, flatShading: true })
  );
  rock.position.set(x, 0.9, z);
  rock.castShadow = true;
  cage.add(rock);
});

// ============================================================
//  HAMSTERS
// ============================================================
const COLORS = [0xf4a261, 0xe76f51, 0xffd166, 0xf8ad9d, 0xcd9cc5, 0xa8dadc];
const hamsters = [];

function makeHamster(color) {
  const g = new THREE.Group();
  const mat  = new THREE.MeshStandardMaterial({ color, flatShading: true });
  const mat2 = new THREE.MeshStandardMaterial({
    color: new THREE.Color(color).lerp(new THREE.Color(0xffffff), 0.45), flatShading: true
  });

  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.45, 1), mat);
  body.scale.set(1.15, 0.95, 1.3);
  body.position.y = 0.45;
  body.castShadow = true;
  g.add(body);

  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.28, 1), mat);
  head.position.set(0, 0.62, 0.52);
  head.castShadow = true;
  g.add(head);

  const cheekL = new THREE.Mesh(new THREE.IcosahedronGeometry(0.12, 0), mat2);
  cheekL.position.set( 0.2, 0.55, 0.62);
  const cheekR = cheekL.clone(); cheekR.position.x = -0.2;
  g.add(cheekL, cheekR);

  const nose = new THREE.Mesh(new THREE.IcosahedronGeometry(0.06, 0),
    new THREE.MeshStandardMaterial({ color: 0xff8fa3, flatShading: true }));
  nose.position.set(0, 0.58, 0.8);
  g.add(nose);

  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x222222 });
  const eyeGeo = new THREE.SphereGeometry(0.05, 6, 6);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat); eyeL.position.set( 0.14, 0.68, 0.72);
  const eyeR = new THREE.Mesh(eyeGeo, eyeMat); eyeR.position.set(-0.14, 0.68, 0.72);
  g.add(eyeL, eyeR);

  const earGeo = new THREE.ConeGeometry(0.1, 0.18, 5);
  const earL = new THREE.Mesh(earGeo, mat2); earL.position.set( 0.18, 0.88, 0.4); earL.rotation.x = -0.3;
  const earR = new THREE.Mesh(earGeo, mat2); earR.position.set(-0.18, 0.88, 0.4); earR.rotation.x = -0.3;
  g.add(earL, earR);

  const tail = new THREE.Mesh(new THREE.IcosahedronGeometry(0.09, 0), mat2);
  tail.position.set(0, 0.4, -0.6);
  g.add(tail);

  const legGeo = new THREE.CylinderGeometry(0.07, 0.05, 0.22, 5);
  const legs = [];
  [[0.28, 0.35], [-0.28, 0.35], [0.28, -0.35], [-0.28, -0.35]].forEach(([x, z]) => {
    const leg = new THREE.Mesh(legGeo, mat);
    leg.position.set(x, 0.14, z);
    leg.castShadow = true;
    g.add(leg);
    legs.push(leg);
  });

  return { group: g, body, head, earL, earR, legs };
}

const BOWL_POS = bowl.position.clone();
const WHEEL_POS = new THREE.Vector3(3.4, 0.78, 0); // running spot in front of wheel

function spawnHamster() {
  const parts = makeHamster(COLORS[hamsters.length % COLORS.length]);
  const h = {
    ...parts,
    state: 'idle',
    timer: Math.random() * 2,
    heading: Math.random() * Math.PI * 2,
    speed: 0.9 + Math.random() * 0.4,
    target: new THREE.Vector3(),
    phase: Math.random() * 10
  };
  h.group.position.set(-2 + Math.random() * 4, 0.78, -1.5 + Math.random() * 3);
  cage.add(h.group);
  hamsters.push(h);
}
for (let i = 0; i < 5; i++) spawnHamster();

// ============================================================
//  HAMSTER BEHAVIOR
// ============================================================
function pickTarget(h) {
  const r = Math.random();
  if (r < 0.3) { h.target.copy(BOWL_POS); h.nextState = 'eat'; }
  else if (r < 0.5) { h.target.copy(WHEEL_POS); h.nextState = 'run'; }
  else {
    h.target.set(
      (Math.random() - 0.5) * (CAGE.w - 2),
      0.78,
      (Math.random() - 0.5) * (CAGE.d - 2)
    );
    h.nextState = 'idle';
  }
}

function updateHamster(h, dt, t) {
  h.timer -= dt;

  if (h.state === 'idle') {
    // gentle breathing / wiggle
    h.body.scale.y = 0.95 + Math.sin(t * 3 + h.phase) * 0.03;
    h.earL.rotation.z = Math.sin(t * 5 + h.phase) * 0.15;
    h.earR.rotation.z = -Math.sin(t * 5 + h.phase) * 0.15;
    h.legs.forEach(l => l.rotation.x = 0);

    if (h.timer <= 0) {
      pickTarget(h);
      h.state = 'walk';
      h.timer = 8; // max walk time before giving up
    }
  }
  else if (h.state === 'walk') {
    const pos = h.group.position;
    const dir = h.target.clone().sub(pos); dir.y = 0;
    const dist = dir.length();

    if (dist > 0.15) {
      const desired = Math.atan2(dir.x, dir.z);
      let diff = desired - h.heading;
      while (diff >  Math.PI) diff -= 2 * Math.PI;
      while (diff < -Math.PI) diff += 2 * Math.PI;
      h.heading += Math.max(-3 * dt, Math.min(3 * dt, diff));

      pos.x += Math.sin(h.heading) * h.speed * dt;
      pos.z += Math.cos(h.heading) * h.speed * dt;

      // waddle animation
      h.legs.forEach((l, i) => l.rotation.x = Math.sin(t * 10 + h.phase + (i % 2) * Math.PI) * 0.6);
      h.group.position.y = 0.78 + Math.abs(Math.sin(t * 8 + h.phase)) * 0.04;
      h.body.rotation.z = Math.sin(t * 10 + h.phase) * 0.06;
    }

    if (dist <= 0.3 || h.timer <= 0) {
      h.state = h.nextState;
      h.timer = h.nextState === 'eat' ? 2.5 : 3.5;
      h.body.rotation.z = 0;
      h.group.position.y = 0.78;
    }
  }
  else if (h.state === 'eat') {
    h.heading = Math.atan2(BOWL_POS.x - h.group.position.x, BOWL_POS.z - h.group.position.z) + Math.PI;
    h.group.rotation.y = h.heading;
    // nibble: head bobs
    h.head.position.y = 0.62 + Math.sin(t * 14 + h.phase) * 0.06;
    h.head.rotation.x = Math.sin(t * 14 + h.phase) * 0.2;
    h.legs.forEach(l => l.rotation.x = 0);
    if (h.timer <= 0) { h.state = 'idle'; h.timer = 1 + Math.random() * 2; h.head.position.y = 0.62; h.head.rotation.x = 0; }
  }
  else if (h.state === 'run') {
    h.heading = Math.atan2(WHEEL_POS.x - h.group.position.x, WHEEL_POS.z - h.group.position.z) + Math.PI;
    h.group.rotation.y = h.heading;
    // running legs + fast bob
    h.legs.forEach((l, i) => l.rotation.x = Math.sin(t * 22 + h.phase + (i % 2) * Math.PI) * 0.9);
    h.group.position.y = 0.78 + Math.abs(Math.sin(t * 16 + h.phase)) * 0.06;
    if (h.timer <= 0) { h.state = 'idle'; h.timer = 1 + Math.random() * 2; }
  }

  if (h.state !== 'walk') h.group.rotation.y = h.heading;
  else h.group.rotation.y = h.heading;

  // keep inside cage
  h.group.position.x = Math.max(-CAGE.w/2 + 0.6, Math.min(CAGE.w/2 - 0.6, h.group.position.x));
  h.group.position.z = Math.max(-CAGE.d/2 + 0.6, Math.min(CAGE.d/2 - 0.6, h.group.position.z));
}

// ============================================================
//  MAIN LOOP
// ============================================================
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  let runnerNear = false;
  for (const h of hamsters) {
    updateHamster(h, dt, t);
    if (h.state === 'run') runnerNear = true;
  }

  // wheel spins faster when a hamster is running
  const targetSpeed = runnerNear ? 9 : 0.3;
  wheelSpeed += (targetSpeed - wheelSpeed) * dt * 3;
  wheelInner.rotation.z -= wheelSpeed * dt;

  // gentle auto-rotate when idle
  if (!dragging) { orbit.theta += dt * 0.05; updateCamera(); }

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

**Scene**
- A teal cage tray with sandy bedding, metal bars and top rails, sitting on a warm table surface
- A **hamster wheel** (spins slowly, speeds up when a hamster runs in it) and a **food bowl** with pellets
- Soft shadows, hemisphere + directional lighting, and a fog-faded pastel background

**Hamsters (5 of them)**
- Built entirely from low-poly primitives (icosahedrons, cones, cylinders) with `flatShading` for the classic low-poly look
- Random cute colors, chubby cheeks, tiny ears, and a nub tail

**Autonomous behavior (state machine)**
- `idle` → breathing wiggle + ear twitch, then picks a goal
- `walk` → steers toward the goal with a waddling leg animation and body bob
- `eat` → walks to the bowl and nibbles (head bobbing)
- `run` → goes to the wheel and sprints, making the wheel spin fast

**Controls**
- Drag to orbit, scroll to zoom, gentle auto-rotation when idle — implemented with plain pointer events, so no extra control libraries are needed.