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
  html, body { margin: 0; height: 100%; overflow: hidden; background: #ffe9f0; font-family: 'Segoe UI', Arial, sans-serif; }
  #hud {
    position: fixed; top: 14px; left: 50%; transform: translateX(-50%);
    background: rgba(255,255,255,0.75); border-radius: 14px; padding: 8px 18px;
    text-align: center; pointer-events: none; box-shadow: 0 3px 10px rgba(0,0,0,0.12);
  }
  #hud h1 { margin: 0; font-size: 20px; color: #d1638a; }
  #hud p  { margin: 2px 0 0; font-size: 12px; color: #8a6a75; }
</style>
</head>
<body>
<div id="hud">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>drag to rotate &nbsp;•&nbsp; scroll to zoom</p>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
/* ============================================================
   LOW-POLY HAMSTER PLAYGROUND
   One file. Four chunky hamsters. One very spinny wheel.
   ============================================================ */

// ---------- Renderer / Scene / Camera ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe3ee);
scene.fog = new THREE.Fog(0xffe3ee, 26, 55);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);

// ---------- Simple custom orbit controls (drag + zoom) ----------
const orbit = { theta: 0.85, phi: 1.05, radius: 15, target: new THREE.Vector3(0, 1.3, 0) };
let dragging = false, px = 0, py = 0;

function updateCamera() {
  orbit.phi = Math.max(0.18, Math.min(1.45, orbit.phi));
  orbit.radius = Math.max(7, Math.min(30, orbit.radius));
  camera.position.set(
    orbit.target.x + orbit.radius * Math.sin(orbit.phi) * Math.sin(orbit.theta),
    orbit.target.y + orbit.radius * Math.cos(orbit.phi),
    orbit.target.z + orbit.radius * Math.sin(orbit.phi) * Math.cos(orbit.theta)
  );
  camera.lookAt(orbit.target);
}
renderer.domElement.addEventListener('pointerdown', e => { dragging = true; px = e.clientX; py = e.clientY; });
addEventListener('pointerup',   () => dragging = false);
addEventListener('pointermove', e => {
  if (!dragging) return;
  orbit.theta -= (e.clientX - px) * 0.006;
  orbit.phi   -= (e.clientY - py) * 0.005;
  px = e.clientX; py = e.clientY;
});
addEventListener('wheel', e => { orbit.radius *= (1 + Math.sign(e.deltaY) * 0.09); });
updateCamera();

// ---------- Lights ----------
scene.add(new THREE.HemisphereLight(0xfff5e8, 0xb8a0c8, 0.85));
const sun = new THREE.DirectionalLight(0xfff0d0, 0.9);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -10; sun.shadow.camera.right = 10;
sun.shadow.camera.top = 10;   sun.shadow.camera.bottom = -10;
scene.add(sun);

// ---------- Helpers ----------
const mat = (color) => new THREE.MeshLambertMaterial({ color, flatShading: true });
function mesh(geo, material, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, material);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}

// ---------- Floor & Cage ----------
const CAGE_HALF = 5.4;                       // hamster clamp limit
const cage = new THREE.Group();
scene.add(cage);

// wooden table
const table = mesh(new THREE.BoxGeometry(26, 0.6, 26), mat(0xc9a27a), 0, -0.35, 0);
cage.add(table);

// tray
const tray = mesh(new THREE.BoxGeometry(12.4, 0.5, 12.4), mat(0x8fd3f4), 0, 0.25, 0);
cage.add(tray);

// bedding (wood chips)
const chipMat = mat(0xf3e0b8);
for (let i = 0; i < 60; i++) {
  const s = 0.12 + Math.random() * 0.2;
  const chip = mesh(new THREE.BoxGeometry(s, 0.04, s * 1.7), chipMat,
    (Math.random() - 0.5) * 11, 0.52, (Math.random() - 0.5) * 11);
  chip.rotation.y = Math.random() * Math.PI;
  chip.castShadow = false;
  cage.add(chip);
}

// bars
const barMat = mat(0xff9ebb);
const barGeo = new THREE.CylinderGeometry(0.07, 0.07, 3.4, 5);
const WALL = 6;
for (let side = 0; side < 4; side++) {
  for (let i = 0; i < 11; i++) {
    const t = -5.7 + i * 1.14;
    const x = side === 0 ? t : side === 1 ? 5.7 : side === 2 ? t : -5.7;
    const z = side === 0 ? -5.7 : side === 1 ? t : side === 2 ? 5.7 : t;
    cage.add(mesh(barGeo, barMat, x, 2.2, z));
  }
}
// top frame
const frameMat = mat(0xff7ba9);
[[-5.7, 0], [5.7, 0], [0, -5.7], [0, 5.7]].forEach(([x, z]) => {
  const bar = mesh(new THREE.BoxGeometry(x === 0 ? 11.8 : 0.22, 0.22, z === 0 ? 11.8 : 0.22), frameMat, x, 3.95, z);
  cage.add(bar);
});

// ---------- Hamster Wheel (interactive object) ----------
const wheelGroup = new THREE.Group();          // spins
const wheelPivot = new THREE.Group();          // holds wheel at height
wheelPivot.position.set(3.2, 1.65, -3.4);
scene.add(wheelPivot);
wheelPivot.add(wheelGroup);

const wheelR = 1.15;
wheelGroup.add(mesh(new THREE.TorusGeometry(wheelR, 0.12, 5, 14), mat(0xffd166)));
wheelGroup.add(mesh(new THREE.CylinderGeometry(0.09, 0.09, 1.5, 6), mat(0xcc5577)).rotateZ(Math.PI / 2) && (() => {
  const a = mesh(new THREE.CylinderGeometry(0.09, 0.09, 1.5, 6), mat(0xcc5577));
  a.rotation.z = Math.PI / 2; return a;
})());
for (let i = 0; i < 6; i++) {                  // spokes
  const spoke = mesh(new THREE.BoxGeometry(0.07, wheelR * 2 - 0.2, 0.07), mat(0xffe9a8));
  spoke.rotation.z = i * Math.PI / 6;
  wheelGroup.add(spoke);
}
for (let i = 0; i < 10; i++) {                 // rungs
  const a = i / 10 * Math.PI * 2;
  const rung = mesh(new THREE.BoxGeometry(0.5, 0.06, 0.06), mat(0xcc5577),
    0, Math.cos(a) * (wheelR - 0.12), Math.sin(a) * (wheelR - 0.12));
  wheelGroup.add(rung);
}
// stand
const standMat = mat(0x9b5de5);
[-0.85, 0.85].forEach(z => {
  const leg = mesh(new THREE.BoxGeometry(0.18, 1.9, 0.18), standMat, 0.55, -0.75, z);
  leg.rotation.z = -0.28;
  wheelPivot.add(leg);
  const foot = mesh(new THREE.BoxGeometry(0.3, 0.15, 0.3), standMat, 0.15, -1.65, z);
  wheelPivot.add(foot);
});

// ---------- Food Bowl ----------
const bowl = new THREE.Group();
bowl.position.set(-3.4, 0.5, 2.8);
scene.add(bowl);
bowl.add(mesh(new THREE.CylinderGeometry(0.85, 0.6, 0.45, 8), mat(0xef476f)));
bowl.add(mesh(new THREE.CylinderGeometry(0.65, 0.5, 0.2, 8), mat(0xffd166), 0, 0.16, 0));
const pelletMat = mat(0xd48c4f);
for (let i = 0; i < 8; i++) {
  const a = Math.random() * Math.PI * 2, r = Math.random() * 0.45;
  bowl.add(mesh(new THREE.IcosahedronGeometry(0.13, 0), pelletMat, Math.cos(a) * r, 0.32, Math.sin(a) * r));
}
const BOWL_POINT = new THREE.Vector3(-3.4, 0.5, 2.8);

// ---------- Cardboard Tunnel (decor + hangout spot) ----------
const tunnel = new THREE.Group();
tunnel.position.set(-1.5, 0.95, -3.6);
scene.add(tunnel);
const tube = mesh(new THREE.CylinderGeometry(0.85, 0.85, 3.4, 9, 1, true), mat(0xd9a066));
tube.rotation.z = Math.PI / 2;
tube.material.side = THREE.DoubleSide;
tunnel.add(tube);
tunnel.add(mesh(new THREE.TorusGeometry(0.85, 0.07, 4, 9), mat(0xb9805a), -1.7, 0, 0).rotateY(Math.PI / 2) || (() => {
  const t = mesh(new THREE.TorusGeometry(0.85, 0.07, 4, 9), mat(0xb9805a), -1.7, 0, 0);
  t.rotation.y = Math.PI / 2; return t;
})());
const TUNNEL_POINT = new THREE.Vector3(-1.5, 0.5, -1.9);

// ---------- Hamsters ----------
const WHEEL_IN = new THREE.Vector3(3.2, 0.5, -3.4);   // entry point in front of wheel

function makeHamster(color) {
  const g = new THREE.Group();
  const bodyMat = mat(color);
  const bellyMat = mat(0xfff5e6);

  const body = mesh(new THREE.IcosahedronGeometry(0.45, 1), bodyMat);
  body.scale.set(1.25, 0.95, 0.9);
  body.position.y = 0.48;
  g.add(body);

  const belly = mesh(new THREE.IcosahedronGeometry(0.36, 1), bellyMat);
  belly.scale.set(1.1, 0.8, 0.75);
  belly.position.set(0.08, 0.38, 0);
  g.add(belly);

  const head = new THREE.Group();
  head.position.set(0.55, 0.62, 0);
  g.add(head);
  head.add(mesh(new THREE.IcosahedronGeometry(0.28, 1), bodyMat));
  // ears
  [-1, 1].forEach(s => {
    head.add(mesh(new THREE.ConeGeometry(0.1, 0.16, 5), bodyMat, -0.05, 0.26, s * 0.17));
    head.add(mesh(new THREE.SphereGeometry(0.055, 4, 4), mat(0xffb3c6), -0.03, 0.25, s * 0.17));
  });
  // snout + nose
  head.add(mesh(new THREE.ConeGeometry(0.1, 0.16, 5), bellyMat, 0.28, -0.02, 0).rotateZ ? (() => { const c = mesh(new THREE.ConeGeometry(0.1, 0.16, 5), bellyMat, 0.28, -0.02, 0); c.rotation.z = -Math.PI / 2; return c; })() : null);
  head.add(mesh(new THREE.SphereGeometry(0.045, 4, 4), mat(0xff7ba9), 0.36, -0.02, 0));
  // cheeks
  const cheekL = mesh(new THREE.IcosahedronGeometry(0.11, 0), mat(0xffd9a0), 0.16, -0.05, 0.18);
  const cheekR = cheekL.clone(); cheekR.position.z = -0.18;
  head.add(cheekL, cheekR);
  // eyes
  [-1, 1].forEach(s => head.add(mesh(new THREE.SphereGeometry(0.05, 5, 5), mat(0x2b2b2b), 0.16, 0.08, s * 0.16)));

  // stubby legs
  const legs = [];
  const legMat = mat(color === 0xf5e6c8 ? 0xe0cba8 : color);
  [[0.28, 0.3], [0.28, -0.3], [-0.28, 0.3], [-0.28, -0.3]].forEach(([x, z]) => {
    const leg = mesh(new THREE.CylinderGeometry(0.07, 0.09, 0.22, 5), legMat, x, 0.12, z);
    g.add(leg); legs.push(leg);
  });

  // nub tail
  const tail = mesh(new THREE.ConeGeometry(0.07, 0.15, 4), bodyMat, -0.58, 0.5, 0);
  tail.rotation.z = Math.PI / 2 + 0.5;
  g.add(tail);

  scene.add(g);
  return { group: g, head, legs, tail, cheekL, cheekR, body };
}

const COLORS = [0xf6c98f, 0xd9a066, 0xf5e6c8, 0xb9805a];
const hamsters = COLORS.map((c, i) => {
  const h = makeHamster(c);
  h.group.position.set(Math.cos(i * 1.7) * 2.5, 0.5, Math.sin(i * 1.7) * 2.5);
  h.heading = Math.random() * Math.PI * 2;
  h.state = 'idle';
  h.timer = Math.random() * 2;
  h.target = new THREE.Vector3();
  h.speed = 1.1 + Math.random() * 0.5;
  h.phase = Math.random() * 10;
  return h;
});
let wheelUser = null;

// ---------- Behavior ----------
function pickNextAction(h) {
  const roll = Math.random();
  if (roll < 0.3 && !wheelUser) {
    h.state = 'toWheel'; wheelUser = h;
    h.target.copy(WHEEL_IN);
  } else if (roll < 0.6) {
    h.state = 'toFood';
    h.target.copy(BOWL_POINT);
  } else if (roll < 0.75) {
    h.state = 'wander';
    h.target.set((Math.random() - 0.5) * 9, 0.5, (Math.random() - 0.5) * 9);
  } else {
    h.state = 'wander';
    h.target.copy(TUNNEL_POINT).add(new THREE.Vector3((Math.random() - 0.5) * 2, 0, (Math.random() - 0.5) * 2));
  }
}

function steerTowards(h, dt) {
  const p = h.group.position;
  const dx = h.target.x - p.x, dz = h.target.z - p.z;
  const desired = Math.atan2(-dz, dx);   // heading 0 = +x
  let diff = desired - h.heading;
  while (diff > Math.PI) diff -= Math.PI * 2;
  while (diff < -Math.PI) diff += Math.PI * 2;
  h.heading += diff * Math.min(1, dt * 6);
  p.x += Math.cos(h.heading) * h.speed * dt;
  p.z += Math.sin(-h.heading) * h.speed * dt;
  p.x = Math.max(-CAGE_HALF + 0.4, Math.min(CAGE_HALF - 0.4, p.x));
  p.z = Math.max(-CAGE_HALF + 0.4, Math.min(CAGE_HALF - 0.4, p.z));
  return Math.hypot(dx, dz);
}

function updateHamster(h, dt, t) {
  const p = h.group.position;
  h.timer -= dt;
  let legSpeed = 0, bob = 0;

  switch (h.state) {
    case 'idle':
      if (h.timer <= 0) pickNextAction(h);
      break;

    case 'wander':
      legSpeed = 9;
      if (steerTowards(h, dt) < 0.35) { h.state = 'idle'; h.timer = 1 + Math.random() * 2.5; }
      break;

    case 'toWheel':
      legSpeed = 11;
      if (steerTowards(h, dt) < 0.35) { h.state = 'run'; h.timer = 4 + Math.random() * 5; }
      break;

    case 'run': {
      // sit inside the wheel, wheel spins under us
      p.set(wheelPivot.position.x, wheelPivot.position.y - wheelR + 0.55, wheelPivot.position.z);
      h.heading = 0;
      legSpeed = 26;
      wheelGroup.rotation.z -= dt * 5.5;
      if (h.timer <= 0) {
        wheelUser = null;
        h.state = 'idle';
        h.timer = 0.8;
        p.z += 1.6; p.y = 0.5;   // tumble out the bottom, cute
        h.heading = Math.PI;
      }
      break;
    }

    case 'toFood':
      legSpeed = 10;
      if (steerTowards(h, dt) < 0.9) { h.state = 'eat'; h.timer = 2.5 + Math.random() * 2; }
      break;

    case 'eat': {
      legSpeed = 2;
      // munching: head bobs, cheeks puff
      h.head.position.y = 0.62 + Math.sin(t * 14) * 0.05;
      const puff = 1 + Math.max(0, Math.sin(t * 7)) * 0.45;
      h.cheekL.scale.setScalar(puff);
      h.cheekR.scale.setScalar(puff);
      if (h.timer <= 0) {
        h.head.position.y = 0.62;
        h.cheekL.scale.setScalar(1); h.cheekR.scale.setScalar(1);
        h.state = 'idle'; h.timer = 1 + Math.random() * 2;
      }
      break;
    }
  }

  // apply pose
  h.group.rotation.y = h.heading;
  if (legSpeed > 0) {
    bob = Math.abs(Math.sin(t * legSpeed * 0.6)) * 0.05;
    h.legs.forEach((leg, i) => leg.rotation.x = Math.sin(t * legSpeed + (i % 2) * Math.PI + (i < 2 ? 0 : Math.PI)) * 0.7);
    h.tail.rotation.y = Math.sin(t * 6) * 0.3;
  } else {
    h.legs.forEach(l => l.rotation.x *= 0.85);
    bob = Math.sin(t * 2 + h.phase) * 0.012;   // breathing
  }
  p.y = (h.state === 'run' ? wheelPivot.position.y - wheelR + 0.55 : 0.5) + bob;
}

// gentle "polite hamsters" separation
function separate() {
  for (let i = 0; i < hamsters.length; i++)
    for (let j = i + 1; j < hamsters.length; j++) {
      const a = hamsters[i].group.position, b = hamsters[j].group.position;
      const dx = b.x - a.x, dz = b.z - a.z;
      const d = Math.hypot(dx, dz);
      if (d > 0.001 && d < 0.85) {
        const push = (0.85 - d) * 0.5;
        a.x -= dx / d * push; a.z -= dz / d * push;
        b.x += dx / d * push; b.z += dz / d * push;
      }
    }
}

// ---------- Animate ----------
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  for (const h of hamsters) updateHamster(h, dt, t);
  separate();

  // idle wheel drift
  if (!wheelUser) wheelGroup.rotation.z *= 0.995;

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

- **The cage** — pastel pink bars on a blue tray, sitting on a wooden table scattered with wood-chip bedding.
- **4 chunky hamsters** — built from low-poly icosahedrons and cones, each a different color, with ears, pink noses, tiny eyes, stubby legs, and a nub tail.
- **Autonomous behavior** — each hamster runs a small state machine: wander → pause → visit the food bowl → munch (cheeks puff out!) → scamper to the wheel → sprint (wheel spins fast) → tumble out the bottom and repeat.
- **Interactive wheel** — only one hamster can use it at a time; the wheel physically spins while running and slowly drifts when idle.
- **Extras** — food bowl with pellets, a cardboard tunnel hangout spot, soft shadows, breathing animation when idle, and gentle collision so hamsters don't overlap.
- **Camera** — lightweight custom orbit controls (drag to rotate, scroll to zoom) so the page has no dependencies beyond the single Three.js script.