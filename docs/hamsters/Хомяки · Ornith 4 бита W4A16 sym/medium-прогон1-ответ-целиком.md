Let me create a single-file browser project called "Low-Poly Hamster Playground" using Three.js. I need to:

1. Use Three.js (via CDN)
2. Everything in one index.html file
3. Scene includes:
   - A cage
   - A floor/tray
   - Several low-poly hamsters
   - One interactive object (wheel, tunnel, food bowl, or toy)
4. Hamsters should have simple autonomous behavior: walking, pausing, turning, or interacting with one object
5. Cute, low-poly, colorful, funny visual style
6. Should run immediately in a modern browser
7. Camera rotation (orbit controls)
8. Stable, readable, visually clear, fun

Let me build this carefully. I'll use Three.js from CDN with OrbitControls.

Let me plan the structure:

**Cage:**
- A tray/base (like a plastic bin) - a shallow box
- Walls (transparent or open top) - could use glass-like material or wireframe
- Actually, let me make a cage with walls that are semi-transparent like glass/acrylic

**Floor:**
- Wood shavings or bedding - maybe a textured plane with some color
- Could scatter small cones/boxes for shavings

**Hamsters:**
- Body (sphere or rounded shape)
- Head (sphere)
- Ears (small spheres)
- Eyes (black spheres)
- Nose (pink)
- Cheeks (small spheres)
- Feet (small cylinders)
- Tail (small)
- Whiskers

Each hamster needs different colors for variety.

**Interactive object:**
- A exercise wheel - this is classic for hamsters
- When a hamster interacts, it goes on the wheel and the wheel spins

**Autonomous behavior:**
- Each hamster has states: WALKING, PAUSING, TURNING
- Randomly switch between states
- Walk around the cage
- Some might go to the wheel

Let me implement a state machine for each hamster:
- Wander: walk in random directions, occasionally pause
- When near the wheel, sometimes interact (get on and spin)

Let me write the code.

For the low-poly look, I'll use MeshStandardMaterial or MeshLambertMaterial with flat shading (flatShading: true) to get that low-poly faceted look.

Let me structure the hamster builder function:

```javascript
function createHamster(color) {
  const hamster = new THREE.Group();
  
  // Body
  const bodyGeo = new THREE.SphereGeometry(0.5, 8, 6);
  const bodyMat = new THREE.MeshStandardMaterial({ color: color, flatShading: true });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.scale.set(1, 0.9, 1.3);
  hamster.add(body);
  
  // Head
  const headGeo = new THREE.SphereGeometry(0.35, 8, 6);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.position.set(0.55, 0.1, 0);
  hamster.add(head);
  
  // Ears
  const earGeo = new THREE.SphereGeometry(0.12, 6, 6);
  const leftEar = new THREE.Mesh(earGeo, bodyMat);
  leftEar.position.set(0.45, 0.4, 0.15);
  const rightEar = new THREE.Mesh(earGeo, bodyMat);
  rightEar.position.set(0.45, 0.4, -0.15);
  hamster.add(leftEar, rightEar);
  
  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.06, 6, 6);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x111111, flatShading: true });
  const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
  leftEye.position.set(0.8, 0.15, 0.15);
  const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
  rightEye.position.set(0.8, 0.15, -0.15);
  hamster.add(leftEye, rightEye);
  
  // Nose
  const noseGeo = new THREE.SphereGeometry(0.05, 6, 6);
  const noseMat = new THREE.MeshStandardMaterial({ color: 0xff69b4, flatShading: true });
  const nose = new THREE.Mesh(noseGeo, noseMat);
  nose.position.set(0.9, 0.05, 0);
  hamster.add(nose);
  
  // Cheeks
  const cheekGeo = new THREE.SphereGeometry(0.12, 6, 6);
  const leftCheek = new THREE.Mesh(cheekGeo, bodyMat);
  leftCheek.position.set(0.7, 0.0, 0.2);
  const rightCheek = new THREE.Mesh(cheekGeo, bodyMat);
  rightCheek.position.set(0.7, 0.0, -0.2);
  hamster.add(leftCheek, rightCheek);
  
  // Feet
  const footGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.1, 6);
  const footMat = new THREE.MeshStandardMaterial({ color: 0xffb6c1, flatShading: true });
  // position feet under body
  
  // Tail
  const tailGeo = new THREE.SphereGeometry(0.08, 6, 6);
  const tail = new THREE.Mesh(tailGeo, bodyMat);
  tail.position.set(-0.6, 0, 0);
  
  return hamster;
}
```

Now for behavior. Let me define an area for the hamsters to roam within the cage.

Cage dimensions: Let's say the tray is about 8 x 4 units wide.

Let me set up:
- Tray bottom at y=0
- Walls go up to y=1.5 or so
- Cage interior bounds: x from -3.5 to 3.5, z from -1.8 to 1.8

Behavior state machine:
```javascript
const STATES = { WALK: 'walk', PAUSE: 'pause', SPIN: 'spin' };
```

Each hamster:
- state
- stateTimer
- target direction / wander angle
- speed

Walking logic:
- Move forward based on heading
- Occasionally change heading randomly
- When timer runs out, either pause or pick new direction

Pause:
- Stay still for a while
- Then pick new direction

Let me also add a food bowl and have some hamsters go eat.

Actually, let me keep it focused but fun. Let me do:
- Exercise wheel (interactive) - hamsters occasionally go and ride it
- Food bowl - hamsters occasionally go eat

Let me make the wheel the main interactive object since it's most visually fun (spinning).

Let me think about the wheel interaction:
- Wheel is a cylinder (torus-like) that spins on an axis
- When a hamster decides to "spin", it moves to the wheel and gets positioned on the inner bottom
- The wheel spins while the hamster is on it
- After a random time, the hamster leaves

Let me simplify: I'll have the wheel spin continuously (like it's always being used), and hamsters randomly hop on and off. Actually, let me make it so when a hamster rides, the wheel spins faster.

Hmm, let me keep it simpler and more stable. Let me have:
- The wheel spins continuously at a base speed
- When a hamster is riding, it adds to the visual fun
- Hamsters periodically approach and ride the wheel

Let me code the hamster behavior more concretely.

```javascript
class Hamster {
  constructor(color, x, z) {
    this.mesh = createHamster(color);
    this.mesh.position.set(x, 0.5, z);
    this.heading = Math.random() * Math.PI * 2;
    this.state = 'walk';
    this.timer = 0;
    this.speed = 0.4 + Math.random() * 0.2;
    this.wheelRiding = false;
    scene.add(this.mesh);
  }
  
  update(dt) {
    this.timer -= dt;
    switch(this.state) {
      case 'walk':
        this.mesh.position.x += Math.sin(this.heading) * this.speed * dt;
        this.mesh.position.z += Math.cos(this.heading) * this.speed * dt;
        this.mesh.rotation.y = this.heading;
        // bobbing animation
        this.bob += dt * 10;
        this.mesh.position.y = 0.5 + Math.abs(Math.sin(this.bob)) * 0.05;
        // bounce feet
        // bounds check
        if (out of bounds) { turn around; }
        // random turn
        if (Math.random() < 0.01) { this.heading += (Math.random()-0.5) * 1.5; }
        // state transition
        if (this.timer <= 0) {
          // decide next state
          const r = Math.random();
          if (r < 0.4) { this.state = 'pause'; this.timer = 1 + Math.random()*2; }
          else if (r < 0.6 && !this.wheelRiding) { this.startWheel(); }
          else { this.state = 'walk'; this.timer = 2 + Math.random()*3; this.heading += Math.PI; }
        }
        break;
      case 'pause':
        if (this.timer <= 0) {
          this.heading += (Math.random()-0.5) * 2;
          this.state = 'walk';
          this.timer = 2 + Math.random()*3;
        }
        break;
      case 'wheel':
        // already handled separately
        break;
    }
  }
}
```

This is getting complex. Let me simplify the wheel interaction.

Actually, I think a cleaner approach: Have hamsters wander freely. Separately, every so often, one hamster will go to the wheel and ride it for a bit. While riding, the wheel spins.

Let me restructure. I'll give each hamster a "goal" system:
- Default: wander randomly
- Occasionally set goal = wheel, move toward wheel, then ride

Let me write it cleanly:

```javascript
update(dt) {
  const t = this.cooldown; // global cooldown
  ...
}
```

Let me just write straightforward code with per-hamster timer and state. I'll handle wheel riding by positioning the hamster at the wheel and marking it as riding.

Let me define the wheel position and radius.

Wheel:
- A torus or cylinder ring
- Center at (wheelX, wheelCenterY, wheelZ)
- Radius R, axis horizontal (along X)
- Hamster rides on inside bottom

Let me place the wheel at one end of the cage.

OK here's my refined plan. Let me write the whole thing.

For animations:
- Walking: bob up/down, maybe wiggle body
- Riding wheel: wheel rotates, hamster bobs with it
- Pausing: slight idle animation (breathing/nose twitch)

Let me add a little nose twitch during pause for cuteness.

Let me also add ambient details:
- Wood shavings on floor (small rotated boxes/cones in tan color)
- A food bowl with pellets
- Maybe some small toys
- Cage bars or transparent walls

Let me make the cage walls semi-transparent acrylic look with edges visible.

Camera: OrbitControls, positioned to see the whole scene from an angle looking down slightly.

Lighting: Ambient light + directional light for shadows. Add a soft fill light.

Let me add ground shadow or just a nice background color.

Background: a soft gradient or solid pastel color. Let me use a light pastel gradient via CSS background or a scene background color. I'll set scene.background to a soft color, maybe a light blue/pink gradient. For simplicity, a solid soft color, but I could add a gradient texture. Let me do a simple canvas gradient background for extra cuteness.

Actually, let me set the scene background to a soft color and add the room floor.

Let me now write everything out.

I'll structure:
1. HTML with container
2. CSS for full-screen canvas and a title overlay
3. JS with Three.js import from CDN (use importmap or direct script)

For Three.js, I'll use the CDN with ES modules via importmap, or use the older non-module version with OrbitControls included. Let me use a reliable CDN.

Option 1: Use unpkg/jsdelivr with importmap:
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

This is clean and modern. Let me use this.

Let me verify the OrbitControls path. In three 0.160, it's `three/addons/controls/OrbitControls.js`. Yes.

Let me write the full code now.

Let me think about the scene layout:
- Cage tray: outer box, say width (x) = 9, depth (z) = 5, wall height = 1.2
- Interior bounds for hamsters: x in [-4, 4], z in [-2.2, 2.2]
- Floor at y=0 (tray bottom thickness ~0.15)

Let me build the tray as a box with open top, plus walls.

Tray construction:
- Bottom: a flat box
- 4 walls: thin boxes around the perimeter

Or I can make a single box and just show it. But for transparency walls, better to build separately.

Let me make:
- Bottom tray: opaque colored box (like a light blue/green plastic bin)
- Walls: could be same color opaque, or transparent glass. 

For a "cage" feel, let me do opaque colored walls with a rim, OR transparent walls so you can see through. Transparent looks nicer for watching hamsters. Let me do transparent acrylic walls with visible edges (lines) for a modern look. Actually, combining: I'll make the lower part of walls opaque (the tray, like a real hamster bin) and upper part transparent (acrylic extension). That's realistic and cute.

Hmm, let me keep it simpler: Make the whole tray opaque colored, and add vertical bars on top (cage bars) to enclose it, giving that classic cage look while still seeing inside. Actually bars might clutter. 

Let me go with: opaque plastic bin tray (lower walls) + transparent glass/acrylic upper walls. Clean and lets you see hamsters.

Let me build:
- Bin: bottom plate + 4 side walls, all up to height ~1.0, opaque pastel color
- Then transparent walls from 1.0 to 1.8 on top

Actually simpler: one opaque bin to height 1.0, then transparent panel to 1.8. Let me just do two sets of walls.

Let me reduce complexity: I'll make the tray as an opaque box (like a shallow bin) with walls height 1.0. Then add transparent panels on top (height 0.8) using glass material. This gives good visibility.

Let me code the bin:

```javascript
const BIN_W = 9, BIN_D = 5, BIN_H = 1.0, THICK = 0.15;
const binMat = new THREE.MeshStandardMaterial({ color: 0x8fd6e0, flatShading: true, roughness: 0.8 });

// bottom
const bottom = new THREE.Mesh(new THREE.BoxGeometry(BIN_W, THICK, BIN_D), binMat);
bottom.position.y = THICK/2;

// walls
const wallGeo = ... 
```

Let me compute wall positions.

Left wall: position x = -BIN_W/2, spans full depth
Right wall: x = BIN_W/2
Front wall: z = BIN_D/2, spans width
Back wall: z = -BIN_D/2

Each wall thickness THICK.

Then transparent top walls height 0.8 above BIN_H.

Bedding/substrate: a plane at y=THICK with wood color, plus scattered shavings.

Let me scatter shavings: many small thin boxes rotated randomly, tan/beige color, near y=THICK+small.

Food bowl: a small inverted-ish hemisphere or cylinder at a corner.

Wheel: at the other end.

Let me finalize positions:
- Food bowl at (-3.5, 0, -1.8) area (back-left)
- Wheel at (3.8, 0, 0) (right side)

Wheel structure:
- An axle/support frame (two side discs on stands)
- A ring (torus) that spins
- Hamster rides inside

Let me build wheel:
- Support stands: two small boxes/pylons
- Axle: a cylinder connecting them
- Ring: a torus (radius 0.7, tube 0.08) oriented vertically, spinning around the horizontal axle (X axis)
- Rungs: small cylinders across for the running surface (optional, adds detail)

The spinning part = ring + rungs, rotating around X axis.

Hamster riding position: inside the ring at the bottom, so hamster sits at wheel center + (0, -ringRadius + hamsterRadius, 0)... Actually the hamster runs on the inside bottom of the wheel. So hamster center is below the wheel center by (ringRadius - hamsterHeight*0.5). Let me place hamster so its feet are on the bottom rung.

Wheel center: (wheelX, wheelCenterY, wheelZ). Let me set wheelCenterY = 1.0 (so bottom of wheel is at ~0.3, above bedding).

Hamster on wheel: positioned at wheel center, y lowered so it's at the bottom inside. The hamster faces sideways (heading along Z) so it looks like it's running in place. The wheel spins around X.

When riding, I'll animate the hamster to bob slightly and the wheel spins.

Let me set wheel center Y such that the bottom of the ring is near the floor. Ring radius 0.7, so bottom at wheelCenterY - 0.7. If wheelCenterY = 1.0, bottom = 0.3. Good, hamster feet around there.

Hamster riding y: hamster body center at wheelCenterY - ringRadius + 0.3 ≈ 1.0 - 0.7 + 0.3 = 0.6. Let me just position and adjust.

Alright, let me also make the wheel spin whenever a hamster is riding, and give it a base slow spin too for life.

Let me now write the code fully.

For the hamster walking animation, I'll add a subtle scale squash/stretch and a bob. Also rotate little feet. Let me keep feet simple—maybe skip feet animation and just bob.

Let me add whiskers for extra cuteness (thin lines). Could use thin cylinders or lines. Let me add two short whiskers on each side of the nose.

Also add little arms/hands? Optional. Let me add tiny front paws.

Let me keep hamsters reasonably detailed but not overdone.

Let me write createHamster returning a group with named parts so I can animate (nose twitch, ear wiggle, legs).

I'll store references: this.hamster.nose, .leftFoot, etc. Actually let me store parts in the object.

Let me define a function that returns { group, parts }.

Parts I want to animate:
- nose (twitch during pause)
- feet (4 little feet - wiggle during walk)
- body (bob/squash during walk)
- head (slight movement)

Let me include 4 feet as small spheres/cylinders at bottom of body, positioned so they can alternate.

For walking leg animation, I'll oscillate two pairs.

Let me write it.

Actually, to keep it stable and not overcomplicated, I'll do:
- Bob the whole hamster up and down during walk (position.y oscillation)
- Squash body slightly (scale x up, scale y down) in sync
- Twitch nose during pause
- Keep feet static but present

That's enough cuteness.

Let me finalize the code and write it out.

Let me consider performance and stability:
- Use modest segment counts for geometries (low-poly look anyway)
- requestAnimationFrame loop with dt clamping to avoid jumps
- Handle window resize

Let me write the final HTML.

I'll add a title overlay and a small instruction text.

Let me also add subtle mouse-follow or auto-rotate? OrbitControls allows user drag to rotate. I'll enable autoRotate slowly for a nice showcase, and let user override. Actually autoRotate + user interaction can fight. Let me enable autoRotate with slow speed so it gently rotates, and users can drag to take over. That's fine.

Let me set orbit controls target to center of cage.

Now let me write it all.

Let me carefully write the hamster wandering bounds. Hamsters should stay within the bin interior. Interior bounds:
- minX = -BIN_W/2 + 0.5, maxX = BIN_W/2 - 0.5
- minZ = -BIN_D/2 + 0.5, maxZ = BIN_D/2 - 0.5

When a hamster exceeds bounds, clamp and reverse heading (turn around).

Let me handle the wheel goal: When a hamster decides to ride, set state='gotoWheel', move toward wheel center (projected on floor), once close, attach as rider (state='riding'). While riding, wheel spins. Timer for riding; when done, detach and resume walking.

But multiple hamsters could try to ride. Let me allow only one rider at a time to keep it clean. Track `wheelRider` reference. If taken, other hamsters wait or skip.

Simplify: Only one hamster rides at a time. When the current rider finishes, the next interested one can take over. I'll manage with a shared variable.

Let me implement:
- Global `wheelRider = null`
- Hamster with goal wheel: if wheelRider === null and it reaches wheel, becomes rider.
- If wheelRider !== null, the interested hamster just waits (pauses near wheel) or gives up.

To keep simple, when a hamster wants the wheel but it's occupied, it goes back to wandering.

Let me code the wheel approach:
```
case 'toWheel':
  move toward (wheelX, ?, wheelZ)
  if distance < 0.6: startRide()
  break;
```

startRide sets state='riding', wheelRider=this, timer=random(3,6).

riding: position hamster at wheel bottom, bob, wheel spins fast. timer countdown. when done: detach, reset heading, state='walk'.

Let me handle the hamster orientation while riding: face along Z (sideways) so it looks like running. Set mesh.rotation.y = PI/2 or -PI/2 depending on which side.

Let me set wheel at x=+side, hamster rides facing -x (toward center) or +x. Let me face it so its head points in +z or -z. I'll set rotation.y = Math.PI/2 (facing +z... need to check hamster facing). My hamster faces +x originally (head at +x). If I set rotation.y = Math.PI/2, head points toward... rotating by +90° about Y maps +x to -z. Let me not overthink; I'll set it and adjust sign.

Actually for a wheel spinning on X axis, the hamster runs in the Z-direction (its body axis is along Z). So hamster head should point along ±Z. rotation.y = ±90°.

Let me set: hamster.rotation.y = Math.PI/2 (or -Math.PI/2). I'll pick one and it'll look fine.

Now the wheel spin: the ring rotates about X axis. When hamster rides at bottom, to look like it's driving the wheel, the top of the wheel moves toward the hamster's facing... eh, doesn't matter much. I'll just spin it.

Let me now also make the wheel spin slowly even when no one rides (idle motion) — actually, let me have it only spin when ridden, and otherwise be still. That makes riding more meaningful. But a little idle wobble is cute. Let me have it spin when ridden, and settle to still otherwise. Simpler: spin only when ridden.

Let me write the animation for the wheel: 
```
if (wheelRider) { wheelSpinSpeed += (target - current); } 
```
Just set angular velocity = base when riding else decay to 0.

Let me do: 
```
const targetSpeed = wheelRider ? 3.0 : 0.0;
wheelSpin += (targetSpeed - wheelSpin) * 0.05; // smooth
wheelGroup.rotation.x += wheelSpin * dt;
```
Wait, rotating about X. wheelGroup is the spinning assembly. Its rotation.x increases by wheelSpin*dt.

Good.

Now let me write everything. Let me be careful with imports and make sure it runs.

Let me also add a shadow-receiving floor outside? Not necessary. I'll add shadow on the tray bedding maybe. Let me enable shadows on main light and have hamsters cast shadows on bedding for depth. Might help readability. Let me enable renderer.shadowMap and set light.castShadow. Then hamsters cast shadows, bedding receives. Walls shouldn't receive necessarily. Let me keep shadows but ensure it looks good. To be safe and avoid dark spots, I'll use a fairly strong ambient/directional.

Actually shadows can make it look nicer. Let me enable but tune.

Let me write the final code.

One more: the hamsters should be visible through transparent top walls. Good.

Let me also add eyes with a small shine (specular) — standard material handles that.

Let me add pink inner ears: use a second smaller sphere in a lighter shade for ear inner. Optional; I'll add small darker/lighter ears. Keep simple: ears same color.

Let me add a tail: small sphere at back.

Let me finalize. Writing now.

Let me write the bedding generation:
```
const beddingMat = new THREE.MeshStandardMaterial({ color: 0xe8c98a, flatShading: true });
const bedding = new THREE.Mesh(new THREE.PlaneGeometry(BIN_W-0.3, BIN_D-0.3), beddingMat);
bedding.rotation.x = -Math.PI/2;
bedding.position.set(0, THICK+0.01, 0);
bedding.receiveShadow = true;
```
Scatter shavings:
```
const shavingMat = new THREE.MeshStandardMaterial({ color: 0xdcb56a, flatShading: true });
for (let i=0;i<120;i++){
  const s = new THREE.Mesh(new THREE.BoxGeometry(0.15,0.03,0.05), shavingMat);
  s.position.set((Math.random()-0.5)*(BIN_W-0.6), THICK+0.02+(Math.random()*0.05), (Math.random()-0.5)*(BIN_D-0.6));
  s.rotation.set(Math.random(), Math.random(), Math.random());
  beddingGroup.add(s);
}
```

Food bowl:
```
const bowlMat = new THREE.MeshStandardMaterial({ color: 0xff6b6b, flatShading: true });
const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.25, 0.2, 12, 1, true), bowlMat);
bowl.position.set(-3.5, THICK+0.15, -1.8);
// inside of bowl darker
const kibbleMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, flatShading: true });
for pellets...
```
Let me add a few kibble pellets (small spheres) in the bowl.

Wheel:
```
const wheelMat = new THREE.MeshStandardMaterial({ color: 0xffd93d, flatShading: true }); // yellow
const standMat = new THREE.MeshStandardMaterial({ color: 0x6bcb77, flatShading: true }); // green stands
```
Wheel center at (3.6, 1.2, 0). Ring radius 0.7, tube 0.06.
Torus geometry: new THREE.TorusGeometry(0.7, 0.06, 8, 24). Oriented in YZ plane by default (torus lies in a plane; default torus is in XY plane with hole along Z). To make it a vertical wheel spinning about X, I need the ring's normal along X. Torus default: the ring is in XY plane, hole along Z. Rotating the group 90° about Z would put normal along X? Let me think.

TorusGeometry default orientation: the circle is centered at origin in the XY plane, and the "tube" goes around. The hole axis is Z. So the wheel plane is XY. For a hamster wheel, I want the wheel plane to be YZ (vertical, facing along X), spinning about X axis. So I need to rotate the torus 90° about X? If I rotate about X by 90°, the XY plane becomes XZ plane... hmm.

Let me think clearly. I want:
- Wheel ring lies in the YZ plane (so it's a vertical wheel as seen from the side along X).
- Spins about the X axis (the axle).

Torus default lies in XY plane, hole along Z. To rotate it so it lies in YZ plane with hole along X, I rotate about the X axis by 90°? Rotating the XY-plane circle about X axis by 90°: points (x,y,0) -> (x, 0, y)? Rotation about X by 90°: (x,y,z)->(x, z*cos - y*sin?, ...). Rotation about X by +90°: y->z, z->-y. So (x,y,0) -> (x, 0, y). That maps XY-plane circle to XZ-plane circle. Not YZ.

To map to YZ plane: I want points originally (0,y,z?) Hmm let me instead just rotate about Z by 90°: (x,y,z)->(x*cos - y*sin, x*sin + y*cos, z). For 90°: ->(-y, x, 0). So XY circle -> X... (-y, x, 0) still in XY plane. No.

Simplest: after creating torus, apply rotation so hole points along X. Default hole = Z. Rotate about Y by 90°: (x,y,z)->(x*cos+z*sin, y, -x*sin+z*cos). 90°: ->(z, y, -x). Original circle in XY (z=0): (0,y,0)->(0,y,0). Hmm that keeps it in Y? Let me just test mentally: rotating about Y by 90° takes Z axis to -X axis. So hole (along Z) becomes along -X. Good, hole now along X. And the wheel plane (XY) becomes... XY plane rotated about Y: X->Z, Y->Y, so plane becomes ZY = YZ. 

So rotate torus group.rotation.y = 90° (Math.PI/2) to get a vertical wheel spinning about X. Wait, but then spinning about X: rotation.x on the group. But if I rotate the whole wheel group by 90° about Y to orient, then the spin axis is X of that group, which after orientation points... the axle is along X locally. After rotating group by 90° about Y, local X maps to local Z? This is getting confusing.

Cleaner approach: Build the wheel assembly as a group. Put the spinning ring + rungs in a sub-group "wheelSpin". Orient the wheelSpin group so the ring is vertical and spins about horizontal X. Then rotate wheelSpin.rotation.x for spinning.

To make a torus spin about X and lie in YZ plane: Create torus, then set torus.rotation.x = Math.PI/2. Let's check: default torus in XY plane, hole along Z. Rotate about X by 90°: hole Z -> as computed (x,y,z)->(x, z*cos90 - y*sin90, x*sin90 + z*cos90) = (x, -y, x*1)?? wait let me redo. Rotation about X by angle θ:
x' = x
y' = y cosθ - z sinθ
z' = y sinθ + z cosθ
For θ=90°: cos=0, sin=1:
x' = x
y' = -z
z' = y
Original hole along Z (points (0,0,z)) -> (0, -z, 0), i.e., hole now along Y. Wheel plane was XY (points (x,y,0)) -> (x, 0, y), i.e., XZ plane. So wheel lies in XZ plane (horizontal-ish? no, XZ is horizontal if Y is up). That's a horizontal wheel spinning about... hole along Y means spin axis Y. Not what I want.

Ugh. Let me just think about what I want: vertical wheel (like a clock on the wall facing us along X), spinning about horizontal axis. The axle is horizontal. If the wheel faces us (we view along X), the plane of the wheel is YZ, axle along X.

Take default torus (XY plane, hole Z). I want to rotate so hole -> X. 
Rotation that maps Z-axis to X-axis: rotate about Y by -90°? Rotation about Y by θ:
x' = x cosθ + z sinθ
y' = y
z' = -x sinθ + z cosθ
Z axis point (0,0,1) -> (sinθ, 0, cosθ). For this to be (1,0,0) [X axis], need sinθ=1, cosθ=0 => θ=90°. So rotate about Y by +90° maps Z->X. Good.
Then wheel plane XY: point (1,0,0)->(cos90, 0, -sin90)=(0,0,-1) => Z; point (0,1,0)->(0,1,0)=>Y. So plane XY -> YZ. 

So: create torus, set rotation.y = 90° (π/2). Now it's a vertical wheel in YZ plane, hole/axle along X. Spin about X: wheelSpin.rotation.x += speed. 

But wait—if I set the wheelSpin group's rotation.y = π/2 to orient, then rotating wheelSpin.rotation.x spins about the group's local X which is now pointing along world X (since we only rotated about Y, local X stays world X). Yes! Because rotating about Y doesn't change the X axis direction. So local X == world X. So wheelSpin.rotation.x spins about world X. 

So the assembly:
```
const wheelSpin = new THREE.Group();
const ring = new THREE.Mesh(new THREE.TorusGeometry(R, tube, 8, 28), wheelMat);
ring.rotation.y = Math.PI/2; // orient ring to YZ plane, axle along X
wheelSpin.add(ring);
// rungs: small cylinders along X (the axle direction) connecting inner ring, spaced around
for (i in 0..N) {
  const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.02,0.02, 2*(R-tube), 6), wheelMat);
  rung.rotation.z = Math.PI/2; // along... hmm
  // position rung around the circle
}
```
Wait rungs should be along the axle (X direction) so the hamster runs on them. Each rung is a short cylinder along X, positioned at angle around the ring. Let me create rungs as cylinders oriented along X (rotation.z = π/2 makes cylinder along... default cylinder is along Y. To make along X, rotate about Z by 90°: rotation.z=π/2. Then it's along X.) Position each rung at (0, R*sin? , ...). Let me place rungs around the circle in YZ:
For angle a, rung center at (0, r_inner*cos? ) hmm. The rung spans the width (X) at radius ~R. Its YZ position is at angle a on the circle: y = R*sin(a)? Let me parametrize ring points: since ring is in YZ plane, a point at angle a: (0, R*cos(a), R*sin(a)). Place rung there, oriented along X, length ~2*(R-tube).

Actually the rungs connect the two sides; simplest: each rung is a diameter chord? No, rungs are the steps, they're short bars along the axle at each angular position. Let me place N rungs, each at angular position a_i, located at radius ~R (near outer), oriented along X.

```
for (let i=0;i<20;i++){
  const a = (i/20)*Math.PI*2;
  const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025, 2*(R-0.08), 6), wheelMat);
  rung.rotation.z = Math.PI/2; // along X
  rung.position.set(0, R*Math.cos(a), R*Math.sin(a));
  wheelSpin.add(rung);
}
```
Hmm but the hamster runs on the inside bottom. The rungs at the bottom (a=−90°, i.e., y negative) are where feet go. Fine.

Stands (support): two pylons holding the axle. Place at x = ±(width/2 + something). The axle spans X from -L to L. Stands at the ends going down to floor.

```
const L = R + 0.2; // half axle length
// two stand legs
for (side of [-1,1]) {
  const stand = new THREE.Mesh(new THREE.BoxGeometry(0.15, axleY, 0.15), standMat);
  stand.position.set(side*(L+0.1), axleY/2 + THICK, 0);
  group.add(stand);
  // base foot
}
```
Actually let me make stands as A-frame or simple vertical posts with a horizontal bar (axle) across top.

Let me do:
- Two vertical posts at x = ±(L+0.15), from floor to axleY.
- A horizontal axle cylinder connecting them along X at height axleY.
- The wheelSpin ring mounted on the axle (centered at x=0, y=axleY, z=0), spinning.

axleY = wheelCenterY.

Let me set wheelCenterY = 1.3. Ring R=0.7, so bottom of ring at 0.6. Hamster feet ~0.6. Good, above bedding (THICK=0.15). 

Stand posts height = axleY = 1.3. Posts at x=±(L+0.15) where L = R + tube + 0.1 ≈ 0.7+0.06+0.1=0.86. So posts at x=±0.96. Axle from -0.96 to 0.96.

Let me build:
```
const wheelGroup = new THREE.Group();
wheelGroup.position.set(WHEEL_X, THICK, WHEEL_Z); // base at floor
const axleY = 1.3;
const L = 0.9;
// posts
for side ±:
  post = box(0.14, axleY, 0.14)
  post.position.set(side*(L+0.1), axleY/2, 0)
  wheelGroup.add(post)
// axle
axle = cylinder(radius 0.05, length 2*L+0.3, oriented along X)
axle.rotation.z = Math.PI/2
axle.position.set(0, axleY, 0)
wheelGroup.add(axle)
// wheelSpin
wheelSpin = new THREE.Group()
wheelSpin.position.set(0, axleY, 0)
wheelSpin.rotation.y = Math.PI/2  // orient ring to YZ plane
wheelSpin.add(ring, rungs...)
wheelGroup.add(wheelSpin)
```
Wait, if I set wheelSpin.rotation.y = π/2 to orient the ring, then spinning about wheelSpin.rotation.x works as established. But the rungs I placed assuming ring in YZ plane with positions (0, R cos a, R sin a) — those are in wheelSpin local coords before the rotation.y. Since I add them to wheelSpin and wheelSpin has rotation.y=π/2 applied, they'll be transformed. But I positioned them in local YZ which after rotation.y=π/2 maps YZ->? rotation.y maps (x,y,z)->(x cosθ + z sinθ, y, -x sinθ + z cosθ). Local point (0, Y, Z) -> (Z sinθ, Y, -Z cosθ) with θ=90: -> (Z, Y, -Z). Hmm that distorts. This is getting messy because the rungs need to be consistent with the rotated ring.

Better approach: Build everything in wheelSpin's local frame WITHOUT the rotation.y, i.e., keep the ring in its default XY orientation and spin about Z? No, I want spin about X for a vertical wheel.

Alternative cleaner approach: Don't use rotation.y on the group. Instead:
- Keep wheelSpin default orientation.
- Create the ring with rotation.x = π/2 so it lies in YZ plane and axle along... let me recompute. Earlier: rotate default torus about X by 90° gave wheel plane XZ, hole along Y. Not what I want.

Let me recompute which single rotation puts the torus in YZ plane with hole along X.
Default torus: ring in XY plane, hole along Z.
I want: ring in YZ plane, hole along X.
Transformation: XY-plane -> YZ-plane, Z-axis -> X-axis.
Rotation about Y by +90°: we found maps Z->X and XY-plane->YZ-plane. 
Check: rotation about Y by 90°: (x,y,z)->(x*0 + z*1, y, -x*1 + z*0) = (z, y, -x).
Ring point (1,0,0) [in XY plane] -> (0,0,-1) = -Z. Point (0,1,0)->(0,1,0)=Y. So ring now spans Y and Z => YZ plane. 
Hole direction Z (0,0,1) -> (1,0,0) = X. 
So set torus.rotation.y = Math.PI/2. Good, that's what I had.

Now rungs: I want them along the axle (X axis), placed around the ring. In the torus's LOCAL frame (before rotation.y applied to the mesh), the ring is in XY plane. So a rung at ring angle a is at local position (R cos a, R sin a, 0), oriented along Z (the local hole direction = axle). Then after the mesh's rotation.y=π/2, local Z (0,0,1) -> (1,0,0)=X. So the rung becomes along X. 

So in local frame: rung oriented along Z (default cylinder is along Y, so rotate to Z: rotation about X by 90°, i.e., rotation.x=π/2 gives cylinder along Z? Let me check: default cylinder along Y. Rotate about X by 90°: Y->Z? Rotation about X by 90°: (x,y,z)->(x, -z, y). So Y axis (0,1,0)->(0,0,1)=Z. Yes! So cylinder with rotation.x=π/2 is along Z.). 

So rung:
```
const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025, 2*(R-tube), 6), wheelMat);
rung.rotation.x = Math.PI/2; // along local Z (= axle before rotation)
rung.position.set(R*Math.cos(a), R*Math.sin(a), 0); // wait radius
wheelSpin.add(rung);
```
Hmm, but the rung should be at the outer radius where hamster runs, spanning from -(R-tube) to +(R-tube) in length (the chord across? No—the rung is a step; it's a bar along the axle at angular position a, located at radius ~R). Length = distance across the wheel width = 2*(R - tube) roughly (from inner to outer). Actually the rung length should span the inner diameter region where feet plant. Let me make length = 2*(R - 0.1). Position at radius R (on the ring). Good.

After wheelSpin.rotation.y=π/2, everything is correctly oriented. And spinning: wheelSpin.rotation.x += speed. But wait, wheelSpin has rotation.y=π/2 baked into its initial rotation. If I then add rotation.x increment, does it spin about the correct axis? wheelSpin.rotation is a Euler; setting rotation.y=π/2 then incrementing rotation.x... Three.js rotations compose. Incrementing rotation.x on a group that already has rotation.y=π/2 will rotate about the local X axis (after Y rotation). Local X after Y-rotation=90°: X axis maps to? rotation about Y by 90° maps X(1,0,0)->(0,0,-1)=-Z. So local X axis of wheelSpin points along world -Z. So spinning about local X would spin the wheel in the... wrong plane (it'd spin about world -Z, making the wheel spin in XY-ish plane). That's wrong.

I need to spin about world X (the axle). Since the group already has rotation.y=π/2, spinning about world X requires care.

Simplest fix: Instead of using Euler rotation.y on wheelSpin, construct wheelSpin already oriented by building the ring directly in YZ plane via geometry, OR do the spin differently.

Cleanest solution: Build the wheel ring geometry already oriented correctly, and spin by rotating about a fixed axis.

Option: Create the wheelSpin group without any pre-rotation. Build the ring as a torus but manually rotate its vertices? Too much.

Better option: Use a different construction. Make the wheel as a set of rungs arranged in a circle, and a couple of ring tori, all built directly in world YZ plane (no group rotation needed), and spin by rotating the whole assembly about world X.

If I never set rotation.y on wheelSpin, and instead place ring and rungs directly in YZ plane using their own rotations, then wheelSpin.rotation.x spins about world X (since wheelSpin has identity rotation). 

So:
- ring: torus, set ring.rotation.x = ? to get it into YZ plane. We need ring in YZ plane. Default torus in XY. To bring to YZ: rotate about X by -90°? Let me recompute. We want ring plane XY->YZ. Rotation about X by 90° mapped XY->XZ (computed earlier). Rotation about X by -90°: (x,y,z)->(x, y*cos(-90)-z*sin(-90), y*sin(-90)+z*cos(-90)) = (x, z, -y). XY point (1,0,0)->(1,0,-1)? that's not YZ. Hmm.

Let me reconsider. Which rotation takes XY plane to YZ plane? 
XY plane contains X and Y axes. YZ plane contains Y and Z axes. So we need X->Z (or -Z) and Y->Y. 
Rotation about Y by 90°: X->? (x,y,z)->(z,y,-x): X(1,0,0)->(0,0,-1)=-Z. Y->Y. So XY plane -> span{-Z, Y} = YZ plane. Good, rotation about Y by 90° (as before).

But that's a Y rotation which conflicts with spinning about X.

Alternatively X->Y, Y->Z (rotation about... ). We want to map the ring's plane to YZ. There are multiple ways. What if ring plane becomes YZ via mapping X-axis->Z-axis and Y-axis->Y-axis (rotation about Y 90°), OR mapping X-axis->Y and Y->Z (that's rotation about X? rotation about X by 90°: X->X, Y->Z. So XY plane -> XZ plane. No.)

The issue: to keep the spin axis as X, I want the wheel plane to be YZ, which requires the "hole" axis to be X. The natural way is rotation about Y by 90° for the ring. But if I apply that as the group's rotation, spinning about X is problematic due to composition.

Solution: Apply the orientation to the individual meshes (ring, rungs) but keep wheelSpin at identity, then spin wheelSpin about X.

So:
- wheelSpin = group at identity, positioned at wheel center.
- ring = torus; to orient into YZ plane with hole along X: I can set ring.rotation such that... I need ring's own rotation = rotation about Y by 90°. Set ring.rotation.y = Math.PI/2. This orients the ring mesh. wheelSpin stays identity.
- rungs: place in local frame as computed (along local Z, at radius), with rung.rotation.x = π/2 to align along Z, then since wheelSpin is identity, they render as-is. But wait, the rungs were designed to be rotated by the group's Y rotation to become along X. If the group is identity, I need to orient rungs myself to be along X and in YZ plane.

Let me just build rungs directly in world terms within wheelSpin (identity):
- A rung is a cylinder along X (world X), positioned at (0, R cos a, R sin a) in YZ plane.
- Cylinder default along Y; to make along X: rotation about Z by 90° (rotation.z=π/2): (x,y,z)->(x*0 - y*1? ) rotation about Z by 90°: x'=x cos90 - y sin90 = -y; y'=x sin90 + y cos90 = x; z'=z. So Y axis (0,1,0)->(-1,0,0)=-X. So cylinder becomes along X (or -X). Good enough (length along X).
- position.set(0, R*cos(a), R*sin(a)).

And ring: torus with rotation.y=π/2 (orients to YZ, hole along X). Let me double check ring with rotation.y=π/2 spins nicely about X when wheelSpin.rotation.x increments. Since wheelSpin is identity and ring is a child, spinning wheelSpin.rotation.x rotates ring about world X. The ring's hole is along world X (we ensured). So it spins correctly! 

So the plan:
```
wheelSpin = new THREE.Group();
wheelSpin.position.set(WHEEL_X, WHEEL_CENTER_Y + THICK, WHEEL_Z);
const ring = new THREE.Mesh(new THREE.TorusGeometry(R, tube, 8, 28), wheelMat);
ring.rotation.y = Math.PI/2;
wheelSpin.add(ring);
// rungs
for a in 0..19:
  rung = new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025, 2*(R-tube), 6), wheelMat);
  rung.rotation.z = Math.PI/2;
  rung.position.set(0, R*Math.cos(a), R*Math.sin(a));
  wheelSpin.add(rung);
// also maybe inner ring for structure
wheelGroup.add(wheelSpin);
```
Wait, but the rungs at a=0 is at (0, R, 0) top; a=π/2 at (0,0,R) front; a=π at (0,-R,0) bottom. Good, they form the wheel circle in YZ. The bottom rung (a=π) at (0,-R,0) is where hamster's feet are. Good.

But hold on, the hamster rides at the BOTTOM inside. The bottom rung is at y = WHEEL_CENTER_Y - R. With WHEEL_CENTER_Y=1.3 (plus THICK?), R=0.7, bottom at 0.6 (+THICK 0.15 => 0.75). Hamster feet ~0.75. Hamster body center ~0.75+0.4=1.15. That's fine, hamster sits low.

Hmm wait, I need to be consistent about THICK. Let me define wheel center in world coordinates including the tray. Let me place wheelGroup at (WHEEL_X, THICK, WHEEL_Z) and build relative to that, so WHEEL_CENTER_Y is relative to tray top. Let me set relative center cy = 1.15 (so absolute 1.3). Bottom rung absolute = 1.3 - 0.7 = 0.6. Hamster feet at 0.6, body center ~1.05. Good.

Actually let me just place wheelSpin directly in world without wheelGroup offset to reduce confusion, but I need stands from floor. Let me keep wheelGroup at y=THICK and use relative coords.

Let me set:
- WHEEL_X = 3.6, WHEEL_Z = 0
- Relative center cy = 1.15, R = 0.68, tube = 0.06
- Bottom rung rel y = cy - R = 0.47 (absolute 0.62). OK.
- Hamster riding: position at (WHEEL_X, THICK + cy - R + footOffset, WHEEL_Z). Hamster body center y = 0.62 + ~0.35 = 0.97. Let me set hamster riding y so feet at bottom rung: hamster feet at rel y = cy - R = 0.47, body center = 0.47 + 0.4 = 0.87. So hamster.position.y = THICK + 0.87 = 1.02. 

Wait, hamster scale: my hamster body radius 0.5. That might be big relative to wheel R=0.68. Let me scale hamsters down a bit, e.g., 0.6x. Or increase wheel size. Let me make wheel R=0.85 and scale hamster to 0.7. Let me tune: hamster body radius 0.5, scaled 0.7 => 0.35 effective. Wheel inner radius ~0.8. Hamster fits.

Let me set R = 0.85, tube = 0.07, cy (rel) = 1.3, bottom rel = 0.45, abs = 0.6. Hamster riding center rel y = 0.45 + 0.32 = 0.77, abs = 0.92.

Stands: posts at rel x = ±(R + tube + 0.1) = ±1.02, from rel y 0 to rel y cy=1.3. Axle at rel y=1.3 spanning x from -1.1 to 1.1.

OK this is fine. Let me just code it and adjust numbers; exactness not critical.

Let me now also handle the hamster riding position precisely: I'll position the riding hamster at wheel center with:
- x = WHEEL_X
- y = THICK + (cy - R) + 0.34 (feet to body center)
- z = WHEEL_Z
- rotation.y = ±π/2 to face sideways

And animate a bob.

Now let me also make sure the wheel spin direction looks like the hamster is running. If hamster faces +Z (rotation.y = -π/2?), the wheel should rotate so the bottom moves toward -Z (back) — like a wheel where the runner drives it. Eh, I'll just spin it consistently; minor.

Let me set spin: when riding, wheelSpin.rotation.x decreases (or increases) at rate ~4 rad/s. The hamster bobs.

Alright. Let me also add a second interactive element maybe: a little food bowl that a hamster can "eat" from (nose near bowl, head bob). But to avoid overcomplication, maybe just the wheel. The prompt says "one interactive object such as a wheel, tunnel, food bowl, or toy." So one is enough. I'll include the wheel as the main interactive object, and optionally the food bowl as decoration with a hamster occasionally visiting. Let me include food bowl as decorative + a hamster sometimes goes to eat (simple), and the wheel as another. Actually, let me keep the wheel as THE interactive object and add food bowl + a tunnel as extra scenery for richness but only wheel has interaction. Hmm, but "interactive object" singular. I'll make the wheel interactive (hamsters ride it). Food bowl and a tunnel as static scenery. That satisfies requirements and looks rich.

Actually, let me add a tunnel too (a half-pipe/tube) for visual interest, static. And a food bowl. And the wheel (interactive). Good.

Let me not overdo; I'll include wheel (interactive), food bowl (deco), and a small tunnel (deco). And shavings. That's a nice scene.

Let me write the tunnel: a half-cylinder or a tube arch. Simple: two half-torus or a bent tube. Let me do a simple "tunnel" as a horizontal cylinder (like a pipe) lying on the bedding, open both ends, colored. Or an arch (half torus). Let me do an arch tunnel: a torus half (semicircle) standing up, colored, as a play tunnel. Simpler: a horizontal tube (cylinder) that hamsters could walk under/through. Let me do a cylinder tunnel lying horizontally:
```
const tunnel = new THREE.Mesh(new THREE.CylinderGeometry(0.35,0.35,1.2, 12, 1, true), tunnelMat);
tunnel.rotation.z = Math.PI/2; // along X
tunnel.position.set(-1.5, THICK+0.35, 1.3);
```
Open ends (no caps since open=true). Add a second color ring at ends. Fine.

Let me place tunnel in the middle-back.

Now let me finalize hamster colors: a palette of cute colors:
- #ffb3ba (pink)
- #baffce (mint green)
- #bae0ff (light blue)
- #ffffba (yellow)
- #e0baff (lavender)
- #ffd8a8 (peach)

Great, 6 colors for 5-6 hamsters.

Let me create 5 hamsters.

Now let me write the behavior more concretely. I'll implement each hamster as an object with methods, updated in the animation loop.

State machine per hamster:
- 'wander': move in current heading, random turns, occasional pause
- 'pause': stand still, nose twitch
- 'toWheel': move to wheel
- 'ride': on wheel, spinning
- 'toFood': move to food bowl (optional)
- 'eat': at food bowl, head bob

Let me include wander + pause + toWheel + ride as core. Maybe add toFood/eat for variety but keep it optional. Let me include eat too for variety since it's easy.

Let me define bounds and helper.

Let me write:

```
const BOUNDS = { minX: -3.8, maxX: 3.8, minZ: -1.9, maxZ: 1.9 };
```
(Wheel at x=3.6 is near maxX edge; hamsters going to wheel will approach from inside.)

Wheel X = 3.6, but bounds maxX=3.8. When hamster goes to wheel, target x = 3.6 (just inside). Fine.

Let me code the update:

```
update(dt, time) {
  this.timer -= dt;
  switch(this.state) {
    case 'wander':
      this.mesh.position.x += Math.sin(this.heading) * this.speed * dt;
      this.mesh.position.z += Math.cos(this.heading) * this.speed * dt;
      this.faceHeading();
      this.walkBob(time);
      // clamp & turn
      this.clampPosition();
      if (Math.random() < 0.02) this.heading += (Math.random()-0.5)*1.6;
      if (this.timer <= 0) this.nextWanderState();
      break;
    case 'pause':
      this.pauseAnim(time);
      if (this.timer <= 0) { this.heading += (Math.random()-0.5)*2.0; this.state='wander'; this.timer = 2+Math.random()*3; }
      break;
    case 'toWheel':
      this.goTo(WHEEL_X, WHEEL_Z, dt);
      if (distToWheel < 0.5) this.startRide();
      else if (this.timer<=0) { this.state='wander'; this.timer=2+Math.random()*3; } // gave up
      break;
    case 'ride':
      this.rideAnim(time);
      if (this.timer <= 0) this.finishRide();
      break;
    case 'toFood':
      this.goTo(FOOD_X, FOOD_Z, dt);
      if (distToFood < 0.45) this.state='eat', this.timer=2+rand...
      else if (timer<=0) resume wander
      break;
    case 'eat':
      this.eatAnim(time);
      if (timer<=0) { heading random; state=wander; timer... }
      break;
  }
}
```

nextWanderState: choose among pause (40%), go to wheel (25% if free), go to food (25% if not currently eating-heavy), continue wander (10%). Let me weight.

Let me track a global `eatingCount` maybe. Keep simple: 
- 45% pause
- 25% toWheel (only if wheel empty)
- 20% toFood (only if food not being eaten and cooldown)
- 10% just continue wander (pick new heading)

But if wheel occupied, and we pick toWheel, we should not start; instead fall back to pause. Let me handle in toWheel update: if wheel occupied, go back to wander.

Let me manage wheel occupancy with `wheelRider`.

For food, multiple can eat; no need to restrict. But to keep calm, add a cooldown per hamster for eating. Let me add this.eatCooldown.

Hmm, getting complex. Let me simplify food: only wander + pause + wheel. Add eating as a rare extra. Actually, let me include a simple "sniff/eat" at food bowl sometimes. I'll add it but keep weights so it's not too frequent.

Let me just implement wander, pause, toWheel, ride, and toFood, eat. I'll gate wheel by occupancy and food by a per-hamster cooldown.

Let me write goTo(targetX, targetZ, dt): move toward target, clamp within bounds, set heading to face movement direction. When close, call callback.

Let me write faceHeading(): mesh.rotation.y = heading (so hamster faces direction of travel). My hamster heads toward +x originally. rotation.y=heading means rotate so +x aligns with (sin heading, cos heading). At heading=0, faces +z? Let me define heading as angle where heading=0 => moving +z (Math.cos(0)=1 in z, sin(0)=0 in x). And facing = heading. Hamster head is at +x locally; after rotation.y=heading, head points to (sin heading, 0, cos heading)? Rotation about Y by heading: local +x (1,0,0) -> (cos heading, 0, -sin heading). Hmm that gives x=cos heading, z=-sin heading. But I moved by (sin heading, cos heading). Slight mismatch (90° offset). Doesn't matter much visually; the hamster will face somewhat along travel. Let me just make heading represent facing and move accordingly, ensuring consistency:

Let me define: heading is the facing angle. Forward vector = (sin heading, 0, -cos heading)? Let me just pick forward = (sin(heading), 0, cos(heading)) and set mesh.rotation.y = heading + something to align head with forward. Since head local +x rotates to (cos heading, 0, -sin heading) for rotation.y=heading. To make head point to (sin heading, 0, cos heading), I need rotation.y = heading - 90°? Let's solve: want rotated local +x = forward = (sin h, 0, cos h). rotation.y=θ maps +x->(cos θ,0,-sin θ). Set cos θ = sin h and -sin θ = cos h => θ = h - 90°? cos(h-90)=sin h ✓, -sin(h-90) = -(-cos h)=cos h ✓. Yes θ = h - π/2. So mesh.rotation.y = heading - π/2 gives head pointing along forward=(sin h,0,cos h). 

I'll just use mesh.rotation.y = heading and accept minor offset, OR use heading - π/2. Let me use heading directly for simplicity and set forward accordingly to match. Actually cleanest: define heading as the rotation.y of the hamster. Forward movement = direction the head faces = rotation of +x by heading: (cos heading, 0, -sin heading). Move along that:
```
pos.x += cos(heading)*speed*dt
pos.z += -sin(heading)*speed*dt
mesh.rotation.y = heading
```
That's consistent. Let me use that.

Let me redefine:
```
this.mesh.position.x += Math.cos(this.heading) * this.speed * dt;
this.mesh.position.z += -Math.sin(this.heading) * this.speed * dt;
this.mesh.rotation.y = this.heading;
```
Good, consistent.

goTo: compute desired heading = atan2(targetX - curX, -(targetZ - curZ))? Since forward = (cos h, -sin h), we want forward toward (dx, dz). cos h ∝ dx, -sin h ∝ dz => h = atan2(-dz, dx). Let me compute: we want unit vector (cos h, -sin h) parallel to (dx,dz). So cos h = dx/|v|, -sin h = dz/|v| => sin h = -dz/|v|. h = atan2(sin h, cos h) = atan2(-dz, dx). 
```
const desired = Math.atan2(-(targetZ - pos.z), (targetX - pos.x));
turn heading toward desired smoothly:
this.heading += normalizeAngle(desired - heading) * turnSpeed * dt;
```
Good.

Let me now also make hamsters avoid overlapping a bit? Not necessary; keep simple. They can pass through each other. Fine for low-poly cute scene. Maybe add slight separation to look nicer but skip for stability.

Now the walkBob: 
```
this.mesh.position.y = BASE_Y + Math.abs(Math.sin(time*this.speed*8)) * 0.06; // bob
this.mesh.scale.x = 1 + Math.sin(time*this.speed*8)*0.04; // squash
this.mesh.scale.y = 1 - Math.sin(...)*0.04;
```
BASE_Y = 0.5 (body center above floor). Wait hamster body center should be around 0.5 (radius 0.5 scaled). At rest hamster sits with bottom at floor y=THICK=0.15, body center at 0.15+0.45=0.6. Let me set BASE_Y = 0.6. During walk bob ±0.06.

Hmm, but I scale the whole hamster group by 0.7 maybe. Let me not scale the group; instead build hamster at smaller radius. Let me build body radius 0.45 and scale group 1.0, base_y = 0.15 + 0.4 = 0.55.

Let me finalize hamster build with body radius 0.45, head radius 0.32, etc.

Let me write createHamster returning group and parts.

Parts:
- body (mesh)
- head (mesh)
- leftEar, rightEar
- leftEye, rightEye
- nose
- leftCheek, rightCheek
- leftFootFL, rightFootFR, leftFootBL, rightFootBR (4 feet)
- tail

I'll store these for animation.

Feet animation during walk: alternate. Let me animate feet as small bob (position.y) alternating pairs. Or rotate them. Simple: lift feet alternately.
```
const step = Math.sin(time*speed*10);
footFL.pos.y = 0.15 + max(0,step)*0.08;
footBL.pos.y = 0.15 + max(0,step)*0.08;
footFR.pos.y = 0.15 + max(0,-step)*0.08;
footBR.pos.y = 0.15 + max(0,-step)*0.08;
```
Eh, feet are small; may not be visible. Let me keep feet static to reduce complexity, just present. Actually let me give them a subtle wiggle. I'll add small rotation to feet. Skip to keep stable. I'll keep feet static, present as little ovals.

Body squash during walk for cute effect: yes.

Head: slight nod during walk. Optional. Keep head static relative to body, or add small bob. Let me add head bob opposite to body for charm. Minor.

Nose twitch during pause: oscillate nose.scale or position.z quickly.
```
nose.scale.setScalar(1 + Math.sin(time*20)*0.15);
```
Nice.

Ears: slight bob. Optional.

Ride animation: hamster positioned at wheel, bobbing, and maybe legs pumping. I'll bob the body and add a little squish. The wheel spins (handled globally).

Eat animation: at food bowl, head dips up/down (nose toward bowl).
```
head.rotation.x = -Math.abs(Math.sin(time*6))*0.3; // dip head
```
Or bob whole head. Let me dip head rotation.

OK let me write it all now. This is a lot but let me be thorough.

Let me also add a subtle idle breathing when paused: body scale y oscillation slow.

Let me now also make sure shadows work. I'll enable shadowMap, set main directional light castShadow, and set receiveShadow on bedding and castShadow on hamsters and objects. Transparent walls shouldn't cast shadows (they won't by default). Let me set hamsters.castShadow=true, bedding.receiveShadow=true, wheel/bowl cast/receive where relevant.

Let me set up lights:
- ambient 0.6
- hemispheric? Let me use ambient + directional + a point for warmth.
- directional key light with shadow.

Let me set directional at angle, castShadow, shadow camera tuned.

Let me write renderer with antialias, shadowMapType PCFSoftShadowMap.

Background: I'll create a canvas gradient texture for a soft sky, or just set scene.background to a pastel. Let me do a gradient via CSS on the body and set scene.background transparent? If background transparent, the CSS shows through — nice gradient backdrop. But transparent background with shadows might look odd. Let me set scene.background to a solid soft color (light gradient is hard). I'll set a CSS gradient behind and make scene background transparent so the gradient shows. Shadows cast on bedding will still be visible against bedding. The floor outside cage—there's no floor outside; hamsters are in the tray. So transparent background is fine. Let me set scene.background = null (transparent) and rely on CSS gradient. Actually THREE scene with null background renders transparent, showing CSS. Good.

But OrbitControls and shadows: shadows on bedding only. Fine.

Let me add a subtle floor outside the cage? Not needed.

Let me also add a nice subtle environment for reflections—not necessary with lambert/standard flat shading.

Materials: Use MeshStandardMaterial with flatShading:true for low-poly look, and some emissive low value for cuteness? Maybe slight emissive on eyes. Eyes black, fine.

Let me set roughness ~0.9, metalness 0 for plastic look.

Let me write final code.

Let me also add a title overlay and a small instruction text.

Let me also handle resize.

Let me write the animation loop with dt:
```
let last = performance.now();
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  let dt = (now - last)/1000;
  last = now;
  dt = Math.min(dt, 0.05); // clamp
  const time = now/1000;
  for (h of hamsters) h.update(dt, time);
  // wheel spin
  const targetSpeed = wheelRider ? 3.5 : 0;
  wheelSpinSpeed += (targetSpeed - wheelSpinSpeed)*0.05;
  wheelSpin.rotation.x += wheelSpinSpeed * dt; // spin about X
  // Wait: wheelSpin.rotation.x increments, but wheelSpin has ring with rotation.y=π/2 as a child, wheelSpin itself identity. Spinning wheelSpin.rotation.x spins about world X. Good.
  controls.update();
  renderer.render(scene, camera);
}
```
Hold on: wheelSpin.rotation.x += dt*speed spins the group about its local X. Since group identity, local X = world X. The ring child has rotation.y=π/2; when we spin parent about X, ring spins about world X, and since its hole is along world X (we oriented it so), it spins like a wheel. 

But careful: wheelSpin.rotation.x += dt*speed spins the group about its local X. Since group identity, local X = world X. The ring child has rotation.y=π/2; when we spin parent about X, ring spins about world X, and since its hole is along world X (we oriented it so), it spins like a wheel. 

Wait, I need to double-check the ring hole is along world X. Ring.rotation.y = π/2. Default torus hole along local Z. After rotation.y=π/2, local Z -> world? rotation about Y by 90° maps Z(0,0,1)->(1,0,0)=X. Yes hole along world X. And spinning parent about world X rotates the ring around its hole axis. 

Now, the rungs: placed at (0, R cos a, R sin a) with rotation.z=π/2 (along X). These are children of wheelSpin, so they spin with it about X. Good, they form the wheel surface. 

Now hamster riding position: at wheel center projected. The hamster stands on the bottom rung. Bottom rung at rel (0, -R, 0) => world (WHEEL_X, CENTER_Y - R, WHEEL_Z). Hamster feet there. Hamster body center above by ~0.35. Let me set hamster ride position:
```
this.mesh.position.set(WHEEL_X, CENTER_Y - R + 0.34, WHEEL_Z);
this.mesh.rotation.y = Math.PI/2; // face sideways (along Z)
```
CENTER_Y here is absolute (including THICK). Let me define CENTER_Y = THICK + 1.3 = 1.45. R=0.85. Bottom rung abs y = 1.45-0.85 = 0.6. Hamster feet 0.6, body center 0.6+0.34=0.94. But hamster base_y (standing) is 0.55. On wheel it's higher (0.9