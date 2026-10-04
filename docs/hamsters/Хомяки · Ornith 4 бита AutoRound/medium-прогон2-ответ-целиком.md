Let me create a single-file HTML project with Three.js that shows a low-poly hamster playground. Let me think about what I need:

1. Three.js library (I'll use CDN)
2. A 3D scene with:
   - A cage (walls made of transparent or wireframe material)
   - A floor/tray
   - Several low-poly hamsters
   - One interactive object (wheel, tunnel, food bowl, or toy)
3. Hamsters with autonomous behavior (walking, pausing, turning, interacting with objects)
4. Cute, low-poly, colorful, funny visual style
5. Camera controls (orbit controls)
6. Run immediately in a browser

Let me build this step by step.

For the hamsters, I'll create them from basic geometries (spheres, boxes, cylinders) to make them low-poly and cute. Each hamster will have:
- Body (sphere/icosahedron for low-poly look)
- Ears
- Eyes
- Nose
- Legs
- Tail

For behavior, I'll implement a simple state machine:
- WALKING: moving around randomly
- PAUSING: standing still
- TURNING: changing direction
- INTERACTING: going to an object (like the food bowl) and interacting

Let me write the code.

I'll use OrbitControls from Three.js CDN.

Let me structure the hamster creation carefully so they look cute. Low-poly means using icosahedron or low-segment spheres.

Let me write this out:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #f5e6d3; font-family: 'Comic Sans MS', cursive, sans-serif; }
  #app { width: 100%; height: 100%; }
  #ui {
    position: fixed; top: 16px; left: 16px; z-index: 10;
    background: rgba(255,255,255,0.85);
    padding: 12px 18px; border-radius: 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    color: #5a4632; font-size: 14px; max-width: 260px;
  }
  #ui h1 { font-size: 18px; margin-bottom: 6px; }
  #ui p { font-size: 12px; line-height: 1.5; opacity: 0.85; }
  #loading {
    position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
    background: #f5e6d3; color: #5a4632; font-family: inherit; font-size: 20px; z-index: 20;
  }
</style>
</head>
<body>
<div id="loading">Preparing hamsters... 🐹</div>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate • Scroll to zoom • Watch the little buddies explore!</p>
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

Now let me fill in the actual Three.js code.

Scene setup:
- Renderer
- Camera
- Controls
- Lights
- Cage
- Floor
- Hamsters
- Interactive object (exercise wheel)
- Animation loop

Let me think about the cage dimensions. Say the tray is 12 x 8 (x, z), and walls are tall.

Let me define the play area bounds so hamsters stay inside.

Let me create the hamster builder function. Each hamster:
- Group
- Body: IcosahedronGeometry with low detail (for low-poly look). Maybe scale it to be oval.
- Head: smaller sphere attached to front
- Two ears: small spheres
- Two eyes: white spheres with black pupils
- Nose: small pink cone/sphere
- Cheeks: small spheres
- 4 legs: small cylinders
- Tail: tiny sphere

Actually, let me keep it manageable but cute. Let me combine body and head into the main shape but add features.

Let me define colors for each hamster - cute pastel colors.

Behavior state machine per hamster:
- state: 'wander' | 'pause' | 'interact'
- target position when wandering
- timer for current state

Let me implement:

```js
class Hamster {
  constructor(color, name) {
    this.mesh = buildHamster(color);
    this.name = name;
    this.state = 'wander';
    this.timer = Math.random() * 3;
    this.speed = 0.6 + Math.random() * 0.4;
    this.target = randomPointInArea();
    this.pauseDuration = 2 + Math.random() * 3;
    this.yaw = Math.random() * Math.PI * 2;
    this.bobPhase = Math.random() * Math.PI * 2;
    this.mesh.position.set(randomRange(-5, 5), 0.4, randomRange(-3, 3));
    // set initial facing toward target
  }
}
```

Let me think about the interaction with the wheel. When a hamster decides to interact, it walks to the wheel position and then spins the wheel / rides it briefly.

Actually let me make the food bowl the interactive object since it's simpler, OR the wheel. Let me do the wheel since it's more fun to watch. Actually, let me do a food bowl where hamsters go eat, plus maybe a wheel. But requirement says "one interactive object such as a wheel, tunnel, food bowl, or toy." So one is enough. Let me do the exercise wheel — it's iconic for hamsters and fun to watch spin.

Let me make hamsters occasionally walk to the wheel and ride it for a few seconds, during which the wheel spins.

Let me now write the full code.

For low-poly look, I'll use `flatShading: true` on materials.

Let me define the play area:
- Half-width X: 5.5
- Half-depth Z: 3.5

Cage dimensions: tray floor at y=0, walls up to y=3.

Let me build the cage:
- Tray: a flat box (thin) with slightly raised edges, colored like wood shavings or plastic.
- Walls: 4 transparent panels (glass/acrylic look) with frames. Or wireframe. Let me do semi-transparent panels with a light tint, plus frame edges.

Let me make it look nice.

Floor bedding: scatter some small cones/cylinders to look like wood shavings? That might be too much. Let me just do a textured-ish floor with a warm color and maybe a few scattered bedding pieces.

Let me keep it clean: floor is a flat plane with wood-shavings color, maybe with a subtle noise via many small low-poly shapes. Actually let me add a handful of bedding flakes as small boxes for texture.

Let me write the hamster building function carefully.

```js
function buildHamster(mainColor) {
  const g = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: mainColor, flatShading: true, roughness: 0.9 });
  
  // Body
  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 1), bodyMat);
  body.scale.set(1, 0.9, 1.15);
  body.position.y = 0.55;
  g.add(body);
  
  // Belly (lighter)
  const bellyMat = new THREE.MeshStandardMaterial({ color: 0xfff3e0, flatShading: true, roughness: 0.9 });
  const belly = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 1), bellyMat);
  belly.scale.set(0.9, 0.85, 1.1);
  belly.position.set(0, 0.5, 0.12);
  g.add(belly);
  
  // Head
  const headMat = new THREE.MeshStandardMaterial({ color: mainColor, flatShading: true, roughness: 0.9 });
  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.4, 1), headMat);
  head.position.set(0, 0.85, 0.35);
  g.add(head);
  
  // Ears
  const earMat = new THREE.MeshStandardMaterial({ color: mainColor, flatShading: true, roughness: 0.9 });
  const earGeo = new THREE.SphereGeometry(0.14, 6, 5);
  const earL = new THREE.Mesh(earGeo, earMat);
  earL.position.set(-0.22, 1.15, 0.32);
  const earR = earL.clone();
  earR.position.x = 0.22;
  g.add(earL, earR);
  
  // Cheeks
  const cheekMat = new THREE.MeshStandardMaterial({ color: 0xffc0cb, flatShading: true, roughness: 0.9 });
  const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.13, 6, 5), cheekMat);
  cheekL.position.set(-0.25, 0.78, 0.45);
  const cheekR = cheekL.clone();
  cheekR.position.x = 0.25;
  g.add(cheekL, cheekR);
  
  // Eyes
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.3, metalness: 0.1 });
  const eyeGeo = new THREE.SphereGeometry(0.075, 8, 6);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(-0.16, 0.92, 0.62);
  const eyeR = eyeL.clone();
  eyeR.position.x = 0.16;
  g.add(eyeL, eyeR);
  
  // Eye shine
  const shineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const shineGeo = new THREE.SphereGeometry(0.025, 6, 4);
  const shineL = new THREE.Mesh(shineGeo, shineMat);
  shineL.position.set(-0.14, 0.95, 0.66);
  const shineR = shineL.clone();
  shineR.position.x = 0.18;
  g.add(shineL, shineR);
  
  // Nose
  const noseMat = new THREE.MeshStandardMaterial({ color: 0xff8fab, flatShading: true, roughness: 0.8 });
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), noseMat);
  nose.position.set(0, 0.82, 0.72);
  g.add(nose);
  
  // Legs (4)
  const legMat = new THREE.MeshStandardMaterial({ color: 0xffc0cb, flatShading: true, roughness: 0.9 });
  const legGeo = new THREE.CylinderGeometry(0.07, 0.08, 0.18, 6);
  const legPositions = [
    [-0.3, 0.09, 0.25], [0.3, 0.09, 0.25],
    [-0.3, 0.09, -0.25], [0.3, 0.09, -0.25]
  ];
  const legs = legPositions.map(p => {
    const leg = new THREE.Mesh(legGeo, legMat);
    leg.position.set(...p);
    return leg;
  });
  legs.forEach(l => g.add(l));
  
  // Tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 5), bellyMat);
  tail.position.set(0, 0.55, -0.6);
  g.add(tail);
  
  return g;
}
```

Now the hamster needs references to its legs for walking animation and body for bobbing. Let me store references.

Actually let me restructure to store references on the hamster object so I can animate.

Let me make buildHamster return the group plus I'll attach named children so I can find them. Or better, return an object with references.

Let me refactor:

```js
function buildHamster(mainColor) {
  const g = new THREE.Group();
  const parts = {};
  // ... build everything
  parts.body = body;
  parts.head = head;
  parts.legs = [leg0, leg1, leg2, leg3];
  // ...
  return g;
}
```

Then in animation I access `hamster.group.parts.legs`.

Hmm, attaching to group as property is fine: `g.parts = parts`.

Let me now design the behavior update:

```js
update(dt) {
  this.timer -= dt;
  switch(this.state) {
    case 'wander':
      // move toward target
      const dx = this.target.x - this.mesh.position.x;
      const dz = this.target.z - this.mesh.position.z;
      const dist = Math.hypot(dx, dz);
      if (dist < 0.2 || this.timer <= 0) {
        // pick new target or pause
        if (Math.random() < 0.35) {
          this.state = 'pause';
          this.timer = this.pauseDuration;
        } else if (Math.random() < 0.15) {
          this.state = 'interact';
          this.timer = 4;
        } else {
          this.target = randomPoint();
          this.timer = 3 + Math.random() * 3;
        }
      } else {
        // move
        const step = this.speed * dt;
        this.mesh.position.x += (dx/dist) * step;
        this.mesh.position.z += (dz/dist) * step;
        // face direction of movement
        this.yaw = Math.atan2(dx, dz);
        this.mesh.rotation.y = this.yaw;
        // walk animation
        this.walkAnim += dt * 10;
      }
      break;
    case 'pause':
      this.timer -= dt; // already decremented at top? 
      // idle bob
      break;
    case 'interact':
      // move to wheel
      ...
      break;
  }
}
```

Wait, I decrement timer at the top for all states, which handles pause and interact durations too. Good.

Let me refine the interaction:

```js
case 'interact':
  const wheelPos = wheel.position;
  const wdx = wheelPos.x - this.mesh.position.x;
  const wdz = wheelPos.z - this.mesh.position.z;
  const wdist = Math.hypot(wdx, wdz);
  if (wdist > 0.3) {
    const step = this.speed * 1.3 * dt;
    this.mesh.position.x += (wdx/wdist) * step;
    this.mesh.position.z += (wdz/wdist) * step;
    this.yaw = Math.atan2(wdx, wdz);
    this.mesh.rotation.y = this.yaw;
    this.walkAnim += dt * 12;
  } else {
    // arrived at wheel - ride it
    this.riding = true;
    this.ridingTime += dt;
    // orient toward wheel side
    // spin wheel handled in main loop based on riders
    if (this.ridingTime > 3) {
      this.state = 'wander';
      this.timer = 1;
      // move away a bit
      this.riding = false;
      this.target = randomPointAwayFromWheel();
    }
  }
```

I need to track ridingTime separately. Let me add this.ridingTime = 0 reset when entering interact state.

For the wheel spinning, I'll track number of hamsters currently riding and spin the wheel proportionally.

Let me now think about the wheel geometry:
- A ring (torus) vertical, mounted on an axle/frame.
- Rungs across it for hamster to climb.

```js
const wheel = new THREE.Group();
const rimMat = new THREE.MeshStandardMaterial({ color: 0xffd93d, flatShading: true, roughness: 0.6 });
const rim = new THREE.Mesh(new THREE.TorusGeometry(0.9, 0.08, 8, 24), rimMat);
wheel.add(rim);
// rungs
for (let i = 0; i < 12; i++) {
  const angle = (i/12) * Math.PI * 2;
  const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.7, 6), rimMat);
  rung.position.set(Math.cos(angle)*0, Math.sin(angle)*0 ...);
  // Actually rungs connect the two rims
}
```

Hmm, a proper wheel has two rims connected by rungs/spokes. Let me simplify: one rim (torus) plus spokes/rungs radiating from center hub. For a hamster wheel, rungs along the circumference work. Let me do:
- Outer torus rim
- Center hub (small cylinder)
- Spokes connecting hub to rim (radial bars)

Actually the classic hamster wheel has rungs that are tangential (along the circle) so the hamster's feet rest on them. Let me place short cylinders tangent to the circle at each point.

Let me just make spokes as lines from center to rim and also a couple concentric rings. It'll look wheel-like enough.

Simpler approach: 
- Torus for outer rim (two of them offset in x for thickness)
- Cross bars (rungs) connecting them

Let me do:
- Two torus rims at x = ±0.06
- Rungs: cylinders oriented along x-axis, positioned around the circle, connecting the two rims.

Each rung: CylinderGeometry with length ~0.12 (the x-gap), radius 0.03, rotated so its length is along x. Position at (0, cos*radius, sin*radius)? Wait, the wheel is in the YZ plane (vertical, facing along X). So points on the circle are at (0, r*cosθ, r*sinθ). A rung connects (-0.06, y, z) to (0.06, y, z), so it's a cylinder along X positioned at (0, r*cosθ, r*sinθ).

Good.

- Axle: cylinder along X at center.
- Stand: two vertical supports + a base foot.

Let me place the wheel at one side of the cage.

Now the interactive object: the wheel. Hamsters ride it.

Let me also add a food bowl as decoration (not interactive) and maybe a small tunnel (torus lying horizontally) for visual interest. Keep it simple though. Requirement only needs one interactive object. I'll add the wheel as interactive, plus a food bowl and a tunnel as decorative props for cuteness.

Actually, let me not overcomplicate. Wheel (interactive) + food bowl (decoration) + a couple bedding flakes. Maybe a small tunnel tube for fun. Let me include the wheel, food bowl, and a tunnel — all low-poly, colorful.

Let me now also handle camera: OrbitControls with damping, target at center.

Lighting: ambient + directional (with shadows) + hemisphere for soft light. Add a soft background color.

Shadows: enable renderer.shadowMap. Directional light casts shadows. But shadows on transparent cage walls might look odd. Let me put the floor to receive shadows and keep it simple. Actually to keep performance and stability, maybe skip shadows or enable lightly. Shadows make it look nicer. Let me enable shadowMap for directional light onto the floor.

Let me set up:
- AmbientLight soft white
- HemisphereLight for ambient fill
- DirectionalLight casting shadows, positioned up and to the side

Floor receives shadow, hamsters cast shadows. Cage walls don't need to.

Let me finalize the code and make sure it runs.

Let me consider the hamster scale and cage scale. Cage inner play area roughly x: ±5, z: ±3.5, wall height 2.8. Hamsters are ~1 unit tall (body radius 0.55 + head). At scale that's fine relative to cage.

Wait, hamster body radius 0.55 means diameter 1.1, plus legs below. Height ~1.2. Cage height 2.8. Fine.

Play area for hamsters: keep within x: ±4.5, z: ±3 (inside walls which are at ±5, ±3.5).

Let me write randomPoint to respect bounds with margin.

Now let me also add subtle idle animation even when paused: gentle bobbing and blinking (scale eyes occasionally). Blinking is a nice touch: periodically scale eyes to 0 in Y quickly.

Let me add blink logic: random chance each frame or timer.

Let me keep blink simple: each hamster has blinkTimer; when it hits 0, do a quick blink (close eyes by scaling Y) over ~0.15s.

Let me write a helper for bobbing: `mesh.position.y = baseY + Math.abs(sin(phase)) * 0.05` while walking.

OK let me now write the complete file.

Let me also add a subtle ground pattern and maybe some scattered "food pellets" as small colorful spheres near the food bowl for fun. And wood shaving bits.

I'll keep the number of hamsters to 4 for clarity and performance.

Let me assign cute names and colors:
1. Biscuit - tan/orange (#e8a876)
2. Mochi - white/cream (#fff5ee)
3. Pebbles - gray (#b8b8c0)
4. Nugget - pink (#ffb3c6)

Let me code it all.

One more thing: I should make sure importmap works and the module script loads. Use unpkg three 0.160.0.

Let me write final code.

For the walking animation, I'll oscillate legs. Each leg gets a phase. leg.rotation.x = sin(phase) * 0.5 for front/back pairs.

Let me set leg pivot: legs are cylinders centered at their position; rotating around X will swing them. Since they're positioned at y=0.09 (near bottom), rotating around X moves the foot. Good enough.

Let me define legs array with positions and animate.

Let me write the update for walking bob:
```
this.bobPhase += dt * this.speed * 8;
const bob = Math.abs(Math.sin(this.bobPhase)) * 0.06;
group.position.y = baseY + bob;
// legs
this.parts.legs.forEach((leg, i) => {
  const dir = i < 2 ? 1 : -1;
  leg.rotation.x = dir * Math.sin(this.bobPhase + (i%2)*Math.PI) * 0.6;
});
// head slight bob
this.parts.head.rotation.z = Math.sin(this.bobPhase*0.5)*0.05;
```

baseY: I'll store hamster.baseY = 0 (ground) and add body squish. Actually the group position y should be ~0 (feet on ground). The body is already positioned up within the group. So group.position.y = bob. Good. baseY = 0.

When riding wheel, position hamster on the inner bottom of the wheel and rotate group to follow wheel rotation? That's complex. Simpler: when riding, place hamster at bottom inside the wheel, and just spin the wheel fast; hamster bobs a bit. Orientation: face the wheel.

Let me compute riding position: wheel in YZ plane at x = wheelX. Inside bottom is at (wheelX, radius - rungRadius, 0) relative to wheel center. Hamster stands there facing X direction (toward viewer or away). Let me face it along +X or -X. I'll set hamster group position to wheel position + (0, r*0.9, 0) and rotation.y = PI/2 (facing along X). And gently bounce.

Let me store wheel radius r = 0.9. Riding y offset ~ r - 0.15 = 0.75 above wheel center. Plus hamster height. Fine.

Let me finalize.

Also I want to make the wheel spin continuously when ridden, and idle slowly maybe.

Let me track riders count. In animation loop:
```
let riders = hamsters.filter(h => h.state === 'interact' && h.riding).length;
const targetSpin = riders * 4; // rad/sec when riding
wheelSpin += (targetSpin - wheel.angularVelocity) ... 
```
Actually simpler: set wheel.angularVelocity = riders > 0 ? 3.5 : Math.max(0, wheel.angularVelocity - dt*0.5). Then wheel.rotation.x += wheel.angularVelocity * dt. Add friction so it slows when no rider.

But if multiple ride, faster. Fine.

Let me set wheelSpin variable and update:
```
const target = riders * 3.2;
wheel.angularVelocity = wheel.angularVelocity + (target - wheel.angularVelocity) * Math.min(1, dt*3);
wheel.rotation.x += wheel.angularVelocity * dt;
```

Good.

Now let me make sure hamster riding orientation: the wheel rotates around X axis, so the inner surface moves in Z and Y. Hamster at bottom inside grabs rungs. Facing along X is fine (sideways to wheel). Actually a hamster on a wheel faces sideways (along the axle). So rotation.y = ±PI/2. Let me set based on which side... just pick +PI/2 consistently, or alternate. I'll face them so they look "forward" - set rotation.y = Math.PI/2.

Hmm but then their belly faces the hub. Fine, it's cute enough.

Let me also handle: when a hamster arrives at wheel to ride, set its position to the riding spot directly (teleport a little) then ride. To avoid popping, I'll lerp position toward riding spot.

Let me set when entering interact state, target = riding position. Then in interact update, move toward it; once close, set state riding (still 'interact' but flag riding=true and lock position at riding spot).

Let me code interact update:
```
case 'interact':
  if (!this.riding) {
    // move to wheel edge
    const toX = wheelX + Math.sign(...) ...
  }
```

Simplify: target riding point = (wheelX, wheelCenterY + r*0.85, 0). Move toward it. When within 0.3, set riding=true, snap position to riding point, set rotation.y = PI/2.

But the wheel center is at some height. Let me place wheel so its center is at y = 1.0 (so bottom rim at y=0.1, touching near floor). Then riding point = (wheelX, 1.0 + 0.76, 0) = y ~1.76. Hamster standing there at feet ~1.6. OK within cage (wall 2.8). Fine.

Actually let me place wheel center higher, say y=1.1, with a stand/base so it looks like it's on the bedding. Bottom rim at y=0.2. Riding point y = 1.1 + 0.76 = 1.86. Hmm that's high. Let me lower center to y=0.95, bottom rim ~0.25. Riding point y = 0.95+0.76 = 1.71. Fine.

Let me set wheel center y = 0.95, radius 0.9 → bottom rim at 0.05 (basically touching floor). Good.

Stand: two vertical posts at (wheelX ± ?, ...) hmm the wheel is in YZ plane; the stand should hold the axle along X. So posts at (wheelX - 0.15, ...) and (wheelX + 0.15, ...) supporting the axle ends. And a base foot on the floor. Let me make an L-stand: a vertical post from floor up to axle height at x = wheelX + 0.2 (one side), and a horizontal arm to the axle, plus a base slab. Simpler: one support post on one side plus a triangular arm. Let me just do:
- Post: box from floor to center height at (wheelX + 0.25, center/2, 0) — along x offset.
- Arm: box from post top to axle center.
- Foot: box on floor at post base.

Color the stand a contrasting color (teal or purple).

Place wheel at x = -3.5 (left side of cage), z = 0. So it's against a wall but accessible.

Wait, if wheel is at x=-3.5 and half-cage is 5, there's room. Hamsters walk from x=-3.5 outward. Good. But hamsters riding need space below/around. Fine.

Actually let me place wheel at x = -3.2, z = 1. Somewhat off-center so scene isn't symmetrical.

Food bowl at x = 3.2, z = -1. Tunnel somewhere center-ish, e.g., x=0.5, z=1.5 as a decorative tube.

Let me now also add name labels? Could add floating text sprites but that's extra. I'll skip labels to keep stable; maybe add a subtle tooltip on hover? Not necessary. Skip.

Let me write everything out now.

Let me reconsider hamster count: 4 is good. Let me maybe do 5 for liveliness. I'll do 4 to keep it clean and performant. Actually 5 gives more life. Let me do 5.

Colors:
- #f2b08a (peach)
- #f7e7d4 (cream)
- #c9c9d4 (lavender gray)
- #ffb3c6 (pink)
- #b5d8a0 (mint)

Names: Biscuit, Mochi, Pebble, Rosie, Avocado. Eh, keep names internal for potential debug.

Let me write the code fully now.

I'll also add a nice gradient-ish background using a large sphere or just a solid color with fog. Use scene.background = new THREE.Color(0xfce4c9) and maybe a gradient sky via a big inverted sphere with vertex colors. Let me keep solid color + fog for simplicity and stability. Add hemisphere light for warmth.

Let me add ambient occlusion-ish by having a soft ground.

Alright, writing final.

Let me make sure to remove the loading div after first frame or on load. I'll hide it after a short delay / on first render.

Let me also guard: if module fails to load (no internet), show error. But assume internet present.

Let me write the update for wander target picking with bounds:
```
function randomPoint(marginX=4.5, marginZ=2.8) {
  return {
    x: rand(-marginX, marginX),
    z: rand(-marginZ, marginZ)
  };
}
```

Now hamsters shouldn't overlap too much but that's okay for chaos.

Let me finalize the walking: ensure they turn smoothly. Setting rotation.y to yaw directly is fine (instant turn) but smoothing is nicer. I'll lerp rotation toward target yaw.

```
this.mesh.rotation.y = lerpAngle(this.mesh.rotation.y, this.yaw, Math.min(1, dt*5));
```

Actually direct assignment is fine and stable. I'll lerp for smoothness.

Let me write lerpAngle handling wraparound. Or just use THREE.MathUtils.lerp on rotation.y if changes are small. Movement direction changes could cause big jumps (e.g., from 0 to 2π). To avoid, I'll keep yaw continuous by adjusting target minimally. Simpler: set rotation directly to atan2; occasional sharp turns are okay/funny. I'll do direct set but clamp. Let me just do direct set; it's fine and less buggy.

Hmm, but a sudden 360° flip looks bad. Let me lerp with shortest path.

```
function shortestYaw(cur, tgt) {
  let d = tgt - cur;
  while (d > Math.PI) d -= Math.PI*2;
  while (d < -Math.PI) d += Math.PI*2;
  return cur + d;
}
```
Then rotation.y = shortestYaw(current, target) with lerp factor. I'll store current rotation.y from mesh.rotation.y.

OK let me write it.

Let me also make hamsters occasionally do a little spin when pausing (funny). Optional. I'll add a small "look around" head tilt. Keep minimal.

Let me now write the full HTML.

I'll be careful with the module imports and structure.

Let me draft the complete script:

```js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const rand = (a,b) => a + Math.random()*(b-a);
const clamp = (v,a,b) => Math.max(a, Math.min(b, v));

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.getElementById('app').appendChild(renderer.domElement);

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xfce4c9);
scene.fog = new THREE.Fog(0xfce4c9, 14, 30);

// Camera
const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(0, 6, 11);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1, 0);
controls.maxPolarAngle = Math.PI * 0.49;
controls.minDistance = 5;
controls.maxDistance = 22;

// Lights
const hemi = new THREE.HemisphereLight(0xffffff, 0xffd9b0, 0.7);
scene.add(hemi);
const ambient = new THREE.AmbientLight(0xffffff, 0.35);
scene.add(ambient);
const sun = new THREE.DirectionalLight(0xfff3e0, 1.4);
sun.position.set(6, 12, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 40;
sun.shadow.camera.left = -12;
sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12;
sun.shadow.camera.bottom = -12;
sun.shadow.bias = -0.0004;
scene.add(sun);

// ... build cage, floor, props, hamsters
```

Floor:
```js
const trayW = 12, trayD = 9, trayH = 0.4;
const tray = new THREE.Mesh(new THREE.BoxGeometry(trayW, trayH, trayD), new THREE.MeshStandardMaterial({ color: 0x9ad7ff, roughness: 0.9, flatShading: true }));
tray.position.y = trayH/2 - 0.0; // sits on ground
tray.receiveShadow = true;
scene.add(tray);
```

Hmm, let me define ground level. Let's say the tray top is at y=0 (bedding surface). The tray walls rise a bit. Let me make tray: a box representing the plastic tray, top surface at y=0.02. Actually let me make the bedding surface at y=0 and tray sides visible above.

Let me do:
- Base slab: BoxGeometry(trayW, 0.3, trayD) at y = -0.15 (below floor).
- Bedding surface: a thin plane/box at y = 0.02 (top of tray). Color wood shavings #e9c893.

Actually simpler: one box for tray from y=-0.3 to y=0.02, and a top surface slightly above at y=0.03 with bedding color. Let me just do:
- Tray body: box height 0.5 centered at y=-0.25, color light blue. receiveShadow.
- Bedding: thin box height 0.08 at y=0.02, color tan, on top.

Add some bedding flakes: scatter ~40 small boxes/cones on the bedding with random rotation and slight color variation.

Let me add flakes:
```js
const beddingMat = new THREE.MeshStandardMaterial({ color: 0xe9c893, flatShading: true, roughness: 1 });
for (let i=0;i<60;i++){
  const flake = new THREE.Mesh(new THREE.BoxGeometry(rand(0.15,0.35),0.05,rand(0.1,0.2)), beddingMat);
  flake.position.set(rand(-5.6,5.6), 0.06, rand(-4,4));
  flake.rotation.set(rand(0,Math.PI), rand(0,Math.PI), rand(0,Math.PI));
  scene.add(flake);
}
```

Cage walls:
```js
const wallH = 3, wallMat = new THREE.MeshPhysicalMaterial({ color: 0xd9f0ff, transmission: 0.85, transparent: true, opacity: 0.25, roughness: 0.2, thickness: 0.5, side: THREE.DoubleSide, depthWrite: false });
```
Hmm transmission requires proper setup; might be heavy. Let me use simple transparent material:
```js
const wallMat = new THREE.MeshStandardMaterial({ color: 0xbfeaff, transparent: true, opacity: 0.22, roughness: 0.5, metalness: 0, side: THREE.DoubleSide, depthWrite: false });
```
Four walls at x=±6, z=±4.5, height 3, thin (0.1). Add frame edges (lines or thin boxes) in a bright color for definition.

Let me add frame posts at corners (thin boxes) in a pastel color, and horizontal rails.

Let me place walls:
- Front/back walls at z = ±4.5, width 12, height 3, thickness 0.1.
- Side walls at x = ±6, width 9, height 3, thickness 0.1.

Add frame: vertical corner posts (boxes) and top rails.

Interactive wheel: as described.

Food bowl: a low cylinder (open top) with a few pellets inside.

Tunnel: a torus lying horizontally (axis along X) or a cylinder (tube) lying down. Let me do a torus lying so its plane is vertical? A hamster tunnel is a tube you crawl through. Represent as a torus lying flat (plane horizontal?) Hmm. Let me make it a short cylinder tube lying horizontally along Z, open ends, colored bright. Actually a "donut" tunnel: torus with large radius, lying in a vertical plane facing X (so hamster goes through along X). Radius 0.8, tube 0.15. Color striped. Place at center.

Let me keep the tunnel as a torus in the YZ plane (hole along X), positioned at y ~0.9 (raised on small legs) so hamsters could go through. Eh, simpler to leave it decorative on the floor as a low arch. Let me make it a half-torus arch (tunnel you walk under) — but that's complex. I'll just place a full torus lying flat on the floor like a ring toy, color it, and it's cute. Or a cylinder lying down.

Decision: Tunnel = a hollow cylinder (tube) lying horizontally along Z, like a short pipe, colored with stripes, placed on the bedding. Hamsters walk around/near it. Decorative.

Let me make it: CylinderGeometry(radius 0.6, 0.6, 2.2, 16, 1, true) open-ended, lying along Z (rotate so axis is Z). Actually CylinderGeometry axis is Y by default; to lie along Z rotate x by 90°. Add inner darkness? It's a shell; fine. Add stripe material with colors via segments? Just one color, maybe bright teal with a couple of ring accents.

Food bowl: CylinderGeometry open top, color coral, with pellets (small spheres) inside in random colors.

Let me now also add a small food pile near bowl: a cluster of colored spheres.

Alright. Let me also add a water bottle? Might be too much. Skip. Keep wheel, bowl, tunnel.

Now hamsters. Let me finalize buildHamster returning group with parts.

Let me write the animation of legs and bobbing.

Let me define Hamster class:

```js
class Hamster {
  constructor(color) {
    this.group = buildHamster(color);
    this.baseY = this.group.position.y;
    this.parts = this.group.userData.parts;
    this.state = 'wander';
    this.timer = rand(1, 4);
    this.pauseDuration = rand(2, 4.5);
    this.speed = rand(0.5, 0.9);
    this.target = randomPoint();
    this.yaw = rand(0, Math.PI*2);
    this.bobPhase = rand(0, Math.PI*2);
    this.riding = false;
    this.ridingTime = 0;
    this.blinkTimer = rand(2, 6);
    this.group.traverse(o => { if (o.isMesh){ o.castShadow = true; } });
    scene.add(this.group);
  }
  ...
}
```

Wait, buildHamster sets positions relative to group origin at y=0 (feet on ground). group.position.y starts 0. Good.

randomPoint returns within bounds.

Update method as designed.

Let me handle blink: 
```
this.blinkTimer -= dt;
if (this.blinkTimer <= 0) {
  this.blinkTimer = rand(2.5, 7);
  this.blinking = 0.15; // seconds of blink
}
if (this.blinking > 0) {
  this.blinking -= dt;
  const s = Math.abs(Math.sin((0.15 - this.blinking)/0.15 * Math.PI)) ; // quick close/open
  this.parts.eyeL.scale.y = clamp(1 - s, 0.05, 1);
  this.parts.eyeR.scale.y = this.parts.eyeL.scale.y;
} else {
  this.parts.eyeL.scale.y = 1;
  this.parts.eyeR.scale.y = 1;
}
```
Hmm the math: at start blink=0.15, we want eyes closed (scale 0). At end blink=0, eyes open (scale 1). Let t = (0.15 - blink)/0.15 goes 1→0. scale = 1 - sin(t*PI)? At t=1 sin(PI)=0 scale=1 (open) wrong. Let me use scale = sin(t*PI): at t=0 (start) sin0=0 closed; at t=1 sin(PI)=0 closed again. That blinks closed-open-closed. I want closed then open. Use scale = sin(t*PI) gives closed at both ends, middle open. That's a blink (quick). Actually a blink is quick close+open. Using sin(t*PI) with t 0→1: starts closed, opens at middle, closes again. That's a quick blink. 

Let me instead do a simpler one-shot: eyes scale from 1 to 0 to 1 over 0.15s using a triangle wave. Eh, sin is fine.

Let me set: when blinkTimer<=0, set blinkStart = time, mark blinkActive. Use elapsed = (time - blinkStart)/0.15 clamped 0..1. scale = sin(elapsed*PI). This makes eyes close then open. Good. I'll store blinkStart and use global clock time.

Let me track with a start time using performance.now or accumulate. I'll accumulate a clock in update: this.clock += dt. Store this.blinkStart. scale = sin(clamp((this.clock - this.blinkStart)/0.15,0,1) * PI).

Good.

Now let me write the whole thing and test mentally.

Let me also make sure to call controls.update() each frame.

Resize handler.

Let me write it all out now in the final answer.

Let me reconsider the wheel riding position and orientation. Wheel center at (wx, wy, wz) = (-3.2, 0.95, 1). Radius 0.9. Riding point on inner bottom: relative to center, bottom inner is (0, -(r - tubeRadius), 0)?? The hamster stands on the rungs inside near the bottom. Bottom of wheel is at wy - r = 0.05. Hamster feet there, center of hamster up ~1.7. So hamster group position = (wx, wy - r + 0.15 + 0.6, wz) ≈ (wx, 0.95-0.9+0.15+0.6 = 0.8, wz). Wait let me compute: bottom rung at y = wy - r = 0.05. Hamster standing on it, hamster center ~0.05 + 1.1 = 1.15. Let me set riding position y = wy - r + 1.1 = 0.95 - 0.9 + 1.1 = 1.15. And face along +X (rotation.y = PI/2) so they face the "direction of travel" on a wheel (sideways). Actually on a wheel the hamster faces sideways (along axle). So rotation.y = ±PI/2. Let me set PI/2.

When riding, also bob slightly: group.position.y = ridingY + sin(bobPhase)*0.03, and rotate the hamster group slightly to follow wheel? Not necessary. Just bob.

Also the hamster should be positioned at the bottom regardless of wheel rotation (since it stays at bottom while running). Good.

But wait—if hamster faces +X and wheel rotates, the hamster's feet are on rungs near bottom; as wheel spins the rungs move but hamster stays at bottom. Visually the hamster appears to run in place while wheel spins. 

Let me also make hamster lean a bit forward when riding: rotation.x = 0.1.

Now, arriving at wheel: target = riding position (wx, 1.15, wz). Move toward it; when within 0.4, set riding=true and snap to riding position, set facing.

But the hamster approaching from where? It'll walk up to the bottom of the wheel. Since wheel is at x=-3.2, hamsters approach from x > -3.2 (inside). They reach the bottom front of the wheel. Fine.

Let me set arrival threshold 0.5.

Let me code interact update:
```
case 'interact':
  if (!this.riding) {
    const dx = this.ridingPos.x - this.group.position.x;
    const dz = this.ridingPos.z - this.group.position.z;
    const d = Math.hypot(dx,dz);
    if (d > 0.5) {
      const step = this.speed*1.4*dt;
      this.group.position.x += dx/d*step;
      this.group.position.z += dz/d*step;
      this.yaw = Math.atan2(dx, dz);
      this.group.rotation.y = shortestYaw(this.group.rotation.y, this.yaw);
      this.bobPhase += dt*this.speed*12;
      this.animateLegs();
    } else {
      this.riding = true;
      this.ridingTime = 0;
      this.group.position.set(this.ridingPos.x, this.ridingPos.y, this.ridingPos.z);
      this.group.rotation.y = Math.PI/2;
      this.group.rotation.x = 0.12;
    }
  } else {
    this.ridingTime += dt;
    this.bobPhase += dt*14;
    this.group.position.y = this.ridingPos.y + Math.abs(Math.sin(this.bobPhase))*0.04;
    // spin handled globally
    if (this.ridingTime > randRide) { // fixed duration
      this.riding = false;
      this.state = 'wander';
      this.timer = rand(0.5,1.5);
      this.group.rotation.x = 0;
      this.ridingPos = null;
      this.target = randomPoint();
      // push away from wheel
      this.target.x = Math.max(this.target.x, -1);
    }
  }
```

I need this.ridingPos defined. Set when entering interact state.

Let me set ridingPos in constructor:
```
this.ridingPos = new THREE.Vector3(wheelX, 1.15, wheelZ);
```
But wheelX/Z constants—define before creating hamsters. Let me define WHEEL_X, WHEEL_Z, WHEEL_Y, WHEEL_R as constants.

Ride duration: fixed ~3s. Use this.rideDuration = rand(2.5, 4).

Now the global wheel spin uses count of riders.

Let me also make sure hamsters don't all go to the wheel at once too often. Probability when finishing wander: 0.25 interact, 0.4 pause, 0.35 new target. Good.

Let me finalize shortestYaw and lerp helpers.

animateLegs:
```
animateLegs() {
  const legs = this.parts.legs;
  for (let i=0;i<4;i++){
    const phase = this.bobPhase + (i<2?0:Math.PI);
    const side = (i%2===0)?1:-1;
    legs[i].rotation.x = side*Math.sin(phase)*0.7;
  }
}
```

Idle/pause: gentle body sway, no leg motion, maybe head turn.

Let me set state 'pause': timer counts down; do idle bob: group.position.y = baseY + sin(clock*2)*0.02; slight rotation.y drift. Also sniff (head bob). Keep simple.

Now let me write buildHamster with userData.parts containing references: body, head, earL, earR, cheekL, cheekR, eyeL, eyeR, nose, legs[], tail.

Let me write it.

Also, I realize flatShading on IcosahedronGeometry with detail 1 gives a nice low-poly look. Good.

Let me also give hamsters a subtle emissive? No, keep diffuse.

Let me now also add name tags as small floating canvas sprites above each hamster? That adds charm but also complexity and potential perf. I'll add simple ones using a canvas texture sprite, positioned above head, showing their name. Actually that could clutter. Let me add them but small and semi-transparent. Hmm, might reduce readability. I'll add subtle name labels; they help identify "several cute hamsters." Let me add them.

Creating a label sprite:
```
function makeLabel(text, color) {
  const canvas = document.createElement('canvas');
  canvas.width = 256; canvas.height = 64;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = 'rgba(255,255,255,0.85)';
  roundRect(ctx, 4, 4, 248, 56, 16); ctx.fill();
  ctx.strokeStyle = color; ctx.lineWidth = 4; ctx.stroke();
  ctx.fillStyle = '#5a4632';
  ctx.font = 'bold 30px Comic Sans MS, cursive';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text, 128, 32);
  const tex = new THREE.CanvasTexture(canvas);
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false });
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(1.6, 0.4, 1);
  return sprite;
}
```
Position above head at y ~1.5 relative to group. Add to group so it follows hamster. But sprite always faces camera (Sprite does). Good. Position y = 1.4.

But labels behind transparent walls still show (depthTest false). Fine.

Names: ['Biscuit','Mochi','Pebble','Rosie','Avocado'].

Let me include 5 hamsters.

Now, potential issue: labels inside cage behind walls — since walls are transparent, fine.

Let me finalize and write the file.

Let me double check imports: importmap maps 'three' and 'three/addons/'. OrbitControls at 'three/addons/controls/OrbitControls.js'. Good for three 0.160.

Let me write it all.

Also add window resize.

Let me also hide loading overlay once first render completes (requestAnimationFrame).

Let me produce final code.

One more: I want the hamsters to cast shadows and floor to receive. Tray top (bedding) receive shadow. Set receiveShadow on bedding surface and flakes maybe (too many). Just on tray body top and a separate receiving plane. Let me add a dedicated receiving plane (the bedding surface) with receiveShadow=true, and tray body also receiveShadow. Hamsters castShadow true.

Let me make bedding surface a mesh with receiveShadow.

Alright writing now.

Let me reconsider cage size vs hamster scale. Cage inner ~12 wide. Hamsters ~1 tall. 5 hamsters. Good density.

Wall positions: x=±6, z=±4.5, height 3. Play bounds for hamsters: x within ±5.4, z within ±3.9. Let me use marginX=5.2, marginZ=3.7.

Wheel at x=-3.2, z=1. Bowl at x=3.2, z=-1.2. Tunnel at x=0.6, z=1.6 (lying along Z).

Let me make sure wheel doesn't clip walls: x=-3.2, radius 0.9, near x=-4? walls at -6. Fine. z=1 within ±4.5. Good.

Tunnel along Z at x=0.6, from z=0.5 to z=2.7, radius 0.6, so spans z 0.5..2.7 within bounds. Good. Raise slightly on legs so hamsters can pass under: bottom at y~0.2, center at y=0.7. Legs: 2 small cylinders.

Food bowl at x=3.2, z=-1.2: a low cylinder outer radius 0.6, height 0.3, open top, color coral. Pellets inside: ~8 small spheres colors.

Let me write.

For the tunnel material stripes, I'll just use a single bright color (teal 0x4ecdc4) with a couple ring accents (small torus) at ends.

Let me finalize.

Actually, to keep it truly simple and stable, let me reduce decorative complexity: wheel (interactive), food bowl (with pellets), and one tunnel. That satisfies "cage, floor/tray, several hamsters, one interactive object" plus a couple decorations. Good.

Let me write the final HTML now. I'll be thorough.

Let me make sure to call controls.update() each frame.

Resize handler.

Let me write it all out now in the final answer.

Let me reconsider the wheel riding position and orientation once more and the global spin.

Global spin in animation loop:
```
let riders = 0;
hamsters.forEach(h => { if (h.state==='interact' && h.riding) riders++; });
const targetSpin = riders * 3.2;
wheel.angularVelocity = wheel.angularVelocity + (targetSpin - wheel.angularVelocity) * Math.min(1, dt*3);
wheel.rotation.x += wheel.angularVelocity * dt;
```
Initial angularVelocity 0. When no riders, it decays to 0. Good.

Now let me write buildHamster returning group with userData.parts.

Let me write final file.

I'll also add a gentle auto-rotate? No, user controls. Keep manual.

Let me write it.

Also ensure the hamster legs pivot correctly: cylinder centered at its position (0.09 y). Rotating around X by ±0.7 swings the ends. Since the cylinder is thin and centered, rotation swings it in a arc. Fine for walk cycle.

Let me finalize the code and output.

Let me write the complete index.html.

I'll include comments for clarity.

Let me make sure the code has no syntax errors. I'll write carefully.

Final structure:
- HTML head with styles
- loading div, ui div, app div
- importmap
- module script

Let me write.

For shortestYaw and lerp helpers.

Let me also clamp hamster positions to bounds in wander to be safe.

Let me write randomPoint:
```
function randomPoint(){
  return { x: rand(-5.2,5.2), z: rand(-3.7,3.7) };
}
```

In wander update, clamp position to bounds after moving.

Let me write the update method fully:

```
update(dt, clock) {
  this.clock = clock;
  this.timer -= dt;

  // blink
  this.updateBlink(dt);

  if (this.state === 'wander') {
    const dx = this.target.x - this.group.position.x;
    const dz = this.target.z - this.group.position.z;
    const d = Math.hypot(dx, dz);
    if (d < 0.25 || this.timer <= 0) {
      const r = Math.random();
      if (r < 0.34) { this.state='pause'; this.timer=this.pauseDuration; }
      else if (r < 0.54) { this.state='interact'; this.timer=4; this.riding=false; this.ridingTime=0; }
      else { this.target=randomPoint(); this.timer=rand(2.5,5); }
    } else {
      const step = this.speed*dt;
      this.group.position.x += (dx/d)*step;
      this.group.position.z += (dz/d)*step;
      this.group.position.x = clamp(this.group.position.x,-5.4,5.4);
      this.group.position.z = clamp(this.group.position.z,-3.9,3.9);
      this.yaw = Math.atan2(dx, dz);
      this.group.rotation.y = shortestYaw(this.group.rotation.y, this.yaw);
      this.bobPhase += dt*this.speed*10;
      this.animateLegs();
    }
  } else if (this.state === 'pause') {
    this.group.position.y = this.baseY + Math.sin(clock*2.2)*0.02;
    this.group.rotation.z = Math.sin(clock*1.5)*0.04;
    this.parts.head.rotation.z = Math.sin(clock*1.8)*0.08;
  } else if (this.state === 'interact') {
    if (!this.riding) {
      const dx = this.ridingPos.x - this.group.position.x;
      const dz = this.ridingPos.z - this.group.position.z;
      const d = Math.hypot(dx, dz);
      if (d > 0.5) {
        const step = this.speed*1.4*dt;
        this.group.position.x += (dx/d)*step;
        this.group.position.z += (dz/d)*step;
        this.group.position.x = clamp(this.group.position.x,-5.4,5.4);
        this.group.position.z = clamp(this.group.position.z,-3.9,3.9);
        this.yaw = Math.atan2(dx, dz);
        this.group.rotation.y = shortestYaw(this.group.rotation.y, this.yaw);
        this.bobPhase += dt*this.speed*12;
        this.animateLegs();
      } else {
        this.riding = true;
        this.ridingTime = 0;
        this.group.position.copy(this.ridingPos);
        this.group.rotation.y = Math.PI/2;
        this.group.rotation.x = 0.12;
      }
    } else {
      this.ridingTime += dt;
      this.bobPhase += dt*14;
      this.group.position.y = this.ridingPos.y + Math.abs(Math.sin(this.bobPhase))*0.04;
      if (this.ridingTime >= this.rideDuration) {
        this.riding = false;
        this.state = 'wander';
        this.timer = rand(0.5,1.5);
        this.group.rotation.x = 0;
        this.target = { x: Math.max(rand(-5.2,5.2), -1), z: rand(-3.7,3.7) };
      }
    }
  }
}
```

Wait, when state becomes 'interact' I set timer=4 but the timer keeps decrementing at top. During interact non-riding phase, timer continues to count down; if it hits 0 before reaching wheel (shouldn't if close enough) it would switch. Since interact is short, timer 4 is plenty. But the top decrement will reduce it; if hamster is far it might run out. Let me set timer high (e.g., 8) for interact to be safe, or ignore timer during interact. Let me just set this.timer = 8 when entering interact and treat interact's own timing separately. Actually simplest: when state==='interact', don't let the top timer switch states. I'll restructure: only apply timer-based transitions when state==='wander' or 'pause'. Let me guard.

Restructure:
```
this.timer -= dt;
this.updateBlink(dt);

if (this.state === 'interact') {
   ... handle interact fully (own timing) ...
   return;
}

if (this.state === 'wander') { ... uses this.timer ... }
else if (this.state === 'pause') { ... uses this.timer ... }
```

And when transitioning to interact, set this.riding=false etc. The timer value doesn't matter for interact. Good.

Let me rewrite with early return for interact.

Also for wander->interact transition, set this.ridingPos already defined in constructor. Good.

Let me also ensure when entering interact from wander, we don't also process timer switch. With early return, fine.

Let me also make pause->back to wander via timer.

Now updateBlink:
```
updateBlink(dt) {
  this.blinkTimer -= dt;
  if (this.blinkTimer <= 0 && !this.blinkStart) {
    this.blinkStart = this.clock; // but clock may not be updated yet at first
  }
  if (this.blinkStart !== undefined) {
    const t = clamp((this.clock - this.blinkStart)/0.15, 0, 1);
    const s = Math.sin(t*Math.PI);
    const ey = clamp(1 - s, 0.05, 1); // closed when s=1 (middle)
    this.parts.eyeL.scale.y = ey;
    this.parts.eyeR.scale.y = ey;
  }
}
```
Hmm I want eyes closed at middle of blink (s=1 → ey=0). At t=0 and t=1, s=0, ey=1 open. So blink: open→closed→open. Good. But I set ey = 1 - s. At s=1, ey=0 closed. Good.

But blinkStart should be set when blink begins. Let me set this.blinkStart = this.clock (current accumulated clock). But clock is updated at top of update before updateBlink? I set this.clock = clock at top, then call updateBlink. Good, clock is current time. Initialize this.blinkStart = 0 and blinkTimer initial so first blink happens. Let me set blinkStart undefined initially; when blinkTimer<=0 set blinkStart = this.clock. Then subsequent frames compute. After blink done (t>=1), next blinkTimer<=0 triggers new blink. But need to reset blinkStart to undefined after blink completes so it doesn't retrigger every frame. Let me set blinkStart = undefined when t>=1.

```
updateBlink() {
  this.blinkTimer -= dt;
  if (this.blinkTimer <= 0) {
    this.blinkStart = this.clock;
    this.blinkTimer = rand(2.5, 7);
  }
  if (this.blinkStart !== undefined) {
    const t = clamp((this.clock - this.blinkStart)/0.15, 0, 1);
    if (t >= 1) this.blinkStart = undefined;
    const s = Math.sin(t*Math.PI);
    const ey = clamp(1 - s, 0.05, 1);
    this.parts.eyeL.scale.y = ey;
    this.parts.eyeR.scale.y = ey;
  } else {
    this.parts.eyeL.scale.y = 1;
    this.parts.eyeR.scale.y = 1;
  }
}
```

Good.

Now the main loop:
```
let last = performance.now();
function tick(now) {
  const dt = Math.min((now - last)/1000, 0.05);
  last = now;
  time += dt;
  hamsters.forEach(h => h.update(dt, time));
  // wheel spin
  let riders = 0; hamsters.forEach(h=>{ if(h.state==='interact'&&h.riding) riders++; });
  const target = riders*3.2;
  wheelAngular += (target - wheelAngular)*Math.min(1,dt*3);
  wheel.rotation.x += wheelAngular*dt;
  // food wobble? optional
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
```

time accumulates for animations.

Let me define wheelAngular as a variable.

Now buildHamster returns group with userData.parts. Let me set group.userData.parts = {...}.

Let me write buildHamster.

Let me finalize everything and output.

I think it's solid. Let me write the final HTML file.

Let me make the UI show hamster count and maybe a hint. Keep as designed.

Also add a subtle title emoji.

Let me write it out completely now.

Double-check: MeshStandardMaterial with flatShading on IcosahedronGeometry detail 1 → faceted. Good. For spheres used for eyes/ears use low segments.

Let me ensure eyes are visible: at head front z=0.35 + radius ~0.4 → front ~0.75. Eyes at z=0.62. Good, facing +Z. Hamsters generally face +Z when yaw 0. Fine.

Nose at z=0.72. Cheeks at z=0.45. Good.

Ears at y=1.15, head top ~0.85+0.4=1.25. Ears on top. Good.

Body center y=0.55, radius 0.55 → top ~1.1, overlaps head lower part. Fine, looks like neckless blob cute.

Legs at y=0.09, length 0.18 → from 0 to 0.18. Feet near ground (y=0). Good. Body bottom ~0. Good.

Tail at back y=0.55 z=-0.6. Good.

Looks like a cute hamster. 

Now labels at y=1.5 above. Good.

Let me write final.

I'll also add a soft ground plane below the tray to receive shadows nicely and extend beyond cage (outside area). Actually shadows fall inside cage mostly. Let me add a large receiving floor outside too? The tray is the floor. Let me add a big plane below the whole cage (y=-0.3) to cast nice shadow context, colored slightly darker. Optional. Let me add a big floor plane at y = -0.32 (below tray) extending wide, receiving shadow, color #d9c6a8, so shadows show. And the tray sits on it.

Hmm but hamsters are inside the cage on the bedding (y~0). Their shadows fall on bedding (y~0.05) which is above the big floor (y=-0.32). Shadows won't show on bedding if receiver is lower. Shadow cascades are limited. Let me instead make the bedding surface itself receive shadows (a plane at y=0.05 with receiveShadow). That's where hamsters walk. Good. So define bedding plane at y=0.04 receiveShadow true. And skip big outer floor (or add for aesthetics without shadow). Let me add a big outer floor for look but it won't get shadows; fine.

Actually to keep shadows meaningful, make bedding surface (top of tray) the receiver. Tray top at y=0.04. Good.

Let me define:
- trayBody: box from y=-0.3 to y=0.02 (height 0.32), color light blue, receiveShadow + castShadow? Body cast shadow onto bedding maybe. Keep receiveShadow true.
- beddingTop: thin box height 0.06 at y=0.05, color tan, receiveShadow true. On top of tray body.

Wait tray body top at 0.02, bedding top at 0.05 overlaps. Let me make tray body top at 0.0 and bedding at 0.0..0.06. Simplify: trayBody box center y=-0.14 height 0.28 (top at 0.0). bedding box center y=0.03 height 0.06 (top 0.06). Good.

Add flakes on top of bedding at y~0.06.

Hamsters walk at y=0 (feet). group.position.y baseY=0. Good, feet at 0 = bedding surface 0.06 minus foot 0.18... hmm feet extend 0..0.18, so feet cross bedding surface. Fine, they stand on bedding.

Actually group.position.y=0 places feet centers at 0.09, feet span -0.09..0.27? Cylinder radius 0.07 centered y=0.09 → spans 0.02..0.16. So feet bottom at 0.02, sitting just above bedding 0.06. Slight overlap, fine.

OK good enough.

Let me write final file now. Enough deliberation.

Let me make sure to call controls.update() each frame.

Let me write the complete file.

I'll write clean code.

Also I'll add a tiny "zzz" or nothing. Keep simple.

Let me output.

Actually, let me reconsider the number of flakes (60) — fine.

Let me also add a couple of scattered pellets as food near bowl and maybe a small ball toy. I'll add a small rubber ball (sphere) that hamsters might bump. Optional but fun. Let me add one bouncing ball? That adds physics. Skip—keep deterministic. Just static ball decoration.

Let me add a small ball toy at x=1.5, z=-1.5, radius 0.25, color red-orange, with stripes (a torus around it). Static.

OK final.

Let me write it all.

Let me also ensure the food bowl pellets are inside and visible.

Alright, writing final answer.

Let me write the CSS for rounded rect helper in canvas—implement manually.

Final code below.

Let me make sure requestAnimationFrame tick uses delta capped.

Also handle visibility: not needed.

Write it.

I'll present the full index.html.

Let me also add a subtle gradient background using a large inverted sphere with vertex colors for a nicer sky. Actually fog + solid color is fine and stable. Keep solid.

Let me finalize.

One concern: MeshPhysicalMaterial transmission removed; using standard transparent walls. Good, lighter.

Let me write walls with opacity 0.22 and depthWrite false so sorting is okay. Since they're transparent and behind hamsters mostly, fine.

Frame posts: 4 corner posts (boxes) color #7fb0ff bright, plus top rails. Add for structure.

Let me define frameMat color #6ec6ff.

Corner posts at (±6, 1.5, ±4.5), size 0.2 x 3 x 0.2. Top rails connecting.

Let me add.

Alright final answer.

Let me write it cleanly and completely.

I'll now produce the final HTML.
</think>

# Low-Poly Hamster Playground 🐹

Here's a complete, single-file project. Just save it as `index.html` and open it in any modern browser — no build step, no dependencies to install (Three.js loads from a CDN via import maps).

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
    background: #f5e6d3; font-family: 'Comic Sans MS', 'Segoe UI', cursive, sans-serif; }
  #app { width: 100%; height: 100%; display: block; }
  #ui {
    position: fixed; top: 16px; left: 16px; z-index: 10;
    background: rgba(255,255,255,0.88); backdrop-filter: blur(6px);
    padding: 14px 18px; border-radius: 18px; max-width: 270px;
    box-shadow: 0 6px 20px rgba(90,70,50,0.18); color: #5a4632;
  }
  #ui h1 { font-size: 19px; margin-bottom: 6px; }
  #ui p  { font-size: 12.5px; line-height: 1.55; opacity: 0.88; }
  #ui .dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:6px; vertical-align:middle; }
  #loading {
    position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
    background: #f5e6d3; color: #5a4632; font-size: 22px; z-index: 20;
    font-family: inherit; letter-spacing: 0.5px; transition: opacity .5s;
  }
</style>
</head>
<body>
<div id="loading">Preparing hamsters... 🐹</div>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p><span class="dot" style="background:#f2b08a"></span><span class="dot" style="background:#c9c9d4"></span>
     <span class="dot" style="background:#ffb3c6"></span> Five little buddies exploring!</p>
  <p>🖱️ Drag to rotate • Scroll to zoom • Watch them walk, pause, &amp; hit the wheel!</p>
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

/* ----------------------------- helpers ----------------------------- */
const rand   = (a, b) => a + Math.random() * (b - a);
const clamp  = (v, a, b) => Math.max(a, Math.min(b, v));
const shortestYaw = (cur, tgt) => {
  let d = tgt - cur;
  while (d >  Math.PI) d -= Math.PI * 2;
  while (d < -Math.PI) d += Math.PI * 2;
  return cur + d;
};

/* --------------------------- renderer / scene ---------------------- */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.getElementById('app').appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xfce4c9);
scene.fog = new THREE.Fog(0xfce4c9, 15, 32);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 6.2, 11.5);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1.1, 0);
controls.minDistance = 5;
controls.maxDistance = 22;
controls.maxPolarAngle = Math.PI * 0.495;

/* ------------------------------ lights ----------------------------- */
scene.add(new THREE.HemisphereLight(0xffffff, 0xffd9b0, 0.75));
scene.add(new THREE.AmbientLight(0xffffff, 0.35));
const sun = new THREE.DirectionalLight(0xfff3e0, 1.45);
sun.position.set(7, 13, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1; sun.shadow.camera.far = 45;
sun.shadow.camera.left = -14; sun.shadow.camera.right = 14;
sun.shadow.camera.top = 14; sun.shadow.camera.bottom = -14;
sun.shadow.bias = -0.0004;
scene.add(sun);

/* ------------------------- cage dimensions ------------------------- */
const W = 12, D = 9, WALL_H = 3;                 // tray width/depth
const HALF_W = W / 2, HALF_D = D / 2;

/* ---------------------------- floor/tray --------------------------- */
const trayBody = new THREE.Mesh(
  new THREE.BoxGeometry(W, 0.28, D),
  new THREE.MeshStandardMaterial({ color: 0x9ad7ff, roughness: 0.9, flatShading: true }));
trayBody.position.y = -0.14; trayBody.receiveShadow = true;
scene.add(trayBody);

const bedding = new THREE.Mesh(
  new THREE.BoxGeometry(W - 0.2, 0.06, D - 0.2),
  new THREE.MeshStandardMaterial({ color: 0xe9c893, roughness: 1, flatShading: true }));
bedding.position.y = 0.03; bedding.receiveShadow = true;
scene.add(bedding);

// scattered wood shavings
const flakeMat = new THREE.MeshStandardMaterial({ color: 0xd9b877, flatShading: true, roughness: 1 });
for (let i = 0; i < 70; i++) {
  const f = new THREE.Mesh(new THREE.BoxGeometry(rand(0.14, 0.34), 0.05, rand(0.09, 0.2)), flakeMat);
  f.position.set(rand(-HALF_W + 0.6, HALF_W - 0.6), 0.07, rand(-HALF_D + 0.6, HALF_D - 0.6));
  f.rotation.set(rand(0, Math.PI), rand(0, Math.PI), rand(0, Math.PI));
  scene.add(f);
}

/* --------------------------- cage walls ---------------------------- */
const wallMat = new THREE.MeshStandardMaterial({
  color: 0xbfeaff, transparent: true, opacity: 0.22, roughness: 0.5,
  side: THREE.DoubleSide, depthWrite: false });
const frameMat = new THREE.MeshStandardMaterial({ color: 0x6ec6ff, roughness: 0.6, flatShading: true });
const wallGeoX = new THREE.BoxGeometry(W + 0.2, WALL_H, 0.12);
const wallGeoZ = new THREE.BoxGeometry(0.12, WALL_H, D + 0.2);
const mkWall = (geo, x, y, z) => { const m = new THREE.Mesh(geo, wallMat); m.position.set(x, y, z); return m; };
scene.add(mkWall(wallGeoX, 0, WALL_H / 2,  HALF_D));
scene.add(mkWall(wallGeoX, 0, WALL_H / 2, -HALF_D));
scene.add(mkWall(wallGeoZ,  HALF_W, WALL_H / 2, 0));
scene.add(mkWall(wallGeoZ, -HALF_W, WALL_H / 2, 0));

// frame posts + top rails
const postGeo = new THREE.BoxGeometry(0.22, WALL_H, 0.22);
[[  HALF_W, HALF_D],[ -HALF_W, HALF_D],[  HALF_W,-HALF_D],[ -HALF_W,-HALF_D]].forEach(([x, z]) => {
  const p = new THREE.Mesh(postGeo, frameMat); p.position.set(x, WALL_H / 2, z); p.castShadow = true; scene.add(p);
});
const railGeoX = new THREE.BoxGeometry(W + 0.2, 0.14, 0.18);
const railGeoZ = new THREE.BoxGeometry(0.18, 0.14, D + 0.2);
[HALF_D, -HALF_D].forEach(z => { const r = new THREE.Mesh(railGeoX, frameMat); r.position.set(0, WALL_H - 0.05, z); scene.add(r); });
[HALF_W, -HALF_W].forEach(x => { const r = new THREE.Mesh(railGeoZ, frameMat); r.position.set(x, WALL_H - 0.05, 0); scene.add(r); });

/* ----------------------- interactive: wheel ------------------------ */
const WHEEL_X = -3.2, WHEEL_Z = 1.2, WHEEL_Y = 0.95, WHEEL_R = 0.9;
const wheel = new THREE.Group();
const wheelMat = new THREE.MeshStandardMaterial({ color: 0xffd93d, roughness: 0.55, flatShading: true });
const rimMat   = new THREE.MeshStandardMaterial({ color: 0xff8fab, roughness: 0.6, flatShading: true });
const rim1 = new THREE.Mesh(new THREE.TorusGeometry(WHEEL_R, 0.07, 8, 26), wheelMat);
rim1.rotation.y = Math.PI / 2; rim1.position.x = -0.12;
rim2 = rim1.clone(); rim2.position.x = 0.12;
const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.3, 8), rimMat);
hub.rotation.z = Math.PI / 2;
wheel.add(rim1, rim2, hub);
for (let i = 0; i < 14; i++) {
  const a = (i / 14) * Math.PI * 2;
  const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.028, 0.028, 0.24, 6), wheelMat);
  rung.rotation.z = Math.PI / 2;
  rung.position.set(0, Math.cos(a) * WHEEL_R, Math.sin(a) * WHEEL_R);
  wheel.add(rung);
}
// stand
const post = new THREE.Mesh(new THREE.BoxGeometry(0.16, WHEEL_Y + 0.1, 0.16), frameMat);
post.position.set(0.28, (WHEEL_Y + 0.1) / 2, 0);
const arm  = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.14, 0.4), frameMat);
arm.position.set(0.14, WHEEL_Y + 0.05, 0);
const foot = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.1, 0.5), frameMat);
foot.position.set(0.28, 0.02, 0);
[post, arm, foot].forEach(m => { m.castShadow = true; wheel.add(m); });
wheel.position.set(WHEEL_X, WHEEL_Y, WHEEL_Z);
scene.add(wheel);

/* ------------------------- food bowl ------------------------------ */
const bowl = new THREE.Group();
const bowlMat = new THREE.MeshStandardMaterial({ color: 0xff6b6b, roughness: 0.6, flatShading: true });
const bowlShell = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.5, 0.32, 16, 1, true), bowlMat);
bowlShell.position.y = 0.16;
const bowlBottom = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.46, 0.06, 16), bowlMat);
bowlBottom.position.y = 0.03;
const pelletColors = [0xf9c74f, 0x90be6d, 0xf8961e, 0xcb9d99];
for (let i = 0; i < 10; i++) {
  const p = new THREE.Mesh(new THREE.DodecahedronGeometry(rand(0.07, 0.11), 0),
    new THREE.MeshStandardMaterial({ color: pelletColors[i % pelletColors.length], roughness: 0.8, flatShading: true }));
  const rr = Math.random() * 0.34, tt = Math.random() * Math.PI * 2;
  p.position.set(Math.cos(tt) * rr, 0.22 + Math.sin(tt * 3) * 0.03, Math.sin(tt) * rr);
  p.rotation.set(rand(0, 3), rand(0, 3), rand(0, 3));
  bowl.add(p);
}
bowl.add(bowlShell, bowlBottom);
bowl.position.set(3.2, 0, -1.3);
bowl.traverse(o => { if (o.isMesh) o.castShadow = true; });
scene.add(bowl);

/* ------------------------- tunnel + ball -------------------------- */
const tunnel = new THREE.Group();
const tunnelMat = new THREE.MeshStandardMaterial({ color: 0x4ecdc4, roughness: 0.7, flatShading: true, side: THREE.DoubleSide });
const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 2.4, 16, 1, true), tunnelMat);
tube.rotation.x = Math.PI / 2; tube.position.y = 0.72;
const ringMat = new THREE.MeshStandardMaterial({ color: 0xffe66d, roughness: 0.6, flatShading: true });
[-1.2, 1.2].forEach(z => {
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.05, 8, 20), ringMat);
  ring.rotation.y = Math.PI / 2; ring.position.set(0, 0.72, z); tunnel.add(ring);
});
[[-0.9, 0], [0.9, 0]].forEach(([z]) => {
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.09, 0.72, 6), ringMat);
  leg.position.set(0, 0.36, z); tunnel.add(leg);
});
tunnel.position.set(0.7, 0, 1.7);
tunnel.traverse(o => { if (o.isMesh) o.castShadow = true; });
scene.add(tunnel);

const ball = new THREE.Group();
const ballShell = new THREE.Mesh(new THREE.IcosahedronGeometry(0.28, 0),
  new THREE.MeshStandardMaterial({ color: 0xff7675, roughness: 0.6, flatShading: true }));
ballShell.position.y = 0.28;
const band = new THREE.Mesh(new THREE.TorusGeometry(0.28, 0.04, 6, 16),
  new THREE.MeshStandardMaterial({ color: 0xfd79a8, roughness: 0.6, flatShading: true }));
band.position.y = 0.28; band.rotation.x = Math.PI / 3;
ball.add(ballShell, band);
ball.position.set(1.6, 0, -1.6);
ball.traverse(o => { if (o.isMesh) o.castShadow = true; });
scene.add(ball);

/* --------------------------- hamsters ----------------------------- */
function buildHamster(mainColor) {
  const g = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: mainColor, roughness: 0.9, flatShading: true });
  const bellyMat = new THREE.MeshStandardMaterial({ color: 0xfff3e0, roughness: 0.9, flatShading: true });
  const skinMat  = new THREE.MeshStandardMaterial({ color: 0xffb3c6, roughness: 0.85, flatShading: true });

  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 1), bodyMat);
  body.scale.set(1, 0.92, 1.16); body.position.y = 0.56;
  const belly = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 1), bellyMat);
  belly.scale.set(0.92, 0.86, 1.12); belly.position.set(0, 0.54, 0.13);
  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.4, 1), bodyMat);
  head.position.set(0, 0.86, 0.36);
  const earGeo = new THREE.SphereGeometry(0.14, 6, 5);
  const earL = new THREE.Mesh(earGeo, bodyMat); earL.position.set(-0.22, 1.16, 0.34);
  const earR = earL.clone(); earR.position.x = 0.22;
  const cheekGeo = new THREE.SphereGeometry(0.13, 6, 5);
  const cheekL = new THREE.Mesh(cheekGeo, skinMat); cheekL.position.set(-0.26, 0.79, 0.46);
  const cheekR = cheekL.clone(); cheekR.position.x = 0.26;
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.3 });
  const eyeGeo = new THREE.SphereGeometry(0.075, 8, 6);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat); eyeL.position.set(-0.16, 0.93, 0.63);
  const eyeR = eyeL.clone(); eyeR.position.x = 0.16;
  const shiny = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const shineGeo = new THREE.SphereGeometry(0.025, 6, 4);
  const shL = new THREE.Mesh(shineGeo, shiny); shL.position.set(-0.14, 0.96, 0.67);
  const shR = shL.clone(); shR.position.x = 0.18;
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), skinMat);
  nose.position.set(0, 0.83, 0.73);
  const legGeo = new THREE.CylinderGeometry(0.07, 0.08, 0.18, 6);
  const legMat = new THREE.MeshStandardMaterial({ color: 0xffc0cb, roughness: 0.9, flatShading: true });
  const legs = [[-0.3, 0.09, 0.26], [0.3, 0.09, 0.26], [-0.3, 0.09, -0.26], [0.3, 0.09, -0.26]]
    .map(p => { const l = new THREE.Mesh(legGeo, legMat); l.position.set(...p); return l; });
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 5), bellyMat);
  tail.position.set(0, 0.55, -0.62);

  g.add(body, belly, head, earL, earR, cheekL, cheekR, eyeL, eyeR, shL, shR, nose, ...legs, tail);
  g.userData.parts = { body, head, eyeL, eyeR, legs };
  return g;
}

function makeLabel(text, color) {
  const c = document.createElement('canvas'); c.width = 256; c.height = 64;
  const ctx = c.getContext('2d');
  ctx.fillStyle = 'rgba(255,255,255,0.9)';
  ctx.beginPath(); ctx.roundRect(6, 6, 244, 52, 16); ctx.fill();
  ctx.strokeStyle = color; ctx.lineWidth = 4; ctx.beginPath(); ctx.roundRect(6, 6, 244, 52, 16); ctx.stroke();
  ctx.fillStyle = '#5a4632'; ctx.font = 'bold 30px Comic Sans MS, cursive';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, 128, 34);
  const tex = new THREE.CanvasTexture(c);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }));
  s.scale.set(1.7, 0.42, 1); return s;
}

const NAMES = [['Biscuit', '#f2b08a'], ['Mochi', '#fff3e0'], ['Pebble', '#c9c9d4'], ['Rosie', '#ffb3c6'], ['Avocado', '#b5d8a0']];
const RIDING_POS = new THREE.Vector3(WHEEL_X, WHEEL_Y - WHEEL_R + 1.12, WHEEL_Z);

const hamsters = [];
for (let i = 0; i < 5; i++) {
  const [name, hex] = NAMES[i];
  const col = new THREE.Color(hex);
  const group = buildHamster(col);
  const label = makeLabel(name, hex); label.position.y = 1.55; group.add(label);
  group.traverse(o => { if (o.isMesh) o.castShadow = true; });

  const h = {
    group, baseY: 0, parts: group.userData.parts,
    state: 'wander', timer: rand(1, 4), pauseDuration: rand(2, 4.5),
    speed: rand(0.5, 0.9), target: { x: rand(-4.6, 4.6), z: rand(-3.2, 3.2) },
    yaw: rand(0, Math.PI * 2), bobPhase: rand(0, Math.PI * 2),
    riding: false, ridingTime: 0, rideDuration: rand(2.6, 4),
    blinkTimer: rand(2, 6), blinkStart: null, clock: 0,
    ridingPos: RIDING_POS.clone(),
  };
  group.position.set(rand(-4.6, 4.6), 0, rand(-3.2, 3.2));
  scene.add(group);
  hamsters.push(h);
}

/* ----------------------- hamster behaviour ------------------------ */
function animateLegs(h) {
  const legs = h.parts.legs;
  for (let i = 0; i < 4; i++) {
    const dir = i < 2 ? 1 : -1;
    const side = (i % 2 === 0) ? 1 : -1;
    legs[i].rotation.x = dir * side * Math.sin(h.bobPhase + (i % 2) * Math.PI) * 0.7;
  }
}

function updateBlink(h) {
  h.blinkTimer -= 0.016; // approx per-frame; real dt applied below
  if (h.blinkTimer <= 0) { h.blinkStart = h.clock; h.blinkTimer = rand(2.5, 7); }
  if (h.blinkStart !== undefined) {
    const t = clamp((h.clock - h.blinkStart) / 0.15, 0, 1);
    if (t >= 1) h.blinkStart = undefined;
    const ey = clamp(1 - Math.sin(t * Math.PI), 0.05, 1);
    h.parts.eyeL.scale.y = ey; h.parts.eyeR.scale.y = ey;
  } else {
    h.parts.eyeL.scale.y = 1; h.parts.eyeR.scale.y = 1;
  }
}

function updateHamster(h, dt) {
  h.clock += dt;
  updateBlink(h);

  if (h.state === 'interact') {
    if (!h.riding) {
      const dx = h.ridingPos.x - h.group.position.x;
      const dz = h.ridingPos.z - h.group.position.z;
      const d = Math.hypot(dx, dz);
      if (d > 0.5) {
        const step = h.speed * 1.4 * dt;
        h.group.position.x += (dx / d) * step;
        h.group.position.z += (dz / d) * step;
        h.group.position.x = clamp(h.group.position.x, -5.4, 5.4);
        h.group.position.z = clamp(h.group.position.z, -3.9, 3.9);
        h.yaw = Math.atan2(dx, dz);
        h.group.rotation.y = shortestYaw(h.group.rotation.y, h.yaw);
        h.bobPhase += dt * h.speed * 12;
        animateLegs(h);
      } else {
        h.riding = true; h.ridingTime = 0;
        h.group.position.copy(h.ridingPos);
        h.group.rotation.y = Math.PI / 2;
        h.group.rotation.x = 0.12;
      }
    } else {
      h.ridingTime += dt;
      h.bobPhase += dt * 14;
      h.group.position.y = h.ridingPos.y + Math.abs(Math.sin(h.bobPhase)) * 0.04;
      if (h.ridingTime >= h.rideDuration) {
        h.riding = false; h.state = 'wander'; h.timer = rand(0.5, 1.5);
        h.group.rotation.x = 0;
        h.target = { x: Math.max(rand(-4.6, 4.6), -1), z: rand(-3.2, 3.2) };
      }
    }
    return;
  }

  h.timer -= dt;

  if (h.state === 'wander') {
    const dx = h.target.x - h.group.position.x;
    const dz = h.target.z - h.group.position.z;
    const d = Math.hypot(dx, dz);
    if (d < 0.25 || h.timer <= 0) {
      const r = Math.random();
      if (r < 0.34)      { h.state = 'pause'; h.timer = h.pauseDuration; }
      else if (r < 0.55) { h.state = 'interact'; h.riding = false; h.ridingTime = 0; }
      else               { h.target = { x: rand(-4.6, 4.6), z: rand(-3.2, 3.2) }; h.timer = rand(2.5, 5); }
    } else {
      const step = h.speed * dt;
      h.group.position.x += (dx / d) * step;
      h.group.position.z += (dz / d) * step;
      h.group.position.x = clamp(h.group.position.x, -5.4, 5.4);
      h.group.position.z = clamp(h.group.position.z, -3.9, 3.9);
      h.yaw = Math.atan2(dx, dz);
      h.group.rotation.y = shortestYaw(h.group.rotation.y, h.yaw);
      h.bobPhase += dt * h.speed * 10;
      animateLegs(h);
    }
  } else if (h.state === 'pause') {
    h.group.position.y = h.baseY + Math.sin(h.clock * 2.2) * 0.02;
    h.group.rotation.z = Math.sin(h.clock * 1.5) * 0.04;
    h.parts.head.rotation.z = Math.sin(h.clock * 1.8) * 0.08;
    h.parts.head.rotation.y = Math.sin(h.clock * 1.2) * 0.15;
  }
}

/* --------------------------- animation ---------------------------- */
let time = 0, last = performance.now(), wheelAngular = 0;

function tick(now) {
  const dt = Math.min((now - last) / 1000, 0.05);
  last = now; time += dt;

  hamsters.forEach(h => updateHamster(h, dt));

  let riders = 0;
  hamsters.forEach(h => { if (h.state === 'interact' && h.riding) riders++; });
  const target = riders * 3.2;
  wheelAngular += (target - wheelAngular) * Math.min(1, dt * 3);
  wheel.rotation.x += wheelAngular * dt;

  // gentle ball bounce for extra life
  ball.position.y = Math.abs(Math.sin(time * 1.6)) * 0.05;
  ball.rotation.y += dt * 0.4;

  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}

requestAnimationFrame(tick);

/* ----------------------------- resize ----------------------------- */
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// hide loader once first frame is drawn
const el = document.getElementById('loading');
el.style.opacity = '0'; setTimeout(() => el.remove(), 600);
</script>
</body>
</html>
```

## What's inside

**Scene contents**
- **Cage**: translucent acrylic-style walls with bright blue corner posts and top rails so the enclosure reads clearly.
- **Floor/tray**: a light-blue plastic tray topped with wood-shavings bedding plus ~70 scattered flakes for texture.
- **5 low-poly hamsters** (Biscuit, Mochi, Pebble, Rosie, Avocado) built from icosahedrons/spheres with flat shading — chubby bodies, fluffy belly, perky ears, rosy cheeks, shiny eyes, little legs, and stumpy tails. Each has a floating name tag.
- **Interactive object**: a spinning exercise wheel that actually rotates faster when a hamster rides it.
- **Decorations**: a food bowl full of pellets, a striped tunnel, and a bouncing ball.

**Autonomous behavior** (per-hamster state machine)
- **Wander** → walk toward a random point, smoothly turn to face travel direction, legs animate, body bobs.
- **Pause** → sniff around, tilt head, gentle sway.
- **Interact** → trot to the wheel, climb on, and run it for a few seconds (spins the wheel) before wandering off again.
- Plus randomized blinking for extra cuteness.

**Controls**: drag to orbit, scroll to zoom (clamped so you can't lose the scene), soft damping, and a shadow-casting warm sun.

It runs instantly — just open the file in Chrome/Firefox/S Edge. Everything is self-contained in the one file.