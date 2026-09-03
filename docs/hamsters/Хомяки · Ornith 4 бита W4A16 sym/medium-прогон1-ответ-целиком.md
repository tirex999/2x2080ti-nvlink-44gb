Let me create a single-file browser project called "Low-Poly Hamster Playground" using Three.js. I need to:

1. Create an index.html file that includes everything (HTML, CSS, JavaScript)
2. Use Three.js (I'll load it from CDN)
3. Create a 3D scene with:
   - A cage
   - A floor/tray
   - Several low-poly hamsters
   - At least one interactive object (wheel, tunnel, food bowl, or toy)
4. Hamsters should have autonomous behavior (walking, pausing, turning, interacting)
5. Cute, low-poly, colorful, funny visual style
6. Camera rotation controls
7. Should run immediately in a modern browser

Let me think about the structure:

- Use Three.js from CDN (unpkg or cdnjs)
- Use OrbitControls for camera rotation
- Build the scene procedurally with Three.js geometries

For the low-poly aesthetic, I'll use flat shading (MeshStandardMaterial or MeshLambertMaterial with flatShading: true).

Let me design the scene:

**Cage:**
- A wireframe or transparent box representing the cage walls
- A base tray

**Floor:**
- A colored plane with bedding material texture (maybe just color)

**Hamsters:**
- Low-poly body (sphere/icosahedron)
- Ears (small spheres)
- Eyes (black spheres)
- Nose (pink)
- Cheeks
- Little feet/legs
- Tail

**Interactive objects:**
- Exercise wheel (spins when hamster interacts)
- Food bowl
- Tunnel (cylinder)
- Maybe a ball toy

**Behavior:**
- Hamsters wander randomly
- Sometimes pause
- Sometimes turn around
- Some interact with the wheel (make it spin)

Let me write this out carefully. I want it to be stable and fun.

Let me structure the hamster creation function so I can create multiple hamsters with slightly different colors.

For autonomous behavior, I'll give each hamster a state machine:
- WANDER: walk in a direction, occasionally change
- PAUSE: stand still for a bit
- INTERACT: go to and use an object (wheel)

Let me implement this step by step.

I'll use:
- Three.js r128 or a recent version from CDN
- OrbitControls

Let me use a recent version with import maps or just classic scripts. To keep it simple and robust, I'll use the classic script approach with a specific version.

Actually, let me use the module approach with import maps for a cleaner modern setup, or use the UMD build. Let me use the UMD build which is simpler for a single file.

Three.js r128 has a build at https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js and OrbitControls at https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js

Actually, with newer versions the controls are separate modules. Let me stick with r128 UMD builds which expose THREE and THREE.OrbitControls.

Wait, in r128, OrbitControls is available as THREE.OrbitControls when loaded via the examples js file. Let me verify... Actually in older versions like r128, the file three.min.js doesn't include OrbitControls. The examples/js/controls/OrbitControls.js adds THREE.OrbitControls globally. That should work.

Let me use r128 to be safe with the global approach.

Actually, let me reconsider. Modern approach with import maps is cleaner but requires ES modules. Let me use the import map approach with a recent version since it's more future-proof and the instructions say "modern browser."

Hmm, but import maps with OrbitControls require the addons path. Let me set up:

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

This should work in modern browsers. Let me go with this.

Now let me build the scene.

Let me think about dimensions. The cage could be like 10x4x6 (width x height x depth). Let me make it reasonable.

Let me code:

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xfff0f5); // light pink background
scene.fog = new THREE.Fog(0xfff0f5, 20, 60);

// Camera
const camera = new THREE.PerspectiveCamera(50, width/height, 0.1, 100);
camera.position.set(0, 8, 16);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(width, height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 2, 0);
controls.maxPolarAngle = Math.PI * 0.495; // don't go below ground
```

Now lighting:
```javascript
const ambient = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(8, 15, 8);
sun.castShadow = true;
sun.shadow.mapSize.width = 2048;
sun.shadow.mapSize.height = 2048;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 50;
sun.shadow.camera.left = -15;
sun.shadow.camera.right = 15;
sun.shadow.camera.top = 15;
sun.shadow.camera.bottom = -15;
scene.add(sun);
```

Now the cage tray (floor):
```javascript
const trayWidth = 14, trayDepth = 10, trayHeight = 1.5;
// Base tray
```

Let me build the tray as a box with open top, maybe with raised edges.

Actually let me build:
- Floor plane with bedding color
- Raised walls of the tray (low)
- Transparent cage walls above

Let me create the bedding as a slightly bumpy surface or just a flat plane with wood-shaving color.

Let me create the hamster builder function.

```javascript
function createHamster(color) {
  const hamster = new THREE.Group();
  
  // Body
  const bodyGeo = new THREE.SphereGeometry(0.7, 12, 10);
  const bodyMat = new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9 });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.scale.set(1, 0.9, 1.2);
  body.castShadow = true;
  hamster.add(body);
  
  // Head
  const headGeo = new THREE.SphereGeometry(0.45, 12, 10);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.position.set(0.7, 0.1, 0);
  head.castShadow = true;
  hamster.add(head);
  
  // Ears
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

For the feet, I'll add small cylinders or spheres that bob when walking.

Let me add legs:
```javascript
const legPositions = [
  [0.35, -0.5, 0.3],
  [0.35, -0.5, -0.3],
  [-0.35, -0.5, 0.3],
  [-0.35, -0.5, -0.3]
];
```

Each leg is a small cylinder + foot sphere. For walking animation, I'll bob the body and alternate legs.

Actually, to keep it simpler and stable, I'll bob the whole body up and down while walking, and add a slight rotation. The legs can just stay. But adding leg animation makes it cuter. Let me add simple leg movement.

Let me think about the eye placement. Eyes are on the head, facing forward-ish. Black spheres. Add little shine.

Nose: pink small sphere at front of head.

Cheeks: two pinkish circles on the sides of the face for that cute chubby look.

Ears: two small circles on top of head.

Let me also give each hamster a slightly different color palette and maybe a stripe or spot.

Now the interactive objects:

1. **Exercise wheel** - a big ring with rungs. When a hamster is in "interacting" state near it, it spins.

2. **Food bowl** - a small bowl with seeds.

3. **Tunnel** - a cylinder you can see through (transparent or colored).

4. **Ball toy** - a colorful ball.

Let me include a wheel (main interactive), a food bowl, and a tunnel. Maybe a ball too.

Let me implement the wheel spinning based on hamster interaction.

Now the AI behavior. Each hamster has:
- state: 'wander' | 'pause' | 'goToTarget' | 'interact'
- velocity/direction
- timer for next action
- target position for interactions

Let me implement a simple wandering system within the cage bounds.

```javascript
class HamsterAI {
  constructor(hamster, mesh) {
    this.hamster = hamster;
    this.mesh = mesh;
    this.state = 'wander';
    this.direction = new THREE.Vector3(Math.random()-0.5, 0, Math.random()-0.5).normalize();
    this.speed = 0.6 + Math.random()*0.4;
    this.timer = 0;
    this.pauseTime = 0;
    this.target = null;
    this.walkPhase = 0;
  }
  
  update(dt) {
    // handle state transitions
  }
}
```

Let me define interaction points:
- Wheel position
- Food bowl position
- Tunnel position

When a hamster decides to interact, it picks a random point, moves toward it, and when arrives, does the interaction (wheel spins, eating at bowl, hiding in tunnel).

Let me simplify: 
- Wander: move in current direction, bounce off walls, occasionally random turn.
- Every few seconds, maybe decide to go to an object.
- At object, perform interaction for a duration.

Let me write the update logic:

```javascript
update(dt) {
  const h = this.mesh;
  this.timer -= dt;
  
  switch(this.state) {
    case 'wander':
      // move
      h.position.addScaledVector(this.direction, this.speed * dt);
      // body orientation follows direction
      h.rotation.y = Math.atan2(this.direction.x, this.direction.z);
      // bob
      this.walkPhase += dt * 10;
      h.position.y = Math.abs(Math.sin(this.walkPhase)) * 0.05;
      // bounce off walls
      checkBounds();
      // random turn
      if (Math.random() < 0.01) {
        this.direction.applyAxisAngle(new THREE.Vector3(0,1,0), (Math.random()-0.5)*1.5);
        this.direction.normalize();
      }
      // sometimes pause or go to object
      if (this.timer <= 0) {
        this.chooseAction();
      }
      break;
    case 'pause':
      // stand still, head looks around
      this.timer -= dt; // handled above
      // small idle bob
      if (this.timer <= 0) this.state = 'wander';
      break;
    case 'goto':
      // move toward target
      const toTarget = this.target.clone().sub(h.position);
      toTarget.y = 0;
      const dist = toTarget.length();
      if (dist < 0.2) {
        this.state = 'interact';
        this.interactTimer = this.interactDuration;
        this.onArrive();
      } else {
        toTarget.normalize();
        h.position.addScaledVector(toTarget, this.speed * dt);
        h.rotation.y = Math.atan2(toTarget.x, toTarget.z);
        this.walkPhase += dt*10;
        h.position.y = Math.abs(Math.sin(this.walkPhase))*0.05;
      }
      break;
    case 'interact':
      this.interactTimer -= dt;
      this.onInteract(dt);
      if (this.interactTimer <= 0) {
        this.state = 'wander';
        this.direction = new THREE.Vector3(Math.random()-0.5,0,Math.random()-0.5).normalize();
        this.timer = 1 + Math.random()*2;
      }
      break;
  }
}
```

Hmm, the timer handling is getting complicated because I subtract in multiple places. Let me restructure with clear timers.

Let me simplify by using a single approach where each state sets its own remaining time.

Actually, let me make it cleaner:

```javascript
update(dt) {
  const h = this.mesh;
  switch(this.state) {
    case 'wander':
      this.wander(dt);
      break;
    case 'pause':
      this.pauseTime -= dt;
      this.idle(h);
      if (this.pauseTime <= 0) {
        this.state = 'wander';
        this.nextActionTimer = 2 + Math.random()*3;
      }
      break;
    case 'goto':
      this.goto(dt);
      break;
    case 'interact':
      this.interactTime -= dt;
      this.onInteract(dt);
      if (this.interactTime <= 0) {
        this.state = 'wander';
        // face away
        this.direction = h.rotation ...; // or random
        this.nextActionTimer = 2 + Math.random()*3;
      }
      break;
  }
}
```

And in wander, when nextActionTimer runs out, choose between pause, goto, or continue wandering.

Let me refine:

```javascript
wander(dt) {
  const h = this.mesh;
  h.position.addScaledVector(this.direction, this.speed * dt);
  h.rotation.y = Math.atan2(this.direction.x, this.direction.z);
  this.walkPhase += dt * 10;
  h.position.y = Math.abs(Math.sin(this.walkPhase)) * 0.06;
  animateLegs(this, this.walkPhase);
  
  // keep within bounds
  const margin = 1.0;
  const maxX = cageHalfWidth - margin;
  const maxZ = cageHalfDepth - margin;
  if (Math.abs(h.position.x) > maxX) {
    h.position.x = Math.sign(h.position.x) * maxX;
    this.direction.x *= -1;
  }
  if (Math.abs(h.position.z) > maxZ) {
    h.position.z = Math.sign(h.position.z) * maxZ;
    this.direction.z *= -1;
  }
  // random turns
  if (Math.random() < 0.02) {
    this.direction.applyAxisAngle(new THREE.Vector3(0,1,0), (Math.random()-0.5)*1.2);
    this.direction.normalize();
  }
  
  this.nextActionTimer -= dt;
  if (this.nextActionTimer <= 0) {
    this.chooseAction();
  }
}

chooseAction() {
  const roll = Math.random();
  if (roll < 0.3) {
    this.state = 'pause';
    this.pauseTime = 1.5 + Math.random()*2;
  } else if (roll < 0.75) {
    // go to object
    const idx = Math.floor(Math.random()*interactionPoints.length);
    const pt = interactionPoints[idx];
    this.target = pt.position.clone();
    this.target.y = 0;
    this.state = 'goto';
    this.interactType = pt.type;
    this.interactDuration = pt.duration;
  } else {
    // just wander more
    this.direction.applyAxisAngle(new THREE.Vector3(0,1,0), (Math.random()-0.5)*2);
    this.direction.normalize();
  }
  this.nextActionTimer = 2 + Math.random()*3;
}
```

For the wheel interaction, the hamster needs to get close and the wheel spins. Let me make the wheel spin based on whether any hamster is currently interacting with it.

Let me define interaction points:
```javascript
const interactionPoints = [
  { type: 'wheel', position: new THREE.Vector3(-4, 0, 3), radius: 1.2, duration: 4 },
  { type: 'food', position: new THREE.Vector3(4, 0, -3), radius: 1.0, duration: 3 },
  { type: 'tunnel', position: new THREE.Vector3(0, 0, -4), radius: 1.5, duration: 2.5 },
];
```

When going to wheel, target is offset from wheel so hamster stands at the rungs.

For the wheel spinning, I'll track a boolean per wheel "active" and spin it faster when active, decelerate when not.

```javascript
let wheelSpin = 0;
function updateWheel(dt) {
  const active = hamsters.some(h => h.state === 'interact' && h.interactType === 'wheel');
  const targetSpeed = active ? 6 : 0;
  wheelSpin += (targetSpeed - wheelSpin) * dt * 2;
  wheel.rotation.y += wheelSpin * dt;
}
```

The hamster at the wheel should face the wheel and bob up and down (running).

Let me make the hamster's interact animation: bobbing body faster, legs moving.

For food: hamster stands at bowl, little head bob (eating).
For tunnel: hamster walks into tunnel (hide), then comes out.

Let me handle tunnel: when arriving, move hamster behind/in front of tunnel briefly then exit. Actually simpler: when at tunnel, hide it (set visible false) for duration, then reappear and wander off. Or move hamster along the tunnel. Let me do: hamster teleports to tunnel center, hides (invisible) for duration, reappears. That's funny.

Actually let me make the tunnel a semi-transparent tube so you can see the hamster inside. Then the hamster moves to the center and stays (visible through tube). That's cute and shows interaction.

Hmm, but then it's stuck in the tunnel. Let me do: hamster goes to tunnel entrance, walks through to the other side and disappears behind, then reappears. Simpler to just have it hide for the duration.

Let me keep it manageable. I'll do:
- Wheel: hamster runs at the wheel, wheel spins.
- Food: hamster eats at bowl (head bob).
- Tunnel: hamster walks to tunnel, becomes invisible for a moment (like it went inside), reappears.

For the tunnel invisibility, I'll set the hamster group visible = false during the hide.

OK let me now also think about the visual cuteness:
- Soft pastel colors
- Rounded shapes
- Big eyes
- Blush cheeks
- Little smile maybe

Let me add blush (pink circles on cheeks) and a small smile (a curved line or small dark shape).

A smile could be a small torus or a bent cylinder. Let me use a small torus segment or just skip and use a tiny cone/nose. Actually a smile adds character. Let me add a small dark curve using a TorusGeometry scaled.

Let me keep it reasonable. I'll add:
- Body, head
- 2 ears
- 2 eyes (white + black pupil + highlight)
- Pink nose
- Pink blush cheeks
- 4 feet (with simple animation)
- Small tail

Let me write the full code now.

For the bedding/floor, let me add some scattered "shavings" as small random boxes or just a textured plane. To keep low-poly and simple, I'll use a plane with a subtle color and maybe some small colored cones/spheres scattered as decoration (pebbles, seeds).

Let me also add a little house/shelter for the hamsters - a small wooden hut. That adds charm. Maybe optional. Let me add a small house.

Let me plan the layout:
- Cage centered at origin, 14 wide (x), 10 deep (z), walls up to ~4.
- Tray floor at y=0.
- House in one corner.
- Wheel in another area.
- Food bowl in another.
- Tunnel connecting areas.

Let me finalize positions:
- House: (-5, 0, -3)
- Wheel: (4.5, 0, 3)
- Food bowl: (5, 0, -3)
- Tunnel: (0, 0, 3.5) horizontal cylinder

Let me write it all out.

Let me be careful with the cage walls - I'll make them transparent (like acrylic/glass) with slight tint, so you can see inside. Edge frames for style.

Cage construction:
- Floor tray: a box (open top) - actually let me make the tray as a shallow box with 4 walls and a floor.
- Upper walls: transparent panels on 4 sides, open top.

Let me build the tray:
```javascript
const tray = new THREE.Group();
const trayWallMat = new THREE.MeshStandardMaterial({ color: 0xffb3c6, flatShading: true, roughness: 0.8 });
const trayW = 14, trayD = 10, trayH = 1.2, thickness = 0.3;

// floor
const floor = new THREE.Mesh(new THREE.BoxGeometry(trayW, thickness, trayD), trayWallMat);
floor.position.y = thickness/2;
floor.receiveShadow = true;
tray.add(floor);

// 4 walls
// front/back/left/right
```

Then bedding on top: a plane at y = thickness + small, color wood shaving.

Then transparent upper walls starting from trayH.

Let me code the upper walls as transparent boxes.

Actually, to keep the hamsters contained visually and allow camera to see, transparent walls are good.

Let me now write everything.

For shadows, only cast on floor/tray and objects. Set castShadow/receiveShadow appropriately.

Let me also add a subtle ground plane outside the cage for shadows? Not necessary. The tray floor receives shadows.

Let me write the animate loop with dt using clock.

```javascript
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  updateHamsters(dt);
  updateWheel(dt);
  controls.update();
  renderer.render(scene, camera);
}
animate();
```

Window resize handler.

Let me now write the complete file.

Let me think about the hamster leg animation more concretely. I'll store references to 4 legs and their base phases. When walking, alternate front-back pairs.

```javascript
hamster.userData.legs = [
  { pos: [0.4, -0.55, 0.28], phase: 0 },
  { pos: [0.4, -0.55, -0.28], phase: Math.PI },
  { pos: [-0.4, -0.55, 0.28], phase: Math.PI },
  { pos: [-0.4, -0.55, -0.28], phase: 0 },
];
```

During walking, each leg's bottom y oscillates: baseY - |sin(phase + t)| * amount. And rotate leg slightly.

Let me implement animateLegs:
```javascript
function animateLegs(group, t, walking) {
  const legs = group.userData.legs;
  legs.forEach(leg => {
    const swing = walking ? Math.sin(t + leg.phase) : 0;
    leg.mesh.position.y = leg.baseY + Math.max(0, swing) * 0.08;
    leg.mesh.rotation.x = swing * 0.3;
  });
}
```

I'll build legs as small cylinders with spherical feet.

Actually simpler: legs as small spheres (feet) that lift. Let me just do feet spheres.

Let me build each leg group: a short cylinder (leg) + sphere (foot). Or just a fat capsule. Let me do a small cylinder colored darker (paw) plus a pink foot pad. Keep simple: just a sphere foot per leg.

Let me do: leg = cylinder (skin colored) standing from body down to foot, foot = flattened sphere. For animation, translate the whole leg group up/down and rotate.

I'll attach legs to the hamster group so they move with it. Each leg is a child group at base position; I animate its local y and rotation.

Let me code building:

```javascript
function makeLeg(baseX, baseZ, phase) {
  const legGroup = new THREE.Group();
  legGroup.position.set(baseX, 0, baseZ);
  const leg = new THREE.Mesh(
    new THREE.CylinderGeometry(0.1, 0.12, 0.35, 8),
    bodyMat
  );
  leg.position.y = -0.18;
  leg.castShadow = true;
  legGroup.add(leg);
  const foot = new THREE.Mesh(
    new THREE.SphereGeometry(0.13, 8, 6),
    footMat // pinkish
  );
  foot.position.y = -0.35;
  foot.scale.y = 0.7;
  legGroup.add(foot);
  return legGroup;
}
```

Then store userData.legs with mesh reference and baseY = legGroup.position.y (0).

Animate: legGroup.position.y = Math.max(0, sin(...)) * 0.1; legGroup.rotation.x = sin(...)*0.4.

Good.

Now the body bob while walking: hamster group.position.y oscillates slightly, and maybe slight tilt.

Let me set the hamster group's vertical position offset for walking bob.

Alright.

Let me also add a little tail: small sphere at back.

Now let me consider the hamster facing direction and mirror for color. Not needed.

Let me write the final code. I'll be thorough.

One more consideration: performance and stability. Use modest polygon counts. flatShading true gives low-poly look and reduces need for textures.

Let me set environment a bit: a gradient background via canvas or just solid color. Solid pastel is fine. Maybe add a soft radial gradient via a big sphere? Keep simple: solid color + fog.

Let me add a ceiling light feel with two lights (ambient + directional) plus maybe a hemispheric light for soft fill.

Add HemisphereLight for nice ambient.

Let me finalize colors:
- Background: #ffe6f0 (soft pink)
- Tray: #ff9eb5 (pink) or #ffd6a5 (warm). Let me use a nice teal tray? For contrast with pink hamsters. Let me use a soft coral/pink tray and light wood bedding.
- Bedding: #f0d9a8 (straw/wood)
- Hamster colors: various pastels - #ffb3ba (pink), #baffc9 (green), #bae1ff (blue), #ffffba (yellow), #e7baff (purple)
- Wheel: bright color like #8ec5ff or multicolor rungs
- Food bowl: #ff6b6b
- Tunnel: #95e1d3 (mint) or rainbow
- House: #f4a460 (wood) with roof #d2691e

Let me make it colorful and fun.

Now let me write the HTML with styling and UI hint text.

Add a title overlay and instructions.

Let me write it all.

I need to make sure OrbitControls import works. With import map pointing to unpkg three@0.160.0, the addons path examples/jsm/OrbitControls.js should exist. Good.

Let me double check the unpkg URL structure:
- https://unpkg.com/three@0.160.0/build/three.module.js ✓
- https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js ✓

Good.

Let me write the code carefully, ensuring no syntax errors.

I'll structure JS:
1. Imports
2. Scene, camera, renderer, controls
3. Lights
4. Build functions: buildCage, buildHamster, buildWheel, buildFoodBowl, buildTunnel, buildHouse, decorate
5. Interaction points array
6. Hamster class / AI
7. Animation loop

Let me write the Hamster as a class holding mesh + AI.

Let me write:

```javascript
class Hamster {
  constructor(color, name) {
    this.mesh = createHamster(color);
    this.name = name;
    this.state = 'wander';
    this.direction = new THREE.Vector3(Math.random()-0.5, 0, Math.random()-0.5).normalize();
    this.speed = 0.7 + Math.random()*0.5;
    this.walkPhase = Math.random()*10;
    this.nextActionTimer = 1 + Math.random()*3;
    this.interactType = null;
    this.interactTime = 0;
    this.pauseTime = 0;
    this.target = new THREE.Vector3();
    scene.add(this.mesh);
    // start position
    this.mesh.position.set((Math.random()-0.5)*6, 1.2, (Math.random()-0.5)*4);
  }
  
  update(dt) {
    switch(this.state) {
      case 'wander': this._wander(dt); break;
      case 'pause': this._pause(dt); break;
      case 'goto': this._goto(dt); break;
      case 'interact': this._interact(dt); break;
    }
  }
  ...
}
```

Let me define cage bounds constants for reuse:
```javascript
const BOUNDS = { x: 6.5, z: 4.3 }; // half extents minus margin
```

Actually tray is 14 wide so half is 7, minus margins ~1 => 6. Let me set x bound 6.2, z bound 3.8.

Let me compute based on actual tray dims.

Let me just hardcode reasonable bounds matching tray.

Tray: width 14 (x from -7 to 7), depth 10 (z from -5 to 5). Hamsters should stay inside. Margin 0.8. So x in [-6.2, 6.2], z in [-4.2, 4.2].

Let me set BOUNDS accordingly.

Now for goto target near objects, ensure targets are within bounds. Wheel at (4.5,0,3) is fine. Food at (5,-3). Tunnel at (0,3.5). House area avoid? It's fine, hamsters can approach house.

Let me write the interaction specifics:

_wheel = spin. On arrive, set state interact, type wheel, time duration. During interact, hamster bobs (running) and faces wheel. Also mark wheel active.

Let me track activeWheel boolean computed each frame:
```javascript
const wheelRunning = hamsters.some(h => h.state === 'interact' && h.interactType === 'wheel');
```

_updateWheel(dt): interpolate wheelSpin toward (wheelRunning ? 8 : 0).

For the hamster at the wheel, position it right at the wheel rungs facing it. When goto arrives, I'll snap position to a point near the wheel. Let me compute arrival position as the target (which I set offset from wheel).

Let me set target = wheelPosition + offset so hamster stands at the running position. The wheel is vertical axis? A hamster wheel rotates around a horizontal axis (like a real exercise wheel — the wheel plane is vertical, axis horizontal). The hamster runs inside, so it faces the wheel's flat side.

Let me orient wheel: wheel is a vertical ring (like a big hula hoop) with horizontal axle. Rotation around the horizontal axle (say X axis). The hamster stands inside facing sideways (+X or -X).

Hmm, let me define wheel geometry:
- Main ring: TorusGeometry(radius, tubeRadius, ...) with rotation so the ring is in the YZ plane (so it looks like a vertical wheel) — actually torus default is in XY plane (flat, like a donut lying flat, hole along Z). To make a vertical wheel (like a ferris wheel), rotate so plane is YZ: rotate X by 90°. Then the axle is along X. Rotation of the wheel is around X axis.

The hamster stands inside at the bottom, facing along X (perpendicular to wheel plane). So wheel position + hamster offset along X.

Let me place wheel axle at (4.5, wheelCenterY, 3). Wheel radius ~1.2. Hamster stands at (4.5 + 1.2 + 0.3, 0, 3)? No—the hamster runs INSIDE the wheel at the bottom. Real hamster wheels: hamster runs on the inner surface at bottom. For simplicity, I'll place the hamster in front of the wheel (outside) running, which looks fine and cute. Or inside at bottom.

Let me place hamster at the front of the wheel facing it, feet at bottom of wheel. Actually let me put the hamster slightly in front (along +X) at ground level, and the wheel behind it. When spinning, it looks like it's running. Good enough.

Let me define:
- Wheel center: (4.5, 1.5, 3), radius 1.2, axle along X.
- Support stand: two vertical bars + axle.
- Hamster standing point: (4.5 + 1.3, 0, 3) facing -X (toward wheel). Its target for goto = (5.8, 0, 3).

Wait if hamster is at +X facing wheel at origin-ish, hamster faces -X. rotation.y = atan2(dir.x, dir.z). If dir = (-1,0,0) => atan2(-1, 0) = -π/2. Good.

The wheel rotates around X axis when running.

Rungs: create small cylinders arranged radially inside the torus, or just rely on torus + a few bars. Let me add rungs as thin cylinders along the axle at various angular positions to make spinning visible.

Let me build wheel:
```javascript
function buildWheel(x, y, z) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  const ringMat = new THREE.MeshStandardMaterial({ color: 0x6dd5ff, flatShading: true, roughness: 0.5, metalness: 0.1 });
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.2, 0.12, 8, 24), ringMat);
  ring.rotation.y = Math.PI/2; // now ring plane is YZ? 
  ...
}
```

Wait, torus default lies in XY plane with normal along Z. To make it a vertical wheel (plane YZ, normal X), rotate around X by 90°: ring.rotation.x = Math.PI/2. Then it stands vertical facing X. The hamster runs along... hmm.

Let me think: I want the wheel to look like a ferris wheel (vertical circle) that spins around a horizontal axle. The axle should be horizontal. Let axle be along Z or X. Let me make axle along Z (so wheel faces X, hamster runs on the side). Actually either works.

Let me make: ring in XY plane rotated so it's vertical. If I rotate the torus by x = PI/2, the ring's plane becomes... The torus is generated in XY plane (the donut lies flat in XY, hole along Z). Rotating about X by 90° tilts it: now the donut plane contains Z axis. The ring becomes vertical with normal along Z. Hmm, let me just visualize: 

Default torus: points at ( (R + r cos v) cos u, (R + r cos v) sin u, r sin v ). So it's in XY (u goes around, centered at origin in XY), z is the tube. Normal (hole direction) is Z.

Rotate about X by 90°: y' = y cos - z sin... This maps the XY-plane ring into XZ plane. So ring becomes vertical (XZ plane), hole along Y (vertical). That's not what I want; I want hole horizontal (axle horizontal) and ring vertical.

Ugh, let me think again. A ferris wheel: ring is vertical circle, axle is horizontal passing through center. The ring's plane is vertical; the axle is perpendicular to the ring plane, so axle is horizontal.

If ring plane is XZ (vertical), axle is along Y (vertical) — that's a spinning top orientation, not ferris wheel. Wait no. If ring plane is XZ, the normal to that plane is Y. The axle is along the normal = Y (vertical). That's like a spinning disc vertically but axle vertical — no.

Hold on. A wheel (like a bicycle wheel) has a plane and an axle perpendicular to that plane. Bicycle wheel plane is vertical, axle is horizontal (through the axle, left-right). So ring plane = vertical (say XY plane if facing sideways, i.e., we see the wheel face-on when looking along Z). Axle along Z.

So: ring in XY plane, axle along Z. That's the DEFAULT torus orientation! Default torus is in XY plane with hole/axle along Z. 

So I DON'T rotate the default torus. The wheel stands like a bicycle wheel facing us (we look along Z to see it round). Axle along Z.

But then the hamster runs on the... the wheel is in XY plane facing Z. The hamster would run along the axle direction? No. A hamster wheel: the hamster runs inside the ring, on the inner bottom surface, and the ring spins around the horizontal axle. The hamster moves perpendicular to... Actually the hamster runs and the wheel surface moves; the axle is horizontal and parallel to the hamster's forward/back axis? 

In reality, a hamster wheel axle is horizontal and runs left-to-right relative to the running hamster (the hamster runs forward, its back is to the side, axle goes through both sides). So axle is horizontal, perpendicular to hamster's motion. Ring plane is vertical and contains the hamster's up-down and forward-back directions. So ring plane is vertical, containing vertical (Y) and forward (say X). Axle along Z (horizontal, to the side).

So ring plane = XY? No: ring plane contains Y (up) and X (forward) → that's XY plane, and axle along Z. Yes! Ring plane XY, axle Z. Same as default torus. 

So hamster runs along X (forward), wheel faces Z (we see it from front if we look along -Z). The hamster is at the bottom of the wheel, inside, at some X position, and the wheel spins around Z.

Wait but if the hamster runs forward (X) inside the wheel, and the wheel spins around Z (axle horizontal, to the side), then the hamster's forward direction is tangent to the wheel at the bottom. Yes that matches: at the bottom of the wheel, the tangent is horizontal (X direction). 

So: wheel center at (cx, cy, cz), hamster at (cx, bottomInner, cz + something)? The hamster is inside the ring at the bottom. Ring in XY plane centered (cx,cy,cz). Bottom inner point is (cx, cy - (R - tube), cz). Hamster stands there facing +X (forward). The wheel spins around Z axis (through center), i.e., wheel.rotation.z.

Hmm wait, spinning around Z means the ring (in XY plane) rotates in its own plane — yes that's the wheel spinning. wheel.rotation.z += speed.

But actually the hamster runs forward and appears to stay in place while the wheel spins — the hamster's feet push the wheel. In our scene the hamster stays at the bottom and the wheel spins. Good.

So wheel.rotation.z is the spin. Let me set the hamster to stand at the bottom inside.

Let me set:
- Wheel center: (4.5, 1.6, 3). Radius R = 1.2.
- Axle support: two vertical posts on either side (±Z) holding the axle.
- Hamster stand point: (4.5, 0, 3) — at ground directly at bottom of wheel, facing +X. Actually the hamster should be at the bottom inner of the wheel. Let me put hamster at (4.5, 0.2, 3) facing +X, and wheel spans from y=1.0 to y=2.2 roughly. Hamster at bottom inside.

Hold on, if the hamster faces +X and runs, and the wheel is in XY plane... the hamster's forward is X which is tangent at bottom. Fine. But we (camera) looking at the scene from an angle see the wheel as an ellipse; that's fine.

Actually, wait. If the hamster is AT the bottom of the wheel and the wheel is in the XY plane (facing Z), then the hamster is at the front face of the wheel (near Z = cz). It would be visible. Good.

Let me place hamster stand target at (4.5, 0, 3.0 + 0.0)? The wheel has thickness (tube). Hamster at cz, facing +X. Fine.

Let me set the goto target for wheel = (4.5, 0, 3) — same as wheel base. But other hamsters might block. It's fine.

Actually, I realize placing hamster exactly at wheel center z might overlap the wheel structure. Let me offset hamster slightly to front: target z = 3 + 0.3. Facing +X means dir (1,0,0). It stands just in front of the wheel's lower area. Good.

Let me set wheel interaction target = (4.5, 0, 3.35).

For food bowl: hamster stands beside bowl, eats. target = bowlPos + offset.

For tunnel: hamster walks to tunnel entrance, hides, reappears.

Let me define tunnel as a horizontal cylinder (axle horizontal) that the hamster can walk through. Place tunnel along X axis at (0, 0.6, 4) — a mint tube. Hamster walks in one end, out the other. For simplicity, when interacting, hamster moves to tunnel center and becomes invisible for duration, then reappears at start.

Actually let me make tunnel interaction: hamster goes to one entrance (target = tunnel end), walks to center, disappears (as if inside), reappears at the other end, wanders off.

Simplify: 
- goto target = tunnel entrance A = ( -2, 0, 4 ).
- On arrive: state interact, type tunnel. During interact: set mesh.visible = false for first half, then visible = true at exit B = (2,0,4). Hmm timing.

Let me do: during interact, count time. At t=duration/2, teleport hamster to exit and set visible true. Before that invisible. So:
```javascript
_interact_tunnel: 
  this.interactTime -= dt;
  const total = this.interactDuration;
  if (this.interactTime < total/2) this.mesh.visible = false;
  else { this.mesh.position.copy(exitPos); this.mesh.visible = true; }
  if (this.interactTime <= 0) { done }
```

That's cute (hamster disappears into tunnel, emerges on other side).

Let me generalize interact by type.

Let me now also make sure the hamster faces appropriate directions at each object. In _goto, set rotation to face movement. On arrive, adjust facing:
- wheel: face +X (dir (1,0,0)) → but depends on wheel side. Let me set facing based on target.
- food: face bowl.
- tunnel: face direction of travel.

Simplest: after arriving, set a facing direction variable and lerp rotation. Or just set rotation.y directly per type.

Let me handle in interact: set mesh.rotation.y to a target facing depending on type:
- wheel: Math.atan2(1, 0) = π/2? atan2(dir.x, dir.z). For facing +X, dir=(1,0): atan2(1,0)=π/2. Hmm rotation.y = π/2 means rotated to face +X? Let me verify: default hamster faces +Z (since head at +0.7? no I put head at +x). Let me define hamster default facing.

I built head at +X (position.set(0.7,0.1,0)). So the hamster's "front" is +X. That's unusual; usually front is +Z. Let me instead build head at +Z so default facing is +Z, matching atan2 conventions. Let me set head position (0, 0.1, 0.7). Then eyes/nose at +Z.

Then to face direction d (unit in XZ), rotation.y = atan2(d.x, d.z). For d=(0,0,1) (default +Z), atan2(0,1)=0 → faces +Z. Good.

So I'll build the hamster facing +Z.

For wheel, hamster faces +X: d=(1,0,0), rotation.y = atan2(1,0) = π/2 ≈ 1.5708.
For food at (5,0,-3) from near, facing toward bowl.
For tunnel along X, facing +X or -X.

Let me just set facing explicitly in interact based on type, computing from target direction.

Actually, I'll compute a desired facing in _goto when arriving: the hamster is moving along direction to target; keep that facing. For wheel specifically, I want it to face +X regardless. Let me special-case.

Let me define per-type approach vector (where the hamster should face while interacting):
- wheel: (1, 0, 0)
- food: direction from bowl outward? The hamster faces the bowl, so face toward bowl: (bowlPos - hamsterPos). Normalize.
- tunnel: travel direction.

I'll set this in the interact setup.

Let me store this.direction as the "facing" while interacting too (reuse). In _interact, I won't move, but I'll set a facingDir and rotate toward it.

Let me code:

```javascript
_interact(dt) {
  const h = this.mesh;
  this.interactTime -= dt;
  const t = this.interactDuration - this.interactTime; // elapsed
  if (this.interactType === 'wheel') {
    // run in place
    this.walkPhase += dt * 20;
    h.position.y = Math.abs(Math.sin(this.walkPhase)) * 0.08 + 0.0;
    animateLegs(this.mesh, this.walkPhase, true);
    // face wheel (+X)
    lerpRotation(h, Math.atan2(1, 0), dt);
  } else if (this.interactType === 'food') {
    // eat: head bob
    this.walkPhase += dt * 8;
    h.position.y = Math.abs(Math.sin(this.walkPhase)) * 0.03;
    // little nibble: rotate head? head is part of group. Let me bob whole group slightly.
    animateLegs(this.mesh, this.walkPhase, false);
    lerpRotation(h, this.facingY, dt);
  } else if (this.interactType === 'tunnel') {
    const total = this.interactDuration;
    if (t < total/2) {
      h.visible = false;
    } else {
      if (!this.exited) {
        this.exited = true;
        h.position.copy(this.tunnelExit);
        h.visible = true;
        this.facingY = Math.atan2(this.tunnelDir.x, this.tunnelDir.z);
      }
      animateLegs(this.mesh, this.walkPhase, true);
      lerpRotation(h, this.facingY, dt);
    }
  }
  if (this.interactTime <= 0) {
    h.visible = true;
    h.position.y = 0;
    this.state = 'wander';
    this.direction = new THREE.Vector3(Math.random()-0.5, 0, Math.random()-0.5).normalize();
    this.nextActionTimer = 1.5 + Math.random()*2.5;
  }
}
```

lerpRotation eases current rotation.y toward target:
```javascript
function lerpRotation(obj, target, dt) {
  // shortest path
  let diff = target - obj.rotation.y;
  while (diff > Math.PI) diff -= Math.PI*2;
  while (diff < -Math.PI) diff += Math.PI*2;
  obj.rotation.y += diff * Math.min(1, dt*8);
}
```

Good.

Now _goto:
```javascript
_goto(dt) {
  const h = this.mesh;
  const to = this.target.clone().sub(h.position);
  to.y = 0;
  const dist = to.length();
  if (dist > 0.05) {
    to.normalize();
    h.position.addScaledVector(to, this.speed * dt);
    lerpRotation(h, Math.atan2(to.x, to.z), dt);
    this.walkPhase += dt * 10;
    h.position.y = Math.abs(Math.sin(this.walkPhase)) * 0.05;
    animateLegs(this.mesh, this.walkPhase, true);
  } else {
    // arrived
    h.position.y = 0;
    if (this.interactType === 'tunnel') {
      this.tunnelExit = this.target.clone();
      this.tunnelExit.x += 4; // exit other side
      this.tunnelDir = new THREE.Vector3(1,0,0);
    }
    this.state = 'interact';
    this.interactTime = this.interactDuration;
    this.exited = false;
  }
}
```

Hmm for tunnel, the target is entrance; exit = entrance + 4 in X. Let me set tunnel along X from x=-2 to x=2. Entrance target = (-2,0,4). Exit = (2,0,4). tunnelDir = (1,0,0). Good.

_pause:
```javascript
_pause(dt) {
  const h = this.mesh;
  animateLegs(h, this.walkPhase, false);
  // idle: slight head tilt / look around
  this.walkPhase += dt * 2;
  h.position.y = Math.abs(Math.sin(this.walkPhase)) * 0.01;
  // occasional tiny turn
  if (Math.random() < 0.02) lerpRotation(h, h.rotation.y + (Math.random()-0.5)*0.5, dt);
  this.pauseTime -= dt;
  if (this.pauseTime <= 0) {
    this.state = 'wander';
    this.direction = new THREE.Vector3(Math.random()-0.5,0,Math.random()-0.5).normalize();
    this.nextActionTimer = 2 + Math.random()*3;
  }
}
```

_wander as above.

chooseAction as above.

Now createHamster builds the mesh and returns group with userData.legs.

Let me write createHamster:

```javascript
function createHamster(color, accentColor) {
  const g = new THREE.Group();
  const furMat = new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.95 });
  const bellyMat = new THREE.MeshStandardMaterial({ color: 0xfff5e0, flatShading: true, roughness: 0.95 });
  const pinkMat = new THREE.MeshStandardMaterial({ color: 0xff9db0, flatShading: true, roughness: 0.8 });
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x2b2b2b, flatShading: true, roughness: 0.6 });
  const whiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });
  
  // Body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.65, 14, 12), furMat);
  body.scale.set(1, 0.92, 1.15);
  body.position.y = 0.6;
  body.castShadow = true;
  g.add(body);
  
  // Belly
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.55, 12, 10), bellyMat);
  belly.scale.set(0.9, 0.85, 1.0);
  belly.position.set(0, 0.5, 0.22);
  g.add(belly);
  
  // Head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.46, 14, 12), furMat);
  head.position.set(0, 0.85, 0.55);
  head.castShadow = true;
  g.add(head);
  
  // Cheeks (chubby)
  const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.22, 10, 8), furMat);
  cheekL.position.set(0.22, 0.75, 0.72);
  g.add(cheekL);
  const cheekR = cheekL.clone();
  cheekR.position.x = -0.22;
  g.add(cheekR);
  
  // Blush
  const blushL = new THREE.Mesh(new THREE.CircleGeometry(0.09, 10), pinkMat);
  blushL.position.set(0.26, 0.72, 0.86);
  blushL.lookAt(0.26+0.3, 0.72, 2);
  g.add(blushL);
  const blushR = blushL.clone();
  blushR.position.x = -0.26;
  blushR.lookAt(-0.26-0.3, 0.72, 2);
  g.add(blushR);
  
  // Ears
  const earGeo = new THREE.SphereGeometry(0.14, 10, 8);
  const earL = new THREE.Mesh(earGeo, furMat);
  earL.position.set(0.2, 1.2, 0.5);
  earL.scale.set(1, 1, 0.6);
  earL.castShadow = true;
  g.add(earL);
  const earR = earL.clone();
  earR.position.x = -0.2;
  g.add(earR);
  
  // Eyes
  const eyeWhiteGeo = new THREE.SphereGeometry(0.1, 12, 10);
  const pupilGeo = new THREE.SphereGeometry(0.065, 10, 8);
  const highlightGeo = new THREE.SphereGeometry(0.025, 8, 6);
  [-0.16, 0.16].forEach(xoff => {
    const ew = new THREE.Mesh(eyeWhiteGeo, whiteMat);
    ew.position.set(xoff, 0.9, 0.92);
    g.add(ew);
    const p = new THREE.Mesh(pupilGeo, darkMat);
    p.position.set(xoff, 0.9, 0.98);
    g.add(p);
    const hi = new THREE.Mesh(highlightGeo, whiteMat);
    hi.position.set(xoff + 0.02, 0.93, 1.0);
    g.add(hi);
  });
  
  // Nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 6), pinkMat);
  nose.position.set(0, 0.8, 1.0);
  nose.scale.y = 0.8;
  g.add(nose);
  
  // Smile (small torus arc)
  const smile = new THREE.Mesh(new THREE.TorusGeometry(0.06, 0.012, 6, 12, Math.PI), darkMat);
  smile.position.set(0, 0.72, 0.94);
  smile.rotation.x = Math.PI * 0.15;
  smile.rotation.z = Math.PI;
  g.add(smile);
  
  // Tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 6), pinkMat);
  tail.position.set(0, 0.5, -0.72);
  tail.scale.set(0.8, 0.8, 0.6);
  g.add(tail);
  
  // Legs
  const legs = [];
  const legBaseY = 0.18;
  const legDefs = [
    [0.32, 0.35, 0],
    [0.32, -0.35, Math.PI],
    [-0.32, 0.35, Math.PI],
    [-0.32, -0.35, 0],
  ];
  legDefs.forEach(([lx, lz, phase]) => {
    const legGroup = new THREE.Group();
    legGroup.position.set(lx, legBaseY, lz);
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.09, 0.22, 8), furMat);
    leg.position.y = -0.1;
    leg.castShadow = true;
    legGroup.add(leg);
    const foot = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 6), pinkMat);
    foot.position.y = -0.2;
    foot.scale.y = 0.6;
    legGroup.add(foot);
    g.add(legGroup);
    legs.push({ group: legGroup, baseY: legBaseY, phase });
  });
  g.userData.legs = legs;
  
  g.scale.setScalar(0.8);
  return g;
}
```

Wait, legs baseY = 0.18 but body bottom is around y=0.6-0.65=... body center y=0.6 radius scaled 0.92*0.65≈0.6, so bottom ~0.0. Floor at y=0 (bedding). Actually tray top bedding at y ~ thickness (1.2?) Hmm. Let me reconsider vertical scale.

Wait, I set tray height 1.2 with floor thickness 0.3, bedding on top. That makes the floor at y=1.2+? That's high. Let me reduce. Let me make tray lower so hamsters sit nicely.

Let me redesign tray:
- Total tray height ~1.0.
- Floor slab thickness 0.2 at y=0.1 (center), top at y=0.2.
- Bedding layer from y=0.2 to y=0.35, color straw.
- Tray side walls from y=0 to y=1.0 (raised edges), open top.

Hamsters stand on bedding at y≈0.35. Hamster body center at y≈0.35+0.6=0.95. Legs from body down to y≈0.35.

Let me set legBaseY relative to group: body center is at some y. Since hamster group position is set at ground level (y = bedding height), the hamster's internal coordinates go up. Let me set hamster group y = beddingTop (0.35). Then legs base at group-local y such that feet reach 0.35 → group-local 0. So legs baseY should be ~0 (feet at group origin y=0). Let me set legBaseY = 0 and feet at -0.2 reaches y=0.15 above bedding? Hmm.

Let me simplify: hamster group placed at y=0 corresponds to ground. I'll set ground (bedding) at y=0 for hamster purposes, and raise the whole tray visually but keep hamster coords relative to bedding.

Actually simplest: put bedding plane at y=0 (world), and build tray walls below/around. Let me put the tray floor top at y=0 and walls going down? That's weird for camera.

Let me just do: bedding surface at y=0. Tray walls rise from y=0 up to y=1.2 (the rim). Below y=0 there's the tray bottom (a slab from y=-0.3 to y=0). So:
- Slab: y from -0.3 to 0 (center -0.15).
- Bedding: thin layer at y=0 to 0.05 (or just use slab top as bedding).
- Walls: y from 0 to 1.2.

Hamster group placed at y=0 (on bedding). Legs baseY = 0.2 (from body down), feet reach ~0.

Let me set body center y = 0.65, radius ~0.6 → bottom ~0.05. Good, sits on bedding. Legs from y=0.4 down to 0.

Let me set legBaseY = 0.4, leg length 0.25, foot at -0.12 → y=0.28. Eh, let me just make feet reach ~0. legBaseY=0.4, cylinder from 0.4 to 0.15, foot at 0.1. Let me set leg group position y=0.4, leg mesh y=-0.12 (extends 0.4-0.12±0.12 → 0.16 to 0.4? no). Cylinder height 0.28 centered at y=-0.14 → from -0.28 to 0 → world 0.12 to 0.4. Foot sphere at y=-0.16 → world 0.24. Hmm feet not quite at 0. Let me set foot at y=-0.28 → world 0.12. Close enough. Or lower leg group to 0.35.

I'm overthinking pixel precision. Let me set:
- body center y = 0.6, radius 0.6, bottom ~0.0.
- legBaseY = 0.3.
- leg cylinder height 0.22, positioned y=-0.11 → spans 0.0 to 0.22.
- foot sphere y=-0.18 radius 0.09 → spans -0.27 to -0.09 → world -0.27 to -0.09. Slightly below 0 but fine (sinks into bedding visually).

Good enough. Let me finalize with body center y=0.6.

Now the bedding: a plane at y=0 (or slightly above) covering the tray interior, color straw. Plus scattered bits.

Let me build tray:

```javascript
function buildCage() {
  const cage = new THREE.Group();
  const wallMat = new THREE.MeshStandardMaterial({ color: 0xffb0c8, flatShading: true, roughness: 0.7, transparent: true, opacity: 1 });
  const glassMat = new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.18, roughness: 0.1, metalness: 0, transmission: 0.9, thickness: 0.5 });
  
  const W = 14, D = 10, rimH = 1.3, slabT = 0.3;
  
  // Slab (bottom)
  const slab = new THREE.Mesh(new THREE.BoxGeometry(W, slabT, D), wallMat);
  slab.position.y = -slabT/2 + 0; // center -0.15
  slab.position.y = -0.15;
  slab.receiveShadow = true;
  cage.add(slab);
  
  // Bedding surface
  const bedding = new THREE.Mesh(new THREE.BoxGeometry(W-0.4, 0.08, D-0.4), new THREE.MeshStandardMaterial({ color: 0xf2d9a0, flatShading: true, roughness: 1 }));
  bedding.position.y = 0.04;
  bedding.receiveShadow = true;
  cage.add(be);
  
  // 4 side walls (raised rim) - opaque lower portion
  const sideMat = wallMat;
  // front & back
  [1, -1].forEach(s => {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(W, rimH, 0.3), sideMat);
    wall.position.set(0, rimH/2, s*(D/2 - 0.15));
    wall.castShadow = true;
    wall.receiveShadow = true;
    cage.add(wall);
  });
  // left & right
  [1, -1].forEach(s => {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(0.3, rimH, D), sideMat);
    wall.position.set(s*(W/2 - 0.15), rimH/2, 0);
    wall.castShadow = true;
    cage.add(wall);
  });
  
  // Transparent upper walls (glass) from rimH up
  const glassH = 3.0;
  const glassFront = new THREE.Mesh(new THREE.BoxGeometry(W, glassH, 0.1), glassMat);
  glassFront.position.set(0, rimH + glassH/2, D/2 - 0.15);
  cage.add(glassFront);
  const glassBack = glassFront.clone();
  glassBack.position.z = -(D/2 - 0.15);
  cage.add(glassBack);
  const glassLeft = new THREE.Mesh(new THREE.BoxGeometry(0.1, glassH, D), glassMat);
  glassLeft.position.set(W/2 - 0.15, rimH + glassH/2, 0);
  cage.add(glassLeft);
  const glassRight = glassLeft.clone();
  glassRight.position.x = -(W/2 - 0.15);
  cage.add(glassRight);
  
  // Frame edges (thin darker lines) - optional, add corners for style
  ...
  
  scene.add(cage);
  return { W, D, rimH };
}
```

The glass material with transmission requires physical material and may need environment map for good look; without it, opacity approach is safer. Let me use a simpler transparent material: MeshStandardMaterial with transparent true, opacity 0.2, color light blue. That avoids transmission complexity. Let me use that for reliability.

Actually MeshPhysicalMaterial transmission needs proper setup and can render dark without environment. Let me use MeshPhysicalMaterial but also add environment? Too complex. Use simple transparent standard material. Good for stability.

Let me set glassMat = new THREE.MeshStandardMaterial({ color: 0xcfeaff, transparent: true, opacity: 0.22, roughness: 0.2, side: THREE.DoubleSide }).

Now decorations:
- Scattered shavings: small thin boxes/cones random on bedding.
- Some colored beads/seeds.
- Food bowl with seeds.
- Wheel.
- Tunnel.
- House.

Let me build these and add to scene.

Food bowl:
```javascript
function buildFoodBowl(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0.05, z);
  const bowlMat = new THREE.MeshStandardMaterial({ color: 0xff6b6b, flatShading: true, roughness: 0.6 });
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.35, 0.25, 16, 1, true), bowlMat);
  bowl.position.y = 0.12;
  bowl.castShadow = true;
  g.add(bowl);
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.05, 16), bowlMat);
  base.position.y = 0.025;
  g.add(base);
  // bottom
  const bottom = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.02, 16), bowlMat);
  bottom.position.y = 0.01;
  g.add(bottom);
  // seeds
  const seedMat = new THREE.MeshStandardMaterial({ color: 0xd4a373, flatShading: true });
  for (let i=0;i<14;i++){
    const seed = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.12, 5), seedMat);
    const a = Math.random()*Math.PI*2, r = Math.random()*0.3;
    seed.position.set(Math.cos(a)*r, 0.22 + Math.random()*0.05, Math.sin(a)*r);
    seed.rotation.z = (Math.random()-0.5)*1.2;
    g.add(seed);
  }
  scene.add(g);
  return g;
}
```

Tunnel:
```javascript
function buildTunnel(x, z, len, dir) {
  const g = new THREE.Group();
  g.position.set(x, 0.6, z);
  const tunnelMat = new THREE.MeshStandardMaterial({ color: 0x95e1d3, flatShading: true, roughness: 0.7, side: THREE.DoubleSide });
  const tunnel = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, len, 20, 1, true), tunnelMat);
  if (dir === 'x') tunnel.rotation.z = Math.PI/2;
  tunnel.castShadow = true;
  g.add(tunnel);
  // stripes
  ...
  scene.add(g);
  return g;
}
```

Place tunnel along X at (0,0.6,4), len 4.

House:
```javascript
function buildHouse(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0.05, z);
  const woodMat = new THREE.MeshStandardMaterial({ color: 0xe0a363, flatShading: true, roughness: 0.9 });
  const roofMat = new THREE.MeshStandardMaterial({ color: 0xc0392b, flatShading: true, roughness: 0.8 });
  const walls = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.2, 1.8), woodMat);
  walls.position.y = 0.6;
  walls.castShadow = true; walls.receiveShadow = true;
  g.add(walls);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(1.4, 0.9, 4), roofMat);
  roof.position.y = 1.55;
  roof.rotation.y = Math.PI/4;
  roof.castShadow = true;
  g.add(roof);
  // door hole (dark)
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.7, 0.1), new THREE.MeshStandardMaterial({ color: 0x3b2a1a, flatShading:true }));
  door.position.set(0, 0.4, 0.9);
  g.add(door);
  scene.add(g);
  return g;
}
```

Wheel stand + ring. Let me build:
```javascript
function buildWheel(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const spinPart = new THREE.Group(); // rotating ring + rungs
  spinPart.position.y = 1.5;
  const ringMat = new THREE.MeshStandardMaterial({ color: 0x6dd5ff, flatShading: true, roughness: 0.4, metalness: 0.2 });
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.09, 8, 28), ringMat);
  // ring in XY plane (default) -> vertical wheel facing Z. Good.
  spinPart.add(ring);
  // rungs
  const rungMat = new THREE.MeshStandardMaterial({ color: 0xffd166, flatShading: true, roughness: 0.5 });
  const N = 14;
  for (let i=0;i<N;i++){
    const a = (i/N)*Math.PI*2;
    const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.18, 6), rungMat);
    rung.rotation.x = Math.PI/2; // align along Z (axle)
    rung.position.set(Math.cos(a)*1.15, Math.sin(a)*1.15, 0);
    spinPart.add(rung);
  }
  g.add(spinPart);
  // stand
  const standMat = new THREE.MeshStandardMaterial({ color: 0xff9aa2, flatShading: true });
  // two vertical posts
  [1,-1].forEach(s => {
    const post = new THREE.Mesh(new THREE.BoxGeometry(0.12, 1.5, 0.12), standMat);
    post.position.set(0, 0.75, s*1.3);
    post.castShadow = true;
    g.add(post);
  });
  // axle
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.6, 8), standMat);
  axle.rotation.x = Math.PI/2; // along Z
  axle.position.y = 1.5;
  g.add(axle);
  // base feet
  [1,-1].forEach(s => {
    const foot = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.1, 0.5), standMat);
    foot.position.set(0, 0.05, s*1.3);
    g.add(foot);
  });
  scene.add(g);
  return { group: g, spin: spinPart };
}
```

Wait, the wheel ring is in XY plane (facing Z). The hamster runs inside at bottom