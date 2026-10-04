The user wants me to create a complete interactive 3D aquarium using Three.js based on the detailed specification they provided in Russian. Let me build this as a single HTML file with all the features described.

Let me plan out the implementation:

1. **Fish** - 15 colorful tropical fish at start
   - Anatomically detailed models (stretched sphere body, realistic eyes, animated tail, fins)
   - 8 color schemes
   - Random sizes from 0.6 to 1.2
   - Smooth animation (tail waving, fin movement, turning)

2. **AI and behavior**
   - Collision avoidance system
   - Wall reflection
   - Random wandering
   - Food chasing
   - Growth after eating
   - Individual parameters

3. **Environment**
   - Glass container with transmission effect
   - Sandy bottom with procedural bumps
   - Decorative rocks (8 deformed dodecahedrons)
   - Seaweed (12 bushes via TubeGeometry)

4. **Bubble system**
   - 30 bubbles at start
   - Transparent spheres with glass effect
   - Movement upward with swaying
   - Position reset when reaching surface

5. **Feeding system**
   - Click creates food
   - Food falls with physics (gravity)
   - Fish detect food within radius 15
   - Remove food + grow fish 5% when eaten
   - Remove food when reaching bottom

6. **Lighting**
   - AmbientLight
   - DirectionalLight with shadows
   - 2 PointLights
   - Toggle button for main light

7. **Camera controls (OrbitControls)**

8. **UI**
   - Info panel (top left)
   - Statistics (top right)
   - Buttons

9. **Visual effects**
   - Fog
   - Gradient background
   - Glass UI

Let me write this all out in a single HTML file. I'll use Three.js r128 from CDN.

Note: The transmission/transparency effect requires MeshPhysicalMaterial which is available in r128. However, transmission requires a environment map or specific setup to look good. Let me include it but make it work reasonably.

Let me write the complete code.

I need to be careful about the OrbitControls path for r128. The correct URL is:
https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js

Let me build this comprehensively.

For the glass container, transmission requires an environment. Without an env map, transmission just makes it transparent. That's fine for our purposes. Actually, for transmission to work properly you often need an environment map. But we can still set transmission value and it will refract based on what's behind. Let me keep it simple.

Let me write the full implementation now.

I'll structure it well with clear sections and comments in Russian since the spec is in Russian.

Let me think about the fish model:
- Body: scaled sphere (Mesh)
- Eyes: 2 small spheres with pupils
- Tail: a cone or flattened shape that rotates on Z axis
- Fins: upper, side fins

For the tail animation, I'll rotate the tail mesh. For fins, I'll do a subtle rotation.

Movement: Each fish has a velocity vector. I update position each frame. Fish steer toward targets (food) or away from each other.

Let me code this up carefully.

For the environment/background gradient, I'll use a canvas texture or CSS. Actually for a 3D scene, I'll create a gradient background using a large plane with a canvas texture, or set scene.background to a color and use fog. The spec says "Background: градиент от темно-синего к синему". I'll create a canvas gradient texture for the background.

Let me write everything now.

For seaweed using TubeGeometry with CatmullRomCurve3:
- Create a curve with control points
- Use TubeGeometry
- Animate by rotating

Let me build the seaweed with a few segments using a curve that bends.

Now let me write the complete HTML file.

I'll make the code robust and well-commented. Let me go.

Actually, let me reconsider the transmission. In r128, MeshPhysicalMaterial supports transmission. But without an environment map, it might render black or weird. Let me add a simple approach: set transmission and also give it an opacity fallback. Actually, I'll just set transmission and see. To be safe, I could also add an environment map via a CubeTextureGenerator or just skip complex env. Let me set transmission: 0.95, opacity: 1, transparent: true, ior: 1.5. This should give a glassy look.

Let me finalize and write the code.

One concern: performance with many objects. Should be fine for this scale.

Let me write it all out now.

For the fish direction/turning: I'll orient the fish mesh to face its velocity direction. If velocity is zero, keep facing forward. I'll use lookAt or compute rotation.

To face direction of travel:
```
const dir = fish.velocity.clone().normalize();
if (dir.lengthSq() > 0) {
  const target = fish.position.clone().add(dir);
  fish.mesh.lookAt(target);
}
```
But lookAt sets the -z axis to point at target. Fish models typically face +z or -z. I'll build the fish facing +z (toward +z), then adjust. Actually let me build fish facing +X or handle the rotation. Let me build fish so head points in +Z direction, then use lookAt which points -Z at target, so I need to rotate 180 or build facing -Z. Let me build fish head pointing toward -Z (typical in three.js where objects face -Z). Then lookAt works directly.

Hmm, let me just build the fish with head pointing in +Y... no. Let me be consistent: I'll build the fish along the X-axis and adjust orientation manually using atan2.

Simplest: build fish head pointing in +Z. Then to face velocity, compute angle and rotate Y:
```
const angle = Math.atan2(velocity.x, velocity.z);
fish.mesh.rotation.y = angle;
```
This rotates the fish so +Z aligns with velocity direction. Good. Then I don't need lookAt. And I can add slight roll/pitch for style.

Wait, atan2(vx, vz) gives the angle such that rotating by this angle around Y maps +Z to the (vx, 0, vz) direction. Let me verify: Rotating around Y by angle θ maps point (0,0,1) to (sinθ, 0, cosθ). We want (sinθ, 0, cosθ) parallel to (vx, 0, vz). So sinθ = vx/r, cosθ = vz/r → θ = atan2(vx, vz). Yes correct.

Good.

Now let me write the full thing.

For food physics:
- Food is a small sphere
- Has velocity, affected by gravity
- Falls down
- When near a fish (within some radius) and fish is heading toward it, get eaten
- When reaches bottom, removed

Let me define food objects: {mesh, velocity, settled}

Detection radius 15 for fish to chase food.

Eating: if food is close enough to fish (distance < fish size * factor) and fish is near, eat it.

Let me code the update loop.

OK let me just write it all now. This is going to be a long file.

Let me make sure to handle window resize.

Let me write it.

For the sandy bottom with procedural bumps: create a PlaneGeometry, displace vertices randomly, add material that receives shadows.

Let me write the complete code now.

I'll aim for a polished, working result.

Let me draft the HTML/CSS first then the JS.

Actually, I realize I should double check the OrbitControls import works with r128 standalone build. The examples/js builds attach to THREE namespace (THREE.OrbitControls). With the CDN script, it should register THREE.OrbitControls. Good.

Let me write everything.

I'll make the background a canvas gradient applied to scene.background as a texture.

Let me now produce the final answer with the complete code.

I'll write clean, well-organized code with Russian comments matching the spec.

Let me be thorough with the fish creation function, behavior update, and all systems.

Here's my plan for the code structure:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>3D Аквариум</title>
<style>...css...</style>
</head>
<body>
<div id="ui">...panels...</div>
<script src="three.min.js"></script>
<script src="OrbitControls.js"></script>
<script>
// All the JS
</script>
</body>
</html>
```

Let me write the CSS for glass UI, gradient buttons, etc.

Then the JS:

1. Scene setup, camera, renderer
2. Background gradient
3. Lighting
4. Aquarium glass container
5. Sandy bottom
6. Rocks
7. Seaweed
8. Bubbles
9. Fish
10. Food system
11. Animation loop
12. Event handlers (click for food, buttons)
13. OrbitControls

Let me write it all.

For fish colors, I'll define 8 palettes with body color and fin accents.

Let me code the fish creation:

```js
function createFish(colorScheme) {
  const group = new THREE.Group();
  const scale = 0.6 + Math.random() * 0.6; // 0.6 to 1.2
  
  // Body
  const bodyGeom = new THREE.SphereGeometry(0.5, 16, 12);
  bodyGeom.scale(1.6, 0.8, 0.7); // stretch
  const bodyMat = new THREE.MeshStandardMaterial({
    color: colorScheme.body,
    metalness: 0.3,
    roughness: 0.4,
    emissive: colorScheme.body.clone().multiplyScalar(0.1)
  });
  const body = new THREE.Mesh(bodyGeom, bodyMat);
  group.add(body);
  
  // Tail
  const tailGeom = new THREE.ConeGeometry(0.35, 0.7, 8);
  const tailMat = new THREE.MeshStandardMaterial({color: colorScheme.fin, metalness: 0.2, roughness: 0.5});
  const tail = new THREE.Mesh(tailGeom, tailMat);
  tail.rotation.x = Math.PI / 2; // point along Z
  tail.position.z = -0.7;
  group.add(tail);
  // pivot for tail - actually rotate around base
  // Better: put tail in a pivot group at back
  ...
}
```

For tail rotation around its base, I should parent the tail mesh to a pivot group positioned at the base of the tail, then rotate the pivot. Let me do that.

```js
const tailPivot = new THREE.Group();
tailPivot.position.z = -0.45; // base of tail at end of body
const tail = new THREE.Mesh(tailGeom, tailMat);
tail.position.z = -0.3; // offset from pivot
tailPivot.add(tail);
group.add(tailPivot);
```

Then animate tailPivot.rotation.x oscillates.

Wait, ConeGeometry points along +Y by default. Rotating x by PI/2 makes it point along Z. Position along z negative puts it behind. Good.

For eyes:
```js
const eyeGeom = new THREE.SphereGeometry(0.1, 12, 12);
const eyeMat = new THREE.MeshStandardMaterial({color: 0xffffff});
const pupilGeom = new THREE.SphereGeometry(0.05, 12, 12);
const pupilMat = new THREE.MeshStandardMaterial({color: 0x000000});
// two eyes at x = ±0.25, z = 0.2, y = 0.1
```

For fins:
```js
const finGeom = new THREE.SphereGeometry(0.25, 8, 8);
finGeom.scale(1, 0.1, 1.5);
// top fin
const topFin = new THREE.Mesh(finGeom, finMat);
topFin.position.y = 0.4;
// side fins
```

Animate fins with rotation.

OK let me just write the whole thing now. I'll be comprehensive.

Let me finalize.

I'll write the animation loop with delta time using clock.getDelta().

For fish behavior update:
```js
function updateFish(fish, delta) {
  const mesh = fish.mesh;
  // Find target
  let desired = new THREE.Vector3();
  
  // Food chasing
  let closestFood = null;
  let closestDist = 15;
  for (const food of foods) {
    if (food.settled) continue;
    const d = mesh.position.distanceTo(food.mesh.position);
    if (d < closestDist) {
      closestDist = d;
      closestFood = food;
    }
  }
  
  if (closestFood) {
    // steer toward food
    desired.copy(closestFood.mesh.position).sub(mesh.position).normalize().multiplyScalar(fish.speed);
  } else {
    // random wander + separation
    desired.set(
      Math.sin(fish.phase + time * 0.3) * fish.speed,
      0,
      Math.cos(fish.phase + time * 0.3) * fish.speed
    );
    // separation from other fish
    const sep = new THREE.Vector3();
    for (const other of fishArray) {
      if (other === fish) continue;
      const d = mesh.position.distanceTo(other.mesh.position);
      if (d < fish.avoidanceRadius) {
        const push = mesh.position.clone().sub(other.mesh.position).normalize().multiplyScalar((fish.avoidanceRadius - d) / fish.avoidanceRadius);
        sep.add(push);
      }
    }
    desired.add(sep.multiplyScalar(0.5));
  }
  
  // Update velocity with smoothing
  fish.velocity.lerp(desired, 0.05);
  
  // Move
  mesh.position.addScaledVector(fish.velocity, delta);
  
  // Wall bounds
  const margin = 2;
  const minX = -16, maxX = 16, minY = -8, maxY = 8, minZ = -8, maxZ = 8;
  if (mesh.position.x < minX) { fish.velocity.x = Math.abs(fish.velocity.x); mesh.position.x = minX; }
  ... etc
  // Actually smoother: apply steering force near walls
  if (mesh.position.x < minX) fish.velocity.x *= -1;
  ...
  
  // Orient
  if (fish.velocity.lengthSq() > 0.01) {
    const angle = Math.atan2(fish.velocity.x, fish.velocity.z);
    mesh.rotation.y = angle;
  }
  
  // Animate tail and fins
  fish.tail.rotation.x = Math.sin(time * fish.tailSpeed + fish.phase) * 0.4;
  ...
}
```

Let me refine wall handling to be smooth. I'll use a steering approach: if beyond boundary, reverse velocity component and clamp position.

For eating food:
```js
// check if any fish eats this food
for (const fish of fishArray) {
  const eatRadius = 0.5 * fish.scale + 0.5; // roughly
  if (mesh.position.distanceTo(food.mesh.position) < eatRadius) {
    // eat
    feedFish(fish);
    removeFood(food);
  }
}
```

Actually eat radius should relate to fish size. Let me use fish.size * 0.8 or so.

Let me store fish.size for scale.

Growth: fish.size *= 1.05, and scale the mesh.

Let me store the base scale and current size. When growing, I'll scale the mesh via mesh.scale.setScalar(newSize/baseSize). Or just re-scale. Simpler: keep a size property and set mesh.scale accordingly at creation, and multiply on growth.

Let me store fish.baseScale and apply mesh.scale initially. On growth, mesh.scale.multiplyScalar(1.05).

OK. Let me write the final code now. I'll be complete.

For bubbles:
```js
function createBubble() {
  const geom = new THREE.SphereGeometry(0.15 + Math.random()*0.2, 12, 12);
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0xaaddff, transmission: 0.95, transparent: true, opacity: 0.6,
    roughness: 0.1, metalness: 0, ior: 1.3
  });
  const bubble = new THREE.Mesh(geom, mat);
  bubble.position.set(randomX, randomY, randomZ);
  bubble.userData = { baseY: bubble.position.y, phase: Math.random()*Math.PI*2, speed: 0.5 + Math.random()*0.5, amplitude: 0.3 + Math.random()*0.3 };
  scene.add(bubble);
  bubbles.push(bubble);
}
```

Update: move up, sway, reset when above surface.

Let me write it all now. Final answer.

I want to make sure the code runs without errors. Let me be careful with variable scoping and references.

Let me write the complete file.

I'll include a loading note and ensure requestAnimationFrame loop.

For FPS counter, measure delta between frames.

Let me write it.

Also need to handle click to create food using raycaster against a plane or the aquarium. I'll raycast against an invisible plane at a certain depth, or just cast against the glass container bounding box. Simpler: cast against an invisible large plane in front of camera, then clamp within aquarium bounds. Or cast against the scene and pick a point. Let me cast against an invisible plane positioned at the aquarium center facing the camera, then map into aquarium bounds.

Actually simplest robust approach: create an invisible plane (Box) representing the aquarium volume, raycast against it, get intersection point inside. Let me use an invisible BoxGeometry slightly larger than aquarium and raycast; use the intersection point but clamp within bounds.

Let me do: raycast against an invisible box mesh; if intersected, place food at that point (clamped to aquarium bounds), give it initial downward velocity 0.

Let me implement.

I'll create the food with a small drop geometry (icosahedron or sphere) colored brownish.

Alright, writing final code now.

Let me make the UI nice with glass morphism.

Final code below.

Let me make sure I reference THREE correctly and that all functions are defined before use in the loop.

I'll write it out fully now.

One more consideration: the transmission effect needs an environment map to look like glass. Without it, in r128 it may appear mostly transparent/dark. To improve, I can generate a simple environment using CubeCamera or just set a background that shows through. Since we have a gradient background and objects behind, transmission will refract them. It should look okay-ish. Let me also add a subtle env map using a CubeTextureGenerator from the scene? That's complex. I'll just rely on transmission + the visible background. Alternatively, I can set the glass material with high transparency and low opacity to fake glass. Let me use transmission with ior and also keep it visible. I'll test mentally: transmission 0.95 means 95% transmission, so 5% reflection/refraction. It should show background through it. Good enough.

Let me finalize.

I'll write the complete HTML now. Given length, I'll be efficient but complete.

Let me also add a subtle caustic-like effect or just keep it clean.

Writing now.

For the directional light shadows, set shadow.mapSize to 2048, camera far appropriate, and position to shine into aquarium. Set target to aquarium center.

Let me set:
```
light.shadow.mapSize.width = 2048;
light.shadow.mapSize.height = 2048;
light.shadow.camera.near = 1;
light.shadow.camera.far = 100;
light.shadow.camera.left = -30;
light.shadow.camera.right = 30;
light.shadow.camera.top = 30;
light.shadow.camera.bottom = -30;
light.position.set(20, 40, 20);
light.target = aquariumCenter;
```

OK writing final.

Let me produce the answer with explanation in Russian (matching the user's language) and the full code.

I'll keep the intro brief and provide the complete code, plus usage notes.
</think>

# 🐠 3D Аквариум с Реалистичными Рыбками

Ниже — полный, готовый к работе код в одном HTML-файле. Просто сохраните его как `aquarium.html` и откройте в браузере.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Аквариум с Рыбками</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; font-family: 'Segoe UI', sans-serif; }
  #canvas { display: block; width: 100vw; height: 100vh; }

  /* Glass UI panels */
  .glass {
    background: rgba(20, 40, 70, 0.28);
    backdrop-filter: blur(14px) saturate(160%);
    -webkit-backdrop-filter: blur(14px) saturate(160%);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 18px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.15);
    color: #eaf4ff;
    padding: 18px 20px;
  }

  #info { position: absolute; top: 20px; left: 20px; max-width: 300px; }
  #stats { position: absolute; top: 20px; right: 20px; min-width: 210px; }

  h1 {
    font-size: 22px; margin-bottom: 10px;
    background: linear-gradient(90deg, #6ee7ff, #a78bfa, #ff8fb1);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; font-weight: 700;
  }
  h2 { font-size: 15px; margin: 14px 0 8px; color: #9fd8ff; letter-spacing: 0.5px; }

  ul { list-style: none; font-size: 13px; line-height: 1.7; color: #cfe4f7; }
  ul li::before { content: "▸ "; color: #6ee7ff; }

  .stat-row { display: flex; justify-content: space-between; font-size: 14px; margin: 6px 0; }
  .stat-val { font-weight: 700; color: #8effd0; }

  /* Gradient buttons */
  button {
    width: 100%; margin-top: 8px; padding: 11px 14px; border: none; border-radius: 12px;
    font-size: 14px; font-weight: 600; color: white; cursor: pointer;
    background: linear-gradient(135deg, #2196f3, #6ee7ff);
    box-shadow: 0 4px 14px rgba(33, 150, 243, 0.4);
    transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease;
  }
  button:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(110, 231, 255, 0.55); filter: brightness(1.1); }
  button:active { transform: translateY(0); }
  button.alt { background: linear-gradient(135deg, #ab47bc, #ff8fb1); box-shadow: 0 4px 14px rgba(171, 71, 188, 0.4); }
  button.on { background: linear-gradient(135deg, #66bb6a, #8effd0); color: #063; }
  button.off { background: linear-gradient(135deg, #555, #888); }

  #hint { position: absolute; bottom: 18px; left: 50%; transform: translateX(-50%);
          font-size: 13px; color: #cfe4f7; background: rgba(10,25,45,0.5);
          padding: 8px 18px; border-radius: 20px; backdrop-filter: blur(6px); }
</style>
</head>
<body>
<canvas id="canvas"></canvas>

<div id="info" class="glass">
  <h1>🐠 3D Аквариум</h1>
  <ul>
    <li><b>Левый клик + движение</b> — вращение камеры</li>
    <li><b>Правый клик</b> — панорамирование</li>
    <li><b>Колесо мыши</b> — зум</li>
    <li><b>Клик по аквариуму</b> — накормить рыбок</li>
  </ul>
</div>

<div id="stats" class="glass">
  <h2>📊 Статистика</h2>
  <div class="stat-row"><span>Рыбки</span><span class="stat-val" id="fishCount">0</span></div>
  <div class="stat-row"><span>Пузыри</span><span class="stat-val" id="bubbleCount">0</span></div>
  <div class="stat-row"><span>Корм</span><span class="stat-val" id="foodCount">0</span></div>
  <div class="stat-row"><span>FPS</span><span class="stat-val" id="fps">0</span></div>
  <button id="addFishBtn">🐟 Добавить рыбку</button>
  <button id="addBubbleBtn" class="alt">🫧 Больше пузырей (+10)</button>
  <button id="lightBtn">💡 Свет: ВКЛ</button>
</div>

<div id="hint">Кликните по аквариуму, чтобы опустить корм — рыбки плывут за ним! 🍽️</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
//  ОСНОВНАЯ ИНИЦИАЛИЗАЦИЯ
// ============================================================
const scene = new THREE.Scene();

// Градиентный фон (темно-синий → синий)
const bgCanvas = document.createElement('canvas');
bgCanvas.width = 2; bgCanvas.height = 512;
const bgCtx = bgCanvas.getContext('2d');
const grad = bgCtx.createLinearGradient(0, 0, 0, 512);
grad.addColorStop(0.0, '#0a2a55');
grad.addColorStop(0.5, '#0d3b6e');
grad.addColorStop(1.0, '#061833');
bgCtx.fillStyle = grad; bgCtx.fillRect(0, 0, 2, 512);
const bgTex = new THREE.CanvasTexture(bgCanvas);
scene.background = bgTex;

// Туман для имитации водной среды
scene.fog = new THREE.FogExp2(0x0a2a55, 0.012);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 4, 48);

const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas'), antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// OrbitControls
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.mouseButtons = { LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN };

// ============================================================
//  ОСВЕЩЕНИЕ
// ============================================================
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sunLight = new THREE.DirectionalLight(0xffffff, 1.1);
sunLight.position.set(20, 45, 20);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.near = 1;
sunLight.shadow.camera.far = 120;
sunLight.shadow.camera.left = -40;
sunLight.shadow.camera.right = 40;
sunLight.shadow.camera.top = 40;
sunLight.shadow.camera.bottom = -40;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);
scene.add(sunLight.target);

// Подводное освещение (голубой + синий)
const underwaterLight1 = new THREE.PointLight(0x44ccff, 0.9, 80);
underwaterLight1.position.set(-15, -5, 10);
scene.add(underwaterLight1);

const underwaterLight2 = new THREE.PointLight(0x2266ff, 0.7, 80);
underwaterLight2.position.set(15, 6, -10);
scene.add(underwaterLight2);

let mainLightOn = true;

// ============================================================
//  ПАРАМЕТРЫ АКВАРИУМА
// ============================================================
const AQU = { w: 36, h: 24, d: 20 };
const CENTER = new THREE.Vector3(0, 0, 0);
const BOUNDS = {
  x: AQU.w / 2 - 1.5,
  y: AQU.h / 2 - 1.5,
  z: AQU.d / 2 - 1.5
};

// ============================================================
//  СТЕКЛЯНЫЙ КОНТЕЙНЕР
// ============================================================
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xbfe8ff,
  transmission: 0.95,
  opacity: 1,
  transparent: true,
  roughness: 0.08,
  metalness: 0,
  ior: 1.45,
  thickness: 1.5,
  side: THREE.DoubleSide,
  depthWrite: false
});
const glassBox = new THREE.Mesh(new THREE.BoxGeometry(AQU.w, AQU.h, AQU.d), glassMat);
glassBox.renderOrder = 1;
scene.add(glassBox);

// Рамка (edges)
const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(AQU.w, AQU.h, AQU.d)),
  new THREE.LineBasicMaterial({ color: 0x9adcff, transparent: true, opacity: 0.55 })
);
scene.add(edges);

// Невидимый бокс для определения кликов (питинг корма)
const clickBox = new THREE.Mesh(
  new THREE.BoxGeometry(AQU.w, AQU.h, AQU.d),
  new THREE.MeshBasicMaterial({ visible: false })
);
scene.add(clickBox);

// ============================================================
//  ПЕСЧАНОЕ ДНО с процедурными неровностями
// ============================================================
const sandGeom = new THREE.PlaneGeometry(AQU.w, AQU.d, 40, 30);
sandGeom.rotateX(-Math.PI / 2);
const pos = sandGeom.attributes.position;
for (let i = 0; i < pos.count; i++) {
  const x = pos.getX(i), z = pos.getZ(i);
  const h = Math.sin(x * 0.4) * Math.cos(z * 0.4) * 0.3 + Math.random() * 0.25;
  pos.setY(i, h - 0.5);
}
sandGeom.computeVertexNormals();
const sand = new THREE.Mesh(sandGeom, new THREE.MeshStandardMaterial({
  color: 0xdcb678, roughness: 1, metalness: 0
}));
sand.position.y = -AQU.h / 2 + 0.3;
sand.receiveShadow = true;
scene.add(sand);

// ============================================================
//  ДЕКОРАТИВНЫЕ КАМНИ (8 деформированных дедекаэдров)
// ============================================================
const rocks = [];
for (let i = 0; i < 8; i++) {
  const detail = Math.random() > 0.5 ? 1 : 0;
  const geom = new THREE.DodecahedronGeometry(1 + Math.random() * 1.6, detail);
  const p = geom.attributes.position;
  for (let j = 0; j < p.count; j++) {
    const f = 0.75 + Math.random() * 0.5;
    p.setXYZ(j, p.getX(j) * f, p.getY(j) * f, p.getZ(j) * f);
  }
  geom.computeVertexNormals();
  const rock = new THREE.Mesh(geom, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.08, 0.1, 0.25 + Math.random() * 0.2),
    roughness: 0.9, metalness: 0.05, flatShading: true
  }));
  const rx = (Math.random() - 0.5) * (AQU.w - 8);
  const rz = (Math.random() - 0.5) * (AQU.d - 8);
  rock.position.set(rx, -AQU.h / 2 + 0.6 + Math.random() * 0.8, rz);
  rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
  rock.castShadow = true;
  rock.receiveShadow = true;
  scene.add(rock);
  rocks.push(rock);
}

// ============================================================
//  ВОДОРОСЛИ (12 кустов через TubeGeometry + CatmullRomCurve3)
// ============================================================
const weeds = [];
function createSeaweed() {
  const group = new THREE.Group();
  const stems = 3 + Math.floor(Math.random() * 3);
  const height = 3 + Math.random() * 4;
  const hue = 0.28 + Math.random() * 0.08;
  for (let s = 0; s < stems; s++) {
    const pts = [];
    const n = 6;
    for (let i = 0; i <= n; i++) {
      const t = i / n;
      pts.push(new THREE.Vector3(
        (Math.random() - 0.5) * 0.8 * t,
        t * height,
        (Math.random() - 0.5) * 0.8 * t
      ));
    }
    const curve = new THREE.CatmullRomCurve3(pts);
    const geom = new THREE.TubeGeometry(curve, 16, 0.12 + Math.random() * 0.1, 6, false);
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(hue, 0.6, 0.35 + Math.random() * 0.15),
      roughness: 0.7, metalness: 0, side: THREE.DoubleSide,
      emissive: new THREE.Color().setHSL(hue, 0.7, 0.12)
    });
    const stem = new THREE.Mesh(geom, mat);
    stem.position.set((Math.random() - 0.5) * 1.5, -AQU.h / 2 + 0.4, (Math.random() - 0.5) * 1.5);
    stem.castShadow = false;
    group.add(stem);
  }
  const px = (Math.random() - 0.5) * (AQU.w - 6);
  const pz = (Math.random() - 0.5) * (AQU.d - 6);
  group.position.set(px, 0, pz);
  scene.add(group);
  weeds.push({ group, phase: Math.random() * Math.PI * 2 });
}
for (let i = 0; i < 12; i++) createSeaweed();

// ============================================================
//  СИСТЕМА ПУЗЫРЕЙ
// ============================================================
const bubbles = [];
function createBubble() {
  const size = 0.15 + Math.random() * 0.22;
  const geom = new THREE.SphereGeometry(size, 14, 14);
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0xcff0ff, transmission: 0.95, opacity: 0.55, transparent: true,
    roughness: 0.05, metalness: 0, ior: 1.1, thickness: 0.5,
    emissive: 0x224466, emissiveIntensity: 0.2
  });
  const b = new THREE.Mesh(geom, mat);
  b.position.set(
    (Math.random() - 0.5) * (AQU.w - 4),
    -AQU.h / 2 + Math.random() * AQU.h,
    (Math.random() - 0.5) * (AQU.d - 4)
  );
  b.userData = {
    baseY: b.position.y,
    phase: Math.random() * Math.PI * 2,
    speed: 0.6 + Math.random() * 0.6,
    amp: 0.4 + Math.random() * 0.5
  };
  scene.add(b);
  bubbles.push(b);
}
for (let i = 0; i < 30; i++) createBubble();

// ============================================================
//  СИСТЕМА КОРМА
// ============================================================
const foods = [];
function createFood(position) {
  const geom = new THREE.IcosahedronGeometry(0.28, 0);
  const mat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.8, metalness: 0.1 });
  const f = new THREE.Mesh(geom, mat);
  f.position.copy(position);
  f.castShadow = true;
  f.userData.velocity = new THREE.Vector3(0, 0, 0);
  f.userData.settled = false;
  scene.add(f);
  foods.push(f);
}

// ============================================================
//  РЫБКИ
// ============================================================
const fishArray = [];

const COLOR_SCHEMES = [
  { body: 0xff8c1a, fin: 0xffb347 },   // оранжевая
  { body: 0x2a7bff, fin: 0x88cfff },   // синяя
  { body: 0xffe020, fin: 0xff3030 },   // желто-красная
  { body: 0x9b30ff, fin: 0xd98fff },   // фиолетовая
  { body: 0xff2b2b, fin: 0xff8080 },   // красная
  { body: 0x2ecc71, fin: 0x80ffbf },   // зеленая
  { body: 0xff69b4, fin: 0xffa0d0 },   // розовая
  { body: 0xffd700, fin: 0xfff0a0 }    // золотая
];

function createFish() {
  const group = new THREE.Group();
  const baseScale = 0.6 + Math.random() * 0.6; // 0.6 – 1.2

  const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];

  // --- Тело (вытянутая сфера) ---
  const bodyGeom = new THREE.SphereGeometry(0.5, 20, 16);
  bodyGeom.scale(1.7, 0.82, 0.72);
  const bodyMat = new THREE.MeshStandardMaterial({
    color: scheme.body, metalness: 0.35, roughness: 0.35,
    emissive: new THREE.Color(scheme.body).multiplyScalar(0.12)
  });
  const body = new THREE.Mesh(bodyGeom, bodyMat);
  body.castShadow = true;
  group.add(body);

  // --- Хвост (на отдельном приводе для вращения по Z/X) ---
  const tailPivot = new THREE.Group();
  tailPivot.position.set(0, 0, 0.75);
  const tailGeom = new THREE.ConeGeometry(0.4, 0.85, 10);
  const tailMat = new THREE.MeshStandardMaterial({
    color: scheme.fin, metalness: 0.25, roughness: 0.4,
    emissive: new THREE.Color(scheme.fin).multiplyScalar(0.12), transparent: true, opacity: 0.95
  });
  const tail = new THREE.Mesh(tailGeom, tailMat);
  tail.rotation.x = Math.PI / 2;
  tail.position.z = 0.45;
  tail.castShadow = true;
  tailPivot.add(tail);
  group.add(tailPivot);

  // --- Верхний плавник ---
  const finGeom = new THREE.SphereGeometry(0.28, 10, 10);
  finGeom.scale(1, 0.18, 1.6);
  const topFin = new THREE.Mesh(finGeom, tailMat.clone());
  topFin.position.set(0, 0.42, -0.05);
  group.add(topFin);

  // --- Боковые плавники ---
  const leftFin = new THREE.Mesh(finGeom, tailMat.clone());
  leftFin.position.set(0.32, -0.05, 0.05);
  leftFin.rotation.z = 0.3;
  group.add(leftFin);
  const rightFin = new THREE.Mesh(finGeom, tailMat.clone());
  rightFin.position.set(-0.32, -0.05, 0.05);
  rightFin.rotation.z = -0.3;
  group.add(rightFin);

  // --- Глаза с зрачками ---
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.4 });
  [0.26, -0.26].forEach(xOff => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 12), eyeMat);
    eye.position.set(xOff, 0.12, 0.38);
    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 10), pupilMat);
    pupil.position.set(0, 0, 0.07);
    eye.add(pupil);
    group.add(eye);
  });

  // Позиция
  group.position.set(
    (Math.random() - 0.5) * (AQU.w - 6),
    (Math.random() - 0.5) * (AQU.h - 6),
    (Math.random() - 0.5) * (AQU.d - 6)
  );
  scene.add(group);

  const fish = {
    mesh: group,
    tail: tailPivot,
    leftFin: leftFin,
    rightFin: rightFin,
    topFin: topFin,
    velocity: new THREE.Vector3(
      (Math.random() - 0.5) * 2,
      (Math.random() - 0.5) * 1,
      (Math.random() - 0.5) * 2
    ),
    speed: 1.5 + Math.random() * 2,
    tailSpeed: 4 + Math.random() * 5,
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: 3 + Math.random() * 2,
    size: baseScale
  };
  group.scale.setScalar(baseScale);
  fishArray.push(fish);
  return fish;
}

for (let i = 0; i < 15; i++) createFish();

// ============================================================
//  ВЗАИМОДЕЙСТВИЕ (клик — корм, кнопки)
// ============================================================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', (e) => {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObject(clickBox);
  if (hits.length > 0) {
    const p = hits[0].point;
    // Ограничиваем внутри аквариума
    p.x = THREE.MathUtils.clamp(p.x, -BOUNDS.x, BOUNDS.x);
    p.y = THREE.MathUtils.clamp(p.y, -BOUNDS.y, BOUNDS.y);
    p.z = THREE.MathUtils.clamp(p.z, -BOUNDS.z, BOUNDS.z);
    createFood(p);
  }
});

document.getElementById('addFishBtn').addEventListener('click', () => createFish());
document.getElementById('addBubbleBtn').addEventListener('click', () => { for (let i = 0; i < 10; i++) createBubble(); });
const lightBtn = document.getElementById('lightBtn');
lightBtn.addEventListener('click', () => {
  mainLightOn = !mainLightOn;
  lightBtn.textContent = '💡 Свет: ' + (mainLightOn ? 'ВКЛ' : 'ВЫКЛ');
  lightBtn.className = mainLightOn ? '' : 'off';
});

// ============================================================
//  АНИМАЦИЯ
// ============================================================
const clock = new THREE.Clock();
let fpsAccum = 0, fpsFrames = 0, fpsValue = 0;

function updateFish(fish, delta, time) {
  const mesh = fish.mesh;

  // Поиск ближайшего корма (радиус обнаружения 15)
  let target = null, bestDist = 15;
  for (const f of foods) {
    if (f.userData.settled) continue;
    const d = mesh.position.distanceTo(f.mesh.position);
    if (d < bestDist) { bestDist = d; target = f.mesh.position; }
  }

  let desired = new THREE.Vector3();
  if (target) {
    desired.copy(target).sub(mesh.position).normalize().multiplyScalar(fish.speed * 1.6);
    fish.targetFood = target;
  } else {
    fish.targetFood = null;
    // Случайное блуждание
    desired.set(
      Math.sin(time * 0.4 + fish.phase) * fish.speed,
      Math.sin(time * 0.6 + fish.phase * 1.7) * fish.speed * 0.3,
      Math.cos(time * 0.4 + fish.phase) * fish.speed
    );
    // Избегание столкновений с другими рыбками
    const sep = new THREE.Vector3();
    for (const other of fishArray) {
      if (other === fish) continue;
      const d = mesh.position.distanceTo(other.mesh.position);
      if (d < fish.avoidanceRadius && d > 0.001) {
        const push = mesh.position.clone().sub(other.mesh.position).normalize()
          .multiplyScalar((fish.avoidanceRadius - d) / fish.avoidanceRadius);
        sep.add(push);
      }
    }
    desired.add(sep.multiplyScalar(0.8));
  }

  // Плавная коррекция скорости
  fish.velocity.lerp(desired, 0.06);

  // Отражение от стен (плавное изменение направления)
  const m = 1.5;
  if (mesh.position.x < -BOUNDS.x) { fish.velocity.x = Math.max(fish.velocity.x, 0.3); mesh.position.x = -BOUNDS.x; }
  if (mesh.position.x >  BOUNDS.x) { fish.velocity.x = Math.min(fish.velocity.x, -0.3); mesh.position.x =  BOUNDS.x; }
  if (mesh.position.y < -BOUNDS.y) { fish.velocity.y = Math.max(fish.velocity.y, 0.3); mesh.position.y = -BOUNDS.y; }
  if (mesh.position.y >  BOUNDS.y) { fish.velocity.y = Math.min(fish.velocity.y, -0.3); mesh.position.y =  BOUNDS.y; }
  if (mesh.position.z < -BOUNDS.z) { fish.velocity.z = Math.max(fish.velocity.z, 0.3); mesh.position.z = -BOUNDS.z; }
  if (mesh.position.z >  BOUNDS.z) { fish.velocity.z = Math.min(fish.velocity.z, -0.3); mesh.position.z =  BOUNDS.z; }

  // Обновление позиции
  mesh.position.addScaledVector(fish.velocity, delta);

  // Поворот в направлении движения
  if (fish.velocity.lengthSq() > 0.01) {
    const angle = Math.atan2(fish.velocity.x, fish.velocity.z);
    mesh.rotation.y = angle;
    // Лёгкий наклон тела
    mesh.rotation.z = THREE.MathUtils.clamp(-fish.velocity.x * 0.04, -0.3, 0.3);
    mesh.rotation.x = THREE.MathUtils.clamp(fish.velocity.z * 0.02, -0.2, 0.2);
  }

  // Анимация хвоста (вращение по X/Z имитируетмах по Z)
  const wave = Math.sin(time * fish.tailSpeed + fish.phase);
  fish.tail.rotation.x = wave * 0.5;
  fish.tail.rotation.z = Math.cos(time * fish.tailSpeed + fish.phase) * 0.2;

  // Анимация плавников
  const finWave = Math.sin(time * fish.tailSpeed * 1.3 + fish.phase) * 0.4;
  fish.leftFin.rotation.z = 0.3 + finWave;
  fish.rightFin.rotation.z = -0.3 - finWave;
  fish.topFin.rotation.z = finWave * 0.5;
  fish.topFin.rotation.x = time * 2 + fish.phase;
}

function updateFood(delta) {
  for (let i = foods.length - 1; i >= 0; i--) {
    const f = foods[i];
    if (!f.userData.settled) {
      f.userData.velocity.y -= 6 * delta; // гравитация
      f.mesh.position.addScaledVector(f.userData.velocity, delta);
      f.mesh.rotation.x += delta * 2;
      f.mesh.rotation.y += delta * 3;

      // Проверка поедания рынками
      for (const fish of fishArray) {
        const eatR = 0.6 * fish.size;
        if (f.mesh.position.distanceTo(fish.mesh.position) < eatR) {
          // Съедено — рыбка растёт на 5%
          const ns = fish.size * 1.05;
          fish.mesh.scale.setScalar(ns);
          fish.size = ns;
          scene.remove(f);
          foods.splice(i, 1);
          break;
        }
      }
    }
    // Удаление при достижении дна
    if (f.mesh.position.y <= -BOUNDS.y - 0.2) {
      scene.remove(f);
      foods.splice(i, 1);
    }
  }
}

function updateBubbles(delta, time) {
  const floor = -AQU.h / 2 + 0.5;
  const ceil = AQU.h / 2 - 0.5;
  for (const b of bubbles) {
    b.position.y += b.userData.speed * delta;
    b.position.x += Math.sin(time * b.userData.speed + b.userData.phase) * b.userData.amp * delta;
    if (b.position.y > ceil) {
      b.position.y = floor;
      b.position.x = (Math.random() - 0.5) * (AQU.w - 4);
      b.position.z = (Math.random() - 0.5) * (AQU.d - 4);
    }
  }
}

function animate() {
  requestAnimationFrame(animate);
  const delta = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;

  for (const fish of fishArray) updateFish(fish, delta, time);
  updateFood(delta);
  updateBubbles(delta, time);

  // Покачивание водорослей (вращение по X и Z)
  for (const w of weeds) {
    w.group.rotation.x = Math.sin(time * 0.8 + w.phase) * 0.06;
    w.group.rotation.z = Math.cos(time * 0.6 + w.phase) * 0.06;
  }

  // Переключение основного света
  sunLight.intensity = mainLightOn ? 1.1 : 0.15;

  controls.update();
  renderer.render(scene, camera);

  // FPS
  fpsAccum += delta; fpsFrames++;
  if (fpsAccum >= 0.5) { fpsValue = Math.round(fpsFrames / fpsAccum); fpsAccum = 0; fpsFrames = 0; }
  document.getElementById('fishCount').textContent = fishArray.length;
  document.getElementById('bubbleCount').textContent = bubbles.length;
  document.getElementById('foodCount').textContent = foods.length;
  document.getElementById('fps').textContent = fpsValue;
}

animate();

// Адаптивность
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

## ✨ Что реализовано

| Требование | Реализация |
|---|---|
| **🐠 Рыбки** | 15 шт. на старте; тело-сфера ×1.7, глаза с зрачками, хвост на приводе (мах по X/Z), 3 плавника, 8 цветовых схем, размер 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений (sep), отражение от стен, случайное блуждание, преследование корма (радиус 15), рост на 5% при поедании |
| **🌊 Окружение** | Стеклянный бокс (`transmission: 0.95`, `ior`) + рамка-edges, песчаное дно с процедурными неровностями, 8 деформированных дедекаэдров, 12 водорослей (`TubeGeometry` + `CatmullRomCurve3`) |
| **💭 Пузыри** | 30 шт., `MeshPhysicalMaterial` со стеклом, движение вверх с синусоидальным покачиванием, сброс при достижении поверхности |
| **🍽️ Кормление** | Клик → падение корма с гравитацией, обнаружение в радиусе 15, поедание + рост, удаление у дна |
| **💡 Освещение** | Ambient, Directional с тенями 2048² (PCFSoft), 2 PointLight (голубой/синий), кнопка вкл/выкл |
| **🎮 Камера** | OrbitControls: вращение/панорама/зум (10–60), damping, `maxPolarAngle = PI/1.8` |
| **🖥️ UI** | Glass-панели с `backdrop-filter`, статистика (рыбки/FPS), кнопки «Добавить рыбку», «Больше пузырей», «Свет» |
| **🎨 Эффекты** | `FogExp2`, градиентный фон, градиентные кнопки с hover-glow |

## 🚀 Как использовать

1. Сохраните код в файл `aquarium.html`.
2. Откройте в современном браузере (Chrome/Edge/Firefox).
3. **Клик по аквариуму** — капает корм, рыбки плывут за ним и растут.
4. Кнопки справа — добавлять рыбок, пузыри, включать/выключать свет.
5. Мышь — вращайте и зумируйте камеру для осмотра.

> 💡 **Совет:** для ещё более стеклянного эффекта можно добавить `scene.environment` с карткой окружения — но и без неё преломление видно на фоне объектов внутри аквариума.

Хотите, чтобы я добавил **звуки пузырей**, **день/ночь с анимированным солнцем** или **систему размножения рыбок**? 🐡