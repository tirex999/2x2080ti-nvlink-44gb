Let me create a complete, self-contained HTML file for a "Low-Poly Hamster Playground" using Three.js. Let me think through this carefully.

I need to:
1. Use Three.js (via CDN)
2. Create a single index.html file
3. Build a 3D scene with:
   - A cage (walls/fence)
   - A floor/tray
   - Several low-poly hamsters
   - One interactive object (wheel, tunnel, food bowl, or toy)
4. Hamster behavior: walking, pausing, turning, interacting
5. OrbitControls for camera rotation
6. Cute, low-poly, colorful, funny style
7. Run immediately

Let me design this thoughtfully.

**Scene Structure:**
- A playbase/tray (a shallow box representing the cage base)
- Cage walls (transparent or wireframe-ish, or just open rails). For simplicity, I'll make low walls with some transparency or just a fenced area. Actually, let me make a nice cage with semi-transparent walls so you can see inside.
- Floor with bedding color

**Hamster:**
A low-poly hamster built from primitives:
- Body: sphere (squished)
- Head: sphere
- Ears: two small spheres/cones
- Eyes: two small black spheres
- Cheeks: two pink small spheres
- Nose: tiny red/pink sphere
- Feet: small boxes/spheres
- Tail: tiny

I'll group these into a mesh.

**Behavior:**
Each hamster has:
- A target position within the cage bounds
- State machine: WALKING → PAUSING → TURNING → etc.
- When walking, move toward target, rotate to face direction
- When reaching target, pause for a random time
- Occasionally interact with the wheel (spin it) or go to food bowl

**Interactive object:**
Let me do a exercise wheel that spins when a hamster is near/on it, plus maybe a food bowl. Actually the requirement says "one interactive object such as a wheel, tunnel, food bowl, or toy." Let me include a wheel that spins, and hamsters will occasionally run on it. I could also add clicking interaction. Let me make the wheel interactive (clickable) - clicking makes it spin fast, and hamsters get attracted to it.

Actually, let me keep it focused but rich. I'll include:
- A spinning wheel (interactive - click to spin)
- Hamsters wander, pause, turn
- Some hamsters periodically run on the wheel

Let me also add some bedding (small colored cubes/planes scattered), maybe some wood shavings.

**Lighting:**
- Ambient light
- Directional light with shadows
- Maybe hemisphere light for soft shadows

**Colors:**
- Warm background
- Colorful hamsters (tan, white, brown, gray variants)
- Green/tan bedding
- Colorful cage

Let me write the code.

I'll use Three.js r160+ from CDN with importmap for modules, or just classic script. Let me use the module approach with importmap for OrbitControls.

Actually, to keep it simple and robust, let me use the non-module version with a global THREE and include OrbitControls via the addon. Hmm, OrbitControls needs to be imported. Let me use importmap.

Let me structure:

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

This is clean and works in modern browsers.

Now let me build the hamster function. I'll create a function `createHamster(color)` that returns a Group with all parts, and store references for animation (like legs for walking animation).

Let me think about the walk animation - I'll animate legs swinging when walking. Simple pendulum motion on front/back legs.

Let me define the hamster:

```js
function createHamster(options) {
  const hamster = new THREE.Group();
  
  // Body
  const bodyGeo = new THREE.SphereGeometry(0.5, 12, 10);
  bodyGeo.scale(1, 0.9, 1.3); // elongated
  const bodyMat = new THREE.MeshStandardMaterial({ color: options.color, roughness: 0.9, flatShading: true });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  hamster.add(body);
  
  // Head
  const headGeo = new THREE.SphereGeometry(0.35, 12, 10);
  const head = new THREE.Mesh(headGeo, bodyMat.clone());
  head.position.set(0.55, 0.2, 0);
  hamster.add(head);
  
  // Ears
  ...
  
  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.08, 8, 8);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.2 });
  ...
  
  // Cheeks (pink)
  ...
  
  // Nose
  ...
  
  // Feet (4)
  ...
  
  return hamster;
}
```

For flatShading low-poly look, set flatShading: 1 on materials and use low segment geometries.

Let me make the feet as separate meshes positioned so they pivot. Actually for simple walk animation, I'll just bob the body and slightly rotate legs.

Let me keep leg animation simple: when walking, alternate leg positions with sine waves.

Now behavior state machine per hamster:
- states: 'idle' (pause), 'walk', 'turn'
- On 'walk': pick random target point within bounds, face it, move. When close, transition to 'pause'.
- On 'pause': wait random time, then pick new target, transition to 'walk' or 'turn'.
- Occasionally (random chance), a hamster goes to the wheel and 'runs' on it.

Let me implement with a simple timer-based approach updated each frame.

Let me define bounds: cage inner area, e.g., x in [-6, 6], z in [-4, 4].

Interaction with wheel: place wheel at one side. When a hamster's target is the wheel location, it moves there and then "runs" (moves legs fast, wheel spins). After running for a while, it leaves.

Let me code the wheel:
- A big ring (TorusGeometry) 
- Support spokes
- Two side discs (circles) 
- Mounted on an axle/frame
- Spins around its axis

Hamster on wheel: position hamster inside/near wheel, orient so it faces tangent, animate legs fast, increase wheel rotation speed.

Let me simplify: wheel is vertical (like a hamster wheel). Axle is horizontal along X. Wheel rotates around X axis. Hamster stands inside facing... hmm, actually hamster runs on the inside, facing forward (let's say +Z or along the direction of running). 

Let me orient wheel so it rotates around X axis (the axle runs left-right, along X). The wheel plane is YZ. Hamster stands inside near the bottom, facing +X? No...

Standard hamster wheel: it's a wheel you run inside, the wheel axis is horizontal. The hamster faces sideways relative to the axis. If axis is along X, hamster faces along Z (into/out of screen) — actually faces perpendicular to axis, so along Z. The wheel spins around X.

Let me place the wheel so its axis is along X. The wheel spins around X. A hamster inside faces +Z (or -Z) and runs. As it runs, the wheel surface moves.

For simplicity, I'll just make the hamster stand next to the wheel or inside and animate it running in place while the wheel spins faster. That reads as "running on wheel."

Let me place hamster inside the wheel at the bottom, facing +Z, and spin wheel around X. Good enough.

Actually, let me reconsider — simpler and clearer: I'll make the wheel spin continuously slowly, and when a hamster decides to use it, the hamster positions itself inside and the wheel speeds up while it runs.

Let me now also add clickable interaction: raycast on wheel click → spin fast + attract nearby hamsters briefly. And a hint text on screen.

Let me also add a food bowl and maybe scatter some "pellets" (small spheres) that hamsters might go eat. But requirement says focus on one interactive object. I'll include the wheel as primary interactive, and maybe a food bowl as decorative + a couple pellets for flavor. Keep it not overcomplicated.

Let me also add bedding: many small flat boxes with random colors/rotations on the floor.

Let me add a tunnel too? Optional. I'll add a simple tunnel (a half-cylinder or a couple of colored tubes) as decoration and maybe hamsters walk through it. Might complicate. Let me keep tunnel as decorative only to avoid pathing issues. Actually, let me add a tunnel that hamsters can be targets for. Hmm, keep simple: I'll add the wheel (interactive) and a food bowl (decorative + hamsters occasionally visit). 

Let me finalize scope:
- Cage: tray (box, top face) + low transparent walls + maybe decorative rails.
- Bedding: scattered small planes.
- 3-4 hamsters with distinct colors.
- Wheel (interactive, spins, hamsters run on it).
- Food bowl (decorative, hamsters occasionally visit to "eat").
- Lighting with shadows.
- OrbitControls.
- UI hint text.

Let me write the full code now.

For shadows: set renderer.shadowMap enabled, directional light casts shadows, receive shadow on floor.

Let me set up the camera, renderer, controls.

Camera at position like [10, 8, 10] looking at center.

Let me write helper to create hamster with all sub-parts and store references.

I'll make the hamster face +X by default (head at +X). So movement direction computed from target - current.

Let me define walking:
```
hamster.userData = {
  state: 'idle',
  timer: random,
  target: new THREE.Vector3(),
  speed: ...,
  legs: [...],
  bodyMesh,
  ...
};
```

Update loop:
```
switch(state):
  'wander': move toward target; rotateToFace; if dist < 0.3 -> state='pause', timer=random(2,5)
  'pause': timer -= dt; if timer<=0 -> pick new target; state='wander'
  'runWheel': move to wheel; if reached, spin wheel fast, animate legs fast; timer; after run duration -> leave
  'eatFood': move to food bowl; if reached, eat animation; timer; after -> wander
```

Rotation: hamster.rotation.y = atan2(dir.x, dir.z).

Leg animation: for each leg, angle = sin(time*freq + phase) * swing. Rotate leg mesh.x by that. When idle, legs static. When running, higher freq and amplitude.

Body bob: when walking, body.position.y oscillates slightly, and maybe tilt.

Let me keep it manageable.

Let me also add subtle idle breathing (body scale y oscillation) and head slight movement.

Alright, let me write it all out. I'll aim for clean, commented, working code.

Let me consider the cage dimensions. Tray: width (x) 16, depth (z) 12, height (y) 1. Walls height ~2. Inner play area roughly x[-7,7], z[-5,5].

Wheel placed at back-left corner area, e.g., position (-5, 1.2, -4), axis along X. Radius ~1.5.

Food bowl at (5, 1, -3).

Hamsters spawn at random positions in center area.

Let me code the wheel geometry:
```
const wheel = new THREE.Group();
const radius = 1.4;
const tube = 0.12;
// ring
const ringGeo = new THREE.TorusGeometry(radius, tube, 8, 24);
const ringMat = new THREE.MeshStandardMaterial({ color: 0xff69b4, roughness:0.5, flatShading:true });
const ring = new THREE.Mesh(ringGeo, ringMat);
wheel.add(ring);
// spokes
for i in 8: spoke mesh (thin box) rotated around, add.
// side discs (two circles) to give it volume-ish look
const discGeo = new THREE.CircleGeometry(radius, 20);
discMat translucent/color; place at z = ±tube, rotate to lie in YZ plane (Circle is in XY plane by default, so rotate.x -90 to make it YZ). Add two discs.
```
Axle/frame: two vertical posts supporting the wheel axis. Or just mount wheel to a stand.

Let me add a stand: two boxes as legs and an axle cylinder along X at wheel center.

Wheel spins around X. Position wheel so center at (wx, wy, wz). Hamster inside near bottom.

Actually torus with spokes spinning—looks like a wheel. Good.

For the hamster running on it: position hamster at bottom inside, facing +Z (so it runs "forward"), legs animate fast. The wheel spins around X.

Hmm, if hamster faces +Z and wheel axis is X, then hamster's forward is along the wheel's running direction (tangent). Good. Place hamster at (wx, wy - radius + 0.5, wz) roughly inside bottom. Face it +Z: rotation.y = pi/2 (since default faces +X; to face +Z set rotation.y = -pi/2 or pi/2). Let me compute: default +X. To face +Z, rotate.y by 90°? Rotating +X by +90° about Y gives... rotation about Y by angle θ: X→(sinθ,0,cosθ)? Let me recall: rotation about Y: 
[x']   [ cosθ  0 sinθ][x]
[y'] = [   0    0  0   ][y]
[z']   [-sinθ   0 cosθ][z]
So +X (1,0,0) → (cosθ, 0, -sinθ). For facing +Z (0,0,1): cosθ=0, -sinθ=1 → θ=-90° (θ= -π/2): cos(-90)=0, sin(-90)=-1, -sinθ=1. Yes so rotation.y = -π/2 faces +Z. Or rotation.y = +π/2 faces -Z.

I'll set accordingly.

Now the click interaction: use Raycaster on pointerdown, if intersect wheel → set wheelSpinBoost and attract. Let me implement a "excite" that makes wheel spin faster for a few seconds and nearby hamsters head to wheel.

Simpler: clicking wheel sets a flag `wheelExcited` for N seconds, increases base spin speed. Also could spawn pellets. Let me just boost spin and maybe add a little particle? Keep simple: boost spin speed.

Also, let me make clicking anywhere that hits a hamster do a little "boop" jump (funny). That's a nice touch. Let me add: clicking a hamster makes it jump up and run away (set state wander to random spot, small hop). Fun and interactive. Good.

Let me implement pointer handling with raycaster for both wheel and hamsters.

Let me now also add ambient occlusion feel with good lighting.

Let me write everything.

I'll be careful with Three.js API. Using BufferGeometry. TorusGeometry exists. CircleGeometry exists.

Let me write the code fully now.

One more: bedding. Create a function that adds ~120 small colored box fragments on floor at y~0.05-0.2, random x,z within tray, random rotation. Use InstancedMesh for efficiency/cleanliness. Actually simpler to just loop Mesh with shared geometry. InstancedMesh is cleaner. Let me use InstancedMesh with BoxGeometry.

Let me also add a few "pellets" (food) as small brown spheres near bowl, maybe animated (appear/disappear) for fun. Optional. I'll add a handful that get eaten when hamster visits. Keep minimal.

Let me now write final code.

I want to ensure performance and stability. Use delta clamp.

Let me draft the update for hamsters carefully.

```
function updateHamster(h, dt, t) {
  const u = h.userData;
  // apply gravity-free simple movement
  
  if (u.state === 'wander') {
    const dir = new THREE.Vector3().subVectors(u.target, h.position);
    dir.y = 0;
    const dist = dir.length();
    if (dist > 0.15) {
      dir.normalize();
      const step = u.speed * dt;
      h.position.x += dir.x * step;
      h.position.z += dir.z * step;
      // face direction
      h.rotation.y = Math.atan2(dir.x, dir.z);
      // leg + body anim
      animateWalk(h, dt, t, u);
    } else {
      // reached
      if (u.nextState) { u.state = u.nextState; u.nextState=null; }
      else { u.state='pause'; u.timer = rand(1.5,4); }
    }
  } else if (u.state === 'pause') {
    u.timer -= dt;
    // idle anim
    breathe(h, t);
    if (u.timer <= 0) {
      pickNewTarget(h);
    }
  } else if (u.state === 'runWheel') {
    // move to wheel
    const dir = new THREE.Vector3().subVectors(u.wheelPos, h.position); dir.y=0;
    const dist = dir.length();
    if (dist > 0.4) {
      dir.normalize();
      h.position.addScaledVector(dir, u.speed*1.6*dt);
      h.rotation.y = Math.atan2(dir.x, dir.z);
      animateWalk(h, dt, t, u, 2.2); // fast
    } else {
      // running on wheel
      h.rotation.y = -Math.PI/2; // face +Z
      animateWalk(h, dt, t, u, 3.5);
      wheelSpinSpeed += (targetSpeed - wheelSpinSpeed)*dt*2;
      u.timer -= dt;
      if (u.timer <= 0) { u.state='pause'; u.timer=rand(2,4); }
    }
  } else if (u.state === 'eat') {
    const dir = new THREE.Vector3().subVectors(u.foodPos, h.position); dir.y=0;
    const dist = dir.length();
    if (dist > 0.4) {
      dir.normalize();
      h.position.addScaledVector(dir, u.speed*dt);
      h.rotation.y = Math.atan2(dir.x, dir.z);
      animateWalk(h, dt, t, u);
    } else {
      // eat
      nibble(h, t);
      u.timer -= dt;
      if (u.timer <= 0) { u.state='pause'; u.timer=rand(2,4); pickNewTarget? no, pickNewTarget called in pause setup }
    }
  }
  
  // bounds clamping
  h.position.x = clamp(h.position.x, -7, 7);
  h.position.z = clamp(h.position.z, -5, 5);
}
```

Hmm, but I need to handle transitions to runWheel/eat states triggered by timer. Let me integrate into the 'pause' state: when pause timer ends, decide next action based on random: mostly wander, sometimes runWheel, sometimes eat.

Let me restructure pickNewTarget logic inside pause end:
```
if (u.timer <= 0) {
  const roll = Math.random();
  if (roll < 0.25) { u.state='runWheel'; u.timer = rand(4,7); prepare to move to wheel }
  else if (roll < 0.4) { u.state='eat'; u.timer=rand(3,5); }
  else { u.state='wander'; pickNewTarget(h); }
}
```

But 'runWheel'/'eat' need to first travel. Let me handle: when entering runWheel, we don't have a wandering target; we go straight to wheelPos. In update runWheel branch I move toward wheelPos. Good. When it reaches, it runs. Good.

For eat similar.

pickNewTarget sets u.target to random point and picks state wander.

Let me also set initial states: start all in pause with random timers, or wander. Start them wandering at random spots.

Let me set up wheel spin: base slow continuous spin regardless. wheelSpinSpeed variable. Add to wheel.rotation.x each frame *= something. Actually wheel spins around X. wheel.rotation.x += wheelSpinSpeed*dt.

Base speed ~0.5 rad/s. When hamster runs, targetSpeed ramps up to ~8. When none, decays back to base.

Let me manage: 
```
let wheelSpeed = 0.5;
// in animate: 
const target = (wheelExcited || runningHamster) ? 8 : 0.5;
wheelSpeed += (target-wheelSpeed)*dt*1.5;
wheel.rotation.x += wheelSpeed*dt;
```

Good.

Clicking wheel sets wheelExcited timer.

Let me code animateWalk:
```
function animateWalk(h, dt, t, mult=1) {
  const legs = h.userData.legs;
  const freq = (3 + 4*mult);
  legs.forEach((leg, i) => {
    const phase = (i%2===0)?0:Math.PI;
    leg.rotation.x = Math.sin(t*freq + phase) * 0.5 * mult;
  });
  // body bob
  h.userData.body.position.y = 0.45 + Math.abs(Math.sin(t*freq*0.5))*0.05;
}
```

Wait, legs are children of hamster group; rotating them about their local x. Need leg pivot near top. I'll position leg meshes at top of body and they hang down; rotation.x swings them forward/back. Since they're offset in +z/-z and +x/-x, rotation about x works reasonably. Let me just place feet as small meshes at body bottom corners and rotate about x. It won't be anatomically perfect but looks like walking bob. Honestly, simplest cute effect: bob the whole body up/down alternating and rotate legs a bit. Let me keep legs simple.

Actually, to make it clearly "walking," I'll animate the four legs with phase offsets so they move like running, plus a gentle body bob. Fine.

breathe (idle):
```
h.userData.body.scale.setScalar? 
```
Let me do: body.scale.x/z slight pulse, and eyes blink occasionally.

Blink: every so often scale eyes Z to small then back. I'll implement simple: blinkTimer; when <0 blink.

Let me include blink for cuteness.

nibble (eating): move head up/down small oscillation.

OK let me just write it. I'll keep functions inline in the module.

Let me make sure to add hamster to scene and also ground reference for y position (floor y). Floor top at y=0.5 (tray top). Hamsters sit on floor. Hamster body radius ~0.45, so body center y ~0.5+0.45=0.95. Let me set tray top at y=0 and build above. Simpler: floor plane at y=0, hamsters y from ~0.5. Let me define ground at y=0, tray walls rise from there.

Let me define:
- Tray: a box from y=-0.5 to y=0.5 (thickness), top face at y=0.5? Let me make tray top at y=0. Hamster feet at y~0.5. Body center y ~ 0.5+0.5=1.0.

Hmm let me just set ground plane at y=0 and put hamsters with body center at y≈0.9. Feet bottom at 0.

Let me define floor plane at y=0 (the bedding). Tray walls: a box frame. Let me create tray as:
- Bottom slab: Box(18, 0.4, 14) centered y=-0.2, so top at y=0.
- Walls: 4 thin boxes rising from y=0 to y=1.6, forming enclosure, material semi-transparent (like acrylic cage wall) for x-faces full width, and z-faces.

Actually a real hamster "cage" here is more like a bin/tray with bedding. Let me make:
- Base tray (opaque, light blue/green) top at y=0.
- Clear side walls (transparent) up to y=1.7 so hamsters stay in and we see them.
- Add decorative colored rails/top maybe.

I'll keep it: base tray + transparent walls + a few colorful "toys"/accessories.

Bedding on top of base: planes at y=0.02.

Hamsters y: body center 0.95.

Wheel center: y = 0.9 (so hamster inside bottom touches bedding). radius 1.4 → bottom of wheel at y=-0.5, that's below base. Let me raise wheel: center y=1.3, radius 1.4 → bottom at -0.1, still okay-ish above base 0. Let me set wheel center y=1.4. Hamster inside bottom near y=0.9+? The hamster stands on bedding y~0.5..0.9 and runs. I'll place hamster at wheel bottom: h.position.y = wheelCenter.y - radius + 0.5. With center 1.4, radius1.4 → 0.5+0.5=1.0. Good, hamster center 1.0.

Let me finalize numbers loosely; visual tuning not critical.

Food bowl: at (5,0, -3). Bowl = cylinder (open) + a few pellets. Hamster eats near it.

Let me now also add sky/background color and maybe fog. Use light gray-blue background 0xbfe3ff or warm. Let me do a soft gradient via scene.background color 0xcfe8ff and floor.

Alright writing now. Let me produce the final HTML.

I'll add a title and instruction overlay in CSS.

Let me make sure OrbitControls damping works and limits.

Let me write.

For the hamster construction, I'll attach eyes, cheeks, nose as children of head so they move with head. Ears children of head. Legs children of hamster group (not head) so they stay on body.

Legs: 4 legs. Positions relative to body: front-left (+x, +z), front-right(+x,-z), back-left(-x,+z), back-right(-x,-z). Body elongated along x (length ~1.3*radius). Let me place legs at x ±0.35, z ±0.35, y ~0.15 below body center, as small capsules/boxes.

I'll represent feet as small boxes or spheres. Use SphereGeometry scaled.

Let me code:
```
const legGeo = new THREE.SphereGeometry(0.13, 6, 6);
const footMat = new THREE.MeshStandardMaterial({color: skinColorShade, flatShading:true, roughness:0.9});
legs = [];
positions = [[0.35,0.35],[0.35,-0.35],[-0.35,0.35],[-0.35,-0.35]];
for each: leg = mesh(legGeo); leg.position.set(x, -0.35, z); (relative to body) ; leg.name='leg'; hamster.add(leg); legs.push(leg);
```
Wait leg positioned relative to hamster group which has body at body center. Body center at (0,0.95,0) in world but within group local coords body is at origin (we set body position within group? Let me put body at group origin). Then legs at y=-0.35 relative → y=0.6 in world. Good, feet near floor.

Hmm but I said body center y=0.95 world; if body is at group origin and group.position.y=0.95, then body local 0 → world 0.95. Legs local y=-0.35 → world 0.6. Good.

Eyes on head: head at local (0.5,0.25,0). Eyes at (0.65, 0.35, ±0.15). Nose at (0.85,0.2,0). Cheeks at (0.55,0.15,±0.22) pink. Ears at (0.4,0.55,±0.25) small spheres.

Let me build head as its own child group so blink/nibble rotate head. Actually simpler: keep head as mesh and rotate whole hamster group for facing; head moves with it. For nibble, rotate head mesh locally.

I'll keep head as a mesh added to hamster group at offset. For eating nibble, animate head.position.y oscillation or rotate head.x. Fine.

Let me write it all. I'll be generous with comments.

Let me also ensure the module imports resolve. Use unpkg three 0.160.0. Addons path: https://unpkg.com/three@0.160.0/examples/jsm/

Let me finalize.

Potential issue: flatShading with SphereGeometry low segments gives low-poly look. Good. I'll use segments 8-10 for spheres.

Let me write the CSS overlay.

Also add window resize handler.

Let me produce final answer with the full code inside a code block, plus brief usage note.

Let me write the complete file now, carefully.

I'll double check the raycast for clicking hamsters: iterate hamsters array, check intersection with their meshes. Since hamster is a group, raycaster.intersectObject(hamster, true) returns intersections. Get distance.

On hamster click: set it to 'flee' → pick far random target, jump (add vertical velocity? simple: set body scale squash then restore, and quick move). I'll implement a little hop by temporarily raising position and animating, plus set state wander to a random spot quickly. Keep simple: trigger 'wander' to a random target and a quick scale squash (bootie). Let me do squash: h.userData.squash animation using TWEEN-like manual: t=0..0.4 expand then contract. I'll just do a quick scale pulse in update.

Actually simplest funny reaction: on click, hamster does a little jump — set state to 'jump' where it moves up and down once while spinning, then flees. Let me implement 'startle' state: 
```
u.startleTimer = 0.6;
u.velY = 2.5; // upward
```
Then in update for startle: h.position.y += velY*dt; velY -= 9*dt; if y>0.9 and velY<0 landed -> done. Hmm need ground y. Let me track hamster rest y (0.9). 

This is getting complex. Let me keep the hamster-click reaction simple but fun: it does a quick spin + hops. I'll implement:
```
u.state='startle'; u.startleT=0;
```
update startle:
```
u.startleT+=dt;
const p=u.startleT/0.5;
if(p<1){ h.position.y = 0.9 + Math.sin(p*Math.PI)*0.6; h.rotation.y += dt*12; }
else { u.state='wander'; pickNewTarget(h); }
```
Good enough and funny (hops and spins).

For wheel click: 
```
wheelExcited=true; u.exciteTimer=4;
// also maybe add pellets
```
And wheelSpeed target 8.

Let me also make clicking wheel not also trigger hamster (separate). Since raycaster returns sorted, I'll check wheel first then hamsters.

Let me finalize and write.

I think this is solid. Let me write the final code.

Let me reconsider hamster count: 4 hamsters with varied colors.

Colors: 0xf3c69f (tan), 0xffffff (white), 0xa05f3a (brown), 0xcccccc (gray).

Let me write createHamster to accept base color and produce skin shade for feet (darker/lighter). I'll just use same color for body and lighter feet, or add small variation. I'll compute a slightly darker color for feet.

Let me code foot color = base*0.75.

Now writing.

Let me make sure to set castShadow on hamsters (each mesh) — could be heavy but fine (4 hamsters * ~15 meshes = 60 meshes, ok). Actually enabling castShadow on all is fine.

I'll set renderer.shadowMap.type = PCFSoftShadowMap.

Directional light casts shadows. Set light.shadow.mapSize, camera frustum.

Ambient + hemisphere for fill.

Let me write final.

Also add a subtle ground reflection? No.

Let me write the file.

I'll include a nice heading and instructions.

Final code below.

Let me carefully write animateWalk referencing legs stored in userData.

I realize I should store userData.legs array and userData.body mesh.

Let me define in createHamster:
```
h.userData = {
  state:'pause', timer: Math.random()*3,
  target:new THREE.Vector3(),
  speed: 1.6+Math.random()*0.6,
  legs: legs,
  body: body,
  head: head,
  eyes: [eyeL,eyeR],
  restY: 0.9,
  blinkT: Math.random()*5,
};
```

pickNewTarget(h):
```
h.userData.target.set(rand(-6.5,6.5), 0, rand(-4.5,4.5));
h.state='wander';
```

Edge: ensure target not too close; fine.

Let me write rand(a,b)=a+Math.random()*(b-a).

clamp(v,a,b).

Alright. Also I want hamsters to not overlap too much—skip that complexity.

Let me write the final HTML now. I'll keep comments concise.

For the wheel spokes and discs, let me build:
```
function createWheel() {
  const g = new THREE.Group();
  const R=1.35, tube=0.1;
  const ringMat = new THREE.MeshStandardMaterial({color:0xff5e7b, roughness:0.5, flatShading:true, metalness:0.1});
  const ring = new THREE.Mesh(new THREE.TorusGeometry(R, tube, 6, 24), ringMat);
  g.add(ring);
  // spokes
  const spokeMat = new THREE.MeshStandardMaterial({color:0xffd166, roughness:0.6, flatShading:true});
  for(let i=0;i<8;i++){
    const spoke = new THREE.Mesh(new THREE.BoxGeometry(R*2, tube*0.6, tube*0.6), spokeMat);
    spoke.rotation.x=0; spoke.rotation.z = (i/8)*Math.PI*2;
    // box aligned along x, rotate about z to angle
    g.add(spoke);
  }
  // side discs
  const discMat = new THREE.MeshStandardMaterial({color:0x8ecae6, transparent:true, opacity:0.35, side:DoubleSide, roughness:0.4, flatShading:true});
  const discGeo = new THREE.CircleGeometry(R, 16);
  const d1=new THREE.Mesh(discGeo,discMat); d1.rotation.x=-Math.PI/2; d1.position.z=tube; g.add(d1);
  const d2=new THREE.Mesh(discGeo,discMat); d2.rotation.x=Math.PI/2; d2.position.z=-tube; g.add(d2);
  // axle + stand
  const axMat = new THREE.MeshStandardMaterial({color:0x5c4033, roughness:0.9, flatShading:true});
  const axle=new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.08,R*2+0.4,6),axMat);
  axle.rotation.z=Math.PI/2; axle.position.y=0; g.add(axle);
  // stand posts
  const postGeo=new THREE.BoxGeometry(0.2, R*1.6, 0.2);
  const p1=new THREE.Mesh(postGeo,axMat); p1.position.set(R+0.1, R*0.6, tube); g.add(p1);
  const p2=new THREE.Mesh(postGeo,axMat); p2.position.set(R+0.1, R*0.6, -tube); g.add(p2);
  // base foot
  const base=new THREE.Mesh(new THREE.BoxGeometry(0.4,0.15,R*2+0.6),axMat); base.position.set(R+0.1,-R*0.7,0); g.add(base);
  return g;
}
```
Wheel spins around X. But my stand posts are along z at x=+R and support axle; spinning around X is fine, posts rotate with wheel visually (they're part of g). That's okay—they'll rotate but look like wheel turns. Acceptable.

Position wheel group: g.position.set(-5.2, 1.45, -3.8). Rotation around X is spin.

Hamster on wheel: place at bottom inside: h.position = (wx, wy - R + 0.55, wz + 0.02). Face +Z → rotation.y=-π/2.

Wait wheel center y=1.45, R=1.35 → bottom at 0.1. Hamster center at 0.1+0.55=0.65. Hmm that's low; hamster restY 0.9. Let me set wy higher. Let me set wheel group y = 1.7. bottom=0.35. hamster center=0.35+0.55=0.9. 

Let me set wheel pos y=1.7.

Food bowl:
```
function createBowl(){
  const g=new THREE.Group();
  const bowl=new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.35,0.3,12,1,true), new THREE.MeshStandardMaterial({color:0x4cc9f0, roughness:0.4, flatShading:true, side:DoubleSide}));
  bowl.rotation.x=Math.PI/2; bowl.position.y=0.15; // orient opening along? Cylinder default along Y; rotate x to face... hmm
  ...
}
```
Simplify: bowl = open cylinder along Y (default). Just Cylinder(0.5,0.35,0.3,14). Add pellets as small spheres inside.

Pellets: a few brown spheres at random small positions inside bowl, y~0.15. When hamster eats, remove some over time (hide). I'll store pellets array; during eat, occasionally hide one.

Let me keep pellets count 6.

Now writing final code fully. Let me assemble.

I'll write the whole thing and then a short explanation.

Let me make sure the module script is type="module" and uses importmap.

Writing now.

Actually, for the "run on wheel" placement, the hamster faces +Z inside the wheel. But wheel axis is X, and hamster runs along Z — as wheel spins on X, the surface at bottom moves in ±Z? Surface velocity direction tangential. Whatever, it's cosmetic. Fine.

Let me write.

Let me also handle the case where multiple hamsters want wheel — fine, they queue via timers.

I'll now produce the final answer.

Let me write CSS overlay nicely:
```
body{margin:0; overflow:hidden; font-family: ...; background:#000;}
#info{position:absolute;top:12px;left:50%;transform:translateX(-50%);color:#fff;background:rgba(0,0,0,.4);padding:8px 14px;border-radius:12px;font-size:14px;pointer-events:none;text-align:center;}
```

Title "🐹 Low-Poly Hamster Playground".

Alright final.

Let me also add hemisphere light and an emissive touch for eyes (eyes could be slightly emissive for shine). I'll set eye material emissive 0x220000 small.

Write it.

Double-check: In update, for 'wander' I compute dir from h.position to target; clamp after. Good.

Also initial: set all hamsters to wander with random target at load.

Let me set h.position random at creation within bounds, y=restY.

Now, the whole thing. Let me write.

I'll make sure to call animate() and use clock.getDelta().

Time t accumulates for animations.

Let me write final code.

Let me reconsider the hamster body orientation: head at +x, so hamster faces +x by default. rotation.y rotates about up. Good, atan2(dir.x,dir.z) gives correct yaw to face dir. Check: to face +x (dir=(1,0,0)): atan2(1,0)=π/2. But default faces +x with rotation.y=0. Mismatch! Let me verify atan2(dir.x,dir.z):
- dir=(1,0,0) → atan2(1,0)= +π/2 (1.5708). rotation.y=π/2 rotates +x toward -z? Using earlier rotation about Y formula: vector (1,0,0) rotates to (cosθ,0,-sinθ) for θ=π/2 → (0,0,-1). So the model's +x axis points to (0,0,-1) after rotation. But world dir we want to face is (1,0,0). The model's forward is its local +x. After applying rotation.y=θ to the group, local +x becomes (cosθ,0,-sinθ) in world. We want that to equal dir normalized. So need (cosθ,0,-sinθ)=(dir.x,0,dir.z). → cosθ=dir.x, -sinθ=dir.z → θ=atan2(-dir.z, dir.x)? Because tanθ = sinθ/cosθ = (-dir.z)/(dir.x). So θ = atan2(-dir.z, dir.x). Let me use that: h.rotation.y = Math.atan2(-dir.z, dir.x).

Check dir=(1,0,0): atan2(0,1)=0 → rotation 0 → local +x stays (1,0,0). Correct!
dir=(0,0,1) (face +z): atan2(-1,0)= -π/2 → θ=-π/2: (cos(-90),0,-sin(-90))=(0,0,1). Correct!
dir=(0,0,-1): atan2(1,0)=π/2 → (0,0,-1). Correct.

Great, use atan2(-dir.z, dir.x).

For wheel facing +Z I earlier used -π/2; let me recompute with formula: dir to face (0,0,1): atan2(-1,0)=-π/2. Yes matches. Good, so in runWheel when running, set rotation.y = atan2(-wz_offset?...). Simpler: face +Z → -π/2. Keep.

Alright. Writing final.

Let me also make sure hamster feet spheres don't clip floor badly; fine.

Final code below. I'll keep it organized.

I think it's ready. Let me output.
</think>

# 🐹 Low-Poly Hamster Playground

Here's a complete, self-contained `index.html`. Just save it and open it in any modern browser — no build step, no server needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>🐹 Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; box-sizing: border-box; }
  html, body { height: 100%; overflow: hidden; background: #cfe8ff; }
  body { font-family: system-ui, sans-serif; }
  #info {
    position: fixed; top: 12px; left: 50%; transform: translateX(-50%);
    color: #fff; background: rgba(20,30,50,.45); backdrop-filter: blur(6px);
    padding: 9px 16px; border-radius: 999px; font-size: 14px; font-weight: 600;
    pointer-events: none; text-align: center; user-select: none; z-index: 10;
    box-shadow: 0 6px 20px rgba(0,0,0,.2);
  }
  #info span { color: #ffe27d; }
</style>
<style id="importmap"></style>
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>
  <div id="info">🐹 <span>Low-Poly Hamster Playground</span> — drag to orbit · scroll to zoom · <span>click a hamster or the wheel!</span></div>

  <script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ------------------------------------------------------------------ */
/*  Renderer / Scene / Camera                                         */
/* ------------------------------------------------------------------ */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xcfe8ff);
scene.fog = new THREE.Fog(0xcfe8ff, 20, 45);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(9, 8, 11);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 6;
controls.maxDistance = 28;
controls.maxPolarAngle = Math.PI / 2.05; // keep above the floor
controls.target.set(0, 1, 0);

/* ------------------------------------------------------------------ */
/*  Lighting                                                          */
/* ------------------------------------------------------------------ */
scene.add(new THREE.HemisphereLight(0xbfe3ff, 0x8faf7a, 0.75));
const ambient = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xfff4e0, 1.1);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 40;
sun.shadow.camera.left = -14;
sun.shadow.camera.right = 14;
sun.shadow.camera.top = 14;
sun.shadow.camera.bottom = -14;
sun.shadow.bias = -0.0005;
scene.add(sun);

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */
const rand  = (a, b) => a + Math.random() * (b - a);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const mat   = (color, opts = {}) => new THREE.MeshStandardMaterial({
  color, roughness: 0.9, metalness: 0.0, flatShading: true, ...opts
});

/* ------------------------------------------------------------------ */
/*  The Cage: tray + transparent walls + bedding                      */
/* ------------------------------------------------------------------ */
const cage = new THREE.Group();
scene.add(cage);

// Base tray
const tray = new THREE.Mesh(
  new THREE.BoxGeometry(18, 0.5, 14),
  mat(0x6ec6ff)
);
tray.position.y = -0.25;
tray.receiveShadow = true;
cage.add(tray);

// Bedding layer (warm sand color)
const bedding = new THREE.Mesh(
  new THREE.BoxGeometry(17.6, 0.12, 13.6),
  mat(0xf4d1a0)
);
bedding.position.y = 0.02;
bedding.receiveShadow = true;
cage.add(bedding);

// Scattered colorful bedding flakes (instanced for speed)
const flakesGeo = new THREE.BoxGeometry(0.28, 0.08, 0.28);
const flakesMat = new THREE.MeshStandardMaterial({ flatShading: true, roughness: 1 });
const FLAKE_COUNT = 260;
const flakes = new THREE.InstancedMesh(flakesGeo, flakesMat, FLAKE_COUNT);
const dummy = new THREE.Object3D();
const flakeColors = [0xffd6a5, 0xfdab8a, 0xe5c08b, 0xbfee7d, 0xffe0a0];
for (let i = 0; i < FLAKE_COUNT; i++) {
  dummy.position.set(rand(-8.3, 8.3), rand(0.06, 0.22), rand(-6.3, 6.3));
  dummy.rotation.y = rand(0, Math.PI);
  dummy.updateMatrix();
  flakes.setMatrixAt(i, dummy.matrix);
  flakes.setColorAt(i, new THREE.Color(flakeColors[i % flakeColors.length]));
}
flakes.castShadow = false;
flakes.receiveShadow = true;
cage.add(flakes);

// Semi-transparent acrylic side walls
const wallMat = mat(0xbfe3ff, { transparent: true, opacity: 0.35, side: THREE.DoubleSide });
const wallH = 1.8;
const walls = [
  { s: [18, wallH, 0.3], p: [0, wallH / 2, -7] },
  { s: [18, wallH, 0.3], p: [0, wallH / 2,  7] },
  { s: [0.3, wallH, 14], p: [-9, wallH / 2, 0] },
  { s: [0.3, wallH, 14], p: [ 9, wallH / 2, 0] },
];
walls.forEach(w => {
  const m = new THREE.Mesh(new THREE.BoxGeometry(...w.s), wallMat);
  m.position.set(...w.p);
  cage.add(m);
});

// Little colorful top-rail accent on the front wall
const rail = new THREE.Mesh(new THREE.BoxGeometry(18, 0.25, 0.4), mat(0xff6b6b));
rail.position.set(0, wallH + 0.05, 7);
cage.add(rail);

/* ------------------------------------------------------------------ */
/*  Interactive Object #1: Exercise Wheel                             */
/* ------------------------------------------------------------------ */
const WHEEL = { group: null, spin: 0.4, excited: 0 };
function buildWheel() {
  const g = new THREE.Group();
  const R = 1.35, tube = 0.1;
  const ringMat = mat(0xff5e7b, { roughness: 0.4 });
  g.add(new THREE.Mesh(new THREE.TorusGeometry(R, tube, 6, 24), ringMat));

  const spokeMat = mat(0xffd166, { roughness: 0.5 });
  for (let i = 0; i < 8; i++) {
    const spoke = new THREE.Mesh(new THREE.BoxGeometry(R * 2, tube * 0.6, tube * 0.6), spokeMat);
    spoke.rotation.z = (i / 8) * Math.PI * 2;
    g.add(spoke);
  }
  const discMat = mat(0x8ecae6, { transparent: true, opacity: 0.3, side: THREE.DoubleSide });
  const discGeo = new THREE.CircleGeometry(R, 16);
  const d1 = new THREE.Mesh(discGeo, discMat); d1.rotation.x = -Math.PI / 2; d1.position.z = tube; g.add(d1);
  const d2 = new THREE.Mesh(discGeo, discMat); d2.rotation.x = Math.PI / 2;   d2.position.z = -tube; g.add(d2);

  const woodMat = mat(0x5c4033, { roughness: 1 });
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, R * 2 + 0.5, 6), woodMat);
  axle.rotation.z = Math.PI / 2; g.add(axle);
  const postGeo = new THREE.BoxGeometry(0.25, R * 1.7, 0.25);
  const p1 = new THREE.Mesh(postGeo, woodMat); p1.position.set(R + 0.1, R * 0.55, tube); g.add(p1);
  const p2 = new THREE.Mesh(postGeo, woodMat); p2.position.set(R + 0.1, R * 0.55, -tube); g.add(p2);
  const foot = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.15, R * 2 + 0.7), woodMat);
  foot.position.set(R + 0.1, -R * 0.7, 0); g.add(foot);

  g.position.set(-5.2, 1.7, -3.8);
  WHEEL.group = g;
  return g;
}
scene.add(buildWheel());
const WHEEL_POS = new THREE.Vector3(-5.2, 1.7, -3.8);

/* ------------------------------------------------------------------ */
/*  Interactive Object #2: Food Bowl + pellets                        */
/* ------------------------------------------------------------------ */
const BOWL = { group: null, pellets: [] };
function buildBowl() {
  const g = new THREE.Group();
  const bowl = new THREE.Mesh(
    new THREE.CylinderGeometry(0.55, 0.4, 0.32, 14),
    mat(0x4cc9f0, { roughness: 0.4 })
  );
  bowl.castShadow = true; bowl.position.y = 0.16; g.add(bowl);
  const rim = new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.06, 8, 16), mat(0x1290b8));
  rim.rotation.x = Math.PI / 2; rim.position.y = 0.3; g.add(rim);

  const pelGeo = new THREE.IcosahedronGeometry(0.09, 0);
  const pelMat = mat(0x8a5a2b, { roughness: 1 });
  for (let i = 0; i < 7; i++) {
    const p = new THREE.Mesh(pelGeo, pelMat.clone());
    p.position.set(rand(-0.35, 0.35), rand(0.24, 0.34), rand(-0.35, 0.35));
    p.userData.eaten = false;
    g.add(p);
    BOWL.pellets.push(p);
  }
  g.position.set(5.2, 0, -3.2);
  BOWL.group = g;
  return g;
}
scene.add(buildBowl());
const FOOD_POS = new THREE.Vector3(5.2, 0, -3.2);

/* ------------------------------------------------------------------ */
/*  The Hamsters                                                      */
/* ------------------------------------------------------------------ */
const hamsters = [];
const HAMSTER_BOUNDS = { x: 7.2, z: 4.8 };

function createHamster(baseColor) {
  const h = new THREE.Group();

  const bodyMat = mat(baseColor);
  const footCol = new THREE.Color(baseColor).multiplyScalar(0.72);
  const footMat = mat(footCol);

  // Body (elongated blob)
  const bodyGeo = new THREE.SphereGeometry(0.5, 12, 10);
  bodyGeo.scale(1, 0.92, 1.35);
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.castShadow = true;
  h.add(body);

  // Head
  const headGeo = new THREE.SphereGeometry(0.36, 12, 10);
  headGeo.scale(1, 0.95, 1.0);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.position.set(0.55, 0.28, 0);
  head.castShadow = true;
  h.add(head);

  // Ears
  const earGeo = new THREE.SphereGeometry(0.16, 8, 8);
  const earMat = mat(new THREE.Color(baseColor).multiplyScalar(1.15));
  const earL = new THREE.Mesh(earGeo, earMat); earL.position.set(0.42, 0.55, 0.22); earL.scale.setScalar(0.9); h.add(earL);
  const earR = new THREE.Mesh(earGeo, earMat); earR.position.set(0.42, 0.55, -0.22); earR.scale.setScalar(0.9); h.add(earR);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.085, 8, 8);
  const eyeMat = mat(0x141414, { roughness: 0.2, emissive: 0x221100, emissiveIntensity: 0.2 });
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat); eyeL.position.set(0.72, 0.34, 0.15); h.add(eyeL);
  const eyeR = new THREE.Mesh(eyeGeo, eyeMat); eyeR.position.set(0.72, 0.34, -0.15); h.add(eyeR);

  // Pink cheeks + nose
  const cheekGeo = new THREE.SphereGeometry(0.12, 8, 8);
  const cheekMat = mat(0xff9aa2, { roughness: 0.9 });
  const ckL = new THREE.Mesh(cheekGeo, cheekMat); ckL.position.set(0.66, 0.16, 0.24); h.add(ckL);
  const ckR = new THREE.Mesh(cheekGeo, cheekMat); ckR.position.set(0.66, 0.16, -0.24); h.add(ckR);
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.06, 8, 8), mat(0xd64d5d));
  nose.position.set(0.9, 0.24, 0); h.add(nose);

  // Four feet
  const legGeo = new THREE.SphereGeometry(0.13, 8, 8);
  const feet = [];
  const spots = [[0.38, 0.28], [0.38, -0.28], [-0.36, 0.28], [-0.36, -0.28]];
  spots.forEach(([x, z]) => {
    const foot = new THREE.Mesh(legGeo, footMat);
    foot.position.set(x, -0.38, z);
    foot.scale.set(1, 0.7, 1.2);
    foot.castShadow = true;
    h.add(foot);
    feet.push(foot);
  });

  // Tiny tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 8), footMat);
  tail.position.set(-0.62, 0.05, 0); h.add(tail);

  h.position.set(rand(-2, 2), 0.9, rand(-2, 2));

  h.userData = {
    state: 'wander',
    timer: rand(0, 3),
    target: new THREE.Vector3(rand(-6, 6), 0, rand(-4, 4)),
    speed: rand(1.5, 2.2),
    legs: feet,
    body, head, eyes: [eyeL, eyeR],
    restY: 0.9,
    blinkT: rand(2, 6),
    hopVel: 0,
    hopping: false,
  };
  return h;
}

const palette = [0xf3c69f, 0xfff4e0, 0xa05f3a, 0xcccccc];
palette.forEach(c => {
  const h = createHamster(c);
  scene.add(h);
  hamsters.push(h);
});

/* ------------------------------------------------------------------ */
/*  Behavior updates                                                  */
/* ------------------------------------------------------------------ */
function pickNewTarget(h) {
  h.userData.target.set(rand(-HAMSTER_BOUNDS.x, HAMSTER_BOUNDS.x), 0, rand(-HAMSTER_BOUNDS.z, HAMSTER_BOUNDS.z));
}

function faceDir(h, dir) {
  h.rotation.y = Math.atan2(-dir.z, dir.x);
}

function animateWalk(h, t, mult = 1) {
  const legs = h.userData.legs;
  const freq = 4 + 4 * mult;
  legs.forEach((leg, i) => {
    leg.rotation.x = Math.sin(t * freq + (i % 2 ? Math.PI : 0)) * 0.55 * mult;
  });
  h.userData.body.position.y = 0.0 + Math.abs(Math.sin(t * freq * 0.5)) * 0.05;
}

function breathe(h, t) {
  const s = 1 + Math.sin(t * 2) * 0.02;
  h.userData.body.scale.set(1, s, 1);
}

function nibble(h, t) {
  h.userData.head.position.y = 0.28 + Math.abs(Math.sin(t * 10)) * 0.05;
}

function updateHamster(h, dt, t) {
  const u = h.userData;

  // Blink
  u.blinkT -= dt;
  if (u.blinkT <= 0) {
    u.blinkT = rand(2, 6);
    const [eL, eR] = u.eyes;
    eL.scale.z = 0.1; eR.scale.z = 0.1;
    setTimeout(() => { eL.scale.z = 1; eR.scale.z = 1; }, 120);
  }

  switch (u.state) {
    case 'wander': {
      const dir = new THREE.Vector3().subVectors(u.target, h.position); dir.y = 0;
      const dist = dir.length();
      if (dist > 0.15) {
        dir.normalize();
        h.position.x += dir.x * u.speed * dt;
        h.position.z += dir.z * u.speed * dt;
        faceDir(h, dir);
        animateWalk(h, t);
      } else {
        u.state = 'pause';
        u.timer = rand(1.5, 4.5);
      }
      break;
    }
    case 'pause': {
      u.timer -= dt;
      breathe(h, t);
      if (u.timer <= 0) {
        const roll = Math.random();
        if (roll < 0.28) { u.state = 'runWheel'; u.timer = rand(4, 7); }
        else if (roll < 0.42) { u.state = 'eat'; u.timer = rand(3, 5); }
        else { u.state = 'wander'; pickNewTarget(h); }
      }
      break;
    }
    case 'runWheel': {
      const dir = new THREE.Vector3().subVectors(WHEEL_POS, h.position); dir.y = 0;
      const dist = dir.length();
      if (dist > 0.5) {
        dir.normalize();
        h.position.x += dir.x * u.speed * 1.7 * dt;
        h.position.z += dir.z * u.speed * 1.7 * dt;
        faceDir(h, dir);
        animateWalk(h, t, 2.0);
      } else {
        faceDir(h, new THREE.Vector3(0, 0, 1));
        animateWalk(h, t, 3.6);
        WHEEL.spin += (8 - WHEEL.spin) * dt * 2;
        u.timer -= dt;
        if (u.timer <= 0) { u.state = 'pause'; u.timer = rand(2, 5); }
      }
      break;
    }
    case 'eat': {
      const dir = new THREE.Vector3().subVectors(FOOD_POS, h.position); dir.y = 0;
      const dist = dir.length();
      if (dist > 0.5) {
        dir.normalize();
        h.position.x += dir.x * u.speed * dt;
        h.position.z += dir.z * u.speed * dt;
        faceDir(h, dir);
        animateWalk(h, t, 0.6);
      } else {
        faceDir(h, new THREE.Vector3(0, 0, -1));
        nibble(h, t);
        // eat a pellet
        if (!u.eatTick) u.eatTick = 0;
        u.eatTick += dt;
        if (u.eatTick > 0.6) {
          u.eatTick = 0;
          const p = BOWL.pellets.find(p => !p.userData.eaten);
          if (p) { p.userData.eaten = true; p.visible = false; }
        }
        u.timer -= dt;
        if (u.timer <= 0) { u.state = 'pause'; u.timer = rand(2, 5); }
      }
      break;
    }
    case 'startle': {
      u.startleT += dt;
      const p = clamp(u.startleT / 0.55, 0, 1);
      if (p < 1) {
        h.position.y = u.restY + Math.sin(p * Math.PI) * 0.7;
        h.rotation.y += dt * 14;
      } else {
        h.position.y = u.restY;
        u.state = 'wander';
        u.target.set(rand(-6, 6), 0, rand(-4, 4));
      }
      break;
    }
  }

  // Keep inside the cage
  h.position.x = clamp(h.position.x, -HAMSTER_BOUNDS.x, HAMSTER_BOUNDS.x);
  h.position.z = clamp(h.position.z, -HAMSTER_BOUNDS.z, HAMSTER_BOUNDS.z);
}

/* ------------------------------------------------------------------ */
/*  Click interaction (raycasting)                                   */
/* ------------------------------------------------------------------ */
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let pointerDown = new THREE.Vector2();

window.addEventListener('pointerdown', (e) => {
  pointerDown.set(e.clientX, e.clientY);
});
window.addEventListener('pointerup', (e) => {
  // only treat as click if mouse didn't drag much
  if (Math.hypot(e.clientX - pointerDown.x, e.clientY - pointerDown.y) > 5) return;
  pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
  pointer.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);

  // 1) Wheel?
  const wheelHits = raycaster.intersectObject(WHEEL.group, true);
  if (wheelHits.length) {
    WHEEL.excited = 5;               // spin up!
    // refill the food bowl for fun
    BOWL.pellets.forEach(p => { p.userData.eaten = false; p.visible = true; });
    return;
  }
  // 2) Any hamster?
  const hamHits = raycaster.intersectObjects(hamsters, true);
  if (hamHits.length) {
    const hit = hamHits[0].object;
    let obj = hit;
    while (obj.parent && !obj.userData.state) obj = obj.parent;
    if (obj.userData && obj.userData.state !== undefined) {
      obj.userData.state = 'startle';
      obj.userData.startleT = 0;
    }
  }
});

/* ------------------------------------------------------------------ */
/*  Main loop                                                         */
/* ------------------------------------------------------------------ */
const clock = new THREE.Clock();
let elapsed = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  elapsed += dt;

  hamsters.forEach(h => updateHamster(h, dt, elapsed));

  // Wheel physics-ish spin
  const target = WHEEL.excited > 0 ? 8 : 0.5;
  WHEEL.spin += (target - WHEEL.spin) * dt * 1.5;
  WHEEL.group.rotation.x += WHEEL.spin * dt;
  if (WHEEL.excited > 0) WHEEL.excited -= dt;

  controls.update();
  renderer.render(scene, camera);
}
animate();

/* ------------------------------------------------------------------ */
/*  Resize                                                            */
/* ------------------------------------------------------------------ */
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
  </script>
</body>
</html>
```

## What's inside

- **Cage & tray** — a shallow blue tray with a warm bedding layer and ~260 scattered colorful flakes (using `InstancedMesh` for performance), plus semi-transparent acrylic walls and a pink accent rail.
- **4 low-poly hamsters** — built from primitive spheres with bodies, heads, ears, glossy eyes, pink cheeks, a nose, four animated feet, and a little tail. Each has a distinct color.
- **Autonomous behavior** — a small state machine per hamster: `wander → pause → (sometimes) run-on-wheel / eat-at-bowl`, plus idle breathing and random blinking.
- **Interactive wheel** — spins continuously; hamsters walk over and "run" on it (spinning it fast). **Click it** to spin it up and refill the food bowl.
- **Food bowl** — hamsters wander over to nibble pellets (which disappear as they're eaten).
- **Click any hamster** → it does a funny hop-and-spin "startle" and scurries off.
- **OrbitControls** — drag to rotate, scroll to zoom, with the camera locked above the floor so you never get stuck under the tray.

Just open the file in Chrome/Firefox/Safari/Edge and it runs instantly. Everything (HTML, CSS, JS, and Three.js via CDN import map) lives in the single file.