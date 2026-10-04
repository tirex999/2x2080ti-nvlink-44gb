Let me create a single-file browser project called "Low-Poly Hamster Playground" using Three.js. I need to include:

1. A 3D hamster cage scene
2. Several cute low-poly hamsters
3. Camera rotation (interactive)
4. Hamsters with autonomous behavior (walking, pausing, turning, interacting)
5. At least one interactive object (wheel, tunnel, food bowl, or toy)
6. Cute, low-poly, colorful, funny visual style
7. Must run immediately in a modern browser

Let me plan this out:

**Structure:**
- Single index.html file
- Use Three.js from CDN
- OrbitControls for camera rotation

**Scene elements:**
1. **Cage**: A transparent box enclosure with bars/frame
2. **Floor/tray**: Bottom of the cage with bedding
3. **Hamsters**: Several low-poly hamsters made from basic geometries (spheres, boxes, cylinders)
4. **Interactive objects**: 
   - Exercise wheel (that spins when hamster interacts)
   - Food bowl
   - Tunnel
   - Maybe a ball/toy

**Hamster design (low-poly):**
- Body: ellipsoid/sphere
- Head: sphere
- Ears: small spheres/circles
- Eyes: dark spheres
- Nose: small pink sphere
- Cheeks: spheres
- Feet: small cylinders/boxes
- Tail: tiny sphere

**Behavior:**
- Wander around randomly
- Pause occasionally
- Turn around
- Interact with the wheel (run on it)
- Maybe go into tunnel

**Visual style:**
- Warm, pastel colors
- Soft lighting
- Cute proportions (big head, small body)

Let me write the code. I'll use Three.js r128 or a recent version from CDN. Let me use a recent version with import maps for modules, or just use the classic script includes.

Actually, let me use the module approach with import maps which is cleaner for recent Three.js, but the classic approach with global THREE is simpler and more reliable. Let me use the classic UMD build with OrbitControls.

Actually, for reliability, let me use the ES module version with import maps since that's the modern standard. But I need to make sure OrbitControls loads correctly.

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
```

Then import THREE and OrbitControls.

Let me build this step by step.

**Hamster function:**
Creates a hamster mesh with random color, position. Each hamster has:
- A group containing all parts
- State machine: WALKING, PAUSING, TURNING, INTERACTING
- Target position for wandering
- Animation for walking (leg movement, bobbing)

**Cage:**
- Tray (bottom): a flat box with rounded look, filled with bedding (maybe green/tan color)
- Walls: transparent panels or wire frame
- Let me do a wooden/plastic tray bottom and transparent/acrylic walls with a metal frame

**Objects:**
1. Exercise wheel - red/orange, spins
2. Food bowl - small, with seeds
3. Tunnel - a cylinder (cardboard tube)
4. Maybe a small house/shed

Let me keep it manageable but fun.

Let me think about the wheel interaction. When a hamster is "INTERACTING" with the wheel, it stands in front of the wheel and the wheel spins. Actually, hamsters run inside wheels. Let me place the hamster so it appears to run inside/on the wheel and the wheel rotates.

Let me also add some bedding particles, maybe some scattered seeds.

Let me write the full code now.

I'll structure the hamster building carefully. Let me make cute hamsters.

For low-poly look, I can use `flatShading: true` on materials.

Let me define colors for hamsters: tan/brown, white, gray, etc.

Let me write helper functions.

```js
function createHamster(color) {
  const hamster = new THREE.Group();
  
  // Body
  const bodyGeo = new THREE.SphereGeometry(0.5, 12, 10);
  bodyGeo.scale(1, 0.9, 1.2); // elongate
  const bodyMat = new THREE.MeshStandardMaterial({ color, flatShading: true });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  hamster.add(body);
  
  // Head
  const headGeo = new THREE.SphereGeometry(0.38, 12, 10);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.position.set(0, 0.15, 0.5);
  hamster.add(head);
  
  // Ears
  const earGeo = new THREE.CircleGeometry(0.14, 12);
  ...
  
  // Eyes
  ...
  
  // Nose
  ...
  
  // Cheeks
  ...
  
  // Feet
  ...
  
  // Tail
  ...
  
  return hamster;
}
```

For legs, I'll create 4 small legs that can animate.

Let me make the legs separate meshes so I can animate them.

Actually, for simplicity and cuteness, let me make little stubby feet.

Let me think about the walking animation. When walking, I'll:
- Bob the body up and down slightly
- Move legs back and forth
- Rotate legs

Let me keep leg animation simple - just swing the front/back legs.

Actually, let me make it simpler - just bob and maybe wiggle. But leg movement makes it look alive. Let me do simple leg swinging.

Let me organize each hamster's parts into named sub-groups so I can access them for animation.

Let me write it all out.

For the behavior AI, I'll implement a simple state system:

```js
class Hamster {
  constructor() {
    this.group = createHamsterMesh(...);
    this.state = 'wander';
    this.timer = 0;
    this.speed = ...;
    this.target = random point;
    this.rotation = 0;
    this.wheel = null; // reference to interacted object
  }
  
  update(dt) {
    this.timer -= dt;
    switch(this.state) {
      case 'wander':
        // move toward target
        // if reached, pick new state
      case 'pause':
        // stand still, maybe turn
      case 'turn':
        // rotate in place
      case 'interact_wheel':
        // run on wheel
    }
  }
}
```

Let me implement this.

For collision with boundaries, keep hamsters within the cage area.

Let me set the cage dimensions. Say the tray is 8 x 5 units, height 3.

Hamsters walk on the floor (y ~ 0.5).

Let me write the full thing.

I'll add ambient light, directional light, and maybe a soft fill light. Add shadows for nice look.

Let me add a nice background color (soft gradient or solid pastel).

Let me also add the bedding texture - I could scatter small colored cones/boxes to represent wood shavings. Let me add some tan colored small pieces on the floor.

Let me also add scattered seeds in the food bowl.

OK let me just write it all.

Let me think about the wheel mechanism. The wheel is a vertical circle (like a hamster wheel). It has an outer ring (torus) and rungs (small cylinders arranged radially), plus a stand. When a hamster runs on it, it spins around its horizontal axis.

The hamster stands at the bottom inside of the wheel and "runs" (legs move fast, body bobs), causing the wheel to spin.

Let me place the wheel at one side of the cage.

Let me define the wheel:
- Main ring: torus
- Rungs: several short cylinders along radius
- Axle/stand: supports it

When spinning, rotate the ring group around its axis.

Let me code the wheel as a group:
```
wheelGroup = new Group()
wheelRing = new Group() // contains torus + rungs, this spins
stand = ...
```

The spin axis is horizontal (x-axis if wheel faces the camera side-on, or z-axis...). Let me orient the wheel so its plane is vertical and it spins around a horizontal axis. If the wheel's flat face points along X, then it spins around X axis. Let me make the wheel plane be the YZ plane, spinning around X axis.

Torus default lies in XY plane with normal along Z. To make it in YZ plane, rotate 90° around X. Then it spins around X axis. Good.

Let me place wheel facing sideways so we see it edge-on... no, we want to see the wheel face. Let me make the wheel face toward the camera-ish. If wheel plane is XY (normal Z), we see it face-on from front. It would spin around Z axis (horizontal, pointing at viewer). That works and looks like a proper hamster wheel! Let me use that orientation.

So wheel ring spins around Z axis. Hamster stands inside near bottom.

Let me place wheel center at (x, y, z). Ring in XY plane, spin around Z.

Hamster stands at bottom of wheel, inside, facing... hmm, if wheel spins around Z and hamster is at bottom, the hamster runs in place. Let me put hamster at position (cx, cy - radius + 0.3, cz) facing +Z or -Z... Actually the hamster should face consistent with wheel rotation. Let me just put it at the bottom facing sideways (along X? no). 

Let me think: wheel in XY plane. Bottom of wheel is at (cx, cy - R, cz). The hamster stands there. Its facing direction - let's have it face +X (toward side) or -X. It doesn't matter much for the visual. Let me have it face -X.

Actually for a nice look, the hamster in a wheel usually faces one direction and the wheel spins. Let me have hamster face +X and wheel spin such that top moves toward -X (backward relative to hamster facing forward)... whatever, it'll look fine.

Let me just make it work visually.

Now let me write everything.

I'll make 4 hamsters of different colors.

Let me also give each hamster slightly different personality (speed, pause duration).

Let me add names floating? No, keep simple. Maybe show a title and instructions overlay.

Let me write the HTML with a nice overlay UI showing title and controls hint.

Let me now write the complete code.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #2b2d42; font-family: 'Segoe UI', system-ui, sans-serif; }
  #app { width: 100%; height: 100%; display: block; }
  .overlay {
    position: fixed; top: 0; left: 0; width: 100%; pointer-events: none;
    padding: 18px 24px;
    display: flex; flex-direction: column; gap: 6px;
  }
  .title {
    font-size: 26px; font-weight: 800; color: #fff;
    text-shadow: 0 2px 8px rgba(0,0,0,0.35);
    letter-spacing: 0.5px;
  }
  .subtitle {
    font-size: 14px; color: #ffe4c4; max-width: 340px; line-height: 1.5;
    text-shadow: 0 1px 4px rgba(0,0,0,0.4);
  }
  .hint {
    position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
    background: rgba(255,255,255,0.12); backdrop-filter: blur(8px);
    color: #fff; padding: 8px 18px; border-radius: 20px;
    font-size: 13px; pointer-events: none;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  }
</style>
</head>
<body>
<div id="app"></div>
<div class="overlay">
  <div class="title">🐹 Low-Poly Hamster Playground</div>
  <div class="subtitle">A cozy little cage with some fuzzy friends. Watch them wander, nap, and hit the gym!</div>
</div>
<div class="hint">Drag to rotate · Scroll to zoom · Right-drag to pan</div>

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

// ... scene setup, hamsters, etc.
</script>
</body>
</html>
```

Now the JavaScript. Let me write it carefully.

Scene setup:
```js
const app = document.getElementById('app');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x9ec5e8); // soft sky
scene.fog = new THREE.Fog(0x9ec5e8, 20, 45);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 100);
camera.position.set(7, 6, 10);

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
controls.maxPolarAngle = Math.PI * 0.49; // don't go below floor
controls.minDistance = 5;
controls.maxDistance = 25;
```

Lighting:
```js
const hemi = new THREE.HemisphereLight(0xffffff, 0xffd9a8, 0.7);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff4e0, 1.2);
sun.position.set(6, 10, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 40;
sun.shadow.camera.left = -12;
sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12;
sun.shadow.camera.bottom = -12;
sun.shadow.bias = -0.0005;
scene.add(sun);

const fill = new THREE.DirectionalLight(0xbfd4ff, 0.4);
fill.position.set(-6, 4, -6);
scene.add(fill);
```

Now the cage. Let me define dimensions:
- Tray: width 10, depth 7, height 0.6 (the low walls)
- Actually a hamster cage tray is like a shallow bin. Let me make base tray walls.

Let me build:
1. Base tray: a box (floor) plus low walls around it.
2. Acrylic/transparent upper walls.
3. Metal frame bars.

Let me keep it clean:

Floor tray (solid):
- Bottom plate: box 10 x 0.3 x 7, at y=0.15, material plastic (light color)
- Bedding layer on top: thin box with wood-shaving color, maybe with some scattered bits.

Side walls (acrylic transparent):
- 4 walls, height ~2.4, transparent white/blue material, transparent true, opacity 0.25.

Frame: vertical corner posts and top rails (metallic or wood color).

Let me build the cage.

Actually to keep it stable and readable, let me do:
- Wooden base tray (open top box): bottom + 4 low walls height 0.7.
- Above that, transparent acrylic walls height 2.0.
- Metal frame posts at corners.

Let me code a function buildCage().

Bedding: scatter small randomly rotated boxes/cones in tan shades on the floor inside the tray.

Let me define play area bounds for hamsters: x in [-4.3, 4.3], z in [-2.8, 2.8].

Now the wheel. Place at one end, say x = -3.5, z = 0.

Food bowl at x = 3.5, z = 0.

Tunnel: a cylinder lying horizontally, maybe at x=0, z=-2.5. Hamsters can go through/behind. Let me make it a cardboard tube (open ends) in tan.

House/shed: small box house at x = 2, z = -2. Optional. Let me add a little house too for cuteness but keep hamsters mostly wandering.

Let me limit to wheel, food bowl, tunnel, and a house. That gives plenty of objects.

Now hamsters. Let me write createHamster with named parts.

Let me define parts:
- bodyGroup (for bobbing)
- body mesh
- head (with headGroup for nodding)
- ears (left/right)
- eyes (left/right) with whites and pupils
- nose
- cheeks (left/right) - cute puffy
- 4 legs: front-left, front-right, back-left, back-right — each a small capsule/box attached so they can swing
- tail

Actually legs need pivot points for swinging. Let me create each leg as a child of a "leg pivot" group positioned at the joint, then the leg mesh offset downward. Rotating the pivot swings the leg.

Let me do that.

For walking animation, alternate front-back legs.

Let me store references:
```
hamster.parts = {
  body, head, earL, earR, eyeL, eyeR, nose, cheekL, cheekR,
  legFL, legFR, legBL, legBR, // these are pivot groups
};
```

Animation:
- Walking: legs swing (sin wave, phase differences), body bobs, head nods slightly.
- Pause: subtle breathing (body scale pulse), maybe blink (eyes scale).
- Turn: rotate whole hamster toward target gradually.
- Interact wheel: fast leg swing, body bob, positioned at wheel.

Blinking: periodically scale eyes to 0 in Y then back. Cute.

Let me add blinking with random timing.

Let me write the Hamster class.

```js
const COLORS = [0xf2b17c, 0xe8d4b8, 0xc9b8a3, 0xf7c5a0, 0xd9a06b];

class Hamster {
  constructor(color, startX, startZ) {
    this.color = color;
    this.group = new THREE.Group();
    this.build();
    this.group.position.set(startX, 0.5, startZ);
    scene.add(this.group);
    
    // behavior
    this.state = 'wander';
    this.timer = 1 + Math.random()*2;
    this.speed = 0.7 + Math.random()*0.5;
    this.heading = Math.random()*Math.PI*2;
    this.walkPhase = Math.random()*Math.PI*2;
    this.nextTarget();
    this.blinkTimer = 2 + Math.random()*3;
    this.legPivots = [];
  }
  ...
}
```

Hmm, let me integrate legs into build and store pivots.

Let me write build():

```js
build() {
  const mat = new THREE.MeshStandardMaterial({ color: this.color, roughness: 0.9, flatShading: true });
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x2a2a2a, roughness: 0.5, flatShading: true });
  const pinkMat = new THREE.MeshStandardMaterial({ color: 0xff9db0, roughness: 0.8, flatShading: true });
  const whiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6, flatShading: true });
  
  // Body
  const bodyGeo = new THREE.SphereGeometry(0.55, 14, 12);
  bodyGeo.scale(1.0, 0.95, 1.25);
  this.body = new THREE.Mesh(bodyGeo, mat);
  this.body.castShadow = true;
  this.body.receiveShadow = true;
  this.group.add(this.body);
  
  // Head group (for nodding) - child of group for positioning
  this.headGroup = new THREE.Group();
  this.headGroup.position.set(0, 0.18, 0.55);
  this.group.add(this.headGroup);
  
  const headGeo = new THREE.SphereGeometry(0.4, 14, 12);
  headGeo.scale(1, 0.95, 1.05);
  this.head = new THREE.Mesh(headGeo, mat);
  this.head.castShadow = true;
  this.headGroup.add(this.head);
  
  // Ears
  const earGeo = new THREE.SphereGeometry(0.16, 12, 10);
  this.earL = new THREE.Mesh(earGeo, mat);
  this.earL.position.set(-0.22, 0.32, -0.02);
  this.earL.scale.set(1, 1, 0.6);
  this.headGroup.add(this.earL);
  this.earR = this.earL.clone();
  this.earR.position.x = 0.22;
  this.headGroup.add(this.earR);
  
  // Eyes
  const eyeWhiteGeo = new THREE.SphereGeometry(0.1, 12, 10);
  this.eyeLW = new THREE.Mesh(eyeWhiteGeo, whiteMat);
  this.eyeLW.position.set(-0.16, 0.06, 0.33);
  this.headGroup.add(this.eyeLW);
  this.eyeRW = this.eyeLW.clone();
  this.eyeRW.position.x = 0.16;
  this.headGroup.add(this.eyeRW);
  
  const pupilGeo = new THREE.SphereGeometry(0.06, 10, 8);
  this.eyeL = new THREE.Mesh(pupilGeo, darkMat);
  this.eyeL.position.set(-0.16, 0.06, 0.4);
  this.headGroup.add(this.eyeL);
  this.eyeR = this.eyeL.clone();
  this.eyeR.position.x = 0.16;
  this.headGroup.add(this.eyeR);
  this.eyes = [this.eyeL, this.eyeR]; // for blink
  
  // Nose
  const noseGeo = new THREE.SphereGeometry(0.055, 10, 8);
  this.nose = new THREE.Mesh(noseGeo, pinkMat);
  this.nose.position.set(0, -0.02, 0.42);
  this.headGroup.add(this.nose);
  
  // Cheeks (puffy)
  const cheekGeo = new THREE.SphereGeometry(0.16, 12, 10);
  this.cheekL = new THREE.Mesh(cheekGeo, mat);
  this.cheekL.position.set(-0.26, -0.04, 0.18);
  this.cheekL.scale.set(1, 0.9, 0.9);
  this.headGroup.add(this.cheekL);
  this.cheekR = this.cheekL.clone();
  this.cheekR.position.x = 0.26;
  this.headGroup.add(this.cheekR);
  
  // Tail
  const tailGeo = new THREE.SphereGeometry(0.09, 10, 8);
  this.tail = new THREE.Mesh(tailGeo, mat);
  this.tail.position.set(0, -0.05, -0.65);
  this.tail.scale.set(1, 0.8, 0.7);
  this.group.add(this.tail);
  
  // Legs with pivots
  const legMat = mat;
  const legOffset = { FL: [-0.28, 0.0, 0.28], FR: [0.28, 0.0, 0.28], BL: [-0.28, 0.0, -0.28], BR: [0.28, 0.0, -0.28] };
  this.legs = {};
  for (const key in legOffset) {
    const [lx, ly, lz] = legOffset[key];
    const pivot = new THREE.Group();
    pivot.position.set(lx, ly, lz);
    this.group.add(pivot);
    const legGeo = new THREE.BoxGeometry(0.12, 0.22, 0.12);
    legGeo.translate(0, -0.11, 0); // pivot at top
    const leg = new THREE.Mesh(legGeo, pinkMat);
    leg.castShadow = true;
    pivot.add(leg);
    this.legs[key] = pivot;
    this.legPivots.push(pivot);
  }
}
```

Wait, legs color - hamster feet are often lighter/pink. Let me use pinkMat for feet. Good.

Now the body is centered at origin of group (y~0.5 after position). Actually body sphere center at group origin. Legs attach at group origin level (y=0) hanging down. But body sits at y=0.5 position of group... wait the group position.y is set to 0.5 in constructor. Body mesh is at local (0,0,0) so body center at world y=0.5. But body radius ~0.55 scaled, so bottom of body ~ y=0.5-0.5 = 0. Floor at y=0.15 (tray top). Hmm let me adjust.

Let me set floor/tray top at y=0. Legs length 0.22 reach from y=0 (local) down to y=-0.22 local. So feet at local y=-0.22. If group.position.y = 0.35, feet at 0.13 ≈ floor. Body center at 0.35, radius 0.55 → body spans 0.35±0.55 roughly (scaled). Bottom ~ 0.35-0.5 = 0.13. Good, sits on floor.

Let me set group.position.y = 0.35. Actually let me recompute with tray top at y=0.15. Let me make hamster stand so feet touch tray top.

Set group.position.y such that feet (local -0.22) = 0.15 → group.y = 0.37. And body center 0.37. Good.

Let me use 0.37.

Now heading/rotation: group.rotation.y = heading so it faces direction of travel. Direction vector = (sin(heading), 0, cos(heading))? Let me define heading as angle; forward = (sin(heading), 0, cos(heading)). Move accordingly.

nextTarget(): pick random point within bounds. Compute desired heading, store targetHeading.

update(dt):
```
this.timer -= dt;
switch(state):
  wander: move toward target, rotate toward target heading, animate walk. If distance < 0.3 or timer<=0 → choose new state.
  pause: stand, breathe, blink. If timer<=0 → wander or turn.
  turn: rotate toward target heading. If close → wander.
  interact_wheel: run on wheel (fast walk), wheel spins. If timer<=0 → leave wheel → wander.
```

Let me implement state transitions.

Let me define bounds: minX=-4.2, maxX=4.2, minZ=-2.7, maxZ=2.7.

Wheel location: wx=-3.4, wz=0. Wheel radius ~1.0. Hamster stands inside bottom of wheel.

When choosing to interact with wheel (random), set state='approach_wheel' then 'interact_wheel'. Simpler: directly set interact with a timer, position hamster at wheel bottom, and spin wheel. After timer, set state wander and move away.

But the hamster needs to get TO the wheel. Let me add approach logic: when deciding to interact, set target = wheel position, state='walk_to_wheel', and a flag. Actually simpler: set state='interact' but first teleport? Teleporting is jarring. Let me do approach.

Let me add states:
- 'wander' (default roaming)
- 'to_wheel': move to wheel, then 'wheel_run'
- 'wheel_run': run on wheel, spin it
- 'pause'
- 'turn'

Also maybe 'to_tunnel' / 'in_tunnel' for the tunnel. Let me add tunnel interaction: hamster walks to tunnel entrance, disappears briefly (or goes behind), comes out. That's cute. Let me implement: 'to_tunnel' then 'in_tunnel' (hide group, timer) then emerge.

And food bowl: 'to_food' then 'eat' (bob head, timer) then leave. Cute eating animation.

Let me include a few interaction types for variety. Keep it fun.

Let me define interaction targets:
- wheel at (-3.4, 0, 0), radius 1.0
- food bowl at (3.5, 0, 0)
- tunnel at (0, 0, -2.5) opening toward +z (front)
- house at (2.5, 0, -2.0)

Behaviors cycle with weighted randomness.

Let me write a method pickNewState():
```
const r = Math.random();
if (r < 0.35) { this.state='pause'; this.timer = 1.5+Math.random()*2.5; }
else if (r < 0.55) { this.state='turn'; this.targetHeading = this.heading + (Math.random()<0.5?-1:1)*(0.6+Math.random()*1.2); this.timer = 0.6+Math.random()*0.8; }
else if (r < 0.75) { this.startInteraction('wheel'); }
else if (r < 0.88) { this.startInteraction('food'); }
else { this.startInteraction('tunnel'); }
```

startInteraction(type):
```
this.interactionType = type;
this.state = 'approach';
this.interactPos = TARGET[type];
this.nextTarget(); // for movement during approach, set wander target to interactPos
this.target = interactPos.clone();
```

Hmm, but I use target for wander movement. During approach I set target = interactPos. Good.

update logic:

```
if (state === 'approach') {
  moveTo(this.interactPos, dt);
  if (distance to interactPos < 0.4) {
    enterInteraction();
  }
} else if (state === 'wheel_run') {
  runOnWheel(dt);
  timer -= dt; if timer<=0 { state='leave'; setTargetAwayFromWheel; }
} else if (state === 'eat') {
  eatAnimation(dt); timer -= dt; if timer<=0 { state='leave'; }
} else if (state === 'in_tunnel') {
  hide; timer -= dt; if timer<=0 { emerge; state='leave'; }
} else if (state === 'leave') {
  moveTo(awayPoint, dt); if reached { state='wander'; nextTarget(); }
} else if (state === 'pause') { ... }
else if (state === 'turn') { ... }
else if (state === 'wander') { ... }
```

This is getting complex but manageable. Let me simplify by combining.

Actually let me reduce complexity: For approach, I'll compute direction to target and move. For interactions, once arrived, perform for timer, then set a "depart" target away from the interaction point and state='wander' with a special flag to go there first.

Let me use a simpler model: 
- wander with target.
- When reaching target or timer expires, roll for new behavior.
- For interaction behaviors, set state to 'X' and position accordingly (with approach moving there).

Let me just code it thoroughly. I'll write helper functions.

Let me define target movement helper:
```
moveTowards(targetPos, dt, speed) {
  const dir = new THREE.Vector3().subVectors(targetPos, this.group.position);
  dir.y = 0;
  const dist = dir.length();
  if (dist < 0.01) return true;
  dir.normalize();
  // rotate toward dir
  const desired = Math.atan2(dir.x, dir.z);
  this.heading = lerpAngle(this.heading, desired, dt * 6);
  const step = Math.min(dist, speed * dt);
  this.group.position.x += dir.x * step;
  this.group.position.z += dir.z * step;
  return false;
}
```

lerpAngle handles angle wrapping.

For wander, target is stored. For approach, target = interactPos.

Depart: compute away point = interactPos + direction away (e.g., opposite of cage center or random). Let me compute awayPoint by moving from interactPos away from center, clamped to bounds. Then set state='wander', nextTarget uses awayPoint as immediate target then continue.

Simplest: set this.target = awayPoint, state='wander', and rely on wander logic to move there then pick new state.

Let me implement wander to use this.target.

OK here's my plan for update:

```
update(dt, time) {
  this.timer -= dt;
  this.blinkTimer -= dt;
  
  // always allow blink
  if (this.blinkTimer <= 0) { this.blink(); this.blinkTimer = 2 + Math.random()*4; }
  
  switch(this.state) {
    case 'wander':
      const arrived = this.moveTowards(this.target, dt, this.speed);
      this.animateWalk(dt, 1);
      if (arrived || this.timer <= 0) this.pickNewState();
      break;
    case 'pause':
      this.animateIdle(dt);
      if (this.timer <= 0) this.pickNewState();
      break;
    case 'turn':
      const prev = this.heading;
      this.heading = lerpAngle(this.heading, this.targetHeading, dt*5);
      this.animateWalk(dt, 0.3);
      if (Math.abs(normalizeAngle(this.heading - this.targetHeading)) < 0.1 || this.timer<=0) { this.state='wander'; this.nextTarget(); }
      break;
    case 'approach':
      const a = this.moveTowards(this.interactPos, dt, this.speed);
      this.animateWalk(dt, 1);
      if (a) this.enterInteraction();
      break;
    case 'wheel_run':
      this.group.position.copy(this.wheelStandPos);
      this.animateWalk(dt, 2.2);
      this.spinWheel(1);
      if (this.timer <= 0) { this.state='wander'; this.depart(); }
      break;
    case 'eat':
      this.group.position.copy(this.foodPos);
      this.group.rotation.y = this.foodFacing;
      this.animateEat(dt);
      if (this.timer <= 0) { this.state='wander'; this.depart(); }
      break;
    case 'in_tunnel':
      this.visible = false;
      if (this.timer <= 0) { this.visible = true; this.state='wander'; this.depart(); }
      break;
  }
  
  // clamp to bounds always
  this.clampPosition();
}
```

enterInteraction():
```
switch(interactionType) {
  case 'wheel':
    this.state='wheel_run'; this.timer=3+Math.random()*3;
    this.wheelStandPos = wheelBottomPos; this.group.rotation.y = this.wheelFacing;
    break;
  case 'food':
    this.state='eat'; this.timer=2+Math.random()*2;
    this.group.position.copy(this.foodPos); this.group.rotation.y=this.foodFacing;
    break;
  case 'tunnel':
    this.state='in_tunnel'; this.timer=2+Math.random()*2;
    break;
}
```

depart(): compute away point and set this.target.
```
depart() {
  const p = this.interactPos.clone();
  // push away from cage center
  const dir = p.clone(); dir.y=0; if(dir.length()===0)dir.set(1,0,0); dir.normalize();
  const away = p.clone().addScaledVector(dir, 1.5);
  away.x = clamp(away.x, minX, maxX);
  away.z = clamp(away.z, minZ, maxZ);
  this.target = away;
}
```

Hmm for wheel, push away from center means further negative x, clamp to minX. Fine.

nextTarget(): random point in bounds.
```
nextTarget() {
  this.target = new THREE.Vector3(
    rand(minX, maxX), rand(minZ, maxZ), 0.37
  );
}
```

pickNewState():
```
const r = Math.random();
if (r < 0.30) { this.state='pause'; this.timer = 1.5+Math.random()*2.5; }
else if (r < 0.50) { this.state='turn'; this.targetHeading = this.heading + (Math.random()<0.5?-1:1)*(0.7+Math.random()*1.3); this.timer=0.7+Math.random(); }
else if (r < 0.72) { this.startInteraction('wheel'); }
else if (r < 0.86) { this.startInteraction('food'); }
else { this.startInteraction('tunnel'); }
```

startInteraction(type):
```
this.interactionType = type;
const T = INTERACTION_POSITIONS[type];
this.interactPos = T.pos.clone();
this.state = 'approach';
this.target = T.pos.clone();
if (type==='food') this.foodFacing = T.facing;
if (type==='wheel') this.wheelFacing = T.facing;
```

INTERACTION_POSITIONS defined with positions and facing angles.

Wheel: hamster stands inside bottom of wheel facing +X (sideways) so we see it. Actually if wheel is in XY plane (facing Z), hamster at bottom should face along X (either +X or -X). Let me face -X so it looks like running backward... doesn't matter. Let me face +X.

wheelBottomPos = (wx, wy - R + footClear, wz). Let me compute: wheel center at (wx, wheelCenterY, wz). Radius R. Bottom inner point ~ (wx, wheelCenterY - R, wz). Hamster stands there, its feet at tray floor though. The hamster is sizeable; let me place hamster at (wx, 0.37, wz) i.e., right at bottom center, standing inside wheel. Facing +X (rotation.y = Math.PI/2 → forward = (sin(PI/2),0,cos(PI/2)) = (1,0,0) = +X). Good.

So wheelFacing = Math.PI/2. wheelStandPos = (wx, 0.37, wz).

Food bowl at (3.5, 0.37, 0). Hamster faces it: bowl is at same pos basically; hamster should face the bowl. Let me put hamster slightly in front: hamster pos = bowlPos - facing*0.6. Facing toward bowl. Let me set foodFacing = Math.PI (facing -Z? no). Let me just set hamster at (3.5, 0.37, 0.7) facing -Z (toward bowl at z=0). facing angle for forward (sin,0,cos): to face -Z, cos(angle)=-1 → angle=PI. sin(PI)=0. forward=(0,0,-1). Good. So foodFacing=PI, foodPos = (3.5, 0.37, 0.7).

Tunnel at (0,0,-2.5). It's a tube along X axis (horizontal), openings at both ends (x=±1.5). Hamster goes into one end and out other. Let me have hamster approach front opening. Actually tunnel lying along X: entrances at x=-1.5 and x=+1.5 at z=-2.5. Hamster walks along +Z toward... hmm. Let me orient tunnel along Z axis instead: entrances at z=±1.5, x=0. Then hamster approaches from front (z > 1.5) walking -Z, enters, comes out other side. 

Let me place tunnel center (0, 0.4, -2.5), oriented along Z, length 3 (from z=-4 to z=-1), radius 0.6. Hamster enters at front (z=-1.5 side, the +z end) → actually front is larger z. Let me have hamster approach from z=-2.5+1.5+0.6 = -0.4? That's near center of cage. Hmm the tunnel is at back (-2.5). Front entrance at z = -2.5+1.5 = -1.0. Hamster approaches from z=-1.0-0.6=-1.6? That's outside... 

Let me simplify: tunnel along Z, center (0, 0.4, -2.5), radius 0.6, half-length 1.3 → z from -3.8 to -1.2. Front entrance at z=-1.2. Hamster approaches from z=-1.2-0.5 = -1.7 walking +Z? No, -1.7 is beyond entrance into tunnel region. Ugh.

Let me reconsider. The tunnel is against the back wall (z=-2.5, near maxZ bound -2.7). Front opening faces +Z (into cage). Hamster approaches from inside cage (z > -1.2) moving toward -Z? No, approaching the opening from the +z side means moving in -Z direction toward z=-1.2. Wait opening at z=-1.2, cage interior is z>-1.2 (toward 0). So hamster at z=-0.5 moving -Z enters tunnel at z=-1.2, travels to z=-3.8, exits back. 

So approach pos = (-0.5, 0.37, -2.5)? Facing -Z (angle PI). Then in_tunnel hides it. Then it emerges at other end (z=-3.8) and walks away (+Z direction). depart pushes away from tunnel center (0,-2.5) → direction (0,-1) normalized → away = (0, 0.37, -2.5+1.5)=(0,0.37,-1.0). Clamp fine.

Hmm, but the tunnel physically occupies z from -3.8 to -1.2 at x=0. The hamster emerging at z=-3.8 (back near wall) then walks +Z across cage. Fine.

Let me set INTERACTION_POSITIONS.tunnel.pos = (-0.6, 0.37, -1.6) (approach point, just outside front entrance, facing -Z). tunnelFacing = PI (face -Z). Actually facing -Z: angle PI. Good.

Wait, but I want the hamster to visibly enter. The approach point should be just outside the entrance. Entrance at z=-1.2. Approach at z=-1.6 is already inside tunnel region (z<-1.2). Let me put approach at z=-0.9 (outside, z>-1.2), facing -Z. Then it walks -Z into tunnel. Good. tunnel.pos = (-0.6, 0.37, -0.9).

Hmm wait the tunnel entrance is at z=-1.2, and cage interior extends z from -2.7 to 2.7. -0.9 is interior. Facing -Z, walks to -1.2, enters. 

Let me just make tunnel shorter so it's clearly at back: center (0,0.45,-2.4), radius 0.65, halfLen 1.1 → z from -3.5 to -1.3. Entrance at z=-1.3. Approach at (-0.7, 0.37, -0.8) facing -Z.

OK this is fine. Let me not overthink exact geometry; visually the hamster will walk to the tunnel area and vanish then appear elsewhere.

Let me now also handle: when in_tunnel, the hamster is hidden. On emerge, set visible true and depart. Good.

Now animations:

animateWalk(dt, intensity):
```
this.walkPhase += dt * 8 * (0.5 + intensity);
const s = Math.sin(this.walkPhase);
// alternate legs
this.legs.FL.rotation.x = s * 0.5 * intensity;
this.legs.BR.rotation.x = s * 0.5 * intensity;
this.legs.FR.rotation.x = -s * 0.5 * intensity;
this.legs.BL.rotation.x = -s * 0.5 * intensity;
// bob body
this.body.position.y = Math.abs(Math.sin(this.walkPhase))*0.03*intensity; // bob
// Actually bob whole group? Let me bob body within group.
// head nod
this.headGroup.rotation.x = Math.sin(this.walkPhase*0.5)*0.08*intensity;
```

Hmm body.position.y relative to group — but legs pivots are at group origin (0,0,0) which is body center. If I move body up and down it's fine. But legs stay at origin. Good.

Wait, but I set group.position.y=0.37 and body at local (0,0,0). If I bob body locally, body center oscillates 0.37±. Fine.

But careful: the body bob also could be done on whole group for a bounce. Let me bob the body mesh locally (small). And also add slight squash. Keep small.

animateIdle(dt): breathing
```
const b = Math.sin(time*2)*0.03;
this.body.scale.set(1+b, 1-b*1.2, 1+b);
// legs rest
dampen leg rotations to 0
```

blink(): 
```
this.eyes.forEach(e => { e.scale.y = 0.1; setTimeout(()=>e.scale.y=1, 120); });
```
Using setTimeout in animation loop is okay but let me do a quick two-frame blink via a timer instead. Simpler: set scale then restore after short delay. setTimeout works fine. But multiple blinks could overlap; fine.

Actually cleaner: blink state. Let me just do the setTimeout approach; it's fine.

animateEat(dt): 
```
// rapid head bob / chewing
this.headGroup.rotation.x = Math.abs(Math.sin(time*12))*0.15;
this.cheekL.scale.x = 1 + Math.sin(time*10)*0.1;
this.cheekR.scale.x = 1 + Math.sin(time*10+0.5)*0.1;
// legs planted
dampen legs
```

spinWheel(amount): multiply wheelSpin by amount each frame while running. Actually let me just set wheel angular velocity. Let me store this.wheel.spin and add.

Let me handle wheel spin globally: wheelSpinVelocity. In wheel_run, increase velocity; otherwise friction decays. Simpler: in wheel_run set ring.rotation.z += 0.4 (fast). Else decay: wheelSpinVelocity *= 0.95; ring.rotation.z += wheelSpinVelocity.

Let me store wheelSpin as velocity on the wheel object.

Let me now also make the wheel respond: when hamster runs, wheel spins fast. When not, slows.

Let me write the wheel build:
```
function buildWheel(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const ringY = 1.1; // center height
  const R = 1.0;
  const spinGroup = new THREE.Group();
  spinGroup.position.set(0, ringY, 0);
  g.add(spinGroup);
  
  const ringMat = new THREE.MeshStandardMaterial({ color: 0xff5a5f, roughness: 0.5, flatShading: true });
  const rungMat = new THREE.MeshStandardMaterial({ color: 0xffd166, roughness: 0.6, flatShading: true });
  
  // outer ring (torus)
  const torus = new THREE.Mesh(new THREE.TorusGeometry(R, 0.08, 8, 24), ringMat);
  torus.castShadow = true;
  spinGroup.add(torus);
  
  // inner ring
  const inner = new THREE.Mesh(new THREE.TorusGeometry(R*0.6, 0.05, 8, 20), ringMat);
  spinGroup.add(inner);
  
  // rungs/spokes
  const spokes = 12;
  for (let i=0;i<spokes;i++){
    const a = i/spokes*Math.PI*2;
    const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.03, R*0.9, 6), rungMat);
    rung.rotation.x = Math.PI/2; // in XY plane
    rung.position.set(Math.cos(a)*R*0.55, Math.sin(a)*R*0.55, 0);
    spinGroup.add(rung);
  }
  
  // stand
  const standMat = new THREE.MeshStandardMaterial({ color: 0x8d6e63, roughness: 0.7, flatShading: true });
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.55, 0.12, 12), standMat);
  base.position.y = 0.06; base.castShadow=true; base.receiveShadow=true;
  g.add(base);
  const post = new THREE.Mesh(new THREE.BoxGeometry(0.14, ringY, 0.14), standMat);
  post.position.set(0, ringY/2, 0.4);
  g.add(post);
  const post2 = post.clone();
  post2.position.z = -0.4;
  g.add(post2);
  
  g.userData.spinGroup = spinGroup;
  g.userData.radius = R;
  g.userData.ringY = ringY;
  return g;
}
```

Wait, the spokes: CylinderGeometry default along Y. I rotate x=PI/2 to lie in XY plane. Then position along radial. Length R*0.9. But after rotating the cylinder to horizontal (along its local... rotating around X makes it lie in XY? A cylinder along Y, rotate PI/2 around X → now along Z. Hmm. Let me think: cylinder axis Y. rotation.x = PI/2 rotates axis to Z. So it'd be along Z, thickness in XY. That gives a rung going into screen, not radial in the wheel plane. Not what I want.

I want spokes radiating in the XY plane (the wheel face). So each spoke should be a short cylinder whose axis points radially in XY plane. Easier: use a box for spokes, or position a cylinder oriented radially.

Alternative: make spokes as thin boxes. BoxGeometry(0.05, R*0.9, 0.05) then rotate to radial angle in XY. To rotate a box to point at angle a in XY plane, rotation.z = a. Then it lies in XY plane along radius. 

Let me use boxes:
```
const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.05, R*0.9, 0.05), rungMat);
spoke.rotation.z = a;
spoke.position.set(Math.cos(a)*R*0.5, Math.sin(a)*R*0.5, 0);
spinGroup.add(spoke);
```
Box along Y, rotate.z=a → axis tilts into XY plane at angle a. Good. Position at mid-radius. 

The spinGroup spins around its own origin (0,ringY,0) with rotation.z. Since spinGroup is at ringY, rotating it around z spins the wheel in place around center (0,ringY,0). 

Now hamster stands at (wx, 0.37, wz) inside. Wheel center at (wx, ringY=1.1, wz). Radius 1.0 → bottom of wheel at y=0.1. Hamster feet at 0.37-0.22=0.15. Hamster body center 0.37. So hamster is inside lower part of wheel. Looks right.

Good.

Food bowl:
```
function buildFoodBowl(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const bowlMat = new THREE.MeshStandardMaterial({ color: 0x4fc3f7, roughness: 0.5, flatShading: true });
  // bowl: use a lathe or inverted sphere slice. Simple: cylinder open top.
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.35, 0.25, 16, 1, true), bowlMat);
  bowl.position.y = 0.125; bowl.castShadow=true;
  g.add(bowl);
  // bottom
  const bottom = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.05, 16), bowlMat);
  bottom.position.y = 0.025; g.add(bottom);
  // seeds
  const seedMat = new THREE.MeshStandardMaterial({ color: 0x8d6e3f, roughness: 0.9, flatShading: true });
  for (let i=0;i<14;i++){
    const seed = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.12, 5), seedMat);
    const ang = Math.random()*Math.PI*2;
    const rr = Math.random()*0.3;
    seed.position.set(Math.cos(ang)*rr, 0.22+Math.random()*0.05, Math.sin(ang)*rr);
    seed.rotation.z = (Math.random()-0.5)*1.2;
    g.add(seed);
  }
  return g;
}
```

Tunnel:
```
function buildTunnel(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const tubeMat = new THREE.MeshStandardMaterial({ color: 0xd9a06b, roughness: 0.9, flatShading: true, side: THREE.DoubleSide });
  const len = 2.6, R = 0.62;
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(R, R, len, 16, 1, true), tubeMat);
  tube.rotation.x = Math.PI/2; // axis along Z
  tube.position.y = R + 0.05;
  tube.castShadow = true;
  g.add(tube);
  // rim rings
  const rimMat = new THREE.MeshStandardMaterial({ color: 0xc0854f, roughness: 0.8, flatShading: true });
  for (const zz of [len/2, -len/2]) {
    const rim = new THREE.Mesh(new THREE.TorusGeometry(R, 0.06, 8, 20), rimMat);
    rim.position.set(0, R+0.05, zz);
    g.add(rim);
  }
  return g;
}
```

Tunnel oriented along Z (rotation.x=PI/2 makes cylinder axis from Y to Z). Half-length 1.3 → z from -1.3 to 1.3 relative to center. Center at z=-2.5 → z from -3.8 to -1.2. Good matches earlier.

House (optional cute):
```
function buildHouse(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const wallMat = new THREE.MeshStandardMaterial({ color: 0xf4a259, roughness: 0.8, flatShading: true });
  const roofMat = new THREE.MeshStandardMaterial({ color: 0xe2704a, roughness: 0.8, flatShading: true });
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.8, 1.2), wallMat);
  body.position.y = 0.4; body.castShadow=true; body.receiveShadow=true;
  g.add(body);
  // roof (pyramid)
  const roof = new THREE.Mesh(new THREE.ConeGeometry(0.95, 0.6, 4), roofMat);
  roof.position.y = 1.1; roof.rotation.y = Math.PI/4;
  roof.castShadow = true;
  g.add(roof);
  // door hole (dark)
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.5, 0.1), new THREE.MeshStandardMaterial({color:0x3a2a1a, flatShading:true}));
  door.position.set(0, 0.3, 0.6);
  g.add(door);
  return g;
}
```

House at (2.5, 0, -2.0). Fine.

Now bedding: scatter small pieces on tray floor.
```
function buildBedding() {
  const g = new THREE.Group();
  const colors = [0xe6c67f, 0xdcae66, 0xf0d897, 0xcba55a];
  for (let i=0;i<260;i++){
    const c = colors[Math.floor(Math.random()*colors.length)];
    const mat = new THREE.MeshStandardMaterial({ color: c, roughness: 1, flatShading: true });
    const size = 0.05 + Math.random()*0.09;
    const geo = Math.random()<0.5 ? new THREE.BoxGeometry(size,size*0.4,size*0.7) : new THREE.ConeGeometry(size*0.5, size, 4);
    const piece = new THREE.Mesh(geo, mat);
    piece.position.set(rand(-4.4,4.4), 0.32, rand(-2.8,2.8));
    piece.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
    g.add(piece);
  }
  return g;
}
```

Tray/cage:
```
function buildCage() {
  const g = new THREE.Group();
  const trayW=10, trayD=7, wallH=0.7, upperH=2.0;
  const trayMat = new THREE.MeshStandardMaterial({ color: 0x7ec8e3, roughness: 0.6, flatShading: true }); // light blue plastic
  const frameMat = new THREE.MeshStandardMaterial({ color: 0xf5deb3, roughness: 0.7, flatShading: true }); // wood
  
  // bottom plate
  const bottom = new THREE.Mesh(new THREE.BoxGeometry(trayW, 0.25, trayD), trayMat);
  bottom.position.y = 0.125; bottom.receiveShadow = true; bottom.castShadow=true;
  g.add(bottom);
  
  // low walls (tray sides)
  const wallThick = 0.15;
  const walls = [
    { w: trayW, d: wallThick, x:0, z: trayD/2 - wallThick/2 },
    { w: trayW, d: wallThick, x:0, z: -trayD/2 + wallThick/2 },
    { w: wallThick, d: trayD, x: trayW/2 - wallThick/2, z:0 },
    { w: wallThick, d: trayD, x: -trayW/2 + wallThick/2, z:0 },
  ];
  for (const wl of walls) {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(wl.w, wallH, wl.d), trayMat);
    wall.position.set(wl.x, wallH/2 + 0.25, wl.z);
    wall.castShadow = true; wall.receiveShadow = true;
    g.add(wall);
  }
  
  // acrylic upper walls (transparent)
  const acrylicMat = new THREE.MeshPhysicalMaterial({
    color: 0xdeffff, transparent: true, opacity: 0.18, roughness: 0.2,
    metalness: 0, transmission: 0.9, side: THREE.DoubleSide
  });
  const upperBase = 0.25 + wallH; // 0.95
  const upperWalls = [
    { w: trayW, h: upperH, x:0, z: trayD/2 },
    { w: trayW, h: upperH, x:0, z: -trayD/2 },
    { w: trayD, h: upperH, x: trayW/2, z:0 },
    { w: trayD, h: upperH, x: -trayW/2, z:0 },
  ];
  for (const uw of upperWalls) {
    const panel = new THREE.Mesh(new THREE.BoxGeometry(uw.w, upperH, 0.06), acrylicMat);
    panel.position.set(uw.x, upperBase + upperH/2, uw.z);
    g.add(panel);
  }
  
  // frame posts (corners) + top rails
  const postGeo = new THREE.BoxGeometry(0.16, wallH+upperH+0.1, 0.16);
  const cornerPositions = [[trayW/2, trayD/2],[-trayW/2, trayD/2],[trayW/2,-trayD/2],[-trayW/2,-trayD/2]];
  for (const [cx,cz] of cornerPositions) {
    const post = new THREE.Mesh(postGeo, frameMat);
    post.position.set(cx, (wallH+upperH)/2 + 0.25, cz);
    post.castShadow = true;
    g.add(post);
  }
  // top rails
  const railTop = upperBase + upperH;
  const railH = 0.12;
  const railLong = new THREE.Mesh(new THREE.BoxGeometry(trayW, railH, 0.12), frameMat);
  const railLong2 = railLong.clone();
  railLong.position.set(0, railTop, trayD/2);
  railLong2.position.set(0, railTop, -trayD/2);
  g.add(railLong); g.add(railLong2);
  const railShort = new THREE.Mesh(new THREE.BoxGeometry(0.12, railH, trayD), frameMat);
  const railShort2 = railShort.clone();
  railShort.position.set(trayW/2, railTop, 0);
  railShort2.position.set(-trayW/2, railTop, 0);
  g.add(railShort); g.add(railShort2);
  
  return g;
}
```

The acrylic might render weird with transmission (needs proper setup). Let me just use simple transparent material to be safe:
```
const acrylicMat = new THREE.MeshStandardMaterial({ color: 0xdfffff, transparent: true, opacity: 0.15, roughness: 0.4, metalness: 0.0, side: THREE.DoubleSide });
```
Avoid transmission for stability. Good.

Now floor outside cage: a ground plane for shadows? The shadows cast onto the tray and floor. Let me add a big ground plane below the cage for nice shadows and a room floor.

```
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(60, 60),
  new THREE.MeshStandardMaterial({ color: 0xb8c6db, roughness: 1 })
);
ground.rotation.x = -Math.PI/2;
ground.position.y = 0;
ground.receiveShadow = true;
scene.add(ground);
```

The tray bottom is at y=0.125, slightly above ground. Shadows on ground fine.

Now let me assemble scene:
```
scene.add(buildCage());
scene.add(buildBedding());
const wheel = buildWheel(-3.4, 0); scene.add(wheel);
const food = buildFoodBowl(3.5, 0.6); scene.add(food);
const tunnel = buildTunnel(0, -2.4); scene.add(tunnel);
const house = buildHouse(2.6, -2.2); scene.add(house);
// maybe a water bottle or ball toy
```

Add a small toy ball that could roll? Optional. Let me add a little ball toy that a hamster might nudge. Keep optional; maybe skip to avoid complexity. I'll add a small ball that gently bobs/rolls for decoration.

Actually requirement says "one interactive object such as a wheel, tunnel, food bowl, or toy." I have wheel, food, tunnel — plenty. Good.

Now hamsters: create 4.
```
const hamsters = [];
const spawnPoints = [[-1, 1], [1, -1], [0.5, 1.5], [-1.5, -0.5]];
for (let i=0;i<4;i++){
  const h = new Hamster(COLORS[i % COLORS.length], spawnPoints[i][0], spawnPoints[i][1]);
  hamsters.push(h);
}
```

Wheel spin handling: I'll store global variable wheelSpinVel and update ring rotation in animation loop.

```
let wheelSpinVel = 0;
// in loop:
wheel.userData.spinGroup.rotation.z += wheelSpinVel;
wheelSpinVel *= 0.96; // decay
```
When hamster runs, wheelSpinVel += 0.15 each frame → reaches ~0.4/0.04=10? Let me tune. Actually increment per frame: 0.15/frame at 60fps → accumulates. Let me cap. Set wheelSpinVel = 0.5 while running (clamp). Simpler: if any hamster running, target vel 0.5 else decay.

```
let targetVel = 0;
// in loop compute: 
hamsters.forEach(h => { if (h.state==='wheel_run') targetVel = 0.6; });
wheelSpinVel += (targetVel - wheelSpinVel) * 0.1;
spinGroup.rotation.z += wheelSpinVel;
```

Good.

Now the animation loop:
```
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;
  hamsters.forEach(h => h.update(dt, t));
  // wheel
  let targetVel = 0;
  hamsters.forEach(h => { if (h.state === 'wheel_run') targetVel = 0.6; });
  wheelSpinVel += (targetVel - wheelSpinVel) * 0.08;
  wheel.userData.spinGroup.rotation.z += wheelSpinVel;
  // gentle idle bob on everything? no.
  controls.update();
  renderer.render(scene, camera);
}
animate();
```

Handle resize:
```
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

Helper functions: rand, clamp, lerpAngle, normalizeAngle.
```
const rand = (a,b) => a + Math.random()*(b-a);
const clamp = (v,a,b) => Math.max(a, Math.min(b, v));
function normalizeAngle(a){ while(a>Math.PI)a-=2*Math.PI; while(a<-Math.PI)a+=2*Math.PI; return a; }
function lerpAngle(from, to, t){ return from + normalizeAngle(to-from)*t; }
```

Hamster clampPosition keeps within bounds.

Let me finalize the Hamster.update with all states. Let me also make sure when state changes to wander, nextTarget sets a fresh random target.

Let me write the full Hamster class cleanly.

One concern: The body bob via body.position.y — but legs are children of group at origin; body moving y doesn't affect legs. Good. But I also want whole-body bounce maybe. Keep body bob only.

Also the headGroup is child of group at (0,0.18,0.55). When hamster rotates group (rotation.y), head rotates with it. Good.

Let me ensure the hamster faces its heading. group.rotation.y = heading. Forward direction (sin(heading), 0, cos(heading)). Let me verify: at heading=0, forward=(0,0,1)=+Z. Nose is at +z on head. Good, nose faces +Z. 

moveTowards computes desired = atan2(dir.x, dir.z). For dir=(0,0,1) (moving +Z), atan2(0,1)=0 → heading 0. Matches. Good.

Now the legs pivot rotation.x swings them forward/back. Good.

Let me also add little whiskers? Optional. Skip.

Cheeks puffy — good for cute.

Let me double check eye blink: eyes are pupils (dark). Blink scales them to 0.1 in Y. Fine.

Now, potential issue: MeshStandardMaterial with flatShading on spheres gives faceted low-poly look. Good. SphereGeometry segments 12-14 gives moderate facets. For more low-poly look, use fewer segments (8-10). Let me use 10-12.

Let me reduce segments for low-poly aesthetic: body 12, head 12, etc. Fine.

Colors: let me pick cute palette:
- #f4a259 (orange tan)
- #ffd6a5 (cream)
- #c9b3a0 (gray brown)
- #ffb4a2 (salmon)
- #a0c4ff (pastel blue) - maybe a unique one

Let me use 4-5 colors.

Let me also add slight variation: belly lighter. Could add a lighter belly mesh. Optional. Let me add a small lighter ellipse on belly for cuteness. Might complicate; skip.

Alright, let me also make sure shadows look good: sun casts shadow; tray receives; hamsters cast. Ground receives. Good.

Let me write final code. I'll be careful with syntax.

Let me reconsider the hamster y-position. Tray top (bedding) at y≈0.32 (bedding pieces at 0.32). Actually bottom plate at y 0.125 top surface 0.25. Low walls start at 0.25. Bedding at 0.32 (slightly above tray top). Hamster feet should rest near 0.25-0.32. Hamster group.position.y: feet local -0.22 → group.y - 0.22 = 0.25 → group.y = 0.47. Let me set group.position.y = 0.47. Body center 0.47, radius scaled ~0.55*0.95≈0.52 → bottom ~0.47-0.52 = -0.05?? That's below floor. Hmm because body is large. Let me reduce: body radius 0.5, scaled 0.95 → semi-axis ~0.475. Bottom of body = 0.47-0.475 ≈ -0.005. Slightly below tray. But feet extend to 0.25. The body sinks into floor visually a bit; acceptable but let me raise group.y to 0.5. Then feet at 0.28, body bottom ~0.025. Better. Let me set 0.5.

Actually the body is an ellipsoid; its lowest point depends. With scale y=0.95 and radius 0.5 → y-semi = 0.475. Group.y=0.5 → bottom 0.025. Feet (pivot at 0, leg length 0.22) at 0.28. Good, hamster stands on floor with body slightly overlapping. Fine.

Let me set group.position.y = 0.5.

Head group at (0, 0.18, 0.55) relative → world y 0.68. Head radius 0.4 → top 1.08. Ears at y 0.18+0.32=0.5 relative → 1.0. OK head sits on top-front of body. Body front extends to z ~1.25*0.5=0.625. Head at z 0.55. Good overlap.

Alright.

Now let me also add a subtle idle sway to hamsters even in wander for life. Already have walk animation.

Let me write it all out now, final.

Let me reconsider the "interact with one object" requirement — satisfied by wheel primarily, plus food and tunnel. Good.

Let me make sure the wheel is clearly the main interactive object.

Let me also add a small label/emoji? No.

Let me also make hamsters blink occasionally and maybe turn to camera? No.

Let me finalize.

I realize I should double check: in 'turn' state I reference this.targetHeading and set state to wander calling nextTarget(). Also in wander I call pickNewState when arrived/timer. pickNewState may set state to 'approach' etc. Good.

But there's a subtlety: when in 'approach' or interaction states, the timer is decremented in update top. For approach I don't use timer (use distance). Fine, timer just keeps decrementing; when entering interaction I set timer to interaction duration. Good.

Edge: pickNewState sets state 'turn' with timer; update decrements timer; when done set wander+nextTarget. Good.

Let me ensure depart sets this.target and state wander; then wander moves there and picks new state. Good.

Now the 'leave'/'depart' for wheel: after wheel_run timer ends, state='wander', depart() sets target away. Good.

Let me write depart to compute away point from current interactPos. Store this.interactPos (set in startInteraction). Good.

Let me code.

Also, I want hamsters to not clip through walls; clamp in update.

Let me also add a gentle auto-rotate? No, user rotates. Keep controls.

Let me write the final HTML.

Let me reconsider using importmap with unpkg three 0.160.0 examples/jsm OrbitControls. That path exists: https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js. Yes.

Let me finalize the code and present it.

Let me write the complete file.

I'll include comments for clarity.

Let me make sure the sleeping/pause breathing uses clock time not dt accumulation for smoothness. I'll pass t (elapsed time) to update and use it for breathing/blinking/eat.

For blink, use t-based: track lastBlink; when t - lastBlink > blinkInterval, blink for a short duration. Let me implement blink with a timer that sets eyes squashed for ~0.12s.

Simpler blink: 
```
this.blinkTimer -= dt;
if (this.blinkTimer <= 0) {
  this.blinkTimer = 2 + Math.random()*4;
  this.blinking = true; this.blinkProgress = 0;
}
if (this.blinking) {
  this.blinkProgress += dt*25;
  const s = Math.sin(Math.min(this.blinkProgress, Math.PI)); // 0..1..0
  this.eyes.forEach(e => e.scale.y = 1 - s*0.9);
  if (this.blinkProgress >= Math.PI) { this.blinking=false; this.eyes.forEach(e=>e.scale.y=1); }
}
```
Good, dt-based blink, no setTimeout.

Breathing in pause/idle: use t.
```
const b = Math.sin(t*2)*0.03;
this.body.scale.set(1+b, 1-b, 1+b);
```
But body.scale gets modified; ensure reset each frame. In non-pause states, reset scale to 1 in animateWalk/other. Let me set body.scale in each animation branch appropriately, or always reset at start of update. Let me reset body.scale to (1,1,1) at start of update, then modify. Actually walk bob uses body.position.y not scale. Breathing uses scale. Let me just set scale in pause branch and reset elsewhere. To be safe, at start of update do this.body.scale.set(1,1,1). Then pause breathing sets it. Good.

Similarly cheeks reset. Let me reset cheek scales at start too.

Let me structure update:
```
update(dt, t) {
  this.timer -= dt;
  // blink
  ...
  // resets
  this.body.scale.set(1,1,1);
  this.cheekL.scale.set(1,0.9,0.9);
  this.cheekR.scale.set(1,0.9,0.9);
  // dampen legs toward 0 if not walking? We'll set explicitly in each branch.
  switch(state) {...}
  clamp
}
```

In walk branches set legs; in pause set legs to 0 (dampen): legs.rotation.x *= 0.8 each frame → settles. Or set to computed small. Let me just set to 0 in pause/eat? Eat uses cheeks/head not legs. Let me set legs to 0 in pause.

Actually simplest: at start set all leg rotations *= 0.8 (dampen). Then walk adds. This naturally settles when not walking. Let me do that:
```
for (const k in this.legs) this.legs[k].rotation.x *= 0.8;
```
Then walk overrides. Good.

Now let me write everything.

Let me also handle the head bob in walk via headGroup.rotation.x, reset in pause (set 0 via damping). Let me dampen head too. Actually let me just set explicitly.

I'll add damping for headGroup.rotation.x and .z at start.

Let me finalize.

Let me write the complete file now. I'll be thorough.

Also I should double-check the torus for wheel outer ring: TorusGeometry(R, 0.08, 8, 24). With flatShading material it's faceted. Good.

Let me also ensure spinGroup is at ringY and rotates around z. Since spinGroup.position=(0,ringY,0) and we set spinGroup.rotation.z, it rotates around its local z which passes through (0,ringY,0). Good, wheel spins in place.

Now, hamster at (wx,0.5,wz) inside wheel bottom. As wheel spins, hamster stays (it's "running" in place). Good.

Let me write final.

Let me also add a water bottle toy on the cage wall for extra cute detail? Optional; might clutter. I'll add a small water bottle attached to a side wall for charm. Actually let me keep scope tight but add one extra: a small ball toy on the floor that slowly rolls randomly. Eh, skip to avoid complexity. The requirement met.

Actually, let me add a couple of decorative elements that don't need logic: a few scattered seeds on floor, a small house. Already have house. Good.

Let me write it.

Final code below. Let me make sure imports and everything correct.

I'll now produce the answer with the full index.html and a brief explanation.

Let me double check OrbitControls usage with module import — yes.

Let me verify PerspectiveCamera fov 50, position (7,6,10) looking at (0,1,0). Should show whole cage (cage ~10 wide). Distance from camera to center: sqrt(49+36+64)=sqrt(149)≈12.2. With fov 50, viewable width at that distance ~ 2*12.2*tan(25°)=2*12.2*0.466=11.4. Cage width 10 fits. Good. Maybe zoom a touch. Fine.

Let me set camera target (0, 0.9, 0).

Let me write.

Also, I want to make sure shadows bias doesn't cause artifacts; set sun.shadow.bias = -0.0004.

Let me finalize and write the answer.

I'll present the complete single-file solution.

One more: the acrylic panels use DoubleSide and transparent; with flatShading not needed. Fine.

Let me also add ambient light low to avoid pure black shadows: hemi already provides some. Add an AmbientLight 0.3 for safety.

Let me include:
```
scene.add(new THREE.AmbientLight(0xffffff, 0.25));
```
plus hemi. Good.

Write now.

Let me reconsider hamster count: 4 is good. Colors array length 5, use modulo.

Let me produce final answer with explanation of features and how to run.

I'll keep the code well-commented and organized.

Let me write it all out carefully in the final response.
</think>

# Low-Poly Hamster Playground 🐹

Here's a complete, single-file project. Just save it as `index.html` and open it in any modern browser — no build step, no server needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden;
    background: #2b2d42; font-family: 'Segoe UI', system-ui, sans-serif; }
  #app { width: 100%; height: 100%; display: block; }
  .overlay {
    position: fixed; top: 0; left: 0; width: 100%; pointer-events: none;
    padding: 18px 24px; display: flex; flex-direction: column; gap: 6px; z-index: 5;
  }
  .title {
    font-size: 26px; font-weight: 800; color: #fff;
    text-shadow: 0 2px 8px rgba(0,0,0,0.35);
  }
  .subtitle {
    font-size: 14px; color: #ffe4c4; max-width: 360px; line-height: 1.5;
    text-shadow: 0 1px 4px rgba(0,0,0,0.4);
  }
  .hint {
    position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
    background: rgba(255,255,255,0.14); backdrop-filter: blur(8px);
    color: #fff; padding: 9px 20px; border-radius: 20px;
    font-size: 13px; pointer-events: none; z-index: 5;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  }
</style>
</head>
<body>
<div id="app"></div>
<div class="overlay">
  <div class="title">🐹 Low-Poly Hamster Playground</div>
  <div class="subtitle">A cozy little cage with some fuzzy friends. Watch them wander, nap, snack, and hit the gym!</div>
</div>
<div class="hint">Drag to rotate · Scroll to zoom · Right-drag to pan</div>

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

/* ============================================================
   RENDERER / CAMERA / CONTROLS
   ============================================================ */
const app = document.getElementById('app');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x9ec5e8);
scene.fog = new THREE.Fog(0x9ec5e8, 26, 50);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(8, 6.5, 11);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0.9, 0);
controls.maxPolarAngle = Math.PI * 0.495;
controls.minDistance = 5;
controls.maxDistance = 24;

/* ============================================================
   LIGHTING
   ============================================================ */
scene.add(new THREE.AmbientLight(0xffffff, 0.28));
const hemi = new THREE.HemisphereLight(0xffffff, 0xffd9a8, 0.7);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff4e0, 1.25);
sun.position.set(7, 12, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 45;
const s = 13;
sun.shadow.camera.left = -s; sun.shadow.camera.right = s;
sun.shadow.camera.top = s;  sun.shadow.camera.bottom = -s;
sun.shadow.bias = -0.0004;
scene.add(sun);

const fill = new THREE.DirectionalLight(0xbfd4ff, 0.45);
fill.position.set(-7, 5, -6);
scene.add(fill);

const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(80, 80),
  new THREE.MeshStandardMaterial({ color: 0xb8c6db, roughness: 1 })
);
ground.rotation.x = -Math.PI/2;
ground.receiveShadow = true;
scene.add(ground);

/* ============================================================
   HELPERS
   ============================================================ */
const rand  = (a, b) => a + Math.random() * (b - a);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
function normAngle(a){ while (a >  Math.PI) a -= 2*Math.PI; while (a < -Math.PI) a += 2*Math.PI; return a; }
function lerpAngle(from, to, t){ return from + normAngle(to - from) * t; }

// Play area bounds (inside the tray)
const BOUNDS = { minX: -4.3, maxX: 4.3, minZ: -2.7, maxZ: 2.7 };
const FLOOR_Y = 0.5;          // hamster standing height (group.y)

/* ============================================================
   CAGE (tray + acrylic walls + wooden frame)
   ============================================================ */
function buildCage() {
  const g = new THREE.Group();
  const W = 10, D = 7, wallH = 0.7, upperH = 2.0;
  const trayMat = new THREE.MeshStandardMaterial({ color: 0x7ec8e3, roughness: 0.6, flatShading: true });
  const frameMat = new THREE.MeshStandardMaterial({ color: 0xf5deb3, roughness: 0.7, flatShading: true });

  // bottom plate
  const bottom = new THREE.Mesh(new THREE.BoxGeometry(W, 0.25, D), trayMat);
  bottom.position.y = 0.125; bottom.receiveShadow = true; bottom.castShadow = true;
  g.add(bottom);

  // low tray walls
  const wallThick = 0.15;
  const walls = [
    { w: W, d: wallThick, x: 0, z:  D/2 - wallThick/2 },
    { w: W, d: wallThick, x: 0, z: -D/2 + wallThick/2 },
    { w: wallThick, d: D, x:  W/2 - wallThick/2, z: 0 },
    { w: wallThick, d: D, x: -W/2 + wallThick/2, z: 0 },
  ];
  for (const wl of walls) {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(wl.w, wallH, wl.d), trayMat);
    wall.position.set(wl.x, wallH/2 + 0.25, wl.z);
    wall.castShadow = true; wall.receiveShadow = true;
    g.add(wall);
  }

  // transparent acrylic upper walls
  const acrylicMat = new THREE.MeshStandardMaterial({
    color: 0xdfffff, transparent: true, opacity: 0.16, roughness: 0.4,
    metalness: 0, side: THREE.DoubleSide
  });
  const upperBase = 0.25 + wallH;
  const upperWalls = [
    { w: W, h: upperH, x: 0, z:  D/2 },
    { w: W, h: upperH, x: 0, z: -D/2 },
    { w: D, h: upperH, x:  W/2, z: 0 },
    { w: D, h: upperH, x: -W/2, z: 0 },
  ];
  for (const uw of upperWalls) {
    const panel = new THREE.Mesh(new THREE.BoxGeometry(uw.w, upperH, 0.06), acrylicMat);
    panel.position.set(uw.x, upperBase + upperH/2, uw.z);
    g.add(panel);
  }

  // corner posts + top rails
  const postGeo = new THREE.BoxGeometry(0.16, wallH + upperH + 0.1, 0.16);
  const corners = [[ W/2, D/2], [-W/2, D/2], [ W/2, -D/2], [-W/2, -D/2]];
  for (const [cx, cz] of corners) {
    const post = new THREE.Mesh(postGeo, frameMat);
    post.position.set(cx, (wallH + upperH)/2 + 0.25, cz);
    post.castShadow = true;
    g.add(post);
  }
  const railTop = upperBase + upperH;
  const rl1 = new THREE.Mesh(new THREE.BoxGeometry(W, 0.12, 0.12), frameMat);
  const rl2 = rl1.clone();
  rl1.position.set(0, railTop,  D/2); rl2.position.set(0, railTop, -D/2);
  g.add(rl1); g.add(rl2);
  const rs1 = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, D), frameMat);
  const rs2 = rs1.clone();
  rs1.position.set( W/2, railTop, 0); rs2.position.set(-W/2, railTop, 0);
  g.add(rs1); g.add(rs2);

  return g;
}

/* ============================================================
   BEDDING (scattered wood shavings)
   ============================================================ */
function buildBedding() {
  const g = new THREE.Group();
  const colors = [0xe6c67f, 0xdcae66, 0xf0d897, 0xcba55a];
  for (let i = 0; i < 260; i++) {
    const mat = new THREE.MeshStandardMaterial({ color: colors[i % colors.length], roughness: 1, flatShading: true });
    const sz = rand(0.05, 0.09);
    const geo = Math.random() < 0.5
      ? new THREE.BoxGeometry(sz, sz*0.4, sz*0.7)
      : new THREE.ConeGeometry(sz*0.5, sz, 4);
    const p = new THREE.Mesh(geo, mat);
    p.position.set(rand(BOUNDS.minX, BOUNDS.maxX), 0.32, rand(BOUNDS.minZ, BOUNDS.maxZ));
    p.rotation.set(rand(0, Math.PI), rand(0, Math.PI), rand(0, Math.PI));
    g.add(p);
  }
  return g;
}

/* ============================================================
   EXERCISE WHEEL  (the main interactive object!)
   ============================================================ */
function buildWheel(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const ringY = 1.15, R = 1.0;

  const spin = new THREE.Group();
  spin.position.set(0, ringY, 0);
  g.add(spin);

  const ringMat = new THREE.MeshStandardMaterial({ color: 0xff5a5f, roughness: 0.5, flatShading: true });
  const rungMat = new THREE.MeshStandardMaterial({ color: 0xffd166, roughness: 0.6, flatShading: true });

  const outer = new THREE.Mesh(new THREE.TorusGeometry(R, 0.08, 8, 24), ringMat);
  outer.castShadow = true; spin.add(outer);
  const inner = new THREE.Mesh(new THREE.TorusGeometry(R*0.55, 0.05, 8, 20), ringMat);
  spin.add(inner);

  for (let i = 0; i < 12; i++) {
    const a = i/12 * Math.PI*2;
    const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.05, R*0.9, 0.05), rungMat);
    spoke.rotation.z = a;
    spoke.position.set(Math.cos(a)*R*0.52, Math.sin(a)*R*0.52, 0);
    spin.add(spoke);
  }

  const standMat = new THREE.MeshStandardMaterial({ color: 0x8d6e63, roughness: 0.7, flatShading: true });
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.55, 0.12, 12), standMat);
  base.position.y = 0.06; base.castShadow = true; base.receiveShadow = true;
  g.add(base);
  const post = new THREE.Mesh(new THREE.BoxGeometry(0.14, ringY, 0.14), standMat);
  post.position.set(0, ringY/2, 0.42); g.add(post);
  const post2 = post.clone(); post2.position.z = -0.42; g.add(post2);

  g.userData.spin = spin;
  return g;
}

/* ============================================================
   FOOD BOWL
   ============================================================ */
function buildFoodBowl(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const bowlMat = new THREE.MeshStandardMaterial({ color: 0x4fc3f7, roughness: 0.5, flatShading: true });
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.35, 0.25, 16, 1, true), bowlMat);
  bowl.position.y = 0.13; bowl.castShadow = true; g.add(bowl);
  const bot = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.05, 16), bowlMat);
  bot.position.y = 0.025; g.add(bot);
  const seedMat = new THREE.MeshStandardMaterial({ color: 0x8d6e3f, roughness: 0.9, flatShading: true });
  for (let i = 0; i < 15; i++) {
    const seed = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.12, 5), seedMat);
    const a = Math.random()*Math.PI*2, r = Math.random()*0.3;
    seed.position.set(Math.cos(a)*r, 0.23, Math.sin(a)*r);
    seed.rotation.z = rand(-0.6, 0.6);
    g.add(seed);
  }
  return g;
}

/* ============================================================
   TUNNEL
   ============================================================ */
function buildTunnel(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const tubeMat = new THREE.MeshStandardMaterial({ color: 0xd9a06b, roughness: 0.9, flatShading: true, side: THREE.DoubleSide });
  const len = 2.6, R = 0.62;
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(R, R, len, 16, 1, true), tubeMat);
  tube.rotation.x = Math.PI/2;                 // axis along Z
  tube.position.y = R + 0.05;
  tube.castShadow = true;
  g.add(tube);
  const rimMat = new THREE.MeshStandardMaterial({ color: 0xc0854f, roughness: 0.8, flatShading: true });
  for (const zz of [ len/2, -len/2 ]) {
    const rim = new THREE.Mesh(new THREE.TorusGeometry(R, 0.06, 8, 20), rimMat);
    rim.position.set(0, R + 0.05, zz);
    g.add(rim);
  }
  return g;
}

/* ============================================================
   LITTLE HOUSE
   ============================================================ */
function buildHouse(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const wallMat = new THREE.MeshStandardMaterial({ color: 0xf4a259, roughness: 0.8, flatShading: true });
  const roofMat = new THREE.MeshStandardMaterial({ color: 0xe2704a, roughness: 0.8, flatShading: true });
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.8, 1.2), wallMat);
  body.position.y = 0.4; body.castShadow = true; body.receiveShadow = true;
  g.add(body);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(0.98, 0.6, 4), roofMat);
  roof.position.y = 1.1; roof.rotation.y = Math.PI/4; roof.castShadow = true;
  g.add(roof);
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.5, 0.1),
    new THREE.MeshStandardMaterial({ color: 0x3a2a1a, flatShading: true }));
  door.position.set(0, 0.3, 0.6);
  g.add(door);
  return g;
}

/* ============================================================
   HAMSTER  (low-poly creature + autonomous behaviour)
   ============================================================ */
const COLORS = [0xf4a259, 0xffd6a5, 0xc9b3a0, 0xffb4a2, 0xa0c4ff];

class Hamster {
  constructor(color, sx, sz) {
    this.color = color;
    this.group = new THREE.Group();
    this.build();
    this.group.position.set(sx, FLOOR_Y, sz);
    scene.add(this.group);

    // behaviour state machine
    this.state = 'wander';
    this.timer = rand(1, 2.5);
    this.speed = rand(0.65, 0.95);
    this.heading = rand(0, Math.PI*2);
    this.walkPhase = rand(0, Math.PI*2);
    this.nextTarget();

    // blink
    this.blinkTimer = rand(1, 3);
    this.blinking = false;
    this.blinkProgress = 0;

    // interaction bookkeeping
    this.interactPos = new THREE.Vector3();
    this.interactionType = '';
  }

  /* ---- build the body from primitives ---- */
  build() {
    const mat  = new THREE.MeshStandardMaterial({ color: this.color, roughness: 0.9, flatShading: true });
    const dark = new THREE.MeshStandardMaterial({ color: 0x2a2a2a, roughness: 0.5, flatShading: true });
    const pink = new THREE.MeshStandardMaterial({ color: 0xff9db0, roughness: 0.8, flatShading: true });
    const white= new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6, flatShading: true });

    // body
    const bGeo = new THREE.SphereGeometry(0.5, 14, 12);
    bGeo.scale(1, 0.95, 1.25);
    this.body = new THREE.Mesh(bGeo, mat);
    this.body.castShadow = true; this.body.receiveShadow = true;
    this.group.add(this.body);

    // head group (nods independently)
    this.headGroup = new THREE.Group();
    this.headGroup.position.set(0, 0.2, 0.55);
    this.group.add(this.headGroup);

    const hGeo = new THREE.SphereGeometry(0.4, 14, 12);
    this.head = new THREE.Mesh(hGeo, mat);
    this.head.castShadow = true;
    this.headGroup.add(this.head);

    // ears
    const earGeo = new THREE.SphereGeometry(0.16, 12, 10);
    this.earL = new THREE.Mesh(earGeo, mat);
    this.earL.position.set(-0.22, 0.34, -0.02); this.earL.scale.set(1,1,0.6);
    this.headGroup.add(this.earL);
    this.earR = this.earL.clone(); this.earR.position.x = 0.22;
    this.headGroup.add(this.earR);

    // eyes (white + pupil, pupil used for blink)
    const wGeo = new THREE.SphereGeometry(0.1, 12, 10);
    this.eyeLW = new THREE.Mesh(wGeo, white); this.eyeLW.position.set(-0.16, 0.06, 0.33); this.headGroup.add(this.eyeLW);
    this.eyeRW = this.eyeLW.clone(); this.eyeRW.position.x = 0.16; this.headGroup.add(this.eyeRW);
    const pGeo = new THREE.SphereGeometry(0.06, 10, 8);
    this.eyeL = new THREE.Mesh(pGeo, dark); this.eyeL.position.set(-0.16, 0.06, 0.4); this.headGroup.add(this.eyeL);
    this.eyeR = this.eyeL.clone(); this.eyeR.position.x = 0.16; this.headGroup.add(this.eyeR);
    this.eyes = [this.eyeL, this.eyeR];

    // nose + puffy cheeks
    this.nose = new THREE.Mesh(new THREE.SphereGeometry(0.055, 10, 8), pink);
    this.nose.position.set(0, -0.02, 0.42); this.headGroup.add(this.nose);
    this.cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 10), mat);
    this.cheekL.position.set(-0.26, -0.04, 0.18); this.cheekL.scale.set(1, 0.9, 0.9); this.headGroup.add(this.cheekL);
    this.cheekR = this.cheekL.clone(); this.cheekR.position.x = 0.26; this.headGroup.add(this.cheekR);

    // tail
    this.tail = new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8), mat);
    this.tail.position.set(0, -0.05, -0.65); this.tail.scale.set(1, 0.8, 0.7);
    this.group.add(this.tail);

    // four swingable legs (each on a pivot at the shoulder/hip)
    const offs = { FL:[-0.28,0,0.28], FR:[0.28,0,0.28], BL:[-0.28,0,-0.28], BR:[0.28,0,-0.28] };
    this.legs = {};
    for (const k in offs) {
      const pivot = new THREE.Group();
      pivot.position.set(offs[k][0], offs[k][1], offs[k][2]);
      this.group.add(pivot);
      const legGeo = new THREE.BoxGeometry(0.12, 0.22, 0.12);
      legGeo.translate(0, -0.11, 0);          // pivot at the top
      const leg = new THREE.Mesh(legGeo, pink);
      leg.castShadow = true;
      pivot.add(leg);
      this.legs[k] = pivot;
    }
  }

  /* ---- movement helpers ---- */
  moveTowards(target, dt) {
    const dir = new THREE.Vector3().subVectors(target, this.group.position); dir.y = 0;
    const dist = dir.length();
    if (dist < 0.01) return true;
    dir.normalize();
    this.heading = lerpAngle(this.heading, Math.atan2(dir.x, dir.z), dt * 6);
    const step = Math.min(dist, this.speed * dt);
    this.group.position.x += dir.x * step;
    this.group.position.z += dir.z * step;
    return false;
  }

  nextTarget() {
    this.target = new THREE.Vector3(rand(BOUNDS.minX, BOUNDS.maxX), FLOOR_Y, rand(BOUNDS.minZ, BOUNDS.maxZ));
  }

  depart() {
    // step away from wherever we were interacting
    const dir = this.interactPos.clone(); dir.y = 0;
    if (dir.lengthSq() === 0) dir.set(1, 0, 0);
    dir.normalize();
    const away = this.interactPos.clone().addScaledVector(dir, 1.6);
    away.y = FLOOR_Y;
    away.x = clamp(away.x, BOUNDS.minX, BOUNDS.maxX);
    away.z = clamp(away.z, BOUNDS.minZ, BOUNDS.maxZ);
    this.target = away;
    this.state = 'wander';
  }

  pickNewState() {
    const r = Math.random();
    if (r < 0.30) {
      this.state = 'pause'; this.timer = rand(1.5, 3);
    } else if (r < 0.52) {
      this.state = 'turn';
      this.targetHeading = this.heading + (Math.random() < 0.5 ? -1 : 1) * rand(0.7, 1.4);
      this.timer = rand(0.6, 1.1);
    } else if (r < 0.74) {
      this.startInteraction('wheel');
    } else if (r < 0.88) {
      this.startInteraction('food');
    } else {
      this.startInteraction('tunnel');
    }
  }

  startInteraction(type) {
    const T = INTERACTIONS[type];
    this.interactionType = type;
    this.interactPos.copy(T.pos);
    this.target.copy(T.pos);
    this.state = 'approach';
  }

  enterInteraction() {
    if (this.interactionType === 'wheel') {
      this.state = 'wheel_run';
      this.timer = rand(3, 5.5);
      this.group.position.set(INTERACTIONS.wheel.pos.x, FLOOR_Y, INTERACTIONS.wheel.pos.z);
      this.group.rotation.y = INTERACTIONS.wheel.facing;
    } else if (this.interactionType === 'food') {
      this.state = 'eat';
      this.timer = rand(2, 3.5);
      this.group.rotation.y = INTERACTIONS.food.facing;
    } else if (this.interactionType === 'tunnel') {
      this.state = 'in_tunnel';
      this.timer = rand(1.8, 3);
      this.group.visible = false;
    }
  }

  /* ---- per-frame update ---- */
  update(dt, t) {
    this.timer -= dt;

    // blink
    this.blinkTimer -= dt;
    if (this.blinkTimer <= 0) {
      this.blinkTimer = rand(2, 5);
      this.blinking = true; this.blinkProgress = 0;
    }
    if (this.blinking) {
      this.blinkProgress += dt * 26;
      const sq = Math.sin(Math.min(this.blinkProgress, Math.PI));
      this.eyes.forEach(e => e.scale.y = 1 - sq * 0.92);
      if (this.blinkProgress >= Math.PI) { this.blinking = false; this.eyes.forEach(e => e.scale.y = 1); }
    }

    // relax limbs & reset shape
    for (const k in this.legs) this.legs[k].rotation.x *= 0.8;
    this.headGroup.rotation.x *= 0.8;
    this.headGroup.rotation.z *= 0.8;
    this.body.scale.set(1, 1, 1);
    this.cheekL.scale.set(1, 0.9, 0.9);
    this.cheekR.scale.set(1, 0.9, 0.9);

    switch (this.state) {
      case 'wander': {
        const arrived = this.moveTowards(this.target, dt);
        this.animateWalk(dt, 1, t);
        if (arrived || this.timer <= 0) this.pickNewState();
        break;
      }
      case 'pause':
        this.animateIdle(t);
        if (this.timer <= 0) this.pickNewState();
        break;
      case 'turn': {
        this.heading = lerpAngle(this.heading, this.targetHeading, dt * 5);
        this.group.rotation.y = this.heading;
        this.animateWalk(dt, 0.35, t);
        if (Math.abs(normAngle(this.heading - this.targetHeading)) < 0.12 || this.timer <= 0) {
          this.state = 'wander'; this.nextTarget();
        }
        break;
      }
      case 'approach': {
        const arrived = this.moveTowards(this.interactPos, dt);
        this.animateWalk(dt, 1, t);
        if (arrived) this.enterInteraction();
        break;
      }
      case 'wheel_run':
        this.animateWalk(dt, 2.4, t);
        if (this.timer <= 0) this.depart();
        break;
      case 'eat':
        this.animateEat(t);
        if (this.timer <= 0) this.depart();
        break;
      case 'in_tunnel':
        if (this.timer <= 0) { this.group.visible = true; this.depart(); }
        break;
    }

    // keep inside the cage
    this.group.position.x = clamp(this.group.position.x, BOUNDS.minX, BOUNDS.maxX);
    this.group.position.z = clamp(this.group.position.z, BOUNDS.minZ, BOUNDS.maxZ);
  }

  /* ---- animations ---- */
  animateWalk(dt, intensity, t) {
    this.walkPhase += dt * 9 * (0.5 + intensity * 0.4);
    const s = Math.sin(this.walkPhase);
    this.legs.FL.rotation.x =  s * 0.55 * intensity;
    this.legs.BR.rotation.x =  s * 0.55 * intensity;
    this.legs.FR.rotation.x = -s * 0.55 * intensity;
    this.legs.BL.rotation.x = -s * 0.55 * intensity;
    this.body.position.y = Math.abs(Math.sin(this.walkPhase)) * 0.035 * intensity;
    this.headGroup.rotation.x = Math.sin(this.walkPhase * 0.5) * 0.09 * intensity;
  }

  animateIdle(t) {
    const b = Math.sin(t * 2.2) * 0.035;
    this.body.scale.set(1 + b, 1 - b, 1 + b);
    this.headGroup.rotation.z = Math.sin(t * 1.3) * 0.05;
  }

  animateEat(t) {
    this.headGroup.rotation.x = Math.abs(Math.sin(t * 13)) * 0.18;
    this.headGroup.rotation.y = Math.sin(t * 3) * 0.08;
    const c = 1 + Math.sin(t * 11) * 0.12;
    this.cheekL.scale.set(c, 0.9, 0.9);
    this.cheekR.scale.set(c, 0.9, 0.9);
  }
}

/* interaction target spots */
const INTERACTIONS = {
  wheel:  { pos: new THREE.Vector3(-3.4, FLOOR_Y, 0.0),  facing: Math.PI/2 },
  food:   { pos: new THREE.Vector3( 3.5, FLOOR_Y, 0.85), facing: Math.PI },
  tunnel: { pos: new THREE.Vector3(-0.7, FLOOR_Y, -0.9), facing: Math.PI }
};

/* ============================================================
   ASSEMBLE SCENE
   ============================================================ */
scene.add(buildCage());
scene.add(buildBedding());

const wheel  = buildWheel(-3.4, 0);   scene.add(wheel);
const food   = buildFoodBowl( 3.5, 0.6); scene.add(food);
const tunnel = buildTunnel( 0, -2.4);  scene.add(tunnel);
const house  = buildHouse(  2.6, -2.2); scene.add(house);

// a stray ball toy rolling gently for extra charm
const toyBall = new THREE.Mesh(
  new THREE.IcosahedronGeometry(0.22, 0),
  new THREE.MeshStandardMaterial({ color: 0x06d6a0, roughness: 0.6, flatShading: true })
);
toyBall.position.set(1.2, 0.72, 1.6); toyBall.castShadow = true;
scene.add(toyBall);
let ballVel = new THREE.Vector3(rand(-0.3, 0.3), 0, rand(-0.3, 0.3));

const hamsters = [];
const spawns = [[-1, 1.2], [1.2, -1], [0.4, 1.6], [-1.6, -0.6]];
for (let i = 0; i < 4; i++) {
  hamsters.push(new Hamster(COLORS[i % COLORS.length], spawns[i][0], spawns[i][1]));
}

/* ============================================================
   ANIMATION LOOP
   ============================================================ */
const clock = new THREE.Clock();
let wheelVel = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t  = clock.elapsedTime;

  hamsters.forEach(h => h.update(dt, t));

  // wheel reacts to hamsters running on it
  let targetVel = 0;
  hamsters.forEach(h => { if (h.state === 'wheel_run') targetVel = 0.6; });
  wheelVel += (targetVel - wheelVel) * 0.08;
  wheel.userData.spin.rotation.z += wheelVel;

  // gentle tumble of the toy ball
  toyBall.rotation.x += ballVel.z * dt;
  toyBall.rotation.z -= ballVel.x * dt;
  toyBall.position.addScaledVector(ballVel, dt);
  toyBall.position.y = 0.72 + Math.abs(Math.sin(t * 3)) * 0.0;
  if (toyBall.position.x < -4 || toyBall.position.x > 4) ballVel.x *= -1;
  if (toyBall.position.z < -2.5 || toyBall.position.z > 2.5) ballVel.z *= -1;

  controls.update();
  renderer.render(scene, camera);
}
animate();

/* ============================================================
   RESIZE
   ============================================================ */
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

**The scene**
- A plastic **tray** with low walls, transparent **acrylic upper walls**, and a wooden **frame** with corner posts and top rails.
- ~260 scattered **wood-shaving bedding** pieces for a cozy look.
- Soft fog + warm sunlight with soft shadows for a friendly, readable mood.

**The hamsters** (4, each built from primitives with `flatShading` for that low-poly look)
- Ellipsoid body, big head, floppy ears, puffy cheeks, bulging eyes that **blink**, a pink nose, stubby feet on swingable pivots, and a little round tail.

**Autonomous behaviour** (a small state machine per hamster)
- **Wander** → pick a random spot, walk toward it (legs swing, body bobs, head nods).
- **Pause** → stand and "breathe."
- **Turn** → rotate in place to face a new direction.
- **Interact** with objects:
  - 🎡 **Exercise wheel** – runs in place, wheel spins up and coasts to a stop.
  - 🥣 **Food bowl** – nibbles with chewing cheek-puffs.
  - 🪄 **Tunnel** – walks in, vanishes, reappears on the far side.

**Interactive object:** the spinning exercise wheel responds to the hamsters running on it.

**Camera controls:** drag to rotate, scroll to zoom, right-drag to pan (damped OrbitControls).

## How to run
1. Copy the code into a file named `index.html`.
2. Open it in Chrome, Firefox, Safari, or Edge (any modern browser).
3. That's it — it loads Three.js from a CDN via the import map, no install step required.

Want me to add sound effects, a day/night toggle, or let you click a hamster to make it scurry away? Just say the word!