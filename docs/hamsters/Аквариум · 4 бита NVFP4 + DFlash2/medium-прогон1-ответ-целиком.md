

# 🐠 3D Аквариум с Реалистичными Рыбками

Полный код в одном HTML-файле. Сохраните как `aquarium.html` и откройте в браузере.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #001a33; }
    canvas { display: block; }

    .panel {
        position: absolute;
        background: rgba(10, 30, 60, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(100, 180, 255, 0.25);
        border-radius: 14px;
        color: #dceeff;
        padding: 16px 20px;
        box-shadow: 0 8px 32px rgba(0, 20, 60, 0.5), inset 0 1px 0 rgba(255,255,255,0.1);
        z-index: 10;
    }

    #infoPanel { top: 20px; left: 20px; max-width: 270px; }
    #infoPanel h1 {
        font-size: 20px;
        background: linear-gradient(90deg, #4fc3f7, #b388ff, #ff8a65);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    #infoPanel p { font-size: 12.5px; line-height: 1.6; opacity: 0.85; margin-bottom: 6px; }
    #infoPanel .hint { color: #8fd3ff; }

    #statsPanel { top: 20px; right: 20px; text-align: right; min-width: 140px; }
    #statsPanel .stat { font-size: 15px; margin-bottom: 4px; }
    #statsPanel .value {
        font-weight: bold;
        font-size: 20px;
        color: #4fc3f7;
        text-shadow: 0 0 10px rgba(79, 195, 247, 0.6);
    }
    #fps { color: #a5d6a7 !important; }

    .btn-row { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
    button {
        cursor: pointer;
        border: none;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 12.5px;
        font-weight: 600;
        color: #fff;
        transition: transform 0.15s, box-shadow 0.15s, filter 0.15s;
    }
    button:hover { transform: translateY(-2px); filter: brightness(1.15); }
    button:active { transform: translateY(0); }

    #addFishBtn {
        background: linear-gradient(135deg, #ff7043, #ffab40);
        box-shadow: 0 4px 14px rgba(255, 112, 67, 0.4);
    }
    #bubbleBtn {
        background: linear-gradient(135deg, #29b6f6, #4dd0e1);
        box-shadow: 0 4px 14px rgba(41, 182, 246, 0.4);
    }
    #lightBtn {
        background: linear-gradient(135deg, #ffd54f, #ffb300);
        box-shadow: 0 4px 14px rgba(255, 213, 79, 0.4);
    }

    @media (max-width: 640px) {
        #infoPanel { max-width: 200px; padding: 12px; }
        #infoPanel p { font-size: 11px; }
        #statsPanel { padding: 10px; }
    }
</style>
</head>
<body>

<div class="panel" id="infoPanel">
    <h1>🐠 3D Аквариум</h1>
    <p><span class="hint">🖱️ ЛКМ + движение</span> — вращение камеры</p>
    <p><span class="hint">🖱️ ПКМ + движение</span> — панорама</p>
    <p><span class="hint">⚙️ Колесо</span> — зум</p>
    <p><span class="hint">🍽️ Клик по воде</span> — покормить рыбок!</p>
    <div class="btn-row">
        <button id="addFishBtn">+ Рыбка</button>
        <button id="bubbleBtn">+ Пузыри</button>
        <button id="lightBtn">💡 Свет</button>
    </div>
</div>

<div class="panel" id="statsPanel">
    <div class="stat">Рыбок: <span class="value" id="fishCount">0</span></div>
    <div class="stat">FPS: <span class="value" id="fps">--</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
//  ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
// ============================================================
const TANK = { w: 36, h: 24, d: 20 }; // размеры аквариума
let scene, camera, renderer, controls, clock;
let sunLight;
let fishArray = [];
let bubbleArray = [];
let foodArray = [];
let algaeArray = [];

// Границы для рыбок (с запасом от стенок)
const BOUNDS = new THREE.Vector3(TANK.w / 2 - 2, TANK.h / 2 - 2, TANK.d / 2 - 2);
const FLOOR_Y = -TANK.h / 2 + 1.5;

// 8 цветовых схем
const COLOR_SCHEMES = [
    { body: 0xff8c42, fin: 0xffb077 },   // оранжевая
    { body: 0x2196f3, fin: 0x64b5f6 },   // синяя
    { body: 0xffeb3b, fin: 0xf44336 },   // жёлто-красная
    { body: 0x9c27b0, fin: 0xba68c8 },   // фиолетовая
    { body: 0xe53935, fin: 0xef9a9a },   // красная
    { body: 0x43a047, fin: 0x81c784 },   // зелёная
    { body: 0xf06292, fin: 0xf8bbd0 },   // розовая
    { body: 0xffd700, fin: 0xfff176 }    // золотая
];

// ============================================================
//  ИНИЦИАЛИЗАЦИЯ СЦЕНЫ
// ============================================================
function init() {
    clock = new THREE.Clock();

    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

    camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 200);
    camera.position.set(0, 8, 45);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    // Градиентный фон
    const bgCanvas = document.createElement('canvas');
    bgCanvas.width = 2; bgCanvas.height = 512;
    const bgCtx = bgCanvas.getContext('2d');
    const grad = bgCtx.createLinearGradient(0, 0, 0, 512);
    grad.addColorStop(0, '#0a3d6b');
    grad.addColorStop(1, '#041225');
    bgCtx.fillStyle = grad;
    bgCtx.fillRect(0, 0, 2, 512);
    scene.background = new THREE.CanvasTexture(bgCanvas);

    setupLights();
    buildTank();
    buildSand();
    buildRocks();
    buildAlgae();

    // Рыбки
    for (let i = 0; i < 15; i++) addFish();

    // Пузыри
    for (let i = 0; i < 30; i++) addBubble(true);

    // Камера
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 10;
    controls.maxDistance = 60;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.target.set(0, 0, 0);

    // События
    window.addEventListener('resize', onResize);
    renderer.domElement.addEventListener('click', onClickFeed);
    document.getElementById('addFishBtn').addEventListener('click', () => addFish());
    document.getElementById('bubbleBtn').addEventListener('click', () => {
        for (let i = 0; i < 10; i++) addBubble(false);
    });
    let lightOn = true;
    document.getElementById('lightBtn').addEventListener('click', function () {
        lightOn = !lightOn;
        sunLight.intensity = lightOn ? 1.1 : 0.15;
        this.textContent = lightOn ? '💡 Свет' : '🌙 Тьма';
    });

    animate();
}

// ============================================================
//  ОСВЕЩЕНИЕ
// ============================================================
function setupLights() {
    scene.add(new THREE.AmbientLight(0x404040, 0.4));

    sunLight = new THREE.DirectionalLight(0xcfe8ff, 1.1);
    sunLight.position.set(15, 30, 15);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.set(2048, 2048);
    sunLight.shadow.camera.left = -25;
    sunLight.shadow.camera.right = 25;
    sunLight.shadow.camera.top = 25;
    sunLight.shadow.camera.bottom = -25;
    scene.add(sunLight);

    const p1 = new THREE.PointLight(0x00bcd4, 0.6, 60);
    p1.position.set(-12, -8, 8);
    scene.add(p1);

    const p2 = new THREE.PointLight(0x1565c0, 0.6, 60);
    p2.position.set(12, 5, -8);
    scene.add(p2);
}

// ============================================================
//  АКВАРИУМ (СТЕКЛО)
// ============================================================
function buildTank() {
    const geo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
    const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0xbfe3ff,
        metalness: 0,
        roughness: 0.05,
        transmission: 0.95,
        transparent: true,
        opacity: 0.15,
        side: THREE.DoubleSide,
        depthWrite: false
    });
    const glass = new THREE.Mesh(geo, glassMat);
    scene.add(glass);

    // Рамка
    const edges = new THREE.EdgesGeometry(geo);
    const frame = new THREE.LineSegments(edges,
        new THREE.LineBasicMaterial({ color: 0x66ccff, transparent: true, opacity: 0.6 }));
    scene.add(frame);
}

// ============================================================
//  ПЕСЧАНОЕ ДНО
// ============================================================
function buildSand() {
    const geo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 40);
    geo.rotateX(-Math.PI / 2);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        pos.setY(i, Math.sin(pos.getX(i) * 0.5) * 0.25 + Math.random() * 0.15);
    }
    geo.computeVertexNormals();
    const mat = new THREE.MeshStandardMaterial({ color: 0xd9b878, roughness: 0.95 });
    const sand = new THREE.Mesh(geo, mat);
    sand.position.y = -TANK.h / 2 + 0.3;
    sand.receiveShadow = true;
    scene.add(sand);
}

// ============================================================
//  КАМНИ
// ============================================================
function buildRocks() {
    for (let i = 0; i < 8; i++) {
        const size = 0.8 + Math.random() * 1.6;
        const geo = new THREE.DodecahedronGeometry(size, 0);
        // Деформация вершин
        const pos = geo.attributes.position;
        for (let v = 0; v < pos.count; v++) {
            pos.setXYZ(v,
                pos.getX(v) * (0.7 + Math.random() * 0.6),
                pos.getY(v) * (0.5 + Math.random() * 0.5),
                pos.getZ(v) * (0.7 + Math.random() * 0.6));
        }
        geo.computeVertexNormals();
        const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.2, 0.3 + Math.random() * 0.2),
            roughness: 0.9
        }));
        rock.position.set(
            (Math.random() - 0.5) * (TANK.w - 6),
            -TANK.h / 2 + size * 0.4,
            (Math.random() - 0.5) * (TANK.d - 6));
        rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
        rock.castShadow = true;
        rock.receiveShadow = true;
        scene.add(rock);
    }
}

// ============================================================
//  ВОДОРОСЛИ
// ============================================================
function buildAlgae() {
    for (let i = 0; i < 12; i++) {
        const height = 3 + Math.random() * 5;
        const points = [];
        const baseX = (Math.random() - 0.5) * (TANK.w - 8);
        const baseZ = (Math.random() - 0.5) * (TANK.d - 8);
        const sway = 0.4 + Math.random() * 0.5;
        for (let s = 0; s <= 5; s++) {
            points.push(new THREE.Vector3(
                baseX + Math.sin(s * 1.2) * sway * (s / 5),
                -TANK.h / 2 + 0.5 + (height * s) / 5,
                baseZ + Math.cos(s * 0.9) * sway * (s / 5)));
        }
        const curve = new THREE.CatmullRomCurve3(points);
        const geo = new THREE.TubeGeometry(curve, 10, 0.18 + Math.random() * 0.12, 5, false);
        const mat = new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.3 + Math.random() * 0.12, 0.7, 0.35),
            roughness: 0.8
        });
        const algae = new THREE.Mesh(geo, mat);
        algae.castShadow = true;
        algae.userData.phase = Math.random() * Math.PI * 2;
        algae.userData.speed = 0.5 + Math.random() * 0.8;
        scene.add(algae);
        algaeArray.push(algae);
    }
}

// ============================================================
//  СОЗДАНИЕ РЫБКИ
// ============================================================
function createFishMesh(colorScheme) {
    const group = new THREE.Group();
    const bodyMat = new THREE.MeshStandardMaterial({ color: colorScheme.body, roughness: 0.4, metalness: 0.15 });
    const finMat = new THREE.MeshStandardMaterial({
        color: colorScheme.fin, roughness: 0.5, transparent: true, opacity: 0.85, side: THREE.DoubleSide
    });

    // Тело — вытянутая сфера
    const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
    body.scale.set(1.6, 1, 0.7);
    body.castShadow = true;
    group.add(body);

    // Хвост — конус, анимируемый по Z
    const tail = new THREE.Mesh(new THREE.ConeGeometry(0.55, 1.2, 8), finMat);
    tail.rotation.z = Math.PI / 2;
    tail.position.x = -1.7;
    group.add(tail);

    // Верхний плавник
    const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.9, 6), finMat);
    topFin.position.set(0.2, 0.95, 0);
    group.add(topFin);

    // Боковые плавники
    const finGeo = new THREE.CircleGeometry(0.45, 8);
    const leftFin = new THREE.Mesh(finGeo, finMat);
    leftFin.position.set(0.3, -0.1, 0.65);
    leftFin.rotation.x = -Math.PI / 2;
    group.add(leftFin);

    const rightFin = leftFin.clone();
    rightFin.position.z = -0.65;
    rightFin.rotation.x = Math.PI / 2;
    group.add(rightFin);

    // Глаза
    const eyeWhiteGeo = new THREE.SphereGeometry(0.22, 10, 8);
    const pupilGeo = new THREE.SphereGeometry(0.11, 8, 6);
    const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
    const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });
    [0.35, -0.35].forEach(z => {
        const eye = new THREE.Mesh(eyeWhiteGeo, eyeMat);
        eye.position.set(1.0, 0.25, z);
        group.add(eye);
        const pupil = new THREE.Mesh(pupilGeo, pupilMat);
        pupil.position.set(1.18, 0.25, z);
        group.add(pupil);
    });

    return { group, tail, leftFin, rightFin };
}

function addFish() {
    const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
    const parts = createFishMesh(scheme);
    const scale = 0.6 + Math.random() * 0.6;
    parts.group.scale.setScalar(scale);
    parts.group.position.set(
        (Math.random() - 0.5) * (TANK.w - 8),
        (Math.random() - 0.5) * (TANK.h - 8),
        (Math.random() - 0.5) * (TANK.d - 8));
    scene.add(parts.group);

    const dir = new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).normalize();

    fishArray.push({
        mesh: parts.group,
        tail: parts.tail,
        leftFin: parts.leftFin,
        rightFin: parts.rightFin,
        velocity: dir.multiplyScalar(0.01 + Math.random() * 0.015),
        speed: 0.015 + Math.random() * 0.02,
        tailSpeed: 0.15 + Math.random() * 0.1,
        phase: Math.random() * Math.PI * 2,
        targetFood: null,
        avoidanceRadius: 2.5 + Math.random() * 1.5,
        wanderTimer: 0
    });

    document.getElementById('fishCount').textContent = fishArray.length;
}

// ============================================================
//  ПУЗЫРИ
// ============================================================
function addBubble(randomY) {
    const size = 0.1 + Math.random() * 0.25;
    const bubble = new THREE.Mesh(
        new THREE.SphereGeometry(size, 10, 8),
        new THREE.MeshPhysicalMaterial({
            color: 0xaaddff,
            transparent: true,
            opacity: 0.35,
            roughness: 0,
            metalness: 0,
            clearcoat: 1
        })
    );
    bubble.position.set(
        (Math.random() - 0.5) * (TANK.w - 4),
        randomY ? (Math.random() - 0.5) * (TANK.h - 4) : -TANK.h / 2 + 1,
        (Math.random() - 0.5) * (TANK.d - 4));
    bubble.userData = {
        speed: 0.02 + Math.random() * 0.04,
        phase: Math.random() * Math.PI * 2,
        amp: 0.3 + Math.random() * 0.5
    };
    scene.add(bubble);
    bubbleArray.push(bubble);
}

// ============================================================
//  СИСТЕМА КОРМЛЕНИЯ
// ============================================================
const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();

function onClickFeed(event) {
    mouseNDC.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouseNDC.y = -(event.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouseNDC, camera);

    // Проекция луча на плоскость z=0 (или ближайшую точку внутри аквариума)
    const point = new THREE.Vector3();
    if (!raycaster.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0, 0, 1), 0), point)) return;

    point.x = THREE.MathUtils.clamp(point.x, -BOUNDS.x, BOUNDS.x);
    point.y = THREE.MathUtils.clamp(point.y, FLOOR_Y, BOUNDS.y);
    point.z = THREE.MathUtils.clamp(point.z, -BOUNDS.z, BOUNDS.z);

    spawnFood(point);
}

function spawnFood(pos) {
    const food = new THREE.Mesh(
        new THREE.SphereGeometry(0.25, 8, 6),
        new THREE.MeshStandardMaterial({ color: 0xff6d00, emissive: 0xbf360c, roughness: 0.6 })
    );
    food.position.copy(pos);
    food.castShadow = true;
    scene.add(food);
    foodArray.push({ mesh: food, velocity: new THREE.Vector3((Math.random() - 0.5) * 0.01, 0, 0) });
}

// ============================================================
//  АНИМАЦИЯ / ИГРОВОЙ ЦИКЛ
// ============================================================
let fpsFrames = 0, fpsTime = 0;

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    updateFish(dt, t);
    updateBubbles(dt, t);
    updateFood(dt);
    updateAlgae(t);

    controls.update();
    renderer.render(scene, camera);

    // FPS
    fpsFrames++;
    fpsTime += dt;
    if (fpsTime >= 0.5) {
        document.getElementById('fps').textContent = Math.round(fpsFrames / fpsTime);
        fpsFrames = 0; fpsTime = 0;
    }
}

function updateFish(dt, t) {
    for (const fish of fishArray) {
        const pos = fish.mesh.position;

        // --- Поиск корма ---
        if (!fish.targetFood || !fish.targetFood.active) {
            fish.targetFood = null;
            for (const f of foodArray) {
                if (pos.distanceTo(f.mesh.position) < 15) { fish.targetFood = f; break; }
            }
        }

        // --- Направление ---
        let desired;
        if (fish.targetFood) {
            desired = fish.targetFood.mesh.position.clone().sub(pos).normalize();
        } else {
            // Случайное блуждание
            fish.wanderTimer -= dt;
            if (fish.wanderTimer <= 0) {
                fish.wanderTimer = 1 + Math.random() * 3;
                const rnd = new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.6, Math.random() - 0.5).normalize();
                fish.velocity.lerp(rnd, 0.5).normalize();
            }
            desired = fish.velocity.clone();
        }

        // --- Избегание других рыбок ---
        for (const other of fishArray) {
            if (other === fish) continue;
            const diff = pos.clone().sub(other.mesh.position);
            const dist = diff.length();
            if (dist < fish.avoidanceRadius && dist > 0.001) {
                desired.add(diff.normalize().multiplyScalar(2 / dist));
            }
        }

        // --- Отражение от стенок ---
        const wallDist = 2;
        if (pos.x > BOUNDS.x - wallDist) desired.x -= 1.5;
        if (pos.x < -BOUNDS.x + wallDist) desired.x += 1.5;
        if (pos.y > BOUNDS.y - wallDist) desired.y -= 1.5;
        if (pos.y < FLOOR_Y + wallDist) desired.y += 1.5;
        if (pos.z > BOUNDS.z - wallDist) desired.z -= 1.5;
        if (pos.z < -BOUNDS.z + wallDist) desired.z += 1.5;

        desired.normalize();

        // Плавный поворот скорости к желаемому направлению
        const turnSpeed = fish.targetFood ? 3.5 : 1.2;
        fish.velocity.lerp(desired, Math.min(1, turnSpeed * dt)).normalize();

        // Ускорение при погоне за едой
        const curSpeed = fish.targetFood ? fish.speed * 2.2 : fish.speed;
        pos.addScaledVector(fish.velocity, curSpeed * dt * 60);

        // Жёсткий клэмп
        pos.x = THREE.MathUtils.clamp(pos.x, -BOUNDS.x, BOUNDS.x);
        pos.y = THREE.MathUtils.clamp(pos.y, FLOOR_Y, BOUNDS.y);
        pos.z = THREE.MathUtils.clamp(pos.z, -BOUNDS.z, BOUNDS.z);

        // Поворот в направлении движения
        const lookTarget = pos.clone().add(fish.velocity);
        fish.mesh.lookAt(lookTarget);

        // --- Анимация хвоста и плавников ---
        const tailAngle = Math.sin(t * fish.tailSpeed * 10 + fish.phase) * 0.5;
        fish.tail.rotation.z = Math.PI / 2 + tailAngle;
        const finAngle = Math.sin(t * fish.tailSpeed * 8 + fish.phase + 1) * 0.35;
        fish.leftFin.rotation.x = -Math.PI / 2 + finAngle;
        fish.rightFin.rotation.x = Math.PI / 2 - finAngle;

        // --- Поглощение корма ---
        if (fish.targetFood) {
            const dist = pos.distanceTo(fish.targetFood.mesh.position);
            if (dist < 0.8) {
                eatFood(fish, fish.targetFood);
            }
        }
    }

    // Чистим съеденный корм
    foodArray = foodArray.filter(f => f.active !== false);
}

function eatFood(fish, food) {
    food.active = false;
    scene.remove(food.mesh);
    food.mesh.geometry.dispose();
    food.mesh.material.dispose();
    // Рост на 5%
    const s = fish.mesh.scale.x * 1.05;
    fish.mesh.scale.setScalar(s);
}

function updateFood(dt) {
    for (const f of foodArray) {
        if (f.active === false) continue;
        f.velocity.y -= 0.0005; // гравитация
        f.mesh.position.addScaledVector(f.velocity, dt * 60);
        // Удаление при достижении дна
        if (f.mesh.position.y < FLOOR_Y - 0.3) {
            f.active = false;
            scene.remove(f.mesh);
            f.mesh.geometry.dispose();
            f.mesh.material.dispose();
        }
    }
}

function updateBubbles(dt, t) {
    for (const b of bubbleArray) {
        b.position.y += b.userData.speed * dt * 60;
        b.position.x += Math.sin(t * 1.5 + b.userData.phase) * 0.008 * b.userData.amp;
        b.position.z += Math.cos(t * 1.2 + b.userData.phase) * 0.008 * b.userData.amp;
        if (b.position.y > TANK.h / 2 - 0.5) {
            b.position.y = -TANK.h / 2 + 1;
            b.position.x = (Math.random() - 0.5) * (TANK.w - 4);
            b.position.z = (Math.random() - 0.5) * (TANK.d - 4);
        }
    }
}

function updateAlgae(t) {
    for (const a of algaeArray) {
        a.rotation.x = Math.sin(t * a.userData.speed + a.userData.phase) * 0.06;
        a.rotation.z = Math.cos(t * a.userData.speed * 0.8 + a.userData.phase) * 0.06;
    }
}

// ============================================================
//  РЕСАЙЗ
// ============================================================
function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Старт
init();
</script>
</body>
</html>
```

## ✨ Что реализовано

| Система | Детали |
|---|---|
| **🐠 Рыбки** | 15 шт., 8 цветовых схем, тело/хвост/3 плавника/глаза с зрачками, масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, отражение от стенок, блуждание, погоня за кормом (радиус 15), рост +5% |
| **🏛️ Окружение** | Стекло с `transmission: 0.95`, рамка-edges, песок с процедурными буграми, 8 деформированных камней, 12 водорослей из `TubeGeometry` |
| **💭 Пузыри** | 30 шт., покачивание sin/cos, сброс у поверхности |
| **🍽️ Кормление** | Клик → корм с гравитацией → рыбки плывут быстрее → съедают → растут |
| **💡 Свет** | Ambient + Directional (тени 2048², PCFSoft) + 2 PointLight, кнопка переключения |
| **🎮 Камера** | OrbitControls с damping, зум 10–60, ограничение полярного угла |
| **🖥️ UI** | Glass-панели с blur, счётчики, 3 кнопки, адаптив |

## 💡 Идеи для развития
- **Частицы плавающих частиц** (marine snow) через `Points`
- **Звуки** — бульканье пузырей через Web Audio API
- **Сохранение состояния** — localStorage для размера рыбок
- **Столкновения с камнями** — AABB-проверки

Хотите, чтобы я добавил что-то из этого? 🚀