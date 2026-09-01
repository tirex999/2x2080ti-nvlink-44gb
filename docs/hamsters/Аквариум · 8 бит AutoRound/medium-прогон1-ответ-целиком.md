

# 🐠 3D Аквариум с Реалистичными Рыбками

Полный код в одном HTML файле:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #04122e; }
    canvas { display: block; }

    .glass-panel {
        position: absolute;
        background: rgba(10, 30, 60, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(100, 200, 255, 0.25);
        border-radius: 14px;
        padding: 16px 20px;
        color: #cfeaff;
        box-shadow: 0 8px 32px rgba(0, 40, 120, 0.4), inset 0 0 20px rgba(80, 180, 255, 0.08);
        z-index: 10;
        user-select: none;
    }

    #infoPanel { top: 20px; left: 20px; max-width: 280px; }
    #infoPanel h1 {
        font-size: 22px;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #4fc3f7, #81d4fa, #b39ddb);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    #infoPanel ul { list-style: none; font-size: 13px; line-height: 1.7; opacity: 0.9; }
    #infoPanel li::before { content: "• "; color: #4fc3f7; }

    .btn-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    button {
        cursor: pointer;
        border: 1px solid rgba(120, 220, 255, 0.4);
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 13px;
        font-weight: 600;
        color: #eaf6ff;
        background: linear-gradient(135deg, #1565c0, #0d47a1);
        transition: all 0.25s ease;
        box-shadow: 0 3px 10px rgba(0, 80, 200, 0.3);
    }
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(60, 160, 255, 0.5);
        background: linear-gradient(135deg, #1e88e5, #1565c0);
    }
    button:active { transform: translateY(0); }

    #statsPanel { top: 20px; right: 20px; min-width: 160px; font-size: 14px; }
    #statsPanel .stat { display: flex; justify-content: space-between; margin: 6px 0; }
    #statsPanel .value { color: #4fc3f7; font-weight: bold; font-size: 16px; }
    #statsPanel h2 { font-size: 16px; margin-bottom: 8px; color: #81d4fa; }

    #hint {
        position: absolute; bottom: 18px; left: 50%; transform: translateX(-50%);
        color: rgba(180, 225, 255, 0.75); font-size: 13px;
        background: rgba(10, 30, 60, 0.4); padding: 8px 18px; border-radius: 20px;
        backdrop-filter: blur(8px); z-index: 10; pointer-events: none;
    }
</style>
</head>
<body>

<div id="infoPanel" class="glass-panel">
    <h1>🐠 3D Аквариум</h1>
    <ul>
        <li>ЛКМ — вращение камеры</li>
        <li>ПКМ — панорамирование</li>
        <li>Колесо — зум</li>
        <li>Клик по воде — кормление</li>
    </ul>
    <div class="btn-row">
        <button id="btnFish">+ Рыбка</button>
        <button id="btnBubbles">+ Пузыри</button>
        <button id="btnLight">💡 Свет</button>
    </div>
</div>

<div id="statsPanel" class="glass-panel">
    <h2>📊 Статистика</h2>
    <div class="stat"><span>Рыбки:</span><span class="value" id="fishCount">0</span></div>
    <div class="stat"><span>FPS:</span><span class="value" id="fps">0</span></div>
</div>

<div id="hint">🖱 Кликните по воде, чтобы покормить рыбок!</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
// ============================================================
const TANK = { w: 36, h: 24, d: 20 }; // ширина, высота, глубина
let scene, camera, renderer, controls, clock;
let sunLight;
let fishArray = [];
let bubbleArray = [];
let foodArray = [];
let algaeArray = [];
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2();
let waterPlane = null; // невидимая плоскость для raycast кликов

// Цветовые схемы рыбок
const FISH_COLORS = [
    { body: 0xff8c42, fin: 0xff6b35 },   // оранжевая
    { body: 0x4a90d9, fin: 0x2c5f9e },   // синяя
    { body: 0xffd93d, fin: 0xe63946 },   // жёлто-красная
    { body: 0x9b5de5, fin: 0x7209b7 },   // фиолетовая
    { body: 0xef476f, fin: 0xc1121f },   // красная
    { body: 0x06d6a0, fin: 0x048a5e },   // зелёная
    { body: 0xffa6c9, fin: 0xf072a0 },   // розовая
    { body: 0xffc300, fin: 0xd4a017 }    // золотая
];

// ============================================================
// ИНИЦИАЛИЗАЦИЯ СЦЕНЫ
// ============================================================
function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x04122e);
    scene.fog = new THREE.FogExp2(0x0a2a5e, 0.012);

    camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 500);
    camera.position.set(30, 18, 42);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 10;
    controls.maxDistance = 60;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.target.set(0, 4, 0);

    clock = new THREE.Clock();

    createLights();
    createTank();
    createSand();
    createRocks();
    createAlgae();
    createWaterPlane();

    for (let i = 0; i < 15; i++) addFish();
    for (let i = 0; i < 30; i++) addBubble(true);

    setupUI();
    window.addEventListener('resize', onResize);
    renderer.domElement.addEventListener('click', onClick);

    animate();
}

// ============================================================
// ОСВЕЩЕНИЕ
// ============================================================
function createLights() {
    const ambient = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambient);

    sunLight = new THREE.DirectionalLight(0xbfdfff, 1.1);
    sunLight.position.set(20, 40, 15);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.set(2048, 2048);
    sunLight.shadow.camera.left = -30;
    sunLight.shadow.camera.right = 30;
    sunLight.shadow.camera.top = 30;
    sunLight.shadow.camera.bottom = -30;
    sunLight.shadow.camera.near = 1;
    sunLight.shadow.camera.far = 100;
    scene.add(sunLight);

    const point1 = new THREE.PointLight(0x4fc3f7, 0.8, 60);
    point1.position.set(-12, 10, 0);
    scene.add(point1);

    const point2 = new THREE.PointLight(0x2196f3, 0.8, 60);
    point2.position.set(12, 8, 5);
    scene.add(point2);
}

// ============================================================
// АКВАРИУМ (СТЕКЛЯННЫЙ КОНТЕЙНЕР)
// ============================================================
function createTank() {
    const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0xaaddff,
        metalness: 0,
        roughness: 0.05,
        transmission: 0.95,
        transparent: true,
        opacity: 0.15,
        side: THREE.DoubleSide,
        depthWrite: false
    });

    const glassGeo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
    const glass = new THREE.Mesh(glassGeo, glassMat);
    glass.position.y = TANK.h / 2;
    scene.add(glass);

    // Рамка (wireframe)
    const edges = new THREE.EdgesGeometry(glassGeo);
    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x8ecae6 }));
    line.position.copy(glass.position);
    scene.add(line);
}

// ============================================================
// ПЕСЧАНОЕ ДНО
// ============================================================
function createSand() {
    const geo = new THREE.PlaneGeometry(TANK.w - 1, TANK.d - 1, 40, 40);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        pos.setZ(i, Math.random() * 0.35 + Math.sin(pos.getX(i) * 0.5) * 0.15);
    }
    geo.computeVertexNormals();

    const mat = new THREE.MeshStandardMaterial({ color: 0xd9c08a, roughness: 1 });
    const sand = new THREE.Mesh(geo, mat);
    sand.rotation.x = -Math.PI / 2;
    sand.position.y = 0.2;
    sand.receiveShadow = true;
    scene.add(sand);
}

// ============================================================
// КАМНИ
// ============================================================
function createRocks() {
    for (let i = 0; i < 8; i++) {
        const size = 0.8 + Math.random() * 1.6;
        const geo = new THREE.DodecahedronGeometry(size, 1);
        // Деформация вершин
        const pos = geo.attributes.position;
        const v = new THREE.Vector3();
        for (let j = 0; j < pos.count; j++) {
            v.fromBufferAttribute(pos, j);
            v.multiplyScalar(0.85 + Math.random() * 0.3);
            pos.setXYZ(j, v.x, v.y, v.z);
        }
        geo.computeVertexNormals();

        const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.15, 0.25 + Math.random() * 0.15),
            roughness: 0.9
        }));
        rock.position.set(
            (Math.random() - 0.5) * (TANK.w - 8),
            size * 0.4,
            (Math.random() - 0.5) * (TANK.d - 6)
        );
        rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
        rock.castShadow = true;
        rock.receiveShadow = true;
        scene.add(rock);
    }
}

// ============================================================
// ВОДОРОСЛИ
// ============================================================
function createAlgae() {
    for (let i = 0; i < 12; i++) {
        const height = 3 + Math.random() * 5;
        const points = [];
        const sway = 0.4 + Math.random() * 0.5;
        for (let j = 0; j <= 6; j++) {
            const t = j / 6;
            points.push(new THREE.Vector3(
                Math.sin(t * 3 + i) * sway * t,
                t * height,
                Math.cos(t * 2.5 + i) * sway * t
            ));
        }
        const curve = new THREE.CatmullRomCurve3(points);
        const geo = new THREE.TubeGeometry(curve, 12, 0.18 - height * 0.015, 5, false);
        const mat = new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.32 + Math.random() * 0.08, 0.7, 0.3 + Math.random() * 0.15),
            roughness: 0.8
        });
        const weed = new THREE.Mesh(geo, mat);
        weed.position.set(
            (Math.random() - 0.5) * (TANK.w - 10),
            0.3,
            (Math.random() - 0.5) * (TANK.d - 8)
        );
        weed.castShadow = true;
        scene.add(weed);
        algaeArray.push({ mesh: weed, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.8 });
    }
}

// Невидимая плоскость воды для raycast кликов
function createWaterPlane() {
    waterPlane = new THREE.Mesh(
        new THREE.PlaneGeometry(TANK.w, TANK.d),
        new THREE.MeshBasicMaterial({ visible: false })
    );
    waterPlane.rotation.x = -Math.PI / 2;
    waterPlane.position.y = TANK.h / 2;
    scene.add(waterPlane);
}

// ============================================================
// СОЗДАНИЕ РЫБКИ
// ============================================================
function createFishMesh(colorScheme) {
    const group = new THREE.Group();
    const bodyMat = new THREE.MeshStandardMaterial({ color: colorScheme.body, roughness: 0.4, metalness: 0.15 });
    const finMat = new THREE.MeshStandardMaterial({
        color: colorScheme.fin, roughness: 0.6, transparent: true, opacity: 0.85, side: THREE.DoubleSide
    });

    // Тело — вытянутая сфера
    const body = new THREE.Mesh(new THREE.SphereGeometry(0.6, 16, 12), bodyMat);
    body.scale.set(1.8, 0.85, 0.85);
    body.castShadow = true;
    group.add(body);

    // Хвост
    const tailGeo = new THREE.ConeGeometry(0.45, 0.9, 8);
    const tail = new THREE.Mesh(tailGeo, finMat);
    tail.rotation.z = -Math.PI / 2;
    tail.position.x = 1.35;
    group.add(tail);

    // Верхний плавник
    const topFinGeo = new THREE.ConeGeometry(0.35, 0.7, 4);
    const topFin = new THREE.Mesh(topFinGeo, finMat);
    topFin.position.set(-0.1, 0.6, 0);
    topFin.rotation.z = 0.3;
    group.add(topFin);

    // Боковые плавники
    const finGeo = new THREE.CircleGeometry(0.35, 8);
    const leftFin = new THREE.Mesh(finGeo, finMat);
    leftFin.position.set(0.1, -0.1, 0.55);
    leftFin.rotation.y = Math.PI / 2;
    leftFin.rotation.x = 0.4;
    group.add(leftFin);

    const rightFin = new THREE.Mesh(finGeo.clone(), finMat);
    rightFin.position.set(0.1, -0.1, -0.55);
    rightFin.rotation.y = -Math.PI / 2;
    rightFin.rotation.x = -0.4;
    group.add(rightFin);

    // Глаза
    const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
    const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });
    [-1, 1].forEach(side => {
        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.14, 10, 8), eyeWhiteMat);
        eye.position.set(-0.65, 0.15, side * 0.35);
        group.add(eye);
        const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 6), pupilMat);
        pupil.position.set(-0.75, 0.15, side * 0.42);
        group.add(pupil);
    });

    return { group, tail, leftFin, rightFin, topFin };
}

function addFish() {
    const scheme = FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)];
    const parts = createFishMesh(scheme);
    const scale = 0.6 + Math.random() * 0.6;
    parts.group.scale.setScalar(scale);
    parts.group.position.set(
        (Math.random() - 0.5) * (TANK.w - 8),
        2 + Math.random() * (TANK.h - 6),
        (Math.random() - 0.5) * (TANK.d - 6)
    );
    scene.add(parts.group);

    const dir = new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).normalize();

    fishArray.push({
        mesh: parts.group,
        tail: parts.tail,
        leftFin: parts.leftFin,
        rightFin: parts.rightFin,
        topFin: parts.topFin,
        velocity: dir.multiplyScalar(0.02),
        speed: 0.025 + Math.random() * 0.03,
        tailSpeed: 6 + Math.random() * 5,
        phase: Math.random() * Math.PI * 2,
        targetFood: null,
        avoidanceRadius: 2.5 + Math.random() * 1.5,
        wanderTimer: Math.random() * 3
    });

    updateStats();
}

// ============================================================
// ПУЗЫРИ
// ============================================================
function addBubble(randomY = false) {
    const r = 0.1 + Math.random() * 0.25;
    const geo = new THREE.SphereGeometry(r, 10, 8);
    const mat = new THREE.MeshPhysicalMaterial({
        color: 0xcceeff,
        metalness: 0,
        roughness: 0,
        transmission: 0.9,
        transparent: true,
        opacity: 0.35,
        clearcoat: 1
    });
    const bubble = new THREE.Mesh(geo, mat);
    bubble.position.set(
        (Math.random() - 0.5) * (TANK.w - 4),
        randomY ? Math.random() * TANK.h : 0.5,
        (Math.random() - 0.5) * (TANK.d - 4)
    );
    scene.add(bubble);
    bubbleArray.push({
        mesh: bubble,
        speed: 0.02 + Math.random() * 0.03,
        phase: Math.random() * Math.PI * 2,
        sway: 0.3 + Math.random() * 0.5
    });
}

// ============================================================
// СИСТЕМА КОРМЛЕНИЯ
// ============================================================
function spawnFood(position) {
    const geo = new THREE.SphereGeometry(0.22, 8, 6);
    const mat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.9 });
    const food = new THREE.Mesh(geo, mat);
    food.position.copy(position);
    food.castShadow = true;
    scene.add(food);
    foodArray.push({ mesh: food, velocity: new THREE.Vector3(0, -0.01, 0) });
}

// ============================================================
// UI
// ============================================================
function setupUI() {
    document.getElementById('btnFish').addEventListener('click', e => {
        e.stopPropagation();
        if (fishArray.length < 40) addFish();
    });
    document.getElementById('btnBubbles').addEventListener('click', e => {
        e.stopPropagation();
        for (let i = 0; i < 10; i++) addBubble();
    });
    let lightOn = true;
    document.getElementById('btnLight').addEventListener('click', e => {
        e.stopPropagation();
        lightOn = !lightOn;
        sunLight.intensity = lightOn ? 1.1 : 0.15;
        e.target.textContent = lightOn ? '💡 Свет' : '🌙 Тьма';
    });
}

function updateStats() {
    document.getElementById('fishCount').textContent = fishArray.length;
}

// ============================================================
// ОБРАБОТКА КЛИКА
// ============================================================
function onClick(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObject(waterPlane);
    if (hits.length > 0) {
        const p = hits[0].point;
        p.x = THREE.MathUtils.clamp(p.x, -TANK.w / 2 + 2, TANK.w / 2 - 2);
        p.z = THREE.MathUtils.clamp(p.z, -TANK.d / 2 + 2, TANK.d / 2 - 2);
        p.y = Math.min(p.y, TANK.h - 2);
        spawnFood(p);
        // Брызги пузырей
        for (let i = 0; i < 3; i++) addBubble(false);
    }
}

// ============================================================
// АНИМАЦИЯ
// ============================================================
let fpsFrames = 0, fpsTime = 0;

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    // FPS
    fpsFrames++;
    fpsTime += dt;
    if (fpsTime >= 0.5) {
        document.getElementById('fps').textContent = Math.round(fpsFrames / fpsTime);
        fpsFrames = 0; fpsTime = 0;
    }

    updateFood(dt);
    updateFish(dt, t);
    updateBubbles(dt, t);
    updateAlgae(t);

    controls.update();
    renderer.render(scene, camera);
}

// --- Корм ---
function updateFood(dt) {
    for (let i = foodArray.length - 1; i >= 0; i--) {
        const f = foodArray[i];
        f.velocity.y -= 0.15 * dt; // гравитация
        f.mesh.position.addScaledVector(f.velocity, dt * 60);
        // Лёгкое сопротивление воды
        f.velocity.multiplyScalar(0.98);
        if (f.mesh.position.y <= 0.5) {
            scene.remove(f.mesh);
            f.mesh.geometry.dispose();
            f.mesh.material.dispose();
            foodArray.splice(i, 1);
        }
    }
}

// --- Рыбки ---
function updateFish(dt, t) {
    const hw = TANK.w / 2 - 2;
    const hh = TANK.h - 2;
    const hd = TANK.d / 2 - 2;

    for (const fish of fishArray) {
        const pos = fish.mesh.position;
        const vel = fish.velocity;

        // Поиск корма
        fish.targetFood = null;
        let bestDist = 15;
        for (const food of foodArray) {
            const d = pos.distanceTo(food.mesh.position);
            if (d < bestDist) { bestDist = d; fish.targetFood = food; }
        }

        if (fish.targetFood) {
            // Преследование корма
            const dir = fish.targetFood.mesh.position.clone().sub(pos).normalize();
            vel.lerp(dir.multiplyScalar(fish.speed * 1.8), 0.08);
        } else {
            // Случайное блуждание
            fish.wanderTimer -= dt;
            if (fish.wanderTimer <= 0) {
                fish.wanderTimer = 2 + Math.random() * 4;
                vel.x += (Math.random() - 0.5) * 0.01;
                vel.y += (Math.random() - 0.5) * 0.006;
                vel.z += (Math.random() - 0.5) * 0.01;
            }
            // Нормализация скорости
            const len = vel.length();
            if (len > 0.001) vel.normalize().multiplyScalar(fish.speed);
        }

        // Избегание столкновений
        for (const other of fishArray) {
            if (other === fish) continue;
            const diff = pos.clone().sub(other.mesh.position);
            const dist = diff.length();
            if (dist < fish.avoidanceRadius && dist > 0.001) {
                vel.add(diff.normalize().multiplyScalar((fish.avoidanceRadius - dist) * 0.002));
            }
        }

        // Отражение от стен (плавное)
        if (pos.x > hw) vel.x -= 0.004;
        if (pos.x < -hw) vel.x += 0.004;
        if (pos.y > hh) vel.y -= 0.004;
        if (pos.y < 1.5) vel.y += 0.004;
        if (pos.z > hd) vel.z -= 0.004;
        if (pos.z < -hd) vel.z += 0.004;

        // Ограничение скорости
        const maxSp = fish.speed * 2;
        if (vel.length() > maxSp) vel.setLength(maxSp);

        pos.addScaledVector(vel, dt * 60);
        pos.x = THREE.MathUtils.clamp(pos.x, -hw, hw);
        pos.y = THREE.MathUtils.clamp(pos.y, 1.2, hh);
        pos.z = THREE.MathUtils.clamp(pos.z, -hd, hd);

        // Поворот в направлении движения
        if (vel.lengthSq() > 0.000001) {
            const targetQuat = new THREE.Quaternion();
            const lookAt = pos.clone().add(vel);
            const m = new THREE.Matrix4().lookAt(pos, lookAt, new THREE.Vector3(0, 1, 0));
            targetQuat.setFromRotationMatrix(m);
            fish.mesh.quaternion.slerp(targetQuat, 0.08);
        }

        // Анимация хвоста и плавников
        const tailAngle = Math.sin(t * fish.tailSpeed + fish.phase) * 0.55;
        fish.tail.rotation.y = tailAngle;
        fish.leftFin.rotation.x = 0.4 + Math.sin(t * fish.tailSpeed * 0.7 + fish.phase) * 0.3;
        fish.rightFin.rotation.x = -0.4 - Math.sin(t * fish.tailSpeed * 0.7 + fish.phase) * 0.3;
        fish.topFin.rotation.z = 0.3 + Math.sin(t * fish.tailSpeed * 0.5 + fish.phase) * 0.15;

        // Поглощение корма
        for (let i = foodArray.length - 1; i >= 0; i--) {
            const food = foodArray[i];
            if (pos.distanceTo(food.mesh.position) < 1.0) {
                scene.remove(food.mesh);
                foodArray.splice(i, 1);
                // Рост на 5%
                const s = fish.mesh.scale.x * 1.05;
                fish.mesh.scale.setScalar(Math.min(s, 2.5));
                fish.targetFood = null;
                break;
            }
        }
    }
}

// --- Пузыри ---
function updateBubbles(dt, t) {
    for (let i = bubbleArray.length - 1; i >= 0; i--) {
        const b = bubbleArray[i];
        b.mesh.position.y += b.speed * dt * 60;
        b.mesh.position.x += Math.sin(t * 2 + b.phase) * 0.008 * b.sway;
        b.mesh.position.z += Math.cos(t * 1.7 + b.phase) * 0.008 * b.sway;
        if (b.mesh.position.y > TANK.h - 0.5) {
            b.mesh.position.y = 0.3;
            b.mesh.position.x = (Math.random() - 0.5) * (TANK.w - 4);
            b.mesh.position.z = (Math.random() - 0.5) * (TANK.d - 4);
        }
    }
}

// --- Водоросли ---
function updateAlgae(t) {
    for (const a of algaeArray) {
        a.mesh.rotation.x = Math.sin(t * a.speed + a.phase) * 0.06;
        a.mesh.rotation.z = Math.cos(t * a.speed * 0.8 + a.phase) * 0.06;
    }
}

// ============================================================
// RESIZE
// ============================================================
function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

init();
</script>
</body>
</html>
```

## ✨ Что реализовано

| Компонент | Детали |
|-----------|--------|
| **Рыбки** | 15 шт., 8 цветовых схем, тело + хвост + 3 плавника + глаза с зрачками, масштаб 0.6–1.2 |
| **ИИ** | Избегание столкновений, плавное отражение от стен, блуждание, преследование корма (радиус 15), рост +5% после еды |
| **Аквариум** | Стеклянный бокс (`transmission: 0.95`) 36×24×20 с wireframe-рамкой |
| **Декор** | Процедурный песок, 8 деформированных камней, 12 водорослей из `TubeGeometry` с покачиванием |
| **Пузыри** | 30 шт., стеклянные, поднимаются с синусоидальным покачиванием, сбрасываются на дно |
| **Кормление** | Клик → raycast по плоскости воды → корм падает с гравитацией, рыбки атакуют |
| **Свет** | Ambient + Directional (тени 2048², PCFSoft) + 2 голубых PointLight, переключатель |
| **UI** | Glassmorphism-панели, градиентный заголовок, FPS-счётчик, 3 кнопки |

**Совет:** сохраните код как `aquarium.html` и откройте в браузере — всё работает без сборки. 🚀