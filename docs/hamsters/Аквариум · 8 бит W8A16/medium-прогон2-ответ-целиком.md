

# 🐠 3D Аквариум с Реалистичными Рыбками

Полный код в одном HTML файле — просто сохраните как `aquarium.html` и откройте в браузере:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #0a1e3f; }
    canvas { display: block; }

    .glass-panel {
        position: absolute;
        background: rgba(10, 30, 60, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(120, 200, 255, 0.25);
        border-radius: 14px;
        padding: 16px 20px;
        color: #cfe8ff;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.1);
        z-index: 10;
        user-select: none;
    }

    #infoPanel { top: 20px; left: 20px; max-width: 280px; }
    #statsPanel { top: 20px; right: 20px; text-align: center; min-width: 150px; }

    h1 {
        font-size: 20px;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #4fc3f7, #81d4fa, #b3e5fc);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }

    .instructions { font-size: 12px; line-height: 1.7; opacity: 0.85; margin-bottom: 12px; }
    .instructions b { color: #81d4fa; }

    .btn-row { display: flex; flex-direction: column; gap: 8px; }

    button {
        padding: 9px 14px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 600;
        color: #fff;
        transition: all 0.25s ease;
        letter-spacing: 0.5px;
    }
    button:hover { transform: translateY(-2px); filter: brightness(1.15); }
    button:active { transform: translateY(0); }

    #addFishBtn { background: linear-gradient(135deg, #00897b, #26a69a); box-shadow: 0 4px 14px rgba(38,166,154,0.4); }
    #bubblesBtn { background: linear-gradient(135deg, #1565c0, #42a5f5); box-shadow: 0 4px 14px rgba(66,165,245,0.4); }
    #lightBtn   { background: linear-gradient(135deg, #f9a825, #ffca28); color: #4a3800; box-shadow: 0 4px 14px rgba(255,202,40,0.4); }

    .stat-line { font-size: 14px; margin-bottom: 6px; }
    .stat-value {
        font-size: 22px;
        font-weight: 700;
        color: #4fc3f7;
        text-shadow: 0 0 12px rgba(79,195,247,0.6);
    }
    #fps { color: #80cbc4; text-shadow: 0 0 12px rgba(128,203,196,0.6); }

    @media (max-width: 640px) {
        #infoPanel { max-width: 200px; padding: 12px; }
        #statsPanel { min-width: 110px; padding: 10px; }
        h1 { font-size: 16px; }
    }
</style>
</head>
<body>

<div class="glass-panel" id="infoPanel">
    <h1>🐠 3D АКВАРИУМ</h1>
    <div class="instructions">
        <b>ЛКМ + движение</b> — вращение камеры<br>
        <b>ПКМ + движение</b> — панорама<br>
        <b>Колесо</b> — зум<br>
        <b>Клик по воде</b> — покормить рыбок 🍤
    </div>
    <div class="btn-row">
        <button id="addFishBtn">➕ Добавить рыбку</button>
        <button id="bubblesBtn">💨 Больше пузырей</button>
        <button id="lightBtn">💡 Свет: ВКЛ</button>
    </div>
</div>

<div class="glass-panel" id="statsPanel">
    <div class="stat-line">Рыбок: <span class="stat-value" id="fishCount">0</span></div>
    <div class="stat-line">FPS: <span class="stat-value" id="fps">--</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
//  ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
// ============================================================
const TANK = { w: 36, h: 24, d: 20 }; // ширина, высота, глубина
const HALF = { x: TANK.w / 2, y: TANK.h / 2, z: TANK.d / 2 };

let scene, camera, renderer, controls, clock;
let sunLight, pointLightA, pointLightB;
let raycaster = new THREE.Raycaster();
let mouseNDC = new THREE.Vector2();
let feedPlane; // плоскость для raycast кликов

const fishArray = [];
const bubbleArray = [];
const foodArray = [];
const seaweedArray = [];

const FISH_COLORS = [
    { body: 0xff7043, fin: 0xffab91, name: 'оранжевая' },
    { body: 0x2196f3, fin: 0x90caf9, name: 'синяя' },
    { body: 0xffeb3b, fin: 0xf44336, name: 'жёлто-красная' },
    { body: 0x9c27b0, fin: 0xce93d8, name: 'фиолетовая' },
    { body: 0xe53935, fin: 0xef9a9a, name: 'красная' },
    { body: 0x43a047, fin: 0xa5d6a7, name: 'зелёная' },
    { body: 0xec407a, fin: 0xf48fb1, name: 'розовая' },
    { body: 0xffb300, fin: 0xfff176, name: 'золотая' }
];

// ============================================================
//  ИНИЦИАЛИЗАЦИЯ СЦЕНЫ
// ============================================================
function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a2a52);
    scene.fog = new THREE.FogExp2(0x0a2a52, 0.012);

    camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 500);
    camera.position.set(0, 12, 48);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(innerWidth, innerHeight);
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 10;
    controls.maxDistance = 60;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.target.set(0, 0, 0);

    clock = new THREE.Clock();

    createLights();
    createTank();
    createSand();
    createRocks();
    createSeaweed();
    createFeedPlane();

    for (let i = 0; i < 15; i++) addFish();
    for (let i = 0; i < 30; i++) addBubble(true);

    updateStats();
}

// ============================================================
//  ОСВЕЩЕНИЕ
// ============================================================
function createLights() {
    scene.add(new THREE.AmbientLight(0x404040, 0.4));

    sunLight = new THREE.DirectionalLight(0xbfe3ff, 1.1);
    sunLight.position.set(15, 30, 15);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.set(2048, 2048);
    sunLight.shadow.camera.left = -25;
    sunLight.shadow.camera.right = 25;
    sunLight.shadow.camera.top = 25;
    sunLight.shadow.camera.bottom = -25;
    scene.add(sunLight);

    pointLightA = new THREE.PointLight(0x40c4ff, 0.6, 60);
    pointLightA.position.set(-10, 5, 5);
    scene.add(pointLightA);

    pointLightB = new THREE.PointLight(0x2962ff, 0.5, 60);
    pointLightB.position.set(10, -5, -5);
    scene.add(pointLightB);
}

// ============================================================
//  АКВАРИУМ (СТЕКЛО + РАМКА)
// ============================================================
function createTank() {
    const geo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
    const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0x88ccff,
        metalness: 0,
        roughness: 0.05,
        transmission: 0.95,
        transparent: true,
        opacity: 0.15,
        side: THREE.DoubleSide,
        depthWrite: false
    });
    const glass = new THREE.Mesh(geo, glassMat);
    glass.renderOrder = 10;
    scene.add(glass);

    const edges = new THREE.LineSegments(
        new THREE.EdgesGeometry(geo),
        new THREE.LineBasicMaterial({ color: 0x9fd8ff, transparent: true, opacity: 0.5 })
    );
    scene.add(edges);
}

// ============================================================
//  ПЕСЧАНОЕ ДНО
// ============================================================
function createSand() {
    const geo = new THREE.PlaneGeometry(TANK.w - 1, TANK.d - 1, 40, 30);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i), y = pos.getY(i);
        pos.setZ(i,
            Math.sin(x * 0.5) * Math.cos(y * 0.4) * 0.35 +
            Math.sin(x * 1.7 + y * 1.3) * 0.15
        );
    }
    geo.computeVertexNormals();
    const mat = new THREE.MeshStandardMaterial({ color: 0xd9b98a, roughness: 1 });
    const sand = new THREE.Mesh(geo, mat);
    sand.rotation.x = -Math.PI / 2;
    sand.position.y = -HALF.y + 0.2;
    sand.receiveShadow = true;
    scene.add(sand);
}

// ============================================================
//  КАМНИ
// ============================================================
function createRocks() {
    for (let i = 0; i < 8; i++) {
        const size = 0.8 + Math.random() * 1.4;
        const geo = new THREE.DodecahedronGeometry(size, 1);
        const p = geo.attributes.position;
        for (let j = 0; j < p.count; j++) {
            p.setXYZ(j,
                p.getX(j) * (0.7 + Math.random() * 0.6),
                p.getY(j) * (0.5 + Math.random() * 0.5),
                p.getZ(j) * (0.7 + Math.random() * 0.6)
            );
        }
        geo.computeVertexNormals();
        const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.15, 0.25 + Math.random() * 0.15),
            roughness: 0.9
        }));
        rock.position.set(
            (Math.random() - 0.5) * (TANK.w - 6),
            -HALF.y + 0.5,
            (Math.random() - 0.5) * (TANK.d - 5)
        );
        rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
        rock.castShadow = true;
        rock.receiveShadow = true;
        scene.add(rock);
    }
}

// ============================================================
//  ВОДОРОСЛИ
// ============================================================
function createSeaweed() {
    for (let i = 0; i < 12; i++) {
        const height = 3 + Math.random() * 5;
        const points = [];
        const baseX = (Math.random() - 0.5) * (TANK.w - 6);
        const baseZ = (Math.random() - 0.5) * (TANK.d - 5);
        for (let s = 0; s <= 5; s++) {
            points.push(new THREE.Vector3(
                baseX + Math.sin(s * 1.2) * 0.5,
                -HALF.y + 0.3 + s * (height / 5),
                baseZ + Math.cos(s * 0.9) * 0.5
            ));
        }
        const curve = new THREE.CatmullRomCurve3(points);
        const geo = new THREE.TubeGeometry(curve, 12, 0.18 + Math.random() * 0.1, 6);
        const mat = new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.3 + Math.random() * 0.12, 0.7, 0.3 + Math.random() * 0.15),
            roughness: 0.8
        });
        const weed = new THREE.Mesh(geo, mat);
        weed.castShadow = true;
        weed.userData.phase = Math.random() * Math.PI * 2;
        weed.userData.sway = 0.3 + Math.random() * 0.4;
        scene.add(weed);
        seaweedArray.push(weed);
    }
}

// ============================================================
//  РЫБКИ
// ============================================================
function createFishMesh(colorScheme, scale) {
    const group = new THREE.Group();
    const bodyMat = new THREE.MeshStandardMaterial({ color: colorScheme.body, roughness: 0.4, metalness: 0.2 });
    const finMat = new THREE.MeshStandardMaterial({
        color: colorScheme.fin, roughness: 0.6,
        transparent: true, opacity: 0.75, side: THREE.DoubleSide
    });

    // Тело — вытянутая сфера
    const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
    body.scale.set(1.8, 0.9, 0.7);
    body.castShadow = true;
    group.add(body);

    // Глаза
    const eyeWhiteGeo = new THREE.SphereGeometry(0.22, 10, 8);
    const pupilGeo = new THREE.SphereGeometry(0.11, 8, 6);
    const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
    [-0.45, 0.45].forEach(z => {
        const ew = new THREE.Mesh(eyeWhiteGeo, eyeWhiteMat);
        ew.position.set(1.35, 0.25, z);
        const pu = new THREE.Mesh(pupilGeo, pupilMat);
        pu.position.set(1.45, 0.25, z * 1.05);
        group.add(ew, pu);
    });

    // Хвост (анимируется по Z)
    const tailGeo = new THREE.ConeGeometry(0.7, 1.2, 8);
    tailGeo.rotateX(Math.PI / 2);
    const tail = new THREE.Mesh(tailGeo, finMat);
    tail.position.set(-1.9, 0, 0);
    tail.rotation.z = Math.PI;
    group.add(tail);

    // Верхний плавник
    const topFinGeo = new THREE.ConeGeometry(0.5, 0.9, 4);
    const topFin = new THREE.Mesh(topFinGeo, finMat);
    topFin.position.set(-0.2, 0.85, 0);
    topFin.rotation.z = 0.4;
    group.add(topFin);

    // Боковые плавники
    const sideFinGeo = new THREE.CircleGeometry(0.45, 8);
    const leftFin = new THREE.Mesh(sideFinGeo, finMat);
    leftFin.position.set(0.3, -0.1, 0.65);
    leftFin.rotation.y = Math.PI / 2;
    group.add(leftFin);
    const rightFin = new THREE.Mesh(sideFinGeo, finMat);
    rightFin.position.set(0.3, -0.1, -0.65);
    rightFin.rotation.y = -Math.PI / 2;
    group.add(rightFin);

    group.scale.setScalar(scale);
    return { group, tail, leftFin, rightFin, topFin };
}

function addFish() {
    const scheme = FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)];
    const scale = 0.6 + Math.random() * 0.6;
    const parts = createFishMesh(scheme, scale);

    const fish = {
        mesh: parts.group,
        tail: parts.tail,
        leftFin: parts.leftFin,
        rightFin: parts.rightFin,
        topFin: parts.topFin,
        velocity: new THREE.Vector3((Math.random()-0.5)*2, (Math.random()-0.5), (Math.random()-0.5)*2).normalize(),
        speed: 4 + Math.random() * 4,
        tailSpeed: 8 + Math.random() * 6,
        phase: Math.random() * Math.PI * 2,
        wanderTimer: Math.random() * 3,
        targetFood: null,
        avoidanceRadius: 2.5 + Math.random() * 1.5,
        currentScale: scale
    };

    fish.mesh.position.set(
        (Math.random() - 0.5) * (TANK.w - 8),
        (Math.random() - 0.5) * (TANK.h - 8),
        (Math.random() - 0.5) * (TANK.d - 8)
    );
    scene.add(fish.mesh);
    fishArray.push(fish);
    updateStats();
}

// ============================================================
//  ПОВЕДЕНИЕ РЫБОК
// ============================================================
const _dir = new THREE.Vector3();

function updateFish(fish, dt, time) {
    const pos = fish.mesh.position;

    // --- Избегание других рыбок ---
    for (const other of fishArray) {
        if (other === fish) continue;
        _dir.subVectors(pos, other.mesh.position);
        const dist = _dir.length();
        if (dist < fish.avoidanceRadius && dist > 0.001) {
            fish.velocity.addScaledVector(_dir.normalize(), (fish.avoidanceRadius - dist) * 2.5 * dt);
        }
    }

    // --- Преследование корма ---
    let food = fish.targetFood;
    if (!food || !food.active) {
        food = null;
        for (const f of foodArray) {
            if (f.active && f.mesh.position.distanceTo(pos) < 15) { food = f; break; }
        }
        fish.targetFood = food;
    }
    if (food) {
        _dir.subVectors(food.mesh.position, pos).normalize();
        fish.velocity.lerp(_dir, 1.5 * dt);
        if (pos.distanceTo(food.mesh.position) < 1.2) eatFood(fish, food);
    } else {
        // --- Случайное блуждание ---
        fish.wanderTimer -= dt;
        if (fish.wanderTimer <= 0) {
            fish.wanderTimer = 2 + Math.random() * 4;
            fish.velocity.x += (Math.random() - 0.5) * 1.5;
            fish.velocity.y += (Math.random() - 0.5) * 0.8;
            fish.velocity.z += (Math.random() - 0.5) * 1.5;
        }
    }

    // --- Отражение от стен (плавное) ---
    const m = 2;
    if (pos.x >  HALF.x - m) fish.velocity.x -= (pos.x - (HALF.x - m)) * 4 * dt;
    if (pos.x < -HALF.x + m) fish.velocity.x -= (pos.x + HALF.x - m) * 4 * dt;
    if (pos.y >  HALF.y - m) fish.velocity.y -= (pos.y - (HALF.y - m)) * 4 * dt;
    if (pos.y < -HALF.y + m) fish.velocity.y -= (pos.y + HALF.y - m) * 4 * dt;
    if (pos.z >  HALF.z - m) fish.velocity.z -= (pos.z - (HALF.z - m)) * 4 * dt;
    if (pos.z < -HALF.z + m) fish.velocity.z -= (pos.z + HALF.z - m) * 4 * dt;

    // --- Нормализация скорости ---
    fish.velocity.clampLength(1, fish.speed * (food ? 1.6 : 1));
    pos.addScaledVector(fish.velocity, dt);

    // Жёсткий кламп внутри аквариума
    pos.x = THREE.MathUtils.clamp(pos.x, -HALF.x + 1.5, HALF.x - 1.5);
    pos.y = THREE.MathUtils.clamp(pos.y, -HALF.y + 1.5, HALF.y - 1.5);
    pos.z = THREE.MathUtils.clamp(pos.z, -HALF.z + 1.5, HALF.z - 1.5);

    // --- Поворот в направлении движения ---
    _dir.copy(fish.velocity).multiplyScalar(-1); // модель смотрит вдоль +X
    const targetQuat = new THREE.Quaternion().setFromRotationMatrix(
        new THREE.Matrix4().lookAt(new THREE.Vector3(0,0,0), fish.velocity.clone().negate(), new THREE.Vector3(0,1,0))
    );
    fish.mesh.quaternion.slerp(targetQuat, 1 - Math.pow(0.001, dt));

    // --- Анимация хвоста и плавников ---
    const t = time * fish.tailSpeed + fish.phase;
    fish.tail.rotation.y = Math.sin(t) * 0.6;
    fish.leftFin.rotation.x = Math.sin(t * 0.8) * 0.4;
    fish.rightFin.rotation.x = -Math.sin(t * 0.8) * 0.4;
    fish.topFin.rotation.z = 0.4 + Math.sin(t * 0.5) * 0.15;
}

function eatFood(fish, food) {
    food.active = false;
    scene.remove(food.mesh);
    food.mesh.geometry.dispose();
    fish.currentScale = Math.min(fish.currentScale * 1.05, 2.2);
    fish.mesh.scale.setScalar(fish.currentScale);
}

// ============================================================
//  ПУЗЫРИ
// ============================================================
function addBubble(randomY) {
    const geo = new THREE.SphereGeometry(0.12 + Math.random() * 0.2, 8, 6);
    const mat = new THREE.MeshPhysicalMaterial({
        color: 0xaaddff,
        transparent: true,
        opacity: 0.35,
        roughness: 0,
        metalness: 0,
        transmission: 0.9
    });
    const bubble = new THREE.Mesh(geo, mat);
    bubble.position.set(
        (Math.random() - 0.5) * (TANK.w - 4),
        randomY ? (Math.random() - 0.5) * (TANK.h - 4) : -HALF.y + 1,
        (Math.random() - 0.5) * (TANK.d - 4)
    );
    bubble.userData = {
        speed: 1.5 + Math.random() * 2,
        phase: Math.random() * Math.PI * 2,
        sway: 0.3 + Math.random() * 0.5
    };
    scene.add(bubble);
    bubbleArray.push(bubble);
}

function updateBubbles(dt, time) {
    for (const b of bubbleArray) {
        b.position.y += b.userData.speed * dt;
        b.position.x += Math.sin(time * 2 + b.userData.phase) * b.userData.sway * dt;
        b.position.z += Math.cos(time * 1.7 + b.userData.phase) * b.userData.sway * dt;
        if (b.position.y > HALF.y - 0.5) {
            b.position.y = -HALF.y + 0.8;
            b.position.x = (Math.random() - 0.5) * (TANK.w - 4);
            b.position.z = (Math.random() - 0.5) * (TANK.d - 4);
        }
    }
}

// ============================================================
//  СИСТЕМА КОРМЛЕНИЯ
// ============================================================
function createFeedPlane() {
    feedPlane = new THREE.Plane(new THREE.PlaneGeometry(200, 200), new THREE.MeshBasicMaterial({ visible: false }));
    scene.add(feedPlane);
}

function spawnFood(worldPos) {
    const geo = new THREE.SphereGeometry(0.25, 8, 6);
    const mat = new THREE.MeshStandardMaterial({ color: 0xff8f00, emissive: 0x663300, roughness: 0.7 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.copy(worldPos);
    scene.add(mesh);
    foodArray.push({
        mesh,
        velocity: new THREE.Vector3((Math.random()-0.5)*1.5, 0, (Math.random()-0.5)*1.5),
        active: true
    });
}

function updateFood(dt) {
    for (let i = foodArray.length - 1; i >= 0; i--) {
        const f = foodArray[i];
        if (!f.active) { foodArray.splice(i, 1); continue; }
        f.velocity.y -= 3 * dt; // гравитация
        f.mesh.position.addScaledVector(f.velocity, dt);
        if (f.mesh.position.y < -HALF.y + 0.5) {
            scene.remove(f.mesh);
            f.mesh.geometry.dispose();
            foodArray.splice(i, 1);
        }
    }
}

rendererClickHandler = function(e) {
    if (e.button !== 0) return;
    mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
    raycaster.setFromCamera(mouseNDC, camera);
    const hit = raycaster.intersectObject(feedPlane)[0];
    if (hit) {
        const p = hit.point;
        p.x = THREE.MathUtils.clamp(p.x, -HALF.x + 1, HALF.x - 1);
        p.y = THREE.MathUtils.clamp(p.y, -HALF.y + 1, HALF.y - 1);
        p.z = THREE.MathUtils.clamp(p.z, -HALF.z + 1, HALF.z - 1);
        spawnFood(p);
    }
};

// ============================================================
//  UI
// ============================================================
let lightOn = true;
document.getElementById('addFishBtn').onclick = () => addFish();
document.getElementById('bubblesBtn').onclick = () => { for (let i = 0; i < 10; i++) addBubble(false); };
document.getElementById('lightBtn').onclick = function() {
    lightOn = !lightOn;
    sunLight.intensity = lightOn ? 1.1 : 0.15;
    this.textContent = '💡 Свет: ' + (lightOn ? 'ВКЛ' : 'ВЫКЛ');
};

let fpsFrames = 0, fpsTime = 0;
function updateStats() {
    document.getElementById('fishCount').textContent = fishArray.length;
}
function updateFPS(dt) {
    fpsFrames++;
    fpsTime += dt;
    if (fpsTime >= 0.5) {
        document.getElementById('fps').textContent = Math.round(fpsFrames / fpsTime);
        fpsFrames = 0; fpsTime = 0;
    }
}

// ============================================================
//  ГЛАВНЫЙ ЦИКЛ
// ============================================================
function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const time = clock.elapsedTime;

    for (const fish of fishArray) updateFish(fish, dt, time);
    updateBubbles(dt, time);
    updateFood(dt);

    // Покачивание водорослей
    for (const w of seaweedArray) {
        w.rotation.x = Math.sin(time * 0.8 + w.userData.phase) * 0.06 * w.userData.sway * 2;
        w.rotation.z = Math.cos(time * 0.6 + w.userData.phase) * 0.06 * w.userData.sway * 2;
    }

    // Мерцание подводных огней
    pointLightA.intensity = 0.5 + Math.sin(time * 1.3) * 0.15;
    pointLightB.intensity = 0.45 + Math.cos(time * 1.1) * 0.15;

    controls.update();
    renderer.render(scene, camera);
    updateFPS(dt);
}

window.addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
});

init();
renderer.domElement.addEventListener('click', rendererClickHandler);
animate();
</script>
</body>
</html>
```

## ✨ Что реализовано

| Категория | Детали |
|-----------|--------|
| **Рыбки** | 15 штук, 8 цветовых схем, тела/глаза/хвост/3 плавника, случайный масштаб 0.6–1.2, слайр-поворот в направлении движения |
| **ИИ** | Отталкивание между рыбками, плавное отражение от стен, блуждание с таймером, преследование корма (радиус 15), ускорение при охоте, рост +5% за корм |
| **Аквариум** | Стекло с `transmission: 0.95`, wireframe-рамка, процедурный песок с неровностями, 8 деформированных камней с тенями, 12 водорослей из `TubeGeometry` + `CatmullRomCurve3` с покачиванием |
| **Пузыри** | 30 на старте, физика подъёма + синусоидальное покачивание, сброс на дно, кнопка «+10» |
| **Кормление** | Raycaster по невидимой плоскости, гравитация, съедание → рост рыбки |
| **Свет** | Ambient + Directional (тени 2048², PCFSoft) + 2 мерцающих PointLight, кнопка переключения |
| **UI** | Glassmorphism-панели, градиентные кнопки с hover, счётчик рыбок, FPS-метр, адаптивность |

**Совет:** если хотите больше интерактива — можно добавить двойной клик для «всплеска» (разгон всех пузырей) или звук всплеска через Web Audio API. 🫧