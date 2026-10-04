Let me create a single-file HTML project for a Low-Poly Hamster Playground using Three.js. I'll make it self-contained, cute, and functional.

Let me think about the design:
1. A cage (transparent walls or wireframe-ish)
2. A floor/tray at the bottom
3. Several low-poly hamsters (I'll build them from basic geometries - spheres, boxes)
4. One interactive object - I'll do a running wheel that rotates when hamsters interact with it
5. Autonomous behavior - hamsters walk, pause, turn, and can interact with the wheel

Let me structure this:
- Three.js from CDN
- OrbitControls for camera rotation
- Build hamsters with body, head, ears, eyes, tail, legs
- Add a running wheel that spins
- Simple AI: random wandering with state machine (walking, pausing, turning)

Let me write clean, working code. I need to be careful to make it actually work.

Key considerations:
- Use a recent Three.js version with importmap for modules, OR use the classic version with global THREE. For simplicity and reliability, I'll use the classic non-module version with OrbitControls included, OR use importmap with ES modules.

Actually, let me use the ESM approach with importmap since that's the modern standard. But to be safe and ensure it "runs immediately," I could use the classic build. Let me use the module approach with importmap pointing to a CDN like unpkg or jsdelivr.

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

Then:
```html
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
</script>
```

This is the modern reliable way.

Now let me design the scene:

**Cage:**
- A tray (box) at the bottom - the base
- Transparent/acrylic walls - I'll use a slightly transparent material for the sides
- Actually, let me make a nice cage with a wooden-looking base tray and clear walls

**Floor:**
- The tray bottom with some bedding color

**Hamsters:**
Build a function createHamster(color) that returns a group with:
- Body (sphere, squished)
- Head (sphere)
- Two ears (small spheres or cones)
- Eyes (black spheres with maybe white)
- Cheeks (optional)
- Tail (small)
- Four legs (small cylinders/boxes)

Each hamster will have:
- reference to its legs for animation
- a state machine

**Running wheel:**
- A wheel made of a torus + rungs
- Rotates when hamsters are near/on it
- Mounted on the cage

**Behavior:**
- Each hamster has a state: 'walk', 'pause', 'turn'
- Walk toward a target or wander randomly
- Pause occasionally
- Turn around

Let me make it fun but stable.

Let me think about the interaction with the wheel: When a hamster reaches the wheel area, it can "run" on the wheel which makes the wheel spin. Or simpler: hamsters wander around the cage floor, and the wheel spins continuously with a slight slowdown, and when a hamster is near it spins faster.

Actually, let me make hamsters actually go onto the wheel and run. That's the fun part. But that adds complexity with physics. Let me keep it simpler:

- Hamsters wander on the floor
- There's a wheel that spins
- Occasionally a hamster decides to go to the wheel and "run" - while running on the wheel, the wheel spins fast and the hamster bobs

Hmm, let me think about a clean approach. I'll give each hamster a target position. They walk toward it. When they get close, they pause. Sometimes the target is the wheel position, and then they spin the wheel.

Let me implement:

```js
class Hamster {
  constructor(scene, color) {
    this.mesh = createHamsterMesh(color);
    scene.add(this.mesh);
    this.state = 'idle';
    this.timer = Math.random() * 3;
    this.target = new THREE.Vector3(randomX, 0, randomZ);
    this.speed = 1.5;
    this.legPhase = 0;
    this.wheelSpin = 0;
  }
}
```

For movement, I'll move along the floor (y is fixed at tray level). Rotation based on movement direction.

Leg animation: alternate front/back legs.

Let me write the full thing carefully.

Let me consider the cage dimensions:
- Tray: width 20, depth 14, height 4 (the base)
- Walls go up a bit more
- Floor is the top of the tray

Actually let me define:
- Play area: x from -8 to 8, z from -6 to 6, y floor at 0
- Tray height 2, walls up to y=5

Let me make the hamsters small (scale ~0.5) so several fit.

Let me plan the wheel:
- Position: one side of cage, e.g., x = 6, z = 0
- Radius 2.5
- Vertical axis (like a real hamster wheel, spins around horizontal axis)
- The wheel plane... a real hamster wheel spins around a horizontal axis. So the wheel is a circle in the XZ plane? No. A hamster wheel: the wheel spins around a horizontal axis (the axle). The wheel itself is in a vertical plane. If axle is along Z, the wheel spins in the XZ plane... 

Let me think: Real hamster wheel sits against a wall. The wheel is vertical (like a bicycle wheel standing up). The axle is horizontal. The hamster runs inside, pushing the bottom.

If the wheel stands in the XZ plane (vertical), axle along Z axis (horizontal, into the wall), then the wheel spins in the XZ plane. Points on the wheel rotate around Z. The hamster runs on the inside bottom.

Let me place wheel at x=6 (near right wall), standing with axle along Z. Radius 2.5, center at y=2.5 (so bottom touches floor at y=0).

For a hamster to "run" on it, I'll just animate the wheel spinning and the hamster positioned at the bottom, bobbing.

Actually, implementing a hamster actually getting on and running requires the hamster to move with the wheel which is complex. Let me simplify: 

When a hamster's target is the wheel, it walks to a point near the wheel, then enters a "running" state where it stays there, the wheel spins fast, and the hamster bobs up and down with leg animation. After a random time it leaves.

That's clean and fun. Let me do that.

Let me also add:
- Ambient light + directional light (sun) for cute shadows
- Soft background color
- Maybe some scattered food pellets / bedding dots
- A small food bowl as an alternative interactive element? The requirement says "one interactive object" - I'll do the wheel as primary. I could add a food bowl too but let me keep focused. Actually let me add both a wheel and maybe some decorative elements but keep the interaction centered on the wheel.

Let me also add name labels? CSS2D could be nice but adds complexity. Skip.

Let me add a subtle "hop" when walking - raise the hamster slightly.

Let me write the code now.

I'll structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style> ... </style>
</head>
<body>
<div id="info">...</div>
<script type="importmap">...</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// scene setup
// lights
// cage
// wheel
// hamsters
// animation loop
</script>
</body>
</html>
```

Let me write the hamster builder function:

```js
function createHamster(color) {
  const group = new THREE.Group();
  
  const furMaterial = new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9 });
  const whiteMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });
  const blackMaterial = new THREE.MeshStandardMaterial({ color: 0x222022, flatShading: true });
  const pinkMaterial = new THREE.MeshStandardMaterial({ color: 0xffb0b0, flatShading: true });
  
  // Body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 12, 10), furMaterial);
  body.scale.set(1, 0.9, 1.25);
  body.position.y = 0.55;
  group.add(body);
  
  // Belly (lighter) - optional
  ...
  
  // Head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.42, 12, 10), furMaterial);
  head.position.set(0.55, 0.7, 0);
  head.scale.set(1, 0.95, 0.95);
  group.add(head);
  
  // Ears
  const earGeo = new THREE.SphereGeometry(0.16, 8, 8);
  const leftEar = new THREE.Mesh(earGeo, furMaterial);
  leftEar.position.set(0.45, 1.05, 0.22);
  ...
  
  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.09, 8, 8);
  leftEye = new THREE.Mesh(eyeGeo, blackMaterial);
  leftEye.position.set(0.82, 0.75, 0.18);
  rightEye similar with z -0.18
  
  // Nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.06, 8, 8), pinkMaterial);
  nose.position.set(0.95, 0.65, 0);
  
  // Cheeks / tail
  // Tail: small sphere at back
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 8), pinkMaterial);
  tail.position.set(-0.6, 0.5, 0);
  
  // Legs - 4 small cylinders
  const legGeo = new THREE.CylinderGeometry(0.09, 0.09, 0.28, 6);
  // positions relative to body center
  const legs = [];
  // front-left, front-right, back-left, back-right
  // Need to offset because body center is at y=0.55
  ...
}
```

Hmm, positioning legs relative to body center needs care. Let me store leg meshes in an array for animation.

Actually, let me make the whole hamster face +X by default (nose at +x). Then rotation around Y turns it. Movement direction determines rotation.

Let me set body center at origin of group, and position everything relative.

Let me redefine with body center at (0,0,0) of the group, then lift group to floor.

Wait, but I want the hamster to sit on the floor (y=0 = floor level). Let me put the group's y=0 at the floor, and all parts positioned above.

Let me redo:
- Group at floor level.
- Body: sphere radius 0.5, center at y=0.45, scaled.
- etc.

For legs, they go from body bottom to floor. Leg length ~0.3, body bottom at y=0.45-0.5ish.

Let me just carefully compute.

Body: SphereGeometry(0.5), scale (1, 0.85, 1.2). Center y = 0.45. So bottom of body ≈ 0.45 - 0.5*0.85 = 0.45-0.425 = 0.025. Good, close to floor.

Legs: Cylinder radius 0.08, height 0.3. Positioned so top at ~0.05 and bottom at 0. Actually cylinder is centered, so center at y=0.15, from 0.0 to 0.3. But body bottom is at 0.025 so legs slightly behind/below. Fine.

Leg positions (in local space, body centered at x=0,y=0.45):
- Front legs near head (+x), back legs near tail (-x).
- front-left: x=0.35, z=0.28, y=0.15
- front-right: x=0.35, z=-0.28
- back-left: x=-0.35, z=0.28
- back-right: x=-0.35, z=-0.28

These are relative to group origin (floor). Good.

For walking animation, I'll rotate legs back and forth. Store references.

Let me also add little hands/feet - skip, keep simple.

Let me add a tail: small sphere at back.

Now the head:
- Head sphere radius 0.38, center at x=0.5, y=0.6.
- Ears at top-back of head: x=0.35, y=0.95, z=±0.22.
- Eyes at x=0.75, y=0.68, z=±0.16.
- Nose at x=0.9, y=0.6, z=0.
- Cheek blush optional.

Alright.

Now, let me also give each hamster a slightly different color and scale and starting rotation for variety.

Behavior state machine per hamster:
States: 'wander' (walking to target), 'pause' (standing), 'runWheel' (on the wheel).

Each frame:
- timer -= dt
- Based on state, update.

Wander: 
- Move toward target.position. If close, transition to pause.
- Rotate to face movement direction.
- Animate legs.

Pause:
- Stand still, maybe slight bob. Timer counts down. Then pick new target (maybe wheel sometimes) -> wander.

RunWheel:
- Position hamster at wheel bottom, facing appropriate direction.
- Spin wheel fast.
- Bob up and down.
- Timer counts down, then -> wander (leave).

Let me define wheel:
- Wheel group centered at wheel center, spins around Z axis (the axle). Wait, if wheel is vertical in XZ plane and axle along Z, spinning around Z means points rotate in XZ plane. Yes that's correct for a wheel standing vertically facing the X direction... 

Hold on. Let me reconsider. If the wheel stands like a clock face looking down the Z axis, then the numbers are in XZ plane and it spins around Z. That means from the side (looking along X) you'd see the wheel edge-on (a line). Hmm, that's not how we want to see it.

A real hamster wheel: you typically see it from the side (it's a big disc standing vertically). The disc plane is vertical. If it's against the right wall (wall is at constant x, the YZ plane), the wheel disc is in the YZ plane? No wait.

Let me think physically. A wheel against a wall: the wheel is a disc. The disc is vertical. The axle is horizontal and perpendicular to the wall (points away from wall, i.e., along X if wall is YZ plane at x=max). The disc lies in the YZ plane (parallel to wall). It spins around the X axis (the axle).

So the wheel disc is in YZ plane, spins around X axis. Hamster runs inside, at the bottom, pushing. Hamster runs along Z direction (parallel to wall).

OK so:
- Wheel center at (wheelX, wheelY, wheelZ)
- Disc in YZ plane
- Spins around X axis
- Bottom of wheel at y = wheelY - radius = floor (0)
- Hamster runs at bottom, moving in ±Z.

Let me set wheelX = 6.5 (near right wall at x=8), wheelZ = 0, radius 2.2, center y = 2.2.

Support structure: two side plates + axle. I'll make a simple stand: two vertical posts and the axle.

Actually to keep it low-poly and cute, let me make the wheel from:
- A torus for the rim (torus geometry, but torus is a donut... if I want a disc in YZ plane spinning around X, I can use a TorusGeometry with radius 2.2, tube 0.1, rotated so the torus lies in YZ plane). By default torus lies in XY plane (hole along Z). To make it lie in YZ plane, rotate 90° around X. Then spin around X.

Hmm, torus default: the ring is in XY plane, tube circles around Z axis (the central axis is Z). If I rotate the torus mesh 90° about X, the ring goes to YZ plane and central axis becomes X. Then rotating the mesh about X spins it. 

Add rungs (spokes) - small cylinders from center to rim, arranged around. And a floor rail.

Actually, simpler: use a bunch of thin boxes as rungs. Let me generate N rungs (like 12) as small boxes positioned radially.

Let me also add two side discs (thin) to give it volume? Could use CircleGeometry. But low-poly, maybe skip discs and just do rim + rungs + side plates. Let me do rim (torus) + rungs + two side plates (CircleGeometry or BoxGeometry) on the sides.

Support posts: two boxes from floor up to hold the axle.

Let me keep it manageable.

For hamster running on wheel:
- When hamster enters runWheel state, set its position to the bottom of the wheel: (wheelX, ~0.35, wheelZ) and orient it tangent to wheel (along Z), so it faces the running direction.
- The wheel spins (rotate around X).
- The hamster bobs (moves up slightly following the "running").
- Actually keeping the hamster at a fixed position while wheel spins underneath is fine and looks like it's running.

But wait, if the hamster is at the bottom and the wheel spins, the hamster stays at bottom - good, that reads as running.

Direction: hamster faces ±Z. Let me face +Z or -Z. I'll set based on nothing specific, just face one way.

Let me make the hamster's local +X become the "forward" (nose). Currently nose is at +x. If hamster should face +Z, rotate group -90° around Y (so +x axis points to +z). Let me compute: rotating -90° about Y: x-axis (1,0,0) -> (0,0,-1)? Rotation about Y by angle θ: x' = cosθ*x + sinθ*z, z' = -sinθ*x + cosθ*z. For θ=-90: cos=0, sin=-1. x' = 0 + (-1)*0... let me just do: to point nose (+x) toward +z: we want new forward = (0,0,1). Original (1,0,0). Rotation about Y by +90°: cos90=0, sin90=1. x' = cosθ*1 + sinθ*0 = 0. z' = -sinθ*1 + cosθ*0 = -1. So +90° Y gives forward (0,0,-1) = -z. To get +z, use -90° Y: θ=-90, cos=0,sin=-1. x'=0, z' = -(-1)*1 = 1 => (0,0,1) = +z. Yes. So rotate -90° about Y to face +z.

OK this is getting detailed. Let me just pick a direction and set orientation.

Now let me also handle the wander targets within bounds: x in [-6, 6], z in [-5, 5]. Avoid the wheel area maybe. Keep simple.

Let me also add collision-free wandering: just pick random points, walk to them. Simpler than steering. Good enough and stable.

Let me add periodic "turn" - actually reaching a target and picking a new one naturally creates turns. The requirement mentions turning - I'll add a little spin when pausing sometimes.

Let me now also think about the "interactive object" - the wheel. To make it clearly interactive, maybe it responds to mouse? The requirement says "one interactive object such as a wheel, tunnel, food bowl, or toy." The hamsters interacting with it makes it interactive. But "interactive" might mean user interacts. Let me add raycasting so clicking the wheel makes it spin faster / a hamster jumps on it. That satisfies "interactive object."

Let me add: clicking on the wheel (raycast) triggers a hamster to run on it and spins it. That's a nice interactive feature.

Let me implement raycasting on click/tap.

Let me now write everything.

I'll add:
- Renderer with antialias, shadow (optional). Let me enable shadows for cuteness but it can cause perf issues; I'll enable soft shadows with a single directional light. Actually to keep stable and simple, maybe skip shadows or use them lightly. I'll enable shadowMap but keep it simple - one directional light casting shadows. Let me enable it but ensure it works.

Hmm, shadows can be finicky. Let me include them but with a generous shadow camera. If concerned, I can disable. I'll include and test logic mentally—it should be fine.

Let me include ambient + hemisphere for nice soft lighting plus directional for shadows.

Background: a soft pastel color, e.g., #bfe3ff or a gradient. Let me use a solid pastel like #cfe8ff. Add fog maybe.

Let me add bedding: a plane with some scattered small boxes (pellets) or just a textured look. Low-poly: I'll scatter small colored cones/spheres as food pellets and wood shavings. Keep count modest (~40).

Food bowl: let me add a small bowl as decoration (not necessarily interactive) - optional. I'll add it for cuteness.

Let me keep scope reasonable. Let me finalize features:
1. Cage: tray base + transparent walls + top frame lines (maybe just walls).
2. Floor: tray bottom with bedding color + scattered pellets.
3. 5 low-poly hamsters (varied colors).
4. Running wheel (interactive via click) that spins.
5. Autonomous behavior: wander, pause, run on wheel.
6. OrbitControls for camera.
7. Cute lighting and colors.
8. Info overlay with instructions.

Let me write the code.

For walls transparency, use MeshPhysicalMaterial with transmission? That's heavy. Use MeshStandardMaterial with transparent true, opacity 0.35, side doubleSide, color light blue. Good enough for acrylic look.

Cage dimensions:
- Tray: outer box width 20 (x), depth 14 (z), height 2 (y). Base tray from y=0 to y=2? Actually let me make tray the base container. Floor at y=0 is inside top of tray. Hmm.

Let me simplify: 
- The "tray" is a shallow box acting as the base walls + floor. Inside floor at y=0.
- Tray: x[-10,10], z[-7,7], base floor thick. Side walls height 2.5 above floor.
- Clear walls on top: from y=2.5 to y=5, transparent.

Let me build:
- Floor plate: Box(20, 0.4, 14) at y=-0.2 (so top at 0). Color: light gray tray plastic, e.g., #d9e2ec. Or a wood tray color #c69b6f. Let me do a cute pastel tray color #a8d8d8 (mint) or pink. Let me pick tray color #f4c7d0 (pinkish) — cute.

Actually let me make tray a nice color and walls a lighter tint.

- Side walls (base): 4 walls of tray. I can make a single box with a hole? Easier: make 4 thin boxes for the sides (front, back, left, right) at the base height 2.
  Actually the base tray can be: a box shell. Let me just make the floor and 4 low walls.

Let me define base wall height hb = 1.5, clear wall from hb to top ht=4.5.

Base walls: 4 boxes:
- Front (z=+7): width 20, height 1.5, thickness 0.4, at y=0.75
- Back (z=-7): same
- Left (x=-10): width 0.4, height 1.5, at z=0, y=0.75
- Right (x=10): same

Clear walls (transparent) from y=1.5 to y=4.5, same positions but height 3.

Add a top rim? Optional. Skip.

Now the play area for hamsters: x in [-9.5, 9.5], z in [-6.5, 6.5].

Wheel placed at right side near x=8.5, but wheel radius 2.2 center y=2.2 → bottom at 0, top at 4.4 (just under clear wall top 4.5). Wheel in YZ plane at x=8.5. Hamster runs at bottom near z=0. Should be within z bounds. Good. But wheel occupies some area; hamsters wandering might path through it—fine, they'll just walk through (no collision needed, keep it simple/funny).

Let me reduce hamster wander bounds a bit to avoid clipping into walls: x in [-8.5, 8.5].

Now let me write the code fully.

Animation loop uses delta time, clamp delta to avoid big jumps.

Let me write helper for random range.

Leg animation: each hamster has 4 leg meshes. During walk, oscillate rotation.x with sine, alternating pairs. legAngle = sin(time*speed + phase) * 0.5. Front pair vs back pair opposite phase.

Also whole hamster slight vertical bob: body.position.y oscillates half frequency.

Let me code the Hamster class.

```js
const FLOOR = 0;
const WALL_BOUNTARY = { minX: -8.5, maxX: 8.5, minZ: -6.2, maxZ: 6.2 };

function makeHamster(baseColor, index) {
  const g = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color: baseColor, flatShading: true, roughness: 0.85, metalness: 0 });
  const bellyMat = new THREE.MeshStandardMaterial({ color: 0xfff4e0, flatShading: true, roughness: 0.9 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x2a2020, flatShading: true, roughness: 0.6 });
  const pink = new THREE.MeshStandardMaterial({ color: 0xffb0b8, flatShading: true, roughness: 0.7 });
  const white = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });

  // body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 14, 12), fur);
  body.scale.set(1, 0.85, 1.25);
  body.position.set(0, 0.45, 0);
  g.add(body);

  // belly
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.4, 12, 10), bellyMat);
  belly.scale.set(0.9, 0.75, 1.1);
  belly.position.set(0.05, 0.38, 0);
  g.add(belly);

  // head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.4, 14, 12), fur);
  head.scale.set(1, 0.95, 0.95);
  head.position.set(0.55, 0.62, 0);
  g.add(head);

  // ears
  const earGeo = new THREE.SphereGeometry(0.16, 8, 8);
  const earL = new THREE.Mesh(earGeo, fur);
  earL.position.set(0.42, 0.98, 0.22);
  earL.scale.set(1, 1, 0.7);
  const earR = earL.clone(); earR.position.z = -0.22;
  g.add(earL, earR);

  // eyes
  const eyeGeo = new THREE.SphereGeometry(0.09, 10, 10);
  const eyeL = new THREE.Mesh(eyeGeo, dark);
  eyeL.position.set(0.82, 0.7, 0.17);
  const eyeR = new THREE.Mesh(eyeGeo, dark);
  eyeR.position.set(0.82, 0.7, -0.17);
  g.add(eyeL, eyeR);
  // eye highlights
  const hlGeo = new THREE.SphereGeometry(0.03, 6, 6);
  const hlL = new THREE.Mesh(hlGeo, white);
  hlL.position.set(0.86, 0.73, 0.19);
  const hlR = hlL.clone(); hlR.position.z = -0.19;
  g.add(hlL, hlR);

  // nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.06, 8, 8), pink);
  nose.position.set(0.95, 0.6, 0);
  g.add(nose);

  // cheeks blush
  const cheekGeo = new THREE.SphereGeometry(0.1, 8, 8);
  const cheekL = new THREE.Mesh(checkGeo... 
```

Oops typo. Let me fix cheek. Actually blush optional; let me add small pink spheres.

```js
  const cheekGeo = new THREE.SphereGeometry(0.09, 8, 8);
  const cheekL = new THREE.Mesh(checkGeo, pink);
```
typo again. Let me write carefully in final.

  // tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), pink);
  tail.position.set(-0.6, 0.42, 0);
  g.add(tail);

  // legs
  const legGeo = new THREE.CylinderGeometry(0.085, 0.09, 0.28, 8);
  const feetMat = pink; // small hands/feet pink
  const legPositions = [
    { x: 0.35, z: 0.28, ph: 0 },     // front left
    { x: 0.35, z: -0.28, ph: Math.PI }, // front right
    { x: -0.35, z: 0.28, ph: Math.PI }, // back left
    { x: -0.35, z: -0.28, ph: 0 },   // back right
  ];
  const legs = [];
  for (const p of legPositions) {
    const leg = new THREE.Mesh(legGeo, fur);
    leg.position.set(p.x, 0.15, p.z);
    leg.userData.phase = p.ph;
    g.add(leg);
    legs.push(leg);
  }

  g.userData = { legs, head, body };
  return g;
}
```

Wait, legs at y=0.15 with height 0.28 → spans 0.01 to 0.29. Body bottom at 0.45 - 0.5*0.85 = 0.025. So legs attach near body bottom. But leg top at 0.29 < 0.025? No, 0.29 > 0.025 meaning leg extends above body bottom a bit, overlapping. That's fine visually (legs under body). Actually we want legs below body. Body bottom ~0.025, floor 0. Legs from 0 to 0.29 overlap with body lower region — acceptable, legs appear under belly. Good enough.

Actually the legs would visually clip into the floor/body but low-poly cute style tolerates it. Let me lower legs a touch: center at y=0.14. Fine.

Now the Hamster behavior wrapper. I'll create a class:

```js
class HamsterAI {
  constructor(mesh, wheel) {
    this.mesh = mesh;
    this.wheel = wheel; // {group, center, radius, spin: 0}
    this.state = 'pause';
    this.time = Math.random() * 3;
    this.target = new THREE.Vector3(rand(-6,6), 0, rand(-4,4));
    this.walkSpeed = 1.2 + Math.random()*0.8;
    this.baseY = 0;
    this.legPhase = 0;
    this.runTimer = 0;
  }
  ...
}
```

Update(dt):
```
this.time -= dt;
switch(state) {
  case 'pause':
    // idle, maybe spin
    if (this.time <= 0) { chooseNextState(); }
    break;
  case 'walk':
    move toward target; animate legs;
    if dist<0.4 -> arrive -> state pause with random timer
    break;
  case 'run':
    // on wheel
    animate; spin wheel fast;
    if time<=0 -> leave wheel -> walk away
}
```

chooseNextState: with prob go to wheel-run else wander.

Let me define positions:
- Wheel bottom point: center (wx, wy, wz). Bottom point is (wx, wy - radius, wz). Hamster stands there facing +z (or -z).
- Actually the hamster runs INSIDE near bottom. Let me place hamster at (wx, wy - radius + 0.25, wz) so it's slightly above bottom, facing +z. And wheel spins.

Movement for walk:
```
const dir = new THREE.Vector3().subVectors(target, mesh.position);
dir.y = 0;
const dist = dir.length();
if (dist > 0.02) {
  dir.normalize();
  mesh.position.addScaledVector(dir, walkSpeed*dt);
  // face direction
  const ang = Math.atan2(dir.x, dir.z);
  mesh.rotation.y = ang; // since nose is +x, rotating by ang makes +x point to dir (x,z)
  // animate legs
  this.legPhase += dt*walkSpeed*... 
} else {
  // arrived
  this.state='pause'; this.time = rand(1,3);
}
```

Rotation: nose at local +x. To face world dir (dx, dz), we want local +x aligned to (dx,0,dz). Rotation about Y by angle θ maps +x to (cosθ, 0, sinθ)? Standard: rotate about Y by θ: x-axis (1,0,0) → (cosθ, 0, -sinθ). Hmm sign depends on convention. Let me just compute θ = atan2(dx, dz) and check.

THREE rotate about Y (right-handed, positive rotates +x toward -z). Rotation matrix about Y:
[ cosθ, 0, sinθ ]
[ 0,1,0 ]
[ -sinθ, 0, cosθ ]
Applied to (1,0,0): (cosθ, 0, -sinθ). So +x → (cosθ,0,-sinθ). We want (dx,0,dz)/norm. So cosθ ∝ dx, -sinθ ∝ dz → θ = atan2(-dz, dx)? Let me set θ such that cosθ = dx, -sinθ = dz → sinθ = -dz → θ = atan2(-dz, dx) = atan2(dz, -dx)... messy.

Simplest: use lookAt or just compute mesh.rotation.y = Math.atan2(dir.x, dir.z) and adjust sign by testing. Many people use `mesh.rotation.y = Math.atan2(direction.x, direction.z)`. Let me reason: we want forward (+x) to point along (dir.x, 0, dir.z). 

Let me define rotation about Y by angle r. Under THREE's Y rotation, a vector v transforms. For forward f0 = (1,0,0). After rotation: fx = cos(r), fz = -sin(r) (from matrix above). We want fx/fz proportional to (dir.x, dir.z). So cos(r) ∝ dir.x and -sin(r) ∝ dir.z → tan: -sin(r)/cos(r) = dir.z/dir.x → -tan(r) = dir.z/dir.x → tan(r) = -dir.z/dir.x → r = atan2(-dir.z, dir.x).

Alternatively r = Math.atan2(dir.z, -dir.x)? Let me just use r = Math.atan2(dir.x, dir.z) and flip by testing, or better: I'll set forward differently.

Actually, simplest robust method: use `mesh.lookAt(target)` — but lookAt sets +Z to direction, and our nose is +x. That would misalign. I could instead rotate the model so nose is +z. Let me reorient the hamster model so it faces +z by default. Then lookAt works, or I compute rotation = atan2 for +z forward.

Let me reorient: after building, I'll rotate the whole group by -90° about Y so nose points to +z? Earlier I found -90° Y makes nose point +z. Let me verify: θ=-90: cos=0, sin=-1. Matrix: fx=cosθ=0, fz=-sinθ = -(-1)=1. So +x → (0,0,1) = +z. Yes! So rotate model -90° about Y → nose faces +z.

Then to face dir (dx, dz): we want +z axis → (dx,0,dz). Rotating about Y by r: original +z is (0,0,1). After Y rotation by r: (0,0,1) → (sin? ) Let me compute using matrix: v=(0,0,1). New x = cosθ*0 + sinθ*1 = sinθ. New z = -sinθ*0 + cosθ*1 = cosθ. So +z → (sinθ, 0, cosθ). We want ∝ (dx, dz). So sinθ ∝ dx, cosθ ∝ dz → θ = atan2(dx, dz). 

So mesh.rotation.y = Math.atan2(dir.x, dir.z). And model nose points +z by default. 

Let me apply mesh.rotateY(-Math.PI/2) after building, or build nose at +z. I'll rotate after building for simplicity: hamsterGroup.rotateY(-Math.PI/2). But then leg positions etc. are in local, fine.

Wait, but I built everything assuming nose at +x (head at x=0.55, eyes at x=0.82). If I rotate whole group -90° about Y, nose goes to +z. Good. All local coords unaffected, just final orientation.

Let me do that.

Now leg animation: rotate legs about X axis. leg.userData.phase gives offset. leg.rotation.x = sin(time*k + phase)*0.6. Front and back alternate: my phases already set front-left 0, front-right π, back-left π, back-right 0. So pairs alternate. Good. Only animate during walk.

Also bob body: body.position.y = 0.45 + abs(sin(...))*0.03. Keep subtle.

Let me incorporate a "hop" step motion: Actually simpler to just bob.

Run state on wheel:
- Set mesh.position to wheel bottom + offset, facing +z (already nose +z default, but wheel run direction—let me face -z so it runs "into" the wheel? doesn't matter). Let me face +z.
- Spin wheel: wheel.spin += dt * runSpeed (e.g., 6).
- Bob hamster up and down faster.
- Legs animate fast.
- timer counts down.

Leaving wheel: when run timer ends, set a target away from wheel (e.g., opposite side), state walk.

Let me also make sure hamster doesn't overlap others—skip, keep simple.

Click interaction: raycast against wheel group. On hit, force a random hamster to run on wheel (set its state to run, timer ~ rand 2-4). Also give wheel a spin boost.

Let me code raycaster in the module, on pointerdown or click.

Let me also add a subtle idle breathing for paused hamsters (scale body slightly).

Now let me write the full HTML. I'll include CSS for a nice overlay.

Let me also add wood-shavings bedding: a group of small flat boxes scattered on floor with brownish colors. ~50.

Food pellets: a few small spheres in a bowl. Let me add a food bowl at some position (decoration). Bowl: a half-sphere or a cylinder open top. Let me make a simple bowl: CylinderGeometry(radius, radius*0.7, h, 16) but only... Actually a full cylinder looks like a cup. For a bowl, use a lathe or just a truncated cone. Let me use ConeGeometry? Hmm. Let me make bowl from a sphere scaled flat + inner. Simplest cute bowl: a CylinderGeometry(topR, bottomR, height, 16) with bottomR smaller, material open? It'll look like a cup/bowl. Add a few small spheres (seeds) inside at top. Good enough.

Place bowl at (-6, 0, 3) maybe.

Let me now also add the wheel support and make wheel a group containing spinning part + static stand.

Wheel construction:
```
function makeWheel() {
  const wheel = new THREE.Group();
  const standMat = new THREE.MeshStandardMaterial({ color: 0xffd166, flatShading:true, roughness:0.8 });
  const rimMat = new THREE.MeshStandardMaterial({ color: 0xef476f, flatShading:true, roughness:0.6 });
  const rungMat = new THREE.MeshStandardMaterial({ color: 0xfffbdb, flatShading:true, roughness:0.7 });

  const cx = 8.2, cy = 2.2, r = 2.0;
  // spinning disc
  const disc = new THREE.Group();
  // rim torus lying in YZ plane
  const rim = new THREE.Mesh(new THREE.TorusGeometry(r, 0.09, 8, 24), rimMat);
  rim.rotation.x = Math.PI/2; // makes torus ring from XY to XZ? 
  ...
}
```

Wait, I need the disc in YZ plane and spin around X. Default torus ring is in XY plane (central axis Z). To move ring to YZ plane, rotate 90° about X: a point in XY (x,y,0) → after rot X by 90: x' = x, y' = -z =0, z' = y. So (x,y,0)->(x,0,y). So ring now in XZ? Hmm that puts it in XZ plane, central axis becomes... The tube circles around what was Z but now mapped to Y? This is confusing.

Let me think again. TorusGeometry(radius, tube, radialSegments, tubularSegments, arc). Default orientation: the torus lies in the XY plane, with the hole along the Z axis. So the "ring" circle is in XY, and the tube sweeps around Z (the central axis is Z).

To make the wheel stand vertically with its plane being YZ and spinning around X (horizontal axle along X), I need the ring circle in YZ plane and sweep around X.

If I rotate the torus by 90° about the X axis: The ring that was in XY moves to XZ? Let's see: rotate about X by +90°: (x,y,z)->(x, -z, y). Ring points originally (r cos t, r sin t, 0). After: (r cos t, 0, r sin t). So they lie in XZ plane (y=0). That's not YZ.

Rotate about X by -90°: (x,y,z)->(x, z, -y). Ring (r cos t, r sin t,0) -> (r cos t, 0, -r sin t). Still XZ plane.

Hmm so rotating about X keeps it in a plane containing X. I want plane YZ (no X variation in the ring). So I need to rotate about... The ring is currently in XY. To get to YZ, I need to rotate about X by 90°? XY->? Let me map axes: I want the ring's plane to become YZ. Currently ring normal is Z (ring in XY). I want ring normal to be X (ring in YZ). So rotate the torus so its normal Z -> X. That's a rotation about Y by -90°? Rotating Z-axis (0,0,1) to X-axis (1,0,0): rotation about Y by -90°: (x,y,z)->(z, y, -x)? Let me use standard: rotate about Y by θ: x-> x cosθ + z sinθ, z -> -x sinθ + z cosθ. For θ=-90: cos=0,sin=-1: x' = z*(-1)*... wait x' = x*0 + z*(-1) = -z. z' = -x*(-1) + z*0 = x. So (x,y,z)->(-z, y, x). Normal Z (0,0,1)-> (-1,0,0) = -X. Close enough (normal along X). Ring points (r cos t, r sin t, 0) -> (0, r sin t, r cos t). Those lie in YZ plane (x=0). 

So rotate torus about Y by -90° (or +90) to get ring in YZ plane, then spin around X.

Let me set rim.rotation.y = -Math.PI/2. Then spin disc.rotation.x.

Hmm wait, but I also need the rungs in the YZ plane. Rungs are cylinders along radial direction in the ring plane. Let me generate rungs as short cylinders positioned at angles around the ring, oriented radially (in YZ plane). Each rung: from center-ish to near rim, along direction (0, sin a, cos a). Cylinder default is along Y. I need to align cylinder Y-axis to the radial direction (0, sin a, cos a). Use a helper to orient a cylinder toward a vector.

Alternatively, simpler: make rungs as thin boxes (BoxGeometry) oriented radially. Box is easier to orient via quaternion.setFromUnitVectors or Euler.

Let me generate rungs using a group approach: for i in 0..N: angle a = i/N*2π. Position rung at radius r*0.5 along (0, sin a, cos a), oriented so its long axis is radial (Y->(0,sina,cosa)). Length ~ r*0.9.

Orient cylinder/box to a direction: 
```
const dir = new THREE.Vector3(0, Math.sin(a), Math.cos(a));
const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0), dir.normalize());
rung.quaternion.copy(quat);
```

Position rung at center + dir * (r*0.55).

Good.

Also add two side plates (discs) to give wheel some width, using CircleGeometry in YZ plane. CircleGeometry default is in XY plane (normal Z). Rotate about Y -90° to be in YZ. Place at x = ±0.06 (thin). Actually the wheel width: let me make the disc span from z offset. The stand posts hold it. Let me keep minimal: just rim + rungs + two side discs. Side discs radius r-0.05.

Let me also add a bottom guide rail? Not necessary.

Stand (static): two vertical posts from floor to wheel center height, at the sides of the wheel (in ±X direction from disc). Posts at x = cx ± 0.15? The wheel disc is at x=cx. Posts at x = cx - 0.2 and cx + 0.2? But wheel plane is YZ at x=cx. Posts should be on either side in X. Let me put posts at x = cx - 0.15 and cx + 0.15, from floor (y=0) up to y=cy+r or so, holding the axle. Plus a base foot.

Actually the axle is along X (through wheel center). Posts hold axle ends. Let me make two uprights each a box, connected by a horizontal bar (the axle) at top. Uprights at z = ±0.3 (in front/back of wheel) hmm. Let me keep it simple: two posts at (cx, 0, wz + 0.3) and (cx, 0, wz - 0.3)? No, those are in Z. The wheel is in YZ plane at x=cx, spanning z. Posts should support from the sides in X: postA at (cx - w, 0, wz), postB at (cx + w, 0, wz) where w ~0.15. Connect top with axle box along X. Each post from y=0 to y=cy. Add base feet for stability (boxes on floor extending in X).

Let me just build something plausible.

Given complexity, let me simplify the wheel to look decent:
- disc (rim + rungs + 2 side discs) spinning around X, at position (cx, cy, wz).
- stand: two boxes (posts) at (cx ± 0.12, cy/2, wz) going up; a top cross bar (box along X) at y=cy; base feet.

I think that's fine.

Let me set cx = 8.0, cy = 2.2, wz = 0, r = 1.9. Bottom of wheel = cy - r = 0.3. Slightly above floor; hamster runs at bottom ~ y=0.3..0.5. Let me lower so bottom near floor: cy = r = 1.9 → bottom 0. But then top at 3.8 < 4.5 clear wall. Let me set r=1.9, cy=1.9, bottom=0 exactly. Hamster at bottom y≈0.4 (standing) with wheel bottom at 0. Good. Actually the hamster's feet at floor 0, center ~0.5. Place hamster center at (cx, 0.5, wz) facing +z. Wheel bottom at 0 touches floor. 

But the hamster needs to be inside the wheel near the bottom inner surface. The inner bottom is at y = cy - r + tube ≈ 0. Place hamster at y=0.45, x=cx, z=wz. Facing +z. As wheel spins, it looks like running. Good.

Hold on, if the hamster is at x=cx exactly and the wheel disc is at x=cx with posts at cx±0.12, the hamster might clip with posts/discs. The hamster width ~1.2 deep (scaled) → spans x ±0.6. That would clip through posts and side discs. Since we view from an angle, minor clipping is OK but let me shift the hamster slightly in front of the wheel plane: place hamster at z = wz + 0.15 (in front) — but running direction +z would move it off. Eh.

Actually, let me reconsider the wheel orientation. Maybe better to have the wheel's plane be XZ? No.

Alternative: Put the wheel facing the camera-friendly side. Let me place the wheel at the BACK of the cage (z = -6) standing in XZ plane? Hmm.

Let me reconsider a cleaner setup: Place wheel against the back wall, wheel plane = XZ? No, wheel must be vertical. If against back wall (z=-7 wall is XY plane at z=-7), the wheel disc is parallel to that wall → disc in XY plane, axle along Z. Then spinning around Z. Hamster runs at bottom along X.

Disc in XY plane: that's the DEFAULT torus orientation! Nice, less rotation confusion. And spinning around Z.

But then from the typical camera angle (looking at XZ from an angle), a wheel in XY plane (vertical, facing +z/-z) would be seen edge-on if camera looks along Z. Our camera orbits around, so we'd see it from various angles; from the side (along X) we'd see the full disc. Fine.

Let me set wheel against back wall: cx=0, cz=-6, cy=1.9, r=1.9. Disc in XY plane (default), spin around Z. Hamster runs at bottom (cx, 0.45, cz) facing +x or -x.

Hmm, but a wheel at the back center might be blocked by camera sometimes. It's fine; orbit lets user rotate.

Actually, let me place it at the right side but with disc in XZ? No.

Let me just go with disc in XY plane (default torus), spin around Z, placed at (cx=6, cz=0, cy=1.9, r=1.9). Wait if disc is in XY plane at z=0, it's a vertical disc facing ±z. From front camera (looking along -z) you'd see it as a line (edge). As camera orbits you see the face. That's acceptable but at the default viewing angle it might look like a thin line initially. Let me set the initial camera angle to view from an isometric-ish angle so the wheel face is visible. If wheel disc normal is Z, to see the face I should view along X (looking in ±X). Let me aim initial camera to look from (15,12,15) toward origin, which has an X component, so we see the wheel somewhat face-on. Good enough.

Hmm, but the wheel at x=6 with disc in XY plane spanning x∈[6-1.9,6+1.9]= [4.1,7.9], z∈[-1.9,1.9]. Hamster at bottom (6, 0.45, 0). The disc is thin in Z (tube). The hamster depth along Z is ~1.2*0.5*... wait hamster body scaled z=1.25 radius 0.5 → z extent ±0.625. At z=0 that's within [-1.9,1.9]. Fine. The disc side plates at z=±0.06 would clip hamster's front/back (z ±0.625). Minor clipping, acceptable.

Actually, I realize the hamster running on a wheel that's edge-on to us at times looks weird. Let me instead orient the wheel so its face is more toward the camera generally. 

You know what, let me just place the wheel against the RIGHT wall with disc in YZ plane (spin around X), and accept that from the default camera angle we see it mostly face-on/side. Let me compute default camera: position (16,12,14) looking at origin. Direction ~ (-16,-12,-14) normalized. The wheel normal is X (YZ plane). Dot of camera forward with X axis: camera looks toward -X mostly (since position +x). So we look along -X, seeing the YZ disc face-on! Great, that works. The wheel (YZ plane, normal X) viewed along X axis → face-on. 

So wheel in YZ plane (spin X) at (cx=8, cz=0, cy=1.9, r=1.9), viewed from +x side → we see the face. 

Let me go with that: rim rotated so ring in YZ plane, spin around X.

Let me recompute torus rotation: I determined rotate about Y by -90° gives ring in YZ. Let me verify once more: default torus ring in XY plane, points (r cos t, r sin t, 0), normal +Z. Rotate whole torus about Y by -90°: mapping (x,y,z)->(-z, y, x) (derived earlier). Points → (0, r sin t, r cos t). Ring now in YZ plane (x=0), normal was +Z (0,0,1) → (-1*? apply: (0,0,1)->(-1*1? use mapping (-z,y,x): (0,0,1)->(-1,0,0)) so normal -X. Good, ring in YZ, spin around X.

So rim.rotation.y = -Math.PI/2. Then spin: disc.rotation.x increments.

Rungs: radial in YZ plane, direction (0, sin a, cos a). Orient box/cyl from +Y to that. Good.

Side discs: CircleGeometry in XY plane default (normal Z), rotate about Y -90° to YZ plane. Place at x=±0.05.

Stand: posts in ±X from disc. Post at (cx - 0.12, cy/2, cz) and (cx+0.12,...). Wait the disc is at x=cx spanning... disc is thin in X (side plates at x=cx±0.05). Posts at x=cx±0.15 hold it. Post from floor to cy. Connect top with axle box along X from cx-0.15 to cx+0.15 at y=cy. Base feet: boxes on floor extending ±X.

Hamster on wheel: position (cx, 0.45, cz)?? But disc side plates at x=cx±0.05, hamster spans x ±0.6 → clips plates and posts. To avoid, place hamster in front of the wheel plane: but wheel plane is YZ at x=cx; "front" is +x or -x. Place hamster at x = cx + 0.2 (just outside the wheel, in front of the near plate). Facing +z (running). As wheel spins behind it... hmm, that looks like hamster running alongside, not on. 

Real hamster runs INSIDE the wheel at the bottom. The hamster is between the side plates. So hamster x should be ≈ cx (within ±0.05). But hamster is wider than the gap. In reality hamster is small relative to wheel width. My hamster is big (body ~1.2 deep). Wheel width (gap between plates) is only 0.1. Mismatch.

Solution: Make the wheel WIDER (bigger gap) so hamster fits, OR make hamster thinner, OR just let it clip (acceptable for cute low-poly). Let me widen the wheel gap: side plates at x=cx±0.5, rungs length ~ r. Then hamster (x extent ±0.6) mostly fits within ±0.5... still slight clip but okay. Let me set plate gap ±0.55. Rungs span from -0.5 to +0.5 in x plus rim. Hamster center x=cx, fits. Posts at x=cx±0.7 (outside plates). 

Let me finalize wheel dims:
- r = 1.9
- plateGap = 1.2 (plates at ±0.6), so inner width 1.2.
- rungs length ~ 1.1 (from -0.55 to 0.55 in x).
- posts at x=cx±0.75.
- axle box from cx-0.75 to cx+0.75 at y=cy.

Hamster at (cx, 0.45, cz), faces +z. Its x extent ±0.6 within plates ±0.6 → borderline, fine.

Actually, wait: I want the hamster to appear INSIDE running at bottom. The bottom of the wheel inner surface is at y = cy - r = 0. Hamster feet at y=0 (floor). Hamster center y=0.45. As wheel spins, hamster stays. Good visual.

But the hamster is at the very bottom touching floor; the wheel bottom also at floor. Fine.

Let me also make sure wheel bottom isn't below floor. cy - r = 1.9 - 1.9 = 0. 

Now, the hamster's nose faces +z (we rotated model -90° Y). Running direction +z means it runs toward +z (into the cage). Fine.

Let me now also reconsider: when hamster is in run state, I set mesh.position to (cx, 0.45, cz) and rotation.y = 0 (nose +z). Good.

Alright, let me also add that clicking the wheel picks a random idle hamster and sends it to run. And the wheel gets a spin impulse.

Now the animation of wheel spin: 
- In run state, wheel.spin += dt * 8 (fast).
- Idle wheel: maybe slow continuous spin for life? Let me have it spin slowly always (ambient) and speed up when running. Actually let me keep it spinning slowly by default so it looks alive, and faster when a hamster runs.

Global wheel.spin accumulates; disc.rotation.x = wheel.spin.

Let me code.

Now let me also handle the "pause" states with occasional little turns (rotate mesh by random amount) and breathing.

Let me write the update for AI:

```
update(dt) {
  this.time -= dt;
  switch(this.state) {
    case 'pause':
      // idle bob
      this.mesh.position.y = 0;
      // gentle breathing
      const b = this.mesh.userData.body;
      if (b) { const s = 1 + Math.sin(performance.now()*0.002 + this.seed)*0.02; b.scale.y = 0.85*s; }
      // occasional turn
      if (this.turnTimer <= 0 && Math.random()<0.01) { this.spinTurn(); }
      if (this.time <= 0) this.pickNewState();
      break;
    case 'walk':
      const dir = new THREE.Vector3().subVectors(this.target, this.mesh.position); dir.y=0;
      const d = dir.length();
      if (d > 0.05) {
        dir.normalize();
        this.mesh.position.addScaledVector(dir, this.walkSpeed*dt);
        this.mesh.rotation.y = Math.atan2(dir.x, dir.z);
        // legs
        const lp = this.legPhase + dt*this.walkSpeed*6;
        this.mesh.userData.legs.forEach((leg,i)=>{
          leg.rotation.x = Math.sin(lp + leg.userData.phase) * 0.7;
        });
        // bob
        this.mesh.position.y = Math.abs(Math.sin(lp*0.5))*0.04;
      } else {
        this.mesh.position.y = 0;
        this.state='pause'; this.time = rand(1.5,4);
      }
      break;
    case 'run':
      // position fixed at wheel bottom
      this.mesh.position.set(wheel.cx, 0.45, wheel.cz);
      this.mesh.rotation.y = 0;
      wheel.spin += dt * 9;
      const rp = this.legPhase + dt*22;
      this.mesh.userData.legs.forEach((leg)=>{ leg.rotation.x = Math.sin(rp+leg.userData.phase)*0.9; });
      this.mesh.position.y = (Math.sin(rp*0.5)*0.5+0.5)*0.15; // bob
      if (this.time <= 0) {
        // leave wheel: pick a target away from wheel
        this.target = new THREE.Vector3(rand(-6,6),0,rand(-4,4));
        this.state='walk';
      }
      break;
  }
}
```

pickNewState:
```
pickNewState() {
  const roll = Math.random();
  if (roll < 0.25) {
    // go run on wheel
    this.state='run'; this.time = rand(2.5,5);
    this.legPhase = Math.random()*Math.PI*2;
  } else {
    this.state='walk';
    this.target = new THREE.Vector3(rand(-7,7), 0, rand(-5,5));
    this.legPhase = Math.random()*Math.PI*2;
  }
}
```

spinTurn: random extra rotation:
```
spinTurn() {
  this.mesh.rotation.y += rand(-1,1);
  this.turnTimer = rand(1,3);
}
```
But I reset turnTimer each pause; let me init turnTimer = rand(1,3).

Hmm, the breathing modifies body.scale.y but body is added to group; scaling works. But note I set base body scale in makeHamster; modifying is fine.

One concern: multiple hamsters running on wheel at once could stack at same position. Allow it (funny). Fine.

Raycast click:
```
function onClick(e) {
  mouse.x = (e.clientX/w)*2-1; mouse.y = -(e.clientY/h)*2+1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObject(wheel.disc, true);
  if (hits.length) {
    // pick an idle hamster
    const candidates = hamsters.filter(h=>h.state!=='run');
    if (candidates.length) {
      const h = candidates[Math.floor(Math.random()*candidates.length)];
      h.state='run'; h.time=rand(2.5,5); h.legPhase=Math.random()*6;
    }
    wheel.spin += 3;
  }
}
```

Good.

Let me set up renderer, controls, lights, build scene, then loop.

Let me write final code carefully, avoiding typos.

Let me also add window resize handler.

Let me add info overlay div with title and instructions.

Let me pick colors:
- Tray (base): 0xf2b7d5? Let me do tray pink 0xf9c7d1, walls lighter 0xffe3ec. Actually let me do a mint tray 0xbde0d0 and walls 0dffeed. Hmm. Let me choose:
  - Floor/tray: 0xfce4b8 (soft sand) — like bedding. Actually let me make tray a plastic color and floor bedding.
  
Let me do:
  - Tray base walls: 0x8ecae6 (light blue) cute.
  - Clear walls: 0cafdf with opacity 0.35.
  - Floor (tray bottom inside): 0xfff3d0 (bedding color) — I'll add bedding pieces.
  
Hamster colors (cute pastels): 
  0xffb3ba (pink), 0xbaaf (peach), 0xd0fcff? Let me pick: 
  ['#ffb3ba','#bad2ff','#baffcc','#ffffba','#e0bbff','#ffdfba']
  6 colors for 6 hamsters.

Let me make 6 hamsters.

Wheel: rim 0xef476f (pink), rungs 0xfffbdb (cream), stand 0ffd166 (yellow).

Let me write it all.

Let me be careful with TorusGeometry segments: radius 1.9, tube 0.09, radialSegments 8, tubularSegments 24.

Side discs: CircleGeometry(r-0.05, 20) rotated to YZ. But CircleGeometry is only a disc (flat), fine.

Rungs: BoxGeometry(length, width, height) oriented radially. Let me use BoxGeometry([0.06, rungLen, 0.06]) then orient. rungLen ~1.0. Position at center + dir*(0.0 + gap/2*... ). Actually place rung midpoint at radius*0.55 from center along dir, and its length spans across. Let me position rung at x=cx (center of gap), offset along dir by 0? The rung is radial so it goes from near center to near rim. If I center it at radius*0.55 along dir, it spans roughly radius*0.55 ± 0.5 → from 0.45 to 2.35 (if r=1.9, 0.55*1.9=1.045, ±0.5 → 0.545 to 1.545). Rim at r=1.9. So rung reaches 1.545, not quite to rim 1.9. Let me center at radius*0.65 and length 1.1 → 1.235 ±0.55 → 0.685..1.785, close to rim. Good enough. Let me center at 0.62*r and length 1.15.

Actually simpler: make rungs full radius from center to rim? That would look like spokes. Let me just do rungs as bars across the diameter? No, hamster wheel rungs go from hub to rim (spokes). Let me do spokes from radius 0.3 to r. Center at 0.6*r, length (r-0.3)=1.6 → half 0.8 → spans 0.3..1.9. length 1.6. Let me set rung length = r*0.85 =1.6, center at r*0.575 (=1.09) → spans 0.27..1.91. 

Let me set: rungLen = r*0.9 (1.71), centerDist = r*0.55 (1.045) → spans 0.19..1.90. Box half-length 0.855. Good.

Number of rungs: 16.

Now let me also double-check torus rotation for ring in YZ and spin axis X.

rim = new THREE.Mesh(new THREE.TorusGeometry(r, 0.09, 8, 24), rimMat)
rim.rotation.y = -Math.PI/2; // ring now in YZ
disc.add(rim)
Then spin disc.rotation.x += v. But wait, after rotating rim by -90° about Y, the rim's own local X axis corresponds to world Z? When I spin the disc about its local X, does that spin the ring (which is in world YZ) about world X? The disc group's local X = world X (disc not rotated except children). rim is rotated -90 about Y within disc. Spinning disc about local X (world X) rotates rim's ring (in YZ) about X. Yes! Because disc.rotation.x rotates everything in disc about X axis. The rim ring is in YZ plane; rotating about X spins it within YZ. Correct.

Good.

Rungs oriented radially in YZ: dir=(0,sina,cosa). Placed at disc center (cx,cy,cz) + offset in x by 0 (they're within the gap at x=cx) — but rungs need to span the gap in X. If rungs are thin boxes oriented radially in YZ, they have negligible X extent, so they won't connect the two side plates in X. That's fine visually (rungs are the steps; they attach to rim at rim points and to hub at center). The rim (torus) provides the circular edge. Rungs radiate out. Looks like a wheel. Good.

But rungs at x=cx only; the rim is also at x=cx (torus centered at disc origin which is at wheel position). Wait disc.position = wheel position (cx,cy,cz). Rim centered at disc origin. Rungs centered at disc origin too (I'll add them to disc at local 0, oriented radially). Good, all consistent.

Side plates: add to disc at local x=±0.06 (thin), CircleGeometry in YZ. Position mesh.position.x = ±0.06. Rotate to YZ. These give the wheel some depth and hide the back.

Posts/stand: separate static group (not spinning). Add to scene.

Let me now write everything out. I'll assemble.

Let me also ensure the wheel disc is added to scene (so raycast works) — yes.

Let me define wheel object as { disc, cx, cy, cz, spin }.

Now, potential issue: hamster model built with nose +x, then I rotate -90° about Y to point nose +z. But I also want the hamster's "up" to remain +y and body oriented properly. Rotating about Y only affects horizontal. Good.

But when I later set mesh.rotation.y = atan2(dir.x, dir.z) for walking, that overrides the -90°? No—the -90° was applied to the group's rotation initially (mesh.rotateY). Then setting rotation.y replaces it. That's fine because we want nose to point along dir regardless of initial. The initial -90° matters only when rotation.y=0 (nose +z). Good.

Wait, but mesh.rotateY(-90°) sets the current rotation to that. Then mesh.rotation.y = value sets Euler Y to value, but X and Z remain 0 (they were 0). Actually rotateY composes; after rotateY(-90), rotation is (0,-90,0) in some order. Setting .rotation.y = value changes only Y component to value, leaving X=0,Z=0. But the previous rotateY already set Y=-90; setting .rotation.y=0 would override to 0. Good, so when I set rotation.y=0 for wheel run, nose points +z. And initial default (before any walk) — I should set rotation.y appropriately or rely on the rotateY(-90). Let me just, after building, NOT call rotateY and instead build nose at +z directly? Building at +z is more code. Let me instead, right after creating mesh, do mesh.rotateY(-Math.PI/2). Then for walk I set rotation.y = atan2(dir.x,dir.z) which OVERRIDES the -90 (sets Y to that value, X,Z stay 0). Wait does setting .rotation.y override the earlier rotateY's Y? 

THREE Object3D.rotation is an Euler. Assigning .rotation.y = v sets euler.y = v. The earlier rotateY(-90) set euler.y = -90 (assuming no prior). So now euler.y = atan2(...) replaces it. euler.x=0,z=0. So net rotation is just about Y by atan2 value. Nose (local +x) rotated about Y by atan2 → points along (dir.x,0,dir.z)? Let me verify with earlier derivation (nose +z default, then rotate Y by r where r=atan2(dir.x,dir.z)): we derived that rotation about Y by r maps +z→(sin r,0,cos r) = (dir.x normalized? ) Let me check: r=atan2(dir.x,dir.z). sin r = dir.x/|.| , cos r = dir.z/|.|. So +z→(sin r,0,cos r)=(dir.x,0,dir.z)/|.|. Yes points along dir. 

But this assumed default nose is +z BEFORE applying rotation.y. But we ALSO did rotateY(-90) first which set nose to +z. Then .rotation.y=r applies additional Y rotation on top? NO—assigning .rotation.y = r REPLACES euler.y, it doesn't add. So the total rotation is just Y=r, not -90+r. That means nose would be at +z rotated by r, i.e., (sin r,0,cos r). Wait that's the same as if default were +z. Because we replaced Y entirely. So effectively nose starts at +z (we intended) and we rotate by r. 

But hold on: the rotateY(-90) set euler.y=-90 making nose +z. Then .rotation.y = r sets euler.y = r (replacing -90). So final euler.y = r. Nose = rotate about Y by r from local +x? NO. Local nose is +x. Final rotation is Y=r. Rotating local +x about Y by r: (cos r, 0, -sin r) [from earlier matrix]. That's NOT (sin r,0,cos r). 

I'm confusing myself. Let me restart the rotation analysis cleanly.

Local nose direction n0 = (1,0,0). We apply a single rotation: Y-axis by angle r. Under THREE right-handed Y rotation, a vector v transforms as v' = Ry(r) v where
Ry(r) = [ cos r, 0, sin r; 0,1,0; -sin r, 0, cos r ].
n0 = (1,0,0): n' = (cos r, 0, -sin r).

We want n' ∝ (dir.x, 0, dir.z). So cos r ∝ dir.x and -sin r ∝ dir.z.
Thus tan r = -dir.z/dir.x → r = atan2(-dir.z, dir.x).

So mesh.rotation.y = Math.atan2(-dir.z, dir.x). Let me double check: r=atan2(-dir.z, dir.x): cos r ∝ dir.x (adjacent), sin r ∝ -dir.z (opposite). Then n'=(cos r,0,-sin r) ∝ (dir.x, 0, -(-dir.z))=(dir.x,0,dir.z). Yes! Correct.

So I should NOT rely on rotateY(-90) + atan2(dir.x,dir.z). Instead either:
(A) Keep nose at +x (don't rotate model), and set rotation.y = atan2(-dir.z, dir.x).
(B) Rotate model so nose at +z, then set rotation.y = atan2(dir.x, dir.z).

Let me use option (A) to avoid confusion: don't rotate the model; use rotation.y = atan2(-dir.z, dir.x).

Let me verify (A) for a simple case: dir = (0,0,1) (want to face +z). r=atan2(-1, 0) = -90°. n' = (cos(-90),0,-sin(-90)) = (0, 0, -(-1)) = (0,0,1) = +z. Correct!

dir=(1,0,0) face +x: r=atan2(0,1)=0. n'=(1,0,0). Correct.

dir=(0,0,-1) face -z: r=atan2(1,0)=90°. n'=(cos90,0,-sin90)=(0,0,-1)=-z. Correct.

Great, option (A) works. I'll keep model nose +x and use rotation.y = atan2(-dir.z, dir.x).

For wheel run state, face +z: rotation.y = atan2(-cz_offset?,...). If I want nose +z: r=atan2(-1,0)=-90°. So mesh.rotation.y = -Math.PI/2. Let me just set that. Or I could face -z. Let me face -z so hamster runs "away" from viewer maybe. Doesn't matter. Let me set rotation.y = Math.PI/2 (face -z) for variety, or -90. I'll set -Math.PI/2 (face +z).

Hmm wait, but if the wheel is at x=cx and the hamster faces +z running into the cage, fine.

OK let me finalize with option (A). No model rotation needed.

Now, one more: the body is scaled z=1.25 (deep along z). Nose at +x. When facing +z (rotation.y=-90), the deep axis (z) becomes horizontal facing viewer. Looks like a round-ish hamster. Fine.

Let me now write the code fully and cleanly.

Let me also add subtle ambient occlusion feel via hemisphere light.

Lights:
- HemisphereLight(0xffffff, 0xbfd7ff, 0.7)
- DirectionalLight(0xfff5e0, 1.2) positioned (8, 12, 6), cast shadows, shadow camera adjusted.

Enable shadows: renderer.shadowMap.enabled=true; type PCSoft. Set lights cast/receive. Floor/tray receive shadows; hamsters cast. Might be heavy but OK.

Actually, to reduce risk of weird shadows, let me enable shadows but keep it simple. I'll set directional shadow map size 1024.

Let me include.

Now bedding: create a group of small flat boxes (shavings) on the floor, colors vary among browns/creams. ~60 pieces random positions within play area, random rotation, small scale.

Food bowl: at (-6,0,3). Bowl: use a LatheGeometry? Simpler: a CylinderGeometry with top radius 0.6, bottom 0.4, height 0.3, open. Material double side. Add ~5 small spheres (seeds) inside at top as food. Color bowl 0xa8d8ea (blue) to contrast.

Let me also maybe add a tiny house/shelter? Optional. Let me add a small "house" (a box with a triangular roof) for cuteness. Actually keep scope; I'll add a simple hut: a box + a cone roof, placed at (-6, ..., 3)? That's where bowl is. Let me put hut at (-6, 0, -3). Provide shelter vibe. Low effort. Let me add it: body box 1.4 wide, roof cone. Color warm wood.

Hmm, adding more objects increases code. Let me include a hut because it adds life and a place hamsters might wander near. But to keep stable and not overcomplicate, I'll add it simply.

Actually, let me keep it to requirements: cage, floor, hamsters, one interactive object (wheel). I'll add bedding and a food bowl and a hut as decorative extras for cuteness, but keep them simple. Fine.

Let me write the code now. I'll be careful.

Let me draft the JS module:

```js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xcfe8ff);
scene.fog = new THREE.Fog(0xcfe8ff, 30, 70);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(14, 12, 14);

const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0,1,0);
controls.minDistance = 8;
controls.maxDistance = 40;
controls.maxPolarAngle = Math.PI/2 + 0.15; // allow a bit below horizon? keep above

// Lights
scene.add(new THREE.HemisphereLight(0xffffff, 0xbcd6ff, 0.75));
const sun = new THREE.DirectionalLight(0xfff2d0, 1.3);
sun.position.set(10, 16, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 60;
sun.shadow.camera.left = -18;
sun.shadow.camera.right = 18;
sun.shadow.camera.top = 18;
sun.shadow.camera.bottom = -18;
sun.shadow.bias = -0.0005;
scene.add(sun);
```

Cage build:
```js
const CAGE = { hx:10, hz:7, baseH:1.5, topH:4.5 };
const trayMat = new THREE.MeshStandardMaterial({color:0x8ecae6, flatShading:true, roughness:0.6});
const wallMat = new THREE.MeshStandardMaterial({color:0xdff3ff, transparent:true, opacity:0.32, side:THREE.DoubleSide, roughness:0.5, transmission:0});
const floorMat = new THREE.MeshStandardMaterial({color:0xfff3d0, flatShading:true, roughness:1});

// floor
const floor = new THREE.Mesh(new THREE.BoxGeometry(CAGE.hx*2, 0.4, CAGE.hz*2), floorMat);
floor.position.y = -0.2;
floor.receiveShadow = true;
scene.add(floor);
```
Wait floor box height 0.4 at y=-0.2 → top at 0. Good, that's the tray bottom.

Base walls (opaque) from y=0 to baseH=1.5:
Front z=+hz: box (hx*2, baseH, 0.4) at (0, baseH/2, hz-0.2)
Back z=-hz: same at z=-(hz-0.2)
Left x=-hx: box(0.4, baseH, hz*2) at (-hx+0.2, baseH/2, 0)
Right x=+hx: at (hx-0.2,...)

Hmm the corner overlaps but fine.

Actually the floor box already covers the base footprint with thickness; adding base walls on top gives the tray sides. Let me place base walls with bottom at y=0 (top of floor) up to baseH.

Front wall: position (0, baseH/2, hz-0.2), size (hx*2, baseH, 0.4). But hx*2=20 equals floor width; wall at z=hz-0.2=6.8. Floor z extent ±7. So wall inside. Fine.

Let me compute positions:
- Front: (0, 0.75, 6.8), size (20, 1.5, 0.4)
- Back: (0, 0.75, -6.8), size (20,1.5,0.4)
- Left: (-9.8, 0.75, 0), size (0.4,1.5,14)
- Right: (9.8,0.75,0), size (0.4,1.5,14)

Clear walls from baseH(1.5) to topH(4.5), height 3:
- Front: (0, 3.0, 6.8), size (20,3,0.2) transparent
- Back: (0,3.0,-6.8)
- Left: (-9.8,3.0,0), size(0.2,3,14)
- Right: (9.8,3.0,0)

Add top rim? skip.

All these as Mesh, castShadow for base walls maybe. Let me set base walls castShadow true, receiveShadow true. Clear walls castShadow false (translucent).

Bedding: scatter small boxes on floor top (y~0.05). Colors: ['#e6c98a','#d9b383','#f0dfa8','#c9a86a','#ecd3a0']. ~70 pieces. Scale small, flat (thin box). Random rot.

Food bowl: at (-6,0,3). Let me build.

Hut: at (-6,0,-3). Build box + cone.

Wheel: as described at (8, 1.9, 0).

Hamsters: 6, placed at random positions, colors from palette.

Let me now write makeHamster and AI.

I'll store hamsters array of {mesh, ai}.

Let me define rand(a,b)=a+Math.random()*(b-a).

Let me code the AI inline as functions operating on mesh + shared wheel.

Actually a class is cleaner. Let me write class.

Let me write final code. I'll include everything.

Let me also add requestAnimationFrame loop with delta clamped to 0.05.

Let me now also make sure the hamster legs array and body accessible: store in mesh.userData.

Let me write makeHamster returning mesh with userData.legs, mesh.userData.body, mesh.userData.earL etc. And seed for breathing phase.

Let me write the pickling.

Edge: When hamster in 'run' state sets position each frame to wheel bottom; but if it just arrived from walk, there might be a frame mismatch—fine.

Let me also ensure hamsters don't start inside walls. Random within [-7,7]x[-5,5]. Good.

Let me write it all out now.

For the wheel side discs, CircleGeometry needs thetaOffset/Length fine.

Let me code rungs orientation helper:
```
function orientAlong(dir){
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0), dir.clone().normalize());
  return q;
}
```
dir=(0,sina,cosa).

Rung mesh: new THREE.Mesh(new THREE.BoxGeometry(0.06, rungLen, 0.06), rungMat). Apply quaternion. position at disc center + dir*(centerDist) but also x offset 0. Add to disc.

Wait, but BoxGeometry along Y; after orient to radial dir (in YZ), its length is along that radial. Good. Position at center + dir*centerDist. centerDist ~ r*0.55.

Let me set rungLen = r*0.9 = 1.71, centerDist = r*0.55 = 1.045. Spans 1.045±0.855 → 0.19..1.90. Reaches rim ~1.9. 

Number of rungs 16.

Side discs: CircleGeometry(r-0.12, 24) rotate Y -90°, position x=±0.06. Add to disc. Material same as rim or stand? Let me use rimMat with color but maybe lighter. Use a slightly darker rim for inside. Let me just use rimMat.

Actually side discs might look odd (filled disc). Let me instead make the wheel open (no discs) but add two side rails (thin boxes) at top and bottom? Overkill. Let me just add the two side discs; they make it read as a wheel and hide the back rungs. Fine.

Posts (stand): 
- Two posts: box(0.15, cy+something, 0.15)? They should be vertical along Y at the sides in X. But the wheel plane is YZ at x=cx; posts at x=cx±0.75. Post box size (0.15, cy, 0.15)? But that's a thin post; better a box (0.15, wheelTop, 0.4) to have depth. Let me make post = BoxGeometry(0.15, cy+0.3, 0.3) at (cx±0.75, (cy+0.3)/2, cz). Hmm height should reach the axle. Let me reach cy+0.2.
- Axle: BoxGeometry(1.7, 0.12, 0.12) at (cx, cy, cz) along X.
- Base feet: two boxes on floor at x=cx±0.75 extending in Z for stability: BoxGeometry(0.4,0.15,1.0) at (cx±0.75, 0.075, cz). Actually feet should spread; let me make base cross: a box along Z connecting posts at floor: BoxGeometry(1.7,0.15,0.4) at (cx,0.075,cz). Plus maybe front/back feet. Keep simple: one base box along X at floor connecting the two posts: BoxGeometry(1.7,0.15,0.4) at (cx,0.075,cz). Good enough for stability look.

Let me set standMat = yellow 0xffd166.

Post height: from floor to cy+0.2. Post at (cx±0.75, (cy+0.2)/2, cz), size (0.15, cy+0.2, 0.15). Add castShadow.

Now the hamster on wheel at (cx, 0.45, cz). Posts at x=cx±0.75 are outside hamster (x extent ±0.6). Good, no clip with posts. Side discs at x=cx±0.06 clip hamster front/back (z). Acceptable.

Alright. Let me also verify wheel bottom clears floor: cy - r = 0. Good, touches.

Let me write the whole thing.

I need to be careful that `scene.fog` with background color matches—fine.

Let me also add a subtle ground reflection? skip.

Let me write CSS overlay:
```
#overlay{position:fixed;left:0;top:0;padding:14px;color:#223;font-family:system-ui;pointer-events:none;z-index:1;}
#overlay h1{margin:0 0 4px;font-size:20px;}
#overlay p{margin:2px;font-size:13px;opacity:.8}
```
Background semi-transparent panel.

Add hint: "Click the wheel to make a hamster run!"

Let me finalize.

Let me write out the complete file now.

I'll double check the animation of legs referencing leg.userData.phase.

Also breathing modifies body.scale.y each pause frame—but I set base 0.85 in makeHamster and then multiply. Let me store baseBodyScaleY=0.85 and animate around it.

Let me also add a little tail wiggle? skip.

Let me also make sure to remove big delta.

Let me write.

Actually, I realize for the "run" state the hamster is at fixed position but I also want it to possibly be chosen from idle. When I click wheel, I set a random non-run hamster to run. But if it's currently walking, setting position to wheel instantly teleports—acceptable (funny). Or I could send it to walk to wheel first. Simpler: teleport. Fine.

Let me also ensure only a couple hamsters run at once to avoid chaos. It's fine.

Let me write final code. I'll keep comments minimal but present.

Let me also verify OrbitControls maxPolarAngle: I set Math.PI/2 + 0.15 to allow camera slightly below. With target y=1. Fine. But if camera goes below floor it's okay since we look up. Keep it.

Let me write.

Also, I should add a subtle idle "look around" by rotating head slightly in pause. Optional. Skip to reduce bugs.

Let me now produce the final HTML.

Let me reconsider hamster count & placement to avoid stacking: place at distinct spots.

Palette & placements:
colors = ['#ffb3ba','#bad2ff','#d6ffcc','#ffffba','#e0bbff','#ffdfba']
positions spread.

Let me code positions as I create.

Final code below.

Let me also ensure the wheel disc is added to scene (so raycast works) — yes.

Let me write.

Double-check: TorusGeometry(r, tube, radialSeg, tubularSeg). For low-poly, radialSeg 8, tubularSeg 20.

CircleGeometry(radius, segments=24).

Let me write.

Also note: When I set mesh.rotation.y for walk using atan2(-dir.z, dir.x), the hamster might flip if dir has negative? atan2 handles all quadrants. Good.

Let me also cap hamster within bounds during walk by clamping target inside bounds (already). And if it wanders out due to float error, clamp position. Add clamp.

Let me write clamp: 
```
this.mesh.position.x = THREE.MathUtils.clamp(this.mesh.position.x, -9, 9);
this.mesh.position.z = THREE.MathUtils.clamp(this.mesh.position.z, -6, 6);
```
Apply in walk when moving.

Now finalize.

I think this is solid. Let me write the complete file.

One more: I'll add a small "name tag" floating? skip.

Let me produce final answer.

Let me write the bedding generation:
```
const shavingColors = [0xe6c98a,0xd9b383,0xf0dfa8,0xc9a86a,0xf5e6c0];
const bedding = new THREE.Group();
const shGeo = new THREE.BoxGeometry(0.25,0.05,0.15);
for (let i=0;i<80;i++){
  const m = new THREE.Mesh(shGeo, new THREE.MeshStandardMaterial({color: shavingColors[i%shavingColors.length], flatShading:true, roughness:1}));
  m.position.set(rand(-9,9), 0.03, rand(-6,6));
  m.rotation.y = rand(0,Math.PI);
  m.scale.setScalar(rand(0.6,1.4));
  bedding.add(m);
}
scene.add(bedding);
```

Food bowl:
```
const bowl = new THREE.Group();
const bowlMat = new THREE.MeshStandardMaterial({color:0x56b6c2, flatShading:true, roughness:0.6, side:THREE.DoubleSide});
const bowlMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.6,0.4,0.3,16,1,false), bowlMat);
bowlMesh.position.y = 0.15;
bowlMesh.castShadow=true;
bowl.add(bowlMesh);
// food pellets
const foodMat = new THREE.MeshStandardMaterial({color:0x8b5a2b, flatShading:true});
for(i...){ pellet sphere radius 0.06 at y 0.3 within radius 0.5 }
bowl.position.set(-6,0,3);
scene.add(bowl);
```
Cylinder open top (openEnded true) — fine.

Hut:
```
const hut = new THREE.Group();
const hutMat = new THREE.MeshStandardMaterial({color:0xd4a373, flatShading:true, roughness:0.9});
const body = new THREE.Mesh(new THREE.BoxGeometry(1.6,1.2,1.6), hutMat);
body.position.y=0.6; body.castShadow=true;
const roof = new THREE.Mesh(new THREE.ConeGeometry(1.3,0.9,4), new THREE.MeshStandardMaterial({color:0xa94227, flatShading:true, roughness:0.9}));
roof.position.y=1.65; roof.rotation.y=Math.PI/4; // align diagonal
roof.castShadow=true;
hut.add(body,roof);
// door hole: small box dark
hut.position.set(-6,0,-3.5);
scene.add(hut);
```
Cone with 4 segments (tetrahedron-ish pyramid) roof. rotation.y 45° to align square base with hut. Good.

Now wheel. Let me write makeWheel returning {disc, stand, cx, cy, cz, spin}.

```
function makeWheel(){
  const cx=8, cy=1.9, cz=0, r=1.9;
  const wheel = { cx, cy, cz, spin:0.3, disc:null };
  const standMat = new THREE.MeshStandardMaterial({color:0xffd166, flatShading:true, roughness:0.7});
  const rimMat = new THREE.MeshStandardMaterial({color:0xef476f, flatShading:true, roughness:0.5});
  const rungMat = new THREE.MeshStandardMaterial({color:0xfffbdb, flatShading:true, roughness:0.7});

  const stand = new THREE.Group();
  // posts
  const postGeo = new THREE.BoxGeometry(0.16, cy+0.3, 0.16);
  const postL = new THREE.Mesh(postGeo, standMat); postL.position.set(cx-0.75,(cy+0.3)/2,cz); postL.castShadow=true;
  const postR = postL.clone(); postR.position.x=cx+0.75;
  // axle
  const axle = new THREE.Mesh(new THREE.BoxGeometry(1.7,0.14,0.14), standMat);
  axle.position.set(cx,cy,cz);
  // base
  const base = new THREE.Mesh(new THREE.BoxGeometry(1.9,0.15,0.7), standMat);
  base.position.set(cx,0.075,cz); base.castShadow=true;
  stand.add(postL,postR,axle,base);
  scene.add(stand);

  const disc = new THREE.Group();
  disc.position.set(cx,cy,cz);
  // rim
  const rim = new THREE.Mesh(new THREE.TorusGeometry(r,0.09,8,24), rimMat);
  rim.rotation.y = -Math.PI/2;
  rim.castShadow=true;
  disc.add(rim);
  // side discs
  const discGeo = new THREE.CircleGeometry(r-0.12,24);
  const sdL = new THREE.Mesh(discGeo, rimMat); sdL.rotation.y=-Math.PI/2; sdL.position.x=-0.06;
  const sdR = new THREE.Mesh(discGeo, rimMat); sdR.rotation.y=-Math.PI/2; sdR.position.x=0.06;
  disc.add(sdL,sdR);
  // rungs
  const rungLen = r*0.9;
  const rungGeo = new THREE.BoxGeometry(0.06,rungLen,0.06);
  for(let i=0;i<16;i++){
    const a = (i/16)*Math.PI*2;
    const dir = new THREE.Vector3(0, Math.sin(a), Math.cos(a));
    const rung = new THREE.Mesh(rungGeo, rungMat);
    rung.quaternion.copy(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0), dir));
    rung.position.copy(dir).multiplyScalar(r*0.55).add(disc.position);
    rung.castShadow=true;
    disc.add(rung);
  }
  scene.add(disc);
  wheel.disc = disc;
  return wheel;
}
```

Wait, rung.position: I compute dir (unit), multiply by r*0.55, add disc.position. But disc.position is (cx,cy,cz). Adding gives world coords. But rungs added to disc which is at (cx,cy,cz); if I set world position = disc.position + offset, that's equivalent to local offset. Since disc has no rotation except none (only children rotated), world==local for position. Good. Actually disc.position is set; adding children with world position = disc.position + dir*d works.

But careful: dir.normalize() in setFromUnitVectors mutates dir to unit; I used dir before normalize? I pass dir to setFromUnitVectors which normalizes a copy? setFromUnitVectors(v1, v2) computes rotation from v1 to v2 and normalizes v2 internally (returns normalized). It doesn't mutate my dir necessarily. Let me be safe: 
```
const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0), dir);
rung.quaternion.copy(q);
```
setFromUnitVectors normalizes the second vector internally without mutating mine? Actually it does normalize a clone. To be safe I'll clone. Let me do dir.clone().normalize() when computing position too.

Let me restructure rung loop:
```
const dir = new THREE.Vector3(0, Math.sin(a), Math.cos(a)).normalize();
const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0), dir);
rung.quaternion.copy(q);
rung.position.copy(disc.position).addScaledVector(dir, r*0.55);
```
Good.

Now hamster creation and AI.

Let me write class Hamster:

```
class Hamster {
  constructor(scene, color){
    this.mesh = makeHamster(color);
    scene.add(this.mesh);
    this.mesh.position.set(rand(-7,7),0,rand(-5,5));
    this.state='pause';
    this.time = rand(0,3);
    this.turnTimer = rand(1,3);
    this.target = new THREE.Vector3(rand(-7,7),0,rand(-5,5));
    this.walkSpeed = 1.3+Math.random()*0.7;
    this.legPhase = Math.random()*Math.PI*2;
    this.seed = Math.random()*10;
  }
  update(dt, wheel){
    this.time-=dt;
    switch(this.state){
      case 'pause':{
        this.mesh.position.y += (0-this.mesh.position.y)*Math.min(1,dt*8);
        // breathing
        const b=this.mesh.userData.body;
        if(b){ b.scale.y = 0.85 + Math.sin(performance.now()*0.002+this.seed)*0.02; }
        if(this.turnTimer--dt<=0 && Math.random()<0.02){
          this.mesh.rotation.y += rand(-0.8,0.8);
          this.turnTimer = rand(1.5,3.5);
        }
        if(this.time<=0) this.decide();
        break;
      }
      case 'walk':{
        const dir=new THREE.Vector3().subVectors(this.target,this.mesh.position); dir.y=0;
        const dist=dir.length();
        if(dist>0.05){
          dir.normalize();
          this.mesh.position.addScaledVector(dir,this.walkSpeed*dt);
          this.mesh.rotation.y = Math.atan2(-dir.z, dir.x);
          const lp=this.legPhase+dt*this.walkSpeed*6;
          this.mesh.userData.legs.forEach(leg=>{ leg.rotation.x=Math.sin(lp+leg.userData.phase)*0.7; });
          this.mesh.position.y = Math.abs(Math.sin(lp*0.5))*0.05;
          this.mesh.position.x = THREE.MathUtils.clamp(this.mesh.position.x,-9,9);
          this.mesh.position.z = THREE.MathUtils.clamp(this.mesh.position.z,-6,6);
        } else {
          this.mesh.position.y=0;
          this.state='pause'; this.time=rand(1.5,4);
        }
        break;
      }
      case 'run':{
        this.mesh.position.set(wheel.cx,0.45,wheel.cz);
        this.mesh.rotation.y=-Math.PI/2;
        wheel.spin+=dt*9;
        const rp=this.legPhase+dt*22;
        this.mesh.userData.legs.forEach(leg=>{ leg.rotation.x=Math.sin(rp+leg.userData.phase)*0.9; });
        this.mesh.position.y=(Math.sin(rp)*0.5+0.5)*0.18;
        if(this.time<=0){
          this.target=new THREE.Vector3(rand(-6,6),0,rand(-4,4));
          this.state='walk';
        }
        break;
      }
    }
  }
  decide(){
    if(Math.random()<0.3){
      this.state='run'; this.time=rand(2.5,5); this.legPhase=Math.random()*Math.PI*2;
    } else {
      this.state='walk';
      this.target=new THREE.Vector3(rand(-7,7),0,rand(-5,5));
      this.legPhase=Math.random()*Math.PI*2;
    }
  }
  forceRun(){
    this.state='run'; this.time=rand(2.5,5); this.legPhase=Math.random()*Math.PI*2;
    wheel.spin+=3;
  }
}
```

Note this.turnTimer--dt<=0 : decrement then compare. turnTimer starts number; --dt returns value then subtracts—messy. Let me do:
```
this.turnTimer-=dt;
if(this.turnTimer<=0 && Math.random()<0.02){ ...; this.turnTimer=rand(1.5,3.5);}
```
But this checks every frame; once <=0 it may trigger repeatedly. Guard with a flag or set to positive after. After triggering, set turnTimer=rand → positive, so next frames <=0 false until decremented again. But if dt large, could be <=0 for many frames before rand resets; but rand resets immediately after trigger same frame. Within same frame after trigger turnTimer>0. Next frame it's >0 again (unless dt huge). Fine.

Let me restructure pause turn:
```
if(this.turnTimer<=0){
  if(Math.random()<0.05){ this.mesh.rotation.y+=rand(-0.8,0.8); this.turnTimer=rand(1.5,3.5);}
} else this.turnTimer-=dt;
```
Simpler. Good.

makeHamster:
```
function makeHamster(color){
  const g=new THREE.Group();
  const fur=new THREE.MeshStandardMaterial({color,flatShading:true,roughness:0.85});
  const bellyMat=new THREE.MeshStandardMaterial({color:0xfff4e0,flatShading:true,roughness:0.9});
  const dark=new THREE.MeshStandardMaterial({color:0x2a2020,flatShading:true,roughness:0.6});
  const pink=new THREE.MeshStandardMaterial({color:0xffb0b8,flatShading:true,roughness:0.7});
  const white=new THREE.MeshStandardMaterial({color:0xffffff,flatShading:true});

  const body=new THREE.Mesh(new THREE.SphereGeometry(0.5,14,12),fur);
  body.scale.set(1,0.85,1.25); body.position.set(0,0.45,0); body.castShadow=true;
  g.add(body);

  const belly=new THREE.Mesh(new THREE.SphereGeometry(0.4,12,10),bellyMat);
  belly.scale.set(0.9,0.75,1.1); belly.position.set(0.05,0.36,0.08);
  g.add(belly);

  const head=new THREE.Mesh(new THREE.SphereGeometry(0.4,14,12),fur);
  head.scale.set(1,0.95,0.95); head.position.set(0.55,0.62,0); head.castShadow=true;
  g.add(head);

  const earGeo=new THREE.SphereGeometry(0.16,8,8);
  const earL=new THREE.Mesh(earGeo,fur); earL.position.set(0.42,0.98,0.22); earL.scale.set(1,1,0.7);
  const earR=new THREE.Mesh(earGeo,fur); earR.position.set(0.42,0.98,-0.22); earR.scale.set(1,1,0.7);
  g.add(earL,earR);

  const eyeGeo=new THREE.SphereGeometry(0.09,10,10);
  const eyeL=new THREE.Mesh(eyeGeo,dark); eyeL.position.set(0.82,0.7,0.17);
  const eyeR=new THREE.Mesh(eyeGeo,dark); eyeR.position.set(0.82,0.7,-0.17);
  g.add(eyeL,eyeR);
  const hlGeo=new THREE.SphereGeometry(0.03,6,6);
  const hlL=new THREE.Mesh(hlGeo,white); hlL.position.set(0.86,0.73,0.19);
  const hlR=new THREE.Mesh(hlGeo,white); hlR.position.set(0.86,0.73,-0.19);
  g.add(hlL,hlR);

  const nose=new THREE.Mesh(new THREE.SphereGeometry(0.06,8,8),pink);
  nose.position.set(0.95,0.6,0); g.add(nose);

  const cheekGeo=new THREE.SphereGeometry(0.09,8,8);
  const cheekL=new THREE.Mesh(checkGeo,pink); cheekL.position.set(0.7,0.55,0.28);
  const cheekR=new THREE.Mesh(checkGeo,pink); cheekR.position.set(0.7,0.55,-0.28);
  g.add(cheekL,cheekR);

  const tail=new THREE.Mesh(new THREE.SphereGeometry(0.1,8,8),pink);
  tail.position.set(-0.6,0.42,0); g.add(tail);

  const legGeo=new THREE.CylinderGeometry(0.085,0.09,0.28,8);
  const legs=[];
  const defs=[{x:0.35,z:0.28,ph:0},{x:0.35,z:-0.28,ph:Math.PI},{x:-0.35,z:0.28,ph:Math.PI},{x:-0.35,z:-0.28,ph:0}];
  for(const p of defs){
    const leg=new THREE.Mesh(legGeo,fur); leg.position.set(p.x,0.14,p.z); leg.userData.phase=p.ph; leg.castShadow=true;
    g.add(leg); legs.push(leg);
  }

  g.userData={legs,body,head};
  return g;
}
```
Fix typo cheekGeo usage.

Main:
```
const hamsters=[];
const palette=['#ffb3ba','#bad2ff','#d6ffcc','#ffffba','#e0bbff','#ffdfba'];
for(let i=0;i<6;i++){ const h=new Hamster(scene, palette[i]); h.start(i); hamsters.push(h);}
```
start places spread.

wheel = makeWheel(); scene background etc.

click:
```
const raycaster=new THREE.Raycaster(); const mouse=new THREE.Vector2();
window.addEventListener('click',(e)=>{
  mouse.x=(e.clientX/innerWidth)*2-1;
  mouse.y=-(e.clientY/innerHeight)*2+1;
  raycaster.setFromCamera(mouse,camera);
  if(raycaster.intersectObject(wheel.disc,true).length){
    const cand=hamsters.filter(h=>h.state!=='run');
    if(cand.length) cand[Math.floor(Math.random()*cand.length)].forceRun();
    wheel.spin+=3;
  }
});
```

loop:
```
let last=performance.now();
function animate(){
  requestAnimationFrame(animate);
  const now=performance.now();
  let dt=(now-last)/1000; last=now;
  if(dt>0.05)dt=0.05;
  controls.update();
  for(const h of hamsters) h.update(dt,wheel);
  wheel.disc.rotation.x += wheel.spin*dt;
  wheel.spin *= 0.985; // friction when nobody running? but run adds 9/frame; multiply dt already. Let me not friction to keep simple; but idle spin should decay. 
  renderer.render(scene,camera);
}
animate();
```

Hmm wheel.spin += dt*9 in run, and rotation += spin*dt. If I also multiply spin by 0.985 each frame, idle decays. But during run spin jumps to ~9 then decays—if no hamster, decays to slow idle. Let me keep a base idle spin: when spin<0.5 set to 0.5? Let me just let it decay and add a minimum. Actually let me not decay; instead: if no hamster running, spin slowly increase toward 0.6. Simpler: 
```
const running=hamsters.some(h=>h.state==='run');
if(running) wheel.spin = Math.max(wheel.spin, 6);
else wheel.spin += (0.6-wheel.spin)*Math.min(1,dt*2);
```
But run state already adds spin*dt*9 and rotation += spin*dt. Adding 9*dt per running hamster each frame could accumulate unbounded if many run. Let me cap: in run, set wheel.spin = 8 (not add). And rotation += spin*dt. That keeps consistent speed while running. Let me do that: in run: wheel.spin=8; Also forceRun sets spin=8. Idle: lerp toward 0.6.

Let me update run case: replace `wheel.spin+=dt*9` with `wheel.spin=8;`. And forceRun: wheel.spin=8. And main: lerp idle.

rotation: wheel.disc.rotation.x += wheel.spin*dt always.

Good, stable.

Let me finalize.

Also add resize:
```
window.addEventListener('resize',()=>{ camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth,innerHeight); });
```

I think it's ready. Let me write the final HTML file with everything.

I'll double check the animation of legs referencing leg.userData.phase.

Also breathing modifies body.scale.y each pause frame—but I set base 0.85 in makeHamster and then multiply. Let me store baseBodyScaleY=0.85 and animate around it.

Let me also add a little tail wiggle? skip.

Let me also make sure to remove big delta.

Let me write.
</think>

# Low-Poly Hamster Playground

Here's a complete, self-contained `index.html` that runs immediately in any modern browser. It builds a cute low-poly cage with six wandering hamsters, scattered bedding, a food bowl, a little hut, and an interactive running wheel that the hamsters actually run on — and that you can click to make a hamster sprint!

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; height: 100%; }
  body { font-family: system-ui, sans-serif; background: #000; }
  #overlay {
    position: fixed; left: 16px; top: 16px; z-index: 10;
    background: rgba(255,255,255,0.85); backdrop-filter: blur(6px);
    padding: 12px 14px; border-radius: 14px; max-width: 260px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15); color: #3a2f4d;
    pointer-events: none; user-select: none;
  }
  #overlay h1 { margin: 0 0 4px; font-size: 18px; }
  #overlay p { margin: 3px 0; font-size: 12.5px; line-height: 1.4; opacity: 0.85; }
  #overlay b { color: #d6336c; }
  canvas { display: block; }
</style>
</head>
<body>
<div id="overlay">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p><b>Drag</b> to rotate · <b>Scroll</b> to zoom</p>
  <p>Click the <b>wheel</b> to make a hamster run!</p>
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

/* ------------------------------------------------------------------
   Renderer / Camera / Lights
------------------------------------------------------------------ */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xcfe8ff);
scene.fog = new THREE.Fog(0xcfe8ff, 32, 70);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(15, 12, 15);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1, 0);
controls.minDistance = 8;
controls.maxDistance = 40;
controls.maxPolarAngle = Math.PI / 2 + 0.15;

scene.add(new THREE.HemisphereLight(0xffffff, 0xbfd7ff, 0.75));
const sun = new THREE.DirectionalLight(0xfff2d0, 1.35);
sun.position.set(10, 16, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 60;
sun.shadow.camera.left = -20;
sun.shadow.camera.right = 20;
sun.shadow.camera.top = 20;
sun.shadow.camera.bottom = -20;
sun.shadow.bias = -0.0004;
scene.add(sun);

/* ------------------------------------------------------------------
   Helpers
------------------------------------------------------------------ */
const rand = (a, b) => a + Math.random() * (b - a);

/* ------------------------------------------------------------------
   The Cage: tray base, opaque lower walls, translucent upper walls
------------------------------------------------------------------ */
const CAGE = { hx: 10, hz: 7, baseH: 1.5, topH: 4.5 };
const trayMat  = new THREE.MeshStandardMaterial({ color: 0x8ecae6, flatShading: true, roughness: 0.6 });
const wallMat  = new THREE.MeshStandardMaterial({ color: 0xdff3ff, transparent: true, opacity: 0.32, side: THREE.DoubleSide, roughness: 0.5 });
const floorMat = new THREE.MeshStandardMaterial({ color: 0xfff3d0, flatShading: true, roughness: 1 });

const floor = new THREE.Mesh(new THREE.BoxGeometry(CAGE.hx * 2, 0.4, CAGE.hz * 2), floorMat);
floor.position.y = -0.2; floor.receiveShadow = true; scene.add(floor);

function wall(w, h, d, x, y, z, mat) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(x, y, z);
  if (mat === trayMat) { m.castShadow = true; m.receiveShadow = true; }
  scene.add(m);
}
// opaque lower tray walls
wall(CAGE.hx * 2, CAGE.baseH, 0.4, 0, CAGE.baseH / 2,  CAGE.hz - 0.2, trayMat);
wall(CAGE.hx * 2, CAGE.baseH, 0.4, 0, CAGE.baseH / 2, -CAGE.hz + 0.2, trayMat);
wall(0.4, CAGE.baseH, CAGE.hz * 2, -CAGE.hx + 0.2, CAGE.baseH / 2, 0, trayMat);
wall(0.4, CAGE.baseH, CAGE.hz * 2,  CAGE.hx - 0.2, CAGE.baseH / 2, 0, trayMat);
// translucent upper acrylic walls
const cwH = CAGE.topH - CAGE.baseH;
wall(CAGE.hx * 2, cwH, 0.2, 0, (CAGE.baseH + CAGE.topH) / 2,  CAGE.hz - 0.2, wallMat);
wall(CAGE.hx * 2, cwH, 0.2, 0, (CAGE.baseH + CAGE.topH) / 2, -CAGE.hz + 0.2, wallMat);
wall(0.2, cwH, CAGE.hz * 2, -CAGE.hx + 0.2, (CAGE.baseH + CAGE.topH) / 2, 0, wallMat);
wall(0.2, cwH, CAGE.hz * 2,  CAGE.hx - 0.2, (CAGE.baseH + CAGE.topH) / 2, 0, wallMat);

/* ------------------------------------------------------------------
   Bedding (wood shavings) + Food bowl + Little hut
------------------------------------------------------------------ */
const shavings = new THREE.Group();
const shGeo = new THREE.BoxGeometry(0.25, 0.05, 0.15);
const shColors = [0xe6c98a, 0xd9b383, 0xf0dfa8, 0xc9a86a, 0xf5e6c0];
for (let i = 0; i < 90; i++) {
  const m = new THREE.Mesh(shGeo, new THREE.MeshStandardMaterial({ color: shColors[i % shColors.length], flatShading: true, roughness: 1 }));
  m.position.set(rand(-9, 9), 0.03, rand(-6, 6));
  m.rotation.y = rand(0, Math.PI);
  m.scale.setScalar(rand(0.6, 1.5));
  shavings.add(m);
}
scene.add(shavings);

const bowl = new THREE.Group();
const bowlMesh = new THREE.Mesh(
  new THREE.CylinderGeometry(0.6, 0.4, 0.3, 16, 1, true),
  new THREE.MeshStandardMaterial({ color: 0x56b6c2, flatShading: true, roughness: 0.6, side: THREE.DoubleSide }));
bowlMesh.position.y = 0.15; bowlMesh.castShadow = true; bowl.add(bowlMesh);
const foodMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, flatShading: true });
for (let i = 0; i < 8; i++) {
  const p = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 6), foodMat);
  const a = Math.random() * Math.PI * 2;
  p.position.set(Math.cos(a) * rand(0, 0.4), 0.32, Math.sin(a) * rand(0, 0.4));
  bowl.add(p);
}
bowl.position.set(-6, 0, 3); scene.add(bowl);

const hut = new THREE.Group();
const hutBody = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.2, 1.6),
  new THREE.MeshStandardMaterial({ color: 0xd4a373, flatShading: true, roughness: 0.9 }));
hutBody.position.y = 0.6; hutBody.castShadow = true; hut.add(hutBody);
const hutRoof = new THREE.Mesh(new THREE.ConeGeometry(1.3, 0.9, 4),
  new THREE.MeshStandardMaterial({ color: 0xa94227, flatShading: true, roughness: 0.9 }));
hutRoof.position.y = 1.65; hutRoof.rotation.y = Math.PI / 4; hutRoof.castShadow = true; hut.add(hutRoof);
const hutDoor = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.7, 0.05),
  new THREE.MeshStandardMaterial({ color: 0x3e2723, flatShading: true }));
hutDoor.position.set(0, 0.45, 0.8); hut.add(hutDoor);
hut.position.set(-6, 0, -3.5); scene.add(hut);

/* ------------------------------------------------------------------
   The Running Wheel (interactive)
------------------------------------------------------------------ */
function makeWheel() {
  const cx = 8, cy = 1.9, cz = 0, r = 1.9;
  const wheel = { cx, cy, cz, spin: 0.6, disc: null };

  const standMat = new THREE.MeshStandardMaterial({ color: 0xffd166, flatShading: true, roughness: 0.7 });
  const rimMat   = new THREE.MeshStandardMaterial({ color: 0xef476f, flatShading: true, roughness: 0.5 });
  const rungMat  = new THREE.MeshStandardMaterial({ color: 0xfffbdb, flatShading: true, roughness: 0.7 });

  const stand = new THREE.Group();
  const postGeo = new THREE.BoxGeometry(0.16, cy + 0.3, 0.16);
  const postL = new THREE.Mesh(postGeo, standMat); postL.position.set(cx - 0.75, (cy + 0.3) / 2, cz); postL.castShadow = true;
  const postR = postL.clone(); postR.position.x = cx + 0.75;
  const axle = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.14, 0.14), standMat); axle.position.set(cx, cy, cz);
  const base = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.15, 0.7), standMat); base.position.set(cx, 0.075, cz); base.castShadow = true;
  stand.add(postL, postR, axle, base);
  scene.add(stand);

  const disc = new THREE.Group();
  disc.position.set(cx, cy, cz);

  const rim = new THREE.Mesh(new THREE.TorusGeometry(r, 0.09, 8, 24), rimMat);
  rim.rotation.y = -Math.PI / 2;            // put the ring in the YZ plane
  rim.castShadow = true; disc.add(rim);

  const discGeo = new THREE.CircleGeometry(r - 0.12, 24);
  const sdL = new THREE.Mesh(discGeo, rimMat); sdL.rotation.y = -Math.PI / 2; sdL.position.x = -0.06;
  const sdR = new THREE.Mesh(discGeo, rimMat); sdR.rotation.y = -Math.PI / 2; sdR.position.x = 0.06;
  disc.add(sdL, sdR);

  const rungLen = r * 0.9, rungGeo = new THREE.BoxGeometry(0.06, rungLen, 0.06);
  for (let i = 0; i < 16; i++) {
    const a = (i / 16) * Math.PI * 2;
    const dir = new THREE.Vector3(0, Math.sin(a), Math.cos(a)).normalize();
    const rung = new THREE.Mesh(rungGeo, rungMat);
    rung.quaternion.copy(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir));
    rung.position.copy(disc.position).addScaledVector(dir, r * 0.55);
    rung.castShadow = true; disc.add(rung);
  }
  scene.add(disc);
  wheel.disc = disc;
  return wheel;
}
const wheel = makeWheel();

/* ------------------------------------------------------------------
   The Hamsters
------------------------------------------------------------------ */
function makeHamster(color) {
  const g = new THREE.Group();
  const fur     = new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.85 });
  const bellyMat= new THREE.MeshStandardMaterial({ color: 0xfff4e0, flatShading: true, roughness: 0.9 });
  const dark    = new THREE.MeshStandardMaterial({ color: 0x2a2020, flatShading: true, roughness: 0.6 });
  const pink    = new THREE.MeshStandardMaterial({ color: 0xffb0b8, flatShading: true, roughness: 0.7 });
  const white   = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 14, 12), fur);
  body.scale.set(1, 0.85, 1.25); body.position.set(0, 0.45, 0); body.castShadow = true; g.add(body);

  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.4, 12, 10), bellyMat);
  belly.scale.set(0.9, 0.75, 1.1); belly.position.set(0.05, 0.36, 0.08); g.add(belly);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.4, 14, 12), fur);
  head.scale.set(1, 0.95, 0.95); head.position.set(0.55, 0.62, 0); head.castShadow = true; g.add(head);

  const earGeo = new THREE.SphereGeometry(0.16, 8, 8);
  const earL = new THREE.Mesh(earGeo, fur); earL.position.set(0.42, 0.98, 0.22); earL.scale.set(1, 1, 0.7);
  const earR = new THREE.Mesh(earGeo, fur); earR.position.set(0.42, 0.98, -0.22); earR.scale.set(1, 1, 0.7);
  g.add(earL, earR);

  const eyeGeo = new THREE.SphereGeometry(0.09, 10, 10);
  const eyeL = new THREE.Mesh(eyeGeo, dark); eyeL.position.set(0.82, 0.7, 0.17);
  const eyeR = new THREE.Mesh(eyeGeo, dark); eyeR.position.set(0.82, 0.7, -0.17);
  g.add(eyeL, eyeR);
  const hlGeo = new THREE.SphereGeometry(0.03, 6, 6);
  const hlL = new THREE.Mesh(hlGeo, white); hlL.position.set(0.86, 0.73, 0.19);
  const hlR = new THREE.Mesh(hlGeo, white); hlR.position.set(0.86, 0.73, -0.19);
  g.add(hlL, hlR);

  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.06, 8, 8), pink);
  nose.position.set(0.95, 0.6, 0); g.add(nose);

  const cheekGeo = new THREE.SphereGeometry(0.09, 8, 8);
  const cheekL = new THREE.Mesh(checkGeo, pink); cheekL.position.set(0.7, 0.55, 0.28);
  const cheekR = new THREE.Mesh(checkGeo, pink); cheekR.position.set(0.7, 0.55, -0.28);
  g.add(cheekL, cheekR);

  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), pink);
  tail.position.set(-0.6, 0.42, 0); g.add(tail);

  const legGeo = new THREE.CylinderGeometry(0.085, 0.09, 0.28, 8);
  const legs = [];
  const defs = [
    { x: 0.35,  z: 0.28, ph: 0 },
    { x: 0.35,  z: -0.28, ph: Math.PI },
    { x: -0.35, z: 0.28, ph: Math.PI },
    { x: -0.35, z: -0.28, ph: 0 },
  ];
  for (const p of defs) {
    const leg = new THREE.Mesh(legGeo, fur);
    leg.position.set(p.x, 0.14, p.z); leg.userData.phase = p.ph; leg.castShadow = true;
    g.add(leg); legs.push(leg);
  }

  g.userData = { legs, body, head };
  return g;
}

class Hamster {
  constructor(scene, color) {
    this.mesh = makeHamster(color);
    scene.add(this.mesh);
    this.state = 'pause';
    this.time = rand(0, 3);
    this.turnTimer = rand(1, 3);
    this.target = new THREE.Vector3(rand(-7, 7), 0, rand(-5, 5));
    this.walkSpeed = 1.3 + Math.random() * 0.7;
    this.legPhase = Math.random() * Math.PI * 2;
    this.seed = Math.random() * 10;
  }

  update(dt, wheel) {
    this.time -= dt;
    switch (this.state) {
      case 'pause': {
        this.mesh.position.y += (0 - this.mesh.position.y) * Math.min(1, dt * 8);
        const b = this.mesh.userData.body;
        if (b) b.scale.y = 0.85 + Math.sin(performance.now() * 0.002 + this.seed) * 0.02;
        if (this.turnTimer <= 0) {
          if (Math.random() < 0.05) {
            this.mesh.rotation.y += rand(-0.8, 0.8);
            this.turnTimer = rand(1.5, 3.5);
          }
        } else this.turnTimer -= dt;
        if (this.time <= 0) this.decide();
        break;
      }
      case 'walk': {
        const dir = new THREE.Vector3().subVectors(this.target, this.mesh.position); dir.y = 0;
        const dist = dir.length();
        if (dist > 0.05) {
          dir.normalize();
          this.mesh.position.addScaledVector(dir, this.walkSpeed * dt);
          this.mesh.rotation.y = Math.atan2(-dir.z, dir.x);
          const lp = this.legPhase + dt * this.walkSpeed * 6;
          this.mesh.userData.legs.forEach(leg => { leg.rotation.x = Math.sin(lp + leg.userData.phase) * 0.7; });
          this.mesh.position.y = Math.abs(Math.sin(lp * 0.5)) * 0.05;
          this.mesh.position.x = THREE.MathUtils.clamp(this.mesh.position.x, -9, 9);
          this.mesh.position.z = THREE.MathUtils.clamp(this.mesh.position.z, -6, 6);
        } else {
          this.mesh.position.y = 0;
          this.state = 'pause'; this.time = rand(1.5, 4);
        }
        break;
      }
      case 'run': {
        this.mesh.position.set(wheel.cx, 0.45, wheel.cz);
        this.mesh.rotation.y = -Math.PI / 2;
        wheel.spin = 8;
        const rp = this.legPhase + dt * 22;
        this.mesh.userData.legs.forEach(leg => { leg.rotation.x = Math.sin(rp + leg.userData.phase) * 0.9; });
        this.mesh.position.y = (Math.sin(rp) * 0.5 + 0.5) * 0.18;
        if (this.time <= 0) {
          this.target = new THREE.Vector3(rand(-6, 6), 0, rand(-4, 4));
          this.state = 'walk';
        }
        break;
      }
    }
  }

  decide() {
    if (Math.random() < 0.3) {
      this.state = 'run'; this.time = rand(2.5, 5); this.legPhase = Math.random() * Math.PI * 2;
    } else {
      this.state = 'walk';
      this.target = new THREE.Vector3(rand(-7, 7), 0, rand(-5, 5));
      this.legPhase = Math.random() * Math.PI * 2;
    }
  }

  forceRun() {
    this.state = 'run'; this.time = rand(2.5, 5); this.legPhase = Math.random() * Math.PI * 2;
    wheel.spin = 8;
  }
}

const palette = ['#ffb3ba', '#bad2ff', '#d6ffcc', '#ffffba', '#e0bbff', '#ffdfba'];
const hamsters = [];
for (let i = 0; i < 6; i++) {
  const h = new Hamster(scene, palette[i]);
  const a = (i / 6) * Math.PI * 2;
  h.mesh.position.set(Math.cos(a) * 4, 0, Math.sin(a) * 3);
  hamsters.push(h);
}

/* ------------------------------------------------------------------
   Interaction: click the wheel to make a hamster run
------------------------------------------------------------------ */
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
window.addEventListener('click', (e) => {
  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  if (raycaster.intersectObject(wheel.disc, true).length) {
    const cand = hamsters.filter(h => h.state !== 'run');
    if (cand.length) cand[Math.floor(Math.random() * cand.length)].forceRun();
  }
});

/* ------------------------------------------------------------------
   Loop
------------------------------------------------------------------ */
let last = performance.now();
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  let dt = (now - last) / 1000; last = now;
  if (dt > 0.05) dt = 0.05;

  controls.update();
  for (const h of hamsters) h.update(dt, wheel);

  const running = hamsters.some(h => h.state === 'run');
  if (!running) wheel.spin += (0.6 - wheel.spin) * Math.min(1, dt * 2); // gentle idle spin
  wheel.disc.rotation.x += wheel.spin * dt;

  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## What's in the scene

- **Cage**: a pastel-blue plastic tray base with opaque lower walls and translucent "acrylic" upper walls.
- **Floor**: sandy bedding tray covered with ~90 scattered wood-shaving pieces.
- **Props**: a blue food bowl with seeds, a little wooden hut with a red roof, and the star — a **pink running wheel** on a yellow stand.
- **Six low-poly hamsters**, each built from primitive shapes (body, belly, head, ears, eyes with highlights, nose, cheeks, tail, four animated legs) in cute pastel colors.

## Behavior

Each hamster runs a tiny state machine:
- **Walk** → picks a random target, strides toward it, faces its movement direction, and cycles its legs with a subtle body bob.
- **Pause** → stands, gently "breathes," and occasionally does a little turn.
- **Run** → hops onto the wheel, which spins fast while its legs pump and it bobs up and down.

## Interactivity

- **Drag** to orbit the camera, **scroll** to zoom (OrbitControls).
- **Click the wheel** to force a random idle hamster to sprint on it.

Just save it as `index.html` and open it in any modern browser — no build step needed.