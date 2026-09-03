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

- Use Three.js from CDN
- Use OrbitControls for camera rotation
- Build low-poly hamsters using basic geometries (spheres, boxes, etc.)
- Create a cage with walls
- Add a floor tray
- Add a exercise wheel (interactive)
- Give hamsters simple AI behaviors

Let me write this out carefully.

For the hamsters, I'll use:
- Body: sphere (slightly flattened)
- Head: sphere
- Ears: small spheres
- Eyes: small dark spheres
- Cheeks: small pink spheres
- Nose: small pink sphere
- Feet: small cylinders/spheres
- Tail: tiny sphere

For behaviors:
- Walking around randomly
- Pausing occasionally
- Turning around
- Interacting with the wheel (one hamster might spin the wheel)

Let me make this cute and colorful. I'll give each hamster a different color.

Let me write the complete code.

I'll structure the hamster creation as a function that creates a group of meshes representing a hamster.

For autonomous behavior, I'll implement a simple state machine:
- WALKING: move in a direction
- PAUSING: stand still
- TURNING: rotate
- INTERACTING: interact with the object (e.g., wheel)

I'll use a timer-based system where hamsters randomly switch states.

Let me think about the cage:
- A tray at the bottom (a shallow box)
- Walls made of transparent material or wireframe so you can see through
- Actually, for visibility, I'll make the walls semi-transparent or just have bars

Let me make a nice scene. I'll add:
- Wood-chip bedding on the floor
- An exercise wheel
- A food bowl
- Maybe a tunnel (tube)

Let me write the code now.

For Three.js, I'll use the CDN version. Let me use a recent version like r128 or use the module version. Actually, for simplicity and reliability, let me use the UMD build from cdnjs or unpkg.

Let me use:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
```

And OrbitControls... For r128, OrbitControls is in the examples. Let me use a version where I can easily get OrbitControls.

Actually, let me use the newer approach with import maps or just use a version that has everything. Let me use r128 with the scripts.

For r128, I need:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
```

Hmm, but jsdelivr might have issues. Let me use the unpkg or a reliable source.

Actually, let me use the ES module approach with import maps which is cleaner:

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

This is cleaner. Let me use this approach.

Let me now write the full code.

I'll create:
1. Scene, camera, renderer
2. Lights
3. Cage (tray + walls/bars)
4. Bedding (wood chips)
5. Exercise wheel (interactive)
6. Food bowl
7. Tunnel
8. Multiple hamsters with AI
9. Animation loop with behaviors
10. OrbitControls

Let me write the hamster function carefully.

```javascript
function createHamster(color) {
  const hamster = new THREE.Group();
  
  const furMaterial = new THREE.MeshStandardMaterial({ 
    color: color, 
    roughness: 0.9, 
    flatShading: true 
  });
  
  // Body
  const body = new THREE.Mesh(
    new THREE.SphereGeometry(0.5, 12, 10),
    furMaterial
  );
  body.scale.set(1, 0.9, 1.2);
  body.position.y = 0.5;
  hamster.add(body);
  
  // Head
  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.35, 12, 10),
    furMaterial
  );
  head.position.set(0, 0.6, 0.5);
  hamster.add(head);
  
  // Ears
  const earGeometry = new THREE.SphereGeometry(0.12, 8, 8);
  const leftEar = new THREE.Mesh(earGeometry, furMaterial);
  leftEar.position.set(-0.2, 0.9, 0.5);
  hamster.add(leftEar);
  const rightEar = new THREE.Mesh(earGeometry, furMaterial);
  rightEar.position.set(0.2, 0.9, 0.5);
  hamster.add(rightEar);
  
  // Eyes
  const eyeMaterial = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.3 });
  const eyeGeometry = new THREE.SphereGeometry(0.06, 8, 8);
  const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
  leftEye.position.set(-0.15, 0.65, 0.8);
  hamster.add(leftEye);
  const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
  rightEye.position.set(0.15, 0.65, 0.8);
  hamster.add(rightEye);
  
  // Cheeks
  const cheekMaterial = new THREE.MeshStandardMaterial({ color: 0xffb6c1, roughness: 0.9 });
  const cheekGeometry = new THREE.SphereGeometry(0.1, 8, 8);
  const leftCheek = new THREE.Mesh(cheekGeometry, cheekMaterial);
  leftCheek.position.set(-0.25, 0.55, 0.65);
  hamster.add(leftCheek);
  const rightCheek = new THREE.Mesh(cheekGeometry, cheekMaterial);
  rightCheek.position.set(0.25, 0.55, 0.65);
  hamster.add(rightCheek);
  
  // Nose
  const nose = new THREE.Mesh(cheekGeometry, cheekMaterial);
  nose.position.set(0, 0.58, 0.85);
  hamster.add(nose);
  
  // Feet
  const footGeometry = new THREE.SphereGeometry(0.1, 8, 8);
  const footMaterial = new THREE.MeshStandardMaterial({ color: 0xffc0cb, roughness: 0.9 });
  // ... 4 feet
  
  // Tail
  const tail = new THREE.Mesh(cheekGeometry, cheekMaterial);
  tail.position.set(0, 0.45, -0.6);
  hamster.add(tail);
  
  return hamster;
}
```

Now for the behaviors. Let me create a state machine.

Each hamster will have:
- state: 'WALK', 'PAUSE', 'TURN', 'INTERACT'
- target position or direction
- timer

Let me implement a simple wander behavior:
- Hamsters walk in random directions within the cage bounds
- Occasionally pause
- Turn around
- One hamster interacts with the wheel

Let me write the update logic:

```javascript
function updateHamster(hamster, delta) {
  const data = hamster.userData;
  data.timer -= delta;
  
  switch(data.state) {
    case 'WALK':
      // Move in current direction
      hamster.position.addScaledVector(data.direction, data.speed * delta);
      // Face direction
      hamster.lookAt(hamster.position.clone().add(data.direction));
      // Bounce animation
      hamster.position.y = 0.15 + Math.abs(Math.sin(data.wobble)) * 0.05;
      data.wobble += delta * 10;
      // Check bounds
      if (bounds check failed) {
        data.direction.negate();
        data.state = 'TURN';
        data.timer = 0.5;
      }
      // Random pause
      if (data.timer <= 0) {
        if (Math.random() < 0.3) {
          data.state = 'PAUSE';
          data.timer = 1 + Math.random() * 2;
        } else {
          // New random direction
          data.direction = new THREE.Vector3(Math.random()-0.5, 0, Math.random()-0.5).normalize();
          data.timer = 1 + Math.random() * 3;
        }
      }
      break;
    case 'PAUSE':
      // Idle animation (maybe eating)
      if (data.timer <= 0) {
        data.state = 'WALK';
        data.direction = new THREE.Vector3(Math.random()-0.5, 0, Math.random()-0.5).normalize();
        data.timer = 1 + Math.random() * 3;
      }
      break;
    case 'TURN':
      hamster.rotation.y += delta * 3;
      if (data.timer <= 0) {
        data.state = 'WALK';
        data.timer = 1 + Math.random() * 3;
      }
      break;
  }
}
```

For the interactive wheel, I'll have one hamster that walks to the wheel and "rides" it, causing the wheel to spin.

Let me refine this. I'll make the wheel spin based on whether a hamster is using it.

Let me also add some fun details:
- The wheel spins when a hamster uses it
- Hamsters have slight bobbing when walking
- Maybe the food bowl gets "emptied" visually (small detail)

Let me keep it manageable but fun.

Let me write the whole thing now.

For the cage, I'll make:
- A base tray (open top box)
- Clear/acrylic walls or metal bars on top
- I'll go with semi-transparent walls for visibility

Actually, let me do a tray with low solid sides and then vertical bars above for a classic cage look. Or just make transparent walls. Transparent walls are cleaner and more visible.

Let me do:
- Wooden-looking tray (base)
- Transparent acrylic walls (slightly transparent blue/green)
- Metal bar top frame

Bedding: scattered small boxes/cylinders in tan color on the floor.

Wheel: 
- Two rings (torus) for the sides
- Horizontal bars connecting them (or a cylinder with holes)
- A central axle
- Spokes

Food bowl: a small cone/disk shape with some pellets.

Tunnel: a corrugated tube (cylinder) that hamsters can go through.

Let me write it all.

For the wheel interaction, let me make it so one designated hamster periodically goes to the wheel and rides it. While riding, the wheel spins faster.

Let me code the wheel:

```javascript
function createWheel() {
  const wheel = new THREE.Group();
  const ringMaterial = new THREE.MeshStandardMaterial({ color: 0xff6b6b, roughness: 0.6, metalness: 0.2 });
  
  // Two side rings
  const ringGeo = new THREE.TorusGeometry(0.8, 0.06, 8, 24);
  const leftRing = new THREE.Mesh(ringGeo, ringMaterial);
  leftRing.position.x = -0.3;
  wheel.add(leftRing);
  const rightRing = new THREE.Mesh(ringGeo, ringMaterial);
  rightRing.position.x = 0.3;
  wheel.add(rightRing);
  
  // Rungs (horizontal bars)
  const rungMaterial = new THREE.MeshStandardMaterial({ color: 0xffd93d, roughness: 0.6 });
  const rungGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.6, 6);
  for (let i = 0; i < 12; i++) {
    const angle = (i / 12) * Math.PI * 2;
    const rung = new THREE.Mesh(rungGeo, rungMaterial);
    rung.position.set(0, Math.cos(angle) * 0.8, Math.sin(angle) * 0.8);
    rung.rotation.z = angle;
    // orient rung horizontally
    rung.rotation.x = Math.PI/2;
    wheel.add(rung);
  }
  
  // Axle/support
  const supportMaterial = new THREE.MeshStandardMaterial({ color: 0x999999, metalness: 0.5, roughness: 0.4 });
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.2, 8), supportMaterial);
  axle.position.y = -0.6;
  wheel.add(axle);
  
  wheel.userData = { spinning: false, spinSpeed: 0 };
  return wheel;
}
```

Hmm, positioning the rungs correctly is tricky. Let me simplify the wheel rungs.

Actually, let me place rungs along the circumference. Each rung is a short cylinder oriented radially... no, rungs should be tangential (going across the width of the wheel, which is the X axis here).

Let me reconsider. The wheel rotates around the X axis. The rungs connect the two side rings. So rungs are parallel to X axis. Each rung is at a position on the circle in the YZ plane.

```javascript
for (let i = 0; i < 16; i++) {
  const angle = (i / 16) * Math.PI * 2;
  const rung = new THREE.Mesh(ringGeo-ish, rungMaterial);
  // rung is along X, length 0.6
  const rungGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.6, 6);
  const rung = new THREE.Mesh(rungGeo, rungMaterial);
  rung.rotation.z = Math.PI/2; // align along X
  const radius = 0.8;
  rung.position.set(0, Math.cos(angle) * radius, Math.sin(angle) * radius);
  wheel.add(rung);
}
```

That's better. The rung cylinder default is along Y, so rotating z by PI/2 makes it along X. Good.

Now the hamster riding: when a hamster is on the wheel, place it near the bottom of the wheel facing the direction of travel, and increment wheel.spinSpeed.

Let me handle this in the update loop.

OK let me just write everything out now. I'll be careful with the code.

Let me define the cage bounds. The tray is, say, 6 x 6 units, walls up to height 2. Hamsters move on the floor (y from 0 to ~0.3).

Bounds: x from -2.7 to 2.7, z from -2.7 to 2.7 (keeping inside the tray).

Let me place objects:
- Wheel at (2, 0, -2)
- Food bowl at (-2.5, 0, 2)
- Tunnel from (-2, 0, -2) to (0, 0, -2) maybe

Let me finalize positions.

Cage center at origin. Tray from -3 to 3 in x and z.

Wheel: at (2.2, 0, -2.2)
Food bowl: at (-2.2, 0, 2.2)
Tunnel: a horizontal tube around (-2.2, 0.3, -2.2), oriented along X, length ~2

Let me write the tunnel:
```javascript
function createTunnel() {
  const tunnel = new THREE.Group();
  const tubeMaterial = new THREE.MeshStandardMaterial({ color: 0x4ecdc4, roughness: 0.8, side: THREE.DoubleSide });
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 2.5, 12, 1, true), tubeMaterial);
  tube.rotation.z = Math.PI/2; // along X
  tunnel.add(tube);
  // ends
  const endMaterial = new THREE.MeshStandardMaterial({ color: 0x45b7d1, roughness: 0.8 });
  const endGeo = new THREE.TorusGeometry(0.5, 0.08, 8, 12);
  const leftEnd = new THREE.Mesh(endGeo, endMaterial);
  leftEnd.position.x = -1.25;
  leftEnd.rotation.y = Math.PI/2;
  tunnel.add(leftEnd);
  const rightEnd = new THREE.Mesh(endGeo, endMaterial);
  rightEnd.position.x = 1.25;
  rightEnd.rotation.y = Math.PI/2;
  tunnel.add(rightEnd);
  return tunnel;
}
```

Food bowl:
```javascript
function createFoodBowl() {
  const bowl = new THREE.Group();
  const bowlMaterial = new THREE.MeshStandardMaterial({ color: 0xffe66d, roughness: 0.5 });
  // Bowl: use a lathe or a truncated cone
  const bowlShape = new THREE.LatheGeometry([
    new THREE.Vector2(0, 0),
    new THREE.Vector2(0.35, 0),
    new THREE.Vector2(0.4, 0.25),
    new THREE.Vector2(0.42, 0.3),
  ], 16);
  const bowlMesh = new THREE.Mesh(bowlShape, bowlMaterial);
  bowl.add(bowlMesh);
  // Pellets
  const pelletMaterial = new THREE.MeshStandardMaterial({ color: 0xa0522d, roughness: 0.9 });
  const pelletGeo = new THREE.SphereGeometry(0.06, 6, 6);
  for (let i = 0; i < 12; i++) {
    const pellet = new THREE.Mesh(pelletGeo, pelletMaterial);
    const a = Math.random() * Math.PI * 2;
    const r = Math.random() * 0.25;
    pellet.position.set(Math.cos(a)*r, 0.22 + Math.random()*0.05, Math.sin(a)*r);
    bowl.add(pellet);
  }
  return bowl;
}
```

Now bedding:
```javascript
function createBedding() {
  const bedding = new THREE.Group();
  const chipMaterial = new THREE.MeshStandardMaterial({ color: 0xd9a06b, roughness: 1.0, flatShading: true });
  const chipGeo = new THREE.BoxGeometry(0.15, 0.05, 0.3);
  for (let i = 0; i < 300; i++) {
    const chip = new THREE.Mesh(chipGeo, chipMaterial);
    chip.position.set((Math.random()-0.5)*5.6, 0.03, (Math.random()-0.5)*5.6);
    chip.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
    bedding.add(chip);
  }
  return bedding;
}
```

Cage walls:
```javascript
function createCage() {
  const cage = new THREE.Group();
  
  // Tray (base)
  const trayMaterial = new THREE.MeshStandardMaterial({ color: 0x95d5b2, roughness: 0.8 });
  const trayBottom = new THREE.Mesh(new THREE.BoxGeometry(6.4, 0.3, 6.4), trayMaterial);
  trayBottom.position.y = 0.15;
  cage.add(trayBottom);
  
  // Tray walls (low solid sides)
  const wallHeight = 0.6;
  const wallThick = 0.2;
  // ... 4 walls
  
  // Transparent upper walls
  const wallMaterial = new THREE.MeshPhysicalMaterial({ 
    color: 0xbce6ff, 
    transparent: true, 
    opacity: 0.15, 
    roughness: 0.1,
    metalness: 0
  });
  // ... 4 transparent walls above
  
  // Bar frame
  // ...
  
  return cage;
}
```

This is getting complex. Let me simplify the cage to just a tray with transparent walls and a bar top frame.

Actually, let me make the tray with solid low walls and transparent walls above, plus vertical bars at corners and edges for a cage feel.

Let me simplify: I'll make a base tray (solid), and transparent walls going up. That's enough for visibility and looks clean.

Let me write the full code now and be done.

Let me reconsider the overall structure to make sure it works.

I'll write:
1. HTML skeleton with import map
2. CSS for full-screen canvas and a small UI overlay
3. JS module with all the logic

Let me make sure the hamster riding the wheel works. I'll designate hamster index 0 as the "rider" that occasionally goes to the wheel.

Actually, to make it more organic, let me have hamsters generally wander, and one specific hamster (say the first one) has a special behavior where it periodically goes to ride the wheel.

Let me define the rider behavior:
- State 'GO_WHEEL': move toward wheel position
- State 'RIDE': position on/near wheel, wheel spins
- After some time, leave wheel

Let me implement.

For the wheel spin, I'll rotate the wheel mesh around X axis based on spinSpeed. When a hamster rides, spinSpeed increases; otherwise it decays.

```javascript
// In update
wheel.rotation.x += wheel.userData.spinSpeed * delta;
wheel.userData.spinSpeed *= 0.98; // decay
```

When rider is active:
```javascript
wheel.userData.spinSpeed = 5; // constant while riding
```

Let me place the rider hamster on the wheel. The wheel center is at wheel.position. The rider should be at the bottom of the wheel, slightly in front, facing sideways (so it looks like running).

Wheel is at (2.2, 0, -2.2), radius 0.8, so bottom of wheel is at y = 0.8 (radius) ... wait, the wheel sits on the floor. Let me position the wheel so its bottom touches the floor. Wheel center y = 0.8 (radius), so it spans from y=0 to y=1.6. Actually the axle extends below. Let me just set wheel.position.y = 0.8 so the ring bottom is at y=0.

Hmm, but the axle/support goes down to y=-0.6 relative, so absolute -0.2, which is below floor. Let me adjust: put wheel center at y = 0.85 so bottom ring at 0.05 (just above floor). Support from center down.

For the rider, place hamster at wheel bottom: position (2.2, 0.2, -2.2 + something) facing Z. Actually the hamster runs inside the wheel near the bottom. Let me place it at the bottom center of the wheel, facing the +X or -X direction (perpendicular to wheel axis), like it's running.

Hmm, actually hamsters run in the wheel facing one direction. The wheel axis is X, so the hamster runs along... no. When a hamster runs in a wheel, it runs along the axis of the wheel (the axle direction). So the hamster faces along X (parallel to axle) and its body is perpendicular to the wheel plane.

Wait, let me think. A hamster wheel: the axle is horizontal. The wheel plane is vertical. The hamster runs on the inner surface near the bottom, running in the direction parallel to the axle. So the hamster faces along the axle direction (X in my setup) and walks forward, causing the wheel to rotate around the X axis. Yes.

So rider hamster at bottom of wheel, facing +X or -X. Position: (2.2 ± 0.1, 0.2, -2.2). Let me face -X so it runs "backward" relative to wheel top motion... doesn't matter much. Let me face +X.

Actually, for the hamster to appear inside the wheel at the bottom, position it at the bottom of the ring: y = 0.05 (bottom of ring), and within the wheel width (x between -0.3 and 0.3 relative to center, so x ≈ 2.2). And z = -2.2 (center of wheel in z). So rider at (2.2, 0.15, -2.2) facing +X.

Let me set it up.

Let me finalize and write the code. I'll keep behaviors simple but effective.

Let me also add subtle idle animations: when paused, hamster might tilt head or the cheeks pulse. I'll add a gentle bob.

Let me write everything now.

One more thing: I want the scene to be lit nicely. I'll use:
- Ambient light (soft)
- Directional light (sun-like, with shadow)
- Maybe a hemisphere light for soft fill

Let me add shadows for depth but keep performance reasonable.

Let me write the final code.

For OrbitControls, I need to import it. With import maps:
```javascript
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
```

Good.

Let me also handle window resize.

Let me write the complete index.html now.

I'll make the hamsters different colors: orange/tan, white/cream, brown, pink, and a mix. Classic hamster colors.

Colors:
- 0xf4a460 (sandy brown)
- 0xf5deb3 (wheat/cream)
- 0x8b5a2b (brown)
- 0xffb6c1 (light pink)
- 0xdcdcdc-ish gray? No, let me keep warm tones.

Let me do 4-5 hamsters.

Let me write it.

For the wobble/bob during walking, I'll animate the whole hamster group's y position and maybe rotate slightly.

Let me also make the hamster's head turn toward movement direction using lookAt, but since we set rotation via lookAt on a horizontal plane, I need to be careful. lookAt sets the mesh to face a point. For a hamster standing on ground, I want it to rotate around Y to face the direction. I can set rotation.y directly:

```javascript
const angle = Math.atan2(direction.x, direction.z);
hamster.rotation.y = angle;
```

That's cleaner than lookAt. Let me use that.

Now let me write the complete file.

Let me think about the hamster scale. Body sphere radius 0.5, scaled. Overall hamster ~1 unit tall-ish. On a 6-unit tray with hamsters, that's fine.

Let me write the code.

Actually, let me reduce complexity in hamster creation but keep it cute. I'll make a helper for appendSphere.

Let me write:

```javascript
function addPart(parent, geo, mat, pos, scale) {
  const m = new THREE.Mesh(geo, mat);
  m.position.copy(pos);
  if (scale) m.scale.copy(scale);
  parent.add(m);
  return m;
}
```

Now writing createHamster:

```javascript
const hamsterColors = [0xf4a460, 0xf5deb3, 0x8b5a2b, 0xffb6c1, 0xe6c200];

function createHamster(color) {
  const s = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color, roughness: 0.95, flatShading: true });
  const dark = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.4, flatShading: true });
  const pink = new THREE.MeshStandardMaterial({ color: 0xff9aa2, roughness: 0.9, flatShading: true });
  
  // Body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 10, 8), fur);
  body.scale.set(1, 0.95, 1.15);
  body.position.y = 0.45;
  s.add(body);
  
  // Head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.32, 10, 8), fur);
  head.position.set(0, 0.6, 0.42);
  s.add(head);
  
  // Cheek puff
  const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.2, 8, 6), fur);
  cheek.position.set(0, 0.5, 0.55);
  cheek.scale.set(1, 0.9, 0.8);
  s.add(cheek);
  
  // Ears
  const earGeo = new THREE.SphereGeometry(0.11, 8, 6);
  const earL = new THREE.Mesh(earGeo, fur); earL.position.set(-0.2, 0.85, 0.4); s.add(earL);
  const earR = new THREE.Mesh(earGeo, fur); earR.position.set(0.2, 0.85, 0.4); s.add(earR);
  
  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.055, 8, 6);
  const eyeL = new THREE.Mesh(eyeGeo, dark); eyeL.position.set(-0.13, 0.64, 0.68); s.add(eyeL);
  const eyeR = new THREE.Mesh(eyeGeo, dark); eyeR.position.set(0.13, 0.64, 0.68); s.add(eyeR);
  
  // Nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.045, 6, 6), pink);
  nose.position.set(0, 0.58, 0.78); s.add(nose);
  
  // Feet
  const footGeo = new THREE.SphereGeometry(0.08, 6, 6);
  const feet = [];
  const footPositions = [[-0.25, 0.12, 0.3], [0.25, 0.12, 0.3], [-0.28, 0.12, -0.25], [0.28, 0.12, -0.25]];
  footPositions.forEach(p => {
    const f = new THREE.Mesh(footGeo, pink);
    f.position.set(...p);
    s.add(f);
    feet.push(f);
  });
  
  // Tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.07, 6, 6), pink);
  tail.position.set(0, 0.4, -0.55); s.add(tail);
  
  s.userData = {
    state: 'WALK',
    timer: 1 + Math.random() * 2,
    direction: new THREE.Vector3(Math.random()-0.5, 0, Math.random()-0.5).normalize(),
    speed: 0.6 + Math.random() * 0.4,
    wobble: Math.random() * 10,
    feet,
    head,
  };
  s.position.set((Math.random()-0.5)*4, 0.1, (Math.random()-0.5)*4);
  return s;
}
```

Using spread with array for position is fine: `f.position.set(...p)`.

Now the update logic. Let me write updateHamster.

Bounds: halfSize = 2.7 (inside tray which is 6.4 wide, so walls at ±3.2, keep hamsters at ±2.7).

```javascript
const HALF = 2.7;

function updateHamster(h, dt) {
  const u = h.userData;
  u.timer -= dt;
  
  // Bobbing always a little
  if (h.children[0]) { /* body */ }
  
  switch(u.state) {
    case 'WALK':
      h.position.x += u.direction.x * u.speed * dt;
      h.position.z += u.direction.z * u.speed * dt;
      h.rotation.y = Math.atan2(u.direction.x, u.direction.z);
      // feet animation
      u.wobble += dt * 12;
      h.position.y = 0.1 + Math.abs(Math.sin(u.wobble)) * 0.04;
      // alternate feet
      u.feet.forEach((f, i) => {
        f.position.y = 0.12 + Math.sin(u.wobble + (i%2?0:Math.PI)) * 0.04;
      });
      // head bob
      h.rotation.z = Math.sin(u.wobble) * 0.03;
      
      // bounds
      if (Math.abs(h.position.x) > HALF || Math.abs(h.position.z) > HALF) {
        u.direction.negate();
        u.direction.x += (Math.random()-0.5)*0.5;
        u.direction.z += (Math.random()-0.5)*0.5;
        u.direction.normalize();
        u.state = 'TURN';
        u.timer = 0.4 + Math.random()*0.4;
      }
      // random pause/new dir
      if (u.timer <= 0) {
        if (Math.random() < 0.35) {
          u.state = 'PAUSE';
          u.timer = 1 + Math.random()*2.5;
        } else {
          u.direction.set(Math.random()-0.5, 0, Math.random()-0.5).normalize();
          u.timer = 1 + Math.random()*3;
        }
      }
      break;
    
    case 'PAUSE':
      // idle: gentle breathing
      h.position.y = 0.1 + Math.sin(performance.now()*0.003)*0.01;
      // nibble (head bob)
      h.rotation.z = Math.sin(performance.now()*0.008)*0.05;
      if (u.timer <= 0) {
        u.direction.set(Math.random()-0.5, 0, Math.random()-0.5).normalize();
        u.state = 'WALK';
        u.timer = 1 + Math.random()*3;
      }
      break;
    
    case 'TURN':
      h.rotation.y += (u.turnDir || 1) * dt * 4;
      h.position.y = 0.1;
      if (u.timer <= 0) {
        u.state = 'WALK';
        u.timer = 1 + Math.random()*3;
      }
      break;
  }
}
```

Need to initialize u.turnDir. Let me set it when entering TURN.

Now the rider hamster. Let me make hamster[0] the special one. Actually, let me make a separate handling. Let me give one hamster a flag `isRider = true`.

Rider behavior:
```javascript
case 'GO_WHEEL':
  // move toward wheel
  const toWheel = new THREE.Vector3(wheelPos.x - h.position.x, 0, wheelPos.z - h.position.z);
  const dist = toWheel.length();
  toWheel.normalize();
  h.position.x += toWheel.x * u.speed * dt;
  h.position.z += toWheel.z * u.speed * dt;
  h.rotation.y = Math.atan2(toWheel.x, toWheel.z);
  // wobble
  ...
  if (dist < 0.3) {
    u.state = 'RIDE';
    u.timer = 3 + Math.random()*3;
  }
  break;

case 'RIDE':
  // position on wheel bottom
  h.position.set(wheelPos.x, 0.12, wheelPos.z);
  h.rotation.y = Math.PI/2; // face X
  // wheel spins
  wheel.userData.spinSpeed = 6;
  // wobble feet
  u.wobble += dt*14;
  u.feet.forEach((f,i)=>{ f.position.y = 0.12 + Math.sin(u.wobble + (i%2?0:Math.PI))*0.05; });
  if (u.timer <= 0) {
    u.state = 'WALK';
    u.direction.set(Math.random()-0.5,0,Math.random()-0.5).normalize();
    u.timer = 1+Math.random()*3;
  }
  break;
```

And occasionally the rider decides to go to the wheel. Let me integrate: in the WALK timer expiry, if this is the rider and random chance, set GO_WHEEL.

Actually simpler: the rider has a separate timer. Let me handle the rider separately before the general update, or add a check.

Let me restructure: I'll give each hamster a `role` property. If role === 'rider', it follows rider logic. Otherwise general wander.

Let me write a unified update that checks role.

Hmm, to keep it clean, let me just handle the rider within the same switch by adding GO_WHEEL and RIDE states, and gate the transition to those states with the isRider flag.

In the WALK state, when timer expires:
```javascript
if (u.timer <= 0) {
  if (u.isRider && Math.random() < 0.5) {
    u.state = 'GO_WHEEL';
    u.timer = 4 + Math.random()*3;
  } else if (Math.random() < 0.35) {
    u.state = 'PAUSE';
    u.timer = 1 + Math.random()*2.5;
  } else {
    u.direction = random;
    u.timer = 1 + Math.random()*3;
  }
}
```

Good.

Now the main loop:
```javascript
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  
  wheel.rotation.x += wheel.userData.spinSpeed * dt;
  wheel.userData.spinSpeed *= 0.96;
  if (Math.abs(wheel.userData.spinSpeed) < 0.01) wheel.userData.spinSpeed = 0;
  
  hamsters.forEach(h => updateHamster(h, dt));
  
  controls.update();
  renderer.render(scene, camera);
}
```

Wait, the rider's feet animation references u.wobble but in RIDE state I update it. But in non-rider hamsters during WALK I also use wobble. Fine.

But there's an issue: in RIDE, I set h.position directly each frame, overriding any WALK movement. Good.

Also, when the rider leaves the wheel (goes back to WALK), it continues from wheel position. Good.

Let me make sure the rider starts somewhere and eventually rides. Since it starts in WALK, after some time it'll randomly pick GO_WHEEL. Good.

Now let me also make the food bowl interactive-ish: maybe a hamster occasionally goes to eat. To keep it simpler and meet "interacting with one object," the wheel interaction suffices. But let me add a subtle food bowl detail: pellets could decrease. Nah, keep it simple. The wheel is the interactive object.

Actually, the requirement says "one interactive object such as a wheel, tunnel, food bowl, or toy." The wheel with spinning is good. Let me make the wheel clearly interactive by having a hamster ride it.

Let me also add a little note in the UI explaining what to do.

Let me also add a second interactive element maybe: clicking a hamster makes it scurry? That could be fun but adds complexity. Let me add raycasting: click a hamster and it quickly runs away (startles). That's a nice touch and easy.

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
window.addEventListener('click', (e) => {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  // check intersection with hamsters
  const meshes = [];
  hamsters.forEach(h => h.traverse(o => { if (o.isMesh) meshes.push(o); }));
  const hits = raycaster.intersectObjects(meshes);
  if (hits.length > 0) {
    // find owner hamster and startle it
    let obj = hits[0].object;
    while (obj.parent && !obj.userData.isHamster) obj = obj.parent;
    if (obj.userData.isHamster) {
      obj.userData.state = 'WALK';
      obj.userData.direction = new THREE.Vector3(Math.random()-0.5,0,Math.random()-0.5).normalize();
      obj.userData.speed = 1.5;
      obj.userData.timer = 1 + Math.random();
    }
  }
});
```

I need to mark each hamster group with isHamster: true in userData. Let me set s.userData.isHamster = true.

This adds a fun interactive element (click hamster to make it run). 

Let me finalize all code and write the file.

Let me also add a nice background color and maybe a gradient. I'll set scene.background to a soft color.

Let me add fog? Not necessary.

Let me add ground shadow receiver on the tray floor. The tray bottom will receive shadows.

Let me set up lights:
```javascript
const ambient = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambient);

const hemi = new THREE.HemisphereLight(0xbfe3ff, 0xd9bfa0, 0.6);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(5, 8, 4);
sun.castShadow = true;
sun.shadow.mapSize.width = 2048;
sun.shadow.mapSize.height = 2048;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 30;
sun.shadow.camera.left = -8;
sun.shadow.camera.right = 8;
sun.shadow.camera.top = 8;
sun.shadow.camera.bottom = -8;
scene.add(sun);
```

Good.

Renderer:
```javascript
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);
```

Camera:
```javascript
const camera = new THREE.PerspectiveCamera(50, aspect, 0.1, 100);
camera.position.set(6, 6, 8);
```

OrbitControls:
```javascript
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1, 0);
controls.minDistance = 4;
controls.maxDistance = 20;
controls.maxPolarAngle = Math.PI * 0.49; // don't go below floor
```

Now let me assemble the cage.

Tray:
```javascript
// Floor base
const trayMat = new THREE.MeshStandardMaterial({ color: 0x7fc8f8, roughness: 0.8 }); // light blue tray
```

Hmm let me pick a nice tray color. Maybe a soft teal or cream. Let me use 0xbde0fe (light blue) or 0xa3e4d7. Let me use 0x90e0ef (sky). Actually for bedding contrast, a neutral tray. Let me use 0xfdf6e3? No. Let me use a soft mint: 0xa3e4d7.

Actually let me make the tray a warm cream/white so bedding (tan) shows. Tray color 0xf5f0e6.

Let me define:
- Tray bottom + walls: color 0xfdf3e7 (cream)
- Bedding chips: tan 0xd9a06b
- Upper transparent walls: light blue, opacity 0.12

Let me write createCage:

```javascript
function createCage() {
  const cage = new THREE.Group();
  const trayMat = new THREE.MeshStandardMaterial({ color: 0xfdf3e7, roughness: 0.9, flatShading: true });
  
  // Bottom
  const bottom = new THREE.Mesh(new THREE.BoxGeometry(6.6, 0.3, 6.6), trayMat);
  bottom.position.y = 0.15;
  bottom.receiveShadow = true;
  cage.add(bottom);
  
  // Lower solid walls (height 0.7)
  const lowH = 0.7;
  const t = 0.2;
  const walls = [
    { w: 6.6, d: t, x: 0, z: 3.2 },
    { w: 6.6, d: t, x: 0, z: -3.2 },
    { w: t, d: 6.6, x: 3.2, z: 0 },
    { w: t, d: 6.6, x: -3.2, z: 0 },
  ];
  walls.forEach(w => {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(w.w, lowH, w.d), trayMat);
    wall.position.set(w.x, 0.3 + lowH/2, w.z);
    wall.receiveShadow = true;
    wall.castShadow = true;
    cage.add(wall);
  });
  
  // Transparent upper walls (height 1.8)
  const glassMat = new THREE.MeshPhysicalMaterial({ 
    color: 0xcdefff, transparent: true, opacity: 0.14, 
    roughness: 0.05, metalness: 0, transmission: 0.2 
  });
  const glassH = 1.8;
  const glassY = 0.3 + lowH + glassH/2;
  const glassWalls = [
    { w: 6.6, d: 0.1, x: 0, z: 3.2 },
    { w: 6.6, d: 0.1, x: 0, z: -3.2 },
    { w: 0.1, d: 6.6, x: 3.2, z: 0 },
    { w: 0.1, d: 6.6, x: -3.2, z: 0 },
  ];
  glassWalls.forEach(w => {
    const g = new THREE.Mesh(new THREE.BoxGeometry(w.w, glassH, w.d), glassMat);
    g.position.set(w.x, glassY, w.z);
    cage.add(g);
  });
  
  // Top bar frame (metal)
  const barMat = new THREE.MeshStandardMaterial({ color: 0xd4d4d4, metalness: 0.7, roughness: 0.4 });
  const barR = 0.05;
  const topY = 0.3 + lowH + glassH;
  // top frame edges
  const frame = [
    { len: 6.6, x: 0, z: 3.2, rotZ: 0, axis: 'x' },
    { len: 6.6, x: 0, z: -3.2, rotZ: 0, axis: 'x' },
    { len: 6.6, x: 3.2, z: 0, rotZ: 0, axis: 'z' },
    { len: 6.6, x: -3.2, z: 0, rotZ: 0, axis: 'z' },
  ];
  frame.forEach(f => {
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(barR, barR, f.len, 8), barMat);
    bar.position.set(f.x, topY, f.z);
    if (f.axis === 'x') bar.rotation.z = Math.PI/2;
    else bar.rotation.x = Math.PI/2;
    cage.add(bar);
  });
  
  // Vertical bars on top frame
  for (let i = -3; i <= 3; i++) {
    // along front/back
    const vb = new THREE.Mesh(new THREE.CylinderGeometry(barR, barR, 0.5, 8), barMat);
    vb.position.set(i * 0.9, topY - 0.25, 3.2);
    cage.add(vb);
    const vb2 = vb.clone();
    vb2.position.z = -3.2;
    cage.add(vb2);
  }
  for (let i = -3; i <= 3; i++) {
    const vb = new THREE.Mesh(new THREE.CylinderGeometry(barR, barR, 0.5, 8), barMat);
    vb.position.set(3.2, topY - 0.25, i * 0.9);
    cage.add(vb);
    const vb2 = vb.clone();
    vb2.position.x = -3.2;
    cage.add(vb2);
  }
  
  return cage;
}
```

This is getting detailed but should look good. Let me simplify the vertical bars a bit—maybe just skip or keep minimal. Actually let me keep a simpler top frame without too many vertical bars to avoid clutter. I'll add a few.

Actually, let me reduce the cage complexity. The transparent walls + a simple top rim are enough. Let me drop the elaborate vertical bars and just do a top frame rim (the 4 horizontal bars). That reads as a cage top edge. Good enough.

Hmm, but a bare top might look like an open box. Let me add vertical bars to make it clearly a cage. I'll keep a moderate number.

Let me keep it but reduce to every 1 unit.

OK let me just write it and not overthink. I'll include vertical bars.

Now, let me put together the complete file. Let me be thorough.

Let me reconsider wheel position relative to cage. Wheel at (2.2, 0, -2.2). Radius 0.8, center at y = 0.85. So it fits. Food bowl at (-2.2, 0, 2.2). Tunnel at (-2.2, 0, -2) spanning x from -3.45 to -0.95. That might overlap the wheel area. Let me place tunnel at (0, 0, -2.4) spanning x from -1.5 to 1.5, so it's in the back middle. And wheel at (2.3, 0, -2.3), food at (-2.3, 0, 2.3). Hamsters spawn in center area.

Let me set:
- Wheel: (2.3, 0, -2.3)
- Food bowl: (-2.3, 0, 2.3)
- Tunnel: center (0, 0, -2.3), along X, length 2.5 → spans x -1.25 to 1.25 at z=-2.3

Hamsters spawn around center: ((Math.random()-0.5)*3, 0, (Math.random()-0.5)*3).

Good.

Now let me write the final complete file.

Let me double check the torus for wheel rings. TorusGeometry(radius, tube, radialSegments, tubularSegments). Default orientation: the torus lies in the XY plane with hole along Z. I want the wheel to spin around X axis, with the ring in the YZ plane. So I need to rotate the torus by 90° around X (or construct appropriately).

If I create torus in XY plane (normal = Z), then rotate the mesh so normal points to X: rotation.x = Math.PI/2 would rotate Z-normal to... rotating around X by 90° takes Z to Y? Let me think. Rotation around X by +90°: Y→Z, Z→-Y. Hmm. I want the ring plane to be YZ, meaning normal along X. 

Start: torus in XY plane, normal along +Z. Rotate around Y by 90°: Z→X? Rotation around Y by +90°: X→-Z, Z→X. So normal +Z becomes +X. Yes! So rotate the ring mesh around Y by 90°: ring.rotation.y = Math.PI/2. Then the ring is in YZ plane, hole along X. And spinning the wheel around X axis (wheel.rotation.x) spins it correctly. 

But wait, I'm building the wheel as a group and rotating the whole group around X. The individual rings need correct initial orientation. Let me set ring.rotation.y = Math.PI/2 on each ring mesh. Then when the group rotates around X, rings spin in their plane. Good.

Actually, simpler: I can just build the rungs and rings and rotate the whole group. Let me set ring rotation so they're in YZ plane.

Let me verify: Torus default is in XY plane (like a donut lying flat, hole pointing up along Z). To stand it up like a wheel (in YZ plane, hole pointing along X = axle), rotate 90° about Y. Yes ring.rotation.y = Math.PI/2.

Alternatively, rotate about... let me just use rotation.y = Math.PI/2 and it should work. Let me also consider the rungs: rungs are cylinders along X (I set rotation.z = Math.PI/2 to make default-Y cylinder point along X). They connect the two rings at x = ±0.3. Their positions are on the circle in YZ. Good.

When the wheel group rotates about X, the rungs (along X) just rotate around themselves positionally—their endpoints trace circles in YZ. Good, that's the wheel spinning.

Alright.

Let me also make sure the rider hamster faces the right way and appears inside the wheel. Rider at (2.3, 0.12, -2.3) facing +X (rotation.y = Math.PI/2 means facing +X? atan2(x,z): facing +X means direction (1,0,0), atan2(1,0) = PI/2. Yes rotation.y = PI/2 faces +X). Good. The hamster sits at the center of the wheel (x=2.3 is center between rings at 2.3±0.3). Wait, rings at x = center ± 0.3. If wheel center x = 2.3, rings at 2.0 and 2.6. Rider at x=2.3 is between them, inside. Good. And z=-2.3 is center of ring circle (bottom of ring is at z where sin(angle)=-1... hmm).

Wait, the ring is a circle in YZ plane centered at (x, ringCenterY, ringCenterZ)? No. The ring position I set is the ring's center. Let me define wheel center properly.

Let me set the wheel group position to the wheel's center point. Rings are offset in X by ±0.3 from group center. The ring circle is centered at the ring's own position (which is on the group's center line in YZ). So the ring circle is centered at (ring.x, group.y, group.z) with radius 0.8 in the YZ plane.

So if wheel group at (2.3, 0.85, -2.3), rings at (2.0, 0.85, -2.3) and (2.6, 0.85, -2.3). Ring circles centered at y=0.85, radius 0.8, so they span y from 0.05 to 1.65. Bottom of wheel at y=0.05. Good, touches near floor.

Rungs at radius 0.8 from center (0.85 in y): positions y = 0.85 + 0.8*cos(angle), z = -2.3 + 0.8*sin(angle). Bottom rung at angle=PI: y=0.85-0.8=0.05, z=-2.3. Good.

Rider at (2.3, 0.12, -2.3): that's at the bottom center of the wheel, between the rings, inside. Facing +X. Looks like running. 

But the rider at y=0.12 is basically on the floor level, at the bottom rung. Good, looks like it's running on the bottom of the wheel.

Actually, I want the rider to look like it's standing on the bottom rung running. Placing at y=0.12 (feet) with body up is fine.

Let me set rider position.y so it sits right. Hamster feet at y~0.1, body center ~0.45. At y=0.12 the whole group is shifted so feet ~0.12... wait the hamster group's local feet are at y=0.12 already (I set foot y=0.12). And body at 0.45. If I place group at y=0.12, then feet at 0.24, body at 0.57. That's floating a bit. Let me place rider group at y=0.05 so feet at 0.17, near the bottom rung (0.05). Eh, close enough. Let me place at y=0.0.

Hmm, actually the hamster standing on the floor normally has group at y=0.1 (I set h.position.y=0.1 in WALK). For the rider on the wheel, I want it elevated to sit on the bottom rung. Bottom rung at y=0.05. So rider group at y=0.05 → feet at 0.17, slightly above rung. Or y=0.0 → feet at 0.12. Let me just set rider at y=0.05. It'll look like it's up in the wheel. Fine.

Actually, let me reconsider: maybe the rider should run on the inner wall higher up? No, hamsters run at the bottom. Keep at bottom. y=0.05.

Let me finalize.

Let me also add a subtle detail: when the wheel spins, maybe add a small "speed" indicator or just trust the visual.

Now let me also make sure the hamsters cast shadows. Set each hamster's meshes castShadow = true. I'll traverse and set. Or set material.castShadow. MeshStandardMaterial supports castShadow on meshes. Let me set in createHamster: after creating, traverse and set o.castShadow = true, o.receiveShadow = true. Actually setting on group: I'll do h.traverse(o => { if (o.isMesh) { o.castShadow = true; }}).

Similarly for other objects.

Let me write it all now. Final code:

I'll include a title and instructions overlay.

Let me write the CSS for overlay:
```css
body { margin: 0; overflow: hidden; font-family: ...; }
#info { position: fixed; top: 16px; left: 50%; transform: translateX(-50%); ... }
```

Let me finalize.

One concern: import map with unpkg. Let me use a stable version. three@0.160.0. The addons path. Let me verify the URL structure:
- https://unpkg.com/three@0.160.0/build/three.module.js
- https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js

These should work. Alternatively jsdelivr:
- https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js
- https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js

Both fine. I'll use unpkg.

Let me write the final HTML.

Let me also add a fallback message if modules fail—not necessary.

Let me make the scene robust: wrap in try/catch? Not needed.

Let me write it out fully now.

I realize I should double-check the hamster feet spread usage: `footPositions.forEach(p => { f.position.set(...p); ...})`. p is [-0.25, 0.12, 0.3]. set(...p) works. Good.

Let me also handle the rider feet animation variable name collision: u.wobble used for both. Fine.

Let me write the complete code. I'll be comprehensive.

Also, I want the hamsters to have a little personality—the rider is hamster[0]. Let me set isRider true for index 0.

Let me also vary hamster scale slightly for variety.

Let me write final.

For the "funny" aspect, maybe add a tiny hat or make one hamster bigger? Let me add a small accessory to one hamster—a little party hat or bow—to be cute. Optional. Let me add a small cone "party hat" on one hamster for fun. Actually, let me add colorful little hats to make them distinct and funny. I'll add a party hat (cone) to the rider.

Party hat:
```javascript
const hatMat = new THREE.MeshStandardMaterial({ color: 0xff4444, roughness: 0.7, flatShading: true });
const hat = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.25, 8), hatMat);
hat.position.set(0, 0.95, 0.4);
// add pom pom
const pom = new THREE.Mesh(new THREE.SphereGeometry(0.05, 6, 6), new THREE.MeshStandardMaterial({color:0xffff00}));
pom.position.set(0, 1.1, 0.4);
s.add(hat, pom);
```

Nice. Let me add to rider.

Alright, writing final file now. Let me make sure everything is consistent.

Let me write the complete thing.

Actually, I realize I should double check: when I do h.traverse to set castShadow, but I also reference h.children[0] as body. children[0] is body (first added). Good.

Let me also make sure the pause breathing uses performance.now consistently. Fine.

Let me write it.

Final code below.

Let me also cap dt to avoid jumps.

Let me write the animate loop with clock.

Also add auto-rotate? The requirement says user can rotate camera. Auto-rotate could be nice but might conflict. Let me enable a slow auto-rotate off by default; maybe enable it for a nice showcase. I'll enable autoRotate at slow speed so it feels alive, but user can override. Actually let me leave autoRotate off so user controls it, but I'll mention drag to rotate. Hmm, "able to rotate the camera" — OrbitControls allows that. Let me add a gentle autoRotate so it's always moving a bit, which is pleasant. I'll set autoRotate true, autoRotateSpeed 0.4. User can still grab and rotate. That's fine.

Let me finalize.

I'll write clean code with comments.

Let me produce the final answer.

Let me reconsider the number of hamsters: 5 is good. One with hat (rider). Colors varied.

Let me write.

Also, I should ensure the canvas resizes and controls update.

Let me write the resize handler:
```javascript
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

Good.

Now, writing the whole file.

Let me make the background a nice soft gradient via CSS on body and scene.background color matching. I'll set scene.background = 0xcfe8ff (soft blue) and body background same, so no harsh edges.

Let me write it all.

I think I've planned enough. Let me write the final complete index.html.

Let me reconsider the wheel spin decay and rider: while rider.active, set spinSpeed = 6 each frame so it keeps spinning. When rider leaves, decay. Good.

Also, I should make the rider only one at a time obviously. Only hamster[0] is rider.

Let me also make sure non-rider hamsters don't accidentally enter GO_WHEEL/RIDE. Only rider role triggers those. In WALK timer expiry, the condition checks u.isRider. Non-riders never set GO_WHEEL. Good.

Let me write.

Also for TURN state, I set u.turnDir. Let me set it when transitioning to TURN: u.turnDir = Math.random()<0.5?1:-1.

Let me finalize the update function with turnDir initialization.

Writing now.

Let me also add a gentle idle sway to paused hamsters (turn head). Already have rotation.z nibble.

OK final code.

Let me write it all out cleanly.

I'll also add a small comment header.

Let me produce the answer with the full code and a brief explanation.

Let me make sure I import OrbitControls correctly and use it.

Complete code:

I need to be careful about one thing: In the import map, I reference "three/addons/". Then import from "three/addons/controls/OrbitControls.js". Good.

Let me write.

Also, I want to double-check lathe geometry for food bowl works. LatheGeometry(points, segments). Points are [Vector2(x,y)] rotated around Y. My points: (0,0),(0.35,0),(0.4,0.25),(0.42,0.3). This creates a bowl shape. Good.

Alright, writing final.

Let me also make sure shadows don't look weird—set shadowMap type PCFSoftShadowMap. Good.

Final answer below.

Let me write the complete file now, carefully.

I'll present the code in a single block and then a short description of how to run and features.

Let me count hamster parts to keep code manageable but cute.

Writing now.
</think>

# Low-Poly Hamster Playground 🐹

Here's a complete, single-file project. Just save it as `index.html` and open it in any modern browser — no build step, no dependencies to install (Three.js loads from a CDN via import maps).

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Low-Poly Hamster Playground 🐹</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #cfe8ff; }
  canvas { display: block; }
  #info {
    position: fixed; top: 16px; left: 50%; transform: translateX(-50%);
    background: rgba(255,255,255,0.82); backdrop-filter: blur(6px);
    padding: 10px 18px; border-radius: 14px;
    font-family: "Segoe UI", system-ui, sans-serif; font-size: 14px;
    color: #3a3a3a; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    pointer-events: none; user-select: none; max-width: 90vw;
  }
  #info b { color: #e05a8a; }
  #title {
    position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
    font-family: "Segoe UI", system-ui, sans-serif; font-size: 12px;
    color: #6a6a6a; pointer-events: none;
  }
</style>
</head>
<body>
<div id="info">🐹 <b>Drag</b> to rotate · <b>Scroll</b> to zoom · <b>Click a hamster</b> to startle it!</div>
<div id="title">Low-Poly Hamster Playground</div>

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

/* =========================================================
   SETUP
   ========================================================= */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xcfe8ff);
scene.fog = new THREE.Fog(0xcfe8ff, 18, 34);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(6.5, 6, 8.5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 4;
controls.maxDistance = 18;
controls.maxPolarAngle = Math.PI * 0.49;   // keep camera above the floor
controls.autoRotate = true;
controls.autoRotateSpeed = 0.5;

/* ---------- Lights ---------- */
scene.add(new THREE.AmbientLight(0xffffff, 0.55));
scene.add(new THREE.HemisphereLight(0xbfe3ff, 0xd9bfa0, 0.65));

const sun = new THREE.DirectionalLight(0xfff4e0, 1.05);
sun.position.set(6, 10, 5);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 30;
const s = 8;
sun.shadow.camera.left = -s; sun.shadow.camera.right = s;
sun.shadow.camera.top = s;   sun.shadow.camera.bottom = -s;
sun.shadow.bias = -0.0004;
scene.add(sun);

/* =========================================================
   CAGE
   ========================================================= */
const trayMat = new THREE.MeshStandardMaterial({ color: 0xfdf3e7, roughness: 0.9, flatShading: true });

function createCage() {
  const cage = new THREE.Group();

  // Base
  const bottom = new THREE.Mesh(new THREE.BoxGeometry(6.6, 0.3, 6.6), trayMat);
  bottom.position.y = 0.15; bottom.receiveShadow = true;
  cage.add(bottom);

  // Low solid walls
  const lowH = 0.7, t = 0.2;
  const lowWalls = [
    { w: 6.6, d: t, x: 0,  z:  3.2 }, { w: 6.6, d: t, x: 0,  z: -3.2 },
    { w: t,   d: 6.6, x: 3.2, z: 0 },  { w: t,   d: 6.6, x: -3.2, z: 0 },
  ];
  lowWalls.forEach(w => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w.w, lowH, w.d), trayMat);
    m.position.set(w.x, 0.3 + lowH / 2, w.z);
    m.receiveShadow = true; m.castShadow = true;
    cage.add(m);
  });

  // Transparent upper walls
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xcdefff, transparent: true, opacity: 0.14,
    roughness: 0.05, metalness: 0,
  });
  const glassH = 1.8, glassY = 0.3 + lowH + glassH / 2;
  const glassWalls = [
    { w: 6.6, d: 0.1, x: 0,  z:  3.2 }, { w: 6.6, d: 0.1, x: 0,  z: -3.2 },
    { w: 0.1, d: 6.6, x: 3.2, z: 0 },   { w: 0.1, d: 6.6, x: -3.2, z: 0 },
  ];
  glassWalls.forEach(w => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w.w, glassH, w.d), glassMat);
    m.position.set(w.x, glassY, w.z);
    cage.add(m);
  });

  // Top bar frame (metal)
  const barMat = new THREE.MeshStandardMaterial({ color: 0xd4d4d4, metalness: 0.7, roughness: 0.4 });
  const barR = 0.05, topY = 0.3 + lowH + glassH;
  [[0, 3.2], [0, -3.2]].forEach(([x, z]) => {
    const b = new