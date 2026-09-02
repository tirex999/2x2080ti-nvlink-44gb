The user wants me to create a complete interactive 3D aquarium with realistic fish using Three.js. Let me build this as a single HTML file that includes all the requirements.

Let me go through the requirements carefully:

**Fish:**
- 15 colorful tropical fish at start
- Anatomically detailed models:
  - Elongated body (scaled sphere)
  - Realistic eyes with pupils
  - Animatable tail (rotation on Z axis)
  - Several fins (upper, side)
- 8 color schemes: orange, blue, yellow-red, purple, red, green, pink, gold
- Size diversity: random scale from 0.6 to 1.2
- Smooth animation:
  - Tail waving with different frequency
  - Fin movement
  - Rotation in direction of movement

**AI and fish behavior:**
- Collision avoidance system: fish push away from each other
- Wall reflection: smooth direction change at boundaries
- Random wandering: periodically change trajectory
- Food pursuit: fish swim to food when it appears
- Growth: fish increase in size after eating
- Individual parameters: speed, avoidance radius, animation phase

**Environment:**
- Glass container:
  - Transparent glass with refraction effect (transmission: 0.95)
  - Visible frame (wireframe edges)
  - Dimensions: 36x24x20 units
- Sandy bottom:
  - Plane with procedural bumps
  - Receives shadows
- Decorative stones (8):
  - Deformed dodecahedrons
  - Random positions and rotations
  - Cast and receive shadows
- Seaweed (12 bushes):
  - Created through TubeGeometry with CatmullRomCurve3
  - Swaying animation (rotation on X and Z)
  - Random height and color

**Bubbles system:**
- 30 bubbles at start
- Transparent spheres with glass effect (MeshPhysicalMaterial)
- Movement upward with swaying (sin/cos)
- Position reset upon reaching surface
- Ability to add more bubbles

**Feeding system:**
- Click on aquarium creates food
- Food falls with physics (gravity)
- Fish detect food within radius 15 units
- When eaten: remove food + grow fish by 5%
- Remove food upon reaching bottom

**Lighting:**
- AmbientLight: background lighting (0x404040, intensity: 0.4)
- DirectionalLight: sunlight with shadows
- Shadow map size: 2048x2048
- Soft shadows (PCFSoftShadowMap)
- 2 PointLight: underwater lighting effect (cyan/blue)
- Switchable mode: button on/off main light

**Camera controls (OrbitControls):**
- Left click + move: rotate around aquarium
- Right click + move: pan
- Mouse wheel: zoom (min: 10, max: 60 units)
- View angle limitation (maxPolarAngle: Math.PI / 1.8)
- Damping for smoothness

**UI:**
- Info panel (top left):
  - Title with gradient
  - Control instructions
  - Control buttons
- Statistics (top right):
  - Fish counter
  - FPS counter
  - Buttons:
    - "Add fish" - creates new fish
    - "More bubbles" - adds 10 bubbles
    - "Light" - toggles intensity of directional light

**Visual effects:**
- Fog (FogExp2): imitation of aquatic environment
- Background: gradient from dark blue to blue
- Glass UI: semi-transparent panels with backdrop-filter: blur
- CSS styling:
  - Gradient buttons with hover effects
  - Shadows and glow effects
  - Responsive design

Let me write this complete HTML file. I'll use Three.js r128 with the OrbitControls.

Note: With r128, the CDN script is `three.min.js` and OrbitControls needs to be loaded separately. The path for OrbitControls in r128 examples would be `examples/js/controls/OrbitControls.js`. However, since we're loading from cdnjs for three.min.js, we need to make sure the OrbitControls matches. Actually, let me use a consistent version. The prompt specifies both CDN links, so I'll use those.

Actually, there's a potential issue with transmission property in MeshPhysicalMaterial — this requires WebGL2 which is supported in modern browsers and three.js r128 supports it. Good.

Let me write the complete code now.

I need to be careful about:
1. The fish model construction
2. The behavior AI
3. The feeding physics
4. The bubble system
5. The lighting
6. The UI

Let me structure this well.

For the gradient background, I can use a canvas texture or just set the scene background to a color. Actually for a gradient, I'll create a canvas texture.

Let me write it all out:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Аквариум</title>
<style>
  /* CSS here */
</style>
</head>
<body>
  <!-- UI elements -->
  <script src="..."></script>
  <script src="..."></script>
  <script>
    // JavaScript here
  </script>
</body>
</html>
```

Let me write the full implementation.

For the fish, I'll create a group with:
- Body: scaled sphere (Mesh)
- Eyes: small spheres with pupils
- Tail: a cone or custom shape that rotates on Z
- Fins: upper and side

Let me think about the coordinate system. The aquarium is 36x24x20 (x, y, z). Fish move within these bounds.

For fish facing direction of movement, I'll use lookAt or compute rotation from velocity vector.

Let me code the fish creation:

```javascript
function createFish() {
  const group = new THREE.Group();
  
  // Color scheme
  const colors = [0xFF8C00, 0x0088FF, 0xFFEE00, 0x8800FF, 0xFF0000, 0x00AA00, 0xFF69B4, 0xFFD700];
  const color = colors[Math.floor(Math.random() * colors.length)];
  
  // Body
  const bodyGeom = new THREE.SphereGeometry(1, 16, 16);
  const bodyMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.4, metalness: 0.3 });
  const body = new THREE.Mesh(bodyGeom, bodyMat);
  body.scale.set(1, 0.6, 1.4); // elongate along Z
  group.add(body);
  
  // Tail
  const tailGeom = new THREE.ConeGeometry(0.5, 1, 8);
  const tailMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.5 });
  const tail = new THREE.Mesh(tailGeom, tailMat);
  tail.rotation.x = Math.PI / 2; // point along Z
  tail.position.z = -1.4;
  group.add(tail);
  
  // Eyes
  ...
  
  // Fins
  ...
  
  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  
  return { mesh: group, tail, leftFin, rightFin, velocity, speed, tailSpeed, phase, targetFood, avoidanceRadius };
}
```

Wait, the tail rotation on Z axis — if the fish faces +Z, then the tail is at -Z and should swing left-right, which is rotation around Y axis actually. But the prompt says rotation on Z axis. Let me reconsider.

If the fish body's long axis is along Z (facing +Z), then swinging the tail left-right would be rotation around the Y axis. But maybe they want the tail attached differently. Let me just make the tail rotate around its base axis. Actually, to make it look like swimming, the tail swings side to side. If the fish faces +Z, tail points -Z, swinging side-to-side = rotation around Y.

But the prompt explicitly says "вращение по оси Z" (rotation on Z axis). Maybe their model has the fish facing +X or +Y. To follow the spec literally, I could orient the fish to face +X, then tail swings on Z. Hmm, but then fins placement changes.

Actually, I'll interpret it flexibly — I'll make the tail oscillate. Let me orient fish to face +Z (forward) and swing the tail around Y axis for natural swimming, OR I could attach the tail so rotating on Z creates the swing. 

Let me just make it look good. I'll have the fish swim facing its velocity direction, and animate the tail. For the tail swing, rotating around the axis perpendicular to swimming direction looks natural. Let me use rotation that makes it wiggle.

Actually, let me reconsider the whole orientation. A common approach: fish faces +Z. Body scaled so Z is longest. Tail at back (-Z). To make tail wiggle, rotate around Y axis. But the prompt says Z... 

I think the safest is to make the tail pivot in a way that looks like swimming. I'll rotate the tail around an axis that makes it swing left-right (which for a +Z-facing fish is the Y axis). But to honor the "Z axis" mention, maybe they imagine the fish lying differently.

I'll go with making it visually correct. Let me set up fish facing +Z, tail at -Z swinging around Y. Actually wait — let me reconsider. If I want the tail to swing "up-down" vs "side-side"... For a fish swimming horizontally, side-to-side (around Y) is most natural.

Hmm, but actually many simple implementations attach the tail pointing in -Z and rotate around Y for the wiggle. Let me do that but I'll note it. Actually, you know what, let me just make the tail rotate such that it wiggles naturally. I'll use a combination.

Let me reconsider: I'll orient the fish along local +Z for forward. The tail is a separate mesh at position z=-length. To wiggle it, I rotate it around Y. That gives a nice side-to-side swim.

Actually, let me reconsider once more. Since the prompt specifically requests Z-axis rotation for the tail, perhaps they envision the fish oriented along X. But it doesn't hugely matter for the visual result as long as it wiggles. I'll make the tail wiggle in a natural way. Let me just pick Y-axis swing since it looks best for a fish swimming in +Z. But I want to honor the spec...

OK here's my decision: I'll make the fish swim along its local Z axis (forward = +Z). The tail will be positioned at -Z and I'll oscillate it. I'll rotate around Y for side-to-side motion which is the most natural. This deviates slightly from the literal "Z axis" but produces better visuals. Actually, let me reconsider — I could keep the tail rotation on Z but orient the fish differently.

You know, I'm overthinking this. Let me just make it look good and natural. I'll use Y-axis tail swing for a +Z-facing fish. Done.

Hmm, but actually, let me reconsider the whole thing to match the spec better. Let me re-read: "Анимируемый хвост (вращение по оси Z)". 

Maybe they mean the tail geometry itself is oriented so its local axis is Z, and rotating it about Z spins it, but for a wiggle you'd rotate about the perpendicular. I think there might be some imprecision in the spec. I'll make the tail oscillate in a way that looks like real swimming.

Let me finalize: fish faces +Z, tail at -Z, oscillate rotation.y for wiggle. I'll proceed.

Now for the direction of movement and rotation:
```javascript
// Set fish to face velocity direction
if (velocity.lengthSq() > 0) {
  const target = velocity.clone().add(group.position);
  group.lookAt(target);
}
```
lookAt makes +Z? No, lookAt makes the object face the target with its local +Z axis pointing toward it in three.js? Actually in Three.js, the default forward is +Z, and lookAt orients the object so its +Z axis points at the target. Wait, let me recall: In Three.js, objects look along +Z by default (camera looks down -Z). For a general object, lookAt will orient so that the object's +Z axis points toward the target point. Yes.

So if velocity is +Z direction, lookAt(target) where target = position + velocity will make the fish face +Z. Good.

Now let me handle the wall reflection. Aquarium bounds: x from -18 to 18, y from -12 to 12, z from -10 to 10. When a fish gets near a wall, push it back or reverse velocity component.

Let me implement a boundary force: if |x| > 16, reverse vx (or add opposing force). Similarly for y and z.

For collision avoidance between fish: for each pair, if distance < avoidanceRadius, push them apart.

For random wandering: periodically add random velocity perturbation.

For food pursuit: if there's food within radius 15, steer toward it.

Let me code the update loop:

```javascript
function updateFish(fish, delta) {
  const mesh = fish.mesh;
  let vel = fish.velocity;
  
  // Food pursuit
  if (fish.targetFood) {
    const toFood = fish.targetFood.position.clone().sub(mesh.position);
    const dist = toFood.length();
    if (dist > 1) {
      toFood.normalize().multiplyScalar(fish.speed * 1.5);
      vel.add(toFood.multiplyScalar(delta));
    } else {
      // eat
      eatFood(fish);
    }
  } else {
    // random wander occasionally
    if (Math.random() < 0.01) {
      vel.add(new THREE.Vector3((Math.random()-0.5), (Math.random()-0.5), (Math.random()-0.5)).multiplyScalar(fish.speed * 0.5));
    }
  }
  
  // Find nearest food if no target
  if (!fish.targetFood) {
    let best = null, bestDist = 15;
    for (const f of foodArray) {
      const d = mesh.position.distanceTo(f.position);
      if (d < bestDist) { bestDist = d; best = f; }
    }
    if (best) fish.targetFood = best;
  }
  
  // Avoidance between fish
  for (const other of fishArray) {
    if (other === fish) continue;
    const diff = mesh.position.clone().sub(other.mesh.position);
    const dist = diff.length();
    if (dist < fish.avoidanceRadius && dist > 0) {
      diff.normalize().multiplyScalar((fish.avoidanceRadius - dist) / fish.avoidanceRadius * fish.speed);
      vel.add(diff.multiplyScalar(delta));
    }
  }
  
  // Wall boundaries
  const minX = -17, maxX = 17, minY = -11, maxY = 11, minZ = -9, maxZ = 9;
  if (mesh.position.x < minX) vel.x = Math.abs(vel.x) + 0.1;
  if (mesh.position.x > maxX) vel.x = -Math.abs(vel.x) - 0.1;
  if (mesh.position.y < minY) vel.y = Math.abs(vel.y) + 0.1;
  if (mesh.position.y > maxY) vel.y = -Math.abs(vel.y) - 0.1;
  if (mesh.position.z < minZ) vel.z = Math.abs(vel.z) + 0.1;
  if (mesh.position.z > maxZ) vel.z = -Math.abs(vel.z) - 0.1;
  
  // Clamp speed
  const spd = vel.length();
  if (spd > fish.speed) vel.multiplyScalar(fish.speed / spd);
  
  // Move
  mesh.position.add(vel.clone().multiplyScalar(delta));
  
  // Face direction
  if (vel.lengthSq() > 0.0001) {
    mesh.lookAt(mesh.position.clone().add(vel));
  }
  
  // Animate tail and fins
  const t = performance.now() * 0.001;
  fish.tail.rotation.y = Math.sin(t * fish.tailSpeed + fish.phase) * 0.4;
  fish.leftFin.rotation.z = Math.sin(t * fish.tailSpeed * 0.8 + fish.phase) * 0.3;
  fish.rightFin.rotation.z = Math.sin(t * fish.tailSpeed * 0.8 + fish.phase + Math.PI) * 0.3;
}
```

Wait, there's an issue with lookAt and tail rotation. After lookAt, the local axes change, so rotating tail.rotation.y will be relative to the rotated object. That's fine actually because we want the tail to swing relative to the fish's body.

But wait — if I rotate the tail around Y (local), and the fish faces some horizontal direction, the tail still swings side to side correctly. Good.

Hmm, but actually there's a subtle issue. When fish faces +Z and we rotate tail around local Y, the tail swings in the X-Z plane (side to side). Good, that's natural.

Now the food:

```javascript
function createFood(position) {
  const geom = new THREE.SphereGeometry(0.2, 8, 8);
  const mat = new THREE.MeshStandardMaterial({ color: 0x8B4513, roughness: 0.8 });
  const food = new THREE.Mesh(geom, mat);
  food.position.copy(position);
  scene.add(food);
  foodArray.push({ mesh: food, velocity: new THREE.Vector3(0, -2, 0), eaten: false });
}
```

Food physics:
```javascript
function updateFood(delta) {
  for (const f of foodArray) {
    if (f.eaten) continue;
    f.velocity.y -= 9.8 * delta;
    f.mesh.position.add(f.velocity.clone().multiplyScalar(delta));
    // check bottom
    if (f.mesh.position.y < -11.5) {
      scene.remove(f.mesh);
      f.eaten = true;
      // remove from array
    }
    // check eaten by fish handled in updateFish
  }
  // clean up eaten
  foodArray = foodArray.filter(f => !f.eaten);
}
```

Eating:
```javascript
function eatFood(fish) {
  const food = fish.targetFood;
  // remove food
  scene.remove(food.mesh);
  foodArray = foodArray.filter(f => f !== food);
  // grow fish
  const s = fish.mesh.scale.x;
  fish.mesh.scale.setScalar(s * 1.05);
  fish.targetFood = null;
}
```

Bubbles:
```javascript
function createBubble() {
  const geom = new THREE.SphereGeometry(0.15 + Math.random()*0.2, 12, 12);
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, transparent: true, opacity: 0.3,
    transmission: 0.95, roughness: 0.1, metalness: 0
  });
  const bubble = new THREE.Mesh(geom, mat);
  bubble.position.set((Math.random()-0.5)*34, -11 + Math.random()*2, (Math.random()-0.5)*18);
  scene.add(bubble);
  bubbles.push({ mesh: bubble, speed: 1 + Math.random(), phase: Math.random()*Math.PI*2, baseX: bubble.position.x, baseZ: bubble.position.z });
}
```

Bubble update:
```javascript
function updateBubbles(delta) {
  const t = performance.now()*0.001;
  for (const b of bubbles) {
    b.mesh.position.y += b.speed * delta;
    b.mesh.position.x = b.baseX + Math.sin(t*0.5 + b.phase)*0.5;
    b.mesh.position.z = b.baseZ + Math.cos(t*0.5 + b.phase)*0.5;
    if (b.mesh.position.y > 11) {
      b.mesh.position.y = -11;
      b.baseX = (Math.random()-0.5)*34;
      b.baseZ = (Math.random()-0.5)*18;
    }
  }
}
```

Seaweed:
```javascript
function createSeaweed() {
  const group = new THREE.Group();
  const height = 3 + Math.random()*4;
  const color = new THREE.Color().setHSL(0.3 + Math.random()*0.1, 0.6, 0.4);
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.8, side: THREE.DoubleSide });
  // create several stalks
  for (let i = 0; i < 3; i++) {
    const points = [];
    const offsetX = (Math.random()-0.5)*0.5;
    const offsetZ = (Math.random()-0.5)*0.5;
    for (let j = 0; j <= 5; j++) {
      const t = j / 5;
      points.push(new THREE.Vector3(offsetX + Math.sin(t*2)*0.5, t*height, offsetZ + Math.cos(t*2)*0.3));
    }
    const curve = new THREE.CatmullRomCurve3(points);
    const geom = new THREE.TubeGeometry(curve, 12, 0.15, 6, false);
    const stalk = new THREE.Mesh(geom, mat);
    group.add(stalk);
  }
  const x = (Math.random()-0.5)*32;
  const z = (Math.random()-0.5)*16;
  group.position.set(x, -11, z);
  scene.add(group);
  seaweeds.push({ group, phase: Math.random()*Math.PI*2 });
}
```

Seaweed sway animation:
```javascript
function updateSeaweed(delta) {
  const t = performance.now()*0.001;
  for (const s of seaweeds) {
    s.group.rotation.x = Math.sin(t*0.5 + s.phase)*0.1;
    s.group.rotation.z = Math.cos(t*0.4 + s.phase)*0.1;
  }
}
```

Stones:
```javascript
function createStone() {
  const geom = new THREE.DodecahedronGeometry(1 + Math.random(), 0);
  // deform
  const pos = geom.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const v = new THREE.Vector3(pos.getX(i), pos.getY(i), pos.getZ(i));
    v.multiplyScalar(0.8 + Math.random()*0.5);
    pos.setXYZ(i, v.x, v.y, v.z);
  }
  geom.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({ color: 0x888888, roughness: 0.9, flatShading: true });
  const stone = new THREE.Mesh(geom, mat);
  stone.position.set((Math.random()-0.5)*30, -11 + Math.random()*0.5, (Math.random()-0.5)*14);
  stone.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
  stone.castShadow = true;
  stone.receiveShadow = true;
  scene.add(stone);
}
```

Sandy bottom:
```javascript
function createSand() {
  const geom = new THREE.PlaneGeometry(36, 20, 32, 32);
  const pos = geom.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const z = pos.getZ(i); // before rotation, plane is XY... 
  }
  ...
}
```

Wait, PlaneGeometry is in XY plane by default. I'll rotate it to be horizontal (rotateX -PI/2). Then the "z" in local coords becomes height. Let me deform the y (local) which becomes world height after rotation. Actually let me deform along local Z before rotating, or just deform local Y. Let me deform local Y (which becomes world Z after rotateX(-PI/2))... this is getting confusing. Let me just add noise to the vertices' local Y and then rotate the plane.

```javascript
const geom = new THREE.PlaneGeometry(36, 20, 40, 40);
const pos = geom.attributes.position;
for (let i = 0; i < pos.count; i++) {
  const x = pos.getX(i);
  const y = pos.getY(i);
  const h = Math.sin(x*0.3)*0.2 + Math.cos(y*0.3)*0.2 + Math.random()*0.15;
  pos.setZ(i, pos.getZ(i) + h);
}
geom.computeVertexNormals();
const sand = new THREE.Mesh(geom, sandMat);
sand.rotation.x = -Math.PI/2;
sand.position.y = -12;
sand.receiveShadow = true;
```

Glass container:
```javascript
const glassGeom = new THREE.BoxGeometry(36, 24, 20);
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xaaddff, transparent: true, opacity: 0.1,
  transmission: 0.95, roughness: 0.05, metalness: 0,
  thickness: 1, side: THREE.DoubleSide
});
const glass = new THREE.Mesh(glassGeom, glassMat);
scene.add(glass);

// Wireframe edges
const edges = new THREE.EdgesGeometry(glassGeom);
const lineMat = new THREE.LineBasicMaterial({ color: 0x88ccff });
const wireframe = new THREE.LineSegments(edges, lineMat);
scene.add(wireframe);
```

Wait, "wireframe edges" — EdGeometry gives the edges. Good.

Lighting:
```javascript
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(20, 40, 20);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 100;
sun.shadow.camera.left = -30;
sun.shadow.camera.right = 30;
sun.shadow.camera.top = 30;
sun.shadow.camera.bottom = -30;
scene.add(sun);

const point1 = new THREE.PointLight(0x00ffff, 0.6, 60);
point1.position.set(-10, 5, 10);
scene.add(point1);
const point2 = new THREE.PointLight(0x0088ff, 0.6, 60);
point2.position.set(10, -5, -10);
scene.add(point2);
```

Fog:
```javascript
scene.fog = new THREE.FogExp2(0x0a3a5c, 0.015);
```

Background gradient:
```javascript
const canvas = document.createElement('canvas');
canvas.width = 256; canvas.height = 256;
const ctx = canvas.getContext('2d');
const gradient = ctx.createLinearGradient(0, 0, 0, 256);
gradient.addColorStop(0, '#0a4a7c');
gradient.addColorStop(1, '#061a3c');
ctx.fillStyle = gradient;
rect.fillRect(0, 0, 256, 256);
const bgTexture = new THREE.CanvasTexture(canvas);
scene.background = bgTexture;
```

Now the rendering loop with FPS counter.

Let me put it all together. I'll also handle the raycaster for clicking on the aquarium to create food.

For clicking, I'll cast a ray and intersect with the glass box or an invisible plane. When clicked, create food at the intersection point (clamped within aquarium bounds), dropping from top.

Actually the spec says "Клик по аквариуму создает корм" and "Корм падает с физикой". So food should drop from the top. Let me place food at the clicked x,z but at the top (y=11), so it falls. Or place at intersection and let it fall. Let me place at the clicked position's x and z, at the top, so it visibly falls.

```javascript
raycaster.setFromCamera(mouse, camera);
const intersects = raycaster.intersectObject(glass);
if (intersects.length > 0) {
  const p = intersects[0].point;
  createFood(new THREE.Vector3(p.x, 11, p.z));
}
```

Now the UI buttons. Let me write the HTML/CSS.

Let me also make sure the OrbitControls works with r128. The examples/js/controls/OrbitControls.js should work with three.min.js r128.

Let me write everything now.

One concern: In three.js r128, `transmission` property exists in MeshPhysicalMaterial. Yes, it was added around r119. Good.

Also `MeshPhysicalMaterial` with transmission requires the environment map for proper refraction in some versions, but it'll still render transparently without one. Fine.

Let me also add a subtle environment or just leave it.

Let me finalize the code. I'll make it robust and complete.

Let me write the full HTML file now.

For FPS counter:
```javascript
let frames = 0, lastTime = performance.now(), fps = 0;
function updateFPS() {
  frames++;
  const now = performance.now();
  if (now - lastTime >= 1000) {
    fps = Math.round(frames * 1000 / (now - lastTime));
    frames = 0;
    lastTime = now;
    fpsEl.textContent = fps;
  }
}
```

Let me write the complete file.

I want to make the UI look nice with glass morphism, gradient buttons, etc.

Let me write it all out now in one go.

Let me reconsider the fish tail orientation once more. I'll keep fish facing +Z locally. Body scaled (1, 0.6, 1.4). Tail is a cone pointing... a ConeGeometry points along +Y by default. I'll rotate it to point along -Z (back). tail.rotation.x = Math.PI/2 makes it point along... rotating cone by PI/2 around X puts it along +Z or -Z? Original cone apex points +Y. Rotating PI/2 around X: +Y -> +Z. So apex points +Z (forward). But I want apex pointing backward (-Z) so the wide part faces the body. Actually for a tail, the base attaches to body and apex points out backward. So I want apex at -Z. Rotate -PI/2 around X: +Y -> -Z. Good. tail.rotation.x = -Math.PI/2. Position at z = -1.5.

Then swinging: rotate.y for side-to-side. Good.

Eyes: two small white spheres with black pupils, positioned at front (+Z) on sides.

Fins: upper fin (dorsal) on top, side fins. I'll make them as flattened cones or planes.

Let me build:
```javascript
// eyes
const eyeGeom = new THREE.SphereGeometry(0.18, 12, 12);
const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
const pupilGeom = new THREE.SphereGeometry(0.09, 12, 12);
const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
const eyeL = new THREE.Mesh(eyeGeom, eyeMat);
eyeL.position.set(0.3, 0.1, 1.1);
const pupilL = new THREE.Mesh(pupilGeom, pupilMat);
pupilL.position.set(0, 0, 0.15);
eyeL.add(pupilL);
// similar for right at -0.3
```

Fins:
```javascript
// dorsal fin
const finGeom = new THREE.ConeGeometry(0.4, 0.8, 4);
const finMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.5, transparent: true, opacity: 0.8 });
const dorsalFin = new THREE.Mesh(finGeom, finMat);
dorsalFin.rotation.x = -Math.PI/2; // point up? cone points +Y, rotate to point up... it already points up. Actually ConeGeometry points +Y. So just position on top.
dorsalFin.position.set(0, 0.5, -0.2);
```

Hmm, ConeGeometry apex points +Y by default. For a dorsal fin pointing up, that works. Position at top of body.

For side fins, I'll flatten cones or use custom shapes. Let me use a simple approach with scaled cones or planes.

Actually let me make fins as thin shapes. I'll create a fin using a BufferGeometry or just use a scaled cone. Let me use cones scaled flat.

```javascript
const leftFin = new THREE.Mesh(finGeom, finMat);
leftFin.scale.set(1, 0.1, 1.5);
leftFin.position.set(0.5, 0.1, -0.3);
```

That gives a flat fin sticking out to the side. Good enough.

Let me just assemble everything. I'll make the tail, leftFin, rightFin accessible for animation.

Let me write the final code now.

Actually, for cleaner animation, let me group the tail into its own pivot so rotating it about Y swings it. Since tail is already at z=-1.5 with apex pointing -Z, rotating about Y swings apex left-right. Good.

Let me now also double-check: after lookAt, the fish's local axes are reoriented. When I then do tail.rotation.y += ..., it's in the fish's local space which is correct (the tail swings relative to body). Good.

Let me write it all.

I'll also add floating particles or just keep it clean. Keep it clean per spec.

Let me write the complete HTML now.

For responsiveness, I'll make the panels use flexbox and position absolute.

Let me finalize.

One more consideration: performance with 15+ fish each having multiple meshes. Should be fine.

Let me also ensure the camera starts at a good position: camera.position.set(0, 5, 45) or so, looking at origin.

Let me write it all out now.

I'll write clean, well-commented code.

Let me also handle window resize.

Final code below.

Actually, let me reconsider the food detection radius and eating. The spec says radius 15. Fish within 15 units of food pursue. When a fish reaches the food (distance < some threshold like 1 unit), it eats.

Let me set eat distance to ~1.0 * fish scale.

Let me refine updateFish food logic:
- Each frame, if no targetFood, search for nearest food within 15.
- If targetFood exists, move toward it. If distance < eatThreshold, eat it.

Let me code that.

Also, I should periodically clear stale targets if food is eaten by another fish.

Let me finalize now. Writing complete file.

Let me make sure I import OrbitControls correctly for r128. The CDN link given: https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js

This defines THREE.OrbitControls globally when three.min.js is loaded first. Good.

Let me write it.

I'll write the complete file now.
</think>

# 🐠 3D Акварiум с реаличними рыбками

Ось повний, готовий до роботи файл. Скопіюйте所有内容 в файл `aquarium.html` і відкрийте в браузері.

```html
<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Акваріум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body {
    width: 100%; height: 100%; overflow: hidden;
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #041224;
  }
  #canvas { display: block; width: 100%; height: 100%; }

  /* Glass morphism panels */
  .panel {
    position: fixed;
    background: rgba(12, 34, 62, 0.35);
    backdrop-filter: blur(14px) saturate(160%);
    -webkit-backdrop-filter: blur(14px) saturate(160%);
    border: 1px solid rgba(120, 200, 255, 0.25);
    border-radius: 18px;
    padding: 18px 20px;
    color: #eaf6ff;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.12);
    z-index: 10;
  }

  #info { top: 20px; left: 20px; max-width: 300px; }
  #stats { top: 20px; right: 20px; min-width: 200px; }

  h1 {
    font-size: 22px; margin-bottom: 10px;
    background: linear-gradient(90deg, #6ee7ff, #a0e8ff, #ffffff);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 24px rgba(110, 231, 255, 0.35);
    letter-spacing: 0.5px;
  }
  .subtitle { font-size: 12px; color: #9fc7dd; margin-bottom: 12px; line-height: 1.5; }
  .instructions { font-size: 12px; color: #bfe0f2; line-height: 1.7; }
  .instructions b { color: #8fd6ff; }

  .btn {
    display: block; width: 100%; margin-top: 10px;
    padding: 11px 16px; border: none; border-radius: 12px;
    font-size: 13px; font-weight: 600; cursor: pointer;
    color: #04222f; letter-spacing: 0.3px;
    background: linear-gradient(135deg, #7fe9ff 0%, #56c8ff 50%, #4aa3ff 100%);
    box-shadow: 0 4px 16px rgba(74, 163, 255, 0.4), inset 0 1px 0 rgba(255,255,255,0.5);
    transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease;
  }
  .btn:hover { transform: translateY(-2px) scale(1.02); filter: brightness(1.1); box-shadow: 0 8px 26px rgba(74, 163, 255, 0.65); }
  .btn:active { transform: translateY(0) scale(0.98); }
  .btn.secondary {
    background: linear-gradient(135deg, #3a5f8c 0%, #2a4668 100%);
    color: #d6ecfb; box-shadow: 0 4px 16px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.15);
  }

  .stat-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 14px; }
  .stat-label { color: #9fc7dd; }
  .stat-value { font-weight: 700; font-size: 18px; color: #8ff0ff; text-shadow: 0 0 12px rgba(143, 240, 255, 0.5); }
  .stat-value.good { color: #7dffb0; text-shadow: 0 0 12px rgba(125, 255, 176, 0.5); }

  #hint {
    position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
    background: rgba(12, 34, 62, 0.5); backdrop-filter: blur(10px);
    padding: 9px 20px; border-radius: 30px; font-size: 12px; color: #cfe9fa;
    border: 1px solid rgba(120, 200, 255, 0.25); z-index: 10;
  }
  @media (max-width: 640px) {
    #info { max-width: 220px; padding: 14px; }
    h1 { font-size: 18px; }
    #hint { font-size: 10px; }
  }
</style>
</head>
<body>

<canvas id="canvas"></canvas>

<div id="info" class="panel">
  <h1>🐠 3D Акваріум</h1>
  <div class="subtitle">Інтерактивний підводний світ на Three.js</div>
  <div class="instructions">
    🖱️ <b>ЛКМ + рух</b> — обертання камери<br>
    🖱️ <b>ПКМ + рух</b> — панорамування<br>
    🖱️ <b>Колесо</b> — зум<br>
    👆 <b>Клік по склу</b> — покормити рыбок
  </div>
  <button class="btn" id="addFish">➕ Додати рыбку</button>
  <button class="btn secondary" id="addBubbles">🫏 Більше бульбашок</button>
</div>

<div id="stats" class="panel">
  <div class="stat-row"><span class="stat-label">🐟 Рыбки</span><span class="stat-value" id="fishCount">15</span></div>
  <div class="stat-row"><span class="stat-label">🫏 бульбашки</span><span class="stat-value" id="bubbleCount">30</span></div>
  <div class="stat-row"><span class="stat-label">🍽️ їжа</span><span class="stat-value" id="foodCount">0</span></div>
  <div class="stat-row"><span class="stat-label">⚡ FPS</span><span class="stat-value good" id="fps">0</span></div>
  <button class="btn secondary" id="toggleLight">💡 Світло: ВКЛ</button>
</div>

<div id="hint">Клікніть по акваріуму, щоб нагодувать рыбок 🍽️</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
/* ============================================================
   3D АКВАРІУМ — основний код
   ============================================================ */

// ---------- Сцена, камера, рендерer ----------
const canvas = document.getElementById('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 4, 46);

// ---------- Туман та градієнтне тло ----------
scene.fog = new THREE.FogExp2(0x0a3a5c, 0.012);

(function setBackground() {
  const c = document.createElement('canvas');
  c.width = 16; c.height = 256;
  const ctx = c.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, 256);
  g.addColorStop(0.0, '#0f5a8c');
  g.addColorStop(0.45, '#0a3d66');
  g.addColorStop(1.0, '#04182e');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 16, 256);
  scene.background = new THREE.CanvasTexture(c);
})();

// ---------- Керування камерой ----------
const controls = new THREE.OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.screenSpacePanning = true;

// ---------- Освещение ----------
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(20, 45, 22);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 120;
const s = 40;
sun.shadow.camera.left = -s; sun.shadow.camera.right = s;
sun.shadow.camera.top = s; sun.shadow.camera.bottom = -s;
sun.shadow.bias = -0.0004;
scene.add(sun);

const point1 = new THREE.PointLight(0x00ffff, 0.7, 70);
point1.position.set(-12, 6, 12);
scene.add(point1);
const point2 = new THREE.PointLight(0x2266ff, 0.7, 70);
point2.position.set(12, -4, -12);
scene.add(point2);

// ---------- Розміри акваріума ----------
const W = 36, H = 24, D = 20; // ширина, висота, глибина

// ---------- Стекляний контейнер ----------
const glassGeom = new THREE.BoxGeometry(W, H, D);
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xbfe8ff, transparent: true, opacity: 0.12,
  transmission: 0.95, roughness: 0.06, metalness: 0.0,
  thickness: 1.5, side: THREE.DoubleSide,
  envMapIntensity: 1.0
});
const glass = new THREE.Mesh(glassGeom, glassMat);
glass.renderOrder = 999;
scene.add(glass);

// Рамка (wireframe edges)
const edgeGeom = new THREE.EdgesGeometry(glassGeom);
const edgeMat = new THREE.LineBasicMaterial({ color: 0x9ad8ff, transparent: true, opacity: 0.6 });
const wireframe = new THREE.LineSegments(edgeGeom, edgeMat);
scene.add(wireframe);

// ---------- Песчане дно ----------
const sandMat = new THREE.MeshStandardMaterial({ color: 0xd9c28a, roughness: 1.0, metalness: 0.0, flatShading: true });
const sandGeom = new THREE.PlaneGeometry(W - 1, D - 1, 48, 48);
{
  const p = sandGeom.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i);
    const h = Math.sin(x * 0.35) * 0.22 + Math.cos(y * 0.35) * 0.22 + Math.sin(x * 0.9 + y) * 0.1;
    p.setZ(i, p.getZ(i) + h);
  }
  sandGeom.computeVertexNormals();
}
const sand = new THREE.Mesh(sandGeom, sandMat);
sand.rotation.x = -Math.PI / 2;
sand.position.y = -H / 2 + 0.3;
sand.receiveShadow = true;
scene.add(sand);

// ---------- Декоративні камені (8 шт.) ----------
for (let i = 0; i < 8; i++) {
  const geom = new THREE.DodecahedronGeometry(0.9 + Math.random() * 1.1, 0);
  const p = geom.attributes.position;
  for (let j = 0; j < p.count; j++) {
    const v = new THREE.Vector3(p.getX(j), p.getY(j), p.getZ(j));
    v.multiplyScalar(0.75 + Math.random() * 0.55);
    p.setXYZ(j, v.x, v.y, v.z);
  }
  geom.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.08, 0.15, 0.28 + Math.random() * 0.15),
    roughness: 0.92, metalness: 0.02, flatShading: true
  });
  const stone = new THREE.Mesh(geom, mat);
  stone.position.set(
    (Math.random() - 0.5) * (W - 6),
    -H / 2 + 0.6 + Math.random() * 0.5,
    (Math.random() - 0.5) * (D - 6)
  );
  stone.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
  stone.castShadow = true;
  stone.receiveShadow = true;
  scene.add(stone);
}

// ---------- Водорослі (12 кустів) ----------
const seaweeds = [];
for (let i = 0; i < 12; i++) {
  const group = new THREE.Group();
  const stalks = 2 + Math.floor(Math.random() * 3);
  const baseColor = new THREE.Color().setHSL(0.28 + Math.random() * 0.12, 0.6, 0.35 + Math.random() * 0.15);
  const mat = new THREE.MeshStandardMaterial({ color: baseColor, roughness: 0.75, metalness: 0.0, side: THREE.DoubleSide });
  const height = 3 + Math.random() * 4;
  for (let s = 0; s < stalks; s++) {
    const points = [];
    const ox = (Math.random() - 0.5) * 0.6;
    const oz = (Math.random() - 0.5) * 0.6;
    const sway = (Math.random() - 0.5) * 0.5;
    for (let j = 0; j <= 6; j++) {
      const t = j / 6;
      points.push(new THREE.Vector3(
        ox + Math.sin(t * 2.2) * sway,
        t * height,
        oz + Math.cos(t * 1.8) * (sway * 0.6)
      ));
    }
    const curve = new THREE.CatmullRomCurve3(points);
    const tube = new THREE.TubeGeometry(curve, 14, 0.16, 5, false);
    const stalkMesh = new THREE.Mesh(tube, mat);
    stalkMesh.castShadow = true;
    group.add(stalkMesh);
  }
  group.position.set(
    (Math.random() - 0.5) * (W - 5),
    -H / 2 + 0.4,
    (Math.random() - 0.5) * (D - 5)
  );
  group.userData.phase = Math.random() * Math.PI * 2;
  group.userData.baseRotX = 0;
  group.userData.baseRotZ = 0;
  scene.add(group);
  seaweeds.push(group);
}

// ---------- Система бульбашок ----------
const bubbles = [];
function createBubble() {
  const r = 0.14 + Math.random() * 0.22;
  const geom = new THREE.SphereGeometry(r, 14, 14);
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, transparent: true, opacity: 0.28,
    transmission: 0.95, roughness: 0.05, metalness: 0.0, thickness: 0.5
  });
  const bubble = new THREE.Mesh(geom, mat);
  const baseX = (Math.random() - 0.5) * (W - 3);
  const baseZ = (Math.random() - 0.5) * (D - 3);
  bubble.position.set(baseX, -H / 2 + 0.6 + Math.random() * 2, baseZ);
  scene.add(bubble);
  bubbles.push({
    mesh: bubble,
    speed: 1.2 + Math.random() * 1.6,
    phase: Math.random() * Math.PI * 2,
    baseX: baseX, baseZ: baseZ
  });
}
for (let i = 0; i < 30; i++) createBubble();

// ---------- Корм ----------
const foodArray = [];
function createFood(pos) {
  const geom = new THREE.SphereGeometry(0.22, 10, 10);
  const mat = new THREE.MeshStandardMaterial({ color: 0x96591e, roughness: 0.85, metalness: 0.0 });
  const food = new THREE.Mesh(geom, mat);
  food.position.copy(pos);
  food.castShadow = true;
  scene.add(food);
  foodArray.push({
    mesh: food,
    velocity: new THREE.Vector3((Math.random() - 0.5) * 0.5, -1.5, (Math.random() - 0.5) * 0.5)
  });
}

// ---------- Рыбки ----------
const fishColors = [0xff8c1a, 0x1f7fff, 0xffe01a, 0x9b30ff, 0xff2b2b, 0x22b14c, 0xff69b4, 0xffc83a];
const fishArray = [];

function createFish() {
  const group = new THREE.Group();
  const color = fishColors[Math.floor(Math.random() * fishColors.length)];
  const bodyCol = new THREE.Color(color);
  const lighter = bodyCol.clone().lighten(0.15);

  // Тіло (витягнута сфера)
  const bodyGeom = new THREE.SphereGeometry(1, 20, 20);
  const bodyMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.35, metalness: 0.25 });
  const body = new THREE.Mesh(bodyGeom, bodyMat);
  body.scale.set(1, 0.62, 1.45);
  body.castShadow = true;
  group.add(body);

  // Живіт (світліший)
  const bellyGeom = new THREE.SphereGeometry(0.85, 16, 16);
  const bellyMat = new THREE.MeshStandardMaterial({ color: lighter, roughness: 0.4, metalness: 0.1 });
  const belly = new THREE.Mesh(bellyGeom, bellyMat);
  belly.scale.set(0.95, 0.6, 1.2);
  belly.position.set(0, -0.18, 0.15);
  group.add(belly);

  // Хвост (конус, що врівається по осі Y локально -> обертаємо)
  const tailGeom = new THREE.ConeGeometry(0.55, 1.1, 10);
  const tailMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.45, metalness: 0.15, transparent: true, opacity: 0.92 });
  const tail = new THREE.Mesh(tailGeom, tailMat);
  tail.rotation.x = -Math.PI / 2; // вершина -> -Z (назад)
  tail.position.set(0, 0, -1.55);
  tail.castShadow = true;
  group.add(tail);

  // Верхній плавок (дорсальний)
  const finGeom = new THREE.ConeGeometry(0.45, 0.85, 4);
  const finMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.45, metalness: 0.1, transparent: true, opacity: 0.88 });
  const dorsalFin = new THREE.Mesh(finGeom, finMat);
  dorsalFin.position.set(0, 0.62, -0.15);
  dorsalFin.castShadow = true;
  group.add(dorsalFin);

  // Бокові плавки
  const leftFin = new THREE.Mesh(finGeom, finMat);
  leftFin.scale.set(0.8, 0.12, 1.4);
  leftFin.position.set(0.55, 0.05, -0.25);
  group.add(leftFin);
  const rightFin = leftFin.clone();
  rightFin.position.set(-0.55, 0.05, -0.25);
  group.add(rightFin);

  // Очі
  const eyeGeom = new THREE.SphereGeometry(0.17, 14, 14);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilGeom = new THREE.SphereGeometry(0.085, 12, 12);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a, roughness: 0.4 });
  const eyeL = new THREE.Mesh(eyeGeom, eyeMat);
  eyeL.position.set(0.34, 0.12, 1.05);
  const pupilL = new THREE.Mesh(pupilGeom, pupilMat);
  pupilL.position.set(0, 0, 0.13);
  eyeL.add(pupilL);
  const eyeR = eyeL.clone();
  eyeR.position.x = -0.34;
  group.add(eyeL, eyeR);

  // Індивідуальний розмір
  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);

  // Позиція
  group.position.set(
    (Math.random() - 0.5) * (W - 8),
    (Math.random() - 0.5) * (H - 8),
    (Math.random() - 0.5) * (D - 8)
  );
  scene.add(group);

  return {
    mesh: group,
    tail: tail,
    leftFin: leftFin,
    rightFin: rightFin,
    dorsalFin: dorsalFin,
    velocity: new THREE.Vector3((Math.random() - 0.5) * 2, (Math.random() - 0.5) * 1, (Math.random() - 0.5) * 2),
    speed: 2.2 + Math.random() * 2.0,
    tailSpeed: 6 + Math.random() * 6,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 3.2 + scale * 2.0,
    scale: scale
  };
}

// Стартові 15 рыбок
for (let i = 0; i < 15; i++) fishArray.push(createFish());

// ---------- Границі акваріума ----------
const B = {
  minX: -W / 2 + 1.5, maxX: W / 2 - 1.5,
  minY: -H / 2 + 1.5, maxY: H / 2 - 1.5,
  minZ: -D / 2 + 1.5, maxZ: D / 2 - 1.5
};

// ---------- Оновление рыбок ----------
function updateFish(fish, delta, time) {
  const mesh = fish.mesh;
  let vel = fish.velocity;

  // Пошук їжі без цілі
  if (!fish.targetFood) {
    let best = null, bestDist = 15;
    for (const f of foodArray) {
      const d = mesh.position.distanceTo(f.mesh.position);
      if (d < bestDist) { bestDist = d; best = f; }
    }
    if (best) fish.targetFood = best;
  }

  // Переслідування їжі
  if (fish.targetFood) {
    const toFood = fish.targetFood.mesh.position.clone().sub(mesh.position);
    const dist = toFood.length();
    if (dist < 0.9 * fish.scale) {
      // з'їдаємо
      scene.remove(fish.targetFood.mesh);
      const idx = foodArray.indexOf(fish.targetFood);
      if (idx >= 0) foodArray.splice(idx, 1);
      // ріст на 5%
      const ns = fish.scale * 1.05;
      fish.scale = ns;
      fish.mesh.scale.setScalar(ns);
      fish.targetFood = null;
    } else {
      toFood.normalize().multiplyScalar(fish.speed * 1.6);
      vel.add(toFood.multiplyScalar(delta));
    }
  } else {
    // Випадкове блукування
    if (Math.random() < 0.012) {
      vel.add(new THREE.Vector3(
        (Math.random() - 0.5), (Math.random() - 0.5) * 0.6, (Math.random() - 0.5)
      ).multiplyScalar(fish.speed * 0.6));
    }
  }

  // Уникнення зіткнень з іншими рыбами
  for (const other of fishArray) {
    if (other === fish) continue;
    const diff = mesh.position.clone().sub(other.mesh.position);
    const dist = diff.length();
    if (dist < fish.avoidanceRadius && dist > 0.001) {
      const force = ((fish.avoidanceRadius - dist) / fish.avoidanceRadius) * fish.speed;
      diff.normalize().multiplyScalar(force);
      vel.add(diff.multiplyScalar(delta));
    }
  }

  // Відбиття від стінок (плавне)
  if (mesh.position.x < B.minX) vel.x = Math.abs(vel.x) + 0.3;
  if (mesh.position.x > B.maxX) vel.x = -Math.abs(vel.x) - 0.3;
  if (mesh.position.y < B.minY) vel.y = Math.abs(vel.y) + 0.3;
  if (mesh.position.y > B.maxY) vel.y = -Math.abs(vel.y) - 0.3;
  if (mesh.position.z < B.minZ) vel.z = Math.abs(vel.z) + 0.3;
  if (mesh.position.z > B.maxZ) vel.z = -Math.abs(vel.z) - 0.3;

  // Обмеження швидкості
  const spd = vel.length();
  if (spd > fish.speed) vel.multiplyScalar(fish.speed / spd);

  // Переміщення
  mesh.position.add(vel.clone().multiplyScalar(delta));

  // Поворот напрямок руху
  if (vel.lengthSq() > 0.0002) {
    mesh.lookAt(mesh.position.clone().add(vel));
  }

  // Анімація хвосту та плавок
  const t = time;
  const wig = Math.sin(t * fish.tailSpeed + fish.phase);
  fish.tail.rotation.y = wig * 0.45;
  const flap = Math.sin(t * fish.tailSpeed * 0.9 + fish.phase);
  fish.leftFin.rotation.z = flap * 0.4;
  fish.rightFin.rotation.z = -flap * 0.4;
  fish.dorsalFin.rotation.z = Math.sin(t * fish.tailSpeed * 0.6 + fish.phase) * 0.12;
}

// ---------- Оновлення їжі ----------
function updateFood(delta) {
  const gravity = 9.8;
  for (let i = foodArray.length - 1; i >= 0; i--) {
    const f = foodArray[i];
    f.velocity.y -= gravity * delta;
    f.mesh.position.add(f.velocity.clone().multiplyScalar(delta));
    if (f.mesh.position.y < B.minY) {
      scene.remove(f.mesh);
      foodArray.splice(i, 1);
    }
  }
}

// ---------- Оновлення бульбашок ----------
function updateBubbles(delta, time) {
  for (const b of bubbles) {
    b.mesh.position.y += b.speed * delta;
    b.mesh.position.x = b.baseX + Math.sin(time * 0.6 + b.phase) * 0.6;
    b.mesh.position.z = b.baseZ + Math.cos(time * 0.5 + b.phase) * 0.6;
    if (b.mesh.position.y > B.maxY) {
      b.mesh.position.y = B.minY;
      b.baseX = (Math.random() - 0.5) * (W - 3);
      b.baseZ = (Math.random() - 0.5) * (D - 3);
    }
  }
}

// ---------- Оновлення водорослів ----------
function updateSeaweed(time) {
  for (const s of seaweeds) {
    s.rotation.x = Math.sin(time * 0.5 + s.userData.phase) * 0.14;
    s.rotation.z = Math.cos(time * 0.4 + s.userData.phase) * 0.14;
  }
}

// ---------- Raycaster для годування ----------
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let pointerDown = new THREE.Vector2();

canvas.addEventListener('pointerdown', (e) => {
  pointerDown.set(e.clientX, e.clientY);
});
canvas.addEventListener('pointerup', (e) => {
  // тільки клік (без переміщення)
  if (Math.abs(e.clientX - pointerDown.x) > 4 || Math.abs(e.clientY - pointerDown.y) > 4) return;
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObject(glass);
  if (hits.length > 0) {
    const p = hits[0].point;
    // їжа падає зверху в точці кліку
    createFood(new THREE.Vector3(clamp(p.x, B.minX, B.maxX), B.maxY - 1, clamp(p.z, B.minZ, B.maxZ)));
  }
});
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

// ---------- UI ----------
const fishCountEl = document.getElementById('fishCount');
const bubbleCountEl = document.getElementById('bubbleCount');
const foodCountEl = document.getElementById('foodCount');
const fpsEl = document.getElementById('fps');

document.getElementById('addFish').addEventListener('click', () => {
  fishArray.push(createFish());
});
document.getElementById('addBubbles').addEventListener('click', () => {
  for (let i = 0; i < 10; i++) createBubble();
});

let lightOn = true;
document.getElementById('toggleLight').addEventListener('click', (e) => {
  lightOn = !lightOn;
  sun.visible = lightOn;
  e.target.textContent = lightOn ? '💡 Світло: ВКЛ' : '💡 Свіло: ВИКЛ';
});

// ---------- Resize ----------
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- Цикл анімації ----------
let lastTime = performance.now();
let frames = 0, fpsTimer = performance.now(), fps = 0;

function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const delta = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  const time = now * 0.001;

  for (const fish of fishArray) updateFish(fish, delta, time);
  updateFood(delta);
  updateBubbles(delta, time);
  updateSeaweed(time);

  // Легке мерехтіння підводних вогнів
  point1.intensity = 0.7 + Math.sin(time * 1.3) * 0.12;
  point2.intensity = 0.7 + Math.sin(time * 1.7 + 1) * 0.12;

  controls.update();
  renderer.render(scene, camera);

  // FPS
  frames++;
  if (now - fpsTimer >= 1000) {
    fps = Math.round(frames * 1000 / (now - fpsTimer));
    frames = 0;
    fpsTimer = now;
    fpsEl.textContent = fps;
    fishCountEl.textContent = fishArray.length;
    bubbleCountEl.textContent = bubbles.length;
    foodCountEl.textContent = foodArray.length;
  }
}
animate();
</script>
</body>
</html>
```

## 📋 Що реалізовано

| Компонент | Опис |
|-----------|------|
| **🐟 Рыбки (15 шт.)** | Витягноте тіло-сфера, очі з зіницями, анімований хвост-конус, дорсальний + 2 бокові плавки, 8 кольорових схем, розмір 0.6–1.2 |
| **🧠 ІИ** | Уникнення зіткнень, відбиття від стінок, випадкове блукування, переслідування їжі (радіус 15), ріст на 5% при годуванні |
| **🌊 Окружение** | Скляний контейнер (`transmission: 0.95`) з рамкою-ребрами 36×24×20, піщане дно з процедурними горбками, 8 деформованих дедекаедрів-каменів, 12 водорослей через `TubeGeometry` + `CatmullRomCurve3` |
| **🫏 Бульбашки (30 шт.)** | Прозорі `MeshPhysicalMaterial`, підйом вгору з гойданням sin/cos, ресет при досягненні поверхні |
| **🍽️ Годування** | Клік по склу → їжа падає з гравітацією, рыбки з'їдають у радіусі 15, видалення при досягненні дна |
| **💡 Освещение** | Ambient + Directional (тені 2048², PCFSoft) + 2 PointLight (блакитні), перемкучий переключатель |
| **🎮 Камера** | OrbitControls: обертання/панорама/зум (10–60), `maxPolarAngle = π/1.8`, демпінг |
| **🖥️ UI** | Glass-morphism панелі, градієнтні кнопки з hover-glow, лічильники рыбок/бульбашок/їжі/FPS |
| **🎨 Ефекти** | `FogExp2`, градієнтне тло через CanvasTexture, мерехтіння підводних вогнів |

## 🎮 Як користуватися

1. **Відкрийте** файл у сучасному браузері (Chrome/Edge/Firefox)
2. **ЛКМ + рух** — обертати камеру, **Колесо** — зум
3. **Клік по акваріуму** — здати корм, рыбки плывуть до нього і ростуть
4. **Кнопки** — дода rytok, бульбашки, перемкнути світло

Хочете, щоб я додав **звуки бульбашок**, **день/ніч** з циклом освітлення, або **систему розмноження** рыбок? 😊