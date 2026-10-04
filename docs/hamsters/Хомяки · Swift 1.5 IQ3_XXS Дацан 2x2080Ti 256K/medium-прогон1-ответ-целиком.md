# 🐹 Low-Poly Hamster Playground

A complete single-file project. Save it as `index.html` and open in any modern browser — no build steps, no server needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐹 Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; height: 100%; }
  canvas { display: block; touch-action: none; }
  #ui {
    position: fixed; top: 14px; left: 16px; color: #7a4b2a;
    font-family: "Comic Sans MS", "Trebuchet MS", sans-serif;
    pointer-events: none; user-select: none; text-shadow: 0 1px 0 #fff;
  }
  #ui h1 { margin: 0; font-size: 22px; }
  #ui p  { margin: 4px 0 0; font-size: 13px; opacity: .8; }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate the camera • Scroll / pinch-drag to zoom</p>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
/* ============================================================
   LOW-POLY HAMSTER PLAYGROUND
   Scene: tray + bedding, cage bars, running wheel, food bowl,
   toy ball, and 5 hamsters with simple autonomous behavior:
   walk -> idle -> wheel / bowl / ball chasing.
   ============================================================ */

// ---------- Renderer / Scene / Camera ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9f2);
scene.fog = new THREE.Fog(0xffe9f2, 22, 45);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 100);
const camTarget = new THREE.Vector3(0, 1.6, 0);
let camTheta = 0.7, camPhi = 1.05, camRadius = 14;

function updateCamera() {
  camPhi    = THREE.MathUtils.clamp(camPhi, 0.25, 1.45);
  camRadius = THREE.MathUtils.clamp(camRadius, 7, 24);
  camera.position.set(
    camTarget.x + camRadius * Math.sin(camPhi) * Math.sin(camTheta),
    camTarget.y + camRadius * Math.cos(camPhi),
    camTarget.z + camRadius * Math.sin(camPhi) * Math.cos(camTheta)
  );
  camera.lookAt(camTarget);
}
updateCamera();

// ---------- Lights ----------
scene.add(new THREE.HemisphereLight(0xfff4e0, 0xb9d8c6, 0.9));
const sun = new THREE.DirectionalLight(0xfff1d6, 0.85);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -10; sun.shadow.camera.right = 10;
sun.shadow.camera.top = 10;   sun.shadow.camera.bottom = -10;
scene.add(sun);

// ---------- Simple orbit controls (mouse + touch) ----------
let dragging = false, lastX = 0, lastY = 0;
const dom = renderer.domElement;
dom.addEventListener('pointerdown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; });
addEventListener('pointerup',   () => dragging = false);
addEventListener('pointermove', e => {
  if (!dragging) return;
  camTheta -= (e.clientX - lastX) * 0.008;
  camPhi   -= (e.clientY - lastY) * 0.008;
  lastX = e.clientX; lastY = e.clientY;
  updateCamera();
});
dom.addEventListener('wheel', e => { camRadius += e.deltaY * 0.01; updateCamera(); }, { passive: true });

// ---------- Helpers ----------
const mat = (color, extra = {}) => new THREE.MeshLambertMaterial(Object.assign({ color, flatShading: true }, extra));
function mesh(geo, material, x, y, z, cast = true) {
  const m = new THREE.Mesh(geo, material);
  m.position.set(x, y, z);
  m.castShadow = cast;
  return m;
}
const rand = (a, b) => a + Math.random() * (b - a);
function angleLerp(a, b, t) {
  let d = ((b - a + Math.PI) % (Math.PI * 2)) - Math.PI;
  if (d < -Math.PI) d += Math.PI * 2;
  return a + d * t;
}

// ---------- Ground + tray ----------
const ground = mesh(new THREE.CircleGeometry(30, 24), mat(0xcfe8d5), 0, -0.62, 0, false);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

const tray = mesh(new THREE.CylinderGeometry(5.4, 5.1, 1.1, 26), mat(0x6fc7b0), 0, -0.05, 0);
tray.receiveShadow = true;
scene.add(tray);

const floorDisc = mesh(new THREE.CircleGeometry(5.0, 26), mat(0xf3e2c0), 0, 0.51, 0, false);
floorDisc.rotation.x = -Math.PI / 2;
floorDisc.receiveShadow = true;
scene.add(floorDisc);

// ---------- Bedding scatter (wood shavings) ----------
const beddingColors = [0xf2d9a0, 0xe8c98a, 0xf7e6bf];
for (let i = 0; i < 55; i++) {
  const a = Math.random() * Math.PI * 2, r = Math.sqrt(Math.random()) * 4.7;
  const b = mesh(
    new THREE.BoxGeometry(rand(0.25, 0.6), rand(0.08, 0.18), rand(0.25, 0.6)),
    mat(beddingColors[i % 3]),
    Math.sin(a) * r, 0.58, Math.cos(a) * r
  );
  b.rotation.y = Math.random() * Math.PI;
  scene.add(b);
}

// ---------- Cage bars ----------
const cageMat = mat(0xf7f3ee);
const BAR_COUNT = 42, BAR_R = 5.15;
for (let i = 0; i < BAR_COUNT; i++) {
  const a = (i / BAR_COUNT) * Math.PI * 2;
  scene.add(mesh(new THREE.CylinderGeometry(0.05, 0.05, 3.6, 5), cageMat,
    Math.sin(a) * BAR_R, 2.3, Math.cos(a) * BAR_R));
}
[1.0, 3.9].forEach(y => {
  const ring = mesh(new THREE.TorusGeometry(BAR_R, 0.07, 5, 40), mat(0xff9db4), 0, y, 0);
  ring.rotation.x = Math.PI / 2;
  scene.add(ring);
});

// ---------- Running wheel (interactive object #1) ----------
const wheelGroup = new THREE.Group();
wheelGroup.position.set(0, 1.75, -3.6);
scene.add(wheelGroup);

const wheel = new THREE.Group();
wheelGroup.add(wheel);
const disc = mesh(new THREE.TorusGeometry(1.15, 0.14, 5, 18), mat(0x9fb8ff), 0, 0, 0);
wheel.add(disc);
for (let i = 0; i < 6; i++) {
  const spoke = mesh(new THREE.BoxGeometry(0.1, 2.15, 0.08), mat(0xc9d8ff), 0, 0, 0);
  spoke.rotation.z = (i / 6) * Math.PI;
  wheel.add(spoke);
}
wheel.add(mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.5, 8), mat(0xff9db4), 0, 0, 0)).rotation.x = Math.PI / 2;
// Stand
[-1, 1].forEach(s => {
  const post = mesh(new THREE.BoxGeometry(0.22, 2.4, 0.22), mat(0xff9db4), s * 0.9, -1.15, 0);
  wheelGroup.add(post);
});
let wheelRunning = 0; // spin speed target

// ---------- Food bowl (interactive object #2) ----------
const bowlPos = new THREE.Vector3(2.6, 0.55, 2.4);
const bowl = new THREE.Group();
bowl.position.copy(bowlPos);
bowl.add(mesh(new THREE.CylinderGeometry(0.75, 0.55, 0.4, 10), mat(0xffb366), 0, 0.2, 0));
bowl.add(mesh(new THREE.TorusGeometry(0.72, 0.09, 5, 12), mat(0xff9147), 0, 0.4, 0)).rotation.x = Math.PI / 2;
for (let i = 0; i < 7; i++)
  bowl.add(mesh(new THREE.IcosahedronGeometry(0.13, 0), mat(0xc98d5a), rand(-0.4, 0.4), 0.45, rand(-0.4, 0.4)));
scene.add(bowl);
let bowlOccupied = false;

// ---------- Toy ball (pushable!) ----------
const ball = mesh(new THREE.IcosahedronGeometry(0.5, 1), mat(0xff6f91), 1.5, 1.05, -0.5);
scene.add(ball);
const ballVel = new THREE.Vector3();

// ---------- Hamster factory ----------
const furColors = [0xf6e3b8, 0xe8a94f, 0xffffff, 0xb0a89a, 0xd98e5f];
const hamsters = [];

function makeHamster(color) {
  const h = new THREE.Group();
  const fur = mat(color);
  const dark = mat(0x3b2f2a);
  const pink = mat(0xff9aa8);

  const body = mesh(new THREE.IcosahedronGeometry(0.5, 1), fur, 0, 0.55, 0);
  body.scale.set(1.0, 0.85, 1.25);
  h.add(body);

  const headPivot = new THREE.Group();
  headPivot.position.set(0, 0.72, 0.45);
  h.add(headPivot);
  const head = mesh(new THREE.IcosahedronGeometry(0.34, 1), fur, 0, 0, 0);
  headPivot.add(head);
  headPivot.add(mesh(new THREE.IcosahedronGeometry(0.09, 0), pink, 0, -0.05, 0.32));   // nose
  headPivot.add(mesh(new THREE.IcosahedronGeometry(0.15, 0), pink,  0.26, -0.02, 0.16)); // cheeks
  headPivot.add(mesh(new THREE.IcosahedronGeometry(0.15, 0), pink, -0.26, -0.02, 0.16));
  headPivot.add(mesh(new THREE.IcosahedronGeometry(0.055, 0), dark,  0.16, 0.12, 0.28)); // eyes
  headPivot.add(mesh(new THREE.IcosahedronGeometry(0.055, 0), dark, -0.16, 0.12, 0.28));
  const ears = new THREE.Group();
  ears.position.set(0, 0.22, -0.05);
  headPivot.add(ears);
  [-1, 1].forEach(s => {
    const ear = mesh(new THREE.CylinderGeometry(0.11, 0.14, 0.14, 6), fur, s * 0.24, 0.1, 0);
    ear.rotation.z = -s * 0.5;
    ears.add(ear);
  });

  h.add(mesh(new THREE.IcosahedronGeometry(0.11, 0), fur, 0, 0.5, -0.62)); // tail

  const legs = [];
  const legGeo = new THREE.BoxGeometry(0.14, 0.26, 0.14);
  [[0.3, 0.32], [-0.3, 0.32], [0.3, -0.32], [-0.3, -0.32]].forEach(([x, z], i) => {
    const pivot = new THREE.Group();
    pivot.position.set(x, 0.32, z);
    pivot.add(mesh(legGeo, fur, 0, -0.13, 0));
    pivot.userData.phase = [0, Math.PI, Math.PI, 0][i];
    h.add(pivot);
    legs.push(pivot);
  });

  h.userData = {
    state: 'idle', timer: rand(0.5, 2), heading: rand(0, Math.PI * 2),
    target: new THREE.Vector3(), legs, headPivot, ears, speed: rand(1.0, 1.5),
    waddle: rand(8, 11)
  };
  scene.add(h);
  hamsters.push(h);
  return h;
}

for (let i = 0; i < 5; i++) {
  const h = makeHamster(furColors[i]);
  const a = Math.random() * Math.PI * 2, r = rand(1, 3.5);
  h.position.set(Math.sin(a) * r, 0.5, Math.cos(a) * r);
}

// ---------- Behavior ----------
const WHEEL_ENTRY = new THREE.Vector3(0, 0.5, -2.35);
const CAGE_LIMIT = 4.5;
let wheelBusy = false;

function pickAction(h) {
  const u = h.userData;
  const roll = Math.random();
  if (!wheelBusy && roll < 0.22) {          // go run on the wheel
    u.state = 'toWheel'; u.target.copy(WHEEL_ENTRY); u.timer = 10;
  } else if (!bowlOccupied && roll < 0.42) { // go eat
    u.state = 'toBowl';
    u.target.set(bowlPos.x + rand(-0.9, 0.9), 0.5, bowlPos.z + rand(-0.9, 0.9));
    u.timer = 12;
  } else if (roll < 0.65) {                  // wander
    const a = Math.random() * Math.PI * 2, r = Math.sqrt(Math.random()) * CAGE_LIMIT;
    u.state = 'walk';
    u.target.set(Math.sin(a) * r, 0.5, Math.cos(a) * r);
    u.timer = rand(3, 7);
  } else {
    u.state = 'idle'; u.timer = rand(1.2, 3.5);
  }
}

function updateHamster(h, dt, t) {
  const u = h.userData;
  u.timer -= dt;

  const legSwing = amp => u.legs.forEach(l =>
    l.rotation.x = Math.sin(t * u.waddle * (amp > 0.5 ? 1.6 : 1) + l.userData.phase) * amp);
  const earWiggle = () => { u.ears.rotation.z = Math.sin(t * 2.4 + h.id) * 0.12; };

  switch (u.state) {
    case 'idle': {
      legSwing(0.05); earWiggle();
      u.headPivot.rotation.x = Math.sin(t * 3) * 0.08; // sniffing bob
      if (u.timer <= 0) pickAction(h);
      break;
    }
    case 'walk': case 'toWheel': case 'toBowl': {
      const dx = u.target.x - h.position.x, dz = u.target.z - h.position.z;
      const dist = Math.hypot(dx, dz);
      const want = Math.atan2(dx, dz);
      h.rotation.y = angleLerp(h.rotation.y, want, dt * 6);
      if (dist > 0.25) {
        h.position.x += Math.sin(h.rotation.y) * u.speed * dt;
        h.position.z += Math.cos(h.rotation.y) * u.speed * dt;
      }
      // keep inside cage
      const r = Math.hypot(h.position.x, h.position.z);
      if (r > CAGE_LIMIT) {
        h.position.x *= CAGE_LIMIT / r;
        h.position.z *= CAGE_LIMIT / r;
        pickAction(h);
      }
      h.position.y = 0.5 + Math.abs(Math.sin(t * u.waddle)) * 0.06; // cute hop
      legSwing(0.55); earWiggle();
      u.headPivot.rotation.x = 0;

      // bump the toy ball
      const bd = h.position.clone().sub(ball.position); bd.y = 0;
      if (bd.length() < 0.95) ballVel.add(bd.normalize().multiplyScalar(dt * 9));

      if (u.state === 'toWheel' && dist < 0.35) {
        u.state = 'wheel'; u.timer = rand(4, 8); wheelBusy = true;
        h.position.copy(WHEEL_ENTRY); h.rotation.y = Math.PI;
      } else if (u.state === 'toBowl' && dist < 0.45) {
        u.state = 'eat'; u.timer = rand(2.5, 5); bowlOccupied = true;
      } else if ((u.state === 'walk' && dist < 0.35) || u.timer <= 0) {
        u.state = 'idle'; u.timer = rand(1, 3);
      }
      break;
    }
    case 'wheel': {
      legSwing(0.8); // little legs blazing
      u.headPivot.rotation.x = -0.15;
      u.ears.rotation.z = Math.sin(t * 12) * 0.2;
      h.position.y = 0.5 + Math.sin(t * u.waddle * 2.4) * 0.05;
      wheelRunning = 5; // spin the wheel!
      if (u.timer <= 0) {
        wheelRunning = 0; wheelBusy = false;
        h.position.z += 1.0;
        u.state = 'idle'; u.timer = rand(1, 2.5);
      }
      break;
    }
    case 'eat': {
      legSwing(0.05);
      u.headPivot.rotation.x = 0.55 + Math.sin(t * 10) * 0.28; // pecking at food
      u.ears.rotation.z = Math.sin(t * 6) * 0.18;
      h.position.y = 0.5;
      if (u.timer <= 0) {
        bowlOccupied = false;
        u.headPivot.rotation.x = 0;
        u.state = 'idle'; u.timer = rand(1, 2);
      }
      break;
    }
  }
}

// ---------- Main loop ----------
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  hamsters.forEach(h => updateHamster(h, dt, t));

  // wheel spin (with easing)
  const targetSpeed = wheelRunning;
  wheelSpin += (targetSpeed - wheelSpin) * dt * 4;
  wheel.rotation.z -= wheelSpin * dt;

  // toy ball physics: velocity, friction, cage wall bounce
  ball.position.addScaledVector(ballVel, dt);
  ballVel.multiplyScalar(1 - dt * 1.6);
  ball.rotation.x += ballVel.z * dt * 2;
  ball.rotation.z -= ballVel.x * dt * 2;
  const br = Math.hypot(ball.position.x, ball.position.z);
  if (br > CAGE_LIMIT) {
    const nx = ball.position.x / br, nz = ball.position.z / br;
    ball.position.set(nx * CAGE_LIMIT, 1.05, nz * CAGE_LIMIT);
    const dot = ballVel.x * nx + ballVel.z * nz;
    ballVel.x -= 2 * dot * nx; ballVel.z -= 2 * dot * nz;
  }

  renderer.render(scene, camera);
}
let wheelSpin = 0;
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
- Rounded mint tray with a sandy floor, scattered low-poly "wood shaving" bedding
- Open-top cage: 42 pastel bars with two pink rings (open top keeps the view clear)
- Soft shadows + hemisphere lighting for the cute flat-shaded look

**Interactive objects** 🎡
- **Running wheel** — hamsters walk to it, jump in, and sprint; the wheel spins up and slows down smoothly
- **Food bowl** — a hamster hops in, pecks at pellets (head-bobbing animation), then leaves
- **Toy ball** — hamsters physically bump it; it rolls, spins, and bounces off the cage wall with friction

**Hamster behavior** 🐹 (simple state machine per hamster)
- `idle` → sniffing bob + ear wiggles
- `walk` → picks a random spot, smooth-turns toward it, hop-waddles with alternating legs
- `wheel` → blazing little legs, wheel spins while occupied
- `eat` → head pecking at the bowl
- Wheel and bowl are single-occupancy, so hamsters negotiate politely

**Camera controls**: drag to orbit, scroll to zoom (custom lightweight orbit — no external control module needed, keeping everything in one file).