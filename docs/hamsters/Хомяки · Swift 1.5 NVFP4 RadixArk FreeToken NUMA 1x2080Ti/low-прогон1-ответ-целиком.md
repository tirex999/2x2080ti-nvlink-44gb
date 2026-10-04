

# Low-Poly Hamster Playground

A complete single-file project. Save as `index.html` and open in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #1a1f2b; }
  #info {
    position: fixed; top: 12px; left: 12px; z-index: 10;
    font-family: system-ui, sans-serif; color: #fff;
    background: rgba(0,0,0,.45); padding: 10px 14px; border-radius: 10px;
    font-size: 13px; line-height: 1.5; user-select: none;
  }
  #info b { color: #ffd166; }
</style>
</head>
<body>
<div id="info">
  <b>🐹 Low-Poly Hamster Playground</b><br>
  Drag = rotate &nbsp;•&nbsp; Scroll = zoom &nbsp;•&nbsp; Right-drag = pan<br>
  Click the <b>wheel</b> to spin it!
</div>

<!-- Three.js (classic build) + OrbitControls -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
/* ============================================================
   Low-Poly Hamster Playground
   One-file Three.js scene: cage, tray, autonomous hamsters,
   a clickable wheel and a food bowl.
   ============================================================ */

// ---------- Renderer / Scene / Camera ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x222a38);
scene.fog = new THREE.Fog(0x222a38, 28, 60);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 200);
camera.position.set(14, 12, 16);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1.5, 0);
controls.minDistance = 8;
controls.maxDistance = 40;
controls.maxPolarAngle = Math.PI * 0.49;

// ---------- Lights ----------
scene.add(new THREE.HemisphereLight(0xfff0d0, 0x334455, 0.7));
const sun = new THREE.DirectionalLight(0xffffff, 0.9);
sun.position.set(10, 18, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -16; sun.shadow.camera.right = 16;
sun.shadow.camera.top = 16;   sun.shadow.camera.bottom = -16;
sun.shadow.camera.far = 60;
scene.add(sun);
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// ---------- Helpers ----------
const mat = (color, flat = true) =>
  new THREE.MeshStandardMaterial({ color, flatShading: flat, roughness: 0.85, metalness: 0.05 });
const rand = (a, b) => a + Math.random() * (b - a);

// Cage inner bounds (hamsters roam inside these)
const BOUND = { x: 7.2, z: 5.2 };

// ---------- Floor / Tray ----------
const tray = new THREE.Group();
const trayTop = new THREE.Mesh(new THREE.BoxGeometry(16, 0.6, 12), mat(0x6ec6ca));
trayTop.position.y = -0.3; trayTop.receiveShadow = true; tray.add(trayTop);
// soft "bedding" patch
const bedding = new THREE.Mesh(new THREE.BoxGeometry(14, 0.2, 10), mat(0xe8c39a));
bedding.position.y = 0.1; bedding.receiveShadow = true; tray.add(bedding);
scene.add(tray);

// ---------- Cage Bars ----------
const cage = new THREE.Group();
const barMat = mat(0xf2f2f2, false);
const barGeo = new THREE.CylinderGeometry(0.07, 0.07, 5, 6);
function addBar(x, z) {
  const b = new THREE.Mesh(barGeo, barMat);
  b.position.set(x, 2.5, z); b.castShadow = true; cage.add(b);
}
for (let x = -7.5; x <= 7.5; x += 1.5) { addBar(x, -5.7); addBar(x, 5.7); }
for (let z = -5.7; z <= 5.7; z += 1.5) { addBar(-7.8, z); addBar(7.8, z); }
// top frame
const frameMat = mat(0xff6b6b, false);
function frame(w, h, d, x, y, z) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), frameMat);
  m.position.set(x, y, z); m.castShadow = true; cage.add(m);
}
frame(16, 0.3, 0.3, 0, 5, -5.7); frame(16, 0.3, 0.3, 0, 5, 5.7);
frame(0.3, 0.3, 12, -7.8, 5, 0);  frame(0.3, 0.3, 12, 7.8, 5, 0);
scene.add(cage);

// ---------- Food Bowl ----------
const bowl = new THREE.Group();
bowl.position.set(-4.5, 0, 3.2);
const bowlOuter = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 0.7, 0.7, 12), mat(0xff9f1c));
bowlOuter.position.y = 0.35; bowlOuter.castShadow = true; bowl.add(bowlOuter);
const food = new THREE.Mesh(new THREE.IcosahedronGeometry(0.7, 0), mat(0x8d5524));
food.position.y = 0.55; food.scale.y = 0.5; bowl.add(food);
scene.add(bowl);
const bowlPos = bowl.position.clone();

// ---------- Wheel (interactive) ----------
const wheel = new THREE.Group();
wheel.position.set(4.8, 2.2, -2.5);
const rim = new THREE.Mesh(new THREE.TorusGeometry(2, 0.18, 6, 18), mat(0x4dabf7, false));
rim.castShadow = true; wheel.add(rim);
const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.6, 8), mat(0xffd166, false));
hub.rotation.z = Math.PI / 2; wheel.add(hub);
for (let i = 0; i < 8; i++) {
  const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 3.8), mat(0xffd166, false));
  spoke.rotation.x = (i / 8) * Math.PI; wheel.add(spoke);
}
// stand
const stand = new THREE.Group();
const post = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 2.2, 6), mat(0xff6b6b, false));
post.position.y = 1.1; post.castShadow = true; stand.add(post);
const base = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.3, 1.4), mat(0xff6b6b, false));
base.position.y = 0.15; base.castShadow = true; stand.add(base);
stand.position.copy(wheel.position); stand.position.y = 0;
scene.add(stand); scene.add(wheel);
const wheelPos = wheel.position.clone();
let wheelSpin = 0; // angular velocity

// ---------- Build a low-poly hamster ----------
function makeHamster(color) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.8, 0), mat(color));
  body.scale.set(1.15, 0.95, 1.35); body.castShadow = true; g.add(body);

  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 0), mat(color));
  head.position.set(0, 0.25, 0.95); head.castShadow = true; g.add(head);

  // cheeks
  const cheekMat = mat(0xffc2d1);
  [-1, 1].forEach(s => {
    const c = new THREE.Mesh(new THREE.IcosahedronGeometry(0.28, 0), cheekMat);
    c.position.set(0.32 * s, 0.15, 1.15); g.add(c);
  });
  // ears
  const earMat = mat(0xffb3c1);
  [-1, 1].forEach(s => {
    const e = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.3, 5), earMat);
    e.position.set(0.3 * s, 0.65, 0.85); g.add(e);
  });
  // eyes
  const eyeMat = mat(0x111111, false);
  [-1, 1].forEach(s => {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.09, 6, 6), eyeMat);
    e.position.set(0.22 * s, 0.32, 1.32); g.add(e);
  });
  // nose
  const nose = new THREE.Mesh(new THREE.IcosahedronGeometry(0.08, 0), mat(0xff6b6b));
  nose.position.set(0, 0.22, 1.45); g.add(nose);
  // tail stub
  const tail = new THREE.Mesh(new THREE.IcosahedronGeometry(0.12, 0), mat(color));
  tail.position.set(0, 0.1, -1.05); g.add(tail);

  // legs (animated)
  const legMat = mat(0xffb3c1);
  const legs = [];
  [[-0.45, 0.55], [0.45, 0.55], [-0.45, -0.55], [0.45, -0.55]].forEach(([x, z]) => {
    const l = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.1, 0.4, 5), legMat);
    l.position.set(x, -0.75, z); l.castShadow = true; g.add(l); legs.push(l);
  });

  g.userData = { legs, body, phase: rand(0, Math.PI * 2) };
  return g;
}

// ---------- Hamsters + simple AI ----------
const hamsters = [];
const colors = [0xd9a066, 0xf4e3c1, 0x9c6644, 0xffd166];
for (let i = 0; i < 4; i++) {
  const h = makeHamster(colors[i]);
  h.position.set(rand(-BOUND.x, BOUND.x), 0.95, rand(-BOUND.z, BOUND.z));
  h.userData.state = 'pause';
  h.userData.timer = rand(0.5, 2);
  h.userData.target = new THREE.Vector3(h.position.x, 0.95, h.position.z);
  h.userData.speed = rand(1.4, 2.2);
  h.userData.wheelTime = 0;
  scene.add(h);
  hamsters.push(h);
}

function pickTarget(h) {
  const r = Math.random();
  if (r < 0.30) h.userData.target = wheelPos.clone().setY(0.95).add(new THREE.Vector3(rand(-1,1),0,rand(-1,1)));
  else if (r < 0.55) h.userData.target = bowlPos.clone().setY(0.95).add(new THREE.Vector3(rand(-0.6,0.6),0,rand(-0.6,0.6)));
  else h.userData.target = new THREE.Vector3(rand(-BOUND.x, BOUND.x), 0.95, rand(-BOUND.z, BOUND.z));
}

function updateHamster(h, dt) {
  const u = h.userData;
  u.timer -= dt;
  const toTarget = new THREE.Vector3().subVectors(u.target, h.position); toTarget.y = 0;
  const dist = toTarget.length();

  // state transitions
  if (u.state === 'pause' && u.timer <= 0) {
    pickTarget(h);
    u.state = Math.random() < 0.85 ? 'walk' : 'turn';
    u.timer = rand(1.5, 4);
  }
  if (u.state === 'walk' && dist < 0.6) {
    // arrived: near wheel? climb on!
    if (h.position.distanceTo(wheelPos) < 2.6) {
      u.state = 'wheel'; u.timer = rand(2.5, 5); u.wheelTime = 0;
    } else {
      u.state = 'pause'; u.timer = rand(0.6, 2.2);
    }
  }
  if (u.state === 'turn' && u.timer <= 0) { u.state = 'walk'; u.timer = rand(1, 3); }
  if ((u.state === 'wheel' || u.state === 'turn') && u.timer <= 0) {
    u.state = 'pause'; u.timer = rand(0.4, 1.5);
  }

  // movement
  let moving = 0;
  if (u.state === 'walk' && dist > 0.05) {
    toTarget.normalize();
    h.position.x += toTarget.x * u.speed * dt;
    h.position.z += toTarget.z * u.speed * dt;
    h.position.x = Math.max(-BOUND.x, Math.min(BOUND.x, h.position.x));
    h.position.z = Math.max(-BOUND.z, Math.min(BOUND.z, h.position.z));
    const yaw = Math.atan2(toTarget.x, toTarget.z);
    h.rotation.y = lerpAngle(h.rotation.y, yaw, 0.12);
    moving = 1;
  }
  if (u.state === 'turn') {
    h.rotation.y += dt * 3; moving = 0.3;
  }
  if (u.state === 'wheel') {
    // sit on wheel, spin it
    h.position.lerp(wheelPos.clone().setY(2.2), 0.15);
    wheelSpin = Math.min(wheelSpin + dt * 6, 9);
    u.wheelTime += dt;
    moving = 1;
  }

  // leg animation + body bob
  u.phase += dt * (moving > 0 ? 14 : 2);
  u.legs.forEach((l, i) => { l.rotation.x = Math.sin(u.phase + i * Math.PI) * 0.6 * moving; });
  u.body.position.y = Math.sin(u.phase * 2) * 0.05 * moving;
}

function lerpAngle(a, b, t) {
  let d = ((b - a + Math.PI) % (Math.PI * 2)) - Math.PI;
  if (d < -Math.PI) d += Math.PI * 2;
  return a + d * t;
}

// ---------- Click the wheel to spin it ----------
const ray = new THREE.Raycaster();
const mouse = new THREE.Vector2();
renderer.domElement.addEventListener('pointerdown', (e) => {
  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;
  ray.setFromCamera(mouse, camera);
  if (ray.intersectObject(wheel, true).length) wheelSpin += 14;
});

// ---------- Resize ----------
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// ---------- Loop ----------
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);

  hamsters.forEach(h => updateHamster(h, dt));

  wheel.rotation.x += wheelSpin * dt;
  wheelSpin *= 0.96; // friction

  controls.update();
  renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>
```

## How it works

**Scene construction** — Everything is built from low-poly primitives (`IcosahedronGeometry`, low-segment cylinders/cones) with `flatShading: true` for the chunky, cute look. The cage is a tray + bedding + a ring of bars + a colored top frame.

**Hamsters** — Each is a `Group` (body, head, puffy cheeks, cone ears, eyes, nose, tail stub, four animated legs). Four color variants for variety.

**Autonomous AI** — A small state machine per hamster: `pause → walk/turn → (wheel?) → pause`. They steer toward a target, face their heading via `lerpAngle`, animate legs with a sine wave, and bob their bodies. With some probability they head to the **food bowl** or the **wheel**; near the wheel they climb on and spin it.

**Interactive wheel** — Click it (raycast) to add spin; a hamster riding it also spins it. Friction (`wheelSpin *= 0.96`) makes it coast down naturally.

**Camera** — `OrbitControls` with damping: drag to rotate, scroll to zoom, right-drag to pan.

**Stability** — Uses the proven non-module `r128` build (no import-map quirks), clamps `dt`, and keeps the scene small. Just open the file — it runs immediately.

Easy tweaks: change `colors`, `BOUND`, hamster count, `u.speed`, or the `pickTarget` probabilities to change behavior.