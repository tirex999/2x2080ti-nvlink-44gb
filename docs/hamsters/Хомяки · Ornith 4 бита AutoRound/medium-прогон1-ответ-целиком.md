Let me create a single-file HTML project using Three.js that features a low-poly hamster playground. Let me think about what I need:

1. **Scene setup**: A cage with a floor/tray, walls (transparent or wireframe so we can see inside)
2. **Multiple hamsters**: Low-poly cute hamsters with body, head, ears, eyes, nose, tail, legs
3. **Interactive object**: A wheel that hamsters can interact with, plus maybe a food bowl
4. **Behavior**: Hamsters walk, pause, turn, and interact with objects
5. **Camera controls**: OrbitControls to rotate the camera
6. **Visual style**: Cute, low-poly, colorful, funny

Let me build this step by step.

I'll use Three.js from CDN. Let me create a comprehensive but stable implementation.

Key components:
- Floor tray (a shallow box)
- Cage walls (transparent panels or wireframe)
- Hamsters built from primitive geometries (spheres, boxes, cylinders)
- A wheel that spins when hamsters are in it
- A food bowl
- Tunnel
- Ambient + directional lighting
- OrbitControls for camera rotation

Let me write the hamster creation function. Each hamster will be a group of meshes:
- Body (elongated sphere or box)
- Head (sphere)
- Two ears (small spheres or cones)
- Eyes (white spheres with black pupils)
- Nose (small pink sphere)
- Cheeks (optional)
- 4 legs (small cylinders)
- Tail (tiny)

Colors: I'll give each hamster a different fur color (tan, brown, white, gray, orange).

Behavior state machine:
- WALKING: move toward a target, rotate to face direction
- PAUSING: stay still, maybe look around
- INTERACTING: go to the wheel and "ride" it, causing the wheel to spin

Let me implement smooth movement with simple AI.

Let me write clean, well-commented code.

I'll structure the JS:
1. Scene, camera, renderer setup
2. Lighting
3. Cage construction (floor, walls)
4. Props (wheel, food bowl, tunnel)
5. Hamster factory function
6. Hamster AI update logic
7. Animation loop

Let me make sure OrbitControls is available. I'll import it from a CDN that supports ES modules, or use the non-module version. Actually, the simplest reliable approach is to use the CDN with global scripts. But OrbitControls needs to be loaded too.

Modern approach: Use importmap with ES modules from a CDN like unpkg or jsdelivr.

Let me use:
```html
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
</script>
```

This is the cleanest modern approach.

Let me now write the full code.

For the hamster, I want it to look cute and low-poly. Let me use flat shading (flatShading: true) on MeshStandardMaterial or MeshLambertMaterial for the low-poly look.

Let me define dimensions:
- Cage interior: maybe 8 x 4 x 5 (width x height x depth)
- Hamsters: body length ~0.6

Let me write the hamster builder:

```js
function createHamster(color) {
  const hamster = new THREE.Group();
  
  const furMaterial = new THREE.MeshStandardMaterial({
    color: color,
    flatShading: true,
    roughness: 0.9,
    metalness: 0.0
  });
  
  // Body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.45, 8, 6), furMaterial);
  body.scale.set(1.3, 1, 1.1);
  body.position.y = 0.45;
  hamster.add(body);
  
  // Head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.32, 8, 6), furMaterial);
  head.position.set(0.55, 0.55, 0);
  hamster.add(head);
  
  // Ears
  const earGeo = new THREE.CylinderGeometry(0.1, 0.12, 0.12, 6);
  const leftEar = new THREE.Mesh(earGeo, furMaterial);
  leftEar.position.set(0.5, 0.82, 0.15);
  const rightEar = new THREE.Mesh(earGeo, furMaterial);
  rightEar.position.set(0.5, 0.82, -0.15);
  hamster.add(leftEar, rightEar);
  
  // Eyes
  const eyeMaterial = new THREE.MeshStandardMaterial({ color: 0x111111, flatShading: true });
  const eyeGeo = new THREE.SphereGeometry(0.06, 6, 6);
  const leftEye = new THREE.Mesh(eyeGeo, eyeMaterial);
  leftEye.position.set(0.8, 0.6, 0.16);
  const rightEye = new THREE.Mesh(eyeGeo, eyeMaterial);
  rightEye.position.set(0.8, 0.6, -0.16);
  hamster.add(leftEye, rightEye);
  
  // Nose
  const noseMaterial = new THREE.MeshStandardMaterial({ color: 0xff9aa2, flatShading: true });
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 6, 6), noseMaterial);
  nose.position.set(0.87, 0.52, 0);
  hamster.add(nose);
  
  // Cheeks (pink)
  ...
  
  // Legs
  const legMaterial = ...
  const legGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.18, 6);
  // 4 legs at positions
  
  // Tail
  ...
  
  return hamster;
}
```

Then I need to animate legs when walking (bobbing or alternating).

Let me keep it simpler but charming. I'll add a slight bob to the whole hamster when walking, and wiggle legs.

For AI, each hamster has:
- state: 'idle' | 'walking' | 'interacting'
- target position
- speed
- timer for next state change
- a reference to an object to interact with (the wheel)

Let me implement:

```js
function updateHamster(h, dt) {
  h.timer -= dt;
  switch(h.state) {
    case 'idle':
      if (h.timer <= 0) {
        // pick new state
        if (Math.random() < 0.4 && !h.interactingWith) {
          h.state = 'walking';
          h.target = randomPointInCage();
          h.interactingWith = null;
        } else if (Math.random() < 0.3) {
          h.state = 'walking';
          h.target = wheel.position.clone();
          h.interactingWith = wheel;
        } else {
          h.state = 'idle';
          h.timer = rand(1, 3);
        }
      }
      break;
    case 'walking':
      // move toward target
      ...
      if (reached target) {
        if (h.interactingWith) {
          h.state = 'interacting';
          h.timer = rand(3, 6);
        } else {
          h.state = 'idle';
          h.timer = rand(1, 3);
        }
      }
      break;
    case 'interacting':
      h.timer -= dt;
      // spin the wheel
      wheelSpin += dt * speed;
      if (h.timer <= 0) {
        h.state = 'idle';
        h.timer = rand(1, 3);
        h.interactingWith = null;
      }
      break;
  }
}
```

Let me make the hamster face its movement direction by setting rotation.y to atan2 of velocity.

Now let me think about the cage bounds so hamsters stay inside. I'll define bounds and clamp targets.

Let me also make the wheel visually spin. The wheel is a torus or a set of bars on an axis. When a hamster rides it, it rotates.

Let me build the wheel as a group:
- An axle (cylinder vertical)
- A ring (torus) 
- Rungs (small cylinders)

Actually a hamster wheel is typically a torus lying in a vertical plane with rungs. Let me make a torus plus some rungs radiating inward.

Let me place the wheel against a wall.

Food bowl: a flattened cylinder (bowl shape) with some "food" pellets (small spheres/boxes) inside.

Tunnel: a cylinder (hollow) that hamsters could walk near. I'll make it a tube hamsters can walk through visually.

Let me keep props manageable: wheel, food bowl, tunnel. That satisfies "one interactive object" but adds flavor.

Let me now write everything out carefully.

For the floor/tray: a shallow box (like a bin). I'll make the base a thin box and add low walls (edges) so bedding doesn't fall out. Actually the "cage" can be the transparent walls, and the "tray" is the bottom.

Let me do:
- Tray: open-top box, low walls, wood/plastic colored
- Bedding: scattered small colored boxes on the floor (optional, for cuteness)
- Transparent walls around the top (glass/accent)

Hmm, let me keep it clean. I'll make:
- A floor plane with a tray border (low walls)
- Transparent cage walls rising up
- A roof optional (skip for visibility, or make it glass)

Let me just make transparent walls so you can see in from any angle.

Let me set up coordinates:
- Ground at y = 0
- Tray floor from -4 to 4 in x and z
- Walls height ~3

Let me write the code now.

I'll add ambient light, hemisphere light, and a directional light with soft shadows for a nice look. Shadows might slow things but look good. Let me enable shadows on directional light and receivers.

Actually, to keep it stable and fast, I'll add shadows but keep them modest.

Let me finalize the colors palette:
- Hamster colors: #f6c177 (tan), #c98a5b (brown), #f0e0d0 (cream), #b0a090 (gray), #f4a460 (orange)
- Tray: #8ecae6 or wood #d4a373
- Bedding: #e9c46a (sawdust yellow)
- Wheel: #ff6b6b (red) or #4cc9f0 (cyan)
- Food bowl: #9b5de5 (purple)
- Food: #8b5e34 (pellets)
- Tunnel: #f9c74f (yellow) or striped

Let me write it all out.

I'll make the hamsters slightly bounce. Let me add leg animation by rotating legs.

Let me write the full HTML now.

One thing about OrbitControls: it's imported from three/addons. Good.

Let me also add a subtle ground shadow catcher.

Let me write the code:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #bfe3f0; font-family: 'Segoe UI', sans-serif; }
  #app { width: 100%; height: 100%; display: block; }
  #ui {
    position: fixed; top: 16px; left: 16px; z-index: 10;
    background: rgba(255,255,255,0.85); border-radius: 14px;
    padding: 12px 16px; box-shadow: 0 4px 18px rgba(0,0,0,0.15);
    backdrop-filter: blur(6px); max-width: 260px;
  }
  #ui h1 { font-size: 18px; color: #4a4a6a; margin-bottom: 4px; }
  #ui p { font-size: 12px; color: #6a6a8a; line-height: 1.5; }
  #hint { position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
    background: rgba(255,255,255,0.8); border-radius: 20px; padding: 8px 18px;
    font-size: 12px; color: #555; box-shadow: 0 2px 10px rgba(0,0,0,0.12); }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate • Scroll to zoom • Right-drag to pan.<br>
  Watch the little guys explore their cage!</p>
</div>
<div id="hint">They love the wheel & the food bowl 🌾</div>
<div id="app"></div>

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

// ... everything
</script>
</body>
</html>
```

Now the JS. Let me write it fully.

Let me define constants and helper functions first.

```js
const app = document.getElementById('app');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xbfe3f0);
scene.fog = new THREE.Fog(0xbfe3f0, 20, 45);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 100);
camera.position.set(9, 7, 11);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1, 0);
controls.maxPolarAngle = Math.PI * 0.49; // don't go below ground
controls.minDistance = 5;
controls.maxDistance = 30;
```

Lighting:
```js
const hemi = new THREE.HemisphereLight(0xffffff, 0x8899aa, 0.7);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff4e0, 1.1);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 40;
sun.shadow.camera.left = -15;
sun.shadow.camera.right = 15;
sun.shadow.camera.top = 15;
sun.shadow.camera.bottom = -15;
sun.shadow.bias = -0.0004;
scene.add(sun);

const fill = new THREE.DirectionalLight(0x9db4ff, 0.3);
fill.position.set(-6, 5, -8);
scene.add(fill);
```

Cage:
```js
const CAGE_W = 10, CAGE_D = 10, CAGE_H = 4, WALL_THICK = 0.2;
```

Tray bottom:
```js
const trayMat = new THREE.MeshStandardMaterial({ color: 0x8ecae6, flatShading: true, roughness: 0.8 });
const trayBottom = new THREE.Mesh(new THREE.BoxGeometry(CAGE_W, 0.4, CAGE_D), trayMat);
trayBottom.position.y = -0.2;
trayBottom.receiveShadow = true;
scene.add(trayBottom);
```

Tray walls (low edges):
```js
const trayWallH = 0.6;
function trayWall(w, h, d, x, z) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), trayMat);
  m.position.set(x, h/2 - 0.4, z);
  m.castShadow = true;
  m.receiveShadow = true;
  scene.add(m);
}
trayWall(CAGE_W + 0.4, trayWallH, WALL_THICK, 0, CAGE_D/2);
trayWall(CAGE_W + 0.4, trayWallH, WALL_THICK, 0, -CAGE_D/2);
trayWall(WALL_THICK, trayWallH, CAGE_D + 0.4, CAGE_W/2, 0);
trayWall(WALL_THICK, trayWallH, CAGE_D + 0.4, -CAGE_W/2, 0);
```

Bedding: scatter small boxes on floor inside tray.
```js
const beddingMat = new THREE.MeshStandardMaterial({ color: 0xe9c46a, flatShading: true, roughness: 1 });
for (let i = 0; i < 120; i++) {
  const b = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.08, 0.22), beddingMat);
  const x = (Math.random()-0.5)*(CAGE_W-0.6);
  const z = (Math.random()-0.5)*(CAGE_D-0.6);
  b.position.set(x, 0.04, z);
  b.rotation.y = Math.random()*Math.PI;
  b.castShadow = false;
  b.receiveShadow = true;
  scene.add(b);
}
```

Transparent cage walls (upper part):
```js
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xffffff, transparent: true, opacity: 0.14,
  roughness: 0.1, metalness: 0, transmission: 0.9,
  side: THREE.DoubleSide
});
```
Hmm, transmission requires newer three.js; 0.160 has it. But to be safe I'll just use opacity. Let me use opacity-based glass.

Actually let me just use opacity 0.15 and emissive none. It'll look like tinted glass.

```js
const glassMat = new THREE.MeshStandardMaterial({ color: 0xcfeeff, transparent: true, opacity: 0.15, roughness: 0.2, side: THREE.DoubleSide });
function glassWall(w, h, d, x, z) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), glassMat);
  m.position.set(x, 0.6 + h/2, z);
  scene.add(m);
}
glassWall(CAGE_W, CAGE_H, WALL_THICK, 0, CAGE_D/2);
glassWall(CAGE_W, CAGE_H, WALL_THICK, 0, -CAGE_D/2);
glassWall(WALL_THICK, CAGE_H, CAGE_D, CAGE_W/2, 0);
glassWall(WALL_THICK, CAGE_H, CAGE_D, -CAGE_W/2, 0);
```

Add a metal frame bar on top edges for style? Optional. Skip to keep simple.

Props:

Wheel:
```js
const wheel = new THREE.Group();
const wheelMat = new THREE.MeshStandardMaterial({ color: 0xff6b6b, flatShading: true, roughness: 0.5 });
const axleMat = new THREE.MeshStandardMaterial({ color: 0x495057, flatShading: true, roughness: 0.6 });

// axle (horizontal axis)
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.4, 8), axleMat);
axle.rotation.z = Math.PI/2;
wheel.add(axle);

// ring
const ring = new THREE.Mesh(new THREE.TorusGeometry(1.0, 0.08, 8, 24), wheelMat);
wheel.add(ring);

// rungs
for (let i = 0; i < 16; i++) {
  const a = (i/16) * Math.PI * 2;
  const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.0, 6), wheelMat);
  rung.position.set(Math.cos(a)*0.5, Math.sin(a)*0.5, 0);
  rung.rotation.z = a + Math.PI/2; // point radially? 
  // Actually rung should connect center to rim along radius
  rung.position.set(Math.cos(a)*0.5, Math.sin(a)*0.5, 0);
  rung.rotation.x = Math.PI/2; // along radial? hmm
  wheel.add(rung);
}
```

Hmm, let me think about the rung orientation. The wheel lies in the XZ plane? No. Let me define the wheel spinning around the X axis (axle along X). So the ring is in the YZ plane. Rungs go from center outward in the YZ plane.

Axle along X: rotation.z = Math.PI/2 makes cylinder (originally along Y) point along Z... wait. CylinderGeometry default axis is Y. To point along X, rotate 90° about Z. Yes axle.rotation.z = Math.PI/2.

Ring as torus: default torus lies in XY plane with hole along Z. I want the hole along X (so ring plane is YZ). Rotate torus 90° about X: torus.rotation.x = Math.PI/2. Then it's in YZ plane. 

Rungs: small cylinders from center (r=0) to rim (r~0.92), lying in YZ plane, oriented radially. A cylinder along Y rotated to point radially in YZ. For a rung at angle a (measured from +Y toward +Z?), position at (0, cos(a)*0.5, sin(a)*0.5) and rotate so cylinder axis points along that radial direction. 

Simpler: make each rung a cylinder along Y, then rotate about X by angle a to place it radially. Position at radius 0.5 along that direction.

Let me do:
```js
for (let i = 0; i < 16; i++) {
  const a = (i/16) * Math.PI * 2;
  const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.95, 6), wheelMat);
  rung.rotation.x = a; // tilt around X to point radially in YZ
  rung.position.set(0, Math.cos(a)*0.475, Math.sin(a)*0.475);
  wheel.add(rung);
}
```
When a=0, rung along Y at (0, 0.475, 0) — pointing up, from center up. Good, it spans from center to near rim. Actually it's centered at 0.475 so it extends 0.475±0.475 => 0 to 0.95. Good, from center to rim.

Support stand for wheel (two L-brackets to a post):
```js
const standMat = axleMat;
// vertical post
const post = new THREE.Mesh(new THREE.BoxGeometry(0.15, 1.6, 0.15), standMat);
post.position.set(0, 1.2, 0.7);
post.castShadow = true;
wheel.add(post);
// bracket to hold axle
const bracket = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.15, 1.0), standMat);
bracket.position.set(0, 2.0, 0.2);
wheel.add(bracket);
```
Place wheel group at some position against wall, e.g., x = -3.5, z = -3.5, and align the wheel plane.

Actually let me place the wheel so its face (YZ plane) faces diagonally into the room. The axle is along X. Put it in a corner.

Let me set wheel position: x=-3.5, z=-3.5, y=1.2 (center of wheel at height ~1.2 above floor, so bottom of wheel at 0.2). The hamster rides inside near the bottom.

Hmm the wheel center at y=1.2, radius 1.0, so bottom at y=0.2. Good, hamster stands at bottom.

Wait, but hamster needs to stand on the floor (y~0.5 top of hamster) inside the wheel. If wheel bottom is at 0.2 and hamster body center at 0.45, hamster's feet at 0, body center 0.45. That works, hamster sits inside lower part of wheel.

But the hamster should face along the axle direction (X) to "run" — actually hamsters run and the wheel spins, hamster's climbing up the side. Simplify: hamster stands at bottom of wheel facing +X (along axle) and wiggles. The wheel spins around X axis.

Let me place wheel so hamster faces into the room or along X. Fine.

Food bowl:
```js
const foodBowl = new THREE.Group();
const bowlMat = new THREE.MeshStandardMaterial({ color: 0x9b5de5, flatShading: true, roughness: 0.6 });
const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.4, 0.3, 12, 1, true), bowlMat);
bowl.position.y = 0.15;
foodBowl.add(bowl);
const bowlBottom = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 0.02, 12), bowlMat);
bowlBottom.position.y = 0.01;
foodBowl.add(bowlBottom);
// food pellets
const foodMat = new THREE.MeshStandardMaterial({ color: 0x8b5e34, flatShading: true });
for (let i=0;i<10;i++){
  const pellet = new THREE.Mesh(new THREE.DodecahedronGeometry(0.08,0), foodMat);
  const a = Math.random()*Math.PI*2, r = Math.random()*0.35;
  pellet.position.set(Math.cos(a)*r, 0.28 + Math.random()*0.06, Math.sin(a)*r);
  pellet.castShadow = true;
  foodBowl.add(pellet);
}
foodBowl.position.set(3.2, 0, 3.0);
scene.add(foodBowl);
```

Tunnel:
```js
const tunnel = new THREE.Group();
const tunnelMat = new THREE.MeshStandardMaterial({ color: 0xf9c74f, flatShading: true, roughness: 0.7, side: THREE.DoubleSide });
const tunnelTube = new THREE.Mesh(new THREE.TorusGeometry(0.7, 0.4, 8, 20, Math.PI), tunnelMat);
tunnelTube.rotation.z = Math.PI/2; // make it a half-pipe arch
// Actually let me make a full cylinder tunnel
```
Let me make tunnel a half-cylinder arch (like a tunnel you crawl through). Use a torus with phiLength = PI.

Actually simpler: a cylinder lying horizontally with holes at both ends (hamster walks through). Use a cylinder geometry with inner visible. Hmm.

Let me make an arch tunnel: a torus (half circle) — like a rainbow tunnel. Torus radius 0.7, tube 0.12, and phiLength = PI so it's a half ring standing up. Place it on the floor. Hamsters walk around it.

```js
const tunnelMat = new THREE.MeshStandardMaterial({ color: 0xff9f1c, flatShading: true, roughness: 0.7, side: THREE.DoubleSide });
const tunnel = new THREE.Mesh(new THREE.TorusGeometry(0.8, 0.12, 6, 24, Math.PI), tunnelMat);
tunnel.rotation.x = Math.PI/2; // lie flat? 
```
Hmm, torus default plane XY, hole along Z. If I want an arch standing up (like a tunnel you walk through horizontally), I want the circle in the XZ plane (ground plane) — no wait.

A hamster tunnel is a tube you crawl through. Let me make it a straight hollow cylinder lying along Z, with opening at both ends. Hamsters walk through it.

```js
const tunnel = new THREE.Group();
const tunnelMat = new THREE.MeshStandardMaterial({ color: 0xff9f1c, flatShading: true, roughness: 0.7, side: THREE.DoubleSide });
const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 2.2, 12, 1, true), tunnelMat);
tube.rotation.x = Math.PI/2; // axis along Z
tunnel.add(tube);
// rings at ends
const ringMat = new THREE.MeshStandardMaterial({ color: 0xfb8500, flatShading: true });
const r1 = new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.08, 8, 16), ringMat);
r1.position.z = 1.1;
const r2 = r1.clone(); r2.position.z = -1.1;
tunnel.add(r1, r2);
tunnel.position.set(0.5, 0.55, -3.2);
scene.add(tunnel);
```

Good. Hamsters walk near it.

Add a little food dish nearby and maybe a small house/sleeping hut for cuteness. Let me add a tiny wooden hut:
```js
const hut = new THREE.Group();
const woodMat = new THREE.MeshStandardMaterial({ color: 0xd4a373, flatShading: true });
const hutBase = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.8, 1.4), woodMat);
hutBase.position.y = 0.4;
const roof = new THREE.Mesh(new THREE.ConeGeometry(1.1, 0.7, 4), new THREE.MeshStandardMaterial({ color: 0xe63946, flatShading: true }));
roof.position.y = 1.15;
roof.rotation.y = Math.PI/4;
hut.add(hutBase, roof);
hut.position.set(-3.5, 0, 3.2);
scene.add(hut);
```

Nice, adds charm.

Now the hamsters. Let me write createHamster returning group plus metadata.

I'll give each hamster legs that animate, and a name/color.

Let me define the bounds for random targets: within the tray minus props. Simplify: random x in [-4,4], z in [-4,4].

Let me write hamster creation:

```js
const hamsterColors = [0xf6c177, 0xc98a5b, 0xf0e0d0, 0xb0a090, 0xf4a460];

function createHamster(furColor) {
  const h = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color: furColor, flatShading: true, roughness: 0.9 });
  const bellyMat = new THREE.MeshStandardMaterial({ color: 0xfff5e6, flatShading: true, roughness: 0.9 });
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, flatShading: true });
  const pinkMat = new THREE.MeshStandardMaterial({ color: 0xff9aa2, flatShading: true });

  // body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.42, 8, 6), fur);
  body.scale.set(1.35, 1.05, 1.1);
  body.position.y = 0.42;
  body.castShadow = true;
  h.add(body);

  // belly
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.34, 8, 6), bellyMat);
  belly.scale.set(1.2, 0.9, 1.0);
  belly.position.set(0.08, 0.34, 0);
  h.add(belly);

  // head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 6), fur);
  head.position.set(0.55, 0.55, 0);
  head.castShadow = true;
  h.add(head);

  // cheeks
  const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.14, 6, 6), pinkMat);
  cheekL.position.set(0.62, 0.46, 0.16);
  const cheekR = cheekL.clone(); cheekR.position.z = -0.16;
  h.add(cheekL, cheekR);

  // ears
  const earGeo = new THREE.SphereGeometry(0.1, 6, 6);
  const earL = new THREE.Mesh(earGeo, fur);
  earL.scale.set(1, 1, 0.5);
  earL.position.set(0.45, 0.8, 0.16);
  const earR = earL.clone(); earR.position.z = -0.16;
  h.add(earL, earR);

  // eyes
  const eyeGeo = new THREE.SphereGeometry(0.055, 6, 6);
  const eyeL = new THREE.Mesh(eyeGeo, darkMat);
  eyeL.position.set(0.78, 0.6, 0.15);
  const eyeR = eyeL.clone(); eyeR.position.z = -0.15;
  h.add(eyeL, eyeR);
  // eye shine
  const shineGeo = new THREE.SphereGeometry(0.018, 4, 4);
  const shineMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
  const sL = new THREE.Mesh(shineGeo, shineMat); sL.position.set(0.8, 0.62, 0.16);
  const sR = sL.clone(); sR.position.z = -0.16;
  h.add(sL, sR);

  // nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.045, 6, 6), pinkMat);
  nose.position.set(0.83, 0.52, 0);
  h.add(nose);

  // legs (front-back pairs)
  const legGeo = new THREE.CylinderGeometry(0.055, 0.05, 0.18, 6);
  const legMat = pinkMat;
  const legs = [];
  const legPositions = [
    [0.28, 0.09, 0.22], [0.28, 0.09, -0.22],
    [-0.28, 0.09, 0.22], [-0.28, 0.09, -0.22]
  ];
  for (const p of legPositions) {
    const leg = new THREE.Mesh(legGeo, legMat);
    leg.position.set(p[0], p[1], p[2]);
    leg.castShadow = true;
    h.add(leg);
    legs.push(leg);
  }

  // tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 6), pinkMat);
  tail.position.set(-0.55, 0.42, 0);
  h.add(tail);

  h.userData.legs = legs;
  return h;
}
```

Now create several hamsters and assign AI state.

```js
const hamsters = [];
const bounds = { minX: -4.2, maxX: 4.2, minZ: -4.2, maxZ: 4.2 };

for (let i = 0; i < 5; i++) {
  const h = createHamster(hamsterColors[i % hamsterColors.length]);
  const startX = (Math.random()-0.5)*6;
  const startZ = (Math.random()-0.5)*6;
  h.position.set(startX, 0, startZ);
  scene.add(h);
  hamsters.push({
    mesh: h,
    legs: h.userData.legs,
    state: 'idle',
    timer: Math.random()*3,
    vx: 0, vz: 0,
    speed: 1.2 + Math.random()*0.8,
    target: new THREE.Vector3((Math.random()-0.5)*6, 0, (Math.random()-0.5)*6),
    facing: Math.random()*Math.PI*2,
    interactTimer: 0,
    bobPhase: Math.random()*Math.PI*2,
    color: hamsterColors[i % hamsterColors.length]
  });
}
```

Update function:

```js
function updateHamster(s, dt) {
  const m = s.mesh;
  s.bobPhase += dt * 8;

  if (s.state === 'idle') {
    s.timer -= dt;
    // small random look-around bob
    m.rotation.y = s.facing;
    if (s.timer <= 0) {
      const roll = Math.random();
      if (roll < 0.35) {
        // go to wheel
        s.state = 'walking';
        s.target.copy(wheel.position).add(new THREE.Vector3(0, 0, 0.6));
        s.interactTarget = wheel;
        s.facing = Math.atan2(0.6, wheel.position.x - m.position.x) ; // rough
      } else if (roll < 0.6) {
        // go to food
        s.state = 'walking';
        s.target.copy(foodBowl.position).add(new THREE.Vector3(0,0,0.6));
        s.interactTarget = foodBowl;
      } else {
        // wander
        s.state = 'walking';
        s.target.set(
          THREE.MathUtils.clamp((Math.random()-0.5)*8, bounds.minX, bounds.maxX),
          0,
          THREE.MathUtils.clamp((Math.random()-0.5)*8, bounds.minZ, bounds.maxZ)
        );
        s.interactTarget = null;
      }
      s.timer = Math.random()*3 + 1;
    }
  } else if (s.state === 'walking') {
    const dx = s.target.x - m.position.x;
    const dz = s.target.z - m.position.z;
    const dist = Math.hypot(dx, dz);
    if (dist > 0.05) {
      const dirX = dx/dist, dirZ = dz/dist;
      m.position.x += dirX * s.speed * dt;
      m.position.z += dirZ * s.speed * dt;
      s.facing = Math.atan2(dirX, dirZ);
      // animate legs
      for (let i=0;i<s.legs.length;i++){
        s.legs[i].rotation.x = Math.sin(s.bobPhase + (i%2)*Math.PI) * 0.6;
      }
      // bob body
      m.position.y = Math.abs(Math.sin(s.bobPhase))*0.03;
    } else {
      // reached
      if (s.interactTarget) {
        s.state = 'interacting';
        s.interactTimer = 3 + Math.random()*3;
        // orient hamster to ride
        if (s.interactTarget === wheel) {
          m.position.y = 0.05;
          s.facing = Math.atan2(0, 1); // face +X along axle
        }
      } else {
        s.state = 'idle';
        s.timer = 1 + Math.random()*2.5;
      }
    }
    // clamp within bounds
    m.position.x = THREE.MathUtils.clamp(m.position.x, bounds.minX, bounds.maxX);
    m.position.z = THREE.MathUtils.clamp(m.position.z, bounds.minZ, bounds.maxZ);
  } else if (s.state === 'interacting') {
    s.interactTimer -= dt;
    // spin wheel
    wheel.rotation.x += dt * 4;
    // wiggle
    m.position.y = 0.05 + Math.abs(Math.sin(s.bobPhase))*0.03;
    for (let i=0;i<s.legs.length;i++){
      s.legs[i].rotation.x = Math.sin(s.bobPhase + (i%2)*Math.PI) * 0.9;
    }
    if (s.interactTimer <= 0) {
      s.state = 'idle';
      s.timer = 1 + Math.random()*2.5;
      s.interactTarget = null;
      // hop off wheel edge
      s.target.set(
        THREE.MathUtils.clamp(m.position.x + (Math.random()-0.5)*3, bounds.minX, bounds.maxX),
        0,
        THREE.MathUtils.clamp(m.position.z + 1.5, bounds.minZ, bounds.maxZ)
      );
    }
  }
}
```

Wait, for the wheel interaction, the hamster should be positioned at the bottom of the wheel facing along the axle. wheel.position is (-3.5, 1.2, -3.5). The hamster should stand at wheel bottom: y = wheel.position.y - wheelRadius = 1.2 - 1.0 = 0.2. And x,z = wheel.position.x, wheel.position.z.

But I set hamster target to wheel.position.add(0,0,0.6). Let me instead set hamster position directly when reaching wheel. Let me adjust: when interacting with wheel, set m.position to (wheel.position.x, 0.2, wheel.position.z). Facing along +X.

Let me refine the walking-to-wheel: target = wheel.position.clone(). When reached, set position exactly.

Also I realize the hamster facing formula Math.atan2(dirX, dirZ) — I defined facing as atan2(x, z). For rotation, m.rotation.y with facing meaning forward is +Z when facing=0. Let me verify: if moving in +Z (dirX=0, dirZ=1), facing = atan2(0,1) = 0. So hamster faces +Z. The hamster model faces +Z? My hamster head is at x=0.55, so the hamster faces +X in local space! I need to reconcile.

The hamster model's "forward" is +X (head at positive x). So to make it face a direction, I need rotation such that local +X aligns with movement direction. If I set rotation.y = theta, then local +X maps to (sin? )... Let me think. Rotating around Y by angle θ: a vector (1,0,0) becomes (sinθ? ). Rotation matrix about Y: 
x' = x cosθ + z sinθ
z' = -x sinθ + z cosθ
So (1,0,0) -> (cosθ, 0, -sinθ). So forward direction = (cosθ, 0, -sinθ). I want this to equal normalized movement (dx,dz). So cosθ = dirX, -sinθ = dirZ => θ = atan2(-dirZ, dirX)? Let me solve: sinθ = -dirZ, cosθ = dirX. θ = atan2(-dirZ, dirX). Hmm let me just use θ = atan2(dirZ, dirX) but flip sign somewhere.

Actually simpler: set m.rotation.y = Math.atan2(dirX, -dirZ)? Let me just compute θ = atan2(dirX, dirZ) and then adjust.

We want forward (cosθ, 0, -sinθ) == (dirX, dirZ).
So cosθ = dirX and -sinθ = dirZ => sinθ = -dirZ.
θ = atan2(sinθ, cosθ) = atan2(-dirZ, dirX).

So m.rotation.y = Math.atan2(-dirZ, dirX).

Alternatively, I can just build the hamster to face +Z to avoid confusion. But head is at +X. Let me instead orient the hamster model so head points +Z by building with head at (0, 0.55, 0.55)? Eh.

Simplest: use m.rotation.y = Math.atan2(dirX, dirZ) and accept a 90° offset, OR fix the model. Let me just fix the facing calc to match the model: model forward = +X. Set rotation so that after rotation, +X points to (dirX, dirZ).

rotation about Y by θ maps +X to (cosθ, 0, -sinθ). Set equal to (dirX, dirZ):
cosθ = dirX, sinθ = -dirZ → θ = atan2(-dirZ, dirX).

OK so I'll use `s.facing = Math.atan2(-dirZ, dirX)`.

For the wheel interaction, hamster faces +X (along axle), which is model's natural forward (facing=0). Good, set s.facing = 0 when riding.

But wait, when resting/idle I set m.rotation.y = s.facing where s.facing was set during walking. Fine.

Let me reconsider: maybe easier to just rotate the whole hamster group so its head points +Z. But it's fine, I'll use the atan2 formula.

Actually, let me reconsider the model orientation to make it intuitive. I'll keep head at +X and use the correct rotation.

Hmm, but there's subtlety: the hamster's body is elongated along X (scale 1.35). Head at +X end. So "forward" is +X. Good.

Let me double check the leg positions relative to body; they're fine.

Now the wheel spin: wheel.rotation.x += dt*4 when hamster rides. But multiple hamsters could ride; that's fine, they'd all contribute but it's just visual. Only one hamster rides at a time realistically but it's okay.

Let me also make the wheel spin decelerate when no hamster rides? Not necessary. Keep it simple: only spin while a hamster interacts.

Let me store a boolean wheelActive. Actually just spin in interacting branch.

Now resize handling:
```js
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

Animation loop:
```js
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  for (const s of hamsters) updateHamster(s, dt);
  controls.update();
  renderer.render(scene, camera);
}
animate();
```

I think that's solid. Let me refine a few visual things:
- Add ambient to soften shadows.
- Maybe add a couple of decorative items: a water bottle, a small ball toy.

Let me add a water bottle for extra cuteness:
```js
const bottle = new THREE.Group();
const bottleMat = new THREE.MeshStandardMaterial({ color: 0x4cc9f0, transparent: true, opacity: 0.7, roughness: 0.2 });
const bottleBody = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.9, 12), bottleMat);
bottleBody.position.y = 1.2;
const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.15, 8), new THREE.MeshStandardMaterial({ color: 0xff6b6b }));
cap.position.y = 1.7;
const spout = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.2, 8), axleMat);
spout.position.y = 0.65;
bottle.add(bottleBody, cap, spout);
bottle.position.set(4.5, 0, -3.5);
scene.add(bottle);
```

Hmm the spout should point down. Fine.

Actually, let me not overload. Requirements say "one interactive object such as a wheel, tunnel, food bowl, or toy." I'll make the wheel the main interactive one (hamsters ride it and it spins), food bowl (hamsters visit to eat), and tunnel as decoration. That satisfies "interactive object" (plural even). Good.

Let me also ensure the hamsters don't clip through walls — bounds clamp handles that.

Let me reconsider the hamster size vs cage. Cage interior 10x10, hamsters ~0.9 long. Good.

Let me reconsider wheel placement and hamster riding height. Wheel center y = 1.2, radius 1.0, so bottom rim at y = 0.2. Hamster standing inside at y=0.2 (feet), body center ~0.6. That's fine, hamster sits low in wheel. Good.

But the hamster's body scale 1.35 * radius 0.42 ≈ 0.57 half-length, so body spans ±0.57 in X. Wheel axle is 1.4 long in X, so hamster fits. Good.

Now the hamster riding: I set m.position.y = 0.2 (not 0.05). Let me use 0.2. Actually the hamster's feet should be at ~0.2. The leg cylinders are 0.18 tall positioned at y=0.09 in local coords (relative to group). Group y is the feet level. If group y = 0.2, feet at 0.2, body center at ~0.42+0.2 = 0.62. Good.

Wait, in createHamster, body.position.y = 0.42 relative to group, and legs at y=0.09 (half leg height, so leg bottom at 0). So group.y = 0 means feet at y=0. Setting group.y = 0.2 raises everything by 0.2. Good.

Let me set hamster y to 0.2 when at wheel.

Also when walking normally, hamster feet at floor y=0, group.y=0. I added a bob m.position.y = abs(sin)*0.03. Fine.

Now, facing at wheel: set s.facing = 0 (faces +X). But the axle is along X, so hamster faces along the axle — that looks like it's looking sideways into the wheel. Alternatively face +Z (into the room) or -Z. Hmm. For a hamster wheel, the hamster faces tangential to rotation, i.e., along the axle direction (X). So facing +X is correct — the hamster runs "forward" along the axle and the wheel spins under it. Actually in reality the hamster runs and the wheel spins around the horizontal axle; the hamster faces along the axle. Yes facing +X is right. Good.

But then m.rotation.y = 0 means it faces +X naturally. Good.

Let me finalize facing computations:
- Walking: s.facing = Math.atan2(-dirZ, dirX)
- Idle: keep s.facing (last known), maybe add slight random drift.
- Interacting: s.facing = 0 (or random). Let me set to face +X: 0.

Wait, but if hamster approaches wheel from behind, it might be nicer to orient based on approach. Simpler to just snap to facing 0 (along axle). Fine.

Let me also make idle hamsters occasionally turn to look around:
```js
if (s.state === 'idle' && Math.random() < 0.01) s.facing += (Math.random()-0.5)*1.5;
```
That gives life.

Now let me also add gentle hamster "breathing" scale pulse? Optional. Skip.

Let me also ensure shadows look good: receiver is trayBottom (receiveShadow true) and maybe a big ground plane under the tray for shadows. The tray bottom receives shadows. Also add a floor plane outside? The scene background is a color; shadows on nothing look odd. Let me add a large ground plane beyond the cage that receives shadows, colored neutral.

Actually let me put the tray on top of a larger floor that receives shadows. Or just let the tray receive. The hamsters are inside the cage; their shadows fall on bedding/tray. That's fine. But the cage posts/props cast shadows onto tray too. Good enough.

Let me add a big receiving floor beneath everything for nicer shadows and a ground color:
```js
const floorMat = new THREE.MeshStandardMaterial({ color: 0x9fbfd0, flatShading: true, roughness: 1 });
const floor = new THREE.Mesh(new THREE.CircleGeometry(30, 48), floorMat);
floor.rotation.x = -Math.PI/2;
floor.position.y = -0.41; // just below tray
floor.receiveShadow = true;
scene.add(floor);
```
Wait tray bottom is at y=-0.2 (BoxGeometry 0.4 tall, centered at -0.2 so top at 0, bottom at -0.4). Let me set tray top at y=0. So BoxGeometry height 0.4 centered at y=-0.2 gives top at 0. Good. Floor at y=-0.42 just below. Good.

Hmm but the tray walls start at y=-0.4 (bottom) going up trayWallH=0.6 to y=0.2. Let me recompute trayWall positions: I set m.position.y = h/2 - 0.4. With h=0.6, that's 0.3-0.4 = -0.1. So wall spans from -0.4 to 0.2. Top at 0.2. Good, sits on tray bottom (top at 0) and rises to 0.2. Then glass walls from y=0.6? That leaves a gap 0.2 to 0.6. Let me align: glass walls should start at y=0.2 (top of tray wall) to y=0.2+CAGE_H. Let me set glass position.y = 0.2 + CAGE_H/2 = 0.2+2 = 2.2. Let me fix: glass position.y = 0.6 + h/2 was wrong. Use 0.2 + h/2.

Let me redo: tray walls top at 0.2. Glass starts at 0.2, height CAGE_H=4, so center at 0.2+2 = 2.2, top at 4.2. Good.

Let me set glassWall(...).position.y = 0.2 + h/2.

Also the tray walls should sit on the tray bottom (their bottom at -0.4). m.position.y = -0.4 + h/2 = -0.4+0.3 = -0.1. Yes matches earlier. Good.

Now let me also raise floor to -0.41 (below tray bottom -0.4). Actually tray bottom spans -0.4 to 0. Its center -0.2. Floor at -0.41 just under. Good.

Let me also add a subtle rim/frame aesthetic. Skip.

Let me reconsider sky/background: gradient would be nice but solid is fine. I'll add a gradient via CSS background behind? The WebGL covers everything. Solid color 0xbfe3f0 (light blue) is pleasant. Add fog for depth. Good.

Now let me write final code carefully and test mentally for errors.

Potential issue: MeshStandardMaterial with flatShading gives low-poly look but requires normals recomputed for scaled non-uniform scales. When I scale a sphere with scale.set(1.35,1.05,1.1), the normals need updating for correct lighting. I should call body.computeVertexNormals() after scaling, or it'll look off but still works (Three auto-updates normals on scale? Actually Three does update normals automatically when scale changes for Mesh? No—since r125ish, Three.js does NOT auto-update normals on scale change for standard materials? Let me recall: Mesh.applyScale used to trigger normal recalculation. In modern Three, changing .scale does NOT automatically recompute normals unless you call computeVertexNormals or the material reads scale. Actually, Three.js does update normals automatically when you modify geometry scale via mesh.scale? Let me recall: There's a known behavior that modifying mesh.scale does not automatically update geometry normals, leading to incorrect lighting. But many examples scale spheres without computeVertexNormals and it looks okay-ish because lambert is forgiving.

To be safe, I'll call .computeVertexNormals() after scaling on body/belly/head/ears/etc. Actually simpler: use scale via geometry? Let me just call computeVertexNormals on scaled meshes to be safe. But computeVertexNormals on a sphere that's already smooth keeps it smooth. Good.

Actually, the cleaner approach: scale the geometry or use non-uniform scale and call computeVertexNormals. Let me call it on body, belly, head, cheeks, ears.

Hmm, but computeVertexNormals might break flatShading smoothing? For a low-poly sphere (segment 8), it's faceted; computeVertexNormals recomputes per-face normals which for flat-shaded geometry stays flat (each triangle gets its own normal). Actually for flat shading, Three uses the face normals when the geometry has flat normals. If I call computeVertexNormals, it averages normals at shared vertices, making it smooth rather than flat! That would ruin the low-poly look.

So for flatShading, I should NOT call computeVertexNormals (which creates smooth normals). Instead, to get correct lighting with scaled geometry, I can rely on Three's automatic normal update OR set geometry.scale? 

Let me recall precisely: In Three.js, when you change a Mesh's .scale, does it update normals? Historically, no. But since ~2019, I believe Three added automatic normal recalculation on scale for meshes? Let me think... Actually I recall that THREE.Mesh does NOT automatically update normals when scale changes, and this is a common gotcha. However, for flatShading, the visual difference is minimal anyway.

Alternative: Don't scale; instead use different geometry sizes. But non-uniform scale is easiest for body shape.

Given flatShading, even if normals are slightly off, it looks fine and low-poly. I'll skip computeVertexNormals to preserve faceting, and accept minor lighting inaccuracy. Many low-poly scenes do this.

Actually, let me reconsider: I can scale the geometry directly using geo.scale(sx,sy,sz) which scales vertices, and for flat-shaded geometry the face normals remain correct (they're derived from vertices). Wait, if I scale vertices, the face normals computed from those vertices remain perpendicular to faces correctly (scaling preserves angles? No, non-uniform scaling changes angles but normals are recomputed from transformed vertices if we recompute). But if geometry stored normals, they won't update. For flat shading, Three computes face normals from vertex positions at render? Actually flat shading uses the normal attribute; if geometry has flat normals stored (from BufferGeometry with per-face normals), scaling vertices without recomputing normals breaks lighting.

This is getting complicated. Simplest robust solution: use MeshBasicMaterial? No, we want lighting/shadows.

Best: Use non-uniform scale but call computeVertexNormals AND disable flatShading? That loses low-poly look.

Alternative robust approach: Instead of scaling spheres, create them already the right shape isn't possible with primitives.

Let me just trust that Three updates normals on scale for standard materials. Let me recall concretely: I'm fairly sure that in recent Three.js, setting mesh.scale does NOT auto-update normals, BUT there's a property. Hmm.

Actually, you know what, I recall clearly now: THREE.Mesh does not auto-update normals on scale. The documented workaround is computeVertexNormals or setting material.needsUpdate. But computeVertexNormals smooths.

Compromise: I'll scale the geometry vertices manually and recompute flat normals? Too complex.

Better compromise: Build hamster parts without scaling, using appropriately sized spheres and boxes. For the body, instead of scaling a sphere, I can use a stretched approach: use a SphereGeometry with more detail and scale, OR use an IcosahedronGeometry scaled. The faceting from IcosahedronGeometry with flatShading stays faceted even after computeVertexNormals? No, computeVertexNormals on an icosahedron averages at vertices creating smooth-ish look.

Hold on. Let me reconsider how flatShading works. flatShading: true on a material tells Three to use per-face (per-triangle) normals from the geometry, ignoring smoothed vertex normals. This is achieved by Three duplicating vertices per face so each face has its own normal. When you call computeVertexNormals on a geometry, it sets vertex normals (smooth) but does NOT create per-face duplication. However, with flatShading:true, Three reads normals per-face regardless? 

Actually the mechanism: BufferGeometry has a 'normal' attribute. With flatShading, Three's renderer uses these normals but for truly flat shading it needs per-face normals. Three.js does handle this: when flatShading is enabled, the shader uses the normal attribute but the geometry should have flat normals. If the geometry has smooth vertex normals (shared), flatShading will still render each triangle with that triangle's normal IF the geometry has been made flat. 

Ugh, this is deep. Let me just take the pragmatic path: I'll scale geometry using geo.scale() (which transforms vertices) and NOT call computeVertexNormals. Then I'll rely on the fact that for flat-shaded low-poly, even slightly-off normals look acceptable. Additionally, I can call `geometry.attributes.normal.needsUpdate = true`? That won't recompute.

You know, honestly, the cleanest is to NOT scale and instead size primitives appropriately, OR accept scaling and let normals be approximate. Given the cuteness and that lighting is diffuse (hemisphere + directional), minor normal issues won't be noticeable. I'll proceed with scaled spheres and flatShading, no computeVertexNormals. If normals are off, the shading still reads as low-poly shaded. Many tutorials do exactly this.

Actually, I now recall definitively: THREE.js DOES automatically update normals when you change a mesh's scale, IF you use `mesh.scale.set(...)` — no wait.

Let me settle: I'll call `mesh.computeVertexNormals()` only on parts where I DON'T use flat shading effect critically, and keep flatShading for the overall look. Hmm.

New plan: I'll avoid the problem entirely by constructing bodies from an IcosahedronGeometry with detail 0 or 1 and scaling, then NOT calling computeVertexNormals. The faceted look with flatShading comes from the icosahedron's inherent flat triangles. Scaling vertices changes their positions; the face normals stored in geometry were computed from original positions and won't match new positions, causing shading artifacts. BUT Three.js, when flatShading is true, actually recomputes per-face normals from vertex positions in the shader? 

I found the answer in memory: In Three.js, when `material.flatShading = true`, the vertex shader computes normals per-face using the geometry's vertex positions and the fact that each triangle is drawn separately? No, BufferGeometry shares triangles.

OK I'm overthinking. Empirically, scaling a flat-shaded sphere in Three.js and rendering works and looks fine (shading follows the deformed shape reasonably because Three recomputes). Let me just go with it. If there's a minor artifact, it's not worth the complexity. I'll proceed.

Actually, I just realized: Three.js DOES update normals on scale automatically since a long time ago via the `Mesh` updateMatrixNormal in the render loop. Yes! In the renderer, before rendering, it calls `object.updateMatrix()` and `object.updateMatrixNormal()` if `matrixAutoUpdate` etc. And material uses the normal matrix (inverse transpose of matrix) to transform normals. So if the mesh has per-vertex normals from the original (smooth) geometry, transforming them by the normal matrix scales them non-uniformly, which distorts them (non-uniform scaling doesn't preserve orthogonality), giving wrong lighting. But for flat-shaded geometry where each face has its own normal, the same distortion applies. So lighting could be slightly off but not catastrophic.

To get truly correct normals after non-uniform scale, you'd recompute. But the visual result with flat shading and diffuse lighting is acceptable. Going with it.

Alright, let me also make sure shadows work: castShadow on hamsters and props, receiveShadow on floor/tray.

Let me finalize and write the complete file. I'll be careful with syntax.

Let me also add a subtle idle animation for hamsters breathing (scale y oscillation) — optional. I'll add a gentle bob.

Let me also give each hamster a name tag? Not needed.

Let me write the final HTML.

One more: the food bowl interaction — when a hamster reaches food, set state 'interacting' but with food. It should bob its head (eating). I'll reuse 'interacting' state but differentiate action. Let me add s.interactTarget and in interacting branch, if target is food, do eating bob; if wheel, spin wheel. Let me incorporate.

Let me restructure interacting:
```js
} else if (s.state === 'interacting') {
  s.interactTimer -= dt;
  if (s.interactTarget === wheel) {
    wheel.rotation.x += dt * 4.5;
    m.position.y = 0.2 + Math.abs(Math.sin(s.bobPhase))*0.03;
  } else {
    // eating at food bowl
    m.position.y = Math.abs(Math.sin(s.bobPhase*1.5))*0.04;
    // little nibble: tilt head
    headGroup... 
  }
  // leg wiggle
  for (...) legs...
  if (s.interactTimer <= 0) { ... leave ... }
}
```

For eating, tilting head requires referencing head. I stored legs in userData but not head. Let me store head too or just do body bob. I'll do a head nod by storing a reference. Let me store head in userData as well. Actually simpler: just bob the whole body faster (nibbling). Good enough.

Let me store head ref for potential future; not necessary.

Let me finalize.

Also, I want the hamsters to not all pile onto the wheel. Since each has independent timers and random choices, they'll spread out. Good.

Let me also cap: at most maybe 2 on wheel at once is fine visually.

Let me write it all now.

Let me reconsider the facing/rotation formula once more and just test with a concrete example:
- Hamster wants to move in +X direction (dirX=1, dirZ=0). We want hamster to face +X. Model's forward is +X when rotation.y = 0. Using s.facing = atan2(-dirZ, dirX) = atan2(0, 1) = 0. rotation.y = 0 → faces +X. Correct!
- Move in +Z (dirX=0, dirZ=1): s.facing = atan2(-1, 0) = -π/2. rotation.y = -π/2 maps +X to (cos(-π/2), 0, -sin(-π/2)) = (0, 0, 1) = +Z. Correct!
- Move in -X (dirX=-1): s.facing = atan2(0, -1) = π. rotation.y=π maps +X to (cos π,0,-sin π)=(-1,0,0) = -X. Correct!
- Move in -Z (dirZ=-1): s.facing = atan2(1,0) = π/2. maps +X to (cos π/2,0,-sin π/2)=(0,0,-1) = -Z. Correct!

Great, formula s.facing = Math.atan2(-dirZ, dirX) is correct.

Now writing final code.

Let me also add window title and a nice font.

Let me also make the scene a bit bigger and camera framing good. Camera at (9,7,11) looking at (0,1,0). Good.

Let me write it out fully and cleanly.

I'll also add a subtle ground shadow catcher: floor receiveShadow true.

Also add environment? No, keep simple.

Let me also add a small "food bowl" eating animation and wheel spin only when hamster present. Since multiple hamsters, wheel.rotation.x += while any rides.

Let me write the code now in full.

Let me reconsider the number of hamsters: 5 is good. Colors array has 5. Good.

Let me also give hamsters tiny smiles? Add a small curved line? Hard. Skip; eyes+nose+cheeks are cute enough.

Maybe add small teeth? Skip.

Let me add eyelids? No.

Alright. Let me also ensure the hamster ears are sphere scaled to look like floppy ears. ear scale (1,1,0.5) makes them flat-ish. Good.

Final code below.

Let me also double-check torus for wheel: new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments, arc). arc default 2π. radius 1.0, tube 0.08, radialSegments 8, tubularSegments 24. Good. rotation.x = Math.PI/2 to put ring in YZ plane. Wait, default torus lies in XY plane (hole along Z). To rotate hole to X axis (ring in YZ plane), rotate about X by 90°: rotation.x = Math.PI/2. Yes.

Axle cylinder along X: default cylinder along Y, rotate about Z by π/2 → points along X? Rotating Y-axis vector (0,1,0) about Z by 90°: (−sin90·? ) rotation about Z: x'=x cosθ - y sinθ; for (0,1,0), θ=90: x' = -1, y'=0 → (-1,0,0). So along X. Good. axle.rotation.z = Math.PI/2.

Rungs: cylinder along Y, rotate about X by angle a to point radially in YZ. rotation.x = a. position at (0, cos a *0.475, sin a*0.475). At a=0: along +Y at y=0.475, spanning 0..0.95. Good. These connect center to near rim. Good.

Wheel group positioned at wheelPos = (-3.5, 1.2, -3.5). The hamster rides at bottom: (wheelPos.x, 0.2, wheelPos.z). Good.

Stand: post behind wheel. Let me place post at z offset so it's behind the wheel (away from room). Wheel faces into room (+Z toward center? The wheel plane is YZ, its "face" is along X). The hamster rides at bottom facing +X. The support post should be on one side along X. Let me put post at (wheelPos.x, ?, wheelPos.z + 0.6) i.e., +Z side. And a horizontal arm to hold axle. Actually the axle itself needs support. Let me make two side brackets.

Simplify: a vertical post at one end of the axle and an arm reaching to the wheel center.

post at (wheelPos.x - 0.7, ..., wheelPos.z) holding one end of axle; arm from post top to wheel center. Let me do:
```js
const post = new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,2.2,8), standMat);
post.position.set(wheelPos.x - 0.7, 1.2, wheelPos.z);
post.castShadow = true;
wheel.add(post);
const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,1.4,8), standMat);
arm.rotation.z = Math.PI/2;
arm.position.set(wheelPos.x - 0.0, 2.3, wheelPos.z); // horizontal along X
```
Hmm this is getting messy. Let me simplify the stand: a single vertical pole from floor to above wheel center, attached at wheel's -X side, plus a horizontal support arm to the axle.

Actually, simplest stable-looking stand: a vertical pole at (-X side) from floor (y=-0.4) up to y=2.4, and a horizontal arm from top of pole to the wheel center holding the axle.

Let me compute in wheel local coords (wheel group origin at wheelPos):
- pole: from (−0.7, −1.2, 0) to (−0.7, +1.2, 0)? That's vertical at x=-0.7. Height 2.4, centered y=0 → spans -1.2 to 1.2. In world: y from 0.0 to 2.4. Bottom at y=0 (floor). Good.
- arm: horizontal from pole top (−0.7,1.2,0) to center (0,?,0). Let me make arm from x=-0.7 to x=0 at y=1.2 (at wheel center height). Arm length 0.7, along X.
  arm rotation.z = π/2 (along X), position at x=-0.35, y=1.2.

Then axle passes through center and is held by pole+arm. Good enough visually.

Let me set:
```js
const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.07, 2.4, 8), standMat);
pole.position.set(-0.7, 0.8, 0); // spans y from -0.4 to 2.0
pole.castShadow = true;
wheel.add(pole);
const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.75, 8), standMat);
arm.rotation.z = Math.PI/2;
arm.position.set(-0.33, 1.2, 0);
wheel.add(arm);
```
pole position y=0.8 spans -0.4 to 2.0. Good, sits on floor (y=-0.4 is tray top; pole bottom at -0.4). Actually wheel group at y=1.2 world; local y=-0.4 → world 0.8? Wait wheel group position y=1.2. Local point y=-1.6 → world -0.4. Pole local position 0.8 with height 2.4 spans local -0.4 to 2.0 → world 0.8 to 3.2. That's too high; pole should reach down to floor.

I'm confusing myself with local vs world. The wheel group's origin is at world (wheelPos) = (-3.5, 1.2, -3.5). Everything added to wheel is offset by this. So a pole at local position (−0.7, −1.2, 0) with height 2.4 spans local y from −2.4 to 0 → world y from −1.2 to 1.2. That goes below floor (tray top at 0). Not good.

Let me instead design the stand relative to world floor. The wheel center is at world y=1.2. The pole should go from world floor (y≈0) up to world y≈2.4, located at local x = -0.7 (i.e., world x = -3.5 -0.7 = -4.2). Local y for world 0 is -1.2; for world 2.4 is +1.2. So pole local position y = 0, height 2.4, spans local -1.2 to 1.2 → world -0.4 to 2.4. Slightly below floor (tray top 0) by 0.4. Let me raise: pole local position y = 0.2, height 2.0, spans local -0.8 to 1.2 → world -0.2 to 2.4. Close enough; bottom at -0.2 just below tray top 0. Acceptable, or shift to y=0.3 height 1.8 spanning -0.6..1.2 → world -0.4..2.4. Hmm.

Simplest: make pole from world y=0 to y=2.4. World 0 → local -1.2; world 2.4 → local +1.2. So local position 0, height 2.4. Bottom local -1.2 → world -0.4. It'll poke 0.4 below tray top into the tray. Visually the pole meets the floor area; minor. Or I can place the whole wheel a bit higher so its stand sits on tray. Let me raise wheel center to y=1.4. Then local -1.2 → world 0.2. Good, pole bottom at 0.2, sitting on tray. And wheel bottom rim at world 1.4-1.0=0.4, hamster rides at y~0.2? Let me set hamster ride y = wheelCenterWorld - radius + hamsterFootOffset. If wheel center world =1.4, rim bottom=0.4. Hamster feet at 0.4, group y=0.4. Let me set hamster interact y = 0.45.

Let me just set wheel center world y = 1.4, and hamster rides at local y = -0.95 (world 0.45). Actually let me place hamster group at world y such that it sits comfortably. Let me set hamster interact y = 0.4 (world). Since wheel center world 1.4, local y = -1.0. That's near rim bottom (0.4). Good, hamster at bottom of wheel.

Let me finalize: wheel center world = (-3.5, 1.4, -3.5). Hamster at (-3.5, 0.4, -3.5).

Pole: local position (−0.7, 0, 0), height 2.4 → world y from 0.2 to 2.6. Bottom at 0.2 sits on tray. Good.
Arm: from pole top area to wheel center. Pole top world y 2.6. Let me instead arm at wheel center height (world 1.4, local 0). Arm from x=-0.7 to x=0 at local y=0. Arm local position (-0.35, 0, 0), length 0.7, rotation.x? No, along X → rotation.z = π/2. Good.

But then the axle at center is supported by arm at x=-0.7..0. Fine.

Actually the pole at x=-0.7 and arm reaching to center; the wheel axle spans x from -0.7 to 0.7 (length 1.4). Support at -0.7 end via pole, and arm bridges. Good enough.

Let me also add a second support? One is fine visually.

Let me set:
```js
const wheelPos = new THREE.Vector3(-3.5, 1.4, -3.5);
wheel.position.copy(wheelPos);
// axle
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,1.4,8), standMat);
axle.rotation.z = Math.PI/2;
wheel.add(axle);
// ring
const ring = new THREE.Mesh(new THREE.TorusGeometry(1.0,0.07,8,28), wheelMat);
ring.rotation.x = Math.PI/2;
wheel.add(ring);
// rungs
for i in 16: rung as described
// stand
pole: local (-0.7,0,0) height 2.4
arm: local (-0.35,0,0) rotation.z=PI/2
```

Hamster at (-3.5, 0.4, -3.5) facing +X.

Good.

Now food bowl at (3.2, 0, 3.0). Hamster eats at (3.2, 0.3, 3.0) maybe slightly offset. Set target to foodBowl.position.add(0,0,0.5) → (3.2,0,3.5). When reached, set hamster position to (3.2, 0.3, 3.5) facing... facing the bowl. Facing = atan2(-dirZ, dirX) where dir from approach. Or just face -Z (toward bowl). Let me set when eating, s.facing = atan2 toward bowl. Simpler: set facing to bring its snout to bowl. Bowl is at (3.2,0,3.0), hamster at (3.2,0,3.5). Bowl is -Z relative. Hamster should face -Z: facing = atan2(-(-0.5?),...). Let me just set s.facing = Math.atan2(-dirZ, dirX) computed at arrival. dir = bowl - hamster = (0,0,-0.5) → dirX=0, dirZ=-1 → facing = atan2(1, 0) = π/2. rotation π/2 faces -Z. Good, snout toward bowl. 

Now hut at (-3.5, 0, 3.2). Decoration.

Tunnel at (0.5, 0.55, -3.2) — arch along Z.

Water bottle at (4.5, 0, -3.5) — attach to wall. Decoration.

Let me also add a couple of scattered chew toys (small cubes) for color. Optional. I'll add 2-3 small colored boxes as toys that hamsters might walk to occasionally. Keep minimal.

Actually to satisfy "toy" I could make one hamster interact with a ball. But that adds complexity. The requirement says "one interactive object such as a wheel, tunnel, food bowl, or toy" — I have wheel + food bowl interactive. That satisfies it. I'll keep tunnel and hut as decor. Maybe add one ball toy that hamsters nudge? I'll add a small ball that rolls when a hamster is near — fun but optional. Let me add a rolling ball toy that a hamster can push. Actually let me keep scope tight: wheel (spin), food bowl (eat). Add tunnel, hut, bottle as decor. Good.

Let me finalize the code and write it out.

Let me reconsider: The prompt says "one interactive object such as a wheel, tunnel, food bowl, or toy." So having the wheel and food bowl both interactive is great.

Let me write final code.

I'll also add a gentle auto-rotate? No, user controls. Keep manual.

Let me write it all.

Also I should double check imports: OrbitControls path 'three/addons/controls/OrbitControls.js'. Good with importmap mapping 'three/addons/'.

Let me produce the final HTML file.

Let me make sure to clamp hamster positions and targets within bounds and away from walls. Bounds minX -4.2 maxX 4.2, minZ -4.2 maxZ 4.2. The tray is 10 wide (−5..5) with walls at ±5. Glass walls at ±5. So hamsters within ±4.2 stay inside. Props: wheel at x=-3.5, food at 3.2, hut -3.5, tunnel 0.5. Hamsters might path into these but that's fine (they'll stand inside/near). To avoid clipping into wheel when not riding, clamp is enough. Acceptable for a cute scene.

Let me finalize.

I'll write the update function robustly.

Let me also add a "nibble" head-bob for eating by referencing head. I'll store head reference in userData.head. Then in eating, rotate head slightly. Nice touch.

Let me add userData.head = head in createHamster.

Now writing final.

Let me also ensure performance: 5 hamsters × ~15 meshes = 75 meshes + props. Fine.

Let me write it.

Also I realize I should set hamster castShadow true and also maybe receiveShadow. Fine.

Let me produce the final code now. I'll be thorough.

Let me write the whole thing carefully.

Final code:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>🐹 Low-Poly Hamster Playground</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:100%; height:100%; overflow:hidden; font-family:'Segoe UI',system-ui,sans-serif; background:#bfe3f0; }
  #app { display:block; width:100%; height:100%; }
  #ui {
    position:fixed; top:16px; left:16px; z-index:10;
    background:rgba(255,255,255,0.88); border-radius:16px;
    padding:14px 18px; max-width:270px;
    box-shadow:0 8px 26px rgba(0,0,0,0.16); backdrop-filter:blur(8px);
  }
  #ui h1 { font-size:18px; color:#464a6a; margin-bottom:6px; }
  #ui p { font-size:12.5px; color:#5c607a; line-height:1.55; }
  #hint {
    position:fixed; bottom:16px; left:50%; transform:translateX(-50%);
    background:rgba(255,255,255,0.9); border-radius:22px; padding:9px 20px;
    font-size:13px; color:#4a4a66; box-shadow:0 6px 20px rgba(0,0,0,0.14);
    z-index:10;
  }
</style>
</head>
<body>
  <div id="ui">
    <h1>🐹 Low-Poly Hamster Playground</h1>
    <p><b>Drag</b> to orbit • <b>Scroll</b> to zoom • <b>Right-drag</b> to pan.<br/>
    Watch the little guys roam, snack, and hit the gym!</p>
  </div>
  <div id="hint">They love the wheel & the food bowl 🌾💜</div>
  <div id="app"></div>

  <script type="importmap">
  {
    "imports": {
      "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
      "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
    }
  }
  </script>
  <script type="module">
  // ... JS
  </script>
</body>
</html>
```

Now JS. Let me write it.

I'll now assemble the complete JS.

I want to double check the leg animation referencing userData.legs and head.

Let me write createHamster to return group with userData {legs:[], head}.

Alright, writing final answer.

Let me also add a subtle breathing scale on idle (body scaleY oscillation) for life. I'll apply to body mesh only. In update, if idle, body.scale.y = 1 + sin(phase)*0.02. But body.scale is also used for shape (1.35,1.05,1.1). Adding breathing modifies y. That's fine, just a tiny oscillation. But resetting scale each frame could conflict. Let me store base scale and multiply. Simpler: skip breathing to avoid complexity; the leg wiggle and bob suffice.

Actually a gentle breathing makes them look alive. Let me add: store body base scale, and in update set body.scale.y = BASE_Y * (1 + 0.03*sin(phase)). But body.scale.x/z also base. Let me store baseScale = {x:1.35,y:1.05,z:1.1} and reconstruct each frame: body.scale.set(base.x, base.y*(1+0.03*sin(phase)), base.z). That keeps shape plus breathing. Good. I'll do that for all states (always breathe).

Let me implement.

Now final code. Let me write it out completely and carefully.

I'll define everything in module scope.

Let me write.

Also, I should make sure to handle the case where a hamster's target equals current position (dist 0) → goes to interacting/idle. Fine.

Let me also add jitter to idle facing.

Write now.

Let me also ensure wheel only spins when a hamster is interacting with it, and decays otherwise (optional). I'll just spin when interacting; when none, it stops. Good.

Also, when a hamster leaves the wheel, it should walk away. I set target to move away. Good.

Let me finalize positions:
- wheelPos = (-3.5, 1.4, -3.5)
- foodBowl at (3.2, 0, 3.0)
- tunnel at (0.6, 0, -3.3) along Z
- hut at (-3.5, 0, 3.2)
- bottle at (4.6, 0, -3.5)

Bounds ±4.2.

Hamsters spawn within ±4.

Alright, writing final answer with the complete code.

Let me make the tunnel properly: I'll make it a half-torus arch so hamsters can walk under it and it looks like a play tunnel. Actually a full cylinder tunnel (you crawl through) is more recognizable. Let me do a cylinder (hollow) lying along Z with open ends. Use CylinderGeometry(radius, radius, length, 16, 1, true) with side DoubleSide. Color orange with darker rings at ends. Hamsters walk through/around.

Let me finalize tunnel:
```js
const tunnel = new THREE.Group();
const tunnelMat = new THREE.MeshStandardMaterial({ color:0xff9f1c, flatShading:true, roughness:0.7, side:THREE.DoubleSide });
const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.55,0.55,2.0,16,1,true), tunnelMat);
tube.rotation.x = Math.PI/2; // axis along Z
tunnel.add(tube);
const ringMat = new THREE.MeshStandardMaterial({ color:0xfb8500, flatShading:true });
const ringA = new THREE.Mesh(new THREE.TorusGeometry(0.55,0.07,8,16), ringMat);
ringA.position.z = 1.0;
const ringB = ringA.clone(); ringB.position.z = -1.0;
tunnel.add(ringA, ringB);
tunnel.position.set(0.6, 0.55, -3.3);
scene.add(tunnel);
```
tunnel at y=0.55 means tube center at 0.55, radius 0.55 → bottom at 0 (floor). Good, sits on floor. Open ends at ±Z.

Good.

Now let me write everything.

I think it's ready. Let me output the final single-file HTML.

Let me make sure about THREE.MathUtils availability — yes in r160 it's THREE.MathUtils. Good.

Also clamp function.

Let me write final.

Double-check: In updateHamster walking branch, I compute dist and move. Good. When reached (dist<0.05), decide interact or idle. For wheel/food interact, set position precisely and facing.

Let me set for wheel: when reached, m.position.set(wheelPos.x, 0.4, wheelPos.z); s.facing = 0 (face +X along axle). interactTarget = wheel.

For food: reached food target (3.2,0,3.5). Set m.position.set(target.x, 0.3, target.z). facing = atan2(-dirZ, dirX) computed from approach (dir = target - position). Actually at arrival dir is tiny; better compute facing = direction from hamster to bowl: bowlAt(3.2,3.0), hamsterAt(3.2,3.5) → dir=(0,0,-0.5) → facing=atan2(0.5,0)=π/2 (faces -Z toward bowl). Let me compute facing = Math.atan2(-(bowl.z - m.position.z), (bowl.x - m.position.x)). = atan2(-(-0.5), 0) = atan2(0.5,0)=π/2. Good.

Let me store bowlPos and use it.

Now interacting branch: if interactTarget===wheel spin; else eat (bob). Both do leg wiggle and body bob. On timer end, choose new wander target away.

Let me code it.

I'll write the final answer now.

Let me also add a nice title color and emoji.

Also I want to add a subtle ground shadow catcher: floor receiveShadow true.

Also add environment? No, keep simple.

Let me produce the final file.

Let me reconsider the number of hamsters: 5 is good. Colors array has 5. Good.

Let me also give hamsters a name tag? Not needed.

Let me add small teeth? Skip.

Let me add eyelids? No.

Alright. Let me also ensure the hamsters don't all pile onto the wheel. Since each has independent timers and random choices, they'll spread out. Good.

Let me also cap: at most maybe 2 on wheel at once is fine visually.

Let me write it all now.

Let me reconsider the facing/rotation formula once more and just test with a concrete example:
- Hamster wants to move in +X direction (dirX=1, dirZ=0). We want hamster to face +X. Model's forward is +X when rotation.y = 0. Using s.facing = atan2(-dirZ, dirX) = atan2(0, 1) = 0. rotation.y = 0 → faces +X. Correct!
- Move in +Z (dirX=0, dirZ=1): s.facing = atan2(-1, 0) = -π/2. rotation.y = -π/2 maps +X to (0,0,1) = +Z. Correct!
etc. Verified above.

Writing final answer.

I'll keep comments concise but helpful.

Let me produce it.
</think>

# 🐹 Low-Poly Hamster Playground

Here's a complete, single-file project. Just save it as `index.html` and open it in any modern browser — no build step, no dependencies to install.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>🐹 Low-Poly Hamster Playground</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:100%; height:100%; overflow:hidden; font-family:'Segoe UI',system-ui,sans-serif; background:#bfe3f0; }
  #app { display:block; width:100%; height:100%; }
  #ui {
    position:fixed; top:16px; left:16px; z-index:10;
    background:rgba(255,255,255,0.88); border-radius:16px;
    padding:14px 18px; max-width:270px;
    box-shadow:0 8px 26px rgba(0,0,0,0.16); backdrop-filter:blur(8px);
  }
  #ui h1 { font-size:18px; color:#464a6a; margin-bottom:6px; }
  #ui p { font-size:12.5px; color:#5c607a; line-height:1.55; }
  #hint {
    position:fixed; bottom:16px; left:50%; transform:translateX(-50%);
    background:rgba(255,255,255,0.9); border-radius:22px; padding:9px 20px;
    font-size:13px; color:#4a4a66; box-shadow:0 6px 20px rgba(0,0,0,0.14);
    z-index:10;
  }
</style>
</head>
<body>
  <div id="ui">
    <h1>🐹 Low-Poly Hamster Playground</h1>
    <p><b>Drag</b> to orbit • <b>Scroll</b> to zoom • <b>Right-drag</b> to pan.<br/>
    Watch the little guys roam, snack, and hit the gym!</p>
  </div>
  <div id="hint">They love the wheel & the food bowl 🌾💜</div>
  <div id="app"></div>

  <script type="importmap">
  {
    "imports": {
      "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
      "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
    }
  }
  </script>
  <script type="module">
  // ============================================================
  //  🐹 Low-Poly Hamster Playground
  // ============================================================
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

  // ---- Renderer / Camera / Controls ----
  const app = document.getElementById('app');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xbfe3f0);
  scene.fog = new THREE.Fog(0xbfe3f0, 26, 55);

  const camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 100);
  camera.position.set(9.5, 7.5, 11.5);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  app.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.target.set(0, 1.2, 0);
  controls.minDistance = 5;
  controls.maxDistance = 30;
  controls.maxPolarAngle = Math.PI * 0.49; // never dive under the floor

  // ---- Lighting ----
  const hemi = new THREE.HemisphereLight(0xffffff, 0x8899aa, 0.75);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xfff4e0, 1.15);
  sun.position.set(8, 15, 6);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.near = 1;
  sun.shadow.camera.far = 45;
  sun.shadow.camera.left = -16;
  sun.shadow.camera.right = 16;
  sun.shadow.camera.top = 16;
  sun.shadow.camera.bottom = -16;
  sun.shadow.bias = -0.0004;
  scene.add(sun);

  const fill = new THREE.DirectionalLight(0x9db4ff, 0.35);
  fill.position.set(-7, 6, -9);
  scene.add(fill);

  // ============================================================
  //  The Cage (tray + bedding + glass walls)
  // ============================================================
  const W = 10, D = 10, GH = 4;                 // cage width / depth / glass height
  const trayWallH = 0.6;

  const trayMat = new THREE.MeshStandardMaterial({ color: 0x8ecae6, flatShading: true, roughness: 0.85 });
  const floorMat = new THREE.MeshStandardMaterial({ color: 0x9fbfd0, flatShading: true, roughness: 1 });

  // Ground that catches shadows (outside the cage)
  const ground = new THREE.Mesh(new THREE.CircleGeometry(32, 48), floorMat);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.42;
  ground.receiveShadow = true;
  scene.add(ground);

  // Wooden tray base
  const trayBottom = new THREE.Mesh(new THREE.BoxGeometry(W + 0.4, 0.4, D + 0.4), trayMat);
  trayBottom.position.y = -0.2;
  trayBottom.receiveShadow = true;
  trayBottom.castShadow = true;
  scene.add(trayBottom);

  // Low tray lips
  function trayWall(w, h, d, x, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), trayMat);
    m.position.set(x, h / 2 - 0.4, z);
    m.castShadow = true; m.receiveShadow = true;
    scene.add(m);
  }
  trayWall(W + 0.5, trayWallH, 0.2, 0,  D / 2);
  trayWall(W + 0.5, trayWallH, 0.2, 0, -D / 2);
  trayWall(0.2, trayWallH, D + 0.5,  W / 2, 0);
  trayWall(0.2, trayWallH, D + 0.5, -W / 2, 0);

  // Sawdust bedding
  const beddingMat = new THREE.MeshStandardMaterial({ color: 0xe9c46a, flatShading: true, roughness: 1 });
  for (let i = 0; i < 140; i++) {
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.07, 0.22), beddingMat);
    b.position.set((Math.random() - 0.5) * (W - 0.6), 0.035, (Math.random() - 0.5) * (D - 0.6));
    b.rotation.y = Math.random() * Math.PI;
    b.receiveShadow = true;
    scene.add(b);
  }

  // Transparent glass walls
  const glassMat = new THREE.MeshStandardMaterial({
    color: 0xcfeeff, transparent: true, opacity: 0.15, roughness: 0.2,
    metalness: 0, side: THREE.DoubleSide
  });
  function glassWall(w, h, d, x, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), glassMat);
    m.position.set(x, trayWallH + h / 2, z);
    scene.add(m);
  }
  glassWall(W, GH, 0.2, 0,  D / 2);
  glassWall(W, GH, 0.2, 0, -D / 2);
  glassWall(0.2, GH, D,  W / 2, 0);
  glassWall(0.2, GH, D, -W / 2, 0);

  // Metal frame caps on top edges
  const frameMat = new THREE.MeshStandardMaterial({ color: 0xd7dcec, flatShading: true, roughness: 0.4, metalness: 0.5 });
  function frameBar(w, d, x, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, 0.12, d), frameMat);
    m.position.set(x, trayWallH + GH + 0.06, z);
    m.castShadow = true;
    scene.add(m);
  }
  frameBar(W + 0.5, 0.24, 0,  D / 2);
  frameBar(W + 0.5, 0.24, 0, -D / 2);
  frameBar(0.24, 0.24,  W / 2, 0);
  frameBar(0.24, 0.24, -W / 2, 0);

  // ============================================================
  //  Props: wheel (interactive), food bowl (interactive),
  //         tunnel, sleeping hut, water bottle (decor)
  // ============================================================
  const standMat = new THREE.MeshStandardMaterial({ color: 0x495057, flatShading: true, roughness: 0.55 });

  // --- Interactive: exercise wheel ---
  const wheel = new THREE.Group();
  const wheelMat = new THREE.MeshStandardMaterial({ color: 0xff6b6b, flatShading: true, roughness: 0.5 });
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.4, 8), standMat);
  axle.rotation.z = Math.PI / 2;
  wheel.add(axle);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.0, 0.07, 8, 28), wheelMat);
  ring.rotation.x = Math.PI / 2;
  wheel.add(ring);
  for (let i = 0; i < 16; i++) {
    const a = (i / 16) * Math.PI * 2;
    const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.95, 6), wheelMat);
    rung.rotation.x = a;
    rung.position.set(0, Math.cos(a) * 0.475, Math.sin(a) * 0.475);
    wheel.add(rung);
  }
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.07, 2.4, 8), standMat);
  pole.position.set(-0.7, 0, 0); pole.castShadow = true;
  wheel.add(pole);
  const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.75, 8), standMat);
  arm.rotation.z = Math.PI / 2; arm.position.set(-0.33, 0.15, 0);
  wheel.add(arm);
  const wheelPos = new THREE.Vector3(-3.5, 1.4, -3.5);
  wheel.position.copy(wheelPos);
  scene.add(wheel);

  // --- Interactive: food bowl ---
  const foodBowl = new THREE.Group();
  const bowlMat = new THREE.MeshStandardMaterial({ color: 0x9b5de5, flatShading: true, roughness: 0.6 });
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.42, 0.3, 12, 1, true), bowlMat);
  bowl.position.y = 0.15;
  const bowlBase = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.04, 12), bowlMat);
  bowlBase.position.y = 0.01;
  foodBowl.add(bowl, bowlBase);
  const foodMat = new THREE.MeshStandardMaterial({ color: 0x8b5e34, flatShading: true });
  for (let i = 0; i < 11; i++) {
    const p = new THREE.Mesh(new THREE.DodecahedronGeometry(0.07, 0), foodMat);
    const a = Math.random() * Math.PI * 2, r = Math.random() * 0.34;
    p.position.set(Math.cos(a) * r, 0.30 + Math.random() * 0.05, Math.sin(a) * r);
    p.castShadow = true;
    foodBowl.add(p);
  }
  const foodPos = new THREE.Vector3(3.2, 0, 3.0);
  foodBowl.position.copy(foodPos);
  scene.add(foodBowl);

  // --- Decor: tunnel ---
  const tunnelMat = new THREE.MeshStandardMaterial({ color: 0xff9f1c, flatShading: true, roughness: 0.7, side: THREE.DoubleSide });
  const tunnel = new THREE.Group();
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 2.0, 16, 1, true), tunnelMat);
  tube.rotation.x = Math.PI / 2;
  tunnel.add(tube);
  const ringMat = new THREE.MeshStandardMaterial({ color: 0xfb8500, flatShading: true });
  const rA = new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.07, 8, 16), ringMat);
  rA.position.z = 1.0;
  const rB = rA.clone(); rB.position.z = -1.0;
  tunnel.add(rA, rB);
  tunnel.position.set(0.6, 0.55, -3.3);
  scene.add(tunnel);

  // --- Decor: sleeping hut ---
  const hut = new THREE.Group();
  const woodMat = new THREE.MeshStandardMaterial({ color: 0xd4a373, flatShading: true, roughness: 0.9 });
  const hutBase = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.85, 1.5), woodMat);
  hutBase.position.y = 0.42; hutBase.castShadow = true; hutBase.receiveShadow = true;
  const roof = new THREE.Mesh(
    new THREE.ConeGeometry(1.15, 0.75, 4),
    new THREE.MeshStandardMaterial({ color: 0xe63946, flatShading: true, roughness: 0.85 })
  );
  roof.rotation.y = Math.PI / 4; roof.position.y = 1.22; roof.castShadow = true;
  hut.add(hutBase, roof);
  hut.position.set(-3.5, 0, 3.2);
  scene.add(hut);

  // --- Decor: water bottle ---
  const bottle = new THREE.Group();
  const bottleBody = new THREE.Mesh(
    new THREE.CylinderGeometry(0.2, 0.2, 0.9, 12),
    new THREE.MeshStandardMaterial({ color: 0x4cc9f0, transparent: true, opacity: 0.72, roughness: 0.2 })
  );
  bottleBody.position.y = 1.2;
  const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.15, 8), new THREE.MeshStandardMaterial({ color: 0xff6b6b }));
  cap.position.y = 1.7;
  const spout = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.22, 8), standMat);
  spout.position.y = 0.66;
  bottle.add(bottleBody, cap, spout);
  bottle.position.set(4.6, 0, -3.5);
  scene.add(bottle);

  // ============================================================
  //  Hamster factory (cute low-poly critter)
  // ============================================================
  const hamsterColors = [0xf6c177, 0xc98a5b, 0xf0e0d0, 0xb0a090, 0xf4a460];

  function createHamster(furColor) {
    const h = new THREE.Group();
    const fur = new THREE.MeshStandardMaterial({ color: furColor, flatShading: true, roughness: 0.9 });
    const bellyMat = new THREE.MeshStandardMaterial({ color: 0xfff5e6, flatShading: true, roughness: 0.9 });
    const darkMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, flatShading: true });
    const pinkMat = new THREE.MeshStandardMaterial({ color: 0xff9aa2, flatShading: true });

    const body = new THREE.Mesh(new THREE.SphereGeometry(0.42, 8, 6), fur);
    body.scale.set(1.35, 1.05, 1.1); body.position.y = 0.42; body.castShadow = true;
    h.add(body);

    const belly = new THREE.Mesh(new THREE.SphereGeometry(0.33, 8, 6), bellyMat);
    belly.scale.set(1.2, 0.9, 1.0); belly.position.set(0.06, 0.34, 0);
    h.add(belly);

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 6), fur);
    head.position.set(0.55, 0.56, 0); head.castShadow = true;
    h.add(head);

    const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.13, 6, 6), pinkMat);
    cheekL.position.set(0.62, 0.46, 0.16);
    const cheekR = cheekL.clone(); cheekR.position.z = -0.16;
    h.add(cheekL, cheekR);

    const earGeo = new THREE.SphereGeometry(0.1, 6, 6);
    const earL = new THREE.Mesh(earGeo, fur); earL.scale.set(1, 1, 0.5); earL.position.set(0.46, 0.82, 0.16);
    const earR = earL.clone(); earR.position.z = -0.16;
    h.add(earL, earR);

    const eyeGeo = new THREE.SphereGeometry(0.055, 6, 6);
    const eyeL = new THREE.Mesh(eyeGeo, darkMat); eyeL.position.set(0.78, 0.61, 0.15);
    const eyeR = eyeL.clone(); eyeR.position.z = -0.15;
    h.add(eyeL, eyeR);
    const shineMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const sL = new THREE.Mesh(new THREE.SphereGeometry(0.018, 4, 4), shineMat); sL.position.set(0.8, 0.63, 0.16);
    const sR = sL.clone(); sR.position.z = -0.16;
    h.add(sL, sR);

    const nose = new THREE.Mesh(new THREE.SphereGeometry(0.045, 6, 6), pinkMat);
    nose.position.set(0.84, 0.52, 0);
    h.add(nose);

    const legGeo = new THREE.CylinderGeometry(0.055, 0.05, 0.18, 6);
    const legs = [];
    const legPos = [[0.28, 0.09, 0.22], [0.28, 0.09, -0.22], [-0.28, 0.09, 0.22], [-0.28, 0.09, -0.22]];
    for (const p of legPos) {
      const leg = new THREE.Mesh(legGeo, pinkMat);
      leg.position.set(p[0], p[1], p[2]); leg.castShadow = true;
      h.add(leg); legs.push(leg);
    }

    const tail = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 6), pinkMat);
    tail.position.set(-0.55, 0.42, 0);
    h.add(tail);

    h.userData = { legs, head, body, baseScale: body.scale.clone() };
    return h;
  }

  // ---- Spawn a little colony ----
  const hamsters = [];
  const B = { minX: -4.3, maxX: 4.3, minZ: -4.3, maxZ: 4.3 };

  for (let i = 0; i < 5; i++) {
    const mesh = createHamster(hamsterColors[i % hamsterColors.length]);
    mesh.position.set((Math.random() - 0.5) * 6, 0, (Math.random() - 0.5) * 6);
    scene.add(mesh);
    hamsters.push({
      mesh, legs: mesh.userData.legs, head: mesh.userData.head, body: mesh.userData.body,
      baseScale: mesh.userData.baseScale.clone(),
      state: 'idle', timer: Math.random() * 3,
      facing: Math.random() * Math.PI * 2,
      speed: 1.1 + Math.random() * 0.8,
      bobPhase: Math.random() * Math.PI * 2,
      target: new THREE.Vector3((Math.random() - 0.5) * 6, 0, (Math.random() - 0.5) * 6),
      interactTarget: null, interactTimer: 0
    });
  }

  // ---- Autonomous behaviour ----
  function updateHamster(s, dt) {
    const m = s.mesh;
    s.bobPhase += dt * 8;

    // always breathing
    s.body.scale.copy(s.baseScale);
    s.body.scale.y *= 1 + 0.03 * Math.sin(s.bobPhase);

    if (s.state === 'idle') {
      s.timer -= dt;
      m.rotation.y = s.facing;
      if (Math.random() < 0.012) s.facing += (Math.random() - 0.5) * 1.4; // look around
      if (s.timer <= 0) {
        const r = Math.random();
        if (r < 0.32) {                     // go ride the wheel
          s.state = 'walking';
          s.target.copy(wheelPos);
          s.interactTarget = 'wheel';
        } else if (r < 0.58) {              // go snack at the bowl
          s.state = 'walking';
          s.target.copy(foodPos).add(new THREE.Vector3(0, 0, 0.55));
          s.interactTarget = 'food';
        } else {                            // wander
          s.state = 'walking';
          s.target.set(
            THREE.MathUtils.clamp((Math.random() - 0.5) * 8, B.minX, B.maxX),
            0,
            THREE.MathUtils.clamp((Math.random() - 0.5) * 8, B.minZ, B.maxZ)
          );
          s.interactTarget = null;
        }
        s.timer = 1.5 + Math.random() * 2.5;
      }
    }

    else if (s.state === 'walking') {
      const dx = s.target.x - m.position.x;
      const dz = s.target.z - m.position.z;
      const dist = Math.hypot(dx, dz);
      if (dist > 0.06) {
        const nx = dx / dist, nz = dz / dist;
        m.position.x += nx * s.speed * dt;
        m.position.z += nz * s.speed * dt;
        s.facing = Math.atan2(-nz, nx);     // model faces +X
        for (let i = 0; i < s.legs.length; i++) {
          s.legs[i].rotation.x = Math.sin(s.bobPhase + (i % 2) * Math.PI) * 0.6;
        }
        m.position.y = Math.abs(Math.sin(s.bobPhase)) * 0.03;
      } else {
        // arrived
        if (s.interactTarget === 'wheel') {
          m.position.set(wheelPos.x, 0.4, wheelPos.z);
          s.facing = 0;                     // face along the axle
        } else if (s.interactTarget === 'food') {
          m.position.set(s.target.x, 0.3, s.target.z);
          s.facing = Math.atan2(-(foodPos.z - m.position.z), (foodPos.x - m.position.x));
        }
        if (s.interactTarget) {
          s.state = 'interacting';
          s.interactTimer = 3 + Math.random() * 3;
        } else {
          s.state = 'idle';
          s.timer = 1 + Math.random() * 2.5;
        }
      }
      m.position.x = THREE.MathUtils.clamp(m.position.x, B.minX, B.maxX);
      m.position.z = THREE.MathUtils.clamp(m.position.z, B.minZ, B.maxZ);
    }

    else if (s.state === 'interacting') {
      s.interactTimer -= dt;
      if (s.interactTarget === 'wheel') {
        wheel.rotation.x += dt * 4.5;
        m.position.y = 0.4 + Math.abs(Math.sin(s.bobPhase)) * 0.03;
      } else {
        m.position.y = Math.abs(Math.sin(s.bobPhase * 1.6)) * 0.045; // nibbling
        s.head.rotation.x = 0.25 * Math.sin(s.bobPhase * 1.6);      // head nod
      }
      for (let i = 0; i < s.legs.length; i++) {
        s.legs[i].rotation.x = Math.sin(s.bobPhase + (i % 2) * Math.PI) * 0.9;
      }
      if (s.interactTimer <= 0) {
        s.state = 'idle';
        s.timer = 1 + Math.random() * 2.5;
        s.interactTarget = null;
        s.head.rotation.x = 0;
        // hop away from the wheel
        s.target.set(
          THREE.MathUtils.clamp(m.position.x + (Math.random() - 0.5) * 3, B.minX, B.maxX),
          0,
          THREE.MathUtils.clamp(m.position.z + 1.6, B.minZ, B.maxZ)
        );
      }
    }
  }

  // ============================================================
  //  Render loop
  // ============================================================
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  const clock = new THREE.Clock();
  (function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    for (const s of hamsters) updateHamster(s, dt);
    controls.update();
    renderer.render(scene, camera);
  })();
  </script>
</body>
</html>
```

## What's inside

**Scene contents**
- A wooden **tray** with low lips, covered in sawdust **bedding**, surrounded by translucent **glass walls** with a metal frame.
- Five hand-built **low-poly hamsters** (body, belly, head, floppy ears, shiny eyes, pink cheeks/nose/feet/tail), each in a different color.
- Interactive **exercise wheel** (spins when a hamster rides it), an interactive **food bowl** (hamsters stop to nibble pellets), plus a **tunnel**, a little **sleeping hut**, and a **water bottle** for flavor.

**Autonomous hamster AI** — each critter cycles through three states:
- **Idle** – pauses, breathes, and randomly glances around.
- **Walking** – picks a target (random spot, the wheel, or the food bowl), walks there with animated alternating legs and a little body bob, and turns to face its direction of travel.
- **Interacting** – rides the wheel (making it spin) or nibbles at the food bowl (with a head-nodding motion), then hops off to do something else.

**Interaction** — `OrbitControls` lets you drag to rotate, scroll to zoom, and right-drag to pan, so you can watch from any angle.

Just open the file in Chrome/Firefox/Safari/Edge and enjoy the hamsters. 🐹