The user wants me to create a complete interactive 3D aquarium using Three.js based on the detailed specification they provided. Let me build this as a single HTML file with all the required features.

Let me plan out the implementation:

1. **HTML structure** with UI panels
2. **CSS styling** with glass effects, gradients, etc.
3. **JavaScript** with Three.js for:
   - Aquarium container (glass with transmission)
   - Sandy bottom with procedural bumps
   - Decorative rocks (8 deformed dodecahedrons)
   - Seaweed (12 bushes via TubeGeometry with CatmullRomCurve3)
   - Bubble system (30 bubbles)
   - Fish system (15 fish with detailed models)
   - AI behavior (avoidance, wall reflection, wandering, food chasing, growth)
   - Feeding system (click to create food, physics, detection)
   - Lighting (ambient, directional with shadows, 2 point lights)
   - Camera controls (OrbitControls)
   - UI (info panel, stats, buttons)

Let me write this comprehensive code. I need to be careful about the Three.js r128 API since that's what's specified. Note that in r128, MeshPhysicalMaterial with transmission exists but the setup is different from newer versions. Let me use it appropriately.

Actually, for r128, transmission material might have issues. Let me use a reasonable approach. In r128, MeshPhysicalMaterial has transmission property but it requires `useLegacyTransmissions` sometimes. Let me just try with transmission and opacity settings.

Let me build this step by step.

For the fish model:
- Elongated body (scaled sphere)
- Realistic eyes with pupils
- Animatable tail (rotation on Z axis)
- Several fins (top, side)

For colors: orange, blue, yellow-red, purple, red, green, pink, gold

Let me write the complete code now.

I'll structure the fish creation carefully. Each fish is a THREE.Group containing:
- Body (sphere scaled)
- Tail (a cone or flat shape)
- Left and right fins
- Eyes (white spheres with dark pupils)

The fish array stores mesh, tail, fins, velocity, speed, tailSpeed, phase, targetFood, avoidanceRadius.

For behavior:
- Avoidance: separate from other fish
- Wall reflection: bounce off boundaries
- Wandering: periodic direction change
- Food chasing: move toward food
- Growth: increase size after eating

For feeding:
- Click creates food
- Food falls with gravity
- Fish detect food within radius 15
- When eaten: remove food + grow fish 5%
- Remove food at bottom

Let me write it all out. This is going to be a large file.

Let me be thoughtful about the physics and make it smooth.

For OrbitControls in r128, the script is loaded from the examples CDN. The usage is standard.

Let me code this up now.

I'll make the aquarium dimensions 36x24x20 (width x height x depth).

Let me set up the scene:
- Camera at reasonable distance
- Renderer with shadows
- Fog

Let me write everything.

For the glass tank, I'll use a box geometry with MeshPhysicalMaterial with transmission. Actually creating a proper glass tank with edges is tricky. Let me create a transparent box for the water/tank and add wireframe edges.

Let me think about the frame/wireframe - I'll use EdgesGeometry to show the edges of the box.

For the sandy bottom, a plane with vertex displacement for bumps, receiving shadows.

For rocks, 8 deformed dodecahedrons at random positions.

For seaweed, 12 bushes created with TubeGeometry and CatmullRomCurve3, with swaying animation.

For bubbles, 30 transparent spheres moving up with sinusoidal motion.

Let me write the full implementation now.

I need to be careful with the r128 OrbitControls - it's attached to THREE.OrbitControls.

Let me write clean, working code.

Here's my plan for the fish movement AI:

```javascript
function updateFish(fish, delta) {
  const mesh = fish.mesh;
  const vel = fish.velocity;
  
  // Find nearest food
  let nearestFood = null;
  let nearestDist = 15; // detection radius
  for (const food of foods) {
    const dist = mesh.position.distanceTo(food.mesh.position);
    if (dist < nearestDist) {
      nearestDist = dist;
      nearestFood = food;
    }
  }
  
  if (nearestFood) {
    fish.targetFood = nearestFood;
    // Move toward food
    const dir = new THREE.Vector3().subVectors(nearestFood.mesh.position, mesh.position).normalize();
    vel.add(dir.multiplyScalar(fish.speed * delta * 2));
  } else {
    // Random wandering
    fish.phase += delta;
    // slight random steering
  }
  
  // Avoidance from other fish
  for (const other of fishArray) {
    if (other === fish) continue;
    const dist = mesh.position.distanceTo(other.mesh.position);
    if (dist < fish.avoidanceRadius) {
      const push = new THREE.Vector3().subVectors(mesh.position, other.mesh.position).normalize();
      vel.add(push.multiplyScalar((fish.avoidanceRadius - dist) / fish.avoidanceRadius * fish.speed * delta));
    }
  }
  
  // Wall reflection
  const margin = 2;
  const bounds = { x: 16, y: 10, z: 8 };
  if (mesh.position.x > bounds.x - margin) vel.x -= delta * fish.speed;
  if (mesh.position.x < -bounds.x + margin) vel.x += delta * fish.speed;
  // etc.
  
  // Apply velocity
  mesh.position.add(vel.clone().multiplyScalar(delta));
  
  // Clamp speed
  if (vel.length() > fish.speed) vel.normalize().multiplyScalar(fish.speed);
  
  // Face direction of movement
  if (vel.length() > 0.001) {
    const target = mesh.position.clone().add(vel);
    mesh.lookAt(target);
  }
  
  // Animate tail and fins
  fish.tail.rotation.z = Math.sin(time * fish.tailSpeed + fish.phase) * 0.4;
  ...
}
```

This is a good structure. Let me refine and write the complete file.

Let me handle the food physics:
```javascript
food = {
  mesh: mesh,
  velocity: new THREE.Vector3(0, 0, 0),
  active: true
};
```

Gravity pulls it down, when it reaches bottom it stays or is removed.

For detecting eating, when a fish is close to food (within some eat radius), remove food and grow fish.

Let me write the complete HTML file now.

I'll make sure to include:
- Gradient background (using a canvas texture or CSS)
- Fog
- Glass UI panels

For the gradient background, I can use a large sphere/cube with a gradient texture, or just set scene.background to a color and rely on fog. The spec says "Background: градиент от темно-синего к синему". Let me create a gradient using a canvas texture on a large sphere or use CSS background behind everything. Actually, simplest is to set scene.background with a color and add fog. But for a nice gradient, I could create a gradient sky. Let me use a canvas texture on an inverted sphere or just set the clear color.

Actually, let me create a gradient background using a large plane/sphere with a shader or canvas texture. To keep it simple and robust, I'll set scene.background to a dark blue and add FogExp2 which will blend distant objects into the background color. That gives a nice underwater feel.

But the spec explicitly wants a gradient. Let me create a gradient background texture and apply it to the scene background via a large sphere. Or I can use CSS for the page background and make the canvas transparent-ish. Hmm, but then fog won't match.

Let me do this: create a canvas with vertical gradient (dark blue to blue), create a texture from it, and use it as scene.background. This works well.

Actually, for a cube background with gradient, it's easier to just use a big sphere with the gradient texture mapped. Let me do that.

Let me write the code.

For transmission material in r128 - there might be issues. Let me test mentally. In r128, MeshPhysicalMaterial supports transmission but you may need `scene.background` set and it renders through. Actually transmission in older versions used a workaround. Let me just set transmission: 0.95, opacity: 1, transparent: true, and see. If it doesn't look great, the wireframe edges will still show the tank.

Actually, to be safe and ensure the tank is visible, I'll make the tank glass material semi-transparent with high transparency, and definitely add edge lines. Let me use MeshPhysicalMaterial with transmission but also keep it working.

Hmm, one concern: in r128, transmission rendering requires the environment map sometimes. Let me add an environment map or just accept a simpler glass look. To be safe, I'll use a material that looks glassy: transparent, opacity ~0.15-0.3, roughness low, plus edge lines. This guarantees visibility regardless of transmission quirks.

Actually the spec specifically asks for transmission: 0.95. Let me include it but make it robust. I'll set:
```javascript
const glassMaterial = new THREE.MeshPhysicalMaterial({
  color: 0xaaddee,
  transmission: 0.95,
  opacity: 1,
  transparent: true,
  roughness: 0.1,
  metalness: 0,
  side: THREE.DoubleSide
});
```

And add edge lines. This should work reasonably.

Let me now write the entire thing.

I want to make sure the code is complete and functional. Let me write it carefully.

For seaweed sway animation, I'll store the seaweed references and rotate them slightly over time.

Let me finalize and write.

One more consideration: the fish need to be oriented so their "forward" is along +X or -X. When I create the fish group, I'll build it so the fish faces +X (nose pointing +X). Then when I do mesh.lookAt(direction), it orients correctly. The tail should oscillate around the back (-X side).

Let me build the fish:
- Body: sphere scaled to (length, height, width) ~ (0.6, 0.3, 0.25), centered at origin, nose at +X
- Tail: attached at -X, a triangle/cone shape pointing back
- Fins: small shapes on top and sides
- Eyes: two small spheres at +X front, top

Actually for the tail rotation around Z axis to look like swimming, the tail should be at the back and rotate. Let me put tail at -X and rotate its local Z.

Let me just build it and it'll look fine.

Let me write the complete code now. I'll be thorough.

I'll structure JS:
1. Setup (renderer, scene, camera, controls)
2. Lighting
3. Aquarium (glass box, edges, sand, rocks, seaweed)
4. Bubbles
5. Fish creation
6. Food system
7. Animation loop
8. Event handlers
9. UI button handlers

Let me write it all.

For FPS counter, I'll track frames and time.

Let me write the CSS for glass panels with backdrop-filter blur, gradient buttons, etc.

OK here's the full code:

I need to make sure the OrbitControls path works. The CDN is:
https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js

In r128, this global script attaches THREE.OrbitControls. Good.

Let me write everything now. I'll produce a single self-contained HTML file.

Let me be careful about the fish facing. When using lookAt, the +Z axis of the object points toward the target in Three.js? No. In Three.js, an object's forward is typically +Z? Actually no - Three.js uses a right-handed coordinate system where the default object looks toward +Z by default when... hmm. Actually the camera looks down -Z by default. For a generic mesh, lookAt makes the object's +Z axis point toward the target. Wait, let me recall.

THREE.Object3D.lookAt() orthonormalizes and sets the orientation such that the object's local +Z axis points toward the target point. Yes, lookAt makes +Z point to target.

So if I build the fish with nose pointing +Z, then lookAt works naturally. But I built it assuming +X. Let me either build nose at +Z or adjust. 

Simplest: build the fish facing +Z (nose at +Z), then lookAt works directly. Let me do that. So:
- Body sphere scaled (0.25, 0.25, 0.6) - elongated along Z
- Tail at -Z
- Eyes at +Z

Actually, it doesn't matter much as long as it's consistent. Let me use +Z for forward to make lookAt natural.

Hmm, but then the tail rotation on Z axis... if forward is Z and tail is at -Z, rotating tail around Z axis would swing it sideways which is correct for a tail wiggle. Good.

Wait, but a tail wiggling should swing left-right, meaning rotation around the forward axis (Z) would rotate it in the XY plane. That's actually a sideways wiggle which looks like a fish tail. Good.

Actually, real fish tails swing left-right meaning the tail moves in the X direction (if swimming in Z), so rotation around Z axis. Yes that's right.

Let me build with forward = +Z.

Body: new THREE.SphereGeometry(0.5, 16, 12) scaled to (0.4, 0.4, 0.9) roughly. Nose at +Z.

Tail: I'll make it a cone or a flat shape at -Z. Let me use a ConeGeometry or a custom shape. A flat tail fin looks better. Let me make two triangular planes or use a cone pointing backward. Actually a common approach: a cone with apex at -Z base at origin. Let me use ConeGeometry(0.25, 0.5, 8) and position/rotate so apex points -Z. ConeGeometry points along +Y by default. I'll rotate it -90° around X so it points along Z, then move to -Z.

Hmm, let me just make the tail a flattened shape. I'll create a group for the tail so rotation works locally.

Let me simplify: tail = a small cone, parented to the fish group at position (0,0,-0.5), rotated to point back. Its rotation.z animates the wiggle.

For fins: top fin and side fins. Small cones or planes.

Eyes: two small white spheres at (±0.15, 0.15, 0.4) with dark pupil spheres slightly in front.

Let me write it.

Actually, to keep tail wiggle looking good, let me parent tail to the fish mesh but offset, and rotate around Z. Since the tail is at -Z and we rotate around Z (the axis pointing forward-back), the tail swings in XY plane. Good.

Let me now also animate side fins (left/right) - rotate around X or Z.

OK let me just write it all and make it look decent.

Let me write the final code.

I'll add comments in Russian since the spec is in Russian, but that's optional. I'll add some comments.

Let me write the complete HTML file now. This will be long.

For the sand bottom procedural bumps: create a PlaneGeometry with many segments, displace vertices with random noise, rotate to horizontal (rotateX -90°), position at bottom.

Bottom y = -10 (since tank height is 20, center at 0, so bottom at -10). Tank: x from -18 to 18, y from -10 to 10, z from -10 to 10. Wait dimensions are 36x24x20. So width=36 (x), height=24 (y), depth=20 (z). Center at origin: x ±18, y ±12, z ±10.

Let me set bounds accordingly:
- x: -18 to 18
- y: -12 to 12
- z: -10 to 10

Sand at y = -12.

Fish movement bounds: keep fish within slightly inside the tank.

Let me write.

For point lights underwater effect (blue/cyan), place two inside the tank.

Let me finalize the lighting:
- AmbientLight 0x404040 intensity 0.4
- DirectionalLight with shadows, shadowMapSize 2048, PCFSoftShadowMap
- 2 PointLights cyan/blue

DirectionalLight castShadow = true, shadow.camera.far large, shadow.mapSize.set(2048,2048).

Renderer.shadowMap.type = THREE.PCFSoftShadowMap.

Toggle light button changes directionalLight.intensity.

Let me write the complete file.

I'll now compose the full HTML.

For FPS: count frames, every second update display.

Let me write it.

Regarding performance with 15+ fish and neighbor checks, O(n²) is fine for small n.

Let me write the code carefully and completely.

Let me define helper functions:
- createFish(): creates a fish group and adds to scene + array
- createBubble()
- createRock()
- createSeaweed()
- dropFood(x, z)

Colors array for fish.

Let me write.

Actually, I realize I should double check the transmission in r128. In three r128, MeshPhysicalMaterial.transmission exists (added around r125 or so). It should work but the rendering quality depends on environment. Without an env map, transmission might look flat but still transparent-ish. To be safe I'll set both transmission and a low opacity fallback. Actually if I set transmission 0.95 AND opacity 1 with transparent false, it might not render transparently without env. Let me set transparent: true and opacity: 0.3 as a base so it's at least see-through even if transmission doesn't fully work. Hmm, but transmission + opacity interaction...

Let me just set:
```
new THREE.MeshPhysicalMaterial({
  color: 0xbfe3ff,
  metalness: 0.0,
  roughness: 0.05,
  transmission: 0.95,
  transparent: true,
  opacity: 1.0,
  thickness: 1.0,
  side: THREE.DoubleSide
})
```

And rely on edge lines for the tank outline. This is the best I can do in r128. It generally works in modern browsers.

Alright, writing now.

Let me also add a subtle env or use scene.background to help.

Let me write the complete file.

I'll make the seaweed sway by storing initial geometry and rotating the group slightly, or by animating per-strand. Simplest: each seaweed is a group of tubes; I rotate the whole group a bit and also could bend. Let me just sway the group rotation on X and Z with small amplitude, varying per strand, and animate continuously. The spec says "Покачивание анимацией (вращение по X и Z)". So rotate group on X and Z. Good.

Let me write.

For seaweed creation with TubeGeometry + CatmullRomCurve3: create a curve from bottom going up with some curve, then TubeGeometry along it, maybe 2-3 strands per bush. Color green variations.

Let me write the code now, finally.

I'll write a comprehensive, working file.

Let me also handle window resize.

Final code below.

Let me make sure to reference the fish correctly in update. I'll iterate fishArray.

For food eating radius, say 1.0 unit (fish reaches food). Detection radius for seeking is 15.

Let me set eat distance ~ fish.size * 1.5 or just 0.8.

Growth: multiply scale by 1.05, and store current size factor.

Let me track fish.baseScale or just scale the mesh. Actually growth should affect the whole group. I'll store fish.scaleFactor and set mesh.scale accordingly, or just multiply mesh.scale each growth. Simpler: keep a size variable and set mesh.scale.setScalar(size). Body geometry created once at base size 1.0, then scaled.

Let me store fish.size starting between 0.6 and 1.2, set mesh.scale.setScalar(size). On eat, size *= 1.05.

Velocity/fins are children, scaling the group scales them too. Good.

Now avoidanceRadius scales with size maybe. Keep simple.

Let me write.

Let me also add the ability for fish to occasionally wander - add a slow random drift.

OK, writing final code. I'll aim for correctness and completeness.

Let me draft the animation loop:

```javascript
let time = 0;
function animate() {
  requestAnimationFrame(animate);
  const delta = Math.min(clock.getDelta(), 0.05);
  time += delta;
  
  updateFish(delta, time);
  updateBubbles(delta, time);
  updateFood(delta);
  updateSeaweed(time);
  
  controls.update();
  renderer.render(scene, camera);
  updateFPS(delta);
}
```

updateFPS: count frames, accumulate time, when >= 1s, compute fps.

Let me write.

I think I've planned enough. Let me write the full HTML file.

One thing about raycasting for feeding: click on the tank area creates food at that x,z falling from top. I'll raycast against an invisible plane or just project the click to a plane at the tank's z. Simpler: raycast against the glass box or an invisible large plane at y = top of tank, get intersection point, drop food there. If no intersection, use camera direction.

Let me create an invisible plane (large, horizontal at y near top) for raycasting, or raycast against the tank glass. Let me raycast against the sand plane or a helper plane. I'll add an invisible plane geometry at y=11 (near surface) facing down, and raycast it. Get point, clamp within tank, drop food.

Actually, dropping food from the surface (y near top) at the clicked x,z is what we want. Let me raycast a horizontal plane at the water surface.

Let me create:
```javascript
const feedPlane = new THREE.PlaneGeometry(100, 100);
const feedMat = new THREE.MeshBasicMaterial({visible:false});
const feedMesh = new THREE.Mesh(feedPlane, feedMat);
feedMesh.rotation.x = -Math.PI/2;
feedMesh.position.y = 11;
scene.add(feedMesh);
```
Raycast this on click, get point, create food at that x,z at y=11, velocity 0, gravity pulls down.

Good.

Let me write everything now. Final.

I'll write the CSS with nice styling.

Let me produce the answer.

Given the length, I'll write it all in one go.

Let me make sure the fish model building function returns the group and I attach children properly.

```javascript
function buildFish(color) {
  const group = new THREE.Group();
  
  const bodyMat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.1 });
  
  // Body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 20, 16), bodyMat);
  body.scale.set(0.45, 0.4, 0.95);
  body.castShadow = true;
  group.add(body);
  
  // Tail
  const tailMat = new THREE.MeshStandardMaterial({ color, roughness: 0.6, side: THREE.DoubleSide });
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.5, 8), tailMat);
  tail.rotation.x = -Math.PI/2; // point along Z
  tail.position.set(0, 0, -0.9);
  tail.castShadow = true;
  group.add(tail);
  
  // Top fin
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.15, 0.35, 4), tailMat);
  topFin.position.set(0, 0.4, 0);
  group.add(topFin);
  
  // Side fins
  const leftFin = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.3, 4), tailMat);
  leftFin.rotation.z = Math.PI/2;
  leftFin.position.set(0.35, -0.1, 0);
  group.add(leftFin);
  const rightFin = leftFin.clone();
  rightFin.position.set(-0.35, -0.1, 0);
  group.add(rightFin);
  
  // Eyes
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
  [-1, 1].forEach(s => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.09, 12, 12), eyeMat);
    eye.position.set(0, 0.12, 0.42 * s... 
```

Wait, eyes should be on the sides (X) since forward is Z. Let me place eyes at ±X.

```javascript
  [-1, 1].forEach(s => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.09, 12, 12), eyeMat);
    eye.position.set(0.32*s, 0.12, 0.4);
    group.add(eye);
    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 10), pupilMat);
    pupil.position.set(0.32*s, 0.12, 0.48);
    group.add(pupil);
  });
```

Good.

Now the tail rotation for wiggle: tail.rotation.z = sin(...) * 0.4. Since tail is a cone pointing -Z (after rotation.x = -π/2, cone originally points +Y, rotating -90° around X makes it point... let me think. ConeGeometry apex at +Y, base at -Y. Rotating by -π/2 around X: +Y maps to -Z? Rotation of point (0,1,0) by angle θ around X: (0, cosθ, sinθ). For θ=-π/2: (0, 0, -1). So apex points -Z. Good, tail points back. 

Wiggle rotation.z swings it in XY plane. Fine.

Now fins: leftFin at +X (0.35), rotates. Let me animate leftFin.rotation.x or z. Let me rotate them up-down: leftFin.rotation.z oscillates. Actually side fins flap. Let me rotate around X for a flap. Whatever, minor visual.

Let me animate:
- tail.rotation.z = sin(t*tailSpeed+phase)*0.4
- leftFin.rotation.x = sin(t*tailSpeed+phase)*0.3
- rightFin.rotation.x = -sin(...)*0.3
- topFin slight

OK good enough.

Now let me write the full thing.

For fish initial velocity, give a random horizontal direction small speed.

Let me set speed between 1 and 3, avoidanceRadius between 2 and 4.

Alright, writing final answer.

Let me write the updateFish:

```javascript
function updateFish(f, t) {
  const m = f.mesh;
  const v = f.velocity;
  
  // Seek food
  f.targetFood = null;
  let best = null, bestDist = 15;
  for (const fd of foods) {
    if (!fd.active) continue;
    const d = m.position.distanceTo(fd.mesh.position);
    if (d < bestDist) { bestDist = d; best = fd; }
  }
  if (best) {
    f.targetFood = best;
    const dir = new THREE.Vector3().subVectors(best.mesh.position, m.position).normalize();
    v.addScaledVector(dir, f.speed * t * 0.5);  // hmm t here is time, not delta
  }
  ...
}
```

Wait, I'm passing t as time. Better pass delta separately. Let me pass (f, delta, time).

Acceleration approach: add steering forces, clamp speed. Let me be careful with units. Use delta for smoothing.

Let me do:
```javascript
const steer = new THREE.Vector3();
if (best) {
  steer.subVectors(best.mesh.position, m.position).normalize();
  steer.multiplyScalar(f.speed);
} else {
  // wander
  f.wanderPhase += delta;
  steer.set(Math.sin(f.wanderPhase*0.7)*f.speed*0.3, 0, Math.cos(f.wanderPhase)*f.speed*0.3);
}
// avoidance
for (const o of fishArray) {
  if (o === f) continue;
  const d = m.position.distanceTo(o.mesh.position);
  if (d < f.avoidanceRadius && d > 0.001) {
    const push = new THREE.Vector3().subVectors(m.position, o.mesh.position).divideScalar(d);
    const strength = (f.avoidanceRadius - d) / f.avoidanceRadius;
    steer.addScaledVector(push, f.speed * strength * 2);
  }
}
// walls
const b = {x:16, y:9, z:8};
const margin = 3;
if (m.position.x > b.x - margin) steer.x -= f.speed;
if (m.position.x < -b.x + margin) steer.x += f.speed;
if (m.position.y > b.y - margin) steer.y -= f.speed;
if (m.position.y < -b.y + margin) steer.y += f.speed;
if (m.position.z > b.z - margin) steer.z -= f.speed;
if (m.position.z < -b.z + margin) steer.z += f.speed;

// integrate
v.addScaledVector(steer, delta);
// damping
v.multiplyScalar(0.96);
// clamp
if (v.length() > f.speed) v.setLength(f.speed);
m.position.addScaledVector(v, delta);

// face direction
if (v.lengthSq() > 1e-5) {
  const look = m.position.clone().add(v);
  m.lookAt(look);
}

// tail animation
f.tail.rotation.z = Math.sin(time*f.tailSpeed + f.phase) * 0.4;
```

This should give smooth movement. The damping 0.96 keeps it fluid.

Eat detection:
```javascript
for (const fd of foods) {
  if (!fd.active) continue;
  if (m.position.distanceTo(fd.mesh.position) < 0.7 * f.size) {
    fd.active = false;
    scene.remove(fd.mesh);
    f.size *= 1.05;
    m.scale.setScalar(f.size);
    foodCount--;
  }
}
```

Good.

Food update:
```javascript
function updateFood(delta) {
  for (const fd of foods) {
    if (!fd.active) continue;
    fd.velocity.y -= 9 * delta; // gravity
    fd.mesh.position.addScaledVector(fd.velocity, delta);
    if (fd.mesh.position.y < -11.5) {
      // reached bottom, remove
      fd.active = false;
      scene.remove(fd.mesh);
    }
  }
  foods = foods.filter(f => f.active);
}
```

Drop food:
```javascript
function dropFood(point) {
  const geo = new THREE.SphereGeometry(0.15, 8, 8);
  const mat = new THREE.MeshStandardMaterial({ color: 0xc8863b, roughness: 0.9 });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(point.x, 10, point.z);
  mesh.castShadow = true;
  scene.add(mesh);
  foods.push({ mesh, velocity: new THREE.Vector3(0,-0.5,0), active: true });
  foodCount++;
}
```

Click handler with raycaster on feedPlane.

Bubbles:
```javascript
function createBubble() {
  const geo = new THREE.SphereGeometry(0.1 + Math.random()*0.15, 12, 12);
  const mat = new THREE.MeshPhysicalMaterial({ color: 0xffffff, transmission: 0.9, transparent: true, opacity: 0.4, roughness: 0, metalness: 0 });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set((Math.random()-0.5)*30, -11 + Math.random()*4, (Math.random()-0.5)*16);
  scene.add(mesh);
  bubbles.push({ mesh, speed: 0.5 + Math.random()*1, phase: Math.random()*Math.PI*2, baseX: mesh.position.x, baseZ: mesh.position.z });
}
function updateBubbles(delta, time) {
  for (const b of bubbles) {
    b.mesh.position.y += b.speed * delta;
    b.mesh.position.x = b.baseX + Math.sin(time*1.5 + b.phase)*0.3;
    b.mesh.position.z = b.baseZ + Math.cos(time*1.2 + b.phase)*0.3;
    if (b.mesh.position.y > 11) {
      b.mesh.position.y = -11;
      b.baseX = (Math.random()-0.5)*30;
      b.baseZ = (Math.random()-0.5)*16;
    }
  }
}
```

Rocks:
```javascript
function createRock() {
  const geo = new THREE.DodecahedronGeometry(0.8 + Math.random()*0.8, 0);
  const pos = geo.attributes.position;
  for (let i=0;i<pos.count;i++){
    pos.setXYZ(i, pos.getX(i)+(Math.random()-0.5)*0.25, pos.getY(i)+(Math.random()-0.5)*0.25, pos.getZ(i)+(Math.random()-0.5)*0.25);
  }
  geo.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({ color: 0x8b7355, roughness: 1 });
  const rock = new THREE.Mesh(geo, mat);
  rock.position.set((Math.random()-0.5)*28, -11 + 0.3, (Math.random()-0.5)*14);
  rock.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
  rock.castShadow = true;
  rock.receiveShadow = true;
  scene.add(rock);
}
```

Seaweed:
```javascript
function createSeaweed() {
  const group = new THREE.Group();
  const strands = 2 + Math.floor(Math.random()*3);
  const height = 2 + Math.random()*3;
  const color = new THREE.Color().setHSL(0.28 + Math.random()*0.08, 0.6, 0.35);
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.8, side: THREE.DoubleSide });
  for (let s=0;s<strands;s++){
    const offsetX = (Math.random()-0.5)*0.5;
    const offsetZ = (Math.random()-0.5)*0.5;
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(offsetX, -11, offsetZ),
      new THREE.Vector3(offsetX+0.3, -11+height*0.3, offsetZ),
      new THREE.Vector3(offsetX-0.2, -11+height*0.6, offsetZ+0.2),
      new THREE.Vector3(offsetX, -11+height, offsetZ-0.1),
    ]);
    const geo = new THREE.TubeGeometry(curve, 12, 0.08 + Math.random()*0.06, 6, false);
    const strand = new THREE.Mesh(geo, mat);
    strand.castShadow = true;
    group.add(strand);
  }
  group.position.set((Math.random()-0.5)*30, 0, (Math.random()-0.5)*16);
  group.userData.swayOffset = Math.random()*Math.PI*2;
  group.userData.swaySpeed = 0.5 + Math.random()*0.5;
  scene.add(group);
  seaweeds.push(group);
}
function updateSeaweed(time) {
  for (const s of seaweeds) {
    const o = s.userData.swayOffset, sp = s.userData.swaySpeed;
    s.rotation.x = Math.sin(time*sp + o)*0.05;
    s.rotation.z = Math.cos(time*sp + o)*0.05;
  }
}
```

Sand:
```javascript
const sandGeo = new THREE.PlaneGeometry(40, 24, 40, 24);
sandGeo.rotateX(-Math.PI/2);
const sp = sandGeo.attributes.position;
for (let i=0;i<sp.count;i++){
  sp.setZ(i, sp.getZ(i) + (Math.random()-0.5)*0.3);  // after rotateX, local z becomes world y... 
}
```

Hmm, after rotateX(-π/2), the plane's local XY becomes world XZ and local Z becomes world -Y. Displacing local Z before rotation moves in Y after. Let me displace before rotation using Z, then rotate. Actually order: create PlaneGeometry in XY plane, displace Z (normal direction), then rotateX(-π/2) to lay flat. The displacement in Z becomes Y. Good. But I rotate then displace Z which is now world -Y. Let me displace before rotate. Let me do:

```javascript
const sandGeo = new THREE.PlaneGeometry(40, 24, 40, 24);
const sp = sandGeo.attributes.position;
for (let i=0;i<sp.count;i++){
  sp.setZ(i, (Math.random()-0.5)*0.35);
}
sandGeo.computeVertexNormals();
sandGeo.rotateX(-Math.PI/2);
const sand = new THREE.Mesh(sandGeo, sandMat);
sand.position.y = -12;
sand.receiveShadow = true;
```

Good.

Glass tank:
```javascript
const tankGeo = new THREE.BoxGeometry(36, 24, 20);
const tankMat = new THREE.MeshPhysicalMaterial({ color: 0xbfe6ff, transmission: 0.95, opacity:1, transparent:true, roughness:0.05, metalness:0, thickness:1, side: THREE.DoubleSide });
const tank = new THREE.Mesh(tankGeo, tankMat);
scene.add(tank);
// edges
const edges = new THREE.EdgesGeometry(tankGeo);
const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x88bbdd }));
tank.add(line);
```

Wait, BoxGeometry with edges - EdgesGeometry gives the 12 edges. Good. Add as child of tank so it moves with it (tank at origin).

Background gradient:
```javascript
const canvas = document.createElement('canvas');
canvas.width = 128; canvas.height = 512;
const ctx = canvas.getContext('2d');
const grad = ctx.createLinearGradient(0,0,0,512);
grad.addColorStop(0, '#0a3d6b');
grad.addColorStop(1, '#061426');
ctx.fillStyle = grad; ctx.fillRect(0,0,128,512);
const tex = new THREE.CanvasTexture(canvas);
tex.mapping = THREE.EquirectangularMapping;
scene.background = tex;
```

Hmm equirectangular on a plane background... scene.background as texture maps to the environment sphere. Equirectangular mapping should fill it. Let me use that. Actually for scene.background texture, it's treated as environment. Equirectangular should work. Let me keep it.

Alternatively use a big sphere. But scene.background is fine.

Fog:
```javascript
scene.fog = new THREE.FogExp2(0x0a3d6b, 0.012);
```

Camera: start at (0, 5, 45) looking at center. Zoom limits 10-60.

OrbitControls min/max distance: maxDistance 60, minDistance 10. maxPolarAngle π/1.8.

Let me write the full file now. Enough planning.

I'll write the complete HTML with embedded CSS and JS.

Let me make the UI panels with glass effect.

Info panel top-left, stats top-right.

Buttons: 
- "Добавить рыбку" (Add fish)
- "Больше пузырей" (More bubbles)
- "Свет" (Light toggle)

Stats: fish count, FPS.

Let me write.

I'll make sure everything is wired.

Final code coming up.

Let me also add instructions text.

Writing now.

I want to double-check: in r128, does `THREE.OrbitControls` exist after loading the script? Yes, the UMD build assigns to THREE.OrbitControls.

Also `clock = new THREE.Clock()`.

Let me write the complete file.

For the feed plane raycasting, I need a Vector2 normalized coords:
```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
window.addEventListener('click', (e) => {
  // ignore clicks on UI
  if (e.target.closest('.ui')) return;
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObject(feedPlane, false);
  if (hits.length) {
    const p = hits[0].point;
    dropFood(p);
  } else {
    dropFood(new THREE.Vector3(0, 10, 0));
  }
});
```

feedPlane is a Mesh, intersectObject works. Good.

Let me finalize.

I'll write it all out now as the answer.

Let me make the CSS polished with glassmorphism.

Done planning. Writing the answer.
</think>

# 🐠 3D Аквариум с Реалистичными Рыбками

Вот полный, готовый к работе файл. Сохраните его как `aquarium.html` и откройте в браузере.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; font-family: 'Segoe UI', system-ui, sans-serif; }
  #app { position: fixed; inset: 0; }

  /* Glass panels */
  .panel {
    position: fixed;
    background: rgba(15, 40, 70, 0.35);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 16px;
    color: #eaf4ff;
    padding: 16px 18px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.15);
    z-index: 10;
    user-select: none;
  }

  #info { top: 18px; left: 18px; max-width: 300px; }
  #stats { top: 18px; right: 18px; min-width: 190px; }

  h1 {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #63d0ff, #a0f0ff, #ffd36b);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.5px;
  }

  .hint { font-size: 12.5px; line-height: 1.6; color: #c6dff5; opacity: 0.9; }
  .hint b { color: #fff; }

  .stat-row { display: flex; justify-content: space-between; align-items: center; margin: 6px 0; font-size: 14px; }
  .stat-row .val { font-weight: 700; color: #a0f0ff; font-variant-numeric: tabular-nums; }

  .btn-grid { display: flex; flex-direction: column; gap: 9px; margin-top: 14px; }
  #stats .btn-grid { margin-top: 10px; }

  button {
    cursor: pointer;
    border: none;
    border-radius: 11px;
    padding: 10px 14px;
    font-size: 13.5px;
    font-weight: 600;
    color: #fff;
    background: linear-gradient(135deg, #2a7fff, #4bd0ff);
    box-shadow: 0 4px 14px rgba(42, 127, 255, 0.4);
    transition: transform 0.12s ease, box-shadow 0.18s ease, filter 0.18s ease;
  }
  button:hover { transform: translateY(-2px); filter: brightness(1.12); box-shadow: 0 6px 20px rgba(42,127,255,0.55); }
  button:active { transform: translateY(0); }
  button.alt { background: linear-gradient(135deg, #ff9a3d, #ffd36b); box-shadow: 0 4px 14px rgba(255,154,61,0.4); }
  button.alt:hover { box-shadow: 0 6px 20px rgba(255,154,61,0.55); }
  button.on { background: linear-gradient(135deg, #3ddc84, #7ff0b0); box-shadow: 0 4px 14px rgba(61,220,132,0.5); }

  .footer-note { position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
    color: rgba(200,225,255,0.55); font-size: 12px; z-index: 5; pointer-events: none; }
</style>
</head>
<body>
<div id="app"></div>

<div class="panel" id="info">
  <h1>🐠 3D Аквариум</h1>
  <div class="hint">
    <b>ЛКМ + движение:</b> вращение камеры<br>
    <b>ПКМ + движение:</b> панорамирование<br>
    <b>Колесо:</b> зум (10–60)<br>
    <b>Клик по стеклу:</b> скормить рыбку
  </div>
  <div class="btn-grid">
    <button id="addFish">➕ Добавить рыбку</button>
    <button id="addBubbles" class="alt">🫧 Больше пузырей</button>
  </div>
</div>

<div class="panel" id="stats">
  <div class="stat-row"><span>🐟 Рыбки</span><span class="val" id="fishCount">0</span></div>
  <div class="stat-row"><span>🫧 Пузи</span><span class="val" id="bubbleCount">0</span></div>
  <div class="stat-row"><span>🍽️ Корм</span><span class="val" id="foodCount">0</span></div>
  <div class="stat-row"><span>⚡ FPS</span><span class="val" id="fps">0</span></div>
  <div class="btn-grid">
    <button id="toggleLight" class="on">💡 Свет: ВКЛ</button>
  </div>
</div>

<div class="footer-note">Интерактивный аквариум • Three.js r128</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* =========================================================
   ОСНОВНАЯ ИНИЦИАЛИЗАЦИЯ
   ========================================================= */
const app = document.getElementById('app');

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a3d6b, 0.011);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 0.1, 500);
camera.position.set(0, 4, 46);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
app.appendChild(renderer.domElement);

// Градиентный фон (темно-синий → синий)
(function gradientBackground(){
  const c = document.createElement('canvas');
  c.width = 128; c.height = 512;
  const ctx = c.getContext('2d');
  const g = ctx.createLinearGradient(0,0,0,512);
  g.addColorStop(0, '#12598f');
  g.addColorStop(0.5, '#0a3d6b');
  g.addColorStop(1, '#041224');
  ctx.fillStyle = g; ctx.fillRect(0,0,128,512);
  const tex = new THREE.CanvasTexture(c);
  tex.mapping = THREE.EquirectangularMapping;
  scene.background = tex;
})();

const clock = new THREE.Clock();

/* =========================================================
   ОСВЕЩЕНИЕ
   ========================================================= */
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(14, 30, 12);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 120;
sun.shadow.camera.left = -40;
sun.shadow.camera.right = 40;
sun.shadow.camera.top = 40;
sun.shadow.camera.bottom = -40;
sun.shadow.bias = -0.0004;
scene.add(sun);
scene.add(sun.target);

// Подводное освещение (голубой + синий)
const underLight1 = new THREE.PointLight(0x33ccff, 0.9, 80);
underLight1.position.set(-12, 6, 8);
scene.add(underLight1);
const underLight2 = new THREE.PointLight(0x2266ff, 0.8, 80);
underLight2.position.set(12, -4, -8);
scene.add(underLight2);

let lightOn = true;

/* =========================================================
   ГЕОМЕТРИЯ АКВАРИУМА
   Размеры: 36 (x) x 24 (y) x 20 (z)
   ========================================================= */
const TANK = { x: 18, y: 12, z: 10 };

// Стеклянный контейнер
const tankGeo = new THREE.BoxGeometry(2*TANK.x, 2*TANK.y, 2*TANK.z);
const tankMat = new THREE.MeshPhysicalMaterial({
  color: 0xbfe6ff,
  transmission: 0.95,
  opacity: 1,
  transparent: true,
  roughness: 0.06,
  metalness: 0,
  thickness: 1.2,
  side: THREE.DoubleSide
});
const tank = new THREE.Mesh(tankGeo, tankMat);
scene.add(tank);

// Видимая рамка (edges)
const edges = new THREE.EdgesGeometry(tankGeo);
const frame = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x9fd4ff, transparent:true, opacity:0.8 }));
tank.add(frame);

// Песчаное дно с процедурными неровностями
const sandGeo = new THREE.PlaneGeometry(38, 22, 46, 28);
{
  const p = sandGeo.attributes.position;
  for (let i=0;i<p.count;i++){
    p.setZ(i, (Math.random()-0.5)*0.5);
  }
  sandGeo.computeVertexNormals();
  sandGeo.rotateX(-Math.PI/2);
}
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({ color: 0xd9c28a, roughness: 1 }));
sand.position.y = -TANK.y;
sand.receiveShadow = true;
scene.add(sand);

// Декоративные камни (8 деформированных дедекаэдров)
for (let i=0;i<8;i++){
  const geo = new THREE.DodecahedronGeometry(0.7 + Math.random()*0.9, 0);
  const p = geo.attributes.position;
  for (let j=0;j<p.count;j++){
    const n = 0.18;
    p.setXYZ(j, p.getX(j)+(Math.random()-0.5)*n, p.getY(j)+(Math.random()-0.5)*n, p.getZ(j)+(Math.random()-0.5)*n);
  }
  geo.computeVertexNormals();
  const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0x8b7355, roughness: 1, flatShading: true }));
  rock.position.set((Math.random()-0.5)*30, -TANK.y+0.2, (Math.random()-0.5)*15);
  rock.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
  rock.castShadow = true;
  rock.receiveShadow = true;
  scene.add(rock);
}

// Водоросли (12 кустов через TubeGeometry + CatmullRomCurve3)
const seaweeds = [];
for (let i=0;i<12;i++){
  const group = new THREE.Group();
  const strands = 2 + Math.floor(Math.random()*3);
  const height = 2.2 + Math.random()*3;
  const color = new THREE.Color().setHSL(0.28 + Math.random()*0.09, 0.6, 0.34);
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.8, side: THREE.DoubleSide });
  for (let s=0;s<strands;s++){
    const ox = (Math.random()-0.5)*0.5, oz = (Math.random()-0.5)*0.5;
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(ox, -TANK.y, oz),
      new THREE.Vector3(ox+0.35, -TANK.y+height*0.3, oz),
      new THREE.Vector3(ox-0.25, -TANK.y+height*0.62, oz+0.2),
      new THREE.Vector3(ox, -TANK.y+height, oz-0.1)
    ]);
    const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 14, 0.07+Math.random()*0.06, 6, false), mat);
    tube.castShadow = true;
    group.add(tube);
  }
  group.position.set((Math.random()-0.5)*32, 0, (Math.random()-0.5)*15);
  group.userData = { off: Math.random()*Math.PI*2, spd: 0.5+Math.random()*0.5 };
  scene.add(group);
  seaweeds.push(group);
}

/* =========================================================
   СИСТЕМА БУБРЕЙ
   ========================================================= */
const bubbles = [];
function createBubble(){
  const r = 0.1 + Math.random()*0.16;
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, transmission: 0.9, transparent: true,
    opacity: 0.45, roughness: 0, metalness: 0, thickness: 0.5
  });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(r, 14, 12), mat);
  const bx = (Math.random()-0.5)*32, bz = (Math.random()-0.5)*16;
  mesh.position.set(bx, -TANK.y+Math.random()*3, bz);
  scene.add(mesh);
  bubbles.push({ mesh, speed: 0.6+Math.random()*1.1, phase: Math.random()*Math.PI*2, baseX: bx, baseZ: bz });
}
for (let i=0;i<30;i++) createBubble();

function updateBubbles(dt, time){
  for (const b of bubbles){
    b.mesh.position.y += b.speed*dt;
    b.mesh.position.x = b.baseX + Math.sin(time*1.5+b.phase)*0.35;
    b.mesh.position.z = b.baseZ + Math.cos(time*1.2+b.phase)*0.35;
    if (b.mesh.position.y > TANK.y-0.5){
      b.mesh.position.y = -TANK.y+Math.random()*2;
      b.baseX = (Math.random()-0.5)*32;
      b.baseZ = (Math.random()-0.5)*16;
    }
  }
}

/* =========================================================
   РЫБКИ
   ========================================================= */
const fishArray = [];
const fishColors = [
  0xff8a2a, // оранжевая
  0x2a7bff, // синяя
  0xffe13a, // желто-красная (база)
  0x9b4dff, // фиолетовая
  0xff3b3b, // красная
  0x3bd66a, // зеленая
  0xff6fb2, // розовая
  0xffc83a  // золотая
];

function buildFishGroup(baseColor){
  const group = new THREE.Group();

  // Тело (вытянутая сфера, нос по +Z)
  const bodyMat = new THREE.MeshStandardMaterial({ color: baseColor, roughness: 0.42, metalness: 0.08 });
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 22, 16), bodyMat);
  body.scale.set(0.46, 0.42, 0.96);
  body.castShadow = true; body.receiveShadow = true;
  group.add(body);

  // Хвост (конус назад, по -Z)
  const finMat = new THREE.MeshStandardMaterial({ color: baseColor, roughness: 0.55, side: THREE.DoubleSide });
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.52, 8), finMat);
  tail.rotation.x = -Math.PI/2;
  tail.position.set(0, 0, -0.92);
  tail.castShadow = true;
  group.add(tail);

  // Верхний плавник
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.34, 4), finMat);
  topFin.position.set(0, 0.4, 0.02);
  group.add(topFin);

  // Боковые плавники
  const leftFin = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.28, 4), finMat);
  leftFin.rotation.z = Math.PI/2;
  leftFin.position.set(0.34, -0.08, 0.05);
  group.add(leftFin);
  const rightFin = leftFin.clone();
  rightFin.position.set(-0.34, -0.08, 0.05);
  group.add(rightFin);

  // Глазы с зрачками
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a });
  [-1, 1].forEach(s => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 12), eyeMat);
    eye.position.set(0.33*s, 0.13, 0.42);
    group.add(eye);
    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 10), pupilMat);
    pupil.position.set(0.33*s, 0.13, 0.5);
    group.add(pupil);
  });

  return { group, tail, topFin, leftFin, rightFin };
}

function addFish(){
  const baseColor = fishColors[Math.floor(Math.random()*fishColors.length)];
  const size = 0.6 + Math.random()*0.6; // 0.6 – 1.2
  const { group, tail, topFin, leftFin, rightFin } = buildFishGroup(baseColor);
  group.scale.setScalar(size);

  // Случайная позиция внутри tank
  group.position.set(
    (Math.random()-0.5)*2*TANK.x*0.7,
    (Math.random()-0.5)*2*TANK.y*0.6,
    (Math.random()-0.5)*2*TANK.z*0.7
  );

  // Начальная скорость
  const ang = Math.random()*Math.PI*2;
  const vel = new THREE.Vector3(Math.cos(ang), (Math.random()-0.5)*0.5, Math.sin(ang));

  scene.add(group);

  fishArray.push({
    mesh: group, tail, topFin, leftFin, rightFin,
    velocity: vel,
    speed: 1.0 + Math.random()*1.6,
    tailSpeed: 6 + Math.random()*6,
    phase: Math.random()*Math.PI*2,
    wanderPhase: Math.random()*Math.PI*2,
    targetFood: null,
    avoidanceRadius: 2.2 + Math.random()*1.8,
    size: size
  });
  updateStats();
}

for (let i=0;i<15;i++) addFish();

/* =========================================================
   КОРМ + ФИЗИКА
   ========================================================= */
const foods = [];
function updateFood(dt){
  for (const fd of foods){
    if (!fd.active) continue;
    fd.velocity.y -= 9*dt;            // гравитация
    fd.mesh.position.addScaledVector(fd.velocity, dt);
    fd.mesh.rotation.x += dt*2;
    fd.mesh.rotation.y += dt*1.5;
    if (fd.mesh.position.y <= -TANK.y+0.15){
      fd.active = false;             // достиг дна — удаляем
      scene.remove(fd.mesh);
    }
  }
  while (foods.length && !foods[foods.length-1].active) foods.pop();
}

function dropFood(point){
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.16, 10, 8),
    new THREE.MeshStandardMaterial({ color: 0xca8a3a, roughness: 0.9 })
  );
  mesh.position.set(point.x, TANK.y-1.5, point.z);
  // ограничим по ширине/глубине
  mesh.position.x = THREE.MathUtils.clamp(mesh.position.x, -TANK.x+1, TANK.x-1);
  mesh.position.z = THREE.MathUtils.clamp(mesh.position.z, -TANK.z+1, TANK.z-1);
  mesh.castShadow = true;
  scene.add(mesh);
  foods.push({ mesh, velocity: new THREE.Vector3(0, -0.6, 0), active: true });
  updateStats();
}

// Невидимая плоскость для клика (уровень поверхности)
const feedPlane = new THREE.Mesh(
  new THREE.PlaneGeometry(120, 120),
  new THREE.MeshBasicMaterial({ visible: false })
);
feedPlane.rotation.x = -Math.PI/2;
feedPlane.position.y = TANK.y-1;
scene.add(feedPlane);

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
renderer.domElement.addEventListener('click', (e) => {
  // игнорируем клики по UI
  if (e.target !== renderer.domElement) return;
  mouse.x = (e.clientX/window.innerWidth)*2 - 1;
  mouse.y = -(e.clientY/window.innerHeight)*2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObject(feedPlane, false);
  if (hits.length) dropFood(hits[0].point);
  else dropFood(new THREE.Vector3(0, TANK.y-1, 0));
});

/* =========================================================
   ПОВЕДЕНИЕ РЫБОК (ИИ)
   ========================================================= */
function updateFish(f, dt, time){
  const m = f.mesh, v = f.velocity;

  // 1) Поиск ближайшего корма (радиус 15)
  let best = null, bestDist = 15;
  for (const fd of foods){
    if (!fd.active) continue;
    const d = m.position.distanceTo(fd.mesh.position);
    if (d < bestDist){ bestDist = d; best = fd; }
  }
  const steer = new THREE.Vector3();

  if (best){
    f.targetFood = best;
    steer.subVectors(best.mesh.position, m.position).normalize().multiplyScalar(f.speed);
  } else {
    // 2) Случайное блуждание
    f.wanderPhase += dt;
    steer.set(Math.sin(f.wanderPhase*0.6)*f.speed*0.35,
              (Math.sin(f.wanderPhase*0.4))*0.2,
              Math.cos(f.wanderPhase*0.6)*f.speed*0.35);
  }

  // 3) Избегание столкновений с другими рыбками
  for (const o of fishArray){
    if (o === f) continue;
    const d = m.position.distanceTo(o.mesh.position);
    if (d < f.avoidanceRadius && d > 0.0001){
      const push = new THREE.Vector3().subVectors(m.position, o.mesh.position).divideScalar(d);
      const strength = (f.avoidanceRadius - d) / f.avoidanceRadius;
      steer.addScaledVector(push, f.speed * strength * 2.2);
    }
  }

  // 4) Отражение от стен
  const margin = 2.5;
  if (m.position.x >  TANK.x-margin) steer.x -= f.speed;
  if (m.position.x < -TANK.x+margin) steer.x += f.speed;
  if (m.position.y >  TANK.y-margin) steer.y -= f.speed;
  if (m.position.y < -TANK.y+margin) steer.y += f.speed;
  if (m.position.z >  TANK.z-margin) steer.z -= f.speed;
  if (m.position.z < -TANK.z+margin) steer.z += f.speed;

  // Интеграция с затуханием
  v.addScaledVector(steer, dt);
  v.multiplyScalar(0.955);
  if (v.length() > f.speed) v.setLength(f.speed);
  m.position.addScaledVector(v, dt);

  // Поворот в направлении движения
  if (v.lengthSq() > 1e-5){
    const look = m.position.clone().add(v);
    m.lookAt(look);
  }

  // 5) Поедание корма
  for (const fd of foods){
    if (!fd.active) continue;
    if (m.position.distanceTo(fd.mesh.position) < 0.6*f.size + 0.15){
      fd.active = false;
      scene.remove(fd.mesh);
      f.size *= 1.05;          // рост на 5%
      m.scale.setScalar(f.size);
      updateStats();
    }
  }

  // 6) Анимация хвоста и плавников
  const wag = Math.sin(time*f.tailSpeed + f.phase);
  f.tail.rotation.z = wag * 0.45;
  f.leftFin.rotation.x = wag * 0.4;
  f.rightFin.rotation.x = -wag * 0.4;
  f.topFin.rotation.z = Math.sin(time*f.tailSpeed*0.7+f.phase)*0.12;
}

/* =========================================================
   УПРАВЛЕНИЕ КАМЕРОЙ
   ========================================================= */
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI/1.8;
controls.target.set(0, 0, 0);

/* =========================================================
   UI — СТАТИСТИКА + КНОПКИ
   ========================================================= */
const elFish  = document.getElementById('fishCount');
const elBub   = document.getElementById('bubbleCount');
const elFood  = document.getElementById('foodCount');
const elFps   = document.getElementById('fps');
const btnLight= document.getElementById('toggleLight');

function updateStats(){
  elFish.textContent = fishArray.length;
  elBub.textContent  = bubbles.length;
  elFood.textContent = foods.filter(f=>f.active).length;
}

document.getElementById('addFish').addEventListener('click', () => { if (fishArray.length < 80) addFish(); });
document.getElementById('addBubbles').addEventListener('click', () => { for (let i=0;i<10;i++) createBubble(); updateStats(); });
btnLight.addEventListener('click', () => {
  lightOn = !lightOn;
  sun.intensity = lightOn ? 1.0 : 0.12;
  btnLight.textContent = '💡 Свет: ' + (lightOn ? 'ВКЛ' : 'ВЫКЛ');
  btnLight.classList.toggle('on', lightOn);
});

// FPS-счётчик
let frames = 0, fpsTime = 0, currentFps = 0;

/* =========================================================
   ЦИКЛ АНИМАЦИИ
   ========================================================= */
function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;

  for (const f of fishArray) updateFish(f, dt, time);
  updateFood(dt);
  updateBubbles(dt, time);

  // Покачивание водорослей (вращение по X и Z)
  for (const s of seaweeds){
    s.rotation.x = Math.sin(time*s.spd + s.off)*0.06;
    s.rotation.z = Math.cos(time*s.spd + s.off)*0.06;
  }

  // Подсветка мерцает для живости
  underLight1.intensity = 0.8 + Math.sin(time*1.5)*0.15;

  controls.update();
  renderer.render(scene, camera);

  // FPS
  frames++; fpsTime += dt;
  if (fpsTime >= 0.5){ currentFps = Math.round(frames/fpsTime); frames=0; fpsTime=0; elFps.textContent = currentFps; }
}

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

updateStats();
animate();
</script>
</body>
</html>
```

## 🎯 Что реализовано

| Категория | Детали |
|-----------|--------|
| **🐠 Рыбки** | 15 шт. на старте, вытянутое тело, глаза с зрачками, анимируемый хвост + 3 плавника, 8 цветов, размер 0.6–1.2 |
| **🧠 ИИ** | избегание рыб, отражение от стен, случайное блуждание, преследование корма (радиус 15), рост на 5% после еды |
| **🌊 Окружение** | стеклянный контейнер (`transmission: 0.95`) с рамкой, песок с неровностями, 8 камней-дедокаэдров, 12 водорослей (TubeGeometry + CatmullRom) |
| **🫧 Пузи** | 30 шт., поднимаются вверх с синусоидальным качанием, сброс у поверхности |
| **🍽️ Корм** | клик → падение с гравитацией, обнаружение рыбками, поедание + рост, исчезновение на дне |
| **💡 Освещение** | Ambient + Directional (тени 2048², PCFSoft) + 2 PointLight (голубой/синий), кнопка включения |
| **🎮 Камера** | OrbitControls: вращение/панорама/зум (10–60), `maxPolarAngle = π/1.8`, damping |
| **🖥️ UI** | glass-панели с `backdrop-filter`, градиентный заголовок, статистика (рыбки/пузи/корм/FPS), 3 кнопки |

## 💡 Советы
- **Кликайте по стеклу** аквариума — рыбки плывут к упавшему корму
- Кнопка **«Свет»** переключает основной солнечный свет
- Наблюдайте, как рыбки **растут** после кормления (увеличивается масштаб)

Если хотите — могу добавить звуки, день/ночь с циклом освещения или систему размножения рыбок. 🌊