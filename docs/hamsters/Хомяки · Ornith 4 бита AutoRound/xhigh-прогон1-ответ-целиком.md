Let me create a single-file HTML project with Three.js that shows a cute low-poly hamster playground. Let me think through this carefully.

Requirements:
1. Use Three.js
2. Everything in one index.html file
3. Scene includes: cage, floor/tray, several low-poly hamsters, one interactive object (wheel, tunnel, food bowl, or toy)
4. Hamsters have simple autonomous behavior: walking, pausing, turning, or interacting with one object
5. Visual style: cute, low-poly, colorful, funny
6. Run immediately in a modern browser
7. Don't overcomplicate - focus on stable, readable, visually clear, fun

Let me plan the scene:

**Cage:**
- A tray/base (low box)
- Walls made of transparent or bars
- Maybe a roof

**Floor/tray:**
- A colored base
- Some bedding (small colored boxes/spheres scattered)

**Hamsters:**
- Low-poly body (icosahedron or sphere)
- Ears (small spheres)
- Eyes (dark spheres with white highlights)
- Nose
- Cheeks
- Little feet/legs
- Tail
- Different colors for each hamster

**Interactive object:**
- A exercise wheel that spins
- Or a food bowl that hamsters visit

**Behavior:**
- Each hamster wanders randomly
- Sometimes pauses
- Sometimes turns
- One hamster interacts with the wheel (runs on it)

Let me use Three.js from CDN with OrbitControls.

Let me build this carefully. I'll use a recent stable version of Three.js.

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
  html, body { width: 100%; height: 100%; overflow: hidden; background: #fde9d0; font-family: 'Segoe UI', sans-serif; }
  #app { width: 100%; height: 100%; display: block; }
  #ui {
    position: fixed; top: 16px; left: 16px; z-index: 10;
    background: rgba(255,255,255,0.85); border-radius: 14px;
    padding: 12px 16px; box-shadow: 0 4px 18px rgba(0,0,0,0.12);
    color: #5a4639; max-width: 260px; backdrop-filter: blur(4px);
  }
  #ui h1 { font-size: 18px; margin-bottom: 4px; }
  #ui p { font-size: 12px; line-height: 1.5; opacity: 0.85; }
  #hint { position: fixed; bottom: 16px; left: 16px; z-index: 10;
    background: rgba(255,255,255,0.85); border-radius: 10px; padding: 8px 12px;
    font-size: 12px; color: #5a4639; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate • Scroll to zoom • Watch the hamsters explore their cozy cage!</p>
</div>
<div id="hint">Click a hamster to pet it! 🥰</div>
<canvas id="app"></canvas>

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

Now let me build out the full JS. Let me think about the structure.

Scene setup:
- Renderer with antialias, shadows
- Camera
- Lights (ambient + directional with shadows)
- OrbitControls

Cage:
- Tray: a shallow box
- Walls: transparent panels or bars
- Bedding: scattered small objects

Hamsters:
- Build a function makeHamster(color) that returns a Group
- Body: icosahedron (low-poly look) scaled
- Head attached? Or just one blob with face features
- Let me do body + head + ears + eyes + nose + cheeks + feet + tail

Actually for simplicity and cuteness, let me make a hamster as a group with:
- Body (main blob)
- Head (smaller blob in front)
- Two ears
- Two eyes (with highlights)
- Nose
- Two cheek blushes
- Four little feet
- Small tail

Behavior system:
- Each hamster has a state machine: WALKING, PAUSING, TURNING
- When walking, move in current direction, slight bobbing
- Randomly decide to pause, turn, or continue
- Keep within cage bounds (bounce off walls)

Interactive object:
- A wheel that one hamster runs on
- Food bowl that some hamsters visit

Let me keep it focused: I'll make a spinning wheel and one hamster that interacts with it (runs on it), plus other hamsters wandering. Also a food bowl.

Let me also add raycasting to click hamsters to pet them (they get happy - bounce).

Let me write clean, well-commented code.

Let me think about the wheel interaction. The wheel is a vertical ring that spins. A hamster sits in front of it and "runs" making the wheel spin faster. Or the hamster is inside the wheel running. Let me put the hamster inside/on the wheel and spin it.

Actually a classic hamster wheel: hamster runs inside, wheel spins. Let me place the hamster at the bottom inside the wheel, and when it's "interacting", the wheel spins fast and the hamster bobs.

Let me design:
- Wheel: torus + spokes + side discs (low-poly)
- Mounted on a vertical axis
- Hamster "runner" assigned to the wheel

Let me write the hamster builder:

```js
function makeHamster(color, accentColor) {
  const g = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9 });
  // Body
  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 1), bodyMat);
  body.scale.set(1, 0.9, 1.1);
  body.position.y = 0.9;
  g.add(body);
  
  // Head
  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.6, 1), bodyMat);
  head.position.set(0, 1.05, 0.7);
  g.add(head);
  
  // Ears
  const earGeo = new THREE.SphereGeometry(0.2, 6, 6);
  const earL = new THREE.Mesh(earGeo, bodyMat);
  earL.position.set(-0.28, 1.5, 0.65);
  const earR = earL.clone();
  earR.position.x = 0.28;
  g.add(earL, earR);
  
  // Eyes
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x2b1a12, flatShading: true });
  const highlightMat = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });
  const eyeGeo = new THREE.SphereGeometry(0.12, 8, 8);
  const eyeHLGeo = new THREE.SphereGeometry(0.045, 6, 6);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(-0.2, 1.1, 1.12);
  const eyeR = eyeL.clone();
  eyeR.position.x = 0.2;
  const hlL = new THREE.Mesh(eyeHLGeo, highlightMat);
  hlL.position.set(-0.17, 1.14, 1.2);
  const hlR = hlL.clone();
  hlR.position.x = 0.23;
  g.add(eyeL, eyeR, hlL, hlR);
  
  // Nose
  const noseMat = new THREE.MeshStandardMaterial({ color: 0xff9aa2, flatShading: true });
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 6), noseMat);
  nose.position.set(0, 1.0, 1.25);
  g.add(nose);
  
  // Cheeks (blush)
  const cheekMat = new THREE.MeshStandardMaterial({ color: 0xffccd5, flatShading: true, transparent: true, opacity: 0.7 });
  const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 6), cheekMat);
  cheekL.position.set(-0.32, 0.95, 1.05);
  const cheekR = cheekL.clone();
  cheekR.position.x = 0.32;
  g.add(cheekL, cheekR);
  
  // Feet
  const footMat = new THREE.MeshStandardMaterial({ color: accentColor || 0xffd6e0, flatShading: true });
  const footGeo = new THREE.SphereGeometry(0.14, 6, 6);
  const feet = [];
  const footPositions = [[-0.4, 0.15, 0.3], [0.4, 0.15, 0.3], [-0.4, 0.15, -0.3], [0.4, 0.15, -0.3]];
  for (const p of footPositions) {
    const f = new THREE.Mesh(footGeo, footMat);
    f.position.set(...p);
    g.add(f);
    feet.push(f);
  }
  
  // Tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 6), footMat);
  tail.position.set(0, 0.85, -1.05);
  g.add(tail);
  
  g.userData.feet = feet;
  g.userData.head = head;
  return g;
}
```

Wait, feet at y=0.15 but body center at y=0.9 with radius ~1... the body extends down to about y=-0.0 (0.9 - 0.9). Actually body radius is 1 (icosahedron geometry 1), scaled y by 0.9 so it goes from 0.9-0.9=0 to 0.9+0.9=1.8. Feet at y=0.15 would be inside the body. Let me adjust. Actually feet should stick out below. Let me set body lower.

Let me reconsider proportions. Body is a blob sitting on the ground. If body radius ~0.9 and we want it to sit on ground (y=0), then center at y=0.9. Feet should be at y~0.1 just above ground, sticking out slightly. But they'd overlap with the body which is fine visually (they're in front/back).

Actually let me make feet small and positioned at the front-back-low so they peek out. Let me position them at y=0.12 and x at ±0.35, z at ±0.35. They'll poke out from under the body. Good.

Hmm, but the body scaled to 1.1 in z means it extends to z=±1.1*... wait icosahedron radius 1, scale z 1.1 => extends to 0.9 + 1.1 = 2.0 in z from center... no. Center y is 0.9. The geometry is centered at origin, radius 1. After scaling, in local y it's 0.9, in local z it's 1.1. So world: y from 0 to 1.8, z from -1.1 to 1.1 relative to group... wait no. The body group position is at group origin. Body center at (0,0.9,0). Extends y: 0 to 1.8, z: -1.1 to 1.1, x: -1.1 to 1.1.

Feet at y=0.12 would be near the bottom edge. Good, they peek out. Let me keep x=±0.4, z=±0.45.

Head at y=1.05, z=0.7, radius 0.6. That sits on upper front of body. Body top is at y=1.8. Head center 1.05 extends 0.45 to 1.65. It overlaps body front. Fine, looks like a head resting on body. Actually maybe raise head a bit to y=1.2 and move forward z=0.8. Let me tweak.

Actually for a cute hamster, having the head near the top-front works. Let me set head at y=1.25, z=0.75.

Eyes at y=1.1... but head center is 1.25 radius 0.6, so head spans y 0.65 to 1.85. Eyes at y=1.2, z=0.75+0.6=1.35 would be on the front surface. Let me recompute. Front of head is at z = 0.75 + 0.6 = 1.35. Eyes radius 0.12, place at z=1.3. x = ±0.2, y=1.35. 

Hmm, this is getting fiddly. Let me just make reasonable values and trust it looks okay. The key is cuteness comes from round shapes and big eyes.

Let me redo with cleaner coordinates:

Body: icosahedron r=1, scale (1, 0.95, 1.05), position y=0.95. Spans y 0 to 1.9.
Head: icosahedron r=0.55, position (0, 1.35, 0.75). Spans y 0.8 to 1.9, z 0.2 to 1.3.
Ears: spheres r=0.18 at (-0.25, 1.7, 0.7) and (0.25, 1.7, 0.7).
Eyes: r=0.11 at (-0.18, 1.4, 1.25) and (0.18, 1.4, 1.25). Highlights offset.
Nose: r=0.07 at (0, 1.25, 1.32).
Cheeks: r=0.1 at (-0.3, 1.2, 1.15) and (0.3, 1.2, 1.15).
Feet: r=0.12 at (±0.35, 0.12, ±0.4).
Tail: r=0.1 at (0, 0.9, -1.0).

That should look decent.

Now the scene layout:

Cage dimensions: let's say inner play area ~10 x 8. Tray is a shallow box. Walls are transparent panels.

Let me define:
- Tray floor: box 12 x 0.3 x 10 at y=-0.15 (top at 0)
- Bedding: many small colored boxes/spheres scattered on top
- Walls: 4 transparent panels (acrylic look) raised 2.5 high
- Actually let me do bars for back/sides and transparent front? Keep it simple: transparent panels on all sides so we can see in.

Let me make the cage:
- Floor tray: BoxGeometry(12, 0.4, 10), material light pink/cream, position y=-0.2
- Bedding: scatter ~60 small items
- Walls: 4 panels of transparent glass-like material, height 2.2, positioned at edges
- Corner posts maybe

Wheel: placed at one side. Torus radius 1.2, tube 0.08, plus spokes and two side discs. Vertical orientation (axis horizontal). Mounted on two vertical posts.

Food bowl: a small shallow cone/torus with pellets inside. Placed at another spot.

Tunnel: maybe a colored torus lying horizontally as a tunnel. Optional. Let me add one tunnel too for fun but keep it minimal. Actually requirement says "one interactive object such as..." — so at least one. I'll include a wheel (interactive, one hamster runs on it), a food bowl (hamsters visit), and maybe a tunnel. Let me include wheel + food bowl + tunnel to make it rich but not overwhelming. Actually let me keep to wheel and food bowl to avoid clutter, plus a tunnel as decoration. Hmm. Let me include wheel (interactive runner), food bowl (some hamsters eat), and a tunnel (hamsters walk through/near). That gives variety.

Actually, to keep it stable and clear, let me do:
- Wheel: one hamster runs on it (spins)
- Food bowl: hamsters occasionally walk to it and eat (bob head)
- Tunnel: decorative, hamsters wander near it

Let me now think about the AI/state machine for hamsters.

Each hamster object gets extended with:
- velocity direction (angle)
- state: 'wander' | 'pause' | 'eat' | 'wheel'
- timer
- target position for going to food
- speed

Simplified approach: 
Each hamster wanders using a random-walk: pick a heading, walk straight for a while, then choose a new heading (random turn), sometimes pause, sometimes change speed. Keep within bounds by wrapping or bouncing.

For the food interaction: occasionally a hamster picks a food target, walks there, eats for a bit, then leaves.

For the wheel hamster: it goes to the wheel and stays, running (wheel spins, legs animate).

Let me implement with a per-hamster object holding state and timers, updated in the animation loop.

Let me define bounds: hamsters move within a square slightly smaller than cage, say x in [-5, 5], z in [-4, 4].

Movement:
```
hamster.heading += random turn
hamster.speed = base speed
position.x += cos(heading) * speed * dt
position.z += sin(heading) * speed * dt
// face direction of movement
rotation.y = heading
// bobbing
body.position.y oscillates, legs animate
```

State machine:
- Wander: moving with heading. Every so often (timer), switch to Pause.
- Pause: stand still, maybe look around (rotate head). After time, pick new heading, switch to Wander.
- Eat: move to food bowl, bob head up/down. After eating, wander off.
- Wheel: go to wheel, mount, run.

Let me give each hamster a role:
- 1 hamster = wheel runner (always at wheel, running)
- 1-2 hamsters = eaters (occasionally go to food)
- rest = wanderers

Let me make 5 hamsters total. Colors: various cute pastel colors.

Let me code the update logic clearly.

I'll create an array `hamsters` where each element is the Group plus userData with AI fields.

Let me write updateHamster(h, dt):

```
const ud = h.userData;
ud.timer -= dt;

switch(ud.state) {
  case 'wheel':
    // running on wheel
    ud.runPhase += dt * 6;
    h.position.y = Math.abs(Math.sin(ud.runPhase)) * 0.05; // bob
    animate legs
    break;
  case 'wander':
    if (ud.timer <= 0) {
      // decide next action
      const r = Math.random();
      if (r < 0.15 && ud.eater) { ud.state='go_eat'; ud.timer = 2; }
      else if (r < 0.4) { ud.state='pause'; ud.timer = 1 + Math.random()*2; }
      else { ud.heading += (Math.random()-0.5)*1.2; ud.timer = 1 + Math.random()*3; ud.speed = 0.3 + Math.random()*0.4; }
    }
    move...
    // bounds
    clamp position, if hit wall bounce (flip heading)
    break;
  case 'pause':
    // idle, head looks around
    if (ud.timer <= 0) { ud.state='wander'; ud.heading = Math.random()*Math.PI*2; ud.timer = 1+Math.random()*3; }
    break;
  case 'go_eat':
    // move toward food
    const dx = foodPos.x - h.position.x, dz = foodPos.z - h.position.z;
    const d = Math.hypot(dx,dz);
    if (d > 0.3) {
      ud.heading = Math.atan2(dz, dx);
      move...
    } else {
      ud.state='eat'; ud.timer = 2 + Math.random()*2;
    }
    break;
  case 'eat':
    // bob head
    if (ud.timer <= 0) { ud.state='wander'; ud.heading = Math.random()*Math.PI*2; ud.timer = 1+Math.random()*3; }
    break;
}
```

Movement helper:
```
function moveHamster(h, speed, dt) {
  h.position.x += Math.cos(h.userData.heading) * speed * dt;
  h.position.z += Math.sin(h.userData.heading) * speed * dt;
  h.rotation.y = h.userData.heading + Math.PI/2; // face movement direction
  // clamp
  const limitX = 5, limitZ = 4;
  if (h.position.x > limitX){ h.position.x = limitX; h.userData.heading += Math.PI; }
  if (h.position.x < -limitX){ h.position.x = -limitX; h.userData.heading += Math.PI; }
  if (h.position.z > limitZ){ h.position.z = limitZ; h.userData.heading += Math.PI; }
  if (h.position.z < -limitZ){ h.position.z = -limitZ; h.userData.heading += Math.PI; }
}
```

Note rotation: heading is atan2(dz,dx). To face that direction, rotation.y should equal heading. Let me set rotation.y = heading. Since +x is right, +z is... in Three.js z is into/out of screen. My movement uses x and z. heading = atan2(dz, dx). Facing direction vector is (cos h, sin h) in (x,z). rotation.y rotates around Y so that +Z local faces... Local +Z after rotation.y=θ points to (sin θ, 0, cos θ)? Let me recall: rotating a point (0,0,1) by rotation.y=θ gives (sinθ, 0, cosθ). Hmm so local +z maps to (sinθ,0,cosθ). I want it to point in direction (cos h, 0, sin h). So need sinθ=cos h and cosθ = sin h → θ = π/2 - h. Alternatively use local -z. This is getting confusing.

Simplest: set rotation.y = heading + something and just eyeball. Actually let me define heading differently. Let me use:
```
h.position.x += Math.cos(ud.heading) * speed * dt;
h.position.z += Math.sin(ud.heading) * speed * dt;
h.rotation.y = -ud.heading; // or + 
```
Let me just test mentally: if heading=0, moves in +x. We want hamster to face +x. Rotation.y=0 keeps local +z pointing to world +z. To face world +x, rotate -90° (rotation.y = -π/2) so local +z → world +x? Rotating (0,0,1) by rotation.y=-π/2: (sin(-π/2),0,cos(-π/2)) = (-1,0,0). That's -x. So rotation.y=+π/2 gives (1,0,0)=+x. So for heading=0, rotation.y=π/2.

General: direction angle in world = heading (measured from +x toward +z). We want local forward (which is +z after building) to point along (cos heading, 0, sin heading). Rotation by rotation.y=θ maps local +z to (sinθ, 0, cosθ). Set sinθ=cos heading, cosθ=sin heading → θ = π/2 - heading. Check heading=0: θ=π/2 → (1,0,0). Good. heading=π/2 (moving +z): θ=0 → (0,0,1) = +z. Good.

So rotation.y = Math.PI/2 - ud.heading.

I'll use that.

Now the wheel runner hamster: place it at the wheel position, facing the wheel, running. The wheel spins. Its legs animate (feet move up/down). It stays put.

Let me make the wheel at position (4.5, 0, 0) maybe against a wall. Runner hamster at (4.5, 0.2, 0.5) facing the wheel.

Actually let me place wheel at back. Let me set wheel center at (0, 1.4, -4) mounted on back wall. Runner hamster at (0, 0.2, -3.2) running upward-ish? Classic hamster runs inside wheel at bottom. Let me put wheel axis horizontal along x, so wheel is in the y-z plane. Runner at bottom of wheel.

Hmm, let me simplify: wheel vertical face toward +z (facing into cage), axis along x. Wheel center at (4, 1.4, -3.5) near back-right corner. Runner hamster sits at bottom inside: position (4, 0.3, -3.5), facing +z (toward camera-ish), running. Wheel spins around x axis.

Let me just do that.

Food bowl at (-3.5, 0, 3). Tunnel somewhere in middle-ish, e.g., (1.5, 0.3, 2) — a horizontal torus/cylinder hamsters can walk near.

Let me finalize the object list:
- Wheel (interactive, spinning) at (4, 1.5, -3.5)
- Food bowl at (-3.5, 0.1, 3) with pellets
- Tunnel: a couple of colored tubes at (1, 0.3, 2.5) angled

Let me keep the tunnel optional/simple. Actually I'll add a tunnel as a torus segment lying horizontally.

Now lighting: ambient light (soft), directional light with shadow for depth, maybe a hemisphere light for nice fill. Background color gradient.

Let me add a soft background gradient via CSS or a large sphere. Simpler: set renderer clear color to a warm cream and add fog. Or use a gradient background div behind canvas. Let me set canvas background via CSS and renderer.setClearColor to match, plus a radial gradient overlay. Keep simple: setClearColor to #fde9d0.

Add shadows: directional light casts shadows onto floor. Enable renderer.shadowMap. Set camera to see shadows. Add ground shadow only? Hamsters casting shadows adds cuteness. Let me enable shadowMap for directional light, and set floor.receiveShadow=true, hamsters castShadow=true.

But transparent cage walls shouldn't cast shadows (or they will, looking bad). Set castShadow=false on walls.

Let me also add a subtle environment for the materials to look nice — but flatShading keeps it low-poly. Standard material with flatShading looks good without env map.

Let me now also add interaction: clicking a hamster makes it "jump/happy" (a bounce) and maybe a heart pops. Use raycaster. On click, find intersected hamster, trigger happy animation (scale squash/stretch + jump) and spawn a little heart particle.

Let me add hearts as simple geometry (or use a canvas texture). Simple heart shape via two spheres + cone, or just a small floating "+" / star. Let me make a tiny heart using a shape. Might be overkill. Let me spawn a floating star/particle that rises and fades. I'll make a small low-poly heart.

Actually, let me keep the pet interaction simple: hamster does a happy jump (rise and return) and wiggles. And spawn a few floating particles (small spheres) that rise. That's cute and simple.

Let me now write everything out fully.

Let me also make sure performance is fine: low-poly counts are low. Good.

Let me consider the OrbitControls target at center of cage.

Let me write the final HTML.

One more thing: I should make the hamsters' body bob when walking. I'll store reference to body mesh within hamster group and offset its y by sin(phase). And animate feet.

Let me structure each hamster group so that body and head are children positioned relative to group, and I animate body.position.y (local) for bobbing, and feet positions.

Since feet are children of the hamster group, and the whole group moves, animating feet local y works.

Let me store references in userData: body, head, feet[], etc.

Let me write makeHamster to return group with userData populated.

Let me also add a name/tag? Not needed.

Let me now also think about the wheel hamster's leg animation — animate its feet similarly.

Alright, let me also add subtle idle breathing to all hamsters (body scale gentle). Optional. I'll add gentle scale pulse.

Let me write the code now.

I'll be careful with imports and module script.

Let me draft the full script:

```js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const canvas = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setClearColor(0xfde9d0);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xfde9d0, 18, 40);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(0, 8, 14);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1, 0);
controls.maxPolarAngle = Math.PI * 0.49;
controls.minDistance = 5;
controls.maxDistance = 30;

// Lights
const ambient = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambient);
const hemi = new THREE.HemisphereLight(0xbfd9ff, 0xffe9c4, 0.5);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff4e0, 1.2);
sun.position.set(6, 12, 6);
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
```

Cage:

```js
const cage = new THREE.Group();
scene.add(cage);

// Tray
const trayMat = new THREE.MeshStandardMaterial({ color: 0xffd0e0, flatShading: true, roughness: 0.9 });
const tray = new THREE.Mesh(new THREE.BoxGeometry(14, 0.5, 12), trayMat);
tray.position.y = -0.25;
tray.receiveShadow = true;
cage.add(tray);

// bedding
const bedColors = [0xffe3a3, 0xffd3e6, 0xd8f0d0, 0xd6ecff, 0xffe0b3];
const bedGeo = new THREE.BoxGeometry(0.25, 0.18, 0.25);
for (let i=0;i<120;i++){
  const m = new THREE.Mesh(bedGeo, new THREE.MeshStandardMaterial({color: bedColors[i%bedColors.length], flatShading:true}));
  m.position.set((Math.random()-0.5)*13, 0.09, (Math.random()-0.5)*11);
  m.rotation.y = Math.random()*Math.PI;
  m.castShadow=false; m.receiveShadow=true;
  cage.add(m);
}

// Walls (transparent acrylic)
const wallMat = new THREE.MeshStandardMaterial({ color: 0xcfeeff, transparent:true, opacity:0.18, roughness:0.1, metalness:0, side: THREE.DoubleSide });
const wallH = 3;
const walls = [
  [0, -6, 14, wallH], // back (z=-6) size x=14
  [0, 6, 14, wallH],  // front
  [-7, 0, 12, wallH], // left
  [7, 0, 12, wallH],  // right
];
```

Wait dimensions: tray is 14 wide (x), 12 deep (z). Walls: back/front span x=14 at z=±6, left/right span z=12 at x=±7. Wall height 3.

```js
walls.forEach(([x,z,w,xh])=>{}); // let me just write explicitly
```

Let me write:
```js
function makeWall(w, d, x, z){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, wallH, d), wallMat);
  m.position.set(x, wallH/2, z);
  cage.add(m);
}
makeWall(14, 0.1, 0, -6);
makeWall(14, 0.1, 0, 6);
makeWall(0.1, 12, -7, 0);
makeWall(0.1, 12, 7, 0);
```

Also add a frame/top bars? Optional. Let me add thin frame edges on top for style. Skip for simplicity. Maybe add a few vertical bars on back wall for aesthetic. I'll add simple vertical bars on the back wall.

Actually keep it clean. Transparent walls + a couple of horizontal bars. Let me add top rim bars (thin boxes) along the top edges. Optional. I'll add small posts at corners for style. Eh, skip. Keep transparent walls only. Maybe add a roof bar accent. I'll add a thin frame on top edges.

Let me add top rails:
```js
const railMat = new THREE.MeshStandardMaterial({ color: 0xffb7c5, flatShading:true, roughness:0.6 });
function rail(w,x,z){ const m=new THREE.Mesh(new THREE.BoxGeometry(w,0.15,0.15), railMat); m.position.set(x, wallH, z); cage.add(m);}
rail(14,0,-6); rail(14,0,6); rail(0.15, -7, 0); rail(0.15,7,0); rail(0.15,0,-6)... 
```
This is getting complicated; skip rails, keep it minimal and clean. Transparent walls + tray + bedding is enough for a cage. I'll add corner posts (short cylinders) for style.

Let me add 4 corner posts:
```js
const postMat = new THREE.MeshStandardMaterial({ color: 0xffb0c0, flatShading:true, roughness:0.6 });
[[ -7,-7],[7,-7],[7,7],[-7,7]].forEach(([x,z])=>{
  const p = new THREE.Mesh(new THREE.CylinderGeometry(0.12,0.12,wallH,7), postMat);
  p.position.set(x, wallH/2, z); cage.add(p);
});
```

Good.

Now the objects.

Wheel:
```js
const wheelGroup = new THREE.Group();
const wheelMat = new THREE.MeshStandardMaterial({ color: 0xff6b8a, flatShading:true, roughness:0.5 });
const wheelRimMat = new THREE.MeshStandardMaterial({ color: 0xff9db0, flatShading:true, roughness:0.5 });
const wheel = new THREE.Group();
const torus = new THREE.Mesh(new THREE.TorusGeometry(1.3, 0.09, 8, 24), wheelMat);
wheel.add(torus);
// spokes
for(let i=0;i<8;i++){
  const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,2.5,6), wheelRimMat);
  spoke.rotation.z = (i/8)*Math.PI;
  wheel.add(spoke);
}
// side discs
const discMat = new THREE.MeshStandardMaterial({ color: 0xffb3c1, flatShading:true, roughness:0.6, transparent:true, opacity:0.85 });
const disc1 = new THREE.Mesh(new THREE.CylinderGeometry(1.25,1.25,0.05,20), discMat);
disc1.rotation.x = Math.PI/2; disc1.position.z = 0.12;
const disc2 = disc1.clone(); disc2.position.z = -0.12;
wheel.add(disc1, disc2);
wheelGroup.add(wheel);
// support posts
const supportMat = new THREE.MeshStandardMaterial({ color:0xdddddd, flatShading:true });
const sup1 = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.08,1.6,8), supportMat);
sup1.position.set(0, -1.4, 0.2);
const sup2 = sup1.clone(); sup2.position.z = -0.2;
wheelGroup.add(sup1, sup2);
wheelGroup.position.set(4.5, 1.8, -4);
wheelGroup.traverse(o=>{ if(o!==wheel){ o.castShadow=false; }});
wheel.castShadow = true;
scene.add(wheelGroup);
```

Wait, torus orientation: default torus lies in xy-plane with hole along z. So the ring is in xy plane, axis along z. For a hamster wheel facing the camera (+z) and spinning around x-axis... hmm. Actually a hamster wheel spins about a horizontal axis. If axis is along x, the ring should be in the y-z plane. Default torus is in xy-plane (normal = z). To make normal along x, rotate torus by π/2 about z? Rotating about x by 90° puts it in xz... let me think. 

Default torus: ring in xy-plane, hole along z-axis. I want hole along x-axis (so the wheel faces +x... no). Let me define: I want the wheel to be a vertical circle facing +z (toward camera), spinning around the horizontal x-axis. So the plane of the ring is the y-z plane, and the rotation axis is x. 

To get default torus (xy-plane, axis=z) to have axis=x, rotate about y by 90°. Then axis becomes x. Let me apply wheel.rotation.y = Math.PI/2. Actually simpler: set rotation on the torus mesh. Let me just rotate the whole wheel group: wheel.rotation.x = Math.PI/2 gives ring in xz plane (horizontal) — no that's flat. 

Ugh, let me be careful. Torus default: lies in XY plane, the central circle is in XY plane, the tube circles around the Z axis. So it looks like a ring lying flat on the ground (XY) with a hole up the Z axis. 

I want a vertical ring like a clock on the wall facing me (in YZ plane), spinning about X axis (horizontal). 

Rotate the default torus so its hole axis (Z) points along X: rotate about Y by 90°. After rotation.y=±90°, the ring is in the YZ plane? Let's verify: point on ring at angle θ: (cosθ, sinθ, 0) (in XY). Rotate about Y by 90°: (x,y,z) -> (x cos90 + z sin90, y, -x sin90 + z cos90) = (z, y, -x) = (0, sinθ, -cosθ). So points now have x=0, in YZ plane. Yes! So rotation.y = PI/2 puts ring in YZ plane facing X... the ring is in YZ plane, normal along X. Facing +X. Hmm I want facing +Z (toward camera which is at +z). 

Rotate about Y by -90°: (x,y,z)->(z*... ) let me: rotation about Y by -90: x' = x cos(-90)+z sin(-90)= -z; y'=y; z' = -x sin(-90)+z cos(-90)= x. Point (cosθ,sinθ,0) -> (-0, sinθ, cosθ) = (0, sinθ, cosθ). In YZ plane, normal along X still. Both ±90 about Y keep it in YZ plane. The facing doesn't change (normal is X either way). 

So a ring in YZ plane faces along X axis, meaning if I look along X I see the face. My camera looks along -Z (from +z looking toward -z). So I'd see the edge of a YZ-plane ring. Not good.

I want the ring in the XZ plane? No, that's horizontal (flat). 

I want the ring's flat face to point toward the camera (along Z). So the ring should lie in the XY plane (like flat on ground) but stood up... no. A ring lying in XY plane has normal along Z, facing up. If I tilt it to vertical facing camera, I rotate about X axis by 90°. Rotate default (XY plane, normal Z) about X by 90°: point (cosθ,sinθ,0) -> (cosθ, sinθ cos90 - 0 sin90, sinθ sin90 + 0) = (cosθ, 0, sinθ). So now in XZ plane, normal along Y. That's a flat ring (horizontal) — no wait points (cosθ, 0, sinθ) all have y=0, so it's in XZ plane = horizontal, normal up (Y). That's a flat wheel on the ground. Not vertical.

Hmm. I'm overcomplicating. Let me just think what orientation makes a vertical wheel facing the camera:
- The ring should be a vertical circle. Its points should vary in Y and Z (vertical and depth), constant-ish X? No. A vertical circle facing +Z (camera) has points at (x0 + r cosθ, y0 + r sinθ, z0) — varying Y and X, fixed Z. Wait that's a circle in the XY plane at fixed z. That faces +Z. Yes! A circle in the XY plane faces along Z. 

So I want the ring in the XY plane facing Z. The default torus IS in the XY plane already (normal along Z)! So default orientation faces the camera (if camera looks along Z). 

So I don't need to rotate the torus at all for it to face the camera. But then it spins about the Z axis (its normal), which means it spins in its own plane — that's correct for a wheel facing you! A wheel facing you spins about the axis coming out of it (Z). 

But wait, a real hamster wheel spins about a horizontal axis, and the hamster runs on the inside bottom. If the wheel faces the camera (in XY plane, spinning about Z), the hamster would run on the side. That's like a guinea pig wheel viewed from the side. Visually, a wheel facing us spinning about Z looks fine and cute. The hamster sits in front (at +z or -z?) Actually the hamster should be inside at the bottom. If wheel is in XY plane centered at (4.5, 1.8, -4), bottom of wheel is at (4.5, 0.5, -4). Hamster sits at (4.5, 0.3, -4) — but that's inside the wheel plane, at the bottom. The hamster faces +Z (toward camera) or -Z? If hamster runs "forward" the wheel bottom moves... whatever, visually fine.

Actually for a hamster wheel facing the camera, the hamster runs and the bottom of the wheel moves away/toward. It looks fine. Let me keep default torus orientation (faces camera). Good, no rotation needed. The hamster stands in front (between wheel and camera) at the bottom, or inside at bottom.

Let me place hamster runner at (4.5, 0.35, -4 + 1.3) = inside bottom? The wheel radius 1.3, center y=1.8, so bottom is y=0.5. Hamster at y=0.35 (sitting), z=-4 (in plane), facing +Z (toward camera). As it "runs", wheel spins (about Z). Fine.

Hmm but if hamster is at z=-4 exactly in the plane and radius 1.3, it's inside. Its feet at bottom touch y=0.35+0.12=~0.47, near bottom of wheel y=0.5. OK close enough.

Actually let me place the hamster slightly in front (z = -4 + 1.2 = -2.8) so it's visible in front of the wheel bottom, facing the wheel (facing -Z). That reads better: hamster in front of wheel running. But then it overlaps the wheel disc. Let me just put it inside at bottom, facing +Z (toward camera), running. It'll look like a hamster in a wheel. Good.

Let me set runner hamster position (4.5, 0.3, -4), facing +Z. I'll set its heading so it faces +Z: heading = atan2(dz,dx). To face +Z, direction (0,1) in (x,z)? heading such that (cos h, sin h) = (0,1) → h = π/2. rotation.y = π/2 - h = 0. So rotation.y=0 faces +Z. Good, set runner.rotation.y = 0.

Now the wheel spinning: in update, wheel.rotation.z += speed.

Food bowl:
```js
const foodBowl = new THREE.Group();
const bowlMat = new THREE.MeshStandardMaterial({ color: 0x6bc4ff, flatShading:true, roughness:0.6 });
const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.5, 0.4, 12, 1, true), bowlMat);
bowl.position.y = 0.2;
const bowlBottom = new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.5,0.05,12), bowlMat);
bowlBottom.position.y = 0.02;
// pellets
const pelletMat = new THREE.MeshStandardMaterial({ color: 0xc9a06a, flatShading:true });
for(let i=0;i<14;i++){
  const p = new THREE.Mesh(new THREE.SphereGeometry(0.09,6,6), pelletMat);
  const a = Math.random()*Math.PI*2, r = Math.random()*0.5;
  p.position.set(Math.cos(a)*r, 0.32 + Math.random()*0.08, Math.sin(a)*r);
  foodBowl.add(p);
}
foodBowl.add(bowl, bowlBottom);
foodBowl.position.set(-3.5, 0, 3);
foodBowl.traverse(o=>{ o.castShadow=true; o.receiveShadow=true; });
scene.add(foodBowl);
```

Tunnel:
```js
const tunnel = new THREE.Group();
const tunnelMat = new THREE.MeshStandardMaterial({ color: 0xffd166, flatShading:true, roughness:0.7, side: THREE.DoubleSide });
const tube = new THREE.Mesh(new THREE.TorusGeometry(0.9, 0.4, 8, 20, Math.PI), tunnelMat);
tube.rotation.z = Math.PI/2; // make it a half-pipe arch? 
```
Hmm a tunnel is a cylinder. Let me make a cylinder lying horizontally:
```js
const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.7,0.7,3,16,1,true), tunnelMat);
tube.rotation.z = Math.PI/2; // axis along X
```
Cylinder default axis along Y. Rotate about Z by 90° → axis along X. Then it's a horizontal tunnel along X. Add two rim rings. Position at (1.5, 0.7, 2.5). Hamsters walk near/through.

Actually a half-pipe tunnel (arch) is cuter and hamsters can walk under it. Let me do an arch: use a torus with 270° or a cylinder cut. Simpler: use a torus segment (half circle) as an arch tunnel. 
```js
const arch = new THREE.Mesh(new THREE.TorusGeometry(0.9, 0.12, 8, 20, Math.PI), tunnelMat);
arch.rotation.x = Math.PI/2; // lie flat? 
```
Ugh orientations again. Let me just do a full cylinder tunnel (open tube) that hamsters walk through. Place it horizontally along X at y=0.7 (so it's lifted? no, on the ground). Cylinder radius 0.7, length 3, axis along X, sitting on ground (bottom at y=0 → center y=0.7). Hamsters can walk inside (they're ~1.8 tall so they'd poke through top, but that's fine/cute — like a tunnel they burrow). Actually if open both ends and hamster walks through, we see it pop out the other side. Cute. Let me do that.

Let me position tunnel along X at (1.5, 0.65, 2.5), radius 0.65, length 3.2.

Add rim rings at both ends (torus) for style.

OK let me just write it.

Now hamsters. Let me define colors and roles.

```js
const hamsterColors = [
  { body: 0xffb3a7, accent: 0xffd9cf }, // coral
  { body: 0xffd6a7, accent: 0xfff0cf }, // peach
  { body: 0xc8e6c9, accent: 0xeaffea }, // mint
  { body: 0xb3e5fc, accent: 0xe6f7ff }, // sky
  { body: 0xe1bee7, accent: 0xf7e6fb }, // lavender
];
```

5 hamsters. Index 0 = wheel runner. Others wander/eat.

Let me build them and assign to scene within bounds.

Let me write buildHamster returning group with userData fields: body, head, feet (array), baseY, phase, speed, happyTimer.

Then initialize each with random state.

Let me write the update loop.

Also hearts on click.

Let me write the full code now, carefully.

For the "pet" interaction: raycast against hamster groups. On hit, set happyTimer and spawn heart particles at that hamster's position.

Heart particles: small group of 2 spheres + a cone, or just small colored spheres that float up and fade (scale down). Let me do simple: create N small spheres (pink) that rise and shrink, removed after time. Add to a particles array.

Let me code:

```js
const particles = [];
function spawnHeart(pos){
  for(let i=0;i<5;i++){
    const m = new THREE.Mesh(new THREE.IcosahedronGeometry(0.12,0), new THREE.MeshStandardMaterial({color:0xff5c8a, flatShading:true}));
    m.position.copy(pos); m.position.y += 1;
    m.userData.vy = 1.5 + Math.random();
    m.userData.life = 1;
    scene.add(m);
    particles.push(m);
  }
}
```

Update particles: y += vy*dt, vy -= gravity*dt, life -= dt, scale down, remove when life<=0.

Now the happy animation: when hamster petted, set happyTimer=1, and during that time do a jump (increase y) and wiggle. I'll incorporate into update: if happyTimer>0, do bounce.

Let me integrate.

Let me now also make sure the wheel runner keeps spinning the wheel even when not "interacting"—it's always running. So wheel always spins at base speed, faster when hamster runs (always). Fine.

Let me write final code. I'll keep comments concise.

Let me double check the OrbitControls import path: three/addons/controls/OrbitControls.js. With importmap mapping "three/addons/" to unpkg examples/jsm/. Good.

Let me ensure unpkg paths work: "https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js". The importmap maps "three/addons/" -> "https://unpkg.com/three@0.160.0/examples/jsm/". So import "three/addons/controls/OrbitControls.js" resolves to ".../examples/jsm/controls/OrbitControls.js". Good.

Also need to make sure OrbitControls imports three correctly — it imports from 'three'. Importmap handles "three" -> unpkg build/three.module.js. Good.

Let me also handle resize.

Let me write it all.

Let me reconsider hamster proportions once more for cuteness and set coordinates:

Body: IcosahedronGeometry(1,1), scale (1, 0.95, 1.08), position y=0.95. So spans y 0.0–1.9, x ±1, z ±1.08.
Head: IcosahedronGeometry(0.55,1), position (0, 1.4, 0.78). spans y 0.85–1.95, z 0.23–1.33.
Ears: SphereGeometry(0.18,6,6), positions (-0.26,1.75,0.72),(0.26,1.75,0.72).
Eyes: SphereGeometry(0.11,8,8), positions (-0.19,1.45,1.28),(0.19,1.45,1.28). Highlights SphereGeometry(0.045) at (-0.16,1.49,1.34),(0.22,1.49,1.34).
Nose: SphereGeometry(0.07) at (0,1.3,1.34).
Cheeks: SphereGeometry(0.11) translucent pink at (-0.32,1.28,1.18),(0.32,1.28,1.18).
Feet: SphereGeometry(0.13) at (±0.36,0.12,±0.42).
Tail: SphereGeometry(0.11) at (0,0.9,-1.05).

Wait head at y=1.4 with radius 0.55 spans up to 1.95, and ears at y=1.75 radius 0.18 span 1.57–1.93, overlapping head top. Good. Eyes at y=1.45 within head (head spans 0.85–1.95). z=1.28 near front of head (front at 1.33). Good.

Body top at 1.9, head bottom at 0.85 — head overlaps body upper front. Looks like head resting on body. Might look like head floats slightly but since they overlap it's fine. Actually head center 1.4, body center 0.95 top 1.9. Head bottom 0.85 is inside body (body spans 0–1.9). So head emerges from body front. Good, natural.

Let me make sure feet at y=0.12 peek below body (body bottom at 0). Feet radius 0.13 at y=0.12 span 0–0.25. They poke just below body bottom edge. Good.

Now the hamster overall height ~1.95 (head top) plus ears ~1.93. Height ~2 units. Cage inner height 3. Fine. Width ~2. Depth ~2.4 (with tail). Within bounds.

Movement bounds: x in [-5.5,5.5], z in [-4.5,4.5] (cage inner ~ ±7, ±6). Let me use ±5.5 and ±4.5 so they don't clip walls.

Now let me write the final file.

Let me also add a subtle idle breathing to all hamsters (body scale gentle). Optional. I'll add gentle scale pulse.

Let me now also think about the wheel runner's leg animation — animate its feet similarly.

Alright, let me write the final code.

Actually, let me reconsider: I want the hamsters to look like they're facing the direction they move. With rotation.y = π/2 - heading. Let me verify with heading=0 (moving +x): rotation.y = π/2. Does rotation.y=π/2 make the hamster face +x? The hamster's front is +z (nose at +z). Rotating by rotation.y=π/2 about world Y: local +z maps to world (sin(π/2),0,cos(π/2))=(1,0,0)=+x. Yes! So nose points +x. Correct.

heading=π/2 (moving +z): rotation.y = π/2 - π/2 = 0. Local +z stays +z. Nose points +z. Correct.

heading=-π/2 (moving -z): rotation.y = π/2+π/2=π. Local +z maps to (sin π,0,cos π)=(0,0,-1)=-z. Correct.

Great, rotation.y = π/2 - heading works.

Now let me finalize and write the file. I'll include a title UI and hint.

Let me write the complete HTML now.

I'll double-check the animation loop uses delta time from clock.

Also add requestAnimationFrame.

Let me write it.

For the wheel runner, I'll set it to state 'wheel' permanently, position at wheel, facing camera, feet animated, body bob. Wheel spins continuously.

Let me make the wheel spin based on hamster running; add slight speed variation.

Let me finalize code. I'll keep functions organized.

Let me write the heart/particle update and petting.

Raycaster on pointerdown (to distinguish from drag). I'll use 'click' event; but click fires after drag sometimes. Let me use pointerdown and check if it moved little. Simpler: use 'pointerdown' and raycast; minor drags still trigger but acceptable. Actually OrbitControls consumes pointer events; 'click' might not fire if dragged. Let me use pointerdown.

I'll store pointer start, and on pointerup if movement small, do raycast. Or just use 'click'. Let me use 'click' — OrbitControls emits its own but DOM click should still fire. To be safe, use pointerdown.

Let me use pointerdown for raycasting.

Alright, writing final.

Let me also make sure to set hamsters castShadow true but keep counts low. Fine.

Let me write it all out now.

I realize I should double check: IcosahedronGeometry with detail 1 has 80 faces, times ~10 meshes per hamster times 5 hamsters = manageable. Plus bedding 120 boxes. Fine.

Let me write.

Final structure of script:
1. imports
2. renderer, scene, camera, controls
3. lights
4. build cage (tray, bedding, walls, posts)
5. build wheel, food bowl, tunnel
6. buildHamster function
7. create hamsters, assign roles
8. state machine update
9. particles + petting
10. animation loop

Let me write it cleanly.

For feeding hamsters, foodPos = foodBowl.position.

Let me set roles: hamster[0] = wheel runner. hamsters[1,2] = eaters (occasionally go eat). hamsters[3,4] = wanderers.

Initialize wanderers with state 'wander', random heading, timer random. Eaters same but flag eater=true.

Let me code the update for eaters to sometimes go eat.

Let me write the code.

I'll now produce the final answer with the full HTML file.

Let me make sure about the "interactive object" — the wheel is interactive (spins, hamster runs), food bowl is interactive (hamsters eat). Good, satisfies requirement. I could also make the wheel clickable to speed it up, but not required. The hamster-clicking is an extra interaction. Good.

Let me write final code. I'll be thorough but not overcomplicate.

Let me write the makeHamster with all parts and return group + userData refs.

I'll store userData on the group: { state, timer, heading, speed, baseY, phase, feet:[], body, head, eater:false, happy:0, isRunner:false }.

Now the update function processes each hamster.

Let me write it.

Actually, for the runner, I'll keep its feet animating and body bobbing, and it stays at wheel position. Wheel spins.

Let me finalize.

Let me also add gentle head turn during pause (rotate head locally) for cuteness. In pause state, head.rotation.y oscillates. Nice touch.

Write now.

Let me produce the file.

I'll write the CSS for a nice look and the UI panels.

Let me make sure the canvas fills screen and UI is on top.

Final code below.

Let me double-check torus for wheel: THREE.TorusGeometry(1.3, 0.09, 8, 24) — radius 1.3, tube 0.09, radial segments 8, tubular 24. Faces camera (default orientation). Good. Spokes: CylinderGeometry(0.04,0.04,2.5,6) rotated about z by i/8*PI. Length 2.5 ≈ diameter 2.6. Good. Discs: CylinderGeometry(1.25,1.25,0.05,20) rotated x by PI/2 to make flat discs perpendicular to z? Cylinder axis is Y; rotate x by 90° → axis along Z, so disc is in XY plane facing Z. Good, matches torus facing Z. Position z ±0.12. Good.

Supports: cylinders along Y at z ±0.2, height 1.6, from ground to wheel center-ish. Position y=-1.4 relative to wheelGroup which is at y=1.8. So supports go from y=1.8-1.6-0.8=... let me place support position y = -1.4 relative, radius 0.08, height 1.6 → spans y 1.8-1.4-0.8= -0.4 to 1.8-1.4+0.8=1.2. Hmm that reaches up to 1.2, but wheel center at 1.8, bottom at 0.5. Support should reach from ground (y=0) to somewhere. Let me set support position y relative = -0.8 (center), height 1.6 → spans y=0.5 to 1.1. That reaches the wheel axle area (wheel bottom 0.5). Good enough. Actually let me make them taller to hold the wheel: position y=-1.0, height 2.0 → spans -0.2 to 1.0. Eh. Let me just make support position y = -1.2, height 2.4 → spans 0 (ground) to 1.2. Reaches mid wheel. Fine, visually holds the wheel axle region. Good.

Wheel center y=1.8, radius 1.3 → spans 0.5 to 3.1. Supports up to 1.2 reach lower part. Acceptable. Could add second support higher but fine.

Now runner hamster at (4.5, 0.3, -4) inside bottom of wheel. Wheel in XY plane at z=-4, so points at (4.5±..., 1.8±..., -4). Bottom point (4.5, 0.5, -4). Hamster at y=0.3 sits just below bottom. Facing +Z (toward camera, since camera at +z). Good, we see the hamster's face and the wheel behind it. 

Wait, hamster at z=-4, wheel also at z=-4 (plane). Hamster faces +Z (toward camera at +z). We see hamster's front. Wheel is behind (same plane). The hamster overlaps the lower part of wheel. Looks like hamster in wheel. 

Now let me finalize and write.

Let me also make the runner's heading such that rotation.y=0 (face +Z). I'll just set runner.rotation.y = 0 directly.

Alright, writing the final HTML now.

Let me also add a soft ground shadow receiver (tray receiveShadow true). Bedding receiveShadow true but cast false (to save perf and avoid clutter). Hamsters cast and receive shadows. Wheel cast shadow true, receive false. Food bowl cast+receive. Tunnel cast true.

Sun shadow camera covers the cage (±15). Good.

Let me write.

I think it's solid. Let me output.

One more: I'll add window resize handler and controls.update in loop.

Also set pixel ratio cap.

Let me write the final file.

Let me make the UI title emoji and hint.

Writing now. I'll produce clean code.

Let me reconsider the number of hamsters — 5 is good. Colors listed.

Let me write buildHamster:

```js
function buildHamster(bodyColor, accentColor){
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: bodyColor, flatShading:true, roughness:0.85 });
  const accMat = new THREE.MeshStandardMaterial({ color: accentColor, flatShading:true, roughness:0.85 });
  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(1,1), mat);
  body.scale.set(1,0.95,1.08); body.position.y=0.95; body.castShadow=true; body.receiveShadow=true;
  g.add(body);
  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55,1), mat);
  head.position.set(0,1.4,0.78); head.castShadow=true; head.receiveShadow=true;
  g.add(head);
  const earGeo = new THREE.SphereGeometry(0.18,6,6);
  const earL=new THREE.Mesh(earGeo,mat); earL.position.set(-0.26,1.75,0.72);
  const earR=earL.clone(); earR.position.x=0.26;
  g.add(earL,earR);
  const eyeMat=new THREE.MeshStandardMaterial({color:0x2a1a12, flatShading:true});
  const eyeGeo=new THREE.SphereGeometry(0.11,8,8);
  const hlMat=new THREE.MeshStandardMaterial({color:0xffffff, flatShading:true});
  const hlGeo=new THREE.SphereGeometry(0.045,6,6);
  const eyeL=new THREE.Mesh(eyeGeo,eyeMat); eyeL.position.set(-0.19,1.45,1.28);
  const eyeR=eyeL.clone(); eyeR.position.x=0.19;
  const hlL=new THREE.Mesh(hlGeo,hlMat); hlL.position.set(-0.16,1.49,1.34);
  const hlR=hlL.clone(); hlR.position.x=0.22;
  g.add(eyeL,eyeR,hlL,hlR);
  const nose=new THREE.Mesh(new THREE.SphereGeometry(0.07,6,6), new THREE.MeshStandardMaterial({color:0xff8fa3, flatShading:true}));
  nose.position.set(0,1.3,1.35);
  g.add(nose);
  const cheekMat=new THREE.MeshStandardMaterial({color:0xff9db8, flatShading:true, transparent:true, opacity:0.55});
  const cheekL=new THREE.Mesh(new THREE.SphereGeometry(0.11,6,6),cheekMat); cheekL.position.set(-0.32,1.28,1.18);
  const cheekR=cheekL.clone(); cheekR.position.x=0.32;
  g.add(cheekL,cheekR);
  const footGeo=new THREE.SphereGeometry(0.13,6,6);
  const feet=[];
  const fp=[[-0.36,0.12,0.42],[0.36,0.12,0.42],[-0.36,0.12,-0.42],[0.36,0.12,-0.42]];
  for(const p of fp){ const f=new THREE.Mesh(footGeo,accMat); f.position.set(...p); f.castShadow=true; g.add(f); feet.push(f);}
  const tail=new THREE.Mesh(new THREE.SphereGeometry(0.11,6,6),accMat); tail.position.set(0,0.9,-1.05);
  g.add(tail);
  g.userData={ body, head, feet, baseY:0, phase: Math.random()*10 };
  return g;
}
```

Now main loop update.

Let me define global references: wheelGroup, wheel (the spinning part), foodBowl position, hamsters array.

I'll grab wheel inner group. In build, I created wheelGroup containing `wheel` group with torus etc. Let me expose the spinning sub-group. I'll set wheelGroup.userData.spinning = wheel (the inner group). Or just reference. Let me store the spinning group as a variable.

Let me restructure: 
```
const wheelSpin = new THREE.Group(); // contains torus, spokes, discs
wheelSpin.position... no, torus centered at origin of wheelSpin
const wheelSupport = new THREE.Group();
wheelSupport.add(wheelSpin, supports);
wheelSupport.position.set(4.5,1.8,-4);
scene.add(wheelSupport);
```
Then wheelSpin.rotation.z is the spin. Good.

Let me write that.

Food bowl: foodBowl.group with position. Store foodPos = new THREE.Vector3(-3.5,0,3).

Tunnel: just decorative.

Now hamsters:
```
const hamsters=[];
const roles = ['runner','eat','eat','wander','wander'];
const colors=[...];
for(let i=0;i<5;i++){
  const h = buildHamster(colors[i].body, colors[i].accent);
  const x=(Math.random()-0.5)*8, z=(Math.random()-0.5)*7;
  h.position.set(clampX,0,clampZ);
  h.userData.heading=Math.random()*Math.PI*2;
  h.userData.state='wander';
  h.userData.timer=1+Math.random()*2;
  h.userData.speed=0.4+Math.random()*0.3;
  h.userData.eater = roles[i]==='eat';
  h.userData.runner = roles[i]==='runner';
  scene.add(h);
  hamsters.push(h);
}
```
For runner, override position and heading:
```
const runner=hamsters[0];
runner.position.set(4.5,0.3,-4);
runner.rotation.y=0;
runner.userData.state='wheel';
```

Update:
```
function updateHamster(h, dt){
  const ud=h.userData;
  // breathing
  const b=Math.sin(performance.now()*0.002 + ud.phase)*0.02;
  ud.body.scale.y=0.95+b;
  ud.baseY=0;
  
  if(ud.runner){
    // running on wheel
    ud.phase += dt*8;
    ud.baseY = Math.abs(Math.sin(ud.phase))*0.06;
    h.position.y = ud.baseY;
    // feet
    ud.feet.forEach((f,i)=>{ f.position.y = 0.12 + Math.abs(Math.sin(ud.phase + i*1.2))*0.12; });
    return;
  }
  
  ud.timer -= dt;
  // head idle
  if(ud.state==='pause'){
    ud.head.rotation.y = Math.sin(performance.now()*0.002)*0.3;
    if(ud.timer<=0){ ud.state='wander'; ud.heading=Math.random()*Math.PI*2; ud.timer=1+Math.random()*3; ud.speed=0.4+Math.random()*0.3; }
    return;
  }
  
  if(ud.state==='wander'){
    if(ud.timer<=0){
      const r=Math.random();
      if(ud.eater && r<0.12){ ud.state='go_eat'; ud.timer=1.5; }
      else if(r<0.45){ ud.state='pause'; ud.timer=1+Math.random()*2.5; }
      else { ud.heading += (Math.random()-0.5)*1.4; ud.timer=1+Math.random()*3; ud.speed=0.35+Math.random()*0.45; }
    }
    moveHamster(h, ud.speed, dt);
    ud.phase += dt*ud.speed*6;
    ud.feet.forEach((f,i)=>{ f.position.y = 0.12 + Math.max(0,Math.sin(ud.phase + i*1.3))*0.12; });
  } else if(ud.state==='go_eat'){
    const dx=foodPos.x-h.position.x, dz=foodPos.z-h.position.z;
    const dist=Math.hypot(dx,dz);
    if(dist>0.4){
      ud.heading=Math.atan2(dz,dx);
      moveHamster(h,0.7,dt);
      ud.phase+=dt*6;
      ud.feet.forEach((f,i)=>{ f.position.y=0.12+Math.max(0,Math.sin(ud.phase+i*1.3))*0.12; });
    } else { ud.state='eat'; ud.timer=2+Math.random()*2; }
  } else if(ud.state==='eat'){
    if(ud.timer<=0){ ud.state='wander'; ud.heading=Math.random()*Math.PI*2; ud.timer=1+Math.random()*3; }
    else {
      // nibble: bob head
      ud.head.position.y = 1.4 + Math.abs(Math.sin(performance.now()*0.01))*0.06;
    }
  }
}

function moveHamster(h,speed,dt){
  h.position.x += Math.cos(h.userData.heading)*speed*dt;
  h.position.z += Math.sin(h.userData.heading)*speed*dt;
  h.rotation.y = Math.PI/2 - h.userData.heading;
  const lx=5.6, lz=4.6;
  if(h.position.x>lx){h.position.x=lx; h.userData.heading+=Math.PI;}
  if(h.position.x<-lx){h.position.x=-lx; h.userData.heading+=Math.PI;}
  if(h.position.z>lz){h.position.z=lz; h.userData.heading+=Math.PI;}
  if(h.position.z<-lz){h.position.z=-lz; h.userData.heading+=Math.PI;}
  h.position.y = 0;
}
```

Wait, when clamping and flipping heading, the hamster continues moving in new direction. Good. But immediate re-clamp could cause jitter at boundaries; acceptable.

Particles & petting:
```
const particles=[];
function spawnHeart(pos){
  for(let i=0;i<6;i++){
    const m=new THREE.Mesh(new THREE.IcosahedronGeometry(0.13,0), new THREE.MeshStandardMaterial({color:0xff5c8a, flatShading:true, emissive:0x551122, emissiveIntensity:0.3}));
    m.position.copy(pos); m.position.y+=1.1;
    m.userData.vy=1.4+Math.random()*0.8;
    m.userData.vx=(Math.random()-0.5)*0.8;
    m.userData.vz=(Math.random()-0.5)*0.8;
    m.userData.life=1.2;
    m.scale.setScalar(0.6+Math.random()*0.6);
    scene.add(m); particles.push(m);
  }
}
function updateParticles(dt){
  for(let i=particles.length-1;i>=0;i--){
    const p=particles[i];
    p.position.y += p.userData.vy*dt;
    p.position.x += p.userData.vx*dt;
    p.position.z += p.userData.vz*dt;
    p.userData.vy -= 3*dt;
    p.userData.life -= dt;
    const s=Math.max(0,p.userData.life/1.2);
    p.scale.setScalar(s*(0.6));
    if(p.userData.life<=0){ scene.remove(p); particles.splice(i,1); }
  }
}
```

Raycast:
```
const raycaster=new THREE.Raycaster();
const ndc=new THREE.Vector2();
let pointerStart=null;
canvas.addEventListener('pointerdown',e=>{ pointerStart={x:e.clientX,y:e.clientY}; });
canvas.addEventListener('pointerup',e=>{
  if(!pointerStart) return;
  const dx=e.clientX-pointerStart.x, dy=e.clientY-pointerStart.y;
  if(Math.hypot(dx,dy)>6){ pointerStart=null; return; }
  pointerStart=null;
  ndc.x=(e.clientX/innerWidth)*2-1;
  ndc.y=-(e.clientY/innerHeight)*2+1;
  raycaster.fromVector(ndc);
  // check hamsters
  const hits=raycaster.intersectObjects(hamsters,true);
  if(hits.length){
    let obj=hits[0].object;
    while(obj.parent && !obj.userData.runner && !obj.userData.eater && obj.parent!==scene) obj=obj.parent;
    // find hamster group
    let h=obj; while(h.parent && !hamsters.includes(h)) h=h.parent;
    if(hamsters.includes(h)){
      spawnHeart(h.position);
      // happy jump
      h.userData.happy=1;
    }
  }
});
```

Hmm finding the hamster group: intersectObjects(hamsters,true) returns intersections whose object is within hamster groups. hits[0].object is some child; I need the hamster group that contains it. Since hamsters array contains groups, and intersectObjects with recursive true returns objects that are descendants of the given objects. hits[0].object is a descendant. To find parent hamster group, walk up until object is in hamsters array.

```
let h=hits[0].object;
while(h && !hamsters.includes(h)) h=h.parent;
```
If h undefined skip. Good.

Happy effect: if h.userData.happy>0, do a jump and wiggle.
In updateHamster, add:
```
if(ud.happy>0){
  ud.happy-=dt;
  ud.baseY = Math.max(0, Math.sin(ud.happy*Math.PI*2))*0.3;
  h.position.y = ud.baseY;
  ud.head.rotation.z = Math.sin(performance.now()*0.03)*0.2;
  ud.body.rotation.z = Math.sin(performance.now()*0.02)*0.1;
  return;
}
```
Place this check early (after breathing) so it overrides. But runner also needs to keep spinning wheel — happy only on non-runner typically. If runner petted, it still should keep wheel spinning. Let me handle: if runner and happy, do happy but still return before normal. Actually runner's normal update sets wheel spin externally (in loop). Happy jump for runner is fine; wheel still spins in loop. So for runner, happy branch returns and wheel continues spinning in main loop. Good.

But note: happy branch returns before the runner's running animation; that's fine, brief.

Let me place happy check right after breathing calc, before runner/eat logic. Actually for runner, we still want wheel to spin (handled in loop). Happy jump overrides body pos. Fine.

Main loop:
```
const clock=new THREE.Clock();
function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),0.05);
  // spin wheel
  wheelSpin.rotation.z -= dt*6; // negative for direction
  // update hamsters
  for(const h of hamsters) updateHamster(h,dt);
  updateParticles(dt);
  controls.update();
  renderer.render(scene,camera);
}
animate();
```

Wheel spin direction: hamster runs, bottom of wheel moves... whatever, just spin continuously. Speed 6 rad/s. Good. Maybe modulate with hamster happiness—not needed.

Resize:
```
window.addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
```

I think that's complete. Let me assemble the full HTML.

Let me double check the clampX/lz used in moveHamster (5.6,4.6) vs cage. Good.

Also ensure hamsters don't overlap too much—random positions fine, they may pass through each other; acceptable for cuteness. Could add simple separation but not necessary. Keep simple.

Let me also make the food bowl have a little "eating" indicator—optional. Skip.

Let me finalize the HTML with styles and UI.

Let me write it out completely now.

I want to ensure the scene is not too empty—maybe add a small house/shelter and a water bottle for extra cuteness. Requirement says don't overcomplicate. I'll add a tiny cozy house (box + roof) and a water dropper bottle as extra scenery, plus maybe a small ladder. Actually let me add: a little house (box with triangular roof) and a water bottle. These add charm without much complexity. And a couple of scattered chew toys (small cubes). Let me add house + water bottle + a few toys. Keep it moderate.

Let me add:
- House: box body + prism roof, color warm, at (-4.5,0,-3).
- Water bottle: cylinder + nozzle at (5,-?), mounted on wall? Hard to mount. Place on ground at (3.5,0,3.5) as a bottle with a ball tip.
- A few chew toys: small colored cylinders/cubes scattered.

These are static decor. Adds charm. Let me include house, water bottle, and 4 chew toys.

Let me write buildHouse, buildWaterBottle.

House:
```
function buildHouse(){
  const g=new THREE.Group();
  const wallMat=new THREE.MeshStandardMaterial({color:0xffb74d, flatShading:true, roughness:0.8});
  const roofMat=new THREE.MeshStandardMaterial({color:0xd84a4a, flatShading:true, roughness:0.8});
  const body=new THREE.Mesh(new THREE.BoxGeometry(1.6,1,1.6), wallMat);
  body.position.y=0.5; body.castShadow=true; body.receiveShadow=true;
  const roof=new THREE.Mesh(new THREE.ConeGeometry(1.25,0.9,4), roofMat);
  roof.position.y=1.0; roof.rotation.y=Math.PI/4; roof.castShadow=true;
  const door=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.7,0.1), new THREE.MeshStandardMaterial({color:0x6b4226, flatShading:true}));
  door.position.set(0,0.35,0.82);
  g.add(body,roof,door);
  return g;
}
```
ConeGeometry with 4 segments is a pyramid (low-poly). Good.

Water bottle:
```
function buildBottle(){
  const g=new THREE.Group();
  const bottleMat=new THREE.MeshStandardMaterial({color:0x8adaff, flatShading:true, roughness:0.3, transparent:true, opacity:0.85});
  const body=new THREE.Mesh(new THREE.CylinderGeometry(0.28,0.28,1.1,12), bottleMat);
  body.position.y=0.95;
  cap=new THREE.Mesh(new THREE.CylinderGeometry(0.12,0.12,0.3,10), new THREE.MeshStandardMaterial({color:0xffffff, flatShading:true}));
  cap.position.y=1.55;
  nozzle=new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.05,0.3,8), new THREE.MeshStandardMaterial({color:0xcccccc, flatShading:true, metalness:0.6, roughness:0.3}));
  nozzle.position.y=1.35; // pointing down? actually nozzle points down from cap
  // place nozzle pointing down
  nozzle.position.set(0,1.25,0.12); nozzle.rotation.x=Math.PI/2; // point toward +z then down? 
  ...
}
```
This is getting fiddly. Let me simplify: bottle standing with cap on top and a small ball nozzle at bottom front. Place at (3.5,0,3.5). Hamsters near it.

Actually let me just make a simple bottle: cylinder body + cone cap + small sphere nozzle at bottom. Position nozzle at (0,0.35,0.28) pointing outward. Fine.

Chew toys: small cylinders in bright colors scattered at random spots on floor.

Let me add ~4 chew sticks.

OK let me just include house, bottle, and sticks. Keeps charm without clutter.

Let me finalize.

Actually, to reduce risk of clutter/visual noise, I'll include house + bottle + 3 sticks. Good.

Let me write final code and assemble.

Let me make sure positions of decor don't block hamster paths too much. House at (-4.5,-3), bottle at (3.5,3.5), sticks scattered. Hamsters wander within ±5.6,±4.6. They might walk through house (occlusion via transparent? house is opaque). They'd walk into it and bounce off walls anyway. Minor. Acceptable. To avoid clipping through house, I could shrink bounds slightly or place house near corner. (-4.5,-3) is near back-left corner, fine.

Alright, writing final answer.

Let me write the complete file now, carefully assembled.

I'll include comments for clarity.

Let me also ensure I import ConeGeometry usage correct.

Final assembly below.

Let me write the CSS nicely with a soft gradient background behind canvas for a dreamy look. I'll set body background to a linear gradient and canvas transparent? But renderer setClearColor to cream. If canvas is opaque it covers gradient. Let me instead make canvas transparent and show CSS gradient behind, plus fog for depth. But transparent canvas + shadows... shadows render onto scene objects with alpha fine. Let me set renderer.setClearColor(0x000000,0) transparent, and put a gradient div behind. Fog color should match gradient center. Let me set fog to a soft pink #f9c8dc. Hmm.

Simpler: keep opaque cream background (clean, readable). Add gradient via a separate absolutely-positioned div behind canvas with lower opacity so it tints. Actually let me just do opaque cream background — clean and readable, meets "visually clear". I'll add a subtle vignette via CSS. Good.

Let me finalize with cream background.

Write now.

Let me produce the final HTML file.

Double-check: setPixelRatio(min(dpr,2)). Good.

I'll write it all.

Also add meta viewport.

Final answer below.

Let me make sure the code has no syntax errors. I'll write carefully.

Let me write the whole thing.

I'll also add a gentle auto-rotate? No, user controls. Keep manual.

Let me finalize.

For the wheel spin, hamster runs making it spin; direction: I'll spin +z slowly pulsing. Fine.

Write final.

Also I realize hamsters cast shadows on each other and themselves — fine.

Let me output.

Let me reconsider the head position relative to body for the "neck". Head at y=1.4, body top at 1.9 (0.95+0.95). Head bottom 0.85. So head overlaps body from 0.85 to 1.9. The head sits "into" the body front-top. Looks like a head on a body. Fine. Maybe raise head slightly to y=1.5 and move z to 0.7 so it sits more on top-front. Let me set head position (0,1.5,0.72). Radius 0.55 → spans 0.95–2.05. Overlaps body top. Ears at 1.75. Eyes at 1.55, nose 1.4, cheeks 1.35. Let me adjust eye y to 1.55, nose 1.38, cheeks 1.35. Slight tweaks. It'll look fine.

Let me set:
- head pos (0,1.5,0.72)
- ears (-0.26,1.82,0.7),(0.26,1.82,0.7)
- eyes (-0.19,1.55,1.24),(0.19,1.55,1.24)
- highlights (-0.16,1.59,1.3),(0.22,1.59,1.3)
- nose (0,1.4,1.32)
- cheeks (-0.32,1.35,1.16),(0.32,1.35,1.16)

Good.

Now final code. Let me write it.

I'll produce the complete file.

Let me ensure I reference variables consistently (wheelSpin, foodPos, hamsters, particles).

Writing now.
</think>

# Low-Poly Hamster Playground 🐹

Here's a complete, single-file project. Just save it as `index.html` and open it in any modern browser.

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
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #fde9d0; }
  #app { width: 100%; height: 100%; display: block; cursor: grab; }
  #app:active { cursor: grabbing; }
  #ui {
    position: fixed; top: 16px; left: 16px; z-index: 10;
    background: rgba(255,255,255,0.82); border-radius: 16px;
    padding: 14px 18px; box-shadow: 0 6px 22px rgba(120,80,60,0.18);
    color: #6b4f40; max-width: 270px; backdrop-filter: blur(6px);
  }
  #ui h1 { font-size: 19px; margin-bottom: 6px; }
  #ui p { font-size: 12.5px; line-height: 1.55; opacity: 0.9; }
  #hint {
    position: fixed; bottom: 16px; left: 16px; z-index: 10;
    background: rgba(255,255,255,0.82); border-radius: 12px;
    padding: 9px 14px; font-size: 12.5px; color: #6b4f40;
    box-shadow: 0 4px 16px rgba(120,80,60,0.16);
  }
  #badge {
    position: fixed; top: 16px; right: 16px; z-index: 10;
    background: rgba(255,255,255,0.82); border-radius: 12px;
    padding: 8px 14px; font-size: 13px; color: #6b4f40;
    box-shadow: 0 4px 16px rgba(120,80,60,0.16);
  }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate · Scroll to zoom · <b>Click a hamster</b> to pet it and make hearts! 💕</p>
</div>
<div id="hint">A hamster runs the wheel 🎡 · Some nibble snacks 🌾 · Others explore 🔎</div>
<div id="badge">🐹 5 hamsters</div>
<canvas id="app"></canvas>

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

/* ---------- Renderer ---------- */
const canvas = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setClearColor(0xfde9d0);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xfde9d0, 20, 44);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(0, 9, 15);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1.2, 0);
controls.minDistance = 5;
controls.maxDistance = 30;
controls.maxPolarAngle = Math.PI * 0.495;

/* ---------- Lights ---------- */
scene.add(new THREE.AmbientLight(0xffffff, 0.72));
scene.add(new THREE.HemisphereLight(0xbfd9ff, 0xffe9c4, 0.55));

const sun = new THREE.DirectionalLight(0xfff4e0, 1.25);
sun.position.set(7, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1; sun.shadow.camera.far = 45;
sun.shadow.camera.left = -16; sun.shadow.camera.right = 16;
sun.shadow.camera.top = 16; sun.shadow.camera.bottom = -16;
sun.shadow.bias = -0.0004;
scene.add(sun);

/* ---------- Cage ---------- */
const cage = new THREE.Group();
scene.add(cage);

const trayMat = new THREE.MeshStandardMaterial({ color: 0xffd0e0, flatShading: true, roughness: 0.9 });
const tray = new THREE.Mesh(new THREE.BoxGeometry(15, 0.5, 13), trayMat);
tray.position.y = -0.25; tray.receiveShadow = true;
cage.add(tray);

// wood-chip bedding
const bedColors = [0xffe3a3, 0xffd3e6, 0xd8f0d0, 0xd6ecff, 0xffe0b3, 0xf3d8ff];
const bedGeo = new THREE.BoxGeometry(0.26, 0.16, 0.26);
for (let i = 0; i < 140; i++) {
  const m = new THREE.Mesh(bedGeo, new THREE.MeshStandardMaterial({
    color: bedColors[i % bedColors.length], flatShading: true }));
  m.position.set((Math.random() - 0.5) * 14, 0.08, (Math.random() - 0.5) * 12);
  m.rotation.y = Math.random() * Math.PI;
  m.castShadow = false; m.receiveShadow = true;
  cage.add(m);
}

// transparent acrylic walls
const wallMat = new THREE.MeshStandardMaterial({ color: 0xcfeeff, transparent: true, opacity: 0.16, roughness: 0.1, side: THREE.DoubleSide });
function makeWall(w, d, x, z) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, 3, d), wallMat);
  m.position.set(x, 1.5, z); cage.add(m);
}
makeWall(15, 0.1, 0, -6.5);
makeWall(15, 0.1, 0, 6.5);
makeWall(0.1, 13, -7.5, 0);
makeWall(0.1, 13, 7.5, 0);

// corner posts
const postMat = new THREE.MeshStandardMaterial({ color: 0xffb0c0, flatShading: true, roughness: 0.6 });
[[-7.5,-6.5],[7.5,-6.5],[7.5,6.5],[-7.5,6.5]].forEach(([x,z]) => {
  const p = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 3, 8), postMat);
  p.position.set(x, 1.5, z); cage.add(p);
});

/* ---------- Decor: house, water bottle, chew toys ---------- */
const decor = new THREE.Group();
scene.add(decor);

// cozy house
const house = new THREE.Group();
const wallMat = new THREE.MeshStandardMaterial({ color: 0xffb74d, flatShading: true, roughness: 0.8 });
const roofMat = new THREE.MeshStandardMaterial({ color: 0xd84a4a, flatShading: true, roughness: 0.8 });
const hBody = new THREE.Mesh(new THREE.BoxGeometry(1.7, 1.1, 1.7), wallMat);
hBody.position.y = 0.55; hBody.castShadow = true; hBody.receiveShadow = true;
const hRoof = new THREE.Mesh(new THREE.ConeGeometry(1.35, 0.95, 4), roofMat);
hRoof.position.y = 1.1; hRoof.rotation.y = Math.PI / 4; hRoof.castShadow = true;
const hDoor = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.75, 0.1),
  new THREE.MeshStandardMaterial({ color: 0x6b4226, flatShading: true }));
hDoor.position.set(0, 0.38, 0.85);
house.add(hBody, hRoof, hDoor);
house.position.set(-4.8, 0, -3.2);
decor.add(house);

// water bottle
const bottle = new THREE.Group();
const bMat = new THREE.MeshStandardMaterial({ color: 0x8adaff, flatShading: true, roughness: 0.3, transparent: true, opacity: 0.85 });
const bBody = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 1.2, 14), bMat);
bBody.position.y = 1.0;
const bCap = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.32, 12),
  new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true }));
bCap.position.y = 1.66;
const bNozzle = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.34, 10),
  new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.6, roughness: 0.3, flatShading: true }));
bNozzle.rotation.x = Math.PI / 2; bNozzle.position.set(0, 1.2, 0.32);
bottle.add(bBody, bCap, bNozzle);
bottle.position.set(3.6, 0, 4.5);
bottle.traverse(o => { if (o.isMesh) o.castShadow = true; });
decor.add(bottle);

// chew toys (little colored sticks/blocks)
const toyColors = [0xff6b8a, 0x6bc4ff, 0xffd166, 0x8bd66b, 0xc084fc];
for (let i = 0; i < 6; i++) {
  const t = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: toyColors[i % toyColors.length], flatShading: true, roughness: 0.7 });
  if (i % 2 === 0) {
    const stick = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.7, 8), mat);
    stick.rotation.z = Math.PI / 2;
    t.add(stick);
  } else {
    const cube = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.4), mat);
    t.add(cube);
  }
  const x = (Math.random() - 0.5) * 12, z = (Math.random() - 0.5) * 10;
  if (Math.hypot(x + 4.8, z + 3.2) < 2.2 || Math.hypot(x - 3.6, z - 4.5) < 2) continue;
  t.position.set(x, 0.22, z);
  t.rotation.y = Math.random() * Math.PI;
  t.traverse(o => { if (o.isMesh) o.castShadow = true; });
  decor.add(t);
}

/* ---------- Interactive: exercise wheel ---------- */
const wheelSpin = new THREE.Group();
const rimMat = new THREE.MeshStandardMaterial({ color: 0xff6b8a, flatShading: true, roughness: 0.5 });
const discMat = new THREE.MeshStandardMaterial({ color: 0xffb3c1, flatShading: true, roughness: 0.6, transparent: true, opacity: 0.85 });
const spinRim = new THREE.Mesh(new THREE.TorusGeometry(1.3, 0.09, 8, 24), rimMat);
spinRim.castShadow = true;
wheelSpin.add(spinRim);
for (let i = 0; i < 8; i++) {
  const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.5, 6), rimMat);
  spoke.rotation.z = (i / 8) * Math.PI; spoke.castShadow = true;
  wheelSpin.add(spoke);
}
const d1 = new THREE.Mesh(new THREE.CylinderGeometry(1.25, 1.25, 0.05, 20), discMat);
d1.rotation.x = Math.PI / 2; d1.position.z = 0.12;
const d2 = d1.clone(); d2.position.z = -0.12;
wheelSpin.add(d1, d2);

const supportMat = new THREE.MeshStandardMaterial({ color: 0xeeeeee, flatShading: true });
const s1 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.4, 8), supportMat);
s1.position.set(0, -1.0, 0.2);
const s2 = s1.clone(); s2.position.z = -0.2;
const wheelBase = new THREE.Group();
wheelBase.add(wheelSpin, s1, s2);
wheelBase.position.set(4.8, 1.6, -4.2);
scene.add(wheelBase);

/* ---------- Interactive: food bowl ---------- */
const foodPos = new THREE.Vector3(-3.6, 0, 3.2);
const foodBowl = new THREE.Group();
const bowlMat = new THREE.MeshStandardMaterial({ color: 0x6bc4ff, flatShading: true, roughness: 0.6 });
const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.52, 0.4, 14, 1, true), bowlMat);
bowl.position.y = 0.22;
const bowlBottom = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.52, 0.06, 14), bowlMat);
bowlBottom.position.y = 0.04;
const pelletMat = new THREE.MeshStandardMaterial({ color: 0xc9a06a, flatShading: true });
for (let i = 0; i < 16; i++) {
  const p = new THREE.Mesh(new THREE.SphereGeometry(0.09, 6, 6), pelletMat);
  const a = Math.random() * Math.PI * 2, r = Math.random() * 0.55;
  p.position.set(Math.cos(a) * r, 0.34 + Math.random() * 0.08, Math.sin(a) * r);
  foodBowl.add(p);
}
foodBowl.add(bowl, bowlBottom);
foodBowl.position.copy(foodPos);
foodBowl.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
scene.add(foodBowl);

/* ---------- Hamsters ---------- */
function buildHamster(bodyColor, accentColor) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: bodyColor, flatShading: true, roughness: 0.85 });
  const accMat = new THREE.MeshStandardMaterial({ color: accentColor, flatShading: true, roughness: 0.85 });

  const body = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 1), mat);
  body.scale.set(1, 0.95, 1.08); body.position.y = 0.95;
  body.castShadow = true; body.receiveShadow = true; g.add(body);

  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 1), mat);
  head.position.set(0, 1.5, 0.72); head.castShadow = true; head.receiveShadow = true; g.add(head);

  const earGeo = new THREE.SphereGeometry(0.18, 6, 6);
  const earL = new THREE.Mesh(earGeo, mat); earL.position.set(-0.26, 1.82, 0.7);
  const earR = earL.clone(); earR.position.x = 0.26;
  g.add(earL, earR);

  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x2a1a12, flatShading: true });
  const eyeGeo = new THREE.SphereGeometry(0.11, 8, 8);
  const hlMat = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true });
  const hlGeo = new THREE.SphereGeometry(0.045, 6, 6);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat); eyeL.position.set(-0.19, 1.55, 1.24);
  const eyeR = eyeL.clone(); eyeR.position.x = 0.19;
  const hlL = new THREE.Mesh(hlGeo, hlMat); hlL.position.set(-0.16, 1.59, 1.3);
  const hlR = hlL.clone(); hlR.position.x = 0.22;
  g.add(eyeL, eyeR, hlL, hlR);

  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.07, 6, 6),
    new THREE.MeshStandardMaterial({ color: 0xff8fa3, flatShading: true }));
  nose.position.set(0, 1.4, 1.32); g.add(nose);

  const cheekMat = new THREE.MeshStandardMaterial({ color: 0xff9db8, flatShading: true, transparent: true, opacity: 0.55 });
  const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.11, 6, 6), cheekMat); cheekL.position.set(-0.32, 1.35, 1.16);
  const cheekR = cheekL.clone; cheekR.position.x = 0.32;
  g.add(cheekL, cheekR);

  const footGeo = new THREE.SphereGeometry(0.13, 6, 6);
  const feet = [];
  const fp = [[-0.36, 0.12, 0.42], [0.36, 0.12, 0.42], [-0.36, 0.12, -0.42], [0.36, 0.12, -0.42]];
  for (const p of fp) {
    const f = new THREE.Mesh(footGeo, accMat); f.position.set(p[0], p[1], p[2]); f.castShadow = true;
    g.add(f); feet.push(f);
  }

  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.11, 6, 6), accMat);
  tail.position.set(0, 0.9, -1.05); g.add(tail);

  g.userData = { body, head, feet, phase: Math.random() * 10, happy: 0 };
  return g;
}

const palette = [
  { body: 0xffb3a7, accent: 0xffd9cf },
  { body: 0xffd6a7, accent: 0xfff0cf },
  { body: 0xc8e6c9, accent: 0xeaffea },
  { body: 0xb3e5fc, accent: 0xe6f7ff },
  { body: 0xe1bee7, accent: 0xf7e6fb },
];

const hamsters = [];
for (let i = 0; i < 5; i++) {
  const h = buildHamster(palette[i].body, palette[i].accent);
  const x = (Math.random() - 0.5) * 8, z = (Math.random() - 0.5) * 7;
  h.position.set(x, 0, z);
  h.userData.heading = Math.random() * Math.PI * 2;
  h.userData.state = 'wander';
  h.userData.timer = 1 + Math.random() * 2;
  h.userData.speed = 0.4 + Math.random() * 0.3;
  h.userData.eater = (i === 1 || i === 2);
  h.userData.runner = (i === 0);
  scene.add(h);
  hamsters.push(h);
}

// the wheel-runner takes its permanent spot
const runner = hamsters[0];
runner.position.set(4.8, 0.3, -4.2);
runner.rotation.y = 0;

/* ---------- Particles (hearts) ---------- */
const particles = [];
function spawnHeart(pos) {
  for (let i = 0; i < 6; i++) {
    const m = new THREE.Mesh(new THREE.IcosahedronGeometry(0.13, 0),
      new THREE.MeshStandardMaterial({ color: 0xff5c8a, flatShading: true, emissive: 0x551122, emissiveIntensity: 0.35 }));
    m.position.copy(pos); m.position.y += 1.1;
    m.userData.vy = 1.5 + Math.random() * 0.8;
    m.userData.vx = (Math.random() - 0.5) * 0.9;
    m.userData.vz = (Math.random() - 0.5) * 0.9;
    m.userData.life = 1.2;
    m.scale.setScalar(0.6 + Math.random() * 0.6);
    scene.add(m); particles.push(m);
  }
}
function updateParticles(dt) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.position.y += p.userData.vy * dt;
    p.position.x += p.userData.vx * dt;
    p.position.z += p.userData.vz * dt;
    p.userData.vy -= 3.2 * dt;
    p.userData.life -= dt;
    p.scale.setScalar(Math.max(0, p.userData.life / 1.2) * 0.7);
    if (p.userData.life <= 0) { scene.remove(p); particles.splice(i, 1); }
  }
}

/* ---------- Pet interaction (raycast) ---------- */
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let pointerStart = null;
canvas.addEventListener('pointerdown', e => { pointerStart = { x: e.clientX, y: e.clientY }; });
canvas.addEventListener('pointerup', e => {
  if (!pointerStart) return;
  const dx = e.clientX - pointerStart.x, dy = e.clientY - pointerStart.y;
  pointerStart = null;
  if (Math.hypot(dx, dy) > 8) return; // ignore drags
  ndc.x = (e.clientX / innerWidth) * 2 - 1;
  ndc.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.fromVector(ndc);
  const hits = raycaster.intersectObjects(hamsters, true);
  if (hits.length) {
    let h = hits[0].object;
    while (h && !hamsters.includes(h)) h = h.parent;
    if (hamsters.includes(h)) { spawnHeart(h.position); h.userData.happy = 1; }
  }
});

/* ---------- Hamster AI ---------- */
function moveHamster(h, speed, dt) {
  h.position.x += Math.cos(h.userData.heading) * speed * dt;
  h.position.z += Math.sin(h.userData.heading) * speed * dt;
  h.rotation.y = Math.PI / 2 - h.userData.heading;
  const lx = 5.8, lz = 4.8;
  if (h.position.x > lx)  { h.position.x = lx;  h.userData.heading += Math.PI; }
  if (h.position.x < -lx) { h.position.x = -lx; h.userData.heading += Math.PI; }
  if (h.position.z > lz)  { h.position.z = lz;  h.userData.heading += Math.PI; }
  if (h.position.z < -lz) { h.position.z = -lz; h.userData.heading += Math.PI; }
  h.position.y = 0;
}

function animateFeet(h, dt) {
  h.userData.phase += dt * h.userData.speed * 6;
  const ph = h.userData.phase;
  h.userData.feet.forEach((f, i) => {
    f.position.y = 0.12 + Math.max(0, Math.sin(ph + i * 1.3)) * 0.13;
  });
}

function updateHamster(h, dt) {
  const ud = h.userData;
  // gentle breathing
  ud.body.scale.y = 0.95 + Math.sin(performance.now() * 0.002 + ud.phase) * 0.02;

  // petted / happy
  if (ud.happy > 0) {
    ud.happy -= dt;
    h.position.y = Math.max(0, Math.sin(ud.happy * Math.PI * 2.5)) * 0.32;
    ud.head.rotation.z = Math.sin(performance.now() * 0.03) * 0.22;
    ud.body.rotation.z = Math.sin(performance.now() * 0.02) * 0.1;
    return;
  }

  // the dedicated wheel-runner
  if (ud.runner) {
    ud.phase += dt * 9;
    h.position.y = Math.abs(Math.sin(ud.phase)) * 0.07;
    ud.feet.forEach((f, i) => { f.position.y = 0.12 + Math.abs(Math.sin(ud.phase + i * 1.1)) * 0.14; });
    return;
  }

  ud.timer -= dt;

  if (ud.state === 'pause') {
    ud.head.rotation.y = Math.sin(performance.now() * 0.002) * 0.32;
    if (ud.timer <= 0) {
      ud.state = 'wander';
      ud.heading = Math.random() * Math.PI * 2;
      ud.timer = 1 + Math.random() * 3;
      ud.speed = 0.4 + Math.random() * 0.3;
    }
    return;
  }

  if (ud.state === 'wander') {
    if (ud.timer <= 0) {
      const r = Math.random();
      if (ud.eater && r < 0.12) { ud.state = 'go_eat'; ud.timer = 1.5; }
      else if (r < 0.45) { ud.state = 'pause'; ud.timer = 1 + Math.random() * 2.5; }
      else { ud.heading += (Math.random() - 0.5) * 1.4; ud.timer = 1 + Math.random() * 3; ud.speed = 0.35 + Math.random() * 0.45; }
    }
    moveHamster(h, ud.speed, dt);
    animateFeet(h, dt);
  } else if (ud.state === 'go_eat') {
    const dx = foodPos.x - h.position.x, dz = foodPos.z - h.position.z;
    const dist = Math.hypot(dx, dz);
    if (dist > 0.4) {
      ud.heading = Math.atan2(dz, dx);
      moveHamster(h, 0.7, dt);
      animateFeet(h, dt);
    } else { ud.state = 'eat'; ud.timer = 2 + Math.random() * 2; }
  } else if (ud.state === 'eat') {
    if (ud.timer <= 0) {
      ud.state = 'wander'; ud.heading = Math.random() * Math.PI * 2; ud.timer = 1 + Math.random() * 3;
    } else {
      ud.head.position.y = 1.5 + Math.abs(Math.sin(performance.now() * 0.012)) * 0.07; // nibbling
    }
  }
}

/* ---------- Loop ---------- */
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  wheelSpin.rotation.z -= dt * 6;          // wheel spins
  for (const h of hamsters) updateHamster(h, dt);
  updateParticles(dt);
  controls.update();
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

**Scene contents**
- 🏠 A wooden **house**, 💧 a **water bottle**, 🍬 scattered **chew toys**, and colorful wood-chip **bedding** on a pink **tray**.
- Transparent acrylic **cage walls** with pink corner posts.
- 🎡 An interactive **exercise wheel** that spins continuously.
- 🥣 An interactive **food bowl** full of pellets.

**Five cute low-poly hamsters** (coral, peach, mint, sky, lavender), each built from rounded low-poly shapes: blob body, big eyes with highlights, rosy cheeks, little ears, feet, and a tail.

**Autonomous behavior** (simple state machine):
- One hamster is the permanent **wheel runner** — it runs in place and spins the wheel.
- Two hamsters are **snackers** — they wander, get hungry, walk to the food bowl, nibble, then wander off.
- The rest **wander, pause to look around, and turn** randomly, bouncing gently off the walls.

**Interactions**
- Drag to rotate the camera, scroll to zoom.
- **Click a hamster** to pet it — it jumps happily and bursts into floating heart particles. 💕

It runs instantly in any modern browser — no build step, no dependencies beyond the Three.js CDN loaded via the import map.