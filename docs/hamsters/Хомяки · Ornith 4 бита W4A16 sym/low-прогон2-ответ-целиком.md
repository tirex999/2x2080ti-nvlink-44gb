Let me create a single-file browser project called "Low-Poly Hamster Playground" using Three.js. I need to:

1. Use Three.js (via CDN)
2. Everything in one index.html file
3. Create a 3D scene with:
   - A cage
   - A floor/tray
   - Several low-poly hamsters
   - At least one interactive object (wheel, tunnel, food bowl, or toy)
4. Hamsters should have autonomous behavior (walking, pausing, turning, interacting)
5. Cute, low-poly, colorful, funny visual style
6. Camera rotation controls
7. Run immediately in a modern browser

Let me build this carefully. I'll use Three.js from a CDN and OrbitControls for camera rotation.

Let me think about the structure:

**Scene setup:**
- Renderer with antialiasing
- Scene with nice background color
- Camera (perspective)
- Lights (ambient + directional)
- OrbitControls for camera rotation

**Cage:**
- A tray/base (like a low box)
- Walls (transparent or wireframe so we can see inside)
- Maybe a roof frame

**Floor:**
- Bedding material (colored plane with some texture or just color)

**Hamsters:**
- Low-poly body (sphere or rounded shape)
- Ears, eyes, nose, cheeks, feet, tail
- Different colors
- Autonomous behavior: walk, pause, turn, interact

**Interactive object:**
- Exercise wheel that hamsters can run on
- Food bowl
- Tunnel

Let me create the hamsters procedurally with groups of meshes. Each hamster will be a THREE.Group with:
- Body (icosahedron or sphere, low-poly look)
- Head
- Ears
- Eyes
- Nose
- Cheeks
- Feet
- Tail

For behavior, I'll give each hamster a state machine:
- WALKING: moves in a direction, maybe wanders randomly
- PAUSED: stops, maybe sniffs/looks around
- INTERACTING: goes to the wheel/bowl and interacts

Let me implement smooth movement with simple AI.

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
  html, body { width: 100%; height: 100%; overflow: hidden; background: #fde9d6; font-family: 'Comic Sans MS', 'Segoe UI', sans-serif; }
  #app { width: 100vw; height: 100vh; display: block; }
  #ui {
    position: fixed; top: 16px; left: 16px; z-index: 10;
    background: rgba(255,255,255,0.85);
    border-radius: 16px; padding: 14px 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    backdrop-filter: blur(6px);
    max-width: 260px;
  }
  #ui h1 { font-size: 18px; color: #d2691e; margin-bottom: 6px; }
  #ui p { font-size: 12px; color: #7a5230; line-height: 1.5; }
  #ui button {
    margin-top: 10px; background: #ffb347; border: none; color: #5a3200;
    padding: 8px 14px; border-radius: 12px; cursor: pointer; font-weight: bold;
    font-size: 12px; transition: transform 0.1s, background 0.2s;
  }
  #ui button:hover { background: #ff9a2e; transform: translateY(-2px); }
</style>
</head>
<body>
<div id="app"></div>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate • Scroll to zoom<br>Watch the little guys roam, nap, and hit the gym!</p>
  <button id="treatBtn">🥕 Drop a Treat!</button>
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

// ... scene setup
</script>
</body>
</html>
```

Now let me flesh out the JavaScript. Let me plan the geometry.

**Renderer:**
```js
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);
```

**Scene & Camera:**
```js
const scene = new THREE.Scene();
scene.background = new THREE.Color('#cde7f5');
scene.fog = new THREE.Fog('#cde7f5', 40, 90);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 200);
camera.position.set(14, 12, 18);
```

**Lights:**
```js
const ambient = new THREE.AmbientLight('#fff5e6', 0.7);
scene.add(ambient);

const hemi = new THREE.HemisphereLight('#ffffff', '#c9a978', 0.5);
scene.add(hemi);

const sun = new THREE.DirectionalLight('#fff8f0', 1.1);
sun.position.set(12, 20, 10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 60;
sun.shadow.camera.left = -25;
sun.shadow.camera.right = 25;
sun.shadow.camera.top = 25;
sun.shadow.camera.bottom = -25;
sun.shadow.bias = -0.0005;
scene.add(sun);
```

**Cage dimensions:**
Let's make the cage about 24x24 units, centered at origin.

**Tray (floor):**
A shallow box. The floor of the tray.

Let me build the cage as a group.

```js
const CAGE = { w: 24, d: 24, h: 8 };
const cageGroup = new THREE.Group();
scene.add(cageGroup);
```

**Floor/tray:**
Bottom of tray - a flat box.
```js
const trayMat = new THREE.MeshStandardMaterial({ color: '#7ec8e3', roughness: 0.9 });
const trayBottom = new THREE.Mesh(new THREE.BoxGeometry(CAGE.w, 0.6, CAGE.d), trayMat);
trayBottom.position.y = 0.3;
trayBottom.receiveShadow = true;
cageGroup.add(trayBottom);
```

**Bedding:**
A layer of colored bedding on top. Let me make it a slightly textured look with random small bits. Actually, let me just do a plane with a nice wood-shaving color, plus some scattered low-poly bedding pieces.

```js
const beddingMat = new THREE.MeshStandardMaterial({ color: '#f0d9a8', roughness: 1 });
const bedding = new THREE.Mesh(new THREE.PlaneGeometry(CAGE.w - 0.6, CAGE.d - 0.6), beddingMat);
bedding.rotation.x = -Math.PI/2;
bedding.position.y = 0.61;
bedding.receiveShadow = true;
cageGroup.add(bedding);
```

Add some scattered bedding bits for low-poly charm:
```js
const bitMat = new THREE.MeshStandardMaterial({ color: '#e8c984', roughness: 1, flatShading: true });
for (let i = 0; i < 200; i++) {
  const bit = new THREE.Mesh(new THREE.TetrahedronGeometry(0.12 + Math.random()*0.12), bitMat);
  bit.position.set((Math.random()-0.5)*(CAGE.w-1), 0.65 + Math.random()*0.1, (Math.random()-0.5)*(CAGE.d-1));
  bit.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
  bit.castShadow = false;
  cageGroup.add(bit);
}
```

**Cage walls:**
Transparent walls so we can see in. Let me make them with glass-like material, with frames.

Actually, for a "cage" look, let me do metal bars (frames) plus maybe transparent panels. To keep it clean and see the hamsters, I'll use semi-transparent walls.

Let me do transparent acrylic-style walls:
```js
const wallMat = new THREE.MeshPhysicalMaterial({
  color: '#dff3fb', transparent: true, opacity: 0.22,
  roughness: 0.1, metalness: 0, transmission: 0.5,
});
```

Hmm, transmission requires proper setup but works in recent versions. Let me keep it simpler with opacity.

Walls: front, back, left, right.

Actually, let me combine: solid frame with transparent panels. That might be complex. Let me just do transparent panels with edge lines.

Let me make four walls as thin boxes:
```js
function makeWall(w, h, x, y, z, ry) {
  const wall = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.3), wallMat);
  wall.position.set(x, y, z);
  wall.rotation.y = ry;
  wall.castShadow = true;
  cageGroup.add(wall);
  // add frame edges
}
```

Actually, let me make the cage walls with a frame look using thin bars. This gives a more "cage" appearance. But transparent walls are cleaner.

Let me go with transparent walls + frame bars for a nicer look.

Let me simplify: transparent walls (acrylic) with metallic frame edges.

Frame bars: vertical bars and horizontal rails.

This is getting complex. Let me just do:
- Transparent acrylic walls (4)
- Frame: thin boxes along edges (vertical corners + horizontal rails)

Let me write a helper.

Actually, to keep things stable and not overcomplicate, let me do:
- 4 transparent acrylic side walls
- A frame made of thin cylinders/boxes at corners and top

Let me just do the acrylic walls and add a simple frame around the top.

**Roof:**
Let me add a partial roof with bars, or skip it. A full transparent top would limit camera. Let me add an open top with some bars, or no roof so camera can look down. Actually a nice touch is a partial bar roof. But for simplicity and camera access, I'll leave the top open but add a frame rim at top of walls.

Let me reconsider — the requirement says "cage". A cage typically has bars. Let me do a hybrid: lower portion transparent acrylic, upper portion vertical bars. That looks like a real hamster cage/tank.

Let me do:
- Acrylic base walls (bottom half, height ~3)
- Metal bars (top half, height ~4) with horizontal rails

Actually, let me keep it manageable. I'll do:
- 4 acrylic walls full height
- Vertical bars overlay on top for cage aesthetic

Hmm, let me just go with acrylic walls + a frame. Bars add complexity. Let me make it look good with acrylic and corner frames.

Decision: Acrylic walls (semi-transparent) + metallic frame strips at the 4 vertical edges and top horizontal edges. This reads as a "tank/cage" and looks clean.

Let me write the frame helper:
```js
const frameMat = new THREE.MeshStandardMaterial({ color: '#ffd7a0', metalness: 0.6, roughness: 0.4 });
function frameBar(length, axis, x, y, z, thickness=0.35) {
  // creates a box
}
```

This is getting long. Let me just carefully write it all.

**Exercise Wheel (interactive object):**
A hamster wheel! This is a classic. Let me build a wheel:
- Two side discs (rings)
- Rungs/spokes
- An axle/stand

The wheel rotates when a hamster runs on it.

Let me place it in one corner.

```js
function makeWheel(x, z) {
  const wheel = new THREE.Group();
  const discMat = new THREE.MeshStandardMaterial({ color: '#ff8fab', roughness: 0.6, metalness: 0.1, flatShading: true });
  const rungMat = new THREE.MeshStandardMaterial({ color: '#ffd07b', roughness: 0.5, metalness: 0.2 });
  const radius = 2.4;
  // outer ring (torus)
  const ring = new THREE.Mesh(new THREE.TorusGeometry(radius, 0.25, 8, 24), discMat);
  wheel.add(ring);
  // second ring offset
  ...
  // rungs
  const spokes = 16;
  for (let i = 0; i < spokes; i++) {
    const angle = (i/spokes) * Math.PI*2;
    const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, radius*2 - 0.5, 6), rungMat);
    rung.rotation.z = angle;
    rung.position.set(Math.cos(angle)*0, ...);
    // position rung along its length
  }
  // stand
  ...
  wheel.position.set(x, 0.6, z);
  return wheel;
}
```

Let me think about wheel orientation: the wheel plane should be vertical (like a real hamster wheel). The axis of rotation is horizontal. So the wheel spins around a horizontal axis.

Let me set the wheel so it spins around the X axis (the axle points along X). The ring is in the YZ plane.

```js
// axle along X
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 2.2, 8), metalMat);
axle.rotation.z = Math.PI/2; // points along X
```

Wait, CylinderGeometry default is along Y. To point along X, rotate by PI/2 around Z.

The ring (torus) — torus is in XY plane by default with normal along Z. I want the torus in YZ plane with normal along X. So rotate torus by PI/2 around X... hmm let me think.

Torus default: lies in XY plane, the "hole" is along Z. To make hole along X, rotate around... rotating around X by 90° keeps X but swaps Y and Z. After rotation around X by 90°, the plane becomes YZ. Yes.

Let me just build it and test mentally. Actually, I'll construct the wheel spinning around the horizontal X-axis.

Let me define:
- WheelGroup contains the spinning part (ring + rungs) 
- The spin axis is X

Spinning part:
```js
const spinPart = new THREE.Group();
// torus in YZ plane:
const ring = new THREE.Mesh(new THREE.TorusGeometry(R, 0.2, 8, 28), discMat);
ring.rotation.y = Math.PI/2; // now normal along X? 
```

Torus default normal is Z. rotation.y = 90° rotates around Z, bringing normal to X? Rotating a vector (0,0,1) by 90° around Z gives (-1, 0, 0)... wait no. Rotation around Z by 90°: x' = x cos - y sin, y' = x sin + y cos, z unchanged. Vector (0,0,1) -> (0,0,1). That doesn't change Z-component. Hmm, so rotating torus around Y by 90°: vector (0,0,1) rotates around Y: x' = x cos z sin... 

Rotation around Y by angle θ: x' = x cosθ + z sinθ, z' = -x sinθ + z cosθ. For (0,0,1): x' = sinθ, z' = cosθ. At θ=90°: x'=1, z'=0. So normal becomes (1,0,0) = X. 

So ring.rotation.y = Math.PI/2 gives normal along X. Good, the wheel spins in... well the ring lies in YZ plane. When it rotates around X axis (spinPart.rotation.x increases), it spins like a wheel. 

Rungs: connect inner to outer along radial direction in YZ plane.
```js
for each rung at angle a in YZ plane:
  rung is a short cylinder along radial direction
  position at radius from center
```

A rung cylinder pointing radially in YZ plane. If rung angle a measured from Y axis in YZ plane:
radial direction = (0, cos a, sin a).
The cylinder default axis is Y. To align with radial (0, cos a, sin a), rotate around X by angle a. Because rotating Y=(0,1,0) around X by a: y' = cos a, z' = sin a. Yes gives (0, cos a, sin a). 

So rung.rotation.x = a, then position at (0, cos a * r_mid, sin a * r_mid) where r_mid is midpoint radius. Length = 2*(R - 0.4) roughly.

Let me set rung length = R*1.6, positioned at radius R*0.2 from center? Actually rungs span most of the diameter. Let me have rungs from near center-ish to near rim. Real hamster wheels have rungs across the diameter. Let me make rung length ~ 2*R*0.9 and center at origin of spinPart.

If rung length L centered at origin, positioned radially: position at distance 0 (center). But then all rungs pass through center. That's fine for a wheel (like a bicycle wheel spokes but full rungs).

Actually full-length rungs across the diameter, each centered at the wheel center. So position = (0,0,0) for all, just rotated. But they'd all overlap at center which is fine (they're thin).

Hmm, but a hamster stands on a rung near the bottom. Let me make rungs span the full diameter so there's a bottom rung to stand on.

Let me set rung length = R * 1.7 (slightly less than diameter 2R), centered at wheel center. Position at origin, rotation.x = a.

SpinPart group centered at wheel center. Wheel center y = R + 0.6 (resting on bedding so bottom rung touches bedding). Actually bottom should be near bedding. Let me set wheel center at y = R + 0.7 so the lowest rung (~ at radius R) is at y=0.7, just above bedding at 0.65.

Stand: holds the wheel axle. Two legs forming a U or a single post. Let me do a stand with a base and a vertical post, plus horizontal supports for the axle ends.

The axle is along X, length ~ 2.5 (wider than wheel). At each end, a support connects to a vertical post.

Let me make a stand:
- Vertical post at back (along Z, at x=0, z = some negative)
- Horizontal crossbar along X holding both axle ends
- Base/legs on ground

Simplest: a vertical post at (0, y, -backOffset) and a horizontal arm reaching forward to (0,y,0) holding the axle. Like a flag.

Let me do:
- Post: cylinder from ground up to wheel center height, at z = -1.5 (behind wheel)
- Arm: horizontal cylinder along Z from post top to wheel center, at x=0
- Axle rests in the arm end

Actually let me make a stable A-frame or just a post with an L arm. For stability look, two legs.

Let me keep it simple: a vertical post behind the wheel connected to the axle via a horizontal arm. Add a small base.

```js
const standMat = new THREE.MeshStandardMaterial({ color: '#a0d8ef', metalness: 0.3, roughness: 0.5 });
// vertical post
const post = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, R+0.7, 8), standMat);
post.position.set(0, (R+0.7)/2 + 0.6, -1.6);
wheelGroup.add(post);
// horizontal arm to axle
const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 1.6, 8), standMat);
arm.rotation.x = Math.PI/2; // along Z
arm.position.set(0, R+0.7, -0.8);
wheelGroup.add(arm);
// base feet
```

This is workable.

**Food bowl (another interactive object):**
A small bowl with pellets. Placed in another corner.

```js
function makeFoodBowl(x, z) {
  const bowl = new THREE.Group();
  const bowlMat = new THREE.MeshStandardMaterial({ color: '#8ce99a', roughness: 0.6, flatShading: true });
  // bowl: use a lathe or truncated cone
  const shape = new THREE.LathePoints... 
}
```

LatheGeometry for a bowl: define profile points.
```js
const pts = [];
pts.push(new THREE.Vector2(0.1, 0));
pts.push(new THREE.Vector2(1.0, 0));
pts.push(new THREE.Vector2(1.1, 0.4));
pts.push(new THREE.Vector2(0.95, 0.5));
const bowlGeo = new THREE.LatheGeometry(pts, 16);
```

Pellets: small spheres/cubes inside.

**Tunnel (optional third object):**
A curved or straight tube. Let me add one for extra fun. A half-pipe tunnel or a straight cylinder cut. Let me do a simple tunnel: a cylinder lying horizontally, hamsters can walk through. Maybe optional.

Let me include wheel + food bowl + tunnel for variety. But requirement says "one interactive object" minimum. I'll do wheel (primary interactive), food bowl, and a tunnel as decorative+interactive.

**Hamsters:**
Let me create a function makeHamster(colorScheme) returning a Group.

Body: low-poly sphere (icosahedron detail 0 or 1) for chunky look, or a squashed sphere.
Head: sphere attached to front.
Ears: two small spheres.
Eyes: black spheres with white highlight.
Nose: small pink sphere.
Cheeks: two small spheres.
Feet: small cylinders/boxes under body.
Tail: tiny sphere at back.
Whiskers maybe.

For low-poly cute look, use flatShading.

Let me define a hamster as a group with sub-parts so I can animate (walk cycle = feet bobbing, body bobbing, head turning).

Movement behavior:
Each hamster has:
- state: 'wander' | 'pause' | 'goToObject' | 'interact'
- target position
- speed
- phase for animation
- a chosen object to interact with (wheel or bowl)

Behavior loop:
- Wander: pick random target within cage, walk toward it, when arrived, maybe pause.
- Pause: stand still for a while (with slight idle animation), then pick new target.
- Occasionally go to interact with object (wheel or bowl), interact for a bit, then resume wandering.

Let me implement with a timer.

Animation:
- Walking: body bobs up/down (sine), maybe slight rotation. Feet alternate (I can animate legs or just bob the whole body).
- Pausing: subtle breathing (scale body slightly), head turns.
- Interacting with wheel: hamster positions at bottom of wheel, wheel spins fast, hamster bobs.
- Interacting with bowl: hamster at bowl, head dips (eating motion).

Let me implement a simple but effective walk: bob the group.y with sine, and tilt slightly. Add leg animation using small leg meshes that swing.

Let me keep legs simple: 4 small capsules, animate rotation to simulate walking when moving.

Actually, to reduce complexity, I'll do body bob + a little tail wiggle + ear flop. Legs can be static or slight bob. Let me add simple leg swinging for cuteness.

Let me define hamster legs as two pairs (front-left, front-right, back-left, back-right). Animate by rotating around a hip joint? Complex. Instead, I'll just move them slightly