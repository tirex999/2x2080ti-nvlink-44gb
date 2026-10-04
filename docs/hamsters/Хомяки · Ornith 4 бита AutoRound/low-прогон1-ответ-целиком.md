Let me create a single-file HTML project using Three.js that shows a low-poly hamster playground. I'll need to:

1. Set up the HTML structure with Three.js (loaded from CDN)
2. Create a 3D scene with a cage/floor tray
3. Build several cute low-poly hamsters with simple geometry
4. Add an interactive object (like a wheel)
5. Implement autonomous behaviors for the hamsters (walking, pausing, turning, interacting)
6. Make it visually cute and colorful
7. Add camera controls so users can rotate

Let me think about the design:

**Hamster construction:**
- Body: an ellipsoid/sphere
- Head: sphere
- Ears: small spheres or cylinders
- Eyes: dark spheres
- Cheeks: small spheres
- Feet: small boxes/spheres
- Nose: small pink sphere
- Tail: tiny sphere

**Cage:**
- Floor tray (open box)
- Maybe walls (transparent or wireframe)
- Bedding material (small colored boxes scattered)

**Interactive object:**
- A exercise wheel that spins when hamsters use it
- Or a food bowl

Let me make a wheel that spins and hamsters can interact with it.

**Behaviors:**
- Wander randomly (pick a target point, walk toward it)
- Pause occasionally
- Turn around
- Some hamsters interact with the wheel

Let me write clean, stable code.

I'll use:
- Three.js r160+ from CDN
- OrbitControls from CDN

Let me build this carefully.

For the hamsters, I'll create a function that builds a hamster group with randomized colors (browns, grays, whites, etc.). Each hamster will have:
- state machine: WALKING_TO_TARGET, PAUSING, USING_WHEEL
- velocity/direction
- animation for legs

Let me code this up.

I'll structure the hamster with:
- bodyGroup containing all parts
- legs that animate

Let me write the full HTML now.

I want to make it robust and fun. Let me plan the hamster movement:

Each hamster has:
- target position (Vector3)
- speed
- state: 'wander' (moving to target), 'pause' (standing still), 'wheel' (on wheel)
- When wandering, pick random point within bounds
- When pausing, wait a random time then pick new target
- One hamster uses the wheel periodically

Actually let me keep it simpler but still interesting. Let me give each hamster a state machine:
- WANDER: move toward target
- PAUSE: stay put for a while
- WHEEL: go to wheel and ride it

Let me implement smooth rotation to face direction of movement.

Leg animation: rotate legs back and forth based on time when moving.

Let me write it all out.

For the interactive wheel: hamsters can ride it and it spins. Let me make one hamster that periodically rides the wheel, and the wheel spins accordingly.

Let me also add a food bowl that a hamster can approach and "eat" (nod head).

Actually, let me keep the scope reasonable: wheel + food bowl. One hamster rides the wheel, another eats at the bowl. Others wander.

Let me write the code.

I'll make the scene:
- Ground plane (wooden tray bottom)
- Low walls around the tray (so hamsters don't wander off) - maybe use invisible boundaries
- Bedding (scattered small cubes)
- Wheel
- Food bowl
- 4-5 hamsters

Camera: OrbitControls with auto-rotate slowly.

Let me code it now.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #fde9d0; font-family: 'Segoe UI', sans-serif; }
  #app { width: 100%; height: 100%; display: block; }
  #hud {
    position: fixed; top: 16px; left: 16px; z-index: 10;
    background: rgba(255,255,255,0.82); backdrop-filter: blur(6px);
    padding: 12px 16px; border-radius: 14px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    color: #5a3a2a; max-width: 280px;
  }
  #hud h1 { font-size: 18px; margin-bottom: 4px; }
  #hud p { font-size: 12px; line-height: 1.5; opacity: 0.85; }
  #loading {
    position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
    background: #fde9d0; color: #5a3a2a; font-size: 20px; z-index: 20;
  }
</style>
</head>
<body>
<div id="loading">Loading hamsters... 🐹</div>
<div id="hud">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate • Scroll to zoom • Watch the little guys wander, pause, eat, and exercise!</p>
</div>
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

// ... scene setup
</script>
</body>
</html>
```

Now let me fill in the JavaScript.

Scene setup:
- Renderer
- Scene
- Camera
- Lights (ambient + directional + hemisphere)
- OrbitControls

Cage:
- Tray: a shallow box (floor + low walls)
- Bedding: scattered small colored boxes

Let me define bounds for hamster movement.

Hamster builder function:

```js
function buildHamster(color, accentColor) {
  const group = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9 });
  const belly = new THREE.MeshStandardMaterial({ color: accentColor, flatShading: true, roughness: 0.9 });
  
  // Body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 12, 10), fur);
  body.scale.set(1, 0.9, 1.2);
  body.position.y = 0.55;
  group.add(body);
  
  // Belly
  const bellyMesh = new THREE.Mesh(new THREE.SphereGeometry(0.4, 10, 8), belly);
  bellyMesh.scale.set(1, 0.85, 1.1);
  bellyMesh.position.set(0, 0.5, 0.18);
  group.add(bellyMesh);
  
  // Head
  const head = new THREE.Group();
  const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.4, 12, 10), fur);
  headMesh.position.y = 0.95;
  head.add(headMesh);
  ...
}
```

Hmm, let me think about the head orientation. Hamsters face along +Z or -Z? Let me have them face +Z (forward is +Z). Then I rotate them to face movement direction.

Ears: two spheres on top of head.
Eyes: two dark spheres.
Nose: pink sphere.
Cheeks: two small spheres.
Feet: four small cylinders/spheres at bottom.
Tail: tiny sphere at back (-Z).

Let me attach the head as a child so it can bob when eating.

Legs: 4 legs, each a small capsule/cylinder, positioned at corners of body underside. Animate by rotating around X axis when walking.

Let me set up the group so that local +Z is forward.

Body center at y ~0.55, feet at y ~0.1.

Let me define leg pivot points at the top of each leg, near the body.

Actually for simplicity, let me make legs as small cylinders anchored at body bottom, and animate their rotation.

Let me just do it and make it look decent.

Movement logic:

```js
class Hamster {
  constructor(scene, opts) {
    this.mesh = buildHamster(...);
    scene.add(this.mesh);
    this.pos = new THREE.Vector3(randomX, 0, randomZ);
    this.mesh.position.copy(this.pos);
    this.heading = Math.random() * Math.PI * 2;
    this.speed = 0;
    this.state = 'wander';
    this.target = randomPoint();
    this.pauseTimer = 0;
    this.stateTimer = 0;
  }
  update(dt) {
    // state machine
  }
}
```

Let me define bounds: the tray is, say, 8 x 8 units, walls at ±4. Hamsters stay within ±3.5.

Wheel location: at one side, say (0, 0, -3.2). Wheel radius ~1.2.

Food bowl: at (2.5, 0, 2.5).

States:
- 'wander': move toward target. When reached, switch to 'pause'.
- 'pause': wait random time, then pick new target. Occasionally switch to 'eat' or 'wheel'.
- 'eat': move to food bowl, eat (bob head) for a while, then wander.
- 'wheel': move to wheel, climb on, ride for a while (wheel spins), then get off and wander.

Only some hamsters do special activities; others just wander and pause.

Let me assign roles randomly per hamster.

Let me implement wheel interaction: when a hamster is at the wheel, place it inside/on the wheel and spin the wheel based on hamster activity.

Actually simpler: hamster stands next to wheel at the "door" position and rides it. The wheel spins.

Let me make the wheel a torus (ring) with spokes, mounted on an axle. When a hamster rides, spin the ring.

Let me code the wheel:
- TorusGeometry for the ring
- Several cylinder spokes
- Two supporting posts
- An axle

Hamster rides at position just in front of the wheel (the opening). Let me place wheel facing +X or something. Let me orient the wheel in the YZ plane (axis along X), so hamster rides on the inside facing +X... hmm.

Actually a hamster wheel: the hamster runs inside, wheel rotates around horizontal axis. The hamster faces sideways relative to the wheel axis. Let me place wheel axis along Z (vertical-ish no). Let me think.

Wheel rotates in a vertical plane. The axis of rotation is horizontal. Let's say axis is along X. So the wheel is in the YZ plane. The hamster stands inside the wheel at the bottom, facing +X (along the axis)? No, hamsters face the direction they run, which is tangential. At the bottom of the wheel, tangential direction is horizontal (along Z if wheel in YZ plane). Hmm, this gets confusing.

Let me simplify: The wheel's flat face points along X (axis along X). The wheel spins in the YZ plane. A hamster rides inside facing +X (looking along the axle). That looks fine — like a real wheel where the hamster faces sideways.

Position of riding hamster: at the bottom of the wheel, offset slightly. Wheel center at (wheelX, wheelCenterY, wheelZ). Riding position: (wheelX, wheelBottomY, wheelZ). Hamster faces +X.

When spinning, the wheel mesh rotates around X axis.

OK let me just place the wheel and have the hamster stand in front of the opening.

Let me reconsider: I'll mount the wheel so its plane is the YZ plane, axis along X. Hamster rides at the bottom, facing +X. Good.

Wheel center: (wheelX, 1.2, wheelZ). Radius 1.1. Bottom of wheel at y ~0.1 (near floor). Hamster standing position: (wheelX, 0.5, wheelZ) but shifted to sit at bottom of wheel inner area. Actually hamster sits at bottom, so position (wheelX, 0.35, wheelZ) facing +X. But the wheel would overlap the hamster — that's fine, hamster is inside.

Hmm, but if hamster faces +X and wheel axis is X, the hamster's body (elongated along Z) would be along the tangential direction at bottom — good, that's how hamsters sit in wheels.

Wait, hamster body elongated along forward direction. At bottom of wheel, forward (running direction) is along Z. So body elongated along Z. Good. Facing +X means... no. If running direction is +Z at the bottom, then hamster faces +Z, not +X.

Let me re-examine. Wheel in YZ plane, spinning. At the bottom of the wheel, a point moves in the +Z or -Z direction (tangential). So the hamster runs in +Z direction, facing +Z. Its body is elongated along Z. Good. And it's located at the bottom of the wheel: (wheelX, wheelCenterY - radius, wheelZ).

So hamster faces +Z at riding position. I'll set heading = PI/2 (since +Z is heading PI/2 in my convention where heading 0 = +Z). Wait let me define heading 0 = +Z. Then facing +Z means heading 0.

OK good.

Let me finalize wheel placement: wheelX = -3, wheelZ = 0. Wheel axis along X. Hamster rides at (-3, 0.15, 0) facing +Z. Wheel spins around X axis.

Food bowl at (2.5, 0, 2.5). Hamster faces it and eats (head bobbing). Eating facing: hamster approaches bowl and faces it.

Alright, let me write everything.

Let me also add bedding: scatter ~40 small colored cubes on the floor.

Add a few decorations: maybe a small house/shelter, some food pellets in the bowl.

Let me keep it moderate. I'll add:
- Tray
- Bedding
- Wheel
- Food bowl with pellets
- A little hideout house (optional, adds cuteness)
- 5 hamsters

Let me write the code now, being careful.

I'll add shadows for depth (shadowMap). Directional light casts shadows.

Let me write the final code.

For controls, OrbitControls with enableDamping, autoRotate slowly, limits on polar angle so you don't go below ground.

Let me write it.

One concern: import maps and module scripts. Using unpkg CDN. Should work in modern browsers.

Let me also handle window resize.

Let me write the hamster building more concretely.

```js
const hamsterColors = [
  { fur: 0xd9a56b, belly: 0xf5e1c8 }, // classic tan
  { fur: 0x8c6a4f, belly: 0xe8d3b0 }, // brown
  { fur: 0xcfc0b0, belly: 0xfaf3e6 }, // gray
  { fur: 0xf0e6d8, belly: 0xffffff }, // white
  { fur: 0xe8b58a, belly: 0xfbe9d0 }, // ginger
];
```

Build function returns a group plus references to legs and head for animation.

Let me store parts on the hamster object for animation.

Let me define leg pivots. Each leg is a mesh; I'll rotate it about its top. To make it look natural, I'll position the leg mesh so its pivot (origin) is at the hip, and extend downward.

Approach: create leg geometry centered at origin, then translate so it hangs below. Use a pivot group.

Simplest: For each leg, create a group (pivot) at the hip position, then add the leg mesh offset downward within the pivot. Rotating the pivot rotates the leg.

Hip positions (relative to body): front-left, front-right, back-left, back-right. Body is elongated along Z (length 1.2*0.55 ~ 0.66 half-length? Actually scale 1.2 on sphere radius 0.55 gives half-length 0.66 along Z). Legs near front/back at Z ~ ±0.4, X ~ ±0.35, Y ~ 0.15.

Let me set leg pivot at body underside.

I'll build legs as small cylinders radius 0.1, length 0.25, positioned so top at pivot.

Let me code:

```js
function makeLeg() {
  const pivot = new THREE.Group();
  const leg = new THREE.Mesh(
    new THREE.CylinderGeometry(0.09, 0.11, 0.28, 8),
    footMat
  );
  leg.position.y = -0.14; // hang below pivot
  // add a little foot
  const foot = new THREE.Mesh(
    new THREE.SphereGeometry(0.12, 8, 6),
    footMat
  );
  foot.scale.set(1, 0.6, 1.3);
  foot.position.y = -0.28;
  pivot.add(leg, foot);
  return pivot;
}
```

Then place pivots at hip positions and add to group.

Animation: when walking, oscillate leg rotation: leg.rotation.x = Math.sin(time * speedFactor + phase) * 0.6.

Head bob: when eating, head.position.y oscillates.

Now the whole hamster group: body at y 0.5, head higher.

Let me set body center y = 0.55 (radius 0.55 scaled). Feet bottoms at y ~ 0.02. Good, sits on floor.

Head group positioned at local (0, 0.95, 0.05) maybe. Actually head should be at front (+Z) a bit. Let me place head at (0, 0.95, 0.15) so it's forward and up. Ears on top, eyes on front, nose at front.

Eyes: at (0, 1.0, 0.42) left/right small offsets x ±0.18.
Ears: at (±0.18, 1.25, 0) spheres radius 0.12.
Nose: (0, 0.92, 0.52) pink small sphere.
Cheeks: (±0.22, 0.85, 0.28) small spheres, translucent-ish.

Tail: small sphere at (0, 0.55, -0.6).

Let me assemble.

Now movement update:

```js
update(dt) {
  const m = this.mesh;
  this.stateTimer -= dt;
  
  if (this.state === 'wander') {
    const dir = new THREE.Vector3().subVectors(this.target, m.position);
    dir.y = 0;
    const dist = dir.length();
    if (dist < 0.15) {
      this.state = 'pause';
      this.stateTimer = 1.5 + Math.random() * 3;
      this.speed = 0;
    } else {
      dir.normalize();
      const step = this.maxSpeed * dt;
      m.position.addScaledVector(dir, step);
      // face direction
      this.heading = Math.atan2(dir.x, dir.z);
      m.rotation.y = this.heading;
      this.speed = this.maxSpeed;
      // bounce off walls
      clampToBounds(m.position);
      // occasionally turn
      if (Math.random() < 0.01) {
        this.heading += (Math.random() - 0.5) * 1.2;
        m.rotation.y = this.heading;
      }
    }
  } else if (this.state === 'pause') {
    this.speed = 0;
    if (this.stateTimer <= 0) {
      // choose next action
      const r = Math.random();
      if (r < 0.15 && this.canDoSpecial) {
        if (Math.random() < 0.5) { this.state = 'wheel'; this.stateTimer = 6; }
        else { this.state = 'eat'; this.stateTimer = 4; }
      } else {
        this.target = randomPoint();
        this.state = 'wander';
        this.stateTimer = 5 + Math.random() * 5;
      }
    }
  }
  // leg & idle animation based on speed
  ...
}
```

Clamp to bounds: keep within ±3.3. If exceeds, push back and pick new target.

randomPoint: random x,z within [-3.3, 3.3].

For special activity, navigate to wheel/bowl. When arriving, transition into "riding"/"eating" sub-state with timer.

Let me refine states: 
- 'wheel': move to wheel door position. When close, set position to riding spot, face +Z, set subState 'riding', wheelSpin active. After timer, set state 'wander' with new target.
- 'eat': move to bowl. When close, set position, face bowl, subState 'eating' (head bob). After timer, wander.

I'll manage this with a small state enum plus flags.

Let me restructure with explicit states:

```
WANDER, PAUSE, GO_WHEEL, RIDE_WHEEL, GO_EAT, EAT
```

Let me code it fully.

For riding wheel, I'll set hamster position to riding spot and let the wheel spin based on a global "wheelActive" count.

Let me track number of hamsters currently riding to spin wheel.

Actually simpler: when a hamster is in RIDE_WHEEL state, increment wheelSpinSpeed; when none, decelerate.

Let me just spin the wheel continuously a bit and faster when someone rides.

Let me finalize and write the complete file.

Let me also add subtle idle breathing (body scale pulse) and blinking (eye scale) for cuteness. Blinking: periodically squash eyes on Y.

I'll add blinking in the main loop for all hamsters: random blink.

Let me write it all.

Also add a soft background gradient via canvas or CSS. I'll set scene background color and fog for depth.

Let me now write the entire thing.

Let me be careful with the wheel geometry and mounting.

Wheel:
- axis along X
- center at (wheelX, wheelCY, wheelZ) = (-3, 1.1, 0)
- ring radius 1.0, tube 0.08 -> TorusGeometry(1.0, 0.08, 10, 24)
- spokes: 6 cylinders along X connecting center to ring, radius 0.04, length 2.0
- axle: cylinder along X length ~1.4 at center
- two stand posts (vertical cylinders) at (wheelX ± 0.7, ...) supporting the axle

The spinning part is a group containing ring + spokes + axle. The stands are static.

Hamster rides at bottom of wheel: position (wheelX, wheelCY - 1.0 + 0.15, wheelZ) = (-3, 0.25, 0), facing +Z (heading 0). Actually the hamster sits at the bottom inside; its feet at floor y~0. Let me place hamster at y such that feet touch floor: body center y ~0.5, so hamster.position.y = 0.5 - ... hmm the hamster group origin is at its feet level? Let me set hamster group origin at floor level (y=0 at feet bottom). Then body at local y 0.55, feet from 0 to 0.28. So hamster.position.y should be ~0.0 (feet at floor). But riding inside wheel at bottom, hamster sits slightly above floor? Let me place at y=0.05. Fine.

Facing +Z => rotation.y = 0.

Wheel spin: wheelSpinGroup.rotation.x += speed * dt.

Let me make wheel spin when riding.

Food bowl:
- a shallow cylinder (bowl) at (2.5, 0.08, 2.5), radius 0.5, height 0.2, open top.
- pellets: small spheres (yellow/orange) inside.

Hideout house (optional): a box with triangular roof at (-2.5, 0, 2.5). Cute. Let me add it.

Alright, writing final code now. Let me make sure everything is wired.

Let me also make the floor/tray:
- Tray floor: BoxGeometry(9, 0.3, 9) at y -0.15 (top at 0). Color wood/beige.
- Walls: 4 low walls height 0.6, open top. Color light blue/white. Use box geometries.
- Actually let me make walls transparent-ish acrylic? Let me make them semi-transparent light blue so you can see inside. Or solid pastel. Let me do solid pastel walls with rounded look. I'll do low walls height 0.7.

Bedding: scatter ~50 small boxes in varying warm colors on top of floor (y ~0.05-0.15).

Let me write.

I'll also add ambient + hemisphere + directional lights, plus a point light for warmth.

Let me finalize the code and test mentally.

Let me write the complete index.html.

I need to be careful about the import map URL and module type.

Let me produce final answer.

For blinking: each hamster has blinkTimer; when <=0, do a quick blink (scale eyes Y to 0.1 for 0.15s).

Let me incorporate blink in update using time.

Let me write helper for eyes blink: store eye meshes array; set scaleY.

Alright.

Let me also ensure the hamsters don't overlap too much — not critical, keep simple.

Now let me write the full code carefully.

I'll set canvas fullscreen.

Let me write:

```js
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xfde9d0);
scene.fog = new THREE.Fog(0xfde9d0, 12, 26);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(6, 7, 9);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0.5, 0);
controls.minDistance = 4;
controls.maxDistance = 20;
controls.maxPolarAngle = Math.PI * 0.49;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.6;
```

Lights:
```js
scene.add(new THREE.HemisphereLight(0xbfd9ff, 0x6b4a30, 0.7));
const amb = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(amb);
const sun = new THREE.DirectionalLight(0xfff4e0, 1.3);
sun.position.set(6, 10, 5);
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
scene.add(new THREE.PointLight(0xffd9a0, 0.4, 30));
```

Cage/tray:
```js
const trayGroup = new THREE.Group();
scene.add(trayGroup);
const trayMat = new THREE.MeshStandardMaterial({ color: 0x8ec5e8, flatShading: true, roughness: 0.8 });
// floor
const floor = new THREE.Mesh(new THREE.BoxGeometry(10, 0.4, 10), new THREE.MeshStandardMaterial({ color: 0xf3c98b, flatShading: true, roughness: 0.95 }));
floor.position.y = -0.2;
floor.receiveShadow = true;
trayGroup.add(floor);
// walls
const wallH = 0.8, wallT = 0.3;
const wallMats = new THREE.MeshStandardMaterial({ color: 0xbfe3f5, flatShading: true, roughness: 0.7, transparent: true, opacity: 0.55 });
const wallDefs = [
  { s:[10.6, wallH, wallT], p:[0, wallH/2 - 0.4, 5.3] },
  { s:[10.6, wallH, wallT], p:[0, wallH/2 - 0.4, -5.3] },
  { s:[wallT, wallH, 10.6], p:[5.3, wallH/2 - 0.4, 0] },
  { s:[wallT, wallH, 10.6], p:[-5.3, wallH/2 - 0.4, 0] },
];
for (const w of wallDefs) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(...w.s), wallMats);
  m.position.set(...w.p);
  m.castShadow = true;
  trayGroup.add(m);
}
```

Hmm walls at y = wallH/2 - 0.4 so bottom aligns with floor top (y=0). floor top at y=0. So wall bottom at 0, top at wallH=0.8 => center at 0.4. Let me set p.y = 0.4. But floor is at -0.2 with height 0.4 so top at 0. Good, wall center y = 0.4. Let me fix: p.y = wallH/2 = 0.4. Remove -0.4.

Bedding:
```js
const beddingColors = [0xf5e1b8, 0xe8c98a, 0xf0d9b0, 0xdcc08a, 0xf7ecc8];
for (let i = 0; i < 120; i++) {
  const b = new THREE.Mesh(
    new THREE.BoxGeometry(0.18 + Math.random()*0.16, 0.08 + Math.random()*0.08, 0.18 + Math.random()*0.16),
    new THREE.MeshStandardMaterial({ color: beddingColors[Math.floor(Math.random()*beddingColors.length)], flatShading: true, roughness: 1 })
  );
  b.position.set((Math.random()-0.5)*9.2, 0.06 + Math.random()*0.06, (Math.random()-0.5)*9.2);
  b.rotation.y = Math.random()*Math.PI;
  b.castShadow = false;
  b.receiveShadow = true;
  trayGroup.add(b);
}
```

Wheel:
```js
const wheelGroup = new THREE.Group();
scene.add(wheelGroup);
const wheelX = -3.4, wheelZ = 0, wheelCY = 1.1, wheelR = 1.0;
const spinGroup = new THREE.Group();
wheelGroup.add(spinGroup);
const rimMat = new THREE.MeshStandardMaterial({ color: 0xff8fb3, flatShading: true, roughness: 0.5, metalness: 0.1 });
const rim = new THREE.Mesh(new THREE.TorusGeometry(wheelR, 0.07, 10, 28), rimMat);
spinGroup.add(rim);
const barMat = new THREE.MeshStandardMaterial({ color: 0xffc1d6, flatShading: true, roughness: 0.6 });
for (let i = 0; i < 6; i++) {
  const a = (i/6) * Math.PI * 2;
  const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, wheelR*2, 8), barMat);
  spoke.rotation.z = a;
  spoke.position.set(Math.cos(a)*wheelR*0.5, Math.sin(a)*wheelR*0.5, 0);
  // hmm orientation
  spinGroup.add(spoke);
}
// axle
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.3, 10), barMat);
axle.rotation.z = Math.PI/2;
spinGroup.add(axle);
// stands
const standMat = new THREE.MeshStandardMaterial({ color: 0x9ad4ff, flatShading: true, roughness: 0.7 });
for (const sx of [-0.7, 0.7]) {
  const stand = new THREE.Mesh(new THREE.BoxGeometry(0.16, wheelCY - 0.05, 0.16), standMat);
  stand.position.set(wheelX + sx, (wheelCY-0.05)/2, 0);
  stand.castShadow = true;
  wheelGroup.add(stand);
  // arm to axle
  const arm = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 0.9), standMat);
  arm.position.set(wheelX + sx*0.9? ... 
}
```

This is getting complicated. Let me simplify the wheel mounts: two vertical posts at (wheelX ± 0.7, ...) and a horizontal bar connecting them at axle height. Actually the axle is along Z? No, wheel axis is along Z now? Let me reconsider orientation.

If wheel is in YZ plane, its axis is along X. Spokes radiate in YZ plane. Axle along X. Posts must support the axle ends along X, so posts at X = wheelX ± 0.65. Posts vertical. A cross bar connects them.

Let me set:
- Posts: two boxes at (wheelX ± 0.65, postHeight/2, wheelZ), size 0.14 x 2.1 x 0.14.
- Top bar: box at (wheelX, 2.0, wheelZ) size 1.3 x 0.14 x 0.14 connecting posts (along X).

Axle along X at height wheelCY. spinGroup centered at (wheelX, wheelCY, wheelZ).

Riding position: hamster at bottom of wheel inner: (wheelX, wheelCY - wheelR + 0.12, wheelZ) = (-3.4, 0.22, 0). Facing +Z (heading 0). But hamster body might stick out the bottom below floor — fine, it's at y 0.22 center, feet near floor y~0.06. OK.

Actually wait, wheelCY - wheelR = 0.1, that's the bottom of the wheel. Hamster sits there. Good.

Let me set wheelCY = 1.1, wheelR = 1.0 => bottom at 0.1. Hamster center at 0.22 + ... let me just place hamster at y=0.12 when riding (body low). Actually let me raise wheel a bit so hamster feet rest near floor. Let me set wheelCY = 1.15, wheelR = 1.05 => bottom at 0.1. Hamster riding center y ~0.2.

Fine.

Post height ~2.2 (from floor y=0 to top 2.2). Axle at wheelCY=1.15.

Let me set posts from y=0 to y=2.2, centered 1.1. Top bar at y=2.1.

Let me finalize numbers:
- wheelX = -3.4, wheelZ = 0
- wheelR = 1.05, wheelCY = 1.2
- bottom of wheel = 0.15
- posts at X = wheelX ± 0.7, height 2.2 (center 1.1), size 0.14x2.2x0.14
- top bar at y 2.05, size 1.5 x 0.14 x 0.14 (along X)
- axle along X at y 1.2, length 1.4

Riding pos: (-3.4, 0.18, 0), heading 0 (facing +Z).

Food bowl at (2.6, 0, 2.6). Hamster faces it: direction from hamster to bowl. When eating, hamster stands at (2.6 - 0.6, 0, 2.6)?? Let me place hamster eating at position (2.0, 0, 2.0) facing toward bowl (direction (0.6,0,0.6) normalized => heading atan2(0.6,0.6)=PI/4). Actually simpler: place hamster at (2.6,0,3.2) facing -Z (toward bowl). Then heading = PI (facing -Z). Let me place eating position at (2.6, 0, 3.2) facing -Z. Bowl at (2.6,0,2.6). Good distance 0.6.

Hideout house at (-2.8, 0, 3.0): box base + roof.

Let me add pellets in bowl: small orange spheres.

Now hamsters: 5 of them with different colors and roles.

Let me assign: hamster 0 and 1 wander/pause only. Hamster 2 sometimes eats. Hamster 3 sometimes rides wheel. Hamster 4 wanders and sometimes eats/wheel randomly.

Actually simpler: each hamster has probability to do special activities. Let me give each a "role" that biases behavior.

Let me just implement the full state machine generically and let randomness decide.

Let me write the Hamster class.

I'll store references: group, eyes (array), head group, legs (array of pivot groups), maxSpeed, etc.

Animation in update:
- If moving (speed > 0.01): legs animate, body bob.
- Idle: gentle breathing.
- Eating: head bob up/down.
- Riding: whole group vibrates slightly, legs pedaling.

Blinking: global random.

Let me write update(dt, time):

```
update(dt, time) {
  const m = this.group;
  this.stateTimer -= dt;
  
  switch(this.state) {
    case 'wander': {
      const dir = new THREE.Vector3(this.target.x - m.position.x, 0, this.target.z - m.position.z);
      const d = dir.length();
      if (d < 0.2) {
        this.state = 'pause'; this.stateTimer = 1.5 + Math.random()*3; this.speed = 0;
      } else {
        dir.normalize();
        m.position.x += dir.x * this.maxSpeed * dt;
        m.position.z += dir.z * this.maxSpeed * dt;
        this.heading = Math.atan2(dir.x, dir.z);
        m.rotation.y = this.heading;
        this.speed = this.maxSpeed;
        clampPos(m.position);
        if (Math.random() < 0.02) {
          this.heading += (Math.random()-0.5)*1.4;
          m.rotation.y = this.heading;
        }
      }
      break;
    }
    case 'pause': {
      this.speed = 0;
      if (this.stateTimer <= 0) {
        const r = Math.random();
        if (this.specialChance > 0 && r < this.specialChance) {
          if (r < this.specialChance*0.5) { this.gotoWheel(); }
          else { this.gotoEat(); }
        } else {
          this.target = randomPoint();
          this.state = 'wander'; this.stateTimer = 4 + Math.random()*5;
        }
      }
      break;
    }
    case 'goto_wheel': {
      // move to riding spot
      const tx = wheelX, tz = wheelZ;
      const dir = new THREE.Vector3(tx - m.position.x, 0, tz - m.position.z);
      const d = dir.length();
      if (d < 0.3) {
        this.state = 'ride_wheel'; this.stateTimer = 4 + Math.random()*3;
        m.position.set(wheelX, ridingY, wheelZ);
        this.heading = 0; m.rotation.y = 0;
        this.onWheel = true;
      } else {
        dir.normalize();
        m.position.x += dir.x*this.maxSpeed*dt;
        m.position.z += dir.z*this.maxSpeed*dt;
        this.heading = Math.atan2(dir.x, dir.z);
        m.rotation.y = this.heading;
        this.speed = this.maxSpeed;
      }
      break;
    }
    case 'ride_wheel': {
      this.speed = this.maxSpeed*0.8;
      this.wheelSpin += this.maxSpeed*0.8*dt*3;
      if (this.stateTimer <= 0) {
        this.state = 'pause'; this.stateTimer = 2 + Math.random()*3;
        this.onWheel = false;
        // move away from wheel
        this.target = randomPoint();
      }
      break;
    }
    case 'goto_eat': {
      const dir = new THREE.Vector3(eatBowl.x - m.position.x, 0, eatBowl.z - m.position.z);
      const d = dir.length();
      if (d < 0.3) {
        this.state = 'eat'; this.stateTimer = 3 + Math.random()*2;
        m.position.set(eatPos.x, 0, eatPos.z);
        this.heading = Math.atan2(eatBowl.x - eatPos.x, eatBowl.z - eatPos.z);
        m.rotation.y = this.heading;
      } else {
        dir.normalize();
        m.position.x += dir.x*this.maxSpeed*dt;
        m.position.z += dir.z*this.maxSpeed*dt;
        this.heading = Math.atan2(dir.x, dir.z);
        m.rotation.y = this.heading;
        this.speed = this.maxSpeed;
      }
      break;
    }
    case 'eat': {
      this.speed = 0;
      if (this.stateTimer <= 0) {
        this.state = 'pause'; this.stateTimer = 2 + Math.random()*3;
        this.target = randomPoint();
      }
      break;
    }
  }
  
  // animation
  this.animate(time, dt);
}
```

For goto_eat, eatPos = (2.6, 0, 3.2), eatBowl = (2.6,0,2.6). heading = atan2(0, -0.6) = atan2(0,-0.6) = PI. Facing -Z. Good.

clampPos keeps within [-3.6, 3.6] maybe, but wheel and house occupy space; fine.

randomPoint: within [-3.6,3.6] but avoid wheel area? Not necessary.

animate:
```
animate(time) {
  const g = this.group;
  const moving = this.speed > 0.02;
  // legs
  if (this.legs) {
    const spd = moving ? 12 : 0;
    for (let i=0;i<this.legs.length;i++){
      const phase = i%2===0 ? 0 : Math.PI;
      this.legs[i].rotation.x = moving ? Math.sin(time*spd + phase)*0.7 : Math.sin(time*1.5+phase)*0.05;
    }
  }
  // body bob
  const bob = moving ? Math.abs(Math.sin(time*12))*0.03 : Math.sin(time*2)*0.015;
  g.position.y = (this.onWheel? ridingY : 0) + bob;
  // head / eating
  if (this.state==='eat') {
    this.head.position.y = 0.95 + Math.abs(Math.sin(time*8))*0.08;
    this.head.rotation.x = Math.sin(time*8)*0.2;
  } else if (this.state==='ride_wheel') {
    this.head.position.y = 0.95 + Math.sin(time*14)*0.02;
    this.head.rotation.x = -0.2;
  } else {
    this.head.position.y = 0.95 + Math.sin(time*2)*0.015;
    this.head.rotation.x = 0;
  }
  // blink
  this.blinkTimer -= 0.016;
  if (this.blinkTimer <= 0) {
    this.blinkTimer = 2 + Math.random()*4;
    this.blinkStart = time; this.blink = true;
  }
  if (this.blink) {
    const t = time - this.blinkStart;
    if (t < 0.12) { for (const e of this.eyes) e.scale.y = 0.1; }
    else if (t < 0.24) { for (const e of this.eyes) e.scale.y = 1; this.blink=false; }
  }
}
```

Wait g.position.y set each frame overrides the base y. But when riding, base is ridingY. When on floor, base 0. But I also add bob. Good. But during goto states the y should be 0. Fine.

Hold on, I set g.position.y in animate, but I also set m.position.y? No, I only set x,z in movement. Good. But for ride_wheel I set position.set(wheelX, ridingY, wheelZ) once, then animate adds bob. Good.

Blink timing uses 0.016 decrement — better to pass dt. Let me pass dt to animate or compute blinkTimer -= dt. Let me pass dt.

Let me restructure: update(dt, time) calls animate(dt, time).

Now eyes blink set scale.y on both eyes.

Let me make sure eyes are children of head so scaling works in head local space; fine.

Now buildHamster returns { group, head, eyes, legs }.

Let me define positions.

Head group local: position (0, 0.95, 0.18). Actually let me put head at (0, 0.95, 0.15). Eyes at (±0.17, 0.02, 0.34) relative to head (front is +Z). Wait head sphere radius 0.4, front at z=0.4+0.15=0.55 from group origin. Eyes at head-local z=0.32, x ±0.16, y 0.0. Ears at head-local (±0.16, 0.22, -0.05). Nose at head-local (0, -0.06, 0.38). Cheeks at (±0.22, -0.05, 0.22).

Let me just code it.

Eyes material dark; add small white highlight maybe. Keep simple.

Let me finalize buildHamster:

```js
function buildHamster(furColor, bellyColor) {
  const g = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color: furColor, flatShading: true, roughness: 0.95 });
  const bellyMat = new THREE.MeshStandardMaterial({ color: bellyColor, flatShading: true, roughness: 0.95 });
  const footMat = new THREE.MeshStandardMaterial({ color: 0xf0bcb0, flatShading: true, roughness: 0.9 });
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x1a1210, flatShading: true, roughness: 0.5 });
  const pinkMat = new THREE.MeshStandardMaterial({ color: 0xff9aa2, flatShading: true, roughness: 0.7 });

  // body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 14, 12), fur);
  body.scale.set(1, 0.92, 1.18);
  body.position.y = 0.55;
  body.castShadow = true; body.receiveShadow = true;
  g.add(body);
  // belly
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.44, 12, 10), bellyMat);
  belly.scale.set(1, 0.9, 1.15);
  belly.position.set(0, 0.5, 0.16);
  g.add(belly);
  // tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 6), pinkMat);
  tail.position.set(0, 0.5, -0.62);
  g.add(tail);

  // head
  const head = new THREE.Group();
  head.position.set(0, 0.95, 0.15);
  const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.4, 14, 12), fur);
  headMesh.scale.set(1, 0.95, 1.0);
  headMesh.castShadow = true;
  head.add(headMesh);
  // ears
  for (const sx of [-1,1]) {
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.13, 10, 8), fur);
    ear.scale.set(1, 1, 0.6);
    ear.position.set(sx*0.18, 0.34, -0.02);
    head.add(ear);
    const inner = new THREE.Mesh(new THREE.SphereGeometry(0.075, 8, 6), pinkMat);
    inner.scale.set(1, 1, 0.5);
    inner.position.set(sx*0.18, 0.34, 0.01);
    head.add(inner);
  }
  // eyes
  const eyes = [];
  for (const sx of [-1,1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.075, 10, 8), darkMat);
    eye.position.set(sx*0.17, 0.02, 0.33);
    head.add(eye); eyes.push(eye);
    const hl = new THREE.Mesh(new THREE.SphereGeometry(0.025, 6, 6), new THREE.MeshStandardMaterial({color:0xffffff, flatShading:true}));
    hl.position.set(sx*0.17 + 0.02, 0.05, 0.37);
    head.add(hl);
  }
  // nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 6), pinkMat);
  nose.position.set(0, -0.06, 0.4);
  head.add(nose);
  // cheeks
  for (const sx of [-1,1]) {
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.11, 10, 8), bellyMat);
    cheek.position.set(sx*0.24, -0.06, 0.2);
    head.add(cheek);
  }
  g.add(head);

  // legs
  const legs = [];
  const legPos = [ [-0.28, 0, 0.32], [0.28, 0, 0.32], [-0.28, 0, -0.32], [0.28, 0, -0.32] ];
  for (const p of legPos) {
    const pivot = new THREE.Group();
    pivot.position.set(p[0], 0.2, p[2]);
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.1, 0.26, 8), footMat);
    leg.position.y = -0.13;
    leg.castShadow = true;
    const foot = new THREE.Mesh(new THREE.SphereGeometry(0.11, 8, 6), footMat);
    foot.scale.set(1, 0.55, 1.3);
    foot.position.y = -0.27;
    pivot.add(leg, foot);
    g.add(pivot); legs.push(pivot);
  }

  return { group: g, head, eyes, legs };
}
```

Note leg pivot at y=0.2 (hip), leg extends down to ~0.0 (bottom). Good, feet touch floor at y~0.

Now instantiate hamsters with random colors and roles.

Let me set up hamsters array.

```js
const hamsters = [];
const roles = ['wander','wander','eater','rider','mixer'];
const palette = [
  [0xd9a56b, 0xf5e1c8],
  [0x8c6a4f, 0xe8d3b0],
  [0xcfc0b0, 0xfaf3e6],
  [0xf0e6d8, 0xffffff],
  [0xe8b58a, 0xfbe9d0],
];
for (let i=0;i<5;i++){
  const b = buildHamster(palette[i][0], palette[i][1]);
  scene.add(b.group);
  const h = {
    group: b.group, head: b.head, eyes: b.eyes, legs: b.legs,
    state: 'wander',
    target: randomPoint(),
    heading: Math.random()*Math.PI*2,
    maxSpeed: 0.9 + Math.random()*0.5,
    speed: 0,
    stateTimer: Math.random()*3,
    specialChance: roles[i]==='wander'?0 : roles[i]==='eater'?0.06 : roles[i]==='rider'?0.06 : 0.05,
    onWheel: false,
    wheelSpin: 0,
    blinkTimer: Math.random()*4,
    blinkStart:0, blink:false,
    role: roles[i],
  };
  b.group.position.copy(h.target);
  b.group.rotation.y = h.heading;
  hamsters.push(h);
}
```

randomPoint within [-3.6,3.6] but maybe avoid exact wheel/bowl. I'll allow overlap; hamsters will navigate anyway.

Now the wheel spin: accumulate hamster wheelSpin contributions. Let me compute total riding count and spin wheel accordingly in main loop:

```js
let ridingCount = 0;
hamsters.forEach(h => { if (h.state==='ride_wheel') ridingCount++; });
wheelSpinGroup.rotation.x += (0.5 + ridingCount*3) * dt;
```

Good.

Main loop:
```js
const clock = new THREE.Clock();
function animate() {
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;
  for (const h of hamsters) h.update(dt, time);
  // wheel spin
  let rc = 0; hamsters.forEach(h=>{ if (h.state==='ride_wheel') rc++; });
  wheelSpinGroup.rotation.x += (0.4 + rc*3.5)*dt;
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();
```

Wait, h.update already increments h.wheelSpin but I'm not using it. Let me remove h.wheelSpin usage and just count. Actually I used wheelSpin in ride_wheel state earlier; let me drop that and rely on counting. Remove wheelSpin.

clampPos:
```js
const BOUND = 3.7;
function clampPos(v){
  if (v.x > BOUND) v.x = BOUND; if (v.x < -BOUND) v.x = -BOUND;
  if (v.z > BOUND) v.z = BOUND; if (v.z < -BOUND) v.z = -BOUND;
}
```

randomPoint:
```js
function randomPoint(){
  return new THREE.Vector3((Math.random()-0.5)*7.4, 0, (Math.random()-0.5)*7.4);
}
```

eat positions:
```js
const eatBowl = new THREE.Vector3(2.6, 0, 2.6);
const eatPos = new THREE.Vector3(2.6, 0, 3.25);
```

Now goto_eat uses eatBowl and eatPos.

Let me double check heading for eat: from eatPos (2.6,3.25) to bowl (2.6,2.6): dir = (0, -0.65). atan2(0, -0.65) = PI. Facing -Z. Good, hamster faces bowl.

goto_wheel uses wheelX, wheelZ. ridingY = 0.18.

Let me set constants:
```js
const wheelX = -3.4, wheelZ = 0, wheelCY = 1.2, wheelR = 1.05, ridingY = 0.18;
```

Now hideout house and food bowl creation.

Food bowl:
```js
const bowlGroup = new THREE.Group();
const bowlMat = new THREE.MeshStandardMaterial({ color: 0x4fc3f7, flatShading: true, roughness: 0.6 });
const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.4, 0.22, 16, 1, true), bowlMat);
bowl.position.y = 0.11;
bowl.castShadow = true;
const bowlBottom = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 0.02, 16), bowlMat);
bowlBottom.position.y = 0.01;
bowlGroup.add(bowl, bowlBottom);
// pellets
const pelletMat = new THREE.MeshStandardMaterial({ color: 0xf4b740, flatShading: true, roughness: 0.8 });
for (let i=0;i<10;i++){
  const p = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), pelletMat);
  const a = Math.random()*Math.PI*2, r = Math.random()*0.35;
  p.position.set(Math.cos(a)*r, 0.16 + Math.random()*0.05, Math.sin(a)*r);
  bowlGroup.add(p);
}
bowlGroup.position.set(2.6, 0, 2.6);
scene.add(bowlGroup);
```

House:
```js
const house = new THREE.Group();
const wallMat2 = new THREE.MeshStandardMaterial({ color: 0xffcc80, flatShading: true, roughness: 0.85 });
const roofMat = new THREE.MeshStandardMaterial({ color: 0xff7043, flatShading: true, roughness: 0.8 });
const houseBody = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.9, 1.2), wallMat2);
houseBody.position.y = 0.45;
houseBody.castShadow = true; houseBody.receiveShadow = true;
house.add(houseBody);
const roof = new THREE.Mesh(new THREE.ConeGeometry(1.0, 0.7, 4), roofMat);
roof.position.y = 1.25;
roof.rotation.y = Math.PI/4;
roof.castShadow = true;
house.add(roof);
// door
const door = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.5, 12, 1, true), new THREE.MeshStandardMaterial({color:0x5d4037, side:THREE.DoubleSide, flatShading:true}));
door.position.set(0, 0.35, 0.61);
door.rotation.x = Math.PI/2;
house.add(door);
house.position.set(-2.8, 0, 3.0);
house.rotation.y = 0.4;
scene.add(house);
```

Wheel building finalized:
```js
const wheelGroup = new THREE.Group();
const spinGroup = new THREE.Group();
wheelGroup.add(spinGroup);
const rimMat = new THREE.MeshStandardMaterial({ color: 0xff8fb3, flatShading: true, roughness: 0.5, metalness: 0.05 });
const rim = new THREE.Mesh(new THREE.TorusGeometry(wheelR, 0.07, 10, 28), rimMat);
spinGroup.add(rim);
const barMat = new THREE.MeshStandardMaterial({ color: 0xffc1d6, flatShading: true, roughness: 0.6 });
for (let i=0;i<6;i++){
  const a = (i/6)*Math.PI*2;
  const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.045,0.045, wheelR*2, 8), barMat);
  spoke.rotation.z = a;
  spoke.position.set(Math.cos(a)*wheelR*0.5, Math.sin(a)*wheelR*0.5, 0);
  spinGroup.add(spoke);
}
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,1.4,10), barMat);
axle.rotation.z = Math.PI/2;
spinGroup.add(axle);
const standMat = new THREE.MeshStandardMaterial({ color: 0x9ad4ff, flatShading: true, roughness: 0.7 });
for (const sx of [-0.72, 0.72]) {
  const post = new THREE.Mesh(new THREE.CylinderGeometry(0.09,0.09,2.2,12), standMat);
  post.position.set(wheelX + sx, 1.1, wheelZ);
  post.castShadow = true;
  wheelGroup.add(post);
}
const topBar = new THREE.Mesh(new THREE.BoxGeometry(1.5,0.14,0.14), standMat);
topBar.position.set(wheelX, 2.15, wheelZ);
wheelGroup.add(topBar);
scene.add(wheelGroup);
```

Wait, spoke orientation: Cylinder default along Y. Setting rotation.z = a rotates it so it lies in YZ plane radially. Position at midpoint. Length = wheelR*2 so spans diameter. That works: spoke from -wheelR to +wheelR along the rotated Y axis. Good. But position at (cos*a*R*0.5, sin*a*R*0.5) places center at mid-radius; combined with length 2R it spans from center outward 2R total => from -R to +R around center. Good, covers full diameter.

Axle rotation.z = PI/2 makes cylinder along X. Good, length 1.4 along X.

Posts at X = wheelX ± 0.72, height 2.2 from y=0 to 2.2. Top bar at y 2.15 connects them. Axle at y 1.2 rests between posts—fine visually.

Now, everything placed. Let me also add a couple of decorative items: maybe a small water bottle or a bone toy. Keep minimal—I'll add a tiny toy (a ball) that a hamster might chase? The requirement says one interactive object; wheel qualifies. I'll keep wheel + food bowl + house as scenery. Good enough.

Let me add a subtle grass/decoration? No.

Let me also add a soft shadow-catching floor? The floor receives shadows. Good.

Now finalize and also hide loading div after first frame.

Let me also make sure OrbitControls target is good and camera initial position nice.

Let me set camera position (7, 6.5, 8).

Add resize handler.

Let me write final HTML.

I realize I should double-check the import map approach works with unpkg three 0.160. OrbitControls addon path: https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js. Yes.

Let me finalize.

Also I want to make sure the hamsters look cute and the scene stable. Let me add a slight emissive to eyes? No.

Let me also give hamsters tiny smile? Skip.

Let me also add that when a hamster pauses, it might "sniff" (rotate). Minor.

I think it's good. Let me write the complete file cleanly.

Let me reconsider the special chance logic: In pause state, when timer expires, if random < specialChance, do special. With specialChance 0.06 and pause durations 1.5-5s, and after special they pause again 2-5s. Over time they'll occasionally do specials. Good.

But note after a special (eat/wheel) I set state='pause' with stateTimer 2-5 and target=randomPoint (for eat) or nothing (for wheel). For wheel I set target=randomPoint() too so it wanders away. Good.

Wait in ride_wheel completion I set state='pause', stateTimer, and target=randomPoint(). Good. In eat completion I set state='pause', stateTimer, target=randomPoint(). Good.

Edge: initial state 'wander' with target random and stateTimer random 0-3. Fine.

Let me ensure the hamsters start on floor (y=0) not inside objects. randomPoint within ±3.7 could place one inside house/wheel/bowl. Minor; they'll move out. Acceptable. Could nudge but skip.

Let me finalize the code and present.

Actually, let me reduce hamsters to 4 to keep it clean and clearly readable, plus maybe a fifth. The prompt says "several". 5 is good. Let me keep 5.

Let me also add a title badge and maybe show counts. The HUD is enough.

Let me write final.

One more: I should ensure flatShading gives low-poly look—yes spheres with low segments.

Let me also set environment for nicer shading? Not needed.

Let me write the final HTML now.

I'll also add a gentle ambient particle? No.

Let me finalize.

Double check: In animate(), I call h.update(dt, time) and h.animate(dt, time). Let me combine into update. I'll keep animate inside update.

Let me also make blinking use dt.

Let me write the update method fully including animation.

Also, I realize when a hamster is riding the wheel, its group position.y is set to ridingY (0.18) and animate adds bob. But in ride_wheel state I don't reset position; it was set when entering. Good. During ride, animate sets g.position.y = ridingY + bob. Good.

When leaving wheel to pause, next frames animate sets g.position.y = 0 + bob (since onWheel false). But the hamster is at ridingY position (inside wheel). It will then move (goto_walk) toward randomPoint, moving away. Good, but initially it's inside the wheel; it'll walk out. Fine.

Actually when entering ride_wheel I set position to (wheelX, ridingY, wheelZ) which is inside the wheel bottom. When it leaves, it starts there and walks away. Good.

Let me finalize.

Let me also ensure the head group's local y offset works: head at (0,0.95,0.15) within group. When group.position.y changes, head moves with it. Good.

Write it out.

Let me also add window.addEventListener('resize').

Final code below.

I'll also wrap in try/catch? Not needed.

Let me produce the final answer with the full index.html.

Let me make sure to remove the leftover `this.wheelSpin` references. In ride_wheel I won't set wheelSpin. Good.

Also remove unused variables.

Let me write clean.

Also I want the loading overlay to disappear. I'll set document.getElementById('loading').style.display='none' after first render.

Let me finalize.

Let me reconsider colors for background vs fog matching: background 0xfde9d0, fog same. Good.

Now produce final.

I'll present the code with brief explanation.

Let me write the complete file text.

Actually, let me reconsider the wheel spokes geometry once more. Torus radius wheelR=1.05 tube 0.07. Spokes length 2*wheelR = 2.1, positioned at mid-radius offset. With 6 spokes at 60°, they form a star. Good.

Axle length 1.4 along X fits between posts at ±0.72. Good.

Alright, finalize.

Let me also add a subtle "food bowl interactive" note: when hamster eats, pellets don't disappear (keep simple). Fine.

Write final answer.

Let me also double check hemisphere light color combos and that shadows visible. Directional light casts shadow; floor receives. Hamsters cast shadows. Good.

Also set renderer.shadowMap for receiver: objects receiveShadow true for floor, hamsters castShadow true. House cast shadow. Good.

Final code.

I'll write it all out now in the answer.

Let me make the HUD nice and add a footer hint.

Done. Writing.

Let me reconsider camera far and fog: fog distance 20, far 100. Good.

Also min polar angle clamp 0.49*PI prevents going under floor. Good.

Write final answer with the full code.

I'll include comments for clarity.

Let me produce it.
</think>

# Low-Poly Hamster Playground

Here's a complete, single-file project. Just save it as `index.html` and open it in any modern browser — no build step needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Low-Poly Hamster Playground 🐹</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #fde9d0; font-family: 'Segoe UI', system-ui, sans-serif; }
  #app { width: 100%; height: 100%; display: block; }
  #hud {
    position: fixed; top: 16px; left: 16px; z-index: 10;
    background: rgba(255, 255, 255, 0.82); backdrop-filter: blur(6px);
    padding: 14px 18px; border-radius: 16px;
    box-shadow: 0 8px 24px rgba(90, 58, 42, 0.18);
    color: #5a3a2a; max-width: 300px;
  }
  #hud h1 { font-size: 18px; margin-bottom: 6px; }
  #hud p { font-size: 12.5px; line-height: 1.55; opacity: 0.9; }
  #hud .dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; vertical-align:middle; }
  #loading {
    position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
    background: #fde9d0; color: #5a3a2a; font-size: 20px; z-index: 20;
    transition: opacity .5s; letter-spacing: .5px;
  }
</style>
</head>
<body>
  <div id="loading">🐹 Loading the hamsters…</div>
  <div id="hud">
    <h1>🐹 Low-Poly Hamster Playground</h1>
    <p><span class="dot" style="background:#ff8fb3"></span>Drag to rotate · Scroll to zoom · Right-drag to pan</p>
    <p>The little guys wander, pause &amp; sniff, take turns eating at the food bowl, and exercise on the wheel!</p>
  </div>
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

  /* ============================================================
     RENDERER / CAMERA / CONTROLS
  ============================================================ */
  const app = document.getElementById('app');
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  app.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xfde9d0);
  scene.fog = new THREE.Fog(0xfde9d0, 14, 30);

  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(7.5, 7, 8.5);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.target.set(0, 0.5, 0);
  controls.minDistance = 4;
  controls.maxDistance = 20;
  controls.maxPolarAngle = Math.PI * 0.49;   // keep camera above the floor
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.6;

  /* ============================================================
     LIGHTS
  ============================================================ */
  scene.add(new THREE.HemisphereLight(0xbfd9ff, 0x6b4a30, 0.75));
  scene.add(new THREE.AmbientLight(0xffffff, 0.45));
  const sun = new THREE.DirectionalLight(0xfff4e0, 1.35);
  sun.position.set(7, 12, 6);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.near = 1; sun.shadow.camera.far = 40;
  sun.shadow.camera.left = -14; sun.shadow.camera.right = 14;
  sun.shadow.camera.top = 14; sun.shadow.camera.bottom = -14;
  sun.shadow.bias = -0.0004;
  scene.add(sun);
  scene.add(new THREE.PointLight(0xffd9a0, 0.4, 32));

  /* ============================================================
     CAGE / TRAY
  ============================================================ */
  const tray = new THREE.Group();
  scene.add(tray);

  const floorMat = new THREE.MeshStandardMaterial({ color: 0xf3c98b, flatShading: true, roughness: 0.98 });
  const floor = new THREE.Mesh(new THREE.BoxGeometry(10.4, 0.4, 10.4), floorMat);
  floor.position.y = -0.2; floor.receiveShadow = true;
  tray.add(floor);

  const wallMat = new THREE.MeshStandardMaterial({ color: 0xbfe3f5, flatShading: true, roughness: 0.7, transparent: true, opacity: 0.5 });
  const wallH = 0.9, wallT = 0.3;
  const wallDefs = [
    { s: [10.6, wallH, wallT], p: [0, wallH/2, 5.3] },
    { s: [10.6, wallH, wallT], p: [0, wallH/2, -5.3] },
    { s: [wallT, wallH, 10.6], p: [5.3, wallH/2, 0] },
    { s: [wallT, wallH, 10.6], p: [-5.3, wallH/2, 0] },
  ];
  for (const w of wallDefs) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(...w.s), wallMat);
    m.position.set(...w.p); m.castShadow = true; tray.add(m);
  }

  // bedding flakes
  const beddingColors = [0xf5e1b8, 0xe8c98a, 0xf0d9b0, 0xdcc08a, 0xf7ecc8];
  for (let i = 0; i < 130; i++) {
    const b = new THREE.Mesh(
      new THREE.BoxGeometry(0.16 + Math.random()*0.16, 0.07 + Math.random()*0.07, 0.16 + Math.random()*0.16),
      new THREE.MeshStandardMaterial({ color: beddingColors[Math.floor(Math.random()*beddingColors.length)], flatShading: true, roughness: 1 })
    );
    b.position.set((Math.random()-0.5)*9.6, 0.05 + Math.random()*0.05, (Math.random()-0.5)*9.6);
    b.rotation.y = Math.random()*Math.PI;
    b.receiveShadow = true;
    tray.add(b);
  }

  /* ============================================================
     INTERACTIVE OBJECT: EXERCISE WHEEL
  ============================================================ */
  const wheelX = -3.4, wheelZ = 0, wheelCY = 1.2, wheelR = 1.05, ridingY = 0.22;
  const wheelGroup = new THREE.Group();
  const spinGroup = new THREE.Group();
  wheelGroup.add(spinGroup);

  const rimMat = new THREE.MeshStandardMaterial({ color: 0xff8fb3, flatShading: true, roughness: 0.5, metalness: 0.05 });
  spinGroup.add(new THREE.Mesh(new THREE.TorusGeometry(wheelR, 0.07, 10, 28), rimMat));

  const barMat = new THREE.MeshStandardMaterial({ color: 0xffc1d6, flatShading: true, roughness: 0.6 });
  for (let i = 0; i < 6; i++) {
    const a = (i/6) * Math.PI * 2;
    const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, wheelR*2, 8), barMat);
    spoke.rotation.z = a;
    spoke.position.set(Math.cos(a)*wheelR*0.5, Math.sin(a)*wheelR*0.5, 0);
    spinGroup.add(spoke);
  }
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.4, 10), barMat);
  axle.rotation.z = Math.PI/2;
  spinGroup.add(axle);

  const standMat = new THREE.MeshStandardMaterial({ color: 0x9ad4ff, flatShading: true, roughness: 0.7 });
  for (const sx of [-0.72, 0.72]) {
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 2.2, 12), standMat);
    post.position.set(wheelX + sx, 1.1, wheelZ); post.castShadow = true;
    wheelGroup.add(post);
  }
  const topBar = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.14, 0.14), standMat);
  topBar.position.set(wheelX, 2.15, wheelZ);
  wheelGroup.add(topBar);
  scene.add(wheelGroup);

  /* ============================================================
     FOOD BOWL (interactive)
  ============================================================ */
  const eatBowl = new THREE.Vector3(2.6, 0, 2.6);
  const eatPos  = new THREE.Vector3(2.6, 0, 3.28);
  const bowlGroup = new THREE.Group();
  const bowlMat = new THREE.MeshStandardMaterial({ color: 0x4fc3f7, flatShading: true, roughness: 0.6 });
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.4, 0.22, 16, 1, true), bowlMat);
  bowl.position.y = 0.11; bowl.castShadow = true;
  const bowlBottom = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 0.02, 16), bowlMat);
  bowlBottom.position.y = 0.01;
  bowlGroup.add(bowl, bowlBottom);
  const pelletMat = new THREE.MeshStandardMaterial({ color: 0xf4b740, flatShading: true, roughness: 0.8 });
  for (let i = 0; i < 11; i++) {
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), pelletMat);
    const a = Math.random()*Math.PI*2, r = Math.random()*0.34;
    p.position.set(Math.cos(a)*r, 0.16 + Math.random()*0.05, Math.sin(a)*r);
    bowlGroup.add(p);
  }
  bowlGroup.position.copy(eatBowl);
  scene.add(bowlGroup);

  /* ============================================================
     LITTLE HOUSE (scenery)
  ============================================================ */
  const house = new THREE.Group();
  const wallMat2 = new THREE.MeshStandardMaterial({ color: 0xffcc80, flatShading: true, roughness: 0.85 });
  const roofMat  = new THREE.MeshStandardMaterial({ color: 0xff7043, flatShading: true, roughness: 0.8 });
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.9, 1.2), wallMat2);
  body.position.y = 0.45; body.castShadow = true; body.receiveShadow = true;
  house.add(body);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(1.0, 0.7, 4), roofMat);
  roof.position.y = 1.25; roof.rotation.y = Math.PI/4; roof.castShadow = true;
  house.add(roof);
  const door = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.5, 12, 1, true),
    new THREE.MeshStandardMaterial({ color: 0x5d4037, side: THREE.DoubleSide, flatShading: true }));
  door.rotation.x = Math.PI/2; door.position.set(0, 0.35, 0.61);
  house.add(door);
  house.position.set(-2.8, 0, 3.0); house.rotation.y = 0.4;
  scene.add(house);

  /* ============================================================
     HAMSTER BUILDER
  ============================================================ */
  function buildHamster(furColor, bellyColor) {
    const g = new THREE.Group();
    const fur      = new THREE.MeshStandardMaterial({ color: furColor, flatShading: true, roughness: 0.95 });
    const bellyMat = new THREE.MeshStandardMaterial({ color: bellyColor, flatShading: true, roughness: 0.95 });
    const footMat  = new THREE.MeshStandardMaterial({ color: 0xf0bcb0, flatShading: true, roughness: 0.9 });
    const darkMat  = new THREE.MeshStandardMaterial({ color: 0x1a1210, flatShading: true, roughness: 0.5 });
    const pinkMat  = new THREE.MeshStandardMaterial({ color: 0xff9aa2, flatShading: true, roughness: 0.7 });
    const shineMat = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });

    // body
    const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 14, 12), fur);
    body.scale.set(1, 0.92, 1.18); body.position.y = 0.55;
    body.castShadow = true; body.receiveShadow = true; g.add(body);
    const belly = new THREE.Mesh(new THREE.SphereGeometry(0.44, 12, 10), bellyMat);
    belly.scale.set(1, 0.9, 1.15); belly.position.set(0, 0.5, 0.16); g.add(belly);
    const tail = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 6), pinkMat);
    tail.position.set(0, 0.5, -0.62); g.add(tail);

    // head
    const head = new THREE.Group();
    head.position.set(0, 0.95, 0.15);
    const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.4, 14, 12), fur);
    headMesh.scale.set(1, 0.95, 1.0); headMesh.castShadow = true; head.add(headMesh);
    for (const sx of [-1, 1]) {
      const ear = new THREE.Mesh(new THREE.SphereGeometry(0.13, 10, 8), fur);
      ear.scale.set(1, 1, 0.6); ear.position.set(sx*0.18, 0.34, -0.02); head.add(ear);
      const inner = new THREE.Mesh(new THREE.SphereGeometry(0.075, 8, 6), pinkMat);
      inner.scale.set(1, 1, 0.5); inner.position.set(sx*0.18, 0.34, 0.01); head.add(inner);
    }
    const eyes = [];
    for (const sx of [-1, 1]) {
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.075, 10, 8), darkMat);
      eye.position.set(sx*0.17, 0.02, 0.33); head.add(eye); eyes.push(eye);
      const hl = new THREE.Mesh(new THREE.SphereGeometry(0.025, 6, 6), shineMat);
      hl.position.set(sx*0.17 + 0.02, 0.05, 0.37); head.add(hl);
    }
    const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 6), pinkMat);
    nose.position.set(0, -0.06, 0.4); head.add(nose);
    for (const sx of [-1, 1]) {
      const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.11, 10, 8), bellyMat);
      cheek.position.set(sx*0.24, -0.06, 0.2); head.add(cheek);
    }
    g.add(head);

    // legs
    const legs = [];
    const legPos = [[-0.28,0,0.32],[0.28,0,0.32],[-0.28,0,-0.32],[0.28,0,-0.32]];
    for (const p of legPos) {
      const pivot = new THREE.Group();
      pivot.position.set(p[0], 0.2, p[2]);
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.1, 0.26, 8), footMat);
      leg.position.y = -0.13; leg.castShadow = true;
      const foot = new THREE.Mesh(new THREE.SphereGeometry(0.11, 8, 6), footMat);
      foot.scale.set(1, 0.55, 1.3); foot.position.y = -0.27;
      pivot.add(leg, foot); g.add(pivot); legs.push(pivot);
    }

    return { group: g, head, eyes, legs };
  }

  /* ============================================================
     HAMSTERS WITH AUTONOMOUS BEHAVIOR
  ============================================================ */
  const BOUND = 3.7;
  const randomPoint = () => new THREE.Vector3((Math.random()-0.5)*7.4, 0, (Math.random()-0.5)*7.4);
  const clampPos = v => {
    if (v.x >  BOUND) v.x =  BOUND; if (v.x < -BOUND) v.x = -BOUND;
    if (v.z >  BOUND) v.z =  BOUND; if (v.z < -BOUND) v.z = -BOUND;
  };

  const palette = [
    [0xd9a56b, 0xf5e1c8], // classic tan
    [0x8c6a4f, 0xe8d3b0], // brown
    [0xcfc0b0, 0xfaf3e6], // gray
    [0xf0e6d8, 0xffffff], // snow
    [0xe8b58a, 0xfbe9d0], // ginger
  ];
  const roles = ['wander', 'wander', 'eater', 'rider', 'mixer'];

  const hamsters = [];
  for (let i = 0; i < 5; i++) {
    const b = buildHamster(palette[i][0], palette[i][1]);
    scene.add(b.group);
    const start = randomPoint();
    const h = {
      group: b.group, head: b.head, eyes: b.eyes, legs: b.legs,
      state: 'wander',
      target: start.clone(),
      heading: Math.random()*Math.PI*2,
      maxSpeed: 0.85 + Math.random()*0.5,
      speed: 0,
      stateTimer: Math.random()*3,
      specialChance: roles[i] === 'wander' ? 0 : 0.06,
      onWheel: false,
      blinkTimer: Math.random()*4, blinkStart: 0, blink: false,
    };
    b.group.position.copy(start);
    b.group.rotation.y = h.heading;
    hamsters.push(h);
  }

  const setState = (h, state, timer) => { h.state = state; h.stateTimer = timer; };

  /* ============================================================
     MAIN LOOP
  ============================================================ */
  const clock = new THREE.Clock();

  function updateHamster(h, dt, time) {
    const m = h.group;
    h.stateTimer -= dt;

    switch (h.state) {
      case 'wander': {
        const dir = new THREE.Vector3(m.position.x - h.target.x, 0, m.position.z - h.target.z);
        const d = dir.length();
        if (d < 0.22) {
          setState(h, 'pause', 1.5 + Math.random()*3); h.speed = 0;
        } else {
          dir.normalize();
          m.position.x += dir.x * h.maxSpeed * dt;
          m.position.z += dir.z * h.maxSpeed * dt;
          h.heading = Math.atan2(dir.x, dir.z);
          m.rotation.y = h.heading;
          h.speed = h.maxSpeed;
          clampPos(m.position);
          if (Math.random() < 0.02) {           // occasional random turn
            h.heading += (Math.random() - 0.5) * 1.4;
            m.rotation.y = h.heading;
          }
        }
        break;
      }
      case 'pause': {
        h.speed = 0;
        if (h.stateTimer <= 0) {
          const r = Math.random();
          if (h.specialChance > 0 && r < h.specialChance) {
            if (r < h.specialChance * 0.55) { setState(h, 'goto_wheel', 6); }
            else {                            setState(h, 'goto_eat', 4); }
          } else {
            h.target = randomPoint(); setState(h, 'wander', 4 + Math.random()*5);
          }
        }
        break;
      }
      case 'goto_wheel': {
        const dir = new THREE.Vector3(wheelX - m.position.x, 0, wheelZ - m.position.z);
        if (dir.length() < 0.32) {
          setState(h, 'ride_wheel', 4 + Math.random()*3);
          m.position.set(wheelX, ridingY, wheelZ);
          h.heading = 0; m.rotation.y = 0; h.onWheel = true;
        } else {
          dir.normalize();
          m.position.x += dir.x * h.maxSpeed * dt;
          m.position.z += dir.z * h.maxSpeed * dt;
          h.heading = Math.atan2(dir.x, dir.z); m.rotation.y = h.heading;
          h.speed = h.maxSpeed;
        }
        break;
      }
      case 'ride_wheel': {
        h.speed = h.maxSpeed * 0.8;
        if (h.stateTimer <= 0) {
          setState(h, 'pause', 2 + Math.random()*3);
          h.onWheel = false; h.target = randomPoint();
        }
        break;
      }
      case 'goto_eat': {
        const dir = new THREE.Vector3(eatBowl.x - m.position.x, 0, eatBowl.z - m.position.z);
        if (dir.length() < 0.32) {
          setState(h, 'eat', 3 + Math.random()*2);
          m.position.copy(eatPos);
          h.heading = Math.atan2(eatBowl.x - eatPos.x, eatBowl.z - eatPos.z);
          m.rotation.y = h.heading;
        } else {
          dir.normalize();
          m.position.x += dir.x * h.maxSpeed * dt;
          m.position.z += dir.z * h.maxSpeed * dt;
          h.heading = Math.atan2(dir.x, dir.z); m.rotation.y = h.heading;
          h.speed = h.maxSpeed;
        }
        break;
      }
      case 'eat': {
        h.speed = 0;
        if (h.stateTimer <= 0) { setState(h, 'pause', 2 + Math.random()*3); h.target = randomPoint(); }
        break;
      }
    }

    // ---- animation ----
    const moving = h.speed > 0.02;
    if (h.legs) {
      const spd = moving ? 13 : 0;
      for (let i = 0; i < h.legs.length; i++) {
        const phase = i % 2 === 0 ? 0 : Math.PI;
        h.legs[i].rotation.x = moving ? Math.sin(time*spd + phase) * 0.7 : Math.sin(time*1.6 + phase) * 0.05;
      }
    }
    const bob = moving ? Math.abs(Math.sin(time*13)) * 0.03 : Math.sin(time*2) * 0.015;
    h.group.position.y = (h.onWheel ? ridingY : 0) + bob;

    if (h.state === 'eat') {
      h.head.position.y = 0.95 + Math.abs(Math.sin(time*9)) * 0.08;
      h.head.rotation.x = Math.sin(time*9) * 0.22;
    } else if (h.state === 'ride_wheel') {
      h.head.position.y = 0.95 + Math.sin(time*15) * 0.02;
      h.head.rotation.x = -0.2;
    } else {
      h.head.position.y = 0.95 + Math.sin(time*2) * 0.015;
      h.head.rotation.x = 0;
    }

    // blink
    h.blinkTimer -= dt;
    if (h.blinkTimer <= 0) { h.blinkTimer = 2.5 + Math.random()*4; h.blinkStart = time; h.blink = true; }
    if (h.blink) {
      const t = time - h.blinkStart;
      for (const e of h.eyes) e.scale.y = (t < 0.12) ? 0.1 : (t < 0.26 ? 1 : 1);
      if (t >= 0.26) h.blink = false;
    }
  }

  function tick() {
    const dt = Math.min(clock.getDelta(), 0.05);
    const time = clock.elapsedTime;

    for (const h of hamsters) updateHamster(h, dt, time);

    // spin the wheel faster while hamsters ride it
    let riders = 0;
    for (const h of hamsters) if (h.state === 'ride_wheel') riders++;
    spinGroup.rotation.x += (0.45 + riders * 3.6) * dt;

    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(tick);
  }

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  document.getElementById('loading').style.opacity = '0';
  setTimeout(() => document.getElementById('loading').remove(), 600);
  tick();
  </script>
</body>
</html>
```

## What's inside

**Scene contents**
- **Cage/tray** — wooden floor tray with low translucent acrylic walls and ~130 scattered bedding flakes.
- **5 low-poly hamsters** — built from primitives (spheres, cylinders, cones) in distinct color schemes (tan, brown, gray, snow, ginger), with ears, blinking eyes, pink nose/cheeks/feet, a tail, and animated four legs.
- **Interactive exercise wheel** — a pink torus wheel with spokes, axle, and blue supports that **spins faster whenever a hamster rides it**.
- **Food bowl** with pellets + a little cozy house for flavor.

**Autonomous behavior (state machines)**
Each hamster wanders to a random spot, pauses to sniff, randomly decides to either **walk to the wheel and ride it** (spinning the wheel) or **walk to the food bowl and eat** (bobbing its head), then resumes wandering. Every hamster also blinks and breathes idly.

**Controls**
- Drag = rotate · Scroll = zoom · Right-drag = pan
- Slow auto-rotate so you can just watch

It runs instantly in any modern browser — no install, no build. Just open the file. 🐹