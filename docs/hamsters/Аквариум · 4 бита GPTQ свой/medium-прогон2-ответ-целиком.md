

# 🐠 3D Аквариум с Реалистичными Рыбками

Полный код в одном HTML-файле. Сохраните как `aquarium.html` и откройте в браузере.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Аквариум</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #001a33; }
    canvas { display: block; }

    .panel {
        position: absolute;
        background: rgba(10, 30, 60, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(100, 180, 255, 0.25);
        border-radius: 14px;
        color: #cfe8ff;
        padding: 16px 20px;
        box-shadow: 0 8px 32px rgba(0, 40, 90, 0.5), inset 0 0 20px rgba(80, 160, 255, 0.08);
        z-index: 10;
    }

    #infoPanel { top: 20px; left: 20px; max-width: 300px; }
    #statsPanel { top: 20px; right: 20px; text-align: right; min-width: 160px; }

    h1 {
        font-size: 22px;
        background: linear-gradient(90deg, #4dd0ff, #7affb0, #ffd84d);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    .instructions { font-size: 12px; line-height: 1.7; opacity: 0.85; margin-bottom: 12px; }
    .instructions b { color: #7affb0; }

    .stat-row { display: flex; justify-content: space-between; gap: 16px; font-size: 14px; margin-bottom: 6px; }
    .stat-value { color: #ffd84d; font-weight: bold; }

    .btn-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    button {
        cursor: pointer;
        border: none;
        border-radius: 10px;
        padding: 9px 14px;
        font-size: 13px;
        font-weight: 600;
        color: #fff;
        background: linear-gradient(135deg, #1e6fd9, #14a08a);
        box-shadow: 0 4px 14px rgba(30, 111, 217, 0.45);
        transition: transform 0.15s, box-shadow 0.15s, filter 0.15s;
    }
    button:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 6px 22px rgba(60, 160, 255, 0.7);
        filter: brightness(1.15);
    }
    button:active { transform: translateY(0) scale(0.98); }
    button.gold { background: linear-gradient(135deg, #d9a51e, #e06a14); box-shadow: 0 4px 14px rgba(217, 165, 30, 0.45); }
    button.pink { background: linear-gradient(135deg, #d94f9e, #8a14d0); box-shadow: 0 4px 14px rgba(217, 79, 158, 0.45); }

    @media (max-width: 600px) {
        #infoPanel { max-width: 200px; padding: 10px; }
        .instructions { display: none; }
    }
</style>
</head>
<body>

<div class="panel" id="infoPanel">
    <h1>🐠 3D Аквариум</h1>
    <div class="instructions">
        <b>ЛКМ + движение</b> — вращение камеры<br>
        <b>ПКМ + движение</b> — панорамирование<br>
        <b>Колесо</b> — зум<br>
        <b>Клик по дну</b> — покормить рыбок 🍽️
    </div>
    <div class="btn-row">
        <button id="addFishBtn">+ Рыбка</button>
        <button id="bubblesBtn" class="pink">+ Пузыри</button>
        <button id="lightBtn" class="gold">💡 Свет</button>
    </div>
</div>

<div class="panel" id="statsPanel">
    <div class="stat-row"><span>🐟 Рыбки:</span><span class="stat-value" id="fishCount">0</span></div>
    <div class="stat-row"><span>📊 FPS:</span><span class="stat-value" id="fpsCounter">0</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
//  ОБЩЕЕ
// ============================================================
const TANK = { w: 36, h: 20, d: 24 }; // ширина(x), высота(y), глубина(z)
const MARGIN = 1.5;

let scene, camera, renderer, controls;
let sunLight;
let fishArray = [];
let bubbleArray = [];
let foodArray = [];
let sandMesh;
let clock = new THREE.Clock();
let elapsed = 0;

// Счётчик FPS
let fpsFrames = 0, fpsTime = 0;

// 8 цветовых схем: [тело, плавники, брюхо]
const PALETTES = [
    { body: 0xff7722, fin: 0xffaa55, belly: 0xffd9a0 }, // оранжевая
    { body: 0x2266ff, fin: 0x55aaff, belly: 0xaad4ff }, // синяя
    { body: 0xffcc00, fin: 0xff3322, belly: 0xffee99 }, // жёлто-красная
    { body: 0x9933ff, fin: 0xbb77ff, belly: 0xe0ccff }, // фиолетовая
    { body: 0xff2233, fin: 0xff6666, belly: 0xffcccc }, // красная
    { body: 0x22bb55, fin: 0x66ee99, belly: 0xccffdd }, // зелёная
    { body: 0xff66aa, fin: 0xffaacc, belly: 0xffdded }, // розовая
    { body: 0xffb300, fin: 0xffd966, belly: 0xfff0b3 }  // золотая
];

// ============================================================
//  ИНИЦИАЛИЗАЦИЯ СЦЕНЫ
// ============================================================
function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x001a33);
    scene.fog = new THREE.FogExp2(0x0a2a50, 0.012);

    camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 200);
    camera.position.set(0, 14, 42);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(innerWidth, innerHeight);
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 2, 0);
    controls.minDistance = 10;
    controls.maxDistance = 60;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;

    createLights();
    createTank();
    createSand();
    createRocks();
    createWeeds();

    for (let i = 0; i < 15; i++) addFish();
    addBubbles(30);

    window.addEventListener('resize', onResize);
    renderer.domElement.addEventListener('click', onFeedClick);

    animate();
}

// ============================================================
//  ОСВЕЩЕНИЕ
// ============================================================
function createLights() {
    scene.add(new THREE.AmbientLight(0x404040, 0.4));

    sunLight = new THREE.DirectionalLight(0xcfe8ff, 1.1);
    sunLight.position.set(15, 30, 10);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.set(2048, 2048);
    sunLight.shadow.camera.left = -25;
    sunLight.shadow.camera.right = 25;
    sunLight.shadow.camera.top = 25;
    sunLight.shadow.camera.bottom = -25;
    scene.add(sunLight);

    const p1 = new THREE.PointLight(0x33ccff, 0.6, 50);
    p1.position.set(-10, 8, 8);
    scene.add(p1);

    const p2 = new THREE.PointLight(0x2255ff, 0.5, 50);
    p2.position.set(10, 6, -8);
    scene.add(p2);
}

// ============================================================
//  СТЕКЛЯННЫЙ КОНТЕЙНЕР
// ============================================================
function createTank() {
    const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0x88ccff,
        transparent: true,
        opacity: 0.12,
        transmission: 0.95,
        roughness: 0.05,
        metalness: 0,
        side: THREE.DoubleSide,
        depthWrite: false
    });

    const geo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
    const glass = new THREE.Mesh(geo, glassMat);
    glass.position.y = TANK.h / 2;
    scene.add(glass);

    const edges = new THREE.LineSegments(
        new THREE.EdgesGeometry(geo),
        new THREE.LineBasicMaterial({ color: 0x66bbff, transparent: true, opacity: 0.6 })
    );
    edges.position.copy(glass.position);
    scene.add(edges);
}

// ============================================================
//  ПЕСЧАНОЕ ДНО
// ============================================================
function createSand() {
    const geo = new THREE.PlaneGeometry(TANK.w - 1, TANK.d - 1, 40, 40);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i), y = pos.getY(i);
        pos.setZ(i,
            Math.sin(x * 0.5) * Math.cos(y * 0.4) * 0.35 +
            Math.sin(x * 1.3 + y * 0.9) * 0.15
        );
    }
    geo.computeVertexNormals();

    const mat = new THREE.MeshStandardMaterial({ color: 0xd9b478, roughness: 1 });
    sandMesh = new THREE.Mesh(geo, mat);
    sandMesh.rotation.x = -Math.PI / 2;
    sandMesh.receiveShadow = true;
    scene.add(sandMesh);
}

// ============================================================
//  КАМНИ
// ============================================================
function createRocks() {
    for (let i = 0; i < 8; i++) {
        const size = 0.8 + Math.random() * 1.6;
        const geo = new THREE.DodecahedronGeometry(size, 1);
        const p = geo.attributes.position;
        for (let j = 0; j < p.count; j++) {
            p.setXYZ(j,
                p.getX(j) * (0.8 + Math.random() * 0.4),
                p.getY(j) * (0.6 + Math.random() * 0.5),
                p.getZ(j) * (0.8 + Math.random() * 0.4)
            );
        }
        geo.computeVertexNormals();

        const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.15, 0.25 + Math.random() * 0.2),
            roughness: 0.9
        }));
        rock.position.set(
            (Math.random() - 0.5) * (TANK.w - 6),
            0.4,
            (Math.random() - 0.5) * (TANK.d - 6)
        );
        rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
        rock.castShadow = true;
        rock.receiveShadow = true;
        scene.add(rock);
    }
}

// ============================================================
//  ВОДОРОССЫ
// ============================================================
const weedList = [];
function createWeeds() {
    for (let i = 0; i < 12; i++) {
        const height = 4 + Math.random() * 6;
        const pts = [];
        const baseX = (Math.random() - 0.5) * (TANK.w - 6);
        const baseZ = (Math.random() - 0.5) * (TANK.d - 6);
        for (let s = 0; s <= 5; s++) {
            const t = s / 5;
            pts.push(new THREE.Vector3(
                baseX + Math.sin(t * 3 + i) * 0.6 * t,
                t * height,
                baseZ + Math.cos(t * 2.5 + i) * 0.6 * t
            ));
        }
        const curve = new THREE.CatmullRomCurve3(pts);
        const geo = new THREE.TubeGeometry(curve, 12, 0.18 + Math.random() * 0.12, 6, false);
        const weed = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.3 + Math.random() * 0.1, 0.7, 0.3 + Math.random() * 0.2),
            roughness: 0.8
        }));
        // Пивот у корня для покачивания
        weed.position.sub(pts[0]);
        const holder = new THREE.Group();
        holder.position.copy(pts[0]);
        holder.add(weed);
        scene.add(holder);
        weedList.push({ obj: holder, phase: Math.random() * Math.PI * 2, speed: 0.8 + Math.random() * 0.8 });
    }
}

// ============================================================
//  РЫБКА
// ============================================================
function addFish(x, y, z) {
    const pal = PALETTES[Math.floor(Math.random() * PALETTES.length)];
    const g = new THREE.Group();
    const scale = 0.6 + Math.random() * 0.6;

    const bodyMat = new THREE.MeshStandardMaterial({ color: pal.body, roughness: 0.35, metalness: 0.15 });
    const finMat = new THREE.MeshStandardMaterial({
        color: pal.fin, roughness: 0.5, transparent: true, opacity: 0.85, side: THREE.DoubleSide
    });

    // Тело (вытянутая сфера)
    const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
    body.scale.set(1.7, 1, 0.75);
    body.castShadow = true;
    g.add(body);

    // Брюшко
    const belly = new THREE.Mesh(new THREE.SphereGeometry(0.75, 12, 8),
        new THREE.MeshStandardMaterial({ color: pal.belly, roughness: 0.5 }));
    belly.scale.set(1.3, 0.85, 0.7);
    belly.position.set(0, -0.15, 0);
    g.add(belly);

    // Глаза
    const eyeWhite = new THREE.SphereGeometry(0.22, 10, 8);
    const pupilGeo = new THREE.SphereGeometry(0.11, 8, 6);
    const pupilMat = new THREE.MeshBasicMaterial({ color: 0x0a0a0a });
    [-1, 1].forEach(side => {
        const ew = new THREE.Mesh(eyeWhite, new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 }));
        ew.position.set(1.2, 0.25, side * 0.42);
        g.add(ew);
        const pu = new THREE.Mesh(pupilGeo, pupilMat);
        pu.position.set(1.38, 0.25, side * 0.42);
        g.add(pu);
    });

    // Хвост — группа-пивот на заднем конце
    const tailPivot = new THREE.Group();
    tailPivot.position.set(-1.7, 0, 0);
    const tail = new THREE.Mesh(new THREE.ConeGeometry(0.7, 1.4, 8), finMat);
    tail.rotation.z = Math.PI / 2;
    tail.scale.set(1, 0.35, 1);
    tail.position.x = -0.7;
    tailPivot.add(tail);
    g.add(tailPivot);

    // Верхний плавник
    const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.5, 0.9, 6), finMat);
    topFin.scale.set(1, 1, 0.25);
    topFin.position.set(-0.2, 0.85, 0);
    topFin.rotation.z = Math.PI;
    g.add(topFin);

    // Боковые плавники
    const finGeo = new THREE.ConeGeometry(0.4, 0.8, 6);
    const leftFin = new THREE.Mesh(finGeo, finMat);
    leftFin.scale.set(0.3, 1, 1);
    leftFin.rotation.z = -Math.PI / 2.3;
    leftFin.position.set(0.3, -0.3, 0.6);
    g.add(leftFin);
    const rightFin = new THREE.Mesh(finGeo, finMat);
    rightFin.scale.set(0.3, 1, 1);
    rightFin.rotation.z = -Math.PI / 2.3;
    rightFin.position.set(0.3, -0.3, -0.6);
    g.add(rightFin);

    g.scale.setScalar(scale);
    g.position.set(
        x !== undefined ? x : (Math.random() - 0.5) * (TANK.w - 8),
        y !== undefined ? y : 3 + Math.random() * (TANK.h - 8),
        z !== undefined ? z : (Math.random() - 0.5) * (TANK.d - 8)
    );
    scene.add(g);

    const v = new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.4, Math.random() - 0.5).normalize();
    fishArray.push({
        mesh: g,
        tail: tailPivot,
        leftFin, rightFin,
        velocity: v.clone(),
        speed: 2.5 + Math.random() * 2.5,
        tailSpeed: 6 + Math.random() * 4,
        phase: Math.random() * Math.PI * 2,
        targetFood: null,
        avoidanceRadius: 2.5 + Math.random() * 1.5,
        wanderTimer: Math.random() * 3
    });
    updateStats();
}

// ============================================================
//  БУБЕЛЬКИ
// ============================================================
function addBubbles(n) {
    for (let i = 0; i < n; i++) {
        const r = 0.08 + Math.random() * 0.22;
        const b = new THREE.Mesh(new THREE.SphereGeometry(r, 10, 8), new THREE.MeshPhysicalMaterial({
            color: 0xbbeeff, transparent: true, opacity: 0.35,
            transmission: 0.8, roughness: 0.05, metalness: 0
        }));
        b.position.set(
            (Math.random() - 0.5) * (TANK.w - 4),
            Math.random() * TANK.h,
            (Math.random() - 0.5) * (TANK.d - 4)
        );
        scene.add(b);
        bubbleArray.push({
            mesh: b,
            baseX: b.position.x,
            baseZ: b.position.z,
            speed: 1.5 + Math.random() * 2.5,
            phase: Math.random() * Math.PI * 2
        });
    }
}

// ============================================================
//  КОРМ
// ============================================================
const foodGeo = new THREE.SphereGeometry(0.25, 8, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xd98833, emissive: 0x552200, roughness: 0.7 });

function spawnFood(pos) {
    const f = new THREE.Mesh(foodGeo, foodMat.clone());
    f.castShadow = true;
    f.position.copy(pos);
    scene.add(f);
    foodArray.push({ mesh: f, vy: 0 });
}

function onFeedClick(e) {
    const mouse = new THREE.Vector2((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
    const ray = new THREE.Raycaster();
    ray.setFromCamera(mouse, camera);
    const hits = ray.intersectObject(sandMesh);
    if (hits.length > 0) {
        const p = hits[0].point;
        p.y += 6 + Math.random() * 6; // корм падает сверху
        p.x = THREE.MathUtils.clamp(p.x, -TANK.w/2 + 2, TANK.w/2 - 2);
        p.z = THREE.MathUtils.clamp(p.z, -TANK.d/2 + 2, TANK.d/2 - 2);
        spawnFood(p);
    }
}

// ============================================================
//  ИИ РЫБОК
// ============================================================
function updateFish(dt) {
    const minX = -TANK.w/2 + MARGIN, maxX = TANK.w/2 - MARGIN;
    const minY = 1.5, maxY = TANK.h - MARGIN;
    const minZ = -TANK.d/2 + MARGIN, maxZ = TANK.d/2 - MARGIN;

    for (let i = fishArray.length - 1; i >= 0; i--) {
        const f = fishArray[i];

        // --- Поиск корма ---
        f.targetFood = null;
        let bestDist = 15;
        for (const food of foodArray) {
            const d = f.mesh.position.distanceTo(food.mesh.position);
            if (d < bestDist) { bestDist = d; f.targetFood = food; }
        }

        const desired = f.velocity.clone();

        if (f.targetFood) {
            desired.copy(f.targetFood.mesh.position).sub(f.mesh.position).normalize();
            // Съедание
            const eatR = 1.2 * f.mesh.scale.x;
            if (f.mesh.position.distanceTo(f.targetFood.mesh.position) < eatR) {
                scene.remove(f.targetFood.mesh);
                foodArray.splice(foodArray.indexOf(f.targetFood), 1);
                f.mesh.scale.multiplyScalar(1.05); // рост на 5%
                f.targetFood = null;
            }
        } else {
            // --- Случайное блуждание ---
            f.wanderTimer -= dt;
            if (f.wanderTimer <= 0) {
                f.wanderTimer = 2 + Math.random() * 4;
                const a = Math.random() * Math.PI * 2;
                const b = (Math.random() - 0.5) * 0.6;
                f.velocity.set(Math.cos(a), b, Math.sin(a)).normalize();
            }
            desired.copy(f.velocity);
        }

        // --- Избегание других рыбок ---
        for (const other of fishArray) {
            if (other === f) continue;
            const diff = f.mesh.position.clone().sub(other.mesh.position);
            const dist = diff.length();
            const r = f.avoidanceRadius * (f.mesh.scale.x + other.mesh.scale.x) * 0.5;
            if (dist < r && dist > 0.001) {
                desired.add(diff.normalize().multiplyScalar((r - dist) / r * 2));
            }
        }

        // --- Отражение от стен (плавный возврат) ---
        const p = f.mesh.position;
        const push = new THREE.Vector3();
        if (p.x < minX) push.x += (minX - p.x);
        if (p.x > maxX) push.x -= (p.x - maxX);
        if (p.y < minY) push.y += (minY - p.y);
        if (p.y > maxY) push.y -= (p.y - maxY);
        if (p.z < minZ) push.z += (minZ - p.z);
        if (p.z > maxZ) push.z -= (p.z - maxZ);
        if (push.lengthSq() > 0) desired.add(push.normalize().multiplyScalar(2));

        // Нормализация и ограничение скорости
        desired.normalize();
        const maxSpd = f.targetFood ? f.speed * 1.6 : f.speed;
        f.velocity.lerp(desired, 0.04).normalize().multiplyScalar(maxSpd);
        f.mesh.position.addScaledVector(f.velocity, dt);

        // Жёсткий кламп
        p.x = THREE.MathUtils.clamp(p.x, minX, maxX);
        p.y = THREE.MathUtils.clamp(p.y, minY, maxY);
        p.z = THREE.MathUtils.clamp(p.z, minZ, maxZ);

        // --- Поворот в направлении движения (плавно) ---
        const targetYaw = Math.atan2(-f.velocity.z, f.velocity.x);
        let dy = targetYaw - f.mesh.rotation.y;
        dy = Math.atan2(Math.sin(dy), Math.cos(dy));
        f.mesh.rotation.y += dy * 0.06;
        f.mesh.rotation.z = THREE.MathUtils.clamp(-f.velocity.y * 0.3, -0.4, 0.4);

        // --- Анимация хвоста и плавников ---
        const t = elapsed * f.tailSpeed + f.phase;
        f.tail.rotation.z = Math.sin(t) * 0.55;
        f.leftFin.rotation.y = Math.sin(t * 1.3) * 0.4;
        f.rightFin.rotation.y = -Math.sin(t * 1.3) * 0.4;
    }
}

// ============================================================
//  АНИМАЦИЯ
// ============================================================
let lightOn = true;

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    elapsed += dt;

    // Рыбки
    updateFish(dt);

    // Корм: падение с гравитацией
    for (let i = foodArray.length - 1; i >= 0; i--) {
        const f = foodArray[i];
        f.vy -= 3.5 * dt;
        f.mesh.position.y += f.vy * dt;
        f.mesh.rotation.y += dt * 2;
        if (f.mesh.position.y <= 0.3) {
            scene.remove(f.mesh);
            foodArray.splice(i, 1);
        }
    }

    // Пузырьки
    for (const b of bubbleArray) {
        b.mesh.position.y += b.speed * dt;
        b.mesh.position.x = b.baseX + Math.sin(elapsed * 1.5 + b.phase) * 0.5;
        b.mesh.position.z = b.baseZ + Math.cos(elapsed * 1.2 + b.phase) * 0.5;
        if (b.mesh.position.y > TANK.h - 0.5) {
            b.mesh.position.y = 0.3;
            b.baseX = (Math.random() - 0.5) * (TANK.w - 4);
            b.baseZ = (Math.random() - 0.5) * (TANK.d - 4);
        }
    }

    // Водоросли
    for (const w of weedList) {
        w.obj.rotation.x = Math.sin(elapsed * w.speed + w.phase) * 0.08;
        w.obj.rotation.z = Math.cos(elapsed * w.speed * 0.8 + w.phase) * 0.08;
    }

    controls.update();
    renderer.render(scene, camera);

    // FPS
    fpsFrames++;
    fpsTime += dt;
    if (fpsTime >= 0.5) {
        document.getElementById('fpsCounter').textContent = Math.round(fpsFrames / fpsTime);
        fpsFrames = 0; fpsTime = 0;
    }
}

// ============================================================
//  UI
// ============================================================
function updateStats() {
    document.getElementById('fishCount').textContent = fishArray.length;
}

document.getElementById('addFishBtn').addEventListener('click', () => addFish());
document.getElementById('bubblesBtn').addEventListener('click', () => addBubbles(10));
document.getElementById('lightBtn').addEventListener('click', () => {
    lightOn = !lightOn;
    sunLight.intensity = lightOn ? 1.1 : 0.15;
});

function onResize() {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
}

init();
</script>
</body>
</html>
```

## ✅ Что реализовано

| Раздел | Детали |
|---|---|
| **Рыбки** | 15 шт., вытянутое тело, глаза с зрачками, анимируемый хвост (pivot-группа, вращение по Z), верхний + 2 боковых плавника, 8 палитр, масштаб 0.6–1.2 |
| **ИИ** | Отталкивание от соседей, плавный возврат от стен, таймер блуждания, погоня за кормом (радиус 15), рост ×1.05 при поедании, индивидуальные скорость/фаза/радиус |
| **Окружение** | Стекло с `transmission: 0.95` + wireframe-рамка, песчаное дно с процедурными буграми и тенями, 8 деформированных додекаэдров, 12 водорослей из `TubeGeometry` + `CatmullRomCurve3` с покачиванием |
| **Пузыри** | 30 шт., стеклянные, подъём с синусоидальным покачиванием, респаун на дне |
| **Кормление** | Клик по дну через Raycaster → корм падает с гравитацией, съедается, удаляется на дне |
| **Свет** | Ambient + Directional (тени 2048², PCFSoft) + 2 подводных PointLight, кнопка переключения |
| **Камера** | OrbitControls: вращение/пан/зум 10–60, `maxPolarAngle`, damping |
| **UI** | Glass-панели с blur, градиентный заголовок, счётчики рыбок/FPS, 3 кнопки с hover-эффектами |

**Совет:** если хотите ещё больше реализма — можно добавить плавающие частицы планктона (`Points`) или рябь воды на поверхности (шейдер на плоскости). Могу дополнить! 🐟