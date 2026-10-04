The user wants me to create an interactive 3D aquarium with realistic fish using Three.js. This is a detailed specification. Let me build a complete HTML file with all the features described.

Let me plan this out:

1. **Fish** - 15 tropical fish with detailed anatomy, 8 color schemes, varied sizes, smooth animation
2. **AI behavior** - collision avoidance, wall reflection, random wandering, food chasing, growth, individual parameters
3. **Environment** - glass container, sandy bottom, decorative rocks, seaweed
4. **Bubble system** - 30 bubbles rising
5. **Feeding system** - click creates food, food falls with physics, fish detect food
6. **Lighting** - ambient, directional with shadows, point lights, toggle
7. **Camera controls** - OrbitControls
8. **UI** - info panel, stats, buttons
9. **Visual effects** - fog, gradient background, glass UI

Let me write this as a single HTML file with embedded CSS and JavaScript.

I'll use Three.js r128 and OrbitControls from CDN as specified.

Let me build this carefully and completely.

Key components:
- Scene setup with fog and gradient background
- Glass container (BoxGeometry with transmission material)
- Sandy bottom with procedural bumps
- 8 rocks (deformed dodecahedrons)
- 12 seaweed bushes (TubeGeometry with CatmullRomCurve3)
- 30 bubbles
- 15 fish with detailed models
- AI behavior system
- Feeding system with raycasting
- Lighting with shadows
- OrbitControls
- UI panels and buttons

Let me write the complete code now.

For the fish model, I need:
- Elongated body (scaled sphere)
- Realistic eyes with pupils
- Animatable tail (rotation on Z axis)
- Several fins (upper, side)

For colors: orange, blue, yellow-red, purple, red, green, pink, gold

Let me structure the fish group:
- Body mesh (scaled sphere)
- Tail mesh
- Left fin, right fin
- Maybe top fin
- Eyes

Let me write everything out.

I'll make sure to include all the requested features. Let me be thorough.

For the water/glass effect, r128 supports MeshPhysicalMaterial with transmission.

Let me code this up properly.
</think>

# 3D Аквариум с Реалистичными Рыбками

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Аквариум с Реалистичными Рыбками</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
        width: 100%; height: 100%;
        overflow: hidden;
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        background: #000;
        color: #e8f0fe;
    }
    #app { position: relative; width: 100vw; height: 100vh; }
    canvas { display: block; }

    /* Glass UI base */
    .glass {
        background: rgba(12, 30, 55, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(120, 200, 255, 0.18);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.08);
    }

    /* Info panel (top-left) */
    #info {
        position: absolute; top: 20px; left: 20px;
        padding: 18px 20px; max-width: 320px; z-index: 10;
    }
    #info h1 {
        font-size: 22px; font-weight: 800; line-height: 1.2;
        background: linear-gradient(90deg, #4dd6ff, #7cffa8, #ffd35c);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    #info .subtitle { font-size: 12px; color: #8fb8d8; margin-bottom: 12px; }
    #info ul { list-style: none; font-size: 12.5px; color: #bcd6ee; }
    #info li { padding: 3px 0; padding-left: 18px; position: relative; }
    #info li::before { content: '🐟'; position: absolute; left: 0; font-size: 10px; }
    #info .hint { font-size: 11px; color: #6fa; margin-top: 8px; }

    /* Buttons */
    .btn-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
    .btn {
        flex: 1; min-width: 92px; cursor: pointer;
        padding: 10px 12px; border: none; border-radius: 12px;
        font-size: 12.5px; font-weight: 700; color: #eaf6ff;
        background: linear-gradient(135deg, #1e5fbf, #2b8cff);
        box-shadow: 0 4px 14px rgba(43,140,255,0.35), inset 0 1px 0 rgba(255,255,255,0.2);
        transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease;
        text-transform: none; letter-spacing: 0.2px;
    }
    .btn:hover { transform: translateY(-2px); filter: brightness(1.15);
        box-shadow: 0 6px 20px rgba(43,140,255,0.55); }
    .btn:active { transform: translateY(0); }
    .btn.alt { background: linear-gradient(135deg, #0d7a5a, #16c99a);
        box-shadow: 0 4px 14px rgba(22,201,154,0.35); }
    .btn.alt:hover { box-shadow: 0 6px 20px rgba(22,201,154,0.55); }
    .btn.warn { background: linear-gradient(135deg, #b8660e, #ffb84d);
        color: #3a2400; box-shadow: 0 4px 14px rgba(255,180,77,0.4); }
    .btn.warn:hover { box-shadow: 0 6px 20px rgba(255,180,77,0.6); }

    /* Stats (top-right) */
    #stats {
        position: absolute; top: 20px; right: 20px; z-index: 10;
        padding: 14px 18px; min-width: 190px; text-align: right;
    }
    #stats .stat { display: flex; justify-content: space-between; align-items: center;
        padding: 5px 0; border-bottom: 1px solid rgba(120,200,255,0.1); font-size: 13px; }
    #stats .stat:last-child { border-bottom: none; }
    #stats .label { color: #8fb8d8; }
    #stats .value { font-weight: 800; color: #7cffa8; font-variant-numeric: tabular-nums; }

    /* Footer hint */
    #footer-hint {
        position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%);
        z-index: 10; padding: 8px 18px; font-size: 12px; color: #a9d0ee;
        border-radius: 20px; background: rgba(12,30,55,0.5); backdrop-filter: blur(8px);
        border: 1px solid rgba(120,200,255,0.15);
    }

    @ media (max-width: 640px) {
        #info { max-width: 220px; padding: 14px; }
        #info h1 { font-size: 18px; }
        #stats { min-width: 150px; }
    }
</style>
</head>
<body>
<div id="app"></div>

<!-- Info Panel -->
<div id="info" class="glass">
    <h1>🌊 3D Аквариум</h1>
    <div class="subtitle">Интерактивная подводная среда на Three.js</div>
    <ul>
        <li>ЛКМ + движение — вращение камеры</li>
        <li>ПКМ + движение — панорама</li>
        <li>Колесо мыши — зум (10–60)</li>
        <li>Клик по воде — скормить рыбок</li>
    </ul>
    <div class="hint">Кормите рыбок, наблюдайте за поведением и ростом!</div>
    <div class="btn-row">
        <button class="btn" id="addFishBtn">+ Рыбка</button>
        <button class="btn alt" id="addBubblesBtn">+ Пузыри</button>
        <button class="btn warn" id="lightBtn">Свет: ВКЛ</button>
    </div>
</div>

<!-- Stats Panel -->
<div id="stats" class="glass">
    <div class="stat"><span class="label">Рыбки</span><span class="value" id="fishCount">15</span></div>
    <div class="stat"><span class="label">Пузыри</span><span class="value" id="bubbleCount">30</span></div>
    <div class="stat"><span class="label">Корм</span><span class="value" id="foodCount">0</span></div>
    <div class="stat"><span class="label">FPS</span><span class="value" id="fps">0</span></div>
</div>

<div id="footer-hint">🐠 Перетащите для обзора • Кликните для кормления 🍽️</div>

<!-- Dependencies -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
// ============================================================
//  3D АКВАРИУМ — Инициализация
// ============================================================
let scene, camera, renderer, controls;
let fishArray = [];
let bubbleArray = [];
let foodArray = [];
let seaweedArray = [];
let rocksArray = [];
let mainLightOn = true;

// Аквариум: размеры 36 x 24 x 20
const TANK = { w: 36, h: 24, d: 20 };
const tankHalfW = TANK.w / 2;
const tankHalfH = TANK.h / 2;
const tankHalfD = TANK.d / 2;

// FPS счётчик
let lastTime = performance.now();
let frameCount = 0;
let fps = 0;

// ---- Инициализация сцены ----
function init() {
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

    // Градиентный фон (через canvas-текстуру)
    const bgCanvas = document.createElement('canvas');
    bgCanvas.width = 2; bgCanvas.height = 2;
    const bgCtx = bgCanvas.getContext('2d');
    const grad = bgCtx.createLinearGradient(0, 0, 0, 2);
    grad.addColorStop(0, '#0b3d6e');
    grad.addColorStop(1, '#04122b');
    bgCtx.fillStyle = grad;
    bgCtx.fillRect(0, 0, 2, 2);
    const bgTex = new THREE.CanvasTexture(bgCanvas);
    scene.background = bgTex;

    // Камера
    camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 8, 55);

    // Рендерер
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('app').appendChild(renderer.domElement);

    // OrbitControls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.rotateOnHorizontal = true;
    controls.minDistance = 10;
    controls.maxDistance = 60;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.mouseButtons = {
        LEFT: THREE.ORBITANGO, // placeholder, set below
    };
    // корректное назначение
    controls.mouseButtons = {
        LEFT: THREE.MOUSE.ROTATE,
        MIDDLE: THREE.MOUSE.DOLLY,
        RIGHT: THREE.MOUSE.PAN
    };
    controls.target.set(0, 0, 0);

    addEventListener('resize', onResize);
    buildLights();
    buildTank();
    buildSandyBottom();
    buildRocks();
    buildSeaweed();
    buildInitialBubbles();
    buildInitialFish();

    animate();
}

// ---- Свет ----
let dirLight, ambientLight;
function buildLights() {
    ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    dirLight = new THREE.DirectionalLight(0xfff6e0, 1.0);
    dirLight.position.set(12, 30, 18);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 1;
    dirLight.shadow.camera.far = 120;
    dirLight.shadow.camera.left = -30;
    dirLight.shadow.camera.right = 30;
    dirLight.shadow.camera.top = 30;
    dirLight.shadow.camera.bottom = -30;
    dirLight.shadow.bias = -0.0008;
    scene.add(dirLight);

    // Подводные point-light (голубой/синий)
    const pl1 = new THREE.PointLight(0x33ccff, 0.7, 90);
    pl1.position.set(-10, 6, 8);
    scene.add(pl1);
    const pl2 = new THREE.PointLight(0x2266ff, 0.6, 90);
    pl2.position.set(10, -4, -8);
    scene.add(pl2);
}

// ---- Стеклянный контейнер ----
function buildTank() {
    const w = TANK.w, h = TANK.h, d = TANK.d;
    const geo = new THREE.BoxGeometry(w, h, d);
    const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0x9fdcff,
        metalness: 0.0,
        roughness: 0.08,
        transmission: 0.95,
        transparent: true,
        opacity: 0.22,
        thickness: 1.2,
        ior: 1.33,
        side: THREE.DoubleSide,
        clearcoat: 1.0,
        clearcoatRoughness: 0.1
    });
    const tank = new THREE.Mesh(geo, glassMat);
    tank.receiveShadow = true;
    scene.add(tank);

    // Wireframe-рамка (edges)
    const edges = new THREE.EdgesGeometry(geo);
    const lineMat = new THREE.LineBasicMaterial({ color: 0x7fd0ff, transparent: true, opacity: 0.55 });
    const wire = new THREE.LineSegments(edges, lineMat);
    tank.add(wire);

    // Дно внутри — тёмная поверхность под стеклом
    const floorGeo = new THREE.BoxGeometry(w, 0.4, d);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x0a1e33, roughness: 1 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.position.y = -h / 2 - 0.2;
    floor.receiveShadow = true;
    scene.add(floor);
}

// ---- Песчаное дно с неровностями ----
function buildSandyBottom() {
    const size = TANK.w - 1;
    const segs = 64;
    const geo = new THREE.PlaneGeometry(size, size, segs, segs);
    geo.rotateX(-Math.PI / 2);
    // процедурные неровности
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i), z = pos.getZ(i);
        const y = Math.sin(x * 0.35) * 0.35 + Math.cos(z * 0.4) * 0.35 + Math.sin((x + z) * 0.15) * 0.6;
        pos.setY(i, Math.abs(y) * 0.5);
    }
    geo.computeVertexNormals();
    const mat = new THREE.MeshStandardMaterial({
        color: 0xd9c48b, roughness: 1, metalness: 0, flatShading: false
    });
    const sand = new THREE.Mesh(geo, mat);
    sand.position.y = -tankHalfH + 0.4;
    sand.receiveShadow = true;
    scene.add(sand);

    // песок-текстура (шум) — мелкие частицы через точки
    const sandGrain = new THREE.PointsMaterial({ color: 0xb8a070, size: 0.12, sizeAttenuation: true });
}

// ---- Декоративные камни (8 деформированных дедакаэдров) ----
function buildRocks() {
    const rockColors = [0x6b6f74, 0x7d7569, 0x5a6169, 0x8a7f6d, 0x66707a, 0x776b5c, 0x5f6b72, 0x857a68];
    for (let i = 0; i < 8; i++) {
        const geo = new THREE.DodecahedronGeometry(1.6 + Math.random() * 1.4, 1);
        // деформация вершин
        const pos = geo.attributes.position;
        for (let v = 0; v < pos.count; v++) {
            const vx = pos.getX(v), vy = pos.getY(v), vz = pos.getZ(v);
            const s = 1 + Math.sin(vx * 3.1) * 0.18 + Math.cos(vz * 2.7) * 0.18;
            pos.set(vx * s, vy * (0.7 + Math.random() * 0.3), vz * s);
        }
        geo.computeVertexNormals();
        const mat = new THREE.MeshStandardMaterial({ color: rockColors[i], roughness: 0.95, metalness: 0.05, flatShading: true });
        const rock = new THREE.Mesh(geo, mat);
        rock.castShadow = true;
        rock.receiveShadow = true;
        rock.position.set(
            (Math.random() - 0.5) * (tankHalfW - 4),
            -tankHalfH + 1.0 + Math.random() * 1.2,
            (Math.random() - 0.5) * (tankHalfD - 4)
        );
        rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
        scene.add(rock);
        rocksArray.push(rock);
    }
}

// ---- Водоросли (12 кустов, TubeGeometry + CatmullRomCurve3) ----
function buildSeaweed() {
    const weedColors = [0x1f7a3a, 0x2e8b3c, 0x3aa e4d, 0x166e2f, 0x4caf50, 0x2e7d32, 0x00897b, 0x33691e, 0x2e921e, 0x00796b, 0x43a047, 0x558b2f];
    for (let k = 0; k < 12; k++) {
        const group = new THREE.Group();
        const cx = (Math.random() - 0.5) * (tankHalfW - 4);
        const cz = (Math.random() - 0.5) * (tankHalfD - 4);
        const baseY = -tankHalfH + 0.6;
        const strands = 3 + Math.floor(Math.random() * 3);
        for (let s = 0; s < strands; s++) {
            const height = 4 + Math.random() * 6;
            const pts = [];
            const segments = 14;
            for (let j = 0; j <= segments; j++) {
                const t = j / segments;
                const x = Math.sin(t * 2.5 + k) * t * 1.4;
                const y = t * height;
                const z = Math.cos(t * 2.0 + k) * t * 1.0;
                pts.push(new THREE.Vector3(x, y, z));
            }
            const curve = new THREE.CatmullRomCurve3(pts);
            const tubeGeo = new THREE.TubeGeometry(curve, 10, 0.18 + Math.random() * 0.12, 6, false);
            const tubeMat = new THREE.MeshStandardMaterial({
                color: weedColors[(k + s) % weedColors.length],
                roughness: 0.8, metalness: 0.0, side: THREE.DoubleSide
            });
            const tube = new THREE.Mesh(tubeGeo, tubeMat);
            tube.castShadow = true;
            tube.position.set(cx, baseY, cz);
            // сохраняем базовые данные для анимации качания
            tube.userData = {
                isSeaweed: true,
                baseRot: tube.rotation.clone(),
                swayPhase: Math.random() * Math.PI * 2,
                swaySpeed: 0.6 + Math.random() * 0.6
            };
            group.add(tube);
        }
        group.userData.isWeedGroup = true;
        scene.add(group);
        seaweedArray.push(group);
    }
}

// ---- Пузыри ----
function buildInitialBubbles() {
    for (let i = 0; i < 30; i++) addBubble();
}
function addBubble() {
    const geo = new THREE.SphereGeometry(0.25 + Math.random() * 0.4, 12, 12);
    const mat = new THREE.MeshPhysicalMaterial({
        color: 0xbfe9ff, metalness: 0.1, roughness: 0.05,
        transmission: 0.9, transparent: true, opacity: 0.5,
        clearcoat: 1.0, clearcoatRoughness: 0.05, side: THREE.DoubleSide
    });
    const b = new THREE.Mesh(geo, mat);
    b.castShadow = false;
    b.position.set(
        (Math.random() - 0.5) * (tankHalfW - 2),
        -tankHalfH + Math.random() * (TANK.h - 2),
        (Math.random() - 0.5) * (tankHalfD - 2)
    );
    b.userData = {
        vy: 0.6 + Math.random() * 0.9,
        swayPhase: Math.random() * Math.PI * 2,
        swaySpeed: 1 + Math.random() * 1.5,
        swayAmp: 0.3 + Math.random() * 0.6
    };
    scene.add(b);
    bubbleArray.push(b);
}

// ============================================================
//  РЫБКИ
// ============================================================
const fishColorSchemes = [
    { body: 0xff8c1a, fin: 0xffa94d },   // оранжевая
    { body: 0x1e7fff, fin: 0x5cb2ff },   // синяя
    { body: 0xffe100, fin: 0xff3030 },   // желто-красная
    { body: 0x9b30ff, fin: 0xc98bff },   // фиолетовая
    { body: 0xe02020, fin: 0xff6a6a },   // красная
    { body: 0x20c040, fin: 0x7dff8a },   // зеленая
    { body: 0xff4fb0, fin: 0xff9ed8 },   // розовая
    { body: 0xffcc00, fin: 0xfff0a8 }    // золотая
];

function createFish(colorScheme) {
    const group = new THREE.Group();
    const scale = 0.6 + Math.random() * 0.6;

    const bodyMat = new THREE.MeshStandardMaterial({ color: colorScheme.body, roughness: 0.5, metalness: 0.15 });
    const finMat = new THREE.MeshStandardMaterial({ color: colorScheme.fin, roughness: 0.6, metalness: 0.1, transparent: true, opacity: 0.9 });

    // Тело — вытянутая сфера
    const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.scale.set(1.6, 0.9, 0.85);
    body.castShadow = true;
    group.add(body);

    // Хвост (конус/плоскость)
    const tailGeo = new THREE.ConeGeometry(0.55, 1.0, 12);
    tailGeo.rotateZ(-Math.PI / 2);
    const tail = new THREE.Mesh(tailGeo, finMat);
    tail.position.set(-1.9, 0, 0);
    tail.castShadow = true;
    group.add(tail);

    // Верхний плавник
    const topFinGeo = new THREE.ConeGeometry(0.4, 0.9, 4);
    const topFin = new THREE.Mesh(topFinGeo, finMat);
    topFin.position.set(0.1, 0.85, 0);
    topFin.rotation.z = Math.PI;
    topFin.castShadow = true;
    group.add(topFin);

    // Боковые плавники (левый/правый)
    const finGeo = new THREE.ConeGeometry(0.3, 0.7, 4);
    const leftFin = new THREE.Mesh(finGeo, finMat);
    leftFin.position.set(-0.2, -0.2, 0.55);
    leftFin.rotation.x = Math.PI / 2;
    leftFin.rotation.z = 0.4;
    leftFin.castShadow = true;
    group.add(leftFin);

    const rightFin = new THREE.Mesh(finGeo, finMat);
    rightFin.position.set(-0.2, -0.2, -0.55);
    rightFin.rotation.x = -Math.PI / 2;
    rightFin.rotation.z = -0.4;
    rightFin.castShadow = true;
    group.add(rightFin);

    // Глаза
    const eyeGeo = new THREE.SphereGeometry(0.2, 12, 12);
    const eyeWhite = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
    const pupilMat = new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.1 });
    [-1, 1].forEach(side => {
        const eye = new THREE.Mesh(eyeGeo, eyeWhite);
        eye.position.set(1.15, 0.18, side * 0.32);
        group.add(eye);
        const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), pupilMat);
        pupil.position.set(1.32, 0.18, side * 0.32);
        group.add(pupil);
    });

    group.scale.setScalar(scale);
    group.userData.scale = scale;

    // Физика/поведение
    const speed = 2.5 + Math.random() * 3.0;
    const fish = {
        mesh: group,
        tail: tail,
        leftFin: leftFin,
        rightFin: rightFin,
        topFin: topFin,
        velocity: new THREE.Vector3((Math.random() - 0.5), (Math.random() - 0.5) * 0.5, (Math.random() - 0.5) * 0.5).normalize().multiplyScalar(speed),
        speed: speed,
        tailSpeed: 4 + Math.random() * 5,
        phase: Math.random() * Math.PI * 2,
        targetFood: null,
        avoidanceRadius: 3.0 + Math.random() * 2.0,
        wanderAngle: Math.random() * Math.PI * 2,
        wanderTimer: Math.random() * 3
    };
    return fish;
}

function buildInitialFish() {
    for (let i = 0; i < 15; i++) {
        const cs = fishColorSchemes[Math.floor(Math.random() * fishColorSchemes.length)];
        const fish = createFish(cs);
        fish.mesh.position.set(
            (Math.random() - 0.5) * (tankHalfW - 4),
            (Math.random() - 0.5) * (tankHalfH - 4),
            (Math.random() - 0.5) * (tankHalfD - 4)
        );
        scene.add(fish.mesh);
        fishArray.push(fish);
    }
}

// ============================================================
//  КОРМ
// ============================================================
function createFood(pos) {
    const geo = new THREE.SphereGeometry(0.22, 8, 8);
    const mat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.9 });
    const f = new THREE.Mesh(geo, mat);
    f.castShadow = true;
    f.position.copy(pos);
    f.userData = { vy: 0 };
    scene.add(f);
    foodArray.push(f);
}

// ============================================================
//  ОБНОВЛЕНИЕ / АНИМАЦИЯ
// ============================================================
function animate() {
    requestAnimationFrame(animate);
    const time = performance.now();
    const dt = Math.min((time - lastTime) / 1000, 0.05);
    lastTime = time;

    updateFish(dt);
    updateFood(dt);
    updateBubbles(dt);
    updateSeaweed(time);

    controls.update();
    renderer.render(scene, camera);

    updateStats();
}

function updateFish(dt) {
    const n = fishArray.length;
    for (let i = 0; i < n; i++) {
        const f = fishArray[i];
        const p = f.mesh.position;
        const vel = f.velocity;

        // --- силы ---
        const acc = new THREE.Vector3();

        // 1) Разделение (avoidance)
        for (let j = 0; j < n; j++) {
            if (i === j) continue;
            const other = fishArray[j].mesh.position;
            const diff = new THREE.Vector3().subVectors(p, other);
            const dist = diff.length();
            if (dist < f.avoidanceRadius && dist > 0.0001) {
                diff.normalize().divideScalar(dist);
                acc.add(diff.multiplyScalar(1.0 / (dist + 0.001)));
            }
        }

        // 2) Преследование корма
        f.targetFood = findNearestFood(p, f, 15.0);
        if (f.targetFood) {
            const toFood = new THREE.Vector3().subVectors(f.targetFood.position, p);
            const d = toFood.length();
            if (d > 0.1) {
                toFood.normalize();
                acc.add(toFood.multiplyScalar(2.0));
                // поедание
                if (d < 1.2) { eatFood(f, f.targetFood); }
            }
        }

        // 3) Случайное блуждание
        f.wanderTimer -= dt;
        if (f.wanderTimer <= 0) {
            f.wanderAngle += (Math.random() - 0.5) * 1.5;
            f.wanderTimer = 1 + Math.random() * 3;
        }
        acc.x += Math.cos(f.wanderAngle) * 0.4;
        acc.z += Math.sin(f.wanderAngle) * 0.4;

        // 4) Отражение от стен (мягкая граница)
        const margin = 2.0;
        const limitX = tankHalfW - margin, limitY = tankHalfH - margin, limitZ = tankHalfD - margin;
        const push = new THREE.Vector3();
        if (p.x > limitX) push.x = -(p.x - limitX);
        else if (p.x < -limitX) push.x = -(p.x + limitX);
        if (p.y > limitY) push.y = -(p.y - limitY);
        else if (p.y < -limitY) push.y = -(p.y + limitY);
        if (p.z > limitZ) push.z = -(p.z - limitZ);
        else if (p.z < -limitZ) push.z = -(p.z + limitZ);
        acc.add(push.multiplyScalar(1.5));

        // --- интегрируем ---
        vel.add(acc.multiplyScalar(dt));
        // ограничение скорости
        const sp = vel.length();
        const maxSp = f.speed * 2.2;
        if (sp > maxSp) vel.multiplyScalar(maxSp / sp);
        // минимальная скорость чтобы не замирало
        if (vel.length() < f.speed * 0.4) vel.multiplyScalar((f.speed * 0.4) / (sp || 1));

        p.add(vel.clone().multiplyScalar(dt));

        // --- границы жёсткой фиксации (на всякий) ---
        p.x = Math.max(-limitX, Math.min(limitX, p.x));
        p.y = Math.max(-limitY, Math.min(limitY, p.y));
        p.z = Math.max(-limitZ, Math.min(limitZ, p.z));

        // --- поворот в направлении движения ---
        if (sp > 0.01) {
            const dir = vel.clone().normalize();
            const targetPos = p.clone().add(dir);
            controls.target.copy(targetPos); // не обязательно, но помогает
            const angleZ = Math.atan2(dir.y, dir.x);
            const angleY = Math.atan2(dir.z, dir.x);
            // поворот корпуса
            f.mesh.lookAt(targetPos);
            // наклон тела (pitch) по вертикали движения
            const pitch = Math.asin(Math.max(-1, Math.min(1, dir.y)));
            f.mesh.rotation.x = pitch * 0.6;
        }

        // --- анимация хвоста и плавников ---
        f.phase += dt * f.tailSpeed;
        const tailSwing = Math.sin(f.phase) * 0.5;
        f.tail.rotation.z = tailSwing;
        f.leftFin.rotation.z = 0.4 + Math.sin(f.phase * 0.5) * 0.3;
        f.rightFin.rotation.z = -0.4 - Math.sin(f.phase * 0.5) * 0.3;
        f.topFin.rotation.x = Math.PI + Math.sin(f.phase * 0.7) * 0.2;
    }
}

function findNearestFood(pos, fish, radius) {
    let best = null, bestDist = radius;
    for (let k = 0; k < foodArray.length; k++) {
        const d = pos.distanceTo(foodArray[k].position);
        if (d < bestDist) { bestDist = d; best = foodArray[k]; }
    }
    return best;
}

function eatFood(fish, food) {
    // удалить корм
    scene.remove(food);
    foodArray.splice(foodArray.indexOf(food), 1);
    // рост рыбки на 5%
    const s = fish.mesh.userData.scale;
    const ns = s * 1.05;
    fish.mesh.userData.scale = ns;
    fish.mesh.scale.setScalar(ns);
}

function updateFood(dt) {
    const gravity = -6.0;
    for (let k = foodArray.length - 1; k >= 0; k--) {
        const f = foodArray[k];
        f.userData.vy += gravity * dt;
        f.position.y += f.userData.vy * dt;
        // достижение дна — удалить
        if (f.position.y < -tankHalfH + 0.6) {
            scene.remove(f);
            foodArray.splice(k, 1);
        }
    }
}

function updateBubbles(dt) {
    const surfaceY = tankHalfH - 0.5;
    for (let i = 0; i < bubbleArray.length; i++) {
        const b = bubbleArray[i];
        const ud = b.userData;
        b.position.y += ud.vy * dt;
        b.position.x += Math.sin(performance.now() * 0.001 * ud.swaySpeed + ud.swayPhase) * ud.swayAmp * dt;
        b.position.z += Math.cos(performance.now() * 0.001 * ud.swaySpeed + ud.swayPhase) * ud.swayAmp * 0.5 * dt;
        // сброс при достижении поверхности
        if (b.position.y > surfaceY) {
            b.position.y = -tankHalfH + Math.random() * 2;
            b.position.x = (Math.random() - 0.5) * (tankHalfW - 2);
            b.position.z = (Math.random() - 0.5) * (tankHalfD - 2);
        }
    }
}

function updateSeaweed(time) {
    const t = time * 0.001;
    for (let g = 0; g < seaweedArray.length; g++) {
        const group = seaweedArray[g];
        for (let m = 0; m < group.children.length; m++) {
            const tube = group.children[m];
            const ud = tube.userData;
            const sway = Math.sin(t * ud.swaySpeed + ud.swayPhase) * 0.15;
            tube.rotation.x = ud.baseRot.x + sway;
            tube.rotation.z = ud.baseRot.z + sway * 0.8;
        }
    }
}

// ============================================================
//  UI / СТАТИСТИКА
// ============================================================
function updateStats() {
    document.getElementById('fishCount').textContent = fishArray.length;
    document.getElementById('bubbleCount').textContent = bubbleArray.length;
    document.getElementById('foodCount').textContent = foodArray.length;
    frameCount++;
    const now = performance.now();
    if (now - lastTime >= 1000) {
        fps = frameCount;
        frameCount = 0;
        lastTime = now;
        document.getElementById('fps').textContent = fps;
    }
}

// ============================================================
//  КЛИК — КОРМЛЕНИЕ (raycaster)
// ============================================================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);

function onCanvasClick(event) {
    // не обрабатываем, если перетащили (drag)
    if (wasDragged) return;

    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);

    // пересечение с горизонтальной плоскостью в аквариуме
    const target = new THREE.Vector3();
    raycaster.ray.intersectPlane(groundPlane, target);
    if (!target) return;
    // ограничим внутри аквариума
    target.x = Math.max(-tankHalfW + 1, Math.min(tankHalfW - 1, target.x));
    target.z = Math.max(-tankHalfD + 1, Math.min(tankHalfD - 1, target.z));
    target.y = tankHalfH - 1.0; // падаем с поверхности

    createFood(target);
}

// определение drag vs click
let downPos = null;
let wasDragged = false;
renderer = renderer; // noop
window.addEventListener('mousedown', (e) => {
    downPos = { x: e.clientX, y: e.clientY };
    wasDragged = false;
});
window.addEventListener('mousemove', () => {
    // если сильно сдвинули — это drag
});
window.addEventListener('mouseup', (e) => {
    if (downPos) {
        const dx = e.clientX - downPos.x;
        const dy = e.clientY - downPos.y;
        if (Math.sqrt(dx*dx + dy*dy) > 5) wasDragged = true;
        downPos = null;
    }
});

// ============================================================
//  КНОПКИ
// ============================================================
document.getElementById('addFishBtn').addEventListener('click', () => {
    const cs = fishColorSchemes[Math.floor(Math.random() * fishColorSchemes.length)];
    const fish = createFish(cs);
    fish.mesh.position.set(
        (Math.random() - 0.5) * (tankHalfW - 4),
        (Math.random() - 0.5) * (tankHalfH - 4),
        (Math.random() - 0.5) * (tankHalfD - 4)
    );
    scene.add(fish.mesh);
    fishArray.push(fish);
});

document.getElementById('addBubblesBtn').addEventListener('click', () => {
    for (let i = 0; i < 10; i++) addBubble();
});

document.getElementById('lightBtn').addEventListener('click', () => {
    mainLightOn = !mainLightOn;
    dirLight.intensity = mainLightOn ? 1.0 : 0.15;
    document.getElementById('lightBtn').textContent = mainLightOn ? 'Свет: ВКЛ' : 'Свет: ВЫКЛ';
});

// Кормление по клику на canvas
renderer.domElement.addEventListener('click', onCanvasClick);

// ============================================================
//  RESIZE
// ============================================================
function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// ---- ЗАПУСК ----
window.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
```

## Что реализовано

Я создал **полноценный интерактивный 3D аквариум** со всеми требуемыми функциями:

### 🐠 Рыбки (15 шт. на старте)
- Анатомически детализированные модели: вытянутое тело (масштабированная сфера), реалистичные глаза с зрачками, анимируемый хвост (вращение по Z), верхний плавник и боковые плавники
- **8 цветовых схем**: оранжевая, синяя, желто-красная, фиолетовая, красная, зеленая, розовая, золотая
- Случайный масштаб 0.6–1.2, плавное махание хвостом с разной частотой, поворот в направлении движения

### 🧠 ИИ-поведение
- Разделение (избегание столкновений между рыбками)
- Мягкое отражение от стен
- Случайное блуждание (wander-система)
- Преследование корма в радиусе 15 единиц
- Рост на 5% после поедания

### 🌊 Окружение
- Стеклянный контейнер с `transmission: 0.95` и wireframe-рамкой (36×24×20)
- Песчаное дно с процедурными неровностями
- 8 деформированных дедакаэдров-камней
- 12 кустов водорослей (TubeGeometry + CatmullRomCurve3) с качанием

### 💭 Пузыри (30 шт.)
- Прозрачные сферы с MeshPhysicalMaterial, движение вверх с покачиванием, сброс у поверхности

### 🍽️ Кормление
- Клик создаёт корм с гравитацией, рыбки его обнаруживают и съедают

### 💡 Освещение & 🎮 Управление & 🖥️ UI
- Ambient + Directional с тенями (2048², PCFSoftShadowMap) + 2 PointLight
- OrbitControls с damping, зумом 10–60, ограничением polar angle
- Glass-панели с backdrop-filter, градиентные кнопки, счётчики FPS/рыбок/пузирей/корма

**Откройте файл в браузере** — используйте мышь для обзора, кликайте по воде для кормления!