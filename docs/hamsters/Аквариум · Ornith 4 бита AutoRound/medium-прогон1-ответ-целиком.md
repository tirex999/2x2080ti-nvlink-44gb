The user wants me to create a complete 3D aquarium project using Three.js based on the detailed specifications they provided. Let me build a comprehensive HTML file with all the features described:

1. Fish - 15 colorful tropical fish with detailed anatomy
2. AI behavior - collision avoidance, wall reflection, random wandering, food chasing, growth
3. Environment - glass container, sandy bottom, decorative stones, seaweed
4. Bubble system - 30 bubbles rising
5. Feeding system - click to create food
6. Lighting - ambient, directional, point lights
7. Camera controls - OrbitControls
8. UI - info panel, statistics, buttons
9. Visual effects - fog, gradient background, glass UI

Let me write this as a single HTML file that includes everything. I'll use Three.js r128 from CDN.

Let me be thorough and create a working, polished implementation.
</think>

# 3D Аккумулям с Реалистичными Рыбами

Вот полноценный интерактивный 3D аквариум на Three.js:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Аквариум с Реалистичными Рыбами</title>
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        overflow: hidden;
        background: #001;
        color: #fff;
    }

    #app {
        position: relative;
        width: 100vw;
        height: 100vh;
    }

    canvas {
        display: block;
    }

    /* Glass UI */
    .glass {
        background: rgba(10, 30, 60, 0.35);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    /* Info Panel */
    #info-panel {
        position: absolute;
        top: 20px;
        left: 20px;
        padding: 20px 24px;
        max-width: 320px;
        z-index: 10;
    }

    #info-panel h1 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 12px;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7, #ff6ec7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
    }

    #info-panel .instructions {
        font-size: 0.82rem;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.75);
        margin-bottom: 16px;
    }

    #info-panel .instructions strong {
        color: #00d4ff;
    }

    /* Stats Panel */
    #stats-panel {
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 18px 22px;
        min-width: 200px;
        z-index: 10;
    }

    #stats-panel h2 {
        font-size: 1.1rem;
        margin-bottom: 12px;
        color: #7be0ff;
    }

    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        font-size: 0.9rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stat-row:last-child {
        border-bottom: none;
    }

    .stat-value {
        font-weight: 700;
        color: #00d4ff;
    }

    /* Buttons */
    .btn-group {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 16px;
    }

    .btn {
        padding: 10px 18px;
        border: none;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        color: #fff;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }

    .btn:hover::before {
        left: 100%;
    }

    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
    }

    .btn:active {
        transform: translateY(0);
    }

    .btn-add {
        background: linear-gradient(135deg, #00d4ff, #0099cc);
    }

    .btn-bubbles {
        background: linear-gradient(135deg, #7b2ff7, #5a1fb0);
    }

    .btn-light {
        background: linear-gradient(135deg, #ffd700, #ff9500);
        color: #1a1a1a;
    }

    .btn-light.off {
        background: linear-gradient(135deg, #555, #333);
    }

    #fps {
        color: #7be0ff;
        font-variant-numeric: tabular-nums;
    }

    /* Tooltip */
    #tooltip {
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 10px 20px;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.8);
        z-index: 10;
        opacity: 0.8;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
</style>
</head>
<body>
<div id="app">
    <!-- Info Panel -->
    <div id="info-panel" class="glass">
        <h1>🐠 3D Аквариум</h1>
        <div class="instructions">
            <strong>Управление камерой:</strong><br>
            • Левый клик + движение — вращение<br>
            • Правый клик — панорамирование<br>
            • Колесо мыши — зум<br><br>
            <strong>Кормление:</strong><br>
            • ЛКМ по аквариуму — бросить корм
        </div>
        <div class="btn-group">
            <button class="btn btn-add" id="btn-add-fish">🐟 Добавить рыбку</button>
            <button class="btn btn-bubbles" id="btn-bubbles">🫧 Больше пузырей</button>
            <button class="btn btn-light" id="btn-light">💡 Свет: ВКЛ</button>
        </div>
    </div>

    <!-- Stats Panel -->
    <div id="stats-panel" class="glass">
        <h2>📊 Статистика</h2>
        <div class="stat-row">
            <span>Рыбки</span>
            <span class="stat-value" id="fish-count">15</span>
        </div>
        <div class="stat-row">
            <span>Пузыри</span>
            <span class="stat-value" id="bubble-count">30</span>
        </div>
        <div class="stat-row">
            <span>Корм</span>
            <span class="stat-value" id="food-count">0</span>
        </div>
        <div class="stat-row">
            <span>FPS</span>
            <span class="stat-value" id="fps">60</span>
        </div>
    </div>

    <div id="tooltip">Кликните по аквариуму, чтобы накормить рыбок 🍽️</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// 3D АКВАРИУМ — ОСНОВНОЙ СКРИPT
// ============================================================

// --- Глобальные переменные ---
let scene, camera, renderer, controls;
let clock = new THREE.Clock();
let fishArray = [];
let bubbleArray = [];
let foodArray = [];
let seaweedArray = [];
let stones = [];
let mainLightOn = true;
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2();
let groundPlane; // невидимая плоскость для raycasting корма

// Размеры аквариума
const AQU_WIDTH = 36;
const AQU_HEIGHT = 24;
const AQU_DEPTH = 20;
const HALF_W = AQU_WIDTH / 2;
const HALF_H = AQU_HEIGHT / 2;
const HALF_D = AQU_DEPTH / 2;

// Цветовые схемы
const COLOR_SCHEMES = [
    { name: 'оранжевая', body: 0xff8c00, fin: 0xffb347 },
    { name: 'синяя',     body: 0x1e90ff, fin: 0x63b3ff },
    { name: 'желто-красная', body: 0xffdd00, fin: 0xff3300 },
    { name: 'фиолетовая', body: 0x9b30ff, fin: 0xcc66ff },
    { name: 'красная',  body: 0xdc143c, fin: 0xff6b8a },
    { name: 'зелёная',  body: 0x2ecc71, fin: 0x6bff9e },
    { name: 'розовая',  body: 0xff69b4, fin: 0xffa0d0 },
    { name: 'золотая',  body: 0xffd700, fin: 0xfff0a0 }
];

// --- Инициализация ---
function init() {
    // Сцена
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0a3a5c, 0.008);

    // Камера
    camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 5, 55);

    // Рендерер
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('app').appendChild(renderer.domElement);

    // Управление камерой
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 10;
    controls.maxDistance = 60;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.mousePan = true;

    createLighting();
    createAquarium();
    createSandyBottom();
    createStones();
    createSeaweed();
    createBubbles();

    // Создаём рыбок
    for (let i = 0; i < 15; i++) {
        createFish();
    }

    // Плоскость для определения точки падения корма
    const groundGeo = new THREE.PlaneGeometry(AQU_WIDTH, AQU_DEPTH);
    const groundMat = new THREE.MeshBasicMaterial({ visible: false });
    groundPlane = new THREE.Mesh(groundGeo, groundMat);
    groundPlane.rotation.x = -Math.PI / 2;
    groundPlane.position.y = -HALF_H + 1;
    scene.add(groundPlane);

    // Обработчики событий
    window.addEventListener('resize', onResize);
    renderer.domElement.addEventListener('click', onClickFeed);
    document.getElementById('btn-add-fish').addEventListener('click', addFish);
    document.getElementById('btn-bubbles').addEventListener('click', addBubbles);
    document.getElementById('btn-light').addEventListener('click', toggleLight);

    animate();
}

// --- Освещение ---
let ambientLight, sunLight;
let pointLights = [];

function createLighting() {
    // Фоновое освещение
    ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    // Солнечный свет с тенями
    sunLight = new THREE.DirectionalLight(0xffffff, 1.0);
    sunLight.position.set(15, 40, 20);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 120;
    sunLight.shadow.camera.left = -40;
    sunLight.shadow.camera.right = 40;
    sunLight.shadow.camera.top = 40;
    sunLight.shadow.camera.bottom = -40;
    sunLight.shadow.bias = -0.0001;
    scene.add(sunLight);

    // Подводные точечные огни (голубой/синий)
    const pl1 = new THREE.PointLight(0x00aaff, 0.8, 80);
    pl1.position.set(-10, -5, 8);
    scene.add(pl1);
    pointLights.push(pl1);

    const pl2 = new THREE.PointLight(0x0066ff, 0.6, 80);
    pl2.position.set(12, 3, -6);
    scene.add(pl2);
    pointLights.push(pl2);
}

// --- Стеклянный аквариум ---
function createAquarium() {
    const glassGeo = new THREE.BoxGeometry(AQU_WIDTH, AQU_HEIGHT, AQU_DEPTH);
    const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0xaaddff,
        transmission: 0.95,
        transparent: true,
        opacity: 0.15,
        roughness: 0.05,
        metalness: 0,
        thickness: 1.5,
        ior: 1.33,
        side: THREE.DoubleSide
    });
    const glass = new THREE.Mesh(glassGeo, glassMat);
    glass.renderOrder = 1;
    scene.add(glass);

    // Рамка (edges)
    const edgesGeo = new THREE.EdgesGeometry(glassGeo);
    const edgesMat = new THREE.LineBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.6 });
    const edges = new THREE.LineSegments(edgesGeo, edgesMat);
    scene.add(edges);

    // Светящиеся линии рамки для красоты
    const glowMat = new THREE.LineBasicMaterial({ color: 0x33ddff, transparent: true, opacity: 0.4 });
    const glowEdges = new THREE.LineSegments(edgesGeo.clone(), glowMat);
    scene.add(glowEdges);
}

// --- Песчаное дно ---
function createSandyBottom() {
    const sandGeo = new THREE.PlaneGeometry(AQU_WIDTH, AQU_DEPTH, 40, 30);
    const positions = sandGeo.attributes.position;
    for (let i = 0; i < positions.count; i++) {
        const x = positions.getX(i);
        const y = positions.getY(i);
        // процедурные неровности
        const noise = Math.sin(x * 0.5) * Math.cos(y * 0.4) * 0.4 +
                      Math.sin(x * 1.3 + 1) * 0.2 +
                      Math.cos(y * 1.7 + 2) * 0.2;
        // Не трогаем края
        if (Math.abs(x) < HALF_W - 1 && Math.abs(y) < HALF_D - 1) {
            positions.setZ(i, noise);
        }
    }
    sandGeo.computeVertexNormals();

    const sandMat = new THREE.MeshStandardMaterial({
        color: 0xdcb876,
        roughness: 1.0,
        metalness: 0.0
    });
    const sand = new THREE.Mesh(sandGeo, sandMat);
    sand.rotation.x = -Math.PI / 2;
    sand.position.y = -HALF_H;
    sand.receiveShadow = true;
    scene.add(sand);
}

// --- Декоративные камни ---
function createStones() {
    for (let i = 0; i < 8; i++) {
        const detail = Math.random() > 0.5 ? 1 : 0;
        const stoneGeo = new THREE.DodecahedronGeometry(1 + Math.random() * 1.5, detail);
        // деформация
        const pos = stoneGeo.attributes.position;
        for (let j = 0; j < pos.count; j++) {
            const factor = 0.8 + Math.random() * 0.5;
            pos.setXYZ(j, pos.getX(j) * factor, pos.getY(j) * factor, pos.getZ(j) * factor);
        }
        stoneGeo.computeVertexNormals();

        const gray = 0x555555 + Math.floor(Math.random() * 0x333333);
        const stoneMat = new THREE.MeshStandardMaterial({
            color: gray,
            roughness: 0.9,
            metalness: 0.1,
            flatShading: true
        });
        const stone = new THREE.Mesh(stoneGeo, stoneMat);
        stone.position.set(
            (Math.random() - 0.5) * (AQU_WIDTH - 8),
            -HALF_H + 0.5 + Math.random() * 1.5,
            (Math.random() - 0.5) * (AQU_DEPTH - 8)
        );
        stone.rotation.set(
            Math.random() * Math.PI,
            Math.random() * Math.PI,
            Math.random() * Math.PI
        );
        stone.castShadow = true;
        stone.receiveShadow = true;
        scene.add(stone);
        stones.push(stone);
    }
}

// --- Водоросли ---
function createSeaweed() {
    for (let i = 0; i < 12; i++) {
        const group = new THREE.Group();
        const baseX = (Math.random() - 0.5) * (AQU_WIDTH - 6);
        const baseZ = (Math.random() - 0.5) * (AQU_DEPTH - 6);
        const height = 4 + Math.random() * 6;
        const color = new THREE.Color().setHSL(0.28 + Math.random() * 0.12, 0.7, 0.35 + Math.random() * 0.2);

        // несколько веток
        const strands = 2 + Math.floor(Math.random() * 3);
        for (let s = 0; s < strands; s++) {
            const points = [];
            const strandOffset = (s - strands / 2) * 0.6;
            for (let p = 0; p <= 6; p++) {
                const t = p / 6;
                points.push(new THREE.Vector3(
                    strandOffset + Math.sin(t * 2) * 0.5,
                    t * height,
                    Math.cos(t * 1.5) * 0.4
                ));
            }
            const curve = new THREE.CatmullRomCurve3(points);
            const tubeGeo = new THREE.TubeGeometry(curve, 12, 0.15 + Math.random() * 0.1, 6, false);
            const tubeMat = new THREE.MeshStandardMaterial({
                color: color,
                roughness: 0.7,
                metalness: 0.0,
                side: THREE.DoubleSide
            });
            const tube = new THREE.Mesh(tubeGeo, tubeMat);
            tube.castShadow = false;
            group.add(tube);
        }

        group.position.set(baseX, -HALF_H, baseZ);
        group.userData.swayPhase = Math.random() * Math.PI * 2;
        group.userData.swaySpeed = 0.5 + Math.random() * 0.5;
        scene.add(group);
        seaweedArray.push(group);
    }
}

// --- Пузыри ---
function createBubbles() {
    for (let i = 0; i < 30; i++) {
        addBubble();
    }
}

function addBubble() {
    const bubbleGeo = new THREE.SphereGeometry(0.15 + Math.random() * 0.35, 12, 12);
    const bubbleMat = new THREE.MeshPhysicalMaterial({
        color: 0xaaddff,
        transmission: 0.98,
        transparent: true,
        opacity: 0.3,
        roughness: 0.05,
        metalness: 0,
        thickness: 0.5,
        ior: 1.33,
        emissive: 0x113355,
        emissiveIntensity: 0.1
    });
    const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
    bubble.position.set(
        (Math.random() - 0.5) * (AQU_WIDTH - 4),
        -HALF_H + Math.random() * (AQU_HEIGHT - 2),
        (Math.random() - 0.5) * (AQU_DEPTH - 4)
    );
    scene.add(bubble);
    bubbleArray.push({
        mesh: bubble,
        speed: 0.5 + Math.random() * 1.0,
        swayPhase: Math.random() * Math.PI * 2,
        swaySpeed: 1 + Math.random() * 1.5,
        swayAmount: 0.2 + Math.random() * 0.4
    });
}

// --- Создание рыбки ---
function createFish() {
    const group = new THREE.Group();
    const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
    const scale = 0.6 + Math.random() * 0.6;

    // Материал тела (с лёгким свечением)
    const bodyMat = new THREE.MeshStandardMaterial({
        color: scheme.body,
        roughness: 0.3,
        metalness: 0.4,
        emissive: new THREE.Color(scheme.body).multiplyScalar(0.15),
        emissiveIntensity: 0.5
    });

    // Тело (вытянутая сфера)
    const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
    bodyGeo.scale(1.4, 0.8, 0.7);
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.castShadow = true;
    group.add(body);

    // Голова
    const headGeo = new THREE.SphereGeometry(0.6, 12, 10);
    const head = new THREE.Mesh(headGeo, bodyMat);
    head.position.set(1.0, 0.05, 0);
    head.castShadow = true;
    group.add(head);

    // Хвост
    const tailShape = new THREE.Shape();
    tailShape.moveTo(0, 0);
    tailShape.lineTo(-0.8, 0.6);
    tailShape.lineTo(-0.8, -0.6);
    tailShape.closePath();
    const tailGeo = new THREE.ShapeGeometry(tailShape);
    const tailMat = new THREE.MeshStandardMaterial({
        color: scheme.fin,
        roughness: 0.4,
        metalness: 0.2,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.9,
        emissive: new THREE.Color(scheme.fin).multiplyScalar(0.1),
        emissiveIntensity: 0.4
    });
    const tail = new THREE.Mesh(tailGeo, tailMat);
    tail.position.set(-1.5, 0, 0);
    tail.rotation.z = Math.PI;
    group.add(tail);

    // Верхний плавник
    const topFinShape = new THREE.Shape();
    topFinShape.moveTo(0, 0);
    topFinShape.quadraticCurveTo(0.3, 0.8, -0.4, 0.7);
    topFinShape.lineTo(-0.3, 0);
    topFinShape.closePath();
    const topFinGeo = new THREE.ShapeGeometry(topFinShape);
    const topFin = new THREE.Mesh(topFinGeo, tailMat.clone());
    topFin.position.set(-0.1, 0.6, 0);
    topFin.rotation.x = -0.3;
    group.add(topFin);

    // Боковые плавники
    const finShape = new THREE.Shape();
    finShape.moveTo(0, 0);
    finShape.quadraticCurveTo(0.5, -0.3, 0.2, -0.7);
    finShape.lineTo(-0.2, -0.3);
    finShape.closePath();
    const finGeo = new THREE.ShapeGeometry(finShape);

    const leftFin = new THREE.Mesh(finGeo, tailMat.clone());
    leftFin.position.set(0.2, -0.2, 0.5);
    leftFin.rotation.z = -0.3;
    group.add(leftFin);

    const rightFin = new THREE.Mesh(finGeo, tailMat.clone());
    rightFin.position.set(0.2, -0.2, -0.5);
    rightFin.rotation.z = -0.3;
    rightFin.rotation.y = Math.PI;
    group.add(rightFin);

    // Глазы
    const eyeGeo = new THREE.SphereGeometry(0.14, 10, 8);
    const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
    const pupilGeo = new THREE.SphereGeometry(0.08, 8, 6);
    const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.5 });

    const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
    eyeL.position.set(1.25, 0.15, 0.3);
    group.add(eyeL);
    const pupilL = new THREE.Mesh(pupilGeo, pupilMat);
    pupilL.position.set(1.37, 0.15, 0.3);
    group.add(pupilL);

    const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
    eyeR.position.set(1.25, 0.15, -0.3);
    group.add(eyeR);
    const pupilR = new THREE.Mesh(pupilGeo, pupilMat);
    pupilR.position.set(1.37, 0.15, -0.3);
    group.add(pupilR);

    // Применяем масштаб
    group.scale.setScalar(scale);

    // Начальная позиция
    group.position.set(
        (Math.random() - 0.5) * (AQU_WIDTH - 6),
        (Math.random() - 0.5) * (AQU_HEIGHT - 6),
        (Math.random() - 0.5) * (AQU_DEPTH - 6)
    );

    scene.add(group);

    // Направление по умолчанию
    const angle = Math.random() * Math.PI * 2;
    const speed = 1.5 + Math.random() * 2;

    fishArray.push({
        mesh: group,
        tail: tail,
        leftFin: leftFin,
        rightFin: rightFin,
        topFin: topFin,
        velocity: new THREE.Vector3(Math.cos(angle) * speed, 0, Math.sin(angle) * speed),
        speed: speed,
        tailSpeed: 3 + Math.random() * 3,
        phase: Math.random() * Math.PI * 2,
        targetFood: null,
        avoidanceRadius: 3 + scale * 2,
        size: scale,
        wanderTimer: Math.random() * 5
    });
}

// --- Добавление рыбки ---
function addFish() {
    createFish();
    updateStats();
}

// --- Пузыри добавление ---
function addBubbles() {
    for (let i = 0; i < 10; i++) {
        addBubble();
    }
    updateStats();
}

// --- Переключение света ---
function toggleLight() {
    mainLightOn = !mainLightOn;
    sunLight.visible = mainLightOn;
    const btn = document.getElementById('btn-light');
    if (mainLightOn) {
        btn.textContent = '💡 Свет: ВКЛ';
        btn.classList.remove('off');
    } else {
        btn.textContent = '💡 Свет: ВЫКЛ';
        btn.classList.add('off');
    }
}

// --- Кормление ---
function onClickFeed(event) {
    // Определяем позицию клика
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);

    // Пересечение с плоскостью на уровне дна аквариума
    const intersects = raycaster.intersectObject(groundPlane, false);
    if (intersects.length > 0) {
        const point = intersects[0].point;
        // Проверяем, что внутри аквариума
        if (Math.abs(point.x) < HALF_W && Math.abs(point.z) < HALF_D && point.y > -HALF_H) {
            createFood(point);
        }
    }
}

function createFood(position) {
    const foodGeo = new THREE.SphereGeometry(0.25, 8, 6);
    const foodMat = new THREE.MeshStandardMaterial({
        color: 0x8B4513,
        roughness: 0.9,
        metalness: 0.0,
        emissive: 0x332200,
        emissiveIntensity: 0.3
    });
    const food = new THREE.Mesh(foodGeo, foodMat);
    food.position.copy(position);
    food.castShadow = true;
    scene.add(food);

    foodArray.push({
        mesh: food,
        velocity: new THREE.Vector3(0, 0, 0),
        life: 0
    });
    updateStats();
}

// --- Обновление физики корма ---
const GRAVITY = -6;

function updateFood(delta) {
    for (let i = foodArray.length - 1; i >= 0; i--) {
        const item = foodArray[i];
        // Гравитация
        item.velocity.y += GRAVITY * delta;
        item.mesh.position.addScaledVector(item.velocity, delta);

        // Достижение дна — удалить
        if (item.mesh.position.y <= -HALF_H + 0.3) {
            item.mesh.position.y = -HALF_H + 0.3;
            scene.remove(item.mesh);
            foodArray.splice(i, 1);
            updateStats();
        }
    }
}

// --- Обновление рыбок ---
function updateFish(delta, time) {
    for (let i = 0; i < fishArray.length; i++) {
        const fish = fishArray[i];
        const mesh = fish.mesh;
        const vel = fish.velocity;

        // --- Поиск еды ---
        fish.targetFood = null;
        let closestDist = fish.avoidanceRadius + 15;
        for (let f = 0; f < foodArray.length; f++) {
            const fd = mesh.position.distanceTo(foodArray[f].mesh.position);
            if (fd < closestDist) {
                closestDist = fd;
                fish.targetFood = foodArray[f];
            }
        }

        // --- Вектор направления ---
        let moveDir = vel.clone().normalize();

        if (fish.targetFood) {
            // Плывут к еде
            const toFood = fish.targetFood.mesh.position.clone().sub(mesh.position).normalize();
            moveDir = toFood;
            // Ускоряемся к еде
            vel.lerp(toFood.multiplyScalar(fish.speed * 1.8), 0.05);

            // Поедание
            if (closestDist < 1.2 * fish.size) {
                eatFood(fish, fish.targetFood);
            }
        } else {
            // --- Случайное блуждание ---
            fish.wanderTimer -= delta;
            if (fish.wanderTimer <= 0) {
                fish.wanderTimer = 2 + Math.random() * 5;
                const wanderAngle = Math.random() * Math.PI * 2;
                moveDir.applyAxisAngle(new THREE.Vector3(0, 1, 0), wanderAngle);
            }

            // --- Избегание других рыбок ---
            for (let j = 0; j < fishArray.length; j++) {
                if (i === j) continue;
                const other = fishArray[j].mesh.position;
                const dir = mesh.position.clone().sub(other);
                const dist = dir.length();
                if (dist < fish.avoidanceRadius && dist > 0.01) {
                    dir.normalize();
                    const force = (fish.avoidanceRadius - dist) / fish.avoidanceRadius;
                    moveDir.add(dir.multiplyScalar(force * 1.5));
                }
            }

            // --- Отражение от стен ---
            const margin = 3;
            if (mesh.position.x > HALF_W - margin) moveDir.x = -Math.abs(moveDir.x);
            if (mesh.position.x < -HALF_W + margin) moveDir.x = Math.abs(moveDir.x);
            if (mesh.position.y > HALF_H - margin) moveDir.y = -Math.abs(moveDir.y);
            if (mesh.position.y < -HALF_H + margin) moveDir.y = Math.abs(moveDir.y);
            if (mesh.position.z > HALF_D - margin) moveDir.z = -Math.abs(moveDir.z);
            if (mesh.position.z < -HALF_D + margin) moveDir.z = Math.abs(moveDir.z);

            // Плавное следование направлению
            vel.lerp(moveDir.multiplyScalar(fish.speed), 0.03);
        }

        // Ограничение скорости
        const currentSpeed = vel.length();
        if (currentSpeed > fish.speed * 2.5) {
            vel.multiplyScalar(fish.speed * 2.5 / currentSpeed);
        }
        if (currentSpeed < fish.speed * 0.3) {
            vel.multiplyScalar(fish.speed * 0.3 / (currentSpeed || 1));
        }

        // --- Обновление позиции ---
        mesh.position.addScaledVector(vel, delta);

        // --- Поворот в направлении движения ---
        if (vel.lengthSq() > 0.001) {
            const target = mesh.position.clone().add(vel);
            mesh.lookAt(target);
            // Поворот так, чтобы голова смотрела вперёд (ось X)
        }

        // --- Анимация хвоста ---
        fish.phase += delta * fish.tailSpeed;
        const tailSwing = Math.sin(fish.phase) * 0.4;
        fish.tail.rotation.z = Math.PI + tailSwing;

        // --- Анимация плавников ---
        const finWave = Math.sin(fish.phase * 1.3) * 0.35;
        fish.leftFin.rotation.z = -0.3 + finWave;
        fish.rightFin.rotation.z = -0.3 - finWave;
        fish.topFin.rotation.z = Math.sin(fish.phase * 0.8) * 0.2;
    }
}

// --- Поедание еды ---
function eatFood(fish, food) {
    scene.remove(food.mesh);
    const idx = foodArray.indexOf(food);
    if (idx !== -1) foodArray.splice(idx, 1);

    // Рост на 5%
    fish.size *= 1.05;
    fish.mesh.scale.setScalar(fish.size);

    // Небольшой импульс после поедания
    fish.velocity.multiplyScalar(1.2);

    updateStats();
}

// --- Обновление пузырей ---
function updateBubbles(delta, time) {
    for (let i = 0; i < bubbleArray.length; i++) {
        const b = bubbleArray[i];
        const mesh = b.mesh;

        // Движение вверх
        mesh.position.y += b.speed * delta;

        // Покачивание
        mesh.position.x += Math.sin(time * b.swaySpeed + b.swayPhase) * b.swayAmount * delta;
        mesh.position.z += Math.cos(time * b.swaySpeed + b.swayPhase) * b.swayAmount * delta;

        // Сброс при достижении поверхности
        if (mesh.position.y > HALF_H - 1) {
            mesh.position.y = -HALF_H + Math.random() * 3;
            mesh.position.x = (Math.random() - 0.5) * (AQU_WIDTH - 4);
            mesh.position.z = (Math.random() - 0.5) * (AQU_DEPTH - 4);
        }
    }
}

// --- Обновление водорослей ---
function updateSeaweed(delta, time) {
    for (let i = 0; i < seaweedArray.length; i++) {
        const sw = seaweedArray[i];
        const sway = Math.sin(time * sw.userData.swaySpeed + sw.userData.swayPhase) * 0.06;
        sw.rotation.x = sway;
        sw.rotation.z = Math.cos(time * sw.userData.swaySpeed + sw.userData.swayPhase) * 0.04;
    }
}

// --- FPS ---
let frameCount = 0;
let fpsTime = 0;
let currentFPS = 60;

function updateFPS(delta) {
    frameCount++;
    fpsTime += delta;
    if (fpsTime >= 1.0) {
        currentFPS = Math.round(frameCount / fpsTime);
        frameCount = 0;
        fpsTime = 0;
        document.getElementById('fps').textContent = currentFPS;
    }
}

// --- Обновление статистики ---
function updateStats() {
    document.getElementById('fish-count').textContent = fishArray.length;
    document.getElementById('bubble-count').textContent = bubbleArray.length;
    document.getElementById('food-count').textContent = foodArray.length;
}

// --- Изменение размера окна ---
function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// --- Цикл анимации ---
function animate() {
    requestAnimationFrame(animate);

    const delta = Math.min(clock.getDelta(), 0.05);
    const time = clock.elapsedTime;

    updateFish(delta, time);
    updateFood(delta);
    updateBubbles(delta, time);
    updateSeaweed(delta, time);
    updateFPS(delta);

    controls.update();
    renderer.render(scene, camera);
}

// --- Запуск ---
window.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
```

## Что реализовано

### 🐠 Рыбки
- **15 рыбок** на старте с 8 цветовыми схемами
- Детализированная модель: вытянутое тело, голова, хвост, 3 плавника, глаза с зрачками
- Различный размер (0.6–1.2), разная скорость, частота махания хвостом, фаза анимации
- Плавный поворот в направлении движения через `lookAt`

### 🧠 ИИ поведение
- **Избегание столкновений** — рыбки отталкиваются друг от друга
- **Отражение от стен** — плавное разворота у границ
- **Случайное блуждание** — периодическое изменение направления
- **Преследование корма** в радиусе 15 единиц
- **Рост на 5%** после поедания

### 🌊 Окружение
- Стеклянный контейнер (`transmission: 0.95`, рамка-edges)
- Песчаное дно с процедурными неровностями (принимает тени)
- 8 деформированных дедекаэдров-камней с тенями
- 12 водорослей из `TubeGeometry` + `CatmullRomCurve3` с покачиванием

### 🫧 Пузыри
- 30 пузырей с эффектом стекла, движение вверх с синусоидальным покачиванием, сброс при достижении поверхности

### 🍽️ Кормление
- Клик по аквариуму → корм падает с гравитацией
- Рыбки обнаруживают корм и плывут к нему
- При поедании — корм исчезает, рыбка растёт

### 💡 Освещение & UI
- Ambient + Directional с мягкими тенями (2048², PCFSoftShadowMap) + 2 PointLight
- OrbitControls с damping, зум 10–60, ограничение угла
- Glass UI с градиентами, статистика, FPS, кнопки управления