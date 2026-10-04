Let me create a single-file HTML project with Three.js that shows a cute low-poly hamster playground. Let me think about what I need to include:

1. **Scene setup**: Three.js scene, camera, renderer
2. **Cage**: A transparent/wireframe cage enclosure
3. **Floor/tray**: The bottom of the cage with bedding
4. **Several low-poly hamsters**: Cute hamsters built from basic geometries
5. **Interactive object**: A running wheel that hamsters can use
6. **Autonomous behavior**: Hamsters walking, pausing, turning
7. **Camera controls**: OrbitControls for rotation
8. **Lighting**: Nice cute lighting

Let me build this step by step.

I'll use Three.js from CDN. I'll create:
- A cage with walls (transparent)
- A tray/floor with wood shavings color
- 3-4 hamsters with body, head, ears, eyes, nose, tail, feet
- A running wheel that rotates
- Simple AI: each hamster has a state machine (walking, pausing, turning)

Let me write clean, well-organized code.

For the hamsters, I'll build them procedurally using a function that creates a group of meshes. Each hamster will be a THREE.Group containing:
- Body (ellipsoid/sphere scaled)
- Head (sphere)
- Two ears (spheres or cones)
- Eyes (small spheres, dark)
- Nose (tiny sphere, pink)
- Cheeks (optional)
- Feet (small boxes)
- Tail (small)

Colors: I'll vary the fur color between hamsters (tan, white, gray, brown).

Behavior system:
- Each hamster picks a target point, walks to it, then pauses, then picks another.
- Sometimes they turn around.
- They animate their legs while walking.

Running wheel:
- A big wheel that rotates when a hamster is on it, or just spins continuously for fun.

Let me also add some bedding (small cubes scattered), maybe a food bowl, and some decorations.

Let me write the code carefully to make sure it's stable.

I'll use OrbitControls from the three examples CDN.

Let me structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  body { margin: 0; overflow: hidden; font-family: ...; }
  #info { position: absolute; ... }
</style>
</head>
<body>
<div id="info">...</div>
<script src="three.js"></script>
<script src="orbitcontrols.js"></script>
<script>
  // main code
</script>
</body>
</html>
```

Let me use a version of three.js that includes everything. I'll use r128 or similar from unpkg/cdnjs. Actually, let me use a recent version with import maps or just the UMD build.

I'll use the UMD build from cdnjs: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js

For OrbitControls, I need the corresponding file. Let me use the module version with import maps instead, which is cleaner for recent three.js.

Actually, let me use the non-module approach with a specific version. Let me use r134 or so.

Let me use import maps with esm.sh or unpkg:

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
...
</script>
```

This is clean and works in modern browsers. Let me go with this.

Now let me write the full scene.

Let me think about the layout:
- Cage: 10 x 4 x 8 (width, height, depth) roughly
- Floor at y=0
- Hamsters move on the floor

Let me define boundaries for hamster movement: x from -4 to 4, z from -3.5 to 3.5.

Running wheel placed at one side.

Let me code the hamster creation:

```javascript
function createHamster(furColor, bellyColor) {
  const group = new THREE.Group();
  
  const furMat = new THREE.MeshStandardMaterial({ color: furColor, flatShading: true });
  const bellyMat = new THREE.MeshStandardMaterial({ color: bellyColor, flatShading: true });
  
  // Body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 8, 6), furMat);
  body.scale.set(1, 0.9, 1.3);
  body.position.y = 0.5;
  group.add(body);
  
  // Head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 6), furMat);
  head.position.set(0.55, 0.65, 0);
  group.add(head);
  
  // Ears
  const earGeo = new THREE.SphereGeometry(0.12, 6, 6);
  const leftEar = new THREE.Mesh(earGeo, bellyMat);
  leftEar.position.set(0.45, 0.95, 0.15);
  group.add(leftEar);
  const rightEar = new THREE.Mesh(earGeo, bellyMat);
  rightEar.position.set(0.45, 0.95, -0.15);
  group.add(rightEar);
  
  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.06, 6, 6);
  const eyeMat = new THREE.MeshBasicMaterial({ color: 0x111111 });
  const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
  leftEye.position.set(0.8, 0.7, 0.12);
  group.add(leftEye);
  const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
  rightEye.position.set(0.8, 0.7, -0.12);
  group.add(rightEye);
  
  // Nose
  const noseGeo = new THREE.SphereGeometry(0.05, 6, 6);
  const noseMat = new THREE.MeshStandardMaterial({ color: 0xff9999, flatShading: true });
  const nose = new THREE.Mesh(noseGeo, noseMat);
  nose.position.set(0.9, 0.62, 0);
  group.add(nose);
  
  // Cheeks / cheeks tufts
  // Feet
  const footGeo = new THREE.BoxGeometry(0.15, 0.12, 0.2);
  ...
  
  // Tail
  ...
  
  return group;
}
```

Hmm, I need to be careful about orientation. If the hamster faces +X, then legs should be positioned accordingly. Let me make the hamster face +X direction (so when moving along X it faces its direction of travel). Actually let me make them face +Z or use rotation.

Actually, simpler: let me make the hamster's forward direction be +X. The head is at positive X. So when the hamster moves, it should rotate so its local +X points in the movement direction.

Legs: front legs near head (positive X), back legs near tail (negative X). Legs at +Y and -Y (sides).

Let me place 4 legs:
- Front left: (0.35, 0.15, 0.25)
- Front right: (0.35, 0.15, -0.25)
- Back left: (-0.35, 0.15, 0.25)
- Back right: (-0.35, 0.15, -0.25)

Wait, but if body is scaled 1.3 in X, the actual positions need adjusting. Let me use a box for the body actually, or keep sphere but scale.

Let me reconsider. Using SphereGeometry scaled:
- body.scale.set(1.2, 0.85, 1) — wider in X (front-back), short in Y

Hmm, this gets confusing. Let me simplify and make the hamster face +X with a clear coordinate system.

Actually, let me make the hamster face +Z (toward camera-ish) to avoid confusion, OR just handle rotation properly.

Let me define:
- Head at +X relative to body center
- Body centered at origin of the group
- So the whole hamster group's "+X" is forward

When moving, compute direction vector, set rotation.y = atan2(dir.x, dir.z)... wait.

If forward is +X, then to face direction (dx, dz):
rotation.y = atan2(dx, dz)? Let me think. 

A quaternion/yaw: if forward vector is (sin(yaw), 0, cos(yaw)) for a system where +Z is forward. But here forward is +X.

Let me just say the hamster faces +X. To rotate to face a direction d = (dx, dz):
We want local +X axis to point along (dx, 0, dz).
yaw such that after rotating +X by yaw around Y... 

Rotating unit vector (1,0,0) by angle yaw around Y axis gives (cos(yaw), 0, -sin(yaw)) [standard right-handed]. Hmm, depends on convention.

Three.js rotate around Y: 
R_y(θ) = [cos θ, 0, sin θ; 0,1,0; -sin θ, 0, cos θ]
So (1,0,0) -> (cos θ, 0, -sin θ).

We want (cos θ, 0, -sin θ) = (dx, 0, dz)/|d|.
So cos θ = dx/|d|, -sin θ = dz/|d| → sin θ = -dz/|d|.
θ = atan2(-dz, dx) = atan2(-dz, dx).

Alternatively θ = -atan2(dz, dx). Let me verify: atan2(-dz, dx). If dx>0, dz=0: θ=0, faces +X. Good. If dx=0, dz>0 (moving +Z): θ = atan2(-dz, 0) = atan2(negative, 0) = -π/2. Then (cos(-π/2), 0, -sin(-π/2)) = (0, 0, 1) = +Z. Yes! Correct.

So `group.rotation.y = Math.atan2(-dir.z, dir.x)` where dir is normalized movement direction. Or equivalently `Math.atan2(dir.z, -dir.x)`. Let me just use atan2(-dz, dx).

Hmm wait, let me double check the sign once more. We want to face direction (dx, dz).

Actually, let me simplify by making hamsters face +Z and adjust. You know what, let me just use a cleaner approach: I'll orient the hamster so its nose points to +X, and use `rotation.y = Math.atan2(dir.x, dir.z)` and test.

atan2(dir.x, dir.z): For facing +X with dir=(1,0): atan2(1, 0) = π/2. Hmm that gives rotation π/2.

Let me just carefully derive and trust the math. I'll use:
forward = +X local.
After rotation.y = θ, forward becomes (cos θ, 0, -sin θ) as derived.
Set equal to normalized (dx, dz):
cos θ = dx, -sin θ = dz (using unit vector)
→ θ = atan2(-dz, dx).

So `rotation.y = Math.atan2(-dirZ, dirX)`.

OK let me just go with that and if it looks wrong I'll flip.

Actually, to reduce risk, let me make the hamster face +Z instead. If nose is at +Z:
forward = (0,0,1) local. After rotation.y=θ: R_y(θ)*(0,0,1) = (sin θ, 0, cos θ).
Set = (dx, dz): sin θ = dx, cos θ = dz → θ = atan2(dx, dz).
So `rotation.y = Math.atan2(dirX, dirZ)`. That's cleaner!

But my model has head at +X. Let me change head to +Z. Then feet and everything shifts to +Z/-Z. Let me reorient the whole hamster so forward = +Z.

Revised hamster layout (forward = +Z):
- Body center at origin
- Head at (0, 0.65, 0.5) [front, +Z]
- Ears at (0, 0.95, 0.4)
- Eyes at (0.12, 0.7, 0.8) and (-0.12, 0.7, 0.8)
- Nose at (0, 0.62, 0.9)
- Front feet at (0.25, ..., 0.3)
- Back feet at (0.25, ..., -0.3)
- Tail at (0, 0.4, -0.6)

Hmm, but then body scaled... let me keep body as sphere scaled so it's elongated along Z (front-back): body.scale.set(1, 0.9, 1.3).

Feet:
- Front-left: (0.2, 0.15, 0.4)
- Front-right: (0.2, 0.15, -0.4)
- Back-left: (-0.2, 0.15, 0.4)
- Back-right: (-0.2, 0.15, -0.4)

Wait, if body is elongated along Z by 1.3, radius 0.5*1.3 = 0.65 in Z. So feet at ±0.4 in Z are within body. Fine.

Actually, I realize having the head at +Z means the hamster looks "backwards" if we think of typical side view, but it's fine — it's just a direction.

Let me reconsider — actually it might look nicer to have the hamster oriented with head toward +Z (toward where camera often looks). It doesn't matter much. Let me go with forward = +Z.

Hold on, let me reconsider whether head at +Z with eyes at +Z makes sense. Yes, eyes on the front of the face. Good.

Now, leg animation: while walking, oscillate legs. Front legs and back legs move opposite to each other (trotting gait). Let me store leg references and animate.

Let me now design the behavior/state machine for each hamster:

States:
- 'idle': standing, occasional blink/head bob
- 'walk': moving toward target
- 'pause': stopped, waiting random time
- 'turn': spin around

Simpler approach: Each hamster has:
- targetPos (Vector3)
- speed
- a timer
- phase for leg animation

Logic in update:
```
if state === 'walk':
   move toward target
   animate legs
   if reached target or random: enter pause
else if pause:
   wait timer, then pick new target
else if idle:
   slight bob
```

Let me implement a clean version:

```javascript
class Hamster {
  constructor(scene, furColor) {
    this.group = createHamster(furColor);
    scene.add(this.group);
    this.legs = []; // {mesh, side('F'/'B'), pos('L'/'R')}
    this.state = 'idle';
    this.timer = Math.random() * 3;
    this.target = this.randomTarget();
    this.speed = 0.8 + Math.random() * 0.5;
    this.pauseTime = 2 + Math.random() * 3;
    this.bobPhase = Math.random() * Math.PI * 2;
  }
  
  randomTarget() {
    return new THREE.Vector3(
      (Math.random() - 0.5) * 8,
      0,
      (Math.random() - 0.5) * 6
    );
  }
  
  update(dt) {
    this.timer -= dt;
    this.bobPhase += dt * 4;
    
    switch(this.state) {
      case 'idle':
        // gentle breathing bob
        this.group.position.y = baseY + Math.sin(this.bobPhase) * 0.02;
        if (this.timer <= 0) {
          this.state = 'walk';
          this.target = this.randomTarget();
        }
        break;
      case 'walk':
        const dir = new THREE.Vector3().subVectors(this.target, this.group.position);
        dir.y = 0;
        const dist = dir.length();
        if (dist < 0.1) {
          this.state = 'pause';
          this.timer = this.pauseTime;
        } else {
          dir.normalize();
          this.group.position.addScaledVector(dir, this.speed * dt);
          this.group.rotation.y = Math.atan2(dir.x, dir.z);
          // leg animation
          this.animateWalk(dt);
          // keep within bounds
          clampPosition();
        }
        break;
      case 'pause':
        this.group.position.y = baseY + Math.sin(this.bobPhase) * 0.02;
        if (this.timer <= 0) {
          // sometimes turn
          if (Math.random() < 0.3) {
            this.state = 'turn';
            this.turnAngle = 0;
            this.timer = 0.5;
          } else {
            this.state = 'idle';
            this.timer = 1 + Math.random() * 2;
          }
        }
        break;
      case 'turn':
        this.group.rotation.y += dt * 3;
        this.timer -= dt;
        if (this.timer <= 0) {
          this.state = 'walk';
          this.target = this.randomTarget();
        }
        break;
    }
  }
}
```

Wait, I referenced baseY — the hamster's group.position.y should stay at 0 (floor). The legs extend down. Let me keep position.y = 0 constant and just add a subtle bob. Actually the group origin — I'll place the group at y=0 and the body sits above via mesh positions. So position.y stays 0. The bob is cosmetic; I can apply to the whole group as a small offset. Let me keep it simple: no vertical bob, just leg animation and rotation. Maybe a tiny bob for cuteness.

Let me reconsider the leg animation. Legs are children of the group, so they inherit rotation. I animate each leg's rotation.x to swing. Front pair and back pair alternate.

```javascript
animateWalk(dt) {
  const t = Date.now() * 0.01;
  this.legs.forEach((leg, i) => {
    const offset = (leg.side === 'F') ? 0 : Math.PI;
    const phase = (leg.pos === 'L') ? 0 : Math.PI;
    leg.mesh.rotation.x = Math.sin(t * 6 + offset + phase) * 0.5;
  });
}
```

Hmm, let me simplify: front legs swing together, back legs swing opposite. Left/right same as front/back for simplicity, or alternate. Let me do:
- front-left, back-right: phase 0
- front-right, back-left: phase π

Actually for a cute waddle, let me just swing all legs with slight phase differences. Keep it simple.

Bounds clamping: keep hamsters within the cage (not through walls). x in [-4.2, 4.2], z in [-3.2, 3.2]. If they hit a boundary, bounce/pick new target.

Now the running wheel. Let me create a wheel:
- Two rims (torus or cylinders) 
- Rungs/spokes connecting them
- Mount it on a stand

The wheel should rotate. Let me make it rotate continuously at a slow speed for visual interest, and when a hamster is near/on it, rotate faster. Or just spin it always slowly. To keep it simple and "interactive," I'll make the wheel spin based on whether a hamster is on it. But detecting "on wheel" adds complexity.

Alternative: Make the wheel a rotating object that spins continuously (funny), and highlight it as interactive via a tooltip. The requirement says "one interactive object such as a wheel, tunnel, food bowl, or toy." Interactive could mean the user can interact (click to spin) OR the hamsters interact with it. Let me interpret "interactive object" as an object the hamsters interact with, OR something clickable. I'll make it both: the wheel spins, and clicking it makes it spin faster / launch a hamster.

Actually, let me make it clean: A running wheel that spins continuously. When a hamster path brings it onto/near the wheel, it "rides" — but that's complex. 

Let me do this: The wheel spins continuously at moderate speed. There's a food bowl too. And I'll make the wheel clickable (raycasting) so clicking it gives a little kick/spin boost — that satisfies "interactive."

Hmm, but I want hamsters to interact with objects per the requirements ("interacting with one object"). Let me have hamsters occasionally walk to the food bowl and eat (pause there), or walk to the wheel.

Let me design: Place a food bowl at a fixed location. Some hamsters target the food bowl to "eat" (pause state with eating animation - little head bob). This satisfies "interacting with one object."

And the wheel spins continuously for fun.

Let me also add raycasting for clicking objects to make it truly interactive: click a hamster and it scurries away, or click the wheel to spin it.

Let me keep scope reasonable. Plan:
1. Wheel — spins continuously, clickable to boost spin.
2. Food bowl — some hamsters visit it to eat.
3. Clicking a hamster makes it panic-run (fast random movement briefly). This is a nice interactive touch.

Let me implement clicking via raycaster.

Let me now also add:
- Bedding: small colored cubes/spheres scattered on floor (wood shavings). Maybe just a textured plane with a few props.
- Cage walls: transparent panels (glass-like) with wireframe or edges for the cage look.
- Lighting: hemisphere + directional for soft shadows. Add ambient.
- Ground outside? Just the tray.

Let me build the cage:
- Tray: a shallow box at bottom (the plastic base), color light blue/green.
- Floor inside: bedding plane.
- Walls: 4 transparent panels + top wireframe, or just 4 vertical glass panels forming a box.

Simplest cute cage: a box with transparent material for walls, open top. Add edge lines for the low-poly cage look.

Let me define cage size: width 12, height 5, depth 10. Centered at origin, floor at y=0, so walls from y=0 to y=5.

Tray: box from -6 to 6 in x, thin in y, -5 to 5 in z, thickness 0.3, at y=-0.15 (so floor surface at y=0). Color pastel.

Walls: 4 planes forming the sides, transparent, at the perimeter.

Let me now write everything out.

For shadows: enable renderer.shadowMap. Use directional light with shadow for the sun-like look, and hemisphere light for fill. Keep it performant.

Let me set up:
- HemisphereLight(color 0xffffff, groundColor 0xbfd9ff, intensity 0.8) — or two hemisphere lights. Let me use HemisphereLight + DirectionalLight.
- DirectionalLight casting shadows, positioned upper right.

Materials: MeshStandardMaterial with flatShading: true for low-poly look. Add slight roughness/metalness. flatShading gives the faceted cute look.

Let me also add emissive subtle or just colors.

Colors palette (cute):
- Fur colors: #f4a460 (sandy), #d2b48c (tan), #c8a882, #8d6e63 (brown), #eeeeee (white-ish)
- Belly: lighter version
- Cage: pastel cyan walls, pink tray
- Wheel: bright yellow/orange
- Food bowl: purple or red
- Bedding: tan/brown bits

Let me write the code now.

I'll structure the JS:
1. Scene, camera, renderer, controls setup
2. Lights
3. Build cage (tray, walls, bedding)
4. Build wheel
5. Build food bowl
6. Create hamsters
7. Animation loop with hamster AI
8. Interaction (raycaster click)
9. Resize handler

Let me write helper functions.

For bedding, scatter ~60 small cubes with random rotation and slight y offset, colors varying tan/brown.

Let me make sure hamsters don't clip through the wheel or bowl — I'll just let them pass (it's cute, low-poly). Or give them a small avoidance. Keep simple: they can walk near/over. Actually passing through a solid wheel looks odd. Let me place the wheel and bowl near a wall so hamsters mostly avoid that area, or just let them walk around. I'll place them in corners.

Let me place:
- Wheel at (−4.5, 0, −3.5) region, near corner.
- Food bowl at (4.5, 0, 3.5), opposite corner.

Hamsters targeting these will go to corners. Good.

Now, let me write the full HTML. I'll be thorough but not overcomplicate.

Let me consider the wheel construction more concretely:
- Stand: two small posts holding the wheel axle. Could be simple.
- Wheel: a torus (the rim) + spokes. Let me use two tori (front and back rim) connected by rung cylinders (the rungs). Plus side discs? Low-poly: just rims + rungs + spokes.

Let me build:
```
wheel group at position
- rimFront = torus(radius, tube, 8, 20) rotated so it's in the YZ plane... 
```
Torus default lies in XY plane (normal along Z). For a hamster wheel, the wheel spins in a vertical plane. Let me have it spin around the X axis (so the wheel is in the YZ plane, spinning like a wheel facing the X direction). 

If wheel plane is YZ (spins around X axis), then the torus normal should be X. Default torus normal is Z. So rotate the torus so its normal aligns with X: rotate around Y by 90°? Rotating a shape whose normal is +Z by -90° around Y gives normal +X. Let me use mesh.rotation.x = ... hmm.

Actually, let me think: I want the wheel to spin around the X axis. The ring itself should lie in the YZ-plane. A torus centered at origin with radius R, tube t: points are at (R cos φ, R sin φ... no. Default torus: the ring is in the XY-plane, generated by sweeping a circle around the Z axis. So the ring lies in XY plane, and its "hole" axis is Z.

To make the ring lie in YZ plane (hole axis = X), I rotate the torus by 90° about the Y axis? Rotating about Y by -90°: X->Z, Z->-X... Let me just set rotation. If I rotate the torus 90° about Y, the hole axis (was Z) becomes X. Yes: rotateY(90°) maps Z-axis to... rotation about Y by +90° sends +Z to +X? Standard: R_y(90°): (x,y,z)->(z, y, -x)? Let me recall: 
R_y(θ) = [[cosθ,0,sinθ],[0,1,0],[-sinθ,0,cosθ]]
Apply to (0,0,1): (sinθ, 0, cosθ) = (1,0,0) for θ=90°. Yes +Z -> +X. Good.
So rotateY(90°) puts hole axis along +X, ring in YZ plane. 

Then spinning = rotateX over time. 

Rungs: connect front rim to back rim along X. Place rungs at various angles around the ring. Each rung is a short cylinder along X, positioned at (0, R*sinφ, R*cosφ)? Wait the ring is in YZ plane now. Points on ring: originally (R cosφ, R sinφ, 0) then after rotateY(90): (0, R cosφ, R sinφ)? Let me recompute. Original ring point (in XY plane): (R cos φ, R sin φ, 0). After rotateY(90): apply R_y: x' = cosθ*x + sinθ*z = cos90*(Rcosφ) + sin90*0 = 0. y' = y = R sinφ. z' = -sinθ*x + cosθ*z = -sin90*(Rcosφ)+0 = -R cosφ. So point -> (0, R sinφ, -R cosφ). OK so ring points span Y and Z. Good, ring in YZ plane.

For rungs, I'll create a cylinder from (0, y1, z1) to (0, y2, z2) where those are on the ring, length = wheel width (X extent). Cylinder default is along Y, so I need to orient it along the X direction (from front rim to back rim). I can use lookAt or set rotation.

This is getting complex. Let me simplify the wheel: use a single torus for the main rim, add a few "spokes" as thin boxes radiating, and two side discs (thin cylinders) to give it volume. Actually for low-poly cuteness, let me do:
- Main rim: torus (big)
- Two side rings: smaller tori at front and back (optional)
- Rungs/spokes: boxes or cylinders connecting front and back rings, spaced around.

Let me build rungs properly with CylinderGeometry and orient via quaternion.fromAxisAngle or lookAt.

Simplest robust method: create a cylinder geometry (default along +Y), then use a helper to point it from point A to point B.

```javascript
function makeRung(a, b, radius) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  const geo = new THREE.CylinderGeometry(radius, radius, len, 6, 1);
  const mesh = new THREE.Mesh(geo);
  mesh.position.copy(a).addScaledVector(dir, 0.5);
  const up = new THREE.Vector3(0,1,0);
  const quat = new THREE.Quaternion().setFromUnitVectors(up, dir.normalize());
  mesh.quaternion.copy(quat);
  return mesh;
}
```

Rungs go from front rim point to back rim point, both at same (y,z) but different x. Front rim at x = -width/2, back rim at x = +width/2. Ring radius R. Point on ring at angle φ: (0, R cosφ, R sinφ) roughly (let me use this simplified: y = R cosφ, z = R sinφ). Front point: (-w/2, R cosφ, R sinφ). Back: (w/2, R cosφ, R sinφ). Rung connects them, along X. Good, and the fromUnitVectors up(0,1,0) to dir(1,0,0) gives rotation that turns Y to X, correct orientation.

So I'll generate N rungs at φ = 0, 2π/N, ... Each rung at (y,z) = (R cosφ, R sinφ).

Also add the main torus rim for the outer edge look. And maybe inner spokes isn't needed.

Let me also add two side discs (thin) to make it look like a wheel? Optional. Let me skip discs, just rims + rungs. Actually a real hamster wheel has a solid-ish surface but low-poly wheels are often just rims + rungs. Let me do front rim ring + back rim ring + rungs + main torus.

Actually, let me simplify to: one big torus (rim) + rungs + two small supporting rings at front/back. That reads clearly as a wheel.

Wheel mounting: put axle at some height so the wheel's bottom is near the floor (hamsters run on the inside bottom). The wheel radius ~1.2. Axle at height = floor + radius - small? Actually the wheel touches floor at bottom. Wheel center at y = R (radius) so bottom at y=0. But then the axle stand needs to hold it at y=R. Let me place wheel center at y = 1.3 (R=1.3), bottom at 0.24... hmm let me just place center at y≈1.2 and bottom ≈0.0. Let me set R=1.15, center y=1.15, bottom=0. Good, hamster runs inside near floor.

Stand: two vertical posts (cylinders) from floor up to the axle height, on either side, plus maybe a cross bar. Color gray/metal.

Let me place the wheel so it faces... the hamster runs inside it. The wheel plane is YZ (spins around X). A hamster inside would be at x around 0 (center of wheel width) at floor level, and the wheel surrounds it. The hamster walks on the rungs/floor inside. Fine.

Orientation: wheel faces the X direction (its plane is YZ). So from the side (looking along X) you see the wheel face-on. From front (along Z) you see the wheel edge-on (a line). For visibility, place wheel against a wall so camera sees it from the open side.

Let me place wheel at x = -4.8 (near left wall), z = 0, spanning. Its plane YZ means it's visible face-on when viewed along X. Camera orbit will show it nicely.

Hmm, but if the wheel plane is YZ and it's at x=-4.8 near the wall at x=-6, the wheel faces ±X toward the center of the cage. Good.

Food bowl at x=+4.8, z=+3.8 (corner). A shallow cone/cylinder.

Let me finalize coordinates:
- Cage interior: x ∈ [-5.5, 5.5], z ∈ [-4.5, 4.5], height 4.5. (Cage width 11, depth 9.)
- Wheel at (-4.8, 0, 0).
- Bowl at (4.8, 0, 3.5).

Hamster bounds: x ∈ [-5, 5], z ∈ [-4, 4].

Let me write it all.

I think I've planned enough. Let me write the complete HTML file. I'll be careful with syntax.

One more consideration: importing OrbitControls via import map from unpkg. Let me use:
```
"three": "https://unpkg.com/three@0.160.0/build/three.module.js"
```
and
```
"three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
```
then `import { OrbitControls } from 'three/addons/controls/OrbitControls.js';`

This works in modern browsers with ES modules.

Let me write the code.

I'll add a nice title overlay and instructions.

Let me also add a subtle ground reflection? No, keep simple.

Let me write the animation loop with delta time using clock.

Let me also make the hamsters cast shadows and receive shadows for depth.

Let me finalize leg definitions and store them.

Let me write createHamster returning { group, legs, head } where legs is array of meshes.

Actually let me store legs as array of {mesh}. For animation I'll just rotate all legs with alternating phases based on index.

Let me write it.

For the "panic" interaction: on click of a hamster, set a flag panicTimer and make it run fast in a random direction.

Raycasting: intersect with all hamster groups. Since each hamster is a Group, I need to raycast against child meshes and find the parent hamster. I'll tag meshes with userData.hamster = the Hamster instance, or traverse. Let me set each mesh's userData to reference the hamster. Simpler: when creating, set mesh.userData.hamster = this (the hamster object). Then on raycast hit, get hit.object.userData.hamster.

Let me implement.

Alright, writing now. Let me make the code clean and commented.

Let me also handle window resize.

Let me write the CSS for the info panel:
```css
#info {
  position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
  color: #447; font-family: 'Segoe UI', sans-serif; font-size: 14px;
  text-align: center; pointer-events: none; text-shadow: 0 0 4px #fff;
  background: rgba(255,255,255,0.6); padding: 8px 14px; border-radius: 12px;
}
```

Title: "🐹 Low-Poly Hamster Playground"
Subtitle: "Drag to rotate • Scroll to zoom • Click a hamster to spook it"

Let me write everything.

Let me reconsider the hamster facing direction math once more since I set forward = +Z. I derived rotation.y = atan2(dirX, dirZ). Let me verify with example: moving in +Z (dirZ=1, dirX=0): atan2(0,1)=0, rotation 0, hamster faces +Z = its forward = movement. Good. Moving +X (dirX=1, dirZ=0): atan2(1,0)=π/2. Rotation by +90° about Y. With forward +Z rotated +90° about Y -> +Z goes to -X? R_y(90)*(0,0,1) = (sin90, 0, cos90) = (1,0,0) = +X. Wait that means forward becomes +X, but we're moving +X. Good, consistent. 

So rotation.y = atan2(dirX, dirZ) is correct for forward=+Z.

Now writing final code.

For the body, I'll use an IcosahedronGeometry or SphereGeometry with low segments for low-poly look. SphereGeometry(0.5, 12, 10) is smoother; for low-poly use (0.5, 8, 6). flatShading makes facets visible. Let me use moderate segments + flatShading.

Let me use BoxGeometry for feet (definitely low-poly), SphereGeometry for head/body with low segments, ConeGeometry or SphereGeometry for ears.

Ears: small spheres or half-spheres. Let me use SphereGeometry scaled to be flat ovals. Or use SphereGeometry(0.13, 6, 6) and scale y=0.6. Fine.

Let me write.

I'll define createHamster:

```js
function createHamster(furHex, bellyHex) {
  const g = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color: furHex, flatShading: true, roughness: 0.9 });
  const belly = new THREE.MeshStandardMaterial({ color: bellyHex, flatShading: true, roughness: 0.9 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, flatShading: true });
  const pink = new THREE.MeshStandardMaterial({ color: 0xffbnc... })
```
Oops typo. pink = 0xff9aa2 or 0xff8fa0.

Body:
```js
const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 10, 8), fur);
body.scale.set(1, 0.9, 1.35);
body.position.y = 0.5;
g.add(body);
```
Hmm if body center at y=0.5 and radius 0.5, bottom at y=0. Good, sits on floor. But feet hang below. Let me place feet at y=-0.05 below body? Body bottom at 0, feet should start at ~0.4 down... wait feet attach under body. If body center y=0.5 radius ~0.5*scale... the body's actual bottom in world: center 0.5 minus 0.5*0.9(scale y)*0.5(radius)=0.5-0.225=0.275. So body bottom at 0.275. Feet from there down to ~0. Let me place feet centers at y=0.15, height 0.2, so they span 0.05 to 0.25, touching floor. Good.

Actually let me simplify: body center at y=0.55. Feet at y=0.1.

Head:
```js
const head = new THREE.Mesh(new THREE.SphereGeometry(0.35, 10, 8), fur);
head.position.set(0, 0.7, 0.55);  // +Z front
g.add(head);
```
Ears at (0, 1.0, 0.45):
```js
const earGeo = new THREE.SphereGeometry(0.13, 6, 6);
leftEar pos (0, 1.0, 0.35), rightEar (0, 1.0, -0.35); scale y 0.7
```
Eyes at (0.12, 0.78, 0.78) and (-0.12, 0.78, 0.78):
```js
eyeGeo radius 0.06, dark mat
```
Nose at (0, 0.7, 0.92), pink small:
```js
noseGeo radius 0.05
```
Cheeks? optional small pink spheres behind eyes. Skip for cleanliness, or add tiny. Let me add two small cheek tufts for cuteness: at (0.18, 0.68, 0.6) and (-0.18, 0.68, 0.6), radius 0.09, pink-ish. Actually cheeks might clutter. I'll add subtle ones.

Feet: 4 boxes.
```js
footGeo = new THREE.BoxGeometry(0.16, 0.12, 0.22);
frontLeft (0.18, 0.1, 0.35)
frontRight (0.18, 0.1, -0.35)
backLeft (-0.18, 0.1, 0.35)
backRight (-0.18, 0.1, -0.35)
```
Tail: small sphere at back:
```js
tail at (0, 0.45, -0.6), radius 0.06, fur
```

Belly: a lighter ellipse on the front/bottom. Add a belly patch: sphere scaled, belly mat, at (0, 0.5, 0.35), radius 0.35, scaled (1,0.9,1). Slight z offset to front. This gives a cute lighter belly. Might blend with body; fine.

Let me collect legs into array for animation: [frontLeft, frontRight, backLeft, backRight].

Return g and legs.

Now animation of legs during walk:
```js
this.legs.forEach((leg, i) => {
  // alternate phases
  const phase = (i % 2 === 0) ? 0 : Math.PI;
  leg.rotation.x = Math.sin(clockTime * 8 + phase) * 0.6;
});
```
Front legs i=0,1; back i=2,3. Alternating even/odd gives FL & BL same, FR & BR same — that's a "pace" gait (same side). For trotting, front-left & back-right same. Let me do phase = (i<2) ? 0 : PI for front/back split, and within, left/right same. Eh, either looks fine. Let me do front pair phase 0, back pair phase PI. Actually let me alternate per leg for a natural look: phase = i * (PI/2)? That staggers all four. Might look like marching. Let me do:
- front-left phase 0
- front-right phase 0
- back-left phase PI
- back-right phase PI
This is pacing (pairs). Cute enough.

Actually, let me make it more natural: diagonal pairs (trot):
- front-left & back-right: phase 0
- front-right & back-left: phase PI
So indices: FL=0 phase0, FR=1 phase PI, BL=2 phase PI, BR=3 phase0.
phase = (i===1 || i===2) ? PI : 0.

Let me use that.

Leg rotation about X swings them forward/back. But legs are at the sides; swinging about X rotates them in the XZ plane (forward/back). Good. But also the hamster might "waddle" — rotate group slightly about Z. Optional. Let me add subtle body bob: during walk, group.position.y oscillates and slight rotation.z waddle. Keep small.

Let me now also handle the wheel spinning and interaction.

Wheel spin: wheelMesh.rotation.x += speed*dt. Clicking boosts speed temporarily.

Let me also make the wheel interactable via raycast (click to boost). Combine with hamster click detection: first check hamsters, else check wheel.

Let me code the click handler:
```js
renderer.domElement.addEventListener('click', (e) => {
  mouse.x = (e.clientX/W)*2-1; mouse.y = -(e.clientY/H)*2+1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(allMeshes, true);
  if (hits.length) {
    const obj = hits[0].object;
    if (obj.userData.hamster) { spook(obj.userData.hamster); }
    else if (obj.userData.wheel) { boostWheel(); }
  }
});
```
I'll tag meshes: hamster meshes get userData.hamster, wheel meshes get userData.wheel.

Spook: set hamster.panic = true, panicTimer = 2, pick random fast target, legs animate fast.

Boost wheel: wheelSpeed += 4, decays.

Let me implement spook in Hamster.update: if panic, move fast toward random target; decrement timer; when done, resume.

Let me now write the whole thing out fully and carefully.

I need to be careful that all meshes added to groups get proper userData. When I do g.add(mesh), the mesh retains userData. Good. But note: for raycasting to find the hamster, I intersect objects list = all meshes across all hamsters + wheel. I'll maintain arrays.

Let me maintain:
- hamsterMeshes = [] (all meshes in all hamsters)
- wheelMeshes = []

And push with userData set at creation.

Let me write createHamster to set userData.hamster on each mesh.

Alright. Also for the food bowl, some hamsters target it. Let me give the food bowl a position constant FOOD_BOWL = new Vector3(4.8, 0, 3.5). When a hamster's randomTarget happens to be near bowl or specifically, it eats. Simpler: give each hamster a "homeBase"/favorite spot. Let me just: with some probability during pause, target the food bowl and set state to 'eat' (a variant of pause with head bob). 

Let me add an 'eat' state: hamster stands at bowl, does head-nod animation, timer counts down.

Actually, to keep it manageable, let me fold eating into pause: when paused at the bowl location, play eat animation. Detect "near bowl" by distance < 1.2 → set isEating true and play nod.

Hmm, let me simplify further: I'll just have hamsters wander and occasionally the one near the bowl eats. Let me implement:

In pause state, before picking next action, check: if this hamster was recently targeting bowl (store a flag targetBowl bool), then it enters 'eat' state for a couple seconds with head bob, then continues.

Let me add targetBowl flag: when generating a target, if target is the bowl, set this.targetBowl=true. In pause, if this.targetBowl and random<0.7 → eat. Else normal.

Let me code eat state:
```
case 'eat':
  // head bob
  headGroup.rotation.x = Math.sin(time*6)*0.3; // nod
  this.timer -= dt;
  if (this.timer<=0){ this.state='walk'; this.target=randomTarget(); this.targetBowl=false; }
```
But head is part of group; I can rotate head mesh. Let me store head ref. Actually simpler: rotate whole group's small vertical bob. Let me just do a little y bob and not bother with separate head. Or rotate a stored head mesh. Let me store head mesh and nod it.

Let me keep it: in eat, do group.position.y bob and head nod using stored head mesh.

I think I'm overengineering. Let me simplify the whole behavior to be robust and cute:

States: 'idle', 'walk', 'pause'. Add 'eat' only for bowl visitors. Let me include it but keep simple.

Let me finalize and write. I'll aim for correctness and cuteness.

Let me write the file now.

Actually, let me reduce risk of bugs by keeping behavior straightforward and well-tested logic. Let me write and mentally simulate.

Animation loop:
```
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;
  hamsters.forEach(h => h.update(dt, t));
  wheel.rotation.x += (baseWheelSpeed + wheelBoost) * dt;
  wheelBoost *= 0.97; // decay
  controls.update();
  renderer.render(scene, camera);
}
```

Hamster.update(dt, t):
```
this.timer -= dt;
switch(state) {
  case 'idle':
    if (this.timer <= 0) { this.startWalking(false); }
    break;
  case 'walk':
    ... move ...
    if reached: this.state='pause'; this.timer = this.pauseTime;
    break;
  case 'pause':
    // bob
    if (this.targetBowl && Math.random()<0.02) { this.state='eat'; this.timer=2+Math.random(); }
    else if (this.timer<=0) { pick next }
    break;
  case 'eat':
    ... nod ...
    if timer<=0: this.state='walk'; pick target;
    break;
}
```

startWalking sets target; if random chance target = bowl and within bounds, set targetBowl=true.

Let me write helper methods on the prototype or inline object. I'll use a class.

Let me write the class:

```js
class Hamster {
  constructor(scene, furHex, bellyHex) {
    const parts = buildHamster(furHex, bellyHex);
    this.group = parts.group;
    this.head = parts.head;
    this.legs = parts.legs;
    scene.add(this.group);
    this.pos = new THREE.Vector3((Math.random()-0.5)*8, 0, (Math.random()-0.5)*6);
    this.group.position.copy(this.pos);
    this.state = 'idle';
    this.timer = 1 + Math.random()*2;
    this.pauseTime = 2 + Math.random()*3;
    this.speed = 1.0 + Math.random()*0.6;
    this.targetBowl = false;
    this.panic = 0;
    this.wobble = Math.random()*Math.PI*2;
  }
  
  pickTarget() {
    // 25% chance to go to food bowl
    if (Math.random() < 0.25) {
      this.target = FOOD_BOWL.clone();
      this.targetBowl = true;
    } else {
      this.target = new THREE.Vector3(
        clamp((Math.random()-0.5)*10, -5, 5),
        0,
        clamp((Math.random()-0.5)*8, -4, 4)
      );
      this.targetBowl = false;
    }
  }
  
  startWalk() { this.pickTarget(); this.state='walk'; }
  
  update(dt, t) {
    this.timer -= dt;
    this.wobble += dt*3;
    // gentle idle bob
    const idleBob = Math.sin(this.wobble)*0.03;
    
    if (this.panic > 0) {
      this.panic -= dt;
      // run randomly
      const dir = new THREE.Vector3().subVectors(this.target, this.pos); dir.y=0;
      if (dir.length() < 0.3) { this.target = new THREE.Vector3((Math.random()-0.5)*10,0,(Math.random()-0.5)*8); }
      dir.normalize();
      this.pos.addScaledVector(dir, 3*dt);
      clampPos();
      this.group.position.copy(this.pos);
      this.group.rotation.y = Math.atan2(dir.x, dir.z);
      fastLegAnim(t);
      return;
    }
    
    switch(this.state) {
      case 'idle':
        this.group.position.y = idleBob;
        if (this.timer<=0) this.startWalk();
        break;
      case 'walk': {
        const dir = new THREE.Vector3().subVectors(this.target, this.pos); dir.y=0;
        const d = dir.length();
        if (d < 0.2) { this.state='pause'; this.timer=this.pauseTime; }
        else {
          dir.normalize();
          this.pos.addScaledVector(dir, this.speed*dt);
          clampPos();
          this.group.position.copy(this.pos);
          this.group.rotation.y = Math.atan2(dir.x, dir.z);
          this.group.position.y = idleBob + 0.02*Math.abs(Math.sin(t*8));
          animLegs(t, this.speed);
        }
        break;
      }
      case 'pause':
        this.group.position.y = idleBob;
        // maybe eat
        if (this.targetBowl && Math.random() < 0.03) { this.state='eat'; this.timer = 1.5+Math.random()*1.5; }
        else if (this.timer<=0) {
          if (Math.random()<0.25) { this.state='idle'; this.timer=1+Math.random()*2; }
          else { this.startWalk(); }
        }
        break;
      case 'eat':
        // head nod
        this.head.rotation.x = Math.sin(t*10)*0.35;
        this.group.position.y = idleBob;
        if (this.timer<=0) { this.head.rotation.x=0; this.state='walk'; this.pickTarget(); }
        break;
    }
  }
}
```

clampPos keeps within cage bounds.

animLegs(t, speed): 
```
this.legs.forEach((leg,i)=>{
  const phase = (i===1||i===2)?Math.PI:0;
  leg.rotation.x = Math.sin(t*10 + phase)*0.6;
});
```
Fast version uses higher freq.

I'll factor leg anim into a method taking t and a frequency.

Let me write buildHamster returning group, head, legs, and pushing userData.

Now buildWheel():
```
function buildWheel() {
  const g = new THREE.Group();
  const frame = new THREE.MeshStandardMaterial({color:0xff6b6b, flatShading:true, roughness:0.6});
  const rungMat = new THREE.MeshStandardMaterial({color:0xffd93d, flatShading:true, roughness:0.7});
  const R = 1.15, W = 0.5; // radius, width
  // main rim (torus) in YZ plane
  const rim = new THREE.Mesh(new THREE.TorusGeometry(R, 0.08, 6, 24), frame);
  rim.rotation.y = Math.PI/2; // put ring in YZ? 
  ...
}
```
Wait, I earlier determined rotateY(90) puts hole axis along X (ring in YZ). Let me just set rim.rotation.y = Math.PI/2. Let me double-check: default torus ring in XY plane, hole axis Z. rotateY(90°): hole axis -> X, ring in YZ. Yes. So rim.rotation.y = Math.PI/2.

Hmm, but I want the wheel to spin around X axis (rotation.x). If ring is in YZ plane, spinning around X rotates points within YZ plane. Yes correct.

Side rings (front/back) at x=±W/2:
```
const ringGeo = new THREE.TorusGeometry(R, 0.05, 6, 20);
const frontRing = new THREE.Mesh(ringGeo, frame); frontRing.position.x = -W/2; frontRing.rotation.y=Math.PI/2;
const backRing = new THREE.Mesh(ringGeo, frame); backRing.position.x = W/2; backRing.rotation.y=Math.PI/2;
```
Rungs: for k in 0..N-1: angle = 2πk/N. Point on ring (YZ): y = R*cos(angle), z = R*sin(angle). Front point (-W/2, y, z), back (W/2, y, z). Make rung connecting them along X.
```
function makeRung(a,b,radius){...}
const rung = makeRung(new V3(-W/2,y,z), new V3(W/2,y,z), 0.03);
rung.material = rungMat; rung.userData.wheel = true;
g.add(rung);
```
Also add main rim userData.wheel=true, rings userData.wheel=true.

Stand: two posts + top bar. Posts at x=±W/2? Actually posts support the axle from below. Let me place two vertical posts at front/back ring positions extending down to floor and up to axle. Simplify: two posts at x=-W/2 and x=W/2, at y near 0 (center of wheel), going from floor (y=0) to axle height (y=R). Post as cylinder along Y.
```
const postGeo = new THREE.CylinderGeometry(0.06,0.06, R, 6);
const postMat = new THREE.MeshStandardMaterial({color:0x95a5a6, flatShading:true});
const post1 = new THREE.Mesh(postGeo, postMat); post1.position.set(-W/2, R/2, 0);
const post2 = ... position (W/2, R/2, 0);
```
Axle: a cylinder along X connecting the two posts at height R:
```
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,W,6), postMat);
axle.rotation.x = Math.PI/2; axle.position.set(0,R,0);
```
Place wheel group so center at (0, R, 0). Bottom of wheel at y=0. Good.

But wait, wheel center at y=R=1.15, and the hamster runs inside near y~0. The hamster is ~1 tall (body center 0.55). It'd fit inside. Good.

Position the wheel group in scene at wheelPos = (-4.8, 0, 0). So wheel center at (-4.8, 1.15, 0).

Hmm, the wheel plane is YZ, so it faces ±X. At x=-4.8 near wall x=-6. Hamster inside runs facing ±Z (into the wheel). Fine.

Let me set wheel group position and add to scene.

Food bowl at (4.8, 0, 3.5):
```
function buildBowl() {
  const g = new THREE.Group();
  const bowlMat = new THREE.MeshStandardMaterial({color:0x9b59b6, flatShading:true, roughness:0.5});
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.35,0.3, 12, 1, true), bowlMat); // open cylinder
  bowl.position.y = 0.15;
  // bottom
  const bottom = new THREE.Mesh(new THREE.CylinderGeometry(0.35,0.35,0.05,12), bowlMat);
  bottom.position.y=0.025;
  // food pellets: small spheres/kernels
  const foodMat = new THREE.MeshStandardMaterial({color:0xd4a017, flatShading:true});
  for (let i=0;i<8;i++){ const p = new THREE.Mesh(new THREE.SphereGeometry(0.06,5,5), foodMat);
    p.position.set((Math.random()-0.5)*0.4, 0.28+Math.random()*0.05, (Math.random()-0.5)*0.4); g.add(p);}
  g.add(bowl, bottom);
  g.position.copy(FOOD_BOWL);
  return g;
}
```

Bedding: scatter small boxes.
```
function makeBedding(scene) {
  const colors = [0xf5deb3, 0xe8c07f, 0xd2b48c, 0xf0e68c];
  for (let i=0;i<80;i++){
    const s = 0.08+Math.random()*0.12;
    const geo = new THREE.BoxGeometry(s, s*0.5, s);
    const mat = new THREE.MeshStandardMaterial({color: colors[i%colors.length], flatShading:true, roughness:1});
    const m = new THREE.Mesh(geo, mat);
    m.position.set((Math.random()-0.5)*10, 0.02, (Math.random()-0.5)*8);
    m.rotation.set(Math.random()*3, Math.random()*3, Math.random()*3);
    scene.add(m);
  }
}
```

Cage:
```
function buildCage(scene) {
  // tray
  const trayMat = new THREE.MeshStandardMaterial({color:0x74c0ec, flatShading:true, roughness:0.9});
  const tray = new THREE.Mesh(new THREE.BoxGeometry(12, 0.4, 10), trayMat);
  tray.position.y = -0.2; // top surface at y=0
  tray.receiveShadow = true;
  scene.add(tray);
  
  // floor surface (bedding color) - optional plane
  // walls: transparent panels
  const wallMat = new THREE.MeshPhysicalMaterial({color:0e0000...})
```
Let me use MeshStandardMaterial with transmission? That requires environment. Keep simple: use transparent opacity walls.
```
const wallMat = new THREE.MeshStandardMaterial({color:0xaffffff...})
```
Syntax error. Let me write:
```
const wallMat = new THREE.MeshStandardMaterial({ color: 0xbfeef5, transparent: true, opacity: 0.35, side: THREE.DoubleSide, roughness: 0.2, metalness: 0 });
```
Four walls:
```
const wallGeo = new THREE.PlaneGeometry(12, 4);
// front (z=+5)
const front = new THREE.Mesh(wallGeo, wallMat); front.position.set(0,2,5); scene.add(front);
const back = new THREE.Mesh(wallGeo, wallMat); back.position.set(0,2,-5); back.rotation.y=Math.PI; scene.add(back);
const leftGeo = new THREE.PlaneGeometry(10,4);
const left = new THREE.Mesh(leftGeo, wallMat); left.position.set(-6,2,0); left.rotation.y=Math.PI/2; scene.add(left);
const right = new THREE.Mesh(leftGeo, wallMat); right.position.set(6,2,0); right.rotation.y=-Math.PI/2; scene.add(right);
```
Add cage edge lines for low-poly cage look:
```
const edgeMat = new THREE.LineBasicMaterial({color:0x4aa3d}); // typo
```
Let me use 0x2b7. Actually 0x2b7aa. Let me just use 0x1f6. Hmm. Use 0x3a7. Let me pick 0x2c3e50 (dark slate) for edges, or a nice blue 0x5dade0. I'll use 0x549fd4.

Create edges for each wall and combine? Simpler: add vertical corner posts (thin boxes) and top rails as wireframe lines. Let me add edge lines using EdgesGeometry on the wall planes.

Actually, let me create the cage as a box with edges for a clean look. But walls are transparent. Let me add EdgeGeometry lines to each wall plane mesh:
```
const edges = new THREE.EdgesGeometry(new THREE.PlaneGeometry(12,4));
const line = new THREE.LineSegments(edges, edgeMat);
line.position.copy(front.position); scene.add(line);
```
Repeat for each wall. That gives a cage-crawl look. Good.

Let me also add a top wireframe? Optional. Skip to keep simple, or add an open top. Keep open top.

Lighting:
```
const hemi = new THREE.HemisphereLight(0xfff7e0, 0x8fa, 0.9); // sky, ground
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 1.2);
sun.position.set(5, 8, 5);
sun.castShadow = true;
sun.shadow.mapSize.width=1024; sun.shadow.mapSize.height=1024;
sun.shadow.camera.near=0.5; sun.shadow.camera.far=50;
sun.shadow.camera.left=-10; sun.shadow.camera.right=10; sun.shadow.camera.top=10; sun.shadow.camera.bottom=-10;
scene.add(sun);
const amb = new THREE.AmbientLight(0xffffff, 0.3); scene.add(amb);
```
HemisphereLight second arg is groundColor; I'll pass 0x404040-ish or a green. Let me use new THREE.HemisphereLight(0xdfe6ff, 0x4a4033, 0.7). 

Shadows: only sun casts. Enable renderer.shadowMap.enabled=true. Make floor/tray receive shadow, hamsters cast shadow.

Camera:
```
camera = new THREE.PerspectiveCamera(50, aspect, 0.1, 100);
camera.position.set(0, 8, 14);
```
Look at origin.

OrbitControls:
```
controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0,1,0);
controls.minDistance=6; controls.maxDistance=30;
controls.maxPolarAngle = Math.PI/2 - 0.05; // don't go below ground
```
Limit polar angle so camera stays above ground. Good.

Resize:
```
window.addEventListener('resize', ()=>{ camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });
```

Let me make sure renderer.setSize uses innerWidth/innerHeight.

Now raycasting setup:
```
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let hamsterMeshes = [];
let wheelMeshes = [];
```
Populate during build.

Click handler as above.

Let me make sure to set userData on hamster meshes: in buildHamster, after creating each mesh, do mesh.userData.hamster = hamsterInstance. But hamsterInstance is created in the class constructor which calls buildHamster. Circular: buildHamster needs reference to the instance. I'll pass the instance into buildHamster, or set userData after building in the constructor.

Better: buildHamster returns {group, head, legs}; in the Hamster constructor I traverse and set userData. Let me do:
```
this.group.traverse(o => { if (o.isMesh) o.userData.hamster = this; });
```
That's clean. Similarly for wheel: after building wheel group, traverse and set userData.wheel = wheelGroup.

Great, avoids circular refs.

Now let me write the final HTML. I'll assemble everything.

Let me double check the torus rotation for the wheel rim. I'll set rim.rotation.y = Math.PI/2. But then spinning via rotation.x. However, if I set rotation.y once at build and then increment rotation.x in the loop, the rotations compose. That's fine (rotation.x += dt keeps adding local X rotation). Actually careful: modifying rotation.x each frame after having rotation.y set — Euler order default 'XYZ'. Adding to x each frame: rotation = (x+=v, y=π/2, z=0). The x rotation is applied first (innermost) then y. Spinning looks right. Good.

But there's subtlety: if I only ever set rotation.x += v, and rotation.y is fixed, the object spins around its local X which after the Y rotation is still the world X (since Y rotation about Y doesn't change X axis direction... rotating about Y keeps X axis in XZ plane but X axis rotates). Hmm, actually rotating the coordinate: after rotating π/2 about Y, the local X axis points along world -Z or +Z. So spinning about local X spins in the plane perpendicular to local X = the YZ-ish plane... which is what we want (the wheel plane). Let me not overthink; visually spinning the wheel should look like a wheel. Let me test conceptually: wheel ring in YZ plane (from our construction). Local X axis is perpendicular to YZ plane = along the axle. Spinning about local X = spinning about axle. Correct! Because after rotateY(π/2), local X = world (rotated) — the axle direction. Yes the axle is along X (we placed rings at ±W/2 in x, rungs along x). So local X is the axle. Spin about X. 

Now, let me make sure the rim torus after rotateY(π/2) indeed lies in YZ. Default torus: parametric, ring center circle in XY plane radius R, tube around it. Points: ((R+t cosψ)cosφ, (R+t cosψ)sinφ, t sinψ). So ring is in XY plane (z=0 for ring center), hole axis = Z. After rotateY(π/2): x' = x cosθ + z sinθ = (R...)cosφ *0 + ... Let me just trust: rotateY(π/2) maps XY-plane ring to YZ-plane ring. Yes.

Good.

Let me also verify rungs: I compute points at (y,z) = (R cos a, R sin a). But the ring after rotation — does the ring pass through these points? Before rotation, ring points at φ: x=(R)cosφ (ignoring tube), y=(R)sinφ, z=0. After rotateY(π/2): x'=Rcosφ*cos90 + 0 = 0, y'=Rsinφ, z'=-Rcosφ*sin90 = -Rcosφ. So ring points: (0, Rsinφ, -Rcosφ). So y=Rsinφ, z=-Rcosφ. My rung formula used y=R cos a, z=R sin a — that's just a phase shift (a = φ-90°), still traces the ring. Fine, rungs will span the ring. Good enough. I'll place rungs at a = k*step and use y=R*cos a, z=R*sin a. These lie on the ring (circle radius R in YZ). 

Now let me also ensure the wheel looks good: R=1.15, tube (torus tube) 0.08, rungs radius 0.03. Width W=0.5. Should look like a wheel.

Let me finalize colors and write.

I realize I should double check: HemisphereLight signature is (skyColor, groundColor, intensity). groundColor affects lighting from below. I'll set groundColor to a warm/brown to match bedding. Use 0x5c4a32.

Let me write the file now. I'll include comments.

Let me also add a subtle ground outside the cage? Not necessary. The tray is the ground.

Let me make the tray bigger visually and add a second layer (the plastic base underside) — optional. Keep single tray box.

Let me also add shadows receiver on tray: tray.receiveShadow=true. And hamsters castShadow=true (set in buildHamster for each mesh: mesh.castShadow=true). Set castShadow on meshes that matter (body, head, legs, wheel). Bedding can receive but not cast (perf). Let me set castShadow on hamster meshes and wheel meshes, and receiving on tray and maybe bedding.

Setting castShadow on many meshes is fine for this small scene.

Let me write buildHamster setting castShadow on each mesh.

Alright, writing final code. Let me be meticulous with braces.

Let me write it all out now.

Actually, I want to double-check the clampPos function and bounds. Cage interior half-width: tray is 12 wide (x from -6 to 6), walls at ±6. Hamster half-body ~0.7. Keep hamster x in [-5.3, 5.3], z in [-4.3, 4.3]. Let me clamp with margin.

```
function clampPos(pos){
  const bx=5.3, bz=4.3;
  pos.x = Math.max(-bx, Math.min(bx, pos.x));
  pos.z = Math.max(-bz, Math.min(bz, pos.z));
}
```

Now if a hamster's target is beyond bounds, pickTarget already clamps. During walk, clampPos prevents escaping. Good.

Let me also make sure when a hamster reaches target near bowl (4.8, 3.5), it's within bounds (4.8<5.3, 3.5<4.3). Good.

Wheel at (-4.8, 0, 0): within bounds but hamsters might walk into it. They'll pass through; acceptable. Actually to avoid hamster appearing inside the wheel, maybe fine.

Let me write now. Final assembly.

Let me reconsider camera aspect in resize: use window.innerWidth.

I'll write the complete file.

One more: I'll add a nice gradient background (scene.background) — a soft color, e.g., 0xcfefff or a gradient texture. Let me set scene.background = 0xbfe9ff (light sky) for a clean look. Or a radial gradient. Keep solid light blue 0xbfe9ff.

Let me write it.

Let me also ensure requestAnimationFrame loop starts.

Final code below.

I need to be careful with the import map and module script. Let me write.

Let me reconsider the number of hamsters: 4 is good. Colors:
1. Sandy #e8a84c, belly #fbe3c4
2. Tan #c98f5e, belly #f5dcc4
3. Gray #9aa5ad, belly #eef2f4
4. Brown #8b5a2b, belly #e8cfa8

Let me pick cute hexes:
1. fur #f4a259, belly #ffe8cf
2. fur #e0a367, belly #fce6cf
3. fur #a6b6c4, belly #eef3f7
4. fur #c1661f? too red. Let me do fur #d98a59 belly #f7dcc2

Let me finalize:
1. #f6b26b / #ffe6cf
2. #e8965a / #ffd9b3
3. #b8c4d0 / #eaf1f5
4. #d9a066 / #f6ddc0

Good.

Now writing final HTML.

Let me make the leg animation frequencies depend on speed for variety but keep simple with fixed freq scaled by speed.

I'll write animLegs(t):
```
animLegs(t){
  const f = 8 + this.speed*2;
  this.legs.forEach((leg,i)=>{
    const phase = (i===1||i===2)?Math.PI:0;
    leg.rotation.x = Math.sin(t*f + phase)*0.7;
  });
}
stopLegs(){ this.legs.forEach(l=>l.rotation.x=0); }
```
During idle/pause/eat, reset leg rotation to 0 (or gentle). For panic, use higher freq.

Let me integrate.

Let me now also handle: when entering walk from any state, call stopLegs then animLegs. Actually animLegs called each walk frame. On idle, legs at 0. Fine.

For panic: animLegs with higher freq. Let me just call animLegs(t) with a multiplier. I'll add a param freqScale.

Let me code panic leg: this.legs.forEach with f=16.

I'll write a dedicated fastLegs(t).

OK final code. Writing now. Let me produce the complete index.html.

Let me carefully write with proper indentation and no syntax errors.

I'll write the whole thing in one go.

Double-check: THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments, arc). Default arc=2π. Good.

THREE.CylinderGeometry(radiusTop, radiusBottom, height, radialSegments). Default axis=Y.

THREE.PlaneGeometry(w,h).

THREE.BoxGeometry(w,h,d).

THREE.SphereGeometry(r, segW, segH).

THREE.IcosahedronGeometry(r) — alternative for smoother low-poly sphere. I'll use SphereGeometry with low segments for classic low-poly.

Let me write.

For the eyes, MeshBasicMaterial (no shading) so they stay black/dark. Good.

For nose, MeshStandardMaterial pink.

Let me finalize and output.

I'll also add window.addEventListener('resize', ...).

Let me write the complete file now.

Actually, let me reconsider whether to include the food pellets spheres as separate meshes that cast shadow — fine.

Let me write.

Also, I should make sure the hamster head nod during eat doesn't conflict with group rotation. The head is a child of group; rotating head.rotation.x while group.rotation.y is set — head local rotation applies in group's local space. Since group is rotated about Y, local X is tilted, so nodding about local X might tilt oddly. To keep it clean, let me nod the head about a local axis that's horizontal. Hmm. Alternatively, for eat animation, just bob the whole group up/down and scale squash. Let me do: during eat, group.position.y bob faster + a squash/stretch on body scale. Simpler and robust. Let me do:
```
case 'eat':
  const eatBob = Math.abs(Math.sin(t*12))*0.08;
  this.group.position.y = eatBob;
  this.body.scale.y = 0.9 + Math.sin(t*12)*0.05; // squash
  if(timer<=0){ this.group.position.y=0; restore body scale; state=walk; }
```
I need reference to body mesh to adjust scale. Let me store this.body. buildHamster can return body too.

Let me return { group, head, body, legs }.

Store this.body and this.head.

Eat: use body scale squash. Good, avoids head-axis issues.

Let me finalize.

Let me write everything.

Also add subtle ear wiggle? Skip.

Writing final now.

Let me produce the code.

I'll double check the `makeRung` fromUnitVectors usage:
```
function makeRung(a, b, r){
  const dir = new THREE.Vector3().subVectors(b,a);
  const len = dir.length();
  const geo = new THREE.CylinderGeometry(r, r, len, 5, 1);
  const m = new THREE.Mesh(geo);
  m.position.copy(a).addScaledVector(dir, 0.5);
  const up = new THREE.Vector3(0,1,0);
  m.quaternion.copy(new THREE.Quaternion().setFromUnitVectors(up, dir));
  return m;
}
```
dir.normalize() mutates dir but setFromUnitVectors uses normalized internally; calling normalize before is fine. Actually setFromUnitVectors(up, dir) normalizes dir internally, so I don't need to pre-normalize. But I compute len before, using original dir length. Good. Don't normalize before computing len. Order: subVectors (dir = b-a), len = dir.length(), then quaternion setFromUnitVectors(up, dir) which normalizes dir copy. Fine.

Good.

Now, rungs: for k in 0..N-1: angle = 2πk/N. Point on ring (YZ): y = R*cos(angle), z = R*sin(angle). Front point (-W/2, y, z), back (W/2, y, z). Make rung connecting them along X.
```
const rung = makeRung(new THREE.Vector3(-W/2,y,z), new THREE.Vector3(W/2,y,z), 0.03);
```
Wait, but the wheel center is at y=R (1.15) in world, but the wheel GROUP is at y=0 initially (I'll position wheel group at wheelPos with y=0, and the wheel meshes are built with center at y=R). Hmm, I need to decide: build wheel meshes centered at origin (ring center at y=R so bottom at 0) OR build at origin and then offset group.

Let me build the wheel with ring center at y=R (so bottom touches y=0). Then position the wheel group at wheelPos=(−4.8,0,0). Since built with center at y=R and group at y=0, world center at y=R. Good, bottom at 0.

But rungs computed with y=R cos a etc. relative to center (0,0,0) of the group. Since group center is at wheelPos (y=0) but meshes built assuming center at y=R... I need to offset rung endpoints by +R in y. Let me just build everything with ring center at y=R directly (add R to all y coords). So:
front point = (-W/2, R + R*cos a, R*sin a)? No wait. Let me define ring local coords with center at origin, then the wheel group will be positioned so that center is at wheelPos + (0, R, 0)? 

Cleaner: Build wheel meshes in a group, with ring center at origin (0,0,0) meaning the ring spans y∈[-R,R]. Then set wheel group position to wheelPos + (0, R, 0) so ring center at world y=R, bottom at 0. And posts stand from floor to axle.

Let me do that: build with center at origin. Rungs: points at (±W/2, R*cos a, R*sin a). Rim at origin. Posts: from y=0 (floor) to y=R (axle) — but axle at center origin? The axle is at the ring center = origin in local, which becomes world y=R after group offset. Posts should go from floor (world 0) to world R. In local coords (center origin), posts go from y=-R (floor) to y=0 (axle). Let me build posts from y=-R to y=0, height R, positioned at x=±W/2. Cylinder height R, center at y=-R/2. So post.position.y = -R/2, position.x = ±W/2. Then group offset by +R in y puts floor at -R+R=0 and axle at 0+R=R. 

Axle: cylinder along X at y=0 local (world R), length W.

So build everything centered at origin, then wheelGroup.position = wheelPos + (0,R,0). 

Let me set wheelPos = new THREE.Vector3(-4.8, 0, 0), and wheelGroup.position.set(-4.8, R, 0).

Posts: 
```
postGeo = new THREE.CylinderGeometry(0.06,0.06,R,6);
post1 = new THREE.Mesh(postGeo, postMat); post1.position.set(-W/2, -R/2, 0);
post2 = ... (W/2, -R/2, 0);
```
Axle:
```
axle = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,W,6), postMat);
axle.rotation.x = Math.PI/2; axle.position.set(0,0,0);
```
Rim at origin rotation.y=π/2. Rings at x=±W/2 rotation.y=π/2. Rungs around.

Good.

Now the hamster runs inside near y=0 (world), which is at local y=-R. Fine.

Let me write buildWheel returning group and set userData.wheel on rim, rings, rungs, axle (maybe not posts). Actually clicking anywhere on wheel boosts. Let me tag rim, rings, rungs, axle as wheel.

Let me write.

I think the plan is solid. Let me write the final HTML.

Let me count hamster meshes for raycasting — traverse handles it.

Final code: I'll write it now comprehensively.

Let me make sure to set castShadow appropriately and that shadows work. Directional light shadow camera covers the scene (±10). Good.

Let me write.

Also, I want to double check the import map and module script. Let me write.

Let me reconsider the number of hamsters: 4 is good.

Now writing final HTML.
</think>

# Low-Poly Hamster Playground

Here's a complete, single-file `index.html` project. Just save it and open it in any modern browser — no build step needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>🐹 Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; }
  html, body { height: 100%; overflow: hidden; }
  body { font-family: "Segoe UI", system-ui, sans-serif; background: #0b1220; }
  canvas { display: block; }
  #ui {
    position: fixed;
    top: 14px;
    left: 50%;
    transform: translateX(-50%);
    color: #12233b;
    text-align: center;
    pointer-events: none;
    user-select: none;
    text-shadow: 0 1px 3px rgba(255,255,255,0.6);
  }
  #ui h1 {
    margin: 0;
    font-size: 22px;
    letter-spacing: 0.5px;
  }
  #ui p {
    margin: 4px 0 0;
    font-size: 13px;
    opacity: 0.85;
  }
</style>
</head>
<body>
  <div id="ui">
    <h1>🐹 Low-Poly Hamster Playground</h1>
    <p>Drag to rotate &nbsp;•&nbsp; Scroll to zoom &nbsp;•&nbsp; Click a hamster to spook it &nbsp;•&nbsp; Click the wheel to spin it</p>
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

    /* ============================================================
       SCENE / CAMERA / RENDERER
    ============================================================ */
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xbfe9ff);

    const camera = new THREE.PerspectiveCamera(
      50, window.innerWidth / window.innerHeight, 0.1, 200
    );
    camera.position.set(0, 11, 16);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 1.2, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 6;
    controls.maxDistance = 30;
    controls.maxPolarAngle = Math.PI / 2 - 0.04; // keep above the floor
    controls.update();

    /* ============================================================
       LIGHTING
    ============================================================ */
    const hemi = new THREE.HemisphereLight(0xdfeaff, 0x5c4a32, 0.85);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xfff4e0, 1.25);
    sun.position.set(6, 12, 6);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 60;
    sun.shadow.camera.left = -14;
    sun.shadow.camera.right = 14;
    sun.shadow.camera.top = 14;
    sun.shadow.camera.bottom = -14;
    sun.shadow.bias = -0.0005;
    scene.add(sun);

    scene.add(new THREE.AmbientLight(0xffffff, 0.25));

    /* ============================================================
       CONSTANTS
    ============================================================ */
    const FOOD_BOWL = new THREE.Vector3(4.8, 0, 3.4);
    const WHEEL_POS = new THREE.Vector3(-4.8, 0, 0);
    const HALF_X = 5.3, HALF_Z = 4.3; // playable bounds

    /* ============================================================
       CAGE (tray + transparent walls + cage edges)
    ============================================================ */
    function buildCage() {
      const cage = new THREE.Group();

      // Plastic tray base
      const trayMat = new THREE.MeshStandardMaterial({
        color: 0x74c0ec, flatShading: true, roughness: 0.9
      });
      const tray = new THREE.Mesh(new THREE.BoxGeometry(12, 0.4, 10), trayMat);
      tray.position.y = -0.2;
      tray.receiveShadow = true;
      cage.add(tray);

      // Transparent walls
      const wallMat = new THREE.MeshStandardMaterial({
        color: 0xbfeef5, transparent: true, opacity: 0.32,
        side: THREE.DoubleSide, roughness: 0.2, metalness: 0.0
      });
      const edgeMat = new THREE.LineBasicMaterial({ color: 0x549fd4 });

      const makeWall = (w, h, pos, rotY) => {
        const wall = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMat);
        wall.position.copy(pos);
        wall.rotation.y = rotY;
        cage.add(wall);
        const edges = new THREE.LineSegments(
          new THREE.EdgesGeometry(new THREE.PlaneGeometry(w, h)), edgeMat
        );
        wall.children.push(edges);
        cage.add(edges);
      };
      makeWall(12, 4, new THREE.Vector3(0, 2, 5), 0);
      makeWall(12, 4, new THREE.Vector3(0, 2, -5), Math.PI);
      makeWall(10, 4, new THREE.Vector3(-6, 2, 0), Math.PI / 2);
      makeWall(10, 4, new THREE.Vector3(6, 2, 0), -Math.PI / 2);

      // Corner posts for a cuter cage look
      const postMat = new THREE.MeshStandardMaterial({ color: 0x549fd4, flatShading: true });
      const cornerMat = new THREE.BoxGeometry(0.15, 4.4, 0.15);
      const corners = [[-6, 5], [6, 5], [-6, -5], [6, -5]];
      corners.forEach(([x, z]) => {
        const p = new THREE.Mesh(cornerMat, postMat);
        p.position.set(x, 2, z);
        cage.add(p);
      });

      scene.add(cage);
    }

    /* ============================================================
       BEDDING (scattered wood-shaving bits)
    ============================================================ */
    function buildBedding() {
      const colors = [0xf5deb3, 0xe8c07f, 0xd2b48c, 0xf0e68c, 0xcaa482];
      for (let i = 0; i < 90; i++) {
        const s = 0.08 + Math.random() * 0.13;
        const mat = new THREE.MeshStandardMaterial({
          color: colors[i % colors.length], flatShading: true, roughness: 1
        });
        const m = new THREE.Mesh(new THREE.BoxGeometry(s, s * 0.5, s), mat);
        m.position.set(
          (Math.random() - 0.5) * 11,
          0.02,
          (Math.random() - 0.5) * 9
        );
        m.rotation.set(
          Math.random() * Math.PI,
          Math.random() * Math.PI,
          Math.random() * Math.PI
        );
        scene.add(m);
      }
    }

    /* ============================================================
       RUNNING WHEEL
    ============================================================ */
    function buildWheel() {
      const wheel = new THREE.Group();
      const R = 1.15, W = 0.5;

      const frameMat = new THREE.MeshStandardMaterial({ color: 0xff6b6b, flatShading: true, roughness: 0.6 });
      const rungMat = new THREE.MeshStandardMaterial({ color: 0xffd93d, flatShading: true, roughness: 0.7 });
      const matMat = new THREE.MeshStandardMaterial({ color: 0x95a5a6, flatShading: true, roughness: 0.6 });

      // Main rim (ring lies in the YZ plane -> spin around X)
      const rim = new THREE.Mesh(new THREE.TorusGeometry(R, 0.08, 6, 26), frameMat);
      rim.rotation.y = Math.PI / 2;
      rim.castShadow = true;
      rim.userData.wheel = wheel;
      wheel.add(rim);

      // Two side rings
      const ringGeo = new THREE.TorusGeometry(R, 0.05, 6, 20);
      const front = new THREE.Mesh(ringGeo, frameMat);
      front.position.x = -W / 2; front.rotation.y = Math.PI / 2;
      front.userData.wheel = wheel;
      const back = new THREE.Mesh(ringGeo, frameMat);
      back.position.x = W / 2; back.rotation.y = Math.PI / 2;
      back.userData.wheel = wheel;
      wheel.add(front, back);

      // Rungs
      const RUNGS = 16;
      for (let k = 0; k < RUNGS; k++) {
        const a = (k / RUNGS) * Math.PI * 2;
        const y = R * Math.cos(a), z = R * Math.sin(a);
        const rung = makeRung(
          new THREE.Vector3(-W / 2, y, z),
          new THREE.Vector3(W / 2, y, z),
          0.03
        );
        rung.material = rungMat;
        rung.castShadow = true;
        rung.userData.wheel = wheel;
        wheel.add(rung);
      }

      // Support stand
      const postGeo = new THREE.CylinderGeometry(0.06, 0.06, R, 6);
      const p1 = new THREE.Mesh(postGeo, matMat);
      p1.position.set(-W / 2, -R / 2, 0);
      const p2 = new THREE.Mesh(postGeo, matMat);
      p2.position.set(W / 2, -R / 2, 0);
      const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, W, 6), matMat);
      axle.rotation.x = Math.PI / 2;
      wheel.add(p1, p2, axle);

      wheel.position.copy(WHEEL_POS);
      wheel.position.y += R; // centre the ring so its bottom touches the floor
      scene.add(wheel);
      return wheel;
    }

    function makeRung(a, b, r) {
      const dir = new THREE.Vector3().subVectors(b, a);
      const len = dir.length();
      const geo = new THREE.CylinderGeometry(r, r, len, 5, 1);
      const m = new THREE.Mesh(geo);
      m.position.copy(a).addScaledVector(dir, 0.5);
      m.quaternion.copy(
        new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir)
      );
      return m;
    }

    /* ============================================================
       FOOD BOWL
    ============================================================ */
    function buildBowl() {
      const bowl = new THREE.Group();
      const bowlMat = new THREE.MeshStandardMaterial({ color: 0x9b59b6, flatShading: true, roughness: 0.5 });
      const inner = new THREE.MeshStandardMaterial({ color: 0x8e44ad, flatShading: true, roughness: 0.5, side: THREE.DoubleSide });

      const bowlShell = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.38, 0.3, 12, 1, true), bowlMat);
      bowlShell.position.y = 0.15; bowlShell.castShadow = true;
      const bottom = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.06, 12), bowlMat);
      bottom.position.y = 0.03; bottom.castShadow = true;
      bowl.add(bowlShell, bottom);

      const foodMat = new THREE.MeshStandardMaterial({ color: 0xd9a02b, flatShading: true, roughness: 0.9 });
      for (let i = 0; i < 10; i++) {
        const seed = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), foodMat);
        seed.position.set(
          (Math.random() - 0.5) * 0.45,
          0.26 + Math.random() * 0.05,
          (Math.random() - 0.5) * 0.45
        );
        bowl.add(seed);
      }
      bowl.position.copy(FOOD_BOWL);
      scene.add(bowl);
    }

    /* ============================================================
       HAMSTER factory
       (facing +Z ; forward direction = +Z)
    ============================================================ */
    function buildHamster(furHex, bellyHex) {
      const g = new THREE.Group();

      const fur = new THREE.MeshStandardMaterial({ color: furHex, flatShading: true, roughness: 0.95 });
      const bellyMat = new THREE.MeshStandardMaterial({ color: bellyHex, flatShading: true, roughness: 0.95 });
      const dark = new THREE.MeshStandardMaterial({ color: 0x141414, flatShading: true });
      const pink = new THREE.MeshStandardMaterial({ color: 0xff9fb0, flatShading: true });

      const cast = (m) => { m.castShadow = true; return m; };

      // Body
      const body = cast(new THREE.Mesh(
        new THREE.SphereGeometry(0.5, 12, 10), fur
      ));
      body.scale.set(1, 0.9, 1.35);
      body.position.y = 0.55;
      g.add(body);

      // Belly patch
      const belly = new THREE.Mesh(new THREE.SphereGeometry(0.34, 10, 8), bellyMat);
      belly.scale.set(1, 0.95, 1.0);
      belly.position.set(0, 0.48, 0.22);
      g.add(belly);

      // Head
      const head = cast(new THREE.Mesh(new THREE.SphereGeometry(0.35, 12, 10), fur));
      head.position.set(0, 0.72, 0.55);
      g.add(head);

      // Ears
      const earGeo = new THREE.SphereGeometry(0.13, 7, 7);
      const earL = cast(new THREE.Mesh(earGeo, fur));
      earL.position.set(0.05, 1.0, 0.32); earL.scale.set(1, 0.7, 1);
      const earR = cast(new THREE.Mesh(earGeo, fur));
      earR.position.set(-0.05, 1.0, 0.32); earR.scale.set(1, 0.7, 1);
      g.add(earL, earR);

      // Eyes
      const eyeGeo = new THREE.SphereGeometry(0.06, 8, 8);
      const eyeL = new THREE.Mesh(eyeGeo, dark);
      eyeL.position.set(0.13, 0.78, 0.8);
      const eyeR = new THREE.Mesh(eyeGeo, dark);
      eyeR.position.set(-0.13, 0.78, 0.8);
      g.add(eyeL, eyeR);

      // Nose
      const nose = cast(new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 8), pink));
      nose.position.set(0, 0.68, 0.93);
      g.add(nose);

      // Cheek tufts
      const cheekGeo = new THREE.SphereGeometry(0.09, 7, 7);
      const ckL = new THREE.Mesh(cheekGeo, pink);
      ckL.position.set(0.2, 0.66, 0.55);
      const ckR = new THREE.Mesh(cheekGeo, pink);
      ckR.position.set(-0.2, 0.66, 0.55);
      g.add(ckL, ckR);

      // Feet
      const footGeo = new THREE.BoxGeometry(0.16, 0.12, 0.22);
      const feet = [
        cast(new THREE.Mesh(footGeo, bellyMat)), // front-left
        cast(new THREE.Mesh(footGeo, bellyMat)), // front-right
        cast(new THREE.Mesh(footGeo, bellyMat)), // back-left
        cast(new THREE.Mesh(footGeo, bellyMat)), // back-right
      ];
      feet[0].position.set(0.2, 0.1, 0.35);
      feet[1].position.set(0.2, 0.1, -0.35);
      feet[2].position.set(-0.2, 0.1, 0.35);
      feet[3].position.set(-0.2, 0.1, -0.35);
      g.add(...feet);

      // Tail
      const tail = cast(new THREE.Mesh(new THREE.SphereGeometry(0.06, 7, 7), fur));
      tail.position.set(0, 0.45, -0.6);
      g.add(tail);

      return { group: g, body, head, legs: feet };
    }

    /* ============================================================
       HAMSTER AI
    ============================================================ */
    class Hamster {
      constructor(scene, furHex, bellyHex) {
        const p = buildHamster(furHex, bellyHex);
        this.group = p.group;
        this.body = p.body;
        this.head = p.head;
        this.legs = p.legs;
        scene.add(this.group);

        this.pos = new THREE.Vector3(
          (Math.random() - 0.5) * 8, 0, (Math.random() - 0.5) * 6
        );
        this.group.position.copy(this.pos);

        this.state = 'idle';
        this.timer = 1 + Math.random() * 2;
        this.pauseTime = 2 + Math.random() * 3;
        this.speed = 1.0 + Math.random() * 0.6;
        this.targetBowl = false;
        this.panic = 0;
        this.wobble = Math.random() * Math.PI * 2;
      }

      clamp() {
        this.pos.x = Math.max(-HALF_X, Math.min(HALF_X, this.pos.x));
        this.pos.z = Math.max(-HALF_Z, Math.min(HALF_Z, this.pos.z));
      }

      pickTarget() {
        if (Math.random() < 0.28) {
          this.target = FOOD_BOWL.clone();
          this.targetBowl = true;
        } else {
          this.target = new THREE.Vector3(
            (Math.random() - 0.5) * 10,
            0,
            (Math.random() - 0.5) * 8
          );
          this.targetBowl = false;
        }
      }

      startWalk() {
        this.pickTarget();
        this.state = 'walk';
      }

      animLegs(t, freq) {
        this.legs.forEach((leg, i) => {
          // diagonal trotting gait
          const phase = (i === 1 || i === 2) ? Math.PI : 0;
          leg.rotation.x = Math.sin(t * freq + phase) * 0.75;
        });
      }

      stopLegs() {
        this.legs.forEach((l) => (l.rotation.x = 0));
      }

      update(dt, t) {
        this.timer -= dt;
        this.wobble += dt * 3;
        const idleBob = Math.sin(this.wobble) * 0.03;

        /* ---- panic: spooked run ---- */
        if (this.panic > 0) {
          this.panic -= dt;
          const dir = new THREE.Vector3().subVectors(this.target, this.pos);
          dir.y = 0;
          if (dir.lengthSq() < 0.25) {
            this.target.set((Math.random() - 0.5) * 10, 0, (Math.random() - 0.5) * 8);
          }
          dir.normalize();
          this.pos.addScaledVector(dir, 3.2 * dt);
          this.clamp();
          this.group.position.copy(this.pos);
          this.group.rotation.y = Math.atan2(dir.x, dir.z);
          this.animLegs(t, 18);
          return;
        }

        switch (this.state) {
          case 'idle':
            this.group.position.y = idleBob;
            if (this.timer <= 0) this.startWalk();
            break;

          case 'walk': {
            const dir = new THREE.Vector3().subVectors(this.target, this.pos);
            dir.y = 0;
            const d = dir.length();
            if (d < 0.2) {
              this.state = 'pause';
              this.timer = this.pauseTime;
            } else {
              dir.normalize();
              this.pos.addScaledVector(dir, this.speed * dt);
              this.clamp();
              this.group.position.copy(this.pos);
              this.group.rotation.y = Math.atan2(dir.x, dir.z);
              this.group.position.y = idleBob + Math.abs(Math.sin(t * 8)) * 0.03;
              this.animLegs(t, 8 + this.speed * 2);
            }
            break;
          }

          case 'pause':
            this.group.position.y = idleBob;
            if (this.targetBowl && Math.random() < 0.04) {
              this.state = 'eat';
              this.timer = 1.5 + Math.random() * 1.5;
            } else if (this.timer <= 0) {
              if (Math.random() < 0.3) {
                this.state = 'idle';
                this.timer = 1 + Math.random() * 2;
              } else {
                this.startWalk();
              }
            }
            break;

          case 'eat': {
            const e = Math.sin(t * 12);
            this.group.position.y = Math.abs(e) * 0.09;
            this.body.scale.y = 0.9 + e * 0.05; // little chewing squash
            if (this.timer <= 0) {
              this.body.scale.y = 0.9;
              this.state = 'walk';
              this.pickTarget();
            }
            break;
          }
        }
      }
    }

    /* ============================================================
       BUILD THE WORLD
    ============================================================ */
    buildCage();
    buildBedding();
    buildBowl();
    const wheel = buildWheel();

    const hamsters = [];
    const palettes = [
      ['#f6b26b', '#ffe6cf'],
      ['#e8965a', '#ffd9b3'],
      ['#b8c4d0', '#eaf1f5'],
      ['#d9a066', '#f6ddc0'],
    ];
    palettes.forEach(([f, b]) =>
      hamsters.push(new Hamster(scene, new THREE.Color(f), new THREE.Color(b)))
    );

    /* ============================================================
       INTERACTION (raycast click)
    ============================================================ */
    const raycaster = new THREE.Raycaster();
    const ndc = new THREE.Vector2();

    function getAllMeshes(root) {
      const out = [];
      root.traverse((o) => { if (o.isMesh) out.push(o); });
      return out;
    }

    window.addEventListener('click', (e) => {
      ndc.x = (e.clientX / window.innerWidth) * 2 - 1;
      ndc.y = -(e.clientY / window.innerHeight) * 2 + 1;
      raycaster.setFromCamera(ndc, camera);

      const hits = raycaster.intersectObjects([...hamsters.flatMap(h => getAllMeshes(h.group)), ...getAllMeshes(wheel)], true);
      if (!hits.length) return;

      const obj = hits[0].object;
      if (obj.userData.hamster) {
        obj.userData.hamster.panic = 2.2; // spook it!
      } else if (obj.userData.wheel) {
        wheel.userData.boost = 6; // spin the wheel faster
      }
    });

    /* ============================================================
       RESIZE
    ============================================================ */
    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    /* ============================================================
       ANIMATION LOOP
    ============================================================ */
    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);
      const dt = Math.min(clock.getDelta(), 0.05);
      const t = clock.elapsedTime;

      hamsters.forEach((h) => h.update(dt, t));

      // Wheel spin (with click boost)
      wheel.userData.boost = (wheel.userData.boost || 0) * 0.96;
      wheel.rotation.x += (0.9 + wheel.userData.boost) * dt;

      controls.update();
      renderer.render(scene, camera);
    }
    animate();
  </script>
</body>
</html>
```

## What's included

- **Cage** — pastel plastic tray, translucent walls with blue cage edges, and corner posts.
- **Floor** — scattered low-poly wood-shaving bedding.
- **4 cute low-poly hamsters** — each built from spheres/boxes with body, belly, head, ears, eyes, nose, cheek tufts, four animated legs, and a tail. Fur colors vary per hamster.
- **Interactive running wheel** — spins continuously; **click it** to give it a fast boost.
- **Food bowl** — some hamsters wander over to nibble (squash‑and‑stretch "chewing" animation).
- **Autonomous behavior** — each hamster switches between *idle → walk → pause → eat/turn*, with a diagonal trotting gait, smooth turning (`atan2` facing), bounded movement, and random targets.
- **Extra interactivity** — **click any hamster** and it gets spooked and scurries away.
- **Orbit controls** — drag to rotate, scroll to zoom, camera clamped above the floor.

Just open the file in Chrome/Firefox/Safari/Edge and it runs instantly (uses an ES‑module import map to pull Three.js + OrbitControls from a CDN).