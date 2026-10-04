

# 🐹 Low-Poly Hamster Playground

Here's the complete single-file project. Save it as `index.html` and open in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; background: #2d1b69; font-family: 'Segoe UI', sans-serif; }
  canvas { display: block; }
  #info {
    position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
    color: #fff; background: rgba(45,27,105,0.7); padding: 12px 24px;
    border-radius: 12px; font-size: 14px; text-align: center;
    backdrop-filter: blur(10px); pointer-events: none;
  }
  #info h1 { font-size: 18px; margin-bottom: 4px; }
</style>
</head>
<body>
<div id="info">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  Drag to rotate &bull; Scroll to zoom
</div>

<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ───────── Scene ───────── */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2d1b69);
scene.fog = new THREE.Fog(0x2d1b69, 15, 30);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(6, 5, 8);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1, 0);
controls.maxPolarAngle = Math.PI * 0.48;
controls.minDistance = 4;
controls.maxDistance = 18;

/* ───────── Lights ───────── */
scene.add(new THREE.AmbientLight(0x8877bb, 0.6));

const sun = new THREE.DirectionalLight(0xffeedd, 1.2);
sun.position.set(5, 10, 7);
sun.castShadow = true;
Object.assign(sun.shadow.camera, { left:-6, right:6, top:6, bottom:-6, near:1, far:25 });
sun.shadow.mapSize.set(1024, 1024);
scene.add(sun);

const lamp = new THREE.PointLight(0xffaa44, 0.5, 10);
lamp.position.set(-2, 3, -2);
scene.add(lamp);

/* ───────── Helpers ───────── */
const M = (c, o = {}) => new THREE.MeshStandardMaterial({
  color: c, roughness: o.r ?? 0.7, metalness: o.m ?? 0.05, ...o
});

/* ───────── Cage ───────── */
function makeCage() {
  const g = new THREE.Group();

  // tray
  const tray = new THREE.Mesh(new THREE.BoxGeometry(6, 0.3, 4), M(0xf5deb3, { r: 0.9 }));
  tray.position.y = -0.15;
  tray.receiveShadow = true;
  g.add(tray);

  // bedding
  const bc = [0xf0c8a0, 0xe8c090, 0xd8b888, 0xf5d8b8];
  for (let i = 0; i < 80; i++) {
    const s = 0.08 + Math.random() * 0.12;
    const b = new THREE.Mesh(new THREE.BoxGeometry(s, s * 0.4, s), M(bc[i % 4]));
    b.position.set((Math.random() - .5) * 5.5, 0.02, (Math.random() - .5) * 3.5);
    b.rotation.y = Math.random() * Math.PI;
    b.receiveShadow = true;
    g.add(b);
  }

  // back wall (translucent)
  const wm = new THREE.MeshStandardMaterial({ color: 0xcccccc, transparent: true, opacity: 0.12, side: THREE.DoubleSide });
  const bw = new THREE.Mesh(new THREE.PlaneGeometry(6, 2.5), wm);
  bw.position.set(0, 1.25, -2);
  g.add(bw);

  // wire grid
  const lm = new THREE.LineBasicMaterial({ color: 0xbbbbbb, transparent: true, opacity: 0.35 });
  for (let y = 0; y <= 2.5; y += 0.35)
    g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-3, y, -1.99), new THREE.Vector3(3, y, -1.99)]), lm));
  for (let x = -3; x <= 3; x += 0.35)
    g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(x, 0, -1.99), new THREE.Vector3(x, 2.5, -1.99)]), lm));

  // frame posts
  const fm = M(0x888888, { m: 0.4, r: 0.4 });
  const pg = new THREE.CylinderGeometry(0.05, 0.05, 2.5, 6);
  [[-3,-2],[3,-2],[-3,2],[3,2]].forEach(([x,z]) => {
    const p = new THREE.Mesh(pg, fm);
    p.position.set(x, 1.25, z);
    p.castShadow = true;
    g.add(p);
  });

  // top rails
  const rg = new THREE.CylinderGeometry(0.04, 0.04, 6, 6);
  const r1 = new THREE.Mesh(rg, fm); r1.rotation.z = Math.PI/2; r1.position.set(0,2.5,-2); g.add(r1);
  const r2 = new THREE.Mesh(rg, fm); r2.rotation.z = Math.PI/2; r2.position.set(0,2.5,2); g.add(r2);
  const sg = new THREE.CylinderGeometry(0.04, 0.04, 4, 6);
  const s1 = new THREE.Mesh(sg, fm); s1.rotation.x = Math.PI/2; s1.position.set(-3,2.5,0); g.add(s1);
  const s2 = new THREE.Mesh(sg, fm); s2.rotation.x = Math.PI/2; s2.position.set(3,2.5,0); g.add(s2);

  return g;
}

/* ───────── Wheel ───────── */
function makeWheel() {
  const g = new THREE.Group();
  const wm = M(0x44cc88, { r: 0.5 });
  const sm = M(0x33aa77);

  g.add(new THREE.Mesh(new THREE.TorusGeometry(0.7, 0.06, 6, 12), wm)).castShadow = true;

  const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.15, 6), sm);
  hub.rotation.x = Math.PI / 2;
  g.add(hub);

  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2;
    const sp = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.6, 4), sm);
    sp.position.set(Math.cos(a) * 0.35, Math.sin(a) * 0.35, 0);
    sp.lookAt(0, 0, 0);
    sp.rotateX(Math.PI / 2);
    g.add(sp);
  }

  // stand
  const st = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 0.5, 6), M(0x666666, { m: 0.3 }));
  st.position.y = -0.95;
  st.castShadow = true;
  g.add(st);
  const bs = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.3, 0.08, 8), M(0x666666, { m: 0.3 }));
  bs.position.y = -1.22;
  g.add(bs);

  g.position.set(2, 1.2, -1.2);
  return g;
}

/* ───────── Food Bowl ───────── */
function makeBowl() {
  const g = new THREE.Group();
  g.add(new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.2, 0.15, 8), M(0xff6688, { r: 0.4 }))).castShadow = true;
  const pm = M(0xddaa44, { r: 0.8 });
  for (let i = 0; i < 8; i++) {
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.04, 4, 3), pm);
    p.position.set((Math.random()-.5)*.25, .08, (Math.random()-.5)*.25);
    g.add(p);
  }
  g.position.set(-1.5, 0.08, 1);
  return g;
}

/* ───────── Tunnel ───────── */
function makeTunnel() {
  const g = new THREE.Group();
  const tm = M(0x66bbff, { r: 0.5, side: THREE.DoubleSide });
  const t = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 1.2, 8, 1, false, 0, Math.PI), tm);
  t.rotation.z = Math.PI / 2;
  t.rotation.y = Math.PI / 2;
  t.position.y = 0.35;
  t.castShadow = true;
  g.add(t);
  const cg = new THREE.CircleGeometry(0.35, 8, 0, Math.PI);
  const c1 = new THREE.Mesh(cg, tm); c1.position.set(0.6, 0.35, 0); c1.rotation.y = Math.PI/2; g.add(c1);
  const c2 = new THREE.Mesh(cg, tm); c2.position.set(-0.6, 0.35, 0); c2.rotation.y = -Math.PI/2; g.add(c2);
  g.position.set(-1, 0, -0.5);
  g.rotation.y = 0.4;
  return g;
}

/* ───────── Hamster ───────── */
function makeHamster(bodyC, accC) {
  const g = new THREE.Group();
  const bm = M(bodyC, { r: 0.8 });
  const am = M(accC, { r: 0.8 });
  const em = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.3 });
  const nm = new THREE.MeshStandardMaterial({ color: 0xff6688, roughness: 0.5 });
  const hm = new THREE.MeshBasicMaterial({ color: 0xffffff });

  // body
  const body = new THREE.Mesh(new THREE.DodecahedronGeometry(0.28), bm);
  body.scale.set(1, 0.75, 1.1);
  body.position.y = 0.28;
  body.castShadow = true;
  g.add(body);

  // head
  const head = new THREE.Mesh(new THREE.DodecahedronGeometry(0.18), bm);
  head.scale.set(1, 0.9, 0.95);
  head.position.set(0, 0.38, 0.22);
  head.castShadow = true;
  g.add(head);

  // cheeks
  const ckg = new THREE.SphereGeometry(0.08, 5, 4);
  const cl = new THREE.Mesh(ckg, am); cl.position.set(-0.12, 0.32, 0.32); g.add(cl);
  const cr = new THREE.Mesh(ckg, am); cr.position.set(0.12, 0.32, 0.32); g.add(cr);

  // eyes
  const eg = new THREE.SphereGeometry(0.035, 5, 4);
  const el = new THREE.Mesh(eg, em); el.position.set(-0.08, 0.4, 0.36); g.add(el);
  const er = new THREE.Mesh(eg, em); er.position.set(0.08, 0.4, 0.36); g.add(er);

  // eye highlights
  const hg = new THREE.SphereGeometry(0.012, 4, 3);
  const hl = new THREE.Mesh(hg, hm); hl.position.set(-0.07, 0.41, 0.39); g.add(hl);
  const hr = new THREE.Mesh(hg, hm); hr.position.set(0.09, 0.41, 0.39); g.add(hr);

  // nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.025, 4, 3), nm);
  nose.position.set(0, 0.36, 0.4);
  g.add(nose);

  // ears
  const ekg = new THREE.ConeGeometry(0.06, 0.08, 4);
  const eal = new THREE.Mesh(ekg, bm); eal.position.set(-0.1, 0.52, 0.2); eal.rotation.z = 0.3; g.add(eal);
  const ear = new THREE.Mesh(ekg, bm); ear.position.set(0.1, 0.52, 0.2); ear.rotation.z = -0.3; g.add(ear);

  // inner ears
  const ig = new THREE.ConeGeometry(0.035, 0.05, 4);
  const il = new THREE.Mesh(ig, am); il.position.set(-0.1, 0.51, 0.22); il.rotation.z = 0.3; g.add(il);
  const ir = new THREE.Mesh(ig, am); ir.position.set(0.1, 0.51, 0.22); ir.rotation.z = -0.3; g.add(ir);

  // feet
  const fg = new THREE.SphereGeometry(0.04, 4, 3);
  [[-0.1,0.04,0.15],[0.1,0.04,0.15],[-0.1,0.04,-0.15],[0.1,0.04,-0.15]].forEach(([x,y,z]) => {
    const f = new THREE.Mesh(fg, am);
    f.position.set(x, y, z);
    f.scale.set(1, 0.6, 1.2);
    g.add(f);
  });

  // tail
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.03, 0.08, 4), bm);
  tail.position.set(0, 0.25, -0.3);
  tail.rotation.x = -Math.PI / 2;
  g.add(tail);

  return g;
}

/* ───────── Build Scene ───────── */
scene.add(makeCage());
const wheel = makeWheel();
scene.add(wheel);
const bowl = makeBowl();
scene.add(bowl);
const tunnel = makeTunnel();
scene.add(tunnel);

// outer ground
const gnd = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), M(0x3d2b7a, { r: 1 }));
gnd.rotation.x = -Math.PI / 2;
gnd.position.y = -0.3;
gnd.receiveShadow = true;
scene.add(gnd);

// trees
function tree(x, z, s = 1) {
  const g = new THREE.Group();
  const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.08*s, 0.12*s, 0.6*s, 5), M(0x8B6914));
  tr.position.y = 0.3*s;
  tr.castShadow = true;
  g.add(tr);
  const lf = new THREE.Mesh(new THREE.IcosahedronGeometry(0.35*s), M(0x44aa44, { r: 0.9 }));
  lf.position.y = 0.75*s;
  lf.castShadow = true;
  g.add(lf);
  g.position.set(x, -0.3, z);
  return g;
}
scene.add(tree(-5, -3, 1.2));
scene.add(tree(5, 2, 0.9));
scene.add(tree(4, -4, 1.1));
scene.add(tree(-4, 4, 0.8));

// rocks
[[−3,3,1],[3,3,.7],[5,−1,.9]].forEach(([x,z,s]) => {
  const r = new THREE.Mesh(new THREE.DodecahedronGeometry(0.15*s), M(0x887766, { r: 0.9 }));
  r.position.set(x, -0.2, z);
  r.scale.y = 0.6;
  r.castShadow = true;
  scene.add(r);
});

/* ───────── Hamsters ───────── */
const COLORS = [
  { b: 0xffa54f, a: 0xffd699 },
  { b: 0xf5deb3, a: 0xffeecc },
  { b: 0xc4956a, a: 0xe8c8a8 },
  { b: 0xfff5ee, a: 0xffcccc },
  { b: 0xff7f50, a: 0xffb088 },
];

const hamsters = [];
const BOUNDS = { x: 2.5, z: 1.7 };
const WHEEL_POS = { x: 2, z: -1.2 };
const BOWL_POS = { x: -1.5, z: 1 };

for (let i = 0; i < 5; i++) {
  const c = COLORS[i];
  const mesh = makeHamster(c.b, c.a);
  mesh.position.set((Math.random()-.5)*4, 0, (Math.random()-.5)*2.5);
  mesh.rotation.y = Math.random()*Math.PI*2;
  scene.add(mesh);

  hamsters.push({
    mesh,
    angle: Math.random()*Math.PI*2,
    speed: 0.3 + Math.random()*0.3,
    state: 'walking',
    timer: 1 + Math.random()*2,
    bob: Math.random()*Math.PI*2,
    tAngle: 0
  });
}

/* ───────── Loop ───────── */
const clock = new THREE.Clock();
let wSpin = 0;

function tick() {
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  hamsters.forEach((h, i) => {
    h.timer -= dt;
    h.bob += dt * 8;

    // bob
    h.mesh.position.y = h.state === 'walking' ? Math.abs(Math.sin(h.bob)) * 0.04 : 0;

    // idle wobble
    h.mesh.rotation.z = h.state === 'paused'
      ? Math.sin(t * 2 + i) * 0.03
      : h.mesh.rotation.z * 0.9;

    // pick new state
    if (h.timer <= 0) {
      const r = Math.random();
      const dW = Math.hypot(h.mesh.position.x - WHEEL_POS.x, h.mesh.position.z - WHEEL_POS.z);
      const dB = Math.hypot(h.mesh.position.x - BOWL_POS.x, h.mesh.position.z - BOWL_POS.z);

      if (dW < 0.8 && r < 0.35) {
        h.state = 'wheeling';
        h.timer = 2 + Math.random() * 2;
      } else if (dB < 0.7 && r < 0.45) {
        h.state = 'eating';
        h.timer = 1.5 + Math.random() * 1.5;
      } else if (r < 0.3) {
        h.state = 'walking';
        h.timer = 1 + Math.random() * 2;
      } else if (r < 0.5) {
        h.state = 'paused';
        h.timer = 0.5 + Math.random() * 1.5;
      } else {
        h.state = 'turning';
        h.timer = 0.4 + Math.random() * 0.4;
        h.tAngle = h.angle + (Math.random() - 0.5) * Math.PI * 1.5;
      }
    }

    // execute
    switch (h.state) {
      case 'walking':
        h.angle += (Math.random() - 0.5) * 0.02;
        h.mesh.position.x += Math.sin(h.angle) * h.speed * dt;
        h.mesh.position.z += Math.cos(h.angle) * h.speed * dt;
        break;

      case 'turning': {
        const d = h.tAngle - h.angle;
        h.angle += d * dt * 3;
        break;
      }

      case 'eating': {
        const ta = Math.atan2(BOWL_POS.x - h.mesh.position.x, BOWL_POS.z - h.mesh.position.z);
        h.angle += (ta - h.angle) * dt * 3;
        h.mesh.rotation.x = Math.sin(t * 5) * 0.08;
        break;
      }

      case 'wheeling': {
        const oa = t * 2 + i;
        const or = 0.4;
        h.mesh.position.x = WHEEL_POS.x + Math.sin(oa) * or;
        h.mesh.position.z = WHEEL_POS.z + Math.cos(oa) * or;
        h.mesh.position.y = 0.1 + Math.abs(Math.sin(oa * 2)) * 0.15;
        h.angle = oa + Math.PI / 2;
        wSpin = 3;
        break;
      }
    }

    // face
    if (h.state !== 'eating') h.mesh.rotation.x *= 0.9;
    h.mesh.rotation.y = h.angle;

    // clamp
    h.mesh.position.x = THREE.MathUtils.clamp(h.mesh.position.x, -BOUNDS.x, BOUNDS.x);
    h.mesh.position.z = THREE.MathUtils.clamp(h.mesh.position.z, -BOUNDS.z, BOUNDS.z);

    // bounce
    if (Math.abs(h.mesh.position.x) >= BOUNDS.x) h.angle = Math.PI - h.angle;
    if (Math.abs(h.mesh.position.z) >= BOUNDS.z) h.angle = -h.angle;
  });

  // wheel spin
  wSpin *= 0.97;
  wheel.rotation.z += wSpin * dt;

  // subtle animations
  bowl.scale.setScalar(1 + Math.sin(t * 3) * 0.02);
  tunnel.rotation.z = Math.sin(t * 0.5) * 0.02;
  lamp.intensity = 0.5 + Math.sin(t * 2) * 0.1;

  controls.update();
  renderer.render(scene, camera);
}

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

tick();
</script>
</body>
</html>
```

## What's inside

| Element | Details |
|---|---|
| **Cage** | Translucent back wall, wire-grid overlay, metal corner posts + top rails, sandy floor tray with ~80 scattered bedding pieces |
| **Wheel** | Green torus ring, 5 spokes, central hub, cylindrical stand + base — **spins** when a hamster enters its orbit |
| **Food bowl** | Pink truncated-cone bowl with 8 golden pellets; gently pulses |
| **Tunnel** | Blue half-cylinder pipe with flat end caps; sways subtly |
| **5 Hamsters** | Dodecahedron body + head, accent-colored cheeks/feet/inner-ears, black eyes with white highlights, pink nose, tiny cone ears + tail. Five distinct warm color schemes |
| **AI states** | `walking` → random drift + movement · `paused` → idle wobble · `turning` → eased rotation to target · `eating` → faces bowl, nods rhythmically · `wheeling` → orbits the wheel, triggers its spin |
| **Environment** | Purple fog, directional sun with soft shadows, warm point light (flickers), outer ground plane, 4 low-poly trees, 3 rocks |
| **Camera** | OrbitControls with damping, polar-angle clamp, distance limits |

Drop the file in a browser — no build step, no server needed.