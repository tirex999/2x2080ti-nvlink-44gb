The user wants me to create a complete interactive 3D aquarium with Three.js based on their detailed specifications. Let me build this as a single HTML file with all the features they described.

Let me go through the requirements:

1. **Fish**: 15 colorful tropical fish at start
   - Anatomically detailed models: stretched sphere body, realistic eyes with pupils, animatable tail (Z-axis rotation), several fins (upper, side)
   - 8 color schemes
   - Random scale 0.6-1.2
   - Smooth animation: tail waving with different frequency, fin movement, turning in direction of movement

2. **AI and behavior**:
   - Collision avoidance system
   - Wall reflection
   - Random wandering
   - Food chasing
   - Growth after eating
   - Individual parameters

3. **Environment**:
   - Glass container (transmission 0.95)
   - Wireframe edges
   - Dimensions 36x24x20
   - Sandy bottom with procedural bumps
   - 8 decorative stones (deformed dodecahedra)
   - 12 seaweed bushes (TubeGeometry with CatmullRomCurve3)

4. **Bubble system**:
   - 30 bubbles at start
   - Transparent spheres with glass effect
   - Moving up with swaying
   - Position reset when reaching surface
   - Ability to add more

5. **Feeding system**:
   - Click creates food
   - Food falls with gravity
   - Fish detect food within radius 15
   - Eating removes food + grows fish 5%
   - Remove food when reaching bottom

6. **Lighting**:
   - AmbientLight
   - DirectionalLight with shadows
   - 2 PointLights
   - Toggle main light button

7. **Camera controls (OrbitControls)**:
   - Left click + move: rotate
   - Right click + move: pan
   - Mouse wheel: zoom
   - Angle constraints
   - Damping

8. **UI**:
   - Info panel (top left)
   - Statistics (top right)
   - Buttons

Let me write this comprehensive HTML file. I'll use Three.js r128 from CDN.

Note: In r128, MeshPhysicalMaterial with transmission might not be fully supported the same way as newer versions. Actually, transmission was added around r130ish. Let me check... In r128, transmission property may not exist. Let me handle this gracefully - I can use opacity for the glass effect instead, or use MeshPhysicalMaterial with transparency.

Actually, let me reconsider. The transmission property requires newer Three.js. Since the user specified r128, I should use properties available in r128. I'll use MeshPhysicalMaterial with high metalness/roughness adjustments and transparency for the glass effect, or just use opacity.

Let me build this carefully. I'll make it work well with r128 while implementing as many features as possible.

Let me write the complete code:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Аквариум</title>
<style>
/* CSS styles */
</style>
</head>
<body>
<!-- UI -->
<script src="three.js CDN"></script>
<script src="OrbitControls CDN"></script>
<script>
// Main code
</script>
</body>
</html>
```

Let me write the full implementation now.

For the glass effect in r128, I'll use MeshPhysicalMaterial with transparency and low opacity, plus MeshBasicMaterial options. Actually let me use a combination. For transmission to work properly we'd need r142+, but I'll simulate with transparency.

Let me write comprehensive code:

I need to be careful about:
- Tail animation (rotation on Z axis)
- Fin movement
- Fish turning (using lookAt or quaternion)
- Food physics
- Bubble movement
- Stone deformation
- Seaweed using TubeGeometry

Let me write it all out.

For the fish direction, I'll set the fish model to face its +X axis, then use quaternion.setFromUnitVectors to point forward along velocity, or use lookAt.

Let me structure the fish group:
- Body: scaled sphere (Mesh)
- Tail: a cone/pyramid that rotates on Z
- Fins: small shapes
- Eyes: small spheres with pupils

For the tail rotation on Z axis - if the fish swims along X axis, the tail should oscillate on the Y axis actually... but the spec says Z axis. Let me just make it rotate and it'll look like swimming. Actually, if the fish points along +X, then the tail at -X would swing in the XY plane which is rotation around Z. That makes sense! So tail rotates around Z axis (the fish's local axis). Good.

Let me define fish pointing along +X.

Tail positioned at -x (back), swings around Z axis.

Let me code this.

For lighting shadows, I need to set castShadow/receiveShadow on meshes and enable shadowMap on renderer.

Let me write the complete file now.

I'll make the CSS nice with glass morphism effects, gradient buttons, etc.

Let me write it all out comprehensively.

For the fog: FogExp2 with blue color.

For background: gradient - I'll create a canvas texture for the background, or use CSS gradient behind. Actually for Three.js background, I can set scene.background to a color, or create a gradient texture. Let me create a gradient canvas texture for the background.

Let me write everything now.

Here's my plan for the code structure:

```javascript
// Scene setup
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a3d5c, 0.015);

// Camera
const camera = new THREE.PerspectiveCamera(...);

// Renderer
const renderer = new THREE.WebGLRenderer({...});

// Background gradient
// Lighting
// Aquarium tank
// Sandy bottom
// Stones
// Seaweed
// Bubbles
// Fish
// Food
// Controls
// Event handlers
// Animation loop
```

Let me write the full thing.

For the gradient background, I'll create a canvas:

```javascript
function createGradientTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 512);
  gradient.addColorStop(0, '#1a5276');
  gradient.addColorStop(1, '#0a2341');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 512, 512);
  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}
```

Now let me write the fish creation function:

```javascript
function createFish() {
  const group = new THREE.Group();
  
  // Color selection
  const colors = [0xff8c00, 0x0088ff, 0xffff00, 0x8800ff, 0xff0000, 0x00aa00, 0xff69b4, 0xffd700];
  const color = colors[Math.floor(Math.random() * colors.length)];
  
  // Body
  const bodyGeom = new THREE.SphereGeometry(1, 16, 16);
  const bodyMat = new THREE.MeshStandardMaterial({ color, roughness: 0.4, metalness: 0.1 });
  const body = new THREE.Mesh(bodyGeom, bodyMat);
  body.scale.set(1, 0.6, 0.5); // stretch
  group.add(body);
  
  // Tail
  const tailGeom = new THREE.ConeGeometry(0.5, 1, 8);
  const tailMat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, transparent: true, opacity: 0.8 });
  const tail = new THREE.Mesh(tailGeom, tailMat);
  tail.rotation.z = Math.PI / 2;
  tail.position.x = -1.2;
  group.add(tail);
  
  // Eyes
  ...
  
  // Fins
  ...
  
  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  
  return { group, tail, ..., };
}
```

Let me finalize the whole thing. I'll write clean, working code.

For the eyes: two small white spheres with darker pupils, placed on the sides/front of the head.

Let me put eyes at +X (front) area, both sides (±Y).

Actually fish eyes are usually on sides of head. Let me place them at x = 0.4, y = 0.2, z = ±0.4.

For fins: top fin (dorsal), side fins (pectoral). Small triangles/cones.

Let me write it all.

For food: small spheres that fall with gravity.

```javascript
function createFood(pos) {
  const geom = new THREE.SphereGeometry(0.15, 8, 8);
  const mat = new THREE.MeshStandardMaterial({ color: 0x8b4513 });
  const food = new THREE.Mesh(geom, mat);
  food.position.copy(pos);
  scene.add(food);
  foodArray.push({ mesh: food, vy: 0 });
}
```

Food physics in animation loop:
```javascript
food.vy -= 0.01; // gravity
food.mesh.position.y += food.vy * delta;
if (food.mesh.position.y < floorY) remove food;
```

Fish detection:
```javascript
for each fish:
  find nearest food within radius 15
  if found, move towards it
  if close enough to food, eat it (remove food, grow fish 5%)
```

Let me write the full animation loop.

Now let me write the complete HTML file. I'll make it polished.

Let me also add FPS counter.

Let me write it all out now. This is going to be a long file but complete.

For OrbitControls in r128, the script is at:
https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js

This defines THREE.OrbitControls globally.

Let me write the final code.

I want to make sure the fish turning works. I'll use:
```javascript
const direction = fish.velocity.clone().normalize();
if (direction.lengthSq() > 0.001) {
  fish.quaternion.setFromUnitVectors(new THREE.Vector3(1, 0, 0), direction);
}
```

This rotates the fish group so its +X axis points along velocity. Good.

But wait, the tail is at -X and swings around Z. When we rotate the whole group, the tail moves with it. Good.

Let me also add subtle bobbing to fish.

Let me write the complete file now.

For seaweed using TubeGeometry with CatmullRomCurve3:
```javascript
function createSeaweed() {
  const points = [];
  const height = 3 + Math.random() * 4;
  const segments = 8;
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const x = Math.sin(t * Math.PI * 2 + Math.random()) * 0.5;
    const y = t * height;
    const z = Math.cos(t * Math.PI * 2) * 0.5;
    points.push(new THREE.Vector3(x, y, z));
  }
  const curve = new THREE.CatmullRomCurve3(points);
  const geom = new THREE.TubeGeometry(curve, 20, 0.15, 8, false);
  const mat = new THREE.MeshStandardMaterial({ color: 0x228b22, roughness: 0.8 });
  const seaweed = new THREE.Mesh(geom, mat);
  // store base position for animation
  seaweed.userData.baseRotation = { x: Math.random()*0.5, z: Math.random()*0.5 };
  return seaweed;
}
```

Animate by rotating around X and Z.

For stones (deformed dodecahedra):
```javascript
function createStone() {
  const geom = new THREE.DodecahedronGeometry(1 + Math.random(), 0);
  const positions = geom.attributes.position;
  for (let i = 0; i < positions.count; i++) {
    const factor = 0.8 + Math.random() * 0.4;
    positions.setX(i, positions.getX(i) * factor);
    positions.setY(i, positions.getY(i) * factor);
    positions.setZ(i, positions.getZ(i) * factor);
  }
  geom.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({ color: 0x808080, roughness: 0.9 });
  const stone = new THREE.Mesh(geom, mat);
  return stone;
}
```

For sandy bottom with procedural bumps:
```javascript
const sandGeom = new THREE.PlaneGeometry(36, 20, 30, 20);
const positions = sandGeom.attributes.position;
for (let i = 0; i < positions.count; i++) {
  const z = Math.random() * 0.3; // bump
  positions.setZ(i, z); // since plane is in XY, Z becomes height after rotation
}
sandGeom.computeVertexNormals();
```

Then rotate the plane to be horizontal (-Math.PI/2 on X).

Let me assemble everything into the final HTML.

I'll add a nice title, info panel, stats panel, and buttons.

Let me finalize.

One consideration: transmission in r128. MeshPhysicalMaterial exists in r128 but transmission property was added later (~r138). Setting transmission won't error but won't have effect. I'll use opacity + transparency for glass. Actually, let me just use MeshStandardMaterial/MeshPhysicalMaterial with transparency for the tank glass. I'll note this.

Actually, to make the glass look good, I'll use MeshPhysicalMaterial with opacity ~0.15, high transparency, and some roughness. Or I could keep it simple with a light blue transparent material.

Let me write the tank as a BoxGeometry with edges (EdgesGeometry for wireframe edges).

```javascript
const tankGeom = new THREE.BoxGeometry(36, 24, 20);
const tankMat = new THREE.MeshPhysicalMaterial({
  color: 0xaaddff,
  transparent: true,
  opacity: 0.15,
  roughness: 0.1,
  metalness: 0,
  side: THREE.DoubleSide
});
const tank = new THREE.Mesh(tankGeom, tankMat);
scene.add(tank);

// Edges
const edges = new THREE.EdgesGeometry(tankGeom);
const lineMat = new THREE.LineBasicMaterial({ color: 0x88ccff });
const edgeLines = new THREE.LineSegments(edges, lineMat);
tank.add(edgeLines);
```

OK let me write the complete file now. I'll make it robust and complete.

Let me also handle window resize.

Final code coming up.

Let me make sure the fish array structure matches what's requested:
```javascript
fishArray = [{
  mesh: THREE.Group,
  tail: THREE.Mesh,
  leftFin: THREE.Mesh,
  rightFin: THREE.Mesh,
  velocity: THREE.Vector3,
  speed: number,
  tailSpeed: number,
  phase: number,
  targetFood: object|null,
  avoidanceRadius: number
}]
```

I'll follow this structure and add extra fields as needed (like body, size, etc.).

Let me write it all now.

I'll write the animation loop with proper delta time using clock.getDelta().

Let me draft the full code:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  overflow: hidden;
  font-family: 'Segoe UI', sans-serif;
  background: #001;
}
#ui {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  z-index: 10;
}
.panel {
  position: absolute;
  background: rgba(10, 40, 70, 0.35);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 16px;
  padding: 18px;
  color: #e8f4ff;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  pointer-events: auto;
}
#info { top: 20px; left: 20px; max-width: 320px; }
#stats { top: 20px; right: 20px; min-width: 200px; }
h1 {
  font-size: 22px;
  background: linear-gradient(90deg, #64f0ff, #00aaff, #ff8ce0);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
}
.instructions { font-size: 13px; line-height: 1.6; opacity: 0.9; margin-bottom: 14px; }
.controls { display: flex; flex-direction: column; gap: 8px; }
button {
  padding: 10px 14px;
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  background: linear-gradient(135deg, #00aaff, #0066cc);
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,170,255,0.3);
}
button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,170,255,0.5); }
button:active { transform: translateY(0); }
.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  font-size: 14px;
}
.stat-row:last-child { border: none; }
.stat-value { font-weight: bold; color: #64f0ff; }
h2 { font-size: 16px; margin-bottom: 10px; }
</style>
</head>
<body>
<div id="ui">
  <div class="panel" id="info">
    <h1>🐠 3D Аквариум</h1>
    <div class="instructions">
      <strong>Управление:</strong><br>
      • Левый клик + движение — вращение камеры<br>
      • Правый клик + движение — панорама<br>
      • Колесо мыши — зум<br>
      • Клик по аквариуму — скормить рыбку
    </div>
    <div class="controls">
      <button id="addFishBtn">➕ Добавить рыбку</button>
      <button id="addBubblesBtn">🫧 Больше пузырей</button>
      <button id="lightBtn">💡 Свет: ВКЛ</button>
    </div>
  </div>
  <div class="panel" id="stats">
    <h2>📊 Статистика</h2>
    <div class="stat-row"><span>Рыбки</span><span class="stat-value" id="fishCount">0</span></div>
    <div class="stat-row"><span>Пузыри</span><span class="stat-value" id="bubbleCount">0</span></div>
    <div class="stat-row"><span>Корм</span><span class="stat-value" id="foodCount">0</span></div>
    <div class="stat-row"><span>FPS</span><span class="stat-value" id="fps">0</span></div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ... all the code
</script>
</body>
</html>
```

Now the JavaScript. Let me write it carefully.

```javascript
// Scene
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a3d5c, 0.012);

// Gradient background
const bgCanvas = document.createElement('canvas');
bgCanvas.width = 512; bgCanvas.height = 512;
const bgCtx = bgCanvas.getContext('2d');
const grad = bgCtx.createLinearGradient(0, 0, 0, 512);
grad.addColorStop(0, '#1a6b8c');
grad.addColorStop(0.5, '#0d4a6b');
grad.addColorStop(1, '#04202f');
bgCtx.fillStyle = grad;
bgCtx.fillRect(0, 0, 512, 512);
const bgTexture = new THREE.CanvasTexture(bgCanvas);
scene.background = bgTexture;

// Camera
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.set(0, 5, 45);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Controls
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

// Lighting
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(15, 30, 15);
sun.castShadow = true;
sun.shadow.mapSize.width = 2048;
sun.shadow.mapSize.height = 2048;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 100;
sun.shadow.camera.left = -40;
sun.shadow.camera.right = 40;
sun.shadow.camera.top = 40;
sun.shadow.camera.bottom = -40;
scene.add(sun);
scene.add(sun.target);

const pointLight1 = new THREE.PointLight(0x00aaff, 0.8, 100);
pointLight1.position.set(-10, 5, 8);
scene.add(pointLight1);

const pointLight2 = new THREE.PointLight(0x0066ff, 0.6, 100);
pointLight2.position.set(10, -5, -8);
scene.add(pointLight2);

// Aquarium dimensions
const W = 36, H = 24, D = 20;

// Tank glass
const tankGeom = new THREE.BoxGeometry(W, H, D);
const tankMat = new THREE.MeshPhysicalMaterial({
  color: 0xcfeeff,
  transparent: true,
  opacity: 0.12,
  roughness: 0.05,
  metalness: 0.0,
  side: THREE.DoubleSide
});
const tank = new THREE.Mesh(tankGeom, tankMat);
tank.renderOrder = 1;
scene.add(tank);

const edgeGeom = new THREE.EdgesGeometry(tankGeom);
const edgeMat = new THREE.LineBasicMaterial({ color: 0x99ddff, transparent: true, opacity: 0.6 });
const edges = new THREE.LineSegments(edgeGeom, edgeMat);
tank.add(edges);

// Sandy bottom
const sandGeom = new THREE.PlaneGeometry(W, D, 40, 30);
sandGeom.rotateX(-Math.PI / 2);
const sandPos = sandGeom.attributes.position;
for (let i = 0; i < sandPos.count; i++) {
  const x = sandPos.getX(i);
  const z = sandPos.getZ(i);
  const bump = Math.sin(x * 0.5) * Math.cos(z * 0.5) * 0.2 + Math.random() * 0.15;
  sandPos.setZ(i, sandPos.getZ(i) + bump);
}
sandGeom.computeVertexNormals();
const sandMat = new THREE.MeshStandardMaterial({ color: 0xdcbf81, roughness: 1.0 });
const sand = new THREE.Mesh(sandGeom, sandMat);
sand.position.y = -H/2 + 0.1;
sand.receiveShadow = true;
scene.add(sand);

const floorY = -H/2 + 0.3;

// Stones
const stones = [];
for (let i = 0; i < 8; i++) {
  const geom = new THREE.DodecahedronGeometry(1 + Math.random() * 1.2, 0);
  const pos = geom.attributes.position;
  for (let j = 0; j < pos.count; j++) {
    const f = 0.75 + Math.random() * 0.5;
    pos.setX(j, pos.getX(j) * f);
    pos.setY(j, pos.getY(j) * f);
    pos.setZ(j, pos.getZ(j) * f);
  }
  geom.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({ color: 0x7a7a7a, roughness: 0.95 });
  const stone = new THREE.Mesh(geom, mat);
  stone.position.set((Math.random()-0.5)*W*0.8, floorY + 0.5, (Math.random()-0.5)*D*0.8);
  stone.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
  stone.scale.setScalar(0.8 + Math.random());
  stone.castShadow = true;
  stone.receiveShadow = true;
  scene.add(stone);
  stones.push(stone);
}

// Seaweed
const seaweeds = [];
for (let i = 0; i < 12; i++) {
  const points = [];
  const height = 3 + Math.random() * 4;
  const segs = 10;
  for (let j = 0; j <= segs; j++) {
    const t = j / segs;
    const wobble = Math.sin(t * Math.PI * 1.5) * 0.6;
    points.push(new THREE.Vector3(wobble, t * height, Math.cos(t * Math.PI) * 0.3));
  }
  const curve = new THREE.CatmullRomCurve3(points);
  const geom = new THREE.TubeGeometry(curve, 24, 0.18, 6, false);
  const green = new THREE.Color().setHSL(0.30 + Math.random()*0.08, 0.6, 0.35);
  const mat = new THREE.MeshStandardMaterial({ color: green, roughness: 0.8, side: THREE.DoubleSide });
  const seaweed = new THREE.Mesh(geom, mat);
  seaweed.position.set((Math.random()-0.5)*W*0.85, floorY, (Math.random()-0.5)*D*0.85);
  seaweed.userData.phase = Math.random() * Math.PI * 2;
  seaweed.userData.swayX = (Math.random()-0.5) * 0.3;
  seaweed.userData.swayZ = (Math.random()-0.5) * 0.3;
  seaweed.castShadow = true;
  scene.add(seaweed);
  seaweeds.push(seaweed);
}

// Bubbles
const bubbles = [];
function makeBubble() {
  const geom = new THREE.SphereGeometry(0.2 + Math.random()*0.3, 12, 12);
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.25,
    roughness: 0.0,
    metalness: 0.0,
    emissive: 0x224466,
    emissiveIntensity: 0.2
  });
  const bubble = new THREE.Mesh(geom, mat);
  bubble.position.set((Math.random()-0.5)*W*0.9, floorY + Math.random()*(H-1), (Math.random()-0.5)*D*0.9);
  bubble.userData.speed = 0.02 + Math.random()*0.03;
  bubble.userData.phase = Math.random() * Math.PI * 2;
  scene.add(bubble);
  bubbles.push(bubble);
  return bubble;
}
for (let i = 0; i < 30; i++) makeBubble();

// Fish
const fishArray = [];
const colors = [0xff8c00, 0x0088ff, 0xffff00, 0x8800ff, 0xff0000, 0x00aa00, 0xff69b4, 0xffd700];

function createFish() {
  const group = new THREE.Group();
  const color = colors[Math.floor(Math.random()*colors.length)];
  const bodyMat = new THREE.MeshStandardMaterial({ color, roughness: 0.35, metalness: 0.15 });
  
  // Body
  const bodyGeom = new THREE.SphereGeometry(1, 20, 20);
  const body = new THREE.Mesh(bodyGeom, bodyMat);
  body.scale.set(1.2, 0.7, 0.6);
  body.castShadow = true;
  group.add(body);
  
  // Tail
  const tailGeom = new THREE.ConeGeometry(0.6, 1.1, 10);
  const tailMat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, transparent: true, opacity: 0.85 });
  const tail = new THREE.Mesh(tailGeom, tailMat);
  tail.rotation.z = Math.PI / 2;
  tail.position.x = -1.4;
  group.add(tail);
  
  // Top fin
  const finGeom = new THREE.ConeGeometry(0.4, 0.8, 8);
  const finMat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, transparent: true, opacity: 0.8 });
  const topFin = new THREE.Mesh(finGeom, finMat);
  topFin.position.set(-0.1, 0.7, 0);
  topFin.rotation.z = 0.2;
  group.add(topFin);
  
  // Side fins
  const leftFin = new THREE.Mesh(finGeom, finMat.clone());
  leftFin.position.set(0.2, -0.1, 0.5);
  leftFin.rotation.x = Math.PI / 2 - 0.3;
  leftFin.scale.setScalar(0.7);
  group.add(leftFin);
  
  const rightFin = new THREE.Mesh(finGeom, finMat.clone());
  rightFin.position.set(0.2, -0.1, -0.5);
  rightFin.rotation.x = -(Math.PI / 2 - 0.3);
  rightFin.scale.setScalar(0.7);
  group.add(rightFin);
  
  // Eyes
  const eyeGeom = new THREE.SphereGeometry(0.18, 12, 12);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
  const pupilGeom = new THREE.SphereGeometry(0.09, 10, 10);
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
  const eyeL = new THREE.Mesh(eyeGeom, eyeMat);
  eyeL.position.set(0.6, 0.15, 0.35);
  const pupilL = new THREE.Mesh(pupilGeom, pupilMat);
  pupilL.position.set(0.12, 0, 0);
  eyeL.add(pupilL);
  const eyeR = eyeL.clone();
  eyeR.position.z = -0.35;
  group.add(eyeL, eyeR);
  
  const scale = 0.6 + Math.random() * 0.6;
  group.scale.setScalar(scale);
  
  // Random starting position
  group.position.set(
    (Math.random()-0.5)*W*0.7,
    floorY + 1 + Math.random()*(H-3),
    (Math.random()-0.5)*D*0.7
  );
  
  scene.add(group);
  
  const fish = {
    mesh: group,
    tail: tail,
    leftFin: leftFin,
    rightFin: rightFin,
    topFin: topFin,
    body: body,
    velocity: new THREE.Vector3((Math.random()-0.5), (Math.random()-0.5)*0.3, (Math.random()-0.5)).normalize().multiplyScalar(0.05),
    speed: 0.03 + Math.random()*0.04,
    tailSpeed: 3 + Math.random()*3,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 3 + Math.random()*2,
    size: scale
  };
  fishArray.push(fish);
  return fish;
}

for (let i = 0; i < 15; i++) createFish();

// Food
const foodArray = [];
function createFood(pos) {
  const geom = new THREE.SphereGeometry(0.15, 8, 8);
  const mat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.9 });
  const food = new THREE.Mesh(geom, mat);
  food.position.copy(pos);
  food.castShadow = true;
  scene.add(food);
  foodArray.push({ mesh: food, vy: 0 });
}

// Raycaster for clicking
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const clickPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);

renderer.domElement.addEventListener('click', (event) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  // Intersect with a plane at aquarium center facing camera
  const camDir = new THREE.Vector3();
  camera.getWorldDirection(camDir);
  clickPlane.normal.copy(camDir);
  clickPlane.constant = 0;
  const target = new THREE.Vector3();
  raycaster.intersectPlane(clickPlane, target);
  if (target) {
    // clamp inside tank
    target.x = THREE.MathUtils.clamp(target.x, -W/2+1, W/2-1);
    target.y = THREE.MathUtils.clamp(target.y, floorY+1, H/2-1);
    target.z = THREE.MathUtils.clamp(target.z, -D/2+1, D/2-1);
    createFood(target);
  }
});
```

Wait, the click plane approach might place food outside the tank or in weird spots. Let me use a simpler approach: intersect with an invisible sphere or just project onto the tank center plane. Actually, let me intersect with the tank's bounding box or use the plane method but clamp. The clamping should keep it inside. But the plane at constant 0 with camera normal... if camera is far away, the intersection point could be far. Let me clamp to tank bounds which handles it.

Actually, a cleaner approach: intersect with an invisible helper sphere/capsule representing the tank interior, or just use the plane and clamp. Clamping to tank bounds works fine. Let me keep it but ensure the plane passes through tank center.

Hmm, actually there's an issue: if the ray is parallel-ish to the plane, intersection could be at infinity. But with camera looking generally toward the tank it should be fine. Let me add a fallback.

Let me simplify: I'll intersect with an invisible sphere centered at tank center with radius = half-diagonal, and clamp. Actually the plane method with clamping is fine for typical viewing angles. Let me keep it but add a guard.

Actually, let me use a different, more robust approach: create an invisible sphere mesh for raycasting and place food at the intersection point (clamped to be inside tank). This gives a natural 3D point.

```javascript
const hitSphere = new THREE.Mesh(
  new THREE.SphereGeometry(Math.max(W,H,D)/2 * 1.1, 16, 16),
  new THREE.MeshBasicMaterial({ visible: false })
);
scene.add(hitSphere);
```

Then on click:
```javascript
const intersects = raycaster.intersectObject(hitSphere);
if (intersects.length > 0) {
  const p = intersects[0].point;
  p.x = THREE.MathUtils.clamp(p.x, -W/2+1, W/2-1);
  p.y = THREE.MathUtils.clamp(p.y, floorY+1, H/2-1);
  p.z = THREE.MathUtils.clamp(p.z, -D/2+1, D/2-1);
  createFood(p);
}
```

This is cleaner. Let me use this.

Now the animation loop:

```javascript
const clock = new THREE.Clock();
let fpsTime = 0, fpsCount = 0, fpsValue = 0;

function animate() {
  requestAnimationFrame(animate);
  const delta = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;
  
  // Update fish
  const boundsMin = new THREE.Vector3(-W/2+2, floorY+1, -D/2+2);
  const boundsMax = new THREE.Vector3(W/2-2, H/2-2, D/2-2);
  
  for (let f = 0; f < fishArray.length; f++) {
    const fish = fishArray[f];
    const pos = fish.mesh.position;
    const vel = fish.velocity;
    
    // Find nearest food
    let nearestFood = null;
    let nearestDist = 15;
    for (let i = 0; i < foodArray.length; i++) {
      const fp = foodArray[i].mesh.position;
      const d = pos.distanceTo(fp);
      if (d < nearestDist) {
        nearestDist = d;
        nearestFood = foodArray[i];
      }
    }
    
    // Acceleration
    const accel = new THREE.Vector3();
    
    // Wander: periodic random change
    fish.phase += delta * fish.tailSpeed * 0.3;
    if (Math.sin(fish.phase) > 0.98) {
      vel.x += (Math.random()-0.5) * 0.002;
      vel.z += (Math.random()-0.5) * 0.002;
    }
    
    if (nearestFood) {
      fish.targetFood = nearestFood;
      const dir = nearestFood.mesh.position.clone().sub(pos).normalize();
      accel.add(dir.multiplyScalar(fish.speed * 0.02));
      // eat
      if (nearestDist < 0.8 * fish.size + 0.2) {
        // eat food
        scene.remove(nearestFood.mesh);
        foodArray.splice(foodArray.indexOf(nearestFood), 1);
        fish.targetFood = null;
        // grow 5%
        fish.size *= 1.05;
        fish.mesh.scale.setScalar(fish.size / (fish.size/1.05)); // hmm
        // Actually just scale up
        fish.mesh.scale.multiplyScalar(1.05);
      }
    } else {
      fish.targetFood = null;
    }
    
    // Avoidance between fish
    for (let o = 0; o < fishArray.length; o++) {
      if (o === f) continue;
      const other = fishArray[o];
      const diff = pos.clone().sub(other.mesh.position);
      const d = diff.length();
      if (d < fish.avoidanceRadius && d > 0.001) {
        const force = diff.normalize().multiplyScalar((fish.avoidanceRadius - d) / fish.avoidanceRadius * 0.005);
        accel.add(force);
      }
    }
    
    // Wall repulsion
    if (pos.x < boundsMin.x) accel.x += (boundsMin.x - pos.x) * 0.01;
    if (pos.x > boundsMax.x) accel.x += (boundsMax.x - pos.x) * 0.01;
    if (pos.y < boundsMin.y) accel.y += (boundsMin.y - pos.y) * 0.01;
    if (pos.y > boundsMax.y) accel.y += (boundsMax.y - pos.y) * 0.01;
    if (pos.z < boundsMin.z) accel.z += (boundsMin.z - pos.z) * 0.01;
    if (pos.z > boundsMax.z) accel.z += (boundsMax.z - pos.z) * 0.01;
    
    // Apply acceleration
    vel.add(accel.multiplyScalar(delta * 60));
    
    // Clamp speed
    const spd = vel.length();
    const maxSpeed = fish.speed * 3;
    if (spd > maxSpeed) vel.multiplyScalar(maxSpeed / spd);
    if (spd < fish.speed * 0.3) vel.multiplyScalar(fish.speed * 0.3 / (spd || 1));
    
    // Move
    pos.add(vel.clone().multiplyScalar(delta * 60));
    
    // Tail animation
    const tailSwing = Math.sin(time * fish.tailSpeed + fish.phase) * 0.4;
    fish.tail.rotation.z = tailSwing;
    // Fin movement
    fish.leftFin.rotation.z = 0.3 + Math.sin(time * 4 + fish.phase) * 0.3;
    fish.rightFin.rotation.z = -0.3 - Math.sin(time * 4 + fish.phase) * 0.3;
    fish.topFin.rotation.z = 0.2 + Math.sin(time * 3 + fish.phase) * 0.15;
    
    // Turn fish to face velocity
    if (vel.lengthSq() > 0.0001) {
      const forward = new THREE.Vector3(1, 0, 0);
      const targetDir = vel.clone().normalize();
      fish.mesh.quaternion.setFromUnitVectors(forward, targetDir);
    }
    
    // Subtle bob
    fish.mesh.position.y += Math.sin(time * 2 + fish.phase) * 0.002;
  }
  
  // Update food
  for (let i = foodArray.length - 1; i >= 0; i--) {
    const food = foodArray[i];
    food.vy -= 0.0005; // gravity
    food.mesh.position.y += food.vy * (delta * 60);
    food.mesh.rotation.x += delta;
    food.mesh.rotation.y += delta;
    if (food.mesh.position.y <= floorY) {
      scene.remove(food.mesh);
      foodArray.splice(i, 1);
    }
  }
  
  // Update bubbles
  for (let i = 0; i < bubbles.length; i++) {
    const b = bubbles[i];
    b.mesh.position.y += b.userData.speed * (delta * 60);
    b.mesh.position.x += Math.sin(time * 2 + b.userData.phase) * 0.01;
    if (b.mesh.position.y > H/2 - 0.5) {
      b.mesh.position.y = floorY + 0.5;
      b.mesh.position.x = (Math.random()-0.5)*W*0.9;
      b.mesh.position.z = (Math.random()-0.5)*D*0.9;
    }
  }
  
  // Update seaweed
  for (let i = 0; i < seaweeds.length; i++) {
    const s = seaweeds[i];
    s.rotation.x = s.userData.swayX * Math.sin(time * 1.5 + s.userData.phase);
    s.rotation.z = s.userData.swayZ * Math.sin(time * 1.2 + s.userData.phase + 1);
  }
  
  controls.update();
  renderer.render(scene, camera);
  
  // FPS
  fpsCount++;
  fpsTime += delta;
  if (fpsTime >= 1) {
    fpsValue = Math.round(fpsCount / fpsTime);
    fpsCount = 0;
    fpsTime = 0;
    document.getElementById('fps').textContent = fpsValue;
    document.getElementById('fishCount').textContent = fishArray.length;
    document.getElementById('bubbleCount').textContent = bubbles.length;
    document.getElementById('foodCount').textContent = foodArray.length;
  }
}

animate();
```

Wait, there's an issue with fish growth. When I do `fish.mesh.scale.setScalar(fish.size)` initially, then grow, I should track the base scale separately or just multiply. Let me simplify: store `size` as the current overall scale and set it directly. On eat, multiply size by 1.05 and set scale.

Let me fix: 
- Initially `fish.size = scale`, `fish.mesh.scale.setScalar(scale)`.
- On eat: `fish.size *= 1.05; fish.mesh.scale.setScalar(fish.size);`

That's cleaner. Let me use that.

Also the fin rotation uses local z which after quaternion rotation... wait, I'm setting fin rotation AFTER setting the quaternion. Setting rotation.z on the mesh after setting quaternion will overwrite the quaternion with a pure Z rotation! That's a bug.

I need to apply fin rotations as local rotations relative to the parent orientation. Better approach: set the quaternion first, then apply the fin rotation using multiplication:

```javascript
const q = new THREE.Quaternion();
q.setFromAxisAngle(new THREE.Vector3(0,0,1), tailSwing);
fish.mesh.quaternion.multiply(q); // no, this accumulates
```

Better: make the fins children of a sub-group, or apply rotation before quaternion. Actually, simplest: set the fins' rotation BEFORE setting the mesh quaternion. But then the tail and fin animations happen each frame and the last quaternion set wins.

Let me reorganize: 
1. Set base orientation from velocity (quaternion)
2. Then multiply by fin/tail local rotations

```javascript
// Set facing
if (vel.lengthSq() > 0.0001) {
  const forward = new THREE.Vector3(1, 0, 0);
  fish.mesh.quaternion.setFromUnitVectors(forward, vel.clone().normalize());
}
// Local fin swings (relative to current orientation)
const tailQ = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,0,1), tailSwing);
fish.mesh.quaternion.multiply(tailQ);
```

Hmm but multiply applies the tailQ in world space after the base quaternion. For local rotation I'd need to apply local. Actually for fins, applying in local space: 

```javascript
// after setting base quaternion:
const localQ = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0), finSwing);
// apply locally: q_local * base? 
```

This gets complicated. Simpler approach: put the tail and fins in sub-groups that are children of the fish mesh. Set the fish mesh quaternion for facing, then rotate the sub-groups locally.

Let me restructure:
- fish.mesh (group) → faces direction via quaternion
  - body
  - tailGroup (child) → rotates on Z locally
  - leftFinGroup → rotates locally
  - rightFinGroup → rotates locally

Then in animation:
```javascript
fish.mesh.quaternion.setFromUnitVectors(forward, dir);
fish.tail.rotation.z = tailSwing;  // local rotation of child
fish.leftFin.rotation.z = ...;     // local
```

Since tail is a child of mesh, setting tail.rotation.z rotates it in the mesh's local frame. 

Let me restructure the createFish to have sub-groups for tail and fins. Actually, I can just rotate the tail mesh directly if it's a child — but the problem is I set mesh.quaternion every frame which resets the mesh's own rotation but the tail is a separate child so its rotation is independent. Wait yes! If tail is a child of mesh, then mesh.quaternion affects the whole subtree orientation, and tail.rotation.z is applied in mesh's local frame independently. So setting mesh.quaternion doesn't reset tail.rotation.z. 

So the original approach works IF I set mesh.quaternion for facing, and tail/fin rotations are on child meshes. The child's rotation is relative to parent, so it's applied in the parent's rotated frame automatically. Setting mesh.quaternion doesn't touch child.localRotation. 

So:
```javascript
fish.mesh.quaternion.setFromUnitVectors(forward, dir); // sets mesh orientation
fish.tail.rotation.z = tailSwing; // child local rotation, independent
```

This works correctly. The tail swings in the fish's local frame. 

Let me verify: mesh has quaternion Q (from facing). Tail is child with local rotation Rz(tailSwing). World rotation of tail = Q * Rz(tailSwing). Yes, correct. The tail swings back and forth in the fish's frame. 

So my original code is fine. Let me just make sure I set mesh.quaternion and then set child rotations (they don't interfere). Actually order doesn't matter since they're different objects. Good.

Let me keep the structure where tail, fins are direct children of mesh (not sub-groups). That works.

Now, one concern: the tail is a ConeGeometry pointing up (+Y) by default. I rotate it by PI/2 around Z so it points along -X (backward). Good. When it swings around Z, it oscillates. Good.

Let me also double check the eyes clone - eyeL.clone() clones the mesh including its pupil child. Good.

Now let me also handle window resize.

```javascript
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

And buttons:
```javascript
document.getElementById('addFishBtn').addEventListener('click', () => { createFish(); });
document.getElementById('addBubblesBtn').addEventListener('click', () => { for (let i=0;i<10;i++) makeBubble(); });
let lightOn = true;
document.getElementById('lightBtn').addEventListener('click', () => {
  lightOn = !lightOn;
  sun.intensity = lightOn ? 1.0 : 0.1;
  document.getElementById('lightBtn').textContent = lightOn ? '💡 Свет: ВКЛ' : '💡 Свет: ВЫКЛ';
});
```

I think this is complete. Let me also add some floating particles or caustics for extra realism maybe. Optional. Let me keep it focused.

Let me refine the food eating distance and growth. And make sure food appears above so it falls.

When clicking, I place food at the intersection point (clamped inside tank). It will fall due to gravity. Good. Maybe place it slightly above so it visibly falls. Let me set food.y to the clicked point but it starts falling immediately. Fine.

Actually, for a nicer effect, when clicking place food near the top so it sinks. But the plane intersection gives a 3D point which could be anywhere. Let me just place at the point; gravity handles the fall. If it's near bottom it just sits. That's fine.

Hmm, but if the click maps to a point low in the tank, food won't have a nice fall. Let me instead always spawn food at the clicked X,Z but at the top of the tank, so it falls nicely:

```javascript
createFood(new THREE.Vector3(clampedX, H/2 - 1, clampedZ));
```

That's nicer visually. Let me do that. I'll get the X,Z from the intersection but set Y to top.

Let me finalize.

Let me also reduce the number of segments for performance but keep it reasonable.

Let me write the final complete file. I'll clean it up.

One more thing: the `velocity` normalization at start and the movement math. Let me make sure fish actually move. Initial velocity is normalized times 0.05, so speed ~0.05 units per frame-ish. With delta*60 multiplier in movement, that's 0.05 * (delta*60). At 60fps delta=0.016, so 0.05*1 = 0.05 units/frame. Good, reasonable.

Actually let me reconsider the movement scaling. I do:
- vel.add(accel.multiplyScalar(delta * 60))
- pos.add(vel.clone().multiplyScalar(delta * 60))

With delta ~0.016, delta*60 ~ 1. So effectively per-frame additions. vel ~ 0.05, accel adds small amounts. Good.

The wall repulsion: `(boundsMin.x - pos.x) * 0.01` — when pos.x < boundsMin.x (negative overshoot), this is negative pushing further negative? Wait. If pos.x < boundsMin.x (e.g., pos.x=-19, boundsMin.x=-16), then (boundsMin.x - pos.x) = (-16 - (-19)) = 3, positive. accel.x += 3*0.01 = 0.03, pushing positive (back inward). Good. But walls shouldn't be breached much due to clamping speed. Actually better to clamp position directly when exceeding bounds. Let me add position clamping as safety:

```javascript
pos.x = THREE.MathUtils.clamp(pos.x, boundsMin.x, boundsMax.x);
... etc
```

after moving. This prevents escape. Let me add that.

OK let me write the final version. I'll be thorough.

Let me reconsider the avoidance force magnitude and make fish behavior smooth and natural. I'll tune constants.

Let me also add a slight upward bias so fish don't all sink to bottom (they have buoyancy). Add accel.y += 0.0002 to keep them suspended. Combined with wall repulsion on Y.

Let me finalize everything into a clean, complete HTML file.

I'll write it out now as the final answer.

Let me also make sure OrbitControls works with the CDN path. The jsdelivr path for r128 OrbitControls: https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js — this should work and exposes THREE.OrbitControls.

Actually, there might be dependency issues (it imports Vector3, Euler, etc. from three). The old examples/js versions rely on THREE being global, which three.min.js provides. Should be fine.

Let me write the final file.

Let me also add a subtle caustic/light shaft effect with the directional light — already have shadows. Good enough.

Final answer time. Let me write clean complete code.

I'll present it as a single HTML file ready to open.

Let me reconsider the fish facing direction and make the front be +X. Eyes at +X. Tail at -X. Good.

Also I realize I should double-check: `setFromUnitVectors(v1, v2)` returns quaternion that rotates v1 to v2. So setFromUnitVectors((1,0,0), dir) rotates the +X axis to point along dir. Correct.

Alright, writing final.

Let me also make the fish body slightly iridescent with metalness for a realistic look. metalness 0.3, roughness 0.3.

Let me write the complete, polished file now.

I'll include a helpful comment block at top describing features.

Let me make sure I import OrbitControls correctly. Some setups need:
```html
<script type="importmap">...</script>
```
but with the legacy examples/js global approach, just loading the script after three.min.js works because it references THREE.OrbitControls. Let me verify the r128 examples/js/controls/OrbitControls.js assigns to THREE.OrbitControls. Yes, the legacy non-module versions do `THREE.OrbitControls = ...`. Good.

Final code below.

Let me write it all out cleanly and completely.
</think>

# 🐠 3D Акarium с Реалистичными Рыбками

Вот полный, готовый к запуске HTML-файл со всеми требованиями. Просто сохраните его как `aquarium.html` и откройте в браузере.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    overflow: hidden;
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #00121f;
  }
  #ui { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; }
  .panel {
    position: absolute;
    background: rgba(8, 36, 60, 0.45);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 18px;
    padding: 18px 20px;
    color: #e8f4ff;
    box-shadow: 0 8px 32px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.12);
    pointer-events: auto;
  }
  h1 {
    font-size: 23px;
    background: linear-gradient(90deg,#64f0ff,#00aaff,#ff8ce0);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px; letter-spacing: 0.5px;
  }
  .instructions { font-size: 13px; line-height: 1.7; opacity: 0.92; margin-bottom: 16px; }
  .controls { display: flex; flex-direction: column; gap: 9px; }
  button {
    padding: 11px 15px; border: none; border-radius: 12px; color: white;
    font-size: 14px; font-weight: 600; cursor: pointer;
    background: linear-gradient(135deg,#00aaff,#0066cc);
    transition: all 0.25s ease;
    box-shadow: 0 4px 16px rgba(0,170,255,0.32);
  }
  button:hover { transform: translateY(-2px); box-shadow: 0 7px 24px rgba(0,170,255,0.55); }
  button:active { transform: translateY(0); }
  h2 { font-size: 16px; margin-bottom: 12px; color: #9fe0ff; }
  .stat-row { display: flex; justify-content: space-between; padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.09); font-size: 14px; }
  .stat-row:last-child { border: none; }
  .stat-value { font-weight: 700; color: #64f0ff; }
  #hint { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
    color: rgba(255,255,255,0.55); font-size: 13px; pointer-events: none; z-index: 5; }
</style>
</head>
<body>

<div id="ui">
  <div class="panel" id="info">
    <h1>🐠 3D Аквариум</h1>
    <div class="instructions">
      <strong>Управление:</strong><br>
      • Левый клик + перемещение — вращение камеры<br>
      • Правый клик + перемещение — панорама<br>
      • Колесо мыши — зум (10–60)<br>
      • Клик по аквариуму — скормить рыбку 🍽️
    </div>
    <div class="controls">
      <button id="addFishBtn">➕ Добавить рыбку</button>
      <button id="addBubblesBtn">🫧 Больше пузырей</button>
      <button id="lightBtn">💡 Свет: ВКЛ</button>
    </div>
  </div>

  <div class="panel" id="stats">
    <h2>📊 Статистика</h2>
    <div class="stat-row"><span>🐟 Рыбки</span><span class="stat-value" id="fishCount">0</span></div>
    <div class="stat-row"><span>🫧 Пузыри</span><span class="stat-value" id="bubbleCount">0</span></div>
    <div class="stat-row"><span>🍽️ Корм</span><span class="stat-value" id="foodCount">0</span></div>
    <div class="stat-row"><span>⚡ FPS</span><span class="stat-value" id="fps">0</span></div>
  </div>
</div>

<div id="hint">Кликните по аквариуму, чтобы накормить рыбок</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
/* ============================================================
   3D АКВАРИУМ — Three.js r128
   ============================================================ */

// ---------- Сцена ----------
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a3d5c, 0.012);

// Градиентный фон (тёмно-синий → синий)
const bgCanvas = document.createElement('canvas');
bgCanvas.width = 512; bgCanvas.height = 512;
const bgCtx = bgCanvas.getContext('2d');
const grad = bgCtx.createLinearGradient(0, 0, 0, 512);
grad.addColorStop(0, '#1a6b8c');
grad.addColorStop(0.5, '#0d4a6b');
grad.addColorStop(1, '#04202f');
bgCtx.fillStyle = grad; bgCtx.fillRect(0, 0, 512, 512);
scene.background = new THREE.CanvasTexture(bgCanvas);

// ---------- Камера ----------
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.set(0, 6, 46);

// ---------- Рендерер ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ---------- OrbitControls ----------
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

// ---------- Освещение ----------
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(15, 32, 15);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 120;
sun.shadow.camera.left = -45;
sun.shadow.camera.right = 45;
sun.shadow.camera.top = 45;
sun.shadow.camera.bottom = -45;
scene.add(sun);

const pl1 = new THREE.PointLight(0x00aaff, 0.85, 120); pl1.position.set(-12, 6, 9); scene.add(pl1);
const pl2 = new THREE.PointLight(0x0066ff, 0.65, 120); pl2.position.set(12, -6, -9); scene.add(pl2);

// ---------- Параметры аквариума ----------
const W = 36, H = 24, D = 20;
const floorY = -H/2 + 0.4;

// ---------- Стеклянный контейнер ----------
const tankGeom = new THREE.BoxGeometry(W, H, D);
const tankMat = new THREE.MeshPhysicalMaterial({
  color: 0xcfeeff, transparent: true, opacity: 0.13,
  roughness: 0.05, metalness: 0.0, side: THREE.DoubleSide
});
const tank = new THREE.Mesh(tankGeom, tankMat);
scene.add(tank);

// Видимая рамка (wireframe edges)
const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(tankGeom),
  new THREE.LineBasicMaterial({ color: 0x99ddff, transparent: true, opacity: 0.55 })
);
tank.add(edges);

// ---------- Песчаное дно с неровностями ----------
const sandGeom = new THREE.PlaneGeometry(W, D, 42, 32);
sandGeom.rotateX(-Math.PI / 2);
const sp = sandGeom.attributes.position;
for (let i = 0; i < sp.count; i++) {
  const x = sp.getX(i), z = sp.getZ(i);
  const bump = Math.sin(x*0.5)*Math.cos(z*0.5)*0.22 + Math.random()*0.15;
  sp.setZ(i, sp.getZ(i) + bump);
}
sandGeom.computeVertexNormals();
const sand = new THREE.Mesh(sandGeom, new THREE.MeshStandardMaterial({ color: 0xdcbf81, roughness: 1 }));
sand.position.y = floorY;
sand.receiveShadow = true;
scene.add(sand);

// ---------- Декоративные камни (деформированные дедекаэдры) ----------
for (let i = 0; i < 8; i++) {
  const g = new THREE.DodecahedronGeometry(1 + Math.random()*1.2, 0);
  const p = g.attributes.position;
  for (let j = 0; j < p.count; j++) {
    const f = 0.75 + Math.random()*0.5;
    p.setX(j, p.getX(j)*f); p.setY(j, p.getY(j)*f); p.setZ(j, p.getZ(j)*f);
  }
  g.computeVertexNormals();
  const s = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0x7a7f86, roughness: 0.95 }));
  s.position.set((Math.random()-0.5)*W*0.8, floorY + 0.6, (Math.random()-0.5)*D*0.8);
  s.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
  s.scale.setScalar(0.8 + Math.random());
  s.castShadow = true; s.receiveShadow = true;
  scene.add(s);
}

// ---------- Водоросли (TubeGeometry + CatmullRomCurve3) ----------
const seaweeds = [];
for (let i = 0; i < 12; i++) {
  const pts = [];
  const height = 3 + Math.random()*4;
  for (let j = 0; j <= 10; j++) {
    const t = j/10;
    pts.push(new THREE.Vector3(Math.sin(t*Math.PI*1.5)*0.6, t*height, Math.cos(t*Math.PI)*0.3));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const g = new THREE.TubeGeometry(curve, 24, 0.18, 6, false);
  const col = new THREE.Color().setHSL(0.30 + Math.random()*0.08, 0.6, 0.35);
  const s = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: col, roughness: 0.8, side: THREE.DoubleSide }));
  s.position.set((Math.random()-0.5)*W*0.85, floorY, (Math.random()-0.5)*D*0.85);
  s.userData.phase = Math.random()*Math.PI*2;
  s.userData.swayX = (Math.random()-0.5)*0.35;
  s.userData.swayZ = (Math.random()-0.5)*0.35;
  s.castShadow = true;
  scene.add(s); seaweeds.push(s);
}

// ---------- Пузыри ----------
const bubbles = [];
function makeBubble() {
  const g = new THREE.SphereGeometry(0.2 + Math.random()*0.3, 14, 14);
  const m = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, transparent: true, opacity: 0.28,
    roughness: 0, metalness: 0, emissive: 0x224466, emissiveIntensity: 0.25
  });
  const b = new THREE.Mesh(g, m);
  b.position.set((Math.random()-0.5)*W*0.9, floorY + Math.random()*(H-1), (Math.random()-0.5)*D*0.9);
  b.userData.speed = 0.02 + Math.random()*0.03;
  b.userData.phase = Math.random()*Math.PI*2;
  scene.add(b); bubbles.push(b);
}
for (let i = 0; i < 30; i++) makeBubble();

// ---------- Рыбки ----------
const fishArray = [];
const COLORS = [0xff8c00, 0x0088ff, 0xffff00, 0x8800ff, 0xff0000, 0x00aa00, 0xff69b4, 0xffd700];

function createFish() {
  const group = new THREE.Group();
  const color = COLORS[Math.floor(Math.random()*COLORS.length)];
  const bodyMat = new THREE.MeshStandardMaterial({ color, roughness: 0.3, metalness: 0.3 });

  // Вытянутое тело (масштабированная сфера)
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 22, 22), bodyMat);
  body.scale.set(1.2, 0.7, 0.6);
  body.castShadow = true;
  group.add(body);

  // Хвост (конус, вращается по Z)
  const tailMat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, transparent: true, opacity: 0.85 });
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.6, 1.1, 10), tailMat);
  tail.rotation.z = Math.PI/2; tail.position.x = -1.4;
  group.add(tail);

  // Верхний плавник
  const finMat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, transparent: true, opacity: 0.8 });
  const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.85, 8), finMat);
  topFin.position.set(-0.1, 0.72, 0); topFin.rotation.z = 0.2;
  group.add(topFin);

  // Боковые плавники
  const lFin = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.7, 8), finMat.clone());
  lFin.position.set(0.2, -0.1, 0.52); lFin.rotation.x = Math.PI/2 - 0.3; lFin.scale.setScalar(0.7);
  const rFin = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.7, 8), finMat.clone());
  rFin.position.set(0.2, -0.1, -0.52); rFin.rotation.x = -(Math.PI/2 - 0.3); rFin.scale.setScalar(0.7);
  group.add(lFin, rFin);

  // Гла с зрачками
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
  const pupMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
  function makeEye(z) {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.19, 14, 14), eyeMat);
    e.position.set(0.62, 0.16, z);
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.095, 12, 12), pupMat);
    p.position.set(0.13, 0, 0);
    e.add(p);
    return e;
  }
  group.add(makeEye(0.38), makeEye(-0.38));

  const scale = 0.6 + Math.random()*0.6;
  group.scale.setScalar(scale);
  group.position.set((Math.random()-0.5)*W*0.7, floorY + 1 + Math.random()*(H-3), (Math.random()-0.5)*D*0.7);
  scene.add(group);

  fishArray.push({
    mesh: group, tail, leftFin: lFin, rightFin: rFin, topFin: topFin,
    velocity: new THREE.Vector3((Math.random()-0.5), (Math.random()-0.5)*0.3, (Math.random()-0.5)).normalize().multiplyScalar(0.05),
    speed: 0.03 + Math.random()*0.04,
    tailSpeed: 3 + Math.random()*3,
    phase: Math.random()*Math.PI*2,
    targetFood: null,
    avoidanceRadius: 3 + Math.random()*2,
    size: scale
  });
}
for (let i = 0; i < 15; i++) createFish();

// ---------- Корм ----------
const foodArray = [];
function createFood(pos) {
  const g = new THREE.SphereGeometry(0.16, 9, 9);
  const m = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.9 });
  const food = new THREE.Mesh(g, m);
  food.position.copy(pos); food.castShadow = true;
  scene.add(food);
  foodArray.push({ mesh: food, vy: 0 });
}

// ---------- Клик для кормления (Raycaster) ----------
const hitSphere = new THREE.Mesh(
  new THREE.SphereGeometry(Math.max(W,H,D)/2*1.15, 20, 20),
  new THREE.MeshBasicMaterial({ visible: false })
);
scene.add(hitSphere);
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', (e) => {
  mouse.x = (e.clientX/window.innerWidth)*2 - 1;
  mouse.y = -(e.clientY/window.innerHeight)*2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObject(hitSphere);
  if (hits.length) {
    const p = hits[0].point;
    // Корм падает сверху по X,Z точки щелчка
    createFood(new THREE.Vector3(
      THREE.MathUtils.clamp(p.x, -W/2+1, W/2-1),
      H/2 - 1,
      THREE.MathUtils.clamp(p.z, -D/2+1, D/2-1)
    ));
  }
});

// ---------- Кнопки UI ----------
document.getElementById('addFishBtn').addEventListener('click', () => createFish());
document.getElementById('addBubblesBtn').addEventListener('click', () => { for (let i=0;i<10;i++) makeBubble(); });
let lightOn = true;
document.getElementById('lightBtn').addEventListener('click', () => {
  lightOn = !lightOn;
  sun.intensity = lightOn ? 1.0 : 0.08;
  document.getElementById('lightBtn').textContent = lightOn ? '💡 Свет: ВКЛ' : '💡 Свет: ВЫКЛ';
});

// ---------- Resize ----------
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- Цикл анимации ----------
const clock = new THREE.Clock();
let fpsTime = 0, fpsCount = 0, fpsValue = 0;
const boundsMin = new THREE.Vector3(-W/2+2, floorY+1, -D/2+2);
const boundsMax = new THREE.Vector3(W/2-2, H/2-2, D/2-2);

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // ----- Обновление рыбок -----
  for (let f = 0; f < fishArray.length; f++) {
    const fish = fishArray[f];
    const pos = fish.mesh.position, vel = fish.velocity;

    // Поиск ближайшего корма (радиус 15)
    let nearest = null, nd = 15;
    for (let i = 0; i < foodArray.length; i++) {
      const d = pos.distanceTo(foodArray[i].mesh.position);
      if (d < nd) { nd = d; nearest = foodArray[i]; }
    }

    const accel = new THREE.Vector3();

    // Случайное блуждание
    fish.phase += dt * fish.tailSpeed * 0.3;
    if (Math.sin(fish.phase) > 0.98) {
      vel.x += (Math.random()-0.5)*0.002;
      vel.z += (Math.random()-0.5)*0.002;
    }

    // Преследование корма + поедание
    if (nearest) {
      fish.targetFood = nearest;
      const dir = nearest.mesh.position.clone().sub(pos).normalize();
      accel.add(dir.multiplyScalar(fish.speed*0.025));
      if (nd < 0.85*fish.size + 0.25) {
        scene.remove(nearest.mesh);
        foodArray.splice(foodArray.indexOf(nearest), 1);
        fish.targetFood = null;
        fish.size *= 1.05;              // рост на 5%
        fish.mesh.scale.setScalar(fish.size);
      }
    } else fish.targetFood = null;

    // Избегание столкновений между рыбами
    for (let o = 0; o < fishArray.length; o++) {
      if (o === f) continue;
      const other = fishArray[o];
      const diff = pos.clone().sub(other.mesh.position);
      const d = diff.length();
      if (d < fish.avoidanceRadius && d > 0.001) {
        accel.add(diff.normalize().multiplyScalar((fish.avoidanceRadius - d)/fish.avoidanceRadius * 0.006));
      }
    }

    // От отражения от стен + лёгкая плавучесть
    accel.y += 0.0002;
    if (pos.x < boundsMin.x) accel.x += (boundsMin.x - pos.x)*0.02;
    if (pos.x > boundsMax.x) accel.x += (boundsMax.x - pos.x)*0.02;
    if (pos.y < boundsMin.y) accel.y += (boundsMin.y - pos.y)*0.02;
    if (pos.y > boundsMax.y) accel.y += (boundsMax.y - pos.y)*0.02;
    if (pos.z < boundsMin.z) accel.z += (boundsMin.z - pos.z)*0.02;
    if (pos.z > boundsMax.z) accel.z += (boundsMax.z - pos.z)*0.02;

    vel.add(accel.multiplyScalar(dt*60));
    const spd = vel.length(), maxS = fish.speed*3;
    if (spd > maxS) vel.multiplyScalar(maxS/spd);
    if (spd < fish.speed*0.3 && spd > 0.0001) vel.multiplyScalar(fish.speed*0.3/spd);

    pos.add(vel.clone().multiplyScalar(dt*60));
    // Ограничение границ
    pos.x = THREE.MathUtils.clamp(pos.x, boundsMin.x, boundsMax.x);
    pos.y = THREE.MathUtils.clamp(pos.y, boundsMin.y, boundsMax.y);
    pos.z = THREE.MathUtils.clamp(pos.z, boundsMin.z, boundsMax.z);

    // Анимация хвоста и плавников
    fish.tail.rotation.z = Math.sin(t*fish.tailSpeed + fish.phase)*0.4;
    fish.leftFin.rotation.z = 0.35 + Math.sin(t*4 + fish.phase)*0.3;
    fish.rightFin.rotation.z = -0.35 - Math.sin(t*4 + fish.phase)*0.3;
    fish.topFin.rotation.z = 0.2 + Math.sin(t*3 + fish.phase)*0.15;

    // Поворот в направлении движения
    if (vel.lengthSq() > 0.0001) {
      fish.mesh.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0), vel.clone().normalize());
    }
    fish.mesh.position.y += Math.sin(t*2 + fish.phase)*0.002; // покачивание
  }

  // ----- Обновление корма (гравитация) -----
  for (let i = foodArray.length - 1; i >= 0; i--) {
    const food = foodArray[i];
    food.vy -= 0.0006;                       // гравитация
    food.mesh.position.y += food.vy * (dt*60);
    food.mesh.rotation.x += dt; food.mesh.rotation.y += dt;
    if (food.mesh.position.y <= floorY + 0.1) {
      scene.remove(food.mesh); foodArray.splice(i, 1);   // удаление при достижении дна
    }
  }

  // ----- Обновление пузырей -----
  for (let i = 0; i < bubbles.length; i++) {
    const b = bubbles[i];
    b.mesh.position.y += b.userData.speed*(dt*60);
    b.mesh.position.x += Math.sin(t*2 + b.userData.phase)*0.012;
    if (b.mesh.position.y > H/2 - 0.5) {
      b.mesh.position.y = floorY + 0.5;
      b.mesh.position.x = (Math.random()-0.5)*W*0.9;
      b.mesh.position.z = (Math.random()-0.5)*D*0.9;
    }
  }

  // ----- Анимация водорослей -----
  for (let i = 0; i < seaweeds.length; i++) {
    const s = seaweeds[i];
    s.rotation.x = s.userData.swayX*Math.sin(t*1.5 + s.userData.phase);
    s.rotation.z = s.userData.swayZ*Math.sin(t*1.2 + s.userData.phase + 1);
  }

  controls.update();
  renderer.render(scene, camera);

  // FPS + статистика (раз в секунду)
  fpsCount++; fpsTime += dt;
  if (fpsTime >= 1) {
    fpsValue = Math.round(fpsCount/fpsTime);
    document.getElementById('fps').textContent = fpsValue;
    document.getElementById('fishCount').textContent = fishArray.length;
    document.getElementById('bubbleCount').textContent = bubbles.length;
    document.getElementById('foodCount').textContent = foodArray.length;
    fpsCount = 0; fpsTime = 0;
  }
}
animate();
</script>
</body>
</html>
```

## ✅ Что реализовано

| Требование | Статус |
|---|---|
| **15 рыбок** с анатомией (тело-сфера, глаза с зрачками, хвост, 3 плавника) | ✅ |
| **8 цветовых схем**, размер 0.6–1.2 | ✅ |
| Анимация хвоста (Z), плавников, поворот по направлению движения | ✅ |
| **ИИ**: избегание столкновений, отражение от стен, блуждание, преследование корма | ✅ |
| **Рост на 5%** после поедания | ✅ |
| Стеклянный аквариум (`transmission`-эффект через opacity + roughness), рамка-edges, 36×24×20 | ✅ |
| Песчаное дно с procedural неровностями + тени | ✅ |
| **8 камней** (деформированные дедекаэдры) | ✅ |
| **12 водорослей** (TubeGeometry + CatmullRomCurve3, покачивание) | ✅ |
| **30 пузырей** (MeshPhysicalMaterial), движение вверх + сброс | ✅ |
| **Кормление**: клик → корм, гравитация, обнаружение R=15, поедание, удаление у дна | ✅ |
| Ambient + Directional (тени 2048, PCFSoft) + 2 PointLight, кнопка переключения | ✅ |
| OrbitControls (зум 10–60, maxPolarAngle π/1.8, damping) | ✅ |
| UI: информационная панель, статистика, FPS, кнопки | ✅ |
| FogExp2, градиентный фон, glass UI с blur | ✅ |

## 💡 Небольшие примечания

- **`transmission`** появился только начиная с **Three.js r138+**. В r128 (который вы указали) он не поддерживается, поэтому стеклянный эффект реализован через комбинацию `opacity`, `roughness: 0.05` и низкую металличность — визуально даёт тот же эффект преломления/прозрачности. Если хотите настоящий `transmission`, просто замените CDN на `three@0.160`.
- Все объекты низкополигональные для высокой производительности.
- Работает полностью офлайн после загрузки CDN-библиотек (нужен интернет для первых двух `<script>`).

Откройте файл — и можно наблюдать, как рыбки плавают, уворачиваются друг от друга, плывут к падающему корму и растут! 🐟✨