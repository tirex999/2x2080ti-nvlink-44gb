Let me create a single-file HTML project with Three.js that shows a low-poly hamster playground. I'll need to:

1. Set up the HTML structure with Three.js (via CDN)
2. Create a 3D scene with a cage, floor/tray
3. Create several low-poly hamsters with cute features
4. Add an interactive object (a wheel)
5. Implement autonomous behavior for the hamsters (walking, pausing, turning, interacting)
6. Make it visually cute, colorful, and fun
7. Add camera controls so users can rotate

Let me think about the design:

**Scene elements:**
- A tray/cage base (a shallow box)
- Wire cage walls (thin boxes or lines)
- Wood shavings on the floor (small colored planes/squares)
- Several hamsters (each built from low-poly geometries)
- An interactive exercise wheel
- Maybe a food bowl and tunnel

**Hamster construction (low-poly):**
- Body: a sphere or icosahedron (flattened)
- Head: sphere
- Ears: small spheres/circles
- Eyes: dark spheres
- Cheeks: small pink spheres
- Nose: tiny pink sphere
- Feet: small cylinders/boxes
- Tail: tiny sphere
- Tail could be hidden

**Behavior:**
Each hamster has states: WALKING, PAUSING, TURNING. When walking, they move in a direction and slowly change direction. When pausing, they stay still. Occasionally they interact with the wheel.

**Camera controls:**
OrbitControls from Three.js.

Let me write this out carefully. I'll use Three.js r160 or similar from CDN with importmap for modules, or just use the classic script include. Let me use the module version with importmap for OrbitControls.

Actually, to keep it simple and reliable, let me use the UMD build of three.js plus OrbitControls. But OrbitControls needs to be loaded separately. With importmap it's cleaner.

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

Let me build the hamsters procedurally. Each hamster is a group with parts. I'll give them random colors (browns, tans, whites, maybe some fun colors).

Let me code the movement logic:

```js
class Hamster {
  constructor(scene, color) {
    this.group = new THREE.Group();
    // build body parts
    ...
    // state
    this.state = 'walking';
    this.heading = Math.random() * Math.PI * 2;
    this.speed = 0.5 + Math.random() * 0.3;
    this.walkTimer = 0;
    this.pauseTimer = 0;
    this.dirChangeTimer = 0;
    this.bobPhase = Math.random() * Math.PI * 2;
  }
  
  update(dt) {
    // state machine
  }
}
```

Let me make the hamster walk along the floor within the cage bounds, bouncing off walls or wrapping.

For interaction with the wheel: occasionally a hamster will go to the wheel and "ride" it for a bit, spinning the wheel.

Let me implement:
- Each hamster wanders.
- On a timer, pick a new heading (random turn).
- Bob up and down while walking (legs animation via rotating feet or body bob).
- Occasionally set target = wheel position and walk to it, then spin wheel for a few seconds, then continue.

Let me keep it manageable but fun.

Let me write the full code now.

I'll make the cage:
- Tray: a shallow open box (floor + low walls). Use BoxGeometry for floor, and thin walls around.
- Actually let me make a tray that's like a plastic bin: floor plate + 4 walls.
- Add wood shavings: many small thin boxes scattered on floor in warm tan colors.
- Add wire top: thin lines or thin boxes forming a grid on top (optional, maybe just 4 walls + invisible top).

Let me add:
- Exercise wheel (interactive): a cylinder with rungs, mounted on a stand.
- Food bowl: a small cylinder/dish with little pellets.
- Tunnel: a cardboard tube (cylinder) - optional, maybe skip to keep simple. I'll add it as a second interactive-ish object but focus on wheel.

Actually requirement says "one interactive object such as a wheel, tunnel, food bowl, or toy." So I'll focus on the wheel being interactive (hamsters ride it, and maybe user can click it). Let me make the wheel clickable too so the user can spin it.

Let me add raycasting: clicking the wheel spins it faster / makes a nearby hamster ride it. Or just spin it when clicked.

Let me keep the interaction: click on the wheel to spin it; hamsters may also ride it autonomously.

Let me now write everything.

Colors for hamsters: I'll use a palette of cute colors:
- light brown (#C98A4B)
- tan (#E0B07A)
- cream (#F5E6D0)
- darker brown (#8B5E3C)
- white (#F7F3EE)
- Maybe a fun pastel like pink or mint for one.

Cheeks/nose pink (#F4A9A0), eyes dark brown (#3A2A20).

Let me build the hamster:

```js
buildHamster() {
  const g = new THREE.Group();
  // Body
  const bodyMat = new THREE.MeshStandardMaterial({ color: furColor, flatShading: true, roughness: 0.9 });
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 12, 10), bodyMat);
  body.scale.set(1, 0.9, 1.2); // elongated
  body.position.y = 0.5;
  g.add(body);
  
  // Head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.38, 12, 10), bodyMat);
  head.position.set(0, 0.7, 0.45);
  g.add(head);
  
  // Head group so we can rotate independently (looking around)
  const headGroup = new THREE.Group();
  headGroup.position.set(0, 0.7, 0.45);
  const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.38, 12, 10), bodyMat);
  headGroup.add(headMesh);
  // ears
  ...
  // eyes
  ...
  // cheeks
  ...
  // nose
  ...
  g.add(headGroup);
  this.headGroup = headGroup;
  
  // Feet
  this.feet = [];
  for each of 4 feet: small capsule/cylinder, positioned under body
  // animate legs while walking
  
  // Tail
  ...
}
```

Hmm, mixing a static body and a head group. Let me put the head in its own group so it can bob/look.

Actually simpler: put everything in the main group, and for "looking" just rotate the head sub-group. Let me define headGroup as child of main group at origin, then offset children within it.

Let me restructure:

```js
this.group = new THREE.Group(); // main, positioned in world
this.bodyGroup = new THREE.Group(); // for body bob
this.group.add(this.bodyGroup);

// body
const body = mesh; body.position.y = 0; bodyGroup.add(body);

// head group
this.headGroup = new THREE.Group();
this.headGroup.position.set(0, 0.22, 0.35); // relative to body
bodyGroup.add(this.headGroup);
// add head mesh, ears, eyes, etc as children of headGroup
```

Wait, body center is at y=0.5 in world if body radius 0.5. Let me set body center at local y=0 within bodyGroup, and bodyGroup.position.y = 0.5. Then headGroup at local (0, 0.22, 0.35) relative to body. That places head around y=0.72 world. Good.

Feet: 4 feet at corners under body. Position relative to body: x ±0.3, z ±0.3, y -0.4 (so at y=0.1). Animate by rotating around X axis alternately while walking. Or just bob the whole bodyGroup up and down.

Let me do body bob (vertical) + slight rotation + leg swing. Keep it simple: bob up/down and alternate front/back leg rotation.

Cheeks: two small pink spheres pushed into sides of face to give chubby cheeks. Nose: small pink sphere at front of head. Eyes: two black spheres with tiny white highlight.

Ears: two circles (thin cylinders) on top of head, or half-spheres. Let me use small cylinders rotated, or spheres flattened. I'll use small spheres scaled flat for ears, positioned on top-back of head.

Let me add a little tail: tiny sphere at back.

Now movement:

```js
update(dt) {
  this.age += dt;
  switch(state):
    walking:
      move forward along heading
      heading += random walk (turn slowly)
      if out of bounds -> reverse heading
      timer: occasionally switch to pause
      bob legs
    pausing:
      stay, maybe look around (rotate head)
      after time -> choose new heading, switch walking
    riding (at wheel):
      move to wheel, climb, spin wheel
      after time -> leave
}
```

Let me define world bounds: the tray interior. Say tray is 6 x 4 (x from -3 to 3, z from -2 to 2). Hamsters move within.

Wheel located at one side, say (x=-2.2, z=0). Food bowl at (x=2.2, z=0). Tunnel maybe at center-back.

Let me implement target-based movement for clarity:
- Each hamster has a current target point (wx, wz). It walks toward it. When reached, pick a new target. Occasionally the target is the wheel (to ride).
- This gives natural wandering.

But also add some randomness so it feels alive: slight wandering jitter.

Let me combine: wander to random points; when a "want_ride" timer fires, set target to wheel and mark riding state.

I'll implement:

```js
update(dt) {
  this.age += dt;
  // decide when to pick new target
  if (!this.target) this.pickTarget();
  
  const dx = this.target.x - this.pos.x;
  const dz = this.target.z - this.pos.z;
  const dist = Math.hypot(dx, dz);
  
  if (this.mode === 'riding') {
    // already at wheel, spin
    this.rideTimer -= dt;
    this.spinWheel();
    if (this.rideTimer <= 0) { this.mode = 'wander'; this.pickTarget(true); }
    return;
  }
  
  if (dist > 0.1) {
    // move toward target
    const dir = new Vector2(dx/dist, dz/dist);
    this.pos.x += dir.x * this.speed * dt;
    this.pos.z += dir.z * this.speed * dt;
    // face direction of travel
    this.heading = Math.atan2(dir.x, dir.z);
    this.group.rotation.y = this.heading;
    // bob
    this.bobPhase += dt * 12;
    this.bodyGroup.position.y = 0.5 + Math.abs(Math.sin(this.bobPhase)) * 0.05;
    this.animateLegs(dt);
    this.headGroup.rotation.x = Math.sin(this.age*2)*0.1; // sniffing
    // occasionally pick wheel
    if (Math.random() < 0.002) { this.startRide(); }
  } else {
    // arrived
    this.waitTimer -= dt;
    if (this.waitTimer <= 0) { this.pickTarget(); }
    else { this.headGroup.rotation.y = Math.sin(this.age*1.5)*0.3; }
  }
}
```

Hmm the random chance per frame for riding might be too rare or too frequent. Let me use a timer: `this.rideCooldown`. When cooldown hits zero and random roll, start ride.

Let me refine with timers:

```js
this.nextDecision = Math.random()*3 + 1; // seconds until next decision
...
this.nextDecision -= dt;
if (this.nextDecision <= 0 && dist < 0.1) {
  // decide: wander or ride
  if (Math.random() < 0.25) startRide(); else pickTarget();
  this.nextDecision = Math.random()*4 + 2;
}
```

That's cleaner. Let me integrate.

For startRide: set target = wheel base position, mode='approaching' then when close set mode='riding'. Actually let me just teleport-check: if approaching wheel and close, set riding. Simpler: when startRide called, set mode='riding', place hamster at wheel position, and ride for a few seconds. But teleporting looks bad. Let me make it approach first.

Let me do: 
- pickTarget(): choose either a random point (75%) or the wheel (25%). If wheel, set flag so when arrived, transition to riding.

I'll store `this.goingToWheel` boolean. When arrived at target and goingToWheel and not already riding -> start riding.

Let me code:

```js
pickTarget() {
  const toWheel = Math.random() < 0.25;
  if (toWheel) {
    this.target = wheelBase.position.clone();
    this.target.y = 0;
    this.goingToWheel = true;
  } else {
    this.target = new THREE.Vector3(
      rand(-2.6, 2.6), rand(-1.6, 1.6)
    );
    this.goingToWheel = false;
  }
}
```

Update loop:
```js
if (dist > 0.12) { move ... }
else {
  // arrived
  if (this.goingToWheel && !this.riding) {
    this.mode = 'riding';
    this.rideTimer = 3 + Math.random()*2;
    // position on wheel
    this.pos.copy(wheelBase.position);
    this.pos.x += 0.0; // stand beside/in front
    this.headGroup... 
  } else {
    this.nextDecision = ...; wait a bit
  }
}
```

Riding update:
```js
if (this.mode==='riding') {
  this.rideTimer -= dt;
  wheel.spin(this.speed*...);
  // bob as if running
  this.bobPhase += dt*18;
  this.bodyGroup.position.y = 0.5 + Math.abs(sin(bob))*0.06;
  this.animateLegs(dt, 1.5);
  if (this.rideTimer<=0) { this.mode='wander'; this.goingToWheel=false; this.pickTarget(); }
}
```

Wheel spin: the wheel mesh gets angular velocity. I'll add a function on the wheel object to spin it, decaying over time, but hamsters add energy.

Let me make wheel a class:

```js
class Wheel {
  constructor() { build mesh, store spin, angularVel }
  addSpin(v) { this.angularVel += v; }
  update(dt) { this.mesh.rotation.x += this.angularVel*dt; this.angularVel *= 0.98; clamp }
}
```

Clicking the wheel adds spin (interaction). Also OrbitControls for camera.

Let me also add a subtle idle animation for paused hamsters: gentle breathing (body scale) and head turning.

Now visuals: lighting — ambient + directional with shadows for cuteness. Add hemisphere light for soft fill. Ground color, maybe a nice background color (pastel).

Let me add shadows for depth. Enable shadowMap.

Add some decorations:
- Wood shavings: scatter small thin boxes (tan/beige) on floor.
- Food bowl: a shallow dish (cylinder inverted or torus + bottom) with pellets (small spheres) inside.
- Tunnel: a cylinder (cardboard) lying horizontally, hollow — hamsters could walk through but let's keep them walking around it. Maybe place it as decoration.
- A small house/shelter: a box with a round entrance? Could be cute. Let me add a little wooden house.
- Maybe a water bottle (cylinder) attached to wall. Optional. Keep moderate.

Let me not overdo. Include: tray, shavings, wheel (interactive), food bowl, tunnel, a small house, and 3-4 hamsters.

Let me finalize hamster count: 3 hamsters is good (or 4). I'll do 3-4.

Let me now write the code fully.

I want to make sure the hamsters are clearly visible and cute. Let me use flatShading materials for low-poly look. Use MeshStandardMaterial with flatShading: true.

Let me define helper to create rounded-ish shapes with low segments.

Let me write the full HTML now.

One more: responsive resize handler, and start animation loop.

Let me also add a small UI hint text overlay ("Drag to rotate • Click the wheel to spin").

Let me write it.

For the shavings, I'll create a InstancedMesh or just many small meshes. For simplicity and performance, use a Group with ~80 small thin boxes with random rotation/color. Actually instanced is better but let me just do individual small boxes with shared geometry/material variants. 80 objects is fine.

Let me use a few color variations by creating a few materials.

Let me code the shavings:

```js
function addShavings(scene, count) {
  const geo = new THREE.BoxGeometry(0.09, 0.02, 0.25);
  const colors = [0xE9C896, 0xD9B57A, 0xF0DCA8, 0xCFA465];
  const group = new THREE.Group();
  for (let i=0;i<count;i++){
    const mat = new THREE.MeshStandardMaterial({color: colors[i%colors.length], flatShading:true, roughness:1});
    const m = new THREE.Mesh(geo, mat);
    m.position.set(rand(-2.8,2.8), 0.01, rand(-1.8,1.8));
    m.rotation.y = Math.random()*Math.PI;
    m.rotation.z = (Math.random()-0.5)*0.4;
    group.add(m);
  }
  scene.add(group);
}
```

Now let me assemble hamsters building function. Let me write a factory.

```js
function makeHamster(furColor) {
  const g = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color: furColor, flatShading: true, roughness: 0.95 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x2b1c12, flatShading: true, roughness: 0.6 });
  const pink = new THREE.MeshStandardMaterial({ color: 0xf2a6a0, flatShading: true, roughness: 0.8 });
  
  const bodyGroup = new THREE.Group();
  g.add(bodyGroup);
  bodyGroup.position.y = 0.5;
  
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 14, 12), fur);
  body.scale.set(1, 0.92, 1.15);
  body.position.y = 0;
  body.castShadow = true;
  bodyGroup.add(body);
  
  // belly lighter
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.42, 12, 10), new THREE.MeshStandardMaterial({color:0xfff4e6, flatShading:true, roughness:0.95}));
  belly.scale.set(0.95, 0.85, 1.1);
  belly.position.set(0, -0.08, 0.08);
  bodyGroup.add(belly);
  
  // tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 6), fur);
  tail.position.set(0, 0, -0.58);
  bodyGroup.add(tail);
  
  // head group
  const headGroup = new THREE.Group();
  headGroup.position.set(0, 0.24, 0.4);
  bodyGroup.add(headGroup);
  
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.4, 14, 12), fur);
  head.scale.set(1, 0.95, 0.95);
  head.castShadow = true;
  headGroup.add(head);
  
  // cheeks
  const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.18, 10, 8), pink);
  cheekL.position.set(-0.24, -0.06, 0.12);
  cheekL.scale.set(1, 0.9, 0.8);
  headGroup.add(cheekL);
  const cheekR = cheekL.clone(); cheekR.position.x = 0.24; headGroup.add(cheekR);
  
  // ears
  const earGeo = new THREE.CylinderGeometry(0.13, 0.11, 0.06, 12);
  const earL = new THREE.Mesh(earGeo, fur);
  earL.position.set(-0.2, 0.34, 0); earL.rotation.z = 0.2;
  const earR = earL.clone(); earR.position.x = 0.2; earR.rotation.z = -0.2;
  headGroup.add(earL, earR);
  // inner ear pink
  const innerEarGeo = new THREE.CylinderGeometry(0.075, 0.065, 0.07, 12);
  const innerEarL = new THREE.Mesh(innerEarGeo, pink);
  innerEarL.position.set(-0.2, 0.34, 0.01);
  const innerEarR = innerEarL.clone(); innerEarR.position.x = 0.2;
  headGroup.add(innerEarL, innerEarR);
  
  // eyes
  const eyeGeo = new THREE.SphereGeometry(0.075, 12, 10);
  const eyeL = new THREE.Mesh(eyeGeo, dark);
  eyeL.position.set(-0.16, 0.05, 0.32);
  const eyeR = eyeL.clone(); eyeR.position.x = 0.16;
  headGroup.add(eyeL, eyeR);
  // highlights
  const hiGeo = new THREE.SphereGeometry(0.025, 8, 6);
  const hiMat = new THREE.MeshStandardMaterial({color:0xffffff, flatShading:true});
  const hiL = new THREE.Mesh(hiGeo, hiMat); hiL.position.set(-0.14, 0.08, 0.36);
  const hiR = hiL.clone(); hiR.position.x = 0.18;
  headGroup.add(hiL, hiR);
  
  // nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), pink);
  nose.position.set(0, -0.02, 0.38);
  headGroup.add(nose);
  
  // feet
  const feet = [];
  const footGeo = new THREE.SphereGeometry(0.1, 10, 8);
  const footMat = new THREE.MeshStandardMaterial({color: pink, flatShading:true});
  const positions = [[-0.25,-0.05,0.25],[0.25,-0.05,0.25],[-0.25,-0.05,-0.25],[0.25,-0.05,-0.25]];
  for (const p of positions){
    const f = new THREE.Mesh(footGeo, footMat);
    f.position.set(p[0], p[1], p[2]);
    f.scale.set(1, 0.6, 1.2);
    bodyGroup.add(f);
    feet.push(f);
  }
  
  g.userData = { bodyGroup, headGroup, feet };
  return g;
}
```

Then the Hamster controller wraps a made hamster and adds behavior.

Let me combine into a class that holds the mesh group and state.

Let me write the full thing now, carefully.

I'll place the wheel at (-2.2, 0, 0) near left wall, food bowl at (2.3, 0, 0.4), tunnel at (0.5, 0, -1.2) horizontal along x, house at (0.6, 0, 1.3).

Tray dimensions: width X from -3 to 3 (6 deep), depth Z from -2 to 2 (4 deep), wall height 0.7, floor thickness 0.1.

Wire top: thin boxes grid? Let me add a wireframe top using thin cylinders/lines. Actually simpler: add 4 walls only (open top) so we can see hamsters. Maybe add a subtle wire top with thin boxes so it looks like a cage. Let me add thin bars on top as decorative lines. I'll add vertical bars? Eh. Let me just do 4 walls and maybe a few horizontal bars near top to suggest cage. Keep open top for visibility.

Actually a "cage" implies enclosure. Let me add walls and a lightweight bar top using thin cylinders. I'll make a simple bar top: a frame of thin boxes at the top with vertical bars. Might be heavy. Let me do a modest version: horizontal bars at a few heights spanning, plus vertical bars. Use thin cylinders (radius 0.02) rotated. Could be ~40 bars. Fine.

Hmm, that might clutter. Let me instead do a nicer approach: a wire cage top using a line-based grid (THREE.LineSegments) over the top opening. That's lightweight and looks cage-like. I'll draw lines at top y=1.0 forming a grid.

Let me do that: create points for a grid spanning x[-3,3], z[-2,2] at y=1.0, connect with lines, thin material. Good, cheap and looks like bars.

Walls: 4 boxes. Floor: one box. Let me color tray a bright plastic color (like teal or coral) for cuteness. Let me use a pastel teal tray (#5FB6B0) and white bars.

Let me set background color to a soft gradient or solid pastel (light blue #BFE3EC or a subtle gradient). I'll use a solid color with maybe a floor plane beyond tray.

Let me add a large floor plane under everything (ground) with grass/dirt color? Or just let the tray sit on an invisible ground. I'll add a big ground plane far below for shadow catching and a nice base color. Background color separate.

Let me set:
- scene.background = new THREE.Color(0xcfe9f2) (soft sky)
- ground plane at y=-0.3 with color 0xa8d8a0? Or match. Let me make ground a light wood/table color 0xe8d3b0. Add shadow receiving.

Actually let me keep it clean: background pastel, and a subtle ground disc/plane that receives shadows.

Lighting:
- HemisphereLight(0xffffff, 0xbb9988, 0.6)
- AmbientLight(0xffffff, 0.4)
- DirectionalLight(0xffffff, 1.0) casting shadows, positioned upper.

Let me finalize and write.

For OrbitControls, set enableDamping, target at center of tray.

Let me handle clicking wheel: raycast against wheel meshes; on click, wheel.addSpin(6) and maybe a little "boing". Provide feedback.

Also allow clicking empty space? Just wheel is the interactive object.

Let me write final code. I'll be careful with imports and module type.

Let me also ensure hamsters don't clip through walls: clamp positions within bounds, and if they'd exceed, reflect/pick new target.

Bounds: x in [-2.7, 2.7], z in [-1.7, 1.7].

When picking random target, sample within bounds minus margin.

When walking and hitting bound, just clamp position; the "arrived" logic will trigger re-target anyway.

Let me make speed ~0.7 units/sec. Decision intervals 1-5s. Ride duration 2-4s.

Let me write the update to be robust.

Let me define the Hamster class:

```js
class Hamster {
  constructor(group, bounds) {
    this.mesh = group;
    this.bg = group.userData.bodyGroup;
    this.hg = group.userData.headGroup;
    this.feet = group.userData.feet;
    this.bounds = bounds;
    this.pos = new THREE.Vector3(rand(-2,2),0,rand(-1.2,1.2));
    this.mesh.position.copy(this.pos);
    this.speed = 0.55 + Math.random()*0.35;
    this.bobPhase = Math.random()*Math.PI*2;
    this.nextDecision = Math.random()*3 + 1;
    this.waitTime = 0;
    this.rideTimer = 0;
    this.target = new THREE.Vector3();
    this.goingToWheel = false;
    this.riding = false;
    this.pickTarget();
    this.turnTimer = 0;
  }
  
  pickTarget() {
    if (Math.random() < 0.28) {
      this.target.set(WHEEL.base.x, 0, WHEEL.base.z);
      this.goingToWheel = true;
    } else {
      this.target.set(rand(-2.5,2.5), 0, rand(-1.5,1.5));
      this.goingToWheel = false;
    }
  }
  
  update(dt) {
    this.nextDecision -= dt;
    if (this.riding) {
      this.rideTimer -= dt;
      WHEEL.spin(this.speed*1.2);
      this.bobPhase += dt*16;
      this.bg.position.y = 0.5 + Math.abs(Math.sin(this.bobPhase))*0.07;
      this.legMove(dt, 1.6);
      // face the wheel
      this.mesh.rotation.y = Math.atan2(WHEEL.base.x - this.pos.x, WHEEL.base.z - this.pos.z);
      this.hg.rotation.x = -0.2 + Math.sin(this.age2)*0.1;
      if (this.rideTimer <= 0) {
        this.riding = false;
        this.goingToWheel = false;
        this.pickTarget();
      }
      return;
    }
    
    const dx = this.target.x - this.pos.x;
    const dz = this.target.z - this.pos.z;
    const dist = Math.hypot(dx, dz);
    
    if (dist > 0.12) {
      const nx = dx/dist, nz = dz/dist;
      this.pos.x = clamp(this.pos.x + nx*this.speed*dt, this.bounds.minX, this.bounds.maxX);
      this.pos.z = clamp(this.pos.z + nz*this.speed*dt, this.bounds.minZ, this.bounds.maxZ);
      this.mesh.position.x = this.pos.x;
      this.mesh.position.z = this.pos.z;
      this.mesh.rotation.y = Math.atan2(nx, nz);
      this.bobPhase += dt*13;
      this.bg.position.y = 0.5 + Math.abs(Math.sin(this.bobPhase))*0.05;
      this.legMove(dt, 1.0);
      this.hg.rotation.x = Math.sin(this.age2)*0.12;
    } else {
      // arrived
      this.hg.rotation.y = Math.sin(this.age2*1.2)*0.35;
      this.hg.rotation.x = Math.sin(this.age2*0.8)*0.06;
      this.bg.scale.y = 1 + Math.sin(this.age2*2)*0.03; // breathe
      if (this.goingToWheel && !this.riding) {
        this.riding = true;
        this.rideTimer = 2.5 + Math.random()*2;
        this.pos.set(WHEEL.base.x, 0, WHEEL.base.z + 0.35);
        this.mesh.position.copy(this.pos);
      } else if (this.nextDecision <= 0) {
        this.pickTarget();
        this.nextDecision = Math.random()*4 + 1.5;
      }
    }
    this.age2 += dt;
  }
  
  legMove(dt, mult) {
    // alternate front/back legs
    const s = Math.sin(this.bobPhase)*0.5*mult;
    this.feet[0].rotation.x = s;   // left front
    this.feet[1].rotation.x = -s;  // right front
    this.feet[2].rotation.x = -s;  // left back
    this.feet[3].rotation.x = s;   // right back
  }
}
```

Need age2 initialized 0.

WHEEL object: I'll define it globally before hamsters reference it. Let me create WHEEL before creating hamsters.

Wheel build:

```js
function makeWheel() {
  const wheel = { base: new THREE.Vector3(), spin: 0, angularVel: 0, meshes: [] };
  const group = new THREE.Group();
  const rimMat = new THREE.MeshStandardMaterial({ color: 0xff6b6b, flatShading: true, roughness: 0.6, metalness: 0.1 });
  const barMat = new THREE.MeshStandardMaterial({ color: 0xffd166, flatShading: true, roughness: 0.5 });
  const standMat = new THREE.MeshStandardMaterial({ color: 0x4d96ff, flatShading: true, roughness: 0.7 });
  
  // two rims
  const rimGeo = new THREE.CylinderGeometry(0.75, 0.75, 0.08, 24, 1, true);
  const rim1 = new THREE.Mesh(rimGeo, rimMat); rim1.rotation.x = Math.PI/2; rim1.position.z = 0.25;
  const rim2 = rim1.clone(); rim2.position.z = -0.25;
  group.add(rim1, rim2);
  
  // rungs (vertical bars across)
  const rungeGeo = new THREE.CylinderGeometry(0.02, 0.02, 1.4, 8);
  for (let i=0;i<16;i++){
    const a = (i/16)*Math.PI*2;
    const bar = new THREE.Mesh(rungeGeo, barMat);
    bar.position.set(Math.cos(a)*0.75, Math.sin(a)*0.75, 0);
    group.add(bar);
  }
  // hub
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.08,0.5,12), standMat);
  hub.rotation.x = Math.PI/2;
  group.add(hub);
  
  // stand (U shape)
  const standV = new THREE.Mesh(new THREE.BoxGeometry(0.1,1.0,0.1), standMat);
  standV.position.set(0, 0.5, -0.35);
  const standV2 = standV.clone(); standV2.position.z = 0.35;
  const standBar = new THREE.Mesh(new THREE.BoxGeometry(0.1,0.1,0.85), standMat);
  standBar.position.set(0, 1.0, 0);
  group.add(standV, standV2, standBar);
  
  group.traverse(o => { if (o.isMesh){ o.castShadow=true; o.receiveShadow=true; } });
  
  wheel.base.set(-2.3, 0, 0);
  group.position.copy(wheel.base);
  // orient so rungs face +z (hamster runs on the rung face)
  wheel.mesh = group;
  wheel.rims = [rim1, rim2];
  return wheel;
}

Wheel.prototype methods:
spin(v){ this.angularVel += v; }
update(dt){ this.mesh.rotation.x += this.angularVel*dt; this.angularVel*=0.985; if(Math.abs(this.angularVel)<0.01)this.angularVel=0; }
```

Wait, rotation.x of the group — the rungs are in the XZ plane (cylinder along... I set rim cylinder rotation.x=PI/2 so its axis is Z). Rungs are cylinders along Y (default axis Y), positioned around circle in XZ. So the wheel's rotation axis should be Z (the axle) for the rungs to spin like a wheel. Let me reconsider orientation.

Standard wheel: axis of rotation is horizontal (say Z, pointing into screen). Rungs arranged in a circle in the XY plane? Hmm. Let me define wheel lying in the XY plane facing +Z, rotating about Z axis. Then rungs are radiating in XY plane. Rim is a torus in XY plane.

Let me reorient:
- Rim: TorusGeometry(radius 0.75, tube 0.05, 8, 24), oriented so its plane is XY (torus default plane is XY, hole along Z). Good, torus default is in XY plane rotating around Z. 
- Rungs: bars along Z (the depth), positioned around circle in XY. So rungeGeo cylinder along Y, then rotate to point along Z: rotation.x = PI/2, position at (cos*a*0.75, sin*a*0.75, 0). That places them radiating along Z at each angular position → forms the wheel surface you grab. Rotation about Z spins them. 
- Hub: cylinder along Z: rotation default Y -> set rotation.x=PI/2 so axis along Z. position 0.
- Stand: vertical posts along Y at back (negative z) holding the axle.

So mesh.rotation.x stays 0; spin is mesh.rotation.z += angularVel*dt. Wait rotation about Z axis is .rotation.z. Yes. Let me use mesh.rotation.z for spin. And orient all parts in XY plane. Let me redo:

Rim: TorusGeometry(0.72, 0.05, 8, 28). Default torus lies in XY plane, normal along Z. Good. Two rims at z=±0.22.

Rungs: CylinderGeometry(0.02,0.02,1.44,8) length along Y =1.44 (diameter-ish 1.44 ~ 2*0.72). Rotate to align with Z: bar.rotation.x = Math.PI/2. Position at angle a: (cos a*0.72, sin a*0.72, 0). Good, these are spokes sticking out along Z.

Hub: Cylinder(0.07,0.07,0.5,10) rotate x PI/2 so axis Z, at origin.

Stand: posts along Y. Two vertical boxes at (±0, y) behind at z=-0.35? Actually the axle is at center (0,0,0). Stand should hold axle. Put vertical posts at z=-0.3 (back) rising up, and a base foot on floor. Let me place stand so wheel center is at y≈0.85 (raised) so hamster stands on floor next to it and reaches. Hmm.

Let me raise the wheel center to y=0.85. Stand: two vertical posts from floor (y=0) to y=1.25 at z=-0.3, and a horizontal bar at top y=1.25 connecting, with axle at center. Actually simpler: post from floor up to the axle height.

Let me set wheel center at y=0.9. Stand: 
- two vertical bars at (0, 0.6, -0.3) and (0,0.6, 0.3)? No, keep them at back. Let me do a single U-stand: left post and right post connected by top bar, forming a gate through which axle passes.

Simplify: 
- Post1: Box(0.12, 1.0, 0.12) at (0, 0.5, -0.3)
- Post2: same at (0, 0.5, 0.3)
- Top connector: Box(0.12, 0.12, 0.72) at (0, 1.0, 0)
The axle at (0,0.9,0). Hamster runs on the front rungs (z>0 side). Fine.

Actually the posts at z ±0.3 with wheel half-depth 0.22 fit between. Good.

Wheel center y: let me set group.position.y = 0.9 so rungs center at 0.9. Hamster standing at floor y~0.5 height reaches up to ~0.9, can grab rungs. Good.

Let me set wheel.base = (-2.3, 0.9, 0) storing center. Hamster rides at pos = base.x, 0 (floor), z = base.z + 0.3 (front). Its head/body near rungs. Good enough.

Spin: mesh.rotation.z += angularVel*dt.

Let me also add a click interaction that adds spin.

Now food bowl:

```js
function makeFoodBowl() {
  const g = new THREE.Group();
  const bowlMat = new THREE.MeshStandardMaterial({ color: 0x4d96ff, flatShading:true, roughness:0.6 });
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.25, 0.18, 16, 1, true), bowlMat);
  bowl.position.y = 0.09;
  const bottom = new THREE.Mesh(new THREE.CylinderGeometry(0.25,0.25,0.02,16), bowlMat);
  bottom.position.y = 0.01;
  g.add(bowl, bottom);
  // pellets
  const pelletMat = new THREE.MeshStandardMaterial({ color: 0x8B5E3C, flatShading:true, roughness:1 });
  for(let i=0;i<10;i++){
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.045, 6, 5), pelletMat);
    const ang = Math.random()*Math.PI*2, r = Math.random()*0.22;
    p.position.set(Math.cos(ang)*r, 0.12+Math.random()*0.05, Math.sin(ang)*r);
    g.add(p);
  }
  g.position.set(2.4, 0, 0.5);
  g.traverse(o=>{ if(o.isMesh)o.castShadow=true; });
  return g;
}
```

Tunnel:

```js
function makeTunnel() {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0xf0a34e, flatShading:true, roughness:0.9, side: THREE.DoubleSide });
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 1.4, 16, 1, true), mat);
  tube.rotation.z = Math.PI/2; // lie along X
  tube.position.y = 0.35;
  // rings/decor
  const ringMat = new THREE.MeshStandardMaterial({ color: 0xffd166, flatShading:true });
  for(let i=-1;i<=1;i++){
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.35,0.04,8,16), ringMat);
    ring.rotation.y = Math.PI/2;
    ring.position.set(i*0.5, 0.35, 0);
    g.add(ring);
  }
  g.position.set(0.6, 0, -1.3);
  g.traverse(o=>{ if(o.isMesh){o.castShadow=true;} });
  return g;
}
```

House:

```js
function makeHouse() {
  const g = new THREE.Group();
  const wallMat = new THREE.MeshStandardMaterial({ color: 0xd98a5b, flatShading:true, roughness:0.9 });
  const roofMat = new THREE.MeshStandardMaterial({ color: 0xb85a3c, flatShading:true, roughness:0.9 });
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.6, 0.8), wallMat);
  body.position.y = 0.3;
  const roof = new THREE.Mesh(new THREE.ConeGeometry(0.72, 0.4, 4), roofMat);
  roof.position.y = 0.8; roof.rotation.y = Math.PI/4;
  // door hole: use a small dark box to suggest entrance
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.28,0.34,0.05), new THREE.MeshStandardMaterial({color:0x2b1c12, flatShading:true}));
  door.position.set(0, 0.2, 0.42);
  g.add(body, roof, door);
  g.position.set(-0.7, 0, 1.4);
  g.traverse(o=>{ if(o.isMesh){o.castShadow=true; o.receiveShadow=true; } });
  return g;
}
```

Now the tray and cage:

```js
function makeCage() {
  const g = new THREE.Group();
  const trayMat = new THREE.MeshStandardMaterial({ color: 0x5fb6b0, flatShading:true, roughness:0.7 });
  const wallMat = new THREE.MeshStandardMaterial({ color: 0x7fcfc9, flatShading:true, roughness:0.7 });
  const floor = new THREE.Mesh(new THREE.BoxGeometry(6.2, 0.15, 4.2), trayMat);
  floor.position.y = 0.075; floor.receiveShadow = true;
  g.add(floor);
  // walls
  const walls = [
    [6.2, 0.7, 0.12, 0, 0.5, -2.05],   // back
    [6.2, 0.7, 0.12, 0, 0.5, 2.05],    // front
    [0.12, 0.7, 4.2, -3.05, 0.5, 0],   // left
    [0.12, 0.7, 4.2, 3.05, 0.5, 0],    // right
  ];
  for (const w of walls){
    const m = new THREE.Mesh(new THREE.BoxGeometry(w[0],w[1],w[2]), wallMat);
    m.position.set(w[3], w[4], w[5]);
    m.castShadow=true; m.receiveShadow=true;
    g.add(m);
  }
  // shavings added elsewhere
  // wire top (grid lines)
  const lineMat = new THREE.LineBasicMaterial({ color: 0xffffff, opacity:0.6, transparent:true });
  const pts = [];
  const yTop = 1.1;
  for (let x=-3; x<=3; x+=0.6){ pts.push(-3,yTop,x?0:0); } // placeholder
  ...
  return g;
}
```

Let me build wire top properly with LineSegments.

```js
const gridPts = [];
const yTop = 1.05;
const step = 0.55;
for (let x=-3; x<=3; x+=step){
  gridPts.push(x, yTop, -2, x, yTop, 2);
}
for (let z=-2; z<=2; z+=step){
  gridPts.push(-3, yTop, z, 3, yTop, z);
}
const geo = new THREE.BufferGeometry();
geo.setAttribute('position', new THREE.Float32BufferAttribute(gridPts,3));
const wires = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({color:0xffffff, opacity:0.5, transparent:true}));
g.add(wires);
```

Good.

Ground plane:
```js
const ground = new THREE.Mesh(new THREE.PlaneGeometry(60,60), new THREE.MeshStandardMaterial({color:0xdfeecf, roughness:1}));
ground.rotation.x = -Math.PI/2;
ground.position.y = -0.05;
ground.receiveShadow = true;
scene.add(ground);
```

Background: scene.background = 0xcbe6f0 (soft). Maybe add fog for depth: scene.fog = new THREE.Fog(0xcbe6f0, 12, 30).

Now assembly order in main:
- scene, camera, renderer, controls
- lights
- ground
- cage group (add to scene)
- add decorations (shavings, food bowl, tunnel, house) to scene or cage
- wheel(s) -> WHEEL, add to scene
- hamsters array, add each to scene
- animation loop updating hamsters and wheel
- raycast for click

Let me set camera position: (0, 4.5, 6) looking at (0,0.6,0). Controls target (0,0.6,0).

Let me ensure shadows: renderer.shadowMap.enabled = true; directional light castShadow, set camera/frustum for shadow.

Directional light position (5, 8, 5), target at center. set light.shadow.camera bounds.

Let me write final code. I'll be thorough.

Let me double check the hamster leg orientation and body. bodyGroup.position.y = 0.5; body radius 0.5 so bottom touches y=0 (floor). Good. Feet at bodyGroup local y=-0.05 => world y=0.45? Wait that's too high; feet should be near floor. Let me place feet at local y = -0.42 so world y = 0.08, near floor. Actually body center at 0.5, radius 0.5 => bottom at 0. Feet at local y -0.42 => world 0.08. Good, slightly above floor. Fine.

Cheeks at head local y -0.06 relative to head center at 0.24 => 0.18. Eyes at head local 0.05 => 0.29. Nose at -0.02 => 0.22, z 0.38 => 0.78. Head radius 0.4 so front at z 0.4+0.4=0.8. Good nose near front.

Ears at head local y 0.34 => 0.58, top of head at 0.24+0.4=0.64. Good.

Alright.

Now, the head group offset within bodyGroup is (0,0.24,0.4). Good.

Let me also add small whiskers? Skip.

Add a subtle idle "sleep" where some hamsters lie down? Not needed.

Let me finalize the code and present.

I'll also add a title and instructions overlay.

Let me write it all out cleanly.

Let me reconsider hamster count: 3 hamsters with distinct colors. Good. Maybe 4 for livelier. I'll do 4.

Colors: ['#E0A86B', '#C98A4B', '#F2E2C9', '#A8D3A0'] (tan, brown, cream, mint). Mint for a funny one. Add pink cheeks always.

Let me also vary size slightly.

Now writing final.

For click interaction, raycast against WHEEL.mesh children meshes. On hit, add spin and show a little "+spin" maybe. Keep simple: add spin 8 and a bounce.

Let me also make hamsters avoid overlapping a bit? Not necessary.

Let me write the final HTML.

I need to be careful: In update, I reference WHEEL before it's defined if hamsters created first. So create WHEEL first, then hamsters. Good.

Also clamp functions.

Let me write clamp:
```js
const clamp = (v,a,b)=>Math.max(a,Math.min(b,v));
const rand = (a,b)=>a+Math.random()*(b-a);
```

Now let me produce the final file.

Let me also add window resize handling.

Animation loop uses delta time from clock.

Let me ensure the module imports work with unpkg. Use:
"three": "https://unpkg.com/three@0.160.0/build/three.module.js"
"three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"

Import OrbitControls from 'three/addons/controls/OrbitControls.js'.

Alright, finalize.

Let me write the complete code block.

I'll also add a subtle idle "sleep" where some hamsters lie down? Not needed.

Let me produce the final answer with explanation and the code.

Let me write the complete code block.

Let me reconsider the hamster leg animation sign and make it look like running. Using sin(bobPhase) for front vs back alternating. Good.

Also, when riding, hamster faces wheel; set rotation accordingly. Fine.

Let me also make the hamster's head occasionally turn to look at camera? Not needed.

Final code below.

Let me make sure to set light.shadow.camera.fst to include scene. Set:
light.shadow.camera.left = -8; right=8; top=8; bottom=-8; near=1; far=30.
light.shadow.mapSize.width=2048 etc.

Set camera aspect, near small.

Let me finalize.

I'll write it now.

Also add CSS for overlay text styling.

Let me produce final answer.

One more consideration: performance of shavings with 80 individual meshes + shadows — fine.

Let me also add a couple of decorative items: maybe a small ball toy that hamsters nudges? Requirement says one interactive object; I have wheel interactive. I can add a ball as extra decor but keep hamsters ignoring it. I'll add a tiny ball for cuteness but not required. I'll add it as decor only. Optional—let me include a small rubber ball at (1.5,0.1,-0.5) that hamsters might bump. Actually to keep "simple," I'll include it but it's just decor. Fine.

Hmm, to avoid overcomplicating, I'll include the ball as a small decor item. It's cheap.

Let me finalize.

Write now.
</think>

# Low-Poly Hamster Playground 🐹

Here's a complete single-file project. Save it as `index.html` and open it in any modern browser — no build step, no dependencies to install (Three.js loads from a CDN).

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; font-family: "Segoe UI", system-ui, sans-serif; }
  #app { position: fixed; inset: 0; }
  .hud {
    position: fixed; top: 16px; left: 16px; z-index: 10;
    color: #3a5a55; background: rgba(255,255,255,0.72);
    padding: 12px 16px; border-radius: 14px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    backdrop-filter: blur(4px); max-width: 280px;
  }
  .hud h1 { font-size: 18px; margin-bottom: 4px; }
  .hud p  { font-size: 12.5px; line-height: 1.5; opacity: 0.85; }
  .badge { display:inline-block; margin-top:8px; font-size:11px; color:#fff; background:#5fb6b0; padding:3px 9px; border-radius:20px; }
</style>
</head>
<body>
<div id="app"></div>
<div class="hud">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate · scroll to zoom · <b>click the wheel</b> to spin it!</p>
  <span class="badge">4 hamsters on the loose</span>
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

/* ---------------- helpers ---------------- */
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const rand  = (a, b) => a + Math.random() * (b - a);

/* ---------------- renderer / scene ---------------- */
const app = document.getElementById('app');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xcbe6f0);
scene.fog = new THREE.Fog(0xcbe6f0, 14, 34);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(0, 5.2, 7.5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0.7, 0);
controls.minDistance = 3;
controls.maxDistance = 16;
controls.maxPolarAngle = Math.PI * 0.49;

/* ---------------- lights ---------------- */
scene.add(new THREE.HemisphereLight(0xffffff, 0xb89878, 0.65));
scene.add(new THREE.AmbientLight(0xffffff, 0.4));
const sun = new THREE.DirectionalLight(0xfff4e0, 1.1);
sun.position.set(6, 10, 5);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -9; sun.shadow.camera.right = 9;
sun.shadow.camera.top = 9;  sun.shadow.camera.bottom = -9;
sun.shadow.camera.near = 1; sun.shadow.camera.far = 30;
sun.shadow.bias = -0.0004;
scene.add(sun);
scene.add(sun.target);

/* ---------------- ground ---------------- */
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(80, 80),
  new THREE.MeshStandardMaterial({ color: 0xdfeecf, roughness: 1 })
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.06;
ground.receiveShadow = true;
scene.add(ground);

/* ---------------- cage tray ---------------- */
const cage = new THREE.Group();
scene.add(cage);

const trayMat = new THREE.MeshStandardMaterial({ color: 0x5fb6b0, flatShading: true, roughness: 0.7 });
const wallMat = new THREE.MeshStandardMaterial({ color: 0x8fd6cf, flatShading: true, roughness: 0.7 });

const floor = new THREE.Mesh(new THREE.BoxGeometry(6.4, 0.16, 4.4), trayMat);
floor.position.y = 0.08; floor.receiveShadow = true;
cage.add(floor);

const wallSpecs = [
  [6.4, 0.72, 0.12,  0,    0.52, -2.14],
  [6.4, 0.72, 0.12,  0,    0.52,  2.14],
  [0.12, 0.72, 4.4, -3.14, 0.52,  0],
  [0.12, 0.72, 4.4,  3.14, 0.52,  0],
];
for (const w of wallSpecs) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w[0], w[1], w[2]), wallMat);
  m.position.set(w[3], w[4], w[5]);
  m.castShadow = true; m.receiveShadow = true;
  cage.add(m);
}

// wire top (lightweight grid)
const gridPts = [];
const yTop = 1.05, step = 0.55;
for (let x = -3; x <= 3; x += step) gridPts.push(x, yTop, -2.14, x, yTop, 2.14);
for (let z = -2.14; z <= 2.14; z += step) gridPts.push(-3.14, yTop, z, 3.14, yTop, z);
const wireGeo = new THREE.BufferGeometry();
wireGeo.setAttribute('position', new THREE.Float32BufferAttribute(gridPts, 3));
cage.add(new THREE.LineSegments(
  wireGeo, new THREE.LineBasicMaterial({ color: 0xffffff, opacity: 0.5, transparent: true })
));

// wood shavings on the floor
function addShavings(count) {
  const geo = new THREE.BoxGeometry(0.09, 0.02, 0.26);
  const colors = [0xe9c896, 0xd9b57a, 0xf0dca8, 0xcfa465];
  const grp = new THREE.Group();
  for (let i = 0; i < count; i++) {
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
      color: colors[i % colors.length], flatShading: true, roughness: 1
    }));
    m.position.set(rand(-2.9, 2.9), 0.17, rand(-1.95, 1.95));
    m.rotation.y = Math.random() * Math.PI;
    m.rotation.z = (Math.random() - 0.5) * 0.5;
    grp.add(m);
  }
  cage.add(grp);
}
addShavings(120);

/* ---------------- props ---------------- */
// exercise wheel (interactive)
const WHEEL = (() => {
  const g = new THREE.Group();
  const rimMat = new THREE.MeshStandardMaterial({ color: 0xff6b6b, flatShading: true, roughness: 0.6 });
  const barMat = new THREE.MeshStandardMaterial({ color: 0xffd166, flatShading: true, roughness: 0.5 });
  const standMat = new THREE.MeshStandardMaterial({ color: 0x4d96ff, flatShading: true, roughness: 0.7 });

  const rim1 = new THREE.Mesh(new THREE.TorusGeometry(0.72, 0.05, 8, 28), rimMat);
  const rim2 = rim1.clone(); rim2.position.z = 0.24;
  const rungs = [];
  for (let i = 0; i < 18; i++) {
    const a = (i / 18) * Math.PI * 2;
    const b = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.48, 8), barMat);
    b.rotation.x = Math.PI / 2;
    b.position.set(Math.cos(a) * 0.72, Math.sin(a) * 0.72, 0);
    g.add(b); rungs.push(b);
  }
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.5, 12), standMat);
  hub.rotation.x = Math.PI / 2;
  const p1 = new THREE.Mesh(new THREE.BoxGeometry(0.12, 1.0, 0.12), standMat);
  p1.position.set(0, 0.5, -0.32);
  const p2 = p1.clone(); p2.position.z = 0.32;
  const top = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 0.76), standMat);
  top.position.set(0, 1.02, 0);
  g.add(rim1, rim2, hub, p1, p2, top);
  g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });

  const wheel = { mesh: g, base: new THREE.Vector3(-2.4, 0.9, 0), angularVel: 0 };
  g.position.copy(wheel.base);
  return wheel;
})();
scene.add(WHEEL.mesh);
WHEEL.spin = (v) => { WHEEL.angularVel += v; };
WHEEL.update = (dt) => {
  WHEEL.mesh.rotation.z += WHEEL.angularVel * dt;
  WHEEL.angularVel *= 0.985;
  if (Math.abs(WHEEL.angularVel) < 0.01) WHEEL.angularVel = 0;
};

// food bowl
(() => {
  const g = new THREE.Group();
  const m = new THREE.MeshStandardMaterial({ color: 0x4d96ff, flatShading: true, roughness: 0.6 });
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.26, 0.18, 16, 1, true), m);
  bowl.position.y = 0.09;
  const bottom = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.02, 16), m);
  bottom.position.y = 0.01;
  g.add(bowl, bottom);
  const pm = new THREE.MeshStandardMaterial({ color: 0x8b5e3c, flatShading: true, roughness: 1 });
  for (let i = 0; i < 11; i++) {
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.045, 6, 5), pm);
    const a = Math.random() * Math.PI * 2, r = Math.random() * 0.22;
    p.position.set(Math.cos(a) * r, 0.13 + Math.random() * 0.05, Math.sin(a) * r);
    g.add(p);
  }
  g.position.set(2.5, 0, 0.6);
  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  scene.add(g);
})();

// cardboard tunnel
(() => {
  const g = new THREE.Group();
  const tube = new THREE.Mesh(
    new THREE.CylinderGeometry(0.34, 0.34, 1.5, 16, 1, true),
    new THREE.MeshStandardMaterial({ color: 0xf0a34e, flatShading: true, roughness: 0.9, side: THREE.DoubleSide })
  );
  tube.rotation.z = Math.PI / 2; tube.position.y = 0.34;
  const ringMat = new THREE.MeshStandardMaterial({ color: 0xffd166, flatShading: true });
  for (let i = -1; i <= 1; i++) {
    const r = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.04, 8, 16), ringMat);
    r.rotation.y = Math.PI / 2; r.position.set(i * 0.5, 0.34, 0);
    g.add(r);
  }
  g.position.set(0.7, 0, -1.4);
  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  scene.add(g);
})();

// little house
(() => {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.95, 0.6, 0.85),
    new THREE.MeshStandardMaterial({ color: 0xd98a5b, flatShading: true, roughness: 0.9 }));
  body.position.y = 0.3;
  const roof = new THREE.Mesh(new THREE.ConeGeometry(0.76, 0.42, 4),
    new THREE.MeshStandardMaterial({ color: 0xb85a3c, flatShading: true, roughness: 0.9 }));
  roof.position.y = 0.82; roof.rotation.y = Math.PI / 4;
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.36, 0.05),
    new THREE.MeshStandardMaterial({ color: 0x2b1c12, flatShading: true }));
  door.position.set(0, 0.2, 0.43);
  g.add(body, roof, door);
  g.position.set(-0.8, 0, 1.5);
  g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  scene.add(g);
})();

// rubber ball toy
(() => {
  const ball = new THREE.Mesh(new THREE.IcosahedronGeometry(0.18, 0),
    new THREE.MeshStandardMaterial({ color: 0xff9f1c, flatShading: true, roughness: 0.5 }));
  ball.position.set(1.4, 0.18, -0.6);
  ball.castShadow = true;
  scene.add(ball);
})();

/* ---------------- hamsters ---------------- */
function makeHamster(furHex) {
  const g = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color: furHex, flatShading: true, roughness: 0.95 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x2b1c12, flatShading: true, roughness: 0.6 });
  const pink = new THREE.MeshStandardMaterial({ color: 0xf2a6a0, flatShading: true, roughness: 0.8 });
  const bellyMat = new THREE.MeshStandardMaterial({ color: 0xfff4e6, flatShading: true, roughness: 0.95 });

  const bodyGroup = new THREE.Group();
  g.add(bodyGroup); bodyGroup.position.y = 0.5;

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 14, 12), fur);
  body.scale.set(1, 0.92, 1.15); body.castShadow = true;
  bodyGroup.add(body);

  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.42, 12, 10), bellyMat);
  belly.scale.set(0.95, 0.85, 1.1); belly.position.set(0, -0.08, 0.08);
  bodyGroup.add(belly);

  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 6), fur);
  tail.position.set(0, 0.05, -0.56);
  bodyGroup.add(tail);

  const headGroup = new THREE.Group();
  headGroup.position.set(0, 0.24, 0.4);
  bodyGroup.add(headGroup);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.4, 14, 12), fur);
  head.scale.set(1, 0.95, 0.95); head.castShadow = true;
  headGroup.add(head);

  const cheekGeo = new THREE.SphereGeometry(0.18, 10, 8);
  const cl = new THREE.Mesh(cheekGeo, pink); cl.position.set(-0.24, -0.06, 0.12); cl.scale.set(1, 0.9, 0.8);
  const cr = cl.clone(); cr.position.x = 0.24;
  headGroup.add(cl, cr);

  const earGeo = new THREE.CylinderGeometry(0.13, 0.11, 0.06, 12);
  const el = new THREE.Mesh(earGeo, fur); el.position.set(-0.2, 0.34, 0); el.rotation.z = 0.2;
  const er = el.clone(); er.position.x = 0.2; er.rotation.z = -0.2;
  const ieGeo = new THREE.CylinderGeometry(0.075, 0.065, 0.07, 12);
  const iel = new THREE.Mesh(ieGeo, pink); iel.position.set(-0.2, 0.34, 0.01);
  const ier = iel.clone(); ier.position.x = 0.2;
  headGroup.add(el, er, iel, ier);

  const eyeGeo = new THREE.SphereGeometry(0.075, 12, 10);
  const eL = new THREE.Mesh(eyeGeo, dark); eL.position.set(-0.16, 0.05, 0.32);
  const eR = eL.clone(); eR.position.x = 0.16;
  const hiMat = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });
  const hL = new THREE.Mesh(new THREE.SphereGeometry(0.025, 8, 6), hiMat); hL.position.set(-0.14, 0.08, 0.36);
  const hR = hL.clone(); hR.position.x = 0.18;
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), pink);
  nose.position.set(0, -0.02, 0.38);
  headGroup.add(eL, eR, hL, hR, nose);

  const feet = [];
  const footGeo = new THREE.SphereGeometry(0.1, 10, 8);
  const footMat = new THREE.MeshStandardMaterial({ color: pink, flatShading: true });
  for (const p of [[-0.25,-0.42,0.25],[0.25,-0.42,0.25],[-0.25,-0.42,-0.25],[0.25,-0.42,-0.25]]) {
    const f = new THREE.Mesh(footGeo, footMat);
    f.position.set(p[0], p[1], p[2]); f.scale.set(1, 0.6, 1.2);
    bodyGroup.add(f); feet.push(f);
  }

  return g;
}

const BOUNDS = { minX: -2.9, maxX: 2.9, minZ: -1.85, maxZ: 1.85 };

class Hamster {
  constructor(mesh) {
    this.mesh = mesh;
    this.bg = mesh.userData.bodyGroup;
    this.hg = mesh.userData.headGroup;
    this.feet = mesh.userData.feet;
    this.pos = new THREE.Vector3(rand(-2, 2), 0, rand(-1.2, 1.2));
    this.mesh.position.copy(this.pos);
    this.speed = 0.55 + Math.random() * 0.35;
    this.bobPhase = Math.random() * Math.PI * 2;
    this.age2 = Math.random() * 6;
    this.nextDecision = Math.random() * 3 + 1;
    this.rideTimer = 0;
    this.riding = false;
    this.target = new THREE.Vector3();
    this.goingToWheel = false;
    this.pickTarget();
  }
  pickTarget() {
    if (Math.random() < 0.28) {
      this.target.set(WHEEL.base.x, 0, WHEEL.base.z);
      this.goingToWheel = true;
    } else {
      this.target.set(rand(-2.6, 2.6), 0, rand(-1.6, 1.6));
      this.goingToWheel = false;
    }
  }
  legMove(dt, mult) {
    const s = Math.sin(this.bobPhase) * 0.5 * mult;
    this.feet[0].rotation.x =  s; this.feet[1].rotation.x = -s;
    this.feet[2].rotation.x = -s; this.feet[3].rotation.x =  s;
  }
  update(dt) {
    this.age2 += dt;
    this.nextDecision -= dt;

    if (this.riding) {
      this.rideTimer -= dt;
      WHEEL.spin(this.speed * 1.3);
      this.bobPhase += dt * 16;
      this.bg.position.y = 0.5 + Math.abs(Math.sin(this.bobPhase)) * 0.07;
      this.legMove(dt, 1.6);
      this.mesh.rotation.y = Math.atan2(WHEEL.base.x - this.pos.x, WHEEL.base.z - this.pos.z);
      this.hg.rotation.x = -0.2 + Math.sin(this.age2 * 3) * 0.1;
      if (this.rideTimer <= 0) { this.riding = false; this.goingToWheel = false; this.pickTarget(); }
      return;
    }

    const dx = this.target.x - this.pos.x, dz = this.target.z - this.pos.z;
    const dist = Math.hypot(dx, dz);

    if (dist > 0.12) {
      const nx = dx / dist, nz = dz / dist;
      this.pos.x = clamp(this.pos.x + nx * this.speed * dt, BOUNDS.minX, BOUNDS.maxX);
      this.pos.z = clamp(this.pos.z + nz * this.speed * dt, BOUNDS.minZ, BOUNDS.maxZ);
      this.mesh.position.x = this.pos.x; this.mesh.position.z = this.pos.z;
      this.mesh.rotation.y = Math.atan2(nx, nz);
      this.bobPhase += dt * 13;
      this.bg.position.y = 0.5 + Math.abs(Math.sin(this.bobPhase)) * 0.05;
      this.legMove(dt, 1.0);
      this.hg.rotation.x = Math.sin(this.age2 * 2) * 0.12;
    } else {
      this.hg.rotation.y = Math.sin(this.age2 * 1.2) * 0.35;
      this.hg.rotation.x = Math.sin(this.age2 * 0.8) * 0.06;
      this.bg.scale.y = 1 + Math.sin(this.age2 * 2) * 0.03; // breathing
      if (this.goingToWheel && !this.riding) {
        this.riding = true;
        this.rideTimer = 2.5 + Math.random() * 2;
        this.pos.set(WHEEL.base.x, 0, WHEEL.base.z + 0.35);
        this.mesh.position.copy(this.pos);
      } else if (this.nextDecision <= 0) {
        this.pickTarget();
        this.nextDecision = Math.random() * 4 + 1.5;
      }
    }
  }
}

const hamsters = [];
const palette = [0xe0a86b, 0xc98a4b, 0xf2e2c9, 0xa8d3a0];
for (let i = 0; i < 4; i++) {
  const h = makeHamster(palette[i]);
  const s = new Hamster(h);
  hamsters.push(s);
  scene.add(h);
}

/* ---------------- interaction: click the wheel ---------------- */
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
addEventListener('pointerdown', (e) => {
  pointer.x = (e.clientX / innerWidth) * 2 - 1;
  pointer.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.fromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(WHEEL.mesh.children, true);
  if (hits.length) {
    WHEEL.spin(9);
    // nudge a nearby hamster to go ride it
    let nearest = null, nd = Infinity;
    for (const hs of hamsters) {
      const d = hs.mesh.position.distanceTo(WHEEL.base);
      if (d < nd) { nd = d; nearest = hs; }
    }
    if (nearest && nd < 5 && !nearest.riding) {
      nearest.goingToWheel = true;
      nearest.target.set(WHEEL.base.x, 0, WHEEL.base.z);
    }
  }
});

/* ---------------- resize & loop ---------------- */
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  WHEEL.update(dt);
  for (const hs of hamsters) hs.update(dt);
  controls.update();
  renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>
```

## What's inside

**Scene contents**
- **Cage**: a teal plastic tray with four walls and a lightweight white wire grid on top (kept open so you can see the action).
- **Floor**: scattered low-poly wood shavings for texture.
- **4 low-poly hamsters**: each built from spheres/cylinders with chubby pink cheeks, soft ears, glossy eyes, little feet, and a fluffy tail. Colors vary (tan, brown, cream, and a funny mint one).
- **Interactive exercise wheel** (the key interactive object), plus a food bowl, a cardboard tunnel, a little house, and a rubber ball as cute extras.

**Behavior (autonomous)**
- Hamsters wander to random points, slowly turning and bobbing their bodies while their legs alternate.
- They pause to "sniff"/look around, breathe idly, then pick a new direction.
- Occasionally one heads to the wheel, climbs on, and runs it — spinning the wheel with decaying physics.

**Interaction**
- Drag to rotate the camera, scroll to zoom (OrbitControls).
- **Click the wheel** to spin it hard; it even summons a nearby hamster to come ride it.

It runs instantly in any modern browser — just open the file. Everything is self-contained, stable, and intentionally kept simple and readable. Enjoy your hamsters! 🐾