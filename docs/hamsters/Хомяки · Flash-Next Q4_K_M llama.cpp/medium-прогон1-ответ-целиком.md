# Low-Poly Hamster Playground 🐹

Here's the complete single-file project. Save it as `index.html` and open it in any modern browser — no build step needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #ffe9f2; }
  canvas { display: block; }
  #hud {
    position: fixed; top: 14px; left: 16px; z-index: 5;
    font-family: "Comic Sans MS", "Segoe UI", sans-serif;
    color: #7a4a2b; pointer-events: none; user-select: none;
  }
  #hud h1 { margin: 0; font-size: 22px; text-shadow: 0 1px 0 #fff; }
  #hud p  { margin: 2px 0 0; font-size: 13px; opacity: .85; }
  #hint {
    position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%);
    font-family: "Segoe UI", sans-serif; font-size: 13px; color: #a06b45;
    background: rgba(255,255,255,.65); padding: 5px 14px; border-radius: 20px;
    pointer-events: none; user-select: none;
  }
</style>
<script type="importmap">
  { "imports": { "three": "https://unpkg.com/three@0.158.0/build/three.module.js" } }
</script>
</head>
<body>

<div id="hud">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>They wander, snack, and sprint on the wheel…</p>
</div>
<div id="hint">drag to rotate &nbsp;•&nbsp; scroll to zoom</div>

<script type="module">
import * as THREE from 'three';

/* ---------------- renderer / scene / camera ---------------- */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe9f2);
scene.fusion = scene.fog = new THREE.Fog(0xffe9f2, 22, 45);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);

/* simple custom orbit camera */
const cam = { theta: 0.7, phi: 1.05, radius: 13, target: new THREE.Vector3(0, 1.2, 0) };
function updateCamera() {
  cam.phi = THREE.MathUtils.clamp(cam.phi, 0.35, 1.45);
  cam.radius = THREE.MathUtils.clamp(cam.radius, 6, 26);
  camera.position.set(
    cam.target.x + cam.radius * Math.sin(cam.phi) * Math.sin(cam.theta),
    cam.target.y + cam.radius * Math.cos(cam.phi),
    cam.target.z + cam.radius * Math.sin(cam.phi) * Math.cos(cam.theta)
  );
  camera.lookAt(cam.target);
}
updateCamera();

let dragging = false, px = 0, py = 0;
addEventListener('pointerdown', e => { dragging = true; px = e.clientX; py = e.clientY; });
addEventListener('pointerup',   () => dragging = false);
addEventListener('pointermove', e => {
  if (!dragging) return;
  cam.theta -= (e.clientX - px) * 0.006;
  cam.phi   -= (e.clientY - py) * 0.005;
  px = e.clientX; py = e.clientY;
  updateCamera();
});
addEventListener('wheel', e => { cam.radius += e.deltaY * 0.01; updateCamera(); }, { passive: true });

/* ---------------- lights ---------------- */
scene.add(new THREE.HemisphereLight(0xfff6ea, 0xd8b7c9, 1.0));
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.position.set(6, 12, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = sun.shadow.camera.bottom = -9;
sun.shadow.camera.right = sun.shadow.camera.top = 9;
scene.add(sun);

/* ---------------- helpers ---------------- */
const mat = (color, rough = 0.85) => new THREE.MeshStandardMaterial({ color, roughness: rough, flatShading: true });
function box(w, h, d, m, x = 0, y = 0, z = 0) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m);
  mesh.position.set(x, y, z); mesh.castShadow = true; return mesh;
}

/* ---------------- room + cage ---------------- */
const FLOOR_Y = 0;
const floor = new THREE.Mesh(new THREE.BoxGeometry(40, 0.5, 40), mat(0xf3d9e5));
floor.position.y = -0.25; floor.receiveShadow = true;
scene.add(floor);

const TRAY_W = 10, TRAY_D = 6, WALL = 0.6, BED_Y = 0.75;   // bedding top height
const tray = mat(0x63c7ba);
scene.add(box(TRAY_W, 0.75, WALL, tray, 0, 0.375, -3);      // back wall (and 3 more)
scene.add(box(TRAY_W, 0.75, WALL, tray, 0, 0.375,  3);
scene.add(box(WALL, 0.75, TRAY_D, tray, -5, 0.375, 0);
scene.add(box(WALL, 0.75, TRAY_D, tray,  5, 0.375, 0);

const bedding = box(TRAY_W - WALL, 0.4, TRAY_D - WALL, mat(0xe8cf9a), 0, 0.55, 0);
bedding.receiveShadow = true;
scene.add(bedding);

/* cage bars */
const barMat = mat(0x9fb8d8);
for (let i = 0; i <= 10; i++) {
  const x = -4.7 + i * 0.94;
  scene.add(box(0.12, 2.6, 0.12, barMat, x, 0.75 + 1.3, -2.75));
  scene.add(box(0.12, 2.6, 0.12, barMat, x, 0.75 + 1.3,  2.75));
}
for (let i = 0; i <= 6; i++) {
  const z = -2.6 + i * 0.87;
  scene.add(box(0.12, 2.6, 0.12, barMat, -4.75, 0.75 + 1.3, z));
  scene.add(box(0.12, 2.6, 0.12, barMat,  4.75, 0.75 + 1.3, z));
}
// top rails
scene.add(box(TRAY_W, 0.22, 0.22, barMat, 0, 3.4, -2.75));
scene.add(box(TRAY_W, 0.22, 0.22, barMat, 0, 3.4,  2.75));
scene.add(box(0.22, 0.22, TRAY_D, barMat, -4.75, 3.4, 0));
scene.add(box(0.22, 0.22, TRAY_D, barMat,  4.75, 3.4, 0));

/* ---------------- the wheel (interactive!) ---------------- */
const WHEEL = new THREE.Vector3(-3.4, BED_Y + 1.05, 0);
const wheel = new THREE.Group();
wheel.position.copy(WHEEL);
const wheelMat = mat(0xff8fae);
const ring = new THREE.Mesh(new THREE.TorusGeometry(0.95, 0.18, 5, 10), wheelMat);
ring.castShadow = true;
wheel.add(ring);
for (let i = 0; i < 3; i++) {
  const spoke = box(1.75, 0.08, 0.08, wheelMat);
  spoke.rotation.z = i * Math.PI / 3;
  wheel.add(spoke);
}
const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.3, 6), mat(0xffd166));
hub.rotation.x = Math.PI / 2;
wheel.add(hub);
scene.add(wheel);
// stand
scene.add(box(0.3, 1.9, 0.3, mat(0xffd166), -4.4, BED_Y + 0.35, 0));

/* ---------------- food bowl ---------------- */
const BOWL = new THREE.Vector3(3.3, BED_Y, 1.1);
const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.45, 0.4, 7), mat(0xffb347));
bowl.position.set(BOWL.x, BED_Y - 0.1, BOWL.z); bowl.castShadow = true;
scene.add(bowl);
const pellets = [];
for (let i = 0; i < 6; i++) {
  const p = new THREE.Mesh(new THREE.IcosahedronGeometry(0.11, 0), mat(0xa5682b));
  p.position.set(BOWL.x + (Math.random() - .5) * .6, BED_Y + 0.12, BOWL.z + (Math.random() - .5) * .6);
  p.castShadow = true; scene.add(p); pellets.push(p);
}

/* ---------------- tunnel + ball (decor) ---------------- */
const tunnel = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 1.3, 7, 1, true), mat(0xb892e8));
tunnel.rotation.x = Math.PI / 2; tunnel.rotation.z = 0.4;
tunnel.position.set(1.2, BED_Y - 0.05, -1.7); tunnel.castShadow = true;
scene.add(tunnel);

const ball = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 0), mat(0xff6b6b));
ball.position.set(1.8, BED_Y + 0.4, 1.4); ball.castShadow = true;
scene.add(ball);

/* ---------------- hamsters ---------------- */
function angleLerp(a, b, t) {
  let d = (b - a) % (Math.PI * 2);
  if (d >  Math.PI) d -= Math.PI * 2;
  if (d < -Math.PI) d += Math.PI * 2;
  return a + d * Math.min(1, t);
}
const rand = (a, b) => a + Math.random() * (b - a);

let wheelBusy = null, bowlBusy = null;

class Hamster {
  constructor(color, name) {
    this.name = name;
    this.state = 'idle';
    this.timer = rand(0.5, 2);
    this.speed = rand(1.0, 1.5);
    this.yaw = rand(0, Math.PI * 2);
    this.target = new THREE.Vector3();
    this.action = 'wander';

    const g = new THREE.Group();
    const fur = mat(color);
    const cream = mat(0xfff2df);
    g.add(box(0.48, 0.42, 0.66, fur, 0, 0.26, 0));            // body
    const head = box(0.38, 0.34, 0.34, fur, 0, 0.42, 0.36);   // head
    g.add(head); this.head = head;
    g.add(box(0.12, 0.05, 0.1, cream, 0, 0.4, 0.54));         // snout
    g.add(box(0.09, 0.09, 0.05, mat(0x222222), -0.1, 0.47, 0.53)); // eyes
    g.add(box(0.09, 0.09, 0.05, mat(0x222222),  0.1, 0.47, 0.53));
    g.add(box(0.1, 0.14, 0.07, mat(0xffb0c4), -0.14, 0.63, 0.26)); // ears
    g.add(box(0.1, 0.14, 0.07, mat(0xffb0c4),  0.14, 0.63, 0.26));
    g.add(box(0.1, 0.1, 0.2, fur, 0, 0.3, -0.4));             // nub tail
    this.legs = [];
    const lp = [[-0.16, 0.34], [0.16, 0.34], [-0.16, -0.2], [0.16, -0.2]];
    for (const [x, z] of lp) {
      const leg = box(0.13, 0.18, 0.13, cream, x, 0.09, z);
      g.add(leg); this.legs.push(leg);
    }
    g.children.forEach(c => c.castShadow = true);
    this.group = g;
    this.group.position.set(rand(-3, 3), BED_Y, rand(-1.8, 1.8));
    scene.add(g);
    this.pickAction();
  }

  pickAction() {
    this.state = 'idle';
    this.timer = rand(0.4, 1.6);
    const r = Math.random();
    if (r < 0.2 && !wheelBusy)      { this.action = 'wheel'; this.target.copy(WHEEL).setY(BED_Y).add(new THREE.Vector3(0.9, 0, 0)); wheelBusy = this; }
    else if (r < 0.4 && !bowlBusy)  { this.action = 'bowl';  this.target.copy(BOWL).add(new THREE.Vector3(0.8, 0, 0.8)); bowlBusy = this; }
    else                            { this.action = 'wander'; this.target.set(rand(-4, 4), BED_Y, rand(-2.1, 2.1)); }
    this.walkTarget = this.target.clone();
  }

  free() { if (wheelBusy === this) wheelBusy = null; if (bowlBusy === this) bowlBusy = null; }

  update(dt, t) {
    const g = this.group;

    if (this.state === 'idle') {
      this.timer -= dt;
      this.legs.forEach(l => l.rotation.x *= 0.9);
      this.head.rotation.x = Math.sin(t * 2 + this.yaw) * 0.05;
      if (this.timer <= 0) { this.free(); this.state = 'walk'; this.walkTarget.copy(this.target); }
    }
    else if (this.state === 'walk') {
      const to = this.walkTarget.clone().sub(g.position); to.y = 0;
      const dist = to.length();
      if (dist < 0.12) { this.state = 'act'; this.timer = rand(1.5, 3.5); }
      else {
        const yaw = Math.atan2(to.x, to.z);
        this.yaw = angleLerp(this.yaw, yaw, dt * 6);
        g.rotation.y = this.yaw;
        g.position.addScaledVector(to.normalize(), this.speed * dt);
        g.position.y = BED_Y + Math.abs(Math.sin(t * 9 + this.yaw * 3)) * 0.05;   // hoppy waddle
        this.legs.forEach((l, i) => l.rotation.x = Math.sin(t * 16 + i * Math.PI) * 0.7);
      }
    }
    else if (this.state === 'act') {
      this.timer -= dt;
      if (this.action === 'wheel') {
        // teleport into wheel and run!
        g.position.lerp(new THREE.Vector3(WHEEL.x, BED_Y, WHEEL.z), dt * 6);
        g.rotation.y = angleLerp(g.rotation.y, -Math.PI / 2, dt * 8);
        this.legs.forEach((l, i) => l.rotation.x = Math.sin(t * 26 + i * Math.PI) * 0.9);
      } else if (this.action === 'bowl') {
        this.head.rotation.x = Math.sin(t * 18) * 0.22;                             // nom-nom bob
        pellets.forEach((p, i) => p.scale.setScalar(1 + Math.sin(t * 10 + i) * 0.25));
        this.legs.forEach(l => l.rotation.x *= 0.85);
      } else {
        this.head.rotation.y = Math.sin(t * 3) * 0.35;                              // sniffy head tilt
        this.legs.forEach(l => l.rotation.x *= 0.85);
      }
      if (this.timer <= 0) { this.free(); this.pickAction(); }
    }
  }
}

const hamsters = [
  new Hamster(0xe8a951, 'Nugget'),
  new Hamster(0x8a5a33, 'Beans'),
  new Hamster(0xf5f0e8, 'Snowpuff'),
  new Hamster(0x9aa7b5, 'Gizmo'),
];

/* ---------------- main loop ---------------- */
const clock = new THREE.Clock();
let wheelSpin = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  for (const h of hamsters) h.update(dt, t);

  // wheel spins only when a hamster is running in it (ramps up!)
  const runner = wheelBusy && wheelBusy.state === 'act' && wheelBusy.action === 'wheel';
  wheelSpin = THREE.MathUtils.lerp(wheelSpin, runner ? 14 : 0, dt * 3);
  wheel.rotation.x += wheelSpin * dt;

  ball.rotation.y += dt * 0.4;
  ball.rotation.x += dt * 0.2;

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

**Scene** — A pastel room with a teal cage tray, sandy bedding, low-poly cage bars with top rails, a pink running wheel on a yellow stand, a snack bowl full of pellets, a purple tunnel, and a wobbly ball.

**Hamsters** — Four boxy, cream-pawed cuties, each with a tiny state machine:
- 🚶 **Wander** — waddle to a random spot with a hoppy bob and scissoring legs
- 😴 **Idle** — pause and head-tilt sniffing
- 🎡 **Wheel** — climb in and sprint (the wheel ramps up its spin only while occupied!)
- 🍜 **Bowl** — nom-nom head bobbing while the pellets pulse

The wheel and bowl are single-occupancy — hamsters reroute to wandering if a spot is taken.

**Controls** — Drag to orbit, scroll to zoom, all with a tiny hand-rolled orbit camera (no extra imports). Just Three.js core from a CDN via import map. 🐹