Let me create a single-file HTML project with a Low-Poly Hamster Playground using Three.js. I need to:

1. Create an index.html file with everything inline
2. Use Three.js (from CDN)
3. Include OrbitControls for camera rotation
4. Build a cage scene with:
   - A cage structure
   - A floor/tray
   - Several low-poly hamsters
   - One interactive object (wheel, tunnel, food bowl, or toy)
5. Add autonomous behavior to hamsters
6. Make it cute, low-poly, colorful, and funny

Let me think about the design:

**Cage:**
- A tray (bottom box) 
- Walls (transparent or bars)
- Could use a plastic base tray with glass/acrylic walls

**Floor:**
- Sawdust/wood shavings texture or just a colored plane
- Maybe some small particles for bedding

**Hamsters:**
- Low-poly body (sphere/icosahedron)
- Ears (cones or spheres)
- Eyes (small spheres)
- Nose (small)
- Cheeks
- Little feet
- Tail
- Different colors

**Interactive object:**
- Exercise wheel (spinning) that hamsters can run on
- Or a food bowl

**Behavior:**
- Walk around randomly
- Pause occasionally
- Turn around
- Interact with the wheel

Let me build this carefully. I'll use Three.js r128 or a recent version from CDN.

Let me write clean, working code.

I'll structure the hamster as a function that creates a group with all parts.

For movement, each hamster will have:
- A target position
- A state machine: WALKING, PAUSING, TURNING
- Speed and direction
- Animation of legs when walking

Let me make the wheel interactive - clicking it makes it spin faster or a hamster goes on it. Actually, let me make the wheel spin continuously and have hamsters occasionally go onto it. Or better - clicking the wheel makes a hamster run on it.

Let me keep it simpler but fun:
- Wheel spins continuously
- Clicking the wheel gives it a boost and attracts nearby hamsters

Actually, let me make a food bowl that when clicked, drops a seed and hamsters go to eat it. That's more interactive.

Let me do both a wheel and make clicking do something. Let me focus on one good interactive element: the exercise wheel. When you click it, it spins fast and a random hamster hops on to run.

Let me plan the code structure:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Low-Poly Hamster Playground</title>
  <style>...</style>
</head>
<body>
  <div id="ui">instructions</div>
  <script src="three.js CDN"></script>
  <script src="orbitcontrols CDN"></script>
  <script>
    // Scene setup
    // Lights
    // Cage
    // Floor
    // Hamsters
    // Wheel (interactive)
    // Animation loop
    // Raycaster for interaction
  </script>
</body>
</html>
```

Let me write it all out. I'll use a recent Three.js version. Let me use r158 or so. Actually, let me use a version where OrbitControls is available via CDN import map or as a script.

I'll use the module approach with import maps, OR the older approach. Let me use the classic approach with a global THREE and the OrbitControls from a UMD build.

Actually the cleanest is to use ES modules with importmap:

```html
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/src/"
  }
}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
</script>
```

Hmm, the addons path. Let me use:
```
"three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
```

That's the standard. Let me verify: three examples/jsm/controls/OrbitControls.js exists. Yes.

Let me write the full thing.

For the hamster creation, I'll build a nice low-poly hamster. Let me define colors.

Let me think about the hamster model:
- Body: an ellipsoid (use scaled sphere) - main color
- Head: sphere merged or separate
- Actually, let me make body and head somewhat separate so the head can bob

Simple approach: one group for the whole hamster.
- Body: IcosahedronGeometry or SphereGeometry scaled
- Head: sphere attached to front
- Two ears: small spheres/cones on top of head
- Two eyes: white with black pupil
- Nose: pink small sphere
- Two cheeks: small spheres
- Four legs: small cylinders/cubes, animated when walking
- Tail: tiny

Let me keep it manageable. I'll make the body a single group and attach head + legs.

Let me code it:

```javascript
function createHamster(color) {
  const hamster = new THREE.Group();
  
  // Body
  const bodyGeo = new THREE.SphereGeometry(0.5, 12, 10);
  bodyGeo.scale(1, 0.9, 1.3); // elongated
  const bodyMat = new THREE.MeshToonMaterial({ color });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  hamster.add(body);
  
  // Head
  const head = new THREE.Group();
  const headGeo = new THREE.SphereGeometry(0.35, 12, 10);
  const headMesh = new THREE.Mesh(headGeo, bodyMat);
  head.add(headMesh);
  head.position.set(0.55, 0.1, 0);
  hamster.add(head);
  
  // Ears
  const earGeo = new THREE.ConeGeometry(0.12, 0.2, 8);
  const earL = new THREE.Mesh(earGeo, bodyMat);
  earL.position.set(0.45, 0.45, 0.15);
  const earR = earL.clone();
  earR.position.z = -0.15;
  head.add(earL, earR);
  
  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.07, 8, 8);
  const eyeMat = new THREE.MeshBasicMaterial({ color: 0x1a1a1a });
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(0.8, 0.15, 0.12);
  const eyeR = eyeL.clone();
  eyeR.position.z = -0.12;
  head.add(eyeL, eyeR);
  
  // Nose
  const noseGeo = new THREE.SphereGeometry(0.05, 8, 8);
  const noseMat = new THREE.MeshBasicMaterial({ color: 0xff9999 });
  const nose = new THREE.Mesh(noseGeo, noseMat);
  nose.position.set(0.9, 0.05, 0);
  head.add(nose);
  
  // Cheeks (white-ish)
  ...
  
  // Legs
  const legGeo = new THREE.BoxGeometry(0.12, 0.2, 0.12);
  ...
  
  return hamster;
}
```

Hmm, the head rotation for bobbing. Let me keep the head as part of the group and rotate it slightly during walk cycle.

Actually to keep it stable and simple, let me make legs children of the body and animate them.

Let me now think about the movement AI:

Each hamster has:
- `state`: 'walk' | 'pause' | 'turn'
- `timer`: time until next state change
- `targetPos`: Vector3 where it's walking to
- `speed`
- `legPhase`: for animation
- reference to its legs for animation

Behavior loop:
- Pick a random target within the cage bounds
- Walk towards it (rotate to face direction, move forward, animate legs)
- When reached, switch to pause state
- After pause, pick new target or turn

Let me implement:

```javascript
class Hamster {
  constructor(scene, color) {
    this.mesh = createHamster(color);
    scene.add(this.mesh);
    this.pos = new THREE.Vector3(...);
    this.vel = ...;
    this.heading = Math.random() * Math.PI * 2;
    this.state = 'walk';
    this.timer = 0;
    this.target = randomPoint();
    this.speed = 0.5 + Math.random()*0.3;
    this.legs = [...];
    scene.remove... 
  }
  
  update(dt) {
    switch(state) {
      case 'walk':
        // move toward target
        // face direction
        // animate legs
        if reached target -> pause
      case 'pause':
        // idle, maybe breathe
        timer -= dt
        if timer <= 0 -> pick new target or turn
      case 'turn':
        rotate
    }
  }
}
```

Let me bound positions within the tray.

Now the interactive wheel:
- A ring/hoop on two supports
- Spins continuously
- When clicked (raycaster), spin speed increases temporarily and a hamster runs onto it

Let me make the wheel spin and when clicked, it boosts. Also let me add a subtle "running" where if a hamster is near the wheel it might join. To keep simple, clicking the wheel just spins it faster and makes all hamsters get excited (move faster briefly). That's fun.

Actually, let me make clicking the wheel attract one hamster to run on it. Hmm, that requires the hamster to climb. Let me keep it simpler: clicking the wheel spins it fast for a couple seconds, and the hamsters nearby get a speed boost. Fun and stable.

Let me also add sawdust particles on the floor for cuteness.

Let me add a food bowl too as decoration, and maybe seeds.

Let me write the complete code now.

For lighting: ambient + directional + hemisphere for soft shadows. Enable shadows for nicety but keep performance.

Let me set up:
- HemisphereLight for ambient
- DirectionalLight with shadow for the sun

Shadows: set camera.shadowCamera, light.shadow.mapSize. Keep it simple.

Let me now write the full HTML.

I need to be careful with the import map and module scripts.

Let me also add a nice background color and maybe fog.

Let me write it:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; height: 100%; }
  #app { width: 100vw; height: 100vh; display: block; }
  #info {
    position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
    font-family: 'Comic Sans MS', 'Segoe UI', sans-serif;
    color: #fff; background: rgba(0,0,0,0.35);
    padding: 8px 16px; border-radius: 20px; font-size: 14px;
    pointer-events: none; user-select: none; text-align: center;
    backdrop-filter: blur(4px);
  }
  #info b { color: #ffe37a; }
</style>
</head>
<body>
<div id="app"></div>
<div id="info"><b>🐹 Low-Poly Hamster Playground</b><br>
Drag to rotate · Scroll to zoom · <b>Click the wheel!</b></div>

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

// ... all the code
</script>
</body>
</html>
```

Now the JS. Let me write it fully.

Let me define constants for the cage size.

Cage tray: width (x) ~ 12, depth (z) ~ 8, height (y) ~ 1.5 for walls.

Let me place wheel at one side, food bowl at another.

Let me write helper functions.

I'll write the whole thing carefully.

For the wheel interaction, I'll use raycasting on mouse click. Detect if hit the wheel mesh (or its children). Then boost.

Let me handle window resize.

Let me code the hamster leg animation. Each leg has a pivot; I'll rotate legs back and forth based on time when walking.

Let me structure legs as: front-left, front-right, back-left, back-right. Animate with sine waves offset by phases.

Legs are children of body group, positioned at 4 corners. When animating, rotate them around X axis.

But rotating a leg that's offset from origin... if I set leg geometry centered and position it, then rotate x, it swings. Good enough.

Let me write:

```javascript
function buildLeg() {
  const leg = new THREE.Group();
  const geo = new THREE.BoxGeometry(0.12, 0.22, 0.12);
  const mat = new THREE.MeshToonMaterial({ color: bodyColor });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.y = -0.11;
  leg.add(mesh);
  leg.userData.baseY = 0; // pivot at body bottom
  return leg;
}
```

Hmm, the leg group pivot is at body center-ish. Let me position legs so their pivot is at the hip, and they hang down.

Actually simpler: place the leg mesh directly with geometry translated down, and rotate the mesh itself. But rotating a mesh that's offset rotates around its own center, causing wobble. Let me instead use a group as pivot at the top of the leg.

Let me do:
- legPivot group positioned at hip point (top of leg)
- inside it, a leg mesh whose local y is downward (so it hangs)
- rotate legPivot.x for swing

That works cleanly.

Let me finalize positions. Body radius ~0.5, scaled. Body bottom at y=0 (ground). Center of body at y ~0.4.

Legs attach at four points around body, at y ~0.3, and hang to y ~0 (feet touch ground). Leg length 0.3.

Front legs near head (x ~ 0.35), back legs near tail (x ~ -0.35). z ~ ±0.28.

OK let me just write it and tune visually.

Let me also give the hamster a slight body scale so it looks like a chubby hamster.

Let me write the entire script now. I'll be thorough.

For randomness in colors, I'll pick from a palette:
- 0xf5c6a0 (cream/tan)
- 0xd9a06b (light brown)
- 0xffffff (white)
- 0xc9b0a0 (greyish)
- 0xe8c07d (golden)
- 0xb5654d (reddish)

Eyes always dark. Nose pink.

Let me add a belly lighter color? Optional. Keep simple.

Let me write now.

Movement bounds: The hamsters should stay within the tray interior. Tray inner area maybe x: [-5,5], z: [-3.5, 3.5]. They should turn before hitting walls.

I'll generate targets within margins.

State machine:
- WALK: move toward target. When distance < 0.2, go PAUSE.
- PAUSE: stand still, breathe. timer random 1-3s. Then 70% pick new walk target, 30% do a quick turn (spin).
- TURN: rotate 180 or random, timer ~0.5s, then WALK.

Walking: heading = atan2(dir). Smoothly rotate toward heading. Move forward along heading. Animate legs.

Breathing during pause: scale body y slightly with sine.

Let me code update:

```javascript
update(dt) {
  const m = this.mesh;
  if (this.boostUntil > 0) { this.boostUntil -= dt; }
  
  switch(this.state) {
    case 'walk': {
      const toTarget = this.target.clone().sub(m.position);
      toTarget.y = 0;
      const dist = toTarget.length();
      if (dist > 0.15) {
        const dir = toTarget.normalize();
        const desiredHeading = Math.atan2(dir.x, dir.z);
        m.rotation.y = lerpAngle(m.rotation.y, desiredHeading, dt * 8);
        m.position.addScaledVector(dir, this.speed * dt * (this.excited ? 1.8 : 1));
        // leg anim
        this.legPhase += dt * 10;
        animateLegs(this.legs, this.legPhase);
        this.headBob += dt;
      } else {
        this.setState('pause');
      }
      break;
    }
    case 'pause': {
      this.timer -= dt;
      // breathing
      const b = 1 + Math.sin(this.timer*3)*0.02;
      m.scale.set(1, b, 1);
      if (this.timer <= 0) {
        if (Math.random() < 0.25) this.setState('turn');
        else this.pickTarget();
      }
      break;
    }
    case 'turn': {
      this.timer -= dt;
      m.rotation.y += (this.turnDir * dt * 3);
      if (this.timer <= 0) { this.pickTarget(); }
      break;
    }
  }
  
  // bounds clamp
  m.position.x = clamp(m.position.x, -5, 5);
  m.position.z = clamp(m.position.z, -3.5, 3.5);
}
```

Good.

Now the wheel. Let me build a running wheel:
- A big hoop (TorusGeometry) vertical, mounted on two vertical posts attached to base.
- Rungs/spokes inside for hamster to grip.
- Posts attached to base plate.

Position wheel at x = -4.5, z = 0. Orient so the wheel plane is... let me make the wheel spin around X axis (like a real hamster wheel viewed from the side) or Z axis. Real hamster wheels spin around a horizontal axis. If viewed from the side, the wheel is a circle in the X-Y plane spinning around X. Hmm.

Let me orient the wheel so its circular face is in the Y-Z plane and it spins around the X axis. Then a hamster runs "into the screen" direction. Actually let me make it spin around the horizontal Z axis so the wheel face is in X-Y plane (facing camera-ish). 

Let me just make a wheel that spins around the X axis (horizontal), facing along X. So the circle is in Y-Z plane. Hamster runs along X direction inside it. Posts hold it at z = ±something.

Actually, for a cute scene, let me mount the wheel facing the camera somewhat. Let me make the wheel spin around the Z axis (horizontal, pointing at viewer), so the wheel appears as a circle in the X-Y plane. Hamster runs up the inside. Posts on left and right (at x ± support).

Hmm, but then hamster walking along X would go into the wheel. Let me place wheel at the side and let hamster approach from front.

Let me simplify: Wheel spins around X axis. It's a circle in the YZ plane. Place at x=-4.5. The hamster runs inside it moving in Z direction. Posts at z = ±0.6 connecting to base.

When a hamster is near the wheel and excited, it could hop in. But let me keep the interaction simple: clicking wheel spins it fast + excites hamsters. That's enough and fun.

Let me build wheel:

```javascript
function buildWheel() {
  const wheel = new THREE.Group();
  const ringMat = new THREE.MeshStandardMaterial({ color: 0xff6b6b, metalness:0.2, roughness:0.5 });
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.9, 0.06, 8, 24), ringMat);
  wheel.add(ring);
  // spokes / rungs
  for (let i=0;i<12;i++){
    const angle = i/12*Math.PI*2;
    const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.03,1.7,6), ringMat);
    rung.rotation.x = Math.PI/2; // along X
    rung.position.set(0, Math.cos(angle)*0.9, Math.sin(angle)*0.9);
    // hmm positioning rungs
  }
  ...
}
```

This is getting complicated. Let me simplify the wheel to a torus with a few cross bars and two side discs (optional). For spinning, I'll rotate the whole ring group around X.

Let me make:
- outerRing: torus
- innerRungs: several thin cylinders across the diameter (like a ladder) so it looks like a wheel
- Actually, let me make rungs as cylinders spanning the width (along X) at various angular positions.

Let me do:
```
for i in 0..10:
  angle = i/10 * PI*2
  rung = cylinder radius 0.03, length 1.5 (along X)
  position: (0, cos(angle)*R, sin(angle)*R)
  rotation.x = PI/2 (so cylinder axis is X)
```
Wait, cylinder default is along Y. To make it along X, rotate PI/2 around Z. Then position at the angular spot on the circle.

Hmm, let me reconsider. A rung spanning the width (X direction) at angle θ on the ring:
- position: (0, R*cosθ, R*sinθ)
- oriented along X: rotate around Z by 90° → but that puts it along... let me think. Cylinder along Y, rotate 90° about Z → now along X. Yes. So rung.rotation.z = Math.PI/2.

Then the ring also has the torus. And two side supports (posts) going down to base.

Supports: two vertical cylinders at (±0.8, -0.45, 0)? No wait, the wheel center is at some height. Let me set wheel center at y=1.0. Posts from (0,0,±0.7) hmm.

Let me restructure. The wheel is a circle in YZ plane centered at (0, 1.0, 0) relative to wheel group. Wait I said wheel faces along X meaning circle in YZ plane. Posts hold the axle. Axle is along X. Two posts come down from the axle ends to the base.

Axle endpoints: (-0.8, 1.0, 0) and (0.8, 1.0, 0)? No. The axle is along X, so its ends are at x=-0.7 and x=+0.7 at the wheel center. Posts descend from there to base at y=0.

Let me set:
- wheel center at y = 1.0
- axle along X from x=-0.75 to x=+0.75
- post1 at x=-0.75: from (−0.75,1.0,0) down to (−0.75,0,0) — but that's a straight vertical post at the axle end. Fine.
- post2 at x=+0.75 similarly.

Base: the wheel group is placed at world position (-4.5, 0, 0). Posts attach wheel to a base plate or directly to ground.

Let me place posts going down to y=0 (ground). Add a small base pad under posts for stability look.

Actually simpler: mount the whole wheel assembly on a base plate.

Let me just build:
- basePlate: box at y=0.05, size 1.6 x 0.1 x 1.4
- two posts from base up to axle level
- axle
- wheel ring + rungs

I'll put the spinning part (ring+rungs) as a child group `spinning`, and rotate that. Posts and base are static.

Let me code:

```javascript
function buildWheel() {
  const group = new THREE.Group();
  const frameMat = new THREE.MeshStandardMaterial({ color: 0x5c9cff, roughness:0.6 });
  const ringMat = new THREE.MeshStandardMaterial({ color: 0xff5252, roughness:0.5, metalness:0.1 });
  
  // base
  const base = new THREE.Mesh(new THREE.BoxGeometry(1.6,0.12,1.4), frameMat);
  base.position.y = 0.06;
  base.castShadow = true;
  group.add(base);
  
  // posts
  const postGeo = new THREE.CylinderGeometry(0.07,0.07,1.0,8);
  const postL = new THREE.Mesh(postGeo, frameMat);
  postL.position.set(-0.7, 0.55, 0.5);
  const postR = postL.clone(); postR.position.z = -0.5;
  group.add(postL, postR);
  
  const spinning = new THREE.Group();
  spinning.position.set(0, 1.05, 0);
  group.add(spinning);
  
  const R = 0.85;
  const ring = new THREE.Mesh(new THREE.TorusGeometry(R, 0.06, 8, 28), ringMat);
  spinning.add(ring);
  
  // rungs along X
  for (let i=0;i<14;i++){
    const a = i/14*Math.PI*2;
    const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.03,1.3,6), ringMat);
    rung.rotation.z = Math.PI/2; // along X
    rung.position.set(0, Math.cos(a)*R, Math.sin(a)*R);
    spinning.add(rung);
  }
  
  // axle
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,1.4,8), frameMat);
  axle.rotation.z = Math.PI/2;
  spinning.add(axle);
  
  group.userData.spinning = spinning;
  return group;
}
```

Wait, the rungs: cylinder along Y by default, rotate PI/2 about Z → along X. Position at (0, R cos a, R sin a). Good, these are the "tread" bars the hamster holds.

The torus is in YZ plane (since torus default is in XY plane!). Hmm. TorusGeometry default lies in XY plane, normal along Z. I want it in YZ plane. So rotate the ring PI/2 about X. Let me add ring.rotation.x = Math.PI/2. Then torus lies in YZ plane. Good. And rungs along X cross it. 

Let me double check: torus in XY plane means the circle is in XY, hole along Z. Rotating PI/2 about X moves it to YZ plane (circle in YZ, hole along X). Yes. So rungs along X pass through the hole and along the rim. 

So spinning group: rotate around X axis for spinning motion. spinning.rotation.x += speed*dt. Good, that spins the wheel like a real hamster wheel (axis horizontal along X).

Now hamster runs inside along Z, moving forward/back in Z. When excited it runs. Actually the wheel spins continuously anyway (idle spin) so it looks alive. Let me have it slowly spin always, and boost on click.

Let me also make a hamster occasionally "run" on the wheel by placing it inside and having it move in Z while wheel spins. That's complex; skip. Just continuous spin + click boost.

Now let me also add a food bowl (interactive-ish) — optional. The requirement says "one interactive object" so wheel suffices. But adding a food bowl as decor is nice. Let me add a food bowl with a couple seeds. Not necessarily interactive, but I can make clicking the bowl drop a seed and a hamster investigates. Let me keep it as bonus: clicking bowl spawns a seed nearby and nearby hamsters get curious. Might complicate. Let me keep just the wheel interactive to stay stable, and add food bowl as static decor with seeds.

Actually, let me make TWO interactions simple: wheel (boost) — that's the required one. Food bowl decorative.

Let me now also add bedding/sawdust: many small colored boxes as instanced or just a textured plane. Let me use a few hundred tiny random boxes (InstancedMesh) scattered on floor for sawdust. Cute.

Floor: a plane (the tray bottom) with a light wood color. Plus walls.

Cage construction:
- Tray bottom: box (the base) 
- Walls: I'll make low translucent walls (like a glass/acrylic cage) OR bar cage. Let me do a plastic base with tall clear walls and a wire top? Keep simple: a base tray with 4 low walls (height ~1.2) made of a semi-transparent material to look like acrylic, plus maybe some bars on top.

Actually a classic hamster "glass tank" or "plastic igloo cage". Let me do:
- Base tray: opaque plastic, light blue/grey
- Walls: transparent acrylic, height ~2
- Corners rounded? Keep box.

Let me make walls with VertexColors or just a transparent material.

Let me define tray:
- outer size: x=13, z=9, base height 0.5
- wall height: 2.0 above base

Walls as 4 boxes forming perimeter, transparent.

Let me compute. Base center at origin, y from 0 to 0.5 (base), walls from 0.5 to 2.5.

Wall thickness 0.2.

Inner play area for hamsters: x in [-6,6], z in [-4,4]. Keep hamster bounds matching.

Let me set hamster bounds: maxX = 5.6, maxZ = 3.4 (inside walls).

Now let me place objects:
- Wheel at x=-4.5, z=2 (near back-left)
- Food bowl at x=4.5, z=-2.5

Let me also add a little hideout/igloo (a dome) for cuteness at x=3, z=2. Optional. Let me add a simple dome "house".

Let me not overdo. Requirements: cage, floor/tray, several hamsters, one interactive object. I'll add wheel (interactive), food bowl (decor), and a small house (decor) for charm.

Now let me write the final code.

Let me handle shadows: directional light casts shadows. Set mapSize. Only base and hamsters cast; walls don't need to receive much. Let me enable shadowMap and set a few objects castShadow.

To keep performance and avoid artifacts, I'll set directional light shadow mapSize 1024 or 2048.

Let me write everything.

Also add orbit controls with damping, and limit polar angle so you can't go below floor too much, and set target to center.

Let me finalize the mouse interaction with raycaster:

```javascript
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
window.addEventListener('click', (e) => {
  pointer.x = (e.clientX / innerWidth)*2 -1;
  pointer.y = -(e.clientY/innerHeight)*2+1;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(wheel.children, true);
  if (hits.length) {
    boostWheel();
  }
});
```

boostWheel: set spinning rotation speed high for ~2s, set excited=true for hamsters for ~2s, maybe spawn hearts? Let me add a little particle burst of hearts or stars. Fun. Let me spawn a few floating stars.

Let me add simple floating emoji-like sprites? Too much. Let me just do a quick scale pulse on the wheel and spin boost.

Actually let me add tiny paper/confetti: create N small planes with random colors that fly up and fall. Simple. Or skip. Let me add a "spark" - a few small cubes that pop up. Keep minimal but fun.

Let me add confetti on click:

```javascript
let confetti = [];
function spawnConfetti(pos){
  for(let i=0;i<20;i++){
    const g = new THREE.BoxGeometry(0.08,0.08,0.08);
    const m = new THREE.MeshBasicMaterial({color: new THREE.Color().setHSL(Math.random(),0.8,0.6)});
    const c = new THREE.Mesh(g,m);
    c.position.copy(pos);
    c.userData.vel = new THREE.Vector3((Math.random()-0.5)*3, Math.random()*3+1, (Math.random()-0.5)*3);
    confetti.push(c);
    scene.add(c);
  }
}
```

Update each: velocity y -= gravity*dt, move, rotate. Remove after 2s.

Good, adds fun.

Now let me write the complete file. I'll be careful with syntax.

Let me also make sure the module imports work. Use unpkg three@0.160.0.

Let me write it all out now.

One concern: MeshToonMaterial requires a gradient map for toon; without it, it still renders (toon without gradient uses a basic 2-tone? Actually MeshToonMaterial needs gradientMap for proper toon, but works without as basic). To be safe and colorful, I'll use MeshStandardMaterial with roughness for a nice matte look, or MeshLambertMaterial. Let me use MeshStandardMaterial with roughness 0.9 for a soft look, and it responds to lights nicely. "Cute low-poly colorful" — standard materials with good lighting look great.

Let me use MeshStandardMaterial for hamsters and objects, metalness ~0, roughness ~0.8.

Eyes: MeshBasicMaterial black (so they're always dark, no shading weirdness). Nose pink basic.

Let me finalize.

Let me write the animation for legs:

```javascript
function animateLegs(legs, phase) {
  // legs: array of {pivot, phase}
  for (const leg of legs) {
    const s = Math.sin(phase + leg.phase) * 0.6;
    leg.pivot.rotation.x = s;
  }
}
```

Each leg pivot has a phase offset (0, PI, PI/2, -PI/2) for natural gait.

Let me store legs in the hamster object.

Let me build hamster:

```javascript
function createHamster(color) {
  const h = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color, roughness:0.85, metalness:0 });
  const dark = new THREE.MeshBasicMaterial({ color: 0x111111 });
  const pink = new THREE.MeshBasicMaterial({ color: 0xffb0b0 });
  
  // body
  const bodyGeo = new THREE.IcosahedronGeometry(0.5, 0);
  const body = new THREE.Mesh(bodyGeo, fur);
  body.scale.set(1, 0.95, 1.25);
  body.position.y = 0.45;
  body.castShadow = true;
  h.add(body);
  
  // head group (for bobbing)
  const head = new THREE.Group();
  head.position.set(0.55, 0.5, 0);
  h.add(head);
  
  const headGeo = new THREE.IcosahedronGeometry(0.38, 0);
  const headMesh = new THREE.Mesh(headGeo, fur);
  headMesh.scale.set(1, 0.9, 1.1);
  headMesh.castShadow = true;
  head.add(headMesh);
  
  // ears
  const earGeo = new THREE.ConeGeometry(0.13, 0.22, 6);
  const earL = new THREE.Mesh(earGeo, fur);
  earL.position.set(-0.05, 0.3, 0.14);
  earL.rotation.z = 0.2;
  const earR = new THREE.Mesh(earGeo, fur);
  earR.position.set(-0.05, 0.3, -0.14);
  earR.rotation.z = 0.2;
  head.add(earL, earR);
  
  // eyes
  const eyeGeo = new THREE.SphereGeometry(0.065, 8, 8);
  const eyeL = new THREE.Mesh(eyeGeo, dark);
  eyeL.position.set(0.22, 0.08, 0.14);
  const eyeR = new THREE.Mesh(eyeGeo, dark);
  eyeR.position.set(0.22, 0.08, -0.14);
  head.add(eyeL, eyeR);
  
  // eye shine
  const shineGeo = new THREE.SphereGeometry(0.02, 6, 6);
  const shineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const sL = new THREE.Mesh(shineGeo, shineMat); sL.position.set(0.24,0.1,0.16);
  const sR = sL.clone(); sR.position.z = -0.16;
  head.add(sL, sR);
  
  // nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 8), pink);
  nose.position.set(0.36, 0.0, 0);
  head.add(nose);
  
  // cheeks (blush) cute
  const cheekMat = new THREE.MeshBasicMaterial({ color: 0xffcccc, transparent:true, opacity:0.5 });
  const cL = new THREE.Mesh(new THREE.SphereGeometry(0.07,8,8), cheekMat);
  cL.position.set(0.18, 0.0, 0.2);
  const cR = cL.clone(); cR.position.z = -0.2;
  head.add(cL, cR);
  
  // legs
  const legs = [];
  const legPivotGeo = null;
  const legMat = fur;
  const footGeo = new THREE.BoxGeometry(0.12,0.12,0.14);
  const positions = [
    {x:0.3, z:0.25, phase:0},       // front right
    {x:0.3, z:-0.25, phase:Math.PI},// front left
    {x:-0.32, z:0.25, phase:Math.PI/2}, // back right
    {x:-0.32, z:-0.25, phase:-Math.PI/2}, // back left
  ];
  for (const p of positions) {
    const pivot = new THREE.Group();
    pivot.position.set(p.x, 0.3, p.z);
    h.add(pivot);
    const legMesh = new THREE.Mesh(new THREE.BoxGeometry(0.1,0.24,0.1), fur);
    legMesh.position.y = -0.12;
    legMesh.castShadow = true;
    pivot.add(legMesh);
    legs.push({ pivot, phase: p.phase });
  }
  
  // tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.06,6,6), pink);
  tail.position.set(-0.6, 0.42, 0);
  h.add(tail);
  
  h.userData = { head, legs, body };
  return h;
}
```

Wait, the head local coordinates: head group at (0.55,0.5,0) in hamster space. Within head, features positioned relative to head center. Eye at (0.22, 0.08, 0.14) relative to head → world (0.77, 0.58, 0.14). Nose at (0.36,0,0) → world (0.91,0.5,0). Good, head faces +x.

Ears at head-local (-0.05, 0.3, ±0.14) → near top-back of head. Good.

The head group can bob: during walk, rotate head.z slightly or y. During pause, idle.

Legs pivots at body: (0.3,0.3,0.25) etc. Body center at y=0.45, so pivot at y=0.3 is slightly below center, feet reach to ~0. Good.

Now hamster standing: body at y=0.45. Feet at y~0 (ground = tray bottom at y=0). Good.

Now the movement uses h.position (world) and h.rotation.y.

Let me write the Hamster class wrapping createHamster.

Let me define scene-level functions: clamp, randRange, lerpAngle.

Let me now also handle the excited boost affecting hamsters.

Alright, writing final code. Let me assemble.

I'll write the animation loop with clock.

Let me make sure to remove old confetti properly.

Let me write clamp:
```javascript
const clamp = (v,a,b)=>Math.max(a,Math.min(b,v));
```

randRange:
```javascript
const rand = (a,b)=>a+Math.random()*(b-a);
```

lerpAngle for smooth rotation:
```javascript
function lerpAngle(a,t,fast){
  // shortest path
  let diff = t - a;
  while(diff > Math.PI) diff -= Math.PI*2;
  while(diff < -Math.PI) diff += Math.PI*2;
  return a + diff*clamp(fast,0,1);
}
```

Now the Hamster class:

```javascript
class Hamster {
  constructor(scene, color) {
    this.mesh = createHamster(color);
    scene.add(this.mesh);
    const p = new THREE.Vector3(rand(-4,4), 0, rand(-2.5,2.5));
    this.mesh.position.copy(p);
    this.mesh.rotation.y = rand(0, Math.PI*2);
    this.speed = rand(0.9, 1.4);
    this.state = 'walk';
    this.timer = rand(0, 1);
    this.phase = 0;
    this.excited = 0;
    this.pickTarget();
  }
  
  pickTarget() {
    this.target = new THREE.Vector3(rand(-4.5,4.5), 0, rand(-3,3));
    this.state = 'walk';
    this.timer = 0;
  }
  
  setState(s){ this.state = s;
    if (s==='pause') this.timer = rand(1.2, 3);
    if (s==='turn') { this.timer = rand(0.4,0.9); this.dir = Math.random()<0.5?1:-1; }
  }
  
  update(dt, clock) {
    const m = this.mesh;
    if (this.excited > 0) this.excited -= dt;
    
    if (this.state === 'walk') {
      const dx = this.target.x - m.position.x;
      const dz = this.target.z - m.position.z;
      const d = Math.hypot(dx,dz);
      if (d > 0.2) {
        const desired = Math.atan2(dx, dz);
        m.rotation.y = lerpAngle(m.rotation.y, desired, dt*6);
        const sp = this.speed * (this.excited>0?2.2:1);
        m.position.x += (dx/d) * sp * dt;
        m.position.z += (dz/d) * sp * dt;
        this.phase += dt * (6 + sp*2);
        for (const leg of this.mesh.userData.legs) {
          leg.pivot.rotation.x = Math.sin(this.phase + leg.phase) * 0.55;
        }
        // body bob
        m.userData.body.position.y = 0.45 + Math.abs(Math.sin(this.phase))*0.02;
      } else {
        this.setState('pause');
      }
    } else if (this.state === 'pause') {
      this.timer -= dt;
      // gentle breathing + peek
      const b = 1 + Math.sin(clock*2)*0.015;
      m.scale.set(b, 1/Math.sqrt(b), b);
      // small random head turn
      this.mesh.userData.head.rotation.y = Math.sin(clock*1.5)*0.2;
      if (this.timer <= 0) {
        if (Math.random() < 0.3) this.setState('turn');
        else this.pickTarget();
      }
    } else if (this.state === 'turn') {
      this.timer -= dt;
      m.rotation.y += this.dir * dt * 4;
      if (this.timer <= 0) this.pickTarget();
    }
    
    // clamp within cage
    m.position.x = clamp(m.position.x, -5.4, 5.4);
    m.position.z = clamp(m.position.z, -3.6, 3.6);
  }
}
```

Note scale set: setting x=z=b and y=1/b keeps volume approx. Fine.

Hmm the head turn during pause: head is a child; rotating its y moves eyes. OK.

Now scene building and loop.

Let me write main:

```javascript
const app = document.getElementById('app');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xbfe3ff);
scene.fog = new THREE.Fog(0xbfe3ff, 18, 34);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(6, 7, 10);

const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
app.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1, 0);
controls.minDistance = 6;
controls.maxDistance = 24;
controls.maxPolarAngle = Math.PI * 0.49; // don't go below floor
controls.update();
```

Lights:
```javascript
const hemi = new THREE.HemisphereLight(0xffffff, 0x444420, 0.9);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff4e5, 1.1);
sun.position.set(6, 12, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 40;
const d = 10;
sun.shadow.camera.left=-d; sun.shadow.camera.right=d; sun.shadow.camera.top=d; sun.shadow.camera.bottom=-d;
sun.shadow.bias = -0.0005;
scene.add(sun);
const fill = new THREE.DirectionalLight(0x88aaff, 0.4);
fill.position.set(-5,4,-6);
scene.add(fill);
```

Cage:
```javascript
const cage = new THREE.Group();
scene.add(cage);

const trayMat = new THREE.MeshStandardMaterial({ color:0x6ec6ff, roughness:0.6 });
const base = new THREE.Mesh(new THREE.BoxGeometry(13,0.6,9), trayMat);
base.position.y = 0.3;
base.castShadow = true; base.receiveShadow = true;
cage.add(base);

// inner floor (bedding color)
const floorMat = new THREE.MeshStandardMaterial({ color:0xfff3d6, roughness:1 });
const floor = new THREE.Mesh(new THREE.PlaneGeometry(12.6, 8.6), floorMat);
floor.rotation.x = -Math.PI/2;
floor.position.y = 0.61;
floor.receiveShadow = true;
cage.add(floor);

// walls (acrylic)
const wallMat = new THREE.MeshStandardMaterial({ color:0xbfe8ff, transparent:true, opacity:0.35, roughness:0.1, metalness:0.2, side: THREE.DoubleSide });
const wallH = 2.2;
const walls = [
  {w:13, x:0, z:4.5}, {w:13, x:0, z:-4.5},
  {w:9, x:6.5, z:0}, {w:9, x:-6.5, z:0}
];
for (const wl of walls) {
  const w = new THREE.Mesh(new THREE.BoxGeometry(wl.w, wallH, 0.15), wallMat);
  w.position.set(wl.x, 0.6+wallH/2, wl.z);
  cage.add(w);
}
```

Hmm the walls at z=±4.5 with width 13 but the base is 13 wide too; wall thickness 0.15 centered. Fine. Side walls at x=±6.5 width 9. Good.

Bedding (sawdust) instanced:
```javascript
const bedMat = new THREE.MeshStandardMaterial({ roughness:1 });
const bedCount = 260;
const bedGeo = new THREE.BoxGeometry(0.12,0.12,0.12);
const bedMesh = new THREE.InstancedMesh(bedGeo, bedMat, bedCount);
const dummy = new THREE.Object3D();
const bedColors = [0xd9b382, 0xe8c07d, 0xcfa26a, 0xf0d9a0];
for (let i=0;i<bedCount;i++){
  dummy.position.set(rand(-5.6,5.6), 0.62, rand(-3.6,3.6));
  dummy.rotation.set(0, rand(0,6.28), 0);
  const s = rand(0.5,1.4); dummy.scale.set(s,s,s);
  dummy.updateMatrix();
  bedMesh.setMatrixAt(i, dummy.matrix);
  bedMesh.setColorAt(i, new THREE.Color(bedColors[i%bedColors.length]));
}
bedMesh.castShadow=false; bedMesh.receiveShadow=false;
cage.add(bedMesh);
```

Wheel:
```javascript
const wheel = buildWheel();
wheel.position.set(-4.5, 0.6, 2.2);
cage.add(wheel);
```

Food bowl:
```javascript
function buildBowl(){
  const g = new THREE.Group();
  const bowlMat = new THREE.MeshStandardMaterial({ color:0xffd166, roughness:0.5 });
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.45,0.3,0.25,12,1,true), bowlMat);
  bowl.position.y = 0.125;
  bowl.castShadow=true;
  g.add(bowl);
  // inner
  const foodMat = new THREE.MeshStandardMaterial({ color:0x8d5b45, roughness:1 });
  const kibble = new THREE.BoxGeometry(0.08,0.08,0.08);
  for (let i=0;i<10;i++){
    const k = new THREE.Mesh(kibble, foodMat);
    k.position.set(rand(-0.3,0.3), 0.22, rand(-0.3,0.3));
    k.rotation.set(rand(0,3),rand(0,3),rand(0,3));
    g.add(k);
  }
  return g;
}
const bowl = buildBowl();
bowl.position.set(4.5, 0.6, -2.4);
cage.add(bowl);
```

House (dome):
```javascript
function buildHouse(){
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color:0xca9eff, roughness:0.85 });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(0.7, 12, 8, 0, Math.PI*2, 0, Math.PI/2), mat);
  dome.rotation.x = 0;
  dome.position.y = 0;
  const door = new THREE.Mesh(new THREE.CircleGeometry(0.28, 12, Math.PI, Math.PI), new THREE.MeshStandardMaterial({ color:0x5a3a6b, roughness:1, side:DoubleSide }));
  // entrance hole as darker plane
  ...
}
```

Keep house simple: a dome with a dark entrance. Let me do a simple igloo: half sphere + a box base with a circular door (using a dark plane). Might be fiddly. Let me just do a dome (half sphere) colored, with a small dark cone "roof"? Overkill.

Let me make a simple house: a box with a pyramid roof (cute). 
```javascript
const walls = new THREE.Mesh(new THREE.BoxGeometry(1,0.8,1), houseMat);
walls.position.y=0.4;
const roof = new THREE.Mesh(new THREE.ConeGeometry(0.85,0.5,4), roofMat);
roof.rotation.y = Math.PI/4;
roof.position.y=0.8+0.25;
// door
const door = new THREE.Mesh(new THREE.CircleGeometry(0.22,12), darkMat);
door.position.set(0,0.25,0.51);
g.add(walls,roof,door);
```

Place house at (3, 0.6, 2.2).

Add a little sign/text? No, keep DOM info.

Hamsters:
```javascript
const palette = [0xf5c6a0, 0xd9a06b, 0xfff4e6, 0xcbb090, 0xe8c07d, 0xc97b5e];
const hamsters = [];
for (let i=0;i<5;i++){
  hamsters.push(new Hamster(scene, palette[i%palette.length]));
}
```

Wheel spin & interaction:
```javascript
let wheelSpeed = 0.3;
const spinning = wheel.userData.spinning;
raycaster...
function boost(){
  wheelBoost = 2.5; // added speed for ~1.5s
  excitedAll = 1.5;
  for (const hs of hamsters) hs.excited = 1.5;
  spawnConfetti(spinning.getWorldPosition(new THREE.Vector3()));
}
```

In loop:
```javascript
if (wheelBoost > 0) { wheelSpeed = 0.3 + wheelBoost*1.5; wheelBoost -= dt; }
else wheelSpeed = 0.3;
spinning.rotation.x += wheelSpeed * dt;
```

Hmm excited set per hamster, decay in update.

Confetti update as described.

Pointer click handler as above. Also add 'touchstart'? Keep click.

Resize handler.

Let me write spawnConfetti and update.

Let me now write the full final file and review.

I realize I should double check the torus orientation and rungs. Let me set ring.rotation.x = Math.PI/2 in buildWheel. And rungs along X. Good.

Also the hamster running on wheel isn't implemented (only boost). That's fine, satisfies "interacting with one object" loosely (they get excited by it). Actually requirement: "Hamsters should have simple autonomous behavior: walking, pausing, turning, or interacting with one object." The "interacting with one object" — I interpret as each hamster interacts with objects (like the bowl/house) OR the scene has interaction. My boost-on-click makes hamsters interact with the wheel. Good enough. Also they walk around objects. Fine.

Let me make sure everything is within one file and runs.

Let me also add a subtle idle wheel spin so it looks alive even without clicking.

Let me write final code and then a brief explanation.

Let me reconsider the head group position vs body. Body center at (0,0.45,0) in hamster local. Head group at (0.55,0.5,0). Head mesh radius 0.38. So head front extends to x ~ 0.55+0.55*1.1 ≈ 1.15 in local? head mesh scaled 1.1 in x, radius 0.38 → extends to 0.38*1.1=0.418 from head center → world x = 0.55+0.418=0.968. Body extends to x=0.5*1.25=0.625. So head pokes out front of body. Good, neck area overlaps.

Ears at head-local (-0.05,0.3,...) → world (0.5, 0.8, ...) near top of head (head top at 0.5+0.38=0.88). Good.

Eyes at head-local (0.22,0.08,0.14) → world (0.77,0.58,0.14). Head center y=0.5, eye y local 0.08 → world 0.58. Good, eyes near top-front of head.

Nose at head-local (0.36,0,0) → world (0.91,0.5,0). Front of nose. Good.

Cheeks at (0.18,0,±0.2) local → world (0.73,0.5,±0.2). Good.

Looks reasonable.

Now legs: pivot at (0.3,0.3,0.25). Body bottom at 0.45-0.5*0.95≈0.45-0.475=0.0? Body scaled y 0.95, radius 0.5 → half-height 0.475, center 0.45 → bottom at -0.025 (slightly below ground 0.6? no). Wait ground is at y=0.6 (tray top). Body center world y = hamster.position.y(0) + 0.45 = 0.45. That's BELOW the tray top 0.6! Problem.

Oh no. The hamster sits at y=0 (mesh.position.y=0) but the floor/tray top is at y=0.6. So hamster would be 0.6 below floor. I need hamster positioned at y=0.6 or raise floor to 0.

Let me set hamster base position y = 0.6 (the tray top). In Hamster constructor, p.y = 0.6. And legs pivot at local y=0.3 → world 0.9, feet at 0.6. Good, feet touch tray.

Body center local 0.45 → world 1.05. Good, above floor.

Let me update constructor to y=0.6. And pickTarget y stays 0.6 (I set target y=0 but only x,z used). Fine.

Also wheel position y=0.6 (I set 0.6). Posts from base. Wheel center at local y=1.05 → world 1.65. Radius 0.85 → bottom of wheel at world 1.65-0.85=0.8, above floor 0.6. Good, hamster can run inside (hamster radius ~0.5, center at 1.05, wheel center 1.65, inner radius ~0.85-0.06=0.79; hamster fits).

Food bowl at y=0.6. House at y=0.6.

Great.

Let me also ensure hamster bounds inside walls: walls at z=±4.5 (inner ~±4.4), x at ±6.5 (inner ±6.4). Hamster radius ~0.6+0.4(head)=~1.0 front. Keep target within ±5.4 x, ±3.6 z as I set. Good.

Now let me write final.

Let me reconsider: I set hamster pickTarget rand(-4.5,4.5) and clamp ±5.4/±3.6. Good.

Let me write the whole thing out cleanly now.

I'll include a small loading note? Not needed since module loads quickly.

Let me also guard: if THREE not defined? With importmap it's fine.

Let me write.

Final check on OrbitControls maxPolarAngle: Math.PI*0.49 keeps camera above horizon. Good.

Let me produce the final answer with the full index.html and a short description.

I'll keep the explanation brief per instructions.

Let me write it.
</think>

# 🐹 Low-Poly Hamster Playground

Here's a complete, self-contained `index.html`. Just save it and open it in any modern browser — no build step, no dependencies beyond the Three.js CDN.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; height: 100%; background: #bfe3ff; }
  #app { width: 100vw; height: 100vh; display: block; }
  #info {
    position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
    font-family: 'Comic Sans MS', 'Segoe UI', system-ui, sans-serif;
    color: #fff; background: rgba(20,30,50,0.35);
    padding: 10px 18px; border-radius: 20px; font-size: 14px; line-height: 1.5;
    pointer-events: none; user-select: none; text-align: center;
    backdrop-filter: blur(4px); box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  }
  #info b { color: #ffe37a; }
</style>
</head>
<body>
<div id="app"></div>
<div id="info">
  <b>🐹 Low-Poly Hamster Playground</b><br>
  Drag to rotate · Scroll to zoom · <b>Click the wheel!</b>
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

/* ------------------------------------------------------------------ */
/*  Tiny helpers                                                      */
/* ------------------------------------------------------------------ */
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const rand  = (a, b) => a + Math.random() * (b - a);

function lerpAngle(a, t, amount) {
  let diff = t - a;
  while (diff > Math.PI)  diff -= Math.PI * 2;
  while (diff < -Math.PI) diff += Math.PI * 2;
  return a + diff * clamp(amount, 0, 1);
}

/* ------------------------------------------------------------------ */
/*  Renderer / Camera / Scene                                         */
/* ------------------------------------------------------------------ */
const app = document.getElementById('app');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xbfe3ff);
scene.fog = new THREE.Fog(0xbfe3ff, 20, 36);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(7, 8, 11);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
app.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1.2, 0);
controls.minDistance = 6;
controls.maxDistance = 24;
controls.maxPolarAngle = Math.PI * 0.49; // keep camera above the floor
controls.update();

/* ------------------------------------------------------------------ */
/*  Lights                                                            */
/* ------------------------------------------------------------------ */
scene.add(new THREE.HemisphereLight(0xffffff, 0x444420, 0.95));

const sun = new THREE.DirectionalLight(0xfff4e5, 1.15);
sun.position.set(7, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 45;
const sd = 11;
sun.shadow.camera.left = -sd; sun.shadow.camera.right = sd;
sun.shadow.camera.top = sd;   sun.shadow.camera.bottom = -sd;
sun.shadow.bias = -0.0004;
scene.add(sun);

const fill = new THREE.DirectionalLight(0x88aaff, 0.45);
fill.position.set(-6, 5, -7);
scene.add(fill);

/* ------------------------------------------------------------------ */
/*  The Cage (tray + translucent walls)                               */
/* ------------------------------------------------------------------ */
const cage = new THREE.Group();
scene.add(cage);

const trayMat = new THREE.MeshStandardMaterial({ color: 0x6ec6ff, roughness: 0.6 });
const base = new THREE.Mesh(new THREE.BoxGeometry(13, 0.6, 9), trayMat);
base.position.y = 0.3;
base.castShadow = true; base.receiveShadow = true;
cage.add(base);

const floorMat = new THREE.MeshStandardMaterial({ color: 0xfff3d6, roughness: 1 });
const floor = new THREE.Mesh(new THREE.PlaneGeometry(12.6, 8.6), floorMat);
floor.rotation.x = -Math.PI / 2;
floor.position.y = 0.61;
floor.receiveShadow = true;
cage.add(floor);

const wallMat = new THREE.MeshStandardMaterial({
  color: 0xbfe8ff, transparent: true, opacity: 0.32,
  roughness: 0.1, metalness: 0.2, side: THREE.DoubleSide
});
const wallH = 2.2;
for (const wl of [
  { w: 13, x: 0,  z: 4.5 }, { w: 13, x: 0,  z: -4.5 },
  { w: 9,  x: 6.5, z: 0 },  { w: 9,  x: -6.5, z: 0 }
]) {
  const w = new THREE.Mesh(new THREE.BoxGeometry(wl.w, wallH, 0.15), wallMat);
  w.position.set(wl.x, 0.6 + wallH / 2, wl.z);
  cage.add(w);
}

/* Sawdust / bedding scattered on the floor */
const bedColors = [0xd9b382, 0xe8c07d, 0xcfa26a, 0xf0d9a0, 0xd0a06a];
const bedMesh = new THREE.InstancedMesh(
  new THREE.BoxGeometry(0.12, 0.12, 0.12),
  new THREE.MeshStandardMaterial({ roughness: 1 }),
  300
);
const dummy = new THREE.Object3D();
for (let i = 0; i < 300; i++) {
  dummy.position.set(rand(-5.6, 5.6), 0.63, rand(-3.6, 3.6));
  dummy.rotation.y = rand(0, Math.PI * 2);
  const s = rand(0.5, 1.5);
  dummy.scale.set(s, s, s);
  dummy.updateMatrix();
  bedMesh.setMatrixAt(i, dummy.matrix);
  bedMesh.setColorAt(i, new THREE.Color(bedColors[i % bedColors.length]));
}
cage.add(bedMesh);

/* ------------------------------------------------------------------ */
/*  Props                                                             */
/* ------------------------------------------------------------------ */
// --- Interactive exercise wheel -------------------------------------
function buildWheel() {
  const group = new THREE.Group();
  const frameMat = new THREE.MeshStandardMaterial({ color: 0x5c9cff, roughness: 0.5 });
  const ringMat  = new THREE.MeshStandardMaterial({ color: 0xff5252, roughness: 0.45, metalness: 0.15 });

  const base = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.14, 1.5), frameMat);
  base.position.y = 0.07; base.castShadow = true;
  group.add(base);

  const postGeo = new THREE.CylinderGeometry(0.07, 0.07, 1.05, 8);
  const postL = new THREE.Mesh(postGeo, frameMat); postL.position.set(-0.75, 0.6, 0.55);
  const postR = new THREE.Mesh(postGeo, frameMat); postR.position.set(-0.75, 0.6, -0.55);
  group.add(postL, postR);

  const spinning = new THREE.Group();
  spinning.position.set(0, 1.1, 0);
  group.add(spinning);

  const R = 0.85;
  const ring = new THREE.Mesh(new THREE.TorusGeometry(R, 0.06, 8, 30), ringMat);
  ring.rotation.x = Math.PI / 2; // lie in YZ plane
  spinning.add(ring);

  for (let i = 0; i < 16; i++) {
    const a = (i / 16) * Math.PI * 2;
    const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.35, 6), ringMat);
    rung.rotation.z = Math.PI / 2; // along X
    rung.position.set(0, Math.cos(a) * R, Math.sin(a) * R);
    spinning.add(rung);
  }
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.5, 8), frameMat);
  axle.rotation.z = Math.PI / 2;
  spinning.add(axle);

  group.userData.spinning = spinning;
  return group;
}
const wheel = buildWheel();
wheel.position.set(-4.5, 0.6, 2.4);
cage.add(wheel);
const spinning = wheel.userData.spinning;

// --- Food bowl ------------------------------------------------------
function buildBowl() {
  const g = new THREE.Group();
  const bowlMat = new THREE.MeshStandardMaterial({ color: 0xffd166, roughness: 0.5 });
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.3, 0.25, 14, 1, true, 0, Math.PI * 2), bowlMat);
  bowl.position.y = 0.125; bowl.castShadow = true;
  g.add(bowl);
  const foodMat = new THREE.MeshStandardMaterial({ color: 0x8d5b45, roughness: 1 });
  for (let i = 0; i < 12; i++) {
    const k = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 0.08), foodMat);
    k.position.set(rand(-0.3, 0.3), 0.24, rand(-0.3, 0.3));
    k.rotation.set(rand(0, 3), rand(0, 3), rand(0, 3));
    g.add(k);
  }
  return g;
}
const bowl = buildBowl();
bowl.position.set(4.5, 0.6, -2.4);
cage.add(bowl);

// --- Cute little house ----------------------------------------------
function buildHouse() {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0xca9eff, roughness: 0.85 });
  const roofMat = new THREE.MeshStandardMaterial({ color: 0x8a5cff, roughness: 0.85 });
  const walls = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.85, 1.1), mat);
  walls.position.y = 0.425; walls.castShadow = true; walls.receiveShadow = true;
  g.add(walls);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(0.9, 0.55, 4), roofMat);
  roof.rotation.y = Math.PI / 4;
  roof.position.y = 0.85 + 0.28;
  g.add(roof);
  const door = new THREE.Mesh(
    new THREE.CircleGeometry(0.26, 14, Math.PI, Math.PI),
    new THREE.MeshStandardMaterial({ color: 0x3a2340, roughness: 1 })
  );
  door.position.set(0, 0.28, 0.555);
  g.add(door);
  return g;
}
const house = buildHouse();
house.position.set(3.0, 0.6, 2.3);
house.rotation.y = -0.5;
cage.add(house);

/* ------------------------------------------------------------------ */
/*  Hamster model                                                     */
/* ------------------------------------------------------------------ */
function createHamster(color) {
  const h = new THREE.Group();
  const fur  = new THREE.MeshStandardMaterial({ color, roughness: 0.85 });
  const dark = new THREE.MeshBasicMaterial({ color: 0x151515 });
  const pink = new THREE.MeshBasicMaterial({ color: 0xffb0b0 });
  const shineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });

  // body
  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.5, 0), fur);
  body.scale.set(1, 0.95, 1.25);
  body.position.y = 0.45;
  body.castShadow = true;
  h.add(body);

  // head group (can bob / look around)
  const head = new THREE.Group();
  head.position.set(0.55, 0.5, 0);
  h.add(head);

  const headMesh = new THREE.Mesh(new THREE.IcosahedronGeometry(0.38, 0), fur);
  headMesh.scale.set(1, 0.9, 1.1);
  headMesh.castShadow = true;
  head.add(headMesh);

  const earGeo = new THREE.ConeGeometry(0.13, 0.24, 6);
  const earL = new THREE.Mesh(earGeo, fur); earL.position.set(-0.05, 0.3, 0.14); earL.rotation.z = 0.25;
  const earR = new THREE.Mesh(earGeo, fur); earR.position.set(-0.05, 0.3, -0.14); earR.rotation.z = 0.25;
  head.add(earL, earR);

  const eyeGeo = new THREE.SphereGeometry(0.065, 8, 8);
  const eyeL = new THREE.Mesh(eyeGeo, dark); eyeL.position.set(0.22, 0.08, 0.14);
  const eyeR = new THREE.Mesh(eyeGeo, dark); eyeR.position.set(0.22, 0.08, -0.14);
  head.add(eyeL, eyeR);
  const sL = new THREE.Mesh(shineGeo = new THREE.SphereGeometry(0.02, 6, 6), shineMat); sL.position.set(0.24, 0.1, 0.16);
  const sR = new THREE.Mesh(new THREE.SphereGeometry(0.02, 6, 6), shineMat); sR.position.set(0.24, 0.1, -0.16);
  head.add(sL, sR);

  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 8), pink);
  nose.position.set(0.36, 0.0, 0);
  head.add(nose);

  const cheekMat = new THREE.MeshBasicMaterial({ color: 0xffcccc, transparent: true, opacity: 0.55 });
  const cL = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), cheekMat); cL.position.set(0.18, 0.0, 0.2);
  const cR = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), cheekMat); cR.position.set(0.18, 0.0, -0.2);
  head.add(cL, cR);

  // legs (animated pivots)
  const legs = [];
  const pos = [
    { x: 0.3,  z: 0.26, phase: 0 },
    { x: 0.3,  z: -0.26, phase: Math.PI },
    { x: -0.32, z: 0.26, phase: Math.PI / 2 },
    { x: -0.32, z: -0.26, phase: -Math.PI / 2 }
  ];
  for (const p of pos) {
    const pivot = new THREE.Group();
    pivot.position.set(p.x, 0.3, p.z);
    h.add(pivot);
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.24, 0.1), fur);
    leg.position.y = -0.12; leg.castShadow = true;
    pivot.add(leg);
    legs.push({ pivot, phase: p.phase });
  }

  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 6), pink);
  tail.position.set(-0.6, 0.42, 0);
  h.add(tail);

  h.userData = { head, legs, body };
  return h;
}

/* ------------------------------------------------------------------ */
/*  Autonomous hamster brain                                          */
/* ------------------------------------------------------------------ */
class Hamster {
  constructor(scene, color) {
    this.mesh = createHamster(color);
    scene.add(this.mesh);
    this.mesh.position.set(rand(-4, 4), 0.6, rand(-2.5, 2.5));
    this.mesh.rotation.y = rand(0, Math.PI * 2);
    this.speed = rand(0.9, 1.5);
    this.state = 'walk';
    this.phase = rand(0, Math.PI * 2);
    this.excited = 0;
    this.pickTarget();
  }

  pickTarget() {
    this.target = new THREE.Vector3(rand(-4.6, 4.6), 0, rand(-3.2, 3.2));
    this.state = 'walk';
  }

  setState(s) {
    this.state = s;
    if (s === 'pause') this.timer = rand(1.2, 3.2);
    if (s === 'turn')  { this.timer = rand(0.4, 0.9); this.dir = Math.random() < 0.5 ? 1 : -1; }
  }

  update(dt, clock) {
    const m = this.mesh;
    if (this.excited > 0) this.excited -= dt;

    if (this.state === 'walk') {
      const dx = this.target.x - m.position.x;
      const dz = this.target.z - m.position.z;
      const d = Math.hypot(dx, dz);
      if (d > 0.2) {
        const desired = Math.atan2(dx, dz);
        m.rotation.y = lerpAngle(m.rotation.y, desired, dt * 6);
        const sp = this.speed * (this.excited > 0 ? 2.3 : 1);
        m.position.x += (dx / d) * sp * dt;
        m.position.z += (dz / d) * sp * dt;
        this.phase += dt * (6 + sp * 2);
        for (const leg of this.mesh.userData.legs) {
          leg.pivot.rotation.x = Math.sin(this.phase + leg.phase) * 0.55;
        }
        this.mesh.userData.body.position.y = 0.45 + Math.abs(Math.sin(this.phase)) * 0.02;
      } else {
        this.setState('pause');
      }
    } else if (this.state === 'pause') {
      this.timer -= dt;
      const b = 1 + Math.sin(clock * 2) * 0.015; // breathing
      m.scale.set(b, 1 / Math.sqrt(b), b);
      this.mesh.userData.head.rotation.y = Math.sin(clock * 1.5) * 0.25; // looking around
      if (this.timer <= 0) {
        if (Math.random() < 0.3) this.setState('turn');
        else this.pickTarget();
      }
    } else if (this.state === 'turn') {
      this.timer -= dt;
      m.rotation.y += this.dir * dt * 4;
      if (this.timer <= 0) this.pickTarget();
    }

    // keep inside the cage
    m.position.x = clamp(m.position.x, -5.4, 5.4);
    m.position.z = clamp(m.position.z, -3.6, 3.6);
  }
}

const palette = [0xf5c6a0, 0xd9a06b, 0xfff4e6, 0xcbb090, 0xe8c07d, 0xc97b5e];
const hamsters = [];
for (let i = 0; i < 5; i++) hamsters.push(new Hamster(scene, palette[i % palette.length]));

/* ------------------------------------------------------------------ */
/*  Interaction: click the wheel -> confetti + excitement             */
/* ------------------------------------------------------------------ */
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

let confetti = [];
function spawnConfetti(worldPos) {
  for (let i = 0; i < 26; i++) {
    const c = new THREE.Mesh(
      new THREE.BoxGeometry(0.09, 0.09, 0.09),
      new THREE.MeshBasicMaterial({ color: new THREE.Color().setHSL(Math.random(), 0.85, 0.6) })
    );
    c.position.copy(worldPos);
    c.userData.vel = new THREE.Vector3(rand(-2.5, 2.5), rand(1.5, 4), rand(-2.5, 2.5));
    c.userData.spin = new THREE.Vector3(rand(4, 8), rand(4, 8), rand(4, 8));
    scene.add(c);
    confetti.push(c);
  }
}

window.addEventListener('click', (e) => {
  pointer.x =  (e.clientX / innerWidth) * 2 - 1;
  pointer.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(wheel.children, true);
  if (hits.length) {
    for (const hs of hamsters) hs.excited = 1.6; // everyone gets a burst of energy
    spawnConfetti(spinning.getWorldPosition(new THREE.Vector3()));
  }
});

/* ------------------------------------------------------------------ */
/*  Main loop                                                           */
/* ------------------------------------------------------------------ */
const clock = new THREE.Clock();
let wheelBoost = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t  = clock.elapsedTime;

  // idle wheel spin + click boost
  if (wheelBoost > 0) wheelBoost -= dt;
  spinning.rotation.x += (0.25 + wheelBoost * 3) * dt;

  for (const hs of hamsters) hs.update(dt, t);

  // confetti physics
  for (let i = confetti.length - 1; i >= 0; i--) {
    const c = confetti[i];
    c.userData.vel.y -= 9 * dt;
    c.position.addScaledVector(c.userData.vel, dt);
    c.rotation.x += c.userData.spin.x * dt;
    c.rotation.y += c.userData.spin.y * dt;
    if (c.position.y < 0.6) { scene.remove(c); confetti.splice(i, 1); }
  }

  controls.update();
  renderer.render(scene, camera);
}
animate();

/* ------------------------------------------------------------------ */
/*  Resize                                                            */
/* ------------------------------------------------------------------ */
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## How to run

1. Copy the code into a file named `index.html`.
2. Double-click it (or open it in Chrome/Firefox/Edge/Safari).
3. **Drag** to orbit the camera, **scroll** to zoom, and **click the red wheel** to launch confetti and give the hamsters a burst of energy. 🎉

## What's inside

| Feature | Details |
|---|---|
| **Cage** | Blue plastic tray, soft bedding floor, translucent acrylic walls |
| **Floor** | Wood-shade tray + ~300 instanced sawdust pieces |
| **Hamsters** | 5 procedurally-built low-poly hamsters (icosahedron bodies, cone ears, shiny eyes, pink noses/blush, animated legs, little tails) in different colors |
| **Interactive object** | Spinning exercise wheel — click it for confetti + hamster excitement |
| **Props** | Food bowl with kibbles, a little purple house |
| **Autonomous behavior** | Each hamster walks to a random target, pauses (breathing + looking around), occasionally spins around, smoothly faces its direction, and legs alternate while walking |
| **Controls** | `OrbitControls` with damping, clamped so you never clip below the floor |

It's intentionally kept lightweight and stable — no external assets, no build tooling, just Three.js from a CDN via an import map.